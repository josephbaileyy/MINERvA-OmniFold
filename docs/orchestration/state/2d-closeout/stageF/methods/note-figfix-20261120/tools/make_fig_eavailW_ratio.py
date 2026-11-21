#!/usr/bin/env python3
"""fig:eavailWband redrawn from the repaired generator predictions, with a generator/data ratio panel under each marginal
(Joseph's request, relayed by the director on 2026-11-20, item (a); the director's GO of 2026-11-21 for the fetch).

usage (figenv/rootmpl3108: PyROOT reads the four generator files):  python3 make_fig_eavailW_ratio.py [--out DIR]

Inputs, each held to a digest in a committed record (refuses otherwise):
  data   note-figstyle-20261113/runs/family5/dumps/band_arrays.npz, key data2d only. Its sha256 must equal the
         out/band_arrays.npz line of that run's connect-family5.session.txt, whose recorded data input is
         excess_eavail_W.root 751bb859 (the session's "excess" line, asserted here). The npz's generator arrays are
         pre-repair and are NOT read.
  gens   runs/eavailw/inputs/{genie_cv,genie_mec,nuwro_cv,gibuu_cv}_xsec_eavailW.root, the s5p stage-7 repaired,
         flux-corrected predictions fetched read-only from the s5p CFS archive. Each sha256 must equal its line in
         state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt. Histogram hXSec_eavailW, read as
         overlay_eavailW_band.py reads it (bin contents, no flow), on axes that must equal its edges.
The marginals are overlay_eavailW_band.py's: dsigma/dE_avail = sum_W x dW, dsigma/dW = sum_E x dE, drawn without the
catch bins (E_avail and W above 3 GeV), as the installed figure draws them.
Checks before drawing (any failure writes nothing):
  1. against the repaired run's committed log (state/s5p/stage7/generator-context/eavailW_band_s5p_repaired-log.txt),
     at the log's printed precision: each generator's total, the data total, the data/gen total ratio, the corner
     (E_avail >= 0.8, W >= 1.8) sums and data/gen corner ratio, and every row of its dsigma/dW table (data and the four);
  2. the caption's claim against docs/analysis-note/values.tex: \\genieWmidLo and \\genieWmidHi (percent, printed
     integers) are min and max of 100 (gen/data - 1) for GENIE CV and GENIE + MEC at 1.4 <= W < 1.8 GeV, within half a
     unit of the printed digit (fig_numbers.py's tolerance);
  3. the data: the session's input line names 751bb859, and the npz digest equals that run's output line (above); the
     data totals and W table also agree with the repaired log in check 1.
After drawing, every step, point and ratio is read back from the figure's artists and asserted equal to the computed
values; no font is under 7 pt. Outputs (to --out, default ../figs-src, not committed): eavailW_band.pdf (no creation
date: reruns are byte-identical), eavailW_band.png (preview), eavailW_band_values.json (every plotted number, input
digests, checks).
Central values only, as the installed figure: no uncertainty is drawn.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REC = HERE.parent
REPO = HERE.parents[7]
sys.path.insert(0, str(REPO))

F5 = "docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/runs/family5"
NPZ = f"{F5}/dumps/band_arrays.npz"
SESSION = f"{F5}/connect-family5.session.txt"
SUMS = "docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt"
LOG = "docs/orchestration/state/s5p/stage7/generator-context/eavailW_band_s5p_repaired-log.txt"
VALUES = "docs/analysis-note/values.tex"
DATA_SHA = "751bb859766adf684eb05f483800505cb5ee8160f31c8e93a4eec277d37f3058"
EAVAIL_EDGES = np.asarray([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float)
W_EDGES = np.asarray([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float)
# (label as the installed figure and the repaired log, file stem, colour and marker as the installed figure draws them)
GENS = (("GENIE-CV", "genie_cv", "#CC79A7", "v"), ("GENIE+MEC", "genie_mec", "#EB6834", "s"),
        ("NuWro", "nuwro_cv", "#1BAF7A", "^"), ("GiBUU", "gibuu_cv", "#4A3AA7", "D"))
DATA_STYLE = ("data (unfolded)", "#C0392B", "o")
UNIT = 1e-38   # the upper panels draw dsigma/dX in units of 1e-38 cm^2/GeV/nucleon (hData2D is cm^2/GeV^2/nucleon)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def th2(path):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(str(path))
    h = f.Get("hXSec_eavailW")
    xa, ya = h.GetXaxis(), h.GetYaxis()
    xe = [xa.GetBinLowEdge(i) for i in range(1, xa.GetNbins() + 2)]
    ye = [ya.GetBinLowEdge(i) for i in range(1, ya.GetNbins() + 2)]
    assert np.array_equal(xe, EAVAIL_EDGES) and np.array_equal(ye, W_EDGES), f"{path.name}: axes {xe} {ye}"
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(len(ye) - 1)] for i in range(len(xe) - 1)])
    f.Close()
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REC / "figs-src")
    a = ap.parse_args()

    # ---- inputs and their digests
    sess = (REPO / SESSION).read_text()
    m = re.search(r"^([0-9a-f]{64})  out/band_arrays\.npz$", sess, re.M)
    npz_sha = sha256(REPO / NPZ)
    assert m and m.group(1) == npz_sha, "band_arrays.npz is not the family5 run's output"
    assert re.search(r"; excess \S+/excess_eavail_W\.root size \d+ sha256 " + DATA_SHA, sess), "data input not 751bb859"
    data2d = np.load(REPO / NPZ)["data2d"]
    sums = {}
    for line in (REPO / SUMS).read_text().splitlines():
        h, p = line.split(None, 1)
        sums[p.strip()] = h
    gens, gsha = {}, {}
    for label, stem, _, _ in GENS:
        p = REC / f"runs/eavailw/inputs/{stem}_xsec_eavailW.root"
        gsha[label] = sha256(p)
        want = sums[f"stage7/genfig/3d-unfolding/genie/{stem}_xsec_eavailW.root"]
        if gsha[label] != want:
            raise SystemExit(f"REFUSE: {p.name} sha256 {gsha[label]} is not the archive's {want}")
        gens[label] = th2(p)

    dea, dw = np.diff(EAVAIL_EDGES)[:, None], np.diff(W_EDGES)[None, :]
    area = dea * dw
    corner = np.outer(EAVAIL_EDGES[:-1] >= 0.8, W_EDGES[:-1] >= 1.8)
    data_ea, data_w = (data2d * dw).sum(axis=1), (data2d * dea).sum(axis=0)
    g_ea = {k: (g * dw).sum(axis=1) for k, g in gens.items()}
    g_w = {k: (g * dea).sum(axis=0) for k, g in gens.items()}
    d_tot, d_cor = float((data2d * area).sum()), float((data2d * area)[corner].sum())

    # ---- check 1: the repaired run's log, at its printed precision
    log = (REPO / LOG).read_text()
    checks = {}
    for label in gens:
        g_tot, g_cor = float((gens[label] * area).sum()), float((gens[label] * area)[corner].sum())
        want = (f"[band] {label}: total={g_tot:.4e} (data {d_tot:.4e}, ratio {d_tot / g_tot:.3f}); "
                f"hiE-hiW corner={g_cor:.4e} (data {d_cor:.4e}, data/gen={d_cor / g_cor:.3f})")
        assert want in log, f"log line differs for {label}: {want}"
        checks[f"log_line_{label}"] = want
    for j in range(len(W_EDGES) - 1):
        row = f"  {W_EDGES[j]:4.1f}-{W_EDGES[j + 1]:5.1f}  {data_w[j]:10.3e}" + "".join(
            f"   {g_w[l][j]:10.3e}" for l in gens)
        assert row in log, f"W table row differs: {row!r}"
    checks["log_W_table_rows"] = len(W_EDGES) - 1

    # ---- check 2: the caption's 9-12 % against values.tex
    vt = (REPO / VALUES).read_text()
    lo = int(re.search(r"\\newcommand\{\\genieWmidLo\}\{(\d+)\}", vt).group(1))
    hi = int(re.search(r"\\newcommand\{\\genieWmidHi\}\{(\d+)\}", vt).group(1))
    jm = int(np.where(np.isclose(W_EDGES[:-1], 1.4))[0][0])
    pct = {l: 100.0 * (g_w[l][jm] / data_w[jm] - 1.0) for l in ("GENIE-CV", "GENIE+MEC")}
    assert abs(min(pct.values()) - lo) <= 0.5 and abs(max(pct.values()) - hi) <= 0.5, f"W-mid {pct} vs {lo}-{hi}"
    checks["values_tex_genieWmid"] = {"printed": [lo, hi], "computed_pct": pct}

    # ---- draw
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import note_print_style as nps
    nps.apply()
    fig, axs = plt.subplots(2, 2, figsize=nps.figsize(0.99, 0.62), sharex="col",
                            gridspec_kw={"height_ratios": [2.6, 1.0], "hspace": 0.06, "wspace": 0.32})
    panels = ((0, EAVAIL_EDGES, data_ea, g_ea, r"$E_{\mathrm{avail}}$ (GeV)", r"$d\sigma/dE_{\mathrm{avail}}$ ($10^{-38}$ cm$^2$/GeV/nucleon)"),
              (1, W_EDGES, data_w, g_w, r"$W$ (GeV)", r"$d\sigma/dW$ ($10^{-38}$ cm$^2$/GeV/nucleon)"))
    drawn = {}
    for c, edges, dv, gv, xlab, ylab in panels:
        e = edges[:-1]                       # the drawn edges: the catch bin is left off, as in the installed figure
        n = len(e) - 1
        cen = 0.5 * (e[:-1] + e[1:])
        top, bot = axs[0, c], axs[1, c]
        rec = {"edges": e.tolist(), "data": dv[:n].tolist(), "gens": {}, "ratio": {}}
        for label, _, col, mk in GENS:
            y = gv[label][:n]
            r = y / dv[:n]
            st = top.stairs(y / UNIT, e, color=col, lw=1.0, baseline=None)
            pt, = top.plot(cen, y / UNIT, marker=mk, linestyle="None", ms=3.5, color=col)
            if c == 0:
                top.plot([], [], marker=mk, linestyle="-", lw=1.0, ms=3.5, color=col, label=label)
            rs = bot.stairs(r, e, color=col, lw=1.0, baseline=None)
            rp, = bot.plot(cen, r, marker=mk, linestyle="None", ms=3.0, color=col)
            rec["gens"][label] = y.tolist()
            rec["ratio"][label] = r.tolist()
            drawn[(c, label)] = (st, pt, rs, rp, y, r, cen)
        dp, = top.plot(cen, dv[:n] / UNIT, marker=DATA_STYLE[2], linestyle="None", ms=4, color=DATA_STYLE[1],
                       label=DATA_STYLE[0] if c == 0 else None, zorder=5)
        drawn[(c, "data")] = (dp, dv[:n], cen)
        bot.axhline(1.0, color="0.35", lw=0.8, ls="--", zorder=0)
        vals = np.concatenate([dv[:n]] + [gv[l][:n] for l in gv])
        top.set_ylim(0.0, vals.max() / UNIT * 1.12)   # linear, from zero, as Fig. 2's upper panels
        top.set_ylabel(ylab)
        rv = np.concatenate([np.asarray(rec["ratio"][l]) for l in rec["ratio"]])
        pad = 0.08 * (rv.max() - rv.min())
        bot.set_ylim(min(rv.min(), 1.0) - pad, max(rv.max(), 1.0) + pad)
        bot.set_xlim(e[0], e[-1])
        bot.set_xlabel(xlab)
        bot.set_ylabel("gen. / data")
        rec["ratio_ylim"] = list(bot.get_ylim())
        drawn[(c, "rec")] = rec
    h, l = axs[0, 0].get_legend_handles_labels()
    order = [l.index(DATA_STYLE[0])] + [i for i, x in enumerate(l) if x != DATA_STYLE[0]]
    fig.legend([h[i] for i in order], [l[i] for i in order], loc="upper center", ncol=len(l), frameon=False,
               bbox_to_anchor=(0.5, 1.0), handlelength=1.8, columnspacing=1.2)
    fig.text(0.01, 0.875, r"MINERvA ME FHC, $1.06\times10^{21}$ POT", ha="left", va="bottom", color="0.35")
    fig.align_ylabels(axs[:, 0])
    fig.align_ylabels(axs[:, 1])
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.11, top=0.86, hspace=0.06, wspace=0.32)

    # ---- identity check: the figure holds the computed numbers
    for c, edges, dv, gv, _, _ in panels:
        for label, _, _, _ in GENS:
            st, pt, rs, rp, y, r, cen = drawn[(c, label)]
            assert np.array_equal(st.get_data().values, y / UNIT) and np.array_equal(st.get_data().edges, edges[:-1])
            assert np.array_equal(rs.get_data().values, r) and np.array_equal(rs.get_data().edges, edges[:-1])
            assert np.array_equal(np.asarray(pt.get_ydata(), float), y / UNIT) and np.array_equal(np.asarray(rp.get_ydata(), float), r)
            assert np.array_equal(np.asarray(pt.get_xdata(), float), cen)
        dp, dd, cen = drawn[(c, "data")]
        assert np.array_equal(np.asarray(dp.get_ydata(), float), dd / UNIT) and np.array_equal(np.asarray(dp.get_xdata(), float), cen)
    small = [(t.get_text(), t.get_fontsize()) for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_fontsize() < 7.0]
    assert not small, f"fonts under 7 pt: {small}"

    a.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out / "eavailW_band.pdf", metadata={"CreationDate": None})
    fig.savefig(a.out / "eavailW_band.png", dpi=200)
    vals = {
        "schema": "note-figfix-eavailw/1",
        "inputs": {"data": {"path": NPZ, "key": "data2d", "bytes_digest_sha256": npz_sha,
                            "made_from": {"path": SESSION, "data_input_sha256": DATA_SHA}},
                   "generators": {l: {"path": str((REC / f"runs/eavailw/inputs/{s}_xsec_eavailW.root").relative_to(REPO)),
                                      "bytes_digest_sha256": gsha[l], "archive_list": SUMS} for l, s, _, _ in GENS}},
        "panels": {"E_avail": drawn[(0, "rec")], "W": drawn[(1, "rec")]},
        "checks": checks,
        "identity_check": "every stairs, point and ratio equals the computed values",
    }
    (a.out / "eavailW_band_values.json").write_text(json.dumps(vals, indent=1) + "\n")
    print("wrote", a.out / "eavailW_band.pdf", "; W-mid (GENIE-CV, GENIE+MEC) %:",
          ", ".join(f"{v:.2f}" for v in pct.values()), f"(printed {lo}-{hi})")


if __name__ == "__main__":
    main()
