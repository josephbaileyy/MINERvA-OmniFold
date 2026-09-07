#!/usr/bin/env python3
"""Focused tests for the bounded ROOT inspection producer and validator.

MUTATION TESTS ARE THE POINT.  Every defect that review found in the first revision is
pinned here by a test that FAILS if the defect returns: an empty capture reading COMPLETE,
an unknown status passing, an unreadable optional counting as the declared absence, the
validator trusting the producer's own obligation list, a stale report satisfying a
fixed-path read, a symlinked output directory landing inside a checkout, an invented mask
digest, and a declared grid size reported as a measured one.

The innocent cases are here for the same reason: a validator that refuses everything is not
correct either, and the expected-optional absence must keep passing.

None of these needs ROOT or any real input.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer  # noqa: E402
import pm_root_validate as validator  # noqa: E402

REQUIRED = validator.REQUIRED
OPTIONAL = validator.OPTIONAL
ATTEMPT = "attempt-under-test"

BINDINGS = json.loads((HERE / "INPUT-BINDINGS-20260908.json").read_text())
KINDS = producer.obligation_kinds(BINDINGS)
OBLIGATIONS = list(KINDS)


def report(reads, attempt_id=ATTEMPT, **extra):
    base = {"attempt_id": attempt_id, "reads": reads,
            "declared_read_ids": list(OBLIGATIONS)}
    base.update(extra)
    return base


def full_capture():
    """An innocent report: every obligation recorded with ITS BOUND KIND."""
    return report([{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                   for rid in OBLIGATIONS])


class InnocentCapturesPass(unittest.TestCase):
    def test_full_capture_is_COMPLETE(self):
        code, _ = validator.classify(full_capture(), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE)

    def test_expected_optional_absence_is_still_COMPLETE(self):
        """hRowIndex5D absent from G is the ANSWER, and must not become a fault."""
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "absent", "kind": OPTIONAL})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE)
        self.assertEqual(findings["expected_optional_absences"], ["G:hRowIndex5D"])


class MutationsThatMustNotPass(unittest.TestCase):
    def test_empty_capture_is_not_COMPLETE(self):
        code, findings = validator.classify(report([]), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("empty capture", findings["reason"])

    def test_producer_cannot_shrink_its_own_obligations(self):
        """A report claiming only one declared read must not thereby become COMPLETE."""
        doc = report([{"read_id": "G:key_listing", "status": "read",
                       "kind": KINDS["G:key_listing"]}])
        doc["declared_read_ids"] = ["G:key_listing"]
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_INCOMPLETE)
        self.assertTrue(findings["producer_declaration_disagrees_with_bindings"])
        self.assertGreater(len(findings["missing_read_records"]), 1)

    def test_stale_report_from_another_attempt_is_refused(self):
        code, findings = validator.classify(full_capture(), BINDINGS, "a-different-attempt")
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("not bound to this attempt", findings["reason"])

    def test_unknown_status_is_a_fault(self):
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS]
        reads[0] = dict(reads[0], status="probably-fine")
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["records_with_unknown_status"], [OBLIGATIONS[0]])

    def test_unknown_kind_is_a_fault(self):
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS]
        reads[0] = dict(reads[0], kind="sort-of-required")
        code, _ = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)

    def test_unreadable_optional_is_a_fault_not_the_declared_absence(self):
        """Listed-but-unreadable is not 'we learned it is absent'."""
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "unreadable",
                      "kind": OPTIONAL})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["unreadable_optional_objects"], ["G:hRowIndex5D"])
        self.assertEqual(findings["expected_optional_absences"], [])

    def test_a_record_cannot_reclassify_its_own_obligation(self):
        """Relabelling a required id as expected-optional must not buy COMPLETE."""
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS]
        reads[0] = {"read_id": OBLIGATIONS[0], "status": "absent", "kind": OPTIONAL}
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn(OBLIGATIONS[0],
                      findings["records_whose_kind_contradicts_bindings"])
        self.assertIn(OBLIGATIONS[0], findings["required_read_failures"])

    def test_wrong_bindings_digest_is_ERROR(self):
        code, findings = validator.classify(full_capture(), BINDINGS, ATTEMPT,
                                            bindings_sha256="wrong")
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("different bindings bytes", findings["reason"])

    def test_required_failure_is_ERROR(self):
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS]
        reads[0] = dict(reads[0], status="unreadable")
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["required_read_failures"], [OBLIGATIONS[0]])

    def test_producer_traceback_is_ERROR_even_with_a_full_capture(self):
        doc = full_capture()
        doc["traceback"] = "Traceback (most recent call last): ..."
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_traceback"])

    def test_missing_record_is_INCOMPLETE(self):
        reads = [{"read_id": rid, "status": "read", "kind": KINDS[rid]}
                 for rid in OBLIGATIONS[:-1]]
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_INCOMPLETE)
        self.assertEqual(findings["missing_read_records"], [OBLIGATIONS[-1]])


class OutputLocationGuards(unittest.TestCase):
    """The reproduced bypass was link -> repo/SUBDIR, not link -> repo."""

    def _repo_with_symlinked_subdir(self, tmp):
        root = Path(tmp).resolve()
        repo = root / "repo"
        (repo / ".git").mkdir(parents=True)
        subdir = repo / "state"
        subdir.mkdir()
        link = root / "link"
        link.symlink_to(subdir, target_is_directory=True)
        return link

    def test_symlink_into_a_repo_subdirectory_is_refused_by_producer(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = self._repo_with_symlinked_subdir(tmp)
            with self.assertRaises(SystemExit):
                producer.refuse_output_inside_a_checkout(link / "run")

    def test_symlink_into_a_repo_subdirectory_is_refused_by_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = self._repo_with_symlinked_subdir(tmp)
            with self.assertRaises(SystemExit):
                validator.refuse_output_inside_a_checkout(link / "run")

    def test_relative_out_dir_is_refused(self):
        for guard in (producer.refuse_output_inside_a_checkout,
                      validator.refuse_output_inside_a_checkout):
            with self.assertRaises(SystemExit):
                guard(Path("relative/run"))

    def test_directory_outside_any_checkout_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            producer.refuse_output_inside_a_checkout(Path(tmp).resolve() / "run")
            validator.refuse_output_inside_a_checkout(Path(tmp).resolve() / "run")


class DigestAlgorithmIsTheDeclaredOne(unittest.TestCase):
    """PREDECLARATION section 4: mask = central > 0, sha256 over int64 idx bytes."""

    def setUp(self):
        import numpy as np
        self.np = np

    def test_mask_is_strictly_greater_than_zero(self):
        """`!= 0` and `> 0` differ on negative bins; the declared spelling is `> 0`."""
        central = self.np.array([1.0, 0.0, -3.0, 2.5], dtype=self.np.float64)
        digests = producer.mask_digests(central)
        self.assertEqual(digests["count"], 2)

    def test_digests_are_sha256_over_int64_index_bytes(self):
        central = self.np.array([1.0, 0.0, -3.0, 2.5, 0.0, 7.0], dtype=self.np.float64)
        idx = self.np.array([0, 3, 5], dtype=self.np.int64)
        digests = producer.mask_digests(central)
        self.assertEqual(digests["row_index_sha256"],
                         hashlib.sha256(idx.tobytes()).hexdigest())
        self.assertEqual(digests["reported_mask_hash"],
                         hashlib.sha256(idx.tobytes() + b"|C").hexdigest())

    def test_S_comparands_are_the_committed_ones(self):
        self.assertEqual(
            producer.S_REPORTED_MASK_HASH,
            "74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a")
        self.assertEqual(
            producer.S_ROW_INDEX_SHA256,
            "61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08")
        self.assertEqual(producer.S_EXPECTED_COUNT, 10694)

    def test_no_match_is_reported_when_digests_differ(self):
        central = self.np.array([1.0, 1.0], dtype=self.np.float64)
        digests = producer.mask_digests(central)
        self.assertFalse(digests["row_index_matches_S"])
        self.assertFalse(digests["reported_mask_matches_S"])
        self.assertFalse(digests["count_matches_S"])


class BindingsMatchThePredeclaration(unittest.TestCase):
    def test_thirteen_inputs_five_bands_ten_endpoints(self):
        self.assertEqual(len(BINDINGS["inputs"]), 13)
        self.assertEqual(len(BINDINGS["bands"]), 5)
        self.assertEqual(
            len([e for e in BINDINGS["inputs"] if e["id"].startswith("EP_")]), 10)

    def test_CS_is_not_hashed_at_runtime_and_says_why(self):
        cs = next(e for e in BINDINGS["inputs"] if e["id"] == "CS")
        self.assertFalse(cs["verify_digest_at_runtime"])
        self.assertIn("NOT re-hashed", cs["digest_limitation"])
        self.assertEqual(cs["digest_provenance"], "committed-historical")

    def test_current_digests_are_labelled_current(self):
        cv = next(e for e in BINDINGS["inputs"] if e["id"] == "CV_central")
        self.assertEqual(cv["digest_provenance"], "measured-current-2026-09-08")

    def test_pm4_gap_is_stated_in_the_bindings(self):
        disclaimer = BINDINGS["what_these_digests_are_NOT"]
        self.assertIn("NOT evidence", disclaimer)
        self.assertIn("PM-4 provenance gap", disclaimer)

    def test_read_onlyness_of_G_is_an_obligation(self):
        self.assertIn("G:read_onlyness", OBLIGATIONS)

    def test_obligations_are_unique_and_cover_every_input(self):
        self.assertEqual(len(OBLIGATIONS), len(set(OBLIGATIONS)))
        for entry in BINDINGS["inputs"]:
            self.assertIn(f"input:{entry['id']}", OBLIGATIONS)

    def test_grid_nbins_matches_p4_lib(self):
        self.assertEqual(BINDINGS["grid_nbins"], 65856)


if __name__ == "__main__":
    unittest.main(verbosity=2)
