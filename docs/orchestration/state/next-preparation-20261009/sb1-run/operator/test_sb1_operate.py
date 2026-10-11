"""Local controls for sb1_operate.py with fake sacct/squeue/scancel (no scheduler is contacted).

    python3 -m unittest test_sb1_operate -v
"""

import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
OP = HERE / "sb1_operate.py"
PKG = "docs/orchestration/state/next-preparation-20261009/sb1-prep"

FAKE = r'''#!/usr/bin/env python3
import json, os, sys
state = json.load(open(os.environ["FAKE_STATE"]))
tool = os.path.basename(sys.argv[0])
if tool == "scancel":
    state.setdefault("cancelled", []).append(sys.argv[1])
    for j in state["jobs"]:
        if j["JobID"] == sys.argv[1]:
            j["State"] = "CANCELLED"
    json.dump(state, open(os.environ["FAKE_STATE"], "w"))
elif tool == "sacct":
    f = sys.argv[sys.argv.index("-o") + 1].split(",")
    print("|".join(f))
    for j in state["jobs"]:
        print("|".join(str(j.get(k, "")) for k in f))
elif tool == "squeue":
    for j in state["jobs"]:
        if j["State"] in ("PENDING", "RUNNING"):
            print("|".join([j["JobID"], j["JobName"], j["Submit"], j["State"], j["WorkDir"]]))
'''


def local(t):
    return t.astimezone().strftime("%Y-%m-%dT%H:%M:%S")


class Operator(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        t = self.tmp = Path(self._tmp.name)
        self.bin = t / "bin"
        self.bin.mkdir()
        for tool in ("sacct", "squeue", "scancel"):
            p = self.bin / tool
            p.write_text(FAKE)
            p.chmod(0o755)
        self.code = t / "code"
        (self.code / PKG / "launch").mkdir(parents=True)
        self.out = t / "sb1-out"
        self.adm = t / "adm.json"
        self.adm.write_text(json.dumps({"checkout": str(self.code), "outroot": str(self.out)}))
        self.state = t / "state.json"

    def tearDown(self):
        self._tmp.cleanup()

    def submit_script(self, body):
        (self.code / PKG / "launch" / "sb1_submit.sh").write_text("#!/bin/bash\n" + body + "\n")

    def jobs(self, jobs):
        self.state.write_text(json.dumps({"jobs": jobs}))

    def run_op(self, *args):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", FAKE_STATE=str(self.state),
                   USER="tester")
        return subprocess.run([sys.executable, OP, *args], capture_output=True, text=True, env=env)

    def job(self, jid, name, wd, state="PENDING", minutes=0):
        t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
        return {"JobID": jid, "JobName": name, "User": "tester", "Submit": local(t),
                "State": state, "WorkDir": str(wd), "StdOut": f"{wd}/{name}_{jid}.out",
                "StdErr": f"{wd}/{name}_{jid}.err", "ElapsedRaw": "0", "AllocTRES": ""}

    def test_a_failed_submission_cancels_only_this_attempts_jobs_including_unreturned_ids(self):
        # the "submit script" queues H0 (returned) and UL (orphan: id never printed), then fails
        self.submit_script(f'mkdir -p "{self.out}"; exit 1')
        other = self.tmp / "elsewhere"
        self.jobs([self.job("1001", "sb1_H0", self.out), self.job("1002", "sb1_UL", self.out),
                   self.job("2001", "sb1_UL", other, minutes=-600),      # another day, other dir
                   self.job("3001", "ki84_boot", other)])                 # unrelated, in window
        r = self.run_op("submit", "--admission", str(self.adm), "--record", str(self.tmp / "rec"))
        self.assertNotEqual(r.returncode, 0)
        st = json.loads(self.state.read_text())
        self.assertEqual(sorted(st["cancelled"]), ["1001", "1002"])
        found = json.loads((self.tmp / "rec" / "attempt-jobs.json").read_text())
        self.assertEqual(sorted(found["matched"]), ["1001", "1002"])
        self.assertEqual(found["ambiguous"], {})

    def test_a_same_name_job_from_another_directory_in_the_window_is_ambiguous_and_untouched(self):
        self.submit_script(f'mkdir -p "{self.out}"; exit 1')
        self.jobs([self.job("1001", "sb1_H0", self.out),
                   self.job("4001", "sb1_SL", self.tmp / "other-attempt")])
        r = self.run_op("submit", "--admission", str(self.adm), "--record", str(self.tmp / "rec"))
        self.assertNotEqual(r.returncode, 0)
        st = json.loads(self.state.read_text())
        self.assertEqual(st["cancelled"], ["1001"])
        log = (self.tmp / "rec" / "operator-log.jsonl").read_text()
        self.assertIn('"ambiguous": ["4001"]', log)

    def test_a_clean_submission_is_left_alone(self):
        ids = {"H0": "1001", "UL": "1002", "SL": "1003", "J1": "1004", "C": "1005", "H1": "1006"}
        self.submit_script(f'mkdir -p "{self.out}"; echo \'{json.dumps({"jobs": ids})}\' > '
                           f'"{self.out}/submission.json"; exit 0')
        self.jobs([self.job(v, f"sb1_{k}", self.out) for k, v in ids.items()])
        r = self.run_op("submit", "--admission", str(self.adm), "--record", str(self.tmp / "rec"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("cancelled", json.loads(self.state.read_text()))

    def test_exit_zero_with_a_missing_id_is_treated_as_ambiguous(self):
        ids = {"H0": "1001", "UL": "1002"}
        self.submit_script(f'mkdir -p "{self.out}"; echo \'{json.dumps({"jobs": ids})}\' > '
                           f'"{self.out}/submission.json"; exit 0')
        self.jobs([self.job("1001", "sb1_H0", self.out), self.job("1002", "sb1_UL", self.out),
                   self.job("1003", "sb1_SL", self.out)])
        r = self.run_op("submit", "--admission", str(self.adm), "--record", str(self.tmp / "rec"))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(sorted(json.loads(self.state.read_text())["cancelled"]),
                         ["1001", "1002", "1003"])

    def test_an_existing_outroot_is_refused_before_submission(self):
        self.out.mkdir()
        self.submit_script("echo SHOULD-NOT-RUN; exit 0")
        self.jobs([])
        r = self.run_op("submit", "--admission", str(self.adm), "--record", str(self.tmp / "rec"))
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("SHOULD-NOT-RUN", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
