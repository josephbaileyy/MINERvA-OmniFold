"""Quartile edges of true q3 for the E5 joint histogram (PROTOCOL-20260925 section 4, E5).

E5 bins true q3 at "quartiles of the DEV bank". The bank manifest (`banks/BANK_MANIFEST.json`)
does not exist yet, so this computes the PROVISIONAL constant `score_design.Q3_QUARTILE_EDGES`
from every truth-passing inventory row with a finite true q3 (unweighted row quantiles,
`numpy.quantile` default linear interpolation). With `--exclude-rows` (an `.npy` of inventory row
indices, e.g. FB and RB once the banks are frozen) it computes the DEV-bank version.

Streams only the signal-MC members `truth_scalars` and `pass_truth` of `G2_FPS_MEFHC_P12.npz`
(deflate-compressed, so read chunk by chunk); real-data and background members are refused by
name. `--check-runs` verifies, for each run directory, that the inventory's q3 column at the run's
prior rows equals the run's `prior_truth[:, 3]` exactly (column order and units).

    python q3_quartiles.py --inventory G2_FPS_MEFHC_P12.npz [--check-runs RUN ...] --out q3.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "diagnostics"))
from build_row_features import REFUSED_PREFIXES, _chunks, sha256  # noqa: E402

ALLOWED = ("truth_scalars", "pass_truth")
Q3_COLUMN = 3          # fullevent_fps_dataloader.SCALAR_COLS["q3"]
PROBS = (0.25, 0.50, 0.75)


def _open(zf: zipfile.ZipFile, name: str):
    if name.startswith(REFUSED_PREFIXES) or name not in ALLOWED:
        raise PermissionError(f"member {name!r} is not an allowed simulation member")
    fh = zf.open(name + ".npy")
    version = np.lib.format.read_magic(fh)
    shape, fortran, dtype = np.lib.format._read_array_header(fh, version)
    if fortran:
        raise ValueError(f"{name}: Fortran order not supported")
    return fh, shape, dtype


def read_q3(inventory: Path) -> tuple[np.ndarray, np.ndarray]:
    with zipfile.ZipFile(inventory) as zf:
        fh, shape, dtype = _open(zf, "truth_scalars")
        q3 = np.empty(shape[0], dtype=dtype)
        for start, chunk in _chunks(fh, shape, dtype):
            q3[start:start + len(chunk)] = chunk[:, Q3_COLUMN]
        fh, shape, dtype = _open(zf, "pass_truth")
        pt = np.concatenate([c for _, c in _chunks(fh, shape, dtype)]).astype(bool)
    if pt.size != q3.size:
        raise ValueError(f"row mismatch: pass_truth {pt.size} vs truth_scalars {q3.size}")
    return q3, pt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--exclude-rows", type=Path, default=None)
    ap.add_argument("--check-runs", nargs="*", type=Path, default=[])
    ap.add_argument("--hash-inventory", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    q3, pt = read_q3(a.inventory)
    checks = {}
    for run in a.check_runs:
        with np.load(run / "replicate_arrays.npz") as A:
            want = A["prior_truth"][:, 3]
            got = q3[A["prior_rows"]].astype(np.float64)
        same = (got == want) | (np.isnan(got) & np.isnan(want))
        checks[str(run)] = {"rows": int(want.size), "equal": bool(same.all()),
                            "n_unequal": int((~same).sum())}
    keep = pt & np.isfinite(q3)
    excluded = 0
    if a.exclude_rows is not None:
        ex = np.load(a.exclude_rows).astype(np.int64)
        excluded = int(keep[ex].sum())
        keep[ex] = False
    vals = q3[keep].astype(np.float64)
    edges = np.quantile(vals, PROBS)
    out = {"schema": "pet-final-design/q3-quartiles/1",
           "inventory": str(a.inventory),
           "inventory_sha256": sha256(a.inventory) if a.hash_inventory else None,
           "population": ("truth-passing rows with finite true q3"
                          + (f", excluding {a.exclude_rows}" if a.exclude_rows else
                             " (ALL inventory rows: provisional, not yet the DEV bank)")),
           "n_rows_inventory": int(q3.size), "n_truth_passing": int(pt.sum()),
           "n_truth_passing_nonfinite_q3": int((pt & ~np.isfinite(q3)).sum()),
           "n_excluded_truth_passing": excluded, "n_used": int(vals.size),
           "probabilities": list(PROBS), "quartile_edges_gev": [float(x) for x in edges],
           "quartile_edges_repr": [repr(float(x)) for x in edges],
           "weighting": "unweighted rows", "quantile_method": "numpy.quantile linear",
           "check_runs": checks, "seconds": round(time.time() - t0, 1)}
    a.out.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0 if all(c["equal"] for c in checks.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
