"""Controls for the s5c campaign meter: each guard fires on its defect and stays silent
on the innocent neighbour (PB-16)."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
METER = HERE.parent / "s5c_meter.py"
sys.path.insert(1, str(HERE.parent))
import s5c_meter  # noqa: E402


def _budget(cpu_cap=10.0, cpu_stages=None, gpu_cap=5.0, gpu_stages=None) -> dict:
    return {
        "campaign_key": "s5c-20260924",
        "pools": {
            "cpu": {"campaign_cap_node_hours": cpu_cap, "stages": cpu_stages or {"pilot": 4.0, "verification_repair": 2.0}},
            "gpu": {"campaign_cap_node_hours": gpu_cap, "stages": gpu_stages or {"pilot": 2.0}},
        },
    }


class MeterHarness(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="s5c-meter-"))
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.budget = self.tmp / "budget.json"
        self.ledger = self.tmp / "ledger" / "admissions.jsonl"
        self.sacct_out = self.tmp / "sacct.txt"
        self.sacct_out.write_text("")
        self.write_budget(_budget())
        self._fake("sacct", f'cat "{self.sacct_out}"\n')
        self._fake("sbatch", 'echo "12345;perlmutter"\n')
        self.tres = self.tmp / "tres.txt"
        self.tres.write_text("JobId=12345 JobName=s5c-t AllocTRES=cpu=64,mem=100G,node=1,billing=128 Foo=bar\n")
        self._fake("scontrol", f'cat "{self.tres}"\n')
        self._fake("scancel", f'echo "$@" >> "{self.tmp}/scancelled"\n')

    def _fake(self, name: str, body: str) -> None:
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(path.stat().st_mode | stat.S_IEXEC)

    def write_budget(self, budget: dict) -> None:
        self.budget.write_text(json.dumps(budget))

    def run_meter(self, *args: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", USER="tester")
        argv = [sys.executable, str(METER), "--budget", str(self.budget), "--ledger", str(self.ledger), *args]
        return subprocess.run(argv, capture_output=True, text=True, env=env)

    def submit(self, *extra: str, stage="pilot", pool="cpu", ntasks="1", timelimit="1", billing="128", qos="shared"):
        return self.run_meter(
            "submit", "--stage", stage, "--pool", pool, "--qos", qos, "--ntasks", ntasks,
            "--timelimit-h", timelimit, "--billing", billing, "--label", "t",
            "--measures", "m", "--cannot-authorize", "c", *extra,
        )

    def ledger_records(self) -> list[dict]:
        return [json.loads(x) for x in self.ledger.read_text().splitlines()]


class AdmissionTests(MeterHarness):
    def test_innocent_within_caps_is_admitted_and_registered(self):
        proc = self.submit("--", "job.sh")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        kinds = [r["kind"] for r in self.ledger_records()]
        self.assertEqual(kinds, ["open", "job"])
        opened = self.ledger_records()[0]
        self.assertAlmostEqual(opened["reservation_node_hours"], 0.5)
        self.assertIn("--no-requeue", opened["argv"])
        self.assertIn("--job-name=s5c-t", opened["argv"])

    def test_stage_cap_refuses(self):
        proc = self.submit("--", "job.sh", ntasks="9", timelimit="1", billing="128")  # 4.5 > 4.0
        self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)
        self.assertFalse(self.ledger.exists() and self.ledger.read_text().strip())

    def test_reservations_accumulate_across_submissions(self):
        first = self.submit("--", "a.sh", ntasks="4", timelimit="1", billing="128")  # 2.0
        self.assertEqual(first.returncode, 0, first.stderr)
        self._fake("sbatch", 'echo "12346;perlmutter"\n')
        second = self.submit("--", "b.sh", ntasks="5", timelimit="1", billing="128")  # 2.0 + 2.5 > 4
        self.assertEqual(second.returncode, 3, second.stdout)

    def test_unknown_stage_refuses(self):
        proc = self.submit("--", "job.sh", stage="inference")
        self.assertEqual(proc.returncode, 3)

    def test_gpu_concurrency_refuses_and_throttle_admits(self):
        self.write_budget(_budget(gpu_cap=50.0, gpu_stages={"pilot": 50.0}))
        self.tres.write_text("JobId=12345 AllocTRES=cpu=32,mem=57G,node=1,billing=32,gres/gpu=1\n")
        wide = self.submit("--gpus-per-task", "1", "--", "g.sh", pool="gpu", qos="gpu_shared", ntasks="8", billing="32")
        self.assertEqual(wide.returncode, 4, wide.stdout)
        narrow = self.submit("--gpus-per-task", "1", "--throttle", "4", "--", "g.sh", pool="gpu", qos="gpu_shared", ntasks="8", billing="32")
        self.assertEqual(narrow.returncode, 0, narrow.stdout + narrow.stderr)

    def test_priced_flag_override_is_refused(self):
        for flag in ("--time=600", "--requeue", "-J", "--account=m3246_g", "--array=0-99", "--parsable"):
            proc = self.submit("--", flag, "job.sh")
            self.assertEqual(proc.returncode, 2, flag)

    def test_refused_qos(self):
        proc = self.submit("--", "job.sh", qos="premium")
        self.assertEqual(proc.returncode, 2)

    def test_sbatch_failure_releases_reservation(self):
        self._fake("sbatch", 'echo "boom" >&2; exit 1\n')
        proc = self.submit("--", "job.sh")
        self.assertEqual(proc.returncode, 7)
        self.assertEqual([r["kind"] for r in self.ledger_records()], ["open", "release"])
        self._fake("sbatch", 'echo "12347;perlmutter"\n')
        again = self.submit("--throttle", "4", "--", "job.sh", ntasks="8", billing="128")  # full 4.0 available again
        self.assertEqual(again.returncode, 0, again.stdout)


class SchedulerPriceTests(MeterHarness):
    def test_underpriced_job_is_cancelled_and_refused(self):
        # nothing in the arguments predicts it (e.g. a site default), but the scheduler bills 100
        self.tres.write_text("JobId=12345 AllocTRES=cpu=100,mem=180G,node=1,billing=100\n")
        proc = self.submit("--", "-c", "32", "job.sh", billing="64")
        self.assertEqual(proc.returncode, 8, proc.stdout + proc.stderr)
        self.assertEqual((self.tmp / "scancelled").read_text().split(), ["12345"])
        self.assertIn("job", [r["kind"] for r in self.ledger_records()])

    def test_matching_price_is_kept(self):
        self.tres.write_text("JobId=12345 AllocTRES=cpu=64,mem=100G,node=1,billing=64\n")
        proc = self.submit("--", "-c", "64", "job.sh", billing="64")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse((self.tmp / "scancelled").exists())

    def test_extra_gpus_are_refused(self):
        self.write_budget(_budget(gpu_cap=50.0, gpu_stages={"pilot": 50.0}))
        self.tres.write_text("JobId=12345 AllocTRES=cpu=64,mem=100G,node=1,billing=64,gres/gpu=2\n")
        proc = self.submit("--gpus-per-task", "1", "--", "-G", "2", "g.sh", pool="gpu", qos="gpu_shared", billing="64")
        self.assertEqual(proc.returncode, 8, proc.stdout + proc.stderr)


class PredictedPriceTests(MeterHarness):
    def test_underdeclared_shared_memory_price_is_refused_before_sbatch(self):
        proc = self.submit("--", "-c", "32", "--mem=90G", "job.sh", billing="32")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertFalse(self.ledger.exists() and self.ledger.read_text().strip())

    def test_declared_at_prediction_is_admitted(self):
        self.tres.write_text("JobId=12345 ReqTRES=cpu=32,mem=90G,node=1,billing=32 AllocTRES=\n")
        proc = self.submit("--", "-c", "32", "--mem=90G", "job.sh", billing="50")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_prediction_values(self):
        req = s5c_meter.Request("pilot", "cpu", "shared", 1, 1, 1.0, 50, 0, "t")
        self.assertEqual(s5c_meter.predicted_billing(req, ["-c", "32", "--mem=64G"]), 36)
        self.assertEqual(s5c_meter.predicted_billing(req, ["-c", "32", "--mem", "80000M"]), 44)
        self.assertEqual(s5c_meter.predicted_billing(req, ["-c", "32", "--mem=90G"]), 50)
        whole = s5c_meter.Request("pilot", "cpu", "regular", 1, 1, 1.0, 256, 0, "t")
        self.assertEqual(s5c_meter.predicted_billing(whole, ["-N", "1"]), 256)
        gpu = s5c_meter.Request("pilot", "gpu", "gpu_shared", 1, 1, 1.0, 32, 1, "t")
        self.assertEqual(s5c_meter.predicted_billing(gpu, ["-G", "1"]), 32)
        gpu_via_shared = s5c_meter.Request("pilot", "gpu", "shared", 1, 1, 1.0, 32, 1, "t")
        self.assertEqual(s5c_meter.predicted_billing(gpu_via_shared, ["--gpus-per-task=1"]), 32)
        gpu_regular = s5c_meter.Request("pilot", "gpu", "regular", 1, 1, 1.0, 128, 4, "t")
        self.assertEqual(s5c_meter.predicted_billing(gpu_regular, ["-N", "1"]), 128)

    def test_measured_attempt_above_declaration_is_flagged(self):
        self.assertEqual(self.submit("--", "job.sh", billing="128").returncode, 0)
        self.sacct_out.write_text("12345|s5c-t|COMPLETED|3600|billing=200|2026-09-25T01:00:00\n")
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertTrue(adm["underpriced"])
        self.assertAlmostEqual(adm["charged"], 200 / 256)


class AllocationTests(MeterHarness):
    def test_granted_allocation_is_recorded_once_and_price_checked(self):
        self._fake("salloc", 'echo "salloc: Pending job allocation 777" >&2; echo "salloc: Granted job allocation 777" >&2\n')
        self.tres.write_text("JobId=777 AllocTRES=cpu=256,mem=500G,node=1,billing=256\n")
        self.write_budget(_budget(cpu_cap=10.0, cpu_stages={"pilot": 4.0}))
        proc = self.submit("--allocate", "--", "-C", "cpu", "-N", "1", qos="interactive", billing="256", timelimit="2")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        kinds = [(r["kind"], r.get("job_id")) for r in self.ledger_records()]
        self.assertEqual(kinds, [("open", None), ("job", "777")])
        self.assertAlmostEqual(self.ledger_records()[0]["reservation_node_hours"], 2.0)

    def test_whole_node_interactive_underdeclared_is_refused(self):
        proc = self.submit("--allocate", "--", "-C", "cpu", "-N", "1", qos="interactive", billing="32")
        self.assertEqual(proc.returncode, 2)

    def test_failed_allocation_releases(self):
        self._fake("salloc", 'echo "salloc: error: Job submit/allocate failed" >&2; exit 1\n')
        self.write_budget(_budget(cpu_cap=10.0, cpu_stages={"pilot": 4.0}))
        proc = self.submit("--allocate", "--", "-C", "cpu", "-N", "1", qos="interactive", billing="256")
        self.assertEqual(proc.returncode, 7)
        self.assertEqual([r["kind"] for r in self.ledger_records()], ["open", "release"])


class ReviewFindingTests(MeterHarness):
    """Independent review 2026-09-25, findings 4 and 5."""

    def test_pending_null_alloctres_falls_back_to_reqtres(self):
        self.tres.write_text("JobId=12345 ReqTRES=cpu=100,mem=180G,node=1,billing=100 AllocTRES=(null)\n")
        proc = self.submit("--", "-c", "32", "job.sh", billing="64")
        self.assertEqual(proc.returncode, 8, proc.stdout + proc.stderr)

    def test_attached_short_and_abbreviated_long_overrides_are_refused(self):
        for bad in ("-t600", "-qpremium", "-a0-999", "--tim=600", "--qo=premium", "--arr=0-9", "--no-req",
                    "--mem-per-cpu=4G", "--exclusive", "--ntasks=4"):
            proc = self.submit("--", bad, "job.sh")
            self.assertEqual(proc.returncode, 2, bad)

    def test_innocent_flags_still_pass(self):
        self.tres.write_text("JobId=12345 AllocTRES=cpu=32,mem=40G,node=1,billing=32\n")
        proc = self.submit("--", "-c", "32", "--mem=40G", "-C", "cpu", "-o", "log.out", "job.sh", billing="64")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_abbreviated_nodes_is_priced(self):
        req = s5c_meter.Request("pilot", "cpu", "regular", 1, 1, 1.0, 256, 0, "t")
        self.assertEqual(s5c_meter.predicted_billing(req, ["--nod=4"]), 1024)


class AccountingTests(MeterHarness):
    def test_unregistered_campaign_job_fails_closed_and_foreign_job_does_not(self):
        self.sacct_out.write_text("999|other-lane|COMPLETED|3600|billing=128|2026-09-25T01:00:00\n")
        self.assertEqual(self.run_meter("measure").returncode, 0)
        self.sacct_out.write_text("998|s5c-rogue|RUNNING|60|billing=32|2026-09-25T01:00:00\n")
        proc = self.run_meter("measure")
        self.assertEqual(proc.returncode, 6, proc.stderr)
        self.assertEqual(self.submit("--", "job.sh").returncode, 6)

    def test_closed_job_is_charged_measured_and_open_job_its_reservation(self):
        self.assertEqual(self.submit("--", "job.sh", ntasks="2", billing="128", timelimit="2").returncode, 0)
        # reservation = 2 * 2 * 0.5 = 2.0; task 0 finished after 0.5 h, task 1 still running
        self.sacct_out.write_text(
            "12345_0|s5c-t|COMPLETED|1800|billing=128|2026-09-25T01:00:00\n"
            "12345_1|s5c-t|RUNNING|600|billing=128|2026-09-25T01:00:00\n"
        )
        rec = json.loads(self.run_meter("measure").stdout)
        adm = next(iter(rec["admissions"].values()))
        self.assertFalse(adm["closed"])
        self.assertAlmostEqual(adm["charged"], 2.0)
        self.sacct_out.write_text(
            "12345_0|s5c-t|COMPLETED|1800|billing=128|2026-09-25T01:00:00\n"
            "12345_1|s5c-t|FAILED|3600|billing=128|2026-09-25T01:00:00\n"
        )
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertTrue(adm["closed"])
        self.assertAlmostEqual(adm["charged"], 0.25 + 0.5)

    def test_cancelled_bracket_closes_never_started_tasks(self):
        self.assertEqual(self.submit("--", "job.sh", ntasks="3", billing="128").returncode, 0)
        self.sacct_out.write_text(
            "12345_0|s5c-t|COMPLETED|360|billing=128|2026-09-25T01:00:00\n"
            "12345_[1-2]|s5c-t|CANCELLED by 1|0||None\n"
        )
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertTrue(adm["closed"])
        self.assertAlmostEqual(adm["charged"], 0.05)

    def test_raw_id_tasks_close_the_array_once_linked(self):
        self.assertEqual(self.submit("--", "job.sh", ntasks="3", billing="128").returncode, 0)
        self.sacct_out.write_text(
            "12345_[2-2%1]|s5c-t|CANCELLED by 1|0||None\n"
            "90001|allocation|CANCELLED by 1|0||2026-09-25T01:00:00\n"
            "90002|allocation|CANCELLED by 1|0||2026-09-25T01:00:00\n"
        )
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertFalse(adm["closed"])  # two tasks unaccounted: reservation kept
        links = self.tmp / "links.txt"
        links.write_text("JobId=12345 ArrayJobId=12345 ArrayTaskId=4294967294\n"
                         "JobId=90002 ArrayJobId=12345 ArrayTaskId=1\nJobId=90001 ArrayJobId=12345 ArrayTaskId=0\n")
        self.assertEqual(self.run_meter("link", "--job", "12345", "--from-file", str(links)).returncode, 0)
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertTrue(adm["closed"])
        self.assertAlmostEqual(adm["charged"], 0.0)

    def test_job_id_queries_carry_no_user_filter(self):
        # a fake sacct that, like the real one, hides raw-id array tasks under -u
        self._fake("sacct", 'case "$*" in *"-u "*) ;; *"-j "*) echo "90001|allocation|CANCELLED by 1|0||x"; '
                            'echo "90002|allocation|CANCELLED by 1|0||x"; '
                            'echo "12345_[2-2%1]|s5c-t|CANCELLED by 1|0||None";; esac\n')
        self.assertEqual(self.submit("--", "job.sh", ntasks="3", billing="128").returncode, 0)
        links = self.tmp / "links.txt"
        links.write_text("JobId=90002 ArrayJobId=12345 ArrayTaskId=1\nJobId=90001 ArrayJobId=12345 ArrayTaskId=0\n")
        self.assertEqual(self.run_meter("link", "--job", "12345", "--from-file", str(links)).returncode, 0)
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertTrue(adm["closed"], adm)

    def test_link_to_unknown_job_is_refused(self):
        links = self.tmp / "links.txt"
        links.write_text("JobId=90001 ArrayJobId=55555 ArrayTaskId=0\n")
        self.assertEqual(self.run_meter("link", "--job", "55555", "--from-file", str(links)).returncode, 5)

    def test_pending_bracket_keeps_reservation(self):
        self.assertEqual(self.submit("--", "job.sh", ntasks="3", billing="128").returncode, 0)
        self.sacct_out.write_text("12345_[0-2%1]|s5c-t|PENDING|0||Unknown\n")
        adm = next(iter(json.loads(self.run_meter("measure").stdout)["admissions"].values()))
        self.assertFalse(adm["closed"])
        self.assertAlmostEqual(adm["charged"], 1.5)

    def test_changed_budget_after_binding_fails_closed(self):
        self.assertEqual(self.run_meter("rebind", "--reason", "initial").returncode, 0)
        self.assertEqual(self.run_meter("measure").returncode, 0)
        self.write_budget(_budget(cpu_cap=11.0))
        self.assertEqual(self.run_meter("measure").returncode, 5)
        self.assertEqual(self.run_meter("rebind", "--reason", "revision 2").returncode, 0)
        self.assertEqual(self.run_meter("measure").returncode, 0)

    def test_stage_allocations_above_cap_are_refused(self):
        self.write_budget(_budget(cpu_cap=5.0))  # stages sum to 6.0
        self.assertEqual(self.run_meter("measure").returncode, 5)

    def test_corrupt_ledger_line_fails_closed(self):
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text('{"kind": "open"\n')
        self.assertEqual(self.run_meter("measure").returncode, 5)


class SuccessorTests(MeterHarness):
    """The s5n successor (OI-191): its own prefix, its own scan, and a cap that cannot exceed the
    unspent carried-forward envelope."""

    def s5n_budget(self, cpu_cap=10.0, envelope=30.0, prior=20.0) -> dict:
        budget = _budget(cpu_cap=cpu_cap)
        budget["campaign_key"] = "s5n-20260925"
        budget["pools"]["cpu"]["carried_forward"] = {"envelope_node_hours": envelope,
                                                     "prior_charged_node_hours": prior}
        return budget

    def test_successor_job_carries_its_own_prefix(self):
        self.write_budget(self.s5n_budget())
        self.assertEqual(self.submit("--dry-run", "--", "job.sh").returncode, 0)
        argv = self.ledger_records()[0]["argv"]
        self.assertIn("--job-name=s5n-t", argv)
        self.assertNotIn("--job-name=s5c-t", argv)

    def test_successor_scan_sees_only_its_own_prefix(self):
        self.write_budget(self.s5n_budget())
        self.sacct_out.write_text("998|s5c-closed-campaign|COMPLETED|60|billing=32|2026-09-25T01:00:00\n")
        self.assertEqual(self.run_meter("measure").returncode, 0)
        self.sacct_out.write_text("997|s5n-rogue|RUNNING|60|billing=32|2026-09-25T01:00:00\n")
        self.assertEqual(self.run_meter("measure").returncode, 6)

    def test_unknown_campaign_key_is_refused(self):
        budget = _budget()
        budget["campaign_key"] = "s5x-20260925"
        self.write_budget(budget)
        self.assertEqual(self.run_meter("measure").returncode, 5)

    def test_cap_above_unspent_envelope_is_refused_and_at_unspent_admitted(self):
        self.write_budget(self.s5n_budget(cpu_cap=10.5, envelope=30.0, prior=20.0))
        self.assertEqual(self.run_meter("measure").returncode, 5)
        self.write_budget(self.s5n_budget(cpu_cap=10.0, envelope=30.0, prior=20.0))
        self.assertEqual(self.run_meter("measure").returncode, 0)

    def test_measure_reconciles_the_envelope(self):
        self.write_budget(self.s5n_budget())
        self.assertEqual(self.submit("--", "job.sh", billing="128").returncode, 0)
        self.sacct_out.write_text("12345|s5n-t|COMPLETED|3600|billing=128|2026-09-25T01:00:00\n")
        cf = json.loads(self.run_meter("measure").stdout)["summary"]["cpu"]["carried_forward"]
        self.assertAlmostEqual(cf["envelope_charged_node_hours"], 20.5)


class UnitTests(unittest.TestCase):
    def test_bracket_expansion(self):
        self.assertEqual(s5c_meter._expand_bracket("7_[0-2,5%2]"), ["7_0", "7_1", "7_2", "7_5"])

    def test_committed_budget_loads(self):
        repo = HERE.parent.parent
        budget = s5c_meter.load_budget(repo / "docs/orchestration/state/s5c/budget.json")
        self.assertAlmostEqual(budget["pools"]["gpu"]["campaign_cap_node_hours"] * 4, 500.0)
        self.assertLessEqual(budget["pools"]["cpu"]["campaign_cap_node_hours"], 500.0)

    def test_committed_successor_budget_carries_the_reconciled_prior_charge(self):
        repo = HERE.parent.parent
        budget = s5c_meter.load_budget(repo / "docs/orchestration/state/s5n/budget.json")
        prior = json.loads((repo / "docs/orchestration/state/s5n/s5c-ledger-reconciliation-20260925T1900Z.json").read_text())
        for pool, envelope in (("cpu", 345.27), ("gpu", 125.0)):
            section = budget["pools"][pool]
            self.assertAlmostEqual(section["carried_forward"]["prior_charged_node_hours"],
                                   prior["summary"][pool]["charged_node_hours"], places=9)
            self.assertAlmostEqual(section["carried_forward"]["envelope_node_hours"], envelope)
            self.assertLessEqual(section["campaign_cap_node_hours"],
                                 envelope - prior["summary"][pool]["charged_node_hours"])


if __name__ == "__main__":
    unittest.main()
