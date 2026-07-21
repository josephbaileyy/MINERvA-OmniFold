#!/bin/bash
#SBATCH --job-name=fe_pet_nom
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=08:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal/logs/fe_pet_nom_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_nominal/logs/fe_pet_nom_%j.err
#
# GATE-4 publication FULL-EVENT PET NOMINAL launcher (CODE-ONLY gate; NOT auto-submitted).
# Runs ONE unbootstrapped nominal training + ONE matched GPU-floor repeat (SAME seeds/config, new
# output tag -> exposes the GPU-nondeterminism floor), both routed through
# fullevent_fps_dataloader.build_fullevent_loaders and GATED by assert_publication_config
# (fingerprint pet-fullevent-fps-v1, bkg_mode=negweight-refined, G2 full-schema markers, background
# inventory). Consumes the negweight-refined literal Gate-2 target and references the Gate-3 source
# manifest. FAILS CLOSED on any fingerprint/target/inventory drift.
#
# This is NOT the quarantined recoil path nd-unfolding/pet/sbatch_pet_nominal_bkgsub.sh
# (KNOWN_ISSUES #19 / F7 -- recoil loader, no muon/background). Do not repurpose that script.
#
# NO AUTO-SUBMIT: this script only runs its body as a real sbatch array/job (SLURM_JOB_ID set) OR in
# login-safe selftest mode (PET_FE_NOMINAL_SELFTEST=1 -> config gate only, no GPU, no training).
# set -u intentionally omitted (root_6_28 conda deactivate aborts under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# ---- immutable bound footing (Gate-2 target + Gate-3 manifest + code) --------------------------
TARGET_NPZ="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_TARGET_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_TARGET_SIZE="9897374636"
GATE3_MANIFEST="${REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"
DATALOADER="${REPO}/nd-unfolding/pet/fullevent_fps_dataloader.py"
DRIVER="${REPO}/nd-unfolding/pet/train_fullevent_nominal.py"
EXPECTED_FINGERPRINT="pet-fullevent-fps-v1"
EXPECTED_BKG_MODE="negweight-refined"
EXPECTED_SCHEMA="g2-fullevent-v1"

OUTDIR="${REPO}/nd-unfolding/pet/fullevent_nominal"
LOG_DIR="${OUTDIR}/logs"
NOMINAL_OUT="${OUTDIR}/pet_fullevent_nominal_weights.npz"
FLOOR_OUT="${OUTDIR}/pet_fullevent_floor_weights.npz"

# adopted nominal seed/config policy (the floor repeat reuses these; only the output tag differs)
ESTIMATOR_SEED=42
SUBSAMPLE_SEED=0
NITER=2
EPOCHS=8
TRAIN_EVENTS=2000000

die() { echo "[fe_pet_nom][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

assert_isolated_namespace() {
  case "${OUTDIR}" in
    *recoil*|*bkgsub*|*of_inputs_pc*|*/g2_fullevent/*|*/active_universe_5d/*)
      die "output namespace resolves to a forbidden/shared path: ${OUTDIR}" ;;
  esac
  [[ "${OUTDIR}" == *"/nd-unfolding/pet/fullevent_nominal" ]] || die "OUTDIR not the isolated namespace: ${OUTDIR}"
}

# Login-safe, no-GPU publication config gate: routes through the driver, which calls
# assert_publication_config (fail closed). Bind the code hashes; verify target existence/markers.
config_gate() {
  [[ -f "$DATALOADER" ]] || die "dataloader missing: $DATALOADER"
  [[ -f "$DRIVER" ]]     || die "driver missing: $DRIVER"
  [[ -s "$TARGET_NPZ" ]] || die "Gate-2 target NPZ missing/empty: $TARGET_NPZ"
  [[ -f "$GATE3_MANIFEST" ]] || die "Gate-3 source manifest missing: $GATE3_MANIFEST"
  # Use the analysis env python by absolute path (modern numpy; login-safe, no TF) so the gate is
  # deterministic before setup_salloc_env.sh is sourced (KNOWN_ISSUES #17).
  local pybin="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}/bin/python3"
  [[ -x "$pybin" ]] || pybin="python3"
  "$pybin" "$DRIVER" --inputs "$TARGET_NPZ" --gate3-manifest "$GATE3_MANIFEST" --config-gate-only \
    || die "publication config gate FAILED (fingerprint/target/inventory mismatch)"
}

# ---- selftest (config view; NO GPU, NO training). PET_FE_NOMINAL_SELFTEST=1. ----
if [[ "${PET_FE_NOMINAL_SELFTEST:-0}" == "1" ]]; then
  assert_isolated_namespace
  echo "[fe_pet_nom-selftest] target=${TARGET_NPZ} sha=${EXPECTED_TARGET_SHA} size=${EXPECTED_TARGET_SIZE}"
  echo "[fe_pet_nom-selftest] fingerprint=${EXPECTED_FINGERPRINT} bkg_mode=${EXPECTED_BKG_MODE} schema=${EXPECTED_SCHEMA}"
  echo "[fe_pet_nom-selftest] gate3_manifest=${GATE3_MANIFEST}"
  echo "[fe_pet_nom-selftest] plan: nominal(seed=${ESTIMATOR_SEED},sub=${SUBSAMPLE_SEED},niter=${NITER},epochs=${EPOCHS},train=${TRAIN_EVENTS}) + matched GPU-floor repeat (same seeds, tag=floor)"
  echo "[fe_pet_nom-selftest] outputs: ${NOMINAL_OUT} , ${FLOOR_OUT}"
  config_gate
  echo "[fe_pet_nom-selftest] CONFIG GATE PASS (no GPU, no training, no submit)"
  return 0 2>/dev/null || exit 0
fi

# ============================ real GPU body (only under sbatch) ============================
[[ -n "${SLURM_JOB_ID:-}" ]] || die "must run as an sbatch job (SLURM_JOB_ID unset); this script never auto-submits"
assert_isolated_namespace
mkdir -p "$OUTDIR" "$LOG_DIR"

# Bound-footing drift guards BEFORE any compute (fail closed on target hash/size/marker/manifest).
g=$(sha_of "$TARGET_NPZ"); [[ "$g" == "$EXPECTED_TARGET_SHA" ]] || die "Gate-2 target sha drift: $g != $EXPECTED_TARGET_SHA"
g=$(stat -c '%s' "$TARGET_NPZ"); [[ "$g" == "$EXPECTED_TARGET_SIZE" ]] || die "Gate-2 target size drift: $g != $EXPECTED_TARGET_SIZE"
config_gate

source "${REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0

echo "[fe_pet_nom] NOMINAL train $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 "$DRIVER" --inputs "$TARGET_NPZ" --out "$NOMINAL_OUT" --tag nominal \
  --gate3-manifest "$GATE3_MANIFEST" --estimator-seed "$ESTIMATOR_SEED" \
  --subsample-seed "$SUBSAMPLE_SEED" --niter "$NITER" --epochs "$EPOCHS" --max-events "$TRAIN_EVENTS" \
  || die "nominal training failed"

echo "[fe_pet_nom] MATCHED GPU-FLOOR repeat (same seeds/config) $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 "$DRIVER" --inputs "$TARGET_NPZ" --out "$FLOOR_OUT" --tag floor \
  --gate3-manifest "$GATE3_MANIFEST" --estimator-seed "$ESTIMATOR_SEED" \
  --subsample-seed "$SUBSAMPLE_SEED" --niter "$NITER" --epochs "$EPOCHS" --max-events "$TRAIN_EVENTS" \
  || die "floor repeat failed"
echo "[fe_pet_nom] DONE $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
