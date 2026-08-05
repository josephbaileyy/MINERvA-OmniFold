#!/usr/bin/env python3
"""POWERED closure: inject a known truth-level tilt and measure how much of it comes back.

WHY THIS EXISTS. The ordinary closure (`closure_fullevent_fps.py`) is an identity check -- the
pseudo-data IS the MC -- so push ~ 1 is very nearly guaranteed and a CONSTANT estimator optimizes it
(AUDIT-FINDINGS-20260728.md, structural zero power). It can show the plumbing runs; it cannot show
the estimator works. Decision D2 (2026-08-04) therefore requires this test before closure evidence
may gate publication, and Gate-4's `closure:powered_recovery_closure_present` fails closed without it.

PREDECLARED PROTOCOL (set 2026-08-05, BEFORE any run; do not tune these to a result):

  * injection      smooth normalized truth-pT tilt, amplitude 0.35
  * samples        two DISJOINT deterministic halves, 2,000,000 each, split seed 7
  * configuration  the exact nominal PET configuration (NOMINAL_SEED_POLICY)
  * acceptance     gap >= 0.15  AND  floor/gap <= 0.10  AND  residual/gap <= 0.20
                   (the last is recovery >= 80%)

DISJOINT IS THE WHOLE POINT. Pseudo-data is drawn from half A and the MC prior from half B, so the
estimator is never shown the events it must reweight. An overlapping split would reintroduce the
identity shortcut and the power would go back to zero.

THE FOUR METRICS, all L1 on unit-normalized 285-cell (pT,p||) spectra:

  gap      = L1(prior, target)     how much signal was injected -- if this is small there is
                                   nothing to recover and a pass would be meaningless
  floor    = L1(prior, untilted)   the irreducible disagreement between two DISJOINT untilted
                                   halves, i.e. sample-split noise. floor/gap bounds how much of
                                   `gap` could be statistical rather than injected
  residual = L1(unfolded, target)  what is left after unfolding
  recovery = 1 - residual/gap

The report carries all FOUR spectra, not just the metrics, so Gate-4 recomputes every number from
the vectors instead of trusting a boolean this script asserts about itself. That asymmetry matters:
the repo's audit history is full of checks that could only agree with themselves.

Runs under TF 2.15 with `bkg_mode='mc-only'` (D2), so no ROOT import occurs and the ROOT/TF
environment conflict that blocked RESTORE Step 3 does not apply.
"""
import argparse
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

REPORT_SCHEMA = "powered-truth-reweight-closure-v1"
DEFAULT_NPZ = os.path.join(_ND, "g2_fullevent", "input", "G2_FPS_MEFHC_P12.npz")

# Predeclared protocol constants. Changing any of these invalidates the acceptance criteria, so the
# report records them and Gate-4 checks them rather than taking the verdict on trust.
TILT_AMPLITUDE = 0.35
SPLIT_SEED = 7
HALF_SIZE = 2_000_000
GAP_MIN = 0.15
FLOOR_OVER_GAP_MAX = 0.10
RESIDUAL_OVER_GAP_MAX = 0.20


def smooth_pt_tilt(pt_truth, amplitude=TILT_AMPLITUDE):
    """The injected reweighting: 1 + A*tanh((pT - p50) / scale), then normalized to preserve rate.

    `tanh` rather than a linear ramp so the tilt is smooth and bounded everywhere, and centred on the
    sample's own median with `scale` from its interquartile range so the shape is defined by the
    distribution rather than by hand-chosen GeV numbers. Rate-preserving on purpose: this test is
    about SHAPE recovery, and leaving a rate change in would let a pure normalization fix look like
    shape recovery.

    Returns (tilt, spec) where `spec` records everything needed to reproduce it.
    """
    pt = np.asarray(pt_truth, dtype=np.float64)
    p25, p50, p75 = (float(x) for x in np.percentile(pt, [25, 50, 75]))
    scale = max(p75 - p25, 1e-6)
    tilt = 1.0 + float(amplitude) * np.tanh((pt - p50) / scale)
    if not np.all(np.isfinite(tilt)) or np.any(tilt <= 0):
        raise SystemExit("[powered] tilt is non-finite or non-positive; refusing to inject")
    mean = float(tilt.mean())
    tilt = tilt / mean                      # rate-preserving
    return tilt, {"form": "1 + A*tanh((pT - p50)/IQR), normalized to unit mean",
                  "amplitude": float(amplitude), "pt_p25": p25, "pt_p50": p50, "pt_p75": p75,
                  "pt_scale_iqr": scale, "pre_normalization_mean": mean,
                  "rate_preserving": True}


def unit_spectrum(pt, ppar, weights, mask, edges_pt, edges_pp):
    """A unit-normalized 285-cell (pT,p||) spectrum, pt-major row-major -- the frozen order."""
    h, _, _ = np.histogram2d(np.asarray(pt)[mask], np.asarray(ppar)[mask],
                             [edges_pt, edges_pp], weights=np.asarray(weights)[mask])
    total = float(h.sum())
    if not total > 0:
        raise SystemExit("[powered] a spectrum summed to <= 0; cannot normalize (fail closed)")
    return (h / total).ravel()


def l1(a, b):
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).sum())


def deterministic_halves(n_rows, half=HALF_SIZE, seed=SPLIT_SEED):
    """Two DISJOINT index sets of `half` rows each, from one seeded permutation.

    One permutation sliced twice, so disjointness is structural rather than checked after the fact.
    """
    if n_rows < 2 * half:
        raise SystemExit(f"[powered] need {2 * half} rows for two disjoint halves of {half}, "
                         f"the loader returned {n_rows} (fail closed)")
    perm = np.random.default_rng(int(seed)).permutation(n_rows)
    a, b = np.sort(perm[:half]), np.sort(perm[half:2 * half])
    if np.intersect1d(a, b).size:
        raise SystemExit("[powered] halves overlap; the split is broken (fail closed)")
    return a, b


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inputs", default=DEFAULT_NPZ)
    p.add_argument("--json", required=True, help="write the machine-readable report here")
    p.add_argument("--half-size", type=int, default=HALF_SIZE)
    p.add_argument("--amplitude", type=float, default=TILT_AMPLITUDE)
    p.add_argument("--split-seed", type=int, default=SPLIT_SEED)
    p.add_argument("--max-events", type=int, default=None,
                   help="rows to load; defaults to 2*half-size, which is what the split needs")
    p.add_argument("--weights-folder", default="./weights_powered_closure")
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    import tensorflow as tf                                    # noqa: F401  (lazy, as elsewhere)
    from omnifold import PET, MultiFold
    from omnifold.dataloader import DataLoader
    import fullevent_fps_dataloader as fe
    from train_fullevent_nominal import NOMINAL_SEED_POLICY

    pol = NOMINAL_SEED_POLICY
    need = int(a.max_events if a.max_events is not None else 2 * a.half_size)
    tf.keras.utils.set_random_seed(int(pol["estimator_seed"]))

    # mc-only (D2): no measured target, no refinement, no ROOT.
    _data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        a.inputs, max_events=need, seed=int(pol["subsample_seed"]), bkg_mode="mc-only")
    if _data is not None:
        raise SystemExit("[powered] mc-only returned a measured loader; wrong build path")

    with zipfile.ZipFile(a.inputs) as z:
        with z.open("truth_scalars.npy") as fh:
            ts = npf.read_array(fh, allow_pickle=False)[imc]     # (n,4) pt,pz,eavail,q3
    pt_t, pp_t = ts[:, 0].astype(np.float64), ts[:, 1].astype(np.float64)

    reco = np.asarray(mc.reco); reco_evt = np.asarray(mc.reco_evt)
    pr = np.asarray(mc.pass_reco).astype(bool); pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    _leg = getattr(mc, "weight_reco", None)
    if _leg is None:
        raise SystemExit("[powered] loader supplied no reco leg; D1 dual-leg weights are required")
    w_reco = np.asarray(_leg, dtype=np.float64)

    ia, ib = deterministic_halves(reco.shape[0], half=int(a.half_size), seed=int(a.split_seed))
    tilt_a, tilt_spec = smooth_pt_tilt(pt_t[ia], amplitude=float(a.amplitude))

    # Pseudo-data: half A at RECO level, carrying the injected truth tilt. The reco leg is what
    # step 1 consumes (D1), so the pseudo-data must be built from it or step 1 sees a second,
    # unintended difference on top of the injection.
    mask_a_reco = pr[ia]
    pdata = DataLoader(reco=reco[ia][mask_a_reco],
                       weight=(w_reco[ia] * tilt_a)[mask_a_reco],
                       normalize=True, reco_evt=reco_evt[ia][mask_a_reco])
    # MC prior: half B, UNTILTED, dual-leg.
    mcB = DataLoader(reco=reco[ib], gen=np.asarray(mc.gen)[ib],
                     pass_reco=pr[ib], pass_gen=pg[ib],
                     weight=w_truth[ib].copy(), weight_reco=w_reco[ib].copy(),
                     normalize=True, normalization_factor=fe.STEP1_MC_NORMALIZATION,
                     reco_evt=reco_evt[ib], gen_evt=np.asarray(mc.gen_evt)[ib])

    P = reco.shape[1]
    m1 = PET(reco.shape[-1], num_evt=meta["n_evt_reco"], num_part=P, num_transformer=2,
             num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(np.asarray(mc.gen).shape[-1], num_evt=meta["n_evt_truth"], num_part=P,
             num_transformer=2, num_heads=2, projection_dim=32, local=True, K=3,
             coord_idx=coord_gen)
    of = MultiFold("fe_powered", m1, m2, pdata, mcB, niter=int(pol["niter"]),
                   epochs=int(pol["epochs"]), batch_size=256,
                   weights_folder=a.weights_folder, verbose=False)
    of.Unfold()
    push = np.asarray(of.weights_push, dtype=np.float64)

    e_pt, e_pp = fe.CANONICAL_PT_EDGES, fe.CANONICAL_PPARALLEL_EDGES
    # All four in TRUTH space over pass_gen, from the raw truth leg -- never mc.weight of the
    # normalized loader, whose scale post-D1 carries the reco-derived constant.
    h_prior = unit_spectrum(pt_t[ib], pp_t[ib], w_truth[ib], pg[ib], e_pt, e_pp)
    h_unfold = unit_spectrum(pt_t[ib], pp_t[ib], w_truth[ib] * push, pg[ib], e_pt, e_pp)
    h_target = unit_spectrum(pt_t[ia], pp_t[ia], w_truth[ia] * tilt_a, pg[ia], e_pt, e_pp)
    h_untilt = unit_spectrum(pt_t[ia], pp_t[ia], w_truth[ia], pg[ia], e_pt, e_pp)

    gap, floor, residual = l1(h_prior, h_target), l1(h_prior, h_untilt), l1(h_unfold, h_target)
    fog = floor / gap if gap > 0 else None
    rog = residual / gap if gap > 0 else None
    ok = (gap >= GAP_MIN and fog is not None and fog <= FLOOR_OVER_GAP_MAX
          and rog is not None and rog <= RESIDUAL_OVER_GAP_MAX)
    print(f"[powered] gap={gap:.4f} floor={floor:.4f} residual={residual:.4f} "
          f"floor/gap={fog:.4f} residual/gap={rog:.4f} recovery={1.0 - rog:.4f} -> "
          f"{'PASS' if ok else 'FAIL'}")

    report = {
        "report_schema": REPORT_SCHEMA,
        "verdict": "PASS" if ok else "FAIL",
        "is_powered_closure": True,
        "closure_class": "injected-truth-reweight-recovery",
        "recovery_criteria_met": bool(ok),
        # The vectors. Gate-4 recomputes every metric from these; the numbers above are convenience.
        "h_prior": [float(x) for x in h_prior],
        "h_target": [float(x) for x in h_target],
        "h_unfolded": [float(x) for x in h_unfold],
        "h_untilted": [float(x) for x in h_untilt],
        "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
        "edges_pt": [float(x) for x in e_pt],
        "edges_pparallel": [float(x) for x in e_pp],
        "metrics": {"gap": gap, "floor": floor, "residual": residual,
                    "floor_over_gap": fog, "residual_over_gap": rog,
                    "recovery": (1.0 - rog) if rog is not None else None},
        "criteria": {"gap_min": GAP_MIN, "floor_over_gap_max": FLOOR_OVER_GAP_MAX,
                     "residual_over_gap_max": RESIDUAL_OVER_GAP_MAX,
                     "recovery_min": 1.0 - RESIDUAL_OVER_GAP_MAX},
        "injection": tilt_spec,
        "samples": {"half_size": int(a.half_size), "split_seed": int(a.split_seed),
                    "disjoint": True, "n_loaded": int(reco.shape[0]),
                    "n_half_a_pass_reco": int(mask_a_reco.sum()),
                    "n_half_b_pass_gen": int(pg[ib].sum())},
        "configuration": {"niter": int(pol["niter"]), "epochs": int(pol["epochs"]),
                          "estimator_seed": int(pol["estimator_seed"]),
                          "subsample_seed": int(pol["subsample_seed"]),
                          "is_nominal_configuration": True},
        "estimator_fingerprint": meta.get("estimator_fingerprint"),
        "event_features_reco": list(meta.get("feature_names") or []),
        "event_features_truth": list(meta.get("truth_feature_names") or []),
        "bkg_mode": meta.get("bkg_mode"),
        "mc_only": bool(meta.get("mc_only", False)),
        "reco_leg_weight_used": "w_reco",
        "inputs": os.path.abspath(a.inputs),
        "input_identity_hashes": meta.get("input_identity_hashes"),
    }
    with open(a.json, "w") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")
    print(f"[powered] wrote report {a.json}")
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
