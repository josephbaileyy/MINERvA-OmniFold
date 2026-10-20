#!/usr/bin/env python3
"""MP4-A extra (c), descriptive: Cramer-Rao widths at D-ID truth grids T1 and T2 with the reco binning
refined 2x per axis (every reco bin split in two at its midpoint), against the unrefined widths.

Everything is D-ID's code: the Builder of ``build_problem.py`` (admission checks, refined reco rows equal
to D-ID's reco rows), ``Diagnostic.problem`` for the nominal same-sample truth, response weighting and
functional rows, ``did.response`` for the refined response, ``did.fisher`` and ``did.widths_from_eig``
for the widths (unit radius, D-ID's convention). The unrefined widths are recomputed by the same path
and checked against D-ID's committed tables.npz (control).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_problem  # noqa: E402
import run_mp4a  # noqa: E402


def cr(did, r, t, b, maps):
    f = did.fisher(r, t, b)
    values, vectors = np.linalg.eigh(f)
    norms = np.linalg.norm(maps, axis=1)
    sigma = np.full(maps.shape[0], np.nan)
    ok = norms > 0
    sigma[ok], _ = did.widths_from_eig(values, vectors, maps[ok])
    value = maps @ t
    rel = np.divide(sigma, np.abs(value), out=np.full_like(sigma, np.nan), where=np.abs(value) > 0)
    return rel, {"eig_max": float(values.max()), "n_null": int(np.sum(values <= 1e-12 * values.max())),
                 "n_reco_kept": int(np.sum((r @ t + b) > 0))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    did = build_problem.load_did()
    captured = {}
    orig = did.Diagnostic.grids

    def grids(self):  # keep the Builder instance (D-ID's grids() runs unchanged)
        orig(self)
        captured["run"] = self

    did.Diagnostic.grids = grids
    rec, _ = build_problem.build(did, a.inputs)
    run = captured["run"]
    tables = np.load(run_mp4a.TABLES)
    rows = [i for i, (g, r) in enumerate(zip(run.groups, run.reported)) if r and g in ("J", "H2")]
    grp = np.asarray(run.groups)[rows]
    f_idx = np.asarray(run.f183)[rows]
    h0 = run.h["nominal"]
    out = {"schema": "mp4a-extra-c/1", "label": "DESCRIPTIVE: not part of the PASS rule",
           "extra_c_sha256": build_problem.sha256(Path(__file__).resolve()),
           "build_problem_sha256": build_problem.sha256(HERE / "build_problem.py"),
           "admission": {k: v["pass"] for k, v in rec["admission"].items()},
           "refinement": {k: v for k, v in rec["R2X"].items() if k != "edges"},
           "refined_edges": rec["R2X"]["edges"], "radius": "unit (Cramer-Rao sigma, D-ID convention)", "grids": {}}
    per = {}
    for grid in ("T1", "T2"):
        pb = run.problem(grid, "nominal", "same", "nom")
        maps = pb["maps"][f_idx]
        s_un, i_un = cr(did, pb["R"], pb["t_bin"], pb["b"], maps)
        rr = did.response(run.G[grid], run.ref["pairs"], run.ref["P"], pb["u_w"], run.ref["cells"].size)
        fold = float(np.max(np.abs(rr @ pb["t_bin"] + run.ref["b"] - run.ref["y"]) / run.ref["y"]))
        s_rf, i_rf = cr(did, rr, pb["t_bin"], run.ref["b"], maps)
        committed = tables[f"{grid}/nominal/widths_nom/sigma_rel"][np.asarray(rows)]
        ctrl = bool(np.array_equal(s_un, committed, equal_nan=True))
        fin = np.isfinite(s_un) & np.isfinite(committed)
        g_out = {"n_cells": int(run.G[grid].n_cells), "control_unrefined_equals_committed_bitwise": ctrl,
                 "control_max_rel_dev": float(np.max(np.abs(s_un[fin] / committed[fin] - 1))) if fin.any() else None,
                 "refined_fold_vs_y_max_rel": fold, "info_unrefined": i_un, "info_refined": i_rf}
        for g in ("J", "H2"):
            m = grp == g
            both = m & np.isfinite(s_un) & np.isfinite(s_rf)
            ratio = s_rf[both] / s_un[both]
            g_out[g] = {"unrefined": run_mp4a.stats(s_un[m]), "refined": run_mp4a.stats(s_rf[m]),
                        "unrefined_finite_only": run_mp4a.stats(s_un[m & np.isfinite(s_un)]),
                        "refined_finite_only": run_mp4a.stats(s_rf[m & np.isfinite(s_rf)]),
                        "ratio_refined_over_unrefined": run_mp4a.stats(ratio),
                        "median_ratio_of_medians_holes_inf": (run_mp4a.quantile_inf(s_rf[m], 0.5)
                                                              / run_mp4a.quantile_inf(s_un[m], 0.5)),
                        "n_le_10pct_unrefined": int(np.sum(s_un[m] <= 0.10)),
                        "n_le_10pct_refined": int(np.sum(s_rf[m] <= 0.10))}
        out["grids"][grid] = g_out
        per[grid] = (s_un, s_rf)
    out["rows"] = [{"group": str(grp[i]), "name": str(run.names[f_idx[i]]),
                    **{f"{gr}_{k}": float(v[i]) for gr, (su, sr) in per.items() for k, v in (("unrefined", su), ("refined", sr))}}
                   for i in range(len(rows))]
    out["resources"] = {"cpu_s": run_mp4a.cpu_all(), "wall_s": time.time() - t0, "peak_rss_bytes": run_mp4a.rss()}
    a.out.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "refined_edges")}, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
