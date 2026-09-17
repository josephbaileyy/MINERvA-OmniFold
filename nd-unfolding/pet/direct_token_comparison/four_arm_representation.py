"""Arms, generic-cloud cap treatments, and bucketing for the four-arm experiment.

New module rather than an edit: every producer of the finished campaign
(`run_typed_token_comparison.py`, `typed_token_comparison.py`, `typed_descriptors.py`)
is hash-bound in ``amended-manifest.json``, so the frozen comparison stays verifiable
and this builds on top of it instead of inside it.

Three pieces, all of which the frozen campaign had no need for:

* **Cap treatments.** Production keeps the twelve highest-energy non-muon clusters and
  discards the rest (`typed_descriptor_source_smoke.py:_build_p12`). ``truncate_cloud``
  reproduces that; ``aggregate_cloud`` keeps eleven and spends the twelfth slot on a
  summary of the discarded tail -- summed energy, mean of the remaining channels, a
  distinct type code, and the **merged count**, which the upstream implementation
  discards. Both return the same shape, so arms A and D differ in content only and the
  contrast between them carries no cost difference.

* **Bucketing.** Grouping events by identical typed multiplicity makes every batch
  uniform and unpadded, which is the geometry the cross-device gate validated -- as
  opposed to the padded, variable-width geometry it failed. The partition is a function
  of the fixture alone, never of the arm, so no contrast can be contaminated by a
  batch-structure difference.

* **A width-set guard.** Removing padding does not by itself make a width validated:
  the frozen gate ran at one specific geometry and refuses every other. So the guard
  here takes the set of widths a gate run actually passed and refuses anything outside
  it. The experiment therefore cannot train at a width no gate has cleared.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

CAP = 12  # the production top-12-by-energy cap
# Ordinary cluster channels, then the two the aggregate token needs. Every arm carries
# the same width; only arm D ever makes the last two non-zero.
CLUSTER_CHANNELS = ("energy", "position", "z", "view", "time")
AGGREGATE_CHANNELS = ("is_aggregate", "merged_count")
CLOUD_WIDTH = len(CLUSTER_CHANNELS) + len(AGGREGATE_CHANNELS)


@dataclass(frozen=True)
class ArmSpec:
    """One arm: whether typed objects are visible, how routed, and the cap treatment."""

    name: str
    typed_enabled: bool
    routing: str
    cap_treatment: str

    def __post_init__(self) -> None:
        if self.routing not in ("pooled", "direct"):
            raise ValueError(f"{self.name}: routing must be pooled or direct")
        if self.cap_treatment not in ("truncate", "aggregate"):
            raise ValueError(f"{self.name}: cap treatment must be truncate or aggregate")
        if not self.typed_enabled and self.routing == "direct":
            # Individual routing of nothing is not a distinct representation, and
            # allowing it would let a fourth arm masquerade as a fifth.
            raise ValueError(f"{self.name}: direct routing needs typed objects enabled")


ARMS = (
    ArmSpec("A", typed_enabled=False, routing="pooled", cap_treatment="truncate"),
    ArmSpec("B", typed_enabled=True, routing="pooled", cap_treatment="truncate"),
    ArmSpec("C", typed_enabled=True, routing="direct", cap_treatment="truncate"),
    ArmSpec("D", typed_enabled=False, routing="pooled", cap_treatment="aggregate"),
)
ARMS_BY_NAME = {arm.name: arm for arm in ARMS}


def order_clusters(cloud: NDArray[Any]) -> NDArray[Any]:
    """Return one event's clusters ordered by decreasing energy.

    Matches the production ordering: ``np.argsort(-energy, kind="stable")``, so ties
    keep their original order rather than being permuted.
    """
    if cloud.ndim != 2 or cloud.shape[1] != CLOUD_WIDTH:
        raise ValueError(f"Cloud must be (n, {CLOUD_WIDTH}), got {cloud.shape}")
    return cloud[np.argsort(-cloud[:, 0], kind="stable")]


def truncate_cloud(cloud: NDArray[Any], cap: int = CAP) -> NDArray[Any]:
    """Keep the ``cap`` highest-energy clusters and discard the rest.

    This is the incumbent treatment. What it discards is discarded completely: the
    tail's energy, its multiplicity, and any function of it.
    """
    ordered = order_clusters(cloud)
    output = np.zeros((cap, CLOUD_WIDTH), dtype=np.float32)
    keep = min(len(ordered), cap)
    output[:keep] = ordered[:keep]
    return output


def aggregate_cloud(cloud: NDArray[Any], cap: int = CAP) -> NDArray[Any]:
    """Keep ``cap - 1`` clusters and summarize the tail into the final slot.

    The aggregate token carries the tail's **summed** energy, the **mean** of its
    remaining channels, a type code of 1, and the number merged. Energy is therefore
    conserved exactly while position, depth, view and timing survive only as an
    average -- the substitution the upstream implementation makes, plus the merged
    count it omits.

    With ``len(cloud) <= cap`` nothing is merged and the result is
    ``truncate_cloud``'s output: a cap that does not bind must not perturb the input.
    """
    ordered = order_clusters(cloud)
    if len(ordered) <= cap:
        output = np.zeros((cap, CLOUD_WIDTH), dtype=np.float32)
        output[: len(ordered)] = ordered
        return output
    head, tail = ordered[: cap - 1], ordered[cap - 1 :]
    output = np.zeros((cap, CLOUD_WIDTH), dtype=np.float32)
    output[: cap - 1] = head
    summary = np.zeros(CLOUD_WIDTH, dtype=np.float32)
    summary[0] = tail[:, 0].sum()
    summary[1 : len(CLUSTER_CHANNELS)] = tail[:, 1 : len(CLUSTER_CHANNELS)].mean(axis=0)
    summary[len(CLUSTER_CHANNELS)] = 1.0
    summary[len(CLUSTER_CHANNELS) + 1] = float(len(tail))
    output[cap - 1] = summary
    return output


def apply_cap(
    clouds: Sequence[NDArray[Any]], treatment: str, cap: int = CAP
) -> NDArray[Any]:
    """Apply one cap treatment to every event's cloud, returning a dense block."""
    if treatment == "truncate":
        handler = truncate_cloud
    elif treatment == "aggregate":
        handler = aggregate_cloud
    else:
        raise ValueError(f"Unknown cap treatment: {treatment}")
    return np.stack([handler(cloud, cap) for cloud in clouds]).astype(np.float32)


def discarded_energy_fraction(
    clouds: Sequence[NDArray[Any]], cap: int = CAP
) -> NDArray[Any]:
    """Return each event's fraction of cluster energy beyond the cap.

    ``nan`` for an event with no energy: that is not a fraction of zero and must not
    be averaged in as one.
    """
    fractions = []
    for cloud in clouds:
        ordered = order_clusters(cloud)
        total = float(ordered[:, 0].sum())
        fractions.append(
            float(ordered[cap:, 0].sum() / total) if total > 0 else float("nan")
        )
    return np.asarray(fractions, dtype=np.float64)


def typed_widths(inputs: Mapping[str, Any], rows: int, families: Iterable[str]) -> Any:
    """Return each row's per-family object count as a tuple key."""
    per_family = []
    for family in families:
        segment = np.asarray(inputs[f"{family}_segment_ids"])
        per_family.append(np.bincount(segment, minlength=rows)[:rows])
    return np.stack(per_family, axis=1)


def bucket_events(widths: NDArray[Any]) -> dict[tuple[int, ...], NDArray[Any]]:
    """Partition row indices by identical per-family width.

    A partition, not a filter: the union of the returned index arrays is every row
    exactly once. Nothing is dropped for having an inconvenient multiplicity.
    """
    buckets: dict[tuple[int, ...], list[int]] = {}
    for row, width in enumerate(widths):
        buckets.setdefault(tuple(int(value) for value in width), []).append(row)
    return {
        key: np.asarray(rows, dtype=np.int64) for key, rows in sorted(buckets.items())
    }


def batch_plan(
    buckets: Mapping[tuple[int, ...], NDArray[Any]], batch_size: int, seed: int
) -> list[tuple[tuple[int, ...], NDArray[Any]]]:
    """Return the shuffled batch sequence: every event once, uniform width per batch.

    Bucket order is shuffled so that multiplicity is not presented to the optimizer in
    a monotone sweep, which would make late training see only one geometry. The plan
    depends on the fixture and the seed alone -- never on the arm -- so every arm
    performs the same steps on the same events.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    rng = np.random.default_rng(seed)
    batches: list[tuple[tuple[int, ...], NDArray[Any]]] = []
    for key, rows in buckets.items():
        shuffled = rows[rng.permutation(len(rows))]
        for start in range(0, len(shuffled), batch_size):
            batches.append((key, np.sort(shuffled[start : start + batch_size])))
    order = rng.permutation(len(batches))
    return [batches[index] for index in order]


class WidthSetGuard:
    """Refuse any batch whose geometry no gate run has validated.

    The frozen guard pins one geometry and says so in its own error message: the GPU
    gate never validated a padded or variable-length batch. Bucketing removes the
    padding but does not validate a new *width*, so this guard carries the set of
    widths a gate run actually passed and refuses everything else. ``declared_disabled``
    is the one deliberate exemption, for the arms that show the model no typed objects
    at all, and it must be declared rather than inferred.
    """

    def __init__(
        self,
        validated_widths: Iterable[tuple[int, ...]],
        families: Sequence[str],
        *,
        declared_disabled: bool = False,
    ) -> None:
        self.validated = {tuple(int(v) for v in width) for width in validated_widths}
        if not self.validated and not declared_disabled:
            raise ValueError("No validated widths: nothing may train")
        self.families = tuple(families)
        self.declared_disabled = declared_disabled

    def check_batch(
        self, inputs: Mapping[str, Any], rows: int, *, label: str
    ) -> dict[str, Any]:
        """Require a uniform, unpadded, validated width, or a declared disabling."""
        measured: dict[str, Any] = {"declared_disabled": self.declared_disabled}
        widths: list[int] = []
        for family in self.families:
            token_mask = np.asarray(inputs[f"{family}_token_mask"])
            enabled = np.asarray(inputs[f"{family}_enabled"])
            declared = np.asarray(inputs[f"{family}_counts"])
            segment = np.asarray(inputs[f"{family}_segment_ids"])
            counts = np.bincount(segment, minlength=rows)[:rows]
            # Stated as two positive requirements rather than one negation, so
            # "some families disabled" cannot slip through either branch.
            if self.declared_disabled:
                if enabled.any():
                    raise ValueError(
                        f"{label}/{family}: declared disabled but some rows are enabled"
                    )
            elif not enabled.all():
                raise ValueError(
                    f"{label}/{family}: a disabled family is not covered unless declared"
                )
            if not token_mask.all():
                raise ValueError(f"{label}/{family}: token-level masking is not covered")
            if int(counts.min()) != int(counts.max()):
                raise ValueError(
                    f"{label}/{family}: widths {int(counts.min())}..."
                    f"{int(counts.max())} are not uniform; bucketing failed"
                )
            if not np.array_equal(declared, counts.astype(declared.dtype)):
                raise ValueError(f"{label}/{family}: declared counts disagree with slots")
            widths.append(int(counts.max()))
        width = tuple(widths)
        if not self.declared_disabled and width not in self.validated:
            raise ValueError(
                f"{label}: width {width} is not in the validated set "
                f"{sorted(self.validated)}; no gate run has cleared it"
            )
        measured.update(width=width, padded_positions=0, typed_tokens_per_row=sum(width))
        return measured


def verify_partition(
    buckets: Mapping[tuple[int, ...], NDArray[Any]], rows: int
) -> None:
    """Require the buckets to be a partition of ``range(rows)``."""
    seen = np.concatenate(list(buckets.values())) if buckets else np.zeros(0, np.int64)
    if len(seen) != rows or not np.array_equal(np.sort(seen), np.arange(rows)):
        raise ValueError(
            f"Buckets are not a partition of {rows} rows: {len(seen)} indices, "
            f"{len(np.unique(seen))} distinct"
        )


def verify_plan_covers_events(
    plan: Sequence[tuple[tuple[int, ...], NDArray[Any]]], rows: int
) -> None:
    """Require the batch plan to visit every event exactly once."""
    visited = (
        np.concatenate([batch for _, batch in plan]) if plan else np.zeros(0, np.int64)
    )
    if not np.array_equal(np.sort(visited), np.arange(rows)):
        raise ValueError(
            f"Batch plan visits {len(visited)} rows for {rows} events; "
            "an event was dropped or repeated"
        )


def verify_weights_preserved(
    plan: Sequence[tuple[tuple[int, ...], NDArray[Any]]], weights: NDArray[Any]
) -> None:
    """Require the multiset of per-event weights to survive bucketing exactly."""
    gathered = np.concatenate([weights[batch] for _, batch in plan])
    if not np.array_equal(np.sort(gathered), np.sort(weights)):
        raise ValueError("Bucketing changed the multiset of per-event weights")
