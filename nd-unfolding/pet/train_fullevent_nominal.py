#!/usr/bin/env python3
"""Publication full-event PET NOMINAL training driver (Gate-4).

Routes the publication nominal through `fullevent_fps_dataloader.py` and FAILS CLOSED via
`assert_publication_config` before any compute: estimator fingerprint `pet-fullevent-fps-v1`,
`bkg_mode=negweight-refined`, the G2 full-schema markers, and a background inventory. It consumes the
negweight-refined literal Gate-2 target NPZ (`G2_FPS_MEFHC_P12.npz`) and references the Gate-3 source
manifest. The quarantined recoil script `sbatch_pet_nominal_bkgsub.sh` (KNOWN_ISSUES #19 / F7) is NOT
this path.

`--config-gate-only` runs ONLY the fail-closed publication config gate (login-safe: no TensorFlow,
no NPZ materialization -- it reads just the tiny scalar marker members from the npz zip header) and
prints the plan. The full training path (build loaders + MultiFold + save) imports TensorFlow lazily
and runs only on a GPU node; this driver NEVER auto-submits and is NEVER invoked at import time."""
import argparse
import io
import json
import os
import sys
import zipfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (_HERE, f"{_REPO}/nd-unfolding", f"{_REPO}/nd-unfolding/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fe  # noqa: E402  (login-safe: TF imported lazily inside)

ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"
# Frozen nominal seed/config policy (mirrors the adopted per-train config; the matched floor repeat
# reuses the SAME seeds/config with a different output tag to expose the GPU-nondeterminism floor).
NOMINAL_SEED_POLICY = {"estimator_seed": 42, "subsample_seed": 0, "niter": 2, "epochs": 8,
                       "train_events": 2000000}


def read_npz_markers(npz_path):
    """Read ONLY the tiny scalar marker members + background presence from the npz zip header
    (no full-array materialization). Returns a cfg dict for assert_publication_config."""
    if not os.path.exists(npz_path):
        raise ValueError(f"[gate4] target NPZ not found: {npz_path}")
    z = zipfile.ZipFile(npz_path)
    names = set(z.namelist())

    def scalar(member):
        fn = f"{member}.npy"
        if fn not in names:
            return None
        # read the member bytes into a seekable buffer (ZipExtFile is not seekable under older numpy)
        return np.load(io.BytesIO(z.read(fn)), allow_pickle=False).item()

    return {
        "estimator_fingerprint": (scalar("estimator_fingerprint") if "estimator_fingerprint.npy"
                                  in names else None),
        "bkg_mode": BKG_MODE,
        "petSchemaVersion": scalar("petSchemaVersion"),
        "hasFullEventSchema": scalar("hasFullEventSchema"),
        "fullPhaseSpace": scalar("fullPhaseSpace"),
        "has_background": "w_bkg.npy" in names,
        "input": npz_path,
    }


def run_config_gate(npz_path, gate3_manifest=None):
    """Fail-closed publication config gate. Reads the target markers, asserts publication config, and
    (if given) asserts the Gate-3 source manifest exists + is PASS. Returns the bound cfg dict."""
    cfg = read_npz_markers(npz_path)
    # 1. the input's own fingerprint (if present) must be the publication fingerprint
    if cfg["estimator_fingerprint"] not in (None, ESTIMATOR_FINGERPRINT):
        raise ValueError(f"[gate4] target estimator_fingerprint {cfg['estimator_fingerprint']!r} "
                         f"!= {ESTIMATOR_FINGERPRINT!r} (fail closed)")
    # 2. the run configuration fingerprint is the publication fingerprint
    cfg["estimator_fingerprint"] = ESTIMATOR_FINGERPRINT
    # 3. the authoritative fail-closed publication gate (fingerprint / bkg_mode / G2 markers / bkg)
    fe.assert_publication_config(cfg)
    if gate3_manifest is not None:
        if not os.path.exists(gate3_manifest):
            raise ValueError(f"[gate4] Gate-3 source manifest missing: {gate3_manifest}")
        m = json.load(open(gate3_manifest))
        if m.get("verdict") not in ("PASS", "PASS_CODE_ONLY", "PROMOTED_PASS"):
            raise ValueError(f"[gate4] Gate-3 source manifest not PASS: {m.get('verdict')!r}")
    return cfg


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True, help="negweight-refined Gate-2 target NPZ")
    ap.add_argument("--out", help="output weights npz (required unless --config-gate-only)")
    ap.add_argument("--tag", default="nominal", choices=["nominal", "floor"],
                    help="nominal, or the matched GPU-floor repeat (same seeds/config, new output)")
    ap.add_argument("--gate3-manifest", default=None)
    ap.add_argument("--estimator-seed", type=int, default=NOMINAL_SEED_POLICY["estimator_seed"])
    ap.add_argument("--subsample-seed", type=int, default=NOMINAL_SEED_POLICY["subsample_seed"])
    ap.add_argument("--niter", type=int, default=NOMINAL_SEED_POLICY["niter"])
    ap.add_argument("--epochs", type=int, default=NOMINAL_SEED_POLICY["epochs"])
    ap.add_argument("--max-events", type=int, default=NOMINAL_SEED_POLICY["train_events"])
    ap.add_argument("--config-gate-only", action="store_true",
                    help="run ONLY the fail-closed publication config gate (login-safe; no TF)")
    args = ap.parse_args(argv)

    cfg = run_config_gate(args.inputs, args.gate3_manifest)
    print(json.dumps({"config_gate": "PASS", "tag": args.tag,
                      "estimator_fingerprint": cfg["estimator_fingerprint"], "bkg_mode": cfg["bkg_mode"],
                      "petSchemaVersion": cfg["petSchemaVersion"],
                      "hasFullEventSchema": cfg["hasFullEventSchema"],
                      "fullPhaseSpace": cfg["fullPhaseSpace"], "has_background": cfg["has_background"],
                      "input": cfg["input"], "seed_policy": NOMINAL_SEED_POLICY}, indent=2))
    if args.config_gate_only:
        return 0
    if not args.out:
        raise SystemExit("[gate4] --out is required for a training run")

    # ---- GPU training path (lazy TF; NEVER runs under --config-gate-only / tests / import) ----
    import tensorflow as tf
    from omnifold import PET, MultiFold
    tf.keras.utils.set_random_seed(int(args.estimator_seed))
    data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        args.inputs, max_events=args.max_events, seed=int(args.subsample_seed),
        bkg_mode=BKG_MODE)
    P = np.asarray(mc.reco).shape[1]
    ev = meta["n_evt"]
    m1 = PET(np.asarray(mc.reco).shape[-1], num_evt=ev, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(np.asarray(mc.gen).shape[-1], num_evt=ev, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_gen)
    of = MultiFold(f"fe_nominal_{args.tag}", m1, m2, data, mc, niter=int(args.niter),
                   epochs=int(args.epochs), batch_size=512,
                   weights_folder=os.path.join(os.path.dirname(args.out) or ".", f"w_{args.tag}"),
                   verbose=False)
    of.Unfold()
    np.savez_compressed(args.out, weights_push=np.asarray(of.weights_push),
                        mc_indices=imc, estimator_fingerprint=ESTIMATOR_FINGERPRINT,
                        bkg_mode=BKG_MODE, tag=args.tag,
                        target=meta.get("target"))
    print(f"[gate4] wrote {args.out} (tag={args.tag})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
