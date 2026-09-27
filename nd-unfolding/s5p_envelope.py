#!/usr/bin/env python3
"""s5p Stage 2 supplement: the study-P envelope h and the vertex linearity, as a receipt (review round 1, LOW).

The Stage-2 exit record quotes h_f = max_k |shift_k,f| over the vertices D1-D5 (the data unfold with the prior
reweighted to vertex k, relative to the CV-prior data unfold) per reported cell, but no receipt held it. This
tool recomputes it from the same products with the Stage-2 analyzer's own cell maps and loaders, and adds:

* h without D1 (the GiBUU/GENIE vertex, contaminated by ``KNOWN_ISSUES.md`` 83 through the GENIE prediction);
* per vertex with a measured bias (D1, D2, D4 from the noise-free asimov traces; D3 from the s5e pseudo
  ensemble): per-cell |shift + bias| / |bias| (median over cells with |bias| > 1%) and the fraction of reported
  cells where |shift| >= |bias| (how far h is from a per-cell bias bound).

MEASURES: the envelope and the linearity diagnostics. CANNOT AUTHORIZE: an interval, a component or any
disposition; amendment 4 applied the frozen rules, and the repair amendment records this receipt beside it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import s5p_stage2_analyze as s2

VERTICES = ("d1", "d2", "d3", "d4", "d5")


def shifts(runs: Path, cells: s2.Cells) -> dict:
    pdir = runs / "s2/prior"
    c0 = cells.of(s2.load(pdir / "prior_R5fix_CV.npz")["xsec_flat"])
    out = {}
    for k in VERTICES:
        ck = cells.of(s2.load(pdir / f"prior_R5fix_prior_{k}.npz")["xsec_flat"])
        out[k] = {P: np.where(c0[P] > 0, ck[P] / np.where(c0[P] > 0, c0[P], 1) - 1.0, 0.0) for P in cells.maps}
    return out


def biases(runs: Path, s5e: Path, cells: s2.Cells) -> dict:
    conv = runs / "s2/conv"
    src = {"d1": ("asimov", conv / "k_b0_gibuu.npz"), "d2": ("asimov", conv / "k_b0_w1.npz"),
           "d4": ("asimov", conv / "k_b0_w3.npz"), "d3": ("pseudo", s5e / "cand/assess/W2")}
    out, used = {}, {}
    names_from = s2.load(conv / "k_b0_w3.npz")  # a completed trace: the functional list is the same for all
    for k, (kind, path) in src.items():
        if kind == "asimov":
            if not path.exists():  # a trace still running: its checkpoint holds iterations 1..k >= 5, no meta
                path = path.with_name(path.name + ".partial.npz")
                z = np.load(path, allow_pickle=False)
                # fn_true_A == fn_true for asimov_same (checked on k_b0_w3 and k_cap10_w3: equal on every nonzero cell)
                p = {"fn_push": np.asarray(z["fn_push"]), "fn_true": np.asarray(z["fn_true_A"]), "meta": names_from["meta"]}
            else:
                p = s2.load(path)
            rows = s2.trace_functionals(p)
            out[k] = {P: p["fn_push"][4][idx] / p["fn_true"][idx] - 1.0 for P, idx in rows.items()}
        else:
            rel, _, _ = s2.ensemble(sorted(path.glob("*.npz")), cells)
            out[k] = {P: rel[P].mean(0) for P in rel}
        used[k] = {"kind": kind, "path": str(path), "sha256": None if path.is_dir() else s2.sha256(path)}
    return out, used


def envelope(sh: dict, cells: s2.Cells, use: tuple) -> dict:
    out = {}
    for P in cells.maps:
        m = cells.reported[P]
        a = np.array([np.abs(sh[k][P]) for k in use])
        h = a.max(0)
        dom = np.asarray(use)[a.argmax(0)]
        out[P] = {"n_reported": int(m.sum()), "h_median_pct": 100 * float(np.median(h[m])),
                  "h_p90_pct": 100 * float(np.quantile(h[m], 0.9)),
                  "dominant_vertex_counts": {k: int(np.sum(dom[m] == k)) for k in use},
                  "h_pct_per_reported_cell": (100 * h[m]).tolist()}
    return out


def linearity(sh: dict, bi: dict, cells: s2.Cells) -> dict:
    out = {}
    for k, b in bi.items():
        out[k] = {}
        for P in cells.maps:
            m = cells.reported[P]
            s, bb = sh[k][P][m], b[P][m]
            big = np.abs(bb) > 0.01
            out[k][P] = {"median_abs_shift_plus_bias_over_abs_bias": float(np.median(np.abs(s[big] + bb[big]) / np.abs(bb[big]))) if big.any() else None,
                         "n_cells_bias_gt_1pct": int(big.sum()),
                         "fraction_abs_shift_ge_abs_bias": float(np.mean(np.abs(s) >= np.abs(bb))),
                         "corr_shift_vs_minus_bias": float(np.corrcoef(-bb, s)[0, 1]),
                         "slope_shift_on_minus_bias": float(np.dot(-bb, s) / np.dot(bb, bb))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--s5e-runs", type=Path, required=True)
    ap.add_argument("--stage1", type=Path, required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    cells = s2.Cells(json.loads(a.stage1.read_text()), json.loads(a.s5c_contract.read_text()))
    sh = shifts(a.runs, cells)
    bi, bias_sources = biases(a.runs, a.s5e_runs, cells)
    products = [a.runs / "s2/prior" / f"prior_R5fix_{t}.npz" for t in ("CV",) + tuple(f"prior_{k}" for k in VERTICES)]
    receipt = {"schema": "s5p-envelope-receipt/1", "stage1_sha256": s2.sha256(a.stage1),
               "code_sha256": {"s5p_envelope.py": s2.sha256(Path(__file__).resolve()),
                               "s5p_stage2_analyze.py": s2.sha256(Path(s2.__file__).resolve())},
               "products": {str(p): s2.sha256(p) for p in products},
               "definition": "h_f = max_k |shift_k,f|, shift = data unfold at the vertex-k prior over the CV-prior data unfold - 1, reported cells",
               "envelope_D1_D5": envelope(sh, cells, VERTICES),
               "envelope_without_D1": envelope(sh, cells, VERTICES[1:]),
               "bias_sources": bias_sources, "linearity": linearity(sh, bi, cells)}
    a.out.write_text(json.dumps(receipt, indent=1) + "\n")
    print(json.dumps({key: {P: round(v["h_median_pct"], 2) for P, v in receipt[key].items()}
                      for key in ("envelope_D1_D5", "envelope_without_D1")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
