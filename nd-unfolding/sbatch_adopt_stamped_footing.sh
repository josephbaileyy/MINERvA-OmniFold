#!/bin/bash
#SBATCH --job-name=adopt5d_stamped
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=180G
#SBATCH --time=03:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/readopt_20260811_footing/adopt_stamped_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/readopt_20260811_footing/adopt_stamped_%j.err

# Produce the footing-matched candidate arms WITH BEN-106 provenance stamps, under adoption
# names, and hash them -- so that a single artifact is simultaneously footing-matched,
# stamp-verified and identified by sha256.  See
# docs/orchestration/PREDECLARE-20260812-stamped-footing-adoption-candidate.md
#
# Authorization: Joseph -> Session A -> Session B, 2026-08-12, item 1 of five.
# Adopts NOTHING into the note.  values.tex is not touched by this job.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export MNV_REPO="$REPO"
export LAUNCHER_SHA256="$(sha256sum "$0" | awk '{print $1}')"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=32
cd "${REPO}/nd-unfolding"

OUTDIR=uq_5d/readopt_20260811_footing
UTHROW=uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root
COMBINED=uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root
A1=${OUTDIR}/stamped_bkgaware_meancentered_20260812.root
A2=${OUTDIR}/stamped_bkgaware_cvcentered_20260812.root

# Refuse to overwrite: a resume guard that validates absence, not a bare -s test (BEN-023).
for f in "$A1" "$A2"; do
  if [[ -e "$f" ]]; then echo "[abort] refusing existing output: $f" >&2; exit 3; fi
done

echo "=== ARM A1' mean-centered ==="
python3 adopt_unified_5d.py --uthrow "$UTHROW" --combined "$COMBINED" --out "$A1"

echo "=== ARM A2' CV-centered ==="
python3 adopt_unified_5d.py --uthrow "$UTHROW" --combined "$COMBINED" --cv-centered --out "$A2"

echo "=== HASH RECEIPT ==="
/usr/bin/python3.11 - <<'PY'
from __future__ import annotations
import datetime as dt, hashlib, json, os
from pathlib import Path

repo = Path(os.environ["MNV_REPO"]); nd = repo / "nd-unfolding"
job = os.environ["SLURM_JOB_ID"]
outdir = nd / "uq_5d/readopt_20260811_footing"
target = outdir / f"STAMPED_HASH_RECEIPT.slurm-{job}.json"
pending = outdir / f".{target.name}.PENDING.{os.getpid()}"
if target.exists() or pending.exists():
    raise SystemExit(f"refusing existing output: {target}")

paths = {
    "uthrow": nd / "uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root",
    "combined_bkgaware": nd / "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root",
    "A1_stamped_meancentered": outdir / "stamped_bkgaware_meancentered_20260812.root",
    "A2_stamped_cvcentered": outdir / "stamped_bkgaware_cvcentered_20260812.root",
}
missing = [str(p) for p in paths.values() if not p.is_file()]
if missing:
    raise SystemExit("missing sources: " + ", ".join(missing))

def digest_stable(path: Path) -> dict:
    before = path.stat()
    h = hashlib.sha256()
    with path.open("rb", buffering=0) as fh:
        while block := fh.read(16 * 1024 * 1024):
            h.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"source changed while hashing: {path}")
    r = {"path": str(path.relative_to(repo)), "size_bytes": before.st_size,
         "mtime_ns": before.st_mtime_ns, "sha256": h.hexdigest()}
    print(f"[hash] {r['sha256']} {r['size_bytes']} {r['path']}", flush=True)
    return r

files = {k: digest_stable(p) for k, p in paths.items()}
payload = {
    "schema": "stamped-footing-candidate-receipt-v1",
    "created_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    "job_id": job,
    "source_job_id": "56693207",
    "launcher_sha256": os.environ["LAUNCHER_SHA256"],
    "authorization": "Joseph -> Session A -> Session B, 2026-08-12, item 1 of five",
    "predeclaration": "docs/orchestration/PREDECLARE-20260812-stamped-footing-adoption-candidate.md",
    "predicted": {"A1_sqrt_tr_new": "5.2696e-38", "A2_sqrt_tr_new": "5.6743e-38"},
    "files": files,
    "adopts_nothing": True,
    "values_tex_untouched": True,
    "verdict": "HASHES_COMPLETE_READ_STDOUT_FOR_ARM_VALUES",
}
outdir.mkdir(parents=True, exist_ok=True)
with pending.open("x") as fh:
    json.dump(payload, fh, indent=2, sort_keys=True); fh.write("\n"); fh.flush(); os.fsync(fh.fileno())
os.replace(pending, target)
print(f"[done] {target}", flush=True)
PY
echo "=== COMPLETED, NOTHING ADOPTED ==="
