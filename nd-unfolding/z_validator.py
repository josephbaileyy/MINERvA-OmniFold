#!/usr/bin/env python3
"""Z's validator structure, declared-leg handling and outcome branches. SPEC §3.2, §3.3, §3.7b.

THE CONSTRAINT THIS MODULE IS BUILT AROUND
------------------------------------------
Joseph, 2026-09-07: *"Missing or unapproved acceptance boundaries must produce an explicit
non-passing result. Do not choose provisional numerical defaults that could grade a production
artifact."*

`assess()` never returns MET when any declared leg's boundary is withheld. It does not return a
boolean, and there is no code path that supplies a number for a withheld boundary -- asking for one
raises `BoundaryWithheld` from `z_contract`, and this module lets that outcome propagate into the
result as a REJECT rather than catching it into a pass.

An unassessable run is a REJECT, NOT A FOURTH GRADE TOKEN. §3.3 condition 4c already covers it:
*"the run proceeds against a fixed-seed null bound or a (cause 3, Z) outcome rule that §3.6 still
lists as incomplete"* is a reject-Z condition. So a withheld boundary produces `assessable=False`
with `4c` in `reject_conditions`, and `branch is None`. `CRITERIA` §0's three-token vocabulary
(`MET` / `OPEN` / `UNRESOLVED`) is NOT extended by this module, and no grade token is emitted here
at all -- grading a cell is a separate act by a lane that did not draft these criteria (`BEN-381`).

THE LEG SET (§3.7b item 5, restated in rev. 16)
-----------------------------------------------
Rev. 7-15 hardcoded the pair `{s_agg, s_med}`, so adopting any third binding leg would have left a
MET branch that ignored it -- values right, scope wrong, and a review reading the numbers would
pass it. The branches below are written over a DECLARED LEG SET `L`, so a third leg binds without a
further edit here.

Each leg declares its class, `aggregate` or `per-bin`. Those two are `R4`'s reporting vocabulary and
are not extended: a correlation-sensitive leg (§3.7d), if ever adopted, must declare which of the
two it REPORTS AS, and that declaration is the adopter's, not this module's. With `|L| > 2` a label
loses information, so the receipt carries the exact failing subset `F` by name and the label is
DERIVED from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from z_contract import BoundaryWithheld, ZContractError, boundary, require

LEG_CLASSES = ("aggregate", "per-bin")

BRANCH_LABELS = {
    1: "INCONCLUSIVE / WRONG FOOTING",
    2: "INCONCLUSIVE / VACUOUS BASELINE VARIATION",
    3: "MET",
    4: "NOT MET - AGGREGATE",
    5: "NOT MET - PER-BIN",
    6: "NOT MET - MIXED",
}


@dataclass(frozen=True)
class Leg:
    """One binding leg of the cause-3 outcome rule.

    `boundary_key` names an entry in `z_contract.Z_BOUNDARIES`. The leg does not hold a number; it
    holds the NAME of one, so a withheld boundary is discovered at assessment time and cannot be
    baked in at declaration time.
    """

    name: str
    klass: str
    boundary_key: str
    statistic_key: str

    def __post_init__(self):
        if self.klass not in LEG_CLASSES:
            raise ZContractError(
                f"leg {self.name!r}: class {self.klass!r} is not one of {LEG_CLASSES}. A "
                f"correlation-sensitive leg must declare which of the two it reports as; this "
                f"module does not invent a third class and R4's vocabulary is not extended.")
        boundary(self.boundary_key)   # fail fast on an unknown boundary name


@dataclass
class LegSet:
    """`L`, predeclared in full before the first task."""

    legs: tuple = ()
    predeclared_at: Optional[str] = None

    def __post_init__(self):
        self.legs = tuple(self.legs)
        require(len(self.legs) > 0, "leg set: L is empty; a criterion with no legs grades nothing")
        names = [lg.name for lg in self.legs]
        require(len(set(names)) == len(names), f"leg set: duplicate leg names in {names}")

    def describe(self) -> dict:
        return {"predeclared_at": self.predeclared_at,
                "legs": [{"name": lg.name, "class": lg.klass, "boundary": lg.boundary_key,
                          "statistic": lg.statistic_key,
                          "boundary_status": boundary(lg.boundary_key).describe()}
                         for lg in self.legs]}


@dataclass
class Validity:
    """Branch 1 and 2 preconditions, supplied by the producer's own recorded operands.

    Defaults are the SAFE direction: absent evidence is a failure, never a pass. `footing_ok=False`
    by default means a caller who forgets to set it gets branch 1, not MET.
    """

    footing_ok: bool = False
    digests_agree: bool = False
    partition_agrees: bool = False
    identities_pass: bool = False
    cv_held_fixed: bool = False
    offsets_match_K: bool = False
    offset_declared_nonzero: bool = False
    product_digests_distinct: bool = False
    all_members_finite: bool = False
    notes: dict = field(default_factory=dict)

    def branch1_failures(self):
        return [k for k in ("footing_ok", "digests_agree", "partition_agrees",
                            "identities_pass", "cv_held_fixed") if not getattr(self, k)]

    def branch2_failures(self):
        return [k for k in ("offsets_match_K", "offset_declared_nonzero",
                            "product_digests_distinct", "all_members_finite")
                if not getattr(self, k)]


@dataclass
class Outcome:
    assessable: bool
    branch: Optional[int]
    branch_label: Optional[str]
    failing_legs: tuple = ()
    reject_conditions: tuple = ()
    leg_results: dict = field(default_factory=dict)
    validity: dict = field(default_factory=dict)
    scope_statement: Optional[str] = None

    @property
    def is_met(self) -> bool:
        return self.assessable and self.branch == 3

    def describe(self) -> dict:
        return {"assessable": self.assessable, "branch": self.branch,
                "branch_label": self.branch_label, "failing_legs": list(self.failing_legs),
                "reject_conditions": list(self.reject_conditions),
                "leg_results": self.leg_results, "validity": self.validity,
                "scope_statement": self.scope_statement}


# The narrowing that must travel WITH the grade, not sit in a specification the grader may not open
# (§3.7d answer (a)). Emitted whenever `L` contains no correlation-sensitive leg.
_DIAGONAL_ONLY_SCOPE = (
    "A MET result on (cause 3, Z) under this leg set states that the declared aggregate and "
    "per-bin summaries did not exceed their declared movement limits. It is NOT evidence that "
    "C_Z's correlation structure is stable, and it does NOT license the assembled covariance for "
    "marginalization, projection, coverage validation or any other off-diagonal-sensitive use.")


def _classify(failing):
    classes = {lg.klass for lg in failing}
    if not classes:
        return 3
    if classes == {"aggregate"}:
        return 4
    if classes == {"per-bin"}:
        return 5
    return 6


def assess(leg_set: LegSet, statistics: dict, validity: Validity,
           correlation_leg_present: bool = False) -> Outcome:
    """Evaluate `L` against the measured statistics. Validity dominates every numerical branch.

    `statistics` maps each leg's `statistic_key` to its measured value.
    """
    require(isinstance(leg_set, LegSet), "assess: leg_set must be a LegSet")
    v1 = validity.branch1_failures()
    v2 = validity.branch2_failures()
    vdesc = {"branch1_failures": v1, "branch2_failures": v2, "notes": dict(validity.notes)}

    if v1:
        return Outcome(assessable=True, branch=1, branch_label=BRANCH_LABELS[1],
                       validity=vdesc, reject_conditions=())
    if v2:
        # A zero spread here is evidence the knob never reached the estimator, NOT a favourable
        # result. That is the execution falsifier and it must never read as MET.
        return Outcome(assessable=True, branch=2, branch_label=BRANCH_LABELS[2],
                       validity=vdesc, reject_conditions=())

    # ---- boundaries, and this is where a withheld one stops everything -----------------------
    leg_results, withheld, failing = {}, [], []
    for lg in leg_set.legs:
        b = boundary(lg.boundary_key)
        entry = {"class": lg.klass, "boundary": b.describe()}
        if lg.statistic_key not in statistics:
            raise ZContractError(
                f"assess: leg {lg.name!r} needs statistic {lg.statistic_key!r}, which was not "
                f"supplied. A missing statistic is not a passing leg.")
        stat = float(statistics[lg.statistic_key])
        entry["statistic"] = stat
        try:
            limit = b.value
        except BoundaryWithheld as exc:
            entry["verdict"] = "NOT ASSESSABLE"
            entry["reason"] = str(exc)
            withheld.append(lg.name)
            leg_results[lg.name] = entry
            continue
        entry["limit"] = limit
        passed = stat <= limit          # written <=; equality is favourable (§3.7b item 4)
        entry["verdict"] = "within limit" if passed else "exceeds limit"
        if not passed:
            failing.append(lg)
        leg_results[lg.name] = entry

    if withheld:
        return Outcome(
            assessable=False, branch=None, branch_label=None,
            failing_legs=tuple(sorted(withheld)),
            reject_conditions=("4c",),
            leg_results=leg_results, validity=vdesc,
            scope_statement=None if correlation_leg_present else _DIAGONAL_ONLY_SCOPE)

    branch = _classify(failing)
    return Outcome(assessable=True, branch=branch, branch_label=BRANCH_LABELS[branch],
                   failing_legs=tuple(sorted(lg.name for lg in failing)),
                   reject_conditions=(), leg_results=leg_results, validity=vdesc,
                   scope_statement=None if correlation_leg_present else _DIAGONAL_ONLY_SCOPE)


# ------------------------------------------------------------------ the null's own assessment --
def assess_null(r_null: float, boundary_key: str = "null_epsilon") -> dict:
    """§3.7a. Report `r_null` and refuse to grade it while `epsilon` is withheld.

    The `min(achievable, acceptable)` construction was withdrawn in rev. 19: it used a feasibility
    floor as an UPPER bound where §3.6a says such a floor bounds `epsilon` from BELOW. The
    replacement is an operating-error bound `B` with stated assumptions and confidence, an
    independently justified scientific cap `S`, the precondition `B <= S`, and `epsilon` argued
    within `[B, S]` -- endpoints included, when justified. Neither `B` nor `S` exists, so there is
    nothing to compare against and this function says so rather than inventing a comparison.
    """
    b = boundary(boundary_key)
    out = {"r_null": float(r_null), "boundary": b.describe()}
    if not b.is_declared:
        out.update({"assessable": False, "verdict": "NOT ASSESSABLE",
                    "reject_conditions": ["4c", "11"],
                    "reason": "the scale-relative null bound is not derived; §3.3 condition 4c "
                              "makes proceeding against it a reject condition"})
        return out
    out.update({"assessable": True,
                "verdict": "within bound" if float(r_null) <= b.value else "exceeds bound",
                "limit": b.value, "reject_conditions": []})
    return out
