#!/usr/bin/env python3
"""Verify, from the operands, what each s5n truth departure does (contract controls C4 and C5).

For each declared truth reweight r of the full signal MC it reports, over pass_truth rows inside the
5D grid (the rows np.histogramdd keeps): the ratio of the reweighted to the nominal w_truth-weighted
total; the reweighted/nominal ratio of every (E_avail, W) M1 functional of the analysis's own
projection (the s5c reported functionals' first 43 rows, cross sections through the analysis
extraction); the per-E_avail-bin ratio; and, for the q3 deformation, the spread of r inside each
(E_avail, W) cell. A departure claimed to preserve a marginal is checked against it numerically.

MEASURES: the truth-level size and shape of each declared departure. CANNOT AUTHORIZE: anything about
the estimator's response to it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_coverage  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402


def xsec(inputs: dict, weights: np.ndarray) -> np.ndarray:
    m = inputs["pass_truth"]
    gen = inputs["MCgen"][m]
    unf, _ = np.histogramdd(gen, bins=inputs["edges"], weights=inputs["w_truth"][m] * weights[m])
    ofin, _ = np.histogramdd(gen, bins=inputs["edges"], weights=inputs["w_truth"][m])
    dn = inputs["denom_nd"]
    comp = np.zeros_like(ofin)
    comp[dn > 0] = ofin[dn > 0] / dn[dn > 0]
    xs, _ = extract_cross_section_nd(unf, comp, inputs["flux"], float(inputs["data_pot"]),
                                     float(inputs["n_nucleons"]), inputs["edges"])
    return xs.ravel(order="C")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True, help="for the reported functionals")
    ap.add_argument("--eavail-ratio", type=Path, required=True)
    ap.add_argument("--eavail-amplitude", type=float, required=True)
    ap.add_argument("--q3-amplitude", type=float, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    if s5c_unfold.sha256_path(a.npz) != a.expect_npz_sha256:
        raise SystemExit("input digest differs")
    inputs = s5c_unfold.load_inputs(a.npz)
    ratio = json.loads(a.eavail_ratio.read_text())
    U, names = s5c_coverage.reported_functionals(json.loads(a.s5c_contract.read_text()))
    M1 = U[:43]
    edges = inputs["edges"]
    gen = inputs["MCgen"]
    ok = inputs["pass_truth"].copy()
    for k, e in enumerate(edges):
        ok &= (gen[:, k] >= e[0]) & (gen[:, k] <= e[-1])
    w = inputs["w_truth"]
    nominal = xsec(inputs, np.ones(gen.shape[0]))
    f0 = M1 @ nominal
    e_edges = np.asarray(edges[2], float)
    ie = np.clip(np.searchsorted(e_edges, gen[:, 2], side="right") - 1, 0, e_edges.size - 2)
    iw = np.clip(np.searchsorted(np.asarray(edges[4], float), gen[:, 4], side="right") - 1, 0, len(edges[4]) - 2)
    out = {"schema": "s5n-truth-check/1", "input_npz_sha256": a.expect_npz_sha256,
           "eavail_ratio_sha256": s5c_unfold.sha256_path(a.eavail_ratio),
           "code_sha256": {"s5n_truth_check.py": s5c_unfold.sha256_path(Path(__file__).resolve()),
                           "s5n_pseudo.py": s5c_unfold.sha256_path(_ND / "s5n_pseudo.py")},
           "rows_in_grid": int(ok.sum()), "departures": {}}
    for name, amp in (("eavail_shape", a.eavail_amplitude), ("q3_given_eavail_w", a.q3_amplitude)):
        r = s5n_pseudo.truth_weight(name, inputs, amp, ratio)
        f = M1 @ xsec(inputs, r)
        rel = f / f0
        per_e = np.array([(w[ok & (ie == k)] * r[ok & (ie == k)]).sum() / w[ok & (ie == k)].sum()
                          for k in range(e_edges.size - 1)])
        rec = {"amplitude": amp,
               "in_grid_total_ratio": float((w[ok] * r[ok]).sum() / w[ok].sum()),
               "r_min": float(r[ok].min()), "r_max": float(r[ok].max()),
               "rows_outside_grid_with_r_not_1": int(np.sum(r[~ok & inputs["pass_truth"]] != 1.0)),
               "M1_ratio_min": float(rel.min()), "M1_ratio_max": float(rel.max()),
               "M1_ratio_max_abs_dev": float(np.max(np.abs(rel - 1.0))),
               "M1_ratio": rel.tolist(), "per_eavail_bin_ratio": per_e.tolist()}
        cell = ie * (len(edges[4]) - 1) + iw
        nw = np.bincount(cell[ok], weights=w[ok])
        rw = np.bincount(cell[ok], weights=(w * r)[ok])
        pos = nw > 0
        rec["weight_marginal_EW_ratio_max_abs_dev"] = float(np.max(np.abs(rw[pos] / nw[pos] - 1.0)))
        if name == "q3_given_eavail_w":
            spread = []
            for c in np.unique(cell[ok]):
                sel = ok & (cell == c)
                ww = w[sel]
                mu = (ww * r[sel]).sum() / ww.sum()
                spread.append(float(np.sqrt((ww * (r[sel] - mu) ** 2).sum() / ww.sum())))
            rec["in_cell_r_std_min"], rec["in_cell_r_std_median"], rec["in_cell_r_std_max"] = (
                float(np.min(spread)), float(np.median(spread)), float(np.max(spread)))
            rec["weight_marginal_preserved_1e-6"] = bool(rec["weight_marginal_EW_ratio_max_abs_dev"] <= 1e-6)
            rec["M1_xsec_preserved_1e-6"] = bool(rec["M1_ratio_max_abs_dev"] <= 1e-6)
        out["departures"][name] = rec
        print(json.dumps({k: v for k, v in rec.items() if not isinstance(v, list)}))
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
