"""Tests of RS1-BINDING-2 addendum A1: the staging of a fresh root by digest, the plan, and the resume wrapper's
teardown guard, each in the direction it acts and the other.

Run: python3 -B nd-unfolding/tests/test_rs1_a1.py (no LightGBM, no ROOT). The job-script tests run sbatch_rs1_a1.sh on a
stand-in deploy whose runner writes an RS1-named product and sidecar per pair and can fail before writing, crash after
writing once, or crash every time.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import rounding_mechanism_analyze as rma  # noqa: E402
import rs1_a1_plan as a1  # noqa: E402

PLAN = Path(os.environ.get("RS1_A1_PLAN", str(ND / "rs1_a1_plan.py")))   # the mutation harness's copy
SBATCH = Path(os.environ.get("RS1_A1_SBATCH", str(ND / "sbatch_rs1_a1.sh")))


def line(tid, arm, pairs, root, flags=()):
    argv = ["run", "--arm", arm, "--", "--npz", "/n", f"--pairs={pairs}", "--tag", f"rs1_{arm}",
            "--out", str(root / "runs" / arm), *flags]
    return "\t".join([tid, str(len(pairs.split(","))), "runner.py", *argv])


def write_queue(path, rows):
    path.write_text("\n".join(["# id\tunfolds\tscript\targv", *rows]) + "\n")


def product(path, value=1.0):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, xsec_flat=np.full(3, value), xtrue_flat=np.ones(3))
    path.with_name(path.name[:-4] + ".trace.json.gz").write_bytes(b"side" + str(value).encode())


def sums(root, rels):
    return "\n".join(f"{a1.sha256_path(root / r)}  {r}" for r in rels) + "\n"


class Expect(unittest.TestCase):
    def test_each_pair_names_its_product_and_sidecar(self):
        got = a1.expected(line("t", "A0", "-:-,-:0,-:3", Path("/R")).split("\t")[3:])
        self.assertEqual([p.name for p in got], ["rs1_A0_b-_j-.npz", "rs1_A0_b-_j-.trace.json.gz", "rs1_A0_b-_j0.npz",
                                                 "rs1_A0_b-_j0.trace.json.gz", "rs1_A0_b-_j3.npz",
                                                 "rs1_A0_b-_j3.trace.json.gz"])
        self.assertTrue(all(p.parent == Path("/R/runs/A0") for p in got))

    def test_a_line_without_one_pairs_or_tag_is_refused(self):
        with self.assertRaises(a1.Refusal):
            a1.expected(["run", "--", "--tag", "t", "--out", "/o"])
        with self.assertRaises(a1.Refusal):
            a1.expected(["run", "--", "--pairs=-:1", "--tag", "t", "--tag", "u", "--out", "/o"])

    def test_the_real_rs1_queue_names_what_the_dry_run_pinned(self):
        """The 9 dry tasks of #891's queue name exactly the 18 files its log-dry/SHA256SUMS pins."""
        rec = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106/receipts/dry"
        if not rec.is_dir():
            self.skipTest("the dry receipt is not in this tree")
        root = Path("/pscratch/sd/j/josephrb/rs1-20261106")
        names = set()
        for tid, argv in a1.read_queue(rec / "dry.tsv"):
            names |= {str(p.relative_to(root)) for p in a1.expected(argv)}
        self.assertEqual(names, set(a1.read_sums(rec / "log-dry" / "SHA256SUMS")))


class Stage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.old, self.new = t / "old", t / "new"
        self.new.mkdir()
        rows_old = [line("d0", "A0", "-:0", self.old), line("f1", "V", "-:1,-:2", self.old),
                    line("f2", "V", "-:3", self.old), line("f3", "V", "-:4", self.old), line("f4", "B63", "-:5", self.old)]
        self.rows_new = [r.replace(str(self.old), str(self.new)) for r in rows_old]
        write_queue(self.new / "queue.tsv", self.rows_new)
        write_queue(self.new / "dry.tsv", self.rows_new[:1])
        for r in ("runs/A0/rs1_A0_b-_j0.npz", "runs/V/rs1_V_b-_j1.npz", "runs/V/rs1_V_b-_j2.npz", "runs/V/rs1_V_b-_j3.npz",
                  "runs/V/rs1_V_b-_j4.npz"):
            product(self.old / r)
        (self.old / "log-dry").mkdir()
        (self.old / "log-dry" / "DONE").write_text(json.dumps({"pin": "p" * 40}))
        (self.old / "log-dry" / "d0.end").write_text("1")
        dry_files = ["runs/A0/rs1_A0_b-_j0.npz", "runs/A0/rs1_A0_b-_j0.trace.json.gz"]
        (self.old / "log-dry" / "SHA256SUMS").write_text(sums(self.old, dry_files))
        (self.old / "log-full").mkdir()
        for tid in ("d0", "f1", "f3"):        # f2 never ended (the crashed task); f4 never started
            (self.old / "log-full" / f"{tid}.end").write_text("1")
        full = dry_files + [f"runs/V/rs1_V_b-_j{j}{x}" for j in (1, 2, 3, 4) for x in (".npz", ".trace.json.gz")]
        (self.old / "log-full" / "SHA256SUMS").write_text(sums(self.old, full))

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self):
        return {l.split("\t")[0]: l.split("\t")[1:] for l in (self.new / "plan.tsv").read_text().splitlines()
                if l and not l.startswith("#")}

    def test_verified_tasks_are_copied_and_the_rest_are_todo(self):
        out = a1.stage(self.old, self.new)
        p = self.plan()
        self.assertEqual({k: v[0] for k, v in p.items()}, {"d0": "done", "f1": "done", "f2": "todo", "f3": "done",
                                                           "f4": "todo"})
        self.assertEqual(out["todo"], ["f2", "f4"])
        for r in ("runs/A0/rs1_A0_b-_j0.npz", "runs/V/rs1_V_b-_j2.trace.json.gz", "runs/V/rs1_V_b-_j4.npz"):
            self.assertEqual(a1.sha256_path(self.new / r), a1.sha256_path(self.old / r))
        self.assertEqual(a1.verify(self.new), [])

    def test_an_unended_tasks_files_go_to_runs_attempt1_never_to_runs(self):
        """The director's ruling 4: the crashed task is recomputed; its old files are for the comparison only."""
        a1.stage(self.old, self.new)
        self.assertFalse((self.new / "runs" / "V" / "rs1_V_b-_j3.npz").exists())
        self.assertTrue((self.new / "runs-attempt1" / "f2" / "rs1_V_b-_j3.npz").exists())
        self.assertTrue((self.new / "runs-attempt1" / "f2" / "rs1_V_b-_j3.trace.json.gz").exists())

    def test_an_ended_task_whose_file_does_not_verify_is_todo_and_not_copied(self):
        product(self.old / "runs/V/rs1_V_b-_j4.npz", value=9.0)        # changed after attempt 1 pinned it
        a1.stage(self.old, self.new)
        self.assertEqual(self.plan()["f3"][0], "todo")
        self.assertFalse((self.new / "runs" / "V" / "rs1_V_b-_j4.npz").exists())

    def test_a_missing_sidecar_makes_a_task_todo(self):
        (self.old / "runs/V/rs1_V_b-_j2.trace.json.gz").unlink()
        a1.stage(self.old, self.new)
        self.assertEqual(self.plan()["f1"][0], "todo")

    def test_log_dry_is_copied_verbatim_and_staging_is_once_only(self):
        a1.stage(self.old, self.new)
        for f in (self.old / "log-dry").iterdir():
            self.assertEqual(a1.sha256_path(f), a1.sha256_path(self.new / "log-dry" / f.name))
        with self.assertRaises(a1.Refusal):
            a1.stage(self.old, self.new)

    def test_a_dry_run_that_left_failed_is_refused(self):
        (self.old / "log-dry" / "FAILED").write_text("rc=1")
        with self.assertRaises(a1.Refusal):
            a1.stage(self.old, self.new)

    def test_verify_finds_a_changed_copy(self):
        a1.stage(self.old, self.new)
        (self.new / "runs" / "V" / "rs1_V_b-_j1.npz").write_bytes(b"x")
        self.assertEqual(a1.verify(self.new), ["runs/V/rs1_V_b-_j1.npz"])

    def test_a_bad_copy_is_refused(self):
        """Audit W01: the copy is re-hashed against attempt 1's line, so a bad copy never reaches copies.sha256."""
        orig = a1.copy_noatime

        def bad(src, dst):
            orig(src, dst)
            with open(dst, "ab") as fh:
                fh.write(b"x")
        a1.copy_noatime = bad
        try:
            with self.assertRaises(a1.Refusal) as cm:
                a1.stage(self.old, self.new)
        finally:
            a1.copy_noatime = orig
        self.assertIn("does not match its line", str(cm.exception))

    def test_a_bad_log_dry_copy_is_refused(self):
        """Audit W02."""
        orig = a1.shutil.copytree

        def bad(src, dst, *a, **kw):
            out = orig(src, dst, *a, **kw)
            with open(Path(dst) / "DONE", "a") as fh:
                fh.write(" ")
            return out
        a1.shutil.copytree = bad
        try:
            with self.assertRaises(a1.Refusal) as cm:
                a1.stage(self.old, self.new)
        finally:
            a1.shutil.copytree = orig
        self.assertIn("log-dry copy", str(cm.exception))

    def test_a_dry_task_is_judged_against_log_dry(self):
        """Audit W03: a dry task needs log-dry's end and SHA256SUMS, not log-full's."""
        (self.old / "log-full" / "d0.end").unlink()
        full = [l for l in (self.old / "log-full" / "SHA256SUMS").read_text().splitlines() if "rs1_A0_b-_j0" not in l]
        (self.old / "log-full" / "SHA256SUMS").write_text("\n".join(full) + "\n")
        a1.stage(self.old, self.new)
        self.assertEqual(self.plan()["d0"][0], "done")

    def test_attempt_ones_dry_done_is_required(self):
        """Audit W07."""
        (self.old / "log-dry" / "DONE").unlink()
        with self.assertRaises(a1.Refusal) as cm:
            a1.stage(self.old, self.new)
        self.assertIn("missing", str(cm.exception))

    def test_a_dry_run_that_left_stop_is_refused(self):
        """Audit W10."""
        (self.old / "log-dry" / "STOP").write_text("x")
        with self.assertRaises(a1.Refusal):
            a1.stage(self.old, self.new)

    def test_a_file_missing_from_sha256sums_makes_a_task_todo(self):
        """Audit W11: the line-absent direction of 'every file matches its line'."""
        full = [l for l in (self.old / "log-full" / "SHA256SUMS").read_text().splitlines() if "rs1_V_b-_j1.npz" not in l]
        (self.old / "log-full" / "SHA256SUMS").write_text("\n".join(full) + "\n")
        a1.stage(self.old, self.new)
        self.assertEqual(self.plan()["f1"][0], "todo")

    def test_the_bound_analysis_accepts_the_fresh_roots_receipts(self):
        """rounding_mechanism_analyze.receipt_problem: dry and full DONE at the same pin, no FAILED beside them."""
        a1.stage(self.old, self.new)
        (self.new / "log-full").mkdir()
        (self.new / "log-full" / "DONE").write_text(json.dumps({"pin": "p" * 40}))
        self.assertIsNone(rma.receipt_problem(self.new / "runs"))


RUNNER = (
    "import sys, pathlib, numpy as np\n"
    "rest = sys.argv[sys.argv.index('--') + 1:]\n"
    "out = pathlib.Path(rest[rest.index('--out') + 1]); tag = rest[rest.index('--tag') + 1]\n"
    "pairs = [t.split('=', 1)[1] for t in rest if t.startswith('--pairs=')][0].split(',')\n"
    "if 'SLOW' in rest: __import__('time').sleep(1.5)\n"
    "if 'FAIL' in rest: sys.exit(3)\n"
    "if 'KILLTASK' in rest:\n"
    "    import os, signal, subprocess\n"
    "    gp = int(subprocess.run(['ps', '-o', 'ppid=', '-p', str(os.getppid())], capture_output=True, text=True).stdout)\n"
    "    os.kill(gp, signal.SIGKILL); sys.exit(0)\n"
    "if 'DROPEND' in rest:\n"
    "    import os, time; e = pathlib.Path(os.environ['L']) / 'b.end'\n"
    "    for _ in range(100):\n"
    "        if e.exists(): e.unlink(); break\n"
    "        time.sleep(0.05)\n"
    "out.mkdir(parents=True, exist_ok=True)\n"
    "for item in pairs:\n"
    "    b, j = item.split(':'); p = out / f'{tag}_b{b}_j{j}.npz'\n"
    "    if p.exists(): continue\n"
    "    np.savez(p, xsec_flat=np.arange(3.0), xtrue_flat=np.ones(3))\n"
    "    p.with_name(p.name[:-4] + '.trace.json.gz').write_bytes(b'side')\n"
    "mark = out / ('crashed-' + tag + pairs[0].replace(':', '_'))\n"
    "if 'CRASH2' in rest: sys.exit(129)\n"
    "if 'CRASH' in rest and not mark.exists(): mark.write_text('1'); sys.exit(129)\n")


def git_repo(path, files):
    path.mkdir(parents=True)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_text(text)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "d"], check=True)
    return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


class JobScript(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.stub = t / "stub"
        self.stub.mkdir()
        (self.stub / "lightgbm.py").write_text("__version__ = 'stub'\n")
        (self.stub / "scipy.py").write_text("")
        self.D, self.A1, self.OUT = t / "deploy", t / "a1", t / "root"
        # The sourced environment puts its own python3 first on PATH, as the real setup_salloc_env.sh puts root_6_28's;
        # this one records each call, so a test can tell which interpreter ran it.
        self.envbin, self.calls = t / "envbin", t / "env-python-calls.txt"
        self.envbin.mkdir()
        (self.envbin / "python3").write_text(f'#!/bin/bash\necho "$*" >> {self.calls}\nexec {sys.executable} "$@"\n')
        (self.envbin / "python3").chmod(0o755)
        # The "system" python3 the job starts with: it refuses the planner, as the cluster's 3.6 did, so any planner
        # call made before the environment is sourced fails.
        self.sysbin = t / "sysbin"
        self.sysbin.mkdir()
        (self.sysbin / "python3").write_text(
            '#!/bin/bash\ncase "$*" in *rs1_a1_plan.py*) echo "system python3: the planner is not supported" >&2; exit 99;; esac\n'
            f'exec {sys.executable} "$@"\n')
        (self.sysbin / "python3").chmod(0o755)
        self.pin = git_repo(self.D, {"nd-unfolding/runner.py": RUNNER,
                                     "setup_salloc_env.sh": f"export PYTHONPATH={self.stub}\nexport PATH={self.envbin}:$PATH\n"})
        self.a1pin = git_repo(self.A1, {"nd-unfolding/rs1_a1_plan.py": PLAN.read_text()})
        self.OUT.mkdir()
        (self.OUT / "log-dry").mkdir()
        (self.OUT / "log-dry" / "DONE").write_text(json.dumps({"pin": self.pin}))
        (self.OUT / "copies.sha256").write_text("\n")
        self.time = t / "time.sh"
        self.time.write_text('#!/bin/bash\nshift 3\nexec "$@"\n')
        self.time.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def setup_plan(self, rows):
        """rows: (id, status, arm, pairs, flags)."""
        write_queue(self.OUT / "queue.tsv", [line(i, a, p, self.OUT, f) for i, _, a, p, f in rows])
        (self.OUT / "plan.tsv").write_text("# id\tstatus\tsource\n" + "\n".join(f"{i}\t{s}\tx" for i, s, *_ in rows) + "\n")

    def job(self, pin=None, a1pin=None):
        env = dict(os.environ, RS1_TIME_BIN=str(self.time), PATH=f"{self.sysbin}:{os.environ['PATH']}")
        return subprocess.run(["bash", str(SBATCH), str(self.D), pin or self.pin, str(self.OUT), str(self.A1),
                               a1pin or self.a1pin], capture_output=True, text=True, env=env)

    def test_only_todo_tasks_run_and_done_is_written(self):
        self.setup_plan([("a", "done", "A0", "-:1", ()), ("b", "todo", "V", "-:2,-:3", ())])
        r = self.job()
        self.assertEqual(r.returncode, 0, r.stderr)
        L = self.OUT / "log-full"
        self.assertFalse((L / "a.start").exists())
        self.assertTrue((L / "b.end").exists())
        d = json.loads((L / "DONE").read_text())
        self.assertEqual((d["mode"], d["pin"], d["a1_pin"], d["tasks"], d["staged"], d["ran"]),
                         ("full", self.pin, self.a1pin, 2, 1, 1))
        self.assertIn("runs/V/rs1_V_b-_j3.trace.json.gz", (L / "SHA256SUMS").read_text())

    def test_a_teardown_crash_is_recomputed_once_and_compared(self):
        """REQUIRED (A1 guard)."""
        self.setup_plan([("a", "todo", "V", "-:6,-:7", ("CRASH",)), ("b", "todo", "V", "-:8", ())])
        r = self.job()
        self.assertEqual(r.returncode, 0, r.stderr)
        L = self.OUT / "log-full"
        t = (L / "a.teardown").read_text()
        self.assertIn("exit=129 after all 4 files were written", t)
        self.assertIn("rs1_V_b-_j6.npz bitwise_identical", t)
        self.assertIn("rs1_V_b-_j7.npz bitwise_identical", t)
        self.assertTrue((self.OUT / "runs-teardown" / "a" / "rs1_V_b-_j6.trace.json.gz").exists())
        self.assertTrue((self.OUT / "runs" / "V" / "rs1_V_b-_j6.npz").exists())
        self.assertIn("a", json.loads((L / "DONE").read_text())["teardown"])

    def test_a_failure_before_writing_is_a_failure_and_the_queue_continues(self):
        """REQUIRED (A1 guard): more tasks than lanes, so an aborting xargs would leave some unstarted."""
        others = [(f"t{i:02d}", "todo", "V", f"-:{i + 1}", ("SLOW",)) for i in range(12)]   # still running when a fails
        self.setup_plan([("a", "todo", "A0", "-:0", ("FAIL",))] + others)
        r = self.job()
        self.assertEqual(r.returncode, 1)
        L = self.OUT / "log-full"
        self.assertIn("before every product was written", (L / "a.failed").read_text())
        self.assertFalse((L / "a.teardown").exists())
        self.assertTrue(all((L / f"{i}.end").exists() for i, *_ in others))
        self.assertIn("failed=a ", (L / "FAILED").read_text())
        self.assertFalse((L / "DONE").exists())

    def test_a_second_crash_is_a_failure(self):
        """REQUIRED (A1 guard)."""
        self.setup_plan([("a", "todo", "V", "-:6", ("CRASH2",))])
        r = self.job()
        self.assertEqual(r.returncode, 1)
        self.assertIn("on the re-run", (self.OUT / "log-full" / "a.failed").read_text())
        self.assertFalse((self.OUT / "log-full" / "DONE").exists())

    def test_refusals_before_anything_is_written(self):
        self.setup_plan([("a", "todo", "V", "-:1", ())])
        dry = (self.OUT / "log-dry" / "DONE").read_text()
        (self.OUT / "log-dry" / "DONE").write_text(json.dumps({"pin": "0" * 40}))   # only the deploy check can catch it
        r = self.job(pin="0" * 40)
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: deploy HEAD", r.stderr)
        (self.OUT / "log-dry" / "DONE").write_text(dry)
        plan = self.A1 / "nd-unfolding" / "rs1_a1_plan.py"
        plan.write_text(plan.read_text() + "# a harmless local edit\n")             # still a working module
        r = self.job()
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: a1 tools", r.stderr)
        subprocess.run(["git", "-C", str(self.A1), "checkout", "-q", "--", "."], check=True)
        r = self.job(a1pin="1" * 40)
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: a1 tools", r.stderr)
        self.assertFalse((self.OUT / "log-full").exists())
        (self.OUT / "log-dry" / "DONE").write_text(json.dumps({"pin": "q" * 40}))
        r = self.job()
        self.assertEqual(r.returncode, 2)
        self.assertIn("ran at pin", r.stderr)
        (self.OUT / "log-dry" / "DONE").write_text(json.dumps({"pin": self.pin}))
        (self.OUT / "plan.tsv").write_text("# h\n")
        r = self.job()
        self.assertEqual(r.returncode, 2)
        self.assertIn("the plan has", r.stderr)
        self.setup_plan([("a", "todo", "V", "-:1", ())])
        (self.OUT / "staged.npz").write_text("y")
        (self.OUT / "copies.sha256").write_text(f"{'0' * 64}  staged.npz\n")
        r = self.job()
        self.assertEqual(r.returncode, 2)
        self.assertIn("no longer verifies", r.stderr)
        (self.OUT / "copies.sha256").write_text("\n")
        self.assertEqual(self.job().returncode, 0)
        self.assertEqual(self.job().returncode, 2)          # log-full now exists

    def test_a_task_whose_expect_fails_is_a_failure_not_a_teardown(self):
        """Audit W04: no declared files (expect refuses a line without --tag) is never 'all present'."""
        self.setup_plan([("a", "todo", "V", "-:1", ())])
        q = (self.OUT / "queue.tsv").read_text().replace("\t--tag\trs1_V", "")
        (self.OUT / "queue.tsv").write_text(q)
        r = self.job()
        self.assertEqual(r.returncode, 1)
        L = self.OUT / "log-full"
        self.assertIn("before every product was written", (L / "a.failed").read_text())
        self.assertFalse((L / "a.teardown").exists())

    def test_every_task_must_be_done_or_ended(self):
        """Audit W05: a task without its end record leaves no DONE even when none failed."""
        self.setup_plan([("b", "todo", "V", "-:1", ()), ("c", "todo", "V", "-:2", ("DROPEND",))])
        r = self.job()
        self.assertEqual(r.returncode, 1)
        self.assertIn("done=0 ran=1 of 2", (self.OUT / "log-full" / "FAILED").read_text())
        self.assertFalse((self.OUT / "log-full" / "DONE").exists())

    def test_xargs_rc_alone_stops_the_run(self):
        """Audit W06: a task killed by a signal writes no .failed; xargs's rc must still decide FAILED."""
        self.setup_plan([("a", "todo", "V", "-:1", ("KILLTASK",))])
        r = self.job()
        self.assertEqual(r.returncode, 1)
        f = (self.OUT / "log-full" / "FAILED").read_text()
        self.assertTrue(f.startswith("rc=") and not f.startswith("rc=0 "), f)
        self.assertFalse((self.OUT / "log-full" / "DONE").exists())

    def test_the_a1_clone_must_hold_the_plan_module(self):
        """Audit W08: a clean clone at its pin, but without rs1_a1_plan.py."""
        self.setup_plan([("a", "todo", "V", "-:1", ())])
        other = Path(self.tmp.name) / "other"
        pin = git_repo(other, {"README": "x\n"})
        env = dict(os.environ, RS1_TIME_BIN=str(self.time))
        r = subprocess.run(["bash", str(SBATCH), str(self.D), self.pin, str(self.OUT), str(other), pin],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: a1 tools", r.stderr)

    def test_a_failed_move_aside_is_a_failure_and_the_crashed_files_are_not_used(self):
        """Audit W09: if the crashed files cannot move aside, the runner would skip them and they would be used."""
        self.setup_plan([("a", "todo", "V", "-:6", ("CRASH",))])
        (self.OUT / "runs-teardown").write_text("a file, so the move-aside directory cannot be made")
        r = self.job()
        self.assertEqual(r.returncode, 1)
        L = self.OUT / "log-full"
        self.assertIn("could not move", (L / "a.failed").read_text())
        self.assertFalse((L / "a.end").exists())

    def test_every_planner_call_runs_under_the_sourced_environment(self):
        """REQUIRED (A1 connect 1's stop): every planner call runs under the job's sourced environment. The job starts
        with a "system" python3 that refuses the planner, so a call made before the source fails the run."""
        self.setup_plan([("a", "todo", "V", "-:6", ("CRASH",))])
        r = self.job()
        self.assertEqual(r.returncode, 0, r.stderr)
        calls = self.calls.read_text()
        self.assertIn("rs1_a1_plan.py verify --root", calls)
        self.assertIn("rs1_a1_plan.py expect", calls)
        self.assertTrue((self.OUT / "log-full" / "env.log").exists())

    def test_an_environment_without_lightgbm_is_refused(self):
        self.setup_plan([("a", "todo", "V", "-:1", ())])
        (self.stub / "lightgbm.py").unlink()
        self.assertEqual(self.job().returncode, 7)


if __name__ == "__main__":
    unittest.main()
