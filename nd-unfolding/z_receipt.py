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
import json
import os
import tempfile
from datetime import datetime, timezone

import numpy as np

from z_contract import ZContractError, require, withheld_boundaries
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
    # A receipt that carries a MET verdict while a boundary it depended on is withheld would be the
    # exact failure Joseph's instruction names. Refuse to write one.
    if outcome and outcome.get("assessable") is False and outcome.get("branch") == 3:
        raise ZContractError(
            "receipt: outcome claims branch 3 (MET) while reporting itself not assessable. "
            "A withheld boundary cannot produce a passing grade.")
    return receipt


def write_receipt(path, receipt) -> dict:
    atomic_write_json(path, receipt)
    return stamp_file(path)
