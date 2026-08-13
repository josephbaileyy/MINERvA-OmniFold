#!/bin/bash
#SBATCH --job-name=g5t-recon
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/target_reconcile_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/logs/target_reconcile_%j.err
set -eo pipefail

# Read-only, terminal target-family validation. It never constructs C_stat and never writes in a
# replica namespace. Training array 56857233 remains the sole writer of training artifacts.
CODE_ROOT=${GATE5_RECON_CODE_ROOT:?submitter must export the committed code worktree}
DATA_ROOT=${GATE5_DATA_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
EXPECTED_HEAD=${GATE5_RECON_EXPECTED_HEAD:?missing committed reconciler HEAD pin}
EXPECTED_VALIDATOR_SHA=${GATE5_RECON_EXPECTED_VALIDATOR_SHA:?missing reconciler sha pin}

VALIDATOR=${CODE_ROOT}/nd-unfolding/pet/reconcile_gate5_family.py
CAMPAIGN=${DATA_ROOT}/nd-unfolding/pet/fullevent_cstat_n50
INPUT=${DATA_ROOT}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
OUTDIR=${CAMPAIGN}/validation
REPORT=${OUTDIR}/GATE5_TARGET_FAMILY_RECONCILIATION.slurm-${SLURM_JOB_ID}.json
MARKER=${REPORT}.done
NOMINAL_SHA=544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9

die() { echo "[gate5-target-reconcile][FAIL] $*" >&2; exit "${2:-1}"; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

[[ -d "$CODE_ROOT/.git" || -f "$CODE_ROOT/.git" ]] || die "invalid code worktree $CODE_ROOT"
[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"
[[ -s "$VALIDATOR" && ! -L "$VALIDATOR" ]] || die "missing/symlink validator"
[[ "$(sha_of "$VALIDATOR")" == "$EXPECTED_VALIDATOR_SHA" ]] || die "validator hash drift"
[[ -s "$INPUT" && ! -L "$INPUT" ]] || die "missing/symlink full-input NPZ"
[[ -d "$CAMPAIGN/replicas" && ! -L "$CAMPAIGN/replicas" ]] || die "missing replica family"

mkdir -p "$OUTDIR"
for f in "$REPORT" "$MARKER"; do
  [[ ! -e "$f" && ! -L "$f" ]] || die "collision/no-clobber guard: $f"
done

module load python
PYTHON_BIN=$(command -v python || command -v python3 || true)
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "Python unavailable"
"$PYTHON_BIN" -c 'import numpy' || die "NumPy unavailable"

echo "[gate5-target-reconcile] START job=${SLURM_JOB_ID} head=${EXPECTED_HEAD} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PYTHON_BIN" "$VALIDATOR" \
  --root "$CAMPAIGN" \
  --n 50 \
  --stage target \
  --source-npz "$INPUT" \
  --nominal-target-sha "$NOMINAL_SHA" \
  --out "$REPORT"

"$PYTHON_BIN" - "$REPORT" "$MARKER" <<'PY'
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

report_path, marker_path = sys.argv[1:]
with open(report_path, "rb") as stream:
    payload = stream.read()
report = json.loads(payload)
if report.get("verdict") != "TARGETS_COMPLETE_PASS":
    raise SystemExit(f"unexpected terminal verdict {report.get('verdict')!r}")
counts = report.get("counts", {})
if counts.get("targets_present") != 50 or counts.get("targets_passing") != 50:
    raise SystemExit(f"unexpected terminal target counts {counts!r}")
marker = {
    "output": os.path.realpath(report_path),
    "sha256": hashlib.sha256(payload).hexdigest(),
    "size": len(payload),
    "marked_at": datetime.now(timezone.utc).isoformat(),
    "job": os.environ.get("SLURM_JOB_ID"),
    "verdict": report["verdict"],
}
with open(marker_path, "x", encoding="utf-8") as stream:
    json.dump(marker, stream, indent=2, sort_keys=True)
    stream.write("\n")
PY

echo "[gate5-target-reconcile] DONE report=${REPORT} marker=${MARKER} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
