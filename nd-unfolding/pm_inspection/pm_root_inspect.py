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
import time
import subprocess
import re
import shlex
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

    ``forbidden_root`` must be the root the BINDINGS declare, not the one argv happens to
    name.  Aimed at argv, a wrong ``--data-root`` both read the wrong tree and re-pointed
    this measurement away from the tree it exists to watch, so the offender list came back
    empty for an import from the declared root -- an empty list from a measurement aimed
    somewhere else says nothing at all.  The validator compares all three: the bindings'
    root, the report's ``data_root``, and this ``forbidden_root``.
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
        ``(value, class_name)``; ``value`` is ``None`` when the object is null, carries
        neither a typed value nor a title, or carries an EMPTY title, all of which callers
        must treat as a fault.  A typed ``0.0`` is a measurement and is returned; an empty
        title is not a measurement of anything, and emitting ``status=read, value=""``
        would be the same hollow record with the null replaced by an empty value.
    """
    obj = handle.Get(name)
    if not obj:
        return None, None
    class_name = obj.ClassName() if hasattr(obj, "ClassName") else type(obj).__name__
    if hasattr(obj, "GetVal"):
        return obj.GetVal(), class_name
    if hasattr(obj, "GetTitle"):
        title = obj.GetTitle()
        return (title if isinstance(title, str) and title.strip() else None), class_name
    return None, class_name


def why_this_object_cannot_be_digested(obj, needs: tuple[str, ...]) -> str | None:
    """Why a listed object cannot be read as a histogram, or ``None`` if it can.

    A listed key whose object will not load, or which loads as something these reads
    cannot be performed on, is ONE ``unreadable`` record and the capture continues.  Round
    2 added that check for ``hInflation_g`` and nowhere else, so a listed-but-null
    ``hXSecND_flat`` or axis histogram was dereferenced straight away: the
    ``AttributeError`` came out of the middle of the first endpoint and cost 21 of the 38
    declared reads, and ``retry_policy.requires_new_authorization`` means a re-run is not
    free.  One bad object must cost one record.
    """
    if not obj:
        return "listed key did not load"
    missing = [name for name in needs if not hasattr(obj, name)]
    if missing:
        return f"loaded object exposes no {', '.join(missing)}"
    return None


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
            # A listed key whose object will not load is a FAULT. Emitting
            # `status=read, nbins=None` reported a measurement that never happened.
            unreadable = why_this_object_cannot_be_digested(hist, ("GetNbinsX",))
            if unreadable:
                record(reads, "G:hInflation_g_nbins", "unreadable",
                       REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail=f"hInflation_g is listed but {unreadable}")
            else:
                nbins = int(hist.GetNbinsX())
                out["hInflation_g_nbins"] = nbins
                record(reads, "G:hInflation_g_nbins", "read",
                       REQUIRED_ABSENCE_IS_A_FAILURE, nbins=nbins)
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
                    # The kind is the one the BINDINGS give this id. Stamping it
                    # `required` here made the validator additionally accuse an honest
                    # producer of reclassifying its own obligation; the verdict was right
                    # and the accusation was not. `status` carries the fault, `kind`
                    # carries the obligation, and they are different questions.
                    record(reads, read_id, "unreadable", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                           present=True,
                           detail="key listed but object could not be read; that is a "
                                  "fault, not the declared absence")
                    out[f"{name}_present"] = None
                    continue
                # If a row index IS there, the count is not the measurement -- the row
                # contents are, because PM-4 compares an index digest against S.
                contents = row_index_contents(obj)
                out[f"{name}_present"] = True
                out[name] = contents
                if not contents.get("contents_readable"):
                    # It loaded and could not be digested. That is the same fault as a
                    # key that did not load: we did not learn what the row index holds,
                    # which is not the declared absence and is not a measurement of the
                    # one object PM-4's premise turns on.
                    record(reads, read_id, "unreadable", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                           present=True, **contents)
                    continue
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
        unreadable = why_this_object_cannot_be_digested(
            hist, ("GetNbinsX", "GetBinContent"))
        if unreadable:
            record(reads, f"{read_prefix}:hXSecND_flat", "unreadable",
                   REQUIRED_ABSENCE_IS_A_FAILURE,
                   detail=f"hXSecND_flat is listed but {unreadable}")
            return out
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
            hist = handle.Get("hXSecND_flat")
            unreadable = why_this_object_cannot_be_digested(
                hist, ("GetNbinsX", "GetBinContent"))
            if unreadable:
                record(reads, f"{label}:hXSecND_flat", "unreadable",
                       REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail=f"hXSecND_flat is listed but {unreadable}")
            else:
                digest = flat_digest(hist, nbins)
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
            unreadable = why_this_object_cannot_be_digested(
                hist, ("GetNbinsX", "GetBinLowEdge", "GetBinWidth"))
            if unreadable:
                record(reads, read_id, "unreadable", REQUIRED_ABSENCE_IS_A_FAILURE,
                       detail=f"{name} is listed but {unreadable}")
                continue
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
                    # `status` carries the fault; `kind` carries the obligation the
                    # BINDINGS give this id. Stamping an optional object `required` here
                    # made the validator accuse an honest producer of reclassifying its
                    # own obligation on top of a verdict that was already correct.
                    record(reads, read_id, "unreadable", OPTIONAL_ABSENCE_IS_AN_ANSWER,
                           present=True, root_class=class_name,
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


def obligation_kinds(bindings: dict) -> dict[str, str]:
    """Map every obligation to the kind the BINDINGS give it, not the kind a record claims.

    An earlier revision let each record carry its own ``kind``, so relabelling
    ``input:G`` as ``expected-optional`` and marking it ``absent`` produced ``COMPLETE``:
    the producer could downgrade its own obligations. The authority for whether an absence
    is an answer or a fault is the committed bindings, and only these ids are optional:
    the conditional reads the predeclaration writes as "only if the listing shows it" and
    "when present".

    THE VALIDATOR NO LONGER CALLS THIS.  It used to, which meant the terminal validator
    derived its obligations from the producer's own code; a mutation here moved both halves
    together and the skew was invisible.  It now keeps its own table and the tests hold
    both to a third restatement of the predeclaration.
    """
    kinds: dict[str, str] = {}
    for entry in bindings["inputs"]:
        kinds[f"input:{entry['id']}"] = REQUIRED_ABSENCE_IS_A_FAILURE
    for read_id in ("G:key_listing", "G:combined_source", "G:centering_convention",
                    "G:sqrt_tr_old", "G:sqrt_tr_new", "G:hInflation_g_nbins",
                    "G:read_onlyness", "CS:key_listing", "CV_central:key_listing",
                    "CV_central:hXSecND_flat"):
        kinds[read_id] = REQUIRED_ABSENCE_IS_A_FAILURE
    for name in bindings["optional_objects"]["G"]:
        kinds[f"G:{name}"] = OPTIONAL_ABSENCE_IS_AN_ANSWER
    for band in bindings["bands"]:
        for endpoint in (0, 1):
            label = f"EP_{band}_{endpoint}"
            required = [f"{label}:key_listing", f"{label}:hXSecND_flat"]
            required += [f"{label}:hXSec_{axis}"
                         for axis in ("pt", "pz", "eavail", "q3", "W")]
            required += [f"{label}:{scalar}"
                         for scalar in ("ndim", "dataPOT", "globalCompleteness")]
            for read_id in required:
                kinds[read_id] = REQUIRED_ABSENCE_IS_A_FAILURE
            for name in bindings["optional_objects"]["endpoint"]:
                kinds[f"{label}:{name}"] = OPTIONAL_ABSENCE_IS_AN_ANSWER
    return kinds


# --------------------------------------------------------------------------- launch mode

#: What campaignctl sets; its parent IS the exclusive claim run directory.
CAMPAIGN_TASK_IDS_FILE_ENV = "MNV_CAMPAIGN_TASK_IDS_FILE"
#: Scheduler task identity, in the exact form r5_meter.py publishes.
TASK_ID_RE = re.compile(r"^[0-9]+(?:_[0-9]+)?$")
#: `sbatch --parsable` prints `<jobid>` or `<jobid>;<cluster>`, ONE line per submission.
PARSABLE_LINE_RE = re.compile(r"^(?P<id>[0-9]+(?:_[0-9]+)?)(?:;[^;\s]+)?$")

#: Measured from the controller 2026-09-08: debug MaxWall 00:30:00, UsageFactor 1.000000,
#: identical factor to interactive, and present in account m3246's association list.
DEFAULT_QOS = "debug"
DEFAULT_MINUTES = 25

EXIT_SUBMISSION_UNCERTAIN = 30


class SubmissionUncertain(Exception):
    """A job may or may not exist, and the reservation must be retained."""


def parse_parsable_receipt(stdout: str) -> str:
    """Return the one job id in an ``sbatch --parsable`` receipt, or refuse.

    A receipt this function cannot read is UNKNOWN, never "the first thing that looks like an
    id". Truncating a multi-line receipt to its first entry would leave later jobs running with
    nobody holding their identity, and cancelling an unvalidated raw string could name a job
    this item never created. Both failure modes end here as SubmissionUncertain with the raw
    receipt preserved for a human.
    """
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise SubmissionUncertain(
            f"sbatch receipt is not one line ({len(lines)}): {stdout!r}. One or more jobs may "
            "exist and cannot be named; nothing will be cancelled on an unvalidated string")
    match = PARSABLE_LINE_RE.fullmatch(lines[0])
    if match is None:
        raise SubmissionUncertain(
            f"sbatch receipt {lines[0]!r} is not a parsable job identity; a job may exist and "
            "cannot be named")
    return match.group("id")


def submit_one_job(wrap_command: str, *, run_dir: Path, account: str, qos: str,
                   minutes: int, comment: str) -> str:
    """Submit exactly one CPU job and return its validated id.

    Validation happens on the RECEIPT, before any caller can lose it, and this function never
    writes a file: recording is the caller's job so a write failure cannot destroy an id this
    function already knows. A non-zero sbatch is NOT proof that no job was created -- an
    acknowledgement can be lost after the scheduler accepted it.
    """
    argv = [
        "sbatch", "--parsable", "--comment", comment,
        "--nodes", "1", "--ntasks", "1", "--constraint", "cpu",
        "--time", str(minutes), "--account", account, "--qos", qos,
        "--no-requeue", "--export=ALL",
        "--output", str(run_dir / "job.log"),
        "--wrap", wrap_command,
    ]
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        raise SubmissionUncertain(f"sbatch could not be run or did not answer: {error}")
    if completed.returncode != 0:
        raise SubmissionUncertain(
            f"sbatch exited {completed.returncode}: {completed.stderr.strip()[:200]!r}. This "
            f"is NOT evidence that no job was created; recoverable by --comment {comment}")
    return parse_parsable_receipt(completed.stdout)


def write_task_ids(path: Path, job_id: str) -> None:
    """Record the identity. The caller must already hold ``job_id`` if this raises."""
    path.write_text(json.dumps([job_id]) + "\n")


def job_state(job_id: str) -> tuple[str | None, str]:
    """Return (terminal_state, detail). ``None`` means NOT KNOWN to be terminal.

    A non-zero ``sacct`` or a timeout is unknown, never terminal: an exit code of 1 with a
    stale COMPLETED on stdout would otherwise read as a finished job.
    """
    terminal = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
                "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE", "PREEMPTED"}
    try:
        probe = subprocess.run(
            ["sacct", "-j", job_id, "-X", "-n", "-P", "-o", "State"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"sacct did not answer: {error}"
    if probe.returncode != 0:
        return None, f"sacct exited {probe.returncode}; state is unknown, not terminal"
    states = [line.split()[0] for line in probe.stdout.splitlines() if line.strip()]
    if not states:
        return None, "sacct returned no rows; state is unknown"
    if all(state in terminal for state in states):
        return states[0], "terminal"
    return None, f"not terminal: {states[0]}"


def wait_for_job(job_id: str, *, deadline: float, poll_seconds: int = 20) -> tuple[str | None, str]:
    """Poll until terminal or the deadline passes."""
    detail = "deadline passed before any probe"
    while time.time() < deadline:
        state, detail = job_state(job_id)
        if state is not None:
            return state, detail
        time.sleep(poll_seconds)
    return None, detail


def cancel_this_job(job_id: str) -> dict[str, object]:
    """Cancel by id only, then VERIFY. A successful request is not a terminated job."""
    result: dict[str, object] = {"job_id": job_id, "cancel_requested": True}
    try:
        completed = subprocess.run(["scancel", job_id], capture_output=True, text=True,
                                   timeout=60)
        result["scancel_returncode"] = completed.returncode
        result["scancel_stderr"] = completed.stderr.strip()[:200]
    except (OSError, subprocess.SubprocessError) as error:
        result["scancel_returncode"] = None
        result["scancel_error"] = str(error)
    state, detail = job_state(job_id)
    result["terminal_state"] = state
    result["verification"] = detail
    result["cleanup"] = "verified-terminal" if state is not None else "UNRESOLVED"
    return result


def launch(args, run_dir: Path, task_ids_path: Path) -> int:
    """Submit one job, record it, wait bounded, and never leave without accounting for it."""
    wrap = shlex.join([
        args.inner_python, "nd-unfolding/mnv_guarded_run.py",
        "--expect-root", str(args.expect_root),
        "--label", "pm-root-inspection-read",
        "--", "nd-unfolding/pm_inspection/pm_root_inspect.py",
        "--mode", "read",
        "--bindings", str(args.bindings),
        "--data-root", str(args.data_root),
        "--attempt-id", run_dir.name,
        "--out", str(run_dir),
    ])
    job_id: str | None = None
    outcome: dict[str, object] = {}
    try:
        try:
            job_id = submit_one_job(wrap, run_dir=run_dir, account=args.account,
                                    qos=args.qos, minutes=args.minutes,
                                    comment=args.comment)
        except SubmissionUncertain as error:
            (run_dir / "submission-uncertain.txt").write_text(str(error) + "\n")
            outcome = {"submission": "uncertain", "reservation": "RETAINED",
                       "detail": str(error)}
            return EXIT_SUBMISSION_UNCERTAIN

        # The id is known from here on. A failure to RECORD it must not lose it.
        try:
            write_task_ids(task_ids_path, job_id)
            outcome["task_ids_written"] = True
        except OSError as error:
            outcome["task_ids_written"] = False
            outcome["task_ids_error"] = f"{type(error).__name__}: {error}"
            (run_dir / "task-ids-write-failed.txt").write_text(
                json.dumps({"job_id": job_id, "error": str(error)}) + "\n")

        state, detail = wait_for_job(job_id, deadline=time.time() + args.minutes * 60 + 120)
        outcome.update({"job_id": job_id, "state": state, "detail": detail})
        if state is None:
            return EXIT_ERROR
        return EXIT_COMPLETE if state == "COMPLETED" else EXIT_ERROR
    finally:
        # Scoped cleanup: only ever this job, only when it is not known terminal.
        if job_id is not None and outcome.get("state") is None:
            outcome["cleanup_attempt"] = cancel_this_job(job_id)
        print(json.dumps(outcome, sort_keys=True))


def declared_read_ids(bindings: dict) -> list[str]:
    """Every read this producer must emit a record for, in a stable order."""
    return list(obligation_kinds(bindings).keys())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("read", "launch"), default="read",
                        help="launch: submit one job and wait. read: perform the reads.")
    parser.add_argument("--inner-python",
                        default="/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python",
                        help="interpreter inside the job; must supply PyROOT. Verified "
                             "2026-09-08 to run the guard to exit 0 on a login node.")
    parser.add_argument("--expect-root", type=Path,
                        default=Path("/pscratch/sd/j/josephrb/exec-20260907"))
    parser.add_argument("--account", default="m3246")
    parser.add_argument("--qos", default=DEFAULT_QOS)
    parser.add_argument("--minutes", type=int, default=DEFAULT_MINUTES)
    parser.add_argument("--comment", default="pm-root-inspection-20260908")
    parser.add_argument("--attempt-id",
                        help="binds this report to THIS attempt; the validator requires it")
    parser.add_argument("--out", type=Path,
                        help="ABSOLUTE run directory, outside every git checkout")
    args = parser.parse_args(argv)

    if args.mode == "launch":
        # No standalone fallback. Launch mode exists only inside a claim: deriving the run
        # directory from --out while taking the task-ids path from the queue is how the
        # producer ends up writing its report somewhere the validator will never look.
        raw = os.environ.get(CAMPAIGN_TASK_IDS_FILE_ENV)
        if not raw:
            raise SystemExit(
                f"--mode launch requires {CAMPAIGN_TASK_IDS_FILE_ENV}; it is set by the queue "
                "under an exclusive claim and there is no standalone launch path")
        task_ids_path = Path(raw)
        claim_dir = task_ids_path.parent
        refuse_output_inside_a_checkout(claim_dir)
        claim_dir.mkdir(parents=True, exist_ok=True)
        return launch(args, claim_dir, task_ids_path)

    if args.mode == "read" and (args.out is None or args.attempt_id is None):
        parser.error("--mode read requires --out and --attempt-id")
    out_dir = args.out if args.out is not None else Path.cwd()
    if args.mode == "read":
        refuse_output_inside_a_checkout(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # The contract carries a FIXED attempt id, so a second run into the same directory
    # would overwrite the first attempt's evidence and present itself as that attempt.
    # Refuse instead: a new attempt needs a new id and a new run directory.
    report_path = out_dir / "pm-inspection-report.json"
    if report_path.exists():
        raise SystemExit(
            f"{report_path} already exists; attempt ids are not reusable. Use a fresh "
            "run directory and a fresh --attempt-id rather than overwriting evidence."
        )


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
        # Aimed at the DECLARED root, never at argv: see module_provenance's docstring.
        report["module_provenance"] = module_provenance(str(bindings["data_root"]))

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

    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"exit_code": exit_code,
                      "records": len(reads),
                      "missing_read_records": len(report["missing_read_records"])}))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
