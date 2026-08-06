#!/usr/bin/env python3
"""Gate-4 validator for the publication full-event PET NOMINAL result (runbook Packet P5A /
PET_UQ_REMEDIATION_STATUS Gate 4).

CODE-ONLY gate: the pure checks below are login-safe and unit-tested against synthetic nominal
results; the actual nominal training is a separate authorized step (nominal_pet_training_allowed
stays false). The validator COMPOSES the existing closure evidence (ordinary closure
`closure_fullevent_fps.py` + omitted-muon stress closure `stress_closure_muon.py`) and adds:

  * finite / full-coverage push weights;
  * strict MC index/order (sorted, unique, in range) AND the subsample size the seed policy froze;
  * the ordinary closure's exact lower-dimensional (pT,p_parallel) marginal closure, recomputed
    here from the histograms that run persisted rather than trusted as a scalar;
  * the RECO-LEVEL FOLDED-FORWARD NORMALIZATION gate (B1 §2d): the reco-weighted mean of the push
    weights must equal the physical data/MC rate ratio R, with R and the reference sums recomputed
    HERE from the G2 dump rather than taken from the driver. This replaces the truth-level
    `sum_w_push/sum_w ~ 1` identity, which a correct unfold does not satisfy (its expected value
    is 1 + <a>(R-1), a function of the acceptance being measured) and which the CLI never wired;
  * cap-sensitivity telemetry (logit-cap saturation fraction bounded), recomputed from the push
    weights themselves;
  * the measured-target provenance the driver already persists and nothing read: target mode,
    the LEARNED production Stay-Positive refinement, the signed-target hash, and pot_scale;
  * the FREEZE of estimator fingerprint + central vector (length/finite/order) + reported-bin
    mask/order + extended-FPS edges + seed/config policy.

NO CHECK MAY BE SILENTLY SKIPPED (audit B2, `AUDIT-FINDINGS-20260729-B.md` §B2 /
`AUDIT-FINDINGS-20260728.md` §B2). Until the 08-03 re-issue this validator called
`build_gate4_report` without `marginal=`, `normalization=`, `saturation_frac=` or `closure=`, and
the report builder skipped every component whose argument was None; `frozen_observed` was built by
copying four FROZEN entries into the "observed" dict, so four freeze checks compared FROZEN to
FROZEN; and it carried no central vector or reported mask, so those checks never ran either. The
result was `verdict PASS, 0 failed` on `|N(1,0.3)|` noise. Two structural rules follow, and both
are load-bearing:

  1. `build_gate4_report` FAILS on absent evidence -- it emits a named failing check rather than
     dropping the component. A gate that cannot see its input says so.
  2. Everything compared against FROZEN is read from the ARTIFACT (or recomputed from the G2 dump),
     never copied out of FROZEN. A self-comparison is not a check.

The output receipt binds the nominal result path/hash, the frozen contract, every check, and a single
PASS/FAIL verdict. It is written unique-temp + fsync + atomic os.replace ONLY to a caller-supplied
WORK path; it never publishes a production artifact."""
import argparse
import hashlib
import json
import os
import sys
import tempfile

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (_HERE, f"{_REPO}/nd-unfolding", f"{_REPO}/nd-unfolding/pet"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fullevent_fps_dataloader as fe  # noqa: E402  (login-safe)

RECEIPT_SCHEMA = "pet-fullevent-gate4-nominal-validation-v1"
ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"
# Report schemas the two closure scripts write with --json. The validator refuses a report whose
# schema it does not recognise rather than guessing at the fields.
ORDINARY_CLOSURE_SCHEMA = "pet-fullevent-ordinary-closure-v1"
STRESS_CLOSURE_SCHEMA = "pet-fullevent-omitted-muon-stress-v1"

# ----------------------------- FROZEN nominal contract -----------------------------
# Frozen NOW (code-only): fingerprint, extended-FPS reporting grid + bin geometry/order, and the
# seed/config policy. The central vector itself is produced by the authorized nominal run; the freeze
# fixes its LENGTH (= reported cells) + order convention so a later result cannot silently reshape it.
N_PT_BINS = len(fe.CANONICAL_PT_EDGES) - 1                 # 15
N_PPAR_BINS = len(fe.CANONICAL_PPARALLEL_EDGES) - 1        # 19
N_CELLS = N_PT_BINS * N_PPAR_BINS                          # 285
FROZEN = {
    "estimator_fingerprint": ESTIMATOR_FINGERPRINT,
    "bkg_mode": BKG_MODE,
    # J01. `pet-fullevent-fps-v1` is defined by FULL_EVENT_FEATURE_CONTRACT.md as the FULL-schema
    # estimator (full muon object + reco vertex + view/timing); `pet-reduced-fps-cross` is the
    # {pT,p||} one, "CROSS-CHECK ONLY -- never a publication lateral/central source". Until
    # 2026-08-01 the gate froze the fingerprint STRING and nothing behind it, so a run on the
    # reduced schema validated as the publication estimator -- the contract refuting itself in
    # code. These two lists are what the fingerprint now MEANS, read from the artifact.
    "event_features_reco": list(fe.DEFAULT_EVT_FEATURES),
    "event_features_truth": list(fe.DEFAULT_TRUTH_EVT_FEATURES),
    "reco_cloud_cols": list(fe.RECO_CLOUD_COLS),
    "reduced_cross_check_features": list(fe.REDUCED_EVT_FEATURES),
    "edges_pt": [float(x) for x in fe.CANONICAL_PT_EDGES],
    "edges_pparallel": [float(x) for x in fe.CANONICAL_PPARALLEL_EDGES],
    "n_pt_bins": N_PT_BINS, "n_pparallel_bins": N_PPAR_BINS, "n_reported_cells": N_CELLS,
    "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
    "seed_policy": {"estimator_seed": 42, "subsample_seed": 0, "niter": 3, "epochs": 8,
                    "batch_size": 512,
                    "train_events": 2000000},
    "closure_scripts": {
        "ordinary": "nd-unfolding/pet/closure_fullevent_fps.py",
        "omitted_muon_stress": "nd-unfolding/pet/stress_closure_muon.py"},
    # Mirrors omnifold.REWEIGHT_LOGIT_CAP (omnifold_nn/omnifold/omnifold.py). Mirrored rather than
    # imported because importing the package pulls TensorFlow and this validator is login-safe;
    # `test_frozen_logit_cap_matches_the_engine` reads the engine's SOURCE and fails if the two
    # drift apart, so the mirror cannot go stale silently.
    # D2 POWERED CLOSURE, predeclared 2026-08-05 before any run. Frozen here so the gate checks the
    # protocol it was promised rather than whatever protocol a report happens to describe.
    "powered_closure": {
        "report_schema": "powered-truth-reweight-closure-v2",
        "amplitude": 0.35,
        "clip_z": 3.0,
        "step1_population": "pass_reco & pass_truth on both sides",
        "spectrum_agreement_atol": 1e-9,
        "half_size": 2000000,
        "split_seed": 7,
        "rate_preserving": True,
        "gap_min": 0.15,
        "floor_over_gap_max": 0.10,
        "residual_over_gap_max": 0.20,
        "metric_agreement_atol": 1e-9,
    },
    "reweight_logit_cap": 30.0,
    "tolerances": {"marginal_l1_max": 0.10, "push_median_dev_max": 0.15,
                   "cap_saturation_frac_max": 1e-3,
                   # B1 §2d. MEASURED 2026-08-06, and the VALUE IS UNCHANGED at 0.05 -- this is not
                   # a tolerance raise. What moved is the structural floor: niter 2 -> 3 drops
                   # (1-a)^k (R-1)/R from 3.7318% to 2.1698%, which is where the margin came from.
                   # 48 seeds (7-54) at the measured operating point (R=1.1240802949941018,
                   # a=20573521/49152885=0.4185618199216587), N=240,000, epochs 8, niter 3:
                   #   max 4.2750%   mean 2.1876%   sd 0.8444%   0/48 above 0.05
                   # At niter=2 this SAME tolerance saw 6/48 exceedances, which is why the policy
                   # moved rather than the number. Clearance is F_3 + 3.35 sigma.
                   # Upper bound is NOT the defect signal (R-1)/R: the parameter-free check is
                   # algebraically dev < C = (R-1)/(2R) = 5.5192%, so any tol >= C is INERT and the
                   # usable range is (worst correct dev, C). 0.05 sits inside it.
                   # See check_fold_forward_ratio for the three terms that set it and why it cannot
                   # inherit a 1e-3-scale identity tolerance.
                   "fold_forward_ratio_dev_max": 0.05,
                   "fold_forward_ratio_dev_max_status": "MEASURED_20260806_B1_48SEEDS_NITER3",
                   # Independence checks: the driver's reported quantities vs the validator's own
                   # recomputation from the dump. Same arithmetic on the same rows -- these ARE
                   # tight, and a mismatch means the two are not looking at the same result.
                   "fold_forward_driver_agreement_max": 1e-6,
                   "spectra_driver_agreement_max": 1e-6},
}


def _ck(name, ok, detail=""):
    return {"name": name, "ok": bool(ok), "detail": str(detail)}


def _missing(component, what):
    """The absent-evidence check. A component whose input was not supplied FAILS, by name.

    This is rule 1 of the module docstring. `build_gate4_report` used to drop such a component
    entirely, which is how four physics checks and three freeze checks came to never execute while
    the receipt still read `verdict PASS, n_failed 0` and embedded the tolerances they would have
    used."""
    return False, [_ck(f"{component}:evidence_supplied", False,
                       f"NOT SUPPLIED: {what} -- the check could not run, so it FAILS")]


def check_weights_finite_coverage(push, n_expected=None):
    push = np.asarray(push, float)
    checks = [_ck("weights:nonempty", push.size > 0, push.size),
              _ck("weights:finite", bool(np.all(np.isfinite(push))), "all finite"),
              _ck("weights:nonnegative", bool(np.all(push >= 0.0)), "likelihood-ratio >= 0"),
              _ck("weights:not_all_zero", bool(np.any(push > 0.0)), "some positive")]
    if n_expected is not None:
        checks.append(_ck("weights:full_coverage", push.shape[0] == int(n_expected),
                          f"{push.shape[0]} vs {n_expected}"))
    return all(c["ok"] for c in checks), checks


def check_mc_index_order(imc, n_full=None, n_expected_subsample=None):
    """Strict index/order, plus the subsample SIZE the seed policy froze.

    The size check is not cosmetic. `check_weights_finite_coverage` is called with
    `n_expected = len(imc)`, i.e. the push array is only ever compared against the subsample's own
    length, so a nominal trained on 1,000 rows instead of 2,000,000 satisfied every index check
    (audit B3 / §4 mutation table: `train_events 2_000_000 -> 1000` was caught by nothing). The
    frozen `seed_policy.train_events` is the only statement of how many rows the nominal is.
    """
    imc = np.asarray(imc)
    checks = [_ck("index:1d_integer", imc.ndim == 1 and np.issubdtype(imc.dtype, np.integer),
                  f"{imc.ndim}d {imc.dtype}"),
              _ck("index:strictly_increasing", imc.size > 0 and bool(np.all(np.diff(imc) > 0)),
                  "sorted unique ascending"),
              _ck("index:nonnegative", imc.size > 0 and int(imc.min()) >= 0, "min>=0")]
    if n_full is not None:
        checks.append(_ck("index:in_range", imc.size > 0 and int(imc.max()) < int(n_full),
                          f"max {int(imc.max()) if imc.size else None} < {n_full}"))
    if n_expected_subsample is not None:
        want = min(int(n_expected_subsample), int(n_full)) if n_full is not None \
            else int(n_expected_subsample)
        checks.append(_ck("index:subsample_size_matches_policy", imc.size == want,
                          f"{imc.size} trained rows vs frozen policy {want}"))
    return all(c["ok"] for c in checks), checks


def marginal_l1(h_truth, h_rw):
    a = np.asarray(h_truth, float); b = np.asarray(h_rw, float)
    a = a / a.sum() if a.sum() else a
    b = b / b.sum() if b.sum() else b
    return float(np.abs(a - b).sum())


def check_marginal_closure(h_truth, h_rw, tol=None):
    tol = FROZEN["tolerances"]["marginal_l1_max"] if tol is None else tol
    l1 = marginal_l1(h_truth, h_rw)
    return (l1 <= tol), [_ck("marginal:pt_ppar_l1", l1 <= tol, f"L1={l1:.4f} <= {tol}")], l1


def _ratio_dev(numerator, denominator, target_ratio):
    """|(numerator/denominator)/target_ratio - 1|, or inf on a degenerate input.

    The former public `check_normalization` primitive, retired at the 08-03 re-issue. It was a
    truth-level `sum_w_push/sum_w ~ 1` gate that main() never wired and MUST NOT be wired: over the
    full truth population, including off-acceptance events where push == 1, a CORRECT unfold gives
    sum(w*push)/sum(w) -> 1 + <a>_w*(R-1) ~ 1.08, not 1 -- a target that depends on the acceptance
    being measured. Asserting ~1 there fails a correct unfold; asserting ~R there fails it worse.
    Restricting the mask to pass_reco is what removes the acceptance dependence, which is
    `check_fold_forward_ratio` below. It survived the 07-29 patch only as a binding-preserving shim
    for the two frozen launch-code tests that pinned its signature; RESTORE-2026-08-03.md Step 2b
    asked for that decision to be made at the re-issue, and this is it -- the entry point is gone,
    the arithmetic lives here, and `normalization_dev_max` is gone from FROZEN with it (nothing
    read it, and the receipt embedded it as though it had been met)."""
    denominator = float(denominator)
    target_ratio = float(target_ratio)
    if denominator and target_ratio:
        return abs((float(numerator) / denominator) / target_ratio - 1.0)
    return float("inf")


def check_fold_forward_ratio(sum_w_push_reco, sum_w_reco, R, tol=None):
    """THE Gate-4 normalization gate (B1 §2d): a reco-level folded-forward closure.

        sum(w_truth * push over pass_reco) / sum(w_truth over pass_reco)  ==  R

    i.e. *the reco-weighted mean of push equals R*. Fold the unfolded truth back through
    acceptance and require it to reproduce the background-subtracted data yield. This is exactly R
    by construction: dividing the absolute identity
    `pot_scale*sum(w_truth*push over pass_reco) == n_data - pot_scale*sum(w_bkg)` by
    `pot_scale*sum(w_truth over pass_reco)` reproduces R's own definition on the right.

    RATIO, NOT ABSOLUTE YIELD. The nominal trains on a 2M subsample of 49,152,885 rows, so `push`
    exists only for the subsample while the measured yield is a full-inventory quantity. The
    absolute form fails a CORRECT unfold by ~ N/n_sub ~ 24. The ratio needs no subsample factor.

    The target is measured rather than modelled, and -- decisively -- it FAILS the current broken
    result (which forces the step-1 class ratio to 1) while PASSING a corrected one. It converts
    Gate-4 from tolerating this defect into detecting its whole class.

    TOLERANCE -- and it cannot inherit a 1e-3-scale identity tolerance:
      1. Acceptance-smoothing residual at finite iteration. omnifold.py:185 pins off-acceptance
         `new_weights` to 1, so step 2 regresses across both acceptance classes at once and
         smooths pass_reco pushes toward 1. When acceptance is statistically independent of the
         truth features -- the worst case, since the step-2 regressor then cannot separate the
         classes at all -- the recursion has a closed form:

             push_k = R - (1-a)^k (R-1)      =>   dev_k = (1-a)^k (R-1)/R

         CORRECTION (adversarial review of b3751cc, 2026-07-29): an earlier version of this
         comment called this an irreducible "structural floor" that "does NOT vanish with more
         iterations". That is wrong, and the closed form above refutes it -- it tends to 0 as
         k -> infinity. `weights_pull = weights_push * new_weights` (omnifold.py:184-187) RETAINS
         the previous push off-acceptance, so each iteration lets the off-acceptance weights catch
         up. Measured: 9.23% / 3.69% / 0.59% at k=1/2/4 (R=1.30, a=0.60). It is a finite-iteration
         residual, and at the frozen niter=2 it is what it is -- but it is not a floor, and it must
         not be cited as one to justify a loose tolerance.
      2. Subsample sampling. The ratio is subsample-invariant in expectation, not algebraically.
    `fold_forward_ratio_dev_max` is PROVISIONAL until the closure run measures these at the
    measured R; it must stay well below (R-1)/R (~0.119) or the check detects nothing, and above
    term 1 at niter=2 (~1.71% at a=0.621, R=1.135) or it fails a correct unfold.

    The second, PARAMETER-FREE check below carries the power claim on its own: a result must land
    nearer R than 1. That is precisely the broken-vs-corrected discriminator, and unlike the
    tolerance it involves no invented threshold, so it is meaningful before the closure lands.
    """
    tol = FROZEN["tolerances"]["fold_forward_ratio_dev_max"] if tol is None else tol
    R = float(R)
    if not (sum_w_reco and np.isfinite(R) and R > 0.0):
        return False, [_ck("normalization:fold_forward_reco_ratio", False,
                           f"undegenerate inputs required (sum_w_reco={sum_w_reco}, R={R})")]
    ratio = float(sum_w_push_reco) / float(sum_w_reco)
    dev = _ratio_dev(sum_w_push_reco, sum_w_reco, R)
    ok_tol = dev <= tol
    checks = [_ck("normalization:fold_forward_reco_ratio", ok_tol,
                  f"|ratio/{R:.6g}-1|={dev:.3e} <= {tol}")]
    # The discriminator is only MEANINGFUL when R differs from 1. At R == 1 the two distances are
    # identical, so `<` is False for every possible input -- including a correct no-change unfold
    # with push == 1, which would then be failed outright. More generally, if |R-1| <= tol, any
    # result inside the tolerance is within tol of BOTH targets and the comparison decides nothing.
    # §4 explicitly contemplates R coming back near 1.0 ("the defect is far less serious than the
    # recoil-only evidence suggests"), so this is a reachable configuration, not a theoretical
    # edge. Found by adversarial review of b3751cc, 2026-07-29.
    if abs(R - 1.0) > tol:
        nearer_R = abs(ratio - R) < abs(ratio - 1.0)
        checks.append(_ck("normalization:rate_recovered_not_erased", nearer_R,
                          f"reco-weighted mean push={ratio:.6f} is nearer R={R:.6f} than 1.0 "
                          f"(|d_R|={abs(ratio - R):.3e} vs |d_1|={abs(ratio - 1.0):.3e})"))
    else:
        nearer_R = True
        checks.append(_ck("normalization:rate_recovered_not_erased", True,
                          f"not applicable: R={R:.6f} is within tol={tol} of 1.0, so rate erasure "
                          "and rate recovery are indistinguishable by construction. The tolerance "
                          "check above is the exact statement in this regime."))
    return (ok_tol and nearer_R), checks


def fold_forward_sums_from_dump(inputs_npz, weights_push, mc_indices):
    """Recompute the §2d fold-forward sums and R from the G2 dump, INDEPENDENTLY of the driver.

    The driver persists its own `(sum(w*push), sum(w))` so the gate can cross-check; this is the
    other side. It reads the weights and `pass_reco` from the dump itself, re-derives the training
    subsample's reco mask from `mc_indices`, and pairs it with the driver's `weights_push` -- the
    result under test is the driver's, the reference data is not. R likewise comes from
    `fe.step1_class_ratio_from_dump`, never from the weights npz.

    D1 (2026-08-04): THIS IS A STEP-1-SPACE QUANTITY, so it reads `w_reco`, matching the leg step 1
    consumes and the leg the driver now sums. It read `w_truth` until the D1 repair; leaving it there
    would have compared a truth-leg reference against a reco-leg result and failed the strict
    independence check for a reason that is not a defect in either side.

    Note both sums are scale-free in the leg's normalization: the driver's arrays were rescaled in
    place by the DataLoader, this reads the raw dump weights, and the RATIO is identical either way.
    Returns (sum_w_push_reco, sum_w_reco, R, telem).
    """
    push = np.asarray(weights_push, float)
    imc = np.asarray(mc_indices)
    with np.load(inputs_npz, allow_pickle=True) as d:
        w_truth_full = np.asarray(d["w_truth"], dtype=np.float64)
        if "w_reco" not in d.files:
            raise ValueError("[gate4] dump carries no 'w_reco'; since D1 the step-1 leg is w_reco "
                             "and this independent recomputation cannot be formed (fail closed)")
        w_reco_full = np.asarray(d["w_reco"], dtype=np.float64)
        pass_reco_full = np.asarray(d["pass_reco"]).astype(bool)
        R, telem = fe.step1_class_ratio_from_dump(
            d, w_truth_full=w_truth_full, w_reco_full=w_reco_full,
            pass_reco_full=pass_reco_full)
    if imc.shape != push.shape:
        raise ValueError(f"[gate4] mc_indices {imc.shape} and weights_push {push.shape} are not "
                         "row-aligned (fail closed)")
    if imc.size and int(imc.max()) >= w_truth_full.shape[0]:
        raise ValueError(f"[gate4] mc_indices max {int(imc.max())} outside the dump's signal "
                         f"inventory ({w_truth_full.shape[0]} rows) -- wrong dump (fail closed)")
    w_sub = w_reco_full[imc]          # D1: reco leg, to match the driver's step-1-space sums
    mask = pass_reco_full[imc]
    if not mask.any():
        raise ValueError("[gate4] no pass_reco rows in the recomputed subsample (fail closed)")
    telem["n_pass_reco_subsample"] = int(mask.sum())
    # The dump is the authority on how many signal rows exist, so `index:in_range` no longer
    # depends on the caller remembering --n-full (it silently skipped the check when omitted).
    telem["n_signal_inventory"] = int(w_truth_full.shape[0])
    return float((w_sub[mask] * push[mask]).sum()), float(w_sub[mask].sum()), R, telem


def nominal_spectra_from_dump(inputs_npz, weights_push, mc_indices):
    """Recompute the reporting-grid spectra the FREEZE checks need, INDEPENDENTLY of the driver.

    Histograms the subsample's TRUTH (pT, p_parallel) over pass_truth on the frozen 285-cell
    extended-FPS grid, once with the prior weights and once with `w_truth * push`, and ravels in
    the frozen pt-major row-major order (C order over (n_pt, n_pparallel) is exactly
    `cell = i_pt * n_pparallel_bins + i_pparallel`).

    Returns (central_vector, reported_bin_mask, telem). `central_vector` is the pushed spectrum --
    the 285-cell object the freeze fixes the length/order/finiteness of; `reported_bin_mask` is the
    prior-occupied cells, i.e. the cells this estimator can report. The driver persists both, and
    `check_spectra_independence` requires the two sides to agree: the freeze checks run on the
    DRIVER's arrays (so they are falsifiable -- a self-computed vector is 285 long by construction
    and its length check would prove nothing), and this recomputation is what stops the driver
    certifying its own reshape.

    UNIT-NORMALIZED, deliberately. The driver histograms `mc.weight`, which the DataLoader rescaled
    in place to sum to 1e6; this reads the dump's raw `w_truth`. Both are the same spectrum up to a
    positive scale, so the two sides can only be compared after normalizing -- and the freeze only
    fixes the vector's length, order and finiteness, none of which the scale carries. The absolute
    cross-section normalization is the extraction step's, not this gate's.
    """
    push = np.asarray(weights_push, float)
    imc = np.asarray(mc_indices)
    with np.load(inputs_npz, allow_pickle=True) as d:
        edges_pt = np.asarray(d["edges_0"], float)
        edges_pp = np.asarray(d["edges_1"], float)
        w_truth_full = np.asarray(d["w_truth"], dtype=np.float64)
        pass_truth_full = np.asarray(d["pass_truth"]).astype(bool)
        ts = np.asarray(d["truth_scalars"], dtype=np.float64)[imc]
    # The grid is frozen; a dump on a different grid must not be histogrammed against FROZEN's
    # edges and reported as agreeing with it (this is the same guard build_fullevent_loaders runs).
    fe.assert_extended_fps_edges(edges_pt, edges_pp)
    if imc.shape != push.shape:
        raise ValueError(f"[gate4] mc_indices {imc.shape} and weights_push {push.shape} are not "
                         "row-aligned (fail closed)")
    w_sub = w_truth_full[imc]
    sel = pass_truth_full[imc]
    if not sel.any():
        raise ValueError("[gate4] no pass_truth rows in the recomputed subsample -- the reporting "
                         "spectrum is undefined (fail closed)")
    pt = ts[:, fe.SCALAR_COLS["pt"]]
    ppar = ts[:, fe.SCALAR_COLS["pparallel"]]
    bins = [np.asarray(FROZEN["edges_pt"], float), np.asarray(FROZEN["edges_pparallel"], float)]
    h_prior, _, _ = np.histogram2d(pt[sel], ppar[sel], bins, weights=w_sub[sel])
    h_push, _, _ = np.histogram2d(pt[sel], ppar[sel], bins, weights=(w_sub * push)[sel])
    central = h_push.ravel()
    total = central.sum()
    if not (np.isfinite(total) and total > 0.0):
        raise ValueError(f"[gate4] pushed reporting spectrum sums to {total} -- not normalizable "
                         "(fail closed)")
    telem = {"n_pass_truth_subsample": int(sel.sum()),
             "push_median_pass_truth": float(np.median(push[sel])),
             "prior_occupied_cells": int((h_prior.ravel() > 0.0).sum()),
             "pushed_spectrum_raw_sum": float(total),
             "grid": f"{N_PT_BINS}x{N_PPAR_BINS}",
             "normalization": "central_vector normalized to unit sum (scale-free comparison with "
                              "the driver, whose mc.weight was rescaled to 1e6 in place)"}
    return central / total, (h_prior.ravel() > 0.0), telem


def cap_saturation_frac_from_push(weights_push, cap=None):
    """Fraction of push weights sitting at the PREDECLARED symmetric logit cap.

    `omnifold.MultiFold.reweight` returns `exp(clip(logit, -cap, +cap))` and logs the saturated
    count without persisting it, so the fraction is recovered from the artifact itself:
    `|log(push)| >= cap`. Off-acceptance rows carry push == 1 exactly (log 0) and so are never
    counted. Computed HERE rather than trusted from the driver -- the driver persists its own
    value and `check_spectra_independence` requires agreement.

    The comparison carries a small relative slack because `weights_push` is stored float32:
    `log(float32(exp(30)))` is 30 to ~1e-6, not exactly 30, and an exact `>=` would report zero
    saturation on a fully saturated result.
    """
    cap = FROZEN["reweight_logit_cap"] if cap is None else float(cap)
    push = np.asarray(weights_push, float)
    if push.size == 0:
        return float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        logit = np.log(push)
    # A non-finite or non-positive push is a defect, not a saturation datum;
    # check_weights_finite_coverage owns it. Count it as saturated so it cannot hide here.
    bad = ~np.isfinite(logit)
    return float((bad | (np.abs(logit) >= cap * (1.0 - 1e-6))).mean())


def check_fold_forward_independence(validator, driver, tol=None):
    """Cross-check the validator's own recomputation against the driver's persisted sums.

    This is what stops §2d degenerating into "the gate certifies the driver's own arithmetic".
    The two sides compute the same ratio over the same rows from different reads of different
    files, so they must agree to round-off; a real disagreement means they are not looking at the
    same result, the same subsample, or the same dump. R is compared too -- the driver got its R
    from the loader, the validator derived its own from the dump.
    """
    tol = FROZEN["tolerances"]["fold_forward_driver_agreement_max"] if tol is None else tol
    v_push, v_w, v_R = (float(x) for x in validator)
    d_push, d_w, d_R = (float(x) for x in driver)
    v_ratio = v_push / v_w if v_w else float("nan")
    d_ratio = d_push / d_w if d_w else float("nan")
    ratio_dev = abs(v_ratio / d_ratio - 1.0) if d_ratio else float("inf")
    r_dev = abs(v_R / d_R - 1.0) if d_R else float("inf")
    return (ratio_dev <= tol and r_dev <= tol), [
        _ck("normalization:driver_validator_ratio_agree", ratio_dev <= tol,
            f"validator {v_ratio:.9f} vs driver {d_ratio:.9f} (rel {ratio_dev:.3e} <= {tol})"),
        _ck("normalization:driver_validator_R_agree", r_dev <= tol,
            f"validator R {v_R:.9f} vs driver R {d_R:.9f} (rel {r_dev:.3e} <= {tol})")]


def check_spectra_independence(validator, driver, tol=None):
    """Cross-check the reporting spectra + cap telemetry the driver persisted.

    `validator`/`driver` are each (central_vector, reported_bin_mask, cap_saturation_frac). The
    freeze checks read the DRIVER's arrays -- that is what makes their length/order/finiteness
    falsifiable -- so something has to establish that those arrays describe the result they are
    attached to. This does: same rows, same grid, two independent reads.
    """
    tol = FROZEN["tolerances"]["spectra_driver_agreement_max"] if tol is None else tol
    v_cv, v_mask, v_sat = validator
    d_cv, d_mask, d_sat = driver
    v_cv = np.asarray(v_cv, float); d_cv = np.asarray(d_cv, float)
    v_mask = np.asarray(v_mask, bool); d_mask = np.asarray(d_mask, bool)
    shapes_agree = v_cv.shape == d_cv.shape and v_mask.shape == d_mask.shape
    if shapes_agree and v_cv.size:
        scale = float(np.abs(v_cv).max()) or 1.0
        cv_dev = float(np.abs(v_cv - d_cv).max() / scale)
    else:
        cv_dev = float("inf")
    mask_agree = shapes_agree and bool(np.array_equal(v_mask, d_mask))
    sat_dev = abs(float(v_sat) - float(d_sat)) if np.isfinite(v_sat) and np.isfinite(d_sat) \
        else float("inf")
    checks = [_ck("spectra:driver_validator_central_vector_agree", cv_dev <= tol,
                  f"max|dv|/max|v| = {cv_dev:.3e} <= {tol} "
                  f"(validator {v_cv.shape} vs driver {d_cv.shape})"),
              _ck("spectra:driver_validator_mask_agree", mask_agree,
                  f"validator {int(v_mask.sum()) if v_mask.size else None} occupied cells vs "
                  f"driver {int(d_mask.sum()) if d_mask.size else None}"),
              _ck("spectra:driver_validator_cap_saturation_agree", sat_dev <= tol,
                  f"validator {v_sat} vs driver {d_sat} (abs {sat_dev:.3e} <= {tol})")]
    return all(c["ok"] for c in checks), checks


def check_cap_sensitivity(saturation_frac, tol=None):
    tol = FROZEN["tolerances"]["cap_saturation_frac_max"] if tol is None else tol
    ok = (saturation_frac is not None and np.isfinite(float(saturation_frac))
          and float(saturation_frac) <= tol)
    return ok, [_ck("cap:saturation_frac", ok, f"{saturation_frac} <= {tol}")]


def check_target_provenance(target):
    """Gate the measured-target provenance the driver persists and nothing read.

    Audit B2: "a grep for `target`/`refinement` over the validator returns zero hits: `z['target']`
    -- the sole carrier of `refinement_is_learned_production`, `refined_sum`, `pot_scale` and
    `signed_target_hash` -- is never read, even though the driver writes it."

    The load-bearing one is `refinement_is_learned_production`. RESTORE-2026-08-03.md Step 4: Delta
    has no ROOT, so `u2d.refine_stay_positive` cannot import there and a Delta run can only inject
    an sklearn refinement, which self-reports `refinement_is_learned_production=False`. Nothing
    stopped such a result being validated as the publication nominal. Now it fails closed.
    """
    if not isinstance(target, dict):
        return _missing("target", f"weights npz carries no `target` mapping (got {type(target)})")
    mode = target.get("target_mode")
    learned = target.get("refinement_is_learned_production")
    sth = target.get("signed_target_hash")
    pot = target.get("pot_scale")
    checks = [
        _ck("target:mode_is_negweight_refined", mode == "negweight-refined", mode),
        _ck("target:refinement_is_learned_production", learned is True,
            f"{learned!r} -- False means an injected/sklearn refinement, not the canonical "
            "u2d.refine_stay_positive (Delta has no ROOT); not promotable"),
        _ck("target:refinement_is_stay_positive",
            str(target.get("refinement", "")).startswith("stay-positive"),
            target.get("refinement")),
        _ck("target:signed_target_hash_bound", isinstance(sth, str) and len(sth) == 64, sth),
        _ck("target:pot_scale_valid",
            pot is not None and np.isfinite(float(pot)) and float(pot) > 0.0, pot),
        _ck("target:refined_weights_nonnegative",
            target.get("refined_min") is not None and float(target["refined_min"]) >= 0.0,
            target.get("refined_min")),
        _ck("target:refined_sum_positive",
            target.get("refined_sum") is not None and float(target["refined_sum"]) > 0.0,
            target.get("refined_sum")),
    ]
    return all(c["ok"] for c in checks), checks


def check_closure_verdicts(ordinary_pass, stress_recoil_blind, stress_fullevent_recovers):
    """Compose the two closure verdicts: ordinary closure PASS (estimator does NOT move when it must
    not) AND omitted-muon stress (recoil-only stays blind, full-event RECOVERS the injected tilt)."""
    checks = [_ck("closure:ordinary_pass", bool(ordinary_pass), ordinary_pass),
              _ck("closure:stress_recoil_blind", bool(stress_recoil_blind), stress_recoil_blind),
              _ck("closure:stress_fullevent_recovers", bool(stress_fullevent_recovers),
                  stress_fullevent_recovers)]
    return all(c["ok"] for c in checks), checks


def check_closure_provenance(ordinary, stress, powered=None):
    """Refuse closure evidence that is not the publication closure.

    Two runs in this repo look like the ordinary closure and are not it, and RESTORE-2026-08-03.md
    Step 3 refuses both in prose. This refuses them in code:

      * `--bkg-mode purity` is a LABELED CONTROL, not the nominal;
      * the 2026-07-26 Delta run (job 20489224) passed on a SYNTHETIC FIXTURE, where the
        pseudo-data IS the MC and push ~ 1 is nearly guaranteed regardless of estimator
        correctness -- "close to zero power to detect a real defect".

    It also requires the run's own CLI thresholds be no looser than FROZEN's, so a closure re-run
    with `--l1-max 0.9` cannot launder itself into a Gate-4 PASS, and requires the grid it
    histogrammed on to be the frozen extended-FPS grid.
    """
    tol = FROZEN["tolerances"]
    o = ordinary if isinstance(ordinary, dict) else {}
    s = stress if isinstance(stress, dict) else {}
    checks = [
        _ck("closure:ordinary_report_schema", o.get("report_schema") == ORDINARY_CLOSURE_SCHEMA,
            o.get("report_schema")),
        # D2 (2026-08-04). This used to require bkg_mode == negweight-refined, which is now wrong in
        # BOTH directions: it rejects the mc-only smoke, and it accepts a negweight-refined run as
        # though that run were evidence about the measured target -- which it never was, because the
        # closure built the refined target and then never referenced it
        # (AUDIT-FINDINGS-20260728.md (b)). 'purity' stays refused: it is a labeled control.
        _ck("closure:ordinary_build_mode_allowed",
            o.get("bkg_mode") in ("mc-only", BKG_MODE),
            f"{o.get('bkg_mode')!r} (mc-only or {BKG_MODE}; purity is a labeled control, never the "
            f"nominal)"),
        # An old report predates the honesty fields and would otherwise pass the checks below by
        # simply not carrying them. Require them present and correctly typed.
        _ck("closure:ordinary_declares_what_it_supports",
            (o.get("closure_class") == "mc-self-consistency-identity"
             and isinstance(o.get("is_powered_closure"), bool)
             and isinstance(o.get("mc_only"), bool)
             and isinstance(o.get("measured_target_constructed"), bool)),
            f"closure_class={o.get('closure_class')!r}, is_powered_closure="
            f"{o.get('is_powered_closure')!r}, mc_only={o.get('mc_only')!r}, "
            f"measured_target_constructed={o.get('measured_target_constructed')!r} -- a report that "
            f"does not say what it supports cannot be composed as evidence"),
        # The claim the legacy report invited: that a negweight-refined build certified the target.
        # It does not, whichever mode it ran in, because the closure's pseudo-data is MC either way.
        _ck("closure:ordinary_makes_no_measured_target_claim",
            o.get("refinement_invoked") is False,
            f"refinement_invoked={o.get('refinement_invoked')!r} -- this closure never consumes the "
            f"refined target, so a report claiming it exercised the refinement is mislabelled"),
        _ck("closure:ordinary_not_synthetic_fixture", o.get("is_synthetic_fixture") is False,
            f"is_synthetic_fixture={o.get('is_synthetic_fixture')!r} -- a synthetic-fixture run "
            "shows the code path runs and has ~no power to detect a defect"),
        _ck("closure:ordinary_thresholds_not_loosened",
            _num_le(o.get("l1_max"), tol["marginal_l1_max"])
            and _num_le(o.get("push_med_tol"), tol["push_median_dev_max"]),
            f"run l1_max={o.get('l1_max')!r} <= {tol['marginal_l1_max']}, "
            f"push_med_tol={o.get('push_med_tol')!r} <= {tol['push_median_dev_max']}"),
        _ck("closure:ordinary_push_finite", o.get("push_finite") is True, o.get("push_finite")),
        _ck("closure:ordinary_push_median",
            _num_le(abs(float(o["push_median"]) - 1.0) if _isnum(o.get("push_median"))
                    else None, tol["push_median_dev_max"]),
            f"|median(push)-1| for push_median={o.get('push_median')!r} "
            f"<= {tol['push_median_dev_max']}"),
        _ck("closure:ordinary_grid_is_frozen",
            _edges_match(o.get("edges_pt"), FROZEN["edges_pt"])
            and _edges_match(o.get("edges_pparallel"), FROZEN["edges_pparallel"]),
            "closure histogrammed on the canonical extended-FPS grid"),
        # J01: a closure is evidence about the estimator it ran on. The ordinary closure that
        # backs a `pet-fullevent-fps-v1` result must have exercised the full schema; one run on
        # {pT,p||} certifies `pet-reduced-fps-cross` and nothing else.
        _ck("closure:ordinary_schema_is_the_full_event_schema",
            [str(x) for x in (o.get("event_features_reco") or [])]
            == FROZEN["event_features_reco"]
            and [str(x) for x in (o.get("event_features_truth") or [])]
            == FROZEN["event_features_truth"],
            f"closure reco schema {o.get('event_features_reco')!r} / truth schema "
            f"{o.get('event_features_truth')!r} vs frozen "
            f"{FROZEN['event_features_reco']} / {FROZEN['event_features_truth']}"),
        _ck("closure:stress_report_schema", s.get("report_schema") == STRESS_CLOSURE_SCHEMA,
            s.get("report_schema")),
        # D2 item 4 lives in check_powered_closure(), as its own component. It used to be a
        # boolean-only check HERE, which accepted `is_powered_closure` and `recovery_criteria_met` --
        # two claims the report makes about itself. Not duplicated back into this list: two copies of
        # one rule drift apart, and the surviving copy should be the one that recomputes.
    ]
    return all(c["ok"] for c in checks), checks


def _powered_rederive(p, inputs_npz):
    """Re-derive the powered closure's four spectra FROM THE DUMP. Returns (spectra, diag, problems).

    This is the difference between checking a report and checking a RESULT. The report's own vectors
    are not inputs here: the persisted artifact gives the absolute dump rows of both halves plus the
    push weights, the tilt is recomputed by importing the closure's own function (one implementation,
    so the two sides cannot drift), and every spectrum is rebuilt from the dump's raw arrays.

    The spectra are unit-normalized, which is what makes this comparable at all: the closure
    histogrammed the DataLoader's rescaled `mc.weight` while this reads the dump's raw `w_truth`, and
    those differ by a single positive constant that unit normalization divides out.
    """
    probs = []
    art = (p.get("artifact") or {})
    apath = art.get("path")
    if not apath or not os.path.exists(apath):
        return None, {}, [f"artifact npz missing: {apath!r}"]
    got = _sha256_file(apath)
    if got != art.get("sha256"):
        return None, {}, [f"artifact sha256 {got[:16]} != reported {str(art.get('sha256'))[:16]}"]
    with np.load(apath, allow_pickle=False) as z:
        for k in ("dump_rows_a", "dump_rows_b", "weights_push"):
            if k not in z.files:
                return None, {}, [f"artifact carries no {k}"]
        rows_a = np.asarray(z["dump_rows_a"]).astype(np.int64)
        rows_b = np.asarray(z["dump_rows_b"]).astype(np.int64)
        push = np.asarray(z["weights_push"]).astype(np.float64)

    P = FROZEN["powered_closure"]
    if rows_a.size != P["half_size"] or rows_b.size != P["half_size"]:
        probs.append(f"half sizes {rows_a.size}/{rows_b.size} != {P['half_size']}")
    overlap = int(np.intersect1d(rows_a, rows_b).size)
    if overlap:
        probs.append(f"{overlap} rows appear in BOTH halves -- the split is not disjoint, which "
                     f"restores the identity shortcut and destroys the power")
    if np.unique(rows_a).size != rows_a.size or np.unique(rows_b).size != rows_b.size:
        probs.append("a half contains duplicate rows")
    if push.size != rows_b.size:
        probs.append(f"push {push.size} not aligned to half B ({rows_b.size})")
    if probs:
        return None, {"overlap_rows": overlap}, probs

    with np.load(inputs_npz, allow_pickle=True) as d:
        n = int(np.asarray(d["pass_reco"]).shape[0])
        if int(max(rows_a.max(), rows_b.max())) >= n:
            return None, {}, ["persisted rows fall outside the dump's signal inventory"]
        ts = np.asarray(d["truth_scalars"])
        pt = ts[:, fe.SCALAR_COLS["pt"]].astype(np.float64)
        pp = ts[:, fe.SCALAR_COLS["pparallel"]].astype(np.float64)
        del ts
        wt = np.asarray(d["w_truth"], dtype=np.float64)
        pgen = np.asarray(d["pass_truth"]).astype(bool)

    from closure_powered_truth_reweight import clipped_exponential_tilt, unit_spectrum
    inj = p.get("injection") or {}
    amp = float(inj.get("amplitude", P["amplitude"]))
    cz = float(inj.get("clip_z", P["clip_z"]))
    ma, mb = pgen[rows_a], pgen[rows_b]
    if not (ma.any() and mb.any()):
        return None, {}, ["a half has no truth-passing rows"]
    tilt_a = np.ones(rows_a.size, dtype=np.float64)
    tilt_on_truth, spec = clipped_exponential_tilt(pt[rows_a][ma], amplitude=amp, clip_z=cz)
    tilt_a[ma] = tilt_on_truth

    e_pt, e_pp = FROZEN["edges_pt"], FROZEN["edges_pparallel"]
    spectra = {
        "h_prior": unit_spectrum(pt[rows_b][mb], pp[rows_b][mb], wt[rows_b][mb], e_pt, e_pp),
        "h_unfolded": unit_spectrum(pt[rows_b][mb], pp[rows_b][mb],
                                    (wt[rows_b] * push)[mb], e_pt, e_pp),
        "h_target": unit_spectrum(pt[rows_a][ma], pp[rows_a][ma],
                                  (wt[rows_a] * tilt_a)[ma], e_pt, e_pp),
        "h_untilted": unit_spectrum(pt[rows_a][ma], pp[rows_a][ma], wt[rows_a][ma], e_pt, e_pp),
    }
    diag = {"overlap_rows": 0, "n_truth_a": int(ma.sum()), "n_truth_b": int(mb.sum()),
            "recomputed_tilt_min": spec["tilt_min"], "recomputed_tilt_max": spec["tilt_max"],
            "recomputed_pt_p50": spec["pt_p50"], "recomputed_pt_iqr": spec["pt_iqr"]}
    return spectra, diag, []


def check_powered_closure(powered, inputs_npz=None,
                          gate2_receipt=None):
    """Recompute the D2 powered-closure metrics FROM THE VECTORS. Returns (ok, checks).

    The first version of this gate accepted `is_powered_closure` and `recovery_criteria_met` -- two
    booleans the report asserts about itself. That is the same self-agreeing shape this repo's audits
    keep finding (four of six freeze checks comparing FROZEN to itself; a binned check that scaled
    both histograms identically and so agreed while being equally wrong). A report can claim
    recovery; only arithmetic on its spectra can establish it.

    So every acceptance number below is recomputed here from `h_prior`, `h_target`, `h_unfolded` and
    `h_untilted`, and the report's OWN metrics block must agree with the recomputation -- which
    catches a doctored metrics block that a criteria-only check would wave through. The protocol
    itself (injection amplitude, disjoint 2M/2M split, seed, nominal configuration) is checked
    against FROZEN, because criteria are only meaningful for the experiment they were declared for.
    """
    P = FROZEN["powered_closure"]
    p = powered if isinstance(powered, dict) else {}
    if not p:
        # An `:evidence_supplied` check exists ONLY when evidence is MISSING -- that is the shape
        # `_missing` uses, and a complete submission must carry none of them (audit B2: a gate is
        # allowed to fail, not to abstain and call it a pass). Emitting one unconditionally, even
        # passing, would put an evidence_supplied entry in every healthy receipt.
        return False, [_ck("powered:evidence_supplied", False,
                           "a powered injected-truth-reweight recovery closure report is REQUIRED: "
                           "the identity closure is optimized by a null estimator and cannot stand "
                           "in for it (D2)")]
    checks = [_ck("powered:report_schema", p.get("report_schema") == P["report_schema"],
                  p.get("report_schema"))]

    vecs, vec_ok = {}, True
    for name in ("h_prior", "h_target", "h_unfolded", "h_untilted"):
        v = p.get(name)
        good = isinstance(v, list) and len(v) == N_CELLS
        arr = np.asarray(v, dtype=float) if good else None
        if good:
            good = bool(np.all(np.isfinite(arr)) and np.all(arr >= -1e-12)
                        and abs(float(arr.sum()) - 1.0) <= 1e-6)
        checks.append(_ck(f"powered:vector_{name}", good,
                          f"{name}: {N_CELLS} cells, finite, non-negative, unit sum "
                          f"(len={len(v) if isinstance(v, list) else None}, "
                          f"sum={float(arr.sum()) if arr is not None else None})"))
        vec_ok = vec_ok and good
        vecs[name] = arr
    checks.append(_ck("powered:grid_is_frozen",
                      _edges_match(p.get("edges_pt"), FROZEN["edges_pt"])
                      and _edges_match(p.get("edges_pparallel"), FROZEN["edges_pparallel"]),
                      "powered closure histogrammed on the canonical extended-FPS grid"))
    checks.append(_ck("powered:bin_order", p.get("bin_order") == FROZEN["bin_order"],
                      p.get("bin_order")))

    inj = p.get("injection") or {}
    checks.append(_ck("powered:injection_amplitude",
                      _isnum(inj.get("amplitude"))
                      and abs(float(inj["amplitude"]) - P["amplitude"]) <= 1e-12,
                      f"amplitude={inj.get('amplitude')!r} (predeclared {P['amplitude']})"))
    checks.append(_ck("powered:injection_clip_z",
                      _isnum(inj.get("clip_z"))
                      and abs(float(inj["clip_z"]) - P["clip_z"]) <= 1e-12,
                      f"clip_z={inj.get('clip_z')!r} (predeclared {P['clip_z']})"))
    checks.append(_ck("powered:injection_on_truth_rows_only",
                      str(inj.get("applied_on", "")).startswith("pass_truth"),
                      f"applied_on={inj.get('applied_on')!r} -- a truth-level reweighting is only "
                      f"defined where a truth record exists"))
    checks.append(_ck("powered:step1_population",
                      (p.get("samples") or {}).get("step1_population") == P["step1_population"],
                      f"{(p.get('samples') or {}).get('step1_population')!r} vs predeclared "
                      f"{P['step1_population']!r}"))
    checks.append(_ck("powered:injection_rate_preserving",
                      inj.get("rate_preserving") is P["rate_preserving"],
                      f"rate_preserving={inj.get('rate_preserving')!r} -- a rate change would let a "
                      f"pure normalization fix look like shape recovery"))
    smp = p.get("samples") or {}
    checks.append(_ck("powered:samples_disjoint_as_declared",
                      smp.get("disjoint") is True
                      and smp.get("half_size") == P["half_size"]
                      and smp.get("split_seed") == P["split_seed"],
                      f"disjoint={smp.get('disjoint')!r}, half_size={smp.get('half_size')!r}, "
                      f"split_seed={smp.get('split_seed')!r} (predeclared "
                      f"{P['half_size']}/{P['half_size']}, seed {P['split_seed']}) -- an "
                      f"overlapping split restores the identity shortcut and the power goes to zero"))
    cfg = p.get("configuration") or {}
    sp = FROZEN["seed_policy"]
    checks.append(_ck("powered:nominal_configuration",
                      all(cfg.get(k) == sp[k] for k in ("niter", "epochs", "estimator_seed",
                                                        "subsample_seed", "batch_size")),
                      f"{ {k: cfg.get(k) for k in ('niter','epochs','estimator_seed','subsample_seed','batch_size')} } "
                      f"vs frozen { {k: sp[k] for k in ('niter','epochs','estimator_seed','subsample_seed','batch_size')} } "
                      f"-- batch_size changes the optimizer trajectory, so it is part of the config"))
    checks.append(_ck("powered:estimator_and_schema",
                      p.get("estimator_fingerprint") == ESTIMATOR_FINGERPRINT
                      and [str(x) for x in (p.get("event_features_reco") or [])]
                      == FROZEN["event_features_reco"]
                      and [str(x) for x in (p.get("event_features_truth") or [])]
                      == FROZEN["event_features_truth"],
                      f"fingerprint={p.get('estimator_fingerprint')!r}; a closure on another schema "
                      f"is evidence about another estimator (J01)"))
    checks.append(_ck("powered:reco_leg_is_w_reco", p.get("reco_leg_weight_used") == "w_reco",
                      f"reco_leg_weight_used={p.get('reco_leg_weight_used')!r} (D1)"))
    checks.append(_ck("powered:input_identity_recorded",
                      bool(p.get("input_identity_hashes")),
                      "the inventory identity hashes the run consumed, so the closure is bound to a "
                      "dump rather than floating free"))

    if not vec_ok:
        checks.append(_ck("powered:recomputed_metrics", False,
                          "spectra unusable, so gap/floor/residual cannot be recomputed -- the "
                          "report's own numbers are NOT accepted as a substitute"))
        return all(c["ok"] for c in checks), checks

    # ---- INDEPENDENT RE-DERIVATION. The acceptance numbers come from HERE, not from the report ----
    # Checking the report's own vectors would still be checking the report. The artifact's absolute
    # dump rows plus the push weights let the gate rebuild every spectrum from the dump, recompute the
    # tilt through the closure's own function, and test disjointness on the ACTUAL index arrays
    # rather than on a `disjoint: true` field the report asserts about itself.
    if not inputs_npz:
        checks.append(_ck("powered:independent_rederivation", False,
                          "no --inputs given, so the powered closure cannot be re-derived from the "
                          "dump; its report is not accepted on its own authority (fail closed)"))
        return all(c["ok"] for c in checks), checks
    rederived, diag, problems = _powered_rederive(p, inputs_npz)
    checks.append(_ck("powered:artifact_and_split_verified", not problems,
                      "; ".join(problems) if problems else
                      f"artifact hash matches, halves are {P['half_size']}+{P['half_size']} with "
                      f"{diag.get('overlap_rows')} overlapping rows, push aligned to half B"))
    if rederived is None:
        checks.append(_ck("powered:independent_rederivation", False,
                          "re-derivation could not run, and the report's own spectra are NOT "
                          "accepted as a substitute"))
        return all(c["ok"] for c in checks), checks

    satol = P["spectrum_agreement_atol"]
    for name, ours in rederived.items():
        theirs = vecs[name]
        dmax = float(np.max(np.abs(ours - theirs)))
        checks.append(_ck(f"powered:spectrum_matches_rederivation_{name}", dmax <= satol,
                          f"max|reported-rederived| = {dmax:.3e} <= {satol:g}"))

    gap = float(np.abs(rederived["h_prior"] - rederived["h_target"]).sum())
    floor = float(np.abs(rederived["h_prior"] - rederived["h_untilted"]).sum())
    resid = float(np.abs(rederived["h_unfolded"] - rederived["h_target"]).sum())
    fog = (floor / gap) if gap > 0 else None
    rog = (resid / gap) if gap > 0 else None

    # Identity VALUES, not merely presence: the inventory the closure consumed must be the one the
    # Gate-2 receipt was built against, or the closure certifies a different dump's estimator.
    if gate2_receipt is not None:
        want = ((gate2_receipt.get("runtime_target") or {}).get("input_identity_hashes")) or {}
        got = p.get("input_identity_hashes") or {}
        shared = sorted(set(want) & set(got))
        checks.append(_ck("powered:identity_values_match_gate2",
                          bool(shared) and all(got[k] == want[k] for k in shared),
                          f"compared {shared or 'NOTHING -- no overlapping inventory keys'}: "
                          + "; ".join(f"{k}:{'ok' if got.get(k) == want.get(k) else 'MISMATCH'}"
                                      for k in shared)))
    src = p.get("source") or {}
    checks.append(_ck("powered:source_dump_digest_matches",
                      bool(src.get("inputs_sha256"))
                      and src["inputs_sha256"] == _sha256_file(inputs_npz),
                      f"report inputs_sha256={str(src.get('inputs_sha256'))[:16]} vs this gate's own "
                      f"read of --inputs"))
    checks.append(_ck("powered:producer_receipt_bound", bool(src.get("producer_receipt_sha256")),
                      f"producer_receipt_sha256={str(src.get('producer_receipt_sha256'))[:16]}"))

    checks.append(_ck("powered:gap_is_large_enough", gap >= P["gap_min"],
                      f"recomputed gap={gap:.6f} >= {P['gap_min']} -- below this there is no "
                      f"injected signal to recover and a pass would be vacuous"))
    checks.append(_ck("powered:floor_small_against_gap",
                      fog is not None and fog <= P["floor_over_gap_max"],
                      f"recomputed floor/gap={fog if fog is None else round(fog, 6)} <= "
                      f"{P['floor_over_gap_max']} -- bounds how much of `gap` is sample-split noise "
                      f"between the two disjoint halves rather than injection"))
    checks.append(_ck("powered:recovery_meets_criterion",
                      rog is not None and rog <= P["residual_over_gap_max"],
                      f"recomputed residual/gap={rog if rog is None else round(rog, 6)} <= "
                      f"{P['residual_over_gap_max']} (recovery "
                      f"{None if rog is None else round(1.0 - rog, 6)} >= "
                      f"{round(1.0 - P['residual_over_gap_max'], 6)})"))

    # A doctored metrics block cannot slip past a criteria-only check, so compare it too.
    claimed = p.get("metrics") or {}
    atol = P["metric_agreement_atol"]
    agree = all(_isnum(claimed.get(k)) and abs(float(claimed[k]) - v) <= atol
                for k, v in (("gap", gap), ("floor", floor), ("residual", resid)))
    checks.append(_ck("powered:reported_metrics_match_recomputation", agree,
                      f"report claims gap={claimed.get('gap')!r} floor={claimed.get('floor')!r} "
                      f"residual={claimed.get('residual')!r}; recomputed "
                      f"{gap:.9f}/{floor:.9f}/{resid:.9f}"))
    return all(c["ok"] for c in checks), checks


def _isnum(x):
    try:
        return np.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _num_le(x, bound):
    return bool(_isnum(x) and float(x) <= float(bound))


def _edges_match(observed, frozen, tol=1e-9):
    if observed is None:
        return False
    o = np.asarray(observed, float)
    f = np.asarray(frozen, float)
    return bool(o.shape == f.shape and np.allclose(o, f, atol=tol, rtol=0))


def check_freeze(observed):
    """Verify a nominal result's declared contract against the FROZEN policy (fingerprint, edges, bin
    geometry/order, seed/config) and the central vector's length/finiteness/order.

    EVERY value in `observed` must come from the artifact under test. Passing FROZEN's own entries
    in is a self-comparison that cannot fail -- audit B2 found four of the six freeze checks in that
    state, and the central-vector / reported-mask checks not running at all because main() never
    populated the keys. Absent keys therefore FAIL here rather than being skipped."""
    checks = []
    checks.append(_ck("freeze:fingerprint", observed.get("estimator_fingerprint")
                      == ESTIMATOR_FINGERPRINT, observed.get("estimator_fingerprint")))
    checks.append(_ck("freeze:bkg_mode", observed.get("bkg_mode") == BKG_MODE,
                      observed.get("bkg_mode")))
    checks.append(_ck("freeze:edges_pt", _edges_match(observed.get("edges_pt"), FROZEN["edges_pt"]),
                      "pt edges"))
    checks.append(_ck("freeze:edges_pparallel",
                      _edges_match(observed.get("edges_pparallel"), FROZEN["edges_pparallel"]),
                      "p|| edges"))
    checks.append(_ck("freeze:bin_order", observed.get("bin_order") == FROZEN["bin_order"],
                      observed.get("bin_order")))
    checks.append(_ck("freeze:seed_policy", observed.get("seed_policy") == FROZEN["seed_policy"],
                      observed.get("seed_policy")))
    # ---- J01: the fingerprint has to mean the schema it names ----
    feat_r = observed.get("event_features_reco")
    feat_t = observed.get("event_features_truth")
    if feat_r is None or feat_t is None:
        checks.append(_ck(
            "freeze:event_feature_schema_present", False,
            "NOT SUPPLIED: the artifact declares no event-feature schema, so nothing establishes "
            f"that a result stamped {ESTIMATOR_FINGERPRINT!r} was trained on the full schema that "
            "fingerprint names. Produced by a driver predating the J01 fix."))
    else:
        feat_r = [str(x) for x in np.asarray(feat_r).ravel().tolist()]
        feat_t = [str(x) for x in np.asarray(feat_t).ravel().tolist()]
        checks.append(_ck("freeze:event_features_reco", feat_r == FROZEN["event_features_reco"],
                          f"{feat_r} vs frozen {FROZEN['event_features_reco']}"))
        checks.append(_ck("freeze:event_features_truth", feat_t == FROZEN["event_features_truth"],
                          f"{feat_t} vs frozen {FROZEN['event_features_truth']}"))
        # Stated separately from the equality above, and deliberately redundant with it: this is
        # the specific substitution J01 found in the tree, and a named failing check is worth more
        # in a receipt than "the list differs".
        checks.append(_ck(
            "freeze:not_the_reduced_cross_check_schema",
            feat_r != FROZEN["reduced_cross_check_features"],
            f"reco schema is {feat_r}; {FROZEN['reduced_cross_check_features']} is "
            "`pet-reduced-fps-cross`, a CROSS-CHECK that may never be a publication source"))
        # The detector quantities have no truth counterpart; one appearing on the truth leg is a
        # leak that survived the loader's own guard only if the artifact was hand-built.
        leaked = sorted(set(feat_t) & set(fe.DETECTOR_ONLY_FEATURES))
        checks.append(_ck("freeze:no_detector_feature_on_the_truth_leg", not leaked,
                          f"detector-only features on event_truth: {leaked}" if leaked
                          else "truth leg reads truth-eligible quantities only"))
    cloud_cols = observed.get("reco_cloud_cols")
    if cloud_cols is None:
        checks.append(_ck(
            "freeze:reco_cloud_cols_present", False,
            "NOT SUPPLIED: the artifact does not record the reco cloud's token columns, so a run "
            "that dropped the G2 view/timing columns is indistinguishable from one that read "
            "them"))
    else:
        cloud_cols = [str(x) for x in np.asarray(cloud_cols).ravel().tolist()]
        checks.append(_ck("freeze:reco_cloud_cols", cloud_cols == FROZEN["reco_cloud_cols"],
                          f"{cloud_cols} vs frozen {FROZEN['reco_cloud_cols']}"))
    cv = observed.get("central_vector")
    mask = observed.get("reported_bin_mask")
    if cv is None:
        checks.append(_ck("freeze:central_vector_present", False,
                          "NOT SUPPLIED: the artifact carries no central_vector, so its length / "
                          "finiteness / bin order are unchecked"))
    else:
        cv = np.asarray(cv, float)
        checks.append(_ck("freeze:central_vector_len", cv.shape == (N_CELLS,), cv.shape))
        checks.append(_ck("freeze:central_vector_finite", bool(np.all(np.isfinite(cv))), "finite"))
        checks.append(_ck("freeze:central_vector_nonnegative", bool(np.all(cv >= 0.0)),
                          f"min={float(cv.min()) if cv.size else None}"))
        checks.append(_ck("freeze:central_vector_nonzero", bool(np.any(cv > 0.0)),
                          "some reported cell is populated"))
    if mask is None:
        checks.append(_ck("freeze:reported_mask_present", False,
                          "NOT SUPPLIED: the artifact carries no reported_bin_mask, so the "
                          "reporting mask and its order are untouched by the gate"))
    else:
        m = np.asarray(mask)
        checks.append(_ck("freeze:reported_mask_len", m.shape == (N_CELLS,), m.shape))
        mb = np.asarray(m, bool)
        checks.append(_ck("freeze:reported_mask_nonempty", bool(mb.any()),
                          f"{int(mb.sum())} of {mb.size} cells reported"))
        if cv is not None and cv.shape == (N_CELLS,) and mb.shape == (N_CELLS,):
            # Order agreement between the two 285-vectors: a reshuffled central vector would
            # populate cells the mask calls empty.
            checks.append(_ck("freeze:central_vector_zero_outside_mask",
                              bool(np.all(cv[~mb] == 0.0)),
                              f"{int((cv[~mb] != 0.0).sum())} populated cells outside the mask"))
    return all(c["ok"] for c in checks), checks


def build_gate4_report(*, result_meta, frozen_observed, weights_push=None, imc=None, n_full=None,
                       n_expected_subsample=None, marginal=None, saturation_frac=None,
                       closure=None, closure_reports=None, observed_at_utc=None, fold_forward=None,
                       fold_forward_driver=None, fold_forward_telemetry=None, target=None,
                       powered_inputs_npz=None, powered_gate2_receipt=None,
                       spectra=None, spectra_driver=None, spectra_telemetry=None):
    """Assemble the Gate-4 receipt + single verdict. Pure (no training). `marginal`=(h_truth,h_rw);
    `closure`=(ordinary,recoil_blind,fullevent_recovers);
    `closure_reports`=(ordinary, stress[, powered_recovery]) as
    written by the two closure scripts' `--json`.

    `fold_forward`=(sum_w_push_reco, sum_w_reco, R) is the B1 §2d normalization gate -- the
    validator's OWN recomputation from the G2 dump. `fold_forward_driver` is the same triple as
    persisted by the driver; their agreement is asserted. `spectra`/`spectra_driver` are the
    matching pair for (central_vector, reported_bin_mask, cap_saturation_frac).

    ABSENT EVIDENCE FAILS. Every component below either runs or contributes an explicit failing
    `<component>:evidence_supplied` check. The pre-08-03 builder skipped any component whose
    argument was None, which is how `marginal`, `normalization`, `saturation_frac` and `closure`
    came to be evaluated by nothing while the receipt reported `verdict PASS, n_failed 0` and
    embedded their tolerances (audit B2). A gate is allowed to fail; it is not allowed to abstain
    and call that a pass."""
    checks, comps = [], {}

    def add(component, ok, cks):
        checks.extend(cks)
        comps[component] = bool(ok)

    add("freeze", *check_freeze(frozen_observed))
    if weights_push is None:
        add("weights", *_missing("weights", "no weights_push in the artifact"))
    else:
        add("weights", *check_weights_finite_coverage(
            weights_push, len(imc) if (imc is not None and hasattr(imc, "__len__")) else n_full))
    if imc is None:
        add("index_order", *_missing("index_order", "no mc_indices in the artifact"))
    else:
        add("index_order", *check_mc_index_order(imc, n_full, n_expected_subsample))
    if marginal is None:
        add("marginal", *_missing(
            "marginal", "no (pT,p_parallel) closure histograms -- the ordinary closure report must "
                        "carry them (closure_fullevent_fps.py --json)"))
    else:
        m_ok, mc, _l1 = check_marginal_closure(*marginal)
        add("marginal", m_ok, mc)
    if fold_forward is None:
        add("fold_forward", *_missing(
            "fold_forward", "no reco-level fold-forward sums; see --allow-missing-fold-forward"))
        add("fold_forward_independence", *_missing(
            "fold_forward_independence", "no fold-forward sums to cross-check"))
    else:
        add("fold_forward", *check_fold_forward_ratio(*fold_forward))
        if fold_forward_driver is None:
            add("fold_forward_independence", *_missing(
                "fold_forward_independence",
                "the driver persisted no fold-forward sums, so the gate would be certifying its "
                "own arithmetic"))
        else:
            add("fold_forward_independence",
                *check_fold_forward_independence(fold_forward, fold_forward_driver))
    if spectra is None or spectra_driver is None:
        add("spectra_independence", *_missing(
            "spectra_independence",
            "the reporting spectra were not available from both the dump and the artifact"))
    else:
        add("spectra_independence", *check_spectra_independence(spectra, spectra_driver))
    if saturation_frac is None:
        add("cap", *_missing("cap", "no logit-cap saturation fraction"))
    else:
        add("cap", *check_cap_sensitivity(saturation_frac))
    if target is None:
        add("target", *_missing("target", "no measured-target provenance block"))
    else:
        add("target", *check_target_provenance(target))
    if closure is None:
        add("closure", *_missing(
            "closure", "no closure verdicts -- Gate-4 composes the ordinary and omitted-muon "
                       "stress closures and cannot certify a result without them"))
    else:
        add("closure", *check_closure_verdicts(*closure))
    if closure_reports is None:
        add("closure_provenance", *_missing(
            "closure_provenance", "no closure reports, so purity-control and synthetic-fixture "
                                  "runs cannot be told apart from the publication closure"))
    else:
        add("closure_provenance", *check_closure_provenance(*closure_reports))
    # D2: recomputed from the powered closure's own spectra, never from its verdict.
    add("powered_closure", *check_powered_closure(
        closure_reports[2] if (closure_reports and len(closure_reports) > 2) else None,
        inputs_npz=powered_inputs_npz, gate2_receipt=powered_gate2_receipt))

    verdict = bool(checks) and all(c["ok"] for c in checks)
    payload = {
        "receipt_schema": RECEIPT_SCHEMA, "verdict": "PASS" if verdict else "FAIL",
        "observed_at_utc": observed_at_utc, "nominal_pet_training_allowed": False,
        "result": dict(result_meta), "frozen_contract": FROZEN,
        "component_verdicts": comps, "checks": checks,
        "n_checks": len(checks), "n_failed": sum(1 for c in checks if not c["ok"])}
    if fold_forward is not None:
        v_push, v_w, v_R = (float(x) for x in fold_forward)
        payload["fold_forward"] = {
            "validator_sum_w_push_reco": v_push, "validator_sum_w_reco": v_w,
            "validator_reco_weighted_mean_push": (v_push / v_w) if v_w else None,
            "validator_R": v_R,
            "driver": ([float(x) for x in fold_forward_driver]
                       if fold_forward_driver is not None else None),
            "tolerance_status": FROZEN["tolerances"]["fold_forward_ratio_dev_max_status"],
            "telemetry": fold_forward_telemetry,
        }
    if spectra is not None:
        v_cv, v_mask, v_sat = spectra
        payload["reporting_spectra"] = {
            "validator_n_reported_cells": int(np.asarray(v_mask, bool).sum()),
            "validator_central_vector_sum": float(np.asarray(v_cv, float).sum()),
            "validator_cap_saturation_frac": float(v_sat),
            "logit_cap": FROZEN["reweight_logit_cap"],
            "telemetry": spectra_telemetry,
        }
    if closure_reports is not None:
        # D2: the tuple grew a third member (the powered recovery closure). Unpacked tolerantly so a
        # 2-tuple from an older caller still works and simply carries no powered report -- which the
        # provenance check then fails closed on, rather than crashing here.
        o, s = closure_reports[0], closure_reports[1]
        pw = closure_reports[2] if len(closure_reports) > 2 else None
        payload["closure_evidence"] = {"ordinary": o, "stress": s, "powered_recovery": pw}
    if target is not None:
        payload["measured_target"] = target
    return payload, verdict


def write_work_receipt(work_path, payload):
    """Atomic WORK-only write (unique temp + fsync + os.replace). Never a production artifact."""
    directory = os.path.dirname(os.path.abspath(work_path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".gate4_nom_", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2, default=str)
            fh.write("\n"); fh.flush(); os.fsync(fh.fileno())
        os.replace(tmp, work_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return work_path


def _sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def _npz_get(z, key, default=None):
    """Read a persisted scalar/array/mapping member, or `default` when the driver omitted it."""
    if key not in z.files:
        return default
    v = z[key]
    if isinstance(v, np.ndarray) and v.dtype == object and v.shape == ():
        return v.item()
    if isinstance(v, np.ndarray) and v.ndim == 0:
        item = v.item()
        return item.decode() if isinstance(item, bytes) else item
    return v


def _read_report(path, label):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"[gate4] cannot read the {label} closure report {path!r}: {exc} "
                         "(fail closed)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate-4 nominal validator (runtime; needs a trained result)")
    ap.add_argument("--nominal-weights", required=True, help="nominal weights npz (from the driver)")
    ap.add_argument("--work", required=True, help="caller-supplied WORK receipt path (JSON)")
    ap.add_argument("--n-full", type=int, default=None,
                    help="OPTIONAL cross-check only. The authoritative signal-inventory row count "
                         "is read from the dump; supplying a different one fails closed.")
    # B1 §2d: the G2 dump the result was trained against. REQUIRED, because without it the
    # normalization check is not computable and would be silently skipped -- which is exactly the
    # state this gate was in before the B1 fix: a correct assertion that never executes.
    ap.add_argument("--inputs", required=True,
                    help="the G2 dump the nominal was trained on (g2-fullevent-v1 npz). Required: "
                         "the fold-forward normalization gate recomputes its reference sums and R "
                         "from it, independently of the driver.")
    # The two closure verdicts Gate-4 COMPOSES. Required for the same reason as --inputs: the
    # `closure=` argument was never wired, so `closure:ordinary_pass`,
    # `closure:stress_recoil_blind` and `closure:stress_fullevent_recovers` never executed.
    ap.add_argument("--closure-report", required=True,
                    help="JSON report from closure_fullevent_fps.py --json (the ordinary closure). "
                         "Carries the (pT,p||) marginal histograms this gate re-derives its L1 "
                         "from, the push median, and the run's bkg_mode / fixture provenance.")
    ap.add_argument("--stress-report", required=True,
                    help="JSON report from stress_closure_muon.py --json (the omitted-muon stress "
                         "closure: recoil-only stays blind, full-event recovers the tilt).")
    ap.add_argument("--powered-inputs", default=None,
                    help="the dump the POWERED closure was run on, which Gate-4 re-derives its "
                         "spectra from. Defaults to --inputs, and in a real run they are the same "
                         "file. It is a separate flag only because the powered closure may legally "
                         "have been run in an earlier job against the same certified inventory; the "
                         "binding is enforced by digest (source.inputs_sha256) and by comparing the "
                         "consumed identity VALUES against the Gate-2 receipt, not by path.")
    ap.add_argument("--gate2-receipt", default=None,
                    help="the Gate-2 runtime receipt. Used to compare the powered closure's "
                         "consumed inventory identity VALUES against the ones Gate-2 was built "
                         "against, so a closure on another dump cannot certify this estimator.")
    ap.add_argument("--powered-closure-report", default=None,
                    help="JSON report from the D2 injected truth-reweight RECOVERY closure, at "
                         "nominal configuration with predeclared recovery criteria "
                         "(is_powered_closure=true, recovery_criteria_met=true). Optional as a flag "
                         "but REQUIRED for a PASS: the ordinary identity closure has ~no power to "
                         "detect a real defect, so it cannot stand in for this.")
    ap.add_argument("--allow-missing-fold-forward", action="store_true",
                    help="DIAGNOSTIC ONLY. Skip the fold-forward gate when the weights npz "
                         "predates the B1 fix. A receipt produced this way does not certify the "
                         "normalization and must not be promoted.")
    args = ap.parse_args(argv)
    import datetime
    z = np.load(args.nominal_weights, allow_pickle=True)

    # ---- the freeze reads the ARTIFACT, never FROZEN (rule 2 of the module docstring) ----
    seed_policy = _npz_get(z, "seed_policy")
    frozen_observed = {
        "estimator_fingerprint": _npz_get(z, "estimator_fingerprint"),
        "bkg_mode": _npz_get(z, "bkg_mode"),
        "edges_pt": _npz_get(z, "edges_pt"),
        "edges_pparallel": _npz_get(z, "edges_pparallel"),
        "bin_order": _npz_get(z, "bin_order"),
        # dict(...) so a persisted mapping compares equal to FROZEN's plain dict
        "seed_policy": dict(seed_policy) if isinstance(seed_policy, dict) else seed_policy,
        "central_vector": _npz_get(z, "central_vector"),
        "reported_bin_mask": _npz_get(z, "reported_bin_mask"),
        # J01: read from the artifact, never from FROZEN (rule 2 of the module docstring).
        "event_features_reco": _npz_get(z, "event_features_reco"),
        "event_features_truth": _npz_get(z, "event_features_truth"),
        "reco_cloud_cols": _npz_get(z, "reco_cloud_cols"),
    }
    target = _npz_get(z, "target")

    # ---- B1 §2d: assemble the fold-forward gate's two sides ----
    fold_forward = fold_forward_driver = fold_forward_telemetry = None
    spectra = spectra_driver = spectra_telemetry = None
    n_full = args.n_full
    driver_keys = ("fold_forward_sum_w_push_reco", "fold_forward_sum_w_reco", "step1_class_ratio")
    missing = [k for k in driver_keys if k not in z.files]
    if missing and not args.allow_missing_fold_forward:
        raise SystemExit(
            f"[gate4] weights npz {args.nominal_weights} lacks {missing} -- it was produced by a "
            "driver predating the B1 fix, so the fold-forward normalization gate cannot run. "
            "Re-run the driver, or pass --allow-missing-fold-forward for a diagnostic (NOT "
            "promotable) receipt.")
    if not missing:
        strap = int(z["bootstrap_seed"]) if "bootstrap_seed" in z.files else -1
        if strap != -1:
            raise SystemExit(
                f"[gate4] weights npz declares bootstrap_seed={strap}. The validator's independent "
                "recomputation reconstructs the NOMINAL inventory only; a replica's R is built "
                "from its own coherent draws, which are not in this file. This gate certifies the "
                "nominal (fail closed).")
        # The driver records the dump it trained against, by path AND by content. Without comparing
        # them the validator simply believes whatever --inputs the caller passed, so a DIFFERENT
        # dump can silently become the reference for every sum below -- the reference data being
        # independent of the driver is the whole point of §2d. The basename check catches the
        # ordinary mistake (the dump is legitimately re-staged between filesystems, so paths must
        # not be compared whole); the sha256 makes it a CONTENT bind, which the 07-29 patch flagged
        # as belonging to this re-issue. Found by adversarial review of b3751cc.
        driver_inputs = _npz_get(z, "inputs_path")
        if driver_inputs and (os.path.basename(str(driver_inputs))
                              != os.path.basename(os.path.abspath(args.inputs))):
            raise SystemExit(
                f"[gate4] --inputs {args.inputs!r} is not the dump this result was trained on "
                f"({driver_inputs!r}). The fold-forward reference sums would come from a different "
                "inventory than the weights (fail closed).")
        driver_inputs_sha = _npz_get(z, "inputs_sha256")
        if driver_inputs_sha:
            observed_sha = _sha256_file(args.inputs)
            if str(driver_inputs_sha) != observed_sha:
                raise SystemExit(
                    f"[gate4] --inputs {args.inputs!r} sha256 {observed_sha} != the dump this "
                    f"result was trained on ({driver_inputs_sha}). Same basename, different "
                    "content (fail closed).")
        v_push, v_w, v_R, fold_forward_telemetry = fold_forward_sums_from_dump(
            args.inputs, z["weights_push"], z["mc_indices"])
        fold_forward = (v_push, v_w, v_R)
        fold_forward_driver = (float(z["fold_forward_sum_w_push_reco"]),
                               float(z["fold_forward_sum_w_reco"]),
                               float(z["step1_class_ratio"]))
        inventory = fold_forward_telemetry.get("n_signal_inventory")
        if n_full is None:
            n_full = inventory
        elif inventory is not None and int(n_full) != int(inventory):
            raise SystemExit(f"[gate4] --n-full {n_full} != the dump's signal inventory "
                             f"{inventory} (fail closed)")
        # The freeze checks run on the DRIVER's spectra; this is the independent side.
        v_cv, v_mask, spectra_telemetry = nominal_spectra_from_dump(
            args.inputs, z["weights_push"], z["mc_indices"])
        v_sat = cap_saturation_frac_from_push(z["weights_push"])
        spectra = (v_cv, v_mask, v_sat)
        spectra_driver = (_npz_get(z, "central_vector"), _npz_get(z, "reported_bin_mask"),
                          _npz_get(z, "cap_saturation_frac"))
        if any(x is None for x in spectra_driver):
            spectra_driver = None

    ordinary = _read_report(args.closure_report, "ordinary")
    stress = _read_report(args.stress_report, "omitted-muon stress")
    powered = (_read_report(args.powered_closure_report, "powered recovery closure")
               if args.powered_closure_report else None)
    target_receipt_payload = None
    if args.gate2_receipt:
        try:
            target_receipt_payload = json.load(open(args.gate2_receipt))
        except (json.JSONDecodeError, OSError) as exc:
            raise SystemExit(f"[gate4] --gate2-receipt unreadable ({exc}); fail closed")
    marginal = None
    if isinstance(ordinary.get("marginal_h_truth"), list) \
            and isinstance(ordinary.get("marginal_h_reweighted"), list):
        marginal = (ordinary["marginal_h_truth"], ordinary["marginal_h_reweighted"])
    closure = (ordinary.get("pass") is True,
               stress.get("recoil_only_fails_to_recover") is True,
               stress.get("fullevent_recovers") is True)

    payload, verdict = build_gate4_report(
        result_meta={"path": os.path.abspath(args.nominal_weights),
                     "sha256": _sha256_file(args.nominal_weights),
                     "inputs_path": os.path.abspath(args.inputs),
                     "inputs_sha256_declared_by_driver": _npz_get(z, "inputs_sha256"),
                     "closure_report": os.path.abspath(args.closure_report),
                     "stress_report": os.path.abspath(args.stress_report)},
        frozen_observed=frozen_observed,
        weights_push=z["weights_push"] if "weights_push" in z.files else None,
        imc=z["mc_indices"] if "mc_indices" in z.files else None, n_full=n_full,
        n_expected_subsample=FROZEN["seed_policy"]["train_events"],
        marginal=marginal, saturation_frac=(spectra[2] if spectra is not None else None),
        closure=closure, closure_reports=(ordinary, stress, powered), target=target,
        # D2: the powered closure is re-derived from THIS dump, and its consumed inventory is
        # compared against the Gate-2 receipt's actual identity values.
        powered_inputs_npz=(args.powered_inputs or args.inputs),
        powered_gate2_receipt=target_receipt_payload,
        fold_forward=fold_forward, fold_forward_driver=fold_forward_driver,
        fold_forward_telemetry=fold_forward_telemetry,
        spectra=spectra, spectra_driver=spectra_driver, spectra_telemetry=spectra_telemetry,
        observed_at_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    if fold_forward is None:
        # A skipped normalization gate must NOT read as green. Previously this produced
        # verdict PASS and exit 0 with only a buried `promotable: false` dissenting -- so any
        # consumer checking the exit status or the verdict string saw a pass, which is the exact
        # B2 failure (a check that does not run) one level up. Found by adversarial review of
        # b3751cc. The flag is diagnostic; a diagnostic run is not a PASS.
        payload["fold_forward"] = {"skipped": True, "promotable": False,
                                   "reason": f"--allow-missing-fold-forward; npz lacks {missing}"}
        payload["verdict"] = "FAIL_NORMALIZATION_NOT_CHECKED"
        payload["component_verdicts"]["fold_forward"] = False
        verdict = False
    write_work_receipt(args.work, payload)
    print(json.dumps({"verdict": payload["verdict"], "n_failed": payload["n_failed"],
                      "component_verdicts": payload["component_verdicts"]}, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
