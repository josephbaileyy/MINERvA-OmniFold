"""Apply dev/FINALIST_RULE-20260926.md mechanically to a DEV_TABLES json (dev/summarize_dev.py).

Screens: S-U1 development tilt >= 0.60, S-U3 D1 -0.35 >= 0.50, S-U4 D4c topology >= 0.25,
S-B2 D4d E_avail residual <= 0.021; K* = the smallest passing k whose development-tilt recovery is
within 0.02 of the best passing k. A k with any screen missing is `incomplete`.

    python apply_finalist_rule.py DEV_TABLES.json SCREENS.json
"""
from __future__ import annotations

import json
import sys

SCREENS = {"S-U1": ("dev tilt R (F reps)", ">=", 0.60), "S-U3": ("D1 -0.35 R", ">=", 0.50),
           "S-U4": ("D4c topo (E x p) R", ">=", 0.25), "S-B2": ("D4d E_avail res L1", "<=", 0.021)}
KS = (2, 3, 4, 5, 6)


def apply(tab: dict) -> dict:
    cands = sorted({c for lab, _, _ in SCREENS.values() for c in tab.get(lab, {})})
    out = {}
    for c in cands:
        rows = []
        for k in KS:
            vals = {}
            for s, (lab, _, _) in SCREENS.items():
                cell = tab.get(lab, {}).get(c, {}).get(str(k), {})
                vals[s] = (cell.get("mean"), cell.get("n", 0))
            if any(v[0] is None for v in vals.values()):
                rows.append({"k": k, "status": "incomplete", "values": vals})
                continue
            ok = all((vals[s][0] >= th) if op == ">=" else (vals[s][0] <= th)
                     for s, (_, op, th) in SCREENS.items())
            rows.append({"k": k, "status": "PASS" if ok else "fail", "values": vals})
        passing = {r["k"]: r["values"]["S-U1"][0] for r in rows if r["status"] == "PASS"}
        kstar = None
        if passing:
            best = max(passing.values())
            kstar = min(k for k, u in passing.items() if u >= best - 0.02)
        out[c] = {"rows": rows, "Kstar": kstar, "dev_tilt_at_Kstar": passing.get(kstar)}
    return out


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    res = apply(json.load(open(argv[0])))
    json.dump(res, open(argv[1], "w"), indent=1)
    for c, r in res.items():
        print(c, "K*", r["Kstar"], "dev", r["dev_tilt_at_Kstar"],
              " ".join(f"k{x['k']}:{x['status']}" for x in r["rows"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
