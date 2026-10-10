"""XR package end to end, on a synthetic fixture, in throwaway git checkouts.

Each checkout holds the real 2D driver, the real OmniFold helper, ``n2/``, the OI-136 guard and
its shim, and this package; ``manifest/runs.json`` and ``references.json`` are rewritten to the
fixture inputs and to fixture reference products made by the real driver without the wrapper.
The admission chain is the real one: manifest, package commit, AUTHORIZATION record, draft.
The fixture is SB1's (``sb1-prep/tests/make_fixture_omnifile.py``, called, not copied); training
on it is small and local. Nothing here touches a cluster.

    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest test_xr -v
"""

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO = PKG.parents[5]
PKG_REL = PKG.relative_to(REPO).as_posix()
sys.path.insert(0, str(REPO / "docs/orchestration/state/next-preparation-20261009/sb1-prep/tests"))
import make_fixture_omnifile as mk  # noqa: E402

DRIVER = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
HELPER = "unbinned_unfolding/python/omnifold.py"
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
GUARD = "nd-unfolding/mnv_guarded_run.py"
COPIED = (DRIVER, HELPER, GUARD, f"{N2}/__init__.py", f"{N2}/execution.py")
RUNS = ("X0", "X0p", "X1", "L0", "L1")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null", "-c", "user.name=fixture",
                           "-c", "user.email=fixture@invalid", *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def py(argv, cwd=None, env=None):
    e = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1", **(env or {}))
    for k in [k for k in e if k.startswith("MNV_GUARD")]:
        e.pop(k)
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, env=e, cwd=cwd)


def driver_direct(root, out, omni, flux, extra):
    """The real driver, unwrapped, to make fixture reference products."""
    return py([root / DRIVER, "--omnifile", omni, "--mcfile", flux, "--iters", "5", "--use-weights", *extra,
               "--out", out], cwd=root / "2d-unfolding")


def ref_record(path):
    import ROOT
    import numpy as np
    f = ROOT.TFile.Open(str(path))
    h = f.Get("hXSec2D")
    x = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    par = {n: float(f.Get(n).GetVal()) for n in ("dataPOT", "mcPOT", "potScale", "nIterations",
                                                  "fluxIntegral_m2_per_POT", "fluxIntegral_cm2_per_POT", "nNucleons")}
    f.Close()
    return {"path": str(path), "sha256": sha(path), "bytes": Path(path).stat().st_size, "params": par,
            "fluxSource": None, "reported_globalid": [int(i * 16 + j) for i, j in np.argwhere(x > 0)]}


def local_environment():
    """The running interpreter's versions, frozen into the fixture runs.json like the cluster's."""
    import importlib
    import platform
    import ROOT
    pk = ("numpy", "sklearn", "lightgbm", "joblib", "threadpoolctl", "scipy")
    return {"python": platform.python_version(), "root": str(ROOT.gROOT.GetVersion()),
            "packages": {n: importlib.import_module(n).__version__ for n in pk}, "nested_setup": ["nested/one.sh"]}


def make_checkout(base, name, omni, flux, refs, mutate=None):
    """A throwaway checkout whose frozen outroot is ``base/out-<name>``."""
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    for rel in COPIED:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, root / rel)
    shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(PKG, root / PKG_REL, ignore=shutil.ignore_patterns("__pycache__", "tests", "expected-code.json"))
    runs_p = root / PKG_REL / "manifest/runs.json"
    runs = json.loads(runs_p.read_text())
    runs["inputs"]["omnifile"].update(path=str(omni), sha256=sha(omni), size=omni.stat().st_size)
    runs["inputs"]["mcfile"].update(path=str(flux), sha256=sha(flux), size=flux.stat().st_size)
    runs["outroot"] = str(base / f"out-{name}")
    runs["environment"] = local_environment()
    if mutate:
        mutate(root, runs, refs)
    runs_p.write_text(json.dumps(runs, indent=1, sort_keys=True) + "\n")
    (root / PKG_REL / "manifest/references.json").write_text(
        json.dumps({"schema": "xr-references/1", "references": refs}, indent=1, sort_keys=True) + "\n")
    (root / "setup_env.sh").write_text("# fixture environment setup\nsource nested/one.sh\n")
    (root / "nested").mkdir()
    (root / "nested/one.sh").write_text("# fixture nested setup\n")
    git(root, "init", "-q")
    # the nested setup is untracked, as the cluster's build and MINERvA101 setups are
    (root / ".git/info/exclude").write_text("nested/\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "package")
    r = py([root / PKG_REL / "xr_admit.py", "manifest"])
    assert r.returncode == 0, r.stderr
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "manifest")
    pkg_commit = git(root, "rev-parse", "HEAD")
    man_sha = sha(root / PKG_REL / "manifest/expected-code.json")
    auth = root / "docs/orchestration/AUTHORIZATION-20261010-xr.md"
    auth.write_text(f"# fixture authorization\n\npackage commit `{pkg_commit}`\nmanifest `{man_sha}`\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "authorization")
    return root, pkg_commit, man_sha


def draft_cmd(root, pkg_commit, man_sha):
    return py([root / PKG_REL / "xr_admit.py", "draft", "--authorization", "docs/orchestration/AUTHORIZATION-20261010-xr.md",
               "--package-commit", pkg_commit, "--manifest-sha", man_sha, "--setup", root / "setup_env.sh"])


def draft(root, pkg_commit, man_sha, base, tag):
    r = draft_cmd(root, pkg_commit, man_sha)
    assert r.returncode == 0, r.stderr + r.stdout
    adm = base / f"out-{tag}" / "admission.json"
    return adm, json.loads(adm.read_text())


def run_xr(root, adm, run, attempt=1, guard=True, cwd=None, strict=True):
    cmd = [root / PKG_REL / "xr_run.py", "--run", run, "--attempt", str(attempt), "--admission", adm]
    if strict:
        cmd.append("--require-provenance")
    if guard:
        cmd = [root / GUARD, "--expect-root", root, "--inventory", Path(adm).parent / f"inv-{run}-{attempt}.jsonl",
               "--label", run, "--", *cmd]
    return py(cmd, cwd=cwd or root / "2d-unfolding")


def receipt(adm_json, run, attempt=1):
    p = Path(adm_json["outroot"], run, f"a{attempt}", "receipt.json")
    return json.loads(p.read_text()) if p.exists() and p.stat().st_size else None


class XR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        (cls.tmp / "inputs").mkdir()
        cls.omni = cls.tmp / "inputs" / "omni.root"
        mk.write_fixture(str(cls.omni), rows=3000, extra=4)
        cls.flux = Path(mk.write_flux(str(cls.tmp / "inputs" / "flux.root")))
        # fixture reference products, made by the real driver without the wrapper
        stage = cls.tmp / "stage"
        (stage / "2d-unfolding").mkdir(parents=True)
        shutil.copy2(REPO / DRIVER, stage / DRIVER)
        (stage / HELPER).parent.mkdir(parents=True)
        shutil.copy2(REPO / HELPER, stage / HELPER)
        (cls.tmp / "refs").mkdir()
        cls.refs = {}
        for key, extra in (("E_C", []), ("CV42", ["--estimator", "lgbm", "--seed", "42"]),
                           ("SEED1", ["--estimator", "lgbm", "--seed", "1"]), ("EXACT_SEED1", ["--seed", "1"])):
            out = cls.tmp / "refs" / f"{key}.root"
            r = py([stage / DRIVER, "--omnifile", cls.omni, "--mcfile", cls.flux, "--iters", "5", "--use-weights",
                    *extra, "--out", out], cwd=stage / "2d-unfolding",
                   env={"PYTHONPATH": f"{stage / 'unbinned_unfolding/python'}:{os.environ.get('PYTHONPATH', '')}"})
            assert r.returncode == 0, r.stderr[-3000:]
            cls.refs[key] = ref_record(out)
        cls.refs["PN_CV"] = dict(cls.refs["CV42"])
        cls.root, cls.pkg, cls.man = make_checkout(cls.tmp, "A", cls.omni, cls.flux, cls.refs)
        cls.adm, cls.admj = draft(cls.root, cls.pkg, cls.man, cls.tmp, "A")
        cls.results = {}
        for run in RUNS:
            Path(cls.admj["outroot"], run, "a1").mkdir(parents=True)
            cls.results[run] = run_xr(cls.root, cls.adm, run)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    # ------------------------------------------------------------------ positive path
    def test_all_five_runs_complete_strict_with_their_intended_backend_and_seeds(self):
        runs = json.loads((self.root / PKG_REL / "manifest/runs.json").read_text())["runs"]
        for run in RUNS:
            r = self.results[run]
            self.assertEqual(r.returncode, 0, f"{run}: {r.stderr[-2000:]}")
            rec = receipt(self.admj, run)
            self.assertEqual(rec["status"], "complete")
            want = runs[run]["backend"]
            classes = {f["class"] for f in rec["fits"]}
            self.assertEqual(classes, {want["classifier"], want["regressor"]}, run)
            seeds = [f["random_state"] for f in rec["fits"] if f["class"] == want["classifier"]]
            self.assertEqual(seeds, [want["random_state"]["step1"], want["random_state"]["step2"]] * 5, run)
            self.assertEqual(rec["fit_counts"], {"classifier_fits": 10, "regressor_fits": 5}, run)
            self.assertTrue(rec["identity"]["strict"])
            self.assertEqual(rec["identity"]["git"]["mismatched"], [])
            self.assertEqual(rec["output"]["n_reported"], len(self.refs["E_C"]["reported_globalid"]))
            executed = {e["relpath"] for e in rec["identity"]["executed"]}
            self.assertIn(runs[run]["driver"], executed)
            self.assertIn(HELPER, executed)
            self.assertEqual(rec["driver_argv"][-2:], ["--out", str(Path(self.admj["outroot"], run, "a1", f"XR-{run}.root"))])

    def test_the_d1bc8813_record_driver_is_what_X0p_executed(self):
        rec = receipt(self.admj, "X0p")
        drv = [e for e in rec["identity"]["executed"] if e["relpath"].endswith("unfold_2d_omnifold_unbinned_d1bc8813.py.record")]
        self.assertEqual(len(drv), 1)
        self.assertEqual(drv[0]["sha256"], "447288e2c61d30cdd46c88077093ec0d78ac08ae63144bb2fe57525e7144ea34")
        self.assertEqual(drv[0]["git_blob"], "0f87330b3fe6e61d8922fafaefd0c17165f752b1")

    def test_comparator_on_the_fixture(self):
        """Deterministic arms reproduce their fixture references to 1e-8. The unseeded exact arms
        are NOT asserted: on this fixture's tied rows sklearn's exact backend with
        random_state=None differs run to run (measured 33 %), so only the comparator's report is
        checked for them."""
        out = self.tmp / "cmp.json"
        r = py([self.root / PKG_REL / "xr_compare.py", "--outroot", self.admj["outroot"], "--out", out])
        self.assertEqual(r.returncode, 0, r.stderr)
        c = json.loads(out.read_text())["comparisons"]
        self.assertIn(c["X0_vs_E_C"]["verdict"], ("PASS", "FAIL"))
        self.assertEqual(c["L0_vs_CV42"]["verdict"], "PASS", c["L0_vs_CV42"])
        self.assertEqual(c["L1_vs_SEED1"]["verdict"], "PASS", c["L1_vs_SEED1"])
        self.assertIn(c["X0p_vs_E_C"]["verdict"], ("PASS", "FAIL"))
        self.assertIn(c["X1_vs_X0"]["verdict"], ("PASS", "FAIL"))
        self.assertEqual(c["NC_X0_vs_CV42"]["verdict"], "FAIL")
        self.assertTrue(c["NC_X0_vs_CV42"]["control_met"])
        import importlib.util
        spec = importlib.util.spec_from_file_location("xr_compare", self.root / PKG_REL / "xr_compare.py")
        xc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xc)
        x1 = Path(self.admj["outroot"], "X1", "a1", "XR-X1.root")
        seeded = xc.compare(x1, self.refs["EXACT_SEED1"]["path"], self.refs["E_C"]["reported_globalid"])
        self.assertEqual(seeded["verdict"], "PASS", seeded)    # a seeded exact run is reproducible
        self.assertEqual(seeded["exactly_equal_cells"], seeded["n_cells"])

    def test_lightgbm_ran_with_a_child_free_core_count(self):
        for run in ("L0", "L1"):
            cc = receipt(self.admj, run)["cpu_count"]
            self.assertGreaterEqual(cc["physical_cores"], 1)
            # loky returns the user-limited (affinity) count when it is below the OS count, else the
            # physical count, which here comes from the child-free cache seed
            self.assertIn(cc["joblib_cpu_count_physical"], (cc["physical_cores"], cc["joblib_cpu_count_logical"]))

    # ------------------------------------------------------------------ refusals before inputs (exit 3)
    def fresh_attempt(self, run, attempt):
        d = Path(self.admj["outroot"], run, f"a{attempt}")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_strict_without_the_guard_is_refused(self):
        self.fresh_attempt("L1", 2)
        r = run_xr(self.root, self.adm, "L1", attempt=2, guard=False)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("mnv_guarded_run", r.stderr)

    def test_an_existing_output_is_never_overwritten(self):
        d = self.fresh_attempt("L1", 3)
        (d / "XR-L1.root").write_bytes(b"precious")
        r = run_xr(self.root, self.adm, "L1", attempt=3)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("already exists", r.stderr)
        self.assertEqual((d / "XR-L1.root").read_bytes(), b"precious")

    def test_a_symlinked_attempt_directory_is_refused(self):
        real = self.tmp / "elsewhere"
        real.mkdir(exist_ok=True)
        link = Path(self.admj["outroot"], "L0", "a2")
        link.symlink_to(real)
        r = run_xr(self.root, self.adm, "L0", attempt=2)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("symlink", r.stderr)
        self.assertEqual(list(real.iterdir()), [])

    def test_an_output_that_is_a_frozen_reference_path_is_refused(self):
        def mutate(root, runs, refs):
            refs["E_C"] = dict(refs["E_C"], path=str(self.tmp / "out-F" / "X0" / "a1" / "XR-X0.root"))
        root, pc, ms = make_checkout(self.tmp, "F", self.omni, self.flux, dict(self.refs), mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "F")
        Path(admj["outroot"], "X0", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "X0")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("frozen reference", r.stderr)

    def test_an_outroot_inside_the_checkout_is_refused(self):
        def mutate(root, runs, refs):
            runs["outroot"] = str(root / "inside")
        root, pc, ms = make_checkout(self.tmp, "IN", self.omni, self.flux, dict(self.refs), mutate)
        r = draft_cmd(root, pc, ms)
        self.assertEqual(r.returncode, 0, r.stderr)
        p = root / "inside" / "admission.json"
        Path(root, "inside", "L0", "a1").mkdir(parents=True)
        r = run_xr(root, p, "L0")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("inside", r.stderr)

    def test_the_wrong_working_directory_is_refused(self):
        self.fresh_attempt("L0", 3)
        r = run_xr(self.root, self.adm, "L0", attempt=3, cwd=self.root)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("working directory", r.stderr)

    def test_unknown_run_and_attempt_over_the_cap_are_refused(self):
        self.assertEqual(run_xr(self.root, self.adm, "X9").returncode, 3)
        self.fresh_attempt("X0", 5)
        r = run_xr(self.root, self.adm, "X0", attempt=5)
        self.assertEqual(r.returncode, 3, r.stderr)

    def test_an_admission_that_is_not_admitted_or_has_other_runs_is_refused(self):
        for key, val in (("status", "PROPOSAL"), ("runs_sha256", "0" * 64), ("outroot", str(self.tmp / "other-outroot"))):
            ad = json.loads(self.adm.read_text())
            ad[key] = val
            p = self.tmp / f"adm-{key}.json"
            p.write_text(json.dumps(ad))
            self.fresh_attempt("L0", 4)
            if key == "outroot":    # an attempt directory exists there, so only the frozen-outroot check refuses
                Path(val, "L0", "a4").mkdir(parents=True, exist_ok=True)
            r = run_xr(self.root, p, "L0", attempt=4)
            self.assertEqual(r.returncode, 3, f"{key}: {r.stderr}")
            if key == "outroot":
                self.assertIn("is not the frozen", r.stderr)
                self.assertEqual(list(Path(val, "L0", "a4").iterdir()), [])

    def test_a_changed_driver_or_helper_is_refused(self):
        for rel in (DRIVER, HELPER):
            def mutate(root, runs, refs, rel=rel):
                with open(root / rel, "a") as fh:
                    fh.write("\n# changed\n")
            tag = "D" if rel == DRIVER else "H"
            root, pc, ms = make_checkout(self.tmp, tag, self.omni, self.flux, dict(self.refs), mutate)
            adm, admj = draft(root, pc, ms, self.tmp, tag)
            Path(admj["outroot"], "L0", "a1").mkdir(parents=True)
            r = run_xr(root, adm, "L0")
            self.assertEqual(r.returncode, 3, f"{rel}: {r.stderr}")
            self.assertIn("sha256", r.stderr)

    def test_an_input_with_other_bytes_is_refused(self):
        bad = self.tmp / "inputs" / "omni-other.root"
        shutil.copy2(self.omni, bad)
        with open(bad, "ab") as fh:
            fh.write(b"\0")

        def mutate(root, runs, refs):
            runs["inputs"]["omnifile"]["path"] = str(bad)   # digest and size still the good file's
        root, pc, ms = make_checkout(self.tmp, "I", self.omni, self.flux, dict(self.refs), mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "I")
        Path(admj["outroot"], "L0", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "L0")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("input omnifile", r.stderr)
        # refused before the run starts: the reserved receipt is still empty and nothing was trained
        rec = Path(admj["outroot"], "L0", "a1", "receipt.json")
        self.assertTrue(rec.exists() and rec.stat().st_size == 0, "the run started before the input refusal")

    # ------------------------------------------------------------------ refusals during or after the run (exit 6)
    def test_a_backend_other_than_the_frozen_one_stops_before_training(self):
        def mutate(root, runs, refs):
            runs["runs"]["X0"]["argv"] = ["--omnifile", "{omnifile}", "--mcfile", "{mcfile}", "--iters", "5",
                                         "--use-weights", "--estimator", "lgbm", "--out", "{out}"]
        root, pc, ms = make_checkout(self.tmp, "B", self.omni, self.flux, dict(self.refs), mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "B")
        Path(admj["outroot"], "X0", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "X0")
        self.assertEqual(r.returncode, 6, r.stderr)
        rec = receipt(admj, "X0")
        self.assertEqual(rec["status"], "backend-refused")
        self.assertEqual(rec["fits"], [])

    def test_a_wrong_seed_stops_before_training(self):
        def mutate(root, runs, refs):
            runs["runs"]["L1"]["backend"]["random_state"]["step1"] = 7
        root, pc, ms = make_checkout(self.tmp, "S", self.omni, self.flux, dict(self.refs), mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "S")
        Path(admj["outroot"], "L1", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "L1")
        self.assertEqual(r.returncode, 6, r.stderr)
        self.assertIn("random_state=1", receipt(admj, "L1")["error"])

    def test_an_environment_other_than_the_frozen_one_stops_before_training(self):
        for tag, field in (("EV", "package"), ("EP", "python")):
            def mutate(root, runs, refs, field=field):
                if field == "package":
                    runs["environment"]["packages"]["numpy"] = "0.0.0"
                else:
                    runs["environment"]["python"] = "3.0.0"
            root, pc, ms = make_checkout(self.tmp, tag, self.omni, self.flux, dict(self.refs), mutate)
            adm, admj = draft(root, pc, ms, self.tmp, tag)
            Path(admj["outroot"], "L1", "a1").mkdir(parents=True)
            r = run_xr(root, adm, "L1")
            self.assertEqual(r.returncode, 6, r.stderr)
            rec = receipt(admj, "L1")
            self.assertEqual(rec["status"], "backend-refused")
            self.assertIn("environment differs", rec["error"])
            self.assertEqual(rec["fits"], [])

    def test_the_environment_and_module_origins_are_recorded(self):
        rec = receipt(self.admj, "L0")
        env = rec["environment_checked"]
        self.assertEqual(env["packages"], local_environment()["packages"])
        self.assertTrue(env["origins"]["lightgbm"].endswith("__init__.py"))
        self.assertIsInstance(env["threadpools"], list)

    def test_a_normalization_differing_from_the_reference_is_refused(self):
        refs = json.loads(json.dumps(self.refs))
        refs["E_C"]["params"]["nNucleons"] *= 1.000001
        root, pc, ms = make_checkout(self.tmp, "N", self.omni, self.flux, refs)
        adm, admj = draft(root, pc, ms, self.tmp, "N")
        Path(admj["outroot"], "L1", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "L1")
        self.assertEqual(r.returncode, 6, r.stderr)
        self.assertIn("normalization", receipt(admj, "L1")["error"])

    # ------------------------------------------------------------------ admission binding
    def check(self, root, auth, commit, man):
        return py([root / PKG_REL / "xr_admit.py", "check", "--authorization", auth, "--package-commit", commit,
                   "--manifest-sha", man])

    def test_the_authorization_binding(self):
        auth = "docs/orchestration/AUTHORIZATION-20261010-xr.md"
        self.assertEqual(self.check(self.root, auth, self.pkg, self.man).returncode, 0)
        cases = {"abbreviated commit": (auth, self.pkg[:12], self.man),
                 "other manifest digest": (auth, self.pkg, "0" * 64),
                 "absolute path": (str(self.root / auth), self.pkg, self.man),
                 "outside docs/orchestration": ("setup_env.sh", self.pkg, self.man),
                 "dot-dot": ("docs/orchestration/../../setup_env.sh", self.pkg, self.man)}
        for why, (a, c, m) in cases.items():
            r = self.check(self.root, a, c, m)
            self.assertEqual(r.returncode, 3, f"{why}: {r.stdout} {r.stderr}")

    def test_a_second_draft_for_the_same_grant_is_refused(self):
        r = draft_cmd(self.root, self.pkg, self.man)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("one admission per grant", r.stderr)
        self.assertEqual(json.loads(self.adm.read_text())["drafted_utc"], self.admj["drafted_utc"])

    def test_verify_refuses_a_changed_nested_setup_or_a_copied_admission(self):
        root, pc, ms = make_checkout(self.tmp, "V", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "V")
        verify = lambda a: py([root / PKG_REL / "xr_admit.py", "verify", "--admission", a])
        self.assertEqual(verify(adm).returncode, 0, verify(adm).stderr)
        copy = self.tmp / "adm-V-copy.json"
        shutil.copy2(adm, copy)
        self.assertEqual(verify(copy).returncode, 3)
        self.assertEqual(git(root, "status", "--porcelain"), "")
        with open(root / "nested/one.sh", "a") as fh:       # an untracked file: only its digest sees it
            fh.write("export X=1\n")
        self.assertEqual(git(root, "status", "--porcelain"), "")
        r = verify(adm)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("changed since admission", r.stderr)

    def next_attempt(self, adm, run, sacct_text, now=None):
        psv = self.tmp / "na-sacct.psv"
        psv.write_text(sacct_text)
        cmd = [self.tmp / "T" / PKG_REL / "xr_admit.py", "next-attempt", "--admission", adm, "--run", run,
               "--sacct", psv]
        return py(cmd + (["--now", now] if now else []))

    def test_next_attempt_counts_sacct_jobs_and_enforces_the_stop(self):
        root, pc, ms = make_checkout(self.tmp, "T", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "T")
        r = self.next_attempt(adm, "X0", "")
        self.assertEqual(r.returncode, 0, r.stderr)
        att, deadline = r.stdout.split()
        self.assertEqual(att, "1")
        # four exact xr_ jobs in sacct (steps and other jobs ignored) exhaust the exact cap with no directory
        rows = "".join(f"{100 + i}|xr_X{i % 2}_a{i}|FAILED\n{100 + i}.batch|batch|FAILED\n" for i in range(4))
        r = self.next_attempt(adm, "X1", rows + "200|sb1_UL|PENDING\n")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("attempts already used", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L0", rows).returncode, 0)
        # the stop: 72 h after the first submission
        Path(admj["outroot"], "submissions.jsonl").write_text(json.dumps(
            {"run": "X0", "kind": "exact", "attempt": 1, "job_id": 1, "submitted_utc": "2026-10-10T00:00:00Z"}) + "\n")
        r = self.next_attempt(adm, "X1", "", now="2026-10-11T18:00:00Z")      # 42 h + 30 h = 72 h: allowed
        self.assertEqual(r.returncode, 0, r.stderr)
        import datetime
        want = datetime.datetime.fromtimestamp(datetime.datetime(2026, 10, 13, tzinfo=datetime.timezone.utc).timestamp())
        self.assertEqual(r.stdout.split()[1], want.strftime("%Y-%m-%dT%H:%M:%S"))
        r = self.next_attempt(adm, "X1", "", now="2026-10-11T18:00:01Z")      # could end past the stop
        self.assertEqual(r.returncode, 3)
        self.assertIn("past the stop", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L1", "", now="2026-10-12T22:59:00Z").returncode, 0)
        r = self.next_attempt(adm, "L1", "", now="2026-10-13T00:00:01Z")
        self.assertEqual(r.returncode, 3)

    def test_admission_tool_is_python36_syntax_and_api(self):
        """The launch scripts run xr_admit.py under the cluster's /usr/bin/python3 (3.6.15)."""
        import ast
        src = (PKG / "xr_admit.py").read_text()
        tree = ast.parse(src, feature_version=(3, 6))
        kws = {k.arg for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords}
        self.assertFalse(kws & {"capture_output", "text"}, "subprocess.run arguments added in 3.7")
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertFalse(attrs & {"fromisoformat", "isascii", "breakpointhook"}, "3.7+ API")

    def test_a_package_change_after_the_package_commit_is_refused(self):
        root, pc, ms = make_checkout(self.tmp, "P", self.omni, self.flux, dict(self.refs))
        with open(root / PKG_REL / "xr_compare.py", "a") as fh:
            fh.write("\n# later\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "later change")
        r = self.check(root, "docs/orchestration/AUTHORIZATION-20261010-xr.md", pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("changed after", r.stderr)

    def test_an_uncommitted_or_symlinked_authorization_is_refused(self):
        root, pc, ms = make_checkout(self.tmp, "U", self.omni, self.flux, dict(self.refs))
        a = root / "docs/orchestration/AUTHORIZATION-20261011-xr.md"
        a.write_text(f"{pc} {ms}\n")
        r = self.check(root, "docs/orchestration/AUTHORIZATION-20261011-xr.md", pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)
        link = root / "docs/orchestration/AUTHORIZATION-20261012-xr.md"
        link.symlink_to(root / "docs/orchestration/AUTHORIZATION-20261010-xr.md")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "symlink")
        r = self.check(root, "docs/orchestration/AUTHORIZATION-20261012-xr.md", pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)

    # ------------------------------------------------------------------ fake Slurm: submit, job caps, ledger
    def fake_slurm(self, d, sbatch_fail_at=0, tres="cpu=12,mem=22860M,node=1,billing=12", qos="shared",
                   limit="1-06:00:00", ncpu="12"):
        d.mkdir(parents=True, exist_ok=True)
        log = d / "calls.log"
        (d / "sbatch").write_text(f"""#!/bin/bash
echo "sbatch $*" >> {log}
n=$(grep -c '^sbatch' {log})
[ "$n" = "{sbatch_fail_at}" ] && exit 1
echo $((1000 + n))
""")
        (d / "scancel").write_text(f"#!/bin/bash\necho \"scancel $*\" >> {log}\n")
        (d / "squeue").write_text("#!/bin/bash\nexit 0\n")
        (d / "sacct").write_text(f"#!/bin/bash\necho \"sacct $*\" >> {log}\n")
        (d / "scontrol").write_text(f"#!/bin/bash\necho 'JobId=1 QOS={qos} NumCPUs={ncpu} TimeLimit={limit} TRES={tres}'\n")
        for f in ("sbatch", "scancel", "squeue", "scontrol", "sacct"):
            (d / f).chmod(0o755)
        return log

    def submit(self, adm, runs, slurm):
        env = dict(os.environ, PATH=f"{slurm}:{os.environ['PATH']}")
        return subprocess.run(["bash", self.root / PKG_REL / "launch/xr_submit.sh", adm, *runs], capture_output=True,
                               text=True, env=env)

    def test_submit_counts_attempts_per_kind_and_cancels_on_a_failed_sbatch(self):
        root, pc, ms = make_checkout(self.tmp, "Q", self.omni, self.flux, dict(self.refs))
        self.__class__.root_q = root
        adm, admj = draft(root, pc, ms, self.tmp, "Q")
        slurm = self.tmp / "slurm-ok"
        log = self.fake_slurm(slurm)
        env = dict(os.environ, PATH=f"{slurm}:{os.environ['PATH']}")
        sub = lambda *runs: subprocess.run(["bash", root / PKG_REL / "launch/xr_submit.sh", adm, *runs],
                                           capture_output=True, text=True, env=env)
        r = sub("X0", "X0p", "X1", "L0", "L1")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X0")                      # the one extra exact attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X1")                      # a fifth exact attempt: refused
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("attempts already used", r.stderr)
        r = sub("L0")                      # the one extra LightGBM attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("L1")
        self.assertNotEqual(r.returncode, 0)
        lines = [json.loads(l) for l in Path(admj["outroot"], "submissions.jsonl").read_text().splitlines()]
        self.assertEqual(len(lines), 7)
        self.assertEqual(sum(1 for l in lines if l["kind"] == "exact"), 4)
        calls = log.read_text()
        self.assertIn("--qos=shared", calls)
        self.assertIn("--cpus-per-task=12", calls)
        self.assertIn("--mem=22860M", calls)
        self.assertIn("--time=30:00:00", calls)
        self.assertIn("--cpus-per-task=64", calls)
        self.assertIn("--time=01:00:00", calls)
        self.assertNotIn("regular", calls)
        self.assertIn("--deadline=", calls)
        self.assertIn("sacct -u", calls)
        self.assertIn("-S 2026-10-10", calls)
        # a failure at the second sbatch cancels the first
        root2, pc2, ms2 = make_checkout(self.tmp, "Q2", self.omni, self.flux, dict(self.refs))
        adm2, admj2 = draft(root2, pc2, ms2, self.tmp, "Q2")
        slurm2 = self.tmp / "slurm-fail"
        log2 = self.fake_slurm(slurm2, sbatch_fail_at=2)
        env2 = dict(os.environ, PATH=f"{slurm2}:{os.environ['PATH']}")
        r = subprocess.run(["bash", root2 / PKG_REL / "launch/xr_submit.sh", adm2, "X0", "X0p"], capture_output=True,
                           text=True, env=env2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("scancel 1001", log2.read_text())

    def test_jobcheck_refuses_an_allocation_outside_the_caps(self):
        cases = {"ok": ({}, 0), "billing 14": ({"tres": "cpu=14,mem=26670M,node=1,billing=14", "ncpu": "14"}, 3),
                 "billing 13 at 12 cpus": ({"tres": "cpu=12,mem=24765M,node=1,billing=13"}, 3),
                 "regular qos": ({"qos": "regular_1"}, 3), "time 31 h": ({"limit": "1-07:00:00"}, 3),
                 "cpus 16": ({"ncpu": "16"}, 3)}
        for why, (kw, code) in cases.items():
            d = self.tmp / f"slurm-jc-{why.replace(' ', '_')}"
            self.fake_slurm(d, **kw)
            env = dict(os.environ, PATH=f"{d}:{os.environ['PATH']}", SLURM_JOB_ID="1")
            r = subprocess.run([sys.executable, self.root / PKG_REL / "xr_admit.py", "jobcheck", "--admission", self.adm,
                                "--run", "X0"], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, code, f"{why}: {r.stdout} {r.stderr}")
            if code == 0:
                self.assertEqual(r.stdout.strip(), "12")

    def test_ledger_charges_and_flags(self):
        out = self.tmp / "ledger-out"
        out.mkdir()
        adm = json.loads(self.adm.read_text())
        adm["outroot"] = str(out)
        p = self.tmp / "adm-ledger.json"
        p.write_text(json.dumps(adm))
        subs = [{"run": "X0", "kind": "exact", "attempt": 1, "job_id": 11, "submitted_utc": "2026-10-10T00:00:00Z"},
                {"run": "L0", "kind": "lgbm", "attempt": 1, "job_id": 12, "submitted_utc": "2026-10-10T00:00:05Z"},
                {"run": "X1", "kind": "exact", "attempt": 1, "job_id": 13, "submitted_utc": "2026-10-10T00:00:09Z"}]
        (out / "submissions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in subs))
        psv = self.tmp / "sacct.psv"
        psv.write_text("JobID|JobName|State|ElapsedRaw|AllocTRES|Timelimit\n"
                       "11|xr_X0_a1|COMPLETED|72000|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n"
                       "12|xr_L0_a1|COMPLETED|900|billing=64,cpu=64,mem=121920M,node=1|01:00:00\n"
                       "13|xr_X1_a1|RUNNING|3600|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n")
        ledger = lambda now: py([self.root / PKG_REL / "xr_admit.py", "ledger", "--admission", p, "--sacct", psv,
                                 "--now", now])
        r = ledger("2026-10-11T00:00:00Z")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        led = json.loads(r.stdout)
        self.assertAlmostEqual(led["hours_since_first_submission"], 24.0, places=9)
        self.assertAlmostEqual(led["charged_node_h"], 12 / 256 * 20 + 64 / 256 * 0.25 + 12 / 256 * 1, places=9)
        self.assertAlmostEqual(led["unfinished_ceiling_node_h"], 1.40625, places=9)
        r = ledger("2026-10-13T00:00:01Z")       # past the stop with job 13 still running
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("cancel them", r.stdout)
        psv.write_text(psv.read_text().replace("billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n12",
                                               "billing=24,cpu=24,mem=45720M,node=1|1-06:00:00\n12"))
        r = ledger("2026-10-11T00:00:00Z")
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("billing 24 > 12", r.stdout)


class Comparator(unittest.TestCase):
    """xr_compare on hand-made products: a 1e-8 shift fails, cell sets must match, digests are enforced."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def product(self, path, scale_cell=None, factor=1.0, zero_cell=None, ymax=16):
        import ROOT
        import numpy as np
        f = ROOT.TFile.Open(str(path), "RECREATE")
        h = ROOT.TH2D("hXSec2D", "", 14, 0, 14, 16, 0, ymax)
        rng = np.random.default_rng(3)
        for i in range(14):
            for j in range(16):
                g = i * 16 + j
                if (i + j) % 7 == 0 or g == zero_cell:
                    continue
                v = float(rng.uniform(1, 2))
                h.SetBinContent(i + 1, j + 1, v * (factor if g == scale_cell else 1.0))
        h.Write()
        f.Close()
        return path

    def test_tolerance_cells_and_digests(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("xr_compare", PKG / "xr_compare.py")
        xc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xc)
        a = self.product(self.tmp / "a.root")
        import ROOT
        import numpy as np
        f = ROOT.TFile.Open(str(a))
        h = f.Get("hXSec2D")
        cells = [i * 16 + j for i in range(14) for j in range(16) if h.GetBinContent(i + 1, j + 1) > 0]
        f.Close()
        self.assertEqual(xc.compare(a, self.product(self.tmp / "b.root"), cells)["verdict"], "PASS")
        c = xc.compare(self.product(self.tmp / "c.root", scale_cell=cells[5], factor=1 + 2e-8), a, cells)
        self.assertEqual(c["verdict"], "FAIL")
        self.assertEqual([o["globalid"] for o in c["cells_over_tol"]], [cells[5]])
        c = xc.compare(self.product(self.tmp / "d.root", scale_cell=cells[5], factor=1 + 5e-9), a, cells)
        self.assertEqual(c["verdict"], "PASS")
        c = xc.compare(self.product(self.tmp / "e.root", zero_cell=cells[0]), a, cells)
        self.assertEqual(c["verdict"], "INCONCLUSIVE")
        c = xc.compare(self.product(self.tmp / "f.root", ymax=32), a, cells)    # same contents, other edges
        self.assertEqual(c["verdict"], "INCONCLUSIVE")
        self.assertIn("axes", c["why"])

    def test_receipts_must_name_their_run_and_admission(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("xr_compare", PKG / "xr_compare.py")
        xc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xc)
        root = self.tmp / "outroot"
        (root / "X0" / "a1").mkdir(parents=True)
        adm = root / "admission.json"
        adm.write_text('{"status": "ADMITTED"}\n')
        prod = self.product(root / "X0" / "a1" / "XR-X0.root")

        def receipt(**upd):
            r = {"run": "X0", "attempt": 1, "status": "complete",
                 "admission": {"path": str(adm.resolve()), "sha256": xc.sha(adm)},
                 "output": {"path": str(prod), "sha256": xc.sha(prod)}}
            r.update(upd)
            (root / "X0" / "a1" / "receipt.json").write_text(json.dumps(r))
        receipt()
        self.assertIsNone(xc.newest_complete(root, "X0")[1])
        for why, upd in (("run", {"run": "X1"}),
                         ("admission digest", {"admission": {"path": str(adm.resolve()), "sha256": "0" * 64}}),
                         ("admission path", {"admission": {"path": str(self.tmp / "admission.json"), "sha256": xc.sha(adm)}}),
                         ("output digest", {"output": {"path": str(prod), "sha256": "0" * 64}})):
            receipt(**upd)
            new, err = xc.newest_complete(root, "X0")
            self.assertIsNone(new, why)
            self.assertTrue(err, why)


class FitCounts(unittest.TestCase):
    def test_the_regressor_must_fit_every_iteration(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("xr_run_unit", PKG / "xr_run.py")
        xr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xr)
        backend = {"estimator": "exact", "random_state": {"step1": None, "step2": None, "regressor": None},
                   "iterations": 5}
        for n_reg, ok in ((5, True), (0, False), (4, False), (6, False)):
            rec = xr.FitRecorder(backend)
            rec.fits = [{"class": "GradientBoostingClassifier"}] * 10 + [{"class": "GradientBoostingRegressor"}] * n_reg
            if ok:
                self.assertEqual(rec.verify_counts(), {"classifier_fits": 10, "regressor_fits": 5})
            else:
                with self.assertRaises(xr.BackendRefusal):
                    rec.verify_counts()


if __name__ == "__main__":
    unittest.main()
