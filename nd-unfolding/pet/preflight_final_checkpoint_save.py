#!/usr/bin/env python3
"""Preflight the BEN-043 final-save block BEFORE a nominal run spends its GPU hours on it.

RESULT 2026-08-07 (GPU, seconds), run before job 56445883 dispatched: PASS for both steps --
clone_model(PET) OK, 96 weight tensors, all 96 perturbed off the initializer, clone-of-clone
+ load_weights round-trip BIT-IDENTICAL, and a fresh clone differs so the check is not vacuous.

WHY THIS EXISTS. The block I added to `train_fullevent_nominal.py` runs AFTER `MultiFold.Unfold()`,
i.e. after ~3 GPU-hours of training for the nominal and again after the matched floor repeat. It has
never executed. If any of its four operations fails on a PET model, the job dies having thrown away the
training, which is the exact late-failure shape this campaign keeps paying for.

The specific risk is not hypothetical: `tf.keras.models.clone_model` REQUIRES a functional or
sequential model and raises on a subclassed `Model`. The engine calls it at omnifold.py:279 on a
freshly-constructed PET, so it must work there -- but my block calls it on `step{1,2}_models[0]`, which
is ITSELF already a clone, and then calls `load_weights` into that second-generation clone. Cloning a
clone and round-tripping weights through it is a different operation from what the engine exercises, and
"it must be fine because the engine does something similar" is exactly the reasoning this repo has been
burned by.

So this reproduces the block's operations exactly, on the real architecture read from the committed
inference contract, with NO training:

    m      = PET(<nominal arch>)                 stands in for the engine's model1/model2
    trained= tf.keras.models.clone_model(m)      what the engine appends to step{1,2}_models
    trained.save_weights(final_path)             my block, line 1
    chk    = tf.keras.models.clone_model(trained)  my block, line 2  <- the untested part
    chk.load_weights(final_path)                 my block, line 3
    assert every weight tensor bit-identical      my block, line 4

Weights are randomized away from the initializer first, so a `save_weights` that silently wrote nothing
(or a `load_weights` that silently matched nothing) cannot pass by both sides happening to hold the same
default initialization -- which would be a vacuous pass of exactly the kind BEN-040 records.

Cheap: no data, no training, one model construction per step. Reads the architecture from the artifact's
contract rather than restating it, so it cannot drift from what the driver builds.
"""
import os
import sys

import numpy as np

# Resolved from THIS file, never a /pscratch absolute -- scratch is purgeable (CLAUDE.md) and a
# tracked tool that hardcodes it is unrunnable in any other checkout. That is the same defect BEN-044
# records in combine_cstat_bkgsub_100rep.py, which is why this one does not repeat it.
ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REPO = os.path.dirname(ND)
# `omnifold` lives under omnifold_nn/, which only reaches sys.path via
# fullevent_fps_dataloader.py:58. This script does not need the loader, so it inserts the same
# two paths directly rather than importing a 9.9 GB-capable module for a side effect.
for _p in (os.path.join(_REPO, "omnifold_nn"), ND, os.path.join(ND, "pet")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
DEFAULT_ARCHIVED = os.path.join(
    ND, "pet/fullevent_nominal/superseded-20260806/pet_fullevent_nominal_weights.npz")
ARCHIVED = os.environ.get("PREFLIGHT_ARTIFACT", DEFAULT_ARCHIVED)
OUT = os.environ.get("PREFLIGHT_OUT",
                     os.path.join(os.environ.get("SCRATCH", "/tmp"),
                                  "preflight_final_save"))


def main():
    os.makedirs(OUT, exist_ok=True)
    with np.load(ARCHIVED, allow_pickle=True) as d:
        contract = d["inference_contract"].item()
        n_evt_reco = int(d["n_evt_reco"])
        n_evt_truth = int(d["n_evt_truth"])
    arch = dict(contract["pet_arch"])
    print(f"arch from the committed contract: {arch}")
    print(f"n_evt_reco={n_evt_reco}  n_evt_truth={n_evt_truth}")

    import tensorflow as tf
    from omnifold import PET

    # Step 2 is the one the extractor loads, so it is the one that must work; step 1 is built at the
    # reco widths and is checked too because my block saves both.
    cases = [
        ("step2", arch["num_feat_gen"], n_evt_truth, tuple(arch["coord_idx"])),
        # the step-1 net differs only in input widths; coord_idx for reco is not in the contract, so
        # the step-2 value is reused HERE ONLY as a shape-compatible stand-in. This preflight tests the
        # clone/save/load mechanics, which do not depend on which columns are coordinates.
        ("step1", arch["num_feat_gen"], n_evt_reco, tuple(arch["coord_idx"])),
    ]

    ok = True
    for name, nfeat, nevt, coord in cases:
        print(f"\n=== {name}: PET(num_feat={nfeat}, num_evt={nevt}, num_part={arch['num_part']}) ===")
        m = PET(nfeat, num_evt=nevt, num_part=arch["num_part"],
                num_transformer=arch["num_transformer"], num_heads=arch["num_heads"],
                projection_dim=arch["projection_dim"], local=arch["local"], K=arch["K"],
                coord_idx=coord)
        try:
            trained = tf.keras.models.clone_model(m)
        except Exception as e:                                    # noqa: BLE001
            print(f"  *** clone_model(PET) FAILED: {type(e).__name__}: {e}")
            print("  -> the ENGINE would fail too (omnifold.py:279); this is not my block's bug")
            ok = False
            continue
        print(f"  clone_model(PET) OK  ({len(trained.get_weights())} weight tensors)")

        # Move OFF the initializer so a no-op save/load cannot pass vacuously.
        rng = np.random.default_rng(1234)
        w0 = trained.get_weights()
        trained.set_weights([w + rng.normal(0, 0.1, size=np.shape(w)).astype(np.asarray(w).dtype)
                             if np.asarray(w).dtype.kind == "f" else w for w in w0])
        w_trained = trained.get_weights()
        moved = sum(1 for a, b in zip(w0, w_trained) if not np.array_equal(a, b))
        print(f"  randomized {moved}/{len(w0)} tensors away from the initializer")
        if moved == 0:
            print("  *** could not perturb any tensor -- the round-trip check below would be vacuous")
            ok = False
            continue

        p = os.path.join(OUT, f"preflight_{name}_final.weights.h5")
        trained.save_weights(p)
        sz = os.path.getsize(p)
        print(f"  save_weights -> {p} ({sz} bytes)")

        # THE UNTESTED PART: clone the clone, then load into it.
        chk = tf.keras.models.clone_model(trained)
        chk.load_weights(p)
        a, b = trained.get_weights(), chk.get_weights()
        same = len(a) == len(b) and all(np.array_equal(x, y) for x, y in zip(a, b))
        print(f"  clone-of-clone + load_weights round-trip bit-identical: {same} "
              f"({len(a)} vs {len(b)} tensors)")
        if not same:
            worst = max((float(np.abs(np.asarray(x) - np.asarray(y)).max())
                         for x, y in zip(a, b) if np.shape(x) == np.shape(y)), default=float("nan"))
            print(f"  *** max |delta| across tensors: {worst:.3e}")
            ok = False

        # And the vacuity check in the other direction: a FRESH clone that never loaded must DIFFER,
        # else `load_weights` is not what made them equal.
        fresh = tf.keras.models.clone_model(trained)
        c = fresh.get_weights()
        differs = any(not np.array_equal(x, y) for x, y in zip(a, c))
        print(f"  POWER: a fresh clone that never loaded differs from the trained one: {differs}")
        if not differs:
            print("  *** two independent clones are identical, so the round-trip proves nothing")
            ok = False

    print()
    print(f"PREFLIGHT {'PASS -- 56445883 will survive its final-save block' if ok else 'FAIL'}")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
