#!/usr/bin/env python3
"""Read the D2 under-fitting probe: does more TRAINING BUDGET close the gap to the achievable ceiling?

WHY THIS EXISTS, AND WHY THE VERDICT RULE IS IN THE FILE RATHER THAN IN MY HEAD. The powered closure
FAILED at the nominal configuration (job 56381674, recovery 0.546853 against a predeclared 0.80).
That FAIL is not the interesting number. The 0.80 bar sits ~17 pp above what the estimator can reach
at ANY iteration count -- the tilt-weighted per-cell ceiling is 0.6332 at k=3
(`FINDING-20260806-niter4-decision.md` 2/2a) -- so no reading of a probe can or should rescue the
gate. The live question is the **19% shortfall between the measured 0.546853 and that 0.6332**, and
whether spending more training budget closes it. If it does not, the estimator is at its structural
limit and the criterion, not the estimator, is what needs redesigning.

That makes the reading of this probe exactly the kind of thing this campaign has got wrong before: a
result arrives, and the threshold for "substantial" gets chosen once the number is visible. BEN-025 is
the standing example (a spread estimate that was never significant inverted a correct decision). So
`PREDECLARED` below is committed BEFORE any arm reports, the rule is evaluated by code rather than by
narration, and the commit that adds this file lands before the arms do. Its git history is the proof.

NOTHING HERE MAY MOVE A THRESHOLD. `recovery_min = 0.80` is untouched and unreferenced as a target:
this script never reports pass/fail against it, because every arm is expected to miss it and saying so
three more times would be noise dressed as evidence.

WHAT IT RECOMPUTES RATHER THAN BELIEVES. Every metric is rebuilt from the report's `h_prior`,
`h_target`, `h_unfolded`, `h_untilted` vectors, and the report's own `metrics` block is then compared
against the recomputation and flagged on disagreement. Checking a report's summary against itself is
the self-agreeing shape `validate_pet_nominal_gate4.check_powered_closure` was rewritten to avoid, and
this file is downstream of the same lesson.

THE CEILING IS A REFERENCE CURVE, NOT A BOUND -- AND THIS SCRIPT SHOWS WHY. Under independent per-cell
dilution, `residual(k) = sum_b (1-a_b)^k |p_b - t_b|`. `omnifold.py:218-220` evaluates the truth
classifier on ALL `pass_gen` rows, so a smooth learner can transport the injected tilt into cells that
have almost no acceptance of their own, and the per-cell table below shows it DOING so: the near-zero
acceptance cells at `i_pparallel = 0` recover far more than their local `1-(1-a_b)^k` allows. The
aggregate is therefore not a theorem-grade bound either, which is why the finding grades it ASSUMED.
It is still the right yardstick for "how much is left on the table", because the aggregate measurement
sits below it -- but a reader must not quote it as a proof of impossibility.
"""
import argparse
import json
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
_REPO = os.environ.get("MNV_REPO") or os.path.dirname(_ND)
# Off `_REPO` rather than `_ND` so an `MNV_REPO` export wins over where this file happens to sit.
DEFAULT_ACCEPTANCE = os.path.join(_REPO, "nd-unfolding", "products", "pet", "fullevent_fps",
                                  "acceptance_map_fullevent_fps.json")

# ---------------------------------------------------------------------------------------------
# PREDECLARED 2026-08-07, BEFORE ANY ARM REPORTED. Do not tune these to a result.
#
# `gap_to_ceiling` = ceiling(k=3) - recovery(baseline) = 0.633208 - 0.546853 = 0.086354, the whole
# quantity in dispute. The arms are read as a FRACTION of it, because "recovery moved 0.01" means
# nothing without saying 0.01 out of what.
#
#   CONFIRMED  best arm closes >= 50% of gap_to_ceiling AND the move is >= 3x the control's own
#              displacement from the published baseline. Diagnosis: under-fitting; the fix is a
#              training-budget change, and the criterion redesign should be re-argued afterwards.
#   REFUTED    best arm closes <= 10% of gap_to_ceiling, or the move does not exceed the run-to-run
#              scale. Diagnosis: the estimator is at its structural limit at this architecture and
#              learning rate; more budget is not the missing ingredient.
#   AMBIGUOUS  anything else. Reported as ambiguous and NOT spun either way.
#
# The run-to-run scale comes from the control arm, which re-runs the baseline configuration exactly.
# It is ONE pair, so it is an order-of-magnitude scale and NOT a confidence interval; the 3x factor
# is deliberately crude for that reason, and the script says so in its own output rather than letting
# a reader mistake `delta_runtorun` for a sigma. Two points cannot produce a sigma (BEN-025).
PREDECLARED = {
    "declared_utc": "2026-08-07",
    "baseline_job": 56381674,
    "baseline_recovery": 0.546853,
    "ceiling_k3_tilt_weighted": 0.633208,
    "gap_to_ceiling": 0.086354,
    "confirmed_fraction_min": 0.50,
    "refuted_fraction_max": 0.10,
    "runtorun_multiple_required": 3.0,
    "threshold_note": "recovery_min=0.80 is NOT a target here and is not evaluated; every arm is "
                      "expected to miss it and the bar is ~17 pp above achievable.",
    # PRIMARY TARGET, REVISED 2026-08-07 BEFORE ANY ARM REPORTED (all three still PENDING at the
    # time of writing; `git log` on this file against the arms' Submit timestamps is the check).
    #
    # The revision is not a loosening, it is a correction of WHAT IS MEASURED, and it happened
    # because the first draft of this rule would have measured the wrong quantity. Decomposing the
    # baseline into a signed response and a scatter term:
    #
    #   per-bin signed recovery r_b = (u_b - p_b)/(t_b - p_b),  weights w_b = |t_b - p_b|
    #   aggregate L1 recovery      = 1 - E_w[|1 - r_b|]        = 0.54685
    #   signed mean response       = E_w[r_b]                  = 0.63129
    #   ideal (dilution model)     = E_w[1-(1-a_b)^k]          = 0.63321
    #   SCATTER PENALTY = E_w[|1-r_b|] - |1 - E_w[r_b]|        = 0.08443
    #
    # The estimator's MEAN per-bin response already matches the ideal to 0.19 pp. The entire
    # 0.086354 `gap_to_ceiling` is the scatter term (0.08443 of 0.08636 = 97.8%): the L1's absolute
    # value converts symmetric per-bin noise into a one-sided penalty, and 87 of 262 occupied bins
    # OVERSHOOT (r>1), carrying 24.1% of the displacement. `docs/OPEN_ITEMS.md` (a) reached this
    # first and independently -- E_w[r] 0.63129 reproduces its number exactly -- and its conclusion
    # is recorded there: the residual is a VARIANCE question needing a seed ensemble, not a longer
    # run.
    #
    # Therefore an arm can only close the gap by REDUCING PER-BIN SCATTER. A rule phrased on the
    # aggregate alone would have been satisfied by a bias shift that this estimator does not have
    # room to make, and would have mis-attributed any move. Both are reported; the scatter term is
    # the one that carries the diagnosis.
    "primary_target": {
        "quantity": "scatter_penalty = E_w[|1-r|] - |1-E_w[r]|",
        "baseline_scatter_penalty": 0.08443,
        "baseline_signed_mean_response": 0.63129,
        "baseline_ideal_signed_mean": 0.63321,
        "share_of_gap_that_is_scatter": 0.978,
        "reading": "under-fitting is CONFIRMED only if the scatter penalty falls by the same "
                   "fraction the aggregate rises; an aggregate move with a flat scatter penalty "
                   "is a bias shift and must be reported as such, not as confirmation",
    },
    # SECONDARY: the low-acceptance transport effect, which is the one place a real per-bin BIAS is
    # visible and which shows the ceiling is not a bound. Cells with a_b < 0.01 carry 23.2% of the
    # displacement and reach a signed response of +0.1525 against an independence ideal of 0.0082.
    # `OPEN_ITEMS.md` (a) records the same census (it counts 35 bins at the <1% threshold to this
    # file's 34; an occupancy cut, not a disagreement).
    "secondary_transport_check": {
        "band": "a_b < 0.01",
        "baseline_signed_response": 0.1525,
        "baseline_ideal": 0.0082,
        "reading": "this band beating its own ceiling is the smooth-transport effect and must NOT "
                   "be read as the estimator doing well; it is why 0.6332 is a reference curve "
                   "rather than a bound",
    },
}

# Acceptance bands for the decomposition. Boundaries chosen from the baseline census BEFORE any arm
# reported, and left fixed thereafter: re-binning after seeing an arm is how a null becomes a signal.
ACCEPTANCE_BANDS = ((0.0, 0.01), (0.01, 0.10), (0.10, 0.30), (0.30, 0.50), (0.50, 0.70), (0.70, 1.01))


def l1(a, b):
    return float(np.abs(np.asarray(a, float) - np.asarray(b, float)).sum())


def load_spectra(path):
    """Pull the four spectra out of a report and rebuild every metric from them."""
    rep = json.load(open(path))
    v = {k: np.asarray(rep[k], dtype=float) for k in
         ("h_prior", "h_target", "h_unfolded", "h_untilted")}
    gap = l1(v["h_prior"], v["h_target"])
    floor = l1(v["h_prior"], v["h_untilted"])
    residual = l1(v["h_unfolded"], v["h_target"])
    recomputed = {"gap": gap, "floor": floor, "residual": residual,
                  "floor_over_gap": floor / gap, "residual_over_gap": residual / gap,
                  "recovery": 1.0 - residual / gap}
    stated = rep.get("metrics") or {}
    disagreements = {k: {"stated": stated.get(k), "recomputed": recomputed[k]}
                     for k in recomputed
                     if stated.get(k) is None
                     or abs(float(stated[k]) - recomputed[k]) > 1e-9}
    cfg = rep.get("configuration") or {}
    return {
        "path": os.path.abspath(path),
        "verdict_in_report": rep.get("verdict"),
        "configuration": cfg,
        "configuration_overrides": rep.get("configuration_overrides") or {},
        "is_nominal_configuration": rep.get("is_nominal_configuration"),
        "early_stop_patience": rep.get("early_stop_patience"),
        "metrics_recomputed": recomputed,
        "metrics_disagree_with_report": disagreements,
        "_v": v,
    }


def ceiling_curve(prior, target, acceptance, kmax=8):
    """`residual(k) = sum_b (1-a_b)^k |p_b - t_b|` -- weighted by the INJECTED DISPLACEMENT.

    Not by truth mass, and not evaluated at the global acceptance: `1-(1-a)^k` is convex in `a`, so
    the global form overstates the achievable per-cell recovery by Jensen. That error shipped once
    already (`acceptance_map_fullevent_fps.py:155`, +19.9 pp at k=3) and read as "the bar is
    achievable and the estimator is broken", the exact inverse of the truth.
    """
    disp = np.abs(prior - target)
    gap = float(disp.sum())
    return {str(k): {"ideal_residual": float((((1 - acceptance) ** k) * disp).sum()),
                     "ideal_recovery": float(1.0 - (((1 - acceptance) ** k) * disp).sum() / gap)}
            for k in range(1, kmax + 1)}


def direction_split(v, acceptance, k):
    """Recovery by tilt direction, each direction measured against ITS OWN ceiling.

    The raw split is confounded: up-tilted cells sit at mean acceptance ~0.43 and down-tilted at
    ~0.69, so a plain "up recovers worse than down" reading is partly just acceptance. Subtracting
    each direction's own ceiling is what isolates estimator quality from geometry.
    """
    p, t, u = v["h_prior"], v["h_target"], v["h_unfolded"]
    disp = np.abs(p - t)
    out = {}
    for name, mask in (("up_tilted", t > p), ("down_tilted", t < p)):
        g = float(disp[mask].sum())
        if g <= 0:
            continue
        r = float(np.abs(u - t)[mask].sum())
        c = float((((1 - acceptance) ** k) * disp)[mask].sum())
        out[name] = {"n_cells": int(mask.sum()), "gap": g, "gap_share": g / float(disp.sum()),
                     "residual": r, "recovery": 1.0 - r / g,
                     "ceiling_recovery": 1.0 - c / g,
                     "shortfall_vs_own_ceiling": (1.0 - c / g) - (1.0 - r / g),
                     "residual_over_ideal": (r / c) if c > 0 else None,
                     "mean_acceptance": float(acceptance[mask].mean())}
    return out


def signed_decomposition(v, acceptance, k):
    """Split the L1 shortfall into a BIAS term and a SCATTER term. The decisive statistic.

    The closure's metric is an L1, so it takes an absolute value per cell, and an absolute value
    turns symmetric per-cell noise into a one-sided penalty. Two estimators with the same mean
    response and different per-cell variance therefore score differently, and the aggregate alone
    cannot say which one you have.

        r_b = (u_b - p_b) / (t_b - p_b)     signed fraction of cell b's displacement recovered
        w_b = |t_b - p_b|                   the closure's own weighting
        aggregate recovery = 1 - E_w[|1 - r_b|]
        signed response    = E_w[r_b]
        scatter penalty    = E_w[|1 - r_b|] - |1 - E_w[r_b]|

    On the baseline the signed response matches the dilution ideal to 0.19 pp while the scatter
    penalty accounts for 97.8% of the distance to that ideal -- i.e. the estimator is not biased,
    it is noisy per cell. `docs/OPEN_ITEMS.md` (a) established this first; this function exists so
    every arm is read on the same axis rather than on the aggregate that hides it.
    """
    p, t, u = v["h_prior"], v["h_target"], v["h_unfolded"]
    d, m = t - p, u - p
    occ = np.abs(d) > 0
    w = np.abs(d)[occ]
    r = m[occ] / d[occ]
    r_ideal = 1.0 - (1.0 - acceptance[occ]) ** k
    ew = lambda x: float((w * x).sum() / w.sum())  # noqa: E731
    agg = 1.0 - ew(np.abs(1.0 - r))
    signed = ew(r)
    return {
        "aggregate_l1_recovery": agg,
        "signed_mean_response": signed,
        "ideal_signed_mean_response": ew(r_ideal),
        "bias_vs_ideal": signed - ew(r_ideal),
        "scatter_penalty": ew(np.abs(1.0 - r)) - abs(1.0 - signed),
        "weighted_rms_r_minus_ideal": float(np.sqrt(ew((r - r_ideal) ** 2))),
        "n_overshoot_bins": int((r > 1).sum()),
        "n_occupied_bins": int(occ.sum()),
        "overshoot_displacement_share": float(w[r > 1].sum() / w.sum()),
    }


def acceptance_band_split(v, acceptance, k):
    """Recovery vs its own ceiling, decomposed by per-cell acceptance. THE sharp diagnostic.

    The aggregate recovery mixes two opposite effects and hides both. In the `a_b < 0.01` cells the
    independence ceiling is ~0.008 and the estimator delivers ~0.15, because the truth classifier
    sees every `pass_gen` row and transports the smooth pT tilt into cells that have essentially no
    acceptance of their own. In the `a_b >= 0.5` cells the ceiling is ~0.94-0.99 and the estimator
    delivers ~0.71-0.85. Averaging those together produces one number that describes neither.
    """
    p, t, u, z = v["h_prior"], v["h_target"], v["h_unfolded"], v["h_untilted"]
    disp = np.abs(p - t)
    gap = float(disp.sum())
    occupied = disp > 0
    out = {}
    for lo, hi in ACCEPTANCE_BANDS:
        m = occupied & (acceptance >= lo) & (acceptance < hi)
        if not m.any():
            continue
        g = float(disp[m].sum())
        r = float(np.abs(u - t)[m].sum())
        c = float((((1 - acceptance) ** k) * disp)[m].sum())
        out[f"[{lo:.2f},{hi:.2f})"] = {
            "n_cells": int(m.sum()), "displacement_share": g / gap,
            "residual": r, "ideal_residual": c,
            "excess_over_ideal": r - c,
            "recovery": 1.0 - r / g, "ceiling_recovery": 1.0 - c / g,
            "shortfall_vs_ceiling": (1.0 - c / g) - (1.0 - r / g),
            "beats_own_ceiling": bool(r < c),
            "sampling_floor_in_band": float(np.abs(p - z)[m].sum()),
        }
    # The one band the secondary prediction is about, pooled.
    m = occupied & (acceptance >= 0.50)
    if m.any():
        g = float(disp[m].sum())
        r = float(np.abs(u - t)[m].sum())
        c = float((((1 - acceptance) ** k) * disp)[m].sum())
        out["POOLED_a_ge_0.50"] = {
            "n_cells": int(m.sum()), "displacement_share": g / gap,
            "residual": r, "ideal_residual": c, "excess_over_ideal": r - c,
            "recovery": 1.0 - r / g, "ceiling_recovery": 1.0 - c / g,
            "shortfall_vs_ceiling": (1.0 - c / g) - (1.0 - r / g),
            "sampling_floor_in_band": float(np.abs(p - z)[m].sum()),
        }
    return out


def per_cell_table(v, acceptance, k, top_n):
    """The top-`top_n` cells by injected displacement, with each cell's own ceiling and noise floor.

    `floor_b = |p_b - z_b|` is the per-cell sampling floor from the untilted half, and it is here so
    that a small per-cell recovery is not read as a defect when it is smaller than that cell's noise.
    """
    p, t, u, z = v["h_prior"], v["h_target"], v["h_unfolded"], v["h_untilted"]
    disp = np.abs(p - t)
    with np.errstate(divide="ignore", invalid="ignore"):
        rec = 1.0 - np.abs(u - t) / np.where(disp > 0, disp, np.nan)
    rows = []
    for i in np.argsort(-disp)[:top_n]:
        i = int(i)
        rows.append({"cell": i, "direction": "up" if t[i] > p[i] else "down",
                     "displacement": float(disp[i]), "acceptance": float(acceptance[i]),
                     "floor_cell": float(abs(p[i] - z[i])),
                     "recovery_cell": (float(rec[i]) if np.isfinite(rec[i]) else None),
                     "ceiling_cell": float(1.0 - (1.0 - acceptance[i]) ** k),
                     "beats_own_ceiling": bool(np.isfinite(rec[i])
                                               and rec[i] > 1.0 - (1.0 - acceptance[i]) ** k)})
    return rows


def verdict(arms, baseline_recovery, control_label):
    """Apply PREDECLARED. Returns the decision dict; the caller does not get to argue with it."""
    P = PREDECLARED
    probes = {k: a for k, a in arms.items() if k != control_label}
    if not probes:
        return {"decision": "NO_PROBE_ARMS", "note": "nothing but the control reported"}
    best_label = max(probes, key=lambda k: probes[k]["metrics_recomputed"]["recovery"])
    best = probes[best_label]["metrics_recomputed"]["recovery"]
    move = best - baseline_recovery
    frac = move / P["gap_to_ceiling"]
    ctl = arms.get(control_label)
    delta = (abs(ctl["metrics_recomputed"]["recovery"] - baseline_recovery)
             if ctl is not None else None)
    beats_noise = (delta is not None and delta > 0
                   and move >= P["runtorun_multiple_required"] * delta)
    # The scatter term is the quantity that must move (PREDECLARED["primary_target"]). An aggregate
    # rise with a flat scatter penalty is a bias shift wearing the aggregate's clothes, and gets
    # labelled as such rather than being allowed to read as confirmation.
    base_scatter = P["primary_target"]["baseline_scatter_penalty"]
    arm_scatter = (probes[best_label].get("signed") or {}).get("scatter_penalty")
    scatter_drop = (base_scatter - arm_scatter) if arm_scatter is not None else None
    scatter_moved = (scatter_drop is not None
                     and scatter_drop >= P["confirmed_fraction_min"] * base_scatter)
    if frac >= P["confirmed_fraction_min"] and beats_noise and scatter_moved:
        decision = "UNDERFITTING_CONFIRMED"
    elif frac >= P["confirmed_fraction_min"] and beats_noise and not scatter_moved:
        decision = "AGGREGATE_MOVED_BUT_NOT_VIA_SCATTER"
    elif frac <= P["refuted_fraction_max"] or (delta is not None and move <= delta):
        decision = "UNDERFITTING_REFUTED"
    else:
        decision = "AMBIGUOUS"
    return {
        "decision": decision,
        "baseline_scatter_penalty": base_scatter,
        "best_arm_scatter_penalty": arm_scatter,
        "scatter_penalty_drop": scatter_drop,
        "scatter_moved": scatter_moved,
        "best_probe_arm": best_label,
        "best_probe_recovery": best,
        "baseline_recovery": baseline_recovery,
        "move": move,
        "fraction_of_gap_to_ceiling_closed": frac,
        "control_displacement_from_baseline": delta,
        "control_displacement_is_a_scale_not_a_sigma": True,
        "move_exceeds_runtorun_multiple": beats_noise,
        "rule": P,
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--baseline", required=True,
                   help="the nominal-configuration report (job 56381674)")
    p.add_argument("--arm", action="append", default=[], metavar="LABEL=PATH",
                   help="a probe arm report; repeatable")
    p.add_argument("--control-label", default="ctl8",
                   help="which --arm label is the baseline-configuration re-run")
    p.add_argument("--acceptance-map", default=DEFAULT_ACCEPTANCE)
    p.add_argument("--k", type=int, default=3, help="iteration count the ceiling is evaluated at")
    p.add_argument("--top-cells", type=int, default=20)
    p.add_argument("--out", required=True, help="write the machine-readable comparison here")
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    acc_doc = json.load(open(a.acceptance_map))
    acceptance = np.asarray(acc_doc["acceptance_cells_pt_major"], dtype=float)

    base = load_spectra(a.baseline)
    if acc_doc.get("bin_order") != json.load(open(a.baseline)).get("bin_order"):
        raise SystemExit("[probe-analyze] acceptance map and report disagree on bin_order; the "
                         "per-cell join would be silently wrong (fail closed)")
    if acceptance.size != base["_v"]["h_prior"].size:
        raise SystemExit(f"[probe-analyze] acceptance map has {acceptance.size} cells, report has "
                         f"{base['_v']['h_prior'].size} (fail closed)")

    arms = {}
    for spec in a.arm:
        if "=" not in spec:
            raise SystemExit(f"[probe-analyze] --arm wants LABEL=PATH, got {spec!r}")
        label, path = spec.split("=", 1)
        if not os.path.exists(path):
            print(f"[probe-analyze] arm {label}: {path} not present yet -- skipping")
            continue
        arms[label] = load_spectra(path)

    # The premise of comparing recoveries at all is that every arm graded the SAME injected problem.
    # gap and floor are budget-independent, so any arm whose gap moves was not measuring this test.
    base_gap = base["metrics_recomputed"]["gap"]
    same_problem = {}
    for label, arm in arms.items():
        rel = abs(arm["metrics_recomputed"]["gap"] - base_gap) / base_gap
        same_problem[label] = {"gap_rel_diff_vs_baseline": rel, "ok": rel <= 1e-6}

    result = {
        "product_schema": "d2-underfitting-probe-comparison-v1",
        "what_this_is": "does more training budget close the gap between the measured powered-"
                        "closure recovery and the achievable tilt-weighted ceiling at k=3",
        "predeclared": PREDECLARED,
        "acceptance_map": {"path": os.path.abspath(a.acceptance_map),
                           "inputs_sha256": acc_doc.get("inputs_sha256"),
                           "git_head": acc_doc.get("git_head")},
        "k": a.k,
        "ceiling_curve_tilt_weighted": ceiling_curve(base["_v"]["h_prior"],
                                                     base["_v"]["h_target"], acceptance),
        "arms_grade_the_same_injected_problem": same_problem,
        "baseline": {k: v for k, v in base.items() if k != "_v"},
        "baseline_signed_decomposition": signed_decomposition(base["_v"], acceptance, a.k),
        "baseline_direction_split": direction_split(base["_v"], acceptance, a.k),
        "baseline_acceptance_bands": acceptance_band_split(base["_v"], acceptance, a.k),
        "baseline_top_cells": per_cell_table(base["_v"], acceptance, a.k, a.top_cells),
        "arms": {},
    }
    base_bands = result["baseline_acceptance_bands"]
    for label, arm in arms.items():
        entry = {k: v for k, v in arm.items() if k != "_v"}
        entry["signed"] = signed_decomposition(arm["_v"], acceptance, a.k)
        arm["signed"] = entry["signed"]          # verdict() reads it off the arm
        entry["direction_split"] = direction_split(arm["_v"], acceptance, a.k)
        entry["acceptance_bands"] = acceptance_band_split(arm["_v"], acceptance, a.k)
        entry["top_cells"] = per_cell_table(arm["_v"], acceptance, a.k, a.top_cells)
        entry["delta_recovery_vs_baseline"] = (arm["metrics_recomputed"]["recovery"]
                                               - base["metrics_recomputed"]["recovery"])
        # The secondary prediction, evaluated: did the band where the information IS present move?
        bk = "POOLED_a_ge_0.50"
        if bk in entry["acceptance_bands"] and bk in base_bands:
            ab, bb = entry["acceptance_bands"][bk], base_bands[bk]
            entry["secondary_band_check"] = {
                "band": "a_b >= 0.50",
                "baseline_recovery": bb["recovery"],
                "arm_recovery": ab["recovery"],
                "delta": ab["recovery"] - bb["recovery"],
                "baseline_shortfall_vs_ceiling": bb["shortfall_vs_ceiling"],
                "fraction_of_band_shortfall_closed":
                    ((ab["recovery"] - bb["recovery"]) / bb["shortfall_vs_ceiling"]
                     if bb["shortfall_vs_ceiling"] > 0 else None),
            }
        result["arms"][label] = entry

    result["verdict"] = verdict(
        {**{k: v for k, v in arms.items()}}, base["metrics_recomputed"]["recovery"],
        a.control_label) if arms else {"decision": "NO_ARMS_YET"}

    with open(a.out, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")

    ceil3 = result["ceiling_curve_tilt_weighted"][str(a.k)]["ideal_recovery"]
    print(f"[probe-analyze] baseline recovery={base['metrics_recomputed']['recovery']:.6f} "
          f"ceiling(k={a.k})={ceil3:.6f} gap_to_ceiling={ceil3 - base['metrics_recomputed']['recovery']:.6f}")
    for label, entry in result["arms"].items():
        cfg = entry["configuration"]
        print(f"[probe-analyze] arm {label:8s} epochs={cfg.get('epochs')} niter={cfg.get('niter')} "
              f"early_stop={entry.get('early_stop_patience')} "
              f"recovery={entry['metrics_recomputed']['recovery']:.6f} "
              f"delta={entry['delta_recovery_vs_baseline']:+.6f} "
              f"same_problem={same_problem[label]['ok']}")
        sg = entry["signed"]
        print(f"[probe-analyze]   signed response={sg['signed_mean_response']:.5f} "
              f"(ideal {sg['ideal_signed_mean_response']:.5f}, bias {sg['bias_vs_ideal']:+.5f}) "
              f"scatter_penalty={sg['scatter_penalty']:.5f} "
              f"overshoot={sg['n_overshoot_bins']}/{sg['n_occupied_bins']}")
        sb = entry.get("secondary_band_check")
        if sb:
            print(f"[probe-analyze]   band a_b>=0.50: {sb['baseline_recovery']:.4f} -> "
                  f"{sb['arm_recovery']:.4f} (delta {sb['delta']:+.4f}, "
                  f"{sb['fraction_of_band_shortfall_closed']:+.3f} of that band's shortfall)")
        if entry["metrics_disagree_with_report"]:
            print(f"[probe-analyze]   WARNING arm {label} report metrics disagree with the "
                  f"recomputation: {entry['metrics_disagree_with_report']}")
    print(f"[probe-analyze] VERDICT {result['verdict'].get('decision')} -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
