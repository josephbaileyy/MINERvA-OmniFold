#!/usr/bin/env python3
"""checks.py: every check of note-figfonts-20261128, rerun from the arms' scratch directories (README.md, "Checks").

usage: python3 checks.py <runs root R> <worktree W> <base commit> > runs/CHECKS.txt

R holds the arms (README.md, "Arms"): arm0, arm1 (regenA4_run.sh before and after the PRINT_FONT change), armc
(run_tension_c.sh), eav0 (run_eavail.sh f17 0), eav1 (run_eavail.sh main 1), nw0, nw1 (run_negweight.sh PRINT_STYLE=0/1).
W is a worktree of the repository; the files installed before this record are read from <base commit> (02ae86003006,
the branch's base) with git show. values.tex is read from W. Needs numpy (capture npz) and poppler (pdffonts,
pdftotext). Ends with CHECKS :: PASS or FAIL; exit 1 on FAIL.
"""
import collections
import json
import re
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R, W, BASE = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
F = Path(tempfile.mkdtemp(prefix="figfonts-base-"))   # the figures as installed at BASE
for _n in ["MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz", "MEFHC_5iter_pull_full", "MEFHC_5iter_xsec_paper_pt_slices",
           "MEFHC_5iter_xsec_paper_pz_slices", "tension_spectrum", "tension_chi2_map", "tension_mode_maps",
           "eavail_marginal_vs_paper_pull_full", "negweight_ratio_2d"]:
    (F / f"{_n}.pdf").write_bytes(subprocess.run(["git", "-C", str(W), "show", f"{BASE}:docs/analysis-note/figures/{_n}.pdf"],
                                                 capture_output=True, check=True).stdout)
print(f"# base {BASE} ({subprocess.run(['git', '-C', str(W), 'rev-parse', BASE], capture_output=True, text=True).stdout.strip()})")
PY = sys.executable
FAIL = []


def run(*a):
    p = subprocess.run([str(x) for x in a], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def check(name, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")
    if not ok:
        FAIL.append(name)


def tool(t, *a):
    return run(PY, "-I", HERE / t, *a)


def fonts(pdf):
    out = run("pdffonts", pdf)[1].splitlines()[2:]
    return [(l.split()[0].split("+")[-1], " ".join(l.split()[1:3])) for l in out if l.strip()]


def texts(cap, name):
    d = json.loads((cap / f"{name}.texts").read_text())
    s = [t[0] for t in d["texts"]]
    return d["size_in"], min(s), statistics.median(s)


A = {  # (a): name -> (arm output path under arm0/arm1, capture subdir)
    "MEFHC_5iter_xsec_proj_pt": ("fig2/out", "fig2"), "MEFHC_5iter_xsec_proj_pz": ("fig2/out", "fig2"),
    "MEFHC_5iter_pull_full": ("fig3/o", "fig3"),
    "MEFHC_5iter_xsec_paper_pt_slices": ("sl/strip", "sl"), "MEFHC_5iter_xsec_paper_pz_slices": ("sl/strip", "sl"),
    "tension_spectrum": ("tn/o", "tn"), "tension_chi2_map": ("tn/o", "tn"), "tension_mode_maps": ("tn/o", "tn"),
}
print("== (a) arm 0 (regenA4_run.sh at W, PRINT_FONT unchanged) against the installed file, date masked")
for n, (o, _) in A.items():
    rc, out = tool("equal_mod_date.py", R / "arm0" / o / f"{n}.pdf", F / f"{n}.pdf")
    check(f"arm0 {n}", rc == 0, out)
print("== (a) arm 1 (PRINT_FONT + pdf.fonttype 42) against arm 0: arrays, artist index, texts (sizes included)")
for n, (o, c) in A.items():
    rc, out = tool("compare_captures.py", "--texts", R / "arm0/cap" / c, R / "arm1/cap" / c, f"{n}.pdf")
    check(f"arm1 {n}", rc == 0, out)
    ft = fonts(R / "arm1" / o / f"{n}.pdf")
    check(f"arm1 {n} fonts", all(t == "CID TrueType" for _, t in ft), ", ".join(f"{f} {t}" for f, t in ft))

print("== (c) tension_spectrum, tension_chi2_map at about 8 pt (run_tension_c.sh) against arm 1")
for n in ("tension_spectrum", "tension_chi2_map"):
    rc, out = tool("compare_captures.py", R / "arm1/cap/tn", R / "armc/cap/tn", f"{n}.pdf")
    check(f"armc {n} data and strings", rc == 0, out)
    (w, h), lo, med = texts(R / "armc/cap/tn", f"{n}.pdf")
    (w0, h0), lo0, med0 = texts(R / "arm1/cap/tn", f"{n}.pdf")
    check(f"armc {n} sizes", lo >= 8.0 and w == 3.185,
          f"canvas {w0} x {h0} in -> {w} x {h} in; text min/median {lo0}/{med0} pt -> {lo}/{med} pt (printed at 3.185 in)")
    rc, out = tool("pdf_text_overlaps.py", R / "armc/tn/o" / f"{n}.pdf")
    check(f"armc {n} overlaps (saved file)", rc == 0, out)
rc, out = tool("compare_captures.py", "--texts", R / "arm1/cap/tn", R / "armc/cap/tn", "tension_mode_maps.pdf")
check("armc tension_mode_maps unchanged", rc == 0, out)
rc, out = tool("equal_mod_date.py", R / "arm1/tn/o/tension_mode_maps.pdf", R / "armc/tn/o/tension_mode_maps.pdf")
check("armc tension_mode_maps file", rc == 0, out)

print("== (b) eavail_marginal_vs_paper_pull_full (run_eavail.sh)")
n = "eavail_marginal_vs_paper_pull_full"
rc, out = tool("equal_mod_date.py", R / "eav0/strip" / f"{n}.pdf", F / f"{n}.pdf")
check("eav0 (HOUSEFONT=0) against the installed file", rc == 0, out)
rc, out = tool("compare_captures.py", R / "eav0/cap", R / "eav1/cap", f"{n}.pdf")
c0 = collections.Counter(t[1] for t in json.loads((R / "eav0/cap" / f"{n}.pdf.texts").read_text())["texts"])
c1 = collections.Counter(t[1] for t in json.loads((R / "eav1/cap" / f"{n}.pdf.texts").read_text())["texts"])
gone, new = sorted((c0 - c1).elements()), sorted((c1 - c0).elements())
# Fig. 3's labels (main's producer since 430b42db2): the heat map's axis labels and its tick labels at the boundaries
# 0, 5, 10, 14 (pT) and every second one (p_par), in GeV/c; nothing else
# and the statistics box's "rms =" -> "rms=" (housefont_run.py HOUSE_TEXTS; the capture shows the box's newlines as spaces)
WANT_GONE = ["$p_T$ bin", "$p_\\parallel$ bin", "0", "10", "12", "12", "14", "14", "16", "2", "2", "4", "4", "6", "8",
             "mean=0.16 rms =0.83 $\\chi^2$/ndf paper = 4.98"]
WANT_NEW = ["$p_T$ (GeV/c)", "$p_\\parallel$ (GeV/c)", "0.4", "1", "1.5", "2.5", "20", "3.5", "4.5", "4.5", "60",
            "mean=0.16 rms=0.83 $\\chi^2$/ndf paper = 4.98"]
check("eav1 (main's producer, HOUSEFONT=1) against eav0: arrays and artist index equal; the only string changes are the "
      "heat map's axis and tick labels, now Fig. 3's (GeV/c), and the statistics box's rms= ",
      out.startswith("DIFFER (drawn strings)") and gone == WANT_GONE and new == WANT_NEW,
      f"{out}; removed {gone}; added {new}")
for arm in ("eav0", "eav1"):
    log = (R / arm / "log.txt").read_text()
    m = re.search(r"PAPER \(stat\+syst\)\s+chi2 =\s+([\d.]+)\s+ndf = (\d+)\s+chi2/ndf =\s+([\d.]+)", log)
    p = re.search(r"pull mean / rms\s*:\s*([\d.-]+) / ([\d.]+)", log)
    check(f"{arm} printed values", bool(m and p) and (m.group(3), p.group(1), p.group(2)) == ("4.981", "0.159", "0.828"),
          f"chi2/ndf {m and m.group(3)}, mean/rms {p and p.group(1)}/{p and p.group(2)}")
ft = fonts(R / "eav1/strip" / f"{n}.pdf")
check("eav1 fonts: no sans, no Type 3", all("Sans" not in f and t == "CID TrueType" for f, t in ft),
      ", ".join(f"{f} {t}" for f, t in ft))
rc, out = tool("pdf_text_overlaps.py", R / "eav1/strip" / f"{n}.pdf")
check("eav1 overlaps (saved file)", rc == 0, out)

print("== (b) negweight_ratio_2d (run_negweight.sh, on the fetched inputs)")
n = "negweight_ratio_2d"
w0 = run("pdftotext", "-raw", R / "nw0/o" / f"{n}.pdf", "-")[1].split()
wi = run("pdftotext", "-raw", F / f"{n}.pdf", "-")[1].split()
check("nw0 (default) against the installed file: the same words", w0 == wi, f"{len(w0)} words")
s0 = run("pdfinfo", R / "nw0/o" / f"{n}.pdf")[1]; si = run("pdfinfo", F / f"{n}.pdf")[1]
pg = lambda s: re.search(r"Page size:\s+(.*)", s).group(1)
check("nw0 against the installed file: page size", pg(s0) == pg(si), pg(s0))
print("  info nw0 is not byte-equal to the installed file (2026-07-14, 4e8033eef; no reproduction record): its colour "
      "bar and tick labels sit about 1.8 pt to the right (pdftotext -bbox); words, page size and the map are the same")
rc, out = tool("compare_captures.py", R / "nw0/cap", R / "nw1/cap", f"{n}.pdf")
s0 = collections.Counter(t[1] for t in json.loads((R / "nw0/cap" / f"{n}.pdf.texts").read_text())["texts"])
s1 = collections.Counter(t[1] for t in json.loads((R / "nw1/cap" / f"{n}.pdf.texts").read_text())["texts"])
gone, new = sorted((s0 - s1).elements()), sorted((s1 - s0).elements())
check("nw1 (--print-style) against nw0: arrays and artist index equal; the only string changes are the two axis labels",
      out.startswith("DIFFER (drawn strings)") and gone == ["p$_T$ (GeV/c)", "p$_{||}$ (GeV/c)"]
      and new == ["$p_T$ (GeV/$c$)", "$p_\\parallel$ (GeV/$c$)"], f"{out}; removed {gone}; added {new}")
z = np.load(R / "nw1/cap" / f"{n}.pdf.npz")
r = np.ma.array(z["i0.array"], mask=z["i0.array.mask"]).compressed()
got = {"nwMedianBin": f"{np.median(r):.3f}", "nwRmsBin": f"{100 * np.sqrt(np.mean((r - 1) ** 2)):.1f}",
       "nwWorstBin": f"{100 * (r - 1)[np.argmax(abs(r - 1))]:.1f}"}
vt = (W / "docs/analysis-note/values.tex").read_text()
want = {k: re.search(r"\\newcommand\{\\" + k + r"\}\{([^}]*)\}", vt).group(1) for k in got}
check("nw1 plotted ratio against values.tex", got == want, f"{len(r)} bins; from the plot {got}; values.tex {want}")
ft = fonts(R / "nw1/o" / f"{n}.pdf")
check("nw1 fonts: no sans, no Type 3", all("Sans" not in f and t == "CID TrueType" for f, t in ft),
      ", ".join(f"{f} {t}" for f, t in ft))
rc, out = tool("pdf_text_overlaps.py", R / "nw1/o" / f"{n}.pdf")
check("nw1 overlaps (saved file)", rc == 0, out)

print(f"CHECKS :: {'PASS' if not FAIL else 'FAIL'}" + (f" ({len(FAIL)}: {FAIL})" if FAIL else ""))
sys.exit(1 if FAIL else 0)
