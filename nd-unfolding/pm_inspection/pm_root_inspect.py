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
    # Resolve first. A symlink whose TARGET is inside a checkout passes a purely lexical
    # walk while writing into the working tree, which is the whole thing this refuses.
    resolved = Path(os.path.realpath(out_dir))
    for candidate in {out_dir, resolved}:
        for parent in [candidate, *candidate.parents]:
            if (parent / ".git").exists():
                raise SystemExit(
                    f"--out {out_dir} resolves to {resolved}, inside the git checkout at "
                    f"{parent}; runtime output must live outside every checkout"
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


def read_scalar(handle, name: str):
    """Read a stored scalar by its ACTUAL type, not by assuming TNamed.

    ``adopt_unified_5d.py:177`` writes ``sqrt_tr_old`` as ``TParameter<double>``, whose
    value lives in ``GetVal()``; ``GetTitle()`` on it returns the title string, not the
    number.  ``p4_evidence.py:88`` is the precedent for reading the typed value.  Returning
    a title where a double was meant is a silently wrong measurement, so this dispatches on
    what the object actually is and reports the class it saw.

    Returns
    -------
    tuple
        ``(value, class_name)``; ``value`` is ``None`` only when the object is null or
        carries neither a typed value nor a title, which callers must treat as a fault.
    """
    obj = handle.Get(name)
    if not obj:
        return None, None
    class_name = obj.ClassName() if hasattr(obj, "ClassName") else type(obj).__name__
    if hasattr(obj, "GetVal"):
        return obj.GetVal(), class_name
    if hasattr(obj, "GetTitle"):
        return obj.GetTitle(), class_name
    return None, class_name


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


def row_index_contents(obj) -> dict[str, object]:
    """Digest a present row index by its CONTENTS, in the predeclared spelling.

    A count is not a measurement of a row index: two different indices share a length.
    PM-4 compares ``row_index_sha256`` against S, so if ``hRowIndex5D`` turns out to be
    present the contents are what has to be captured.
    """
    import numpy as np  # noqa: PLC0415

    if hasattr(obj, "GetNbinsX"):
        count = int(obj.GetNbinsX())
        values = np.array(
            [obj.GetBinContent(index + 1) for index in range(count)], dtype=np.float64)
    elif hasattr(obj, "GetSize"):
        count = int(obj.GetSize())
        values = np.array([obj[index] for index in range(count)], dtype=np.float64)
    else:
        return {"contents_readable": False,
                "detail": "object exposes neither GetNbinsX nor GetSize"}
    idx = values.astype(np.int64)
    raw = idx.tobytes()
    return {
        "contents_readable": True,
        "count": int(idx.size),
        "row_index_sha256": hashlib.sha256(raw).hexdigest(),
        "reported_mask_hash": hashlib.sha256(raw + b"|C").hexdigest(),
        "row_index_matches_S": (
            hashlib.sha256(raw).hexdigest() == S_ROW_INDEX_SHA256),
        "provenance": "read_from_G",
    }


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
            value, class_name = read_scalar(handle, scalar)
            if value is None:
                record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                       root_class=class_name,
                       detail="key present but object is null or carries no value")
                continue
            out[scalar] = value
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, value=value,
                   root_class=class_name)

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
                if not obj:
                    record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                           detail="key listed but object could not be read; that is a "
                                  "fault, not the declared absence")
                    out[f"{name}_present"] = None
                    continue
                # If a row index IS there, the count is not the measurement -- the row
                # contents are, because PM-4 compares an index digest against S.
                contents = row_index_contents(obj)
                out[f"{name}_present"] = True
                out[name] = contents
                record(reads, read_id, "read", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=True, **contents)
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


#: S's committed comparands, PREDECLARATION section 4 and
#: nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json.
#: Comparison is exact digest equality, no tolerance.
S_REPORTED_MASK_HASH = "74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a"
S_ROW_INDEX_SHA256 = "61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08"
S_EXPECTED_COUNT = 10694


def mask_digests(central) -> dict[str, object]:
    """The PREDECLARED digest algorithm, not an invented one.

    From PREDECLARATION section 4, which cites ``p4_evidence.py:78-84``,
    ``p4_lib.py:1209-1218`` and ``p4_build_components.py:198-203,224-230``:

        mask               = central > 0            # strictly greater, NOT != 0
        idx                = np.nonzero(mask)[0].astype(np.int64)
        reported_mask_hash = sha256(idx.tobytes() + b"|C")
        row_index_sha256   = sha256(idx.tobytes())

    Zero-based ascending global indices on the C-order (pt,pz,eavail,q3,W) grid, native
    byte order, no rounding.  ``central > 0`` and ``central != 0`` differ on negative bins,
    and a JSON rendering of booleans is not ``idx.tobytes()``: an earlier revision of this
    file used both wrong spellings and would have produced digests that could never match
    S while looking plausible.

    Parameters
    ----------
    central : numpy.ndarray
        The regular bins only, under/overflow already excluded.
    """
    import numpy as np  # noqa: PLC0415 -- the declared algorithm is a numpy one

    mask = central > 0
    idx = np.nonzero(mask)[0].astype(np.int64)
    raw = idx.tobytes()
    return {
        "count": int(idx.size),
        "expected_count": S_EXPECTED_COUNT,
        "count_matches_S": int(idx.size) == S_EXPECTED_COUNT,
        "row_index_sha256": hashlib.sha256(raw).hexdigest(),
        "reported_mask_hash": hashlib.sha256(raw + b"|C").hexdigest(),
        "row_index_matches_S": hashlib.sha256(raw).hexdigest() == S_ROW_INDEX_SHA256,
        "reported_mask_matches_S": (
            hashlib.sha256(raw + b"|C").hexdigest() == S_REPORTED_MASK_HASH),
        "byte_order": sys.byteorder,
        "dtype": "int64",
        "provenance": "reconstructed_through_producer_input_route",
        "NOT": "read_from_G",
    }


def flat_digest(hist, declared_nbins: int) -> dict[str, object]:
    """Digest ``hXSecND_flat``'s regular bins, checking the grid rather than assuming it.

    ``declared_nbins`` is what the bindings SAY the grid is.  The histogram's own
    ``GetNbinsX()`` is what it IS.  Reporting the former as if it were the latter is how a
    grid non-conformance -- exactly what PM-3's grid arm exists to detect -- gets reported
    as conformance, so both are recorded and any disagreement is a measured mismatch.
    """
    import numpy as np  # noqa: PLC0415

    measured_nbins = int(hist.GetNbinsX())
    central = np.array(
        [float(hist.GetBinContent(index + 1)) for index in range(measured_nbins)],
        dtype=np.float64,
    )
    digests = mask_digests(central)
    digests.update({
        "declared_nbins": int(declared_nbins),
        "measured_nbins": measured_nbins,
        "nbins_conforms": measured_nbins == int(declared_nbins),
        "all_finite": bool(np.isfinite(central).all()),
        "content_sha256": hashlib.sha256(central.tobytes()).hexdigest(),
    })
    return digests


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
            value, class_name = read_scalar(handle, scalar)
            if value is None:
                record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                       root_class=class_name,
                       detail="key present but object is null or carries no value")
                continue
            out[scalar] = value
            record(reads, read_id, "read", REQUIRED_ABSENCE_IS_A_FAILURE, value=value,
                   root_class=class_name)

        # "when present" in the predeclaration: absence is an expected outcome. A key that
        # is listed but unreadable is NOT that outcome -- it is a fault.
        for name in optional_names:
            read_id = f"{label}:{name}"
            if name in present:
                value, class_name = read_scalar(handle, name)
                if value is None:
                    record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                           root_class=class_name,
                           detail="key listed but unreadable; not the declared absence")
                    continue
                out[name] = value
                record(reads, read_id, "read", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                       present=True, value=value, root_class=class_name)
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
            "G:sqrt_tr_old", "G:sqrt_tr_new", "G:hInflation_g_nbins",
            "G:read_onlyness"]
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
    parser.add_argument("--attempt-id", required=True,
                        help="binds this report to THIS attempt; the validator requires it")
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
        "attempt_id": args.attempt_id,
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
            # PREDECLARATION section 4: G's sha256 before and after, so read-onlyness for G
            # is MEASURED. CS is 41.4 GB and is not re-hashed, so its read-onlyness stays
            # asserted-by-opening-READ and is recorded as a limitation, never as a proof.
            g_before = sha256_file(resolved["G"])
            report["G"] = read_G(ROOT, resolved["G"],
                                 bindings["optional_objects"]["G"], reads)
            g_after = sha256_file(resolved["G"])
            unchanged = g_before == g_after
            report["G_read_onlyness"] = {
                "sha256_before": g_before,
                "sha256_after": g_after,
                "unchanged": unchanged,
                "basis": "measured by before/after digest",
            }
            record(reads, "G:read_onlyness",
                   "read" if unchanged else "unreadable",
                   REQUIRED_ABSENCE_IS_A_FAILURE,
                   sha256_before=g_before, sha256_after=g_after, unchanged=unchanged,
                   detail=None if unchanged else
                   "G CHANGED ACROSS THE INSPECTION; the read was not read-only")
            report["CS_read_onlyness"] = {
                "basis": "asserted by opening READ; NOT proven by digest",
                "reason": "41,436,632,945 bytes; a before/after digest is excluded",
            }
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
