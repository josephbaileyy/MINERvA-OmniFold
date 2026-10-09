"""KNOWN_ISSUES 84: a bootstrap replica must divide by the central value's completeness.

On a Phase-17 input, mc_signal_reco holds every truth-passing event of mc_truth_denom, so
the central value's completeness c = hOFInputTruth / hOFTruthDenom is 1 to rounding in
every bin. The Poisson(1) MC bootstrap used to multiply sig["w_truth"] before
`compute_omnifold_completeness_2d`, so a replica's numerator was resampled while its
denominator (mc_truth_denom, never resampled) was not. Each replica then divided by its
own c_b = sum(b*w)/sum(w), roughly 0.94-1.15 per bin on the production input. The
central value carries no such term.

These tests run the real `main()` end to end on a small synthetic Phase-17 input. Only
the OmniFold classifier is replaced, by a stub that returns unit weights, because the
completeness path does not depend on the trained weights. Each run is a subprocess, so
ROOT state does not leak between runs. The pre-fix reference is the script at
PRE_FIX_COMMIT, read from git.

Needs PyROOT and numpy. Skips when ROOT is unavailable or git cannot supply the pre-fix
blob. Locally:
  PYTHONPATH=$(root-config --libdir) python3.13 -m unittest \
      2d-unfolding/tests/test_bootstrap_completeness_ki84.py -v
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
U2D_DIR = HERE.parents[1]
REPO = HERE.parents[2]
SCRIPT = U2D_DIR / "unfold_2d_omnifold_unbinned.py"
PRE_FIX_COMMIT = "4e7c20bb"  # origin/main when the fix branch was cut

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover - depends on the host
    HAVE_ROOT = False

PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]
TAN20 = math.tan(math.radians(20.0))

# Runs main() with the OmniFold classifier stubbed out. argv[1] is the script to load
# (the current one or the pre-fix blob); the rest is passed to main().
RUNNER = textwrap.dedent("""
    import importlib.util, os, sys, types
    import numpy as np

    def _omnifold(MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass,
                  iters, **kw):
        return (np.ones(int(np.count_nonzero(pass_reco))),
                np.ones(int(np.count_nonzero(pass_truth))))

    ohf = types.ModuleType("omnifold.OmniFold_helper_functions")
    ohf.omnifold = _omnifold
    pkg = types.ModuleType("omnifold")
    pkg.OmniFold_helper_functions = ohf
    pkg.__path__ = []
    if os.environ.get("U2D_STUB_HELPER_FILE"):
        pkg.__file__ = os.environ["U2D_STUB_HELPER_FILE"]
    sys.modules["omnifold"] = pkg
    sys.modules["omnifold.OmniFold_helper_functions"] = ohf

    spec = importlib.util.spec_from_file_location("u2d_under_test", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.argv = ["unfold_2d_omnifold_unbinned.py"] + sys.argv[2:]
    mod.main()
""")


def _write_inputs(tmp, phase17=True, n_sig=6000, seed=20261005):
    """A small omnifile and flux file in the production schema.

    Phase 17: mc_truth_denom holds exactly the truth-passing rows of mc_signal_reco,
    with the same w_truth. Legacy: mc_truth_denom also holds rows absent from
    mc_signal_reco (about 25 %), so c is about 0.75.
    """
    import ROOT
    from array import array

    rng = np.random.default_rng(seed)
    pz = rng.uniform(1.5, 60.0, n_sig)
    pt = rng.uniform(0.0, 1.0, n_sig) * np.minimum(4.5, TAN20 * pz) * 0.999
    w_truth = rng.uniform(0.5, 1.5, n_sig)
    w_reco = w_truth * rng.uniform(0.9, 1.1, n_sig)
    sim_pass = rng.uniform(size=n_sig) < 0.7
    sim_pt = pt * rng.normal(1.0, 0.05, n_sig)
    sim_pz = pz * rng.normal(1.0, 0.03, n_sig)

    path = os.path.join(tmp, "omni_phase17.root" if phase17 else "omni_legacy.root")
    f = ROOT.TFile(path, "RECREATE")

    def tree(name, cols):
        t = ROOT.TTree(name, name)
        bufs = {}
        for c, (typ, _) in cols.items():
            bufs[c] = array(typ, [0])
            t.Branch(c, bufs[c], f"{c}/{'D' if typ == 'd' else 'b'}")
        n = len(next(iter(cols.values()))[1])
        for i in range(n):
            for c, (typ, vals) in cols.items():
                bufs[c][0] = float(vals[i]) if typ == "d" else int(vals[i])
            t.Fill()
        t.Write()

    tree("mc_signal_reco", {
        "MC": ("d", pt), "MC_pz": ("d", pz), "sim": ("d", sim_pt),
        "sim_pz": ("d", sim_pz), "sim_pass": ("B", sim_pass),
        "w_truth": ("d", w_truth), "w_reco": ("d", w_reco)})
    if phase17:
        d_pt, d_pz, d_w = pt, pz, w_truth
    else:
        n_extra = n_sig // 3
        e_pz = rng.uniform(1.5, 60.0, n_extra)
        e_pt = rng.uniform(0.0, 1.0, n_extra) * np.minimum(4.5, TAN20 * e_pz) * 0.999
        d_pt = np.concatenate([pt, e_pt])
        d_pz = np.concatenate([pz, e_pz])
        d_w = np.concatenate([w_truth, rng.uniform(0.5, 1.5, n_extra)])
    tree("mc_truth_denom", {"MC": ("d", d_pt), "MC_pz": ("d", d_pz), "w_truth": ("d", d_w)})

    sel = sim_pass
    n_data = int(sel.sum())
    tree("data", {"measured": ("d", sim_pt[sel] * rng.normal(1, 0.01, n_data)),
                  "measured_pz": ("d", sim_pz[sel] * rng.normal(1, 0.01, n_data)),
                  "measured_pass": ("B", np.ones(n_data, bool))})
    n_bkg = 300
    b_pz = rng.uniform(1.5, 60.0, n_bkg)
    tree("mc_background", {
        "sim_background": ("d", rng.uniform(0, 1, n_bkg) * np.minimum(4.5, TAN20 * b_pz)),
        "sim_background_pz": ("d", b_pz),
        "sim_background_pass": ("B", np.ones(n_bkg, bool)),
        "w_bkg": ("d", np.full(n_bkg, 0.2))})
    for name, val in (("dataPOTUsed", 1.0e20), ("mcPOTUsed", 1.0e20),
                      ("hasTruthOnlyMisses", 12.0 if phase17 else 0.0),
                      ("nTruthOnlyMisses", 1000.0 if phase17 else 0.0)):
        ROOT.TParameter("double")(name, val).Write()
    f.Close()

    flux = os.path.join(tmp, "flux.root")
    g = ROOT.TFile(flux, "RECREATE")
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", len(PT_EDGES) - 1,
                  array("d", PT_EDGES))
    for i in range(1, len(PT_EDGES)):
        h.SetBinContent(i, 1.0e-8 * i)
    h.Write()
    g.Close()
    return path, flux


def _run(script, omni, flux, out, extra=(), helper_file=None):
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "1"
    env.pop("U2D_STUB_HELPER_FILE", None)
    if helper_file:
        env["U2D_STUB_HELPER_FILE"] = helper_file
    cmd = [sys.executable, "-c", RUNNER, str(script), "--omnifile", omni,
           "--mcfile", flux, "--out", out, "--iters", "1", "--use-weights",
           "--seed", "1", *extra]
    p = subprocess.run(cmd, cwd=os.path.dirname(out), env=env,
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise AssertionError(f"run failed ({p.returncode}):\n{p.stdout[-3000:]}\n"
                             f"{p.stderr[-3000:]}")
    return p.stdout


def _read(out, name):
    import ROOT
    f = ROOT.TFile.Open(out)
    h = f.Get(name)
    if not h:
        raise AssertionError(f"{name} missing from {out}")
    a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                  for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a


def _pre_fix_script(tmp):
    git = shutil.which("git")
    if git is None:
        return None
    p = subprocess.run([git, "-C", str(REPO), "show",
                        f"{PRE_FIX_COMMIT}:2d-unfolding/unfold_2d_omnifold_unbinned.py"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return None
    path = os.path.join(tmp, "unfold_2d_pre_fix.py")
    with open(path, "w") as fh:
        fh.write(p.stdout)
    return path


@unittest.skipUnless(HAVE_ROOT, "PyROOT not importable")
class BootstrapCompletenessMatchesCentral(unittest.TestCase):
    """The KNOWN_ISSUES 84 regression, on the real pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="ki84_")
        cls.omni, cls.flux = _write_inputs(cls.tmp, phase17=True)
        cls.out = {}
        for tag, extra in (("central", ()),
                           ("boot7", ("--bootstrap-seed", "7")),
                           ("boot8", ("--bootstrap-seed", "8")),
                           ("boot7_data", ("--bootstrap-seed", "7",
                                           "--bootstrap-streams", "data"))):
            out = os.path.join(cls.tmp, f"{tag}.root")
            cls.out[tag + "_log"] = _run(SCRIPT, cls.omni, cls.flux, out, extra)
            cls.out[tag] = out

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _support(self):
        return _read(self.out["central"], "hOFTruthDenom2D") > 0

    def test_fixture_is_phase17_with_unit_central_completeness(self):
        # Premise: without it the replica checks below prove nothing.
        sup = self._support()
        self.assertGreater(int(sup.sum()), 100)
        c = _read(self.out["central"], "hOFCompleteness2D")
        self.assertLess(float(np.abs(c[sup] - 1.0).max()), 1e-12)
        self.assertIn("Phase-17 mode", self.out["central_log"])

    def test_bootstrapped_replica_has_unit_completeness_in_every_bin(self):
        sup = self._support()
        for tag in ("boot7", "boot8"):
            c = _read(self.out[tag], "hOFCompleteness2D")
            dev = float(np.abs(c[sup] - 1.0).max())
            self.assertLess(dev, 1e-12, f"{tag}: max |c-1| = {dev:.3g} over "
                            f"{int(sup.sum())} bins")

    def test_bootstrapped_completeness_is_bitwise_the_central_value(self):
        c0 = _read(self.out["central"], "hOFCompleteness2D")
        for tag in ("boot7", "boot8", "boot7_data"):
            np.testing.assert_array_equal(
                _read(self.out[tag], "hOFCompleteness2D"), c0, err_msg=tag)

    def test_replicas_still_resample_the_mc(self):
        # Positive control: the fix must not switch the MC bootstrap off.
        u0 = _read(self.out["central"], "hUnfold2D")
        u7 = _read(self.out["boot7"], "hUnfold2D")
        u8 = _read(self.out["boot8"], "hUnfold2D")
        sup = self._support()
        self.assertGreater(float(np.abs(u7[sup] / u0[sup] - 1).max()), 1e-3)
        self.assertFalse(np.array_equal(u7, u8))


@unittest.skipUnless(HAVE_ROOT, "PyROOT not importable")
class PathsTheFixMustNotChange(unittest.TestCase):
    """Bit-identity against the pre-fix script on the paths outside the fix."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="ki84_ref_")
        cls.pre = _pre_fix_script(cls.tmp)
        if cls.pre is None:
            raise unittest.SkipTest(f"git cannot supply {PRE_FIX_COMMIT}")
        cls.p17 = _write_inputs(cls.tmp, phase17=True)
        cls.leg = _write_inputs(cls.tmp, phase17=False)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    HISTS = ("hXSec2D", "hUnfold2D", "hOFCompleteness2D", "hOFInputTruth2D",
             "hOFTruthDenom2D", "hEff2D")

    def _same(self, inputs, extra, tag, hists=HISTS):
        omni, flux = inputs
        new = os.path.join(self.tmp, f"{tag}_new.root")
        old = os.path.join(self.tmp, f"{tag}_old.root")
        _run(SCRIPT, omni, flux, new, extra)
        _run(self.pre, omni, flux, old, extra)
        for h in hists:
            np.testing.assert_array_equal(_read(new, h), _read(old, h),
                                          err_msg=f"{tag}: {h}")

    def test_central_value_is_bit_identical(self):
        self._same(self.p17, (), "central")

    def test_legacy_input_bootstrap_is_unchanged(self):
        # Out of scope by design: a pre-Phase-17 input keeps its resampled c.
        self._same(self.leg, ("--bootstrap-seed", "7"), "legacy_boot")

    def test_data_only_bootstrap_is_bit_identical(self):
        self._same(self.p17, ("--bootstrap-seed", "7", "--bootstrap-streams", "data"),
                   "data_only")

    def test_bootstrapped_unfold_is_unchanged(self):
        # The fix changes only the divisor; the resampled unfolded counts stay as they were.
        self._same(self.p17, ("--bootstrap-seed", "7"), "boot_unfold",
                   hists=("hUnfold2D", "hOFTruthDenom2D", "hEff2D"))


def _named(out, name):
    import ROOT
    f = ROOT.TFile.Open(out)
    obj = f.Get(name)
    title = obj.GetTitle() if obj else None
    f.Close()
    return title


@unittest.skipUnless(HAVE_ROOT, "PyROOT not importable")
class RunProvenanceIsRecorded(unittest.TestCase):
    """Each output names its effective settings and the OmniFold helper that ran.

    Placed here because this file is the end-to-end harness for main(). The 2026-10-08
    pairing audit could not tell from the products which backend, seed or helper made
    them: the central value omits --estimator, so its backend was only the launcher's
    absence of a flag, and the helper arrives through the rooted insert in main().
    """

    @classmethod
    def setUpClass(cls):
        import hashlib
        cls.tmp = tempfile.mkdtemp(prefix="u2d_prov_")
        cls.omni, cls.flux = _write_inputs(cls.tmp, phase17=True)
        cls.helper = os.path.join(cls.tmp, "omnifold_stand_in.py")
        with open(cls.helper, "w") as fh:
            fh.write("# stand-in for unbinned_unfolding/python/omnifold.py\n")
        cls.helper_sha = hashlib.sha256(open(cls.helper, "rb").read()).hexdigest()
        cls.script_sha = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
        cls.out = {}
        for tag, extra, helper in (
                ("central", (), cls.helper),
                ("boot7_mc", ("--bootstrap-seed", "7", "--bootstrap-streams", "mc",
                              "--estimator", "lgbm"), cls.helper),
                ("no_helper_file", (), None)):
            out = os.path.join(cls.tmp, f"{tag}.root")
            _run(SCRIPT, cls.omni, cls.flux, out, extra, helper_file=helper)
            cls.out[tag] = out

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_an_omitted_flag_is_recorded_by_its_effective_value(self):
        import json
        cfg = json.loads(_named(self.out["central"], "runConfig"))
        self.assertEqual(cfg["estimator"], "exact")
        self.assertEqual(cfg["seed"], 1)
        self.assertIsNone(cfg["bootstrap_seed"])
        self.assertEqual(cfg["bkg_mode"], "purity")

    def test_bootstrap_settings_are_recorded(self):
        import json
        cfg = json.loads(_named(self.out["boot7_mc"], "runConfig"))
        self.assertEqual((cfg["estimator"], cfg["bootstrap_seed"], cfg["bootstrap_streams"]),
                         ("lgbm", 7, "mc"))
        argv = json.loads(_named(self.out["boot7_mc"], "runArgv"))
        self.assertIn("--bootstrap-streams", argv)

    def test_driver_bytes_are_identified(self):
        self.assertEqual(_named(self.out["central"], "driverSha256"), self.script_sha)
        self.assertEqual(_named(self.out["central"], "driverFile"), str(SCRIPT))

    def test_the_imported_helper_is_identified_by_path_and_digest(self):
        self.assertEqual(_named(self.out["central"], "omnifoldHelperFile"),
                         os.path.abspath(self.helper))
        self.assertEqual(_named(self.out["central"], "omnifoldHelperSha256"), self.helper_sha)

    def test_a_helper_without_a_file_is_reported_unavailable_not_guessed(self):
        self.assertEqual(_named(self.out["no_helper_file"], "omnifoldHelperFile"), "unavailable")
        self.assertEqual(_named(self.out["no_helper_file"], "omnifoldHelperSha256"), "unavailable")

    def test_recording_provenance_leaves_the_histograms_alone(self):
        np.testing.assert_array_equal(_read(self.out["central"], "hXSec2D"),
                                      _read(self.out["no_helper_file"], "hXSec2D"))


if __name__ == "__main__":
    unittest.main()
