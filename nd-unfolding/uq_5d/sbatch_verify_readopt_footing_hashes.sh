#!/bin/bash
#SBATCH --job-name=readopt5d_hash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/readopt_20260811_footing/hash_verify_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/readopt_20260811_footing/hash_verify_%j.err

# Read-only completion of the SHA-256 receipt predeclared for footing job 56693207.
# The three large inputs total ~84 GB, so this belongs on a compute node rather
# than the login shell.  It never opens ROOT in write mode and publishes through
# a job-scoped PENDING file only after every source remained stable while read.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export MNV_REPO="$REPO"
export LAUNCHER_SHA256="$(sha256sum "$0" | awk '{print $1}')"
cd "$REPO/nd-unfolding"

/usr/bin/python3.11 - <<'PY'
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

repo = Path(os.environ["MNV_REPO"])
nd = repo / "nd-unfolding"
job = os.environ["SLURM_JOB_ID"]
outdir = nd / "uq_5d/readopt_20260811_footing"
target = outdir / f"HASH_RECEIPT.slurm-{job}.json"
pending = outdir / f".{target.name}.PENDING.{os.getpid()}"
if target.exists() or pending.exists():
    raise SystemExit(f"refusing existing output: {target} or {pending}")

paths = {
    "uthrow": nd / "uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root",
    "combined_bkgaware": nd / "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root",
    "combined_nonbkgaware": nd / "uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root",
    "A1_bkgaware_meancentered": outdir / "adopted_bkgaware_meancentered_20260811_footing.root",
    "A2_bkgaware_cvcentered": outdir / "adopted_bkgaware_cvcentered_20260811_footing.root",
    "C1_control_nonbkg_meancentered": outdir / "control_nonbkg_meancentered_20260811_footing.root",
    "C2_control_nonbkg_cvcentered": outdir / "control_nonbkg_cvcentered_20260811_footing.root",
    "whole_stream_log": nd / "uq_5d/readopt_footing_56693207.out",
}
missing = [str(p) for p in paths.values() if not p.is_file()]
if missing:
    raise SystemExit("missing sources: " + ", ".join(missing))

def digest_stable(path: Path) -> dict[str, object]:
    before = path.stat()
    h = hashlib.sha256()
    with path.open("rb", buffering=0) as handle:
        while block := handle.read(16 * 1024 * 1024):
            h.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"source changed while hashing: {path}")
    result = {
        "path": str(path.relative_to(repo)),
        "size_bytes": before.st_size,
        "mtime_ns": before.st_mtime_ns,
        "sha256": h.hexdigest(),
    }
    print(f"[hash] {result['sha256']} {result['size_bytes']} {result['path']}", flush=True)
    return result

files = {name: digest_stable(path) for name, path in paths.items()}
payload = {
    "schema": "readopt-footing-hash-receipt-v1",
    "created_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    "job_id": job,
    "source_job_id": "56693207",
    "launcher_sha256": os.environ["LAUNCHER_SHA256"],
    "files": files,
    "arms": {
        "A1": ["uthrow", "combined_bkgaware", "A1_bkgaware_meancentered"],
        "A2": ["uthrow", "combined_bkgaware", "A2_bkgaware_cvcentered"],
        "C1": ["uthrow", "combined_nonbkgaware", "C1_control_nonbkg_meancentered"],
        "C2": ["uthrow", "combined_nonbkgaware", "C2_control_nonbkg_cvcentered"],
    },
    "read_only": True,
    "adopts_nothing": True,
    "verdict": "HASHES_COMPLETE",
}
outdir.mkdir(parents=True, exist_ok=True)
with pending.open("x") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
    handle.write("\n")
    handle.flush()
    os.fsync(handle.fileno())
os.replace(pending, target)
print(f"[done] {target}", flush=True)
PY
