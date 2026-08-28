#!/usr/bin/env python3
"""Combine the per-seed coupled-phi sweeps into one curve. Analysis only, no training.

Separate from the driver for the same reason feature_rank_summarize.py is: the seeds come from
DIFFERENT JOBS (20636012 seed 0, 20636013 seed 7), so the comparison must not require them to
have come from one process.

WHAT THIS GUARDS AGAINST. The driver's own crossing estimate interpolates the gain curve to the
+0.25 clearance using a single seed's numbers. That is the right quantity and the wrong error
model: the seed spread GROWS with coupling (thinning at 16% acceptance leaves a far more variable
fixture than thinning at 100%), so the crossing, if it exists, sits in the noisiest part of the
curve. This script computes the crossing three times -- on the mean curve, on mean+spread, and on
mean-spread -- and REFUSES to quote a single number when the band is wider than the gap between
adjacent tested couplings. An interpolated crossing the seeds cannot resolve is not a measurement.

WHAT IT ALSO CHECKS. Whether the curve's SHAPE is resolved at all: a monotone decline is only a
decline if each step down exceeds the local seed spread. A curve that wanders inside its own noise
band is reported as FLAT, not as a weak trend, for the same reason feature_rank_summarize.py
reports sub-floor shifts as NOT RANKED rather than as zero.
"""
import argparse
import glob
import json
import os

import numpy as np

CLEARANCE = 0.25   # the threshold job 20600383 used for "the extension adds capability"
# Trained-or-not floor for an arm's own recovery, matching the driver's `control_ok = ctrl > 0.5`.
# Applied to the EXTENDED arm here because the driver's positive control only exercises the base
# arm. This is a did-it-train gate, nowhere near the ~0.90 the extended arm actually reaches, so it
# invalidates nothing in the recorded sweeps -- it exists so a future undertrained point cannot be
# read as a real gain collapse.
EXTENDED_FLOOR = 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", default=["products/pet"],
                    help="directories holding closure_coupled_phi_sweep[_hi]_s<seed>.json")
    ap.add_argument("--pattern", default="closure_coupled_phi_sweep*_s*.json",
                    help="glob for the per-seed sweep JSONs; the default picks up BOTH the "
                         "original lambda grid and the high-lambda extension")
    ap.add_argument("--law-fit-max-corr", type=float, default=0.62,
                    help="upper edge of the range leak=corr^2 was originally fitted on; points "
                         "above this are the OUT-OF-SAMPLE test of the law")
    ap.add_argument("--out", default="products/pet/coupled_phi_curve.json")
    a = ap.parse_args()

    files = sorted({f for d in a.dirs for f in glob.glob(os.path.join(d, a.pattern))})
    if len(files) < 2:
        raise SystemExit(f"need >=2 seed files to have a spread; found {files}. A single-seed "
                         "curve cannot separate a bend from retraining noise.")

    runs = []
    for f in files:
        with open(f) as fh:
            r = json.load(fh)
        r["_file"] = os.path.basename(f)
        runs.append(r)
    seeds = [r["config"]["seed"] for r in runs]
    print(f"{len(runs)} seed runs {seeds} from {len(files)} files")

    # ONE FIXTURE, OR THE GAINS ARE NOT ON ONE CURVE. feature_rank_summarize.py:51 hard-fails when
    # its arms disagree on the injected gap, for exactly this reason; this script globbed two files
    # and merged them on trust. Everything that defines the fixture must match. The lambda GRID is
    # the deliberate exception -- the high-lambda extension is a different grid by design, which is
    # the whole reason the glob picks up both files.
    FIXTURE_KEYS = ("n_events", "tokens", "strata", "amplitude", "niter", "epochs", "batch_size")
    fixtures = {}
    for r in runs:
        fixtures.setdefault(tuple(r["config"].get(k) for k in FIXTURE_KEYS), []).append(r["_file"])
    if len(fixtures) != 1:
        detail = "\n".join(
            f"    {', '.join(f'{k}={v!r}' for k, v in zip(FIXTURE_KEYS, key))}\n"
            f"      <- {', '.join(fs)}" for key, fs in fixtures.items())
        raise SystemExit("sweep files disagree on the fixture, so their gains do not lie on one "
                         f"curve and merging them would confound coupling with configuration:\n"
                         f"{detail}\n  Only the lambda grid may differ between files.")

    # Grids are UNIONED, not required identical: the high-lambda extension is a different grid by
    # design, and the overlap point (lambda 2.2) is a deliberate cross-job tie-in rather than a
    # mistake. What still has to hold is that every coupling carries >=2 DISTINCT SEEDS, since a
    # single-seed point has no spread and cannot gate its own step.
    grid = sorted({round(p["coupling"], 6) for r in runs for p in r["points"]})

    def pairwise_spread(v):
        """Mean pairwise |difference| = this point's retraining noise in whatever quantity."""
        return float(np.mean([abs(v[i] - v[j])
                              for i in range(len(v)) for j in range(i + 1, len(v))]))

    rows = []
    for lam in grid:
        # Tagged with the seed, because counting POINTS is not counting SEEDS: lambda 2.2 appears
        # in both the original and high-lambda grids, so a same-seed pair of files would satisfy
        # `len(pts) >= 2` while carrying zero retraining information. Found by review 2026-07-31.
        tagged = [(r["config"]["seed"], p) for r in runs for p in r["points"]
                  if round(p["coupling"], 6) == lam]
        pts = [p for _s, p in tagged]
        n_distinct = len({s for s, _p in tagged})
        if n_distinct < 2:
            raise SystemExit(f"coupling {lam} carries {len(pts)} point(s) from only {n_distinct} "
                             f"distinct seed(s); every point needs >=2 SEEDS or its spread "
                             f"measures nothing and its step cannot be gated against retraining "
                             f"noise")
        # A point is usable only if EVERY seed's positive control passed there. One failed control
        # means that fixture is untrained, not that the gain vanished.
        #
        # THE EXTENDED ARM IS GATED TOO, on the same threshold. The driver's positive control runs
        # the BASE arm on a pT tilt, so it cannot detect an extended arm that failed to train --
        # and `gain = extended - leak` collapses either way, so an untrained extended arm would be
        # read as a real crossing. That is the confound the control exists to exclude, for the arm
        # it does not test. The extended arm's own phi recovery IS the right control for it (same
        # tilt, same metric), so it is gated here rather than inferred: recomputed from the
        # recorded value so runs predating the driver's `extended_ok` field are covered too.
        valid = (all(p.get("control_ok", False) for p in pts)
                 and all(p.get("extended", 0.0) > EXTENDED_FLOOR for p in pts))
        rows.append({
            "coupling": lam,
            "corr": float(np.mean([p["corr"]["cosphi_pt"] for p in pts])),
            "leak": float(np.mean([p["leak"] for p in pts])),
            "extended": float(np.mean([p["extended"] for p in pts])),
            "gain": float(np.mean([p["gain"] for p in pts])),
            "gain_spread": pairwise_spread([p["gain"] for p in pts]),
            # The law below judges LEAK residuals, so it needs the leak's own seed noise. Using
            # the gain's was a 26x understatement at lambda=1.60 (leaks 0.2148/0.2378, spread
            # 0.0230; gains 0.6473/0.6464, spread 0.0009) because the extended arm's scatter
            # cancels in the difference. Found by review 2026-07-31.
            "leak_spread": pairwise_spread([p["leak"] for p in pts]),
            "extended_min": float(min(p["extended"] for p in pts)),
            "control_min": float(min(p["control"] for p in pts)),
            "accepted": float(np.mean([p["accepted_fraction"] for p in pts])),
            "valid": bool(valid), "n_seeds": n_distinct, "n_points": len(pts)})

    print(f"\n{'lambda':>7s} {'corr':>7s} {'accept':>7s} {'leak':>8s} {'extended':>9s} "
          f"{'gain':>8s} {'gn sprd':>8s} {'lk sprd':>8s} {'ext min':>8s} {'ctrl min':>9s}  valid")
    for r in rows:
        print(f"{r['coupling']:7.2f} {r['corr']:+7.3f} {100*r['accepted']:6.1f}% "
              f"{r['leak']:+8.4f} {r['extended']:+9.4f} {r['gain']:+8.4f} {r['gain_spread']:8.4f} "
              f"{r['leak_spread']:8.4f} {r['extended_min']:+8.4f} {r['control_min']:+9.4f}  "
              f"{'yes' if r['valid'] else 'NO'}")

    usable = [r for r in rows if r["valid"]]
    if len(usable) < 3:
        raise SystemExit("fewer than three valid points -- no curve")

    # ---- is the shape resolved? Each step must clear the larger of the two local spreads.
    steps = []
    for i in range(len(usable) - 1):
        d = usable[i + 1]["gain"] - usable[i]["gain"]
        noise = max(usable[i]["gain_spread"], usable[i + 1]["gain_spread"])
        steps.append({"from": usable[i]["coupling"], "to": usable[i + 1]["coupling"],
                      "delta": d, "noise": noise,
                      "resolved": bool(noise > 0 and abs(d) > noise)})
    print(f"\n{'step':>16s} {'delta gain':>11s} {'seed noise':>11s}  resolved")
    for s in steps:
        print(f"{s['from']:6.2f} -> {s['to']:5.2f} {s['delta']:+11.4f} {s['noise']:11.4f}  "
              f"{'yes' if s['resolved'] else 'no (inside noise)'}")
    resolved_down = [s for s in steps if s["resolved"] and s["delta"] < 0]
    total_drop = usable[0]["gain"] - usable[-1]["gain"]

    # ---- leak = corr^2, tested OUT OF SAMPLE.
    # The relation was read off points with corr <= --law-fit-max-corr. Anything above that edge
    # is a PREDICTION, not a fit, and is the only thing that can tell a mechanism from a
    # curve-fit: a law that holds only where it was fitted has explained nothing. Residuals are
    # judged against each point's own seed spread, not against a fixed tolerance, for the same
    # reason the steps are.
    law = [{"corr": r["corr"], "leak": r["leak"], "pred": r["corr"] ** 2,
            "ratio": r["leak"] / r["corr"] ** 2, "resid": r["leak"] - r["corr"] ** 2,
            "spread": r["leak_spread"], "gain_spread": r["gain_spread"],
            "in_fit": bool(abs(r["corr"]) <= a.law_fit_max_corr),
            "extended": r["extended"]}
           for r in usable if abs(r["corr"]) >= 0.05]   # corr^2 ~ 0: the ratio is meaningless
    out_law = {"fit_max_corr": a.law_fit_max_corr, "points": law}
    if law:
        print("\nleak vs corr^2 (the conjecture from the lambda<=2.2 sweep)")
        print(f"{'corr':>7s} {'corr^2':>8s} {'leak':>8s} {'ratio':>7s} {'resid':>8s} "
              f"{'leak sd':>8s}  range")
        for L in law:
            print(f"{L['corr']:+7.3f} {L['pred']:8.4f} {L['leak']:8.4f} {L['ratio']:7.3f} "
                  f"{L['resid']:+8.4f} {L['spread']:8.4f}  "
                  f"{'fitted' if L['in_fit'] else 'OUT-OF-SAMPLE'}")
        oos = [L for L in law if not L["in_fit"]]
        if oos:
            # TOLERANCE IS POOLED, NOT PER-POINT. A two-seed spread is a terrible noise estimate:
            # in the lambda<=2.2 sweep it ranged 0.0009 to 0.0553 across points that differ only
            # in coupling, so a point whose two seeds happened to agree would "break" any law by
            # luck of the draw. The yardstick is instead the law's OWN residual scatter where it
            # was fitted, floored by the pooled seed noise so a suspiciously tight fit cannot make
            # the test unfalsifiable in the other direction.
            #
            # The pooled floor is the LEAK's seed noise, since leak is what the residual is in.
            # It was the GAIN's, which is systematically larger (median 0.0192 vs 0.0104 over the
            # ten-point curve) because the extended arm's scatter enters the gain and cancels out
            # of the leak -- i.e. the floor was too LOOSE, biasing toward "the law holds". The
            # recorded verdict is unaffected: 3xRMS = 0.0233 dominated the max() either way, so
            # the same 2 of 4 out-of-sample points break. Found by review 2026-07-31.
            in_fit = [L for L in law if L["in_fit"]]
            rms = float(np.sqrt(np.mean([L["resid"] ** 2 for L in in_fit]))) if in_fit else 0.0
            pooled = float(np.median([L["spread"] for L in law]))
            tol = max(3.0 * rms, pooled)
            broke = [L for L in oos if abs(L["resid"]) > tol]
            out_law.update({"out_of_sample_n": len(oos), "out_of_sample_broken": len(broke),
                            "in_fit_resid_rms": rms, "pooled_seed_noise": pooled,
                            "tolerance": tol, "holds_out_of_sample": not broke})
            print(f"\nin-fit residual RMS {rms:.4f}, pooled LEAK seed noise {pooled:.4f} "
                  f"-> tolerance max(3xRMS, pooled) = {tol:.4f}")
            if broke:
                print(f"LEAK = CORR^2 BREAKS out of sample: {len(broke)} of {len(oos)} points "
                      f"above corr {a.law_fit_max_corr:.2f} miss by more than {tol:.4f} "
                      f"(worst {max(abs(L['resid']) for L in broke):+.4f}). The relation was a "
                      f"curve-fit over the original range, not a mechanism, and any crossing "
                      f"inferred from it is void -- read the crossing off the measured points "
                      f"below instead.")
            else:
                print(f"LEAK = CORR^2 HOLDS out of sample: all {len(oos)} points above corr "
                      f"{a.law_fit_max_corr:.2f} sit within {tol:.4f} (worst "
                      f"{max(abs(L['resid']) for L in oos):+.4f}). The baseline recovers the "
                      f"shared variance and nothing else -- a mechanism, not a fit.")
        else:
            out_law["holds_out_of_sample"] = None
            print(f"\nNo point above corr {a.law_fit_max_corr:.2f}: the law is untested outside "
                  "the range it was read off, so it stays a conjecture.")
        # The flat-extension half of the conjecture has to survive too, or a crossing arrives
        # early for a reason that has nothing to do with the leak.
        e = np.array([L["extended"] for L in law])
        out_law["extended_mean"] = float(e.mean())
        out_law["extended_sd"] = float(e.std(ddof=1)) if len(e) > 1 else float("nan")
        print(f"extended arm over the same points: mean {e.mean():+.4f} sd {e.std(ddof=1):.4f} "
              f"min {e.min():+.4f} -- the 'flat extension' half of the conjecture "
              f"{'HOLDS' if e.std(ddof=1) < 0.05 else 'BREAKS (the extension itself degrades)'}")

    def crossing(offset):
        """corr at which the (mean + offset*spread) curve falls through CLEARANCE."""
        xs = [r["corr"] for r in usable]
        gs = [r["gain"] + offset * r["gain_spread"] for r in usable]
        for i in range(len(usable) - 1):
            if (gs[i] - CLEARANCE) * (gs[i + 1] - CLEARANCE) <= 0 and gs[i] != gs[i + 1]:
                t = (gs[i] - CLEARANCE) / (gs[i] - gs[i + 1])
                return xs[i] + t * (xs[i + 1] - xs[i])
        return None

    mid, hi, lo = crossing(0.0), crossing(+1.0), crossing(-1.0)
    corr_max = usable[-1]["corr"]
    out = {"seeds": seeds, "files": [r["_file"] for r in runs], "clearance": CLEARANCE,
           "points": rows, "steps": steps, "law_leak_eq_corr2": out_law,
           "total_drop": total_drop, "crossing_mean": mid,
           "crossing_band": [lo, hi], "corr_max_tested": corr_max}

    print()
    if mid is None:
        # No crossing inside the tested range. The honest statement is a BOUND, not an
        # extrapolation: nothing here constrains what the curve does past the last point.
        out["verdict"] = ("GAIN_CLEARS_THROUGHOUT" if min(r["gain"] for r in usable) > CLEARANCE
                          else "GAIN_BELOW_THROUGHOUT")
        if out["verdict"] == "GAIN_CLEARS_THROUGHOUT":
            print(f"The gain clears +{CLEARANCE:.2f} at EVERY valid coupling out to "
                  f"corr(cos phi,pT) = {corr_max:+.3f}.")
            print(f"So the capability claim does NOT depend on the independence assumption "
                  f"anywhere in the tested range, and the crossing -- if there is one -- lies "
                  f"beyond {corr_max:+.3f}. This sweep does not say where; extrapolating past "
                  f"the last point would be inventing a number.")
            if resolved_down:
                print(f"The gain does DECLINE measurably ({total_drop:+.4f} total, "
                      f"{len(resolved_down)} of {len(steps)} steps clear their seed noise), so "
                      f"the independence caveat was real -- it is just far smaller than the "
                      f"headline gain over this range.")
            else:
                print(f"No step clears its own seed noise (total drift {total_drop:+.4f}), so "
                      f"the curve is FLAT at this resolution: coupling has no measurable effect "
                      f"on the gain, not merely a small one.")
        else:
            print("The gain never clears the threshold -- including at zero coupling, which "
                  "contradicts job 20600383. Suspect the fixture, not the physics.")
    else:
        band = [x for x in (lo, hi) if x is not None]
        # Adjacent-point separation is the resolution floor: an interpolated crossing cannot be
        # quoted more precisely than the grid it was interpolated on.
        gaps = [usable[i + 1]["corr"] - usable[i]["corr"] for i in range(len(usable) - 1)]
        width = (max(band) - min(band)) if len(band) == 2 else float("inf")
        if width > min(gaps):
            out["verdict"] = "CROSSING_PRESENT_BUT_UNRESOLVED"
            print(f"The gain does fall through +{CLEARANCE:.2f}, near corr(cos phi,pT) ~ "
                  f"{mid:+.3f}, but the +-1 seed-spread band spans {min(band):+.3f} to "
                  f"{max(band):+.3f} -- wider than the {min(gaps):.3f} spacing of the grid it is "
                  f"interpolated on. Two seeds cannot place this crossing. Quote the BAND, not "
                  f"the midpoint, and add seeds before using it as a decision threshold.")
        else:
            out["verdict"] = "CROSSING_RESOLVED"
            print(f"The gain falls through +{CLEARANCE:.2f} at corr(cos phi,pT) = {mid:+.3f} "
                  f"(+-1 seed spread: {min(band):+.3f} to {max(band):+.3f}).")
            print(f"THE 08-03 TEST: measure corr(cos phi, pT) in the real FPS sample. Below "
                  f"{mid:+.3f}, the extension's phi channel still buys something; above, it "
                  f"does not.")

    print("\nCLOSURE, not data: pseudo-data is a reweighted MC half. This bounds a CAPABILITY and "
          "is not evidence that the real data carries an azimuthal mismatch.")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
