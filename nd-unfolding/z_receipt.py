#!/usr/bin/env python3
"""Z's receipt schema (SPEC §1.5) and the null operands it must persist (§3.7a, §3.3 11b/11c).

WRITTEN LAST, identifying the exact Z it describes.

THE PERSISTENCE REQUIREMENT, and why it is a WRITER change rather than a receipt field
--------------------------------------------------------------------------------------
`unified_throw_cov.py:540-579` writes `C_unified`, `C_blocksum`, `C_cross`, `hJointMeanShift`, the
two seeds, the offset provenance and `fixed_seed_null_norm` -- and it does NOT write `x_cv`. The
vector is computed at `:369-371`, carried in the return dict as `x_cv_reported` at `:586`, and
dropped. So the denominator of the ratio the null criterion grades is not recoverable from the
product the criterion grades, and a validator could only read the producer's own number back and
compare it with itself -- the shape §1.3b rejected for `g`.

Rev. 16 proposed sourcing the denominator from the production ROOT's `hXSecND_flat` instead. Rev. 17
withdrew that: the numerator compares two INTERNALLY re-unfolded CVs, so an externally produced
denominator PRESUMES the determinism the null is testing, and `adopt_unified_5d.py:116-121` checks
CARDINALITY only -- not the mask, not the values. A file hash binds bytes, not equality between two
productions' vectors.

So Z persists `x_cv`, `x_cv2` and the support predicate's result in its own product:

    2 x 65,856 float64 + one bool mask  ~=  1.05 MB
    against a throw product measured at   2,668,021,041 B = 2.668 GB
    a fraction of                          3.9e-4

(Rev. 16 divided by 41 GB, which is the 45-component band family and G's `combined_source` -- a
different object. The conclusion survived; the operand was still wrong.)

`_atomic_savez` is imported from the producer rather than reimplemented: a retyped write idiom is a
second implementation, and this one already handles the partial-write case.
"""

from __future__ import annotations

import hashlib
import math
import json
import os
import tempfile
from datetime import datetime, timezone

import numpy as np

from z_contract import Z_BOUNDARIES, ZContractError, require, withheld_boundaries
from unified_throw_cov import _atomic_savez   # the producer's own idiom; do not reimplement

Z_RECEIPT_SCHEMA_VERSION = 1

# §1.5's negative statement, verbatim. Carried in every receipt because its absence is what let a
# neighbouring receipt be read as evidence about a different object.
NEGATIVE_STATEMENT = (
    "F's 266-bin receipt, S's whole-file PASS, and any receipt about G are not evidence that Z was "
    "produced. Where S supplies a component, that component's digest is rebound into this receipt "
    "at Z's build time.")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_array(a) -> str:
    """Digest an array by its bytes AND its shape/dtype.

    Shape and dtype are folded in because two different arrays can share a byte buffer -- a
    reshaped view digests identically otherwise, and the mask and the vector must not collide.
    """
    a = np.ascontiguousarray(a)
    h = hashlib.sha256()
    h.update(f"{a.dtype.str}|{a.shape}|".encode())
    h.update(a.tobytes())
    return h.hexdigest()


def stamp_file(path) -> dict:
    """Identity stamped AT OPEN TIME -- §1.5, from §7 item 2's finding.

    The launcher that produced G hashed AFTER building, so its digest binds the bytes at job end
    rather than at open. `inode` and `device` are included because a path plus a digest does not
    distinguish a file that was replaced between two reads.
    """
    st = os.stat(path)
    return {"path": os.path.abspath(os.fspath(path)), "sha256": sha256_file(path),
            "size": st.st_size, "mtime_ns": st.st_mtime_ns,
            "inode": st.st_ino, "device": st.st_dev, "stamped_at_utc": utc_now()}


def atomic_write_json(path, payload) -> None:
    path = os.path.abspath(os.fspath(path))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fh = tempfile.NamedTemporaryFile("w", prefix=os.path.basename(path) + ".",
                                     suffix=".tmp.json", dir=os.path.dirname(path) or ".",
                                     delete=False, encoding="utf-8")
    tmp = fh.name
    try:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
        fh.close()
        os.replace(tmp, path)
    except Exception:
        fh.close()
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ------------------------------------------------------------------- null operand persistence --
def persist_null_operands(path, x_cv, x_cv2, mask) -> dict:
    """Write the null's own operands beside Z's product, and return their stamp.

    Both vectors are persisted on the FULL GRID and the predicate's RESULT is persisted with them,
    so a validator recomputes `n_rep` from the mask rather than trusting a recorded integer.
    """
    x_cv = np.asarray(x_cv, float)
    x_cv2 = np.asarray(x_cv2, float)
    mask = np.asarray(mask, bool)
    require(x_cv.shape == x_cv2.shape == mask.shape,
            f"persist: shapes differ -- x_cv {x_cv.shape}, x_cv2 {x_cv2.shape}, "
            f"mask {mask.shape}")
    require(x_cv.ndim == 1, f"persist: expected flat grid vectors, got {x_cv.ndim}-D")
    _atomic_savez(path, x_cv=x_cv, x_cv2=x_cv2, support_mask=mask)
    return {"stamp": stamp_file(path),
            "n_grid": int(x_cv.size), "n_rep": int(mask.sum()),
            "sha256_x_cv": sha256_array(x_cv), "sha256_x_cv2": sha256_array(x_cv2),
            "sha256_support_mask": sha256_array(mask),
            "bytes_persisted": int(x_cv.nbytes + x_cv2.nbytes + mask.nbytes)}


def load_null_operands(path):
    """Read them back. Fails closed on a missing key rather than substituting a default."""
    with np.load(path) as z:
        for key in ("x_cv", "x_cv2", "support_mask"):
            if key not in z:
                raise ZContractError(
                    f"null operands at {path}: key {key!r} is absent. §3.3 condition 11b requires "
                    f"the ratio to be reconstructible from the persisted operands; a missing "
                    f"operand is a reject, not a fallback to the producer's recorded scalar.")
        return (np.asarray(z["x_cv"], float), np.asarray(z["x_cv2"], float),
                np.asarray(z["support_mask"], bool))


# ------------------------------------------------------------------------------ the receipt ----
def build_receipt(*, z_stamp, variant, parent, code_identity, inflation, null_block,
                  cause_blocks, closure, outcome=None, reproducibility=None, notes=None) -> dict:
    """Assemble §1.5's field set. Refuses to omit the blocks whose absence has cost this campaign.

    It does NOT decide anything. `outcome` is whatever `z_validator.assess` returned, recorded
    as-is; if a boundary was withheld the receipt says so in the same place it would otherwise say
    MET, which is the point.
    """
    require(variant in ("cv", "mean"),
            f"receipt: variant must be 'cv' or 'mean', got {variant!r} -- §3.3 condition 14 "
            f"refuses a build that produced only one, and an unnamed variant is worse")
    for name, block in (("z_stamp", z_stamp), ("parent", parent),
                        ("code_identity", code_identity), ("inflation", inflation),
                        ("null_block", null_block), ("closure", closure)):
        require(isinstance(block, dict) and block,
                f"receipt: block {name!r} is empty or missing; §1.5 requires it")
    require("import_closure_digests" in code_identity and "revision" in code_identity,
            "receipt: code identity needs a pinned revision AND import-closure digests bound to "
            "the run -- a clean implementation at an unpinned revision is not C")

    receipt = {
        "schema_version": Z_RECEIPT_SCHEMA_VERSION,
        "written_at_utc": utc_now(),
        "subject": "Z -- one complete scalar-5D covariance successor",
        "centering_variant": variant,
        "z": z_stamp,
        "parent": parent,
        "code_identity": code_identity,
        "inflation": inflation,
        "null": null_block,
        "causes": cause_blocks,
        "closure": closure,
        "outcome": outcome,
        "reproducibility": reproducibility,
        "withheld_boundaries": {k: b.describe() for k, b in withheld_boundaries().items()},
        "negative_statement": NEGATIVE_STATEMENT,
        "notes": notes or {},
    }
    _validate_passing_outcome(outcome, inflation)
    return receipt


def _validate_passing_outcome(outcome, inflation=None) -> None:
    """A MET receipt must be justified by the declarations it actually rests on.

    ⚠ REVIEW FINDING 1, SECOND HALF. The first version refused only the self-contradictory case --
    `assessable=False` together with `branch=3`. So an outcome claiming `assessable=True,
    branch=3` was written happily while the receipt's own `withheld_boundaries` block recorded all
    four boundaries as withheld. The receipt contained its own refutation and did not look at it.

    A passing grade is now checked against the per-leg boundary records the outcome carries AND
    against the live registry, because those are two different ways to be wrong: a stale outcome
    dict, and a leg whose boundary was withdrawn after the outcome was computed.
    """
    if not outcome:
        return
    branch = outcome.get("branch")
    if outcome.get("assessable") is False and branch == 3:
        raise ZContractError(
            "receipt: outcome claims branch 3 (MET) while reporting itself not assessable. "
            "A withheld boundary cannot produce a passing grade.")
    if branch != 3:
        return

    _validate_reconstruction_ran(inflation)

    legs = outcome.get("leg_results") or {}
    if not legs:
        raise ZContractError(
            "receipt: outcome claims branch 3 (MET) but records no leg results. A pass with no "
            "legs is not a pass -- §3.7b item 5 grades over a declared leg set L.")
    offenders = [f"{name} ({why})" for name, entry in legs.items()
                 for why in [_leg_is_unbacked(entry)] if why]
    if offenders:
        raise ZContractError(
            "receipt: outcome claims branch 3 (MET) but these legs are not backed by a declared "
            f"boundary: {sorted(offenders)}. Joseph, 2026-09-07: missing or unapproved acceptance "
            "boundaries must produce an explicit non-passing result.")


RECONSTRUCTION_KEY = "G3R_raw_operand_reconstruction"


def _validate_reconstruction_ran(inflation) -> None:
    """A MET receipt must PROVE §1.3b's reconstruction ran, on BOTH variants.

    Integrated 2026-09-07 under Joseph's authorization. §1.3b's whole point is that the other four
    inflation gates are *jointly satisfiable by an uninflated object*, so a receipt that records
    them and not this one records a green state reachable without the work being done. The
    validator's `identities_pass` flag cannot substitute: it is a producer-supplied boolean, which
    is the "read the producer's own value back" shape §1.3b explicitly rejects.

    So this looks for the gate's own measured output, not for an assertion that it passed:

      * the block must be present under `RECONSTRUCTION_KEY`,
      * it must carry `per_variant` results for BOTH `mean` and `cv` -- one variant cannot expose
        the reuse fault,
      * each variant's `max_rel_diff` must be within the `rtol` the gate recorded.

    ⚠ A NON-DISCRIMINATING PASS IS RECORDED, NOT REJECTED. Where `ms**2` is under the tolerance the
    gate cannot see a dropped shift and says so; refusing on that would make the receipt refuse
    correct builds whose mean shift is genuinely tiny. The receipt therefore carries
    `discriminating` through to the reader instead of silently upgrading it to assurance --
    the same choice, for the same reason, as the gate itself.
    """
    block = (inflation or {}).get(RECONSTRUCTION_KEY)
    if not isinstance(block, dict):
        raise ZContractError(
            f"receipt: outcome claims branch 3 (MET) but the inflation block records no "
            f"{RECONSTRUCTION_KEY!r}. §1.3b's reconstruction is what makes the other four "
            f"inflation gates capable of failing -- an uninflated object satisfies all four -- so "
            f"a pass that cannot show it ran is not a pass.")
    per_variant = block.get("per_variant")
    if not isinstance(per_variant, dict):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} carries no per_variant measurements. A recorded "
            f"verdict is not a recorded measurement.")
    absent = [v for v in ("mean", "cv") if v not in per_variant]
    if absent:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} is missing variant(s) {absent}. §1.3b requires BOTH "
            f"variants be reconstructed independently, because g^mean and g^cv differ only "
            f"through the mean-shift term.")
    # ⚠ ROUND-6 BLOCKER 2. Every comparison below was made against values that were never
    # checked for being NUMBERS IN RANGE, so three MET receipts were reproduced:
    #   * `rtol=inf` with `max_rel_diff=100`   -- 100 <= inf is True
    #   * `max_rel_diff=-inf`                  -- -inf <= rtol is True
    #   * no `discriminating` field at all     -- the disclosure simply omitted
    # A tolerance of infinity is not a loose tolerance, it is the ABSENCE of one, and a negative
    # relative residual is not a small residual, it is not a residual. Both passed a comparison
    # that was well formed and vacuous -- the same shape as the PSD gate's absolute floor.
    rtol = block.get("rtol")
    if isinstance(rtol, bool) or not isinstance(rtol, (int, float)):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} records rtol {rtol!r}; a comparison with no stated "
            f"tolerance cannot be re-checked by a reader.")
    if not math.isfinite(rtol) or not rtol > 0:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} records rtol {rtol!r}, which is not a finite positive "
            f"tolerance. `inf` is not a loose tolerance -- it is the absence of one, and every "
            f"residual satisfies it.")
    for variant in ("mean", "cv"):
        diff = (per_variant[variant] or {}).get("max_rel_diff")
        if isinstance(diff, bool) or not isinstance(diff, (int, float)):
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} variant {variant!r} records max_rel_diff "
                f"{diff!r}, which is not a measurement.")
        if not math.isfinite(diff) or diff < 0:
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} variant {variant!r} records max_rel_diff "
                f"{diff!r}. A relative residual is finite and non-negative by construction, so "
                f"this value did not come from the gate -- and `-inf <= rtol` would have passed.")
        if not diff <= rtol:
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} variant {variant!r} recorded max_rel_diff "
                f"{diff:.6e} > rtol {rtol:.0e}, so the reconstruction did NOT pass, yet the "
                f"outcome claims MET.")

    # THE DISCLOSURE IS PART OF THE EVIDENCE, NOT A COURTESY. A pass whose discriminating power
    # is unstated reads as assurance it may not carry, which is the whole subject of this gate's
    # three corrected docstrings. Absent metadata is refused rather than defaulted either way.
    if "discriminating" not in block:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} omits `discriminating`. Whether the reconstruction "
            f"could have detected a dropped shift on these operands is part of what a pass "
            f"means; a receipt that does not say reads as assurance it may not carry.")
    discriminating = block["discriminating"]
    if not isinstance(discriminating, bool):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} records discriminating {discriminating!r}, which is "
            f"not a verdict.")
    if not discriminating:
        note = block.get("note")
        if not isinstance(note, str) or not note.strip():
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} reports discriminating=False and carries no "
                f"limitation note. A non-discriminating pass is admissible -- a genuinely tiny "
                f"mean shift is not a defect -- but it must arrive WITH the statement of what "
                f"was not tested, or the reader cannot tell it from a discriminating one.")
        if not isinstance(block.get("discrimination_blockers"), dict):
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} reports discriminating=False without "
                f"`discrimination_blockers`. WHY the gate was blind -- pinned, saturated, or "
                f"below tolerance -- is the actionable part, and saturation is invisible to a "
                f"tolerance argument.")
    if isinstance(block.get("discrimination_blockers"), dict):
        _validate_discrimination_blockers(block["discrimination_blockers"], discriminating)


BLOCKER_COUNTS = ("n_bins", "n_separated", "n_pinned", "n_saturated_v_uni_below_v_blk",
                  "n_shift_below_tolerance")


def _validate_discrimination_blockers(blockers, discriminating) -> None:
    """The disclosure must contain MEASUREMENTS, and they must be consistent with the verdict.

    ⚠ ROUND-7 ISSUE 2. Requiring the key was not requiring the content: `discrimination_blockers
    = {}` satisfied "is a dict" and a MET receipt was written carrying a note that explained
    nothing and a breakdown that measured nothing. So did a breakdown whose counts did not add
    up, and one that said `discriminating=False` beside `n_separated=5` -- a record contradicting
    the verdict it accompanies.

    Four checks, because they fail independently:

      * PRESENT -- every count and `max_separation`, so an empty or partial dict is refused.
      * IN DOMAIN -- counts are non-negative integers, `max_separation` finite and non-negative.
        `bool` is excluded: `isinstance(True, int)` is True in Python.
      * PARTITIONING -- separated + pinned + saturated + below-tolerance == n_bins. Named
        mechanisms that do not add up leave a fifth cause unaccounted for, and the whole reason
        this breakdown exists is that saturation was the cause nobody had named.
      * CONSISTENT -- `discriminating` is exactly `n_separated > 0`. The verdict is a function of
        the measurements, so a receipt where they disagree is not a receipt with a bad number in
        it; it is one whose two halves came from different runs.
    """
    missing = [k for k in BLOCKER_COUNTS + ("max_separation",) if k not in blockers]
    if missing:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers omits {missing}. A breakdown "
            f"that names no mechanism explains nothing -- an empty dict satisfied the previous "
            f"check, which required the key and not its content.")

    for key in BLOCKER_COUNTS:
        v = blockers[key]
        if isinstance(v, bool) or not isinstance(v, int):
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers[{key!r}] is {v!r}, which "
                f"is not a bin count.")
        if v < 0:
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers[{key!r}] is {v}; a count "
                f"of bins cannot be negative.")

    sep_max = blockers["max_separation"]
    if isinstance(sep_max, bool) or not isinstance(sep_max, (int, float)):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers['max_separation'] is "
            f"{sep_max!r}, which is not a measurement.")
    if not math.isfinite(sep_max) or sep_max < 0:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers['max_separation'] is "
            f"{sep_max!r}; a relative separation is finite and non-negative by construction.")

    if blockers["n_bins"] <= 0:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers reports n_bins "
            f"{blockers['n_bins']}. A reconstruction over no bins is not evidence of anything.")

    parts = ("n_separated", "n_pinned", "n_saturated_v_uni_below_v_blk",
             "n_shift_below_tolerance")
    total = sum(blockers[k] for k in parts)
    if total != blockers["n_bins"]:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} discrimination_blockers do not partition the bins -- "
            f"{' + '.join(f'{k}={blockers[k]}' for k in parts)} = {total}, but n_bins is "
            f"{blockers['n_bins']}. Mechanisms that do not add up leave a cause unnamed, which is "
            f"exactly how saturation went unnoticed.")

    expected = blockers["n_separated"] > 0
    if bool(discriminating) is not expected:
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} records discriminating={discriminating!r} beside "
            f"n_separated={blockers['n_separated']}. The verdict is a FUNCTION of the "
            f"measurements -- discriminating is exactly n_separated > 0 -- so these two halves "
            f"did not come from the same run.")


def _leg_is_unbacked(entry):
    """Why this leg cannot support a MET grade, or `None` if it can.

    ⚠ ROUND-3 FINDING 1. The first repair checked the recorded boundary block and, if the live
    registry happened to hold that name, that the live one was still declared. Both halves leaked:

      * `Z_BOUNDARIES.get(name)` returns `None` for an UNKNOWN name, and `live is not None` guarded
        the only check that used it. Measured: a leg citing `cause3_aggg` -- one keystroke off, no
        provenance -- graded MET inside a receipt whose own `withheld_boundaries` block listed all
        four real boundaries as withheld.
      * nothing compared the recorded declaration with the live one. Measured: a stale outcome
        applying `limit=1.0` under approval record `APPROVAL-OLD` passed while the live boundary
        was `0.1` under `APPROVAL-NEW` -- a receipt graded against a superseded criterion, and the
        receipt itself is where that would have to be caught.

    So the chain is checked end to end: the cited name must be a boundary Z actually HAS, that
    boundary must be declared NOW, the recorded copy must agree with it in both value and
    provenance, and the limit that was APPLIED must be that value. A pass is only as good as the
    weakest link in that chain, and each link is a different way to be wrong.
    """
    entry = entry or {}
    b = entry.get("boundary") or {}
    name = b.get("name")

    if not name:
        return "cites no boundary name"
    live = Z_BOUNDARIES.get(name)
    if live is None:
        return (f"cites boundary {name!r}, which is not in Z's registry -- known names are "
                f"{sorted(Z_BOUNDARIES)}")
    if not live.is_declared:
        return f"boundary {name!r} is withheld in the registry now"
    if b.get("status") != "DECLARED" or b.get("value") is None:
        return f"boundary {name!r} recorded as {b.get('status')!r} with value {b.get('value')!r}"

    live_value = live.value
    if b.get("value") != live_value:
        return (f"recorded boundary value {b.get('value')!r} != the live declaration "
                f"{live_value!r} for {name!r} -- the outcome is stale")
    if b.get("provenance") != live.provenance:
        return (f"recorded provenance {b.get('provenance')!r} != the live approval record "
                f"{live.provenance!r} for {name!r} -- graded against a superseded criterion")
    if "limit" not in entry:
        return "no limit was applied"
    if entry.get("limit") != live_value:
        return (f"applied limit {entry.get('limit')!r} != the declared boundary {live_value!r} "
                f"for {name!r}")
    return None


def write_receipt(path, receipt) -> dict:
    atomic_write_json(path, receipt)
    return stamp_file(path)
