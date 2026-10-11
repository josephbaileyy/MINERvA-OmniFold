"""`--branch-select derived`: the opt-in selective-read path of the 2D driver.

The default (`--branch-select all`) must stay the call the driver has always made, and the
opt-in path must hand every loader's caller the same bytes while reading fewer branches.
The controls are SB1's (`docs/orchestration/state/next-preparation-20261009/sb1-prep/tests/`
at `d4335d3b`: `test_branch_select.py`, `test_sb1_guarded.py`), re-pointed at the live driver:

* `Loaders`: every loader in the CV (with and without weights), vertical (`Flux_0`,
  `GEANT_Neutron_0`), lateral (`Muon_Energy_MINOS_0`) and alt-model-closure patterns; array,
  dtype, shape and filled-histogram digests equal to the direct call; the derived branch lists;
  a reused tree; a partial entry state; discovery without a read; an empty tree;
* `Refusals`: every omitted activation and an extra one, refused before the first read with the
  tree restored; the silent defect the guard exists for, reproduced without it; a loader that
  reads another branch (refused by the rule); a wrong rule that agrees with a wrong loader
  (caught only by the bytes); an unmodelled tree access;
* `CommandLine`: the real `main()`, run as a script under `nd-unfolding/mnv_guarded_run.py` in a
  throwaway git checkout, in six modes. Both settings must give the same OmniFold inputs and
  estimator arguments (captured by a stub helper, so nothing is trained), the same histograms,
  bin maps, normalization and metadata, and differ only in `runConfig`, `runArgv` and the added
  `branchSelection` record. The default must also equal the driver before this change
  (`BASE_COMMIT`, read from git), and two mutant drivers that omit or add an activation must be
  refused through the same entry point with no output written.

Fixture: SB1's synthetic omnifile (`make_fixture_omnifile.py`, loaded read-only from the frozen
package; it reaches every boundary the loaders test and is written with `TTree`/`RDataFrame`
calls that ROOT 6.28 supports). ROOT 6.28 portability: SB1's `test_boundaries_present` failed on
6.28 because `RDataFrame.AsNumpy` returns a `UChar_t` column as Python `str` objects there
(`Q/sb1-run/REPORT.md` §3). That is a fixture-READING problem, not loader behaviour: the loaders
read the flag through `SetBranchAddress` into `array("B")`. These tests never call `AsNumpy`;
`column()` reads every fixture column per row the same way the loaders do.

Needs PyROOT and numpy:
  PYTHONPATH=$(root-config --libdir) python3 -m unittest 2d-unfolding/tests/test_selective_io.py -v
"""
import contextlib
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from array import array
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
U2D_DIR = HERE.parents[1]
REPO = HERE.parents[2]
SCRIPT = U2D_DIR / "unfold_2d_omnifold_unbinned.py"
DRIVER_REL = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
BASE_COMMIT = "3892e769043cddebfd58ec19e1ab1a567eb01784"  # main before --branch-select
FIXTURE_GEN = (REPO / "docs/orchestration/state/next-preparation-20261009/sb1-prep/tests"
               / "make_fixture_omnifile.py")
GUARD = "nd-unfolding/mnv_guarded_run.py"
HELPER = "unbinned_unfolding/python/omnifold.py"
ROOTED_HELPER_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python"

try:
    import ROOT
    HAVE_ROOT = True
except Exception:  # pragma: no cover - depends on the host
    HAVE_ROOT = False


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if HAVE_ROOT:
    DRV = _load("u2d_selective_io_under_test", SCRIPT)
    MK = _load("sb1_make_fixture_omnifile", FIXTURE_GEN)
    LO_HI = (DRV.PT_EDGES[0], DRV.PT_EDGES[-1], DRV.PZ_EDGES[0], DRV.PZ_EDGES[-1])
POT = 1.0e20 / 4.708e20
LAT = ("Muon_Energy_MINOS", 0)
S = "Muon_Energy_MINOS_0"
#: CV without and with weights, two vertical universes, one lateral universe (SB1's MODES).
MODES = [(False, None), (True, None), (True, ("Flux", 0)), (True, ("GEANT_Neutron", 0)),
         (True, LAT)]
TREES = ("data", "mc_background", "mc_signal_reco", "mc_truth_denom")
LOADER_OF = {"data": "fill_data_reco_2d", "mc_background": "fill_bkg_reco_2d",
             "mc_signal_reco": "collect_signal_arrays_2d",
             "mc_truth_denom": "collect_truth_denom_arrays"}


def setUpModule():
    global TMP, FIX
    if not HAVE_ROOT:
        return
    TMP = tempfile.TemporaryDirectory()
    FIX = os.path.join(TMP.name, "fixture.root")
    MK.write_fixture(FIX, rows=6000, extra=12)


def tearDownModule():
    if HAVE_ROOT:
        TMP.cleanup()


def array_digest(a):
    a = np.asarray(a)
    h = hashlib.sha256()
    h.update(f"{a.dtype.str}|{a.shape}|".encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def hist_digest(h):
    """Contents, Sumw2, statistics and entries of a TH2, as bytes."""
    nx, ny = h.GetNbinsX() + 2, h.GetNbinsY() + 2
    cont = np.array([h.GetBinContent(i, j) for i in range(nx) for j in range(ny)])
    sw2 = h.GetSumw2()
    err2 = (np.array([sw2.At(h.GetBin(i, j)) for i in range(nx) for j in range(ny)])
            if sw2.GetSize() else np.zeros(0))
    stats = np.zeros(13)
    h.GetStats(stats)
    blob = cont.tobytes() + err2.tobytes() + stats.tobytes() + np.float64(h.GetEntries()).tobytes()
    return hashlib.sha256(blob).hexdigest()


def result_digests(result, hist=None):
    """sha256 of every array (dtype, shape and bytes) a loader returns, plus its histogram."""
    items = sorted(result.items()) if isinstance(result, dict) else list(enumerate(result))
    out = {str(k): array_digest(v) for k, v in items}
    sizes = {str(k): int(np.asarray(v).size) for k, v in items}
    if hist is not None:
        out["histogram"] = hist_digest(hist)
    return out, sizes


def column(tree, name, typecode):
    """One fixture column read per row through SetBranchAddress, as the loaders read it.

    Never `AsNumpy`: on ROOT 6.28 it returns a UChar_t column as `str` objects.
    """
    buf = array(typecode, [0])
    tree.SetBranchAddress(name, buf)
    vals = []
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        vals.append(buf[0])
    tree.ResetBranchAddresses()
    return np.asarray(vals, dtype=np.uint8 if typecode == "B" else float)


class Open:
    """One freshly opened tree (every branch active, as main() opens it)."""

    def __init__(self, name, path=None):
        self.f = ROOT.TFile.Open(path or FIX)
        self.t = self.f.Get(name)

    def __enter__(self):
        return self.t

    def __exit__(self, *exc):
        self.f.Close()


def loader_args(tree_name, use_w, uni, alt=None, tag=""):
    """main()'s arguments for one loader; returns (args, kwargs, histogram or None)."""
    hist = None
    if tree_name == "data":
        hist = DRV.make_th2d(f"hD{tag}{id(object())}", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        return (hist, *LO_HI), {"verbose": False}, hist
    if tree_name == "mc_background":
        hist = DRV.make_th2d(f"hB{tag}{id(object())}", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        return ((hist, POT), {"pt_lo": LO_HI[0], "pt_hi": LO_HI[1], "pz_lo": LO_HI[2],
                              "pz_hi": LO_HI[3], "verbose": False, "universe_branch": uni}, hist)
    kwargs = {"use_weights": use_w, "verbose": False, "universe_branch": uni}
    if tree_name == "mc_signal_reco":
        kwargs["alt_universe_branch"] = alt
    return (*LO_HI, POT), kwargs, None


def call(tree_name, use_w, uni, how, tree=None, driver=None, alt=None):
    """Run one loader as main() would. how: direct, all or derived.

    Returns (digests, sizes, selection record or None).
    """
    driver = driver or DRV
    func = getattr(driver, LOADER_OF[tree_name])
    args, kwargs, hist = loader_args(tree_name, use_w, uni, alt, how)

    def run(t):
        log = []
        if how == "direct":
            res = func(t, *args, **kwargs)
        else:
            res = driver.call_loader(func, t, *args, branch_select=how, selection_log=log,
                                     **kwargs)
        dig, sizes = result_digests(res, hist)
        return dig, sizes, (log[0] if log else None)

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


@contextlib.contextmanager
def perturbed_activation(omit=(), extra=()):
    """Perturb the APPLIED set while the guard still checks against the derived one."""
    orig = DRV.apply_branch_selection

    def apply(tree, names):
        return orig(tree, [n for n in names if n not in omit] +
                    [n for n in extra if n not in names])
    DRV.apply_branch_selection = apply
    try:
        yield
    finally:
        DRV.apply_branch_selection = orig


def mutant_driver(test, old, new):
    src = SCRIPT.read_text()
    test.assertEqual(src.count(old), 1, old)
    mod = types.ModuleType("u2d_mutant")
    mod.__file__ = str(SCRIPT)
    exec(compile(src.replace(old, new), "u2d_mutant", "exec"), mod.__dict__)
    return mod


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class TheFixture(unittest.TestCase):
    """The fixture must reach every boundary, or equality on it proves less than claimed."""

    def test_boundaries_present(self):
        with Open("mc_signal_reco") as t:
            pt, pz = column(t, "MC", "d"), column(t, "MC_pz", "d")
            flags = column(t, "sim_pass", "B")
            weights = [column(t, "w_truth", "d"), column(t, "w_reco", "d")]
        fin = np.isfinite(pt) & np.isfinite(pz) & (pz > 0)
        near = np.abs(np.arctan2(pt[fin], pz[fin]) - math.radians(20.0)) < 1e-14
        self.assertGreater(int(near.sum()), 20)
        self.assertEqual(set(flags.tolist()), {0, 1, 2})        # the loader tests != 0
        for w in weights:
            self.assertGreater(int((w == 1e4).sum()), 0)
            self.assertGreater(int((w == np.nextafter(1e4, 0)).sum()), 0)
            self.assertGreater(int((~np.isfinite(w)).sum()), 0)
            self.assertGreater(int((w < 0).sum()), 0)
        self.assertGreater(int(((pt == 0.0) & np.signbit(pt)).sum()), 0)        # -0.0
        with Open("mc_background") as t:
            b = column(t, "w_bkg", "d")
        self.assertGreater(int((b == 1e6).sum()) + int((b == np.nextafter(1e6, 0)).sum()), 1)
        with Open("data") as t:
            d = column(t, "measured", "d")
        self.assertGreater(int((np.abs(d) > 1e3).sum()), 0)

    def test_lateral_branches_differ_from_cv_and_vertical_have_none(self):
        for tree, pairs in (("mc_truth_denom", [(f"pT_truth_{S}", "MC"), (f"pz_truth_{S}", "MC_pz")]),
                            ("mc_signal_reco", [(f"MC_{S}", "MC"), (f"sim_pz_{S}", "sim_pz")]),
                            ("mc_background", [(f"sim_background_{S}", "sim_background")])):
            for a, b in pairs:
                with Open(tree) as t:
                    ca, cb = column(t, a, "d"), column(t, b, "d")
                fin = np.isfinite(ca) & np.isfinite(cb)
                self.assertGreater(float(np.mean(ca[fin] != cb[fin])), 0.9, (tree, a))
        with Open("mc_signal_reco") as t:
            self.assertFalse(t.GetBranch("MC_Flux_0") or t.GetBranch("sim_GEANT_Neutron_0"))


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Loaders(unittest.TestCase):
    def test_derived_is_byte_identical_to_the_direct_call_in_every_pattern(self):
        n = 0
        for tree in TREES:
            for use_w, uni in MODES:
                if not applicable(tree, use_w, uni):
                    continue
                with self.subTest(tree=tree, use_weights=use_w, universe=uni):
                    ref, sizes, _ = call(tree, use_w, uni, "direct")
                    got, _, rec = call(tree, use_w, uni, "derived")
                    also, _, none = call(tree, use_w, uni, "all")
                    self.assertEqual(ref, got)
                    self.assertEqual(ref, also)
                    self.assertIsNone(none)
                    self.assertGreater(max(sizes.values()), 0)
                    if tree in ("data", "mc_background"):          # the histogram it fills
                        self.assertIn("histogram", got)
                    self.assertTrue(rec["verified"])
                    self.assertEqual(rec["tree"], tree)
                    self.assertLess(len(rec["branches"]), rec["n_branches_in_tree"])
                    n += 1
        self.assertEqual(n, 1 + 4 + 5 + 5)            # data, background, signal, truth

    def test_the_alt_model_closure_path_is_byte_identical(self):
        ref, _, _ = call("mc_signal_reco", True, None, "direct", alt=("Flux", 0))
        got, _, rec = call("mc_signal_reco", True, None, "derived", alt=("Flux", 0))
        self.assertEqual(ref, got)
        self.assertIn("w_truth_alt", ref)
        self.assertEqual(rec["branches"], ["MC", "MC_pz", "sim", "sim_pz", "sim_pass",
                                           "w_truth", "w_reco", "w_truth_Flux_0",
                                           "w_reco_Flux_0"])

    def test_the_lateral_selection_names_every_shifted_branch(self):
        want = {"mc_signal_reco": [f"MC_{S}", f"MC_pz_{S}", f"sim_{S}", f"sim_pz_{S}", "sim_pass",
                                   f"w_truth_{S}", f"w_reco_{S}"],
                "mc_truth_denom": [f"pT_truth_{S}", f"pz_truth_{S}", f"w_truth_{S}"],
                "mc_background": [f"sim_background_{S}", f"sim_background_pz_{S}",
                                  "sim_background_pass", f"w_bkg_{S}"],
                "data": ["measured", "measured_pz", "measured_pass"]}
        for tree, names in want.items():
            _, _, rec = call(tree, True, LAT if tree != "data" else None, "derived")
            self.assertEqual(rec["branches"], names)

    def test_the_vertical_selection_keeps_cv_kinematics(self):
        _, _, rec = call("mc_signal_reco", True, ("Flux", 0), "derived")
        self.assertEqual(rec["branches"], ["MC", "MC_pz", "sim", "sim_pz", "sim_pass",
                                           "w_truth_Flux_0", "w_reco_Flux_0"])
        _, _, rec = call("mc_background", True, ("GEANT_Neutron", 0), "derived")
        self.assertEqual(rec["branches"], ["sim_background", "sim_background_pz",
                                           "sim_background_pass", "w_bkg_GEANT_Neutron_0"])
        _, _, rec = call("mc_truth_denom", False, None, "derived")
        self.assertEqual(rec["branches"], ["MC", "MC_pz"])

    def test_the_default_hands_the_loader_the_real_tree_and_touches_no_status(self):
        seen = []

        def loader(t, *a, **k):
            seen.append(t)
            return ()
        with Open("mc_signal_reco") as t:
            t.SetBranchStatus("MC_q3", 0)
            before = DRV.branch_status_snapshot(t)
            DRV.call_loader(loader, t, 1, 2, branch_select="all", selection_log=[])
            self.assertIs(seen[0], t)
            self.assertEqual(DRV.branch_status_snapshot(t), before)

    def test_a_reused_tree_is_restored_and_reads_identically_afterwards(self):
        for tree in ("mc_signal_reco", "mc_truth_denom", "mc_background"):
            with self.subTest(tree=tree), Open(tree) as t:
                before = DRV.branch_status_snapshot(t)
                for uni in (LAT, ("Flux", 0)):            # two selections on one tree object
                    got, _, rec = call(tree, True, uni, "derived", tree=t)
                    self.assertEqual(DRV.branch_status_snapshot(t), before)
                    # The loader's buffers are freed on return; a fresh tree's null addresses
                    # must be back, or the next read writes through freed memory.
                    self.assertFalse(any(DRV._branch_has_address(t.GetBranch(n))
                                         for n in rec["branches"]))
                    self.assertEqual(got, call(tree, True, uni, "direct")[0])
                after, _, _ = call(tree, True, LAT, "direct", tree=t)  # default read, same object
                self.assertEqual(after, call(tree, True, LAT, "direct")[0])

    def test_a_partial_entry_state_is_restored_exactly(self):
        with Open("mc_signal_reco") as t:
            t.SetBranchStatus("MC_q3", 0)
            t.SetBranchStatus("w_truth_Pad_3", 0)
            before = DRV.branch_status_snapshot(t)
            call("mc_signal_reco", True, LAT, "derived", tree=t)
            self.assertEqual(DRV.branch_status_snapshot(t), before)

    def test_discovery_reads_no_entry_and_leaves_no_address(self):
        with Open("mc_signal_reco") as t:
            names, proxy = DRV.discover_loader_branches(
                DRV.collect_signal_arrays_2d, t, (*LO_HI, POT),
                {"use_weights": True, "universe_branch": LAT})
            self.assertTrue(proxy.stopped_at_first_entry)
            self.assertEqual(t.GetReadEntry(), -1)
            self.assertFalse(any(DRV._branch_has_address(t.GetBranch(n)) for n in names))
            self.assertTrue(all(s for _, s in DRV.branch_status_snapshot(t)))

    def test_an_empty_tree_is_verified_without_a_read(self):
        t = ROOT.TTree("data", "empty")
        bufs = {n: array("d" if n != "measured_pass" else "B", [0])
                for n in ("measured", "measured_pz", "measured_pass", "measured_q3")}
        for n, b in bufs.items():
            t.Branch(n, b, f"{n}/{'b' if n == 'measured_pass' else 'D'}")
        log = []
        h = DRV.make_th2d("hEmpty", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        pt, pz = DRV.call_loader(DRV.fill_data_reco_2d, t, h, *LO_HI, branch_select="derived",
                                 selection_log=log)
        self.assertEqual((pt.size, pz.size), (0, 0))
        self.assertTrue(log[0]["verified"])
        self.assertTrue(all(s for _, s in DRV.branch_status_snapshot(t)))

    def test_a_universe_branch_missing_from_the_tree_fails_as_the_default_does(self):
        msgs = []
        for how in ("direct", "derived"):
            with self.assertRaises(RuntimeError) as cm:
                call("mc_signal_reco", True, ("NoSuchBand", 0), how)
            msgs.append(str(cm.exception))
        self.assertEqual(msgs[0], msgs[1])
        self.assertNotIsInstance(cm.exception, DRV.BranchSelectionError)

    def test_an_unknown_mode_is_refused(self):
        with Open("data") as t, self.assertRaises(DRV.BranchSelectionError):
            DRV.call_loader(DRV.fill_data_reco_2d, t, None, *LO_HI, branch_select="some")


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class Refusals(unittest.TestCase):
    """Each defect must be refused before any value is read, or caught by the byte comparison."""

    def test_the_silent_defect_is_real_without_the_guard(self):
        with Open("mc_signal_reco") as t:
            names = DRV.derive_loader_branches(DRV.collect_signal_arrays_2d, t, (*LO_HI, POT),
                                               {"use_weights": True, "universe_branch": LAT})
            DRV.apply_branch_selection(t, [n for n in names if n != f"w_reco_{S}"])
            res = DRV.collect_signal_arrays_2d(t, *LO_HI, POT, use_weights=True,
                                               universe_branch=LAT)
            got, _ = result_digests(res)
        ref, _, _ = call("mc_signal_reco", True, LAT, "direct")
        self.assertNotEqual(got["w_reco"], ref["w_reco"])

    def test_every_omitted_activation_is_refused_before_the_first_read(self):
        for tree in TREES:
            uni = None if tree == "data" else LAT
            names = call(tree, True, uni, "derived")[2]["branches"]
            for omit in names:
                with self.subTest(tree=tree, omit=omit), Open(tree) as t:
                    with perturbed_activation(omit=(omit,)), \
                            self.assertRaisesRegex(DRV.BranchSelectionError, "inactive"):
                        call(tree, True, uni, "derived", tree=t)
                    self.assertEqual(t.GetReadEntry(), -1)
                    self.assertTrue(all(s for _, s in DRV.branch_status_snapshot(t)))

    def test_an_extra_activation_is_refused_before_the_first_read(self):
        for tree, extra in (("mc_signal_reco", "w_truth"), ("mc_truth_denom", "MC_q3"),
                            ("mc_background", "w_bkg"), ("data", "measured_q3")):
            uni = None if tree == "data" else LAT
            with self.subTest(tree=tree), Open(tree) as t:
                with perturbed_activation(extra=(extra,)), \
                        self.assertRaisesRegex(DRV.BranchSelectionError, "active"):
                    call(tree, True, uni, "derived", tree=t)
                self.assertEqual(t.GetReadEntry(), -1)
                self.assertTrue(all(s for _, s in DRV.branch_status_snapshot(t)))

    def test_a_loader_that_reads_another_branch_is_refused_by_the_rule(self):
        mut = mutant_driver(self, 't_sig.SetBranchAddress("sim_pass", sim_pass)',
                            't_sig.SetBranchAddress("sim_eavail", sim_pass)')
        with Open("mc_signal_reco") as t, \
                self.assertRaisesRegex(mut.BranchSelectionError, "rule"):
            mut.call_loader(mut.collect_signal_arrays_2d, t, *LO_HI, POT, use_weights=True,
                            universe_branch=LAT, branch_select="derived")

    def test_a_wrong_rule_and_access_that_agree_are_caught_by_the_bytes(self):
        # The truth loader stops swapping lateral kinematics AND the static rule is changed to
        # agree, so the guard is satisfied; only the comparison with the direct call catches it.
        mut = mutant_driver(
            self, "if t_truth_denom.GetBranch(lat_pt) and t_truth_denom.GetBranch(lat_pz):",
            "if False:")
        orig = mut.expected_loader_branches

        def agreeing(loader, settings, present):
            want = orig(loader, settings, present)
            return ["MC", "MC_pz", want[2]] if loader == "collect_truth_denom_arrays" else want
        mut.expected_loader_branches = agreeing
        got, _, rec = call("mc_truth_denom", True, LAT, "derived", driver=mut)
        self.assertTrue(rec["verified"])
        ref, _, _ = call("mc_truth_denom", True, LAT, "direct")
        self.assertNotEqual(got, ref)

    def test_an_unmodelled_tree_access_is_refused(self):
        def loader(t, *a, **k):
            t.SetBranchAddress("MC", None)
            return t.GetLeaf("MC")
        loader.__name__ = "collect_truth_denom_arrays"
        with Open("mc_truth_denom") as t:
            with self.assertRaises(DRV.UnmodelledTreeAccess):
                DRV.discover_loader_branches(loader, t, (), {})
            with self.assertRaises(DRV.UnmodelledTreeAccess):
                DRV._SelectedTree(t, ["MC"]).GetLeaf("MC")

    def test_the_digest_sees_sign_dtype_shape_and_one_ulp(self):
        a = np.array([0.0, 1.0, 2.0])
        d = array_digest(a)
        for b in (np.array([-0.0, 1.0, 2.0]), a.astype(np.float32), a.reshape(3, 1),
                  np.array([0.0, np.nextafter(1.0, 2.0), 2.0]), a[:2]):
            self.assertNotEqual(array_digest(b), d)
        self.assertEqual(array_digest(a.copy()), d)

    def test_the_histogram_digest_sees_one_fill(self):
        h = DRV.make_th2d("hdig", "", DRV.PT_EDGES, DRV.PZ_EDGES)
        d = hist_digest(h)
        h.Fill(0.1, 2.2, 1.0)
        self.assertNotEqual(hist_digest(h), d)


# ---------------------------------------------------------------------------
# The command line, under the OI-136 guard
# ---------------------------------------------------------------------------
STUB_HELPER = '''"""Stand-in for omnifold.py: records what the driver passes, trains nothing."""
import hashlib
import json
import os

import numpy as np


def _digest(a):
    a = np.asarray(a)
    h = hashlib.sha256()
    h.update(f"{a.dtype.str}|{a.shape}|".encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


class OmniFold_helper_functions:
    def omnifold(MCgen, MCreco, measured, pass_reco, pass_truth, pass_measured, iters, **kw):
        rec = {"args": [_digest(x) for x in (MCgen, MCreco, measured, pass_reco, pass_truth,
                                              pass_measured)],
               "sizes": [int(np.asarray(x).size) for x in (MCgen, measured)],
               "iters": int(iters),
               "kwargs": {k: ({"digest": _digest(v)} if isinstance(v, np.ndarray) else v)
                          for k, v in sorted(kw.items())}}
        with open(os.environ["U2D_STUB_CAPTURE"], "w") as fh:
            json.dump(rec, fh, sort_keys=True, default=repr)
        g = np.asarray(MCgen)[np.asarray(pass_truth, dtype=bool)]
        w = 1.0 + 0.1 * np.sin(7.0 * g[:, 0] + g[:, 1])     # deterministic, not unit
        return w.copy(), w
'''
#: Six supported modes of main(); each runs once per --branch-select setting.
CLI_MODES = {
    "cv": ("--use-weights", "--seed", "1"),
    "cv-unweighted": ("--seed", "1"),
    "lateral": ("--use-weights", "--universe", "Muon_Energy_MINOS:0", "--seed", "42",
                "--estimator", "lgbm"),
    "vertical-flux": ("--use-weights", "--universe", "Flux:0", "--seed", "42"),
    "alt-closure": ("--use-weights", "--closure", "--closure-alt-universe", "Flux:0"),
    "bootstrap-negweight": ("--use-weights", "--bootstrap-seed", "3", "--bkg-mode",
                            "negweight", "--estimator", "hist"),
}
#: Output objects the --branch-select setting is allowed to change.
SETTING_DEPENDENT = {"runConfig", "runArgv", "branchSelection"}


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                           "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def make_checkout(base, name, driver_src=None):
    """A throwaway checkout: the driver (or a variant), the guard, its shim, a stub helper."""
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    (root / "2d-unfolding").mkdir()
    (root / DRIVER_REL).write_text(driver_src if driver_src is not None else SCRIPT.read_text())
    shutil.copy2(REPO / GUARD, root / GUARD)
    shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / HELPER).parent.mkdir(parents=True)
    (root / HELPER).write_text(STUB_HELPER)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    return root


def write_flux_universes(path, n_univ=2):
    f = ROOT.TFile(str(path), "RECREATE")
    n = len(DRV.PT_EDGES) - 1
    hcv = ROOT.TH1D("hFluxCV", "", n, array("d", DRV.PT_EDGES))
    hu = ROOT.TH2D("hFluxUniv", "", n, array("d", DRV.PT_EDGES), n_univ, 0, n_univ)
    for i in range(1, n + 1):
        hcv.SetBinContent(i, 1.0e-8 * i)                    # MK.write_flux's CV
        for u in range(n_univ):
            hu.SetBinContent(i, u + 1, 1.0e-8 * i * (1.0 + 0.03 * (u + 1)))
    hcv.Write()
    hu.Write()
    f.Close()
    return path


def output_objects(path):
    """Every object a driver output holds: histograms (both axes' bin edges, contents and errors
    with flow, entries), TNamed titles and TParameter values."""
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        name = key.GetName()
        if obj.InheritsFrom("TH1"):
            n = obj.GetNcells()
            out[name] = ("TH1", obj.GetDimension(),
                         [obj.GetXaxis().GetBinLowEdge(i) for i in range(1, obj.GetNbinsX() + 2)],
                         [obj.GetYaxis().GetBinLowEdge(i) for i in range(1, obj.GetNbinsY() + 2)],
                         np.array([obj.GetBinContent(i) for i in range(n)]).tobytes().hex(),
                         np.array([obj.GetBinError(i) for i in range(n)]).tobytes().hex(),
                         repr(obj.GetEntries()))
        elif obj.InheritsFrom("TNamed") and obj.ClassName() == "TNamed":
            out[name] = ("TNamed", obj.GetTitle())
        elif obj.ClassName().startswith("TParameter"):
            out[name] = ("TParameter", repr(obj.GetVal()))
        else:
            out[name] = (obj.ClassName(), None)
    f.Close()
    return out


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
@unittest.skipIf(os.path.isdir(ROOTED_HELPER_DIR),
                 "the driver's rooted insert (OI-136) would load the canonical helper instead of "
                 "the stub here, and the guard would refuse it")
class CommandLine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        inputs = cls.tmp / "inputs"
        inputs.mkdir()
        cls.omni = inputs / "omni.root"
        MK.write_fixture(str(cls.omni), rows=4000, extra=8)
        cls.flux = Path(MK.write_flux(str(inputs / "flux.root")))
        cls.flux_uni = write_flux_universes(inputs / "flux_universes.root")
        base_src = subprocess.run(["git", "-C", str(REPO), "show", f"{BASE_COMMIT}:{DRIVER_REL}"],
                                  capture_output=True, text=True)
        cls.base_src = base_src.stdout if base_src.returncode == 0 else None
        cls.root = make_checkout(cls.tmp, "live")
        cls.runs = {}
        for mode, extra in CLI_MODES.items():
            for setting in ("all", "derived"):
                cls.runs[(mode, setting)] = cls.unfold(cls.root, f"{mode}-{setting}",
                                                       (*extra, "--branch-select", setting))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def unfold(cls, root, tag, extra):
        out = cls.tmp / f"{tag}.root"
        cap = cls.tmp / f"{tag}.capture.json"
        inv = cls.tmp / f"{tag}.inv"
        env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1",
                   U2D_STUB_CAPTURE=str(cap))
        for k in [k for k in env if k.startswith("MNV_GUARD")]:
            env.pop(k)
        env["PYTHONPATH"] = os.pathsep.join(
            [str(root / "unbinned_unfolding/python")] +
            [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p])
        cmd = [sys.executable, str(root / GUARD), "--expect-root", str(root),
               "--inventory", str(inv), "--label", tag, "--", str(root / DRIVER_REL),
               "--omnifile", str(cls.omni), "--mcfile", str(cls.flux),
               "--flux-universe-file", str(cls.flux_uni), "--iters", "2", "--out", str(out),
               *extra]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cls.tmp)
        return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "out": out,
                "capture": json.loads(cap.read_text()) if cap.exists() else None, "inv": inv}

    def ok(self, run):
        self.assertEqual(run["rc"], 0, run["stderr"][-3000:])
        return run

    def test_every_mode_ran_under_the_guard_from_this_checkout(self):
        for key, run in self.runs.items():
            with self.subTest(run=key):
                self.ok(run)
                inv = [json.loads(x) for x in run["inv"].read_text().splitlines()]
                self.assertTrue(inv and all(i.get("repo_origin_count", 0) >= 1 for i in inv))
                objs = output_objects(run["out"])
                self.assertEqual(objs["driverFile"][1], str(self.root / DRIVER_REL))
                self.assertEqual(objs["omnifoldHelperFile"][1], str(self.root / HELPER))

    def test_omnifold_gets_the_same_inputs_and_estimator_arguments(self):
        for mode in CLI_MODES:
            with self.subTest(mode=mode):
                a = self.ok(self.runs[(mode, "all")])["capture"]
                b = self.ok(self.runs[(mode, "derived")])["capture"]
                self.assertEqual(a, b)
                self.assertGreater(min(a["sizes"]), 0)
                for k in ("classifier1_params", "classifier2_params", "regressor_params",
                          "estimator", "device", "measured_weights"):
                    self.assertIn(k, a["kwargs"])

    def test_outputs_differ_only_in_the_setting_records(self):
        for mode in CLI_MODES:
            with self.subTest(mode=mode):
                a = output_objects(self.ok(self.runs[(mode, "all")])["out"])
                b = output_objects(self.ok(self.runs[(mode, "derived")])["out"])
                self.assertIn("hXSec2D", a)
                self.assertEqual(set(b) - set(a), {"branchSelection"})
                self.assertEqual(set(a) - set(b), set())
                for name in set(a) - SETTING_DEPENDENT:
                    self.assertEqual(a[name], b[name], name)
                ca, cb = json.loads(a["runConfig"][1]), json.loads(b["runConfig"][1])
                self.assertEqual((ca.pop("branch_select"), cb.pop("branch_select")),
                                 ("all", "derived"))
                self.assertEqual((ca.pop("out"), cb.pop("out")),
                                 tuple(str(self.runs[(mode, s)]["out"])
                                       for s in ("all", "derived")))
                self.assertEqual(ca, cb)

    def test_the_derived_run_records_its_selections(self):
        loaders = {"cv": 4, "alt-closure": 3}                # closure skips mc_truth_denom
        for mode in CLI_MODES:
            with self.subTest(mode=mode):
                run = self.ok(self.runs[(mode, "derived")])
                rec = json.loads(output_objects(run["out"])["branchSelection"][1])
                self.assertEqual(rec["mode"], "derived")
                self.assertEqual(len(rec["loaders"]), loaders.get(mode, 4))
                for r in rec["loaders"]:
                    self.assertTrue(r["verified"])
                    self.assertLess(len(r["branches"]), r["n_branches_in_tree"])
                    self.assertIn(f"branch-select=derived: {r['tree']} read", run["stdout"])
                self.assertNotIn("branch-select=derived", self.runs[(mode, "all")]["stdout"])
        rec = json.loads(output_objects(self.runs[("lateral", "derived")]["out"])
                         ["branchSelection"][1])
        sel = {r["tree"]: r["branches"] for r in rec["loaders"]}
        self.assertEqual(sel["mc_truth_denom"], [f"pT_truth_{S}", f"pz_truth_{S}",
                                                 f"w_truth_{S}"])

    def test_the_default_equals_the_driver_before_this_change(self):
        if self.base_src is None:
            self.skipTest(f"git cannot supply {BASE_COMMIT}:{DRIVER_REL}")
        self.assertNotIn("branch_select", self.base_src)
        root = make_checkout(self.tmp, "base", driver_src=self.base_src)
        for mode in ("cv", "lateral", "vertical-flux", "bootstrap-negweight"):
            with self.subTest(mode=mode):
                old = self.ok(self.unfold(root, f"base-{mode}", CLI_MODES[mode]))
                new = self.ok(self.runs[(mode, "all")])
                self.assertEqual(old["capture"], new["capture"])
                a, b = output_objects(old["out"]), output_objects(new["out"])
                self.assertEqual(set(a), set(b))
                # Two checkouts and two output names: the paths differ, the helper's digest
                # does not, and the driver's digest does (it is the edit under test).
                differ = {k for k in a if a[k] != b[k]}
                self.assertEqual(differ, {"runConfig", "runArgv", "driverFile", "driverSha256",
                                          "omnifoldHelperFile"})
                self.assertEqual(a["omnifoldHelperSha256"], b["omnifoldHelperSha256"])
                ca, cb = json.loads(a["runConfig"][1]), json.loads(b["runConfig"][1])
                self.assertEqual(cb.pop("branch_select"), "all")
                self.assertEqual((ca.pop("out"), cb.pop("out")),
                                 (str(old["out"]), str(new["out"])))
                self.assertEqual(ca, cb)

    def test_mutant_activations_are_refused_through_the_entry_point(self):
        src = SCRIPT.read_text()
        old = "        apply_branch_selection(tree, names)\n"
        self.assertEqual(src.count(old), 1)
        for tag, new, why in (
                ("omit", "        apply_branch_selection(tree, names[:-1])\n", "inactive"),
                ("extra", "        apply_branch_selection(tree, names + [n for n in "
                          "tree_branch_names(tree) if n not in names][:1])\n", "active")):
            with self.subTest(control=tag):
                root = make_checkout(self.tmp, f"mutant-{tag}", src.replace(old, new))
                run = self.unfold(root, f"mutant-{tag}", CLI_MODES["lateral"] +
                                  ("--branch-select", "derived"))
                self.assertNotEqual(run["rc"], 0)
                self.assertIn("BranchSelectionError", run["stderr"])
                self.assertIn(why, run["stderr"])
                self.assertFalse(run["out"].exists())
                self.assertIsNone(run["capture"])               # stopped before training
                ok = self.ok(self.unfold(root, f"mutant-{tag}-default", CLI_MODES["lateral"]))
                self.assertEqual(ok["capture"], self.runs[("lateral", "all")]["capture"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
