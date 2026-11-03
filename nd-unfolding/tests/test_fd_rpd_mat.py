#!/usr/bin/env python3
"""The RPD inputs' ROOT reads on the real staged files (binding 2 A1; FD-RPD-DECLARATION-PART2.md section 3): the
tested-language counterpart of test_fd_rpd.RootPaths' plain-TH1D fixtures. Login node only, with FD_RPD_R naming the
run directory; it reads <R>/staged only (each copy re-hashed against the staging record first) and writes nothing.

* ``Mat`` runs in flux's pinned MAT environment: mat_environment passes, and each staged baseline flux file's
  histogram is a PlotUtils::MnvH1D that the pinned combiner reads to finite, positive contents and POTs.
* ``ZeroLoops`` runs in both environments (the MAT one and root_6_28 by prefix, job A's): loop_pots reads all twelve
  staged zero loops to finite, positive POTs.

    FD_RPD_R=<R> python3 -B -m unittest test_fd_rpd_mat            (MAT environment)
    FD_RPD_R=<R> python3 -B -m unittest test_fd_rpd_mat.ZeroLoops  (root_6_28 by prefix)

Without FD_RPD_R, or without ROOT, every test errors rather than skips.
"""
import math
import os
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_rpd_inputs as ri  # noqa: E402


def run_dir() -> Path:
    r = os.environ.get("FD_RPD_R")
    if not r or not (Path(r) / "staged/STAGED.json").is_file():
        raise RuntimeError("FD_RPD_R must name a run directory with a staging record")
    return Path(r)


class Mat(unittest.TestCase):
    def test_the_environment_is_flux_s_pinned_one(self):
        env = ri.mat_environment()
        self.assertEqual(env["setup_sha256"], ri.MAT_SETUP)
        self.assertEqual(env["mat_sha256"], ri.MAT_FILES)
        self.assertEqual(env["symlink"], {ri.MAT_LINK[0]: ri.MAT_LINK[1]})
        self.assertTrue(env["plotutils_mnvh1d_dictionary"])

    def test_each_staged_flux_histogram_is_an_mnvh1d_the_pinned_combiner_reads(self):
        import ROOT
        R = run_dir()
        ri.mat_environment()
        for pl in ri.PLAYLISTS:
            for kind in ("MC", "Data"):
                ri.staged(R, f"baseline/runEventLoop{kind}_{pl}.root")
            f = ROOT.TFile.Open(str(R / f"staged/baseline/runEventLoopMC_{pl}.root"), "READ")
            self.assertEqual(f.Get(ri.HIST).ClassName(), "PlotUtils::MnvH1D", pl)
            f.Close()
        cf = ri.load_combiner(ri.DEPLOY, R / "staged/baseline")
        for pl in ri.PLAYLISTS:
            edges, contents, errors, pot_data, pot_mc = cf.read_playlist(pl)
            self.assertEqual(len(edges), len(contents) + 1, pl)
            self.assertTrue(all(math.isfinite(v) and v > 0 for v in contents), pl)
            self.assertTrue(all(math.isfinite(v) and v >= 0 for v in errors), pl)
            self.assertTrue(math.isfinite(pot_data) and pot_data > 0 and math.isfinite(pot_mc) and pot_mc > 0, pl)


class ZeroLoops(unittest.TestCase):
    def test_loop_pots_reads_all_twelve_staged_zero_loops(self):
        R = run_dir()
        for pl in ri.PLAYLISTS:
            p, _ = ri.staged(R, f"zero/runEventLoopOmniFold_5D_{pl}_zero.root")
            data_pot, mc_pot = ri.loop_pots(p)
            self.assertTrue(isinstance(data_pot, float) and isinstance(mc_pot, float), pl)
            self.assertTrue(math.isfinite(data_pot) and data_pot > 0 and math.isfinite(mc_pot) and mc_pot > 0, pl)


if __name__ == "__main__":
    unittest.main()
