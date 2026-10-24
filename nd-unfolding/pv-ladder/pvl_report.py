#!/usr/bin/env python3
"""PV ladder: REPORT.md's tables, from the pvl_analyze.py readouts, the frozen reweights and PV-2D's committed
readouts (numpy only). Written before any vertex readout was read.

Prints markdown:
  1. the ladder: per rung and arm, the headline cells, h median / p90 / max, the dominant vertex, the PC, the
     |shift| >= |bias| fraction, and two properties of the reweight that pull h in opposite directions (the
     director's interpretation point, 2026-10-24): the share of the prior's truth weight on pooled J-coarse ratios
     (a coarser effective reweight can damp the shifts), and the share in cells beside a step in r > 0.1 drawn by
     the gate or a cut (PV-2D REPORT §5 found the large-shift tail there); L-2D's rows from PV-2D, L-5D's from s5p;
  2. Ben's comparison: L-EW against L-5D-PV on the 39 RD3 cells. They differ in the classifier's features AND in the
     reweight's strength (each rung's reweight is built on its own cells; REPORT.md §4);
  3. the (p_T, p_parallel) projection of L-3D, L-4D and L-5D-PV against L-2D on its 205 cells;
  4. the J-coarse readouts;
  5. for the rungs whose headline cells are their reweight cells (L-EW, L-3D, L-4D; L-2D from PV-2D), h with and
     without the headline cells beside a construction-drawn step (descriptive, as PV-2D REPORT §5).

MEASURES: arithmetic on the readouts and reweights. CANNOT AUTHORIZE: any claim change.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_PV2D = _HERE.parents[1] / "2d-unfolding" / "pv2d"
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_PV2D))
import pvl_lib as L  # noqa: E402

VERTICES = ("genie_mec", "nuwro", "gibuu")
NAMES = {"genie_mec": "GENIE+MEC", "nuwro": "NuWro", "gibuu": "GiBUU"}
ROWS = (("L-EW", "e"), ("L-EW", "c"), ("L-3D", "e"), ("L-4D", "e"), ("L-5D-PV", "e"))
# s5p's record, RECORD-20260927-s5p-stage2-exit.md:126-131 (R, vertices D1-D5)
S5P = {"RD3 EW (39)": (0.134, 0.392), "RD1 J (109)": (0.120, 0.386), "RD2 H2 (27)": (0.096, 0.225)}


def load(p):
    with open(p) as f:
        return json.load(f)


def pct(x, nd=2):
    return "—" if x is None else f"{100 * x:.{nd}f} %"


def q3(e):
    return f"{pct(e['median'])} / {pct(e['p90'])} / {pct(e['max'])}"


def rung_reweight(ratios_dir, rung):
    """Per rung: the pooled share per vertex, and the step-adjacent mask (union over vertices) on the reweight cells
    with the prior's truth weight there."""
    R = load(ratios_dir / rung / "ratios.json")
    axes = tuple(R["axes"])
    shape = tuple(len(L.FINE[a]) - 1 for a in axes)
    p = np.asarray(R["prior_truth_weight"], float)
    near = np.zeros(int(np.prod(shape)), bool)
    pooled = {}
    for v in VERTICES:
        rec = R["vertices"][v]
        r = np.asarray(load(ratios_dir / rung / rec["ratio_file"])["r"], float)
        cls = L.classify_cells(r, rec["label"], shape)
        near |= np.isin(cls, ("gate", "cut"))
        pooled[v] = rec["tiers_on_cv_positive_cells"]["coarse cell"]["prior_weight_share"]
    on = p > 0
    return {"pooled": pooled, "near": near, "near_share": float(p[on & near].sum() / p[on].sum()), "axes": axes}


def pv2d_reweight():
    import report_tables as RT

    I = RT.Inputs(_PV2D / "ratios" / "projections.json", _PV2D / "ratios")
    w = np.asarray(I.P["prior_truth_weight"], float).ravel()[I.cells]
    pooled = {v: float(w[I.lab[v].ravel()[I.cells] == "coarse"].sum() / w.sum()) for v in VERTICES}
    return {"pooled": pooled, "near_headline": I.near["h"], "near_share": float(w[I.near["h"]].sum() / w.sum())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--readouts", type=Path, required=True, help="pvl_analyze.py outputs, <rung>_<arm>.json")
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios directory")
    a = ap.parse_args(argv)
    X = {(r, arm): load(a.readouts / f"{r}_{arm}.json") for r, arm in ROWS}
    RW = {r: rung_reweight(a.ratios, r) for r in ("L-EW", "L-3D", "L-4D", "L-5D-PV")}
    A2, R2 = load(_PV2D / "readouts" / "readout_a.json"), load(_PV2D / "readouts" / "readout_ref.json")
    P2 = pv2d_reweight()

    def prange(pooled):
        v = list(pooled.values())
        return f"{pct(min(v), 1)}–{pct(max(v), 1)}"

    print("### 1. The ladder (headline cells)\n")
    print("| rung | arm | cells | h median / p90 / max | dominant (GENIE+MEC / NuWro / GiBUU) | PC | |shift| ≥ |bias| | "
          "pooled share | step-adjacent share | h / σ median (h > σ) |")
    print("|---|---|---:|---|---|---|---:|---|---:|---|")
    for lab, X2 in (("L-2D (a)", A2), ("L-2D refined", R2)):
        e, pc = X2["envelope"], (X2["controls"].get("PC") or {}).get("primary")
        pcs = f"{pc['verdict']} (n {pc['n_cells']}, corr {pc['corr']:.3f}, slope {pc['slope']:.3f})" if pc else "— (on (a))"
        frac = pct(pc["shift_ge_bias_frac"], 1) if pc else "—"
        hs = X2["h_vs_sigma_Q"]
        dom = " / ".join(str(e["dominant_vertex_counts"][v]) for v in VERTICES)
        print(f"| {lab} | | 205 | {q3(e)} | {dom} | {pcs} | {frac} | {prange(P2['pooled'])} | {pct(P2['near_share'], 1)} | "
              f"{hs['ratio_median']:.2f} ({int(round(hs['frac_h_gt_sigma'] * 205))}) vs σ_Q |")
    for r, arm in ROWS:
        x = X[(r, arm)]
        s = x["headline"]
        sp = x["spaces"][s]
        e = sp["envelope"]
        pc = x["controls"].get("PC")
        if pc:
            pr = pc.get("fallback") or pc["primary"]
            pcs = f"{pc['verdict']} (n {pr['n_cells']}, corr {pr['corr']:.3f}, slope {pr['slope']:.3f})"
            frac = pct(pc["primary"].get("shift_ge_bias_frac"), 1)
        else:
            pcs, frac = "— (arm (c) has none)", "—"
        hs = sp.get("h_vs_sigma")
        hstxt = (f"{hs['ratio_median']:.2f} ({int(round(hs['frac_h_gt_sigma'] * sp['n_cells']))}) vs C_eavailW"
                 if hs else "none quoted")
        dom = " / ".join(str(e["dominant_vertex_counts"][v]) for v in VERTICES)
        print(f"| {r} | ({arm}) | {sp['n_cells']} {s} | {q3(e)} | {dom} | {pcs} | {frac} | {prange(RW[r]['pooled'])} | "
              f"{pct(RW[r]['near_share'], 1)} | {hstxt} |")
    for k, (m, p90) in S5P.items():
        print(f"| L-5D (s5p, D1–D5) | R | {k} | {pct(m, 1)} / {pct(p90, 1)} / — | | | | | | |")
    print("\nPooled share: the prior's truth weight on pooled J-coarse ratios, range over the three vertices. "
          "Step-adjacent share: the prior's truth weight in reweight cells beside a step in r > 0.1 drawn by the gate "
          "or a cut, union over the vertices.")

    print("\n### 2. Ben's question: L-EW against L-5D-PV on the 39 RD3 cells (features and reweight strength differ)\n")
    ew, f5 = X[("L-EW", "e")]["spaces"]["EW"], X[("L-5D-PV", "e")]["spaces"]["EW"]
    print("| | L-EW (e), direct (E_avail, W) | L-5D-PV (e), 5D projected | s5p RD3 (D1–D5) |")
    print("|---|---|---|---|")
    print(f"| h median / p90 / max | {q3(ew['envelope'])} | {q3(f5['envelope'])} | 13.4 % / 39.2 % / — |")
    for v in VERTICES:
        print(f"| {NAMES[v]} |shift| median / p90 / max | {q3(ew['vertices'][v])} | {q3(f5['vertices'][v])} | |")
    h1, h5 = np.asarray(ew["envelope"]["h"]), np.asarray(f5["envelope"]["h"])
    print(f"\nPer cell: h(L-EW) < h(L-5D-PV) in {int((h1 < h5).sum())} of 39 cells; median h(L-EW) / h(L-5D-PV) "
          f"{np.median(h1 / h5):.3f}.")
    if ew.get("h_vs_sigma"):
        sig = np.asarray(ew["sigma"]["cells"])
        print(f"Against C_eavailW (median σ {pct(np.median(sig))}): L-EW h/σ median {np.median(h1 / sig):.2f}, "
              f"h > σ in {int((h1 > sig).sum())}; L-5D-PV h/σ median {np.median(h5 / sig):.2f}, h > σ in "
              f"{int((h5 > sig).sum())}.")

    print("\n### 3. The (p_T, p_parallel) projection on L-2D's 205 cells\n")
    print("| rung | h median / p90 / max | GENIE+MEC / NuWro / GiBUU median |shift| |")
    print("|---|---|---|")
    for lab, X2 in (("L-2D (a)", A2), ("L-2D refined", R2)):
        print(f"| {lab} | {q3(X2['envelope'])} | "
              + " / ".join(pct(X2['vertices'][v]['median']) for v in VERTICES) + " |")
    for r in ("L-3D", "L-4D", "L-5D-PV"):
        sp = X[(r, "e")]["spaces"]["PTPZ"]
        print(f"| {r} (e) | {q3(sp['envelope'])} | " + " / ".join(pct(sp['vertices'][v]['median']) for v in VERTICES) + " |")

    print("\n### 4. The J-coarse cells\n")
    print("| rung | J cells | h median / p90 / max |")
    print("|---|---:|---|")
    for r in ("L-3D", "L-4D", "L-5D-PV"):
        sp = X[(r, "e")]["spaces"]["J"]
        print(f"| {r} (e) | {sp['n_cells']} | {q3(sp['envelope'])} |")
    print(f"| L-5D (s5p, D1–D5) | 109 | 12.0 % / 38.6 % / — |")

    print("\n### 5. h with and without the headline cells beside a construction-drawn step (descriptive)\n")
    print("| rung | arm | cells beside a step | h all: median / p90 / max | h rest: median / p90 / max |")
    print("|---|---|---:|---|---|")
    h2 = np.asarray(A2["envelope"]["h"])
    m2 = np.asarray(P2["near_headline"])
    for lab, h, m in (("L-2D (a)", h2, m2),):
        print(f"| {lab} | | {int(m.sum())} of {m.size} | {q3(L_q(h))} | {q3(L_q(h[~m]))} |")
    for r, arm in (("L-EW", "e"), ("L-EW", "c"), ("L-3D", "e"), ("L-4D", "e")):
        x = X[(r, arm)]
        cells = np.asarray(x["cells"][x["headline"]])
        m = RW[r]["near"][cells]
        h = np.asarray(x["spaces"][x["headline"]]["envelope"]["h"])
        rest = q3(L_q(h[~m])) if (~m).any() else "—"
        print(f"| {r} | ({arm}) | {int(m.sum())} of {m.size} | {q3(L_q(h))} | {rest} |")
    return 0


def L_q(a):
    a = np.abs(np.asarray(a, float))
    return {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(np.max(a))}


if __name__ == "__main__":
    raise SystemExit(main())
