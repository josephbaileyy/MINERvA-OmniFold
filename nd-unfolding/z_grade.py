#!/usr/bin/env python3
"""Grade `(cause 3, Z)` over a MULTI-MEMBER campaign -- the first production caller of `assess()`.

WHAT WAS MISSING, AND WHY IT COULD NOT BE NOTICED. `z_validator.assess()` has existed, tested, for
weeks; `z_statistics` has carried `s_agg`, `s_med` and `s_proj` just as long. **Nothing in
production ever put them together.** `z_build` calls `assess()` with `{}` statistics because one
build is one member and a single member cannot make a cause-3 statistic, so every production call
returned on the branch-2 validity check BEFORE reaching a leg. The branch machinery, the leg set,
the boundaries and the statistics were all reachable and all unreached: `boundary_readership.py`
recorded that `assess` *"has no caller outside `tests/`"*. This module is that caller.

THREE THINGS IT REFUSES TO DO, each because a cheaper version of this file would have done them:

1. **It will not grade one member.** Joseph, 2026-09-19 (`R9`): *"Cause 3 is NOT to be assessed on a
   one-member basis."* A one-member campaign has zero spread by construction, and zero spread is
   `SPEC` §3.7b's **execution falsifier**, not a favourable result. The refusal is at the top of
   `grade()`, before any array is read, so it cannot be reached around.
2. **It will not take a validity field from a producer's say-so.** Every one of the nine
   `Validity` fields is RE-MEASURED here from the members' own bytes -- digests recomputed,
   symmetry and PSD re-run, the support mask and row order compared element-wise across members.
   §1.3b already rejects the *"read the producer's own value back"* shape; a grader that trusted
   `receipt["closure"]` would reintroduce it one level up.
3. **It will not infer a member's offset from its path.** The offset is read from the product's own
   `member_identity` block, which `z_build` writes from the digest-verified throw source.
   `seed_offset_policy.declared_offset` is explicit that an UNHOOKED leg stamps its baseline and is
   *"indistinguishable from a member at k = 0"*, so `est_seed_offset_declared == 0` is a REFUSAL
   and not a member at offset zero.

THE FUNCTIONAL SET FOR `s_proj` IS BUILT, NOT CHOSEN HERE.
`AUTHORIZATION-20260918-d-resource-required-deliverable-path.md` ruling 4 approved *"the rows of
`project_cov_nd.py`'s `M`, plus the all-ones vector"*, and the one required projection is **M1,
`5D -> (E_avail, W)`** (`run_m1_projection.sh:158`, `--keep-axes eavail,W`). So the set is
constructed by calling `project_cov_nd.build_projection` itself rather than by restating its
arithmetic -- a rule retyped is a second implementation that does not change when the first is
corrected.

WHAT A PASS HERE IS AND IS NOT. A branch-3 result grades `(cause 3, Z)`'s `M(ii)` and **authorizes
nothing**. It is not an adoption, and the graded product's own build-time
`scientific_acceptance` is a per-BUILD verdict that stays `NON-PASSING`: at build time a member is
alone and branch 2 is the correct computed answer for it. The campaign verdict is a separate act on
a separate receipt, which is why this file writes one instead of rewriting the products.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

import z_assembly as assembly
import z_contract as contract
import z_receipt as receipt
import z_statistics as statistics
import z_validator as validator
from z_build import acceptance_token

GRADE_SCHEMA_VERSION = 1
TOTAL_KEY = "hCov_combined5d_total_uthrow"
BASELINE_OFFSET = 0

#: The one required projection. `run_m1_projection.sh:158`, and `AUTHORIZATION-20260918` ruling 4.
M1_SRC_AXES = ("pt", "pz", "eavail", "q3", "W")
M1_KEEP_AXES = ("eavail", "W")

#: Every array a member product must carry. Absence is a refusal, not a skipped check.
MEMBER_ARRAYS = (TOTAL_KEY, "hInflation_g", "hPinnedMask", "hXSecND_flat",
                 "hSupportMask", "hRowIndex5D")


class Member:
    """One built Z product, read back from its own bytes.

    Nothing here is taken from the receipt except things the receipt is the ONLY source of
    (the band partition), and those are compared across members rather than believed.
    """

    def __init__(self, product: Path, receipt_path: Path, expect_variant: str) -> None:
        self.product = Path(product).resolve()
        self.receipt_path = Path(receipt_path).resolve()
        self.file_sha256 = receipt.sha256_file(self.product)
        self.arrays: dict[str, np.ndarray] = {}
        self.notes: list[str] = []

        contract.require(self.product.suffix == ".npz",
                         f"{self.product}: this grader reads NPZ products; a ROOT product must be "
                         f"graded by a reader that binds the same bytes, not transcribed first")
        with np.load(self.product, allow_pickle=False) as store:
            present = set(store.files)
            missing = [k for k in (*MEMBER_ARRAYS, "metadata_json") if k not in present]
            contract.require(not missing, f"{self.product}: missing {sorted(missing)}")
            for key in MEMBER_ARRAYS:
                self.arrays[key] = np.asarray(store[key])
            raw = store["metadata_json"]
            contract.require(raw.shape == () and raw.dtype.kind == "U",
                             f"{self.product}: malformed metadata")
            self.metadata: dict[str, Any] = json.loads(str(raw.item()))

        self.receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))

        variant = self.metadata.get("variant")
        contract.require(variant == expect_variant,
                         f"{self.product}: declares variant {variant!r}, expected "
                         f"{expect_variant!r}. A grader that accepts either variant is comparing "
                         f"two different objects.")
        self.variant = variant

        ident = self.metadata.get("member_identity")
        contract.require(isinstance(ident, dict) and
                         {"est_seed_offset_declared", "est_seed_offset"} <= set(ident),
                         f"{self.product}: no member_identity block. A product that cannot say "
                         f"which member it is cannot be one. Rebuild it with a builder that "
                         f"records the offset from its throw source.")
        self.declared = int(ident["est_seed_offset_declared"])
        self.offset = int(ident["est_seed_offset"])
        self.member_identity = ident

    # -- properties every cross-member check reads ------------------------------------------
    @property
    def cov(self) -> np.ndarray:
        return self.arrays[TOTAL_KEY]

    @property
    def central(self) -> np.ndarray:
        return self.arrays["hXSecND_flat"]

    @property
    def mask(self) -> np.ndarray:
        return self.arrays["hSupportMask"].astype(bool)

    @property
    def rows(self) -> np.ndarray:
        return self.arrays["hRowIndex5D"].astype(np.int64)

    def cov_digest(self) -> str:
        return receipt.sha256_array(np.asarray(self.cov, float))

    def footing(self) -> dict:
        return {"mask_sha256": receipt.sha256_array(self.mask),
                "row_order_sha256": receipt.sha256_array(self.rows),
                "n_reported": int(self.mask.sum())}

    def throw_sha256(self):
        """The digest of the throw product this member's covariance was actually built from."""
        return (self.member_identity.get("read_from") or {}).get("sha256")

    def throw_source_on_disk(self) -> dict:
        """RE-HASH the throw product, rather than believing the string inside the member.

        ⚠ AN INDEPENDENT REVIEWER CALLED THE FIRST VERSION COSMETIC AND WAS RIGHT. Distinctness
        was measured on digests *recorded inside each member's own metadata*, so the cheapest
        forgery survived it untouched: copy a member, perturb the covariance, and edit one
        character of the recorded `read_from.sha256`. Two strings differ; no second campaign
        exists. A digest is evidence only when something re-computes it from the bytes.

        Fail-closed: a member whose throw source is not present and readable where it says it is
        cannot be graded. That is stricter than the alternative and it is the point.
        """
        decl = self.member_identity.get("read_from") or {}
        raw_path, declared = decl.get("path"), decl.get("sha256")
        contract.require(bool(raw_path) and bool(declared),
                         f"{self.product}: member_identity records no throw source path/digest")
        path = Path(raw_path)
        contract.require(path.is_file(),
                         f"{self.product}: its throw source {path} is not present, so the digest "
                         f"it records cannot be verified. A recorded digest nobody re-computes is "
                         f"a claim, not evidence.")
        measured = receipt.sha256_file(path)
        contract.require(
            measured == declared,
            f"{self.product}: throw source {path} hashes to {measured}, but the member records "
            f"{declared}. The covariance was not built from the file this member names.")
        return {"path": str(path), "recorded": declared, "recomputed": measured,
                "verified": True}

    def recorded_z_sha256(self):
        return ((self.receipt.get("z") or {}).get("sha256"))

    def recorded_partition(self):
        return ((self.receipt.get("inflation") or {}).get("partition"))

    def reverify_identities(self) -> dict:
        """§1.3b, re-derived from this member's own bytes -- and HONEST about what it cannot reach.

        ⚠ THE FIRST VERSION RAN ONLY `gate_symmetry_psd` AND CALLED THAT `identities_pass`. An
        independent reviewer called it a BLOCK and was right: a campaign that discarded the entire
        inflation -- `g == 1` everywhere -- produces a symmetric PSD block sum, so it would have
        passed and could have reached branch 3, while §3.7b's branch 1 fails any member whose
        `C_Z^(k)` fails a §1.3b identity.

        WHAT IS RE-RUN HERE, from the product alone:
          * symmetry and PSD on the inflated object (`gate_symmetry_psd`);
          * the `g` domain conditions §1.3b states over `g^c`: finite, `>= 1` everywhere, and
            EXACTLY `1` on the pinned set -- `hInflation_g` and `hPinnedMask` are both in the
            product, so this needs nothing external.

        WHAT CANNOT BE RE-RUN HERE, stated rather than quietly dropped: the closure identity and
        the `g` reconstruction need the five component blocks and the raw diagonals, which the
        product does not carry -- it carries their SUM. For those, the receipt must PROVE the gate
        ran by carrying its measured output, which is what `z_receipt`'s reconstruction validator
        checks; a bare boolean is refused there for exactly the reason it would be refused here.

        ⚠ AND ONE THING THE DOMAIN CHECK DOES NOT CATCH, because it MUST NOT. An all-ones `g` is a
        LEGITIMATE outcome of `compute_g` -- it returns exactly `1` wherever `v_uni <= v_blk` --
        so refusing it would be a guard that fires on a correct run. A reviewer read the first
        version of this docstring as claiming otherwise; it did, and it was wrong. What stands
        between a DISCARDED inflation and a pass is the reconstruction block below, not this.
        """
        row: dict[str, Any] = {"product": str(self.product), "reran": [], "verified_recorded": []}
        ok = True
        try:
            row["symmetry_psd"] = assembly.gate_symmetry_psd(self.cov)
            row["reran"].append("gate_symmetry_psd")
        except contract.ZContractError as exc:
            row["symmetry_psd"] = {"error": str(exc)}
            ok = False

        g = np.asarray(self.arrays["hInflation_g"], float)
        pinned = np.asarray(self.arrays["hPinnedMask"], float).astype(bool)
        g_finite = bool(np.all(np.isfinite(g)))
        g_ge_one = bool(np.all(g >= 1.0))
        g_pinned_exact = bool(np.all(g[pinned] == 1.0)) if pinned.any() else True
        row["g_domain"] = {"finite": g_finite, "ge_one": g_ge_one,
                           "exactly_one_where_pinned": g_pinned_exact,
                           "n_pinned": int(pinned.sum()), "g_max": float(g.max()) if g.size else 0.0}
        row["reran"].append("g_domain")
        ok = ok and g_finite and g_ge_one and g_pinned_exact

        inflation = self.receipt.get("inflation") or {}
        try:
            receipt.validate_reconstruction_ran(inflation)
            row["reconstruction"] = {"proved": True,
                                     "by": "z_receipt.validate_reconstruction_ran"}
            row["verified_recorded"].append(receipt.RECONSTRUCTION_KEY)
        except contract.ZContractError as exc:
            row["reconstruction"] = {"proved": False, "why": str(exc)}
            ok = False

        closure = self.receipt.get("closure") or {}
        missing = [k for k in ("active_total_eq_sum5", "blocksum_symmetry_psd") if k not in closure]
        row["closure_blocks"] = {"present": sorted(closure), "missing": missing}
        row["verified_recorded"].append("closure block completeness")
        ok = ok and not missing

        row["passed"] = bool(ok)
        return row

    def describe(self) -> dict:
        return {"product": str(self.product), "file_sha256": self.file_sha256,
                "cov_sha256": self.cov_digest(), "variant": self.variant,
                "est_seed_offset_declared": self.declared, "est_seed_offset": self.offset,
                "receipt": str(self.receipt_path), "footing": self.footing(),
                "member_identity": self.member_identity}


# ------------------------------------------------------------------ the functional set ------
def m1_functionals(mask) -> tuple[np.ndarray, dict]:
    """`s_proj`'s predeclared `u` set: M1's rows plus the all-ones vector.

    Built by CALLING `project_cov_nd.build_projection`, never by restating it. Destination cells
    that receive no reported source cell are excluded, because an all-zero row has zero baseline
    uncertainty and `s_proj` aborts on one -- correctly: it cannot measure the movement of a
    functional that measures nothing.
    """
    import project_cov_nd as proj

    mask = np.asarray(mask, bool)
    src_report = np.flatnonzero(mask).astype(np.int64)
    src_shape = tuple(len(proj.AXIS_EDGES[a]) - 1 for a in M1_SRC_AXES)
    contract.require(int(np.prod(src_shape)) == mask.size,
                     f"m1_functionals: axis edges give {int(np.prod(src_shape))} cells, mask has "
                     f"{mask.size}")
    dst_shape = tuple(len(proj.AXIS_EDGES[a]) - 1 for a in M1_KEEP_AXES)
    n_dst_dense = int(np.prod(dst_shape))

    keep_pos = [M1_SRC_AXES.index(a) for a in M1_KEEP_AXES]
    idx = np.unravel_index(src_report, src_shape)
    dst_dense = np.ravel_multi_index(tuple(idx[p] for p in keep_pos), dst_shape)
    receiving = np.zeros(n_dst_dense, bool)
    receiving[np.unique(dst_dense)] = True
    dst_index_of = np.full(n_dst_dense, -1, np.int64)
    dst_index_of[receiving] = np.arange(int(receiving.sum()))

    M, dropped = proj.build_projection(list(M1_SRC_AXES), list(M1_KEEP_AXES), src_report,
                                       src_shape, dst_shape, dst_index_of)
    # ⚠ `dropped == 0` IS A TAUTOLOGY AND THE REVIEWER SAID SO. `dst_index_of` is built by mapping
    # exactly these source cells, so every one of them has an index by construction; the assertion
    # tested Python's array indexing. Kept as a cheap invariant, but the load-bearing checks are
    # the two below, which are about `M` itself: every reported source cell must contribute to
    # exactly one destination (so no column is empty and none is double-counted), and every row
    # must have at least one contributor (so no functional measures nothing).
    contract.require(dropped == 0, f"m1_functionals: {dropped} cells reach no destination")
    nz_per_col = (M != 0).sum(axis=0)
    nz_per_row = (M != 0).sum(axis=1)
    contract.require(int(nz_per_col.min()) == 1 and int(nz_per_col.max()) == 1,
                     f"m1_functionals: a reported source cell contributes to "
                     f"{int(nz_per_col.min())}..{int(nz_per_col.max())} destinations; "
                     f"marginalization sends each cell to exactly one")
    contract.require(int(nz_per_row.min()) >= 1,
                     "m1_functionals: a destination row has no contributing source cell, so its "
                     "baseline uncertainty is zero and s_proj would abort on it")
    U = np.vstack([M, np.ones((1, src_report.size))])
    provenance = {
        "builder": "project_cov_nd.build_projection",
        "src_axes": list(M1_SRC_AXES), "keep_axes": list(M1_KEEP_AXES),
        "src_shape": list(src_shape), "dst_shape": list(dst_shape),
        "n_dst_dense": n_dst_dense, "n_dst_receiving": int(receiving.sum()),
        "n_functionals": int(U.shape[0]),
        "all_ones_appended": True,
        "authorization": ("AUTHORIZATION-20260918-d-resource-required-deliverable-path.md "
                          "ruling 4: the rows of project_cov_nd.py M, plus the all-ones vector"),
        "sha256": hashlib.sha256(np.ascontiguousarray(U, np.float64).tobytes()).hexdigest(),
    }
    return U, provenance


# ------------------------------------------------------------------ cross-member validity ---
def cross_member_validity(members, declared_K):
    """Re-measure all nine `Validity` fields from the members' bytes. `(Validity, evidence)`.

    Absent or unequal evidence is `False` in every case. No field is read from a producer's
    recorded boolean.
    """
    ev: dict[str, Any] = {}
    base = members[0]

    # ---- branch 1 -------------------------------------------------------------------------
    footings = [m.footing() for m in members]
    footing_ok = all(f == footings[0] for f in footings) and footings[0]["n_reported"] > 0
    ev["footing"] = {"per_member": footings, "agree": bool(footing_ok)}

    digest_rows = []
    digests_agree = True
    for m in members:
        recorded = m.recorded_z_sha256()
        row = {"product": str(m.product), "recomputed": m.file_sha256,
               "receipt_records": recorded,
               "manifest_sha256_metadata": m.metadata.get("manifest_sha256"),
               "manifest_sha256_receipt": ((m.receipt.get("notes") or {})
                                           .get("manifest") or {}).get("sha256")}
        row["match"] = bool(recorded) and recorded == m.file_sha256 and \
            row["manifest_sha256_metadata"] is not None and \
            row["manifest_sha256_metadata"] == row["manifest_sha256_receipt"]
        digests_agree = digests_agree and row["match"]
        digest_rows.append(row)
    ev["digests"] = digest_rows

    partitions = [m.recorded_partition() for m in members]
    partition_agrees = bool(partitions[0]) and all(p == partitions[0] for p in partitions)
    ev["partition"] = {"agree": bool(partition_agrees),
                       "present": [bool(p) for p in partitions]}

    identity_rows, identities_pass = [], True
    for m in members:
        identity_rows.append(m.reverify_identities())
        identities_pass = identities_pass and identity_rows[-1]["passed"]
    ev["identities"] = identity_rows

    cv_held_fixed = all(np.array_equal(m.central, base.central) for m in members)
    ev["cv_held_fixed"] = {"reference": str(base.product),
                           "elementwise_equal": bool(cv_held_fixed),
                           "cv_sha256": receipt.sha256_array(np.asarray(base.central, float))}

    finite_rows, all_finite = [], True
    for m in members:
        bad = sorted(k for k, a in m.arrays.items()
                     if np.asarray(a).size == 0 or not np.all(np.isfinite(a)))
        finite_rows.append({"product": str(m.product), "non_finite_or_empty": bad})
        all_finite = all_finite and not bad
    ev["finiteness"] = finite_rows

    # ---- branch 2 -------------------------------------------------------------------------
    read_back = sorted(m.offset for m in members)
    wanted = sorted(int(k) for k in declared_K)
    offsets_match_K = read_back == wanted and len(set(read_back)) == len(read_back)
    ev["offsets"] = {"declared_K": wanted, "read_back": read_back,
                     "match": bool(offsets_match_K)}

    undeclared = [str(m.product) for m in members if m.declared == 0]
    offset_declared_nonzero = not undeclared
    ev["offset_declaration"] = {
        "per_member": [{"product": str(m.product), "declared": m.declared,
                        "offset": m.offset} for m in members],
        "undeclared": undeclared,
        "why": ("seed_offset_policy.declared_offset: declared = 0 means the leg did not go "
                "through a hooked launcher, so NOTHING can be concluded about which scan member "
                "it is. A baseline-valued seed is not evidence of being the anchor."),
    }

    # ⚠ WIDENED AFTER REVIEW, AND THIS IS THE FIX FOR THE CHEAPEST FORGERY. The reviewer showed
    # that distinctness measured on the covariance alone is bypassed by copying a member and adding
    # `1e-10` to its diagonal: the digests differ, the statistics stay ~0, and a campaign that cost
    # nothing reaches branch 3. Two members are distinct because they came from DIFFERENT UPSTREAM
    # PRODUCTIONS, so the throw source each member was built from must differ too -- that digest is
    # recorded by the builder from the file it actually read, and no amount of post-hoc noise on
    # the covariance creates a second throw campaign.
    cov_digests = [m.cov_digest() for m in members]
    throw_on_disk = [m.throw_source_on_disk() for m in members]
    throw_digests = [t["recomputed"] for t in throw_on_disk]
    manifests = [m.metadata.get("manifest_sha256") for m in members]
    cov_distinct = len(set(cov_digests)) == len(cov_digests)
    throw_distinct = all(throw_digests) and len(set(throw_digests)) == len(throw_digests)
    manifests_distinct = all(manifests) and len(set(manifests)) == len(manifests)
    product_digests_distinct = cov_distinct and throw_distinct and manifests_distinct
    ev["product_digests"] = {
        "covariance": cov_digests, "covariance_distinct": bool(cov_distinct),
        "throw_source": throw_on_disk, "throw_source_distinct": bool(throw_distinct),
        "manifest": manifests, "manifest_distinct": bool(manifests_distinct),
        "distinct": bool(product_digests_distinct),
        "why": ("distinctness is a claim about two PRODUCTIONS, not about two byte strings. "
                "Perturbing one covariance makes the covariance digests differ and changes "
                "nothing about whether a second campaign ran."),
    }

    # The members must have been built by the SAME CODE, or the spread mixes a seed offset with a
    # builder change. This is branch-1 footing, recorded under `footing_ok`.
    revisions = [((m.metadata.get("code_identity") or {}).get("revision")) for m in members]
    closures = [json.dumps((m.metadata.get("code_identity") or {})
                           .get("import_closure_digests"), sort_keys=True) for m in members]
    code_agrees = bool(revisions[0]) and all(r == revisions[0] for r in revisions) \
        and all(c == closures[0] for c in closures)
    ev["code_identity"] = {"revisions": revisions, "agree": bool(code_agrees),
                           "import_closure_identical": bool(
                               all(c == closures[0] for c in closures))}
    # ⚠ A REVIEWER OBJECTED TO FOLDING CODE IDENTITY INTO `footing_ok`, on the ground that footing
    # is about the mathematical problem definition and this is about software revision history.
    # KEPT, WITH THE REASON, because the alternative is worse in the direction that matters: two
    # members built by different code are NOT COMPARABLE, so the campaign is inconclusive, and the
    # only branch that says "inconclusive, report no magnitude" is branch 1. Putting it in branch 2
    # would call a builder mismatch a VACUOUS BASELINE, which is the mischaracterisation R7 just
    # corrected elsewhere; leaving it out would let a mismatch reach a graded number. The reporting
    # concern is answered by naming it: the receipt carries `validity_evidence.code_identity` as
    # its own block, and `footing.code_identity_agrees` says which sub-condition failed.
    footing_ok = bool(footing_ok) and code_agrees
    ev["footing"]["code_identity_agrees"] = bool(code_agrees)
    ev["footing"]["note"] = ("code identity is folded in here deliberately: members built by "
                             "different code are not comparable, and branch 1 is the only branch "
                             "that reports an inconclusive campaign without a magnitude.")

    v = validator.Validity(
        footing_ok=bool(footing_ok),
        digests_agree=bool(digests_agree),
        partition_agrees=bool(partition_agrees),
        identities_pass=bool(identities_pass),
        cv_held_fixed=bool(cv_held_fixed),
        offsets_match_K=bool(offsets_match_K),
        offset_declared_nonzero=bool(offset_declared_nonzero),
        product_digests_distinct=bool(product_digests_distinct),
        all_members_finite=bool(all_finite),
        notes={"measured_by": "z_grade.cross_member_validity",
               "provenance": "every field re-measured from the members' own bytes"},
    )
    return v, ev


# ------------------------------------------------------------------ the statistics -----------
def member_statistics(members, functionals):
    """`s_agg`, `s_med`, `s_proj` over the members, baselined at offset 0."""
    cov_by_offset = {m.offset: m.cov for m in members}
    contract.require(len(cov_by_offset) == len(members),
                     "member_statistics: two members share an offset")
    contract.require(BASELINE_OFFSET in cov_by_offset,
                     f"member_statistics: no member at the baseline offset {BASELINE_OFFSET}; "
                     f"every cause-3 statistic is a change RELATIVE to the anchor")
    base = next(m for m in members if m.offset == BASELINE_OFFSET)
    # ⚠ THE `kappa` ARM IS NOT EVALUATED AND CANNOT BE -- SO THE OPERAND IT WOULD NEED IS RECORDED.
    # `z_build_path.classify_baseline_degeneracy` compares each functional's Rayleigh quotient
    # `q_i / (||u_i||^2 * lambda_max(C_0))` against a declared `kappa`. `kappa` is UNDECLARED and
    # Joseph's standing instruction is *"do not invent an unapproved numerical kappa"*, so routing
    # `s_proj` through that entry point would return `KAPPA_UNDECLARED` and make the leg
    # permanently unevaluable rather than guarded. The round-off half of the degeneracy question
    # IS closed, inside `s_proj` itself. The `kappa` half stays open -- and rather than leave the
    # campaign unable to answer it later, the quotients are measured and written into the receipt
    # here, so whoever declares `kappa` can apply it to THIS campaign without re-running it.
    C0 = np.asarray(base.cov, float)
    U = np.atleast_2d(np.asarray(functionals, float))
    q0 = np.einsum("ij,jk,ik->i", U, C0, U)
    nsq = np.einsum("ij,ij->i", U, U)
    lam_max = float(np.linalg.eigvalsh(C0)[-1])
    rayleigh = (q0 / (nsq * lam_max)).tolist() if lam_max > 0 else None
    agg = statistics.s_agg(cov_by_offset, baseline_key=BASELINE_OFFSET)
    med = statistics.s_med(cov_by_offset, base.central, base.mask, baseline_key=BASELINE_OFFSET)
    prj = statistics.s_proj(cov_by_offset, functionals, baseline_key=BASELINE_OFFSET)
    movement = statistics.per_bin_movement(cov_by_offset, base.mask,
                                           baseline_key=BASELINE_OFFSET, x_cv=base.central)
    return ({"s_agg": agg["s_agg"], "s_med": med["s_med"], "s_proj": prj["s_proj"]},
            {"s_agg": agg, "s_med": med, "s_proj": prj,
             "per_bin_movement_REPORTED_GRADING_NOTHING": movement,
             "kappa_arm_NOT_EVALUATED": {
                 "why": ("kappa is UNDECLARED and may not be invented (Joseph, 2026-09-11). "
                         "z_build_path.evaluate_a7 returns KAPPA_UNDECLARED, so routing through "
                         "it would make this leg unevaluable rather than guarded. The ROUND-OFF "
                         "half of the degeneracy question is closed inside s_proj itself."),
                 "operand_recorded_so_a_later_kappa_can_be_applied": True,
                 "predicate": "q_i / (||u_i||^2 * lambda_max(C_0)) >= kappa",
                 "lambda_max_baseline": lam_max,
                 "rayleigh_quotients": rayleigh,
                 "min_rayleigh": (min(rayleigh) if rayleigh else None)}})


# ------------------------------------------------------------------ the null -----------------
def measure_null(null_npz: Path, graded=None) -> dict:
    """Re-measure `r_null` from the graded member's OWN persisted operands, and PROVE they are its.

    Recomputed, not read out of a receipt: R8 requires the graded product's null to be measured in
    its own production, and a number copied from a JSON file is a claim about a measurement rather
    than the measurement.

    ⚠ AND THE FILE MUST BELONG TO THE GRADED MEMBER. An independent reviewer showed the cheapest
    way past the first version: hand it *any* valid `null.npz` from *any* run. Nothing tied the two
    together, so "measured in its own production" was a sentence in a docstring rather than a
    check. Three bindings now, all from the graded member's own receipt and arrays:
      1. the file's `sha256` is the one the builder recorded when it persisted the operands;
      2. the recomputed `r_null` reproduces the value in that receipt;
      3. the null's support mask is elementwise equal to the member's own `hSupportMask`.
    """
    path = Path(null_npz)
    x1, x2, mask = receipt.load_null_operands(path)
    measured = statistics.reconstruct_null_ratio(x1, x2, mask)
    out = validator.assess_null(measured["r_null"])
    out["reconstruction"] = measured
    out["source"] = receipt.stamp_file(path)
    if graded is not None:
        recorded = ((graded.receipt.get("null") or {}).get("persisted") or {}).get("stamp") or {}
        contract.require(
            recorded.get("sha256") == out["source"]["sha256"],
            f"null: {path} has sha256 {out['source']['sha256']}, but the graded member's receipt "
            f"records {recorded.get('sha256')!r} for its persisted operands. R8 requires the "
            f"graded product's null to be measured in ITS OWN production; an unbound file is "
            f"another run's null wearing the right filename.")
        recorded_r = (graded.receipt.get("null") or {}).get("r_null")
        contract.require(
            recorded_r is not None and float(recorded_r) == float(measured["r_null"]),
            f"null: recomputed r_null {measured['r_null']!r} does not reproduce the value the "
            f"graded member's receipt records ({recorded_r!r}).")
        contract.require(
            np.array_equal(np.asarray(mask, bool), graded.mask),
            "null: the persisted support mask is not the graded member's own support.")
        out["bound_to_graded_member"] = {
            "product": str(graded.product), "receipt_sha256": recorded.get("sha256"),
            "receipt_r_null": recorded_r, "mask_elementwise_equal": True}
    return out


# ------------------------------------------------------------------ the grade ----------------
def load_preregistration(path):
    """R8's control on `--declared-K` and the graded offset: they are DECLARED IN ADVANCE.

    The reviewer's point was exact -- a `K` chosen after seeing the members' offsets is not a
    predeclaration, it is a description. The preregistration is a committed file; the grader reads
    `K`, the graded offset and the builder revision out of it and refuses any disagreement with its
    own arguments, so the arguments cannot be tuned to the campaign.
    """
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key in ("declared_K", "graded_offset", "builder_revision", "S", "epsilon", "pass_rule"):
        contract.require(key in doc, f"preregistration {path}: missing {key!r}")
    doc["_stamp"] = receipt.stamp_file(path)
    return doc


def grade(members, declared_K, graded_offset, null_npz, prereg=None):
    """The campaign verdict. Validity dominates; the null gates the token."""
    if prereg is not None:
        contract.require(
            sorted(int(k) for k in prereg["declared_K"]) == sorted(int(k) for k in declared_K),
            f"grade: --declared-K {sorted(declared_K)} is not the preregistered "
            f"{sorted(prereg['declared_K'])}. A set chosen after seeing the members is a "
            f"description, not a predeclaration.")
        contract.require(
            int(prereg["graded_offset"]) == int(graded_offset),
            f"grade: --graded-offset {graded_offset} is not the preregistered "
            f"{prereg['graded_offset']}.")
        for m in members:
            rev = (m.metadata.get("code_identity") or {}).get("revision")
            contract.require(
                rev == prereg["builder_revision"],
                f"grade: {m.product} was built at {rev!r}, not the preregistered builder "
                f"revision {prereg['builder_revision']!r}.")
    contract.require(len(members) >= 2,
                     "R9, Joseph 2026-09-19: cause 3 is NOT to be assessed on a one-member "
                     "basis. A one-member campaign has zero spread BY CONSTRUCTION and zero "
                     "spread is the execution falsifier, not a favourable result.")
    offsets = [m.offset for m in members]
    contract.require(graded_offset in offsets,
                     f"grade: the graded offset {graded_offset} is not among the members "
                     f"{sorted(offsets)}")
    graded = next(m for m in members if m.offset == graded_offset)

    v, ev = cross_member_validity(members, declared_K)

    # ⚠ VALIDITY IS EVALUATED FIRST, AND A FAILURE MEANS NO MAGNITUDE IS COMPUTED AT ALL.
    # `SPEC` §3.7b's branch 1 ends with two words -- **"Report no magnitude."** -- and branch 2 is
    # the execution falsifier, so neither may be accompanied by a number a reader could quote.
    # The first version of this function computed the statistics unconditionally and passed them
    # to `assess()`, relying on `assess()` to return on the validity check before reading them.
    # That is wrong twice over: it would have PUT the magnitudes in the receipt beside a branch-1
    # verdict, and on the failures that matter it does not even get that far -- two members with
    # different support masks have different dimensions, and a member carrying a `NaN` gives
    # `sqrt(Tr C) = nan`, so the grader raised where it was supposed to REPORT WRONG FOOTING.
    # Both were caught by the tests for those exact branches.
    blocking = list(v.branch1_failures()) + list(v.branch2_failures())
    if blocking:
        stats: dict = {}
        u_prov = {"built": False,
                  "why": ("SPEC 3.7b: a validity failure dominates every numerical branch and "
                          "branch 1 says 'Report no magnitude.' No functional set was built.")}
        stats_detail = {"computed": False, "blocking_validity_fields": blocking,
                        "why": u_prov["why"]}
    else:
        U, u_prov = m1_functionals(members[0].mask)
        stats, stats_detail = member_statistics(members, U)
    outcome = validator.assess(validator.Z_LEG_SET, stats, v)
    science = outcome.describe()
    # The null is a magnitude too, and it was previously measured UNCONDITIONALLY -- so a branch-1
    # verdict shipped with an `r_null` beside it, and a bad null file could raise where the grader
    # was supposed to report WRONG FOOTING. Both were the reviewer's finding. It is now inside the
    # same gate as the cause-3 statistics.
    if blocking:
        null = {"measured": False, "assessable": False,
                "why": ("SPEC 3.7b: a validity failure dominates, and branch 1 says 'Report no "
                        "magnitude.' The null is a magnitude. Not measured."),
                "blocking_validity_fields": blocking}
        null_within = False
    else:
        null = measure_null(null_npz, graded=graded)
        null["measured"] = True
        null_within = bool(null.get("assessable") and null.get("verdict") == "within bound")
    token = acceptance_token(science, null_within=null_within)

    return {
        "schema_version": GRADE_SCHEMA_VERSION,
        "written_at_utc": receipt.utc_now(),
        "subject": "(cause 3, Z) M(ii) -- multi-member estimator-seed campaign verdict",
        "scientific_acceptance": token,
        "outcome": science,
        "statistics": stats,
        "statistics_detail": stats_detail,
        "null": null,
        "null_within_bound": null_within,
        "graded_product": graded.describe(),
        "comparison_members": [m.describe() for m in members if m is not graded],
        "declared_K": sorted(int(k) for k in declared_K),
        "preregistration": (None if prereg is None else
                            {k: prereg[k] for k in ("declared_K", "graded_offset",
                                                    "builder_revision", "S", "epsilon",
                                                    "pass_rule", "_stamp")}),
        "leg_set": validator.Z_LEG_SET.describe(),
        "functionals": u_prov,
        "validity_evidence": ev,
        "boundaries": {k: b.describe() for k, b in contract.Z_BOUNDARIES.items()},
        "withheld_boundaries": {k: b.describe()
                                for k, b in contract.withheld_boundaries().items()},
        "authorizes": ("NOTHING. A branch-3 result grades (cause 3, Z)'s M(ii) only. Adoption is "
                       "a separate act naming this digest. The graded product's own build-time "
                       "scientific_acceptance is a per-BUILD verdict and stays NON-PASSING: at "
                       "build time a member is alone, and branch 2 is the correct answer for it."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--member", action="append", required=True, metavar="PRODUCT:RECEIPT",
                    help="repeatable; at least two are required")
    ap.add_argument("--declared-K", required=True,
                    help="comma-separated declared offset set, e.g. 0,1200")
    ap.add_argument("--graded-offset", type=int, required=True)
    ap.add_argument("--null-npz", required=True,
                    help="the GRADED member's own persisted null operands")
    ap.add_argument("--variant", required=True, choices=("cv", "mean"))
    ap.add_argument("--preregistration", required=True,
                    help="the committed preregistration JSON. R8: K, the graded offset and the "
                         "builder revision are declared BEFORE production, and the grader refuses "
                         "arguments that disagree with it. ⚠ REQUIRED, NO DEFAULT -- it had one, "
                         "and an independent reviewer pointed out that dropping the flag then "
                         "skipped every predeclaration check. Suppression by omission needs no "
                         "positive act, so it is EASIER than a flag, not harder; this repository "
                         "already has that finding on record at z_build_path.py and I reproduced "
                         "it one module later.")
    ap.add_argument("--out", required=True, help="grading receipt path (.json), must not exist")
    args = ap.parse_args(argv)

    out = Path(args.out)
    contract.require(out.suffix == ".json", "--out must be .json")
    contract.require(not out.exists(), f"--out exists: {out}. A grade is written once.")

    members = []
    for spec in args.member:
        product, _, receipt_path = spec.partition(":")
        contract.require(receipt_path, f"--member needs PRODUCT:RECEIPT, got {spec!r}")
        members.append(Member(Path(product), Path(receipt_path), args.variant))

    declared_K = [int(k) for k in args.declared_K.split(",") if k.strip()]
    prereg = load_preregistration(args.preregistration)
    result = grade(members, declared_K, args.graded_offset, Path(args.null_npz), prereg=prereg)
    out.parent.mkdir(parents=True, exist_ok=True)
    stamp = receipt.write_receipt(out, result)
    print(json.dumps({"grade_receipt": stamp,
                      "scientific_acceptance": result["scientific_acceptance"],
                      "branch": result["outcome"]["branch"],
                      "branch_label": result["outcome"]["branch_label"],
                      "statistics": result["statistics"],
                      "r_null": result["null"].get("r_null")}, indent=2))
    # 0 = graded MET and null within bound; 2 = graded, not passing. Never share a code with a
    # usage error, which argparse already owns at 2 -- so a refusal raises instead.
    return 0 if result["scientific_acceptance"] == "PASSING" else 2


if __name__ == "__main__":
    sys.exit(main())
