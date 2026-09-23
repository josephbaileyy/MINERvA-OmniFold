#!/bin/bash
# V1 CPU check on the REAL inventory, before any GPU time: the perlmutter-only tests, the input
# path with the historical halves forced in (byte-compared with closure_data.build_closure_inputs),
# one pool-S replicate's inputs, and the pool-S population target. No training.
#   env: MINE MINE_COMMIT OUT
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pv1-cpucheck
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
POOLS=/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz
POPULATIONS=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
case "$(realpath -m "$OUT")" in /pscratch/sd/j/josephrb/campaign-20260920*) exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
C="$MINE/nd-unfolding/pet/improvement_campaign"; V="$C/confirm"
G=(python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE")
CFG="$V/configs/v1ctl-H-K3-s1.json"; H=$(awk -F'\t' '$1=="v1ctl-H-K3-s1"{print $3}' "$V/runs/v1-infrastructure.tsv")
CFG2="$V/configs/v1mech-H-K2-s1.json"; H2=$(awk -F'\t' '$1=="v1mech-S0-H-K2-s1"{print $3}' "$V/runs/v1-infrastructure.tsv")
status=0
( cd "$V" && "${G[@]}" --inventory "$OUT/guard-pytest.json" --label V1-pytest -- \
    "$C/phase_a/run_pytest.py" -q test_confirm.py ../test_authorization_scope.py -p no:cacheprovider ) \
    > "$OUT/pytest.log" 2>&1 || status=1
/usr/bin/time -v "${G[@]}" --inventory "$OUT/guard-hist.json" --label V1-inputs-hist -- \
  "$V/run_replicate.py" --config "$CFG" --config-hash "$H" --repo "$MINE" --out "$OUT/hist" \
  --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" --populations "$POPULATIONS" \
  --historical-halves --crosscheck-closure-data --inputs-only > "$OUT/hist.log" 2>&1 || status=1
/usr/bin/time -v "${G[@]}" --inventory "$OUT/guard-s0.json" --label V1-inputs-s0 -- \
  "$V/run_replicate.py" --config "$CFG2" --config-hash "$H2" --repo "$MINE" --out "$OUT/s0" \
  --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" --populations "$POPULATIONS" \
  --pool S --replicate 0 --pools-npz "$POOLS" --manifest "$C/pools/POOL_MANIFEST.json" \
  --inputs-only > "$OUT/s0.log" 2>&1 || status=1
"${G[@]}" --inventory "$OUT/guard-target.json" --label V1-target -- "$V/population_target.py" \
  --pool S --distortion dev --inputs-npz "$INPUTS" --pools-npz "$POOLS" \
  --manifest "$C/pools/POOL_MANIFEST.json" --populations "$POPULATIONS" \
  --output "$OUT/targets/S-dev.json" > "$OUT/target.log" 2>&1 || status=1
echo "status $status" > "$OUT/status.txt"
exit $status
