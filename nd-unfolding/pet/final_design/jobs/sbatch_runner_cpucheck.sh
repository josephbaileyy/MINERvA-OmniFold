#!/bin/bash
# CPU checks of the study runner on the REAL inventory (no training, no GPU):
#   PART=parity   the runner tests (incl. the design_lib.sh shell test, bash >= 4 here) and the
#                 predecessor-selection parity: run_replicate.py and run_design.py --inputs-only on
#                 the same predecessor replicate, compared member by member;
#   PART=bank     run_design.py --inputs-only on a DEV bank draw (null distortion, one bootstrap
#                 member) with the committed bank manifest and $BANKS.
#   env: MINE MINE_COMMIT OUT PART [SEL=T:0] [CFG=<config rel. to confirm/configs>] [BANKS]
#   submit: sbatch -A m3246 -C cpu -q shared -c 4 --mem=40G -t 00:45:00 --export=ALL,... this
#SBATCH --job-name=pfd-runner-cpu
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${PART:?}"
case "$(realpath -m "$OUT")" in
  /pscratch/sd/j/josephrb/pet-final-design-20260925/impl-runner/*) ;;
  *) echo "OUT must be under the impl-runner study area" >&2; exit 2;;
esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]] || { echo "checkout not at $MINE_COMMIT" >&2; exit 2; }
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "checkout not clean" >&2; exit 2; }
mkdir -p "$OUT"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
POOLS=/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz
POPULATIONS=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
BANKS="${BANKS:-/pscratch/sd/j/josephrb/pet-final-design-20260925/impl-runner/banks/banks.npz}"
C="$MINE/nd-unfolding/pet/improvement_campaign"; V="$C/confirm"
STUDY="$MINE/nd-unfolding/pet/final_design"; D="$STUDY/runner"
G=(python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE")
CFG="${CFG:-../../final_design/configs/dev1/dev1-H1-T0-D1_p0.350.json}"
HASH=$(python -c "import sys; sys.path.insert(0, '$C'); from recipe import RunConfig; print(RunConfig.from_json(open('$V/configs/$CFG').read()).content_hash())")
SEL="${SEL:-T:0}"
COMMON=(--config "$V/configs/$CFG" --config-hash "$HASH" --repo "$MINE" --inputs-npz "$INPUTS"
        --identity-sidecar "$SIDECAR" --populations "$POPULATIONS" --inputs-only)
status=0
echo "$(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} host $(hostname) part $PART commit $MINE_COMMIT" >> "$OUT/cpucheck.log"
if [[ "$PART" == parity ]]; then
  ( cd "$STUDY" && "${G[@]}" --inventory "$OUT/guard-pytest.json" --label PFD-pytest -- \
      "$C/phase_a/run_pytest.py" -q -p no:cacheprovider --basetemp="$OUT/pytest-tmp" \
      runner/test_run_design.py banks/test_build_banks.py -rs ) > "$OUT/pytest.log" 2>&1 || status=1
  POOLARGS=(--pool "${SEL%%:*}" --replicate "${SEL##*:}" --pools-npz "$POOLS"
            --manifest "$C/pools/POOL_MANIFEST.json" --distortion dev)
  /usr/bin/time -v "${G[@]}" --inventory "$OUT/guard-pred.json" --label PFD-parity-pred -- \
    "$V/run_replicate.py" "${COMMON[@]}" --out "$OUT/pred" "${POOLARGS[@]}" \
    > "$OUT/pred.log" 2>&1 || status=1
  /usr/bin/time -v "${G[@]}" --inventory "$OUT/guard-study.json" --label PFD-parity-study -- \
    "$D/run_design.py" "${COMMON[@]}" --out "$OUT/study" "${POOLARGS[@]}" \
    > "$OUT/study.log" 2>&1 || status=1
  "${G[@]}" --inventory "$OUT/guard-compare.json" --label PFD-parity-compare -- \
    "$D/compare_inputs_runs.py" --predecessor "$OUT/pred" --study "$OUT/study" \
    --output "$OUT/parity.json" > "$OUT/compare.log" 2>&1 || status=1
elif [[ "$PART" == bank ]]; then
  /usr/bin/time -v "${G[@]}" --inventory "$OUT/guard-bank.json" --label PFD-bankdraw -- \
    "$D/run_design.py" "${COMMON[@]}" --out "$OUT/bank-dev-null-b1" \
    --bank-draw "${BANK_DRAW:-cpucheck:0}" --pseudo-bank DEV --banks-npz "$BANKS" \
    --distortion null --bootstrap-member 1 --bootstrap-seed 20260925 \
    > "$OUT/bank.log" 2>&1 || status=1
else
  echo "unknown PART $PART" >&2; exit 2
fi
echo "$(date -u +%FT%TZ) status $status" >> "$OUT/cpucheck.log"
exit $status
