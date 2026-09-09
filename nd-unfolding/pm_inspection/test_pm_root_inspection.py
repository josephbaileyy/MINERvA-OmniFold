#!/usr/bin/env python3
"""Focused tests for the bounded ROOT inspection producer and validator.

MUTATION TESTS ARE THE POINT.  Every defect that review found in an earlier revision is
pinned here by a test that FAILS if the defect returns: an empty capture reading COMPLETE,
an unknown status passing, an unreadable optional counting as the declared absence, the
validator trusting the producer's own obligation list, a stale report satisfying a
fixed-path read, a symlinked output directory landing inside a checkout, an invented mask
digest, and a declared grid size reported as a measured one.

THE FIXTURES DO NOT CALL THE RULES THEY TEST.  Round 4 of review measured what that costs:
``payloaded()`` used to build each record by calling ``validator.payload_fields_for()``, so
emptying seven of the eight payload branches left all 44 tests green -- the fixture moved
with the rule and could not disagree with it.  The obligation table, each obligation's
kind, the payload branch each read falls in, and the payload values themselves are now
restated here from ``PREDECLARATION-20260906-pm-root-inspection.md`` sections 3-4.  Two
statements that must agree is the whole point; one statement asked twice is not a test.

AND THE FIXTURE MUST CARRY THE WHOLE PAYLOAD, WHICH IS WHERE ROUND 4 STOPPED SHORT.  Its
report SECTIONS stayed four hand-written stubs -- ``{"key_count": 13}``, one endpoint out
of ten, no TKey listing, no axis edges and no digest anywhere -- so a rule requiring any of
those could not fail against this suite, and round 5 reproduced four classes that walked
straight through it.  ``sections_from()`` now builds every nested section the producer
writes, from ``section_path()``, ``SYNTHETIC_KEY_LISTING`` and ``SYNTHETIC_AXIS_EDGES``,
which are this file's restatement of PREDECLARATION section 4 (what each read produces) and
section 7 (the listings and every computed digest are preserved outputs).  Nothing in the
fixture is read out of ``pm_root_validate``.

The innocent cases are here for the same reason: a validator that refuses everything is not
correct either, and the expected-optional absence must keep passing.

None of these needs ROOT or any real input.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
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

# --------------------------------------------------------------------------------------
# The predeclaration, restated. Nothing below is read out of the validator or the producer.
# --------------------------------------------------------------------------------------

#: PREDECLARATION section 3: every input file, keyed by the read id that opens it.
BINDING_BY_READ_ID = {f"input:{entry['id']}": entry for entry in BINDINGS["inputs"]}

#: PREDECLARATION section 4: the conditional reads, the only ids whose absence is an answer.
G_OPTIONAL_OBJECTS = ("hRowIndex5D",)
ENDPOINT_OPTIONAL_OBJECTS = ("estimator_seed", "estimator_seed_0", "estimator_seed_1",
                             "est_seed_offset", "est_seed_offset_0", "est_seed_offset_1")
G_REQUIRED_READS = ("G:key_listing", "G:combined_source", "G:centering_convention",
                    "G:sqrt_tr_old", "G:sqrt_tr_new", "G:hInflation_g_nbins",
                    "G:read_onlyness")
AXES = ("pt", "pz", "eavail", "q3", "W")
ENDPOINT_SCALARS = ("ndim", "dataPOT", "globalCompleteness")

#: The sections a capture must carry, spelled out so that dropping one from the validator's
#: own tuple fails a test instead of silently narrowing the rule.
EXPECTED_REPORT_SECTIONS = ("G", "CS", "CV_central", "endpoints", "G_read_onlyness",
                            "module_provenance", "root_version")


def spelled_out_obligations(bindings):
    """Every declared read and the kind the predeclaration gives it, restated here."""
    kinds = {}
    for entry in bindings["inputs"]:
        kinds[f"input:{entry['id']}"] = REQUIRED
    for read_id in G_REQUIRED_READS:
        kinds[read_id] = REQUIRED
    for name in G_OPTIONAL_OBJECTS:
        kinds[f"G:{name}"] = OPTIONAL
    for read_id in ("CS:key_listing", "CV_central:key_listing",
                    "CV_central:hXSecND_flat"):
        kinds[read_id] = REQUIRED
    for band in bindings["bands"]:
        for endpoint in (0, 1):
            label = f"EP_{band}_{endpoint}"
            kinds[f"{label}:key_listing"] = REQUIRED
            kinds[f"{label}:hXSecND_flat"] = REQUIRED
            for axis in AXES:
                kinds[f"{label}:hXSec_{axis}"] = REQUIRED
            for scalar in ENDPOINT_SCALARS:
                kinds[f"{label}:{scalar}"] = REQUIRED
            for name in ENDPOINT_OPTIONAL_OBJECTS:
                kinds[f"{label}:{name}"] = OPTIONAL
    return kinds


KINDS = spelled_out_obligations(BINDINGS)
OBLIGATIONS = list(KINDS)


def payload_branch(read_id):
    """Which declared read this is. Restated, not asked of the validator."""
    if read_id.startswith("input:"):
        return "input"
    if read_id.endswith(":key_listing"):
        return "key_listing"
    if read_id.endswith(":hXSecND_flat"):
        return "flat_histogram"
    if read_id == "G:hInflation_g_nbins":
        return "inflation_nbins"
    if read_id == "G:read_onlyness":
        return "read_onlyness"
    if ":hXSec_" in read_id:
        return "axis_histogram"
    if read_id == "G:hRowIndex5D":
        return "row_index"
    return "stored_scalar"


def section_path(read_id):
    """Where the report PRESERVES this read's product. Restated from the predeclaration.

    Section 4 names what each read produces and section 7 lists the key listings and every
    computed digest among the outputs to be preserved, so each obligation has a place in
    the report that its measurement has to occupy. An input read has none: its whole
    measurement is the record.
    """
    if read_id.startswith("input:"):
        return ()
    if read_id == "G:read_onlyness":
        return ("G_read_onlyness",)
    owner, _, name = read_id.partition(":")
    if owner in ("G", "CS", "CV_central"):
        return (owner, name)
    return ("endpoints", owner, name)


#: What a ``status="read"`` record of each branch MUST carry. The row-index branch is the
#: readable case; the undigestible case is a contradiction, tested separately. The input
#: branch is completed per input by ``expected_payload_fields``, because which digest
#: field a record carries is that input's OWN binding policy.
EXPECTED_PAYLOAD_FIELDS = {
    "input": ("path", "size_bytes", "digest_provenance", "digest_verified"),
    "key_listing": ("key_count",),
    "flat_histogram": ("row_index_sha256", "reported_mask_hash", "count",
                       "measured_nbins", "declared_nbins", "nbins_conforms",
                       "all_finite", "content_sha256"),
    "inflation_nbins": ("nbins",),
    "read_onlyness": ("sha256_before", "sha256_after", "unchanged"),
    "axis_histogram": ("nbins", "first_edge", "last_edge"),
    "row_index": ("present", "contents_readable", "count", "row_index_sha256",
                  "reported_mask_hash"),
    "stored_scalar": ("value",),
}


def expected_payload_fields(read_id):
    """The record fields this read must carry, including its binding's digest policy.

    PREDECLARATION section 4 excludes a full sha256 of CS -- 41.4 GB -- and the bindings
    carry that as ``verify_digest_at_runtime: false`` with the historical
    ``support_family_sha256``. A re-hashed input therefore records a MEASURED ``sha256``
    and a CS-like input records the bound digest it did not verify. Those are two
    different measurements and the fixture spells both.
    """
    if read_id.startswith("input:"):
        binding = BINDING_BY_READ_ID[read_id]
        measured = ("sha256",) if binding["verify_digest_at_runtime"] else (
            "sha256_bound_not_verified",)
        return EXPECTED_PAYLOAD_FIELDS["input"] + measured
    return EXPECTED_PAYLOAD_FIELDS[payload_branch(read_id)]


#: PREDECLARATION section 4 read 1: "top-level TKey NAMES, CLASSES and CYCLES". Thirteen
#: of them, G's committed inventory (section 5). Two entries share a name and differ in
#: cycle, which is why the cycle is part of the declared read and not decoration.
SYNTHETIC_KEY_LISTING = [
    {"name": "centering_convention", "class": "TNamed", "cycle": 1},
    {"name": "combined_source", "class": "TNamed", "cycle": 1},
    {"name": "dataPOT", "class": "TParameter<double>", "cycle": 1},
    {"name": "globalCompleteness", "class": "TParameter<double>", "cycle": 1},
    {"name": "hCov_stamped5d_total", "class": "TH2D", "cycle": 1},
    {"name": "hInflation_g", "class": "TH1D", "cycle": 1},
    {"name": "hXSec_eavail", "class": "TH1D", "cycle": 1},
    {"name": "hXSec_pt", "class": "TH1D", "cycle": 1},
    {"name": "hXSec_pz", "class": "TH1D", "cycle": 1},
    {"name": "ndim", "class": "TNamed", "cycle": 1},
    {"name": "sqrt_tr_new", "class": "TParameter<double>", "cycle": 1},
    {"name": "sqrt_tr_old", "class": "TParameter<double>", "cycle": 1},
    {"name": "stamp_utc", "class": "TNamed", "cycle": 2},
]

#: PREDECLARATION section 4 read 4: the axis edges INCLUDING the final upper edge, so an
#: axis of n bins has n+1 of them. The record's nbins/first_edge/last_edge are derived
#: from this one literal, which is what makes them agree by construction.
SYNTHETIC_AXIS_EDGES = [0.0, 1.5, 3.0, 5.0, 7.5]

#: One literal, internally consistent value per payload field. ``first_edge`` is 0.0 on
#: purpose: a legitimately-zero numeric must pass, while an empty digest must not.
LITERAL_PAYLOAD_VALUES = {
    "key_count": len(SYNTHETIC_KEY_LISTING),
    "row_index_sha256": "a" * 64,
    "reported_mask_hash": "b" * 64,
    "content_sha256": "c" * 64,
    "count": 3,
    "measured_nbins": 65856,
    "declared_nbins": 65856,
    "nbins_conforms": True,
    "all_finite": True,
    "nbins": len(SYNTHETIC_AXIS_EDGES) - 1,
    "sha256_before": "d" * 64,
    "sha256_after": "d" * 64,
    "first_edge": SYNTHETIC_AXIS_EDGES[0],
    "last_edge": SYNTHETIC_AXIS_EDGES[-1],
    "unchanged": True,
    "present": True,
    "contents_readable": True,
    "value": 1.5,
}


def input_payload(binding):
    """What an ``input:`` record measures, from PREDECLARATION section 3 and the binding.

    The path is the bound tree plus the bound relpath, the size is the bound size, and the
    digest is whichever of the two the binding's own policy names. Nothing here is asked
    of the validator: it is read out of the committed bindings.
    """
    fields = {
        "path": os.path.join(BINDINGS["data_root"], binding["relpath"]),
        "size_bytes": binding["size_bytes"],
        "digest_provenance": binding["digest_provenance"],
        "digest_verified": bool(binding["verify_digest_at_runtime"]),
    }
    if binding["verify_digest_at_runtime"]:
        fields["sha256"] = binding["sha256"]
    else:
        fields["sha256_bound_not_verified"] = binding["sha256"]
    return fields


def literal_payload_value(read_id, field):
    if read_id.startswith("input:"):
        return input_payload(BINDING_BY_READ_ID[read_id])[field]
    return LITERAL_PAYLOAD_VALUES[field]


def payloaded(read_id, status="read", kind=None, **overrides):
    """A record carrying literal values for the payload its read is required to produce."""
    entry = {"read_id": read_id, "status": status,
             "kind": kind if kind is not None else KINDS[read_id]}
    if status == "read":
        for field in expected_payload_fields(read_id):
            entry[field] = literal_payload_value(read_id, field)
    entry.update(overrides)
    return entry


def a_whole_number(value):
    return isinstance(value, int) and not isinstance(value, bool)


def nested_capture(read_id, entry):
    """The product this read is declared to leave in the report, mirroring the record.

    Round 4's fixtures were built by CALLING the rule under test, so no test could detect
    a gap in either. This is built from the predeclaration's own account of what each read
    produces -- a TKey listing of names, classes and cycles; the complete axis edges; the
    digests -- and from the record the producer would have written beside it, never from
    ``pm_root_validate``. Mirroring the record is what the producer literally does: it
    records one measurement dict and stores the same dict in the section.
    """
    branch = payload_branch(read_id)
    if branch == "key_listing":
        count = entry.get("key_count")
        if a_whole_number(count) and 0 <= count <= len(SYNTHETIC_KEY_LISTING):
            return SYNTHETIC_KEY_LISTING[:count]
        return list(SYNTHETIC_KEY_LISTING)
    if branch == "axis_histogram":
        capture = {"edges": list(SYNTHETIC_AXIS_EDGES)}
        if "nbins" in entry:
            capture["nbins"] = entry["nbins"]
        return capture
    if branch in ("flat_histogram", "read_onlyness", "row_index"):
        # The row index's yes/no answer is stored beside the contents at
        # `hRowIndex5D_present`, not inside them, so it is not part of this mapping.
        return {field: entry[field]
                for field in EXPECTED_PAYLOAD_FIELDS[branch]
                if field in entry and not (branch == "row_index" and field == "present")}
    if branch == "inflation_nbins":
        return entry.get("nbins")
    return entry.get("value")


def place(document, path, value):
    node = document
    for step in path[:-1]:
        node = node.setdefault(step, {})
    node[path[-1]] = value


def sections_from(reads):
    """The five nested sections, carrying the product of every read that happened.

    The old fixture's sections were four hand-written stubs -- ``{"key_count": 13}``,
    ``{"key_count": 4}``, one endpoint out of ten -- with no listing, no edges and no
    digest anywhere in them. A rule requiring any of those could not fail against it,
    which is precisely how round 5's first class walked through five rounds of repair.
    """
    sections = {"G": {}, "CS": {}, "CV_central": {}, "endpoints": {},
                "G_read_onlyness": {}}
    for entry in reads:
        read_id = entry.get("read_id")
        if read_id not in KINDS:
            continue
        path = section_path(read_id)
        if not path:
            continue
        status = entry.get("status")
        if payload_branch(read_id) == "row_index" and status in ("read", "absent"):
            # G's declared conditional read: "settle whether G carries a row index at
            # all", so the answer is preserved either way.
            place(sections, path[:-1] + (path[-1] + "_present",), entry.get("present"))
        if status == "read":
            place(sections, path, nested_capture(read_id, entry))
    return sections


def module_provenance_capture(extra_modules=None):
    """What ``module_provenance()`` measures: the per-module file MAP, plus a summary.

    The map is the measurement and ``modules_loaded_from_forbidden_root`` is the
    producer's account of it, so the fixture carries both and derives the second from the
    first exactly as the producer does.
    """
    modules = {
        "hashlib": "/opt/python/lib/python3.12/hashlib.py",
        "json": "/opt/python/lib/python3.12/json/__init__.py",
        "pm_root_inspect": str(HERE / "pm_root_inspect.py"),
    }
    modules.update(extra_modules or {})
    prefix = BINDINGS["data_root"].rstrip("/") + "/"
    return {
        "forbidden_root": BINDINGS["data_root"],
        "modules": modules,
        "module_count": len(modules),
        "modules_loaded_from_forbidden_root": sorted(
            name for name, filename in modules.items() if filename.startswith(prefix)),
    }


def report(reads, attempt_id=ATTEMPT, **extra):
    """An otherwise-intact report whose sections carry the FULL declared payload."""
    base = {
        "attempt_id": attempt_id,
        "reads": reads,
        "declared_read_ids": list(OBLIGATIONS),
        "data_root": BINDINGS["data_root"],
        "module_provenance": module_provenance_capture(),
        "root_version": "6.28/12",
    }
    base.update(sections_from(reads))
    base.update(extra)
    return base


def full_capture():
    """An innocent report: every obligation recorded with its bound kind and payload."""
    return report([payloaded(rid) for rid in OBLIGATIONS])


def capture_with(read_id, **changes):
    """A full capture in which exactly one record has been changed."""
    reads = [payloaded(rid) for rid in OBLIGATIONS if rid != read_id]
    reads.append(payloaded(read_id, **changes))
    return report(reads)


REQUIREMENTS = validator.obligation_requirements(BINDINGS)


class ThePredeclarationIsTheAuthority(unittest.TestCase):
    """The rules under test must match this file's independent restatement of them."""

    def test_validator_obligations_match_the_predeclaration(self):
        self.assertEqual(validator.obligation_kinds(BINDINGS), KINDS)

    def test_producer_obligations_match_the_predeclaration(self):
        """Producer and validator now hold separate tables; they must still agree."""
        self.assertEqual(producer.obligation_kinds(BINDINGS), KINDS)

    def test_required_sections_are_the_seven_declared_ones(self):
        self.assertEqual(validator.REQUIRED_REPORT_SECTIONS, EXPECTED_REPORT_SECTIONS)

    def test_every_obligation_requires_the_payload_its_read_measures(self):
        """Emptying any payload branch fails here, which is what round 4 could not do."""
        for read_id in OBLIGATIONS:
            branch = payload_branch(read_id)
            with self.subTest(read_id=read_id, branch=branch):
                self.assertEqual(
                    set(validator.required_record_fields(REQUIREMENTS[read_id],
                                                         payloaded(read_id))),
                    set(expected_payload_fields(read_id)))

    def test_every_obligation_preserves_its_read_in_the_declared_section(self):
        """The nested capture each read leaves behind, restated independently. A rule
        that names the wrong place cannot detect an emptied one."""
        for read_id in OBLIGATIONS:
            with self.subTest(read_id=read_id):
                self.assertEqual(REQUIREMENTS[read_id].section_path,
                                 section_path(read_id))

    def test_every_input_is_matched_against_its_own_binding_policy(self):
        """CS's no-rehash branch and the twelve re-hashed inputs are different records."""
        for read_id, binding in BINDING_BY_READ_ID.items():
            with self.subTest(read_id=read_id):
                self.assertEqual(
                    set(validator.required_record_fields(REQUIREMENTS[read_id],
                                                         payloaded(read_id))),
                    set(expected_payload_fields(read_id)))
        self.assertIn("sha256_bound_not_verified", expected_payload_fields("input:CS"))
        self.assertIn("sha256", expected_payload_fields("input:G"))

    def test_every_payload_branch_is_exercised_by_some_obligation(self):
        covered = {payload_branch(read_id) for read_id in OBLIGATIONS}
        self.assertEqual(covered, set(EXPECTED_PAYLOAD_FIELDS))


class InnocentCapturesPass(unittest.TestCase):
    def test_full_capture_is_COMPLETE(self):
        code, findings = validator.classify(full_capture(), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)

    def test_expected_optional_absence_is_still_COMPLETE(self):
        """hRowIndex5D absent from G is the ANSWER, and must not become a fault."""
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "absent", "kind": OPTIONAL,
                      "present": False})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)
        self.assertEqual(findings["expected_optional_absences"], ["G:hRowIndex5D"])

    def test_a_legitimately_zero_number_is_a_measurement(self):
        """0 non-zero bins, or a first edge at 0.0, is a real answer. An empty digest is
        never one, which is why the two are not treated alike."""
        doc = capture_with("CV_central:hXSecND_flat", count=0)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)

    def test_a_false_boolean_measurement_is_not_a_missing_one(self):
        """nbins_conforms=False is a measured grid non-conformance, not a capture gap.
        Faulting on its VALUE would be an acceptance threshold; the validator has none."""
        doc = capture_with("CV_central:hXSecND_flat", nbins_conforms=False,
                           measured_nbins=4)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)


class MutationsThatMustNotPass(unittest.TestCase):
    def test_empty_capture_is_not_COMPLETE(self):
        code, findings = validator.classify(report([]), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("empty capture", findings["reason"])

    def test_producer_cannot_shrink_its_own_obligations(self):
        """A report claiming only one declared read must not thereby become COMPLETE.

        The declaration mismatch is itself the fault: the records may all be missing as
        well, but a producer that disagrees with the committed bindings about what it was
        supposed to read has already failed, so this is ERROR and not INCOMPLETE.
        """
        doc = report([payloaded("G:key_listing")])
        doc["declared_read_ids"] = ["G:key_listing"]
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_declaration_disagrees_with_bindings"])
        self.assertGreater(len(findings["missing_read_records"]), 1)

    def test_a_declared_read_that_does_not_exist_is_a_fault(self):
        """The only cross-check on producer/validator skew must reach the verdict."""
        doc = full_capture()
        doc["declared_read_ids"] = list(OBLIGATIONS) + ["a-read-that-does-not-exist"]
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_declaration_disagrees_with_bindings"])

    def test_a_record_for_an_undeclared_read_is_a_fault(self):
        """The mirror of the declaration cross-check: a measurement nobody asked for is
        the same report/bindings disagreement as a declaration nobody can perform."""
        reads = [payloaded(rid) for rid in OBLIGATIONS]
        reads.append({"read_id": "G:hSomethingNobodyDeclared", "status": "read",
                      "kind": REQUIRED, "value": 1.0})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["records_for_reads_the_bindings_do_not_declare"],
                         ["G:hSomethingNobodyDeclared"])

    def test_stale_report_from_another_attempt_is_refused(self):
        code, findings = validator.classify(full_capture(), BINDINGS, "a-different-attempt")
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("not bound to this attempt", findings["reason"])

    def test_unknown_status_is_a_fault(self):
        doc = capture_with(OBLIGATIONS[0], status="probably-fine")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["records_with_unknown_status"], [OBLIGATIONS[0]])

    def test_unknown_kind_is_a_fault(self):
        doc = capture_with(OBLIGATIONS[0], kind="sort-of-required")
        code, _ = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)

    def test_unreadable_optional_is_a_fault_not_the_declared_absence(self):
        """Listed-but-unreadable is not 'we learned it is absent'."""
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "unreadable",
                      "kind": OPTIONAL})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["unreadable_optional_objects"], ["G:hRowIndex5D"])
        self.assertEqual(findings["expected_optional_absences"], [])

    def test_a_record_cannot_reclassify_its_own_obligation(self):
        """Relabelling a required id as expected-optional must not buy COMPLETE."""
        reads = [payloaded(rid) for rid in OBLIGATIONS]
        reads[0] = {"read_id": OBLIGATIONS[0], "status": "absent", "kind": OPTIONAL}
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn(OBLIGATIONS[0],
                      findings["records_whose_kind_contradicts_bindings"])
        self.assertIn(OBLIGATIONS[0], findings["required_read_failures"])

    def test_a_kind_disagreement_alone_is_a_fault(self):
        """With no other defect in the report, the kind disagreement must still be ERROR:
        removing it from the faults expression left the whole suite green in round 4."""
        doc = capture_with("G:hRowIndex5D", kind=REQUIRED)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(findings["records_whose_kind_contradicts_bindings"],
                         ["G:hRowIndex5D"])
        self.assertEqual(findings["required_read_failures"], [])
        self.assertEqual(findings["reads_missing_payload"], [])
        self.assertEqual(code, validator.EXIT_ERROR)

    def test_wrong_bindings_digest_is_ERROR(self):
        code, findings = validator.classify(full_capture(), BINDINGS, ATTEMPT,
                                            bindings_sha256="wrong")
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("different bindings bytes", findings["reason"])

    def test_required_failure_is_ERROR(self):
        doc = capture_with(OBLIGATIONS[0], status="unreadable")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["required_read_failures"], [OBLIGATIONS[0]])

    def test_producer_traceback_is_ERROR_even_with_a_full_capture(self):
        doc = full_capture()
        doc["traceback"] = "Traceback (most recent call last): ..."
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_traceback"])

    def test_producer_fatal_is_ERROR_even_with_a_full_capture(self):
        doc = full_capture()
        doc["fatal"] = "required inputs unusable: CV_central"
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["producer_fatal"])

    def test_missing_record_is_INCOMPLETE(self):
        reads = [payloaded(rid) for rid in OBLIGATIONS[:-1]]
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_INCOMPLETE)
        self.assertEqual(findings["missing_read_records"], [OBLIGATIONS[-1]])


class EveryPayloadBranchMustCarryItsMeasurement(unittest.TestCase):
    """One test per branch, each failing if THAT branch's rule is emptied.

    Round 4 emptied seven of the eight branches one at a time and the suite stayed green,
    because the fixture was built by calling the rule. These strip the fields this file
    says the branch must carry, and require the verdict -- not just the finding list -- to
    change.
    """

    #: A row index that says its contents were unreadable is not required to carry the
    #: digest of contents it could not read -- it is a contradiction, tested separately --
    #: so this one field stays, and the digest stays required because of it.
    KEEP = {"row_index": {"contents_readable": True}}

    def _strip(self, branch):
        reads = []
        stripped = []
        keep = self.KEEP.get(branch, {})
        for read_id in OBLIGATIONS:
            entry = payloaded(read_id)
            if payload_branch(read_id) == branch:
                for field in expected_payload_fields(read_id):
                    if field in keep:
                        continue
                    entry.pop(field, None)
                    stripped.append(f"{read_id}:{field}")
            reads.append(entry)
        self.assertTrue(stripped, f"no obligation falls in branch {branch}")
        return report(reads), stripped

    def _assert_branch_is_pinned(self, branch):
        doc, stripped = self._strip(branch)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        for entry in stripped:
            self.assertIn(entry, findings["reads_missing_payload"])

    def test_input_branch(self):
        self._assert_branch_is_pinned("input")

    def test_key_listing_branch(self):
        self._assert_branch_is_pinned("key_listing")

    def test_flat_histogram_branch(self):
        self._assert_branch_is_pinned("flat_histogram")

    def test_inflation_nbins_branch(self):
        self._assert_branch_is_pinned("inflation_nbins")

    def test_read_onlyness_branch(self):
        self._assert_branch_is_pinned("read_onlyness")

    def test_axis_histogram_branch(self):
        self._assert_branch_is_pinned("axis_histogram")

    def test_row_index_branch(self):
        self._assert_branch_is_pinned("row_index")

    def test_stored_scalar_branch(self):
        self._assert_branch_is_pinned("stored_scalar")


class EveryReadMustLeaveItsProductInTheReport(unittest.TestCase):
    """One test per branch that HAS a nested capture, each failing if that branch's rule
    is dropped from the validator.

    This is what the repaired fixture buys. The old ``report()`` carried four hand-written
    section stubs -- no listing, no edges, no digest, one endpoint out of ten -- so a rule
    requiring any of those could not fail against it, and round 5's first class walked
    through five rounds of record-side repair. The sections here are built from this
    file's restatement of PREDECLARATION sections 4 and 7, and the validator is never
    asked what they should contain.
    """

    BRANCHES_WITH_A_SECTION = ("key_listing", "flat_histogram", "inflation_nbins",
                               "read_onlyness", "axis_histogram", "row_index",
                               "stored_scalar")

    def _drop(self, branch):
        doc = full_capture()
        dropped = []
        for read_id in OBLIGATIONS:
            if payload_branch(read_id) != branch:
                continue
            path = section_path(read_id)
            found, node = validator.dig(doc, path[:-1])
            if found and isinstance(node, dict) and path[-1] in node:
                del node[path[-1]]
                dropped.append(read_id)
        self.assertTrue(dropped, f"no obligation falls in branch {branch}")
        return doc, dropped

    def test_every_branch_with_a_section_is_pinned_one_at_a_time(self):
        for branch in self.BRANCHES_WITH_A_SECTION:
            with self.subTest(branch=branch):
                doc, dropped = self._drop(branch)
                code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
                self.assertEqual(code, validator.EXIT_ERROR)
                self.assertEqual(findings["reads_missing_payload"], [],
                                 "the RECORDS are intact; only the products are gone")
                for read_id in dropped:
                    self.assertIn(read_id, findings["reads_missing_nested_capture"])

    def test_every_branch_with_a_section_is_covered_by_some_obligation(self):
        covered = {payload_branch(read_id) for read_id in OBLIGATIONS
                   if section_path(read_id)}
        self.assertEqual(covered, set(self.BRANCHES_WITH_A_SECTION))

    def test_a_nonempty_mapping_is_not_a_section(self):
        """`{"lost": true}` passes every shape rule round 4 added."""
        for section in ("G", "CS", "CV_central", "endpoints"):
            with self.subTest(section=section):
                doc = full_capture()
                doc[section] = {"lost": True}
                code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
                self.assertEqual(code, validator.EXIT_ERROR)
                self.assertEqual(findings["missing_report_sections"], [])
                self.assertTrue(findings["reads_missing_nested_capture"])

    def test_a_truncated_axis_is_not_a_complete_capture(self):
        doc = full_capture()
        doc["endpoints"]["EP_BeamAngleX_0"]["hXSec_pt"]["edges"].pop()
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("EP_BeamAngleX_0:hXSec_pt",
                      findings["reads_missing_nested_capture"])

    def test_a_listing_whose_length_disagrees_with_its_count_is_a_fault(self):
        doc = full_capture()
        doc["CS"]["key_listing"] = SYNTHETIC_KEY_LISTING[:3]
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("CS:key_listing", findings["reads_missing_nested_capture"])

    def test_the_answer_to_Gs_conditional_read_must_be_in_the_report(self):
        """hRowIndex5D absent is the ANSWER; deleting the answer is not the answer."""
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "absent", "kind": OPTIONAL,
                      "present": False})
        doc = report(reads)
        self.assertIs(doc["G"]["hRowIndex5D_present"], False)   # the control
        self.assertEqual(validator.classify(doc, BINDINGS, ATTEMPT)[0],
                         validator.EXIT_COMPLETE)
        del doc["G"]["hRowIndex5D_present"]
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("G:hRowIndex5D", findings["reads_missing_nested_capture"])


class OneDeclaredReadIsOneRecord(unittest.TestCase):
    """Two records for one declared read is two answers to one question."""

    def test_a_duplicate_record_is_a_fault(self):
        reads = [payloaded(rid) for rid in OBLIGATIONS]
        reads.append(payloaded("G:sqrt_tr_old", value=999))
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["duplicate_read_records"], ["G:sqrt_tr_old"])

    def test_the_control_has_no_duplicates(self):
        code, findings = validator.classify(full_capture(), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)
        self.assertEqual(findings["duplicate_read_records"], [])


class EmptyIsNotAMeasurement(unittest.TestCase):
    """`""`, `{}` and `[]` passed every presence check in round 4: it tested for None."""

    def test_an_empty_digest_is_not_a_capture(self):
        doc = capture_with("CV_central:hXSecND_flat", row_index_sha256="")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("CV_central:hXSecND_flat:row_index_sha256",
                      findings["reads_missing_payload"])

    def test_a_whitespace_only_text_field_is_not_a_capture(self):
        doc = capture_with("input:G", digest_provenance="   ")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("input:G:digest_provenance", findings["reads_missing_payload"])

    def test_a_number_where_a_digest_belongs_is_not_a_capture(self):
        """The round-3 fixture put 1 in every field, digests included."""
        doc = capture_with("CV_central:hXSecND_flat", content_sha256=1)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("CV_central:hXSecND_flat:content_sha256",
                      findings["reads_missing_payload"])

    def test_a_string_where_a_count_belongs_is_not_a_capture(self):
        doc = capture_with("G:key_listing", key_count="thirteen")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("G:key_listing:key_count", findings["reads_missing_payload"])

    def test_a_digest_that_is_not_a_digest_is_not_a_capture(self):
        doc = capture_with("CV_central:hXSecND_flat", content_sha256="deadbeef")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("CV_central:hXSecND_flat:content_sha256",
                      findings["reads_missing_payload"])

    def test_an_empty_scalar_value_is_not_a_capture(self):
        doc = capture_with("G:combined_source", value="")
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("G:combined_source:value", findings["reads_missing_payload"])

    def test_every_required_section_is_pinned_one_at_a_time(self):
        """Dropping any single section from the validator's tuple fails here."""
        for section in EXPECTED_REPORT_SECTIONS:
            with self.subTest(section=section):
                doc = full_capture()
                doc.pop(section)
                code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
                self.assertEqual(code, validator.EXIT_ERROR)
                self.assertIn(section, findings["missing_report_sections"])

    def test_an_empty_section_is_as_absent_as_a_missing_one(self):
        for section in EXPECTED_REPORT_SECTIONS:
            with self.subTest(section=section):
                doc = full_capture()
                doc[section] = {} if section != "root_version" else ""
                code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
                self.assertEqual(code, validator.EXIT_ERROR)
                self.assertIn(section, findings["missing_report_sections"])

    def test_sections_alone_carry_the_verdict(self):
        """With every record payload intact, emptying the sections must still be ERROR:
        removing missing_sections from the faults expression must not be survivable."""
        doc = full_capture()
        for section in EXPECTED_REPORT_SECTIONS:
            doc[section] = {}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(findings["reads_missing_payload"], [])
        self.assertEqual(list(findings["missing_report_sections"]),
                         list(EXPECTED_REPORT_SECTIONS))
        self.assertEqual(code, validator.EXIT_ERROR)

    def test_the_whole_round_four_reproducer(self):
        """Every digest "", every count 0, every section {}: review got COMPLETE."""
        doc = full_capture()
        for section in EXPECTED_REPORT_SECTIONS:
            doc[section] = {}
        for entry in doc["reads"]:
            for field in expected_payload_fields(entry["read_id"]):
                value = literal_payload_value(entry["read_id"], field)
                entry[field] = 0 if isinstance(value, (int, float)) else ""
        code, _ = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)


class ARecordMustAgreeWithItself(unittest.TestCase):
    """Consistency between fields the producer already wrote. Not a threshold: no field's
    VALUE is judged, only whether it contradicts another field in the same record."""

    def test_G_changing_across_the_inspection_is_a_fault(self):
        doc = capture_with("G:read_onlyness", sha256_after="e" * 64, unchanged=False)
        doc["G_read_onlyness"] = {"sha256_before": "d" * 64, "sha256_after": "e" * 64,
                                  "unchanged": False}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["source_artifact_changed_during_the_inspection"])

    def test_unchanged_must_equal_the_digest_comparison(self):
        """The producer's summary of the measurement cannot outrank the measurement."""
        doc = capture_with("G:read_onlyness", sha256_after="e" * 64, unchanged=True)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(any("read_onlyness" in item for item
                            in findings["records_contradicting_their_own_measurement"]))

    def test_the_read_onlyness_section_must_agree_with_the_record(self):
        doc = full_capture()
        doc["G_read_onlyness"] = {"sha256_before": "d" * 64, "sha256_after": "e" * 64,
                                  "unchanged": False}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["source_artifact_changed_during_the_inspection"])

    def test_status_read_must_mean_present(self):
        doc = capture_with("G:hRowIndex5D", present=False)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_status_absent_must_not_mean_present(self):
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "absent", "kind": OPTIONAL,
                      "present": True})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_a_row_index_that_loaded_but_could_not_be_digested_is_a_fault(self):
        """The object PM-4's premise turns on: it loads, exposes neither GetNbinsX nor
        GetSize, and round 4 classified that as a measurement."""
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "read", "kind": OPTIONAL,
                      "present": True, "contents_readable": False,
                      "detail": "object exposes neither GetNbinsX nor GetSize"})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_a_present_row_index_must_carry_its_digest(self):
        reads = [payloaded(rid) for rid in OBLIGATIONS if rid != "G:hRowIndex5D"]
        reads.append({"read_id": "G:hRowIndex5D", "status": "read", "kind": OPTIONAL,
                      "present": True, "contents_readable": True})
        code, findings = validator.classify(report(reads), BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("G:hRowIndex5D:row_index_sha256", findings["reads_missing_payload"])

    def test_nbins_conforms_must_equal_the_two_numbers_beside_it(self):
        """Hardcoding nbins_conforms=True over a measured non-conformance is caught here;
        the VALUE of nbins_conforms is still never judged."""
        doc = capture_with("CV_central:hXSecND_flat", measured_nbins=4,
                           nbins_conforms=True)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_a_count_cannot_exceed_the_bins_it_was_counted_over(self):
        doc = capture_with("CV_central:hXSecND_flat", count=70000)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_the_two_mask_digests_cannot_be_the_same_bytes(self):
        """One is sha256(idx), the other sha256(idx + b"|C"); equality means one was
        copied into the other."""
        doc = capture_with("CV_central:hXSecND_flat", reported_mask_hash="a" * 64)
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])


class TheCaptureMustComeFromTheBoundTree(unittest.TestCase):
    def test_a_report_from_another_data_root_is_a_fault(self):
        doc = full_capture()
        doc["data_root"] = "/tmp/some-other-tree"
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["data_root_disagrees_with_bindings"])

    def test_a_trailing_slash_is_not_a_different_tree(self):
        doc = full_capture()
        doc["data_root"] = BINDINGS["data_root"] + "/"
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_COMPLETE, findings)

    def test_a_contamination_measurement_aimed_elsewhere_is_a_fault(self):
        """A forbidden_root that is not the bound tree measures nothing about the bound
        tree, so the offender list being empty says nothing either."""
        doc = full_capture()
        doc["module_provenance"] = {"forbidden_root": "/tmp/somewhere-harmless",
                                    "modules_loaded_from_forbidden_root": []}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["contamination_measurement_aimed_at_the_wrong_tree"])

    def test_a_populated_offender_list_is_a_fault(self):
        doc = full_capture()
        doc["module_provenance"] = {
            "forbidden_root": BINDINGS["data_root"],
            "modules_loaded_from_forbidden_root": ["p4_lib"]}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertEqual(findings["modules_loaded_from_the_forbidden_root"], ["p4_lib"])

    def test_a_missing_offender_list_is_a_fault(self):
        """Deleting the measurement must not read the same as measuring no offenders."""
        doc = full_capture()
        doc["module_provenance"] = {"forbidden_root": BINDINGS["data_root"]}
        code, findings = validator.classify(doc, BINDINGS, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertTrue(findings["records_contradicting_their_own_measurement"])

    def test_bindings_without_a_data_root_cannot_ground_the_check(self):
        bindings = dict(BINDINGS)
        bindings.pop("data_root")
        code, findings = validator.classify(full_capture(), bindings, ATTEMPT)
        self.assertEqual(code, validator.EXIT_ERROR)
        self.assertIn("data_root", findings["reason"])


class TheValidatorDoesNotImportTheProducer(unittest.TestCase):
    """Round 2 moved the obligation table out of the producer's DATA. It stayed in the
    producer's CODE, and the validator imported it, so producer/validator skew was
    invisible. The two tables are now separate statements that a test compares."""

    def test_the_validator_classifies_with_the_producer_unimportable(self):
        """A subprocess is the only place this is measurable: in this process the producer
        is already imported, so a `import pm_root_inspect` inside the validator would find
        it in sys.modules and no hook would fire. The report below is minimal on purpose --
        it only has to be well-formed enough to reach the obligation table and the whole
        record walk, which is where the import used to be."""
        script = textwrap.dedent(f"""
            import json, sys
            HERE = {str(HERE)!r}

            class RefuseTheProducer:
                def find_module(self, name, path=None):
                    if name == "pm_root_inspect":
                        raise AssertionError(
                            "the validator must not import the producer")
                def find_spec(self, name, path=None, target=None):
                    return self.find_module(name, path)

            sys.meta_path.insert(0, RefuseTheProducer())
            sys.path.insert(0, HERE)
            import pm_root_validate as validator
            bindings = json.load(open(HERE + "/INPUT-BINDINGS-20260908.json"))
            report = {{"attempt_id": "a", "data_root": bindings["data_root"],
                      "reads": [{{"read_id": "G:key_listing", "status": "read",
                                 "kind": "required", "key_count": 13}}]}}
            code, findings = validator.classify(report, bindings, "a")
            print(len(validator.obligation_kinds(bindings)), code,
                  len(findings["missing_read_records"]))
        """)
        completed = subprocess.run([sys.executable, "-c", script],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        counted, code, missing = completed.stdout.split()
        self.assertEqual(int(counted), len(OBLIGATIONS))
        self.assertEqual(int(code), validator.EXIT_ERROR)   # sections are gone
        self.assertEqual(int(missing), len(OBLIGATIONS) - 1)


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
