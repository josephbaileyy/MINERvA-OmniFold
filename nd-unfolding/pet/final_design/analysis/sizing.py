"""The section-8 sizing rule (PROTOCOL-20260925, stage S3p).

`n_F` = the smallest n giving 80 % power for every declared contrast -- each section-6.5
non-inferiority contrast (paired small - large differences against its margin) and U1 (R_E0
against the adequacy floor) -- with true value = the pilot mean and sd = the pilot sd's 80 % upper
confidence bound, at one-sided alpha Bonferroni-split over the declared contrasts (and halved per
look when the two-look sequential rule is planned, `looks_planned = 2`: look 1 decides at alpha/2);
floor 24, cap 60.

Power of the one-sided t test that rejects `mean <= margin` when the lower bound exceeds the
margin, at true mean mu and sd sigma: `1 - nct.cdf(t_{1-alpha, n-1}, n - 1, (mu - margin) sqrt(n)
/ sigma)`. The search is exact (every n from 2 upward). A contrast whose required n exceeds the
cap is reported with its uncapped n (searched to `SEARCH_LIMIT`) or as UNATTAINABLE (pilot mean
at or below its margin, or no n <= SEARCH_LIMIT); `n_F` is then the cap and `capped` is true --
never a silent search bound.

    python sizing.py --pilot pilot.json --out sizing.json

pilot.json: {"contrasts": [{"id": ..., "values": [per-replicate ...], "margin": m}, ...],
             "bonferroni_m": optional (default: number of contrasts), "looks_planned": 2}
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inference as inf  # noqa: E402

POWER = 0.80
FLOOR, CAP = 24, 60
SEARCH_LIMIT = 100_000


def power(n: np.ndarray, mu: float, margin: float, sigma: float, alpha: float) -> np.ndarray:
    n = np.asarray(n, dtype=np.float64)
    df = n - 1
    crit = stats.t.ppf(1.0 - alpha, df)
    return 1.0 - stats.nct.cdf(crit, df, (mu - margin) * np.sqrt(n) / sigma)


def smallest_n(mu: float, margin: float, sigma: float, alpha: float, target: float = POWER,
               limit: int = SEARCH_LIMIT) -> int | None:
    """Exact smallest n >= 2 with power >= target, or None if none <= limit."""
    if sigma <= 0:
        return 2 if mu > margin else None
    if mu <= margin:
        return None
    lo = 2
    for hi in sorted({min(h, limit) for h in (100, 1_000, 10_000, limit)}):
        if hi < lo:
            continue
        n = np.arange(lo, hi + 1)
        ok = np.flatnonzero(power(n, mu, margin, sigma, alpha) >= target)
        if ok.size:
            return int(n[ok[0]])
        lo = hi + 1
    return None


def size(contrasts: Sequence[Mapping[str, Any]], bonferroni_m: int | None = None,
         looks_planned: int = 2, floor: int = FLOOR, cap: int = CAP) -> dict[str, Any]:
    if not contrasts:
        raise ValueError("no declared contrasts")
    m = int(bonferroni_m or len(contrasts))
    alpha = inf.per_bound_alpha(m, looks_planned)
    rows, need = {}, []
    for c in contrasts:
        v = np.asarray(c["values"], dtype=np.float64)
        if v.size < 2:
            raise ValueError(f"{c['id']}: need >= 2 pilot values")
        sd = float(v.std(ddof=1))
        ucb = inf.ucb80_sd(sd, v.size - 1)
        # a non-inferiority contrast is sized at a true difference of min(pilot mean, 0): a noisy
        # favourable pilot mean must not shrink n (Amendment 2c; statistical review 8d9aaf8d item 6)
        kind = c.get("kind", "ni" if float(c["margin"]) <= 0 else "level")
        mu = min(float(v.mean()), 0.0) if kind == "ni" else float(v.mean())
        n = smallest_n(mu, float(c["margin"]), ucb, alpha)
        n_one_look = smallest_n(mu, float(c["margin"]), ucb, inf.per_bound_alpha(m, 1))
        rows[c["id"]] = {"n_pilot": int(v.size), "mean": float(v.mean()), "sd": sd,
                         "kind": kind, "true_value_assumed": mu,
                         "sd_ucb80": ucb, "margin": float(c["margin"]),
                         "n_for_power": n, "status": ("OK" if n is not None and n <= cap else
                                                      "EXCEEDS_CAP" if n is not None else
                                                      "UNATTAINABLE"),
                         "n_for_power_if_single_look": n_one_look}
        need.append(n)
    worst = None if any(n is None for n in need) else max(need)
    capped = worst is None or worst > cap
    n_final = cap if capped else max(floor, worst)
    powers = {k: float(power(np.array([n_final]), r["true_value_assumed"], r["margin"], r["sd_ucb80"],
                             alpha)[0]) for k, r in rows.items()}
    joint = float(np.prod(list(powers.values())))
    return {"power_at_n_F": powers,
            "joint_power_at_n_F_product": joint,
            "joint_power_note": "product of the per-contrast powers (independence); the joint power "
                                "of positively correlated contrasts is at least this",
            "alpha_one_sided_per_contrast": alpha, "bonferroni_m": m,
            "looks_planned": looks_planned, "power": POWER, "floor": floor, "cap": cap,
            "contrasts": rows, "n_required_uncapped": worst,
            "n_F": n_final, "capped": capped,
            "binding_contrasts": [k for k, r in rows.items()
                                  if r["n_for_power"] is None or r["n_for_power"] == worst]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pilot", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    p = json.loads(a.pilot.read_text())
    res = size(p["contrasts"], p.get("bonferroni_m"), int(p.get("looks_planned", 2)))
    a.out.write_text(json.dumps(res, indent=1) + "\n")
    print(f"n_F = {res['n_F']} (uncapped {res['n_required_uncapped']}, capped={res['capped']}, "
          f"alpha={res['alpha_one_sided_per_contrast']:.5f})")
    for k, r in res["contrasts"].items():
        print(f"  {k}: mean {r['mean']:+.4f} sd_ucb80 {r['sd_ucb80']:.4f} margin {r['margin']:+.4f}"
              f" -> n {r['n_for_power']} [{r['status']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
