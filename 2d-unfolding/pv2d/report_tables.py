#!/usr/bin/env python3
"""PV-2D: some of REPORT.md's tables, from the committed readouts and ratios/ alone (numpy only).

Prints markdown:
  - the gate tiers per vertex: cells and share of the prior's truth weight on the 205 reported cells, in the three
    tiers the binding names (own ratio, coarse-cell ratio, r = 1);
  - |shift| per vertex by tier;
  - amendment 6's two linearity measures on the PC cells;
  - the cells where h > sigma_Q, with their (pT, p_parallel) ranges, the dominant vertex and its tier;
  - post hoc (not declared), with one rule throughout (classify_cell): which cells sit beside a step in r > STEP, and
    whether the generator's own ratio or the construction drew it; |shift| and h with and without the
    construction-step cells, per arm; the PC's linear response on the two subsets;
  - with --readout-ref, the refined arm beside configuration (a), and the per-cell difference of the two arms' shifts.
The per-vertex shift and h-against-sigma tables of the report are the readout files' own summary fields.

Refuses unless every ratio file's sha256 equals projections.json's, projections.json's own sha256 equals each
readout's ratios_projection_sha256, and the readouts' arm fields are "a" and "refined".

MEASURES: arithmetic on the readouts. CANNOT AUTHORIZE: any claim or verdict.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pv2d_lib as L  # noqa: E402

VERTICES = ("genie_mec", "nuwro", "gibuu")
NAMES = {"genie_mec": "GENIE+MEC", "nuwro": "NuWro", "gibuu": "GiBUU", "h": "envelope h"}
TIERS = (("own ratio", ("fine",)), ("coarse cell", ("coarse",)), ("r = 1", ("noisy", "off")))
STEP = 0.1
# A neighbouring pair's step is drawn by the generator's own ratio only if both cells keep their own ratio ("fine").
# Otherwise the construction drew it: "gate" if a side is a coarse-pooled or noisy (r = 1) cell, the noise gate's
# tiers; "cut" if the only non-fine side is "off" (an unreported cell, or GiBUU at p_parallel >= 10 GeV/c).
CONSTRUCTION = ("gate", "cut")


def load(path):
    with open(path) as f:
        return json.load(f)


def cell_range(gid, pt, pz):
    i, j = divmod(gid, len(pz) - 1)
    return f"{pt[i]:g}–{pt[i + 1]:g}", f"{pz[j]:g}–{pz[j + 1]:g}"


def pct(x, nd=2):
    return f"{100 * x:.{nd}f}%"


def q3(y):
    return " / ".join(pct(q) for q in (np.median(y), np.percentile(y, 90), np.max(y)))


def largest_step(r, gid):
    """The largest |r(cell) - r(neighbour)| over the cell's four grid neighbours, and that neighbour's index."""
    i, j = divmod(gid, r.shape[1])
    best, nb = 0.0, (i, j)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < r.shape[0] and 0 <= b < r.shape[1] and abs(r[i, j] - r[a, b]) > best:
            best, nb = abs(r[i, j] - r[a, b]), (a, b)
    return best, nb


def pair_kind(la, lb):
    if la == "fine" and lb == "fine":
        return "generator"
    if {"coarse", "noisy"} & {la, lb}:
        return "gate"
    return "cut"


def classify_cell(r, lab, gid):
    """Over the cell's grid neighbours with |r - r_nb| > STEP: "gate" if any such pair is a gate pair, else "cut"
    if any is a cut pair, else "generator" if any is a fine|fine pair, else "none"."""
    i, j = divmod(gid, r.shape[1])
    kinds = set()
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < r.shape[0] and 0 <= b < r.shape[1] and abs(r[i, j] - r[a, b]) > STEP:
            kinds.add(pair_kind(lab[i, j], lab[a, b]))
    for k in ("gate", "cut", "generator"):
        if k in kinds:
            return k
    return "none"


def beside_construction_step(r, lab, gid):
    return classify_cell(r, lab, gid) in CONSTRUCTION


class Inputs:
    """The declared ratios, checked against projections.json, and the per-vertex cell classes on the reported cells."""

    def __init__(self, projections, ratios_dir):
        self.P = load(projections)
        self.sha = L.sha256_path(projections)
        self.cells = np.asarray(self.P["reported_cells"])
        self.r, self.lab, self.cls = {}, {}, {}
        for v in VERTICES:
            spec = self.P["vertices"][v]
            path = os.path.join(ratios_dir, spec["ratio_file"])
            if L.sha256_path(path) != spec["ratio_sha256"]:
                sys.exit(f"[FAIL] {path}: sha256 differs from projections.json")
            self.r[v] = np.asarray(load(path)["r"], float)
            self.lab[v] = np.asarray(spec["label"])
            self.cls[v] = np.array([classify_cell(self.r[v], self.lab[v], int(c)) for c in self.cells])
        self.near = {v: np.isin(self.cls[v], CONSTRUCTION) for v in VERTICES}
        self.near["h"] = np.logical_or.reduce([self.near[v] for v in VERTICES])

    def check(self, X, arm):
        if X.get("arm") != arm:
            sys.exit(f"[FAIL] readout arm {X.get('arm')!r}, expected {arm!r}")
        if X.get("ratios_projection_sha256") != self.sha:
            sys.exit("[FAIL] the readout was made against a different projections.json")
        if list(X["cells"]) != list(self.cells):
            sys.exit("[FAIL] the readout's cells differ from projections.json's reported_cells")


def exclusion_table(name, X, I):
    """|shift| per vertex and h, on all cells and (post hoc) without the cells beside a construction-drawn step."""
    sq = np.asarray(X["sigma_Q"]["cells"])
    print(f"\n### {name}: all {len(I.cells)} cells, and POST HOC without the cells beside a construction-drawn step "
          f"> {STEP}\n")
    print("| | all cells: median / p90 / max | cells excluded (of them, by a cut alone) | post hoc, rest: median / p90 / max |")
    print("|---|---|---:|---|")
    for v in VERTICES + ("h",):
        x = np.abs(np.asarray(X["vertices"][v]["shift"])) if v != "h" else np.asarray(X["envelope"]["h"])
        if v == "h":
            cut_only = I.near["h"] & ~np.logical_or.reduce([I.cls[u] == "gate" for u in VERTICES])
        else:
            cut_only = I.cls[v] == "cut"
        print(f"| {NAMES[v]} | {q3(x)} | {int(I.near[v].sum())} ({int(cut_only.sum())}) | {q3(x[~I.near[v]])} |")
    h = np.asarray(X["envelope"]["h"])
    keep = ~I.near["h"]
    print(f"\nh > σ_Q: {int((h > sq).sum())} of {len(I.cells)} on all cells; post hoc, "
          f"{int((h[keep] > sq[keep]).sum())} of {int(keep.sum())} on the cells not beside a construction-drawn step "
          f"(for h, a cell is excluded if it is beside one in any vertex).")


def pc_subsets(A, I):
    """The PC's linear response (pv2d_lib.linear_response) on the PC cells beside and not beside a
    construction-drawn step: at the PC vertex, and in any vertex."""
    pc = A["controls"]["PC"]["primary"]
    v = pc["vertex"]
    b, s = np.asarray(pc["bias_cells"]), np.asarray(pc["shift_cells"])
    mb = pc["min_abs_bias"]
    print(f"\n### POST HOC: the positive control's linear response on the two subsets (PC cells: |bias| > "
          f"{pct(mb, 0)})\n")
    print("| PC cells | n | corr(shift, −bias) | slope | \\|shift\\| ≥ \\|bias\\| |")
    print("|---|---:|---:|---:|---:|")
    rows = (("all (the declared PC)", np.ones(len(b), bool)),
            (f"beside a construction step in {NAMES[v]}'s r", I.near[v]), (f"not beside one in {NAMES[v]}'s r", ~I.near[v]),
            ("beside one in any vertex's r", I.near["h"]), ("not beside one in any vertex's r", ~I.near["h"]))
    for name, m in rows:
        lr = L.linear_response(s[m], b[m], mb)
        sel = m & (np.abs(b) > mb)
        frac = np.mean(np.abs(s[sel]) >= np.abs(b[sel]))
        print(f"| {name} | {lr['n_cells']} | {lr['corr']:.3f} | {lr['slope']:.3f} | {pct(frac, 0)} |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projections", required=True)
    ap.add_argument("--readout-a", required=True)
    ap.add_argument("--readout-ref")
    ap.add_argument("--ratios-dir", help="default: the directory of --projections")
    a = ap.parse_args(argv)
    I = Inputs(a.projections, a.ratios_dir or os.path.dirname(os.path.abspath(a.projections)))
    A = load(a.readout_a)
    I.check(A, "a")
    P, cells = I.P, I.cells
    pt, pz = P["pt_edges"], P["pz_edges"]
    w = np.asarray(P["prior_truth_weight"], float).ravel()[cells]
    labels = {v: I.lab[v].ravel()[cells] for v in VERTICES}

    print("### Gate tiers (cells, share of prior truth weight on the 205 reported cells)\n")
    print("| vertex | " + " | ".join(t for t, _ in TIERS) + " |")
    print("|---|" + "---:|" * len(TIERS))
    for v in VERTICES:
        row = []
        for _, labs in TIERS:
            m = np.isin(labels[v], labs)
            row.append(f"{int(m.sum())} ({pct(w[m].sum() / w.sum())})")
        print(f"| {NAMES[v]} | " + " | ".join(row) + " |")

    print("\n### Median |shift| by tier, configuration (a)\n")
    print("| vertex | " + " | ".join(t for t, _ in TIERS) + " |")
    print("|---|" + "---:|" * len(TIERS))
    for v in VERTICES:
        s = np.abs(np.asarray(A["vertices"][v]["shift"]))
        row = []
        for _, labs in TIERS:
            m = np.isin(labels[v], labs)
            row.append(pct(np.median(s[m])) if m.any() else "—")
        print(f"| {NAMES[v]} | " + " | ".join(row) + " |")

    pc = A["controls"]["PC"]["primary"]
    b, s = np.asarray(pc["bias_cells"]), np.asarray(pc["shift_cells"])
    m = np.abs(b) > pc["min_abs_bias"]
    print(f"\n### Amendment 6's two linearity measures in 2D (the PC cells, |bias| > {pct(pc['min_abs_bias'], 0)}: "
          f"{int(m.sum())})\n")
    print(f"- |shift| >= |bias| in {pct(np.mean(np.abs(s[m]) >= np.abs(b[m])), 1)} of them (declared readout)")
    print(f"- median |shift + bias| / |bias| = {np.median(np.abs(s[m] + b[m]) / np.abs(b[m])):.2f} (post-hoc, not declared)")

    h = np.asarray(A["envelope"]["h"])
    dom = A["envelope"]["dominant"]
    sq = np.asarray(A["sigma_Q"]["cells"])
    sp = np.asarray(A["sigma_paper"]["cells"])
    over = np.flatnonzero(h > sq)
    print(f"\n### Cells with h > σ_Q, configuration (a): {len(over)} of {len(cells)}\n")
    print("| cell | p_T (GeV/c) | p_∥ (GeV/c) | h | σ_Q | σ_paper | dominant | its tier | step beside it (post hoc) |")
    print("|---:|---|---|---:|---:|---:|---|---|---|")
    for k in over[np.argsort(-h[over] / sq[over])]:
        a_pt, a_pz = cell_range(int(cells[k]), pt, pz)
        v = dom[k]
        print(f"| {cells[k]} | {a_pt} | {a_pz} | {pct(h[k], 1)} | {pct(sq[k], 1)} | {pct(sp[k], 1)} | {NAMES[v]} | "
              f"{labels[v][k]} | {I.cls[v][k]} |")
    by_v = {v: int(sum(dom[k] == v for k in over)) for v in VERTICES}
    print("\nDominant vertex among them: " + ", ".join(f"{NAMES[v]} {n}" for v, n in by_v.items()))

    print(f"\n### POST HOC: the step class of each h > σ_Q cell, in its dominant vertex's r (threshold {STEP})\n")
    kinds = {k: int(sum(I.cls[dom[i]][i] == k for i in over)) for k in ("gate", "cut", "generator", "none")}
    print(f"- beside a gate step (a coarse-pooled or noisy cell on one side): {kinds['gate']}")
    print(f"- beside a cut step only (an unreported cell, or GiBUU's p_∥ ≥ 10 GeV/c cut): {kinds['cut']}")
    print(f"- beside a step between two own-ratio cells only (the generator's shape): {kinds['generator']}")
    print(f"- no neighbouring step above {STEP}: {kinds['none']}")
    for v in VERTICES:
        st = np.array([largest_step(I.r[v], int(c))[0] for c in cells])
        sv = np.abs(np.asarray(A["vertices"][v]["shift"]))
        dev = np.abs(I.r[v].ravel()[cells] - 1)
        print(f"- {NAMES[v]}: {pct(np.mean(st > STEP), 0)} of all {len(cells)} cells sit beside a step above {STEP}, "
              f"{pct(np.mean(I.near[v]), 0)} beside a construction-drawn one; corr(|shift|, local step) "
              f"{np.corrcoef(sv, st)[0, 1]:.2f}, corr(|shift|, |r − 1|) {np.corrcoef(sv, dev)[0, 1]:.2f}")

    exclusion_table("Configuration (a)", A, I)
    pc_subsets(A, I)

    if a.readout_ref:
        R = load(a.readout_ref)
        I.check(R, "refined")
        exclusion_table("Refined arm", R, I)
        print("\n### The refined arm beside configuration (a)\n")
        print("| vertex | (a) median / p90 / max | refined median / p90 / max | median \\|Δshift\\| | max \\|Δshift\\| |")
        print("|---|---|---|---:|---:|")
        for v in VERTICES:
            sa, sr = A["vertices"][v], R["vertices"][v]
            d = np.abs(np.asarray(sr["shift"]) - np.asarray(sa["shift"]))
            fa = " / ".join(pct(sa[k]) for k in ("median", "p90", "max"))
            fr = " / ".join(pct(sr[k]) for k in ("median", "p90", "max"))
            print(f"| {NAMES[v]} | {fa} | {fr} | {pct(np.median(d))} | {pct(d.max())} |")
        ea, er = A["envelope"], R["envelope"]
        dh = np.abs(np.asarray(er["h"]) - h)
        print(f"| envelope h (Δh) | " + " / ".join(pct(ea[k]) for k in ("median", "p90", "max")) + " | "
              + " / ".join(pct(er[k]) for k in ("median", "p90", "max")) + f" | {pct(np.median(dh))} | {pct(dh.max())} |")
        for name, key in (("σ_Q", "h_vs_sigma_Q"), ("σ_paper", "h_vs_sigma_paper")):
            ca, cr = A[key], R[key]
            print(f"\n{name}: median h/σ (a) {ca['ratio_median']:.3f}, refined {cr['ratio_median']:.3f}; "
                  f"h > σ in {pct(ca['frac_h_gt_sigma'], 1)} vs {pct(cr['frac_h_gt_sigma'], 1)} of cells; "
                  f"h > σ/2 in {pct(ca['frac_h_gt_half_sigma'], 1)} vs {pct(cr['frac_h_gt_half_sigma'], 1)}.")


if __name__ == "__main__":
    main()
