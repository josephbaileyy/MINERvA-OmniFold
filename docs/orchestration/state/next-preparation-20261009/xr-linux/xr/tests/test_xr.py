"""XR package (xr-linux) end to end, on a synthetic fixture, in throwaway git checkouts.

Each checkout holds the real 2D driver, the real OmniFold helper, ``n2/``, the OI-136 guard and
its shim, X0p's record of the ``d1bc8813`` driver, SB1's fixture writer, and this package;
``manifest/runs.json`` and ``references.json`` are rewritten to the fixture inputs and to fixture
reference products made by the real driver without the wrapper. The admission chain is the real
one: manifest, package commit, AUTHORIZATION record, draft.

The suite runs on macOS, which cannot show the Linux-only child launches (``ldconfig`` through
``ctypes.util.find_library``) that stopped the 2026-10-11 preflight: the package's preflight runs
the same fixture stage inside the allocation, under the guard, for that. Here, test checkouts that
train ("mac kinds") give every kind 2 CPUs (LightGBM 1) and set ``LOKY_MAX_CPU_COUNT``, which
stands in for the CPU affinity macOS lacks (``xr_run.thread_plan``). Nothing here touches a
cluster.

    PYTHONPATH=$(root-config --libdir) python3.13 -m unittest test_xr -v
"""

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
REPO = PKG.parents[5]
PKG_REL = PKG.relative_to(REPO).as_posix()
Q = "docs/orchestration/state/next-preparation-20261009"
sys.path.insert(0, str(REPO / Q / "sb1-prep/tests"))
import make_fixture_omnifile as mk  # noqa: E402

DRIVER = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
HELPER = "unbinned_unfolding/python/omnifold.py"
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
GUARD = "nd-unfolding/mnv_guarded_run.py"
RECORD = f"{Q}/two-d-followup/xr/record/unfold_2d_omnifold_unbinned_d1bc8813.py.record"
MAKER = f"{Q}/sb1-prep/tests/make_fixture_omnifile.py"
COPIED = (DRIVER, HELPER, GUARD, f"{N2}/__init__.py", f"{N2}/execution.py", RECORD, MAKER)
RUNS = ("X0", "X0p", "X1", "L0", "L1")
SCHED = HERE / "scheduler"          # real Perlmutter scheduler output, captured read-only (README.txt)
PF_JOB = "59655414"                 # the 2026-10-11 preflight, whose RUNNING line is captured
PENDING_JOB = "59645304"
SACCT_NOW = "sacct-X-n-P-20261011.psv"
LEDGER_NOW = "sacct-X-P-ledger-20261011.psv"
PRIOR_CHARGE = 0.002313368055555556
MAC_KINDS = {"exact": 2, "preflight": 2, "lgbm": 1}


def captured(name):
    return (SCHED / name).read_text()


def substitute(line, **fields):
    """``line`` with named ``Key=Value`` fields replaced. Each field must occur exactly once as a
    token, so a test cannot invent a field the real format lacks."""
    for key, val in fields.items():
        pat = re.compile(r"(^|\s){}=\S*".format(re.escape(key)))
        assert len(pat.findall(line)) == 1, f"{key} is not a single field of the captured line"
        line = pat.sub(lambda m: f"{m.group(1)}{key}={val}", line)
    return line


def scontrol_line(**fields):
    """The captured PENDING line (AllocTRES=(null)) with named fields replaced."""
    return substitute(captured(f"scontrol-pending-{PENDING_JOB}.txt"), **fields)


def running_line(**fields):
    """The captured RUNNING line of the 2026-10-11 preflight (12 CPUs, 5 min, billing 12), fields replaced."""
    return substitute(captured(f"scontrol-running-{PF_JOB}.txt"), **fields)


def preflight_line(job=PF_JOB):
    return running_line() if job == PF_JOB else running_line(JobId=job)


def lgbm_line(**fields):
    return running_line(**dict({"NumCPUs": "64", "TimeLimit": "01:00:00",
                                "AllocTRES": "cpu=64,mem=121920M,node=1,billing=64"}, **fields))


def exact_line(**fields):
    return running_line(**dict({"NumCPUs": "12", "TimeLimit": "1-06:00:00",
                                "AllocTRES": "cpu=12,mem=22860M,node=1,billing=12"}, **fields))


def load_module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_admit():
    return load_module("xr_admit_unit", PKG / "xr_admit.py")


def load_run():
    return load_module("xr_run_unit", PKG / "xr_run.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null", "-c", "user.name=fixture",
                           "-c", "user.email=fixture@invalid", *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def py(argv, cwd=None, env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("MNV_GUARD") and k != "LOKY_MAX_CPU_COUNT"}
    e.update(OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    e.update(env or {})
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, env=e, cwd=cwd)


def kind_env(root, run):
    """The thread environment a job of the run's kind gets (macOS: LOKY_MAX_CPU_COUNT as the affinity)."""
    runs = json.loads((root / PKG_REL / "manifest/runs.json").read_text())
    k = runs["kinds"][runs["runs"][run]["kind"]]
    return {"OMP_NUM_THREADS": str(k["omp_threads"]), "LOKY_MAX_CPU_COUNT": str(k["cpus_per_task"])}


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


def make_checkout(base, name, omni, flux, refs, mutate=None, mac=False):
    """A throwaway checkout whose frozen outroot is ``base/out-<name>``; ``mac`` gives the kinds the
    test machine's thread counts (MAC_KINDS)."""
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
    if mac:
        for k, n in MAC_KINDS.items():
            runs["kinds"][k].update(cpus_per_task=n, omp_threads=n, billing_max=n)
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
    auth = root / "docs/orchestration/AUTHORIZATION-20261011-xr-linux.md"
    auth.write_text(f"# fixture authorization\n\npackage commit `{pkg_commit}`\nmanifest `{man_sha}`\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "authorization")
    return root, pkg_commit, man_sha


AUTH = "docs/orchestration/AUTHORIZATION-20261011-xr-linux.md"


def draft_cmd(root, pkg_commit, man_sha):
    return py([root / PKG_REL / "xr_admit.py", "draft", "--authorization", AUTH,
               "--package-commit", pkg_commit, "--manifest-sha", man_sha, "--setup", root / "setup_env.sh"])


def draft(root, pkg_commit, man_sha, base, tag):
    r = draft_cmd(root, pkg_commit, man_sha)
    assert r.returncode == 0, r.stderr + r.stdout
    adm = base / f"out-{tag}" / "admission.json"
    return adm, json.loads(adm.read_text())


def run_xr(root, adm, run, attempt=1, guard=True, cwd=None, strict=True, env=None):
    cmd = [root / PKG_REL / "xr_run.py", "--run", run, "--attempt", str(attempt), "--admission", adm]
    if strict:
        cmd.append("--require-provenance")
    if guard:
        cmd = [root / GUARD, "--expect-root", root, "--inventory", Path(adm).parent / f"inv-{run}-{attempt}.jsonl",
               "--label", run, "--", *cmd]
    return py(cmd, cwd=cwd or root / "2d-unfolding", env=dict(kind_env(root, run), **(env or {})))


def receipt(adm_json, run, attempt=1, name="receipt.json"):
    p = Path(adm_json["outroot"], run, f"a{attempt}", name)
    return json.loads(p.read_text()) if p.exists() and p.stat().st_size else None


def write_preflight_pass(admj, attempt=1, job=None, line=None, record=True, inventory=None, **upd):
    """A passing preflight receipt bound to its PF job, as the job writes one: the job id is the PF
    submission's (a submission is recorded if there is none), the allocation line is recorded in
    ``scontrol-job.txt`` and in the receipt, the fixture stage and controls are met and the guard
    inventory is clean. ``upd`` overrides receipt fields; ``inventory`` replaces the inventory record."""
    import datetime
    adm = Path(admj["outroot"], "admission.json")
    subs_p = Path(admj["outroot"], "submissions.jsonl")
    subs = [json.loads(l) for l in subs_p.read_text().splitlines() if l.strip()] if subs_p.exists() else []
    pf = [s for s in subs if s["run"] == "PF" and s["attempt"] == attempt]
    if pf:
        job = job or str(pf[0]["job_id"])
    else:
        job = job or PF_JOB
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(subs_p, "a") as fh:
            fh.write(json.dumps({"run": "PF", "kind": "preflight", "attempt": attempt, "job_id": int(job),
                                 "submitted_utc": now}) + "\n")
    d = Path(admj["outroot"], "PF", f"a{attempt}")
    d.mkdir(parents=True, exist_ok=True)
    line = preflight_line(job) if line is None else line
    r = {"schema": "xr-preflight-receipt/2", "run": "PF", "attempt": attempt, "kind": "preflight",
         "status": "preflight-pass", "fits": [], "exit_code": 0, "identity": {"strict": True}, "launches": [],
         "environment": {"slurm": {"SLURM_JOB_ID": job}},
         "admission": {"path": str(adm.resolve()), "sha256": sha(adm)},
         "fixture": {"verdict": "PASS", "runs": {r_: {"status": "complete"} for r_ in RUNS + ("L0-repeat",)},
                     "checks": {"all_complete": True, "repeat_reproduces_to_the_criterion": True},
                     "controls": {"wrong_seed": {"met": True}, "launch_window": {"met": True}}},
         "controls": {"jobcheck_other_kind": {"met": True}, "guard_refuses_launch": {"met": True}}}
    if record:
        (d / "scontrol-job.txt").write_text(line)
        r["allocation_record"] = {"path": str(d / "scontrol-job.txt"), "sha256": sha(d / "scontrol-job.txt"), "line": line}
    r.update(upd)
    (d / "preflight-receipt.json").write_text(json.dumps(r))
    inv = {"label": f"XR-PF-a{attempt}", "verdict": "REPOSITORY-ORIGINS-INSPECTED", "violation": None,
           "repo_origins_outside_expect_root": 0, "guard_installed": True}
    (d / "inventory.jsonl").write_text(json.dumps(inventory if inventory is not None else inv) + "\n")
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


def fixture_inputs(tmp):
    (tmp / "inputs").mkdir()
    omni = tmp / "inputs" / "omni.root"
    mk.write_fixture(str(omni), rows=3000, extra=4)
    flux = Path(mk.write_flux(str(tmp / "inputs" / "flux.root")))
    return omni, flux


class XR(unittest.TestCase):
    """The five runs end to end under the guard, strict, on the fixture (mac kinds)."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        cls.omni, cls.flux = fixture_inputs(cls.tmp)
        # fixture reference products, made by the real driver without the wrapper, on the same
        # thread counts as the wrapped runs (LightGBM 1)
        stage = cls.tmp / "stage"
        (stage / "2d-unfolding").mkdir(parents=True)
        shutil.copy2(REPO / DRIVER, stage / DRIVER)
        (stage / HELPER).parent.mkdir(parents=True)
        shutil.copy2(REPO / HELPER, stage / HELPER)
        (cls.tmp / "refs").mkdir()
        cls.refs = {}
        for key, extra, threads in (("E_C", [], "2"), ("CV42", ["--estimator", "lgbm", "--seed", "42"], "1"),
                                    ("SEED1", ["--estimator", "lgbm", "--seed", "1"], "1"), ("EXACT_SEED1", ["--seed", "1"], "2")):
            out = cls.tmp / "refs" / f"{key}.root"
            r = py([stage / DRIVER, "--omnifile", cls.omni, "--mcfile", cls.flux, "--iters", "5", "--use-weights",
                    *extra, "--out", out], cwd=stage / "2d-unfolding",
                   env={"PYTHONPATH": f"{stage / 'unbinned_unfolding/python'}:{os.environ.get('PYTHONPATH', '')}",
                        "OMP_NUM_THREADS": threads, "LOKY_MAX_CPU_COUNT": threads})
            assert r.returncode == 0, r.stderr[-3000:]
            cls.refs[key] = ref_record(out)
        cls.refs["PN_CV"] = dict(cls.refs["CV42"])
        cls.root, cls.pkg, cls.man = make_checkout(cls.tmp, "A", cls.omni, cls.flux, cls.refs, mac=True)
        cls.adm, cls.admj = draft(cls.root, cls.pkg, cls.man, cls.tmp, "A")
        cls.results = {}
        for run in RUNS:
            Path(cls.admj["outroot"], run, "a1").mkdir(parents=True)
            cls.results[run] = run_xr(cls.root, cls.adm, run)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def checkout(self, tag, mutate=None, refs=None):
        root, pc, ms = make_checkout(self.tmp, tag, self.omni, self.flux, refs or dict(self.refs), mutate, mac=True)
        return root, pc, ms

    # ------------------------------------------------------------------ positive path
    def test_all_five_runs_complete_strict_with_their_intended_backend_seeds_and_threads(self):
        runs = json.loads((self.root / PKG_REL / "manifest/runs.json").read_text())
        for run in RUNS:
            r = self.results[run]
            self.assertEqual(r.returncode, 0, f"{run}: {r.stderr[-2000:]}")
            rec = receipt(self.admj, run)
            self.assertEqual(rec["status"], "complete")
            want = runs["runs"][run]["backend"]
            classes = {f["class"] for f in rec["fits"]}
            self.assertEqual(classes, {want["classifier"], want["regressor"]}, run)
            seeds = [f["random_state"] for f in rec["fits"] if f["class"] == want["classifier"]]
            self.assertEqual(seeds, [want["random_state"]["step1"], want["random_state"]["step2"]] * 5, run)
            self.assertEqual(rec["fit_counts"], {"classifier_fits": 10, "regressor_fits": 5}, run)
            self.assertTrue(rec["identity"]["strict"])
            self.assertEqual(rec["identity"]["git"]["mismatched"], [])
            self.assertEqual(rec["launches"], [])
            self.assertEqual(rec["output"]["n_reported"], len(self.refs["E_C"]["reported_globalid"]))
            executed = {e["relpath"] for e in rec["identity"]["executed"]}
            self.assertIn(runs["runs"][run]["driver"], executed)
            self.assertIn(HELPER, executed)
            self.assertEqual(rec["driver_argv"][-2:], ["--out", str(Path(self.admj["outroot"], run, "a1", f"XR-{run}.root"))])
            kind = runs["kinds"][runs["runs"][run]["kind"]]
            self.assertEqual(rec["threads"]["lgbm_num_threads"], kind["cpus_per_task"])
            self.assertEqual(rec["threads"]["joblib_cpu_count_physical"], kind["cpus_per_task"])
            if want["estimator"] == "lgbm":
                self.assertTrue(all(f["num_threads"] == kind["cpus_per_task"] for f in rec["fits"]), run)
                self.assertGreater(rec["predicts"]["calls"], 0)
                self.assertEqual(rec["predicts"]["num_threads"], [kind["cpus_per_task"]])
            else:
                self.assertTrue(all(f["num_threads"] is None for f in rec["fits"]), run)
                self.assertEqual(rec["threads"]["exact_estimator_threads"], 1)

    def test_the_d1bc8813_record_driver_is_what_X0p_executed(self):
        rec = receipt(self.admj, "X0p")
        drv = [e for e in rec["identity"]["executed"] if e["relpath"] == RECORD]
        self.assertEqual(len(drv), 1)
        self.assertEqual(drv[0]["sha256"], "447288e2c61d30cdd46c88077093ec0d78ac08ae63144bb2fe57525e7144ea34")
        self.assertEqual(drv[0]["git_blob"], "0f87330b3fe6e61d8922fafaefd0c17165f752b1")

    def test_comparator_on_the_fixture(self):
        """Deterministic arms reproduce their unwrapped fixture references to 1e-8 (so the recorder,
        the thread plan and the launch window change no result). The unseeded exact arms are NOT
        asserted: with tied rows sklearn's exact backend with random_state=None differs run to run."""
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
        self.assertEqual(sorted(c), ["L0_vs_CV42", "L0_vs_PN_CV", "L1_vs_SEED1", "NC_X0_vs_CV42", "X0_vs_E_C",
                                     "X0p_vs_E_C", "X1_vs_X0"])
        xc = load_module("xr_compare", self.root / PKG_REL / "xr_compare.py")
        x1 = Path(self.admj["outroot"], "X1", "a1", "XR-X1.root")
        seeded = xc.compare(x1, self.refs["EXACT_SEED1"]["path"], self.refs["E_C"]["reported_globalid"])
        self.assertEqual(seeded["verdict"], "PASS", seeded)    # a seeded exact run is reproducible
        self.assertEqual(seeded["exactly_equal_cells"], seeded["n_cells"])

    def test_the_environment_record_is_child_free(self):
        rec = receipt(self.admj, "L0")
        env = rec["environment_checked"]
        self.assertEqual(env["packages"], local_environment()["packages"])
        self.assertTrue(env["origins"]["lightgbm"].endswith("__init__.py"))
        self.assertNotIn("threadpools", env)
        self.assertIn("runtime", env)
        if sys.platform != "linux":
            self.assertTrue(env["runtime"]["source"].startswith("unavailable"))

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
        root, pc, ms = self.checkout("F", mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "F")
        Path(admj["outroot"], "X0", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "X0")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("frozen reference", r.stderr)

    def test_an_outroot_inside_the_checkout_is_refused(self):
        def mutate(root, runs, refs):
            runs["outroot"] = str(root / "inside")
        root, pc, ms = self.checkout("IN", mutate)
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
        self.assertEqual(run_xr(self.root, self.adm, "L0", attempt=1, env={}).returncode, 3)   # a1 is used
        r = py([self.root / PKG_REL / "xr_run.py", "--run", "X9", "--attempt", "1", "--admission", self.adm])
        self.assertEqual(r.returncode, 3)
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
            root, pc, ms = self.checkout(tag, mutate)
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
        root, pc, ms = self.checkout("I", mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "I")
        Path(admj["outroot"], "L0", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "L0")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("input omnifile", r.stderr)
        rec = Path(admj["outroot"], "L0", "a1", "receipt.json")
        self.assertTrue(rec.exists() and rec.stat().st_size == 0, "the run started before the input refusal")

    # ------------------------------------------------------------------ refusals during or after the run (exit 6)
    def test_a_backend_other_than_the_frozen_one_stops_before_training(self):
        def mutate(root, runs, refs):
            runs["runs"]["X0"]["argv"] = ["--omnifile", "{omnifile}", "--mcfile", "{mcfile}", "--iters", "5",
                                         "--use-weights", "--estimator", "lgbm", "--out", "{out}"]
        root, pc, ms = self.checkout("B", mutate)
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
        root, pc, ms = self.checkout("S", mutate)
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
            root, pc, ms = self.checkout(tag, mutate)
            adm, admj = draft(root, pc, ms, self.tmp, tag)
            Path(admj["outroot"], "L1", "a1").mkdir(parents=True)
            r = run_xr(root, adm, "L1")
            self.assertEqual(r.returncode, 6, r.stderr)
            rec = receipt(admj, "L1")
            self.assertEqual(rec["status"], "backend-refused")
            self.assertIn("environment differs", rec["error"])
            self.assertEqual(rec["fits"], [])

    def test_a_thread_count_other_than_the_kinds_stops_before_training(self):
        """The thread plan refuses before any fit: OMP_NUM_THREADS, or a joblib count (here its
        stand-in) other than the kind's CPUs."""
        for att, env, text in ((2, {"OMP_NUM_THREADS": "3"}, "OMP_NUM_THREADS='3'"),
                               (3, {"LOKY_MAX_CPU_COUNT": "1"}, "LOKY_MAX_CPU_COUNT must equal")):
            self.fresh_attempt("X1", att)
            r = run_xr(self.root, self.adm, "X1", attempt=att, env=env)
            self.assertEqual(r.returncode, 6, r.stderr)
            rec = receipt(self.admj, "X1", att)
            self.assertEqual(rec["status"], "backend-refused")
            self.assertIn(text, rec["error"])
            self.assertEqual(rec["fits"], [])

    def test_a_normalization_differing_from_the_reference_is_refused(self):
        refs = json.loads(json.dumps(self.refs))
        refs["E_C"]["params"]["nNucleons"] *= 1.000001
        root, pc, ms = self.checkout("N", refs=refs)
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
        self.assertEqual(self.check(self.root, AUTH, self.pkg, self.man).returncode, 0)
        cases = {"abbreviated commit": (AUTH, self.pkg[:12], self.man),
                 "other manifest digest": (AUTH, self.pkg, "0" * 64),
                 "absolute path": (str(self.root / AUTH), self.pkg, self.man),
                 "outside docs/orchestration": ("setup_env.sh", self.pkg, self.man),
                 "dot-dot": ("docs/orchestration/../../setup_env.sh", self.pkg, self.man)}
        for why, (a, c, m) in cases.items():
            r = self.check(self.root, a, c, m)
            self.assertEqual(r.returncode, 3, f"{why}: {r.stdout} {r.stderr}")

    def test_a_second_draft_for_the_same_package_is_refused(self):
        r = draft_cmd(self.root, self.pkg, self.man)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("one admission per grant", r.stderr)
        self.assertEqual(json.loads(self.adm.read_text())["drafted_utc"], self.admj["drafted_utc"])

    def test_verify_refuses_a_changed_nested_setup_or_a_copied_admission(self):
        root, pc, ms = self.checkout("V")
        adm, admj = draft(root, pc, ms, self.tmp, "V")
        verify = lambda a: py([root / PKG_REL / "xr_admit.py", "verify", "--admission", a])
        self.assertEqual(verify(adm).returncode, 0, verify(adm).stderr)
        copy_ = self.tmp / "adm-V-copy.json"
        shutil.copy2(adm, copy_)
        self.assertEqual(verify(copy_).returncode, 3)
        self.assertEqual(git(root, "status", "--porcelain"), "")
        with open(root / "nested/one.sh", "a") as fh:       # an untracked file: only its digest sees it
            fh.write("export X=1\n")
        self.assertEqual(git(root, "status", "--porcelain"), "")
        r = verify(adm)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("changed since admission", r.stderr)

    def test_a_package_change_after_the_package_commit_is_refused(self):
        root, pc, ms = self.checkout("P")
        with open(root / PKG_REL / "xr_compare.py", "a") as fh:
            fh.write("\n# later\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "later change")
        r = self.check(root, AUTH, pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("changed after", r.stderr)

    def test_a_change_to_an_executed_file_outside_the_package_is_refused(self):
        """X0p's record and the fixture writer live in frozen packages; the binding covers them."""
        for rel in (RECORD, MAKER):
            tag = "PR" if rel == RECORD else "PM"
            root, pc, ms = self.checkout(tag)
            with open(root / rel, "a") as fh:
                fh.write("\n# later\n")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "later change")
            r = self.check(root, AUTH, pc, ms)
            self.assertEqual(r.returncode, 3, f"{rel}: {r.stderr}")
            self.assertIn("changed after", r.stderr)

    def test_an_uncommitted_or_symlinked_authorization_is_refused(self):
        root, pc, ms = self.checkout("U")
        a = root / "docs/orchestration/AUTHORIZATION-20261012-xr-other.md"
        a.write_text(f"{pc} {ms}\n")
        r = self.check(root, "docs/orchestration/AUTHORIZATION-20261012-xr-other.md", pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)
        link = root / "docs/orchestration/AUTHORIZATION-20261013-xr.md"
        link.symlink_to(root / AUTH)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "symlink")
        r = self.check(root, "docs/orchestration/AUTHORIZATION-20261013-xr.md", pc, ms)
        self.assertEqual(r.returncode, 3, r.stderr)


class Launch(unittest.TestCase):
    """Admission, scheduler, release order, ledger and the preflight. The preflight runs through the
    real xr_job.sbatch on a mac-kinds checkout (fake scontrol printing the captured RUNNING line at
    the mac preflight size); everything else uses the real kinds and does not train."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name).resolve()
        cls.omni, cls.flux = fixture_inputs(cls.tmp)
        cls.refs = {k: {"path": str(cls.tmp / "refs" / f"{k}.root"), "sha256": "0" * 64, "params": {},
                        "reported_globalid": []} for k in ("E_C", "CV42", "SEED1", "PN_CV")}
        cls.root, cls.pkg, cls.man = make_checkout(cls.tmp, "A", cls.omni, cls.flux, cls.refs)
        cls.adm, cls.admj = draft(cls.root, cls.pkg, cls.man, cls.tmp, "A")
        cls.pf_root, cls.pf_pkg, cls.pf_man = make_checkout(cls.tmp, "PF", cls.omni, cls.flux, cls.refs, mac=True)
        cls.pf_adm, cls.pf_admj = draft(cls.pf_root, cls.pf_pkg, cls.pf_man, cls.tmp, "PF")
        cls.pf_line = running_line(NumCPUs="2", AllocTRES="cpu=2,mem=3810M,node=1,billing=2")
        cls.pf = cls.job_script(cls.pf_root, cls.pf_adm, cls.pf_admj, cls.pf_line, "pf")

    @classmethod
    def job_script(cls, root, adm, admj, line, tag, attempt=1):
        """The preflight through the real xr_job.sbatch: jobcheck on a real-format allocation line,
        verify, the setup sourced, the two job controls, the guard, xr_run.py --run PF."""
        Path(admj["outroot"], "PF", f"a{attempt}").mkdir(parents=True)
        slurm = cls.tmp / f"slurm-{tag}"
        slurm.mkdir()
        (slurm / "scontrol").write_text(f"#!/bin/bash\ncat {slurm / 'line.txt'}\n")
        (slurm / "line.txt").write_text(line)
        (slurm / "python").write_text(f"#!/bin/bash\nexec {sys.executable} \"$@\"\n")
        for f in ("scontrol", "python"):
            (slurm / f).chmod(0o755)
        env = {k: v for k, v in os.environ.items() if not k.startswith("MNV_GUARD")}
        env.update(PATH=f"{slurm}:{os.environ['PATH']}", SLURM_JOB_ID=PF_JOB, PYTHONDONTWRITEBYTECODE="1",
                   LOKY_MAX_CPU_COUNT=str(MAC_KINDS["preflight"]))
        with open(Path(admj["outroot"], "submissions.jsonl"), "a") as fh:
            fh.write(json.dumps({"run": "PF", "kind": "preflight", "attempt": attempt, "job_id": int(PF_JOB),
                                 "submitted_utc": "2026-10-11T06:00:00Z"}) + "\n")
        return subprocess.run(["bash", root / PKG_REL / "launch/xr_job.sbatch", adm, "PF", str(attempt)],
                              capture_output=True, text=True, env=env, cwd=root)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    # ------------------------------------------------------------------ the preflight
    def test_the_preflight_through_the_job_script_passes_with_its_fixture_stage(self):
        self.assertEqual(self.pf.returncode, 0, self.pf.stdout[-2000:] + self.pf.stderr[-4000:])
        d = Path(self.pf_admj["outroot"], "PF", "a1")
        rec = json.loads((d / "preflight-receipt.json").read_text())
        self.assertEqual(rec["schema"], "xr-preflight-receipt/2")
        self.assertEqual(rec["status"], "preflight-pass", rec.get("error"))
        self.assertEqual(rec["fits"], [])
        self.assertEqual(rec["launches"], [])
        self.assertIn("not_a_result", rec)
        self.assertEqual((d / "scontrol-job.txt").read_text(), self.pf_line)
        self.assertEqual(rec["allocation_record"]["line"], self.pf_line)
        self.assertTrue(rec["identity"]["strict"])
        executed = {e["relpath"] for e in rec["identity"]["executed"]}
        runs = json.loads((self.pf_root / PKG_REL / "manifest/runs.json").read_text())
        for run in RUNS:
            self.assertIn(runs["runs"][run]["driver"], executed)
        self.assertIn(HELPER, executed)
        self.assertIn(MAKER, executed)
        self.assertIn(PKG_REL + "/xr_compare.py", executed)
        self.assertEqual(rec["inputs_start"]["omnifile"]["sha256"], sha(self.omni))
        self.assertEqual(rec["environment_checked"]["packages"], local_environment()["packages"])
        self.assertEqual(rec["threads"]["OMP_NUM_THREADS"], "2")
        self.assertEqual(rec["threads"]["lgbm_num_threads"], 2)
        fx = rec["fixture"]
        self.assertEqual(fx["verdict"], "PASS", json.dumps(fx.get("checks")))
        self.assertEqual(set(fx["runs"]), set(RUNS) | {"L0-repeat"})
        for name, r in fx["runs"].items():
            self.assertEqual(r["status"], "complete", f"{name}: {r.get('error')}")
            self.assertEqual(r["fit_counts"], {"classifier_fits": 10, "regressor_fits": 5}, name)
        self.assertTrue(all(fx["checks"].values()), fx["checks"])
        self.assertEqual(fx["comparator"]["L0-repeat_vs_L0"]["verdict"], "PASS")
        self.assertEqual(fx["comparator"]["X0_vs_L0"]["verdict"], "FAIL")
        for name in ("wrong_seed", "wrong_backend", "wrong_lgbm_threads"):
            self.assertTrue(fx["controls"][name]["met"], fx["controls"][name])
            self.assertEqual(fx["controls"][name]["fits"], [], name)
        lw = fx["controls"]["launch_window"]
        self.assertTrue(lw["met"], lw)
        self.assertTrue(lw["probes"]["loky_physical_cores"]["launches"])
        for name in ("jobcheck_other_kind", "guard_refuses_launch"):
            self.assertTrue(rec["controls"][name]["met"], rec["controls"][name])
        self.assertTrue((d / "inventory.jsonl").is_file())
        # no result of any kind: no output or run receipt in the attempt directory itself
        self.assertFalse(list(d.glob("*.root")))
        self.assertFalse((d / "receipt.json").exists())
        xa = load_admit()
        self.assertTrue(xa.inventory_clean(d / "inventory.jsonl", "XR-PF-a1"))
        self.assertTrue(xa.preflight_passed(self.pf_admj, json.loads((self.pf_root / PKG_REL / "manifest/runs.json").read_text())))
        self.assertFalse(xa.comparable(self.pf_admj, "PF"))
        # the comparator never reads the fixture products
        out = self.tmp / "cmp-pf.json"
        r = py([self.pf_root / PKG_REL / "xr_compare.py", "--outroot", self.pf_admj["outroot"], "--out", out])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(all(v["verdict"] == "INCONCLUSIVE" for v in json.loads(out.read_text())["comparisons"].values()))

    def test_the_preflight_fails_when_a_job_control_is_not_met(self):
        """The same job, but the recorded allocation also fits the other kind's caps, so the
        jobcheck control is not refused: the preflight must fail and release nothing."""
        def mutate(root, runs, refs):
            for k in runs["kinds"].values():
                k.update(cpus_per_task=2, omp_threads=2, billing_max=2)
        root, pc, ms = make_checkout(self.tmp, "PC", self.omni, self.flux, self.refs, mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "PC")
        r = self.job_script(root, adm, admj, self.pf_line, "pc")
        self.assertEqual(r.returncode, 6, r.stderr[-3000:])
        rec = receipt(admj, "PF", name="preflight-receipt.json")
        self.assertEqual(rec["status"], "preflight-fail")
        self.assertIn("jobcheck_other_kind", rec["error"])
        self.assertFalse(rec["controls"]["jobcheck_other_kind"]["met"])
        xa = load_admit()
        self.assertFalse(xa.preflight_passed(admj, json.loads((root / PKG_REL / "manifest/runs.json").read_text())))

    def test_the_preflight_pins_the_fixture_writer(self):
        def mutate(root, runs, refs):
            runs["preflight"]["fixture"]["maker_digest"] = "0" * 64
        root, pc, ms = make_checkout(self.tmp, "PW", self.omni, self.flux, dict(self.refs), mutate, mac=True)
        adm, admj = draft(root, pc, ms, self.tmp, "PW")
        Path(admj["outroot"], "PF", "a1").mkdir(parents=True)
        r = run_xr(root, adm, "PF")
        self.assertEqual(r.returncode, 3, r.stderr[-2000:])
        self.assertIn("the preflight pins", r.stderr)
        self.assertEqual(list(Path(admj["outroot"], "PF", "a1").iterdir()), [])

    def test_a_preflight_run_by_hand_outside_the_job_releases_nothing(self):
        """No allocation record, no job controls: the hand-run preflight fails and releases nothing."""
        root, pc, ms = make_checkout(self.tmp, "PH", self.omni, self.flux, dict(self.refs), mac=True)
        adm, admj = draft(root, pc, ms, self.tmp, "PH")
        Path(admj["outroot"], "PF", "a1").mkdir(parents=True)
        Path(admj["outroot"], "submissions.jsonl").write_text(json.dumps(
            {"run": "PF", "kind": "preflight", "attempt": 1, "job_id": int(PF_JOB),
             "submitted_utc": "2026-10-11T00:00:00Z"}) + "\n")
        r = run_xr(root, adm, "PF")
        got = receipt(admj, "PF", name="preflight-receipt.json")
        self.assertNotIn("allocation_record", got)
        self.assertEqual(got["status"], "preflight-fail")
        self.assertIn("job controls not met", got["error"])
        self.assertEqual(r.returncode, 6, r.stderr[-2000:])
        xa = load_admit()
        self.assertFalse(xa.preflight_passed(admj, xa.load_runs()))
        psv = self.tmp / "ph.psv"
        psv.write_text(captured(SACCT_NOW))
        r = py([root / PKG_REL / "xr_admit.py", "next-attempt", "--admission", adm, "--run", "L0", "--sacct", psv])
        self.assertEqual(r.returncode, 3)
        self.assertIn("no passed preflight", r.stderr)

    def test_the_preflight_gate_requires_the_pf_jobs_own_bound_and_complete_receipt(self):
        xa = load_admit()
        runs = xa.load_runs()

        def gate(tag, **kw):
            out = self.tmp / f"gate-{tag}"
            out.mkdir()
            (out / "admission.json").write_text('{"status": "ADMITTED"}\n')
            admj = {"outroot": str(out)}
            write_preflight_pass(admj, **kw)
            return xa.preflight_passed(admj, runs)
        self.assertTrue(gate("ok"))
        bad_fx = lambda **u: dict(fixture=dict({"verdict": "PASS", "runs": {r: {"status": "complete"} for r in RUNS},
                                               "checks": {"all_complete": True},
                                               "controls": {"wrong_seed": {"met": True}}}, **u))
        refused = {"no allocation record": dict(record=False),
                   "record of another job": dict(line=preflight_line("59645305")),
                   "record over the cap": dict(line=running_line(AllocTRES="cpu=12,mem=24765M,node=1,billing=13")),
                   "record of a pending job": dict(line=scontrol_line(NumCPUs="12", TimeLimit="00:05:00")),
                   "no Slurm job id": dict(environment={"slurm": {"SLURM_JOB_ID": None}}),
                   "another job id than submitted": dict(environment={"slurm": {"SLURM_JOB_ID": "59645305"}},
                                                         line=preflight_line("59645305")),
                   "not strict": dict(identity={"strict": False}),
                   "nonzero exit": dict(exit_code=6),
                   "a fit recorded": dict(fits=[{"class": "LGBMClassifier"}]),
                   "the old schema": dict(schema="xr-preflight-receipt/1"),
                   "a launch recorded": dict(launches=[{"call": "subprocess.Popen"}]),
                   "fixture FAIL": bad_fx(verdict="FAIL"),
                   "a fixture run missing": bad_fx(runs={r: {"status": "complete"} for r in RUNS[:-1]}),
                   "a fixture run errored": bad_fx(runs=dict({r: {"status": "complete"} for r in RUNS}, L1={"status": "error"})),
                   "a fixture check false": bad_fx(checks={"all_complete": True, "repeat_reproduces_to_the_criterion": False}),
                   "a fixture control unmet": bad_fx(controls={"wrong_seed": {"met": False}}),
                   "no fixture controls": bad_fx(controls={}),
                   "a job control unmet": dict(controls={"jobcheck_other_kind": {"met": True},
                                                         "guard_refuses_launch": {"met": False}}),
                   "no job controls": dict(controls={}),
                   "a refused guard inventory": dict(inventory={"label": "XR-PF-a1", "verdict": "REFUSED launch",
                                                                "violation": None, "guard_installed": True,
                                                                "repo_origins_outside_expect_root": 0}),
                   "an inventory of another run": dict(inventory={"label": "XR-L0-a1", "verdict": "REPOSITORY-ORIGINS-INSPECTED",
                                                                  "violation": None, "guard_installed": True,
                                                                  "repo_origins_outside_expect_root": 0})}
        for i, (why, kw) in enumerate(refused.items()):
            self.assertFalse(gate(f"r{i}", **kw), why)
        out = self.tmp / "gate-edited"
        out.mkdir()
        (out / "admission.json").write_text('{"status": "ADMITTED"}\n')
        d = write_preflight_pass({"outroot": str(out)})
        (d / "scontrol-job.txt").write_text(preflight_line() + " ")
        self.assertFalse(xa.preflight_passed({"outroot": str(out)}, runs))
        out = self.tmp / "gate-noinv"
        out.mkdir()
        (out / "admission.json").write_text('{"status": "ADMITTED"}\n')
        d = write_preflight_pass({"outroot": str(out)})
        (d / "inventory.jsonl").unlink()
        self.assertFalse(xa.preflight_passed({"outroot": str(out)}, runs))

    # ------------------------------------------------------------------ admission and release order
    def test_draft_refuses_every_prior_grants_outroot(self):
        for i, g in enumerate(load_admit().load_runs()["prior"]["grants"]):
            def mutate(root, runs, refs, i=i):
                runs["prior"]["grants"][i]["outroot"] = runs["outroot"]
            root, pc, ms = make_checkout(self.tmp, f"PO{i}", self.omni, self.flux, dict(self.refs), mutate)
            r = draft_cmd(root, pc, ms)
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn("is a prior grant's", r.stderr)
            self.assertFalse(Path(self.tmp, f"out-PO{i}").exists())

    def next_attempt(self, adm, run, sacct_text, now=None, diagnosis=None, root=None):
        psv = self.tmp / "na-sacct.psv"
        psv.write_text(sacct_text)
        cmd = [(root or self.tmp / "T") / PKG_REL / "xr_admit.py", "next-attempt", "--admission", adm, "--run", run,
               "--sacct", psv]
        return py(cmd + (["--now", now] if now else []) + (["--diagnosis", diagnosis] if diagnosis is not None else []))

    def test_next_attempt_counts_only_this_amendment_and_enforces_order_spares_and_the_stop(self):
        root, pc, ms = make_checkout(self.tmp, "T", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "T")
        real = captured(SACCT_NOW)             # the five xr_* jobs, xrr_PF_a1 and SB1's
        r = self.next_attempt(adm, "L0", real)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("no passed preflight", r.stderr)
        r = self.next_attempt(adm, "PF", real)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split()[0], "1")
        # sacct must show exactly every earlier grant's jobs
        for missing, jid in (("|xr_X0_a1|", "59648608"), ("|xrr_PF_a1|", "59655414")):
            r = self.next_attempt(adm, "PF", "".join(l + "\n" for l in real.splitlines() if missing not in l))
            self.assertEqual(r.returncode, 3)
            self.assertIn(f"missing ['{jid}']", r.stderr)
        for extra, jid in (("60000001|xr_X0_a2|PENDING\n", "60000001"), ("60000002|xrr_PF_a2|FAILED\n", "60000002")):
            r = self.next_attempt(adm, "PF", real + extra)
            self.assertEqual(r.returncode, 3)
            self.assertIn(f"unexpected ['{jid}']", r.stderr)
        # a second preflight is a spare: it needs a diagnosis
        Path(admj["outroot"], "PF", "a1").mkdir(parents=True)
        r = self.next_attempt(adm, "PF", real)
        self.assertEqual(r.returncode, 3)
        self.assertIn("--diagnosis", r.stderr)
        r = self.next_attempt(adm, "PF", real, diagnosis="node failure: NODE_FAIL in sacct")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split()[0], "2")
        Path(admj["outroot"], "PF", "a2").mkdir(parents=True)
        r = self.next_attempt(adm, "PF", real, diagnosis="again")
        self.assertEqual(r.returncode, 3)
        self.assertIn("2 preflight attempts already used of 2", r.stderr)
        shutil.rmtree(Path(admj["outroot"], "PF"))
        write_preflight_pass(admj)
        r = self.next_attempt(adm, "PF", real, diagnosis="x")
        self.assertEqual(r.returncode, 3)
        self.assertIn("already passed", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L0", real).returncode, 0)
        r = self.next_attempt(adm, "X0", real)          # L0 first
        self.assertEqual(r.returncode, 3)
        self.assertIn("L0 has no complete, comparable receipt", r.stderr)
        d = write_complete(admj, "L0", schema="xr-preflight-receipt/2", kind="preflight")
        r = self.next_attempt(adm, "X0", real)
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn("L0 has no complete, comparable receipt", r.stderr)
        shutil.rmtree(d)
        write_complete(admj, "L0")
        self.assertEqual(self.next_attempt(adm, "X0", real).returncode, 0)
        r = self.next_attempt(adm, "L0", real, diagnosis="x")
        self.assertEqual(r.returncode, 3)
        self.assertIn("no rerun", r.stderr)
        # a spare exact attempt: only with a diagnosis
        Path(admj["outroot"], "X0", "a1").mkdir(parents=True)
        r = self.next_attempt(adm, "X0", real)
        self.assertEqual(r.returncode, 3)
        self.assertIn("spare attempt needs a stated --diagnosis", r.stderr)
        r = self.next_attempt(adm, "X0", real, diagnosis="TIMEOUT at 30 h on a slow node; no receipt")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split()[0], "2")
        # caps count this amendment's xrl_* jobs only (steps and other jobs ignored)
        rows = "".join(f"{100 + i}|xrl_X{i % 2}_a{i}|FAILED\n{100 + i}.batch|batch|FAILED\n" for i in range(4))
        r = self.next_attempt(adm, "X1", real + rows)
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("attempts already used", r.stderr)
        self.assertEqual(self.next_attempt(adm, "L1", real + rows).returncode, 0)
        xa = load_admit()
        psv = self.tmp / "na-units.psv"
        psv.write_text(real + "".join(f"{200 + i}|xrl_X0_a{i}|FAILED\n" for i in range(2)) + "201|xrr_X0_a9|FAILED\n")
        _, parts = xa.attempts_by_kind(admj, xa.load_runs(), psv)
        self.assertEqual(parts["sacct"], {"exact": 2, "lgbm": 0, "preflight": 0})
        # the stop: 72 h after the first submission, which is the preflight's
        Path(admj["outroot"], "submissions.jsonl").write_text(json.dumps(
            {"run": "PF", "kind": "preflight", "attempt": 1, "job_id": int(PF_JOB),
             "submitted_utc": "2026-10-11T00:00:00Z"}) + "\n")
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

    def test_a_window_start_carried_by_a_repaired_package_is_honoured(self):
        def mutate(root, runs, refs):
            runs["window"]["first_submission_utc"] = "2026-10-10T00:00:00Z"
        root, pc, ms = make_checkout(self.tmp, "WS", self.omni, self.flux, dict(self.refs), mutate)
        adm, admj = draft(root, pc, ms, self.tmp, "WS")
        r = self.next_attempt(adm, "PF", captured(SACCT_NOW), now="2026-10-12T23:55:00Z", root=root)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.next_attempt(adm, "PF", captured(SACCT_NOW), now="2026-10-12T23:55:01Z", root=root)
        self.assertEqual(r.returncode, 3)
        self.assertIn("past the stop", r.stderr)

    def test_the_planned_cumulative_ceiling_includes_every_prior_charge(self):
        xa = load_admit()
        runs = xa.load_runs()
        root = self.tmp / "ceiling"
        root.mkdir()
        admj = {"outroot": str(root)}
        kinds = runs["kinds"]
        full = sum(k["ceiling_node_h_per_attempt"] * k["max_attempts_total"] for k in kinds.values())
        self.assertAlmostEqual(xa.planned_ceiling(admj, runs, 0.0) + full, runs["ceiling_node_h_total"], places=12)
        self.assertLessEqual(runs["ceiling_node_h_total"], runs["cap_node_h"])
        self.assertEqual(runs["prior"]["charged_node_h_recorded"], PRIOR_CHARGE)
        self.assertEqual((kinds["preflight"]["max_attempts_total"], kinds["exact"]["max_attempts_total"],
                          kinds["lgbm"]["max_attempts_total"]), (2, 4, 3))
        heavy = json.loads(json.dumps(runs))
        heavy["prior"]["charged_node_h_recorded"] = 5.0
        Path(root, "submissions.jsonl").write_text(json.dumps(
            {"run": "PF", "kind": "preflight", "attempt": 1, "job_id": int(PF_JOB), "submitted_utc": "2026-10-11T00:00:00Z"}) + "\n")
        Path(root, "admission.json").write_text(json.dumps({"stop_after_hours": 72, "outroot": str(root)}))
        write_preflight_pass({"outroot": str(root)})
        write_complete({"outroot": str(root)}, "L0")
        psv = self.tmp / "ceiling.psv"
        psv.write_text(captured(SACCT_NOW))
        xa.load_runs = lambda: heavy
        args = type("A", (), {"admission": str(root / "admission.json"), "run": "X0", "sacct": str(psv),
                              "now": "2026-10-11T00:01:00Z", "diagnosis": None})
        with self.assertRaisesRegex(xa.Refusal, "planned cumulative ceiling"):
            xa.next_attempt(args)
        heavy["prior"]["charged_node_h_recorded"] = runs["prior"]["charged_node_h_recorded"]
        self.assertEqual(xa.next_attempt(args), 0)

    # ------------------------------------------------------------------ fake Slurm: submit, job caps, ledger
    def fake_slurm(self, d, sbatch_fail_at=0, line=None):
        """sbatch/scancel/squeue stubs; scontrol prints ``line`` (a real-format line) and sacct the
        captured real ``sacct -X -n -P`` output, which lists every earlier grant's jobs."""
        d.mkdir(parents=True, exist_ok=True)
        log = d / "calls.log"
        (d / "scontrol.txt").write_text(line if line is not None else exact_line())
        (d / "sbatch").write_text(f"""#!/bin/bash
echo "sbatch $*" >> {log}
n=$(grep -c '^sbatch' {log})
[ "$n" = "{sbatch_fail_at}" ] && exit 1
echo $((1000 + n))
""")
        (d / "scancel").write_text(f"#!/bin/bash\necho \"scancel $*\" >> {log}\n")
        (d / "squeue").write_text("#!/bin/bash\nexit 0\n")
        (d / "sacct").write_text(f"#!/bin/bash\necho \"sacct $*\" >> '{log}'\ncat '{SCHED / SACCT_NOW}'\n")
        (d / "scontrol").write_text(f"#!/bin/bash\ncat '{d / 'scontrol.txt'}'\n")
        for f in ("sbatch", "scancel", "squeue", "scontrol", "sacct"):
            (d / f).chmod(0o755)
        return log

    def test_submit_releases_in_order_counts_attempts_records_diagnoses_and_cancels_on_a_failed_sbatch(self):
        root, pc, ms = make_checkout(self.tmp, "Q", self.omni, self.flux, dict(self.refs))
        adm, admj = draft(root, pc, ms, self.tmp, "Q")
        slurm = self.tmp / "slurm-ok"
        log = self.fake_slurm(slurm)
        base = {k: v for k, v in os.environ.items() if k != "XR_DIAGNOSIS"}

        def sub(*runs, diagnosis=None):
            env = dict(base, PATH=f"{slurm}:{os.environ['PATH']}")
            if diagnosis:
                env["XR_DIAGNOSIS"] = diagnosis
            return subprocess.run(["bash", root / PKG_REL / "launch/xr_submit.sh", adm, *runs],
                                  capture_output=True, text=True, env=env)
        r = sub("X0", "L0")                # nothing before the preflight
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no passed preflight", r.stderr)
        self.assertEqual(sub("PF").returncode, 0)
        r = sub("PF")                      # the second preflight is a spare: refused without a diagnosis
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--diagnosis", r.stderr)
        self.assertEqual(sub("PF", diagnosis="PF a1 TIMEOUT: CFS read stalled").returncode, 0)
        r = sub("PF", diagnosis="third")   # a third preflight: refused
        self.assertNotEqual(r.returncode, 0)
        write_preflight_pass(admj, attempt=2)
        r = sub("L0", "X0")                # L0 goes; X0 waits for L0's receipt
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("L0 has no complete", r.stderr)
        write_complete(admj, "L0")
        r = sub("X0", "X0p", "X1", "L1")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X0", diagnosis="X0 a1 NODE_FAIL")      # the one extra exact attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("X1", diagnosis="x")       # a fifth exact attempt: refused
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("attempts already used", r.stderr)
        r = sub("L1", diagnosis="L1 a1 OUT_OF_MEMORY")  # the one extra LightGBM attempt
        self.assertEqual(r.returncode, 0, r.stderr)
        r = sub("L1", diagnosis="x")
        self.assertNotEqual(r.returncode, 0)
        lines = [json.loads(l) for l in Path(admj["outroot"], "submissions.jsonl").read_text().splitlines()]
        self.assertEqual([l["run"] for l in lines], ["PF", "PF", "L0", "X0", "X0p", "X1", "L1", "X0", "L1"])
        self.assertEqual([l["diagnosis"] for l in lines][:2], [None, "PF a1 TIMEOUT: CFS read stalled"])
        self.assertEqual(lines[7]["diagnosis"], "X0 a1 NODE_FAIL")
        self.assertEqual(sum(1 for l in lines if l["kind"] == "exact"), 4)
        calls = log.read_text()
        for want in ("--job-name=xrl_PF_a1", "--job-name=xrl_PF_a2", "--time=00:05:00", "--qos=shared",
                     "--cpus-per-task=12", "--mem=22860M", "--time=30:00:00", "--cpus-per-task=64", "--time=01:00:00",
                     "--deadline=", "sacct -u", "-S 2026-10-10"):
            self.assertIn(want, calls)
        self.assertNotIn("regular", calls)
        self.assertNotIn("--job-name=xr_", calls)
        self.assertNotIn("--job-name=xrr_", calls)
        # a failure at the second sbatch cancels the first
        root2, pc2, ms2 = make_checkout(self.tmp, "Q2", self.omni, self.flux, dict(self.refs))
        adm2, admj2 = draft(root2, pc2, ms2, self.tmp, "Q2")
        write_preflight_pass(admj2)
        write_complete(admj2, "L0")
        slurm2 = self.tmp / "slurm-fail"
        log2 = self.fake_slurm(slurm2, sbatch_fail_at=2)
        env2 = dict(base, PATH=f"{slurm2}:{os.environ['PATH']}")
        r = subprocess.run(["bash", root2 / PKG_REL / "launch/xr_submit.sh", adm2, "X0", "X0p"], capture_output=True,
                           text=True, env=env2)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("scancel 1001", log2.read_text())

    def test_jobcheck_on_real_format_allocations(self):
        cases = {"ok (exact)": ("X0", exact_line(), 0), "ok (lgbm)": ("L0", lgbm_line(), 0),
                 "ok (preflight, the captured line itself)": ("PF", captured(f"scontrol-running-{PF_JOB}.txt"), 0),
                 "billing 14": ("X0", exact_line(NumCPUs="14", AllocTRES="cpu=14,mem=26670M,node=1,billing=14"), 3),
                 "billing 13 at 12 cpus": ("X0", exact_line(AllocTRES="cpu=12,mem=24765M,node=1,billing=13"), 3),
                 "regular qos": ("X0", exact_line(QOS="regular_1"), 3),
                 "time 31 h": ("X0", exact_line(TimeLimit="1-07:00:00"), 3),
                 "cpus 16": ("X0", exact_line(NumCPUs="16"), 3),
                 "the preflight's allocation for L0": ("L0", captured(f"scontrol-running-{PF_JOB}.txt"), 3),
                 "pending (null)": ("X0", scontrol_line(JobId=PF_JOB, NumCPUs="12", TimeLimit="1-06:00:00"), 3)}
        for why, (run, line, code) in cases.items():
            d = self.tmp / ("slurm-jc-" + "".join(c if c.isalnum() else "_" for c in why))
            self.fake_slurm(d, line=line)
            rec = d / "scontrol-job.txt"
            env = dict(os.environ, PATH=f"{d}:{os.environ['PATH']}", SLURM_JOB_ID=PF_JOB)
            r = subprocess.run([sys.executable, self.root / PKG_REL / "xr_admit.py", "jobcheck", "--admission", self.adm,
                                "--run", run, "--record", rec], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, code, f"{why}: {r.stdout} {r.stderr}")
            self.assertEqual(rec.read_text(), line, why)          # recorded even when refused
            if code == 0:
                self.assertEqual(r.stdout.strip(), {"X0": "12", "L0": "64", "PF": "12"}[run])

    def ledger(self, sacct_text, now, subs=None):
        out = self.tmp / f"ledger-{abs(hash((sacct_text, now)))}"
        out.mkdir()
        adm = json.loads(self.adm.read_text())
        adm["outroot"] = str(out)
        p = out / "adm-ledger.json"
        p.write_text(json.dumps(adm))
        (out / "submissions.jsonl").write_text("".join(json.dumps(s) + "\n" for s in (subs or [])))
        psv = out / "sacct.psv"
        psv.write_text(sacct_text)
        return py([self.root / PKG_REL / "xr_admit.py", "ledger", "--admission", p, "--sacct", psv, "--now", now])

    def test_ledger_is_cumulative_over_every_prior_grant_and_flags(self):
        subs = [{"run": "PF", "kind": "preflight", "attempt": 1, "job_id": 10, "submitted_utc": "2026-10-11T00:00:00Z"},
                {"run": "X0", "kind": "exact", "attempt": 1, "job_id": 11, "submitted_utc": "2026-10-11T00:10:00Z"},
                {"run": "L0", "kind": "lgbm", "attempt": 1, "job_id": 12, "submitted_utc": "2026-10-11T00:10:05Z"},
                {"run": "X1", "kind": "exact", "attempt": 1, "job_id": 13, "submitted_utc": "2026-10-11T00:10:09Z"},
                {"run": "X0p", "kind": "exact", "attempt": 1, "job_id": 14, "submitted_utc": "2026-10-11T00:10:12Z"}]
        prior = captured(LEDGER_NOW)          # real: header and the six prior jobs (energy= inside AllocTRES)
        new = ("10|xrl_PF_a1|COMPLETED|120|billing=12,cpu=12,energy=40000,mem=22860M,node=1|00:05:00\n"
               "11|xrl_X0_a1|COMPLETED|72000|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n"
               "12|xrl_L0_a1|COMPLETED|900|billing=64,cpu=64,mem=121920M,node=1|01:00:00\n"
               "13|xrl_X1_a1|RUNNING|3600|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n"
               "14|xrl_X0p_a1|CANCELLED by 112498|60|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n")
        r = self.ledger(prior + new, "2026-10-12T00:00:00Z", subs)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        led = json.loads(r.stdout)
        self.assertAlmostEqual(led["prior_charged_node_h"], PRIOR_CHARGE, places=15)
        amend = 12 / 256 * 120 / 3600 + 12 / 256 * 20 + 64 / 256 * 0.25 + 12 / 256 * 1 + 12 / 256 * 60 / 3600
        self.assertAlmostEqual(led["amendment_charged_node_h"], amend, places=12)
        self.assertAlmostEqual(led["cumulative_charged_node_h"], PRIOR_CHARGE + amend, places=12)
        self.assertAlmostEqual(led["unfinished_ceiling_node_h"], 1.40625, places=12)   # only X1 (CANCELLED is finished)
        self.assertAlmostEqual(led["hours_since_first_submission"], 24.0, places=9)
        r = self.ledger(prior + new, "2026-10-14T00:00:01Z", subs)       # past the stop with job 13 still running
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("cancel them", r.stdout)
        for why, text, flag in (
                ("a prior job missing", prior.replace("59648611|", "59648699|"), "prior job 59648611"),
                ("the recovery preflight missing", prior.replace("59655414|", "59655499|"), "prior job 59655414"),
                ("a prior charge changed", prior.replace("|xrr_PF_a1|FAILED|74|", "|xrr_PF_a1|FAILED|75|"), "differs from the recorded"),
                ("another xr_ job", prior + "59700000|xr_X0_a2|FAILED|5|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n",
                 "carries a prior prefix"),
                ("another xrr_ job", prior + "59700001|xrr_X0_a1|FAILED|5|billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n",
                 "carries a prior prefix"),
                ("an unrecorded xrl_ job", prior + "15|xrl_X0p_a2|PENDING|0||1-06:00:00\n", "not in the submissions record"),
                ("a prior job's billing unreadable", prior.replace("billing=64,cpu=64,mem=121920M,node=1|01:00:00\n59648617",
                                                                   "cpu=64,mem=121920M,node=1|01:00:00\n59648617"), "unreadable billing")):
            r = self.ledger(text + new, "2026-10-12T00:00:00Z", subs)
            self.assertEqual(r.returncode, 6, f"{why}: {r.stdout}")
            self.assertIn(flag, r.stdout, why)
        r = self.ledger(prior + new.replace("11|xrl_X0_a1|COMPLETED|72000|billing=12,cpu=12,mem=22860M,node=1|",
                                            "11|xrl_X0_a1|COMPLETED|72000||"), "2026-10-12T00:00:00Z", subs)
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("job 11 ran 72000 s with unreadable billing", r.stdout)
        r = self.ledger(prior + new.replace("billing=12,cpu=12,mem=22860M,node=1|1-06:00:00\n12",
                                            "billing=24,cpu=24,mem=45720M,node=1|1-06:00:00\n12"), "2026-10-12T00:00:00Z", subs)
        self.assertEqual(r.returncode, 6, r.stdout)
        self.assertIn("billing 24 > 12", r.stdout)

    def test_ledger_refuses_a_header_lacking_a_column_before_reading_any_row(self):
        """Review N-1 of the recovery: a header lacking State or JobName crashed (rc 1) after reading
        rows. Now any missing column exits 6 before a row is read, with a printed reason."""
        head, *rows = captured(LEDGER_NOW).splitlines()
        cols = head.split("|")
        for drop in ("JobID", "JobName", "State", "ElapsedRaw", "AllocTRES"):
            keep = [i for i, c in enumerate(cols) if c != drop]
            text = "".join("|".join(line.split("|")[i] for i in keep) + "\n" for line in [head] + rows)
            r = self.ledger(text, "2026-10-12T00:00:00Z")
            self.assertEqual(r.returncode, 6, f"{drop}: {r.stdout} {r.stderr}")
            out = json.loads(r.stdout)
            self.assertIn(f"lacks ['{drop}']", out["over"][0])
            self.assertIn("no row was read", out["over"][0])
            self.assertEqual(r.stderr, "")
        r = self.ledger("", "2026-10-12T00:00:00Z")            # an empty file
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)
        r = self.ledger(captured(SACCT_NOW), "2026-10-12T00:00:00Z")    # the headerless -n format
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)


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
        xc = load_module("xr_compare", PKG / "xr_compare.py")
        a = self.product(self.tmp / "a.root")
        import ROOT
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
        xc = load_module("xr_compare", PKG / "xr_compare.py")
        root = self.tmp / "outroot"
        (root / "X0" / "a1").mkdir(parents=True)
        adm = root / "admission.json"
        adm.write_text('{"status": "ADMITTED"}\n')
        prod = self.product(root / "X0" / "a1" / "XR-X0.root")

        def rcpt(**upd):
            r = {"schema": "xr-receipt/2", "run": "X0", "attempt": 1, "status": "complete",
                 "admission": {"path": str(adm.resolve()), "sha256": xc.sha(adm)},
                 "output": {"path": str(prod), "sha256": xc.sha(prod)}}
            r.update(upd)
            (root / "X0" / "a1" / "receipt.json").write_text(json.dumps(r))
        rcpt()
        self.assertIsNone(xc.newest_complete(root, "X0")[1])
        for why, upd in (("run", {"run": "X1"}),
                         ("admission digest", {"admission": {"path": str(adm.resolve()), "sha256": "0" * 64}}),
                         ("admission path", {"admission": {"path": str(self.tmp / "admission.json"), "sha256": xc.sha(adm)}}),
                         ("output digest", {"output": {"path": str(prod), "sha256": "0" * 64}}),
                         ("a preflight receipt", {"schema": "xr-preflight-receipt/2", "kind": "preflight"}),
                         ("no schema", {"schema": None})):
            rcpt(**upd)
            new, err = xc.newest_complete(root, "X0")
            self.assertIsNone(new, why)
            self.assertTrue(err, why)


class Scheduler(unittest.TestCase):
    """The allocation and sacct parsers on captured real Perlmutter output (tests/scheduler/)."""

    @classmethod
    def setUpClass(cls):
        cls.xa = load_admit()
        cls.runs = cls.xa.load_runs()

    def test_the_captured_formats_have_AllocTRES_and_no_TRES_field(self):
        for name in (f"scontrol-pending-{PENDING_JOB}.txt", "scontrol-pending-59645305.txt",
                     f"scontrol-running-{PF_JOB}.txt"):
            line = captured(name)
            self.assertIsNone(re.search(r"(^|\s)TRES=", line), name)
            self.assertIsNotNone(self.xa.parse_billing(self.xa.scontrol_field(line, "ReqTRES")))
            self.assertIn("SubmitLine=sbatch ", line)      # free text with spaces after the fields
        self.assertEqual(self.xa.scontrol_field(captured(f"scontrol-pending-{PENDING_JOB}.txt"), "AllocTRES"), "(null)")

    def test_the_captured_running_line_is_the_preflight_kind_and_no_other(self):
        line = captured(f"scontrol-running-{PF_JOB}.txt")
        got = self.xa.check_allocation(line, self.runs["kinds"]["preflight"], PF_JOB)
        self.assertEqual((got["billing"], got["NumCPUs"], got["TimeLimit"], got["QOS"]), (12, "12", "00:05:00", "shared"))
        with self.assertRaises(self.xa.Refusal):
            self.xa.check_allocation(line, self.runs["kinds"]["lgbm"], PF_JOB)
        with self.assertRaises(self.xa.Refusal):
            self.xa.check_allocation(line, self.runs["kinds"]["preflight"], "59645305")

    def test_billing_is_read_from_AllocTRES_explicitly(self):
        xa, lgbm = self.xa, self.runs["kinds"]["lgbm"]
        ok = lgbm_line()
        self.assertEqual(xa.check_allocation(ok, lgbm, PF_JOB)["billing"], 64)
        old = dict(tok.split("=", 1) for tok in ok.split() if "=" in tok).get("TRES", "")
        self.assertIsNone(xa.parse_billing(old))
        refuse = {
            "pending (null)": scontrol_line(JobId=PF_JOB, NumCPUs="64", TimeLimit="01:00:00"),
            "billing over the cap": lgbm_line(AllocTRES="cpu=64,mem=121920M,node=1,billing=65"),
            "no billing": lgbm_line(AllocTRES="cpu=64,mem=121920M,node=1"),
            "billing not a number": lgbm_line(AllocTRES="cpu=64,mem=121920M,node=1,billing=6x4"),
            "empty billing": lgbm_line(AllocTRES="cpu=64,mem=121920M,node=1,billing="),
            "billing twice": lgbm_line(AllocTRES="billing=1,cpu=64,mem=121920M,node=1,billing=64"),
            "empty AllocTRES": lgbm_line(AllocTRES=""),
            "AllocTRES absent": re.sub(r" AllocTRES=\S*", "", ok),
            "AllocTRES twice (SubmitLine)": ok.replace("SubmitLine=sbatch ", "SubmitLine=sbatch AllocTRES=billing=1 "),
            "QOS twice": ok.replace("SubmitLine=sbatch ", "SubmitLine=sbatch QOS=shared "),
            "another job": lgbm_line(JobId="59645305"),
            "unlimited time": lgbm_line(TimeLimit="UNLIMITED"),
            "64 CPUs over 1 h": lgbm_line(TimeLimit="01:00:01"),
            "empty output": "",
            "the old fixture's format": f"JobId={PF_JOB} QOS=shared NumCPUs=64 TimeLimit=00:40:00 TRES=cpu=64,billing=64",
        }
        for why, line in refuse.items():
            with self.assertRaises(xa.Refusal, msg=why):
                xa.check_allocation(line, lgbm, PF_JOB)
        with self.assertRaisesRegex(xa.Refusal, "AllocTRES appears 2 times"):
            xa.check_allocation(refuse["AllocTRES twice (SubmitLine)"], lgbm, PF_JOB)
        with self.assertRaisesRegex(xa.Refusal, "AllocTRES appears 0 times"):
            xa.check_allocation(refuse["AllocTRES absent"], lgbm, PF_JOB)
        self.assertEqual(xa.check_allocation(exact_line(), self.runs["kinds"]["exact"], PF_JOB)["billing"], 12)
        with self.assertRaises(xa.Refusal):
            xa.check_allocation(running_line(TimeLimit="00:05:01"), self.runs["kinds"]["preflight"], PF_JOB)

    def test_the_sacct_parsers_on_captured_output(self):
        xa = self.xa
        rows = xa.sacct_jobs(SCHED / SACCT_NOW, "xr")
        self.assertEqual(sorted((j["job_id"], j["run"], j["state"]) for j in rows),
                         [("59648608", "X0", "FAILED"), ("59648610", "X0p", "FAILED"), ("59648611", "X1", "FAILED"),
                          ("59648616", "L0", "FAILED"), ("59648617", "L1", "FAILED")])
        self.assertEqual([(j["job_id"], j["run"]) for j in xa.sacct_jobs(SCHED / SACCT_NOW, "xrr")], [("59655414", "PF")])
        self.assertEqual(xa.sacct_jobs(SCHED / SACCT_NOW, "xrl"), [])
        self.assertEqual(sorted(j["job_id"] for j in xa.sacct_jobs(SCHED / "sacct-steps-P.psv", "xr")),
                         ["59648608", "59648616"])                 # header and .batch/.extern steps excluded
        xa.check_prior(self.runs, SCHED / SACCT_NOW)
        with self.assertRaises(xa.Refusal):
            xa.check_prior(self.runs, SCHED / "sacct-X-n-P.psv")   # captured before the recovery preflight
        self.assertIsNone(xa.parse_billing("cpu=12,mem=22860M,node=1"))      # a step's AllocTRES
        head, *lines = captured(LEDGER_NOW).splitlines()
        total = sum(xa.charge(dict(zip(head.split("|"), line.split("|"))))[0] for line in lines)
        self.assertAlmostEqual(total, self.runs["prior"]["charged_node_h_recorded"], places=15)
        self.assertEqual(round(total * 921600), 2132)
        want = {j: r for g in self.runs["prior"]["grants"] for j, r in g["jobs"].items()}
        self.assertEqual({l.split("|")[0]: l.split("|")[1].split("_", 1)[1].rsplit("_a", 1)[0] for l in lines}, want)

    def test_other_real_states_and_allocation_shapes(self):
        """Rows selected by state from this account's history: CANCELLED by <uid> (with and without an
        allocation), TIMEOUT, array ids, PREEMPTED, gres items and a JobName holding '=' and '/'."""
        xa = self.xa
        head, *lines = captured("sacct-states-20261011.psv").splitlines()
        rows = [dict(zip(head.split("|"), l.split("|"))) for l in lines]
        self.assertEqual(len(rows), 7)
        got = [(r["State"].split()[0], xa.charge(r)[1], xa.charge(r)[2]) for r in rows]
        self.assertEqual(got, [("CANCELLED", 256, 8130), ("TIMEOUT", 128, 1804), ("TIMEOUT", 32, 36022),
                               ("FAILED", 64, 2334), ("PREEMPTED", 128, 12694), ("CANCELLED", None, 0),
                               ("CANCELLED", None, 0)])
        self.assertTrue(all(r["State"].split()[0] in xa.FINISHED for r in rows))
        self.assertEqual(xa.seconds("1-06:00:00"), 108000)
        self.assertEqual(xa.seconds("00:05:00"), 300)
        self.assertEqual(xa.sacct_jobs(SCHED / "sacct-states-20261011.psv", "xrl"), [])


class Units(unittest.TestCase):
    """xr_run's thread plan, launch window, fit recorder and record parsers, in this process."""

    @classmethod
    def setUpClass(cls):
        cls.xr = load_run()

    def test_the_run_path_has_no_child_launching_inspection(self):
        """threadpoolctl.threadpool_info() reached ldconfig through ctypes.util.find_library on
        Linux; loky's cache was seeded by hand. Neither may come back: find_library appears only in
        the deliberate launch control, and nothing writes loky's private cache."""
        import ast
        src = (PKG / "xr_run.py").read_text()
        tree = ast.parse(src)
        self.assertNotIn("threadpool_info", src)
        self.assertNotIn("physical_cores_cache", src)
        owners = []
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef):
                for n in ast.walk(fn):
                    if isinstance(n, ast.Attribute) and n.attr == "find_library":
                        owners.append(fn.name)
        self.assertEqual(set(owners), {"launch_controls"})

    def test_both_paths_refuse_on_a_recorded_launch(self):
        """The run path and the preflight both end their window with require_no_launch, so a launch a
        library swallowed (loky) still refuses the run."""
        import ast
        tree = ast.parse((PKG / "xr_run.py").read_text())
        calls = {fn.name: [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "require_no_launch"]
                 for fn in tree.body if isinstance(fn, ast.FunctionDef)}
        self.assertEqual(len(calls["main"]), 1)
        self.assertEqual(len(calls["preflight"]), 1)

    def test_the_launch_window_refuses_and_records_then_restores(self):
        import subprocess as sp
        before = (sp.Popen, os.system, os.posix_spawn, os.execv, os.fork)
        with self.xr.LaunchSpy() as spy:
            for call in (lambda: sp.run(["true"]), lambda: os.system("true"), lambda: sp.check_output(["true"]),
                         lambda: os.posix_spawn("/usr/bin/true", ["true"], {})):
                with self.assertRaises(self.xr.LaunchRefusal):
                    call()
            with self.xr.LaunchSpy() as inner:            # nested: the inner spy refuses first, the outer sees nothing
                with self.assertRaises(self.xr.LaunchRefusal):
                    sp.run(["true"])
            self.assertEqual(len(inner.calls), 1)
        self.assertEqual(len(spy.calls), 4)
        self.assertEqual((sp.Popen, os.system, os.posix_spawn, os.execv, os.fork), before)
        self.assertEqual(sp.run(["true"]).returncode, 0)
        with self.assertRaises(self.xr.LaunchRefusal):
            self.xr.require_no_launch(spy)
        self.xr.require_no_launch(self.xr.LaunchSpy())

    def test_a_launch_a_library_swallows_is_still_recorded(self):
        """loky catches a failed physical-core query and falls back; the window must still see it."""
        from joblib.externals.loky.backend import context as loky_context
        with self.xr.LaunchSpy() as spy:
            n, exc = (None, None)
            try:
                n = (loky_context._count_physical_cores_linux() if sys.platform.startswith("linux")
                     else loky_context._count_physical_cores_darwin())
            except self.xr.LaunchRefusal as e:
                exc = e
        self.assertTrue(spy.calls)
        with self.assertRaises(self.xr.LaunchRefusal):
            self.xr.require_no_launch(spy)

    def test_launch_controls_are_unmet_when_a_probe_launches_nothing(self):
        import ctypes.util
        from joblib.externals.loky.backend import context as loky_context
        self.assertTrue(self.xr.launch_controls()["met"])
        saved = (loky_context._count_physical_cores_linux, loky_context._count_physical_cores_darwin, ctypes.util.find_library)
        try:
            loky_context._count_physical_cores_linux = loky_context._count_physical_cores_darwin = lambda: 8
            ctypes.util.find_library = lambda name: None
            res = self.xr.launch_controls()
        finally:
            loky_context._count_physical_cores_linux, loky_context._count_physical_cores_darwin, ctypes.util.find_library = saved
        self.assertFalse(res["met"])
        self.assertEqual(res["probes"]["loky_physical_cores"], {"outcome": "returned", "launches": []})

    def plan(self, platform, affinity, os_count, env, kind=None, joblib_count=None):
        kind = kind or {"cpus_per_task": 64, "omp_threads": 64}
        xr = self.xr
        saved = (sys.platform, os.cpu_count, getattr(os, "sched_getaffinity", None), dict(os.environ))
        import joblib
        saved_cc = joblib.cpu_count
        try:
            sys.platform = platform
            os.cpu_count = lambda: os_count
            os.sched_getaffinity = lambda pid: set(range(affinity))
            joblib.cpu_count = lambda only_physical_cores=False: (min(affinity, os_count) if joblib_count is None
                                                                  else joblib_count)
            for k in ("LOKY_MAX_CPU_COUNT", "OMP_NUM_THREADS"):
                os.environ.pop(k, None)
            os.environ.update(env)
            return xr.thread_plan(kind)
        finally:
            sys.platform, os.cpu_count = saved[0], saved[1]
            if saved[2] is None:
                del os.sched_getaffinity
            else:
                os.sched_getaffinity = saved[2]
            os.environ.clear()
            os.environ.update(saved[3])
            joblib.cpu_count = saved_cc

    def test_the_linux_thread_plan(self):
        ok = self.plan("linux", 64, 256, {"OMP_NUM_THREADS": "64"})
        self.assertEqual((ok["lgbm_num_threads"], ok["affinity"], ok["os_cpu_count"]), (64, 64, 256))
        self.assertEqual(ok["exact_estimator_threads"], 1)
        for why, args, text in (
                ("full node: joblib would ask lscpu", ("linux", 64, 64, {"OMP_NUM_THREADS": "64"}), "not below the node"),
                ("affinity other than the kind", ("linux", 32, 256, {"OMP_NUM_THREADS": "64"}), "differs from the kind"),
                ("LOKY_MAX_CPU_COUNT set", ("linux", 64, 256, {"OMP_NUM_THREADS": "64", "LOKY_MAX_CPU_COUNT": "64"}), "is set"),
                ("OMP other than the kind", ("linux", 64, 256, {"OMP_NUM_THREADS": "128"}), "OMP_NUM_THREADS")):
            with self.assertRaisesRegex(self.xr.BackendRefusal, text, msg=why):
                self.plan(*args)
        with self.assertRaisesRegex(self.xr.BackendRefusal, "joblib resolves 63"):   # e.g. a cgroup quota
            self.plan("linux", 64, 256, {"OMP_NUM_THREADS": "64"}, joblib_count=63)

    def test_maps_parsing(self):
        text = ("7f00-7f01 r-xp 00000000 00:2f 1 /opt/conda/lib/libgomp.so.1.0.0\n"
                "7f01-7f02 r--p 00001000 00:2f 1 /opt/conda/lib/libgomp.so.1.0.0\n"
                "7f02-7f03 r-xp 00000000 00:2f 2 /opt/conda/lib/python3.11/site-packages/lightgbm/lib/lib_lightgbm.so\n"
                "7f03-7f04 rw-p 00000000 00:00 0 \n"
                "7f04-7f05 r-xp 00000000 00:2f 3 /opt/conda/lib/libopenblasp-r0.3.27.so (deleted)\n"
                "7ffd-7ffe rw-p 00000000 00:00 0 [stack]\n")
        self.assertEqual(self.xr.loaded_libraries(text),
                         ["/opt/conda/lib/libgomp.so.1.0.0", "/opt/conda/lib/libopenblasp-r0.3.27.so (deleted)",
                          "/opt/conda/lib/python3.11/site-packages/lightgbm/lib/lib_lightgbm.so"])

    def recorder(self, backend, threads):
        rec = self.xr.FitRecorder(backend, threads)
        rec.install()
        return rec

    def test_the_lightgbm_thread_count_is_checked_at_fit_after_fit_and_at_predict(self):
        import numpy as np
        import lightgbm
        backend = {"estimator": "lgbm", "random_state": {"step1": 42, "step2": 43, "regressor": 44}, "iterations": 5}
        X = np.random.default_rng(1).normal(size=(200, 2))
        y = (X[:, 0] > 0).astype(int)
        orig = (lightgbm.LGBMClassifier.fit, lightgbm.sklearn.LGBMModel.predict)
        saved = os.environ.get("LOKY_MAX_CPU_COUNT")
        os.environ["LOKY_MAX_CPU_COUNT"] = "1"
        try:
            rec = self.recorder(backend, 1)
            try:
                est = lightgbm.LGBMClassifier(n_estimators=3, random_state=42, verbose=-1).fit(X, y)
                est.predict_proba(X)
            finally:
                rec.uninstall()
            self.assertEqual(rec.fits[0]["num_threads"], 1)
            self.assertEqual(rec.predicts, {"calls": 1, "num_threads": [1]})
            rec = self.recorder(backend, 2)                 # the plan says 2; LightGBM resolves 1
            try:
                with self.assertRaisesRegex(self.xr.BackendRefusal, "would train on 1 threads"):
                    lightgbm.LGBMClassifier(n_estimators=3, random_state=42, verbose=-1).fit(X, y)
            finally:
                rec.uninstall()
            self.assertEqual(rec.fits, [])
            rec = self.recorder(backend, 1)                 # an alias overrides n_jobs: caught after the fit
            try:
                with self.assertRaisesRegex(self.xr.BackendRefusal, "trained with num_threads=2"):
                    lightgbm.LGBMClassifier(n_estimators=3, random_state=42, verbose=-1, num_threads=2).fit(X, y)
            finally:
                rec.uninstall()
            est = lightgbm.LGBMClassifier(n_estimators=3, random_state=42, verbose=-1).fit(X, y)
            rec = self.recorder(backend, 2)                 # a prediction on another count than the plan
            try:
                with self.assertRaisesRegex(self.xr.BackendRefusal, "predict would run on 1 threads"):
                    est.predict_proba(X)
            finally:
                rec.uninstall()
        finally:
            if saved is None:
                os.environ.pop("LOKY_MAX_CPU_COUNT", None)
            else:
                os.environ["LOKY_MAX_CPU_COUNT"] = saved
        self.assertEqual((lightgbm.LGBMClassifier.fit, lightgbm.sklearn.LGBMModel.predict), orig)

    def test_uninstall_restores_every_class_so_runs_can_follow_in_one_process(self):
        import sklearn.ensemble as ske
        import lightgbm
        classes = (ske.GradientBoostingClassifier, ske.GradientBoostingRegressor, lightgbm.LGBMClassifier,
                   lightgbm.LGBMRegressor, lightgbm.sklearn.LGBMModel)
        before = [(c, c.__dict__.get("fit"), c.__dict__.get("predict")) for c in classes]
        backend = {"estimator": "exact", "random_state": {"step1": None, "step2": None, "regressor": None}, "iterations": 5}
        for _ in range(2):
            rec = self.recorder(backend, 1)
            self.assertTrue(hasattr(ske.GradientBoostingClassifier.fit, "__xr_wrapped__"))
            rec.uninstall()
        self.assertEqual([(c, c.__dict__.get("fit"), c.__dict__.get("predict")) for c in classes], before)
        self.assertFalse(hasattr(ske.GradientBoostingClassifier.fit, "__xr_wrapped__"))

    def test_the_regressor_must_fit_every_iteration(self):
        backend = {"estimator": "exact", "random_state": {"step1": None, "step2": None, "regressor": None},
                   "iterations": 5}
        for n_reg, ok in ((5, True), (0, False), (4, False), (6, False)):
            rec = self.xr.FitRecorder(backend, 1)
            rec.fits = [{"class": "GradientBoostingClassifier"}] * 10 + [{"class": "GradientBoostingRegressor"}] * n_reg
            if ok:
                self.assertEqual(rec.verify_counts(), {"classifier_fits": 10, "regressor_fits": 5})
            else:
                with self.assertRaises(self.xr.BackendRefusal):
                    rec.verify_counts()

    def test_lightgbm_runs_must_have_predicted_on_the_plan(self):
        backend = {"estimator": "lgbm", "random_state": {"step1": 1, "step2": 2, "regressor": 3}, "iterations": 5}
        fits = [{"class": "LGBMClassifier"}] * 10 + [{"class": "LGBMRegressor"}] * 5
        for predicts, ok in (({"calls": 3, "num_threads": [64]}, True), ({"calls": 0, "num_threads": []}, False),
                             ({"calls": 3, "num_threads": [64, 32]}, False)):
            rec = self.xr.FitRecorder(backend, 64)
            rec.fits, rec.predicts = list(fits), predicts
            if ok:
                rec.verify_counts()
            else:
                with self.assertRaises(self.xr.BackendRefusal):
                    rec.verify_counts()

    def test_fit_sequence(self):
        b = {"estimator": "lgbm", "random_state": {"step1": 1, "step2": 2, "regressor": 3}, "iterations": 2}
        good = [{"class": c, "random_state": s} for c, s in (("LGBMClassifier", 1), ("LGBMRegressor", 3), ("LGBMClassifier", 2)) * 2]
        self.assertTrue(self.xr.fit_sequence(good, b))
        self.assertFalse(self.xr.fit_sequence(good[:-1], b))
        swapped = copy.deepcopy(good)
        swapped[0]["random_state"], swapped[2]["random_state"] = 2, 1
        self.assertFalse(self.xr.fit_sequence(swapped, b))


if __name__ == "__main__":
    unittest.main()
