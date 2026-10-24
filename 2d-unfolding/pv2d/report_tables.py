#!/usr/bin/env python3
"""PV-2D: the REPORT.md tables, from the committed readouts and ratios/projections.json alone (numpy only).

Prints markdown:
  - the gate tiers per vertex: cells and share of the prior's truth weight on the 205 reported cells, in the three
    tiers the binding names (own ratio, coarse-cell ratio, r = 1);
  - |shift| per vertex by tier;
  - the cells where h > sigma_Q, with their (pT, p_parallel) ranges, the dominant vertex and its tier;
  - post-hoc (not declared): whether those cells sit beside a step in r, and whether the gate built that step;
  - post-hoc (not declared): |shift| and h with and without the cells beside a gate-drawn step, per arm;
  - with --readout-ref, the refined arm beside configuration (a), and the per-cell difference of the two arms' shifts.

MEASURES: arithmetic on the readouts. CANNOT AUTHORIZE: any claim or verdict.
"""
import argparse
import json
import os
import sys

import numpy as np

VERTICES = ("genie_mec", "nuwro", "gibuu")
NAMES = {"genie_mec": "GENIE+MEC", "nuwro": "NuWro", "gibuu": "GiBUU"}
TIERS = (("own ratio", ("fine",)), ("coarse cell", ("coarse",)), ("r = 1", ("noisy", "off")))


def load(path):
    with open(path) as f:
        return json.load(f)


def cell_range(gid, pt, pz):
    i, j = divmod(gid, len(pz) - 1)
    return f"{pt[i]:g}–{pt[i + 1]:g}", f"{pz[j]:g}–{pz[j + 1]:g}"


def pct(x, nd=2):
    return f"{100 * x:.{nd}f}%"


STEP = 0.1


def largest_step(r, gid):
    """The largest |r(cell) - r(neighbour)| over the cell's four grid neighbours, and that neighbour's index."""
    i, j = divmod(gid, r.shape[1])
    best, nb = 0.0, (i, j)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if 0 <= a < r.shape[0] and 0 <= b < r.shape[1] and abs(r[i, j] - r[a, b]) > best:
            best, nb = abs(r[i, j] - r[a, b]), (a, b)
    return best, nb


def beside_gate_step(r, lab, gid):
    """True if some grid neighbour differs from the cell by more than STEP in r and the pair is not two own-ratio
    ("fine") cells: a step at a boundary the gate drew."""
    i, j = divmod(gid, r.shape[1])
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = i + di, j + dj
        if (0 <= a < r.shape[0] and 0 <= b < r.shape[1] and abs(r[i, j] - r[a, b]) > STEP
                and not (lab[i, j] == "fine" and lab[a, b] == "fine")):
            return True
    return False


def exclusion_table(name, X, P, cells, ratios_dir):
    """|shift| per vertex and h, on all cells and (post hoc) without the cells beside a gate-drawn step."""
    near = {}
    for v in VERTICES:
        r = np.asarray(load(f"{ratios_dir}/{P['vertices'][v]['ratio_file']}")["r"], float)
        lab = np.asarray(P["vertices"][v]["label"])
        near[v] = np.array([beside_gate_step(r, lab, int(c)) for c in cells])
    near["h"] = np.logical_or.reduce([near[v] for v in VERTICES])
    sq = np.asarray(X["sigma_Q"]["cells"])
    print(f"\n### {name}: all {len(cells)} cells, and POST HOC without the cells beside a gate-drawn step > {STEP}\n")
    print("| | all cells: median / p90 / max | cells excluded | post hoc, rest: median / p90 / max |")
    print("|---|---|---:|---|")
    for v in VERTICES + ("h",):
        x = np.abs(np.asarray(X["vertices"][v]["shift"])) if v != "h" else np.asarray(X["envelope"]["h"])
        keep = ~near[v]
        f = lambda y: " / ".join(pct(q) for q in (np.median(y), np.percentile(y, 90), np.max(y)))
        print(f"| {NAMES.get(v, 'envelope h')} | {f(x)} | {int(near[v].sum())} | {f(x[keep])} |")
    h = np.asarray(X["envelope"]["h"])
    keep = ~near["h"]
    print(f"\nh > σ_Q: {int((h > sq).sum())} of {len(cells)} on all cells; post hoc, "
          f"{int((h[keep] > sq[keep]).sum())} of {int(keep.sum())} on the cells not beside a gate-drawn step "
          f"(h excludes a cell beside such a step in any vertex).")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projections", required=True)
    ap.add_argument("--readout-a", required=True)
    ap.add_argument("--readout-ref")
    ap.add_argument("--ratios-dir", help="default: the directory of --projections")
    a = ap.parse_args(argv)
    a.ratios_dir = a.ratios_dir or os.path.dirname(os.path.abspath(a.projections))
    P, A = load(a.projections), load(a.readout_a)
    cells = np.asarray(A["cells"])
    if list(cells) != list(P["reported_cells"]):
        sys.exit("[FAIL] the readout's cells differ from projections.json's reported_cells")
    pt, pz = P["pt_edges"], P["pz_edges"]
    w = np.asarray(P["prior_truth_weight"], float).ravel()[cells]
    labels = {v: np.asarray(P["vertices"][v]["label"]).ravel()[cells] for v in VERTICES}

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
    print("| cell | p_T (GeV/c) | p_∥ (GeV/c) | h | σ_Q | σ_paper | dominant | its tier |")
    print("|---:|---|---|---:|---:|---:|---|---|")
    for k in over[np.argsort(-h[over] / sq[over])]:
        a_pt, a_pz = cell_range(int(cells[k]), pt, pz)
        v = dom[k]
        print(f"| {cells[k]} | {a_pt} | {a_pz} | {pct(h[k], 1)} | {pct(sq[k], 1)} | {pct(sp[k], 1)} | {NAMES[v]} | "
              f"{labels[v][k]} |")
    by_v = {v: int(sum(dom[k] == v for k in over)) for v in VERTICES}
    print("\nDominant vertex among them: " + ", ".join(f"{NAMES[v]} {n}" for v, n in by_v.items()))

    print(f"\n### Post-hoc (not declared): the largest step in r beside each h > σ_Q cell (threshold {STEP})\n")
    kinds = {"gate": 0, "generator": 0, "none": 0}
    for k in over:
        v = dom[k]
        r = np.asarray(load(f"{a.ratios_dir}/{P['vertices'][v]['ratio_file']}")["r"], float)
        lab = np.asarray(P["vertices"][v]["label"])
        step, nb = largest_step(r, int(cells[k]))
        i, j = divmod(int(cells[k]), r.shape[1])
        if step <= STEP:
            kinds["none"] += 1
        elif lab[i, j] == "fine" and lab[nb] == "fine":
            kinds["generator"] += 1
        else:
            kinds["gate"] += 1
    print(f"- beside a step that touches a coarse, noisy or off cell (built by the gate): {kinds['gate']}")
    print(f"- beside a step between two own-ratio cells (the generator's shape): {kinds['generator']}")
    print(f"- no neighbouring step above {STEP}: {kinds['none']}")
    for v in VERTICES:
        r = np.asarray(load(f"{a.ratios_dir}/{P['vertices'][v]['ratio_file']}")["r"], float)
        st = np.array([largest_step(r, int(c))[0] for c in cells])
        s = np.abs(np.asarray(A["vertices"][v]["shift"]))
        dev = np.abs(r.ravel()[cells] - 1)
        print(f"- {NAMES[v]}: {pct(np.mean(st > STEP), 0)} of all {len(cells)} cells sit beside a step above {STEP}; "
              f"corr(|shift|, local step) {np.corrcoef(s, st)[0, 1]:.2f}, "
              f"corr(|shift|, |r − 1|) {np.corrcoef(s, dev)[0, 1]:.2f}")

    exclusion_table("Configuration (a)", A, P, cells, a.ratios_dir)

    if a.readout_ref:
        R = load(a.readout_ref)
        if list(R["cells"]) != list(A["cells"]):
            sys.exit("[FAIL] the two arms' cells differ")
        exclusion_table("Refined arm", R, P, cells, a.ratios_dir)
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
        print(f"| envelope h | " + " / ".join(pct(ea[k]) for k in ("median", "p90", "max")) + " | "
              + " / ".join(pct(er[k]) for k in ("median", "p90", "max")) + " | "
              f"{pct(np.median(np.abs(np.asarray(er['h']) - h)))} | {pct(np.abs(np.asarray(er['h']) - h).max())} |")
        for name, key in (("σ_Q", "h_vs_sigma_Q"), ("σ_paper", "h_vs_sigma_paper")):
            ca, cr = A[key], R[key]
            print(f"\n{name}: median h/σ (a) {ca['ratio_median']:.3f}, refined {cr['ratio_median']:.3f}; "
                  f"h > σ in {pct(ca['frac_h_gt_sigma'], 1)} vs {pct(cr['frac_h_gt_sigma'], 1)} of cells; "
                  f"h > σ/2 in {pct(ca['frac_h_gt_half_sigma'], 1)} vs {pct(cr['frac_h_gt_half_sigma'], 1)}.")


if __name__ == "__main__":
    main()
