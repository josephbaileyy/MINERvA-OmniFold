"""Tests for tol_compare.py: the tolerance criterion and the predeclared tables, both directions, synthetic."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tol_compare as tc  # noqa: E402

BASE = np.array([1.0, 2.0, 0.0, 4.0, 3.0])
SEP = np.array([1.01, 1.98, 0.0, 4.05, 2.97])      # another contract: ~1% away, same zeros


def near(v, rel):
    """v scaled by (1 + rel): a reproduction `rel` away in every nonzero bin."""
    return v * (1.0 + rel)


class Harness:
    def __init__(self):
        self.d = Path(tempfile.mkdtemp(prefix="oi160-tol-"))
        (self.d / "out").mkdir(); (self.d / "stored").mkdir()
        self.rows = []

    def npz(self, path, values, seed):
        np.savez_compressed(path, seed=seed, xsec_flat=np.asarray(values, float),
                            shape=np.array([len(values)]), total_xsec=float(np.sum(values)))

    def control(self, a1, a2):
        self.npz(self.d / "out" / "control_A1.npz", a1, 1)
        self.npz(self.d / "out" / "control_A2.npz", a2, 1)
        self.npz(self.d / "first_A1.npz", a1, 1)

    def seed(self, s, producer, stored, a, b):
        self.npz(self.d / "stored" / f"res_boot_{s}.npz", stored, s)
        if a is not None:
            self.npz(self.d / "out" / f"s{s}_A.npz", a, s)
        if b is not None:
            self.npz(self.d / "out" / f"s{s}_B.npz", b, s)
        digest = hashlib.sha256((self.d / "stored" / f"res_boot_{s}.npz").read_bytes()).hexdigest()
        self.rows.append((len(self.rows) + 1, s, producer, digest))

    def run(self, corrupt_pin=False):
        seeds = self.d / "seeds.tsv"
        lines = ["task\tseed\tproducer\tmtime_minus0700\tsha256\tidentified_by"]
        for t, s, p, h in self.rows:
            lines.append(f"{t}\t{s}\t{p}\tx\t{'0' * 64 if corrupt_pin else h}\tx")
        seeds.write_text("\n".join(lines) + "\n")
        out = self.d / "readout.json"
        code = tc.main(["--out-dir", str(self.d / "out"), "--stored-dir", str(self.d / "stored"),
                        "--seeds", str(seeds), "--first-run-a1", str(self.d / "first_A1.npz"),
                        "--readout", str(out)])
        return code, (json.loads(out.read_text()) if out.exists() else None)


class Tests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.h.control(BASE, near(BASE, 3e-12))          # the measured floor scale

    def verdicts(self, r):
        return {s["seed"]: s["verdict"] for s in r["seeds"]}

    def test_corrected_old_and_neither_per_seed(self):
        self.h.seed(2, "p1", BASE, near(BASE, 1e-12), SEP)    # corrected
        self.h.seed(3, "p2", SEP, BASE, near(SEP, 1e-12))     # old
        self.h.seed(6, "p3", BASE * 1.5, BASE, SEP)           # neither
        code, r = self.h.run()
        self.assertEqual(code, 0)
        self.assertEqual(self.verdicts(r), {2: "CORRECTED", 3: "OLD", 6: "NEITHER"})
        self.assertEqual(r["overall"], "MIXED")

    def test_one_reading_across_all_producers(self):
        for s, p in ((2, "p1"), (3, "p2"), (40, "p3")):
            self.h.seed(s, p, BASE, near(BASE, 2e-12), SEP)
        r = self.h.run()[1]
        self.assertEqual(r["producers"], {"p1": "CORRECTED", "p2": "CORRECTED", "p3": "CORRECTED"})
        self.assertEqual(r["overall"], "CORRECTED")

    def test_the_tolerance_boundary_both_sides(self):
        self.h.seed(2, "p1", BASE, near(BASE, 0.99e-8), SEP)  # just inside TAU: agrees
        self.h.seed(3, "p1", BASE, near(BASE, 2e-8), SEP)     # outside TAU: disagrees
        v = self.verdicts(self.h.run()[1])
        self.assertEqual((v[2], v[3]), ("CORRECTED", "NEITHER"))

    def test_a_different_zero_pattern_disagrees_even_within_tolerance(self):
        a = BASE.copy(); a[2] = 1e-60                          # tiny, but nonzero where stored is zero
        self.h.seed(2, "p1", BASE, a, SEP)
        self.assertEqual(self.verdicts(self.h.run()[1])[2], "NEITHER")

    def test_a_high_fresh_floor_voids_everything(self):
        self.h.control(BASE, near(BASE, 1e-9))                # above TAU/100
        self.h.seed(2, "p1", BASE, BASE, SEP)
        r = self.h.run()[1]
        self.assertFalse(r["fresh_floor_ok"])
        self.assertEqual((self.verdicts(r)[2], r["overall"]), ("VOID", "VOID"))

    def test_codes_that_do_not_separate_void_the_seed(self):
        self.h.seed(2, "p1", BASE, BASE, near(BASE, 1e-9))    # A and B closer than 100*TAU
        self.assertEqual(self.verdicts(self.h.run()[1])[2], "VOID")

    def test_mixed_within_a_producer(self):
        self.h.seed(3, "p2", BASE, near(BASE, 1e-12), SEP)    # corrected
        self.h.seed(6, "p2", SEP, BASE, near(SEP, 1e-12))     # old
        r = self.h.run()[1]
        self.assertEqual(r["producers"]["p2"], "MIXED")
        self.assertEqual(r["overall"], "MIXED")

    def test_a_missing_old_output_is_not_agreement(self):
        self.h.seed(2, "p1", BASE, near(BASE, 1e-12), None)
        self.assertEqual(self.verdicts(self.h.run()[1])[2], "VOID")   # cannot show separation

    def test_a_stored_file_that_is_not_the_pinned_one_is_refused(self):
        self.h.seed(2, "p1", BASE, BASE, SEP)
        code, r = self.h.run(corrupt_pin=True)
        self.assertEqual((code, r), (1, None))


if __name__ == "__main__":
    unittest.main()
