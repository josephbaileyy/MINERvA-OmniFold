#!/bin/bash
# Task A1: are the three declared differences in his inputs what ran, and can
# they be resolved? Re-runs the historical builder on one MC shard in the ROOT
# environment the build used (setup_salloc_env.sh), through the unedited guard.
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --job-name=pa1-build
set -eo pipefail
: "${HIST:?}" ; : "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}"
HIST_COMMIT=68cf9d29f8ab1b0f5acd933d4baec1962b29e34d
HARDCODED=/pscratch/sd/j/josephrb/MINERvA-OmniFold
RUN=MasterAnaDev_mc_AnaTuple_run00110000_Playlist
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
for pair in "$HIST:$HIST_COMMIT" "$MINE:$MINE_COMMIT"; do
  dir=${pair%%:*}; want=${pair##*:}
  [[ "$(git -C "$dir" rev-parse HEAD)" == "$want" ]]
  [[ -z "$(git -C "$dir" status --porcelain)" ]]
done
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-build.txt"
git -C "$HIST" ls-tree -r HEAD > "$OUT/tree-68cf9d29-build.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
source "$HARDCODED/setup_salloc_env.sh" >/dev/null 2>&1 || true
cd "$OUT"
python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" --allow "$HIST" \
  --inventory "$OUT/guard-build.json" --label "A1-build-check" \
  -- "$MINE/nd-unfolding/pet/improvement_campaign/phase_a/check_theirs_build.py" \
  --historical-repo "$HIST" --tree-listing "$OUT/tree-68cf9d29-build.txt" \
  --executed-builder /pscratch/sd/j/josephrb/build_theirs_inputs.py \
  --executed-schema /pscratch/sd/j/josephrb/theirs_token_schema.py \
  --slim "/pscratch/sd/j/josephrb/r4slim/1A_MC/$RUN.slim.root" \
  --executed-shard "/pscratch/sd/j/josephrb/theirs_inputs/1A_MC/$RUN.theirs.npz" \
  --source-anatuple "/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/$RUN.root" \
  --limit 20000 --out "$OUT/theirs_build_check.json" > "$OUT/build-check.log" 2>&1
for dir in "$HIST" "$MINE"; do [[ -z "$(git -C "$dir" status --porcelain)" ]]; done
echo COMPLETE > "$OUT/terminal-build.txt"
