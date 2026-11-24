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
    sys.exit(int(os.environ.get("FAKE_REFCHECK", "0")))
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
# drop srun's options, then /usr/bin/time -v -o FILE, and run the rest
while [ "$#" -gt 0 ] && [ "$1" != /usr/bin/time ]; do shift; done
shift; [ "$1" = -v ] && shift; [ "$1" = -o ] && shift 2
exec "$@"
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
        self.log = self.d / "dispatch.log"

    def run_job(self, M=None, **env):
        e = dict(os.environ, IBUB_TEST="1", IBUB_PY=sys.executable, IBUB_SRUN=str(self.srun), FAKE_LOG=str(self.log),
                 PYTHONDONTWRITEBYTECODE="1", **env)
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
        self.assertEqual((d["stage"], d["rc"], d["toy_pass_markers"], d["porcelain_after"]), ("toys", 0, 600, 0))
        self.assertIn("barrier PASS", r.stdout)

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
        self.assertEqual(self.done()["toy_pass_markers"], 599)

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
        e = dict(os.environ, IBUB_TEST="0")
        r = subprocess.run(["bash", str(JOB), str(self.deploy), str(self.N), self.M], capture_output=True, text=True, env=e)
        self.assertEqual(r.returncode, 2)
        self.assertIn("refusing: N is", r.stdout)


if __name__ == "__main__":
    unittest.main()
