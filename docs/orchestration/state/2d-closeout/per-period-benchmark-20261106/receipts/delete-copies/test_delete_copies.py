#!/usr/bin/env python3
"""Tests for delete_copies.py, each guard in both directions. Run: python3 -B -m unittest test_delete_copies"""
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import delete_copies as D  # noqa: E402

NS = "/pscratch/sd/j/josephrb/per-period-benchmark-20261106/"
INPUTS = os.environ.get("PPB_INPUTS")   # the committed INPUTS.sha256, for the cross-check


def make(root, files):
    os.makedirs(root)
    want = {}
    for name, data in files.items():
        with open(os.path.join(root, name), "wb") as fh:
            fh.write(data)
        want[name] = hashlib.sha256(data).hexdigest()
    return want


class TestRun(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.a, self.b = os.path.join(self.t.name, "a"), os.path.join(self.t.name, "b")
        self.targets = {self.a: make(self.a, {"x.root": b"x" * 1000, "copies.json": b"{}"}),
                        self.b: make(self.b, {"y.root": b"y" * 10})}
        self.ledger = os.path.join(self.t.name, "ledger")

    def tearDown(self):
        self.t.cleanup()

    def go(self):
        return D.run(self.targets, self.ledger, 0, require_login=False)

    def present(self):
        return [p for r, w in self.targets.items() for p in [os.path.join(r, n) for n in w] + [r] if os.path.lexists(p)]

    def test_clean_case_deletes_everything_and_records_it(self):
        rc, rec = self.go()
        self.assertEqual(rc, 0)
        self.assertEqual(self.present(), [])
        self.assertEqual(len(rec["roots"][self.a]["removed"]), 2)
        self.assertTrue(os.path.isfile(os.path.join(self.ledger, "ledger.json")))
        self.assertEqual(rec["roots"][self.a]["measured"], self.targets[self.a])     # both values recorded

    def test_wrong_digest_stops_with_nothing_deleted(self):
        self.targets[self.b]["y.root"] = "0" * 64
        rc, _ = self.go()
        self.assertEqual(rc, 4)
        self.assertEqual(len(self.present()), 5)          # root a passed its checks but nothing in it was removed

    def test_extra_file_stops(self):
        open(os.path.join(self.a, "stray"), "w").close()
        self.assertEqual(self.go()[0], 4)
        self.assertEqual(len(self.present()), 5)

    def test_subdirectory_stops(self):
        os.makedirs(os.path.join(self.b, "sub"))
        self.assertEqual(self.go()[0], 4)
        self.assertEqual(len(self.present()), 5)

    def test_missing_file_stops(self):
        os.remove(os.path.join(self.a, "x.root"))
        rc, rec = self.go()
        self.assertEqual(rc, 4)
        self.assertEqual(rec["roots"][self.a]["missing"], ["x.root"])
        self.assertTrue(os.path.isfile(os.path.join(self.a, "copies.json")))

    def test_symlink_in_place_of_a_file_stops(self):
        p = os.path.join(self.b, "y.root")
        os.remove(p)
        os.symlink(os.path.join(self.a, "x.root"), p)
        self.assertEqual(self.go()[0], 4)
        self.assertTrue(os.path.isfile(os.path.join(self.a, "x.root")))

    def test_existing_ledger_refuses(self):
        os.makedirs(self.ledger)
        self.assertEqual(self.go()[0], 4)
        self.assertEqual(len(self.present()), 5)

    def test_login_node_required(self):
        if not os.uname().nodename.startswith("login"):
            rc, rec = D.run(self.targets, self.ledger, 0, require_login=True)
            self.assertEqual(rc, 4)
            self.assertEqual(len(self.present()), 5)


class TestProductionTargets(unittest.TestCase):
    def test_scope_is_exactly_the_read_copies_root(self):
        self.assertEqual(sorted(D.TARGETS), [NS + "read/copies"])           # the GO named the 39 read copies only
        self.assertEqual(len(D.TARGETS[NS + "read/copies"]), 41)               # 39 copies + copies.json + verify.json
        self.assertEqual(sorted(n for n in D.TARGETS[NS + "read/copies"] if not n.endswith(".root")),
                         ["copies.json", "verify.json"])
        self.assertEqual(D.LEDGER, NS + "delete-ledger")
        for w in D.TARGETS.values():
            for n, h in w.items():
                self.assertEqual(len(h), 64)
                self.assertNotIn("/", n)

    @unittest.skipUnless(INPUTS, "PPB_INPUTS not set")
    def test_every_root_copy_digest_is_the_declared_operand_digest(self):
        declared = {}
        for line in open(INPUTS):
            if line.strip():
                h, src = line.split(None, 1)
                src = src.strip()
                base = os.path.basename(src)
                declared[base if base.startswith("cov_ptpl_") else os.path.basename(os.path.dirname(src)) + "__" + base] = h
        for root, w in D.TARGETS.items():
            for n, h in w.items():
                if n.endswith(".root"):
                    self.assertEqual(h, declared[n], n)
        self.assertEqual(sorted(n for n in D.TARGETS[NS + "read/copies"] if n.endswith(".root")), sorted(declared))


class TestSmokeTargets(unittest.TestCase):
    def test_second_row_scope_and_ledger(self):
        import delete_smoke_copies as S2
        self.assertEqual(sorted(S2.TARGETS), [NS + "connect1/smoke-copies"])
        self.assertEqual(sorted(S2.TARGETS[NS + "connect1/smoke-copies"]),
                         ["cov_ptpl_minerva_inclusive_6GeV.root", "pu_PA_b01__xsec.root"])
        self.assertEqual(S2.LEDGER, NS + "delete-ledger-smoke")
        self.assertNotEqual(S2.LEDGER, D.LEDGER)
        for n, h in S2.TARGETS[NS + "connect1/smoke-copies"].items():
            self.assertEqual(h, D.TARGETS[NS + "read/copies"][n])     # the same operands as the read copies


if __name__ == "__main__":
    unittest.main()
