#!/bin/bash
#SBATCH --job-name=g6_leg0_tier
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --array=1-5
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/trajectory/logs/g6_leg0_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/trajectory/logs/g6_leg0_%A_%a.err
#
# Gate 6 Leg 0 -- TIER CALIBRATION.  Zero training, inference only.
#
# WHAT THIS MEASURES.  The Gate-6 monotonicity metric is read at iterations 0, 1, 2 from checkpoints
# of two different provenance tiers: best-epoch at 0 and 1, BEN-043 `_final` at 2 (the member
# inventory carries `_final` for iteration 2 only).  Member 3 FAILs on a +0.001098 rise at the one
# step that crosses that boundary, against a best-vs-final systematic BEN-043 measured at ~1.3% on a
# DIFFERENT quantity, the fold-forward ratio.  This array re-reads all five existing members forcing
# the whole trajectory to best-epoch, so the tier systematic is measured ON THE GATE-6 METRIC
# ITSELF.  Five samples, no training, no new estimator.
#
# WHAT IT DOES NOT DO, and these are constraints not commentary:
#   * Member 3 is NOT promoted, selected, or removed.  The family still blocks on 2, 4 and 5.
#   * No C_ML is constructed.  No member selection.  No central move.  No Leg 2, no Leg X.
#   * All five Gate-6 prohibitions at 19585b7 stay live; nothing here clears any of them.
#   * The only thing this can change is the FAULT DESCRIPTION the retry has to explain: whether the
#     family has three real failures or four.
#
# WHY A NEW LAUNCHER RATHER THAN A FLAG ON sbatch_gate6_member_trajectory_array.sh.  That launcher's
# bytes are frozen by an active run receipt -- `gate6-trajectory-array-active-56847059.json` binds it
# at sha 13a598f2 -- and `sbatch_pet_fullevent_floor_replicate_array.sh` is likewise bound by
# `gate6-floor-replication-active-56863958.json` at b0308f24.  Both were edited in place first and
# `verify_hash_bindings.py` refused them, correctly: its docstring says a stale pin "is not repaired
# by editing the hash... Re-issue the owning gate and record the move," and those two receipts record
# what actually ran.  Rewriting them to accommodate a downstream code change would falsify submit-time
# provenance of two COMPLETED runs.  So no existing launcher is touched, and this file carries the new
# pin instead -- the same "why a new launcher" reasoning sbatch_pet_fullevent_ml_ensemble.sh sets.
#
# CONSEQUENCE FOR THE CODE TREE, which is the whole reason for G6_LEG0_CODE_REPO.  The three existing
# launchers pin step1_increment_trajectory.py at 48f8353d and read it out of
# /pscratch/sd/j/josephrb/gate6-reconcile-56834281.  That pin is CORRECT for that tree and must stay
# correct: syncing the flag-carrying file into it would break the trajectory, floor-replicate and
# legx launchers all at once.  Leg 0 therefore runs from its OWN checkout, and gate6-reconcile-56834281
# is left byte-identical.  Point G6_LEG0_CODE_REPO at a tree holding the commit that added
# --checkpoint-tier; the pins below fail closed if it does not.
set -eo pipefail

die() { echo "[g6-leg0] FATAL: $*" >&2; exit 64; }

TASK="${SLURM_ARRAY_TASK_ID:-}"
[[ "$TASK" =~ ^[1-5]$ ]] || die "array task must be 1..5, got ${TASK:-<unset>}"
[[ "${SLURM_NTASKS:-1}" == "1" ]] || die "launcher is single-rank"

# Hardcoded, not parameterised.  `auto` would reproduce 56847059 and measure nothing; `final` cannot
# be satisfied at iterations 0 and 1, which have no _final checkpoint.  best-epoch is the only tier
# that yields a contrast, so making it an option would only create a way to run the wrong arm.
TRAJ_TIER="best-epoch"

SCI_REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CODE_REPO="${G6_LEG0_CODE_REPO:?set G6_LEG0_CODE_REPO to a checkout carrying the --checkpoint-tier commit; gate6-reconcile-56834281 must NOT be used, its pins bind the pre-flag file}"
CODE_PET="${CODE_REPO}/nd-unfolding/pet"
SCI_PET="${SCI_REPO}/nd-unfolding/pet"
MEMBER_DIR="${SCI_PET}/fullevent_ml_ensemble/member_${TASK}"
ARTIFACT="${MEMBER_DIR}/pet_fullevent_ml_member${TASK}_weights.npz"
DONE="${ARTIFACT}.done"
TARGET="${SCI_REPO}/nd-unfolding/g2_fullevent/gate2/final/superseded-20260813-pre-gate5-rerun/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
TARGET_SHA="544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9"
RUN_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-nojob}}_${TASK}"
OUT_DIR="${MEMBER_DIR}/trajectory"
# The tier goes in the FILENAME, not only in the JSON body.  A bare
# STEP1_TRAJECTORY.slurm-<id>.json sitting beside the committed 56847059 receipts is
# indistinguishable from them by name, and the entire point of this leg is that the two readings are
# NOT interchangeable.
GATE="${OUT_DIR}/GATE_AB_PUSH_PROVENANCE.slurm-${RUN_ID}.leg0-tier-${TRAJ_TIER}.json"
DECOMP="${OUT_DIR}/STEP1_DECOMPOSITION.slurm-${RUN_ID}.leg0-tier-${TRAJ_TIER}.json"
TRAJ="${OUT_DIR}/STEP1_TRAJECTORY.slurm-${RUN_ID}.leg0-tier-${TRAJ_TIER}.json"
LOCK="${OUT_DIR}/.writer-leg0-${RUN_ID}.lock"

mkdir -p "$OUT_DIR"
exec 9>"$LOCK"
flock -n 9 || die "writer lock is already held: $LOCK"
for output in "$GATE" "$DECOMP" "$TRAJ"; do
  [[ ! -e "$output" ]] || die "refusing to overwrite $output"
done
[[ -f "$ARTIFACT" && -f "$DONE" ]] || die "member ${TASK} artifact/done pair incomplete"
[[ -f "$TARGET" ]] || die "archived target is absent: $TARGET"

# The frozen trees must stay frozen: refuse to run out of either even if one is exported explicitly.
# Both the raw and the canonicalized value are tested, and an unresolvable canonicalization falls
# back to the raw string rather than to the empty string -- `readlink -f` on a path that does not
# exist prints nothing on some platforms, and a case over "" matches no pattern, so testing the
# canonical form alone would make this guard fail OPEN in exactly the situation it is meant to catch.
CODE_REPO_CANON="$(readlink -f "$CODE_REPO" 2>/dev/null || true)"
[[ -n "$CODE_REPO_CANON" ]] || CODE_REPO_CANON="$CODE_REPO"
for candidate in "$CODE_REPO" "$CODE_REPO_CANON"; do
  case "${candidate%/}" in
    */gate6-reconcile-56834281|*/gate6traj-reconcile-56847059)
      die "CODE_REPO $CODE_REPO resolves to a frozen tree ($candidate); Leg 0 must run from its own checkout" ;;
  esac
done

# Same member artifact hashes the 56847059 array asserted.  Restated rather than sourced: this leg's
# whole claim is that it read the SAME five members, and a shared file could move under both.
case "$TASK" in
  1) ARTIFACT_SHA="3e08850d44f773bb50f5cb132a7a1d4d672e0ab15f1d38d785a4eddbf5179b2e" ;;
  2) ARTIFACT_SHA="5b8e129f9dba90659ed0fc17f322499ea41fea505add57ab957ad209152f1c13" ;;
  3) ARTIFACT_SHA="f6087581e320d1bfce1a968e62c737d8fac346dedb94836f7fe173980a5b55e8" ;;
  4) ARTIFACT_SHA="04759d0a07f120bda112b87222b0a91fd0e98a2ce402be12d37f30d06a2a0bfd" ;;
  5) ARTIFACT_SHA="4120a5483255847e9dceb79dc5796dd820fca419cfba8adddabc42924d82eff1" ;;
esac
[[ "$(sha256sum "$ARTIFACT" | awk '{print $1}')" == "$ARTIFACT_SHA" ]] || die "artifact hash mismatch"
[[ "$(sha256sum "$TARGET" | awk '{print $1}')" == "$TARGET_SHA" ]] || die "archived target hash mismatch"

# Identical to the 56847059 pin set except step1_increment_trajectory.py, which moves
# 48f8353d -> ca2128ac for the --checkpoint-tier flag.  Everything else is byte-for-byte the code
# that produced the committed readings, which is what makes the two arms comparable.
declare -A CODE_SHA=(
  [diagnostic_target_override.py]="3f2ee2d2dc39c58c0ba71dc85ad1560ecab7166082ce418864701a6f5ee78671"
  [gate_ab_push_provenance.py]="fd181aeba1e43b4ddfe6fc257f7ce39dc95b74834fee16feb9caf72d313d6c95"
  [step1_pull_push_decomposition.py]="175edde3860da313cf07024514922a0b1a89fb802aaaa94abdf120674f92fabe"
  [step1_increment_trajectory.py]="ca2128aca2a7226720e0ce3c878f9937d129cc6a260f88750308de97cafeaf3c"
  [train_fullevent_nominal.py]="91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc"
  [fullevent_fps_dataloader.py]="e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1"
  [extract_fullevent_fps.py]="de0f044b612782edb58e152205b426e6dbbca7637b7f3f342a1373fe4dc7d51a"
)
for file in "${!CODE_SHA[@]}"; do
  [[ "$(sha256sum "${CODE_PET}/${file}" | awk '{print $1}')" == "${CODE_SHA[$file]}" ]] || die "code hash mismatch: $file"
done
[[ "$(sha256sum "${CODE_REPO}/omnifold_nn/omnifold/omnifold.py" | awk '{print $1}')" == "3a2022b0809fa457acb03bcc4c76fd97954061d3253c3f9d753316a3b54de9aa" ]] || die "engine hash mismatch"

module load tensorflow/2.15.0
export PYTHONUNBUFFERED=1
export MNV_REPO="$SCI_REPO"
export PYTHONPATH="${CODE_REPO}/omnifold_nn:${CODE_REPO}/nd-unfolding:${CODE_PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$CODE_PET"

# Fail before model construction unless the artifact resolves to this task's isolated 3-iteration,
# eight-checkpoint namespace -- and, for this leg specifically, unless the six best-epoch files the
# forced tier is about to read are all present.  Without that second check a missing best-epoch file
# would surface as a mid-run SystemExit after ~10 minutes of GPU time.
python3 -u - "$ARTIFACT" "$MEMBER_DIR" "$TASK" <<'PYEOF'
import json, os, sys
import numpy as np
artifact, member_dir, task = sys.argv[1:]
with np.load(artifact, allow_pickle=True) as data:
    contract = data["inference_contract"].item()
    policy = data["seed_policy"].item()
folder = os.path.realpath(contract["weights_folder"])
expected_folder = os.path.realpath(os.path.join(member_dir, "w_nominal"))
if folder != expected_folder:
    raise SystemExit(f"weights_folder collision: {folder} != {expected_folder}")
if int(policy["niter"]) != 3:
    raise SystemExit(f"niter changed: {policy['niter']}")
name = contract["multifold_name"]
best = [f"OmniFold_{name}_iter{i}_step{s}.weights.h5" for i in range(3) for s in (1, 2)]
expected = sorted(best + [f"OmniFold_{name}_iter2_step{s}_final.weights.h5" for s in (1, 2)])
actual = sorted(x for x in os.listdir(folder) if x.endswith(".weights.h5"))
if actual != expected:
    raise SystemExit(f"checkpoint inventory mismatch: {actual}")
missing = [b for b in best if not os.path.exists(os.path.join(folder, b))]
if missing:
    raise SystemExit(f"best-epoch tier requested but these are absent: {missing}")
print(json.dumps({"member": int(task), "weights_folder": folder,
                  "checkpoint_count": len(actual), "best_epoch_available": len(best),
                  "checkpoint_tier": "best-epoch", "preflight": "PASS"}, sort_keys=True))
PYEOF

echo "[g6-leg0] member=${TASK} run_id=${RUN_ID} tier=${TRAJ_TIER} code_repo=${CODE_REPO} host=$(hostname) start=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
python3 -u gate_ab_push_provenance.py \
  --artifact "$ARTIFACT" --json "$GATE" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
# gate_ab_push_provenance.py and step1_pull_push_decomposition.py are NOT tier-aware and still read
# `_final` at iteration 2.  So the trajectory's own reproduction gate below becomes a CROSS-TIER
# comparison, deliberately: it turns the gate block into a direct readout of the tier systematic,
# with push_prev (iteration 1, best-epoch in both arms) as a tier-invariant null control that must
# still reproduce to ~0.  A gate MISMATCH here is a measurement of a large gap, not an environment
# defect -- REPRO_RTOL is not relaxed for it, and the GATE_FAILED receipt carries R, the tier and the
# per-checkpoint provenance so |push_final/R - 1| stays derivable even then.
python3 -u step1_pull_push_decomposition.py \
  --artifact "$ARTIFACT" --gate-receipt "$GATE" --json "$DECOMP" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
python3 -u step1_increment_trajectory.py \
  --weights "$ARTIFACT" --decomposition-receipt "$DECOMP" --json "$TRAJ" \
  --checkpoint-tier "$TRAJ_TIER" \
  --precomputed-target-override "$TARGET" \
  --precomputed-target-sha256 "$TARGET_SHA"
echo "[g6-leg0] member=${TASK} rc=0 tier=${TRAJ_TIER} trajectory=${TRAJ} end=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
