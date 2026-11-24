"""Tests for covfix_ledger (COVFIX-DECLARATION.md rev 11.4 section 3.3, ST3/ST6). Synthetic sacct rows and a fake
scheduler (sbatch, scontrol, scancel scripts) only.

  python3 -B -m unittest -v test_covfix_ledger.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import covfix_ledger as cl

CAPS = {"PG": 3.0, "P1": 330.0, "PV": 135.0}
GROUPS = {"pg": "PG", "w1": "P1", "w2": "P1", "pv": "PV"}
H = 3600
TOYS = {"w1": {"N1": ["t1", "t2"], "N2": ["t1"]}}
FIXED = {}


def mk(d, caps=CAPS, groups=GROUPS, ceiling=541.50, toys=None, fixed=None):
    return cl.Ledger(d, caps, groups, ceiling, TOYS if toys is None else toys, FIXED if fixed is None else fixed)


def row(job, name, state, nodes=1, elapsed=3600):
    return {"JobID": str(job), "JobName": name, "State": state, "NNodes": str(nodes), "ElapsedRaw": str(elapsed)}


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)
        self.L = mk(self.d / "campaign", CAPS, GROUPS, 541.50)
        self.L.init()

    def tearDown(self):
        self._td.cleanup()

    def submitted(self, phase="w1", nodes=1, t=60, job="1"):
        r = self.L.new_intent(phase, nodes, t)
        self.L.record_submission(r["intent"], job)
        return r


class Units(unittest.TestCase):
    def test_minute_rounding_in_node_seconds(self):
        self.assertEqual(cl.reservation_ns(1, 3600), 3600)
        self.assertEqual(cl.reservation_ns(2, 61), 2 * 120)
        self.assertEqual(cl.reservation_ns(1, 60), 60)

    def test_refusals(self):
        for n, t in ((0, 60), (1, 0), (1.5, 60), (1, 60.0), (True, 60)):
            with self.subTest(n=n, t=t), self.assertRaises(cl.Refusal):
                cl.reservation_ns(n, t)

    def test_hhmmss_and_scontrol_time(self):
        self.assertEqual(cl.hhmmss(45 * 60), "00:45:00")                 # never "0:45" (45 seconds)
        self.assertEqual(cl.hhmmss(11 * H + 29 * 60), "11:29:00")
        self.assertEqual(cl.hhmmss(48 * H), "48:00:00")
        self.assertEqual(cl.slurm_seconds("1-02:03:04"), ((24 + 2) * 60 + 3) * 60 + 4)
        self.assertEqual(cl.slurm_seconds("02:03:04"), (2 * 60 + 3) * 60 + 4)
        self.assertEqual(cl.slurm_seconds("45:00"), 45 * 60)
        self.assertIsNone(cl.slurm_seconds("UNLIMITED"))

    def test_sacct_state(self):
        self.assertEqual(cl.sacct_state("CANCELLED by 12345"), "CANCELLED")
        self.assertEqual(cl.sacct_state(""), "")

    def test_policy_validation(self):
        for caps, groups, ceil in (({"P1": float("nan")}, {"w1": "P1"}, 1.0), ({"P1": 1.0}, {"w1": "P1"}, float("inf")),
                                   ({"P1": -1.0}, {"w1": "P1"}, 1.0), ({"P1": 1.0}, {"w1": "P1"}, 1 / 7),
                                   ({"P1": 1.0}, {"pv": "PV"}, 1.0), ({}, {}, 1.0), ({"P1": 1.0}, {"W 1": "P1"}, 1.0)):
            with self.subTest(caps=caps, ceil=ceil), self.assertRaises(cl.Refusal):
                mk("/nowhere", caps, groups, ceil)
        self.assertEqual(mk("/nowhere", CAPS, GROUPS, 541.50).ceiling, 1_949_400)


class Init(unittest.TestCase):
    def test_init_once_policy_bound_and_absent_refused(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "c"
            L = mk(d, CAPS, GROUPS, 541.50)
            with self.assertRaises(cl.Refusal):
                L.new_intent("w1", 1, 60)                               # not initialized
            with mock.patch.object(cl.os, "fsync") as f:
                L.init()
            self.assertEqual(f.call_count, 3)                            # the new dir's parent, the file, its dir
            with self.assertRaises(cl.Refusal):
                L.init()                                                 # never re-created
            other = mk(d, dict(CAPS, P1=331.0), GROUPS, 541.50)
            with self.assertRaises(cl.Refusal):
                other.new_intent("w1", 1, 60)                           # a different policy
            with self.assertRaises(cl.Refusal):
                mk(Path(td) / "absent", CAPS, GROUPS, 541.50).state()

    def test_locked_needs_the_directory(self):
        with self.assertRaises(cl.Refusal):
            with mk("/nonexistent-dir-xyz", CAPS, GROUPS, 541.50).locked():
                pass


class Intents(Base):
    def test_intent_and_job_name(self):
        r = self.L.new_intent("w1", 1, 3600)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{32}", r["intent"]))
        self.assertEqual(r["job_name"], f"covfix_w1_{r['intent']}")
        self.assertEqual((r["gate"]["group"], r["gate"]["total_ns"]), ("P1", 3600))
        line = json.loads((self.d / "campaign" / cl.LEDGER).read_text().splitlines()[1])
        self.assertEqual((line["kind"], line["phase"], line["reservation"]), ("intent", "w1", 3600))

    def test_no_new_intent_while_one_is_unrecorded(self):
        self.L.new_intent("w1", 1, 3600)
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("w1", 1, 3600)

    def test_unknown_phase(self):
        for p in ("px", "W1", "bad phase"):
            with self.subTest(p=p), self.assertRaises(cl.Refusal):
                self.L.new_intent(p, 1, 60)

    def test_group_cap_and_ceiling_exact_integers(self):
        self.submitted("pg", 1, 3 * H, "1")                             # exactly the PG cap
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("pg", 1, 60)
        with tempfile.TemporaryDirectory() as td:
            L = mk(Path(td), {"P1": 1000.0}, {"w1": "P1"}, 2.0)
            L.init()
            r = L.new_intent("w1", 1, 2 * H)                            # exactly the ceiling
            L.record_submission(r["intent"], "2")
            with self.assertRaises(cl.Refusal):
                L.new_intent("w1", 1, 60)

    def test_group_totals_are_separate(self):
        self.submitted("pg", 1, H, "21")
        self.submitted("w1", 2, H, "22")
        st = self.L.state()
        self.assertEqual(self.L.totals(st, "PG"), {"spent_ns": 0, "held_ns": H})
        self.assertEqual(self.L.totals(st, "P1"), {"spent_ns": 0, "held_ns": 2 * H})
        self.assertEqual(self.L.totals(st), {"spent_ns": 0, "held_ns": 3 * H})

    def test_record_submission(self):
        r = self.L.new_intent("w1", 1, 60)
        for bad in ("abc", "12a"):
            with self.subTest(bad=bad), self.assertRaises(cl.Refusal):
                self.L.record_submission(r["intent"], bad)
        with self.assertRaises(cl.Refusal):
            self.L.record_submission("0" * 32, "5")
        self.L.record_submission(r["intent"], "5")
        with self.assertRaises(cl.Refusal):
            self.L.record_submission(r["intent"], "6")
        r2 = self.L.new_intent("w1", 1, 60)
        with self.assertRaises(cl.Refusal):
            self.L.record_submission(r2["intent"], "5")


class Reconcile(Base):
    def test_lost_id_is_matched_from_the_full_job_name(self):
        r = self.L.new_intent("w1", 2, 3600)
        out = self.L.reconcile([row(900, r["job_name"], "RUNNING", 2, 100)])
        self.assertEqual((out["matched"], out["open"]), (1, 1))
        self.assertEqual(self.L.state()["intents"][r["intent"]]["job"], "900")
        self.L.new_intent("w1", 1, 60)

    def test_a_different_phase_in_the_name_does_not_match(self):
        r = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(901, f"covfix_w2_{r['intent']}", "RUNNING")])
        self.assertEqual(out["unresolved"], [r["intent"]])

    def test_ambiguous_or_absent_stays_unresolved(self):
        r = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(1, r["job_name"], "PENDING"), row(2, r["job_name"], "PENDING")])
        self.assertEqual(out["unresolved"], [r["intent"]])
        self.assertEqual(self.L.reconcile([])["unresolved"], [r["intent"]])
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("w1", 1, 60)

    def test_a_matched_job_already_used_stays_unresolved(self):
        self.submitted("w1", job="7")
        b = self.L.new_intent("w1", 1, 60)
        self.assertEqual(self.L.reconcile([row(7, b["job_name"], "PENDING")])["unresolved"], [b["intent"]])

    def test_terminal_charge_once_and_frees_the_reservation(self):
        r = self.submitted("pg", 1, 3 * H, "11")
        self.assertEqual(self.L.totals(self.L.state(), "PG"), {"spent_ns": 0, "held_ns": 3 * H})
        self.assertEqual(self.L.reconcile([row(11, r["job_name"], "CANCELLED by 9", 1, 1800)])["charged"], 1)
        self.assertEqual(self.L.totals(self.L.state(), "PG"), {"spent_ns": 1800, "held_ns": 0})
        self.assertEqual(self.L.reconcile([row(11, r["job_name"], "COMPLETED", 1, 9999)])["charged"], 0)
        self.assertEqual(self.L.state()["intents"][r["intent"]]["charge"], 1800)
        self.L.new_intent("pg", 1, int(2.5 * H))

    def test_charge_counts_every_node(self):
        r = self.submitted("w1", 2, H, "12")
        self.L.reconcile([row(12, r["job_name"], "COMPLETED", 2, 1800)])
        self.assertEqual(self.L.state()["intents"][r["intent"]]["charge"], 2 * 1800)

    def test_uncertain_accounting_stays_open(self):
        r = self.submitted("w1", job="3")
        n = r["job_name"]
        for rows in ([row(3, n, "RUNNING")],
                     [dict(row(3, n, "COMPLETED"), NNodes="x")],
                     [dict(row(3, n, "COMPLETED"), ElapsedRaw="-5")],
                     [dict(row(3, n, "COMPLETED"), NNodes="0")],
                     [row(3, n, "COMPLETED", 1, 100), row(3, n, "COMPLETED", 1, 200)],   # conflicting rows
                     [row(3, "someone_else", "COMPLETED")],                              # the job's name is not ours
                     []):
            with self.subTest(rows=str(rows)[:60]):
                self.assertEqual(self.L.reconcile(rows)["open"], 1)
        self.assertIsNone(self.L.state()["intents"][r["intent"]]["charge"])

    def test_foreign_and_step_rows_are_ignored(self):
        r = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(5, "ibub_run", "COMPLETED"), row("5.batch", r["job_name"], "COMPLETED")])
        self.assertEqual(out["unresolved"], [r["intent"]])


class Submit(Base):
    def fake(self, name, body):
        p = self.d / name
        p.write_text(f"#!{sys.executable}\nimport sys, os\n{body}")
        p.chmod(0o755)
        return str(p)

    def scheduler(self, job_out="4242", tl=None, name=None, qos="regular_1", sb_rc=0, nn=None, rq="0"):
        log = self.d / "calls.log"
        sb = self.fake("sbatch", f"open({str(log)!r}, 'a').write('sbatch ' + ' '.join(sys.argv[1:]) + '\\n')\n"
                                 f"print({job_out!r}); sys.exit({sb_rc})\n")
        sc = self.fake("scontrol", f"open({str(log)!r}, 'a').write('scontrol ' + ' '.join(sys.argv[1:]) + '\\n')\n"
                                   "args = [a for a in open(" + repr(str(log)) + ").read().split() if a.startswith('--')]\n"
                                   "nm = [a.split('=',1)[1] for a in args if a.startswith('--job-name=')][-1]\n"
                                   "tm = [a.split('=',1)[1] for a in args if a.startswith('--time=')][-1]\n"
                                   "nd = [a.split('=',1)[1] for a in args if a.startswith('--nodes=')][-1]\n"
                                   f"nm = {name!r} or nm\ntm = {tl!r} or tm\nnd = {nn!r} or nd\n"
                                   f"print('JobId=4242 JobName=' + nm + ' UserId=x QOS={qos} TimeLimit=' + tm"
                                   f" + ' NumNodes=' + nd + ' Requeue={rq}')\n")
        sx = self.fake("scancel", f"open({str(log)!r}, 'a').write('scancel ' + ' '.join(sys.argv[1:]) + '\\n')\n")
        return sb, sc, sx, log

    def test_submit_argv_record_and_verify(self):
        it = self.L.new_intent("w1", 1, 45 * 60)
        sb, sc, sx, log = self.scheduler()
        self.assertEqual(self.L.submit(it["intent"], "/x/job.sbatch", sb, sc, sx), "4242")
        calls = log.read_text()
        self.assertIn(f"--job-name={it['job_name']}", calls)
        self.assertIn("--time=00:45:00", calls)
        self.assertIn("--no-requeue", calls)
        self.assertIn("--nodes=1", calls)
        self.assertIn("scontrol show job 4242", calls)
        self.assertNotIn("scancel", calls)
        self.assertNotIn("squeue", calls)
        self.assertEqual(self.L.state()["intents"][it["intent"]]["job"], "4242")

    def test_cluster_suffix_parsed(self):
        it = self.L.new_intent("w1", 1, 60)
        sb, sc, sx, _ = self.scheduler(job_out="4242;perlmutter")
        self.assertEqual(self.L.submit(it["intent"], "/x/j", sb, sc, sx), "4242")

    def test_mismatches_scancel_and_stop(self):
        for kw, field in (({"tl": "00:44:00"}, "TimeLimit"), ({"name": "covfix_w1_" + "0" * 32}, "JobName"),
                          ({"qos": "debug"}, "QOS"), ({"nn": "2"}, "NumNodes"), ({"rq": "1"}, "Requeue")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                L = mk(Path(td), CAPS, GROUPS, 541.50)
                L.init()
                it = L.new_intent("w1", 1, 45 * 60)
                sb, sc, sx, log = self.scheduler(**kw)
                log.write_text("")
                with self.assertRaises(cl.Refusal) as e:
                    L.submit(it["intent"], "/x/j", sb, sc, sx)
                self.assertIn(field, str(e.exception))
                self.assertIn("scancel 4242", log.read_text())
                self.assertIn(field, L.state()["intents"][it["intent"]]["stop"])

    def test_an_sbatch_that_cannot_launch_stops(self):
        it = self.L.new_intent("w1", 1, 60)
        _, sc, sx, _ = self.scheduler()
        with self.assertRaises(cl.Refusal):
            self.L.submit(it["intent"], "/x/j", str(self.d / "no-such-sbatch"), sc, sx)   # an OSError at launch
        self.assertIn("sbatch", self.L.state()["intents"][it["intent"]]["stop"])

    def test_sbatch_failure_keeps_the_hold_and_stops(self):
        it = self.L.new_intent("w1", 1, 60)
        sb, sc, sx, log = self.scheduler(job_out="4242", sb_rc=1)       # a job ID printed, but sbatch failed
        with self.assertRaises(cl.Refusal):
            self.L.submit(it["intent"], "/x/j", sb, sc, sx)
        st = self.L.state()["intents"][it["intent"]]
        self.assertIsNone(st["job"])
        self.assertIn("sbatch", st["stop"])
        self.assertEqual(self.L.totals(self.L.state()), {"spent_ns": 0, "held_ns": 60})
        n = log.read_text().count("sbatch ")
        with self.assertRaises(cl.Refusal):
            self.L.submit(it["intent"], "/x/j", sb, sc, sx)              # claimed: never a second sbatch
        self.assertEqual(log.read_text().count("sbatch "), n)
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("w1", 1, 60)                               # still held, still unrecorded

    def test_claim_once_before_sbatch(self):
        it = self.L.new_intent("w1", 1, 60)
        sb, sc, sx, log = self.scheduler()
        self.assertEqual(self.L.submit(it["intent"], "/x/j", sb, sc, sx), "4242")
        with self.assertRaises(cl.Refusal):
            self.L.submit(it["intent"], "/x/j", sb, sc, sx)
        self.assertEqual(log.read_text().count("sbatch "), 1)
        kinds = [json.loads(x)["kind"] for x in (self.d / "campaign" / cl.LEDGER).read_text().splitlines()]
        self.assertLess(kinds.index("claimed"), kinds.index("submitted"))
        with self.assertRaises(cl.Refusal):
            self.L.submit("0" * 32, "/x/j", sb, sc, sx)

    def test_argv_from_the_stored_reservation_and_extra_allowlist(self):
        it = self.L.new_intent("w1", 2, 45 * 60)
        sb, sc, sx, log = self.scheduler()
        for bad in (("--time=99:00:00",), ("--nodes=4",), ("-N", "4"), ("--requeue",), ("--job-name=x",)):
            with self.subTest(bad=bad), self.assertRaises(cl.Refusal):
                self.L.submit(it["intent"], "/x/j", sb, sc, sx, extra=bad)
        self.assertFalse(log.exists() and "sbatch " in log.read_text())
        self.L.submit(it["intent"], "/x/j", sb, sc, sx, extra=("--account=m3246", "--constraint=cpu", "--exclusive"))
        calls = log.read_text()
        self.assertIn("--nodes=2", calls)
        self.assertIn("--time=00:45:00", calls)
        self.assertIn("--account=m3246", calls)

    def test_whole_minutes_required(self):
        it = self.L.new_intent("w1", 1, 61)
        with self.assertRaises(cl.Refusal):
            self.L.submit(it["intent"], "/x/j", "/bin/false", "/bin/false", "/bin/false")
        self.assertFalse(self.L.state()["intents"][it["intent"]]["claimed"])


class Toys(Base):
    def test_accept_exactly_once_tied_to_a_job_of_the_phase(self):
        self.submitted("w1", job="31")
        self.submitted("pg", job="32")
        self.L.accept("w1", "N1", "t1", "a" * 64, "31")
        with self.assertRaises(cl.Refusal):
            self.L.accept("w1", "N1", "t1", "b" * 64, "31")
        for bad in (("t9", "a" * 64, "31"), ("t2", "A" * 64, "31"), ("t2", "a" * 64, "32"), ("t2", "a" * 64, "99")):
            with self.subTest(bad=bad), self.assertRaises(cl.Refusal):
                self.L.accept("w1", "N1", bad[0], bad[1], bad[2])
        self.assertEqual(self.L.complete("w1", "N1"), {"complete": False, "missing": ["t2"], "n": 1})
        self.L.accept("w1", "N1", "t2", "c" * 64, "31")
        self.assertTrue(self.L.complete("w1", "N1")["complete"])
        self.L.accept("w1", "N2", "t1", "d" * 64, "31")


class Storage(Base):
    def lines(self):
        return (self.d / "campaign" / cl.LEDGER).read_text()

    def test_corrupt_or_invalid_transitions_refuse(self):
        r = self.submitted("w1", job="41")
        good = self.lines()
        p = self.d / "campaign" / cl.LEDGER
        bad_tails = ["not json\n", json.dumps({"kind": "other"}) + "\n", good.splitlines()[1] + "\n",
                     json.dumps({"kind": "reconciled", "intent": r["intent"], "job": "41", "charge": -5}) + "\n",
                     json.dumps({"kind": "submitted", "intent": r["intent"], "job": "041"}) + "\n",
                     json.dumps({"kind": "amendment", "group": "PV", "cap_ns": 3600, "director_sha": "x"}) + "\n",
                     json.dumps({"kind": "accepted", "phase": "w1", "arm": "N1", "toy": "t9", "sha256": "a" * 64,
                                 "job": "41"}) + "\n",
                     json.dumps({"kind": "intent", "intent": r["intent"], "phase": "w1", "reservation": 60}) + "\n",
                     json.dumps({"kind": "submitted", "intent": r["intent"], "job": "42"}) + "\n",
                     json.dumps({"kind": "reconciled", "intent": r["intent"], "job": "99", "charge": 1}) + "\n",
                     json.dumps({"kind": "policy"}) + "\n"]
        for tail in bad_tails:
            with self.subTest(tail=tail[:40]):
                p.write_text(good + tail)
                with self.assertRaises(cl.Refusal):
                    self.L.state()
        p.write_text(good)
        self.L.reconcile([row(41, r["job_name"], "COMPLETED")])
        twice = self.lines().splitlines()[-1] + "\n"
        p.write_text(self.lines() + twice)
        with self.assertRaises(cl.Refusal):
            self.L.state()

    def test_a_duplicated_acceptance_line_refuses(self):
        self.submitted("w1", job="51")
        self.L.accept("w1", "N1", "t1", "a" * 64, "51")
        p = self.d / "campaign" / cl.LEDGER
        last = p.read_text().splitlines()[-1] + "\n"
        p.write_text(p.read_text() + last)
        with self.assertRaises(cl.Refusal):
            self.L.state()

    def test_every_append_is_fsynced(self):
        with mock.patch.object(cl.os, "fsync") as f:
            r = self.L.new_intent("w1", 1, 60)
            self.L.record_submission(r["intent"], "4")
        self.assertEqual(f.call_count, 2)

    def test_lock_is_exclusive(self):
        probe = ("import fcntl,sys\nf=open(sys.argv[1],'a')\n"
                 "try:\n fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);print('got')\nexcept OSError:\n print('busy')\n")
        with self.L.locked():
            out = subprocess.run([sys.executable, "-c", probe, str(self.d / "campaign" / cl.LOCK)],
                                 capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "busy")
        out = subprocess.run([sys.executable, "-c", probe, str(self.d / "campaign" / cl.LOCK)],
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "got")


class ZeroAndCanon(Base):
    def test_a_zero_charge_needs_a_never_started_job(self):
        r = self.submitted("w1", job="61")
        n = r["job_name"]
        self.assertEqual(self.L.reconcile([row(61, n, "CANCELLED", 1, 0)])["open"], 1)          # no Start: held
        self.assertEqual(self.L.reconcile([dict(row(61, n, "CANCELLED", 1, 0), Start="2026-11-24T10:00:00")])["open"], 1)
        self.assertEqual(self.L.reconcile([dict(row(61, n, "CANCELLED", 1, 0), Start="None")])["charged"], 1)
        self.assertEqual(self.L.state()["intents"][r["intent"]]["charge"], 0)

    def test_job_ids_are_canonical(self):
        r = self.L.new_intent("w1", 1, 60)
        self.L.record_submission(r["intent"], "0042")
        self.assertEqual(self.L.state()["intents"][r["intent"]]["job"], "42")
        self.assertEqual(self.L.reconcile([row("042", r["job_name"], "COMPLETED", 1, 30)])["charged"], 1)
        self.L.accept("w1", "N1", "t1", "a" * 64, "00042")
        self.assertEqual(self.L.state()["toys"][("w1", "N1", "t1")]["job"], "42")


class FixedAndAmend(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.L = mk(Path(self._td.name) / "c", {"PV": 3.0}, {"pv": "PV"}, 10.0, toys={},
                    fixed={"synth": {"group": "PV", "node_h": 2.0}, "u2draw": {"group": "PV", "node_h": 1.0}})
        self.L.init()

    def tearDown(self):
        self._td.cleanup()

    def test_fixed_lines_are_held_from_init(self):
        self.assertEqual(self.L.totals(self.L.state(), "PV"), {"spent_ns": 0, "held_ns": 3 * H})
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("pv", 1, 60)                               # the cap is fully held by the two lines

    def test_an_intent_draws_on_its_line_once(self):
        r = self.L.new_intent("pv", 1, 2 * H, fixed="synth")
        self.assertEqual(r["gate"]["group_total_ns"], 3 * H)             # the line's hold replaced, not added
        self.L.record_submission(r["intent"], "71")
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("pv", 1, 60, fixed="synth")                # used
        self.L.reconcile([row(71, r["job_name"], "COMPLETED", 1, 1800)])
        self.assertEqual(self.L.totals(self.L.state(), "PV"), {"spent_ns": 1800, "held_ns": H})

    def test_a_line_refuses_a_larger_or_unknown_draw(self):
        self.L.amend_cap("PV", 10.0, "b" * 40)                           # room under the cap: only the line refuses
        for kw in ({"fixed": "u2draw", "t": 2 * H}, {"fixed": "nope", "t": 60}):
            with self.subTest(kw=kw), self.assertRaises(cl.Refusal):
                self.L.new_intent("pv", 1, kw["t"], fixed=kw["fixed"])

    def test_amendment_needs_a_sha_and_moves_the_cap(self):
        with self.assertRaises(cl.Refusal):
            self.L.amend_cap("PV", 4.0, "not-a-sha")
        with self.assertRaises(cl.Refusal):
            self.L.amend_cap("PX", 4.0, "a" * 40)
        self.L.amend_cap("PV", 4.0, "a" * 40)
        self.assertEqual(self.L.state()["caps"]["PV"], 4 * H)
        self.L.new_intent("pv", 1, H)                                    # now fits beside the two lines

    def test_policy_validation_of_toys_and_fixed(self):
        for toys, fixed in (({"zz": {"A": ["t"]}}, {}), ({"pv": {"A": []}}, {}), ({"pv": {"A": ["t", "t"]}}, {}),
                            ({}, {"x": {"group": "PX", "node_h": 1.0}}), ({}, {"x": {"group": "PV"}}),
                            ({}, {"x": {"group": "PV", "node_h": float("nan")}})):
            with self.subTest(toys=toys, fixed=fixed), self.assertRaises(cl.Refusal):
                mk("/nowhere", {"PV": 3.0}, {"pv": "PV"}, 10.0, toys=toys, fixed=fixed)


class PolicyToys(Base):
    def test_accept_only_toys_in_the_policy(self):
        self.submitted("w1", job="81")
        with self.assertRaises(cl.Refusal):
            self.L.accept("w1", "N9", "t1", "a" * 64, "81")
        with self.assertRaises(cl.Refusal):
            self.L.complete("w1", "N9")
        self.L.accept("w1", "N2", "t1", "a" * 64, "81")
        self.assertTrue(self.L.complete("w1", "N2")["complete"])


if __name__ == "__main__":
    unittest.main()
