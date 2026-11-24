"""S2R's pass rule, fixed before the run (S2R-DECLARATION.md section 3).

PASS only if, at k = 5 on the noise-free split-991000 pseudo-data with background:
  rho_S2R <= rho_B0 - BAR at BOTH A7_gibuu and q3 (rho_B0 from the same job, C-PAIR'd to FD-PRR's B0), and
  the nominal truth is not flagged under its F0b grade matrix.
An undefined rho at either truth, or either arm, is a FAIL. Nothing here is tuned on the output.
"""
from __future__ import annotations

BAR = 0.05  # prr-floor: the improvement bar FD-PRR and T3 declared (prr_read.BAR_FLOOR, t3p_read.BAR_FLOOR)
TRUTHS = ("A7_gibuu", "q3")


def verdict(rho_s2r: dict, rho_b0: dict, nominal_flagged: bool) -> dict:
    per = {}
    ok = not bool(nominal_flagged)
    for t in TRUTHS:
        a, b = rho_s2r.get(t), rho_b0.get(t)
        if a is None or b is None:
            per[t] = {"rho_S2R": a, "rho_B0": b, "delta": None, "clears": False}
            ok = False
            continue
        d = float(a) - float(b)
        clears = bool(float(a) <= float(b) - BAR)
        per[t] = {"rho_S2R": float(a), "rho_B0": float(b), "delta": d, "clears": clears}
        ok = ok and clears
    return {"verdict": "PASS" if ok else "FAIL", "bar": BAR, "per_truth": per,
            "nominal_flagged": bool(nominal_flagged)}
