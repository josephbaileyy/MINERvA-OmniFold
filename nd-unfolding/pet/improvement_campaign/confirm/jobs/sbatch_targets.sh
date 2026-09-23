#!/bin/bash
# CPU job: population targets for a list of "POOL DISTORTION OUTDIR" specs (TARGETS, ';'-separated)
# before the runs that need them finish, plus the campaign tests at this commit.
#   env: MINE MINE_COMMIT LOG TARGETS
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pv1-targets
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${LOG:?}" ; : "${TARGETS:?}"
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
MANIFEST=unused OUT=/dev/null
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
mkdir -p "$LOG"
( cd "$V" && python "$GUARD" --expect-root "$MINE" --inventory "$LOG/guard-pytest.json" --label V1-pytest -- \
    "$C/phase_a/run_pytest.py" -q test_confirm.py ../test_authorization_scope.py -p no:cacheprovider ) \
    > "$LOG/pytest.log" 2>&1 &
IFS=';' read -r -a SPECS <<< "$TARGETS"
for spec in "${SPECS[@]}"; do
  read -r pool dist out <<< "$spec"
  OUT=$out ensure_target "$pool" "$dist" &
done
wait
