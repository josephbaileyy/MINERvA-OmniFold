"""Characterize real per-event multiplicity and the truncated generic tail.

Authorized as A1 on 2026-09-18. This reads **counts, plus cluster energy**, and
nothing else: no positions, no timing, no truth, no weights, no muon kinematics
beyond the event keys used for provenance. It produces a fixture input, not an
analysis product, and it decides nothing.

Two design rules make the read auditable:

* Its branch set is asserted to be a **subset** of the already-authorized
  ``REQUIRED_BRANCHES``, so the read provably cannot exceed what the fixed-source
  smoke was cleared for. Sources are resolved through the same digest-pinned
  manifests and the same UUID check.
* The pre-truncation quantities it needs are exactly the ones production throws
  away, so it re-derives the selection -- non-muon clusters, energy-sorted
  descending -- rather than importing a function that returns the already-truncated
  block. A re-derivation can drift from the original, so every ``--crosscheck-every``
  entries it calls the production builder ``_build_p12`` and requires its own top-12
  to agree exactly. A disagreement is a hard failure, not a warning.

The energy share beyond the cap is a **proxy for how much the cap could matter**. It
is not evidence that the discarded clusters carry predictive information: energy and
predictive importance are different quantities, and nothing here measures the second.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

CAP = 12  # the production top-12-by-energy cap
DEFAULT_ENTRIES = 200_000
PHOTON_PRESENCE_THRESHOLD = 1.0e-5


def _install(checkout: Path) -> None:
    """Put the checkout's pet modules first."""
    root = checkout / "nd-unfolding" / "pet"
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    sys.path.insert(0, str(root))


def branch_scope(smoke: Any) -> tuple[str, ...]:
    """Return the counts-and-energy branch set, proven inside the authorized set."""
    scope = tuple(
        dict.fromkeys(
            smoke.EVENT_KEY_BRANCHES
            + smoke.GENERIC_VALUE_BRANCHES
            + smoke.GENERIC_COUNT_BRANCHES
            + ("MasterAnaDev_BlobTotalE_sz", "n_prongs", "gamma1_E", "gamma2_E")
        )
    )
    outside = sorted(set(scope) - set(smoke.REQUIRED_BRANCHES))
    if outside:
        raise ValueError(f"Branches outside the authorized set: {outside}")
    return scope


def retained_energies(energy: Any, is_muon: Any) -> np.ndarray:
    """Return non-muon cluster energies, sorted descending.

    Mirrors the production selection in ``_build_p12``: keep clusters whose
    ``cluster_isMuontrack`` flag is zero, then order by decreasing energy.
    """
    values = np.asarray(
        [float(e) for e, flag in zip(energy, is_muon) if int(flag) == 0],
        dtype=np.float64,
    )
    return values[np.argsort(-values, kind="stable")]


def tail_energy_share(sorted_energies: np.ndarray, cap: int = CAP) -> float | None:
    """Return the fraction of retained energy carried beyond the cap.

    ``None`` when the event has no retained energy at all, which is a different
    statement from a share of zero and must not be averaged in as one.
    """
    total = float(sorted_energies.sum())
    if not np.isfinite(total) or total <= 0.0:
        return None
    return float(sorted_energies[cap:].sum() / total)


def photon_count(gamma1_e: float, gamma2_e: float) -> tuple[int, int]:
    """Count photons present, and separately count non-finite presence energies.

    The fixed-source smoke *raises* on a non-finite ``gammaN_E`` because presence
    is then ambiguous (`typed_descriptor_source_smoke.py:869`). Aborting a
    200,000-entry characterization on one such event would be worse than useless,
    so this counts them instead and the receipt reports the total. Silently
    treating them as absent is the one option not taken.
    """
    present = 0
    nonfinite = 0
    for value in (gamma1_e, gamma2_e):
        if not np.isfinite(value):
            nonfinite += 1
        elif value > PHOTON_PRESENCE_THRESHOLD:
            present += 1
    return present, nonfinite


class Accumulator:
    """Collect count histograms and tail shares without storing per-event rows."""

    def __init__(self) -> None:
        self.generic_all: Counter[int] = Counter()
        self.generic_nonmuon: Counter[int] = Counter()
        self.blobs: Counter[int] = Counter()
        self.prongs: Counter[int] = Counter()
        self.photons: Counter[int] = Counter()
        self.tail_shares: list[float] = []
        self.events_with_no_energy = 0
        self.nonfinite_photon_energies = 0
        self.entries = 0

    def add(
        self,
        *,
        generic_all: int,
        generic_nonmuon: int,
        blobs: int,
        prongs: int,
        photons: int,
        nonfinite_photons: int,
        tail_share: float | None,
    ) -> None:
        """Record one event."""
        self.entries += 1
        self.nonfinite_photon_energies += nonfinite_photons
        self.generic_all[generic_all] += 1
        self.generic_nonmuon[generic_nonmuon] += 1
        self.blobs[blobs] += 1
        self.prongs[prongs] += 1
        self.photons[photons] += 1
        if tail_share is None:
            self.events_with_no_energy += 1
        else:
            self.tail_shares.append(tail_share)

    @staticmethod
    def _describe(counts: Counter[int]) -> dict[str, Any]:
        """Summarize one count distribution, keeping the full histogram."""
        total = sum(counts.values())
        if not total:
            return {"events": 0}
        values = np.repeat(
            np.fromiter(counts.keys(), dtype=np.int64),
            np.fromiter(counts.values(), dtype=np.int64),
        )
        return {
            "events": int(total),
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "min": int(values.min()),
            "max": int(values.max()),
            "fraction_at_or_above_cap": float((values >= CAP).mean()),
            "fraction_above_cap": float((values > CAP).mean()),
            "histogram": {str(k): int(v) for k, v in sorted(counts.items())},
        }

    def summary(self) -> dict[str, Any]:
        """Return the receipt body for one source."""
        shares = np.asarray(self.tail_shares, dtype=np.float64)
        tail: dict[str, Any] = {
            "events_with_retained_energy": int(shares.size),
            "events_with_no_retained_energy": self.events_with_no_energy,
        }
        if shares.size:
            tail.update(
                mean=float(shares.mean()),
                median=float(np.median(shares)),
                p90=float(np.quantile(shares, 0.90)),
                p99=float(np.quantile(shares, 0.99)),
                max=float(shares.max()),
                fraction_of_events_nonzero=float((shares > 0).mean()),
            )
        return {
            "entries_read": self.entries,
            "nonfinite_photon_presence_energies": self.nonfinite_photon_energies,
            "generic_clusters_all": self._describe(self.generic_all),
            "generic_clusters_nonmuon": self._describe(self.generic_nonmuon),
            "blobs": self._describe(self.blobs),
            "prongs": self._describe(self.prongs),
            "photons": self._describe(self.photons),
            "tail_energy_share_beyond_cap": tail,
        }


def read_source(
    smoke: Any, resolved: Any, scope: tuple[str, ...], entries: int, crosscheck: int
) -> dict[str, Any]:
    """Read one pinned source and accumulate its multiplicity summary."""
    import ROOT  # type: ignore[import-not-found]

    handle = ROOT.TFile.Open(resolved.path, "READ")
    if not handle or handle.IsZombie():
        raise OSError(f"Could not open source: {resolved.path}")
    try:
        uuid = str(handle.GetUUID().AsString())
        if uuid != resolved.spec.expected_uuid:
            raise ValueError(
                f"Source UUID {uuid} != pinned {resolved.spec.expected_uuid}"
            )
        tree = handle.Get(smoke.TREE_NAME)
        if tree is None:
            raise ValueError(f"Source has no {smoke.TREE_NAME!r} tree")
        missing = [name for name in scope if not tree.GetBranch(name)]
        if missing:
            raise ValueError(f"Source is missing branches: {missing}")
        tree.SetBranchStatus("*", 0)
        for name in scope:
            tree.SetBranchStatus(name, 1)
        available = int(tree.GetEntries())
        limit = min(entries, available)
        accumulator = Accumulator()
        crosschecks = 0
        for entry in range(limit):
            if int(tree.GetEntry(entry)) <= 0:
                raise OSError(f"Entry {entry} read zero bytes")
            energy = tree.cluster_energy
            is_muon = tree.cluster_isMuontrack
            declared = int(tree.cluster_energy_sz)
            if len(energy) != declared or len(is_muon) != declared:
                raise ValueError(f"Entry {entry}: cluster vectors disagree with _sz")
            ordered = retained_energies(energy, is_muon)
            photons, nonfinite = photon_count(
                float(tree.gamma1_E), float(tree.gamma2_E)
            )
            accumulator.add(
                generic_all=declared,
                generic_nonmuon=int(ordered.size),
                blobs=int(tree.MasterAnaDev_BlobTotalE_sz),
                prongs=int(tree.n_prongs),
                photons=photons,
                nonfinite_photons=nonfinite,
                tail_share=tail_energy_share(ordered),
            )
            if crosscheck and entry % crosscheck == 0:
                raw = {
                    name: (
                        int(getattr(tree, name))
                        if name.endswith("_sz")
                        else list(getattr(tree, name))
                    )
                    for name in smoke.GENERIC_VALUE_BRANCHES
                    + smoke.GENERIC_COUNT_BRANCHES
                }
                production = smoke._build_p12(raw)
                mine = np.zeros(CAP, dtype=np.float32)
                mine[: min(ordered.size, CAP)] = ordered[:CAP].astype(np.float32)
                if not np.array_equal(production[:, 0], mine):
                    raise ValueError(
                        f"Entry {entry}: re-derived ranking disagrees with _build_p12"
                    )
                crosschecks += 1
        summary = accumulator.summary()
        summary.update(
            role=resolved.spec.role,
            playlist=resolved.spec.playlist,
            basename=resolved.spec.expected_basename,
            source_uuid=uuid,
            manifest=resolved.spec.manifest_relative_path,
            manifest_sha256=resolved.manifest_sha256,
            entries_available=available,
            entries_requested=entries,
            production_crosschecks_passed=crosschecks,
        )
        return summary
    finally:
        handle.Close()


def main() -> None:
    """Characterize both pinned sources and write one receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--entries", type=int, default=DEFAULT_ENTRIES)
    parser.add_argument("--crosscheck-every", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _install(args.checkout)
    import typed_descriptor_source_smoke as smoke

    scope = branch_scope(smoke)
    sources = smoke.resolve_fixed_sources(args.checkout)
    receipt: dict[str, Any] = {
        "scope": (
            "counts and cluster energy only; no positions, timing, truth, weights, or "
            "muon kinematics. A fixture input, not an analysis product."
        ),
        "authorization": "A1, Joseph, 2026-09-18",
        "cap": CAP,
        "branches_read": list(scope),
        "branch_count": len(scope),
        "sources": [
            read_source(smoke, resolved, scope, args.entries, args.crosscheck_every)
            for resolved in sources
        ],
        "qualification": (
            "Tail energy share bounds how much the cap COULD matter. It does not "
            "establish that the discarded clusters carry predictive information; "
            "energy share and predictive importance are different quantities and only "
            "the first is measured here."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    for source in receipt["sources"]:
        nonmuon = source["generic_clusters_nonmuon"]
        tail = source["tail_energy_share_beyond_cap"]
        print(
            f"{source['role']:>4} {source['playlist']}: "
            f"{source['entries_read']} entries, non-muon clusters mean "
            f"{nonmuon['mean']:.2f} median {nonmuon['median']:.0f}, "
            f"{100 * nonmuon['fraction_above_cap']:.1f}% above the cap, "
            f"tail energy share median {tail.get('median', float('nan')):.4f} "
            f"mean {tail.get('mean', float('nan')):.4f}, "
            f"{source['production_crosschecks_passed']} crosschecks passed"
        )


if __name__ == "__main__":
    main()
