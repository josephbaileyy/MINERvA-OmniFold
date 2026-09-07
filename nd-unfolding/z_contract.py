#!/usr/bin/env python3
"""Z's contract constants and its ACCEPTANCE BOUNDARY REGISTRY.

Baseline: `SPEC-20260906-complete-scalar5d-successor-Z.md` at `10c24678`, accepted by Joseph
2026-09-07 as the implementation baseline with "unresolved scientific acceptance criteria expressly
withheld".

THE ONE RULE THIS MODULE EXISTS TO ENFORCE
------------------------------------------
Joseph, 2026-09-07: *"Missing or unapproved acceptance boundaries must produce an explicit
non-passing result. Do not choose provisional numerical defaults that could grade a production
artifact."*

So a boundary here is not a float. It is a `Boundary`, which is either DECLARED -- carrying the
value AND the record that approved it -- or WITHHELD, carrying the reason. There is deliberately no
constructor that produces a value without a provenance string, and no default anywhere that a
caller can fall through to. `Z_BOUNDARIES` ships with every scientific boundary WITHHELD, and
`tests/test_z_contract.py` asserts that at import time, so the day one is declared is a day a test
changes and a reviewer sees it.

Why that shape rather than `None` and a check: a `None` default is one forgotten `if` away from
grading a production artifact with a number nobody approved. `Boundary.value` RAISES on a withheld
boundary, so the failure is at the point of use and cannot be reached by accident.

WHAT IS AND IS NOT WITHHELD
---------------------------
Withheld (the spec's §3.7a/§3.7b/§3.7d, all still with Joseph):
  * `null_epsilon`   -- §3.7a. `n_iters * n_rep * eps` was WITHDRAWN in rev. 17: a summation bound
                        over a computation that is not a summation. Needs `B <= S` and an `epsilon`
                        argued within `[B, S]`.
  * `cause3_agg`     -- §3.7b. The format-derived `0.0861%` was withdrawn in rev. 16.
  * `cause3_med`     -- §3.7b. Likewise `0.0374%`; and the per-bin leg also needs a coverage
                        fraction, not just a tolerance (`D2`).
  * `cause3_corr`    -- §3.7d. No correlation leg is adopted and none has a boundary.

NOT withheld, because they are not scientific acceptance criteria -- they are structural identities
whose tolerance is arithmetic, and the spec fixes them:
  * `IDENTITY_RTOL`  -- §3.3 condition 2's "outside relative 1e-9".
  * `G_FLOOR`        -- §1.3a property: `g >= 1` exactly, by construction.

IMPORTED, NEVER RETYPED (§1.2). A retyped band list is a second implementation of a predicate.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Same rooted-insert idiom as `unified_throw_cov_5d.py:39-42`, and the same reason (OI-136): a
# hardcoded root decides the executing tree before any guard starts. No absolute fallback.
_REPO = str(Path(__file__).resolve().parents[1])
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import p4_lib                      # noqa: E402
import adopt_unified_5d as _adopt  # noqa: E402
import uq_math                     # noqa: E402


# --------------------------------------------------------------------------- band partition ----
# §1.3a's V / R / A. Imported from the modules that own them; `Z_R_BANDS` is DERIVED as the
# remainder rather than listed, so it cannot drift from the two that are imported.
VERT_BANDS = tuple(_adopt.VERT_BANDS)       # V, 13 -- inflated through D_Z
LATERAL_BANDS = tuple(p4_lib.BANDS)         # A, 5  -- enter as L_b, uninflated
N_VERT = len(VERT_BANDS)
N_LATERAL = len(LATERAL_BANDS)
N_BANDS_TOTAL = 45                          # §1.3a: |V| + |R| + |A|
N_RESIDUAL = N_BANDS_TOTAL - N_VERT - N_LATERAL   # R, 27 -- derived, never listed

F7_FLOOR_MULTIPLE = uq_math.F7_FLOOR_MULTIPLE     # imported; §3.7b: no role in cause 3

# The existing, VALIDATED reproduction path (`p4_lib:88-100`, `run_p4_unfold_std.sh:17-23`).
# Joseph 2026-09-07: "Preserve all existing non-Z defaults and validated reproduction paths."
# Z imports these to REPORT against; it does NOT adopt them as its own boundary -- they were
# declared for the standard-P4 chain, which is a different subject (see `z_reproducibility`).
P4_REPRO_RTOL_PER_BIN = p4_lib.REPRO_RTOL_PER_BIN
P4_REPRO_RTOL_INTEGRAL = p4_lib.REPRO_RTOL_INTEGRAL

# Structural, not scientific. §3.3 condition 2.
IDENTITY_RTOL = 1e-9
G_FLOOR = 1.0


class ZContractError(RuntimeError):
    """Fail-closed gate failure. Never swallow. Mirrors `p4_lib.P4GateError`."""


class BoundaryWithheld(ZContractError):
    """Raised when a withheld acceptance boundary is USED.

    Distinct from `ZContractError` so a caller may report 'not assessable' without conflating it
    with 'assessed and failed'. Those are different outcomes and §3.2 keeps them apart.
    """


def require(cond, msg):
    """Fail-closed. Same idiom and the same reason as `p4_lib.require`."""
    if not cond:
        raise ZContractError(msg)


# ------------------------------------------------------------------------------- boundaries ----
@dataclass(frozen=True)
class Boundary:
    """An acceptance boundary that knows whether it may be used.

    Construct only via `declared()` or `withheld()`. `declared()` demands a provenance string
    because a number without the record that approved it is exactly what §3.6d's ordering rule and
    `BEN-381` forbid -- and because a reviewer must be able to find the approval from the code.
    """

    name: str
    _value: Optional[float]
    provenance: Optional[str]
    reason: Optional[str]

    def __post_init__(self):
        """⚠ THE INVARIANT LIVES HERE, NOT IN THE CLASSMETHODS.

        Review finding 1: the first version enforced provenance only inside `declared()`, so the
        dataclass's own generated constructor -- `Boundary("null_epsilon", 1.0, None, None)` --
        produced a usable boundary with no approval behind it. A guard on the polite path is not a
        guard.

        THE PATHS THIS COVERS, and what establishes each (round 3 corrected the list):

          * `Boundary(...)`, `declared()`, `withheld()` -- `__post_init__` is called by the
            generated `__init__`.
          * `dataclasses.replace()` -- calls `__init__`, so likewise.
          * `pickle.loads()` -- **NOT** by `__post_init__`. Measured: a round trip through
            `pickle` restores state directly and never calls `__init__`, and a payload whose
            provenance had been blanked came back with `.value` usable. That is what `__setstate__`
            below is for. The earlier blanket claim that this method runs on "every construction
            path, including unpickling" was WRONG, and it was wrong in the direction that matters.
        """
        if not self.name or not str(self.name).strip():
            raise ZContractError("boundary: a name is required")
        if self._value is None:
            if not self.reason or not str(self.reason).strip():
                raise ZContractError(
                    f"boundary {self.name!r}: a withheld boundary requires a reason")
            if self.provenance:
                raise ZContractError(
                    f"boundary {self.name!r}: a withheld boundary must not carry provenance -- "
                    f"provenance is what makes a value citable, and there is no value")
        else:
            v = float(self._value)
            if v != v or abs(v) == float("inf"):
                raise ZContractError(
                    f"boundary {self.name!r}: value must be finite, got {self._value!r}")
            if not self.provenance or not str(self.provenance).strip():
                raise ZContractError(
                    f"boundary {self.name!r}: a declared boundary requires provenance naming the "
                    f"record that approved it. A number without an approval is not a criterion.")
            if self.reason:
                raise ZContractError(
                    f"boundary {self.name!r}: a declared boundary must not also carry a "
                    f"withholding reason -- one of the two states, never both")

    def __setstate__(self, state):
        """Re-run the invariant after deserialization, because `__post_init__` will not.

        Nothing in Z pickles a `Boundary` today -- receipts are JSON. This exists because the
        alternative on offer was to document the gap and leave it open, and a three-line hook that
        makes the docstring above TRUE is worth more than a caveat that has to be remembered. The
        state is restored through `object.__setattr__` since the dataclass is frozen.
        """
        for key, value in state.items():
            object.__setattr__(self, key, value)
        self.__post_init__()

    @classmethod
    def declared(cls, name: str, value: float, provenance: str) -> "Boundary":
        if value is None:
            raise ZContractError(
                f"boundary {name!r}: declared() needs a value; use withheld() to withhold one")
        return cls(name=name, _value=float(value), provenance=provenance, reason=None)

    @classmethod
    def withheld(cls, name: str, reason: str) -> "Boundary":
        return cls(name=name, _value=None, provenance=None, reason=reason)

    @property
    def is_declared(self) -> bool:
        return self._value is not None

    @property
    def value(self) -> float:
        """The boundary, or RAISE. There is no fallback and no default, by design."""
        if self._value is None:
            raise BoundaryWithheld(
                f"acceptance boundary {self.name!r} is WITHHELD and cannot grade anything: "
                f"{self.reason}")
        return self._value

    def describe(self) -> dict:
        """Receipt-shaped, and safe to call on a withheld boundary."""
        return {
            "name": self.name,
            "status": "DECLARED" if self.is_declared else "WITHHELD",
            "value": self._value,
            "provenance": self.provenance,
            "reason": self.reason,
        }


# Every scientific acceptance boundary Z needs, and every one of them is withheld at this baseline.
# Joseph accepted the baseline "with unresolved scientific acceptance criteria expressly withheld",
# so this dict IS that withholding, expressed where the code would otherwise reach for a number.
Z_BOUNDARIES = {
    "null_epsilon": Boundary.withheld(
        "null_epsilon",
        "SPEC §3.7a: `n_iters * n_rep * eps` was withdrawn in rev. 17 -- a summation bound over a "
        "computation that is not a summation. Needs an operating-error bound B with stated "
        "assumptions and confidence, an independently justified scientific cap S, the precondition "
        "B <= S, and an epsilon argued within [B, S]. Neither B nor S is established."),
    "cause3_agg": Boundary.withheld(
        "cause3_agg",
        "SPEC §3.7b item 4: the format-derived 0.0861% was withdrawn in rev. 16. Macro formatting "
        "does not establish how much estimator-baseline sensitivity is scientifically acceptable, "
        "and the half-display-unit rule behind it is wrong in both directions. Needs a use-based "
        "justification."),
    "cause3_med": Boundary.withheld(
        "cause3_med",
        "SPEC §3.7b item 3 / D2: the printed median's precision is a new tolerance choice, not a "
        "consequence of that summary's formatting. Needs a justified per-bin tolerance AND a "
        "justified coverage fraction -- two numbers, and both are scientific."),
    "cause3_corr": Boundary.withheld(
        "cause3_corr",
        "SPEC §3.7d: no correlation-sensitive leg is adopted, and none has a boundary. Both "
        "adopted statistics are functions of the diagonal alone, so a MET result on them licenses "
        "nothing about C_Z's off-diagonal structure."),
}


def boundary(name: str) -> Boundary:
    """Look up a boundary. Unknown names FAIL rather than returning a permissive default."""
    if name not in Z_BOUNDARIES:
        raise ZContractError(
            f"unknown acceptance boundary {name!r}; known: {sorted(Z_BOUNDARIES)}")
    return Z_BOUNDARIES[name]


def declared_boundaries() -> dict:
    return {k: b for k, b in Z_BOUNDARIES.items() if b.is_declared}


def withheld_boundaries() -> dict:
    return {k: b for k, b in Z_BOUNDARIES.items() if not b.is_declared}


# ------------------------------------------------------------------------- the band partition --
def check_band_partition(vert, residual, lateral, band_inventory):
    """§1.3b gate 5 / §3.3 condition 3: V, R, A pairwise disjoint and EXHAUSTIVE.

    Takes the three sets as the PRODUCER built them and checks them against the imported
    constants. It does not rebuild them from those constants -- a check that constructs its own
    operand cannot disagree with the producer, which is the fixture-derived-from-the-rule failure
    this repository has already paid for.

    ⚠ `band_inventory` IS REQUIRED, and review finding 6 is why. The first version checked only
    disjointness, the two imported sets and a COUNT, so the correct `V` and `A` plus 27 INVENTED
    residual names passed -- 45 of them, all disjoint, none of them real. A count is not an
    inventory. Exhaustiveness is a claim about the support family's actual band set, so the actual
    set has to be supplied; there is no default, because a defaulted inventory would be the
    producer's own list and the check would agree with it by construction.
    """
    V, R, A = set(vert), set(residual), set(lateral)
    inv = set(band_inventory)
    require(inv, "band inventory is empty -- exhaustiveness cannot be checked against nothing")
    require(len(V) == len(list(vert)), "V contains duplicates")
    require(len(R) == len(list(residual)), "R contains duplicates")
    require(len(A) == len(list(lateral)), "A contains duplicates")
    require(not (V & R), f"V and R overlap: {sorted(V & R)}")
    require(not (V & A), f"V and A overlap: {sorted(V & A)}")
    require(not (R & A), f"R and A overlap: {sorted(R & A)}")
    require(V == set(VERT_BANDS),
            f"V is not adopt_unified_5d.VERT_BANDS: missing {sorted(set(VERT_BANDS) - V)}, "
            f"extra {sorted(V - set(VERT_BANDS))}")
    require(A == set(LATERAL_BANDS),
            f"A is not p4_lib.BANDS: missing {sorted(set(LATERAL_BANDS) - A)}, "
            f"extra {sorted(A - set(LATERAL_BANDS))}")
    union = V | R | A
    missing, invented = inv - union, union - inv
    require(not missing,
            f"partition is not exhaustive: {len(missing)} band(s) in the support-family inventory "
            f"are in no part -- {sorted(missing)[:6]}")
    require(not invented,
            f"partition contains {len(invented)} band(s) absent from the support-family "
            f"inventory -- {sorted(invented)[:6]}. A name that is not in the inventory is not a "
            f"band, however neatly it partitions")
    total = len(V) + len(R) + len(A)
    require(total == N_BANDS_TOTAL,
            f"V+R+A = {total}, expected {N_BANDS_TOTAL} ({N_VERT}+{N_RESIDUAL}+{N_LATERAL})")
    require(len(R) == N_RESIDUAL, f"|R| = {len(R)}, expected {N_RESIDUAL}")
    return {"n_vert": len(V), "n_residual": len(R), "n_lateral": len(A), "n_total": total,
            "n_inventory": len(inv), "exhaustive": True}
