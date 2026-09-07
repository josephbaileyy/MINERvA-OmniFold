#!/usr/bin/env python3
"""Producer for the bounded read-only ROOT inspection of PM-1, PM-3, PM-4 and PM-5.

WHAT THIS IS.  The executable packaging of the fixed reads predeclared in
``docs/orchestration/PREDECLARATION-20260906-pm-root-inspection.md`` sections 3 and 4.  It
opens exactly the thirteen bound inputs ``READ``, performs exactly the declared reads, and
writes one JSON report plus the raw key listings.  It computes no covariance, trains
nothing, adopts nothing, and writes nothing outside its run directory.

WHAT IT DOES NOT DO.  It assigns no scientific grade and reaches no verdict about the
physics.  ``COMPLETE`` here means *the declared measurements were captured*, never that the
measurements are good, sufficient, or citable for a discharge.  Whether the captured values
satisfy PM-1, PM-3, PM-4 or PM-5 is a question for whoever owns those rows.

THE PM-4 PROVENANCE GAP IS PRESERVED, NOT CLOSED.  Digests bound at 2026-09-08 describe the
bytes those files hold now.  They are not evidence of what G consumed in August: G's own
hash receipt does not bind the central CV.  Any digest this producer reconstructs is
labelled ``reconstructed_through_producer_input_route`` and never ``read_from_G``.

EXIT CODES, which are the terminal branch selector:
  0   capture complete
  10  capture incomplete -- ran to the end, but a declared read has no record
  20  error -- a required input missing or unreadable, a digest mismatch, an import
      failure, or an unhandled exception.  Error evidence is still written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import sys
import traceback
from pathlib import Path

EXIT_COMPLETE = 0
EXIT_INCOMPLETE = 10
EXIT_ERROR = 20

#: Read 8 MiB at a time; these are network filesystems.
HASH_CHUNK = 8 * 1024 * 1024

#: Objects whose ABSENCE is a declared, expected outcome rather than a failure.  The whole
#: point of reading G is to settle whether ``hRowIndex5D`` is there; "absent" is an answer.
OPTIONAL_ABSENCE_IS_AN_ANSWER = "expected-optional"
#: Objects whose absence means the capture did not happen.
REQUIRED_ABSENCE_IS_A_FAILURE = "required"


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(HASH_CHUNK)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def refuse_output_inside_a_checkout(out_dir: Path) -> None:
    """The run directory must be absolute and outside every git working tree.

    Runtime output inside a checkout is how a read-only inspection becomes a checkout
    mutation, and how an evidence directory acquires files nobody decided to commit.  The
    committed evidence destination is a SEPARATE, later, deliberate copy.
    """
    if not out_dir.is_absolute():
        raise SystemExit(f"--out must be an absolute path, got {out_dir}")
    for parent in [out_dir, *out_dir.parents]:
        if (parent / ".git").exists():
            raise SystemExit(
                f"--out {out_dir} is inside the git checkout at {parent}; "
                "runtime output must live outside every checkout"
            )


def module_provenance(forbidden_root: str) -> dict[str, object]:
    """Measure where the loaded modules actually came from.

    Sourcing the deployed tree's environment is allowed; importing its ANALYSIS CODE is
    not.  Asserting that in prose is worth nothing, so this measures it: every loaded
    module's file, and an explicit list of any that resolve under the forbidden root.
    """
    loaded: dict[str, str] = {}
    for name, module in sorted(sys.modules.items()):
        filename = getattr(module, "__file__", None)
        if filename:
            loaded[name] = filename
    offenders = sorted(
        name for name, filename in loaded.items()
        if filename.startswith(forbidden_root.rstrip("/") + "/")
    )
    return {
        "python": sys.executable,
        "version": sys.version.split()[0],
        "platform": platform.platform(),
        "sys_path": list(sys.path),
        "forbidden_root": forbidden_root,
        "modules_loaded_from_forbidden_root": offenders,
        "module_count": len(loaded),
        "modules": loaded,
    }


def open_root_file(ROOT, path: Path):
    handle = ROOT.TFile.Open(str(path), "READ")
    if not handle or handle.IsZombie():
        raise OSError(f"ROOT could not open {path}")
    return handle


def key_listing(handle) -> list[dict[str, object]]:
    listing = []
    for key in handle.GetListOfKeys():
        listing.append({
            "name": key.GetName(),
            "class": key.GetClassName(),
            "cycle": int(key.GetCycle()),
        })
    return sorted(listing, key=lambda entry: (entry["name"], entry["cycle"]))


def record(reads: list, read_id: str, status: str, kind: str, **extra) -> None:
    """Append one record per declared read.

    ``status`` is one of ``read``, ``absent``, ``unreadable``.  ``kind`` says whether an
    absence is an answer or a failure, so the validator never has to guess.
    """
    entry = {"read_id": read_id, "status": status, "kind": kind}
    entry.update(extra)
    reads.append(entry)


def bind_inputs(bindings: dict, data_root: Path, reads: list) -> dict[str, Path]:
    """Resolve and verify every bound input BEFORE any ROOT call.

    A required input that is missing, unreadable, the wrong size, or whose bytes do not
    match a digest flagged for runtime verification is a capture failure, not a finding.
    CS is size-checked only: it is 41.4 GB and this inspection does not re-hash it, which
    is a stated limitation and not an oversight.
    """
    resolved: dict[str, Path] = {}
    for entry in bindings["inputs"]:
        input_id = entry["id"]
        path = data_root / entry["relpath"]
        read_id = f"input:{input_id}"
        if not path.is_file() or not os.access(path, os.R_OK):
            record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                   path=str(path), detail="missing or not readable")
            continue
        size = path.stat().st_size
        if size != entry["size_bytes"]:
            record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                   path=str(path), detail=f"size {size} != bound {entry['size_bytes']}")
            continue
        if entry.get("verify_digest_at_runtime"):
            measured = sha256_file(path)
            if measured != entry["sha256"]:
                record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                       path=str(path),
                       detail=f"sha256 {measured} != bound {entry['sha256']}")
                continue
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, path=str(path),
                   size_bytes=size, sha256=measured, digest_verified=True,
                   digest_provenance=entry["digest_provenance"])
        else:
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, path=str(path),
                   size_bytes=size, sha256_bound_not_verified=entry["sha256"],
                   digest_verified=False,
                   digest_provenance=entry["digest_provenance"],
                   digest_limitation=entry.get("digest_limitation"))
        resolved[input_id] = path
    return resolved


def read_G(ROOT, path: Path, optional_names: list[str], reads: list) -> dict:
    """Declared read 1: G's key listing, the stamp scalars, and the row index IF present."""
    out: dict[str, object] = {}
    handle = open_root_file(ROOT, path)
    try:
        listing = key_listing(handle)
        out["key_listing"] = listing
        out["key_count"] = len(listing)
        present = {entry["name"] for entry in listing}
        record(reads, "G:key_listing", "read", REQUIRED_ABSENCE_IS_A_FAILURE,
               key_count=len(listing))

        for scalar in ("combined_source", "centering_convention", "sqrt_tr_old",
                       "sqrt_tr_new"):
            read_id = f"G:{scalar}"
            if scalar not in present:
                record(reads, read_id, "absent", REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail="declared scalar not in G's key listing")
                continue
            obj = handle.Get(scalar)
            value = getattr(obj, "GetTitle", lambda: None)() if obj else None
            out[scalar] = value
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, value=value)

        if "hInflation_g" in present:
            hist = handle.Get("hInflation_g")
            nbins = int(hist.GetNbinsX()) if hist else None
            out["hInflation_g_nbins"] = nbins
            record(reads, "G:hInflation_g_nbins", "read", REQUIRED_ABSENCE_IS_A_FAILURE,
                   nbins=nbins)
        else:
            record(reads, "G:hInflation_g_nbins", "absent",
                   REQUIRED_ABSENCE_IS_A_FAILURE,
                   detail="hInflation_g not in G's key listing")

        # The declared conditional read. Absence here is the ANSWER to PM-4's premise, not
        # a failure, and the validator must not confuse the two.
        for name in optional_names:
            read_id = f"G:{name}"
            if name in present:
                obj = handle.Get(name)
                record(reads, read_id, "read", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=True,
                       entries=int(obj.GetEntries()) if hasattr(obj, "GetEntries") else None)
                out[f"{name}_present"] = True
            else:
                record(reads, read_id, "absent", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=False,
                       detail="declared conditional read; absence is a measurement")
                out[f"{name}_present"] = False
    finally:
        handle.Close()
    return out


def read_CS(ROOT, path: Path, reads: list) -> dict:
    """Declared read 2: CS top-level key listing ONLY. No Get() on any band matrix."""
    handle = open_root_file(ROOT, path)
    try:
        listing = key_listing(handle)
        names = [entry["name"] for entry in listing]
        bands = sorted(
            name for name in names
            if name.startswith("hCov_universe5d_") and name != "hCov_universe5d_total"
        )
        record(reads, "CS:key_listing", "read", REQUIRED_ABSENCE_IS_A_FAILURE,
               key_count=len(listing), band_key_count=len(bands),
               note="listing only; no ReadObj on any covariance matrix")
        return {"key_listing": listing, "band_keys": bands,
                "total_present": "hCov_universe5d_total" in names}
    finally:
        handle.Close()


def flat_digest(hist, nbins: int) -> dict[str, object]:
    """Digest the regular-bin contents of a flat 5D histogram.

    Returned under a name that keeps the provenance caveat attached to the value.
    """
    values = [float(hist.GetBinContent(index + 1)) for index in range(nbins)]
    finite = all(value == value and abs(value) != float("inf") for value in values)
    payload = json.dumps([repr(value) for value in values]).encode()
    return {
        "nbins": nbins,
        "all_finite": finite,
        "content_sha256": hashlib.sha256(payload).hexdigest(),
        "mask_sha256": hashlib.sha256(
            json.dumps([value != 0.0 for value in values]).encode()
        ).hexdigest(),
        "provenance": "reconstructed_through_producer_input_route",
        "NOT": "read_from_G",
    }


def read_flat_source(ROOT, path: Path, read_prefix: str, nbins: int, reads: list) -> dict:
    """Declared read 3: the central CV's key listing and hXSecND_flat contents."""
    handle = open_root_file(ROOT, path)
    try:
        listing = key_listing(handle)
        present = {entry["name"] for entry in listing}
        record(reads, f"{read_prefix}:key_listing", "read",
               REQUIRED_ABSENCE_IS_A_FAILURE, key_count=len(listing))
        out: dict[str, object] = {"key_listing": listing}
        if "hXSecND_flat" not in present:
            record(reads, f"{read_prefix}:hXSecND_flat", "absent",
                   REQUIRED_ABSENCE_IS_A_FAILURE,
                   detail="declared required object absent from this file")
            return out
        hist = handle.Get("hXSecND_flat")
        digest = flat_digest(hist, nbins)
        out["hXSecND_flat"] = digest
        record(reads, f"{read_prefix}:hXSecND_flat", "read",
               REQUIRED_ABSENCE_IS_A_FAILURE, **digest)
        return out
    finally:
        handle.Close()


def read_endpoint(ROOT, path: Path, label: str, nbins: int, optional_names: list[str],
                  reads: list) -> dict:
    """Declared read 4: one endpoint, closed before the next is opened."""
    out: dict[str, object] = {}
    handle = open_root_file(ROOT, path)
    try:
        listing = key_listing(handle)
        present = {entry["name"] for entry in listing}
        out["key_listing"] = listing
        record(reads, f"{label}:key_listing", "read", REQUIRED_ABSENCE_IS_A_FAILURE,
               key_count=len(listing))

        if "hXSecND_flat" in present:
            digest = flat_digest(handle.Get("hXSecND_flat"), nbins)
            out["hXSecND_flat"] = digest
            record(reads, f"{label}:hXSecND_flat", "read",
                   REQUIRED_ABSENCE_IS_A_FAILURE, **digest)
        else:
            record(reads, f"{label}:hXSecND_flat", "absent",
                   REQUIRED_ABSENCE_IS_A_FAILURE,
                   detail="declared required object absent from this endpoint")

        for axis in ("pt", "pz", "eavail", "q3", "W"):
            name = f"hXSec_{axis}"
            read_id = f"{label}:{name}"
            if name not in present:
                record(reads, read_id, "absent", REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail="declared axis histogram absent")
                continue
            hist = handle.Get(name)
            count = int(hist.GetNbinsX())
            edges = [float(hist.GetBinLowEdge(index + 1)) for index in range(count)]
            edges.append(float(hist.GetBinLowEdge(count) + hist.GetBinWidth(count)))
            out[name] = {"nbins": count, "edges": edges}
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE,
                   nbins=count, first_edge=edges[0], last_edge=edges[-1])

        for scalar in ("ndim", "dataPOT", "globalCompleteness"):
            read_id = f"{label}:{scalar}"
            if scalar not in present:
                record(reads, read_id, "absent", REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail="declared scalar absent")
                continue
            obj = handle.Get(scalar)
            value = getattr(obj, "GetTitle", lambda: None)() if obj else None
            out[scalar] = value
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, value=value)

        # "when present" in the predeclaration: absence is an expected outcome.
        for name in optional_names:
            read_id = f"{label}:{name}"
            if name in present:
                obj = handle.Get(name)
                value = getattr(obj, "GetTitle", lambda: None)() if obj else None
                out[name] = value
                record(reads, read_id, "read", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=True, value=value)
            else:
                record(reads, read_id, "absent", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=False, detail="declared as 'when present'")
        return out
    finally:
        handle.Close()


def declared_read_ids(bindings: dict) -> list[str]:
    """Every read this producer is required to emit a record for, computed from bindings.

    The validator compares the report against this same list, so a read that is silently
    skipped is INCOMPLETE rather than invisible.
    """
    ids = [f"input:{entry['id']}" for entry in bindings["inputs"]]
    ids += ["G:key_listing", "G:combined_source", "G:centering_convention",
            "G:sqrt_tr_old", "G:sqrt_tr_new", "G:hInflation_g_nbins"]
    ids += [f"G:{name}" for name in bindings["optional_objects"]["G"]]
    ids += ["CS:key_listing", "CV_central:key_listing", "CV_central:hXSecND_flat"]
    for band in bindings["bands"]:
        for endpoint in (0, 1):
            label = f"EP_{band}_{endpoint}"
            ids += [f"{label}:key_listing", f"{label}:hXSecND_flat"]
            ids += [f"{label}:hXSec_{axis}" for axis in ("pt", "pz", "eavail", "q3", "W")]
            ids += [f"{label}:{scalar}" for scalar in ("ndim", "dataPOT",
                                                       "globalCompleteness")]
            ids += [f"{label}:{name}"
                    for name in bindings["optional_objects"]["endpoint"]]
    return ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="ABSOLUTE run directory, outside every git checkout")
    args = parser.parse_args(argv)

    out_dir = args.out
    refuse_output_inside_a_checkout(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bindings = json.loads(args.bindings.read_text())
    reads: list[dict] = []
    report: dict[str, object] = {
        "schema_version": 1,
        "started_at_utc": utcnow(),
        "bindings_sha256": hashlib.sha256(args.bindings.read_bytes()).hexdigest(),
        "data_root": str(args.data_root),
        "out_dir": str(out_dir),
        "declared_read_ids": declared_read_ids(bindings),
        "capture_note": (
            "COMPLETE means the declared measurements were captured. It is not a "
            "scientific grade and it is not a statement that anything is discharged."
        ),
        "pm4_provenance": (
            "Digests here are reconstructed through G's producer-input route. G's own "
            "hash receipt does not bind the central CV, so nothing here establishes what "
            "G consumed historically. Never relabel these as read_from_G."
        ),
    }
    exit_code = EXIT_COMPLETE

    try:
        import ROOT  # noqa: PLC0415 -- deliberately late: the env is sourced by the caller
        ROOT.gROOT.SetBatch(True)
        ROOT.gErrorIgnoreLevel = ROOT.kWarning
        report["root_version"] = ROOT.gROOT.GetVersion()
        report["module_provenance"] = module_provenance(str(args.data_root))

        resolved = bind_inputs(bindings, args.data_root, reads)
        missing = [entry["id"] for entry in bindings["inputs"]
                   if entry["id"] not in resolved]
        if missing:
            report["fatal"] = f"required inputs unusable: {', '.join(sorted(missing))}"
            exit_code = EXIT_ERROR
        else:
            nbins = int(bindings["grid_nbins"])
            report["G"] = read_G(ROOT, resolved["G"],
                                 bindings["optional_objects"]["G"], reads)
            report["CS"] = read_CS(ROOT, resolved["CS"], reads)
            report["CV_central"] = read_flat_source(
                ROOT, resolved["CV_central"], "CV_central", nbins, reads)
            endpoints: dict[str, object] = {}
            for band in bindings["bands"]:
                for endpoint in (0, 1):
                    label = f"EP_{band}_{endpoint}"
                    endpoints[label] = read_endpoint(
                        ROOT, resolved[label], label, nbins,
                        bindings["optional_objects"]["endpoint"], reads)
            report["endpoints"] = endpoints
    except Exception:  # noqa: BLE001 -- error evidence is preserved, not swallowed
        report["traceback"] = traceback.format_exc()
        exit_code = EXIT_ERROR

    report["reads"] = reads
    seen = {entry["read_id"] for entry in reads}
    report["missing_read_records"] = sorted(
        set(report["declared_read_ids"]) - seen)
    report["finished_at_utc"] = utcnow()
    if exit_code == EXIT_COMPLETE and report["missing_read_records"]:
        exit_code = EXIT_INCOMPLETE
    report["producer_exit_code"] = exit_code

    (out_dir / "pm-inspection-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"exit_code": exit_code,
                      "records": len(reads),
                      "missing_read_records": len(report["missing_read_records"])}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
