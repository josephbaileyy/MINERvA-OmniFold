"""The 2D reported-cell identity contract (uq/reported_cells.py).

A covariance over "the reported bins" is ordered by the sorted flat indices of
its cells. Two of them may be added, or embedded in the 224-cell grid, only
when those index sets are equal; an equal count with one different cell
misaligns every later element without changing any shape.

The grid tests compare the contract with two copies it must not be derived
from: the driver's own literal (read from its source, not imported) and the
paper's bin_mapping.txt. The ROOT tests are skipped when PyROOT is
unavailable. Locally:
  PYTHONPATH=$(root-config --libdir) python3.13 -m unittest \
      2d-unfolding/tests/test_reported_cells.py -v
"""
import ast
import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
U2D_DIR = HERE.parents[1]
UQ_DIR = U2D_DIR / "uq"
ANC = U2D_DIR / "minerva_paper_anc"
sys.path.insert(0, str(UQ_DIR))
import reported_cells as rc  # noqa: E402

try:
    import ROOT
    ROOT.gROOT.SetBatch(True)
except ImportError:
    ROOT = None


def literal_assignments(path):
    """Top-level NAME = <literal> assignments of a source file, without importing it."""
    out = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


def paper_stat_mask():
    diag = np.zeros(rc.N_CELLS)
    with open(ANC / "cov_ptpl_minerva_inclusive_6GeV_stat.txt") as f:
        r = csv.reader(f)
        next(r)
        for i, j, v in r:
            if i == j:
                diag[int(i)] = float(v)
    return diag > 0


class GridTest(unittest.TestCase):
    def test_edges_equal_the_driver_literal(self):
        drv = literal_assignments(U2D_DIR / "unfold_2d_omnifold_unbinned.py")
        np.testing.assert_array_equal(rc.PT_EDGES, np.array(drv["PT_EDGES"], dtype=float))
        np.testing.assert_array_equal(rc.PZ_EDGES, np.array(drv["PZ_EDGES"], dtype=float))

    def test_flat_index_is_the_paper_global_id(self):
        with open(ANC / "bin_mapping.txt") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), rc.N_CELLS)
        for row in rows:
            ipt, ipz = int(row["Ptbin"]) - 1, int(row["P||bin"]) - 1
            mask = np.zeros(rc.GRID_SHAPE, dtype=bool)
            mask[ipt, ipz] = True
            self.assertEqual(rc.reported_indices(mask).tolist(), [int(row["GlobalID"])])
            self.assertEqual(float(row["Ptbin_lowedge"]), rc.PT_EDGES[ipt])
            self.assertEqual(float(row["Ptbin_highedge"]), rc.PT_EDGES[ipt + 1])
            self.assertEqual(float(row["P||bin_lowedge"]), rc.PZ_EDGES[ipz])
            self.assertEqual(float(row["P||bin_highedge"]), rc.PZ_EDGES[ipz + 1])

    def test_producers_keep_the_names_their_importers_use(self):
        # Six frozen receipt scripts and coverage_fixed_truth/ki85_compare.py import
        # analyze_uq for these names; uqpaper-median-20261006/paper_median.py imports
        # _ours_only_chi2 for the other two.
        for script, names in (("analyze_uq.py", {"th2_to_array", "th1_to_array",
                                                 "PT_EDGES", "PZ_EDGES"}),
                              ("_ours_only_chi2.py", {"flatten_paper", "tmatrix_to_numpy"})):
            tree = ast.parse((UQ_DIR / script).read_text())
            defined = set()
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    defined.add(node.name)
                elif isinstance(node, ast.ImportFrom) and node.module == "reported_cells":
                    defined.update(a.asname or a.name for a in node.names)
            self.assertLessEqual(names, defined, script)


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.paper = paper_stat_mask().reshape(rc.GRID_SHAPE)
        self.cells = rc.reported_indices(self.paper)

    def test_paper_reports_205_cells(self):
        self.assertEqual(self.cells.size, 205)

    def test_identical_sets_pass(self):
        rc.require_same_cells(self.cells, self.cells.copy(), "a", "b")

    def test_equal_count_permutation_is_refused(self):
        moved = self.paper.copy()
        reported, unreported = np.argwhere(moved), np.argwhere(~moved)
        moved[tuple(reported[100])] = False
        moved[tuple(unreported[0])] = True
        other = rc.reported_indices(moved)
        self.assertEqual(other.size, self.cells.size)
        with self.assertRaises(rc.CellIdentityError) as cm:
            rc.require_same_cells(self.cells, other, "cv", "bootstrap")
        msg = str(cm.exception)
        self.assertIn(f"only in cv: {self.cells[100]}(", msg)
        self.assertIn("only in bootstrap: ", msg)

    def test_omission_is_refused(self):
        with self.assertRaises(rc.CellIdentityError):
            rc.require_same_cells(self.cells, np.delete(self.cells, 7), "a", "b")

    def test_transposed_grid_is_refused(self):
        with self.assertRaises(rc.CellIdentityError):
            rc.reported_indices(self.paper.T)


@unittest.skipIf(ROOT is None, "PyROOT unavailable")
class RootIdentityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "cells.root")
        self.cells = rc.reported_indices(paper_stat_mask().reshape(rc.GRID_SHAPE))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, *hists):
        f = ROOT.TFile.Open(self.path, "RECREATE")
        for h in hists:
            h.Write()
        f.Close()

    def read(self, **kw):
        f = ROOT.TFile.Open(self.path)
        try:
            return rc.read_cells(f, **kw)
        finally:
            f.Close()

    def test_identity_round_trip(self):
        self.write(rc.identity_hist(self.cells))
        cells, source = self.read()
        np.testing.assert_array_equal(cells, self.cells)
        self.assertEqual(source, rc.IDENTITY_HIST)

    def test_legacy_mean_fallback(self):
        h = ROOT.TH2D("hMean2D", "", 14, rc.PT_EDGES, 16, rc.PZ_EDGES)
        for i in self.cells:
            h.SetBinContent(int(i) // 16 + 1, int(i) % 16 + 1, 1e-39)
        self.write(h)
        self.assertEqual(self.read(), (None, None))
        cells, source = self.read(mean_fallback="hMean2D")
        np.testing.assert_array_equal(cells, self.cells)
        self.assertEqual(source, "hMean2D > 0")

    def test_wrong_edges_are_refused(self):
        h = ROOT.TH2D(rc.IDENTITY_HIST, "", 14, rc.PT_EDGES * 1.001, 16, rc.PZ_EDGES)
        self.write(h)
        with self.assertRaises(rc.CellIdentityError):
            self.read()

    def test_transposed_identity_is_refused(self):
        h = ROOT.TH2D(rc.IDENTITY_HIST, "", 16, rc.PZ_EDGES, 14, rc.PT_EDGES)
        self.write(h)
        with self.assertRaises(rc.CellIdentityError):
            self.read()

    def test_non_binary_identity_is_refused(self):
        h = rc.identity_hist(self.cells)
        h.SetBinContent(1, 1, 0.5)
        self.write(h)
        with self.assertRaises(rc.CellIdentityError):
            self.read()


def _has_matplotlib():
    try:
        import matplotlib  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipIf(ROOT is None or not _has_matplotlib(), "PyROOT or matplotlib unavailable")
class ScriptGuardTest(unittest.TestCase):
    """analyze_universes.py and _ours_only_chi2.py refuse a cell mismatch.

    Each script runs as a subprocess on small synthetic files. The permuted
    inputs keep the count (205) and move one reported cell to an unreported
    one, which the scripts at 5ac9706a combined without complaint.
    """

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.dir = Path(cls.tmp.name)
        rng = np.random.default_rng(7)
        paper = paper_stat_mask().reshape(rc.GRID_SHAPE)
        cls.cells = rc.reported_indices(paper)
        unreported = np.setdiff1d(np.arange(rc.N_CELLS), cls.cells)
        cls.perm = np.sort(np.append(np.delete(cls.cells, 100), unreported[0]))
        cv = np.where(paper, rng.lognormal(-88.5, 1.0, rc.GRID_SHAPE), 0.0)
        cls.write_xsec(d / "cv.root", cv)
        for band in ("Flux", "GENIE_MaCCQE"):
            for k in range(3):
                cls.write_xsec(d / f"x_uni_{band}_{k}.root",
                               cv * (1 + 0.02 * rng.standard_normal(rc.GRID_SHAPE)))
        diag = (0.01 * cv.ravel()[cls.cells]) ** 2
        cls.write_boot(d / "boot.root", diag, cls.cells)
        cls.write_boot(d / "boot_perm.root", diag, cls.perm)
        cls.write_boot(d / "boot_omit.root", diag[:-1], cls.cells[:-1])
        cls.write_boot(d / "boot_noid.root", diag, None)
        # A legacy analyze_uq output: no hReportedCells, cells carried by hMean2D > 0.
        cls.write_boot(d / "boot_legacy.root", diag, None, mean=cv)
        f = ROOT.TFile.Open(str(d / "cov_ptpl_minerva_inclusive_6GeV.root"), "RECREATE")
        h = ROOT.TH2D("pt_pl_cross_section", "", 14, rc.PT_EDGES, 16, rc.PZ_EDGES)
        for i in cls.cells:
            h.SetBinContent(int(i) // 16 + 1, int(i) % 16 + 1, 1.01 * cv.ravel()[i])
        h.Write()
        m = ROOT.TMatrixD(rc.N_CELLS, rc.N_CELLS)
        for k, i in enumerate(cls.cells):
            m[int(i)][int(i)] = float(4 * diag[k])
        m.Write("StatOnlyCovariance")
        f.Close()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def write_xsec(path, a):
        f = ROOT.TFile.Open(str(path), "RECREATE")
        h = ROOT.TH2D("hXSec2D", "", 14, rc.PT_EDGES, 16, rc.PZ_EDGES)
        for ix in range(14):
            for iy in range(16):
                h.SetBinContent(ix + 1, iy + 1, float(a[ix, iy]))
        h.Write()
        f.Close()

    @staticmethod
    def write_boot(path, diag, cells, mean=None):
        f = ROOT.TFile.Open(str(path), "RECREATE")
        n = len(diag)
        h = ROOT.TH2D("hCov2D_reported", "", n, 0, n, n, 0, n)
        for i in range(n):
            h.SetBinContent(i + 1, i + 1, float(diag[i]))
        h.Write()
        if cells is not None:
            rc.identity_hist(cells).Write()
        if mean is not None:
            hm = ROOT.TH2D("hMean2D", "", 14, rc.PT_EDGES, 16, rc.PZ_EDGES)
            for ix in range(14):
                for iy in range(16):
                    hm.SetBinContent(ix + 1, iy + 1, float(mean[ix, iy]))
            hm.Write()
        f.Close()

    def run_script(self, argv):
        env = dict(os.environ, MPLCONFIGDIR=str(self.dir / "mpl"))
        return subprocess.run([sys.executable] + argv, cwd=self.dir, env=env,
                              capture_output=True, text=True)

    def universes(self, outdir, boot=None):
        argv = [str(UQ_DIR / "analyze_universes.py"), "--cv", str(self.dir / "cv.root"),
                "--glob", str(self.dir / "x_uni_*.root"), "--outdir", str(self.dir / outdir)]
        if boot:
            argv += ["--bootstrap-cov", str(self.dir / boot)]
        return self.run_script(argv)

    def read_cov(self, path, name):
        f = ROOT.TFile.Open(str(path))
        h = f.Get(name)
        n = h.GetNbinsX()
        a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)] for i in range(n)])
        f.Close()
        return a

    def test_matched_bootstrap_is_block_summed(self):
        p = self.universes("u_ok", "boot.root")
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        out = self.dir / "u_ok" / "uq_universe_covariance.root"
        np.testing.assert_array_equal(
            self.read_cov(out, "hCov_combined"),
            self.read_cov(out, "hCov_universe_total")
            + self.read_cov(self.dir / "boot.root", "hCov2D_reported"))

    def test_legacy_bootstrap_is_block_summed(self):
        p = self.universes("u_legacy", "boot_legacy.root")
        self.assertEqual(p.returncode, 0, p.stderr[-2000:])
        out = self.dir / "u_legacy" / "uq_universe_covariance.root"
        np.testing.assert_array_equal(
            self.read_cov(out, "hCov_combined"),
            self.read_cov(out, "hCov_universe_total")
            + self.read_cov(self.dir / "boot_legacy.root", "hCov2D_reported"))

    def test_mismatched_bootstraps_are_refused(self):
        for boot, text in (("boot_perm.root", "refusing to block-sum"),
                           ("boot_omit.root", "refusing to block-sum"),
                           ("boot_noid.root", "reported cells are unknown")):
            with self.subTest(boot=boot):
                outdir = "u_" + boot.replace(".root", "")
                p = self.universes(outdir, boot)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn(text, p.stderr)
                self.assertEqual(list((self.dir / outdir).iterdir()), [],
                                 "a refused run wrote an output file")

    def ours_only(self, universe_root, boot):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import _ours_only_chi2 as oo; "
                "oo.ANC = sys.argv[2]; sys.argv = ['_ours_only_chi2.py'] + sys.argv[3:]; oo.main()")
        return self.run_script(["-c", code, str(UQ_DIR), str(self.dir), "--ours",
                                str(self.dir / "cv.root"), "--universe-cov", str(universe_root),
                                "--bootstrap-cov", str(self.dir / boot)])

    def test_ours_only_refuses_a_permuted_bootstrap(self):
        uni = self.dir / "oo_u" / "uq_universe_covariance.root"
        if not uni.exists():
            self.assertEqual(self.universes("oo_u").returncode, 0)
        ok = self.ours_only(uni, "boot.root")
        self.assertEqual(ok.returncode, 0, ok.stderr[-2000:])
        self.assertIn("direct inverse: chi^2", ok.stdout)
        bad = self.ours_only(uni, "boot_perm.root")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("reported cells differ", bad.stderr)

    def test_ours_only_refuses_a_permuted_universe_and_warns_on_a_legacy_one(self):
        def write_universe(path, cells):
            f = ROOT.TFile.Open(str(path), "RECREATE")
            n = self.cells.size
            h = ROOT.TH2D("hCov_universe_total", "", n, 0, n, n, 0, n)
            for i in range(n):
                h.SetBinContent(i + 1, i + 1, 1e-80)
            h.Write()
            if cells is not None:
                rc.identity_hist(cells).Write()
            f.Close()

        perm = self.dir / "perm_universe.root"
        write_universe(perm, self.perm)
        bad = self.ours_only(perm, "boot.root")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("reported cells differ", bad.stderr)
        self.assertIn("universe", bad.stderr)
        legacy = self.dir / "legacy_universe.root"
        write_universe(legacy, None)
        ok = self.ours_only(legacy, "boot.root")
        self.assertEqual(ok.returncode, 0, ok.stderr[-2000:])
        self.assertIn("checked by count only", ok.stdout)


if __name__ == "__main__":
    unittest.main()
