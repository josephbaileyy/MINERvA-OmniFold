#!/usr/bin/env python3
"""Bridge the throw producer's persisted ROOT null operands into the build reader's NPZ schema.

WHAT WAS MISSING, AND WHY IT IS THIS AND NOT MORE. `z_build.build_z` requires
`sources["null"].format == "npz"` and reads it with `z_receipt.load_null_operands`, while
`unified_throw_cov.py`'s combine persists the same three objects as ROOT histograms
(`hCvExecution0`, `hCvExecution1`, `hCvSupportMask`). Z_BUILD.md's remaining requirement 3 --
"Capture both same-run internal fixed-seed CV vectors and the predicate in the throw producer" --
is now DISCHARGED BY THE PRODUCER, so the only thing standing between a real precursor product
and the existing build is a format transcription. Nothing else here is new: the digest-bound
read is `z_build.Source`, the write is `z_receipt.persist_null_operands`, the predicate
recomputation is `z_statistics.support_mask`, and the overwrite refusal is
`z_build_path.preservation_guard`.

THIS TRANSCRIBES; IT DOES NOT REPAIR. Every cross-check below refuses on disagreement rather
than coercing, because a bridge that fixes its input is a bridge that hides a producer defect.
The producer's own recorded scalars are checked AGAINST the arrays rather than trusted in place
of them -- the same reason `z_statistics.reconstruct_null_ratio` recomputes the predicate instead
of applying it.

THE MASK IS THE DANGEROUS ONE. `Source.read` returns float64 for every histogram, and
`persist_null_operands` casts the mask with `np.asarray(mask, bool)`, under which ANY non-zero
value becomes `True`. A `TH1I` holding 2 -- or 0.5 -- would therefore be laundered into a valid
looking predicate. The values are required to be exactly 0 or 1 BEFORE the cast, so a producer
that writes counts instead of a predicate is refused rather than reinterpreted.

PROVENANCE IS THE PRODUCER'S, NOT THIS BRIDGE'S. The slab's `code_identity` names the execution
that COMPUTED the operands, read out of the product itself (`cv_code_revision`,
`cv_producer_file`, `cv_producer_sha256`). `z_build` separately re-stamps its own copy with the
ASSEMBLY's revision, and the two must stay distinct: the precursor's producer revision is
evidence about where the numbers came from, and overwriting it with the assembling revision
would destroy exactly that.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import numpy as np

import z_build as build
import z_build_path as build_path
import z_contract as contract
import z_receipt as receipt
import z_statistics as statistics

BRIDGE_SCHEMA_VERSION = 1

#: The producer's object names, pinned. `unified_throw_cov.py`'s combine writes exactly these.
KEY_CV1 = "hCvExecution0"
KEY_CV2 = "hCvExecution1"
KEY_MASK = "hCvSupportMask"

#: Scalars the producer records beside the arrays. Checked against the arrays, never substituted
#: for them.
COUNT_KEYS = ("n_cv_bins_total", "n_cv_support", "n_cv_genuine_zero", "n_cv_negative")
PROVENANCE_KEYS = ("cv_code_revision", "cv_producer_file", "cv_producer_sha256")
PREDICATE_KEY = "cv_support_predicate"

#: The predicate this bridge is willing to transcribe. `z_statistics.support_mask` implements
#: `x_cv > 0`; a product declaring anything else is refused rather than assumed equivalent.
EXPECTED_PREDICATE = "x_cv > 0"


def _named(store: Any, key: str) -> str:
    """Read a `TNamed` title, refusing a missing or wrongly-typed object.

    ⚠ REVIEWER FINDING. This used `InheritsFrom("TNamed")`, and `TH1`, `TTree` and `TGraph` ALL
    satisfy that -- so a histogram that happened to be named `cv_code_revision` would hand back
    its TITLE as the producer's revision. The class is now required EXACTLY, matching the
    exactness `_count` already had for `TParameter<int>`. The two checks were asymmetric and the
    looser one guarded the provenance field, which is the one that matters most.
    """
    contract.require(store.GetListOfKeys().Contains(key), f"null bridge: missing {key!r}")
    obj = store.Get(key)
    contract.require(obj is not None, f"null bridge: {key!r} did not load")
    contract.require(
        obj.ClassName() == "TNamed",
        f"null bridge: {key!r} is {obj.ClassName()}, expected exactly TNamed. TH1, TTree and "
        f"TGraph all inherit from TNamed, so an inheritance test would accept a histogram's title "
        f"as this field's value.",
    )
    value = str(obj.GetTitle())
    contract.require(value.strip() != "", f"null bridge: {key!r} is blank")
    return value


def _count(store: Any, key: str) -> int:
    """Read a `TParameter<int>`, refusing a missing or wrongly-typed object.

    `Source.read` cannot serve here: it requires `hist.InheritsFrom("TH1")`, and these are
    parameters, not histograms. Reading them through their own accessor keeps the histogram
    reader's contract intact instead of widening it for a different object class.
    """
    contract.require(store.GetListOfKeys().Contains(key), f"null bridge: missing {key!r}")
    obj = store.Get(key)
    contract.require(obj is not None, f"null bridge: {key!r} did not load")
    contract.require(
        "TParameter<int>" in obj.ClassName(),
        f"null bridge: {key!r} is {obj.ClassName()}, expected TParameter<int>",
    )
    return int(obj.GetVal())


def validate_transcription(x_cv, x_cv2, mask_raw, *, recorded_counts, declared_predicate):
    """Every check the transcription makes, over ARRAYS, with no ROOT in the way.

    Factored out for one reason: reached only through `Source`, each refusal below would be
    exercisable only under PyROOT, and this repository's PyROOT-gated tests SKIP on the default
    interpreter. A guard whose test skips is a guard with no test -- the exact shape of F1 in
    Z_BUILD.md, where a forged-label assertion lived only in a ROOT-gated test. These run
    everywhere; `bridge_null_operands` adds the file binding and the write.

    Returns `(mask, measured_counts, agreement)`. Raises `ZContractError` on any disagreement --
    never a coerced value, because a bridge that repairs its input hides a producer defect.
    """
    x_cv = np.asarray(x_cv, float)
    x_cv2 = np.asarray(x_cv2, float)
    mask_raw = np.asarray(mask_raw, float)
    for name, array in ((KEY_CV1, x_cv), (KEY_CV2, x_cv2), (KEY_MASK, mask_raw)):
        contract.require(
            array.ndim == 1,
            f"null bridge: {name!r} is {array.ndim}-D; the slab declares 1-D full grid",
        )
        contract.require(
            np.all(np.isfinite(array)), f"null bridge: {name!r} holds non-finite values"
        )
    contract.require(
        x_cv.shape == x_cv2.shape == mask_raw.shape,
        f"null bridge: shapes differ -- {KEY_CV1} {x_cv.shape}, {KEY_CV2} {x_cv2.shape}, "
        f"{KEY_MASK} {mask_raw.shape}. The ratio and its predicate must be over one grid.",
    )

    # The mask is a PREDICATE RESULT, not a count. Checked BEFORE any bool cast:
    # `np.asarray(x, bool)` maps every non-zero to True, so a producer writing 2 -- or 0.5 --
    # would otherwise be laundered into a plausible predicate.
    offending = np.unique(mask_raw[(mask_raw != 0.0) & (mask_raw != 1.0)])
    contract.require(
        offending.size == 0,
        f"null bridge: {KEY_MASK!r} holds value(s) {offending[:8].tolist()} outside {{0, 1}}. "
        f"The slab declares this array to be a predicate's RESULT; casting a count or a "
        f"fraction to bool would make any non-zero read as selected.",
    )
    mask = mask_raw.astype(bool)

    # The predicate is RECOMPUTED and the producer's must agree exactly. Same discipline as
    # `z_statistics.reconstruct_null_ratio`: applying the producer's predicate would carry a
    # wrong one through into a slab the build then trusts.
    recomputed = statistics.support_mask(x_cv)
    contract.require(
        recomputed.shape == mask.shape,
        f"null bridge: recomputed predicate shape {recomputed.shape} != persisted {mask.shape}",
    )
    if not np.array_equal(mask, recomputed):
        n_bad = int(np.count_nonzero(mask != recomputed))
        raise contract.ZContractError(
            f"null bridge: the product's persisted support mask disagrees with "
            f"`{EXPECTED_PREDICATE}` recomputed from its own {KEY_CV1!r} in {n_bad} bin(s) "
            f"(persisted selects {int(mask.sum())}, recomputed {int(recomputed.sum())}). "
            f"This is transcribed, not corrected: a producer whose predicate does not match "
            f"its own CV is a producer finding."
        )
    contract.require(int(mask.sum()) > 0, "null bridge: the reported support is empty")

    contract.require(
        declared_predicate == EXPECTED_PREDICATE,
        f"null bridge: the product declares its predicate as {declared_predicate!r} and this "
        f"bridge transcribes only {EXPECTED_PREDICATE!r} (implemented by "
        f"`z_statistics.support_mask`). A different predicate is not assumed equivalent.",
    )

    contract.require(
        set(recorded_counts) == set(COUNT_KEYS),
        f"null bridge: recorded counts must be exactly {sorted(COUNT_KEYS)}, got "
        f"{sorted(recorded_counts)}",
    )
    measured = {
        "n_cv_bins_total": int(x_cv.size),
        "n_cv_support": int(mask.sum()),
        "n_cv_genuine_zero": int(np.count_nonzero(x_cv == 0.0)),
        "n_cv_negative": int(np.count_nonzero(x_cv < 0.0)),
    }
    disagreeing = {
        k: {"recorded": recorded_counts[k], "measured": measured[k]}
        for k in COUNT_KEYS
        if int(recorded_counts[k]) != measured[k]
    }
    contract.require(
        not disagreeing,
        f"null bridge: recorded count(s) disagree with the arrays {disagreeing}. The recorded "
        f"integers are checked here precisely so one cannot stand in for the array it describes.",
    )
    contract.require(
        measured["n_cv_support"] + measured["n_cv_genuine_zero"] + measured["n_cv_negative"]
        == measured["n_cv_bins_total"],
        f"null bridge: support {measured['n_cv_support']} + zero "
        f"{measured['n_cv_genuine_zero']} + negative {measured['n_cv_negative']} != grid "
        f"{measured['n_cv_bins_total']}; the predicate does not partition the grid.",
    )

    # RECORDED, NOT GRADED. `B`, `S` and `epsilon` are unapproved (Z_BUILD.md requirement 3), so
    # a verdict here would be an invented tolerance.
    denom = float(np.linalg.norm(x_cv[mask]))
    agreement = {
        "operands_bitwise_identical": bool(np.array_equal(x_cv, x_cv2)),
        "max_abs_difference": float(np.max(np.abs(x_cv2 - x_cv))),
        "relative_l2_over_support": (
            float(np.linalg.norm(x_cv2[mask] - x_cv[mask]) / denom) if denom > 0 else None
        ),
        "graded": False,
        "why_not_graded": (
            "Z_BUILD.md requirement 3 leaves B, S, B <= S and epsilon in [B, S] unapproved. "
            "No tolerance is invented here; the measurement is recorded for the approver."
        ),
    }
    return mask, measured, agreement


def transcribe_identity(provenance, extra_import_closure=None) -> dict:
    """The PRODUCER's code identity, from what the product itself records.

    The revision and closure name the execution that COMPUTED the operands. `z_build` re-stamps
    its own copy of the slab with the ASSEMBLING revision, and the two must stay distinct: the
    precursor's producer revision is the evidence for where the numbers came from, and
    overwriting it with the assembling revision would destroy exactly that.

    `unified_throw_cov.py -> <its sha256>` is a MEASURED import digest bound to the run, read out
    of the product, so the identity is real provenance rather than the shape of it -- the defect
    `z_receipt._require_code_identity`'s reviewer block records.
    """
    contract.require(
        set(provenance) == set(PROVENANCE_KEYS),
        f"null bridge: provenance must be exactly {sorted(PROVENANCE_KEYS)}, got "
        f"{sorted(provenance)}",
    )
    revision = provenance["cv_code_revision"]
    # ⚠ REVIEWER FINDING: ASYMMETRIC STANDARDS. `z_pilot.build_manifest` requires the ASSEMBLING
    # revision to be a full 40-character sha, while the PRODUCER's went through
    # `z_receipt._require_code_identity`, which asks only for a non-empty string -- so "unknown"
    # was an acceptable identity for the field that IS the original execution provenance. The
    # weaker check guarded the more important field. Same standard now applies to both.
    contract.require(
        bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
        f"null bridge: the product records cv_code_revision {revision!r}, which is not a full "
        f"40-character lowercase hex commit sha. A producer whose revision cannot be resolved is "
        f"not provenance, and this is the field a reader acts on when the bytes turn out wrong.",
    )
    closure = {provenance["cv_producer_file"]: provenance["cv_producer_sha256"]}
    for module_id, digest in (extra_import_closure or {}).items():
        if module_id in closure:
            contract.require(
                closure[module_id] == digest,
                f"null bridge: caller's import-closure digest for {module_id!r} is {digest!r} "
                f"and the product records {closure[module_id]!r}. A conflict is refused rather "
                f"than resolved by precedence.",
            )
        closure[module_id] = digest
    return {"revision": revision, "import_closure_digests": closure}


def bridge_null_operands(
    root_path,
    out_path,
    *,
    expect_sha256: str,
    allow_overwrite: bool = False,
    extra_import_closure: dict | None = None,
) -> dict:
    """Transcribe a producer ROOT product's null operands into the versioned NPZ slab.

    Parameters
    ----------
    root_path : path
        The throw producer's combined product, e.g. `unified_throw_cov_5d.root`.
    out_path : path
        New `.npz` path for the versioned null slab. Refused if it exists.
    expect_sha256 : str
        The product's declared digest. Bound before any object is read.
    allow_overwrite : bool
        Must be given deliberately; the default refuses an existing output.
    extra_import_closure : dict, optional
        Additional measured `module -> digest` entries for the PRODUCER's closure. Merged into
        the identity read from the product; a conflicting value for a module already named by
        the product is refused rather than silently preferred either way.

    Returns
    -------
    dict
        The persisted slab's stamp, the producer identity transcribed, and every cross-check's
        measured operands.

    Raises
    ------
    ZContractError
        The digest, an object, a recorded count, the predicate or the mask's values disagree.
    """
    root_path = Path(root_path).resolve()
    out_path = Path(out_path).resolve()
    contract.require(
        out_path.suffix == ".npz", f"null bridge: output must be .npz, got {out_path.suffix!r}"
    )
    contract.require(root_path != out_path, "null bridge: output aliases the input")
    build_path.preservation_guard(str(out_path), allow_overwrite=allow_overwrite)

    declaration = {"path": root_path.name, "format": "root", "sha256": expect_sha256}
    with build.Source(declaration, root_path.parent) as source:
        # ---- the three arrays, digest-recorded by the reader we already have ------------------
        x_cv = source.read(KEY_CV1)
        x_cv2 = source.read(KEY_CV2)
        mask_raw = source.read(KEY_MASK)
        for name, array in ((KEY_CV1, x_cv), (KEY_CV2, x_cv2), (KEY_MASK, mask_raw)):
            contract.require(
                array.ndim == 1,
                f"null bridge: {name!r} is {array.ndim}-D; the slab declares 1-D full grid",
            )
        contract.require(
            x_cv.shape == x_cv2.shape == mask_raw.shape,
            f"null bridge: shapes differ -- {KEY_CV1} {x_cv.shape}, {KEY_CV2} {x_cv2.shape}, "
            f"{KEY_MASK} {mask_raw.shape}. The ratio and its predicate must be over one grid.",
        )

        declared_predicate = _named(source.store, PREDICATE_KEY)
        counts = {key: _count(source.store, key) for key in COUNT_KEYS}
        mask, measured, agreement = validate_transcription(
            x_cv, x_cv2, mask_raw,
            recorded_counts=counts, declared_predicate=declared_predicate,
        )

        # ---- the PRODUCER's identity, transcribed, never this bridge's -----------------------
        provenance = {key: _named(source.store, key) for key in PROVENANCE_KEYS}
        producer_identity = transcribe_identity(provenance, extra_import_closure)

        persisted = receipt.persist_null_operands(
            out_path, x_cv, x_cv2, mask, code_identity=producer_identity
        )
        source.verify_unchanged()

    # Read the slab back through the reader the build will use, and require the operands survived.
    reloaded = receipt.load_null_operands(out_path)
    contract.require(
        all(np.array_equal(a, b) for a, b in zip(reloaded, (x_cv, x_cv2, mask))),
        "null bridge: the slab read back differs from the operands transcribed into it",
    )
    rebuilt = statistics.reconstruct_null_ratio(*reloaded)
    contract.require(
        all(np.isfinite(v) for v in rebuilt.values()),
        "null bridge: the slab's reconstructed null measurement is non-finite",
    )

    return {
        "bridge_schema_version": BRIDGE_SCHEMA_VERSION,
        "source": {"path": str(root_path), "sha256": expect_sha256, "objects": source.reads},
        "producer_identity": producer_identity,
        "declared_predicate": declared_predicate,
        "recorded_counts": counts,
        "measured_counts": measured,
        "cv_execution_agreement": agreement,
        "persisted": persisted,
        "reconstructed_null": rebuilt,
        "out_path": str(out_path),
    }


def main(argv: list[str] | None = None) -> int:
    """Transcribe one product's null operands. Exit 0 on success, 1 on refusal.

    Deliberately NOT `z_build.py`'s exit-2 convention: this command performs no construction and
    makes no scientific claim, so borrowing the code that means "ran to completion, non-passing
    science" would make a transcription look like a build.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Bridge ROOT null operands to the NPZ slab.")
    parser.add_argument("--product", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--out-null", required=True, type=Path)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--record", type=Path, default=None,
                        help="write this transcription's full record here, atomically. A bare "
                             "shell redirect would truncate an existing file silently and leave "
                             "the richest provenance record of the transcription unbound.")
    args = parser.parse_args(argv)
    try:
        # CHECKED BEFORE THE SLAB IS WRITTEN. Guarding --record only after the transcription
        # succeeded meant an existing record refused AFTER z-null-source.npz already existed,
        # leaving an orphan slab behind a non-zero exit. `bridge_null_operands` guards its own
        # output up front; this one has to as well.
        if args.record is not None:
            build_path.preservation_guard(str(args.record),
                                          allow_overwrite=args.allow_overwrite)
        result = bridge_null_operands(
            args.product, args.out_null, expect_sha256=args.sha256,
            allow_overwrite=args.allow_overwrite,
        )
        if args.record is not None:
            receipt.atomic_write_json(args.record, {"bridge_status": "TRANSCRIBED", **result})
            result["record"] = str(args.record)
            result["record_stamp"] = receipt.stamp_file(args.record)
    except contract.ZContractError as exc:
        print(json.dumps({"bridge_status": "FAILED", "reason": str(exc)}), file=__import__("sys").stderr)
        return 1
    print(json.dumps({"bridge_status": "TRANSCRIBED", **result}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
