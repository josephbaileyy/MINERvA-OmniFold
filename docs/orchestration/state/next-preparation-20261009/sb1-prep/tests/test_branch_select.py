"""Byte equality of prototype 1 against the pinned, unmodified loaders, with negative controls.

Synthetic inputs only (``make_fixture_omnifile.py``); nothing is trained, fitted or submitted. The
pinned driver is executed from verified bytes (``n2/execution.load_verified`` with
``sb1_run.DRIVER_SHA256``), never edited.

    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest discover -s tests -v
"""

import math
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(HERE))

import sb1_run  # noqa: E402
from sb1_run import gx  # noqa: E402
import make_fixture_omnifile as mk  # noqa: E402

import ROOT  # noqa: E402

DRV, _ = gx.load_verified("unfold_2d_omnifold_unbinned", sb1_run.REPO / sb1_run.DRIVER_REL,
                          sb1_run.REPO, sb1_run.DRIVER_SHA256)
BS, _ = gx.load_verified("branch_select", PKG / "branch_select.py", sb1_run.REPO)
LO_HI = (DRV.PT_EDGES[0], DRV.PT_EDGES[-1], DRV.PZ_EDGES[0], DRV.PZ_EDGES[-1])
POT = 1.0e20 / 4.708e20
LAT = ("Muon_Energy_MINOS", 0)
#: CV with and without weights, two vertical universes, one genuinely lateral universe.
MODES = [(False, None), (True, None), (True, ("Flux", 0)), (True, ("GEANT_Neutron", 0)), (True, LAT)]
TREES = ("data", "mc_background", "mc_signal_reco", "mc_truth_denom")


def setUpModule():
    global TMP, FIX
    TMP = tempfile.TemporaryDirectory()
    FIX = os.path.join(TMP.name, "fixture.root")
    mk.write_fixture(FIX, rows=6000, extra=12)


def tearDownModule():
    TMP.cleanup()


class Open:
    """One freshly opened tree (every branch active, as the driver opens it)."""

    def __init__(self, name):
        self.f = ROOT.TFile.Open(FIX)
        self.t = self.f.Get(name)

    def __enter__(self):
        return self.t

    def __exit__(self, *exc):
        self.f.Close()


def call(tree_name, use_w, uni, how, tree=None, driver=DRV, **kw):
    """Run one loader with ``main()``'s arguments; return its digest record (and result)."""
    func = {"data": "fill_data_reco_2d", "mc_background": "fill_bkg_reco_2d",
            "mc_signal_reco": "collect_signal_arrays_2d",
            "mc_truth_denom": "collect_truth_denom_arrays"}[tree_name]
    loader = getattr(driver, func)
    hist = None
    if tree_name == "data":
        hist = DRV.make_th2d(f"hD{id(kw)}{how}", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        args, kwargs = (hist, *LO_HI), {"verbose": False}
    elif tree_name == "mc_background":
        hist = DRV.make_th2d(f"hB{id(kw)}{how}", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        args = (hist, POT)
        kwargs = {"pt_lo": LO_HI[0], "pt_hi": LO_HI[1], "pz_lo": LO_HI[2], "pz_hi": LO_HI[3],
                  "verbose": False, "universe_branch": uni}
    elif tree_name == "mc_signal_reco":
        args = (*LO_HI, POT)
        kwargs = {"use_weights": use_w, "verbose": False, "universe_branch": uni,
                  "alt_universe_branch": None}
    else:
        args = (*LO_HI, POT)
        kwargs = {"use_weights": use_w, "verbose": False, "universe_branch": uni}

    def run(t):
        if how == "pinned":
            res, rec = loader(t, *args, **kwargs), {}
        elif how == "all":
            res, rec = BS.call_all(loader, t, *args, **kwargs)
        else:
            res, rec = BS.call_selective(loader, t, *args, **kw, **kwargs)
        rec.update(BS.result_digests(func, res, hist))
        return rec, res

    if tree is not None:
        return run(tree)
    with Open(tree_name) as t:
        return run(t)


def applicable(tree_name, use_w, uni):
    # the background loader has no use_weights switch; data has neither switch nor universe
    if tree_name == "data":
        return uni is None and use_w
    if tree_name == "mc_background":
        return use_w
    return True


class TheFixture(unittest.TestCase):
    """The fixture must reach every boundary, or equality on it proves less than claimed."""

    def cols(self, tree, names):
        with Open(tree) as t:
            return ROOT.RDataFrame(t).AsNumpy(names)

    def test_boundaries_present(self):
        c = self.cols("mc_signal_reco", ["MC", "MC_pz", "w_truth", "w_reco", "sim_pass"])
        pt, pz = c["MC"], c["MC_pz"]
        fin = np.isfinite(pt) & np.isfinite(pz) & (pz > 0)
        near = np.abs(np.arctan2(pt[fin], pz[fin]) - math.radians(20.0)) < 1e-14
        self.assertGreater(int(near.sum()), 20)
        self.assertGreater(int((np.asarray(c["sim_pass"]).view(np.uint8) == 2).sum()), 0)
        for w in (c["w_truth"], c["w_reco"]):
            self.assertGreater(int((w == 1e4).sum()), 0)
            self.assertGreater(int((w == np.nextafter(1e4, 0)).sum()), 0)
            self.assertGreater(int((~np.isfinite(w)).sum()), 0)
            self.assertGreater(int((w < 0).sum()), 0)
        self.assertGreater(int(((pt == 0.0) & np.signbit(pt)).sum()), 0)        # -0.0
        b = self.cols("mc_background", ["w_bkg"])["w_bkg"]
        self.assertGreater(int((b == 1e6).sum()) + int((b == np.nextafter(1e6, 0)).sum()), 1)
        d = self.cols("data", ["measured"])["measured"]
        self.assertGreater(int((np.abs(d) > 1e3).sum()), 0)

    def test_lateral_branches_differ_from_cv_and_vertical_have_none(self):
        s = "Muon_Energy_MINOS_0"
        for tree, pairs in (("mc_truth_denom", [(f"pT_truth_{s}", "MC"), (f"pz_truth_{s}", "MC_pz")]),
                            ("mc_signal_reco", [(f"MC_{s}", "MC"), (f"sim_pz_{s}", "sim_pz")]),
                            ("mc_background", [(f"sim_background_{s}", "sim_background")])):
            for a, b in pairs:
                c = self.cols(tree, [a, b])
                fin = np.isfinite(c[a]) & np.isfinite(c[b])
                self.assertGreater(float(np.mean(c[a][fin] != c[b][fin])), 0.9, (tree, a))
        with Open("mc_signal_reco") as t:
            self.assertFalse(t.GetBranch("MC_Flux_0") or t.GetBranch("sim_GEANT_Neutron_0"))


class Equality(unittest.TestCase):
    def test_selective_is_byte_identical_to_the_pinned_loaders(self):
        n = 0
        for tree in TREES:
            for use_w, uni in MODES:
                if not applicable(tree, use_w, uni):
                    continue
                with self.subTest(tree=tree, use_weights=use_w, universe=uni):
                    ref, _ = call(tree, use_w, uni, "pinned")
                    got, _ = call(tree, use_w, uni, "selective")
                    also, _ = call(tree, use_w, uni, "all")
                    self.assertEqual(ref["digests"], got["digests"])
                    self.assertEqual(ref["digests"], also["digests"])
                    self.assertGreater(max(ref["sizes"].values()), 0)
                    if tree in ("data", "mc_background"):          # the histogram it fills
                        self.assertIn("histogram", got["digests"])
                    self.assertTrue(got["verified_before_first_read"])
                    self.assertLess(len(got["branches"]), got["n_branches_in_tree"])
                    n += 1
        self.assertEqual(n, 1 + 4 + 5 + 5)            # data, background, signal, truth

    def test_the_lateral_selection_names_every_shifted_branch(self):
        s = "Muon_Energy_MINOS_0"
        want = {"mc_signal_reco": [f"MC_{s}", f"MC_pz_{s}", f"sim_{s}", f"sim_pz_{s}", "sim_pass",
                                   f"w_truth_{s}", f"w_reco_{s}"],
                "mc_truth_denom": [f"pT_truth_{s}", f"pz_truth_{s}", f"w_truth_{s}"],
                "mc_background": [f"sim_background_{s}", f"sim_background_pz_{s}",
                                  "sim_background_pass", f"w_bkg_{s}"],
                "data": ["measured", "measured_pz", "measured_pass"]}
        for tree, names in want.items():
            got, _ = call(tree, True, LAT if tree != "data" else None, "selective")
            self.assertEqual(got["branches"], names)

    def test_the_vertical_selection_keeps_cv_kinematics(self):
        got, _ = call("mc_signal_reco", True, ("Flux", 0), "selective")
        self.assertEqual(got["branches"], ["MC", "MC_pz", "sim", "sim_pz", "sim_pass",
                                           "w_truth_Flux_0", "w_reco_Flux_0"])
        got, _ = call("mc_background", True, ("GEANT_Neutron", 0), "selective")
        self.assertEqual(got["branches"], ["sim_background", "sim_background_pz",
                                           "sim_background_pass", "w_bkg_GEANT_Neutron_0"])

    def test_a_reused_tree_is_restored_and_reads_identically_afterwards(self):
        for tree in ("mc_signal_reco", "mc_truth_denom", "mc_background"):
            with self.subTest(tree=tree), Open(tree) as t:
                before = BS.snapshot_status(t)
                for uni in (LAT, ("Flux", 0)):            # two selections on one tree object
                    got, _ = call(tree, True, uni, "selective", tree=t)
                    self.assertEqual(BS.snapshot_status(t), before)
                    self.assertEqual(got["digests"], call(tree, True, uni, "pinned")[0]["digests"])
                after, _ = call(tree, True, LAT, "pinned", tree=t)  # production read, same object
                self.assertEqual(after["digests"], call(tree, True, LAT, "pinned")[0]["digests"])

    def test_a_partial_entry_state_is_restored_exactly(self):
        with Open("mc_signal_reco") as t:
            t.SetBranchStatus("MC_q3", 0)
            t.SetBranchStatus("w_truth_Pad_3", 0)
            before = BS.snapshot_status(t)
            call("mc_signal_reco", True, LAT, "selective", tree=t)
            self.assertEqual(BS.snapshot_status(t), before)
            with self.assertRaises(BS.SelectionError):      # production arm refuses that state
                call("mc_signal_reco", True, LAT, "all", tree=t)

    def test_discovery_reads_no_entry_and_leaves_no_address(self):
        with Open("mc_signal_reco") as t:
            names, proxy = BS.discover(DRV.collect_signal_arrays_2d, t,
                                       (*LO_HI, POT), {"use_weights": True,
                                                       "universe_branch": LAT})
            self.assertTrue(proxy.stopped_at_first_entry)
            self.assertEqual(t.GetReadEntry(), -1)
            self.assertFalse(any(BS._has_address(t.GetBranch(n)) for n in names))
            self.assertTrue(all(s for _, s in BS.snapshot_status(t)))


class NegativeControls(unittest.TestCase):
    """Each defect must be refused before any value is read, or caught by the byte comparison."""

    def test_the_silent_defect_is_real_without_the_guard(self):
        with Open("mc_signal_reco") as t:
            names = BS.derive(DRV.collect_signal_arrays_2d, t, (*LO_HI, POT),
                              {"use_weights": True, "universe_branch": LAT})
            BS.apply_selection(t, [n for n in names if n != "w_reco_Muon_Energy_MINOS_0"])
            res = DRV.collect_signal_arrays_2d(t, *LO_HI, POT, use_weights=True,
                                               universe_branch=LAT)
            got = BS.result_digests("collect_signal_arrays_2d", res)["digests"]
        ref = call("mc_signal_reco", True, LAT, "pinned")[0]["digests"]
        self.assertNotEqual(got["w_reco"], ref["w_reco"])

    def test_every_omitted_activation_is_refused_before_the_first_read(self):
        for tree in TREES:
            uni = None if tree == "data" else LAT
            names = call(tree, True, uni, "selective")[0]["branches"]
            for omit in names:
                with self.subTest(tree=tree, omit=omit), Open(tree) as t:
                    with self.assertRaisesRegex(BS.SelectionError, "inactive"):
                        call(tree, True, uni, "selective", tree=t, omit=(omit,))
                    self.assertEqual(t.GetReadEntry(), -1)
                    self.assertTrue(all(s for _, s in BS.snapshot_status(t)))

    def test_an_extra_activation_is_refused_before_the_first_read(self):
        for tree, extra in (("mc_signal_reco", "w_truth"), ("mc_truth_denom", "MC_q3"),
                            ("mc_background", "w_bkg"), ("data", "measured_q3")):
            uni = None if tree == "data" else LAT
            with self.subTest(tree=tree), Open(tree) as t:
                with self.assertRaisesRegex(BS.SelectionError, "active"):
                    call(tree, True, uni, "selective", tree=t, extra=(extra,))
                self.assertEqual(t.GetReadEntry(), -1)

    def mutant_driver(self, old, new):
        src = (sb1_run.REPO / sb1_run.DRIVER_REL).read_text()
        self.assertEqual(src.count(old), 1, old)
        mod = types.ModuleType("driver_mutant")
        exec(compile(src.replace(old, new), "driver_mutant", "exec"), mod.__dict__)
        return mod

    def test_a_loader_that_reads_another_branch_is_refused_by_the_rule(self):
        mut = self.mutant_driver('t_sig.SetBranchAddress("sim_pass", sim_pass)',
                                 't_sig.SetBranchAddress("sim_eavail", sim_pass)')
        with Open("mc_signal_reco") as t, self.assertRaisesRegex(BS.SelectionError, "rule"):
            BS.call_selective(mut.collect_signal_arrays_2d, t, *LO_HI, POT, use_weights=True,
                              universe_branch=LAT)

    def test_a_wrong_rule_and_access_that_agree_are_caught_by_the_bytes(self):
        # The truth loader stops swapping lateral kinematics AND the static rule is changed to
        # agree, so the guard is satisfied; only the comparison with the pinned loader catches it.
        mut = self.mutant_driver(
            "if t_truth_denom.GetBranch(lat_pt) and t_truth_denom.GetBranch(lat_pz):",
            "if False:")
        orig = BS.expected_branches

        def agreeing(loader, settings, present):
            want = orig(loader, settings, present)
            return ["MC", "MC_pz", want[2]] if loader == "collect_truth_denom_arrays" else want
        BS.expected_branches = agreeing
        try:
            got, _ = call("mc_truth_denom", True, LAT, "selective", driver=mut)
        finally:
            BS.expected_branches = orig
        ref, _ = call("mc_truth_denom", True, LAT, "pinned")
        self.assertNotEqual(got["digests"], ref["digests"])

    def test_an_unmodelled_tree_access_is_refused(self):
        def loader(t, *a, **k):
            t.SetBranchAddress("MC", None)
            return t.GetLeaf("MC")
        loader.__name__ = "collect_truth_denom_arrays"
        with Open("mc_truth_denom") as t, self.assertRaises(BS.UnmodelledAccess):
            BS.discover(loader, t, (), {})

    def test_the_digest_sees_sign_dtype_shape_and_one_ulp(self):
        a = np.array([0.0, 1.0, 2.0])
        d = BS.array_digest(a)
        for b in (np.array([-0.0, 1.0, 2.0]), a.astype(np.float32), a.reshape(3, 1),
                  np.array([0.0, np.nextafter(1.0, 2.0), 2.0]), a[:2]):
            self.assertNotEqual(BS.array_digest(b), d)
        self.assertEqual(BS.array_digest(a.copy()), d)

    def test_the_histogram_digest_sees_one_fill(self):
        h = DRV.make_th2d("hdig", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        d = BS.hist_digest(h)
        h.Fill(0.1, 2.2, 1.0)
        self.assertNotEqual(BS.hist_digest(h), d)


if __name__ == "__main__":
    unittest.main(verbosity=2)
