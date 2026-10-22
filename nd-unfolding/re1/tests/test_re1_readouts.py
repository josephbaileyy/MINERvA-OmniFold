"""Tests for the RE-1 readouts: ``nd-unfolding/re1/re1_nd_movement.py`` and ``2d-unfolding/re1/re1_2d_analyze.py``.

Synthetic products only; needs PyROOT and numpy:
    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest nd-unfolding/re1/tests/test_re1_readouts.py -v
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "nd-unfolding" / "re1"))
sys.path.insert(0, str(REPO / "2d-unfolding" / "re1"))

try:
    import ROOT
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

if HAVE_ROOT:
    import re1_2d_analyze as A
    import re1_nd_movement as M


def nd_product(path, x, shape, bkg_mode, npz_sha, candidate=None, n_est=None):
    meta = {"bkg_mode": bkg_mode, "config": "deterministic", "data": True, "estimator_seed": 42,
            "input_npz_sha256": npz_sha, "code_sha256": {"candidate": candidate} if candidate else {},
            "refinement": ({"ran": True, "classifier_params": {"n_estimators": n_est, "num_leaves": 31},
                            "clipped_fraction": 1e-4, "refined_over_signed": 1.0} if candidate else {"ran": False})}
    np.savez(path, xsec_flat=x, shape=np.array(shape), meta=json.dumps(meta))


def flat_root(path, x, name="hXSecND_flat"):
    f = ROOT.TFile.Open(str(path), "RECREATE")
    h = ROOT.TH1D(name, "", x.size, 0, x.size)
    for i, v in enumerate(x, start=1):
        h.SetBinContent(i, float(v))
    h.Write()
    f.Close()


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Movement(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        self.shape = M.SHAPES[4]
        n = int(np.prod(self.shape))
        rng = np.random.default_rng(1)
        self.xa = rng.uniform(1, 2, n)
        self.xa[:10] = 0.0                                  # not reported
        self.xc = self.xa * 1.02
        self.xe = self.xa * 1.05
        edges = [np.linspace(0, 1, s + 1) for s in self.shape]
        self.npz = d / "in.npz"
        np.savez(self.npz, nedges=len(edges), **{f"edges_{i}": e for i, e in enumerate(edges)})
        sha = M.sha256_path(self.npz)
        self.e, self.c, self.cur = d / "e.npz", d / "c.npz", d / "cur.root"
        nd_product(self.e, self.xe, self.shape, "negweight-refined", sha, "R", 400)
        nd_product(self.c, self.xc, self.shape, "purity", sha)
        flat_root(self.cur, self.xa)
        self.out = d / "m.json"

    def tearDown(self):
        self.td.cleanup()

    def argv(self, **over):
        s = M.sha256_path
        args = {"--e": self.e, "--c": self.c, "--current": self.cur, "--edges-npz": self.npz,
                "--expect-e-sha256": s(self.e), "--expect-c-sha256": s(self.c), "--expect-current-sha256": s(self.cur),
                "--out": self.out}
        args.update(over)
        return ["--dim", "4"] + [str(v) for kv in args.items() for v in kv]

    def test_known_movement(self):
        self.assertEqual(M.main(self.argv()), 0)
        out = json.loads(self.out.read_text())
        self.assertEqual(out["n_cells_all_positive"], int(np.prod(self.shape)) - 10)
        self.assertAlmostEqual(out["e_minus_a"]["relative_percent"]["median_abs"], 5.0, places=9)
        self.assertAlmostEqual(out["e_minus_c"]["relative_percent"]["median_abs"], 100 * (1.05 / 1.02 - 1), places=9)
        self.assertAlmostEqual(out["c_minus_a"]["integral_change_percent"], 2.0, places=9)

    def test_refuses_wrong_digest(self):
        self.assertEqual(M.main(self.argv(**{"--expect-e-sha256": "0" * 64})), 4)

    def test_refuses_e_not_at_400_31(self):
        nd_product(self.e, self.xe, self.shape, "negweight-refined", M.sha256_path(self.npz), "R", 100)
        with self.assertRaisesRegex(RuntimeError, "400/31"):
            M.main(self.argv(**{"--expect-e-sha256": M.sha256_path(self.e)}))

    def test_refuses_swapped_arms(self):
        with self.assertRaisesRegex(RuntimeError, "bkg_mode"):
            M.main(self.argv(**{"--e": self.c, "--c": self.e, "--expect-e-sha256": M.sha256_path(self.c),
                                "--expect-c-sha256": M.sha256_path(self.e)}))

    def test_refuses_other_inputs(self):
        nd_product(self.c, self.xc, self.shape, "purity", "f" * 64)
        with self.assertRaisesRegex(RuntimeError, "different inputs"):
            M.main(self.argv(**{"--expect-c-sha256": M.sha256_path(self.c)}))

    def test_trunk_sigma_maps_by_row_index(self):
        d = Path(self.td.name)
        shape5 = M.SHAPES[5]
        n = int(np.prod(shape5))
        xa = np.random.default_rng(2).uniform(1, 2, n)
        rows = np.arange(0, n, 7)
        sig = np.linspace(0.1, 0.2, rows.size)
        trunk = d / "z.npz"
        np.savez(trunk, hRowIndex5D=rows, hCov_combined5d_total_uthrow=np.diag(sig ** 2), hXSecND_flat=xa)
        edges = [np.linspace(0, 1, s + 1) for s in shape5]
        npz = d / "in5.npz"
        np.savez(npz, nedges=5, **{f"edges_{i}": e for i, e in enumerate(edges)})
        sha = M.sha256_path(npz)
        e5, c5, cur5 = d / "e5.npz", d / "c5.npz", d / "cur5.root"
        delta = np.zeros(n)
        delta[rows] = 0.5 * sig
        nd_product(e5, xa + delta, shape5, "negweight-refined", sha, "R", 400)
        nd_product(c5, xa, shape5, "purity", sha)
        flat_root(cur5, xa)
        s = M.sha256_path
        rc = M.main(["--dim", "5", "--e", str(e5), "--c", str(c5), "--current", str(cur5), "--edges-npz", str(npz),
                     "--expect-e-sha256", s(e5), "--expect-c-sha256", s(c5), "--expect-current-sha256", s(cur5),
                     "--trunk", str(trunk), "--expect-trunk-sha256", s(trunk), "--out", str(self.out)])
        self.assertEqual(rc, 0)
        out = json.loads(self.out.read_text())
        self.assertTrue(out["trunk_central_equals_current"])
        z = out["e_minus_c_on_trunk_support"]["in_trunk_total_sigma"]
        self.assertAlmostEqual(z["median_abs"], 0.5, places=12)
        self.assertAlmostEqual(z["max_abs"], 0.5, places=12)
        self.assertEqual(out["n_cells_on_trunk_support"], rows.size)


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class TwoD(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        d = Path(self.td.name)
        rng = np.random.default_rng(3)
        self.eu = rng.uniform(1, 2, (14, 16))
        self.eu[0, :3] = 0.0
        cells = np.flatnonzero(self.eu.ravel() > 0)
        n = cells.size
        self.cells = cells
        self.sig_stat = np.full(n, 0.01)
        self.sig_tot = np.full(n, 0.05)
        self.cov = d / "cov.npz"
        self.q = d / "q.npz"
        area = np.ones(n)
        np.savez(self.cov, cells_x_EU=self.eu.ravel()[cells], area=area, stat=np.diag(self.sig_stat ** 2),
                 total=np.diag((0.04 * np.ones(n)) ** 2))
        np.savez(self.q, cells_x_EU=self.eu.ravel()[cells], area=area, total_plus_C_PL=np.diag(self.sig_tot ** 2))
        self.eu_root = d / "eu.root"
        f = ROOT.TFile.Open(str(self.eu_root), "RECREATE")
        h = ROOT.TH2D("hXSec2D", "", 14, 0, 14, 16, 0, 16)
        for i in range(14):
            for j in range(16):
                h.SetBinContent(i + 1, j + 1, self.eu[i, j])
        h.Write()
        f.Close()
        self.d = d

    def tearDown(self):
        self.td.cleanup()

    def base(self):
        s = A.sha256_path
        return ["--eu", str(self.eu_root), "--cov", str(self.cov), "--q", str(self.q),
                "--expect-eu-sha256", s(self.eu_root), "--expect-cov-sha256", s(self.cov),
                "--expect-q-sha256", s(self.q), "--out", str(self.d / "r.json")]

    def test_k1_pass_and_fail(self):
        k = self.d / "k1.npz"
        np.savez(k, xsec=self.eu)
        self.assertEqual(A.main(self.base() + ["--k1", str(k)]), 0)
        self.assertEqual(json.loads((self.d / "r.json").read_text())["k1"]["verdict"], "PASS")
        bad = self.eu.copy()
        bad[5, 5] *= 1 + 2e-8
        np.savez(k, xsec=bad)
        A.main(self.base() + ["--k1", str(k)])
        self.assertEqual(json.loads((self.d / "r.json").read_text())["k1"]["verdict"], "FAIL")

    def write_seeds(self, shift_cell=None, shift=0.0, scale=1.0):
        pdir = self.d / "c2"
        pdir.mkdir(exist_ok=True)
        rng = np.random.default_rng(4)
        for s in range(1, 21):
            xt = self.eu.copy()
            xp = xt + rng.normal(0, 0.01, xt.shape)
            xr = xp.copy() * scale
            if shift_cell is not None:
                xr.ravel()[shift_cell] += shift
            np.savez(pdir / f"nominal_s{s}.npz", xtrue=xt, xsec_purity=xp, xsec_refined=xr,
                     meta=json.dumps({"pseudo_seed": s}))
        return pdir

    def test_c2_no_flag_and_flags(self):
        p = self.write_seeds()
        A.main(self.base() + ["--pseudo-dir", str(p), "--seeds", "1:20"])
        out = json.loads((self.d / "r.json").read_text())["c2"]
        self.assertEqual(out["verdict"], "NO-FLAG")
        self.assertEqual(out["arm_difference"]["in_stat_sigma"]["max_abs"], 0.0)
        p = self.write_seeds(shift_cell=int(self.cells[7]), shift=0.011)   # 1.1 stat sigma in one cell
        A.main(self.base() + ["--pseudo-dir", str(p), "--seeds", "1:20"])
        out = json.loads((self.d / "r.json").read_text())["c2"]
        self.assertEqual(out["verdict"], "FLAG")
        self.assertEqual(out["flags"][0]["globalids"], [int(self.cells[7])])
        p = self.write_seeds(scale=1.006)                                   # +0.6 % everywhere
        A.main(self.base() + ["--pseudo-dir", str(p), "--seeds", "1:20"])
        out = json.loads((self.d / "r.json").read_text())["c2"]
        self.assertIn("0.5 %", " ".join(f["rule"] for f in out["flags"]))

    def test_refuses_cells_that_do_not_match_the_covariance(self):
        np.savez(self.q, cells_x_EU=self.eu.ravel()[self.cells] * 1.0000001, area=np.ones(self.cells.size),
                 total_plus_C_PL=np.diag(self.sig_tot ** 2))
        s = A.sha256_path
        argv = self.base()
        argv[argv.index("--expect-q-sha256") + 1] = s(self.q)
        with self.assertRaisesRegex(RuntimeError, "cells_x_EU"):
            A.main(argv)


if __name__ == "__main__":
    unittest.main()
