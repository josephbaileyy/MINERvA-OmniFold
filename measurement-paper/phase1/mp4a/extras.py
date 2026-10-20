#!/usr/bin/env python3
"""MP4-A descriptive extras (run only after the verdict; nothing here enters the PASS rule).

(a) the share of the nominal truth inside acceptance holes (zero-efficiency T2 cells), overall and per
    reported hole functional;
(b) grid T3: the size of the problem and a measured cost of one inner solve, to decide tractability;
    the T3 Cramer-Rao widths (D-ID's widths_from_eig) when the eigendecomposition is affordable;
(c) the Cramer-Rao width at grid T2 with the reco binning refined 2x per axis (every reco bin split at
    its midpoint), through D-ID's fisher() and widths_from_eig(), against the T2 nominal widths.
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.optimize import lsq_linear
from scipy.stats import chi2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_problem  # noqa: E402
import osb  # noqa: E402
import run_mp4a  # noqa: E402

PSI2 = float(chi2.ppf(0.6827, 1))


def csr(z, key):
    return sparse.csr_matrix((z[f"{key}/R_data"], z[f"{key}/R_indices"], z[f"{key}/R_indptr"]),
                             shape=tuple(z[f"{key}/R_shape"]))


def cpu():
    a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def widths(did, r, t, b, maps):
    f = did.fisher(r, t, b)
    values, vectors = np.linalg.eigh(f)
    sigma, null = did.widths_from_eig(values, vectors, maps)
    value = maps @ t
    return sigma / np.abs(value), null, {"eig_max": float(values.max()),
                                         "n_null": int(np.sum(values <= 1e-12 * values.max()))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--operands", type=Path, required=True)
    ap.add_argument("--t3", choices=("probe", "widths", "skip"), default="probe")
    a = ap.parse_args(argv)
    did = build_problem.load_did()
    dec = json.loads((run_mp4a.OUT / "DECLARATION.json").read_text())
    if build_problem.sha256(a.operands) != dec["inputs"]["operands_sha256"]:
        raise SystemExit("operands digest differs")
    z = np.load(a.operands)
    rows = run_mp4a.reported_rows(z, groups=("J", "H2"))
    out = {"schema": "mp4a-extras/1", "label": "DESCRIPTIVE: not part of the PASS rule",
           "extras_sha256": build_problem.sha256(Path(__file__).resolve())}
    c0, w0 = cpu(), time.time()
    # (a)
    t, eff, h_all = z["T2/t"], z["T2/eff"], z["T2/H"]
    hole = eff <= 0
    per = []
    for row in rows:
        h = h_all[row["row185"]]
        if np.any(h[hole] != 0):
            per.append({**row, "share_of_nominal_in_zero_eff_cells": float((h[hole] @ t[hole]) / (h @ t))})
    out["a_hole_truth_share"] = {
        "n_zero_eff_cells_T2": int(hole.sum()), "n_T2_cells": int(t.size),
        "share_of_total_T2_nominal_truth_counts": float(t[hole].sum() / t.sum()),
        "share_of_J_total": None, "per_hole_functional": per}
    jsel = [r["row185"] for r in rows if r["group"] == "J"]
    hj = h_all[jsel].sum(axis=0)
    out["a_hole_truth_share"]["share_of_J_total"] = float((hj[hole] @ t[hole]) / (hj @ t))
    # (c)
    r2 = csr(z, "T2")
    rx = csr(z, "R2X")
    maps = h_all[[r["row185"] for r in rows]]
    s_nom, null_nom, i_nom = widths(did, r2, t, z["T2/b"], maps)
    s_ref, null_ref, i_ref = widths(did, rx, t, z["R2X/b"], maps)
    grp = np.array([r["group"] for r in rows])
    out["c_refined_reco_cr"] = {"n_reco_cells_T2": int(r2.shape[0]), "n_reco_cells_refined": int(rx.shape[0]),
                                "info_nominal": i_nom, "info_refined": i_ref,
                                "radius": "unit (Cramer-Rao sigma, D-ID convention)"}
    for g in ("J", "H2"):
        m = grp == g
        ratio = s_ref[m] / s_nom[m]
        out["c_refined_reco_cr"][g] = {"nominal_T2": run_mp4a.stats(s_nom[m]), "refined_reco_T2": run_mp4a.stats(s_ref[m]),
                                       "ratio_refined_over_nominal_finite": run_mp4a.stats(ratio[np.isfinite(ratio)]),
                                       "psi_scaled_refined_median": float(np.sqrt(PSI2)) * run_mp4a.quantile_inf(s_ref[m], 0.5)}
    out["c_rows"] = [{**r, "sigma_rel_T2": float(s_nom[i]), "sigma_rel_T2_refined_reco": float(s_ref[i])}
                     for i, r in enumerate(rows)]
    # (b)
    if a.t3 != "skip":
        r3, t3, b3 = csr(z, "T3"), z["T3/t"], z["T3/b"]
        info = {"n_cells": int(t3.size), "dense_fisher_bytes": int(8 * t3.size**2)}
        c1 = cpu()
        f3 = did.fisher(r3, t3, b3)
        info["fisher_cpu_s"] = cpu() - c1
        c1 = cpu()
        values, vectors = np.linalg.eigh(f3)
        info["eigh_cpu_s"] = cpu() - c1
        del f3
        maps3 = z["T3/H"][[r["row185"] for r in rows]]
        sigma, null = did.widths_from_eig(values, vectors, maps3)
        s3 = sigma / np.abs(maps3 @ t3)
        for g in ("J", "H2"):
            info[f"cr_{g}"] = run_mp4a.stats(s3[grp == g])
        if a.t3 == "probe":
            pos = values > 1e-12 * values.max()
            sq = np.sqrt(values[pos])
            j0 = int(np.flatnonzero((grp == "J") & np.isfinite(s3))[0])
            u = (vectors[:, pos].T @ maps3[j0]) / sq
            gm = sq[:, None] * vectors[:, pos].T
            del vectors
            c1 = cpu()
            res = lsq_linear(gm, -np.sqrt(PSI2) / np.linalg.norm(u) * u, bounds=(-t3, np.inf), method="bvls",
                             tol=1e-12)
            info["probe_functional"] = rows[j0]["name"]
            info["one_inner_bvls_cpu_s"] = cpu() - c1
            info["one_inner_bvls_status_nit"] = [int(res.status), int(res.nit)]
        out["b_T3"] = info
    out["resources"] = {"cpu_s": cpu() - c0, "wall_s": time.time() - w0,
                        "peak_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}
    (run_mp4a.OUT / "extras.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("c_rows",)}, indent=1, default=float)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
