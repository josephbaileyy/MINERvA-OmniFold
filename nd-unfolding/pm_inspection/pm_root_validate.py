#!/usr/bin/env python3
"""Terminal validator for the bounded ROOT inspection.

IT CLASSIFIES MEASUREMENT CAPTURE, NOT SCIENCE.  It never looks at whether a measured value
is good, expected, or sufficient, and it has no acceptance threshold, because none was
authorized and inventing one here would be inventing a scientific criterion.

IT IS REQUIREMENT-DRIVEN, AND THAT IS THE ROUND-5 REPAIR.  Five review rounds each found
one form of the same defect, and each earlier repair checked the records that were PRESENT
a little harder.  The asymmetry that kept the class alive was structural: the obligation
side was a flat id-presence set (``set(obligations) - seen``) while every content rule
walked ``reads``, so PRESENCE satisfied an obligation and CONTENT was only ever examined
from the record side.  ``classify`` now walks the OBLIGATIONS.  For each one it demands a
record, demands that record's status, demands the record payload that obligation's read
produces, and demands the NESTED capture the obligation's read is declared to preserve --
the TKey listing, the complete axis edges, the digests.  The record side is used for
exactly one thing: detecting records nobody asked for, and records asked for twice.

IT DOES NOT TRUST THE PRODUCER'S ACCOUNT OF ITS OWN OBLIGATIONS.  An earlier revision took
``declared_read_ids`` from the report, so a producer that declared nothing and read nothing
was ``COMPLETE``.  The obligation list is recomputed from the committed bindings, by this
file's own table rather than by importing the producer's, and a report is refused unless it
is bound to THIS attempt -- otherwise a stale report left at the fixed path satisfies the
read.

IT DOES NOT TRUST A RECORD'S SUMMARY OF A MEASUREMENT OVER THE MEASUREMENT BESIDE IT.  A
payload field must be non-empty and of the kind its read produces; where two fields in one
record determine each other they are compared; where a record and the report section for
the same read state the same measurement twice, the two must agree.  An input is matched
against ITS OWN committed binding rather than against its own account of itself, and the
contamination offender list is RECOMPUTED from the module map beside it rather than
believed.  Nothing here asks whether a digest is the RIGHT digest.

THE DISTINCTION THAT MATTERS.  ``hRowIndex5D`` absent from G is the ANSWER to a declared
question and is ``COMPLETE``.  A required input that is missing or digest-mismatched, a key
that is listed but unreadable, or a record with a status this validator does not model, are
all FAULTS.  Collapsing those would turn a measurement into a fault or a fault into a
measurement.

EXIT CODES, which select the contract's terminal branch:
  0   COMPLETE    every obligation has a record, and no fault
  10  INCOMPLETE  ran to the end, but an obligation has no record
  20  ERROR       fault, unbound or unreadable report, or an empty capture
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

EXIT_COMPLETE = 0
EXIT_INCOMPLETE = 10
EXIT_ERROR = 20

OPTIONAL = "expected-optional"
REQUIRED = "required"

#: The only statuses this validator models. Anything else is a fault rather than a pass,
#: because an unmodelled status is a measurement whose meaning nobody has decided.
KNOWN_STATUSES = frozenset({"read", "absent", "unreadable"})

#: Top-level sections a capture must carry. Their absence means the payloads are gone even
#: if every read record survives, which is the shape review reproduced: records stripped to
#: read_id/status/kind, sections deleted, and the whole thing still reading as COMPLETE.
#: Present-but-EMPTY is the same loss, so a section must be non-empty as well.  It is only
#: the OUTER shell: ``{"lost": true}`` is a non-empty mapping and passes here, which is why
#: every obligation separately demands its own nested capture inside these sections.
REQUIRED_REPORT_SECTIONS = (
    "G", "CS", "CV_central", "endpoints", "G_read_onlyness", "module_provenance",
    "root_version",
)

#: The one section that is a string rather than a mapping: the ROOT version ROOT reported.
SECTIONS_THAT_ARE_TEXT = frozenset({"root_version"})

SHA256_HEX = re.compile(r"[0-9a-f]{64}")

#: What KIND of value each payload field carries. The split is deliberate and it is not a
#: threshold: an EMPTY DIGEST is never a measurement, whereas a count of 0 legitimately is
#: -- zero non-zero bins is a real answer -- and ``unchanged=False`` is the measurement
#: itself rather than a missing one. So emptiness is refused where emptiness is impossible,
#: and zero and False are accepted where they are answers.
SHA256_FIELDS = frozenset({"row_index_sha256", "reported_mask_hash", "content_sha256",
                           "sha256_before", "sha256_after", "sha256",
                           "sha256_bound_not_verified"})
TEXT_FIELDS = frozenset({"path", "digest_provenance"})
NUMERIC_FIELDS = frozenset({"size_bytes", "key_count", "count", "measured_nbins",
                            "declared_nbins", "nbins", "first_edge", "last_edge"})
BOOLEAN_FIELDS = frozenset({"unchanged", "present", "contents_readable",
                            "nbins_conforms", "all_finite", "digest_verified"})


def is_number(value: object) -> bool:
    """A real number, and not a bool: ``True`` is an ``int`` and is not a count."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class Requirement(NamedTuple):
    """One obligation, and everything the bindings require of the report about it.

    ``branch`` is which declared read this is; ``record_fields`` is what its ``read``
    record must carry; ``section_path`` is where in the report the read's NESTED capture
    has to live -- the TKey listing, the axis edges, the digest mapping -- and is empty
    only for the input reads, whose whole measurement is the record.  ``binding`` is the
    committed input entry an ``input:`` read must match, including that entry's own
    digest policy.
    """

    read_id: str
    kind: str
    branch: str
    record_fields: tuple[str, ...]
    section_path: tuple[str, ...]
    binding: dict | None = None


#: What a ``status="read"`` record of each branch MUST carry, by what that read measures.
#: A record that says a read happened but carries no measurement is not a capture.  This
#: is a completeness rule, not an acceptance threshold: it asks whether the number is
#: THERE, never whether the number is right, expected, or good enough.
RECORD_FIELDS = {
    "key_listing": ("key_count",),
    "flat_histogram": ("row_index_sha256", "reported_mask_hash", "count",
                       "measured_nbins", "declared_nbins", "nbins_conforms",
                       "all_finite", "content_sha256"),
    "inflation_nbins": ("nbins",),
    "read_onlyness": ("sha256_before", "sha256_after", "unchanged"),
    "axis_histogram": ("nbins", "first_edge", "last_edge"),
    "row_index": ("present", "contents_readable"),
    "stored_scalar": ("value",),
}

#: A row index that loaded AND could be digested must carry the digest; one that loaded
#: and could not is a contradiction, handled by ``self_contradictions``.
ROW_INDEX_CONTENT_FIELDS = ("count", "row_index_sha256", "reported_mask_hash")

#: PREDECLARATION section 4, read 4: the five axis histograms, by name.
AXES = ("pt", "pz", "eavail", "q3", "W")


def input_record_fields(binding: dict) -> tuple[str, ...]:
    """What an ``input:`` record must carry, under ITS OWN binding's digest policy.

    The two policies are different measurements and must not be spelled the same way.  An
    input flagged ``verify_digest_at_runtime`` was re-hashed, so its record carries the
    measured ``sha256`` and ``digest_verified: true``.  CS is not: it is 41.4 GB, the
    bindings deliberately exclude it from re-hashing, and its record carries the historical
    ``support_family_sha256`` as ``sha256_bound_not_verified`` with ``digest_verified:
    false``.  That exclusion is a STATED LIMITATION and is not a fault -- but the record
    has to say which of the two happened, and a record claiming a verification the bindings
    exclude is claiming a re-hash that did not occur.
    """
    measured = ("sha256",) if binding.get("verify_digest_at_runtime") else (
        "sha256_bound_not_verified",)
    return ("path", "size_bytes", "digest_provenance", "digest_verified") + measured


def obligation_requirements(bindings: dict) -> dict[str, Requirement]:
    """Every obligation the committed bindings impose, and what each one requires.

    THIS TABLE IS THIS FILE'S OWN.  It used to be imported from the producer, which meant
    the terminal validator derived its obligations from the code it was validating: round 2
    moved the kinds out of the producer's DATA and they stayed in the producer's CODE, so
    producer/validator skew was invisible by construction.  The duplication is the point --
    two statements of the predeclaration that a test compares are a cross-check, and one
    statement asked twice is not.  ``test_pm_root_inspection.py`` holds both to a third,
    independent restatement of PREDECLARATION sections 3-4.

    The section paths come from PREDECLARATION section 4 (what each read produces) and
    section 7 (the key listings and every computed digest are outputs to be preserved).

    Only the conditional reads are optional: the ones the predeclaration writes as "only if
    the listing shows it" and "when present".
    """
    reqs: dict[str, Requirement] = {}

    def add(read_id, kind, branch, section_path, binding=None):
        reqs[read_id] = Requirement(
            read_id, kind, branch,
            input_record_fields(binding) if branch == "input"
            else RECORD_FIELDS[branch],
            section_path, binding)

    for entry in bindings["inputs"]:
        add(f"input:{entry['id']}", REQUIRED, "input", (), entry)

    add("G:key_listing", REQUIRED, "key_listing", ("G", "key_listing"))
    for scalar in ("combined_source", "centering_convention", "sqrt_tr_old",
                   "sqrt_tr_new"):
        add(f"G:{scalar}", REQUIRED, "stored_scalar", ("G", scalar))
    add("G:hInflation_g_nbins", REQUIRED, "inflation_nbins", ("G", "hInflation_g_nbins"))
    add("G:read_onlyness", REQUIRED, "read_onlyness", ("G_read_onlyness",))
    for name in bindings["optional_objects"]["G"]:
        add(f"G:{name}", OPTIONAL, "row_index", ("G", name))

    add("CS:key_listing", REQUIRED, "key_listing", ("CS", "key_listing"))
    add("CV_central:key_listing", REQUIRED, "key_listing", ("CV_central", "key_listing"))
    add("CV_central:hXSecND_flat", REQUIRED, "flat_histogram",
        ("CV_central", "hXSecND_flat"))

    for band in bindings["bands"]:
        for endpoint in (0, 1):
            label = f"EP_{band}_{endpoint}"
            here = ("endpoints", label)
            add(f"{label}:key_listing", REQUIRED, "key_listing", here + ("key_listing",))
            add(f"{label}:hXSecND_flat", REQUIRED, "flat_histogram",
                here + ("hXSecND_flat",))
            for axis in AXES:
                add(f"{label}:hXSec_{axis}", REQUIRED, "axis_histogram",
                    here + (f"hXSec_{axis}",))
            for scalar in ("ndim", "dataPOT", "globalCompleteness"):
                add(f"{label}:{scalar}", REQUIRED, "stored_scalar", here + (scalar,))
            for name in bindings["optional_objects"]["endpoint"]:
                add(f"{label}:{name}", OPTIONAL, "stored_scalar", here + (name,))
    return reqs


def obligation_kinds(bindings: dict) -> dict[str, str]:
    """Map every obligation to the kind the BINDINGS give it."""
    return {read_id: req.kind
            for read_id, req in obligation_requirements(bindings).items()}


def required_record_fields(req: Requirement, entry: dict) -> tuple[str, ...]:
    """The record fields this obligation requires, given what the record found."""
    if req.branch == "row_index" and entry.get("contents_readable") is True:
        return req.record_fields + ROW_INDEX_CONTENT_FIELDS
    return req.record_fields


def payload_field_defect(field: str, entry: dict) -> str | None:
    """Why this field is not a measurement, or ``None`` if it is one."""
    if field not in entry:
        return "absent"
    value = entry[field]
    if value is None:
        return "null"
    if field in SHA256_FIELDS:
        if not isinstance(value, str) or not SHA256_HEX.fullmatch(value):
            return "not a sha256 hex digest"
        return None
    if field in TEXT_FIELDS:
        if not isinstance(value, str) or not value.strip():
            return "not a non-empty string"
        return None
    if field in NUMERIC_FIELDS:
        if not is_number(value):
            return "not a number"
        return None
    if field in BOOLEAN_FIELDS:
        if not isinstance(value, bool):
            return "not a boolean"
        return None
    # A stored scalar carries whatever ROOT held: a number, or a TNamed's title. A zero is
    # a measurement; an empty title is not a value, and the producer records that as
    # unreadable rather than as a read.
    if isinstance(value, str):
        return None if value.strip() else "empty string where a stored value belongs"
    if is_number(value):
        return None
    return "not a stored scalar value"


# --------------------------------------------------------------------------------------
# The NESTED capture. PREDECLARATION section 4 says what each read produces and section 7
# says the listings and every computed digest are preserved outputs. A record summarising
# a read whose product is not in the report is the same defect as a status with no payload,
# one layer up: `{"lost": true}` is a non-empty mapping and satisfies every shape rule.
# --------------------------------------------------------------------------------------


def dig(document: object, path: tuple[str, ...]) -> tuple[bool, object]:
    """Follow a section path, returning ``(found, value)``."""
    node = document
    for step in path:
        if not isinstance(node, dict) or step not in node:
            return False, None
        node = node[step]
    return True, node


def tkey_listing_defect(value: object) -> str | None:
    """PREDECLARATION section 4: TKey NAMES, CLASSES and CYCLES, not a count of them."""
    if not isinstance(value, list) or not value:
        return "not a non-empty list of TKey entries"
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            return f"TKey entry {index} is not a mapping"
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            return f"TKey entry {index} carries no name"
        if not isinstance(item.get("class"), str) or not item["class"].strip():
            return f"TKey entry {index} carries no class"
        if not is_number(item.get("cycle")):
            return f"TKey entry {index} carries no cycle"
    return None


def listing_capture_defect(value: object, entry: dict) -> str | None:
    problem = tkey_listing_defect(value)
    if problem is not None:
        return problem
    key_count = entry.get("key_count")
    if is_number(key_count) and len(value) != key_count:
        return (f"the preserved listing holds {len(value)} TKeys and the record counted "
                f"{key_count}")
    return None


def axis_capture_defect(value: object, entry: dict) -> str | None:
    """PREDECLARATION section 4: the axis edges INCLUDING the final upper edge."""
    if not isinstance(value, dict) or not value:
        return "the section carries no axis capture"
    nbins, edges = value.get("nbins"), value.get("edges")
    if not is_number(nbins):
        return "the axis capture carries no nbins"
    if not isinstance(edges, list) or not edges:
        return "the axis capture carries no edges"
    if any(not is_number(edge) for edge in edges):
        return "an edge is not a number"
    if len(edges) != int(nbins) + 1:
        return (f"{len(edges)} edges for {int(nbins)} bins; the declared read is the edges "
                "INCLUDING the final upper edge, so a complete axis has nbins+1 of them")
    if nbins != entry.get("nbins"):
        return f"the axis capture's nbins {nbins} disagrees with the record's "\
               f"{entry.get('nbins')}"
    if edges[0] != entry.get("first_edge"):
        return f"the first edge {edges[0]} disagrees with the record's "\
               f"{entry.get('first_edge')}"
    if edges[-1] != entry.get("last_edge"):
        return f"the last edge {edges[-1]} disagrees with the record's "\
               f"{entry.get('last_edge')}"
    return None


def mirror_capture_defect(value: object, entry: dict,
                          fields: tuple[str, ...]) -> str | None:
    """The section states this read's measurement a second time; the two must agree."""
    if not isinstance(value, dict) or not value:
        return "the section carries no capture mapping for this read"
    for field in fields:
        if field not in value:
            return f"the section's capture omits {field}"
        if value[field] != entry.get(field):
            return (f"the section's {field} {value[field]!r} disagrees with the record's "
                    f"{entry.get(field)!r}")
    return None


def nested_capture_defect(report: dict, req: Requirement, entry: dict) -> str | None:
    """What the obligation's declared read produced, as preserved in the report."""
    found, value = dig(report, req.section_path)
    where = ".".join(req.section_path)
    if not found:
        return f"the report preserves nothing at {where} for this read"
    if req.branch == "key_listing":
        return listing_capture_defect(value, entry)
    if req.branch == "axis_histogram":
        return axis_capture_defect(value, entry)
    if req.branch == "flat_histogram":
        return mirror_capture_defect(value, entry, RECORD_FIELDS["flat_histogram"])
    if req.branch == "read_onlyness":
        return mirror_capture_defect(value, entry, RECORD_FIELDS["read_onlyness"])
    if req.branch == "row_index":
        # The contents live at the object's own name and the yes/no answer lives beside
        # them at `<name>_present`, which is how the producer stores what it measured.
        contents = tuple(field for field in required_record_fields(req, entry)
                         if field != "present")
        return (mirror_capture_defect(value, entry, contents)
                or present_answer_defect(report, req, entry.get("present")))
    if req.branch == "inflation_nbins":
        if not is_number(value):
            return f"{where} carries no measured bin count"
        if value != entry.get("nbins"):
            return f"{where} {value} disagrees with the record's {entry.get('nbins')}"
        return None
    # A stored scalar: the section holds the value itself.
    defect = payload_field_defect("value", {"value": value})
    if defect is not None:
        return f"{where} is {defect}"
    if value != entry.get("value"):
        return f"{where} {value!r} disagrees with the record's {entry.get('value')!r}"
    return None


def present_answer_defect(report: dict, req: Requirement,
                          answer: object) -> str | None:
    """G's conditional read has to leave its yes/no answer in the report.

    ``hRowIndex5D`` absent from G is the ANSWER to PM-4's premise, and PREDECLARATION
    section 4 reads G precisely "to settle whether G carries a row index at all", so the
    answer has to be IN the report and has to be the same answer the record gives. This
    demands that the answer is recorded and consistent, never what the answer is.
    """
    path = req.section_path[:-1] + (req.section_path[-1] + "_present",)
    found, value = dig(report, path)
    where = ".".join(path)
    if not found:
        return f"the report preserves no {where}; the declared question has no answer"
    if value != answer:
        return (f"{where} is {value!r} and the record says the object's presence is "
                f"{answer!r}")
    return None


def optional_absence_capture_defect(report: dict, req: Requirement) -> str | None:
    """An absent optional carries no payload -- but G still answered the question."""
    if req.branch != "row_index":
        return None
    return present_answer_defect(report, req, False)


def input_identity_problems(req: Requirement, entry: dict,
                            declared_root: str) -> list[str]:
    """Match an input record against ITS OWN committed binding and that binding's policy.

    Round 5 reproduced the gap: a wrong ``path``, ``size_bytes: -7``, ``sha256`` of all
    zeros and ``digest_verified: false`` each returned COMPLETE, because the record's
    fields were only ever checked for being non-empty and of the right TYPE. The bindings
    are the authority for what each input IS, so each field is compared to the binding
    rather than believed.

    CS's no-rehash branch is PRESERVED, not turned into a fault: the bindings exclude it
    from runtime verification at 41.4 GB, so its record must carry the historical digest
    unverified, and that is a complete capture.
    """
    binding = req.binding or {}
    problems: list[str] = []
    expected_path = os.path.join(declared_root, str(binding.get("relpath", "")))
    if not same_path(entry.get("path"), expected_path):
        problems.append(f"{req.read_id}: path {entry.get('path')!r} is not the bound "
                        f"{expected_path!r}")
    if entry.get("size_bytes") != binding.get("size_bytes"):
        problems.append(f"{req.read_id}: size_bytes {entry.get('size_bytes')!r} is not "
                        f"the bound {binding.get('size_bytes')!r}")
    if entry.get("digest_provenance") != binding.get("digest_provenance"):
        problems.append(
            f"{req.read_id}: digest_provenance {entry.get('digest_provenance')!r} is not "
            f"the bound {binding.get('digest_provenance')!r}")

    if binding.get("verify_digest_at_runtime"):
        if entry.get("digest_verified") is not True:
            problems.append(
                f"{req.read_id}: the binding requires runtime digest verification and the "
                f"record's digest_verified is {entry.get('digest_verified')!r}")
        if entry.get("sha256") != binding.get("sha256"):
            problems.append(f"{req.read_id}: sha256 {entry.get('sha256')!r} is not the "
                            f"bound {binding.get('sha256')!r}")
    else:
        if entry.get("digest_verified") is not False:
            problems.append(
                f"{req.read_id}: the bindings exclude this input from re-hashing, so "
                f"digest_verified {entry.get('digest_verified')!r} claims a verification "
                "that did not happen")
        if entry.get("sha256_bound_not_verified") != binding.get("sha256"):
            problems.append(
                f"{req.read_id}: sha256_bound_not_verified "
                f"{entry.get('sha256_bound_not_verified')!r} is not the bound "
                f"{binding.get('sha256')!r}")
        if "sha256" in entry:
            problems.append(
                f"{req.read_id}: carries a measured sha256 for an input the bindings "
                "exclude from re-hashing")
    return problems


def contamination_findings(provenance: object,
                           declared_root: str) -> tuple[bool, list[str], list[str]]:
    """Recompute the offenders from the module map; do not believe the summary.

    ``module_provenance()`` measures where every loaded module came from AND then
    summarises which of them resolve under the forbidden root. Round 5 reproduced what
    happens when only the summary is read: a module loaded from the bound tree with an
    empty offender list returned COMPLETE. The map is the measurement and the list is the
    producer's account of it, so the list is recomputed and compared.

    Returns ``(aimed_elsewhere, offenders, problems)``.
    """
    problems: list[str] = []
    if not isinstance(provenance, dict) or not provenance:
        return False, [], []

    aim = provenance.get("forbidden_root")
    aimed_elsewhere = not (isinstance(aim, str) and same_path(aim, declared_root))

    modules = provenance.get("modules")
    recomputed: list[str] = []
    if not isinstance(modules, dict) or not modules:
        problems.append(
            "module_provenance: no per-module file map, so the offender list cannot be "
            "recomputed and the producer's account of its own contamination is the only "
            "statement of it")
    else:
        prefix = os.path.normpath(declared_root) + os.sep
        recomputed = sorted(
            str(name) for name, filename in modules.items()
            if isinstance(filename, str) and os.path.normpath(filename).startswith(prefix)
        )
        count = provenance.get("module_count")
        if is_number(count) and count != len(modules):
            problems.append(
                f"module_provenance: module_count {count} disagrees with the {len(modules)}"
                " modules in the map beside it")

    listed = provenance.get("modules_loaded_from_forbidden_root")
    if not isinstance(listed, list):
        problems.append(
            "module_provenance: no modules_loaded_from_forbidden_root list, so "
            "nothing was measured about imports from the bound tree")
        listed_names: list[str] = []
    else:
        listed_names = sorted(str(name) for name in listed)
        if isinstance(modules, dict) and modules and listed_names != recomputed:
            problems.append(
                f"module_provenance: the reported offenders {listed_names} disagree with "
                f"the {recomputed} recomputed from the module map beside them")
    return aimed_elsewhere, sorted(set(listed_names) | set(recomputed)), problems


def self_contradictions(entry: dict) -> list[str]:
    """Ways one record disagrees with itself.

    Every check here compares two fields the producer already wrote. None of them asks
    whether a value is right, big enough, or close enough -- ``unchanged`` is compared to
    the two digests that define it, ``nbins_conforms`` to the two bin counts that define
    it, and a count to the bins it was counted over. A record whose summary contradicts its
    own measurement is the one thing five review rounds kept finding, and it is exactly
    what a capture-completeness classifier can see without deciding any science.
    """
    problems: list[str] = []
    status = entry.get("status")

    if "present" in entry:
        if status == "read" and entry["present"] is not True:
            problems.append("status=read but present is not true")
        if status == "absent" and entry["present"] is not False:
            problems.append("status=absent but present is not false")
    if status == "read" and entry.get("contents_readable") is False:
        problems.append(
            "status=read but contents_readable is false: the object loaded and its "
            "contents could not be digested, which is a fault and not a measurement")

    before, after, unchanged = (entry.get("sha256_before"), entry.get("sha256_after"),
                                entry.get("unchanged"))
    if (isinstance(before, str) and isinstance(after, str)
            and isinstance(unchanged, bool) and unchanged != (before == after)):
        problems.append(
            f"unchanged={unchanged} but sha256_before == sha256_after is {before == after}")

    measured, declared = entry.get("measured_nbins"), entry.get("declared_nbins")
    conforms = entry.get("nbins_conforms")
    if (is_number(measured) and is_number(declared) and isinstance(conforms, bool)
            and conforms != (measured == declared)):
        problems.append(
            f"nbins_conforms={conforms} but measured_nbins {measured} == declared_nbins "
            f"{declared} is {measured == declared}")

    count = entry.get("count")
    if is_number(count) and is_number(measured) and count > measured:
        problems.append(f"count {count} exceeds the measured_nbins {measured} it was "
                        "counted over")

    row_index, mask = entry.get("row_index_sha256"), entry.get("reported_mask_hash")
    if isinstance(row_index, str) and row_index == mask:
        problems.append("row_index_sha256 and reported_mask_hash are the same bytes; one "
                        "is sha256(idx) and the other sha256(idx + b'|C')")

    read_id = entry.get("read_id", "<unnamed>")
    return [f"{read_id}: {problem}" for problem in problems]


def read_onlyness_of_the_source(report: dict, reads: list) -> tuple[bool, list[str]]:
    """Did G change across the inspection, by the digests the producer itself wrote?

    PREDECLARATION section 4 has G's before/after digest so that read-onlyness for G is
    MEASURED rather than asserted, and the authorization forbids modifying source
    artifacts. Round 4 found that ``sha256_before``, ``sha256_after`` and ``unchanged``
    appeared in this file exactly once each -- in the required-field list -- and were never
    compared, so a report stating that G CHANGED validated as COMPLETE.

    This is exact byte equality of two fields already in the record, and the report states
    the same three fields twice: once in the ``G:read_onlyness`` record and once in the
    ``G_read_onlyness`` section. Either one saying G changed is a fault, and the two
    disagreeing is a fault, because then the report does not carry one answer.
    """
    problems: list[str] = []
    changed = False
    record = next((entry for entry in reads if isinstance(entry, dict)
                   and entry.get("read_id") == "G:read_onlyness"), None)
    section = report.get("G_read_onlyness")
    views = []
    if record is not None:
        views.append(("record G:read_onlyness", record))
    if isinstance(section, dict) and section:
        views.append(("section G_read_onlyness", section))

    for label, view in views:
        before, after = view.get("sha256_before"), view.get("sha256_after")
        if isinstance(before, str) and isinstance(after, str) and before != after:
            changed = True
            problems.append(f"{label}: G changed across the inspection, sha256_before "
                            f"{before} != sha256_after {after}")
        if view.get("unchanged") is False:
            changed = True
            problems.append(f"{label}: unchanged is false; the read was not read-only")

    if len(views) == 2:
        for field in ("sha256_before", "sha256_after", "unchanged"):
            if record.get(field) != section.get(field):
                problems.append(
                    f"section G_read_onlyness {field} does not match the G:read_onlyness "
                    "record; the report carries two answers for one measurement")
    return changed, sorted(set(problems))


def same_path(left: object, right: object) -> bool:
    """Lexical comparison only: the validating host need not hold either tree."""
    return os.path.normpath(str(left)) == os.path.normpath(str(right))


def refuse_output_inside_a_checkout(out_dir: Path) -> None:
    """Same rule as the producer: absolute, and outside every working tree once resolved."""
    if not out_dir.is_absolute():
        raise SystemExit(f"--out must be an absolute path, got {out_dir}")
    resolved = Path(os.path.realpath(out_dir))
    for candidate in {out_dir, resolved}:
        for parent in [candidate, *candidate.parents]:
            if (parent / ".git").exists():
                raise SystemExit(
                    f"--out {out_dir} resolves to {resolved}, inside the git checkout at "
                    f"{parent}; validator output must live outside every checkout"
                )


def classify(report: dict, bindings: dict, attempt_id: str,
             bindings_sha256: str | None = None) -> tuple[int, dict]:
    """Return (exit_code, findings). Pure, so tests can drive every branch directly."""
    findings: dict[str, object] = {}

    if not isinstance(report, dict):
        return EXIT_ERROR, {"reason": "report is not a JSON object"}
    if not isinstance(bindings, dict) or not isinstance(bindings.get("inputs"), list):
        return EXIT_ERROR, {"reason": "bindings are not a JSON object with inputs"}
    declared_root = bindings.get("data_root")
    if not isinstance(declared_root, str) or not declared_root.strip():
        return EXIT_ERROR, {
            "reason": "bindings declare no data_root, so nothing binds the capture to a "
                      "tree and the contamination measurement has no target"}
    if report.get("attempt_id") != attempt_id:
        return EXIT_ERROR, {
            "reason": "report is not bound to this attempt",
            "expected_attempt_id": attempt_id,
            "report_attempt_id": report.get("attempt_id"),
        }

    if bindings_sha256 is not None:
        claimed = report.get("bindings_sha256")
        if claimed != bindings_sha256:
            return EXIT_ERROR, {
                "reason": "report was produced against different bindings bytes",
                "expected_bindings_sha256": bindings_sha256,
                "report_bindings_sha256": claimed,
            }

    reads = report.get("reads")
    if not isinstance(reads, list):
        return EXIT_ERROR, {"reason": "report has no reads array"}
    malformed = [index for index, entry in enumerate(reads)
                 if not isinstance(entry, dict) or "read_id" not in entry]
    if malformed:
        return EXIT_ERROR, {"reason": "report has malformed read records",
                            "malformed_record_indices": malformed[:20]}

    # A section that is present but EMPTY has lost exactly what a missing one lost. This
    # is only the outer shell; each obligation demands its own capture inside it below.
    missing_sections = [
        name for name in REQUIRED_REPORT_SECTIONS
        if not (isinstance(report.get(name), str) and report[name].strip()
                if name in SECTIONS_THAT_ARE_TEXT
                else isinstance(report.get(name), dict) and report[name])
    ]

    # The obligations, their kinds, their payloads AND the nested capture each one
    # requires all come from the committed bindings, NEVER from the report. A record's
    # self-declared `kind` is descriptive, never authoritative.
    requirements = obligation_requirements(bindings)
    obligations = list(requirements)
    findings["obligation_count"] = len(obligations)
    if not obligations:
        return EXIT_ERROR, {"reason": "bindings declare no reads; nothing to validate"}
    if not reads:
        return EXIT_ERROR, {"reason": "empty capture: no read records at all",
                            "obligation_count": len(obligations)}

    # The record side is used for exactly two things: a read nobody declared, and a read
    # declared once and recorded twice. Everything else is driven from the obligations.
    by_id: dict[object, list[dict]] = {}
    for entry in reads:
        by_id.setdefault(entry.get("read_id"), []).append(entry)
    duplicates = sorted(str(read_id) for read_id, group in by_id.items()
                        if len(group) > 1)
    undeclared = sorted(str(read_id) for read_id in by_id if read_id not in requirements)
    missing = sorted(read_id for read_id in obligations if read_id not in by_id)

    # The one cross-check on producer/validator skew, and it has to reach the verdict: a
    # report declaring a read that does not exist, or omitting one that does, means the two
    # halves disagree about what was supposed to be read.
    claimed_reads = report.get("declared_read_ids")
    declaration_disagrees = (claimed_reads is not None
                             and sorted(claimed_reads) != sorted(obligations))
    findings["producer_declaration_disagrees_with_bindings"] = declaration_disagrees

    if report.get("traceback"):
        findings["producer_traceback"] = True
    if report.get("fatal"):
        findings["producer_fatal"] = report["fatal"]

    bad_status: list[str] = []
    bad_kind: list[str] = []
    kind_disagreements: list[str] = []
    required_failures: list[str] = []
    unreadable_optional: list[str] = []
    optional_absences: list[str] = []
    payload_reasons: dict[str, str] = {}
    nested_reasons: dict[str, str] = {}
    identity_problems: list[str] = []
    contradictions: list[str] = []

    for read_id in obligations:
        group = by_id.get(read_id)
        if not group:
            continue
        req = requirements[read_id]
        entry = group[0]
        status, kind = entry.get("status"), entry.get("kind")

        if status not in KNOWN_STATUSES:
            bad_status.append(read_id)
        if kind not in {REQUIRED, OPTIONAL}:
            bad_kind.append(read_id)
        elif kind != req.kind:
            # A record that claims a different kind than the bindings give its id is a
            # fault in itself: the producer trying to reclassify its own obligation.
            kind_disagreements.append(read_id)

        # A required read that did not happen, OR an optional key that was listed and then
        # could not be read. The second is not the declared absence: we did not learn
        # whether it is there, which is a different thing from learning that it is not.
        if req.kind == REQUIRED:
            if status in {"absent", "unreadable"}:
                required_failures.append(read_id)
        elif status == "unreadable":
            unreadable_optional.append(read_id)
        elif status == "absent":
            optional_absences.append(read_id)

        contradictions.extend(self_contradictions(entry))

        if status != "read":
            if req.kind == OPTIONAL and status == "absent":
                defect = optional_absence_capture_defect(report, req)
                if defect is not None:
                    nested_reasons[read_id] = defect
            continue

        for field in required_record_fields(req, entry):
            defect = payload_field_defect(field, entry)
            if defect is not None:
                payload_reasons[f"{read_id}:{field}"] = defect

        if req.branch == "input":
            identity_problems.extend(
                input_identity_problems(req, entry, declared_root))
        else:
            # Every obligation reports its OWN missing product, even when the whole
            # section around it is gone. `missing_report_sections` is a shell check and
            # cannot say which declared read lost its measurement.
            defect = nested_capture_defect(report, req, entry)
            if defect is not None:
                nested_reasons[read_id] = defect

    findings["records_whose_kind_contradicts_bindings"] = sorted(kind_disagreements)
    findings["records_with_unknown_status"] = sorted(bad_status)
    findings["records_with_unknown_kind"] = sorted(bad_kind)
    findings["required_read_failures"] = sorted(required_failures)
    findings["unreadable_optional_objects"] = sorted(unreadable_optional)
    findings["expected_optional_absences"] = sorted(optional_absences)
    findings["expected_optional_absences_are_measurements"] = True
    findings["duplicate_read_records"] = duplicates
    findings["missing_read_records"] = missing
    findings["records_for_reads_the_bindings_do_not_declare"] = undeclared
    findings["missing_report_sections"] = missing_sections
    findings["reads_missing_payload"] = sorted(payload_reasons)
    findings["reads_missing_payload_why"] = payload_reasons
    findings["reads_missing_nested_capture"] = sorted(nested_reasons)
    findings["reads_missing_nested_capture_why"] = nested_reasons
    findings["inputs_that_disagree_with_their_binding"] = sorted(identity_problems)

    # The capture has to have come from the tree the bindings bind, and the contamination
    # measurement has to have been aimed at that same tree: a forbidden_root pointed
    # somewhere else measures nothing about the bound tree, so its empty offender list
    # says nothing either.
    wrong_data_root = not same_path(report.get("data_root"), declared_root)
    aimed_elsewhere, offenders, contamination_problems = contamination_findings(
        report.get("module_provenance"), declared_root)
    contradictions.extend(contamination_problems)
    findings["data_root_disagrees_with_bindings"] = wrong_data_root
    findings["bindings_data_root"] = declared_root
    findings["contamination_measurement_aimed_at_the_wrong_tree"] = aimed_elsewhere
    findings["modules_loaded_from_the_forbidden_root"] = offenders

    source_changed, read_onlyness_problems = read_onlyness_of_the_source(report, reads)
    contradictions = sorted(set(contradictions) | set(read_onlyness_problems))
    findings["source_artifact_changed_during_the_inspection"] = source_changed
    findings["records_contradicting_their_own_measurement"] = contradictions

    faults = (bad_status or bad_kind or kind_disagreements or required_failures
              or unreadable_optional or missing_sections or payload_reasons
              or nested_reasons or identity_problems or duplicates
              or contradictions or source_changed or declaration_disagrees
              or undeclared or wrong_data_root or aimed_elsewhere or offenders
              or report.get("traceback") or report.get("fatal"))
    if faults:
        return EXIT_ERROR, findings
    if missing:
        return EXIT_INCOMPLETE, findings
    return EXIT_COMPLETE, findings


#: The one artifact this half of the contract preserves.
VERDICT_FILENAME = "pm-inspection-verdict.json"


class VerdictNotWritten(Exception):
    """The classification happened; its artifact did not."""


def build_verdict(report_path: Path, bindings_path: Path,
                  attempt_id: str) -> tuple[int, dict]:
    """Classify, returning a verdict for every input shape including the broken ones.

    A malformed shape must produce a VERDICT, not a traceback: an uncaught exception
    leaves the terminal branch unselected, which is the one outcome the contract has no
    consequence for.
    """
    try:
        report = json.loads(report_path.read_text())
        bindings = json.loads(bindings_path.read_text())
    except (OSError, ValueError) as error:
        return EXIT_ERROR, {"terminal_branch": "ERROR",
                            "reason": f"cannot read report or bindings: {error}"}
    try:
        measured = hashlib.sha256(bindings_path.read_bytes()).hexdigest()
        exit_code, findings = classify(report, bindings, attempt_id,
                                       bindings_sha256=measured)
    except Exception as error:  # noqa: BLE001
        return EXIT_ERROR, {
            "terminal_branch": "ERROR",
            "reason": f"validator could not classify this report: {error!r}"}
    return exit_code, {
        "terminal_branch": {EXIT_COMPLETE: "COMPLETE",
                            EXIT_INCOMPLETE: "INCOMPLETE"}.get(exit_code, "ERROR"),
        "attempt_id": attempt_id,
        "findings": findings,
        "classifies": "measurement capture only",
        "does_not_classify": (
            "scientific adequacy, discharge of PM-1/PM-3/PM-4/PM-5, adoption, "
            "gate movement, or blanket citability"
        ),
    }


def write_verdict(out_dir: Path, verdict: dict) -> Path:
    """Write the verdict, and NEVER overwrite one.

    ``preservation_behavior.mode`` is ``preserve-first`` and the producer already refuses
    to overwrite its report. A verdict silently replaced is a terminal classification
    nobody can audit afterwards: review dropped one record from the report, re-ran with
    the same argv, and the COMPLETE verdict became an INCOMPLETE with no trace of the
    first. Refusing keeps the first artifact, and the refusal is still an ERROR return
    rather than a traceback, so a branch is selected either way.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / VERDICT_FILENAME
    if path.exists():
        raise VerdictNotWritten(
            f"{path} already exists and a verdict is never overwritten; a second "
            "classification needs a fresh run directory and a fresh --attempt-id")
    path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="ABSOLUTE run directory, outside every git checkout")
    args = parser.parse_args(argv)

    refuse_output_inside_a_checkout(args.out)

    exit_code, verdict = build_verdict(args.report, args.bindings, args.attempt_id)
    verdict["validator_exit_code"] = exit_code
    try:
        write_verdict(args.out, verdict)
    except (OSError, VerdictNotWritten) as error:
        # The write path used to sit outside every guard, so an --out that was a regular
        # file, a verdict path that was a directory, and an unwritable --out each ended in
        # a traceback with no artifact at all. The classification is reported here and the
        # return is ERROR: a validation whose verdict cannot be recorded is not one.
        print(json.dumps({
            "terminal_branch": "ERROR",
            "exit_code": EXIT_ERROR,
            "verdict_not_written": str(error),
            "classification_that_could_not_be_written": verdict["terminal_branch"],
        }))
        return EXIT_ERROR
    print(json.dumps({"terminal_branch": verdict["terminal_branch"],
                      "exit_code": exit_code}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
