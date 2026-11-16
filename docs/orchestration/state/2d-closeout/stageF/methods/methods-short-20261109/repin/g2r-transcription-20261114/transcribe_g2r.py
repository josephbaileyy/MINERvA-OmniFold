#!/usr/bin/env python3
"""Lossless CSV transcription of COV2D-G2R's data readout, data_g2r.npz (sha256 3b8cc7ce...), on the Mac, from the
copy cov2d fetched with O_NOATIME reads. Run from the top of a checkout of the repository.

usage: python3 transcribe_g2r.py <data_g2r.npz> <out dir>

Writes, into <out dir> (which must be empty or absent):
  g2r_<M>.csv     for M in C_new, C_univ_old, C_univ_new: a 205 x 205 matrix, header global_id then the ids, one row
                  per id, each float64 in repr
  g2r_bands.csv   band, universe, then the 205 ids: one row per universe of each band__<band> array, in the npz's
                  band order and row order, each float64 in repr
The npz carries no cell ids. Its order is that of the c2a transcription (receipts/c2a-20261109 on #981), which this
script reads from the checkout: C_new must equal c2a's Q - C_univ_old + C_univ_new byte for byte, which holds only if
the orders agree. repr is Python's shortest string that parses back to the same float64. The round trip parses every
file back and requires each array to equal the npz's byte for byte (ndarray.tobytes()); NaN, infinities and negative
zeros are refused first. The script also recomputes the median per-cell relative sigma of c2a's Q and of C_new and
requires each to equal data_g2r.json's readings.sigma.median_pct (committed, PR #1144) exactly. Requires numpy.
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

WANT = "3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b"
MATRICES = ["C_new", "C_univ_old", "C_univ_new"]
C2A = ("docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/receipts/c2a-20261109/"
       "transcription")
C2A_REF = "origin/pkg/methods-result-20261109"     # #981's branch, where the c2a receipt is committed
C2A_SHA = {"cov2d_x.csv": "f0612bcc3bc432e90b6a1546a106043a7c525d4cae69e29ebdcec6a4505df723",
           "cov2d_Q.csv": "4f07aa887c5896161f82297431a12cbdd30bdc3e11d86befb3c76648078b2d74"}
READOUT = ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/readout/data/"
           "data_g2r.json")
READOUT_SHA = "cd975b64402325da489ae608277faf5f6d7a7cbebe4974465f90b07c336e083f"


def git_bytes(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, check=True).stdout


def pinned(ref, path, want):
    b = git_bytes(ref, path)
    got = hashlib.sha256(b).hexdigest()
    if got != want:
        raise SystemExit(f"TRANSCRIBE: {ref}:{path} has sha256 {got}, pinned {want}")
    return b.decode()


def finite(name, a):
    if not np.isfinite(a).all() or np.any((a == 0) & np.signbit(a)):
        raise SystemExit(f"TRANSCRIBE: {name} holds a NaN, an infinity or a negative zero")


def main(argv):
    src, out = Path(argv[0]), Path(argv[1])
    raw = src.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != WANT:
        raise SystemExit(f"TRANSCRIBE: {src} has sha256 {got}, bound {WANT}")
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"TRANSCRIBE: {out} is not empty")
    z = np.load(src, allow_pickle=False)
    bands = [k for k in z.files if k.startswith("band__")]
    if sorted(z.files) != sorted(MATRICES + bands) or len(bands) != 38:
        raise SystemExit(f"TRANSCRIBE: arrays {sorted(z.files)}")
    for k in MATRICES:
        if z[k].dtype != np.float64 or z[k].shape != (205, 205):
            raise SystemExit(f"TRANSCRIBE: {k} has an unexpected dtype or shape")
    for k in bands:
        if z[k].dtype != np.float64 or z[k].ndim != 2 or z[k].shape[1] != 205:
            raise SystemExit(f"TRANSCRIBE: {k} has an unexpected dtype or shape")
    for k in z.files:
        finite(k, z[k])
    n_univ = sum(z[k].shape[0] for k in bands)

    # the cell order, from c2a
    xr = list(csv.reader(pinned(C2A_REF, f"{C2A}/cov2d_x.csv", C2A_SHA["cov2d_x.csv"]).splitlines()))
    ids = [int(r[0]) for r in xr[1:]]
    x = np.array([float(r[1]) for r in xr[1:]], dtype=np.float64)
    qr = list(csv.reader(pinned(C2A_REF, f"{C2A}/cov2d_Q.csv", C2A_SHA["cov2d_Q.csv"]).splitlines()))
    if [int(v) for v in qr[0][1:]] != ids or [int(r[0]) for r in qr[1:]] != ids:
        raise SystemExit("TRANSCRIBE: c2a's Q ids differ from its x ids")
    Q = np.array([[float(v) for v in r[1:]] for r in qr[1:]], dtype=np.float64)
    order = (Q - z["C_univ_old"] + z["C_univ_new"]).tobytes() == np.ascontiguousarray(z["C_new"]).tobytes()
    print(f"C_new equals c2a's Q - C_univ_old + C_univ_new byte for byte (the npz is in c2a's cell order): {order}")
    if not order:
        raise SystemExit("TRANSCRIBE: the npz's cell order is not established")

    # the readout's medians, recomputed
    ro = json.loads(pinned("HEAD", READOUT, READOUT_SHA))["readings"]["sigma"]["median_pct"]
    med = [float(np.sort(100 * np.sqrt(np.diag(M)) / x)[102]) for M in (Q, z["C_new"])]
    print(f"median per-cell relative sigma: c2a's Q {med[0]!r}, C_new {med[1]!r}; data_g2r.json {ro[0]!r}, {ro[1]!r}")
    if med != [float(ro[0]), float(ro[1])]:
        raise SystemExit("TRANSCRIBE: the medians differ from data_g2r.json")

    out.mkdir(parents=True, exist_ok=True)
    for k in MATRICES:
        with open(out / f"g2r_{k}.csv", "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["global_id"] + ids)
            w.writerows([i] + [repr(float(v)) for v in row] for i, row in zip(ids, z[k]))
    with open(out / "g2r_bands.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["band", "universe"] + ids)
        for k in bands:
            w.writerows([k[len("band__"):], u] + [repr(float(v)) for v in row] for u, row in enumerate(z[k]))

    # the round trip: every file parsed back equals the npz byte for byte
    ok = True
    for k in MATRICES:
        rows = list(csv.reader(open(out / f"g2r_{k}.csv")))
        hdr_ok = [int(v) for v in rows[0][1:]] == ids and [int(r[0]) for r in rows[1:]] == ids
        back = np.array([[float(v) for v in r[1:]] for r in rows[1:]], dtype=np.float64)
        same = hdr_ok and back.tobytes() == np.ascontiguousarray(z[k]).tobytes()
        print(f"g2r_{k}.csv: ids in order and matrix bitwise equal to the npz: {same}")
        ok = ok and same
    rows = list(csv.reader(open(out / "g2r_bands.csv")))
    same = [int(v) for v in rows[0][2:]] == ids and len(rows) - 1 == n_univ
    i = 1
    for k in bands:
        n = z[k].shape[0]
        blk = rows[i:i + n]
        same = same and all(r[0] == k[len("band__"):] and int(r[1]) == u for u, r in enumerate(blk))
        back = np.array([[float(v) for v in r[2:]] for r in blk], dtype=np.float64)
        same = same and back.tobytes() == np.ascontiguousarray(z[k]).tobytes()
        i += n
    print(f"g2r_bands.csv: {len(bands)} bands, {n_univ} universe rows, labels in order and every row bitwise equal to "
          f"the npz: {same}")
    ok = ok and same
    for p in sorted(out.iterdir()):
        print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    if not ok:
        raise SystemExit("TRANSCRIBE: the round trip is not exact")
    print(f"TRANSCRIBE :: PASS (npz {got}; 4 files; every array bitwise equal after the round trip)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
