#!/usr/bin/env python3
"""Lossless CSV transcription of RE-2 part C's cov2d_Q_205.npz (sha256 7153b194...), on the Mac, from the copy that
cov2d_arrays_login.sh read and decode_c2a.py verified.

usage: python3 transcribe_c2a.py <cov2d_Q_205.npz> <out dir>

Writes, into <out dir> (which must be empty or absent):
  cov2d_x.csv            global_id,x: the 205 reported cells' global ids (pt*16 + pz) and x, each float64 in repr
  cov2d_<M>.csv          for M in Q, s5_total, universe, stat, c08, C_PL: a 205 x 205 matrix, header global_id then
                         the ids, one row per id, each float64 in repr
repr is Python's shortest string that parses back to the same float64, so the transcription is exact. The round-trip
check parses every file back and requires the arrays to equal the npz's byte for byte (ndarray.tobytes()); it refuses
NaN, infinities and negative zeros first, since those could hide in a text round trip. Requires numpy.
"""
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np

WANT = "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2"
MATRICES = ["Q", "s5_total", "universe", "stat", "c08", "C_PL"]


def main(argv):
    src, out = Path(argv[0]), Path(argv[1])
    raw = src.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != WANT:
        raise SystemExit(f"TRANSCRIBE: {src} has sha256 {got}, bound {WANT}")
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"TRANSCRIBE: {out} is not empty")
    out.mkdir(parents=True, exist_ok=True)
    z = np.load(src, allow_pickle=False)
    if sorted(z.files) != sorted(MATRICES + ["cells", "x"]):
        raise SystemExit(f"TRANSCRIBE: arrays {sorted(z.files)}")
    cells, x = z["cells"], z["x"]
    if cells.dtype != np.int64 or cells.shape != (205,) or x.dtype != np.float64 or x.shape != (205,):
        raise SystemExit("TRANSCRIBE: cells or x has an unexpected dtype or shape")
    for k in MATRICES + ["x"]:
        a = z[k]
        if not np.isfinite(a).all() or np.any((a == 0) & np.signbit(a)):
            raise SystemExit(f"TRANSCRIBE: {k} holds a NaN, an infinity or a negative zero")
    ids = [int(i) for i in cells]
    with open(out / "cov2d_x.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["global_id", "x"])
        w.writerows([i, repr(float(v))] for i, v in zip(ids, x))
    for k in MATRICES:
        a = z[k]
        if a.dtype != np.float64 or a.shape != (205, 205):
            raise SystemExit(f"TRANSCRIBE: {k} has an unexpected dtype or shape")
        with open(out / f"cov2d_{k}.csv", "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["global_id"] + ids)
            w.writerows([i] + [repr(float(v)) for v in row] for i, row in zip(ids, a))
    # the round trip: every file parsed back equals the npz byte for byte
    rows = list(csv.reader(open(out / "cov2d_x.csv")))
    back_ids = np.array([int(r[0]) for r in rows[1:]], dtype=np.int64)
    back_x = np.array([float(r[1]) for r in rows[1:]], dtype=np.float64)
    ok = back_ids.tobytes() == cells.tobytes() and back_x.tobytes() == x.tobytes()
    print(f"cov2d_x.csv: ids and x bitwise equal to the npz: {ok}")
    for k in MATRICES:
        rows = list(csv.reader(open(out / f"cov2d_{k}.csv")))
        hdr_ok = [int(v) for v in rows[0][1:]] == ids and [int(r[0]) for r in rows[1:]] == ids
        back = np.array([[float(v) for v in r[1:]] for r in rows[1:]], dtype=np.float64)
        same = hdr_ok and back.tobytes() == np.ascontiguousarray(z[k]).tobytes()
        print(f"cov2d_{k}.csv: ids in order and matrix bitwise equal to the npz: {same}")
        ok = ok and same
    for p in sorted(out.iterdir()):
        print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    if not ok:
        raise SystemExit("TRANSCRIBE: the round trip is not exact")
    print(f"TRANSCRIBE :: PASS (npz {got}; 7 files; every array bitwise equal after the round trip)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
