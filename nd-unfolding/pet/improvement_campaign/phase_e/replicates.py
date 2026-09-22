"""Replicate draws inside an event pool (PROTOCOL-20260922 section 3).

The pools are fixed by `pools/POOL_MANIFEST.json` and the per-inventory-row codes in `pools.npz`
(0=P, 1=F, 2=S, 3=T, 4=R, -1 excluded). This module turns a pool into replicate draws, each a
PRIOR sample and a PSEUDODATA sample, with three properties the protocol asks for:

* **Identity-keyed.** Every choice is a function of the event identity `(mc_run, mc_subrun,
  mc_nthEvtInFile)`, hashed with blake2b exactly as `stage_splits.uniform_hash` and the pool
  builder do, never of a row position or an RNG stream. The same pool gives the same draws on any
  machine, in any row order.
* **Disjoint prior and pseudodata** within a replicate, always.
* **Independent across replicates.** Two hashes are used:

  1. a FAMILY hash `u_F = H(identity; salt/pool/family)` ranks the pool. Replicate r owns the rank
     block `[r*m, (r+1)*m)`, `m = n_prior + n_pseudo`, so replicates of one family are disjoint
     random subsets of the pool -- independent event draws, not seed repetitions;
  2. a REPLICATE hash `u_r = H(identity; salt/pool/family/r)` -- the "second identity hash salted
     with the replicate id" -- orders the block; its first `n_prior` events are the prior, the
     remaining `n_pseudo` the pseudodata.

  A family that needs more events than the pool holds (`n_replicates * m > pool size`) cannot be
  disjoint. It must say so (`disjoint=False`); each replicate's block is then the `m`
  lowest-`u_r` events of the whole pool, replicates are independent random subsets that may
  SHARE events, and the pairwise overlap is measured and returned, never hidden.

An `exclude` mask (e.g. a common untouched evaluation population, protocol section 6) removes rows
before either hash is applied.

Nothing here reads event content: only identities, pool codes and row numbers. PET is diagnostic
method development; no real data is involved.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

SALT = "pet-improvement-20260922-replicates"
POOL_CODES = {"P": 0, "F": 1, "S": 2, "T": 3, "R": 4}


# ------------------------------------------------------------------------------------------- #
# Hashing (identical algorithm to configuration_comparison/stage_splits.uniform_hash; tested)
# ------------------------------------------------------------------------------------------- #
def seed_from_salt(salt: str) -> int:
    """Signed 64-bit seed from a salt string, as `pools/build_pools.pool_seed` derives its seed."""
    return int.from_bytes(hashlib.sha256(salt.encode()).digest()[:8], "little", signed=True)


def uniform_hash(identity: np.ndarray, seed: int) -> np.ndarray:
    """A stable uniform [0, 1) per event: blake2b(seed bytes + identity bytes), 8-byte digest.

    Byte-for-byte the algorithm of `stage_splits.uniform_hash` (which the pool assignment used),
    reimplemented here so this module imports nothing from the historical comparison.
    """
    rows = np.ascontiguousarray(np.asarray(identity, dtype=np.int64))
    if rows.ndim != 2:
        raise ValueError(f"identity must be 2-D (events, fields), got {rows.shape}")
    prefix = int(seed).to_bytes(8, "little", signed=True)
    width = rows.shape[1] * 8
    raw = rows.tobytes()
    blake = hashlib.blake2b
    ints = np.fromiter(
        (int.from_bytes(blake(prefix + raw[i:i + width], digest_size=8).digest(), "little")
         for i in range(0, len(raw), width)),
        dtype=np.uint64, count=rows.shape[0])
    return ints.astype(np.float64) / float(1 << 64)


def rows_digest(rows: np.ndarray) -> str:
    """sha256 of the SORTED int64 row list: a replicate's identity, independent of order."""
    return hashlib.sha256(np.sort(np.asarray(rows, dtype=np.int64)).tobytes()).hexdigest()


def sha256_file(path: Path | str, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------- #
# Pools
# ------------------------------------------------------------------------------------------- #
def load_pool_codes(pools_npz: Path | str, manifest_json: Path | str) -> tuple[np.ndarray, dict]:
    """The per-inventory-row pool codes, after checking the npz against the committed manifest.

    Refuses on a sha256 or per-pool count that differs from `POOL_MANIFEST.json`.
    """
    manifest = json.loads(Path(manifest_json).read_text())
    got = sha256_file(pools_npz)
    want = manifest["output"]["sha256"]
    if got != want:
        raise SystemExit(f"[replicates] pools npz sha256 {got} != manifest {want}")
    with np.load(pools_npz, allow_pickle=False) as handle:
        codes = np.asarray(handle["pool_codes"], dtype=np.int8)
    for name, info in manifest["pools"].items():
        n = int((codes == info["code"]).sum())
        if n != int(info["count"]):
            raise SystemExit(f"[replicates] pool {name}: {n} rows, manifest says {info['count']}")
    record = {"pools_npz": str(pools_npz), "pools_npz_sha256": got,
              "manifest": str(manifest_json), "manifest_commit": manifest.get("commit"),
              "counts": {k: int(v["count"]) for k, v in manifest["pools"].items()}}
    return codes, record


def pool_rows(codes: np.ndarray, pool: str) -> np.ndarray:
    """Inventory rows of one pool, ascending."""
    return np.flatnonzero(np.asarray(codes) == POOL_CODES[pool]).astype(np.int64)


# ------------------------------------------------------------------------------------------- #
# Replicate draws
# ------------------------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ReplicateDesign:
    """A named family of replicate draws in one pool, at fixed sample sizes."""
    pool: str
    family: str
    n_prior: int
    n_pseudo: int
    disjoint: bool = True

    def __post_init__(self) -> None:
        if self.pool not in POOL_CODES:
            raise ValueError(f"unknown pool {self.pool!r}")
        if self.n_prior < 0 or self.n_pseudo < 0 or self.n_prior + self.n_pseudo == 0:
            raise ValueError("sample sizes must be non-negative and not both zero")
        if "/" in self.family:
            raise ValueError("family names may not contain '/'")

    @property
    def block(self) -> int:
        return int(self.n_prior + self.n_pseudo)

    def family_salt(self) -> str:
        return f"{SALT}/{self.pool}/{self.family}"

    def replicate_salt(self, replicate: int) -> str:
        return f"{SALT}/{self.pool}/{self.family}/{int(replicate)}"

    def capacity(self, n_available: int) -> int:
        """How many DISJOINT replicates the available rows support."""
        return int(n_available // self.block)


@dataclass
class Replicate:
    design: ReplicateDesign
    replicate: int
    prior_rows: np.ndarray       # inventory rows, in u_r order
    pseudo_rows: np.ndarray      # inventory rows, in u_r order

    def record(self) -> dict[str, Any]:
        return {"design": asdict(self.design), "replicate": int(self.replicate),
                "family_salt": self.design.family_salt(),
                "replicate_salt": self.design.replicate_salt(self.replicate),
                "n_prior": int(self.prior_rows.size), "n_pseudo": int(self.pseudo_rows.size),
                "prior_rows_sha256": rows_digest(self.prior_rows),
                "pseudo_rows_sha256": rows_digest(self.pseudo_rows)}


def _order(u: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Positions sorted by (u, row): a total order even in the (never observed) case of ties."""
    return np.lexsort((rows, u))


def draw_replicates(design: ReplicateDesign, replicates: Sequence[int], rows: np.ndarray,
                    identity: np.ndarray, exclude: np.ndarray | None = None
                    ) -> tuple[list[Replicate], dict[str, Any]]:
    """Draw the named replicates of `design` from the pool given by (`rows`, `identity`).

    ``rows`` are the pool's inventory rows and ``identity`` their (n, 3) event identities (aligned).
    ``exclude`` is an optional boolean mask aligned to ``rows``. Returns the replicates and a record
    carrying the salts, seeds, availability, capacity and (if not disjoint) the measured overlaps.
    """
    rows = np.asarray(rows, dtype=np.int64)
    identity = np.asarray(identity, dtype=np.int64)
    if identity.shape[0] != rows.size:
        raise ValueError(f"{identity.shape[0]} identities for {rows.size} rows")
    if np.unique(rows).size != rows.size:
        raise ValueError("pool rows are not unique")
    keep = np.ones(rows.size, dtype=bool) if exclude is None else ~np.asarray(exclude, bool)
    avail_rows, avail_id = rows[keep], identity[keep]
    n_avail = int(avail_rows.size)
    reps = sorted({int(r) for r in replicates})
    if any(r < 0 for r in reps):
        raise ValueError("replicate ids must be >= 0")
    cap = design.capacity(n_avail)
    record: dict[str, Any] = {"design": asdict(design), "salt": SALT,
                              "family_salt": design.family_salt(),
                              "family_seed": seed_from_salt(design.family_salt()),
                              "n_pool_rows": int(rows.size), "n_excluded": int((~keep).sum()),
                              "n_available": n_avail, "disjoint_capacity": cap,
                              "replicates": {}}
    if design.block > n_avail:
        raise SystemExit(f"[replicates] {design.family}: one replicate needs {design.block} rows, "
                         f"{n_avail} available")
    if design.disjoint:
        if reps and reps[-1] >= cap:
            raise SystemExit(f"[replicates] {design.family}: replicate {reps[-1]} needs "
                             f"{(reps[-1] + 1) * design.block} rows for a disjoint draw, "
                             f"{n_avail} available (capacity {cap}); declare disjoint=False")
        u_f = uniform_hash(avail_id, seed_from_salt(design.family_salt()))
        family_order = _order(u_f, avail_rows)
    out = []
    for r in reps:
        if design.disjoint:
            pos = family_order[r * design.block:(r + 1) * design.block]
        else:
            u_all = uniform_hash(avail_id, seed_from_salt(design.replicate_salt(r)))
            pos = _order(u_all, avail_rows)[:design.block]
        u_r = uniform_hash(avail_id[pos], seed_from_salt(design.replicate_salt(r)))
        pos = pos[_order(u_r, avail_rows[pos])]
        rep = Replicate(design, r, avail_rows[pos[:design.n_prior]],
                        avail_rows[pos[design.n_prior:]])
        out.append(rep)
        record["replicates"][str(r)] = rep.record()
        record["replicates"][str(r)]["replicate_seed"] = seed_from_salt(design.replicate_salt(r))
    record["overlap"] = measure_overlap(out)
    return out, record


def measure_overlap(reps: Iterable[Replicate]) -> dict[str, Any]:
    """Shared-event counts between every pair of replicates (0 for a disjoint family), and the
    prior/pseudodata disjointness inside each replicate (must be 0)."""
    reps = list(reps)
    sets = {r.replicate: np.union1d(r.prior_rows, r.pseudo_rows) for r in reps}
    within = {str(r.replicate): int(np.intersect1d(r.prior_rows, r.pseudo_rows).size) for r in reps}
    if any(within.values()):
        raise AssertionError(f"prior and pseudodata share events: {within}")
    pairs = {}
    keys = sorted(sets)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            shared = int(np.intersect1d(sets[a], sets[b], assume_unique=True).size)
            pairs[f"{a}-{b}"] = {"shared_events": shared,
                                 "fraction_of_block": shared / max(sets[a].size, 1)}
    return {"within_replicate_prior_pseudo_shared": within, "pairwise": pairs,
            "max_pairwise_fraction": max((p["fraction_of_block"] for p in pairs.values()),
                                         default=0.0)}
