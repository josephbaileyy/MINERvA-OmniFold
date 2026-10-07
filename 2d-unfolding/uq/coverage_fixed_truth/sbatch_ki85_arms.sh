#!/bin/bash
#SBATCH --job-name=ki85_diag
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=01:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/ki85-diag-20261006/logs/%x_%a_%A.out
#SBATCH --error=/pscratch/sd/j/josephrb/ki85-diag-20261006/logs/%x_%a_%A.err

# KNOWN_ISSUES 85 bootstrap-on-one-toy diagnostic. The decision rule is in
# docs/orchestration/DECISION-RULE-20261006-ki85-bootstrap-diagnostic.md and was committed before any run.
#   arm T  KI85_ARM=T sbatch --array=301-350%N ...   fresh pseudo-data toys, MC unresampled
#   arm B  KI85_ARM=B sbatch --array=1-50%N   ...    data-only bootstrap S of toy 1's pseudo-data
# Both arms need KI85_EXPECT_HEAD (the reviewed commit). Outputs go under OUTROOT only.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-64}

PROD="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE="/pscratch/sd/j/josephrb/MINERvA-OmniFold-ki84-20261006"
OUTROOT="/pscratch/sd/j/josephrb/ki85-diag-20261006"
EXPECT_HEAD="${KI85_EXPECT_HEAD:?set KI85_EXPECT_HEAD to the reviewed commit}"
BASE_TOY=1
I="${SLURM_ARRAY_TASK_ID:?run as an array}"
case "${KI85_ARM:?set KI85_ARM=T|B}" in
  T) (( I >= 301 && I <= 350 )) || { echo "[FAIL] arm T toys are 301-350, got ${I}" >&2; exit 2; }
     OUT="${OUTROOT}/armT/toy${I}.root"; ARGS=(--toy "${I}" --no-mc-bootstrap) ;;
  B) (( I >= 1 && I <= 50 )) || { echo "[FAIL] arm B replicas are 1-50, got ${I}" >&2; exit 2; }
     OUT="${OUTROOT}/armB/boot${I}.root"; ARGS=(--toy "${BASE_TOY}" --no-mc-bootstrap --data-bootstrap "${I}") ;;
  *) echo "[FAIL] KI85_ARM=${KI85_ARM}" >&2; exit 2 ;;
esac
case "${OUT}" in "${PROD}"/*) echo "[FAIL] refusing to write under ${PROD}" >&2; exit 2 ;; esac

source "${CODE}/lib/resume_guard.sh"
rg_skip_if_complete "${OUT}" && exit 0
HEAD="$(git -C "${CODE}" rev-parse HEAD)"
[[ "${HEAD}" == "${EXPECT_HEAD}"* ]] || { echo "[FAIL] ${CODE} is at ${HEAD}, expected ${EXPECT_HEAD}" >&2; exit 3; }
[[ -z "$(git -C "${CODE}" status --porcelain --untracked-files=no)" ]] || { echo "[FAIL] ${CODE} is dirty" >&2; exit 3; }
source "${PROD}/setup_salloc_env.sh"
mkdir -p "$(dirname "${OUT}")"

echo "[sbatch] node=$(hostname) job=${SLURM_JOB_ID} arm=${KI85_ARM} index=${I} qos=${SLURM_JOB_QOS:-?} head=${HEAD}"
rg_run "${OUT}" python "${CODE}/2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py" "${ARGS[@]}" \
  --omnifile "${PROD}/2d-unfolding/runEventLoopOmniFold_MEFHC.root" \
  --mcfile "${PROD}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root" \
  --iters 5 --estimator lgbm --seed 1 --out "${OUT}"
echo "[sbatch] done $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
