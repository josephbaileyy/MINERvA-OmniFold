#!/usr/bin/env python3
"""Terminal validator for the bounded ROOT inspection.

IT CLASSIFIES MEASUREMENT CAPTURE, NOT SCIENCE.  It never looks at whether a measured value
is good, expected, or sufficient, and it has no acceptance threshold, because none was
authorized and inventing one here would be inventing a scientific criterion.

IT DOES NOT TRUST THE PRODUCER'S ACCOUNT OF ITS OWN OBLIGATIONS.  An earlier revision took
``declared_read_ids`` from the report, so a producer that declared nothing and read nothing
was ``COMPLETE``.  The obligation list is now recomputed from the committed bindings, and a
report is refused unless it is bound to THIS attempt -- otherwise a stale report left at the
fixed path satisfies the read.

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
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pm_root_inspect as producer_module  # noqa: E402

EXIT_COMPLETE = 0
EXIT_INCOMPLETE = 10
EXIT_ERROR = 20

OPTIONAL = "expected-optional"
REQUIRED = "required"

#: The only statuses this validator models. Anything else is a fault rather than a pass,
#: because an unmodelled status is a measurement whose meaning nobody has decided.
KNOWN_STATUSES = frozenset({"read", "absent", "unreadable"})


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

    # The obligations AND their kinds come from the committed bindings, NEVER from the
    # report. A record's self-declared `kind` is descriptive, never authoritative.
    kinds = producer_module.obligation_kinds(bindings)
    obligations = list(kinds)
    findings["obligation_count"] = len(obligations)
    if not obligations:
        return EXIT_ERROR, {"reason": "bindings declare no reads; nothing to validate"}
    if not reads:
        return EXIT_ERROR, {"reason": "empty capture: no read records at all",
                            "obligation_count": len(obligations)}

    claimed = report.get("declared_read_ids")
    if claimed is not None and sorted(claimed) != sorted(obligations):
        findings["producer_declaration_disagrees_with_bindings"] = True

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
    findings["missing_read_records"] = missing

    faults = (bad_status or bad_kind or kind_disagreements or required_failures
              or unreadable_optional or report.get("traceback") or report.get("fatal"))
    if faults:
        return EXIT_ERROR, findings
    if missing:
        return EXIT_INCOMPLETE, findings
    return EXIT_COMPLETE, findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="ABSOLUTE run directory, outside every git checkout")
    args = parser.parse_args(argv)

    refuse_output_inside_a_checkout(args.out)

    try:
        report = json.loads(args.report.read_text())
        bindings = json.loads(args.bindings.read_text())
    except (OSError, ValueError) as error:
        verdict = {"terminal_branch": "ERROR",
                   "reason": f"cannot read report or bindings: {error}"}
        exit_code = EXIT_ERROR
    else:
        measured = hashlib.sha256(args.bindings.read_bytes()).hexdigest()
        exit_code, findings = classify(report, bindings, args.attempt_id,
                                       bindings_sha256=measured)
        verdict = {
            "terminal_branch": {EXIT_COMPLETE: "COMPLETE",
                                EXIT_INCOMPLETE: "INCOMPLETE"}.get(exit_code, "ERROR"),
            "attempt_id": args.attempt_id,
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
