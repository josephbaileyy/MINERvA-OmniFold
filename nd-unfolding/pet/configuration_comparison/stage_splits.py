"""Assign every event to tuning, pilot or final, once and stably.

`frozen_design.SPLITS` requires the three stages to be disjoint, assigned "by a
hash of the event identity (source, run, subrun, gate, occurrence), so the same
event lands in the same split for BOTH arms and across reruns". Nothing
implemented it, so all three stages trained on the same events: the learning
rate would have been chosen on the data the effect is measured on, and the
pilot's variance -- which sizes the final -- would have been in-sample.

WHY IDENTITY AND NOT ROW NUMBER. Hashing the dump row index is stable across
arms and reruns too, and it is one line shorter. It is not stable across a
REGENERATED dump: the same event at a different row would change stage, and
nothing would report that, because the fractions would still come out right.
The identity is a property of the event; the row number is a property of the
file it happens to sit in.

WHY A HASH AND NOT A SHUFFLE. A seeded permutation of N rows gives exact
fractions but depends on N. Add one event to the dump and every assignment
moves. A per-event hash is independent of the population, so the split of the
events that were already there does not move when the dump grows -- at the cost
of fractions that are only exact in expectation, which is reported.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

import numpy as np

import frozen_design as fd

STAGES = ("tuning", "pilot", "final")


def _fractions() -> dict[str, float]:
    frac = {k: float(v) for k, v in fd.SPLITS["fractions"].items()}
    missing = [s for s in STAGES if s not in frac]
    if missing:
        raise ValueError(f"SPLITS has no fraction for {missing}")
    total = sum(frac[s] for s in STAGES)
    if abs(total - 1.0) > 1e-12:
        raise ValueError(
            f"the stage fractions sum to {total}, not 1. A partition whose "
            "parts do not cover the population is not a partition")
    return frac


def uniform_hash(identity: np.ndarray, seed: int) -> np.ndarray:
    """A stable uniform [0,1) per event, from its identity and the split seed.

    blake2b over the identity's raw bytes with the seed as a salt-like prefix.
    Python's own `hash` is salted per process and would give a different split
    every run; `hash()` on a tuple of ints would also be stable only within one
    interpreter version.
    """
    rows = np.ascontiguousarray(np.asarray(identity, dtype=np.int64))
    if rows.ndim != 2:
        raise ValueError(f"identity must be 2-D (events, fields), got {rows.shape}")
    prefix = int(seed).to_bytes(8, "little", signed=True)
    width = rows.shape[1] * 8
    raw = rows.tobytes()
    out = np.empty(rows.shape[0], dtype=np.float64)
    for i in range(rows.shape[0]):
        digest = hashlib.blake2b(prefix + raw[i * width:(i + 1) * width],
                                 digest_size=8).digest()
        out[i] = int.from_bytes(digest, "little") / float(1 << 64)
    return out


def assign(identity: np.ndarray, seed: int | None = None) -> np.ndarray:
    """Stage label per event. Disjoint and covering by construction."""
    seed = int(fd.SPLITS["split_seed"]) if seed is None else int(seed)
    frac = _fractions()
    u = uniform_hash(identity, seed)
    edges = np.cumsum([frac[s] for s in STAGES])
    labels = np.empty(u.shape[0], dtype="<U8")
    labels[:] = STAGES[-1]
    labels[u < edges[1]] = STAGES[1]
    labels[u < edges[0]] = STAGES[0]
    return labels


def rows_for_stage(identity: np.ndarray, stage: str,
                   seed: int | None = None) -> np.ndarray:
    """Positions of the events assigned to `stage`."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected one of {STAGES}")
    return np.flatnonzero(assign(identity, seed) == stage)


def census(identity: np.ndarray, seed: int | None = None) -> dict[str, Any]:
    """What the split actually produced, against what it intended."""
    labels = assign(identity, seed)
    frac = _fractions()
    n = int(labels.size)
    got = {s: int((labels == s).sum()) for s in STAGES}
    return {
        "rows": n,
        "counts": got,
        "fractions_intended": frac,
        "fractions_observed": {s: (got[s] / n if n else 0.0) for s in STAGES},
        "disjoint": True,
        "covering": sum(got.values()) == n,
        "seed": int(fd.SPLITS["split_seed"]) if seed is None else int(seed),
        "note": ("fractions are exact in expectation, not per draw: the hash is "
                 "per event so the assignment does not move when the dump grows"),
    }


def usable_half_size(identity: np.ndarray, stage: str,
                     seed: int | None = None) -> int:
    """The largest half that fits twice inside this stage.

    The closure needs TWO disjoint halves inside whichever events the stage
    owns. With the frozen 0.20/0.20/0.60 fractions the stages can support
    different half sizes, and the pilot's is the one that binds: the pilot
    sizes the final, and a pilot whose halves are smaller than the final's
    OVERSTATES the variance, which sizes the final conservatively rather than
    optimistically. That direction is the safe one and it is stated rather
    than discovered.
    """
    return int(rows_for_stage(identity, stage, seed).size // 2)
