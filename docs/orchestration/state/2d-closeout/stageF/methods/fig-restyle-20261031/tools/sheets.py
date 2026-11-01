#!/usr/bin/env python3
"""Side-by-side review sheets for Joseph (DECLARATION.md §5.1): one PDF per figure, old on the left, new on the right.

usage: python3 -I sheets.py OLD_DIR NEW_DIR DEPLOY OUT_DIR
OLD_DIR holds the committed copies (re2-integration/figs/), NEW_DIR the bound run's "after" PDFs (run/after/out/).
Each sheet places both PDFs, as vector graphics, at the width the note prints the figure (restyle_2026_10.WIDTH, from
DEPLOY/2d-unfolding), so that the sheet shows them at print scale. It is built with pdflatex. Writes
OUT_DIR/<figure>.pdf for the eleven figures and OUT_DIR/SHA256SUMS. Exit 1 if a PDF is missing, a build fails or a
sheet is not one page.
RESTYLE AMENDMENT 2: where red changes meaning between the two copies, the sheet's header says so (NOTE)."""
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

old, new, deploy, out = (Path(a).resolve() for a in sys.argv[1:5])
sys.path.insert(0, str(deploy / "2d-unfolding"))
import restyle_2026_10 as rs  # noqa: E402

FIGS = [("MEFHC_5iter_fig13", "fig13", "Fig. 7 (top); also the primer"), ("MEFHC_5iter_xsec_proj_pt", "proj", "Fig. 7 (bottom left)"),
        ("MEFHC_5iter_xsec_proj_pz", "proj", "Fig. 7 (bottom right)"), ("MEFHC_5iter_pull_full", "pull_full", "Fig. 8"),
        ("MEFHC_5iter_xsec_paper_pt_slices", "slices", "Fig. 9"), ("MEFHC_5iter_xsec_paper_pz_slices", "slices", "Fig. 10"),
        ("tension_spectrum", "spectrum", "Fig. 11 (left)"), ("tension_chi2_map", "chi2_map", "Fig. 11 (right)"),
        ("tension_mode_maps", "mode_maps", "Fig. 12"), ("model_comp_projections", "projections", "Fig. 13"),
        ("model_comp_ratio_maps", "ratio_maps", "Fig. 14")]
# RESTYLE AMENDMENT 2: the committed fig13 and p_T, p_parallel projections draw Tune v1 in red; the amended ones draw
# This work (OmniFold) in red (AMENDMENT-2.md section 2)
RED = "Red means Tune v1 on the left (the committed copy) and This work (OmniFold) on the right."
NOTE = {"MEFHC_5iter_fig13": RED, "MEFHC_5iter_xsec_proj_pt": RED, "MEFHC_5iter_xsec_proj_pz": RED}


def page(pdf):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    w, h = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+)", info).groups()
    return float(w), float(h)


def main():
    out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for stem, key, where in FIGS:
        a, b = old / f"{stem}.pdf", new / f"{stem}.pdf"
        if not (a.is_file() and b.is_file()):
            print(f"MISSING {stem}"); bad += 1; continue
        w = rs.WIDTH[key]
        hs = [w * page(p)[1] / page(p)[0] for p in (a, b)]
        tex = rf"""\documentclass{{article}}
\usepackage[paperwidth={2 * w + 1.2:.3f}in,paperheight={max(hs) + 1.6:.3f}in,margin=0.4in]{{geometry}}
\usepackage{{graphicx}}\pagestyle{{empty}}\setlength{{\parindent}}{{0pt}}
\begin{{document}}\sffamily\footnotesize
{where}: \texttt{{{stem.replace('_', r'\_')}}}, at its printed width ({w:.2f} in)\par
{(r"\textbf{" + NOTE[stem] + "}") if stem in NOTE else ""}\par\medskip
\begin{{minipage}}[t]{{{w:.3f}in}}Before: the committed copy\par\smallskip\includegraphics[width={w:.3f}in]{{a.pdf}}\end{{minipage}}\hspace{{0.4in}}%
\begin{{minipage}}[t]{{{w:.3f}in}}After: \texttt{{-{{}}-style restyle-2026-10}}\par\smallskip\includegraphics[width={w:.3f}in]{{b.pdf}}\end{{minipage}}
\end{{document}}
"""
        with tempfile.TemporaryDirectory() as t:
            shutil.copy(a, Path(t) / "a.pdf")
            shutil.copy(b, Path(t) / "b.pdf")
            (Path(t) / "s.tex").write_text(tex)
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "s.tex"], cwd=t,
                               capture_output=True, text=True)
            info = subprocess.run(["pdfinfo", str(Path(t) / "s.pdf")], capture_output=True, text=True).stdout
            if r.returncode or not re.search(r"^Pages:\s+1$", info, re.M):
                print(f"BUILD FAILED {stem} (a sheet must be one page)"); bad += 1; continue
            shutil.copy(Path(t) / "s.pdf", out / f"{stem}.pdf")
        print(f"sheet {stem}.pdf ({where})")
    with open(out / "SHA256SUMS", "w") as f:
        for p in sorted(out.glob("*.pdf")):
            f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
