#!/bin/bash
# Phase A2 CPU jobs: recompute the historical headline, test the data path, inventory features.
#
# MODE=recover    1. the COMMITTED report_campaign.py, from the clean 68cf9d29 checkout, guarded,
#                    in the environment the historical deliver job used (`module load python`),
#                    over the ORIGINAL campaign outputs -> recomputed_campaign_report.json
#                 2. a2_recover.py (this branch), guarded, importing the 68cf9d29 modules, under
#                    the TF module because the loader's engine package imports TensorFlow
# MODE=inventory  a2_feature_inventory.py (this branch), guarded, `module load python` (uproot)
#
# Nothing here trains, and nothing writes under the historical campaign directory.
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=220G
#SBATCH --time=04:00:00
#SBATCH --job-name=pet-a2
set -eo pipefail

: "${MODE:?recover|inventory}" ; : "${MINE:?}" ; : "${MINE_COMMIT:?}"
: "${PINNED:?}" ; : "${PINNED_COMMIT:?}" ; : "${OUT:?}"

for pair in "$MINE:$MINE_COMMIT" "$PINNED:$PINNED_COMMIT"; do
  tree=${pair%%:*}; want=${pair##*:}
  [[ "$(git -C "$tree" rev-parse HEAD)" == "$want" ]] || { echo "HEAD of $tree != $want" >&2; exit 2; }
  [[ -z "$(git -C "$tree" status --porcelain)" ]] || { echo "$tree is not clean" >&2; exit 2; }
done

CAMPAIGN=/pscratch/sd/j/josephrb/campaign-20260920
NPZ=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
RECEIPT=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12_RECEIPT.json
PROD=/pscratch/sd/j/josephrb/MINERvA-OmniFold
mkdir -p "$OUT/receipts" "$OUT/guard"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$MODE-$SLURM_JOB_ID.txt"

if [[ "$MODE" == recover ]]; then
  # The reference exactly as the historical deliver job passed it, read without a Python entrypoint.
  REF=$(sed -n 's/^    "aggregate": \([0-9.]*\),$/\1/p' \
        "$PINNED/nd-unfolding/pet/configuration_comparison/frozen_design.py")
  [[ "$REF" == 0.6949731568655361 ]] || { echo "unexpected frozen reference $REF" >&2; exit 2; }
  ( module load python
    cd "$PINNED"      # report_campaign records `git rev-parse HEAD` of the cwd as its commit
    python3 --version; python3 -c 'import numpy; print("numpy", numpy.__version__)'
    python3 "$PINNED/nd-unfolding/mnv_guarded_run.py" --expect-root "$PINNED" \
      --inventory "$OUT/guard/report-regen.jsonl" --label a2-report-regen -- \
      "$PINNED/nd-unfolding/pet/configuration_comparison/report_campaign.py" \
      --campaign "$CAMPAIGN" --closure-npz "$NPZ" --reference "$REF" \
      --output "$OUT/recomputed_campaign_report.json"
  )
  ( module load tensorflow/2.15.0
    cd "$OUT"
    python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" --allow "$PINNED" \
      --inventory "$OUT/guard/a2-recover.jsonl" --label a2-recover -- \
      "$MINE/nd-unfolding/pet/improvement_campaign/phase_a/a2_recover.py" \
      --comparison-root "$PINNED" --campaign "$CAMPAIGN" --closure-npz "$NPZ" \
      --identity-sidecar "$SIDECAR" --inventory-receipt "$RECEIPT" \
      --committed-report "$MINE/nd-unfolding/pet/configuration_comparison/campaign_report.json" \
      --recomputed-report "$OUT/recomputed_campaign_report.json" \
      --theirs-index "$CAMPAIGN/join" --production-root "$PROD" --outdir "$OUT/receipts"
  )
elif [[ "$MODE" == inventory ]]; then
  ( module load python
    cd "$OUT"
    python3 "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" --allow "$PINNED" \
      --inventory "$OUT/guard/a2-inventory.jsonl" --label a2-inventory -- \
      "$MINE/nd-unfolding/pet/improvement_campaign/phase_a/a2_feature_inventory.py" \
      --comparison-root "$PINNED" --closure-npz "$NPZ" --identity-sidecar "$SIDECAR" \
      --omnifile-3d "$PROD/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root" \
      --omnifile-g2-playlist "$PROD/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1L.root" \
      --omnifile-g2-merged "$PROD/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root" \
      --mc-manifest "$MINE/2d-unfolding/playlist_manifests/1A_MC.txt" \
      --data-manifest "$MINE/2d-unfolding/playlist_manifests/1A_Data.txt" \
      --r4-slim "$(ls /pscratch/sd/j/josephrb/r4slim/1A_MC/*.root | head -1)" \
      --theirs-shard "$(ls /pscratch/sd/j/josephrb/theirs_inputs/1A_MC/*.theirs.npz | head -1)" \
      --theirs-cache "$CAMPAIGN/cache/theirs-final.npz" \
      --final-weights "$CAMPAIGN/final/ours-seed127/weights/weights_ours_final_127.npz" \
      --outdir "$OUT/receipts"
  )
else
  echo "unknown MODE $MODE" >&2; exit 2
fi
echo "COMPLETE $MODE" > "$OUT/terminal-$MODE.txt"
