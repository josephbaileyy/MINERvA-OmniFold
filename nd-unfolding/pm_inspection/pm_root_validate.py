#!/usr/bin/env python3
"""Terminal validator for the bounded ROOT inspection.

IT CLASSIFIES MEASUREMENT CAPTURE, NOT SCIENCE.  It reads the producer's report and
selects exactly one terminal branch.  It never looks at whether a measured value is good,
expected, or sufficient, and it has no acceptance threshold to apply -- because none was
authorized and inventing one here would be inventing a scientific criterion.

THE DISTINCTION THAT MATTERS.  ``hRowIndex5D`` absent from G is the ANSWER to a declared
question and is COMPLETE.  A required input that is missing, the wrong size, or whose bytes
do not match its binding is a capture FAILURE and is ERROR.  Collapsing those two would
turn a real measurement into a fault, or a fault into a measurement; keeping them apart is
this validator's whole job.

WHAT COMPLETE DOES AND DOES NOT UNLOCK.  It unlocks preserving the capture as a
measurement.  It does not discharge PM-1, PM-3, PM-4 or PM-5, does not adopt anything, and
does not make the numbers citable for a gate movement.  Those belong to whoever owns those
rows, on evidence this inspection only supplies.

EXIT CODES, which select the contract's terminal branch:
  0   COMPLETE    every declared read has a record, and no required read failed
  10  INCOMPLETE  ran to the end, but a declared read has no record
  20  ERROR       required input unusable, producer error, or an unreadable report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXIT_COMPLETE = 0
EXIT_INCOMPLETE = 10
EXIT_ERROR = 20

OPTIONAL = "expected-optional"
REQUIRED = "required"


def classify(report: dict) -> tuple[int, dict]:
    """Return (exit_code, findings). Pure: no I/O, so the tests can drive it directly."""
    findings: dict[str, object] = {}

    reads = report.get("reads")
    declared = report.get("declared_read_ids")
    if not isinstance(reads, list) or not isinstance(declared, list):
        return EXIT_ERROR, {"reason": "report is missing reads or declared_read_ids"}

    if report.get("traceback"):
        findings["producer_traceback"] = True
    if report.get("fatal"):
        findings["producer_fatal"] = report["fatal"]

    seen = {entry.get("read_id") for entry in reads}
    missing = sorted(set(declared) - seen)
    findings["missing_read_records"] = missing

    required_failures = sorted(
        entry.get("read_id", "<unnamed>") for entry in reads
        if entry.get("kind") == REQUIRED and entry.get("status") in {"absent",
                                                                     "unreadable"}
    )
    optional_absences = sorted(
        entry.get("read_id", "<unnamed>") for entry in reads
        if entry.get("kind") == OPTIONAL and entry.get("status") == "absent"
    )
    findings["required_read_failures"] = required_failures
    findings["expected_optional_absences"] = optional_absences
    findings["expected_optional_absences_are_measurements"] = True

    unknown_kind = sorted(
        entry.get("read_id", "<unnamed>") for entry in reads
        if entry.get("kind") not in {REQUIRED, OPTIONAL}
    )
    if unknown_kind:
        findings["records_with_unknown_kind"] = unknown_kind
        return EXIT_ERROR, findings

    if report.get("traceback") or report.get("fatal") or required_failures:
        return EXIT_ERROR, findings
    if missing:
        return EXIT_INCOMPLETE, findings
    return EXIT_COMPLETE, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="ABSOLUTE run directory the producer wrote to")
    args = parser.parse_args(argv)

    try:
        report = json.loads(args.report.read_text())
    except (OSError, ValueError) as error:
        verdict = {"terminal_branch": "ERROR",
                   "reason": f"cannot read producer report: {error}"}
        exit_code = EXIT_ERROR
    else:
        exit_code, findings = classify(report)
        verdict = {
            "terminal_branch": {EXIT_COMPLETE: "COMPLETE",
                                EXIT_INCOMPLETE: "INCOMPLETE"}.get(exit_code, "ERROR"),
            "findings": findings,
            "classifies": "measurement capture only",
            "does_not_classify": (
                "scientific adequacy, discharge of PM-1/PM-3/PM-4/PM-5, adoption, "
                "gate movement, or blanket citability"
            ),
        }
    verdict["validator_exit_code"] = exit_code
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "pm-inspection-verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal_branch": verdict["terminal_branch"],
                      "exit_code": exit_code}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
