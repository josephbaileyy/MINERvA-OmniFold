"""RDX's shared constants and the event-identity key (RDX-DECLARATION.md rev 3 §2)."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

TRUTHX = ("truthx_enu", "truthx_vtx_x", "truthx_vtx_y", "truthx_vtx_z", "truthx_kep_lead")
IDS = ("truthx_run", "truthx_subrun", "truthx_evt")
C1_BRANCHES = TRUTHX + IDS
C1_TREES = ("mc_signal_reco", "mc_truth_denom")
SIDECAR_SCHEMA = "rdx-truthx-sidecar/1"
SUB_BITS, EVT_BITS = 20, 22


class CheckError(RuntimeError):
    """An RDX check could not run as declared."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def pack(run, subrun, evt) -> np.ndarray:
    """One int64 key per (run, subrun, event); refuses a value outside the packed field widths."""
    run, subrun, evt = (np.asarray(a, np.int64) for a in (run, subrun, evt))
    if (np.any(run < 0) or np.any(subrun < 0) or np.any(evt < 0) or np.any(subrun >= 1 << SUB_BITS)
            or np.any(evt >= 1 << EVT_BITS) or np.any(run >= 1 << (63 - SUB_BITS - EVT_BITS))):
        raise CheckError("an event identity is outside the packed key's field widths")
    return (run << (SUB_BITS + EVT_BITS)) | (subrun << EVT_BITS) | evt


def index_of(keys: np.ndarray, what: str) -> tuple[np.ndarray, np.ndarray]:
    """(sorted keys, their row order); refuses duplicate keys."""
    order = np.argsort(keys, kind="stable")
    sk = keys[order]
    if sk.size and np.any(sk[1:] == sk[:-1]):
        raise CheckError(f"{what} has duplicate event identities")
    return sk, order


def lookup(sk: np.ndarray, order: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Row index of each query key in the indexed table, or -1."""
    pos = np.searchsorted(sk, q)
    pos_c = np.minimum(pos, max(sk.size - 1, 0))
    hit = (pos < sk.size) & (sk[pos_c] == q) if sk.size else np.zeros(q.size, bool)
    return np.where(hit, order[pos_c], -1)
