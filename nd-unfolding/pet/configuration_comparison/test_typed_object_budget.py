"""Tests for the token-budget derivation.

The bracket is the part worth testing: it is the only place in this comparison where
a number is *derived* rather than quoted, and it is derived from marginals that
cannot in principle pin the answer. Each test below fixes one way the derivation
could be wrong in a direction that would flatter the recommendation.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_typed_object_budget as budget


def _histogram(pairs: dict[int, int]) -> dict[str, int]:
    return {str(k): v for k, v in pairs.items()}


def _source(blobs: dict[int, int], max_photons: int, max_prongs: int) -> dict:
    return {
        "role": "mc",
        "playlist": "1A",
        "entries_read": sum(blobs.values()),
        "blobs": {"histogram": _histogram(blobs), "median": 6.0, "mean": 12.0,
                  "max": max(blobs)},
        "prongs": {"histogram": _histogram({1: 1}), "median": 2.0, "mean": 1.7,
                   "max": max_prongs},
        "photons": {"histogram": _histogram({0: 1}), "median": 0.0, "mean": 0.35,
                    "max": max_photons},
        "generic_clusters_nonmuon": {"median": 60.0, "mean": 102.6, "max": 2349,
                                     "fraction_above_cap": 0.844},
        "tail_energy_share_beyond_cap": {"median": 0.449},
    }


class TailFraction(unittest.TestCase):
    def test_counts_at_the_threshold(self):
        """`>= threshold` includes the threshold; an off-by-one here understates."""
        self.assertAlmostEqual(
            budget._tail_fraction(_histogram({10: 1, 12: 1, 14: 2}), 12), 0.75
        )

    def test_empty_histogram_raises(self):
        with self.assertRaises(ValueError):
            budget._tail_fraction({}, 12)


class Bracket(unittest.TestCase):
    def test_lower_bound_is_blobs_alone(self):
        """The lower bound must assume no other family contributes."""
        source = _source({0: 90, 33: 10}, max_photons=2, max_prongs=12)
        result = budget.typed_bracket(source, 33)
        self.assertAlmostEqual(result["binds_at_least"], 0.10)

    def test_upper_bound_uses_this_files_maxima(self):
        """Headroom is 1 muon + observed max photons + observed max prongs."""
        # cap 33, headroom 1+2+12=15 => upper threshold 18.
        source = _source({17: 50, 18: 30, 33: 20}, max_photons=2, max_prongs=12)
        result = budget.typed_bracket(source, 33)
        self.assertAlmostEqual(result["binds_at_least"], 0.20)
        self.assertAlmostEqual(result["binds_at_most"], 0.50)

    def test_upper_bound_is_never_below_the_lower_bound(self):
        source = _source({1: 10, 40: 90}, max_photons=0, max_prongs=0)
        result = budget.typed_bracket(source, 33)
        self.assertGreaterEqual(result["binds_at_most"], result["binds_at_least"])

    def test_smaller_headroom_gives_a_tighter_bracket(self):
        """A file with fewer photons/prongs must not widen the interval."""
        wide = budget.typed_bracket(_source({18: 40, 33: 60}, 2, 12), 33)
        tight = budget.typed_bracket(_source({18: 40, 33: 60}, 0, 0), 33)
        self.assertLessEqual(
            tight["binds_at_most"] - tight["binds_at_least"],
            wide["binds_at_most"] - wide["binds_at_least"],
        )


class Receipt(unittest.TestCase):
    def test_rejects_a_receipt_with_a_different_cap(self):
        """The whole comparison is against the 12-token cap; a 16 would silently lie."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.json"
            src.write_text(json.dumps({"cap": 16, "sources": []}))
            out = Path(tmp) / "out.json"
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("measure_typed_object_budget.py")),
                 "--source-receipt", str(src), "--output", str(out)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("expected 12", proc.stderr)
            self.assertFalse(out.exists())

    def test_qualifications_survive_into_the_output(self):
        """The unselected-population caveat must travel with the numbers."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source.json"
            src.write_text(json.dumps(
                {"cap": 12, "sources": [_source({5: 90, 40: 10}, 2, 12)]}))
            out = Path(tmp) / "out.json"
            subprocess.run(
                [sys.executable, str(Path(__file__).with_name("measure_typed_object_budget.py")),
                 "--source-receipt", str(src), "--output", str(out)],
                check=True, capture_output=True, text=True,
            )
            written = json.loads(out.read_text())
            joined = " ".join(written["qualifications"])
            self.assertIn("UNSELECTED", joined)
            self.assertIn("NOT measured here", joined)
            self.assertEqual(len(written["rows"]), 1)


if __name__ == "__main__":
    unittest.main()
