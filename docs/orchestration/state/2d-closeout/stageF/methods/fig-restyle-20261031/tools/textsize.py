#!/usr/bin/env python3
"""Printed text sizes of a run's figures (DECLARATION.md §5.4, as amended): what each figure draws, scaled to print.

usage: python3 -I textsize.py RUN_DIR DEPLOY [--floor PT]
For every capture/<step>/<figure>.textsizes.tsv (capture.py: each drawn text's font size), the printed size is the font
size times the figure's printed width over the saved PDF's page width (RUN_DIR/out/<figure>.pdf, read with pdfinfo).
The printed widths are restyle_2026_10.WIDTH, imported from DEPLOY/2d-unfolding. A figure with no printed width (not
one of the note's Figs. 7-14) is skipped. Mathtext sub- and superscripts are drawn at about 0.7 of their text's size and
are not listed separately. Prints each figure's smallest and median printed size and its smallest text; with --floor,
exits 1 if any figure's smallest printed size is below PT."""
import re
import subprocess
import sys
from pathlib import Path

run, deploy = Path(sys.argv[1]), Path(sys.argv[2])
floor = float(sys.argv[sys.argv.index("--floor") + 1]) if "--floor" in sys.argv else None
sys.path.insert(0, str(deploy / "2d-unfolding"))
import restyle_2026_10 as rs  # noqa: E402

KEY = {"MEFHC_5iter_fig13": "fig13", "MEFHC_5iter_xsec_proj_pt": "proj", "MEFHC_5iter_xsec_proj_pz": "proj",
       "MEFHC_5iter_pull_full": "pull_full", "MEFHC_5iter_xsec_paper_pt_slices": "slices",
       "MEFHC_5iter_xsec_paper_pz_slices": "slices", "tension_spectrum": "spectrum", "tension_chi2_map": "chi2_map",
       "tension_mode_maps": "mode_maps", "model_comp_projections": "projections", "model_comp_ratio_maps": "ratio_maps"}
bad = 0
for tsv in sorted(run.glob("capture/*/*.textsizes.tsv")):
    stem = tsv.name[:-len(".png.textsizes.tsv")]
    if stem not in KEY:
        continue
    info = subprocess.run(["pdfinfo", str(run / "out" / f"{stem}.pdf")], capture_output=True, text=True).stdout
    page_w = float(re.search(r"Page size:\s+([0-9.]+) x", info).group(1))
    scale = rs.WIDTH[KEY[stem]] * 72 / page_w
    rows = [l.split("\t", 1) for l in tsv.read_text().splitlines() if not l.startswith("#")]
    sizes = sorted((float(s) * scale, x) for s, x in rows)
    lo, med = sizes[0], sizes[len(sizes) // 2][0]
    fail = floor is not None and lo[0] < floor
    bad += fail
    print(f"{'FAIL' if fail else 'ok  '} {stem:34s} texts {len(sizes):4d}  min {lo[0]:5.2f} pt  median {med:5.2f} pt"
          f"  smallest {lo[1][:40]!r}")
if floor is not None:
    print("TEXTSIZE ::", "PASS" if not bad else f"FAIL ({bad})", f"(floor {floor} pt)")
sys.exit(1 if bad else 0)
