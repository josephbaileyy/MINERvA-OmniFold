#!/usr/bin/env python3
"""RE-1 report 2: the per-cell C2/D2 table and the SE-based counts, from the declared 2D readout.

    re1_c2_cells.py --readout readout_2d_full.json --cov production_cov.npz --q s5_plus_playlist.npz \
        --expect-readout-sha256 S --expect-cov-sha256 S --expect-q-sha256 S --tsv cells.tsv --out counts.json

Arithmetic on the readout only, no unfold:

* the TSV: for each of the 205 cells, its bin edges and E_U value, sigma_stat and sigma_total as a percent of E_U,
  each arm's mean residual and the arm difference (with its SE) in sigma_stat, the difference in sigma_total, and
  D2's per-cell z in both sigmas;
* the JSON: for each arm and for the arm difference, how many cells lie beyond 2 and 3 of their own SE (mean / SE
  over the 20 seeds), the significance a reader of a 20-seed mean needs next to the sigma_stat yardstick.

MEASURES: descriptive numbers. CANNOT AUTHORIZE: a verdict; the declared one is the readout's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "2d-unfolding"))


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def cells_table(o: dict, cov, q, pt, pz) -> list[str]:
    ss, st, x = np.sqrt(np.diag(cov["stat"])), np.sqrt(np.diag(q["total_plus_C_PL"])), cov["cells_x_EU"]
    c, d2 = o["c2"], {r["globalid"]: r for r in o["d2"]["per_cell"]}
    rows = ["globalid\tix\tiy\tpt_lo\tpt_hi\tpz_lo\tpz_hi\tx_EU\tsigma_stat_rel_pct\tsigma_total_rel_pct\t"
            "purity_resid_stat\trefined_resid_stat\tdiff_stat\tdiff_se_stat\tdiff_total\td2_z_stat\td2_z_total"]
    for i, g in enumerate(sorted(d2)):
        ix, iy = divmod(g, 16)
        pr = c["purity"]["per_cell_mean_residual"][i] / ss[i]
        rr = c["refined"]["per_cell_mean_residual"][i] / ss[i]
        dd, dse = c["arm_difference"]["per_cell_mean"][i], c["arm_difference"]["per_cell_se"][i]
        rows.append("\t".join(map(str, [g, ix, iy, pt[ix], pt[ix + 1], pz[iy], pz[iy + 1], "%.6e" % x[i],
                                        "%.3f" % (100 * ss[i] / x[i]), "%.3f" % (100 * st[i] / x[i]), "%.4f" % pr,
                                        "%.4f" % rr, "%.4f" % (dd / ss[i]), "%.4f" % (dse / ss[i]),
                                        "%.4f" % (dd / st[i]), "%.4f" % d2[g]["z_stat"], "%.4f" % d2[g]["z_total"]])))
    return rows


def se_counts(o: dict) -> dict:
    c = o["c2"]
    out = {}
    for name, m, s in (("purity", c["purity"]["per_cell_mean_residual"], c["purity"]["per_cell_se"]),
                       ("refined", c["refined"]["per_cell_mean_residual"], c["refined"]["per_cell_se"]),
                       ("arm_difference", c["arm_difference"]["per_cell_mean"], c["arm_difference"]["per_cell_se"])):
        t = np.asarray(m) / np.asarray(s)
        out[name] = {"n_cells": int(t.size), "n_over_2_se": int((np.abs(t) > 2).sum()),
                     "n_over_3_se": int((np.abs(t) > 3).sum()), "max_abs_t": float(np.abs(t).max()),
                     "expected_over_2_se_if_null": float(t.size * 0.0455)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("readout", "cov", "q"):
        ap.add_argument(f"--{k}", type=Path, required=True)
        ap.add_argument(f"--expect-{k}-sha256", required=True)
    ap.add_argument("--tsv", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    for k in ("readout", "cov", "q"):
        if sha256_path(getattr(a, k)) != getattr(a, f"expect_{k}_sha256"):
            print(f"--{k} digest differs", file=sys.stderr)
            return 4
    import unfold_2d_omnifold_unbinned as u2d
    o = json.loads(a.readout.read_text())
    a.tsv.write_text("\n".join(cells_table(o, np.load(a.cov), np.load(a.q), u2d.PT_EDGES, u2d.PZ_EDGES)) + "\n")
    out = {"schema": "re1-c2-cells/1", "readout_sha256": a.expect_readout_sha256, "se_counts": se_counts(o),
           "tsv_sha256": sha256_path(a.tsv), "code_sha256": sha256_path(Path(__file__).resolve())}
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out["se_counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
