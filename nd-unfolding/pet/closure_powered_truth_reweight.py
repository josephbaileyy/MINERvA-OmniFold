#!/usr/bin/env python3
"""POWERED closure: inject a known truth-level tilt and measure how much of it comes back.

WHY THIS EXISTS. The ordinary closure (`closure_fullevent_fps.py`) is an identity check -- the
pseudo-data IS the MC -- so push ~ 1 is very nearly guaranteed and a CONSTANT estimator optimizes it
(AUDIT-FINDINGS-20260728.md, structural zero power). It can show the plumbing runs; it cannot show
the estimator works. Decision D2 (2026-08-04) requires this test before closure evidence may gate
publication, and Gate-4's `powered_closure` component fails closed without it.

PREDECLARED PROTOCOL (set 2026-08-05, BEFORE any run; do not tune these to a result):

  * injection      CLIPPED EXPONENTIAL tilt in truth pT, amplitude 0.35, clip |z| <= 3,
                   applied on TRUTH-PASSING rows only, rate-preserving over that population
  * samples        two DISJOINT deterministic halves, 2,000,000 each, split seed 7
  * step-1 rows    `pass_reco & pass_truth` on BOTH sides
  * configuration  the exact nominal PET policy, batch_size included
  * acceptance     gap >= 0.15  AND  floor/gap <= 0.10  AND  residual/gap <= 0.20  (recovery >= 80%)

WHY EACH OF THOSE, since a protocol nobody can justify is a protocol nobody can check:

  * DISJOINT halves -- pseudo-data from half A, prior from half B, so the estimator never sees the
    events it must reweight. An overlapping split restores the identity shortcut and power -> 0.
  * TRUTH-PASSING rows only -- the injection is a truth-level reweighting, so it is only defined
    where a truth record exists. Applying 1.0 to truth-failing rows and then including them would
    dilute the measured tilt with an unmeasurable population.
  * `pass_reco & pass_truth` on BOTH step-1 sides -- otherwise one side carries reco-only rows whose
    tilt is undefined, and step 1 sees a second difference on top of the injection.
  * RATE-PRESERVING -- a rate change would let a pure normalization fix look like shape recovery.
  * CLIPPED -- bounds the injected weight to [exp(-1.05), exp(+1.05)] so no handful of rows carries
    the result.

WHAT THIS SCRIPT PERSISTS, so Gate-4 can re-derive rather than believe: the ABSOLUTE dump row
indices of both halves, the push weights, and the hashes of the source NPZ and its producer receipt.
Gate-4 recomputes the tilt (importing the function below, so the two cannot drift), recomputes all
four spectra from the dump, and checks disjointness on the actual index arrays. The metrics printed
here are convenience; none of them is load-bearing for the verdict.

Runs `bkg_mode='mc-only'` (D2), so no ROOT import and no ROOT/TF environment conflict.

ENVIRONMENT, measured 2026-08-05 rather than assumed. `mc-only` avoids ROOT, which is the conflict
with no resolution on Perlmutter -- but it still needs TENSORFLOW IMPORTABLE, because
`build_fullevent_loaders` ends at `from omnifold.dataloader import DataLoader`, and that triggers
`omnifold/__init__.py`, which imports MultiFold and therefore TF. So this does NOT run under the
ROOT-only `root_6_28` env: a memory-sizing probe there died with `ModuleNotFoundError: No module
named 'tensorflow'` at exactly that line. Gate-2 sidesteps it via
`gate2_target_runtime.load_exact_numpy_dataloader`, which pre-binds the exact NumPy module in
sys.modules. Nothing here needs that trick -- PET wants TF anyway -- but a reader trying `mc-only`
in the ROOT env will otherwise conclude D2 is broken.

(Recorded here rather than in the loader's own docstring on purpose: `fullevent_fps_dataloader.py` is
hash-pinned by the Gate-2 runtime receipt and by run_gate2_target_validator.sh, so editing it even
for a comment invalidates the receipt and costs a full gate re-issue.)
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

import numpy as np
import numpy.lib.format as npf

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(_ND)
for _p in (os.path.join(_REPO, "omnifold_nn"), _ND, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

REPORT_SCHEMA = "powered-truth-reweight-closure-v2"
DEFAULT_NPZ = os.path.join(_ND, "g2_fullevent", "input", "G2_FPS_MEFHC_P12.npz")
DEFAULT_PRODUCER_RECEIPT = os.path.join(_ND, "g2_fullevent", "input",
                                        "G2_FPS_MEFHC_P12_RECEIPT.json")

# Predeclared protocol. Gate-4 checks these against its own FROZEN copy, so changing one here does
# not quietly move the goalposts.
TILT_AMPLITUDE = 0.35
TILT_CLIP_Z = 3.0
SPLIT_SEED = 7
HALF_SIZE = 2_000_000
GAP_MIN = 0.15
FLOOR_OVER_GAP_MAX = 0.10
RESIDUAL_OVER_GAP_MAX = 0.20


def sha256_file(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def clipped_exponential_tilt(pt_truth, amplitude=TILT_AMPLITUDE, clip_z=TILT_CLIP_Z):
    """THE injection. Imported by Gate-4 so both sides compute one function, not two copies.

        u    = (pT - p50) / IQR          quantiles from the rows passed in
        z    = clip(u, -clip_z, +clip_z)
        tilt = exp(amplitude * z) / mean(exp(amplitude * z))

    Clipping the COORDINATE rather than the weight keeps the map monotone and smooth in pT while
    still bounding the weight to [exp(-A*clip_z), exp(+A*clip_z)]; clipping the weight instead would
    flatten the tilt over whole tails and make the recoverable signal depend on the tail population.
    Normalizing by the mean makes it rate-preserving over exactly the rows it is applied to.

    Pass ONLY the truth-passing rows: the quantiles must describe the injected population, or the
    tilt's centre drifts with the reco acceptance.

    Returns (tilt, spec). `spec` is everything needed to reproduce and check it.
    """
    pt = np.asarray(pt_truth, dtype=np.float64)
    if pt.size == 0:
        raise SystemExit("[powered] no truth-passing rows to inject into (fail closed)")
    p25, p50, p75 = (float(x) for x in np.percentile(pt, [25, 50, 75]))
    iqr = max(p75 - p25, 1e-12)
    z = np.clip((pt - p50) / iqr, -float(clip_z), float(clip_z))
    raw = np.exp(float(amplitude) * z)
    mean = float(raw.mean())
    if not (np.isfinite(mean) and mean > 0):
        raise SystemExit(f"[powered] tilt normalization is {mean!r} (fail closed)")
    tilt = raw / mean
    if not np.all(np.isfinite(tilt)) or np.any(tilt <= 0):
        raise SystemExit("[powered] tilt is non-finite or non-positive (fail closed)")
    return tilt, {
        "form": "exp(A*clip((pT-p50)/IQR, -Z, +Z)) / mean(...)",
        "amplitude": float(amplitude), "clip_z": float(clip_z),
        "pt_p25": p25, "pt_p50": p50, "pt_p75": p75, "pt_iqr": iqr,
        "pre_normalization_mean": mean, "rate_preserving": True,
        "applied_on": "pass_truth rows only",
        "n_injected_rows": int(pt.size),
        "tilt_min": float(tilt.min()), "tilt_max": float(tilt.max()),
    }


def unit_spectrum(pt, ppar, weights, edges_pt, edges_pp):
    """Unit-normalized 285-cell (pT,p||) spectrum, pt-major row-major -- the frozen order.

    Callers pass ALREADY-MASKED arrays: masking here too invited the caller and this function to
    disagree about which population a spectrum describes.
    """
    h, _, _ = np.histogram2d(np.asarray(pt, float), np.asarray(ppar, float),
                             [edges_pt, edges_pp], weights=np.asarray(weights, float))
    total = float(h.sum())
    if not total > 0:
        raise SystemExit("[powered] a spectrum summed to <= 0; cannot normalize (fail closed)")
    return (h / total).ravel()


def l1(a, b):
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).sum())


def deterministic_halves(n_rows, half=HALF_SIZE, seed=SPLIT_SEED):
    """Two DISJOINT index sets of `half` rows each, from ONE seeded permutation sliced twice, so
    disjointness is structural rather than asserted after the fact."""
    if n_rows < 2 * half:
        raise SystemExit(f"[powered] need {2 * half} rows for two disjoint halves of {half}; the "
                         f"loader returned {n_rows} (fail closed)")
    perm = np.random.default_rng(int(seed)).permutation(n_rows)
    a, b = np.sort(perm[:half]), np.sort(perm[half:2 * half])
    if np.intersect1d(a, b).size:
        raise SystemExit("[powered] halves overlap; the split is broken (fail closed)")
    return a, b


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inputs", default=DEFAULT_NPZ)
    p.add_argument("--producer-receipt", default=DEFAULT_PRODUCER_RECEIPT)
    p.add_argument("--json", required=True, help="write the machine-readable report here")
    p.add_argument("--artifact", default=None,
                   help="npz for the A/B dump-row indices and push weights (default: alongside "
                        "--json). Gate-4 re-derives every spectrum from this plus the dump.")
    p.add_argument("--half-size", type=int, default=HALF_SIZE)
    p.add_argument("--amplitude", type=float, default=TILT_AMPLITUDE)
    p.add_argument("--clip-z", type=float, default=TILT_CLIP_Z)
    p.add_argument("--split-seed", type=int, default=SPLIT_SEED)
    p.add_argument("--max-events", type=int, default=None,
                   help="rows to load; defaults to 2*half-size, which is what the split needs")
    p.add_argument("--weights-folder", default="./weights_powered_closure")
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    import tensorflow as tf
    from omnifold import PET, MultiFold
    from omnifold.dataloader import DataLoader
    import fullevent_fps_dataloader as fe
    from train_fullevent_nominal import NOMINAL_SEED_POLICY

    pol = NOMINAL_SEED_POLICY
    need = int(a.max_events if a.max_events is not None else 2 * a.half_size)
    artifact = a.artifact or (os.path.splitext(a.json)[0] + "_artifact.npz")
    tf.keras.utils.set_random_seed(int(pol["estimator_seed"]))

    _data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        a.inputs, max_events=need, seed=int(pol["subsample_seed"]), bkg_mode="mc-only")
    if _data is not None:
        raise SystemExit("[powered] mc-only returned a measured loader; wrong build path")
    imc = np.asarray(imc)

    with zipfile.ZipFile(a.inputs) as z:
        with z.open("truth_scalars.npy") as fh:
            ts = npf.read_array(fh, allow_pickle=False)[imc]
    pt_t = ts[:, fe.SCALAR_COLS["pt"]].astype(np.float64)
    pp_t = ts[:, fe.SCALAR_COLS["pparallel"]].astype(np.float64)
    del ts

    reco = np.asarray(mc.reco); reco_evt = np.asarray(mc.reco_evt)
    gen = np.asarray(mc.gen); gen_evt = np.asarray(mc.gen_evt)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    _leg = getattr(mc, "weight_reco", None)
    if _leg is None:
        raise SystemExit("[powered] loader supplied no reco leg; D1 dual-leg weights are required")
    w_reco = np.asarray(_leg, dtype=np.float64)

    ia, ib = deterministic_halves(reco.shape[0], half=int(a.half_size), seed=int(a.split_seed))

    # The injection lives on half A's TRUTH-PASSING rows, and its quantiles come from exactly those.
    pg_a = pg[ia]
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_on_truth, tilt_spec = clipped_exponential_tilt(
        pt_t[ia][pg_a], amplitude=float(a.amplitude), clip_z=float(a.clip_z))
    tilt_a[pg_a] = tilt_on_truth

    # STEP-1 population: pass_reco & pass_truth on BOTH sides.
    s1_a = pr[ia] & pg_a
    s1_b = pr[ib] & pg[ib]
    if not (s1_a.any() and s1_b.any()):
        raise SystemExit("[powered] a step-1 side has no pass_reco & pass_truth rows (fail closed)")

    # FLOAT32 INTO THE ENGINE. `net.weighted_binary_crossentropy` does
    # `weights * tf.nn.sigmoid_cross_entropy_with_logits(...)`, and the logits are float32, so a
    # float64 weight array dies inside a tf.function with `Input 'y' of 'Mul' Op has type float64`
    # -- a traceback that names Keras internals and not the caller. Measured on the first GPU smoke,
    # 2026-08-05. build_fullevent_loaders passes float32, which is why the nominal never hits it, so
    # float32 is the engine's actual contract and this matches it rather than widening the engine
    # (whose dataloader.py is hash-pinned by the Gate-2 receipt and must not move).
    # The float64 copies above stay float64 for the spectra arithmetic, where precision is free.
    pdata = DataLoader(reco=reco[ia][s1_a],
                       weight=((w_reco[ia] * tilt_a)[s1_a]).astype(np.float32),
                       normalize=True, reco_evt=reco_evt[ia][s1_a])
    mcB = DataLoader(reco=reco[ib], gen=gen[ib], pass_reco=s1_b, pass_gen=pg[ib],
                     weight=w_truth[ib].astype(np.float32),
                     weight_reco=w_reco[ib].astype(np.float32),
                     normalize=True, normalization_factor=fe.STEP1_MC_NORMALIZATION,
                     reco_evt=reco_evt[ib], gen_evt=gen_evt[ib])
    for _nm, _dl in (("pdata", pdata), ("mcB", mcB)):
        for _f in ("weight", "weight_reco"):
            _arr = getattr(_dl, _f, None)
            if _arr is not None and np.asarray(_arr).dtype != np.float32:
                raise SystemExit(f"[powered] {_nm}.{_f} is {np.asarray(_arr).dtype}, not float32; "
                                 f"the engine multiplies it against float32 logits (fail closed)")

    P = reco.shape[1]
    m1 = PET(reco.shape[-1], num_evt=meta["n_evt_reco"], num_part=P, num_transformer=2,
             num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(gen.shape[-1], num_evt=meta["n_evt_truth"], num_part=P, num_transformer=2,
             num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_gen)
    of = MultiFold("fe_powered", m1, m2, pdata, mcB, niter=int(pol["niter"]),
                   epochs=int(pol["epochs"]), batch_size=int(pol["batch_size"]),
                   weights_folder=a.weights_folder, verbose=False)
    of.Unfold()
    push = np.asarray(of.weights_push, dtype=np.float64)
    if push.shape[0] != ib.size:
        raise SystemExit(f"[powered] push {push.shape} not aligned to half B ({ib.size}) rows")

    e_pt, e_pp = fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES
    mb, ma = pg[ib], pg_a
    h_prior = unit_spectrum(pt_t[ib][mb], pp_t[ib][mb], w_truth[ib][mb], e_pt, e_pp)
    h_unfold = unit_spectrum(pt_t[ib][mb], pp_t[ib][mb], (w_truth[ib] * push)[mb], e_pt, e_pp)
    h_target = unit_spectrum(pt_t[ia][ma], pp_t[ia][ma], (w_truth[ia] * tilt_a)[ma], e_pt, e_pp)
    h_untilt = unit_spectrum(pt_t[ia][ma], pp_t[ia][ma], w_truth[ia][ma], e_pt, e_pp)

    gap, floor, residual = l1(h_prior, h_target), l1(h_prior, h_untilt), l1(h_unfold, h_target)
    fog, rog = (floor / gap, residual / gap) if gap > 0 else (None, None)
    ok = (gap >= GAP_MIN and fog is not None and fog <= FLOOR_OVER_GAP_MAX
          and rog is not None and rog <= RESIDUAL_OVER_GAP_MAX)

    # ABSOLUTE dump rows, so Gate-4 re-derives from the dump without replaying the subsample logic.
    rows_a, rows_b = imc[ia].astype(np.int64), imc[ib].astype(np.int64)
    np.savez_compressed(artifact, dump_rows_a=rows_a, dump_rows_b=rows_b,
                        weights_push=push.astype(np.float64),
                        mc_indices=imc.astype(np.int64))
    art_sha = sha256_file(artifact)

    print(f"[powered] gap={gap:.4f} floor={floor:.4f} residual={residual:.4f} "
          f"floor/gap={fog:.4f} residual/gap={rog:.4f} recovery={1.0 - rog:.4f} -> "
          f"{'PASS' if ok else 'FAIL'}")

    report = {
        "report_schema": REPORT_SCHEMA,
        "verdict": "PASS" if ok else "FAIL",
        "is_powered_closure": True,
        "closure_class": "injected-truth-reweight-recovery",
        "recovery_criteria_met": bool(ok),
        "h_prior": [float(x) for x in h_prior], "h_target": [float(x) for x in h_target],
        "h_unfolded": [float(x) for x in h_unfold], "h_untilted": [float(x) for x in h_untilt],
        "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
        "edges_pt": [float(x) for x in e_pt], "edges_pparallel": [float(x) for x in e_pp],
        "metrics": {"gap": gap, "floor": floor, "residual": residual,
                    "floor_over_gap": fog, "residual_over_gap": rog,
                    "recovery": (1.0 - rog) if rog is not None else None},
        "criteria": {"gap_min": GAP_MIN, "floor_over_gap_max": FLOOR_OVER_GAP_MAX,
                     "residual_over_gap_max": RESIDUAL_OVER_GAP_MAX,
                     "recovery_min": 1.0 - RESIDUAL_OVER_GAP_MAX},
        "injection": tilt_spec,
        "samples": {"half_size": int(a.half_size), "split_seed": int(a.split_seed),
                    "disjoint": True, "n_loaded": int(reco.shape[0]),
                    "n_step1_a": int(s1_a.sum()), "n_step1_b": int(s1_b.sum()),
                    "n_truth_a": int(ma.sum()), "n_truth_b": int(mb.sum()),
                    "step1_population": "pass_reco & pass_truth on both sides"},
        "configuration": {k: int(pol[k]) for k in ("niter", "epochs", "estimator_seed",
                                                   "subsample_seed", "batch_size")},
        "artifact": {"path": os.path.abspath(artifact), "sha256": art_sha,
                     "contains": ["dump_rows_a", "dump_rows_b", "weights_push", "mc_indices"]},
        "source": {"inputs": os.path.abspath(a.inputs),
                   "inputs_sha256": sha256_file(a.inputs),
                   "producer_receipt": os.path.abspath(a.producer_receipt),
                   "producer_receipt_sha256": (sha256_file(a.producer_receipt)
                                               if os.path.exists(a.producer_receipt) else None)},
        "estimator_fingerprint": meta.get("estimator_fingerprint"),
        "event_features_reco": list(meta.get("feature_names") or []),
        "event_features_truth": list(meta.get("truth_feature_names") or []),
        "bkg_mode": meta.get("bkg_mode"), "mc_only": bool(meta.get("mc_only", False)),
        "reco_leg_weight_used": "w_reco",
        "input_identity_hashes": meta.get("input_identity_hashes"),
    }
    with open(a.json, "w") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    print(f"[powered] wrote report {a.json} and artifact {artifact} (sha {art_sha[:16]})")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
