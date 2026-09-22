#!/bin/bash
# Task A1: every campaign test (non-TF and TF) from a pinned checkout, through the guard.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pa1-tests
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-tests.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES="" TF_CPP_MIN_LOG_LEVEL=2
module load tensorflow/2.15.0
cd "$OUT"
C="$MINE/nd-unfolding/pet/improvement_campaign"
python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
  --inventory "$OUT/guard-tests.json" --label "A1-tests" \
  -- "$C/phase_a/run_pytest.py" -q -rxXs -p no:cacheprovider --junitxml "$OUT/junit.xml" \
  "$C/test_recipe.py" "$C/test_authorization_scope.py" "$C/test_feature_arms.py" \
  "$C/test_confirmed_defects.py" > "$OUT/pytest.log" 2>&1 || echo "pytest exit $?" >> "$OUT/pytest.log"
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
echo COMPLETE > "$OUT/terminal-tests.txt"
