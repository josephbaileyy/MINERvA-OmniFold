#!/usr/bin/env python3
"""Enumerate universe weight branches in an omnifile, emit BAND:IDX list.

Reads w_truth_<band>_<idx> branches from mc_truth_denom and writes one
"BAND:IDX" per line to the output file, sorted by (band, idx). The
sbatch full-universe sweep arrays consume this list via sed -n.

Usage:
  python uq/gen_universe_list.py [OMNIFILE] [OUT_FILE]

Defaults:
  OMNIFILE = runEventLoopOmniFold_MEFHC_universes_full.root  (cwd-relative)
  OUT_FILE = uq/universes_full_list.txt                       (cwd-relative)
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict

import ROOT

ROOT.gROOT.SetBatch(True)


def main():
    omnifile = sys.argv[1] if len(sys.argv) > 1 \
        else "runEventLoopOmniFold_MEFHC_universes_full.root"
    out_path = sys.argv[2] if len(sys.argv) > 2 \
        else "uq/universes_full_list.txt"

    f = ROOT.TFile.Open(omnifile)
    if not f or f.IsZombie():
        sys.exit(f"[FAIL] cannot open {omnifile}")
    t = f.Get("mc_truth_denom")
    if not t:
        sys.exit(f"[FAIL] no mc_truth_denom tree in {omnifile}")

    bands: dict[str, list[int]] = defaultdict(list)
    pat = re.compile(r"^w_truth_(.+)_(\d+)$")
    for b in t.GetListOfBranches():
        m = pat.match(b.GetName())
        if m:
            bands[m.group(1)].append(int(m.group(2)))
    for v in bands.values():
        v.sort()

    total = sum(len(v) for v in bands.values())
    with open(out_path, "w") as fo:
        for band in sorted(bands):
            for idx in bands[band]:
                fo.write(f"{band}:{idx}\n")

    print(f"[gen_universe_list] {omnifile}")
    print(f"[gen_universe_list] {len(bands)} bands, {total} (band,idx) entries")
    for band in sorted(bands):
        print(f"  {band:<28} n={len(bands[band])}")
    print(f"[gen_universe_list] wrote {out_path}")


if __name__ == "__main__":
    main()
