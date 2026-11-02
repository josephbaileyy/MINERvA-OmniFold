"""Group-level additivity of I2's modes, from committed readouts only (audit R1 on #650).

Reads ``i2.json`` (this directory) and ``../../diag/diag.json`` and writes ``group_additivity.json``.
No product is opened. Per interaction band b and cell c:

- M_b = M * share_s1_b / sum over interaction bands of share_s1, and E_b likewise from share_toys;
- A_b = (A/M)_b^2 M_b, B_b = (B/E)_b^2 E_b, C_b = (C/A)_b^2 A_b, res_b = (residual/A)_b^2 A_b,
  since i2.json's per-band ratios are sigma ratios (fd_1b_diag.ratio takes the square root).

The script refuses unless sum_b A_b, B_b and C_b rebuild the readout's A, B and C. Signs come from the
pair estimator's rank-one blocks: a pair band's diagonal entry is d^2 with d = (s+ - s-)/2, so
|d_A|, |d_B|, |d_C| and |d_A - d_B - d_C| fix the relative signs of d_B and d_C against d_A.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
I2 = HERE / "i2.json"
DIAG = HERE.parents[1] / "diag" / "diag.json"
OUT = HERE / "group_additivity.json"
REBUILD_TOL = 1e-12
SIGN_TOL = 1e-9


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sq(x) -> float:
    """A sigma ratio back to a block ratio; None means both blocks are zero."""
    if x is None:
        return 0.0
    if isinstance(x, str):
        raise SystemExit(f"REFUSE: ratio {x!r} cannot be rebuilt (zero S1-side block, non-zero other side)")
    return float(x) ** 2


def summary(v: list[float]) -> dict:
    return {"median": statistics.median(v), "min": min(v), "max": max(v), "above_1": sum(x > 1 for x in v)}


def main() -> int:
    i2, diag = json.loads(I2.read_text()), json.loads(DIAG.read_text())
    cells, bands = i2["cells"], list(i2["per_band"])
    if diag["cells"] != cells:
        raise SystemExit("REFUSE: diag.json and i2.json name different cells")
    n = len(cells)
    blocks = {k: {} for k in ("M", "E", "A", "B", "C", "res")}
    for b in bands:
        pb = i2["per_band"][b]
        for c in range(n):
            s1 = sum(diag["per_band"][x]["share_s1"][c] for x in bands)
            st = sum(diag["per_band"][x]["share_toys"][c] for x in bands)
            M_b = i2["M"][c] * diag["per_band"][b]["share_s1"][c] / s1
            E_b = i2["E"][c] * diag["per_band"][b]["share_toys"][c] / st
            A_b = sq(pb["A_over_M"][c]) * M_b
            blocks["M"][b, c], blocks["E"][b, c], blocks["A"][b, c] = M_b, E_b, A_b
            blocks["B"][b, c] = sq(pb["B_over_E"][c]) * E_b
            blocks["C"][b, c] = sq(pb["C_over_A"][c]) * A_b
            blocks["res"][b, c] = sq(pb["residual_over_A"][c]) * A_b
    rebuild = {}
    for k in ("A", "B", "C"):
        rel = [abs(sum(blocks[k][b, c] for b in bands) / i2[k][c] - 1) for c in range(n)]
        rebuild[k] = max(rel)
        if rebuild[k] > REBUILD_TOL:
            raise SystemExit(f"REFUSE: sum of per-band {k} misses the readout by {rebuild[k]:.2e}")
    res = [sum(blocks["res"][b, c] for b in bands) for c in range(n)]
    over_A = [math.sqrt(res[c] / i2["A"][c]) for c in range(n)]
    over_B = [math.sqrt(res[c] / i2["B"][c]) for c in range(n)]

    pairs = [b for b in bands if len(i2["per_band"][b]["corr_sD_minus_sB"]) == 2]
    left_out = [b for b in bands if b not in pairs]
    fit_worst, ambiguous, chosen = 0.0, 0, {}
    sums = {k: [0.0] * n for k in ("A_minus_C", "A_minus_B", "A_minus_B_minus_C", "A")}
    for b in pairs:
        for c in range(n):
            a, bb, cc, r = (math.sqrt(blocks[k][b, c]) for k in ("A", "B", "C", "res"))
            scale = max(a, bb, cc, r, 1e-300)
            fits = sorted((abs(abs(a - sB * bb - sC * cc) - r) / scale, sB, sC)
                          for sB, sC in itertools.product((1, -1), repeat=2))
            err, sB, sC = fits[0]
            fit_worst = max(fit_worst, err)
            if fits[1][0] <= SIGN_TOL:
                ambiguous += 1
            chosen[(sB, sC)] = chosen.get((sB, sC), 0) + 1
            sums["A"][c] += a * a
            sums["A_minus_C"][c] += (a - sC * cc) ** 2
            sums["A_minus_B"][c] += (a - sB * bb) ** 2
            sums["A_minus_B_minus_C"][c] += (a - sB * bb - sC * cc) ** 2
    left_share = [sum(blocks["A"][b, c] for b in left_out) / i2["A"][c] for c in range(n)]
    signed = {k: [math.sqrt(sums[k][c] / sums["A"][c]) for c in range(n)]
              for k in ("A_minus_C", "A_minus_B", "A_minus_B_minus_C")}
    out = {
        "schema": "fd-1b-inv-group-additivity/1",
        "label": "DERIVATION (arithmetic on committed readouts)",
        "inputs": {"i2.json": sha256(I2), "diag.json": sha256(DIAG)},
        "cells": cells,
        "rebuild_max_rel_error": rebuild,
        "group_residual_sigma_over_A": dict(zip(cells, over_A)),
        "group_residual_sigma_over_B": dict(zip(cells, over_B)),
        "summary": {"over_A": summary(over_A), "over_B": summary(over_B)},
        "signed_pairs": {
            "bands": len(pairs), "band_cells": len(pairs) * n, "left_out": left_out,
            "left_out_share_of_A_max": max(left_share),
            "fit_worst_rel": fit_worst, "ambiguous_band_cells": ambiguous,
            "sign_choice_counts": {f"sB={k[0]:+d},sC={k[1]:+d}": v for k, v in sorted(chosen.items())},
            "per_cell": {k: dict(zip(cells, v)) for k, v in signed.items()},
            "summary": {k: summary(v) for k, v in signed.items()},
        },
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"out": OUT.name, "over_A": out["summary"]["over_A"], "over_B": out["summary"]["over_B"],
                      "signed": out["signed_pairs"]["summary"], "fit_worst": fit_worst,
                      "ambiguous": ambiguous, "rebuild": rebuild}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
