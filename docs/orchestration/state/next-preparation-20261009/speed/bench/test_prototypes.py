"""Byte-equality tests for the two loader prototypes, with negative controls.

Runs only on the synthetic trees from ``make_synthetic_trees.py``; it trains
nothing, submits nothing and writes nothing outside a temporary directory.

    SPEED_TREES=<dir with synth_*.root> python3.13 -I test_prototypes.py
"""

import glob
import math
import os
import sys
import types
import unittest

import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pinned  # noqa: E402

import ROOT  # noqa: E402

DRV = pinned.load_driver()
BS = pinned.load_proto("branch_status")
VL = pinned.load_proto("vector_loader")
TREES = sorted(glob.glob(os.path.join(os.environ["SPEED_TREES"], "synth_rows*_extra*.root")))
LO_HI = (DRV.PT_EDGES[0], DRV.PT_EDGES[-1], DRV.PZ_EDGES[0], DRV.PZ_EDGES[-1])
POT = 0.212405        # the production data/MC POT scale printed by the driver
KEYS = ("truth_pt", "truth_pz", "reco_pt", "reco_pz", "pass_reco", "pass_truth",
        "w_truth", "w_reco")


def modes_for(tree):
    modes = [(True, None), (False, None)]
    if tree.GetBranch("w_truth_Flux_0"):
        modes += [(True, ("Flux", 0)), (True, ("GEANT", 0))]
    return modes


def open_tree(path):
    f = ROOT.TFile.Open(path)
    return f, f.Get("mc_signal_reco")


def reference(path, use_weights, universe):
    f, t = open_tree(path)
    out = DRV.collect_signal_arrays_2d(t, *LO_HI, POT, use_weights=use_weights,
                                       universe_branch=universe)
    f.Close()
    return out


def diff_keys(a, b):
    """Keys whose arrays differ in dtype, shape or any byte."""
    return [k for k in KEYS
            if a[k].dtype != b[k].dtype or a[k].shape != b[k].shape
            or a[k].tobytes() != b[k].tobytes()]


def columnar(path, use_weights, universe, module=VL):
    f, t = open_tree(path)
    names = BS.signal_branches(use_weights, universe, t)
    wt, wr = (names[5], names[6]) if use_weights else (None, None)
    out = module.collect_signal_arrays_columnar(t, (*names[:4], wt, wr), *LO_HI, POT,
                                                use_weights=use_weights)
    f.Close()
    return out


def mutant(old, new):
    """A copy of the columnar prototype with one source substitution applied."""
    with open(VL.__file__) as fh:
        src = fh.read()
    assert src.count(old) == 1, f"mutation site {old!r} must occur exactly once"
    mod = types.ModuleType("vector_loader_mutant")
    exec(compile(src.replace(old, new), "vector_loader_mutant", "exec"), mod.__dict__)
    return mod


class Equality(unittest.TestCase):
    def test_trees_present(self):
        self.assertGreaterEqual(len(TREES), 2, TREES)

    def test_branch_status_is_byte_identical(self):
        for path in TREES:
            f, t = open_tree(path)
            for use_w, uni in modes_for(t):
                with self.subTest(tree=os.path.basename(path), use_weights=use_w, universe=uni):
                    ref = reference(path, use_w, uni)
                    g, u = open_tree(path)
                    BS.restrict_active_branches(u, BS.signal_branches(use_w, uni, u))
                    guarded = BS.ActiveOnlyTree(u)
                    got = DRV.collect_signal_arrays_2d(guarded, *LO_HI, POT, use_weights=use_w,
                                                       universe_branch=uni)
                    self.assertEqual(sorted(guarded.addressed),
                                     sorted(BS.signal_branches(use_w, uni, u)))
                    g.Close()
                    self.assertEqual(diff_keys(ref, got), [])
                    self.assertGreater(ref["truth_pt"].size, 0)
            f.Close()

    def test_columnar_is_byte_identical(self):
        for path in TREES:
            f, t = open_tree(path)
            for use_w, uni in modes_for(t):
                with self.subTest(tree=os.path.basename(path), use_weights=use_w, universe=uni):
                    self.assertEqual(diff_keys(reference(path, use_w, uni),
                                               columnar(path, use_w, uni)), [])
            f.Close()


class NegativeControls(unittest.TestCase):
    """Each defect must be caught by the comparison the equality tests use."""

    path = None

    @classmethod
    def setUpClass(cls):
        cls.path = next(p for p in TREES if "extra192" in p)
        cls.ref = reference(cls.path, True, None)

    def test_fixture_reaches_every_boundary(self):
        f, t = open_tree(self.path)
        cols = ROOT.RDataFrame(t).AsNumpy(["MC", "MC_pz", "sim_pass", "w_truth"])
        f.Close()
        pt, pz = cols["MC"], cols["MC_pz"]
        fin = np.isfinite(pt) & np.isfinite(pz) & (pz > 0)
        theta = np.arctan2(pt[fin], pz[fin])
        near = np.abs(theta - math.radians(20.0)) < 1e-14
        self.assertGreater(int(near.sum()), 100)
        self.assertGreater(int((np.asarray(cols["sim_pass"]).view(np.uint8) == 2).sum()), 0)
        self.assertGreater(int((cols["w_truth"] == 1e4).sum()), 0)
        self.assertGreater(int((~np.isfinite(cols["w_truth"])).sum()), 0)

    def test_missing_activation_is_caught(self):
        g, u = open_tree(self.path)
        names = BS.signal_branches(True, None, u)
        BS.restrict_active_branches(u, [n for n in names if n != "w_reco"])
        got = DRV.collect_signal_arrays_2d(u, *LO_HI, POT, use_weights=True)
        self.assertIn("w_reco", diff_keys(self.ref, got))     # the silent defect is real
        # and it leaves nothing to inspect afterwards: no status, and no address recorded
        self.assertFalse(u.GetBranchStatus("w_reco"))
        self.assertTrue(ROOT.gInterpreter.ProcessLine(
            f"((TTree*){ROOT.addressof(u)})->GetBranch(\"w_reco\")->GetAddress() == nullptr;"))
        with self.assertRaises(RuntimeError):                  # and the guard refuses it
            DRV.collect_signal_arrays_2d(BS.ActiveOnlyTree(u), *LO_HI, POT, use_weights=True)
        g.Close()

    def _assert_mutant_caught(self, old, new):
        got = columnar(self.path, True, None, module=mutant(old, new))
        self.assertNotEqual(diff_keys(self.ref, got), [], f"mutant {new!r} not caught")

    def test_sim_pass_equals_one_is_caught(self):
        self._assert_mutant_caught("passed = raw != 0", "passed = raw == 1")


    def test_weight_window_edge_is_caught(self):
        self._assert_mutant_caught("(wt < 1e4)", "(wt <= 1e4)")

    def test_dropped_angle_cut_is_caught(self):
        self._assert_mutant_caught("tru_ok[cand], n_guard = _theta_below_cut(tru_pt[cand], tru_pz[cand])",
                                   "tru_ok[cand], n_guard = True, 0")

    def test_sentinel_is_caught(self):
        self._assert_mutant_caught('np.where(pass_reco, rec_pt, SENTINEL)',
                                   'np.where(pass_reco, rec_pt, -999.0)')


class DefensiveGuards(unittest.TestCase):
    """Record whether each defensive guard was needed on this platform (not pass criteria)."""

    def test_report_bool_view_difference(self):
        # Review F12: drop the byte view and test AsNumpy's non-canonical bool array directly.
        path = next(p for p in TREES if "extra192" in p)
        got = columnar(path, True, None, module=mutant("raw = raw.view(np.uint8)", "pass"))
        print(f"\n[bool-view] without the byte view, keys differing: "
              f"{diff_keys(reference(path, True, None), got)}", file=sys.stderr)

    def test_report_unguarded_difference(self):
        path = next(p for p in TREES if "extra192" in p)
        ref = reference(path, True, None)
        got = columnar(path, True, None, module=mutant("ATAN2_GUARD_ULPS = 64",
                                                       "ATAN2_GUARD_ULPS = -1"))
        guarded = columnar(path, True, None)
        print(f"\n[atan2] guard rows re-evaluated: {guarded['_atan2_guard_rows']}; "
              f"unguarded NumPy arctan2 differs in keys: {diff_keys(ref, got)}",
              file=sys.stderr)


if __name__ == "__main__":
    print(f"driver blob {DRV.__pinned_blob__}; ROOT {ROOT.gROOT.GetVersion()}; "
          f"numpy {np.__version__}; trees {[os.path.basename(p) for p in TREES]}", file=sys.stderr)
    unittest.main(verbosity=2)
