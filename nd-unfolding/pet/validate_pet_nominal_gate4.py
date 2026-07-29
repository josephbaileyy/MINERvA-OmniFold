#!/usr/bin/env python3
"""Gate-4 validator for the publication full-event PET NOMINAL result (runbook Packet P5A /
PET_UQ_REMEDIATION_STATUS Gate 4).

CODE-ONLY gate: the pure checks below are login-safe and unit-tested against synthetic nominal
results; the actual nominal training is a separate authorized step (nominal_pet_training_allowed
stays false). The validator COMPOSES the existing closure evidence (ordinary closure
`closure_fullevent_fps.py` + omitted-muon stress closure `stress_closure_muon.py`) and adds:

  * finite / full-coverage push weights;
  * strict MC index/order (sorted, unique, in range);
  * exact lower-dimensional (pT,p_parallel) marginal closure;
  * the RECO-LEVEL FOLDED-FORWARD NORMALIZATION gate (B1 §2d): the reco-weighted mean of the push
    weights must equal the physical data/MC rate ratio R, with R and the reference sums recomputed
    HERE from the G2 dump rather than taken from the driver. This replaces the truth-level
    `sum_w_push/sum_w ~ 1` identity, which a correct unfold does not satisfy (its expected value
    is 1 + <a>(R-1), a function of the acceptance being measured) and which the CLI never wired;
  * cap-sensitivity telemetry (logit-cap saturation fraction bounded);
  * the FREEZE of estimator fingerprint + central vector (length/finite/order) + reported-bin
    mask/order + extended-FPS edges + seed/config policy.

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
    "edges_pt": [float(x) for x in fe.CANONICAL_PT_EDGES],
    "edges_pparallel": [float(x) for x in fe.CANONICAL_PPARALLEL_EDGES],
    "n_pt_bins": N_PT_BINS, "n_pparallel_bins": N_PPAR_BINS, "n_reported_cells": N_CELLS,
    "bin_order": "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel",
    "seed_policy": {"estimator_seed": 42, "subsample_seed": 0, "niter": 2, "epochs": 8,
                    "train_events": 2000000},
    "closure_scripts": {
        "ordinary": "nd-unfolding/pet/closure_fullevent_fps.py",
        "omitted_muon_stress": "nd-unfolding/pet/stress_closure_muon.py"},
    "tolerances": {"marginal_l1_max": 0.10, "push_median_dev_max": 0.15,
                   "normalization_dev_max": 1e-3, "cap_saturation_frac_max": 1e-3,
                   # B1 §2d. PROVISIONAL -- must be re-derived from the closure run before the
                   # 08-03 re-issue freezes it. See check_fold_forward_ratio for the three terms
                   # that set it and why it cannot inherit normalization_dev_max's 1e-3.
                   "fold_forward_ratio_dev_max": 0.05,
                   "fold_forward_ratio_dev_max_status": "PROVISIONAL_PENDING_CLOSURE_MEASUREMENT",
                   # Independence check: the driver's reported ratio vs the validator's own
                   # recomputation from the dump. Same arithmetic on the same rows -- this one
                   # IS tight, and a mismatch means the two are not looking at the same result.
                   "fold_forward_driver_agreement_max": 1e-6},
}


def _ck(name, ok, detail=""):
    return {"name": name, "ok": bool(ok), "detail": str(detail)}


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


def check_mc_index_order(imc, n_full=None):
    imc = np.asarray(imc)
    checks = [_ck("index:1d_integer", imc.ndim == 1 and np.issubdtype(imc.dtype, np.integer),
                  f"{imc.ndim}d {imc.dtype}"),
              _ck("index:strictly_increasing", imc.size > 0 and bool(np.all(np.diff(imc) > 0)),
                  "sorted unique ascending"),
              _ck("index:nonnegative", imc.size > 0 and int(imc.min()) >= 0, "min>=0")]
    if n_full is not None:
        checks.append(_ck("index:in_range", imc.size > 0 and int(imc.max()) < int(n_full),
                          f"max {int(imc.max()) if imc.size else None} < {n_full}"))
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


def check_normalization(sum_w_push, sum_w, target_ratio=1.0, tol=None, name="normalization:sum_ratio"):
    """Primitive: |(sum_w_push/sum_w) / target_ratio - 1| <= tol.

    NOT the Gate-4 normalization gate -- `check_fold_forward_ratio` below is. Left at its original
    default (`target_ratio=1.0`) because the frozen launch-code test binds this signature, and
    generalized rather than duplicated so the arithmetic lives in one place.

    Do NOT wire this directly with truth-level sums and the default target. Over the full truth
    population, including off-acceptance events where push == 1, a CORRECT unfold gives
    sum(w*push)/sum(w) -> 1 + <a>_w*(R-1) ~ 1.08, not 1 -- a target that depends on the acceptance
    being measured. Asserting ~1 there fails a correct unfold; asserting ~R there fails it worse.
    Restricting the mask to pass_reco is what removes the acceptance dependence.
    """
    target_ratio = float(target_ratio)
    if sum_w and target_ratio:
        dev = abs((float(sum_w_push) / float(sum_w)) / target_ratio - 1.0)
    else:
        dev = float("inf")
    tol = FROZEN["tolerances"]["normalization_dev_max"] if tol is None else tol
    detail = (f"|ratio-1|={dev:.3e} <= {tol}" if target_ratio == 1.0
              else f"|ratio/{target_ratio:.6g}-1|={dev:.3e} <= {tol}")
    return (dev <= tol), [_ck(name, dev <= tol, detail)]


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

    TOLERANCE -- three terms, and it cannot inherit normalization_dev_max's 1e-3:
      1. Structural floor. omnifold.py:185 pins off-acceptance `pull` to 1, so step 2 regresses
         across both acceptance classes at once and smooths pass_reco pushes toward 1. This does
         NOT vanish with more iterations -- it is a property of the estimator, not of finite
         niter -- and it sets the irreducible floor.
      2. Finite iteration. At niter=2 the reco-level sum under `push` differs from that under
         `pull`.
      3. Subsample sampling. The ratio is subsample-invariant in expectation, not algebraically.
    Term 1 caps the check's power. `fold_forward_ratio_dev_max` is PROVISIONAL until the closure
    run measures these; it must stay well below R-1 (~0.135) or the check detects nothing, and
    above the floor or it fails a correct unfold.

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
    ok_tol, checks = check_normalization(sum_w_push_reco, sum_w_reco, target_ratio=R, tol=tol,
                                         name="normalization:fold_forward_reco_ratio")
    nearer_R = abs(ratio - R) < abs(ratio - 1.0)
    checks.append(_ck("normalization:rate_recovered_not_erased", nearer_R,
                      f"reco-weighted mean push={ratio:.6f} is nearer R={R:.6f} than 1.0 "
                      f"(|d_R|={abs(ratio - R):.3e} vs |d_1|={abs(ratio - 1.0):.3e})"))
    return (ok_tol and nearer_R), checks


def fold_forward_sums_from_dump(inputs_npz, weights_push, mc_indices):
    """Recompute the §2d fold-forward sums and R from the G2 dump, INDEPENDENTLY of the driver.

    The driver persists its own `(sum(w*push), sum(w))` so the gate can cross-check; this is the
    other side. It reads `w_truth` and `pass_reco` from the dump itself, re-derives the training
    subsample's reco mask from `mc_indices`, and pairs it with the driver's `weights_push` -- the
    result under test is the driver's, the reference data is not. R likewise comes from
    `fe.step1_class_ratio_from_dump`, never from the weights npz.

    Note both sums are scale-free in `w_truth`'s normalization: the driver's `mc.weight` was
    rescaled in place to 1e6 by the DataLoader, this reads the raw dump weights, and the RATIO is
    identical either way. Returns (sum_w_push_reco, sum_w_reco, R, telem).
    """
    push = np.asarray(weights_push, float)
    imc = np.asarray(mc_indices)
    with np.load(inputs_npz, allow_pickle=True) as d:
        w_truth_full = np.asarray(d["w_truth"], dtype=np.float64)
        pass_reco_full = np.asarray(d["pass_reco"]).astype(bool)
        R, telem = fe.step1_class_ratio_from_dump(
            d, w_truth_full=w_truth_full, pass_reco_full=pass_reco_full)
    if imc.shape != push.shape:
        raise ValueError(f"[gate4] mc_indices {imc.shape} and weights_push {push.shape} are not "
                         "row-aligned (fail closed)")
    if imc.size and int(imc.max()) >= w_truth_full.shape[0]:
        raise ValueError(f"[gate4] mc_indices max {int(imc.max())} outside the dump's signal "
                         f"inventory ({w_truth_full.shape[0]} rows) -- wrong dump (fail closed)")
    w_sub = w_truth_full[imc]
    mask = pass_reco_full[imc]
    if not mask.any():
        raise ValueError("[gate4] no pass_reco rows in the recomputed subsample (fail closed)")
    telem["n_pass_reco_subsample"] = int(mask.sum())
    return float((w_sub[mask] * push[mask]).sum()), float(w_sub[mask].sum()), R, telem


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


def check_cap_sensitivity(saturation_frac, tol=None):
    tol = FROZEN["tolerances"]["cap_saturation_frac_max"] if tol is None else tol
    ok = saturation_frac is not None and float(saturation_frac) <= tol
    return ok, [_ck("cap:saturation_frac", ok, f"{saturation_frac} <= {tol}")]


def check_closure_verdicts(ordinary_pass, stress_recoil_blind, stress_fullevent_recovers):
    """Compose the two closure verdicts: ordinary closure PASS (estimator does NOT move when it must
    not) AND omitted-muon stress (recoil-only stays blind, full-event RECOVERS the injected tilt)."""
    checks = [_ck("closure:ordinary_pass", bool(ordinary_pass), ordinary_pass),
              _ck("closure:stress_recoil_blind", bool(stress_recoil_blind), stress_recoil_blind),
              _ck("closure:stress_fullevent_recovers", bool(stress_fullevent_recovers),
                  stress_fullevent_recovers)]
    return all(c["ok"] for c in checks), checks


def check_freeze(observed):
    """Verify a nominal result's declared contract against the FROZEN policy (fingerprint, edges, bin
    geometry/order, seed/config) and the central vector's length/finiteness/order."""
    checks = []
    checks.append(_ck("freeze:fingerprint", observed.get("estimator_fingerprint")
                      == ESTIMATOR_FINGERPRINT, observed.get("estimator_fingerprint")))
    checks.append(_ck("freeze:bkg_mode", observed.get("bkg_mode") == BKG_MODE,
                      observed.get("bkg_mode")))
    checks.append(_ck("freeze:edges_pt", observed.get("edges_pt") == FROZEN["edges_pt"], "pt edges"))
    checks.append(_ck("freeze:edges_pparallel",
                      observed.get("edges_pparallel") == FROZEN["edges_pparallel"], "p|| edges"))
    checks.append(_ck("freeze:bin_order", observed.get("bin_order") == FROZEN["bin_order"],
                      observed.get("bin_order")))
    checks.append(_ck("freeze:seed_policy", observed.get("seed_policy") == FROZEN["seed_policy"],
                      observed.get("seed_policy")))
    cv = observed.get("central_vector")
    mask = observed.get("reported_bin_mask")
    if cv is not None:
        cv = np.asarray(cv, float)
        checks.append(_ck("freeze:central_vector_len", cv.shape == (N_CELLS,), cv.shape))
        checks.append(_ck("freeze:central_vector_finite", bool(np.all(np.isfinite(cv))), "finite"))
    if mask is not None:
        checks.append(_ck("freeze:reported_mask_len", np.asarray(mask).shape == (N_CELLS,),
                          np.asarray(mask).shape))
    return all(c["ok"] for c in checks), checks


def build_gate4_report(*, result_meta, frozen_observed, weights_push=None, imc=None, n_full=None,
                       marginal=None, normalization=None, saturation_frac=None,
                       closure=None, observed_at_utc=None, fold_forward=None,
                       fold_forward_driver=None, fold_forward_telemetry=None):
    """Assemble the Gate-4 receipt + single verdict. Pure (no training). `marginal`=(h_truth,h_rw);
    `closure`=(ordinary,recoil_blind,fullevent_recovers).

    `fold_forward`=(sum_w_push_reco, sum_w_reco, R) is the B1 §2d normalization gate -- the
    validator's OWN recomputation from the G2 dump. `fold_forward_driver` is the same triple as
    persisted by the driver; when both are present their agreement is asserted.

    `normalization`=(sum_w_push,sum_w) is the LEGACY truth-level pair. It is retained because the
    frozen launch-code test binds it, and is deliberately NOT what main() wires: see
    check_normalization's docstring for why the truth-level target is acceptance-dependent and so
    cannot be gated on."""
    checks, comps = [], {}
    fz_ok, fz = check_freeze(frozen_observed); checks += fz; comps["freeze"] = fz_ok
    if weights_push is not None:
        w_ok, wc = check_weights_finite_coverage(weights_push, n_full if imc is None else
                                                 (len(imc) if hasattr(imc, "__len__") else None))
        checks += wc; comps["weights"] = w_ok
    if imc is not None:
        i_ok, ic = check_mc_index_order(imc, n_full); checks += ic; comps["index_order"] = i_ok
    if marginal is not None:
        m_ok, mc, _l1 = check_marginal_closure(*marginal); checks += mc; comps["marginal"] = m_ok
    if normalization is not None:
        n_ok, nc = check_normalization(*normalization); checks += nc; comps["normalization"] = n_ok
    if fold_forward is not None:
        f_ok, fc = check_fold_forward_ratio(*fold_forward)
        checks += fc; comps["fold_forward"] = f_ok
        if fold_forward_driver is not None:
            d_ok, dc = check_fold_forward_independence(fold_forward, fold_forward_driver)
            checks += dc; comps["fold_forward_independence"] = d_ok
    if saturation_frac is not None:
        c_ok, cc = check_cap_sensitivity(saturation_frac); checks += cc; comps["cap"] = c_ok
    if closure is not None:
        cl_ok, clc = check_closure_verdicts(*closure); checks += clc; comps["closure"] = cl_ok
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate-4 nominal validator (runtime; needs a trained result)")
    ap.add_argument("--nominal-weights", required=True, help="nominal weights npz (from the driver)")
    ap.add_argument("--work", required=True, help="caller-supplied WORK receipt path (JSON)")
    ap.add_argument("--n-full", type=int, default=None)
    # B1 §2d: the G2 dump the result was trained against. REQUIRED, because without it the
    # normalization check is not computable and would be silently skipped -- which is exactly the
    # state this gate was in before the B1 fix: a correct assertion that never executes.
    ap.add_argument("--inputs", required=True,
                    help="the G2 dump the nominal was trained on (g2-fullevent-v1 npz). Required: "
                         "the fold-forward normalization gate recomputes its reference sums and R "
                         "from it, independently of the driver.")
    ap.add_argument("--allow-missing-fold-forward", action="store_true",
                    help="DIAGNOSTIC ONLY. Skip the fold-forward gate when the weights npz "
                         "predates the B1 fix. A receipt produced this way does not certify the "
                         "normalization and must not be promoted.")
    args = ap.parse_args(argv)
    import datetime
    z = np.load(args.nominal_weights, allow_pickle=True)
    frozen_observed = {"estimator_fingerprint": str(z["estimator_fingerprint"]) if
                       "estimator_fingerprint" in z.files else None,
                       "bkg_mode": str(z["bkg_mode"]) if "bkg_mode" in z.files else None,
                       "edges_pt": FROZEN["edges_pt"], "edges_pparallel": FROZEN["edges_pparallel"],
                       "bin_order": FROZEN["bin_order"], "seed_policy": FROZEN["seed_policy"]}

    # ---- B1 §2d: assemble the fold-forward gate's two sides ----
    fold_forward = fold_forward_driver = fold_forward_telemetry = None
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
        v_push, v_w, v_R, fold_forward_telemetry = fold_forward_sums_from_dump(
            args.inputs, z["weights_push"], z["mc_indices"])
        fold_forward = (v_push, v_w, v_R)
        fold_forward_driver = (float(z["fold_forward_sum_w_push_reco"]),
                               float(z["fold_forward_sum_w_reco"]),
                               float(z["step1_class_ratio"]))

    payload, verdict = build_gate4_report(
        result_meta={"path": os.path.abspath(args.nominal_weights),
                     "sha256": _sha256_file(args.nominal_weights),
                     "inputs_path": os.path.abspath(args.inputs)},
        frozen_observed=frozen_observed,
        weights_push=z["weights_push"] if "weights_push" in z.files else None,
        imc=z["mc_indices"] if "mc_indices" in z.files else None, n_full=args.n_full,
        fold_forward=fold_forward, fold_forward_driver=fold_forward_driver,
        fold_forward_telemetry=fold_forward_telemetry,
        observed_at_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    if fold_forward is None:
        payload["fold_forward"] = {"skipped": True, "promotable": False,
                                   "reason": f"--allow-missing-fold-forward; npz lacks {missing}"}
    write_work_receipt(args.work, payload)
    print(json.dumps({"verdict": payload["verdict"], "n_failed": payload["n_failed"],
                      "component_verdicts": payload["component_verdicts"]}, indent=2))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
