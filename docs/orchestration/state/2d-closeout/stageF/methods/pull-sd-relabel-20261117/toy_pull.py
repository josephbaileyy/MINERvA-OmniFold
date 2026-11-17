#!/usr/bin/env python3
"""Test stand-in for compare_to_paper_fullcov.py (test_check_sd.sh and test_connect_sd.sh only; never on the cluster).

usage (as the producer, through boxes.py): toy_pull.py --ours FILE --out-prefix PREFIX [--style restyle-2026-10]
                                           [--sd-label]
It needs no ROOT. It reads FILE whole (so capture.py records it), takes the pull map and the 205 pull values from
run-a2's committed capture of the installed figure (fig-restyle-20261031/run-a2/after/capture/pull_full), and runs the
plotting block of the compare_to_paper_fullcov.py it finds first on sys.path (the deploy's, which boxes.py and
capture.py put there), from "# Summary plot." up to the save, unchanged, then saves PREFIX_pull_full.png as the
producer does and prints the producer's run-log summary lines. TOY_MUT, for the tests' mutants:
  ulp     the first pull value one ulp up          xlabel  the histogram's x label changed
  move    the headline box moved right             log     one more line in the log"""
import argparse
import json
import os
import sys
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CAP = HERE.parent / "fig-restyle-20261031/run-a2/after/capture/pull_full"
ap = argparse.ArgumentParser()
ap.add_argument("--ours", required=True)
ap.add_argument("--out-prefix", required=True)
ap.add_argument("--style", default=None)
ap.add_argument("--sd-label", action="store_true")
args = ap.parse_args()
Path(args.ours).read_bytes()
mut = os.environ.get("TOY_MUT", "")
src = next(Path(p) / "compare_to_paper_fullcov.py" for p in sys.path if (Path(p) / "compare_to_paper_fullcov.py").is_file())
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import restyle_2026_10 as rs  # noqa: E402
import technote_style  # noqa: E402

idx = json.loads((CAP / "MEFHC_5iter_pull_full.png.json").read_text())
z = np.load(CAP / "MEFHC_5iter_pull_full.png.npz")
(hin,) = [it["i"] for it in idx if it["kind"] == "hist-input"]
(key,) = [k for k in z.keys() if k.startswith(f"i{hin}.")]
pull = np.array(z[key], float)
if mut == "ulp":
    pull[0] = np.nextafter(pull[0], np.inf)
pull_map = np.ma.masked_array(z["i0.array"], z["i0.array.mask"]).T.filled(np.nan)
text = src.read_text()
a, b = text.index("    # Summary plot."), text.index('    out = f"{OUT_PREFIX}_pull_full.png"')
env = dict(restyled=args.style == rs.STYLE, rs=rs, plt=plt, np=np, pull_map=pull_map, N_PT=14, N_PZ=16, pull=pull,
           mask=np.ones(pull.size, bool), chi2_tot=465.42, ndf_stat=205, chi2_combined=None,
           technote_style=technote_style, args=types.SimpleNamespace(**vars(args)))
exec("\n".join(line[4:] for line in text[a:b].splitlines()), env)
fig, axs = env["fig"], env["axs"]
if mut == "xlabel":
    axs[1].set_xlabel("Standardized diff.")
if mut == "move":
    axs[1].texts[0].set_position((0.06, 0.95))
out = f"{args.out_prefix}_pull_full.png"
fig.savefig(out, dpi=130)
print(f"\nwrote {out}")
mu, sd = pull.mean(), pull.std()
print("\nSummary for run log:")
print(f"  reported bins: {pull.size}")
print(f"  chi^2/ndf  PAPER (full cov) : {465.42 / 205:.3f}")
print(f"  pull mean / rms             : {mu:.3f} / {sd:.3f}")
if mut == "log":
    print("  one more line")
