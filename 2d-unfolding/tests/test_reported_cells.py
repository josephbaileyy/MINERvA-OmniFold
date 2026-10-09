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


if __name__ == "__main__":
    unittest.main()
