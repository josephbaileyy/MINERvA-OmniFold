#!/bin/bash
# Phase A2: decompose the masks_and_padding FAIL into its conjuncts. Reads only.
#SBATCH --account=m3246
#SBATCH --qos=debug
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=220G
#SBATCH --time=00:29:00
#SBATCH --job-name=pet-a2-mask
set -eo pipefail
MINE=/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/e39774e7
WANT=e39774e7c8e3195c8fcfea8750d909708dc6437d
OUT=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseA2/run3
[[ "$(git -C $MINE rev-parse HEAD)" == "$WANT" ]] || { echo 'HEAD mismatch' >&2; exit 2; }
[[ -z "$(git -C $MINE status --porcelain)" ]] || { echo 'not clean' >&2; exit 2; }
mkdir -p $OUT/receipts $OUT/guard
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
scontrol show job -o $SLURM_JOB_ID > $OUT/allocation-mask-$SLURM_JOB_ID.txt
module load python
cd $OUT
python3 $MINE/nd-unfolding/mnv_guarded_run.py --expect-root $MINE \
  --inventory $OUT/guard/a2-mask.jsonl --label a2-mask -- \
  $MINE/nd-unfolding/pet/improvement_campaign/phase_a/a2_mask_diagnose.py \
  --closure-npz /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz \
  --run-weights /pscratch/sd/j/josephrb/campaign-20260920/final/ours-seed127/weights/weights_ours_final_127.npz \
  --outdir $OUT/receipts
echo COMPLETE > $OUT/terminal-mask.txt
