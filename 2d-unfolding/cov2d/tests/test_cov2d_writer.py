"""cov2d_writer: the counts, the expansion, the file's schema, and control (2)'s writer half on a synthetic $CV.
Needs PyROOT, uproot 5.6.9 and numpy. From the checkout:
    python -B -m pytest -q 2d-unfolding/cov2d/tests/test_cov2d_writer.py
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d_writer as w  # noqa: E402

try:
    import ROOT  # noqa: F401
    import uproot  # noqa: F401
    HAVE = True
except Exception:  # pragma: no cover
    HAVE = False


class Counts(unittest.TestCase):
    def test_clipped_and_recorded(self):
        ks, kb, rec = w.draw_counts(np.array([2.0, -1.0, 0.0, 3.5]), np.array([-0.5, 1.0]),
                                    np.random.default_rng(4))
        self.assertEqual((ks[1], ks[2], kb[0]), (0, 0, 0))
        self.assertEqual(rec["signal"], {"sum_lambda": 4.5, "sum_lambda_neg": -1.0, "rows_neg": 1})
        self.assertEqual(rec["background"], {"sum_lambda": 0.5, "sum_lambda_neg": -0.5, "rows_neg": 1})

    def test_signal_drawn_before_background(self):
        ls, lb = np.full(50, 3.0), np.full(40, 2.0)
        ks, kb, _ = w.draw_counts(ls, lb, np.random.default_rng(8))
        r = np.random.default_rng(8)
        np.testing.assert_array_equal(ks, r.poisson(ls))
        np.testing.assert_array_equal(kb, r.poisson(lb))

    def test_expand(self):
        got = w.expand(np.array([0.1, 0.2, 0.3, 0.4]), np.array([2.0, 3.0, 4.0, 5.0]),
                       np.array([1, 0, 1, 1], np.uint8), np.array([2, 5, 0, 1]))
        np.testing.assert_array_equal(got["measured"], [0.1, 0.1, 0.4])
        np.testing.assert_array_equal(got["measured_pz"], [2.0, 2.0, 5.0])
        np.testing.assert_array_equal(got["measured_pass"], [1, 1, 1])
        self.assertEqual(got["measured_pass"].dtype, np.uint8)
        both = w.concat(got, w.expand(np.array([9.0]), np.array([9.5]), np.array([1]), np.array([1])))
        np.testing.assert_array_equal(both["measured"], [0.1, 0.1, 0.4, 9.0])


def write_cv(path: Path, cols: dict, pot: float, extra_tree: bool = True) -> None:
    """A $CV-shaped file: its data tree in $CV's leaves, dataPOTUsed, and an unrelated simulation tree."""
    import ROOT
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE")
    t = ROOT.TTree("data", "data")
    bufs = {b: array(w.LEAVES[b][0], [0]) for b in w.BRANCHES}
    for b in w.BRANCHES:
        t.Branch(b, bufs[b], f"{b}/{w.LEAVES[b][1]}")
    for i in range(cols["measured"].size):
        for b in w.BRANCHES:
            bufs[b][0] = cols[b][i].item()
        t.Fill()
    t.Write()
    if extra_tree:
        s = ROOT.TTree("mc_signal_reco", "mc_signal_reco")
        x = array("d", [0])
        s.Branch("sim", x, "sim/D")
        for v in (1.0, 2.0):
            x[0] = v
            s.Fill()
        s.Write()
    ROOT.TParameter("double")("dataPOTUsed", pot).Write()
    ROOT.TParameter("double")("mcPOTUsed", 4 * pot).Write()
    f.Close()


@unittest.skipUnless(HAVE, "needs PyROOT and uproot")
class File(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = mock.patch.object(os, "O_NOATIME", getattr(os, "O_NOATIME", 0), create=True)
        p.start()
        self.addCleanup(p.stop)
        r = np.random.default_rng(12)
        n = 2345
        self.cols = {"measured": r.uniform(0, 3, n), "measured_pz": r.uniform(1, 30, n),
                     "measured_pass": (r.uniform(size=n) < 0.8).astype(np.uint8)}
        self.cols["measured"][7] = -0.0
        self.cv = Path(self.tmp.name) / "cv.root"
        write_cv(self.cv, self.cols, 1.057394261158926e21)
        future = time.time() + 86400
        os.utime(self.cv, (future, os.stat(self.cv).st_mtime))

    def test_schema_and_parameter(self):
        import uproot
        out = Path(self.tmp.name) / "d.root"
        w.write_data_file(out, self.cols, 1.5e20)
        f = uproot.open(out)
        self.assertEqual(sorted(f.classnames(recursive=False)), ["data;1", "dataPOTUsed;1"])
        t = f["data"]
        self.assertEqual([str(t[b].interpretation) for b in w.BRANCHES],
                         ["AsDtype('>f8')", "AsDtype('>f8')", "AsDtype('uint8')"])
        self.assertEqual([t[b].title for b in w.BRANCHES], ["measured/D", "measured_pz/D", "measured_pass/b"])
        self.assertEqual(f["dataPOTUsed"].member("fVal"), 1.5e20)
        a = t.arrays(list(w.BRANCHES), library="np")
        for b in w.BRANCHES:
            self.assertTrue(np.array_equal(a[b].astype(self.cols[b].dtype).view(np.uint8),
                                           self.cols[b].view(np.uint8)), b)

    @contextlib.contextmanager
    def autosaving(self):
        # A1: ROOT.TTree replaced by a factory that autosaves every 200 entries, so the 2,345-row fixture reaches the
        # autosaves that $CV's 4,119,797 rows reached in control (2a). It yields each tree's threshold as built, and as
        # in force when the tree is written: a threshold above the fixture's size (ROOT's default, 300 MB) would pass
        # the key check here and fail on $CV. mock.patch.object cannot restore ROOT.TTree: it is a lazy attribute of
        # ROOT's facade, so the exit's delattr fails. A Python subclass of TTree crashes cppyy, so Write is wrapped on
        # the instance.
        import ROOT
        real, built, at_write = ROOT.TTree, [], []

        def factory(*a):
            t = real(*a)
            t.SetAutoSave(200)
            built.append(t.GetAutoSave())
            write = t.Write

            def recording_write(*args):
                at_write.append(t.GetAutoSave())
                return write(*args)
            t.Write = recording_write
            return t
        ROOT.TTree = factory
        try:
            yield built, at_write
        finally:
            ROOT.TTree = real

    def test_one_cycle_when_autosave_would_fire(self):
        import uproot
        out = Path(self.tmp.name) / "d.root"
        with self.autosaving() as (built, at_write):
            w.write_data_file(out, self.cols, 1.5e20)
        self.assertEqual(built, [200])  # the factory built the tree: the test cannot pass without forcing
        f = uproot.open(out)
        self.assertEqual(sorted(f.classnames(recursive=False)), ["data;1", "dataPOTUsed;1"])
        a = f["data"].arrays(list(w.BRANCHES), library="np")
        for b in w.BRANCHES:
            self.assertTrue(np.array_equal(a[b].astype(self.cols[b].dtype).view(np.uint8),
                                           self.cols[b].view(np.uint8)), b)
        self.assertEqual(at_write, [0])  # AutoSave is off when the tree is written, whatever the row count

    def test_control_passes_when_autosave_would_fire(self):
        with self.autosaving() as (built, _):
            code, text = self.run_control()
        self.assertEqual(built, [200])
        self.assertEqual(code, 0, text)
        self.assertIn("WRITER-CONTROL PASS failures=0", text)

    def test_refuses_unequal_columns(self):
        bad = dict(self.cols, measured_pz=self.cols["measured_pz"][:-1])
        with self.assertRaises(w.c.Refusal):
            w.write_data_file(Path(self.tmp.name) / "x.root", bad, 1.0)

    def run_control(self):
        out = Path(self.tmp.name) / "control.root"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = w.main(["control", "--out", str(out), "--cv", str(self.cv)])
        return code, buf.getvalue()

    def test_control_passes_on_the_writer(self):
        code, text = self.run_control()
        self.assertEqual(code, 0, text)
        self.assertIn("WRITER-CONTROL PASS failures=0", text)
        self.assertIn("EQUAL  data.measured rows=2345", text)

    def test_control_fires_on_a_changed_row(self):
        real = w.write_data_file

        def off_by_one(path, cols, pot):
            cols = {k: v.copy() for k, v in cols.items()}
            cols["measured_pz"][100] = np.nextafter(cols["measured_pz"][100], 99.0)
            real(path, cols, pot)

        with mock.patch.object(w, "write_data_file", off_by_one):
            code, text = self.run_control()
        self.assertEqual(code, 3)
        self.assertIn("FAILURE data.measured_pz: 1 rows differ", text)

    def test_control_fires_on_a_leaf_type(self):
        with mock.patch.dict(w.LEAVES, {"measured_pass": ("i", "I")}):
            code, text = self.run_control()
        self.assertEqual(code, 3)
        self.assertIn("data.measured_pass: interpretation", text)

    def test_control_fires_on_the_parameter(self):
        real = w.write_data_file
        with mock.patch.object(w, "write_data_file", lambda p, cols, pot: real(p, cols, pot * (1 + 1e-15))):
            code, text = self.run_control()
        self.assertEqual(code, 3)
        self.assertIn("FAILURE dataPOTUsed differs", text)

    def test_control_fires_on_a_dropped_row(self):
        real = w.write_data_file
        with mock.patch.object(w, "write_data_file",
                               lambda p, cols, pot: real(p, {k: v[:-1] for k, v in cols.items()}, pot)):
            code, text = self.run_control()
        self.assertEqual(code, 3)
        self.assertIn("FAILURE data: entries", text)


if __name__ == "__main__":
    unittest.main()
