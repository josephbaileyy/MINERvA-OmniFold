#!/usr/bin/env python3
"""Phase 7: retrain the PET reweighter on ONE systematic universe's prior.

Retraining-response study. The FROZEN-reweighter systematic estimate (C_syst)
holds the nominal reco->truth PET map FIXED and applies each universe's per-event
truth ratio r_u at truth binning: x_u^frozen = bin(w_push_nominal * w_truth * r_u).
This driver instead RETRAINS a fresh PET map on the universe-u MC prior
(w_truth * r_u) at the SAME estimator config as the nominal, producing a
universe-specific full-cloud push weight w_push_u. Downstream
`phase7_extract_compare.py` forms x_u^retrain = bin(w_push_u * w_truth * r_u) and
the retraining response Delta_u = x_u^retrain - x_u^frozen, tested against the
predeclared materiality criterion (see PET_UQ_PRODUCTION_STATUS.md Phase 7).

Design (LOW-RISK, disk-free): reuse the VALIDATED training path
`minerva_pet_dataloader.build_loaders` unchanged, then inject r_u into the MC
prior by rescaling the (already-normalized) MC weight -- normalization is
scale-homogeneous, so normalize(w_norm * r) == normalize(w_raw * r). r_u enters
TRAINING only; the full-cloud reweight-all push eval is r_u-agnostic (it just
evaluates the trained gen model on gen kinematics); r_u re-enters at EXTRACTION.
We do NOT scale w_truth in any npz -- PETxsec5D hard-requires bit-identical
w_truth (its W-source alignment gate), and extraction uses the nominal cloud.

Runs under tensorflow/2.15.0 on 1 GPU (~1 h, cf. the nominal train). The
universe ratio is read from a truth-ratio bank; for the PRELIMINARY dry-run this
is the pre-fix `bank_uthrow_5d` (support-limited, KNOWN_ISSUES #13/#16). The
FINAL rerun swaps in the GBDT background-aware/selection-complete bank once it
lands (and CPU is restored).
"""
import argparse
import os
import random
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ND = f"{_REPO}/nd-unfolding"
for _p in (f"{_REPO}/omnifold_nn", _ND, f"{_ND}/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def universe_file(key):
    """Pure key -> (bank filename, human label). ROOT-free (unit-testable).
    key = 'MaRES:1' (band:endpoint 0|1) or 'flux:37' (flux universe u)."""
    name, idx = key.split(":")
    idx = int(idx)
    if name == "flux":
        return f"sig_flux_t_{idx}.npy", f"Flux:{idx}"
    if idx not in (0, 1):
        raise SystemExit(f"[FAIL] knob endpoint must be 0 or 1, got {idx} in {key!r}")
    return f"sig_{name}_t_{idx}.npy", f"{name}:{'+1' if idx else '-1'}"


# mirrors pet_systematics_5d.RHO_CLIP (kept in sync). That module imports ROOT
# transitively (unfold_2d_omnifold_unbinned) and CANNOT be imported under the
# TF-module python this driver runs in (KNOWN_ISSUES #17), so we inline the two
# ROOT-free pieces (bank .npy load + RHO_CLIP) and take guarded_ratio from the
# ROOT-free uq_math.
RHO_CLIP = (1e-2, 1e2)


def _universe_ratio(bank, key, invalid_policy):
    """Returns (full-cloud truth ratio r_u, label) for universe `key`.
    ROOT-free: loads the bank .npy directly + clips via uq_math.guarded_ratio."""
    from uq_math import guarded_ratio  # ROOT-free
    fname, label = universe_file(key)
    p = os.path.join(bank, fname)
    if not os.path.exists(p):
        raise SystemExit(f"[FAIL] bank file missing: {p}")
    raw = np.load(p).astype(np.float64)
    r = guarded_ratio(raw, label, invalid_policy=invalid_policy, clip=RHO_CLIP)
    return np.asarray(r, dtype=np.float64), label


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--universe", required=True,
                    help="'MaRES:1' (band:endpoint) or 'flux:37' (flux universe)")
    ap.add_argument("--inputs", default=f"{_ND}/of_inputs_pc_fullcloud_bkgsub_5d.npz")
    ap.add_argument("--bank", default=f"{_ND}/bank_uthrow_5d",
                    help="truth-ratio bank; PRELIMINARY dry-run uses pre-fix bank_uthrow_5d")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="neutral")
    ap.add_argument("--max-events", type=int, default=2_000_000)
    ap.add_argument("--niter", type=int, default=2)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0, help="subsample-draw seed (nominal=0)")
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--save-weights", required=True)
    a = ap.parse_args()

    from minerva_pet_dataloader import build_loaders  # validated loader

    # full-cloud order truth ratio; must align to w_truth / gen-cloud order
    with np.load(a.inputs, allow_pickle=True) as zin:
        n_global = int(zin["w_truth"].shape[0])
    if a.universe in ("null", "identity"):
        # NULL CONTROL: retrain at the NOMINAL prior (r=1, injection is a no-op),
        # same seed/config as a universe retrain. x_null - CV then measures the
        # network-to-network training-noise floor (GPU nondeterminism + fresh
        # init) that contaminates every universe Delta; see PET_UQ Phase 7.
        r_u, label = np.ones(n_global, dtype=np.float64), "null"
    else:
        r_u, label = _universe_ratio(a.bank, a.universe, a.invalid_ratio)
    if r_u.shape[0] != n_global:
        raise SystemExit(f"[FAIL] ratio len {r_u.shape[0]} != n_events {n_global} "
                         f"(bank/cloud misalignment) for {a.universe!r}")
    finite = np.isfinite(r_u).all()
    print(f"[p7] universe {a.universe} ({label}): ratio finite={finite} "
          f"mean={r_u.mean():.4f} min={r_u.min():.3e} max={r_u.max():.3e} n={n_global}",
          flush=True)
    if not finite:
        raise SystemExit("[FAIL] non-finite universe ratio (guarded_ratio should prevent this)")

    # training loaders on the 2M subsample (same draw as the nominal: seed, rank0/size1)
    data, mc, imc = build_loaders(a.inputs, mode="pointcloud", num_part=1,
                                  max_events=a.max_events, rank=0, size=1,
                                  memmap_dir=None, seed=a.seed, bootstrap_seed=None)
    imc = np.asarray(imc, dtype=np.int64)

    # INJECT the universe prior: rescale the (normalized) MC weight by r_u on this
    # subsample, then rebuild the loader (normalize=True). Scale-homogeneous ->
    # identical to scaling raw w_truth then normalizing.
    from omnifold import DataLoader, MultiFold, PET
    w_old = np.asarray(mc.weight, dtype=np.float64)
    w_new = (w_old * r_u[imc]).astype(np.float32)
    if not np.isfinite(w_new).all() or w_new.sum() <= 0:
        raise SystemExit("[FAIL] universe-reweighted MC weight non-finite / non-positive")
    print(f"[p7] MC prior reweighted: sumw {w_old.sum():.4e} -> {float(w_new.sum()):.4e} "
          f"(subsample n={imc.size}); effective shift mean r_u[imc]={float(r_u[imc].mean()):.4f}",
          flush=True)
    mc = DataLoader(reco=np.asarray(mc.reco), gen=np.asarray(mc.gen),
                    pass_reco=np.asarray(mc.pass_reco), pass_gen=np.asarray(mc.pass_gen),
                    weight=w_new, normalize=True, bootstrap=False)

    # fixed estimator seed (identical to the nominal -> the retrained vs frozen
    # difference isolates the MAP-retraining response, not a config change)
    random.seed(a.estimator_seed)
    np.random.seed(a.estimator_seed)
    import tensorflow as tf
    tf.keras.utils.set_random_seed(a.estimator_seed)
    print(f"[p7] estimator seed={a.estimator_seed}; config max_events={a.max_events} "
          f"niter={a.niter} epochs={a.epochs} (matches nominal)", flush=True)

    reco_arr = np.asarray(mc.reco)
    gen_arr = np.asarray(mc.gen)
    num_part = reco_arr.shape[1]
    m1 = PET(reco_arr.shape[-1], num_part=num_part, local=(num_part >= 3))
    m2 = PET(gen_arr.shape[-1], num_part=num_part, local=(num_part >= 3))
    of = MultiFold(f"minerva_pet_p7_{a.universe.replace(':', '_')}", m1, m2, data, mc,
                   niter=a.niter, epochs=a.epochs, batch_size=1024, size=1, rank=0,
                   weights_folder="/tmp/minerva_pet_p7_weights", verbose=True)
    of.Unfold()

    # reweight-all: evaluate the FINAL gen model on the FULL gen cloud (r_u-agnostic)
    _, full_mc, full_imc = build_loaders(a.inputs, mode="pointcloud", num_part=1,
                                         max_events=None, rank=0, size=1, memmap_dir=None)
    full_gen = np.asarray(full_mc.gen)
    print(f"[p7] reweight-all: FULL gen n={full_gen.shape[0]}", flush=True)
    w = of.reweight(full_gen, of.model2, batch_size=4096)
    w = np.asarray(w)
    if not np.isfinite(w).all():
        raise SystemExit("[FAIL] non-finite full-cloud push weights")
    print(f"[p7] full-stats w_push n={len(w)} mean={w.mean():.4f} std={w.std():.4f}", flush=True)

    np.savez_compressed(a.save_weights, w_push=w,
                        mc_indices=np.asarray(full_imc, dtype=np.int64), model="pet",
                        pass_truth=np.asarray(full_mc.pass_gen),
                        universe=a.universe, universe_label=label,
                        bank=os.path.abspath(a.bank),
                        estimator_seed=np.asarray(a.estimator_seed),
                        subsample_seed=np.asarray(a.seed))
    print(f"[p7] saved retrained push weights -> {a.save_weights}")


if __name__ == "__main__":
    main()
