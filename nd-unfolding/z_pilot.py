#!/usr/bin/env python3
"""Assembly/spectrum pilot: bind the real inputs, run the existing build, persist the spectrum.

THREE THINGS, AND THE MIDDLE ONE IS NOT NEW. `build_manifest` writes the version-1 declaration
`z_build.build_z` already validates; `run_pilot` invokes the existing CLI and then establishes
what its exit code does NOT establish; `spectrum_diagnostics` records the eigenvalue spectrum
that Z_BUILD.md requirement 8 defers to "a separately assessed resource plan". No construction
gate, criterion, tolerance or assembly step is reimplemented here.

WHY EXIT 2 NEEDS ITS OWN VALIDATOR. `z_build.main` returns 2 for "the build RAN TO COMPLETION
and its science is NON-PASSING", which is its ONLY completion code -- and Z_BUILD.md states
outright that 2 "is not, on its own, proof that the artifacts exist". A hard kill between the
product write and the receipt write leaves exit-2-shaped wreckage. Two failure modes are
therefore refused here, and they are opposite:

  * TREATING 2 AS SUCCESS. `rc == 2` with a missing receipt, or a receipt whose recorded product
    digest does not match the file beside it, is an INCOMPLETE build.
  * CONVERTING 2 TO 0. A wrapper that maps 2 to 0 destroys the only signal distinguishing
    "completed, non-passing" from "passed", and non-passing is the correct and permanent status
    of this construction. This pilot's own exit code keeps 2 for that outcome.

NO INVENTED NUMBERS. The spectrum is REPORTED, never clipped, floored or regularized: negative
eigenvalues are counted and their magnitudes recorded relative to lambda_max, which is what
`z_assembly.gate_symmetry_psd` already does for the PSD decision. That gate keeps its own
scale-free `lam_min >= -rtol * lam_max` verdict and this module does not second-guess it. No
kappa, no null tolerance, no eigenvalue floor is introduced -- Z_BUILD.md requirements 3 and 5
leave those to an approver.

THE SPECTRUM IS A SECOND, INDEPENDENT EIGENSOLVE, and that is recorded rather than hidden. The
PSD gate computes `eigvalsh` inside `build_z` and discards everything but the extrema; reaching
into it to harvest `w` would mean threading a sink through `build_z` and `_verify_products` and
changing a function every existing Z test exercises. Measuring the CLOSED artifact instead costs
one more decomposition per variant -- which is precisely the cost requirement 8 asks the pilot
to establish -- and buys an independent check of the shipped bytes rather than of an in-memory
array. The cost is priced in the execution request, not absorbed silently.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np

import p4_lib as p4
import z_build as build
import z_build_path as build_path
import z_contract as contract
import z_receipt as receipt
import z_statistics as statistics

PILOT_SCHEMA_VERSION = 1

#: The one completion code the build can produce. Not 0, and not converted to 0.
BUILD_COMPLETION_RC = 2
BUILD_FAILURE_RC = 1

#: Quantiles reported for the spectrum. Fixed so two runs are comparable, and chosen to expose
#: the low end where a PSD problem would live rather than to smooth it away.
SPECTRUM_QUANTILES = (0.0, 0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999, 1.0)

SOURCE_ROLES = ("parent", "central", "support", "active", "stat", "ml", "throw", "null")


# ----------------------------------------------------------------- the digest-bound manifest ---
def build_manifest(
    manifest_path,
    *,
    sources: dict,
    run: dict,
    producing_revision: str,
    stat_key: str,
    ml_key: str,
    input_kind: str = "real",
    allow_overwrite: bool = False,
    provenance_path=None,
) -> dict:
    """Write the version-1 manifest with every declared source bound by measured digest.

    Every digest is COMPUTED from the file on disk, never accepted from the caller: a manifest
    whose hashes were supplied alongside its paths would record the caller's belief about the
    bytes rather than the bytes. A caller that wants to assert an expected digest passes
    `expect_sha256` per role and it is checked against the measurement.

    `footing` is DERIVED from the declared `central`, not declared: `mask_sha256` and
    `row_order_sha256` are what `build_z` recomputes and compares, so computing them here from
    any other object would guarantee a mismatch at build time rather than agreement now.

    Band membership, donor identities and component provenance do not fit in the manifest -- its
    field set is closed and unknown fields fail -- so they are written to a SEPARATE provenance
    record that names the manifest by digest. Preserving them means recording what the actual
    files contain; none of it is invented or reordered here.
    """
    manifest_path = Path(manifest_path).resolve()
    build_path.preservation_guard(str(manifest_path), allow_overwrite=allow_overwrite)
    contract.require(
        set(sources) == set(SOURCE_ROLES),
        f"pilot manifest: expected exactly the roles {sorted(SOURCE_ROLES)}, got "
        f"{sorted(sources)}",
    )
    contract.require(input_kind in ("synthetic", "real"), "pilot manifest: unknown input kind")
    contract.require(
        isinstance(run, dict) and set(run) == {"id", "step"},
        "pilot manifest: run needs exactly `id` and `step`",
    )
    for key, value in run.items():
        contract.require(
            isinstance(value, str) and value.strip(), f"pilot manifest: run {key} is blank"
        )
    contract.require(
        isinstance(producing_revision, str) and len(producing_revision) == 40,
        "pilot manifest: producing_revision must be a full 40-character commit sha",
    )

    declared: dict[str, Any] = {}
    measured: dict[str, Any] = {}
    for role in SOURCE_ROLES:
        spec = sources[role]
        contract.require(
            isinstance(spec, dict) and {"path", "format"} <= set(spec),
            f"pilot manifest: source {role!r} needs `path` and `format`",
        )
        unknown = set(spec) - {"path", "format", "expect_sha256"}
        contract.require(
            not unknown, f"pilot manifest: source {role!r} has unknown field(s) {sorted(unknown)}"
        )
        path = Path(spec["path"]).resolve()
        contract.require(path.is_file(), f"pilot manifest: source {role!r} is not a file: {path}")
        fmt = spec["format"]
        contract.require(
            fmt in ("npz", "root", "opaque"), f"pilot manifest: source {role!r} bad format {fmt!r}"
        )
        if role == "null":
            contract.require(
                fmt == "npz",
                "pilot manifest: the null source must be `npz` -- run `z_null_bridge` on the "
                "producer's ROOT product first; the build reader does not read ROOT nulls.",
            )
        stamp = receipt.stamp_file(path)
        if "expect_sha256" in spec:
            contract.require(
                stamp["sha256"] == spec["expect_sha256"],
                f"pilot manifest: source {role!r} digests to {stamp['sha256']} and the caller "
                f"declared {spec['expect_sha256']}. The file is not the one authorized.",
            )
        declared[role] = {"path": str(path), "format": fmt, "sha256": stamp["sha256"]}
        measured[role] = stamp

    # `footing` from the declared central, computed exactly as `build_z` will recompute it.
    central_decl = dict(declared["central"])
    with build.Source(
        {k: central_decl[k] for k in ("path", "format", "sha256")}, Path("/")
    ) as central_source:
        central = central_source.read("hXSecND_flat")
    mask = statistics.support_mask(central)
    rows = np.flatnonzero(mask).astype(np.int64)
    contract.require(rows.size > 0, "pilot manifest: the declared central has empty support")
    footing = {
        "mask_sha256": receipt.sha256_array(mask),
        "row_order_sha256": receipt.sha256_array(rows),
    }

    manifest = {
        "schema_version": build.SCHEMA_VERSION,
        "input_kind": input_kind,
        "run": dict(run),
        "producing_revision": producing_revision,
        "sources": declared,
        "stat_key": stat_key,
        "ml_key": ml_key,
        "footing": footing,
    }
    receipt.atomic_write_json(manifest_path, manifest)
    manifest_stamp = receipt.stamp_file(manifest_path)

    provenance = _component_provenance(declared, manifest_stamp, mask, rows)
    if provenance_path is not None:
        provenance_path = Path(provenance_path).resolve()
        build_path.preservation_guard(str(provenance_path), allow_overwrite=allow_overwrite)
        receipt.atomic_write_json(provenance_path, provenance)
        provenance["written_to"] = str(provenance_path)
    return {
        "manifest": str(manifest_path),
        "manifest_stamp": manifest_stamp,
        "sources": measured,
        "footing": footing,
        "provenance": provenance,
    }


def _component_provenance(declared: dict, manifest_stamp: dict, mask, rows) -> dict:
    """Record actual band membership, donor identities, support and row order.

    Read from the FILES, in the order the files present them. `build_z` derives the residual
    band set as `inventory - V - A`; the same derivation is recorded here so a reader can see the
    membership that will be used rather than a membership asserted alongside it.
    """
    with build.Source(
        {k: declared["support"][k] for k in ("path", "format", "sha256")}, Path("/")
    ) as support:
        inventory = sorted(
            key[len(build.SUPPORT_PREFIX) :]
            for key in support.keys()
            if key.startswith(build.SUPPORT_PREFIX)
            and key != build.SUPPORT_PREFIX + "total"
        )
    residual = tuple(
        sorted(set(inventory) - set(contract.VERT_BANDS) - set(contract.LATERAL_BANDS))
    )
    partition = contract.check_band_partition(
        contract.VERT_BANDS, residual, contract.LATERAL_BANDS, inventory
    )
    return {
        "pilot_schema_version": PILOT_SCHEMA_VERSION,
        "manifest": manifest_stamp,
        "band_membership": {
            "bands_vert": list(contract.VERT_BANDS),
            "bands_residual": list(residual),
            "bands_lateral": list(contract.LATERAL_BANDS),
            "band_inventory": list(inventory),
            "partition": partition,
            "residual_derivation": "inventory - VERT_BANDS - LATERAL_BANDS, as `build_z` derives it",
        },
        "donor_identities": {
            "lateral_band_keys": {
                band: p4.candidate_band_key(band) for band in contract.LATERAL_BANDS
            },
            "active_total_key": p4.CANDIDATE_ACTIVE_TOTAL_KEY,
            "support_key_prefix": build.SUPPORT_PREFIX,
            "note": (
                "Donor keys are the names this build will read. No band's donor is changed here; "
                "a donor change is a scientific decision, not a packaging one."
            ),
        },
        "support_and_row_order": {
            "n_grid": int(np.asarray(mask).size),
            "n_reported": int(np.asarray(mask).sum()),
            "mask_sha256": receipt.sha256_array(mask),
            "row_order_sha256": receipt.sha256_array(rows),
            "row_order_basis": (
                "C-order flat indices reconstructed from the declared production CV; "
                "NOT read_from_G"
            ),
        },
        "component_provenance": {
            role: declared[role] for role in SOURCE_ROLES
        },
        "adoptable": False,
        "scientific_acceptance": "NON-PASSING",
    }


# -------------------------------------------------------------------- the spectrum diagnostic ---
def spectrum_diagnostics(covariance, *, label: str) -> dict:
    """The full eigenvalue spectrum of one closed covariance, reported and never clipped.

    Returns the extrema, fixed quantiles and the negative tail's size and magnitude. It states no
    verdict: `z_assembly.gate_symmetry_psd` owns the PSD decision with its scale-free
    `lam_min >= -rtol * lam_max`, and duplicating that threshold here would be a second
    implementation of one rule. Reporting `neg_fraction_of_max` in the same units that gate uses
    lets a reader apply ITS criterion to THIS measurement.
    """
    C = np.asarray(covariance, float)
    contract.require(
        C.ndim == 2 and C.shape[0] == C.shape[1], f"spectrum[{label}]: not square, {C.shape}"
    )
    contract.require(np.all(np.isfinite(C)), f"spectrum[{label}]: non-finite entries")
    started = time.monotonic()
    w = np.linalg.eigvalsh(0.5 * (C + C.T))
    elapsed = time.monotonic() - started
    lam_min, lam_max = float(w[0]), float(w[-1])
    contract.require(lam_max > 0, f"spectrum[{label}]: no positive eigenvalue")
    negative = w[w < 0.0]
    return {
        "label": label,
        "n": int(C.shape[0]),
        "method": "numpy.linalg.eigvalsh on 0.5 * (C + C.T)",
        "clipped": False,
        "regularized": False,
        "independent_second_eigensolve": True,
        "lambda_min": lam_min,
        "lambda_max": lam_max,
        "neg_fraction_of_max": abs(min(lam_min, 0.0)) / lam_max,
        "n_negative": int(negative.size),
        "negative_mass_over_trace": (
            float(abs(negative.sum()) / float(np.trace(C))) if np.trace(C) > 0 else None
        ),
        "quantiles": {
            f"q{q:g}": float(np.quantile(w, q)) for q in SPECTRUM_QUANTILES
        },
        "trace": float(np.trace(C)),
        "sqrt_trace": float(np.sqrt(max(float(np.trace(C)), 0.0))),
        "spectrum_sha256": receipt.sha256_array(w),
        "eigensolve_seconds": float(elapsed),
        "verdict": None,
        "why_no_verdict": (
            "z_assembly.gate_symmetry_psd owns the PSD decision and already ran on this closed "
            "object inside the build. Restating its threshold here would be a second "
            "implementation of one rule."
        ),
    }


# -------------------------------------------------------------- the exit-aware build invocation ---
def _validate_completion(rc: int, stdout: str, artifacts: dict) -> dict:
    """Establish what exit 2 does not: that the artifacts exist and match their receipts."""
    if rc == BUILD_FAILURE_RC:
        raise contract.ZContractError(
            f"pilot: the build exited {rc} (construction failed or the invocation was "
            f"malformed). stderr envelope, if any, is the build's own. Nothing is validated."
        )
    contract.require(
        rc == BUILD_COMPLETION_RC,
        f"pilot: the build exited {rc}, and the only completion code this CLI produces is "
        f"{BUILD_COMPLETION_RC}. 0 is reachable only from --help, which writes nothing.",
    )
    try:
        result = json.loads(stdout)
    except ValueError as exc:
        raise contract.ZContractError(
            f"pilot: the build exited {BUILD_COMPLETION_RC} but its stdout is not JSON ({exc}). "
            f"The exit code alone is not evidence of a completed construction."
        ) from exc
    for field, want in (
        ("construction_status", "CHECKED"),
        ("scientific_acceptance", "NON-PASSING"),
    ):
        contract.require(
            result.get(field) == want,
            f"pilot: the build reported {field}={result.get(field)!r}, expected {want!r}.",
        )
    contract.require(
        result.get("adoptable") is False,
        f"pilot: the build reported adoptable={result.get('adoptable')!r}; this construction is "
        f"permanently non-adoptable and a pilot must not record otherwise.",
    )

    missing = [name for name, path in artifacts.items() if not Path(path).is_file()]
    contract.require(
        not missing,
        f"pilot: the build exited {BUILD_COMPLETION_RC} but artifact(s) {sorted(missing)} are "
        f"absent. A hard kill between the product write and the receipt write leaves exactly "
        f"this state, and the exit code cannot distinguish it from a finished build.",
    )

    # Each receipt's recorded product digest, against the file beside it.
    checked = {}
    for variant in ("cv", "mean"):
        receipt_path = Path(artifacts[f"receipt_{variant}"])
        product_path = Path(artifacts[f"out_{variant}"])
        # A torn or foreign receipt raises json.JSONDecodeError (a ValueError) or OSError, and
        # `main` catches only ZContractError -- so without this the structured
        # {"pilot_status": "FAILED", ...} envelope is lost and the launcher mislabels a crash as
        # "the pilot refused". This writer cannot tear a receipt (atomic_write_json uses
        # os.replace); a foreign or interrupted writer can.
        try:
            record = json.loads(receipt_path.read_text())
        except (ValueError, OSError) as exc:
            raise contract.ZContractError(
                f"pilot: receipt {receipt_path.name} could not be read back as JSON ({exc}). "
                f"An unreadable receipt is an incomplete build, not a missing check."
            ) from exc
        recorded = _find_product_sha(record, product_path)
        actual = receipt.sha256_file(product_path)
        contract.require(
            recorded == actual,
            f"pilot: receipt {receipt_path.name} records product sha256 {recorded} and "
            f"{product_path.name} digests to {actual}. The receipt does not describe the file "
            f"shipped with it.",
        )
        checked[variant] = {"receipt": str(receipt_path), "product": str(product_path),
                            "sha256": actual}
    return {"build_result": result, "verified_products": checked}


def _find_product_sha(record: dict, product_path: Path) -> str:
    """Pull the recorded digest for one product out of a receipt, by PATH not by position.

    A receipt carries both variants' stamps, so selecting by index or by insertion order would
    silently compare the cv product against the mean product's digest -- which would pass
    whenever both were written and prove nothing about either.
    """
    target = str(product_path.resolve())
    found = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            path = node.get("path")
            sha = node.get("sha256")
            if isinstance(path, str) and isinstance(sha, str):
                if str(Path(path).resolve()) == target:
                    found.append(sha)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(record)
    contract.require(
        found, f"pilot: the receipt records no stamp whose path is {target}"
    )
    contract.require(
        len(set(found)) == 1,
        f"pilot: the receipt records {len(set(found))} different digests for {target}",
    )
    return found[0]


def _producer_revision(null_slab) -> str:
    """The revision recorded INSIDE the null slab's declaration, i.e. the producer's own.

    Read from the slab rather than taken from a caller, because the whole point of the field is
    that it describes an execution this process did not perform.
    """
    with np.load(null_slab, allow_pickle=False) as store:
        decl = json.loads(str(store["declaration_json"]))
    revision = decl["writer"]["code_identity"]["revision"]
    contract.require(
        isinstance(revision, str) and revision.strip(),
        f"pilot: the null slab at {null_slab} names no producing revision",
    )
    return revision


def run_pilot(
    manifest,
    *,
    out_dir,
    interpreter: str | None = None,
    allow_overwrite: bool = False,
    receipt_path=None,
) -> dict:
    """Run the existing build CLI, validate its completion, and persist both spectra.

    The build is invoked as a SUBPROCESS on purpose. Calling `z_build.main` in-process would
    exercise the function while leaving the exit-code contract -- the thing this pilot exists to
    handle correctly -- untested, and `main` is the only place the usage-error/completion code
    split lives.
    """
    manifest = Path(manifest).resolve()
    out_dir = Path(out_dir).resolve()
    contract.require(manifest.is_file(), f"pilot: manifest not found: {manifest}")
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "out_cv": out_dir / "z-cv.npz",
        "out_mean": out_dir / "z-mean.npz",
        "receipt_cv": out_dir / "z-receipt-cv.json",
        "receipt_mean": out_dir / "z-receipt-mean.json",
        "out_null": out_dir / "z-null.npz",
    }
    for path in artifacts.values():
        build_path.preservation_guard(str(path), allow_overwrite=allow_overwrite)
    receipt_path = Path(receipt_path).resolve() if receipt_path else out_dir / "z-pilot-receipt.json"
    build_path.preservation_guard(str(receipt_path), allow_overwrite=allow_overwrite)

    cmd = [interpreter or sys.executable, str(Path(build.__file__).resolve()),
           "--manifest", str(manifest)]
    for key, path in artifacts.items():
        cmd += [f"--{key.replace('_', '-')}", str(path)]
    started = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(build.__file__).parent))
    build_seconds = time.monotonic() - started

    completion = _validate_completion(proc.returncode, proc.stdout,
                                      {k: str(v) for k, v in artifacts.items()})

    # ⚠ THE PRODUCER'S REVISION MUST DIFFER FROM THE ASSEMBLING ONE, AND NOTHING ASSERTED IT.
    # Three docstrings and Z_BUILD.md said the two must stay distinct; no code compared them, so
    # the property held only because this pilot's modules do not exist at the precursor's
    # revision -- an accident of file existence, which the parity check would catch for a
    # different reason. An accident is not an assertion.
    # READ FROM THE DECLARED INPUT SLAB, NOT FROM `out_null`. `build_z` re-stamps its own copy
    # with the ASSEMBLING identity (z_build.py: persist_null_operands(..., code_identity=code)),
    # so `out_null` carries the assembling revision by design -- reading the producer's revision
    # from it would compare the assembling revision with itself and this check would fail on every
    # correct run. The producer's identity survives in the INPUT slab the bridge wrote.
    declared = json.loads(manifest.read_text())
    # RESOLVED AGAINST THE MANIFEST DIRECTORY, exactly as `z_build.Source` resolves it. The
    # manifest contract allows relative source paths ("relative inputs resolve against the
    # manifest directory"), and `build_manifest` happens to write absolute ones -- so reading the
    # field literally worked for manifests this module wrote and failed for every hand-written or
    # fixture manifest, which is the larger population.
    producer_revision = _producer_revision(
        manifest.parent / declared["sources"]["null"]["path"]
    )
    assembling_revision = declared["producing_revision"]
    contract.require(
        producer_revision != assembling_revision,
        f"pilot: the null slab's producing revision and this assembly's revision are both "
        f"{producer_revision}. The precursor's producer revision is the evidence for where the "
        f"operands came from; if the assembling code is the same revision, that evidence says "
        f"nothing and the two roles have been collapsed.",
    )

    # The spectrum, from the CLOSED artifacts, bound by their digests.
    spectra = {}
    for variant in ("cv", "mean"):
        product = artifacts[f"out_{variant}"]
        decl = {"path": product.name, "format": product.suffix.lstrip("."),
                "sha256": receipt.sha256_file(product)}
        with build.Source(decl, product.parent) as source:
            covariance = source.read(build.TOTAL_KEY)
        spectra[variant] = spectrum_diagnostics(covariance, label=variant)
        spectra[variant]["product"] = decl

    pilot_receipt = {
        "pilot_schema_version": PILOT_SCHEMA_VERSION,
        "subject": "Z assembly/spectrum pilot",
        "written_at_utc": receipt.utc_now(),
        "manifest": receipt.stamp_file(manifest),
        "build_command": cmd,
        "build_returncode": proc.returncode,
        "build_seconds": float(build_seconds),
        "exit_code_meaning": (
            f"{BUILD_COMPLETION_RC} = construction ran to completion with NON-PASSING science. "
            f"Not success, and not converted to 0."
        ),
        **completion,
        "spectra": spectra,
        "producer_revision": producer_revision,
        "assembling_revision": assembling_revision,
        "revisions_distinct": True,
        "artifacts": {k: receipt.stamp_file(v) for k, v in artifacts.items()},
        "scientific_acceptance": "NON-PASSING",
        "adoptable": False,
        "invalid_ratio_policy": (
            "Unchanged. The producer's non-finite/<=0 ratio substitution and clipping policy is "
            "recorded by the producer's own logs and is not re-decided here."
        ),
        "remaining_requirements": build.REQUIREMENTS,
    }
    # RECEIPT LAST: every product, the null slab and both spectra exist and have been read back
    # before this file appears.
    receipt.atomic_write_json(receipt_path, pilot_receipt)
    readback = json.loads(Path(receipt_path).read_text())
    contract.require(
        readback == pilot_receipt, "pilot: receipt readback differs from what was built"
    )
    return {"receipt": str(receipt_path), **pilot_receipt}


def main(argv: list[str] | None = None) -> int:
    """Run the pilot. Exit 2 = completed construction, NON-PASSING science. Exit 1 = failure.

    2 IS PRESERVED, not converted. The build's completion code is the honest status of this
    construction, and a pilot that returned 0 would tell a launcher the science passed.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--receipt", type=Path, default=None)
    parser.add_argument("--interpreter", default=None)
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_pilot(
            args.manifest, out_dir=args.out_dir, receipt_path=args.receipt,
            interpreter=args.interpreter, allow_overwrite=args.allow_overwrite,
        )
    except contract.ZContractError as exc:
        print(json.dumps({"pilot_status": "FAILED", "reason": str(exc)}), file=sys.stderr)
        return BUILD_FAILURE_RC
    print(json.dumps({"pilot_status": "CHECKED", "receipt": result["receipt"],
                      "scientific_acceptance": "NON-PASSING", "adoptable": False,
                      "spectra": {k: {"lambda_min": v["lambda_min"],
                                      "lambda_max": v["lambda_max"],
                                      "n_negative": v["n_negative"],
                                      "eigensolve_seconds": v["eigensolve_seconds"]}
                                  for k, v in result["spectra"].items()}}, indent=2))
    return BUILD_COMPLETION_RC


if __name__ == "__main__":
    raise SystemExit(main())
