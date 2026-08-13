#!/usr/bin/env python3
"""Tests for the hash-bound diagnostic target override."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


PET = Path(__file__).resolve().parents[1] / "pet"
sys.path.insert(0, str(PET))

from diagnostic_target_override import resolve_precomputed_target  # noqa: E402


class DiagnosticTargetOverrideTest(unittest.TestCase):
    def test_recorded_path_is_unchanged_without_override(self):
        path, receipt = resolve_precomputed_target("/recorded/target.npy", None, None)
        self.assertEqual(path, "/recorded/target.npy")
        self.assertFalse(receipt["override_used"])

    def test_override_requires_hash(self):
        with self.assertRaises(SystemExit):
            resolve_precomputed_target("/recorded/target.npy", "/moved.npy", None)

    def test_matching_override_is_hash_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target.npy"
            target.write_bytes(b"target bytes")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            path, receipt = resolve_precomputed_target(
                "/recorded/target.npy", str(target), digest
            )
            self.assertEqual(path, str(target.resolve()))
            self.assertTrue(receipt["override_used"])
            self.assertEqual(receipt["sha256"], digest)

    def test_mismatched_override_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target.npy"
            target.write_bytes(b"target bytes")
            with self.assertRaises(SystemExit):
                resolve_precomputed_target(
                    "/recorded/target.npy", str(target), "0" * 64
                )


if __name__ == "__main__":
    unittest.main()
