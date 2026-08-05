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
from atomic_write import atomic_savez_compressed, is_complete  # noqa: E402  (login-safe)

ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"
# Frozen nominal seed/config policy (mirrors the adopted per-train config; the matched floor repeat
# reuses the SAME seeds/config with a different output tag to expose the GPU-nondeterminism floor).
# `batch_size` belongs HERE, not as a literal at the MultiFold call. It changes the optimizer's
# trajectory, so a run at a different batch size is a differently-configured estimator; leaving it
# uncommitted meant the artifact could not record it, FROZEN could not gate it, and a closure could
# claim "nominal configuration" while training at another batch size.
NOMINAL_SEED_POLICY = {"estimator_seed": 42, "subsample_seed": 0, "niter": 2, "epochs": 8,
                       "train_events": 2000000, "batch_size": 512}
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

    Unit-normalized because `w_truth` here is `mc.weight`, which the DataLoader rescaled in place --
    to 1e6 pre-D1, and post-D1 to 1e6*sum(w_truth)/sum(w_reco), since the constant is derived from
    the reco leg -- while the validator's independent recomputation reads the dump's raw weights. The
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


DEFAULT_TARGET_NPY = os.path.join(
    _REPO, "nd-unfolding", "g2_fullevent", "gate2", "final",
    "G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy")
DEFAULT_TARGET_RECEIPT = os.path.join(
    _REPO, "nd-unfolding", "g2_fullevent", "gate2", "final",
    "G2_GATE2_TARGET_RUNTIME_RECEIPT.json")


def assert_target_provenance(target_npy, receipt_path, inputs_npz):
    """Bind the precomputed Gate-2 target to the receipt that owns it. Returns the receipt.

    D2 (2026-08-04). Audit J04: this driver used to call `build_fullevent_loaders` with no target
    path, silently re-running the whole 4,680,719-row refinement in process, and NOTHING ever
    compared the result against the published array. So the target Gate-2 certified was certified
    and then discarded, and the launcher comment claiming the nominal 'consumes the negweight-refined
    literal Gate-2 target' described an intent, not the code.

    Every check here is fail-closed, and none of them is a substitute for another: the target hash
    proves WHICH array, the receipt status proves it was certified, the fingerprint and target_mode
    prove it is the publication estimator's target and not a control's, `bootstrap_seed is None`
    proves it is the nominal rather than a replica, and the input size binds it to the source dump.
    Row order -- the one property a hash cannot express on its own -- is bound separately by
    `assert_consumed_inventory_matches_receipt`, against the arrays the loader actually read.
    """
    if not os.path.exists(receipt_path):
        raise SystemExit(f"[gate4/D2] Gate-2 runtime receipt missing: {receipt_path}. The nominal "
                         f"must consume a target some receipt owns (fail closed).")
    try:
        rec = json.load(open(receipt_path))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"[gate4/D2] Gate-2 runtime receipt unreadable ({exc}); fail closed")
    if rec.get("status") != "PASS":
        raise SystemExit(f"[gate4/D2] Gate-2 runtime receipt status is {rec.get('status')!r}, not "
                         f"'PASS'; its target is not certified (fail closed)")
    feed = rec.get("step1_feed") or {}
    wmeta = feed.get("weights") or {}
    rt = rec.get("runtime_target") or {}

    if not os.path.exists(target_npy):
        raise SystemExit(f"[gate4/D2] precomputed target missing: {target_npy}. There is NO fallback "
                         f"to rebuilding it in process -- that is the J04 defect (fail closed).")
    want_sha = wmeta.get("sha256")
    if not want_sha:
        raise SystemExit("[gate4/D2] receipt records no step1_feed.weights.sha256; it cannot own a "
                         "target (fail closed)")
    got_sha = sha256_file(target_npy)
    if got_sha != want_sha:
        raise SystemExit(f"[gate4/D2] target sha256 mismatch\n  receipt {want_sha}\n  on disk "
                         f"{got_sha}\nThis is not the array Gate-2 certified (fail closed)")
    want_size = wmeta.get("size_bytes")
    got_size = os.path.getsize(target_npy)
    if want_size is not None and int(want_size) != int(got_size):
        raise SystemExit(f"[gate4/D2] target size {got_size} != receipt {want_size} (fail closed)")

    if rt.get("estimator_fingerprint") != ESTIMATOR_FINGERPRINT:
        raise SystemExit(f"[gate4/D2] receipt's target fingerprint "
                         f"{rt.get('estimator_fingerprint')!r} != {ESTIMATOR_FINGERPRINT!r}; it "
                         f"belongs to a different estimator (fail closed)")
    if rt.get("target_mode") != BKG_MODE:
        raise SystemExit(f"[gate4/D2] receipt's target_mode {rt.get('target_mode')!r} != "
                         f"{BKG_MODE!r}; a control's target cannot serve the nominal (fail closed)")
    if not rt.get("refinement_is_learned_production"):
        raise SystemExit("[gate4/D2] receipt reports refinement_is_learned_production=False; the "
                         "target came from a substitute refiner and cannot certify the nominal "
                         "estimator (fail closed)")
    if rt.get("bootstrap_seed") is not None:
        raise SystemExit(f"[gate4/D2] receipt's target is bootstrap replica "
                         f"{rt.get('bootstrap_seed')!r}, not the nominal (fail closed)")

    nsum = feed.get("normalized_sum")
    if nsum is None or not np.isfinite(nsum) or nsum <= 0:
        raise SystemExit(f"[gate4/D2] receipt's step1_feed.normalized_sum is {nsum!r}; a target "
                         f"whose own normalization is unrecorded is not certifiable (fail closed)")
    pre = rec.get("input_preflight") or {}
    want_in_size = pre.get("size_bytes")
    if want_in_size is not None and int(want_in_size) != int(os.path.getsize(inputs_npz)):
        raise SystemExit(f"[gate4/D2] source NPZ size {os.path.getsize(inputs_npz)} != the size the "
                         f"receipt was built against ({want_in_size}); the target belongs to a "
                         f"different dump (fail closed)")
    # Size alone is NOT enough, and the receipt carries the digest, so use it. A same-size
    # substitution -- a re-dump of the same inventory with different values, or a differently
    # ordered one -- would otherwise pair the certified target with a different dump and pass every
    # other check here. This costs one sequential read of the ~9.9 GB NPZ; that is proportionate for
    # the gate that authorizes eight GPU-hours, and the digest is returned so the caller reuses it
    # for the artifact record rather than hashing twice.
    want_in_sha = pre.get("sha256")
    if not want_in_sha:
        raise SystemExit("[gate4/D2] receipt records no input_preflight.sha256; the target cannot be "
                         "bound to a source dump (fail closed)")
    got_in_sha = sha256_file(inputs_npz)
    if got_in_sha != want_in_sha:
        raise SystemExit(f"[gate4/D2] source NPZ sha256 mismatch\n  receipt {want_in_sha}\n  on disk "
                         f"{got_in_sha}\nThe certified target was built against a different dump "
                         f"(fail closed)")
    print(json.dumps({"target_provenance": "PASS", "target": target_npy, "target_sha256": got_sha,
                      "receipt": receipt_path, "receipt_status": rec.get("status"),
                      "receipt_verdict": rec.get("verdict"),
                      "receipt_rows": feed.get("rows"),
                      "receipt_normalized_sum": nsum,
                      "source_npz_sha256": got_in_sha,
                      "refinement_rebuilt_in_process": False}, indent=2))
    rec["_verified_input_sha256"] = got_in_sha
    return rec


def assert_consumed_inventory_matches_receipt(meta, rec):
    """Bind ROW ORDER, which the target hash cannot.

    The target is row-aligned to the concatenated data++background order. A same-length target from a
    differently-ordered dump would pass every hash check above and silently attach the wrong weight
    to every row. The loader recomputes each inventory's identity/order hash from the arrays it
    actually read (`_verify_stored_identity`), so comparing those against the receipt's closes it.
    """
    want = ((rec.get("runtime_target") or {}).get("input_identity_hashes")) or {}
    got = (meta.get("input_identity_hashes") or {})
    if not want:
        raise SystemExit("[gate4/D2] receipt carries no runtime_target.input_identity_hashes; row "
                         "order cannot be corroborated (fail closed)")
    missing = [k for k in want if k not in got]
    if missing:
        raise SystemExit(f"[gate4/D2] loader recomputed no identity hash for {missing}; run with "
                         f"verify_identities=True (fail closed)")
    bad = {k: (want[k], got[k]) for k in want if got[k] != want[k]}
    if bad:
        detail = "; ".join(f"{k}: receipt {v[0][:16]} vs consumed {v[1][:16]}"
                           for k, v in sorted(bad.items()))
        raise SystemExit(f"[gate4/D2] consumed inventory does not match the receipt's -- {detail}. "
                         f"The precomputed target's row order does not correspond to the rows this "
                         f"run built (fail closed)")
    print(json.dumps({"consumed_inventory_matches_receipt": True,
                      "inventories": sorted(want)}, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", required=True, help="negweight-refined Gate-2 target NPZ")
    ap.add_argument("--out", help="output weights npz (required unless --config-gate-only)")
    ap.add_argument("--tag", default="nominal", choices=["nominal", "floor"],
                    help="nominal, or the matched GPU-floor repeat (same seeds/config, new output)")
    ap.add_argument("--gate3-manifest", default=None)
    ap.add_argument("--target-npy", default=DEFAULT_TARGET_NPY,
                    help="the PRECOMPUTED negweight-refined Gate-2 target to consume (D2). "
                         "Mandatory: there is no fallback to rebuilding the refinement in process, "
                         "which is audit defect J04 and also needs ROOT in this interpreter.")
    ap.add_argument("--target-receipt", default=DEFAULT_TARGET_RECEIPT,
                    help="the Gate-2 runtime receipt that OWNS --target-npy; every provenance "
                         "check is made against it")
    ap.add_argument("--estimator-seed", type=int, default=NOMINAL_SEED_POLICY["estimator_seed"])
    ap.add_argument("--subsample-seed", type=int, default=NOMINAL_SEED_POLICY["subsample_seed"])
    ap.add_argument("--niter", type=int, default=NOMINAL_SEED_POLICY["niter"])
    ap.add_argument("--epochs", type=int, default=NOMINAL_SEED_POLICY["epochs"])
    ap.add_argument("--max-events", type=int, default=NOMINAL_SEED_POLICY["train_events"])
    ap.add_argument("--batch-size", type=int, default=NOMINAL_SEED_POLICY["batch_size"],
                    help="training batch size; part of the frozen nominal policy")
    ap.add_argument("--config-gate-only", action="store_true",
                    help="run ONLY the fail-closed publication config gate (login-safe; no TF)")
    ap.add_argument("--allow-overwrite", action="store_true",
                    help="replace an output that already carries a valid completion marker "
                         "(J10 no-clobber guard; a partial leftover is always replaceable)")
    args = ap.parse_args(argv)

    cfg = run_config_gate(args.inputs, args.gate3_manifest)
    print(json.dumps({"config_gate": "PASS", "tag": args.tag,
                      "estimator_fingerprint": cfg["estimator_fingerprint"], "bkg_mode": cfg["bkg_mode"],
                      "petSchemaVersion": cfg["petSchemaVersion"],
                      "hasFullEventSchema": cfg["hasFullEventSchema"],
                      "fullPhaseSpace": cfg["fullPhaseSpace"], "has_background": cfg["has_background"],
                      "input": cfg["input"], "seed_policy": NOMINAL_SEED_POLICY}, indent=2))
    # D2: the target binding is checked HERE, inside the login-safe gate, so --config-gate-only
    # verifies it too. Step 2b's launch-code gate is exactly the question "may this train?", and a
    # nominal that cannot name a certified target is not launchable.
    target_receipt = assert_target_provenance(args.target_npy, args.target_receipt, args.inputs)
    if args.config_gate_only:
        return 0
    if not args.out:
        raise SystemExit("[gate4] --out is required for a training run")
    # J10 no-clobber guard, BEFORE the eight GPU-hours rather than after them. A completed
    # publication artifact (one carrying a valid completion marker) is not silently replaced;
    # a partial leftover from an interrupted run carries no marker and is freely overwritten,
    # which is exactly the case the old resume behaviour got backwards.
    if is_complete(args.out) and not args.allow_overwrite:
        raise SystemExit(f"[gate4] {args.out} already exists AND is marked complete. Refusing to "
                         f"overwrite a finished publication artifact; pass --allow-overwrite if "
                         f"replacing it is intended.")

    # ---- GPU training path (lazy TF; NEVER runs under --config-gate-only / tests / import) ----
    import tensorflow as tf
    from omnifold import PET, MultiFold
    tf.keras.utils.set_random_seed(int(args.estimator_seed))
    data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        args.inputs, max_events=args.max_events, seed=int(args.subsample_seed),
        bkg_mode=BKG_MODE, precomputed_target=args.target_npy)
    # D2: row ORDER, which no file hash can bind. Compares the identity hashes the loader recomputed
    # from the arrays it just read against the ones the receipt was built against.
    assert_consumed_inventory_matches_receipt(meta, target_receipt)
    P = np.asarray(mc.reco).shape[1]
    # The two legs have DIFFERENT event-feature widths as of the full-schema loader (J01): step 1
    # is conditioned on the reconstructed muon object + reco vertex, step 2 only on the truth muon,
    # because no truth counterpart for the detector quantities exists. Passing one `n_evt` to both
    # -- as this driver did while both legs read {pT,p||} -- now builds the step-2 network at the
    # wrong input width and dies inside Keras with a shape error rather than here with a reason.
    ev_reco, ev_truth = meta["n_evt_reco"], meta["n_evt_truth"]
    if ev_reco != np.asarray(mc.reco_evt).shape[1] or ev_truth != np.asarray(mc.gen_evt).shape[1]:
        raise SystemExit(f"[gate4] loader meta widths ({ev_reco}, {ev_truth}) disagree with the "
                         f"built blocks ({np.asarray(mc.reco_evt).shape[1]}, "
                         f"{np.asarray(mc.gen_evt).shape[1]}) -- fail closed")
    if list(meta["feature_names"]) == list(fe.REDUCED_EVT_FEATURES):
        raise SystemExit(
            "[gate4] the loader built the REDUCED {pT,p||} schema, which "
            "FULL_EVENT_FEATURE_CONTRACT.md marks 'CROSS-CHECK ONLY -- never a publication "
            f"lateral/central source', yet this driver stamps {ESTIMATOR_FINGERPRINT!r}. That "
            "self-contradiction is AUDIT-FINDINGS-20260731 J01; it is now refused rather than "
            "written. Run the reduced ablation through a driver that stamps "
            "'pet-reduced-fps-cross'.")
    m1 = PET(np.asarray(mc.reco).shape[-1], num_evt=ev_reco, num_part=P,
             num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(np.asarray(mc.gen).shape[-1], num_evt=ev_truth, num_part=P,
             num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_gen)
    mf_name = f"fe_nominal_{args.tag}"
    weights_folder = os.path.join(os.path.dirname(args.out) or ".", f"w_{args.tag}")
    of = MultiFold(mf_name, m1, m2, data, mc, niter=int(args.niter),
                   epochs=int(args.epochs), batch_size=int(args.batch_size),
                   weights_folder=weights_folder,
                   verbose=False)
    of.Unfold()
    # Everything `extract_fullevent_fps.py` needs to rebuild the step-2 network and reproduce the
    # exact input space at full-inventory inference: the architecture, the checkpoint location,
    # and -- decisively -- the event-feature normalization. The truth block was z-scored with the
    # statistic of THIS 2M subsample's pass_truth rows; re-deriving it over 49.2M rows at
    # extraction would feed the trained model a differently-scaled input and produce a confident
    # wrong answer with nothing to notice it.
    inference_contract = {
        "multifold_name": mf_name,
        "weights_folder": os.path.abspath(weights_folder),
        "step2_checkpoint": os.path.abspath(os.path.join(
            weights_folder, f"OmniFold_{mf_name}_iter{int(args.niter) - 1}_step2.weights.h5")),
        "pet_arch": {"num_feat_gen": int(np.asarray(mc.gen).shape[-1]), "num_evt": int(ev_truth),
                     "num_part": int(P), "num_transformer": 2, "num_heads": 2,
                     "projection_dim": 32, "local": True, "K": 3, "coord_idx": list(coord_gen)},
        "event_features_reco": list(meta["feature_names"]),
        "event_features_truth": list(meta["truth_feature_names"]),
        "reco_cloud_cols": list(meta["reco_cloud_cols"]),
        "truth_norm_mean": list(meta["truth_norm_mean"]),
        "truth_norm_std": list(meta["truth_norm_std"]),
        "reco_norm_mean": list(meta["reco_norm_mean"]),
        "reco_norm_std": list(meta["reco_norm_std"]),
        "degenerate_reco_columns": list(meta["degenerate_reco_columns"]),
        "degenerate_truth_columns": list(meta["degenerate_truth_columns"]),
    }
    if meta["degenerate_reco_columns"] or meta["degenerate_truth_columns"]:
        # Not fatal (a selection cut can legitimately make a column constant) but it must be
        # visible: a feature constant on one leg and not the other is a pure data/MC label.
        print(f"[gate4] WARNING degenerate event-feature columns "
              f"reco={meta['degenerate_reco_columns']} "
              f"truth={meta['degenerate_truth_columns']}", file=sys.stderr)

    # ---- B1 §2d: the reco-level fold-forward sums Gate-4's normalization check needs ----
    # Gate-4 asserts that the reco-weighted mean of push equals the physical rate ratio R, i.e.
    # that the unfolded result, folded back through acceptance, reproduces the background-
    # subtracted data yield. Neither w_truth nor pass_reco is in scope in the validator, so
    # without this the check is not computable and is silently skipped.
    #
    # These are the DRIVER's side of a two-sided check. The validator recomputes both sums from
    # the G2 dump independently and asserts the two agree; a gate fed only the driver's own
    # arithmetic certifies nothing. Note the ratio is scale-free, so it does not matter that the
    # DataLoader has already rescaled the leg in place -- nor, post-D1, that the constant it used
    # was derived from the reco leg and leaves the truth leg off 1e6.
    push = np.asarray(of.weights_push, dtype=np.float64)
    # D1 (2026-08-04): this is a STEP-1-space ratio, so it must be built from the leg step 1
    # actually consumed -- the reco leg. It is cross-checked against the loader's
    # step1_class_ratio, whose denominator is now sum(w_reco[pass_reco]); building it from
    # mc.weight would compare a truth-leg ratio against a reco-leg R. Falls back to mc.weight only
    # for a single-weight loader, where the two legs are the same array.
    # NAMED BY LEG, deliberately. An earlier draft of this called the reco leg `w_mc` and then
    # reused that same variable for the TRUTH-space reporting spectrum below -- whose parameter is
    # literally named `w_truth`. Nothing caught it, because both arrays are the right shape and the
    # spectrum is unit-normalized, so the artifact looked fine and was simply the wrong spectrum.
    # There is no single "the MC weight" any more; every use site must say which leg it means.
    _reco_leg = getattr(mc, "weight_reco", None)
    w_reco_leg = np.asarray(mc.weight if _reco_leg is None else _reco_leg, dtype=np.float64)
    w_truth_leg = np.asarray(mc.weight, dtype=np.float64)
    pass_reco_sub = np.asarray(mc.pass_reco).astype(bool)
    if not (push.shape == w_reco_leg.shape == w_truth_leg.shape == pass_reco_sub.shape):
        raise SystemExit(f"[gate4] push {push.shape} / reco leg {w_reco_leg.shape} / truth leg "
                         f"{w_truth_leg.shape} / pass_reco {pass_reco_sub.shape} are not "
                         f"row-aligned (fail closed)")
    if not pass_reco_sub.any():
        raise SystemExit("[gate4] no pass_reco rows in the training subsample; the fold-forward "
                         "ratio is undefined (fail closed)")
    # Step-1 space => reco leg.
    sum_w_push_reco = float((w_reco_leg[pass_reco_sub] * push[pass_reco_sub]).sum())
    sum_w_reco = float(w_reco_leg[pass_reco_sub].sum())
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
                   "epochs": int(args.epochs), "train_events": int(args.max_events),
                   "batch_size": int(args.batch_size)}
    # The truth (pT,p||) of the SAME subsample, from the dump (build_fullevent_loaders keeps the
    # scalars only for the event-feature block, so they are re-read here rather than plumbed out).
    with np.load(args.inputs, allow_pickle=True) as _d:
        truth_scalars_sub = np.asarray(_d["truth_scalars"])[imc]
    pass_truth_sub = np.asarray(mc.pass_gen).astype(bool)
    # TRUTH space => truth leg. Not the reco leg, and not a variable that used to hold either.
    central_vector, reported_bin_mask = reporting_spectra(
        truth_scalars_sub, w_truth_leg, push, pass_truth_sub)
    del truth_scalars_sub
    import omnifold.omnifold as _of_engine                # the authoritative F3 cap, not a copy
    sat_frac = cap_saturation_frac(push, _of_engine.REWEIGHT_LOGIT_CAP)

    # J10: TRANSACTIONAL publication write. A bare np.savez_compressed streams straight to
    # args.out, so an interrupted train leaves a nonempty, plausible, incomplete npz there --
    # which every `[[ -s ... ]]` resume guard in the tree then reads as a finished result, and
    # which Gate-4 would validate as if it were one. atomic_savez_compressed writes a temp
    # sibling, fsyncs it, and os.replace()s it into position, so args.out is either the old
    # file or the whole new one. The completion marker is stamped LAST (mark=True), so its
    # presence always implies a fully published artifact and never the reverse.
    written = atomic_savez_compressed(
        args.out,
        dict(weights_push=np.asarray(of.weights_push),
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
             # Already computed and CHECKED against the receipt by assert_target_provenance; reused
             # rather than recomputed, so the artifact records the digest that was actually verified.
             inputs_sha256=np.asarray(target_receipt["_verified_input_sha256"]),
             seed_policy=np.asarray(seed_policy, dtype=object),
             edges_pt=fe.CANONICAL_PT_EDGES,
             edges_pparallel=fe.CANONICAL_PPARALLEL_EDGES,
             bin_order=np.asarray(BIN_ORDER),
             central_vector=central_vector,
             reported_bin_mask=reported_bin_mask,
             cap_saturation_frac=np.asarray(sat_frac),
             reweight_logit_cap=np.asarray(float(_of_engine.REWEIGHT_LOGIT_CAP)),
             # J01: the schema the result was ACTUALLY trained on, so Gate-4's freeze can read it
             # instead of assuming it. Without this the fingerprint is a label with nothing behind
             # it -- which is how `pet-fullevent-fps-v1` came to be stamped on a {pT,p||} run.
             event_features_reco=np.asarray(list(meta["feature_names"]), dtype=object),
             event_features_truth=np.asarray(list(meta["truth_feature_names"]), dtype=object),
             reco_cloud_cols=np.asarray(list(meta["reco_cloud_cols"]), dtype=object),
             n_evt_reco=np.asarray(int(ev_reco)), n_evt_truth=np.asarray(int(ev_truth)),
             # J02: the full-inventory extractor's contract (architecture, checkpoint, and the
             # normalization statistics inference must reuse).
             inference_contract=np.asarray(inference_contract, dtype=object)),
        mark=True, note=f"gate4 fullevent nominal tag={args.tag}")
    # Report where it actually landed, not where it was asked to go: numpy appends '.npz' to a
    # name that lacks it, and a receipt that records the requested path can then name a file
    # that does not exist.
    print(f"[gate4] wrote {written} (tag={args.tag})")
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
