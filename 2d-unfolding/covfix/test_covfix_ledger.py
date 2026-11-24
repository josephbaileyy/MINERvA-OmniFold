"""Tests for covfix_ledger (COVFIX-DECLARATION.md rev 11.4 section 3.3, ST3/ST6). Synthetic sacct rows only.

  python3 -B -m unittest -v test_covfix_ledger.py
"""
from __future__ import annotations

import fcntl
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


def row(job, name, state, nodes=1, elapsed=3600):
    return {"JobID": str(job), "JobName": name, "State": state, "NNodes": str(nodes), "ElapsedRaw": str(elapsed)}


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)
        self.L = cl.Ledger(self.d / "campaign", CAPS, GROUPS, 541.50)

    def tearDown(self):
        self._td.cleanup()


class Reservation(unittest.TestCase):
    def test_minute_rounding(self):
        self.assertEqual(cl.reservation_nodeh(1, 3600), 1.0)
        self.assertEqual(cl.reservation_nodeh(2, 61), 2 * 2 / 60)
        self.assertEqual(cl.reservation_nodeh(1, 60), 1 / 60)

    def test_refusals(self):
        for n, t in ((0, 60), (1, 0), (1.5, 60), (1, 60.0)):
            with self.subTest(n=n, t=t), self.assertRaises(cl.Refusal):
                cl.reservation_nodeh(n, t)

    def test_sacct_state(self):
        self.assertEqual(cl.sacct_state("CANCELLED by 12345"), "CANCELLED")
        self.assertEqual(cl.sacct_state(""), "")

    def test_groups_need_caps(self):
        with self.assertRaises(cl.Refusal):
            cl.Ledger("/nowhere", {"P1": 1.0}, {"pv": "PV"}, 1.0)


class Intents(Base):
    def test_intent_and_job_name(self):
        r = self.L.new_intent("w1", 1, 3600)
        self.assertTrue(re.fullmatch(r"[0-9a-f]{32}", r["intent"]))
        self.assertEqual(r["job_name"], f"covfix_w1_{r['intent']}")
        self.assertEqual(r["gate"]["group"], "P1")
        line = json.loads((self.d / "campaign" / cl.LEDGER).read_text().splitlines()[0])
        self.assertEqual((line["kind"], line["phase"], line["reservation"]), ("intent", "w1", 1.0))

    def test_no_new_intent_while_one_is_unrecorded(self):
        self.L.new_intent("w1", 1, 3600)
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("w1", 1, 3600)

    def test_unknown_phase(self):
        for p in ("px", "W1", "bad phase"):
            with self.subTest(p=p), self.assertRaises(cl.Refusal):
                self.L.new_intent(p, 1, 60)

    def test_group_cap_and_ceiling(self):
        r = self.L.new_intent("pg", 1, 3 * 3600)               # exactly the PG cap: allowed
        self.L.record_submission(r["intent"], "1")
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("pg", 1, 60)                     # one more minute exceeds the cap
        L = cl.Ledger(self.d / "c2", {"P1": 1000.0}, {"w1": "P1"}, 2.0)
        r = L.new_intent("w1", 1, 2 * 3600)                    # exactly the ceiling
        L.record_submission(r["intent"], "2")
        with self.assertRaises(cl.Refusal):
            L.new_intent("w1", 1, 60)

    def test_group_totals_are_separate(self):
        a = self.L.new_intent("pg", 1, 3600)
        self.L.record_submission(a["intent"], "21")
        b = self.L.new_intent("w1", 2, 3600)
        self.L.record_submission(b["intent"], "22")
        st = self.L.state()
        self.assertEqual(self.L.totals(st, "PG"), {"spent": 0.0, "held": 1.0})
        self.assertEqual(self.L.totals(st, "P1"), {"spent": 0.0, "held": 2.0})
        self.assertEqual(self.L.totals(st), {"spent": 0.0, "held": 3.0})

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
            self.L.record_submission(r2["intent"], "5")        # the job is another intent's


class Reconcile(Base):
    def test_lost_id_is_matched_from_the_job_name(self):
        r = self.L.new_intent("w1", 2, 3600)
        out = self.L.reconcile([row(900, r["job_name"], "RUNNING", 2, 100)])
        self.assertEqual((out["matched"], out["open"]), (1, 1))
        self.assertEqual(self.L.state()["intents"][r["intent"]]["job"], "900")
        self.L.new_intent("w1", 1, 60)                          # reconciled: a new intent may proceed

    def test_ambiguous_or_absent_stays_unresolved(self):
        r = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(1, r["job_name"], "PENDING"), row(2, r["job_name"], "PENDING")])
        self.assertEqual(out["unresolved"], [r["intent"]])
        self.assertEqual(self.L.reconcile([])["unresolved"], [r["intent"]])
        with self.assertRaises(cl.Refusal):
            self.L.new_intent("w1", 1, 60)

    def test_a_matched_job_already_used_stays_unresolved(self):
        a = self.L.new_intent("w1", 1, 60)
        self.L.record_submission(a["intent"], "7")
        b = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(7, b["job_name"], "PENDING")])
        self.assertEqual(out["unresolved"], [b["intent"]])

    def test_terminal_charge_once_and_frees_the_reservation(self):
        r = self.L.new_intent("pg", 1, 3 * 3600)
        self.L.record_submission(r["intent"], "11")
        self.assertEqual(self.L.totals(self.L.state(), "PG"), {"spent": 0.0, "held": 3.0})
        out = self.L.reconcile([row(11, r["job_name"], "CANCELLED by 9", 1, 1800)])
        self.assertEqual(out["charged"], 1)
        self.assertEqual(self.L.totals(self.L.state(), "PG"), {"spent": 0.5, "held": 0.0})
        self.assertEqual(self.L.reconcile([row(11, r["job_name"], "COMPLETED", 1, 9999)])["charged"], 0)
        self.assertEqual(self.L.state()["intents"][r["intent"]]["charge"], 0.5)
        self.L.new_intent("pg", 1, int(2.5 * 3600))            # 0.5 spent + 2.5 = the cap

    def test_running_or_garbled_stays_open(self):
        r = self.L.new_intent("w1", 1, 60)
        self.L.record_submission(r["intent"], "3")
        self.assertEqual(self.L.reconcile([row(3, r["job_name"], "RUNNING")])["open"], 1)
        bad = row(3, r["job_name"], "COMPLETED")
        bad["NNodes"] = "x"
        self.assertEqual(self.L.reconcile([bad])["open"], 1)
        self.assertIsNone(self.L.state()["intents"][r["intent"]]["charge"])

    def test_foreign_rows_are_ignored(self):
        r = self.L.new_intent("w1", 1, 60)
        out = self.L.reconcile([row(5, "ibub_run", "COMPLETED"), row("5.batch", r["job_name"], "COMPLETED")])
        self.assertEqual(out["unresolved"], [r["intent"]])


class Toys(Base):
    def test_accept_exactly_once(self):
        exp = {"t1", "t2"}
        self.L.accept("w1", "N1", "t1", "a" * 64, exp)
        with self.assertRaises(cl.Refusal):
            self.L.accept("w1", "N1", "t1", "b" * 64, exp)
        with self.assertRaises(cl.Refusal):
            self.L.accept("w1", "N1", "t9", "a" * 64, exp)
        with self.assertRaises(cl.Refusal):
            self.L.accept("w1", "N1", "t2", "A" * 64, exp)
        self.assertEqual(self.L.complete("w1", "N1", exp), {"complete": False, "missing": ["t2"], "n": 1})
        self.L.accept("w1", "N1", "t2", "c" * 64, exp)
        self.assertTrue(self.L.complete("w1", "N1", exp)["complete"])
        self.L.accept("w1", "N2", "t1", "d" * 64, exp)          # another arm is separate


class Storage(Base):
    def test_corrupt_or_unknown_lines_refuse(self):
        self.L.new_intent("w1", 1, 60)
        p = self.d / "campaign" / cl.LEDGER
        p.write_text(p.read_text() + "not json\n")
        with self.assertRaises(cl.Refusal):
            self.L.state()
        p.write_text(json.dumps({"kind": "other"}) + "\n")
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


if __name__ == "__main__":
    unittest.main()
