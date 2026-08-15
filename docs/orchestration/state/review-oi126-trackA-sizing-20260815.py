"""Second read of the Track A sizing arithmetic, SCOPED to whether this lane's measurements are used
correctly. Not a review of the design: this lane designed the retired tiebreak and has a stake.

Read-only, local, derived from the committed sigma probe. Emits the review receipt.
"""
import json, math, hashlib
import numpy as np
from scipy import stats

SIG = "docs/orchestration/state/probe-oi126-band-Rpush-sigma-20260815.json"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
d = json.load(open(SIG))
s = d["summary"]
SD, MEAN = s["sd_ddof1"], s["mean"]
mid = (MEAN + 1.0) / 2.0
dist = MEAN - mid
dcoh = dist / SD
power = lambda n, dd=None: float(1 - stats.nct.cdf(stats.t.ppf(0.975, n - 1), n - 1, (dd or dcoh) * math.sqrt(n))
                                 + stats.nct.cdf(-stats.t.ppf(0.975, n - 1), n - 1, (dd or dcoh) * math.sqrt(n)))
hw = lambda n, sdv=None: float(stats.t.ppf(0.975, n - 1) * (sdv or SD) / math.sqrt(n))
n_for_power = lambda tgt: next(n for n in range(3, 400) if power(n) >= tgt)

med = np.array(d["per_replica_band_R_push_MEDIAN_over_cells"])
alt = d["alternative_statistics_not_substituted"]
variants = {"median_over_cells_PINNED": med,
            "mean_over_cells": np.array([a["mean_over_cells"] for a in alt]),
            "ratio_of_sums": np.array([a["ratio_of_sums"] for a in alt])}
st = d["is_the_spread_pparallel_structured"]
sdcol = np.array(st["sd_by_column"]); relcol = np.array(st["rel_sd_by_column"])

out = {
 "what": "scoped second read of the Track A sizing: are lane B's measurements used correctly?",
 "SCOPE_AND_ITS_REASON": ("checks the arithmetic and the use of this lane's numbers ONLY. The DESIGN is out "
   "of scope by the mediator's instruction and this lane agrees: this lane designed the tiebreak that was "
   "refused, so it has a stake in the instrument that replaced it. Nothing here comments on whether "
   "Exponential(1) is the right null."),
 "WHAT_THIS_DOES_NOT_CERTIFY": ("THE PREDECLARATION IS NOT COMMITTED. Searched origin/main for "
   "'Exponential', 'variance-matched', 'zero-free' and for the quoted figures; every hit is this lane's own "
   "work. So this is a review of the ARITHMETIC AS RELAYED, not of the document. Claims about how the "
   "document pins or carries anything CANNOT be verified from here and are marked UNVERIFIABLE."),
 "ingredients": {"sigma_probe": {"path": SIG, "sha256": sha(SIG)}},
 "lane_B_numbers_as_measured": {
   "sd_ddof1": SD, "mean": MEAN, "n_replicas": s["n_replicas"],
   "statistic": ("spread and mean ACROSS 50 REPLICAS of the PER-REPLICA MEDIAN over the 84 geometric band "
     "cells of T_nom/T_k, where T_a(cell) = sum over pass_truth rows in cell of w_truth*w_push_a; band = "
     "p_parallel columns 10-15 intersected with the 257-cell quotable sub-block; 0 cells dropped"),
   "it_is_the_POISSON_arm": True},

 "CHECK_1_statistic_pinning": {
   "verdict": "PASS on the definition; and the STATED REASON for pinning is wrong in a way worth fixing",
   "pinning_itself_is_UNVERIFIABLE_here": "the document is not committed",
   "the_warning_as_relayed": "substituting a mean-over-cells statistic would silently invalidate the sizing",
   "measured": {k: {"mean": float(v.mean()), "sd_ddof1": float(v.std(ddof=1)),
                    "cohen_d": float((v.mean() - 1.0) / 2 / v.std(ddof=1)),
                    "midpoint_boundary": float((v.mean() + 1.0) / 2),
                    "n_by_the_t_rule": next(n for n in range(3, 200)
                                            if hw(n, v.std(ddof=1)) < (v.mean() - (v.mean() + 1.0) / 2))}
               for k, v in variants.items()},
   "correction": ("n is NEARLY INVARIANT across the three statistics (9, 9, 7) because the spread scales "
     "with the mean, so d stays ~0.81-0.95. THE SIZING IS NOT WHAT BREAKS. What breaks is the BOUNDARY: "
     "the midpoint is 2.2985 under the pinned statistic, 2.4242 under mean-over-cells and 1.8008 under "
     "ratio-of-sums. A boundary quoted from one statistic and applied to a result computed with another is "
     "a real error EVEN WHEN n SURVIVES -- and it is the more dangerous failure because the sizing check "
     "would pass and hide it. Pin the statistic for the BOUNDARY's sake, and say so.")},

 "CHECK_2_boundary": {
   "verdict": "PASS; caveat correctly identified as a caveat, with one addition",
   "midpoint_reproduced": mid, "quoted_as": 2.2985, "agrees": bool(abs(mid - 2.2985) < 5e-5),
   "one_side_measured": MEAN, "other_side_ASSUMED": 1.0,
   "distance": dist, "quoted_distance": 1.2984,
   "note_on_the_quoted_distance": ("1.2984 is a TRUNCATION of 1.298453...; the round is 1.2985. Immaterial, "
     "and in the conservative direction -- it makes the n=9 test marginally harder, not easier."),
   "ADDITION": ("the boundary's LOCATION depends on the unmeasured (b) value. If (b) collapses to 1.3 "
     "rather than 1.0 the midpoint moves to %.4f and the distance falls to %.4f, which alone would cost "
     "power. The 1.0 is a hypothesis, not a measurement, and the boundary inherits that."
     % ((MEAN + 1.3) / 2, MEAN - (MEAN + 1.3) / 2))},

 "CHECK_3_t_versus_z_AND_THE_ONE_SUBSTANTIVE_FINDING": {
   "t_choice_verdict": ("CORRECT, and it corrects THIS LANE's optimism. Lane B's n>=6 used z=1.96 with sd "
     "treated as KNOWN. Under Student's t with each arm's spread estimated from its own draws, n=6 fails: "
     "halfwidth %.4f > %.4f. The 6 -> 9 move is right." % (hw(6), dist)),
   "quoted_figures_reproduce": {"halfwidth_n9": hw(9), "quoted": 1.2369,
     "n8_halfwidth": hw(8), "n8_shortfall": hw(8) - dist, "quoted_shortfall": 0.047},
   "THE_FINDING": ("THE SIZING RULE IS NOT A POWER CALCULATION. 't*sd/sqrt(n) < distance' substitutes the "
     "TRUE sd for the realized sample sd and the TRUE mean for the realized sample mean, which is "
     "approximately the condition for FIFTY PERCENT power. Measured, with (a) exactly true and sd exactly "
     "as this lane measured it:"),
   "power_if_a_is_exactly_true": {str(n): power(n) for n in (9, 10, 12, 14, 15, 16, 19, 20, 24)},
   "power_at_n9": power(9),
   "n_for_80pc_power": n_for_power(0.80), "n_for_90pc_power": n_for_power(0.90),
   "consequence": ("at n=9 there is roughly a %.0f%% chance of returning UNRESOLVED even if (a) is exactly "
     "right. That is a coin flip on a paid experiment, and it is a property of the sizing RULE, not of the "
     "design." % (100 * (1 - power(9)))),
   "why_n9_can_fail": {"sd_rel_uncertainty_at_n9": float(1 / math.sqrt(2 * 8)),
     "halfwidth_if_realized_s_is_1sigma_high": hw(9, SD * 1.25),
     "P_realized_s_small_enough_alone": float(stats.chi2.cdf(
        8 * ((dist * 3 / stats.t.ppf(0.975, 8)) / SD) ** 2, 8))},
   "which_side_this_applies_to": ("the (a) side, i.e. the side that borrows THIS LANE's sd as its assumed "
     "value -- which is exactly the part in scope. Under (b) the Exponential arm's spread would plausibly "
     "be SMALLER, since the zero-support pathology is what is removed, so the (b) side likely has more "
     "power than this. NOT MEASURED, because that arm does not exist yet.")},

 "CHECK_4_per_column_prohibition": {
   "verdict": "CORRECTLY SCOPED, and the justification can be made stronger than the range alone",
   "the_11x_is_the_ABSOLUTE_sd_range": {"sd_by_column": sdcol.tolist(),
     "max_over_min_absolute": float(sdcol.max() / sdcol.min())},
   "this_lane_s_receipt_reports_the_RELATIVE_range": {"rel_sd_by_column": relcol.tolist(),
     "max_over_min_relative": float(relcol.max() / relcol.min()),
     "field_name": "is_the_spread_pparallel_structured.max_over_min_of_rel_sd"},
   "DO_NOT_CONFLATE": ("both are true and they are different quantities: 11.12x absolute, 1.87x relative. "
     "If a document cites '11x' next to this lane's field name it is quoting the wrong field."),
   "measured_per_column_feasibility_at_n9": [
     {"i_pparallel": r["i_pparallel"], "pparallel_bin": r["pparallel_bin"], "mean": r["mean_over_50"],
      "sd": float(sc), "own_midpoint": (r["mean_over_50"] + 1.0) / 2,
      "own_distance": r["mean_over_50"] - (r["mean_over_50"] + 1.0) / 2,
      "halfwidth_n9": hw(9, float(sc)),
      "resolvable_at_n9": bool(hw(9, float(sc)) < r["mean_over_50"] - (r["mean_over_50"] + 1.0) / 2),
      "power_n9": power(9, (r["mean_over_50"] - (r["mean_over_50"] + 1.0) / 2) / float(sc))}
     for r, sc in zip(d["per_pparallel_column"], sdcol)],
   "STRONGER_GROUND_FOR_THE_PROHIBITION": ("NO column is resolvable at n=9, and the reason is structural "
     "rather than incidental: because relative spread is near-constant across columns, each column's own "
     "Cohen d is nearly invariant, so EVERY per-column test sits near 50% power regardless of how large "
     "that column's effect is. A per-column verdict gains nothing anywhere. Column 15 is a separate case "
     "again -- its mean is 1.105, already at the (b) hypothesis, so a per-column test there would be "
     "testing a null effect (power 0.07).")},

 "DESIGN_CONCERNS_FLAGGED_TO_THE_MEDIATOR_NOT_AS_REVIEW_FINDINGS": [
   "none. This lane has no concern about Exponential(1) as the null that it would raise even informally; "
   "the same-mean same-variance differing-only-in-P(X=0) construction is a cleaner contrast than the "
   "instrument it replaced, which was this lane's."],
 "SUMMARY": ("arithmetic: all quoted figures reproduce. Use of this lane's numbers: correct, with one "
   "correction (pin the statistic for the BOUNDARY, not the sizing) and ONE SUBSTANTIVE FINDING -- n=9 is "
   "~57% power, not high confidence; 80% needs n=15 and 90% needs n=19. Whether that changes the decision "
   "is a cost question for the instrument's owner and Joseph, not this lane's call."),
}
P = "docs/orchestration/state/RECEIPT-20260815-trackA-sizing-second-read.json"
open(P, "w").write(json.dumps(out, indent=1) + "\n")
print("power n=9  %.4f   n for 80%%: %d   n for 90%%: %d" % (power(9), n_for_power(0.80), n_for_power(0.90)))
print("halfwidth n=9 %.6f  n=8 %.6f (shortfall %.4f)  n=6 %.6f" % (hw(9), hw(8), hw(8) - dist, hw(6)))
print("midpoints: median %.4f  mean-over-cells %.4f  ratio-of-sums %.4f"
      % (mid, (variants['mean_over_cells'].mean() + 1) / 2, (variants['ratio_of_sums'].mean() + 1) / 2))
print("written", P)
