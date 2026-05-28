#!/usr/bin/env python3
"""Merge 12 per-playlist _universes_full ROOTs into one MEFHC omnifile.

Drop-in replacement for `hadd -f` when the merged TTree would exceed
ROOT's 100 GB auto-rollover limit. Bumps `TTree::SetMaxTreeSize` to
300 GB so the merger does not split files mid-merge.

Usage:
  python uq/hadd_universes_full.py [OUT] [INPUT...]

Defaults: OUT = runEventLoopOmniFold_MEFHC_universes_full.root
          INPUT = runEventLoopOmniFold_1{A,B,C,D,E,F,G,L,M,N,O,P}_universes_full.root
"""
from __future__ import annotations

import sys
import time

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.TTree.SetMaxTreeSize(int(300e9))


DEFAULT_PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F",
                     "1G", "1L", "1M", "1N", "1O", "1P"]


def main():
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
        inputs = sys.argv[2:] or [
            f"runEventLoopOmniFold_{pl}_universes_full.root"
            for pl in DEFAULT_PLAYLISTS
        ]
    else:
        out_path = "runEventLoopOmniFold_MEFHC_universes_full.root"
        inputs = [
            f"runEventLoopOmniFold_{pl}_universes_full.root"
            for pl in DEFAULT_PLAYLISTS
        ]

    merger = ROOT.TFileMerger(False)
    merger.SetFastMethod(True)
    if not merger.OutputFile(out_path, "RECREATE", 1):
        sys.exit(f"[FAIL] cannot create {out_path}")

    print(f"[hadd] target: {out_path}")
    print(f"[hadd] max tree size: {ROOT.TTree.GetMaxTreeSize() / 1e9:.1f} GB")
    for f in inputs:
        print(f"[hadd] + {f}")
        if not merger.AddFile(f):
            sys.exit(f"[FAIL] cannot add input {f}")

    t0 = time.time()
    mode = (ROOT.TFileMerger.kAll | ROOT.TFileMerger.kRegular
            | ROOT.TFileMerger.kIncremental)
    if not merger.PartialMerge(mode):
        sys.exit(f"[FAIL] PartialMerge returned False on {out_path}")
    dt = time.time() - t0
    print(f"[hadd] merge complete in {dt/60:.1f} min -> {out_path}")


if __name__ == "__main__":
    main()
