#!/bin/bash
#SBATCH --job-name=g5-family-val
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/family_validate_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/family_validate_%j.err
set -eo pipefail

# Read-only terminal promotion gate. It neither extracts a spectrum nor constructs C_stat.
CODE_ROOT=${GATE5_VALIDATOR_CODE_ROOT:?submitter must export immutable committed worktree}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_VALIDATOR_EXPECTED_HEAD:?missing validator HEAD pin}
EXPECTED_RECON_SHA=${GATE5_RECON_EXPECTED_SHA:?missing family reconciler hash pin}
EXPECTED_ARTIFACT_SHA=${GATE5_ARTIFACT_VALIDATOR_EXPECTED_SHA:?missing artifact validator hash pin}
EXPECTED_ATOMIC_SHA=${GATE5_ATOMIC_EXPECTED_SHA:?missing atomic_write hash pin}

RECON=${CODE_ROOT}/nd-unfolding/pet/reconcile_gate5_family.py
ARTIFACT_VALIDATOR=${CODE_ROOT}/nd-unfolding/pet/validate_gate5_training_artifacts.py
ATOMIC=${CODE_ROOT}/nd-unfolding/pet/atomic_write.py
CAMPAIGN=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
OUTDIR=${CAMPAIGN}/validation
RECON_REPORT=${OUTDIR}/GATE5_FAMILY_RECONCILIATION.slurm-${SLURM_JOB_ID}.json
ARTIFACT_REPORT=${OUTDIR}/GATE5_TRAINING_ARTIFACT_VALIDATION.slurm-${SLURM_JOB_ID}.json
SACCT_REPORT=${OUTDIR}/GATE5_TRAINING_SACCT.slurm-${SLURM_JOB_ID}.psv
MARKER=${OUTDIR}/GATE5_TRAINING_FAMILY_PROMOTION.slurm-${SLURM_JOB_ID}.done
NOMINAL_SHA=544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9

die() { echo "[gate5-family-validate][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "invalid code worktree"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
for spec in "$RECON:$EXPECTED_RECON_SHA" "$ARTIFACT_VALIDATOR:$EXPECTED_ARTIFACT_SHA" \
            "$ATOMIC:$EXPECTED_ATOMIC_SHA"; do
  path=${spec%%:*}; expected=${spec##*:}
  [[ -s "$path" && ! -L "$path" ]] || die "missing/symlink code $path"
  [[ "$(sha_of "$path")" == "$expected" ]] || die "code hash drift $path"
done
[[ -s "$INPUT" && ! -L "$INPUT" ]] || die "missing/symlink source NPZ"
[[ -d "$CAMPAIGN/replicas" && ! -L "$CAMPAIGN/replicas" ]] || die "missing replica family"
mkdir -p "$OUTDIR"
for f in "$RECON_REPORT" "$ARTIFACT_REPORT" "$SACCT_REPORT" "$MARKER"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done

module load python
PYTHON_BIN=$(command -v python || command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "Python unavailable"
"$PYTHON_BIN" -c 'import numpy' || die "NumPy unavailable"
export PYTHONPATH="$(dirname "$ATOMIC"):${PYTHONPATH:-}"

echo "[gate5-family-validate] START job=${SLURM_JOB_ID} head=${EXPECTED_HEAD} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
sacct -j 56857233 -X -n -P \
  --format=JobID,JobIDRaw,State,ExitCode,Elapsed,Start,End,NodeList > "$SACCT_REPORT"

"$PYTHON_BIN" "$RECON" \
  --root "$CAMPAIGN" \
  --n 50 \
  --stage family \
  --source-npz "$INPUT" \
  --nominal-target-sha "$NOMINAL_SHA" \
  --out "$RECON_REPORT"

"$PYTHON_BIN" "$ARTIFACT_VALIDATOR" \
  --campaign-root "$CAMPAIGN" \
  --family-report "$RECON_REPORT" \
  --sacct "$SACCT_REPORT" \
  --out "$ARTIFACT_REPORT"

"$PYTHON_BIN" - "$RECON_REPORT" "$ARTIFACT_REPORT" "$SACCT_REPORT" "$MARKER" \
  "$EXPECTED_HEAD" "$EXPECTED_RECON_SHA" "$EXPECTED_ARTIFACT_SHA" <<'PY'
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

recon_path, artifact_path, sacct_path, marker_path, head, recon_sha, artifact_sha = sys.argv[1:]
def read(path):
    with open(path, "rb") as stream:
        data = stream.read()
    return data, json.loads(data)
recon_bytes, recon = read(recon_path)
artifact_bytes, artifact = read(artifact_path)
if recon.get("verdict") != "FAMILY_COMPLETE_PASS" or not recon.get("is_full_strength"):
    raise SystemExit("family reconciler is not a full-strength complete PASS")
if artifact.get("verdict") != "GATE5_TRAINING_ARTIFACTS_PASS":
    raise SystemExit("training artifact validator is not PASS")
marker = {
    "schema_version": 1,
    "verdict": "GATE5_TRAINING_FAMILY_PROMOTION_PASS",
    "job_id": os.environ["SLURM_JOB_ID"],
    "source_array_job_id": "56857233",
    "validator_head": head,
    "validator_sha256": {"family_reconciler": recon_sha,
                         "training_artifact_validator": artifact_sha},
    "reports": {
        "family": {"path": os.path.realpath(recon_path),
                   "sha256": hashlib.sha256(recon_bytes).hexdigest(),
                   "verdict": recon["verdict"]},
        "training_artifacts": {"path": os.path.realpath(artifact_path),
                               "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
                               "verdict": artifact["verdict"]},
        "sacct": {"path": os.path.realpath(sacct_path),
                  "sha256": hashlib.sha256(open(sacct_path, "rb").read()).hexdigest()},
    },
    "counts": {"targets": 50, "trainings": 50, "passing": 50, "failing": 0},
    "C_stat": None,
    "next_stage": "predeclared full-input per-replica extraction and complete manifest",
    "marked_at": datetime.now(timezone.utc).isoformat(),
}
with open(marker_path, "x", encoding="utf-8") as stream:
    json.dump(marker, stream, indent=2, sort_keys=True)
    stream.write("\n")
PY

echo "[gate5-family-validate] DONE marker=${MARKER} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
