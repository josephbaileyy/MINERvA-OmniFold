"""Check a source read against the authorization that permits it, not against a superset.

**Why this exists, measured 2026-09-18.** `characterize_source_multiplicity.py` builds the
branch list it will read and then asserts that list is a subset of
`typed_descriptor_source_smoke.REQUIRED_BRANCHES`. That set was cleared for a fixed-source
15-entry smoke and contains blob positions, prong four-vectors, photon dE/dx and the
per-subdetector energy blocks. **A1 authorized 19 branches** -- event keys, the six
`cluster_*` vectors with their counts, `MasterAnaDev_BlobTotalE_sz`, `n_prongs`,
`gamma1_E`, `gamma2_E` -- i.e. *counts only* for blobs and prongs.

So the guard is a superset of the authorization. The read that ran was inside A1, but the
check could not have caught it leaving: adding `MasterAnaDev_BlobX` to the scope list
would satisfy the guard and exceed the authorization silently. A filter has to be tested
in the direction it acts, and that one cannot fire.

This module enforces the authorization itself. It also refuses the mirror-image error:
an authorization that lists branches nothing reads is reported, because a permission
nobody exercises is usually a sign the list was copied rather than derived.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

# A1, ratified by Joseph 2026-09-18. Transcribed from the emitted receipt's
# `branches_read`, which is the record of what was actually permitted and read --
# not from the code's own scope list, which is the thing being checked.
A1_AUTHORIZED_BRANCHES: tuple[str, ...] = (
    "ev_run", "ev_subrun", "ev_gate",
    "cluster_energy", "cluster_pos", "cluster_z", "cluster_view", "cluster_time",
    "cluster_isMuontrack",
    "cluster_energy_sz", "cluster_pos_sz", "cluster_z_sz", "cluster_view_sz",
    "cluster_time_sz", "cluster_isMuontrack_sz",
    "MasterAnaDev_BlobTotalE_sz",
    "n_prongs",
    "gamma1_E", "gamma2_E",
)

A1_SCOPE_SENTENCE = (
    "counts and cluster energy only; no positions, timing, truth, weights, or muon "
    "kinematics. A fixture input, not an analysis product."
)


class AuthorizationError(Exception):
    """Raised when a read exceeds its authorization. Never a warning."""


@dataclass(frozen=True)
class ScopeReport:
    """The comparison between what is authorized and what would be read."""

    authorized: tuple[str, ...]
    requested: tuple[str, ...]
    exceeding: tuple[str, ...]
    unexercised: tuple[str, ...]

    @property
    def within_authorization(self) -> bool:
        return not self.exceeding


def compare_scope(
    requested: Iterable[str],
    authorized: Iterable[str] = A1_AUTHORIZED_BRANCHES,
) -> ScopeReport:
    """Report branches outside the authorization, and authorized ones left unread."""
    req = tuple(dict.fromkeys(requested))
    auth = tuple(dict.fromkeys(authorized))
    if not auth:
        raise AuthorizationError("empty authorization: nothing is permitted")
    return ScopeReport(
        authorized=auth,
        requested=req,
        exceeding=tuple(sorted(set(req) - set(auth))),
        unexercised=tuple(sorted(set(auth) - set(req))),
    )


def require_within_authorization(
    requested: Iterable[str],
    authorized: Iterable[str] = A1_AUTHORIZED_BRANCHES,
    *,
    label: str = "source read",
) -> ScopeReport:
    """Return the report, or raise if the read exceeds the authorization."""
    report = compare_scope(requested, authorized)
    if not report.within_authorization:
        raise AuthorizationError(
            f"{label} requests {len(report.exceeding)} branch(es) outside its "
            f"authorization: {list(report.exceeding)}. Reading them needs a new "
            "authorization naming the branches, the entry count and what is emitted."
        )
    return report


def typed_object_gap(
    typed_branches: Iterable[str],
    authorized: Iterable[str] = A1_AUTHORIZED_BRANCHES,
) -> dict[str, Any]:
    """Name exactly which typed-object branches a new authorization would have to cover.

    This is the honest form of "the typed fields are already authorized", which they are
    not: A1 covers their *counts*, not their values.
    """
    report = compare_scope(typed_branches, authorized)
    return {
        "already_authorized": sorted(set(report.requested) & set(report.authorized)),
        "needs_new_authorization": list(report.exceeding),
        "count_needing_authorization": len(report.exceeding),
        "a1_scope_sentence": A1_SCOPE_SENTENCE,
        "correction": (
            "An earlier draft of mine stated that every typed field was already inside "
            "the A1-authorized set. That was wrong: it is inside the fixed-source "
            "smoke's REQUIRED_BRANCHES, which is a different and broader clearance."
        ),
    }


def audit_guard(
    guard_reference_set: Iterable[str],
    authorized: Iterable[str] = A1_AUTHORIZED_BRANCHES,
) -> dict[str, Any]:
    """Report whether a guard's reference set is wider than the authorization.

    A guard checking membership of a superset cannot fail when a read leaves the
    authorization, which is the only direction that matters.
    """
    guard = tuple(dict.fromkeys(guard_reference_set))
    auth = tuple(dict.fromkeys(authorized))
    wider_by = sorted(set(guard) - set(auth))
    return {
        "guard_set_size": len(guard),
        "authorization_size": len(auth),
        "guard_is_wider_than_authorization": bool(wider_by),
        "branches_the_guard_would_permit_but_a1_does_not": wider_by,
        "consequence": (
            "The guard cannot fire on an authorization overrun. It is a schema check, "
            "not a permission check, and must not be cited as the latter."
        ) if wider_by else "The guard is no wider than the authorization.",
    }
