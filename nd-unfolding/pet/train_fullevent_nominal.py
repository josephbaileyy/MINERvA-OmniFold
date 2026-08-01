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
and runs only on a GPU node; this driver NEVER auto-submits and is NEVER invoked at import time.
WHAT THIS DRIVER MUST PERSIST, AND WHY (audit B2). Until the 08-03 Gate-4 re-issue it wrote only
`weights_push, mc_indices, estimator_fingerprint, bkg_mode, tag, target` -- no niter, epochs, seeds,
train_events, grid, input hash or reporting spectrum. The consequence was not a missing convenience:
`freeze:seed_policy` was UNFALSIFIABLE by construction (the validator compared its own FROZEN policy
to itself), and the central-vector / reported-mask / cap-saturation checks had no artifact to read
and so never executed at all. A nominal launched with `--niter 1 --epochs 2` validated PASS against
a receipt that recorded `niter: 2, epochs: 8`. Everything added below exists so that the gate reads
the RESULT rather than its own constants; see `validate_pet_nominal_gate4.check_freeze`.
"""
import argparse
import hashlib
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
# The ravel convention of `central_vector` / `reported_bin_mask`. Stated INDEPENDENTLY of the
# validator's FROZEN["bin_order"] on purpose: the whole point of persisting it is that the gate can
# find the two disagreeing, which it cannot do if both sides read one constant. The two literals are
# pinned equal by test_b1_normalization_fix.Gate4ArtifactContract.
BIN_ORDER = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"


def sha256_file(path, chunk=1 << 22):
    """Content hash of the G2 dump. Gate-4 compares it against its own read of --inputs, which turns
    the validator's basename check into a CONTENT bind (a re-staged dump legitimately changes path;
    a substituted one must not pass as the same inventory)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def reporting_spectra(truth_scalars, w_truth, push, pass_truth):
    """The 285-cell reporting spectra Gate-4's freeze checks read from the artifact.

    Returns (central_vector, reported_bin_mask). `central_vector` is the pushed (pT,p_parallel)
    spectrum over pass_truth on the canonical extended-FPS grid, ravelled in the frozen pt-major
    row-major order and NORMALIZED TO UNIT SUM; `reported_bin_mask` marks the prior-occupied cells.

    Unit-normalized because `w_truth` here is `mc.weight`, which the DataLoader rescaled in place to
    sum to 1e6, while the validator's independent recomputation reads the dump's raw weights. The
    two are the same spectrum up to a positive scale and the freeze fixes only length/order/
    finiteness, so normalizing is what makes the two-sided agreement check exact. The absolute
    cross-section normalization belongs to the extraction step, not to this artifact."""
    ts = np.asarray(truth_scalars, dtype=np.float64)
    w = np.asarray(w_truth, dtype=np.float64)
    p = np.asarray(push, dtype=np.float64)
    sel = np.asarray(pass_truth).astype(bool)
    if not (ts.shape[0] == w.shape[0] == p.shape[0] == sel.shape[0]):
        raise SystemExit(f"[gate4] reporting-spectra inputs not row-aligned: truth_scalars "
                         f"{ts.shape}, weight {w.shape}, push {p.shape}, pass_truth {sel.shape}")
    if not sel.any():
        raise SystemExit("[gate4] no pass_truth rows in the training subsample; the reporting "
                         "spectrum is undefined (fail closed)")
    bins = [fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES]
    pt = ts[:, fe.SCALAR_COLS["pt"]]; ppar = ts[:, fe.SCALAR_COLS["pparallel"]]
    h_prior, _, _ = np.histogram2d(pt[sel], ppar[sel], bins, weights=w[sel])
    h_push, _, _ = np.histogram2d(pt[sel], ppar[sel], bins, weights=(w * p)[sel])
    central = h_push.ravel()
    total = central.sum()
    if not (np.isfinite(total) and total > 0.0):
        raise SystemExit(f"[gate4] pushed reporting spectrum sums to {total} (fail closed)")
    return central / total, (h_prior.ravel() > 0.0)


def cap_saturation_frac(push, cap):
    """Fraction of push weights sitting at the engine's PREDECLARED symmetric logit cap.

    `MultiFold.reweight` returns `exp(clip(logit, -cap, +cap))` and logs the saturated count without
    persisting it, so the fraction is recovered as `|log(push)| >= cap`. `cap` is read from the
    engine itself; Gate-4 mirrors the constant and recomputes this fraction from `weights_push`
    independently, so a drift on either side shows up as a disagreement rather than silently."""
    p = np.asarray(push, dtype=np.float64)
    if p.size == 0:
        return float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        logit = np.log(p)
    bad = ~np.isfinite(logit)
    return float((bad | (np.abs(logit) >= float(cap) * (1.0 - 1e-6))).mean())


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

    # ---- B1 §2d: the reco-level fold-forward sums Gate-4's normalization check needs ----
    # Gate-4 asserts that the reco-weighted mean of push equals the physical rate ratio R, i.e.
    # that the unfolded result, folded back through acceptance, reproduces the background-
    # subtracted data yield. Neither w_truth nor pass_reco is in scope in the validator, so
    # without this the check is not computable and is silently skipped.
    #
    # These are the DRIVER's side of a two-sided check. The validator recomputes both sums from
    # the G2 dump independently and asserts the two agree; a gate fed only the driver's own
    # arithmetic certifies nothing. Note the ratio is scale-free, so it does not matter that
    # `mc.weight` has already been rescaled in place to 1e6 by the DataLoader.
    push = np.asarray(of.weights_push, dtype=np.float64)
    w_mc = np.asarray(mc.weight, dtype=np.float64)
    pass_reco_sub = np.asarray(mc.pass_reco).astype(bool)
    if not (push.shape == w_mc.shape == pass_reco_sub.shape):
        raise SystemExit(f"[gate4] push {push.shape} / mc.weight {w_mc.shape} / pass_reco "
                         f"{pass_reco_sub.shape} are not row-aligned (fail closed)")
    if not pass_reco_sub.any():
        raise SystemExit("[gate4] no pass_reco rows in the training subsample; the fold-forward "
                         "ratio is undefined (fail closed)")
    sum_w_push_reco = float((w_mc[pass_reco_sub] * push[pass_reco_sub]).sum())
    sum_w_reco = float(w_mc[pass_reco_sub].sum())
    target_meta = meta.get("target") or {}
    class_ratio = target_meta.get("step1_class_ratio")
    if class_ratio is None:
        raise SystemExit("[gate4] loader meta carries no step1_class_ratio -- this driver requires "
                         "the B1-corrected loader (fail closed)")

    # ---- audit B2: the run's ACTUAL configuration + reporting spectra, for the Gate-4 freeze ----
    # `seed_policy` is what the run really did, read off argv -- not NOMINAL_SEED_POLICY. Persisting
    # the constant instead would recreate the self-comparison the freeze check exists to avoid.
    seed_policy = {"estimator_seed": int(args.estimator_seed),
                   "subsample_seed": int(args.subsample_seed), "niter": int(args.niter),
                   "epochs": int(args.epochs), "train_events": int(args.max_events)}
    # The truth (pT,p||) of the SAME subsample, from the dump (build_fullevent_loaders keeps the
    # scalars only for the event-feature block, so they are re-read here rather than plumbed out).
    with np.load(args.inputs, allow_pickle=True) as _d:
        truth_scalars_sub = np.asarray(_d["truth_scalars"])[imc]
    pass_truth_sub = np.asarray(mc.pass_gen).astype(bool)
    central_vector, reported_bin_mask = reporting_spectra(
        truth_scalars_sub, w_mc, push, pass_truth_sub)
    del truth_scalars_sub
    import omnifold.omnifold as _of_engine                # the authoritative F3 cap, not a copy
    sat_frac = cap_saturation_frac(push, _of_engine.REWEIGHT_LOGIT_CAP)

    np.savez_compressed(args.out, weights_push=np.asarray(of.weights_push),
                        mc_indices=imc, estimator_fingerprint=ESTIMATOR_FINGERPRINT,
                        bkg_mode=BKG_MODE, tag=args.tag,
                        target=meta.get("target"),
                        # B1 §2d fold-forward inputs (see comment above)
                        fold_forward_sum_w_push_reco=np.asarray(sum_w_push_reco),
                        fold_forward_sum_w_reco=np.asarray(sum_w_reco),
                        fold_forward_n_pass_reco=np.asarray(int(pass_reco_sub.sum())),
                        step1_class_ratio=np.asarray(float(class_ratio)),
                        # -1 = nominal (no bootstrap); the validator's recomputation from the dump
                        # is only valid for the nominal, so it must be able to tell.
                        bootstrap_seed=np.asarray(
                            -1 if target_meta.get("bootstrap_seed") is None
                            else int(target_meta["bootstrap_seed"])),
                        inputs_path=np.asarray(os.path.abspath(args.inputs)),
                        # audit B2: the freeze must read the RESULT, not the validator's constants
                        inputs_sha256=np.asarray(sha256_file(args.inputs)),
                        seed_policy=np.asarray(seed_policy, dtype=object),
                        edges_pt=fe.CANONICAL_PT_EDGES,
                        edges_pparallel=fe.CANONICAL_PPARALLEL_EDGES,
                        bin_order=np.asarray(BIN_ORDER),
                        central_vector=central_vector,
                        reported_bin_mask=reported_bin_mask,
                        cap_saturation_frac=np.asarray(sat_frac),
                        reweight_logit_cap=np.asarray(float(_of_engine.REWEIGHT_LOGIT_CAP)))
    print(f"[gate4] wrote {args.out} (tag={args.tag})")
    print(json.dumps({"fold_forward_reco_ratio": sum_w_push_reco / sum_w_reco,
                      "step1_class_ratio_R": float(class_ratio),
                      "n_pass_reco_subsample": int(pass_reco_sub.sum()),
                      "n_pass_truth_subsample": int(pass_truth_sub.sum()),
                      "n_reported_cells": int(reported_bin_mask.sum()),
                      "cap_saturation_frac": sat_frac,
                      "seed_policy": seed_policy}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
