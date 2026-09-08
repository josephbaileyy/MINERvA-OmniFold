#!/usr/bin/env python3
"""Terminal validator for the bounded ROOT inspection.

IT CLASSIFIES MEASUREMENT CAPTURE, NOT SCIENCE.  It never looks at whether a measured value
is good, expected, or sufficient, and it has no acceptance threshold, because none was
authorized and inventing one here would be inventing a scientific criterion.

IT DOES NOT TRUST THE PRODUCER'S ACCOUNT OF ITS OWN OBLIGATIONS.  An earlier revision took
``declared_read_ids`` from the report, so a producer that declared nothing and read nothing
was ``COMPLETE``.  The obligation list is recomputed from the committed bindings, by this
file's own table rather than by importing the producer's, and a report is refused unless it
is bound to THIS attempt -- otherwise a stale report left at the fixed path satisfies the
read.

IT DOES NOT TRUST A RECORD'S SUMMARY OF A MEASUREMENT OVER THE MEASUREMENT BESIDE IT.  Four
review rounds each found one form of that: obligations taken from the producer's account, a
self-declared ``kind`` treated as authoritative, a ``status`` carried with the payload
absent, and then ``status``/``unchanged``/``present``/``nbins_conforms`` believed over the
digests and counts in the same record.  So a payload field must be non-empty and of the
kind its read produces, and where two fields in one record determine each other they are
compared.  ``unchanged`` must equal ``sha256_before == sha256_after``; nothing here asks
whether a digest is the RIGHT digest.

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
#: Present-but-EMPTY is the same loss, so a section must be non-empty as well.
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
                           "sha256_before", "sha256_after"})
TEXT_FIELDS = frozenset({"path", "digest_provenance"})
NUMERIC_FIELDS = frozenset({"size_bytes", "key_count", "count", "measured_nbins",
                            "declared_nbins", "nbins", "first_edge", "last_edge"})
BOOLEAN_FIELDS = frozenset({"unchanged", "present", "contents_readable",
                            "nbins_conforms", "all_finite"})


def is_number(value: object) -> bool:
    """A real number, and not a bool: ``True`` is an ``int`` and is not a count."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def obligation_kinds(bindings: dict) -> dict[str, str]:
    """Map every obligation to the kind the BINDINGS give it.

    THIS TABLE IS THIS FILE'S OWN.  It used to be imported from the producer, which meant
    the terminal validator derived its obligations from the code it was validating: round 2
    moved the kinds out of the producer's DATA and they stayed in the producer's CODE, so
    producer/validator skew was invisible by construction.  The duplication is the point --
    two statements of the predeclaration that a test compares are a cross-check, and one
    statement asked twice is not.  ``test_pm_root_inspection.py`` holds both to a third,
    independent restatement of PREDECLARATION sections 3-4.

    Only the conditional reads are optional: the ones the predeclaration writes as "only if
    the listing shows it" and "when present".
    """
    kinds: dict[str, str] = {}
    for entry in bindings["inputs"]:
        kinds[f"input:{entry['id']}"] = REQUIRED
    for read_id in ("G:key_listing", "G:combined_source", "G:centering_convention",
                    "G:sqrt_tr_old", "G:sqrt_tr_new", "G:hInflation_g_nbins",
                    "G:read_onlyness", "CS:key_listing", "CV_central:key_listing",
                    "CV_central:hXSecND_flat"):
        kinds[read_id] = REQUIRED
    for name in bindings["optional_objects"]["G"]:
        kinds[f"G:{name}"] = OPTIONAL
    for band in bindings["bands"]:
        for endpoint in (0, 1):
            label = f"EP_{band}_{endpoint}"
            for read_id in (f"{label}:key_listing", f"{label}:hXSecND_flat"):
                kinds[read_id] = REQUIRED
            for axis in ("pt", "pz", "eavail", "q3", "W"):
                kinds[f"{label}:hXSec_{axis}"] = REQUIRED
            for scalar in ("ndim", "dataPOT", "globalCompleteness"):
                kinds[f"{label}:{scalar}"] = REQUIRED
            for name in bindings["optional_objects"]["endpoint"]:
                kinds[f"{label}:{name}"] = OPTIONAL
    return kinds


def payload_fields_for(read_id: str, entry: dict | None = None) -> tuple[str, ...]:
    """Fields a ``status="read"`` record MUST carry, by what that read measures.

    A record that says a read happened but carries no measurement is not a capture. This is
    a completeness rule, not an acceptance threshold: it asks whether the number is THERE,
    never whether the number is right, expected, or good enough.

    ``entry`` is the record itself, for the one read whose payload depends on what it
    found: a row index that loaded and could be digested must carry the digest, and one
    that loaded and could not is a contradiction handled by ``self_contradictions``.
    """
    if read_id.startswith("input:"):
        return ("path", "size_bytes", "digest_provenance")
    if read_id.endswith(":key_listing"):
        return ("key_count",)
    if read_id.endswith(":hXSecND_flat"):
        return ("row_index_sha256", "reported_mask_hash", "count", "measured_nbins",
                "declared_nbins", "nbins_conforms", "all_finite", "content_sha256")
    if read_id == "G:hInflation_g_nbins":
        return ("nbins",)
    if read_id == "G:read_onlyness":
        return ("sha256_before", "sha256_after", "unchanged")
    if ":hXSec_" in read_id:
        return ("nbins", "first_edge", "last_edge")
    if read_id == "G:hRowIndex5D":
        fields = ("present", "contents_readable")
        if entry is not None and entry.get("contents_readable") is True:
            fields += ("count", "row_index_sha256", "reported_mask_hash")
        return fields
    # Every remaining declared read is a stored scalar.
    return ("value",)


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


def payload_defects(reads: list, kinds: dict) -> tuple[list[str], dict[str, str]]:
    """Read ids whose ``read`` record is missing, empties, or mistypes a payload field."""
    reasons: dict[str, str] = {}
    for entry in reads:
        if not isinstance(entry, dict) or entry.get("status") != "read":
            continue
        read_id = entry.get("read_id")
        if read_id not in kinds:
            continue
        for field in payload_fields_for(str(read_id), entry):
            defect = payload_field_defect(field, entry)
            if defect is not None:
                reasons[f"{read_id}:{field}"] = defect
    return sorted(reasons), reasons


def self_contradictions(entry: dict) -> list[str]:
    """Ways one record disagrees with itself.

    Every check here compares two fields the producer already wrote. None of them asks
    whether a value is right, big enough, or close enough -- ``unchanged`` is compared to
    the two digests that define it, ``nbins_conforms`` to the two bin counts that define
    it, and a count to the bins it was counted over. A record whose summary contradicts its
    own measurement is the one thing four review rounds kept finding, and it is exactly
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

    # A section that is present but EMPTY has lost exactly what a missing one lost.
    missing_sections = [
        name for name in REQUIRED_REPORT_SECTIONS
        if not (isinstance(report.get(name), str) and report[name].strip()
                if name in SECTIONS_THAT_ARE_TEXT
                else isinstance(report.get(name), dict) and report[name])
    ]

    # The obligations AND their kinds come from the committed bindings, NEVER from the
    # report. A record's self-declared `kind` is descriptive, never authoritative.
    kinds = obligation_kinds(bindings)
    obligations = list(kinds)
    findings["obligation_count"] = len(obligations)
    if not obligations:
        return EXIT_ERROR, {"reason": "bindings declare no reads; nothing to validate"}
    if not reads:
        return EXIT_ERROR, {"reason": "empty capture: no read records at all",
                            "obligation_count": len(obligations)}

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

    bad_status = sorted(
        str(entry.get("read_id", "<unnamed>")) for entry in reads
        if entry.get("status") not in KNOWN_STATUSES
    )
    bad_kind = sorted(
        str(entry.get("read_id", "<unnamed>")) for entry in reads
        if entry.get("kind") not in {REQUIRED, OPTIONAL}
    )
    # A record that claims a different kind than the bindings give its id is a fault in
    # itself: it is the producer trying to reclassify its own obligation.
    kind_disagreements = sorted(
        str(entry.get("read_id"))
        for entry in reads
        if entry.get("read_id") in kinds
        and entry.get("kind") in {REQUIRED, OPTIONAL}
        and entry.get("kind") != kinds[entry["read_id"]]
    )
    findings["records_whose_kind_contradicts_bindings"] = kind_disagreements
    findings["records_with_unknown_status"] = bad_status
    findings["records_with_unknown_kind"] = bad_kind

    # A required read that did not happen, OR an optional key that was listed and then
    # could not be read. The second is not the declared absence: we did not learn whether
    # it is there, which is a different thing from learning that it is not.
    def bound_kind(entry):
        return kinds.get(entry.get("read_id"))

    required_failures = sorted(
        str(entry.get("read_id", "<unnamed>")) for entry in reads
        if bound_kind(entry) == REQUIRED
        and entry.get("status") in {"absent", "unreadable"}
    )
    unreadable_optional = sorted(
        str(entry.get("read_id", "<unnamed>")) for entry in reads
        if bound_kind(entry) == OPTIONAL and entry.get("status") == "unreadable"
    )
    optional_absences = sorted(
        str(entry.get("read_id", "<unnamed>")) for entry in reads
        if bound_kind(entry) == OPTIONAL and entry.get("status") == "absent"
    )
    findings["required_read_failures"] = required_failures
    findings["unreadable_optional_objects"] = unreadable_optional
    findings["expected_optional_absences"] = optional_absences
    findings["expected_optional_absences_are_measurements"] = True

    seen = {entry.get("read_id") for entry in reads}
    missing = sorted(set(obligations) - seen)
    # The mirror of the declaration cross-check, and the same disagreement: a record for a
    # read the bindings do not declare is a measurement nobody asked for. Now that the two
    # halves keep separate obligation tables, this is where producer-side skew surfaces.
    undeclared = sorted(str(read_id) for read_id in seen - set(obligations))
    findings["missing_read_records"] = missing
    findings["records_for_reads_the_bindings_do_not_declare"] = undeclared
    findings["missing_report_sections"] = missing_sections
    payload_missing, payload_reasons = payload_defects(reads, kinds)
    findings["reads_missing_payload"] = payload_missing
    findings["reads_missing_payload_why"] = payload_reasons

    contradictions = sorted(
        problem for entry in reads if entry.get("read_id") in kinds
        for problem in self_contradictions(entry))

    # The capture has to have come from the tree the bindings bind, and the contamination
    # measurement has to have been aimed at that same tree: a forbidden_root pointed
    # somewhere else measures nothing about the bound tree, so its empty offender list
    # says nothing either.
    wrong_data_root = not same_path(report.get("data_root"), declared_root)
    provenance = report.get("module_provenance")
    aimed_elsewhere = False
    offenders: list[str] = []
    if isinstance(provenance, dict) and provenance:
        aim = provenance.get("forbidden_root")
        aimed_elsewhere = not (isinstance(aim, str) and same_path(aim, declared_root))
        listed = provenance.get("modules_loaded_from_forbidden_root")
        if isinstance(listed, list):
            offenders = sorted(str(name) for name in listed)
        else:
            contradictions.append(
                "module_provenance: no modules_loaded_from_forbidden_root list, so "
                "nothing was measured about imports from the bound tree")
    findings["data_root_disagrees_with_bindings"] = wrong_data_root
    findings["bindings_data_root"] = declared_root
    findings["contamination_measurement_aimed_at_the_wrong_tree"] = aimed_elsewhere
    findings["modules_loaded_from_the_forbidden_root"] = offenders

    source_changed, read_onlyness_problems = read_onlyness_of_the_source(report, reads)
    contradictions = sorted(set(contradictions) | set(read_onlyness_problems))
    findings["source_artifact_changed_during_the_inspection"] = source_changed
    findings["records_contradicting_their_own_measurement"] = contradictions

    faults = (bad_status or bad_kind or kind_disagreements or required_failures
              or unreadable_optional or missing_sections or payload_missing
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
