#!/usr/bin/env python3
"""#977's L rows (RESPONSE.md 4.2/F4.3, 4.3, F5.3, F5.4, 3.3, m5/Fm7, s11c): one derived readout from committed sources.

Usage (repo root, python -I): l_rows.py <out l_rows.json>
Every source is read from this checkout and pinned below by sha256; a mismatch stops the run (exit 3). Descriptive
numbers only: no criterion, trigger or grade changes.

  4.2/F4.3  pscr-20261112/members/work_proxy.npz (per-playlist templates) and the coverage run's proxy_hists_meta.json
            (POT): background k*B over data D on the 14x16 analysis grid, k = pot_data/pot_mc per playlist. Compared,
            not gated, with E_U's totals (stageA/REPORT.md:178-179: background 119,132.37, 2.91% of data 4,091,707).
  4.3       fig:tension2d's per-bin contributions Delta_i (C+ Delta)_i, the committed capture of the current figure
            (fig-restyle-20261031 run-a2/after/capture/tension, stored [pz, pt]); they must sum to C-PUB's chi2
            465.41527219152636. Cell set T, fixed by rule: the largest contributors, in decreasing order, until their sum
            first reaches half the chi2. Reported: the background fraction over T and over all 205 cells, and the Spearman
            rank correlation of the per-cell fraction with the contribution over the 205.
  F5.3      pscr-20261112/members/f53.json (measured with r4_migration.py's masks; its control passed in the session).
  F5.4      stage1_inspect.json mc.H2 and h2_definition.json unreported_boxes: the four boxes' share of the truth weight
            and of the expected reconstructed signal, at the data exposure.
  3.3       l-rows-20261112/derived/r33.json (r33_leave_gibuu.py).
  m5/Fm7    pscr-20261112/derived/m5_injected.json (m5_injected.py), and stage1_inspect.json mc.EW (populations, support).
  s11c      s5e/cand/assess_receipt.json points.eavail_gibuu.per_functional (the reported estimator, 20 experiments).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path.cwd()
M = "docs/orchestration/state/2d-closeout/stageF/methods"
P = f"{M}/methods-short-20261109/pscr-20261112"
L = f"{M}/methods-short-20261109/l-rows-20261112"
SRC = {
    "work_proxy": (f"{P}/members/work_proxy.npz", "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621"),
    "proxy_meta": ("docs/orchestration/state/2d-closeout/playlist-spread-20261014/coverage/outputs/proxy_hists_meta.json", None),
    "tension": (f"{M}/fig-restyle-20261031/run-a2/after/capture/tension/tension_chi2_map.png.npz",
                "e3f12c5dcbe157aebced40234b955dcaa7606d38a3bf28c3f6ae674e70ff26ed"),
    "f53": (f"{P}/members/f53.json", "20c1932b2a05eafb405a85e8c1f92d08cc9d07d266d1a8a103ce4d3cbc1f1824"),
    "s1i": ("docs/orchestration/state/s5p/stage1/stage1_inspect.json", None),
    "h2def": ("nd-unfolding/pv-ladder/readouts/h2_definition.json", None),
    "r33": (f"{L}/derived/r33.json", "8543c3962e63208b65e50b4e9cc0371c9636bf6e18ad789883490428474cb104"),
    "m5": (f"{P}/derived/m5_injected.json", "05afb8b71b8cce2f32071b39eada5fb91f837ac8c8165b041a61b39f883fb8ff"),
    "assess": ("docs/orchestration/state/s5e/cand/assess_receipt.json", None),
}
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
CPUB_CHI2 = 465.41527219152636
EU_BKG, EU_DATA = 119132.37, 4091707


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rank(x: np.ndarray) -> np.ndarray:
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[o] = np.arange(len(x))
    # average ties
    for v in np.unique(x):
        t = x == v
        if t.sum() > 1:
            r[t] = r[t].mean()
    return r


def main() -> int:
    out = Path(sys.argv[1])
    src = {}
    for k, (p, want) in SRC.items():
        got = digest(REPO / p)
        if want is not None and got != want:
            print(f"STOP: {p} sha256 {got} is not {want}"); return 3
        src[k] = {"path": p, "bytes_digest_sha256": got}
    rec = {"schema": "methods-short-l-rows/1", "label": "descriptive only", "sources": src}

    # 4.2 / F4.3
    w = np.load(REPO / SRC["work_proxy"][0], allow_pickle=False)
    meta = json.loads((REPO / SRC["proxy_meta"][0]).read_text())
    assert sorted(meta) == sorted(PLS)
    B = D = 0
    per = {}
    for pl in PLS:
        k = meta[pl]["pot_data"] / meta[pl]["pot_mc"]
        b, d = k * w[f"{pl}__ana__B"], w[f"{pl}__ana__D"]
        per[pl] = round(float(b.sum() / d.sum()), 5)
        B, D = B + b, D + d
    cells = D > 0
    frac = np.where(cells, B / np.where(cells, D, 1), np.nan)
    f_all = float(B.sum() / D.sum())
    rec["bkg_42"] = {"fraction_full_sample": f_all, "sum_background": float(B.sum()), "sum_data_in_grid": float(D.sum()),
                     "n_cells_with_data": int(cells.sum()), "per_playlist": per,
                     "per_cell_min": float(np.nanmin(frac)), "per_cell_median": float(np.nanmedian(frac)),
                     "per_cell_max": float(np.nanmax(frac)),
                     "per_cell_max_at_pt_pz_bin": [int(i) for i in np.unravel_index(np.nanargmax(frac), frac.shape)],
                     "compare_E_U": {"E_U_background": EU_BKG, "E_U_data": EU_DATA,
                                     "data_equal": float(D.sum()) == EU_DATA,
                                     "background_rel_diff": float(B.sum() / EU_BKG - 1),
                                     "E_U_fraction": EU_BKG / EU_DATA},
                     "not_separated": "genuine background and out-of-phase-space signal: no committed record separates them"}

    # 4.3
    t = np.load(REPO / SRC["tension"][0], allow_pickle=False)
    c = np.ma.array(t["i0.array"], mask=t["i0.array.mask"]).T  # -> [pt, pz]
    if not (np.isclose(float(c.sum()), CPUB_CHI2, rtol=1e-12) and ((~c.mask) == cells).all()):
        print("STOP: the contributions do not sum to C-PUB's chi2, or their cells are not the 205 with data"); return 4
    cv, fv, bv, dv = c.data[cells], frac[cells], B[cells], D[cells]
    o = np.argsort(-cv, kind="mergesort")
    cs = np.cumsum(cv[o])
    n_t = int(np.searchsorted(cs, CPUB_CHI2 / 2) + 1)
    T = o[:n_t]
    rho = float(np.corrcoef(rank(cv), rank(fv))[0, 1])
    rec["bkg_43"] = {"rule": "largest contributors in decreasing order until their sum first reaches chi2/2",
                     "chi2": float(c.sum()), "n_cells_T": n_t, "chi2_share_T": float(cs[n_t - 1] / c.sum()),
                     "fraction_T": float(bv[T].sum() / dv[T].sum()), "fraction_all": f_all,
                     "per_cell_median_T": float(np.median(fv[T])), "per_cell_median_all": float(np.median(fv)),
                     "per_cell_min_T": float(fv[T].min()), "per_cell_max_T": float(fv[T].max()),
                     "spearman_fraction_vs_contribution_205": rho}

    # F5.3
    f53 = json.loads((REPO / SRC["f53"][0]).read_text())
    assert f53["control_r4_match"]
    rec["f53"] = {"weighted_outside_reco_window": 1 - f53["frac_reco_in_window_weighted"],
                  "weighted_gen_outside_grid": 1 - f53["frac_gen_in_grid_weighted"],
                  "n_reco_outside_window": f53["n_reco_outside_window"], "n_gen_outside_grid": f53["n_gen_outside_grid"],
                  "n_pass_reco": f53["n_pass_reco"],
                  "gen_outside_grid_includes": "rows with the -9999 truth sentinel in q3 and W (r4_migration.json gen_min_per_col)",
                  "measured_side": "s5c_pseudo.purity_weights :104-112 gives pseudo-data outside the window measured weight 0"}

    # F5.4
    s1 = json.loads((REPO / SRC["s1i"][0]).read_text())
    h2 = s1["mc"]["H2"]
    un = [b[0] for b in json.loads((REPO / SRC["h2def"][0]).read_text())["unreported_boxes"]]
    td, er = np.asarray(h2["truth_denominator"], float), np.asarray(h2["expected_reco_signal"], float)
    rec["f54"] = {"boxes": un, "truth_weight": [float(td[i]) for i in un], "expected_reco_signal": [float(er[i]) for i in un],
                  "share_truth_weight": float(td[un].sum() / td.sum()),
                  "share_expected_reco_signal": float(er[un].sum() / er.sum()),
                  "truth_weight_total": float(td.sum()), "expected_reco_signal_total": float(er.sum())}

    # 3.3
    r33 = json.loads((REPO / SRC["r33"][0]).read_text())
    assert all(r33["control_M0_reproduces_readout"].values()) and all(r33["t2b_controls_rerun"].values())
    ch = {n: r["leave_gibuu"]["chi2"] - r["existing"]["chi2"] for n, r in r33["records"].items()}
    moved = {n: [len(r["existing"]["cells_abs_z_gt_2"]), len(r["leave_gibuu"]["cells_abs_z_gt_2"])]
             for n, r in r33["records"].items() if r["cells_abs_z_gt_2_added"] or r["cells_abs_z_gt_2_removed"]}
    nmax = max(ch, key=ch.get)
    rec["r33"] = {"n_records": len(ch), "records_count_moved": moved,
                  "chi2_rise_max": ch[nmax], "chi2_rise_max_record": nmax,
                  "chi2_from_to_max_record": [r33["records"][nmax]["existing"]["chi2"], r33["records"][nmax]["leave_gibuu"]["chi2"]],
                  "unchanged_own_gibuu": [n for n, r in r33["records"].items() if r["same_matrix"]],
                  "q3_max_abs_z": [r33["records"]["q3"]["existing"]["max_abs_z"], r33["records"]["q3"]["leave_gibuu"]["max_abs_z"]],
                  "q3_cells_abs_z_gt_2_added": r33["records"]["q3"]["cells_abs_z_gt_2_added"]}

    # m5 / Fm7
    m5 = json.loads((REPO / SRC["m5"][0]).read_text())
    ew = s1["mc"]["EW"]
    rep = np.asarray(ew["reported"], bool)
    inj = {k: np.asarray(v) for k, v in m5["injected_change_pct"].items()}
    rec["m5"] = {"max_abs_injected_pct": m5["max_abs_injected_pct"],
                 "max_abs_injected_pct_supported": {k: [float(np.max(np.abs(v[rep]))), f"EW{int(np.flatnonzero(rep)[np.argmax(np.abs(v[rep]))])}"]
                                                    for k, v in inj.items()},
                 "unsupported_EW": [f"EW{i}" for i in np.flatnonzero(~rep)],
                 "unsupported_truth_weight": [float(ew["truth_denominator"][i]) for i in np.flatnonzero(~rep)],
                 "controls_pass": [m5["control_W1"]["pass"], m5["control_W2"]["pass"]],
                 "support_cells_empty_in_every_seed": {k: v["support_cells_empty_in_every_seed"] for k, v in m5["sets"].items()},
                 "not_checkable": "a fine cell populated in the full MC but empty in every one of the 100 halves"}

    # s11c
    a = json.loads((REPO / SRC["assess"][0]).read_text())
    pg = a["points"]["eavail_gibuu"]
    mr = 100 * np.asarray(pg["per_functional"]["mean_rel"][:42])
    rec["s11c"] = {"n_experiments": pg["n"], "estimator": a.get("candidate"),
                   "max_abs_residual_pct": [float(np.max(np.abs(mr))), f"EW{int(np.argmax(np.abs(mr)))}"],
                   "median_abs_residual_pct": float(np.median(np.abs(mr))),
                   "max_abs_residual_pct_supported": float(np.max(np.abs(mr[rep]))),
                   "residual_pct": mr.tolist()}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rec.items() if k not in ("sources",)}, indent=1)[:6000])
    print("L-ROWS OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
