#!/bin/bash
#SBATCH --job-name=fpsActLatChain
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=32G --time=08:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=active_universe_5d/fps/logs/fpsActLatChain_%j.out
#SBATCH --error=active_universe_5d/fps/logs/fpsActLatChain_%j.err
#
# The four committed steps of the selection-complete FIVE-BAND active-lateral FPS chain, run in one
# job so the (large) hashing cost is paid on compute and each step's input is the previous step's
# verified output. NOTHING here is new science code -- every step is pre-existing, committed
# infrastructure invoked with EXPLICIT --out paths.
#
#   1. fps_build_publication_manifest.py   -> publication manifest (schema v2) + PASS receipt
#   2. build_active_lateral_fps.py         -> active_scalar_lateral_fps_cov.root + component_build receipt
#   3. p4_validate_active_lateral_fps.py   -> p4 summary JSON + p4_validation receipt
#   4. adopt_active_lateral_fps.py         -> ..._combined_activelat.root + active_adoption receipt
#
# WHY 8 h for what is arithmetically trivial: fps_provenance.ENDPOINT_ARTIFACTS includes
# ("input_merged_sha256","input_merged_root"), so require_recompute_hashes() sha256s all TEN 74.8 GB
# merged endpoint omnifiles -- 748 GB per step, ~3 TB across the four steps. This is deliberate
# fail-closed design (never trust a stored hash string), but it means walltime is set by I/O, not by
# the 266x266 linear algebra. Sized generously on purpose: per BEN-030 a timeout here produces nothing,
# and every step writes its product only at the very end.
#
# Prerequisite (verified before submission): the ten negweight-refined endpoint unfolds from
# 56430128 exist in active_universe_5d/fps/unfolds_negweight_refined/ with bkg_mode=negweight-refined.
# Step 1 aggregates and reports any missing/mis-footed endpoint rather than failing on the first.
#
# Fail-closed: each step's rc is checked with NO pipe in between (BEN-035) and the chain stops on the
# first failure, so a red p4 validation can never be followed by an adoption. Every stream is
# redirected WHOLE to its own log and only read afterwards (BEN-026); python3 -u throughout (BEN-028).

set -o pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; ND="${REPO}/nd-unfolding"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${ND}" || exit 2

COV="active_universe_5d/fps/covariance"
LOGD="active_universe_5d/fps/logs/chain_${SLURM_JOB_ID}"
mkdir -p "${LOGD}" "${COV}"

# ONE utc stamp for the whole chain, so every receipt in it agrees.
UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

MANIFEST="${COV}/fps_publication_manifest.json"
PASSR="${COV}/fps_publication_pass_receipt.json"
ACTIVE="${COV}/active_scalar_lateral_fps_cov.root"
CBR="${COV}/receipt_component_build.json"
P4SUM="${COV}/p4_summary_active_lateral_fps.json"
P4R="${COV}/receipt_p4_validation.json"
COMBINED="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root"
ADOPTED="uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root"
ADOPTR="${COV}/receipt_active_adoption.json"
CV="uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"

echo "[chain] job=${SLURM_JOB_ID} utc=${UTC} host=$(hostname) start=$(date -u '+%F %T UTC')"
echo "[chain] logs -> ${LOGD}"

run_step () {                 # run_step <n> <label> <logfile> -- <cmd...>
    local n="$1" label="$2" log="$3"; shift 4
    local t0=${SECONDS}
    echo "[chain] STEP ${n} ${label} :: start $(date -u '+%F %T UTC')"
    "$@" > "${log}" 2>&1      # rc of the COMMAND, no pipe in between (BEN-035)
    local rc=$?
    local dt=$(( SECONDS - t0 ))
    echo "[chain] STEP ${n} ${label} :: rc=${rc} elapsed=${dt}s ($(( dt / 60 ))m)"
    if [ ${rc} -ne 0 ]; then
        echo "[chain] FAILED at step ${n} (${label}); chain stops. Full log: ${log}"
        echo "[chain] ---- last of ${log} for triage (the WHOLE log is on disk, untruncated) ----"
        tail -40 "${log}"
        exit ${rc}
    fi
    return 0
}

run_step 1 "publication manifest" "${LOGD}/step1_manifest.log" -- \
    python3 -u fps_build_publication_manifest.py \
        --negweight-dir active_universe_5d/fps/unfolds_negweight_refined \
        --merged-dir active_universe_5d/fps/merged \
        --cv "${CV}" \
        --out-manifest "${MANIFEST}" --out-receipt "${PASSR}" --utc "${UTC}"

run_step 2 "active lateral rollup" "${LOGD}/step2_rollup.log" -- \
    python3 -u build_active_lateral_fps.py \
        --manifest "${MANIFEST}" --pass-receipt "${PASSR}" --cv "${CV}" \
        --out "${ACTIVE}" --out-receipt "${CBR}" --utc "${UTC}"

run_step 3 "p4 validation" "${LOGD}/step3_p4.log" -- \
    python3 -u p4_validate_active_lateral_fps.py \
        --manifest "${MANIFEST}" --pass-receipt "${PASSR}" --component-receipt "${CBR}" \
        --active "${ACTIVE}:hCov_universe4d_total" \
        --support "${COMBINED}" --cv "${CV}" \
        --out "${P4SUM}" --out-receipt "${P4R}" --utc "${UTC}"

run_step 4 "active-lateral adoption" "${LOGD}/step4_adopt.log" -- \
    python3 -u adopt_active_lateral_fps.py \
        --manifest "${MANIFEST}" --pass-receipt "${PASSR}" --p4-receipt "${P4R}" \
        --combined "${COMBINED}" --active "${ACTIVE}:hCov_universe4d_total" \
        --stat uq_fps/corrected/uq_cov_stat_fps.root:hCov_statfps_reported \
        --ml uq_fps/corrected/uq_cov_mlsplit_fps.root:hCov_mlsplitfps_reported \
        --out "${ADOPTED}" --out-receipt "${ADOPTR}" --utc "${UTC}"

echo "[chain] ALL FOUR STEPS PASSED  end=$(date -u '+%F %T UTC')"
echo "[chain] manifest  ${MANIFEST}"
echo "[chain] active    ${ACTIVE}"
echo "[chain] p4 summ   ${P4SUM}"
echo "[chain] adopted   ${ADOPTED}"
