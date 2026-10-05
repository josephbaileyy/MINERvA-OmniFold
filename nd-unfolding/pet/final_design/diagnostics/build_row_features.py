"""Compact per-row simulation features for the PET final-design study (simulation only).

Streams the signal-MC members of `G2_FPS_MEFHC_P12.npz` chunk by chunk (the members are deflate
compressed, so they cannot be memory-mapped) and writes one small `.npz` with, for every inventory
row:

* truth-cloud species counts from `part_gen` PDG codes -- protons (2212), neutrons (2112), charged
  pions (211), neutral pions (111), everything else -- and the number of real tokens. **These are
  counts over the stored, energy-ordered 12-token truth cloud (`TRUNCATED_CLOUD_COUNTS`), not full
  final-state multiplicities**: an event with 12 real tokens may have had more hadrons. They are
  exactly the counts the predecessor's D4 distortions are defined on (`phase_e/distortions.py
  count_species`), and exactly what PET's truth side receives.
* truth-cloud energy sums (all tokens; protons; neutrons), GeV.
* reco-cloud summaries from `part_reco`: number of real clusters (energy != 0) and their energy
  sum, GeV, over the stored 12-token reco cloud (also truncated).

Only simulation members are read. Real-data (`data_*`, `measured_*`) and background (`bkg_*`)
members are refused by name before any byte is read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

ALLOWED_MEMBERS = ("part_gen", "part_reco", "pass_reco", "pass_truth")
REFUSED_PREFIXES = ("data_", "measured_", "bkg_")
PDG = {"p": 2212, "n": 2112, "pipm": 211, "pi0": 111}
ENERGY_SCALE = 1000.0  # MeV -> GeV, as fullevent_fps_dataloader._SCALE
TRUNCATED_CLOUD_COUNTS = True
CHUNK_ROWS = 1_000_000


def _open_member(zf: zipfile.ZipFile, name: str):
    if name.startswith(REFUSED_PREFIXES) or name not in ALLOWED_MEMBERS:
        raise PermissionError(f"member {name!r} is not an allowed simulation member")
    fh = zf.open(name + ".npy")
    version = np.lib.format.read_magic(fh)
    shape, fortran, dtype = np.lib.format._read_array_header(fh, version)
    if fortran:
        raise ValueError(f"{name}: Fortran order not supported")
    return fh, shape, dtype


def _chunks(fh, shape, dtype, chunk_rows=None):
    chunk_rows = chunk_rows or CHUNK_ROWS
    row_items = int(np.prod(shape[1:])) if len(shape) > 1 else 1
    row_bytes = row_items * dtype.itemsize
    done = 0
    while done < shape[0]:
        n = min(chunk_rows, shape[0] - done)
        buf = fh.read(n * row_bytes)
        if len(buf) != n * row_bytes:
            raise IOError(f"short read at row {done}: {len(buf)} of {n * row_bytes} bytes")
        yield done, np.frombuffer(buf, dtype=dtype).reshape((n,) + tuple(shape[1:]))
        done += n


def truth_features(part_gen: np.ndarray) -> dict[str, np.ndarray]:
    E = part_gen[:, :, 0]
    pdg = np.rint(part_gen[:, :, 4]).astype(np.int64)
    valid = E != 0
    apdg = np.abs(pdg)
    out = {"tr_n_valid": valid.sum(1).astype(np.int8)}
    known = np.zeros_like(valid)
    for key, code in PDG.items():
        m = valid & (apdg == code)
        known |= m
        out[f"tr_n_{key}"] = m.sum(1).astype(np.int8)
    out["tr_n_other"] = (valid & ~known).sum(1).astype(np.int8)
    Eg = np.where(valid, E, 0.0) / ENERGY_SCALE
    out["tr_E_sum"] = Eg.sum(1).astype(np.float32)
    out["tr_E_p"] = np.where(apdg == PDG["p"], Eg, 0.0).sum(1).astype(np.float32)
    out["tr_E_n"] = np.where(apdg == PDG["n"], Eg, 0.0).sum(1).astype(np.float32)
    return out


def reco_features(part_reco: np.ndarray) -> dict[str, np.ndarray]:
    E = np.nan_to_num(part_reco[:, :, 0].astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    valid = E != 0
    return {"rc_n_valid": valid.sum(1).astype(np.int8),
            "rc_E_sum": (np.where(valid, E, 0.0) / ENERGY_SCALE).sum(1).astype(np.float32)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def build(inventory: Path, out: Path, expect_sha: str | None) -> dict:
    t0 = time.time()
    inv_sha = sha256(inventory) if expect_sha else None
    if expect_sha and inv_sha != expect_sha:
        raise ValueError(f"inventory sha256 {inv_sha} != expected {expect_sha}")
    cols: dict[str, np.ndarray] = {}
    with zipfile.ZipFile(inventory) as zf:
        for member, fn in (("part_gen", truth_features), ("part_reco", reco_features)):
            fh, shape, dtype = _open_member(zf, member)
            n = shape[0]
            for start, chunk in _chunks(fh, shape, dtype):
                feats = fn(chunk)
                for k, v in feats.items():
                    if k not in cols:
                        cols[k] = np.empty(n, dtype=v.dtype)
                    cols[k][start:start + len(v)] = v
                print(f"[{member}] {start + len(chunk)}/{n} rows, {time.time() - t0:.0f}s",
                      flush=True)
        for member in ("pass_reco", "pass_truth"):
            fh, shape, dtype = _open_member(zf, member)
            cols[member] = np.concatenate([c for _, c in _chunks(fh, shape, dtype)]).astype(bool)
    n_rows = {len(v) for v in cols.values()}
    if len(n_rows) != 1:
        raise ValueError(f"row-count mismatch across members: {n_rows}")
    np.savez(out, **cols)
    receipt = {
        "schema": "pet-final-design/row-features/1",
        "inventory": str(inventory), "inventory_sha256": inv_sha,
        "output": str(out), "output_sha256": sha256(out),
        "rows": n_rows.pop(), "columns": sorted(cols),
        "truncated_cloud_counts": TRUNCATED_CLOUD_COUNTS,
        "members_read": list(ALLOWED_MEMBERS), "seconds": round(time.time() - t0, 1),
        "totals": {k: int(cols[k].astype(np.int64).sum()) for k in cols if k.startswith(("tr_n", "rc_n"))},
    }
    out.with_suffix(".receipt.json").write_text(json.dumps(receipt, indent=1))
    return receipt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--expect-sha256", default=None)
    a = ap.parse_args(argv)
    r = build(a.inventory, a.out, a.expect_sha256)
    print(json.dumps({k: r[k] for k in ("rows", "output_sha256", "seconds")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
