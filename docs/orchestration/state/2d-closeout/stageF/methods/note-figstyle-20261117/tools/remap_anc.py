#!/usr/bin/env python3
"""Run a 2D figure producer on the laptop with the published covariance's directory remapped (tier 2, the note palette).

usage: python3 remap_anc.py <local anc dir> <script> [args...]

The producers name the published measurement's ancillary directory by its cluster path,
compare_to_paper_fullcov.ANC_DIR = /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc (it is not
an argument). Before the producer runs (runpy, as __main__, sys.argv = [script, *args]), ROOT.TFile.Open, builtins.open
and os.path.exists are wrapped so that a path under that prefix is read from <local anc dir> instead. Nothing else is
remapped, and not one producer byte changes. <local anc dir> must hold:
  cov_ptpl_minerva_inclusive_6GeV.root with sha256 6c6dce72... (the read-only fetch of 2026-11-17, figfetch/er-anc), and
  the repository's committed 2d-unfolding/minerva_paper_anc/*.txt, byte-equal (checked here against this worktree).
"""
import builtins
import hashlib
import os
import runpy
import sys
from pathlib import Path

PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
COV_SHA = "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3"
ROOT_DIR = Path(__file__).resolve().parents[8]
local, script, args = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3:]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


if sha(local / "cov_ptpl_minerva_inclusive_6GeV.root") != COV_SHA:
    sys.exit("remap_anc: the local covariance is not the pinned 6c6dce72")
for t in sorted((ROOT_DIR / "2d-unfolding/minerva_paper_anc").glob("*.txt")):
    if not (local / t.name).is_file() or sha(local / t.name) != sha(t):
        sys.exit(f"remap_anc: {t.name} in {local} is not the committed copy")


def remap(p):
    s = os.fspath(p) if hasattr(p, "__fspath__") or isinstance(p, (str, bytes)) else p
    if isinstance(s, str) and s.startswith(PREFIX):
        return str(local) + s[len(PREFIX):]
    return p


_open, _exists = builtins.open, os.path.exists
builtins.open = lambda f, *a, **k: _open(remap(f), *a, **k)
os.path.exists = lambda p: _exists(remap(p))
try:
    import ROOT
    _tfo = ROOT.TFile.Open
    ROOT.TFile.Open = lambda name, *a, **k: _tfo(remap(name), *a, **k)
except ImportError:
    pass
sys.argv = [str(script), *args]
sys.path.insert(0, str(script.parent))
runpy.run_path(str(script), run_name="__main__")
