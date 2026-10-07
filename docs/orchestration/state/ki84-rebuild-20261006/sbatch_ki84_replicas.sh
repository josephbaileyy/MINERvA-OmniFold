#!/bin/bash
#SBATCH --job-name=ki84_boot
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/ki84-rebuild-20261006/logs/boot_%a_%A.out
#SBATCH --error=/pscratch/sd/j/josephrb/ki84-rebuild-20261006/logs/boot_%a_%A.err

# KNOWN_ISSUES 84 candidate rebuild of the VL162 2D statistical replicas.
# The production launcher 2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootstrap_scaleup.sh is
# repeated argument for argument (--iters 5 --use-weights --estimator lgbm --bootstrap-seed N
# --seed 1; streams both and bkg-mode purity by default), with the fixed code. Only the code
# path and the output path differ. The VL162 files under the production uq/ are never written.
#   pilot  sbatch --array=1 ...   (writes pilot/)       KI84_STAGE=pilot
#   full   sbatch --array=1-300%N (writes replicas/)    KI84_STAGE=full
# Other lanes: sbatch --qos=shared --cpus-per-task=64 ... or --qos=debug --time=00:30:00.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

PROD="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE="/pscratch/sd/j/josephrb/MINERvA-OmniFold-ki84-20261006"
EXPECT_HEAD="${KI84_EXPECT_HEAD:?set KI84_EXPECT_HEAD to the reviewed commit}"
OUTROOT="/pscratch/sd/j/josephrb/ki84-rebuild-20261006"
OMNIFILE="${PROD}/2d-unfolding/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${PROD}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
SEED="${SLURM_ARRAY_TASK_ID:?run as an array; the index is the bootstrap seed}"
case "${KI84_STAGE:?set KI84_STAGE=pilot|full}" in
  pilot) OUTDIR="${OUTROOT}/pilot" ;;
  full)  OUTDIR="${OUTROOT}/replicas" ;;
  *) echo "[FAIL] KI84_STAGE=${KI84_STAGE}" >&2; exit 2 ;;
esac
OUT="${OUTDIR}/2d_xsec_MEFHC_5iter_lgbm_boot${SEED}.root"
case "${OUT}" in "${PROD}"/*) echo "[FAIL] refusing to write under ${PROD}" >&2; exit 2 ;; esac

source "${CODE}/lib/resume_guard.sh"
rg_skip_if_complete "${OUT}" && exit 0

HEAD="$(git -C "${CODE}" rev-parse HEAD)"
if [[ "${HEAD}" != "${EXPECT_HEAD}"* ]]; then
  echo "[FAIL] ${CODE} is at ${HEAD}, expected ${EXPECT_HEAD}" >&2; exit 3
fi
if [[ -n "$(git -C "${CODE}" status --porcelain --untracked-files=no)" ]]; then
  echo "[FAIL] ${CODE} has uncommitted changes" >&2; exit 3
fi
source "${PROD}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${OUTDIR}"

echo "[sbatch] node=$(hostname) job=${SLURM_JOB_ID} seed=${SEED} qos=${SLURM_JOB_QOS:-?} threads=${OMP_NUM_THREADS}"
echo "[sbatch] code=${CODE} head=${HEAD}"
echo "[sbatch] start $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
rg_run "${OUT}" python "${CODE}/2d-unfolding/unfold_2d_omnifold_unbinned.py" \
  --omnifile        "${OMNIFILE}" \
  --mcfile          "${FLUX_MC}" \
  --iters           5 \
  --use-weights \
  --estimator       lgbm \
  --bootstrap-seed  "${SEED}" \
  --seed            1 \
  --out             "${OUT}"
echo "[sbatch] done $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
