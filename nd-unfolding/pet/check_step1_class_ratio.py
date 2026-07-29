#!/usr/bin/env python3
"""Measure the step-1 class ratio R that `normalize=True` erases -- login-safe, read-only.

WHY THIS EXISTS
---------------
`fullevent_fps_dataloader.py:613` (MC) and `:658` (measured) both pass `normalize=True`
to the vendored DataLoader. `omnifold_nn/omnifold/dataloader.py:110-113` rescales each
loader's pass_reco weight sum in place to 1e6, and `omnifold_nn/omnifold/omnifold.py:176-177`
feeds exactly those arrays as the two step-1 class weight blocks. So at iteration 0 the
class totals are identical and W1/W0 == 1 by construction: the physical POT-scaled
data/MC rate ratio R is erased, and nothing downstream restores it.

This script measures R. It reads ONLY small 1-D members of the G2 npz (weights, masks,
scalars) -- never the point clouds -- so it costs a few hundred MB and a minute or two on
a login node. It writes nothing except an optional JSON report. It does NOT construct a
DataLoader, import TensorFlow, or touch the refiner.

WHAT R IS
---------
Step-1 class 0 (MC)   total = sum(w_truth[pass_reco])   -- RAW MC weights
Step-1 class 1 (data) total = sum(w_refined)            -- signed data - POT-scaled bkg

`w_truth` in this npz is the RAW literal ROOT per-event MC weight, NOT POT-scaled
(`fullevent_fps_dataloader.py:551`; convention stated at
`dump_pointcloud_inputs.py:183-186`: "Consumers apply pot_scale"). To compare an MC
prediction to a measured yield the MC side must be scaled into the data's POT, so the
physically meaningful ratio is

    R = (n_data - pot_scale * sum(w_bkg)) / (pot_scale * sum(w_truth[pass_reco]))

Both conventions are reported. `R_pot_scaled` is the physical one and the one to use;
`R_unscaled` (denominator without pot_scale) is printed only because it is easy to
arrive at by mistake, and the two differ by 1/pot_scale ~ 4.7x.

WHICH MC WEIGHT BELONGS IN THE DENOMINATOR (finding B-4 changes this answer)
---------------------------------------------------------------------------
The denominator above uses `w_truth` because that is what the loader actually feeds the
reco leg: `grep -c w_reco fullevent_fps_dataloader.py` is 0, and the single
`w_truth_full` vector at `:551` is passed to `DataLoader(weight=w_truth, ...)` at
`:612-614` and consumed by BOTH `omnifold.py:176-177` (step 1, detector level) and
`:196-197` (step 2, truth level). The G2 contract nonetheless carries a separate
reco-leg weight (`dump_pointcloud_inputs.py:201`, required at `:299`/`:540`), and the
validated 2D path uses the two legs separately
(`2d-unfolding/unfold_2d_omnifold_unbinned.py:1715-1716`).

So R is denominator-dependent, and B-4 and B1 are NOT independent fixes: if the reco leg
is corrected to use `w_reco`, the physical denominator becomes
`pot_scale * sum(w_reco[pass_reco])` and R moves by
`sum(w_truth[pass_reco]) / sum(w_reco[pass_reco])`. This script therefore reports R under
both denominators, plus the w_reco-vs-w_truth comparison that is B-4's own minimal check,
so one pass over the dump answers both questions. If the two agree bit-for-bit for the
CV, B-4 is inactive for the nominal and `R_pot_scaled` stands as written -- but repeat per
systematic endpoint before P5B, since reco-side reweighters are exactly the point there.

SELF-CHECK
----------
The numerator is independently known: the promoted Gate-2 receipt records
`independent_binned_checks.raw_signed_sum = 4006528.6006158064`, built from the same
inputs by frozen code. If this script's numerator does not reproduce that, it has read
the wrong members and R must NOT be trusted. That check is fail-closed.

SUBSAMPLE NOTE (why "just delete normalize=True" is NOT the fix)
----------------------------------------------------------------
The nominal trains on a bounded MC subsample (`--max-events`, 2M for the nominal) while
the measured target is the FULL data+background inventory. With `normalize=False` the
step-1 class ratio would become the arbitrary MC *sampling fraction*, not R. Pass
--max-events to print that number and see how far off it lands.

USAGE
-----
    python3 check_step1_class_ratio.py --inputs /path/to/G2_FPS_MEFHC_P12.npz
    python3 check_step1_class_ratio.py --inputs ... --max-events 2000000 --json out.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

# B1: the R formula lives in ONE body (fullevent_fps_dataloader.step1_class_ratio) so a B-4 flip
# is a one-line change rather than a search. This script MEASURES R on 08-03, so a private copy
# of the arithmetic here would be the first place that rule broke. Login-safe: the loader module
# imports only numpy at module level (ROOT/TF/u2d are all deferred).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fullevent_fps_dataloader as fed  # noqa: E402

# ---- frozen expectations from the promoted Gate-2 receipt --------------------
# nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
RECEIPT_RAW_SIGNED_SUM = 4006528.6006158064   # independent_binned_checks.raw_signed_sum
RECEIPT_RAW_DATA_SUM = 4116128.0              # independent_binned_checks.raw_data_sum
RECEIPT_BKG_POT_SCALED_SUM = 109599.39938419356  # ..raw_background_pot_scaled_sum
RECEIPT_POT_SCALE = 0.21240500334472884       # runtime_target.pot_scale
RECEIPT_ROWS = {"data": 4116128, "background": 564591, "signal": 49152885}
NUMERATOR_RTOL = 1e-9    # frozen code, same inputs: expect bit-comparable agreement
NUMERATOR_ATOL = 1.0     # one weight-unit of slack


class CheckError(RuntimeError):
    pass


def die(msg: str) -> None:
    raise CheckError(msg)


def _resolve_pot_scale(d) -> tuple[float, str]:
    """Mirror the loader's own resolution order (fullevent_fps_dataloader.py:570-578)."""
    if "pot_scale" in d.files:
        return float(np.asarray(d["pot_scale"]).item()), "pot_scale"
    if "data_pot" in d.files and "mc_pot" in d.files:
        dp = float(np.asarray(d["data_pot"]).item())
        mp = float(np.asarray(d["mc_pot"]).item())
        if not (np.isfinite(mp) and mp > 0.0):
            die(f"invalid mc_pot {mp!r}")
        return dp / mp, "data_pot/mc_pot"
    die("no pot_scale (and no data_pot/mc_pot) in input")


def run(inputs: str, max_events: int | None) -> dict:
    out: dict = {"inputs": inputs}

    with np.load(inputs, allow_pickle=True, mmap_mode=None) as d:
        for key in ("w_truth", "pass_reco", "w_bkg"):
            if key not in d.files:
                die(f"required member {key!r} absent from input")

        pot_scale, pot_source = _resolve_pot_scale(d)
        if not (np.isfinite(pot_scale) and pot_scale > 0.0):
            die(f"invalid pot_scale {pot_scale!r} (require finite > 0)")

        # --- MC side: raw signal weights over the reco-accepted subset ---------
        w_truth = np.asarray(d["w_truth"], dtype=np.float64)
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)
        if w_truth.shape != pass_reco.shape:
            die(f"w_truth {w_truth.shape} and pass_reco {pass_reco.shape} disagree")
        if not np.all(np.isfinite(w_truth)):
            die("w_truth contains non-finite entries")

        n_signal = int(w_truth.shape[0])
        n_pass_reco = int(pass_reco.sum())
        sum_w_truth_pass = float(w_truth[pass_reco].sum())

        # --- B-4: the reco-leg weight the loader ignores ----------------------
        # Costs one more ~400 MB float64 view; released immediately. Absence is not
        # fatal here (the loader never reads it), but it IS a contract violation.
        wreco: dict | None = None
        if "w_reco" in d.files:
            w_reco = np.asarray(d["w_reco"], dtype=np.float64)
            if w_reco.shape != w_truth.shape:
                die(f"w_reco {w_reco.shape} and w_truth {w_truth.shape} disagree")
            if not np.all(np.isfinite(w_reco)):
                die("w_reco contains non-finite entries")
            wt_p, wr_p = w_truth[pass_reco], w_reco[pass_reco]
            differs = wr_p != wt_p
            n_differs = int(differs.sum())
            nz = wt_p != 0.0
            ratio = wr_p[nz] / wt_p[nz]
            wreco = {
                "sum_w_reco_pass_reco_raw": float(wr_p.sum()),
                "bit_identical_to_w_truth_over_pass_reco": n_differs == 0,
                "n_pass_reco_differing": n_differs,
                "frac_pass_reco_differing": n_differs / n_pass_reco if n_pass_reco else None,
                "ratio_w_reco_over_w_truth": {
                    "min": float(ratio.min()) if ratio.size else None,
                    "median": float(np.median(ratio)) if ratio.size else None,
                    "max": float(ratio.max()) if ratio.size else None,
                    "n_w_truth_zero": int((~nz).sum()),
                },
            }
            del w_reco, wt_p, wr_p, differs, nz, ratio

        # --- data side: unit-weight data rows minus POT-scaled background ------
        w_bkg = np.asarray(d["w_bkg"], dtype=np.float64)
        if not np.all(np.isfinite(w_bkg)):
            die("w_bkg contains non-finite entries")
        n_bkg = int(w_bkg.shape[0])
        sum_w_bkg = float(w_bkg.sum())
        bkg_pot_scaled = pot_scale * sum_w_bkg

        # data row count: prefer the measured cloud's own row count
        if "measured_pc" in d.files:
            n_data = int(np.asarray(d["measured_pc"]).shape[0])
        elif "measured_scalars" in d.files:
            n_data = int(np.asarray(d["measured_scalars"]).shape[0])
        else:
            die("neither measured_pc nor measured_scalars present; cannot count data rows")

    numerator = float(n_data) - bkg_pot_scaled

    # --- fail-closed self-check against the frozen receipt --------------------
    if not np.isclose(numerator, RECEIPT_RAW_SIGNED_SUM,
                      rtol=NUMERATOR_RTOL, atol=NUMERATOR_ATOL):
        die(f"numerator {numerator!r} does not reproduce the promoted Gate-2 receipt's "
            f"raw_signed_sum {RECEIPT_RAW_SIGNED_SUM!r} -- this script has read the wrong "
            f"members or the input is not the frozen G2 dump. R is NOT trustworthy; stop.")
    for label, got, want in (("n_data", n_data, RECEIPT_ROWS["data"]),
                             ("n_bkg", n_bkg, RECEIPT_ROWS["background"]),
                             ("n_signal", n_signal, RECEIPT_ROWS["signal"])):
        if got != want:
            die(f"{label} = {got} != frozen receipt {want}; wrong input file")
    if not np.isclose(pot_scale, RECEIPT_POT_SCALE, rtol=1e-12, atol=0.0):
        die(f"pot_scale {pot_scale!r} != frozen receipt {RECEIPT_POT_SCALE!r}")

    denom_pot = pot_scale * sum_w_truth_pass
    if denom_pot <= 0.0:
        die(f"non-positive MC denominator {denom_pot!r}")

    # THE shared formula -- identical body to the one the loader and both gates use.
    try:
        R_pot = fed.step1_class_ratio(n_data=float(n_data), sum_w_bkg_raw=sum_w_bkg,
                                      sum_w_mc_reco_raw=sum_w_truth_pass, pot_scale=pot_scale)
    except ValueError as exc:
        die(str(exc))
    # NOT the formula: the denominator-unscaled convention, reported only because it is easy to
    # arrive at by mistake and differs by 1/pot_scale ~ 4.7x. Deliberately kept inline so it can
    # never be confused for the shared one above.
    R_unscaled = numerator / sum_w_truth_pass

    out.update({
        "pot_scale": pot_scale,
        "pot_scale_source": pot_source,
        "n_signal_rows": n_signal,
        "n_signal_pass_reco": n_pass_reco,
        "signal_reco_acceptance_rowfrac": n_pass_reco / n_signal if n_signal else None,
        "n_data_rows": n_data,
        "n_bkg_rows": n_bkg,
        "sum_w_truth_pass_reco_raw": sum_w_truth_pass,
        "sum_w_bkg_raw": sum_w_bkg,
        "bkg_pot_scaled_sum": bkg_pot_scaled,
        "numerator_signed_data": numerator,
        "receipt_numerator_check": "OK",
        "R_pot_scaled": R_pot,
        "R_unscaled": R_unscaled,
        "erased_factor_note": "step-1 forced W1/W0 == 1; the physical value is R_pot_scaled",
    })

    # --- R under the w_reco denominator (what B-4's fix would make it) --------
    if wreco is not None:
        denom_wreco = pot_scale * wreco["sum_w_reco_pass_reco_raw"]
        wreco["R_pot_scaled_wreco_denominator"] = (
            fed.step1_class_ratio(n_data=float(n_data), sum_w_bkg_raw=sum_w_bkg,
                                  sum_w_mc_reco_raw=wreco["sum_w_reco_pass_reco_raw"],
                                  pot_scale=pot_scale)
            if denom_wreco > 0 else None)
        wreco["R_shift_factor_if_B4_fixed"] = (sum_w_truth_pass
                                               / wreco["sum_w_reco_pass_reco_raw"]
                                               if wreco["sum_w_reco_pass_reco_raw"] else None)
        out["w_reco_reco_leg"] = wreco
    else:
        out["w_reco_reco_leg"] = {"present_in_dump": False,
                                  "note": "w_reco absent -- required by "
                                          "dump_pointcloud_inputs.py:299; contract violation"}

    # --- what normalize=False would actually give (option-1 counterexample) ---
    if max_events:
        m = int(max_events)
        if m > n_signal:
            die(f"--max-events {m} exceeds signal rows {n_signal}")
        # The loader subsamples the FULL signal inventory, then takes pass_reco[imc].
        # Row-fraction scaling is the right first-order model of that subsample's
        # weight sum; this is indicative, not the exact realized draw.
        frac = m / n_signal
        sub_sum = sum_w_truth_pass * frac
        out["subsample"] = {
            "max_events": m,
            "row_fraction_of_full_inventory": frac,
            "approx_sum_w_truth_pass_reco": sub_sum,
            "class_ratio_if_normalize_false": (numerator / (pot_scale * sub_sum)
                                               if sub_sum > 0 else None),
            "interpretation": ("with normalize=False the step-1 class ratio tracks the MC "
                               "SAMPLING FRACTION, not R -- which is why deleting "
                               "normalize=True is not the fix"),
        }

    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--inputs", required=True,
                    help="path to G2_FPS_MEFHC_P12.npz (the frozen full-event dump)")
    ap.add_argument("--max-events", type=int, default=None,
                    help="also report the class ratio a normalize=False run would see "
                         "for this bounded MC subsample (nominal uses 2000000)")
    ap.add_argument("--json", dest="json_out", default=None,
                    help="write the report to this path as JSON")
    args = ap.parse_args(argv)

    try:
        rep = run(args.inputs, args.max_events)
    except CheckError as exc:
        print(f"[step1-ratio][FAIL] {exc}", file=sys.stderr)
        return 1

    print("\n  step-1 class ratio -- the quantity normalize=True erases")
    print(f"  pot_scale                     = {rep['pot_scale']:.17g}  ({rep['pot_scale_source']})")
    print(f"  signal rows                   = {rep['n_signal_rows']:,}")
    print(f"  signal rows pass_reco         = {rep['n_signal_pass_reco']:,} "
          f"({rep['signal_reco_acceptance_rowfrac']:.4f} of inventory)")
    print(f"  sum w_truth[pass_reco] (raw)  = {rep['sum_w_truth_pass_reco_raw']:.6f}")
    print(f"  data rows                     = {rep['n_data_rows']:,}")
    print(f"  bkg POT-scaled sum            = {rep['bkg_pot_scaled_sum']:.6f}")
    print(f"  signed data numerator         = {rep['numerator_signed_data']:.6f}"
          f"   [receipt check {rep['receipt_numerator_check']}]")
    print()
    print(f"  R (physical, POT-scaled MC)   = {rep['R_pot_scaled']:.6f}   <-- USE THIS")
    print(f"  R (denominator unscaled)      = {rep['R_unscaled']:.6f}   (wrong convention, "
          f"shown to prevent the mistake)")
    print(f"\n  step 1 currently forces W1/W0 = 1.0, so the erased factor is "
          f"{rep['R_pot_scaled']:.6f}.")

    wr = rep.get("w_reco_reco_leg") or {}
    if wr.get("present_in_dump") is False:
        print(f"\n  [B-4] {wr['note']}")
    elif wr:
        print("\n  [B-4] reco-leg weight the loader never reads (w_reco):")
        if wr["bit_identical_to_w_truth_over_pass_reco"]:
            print("    w_reco == w_truth bit-for-bit over pass_reco -> B-4 INACTIVE for this "
                  "\n    dump; R above stands. Re-check per systematic endpoint before P5B.")
        else:
            rr = wr["ratio_w_reco_over_w_truth"]
            print(f"    differs on {wr['n_pass_reco_differing']:,} pass_reco rows "
                  f"({wr['frac_pass_reco_differing']:.6f} of them)")
            print(f"    w_reco/w_truth  min={rr['min']:.6g}  median={rr['median']:.6g}  "
                  f"max={rr['max']:.6g}  (w_truth==0 on {rr['n_w_truth_zero']:,} rows)")
            print(f"    R with w_reco denominator   = "
                  f"{wr['R_pot_scaled_wreco_denominator']:.6f}")
            print(f"    -> B-4 is ACTIVE. Fixing the reco leg moves R by "
                  f"{wr['R_shift_factor_if_B4_fixed']:.6f}; resolve B-4 BEFORE freezing R.")

    if "subsample" in rep:
        s = rep["subsample"]
        print(f"\n  if normalize=False at max_events={s['max_events']:,}:")
        print(f"    approx class ratio          = {s['class_ratio_if_normalize_false']:.6f} "
              f"(row fraction {s['row_fraction_of_full_inventory']:.6f})")
        print(f"    -> {s['interpretation']}")

    print("\n  NOTE: R alone does not size the bias. Per omnifold.py:185 the off-acceptance "
          "\n  weights are pinned at 1 in both the correct and the normalized run, so the "
          "\n  per-bin distortion is 1 + a(bin)*(R-1) -- acceptance-dependent, NOT a global "
          "\n  scalar. Do not 'correct' a published result by multiplying by R.\n")

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(rep, fh, indent=2, sort_keys=True)
        print(f"  wrote {args.json_out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
