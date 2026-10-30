"""Tests for cml_compare.py: the tolerance criterion and the predeclared tables, both directions, synthetic."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cml_compare as cc  # noqa: E402

BASE = np.array([1.0, 2.0, 0.0, 4.0, 3.0])
SEP = np.array([1.01, 1.98, 0.0, 4.05, 2.97])      # another contract: ~1% away, same zeros


def near(v, rel):
    """v scaled by (1 + rel): a reproduction `rel` away in every nonzero bin."""
    return v * (1.0 + rel)


class Harness:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp(prefix="oi160-cml-"))
        (self.d / "out").mkdir(); (self.d / "stored").mkdir()
        self.rows = []

    def npz(self, path, values, seed, train_frac=0.8):
        np.savez_compressed(path, split_seed=seed, train_frac=train_frac, xsec_flat=np.asarray(values, float),
                            shape=np.array([len(values)]), total_xsec=float(np.sum(values)))

    def control(self, a1, a2):
        self.npz(self.d / "out" / "control_A1.npz", a1, 1)
        self.npz(self.d / "out" / "control_A2.npz", a2, 1)

    def seed(self, s, producer, stored, a, b, stored_train_frac=0.8):
        self.npz(self.d / "stored" / f"res_split_{s}.npz", stored, s, stored_train_frac)
        if a is not None:
            self.npz(self.d / "out" / f"s{s}_A.npz", a, s)
        if b is not None:
            self.npz(self.d / "out" / f"s{s}_B.npz", b, s)
        digest = hashlib.sha256((self.d / "stored" / f"res_split_{s}.npz").read_bytes()).hexdigest()
        self.rows.append((len(self.rows) + 1, s, producer, digest))

    def run(self, corrupt_pin=False):
        seeds = self.d / "seeds.tsv"
        lines = ["task\tseed\tproducer\tmtime_minus0700\tsha256\tidentified_by"]
        for t, s, p, h in self.rows:
            lines.append(f"{t}\t{s}\t{p}\tx\t{'0' * 64 if corrupt_pin else h}\tx")
        seeds.write_text("\n".join(lines) + "\n")
        out = self.d / "readout.json"
        code = cc.main(["--out-dir", str(self.d / "out"), "--stored-dir", str(self.d / "stored"),
                        "--seeds", str(seeds), "--readout", str(out)])
        return code, (json.loads(out.read_text()) if out.exists() else None)


class Tests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.h.control(BASE, near(BASE, 3e-12))          # the C_stat run's measured floor scale

    def verdicts(self, r):
        return {s["seed"]: s["verdict"] for s in r["seeds"]}

    def test_corrected_old_and_neither_per_seed(self):
        self.h.seed(4, "p1", BASE, near(BASE, 1e-12), SEP)    # corrected
        self.h.seed(9, "p2", SEP, BASE, near(SEP, 1e-12))     # old
        self.h.seed(14, "p3", BASE * 1.5, BASE, SEP)          # neither
        code, r = self.h.run()
        self.assertEqual(code, 0)
        self.assertEqual(self.verdicts(r), {4: "CORRECTED", 9: "OLD", 14: "NEITHER"})
        self.assertEqual(r["overall"], "MIXED")

    def test_one_reading_across_the_producer(self):
        for s in (4, 9, 14, 19, 24):
            self.h.seed(s, "p1", BASE, near(BASE, 2e-12), SEP)
        r = self.h.run()[1]
        self.assertEqual(r["producers"], {"p1": "CORRECTED"})
        self.assertEqual(r["overall"], "CORRECTED")

    def test_coincident_codes_that_both_reproduce_read_inert(self):
        self.h.seed(4, "p1", BASE, near(BASE, 1e-12), near(BASE, 2e-12))
        r = self.h.run()[1]
        self.assertEqual((self.verdicts(r)[4], r["seeds"][0]["separation"]), ("INERT", "COINCIDENT"))
        self.assertEqual(r["overall"], "INERT")

    def test_coincident_codes_that_both_miss_read_neither(self):
        self.h.seed(4, "p1", SEP, BASE, near(BASE, 1e-12))
        self.assertEqual(self.verdicts(self.h.run()[1])[4], "NEITHER")

    def test_coincident_codes_with_only_one_reproducing_void_the_seed(self):
        self.h.seed(4, "p1", BASE, near(BASE, 0.9e-8), near(BASE, 1.5e-8))   # A/B ~6e-9: coincident
        self.assertEqual(self.verdicts(self.h.run()[1])[4], "VOID")

    def test_codes_in_the_grey_band_void_the_seed(self):
        self.h.seed(4, "p1", BASE, BASE, near(BASE, 1e-7))    # TAU < A/B < 100*TAU
        r = self.h.run()[1]
        self.assertEqual((self.verdicts(r)[4], r["seeds"][0]["separation"]), ("VOID", "GREY"))

    def test_the_tolerance_boundary_both_sides(self):
        self.h.seed(4, "p1", BASE, near(BASE, 0.99e-8), SEP)  # just inside TAU: agrees
        self.h.seed(9, "p1", BASE, near(BASE, 2e-8), SEP)     # outside TAU: disagrees
        v = self.verdicts(self.h.run()[1])
        self.assertEqual((v[4], v[9]), ("CORRECTED", "NEITHER"))

    def test_a_different_zero_pattern_disagrees_even_within_tolerance(self):
        a = BASE.copy(); a[2] = 1e-60                          # tiny, but nonzero where stored is zero
        self.h.seed(4, "p1", BASE, a, SEP)
        self.assertEqual(self.verdicts(self.h.run()[1])[4], "NEITHER")

    def test_a_different_train_frac_disagrees(self):
        self.h.seed(4, "p1", BASE, near(BASE, 1e-12), SEP, stored_train_frac=0.7)
        r = self.h.run()[1]
        self.assertEqual(self.verdicts(r)[4], "NEITHER")
        self.assertFalse(r["seeds"][0]["stored_train_frac_is_declared"])

    def test_a_high_fresh_floor_voids_everything(self):
        self.h.control(BASE, near(BASE, 1e-9))                # above TAU/100
        self.h.seed(4, "p1", BASE, BASE, SEP)
        r = self.h.run()[1]
        self.assertFalse(r["fresh_floor_ok"])
        self.assertEqual((self.verdicts(r)[4], r["overall"]), ("VOID", "VOID"))

    def test_mixed_within_a_producer(self):
        self.h.seed(4, "p1", BASE, near(BASE, 1e-12), SEP)    # corrected
        self.h.seed(9, "p1", SEP, BASE, near(SEP, 1e-12))     # old
        r = self.h.run()[1]
        self.assertEqual((r["producers"]["p1"], r["overall"]), ("MIXED", "MIXED"))

    def test_a_missing_old_output_is_not_agreement(self):
        self.h.seed(4, "p1", BASE, near(BASE, 1e-12), None)   # the old code's SKIPPED path writes nothing
        self.assertEqual(self.verdicts(self.h.run()[1])[4], "VOID")

    def test_a_stored_file_that_is_not_the_pinned_one_is_refused(self):
        self.h.seed(4, "p1", BASE, BASE, SEP)
        code, r = self.h.run(corrupt_pin=True)
        self.assertEqual((code, r), (1, None))


if __name__ == "__main__":
    unittest.main()
