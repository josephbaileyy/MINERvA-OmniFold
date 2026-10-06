"""Copy completed PET run inputs from Perlmutter and verify them against their committed digests.

    pgc_fetch.py runs --pet-source SRC --dest RAW S4F-H2S1T24K5-FB0 S4S-H2S1T24K5-FB3-D4c_p_up ...
    pgc_fetch.py iteration --dest RAW --run S4F-H2S1T24K5-FB0 --k 5
    pgc_fetch.py inventory --dest RAW

Read-only on the cluster: `scp` of finished files and one byte-range read of the inventory's
`reco_scalars` member (no Python, no allocation). Every copied `replicate_arrays.npz` must hash to
the `replicate_arrays_sha256` its committed score file records (look-1 final-bank runs:
`results/final/scored_fb/`; development runs: `scalar/extract_receipt.json`), an iteration file to
the `iteration_file_sha256` of the committed score, and the decoded `reco_scalars` member to its
zip CRC and then to `RECO_SCALARS_SHA256`. A mismatch deletes the copy and exits non-zero.

Only signal-MC members are read: the inventory member is fetched by name and offset, and its
local header name is checked before decoding.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import subprocess
import sys
import zlib
from pathlib import Path

HOST = "saul.nersc.gov"
STUDY = "/pscratch/sd/j/josephrb/pet-final-design-20260925"
INVENTORY = "/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz"
INVENTORY_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
# zip local-header offset and span of `reco_scalars.npy` (from the zip central directory, read
# 2026-10-05 with Python's zipfile on the login node)
RECO_SCALARS_MEMBER = {"name": "reco_scalars.npy", "offset": 2128254706, "span": 312726429}
RECO_SCALARS_SHA256 = "66aea2d1e838f9687a3e9b8ab73b3dec3d4f28f1799c333e1430455de370291a"
ROW_FEATURES = f"{STUDY}/rowfeatures/row_features.npz"
ROW_FEATURES_SHA256 = "6b1168c825db71c803c9a76a87de6ae3d0f4c099097376df9010d3af96aa7121"
SCORED_FB = "nd-unfolding/pet/final_design/results/final/scored_fb"
DEV3N = "nd-unfolding/pet/final_design/results/dev3N"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def cluster_dir(run: str) -> str:
    if run.startswith("S4F-"):
        return f"{STUDY}/s4f/{run}"
    if run.startswith("S4S-"):
        return f"{STUDY}/s4s/{run}"
    if run.startswith("dev3N-"):
        return f"{STUDY}/dev3N/{run}"
    raise SystemExit(f"no route for {run!r} (look-1 S4F/S4S and dev3N only)")


def committed_score(pet_source: Path, run: str) -> dict:
    if run.startswith("dev3N-"):
        return json.loads((pet_source / DEV3N / f"{run}.scores.json").read_text())
    return json.loads((pet_source / SCORED_FB / f"{run}.design_scores.json").read_text())


def expected_arrays_sha(pet_source: Path, run: str) -> str:
    doc = committed_score(pet_source, run)
    prov = doc["provenance"]
    sha = prov.get("replicate_arrays_sha256")
    if not sha:
        raise SystemExit(f"{run}: committed score records no replicate_arrays_sha256")
    return sha


def scp(src: str, dest: Path) -> None:
    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", f"{HOST}:{src}", str(dest)], check=True)


def fetch_runs(a: argparse.Namespace) -> int:
    bad = []
    for run in a.runs:
        want = expected_arrays_sha(a.pet_source, run)
        d = a.dest / run
        f = d / "replicate_arrays.npz"
        if f.exists() and sha256_file(f) == want:
            continue
        d.mkdir(parents=True, exist_ok=True)
        scp(f"{cluster_dir(run)}/replicate_arrays.npz", f)
        scp(f"{cluster_dir(run)}/run_identity.json", d / "run_identity.json")
        got = sha256_file(f)
        if got != want:
            f.unlink()
            bad.append((run, got, want))
            continue
        print(f"{run}: replicate_arrays.npz {got[:12]} verified", flush=True)
    if bad:
        print(f"DIGEST MISMATCH (copies deleted): {bad}", file=sys.stderr)
        return 1
    return 0


def fetch_iteration(a: argparse.Namespace) -> int:
    doc = committed_score(a.pet_source, a.run)
    its = [r for r in doc["iterations"] if r["k"] == a.k]
    want = its[0].get("iteration_file_sha256") or its[0].get("file_sha256")
    d = a.dest / a.run / "iterations"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"iter{a.k - 1:02d}.npz"
    scp(f"{cluster_dir(a.run)}/iterations/{f.name}", f)
    got = sha256_file(f)
    if got != want:
        f.unlink()
        print(f"{a.run} {f.name}: {got} != committed {want} (deleted)", file=sys.stderr)
        return 1
    print(f"{a.run} {f.name}: {got[:12]} verified")
    return 0


def fetch_inventory(a: argparse.Namespace) -> int:
    import numpy as np
    a.dest.mkdir(parents=True, exist_ok=True)
    m = RECO_SCALARS_MEMBER
    raw = subprocess.run(["ssh", "-o", "BatchMode=yes", HOST,
                          f"tail -c +{m['offset'] + 1} {INVENTORY} | head -c {m['span']}"],
                         capture_output=True, check=True).stdout
    sig, _v, _flag, method, _t, _d, crc, _cs, _us, nlen, elen = struct.unpack(
        "<IHHHHHIIIHH", raw[:30])
    name = raw[30:30 + nlen].decode()
    if sig != 0x04034B50 or name != m["name"] or method != 8:
        raise SystemExit(f"unexpected zip member at the recorded offset: {name!r}, method {method}")
    data = zlib.decompressobj(-15).decompress(raw[30 + nlen + elen:])
    if (zlib.crc32(data) & 0xFFFFFFFF) != crc:
        raise SystemExit("reco_scalars: CRC mismatch")
    arr = np.load(io.BytesIO(data), allow_pickle=False)
    out = a.dest / "reco_scalars.npy"
    np.save(out, arr)
    got = sha256_file(out)
    if got != RECO_SCALARS_SHA256:
        out.unlink()
        raise SystemExit(f"reco_scalars.npy {got} != {RECO_SCALARS_SHA256} (deleted)")
    rf = a.dest / "row_features.npz"
    if not rf.exists() or sha256_file(rf) != ROW_FEATURES_SHA256:
        scp(ROW_FEATURES, rf)
        if sha256_file(rf) != ROW_FEATURES_SHA256:
            rf.unlink()
            raise SystemExit("row_features.npz digest mismatch (deleted)")
    print(f"reco_scalars.npy {arr.shape} {got[:12]}; row_features.npz verified")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("runs")
    r.add_argument("--pet-source", type=Path, required=True)
    r.add_argument("--dest", type=Path, required=True)
    r.add_argument("runs", nargs="+")
    i = sub.add_parser("iteration")
    i.add_argument("--pet-source", type=Path, required=True)
    i.add_argument("--dest", type=Path, required=True)
    i.add_argument("--run", required=True)
    i.add_argument("--k", type=int, required=True)
    v = sub.add_parser("inventory")
    v.add_argument("--dest", type=Path, required=True)
    a = ap.parse_args(argv)
    return {"runs": fetch_runs, "iteration": fetch_iteration, "inventory": fetch_inventory}[
        a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
