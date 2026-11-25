#!/usr/bin/env python3
"""regenA amendment A5's control C5-LIT: OLD's readout reproduces every literal appC_supplementary.tex:7 and
records_r03_twod.tex:18 print, at their printed rounding.  a5_literals.py <readout_old.json>"""
import json, math, sys
o = json.load(open(sys.argv[1])); sp = o["six_split"]
sig1 = lambda x: float(f"{x:.0e}")   # one significant figure, as "4x10^-9" prints
checks = {
    "9.6% (ten smallest-lambda modes' share)": f"{100 * o['share10_smallest']:.1f}" == "9.6",
    "two of the five largest in the smallest-lambda tenth": o["top5_in_smallest_tenth"] == 2,
    "three of the six leading at the highest p_par": len(sp["high_pz"]) == 3 and len(sp["lower_pz"]) == 3,
    "those three: lambda/lambda_max <~ 4e-9 (each <= 4e-9 at one significant figure)": all(sig1(x) <= 4e-9 for x in sp["high_pz_lam_rel"]),
    "the other three: lambda/lambda_max between 4e-6 and 6e-5 (one significant figure)": all(4e-6 <= sig1(x) <= 6e-5 for x in sp["lower_pz_lam_rel"])
        and sig1(min(sp["lower_pz_lam_rel"])) == 4e-6 and sig1(max(sp["lower_pz_lam_rel"])) == 6e-5,
    "largest standardized component 4.7": f"{o['largest_abs_z']:.1f}" == "4.7",
    "the next nine 3.4-3.8": f"{min(o['next_nine_abs_z']):.1f}" == "3.4" and f"{max(o['next_nine_abs_z']):.1f}" == "3.8",
}
for k, v in checks.items(): print(("PASS " if v else "FAIL ") + k)
print("C5-LIT ::", "PASS" if all(checks.values()) else "FAIL"); sys.exit(0 if all(checks.values()) else 1)
