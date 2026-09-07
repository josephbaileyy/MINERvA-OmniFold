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

The slab carries its own schema version and a digest of its declared construction, on a counter
independent of this receipt's. The first cut carried neither, and its reader admitted a file on the
presence of three familiar keys -- which admits any later file that happens to reuse those names
for something else. The reasoning, and what the reader deliberately does NOT check, is in the block
above `Z_NULL_OPERAND_SCHEMA_VERSION`.
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
# ⚠ THE FINDING THIS SECTION CLOSES. The first version wrote three arrays with no schema version
# and no writer identity, and the reader accepted the file on KEY PRESENCE alone. That is the
# writer-end form of a defect this campaign has now met at three levels: a check that validates the
# object nearest to hand rather than the one its claim depends on. `x_cv`, `x_cv2` and
# `support_mask` being present establishes that three familiar names are in the file. It does not
# establish that those names mean here what this reader assumes they mean. A later writer that made
# `x_cv` per-throw rows, or `support_mask` a selection INDEX rather than a boolean predicate result,
# would satisfy every check the old reader made and hand back operands with different semantics to
# a caller that would then divide by them.
#
# So the format is NAMED, and the name is checked before any operand is touched:
#
#   schema_version       an integer this reader must recognise. An UNVERSIONED file is refused
#                        outright -- never read as version 1 -- because inferring "current format"
#                        from familiar keys is precisely the inference that produced the finding.
#   construction_digest  sha256 over `NULL_OPERAND_CONSTRUCTION`, the literal declaration of what
#                        each array IS. The reader recomputes it from its OWN copy of that literal,
#                        so a declaration that changed WITHOUT a version bump fails -- which is the
#                        silent reinterpretation the version alone cannot catch, in either
#                        direction: an older file read by a moved reader, and a moved writer's file
#                        read here. A version that DID change is caught one line earlier, by the
#                        version check; the digest is not what refuses that case, and the pair is
#                        what makes the format checkable rather than either field alone.
#   writer               who wrote it, when, at which revision, with which import closure. Required
#                        to be present and well formed, and carried INSIDE the same declaration the
#                        version and the construction digest govern, so no loadable file exists
#                        that does not name its producer's code identity.
#
# THE WRITER IDENTITY IS NOT A PASS CONDITION, and the tests pin both directions. A stranger's file
# loads if its version, construction and internal consistency hold; our own writer identity does
# not rescue a file whose declaration disagrees with its arrays. Provenance answers who to ask when
# the bytes are wrong. It never answers whether they are right.
#
# THE INTERNAL DIGESTS ARE BOUNDED IN THE SAME WAY. They bind the three arrays to the declaration
# that describes them, so a partially rewritten slab is caught. They cannot detect a file rewritten
# wholesale by the same code, because the writer computes them -- the external binding is the
# receipt's `stamp_file` sha256 over the whole file, and that is where a reader must look for it.
#
# WHAT THIS READER DELIBERATELY DOES NOT CHECK. It does not recompute the support predicate and
# demand the persisted mask agree with it. That check belongs to §3.3 condition 11b and lives in
# `z_statistics.reconstruct_null_ratio`. Moving it here would make the reconstruction's
# independence check unreachable on the only path that feeds it, while leaving a later reader to
# believe independence had been established at load time. This reader establishes that the FILE is
# the format it claims to be. It is not evidence that the physics in it is right and must not be
# cited for that.
Z_NULL_OPERAND_SCHEMA_VERSION = 1

# Deliberately NOT `Z_RECEIPT_SCHEMA_VERSION`. The receipt's field set and this slab's layout
# change for unrelated reasons; one shared integer would either invalidate every operand file
# whenever a receipt field was added, or leave the slab's own format change unversioned.
SUPPORTED_NULL_OPERAND_SCHEMA_VERSIONS = (1,)

NULL_OPERAND_ARRAY_KEYS = ("x_cv", "x_cv2", "support_mask")
NULL_OPERAND_HEADER_KEYS = ("schema_version", "construction_digest", "declaration_json")

# The declared construction: what each array IS, in words a later reader can disagree with. The
# digest below covers this literal, so editing it without bumping the version breaks every existing
# file loudly rather than reinterpreting it silently.
NULL_OPERAND_CONSTRUCTION = {
    "subject": "Z null operands (SPEC §3.7a; §3.3 conditions 11b/11c)",
    "grid": "FULL -- both vectors and the mask span the whole grid; nothing here is pre-masked",
    "arrays": {
        "x_cv": {
            "dtype": "float64", "ndim": 1,
            "role": "the first internally re-unfolded CV; the null ratio's DENOMINATOR"},
        "x_cv2": {
            "dtype": "float64", "ndim": 1,
            "role": "the second internally re-unfolded CV, same run, same fixed seed"},
        "support_mask": {
            "dtype": "bool", "ndim": 1,
            "role": "the reported-support predicate's RESULT, `x_cv > 0` "
                    "(unified_throw_cov.py:370, via z_statistics.support_mask). A RESULT over the "
                    "full grid, never a selection index and never a pre-applied filter."},
    },
    "predicate_agreement_checked_by":
        "z_statistics.reconstruct_null_ratio -- NOT by the reader, on purpose",
}


def _canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


NULL_OPERAND_CONSTRUCTION_DIGEST = hashlib.sha256(
    _canonical_json(NULL_OPERAND_CONSTRUCTION).encode()).hexdigest()


def _require_code_identity(code_identity, where) -> dict:
    """One definition of what a code identity is, for the receipt and the operand slab alike.

    Retyping this rule in the second caller would be a second implementation of it, and the two
    would drift -- so `build_receipt` calls it too. Both products must name the SAME identity for a
    reader to be able to ask whether the slab and the receipt describe one run.
    """
    require(isinstance(code_identity, dict) and code_identity,
            f"{where}: code identity is missing or empty. A product that does not name the code "
            f"that made it cannot be re-derived, and provenance is the only thing a reader can "
            f"act on when the bytes turn out to be wrong.")
    revision = code_identity.get("revision")
    require(isinstance(revision, str) and revision.strip(),
            f"{where}: code identity needs a pinned `revision` -- a clean implementation at an "
            f"unpinned revision is not C.")
    closure = code_identity.get("import_closure_digests")
    require(isinstance(closure, dict) and closure,
            f"{where}: code identity needs import-closure digests bound to the run; a pinned "
            f"revision alone does not fix what was actually imported.")

    # ⚠ REVIEWER BLOCK, DEFECT 2. This validated the CONTAINER -- "a non-empty dict" -- and never
    # its CONTENTS. Measured as accepted on WRITE and carried back on READ:
    #     {"z_receipt.py": None}   {"m": 7}   {"m": ""}   {"": "a"*64}   {"m": ["a"]}
    # An identity naming a module and pairing it with `null` is not provenance; it is the SHAPE of
    # provenance, which is worse, because it satisfies every check a reader is likely to make.
    #
    # The writer's own error message already asserted that "an import-closure digest is a string"
    # while nothing enforced it. A contract stated in prose and unenforced in code is the same
    # defect as a description bound to nothing -- defect 1, one product over.
    #
    # THE ENCODING CONTRACT, stated rather than left to be inferred: a module ID is a non-empty
    # string without surrounding whitespace, and a digest is a non-empty string. A digest is
    # deliberately NOT required to be hex and NOT required to carry a `sha256:` / `blob:` prefix.
    # Both would be defensible and neither is this repair's call: at eight hex characters a blob id
    # and a sha256 are indistinguishable by eye, so a prefix convention has real merit -- but hex-
    # only and prefixed are mutually exclusive, it would reject every existing caller, and it
    # belongs to whoever owns the receipt's provenance format. Raised, not decided here.
    for module_id, value in sorted(closure.items(), key=lambda kv: str(kv[0])):
        require(isinstance(module_id, str) and module_id.strip(),
                f"{where}: import-closure digests are keyed by module ID, and {module_id!r} is "
                f"not a non-empty string. A digest attached to an unnameable module cannot be "
                f"re-checked against anything.")
        require(isinstance(value, str) and value.strip(),
                f"{where}: the import-closure digest for {module_id!r} is {value!r}, which is not "
                f"a non-empty string. Naming a module and pairing it with a non-digest is the "
                f"SHAPE of provenance without the content, and it passes every check a reader who "
                f"trusts the key set would make.")
    return {"revision": revision, "import_closure_digests": dict(closure)}


def persist_null_operands(path, x_cv, x_cv2, mask, *, code_identity) -> dict:
    """Write the null's own operands beside Z's product, versioned, and return their stamp.

    Both vectors are persisted on the FULL GRID and the predicate's RESULT is persisted with them,
    so a validator recomputes `n_rep` from the mask rather than trusting a recorded integer.

    `code_identity` is REQUIRED and takes the same shape the receipt carries, because a slab whose
    producer cannot be named is a slab no reader can act on. It is recorded, never graded.
    """
    x_cv = np.asarray(x_cv, float)
    x_cv2 = np.asarray(x_cv2, float)
    mask = np.asarray(mask, bool)
    require(x_cv.shape == x_cv2.shape == mask.shape,
            f"persist: shapes differ -- x_cv {x_cv.shape}, x_cv2 {x_cv2.shape}, "
            f"mask {mask.shape}")
    require(x_cv.ndim == 1, f"persist: expected flat grid vectors, got {x_cv.ndim}-D")
    identity = _require_code_identity(code_identity, "persist")

    arrays = {"x_cv": x_cv, "x_cv2": x_cv2, "support_mask": mask}
    writer = {"module": __name__, "function": "persist_null_operands",
              "written_at_utc": utc_now(), "code_identity": identity}
    declaration = {
        "schema_version": Z_NULL_OPERAND_SCHEMA_VERSION,
        "construction": NULL_OPERAND_CONSTRUCTION,
        "construction_digest": NULL_OPERAND_CONSTRUCTION_DIGEST,
        "writer": writer,
        "n_grid": int(x_cv.size),
        "n_rep": int(mask.sum()),
        "dtypes": {k: NULL_OPERAND_CONSTRUCTION["arrays"][k]["dtype"]
                   for k in NULL_OPERAND_ARRAY_KEYS},
        "digests": {k: sha256_array(a) for k, a in arrays.items()},
    }
    # `code_identity` is the only caller-supplied part of the declaration, so it is the only part
    # that can fail to serialise. Letting a TypeError out of a fail-closed module would be a
    # different error class for the same kind of fault, and a caller catching ZContractError would
    # miss it.
    #
    # ⚠ AFTER THE REVIEWER'S BLOCK 2 THIS IS UNREACHABLE, and that is recorded here rather than left
    # to be discovered. Every component of `declaration` is now a validated primitive: the counts
    # and the version are ints this function computes, the dtypes and digests are strings it
    # computes, and `_require_code_identity` has just established that the revision, every module ID
    # and every digest is a non-empty string. No input reaches the `except` any more -- `object()`
    # used to, and is now refused earlier and better, by name. It stays as a backstop against a
    # FUTURE caller-supplied field being added to the declaration, and NO TEST CLAIMS TO EXERCISE
    # IT: an unreachable guard is tolerable, a test asserting it fired would be a coverage claim
    # with nothing behind it.
    try:
        declaration_json = _canonical_json(declaration)
    except TypeError as exc:
        raise ZContractError(
            f"persist: the declaration does not serialise to JSON ({exc}). `code_identity` is the "
            f"only caller-supplied part of it -- an import-closure digest is a string, and a "
            f"value that is not one cannot be written or read back.") from exc
    _atomic_savez(
        path,
        schema_version=np.asarray(Z_NULL_OPERAND_SCHEMA_VERSION, dtype=np.int64),
        construction_digest=np.asarray(NULL_OPERAND_CONSTRUCTION_DIGEST),
        declaration_json=np.asarray(declaration_json),
        **arrays)
    return {"stamp": stamp_file(path),
            "schema_version": Z_NULL_OPERAND_SCHEMA_VERSION,
            "construction_digest": NULL_OPERAND_CONSTRUCTION_DIGEST,
            "writer": writer,
            "n_grid": int(x_cv.size), "n_rep": int(mask.sum()),
            "sha256_x_cv": sha256_array(x_cv), "sha256_x_cv2": sha256_array(x_cv2),
            "sha256_support_mask": sha256_array(mask),
            "bytes_persisted": int(x_cv.nbytes + x_cv2.nbytes + mask.nbytes)}


def _scalar(store, key, kinds, kind_name, path):
    a = np.asarray(store[key])
    require(a.ndim == 0,
            f"null operands at {path}: {key!r} must be a scalar, got shape {a.shape}.")
    require(a.dtype.kind in kinds,
            f"null operands at {path}: {key!r} has dtype {a.dtype!s}; this format stores it as "
            f"{kind_name}. A header field of the wrong type is a format mismatch, not a value to "
            f"coerce.")
    return a.item()


def _declared(decl, field, typ, path, what):
    value = decl.get(field, None)
    ok = isinstance(value, typ) and not (typ is int and isinstance(value, bool))
    require(ok,
            f"null operands at {path}: declaration field {field!r} is missing or not "
            f"{typ.__name__} (got {value!r}). {what}")
    return value


def _validate_declaration(decl, version, digest, path) -> dict:
    """The declaration must be complete, in domain, and agree with the header that admitted it."""
    require(isinstance(decl, dict),
            f"null operands at {path}: `declaration_json` did not decode to an object.")
    _declared(decl, "schema_version", int, path,
              "The version is stated twice -- in the header and in the declaration -- so that a "
              "header written by one revision beside a body written by another is visible.")
    require(decl["schema_version"] == version,
            f"null operands at {path}: the header says schema_version {version} and the "
            f"declaration says {decl['schema_version']}. These came from different writes.")
    _declared(decl, "construction_digest", str, path, "It names the construction this file uses.")
    require(decl["construction_digest"] == digest,
            f"null operands at {path}: the header's construction digest and the declaration's "
            f"disagree. These came from different writes.")

    # ⚠ REVIEWER BLOCK, DEFECT 1. The header digest certifies THIS READER's construction literal.
    # It said nothing whatever about the file's OWN copy -- which is the part a human, or any tool
    # that is not this reader, actually opens to find out what the arrays are. Measured on
    # writer-produced files: `construction` REMOVED, `construction` replaced by the integer 17, and
    # `arrays.x_cv.role` rewritten to "externally supplied CV from the production ROOT" all LOADED.
    #
    # That is this section's own defect one level in. I checked the object nearest to hand -- a
    # digest STRING -- rather than the object whose correctness the claim depends on, namely the
    # construction that digest is supposed to certify. A file could therefore carry a
    # self-contradicting description that the digest check appeared to have blessed, and the
    # rewritten role is the dangerous one: it names the exact operand §3.7a REJECTED, so a reader
    # trusting the file's own words would believe Z's denominator came from a separately produced
    # ROOT -- which presumes the determinism the null exists to test.
    #
    # Both comparisons are made rather than one. `digest == NULL_OPERAND_CONSTRUCTION_DIGEST` is
    # established by the loader one step earlier, so checking only `actual == digest` would leave
    # this function's guarantee dependent on its caller.
    construction = decl.get("construction")
    require(isinstance(construction, dict) and construction,
            f"null operands at {path}: the declaration carries no `construction` object (got "
            f"{type(construction).__name__}). The digest names a construction; the declaration "
            f"must CONTAIN it, or the file describes itself to a reader in words nothing checks.")
    actual = hashlib.sha256(_canonical_json(construction).encode()).hexdigest()
    require(actual == digest and actual == NULL_OPERAND_CONSTRUCTION_DIGEST,
            f"null operands at {path}: the declaration's own `construction` hashes to {actual}, "
            f"against the header's {digest} and this reader's "
            f"{NULL_OPERAND_CONSTRUCTION_DIGEST}. The file's description of what its arrays ARE is "
            f"not the description its digest certifies, so one of the two is a forgery or an edit "
            f"that did not propagate.")
    n_grid = _declared(decl, "n_grid", int, path,
                       "The declared grid length is checked against the arrays, not believed.")
    require(n_grid > 0,
            f"null operands at {path}: declared n_grid is {n_grid}; a slab with no grid cannot "
            f"reconstruct a ratio.")
    n_rep = _declared(decl, "n_rep", int, path,
                      "The declared support count is recomputed from the mask, not believed.")
    require(0 <= n_rep <= n_grid,
            f"null operands at {path}: declared n_rep {n_rep} is outside [0, {n_grid}].")

    for field in ("dtypes", "digests"):
        table = _declared(decl, field, dict, path, f"One {field[:-1]} per persisted array.")
        require(set(table) == set(NULL_OPERAND_ARRAY_KEYS),
                f"null operands at {path}: declaration {field!r} covers {sorted(table)}, not "
                f"{sorted(NULL_OPERAND_ARRAY_KEYS)}. A declaration that describes a different set "
                f"of arrays than the file holds is not a description of this file.")

    writer = _declared(decl, "writer", dict, path,
                       "A slab whose producer cannot be named is a slab no reader can act on.")
    for field in ("module", "function", "written_at_utc"):
        value = writer.get(field)
        require(isinstance(value, str) and value.strip(),
                f"null operands at {path}: writer.{field} is missing or empty.")
    _require_code_identity(writer.get("code_identity"), f"null operands at {path}: writer")
    return decl


def _validate_operands(arrays, decl, path) -> None:
    """The arrays must be what the declaration says they are: type, shape, count and bytes."""
    n_grid = None
    for key in NULL_OPERAND_ARRAY_KEYS:
        a = arrays[key]
        expected = NULL_OPERAND_CONSTRUCTION["arrays"][key]["dtype"]
        require(a.ndim == 1,
                f"null operands at {path}: {key!r} is {a.ndim}-D; this construction declares it "
                f"1-D over the full grid.")
        require(a.dtype == np.dtype(expected),
                f"null operands at {path}: {key!r} has dtype {a.dtype!s}, and this construction "
                f"declares {expected}. Coercing it would let a narrower producer's values through "
                f"as though they were this format's.")
        require(decl["dtypes"][key] == expected,
                f"null operands at {path}: the declaration says {key!r} is "
                f"{decl['dtypes'][key]!r} where this construction says {expected!r}.")
        if n_grid is None:
            n_grid = int(a.size)
        require(int(a.size) == n_grid,
                f"null operands at {path}: {key!r} has length {a.size} against x_cv's {n_grid}. "
                f"The ratio and its predicate must be over one grid.")
    require(decl["n_grid"] == n_grid,
            f"null operands at {path}: the declaration says n_grid {decl['n_grid']} and the "
            f"arrays are length {n_grid}.")
    n_rep = int(arrays["support_mask"].sum())
    require(decl["n_rep"] == n_rep,
            f"null operands at {path}: the declaration says n_rep {decl['n_rep']} and the "
            f"persisted mask selects {n_rep}. The count is recomputed here precisely so that a "
            f"recorded integer cannot stand in for the predicate's result.")
    for key in NULL_OPERAND_ARRAY_KEYS:
        actual = sha256_array(arrays[key])
        require(decl["digests"][key] == actual,
                f"null operands at {path}: {key!r} does not digest to the value declared with it. "
                f"The array and its description were not written together.")


def load_null_operands(path):
    """Read the operands back, after establishing that the file is the format it claims to be.

    Returns `(x_cv, x_cv2, support_mask)`, the same three arrays as before -- the validation
    happens before the return rather than in the caller, because a caller that has to remember to
    validate is a caller that will one day not.
    """
    with np.load(path, allow_pickle=False) as store:
        present = set(store.files)

        # THE VERSION FIRST, AND ALONE. Nothing else in the file is read until it has said what it
        # is. An unversioned file is refused; it is never read as the current format.
        if "schema_version" not in present:
            raise ZContractError(
                f"null operands at {path}: no `schema_version`. This file predates the versioned "
                f"format or was not written by this writer, and it is REFUSED rather than read as "
                f"version {Z_NULL_OPERAND_SCHEMA_VERSION}. That the keys "
                f"{list(NULL_OPERAND_ARRAY_KEYS)} are present establishes only that three "
                f"familiar names are in the file, not that they mean what this reader would "
                f"assume. Rewrite it with `persist_null_operands`.")
        version = _scalar(store, "schema_version", "iu", "an integer", path)
        if version not in SUPPORTED_NULL_OPERAND_SCHEMA_VERSIONS:
            raise ZContractError(
                f"null operands at {path}: schema_version {version} is not supported by this "
                f"reader, which reads {list(SUPPORTED_NULL_OPERAND_SCHEMA_VERSIONS)}. An "
                f"unrecognised version is a reject: a newer writer may have changed what these "
                f"arrays mean, and this reader has no way to find out from the file.")

        for key in NULL_OPERAND_HEADER_KEYS:
            if key not in present:
                raise ZContractError(
                    f"null operands at {path}: header key {key!r} is absent from a file declaring "
                    f"schema_version {version}. The version claims a format this file does not "
                    f"have.")
        digest = _scalar(store, "construction_digest", "U", "a unicode string", path)
        if digest != NULL_OPERAND_CONSTRUCTION_DIGEST:
            raise ZContractError(
                f"null operands at {path}: the declared construction digests to {digest} and this "
                f"reader's construction digests to {NULL_OPERAND_CONSTRUCTION_DIGEST}. The file "
                f"and the reader disagree about what these arrays ARE. Either this file was "
                f"written against a construction this reader does not implement, or this reader's "
                f"construction has moved since the file was written. A version this reader "
                f"accepts beside a construction it does not is the silent reinterpretation the "
                f"pair exists to prevent, and reading the arrays cannot settle it.")

        raw = _scalar(store, "declaration_json", "U", "a unicode string", path)
        try:
            decl = json.loads(raw)
        except ValueError as exc:
            raise ZContractError(
                f"null operands at {path}: `declaration_json` is not valid JSON ({exc}).") from exc
        decl = _validate_declaration(decl, version, digest, path)

        missing = [k for k in NULL_OPERAND_ARRAY_KEYS if k not in present]
        if missing:
            raise ZContractError(
                f"null operands at {path}: operand key(s) {missing} absent. §3.3 condition 11b "
                f"requires the ratio to be reconstructible from the persisted operands; a missing "
                f"operand is a reject, not a fallback to the producer's recorded scalar.")
        unexpected = sorted(present - set(NULL_OPERAND_ARRAY_KEYS) - set(NULL_OPERAND_HEADER_KEYS))
        if unexpected:
            raise ZContractError(
                f"null operands at {path}: unexpected key(s) {unexpected} in a file declaring "
                f"schema_version {version}. Content this reader does not know about means the "
                f"writer changed the format without bumping the version -- which is the one thing "
                f"the version exists to prevent.")
        arrays = {k: np.asarray(store[k]) for k in NULL_OPERAND_ARRAY_KEYS}

    _validate_operands(arrays, decl, path)
    return (arrays["x_cv"], arrays["x_cv2"], arrays["support_mask"])


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
    _require_code_identity(code_identity, "receipt")

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
    # ⚠ ROUND-8, FIRST PATH. The breakdown was demanded only when `discriminating` was False,
    # so OMITTING it on a True verdict skipped validation entirely and wrote MET. The asymmetry
    # was never justified: a claim that the gate COULD see a dropped shift is exactly as much in
    # need of its measurements as a claim that it could not, and it is the more consequential of
    # the two, because it is the one a reader treats as assurance.
    blockers = block.get("discrimination_blockers")
    if not isinstance(blockers, dict):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} carries no `discrimination_blockers`. The breakdown "
            f"is required for EITHER verdict -- pinned, saturated and below-tolerance counts are "
            f"what make `discriminating` checkable, and a True verdict without them is an "
            f"assurance with nothing behind it.")
    _validate_discrimination_blockers(blockers, discriminating, rtol)

    if not discriminating:
        note = block.get("note")
        if not isinstance(note, str) or not note.strip():
            raise ZContractError(
                f"receipt: {RECONSTRUCTION_KEY} reports discriminating=False and carries no "
                f"limitation note. A non-discriminating pass is admissible -- a genuinely tiny "
                f"mean shift is not a defect -- but it must arrive WITH the statement of what "
                f"was not tested, or the reader cannot tell it from a discriminating one.")


BLOCKER_COUNTS = ("n_bins", "n_separated", "n_pinned", "n_saturated_v_uni_below_v_blk",
                  "n_shift_below_tolerance")


def _validate_discrimination_blockers(blockers, discriminating, rtol) -> None:
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

    # ⚠ ROUND-8, SECOND PATH. Checking `discriminating == (n_separated > 0)` left the third
    # term free, so the flag and the count could agree while CONTRADICTING the separation they
    # are both derived from. Both of these were written as MET at rtol=1e-9, with valid
    # partitions:
    #     n_separated=0, discriminating=False, max_separation=0.5   (0.5 > rtol: something moved)
    #     n_separated=3, discriminating=True,  max_separation=0     (nothing moved at all)
    #
    # In the producer these are one quantity read three ways -- `n_separated = sum(sep > rtol)`
    # and `max_separation = sep.max()`, so `max(sep) > rtol` iff `any(sep) > rtol` EXACTLY. The
    # identity is therefore checkable in full, and two of its three pairings are not enough: a
    # partial consistency check is what let a self-contradicting record through twice.
    n_sep_positive = blockers["n_separated"] > 0
    sep_exceeds_rtol = blockers["max_separation"] > rtol
    if not (bool(discriminating) == n_sep_positive == sep_exceeds_rtol):
        raise ZContractError(
            f"receipt: {RECONSTRUCTION_KEY} breaks the discrimination identity. "
            f"discriminating={discriminating!r}, n_separated={blockers['n_separated']} "
            f"(> 0 is {n_sep_positive}), max_separation={blockers['max_separation']!r} "
            f"(> rtol {rtol:.0e} is {sep_exceeds_rtol}). These are ONE measurement read three "
            f"ways -- n_separated counts the bins with sep > rtol and max_separation is that "
            f"same sep's maximum -- so all three must agree. They did not, which means the "
            f"record was assembled rather than measured.")


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
