#!/usr/bin/env python3
"""Z's build path: estimator-seed selection and block-source selection, CONTROLLED SEPARATELY.

AUTHORIZED SCOPE (2026-09-11): implementation and local synthetic tests only. NOT merge, NOT cluster
execution, NOT adoption, and nothing here moves Gate 2 or R5. `1%` is a PROPOSED requirement.

WHY THIS MODULE EXISTS -- the one-variable conflation, measured at 6f24fb00
--------------------------------------------------------------------------
`lib_member_resume.sh:230` is `mr_declared() { [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; }`, so ONE
variable simultaneously means two things:

    (a) "this run is a member of the declared offset set K"
    (b) "build your own statistical and ML blocks"

Because they are the same switch, `sbatch_finalize_5d_bkgaware_gpu.sh:416-424` reads
`if mr_declared; then ... "building this member's OWN C_stat and C_ML"` -- both blocks member-local
via `mr_prefix` at `:414-415`. The `else` at `:423` says *"undeclared: reusing the archive's
C_stat/C_ML, per this script's original contract"*.

⚠ AND THE HEADER DESCRIBES THE `else` PATH, NOT THE MEMBER PATH. `:8-10` states the original
contract -- *"C_stat/C_ML are #13-invariant -> reuse existing"* -- and the `mr_declared` branch
OVERRIDES it. A contract stated at the top of a file is the thing the code below it is most likely
to override, and reading `:8-10` as the member behaviour is a recorded error in this campaign.

SO: with one switch there is no configuration that has a NONTRIVIAL `K` AND SHARED BLOCKS, which is
the only configuration in which a released-bar stability criterion can both BIND and be SATISFIABLE.
Separating the two controls is what makes it reachable. The criterion is not loosened to fit the
launcher; the launcher gains a control it did not have.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not launch anything, does not write products, does not choose `kappa`, and does not grade.
`assess_*` lives in `z_validator`. Every scientific number here is either DECLARED by a caller or
the call FAILS -- there are no numerical defaults, per Joseph's 2026-09-11 instruction *"do not
invent an unapproved numerical kappa."*
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from z_contract import ZContractError, require


# ------------------------------------------------------------------ the two SEPARATE controls --
#: Control 2's admissible values. `SHARED` is DIGEST-bound, never path-bound: two members agreeing
#: on a path prove nothing (the path can be rewritten between reads -- the 07-13 rebuild in this
#: campaign's provenance search is the worked example, where identical paths held different bytes).
BLOCK_SOURCES = ("SHARED_DIGEST_BOUND", "PER_MEMBER")


@dataclass(frozen=True)
class BuildPath:
    """Control 1 (membership) and control 2 (block source), declared independently.

    Neither is inferred from the other and neither has a default. A caller that omits either gets
    an error rather than a behaviour.
    """

    member_offset: Optional[int]
    """Control 1. `None` = not a member of `K` (the archive path). An int = this member's offset."""

    block_source: str
    """Control 2. One of `BLOCK_SOURCES`. INDEPENDENT of `member_offset` -- that independence IS
    the authorized change."""

    stat_digest: Optional[str] = None
    ml_digest: Optional[str] = None
    """Required when `block_source == "SHARED_DIGEST_BOUND"`: the digests every member must read."""

    def __post_init__(self):
        require(self.block_source in BLOCK_SOURCES,
                f"block_source {self.block_source!r} not in {BLOCK_SOURCES}; there is no default")
        if self.member_offset is not None:
            require(isinstance(self.member_offset, (int, np.integer)),
                    f"member_offset must be an int, got {type(self.member_offset).__name__}")
        if self.block_source == "SHARED_DIGEST_BOUND":
            require(bool(self.stat_digest) and bool(self.ml_digest),
                    "SHARED_DIGEST_BOUND requires BOTH stat_digest and ml_digest. Sharing a PATH "
                    "is not sharing bytes -- this campaign measured identical paths holding "
                    "different bytes across a rebuild.")

    @property
    def is_member(self) -> bool:
        return self.member_offset is not None

    @property
    def blocks_are_shared(self) -> bool:
        return self.block_source == "SHARED_DIGEST_BOUND"

    def describe(self) -> dict:
        return {"member_offset": self.member_offset, "is_member": self.is_member,
                "block_source": self.block_source, "blocks_are_shared": self.blocks_are_shared,
                "stat_digest": self.stat_digest, "ml_digest": self.ml_digest}


# --------------------------------------------------- requirement 3: the ENUMERATION, verified --
#: What is member-local under a DECLARED member. Population taken from ALL EIGHT
#: `mr_prefix`/`mr_dir_prefix` call sites in `sbatch_finalize_5d_bkgaware_gpu.sh`, enumerated by
#: grepping the whole file for the construct.
#:
#: ⚠⚠ REV. 2: REV. 1 DEFINED THIS FROM A WINDOW OF LINES (`:403-415`) AND MISSED TWO -- and it did
#: so in a tuple whose own comment warns against exactly that (*"NOT only the bands, which is what a
#: reader of the COMB line alone would conclude"*). Six sites are in that window; `:422` and `:423`
#: are not, and they are `boot_nd_5d` and `seedscan_split_5d` -- THE REPLICA INPUT DIRECTORIES,
#: member-prefixed on the same condition as the other six. **A warning against inferring a
#: population from a subset of lines, implemented by inferring a population from a window of lines.**
MEMBER_LOCAL_TODAY = (
    "CV",                  # :405  the member's own universe-sweep CV
    "OUTD",                # :409  member-scoped output directory
    "COMB",                # :410  the combined systematic-universe covariance (the BANDS)
    "SWEEP_GLOB",          # :411  the member's universe sweep inputs
    "UTHROW",              # :412  the unified-throw covariance  <-- not only the bands
    "STAT_COV",            # :413  the statistical block
    "ML_COV",              # :414  the ML block
    "boot_nd_5d",          # :422  ⚠ the BOOTSTRAP REPLICA DIR, --expected-ids 1-100
    "seedscan_split_5d",   # :423  ⚠ the SEEDSCAN SPLIT REPLICA DIR, --expected-ids 1-24
)

#: What MUST vary when the estimator baseline changes -- derived products downstream of the
#: estimator, rebuilt from inputs that already exist. These are the CHEAP terms.
RECOMPUTED_UNDER_ESTIMATOR_CHANGE = ("CV", "SWEEP_GLOB", "COMB", "UTHROW", "OUTD")

#: ⚠ THE THIRD CATEGORY, and it is warranted rather than tidy. `boot_nd_5d` and `seedscan_split_5d`
#: are member-local INPUT ENSEMBLES that must be POPULATED, not derived products to recompute --
#: neither "recomputed" nor "pinned" is true of them. The category exists because of the COST
#: asymmetry: `STAT_COV`/`ML_COV` are cheap combines OVER these replicas, while the replicas are the
#: actual compute. An enumeration used to price a member run that omits these understates it BY THE
#: DOMINANT TERMS while including five cheap entries.
#: And there is no cheap third option: `:418-420` keeps `--expected-ids` at the FULL range on
#: purpose, so a member either has its own complete 100 + 24 or the run REFUSES.
MEMBER_LOCAL_INPUTS_REQUIRING_POPULATION = {
    "boot_nd_5d": {"declared_ids": "1-100", "n": 100, "site": ":422",
                   "kind": "bootstrap replicas", "cost": "DOMINANT"},
    "seedscan_split_5d": {"declared_ids": "1-24", "n": 24, "site": ":423",
                          "kind": "seedscan splits", "cost": "DOMINANT"},
}

#: What MUST NOT vary under `SHARED_DIGEST_BOUND` -- the decoupling's whole content.
INVARIANT_UNDER_SHARED_BLOCKS = ("STAT_COV", "ML_COV")


def enumerate_recomputation(path: BuildPath) -> dict:
    """Which components are recomputed for this build path, and which are pinned.

    This is requirement 3's deliverable as a FUNCTION rather than a paragraph, so a receipt can
    record what actually applied instead of what a document said would.
    """
    require(isinstance(path, BuildPath), "enumerate_recomputation: need a BuildPath")
    if not path.is_member:
        return {"recomputed": (), "pinned": MEMBER_LOCAL_TODAY,
                "note": "not a member of K: the archive path, nothing member-local"}
    recomputed = list(RECOMPUTED_UNDER_ESTIMATOR_CHANGE)
    if path.blocks_are_shared:
        pinned = list(INVARIANT_UNDER_SHARED_BLOCKS)
        must_populate = {}
    else:
        recomputed += list(INVARIANT_UNDER_SHARED_BLOCKS)
        pinned = []
        # ⚠ the replica ensembles are only needed when the member builds its OWN blocks
        must_populate = dict(MEMBER_LOCAL_INPUTS_REQUIRING_POPULATION)

    _terms = ", ".join([k + " n=" + str(v["n"])
                        for k, v in sorted(must_populate.items())]) or "none"
    # ⚠ A FOURTH STATE, found by smoke-testing the function rather than by reading it. Under
    # SHARED_DIGEST_BOUND the member never runs the combines, so the member-local REPLICA dirs are
    # never read: they are neither recomputed, nor pinned, nor to-populate -- they are NOT USED.
    # Without this the coverage flag read False for a configuration that is fully specified, which
    # would have looked like the omission it exists to detect.
    not_used = ({} if not path.blocks_are_shared
                else {k: "not read: the member does not run the combines under SHARED blocks"
                      for k in MEMBER_LOCAL_INPUTS_REQUIRING_POPULATION})
    covered = set(recomputed) | set(pinned) | set(must_populate) | set(not_used)
    uncovered = [c for c in MEMBER_LOCAL_TODAY if c not in covered]
    # the universal is DERIVED, not asserted: rev. 1's note said "EVERY component varies" while the
    # code compared against a hand-listed set, so the comment quantified over the enumeration only.
    return {"recomputed": tuple(recomputed), "pinned": tuple(pinned),
            "must_be_populated": must_populate,
            "not_used": not_used,
            "uncovered": tuple(uncovered),
            "covers_all_member_local": not uncovered,
            "dominant_cost_terms": tuple(sorted(must_populate)),
            "note": ("blocks SHARED and digest-bound: only estimator-downstream components vary, "
                     "and the replica ensembles need NOT be repopulated -- which is where the "
                     "saving is"
                     if path.blocks_are_shared else
                     f"blocks PER_MEMBER: {len(recomputed)} recomputed plus "
                     f"{len(must_populate)} INPUT ENSEMBLES to populate ({_terms}) -- and a "
                     f"released-bar criterion cannot separate estimator sensitivity from block "
                     f"resampling")}


# ------------------------------------------------------- the declared population (control 1) --
def declared_population(offsets, declared_at: str) -> tuple:
    """`K`, EXPLICITLY declared and NONTRIVIAL. Not defaulted, not inferred.

    Fails closed on the three ways a population can be vacuous, because a vacuous `K` makes every
    difference statistic return 0 and that is `INCONCLUSIVE / VACUOUS SEED VARIATION`, never a pass.
    """
    require(bool(declared_at), "declared_population: `declared_at` must name where K was declared")
    ks = [int(k) for k in offsets]
    require(len(ks) >= 2,
            f"K has {len(ks)} member(s); a population with fewer than 2 cannot exhibit "
            f"estimator-baseline variation at all. This is VACUOUS, not passing.")
    require(len(set(ks)) == len(ks), f"K contains duplicate offsets: {ks}")
    require(0 in ks, f"K must contain the baseline offset 0; got {sorted(ks)}")
    require(any(k != 0 for k in ks),
            "K contains only the baseline; there is no variation to measure")
    return tuple(sorted(ks))


# ------------------------------------------------------------------ terminal handling (item 2) --
#: `CRITERIA` §0's vocabulary is NOT extended. These are REPORTED states that map to existing
#: `z_validator` branches -- see `A7_TERMINAL_ROUTING`.
A7_TERMINAL_ROUTING = {
    "VACUOUS_SEED_VARIATION": "branch 2 (INCONCLUSIVE / VACUOUS BASELINE VARIATION)",
    "DEGENERATE_FUNCTIONAL": "branch 1 (INCONCLUSIVE / WRONG FOOTING) -- names the FUNCTIONAL",
    "KAPPA_UNDECLARED": "branch 1 -- refuses; there is NO default kappa",
    "SUPPORT_DEFINITION_CHANGED": "branch 1 -- names the changed declaration",
    "FEASIBILITY_NOT_APPLICABLE": "reported NOT APPLICABLE, never SATISFIED (Joseph, item 4)",
}


def classify_baseline_degeneracy(q_baseline, c_scale, kappa: Optional[float]):
    """Is a declared functional's baseline numerically resolvable?

    `q_baseline` = `m_i' C_0 m_i` per declared functional; `c_scale` = a declared scale for `C_0`
    (e.g. its largest eigenvalue). Returns the terminal state and the offending indices.

    ⚠ `kappa` HAS NO DEFAULT. If it is `None` this returns `KAPPA_UNDECLARED` rather than choosing
    a cutoff -- Joseph, 2026-09-11: *"do not invent an unapproved numerical kappa."* A silent
    default here would be a numerical convenience acquiring scientific authority.

    ⚠ AND THE STRUCTURAL ARM RUNS FIRST AND NEEDS NO `kappa`: an EXACTLY non-positive baseline is
    degenerate regardless of any threshold, so that case is caught even while `kappa` is withheld.
    """
    q = np.asarray(q_baseline, float)
    require(q.ndim == 1 and q.size > 0, f"baseline quadratic forms: want 1-D non-empty, got {q.shape}")
    scale = float(c_scale)
    require(np.isfinite(scale) and scale > 0, f"c_scale must be finite and positive, got {scale!r}")

    nonfinite = np.nonzero(~np.isfinite(q))[0]
    if nonfinite.size:
        return {"state": "DEGENERATE_FUNCTIONAL", "reason": "non-finite baseline",
                "functionals": nonfinite.tolist(), "kappa": kappa}

    # structural arm: exact zero or negative. No threshold can make this resolvable.
    structural = np.nonzero(q <= 0.0)[0]
    if structural.size:
        return {"state": "DEGENERATE_FUNCTIONAL",
                "reason": "baseline q = m' C_0 m is <= 0 EXACTLY; degenerate structurally, not "
                          "by threshold. ⚠ Blaming the OPERAND here would be wrong: C_0 may be "
                          "PSD and the FUNCTIONAL is what has no support.",
                "functionals": structural.tolist(), "kappa": kappa}

    if kappa is None:
        return {"state": "KAPPA_UNDECLARED",
                "reason": "every declared functional has a strictly positive baseline, so the "
                          "structural arm is silent -- but distinguishing a ROUND-OFF positive "
                          "from a resolvable one requires a declared relative cutoff `kappa`, and "
                          "there is no approved value. REFUSING rather than defaulting.",
                "functionals": [], "kappa": None}

    k = float(kappa)
    require(np.isfinite(k) and k > 0, f"kappa must be finite and positive, got {kappa!r}")
    below = np.nonzero(q < k * scale)[0]
    if below.size:
        return {"state": "DEGENERATE_FUNCTIONAL",
                "reason": f"baseline below the declared relative cutoff kappa={k:.3e}",
                "functionals": below.tolist(), "kappa": k}
    return {"state": "RESOLVED", "reason": "every declared functional's baseline is resolvable",
            "functionals": [], "kappa": k}


def classify_support_change(declared_support, observed_support):
    """A changed projection/support definition is a DECLARATION defect, not a tolerance question."""
    d = np.asarray(declared_support, bool)
    o = np.asarray(observed_support, bool)
    if d.shape != o.shape:
        return {"state": "SUPPORT_DEFINITION_CHANGED",
                "reason": f"support shape {o.shape} != declared {d.shape}", "n_differing": -1}
    diff = int(np.sum(d != o))
    if diff:
        return {"state": "SUPPORT_DEFINITION_CHANGED",
                "reason": f"{diff} bin(s) differ from the declared support",
                "n_differing": diff, "indices": np.nonzero(d != o)[0][:10].tolist()}
    return {"state": "RESOLVED", "reason": "support matches the declaration", "n_differing": 0}


# ----------------------------------------------------- item 1: BOTH-DIRECTION support checks --
def check_projection_support(M, declared_exclusions=()):
    """Both arms of the map's support check, each naming what it catches. ADDITIVE -- this does not
    modify `project_cov_nd.build_projection`, whose existing callers must keep their behaviour.

    ARM 1 (SOURCE-side): a reported source column reaching no destination row -- an all-zero COLUMN.
    ARM 2 (DESTINATION-side): a reported destination row reached by no source column -- an all-zero
      ROW. Lifted from `p4_lib:1395`'s predicate, whose comment records the real-product MASKING
      incident: orphan rows survive to a central check as exact zeros and report `rel = 1.0`
      regardless of how small the bin is, hiding the actual result behind them.

    ⚠ NEITHER ARM SUBSUMES THE OTHER: arm 1 quantifies over COLUMNS, arm 2 over ROWS, and a map can
    be perfect in one direction and defective in the other.

    `declared_exclusions` is the FIRST of two ledgers: intentional, enumerated destination rows that
    are declared absent (the `[3,100] GeV` catch bin excluded from `fig:eavail`'s axis is the worked
    case). They are reported SEPARATELY and never summed with discarded support -- a declared
    exclusion is a scientific choice with a reason; a dropped bin is a map defect with none, and one
    number carrying both would have two meanings and no way to tell which.
    """
    M = np.asarray(M, float)
    require(M.ndim == 2, f"check_projection_support: M must be 2-D, got {M.shape}")
    excl = {int(i) for i in declared_exclusions}
    n_dst = M.shape[0]
    for i in excl:
        require(0 <= i < n_dst, f"declared exclusion row {i} is outside 0..{n_dst-1}")

    orphan_rows = [int(r) for r in np.nonzero(~M.any(axis=1))[0] if int(r) not in excl]
    orphan_cols = [int(c) for c in np.nonzero(~M.any(axis=0))[0]]

    return {
        "arm1_source_side": {"catches": "reported SOURCE bins reaching no destination row",
                             "orphan_columns": orphan_cols, "n": len(orphan_cols),
                             "ok": not orphan_cols},
        "arm2_destination_side": {"catches": "reported DESTINATION rows reached by no source bin",
                                  "orphan_rows": orphan_rows, "n": len(orphan_rows),
                                  "ok": not orphan_rows},
        "declared_exclusions": {"ledger": "SEPARATE -- intentional, with reasons",
                                "rows": sorted(excl), "n": len(excl)},
        "ok": (not orphan_cols) and (not orphan_rows),
    }


def require_projection_support(M, declared_exclusions=(), where: str = "projection"):
    """`check_projection_support` as a fail-closed gate, at CONSTRUCTION.

    `p4_lib:1393`: *"Fail here, at construction, where the diagnosis is the orphan list itself."*
    Failing at the central comparison instead is where the masking happens.
    """
    rep = check_projection_support(M, declared_exclusions)
    a1, a2 = rep["arm1_source_side"], rep["arm2_destination_side"]
    if not a2["ok"]:
        raise ZContractError(
            f"{where}: ARM 2 (destination-side) -- {a2['n']} declared destination row(s) receive no "
            f"contribution from any reported source bin: {a2['orphan_rows'][:10]}"
            f"{' ...' if a2['n'] > 10 else ''}. These rows are all-zero in M and would reach a "
            f"central comparison as EXACT ZEROS, reporting rel = 1.0 regardless of bin size and "
            f"masking every other result. Declared exclusions ({sorted(rep['declared_exclusions']['rows'])}) "
            f"are accounted for separately and are NOT among these.")
    if not a1["ok"]:
        raise ZContractError(
            f"{where}: ARM 1 (source-side) -- {a1['n']} reported source bin(s) reach no destination "
            f"row: {a1['orphan_columns'][:10]}{' ...' if a1['n'] > 10 else ''}. Support would be "
            f"silently discarded out of the map.")
    return rep


# ------------------------------------------------------------------- item 4: member receipts --
@dataclass
class MemberReceipt:
    """ACTUAL seeds, component sources and producing revisions -- not declared ones.

    The distinction is the one this campaign has paid for most often: a launcher's `--expected-ids`
    is what was ASKED FOR, a printed count is what was SEEN, and a job State is neither. Every field
    here is recorded from the run, and `verify_against` compares record to declaration.
    """

    member_offset: int
    actual_seeds: dict = field(default_factory=dict)
    component_sources: dict = field(default_factory=dict)   # name -> {"path":…, "digest":…}
    producing_revisions: dict = field(default_factory=dict)  # tool -> commit
    notes: dict = field(default_factory=dict)

    def verify_against(self, path: BuildPath, declared_K) -> dict:
        """Did the run do what the build path declared? Returns failures rather than raising, so a
        caller can report every mismatch at once."""
        fails = []
        if self.member_offset not in tuple(declared_K):
            fails.append(f"member_offset {self.member_offset} is not in declared K {tuple(declared_K)}")
        if not self.actual_seeds:
            fails.append("no ACTUAL seeds recorded: a declared offset that never reached the "
                         "estimator is VACUOUS_SEED_VARIATION, not a pass")
        if path.blocks_are_shared:
            for name, want in (("STAT_COV", path.stat_digest), ("ML_COV", path.ml_digest)):
                got = (self.component_sources.get(name) or {}).get("digest")
                if got is None:
                    fails.append(f"{name}: no digest recorded, so sharing is UNVERIFIED")
                elif got != want:
                    fails.append(f"{name}: digest {got!r} != the shared digest {want!r}; the "
                                 f"blocks are NOT shared at runtime whatever the flag said")
        missing_rev = [k for k, v in self.producing_revisions.items() if not v]
        if missing_rev:
            fails.append(f"producing revision absent for {missing_rev}")
        if not self.producing_revisions:
            fails.append("no producing revisions recorded")
        return {"ok": not fails, "failures": fails,
                "checked": {"member_offset": self.member_offset,
                            "blocks_are_shared": path.blocks_are_shared}}


def preservation_guard(out_path: str, allow_overwrite: bool = False) -> None:
    """Requirement 5: additive only. No implicit fallback, no overwrite.

    `SPEC` §1.6 warns that `p4_build_components.py:180` opens `--out` with `RECREATE` and
    `adopt_unified_5d.py:79-80` DEFAULTS `--out` -- so a Z build that inherited either could
    overwrite an archived artifact without naming it. This refuses unless a caller EXPLICITLY
    opts in, and the default is the safe direction.
    """
    require(bool(out_path), "preservation_guard: out_path must be non-empty")
    if os.path.exists(out_path) and not allow_overwrite:
        raise ZContractError(
            f"preservation_guard: {out_path} already exists and allow_overwrite is False. "
            f"Z's build path is ADDITIVE: it must not overwrite an existing or archived artifact, "
            f"and it must not fall back to a default output path. Name a new path, or pass "
            f"allow_overwrite=True deliberately.")


# =============================== THE INTERCEPTION POINT (wiring) ===============================
# ⚠ WHY THIS SECTION EXISTS. Rev. 1 of this module was BLOCKED on review, and the ground was not the
# classifiers -- they were verified correct on all three of F3's cohorts -- but that NOTHING
# IMPORTED THEM. Measured: zero importers outside this file and its test, so `z_statistics.s_proj`
# still ran `require(np.all(q >= 0))` then `require(np.all(base > 0))` and graded, exactly as F3
# measured.
#
# A CORRECT HANDLER PROVES NOTHING ABOUT WHETHER ANYTHING ROUTES TO IT. The defect was the absent
# interception point, not the guard. `evaluate_a7` IS that point, and importing `z_statistics` below
# is what makes this module a consumer rather than a library nobody calls.
import z_statistics as _zs                                            # noqa: E402  (the wiring)


def evaluate_a7(cov_by_offset, projection_M, *, declared_K, c_scale, kappa,
                extra_functionals=(), declared_exclusions=(), declared_support=None,
                observed_support=None, baseline_key=0):
    """THE ONLY SANCTIONED ROUTE TO AN A-7 VERDICT. Guards first, `s_proj` last.

    Order is load-bearing and is the reverse of what a convenience wrapper would do: every refusal
    is evaluated BEFORE the statistic, because `s_proj`'s own `require`s raise messages that blame
    the OPERAND (*"C is not PSD on these u"*) when the defect is the FUNCTIONAL DECLARATION --
    F3's mislabelling finding. Reaching `s_proj` at all means every declaration was accepted.

    ⚠ DISCLOSED RESIDUE, measured rather than assumed: this does NOT retrofit
    `z_statistics.s_proj`. A direct `s_proj` call remains unguarded and grades a round-off-positive
    baseline exactly as before -- `TestTheResidueIsReal` DEMONSTRATES that rather than asserting it.
    It is sufficient for A-7 because `s_proj` has NO production callers (measured: 17 in this
    campaign's probe, 1 in `test_z_validator`), so the criterion's entry point is the only route
    needing the guard. If `s_proj` ever acquires a production caller this residue becomes live and
    the guard must move into it.

    ⚠ AND ONE BEHAVIOUR TO DOCUMENT AS INTENDED RATHER THAN DISCOVER LATER: while `kappa` is
    undeclared, a HEALTHY baseline also returns `KAPPA_UNDECLARED`. Fail-closed in the strong
    sense -- **A-7 cannot grade anything at all until `kappa` is declared**, which is correct under
    Joseph's *"do not invent an unapproved numerical kappa"* and makes the 1% criterion unevaluable
    until `kappa` exists. Whose act that declaration is has not been decided.
    """
    K = declared_population(declared_K, "evaluate_a7 caller")
    require(set(cov_by_offset) == set(K),
            f"members supplied {sorted(cov_by_offset)} != declared K {list(K)}; a population that "
            f"is not the declared one is INCONCLUSIVE / WRONG FOOTING, not a result")

    # ⚠ ARM 1 IS A PREDICATE ABOUT A PROJECTION MAP, NOT ABOUT A FUNCTIONAL SET, and rev. 2 of this
    # function conflated them -- caught by smoke-testing it, not by review. Arm 1 requires EVERY
    # reported source bin to land in some destination row, which is true of a complete map `M` and
    # FALSE of `U` by construction: `U = M's rows + the all-ones total-rate functional`, and
    # all-ones is NOT a row of `M`. Applied to `U` as a whole, arm 1 fired on a legitimate
    # declaration (37 of 40 source bins "unreached" for a 3-functional set).
    # So the arms run on `projection_M`, and `U` is assembled afterwards for the statistic.
    M = np.atleast_2d(np.asarray(projection_M, float))
    rep_support = require_projection_support(M, declared_exclusions, where="A-7 projection map")
    extras = np.asarray(extra_functionals, float)
    U = M if extras.size == 0 else np.vstack([M, np.atleast_2d(extras)])
    require(U.shape[1] == M.shape[1],
            f"extra functionals have width {U.shape[1]} != the map's {M.shape[1]}")

    if declared_support is not None or observed_support is not None:
        require(declared_support is not None and observed_support is not None,
                "support checking needs BOTH declared_support and observed_support")
        sup = classify_support_change(declared_support, observed_support)
        if sup["state"] != "RESOLVED":
            return {"state": sup["state"], "routed_to": A7_TERMINAL_ROUTING[sup["state"]],
                    "detail": sup, "s_proj": None}

    C0 = np.asarray(cov_by_offset[baseline_key], float)
    q0 = np.einsum("ij,jk,ik->i", U, C0, U)
    deg = classify_baseline_degeneracy(q0, c_scale=c_scale, kappa=kappa)
    if deg["state"] != "RESOLVED":
        return {"state": deg["state"], "routed_to": A7_TERMINAL_ROUTING[deg["state"]],
                "detail": deg, "s_proj": None}

    out = _zs.s_proj(cov_by_offset, U, baseline_key=baseline_key)
    return {"state": "GRADED", "routed_to": "A-7's numerical comparison against the proposed 1%",
            "detail": {"support": rep_support, "degeneracy": deg}, "s_proj": out}
