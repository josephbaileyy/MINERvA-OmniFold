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
SCHED = HERE / "scheduler"          # real Perlmutter scheduler output, captured read-only (README.txt)
PENDING_JOB = "59645304"
RUNNING_ALLOC = "cpu=64,mem=121920M,node=1,billing=64"    # scontrol's AllocTRES for the finished 59648617


def captured(name):
    return (SCHED / name).read_text()


def scontrol_line(**fields):
    """The captured pending ``scontrol -o`` line with named fields replaced. Each field must occur
    exactly once as a token, so a test cannot invent a field the real format lacks."""
    import re
    line = captured(f"scontrol-pending-{PENDING_JOB}.txt")
    for key, val in fields.items():
        pat = re.compile(r"(^|\s){}=\S*".format(re.escape(key)))
        assert len(pat.findall(line)) == 1, f"{key} is not a single field of the captured line"
        line = pat.sub(lambda m: f"{m.group(1)}{key}={val}", line)
    return line


def running_line(**fields):
    """A RUNNING form of the captured line: JobState and AllocTRES set as a granted allocation prints them."""
    return scontrol_line(**dict({"JobState": "RUNNING", "AllocTRES": RUNNING_ALLOC}, **fields))


def preflight_line():
    """The running line for the preflight kind: 12 CPUs, 5 minutes, billing 12."""
    return running_line(NumCPUs="12", TimeLimit="00:05:00", AllocTRES="cpu=12,mem=22860M,node=1,billing=12")


def load_admit():
    import importlib.util
    spec = importlib.util.spec_from_file_location("xr_admit_unit", PKG / "xr_admit.py")
    xa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xa)
    return xa


def write_preflight_pass(admj, attempt=1, **upd):
    """A passing preflight receipt for this admission, as xr_run.py writes one (for the release gate)."""
    adm = Path(admj["outroot"], "admission.json")
    d = Path(admj["outroot"], "PF", f"a{attempt}")
    d.mkdir(parents=True, exist_ok=True)
    r = {"schema": "xr-preflight-receipt/1", "run": "PF", "attempt": attempt, "kind": "preflight",
         "status": "preflight-pass", "fits": [],
         "admission": {"path": str(adm.resolve()), "sha256": sha(adm)}}
    r.update(upd)
    (d / "preflight-receipt.json").write_text(json.dumps(r))
    return d


def write_complete(admj, run, attempt=1, name="receipt.json", **upd):
    """A complete, comparable run receipt for this admission, with its output file."""
    adm = Path(admj["outroot"], "admission.json")
    d = Path(admj["outroot"], run, f"a{attempt}")
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"XR-{run}.root"
    out.write_bytes(b"fixture output " + run.encode())
    r = {"schema": "xr-receipt/2", "run": run, "attempt": attempt, "kind": "lgbm", "status": "complete",
         "identity": {"strict": True}, "admission": {"path": str(adm.resolve()), "sha256": sha(adm)},
         "output": {"path": str(out), "sha256": sha(out)}}
    r.update(upd)
    (d / name).write_text(json.dumps(r))
    return d


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
        # the comparisons and control are the admitted ones; the preflight is in none of them
        self.assertEqual(sorted(c), ["L0_vs_CV42", "L0_vs_PN_CV", "L1_vs_SEED1", "NC_X0_vs_CV42", "X0_vs_E_C",
                                     "X0p_vs_E_C", "X1_vs_X0"])
        self.assertFalse([k for k, v in c.items() if (v.get("new") or {}).get("path", "").find("/PF/") >= 0])
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



class Launch(unittest.TestCase):
    """Admission, scheduler, release order, ledger and the preflight: a fixture checkout and its
    admission, with no reference products and no training (the references are placeholders), so
    the mutants of this code run in seconds."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        (cls.tmp / "inputs").mkdir()
        cls.omni = cls.tmp / "inputs" / "omni.root"
        mk.write_fixture(str(cls.omni), rows=3000, extra=4)
        cls.flux = Path(mk.write_flux(str(cls.tmp / "inputs" / "flux.root")))
        cls.refs = {k: {"path": str(cls.tmp / "refs" / f"{k}.root"), "sha256": "0" * 64, "params": {},
                        "reported_globalid": []} for k in ("E_C", "CV42", "SEED1", "PN_CV")}
        cls.root, cls.pkg, cls.man = make_checkout(cls.tmp, "A", cls.omni, cls.flux, cls.refs)
        cls.adm, cls.admj = draft(cls.root, cls.pkg, cls.man, cls.tmp, "A")
        # the preflight through the real xr_job.sbatch: jobcheck on a real-format allocation line,
        # verify, the setup sourced, the guard, xr_run.py --run PF
        Path(cls.admj["outroot"], "PF", "a1").mkdir(parents=True)
        cls.pf_slurm = cls.tmp / "slurm-pf"
        cls.pf_slurm.mkdir()
        (cls.pf_slurm / "scontrol").write_text(f"#!/bin/bash\ncat {cls.pf_slurm / 'line.txt'}\n")
        (cls.pf_slurm / "line.txt").write_text(preflight_line())
        (cls.pf_slurm / "python").write_text(f"#!/bin/bash\nexec {sys.executable} \"$@\"\n")
        for f in ("scontrol", "python"):
            (cls.pf_slurm / f).chmod(0o755)
        env = {k: v for k, v in os.environ.items() if not k.startswith("MNV_GUARD")}
        env.update(PATH=f"{cls.pf_slurm}:{os.environ['PATH']}", SLURM_JOB_ID=PENDING_JOB, PYTHONDONTWRITEBYTECODE="1")
        cls.pf = subprocess.run(["bash", cls.root / PKG_REL / "launch/xr_job.sbatch", cls.adm, "PF", "1"],
                                capture_output=True, text=True, env=env, cwd=cls.root)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_draft_refuses_the_prior_grants_outroot(self):
        def mutate(root, runs, refs):
            runs["prior"]["outroot"] = runs["outroot"]
        root, pc, ms = make_checkout(self.tmp, "PO", self.omni, self.flux, dict(self.refs), mutate)
        r = draft_cmd(root, pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("is the prior grant's", r.stderr)
        self.assertFalse(Path(self.tmp, "out-PO").exists())

    def next_attempt(self, adm, run, sacct_text, now=None):
        psv = self.tmp / "na-sacct.psv"
        psv.write_text(sacct_text)
        cmd = [self.tmp / "T" / PKG_REL / "xr_admit.py", "next-attempt", "--admission", adm, "--run", run,
               "--sacct", psv]
        return py(cmd + (["--now", now] if now else []))

    def test_next_attempt_counts_only_this_amendment_and_enforces_order_and_the_stop(self):
        root, pc, ms = make_checkout(self.tmp, "T", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "T")
        real = captured("sacct-X-n-P.psv")             # the prior grant's five xr_* jobs, SB1's jobs
        # release order: nothing before the preflight
        r = self.next_attempt(adm, "L0", real)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("no passed preflight", r.stderr)
        r = self.next_attempt(adm, "PF", real)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split()[0], "1")
        # sacct must show exactly the prior grant's jobs
        no_prior = "".join(l + "\n" for l in real.splitlines() if "|xr_X0_a1|" not in l)
        r = self.next_attempt(adm, "PF", no_prior)
        self.assertEqual(r.returncode, 3)
        self.assertIn("missing ['59648608']", r.stderr)
        r = self.next_attempt(adm, "PF", real + "60000001|xr_X0_a2|PENDING\n")
        self.assertEqual(r.returncode, 3)
        self.assertIn("unexpected ['60000001']", r.stderr)
        write_preflight_pass(admj)
        r = self.next_attempt(adm, "PF", real)
        self.assertEqual(r.returncode, 3)
        self.assertIn("already passed", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L0", real).returncode, 0)
        r = self.next_attempt(adm, "X0", real)          # L0 first
        self.assertEqual(r.returncode, 3)
        self.assertIn("L0 has no complete, comparable receipt", r.stderr)
        # a preflight receipt never stands in for L0's result, even marked complete and with an output
        d = write_complete(admj, "L0", schema="xr-preflight-receipt/1", kind="preflight")
        r = self.next_attempt(adm, "X0", real)
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn("L0 has no complete, comparable receipt", r.stderr)
        shutil.rmtree(d)
        write_complete(admj, "L0")
        self.assertEqual(self.next_attempt(adm, "X0", real).returncode, 0)
        r = self.next_attempt(adm, "L0", real)
        self.assertEqual(r.returncode, 3)
        self.assertIn("no rerun", r.stderr)
        # caps count this amendment's xrr_* jobs only (steps and other jobs ignored)
        rows = "".join(f"{100 + i}|xrr_X{i % 2}_a{i}|FAILED\n{100 + i}.batch|batch|FAILED\n" for i in range(4))
        r = self.next_attempt(adm, "X1", real + rows)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("attempts already used", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L1", real + rows).returncode, 0)
        xa = load_admit()
        psv = self.tmp / "na-units.psv"
        psv.write_text(real + "".join(f"{200 + i}|xrr_X0_a{i}|FAILED\n" for i in range(2)))
        _, parts = xa.attempts_by_kind(admj, xa.load_runs(), psv)
        self.assertEqual(parts["sacct"], {"exact": 2, "lgbm": 0, "preflight": 0})
        # the stop: 72 h after the first submission, which is the preflight's
        Path(admj["outroot"], "submissions.jsonl").write_text(json.dumps(
            {"run": "PF", "kind": "preflight", "attempt": 1, "job_id": 1, "submitted_utc": "2026-10-11T00:00:00Z"}) + "\n")
        r = self.next_attempt(adm, "X1", real, now="2026-10-12T18:00:00Z")      # 42 h + 30 h = 72 h: allowed
        self.assertEqual(r.returncode, 0, r.stderr)
        import datetime
        want = datetime.datetime.fromtimestamp(datetime.datetime(2026, 10, 14, tzinfo=datetime.timezone.utc).timestamp())
        self.assertEqual(r.stdout.split()[1], want.strftime("%Y-%m-%dT%H:%M:%S"))
        r = self.next_attempt(adm, "X1", real, now="2026-10-12T18:00:01Z")      # could end past the stop
        self.assertEqual(r.returncode, 3)
        self.assertIn("past the stop", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L1", real, now="2026-10-13T22:59:00Z").returncode, 0)
        self.assertEqual(self.next_attempt(adm, "L1", real, now="2026-10-14T00:00:01Z").returncode, 3)

    def test_the_planned_cumulative_ceiling_includes_the_prior_charge(self):
        xa = load_admit()
        runs = xa.load_runs()
        root = self.tmp / "ceiling"
        root.mkdir()
        admj = {"outroot": str(root)}
        kinds = runs["kinds"]
        full = sum(k["ceiling_node_h_per_attempt"] * k["max_attempts_total"] for k in kinds.values())
        self.assertAlmostEqual(xa.planned_ceiling(admj, runs, 0.0) + full, runs["ceiling_node_h_total"], places=12)
        self.assertLessEqual(runs["ceiling_node_h_total"], runs["cap_node_h"])
        self.assertAlmostEqual(runs["prior"]["charged_node_h_recorded"], 0.0013498263888888891, places=15)
        # with a prior charge that leaves less than one exact attempt, next-attempt refuses
        heavy = json.loads(json.dumps(runs))
        heavy["prior"]["charged_node_h_recorded"] = 5.0
        Path(root, "submissions.jsonl").write_text(json.dumps(
            {"run": "PF", "kind": "preflight", "attempt": 1, "job_id": 1, "submitted_utc": "2026-10-11T00:00:00Z"}) + "\n")
        Path(root, "admission.json").write_text(json.dumps({"stop_after_hours": 72, "outroot": str(root)}))
        write_preflight_pass({"outroot": str(root)})
        write_complete({"outroot": str(root)}, "L0")
        psv = self.tmp / "ceiling.psv"
        psv.write_text(captured("sacct-X-n-P.psv"))
        xa.load_runs = lambda: heavy
        args = type("A", (), {"admission": str(root / "admission.json"), "run": "X0", "sacct": str(psv),
                              "now": "2026-10-11T00:01:00Z"})
        with self.assertRaisesRegex(xa.Refusal, "planned cumulative ceiling"):
            xa.next_attempt(args)
        heavy["prior"]["charged_node_h_recorded"] = runs["prior"]["charged_node_h_recorded"]
        self.assertEqual(xa.next_attempt(args), 0)

    # ------------------------------------------------------------------ fake Slurm: submit, job caps, ledger
    def fake_slurm(self, d, sbatch_fail_at=0, line=None):
        """sbatch/scancel/squeue stubs; scontrol prints ``line`` (a real-format line) and sacct the
        captured real ``sacct -X -n -P`` output, which lists the prior grant's five jobs."""
        d.mkdir(parents=True, exist_ok=True)
        log = d / "calls.log"
        (d / "scontrol.txt").write_text(line if line is not None else running_line(
            NumCPUs="12", TimeLimit="1-06:00:00", AllocTRES="cpu=12,mem=22860M,node=1,billing=12"))
        (d / "sbatch").write_text(f"""#!/bin/bash
echo "sbatch $*" >> {log}
n=$(grep -c '^sbatch' {log})
[ "$n" = "{sbatch_fail_at}" ] && exit 1
echo $((1000 + n))
""")
        (d / "scancel").write_text(f"#!/bin/bash\necho \"scancel $*\" >> {log}\n")
        (d / "squeue").write_text("#!/bin/bash\nexit 0\n")
        (d / "sacct").write_text(f"#!/bin/bash\necho \"sacct $*\" >> '{log}'\ncat '{SCHED / 'sacct-X-n-P.psv'}'\n")
        (d / "scontrol").write_text(f"#!/bin/bash\ncat '{d / 'scontrol.txt'}'\n")
        for f in ("sbatch", "scancel", "squeue", "scontrol", "sacct"):
            (d / f).chmod(0o755)
        return log

    def submit(self, adm, runs, slurm):
        env = dict(os.environ, PATH=f"{slurm}:{os.environ['PATH']}")
        return subprocess.run(["bash", self.root / PKG_REL / "launch/xr_submit.sh", adm, *runs], capture_output=True,
                               text=True, env=env)

    def test_submit_releases_in_order_counts_attempts_and_cancels_on_a_failed_sbatch(self):
        root, pc, ms = make_checkout(self.tmp, "Q", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "Q")
        slurm = self.tmp / "slurm-ok"
        log = self.fake_slurm(slurm)
        env = dict(os.environ, PATH=f"{slurm}:{os.environ['PATH']}")
        sub = lambda *runs: subprocess.run(["bash", root / PKG_REL / "launch/xr_submit.sh", adm, *runs],
                                           capture_output=True, text=True, env=env)
        r = sub("X0", "L0")                # nothing before the preflight
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no passed preflight", r.stderr)
        self.assertEqual(sub("PF").returncode, 0)
        r = sub("PF")                      # the one preflight attempt
        self.assertNotEqual(r.returncode, 0)
        write_preflight_pass(admj)
        r = sub("L0", "X0")                # L0 goes; X0 waits for L0's receipt
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("L0 has no complete", r.stderr)
        write_complete(admj, "L0")
        r = sub("X0", "X0p", "X1", "L1")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X0")                      # the one extra exact attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X1")                      # a fifth exact attempt: refused
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("attempts already used", r.stderr)
        r = sub("L1")                      # the one extra LightGBM attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("L1")
        self.assertNotEqual(r.returncode, 0)
        lines = [json.loads(l) for l in Path(admj["outroot"], "submissions.jsonl").read_text().splitlines()]
        self.assertEqual([l["run"] for l in lines], ["PF", "L0", "X0", "X0p", "X1", "L1", "X0", "L1"])
        self.assertEqual(sum(1 for l in lines if l["kind"] == "exact"), 4)
        calls = log.read_text()
        self.assertIn("--job-name=xrr_PF_a1", calls)
        self.assertIn("--time=00:05:00", calls)
        self.assertIn("--qos=shared", calls)
        self.assertIn("--cpus-per-task=12", calls)
        self.assertIn("--mem=22860M", calls)
        self.assertIn("--time=30:00:00", calls)
        self.assertIn("--cpus-per-task=64", calls)
        self.assertIn("--time=01:00:00", calls)
        self.assertNotIn("regular", calls)
        self.assertNotIn("--job-name=xr_", calls)
        self.assertIn("--deadline=", calls)
        self.assertIn("sacct -u", calls)
        self.assertIn("-S 2026-10-10", calls)
        # a failure at the second sbatch cancels the first
        root2, pc2, ms2 = make_checkout(self.tmp, "Q2", self.omni, self.flux, dict(self.refs))
        adm2, admj2 = draft(root2, pc2, ms2, self.tmp, "Q2")
        write_preflight_pass(admj2)
        write_complete(admj2, "L0")
        slurm2 = self.tmp / "slurm-fail"
        log2 = self.fake_slurm(slurm2, sbatch_fail_at=2)
        env2 = dict(os.environ, PATH=f"{slurm2}:{os.environ['PATH']}")
        r = subprocess.run(["bash", root2 / PKG_REL / "launch/xr_submit.sh", adm2, "X0", "X0p"], capture_output=True,
                           text=True, env=env2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("scancel 1001", log2.read_text())

    def test_jobcheck_on_real_format_allocations(self):
        ok12 = dict(NumCPUs="12", TimeLimit="1-06:00:00", AllocTRES="cpu=12,mem=22860M,node=1,billing=12")
        cases = {"ok": (running_line(**ok12), 0),
                 "billing 14": (running_line(**dict(ok12, NumCPUs="14", AllocTRES="cpu=14,mem=26670M,node=1,billing=14")), 3),
                 "billing 13 at 12 cpus": (running_line(**dict(ok12, AllocTRES="cpu=12,mem=24765M,node=1,billing=13")), 3),
                 "regular qos": (running_line(**dict(ok12, QOS="regular_1")), 3),
                 "time 31 h": (running_line(**dict(ok12, TimeLimit="1-07:00:00")), 3),
                 "cpus 16": (running_line(**dict(ok12, NumCPUs="16")), 3),
                 "pending (null)": (scontrol_line(**{k: v for k, v in ok12.items() if k != "AllocTRES"}), 3)}
        for why, (line, code) in cases.items():
            d = self.tmp / ("slurm-jc-" + "".join(c if c.isalnum() else "_" for c in why))
            self.fake_slurm(d, line=line)
            rec = d / "scontrol-job.txt"
            env = dict(os.environ, PATH=f"{d}:{os.environ['PATH']}", SLURM_JOB_ID=PENDING_JOB)
            r = subprocess.run([sys.executable, self.root / PKG_REL / "xr_admit.py", "jobcheck", "--admission", self.adm,
                                "--run", "X0", "--record", rec], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, code, f"{why}: {r.stdout} {r.stderr}")
            self.assertEqual(rec.read_text(), line, why)          # recorded even when refused
            if code == 0:
                self.assertEqual(r.stdout.strip(), "12")

    def test_ledger_is_cumulative_over_the_prior_grant_and_flags(self):
        out = self.tmp / "ledger-out"
        out.mkdir()
        adm = json.loads(self.adm.read_text())
        adm["outroot"] = str(out)
        p = self.tmp / "adm-ledger.json"
        p.write_text(json.dumps(adm))
        subs = [{"run": "PF", "kind": "preflight", "attempt": 1, "job_id": 10, "submitted_utc": "2026-10-11T00:00:00Z"},
                {"run": "X0", "kind": "exact", "attempt": 1, "job_id": 11, "submitted_utc": "2026-10-11T00:10:00Z"},
                {"run": "L0", "kind": "lgbm", "attempt": 1, "job_id": 12, "submitted_utc": "2026-10-11T00:10:05Z"},
                {"run": "X1", "kind": "exact", "attempt": 1, "job_id": 13, "submitted_utc": "2026-10-11T00:10:09Z"}]
        (out / "submissions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in subs))
        prior = captured("sacct-X-P-ledger.psv")          # real: header and the five prior jobs
        new = ("10|xrr_PF_a1|COMPLETED|120|billing=12,cpu=12,mem=22860M,node=1|00:05:00\n"
               "11|xrr_X0_a1|COMPLETED|72000|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n"
               "12|xrr_L0_a1|COMPLETED|900|billing=64,cpu=64,mem=121920M,node=1|01:00:00\n"
               "13|xrr_X1_a1|RUNNING|3600|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n")
        psv = self.tmp / "sacct.psv"
        ledger = lambda now: py([self.root / PKG_REL / "xr_admit.py", "ledger", "--admission", p, "--sacct", psv,
                                 "--now", now])
        psv.write_text(prior + new)
        r = ledger("2026-10-12T00:00:00Z")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        led = json.loads(r.stdout)
        self.assertEqual(led["prior_charged_node_h"], 0.0013498263888888891)
        amend = 12 / 256 * 120 / 3600 + 12 / 256 * 20 + 64 / 256 * 0.25 + 12 / 256 * 1
        self.assertAlmostEqual(led["amendment_charged_node_h"], amend, places=12)
        self.assertAlmostEqual(led["cumulative_charged_node_h"], 0.0013498263888888891 + amend, places=12)
        self.assertAlmostEqual(led["unfinished_ceiling_node_h"], 1.40625, places=12)
        self.assertAlmostEqual(led["hours_since_first_submission"], 24.0, places=9)
        r = ledger("2026-10-14T00:00:01Z")       # past the stop with job 13 still running
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("cancel them", r.stdout)
        for why, text, flag in (
                ("a prior job missing", prior.replace("59648611|", "59648699|"), "prior job 59648611"),
                ("a prior charge changed", prior.replace("|xr_X1_a1|FAILED|7|", "|xr_X1_a1|FAILED|8|"), "differs from the recorded"),
                ("another xr_ job", prior + "59700000|xr_X0_a2|FAILED|5|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n",
                 "carries the prior prefix"),
                ("an unrecorded xrr_ job", prior + "14|xrr_X0p_a1|PENDING|0||1-06:00:00\n", "not in the submissions record")):
            psv.write_text(text + new)
            r = ledger("2026-10-12T00:00:00Z")
            self.assertEqual(r.returncode, 6, f"{why}: {r.stdout}")
            self.assertIn(flag, r.stdout, why)
        psv.write_text(prior + new.replace("billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n12",
                                           "billing=24,cpu=24,mem=45720M,node=1|1-06:00:00\n12"))
        r = ledger("2026-10-12T00:00:00Z")
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("billing 24 > 12", r.stdout)

    # ------------------------------------------------------------------ the preflight
    def test_the_preflight_through_the_job_script_passes_without_a_fit(self):
        self.assertEqual(self.pf.returncode, 0, self.pf.stdout[-2000:] + self.pf.stderr[-3000:])
        d = Path(self.admj["outroot"], "PF", "a1")
        rec = json.loads((d / "preflight-receipt.json").read_text())
        self.assertEqual(rec["schema"], "xr-preflight-receipt/1")
        self.assertEqual(rec["status"], "preflight-pass", rec.get("error"))
        self.assertEqual(rec["fits"], [])
        self.assertIn("not_a_result", rec)
        # every step a run takes before its first fit
        self.assertEqual((d / "scontrol-job.txt").read_text(), preflight_line())
        self.assertEqual(rec["allocation_record"]["line"], preflight_line())
        self.assertTrue(rec["identity"]["strict"])
        executed = {e["relpath"] for e in rec["identity"]["executed"]}
        runs = json.loads((self.root / PKG_REL / "manifest/runs.json").read_text())["runs"]
        for run in RUNS:
            self.assertIn(runs[run]["driver"], executed)
        self.assertIn(HELPER, executed)
        self.assertEqual(set(rec["inputs_start"]), {"omnifile", "mcfile"})
        self.assertEqual(rec["inputs_start"]["omnifile"]["sha256"], sha(self.omni))
        self.assertEqual(rec["environment_checked"]["packages"], local_environment()["packages"])
        self.assertGreaterEqual(rec["cpu_count"]["physical_cores"], 1)
        self.assertEqual(rec["threads"], {"OMP_NUM_THREADS": "12", "kind_omp_threads": 12})
        self.assertTrue(Path(self.admj["outroot"], "PF", "a1", "inventory.jsonl").is_file())
        # no result of any kind
        self.assertFalse(list(d.glob("*.root")))
        self.assertFalse((d / "receipt.json").exists())
        xa = load_admit()
        self.assertTrue(xa.preflight_passed(self.admj, xa.load_runs()))
        self.assertFalse(xa.comparable(self.admj, "PF"))

    def test_the_preflight_refuses_the_wrong_thread_count(self):
        # run directly (not through the job script) with one thread: refused, recorded, no fit
        root, pc, ms = make_checkout(self.tmp, "PT", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "PT")
        Path(admj["outroot"], "PF", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "PF")
        self.assertEqual(r.returncode, 6, r.stderr)
        got = json.loads(Path(admj["outroot"], "PF", "a1", "preflight-receipt.json").read_text())
        self.assertEqual(got["status"], "preflight-fail")
        self.assertIn("OMP_NUM_THREADS='1'", got["error"])
        self.assertEqual(got["fits"], [])
        xa = load_admit()
        self.assertFalse(xa.preflight_passed(admj, xa.load_runs()))


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
            r = {"schema": "xr-receipt/2", "run": "X0", "attempt": 1, "status": "complete",
                 "admission": {"path": str(adm.resolve()), "sha256": xc.sha(adm)},
                 "output": {"path": str(prod), "sha256": xc.sha(prod)}}
            r.update(upd)
            (root / "X0" / "a1" / "receipt.json").write_text(json.dumps(r))
        receipt()
        self.assertIsNone(xc.newest_complete(root, "X0")[1])
        for why, upd in (("run", {"run": "X1"}),
                         ("admission digest", {"admission": {"path": str(adm.resolve()), "sha256": "0" * 64}}),
                         ("admission path", {"admission": {"path": str(self.tmp / "admission.json"), "sha256": xc.sha(adm)}}),
                         ("output digest", {"output": {"path": str(prod), "sha256": "0" * 64}}),
                         ("a preflight receipt", {"schema": "xr-preflight-receipt/1", "kind": "preflight"}),
                         ("no schema", {"schema": None})):
            receipt(**upd)
            new, err = xc.newest_complete(root, "X0")
            self.assertIsNone(new, why)
            self.assertTrue(err, why)


class Scheduler(unittest.TestCase):
    """The allocation and sacct parsers on captured real Perlmutter output (tests/scheduler/)."""

    @classmethod
    def setUpClass(cls):
        cls.xa = load_admit()
        cls.runs = cls.xa.load_runs()

    def test_the_captured_format_has_AllocTRES_and_no_TRES_field(self):
        import re
        for job in ("59645304", "59645305"):
            line = captured(f"scontrol-pending-{job}.txt")
            self.assertIsNone(re.search(r"(^|\s)TRES=", line), job)
            self.assertEqual(self.xa.scontrol_field(line, "AllocTRES"), "(null)")
            self.assertIsNotNone(self.xa.parse_billing(self.xa.scontrol_field(line, "ReqTRES")))
            self.assertIn("SubmitLine=sbatch ", line)      # free text with spaces after the fields

    def test_billing_is_read_from_AllocTRES_explicitly(self):
        xa, lgbm = self.xa, self.runs["kinds"]["lgbm"]
        ok = running_line()                               # sb1_C's shape: shared, 64 CPUs, 40 min
        self.assertEqual(xa.check_allocation(ok, lgbm, PENDING_JOB)["billing"], 64)
        # the old parser on the same real line: no TRES field, so it refused every valid allocation
        old = dict(tok.split("=", 1) for tok in ok.split() if "=" in tok).get("TRES", "")
        self.assertIsNone(xa.parse_billing(old))
        import re
        refuse = {
            "pending (null)": scontrol_line(),
            "billing over the cap": running_line(AllocTRES="cpu=64,mem=121920M,node=1,billing=65"),
            "no billing": running_line(AllocTRES="cpu=64,mem=121920M,node=1"),
            "billing not a number": running_line(AllocTRES="cpu=64,mem=121920M,node=1,billing=6x4"),
            "empty billing": running_line(AllocTRES="cpu=64,mem=121920M,node=1,billing="),
            "billing twice": running_line(AllocTRES="billing=1,cpu=64,mem=121920M,node=1,billing=64"),
            "empty AllocTRES": running_line(AllocTRES=""),
            "AllocTRES absent": re.sub(r" AllocTRES=\S*", "", ok),
            "AllocTRES twice (SubmitLine)": ok.replace("SubmitLine=sbatch ", "SubmitLine=sbatch AllocTRES=billing=1 "),
            "QOS twice": ok.replace("SubmitLine=sbatch ", "SubmitLine=sbatch QOS=shared "),
            "another job": running_line(JobId="59645305"),
            "unlimited time": running_line(TimeLimit="UNLIMITED"),
            "64 CPUs over 1 h": running_line(TimeLimit="01:00:01"),
            "empty output": "",
            "the old fixture's format": "JobId=59645304 QOS=shared NumCPUs=64 TimeLimit=00:40:00 TRES=cpu=64,billing=64",
        }
        for why, line in refuse.items():
            with self.assertRaises(xa.Refusal, msg=why):
                xa.check_allocation(line, lgbm, PENDING_JOB)
        with self.assertRaisesRegex(xa.Refusal, "AllocTRES appears 2 times"):
            xa.check_allocation(refuse["AllocTRES twice (SubmitLine)"], lgbm, PENDING_JOB)
        with self.assertRaisesRegex(xa.Refusal, "AllocTRES appears 0 times"):
            xa.check_allocation(refuse["AllocTRES absent"], lgbm, PENDING_JOB)
        # each kind's caps on its own real-format allocation
        exact = running_line(NumCPUs="12", TimeLimit="1-06:00:00", AllocTRES="cpu=12,mem=22860M,node=1,billing=12")
        self.assertEqual(xa.check_allocation(exact, self.runs["kinds"]["exact"], PENDING_JOB)["billing"], 12)
        self.assertEqual(xa.check_allocation(preflight_line(), self.runs["kinds"]["preflight"], PENDING_JOB)["billing"], 12)
        with self.assertRaises(xa.Refusal):
            xa.check_allocation(running_line(NumCPUs="12", TimeLimit="00:05:01",
                                             AllocTRES="cpu=12,mem=22860M,node=1,billing=12"),
                                self.runs["kinds"]["preflight"], PENDING_JOB)

    def test_the_sacct_parsers_on_captured_output(self):
        xa = self.xa
        rows = xa.sacct_jobs(SCHED / "sacct-X-n-P.psv", "xr")
        self.assertEqual(sorted((j["job_id"], j["run"], j["state"]) for j in rows),
                         [("59648608", "X0", "FAILED"), ("59648610", "X0p", "FAILED"), ("59648611", "X1", "FAILED"),
                          ("59648616", "L0", "FAILED"), ("59648617", "L1", "FAILED")])
        self.assertEqual(xa.sacct_jobs(SCHED / "sacct-X-n-P.psv", "xrr"), [])
        self.assertEqual(sorted(j["job_id"] for j in xa.sacct_jobs(SCHED / "sacct-steps-P.psv", "xr")),
                         ["59648608", "59648616"])                 # header and .batch/.extern steps excluded
        xa.check_prior(self.runs, SCHED / "sacct-X-n-P.psv")
        self.assertIsNone(xa.parse_billing("cpu=12,mem=22860M,node=1"))      # a step's AllocTRES
        self.assertEqual(xa.parse_billing("billing=12,cpu=12,mem=22860M,node=1"), 12)
        head, *lines = captured("sacct-X-P-ledger.psv").splitlines()
        total = 0.0
        for line in lines:
            r = dict(zip(head.split("|"), line.split("|")))
            total += xa.charge(r)[0]
        self.assertEqual(total, self.runs["prior"]["charged_node_h_recorded"])
        self.assertEqual({l.split("|")[0]: l.split("|")[1][3:].rsplit("_a", 1)[0] for l in lines}, self.runs["prior"]["jobs"])


class FitCounts(unittest.TestCase):
    def test_the_preflight_recorder_refuses_every_fit(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("xr_run_pf", PKG / "xr_run.py")
        xr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xr)
        import numpy as np
        import sklearn.ensemble as ske
        import lightgbm
        classes = (ske.GradientBoostingClassifier, ske.GradientBoostingRegressor, lightgbm.LGBMClassifier,
                   lightgbm.LGBMRegressor)
        orig = [c.fit for c in classes]
        rec = xr.FitRecorder(None)
        rec.install()
        try:
            X, y = np.zeros((4, 1)), [0, 1, 0, 1]
            for cls in classes:
                with self.assertRaises(xr.BackendRefusal, msg=cls.__name__):
                    cls().fit(X, y)
        finally:
            for c, f in zip(classes, orig):
                c.fit = f
        self.assertEqual(rec.fits, [])

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
