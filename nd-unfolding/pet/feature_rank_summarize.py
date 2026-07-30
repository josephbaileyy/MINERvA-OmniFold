#!/usr/bin/env python3
"""Combine feature-rank arm JSONs into the floor-referenced ranking. Analysis only, no training.

Deliberately separate from `feature_rank_arms.py`: the arms cost GPU hours and may be produced by
several jobs (they were -- job 20599606 died mid-set on the `q3` non-finite defect and job
20601059 supplied the remainder), so the comparison must not require them to have come from one
process. Reads every `arm_<name>_s<seed>.json` in a directory and re-derives the verdicts.

THE DECISION RULE, restated here because it is the whole point. An extension arm counts only if
its shift away from base CLEARS THE BASE SEED-TO-SEED SPREAD. That floor is what CLM-006 lacked:
its two arms differed in niter AND train size AND representation, so its "Tier-1 median 4.25%"
mixes three effects and OMNIFOLD-DOSSIER.md:67 records it with no tolerance. A shift below the
floor is NOT a small effect -- it is an unmeasured one, and is reported as NOT RANKED rather than
as zero.

WHAT IS NOT DONE HERE. The whitened SVD ranking (C^-1/2 D) needs a covariance C_base, which comes
from the C_stat replica machinery and does not exist at this scale. This emits the UNWHITENED
shift ingredients only. Quoting a chi^2 from these numbers would be wrong twice over: no C, and
chi^2 is dominated by C's smallest eigenvalues, which are its least-determined directions
(cf. eavail_generator_significance.py:99-102, which prints the condition number for exactly this
reason, and adopt_unified_4d.py:8, which records 2285 negative eigenvalues in a throw covariance).
"""
import argparse
import glob
import json
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", default=["products/pet/feature_rank"],
                    help="one or more directories holding arm_<name>_s<seed>.json")
    ap.add_argument("--baseline", default="base")
    ap.add_argument("--out", default="products/pet/feature_rank/ranking.json")
    a = ap.parse_args()

    files = sorted({f for d in a.dirs for f in glob.glob(os.path.join(d, "arm_*.json"))})
    if not files:
        raise SystemExit(f"no arm_*.json under {a.dirs}")
    arms = {}
    for f in files:
        with open(f) as fh:
            r = json.load(fh)
        arms.setdefault(r["arm"], []).append(r)
    for k in arms:
        arms[k].sort(key=lambda r: r["seed"])

    # Every arm must sit on the same injected gap, else the recoveries are not comparable.
    gaps = {round(r["gap"], 10) for rs in arms.values() for r in rs}
    if len(gaps) != 1:
        raise SystemExit(f"arms disagree on the injected gap {gaps} -- different fixtures, "
                         "not comparable")
    gap = gaps.pop()

    def spread(specs):
        """Mean pairwise L1 between an arm's own seeds = that arm's retraining noise."""
        if len(specs) < 2:
            return float("nan")
        return float(np.mean([np.abs(specs[i] - specs[j]).sum()
                              for i in range(len(specs)) for j in range(i + 1, len(specs))]))

    print(f"{len(files)} arm runs over {len(arms)} arms; injected gap L1 = {gap:.5f}\n")
    print(f"{'arm':10s} {'n':>2s} {'seeds':>14s} {'recovery mean':>14s} {'sd':>8s} "
          f"{'seed spread L1':>15s}")
    table = {}
    for name, rs in sorted(arms.items()):
        specs = [np.asarray(r["spectrum"], float) for r in rs]
        recs = np.array([r["recovery"] for r in rs])
        sd = float(recs.std(ddof=1)) if len(recs) > 1 else float("nan")
        table[name] = {"n": len(rs), "seeds": [r["seed"] for r in rs],
                       "recovery_mean": float(recs.mean()), "recovery_sd": sd,
                       "seed_spread_l1": spread(specs),
                       "mean_spectrum": np.mean(specs, axis=0)}
        print(f"{name:10s} {len(rs):2d} {str([r['seed'] for r in rs]):>14s} "
              f"{recs.mean():+14.4f} {sd:8.4f} {table[name]['seed_spread_l1']:15.5f}")

    if a.baseline not in table:
        raise SystemExit(f"baseline arm '{a.baseline}' absent; have {sorted(table)}")
    floor = table[a.baseline]["seed_spread_l1"]
    base_spec = table[a.baseline]["mean_spectrum"]
    if not np.isfinite(floor):
        raise SystemExit(f"baseline '{a.baseline}' has <2 seeds, so there is no floor to compare "
                         "against; a single-seed baseline cannot separate signal from retraining "
                         "noise")

    print(f"\nbaseline '{a.baseline}' retraining floor (mean pairwise seed L1) = {floor:.5f}")
    print(f"{'arm':10s} {'shift vs base L1':>17s} {'x floor':>9s}   verdict")
    ranking = {}
    for name, t in sorted(table.items(), key=lambda kv: -abs(
            np.abs(kv[1]["mean_spectrum"] - base_spec).sum())):
        if name == a.baseline:
            continue
        shift = float(np.abs(t["mean_spectrum"] - base_spec).sum())
        ratio = shift / floor
        # A shift inside the baseline's own seed scatter is indistinguishable from retraining
        # noise. Calling it "small" would imply it was measured; it was not.
        verdict = "RANKED (above floor)" if ratio > 1.0 else "NOT RANKED (at/below floor)"
        ranking[name] = {"shift_l1": shift, "x_floor": ratio, "verdict": verdict,
                         "recovery_mean": t["recovery_mean"],
                         "recovery_delta_vs_base": t["recovery_mean"] - table[a.baseline]["recovery_mean"]}
        print(f"{name:10s} {shift:17.5f} {ratio:9.2f}   {verdict}")

    ranked = [k for k, v in ranking.items() if v["x_floor"] > 1.0]
    print()
    if ranked:
        print(f"RANKED above the retraining floor: {', '.join(sorted(ranked))}")
        print("Read as a shape effect only, and as a CLOSURE: pseudo-data is an independent MC")
        print("half, so this is not evidence that real data/MC differ in these features.")
    else:
        print("NO arm clears the baseline retraining floor.")
        print("Reading: given what the recoil cloud already carries, the already-dumped event")
        print("features add no measurable shape information at this scale. That is evidence")
        print("AGAINST spending the C++ dump + FPS-CV regeneration on a wider event block --")
        print("but it bounds the EXISTING features only. The eight absent extension arrays are")
        print("unrankable until G2; see closure_unread_variable_phi.py for the pre-G2 evidence.")

    payload = {"gap": gap, "baseline": a.baseline, "floor_l1": floor,
               "arms": {k: {kk: vv for kk, vv in v.items() if kk != "mean_spectrum"}
                        for k, v in table.items()},
               "ranking": ranking, "ranked_above_floor": sorted(ranked)}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
