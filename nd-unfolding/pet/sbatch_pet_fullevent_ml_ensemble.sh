#!/bin/bash
#SBATCH --job-name=fe_pet_ml
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/logs/fe_pet_ml_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/logs/fe_pet_ml_%A_%a.err
#
# GATE 6 — PET-SPECIFIC ML ENSEMBLE, N=5. One array task per member.
# PREDECLARED: docs/orchestration/PREDECLARATION-20260813-gate6-ml-ensemble.md
#   N=5 is the neutrino OmniFold precedent (5 trials, stated justification that the resulting
#   standard error is negligible against the systematic and statistical budget). HERA jet
#   substructure used 10 per step. The choice is [CLAUDE]-class reasoning Joseph ENDORSED.
#
# WHY A NEW LAUNCHER RATHER THAN A FLAG ON AN EXISTING ONE. train_fullevent_nominal.py,
# sbatch_pet_fullevent_nominal.sh and their tests are LIVE PINS in
# p3f-pet-gate4-launch-code-gate-20260812.json -- 22 pinned files, verified sha256-identical to the
# working tree. Editing any of them converts a code change into a code-gate RE-ISSUE plus
# re-attestation of every pin. So this is a new file and touches none of them. Same reasoning, and
# the same precedent, as sbatch_pet_fullevent_nominal_annealed.sh.
#
# NO POISSON FLUCTUATION. Gate 6's own text: "Use the nominal target with no Poisson fluctuation.
# Vary only the predeclared crossed training/subsample/split and estimator seeds." So this consumes
# the PROMOTED Gate-2 target unchanged and varies seeds only. It is NOT Gate 5: no replica draw, no
# per-replica target rebuild, no --bootstrap-seed. Gate 5's N=50 is bootstrap replicas for the
# statistical component and is a different quantity from this N=5.
#
# "CROSSED" MEANS FIVE INDEPENDENT MEMBERS, NOT A FACTORIAL SCAN. A factorial of five values on two
# axes is 25 members, which is not what N=5 means and is not authorized. Member 1 is the PROMOTED
# NOMINAL'S OWN POLICY (42, 0), so the adopted estimator sits INSIDE the ensemble rather than being
# a sixth neighbour of it.
#
# THE POLICY IS NOT RESTATED HERE beyond the two varied seeds -- same reason as the canonical and
# annealed launchers: a launcher that hardcodes policy drifts from the driver, and the drift is only
# detected after a full training run. lr_policy has NO FLAG by design.
#
# Submit:  sbatch --array=1-5 sbatch_pet_fullevent_ml_ensemble.sh
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DRIVER="${REPO}/nd-unfolding/pet/train_fullevent_nominal.py"
TARGET_NPZ="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
EXPECTED_TARGET_SHA="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
GATE3_MANIFEST="${REPO}/docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json"

ENSDIR="${REPO}/nd-unfolding/pet/fullevent_ml_ensemble"
LOG_DIR="${ENSDIR}/logs"
mkdir -p "$LOG_DIR"

die() { echo "[fe_pet_ml][FAIL] $*" >&2; exit "${2:-1}"; }

MID="${SLURM_ARRAY_TASK_ID:-${MEMBER_ID:?set MEMBER_ID or submit as an array}}"

# THE PREDECLARED SEED TABLE. Member 1 == the promoted nominal's policy.
case "$MID" in
  1) EST=42; SUB=0 ;;
  2) EST=43; SUB=1 ;;
  3) EST=44; SUB=2 ;;
  4) EST=45; SUB=3 ;;
  5) EST=46; SUB=4 ;;
  *) die "member id $MID is outside the predeclared 1..5; N=5 is predeclared and a sixth member is not authorized" 3 ;;
esac

MEMBER_OUT="${ENSDIR}/member_${MID}/pet_fullevent_ml_member${MID}_weights.npz"
mkdir -p "$(dirname "$MEMBER_OUT")"

echo "[fe_pet_ml] job=${SLURM_JOB_ID:-nojob} array=${SLURM_ARRAY_JOB_ID:-na} member=${MID} host=$(hostname)"
echo "[fe_pet_ml] predeclared seeds: estimator=${EST} subsample=${SUB}"
echo "[fe_pet_ml] out=${MEMBER_OUT}"

for f in "$DRIVER" "$TARGET_NPZ" "$GATE3_MANIFEST"; do
  [[ -s "$f" ]] || die "missing $f"
done

# FAIL CLOSED ON THE TARGET. The ensemble is meaningless if members consume different targets.
gs="$(sha256sum "$TARGET_NPZ" | cut -d' ' -f1)"
[[ "$gs" == "$EXPECTED_TARGET_SHA" ]] || die "target sha mismatch: $gs != $EXPECTED_TARGET_SHA" 3
echo "[fe_pet_ml] target sha256 verified: ${gs:0:16}"
echo "[fe_pet_ml] driver sha256: $(sha256sum "$DRIVER" | cut -d' ' -f1 | cut -c1-16)"

# ENVIRONMENT. Omitting these is what killed members 1 and 2 of array 56832077 at 51s with
# ModuleNotFoundError: No module named 'tensorflow'. The canonical and annealed launchers both do
# exactly this and I modelled the rest of the file on them while dropping the two lines that make
# python3 the right python3. CLAUDE.md's compute quick reference states it: module load
# tensorflow/2.15.0.
source "${REPO}/setup_salloc_env.sh"
module load tensorflow/2.15.0

# PREFLIGHT, so the NEXT environment failure costs seconds and names itself rather than surfacing as
# a traceback from inside the driver after the provenance gates have already passed. Members 1 and 2
# printed target_provenance PASS and the correct promoted-target sha256 before dying on an import --
# every guard I wrote worked and the one I did not write is what failed.
python3 -c "import tensorflow as tf; print('[fe_pet_ml] tensorflow', tf.__version__)" \
  || die "tensorflow not importable after module load -- environment is wrong, not the physics" 5

# REFUSE TO CLOBBER. The driver already refuses to overwrite a finished artifact; this is the
# earlier, cheaper refusal so a resubmit does not burn six GPU-hours to discover it.
if [[ -s "${MEMBER_OUT}.done" ]]; then
  die "member ${MID} already has a .done marker -- refusing to rerun. Remove nothing; investigate." 4
fi

echo "[fe_pet_ml] TRAINING member ${MID} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 "$DRIVER" --inputs "$TARGET_NPZ" --out "$MEMBER_OUT" --tag nominal \
  --gate3-manifest "$GATE3_MANIFEST" \
  --estimator-seed "$EST" --subsample-seed "$SUB" \
  || die "member ${MID} training failed"

# POST-CONDITION, NOT JUST A PRE-CONDITION. The predeclaration says to read the REALIZED seed_policy
# the driver persists off argv, not the launch command -- the two can differ and only the persisted
# record is evidence. This is the check that makes that guarantee real rather than stated.
python3 - "$MEMBER_OUT" "$EST" "$SUB" "$MID" <<'PY'
import sys, numpy as np, json
out, est, sub, mid = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
z = np.load(out, allow_pickle=True)
if "seed_policy" not in z:
    raise SystemExit(f"[fe_pet_ml][FAIL] member {mid}: no seed_policy persisted; cannot verify realization")
sp = z["seed_policy"]
sp = json.loads(str(sp)) if sp.dtype.kind in "US" else sp.item()
got_e, got_s = int(sp["estimator_seed"]), int(sp["subsample_seed"])
if (got_e, got_s) != (est, sub):
    raise SystemExit(f"[fe_pet_ml][FAIL] member {mid}: realized seeds ({got_e},{got_s}) != requested ({est},{sub})")
print(f"[fe_pet_ml] member {mid} realized seed_policy CONFIRMED: estimator={got_e} subsample={got_s}")
print(f"[fe_pet_ml] member {mid} full realized policy: {json.dumps(sp, default=str)}")
PY

echo "[fe_pet_ml] member ${MID} COMPLETE $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
