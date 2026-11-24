#!/usr/bin/env python3
"""Tests for ``jobs/ibub_job.sbatch`` and ``ibub_lanes.py`` (IBUB-DECLARATION.md section 8).

The real job script runs in test mode (IBUB_TEST=1) against a throwaway git deploy. The deploy holds the real
``ibub_lanes.py`` and ``cov2d.py`` and a fake ``ibub_unit.py``, which logs every unit it is handed and writes its
done-marker. A stub srun drops srun's options and ``/usr/bin/time -v -o FILE`` (macOS's time has no -v) and runs the
rest.

**The clean case:**
- the two references run;
- the barrier passes;
- each of the 600 toys is dispatched exactly once, on its lane, in steps of at most 10 units;
- IBUB-DONE reads 600 and exit 0.

**Each of these must stop:**
- a failed barrier, or a failed reference step: exit 3, and no toy is dispatched;
- a failed toy: exit 1, with the lane carrying on and the rest still run;
- a dirty deploy, another M, an existing IBUB-DONE, or a stage.json that is not PASS: exit 2, and nothing runs.

Needs bash (3.2 or later), git and numpy.
    cd 2d-unfolding/ibub && python -B -m unittest -v test_ibub_job
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ibub_lanes as il  # noqa: E402

JOB = HERE / "jobs" / "ibub_job.sbatch"
FAKE_UNIT = r'''import json, os, sys
from pathlib import Path
a = sys.argv[1:]
if a[0] == "refcheck":
    times = [a[i + 1] for i, x in enumerate(a) if x == "--time"]
    with open(os.environ["FAKE_LOG"] + ".refcheck", "w") as f:
        f.write(" ".join(times))
    if sorted(t.split("=")[0] for t in times) != ["central", "central_df"] or not all(Path(t.split("=", 1)[1]).exists() for t in times):
        sys.exit(9)
    sys.exit(int(os.environ.get("FAKE_REFCHECK", "0")))
if a[0] == "complete":
    print(json.dumps({"verdict": "PASS" if os.environ.get("FAKE_COMPLETE", "0") == "0" else "FAIL", "toy_pass": 600}))
    sys.exit(int(os.environ.get("FAKE_COMPLETE", "0")))
assert os.environ.get("IBUB_M") and os.environ.get("SLURM_JOB_ID"), "the unit is not bound"
units = [a[i + 1] for i, x in enumerate(a) if x == "--unit"]
out = Path(a[a.index("--out") + 1]); out.mkdir(parents=True, exist_ok=True)
fail = set(os.environ.get("FAKE_FAIL", "").split(","))
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(f"{os.getpid()} {' '.join(units)}\n")
rc = 0
for u in units:
    name = u.replace(":", "_")
    bad = u in fail
    (out / f"{name}.done").write_text(json.dumps({"unit": name, "verdict": "FAIL" if bad else "PASS"}))
    rc = rc or (6 if bad else 0)
sys.exit(rc)
'''
SRUN = r'''#!/bin/bash
# drop srun's options, then /usr/bin/time -v -o FILE (writing FILE as GNU time would), and run the rest
while [ "$#" -gt 0 ] && [ "$1" != /usr/bin/time ]; do shift; done
shift; [ "$1" = -v ] && shift; [ "$1" = -o ] && { tf=$2; shift 2; }
"$@"; rc=$?
printf '\tElapsed (wall clock) time (h:mm:ss or m:ss): 0:01.00\n\tExit status: %s\n' "$rc" > "$tf"
exit $rc
'''
SCONTROL = r'''#!/bin/bash
[ -n "$FAKE_SCONTROL_FAIL" ] && exit 1
echo "JobId=$2 JobName=${F_NAME:-ibub_run}"
echo "   QOS=${F_QOS:-regular} JobState=RUNNING"
echo "   RunTime=00:00:01 TimeLimit=${F_LIMIT:-11:29:00} TimeMin=N/A"
echo "   NumNodes=${F_NODES:-1} NumCPUs=256 OverSubscribe=${F_OVER:-NO} Contiguous=0"
echo "   AllocTRES=${F_TRES:-cpu=256,mem=480000M,node=1,billing=256}"
echo "   StdOut=${F_STDOUT:-$IBUB_NS/logs/ibub_run-$2.out}"
'''


class Lanes(unittest.TestCase):
    def test_the_table_is_two_references_then_600_toys_round_robin(self):
        rows = il.table()
        self.assertEqual(rows[:2], [("refs", 0, "central"), ("refs", 1, "central_df")])
        toys = [u for p, _, u in rows if p == "toys"]
        self.assertEqual(len(toys), 600)
        self.assertEqual(len(set(toys)), 600)
        self.assertEqual(Counter(ln for p, ln, _ in rows if p == "toys"), {0: 150, 1: 150, 2: 150, 3: 150})
        self.assertEqual(toys[0], "toy:G18:5720000")
        self.assertEqual(toys[300], "toy:AR23:5730000")
        self.assertEqual(il.lane("toys", 1)[:2], ["toy:G18:5720001", "toy:G18:5720005"])
        self.assertEqual(il.lane("refs", 2), [])
        for bad in (("refs", 4), ("x", 0)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                il.lane(*bad)

    def test_the_cli_in_process(self):
        import contextlib
        import io
        for argv, rc_want, lines in ((["verify"], 0, 1), (["table"], 0, 602), (["toys", "0"], 0, 150), (["toys", "7"], 2, 0),
                                     (["bogus"], 2, 0)):
            buf, err = io.StringIO(), io.StringIO()
            with self.subTest(argv=argv), contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                self.assertEqual(il.main(argv), rc_want)
            self.assertEqual(len([ln for ln in buf.getvalue().splitlines() if ln]), lines)
        with unittest.mock.patch.object(il, "verify", lambda: ["a problem"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(il.main(["verify"]), 1)

    def test_the_cli(self):
        r = subprocess.run([sys.executable, "-B", str(HERE / "ibub_lanes.py"), "toys", "3"], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(r.stdout.split()), 150)
        self.assertEqual(subprocess.run([sys.executable, "-B", str(HERE / "ibub_lanes.py"), "toys", "9"],
                                        capture_output=True).returncode, 2)
        r = subprocess.run([sys.executable, "-B", str(HERE / "ibub_lanes.py"), "table"], capture_output=True, text=True)
        self.assertEqual(len(r.stdout.splitlines()), 602)


class Job(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.d, True)
        self.deploy = self.d / "deploy"
        for rel, text in (("2d-unfolding/ibub/ibub_unit.py", FAKE_UNIT),
                          ("2d-unfolding/ibub/ibub_lanes.py", (HERE / "ibub_lanes.py").read_text()),
                          ("2d-unfolding/cov2d/cov2d.py", (HERE.parent / "cov2d" / "cov2d.py").read_text())):
            p = self.deploy / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        (self.deploy / ".gitignore").write_text("__pycache__/\n")
        g = ["git", "-C", str(self.deploy)]
        subprocess.run(g + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "fixture"], check=True)
        self.M = subprocess.run(g + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        self.N = self.d / "ns"
        (self.N / "stage").mkdir(parents=True)
        (self.N / "stage" / "stage.json").write_text(json.dumps({"verdict": "PASS"}))
        self.srun = self.d / "srun"
        self.srun.write_text(SRUN)
        self.srun.chmod(0o755)
        self.scontrol = self.d / "scontrol"
        self.scontrol.write_text(SCONTROL)
        self.scontrol.chmod(0o755)
        self.log = self.d / "dispatch.log"

    def run_job(self, M=None, **env):
        e = dict(os.environ, IBUB_TEST="1", IBUB_PY=sys.executable, IBUB_SRUN=str(self.srun),
                 IBUB_SCONTROL=str(self.scontrol), IBUB_NS=str(self.N), SLURM_JOB_ID="61900001",
                 FAKE_LOG=str(self.log), PYTHONDONTWRITEBYTECODE="1")
        e.update(env)
        return subprocess.run(["bash", str(JOB), str(self.deploy), str(self.N), M or self.M], capture_output=True,
                              text=True, env=e)

    def dispatched(self) -> list[list[str]]:
        return [ln.split()[1:] for ln in self.log.read_text().splitlines()] if self.log.exists() else []

    def done(self) -> dict:
        return json.loads((self.N / "IBUB-DONE").read_text())

    def test_clean_run_dispatches_every_toy_once_in_chunks_after_the_barrier(self):
        r = self.run_job()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        steps = self.dispatched()
        self.assertEqual(sorted(steps[:2]), [["central"], ["central_df"]])      # the references come first
        toys = [u for s in steps[2:] for u in s]
        self.assertEqual(Counter(toys), Counter(u for p, _, u in il.table() if p == "toys"))
        self.assertTrue(all(len(s) <= 10 for s in steps[2:]))
        self.assertEqual(len(steps[2:]), 60)
        for s in steps[2:]:                                    # every step's units are one lane's
            self.assertEqual(len({ln for p, ln, u in il.table() if u in s}), 1)
        d = self.done()
        self.assertEqual((d["stage"], d["rc"], d["job"], d["M"]), ("toys", 0, "61900001", self.M))
        self.assertEqual(d["completion"]["verdict"], "PASS")
        self.assertIn("barrier PASS", r.stdout)
        self.assertEqual(list(self.N.glob("IBUB-DONE.tmp*")), [])                     # published once, by rename
        times = (self.log.parent / (self.log.name + ".refcheck")).read_text().split()
        self.assertEqual(sorted(t.split("=")[0] for t in times), ["central", "central_df"])   # the full steps' walls
        self.assertTrue(all(t.endswith(".time") for t in times))

    def test_a_failed_barrier_or_reference_stops_before_any_toy(self):
        for env in ({"FAKE_REFCHECK": "3"}, {"FAKE_FAIL": "central_df"}):
            with self.subTest(env=env):
                self.setUp()
                r = self.run_job(**env)
                self.assertEqual(r.returncode, 3, r.stdout)
                self.assertTrue(all(s in (["central"], ["central_df"]) for s in self.dispatched()))
                self.assertEqual(self.done()["stage"], "refs")
                self.assertIn("no toy starts", r.stdout)

    def test_a_failed_toy_ends_rc1_and_the_rest_still_run(self):
        r = self.run_job(FAKE_FAIL="toy:AR23:5730007")
        self.assertEqual(r.returncode, 1, r.stdout)
        toys = [u for s in self.dispatched()[2:] for u in s]
        self.assertEqual(len(toys), 600)
        self.assertEqual(self.done()["rc"], 1)

    def test_a_failed_completion_check_ends_rc1(self):
        r = self.run_job(FAKE_COMPLETE="1")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual((self.done()["rc"], self.done()["completion"]["verdict"]), (1, "FAIL"))

    def test_each_allocation_mismatch_or_a_failed_query_refuses_with_nothing_run(self):
        cases = {"name": ({"F_NAME": "ibub_other"}, "JobName is"), "qos": ({"F_QOS": "debug"}, "QOS is"),
                 "limit": ({"F_LIMIT": "12:00:00"}, "TimeLimit is"), "nodes": ({"F_NODES": "2"}, "NumNodes is"),
                 "shared": ({"F_OVER": "OK"}, "OverSubscribe is"),
                 "stdout": ({"F_STDOUT": "/tmp/elsewhere.out"}, "StdOut"),
                 "tres unreadable": ({"F_TRES": "billing=256"}, "not readable from AllocTRES"),
                 "too small": ({"F_TRES": "cpu=128,mem=200000M"}, "do not fit"),
                 "query fails": ({"FAKE_SCONTROL_FAIL": "1"}, "scontrol show job failed")}
        for tag, (env, why) in cases.items():
            with self.subTest(case=tag):
                self.setUp()
                r = self.run_job(**env)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn(why, r.stdout)                      # the check that fired is the one named
                self.assertEqual(self.dispatched(), [])
        self.setUp()
        self.assertEqual(self.run_job(F_TRES="cpu=256,mem=470G").returncode, 0)     # mem given in G is read too

    def test_containment_refuses_a_symlinked_dir_a_used_units_dir_and_another_namespace(self):
        self.setUp()
        (self.N / "units").mkdir()
        (self.N / "units" / "central.done").write_text("{}")                      # an earlier job's products
        r = self.run_job()
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("not empty", r.stdout)
        self.setUp()
        elsewhere = self.d / "elsewhere"
        elsewhere.mkdir()
        (self.N / "logs").symlink_to(elsewhere)
        r = self.run_job()
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.setUp()
        r = self.run_job(IBUB_NS=str(self.d / "other"))
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.dispatched(), [])
        self.setUp()
        r = self.run_job(SLURM_JOB_ID="abc")
        self.assertEqual(r.returncode, 2)

    def test_each_precondition_refuses_with_nothing_run(self):
        cases = {
            "another M": dict(M="0" * 40),
            "not a sha": dict(M="HEAD"),
        }
        for tag, kw in cases.items():
            with self.subTest(case=tag):
                self.setUp()
                r = self.run_job(**kw)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertEqual(self.dispatched(), [])
        self.setUp()
        (self.deploy / "stray.txt").write_text("x")              # a dirty deploy
        self.assertEqual(self.run_job().returncode, 2)
        self.assertEqual(self.dispatched(), [])
        self.setUp()
        (self.N / "IBUB-DONE").write_text("{}")                    # an earlier run's end
        self.assertEqual(self.run_job().returncode, 2)
        self.setUp()
        (self.N / "stage" / "stage.json").write_text(json.dumps({"verdict": "FAIL"}))
        self.assertEqual(self.run_job().returncode, 2)
        self.assertEqual(self.dispatched(), [])

    def test_the_namespace_is_refused_outside_test_mode(self):
        e = dict(os.environ, IBUB_TEST="0", SLURM_JOB_ID="1")
        r = subprocess.run(["bash", str(JOB), str(self.deploy), str(self.N), self.M], capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: N is", r.stdout)

    def test_lanes_verify(self):
        self.assertEqual(il.verify(), [])
        real = il.table
        for tag, bad in (("a toy dropped", lambda: real()[:-1]), ("a toy twice", lambda: real() + [real()[-1]]),
                         ("references swapped", lambda: [("refs", 0, "central_df"), ("refs", 1, "central")] + real()[2:]),
                         ("a toy moved to another lane", lambda: real()[:2] + [("toys", 1, real()[2][2])] + real()[3:])):
            with self.subTest(case=tag), unittest.mock.patch.object(il, "table", bad):
                self.assertNotEqual(il.verify(), [])


if __name__ == "__main__":
    unittest.main()
