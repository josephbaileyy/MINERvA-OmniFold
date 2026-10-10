"""Synthetic tests: the toy and KI-85 producers execute this checkout's code, record it, and refuse
before any output when they cannot.

Each test builds throwaway checkouts holding copies of the real producer, driver, toy design, guard
and ``n2/execution.py``, and a STUB OmniFold helper (and stub ``analyze_uq``) whose result says which
checkout's copy ran: checkout ``A`` scales the unfolded weights by 2, checkout ``B`` by 3. No
classifier is trained, nothing is submitted, and no real input is read.

The ROOT-dependent tests skip without PyROOT. Locally:
  PYTHONPATH=$(root-config --libdir) python3.13 -m unittest discover -s \
      2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_*.py' -v
"""
import json
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from n2 import execution as gx  # noqa: E402

try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:  # pragma: no cover - depends on the host
    HAVE_ROOT = False

COPIED = ("nd-unfolding/mnv_guarded_run.py",
          "2d-unfolding/unfold_2d_omnifold_unbinned.py",
          "2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py",
          "2d-unfolding/uq/coverage_fixed_truth/toy_design.py",
          "2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py",
          "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
          "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py")
TOY = "2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py"
KI85 = "2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py"
HELPER = "unbinned_unfolding/python/omnifold.py"
ANALYZE = "2d-unfolding/uq/analyze_uq.py"

STUB_HELPER = textwrap.dedent('''\
    import json, os
    import numpy as np
    FACTOR = {factor}

    class OmniFold_helper_functions:
        @staticmethod
        def omnifold(MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass, iters, **kw):
            sink = os.environ.get("STUB_KWARGS_SINK")
            if sink:
                with open(sink, "w") as fh:
                    json.dump({{"iters": iters, "estimator": kw.get("estimator"),
                               "device": kw.get("device"),
                               "classifier1_params": kw.get("classifier1_params"),
                               "classifier2_params": kw.get("classifier2_params"),
                               "regressor_params": kw.get("regressor_params"),
                               "n_measured": int(len(measured))}}, fh)
            return (np.ones(int(np.count_nonzero(pass_reco))),
                    np.full(int(np.count_nonzero(pass_truth)), float(FACTOR)))
    ''')
STUB_ANALYZE = textwrap.dedent('''\
    import sys as _sys, pathlib as _pathlib
    for _a in _pathlib.Path(__file__).resolve().parents:
        if (_a / "technote_style.py").exists():
            _sys.path.insert(0, str(_a)); break
    import technote_style  # noqa: F401  (the real analyze_uq.py:27-31 shape)
    import numpy as np
    FACTOR = {factor}

    def th2_to_array(h):
        return FACTOR * np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                                  for i in range(1, h.GetNbinsX() + 1)])
    ''')

PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
TAN20 = math.tan(math.radians(20.0))


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                           "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                           *args], capture_output=True, text=True, check=True).stdout.strip()


def make_checkout(base, name, factor, commit=True):
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    for rel in COPIED:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, root / rel)
    shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for rel, text in ((HELPER, STUB_HELPER), (ANALYZE, STUB_ANALYZE),
                      ("technote_style.py", "STYLE = {factor}\n")):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text.format(factor=factor))
    if commit:
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture")
    return root


def sha(path):
    return gx.sha256_hex(Path(path).read_bytes())


def expectations(root, inputs, **override):
    mods = {rel: sha(root / rel) for rel in
            (TOY, "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
             "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py",
             "2d-unfolding/uq/coverage_fixed_truth/toy_design.py",
             "2d-unfolding/unfold_2d_omnifold_unbinned.py", HELPER)}
    exp = {"commit": git(root, "rev-parse", "HEAD"), "modules": mods,
           "inputs": {k: sha(v) for k, v in inputs.items()}}
    exp.update(override)
    return exp


def write_inputs(tmp, n_sig=3000, seed=20261009):
    """A small omnifile and flux file in the production schema (as the KI-84 test builds them)."""
    import ROOT
    from array import array
    rng = np.random.default_rng(seed)
    pz = rng.uniform(1.5, 60.0, n_sig)
    pt = rng.uniform(0.0, 1.0, n_sig) * np.minimum(4.5, TAN20 * pz) * 0.999
    w_truth = rng.uniform(0.5, 1.5, n_sig)
    w_reco = w_truth * rng.uniform(0.9, 1.1, n_sig)
    sim_pass = rng.uniform(size=n_sig) < 0.7
    sim_pt, sim_pz = pt * rng.normal(1.0, 0.05, n_sig), pz * rng.normal(1.0, 0.03, n_sig)
    path = os.path.join(tmp, "omni.root")
    f = ROOT.TFile(path, "RECREATE")

    def tree(name, cols):
        t = ROOT.TTree(name, name)
        bufs = {}
        for c, (typ, _) in cols.items():
            bufs[c] = array(typ, [0])
            t.Branch(c, bufs[c], f"{c}/{'D' if typ == 'd' else 'b'}")
        for i in range(len(next(iter(cols.values()))[1])):
            for c, (typ, vals) in cols.items():
                bufs[c][0] = float(vals[i]) if typ == "d" else int(vals[i])
            t.Fill()
        t.Write()

    tree("mc_signal_reco", {"MC": ("d", pt), "MC_pz": ("d", pz), "sim": ("d", sim_pt),
                            "sim_pz": ("d", sim_pz), "sim_pass": ("B", sim_pass),
                            "w_truth": ("d", w_truth), "w_reco": ("d", w_reco)})
    tree("mc_truth_denom", {"MC": ("d", pt), "MC_pz": ("d", pz), "w_truth": ("d", w_truth)})
    n_data = int(sim_pass.sum())
    tree("data", {"measured": ("d", sim_pt[sim_pass]), "measured_pz": ("d", sim_pz[sim_pass]),
                  "measured_pass": ("B", np.ones(n_data, bool))})
    b_pz = rng.uniform(1.5, 60.0, 200)
    tree("mc_background", {
        "sim_background": ("d", rng.uniform(0, 1, 200) * np.minimum(4.5, TAN20 * b_pz)),
        "sim_background_pz": ("d", b_pz), "sim_background_pass": ("B", np.ones(200, bool)),
        "w_bkg": ("d", np.full(200, 0.2))})
    for name, val in (("dataPOTUsed", 1.0e20), ("mcPOTUsed", 1.0e20),
                      ("hasTruthOnlyMisses", 12.0), ("nTruthOnlyMisses", 0.0)):
        ROOT.TParameter("double")(name, val).Write()
    f.Close()
    flux = os.path.join(tmp, "flux.root")
    g = ROOT.TFile(flux, "RECREATE")
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", len(PT_EDGES) - 1, array("d", PT_EDGES))
    for i in range(1, len(PT_EDGES)):
        h.SetBinContent(i, 1.0e-8 * i)
    h.Write()
    g.Close()
    return {"omnifile": path, "mcfile": flux}


def pre_import(directory, name):
    """A ``-c`` program: import ``name`` from ``directory``, then run argv[1] as ``__main__``."""
    return (f"import runpy, sys; sys.path.insert(0, {str(directory)!r}); import {name}; "
            "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')")


def run(argv, env_extra=None, cwd=None):
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    for k in [k for k in env if k.startswith("MNV_GUARD")]:
        env.pop(k)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True,
                          env=env, cwd=cwd)


class Checkouts(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
        self.a = make_checkout(self.tmp, "A", 2)
        self.b = make_checkout(self.tmp, "B", 3)


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class TheToyProducer(Checkouts):
    def setUp(self):
        super().setUp()
        self.inputs = write_inputs(str(self.tmp))
        self.base = ["--no-fluctuation", "--omnifile", self.inputs["omnifile"],
                     "--mcfile", self.inputs["mcfile"], "--iters", "1", "--seed", "7"]

    def guarded(self, root, out, extra=(), expect_root=None, env_extra=None):
        return run([root / "nd-unfolding/mnv_guarded_run.py", "--expect-root",
                    expect_root or root, "--", root / TOY, *self.base, "--out", out, *extra],
                   env_extra=env_extra)

    def write_exp(self, exp, name="exp.json"):
        path = self.tmp / name
        path.write_text(json.dumps(exp))
        return path

    def read(self, out):
        import ROOT
        f = ROOT.TFile.Open(str(out))
        unf, prior = f.Get("hUnfold2D").Integral(), f.Get("hTruth2D").Integral()
        prov = json.loads(f.Get("producerProvenance").GetTitle())
        helper = (f.Get("omnifoldHelperFile").GetTitle(), f.Get("omnifoldHelperSha256").GetTitle())
        f.Close()
        return unf / prior, prov, helper

    def test_strict_guarded_run_executes_this_checkouts_helper_and_records_it(self):
        """Positive control: exit 0, the A helper's factor 2 in the output, every file at HEAD."""
        out, sink = self.tmp / "a.root", self.tmp / "kwargs.json"
        exp = self.write_exp(expectations(self.a, self.inputs))
        cp = self.guarded(self.a, out, ["--expect", exp, "--require-provenance"],
                          env_extra={"STUB_KWARGS_SINK": str(sink)})
        self.assertEqual(cp.returncode, 0, cp.stdout[-2000:] + cp.stderr[-3000:])
        ratio, prov, helper = self.read(out)
        self.assertAlmostEqual(ratio, 2.0, places=12)
        self.assertEqual(helper, (str(self.a / HELPER), sha(self.a / HELPER)))
        self.assertTrue(prov["strict"] and prov["guard"]["installed"])
        self.assertEqual(prov["guard"]["expect_root"], str(self.a))
        self.assertEqual(prov["git"]["commit"], git(self.a, "rev-parse", "HEAD"))
        self.assertEqual(prov["git"]["mismatched"], [])
        self.assertEqual({r["relpath"] for r in prov["executed"]}, set(json.loads(
            exp.read_text())["modules"]))
        self.assertTrue(all(r["path"].startswith(str(self.a)) for r in prov["executed"]))
        self.assertEqual(prov["inputs"]["omnifile"]["sha256"], sha(self.inputs["omnifile"]))
        # The recorded estimator arguments are the ones the helper received.
        got = json.loads(sink.read_text())
        for key in ("iters", "estimator", "device", "classifier1_params", "classifier2_params",
                    "regressor_params"):
            self.assertEqual(got[key], prov["estimator"][key], key)
        self.assertEqual(got["classifier1_params"], {"random_state": 7})

    def b_first(self):
        return {"PYTHONPATH": os.pathsep.join(filter(None, [
            str(self.b / "unbinned_unfolding/python"), str(self.b / "2d-unfolding"),
            os.environ.get("PYTHONPATH")]))}

    def test_control_the_pre_repair_toy_executes_the_other_checkouts_helper(self):
        """The fixture really hijacks: the toy as of 5ac9706a runs B's helper (factor 3) from A."""
        old = subprocess.run(["git", "-C", str(REPO), "show", f"5ac9706a:{TOY}"],
                             capture_output=True, text=True)
        if old.returncode != 0:
            self.skipTest("git cannot supply the pre-repair blob")
        script = self.a / TOY.replace("fixed_truth_toy", "fixed_truth_toy_pre_repair")
        script.write_text(old.stdout)
        out = self.tmp / "old.root"
        cp = run([script, *self.base, "--out", out], env_extra=self.b_first())
        self.assertEqual(cp.returncode, 0, cp.stderr[-3000:])
        import ROOT
        f = ROOT.TFile.Open(str(out))
        ratio = f.Get("hUnfold2D").Integral() / f.Get("hTruth2D").Integral()
        has_record = bool(f.Get("producerProvenance"))
        f.Close()
        self.assertAlmostEqual(ratio, 3.0, places=12)
        self.assertFalse(has_record)

    def test_a_conflicting_checkout_first_on_the_path_does_not_change_what_runs(self):
        """B's helper directory at the front of PYTHONPATH: A's helper still executes."""
        out = self.tmp / "a.root"
        cp = run([self.a / TOY, *self.base, "--out", out], env_extra=self.b_first())
        self.assertEqual(cp.returncode, 0, cp.stderr[-3000:])
        ratio, prov, helper = self.read(out)
        self.assertAlmostEqual(ratio, 2.0, places=12)
        self.assertEqual(helper[0], str(self.a / HELPER))
        self.assertFalse(prov["strict"])

    def test_a_pre_imported_helper_from_another_checkout_refuses_before_output(self):
        out = self.tmp / "a.root"
        cp = run(["-c", pre_import(self.b / "unbinned_unfolding/python", "omnifold"),
                  self.a / TOY, *self.base, "--out", out])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("already imported", cp.stderr)
        self.assertIn(str(self.b), cp.stderr)
        self.assertFalse(out.exists())

    def test_changed_helper_bytes_refuse_before_the_helper_runs(self):
        exp = self.write_exp(expectations(self.a, self.inputs))
        with open(self.a / HELPER, "a") as fh:
            fh.write("open(__file__ + '.executed', 'w').close()\n")
        out = self.tmp / "a.root"
        cp = self.guarded(self.a, out, ["--expect", exp])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn(HELPER.split("/")[-1], cp.stderr)
        self.assertFalse(out.exists())
        self.assertFalse(Path(str(self.a / HELPER) + ".executed").exists(),
                         "the mismatched helper's module body ran before the refusal")

    def test_a_module_symlinked_outside_the_checkout_is_a_refusal_not_a_crash(self):
        """Review R1: the toy's own relative-path step exits 3 like every other refusal."""
        out = self.tmp / "a.root"
        for rel in ("2d-unfolding/uq/coverage_fixed_truth/toy_design.py",
                    "2d-unfolding/unfold_2d_omnifold_unbinned.py", HELPER):
            with self.subTest(rel):
                kept = (self.a / rel).read_bytes()
                (self.a / rel).unlink()
                (self.a / rel).symlink_to(self.b / rel)
                try:
                    cp = run([self.a / TOY, *self.base, "--out", out])
                finally:
                    (self.a / rel).unlink()
                    (self.a / rel).write_bytes(kept)
                self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
                self.assertIn("resolves outside the admitted checkout", cp.stderr)
                self.assertNotIn("Traceback", cp.stderr)
                self.assertFalse(out.exists())

    def test_strict_mode_refuses_a_committed_helper_edited_since_head(self):
        """No --expect digest for the helper: strict still refuses bytes that are not HEAD's."""
        exp = expectations(self.a, self.inputs)
        (self.a / HELPER).write_text((self.a / HELPER).read_text() + "# drift\n")
        exp["modules"][HELPER] = sha(self.a / HELPER)
        cp = self.guarded(self.a, self.tmp / "a.root",
                          ["--expect", self.write_exp(exp), "--require-provenance"])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("differ from HEAD", cp.stderr)

    def test_strict_mode_refuses_missing_provenance(self):
        exp = expectations(self.a, self.inputs)
        cases = {
            "unguarded": (lambda out: run([self.a / TOY, *self.base, "--out", out, "--expect",
                                           self.write_exp(exp), "--require-provenance"]),
                          "not running under"),
            "no expectations": (lambda out: self.guarded(self.a, out, ["--require-provenance"]),
                                "stated commit"),
            "no commit": (lambda out: self.guarded(
                self.a, out, ["--expect", self.write_exp(dict(exp, commit=None), "e3.json"),
                              "--require-provenance"]), "stated commit"),
            "no input digest": (lambda out: self.guarded(
                self.a, out, ["--expect", self.write_exp(dict(exp, inputs={}), "e2.json"),
                              "--require-provenance"]), "input digests"),
        }
        for label, (go, needle) in cases.items():
            with self.subTest(label):
                out = self.tmp / f"{label}.root"
                cp = go(out)
                self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
                self.assertIn(needle, cp.stderr)
                self.assertFalse(out.exists())

    def test_strict_mode_refuses_without_git_identity(self):
        c = make_checkout(self.tmp, "C", 2, commit=False)
        exp = dict(expectations(self.a, self.inputs), commit=None)
        exp["modules"] = {rel: sha(c / rel) for rel in exp["modules"]}
        cp = self.guarded(c, self.tmp / "c.root",
                          ["--expect", self.write_exp(exp), "--require-provenance"])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("commit unavailable", cp.stderr)

    def test_the_guard_refuses_a_script_from_another_checkout(self):
        cp = run([self.b / "nd-unfolding/mnv_guarded_run.py", "--expect-root", self.b, "--",
                  self.a / TOY, *self.base, "--out", self.tmp / "x.root"])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("SCRIPT OUTSIDE THE EXPECTED TREE", cp.stderr)
        self.assertFalse((self.tmp / "x.root").exists())

    def test_strict_mode_refuses_to_overwrite_and_leaves_the_file_untouched(self):
        out = self.tmp / "a.root"
        out.write_bytes(b"an existing result\n")
        cp = self.guarded(self.a, out, ["--expect", self.write_exp(
            expectations(self.a, self.inputs)), "--require-provenance"])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("refusing to overwrite", cp.stderr)
        self.assertEqual(out.read_bytes(), b"an existing result\n")


class TheKi85Producer(Checkouts):
    """Refusals happen before ``import ROOT``, so these run without PyROOT."""

    def test_a_pre_imported_analyzer_from_another_checkout_refuses(self):
        out = self.tmp / "k.json"
        cp = run(["-c", pre_import(self.b / "2d-unfolding/uq", "analyze_uq"), self.a / KI85,
                  "--out", out])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn(str(self.b), cp.stderr)
        self.assertFalse(out.exists())

    def test_a_changed_analyzer_refuses_before_its_body_runs(self):
        exp = self.tmp / "exp.json"
        exp.write_text(json.dumps({"modules": {ANALYZE: sha(self.a / ANALYZE)}}))
        with open(self.a / ANALYZE, "a") as fh:
            fh.write("open(__file__ + '.executed', 'w').close()\n")
        cp = run([self.a / KI85, "--out", self.tmp / "k.json", "--expect", exp])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("analyze_uq", cp.stderr)
        self.assertFalse(Path(str(self.a / ANALYZE) + ".executed").exists(),
                         "the mismatched analyzer's module body ran before the refusal")

    def ki85_strict(self, exp):
        path = self.tmp / "kexp.json"
        path.write_text(json.dumps(exp))
        out = self.tmp / "k.json"
        cp = run([self.a / "nd-unfolding/mnv_guarded_run.py", "--expect-root", self.a, "--",
                  self.a / KI85, "--out", out, "--expect", path, "--require-provenance"])
        return cp, out

    def ki85_modules(self, root):
        return {rel: sha(root / rel) for rel in (
            KI85, ANALYZE, "technote_style.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py",
            "2d-unfolding/uq/coverage_fixed_truth/n2/execution.py")}

    def test_strict_mode_records_and_head_checks_the_analyzers_own_imports(self):
        """analyze_uq imports technote_style normally: strict mode must see it (review M2)."""
        exp = {"commit": git(self.a, "rev-parse", "HEAD"), "modules": self.ki85_modules(self.a),
               "inputs": {}}
        del exp["modules"]["technote_style.py"]
        cp, out = self.ki85_strict(exp)
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("technote_style.py", cp.stderr)
        (self.a / "technote_style.py").write_text("STYLE = 'edited after the commit'\n")
        exp["modules"] = self.ki85_modules(self.a)
        cp, out = self.ki85_strict(exp)
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("differ from HEAD", cp.stderr)
        self.assertIn("technote_style.py", cp.stderr)
        self.assertFalse(out.exists())

    def test_strict_mode_refuses_unguarded(self):
        cp = run([self.a / KI85, "--out", self.tmp / "k.json", "--require-provenance"])
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr[-3000:])
        self.assertIn("not running under", cp.stderr)

    @unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
    def test_guarded_run_reads_through_this_checkouts_analyzer(self):
        """Positive control: A's analyzer (x2) runs, and the result equals the pure functions'."""
        import ROOT
        rng = np.random.default_rng(5)
        n_pt, n_pz = 14, 16
        rep = np.zeros((n_pt, n_pz), bool)
        rep.flat[:40] = True
        state = self.a / "docs/orchestration/state"
        (state / "coverage-2d-20261005").mkdir(parents=True)
        (state / "ki84-adopt-20261006").mkdir(parents=True)
        T = rng.uniform(1, 2, (n_pt, n_pz))
        np.savez(state / "coverage-2d-20261005/interim.npz", reported=rep, prod_mean=T, T=T)
        (state / "ki84-adopt-20261006/purity_fdata.json").write_text(
            json.dumps({"purity_reco": np.ones((n_pt, n_pz)).tolist()}))
        arrays = {}
        for arm, pattern, n, s in (("armB", "armB/boot{}.root", 50, 0.010),
                                   ("armT", "armT/toy{}.root", 50, 0.012),
                                   ("realboot", "boot_data/2d_xsec_MEFHC_5iter_lgbm_boot{}.root", 200,
                                    0.02)):
            X = []
            for i in range(1, n + 1):
                v = T * (1 + s * rng.standard_normal(T.shape))
                p = self.tmp / "data" / pattern.format(i)
                p.parent.mkdir(parents=True, exist_ok=True)
                f = ROOT.TFile(str(p), "RECREATE")
                h = ROOT.TH2D("hXSec2D", "", n_pt, 0, 1, n_pz, 0, 1)
                for ix in range(n_pt):
                    for iy in range(n_pz):
                        h.SetBinContent(ix + 1, iy + 1, v[ix, iy])
                h.Write()
                f.Close()
                if arm != "realboot":
                    Path(str(p) + ".done").touch()
                X.append(2 * v.ravel(order="C")[rep.ravel(order="C")])
            arrays[arm] = np.array(X)
        runner = self.a / "2d-unfolding/uq/coverage_fixed_truth/run_ki85_fixture.py"
        runner.write_text(textwrap.dedent(f'''\
            import sys
            import ki85_compare as kc
            kc.OUTROOT = {str(self.tmp / "data")!r}
            kc.REALBOOT = {str(self.tmp / "data/boot_data")!r}
            sys.argv = ["ki85_compare.py"] + sys.argv[1:]
            kc.main()
            '''))
        git(self.a, "add", "-A")
        git(self.a, "commit", "-q", "-m", "fixture inputs")
        out = self.tmp / "k.json"
        cp = run([self.a / "nd-unfolding/mnv_guarded_run.py", "--expect-root", self.a, "--",
                  runner, "--out", out])
        self.assertEqual(cp.returncode, 0, cp.stderr[-3000:])
        res = json.loads(out.read_text())
        prov = res["provenance"]
        analyzer = next(r for r in prov["executed"] if r["relpath"] == ANALYZE)
        self.assertEqual(analyzer["path"], str(self.a / ANALYZE))
        self.assertEqual(prov["git"]["mismatched"], [])
        self.assertEqual(len(prov["replicas"]["realboot"]), 200)
        import ki85_compare as kc
        rho = kc.per_bin_ratios(arrays["armB"], arrays["armT"], arrays["realboot"],
                                np.ones(int(rep.sum())))
        self.assertAlmostEqual(res["sigma_B_over_sigma_T"]["median"],
                               float(np.median(rho["rho1"])), places=12)
        self.assertEqual(res["median_rel_spread_pct"]["armB"],
                         float(100 * np.median(kc.rel_spread(arrays["armB"]))))


class TheLoader(unittest.TestCase):
    """``load_verified`` in-process."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
        self.mod = self.root / "pkg" / "victim_mod_n2.py"
        self.mod.parent.mkdir()
        self.mod.write_text("MARK = 'verified'\n")
        self.addCleanup(sys.modules.pop, "victim_mod_n2", None)

    def test_executes_the_hashed_bytes_and_records_them(self):
        mod, rec = gx.load_verified("victim_mod_n2", self.mod, self.root)
        self.assertEqual(mod.MARK, "verified")
        self.assertEqual(rec["sha256"], sha(self.mod))
        self.assertEqual(rec["relpath"], "pkg/victim_mod_n2.py")
        again, _ = gx.load_verified("victim_mod_n2", self.mod, self.root)
        self.assertIs(again, mod)

    def test_refuses_outside_the_root(self):
        with self.assertRaises(gx.ProvenanceRefusal):
            gx.load_verified("victim_mod_n2", self.mod, self.root / "pkg" / "elsewhere")

    def test_refuses_a_module_imported_by_anything_else(self):
        sys.modules["victim_mod_n2"] = type(sys)("victim_mod_n2")
        with self.assertRaisesRegex(gx.ProvenanceRefusal, "already imported"):
            gx.load_verified("victim_mod_n2", self.mod, self.root)

    def test_refuses_a_digest_mismatch_without_executing(self):
        self.mod.write_text("raise SystemExit('executed')\n")
        with self.assertRaisesRegex(gx.ProvenanceRefusal, "expected"):
            gx.load_verified("victim_mod_n2", self.mod, self.root, expect_sha256="0" * 64)
        self.assertNotIn("victim_mod_n2", sys.modules)

    def test_require_guard_refuses_absent_wrong_and_widened_guards(self):
        root = str(self.root)
        for state, needle in (
                ({"installed": False}, "not running"),
                ({"installed": True, "expect_root": "/other", "allowed": ["/other"]}, "enforces"),
                ({"installed": True, "expect_root": root, "allowed": [root, "/x"]}, "also allows")):
            with self.subTest(needle):
                with self.assertRaisesRegex(gx.ProvenanceRefusal, needle):
                    gx.require_guard(root, state)
        gx.require_guard(root, {"installed": True, "expect_root": root, "allowed": [root]})

    def test_a_file_outside_the_root_is_a_refusal_not_a_crash(self):
        with self.assertRaises(gx.ProvenanceRefusal):
            gx.file_record(self.mod, b"", self.root / "pkg" / "elsewhere")

    def test_reserve_output_is_exclusive(self):
        out = self.root / "out.root"
        gx.reserve_output(out)
        with self.assertRaisesRegex(gx.ProvenanceRefusal, "refusing to overwrite"):
            gx.reserve_output(out)

    def test_a_repository_module_imported_after_the_check_is_caught(self):
        late = self.root / "pkg" / "late_mod_n2.py"
        late.write_text("X = 1\n")
        sys.path.insert(0, str(late.parent))
        self.addCleanup(sys.path.remove, str(late.parent))
        self.addCleanup(sys.modules.pop, "late_mod_n2", None)
        import late_mod_n2  # noqa: F401
        with self.assertRaisesRegex(gx.ProvenanceRefusal, "late_mod_n2"):
            gx.recheck(self.root, {"executed": [], "strict": True})
        ident = gx.recheck(self.root, {"executed": [], "strict": False})
        self.assertIn("pkg/late_mod_n2.py", {r["relpath"] for r in ident["executed"]})

    def test_git_identity_ignores_a_GIT_DIR_naming_another_repository(self):
        if shutil.which("git") is None:
            self.skipTest("no git")
        heads = {}
        for name in ("this", "other"):
            r = self.root / name
            r.mkdir()
            (r / "f.txt").write_text(name)
            git(r, "init", "-q")
            git(r, "add", "-A")
            git(r, "commit", "-q", "-m", name)
            heads[name] = git(r, "rev-parse", "HEAD")
        old = os.environ.get("GIT_DIR")
        os.environ["GIT_DIR"] = str(self.root / "other" / ".git")
        try:
            got = gx.git_identity(self.root / "this", [])
        finally:
            if old is None:
                os.environ.pop("GIT_DIR")
            else:
                os.environ["GIT_DIR"] = old
        self.assertEqual(got["commit"], heads["this"])

    def test_git_blob_matches_git(self):
        if shutil.which("git") is None:
            self.skipTest("no git")
        out = subprocess.run(["git", "hash-object", str(self.mod)], capture_output=True,
                             text=True, check=True).stdout.strip()
        self.assertEqual(gx.git_blob_sha1(self.mod.read_bytes()), out)


if __name__ == "__main__":
    unittest.main()
