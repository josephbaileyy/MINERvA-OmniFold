#!/bin/bash
#SBATCH --job-name=gibuu_mefhc
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=00:45:00
#SBATCH --array=1-80%40
#SBATCH --output=gibuu_mefhc_%a_%A.out
#SBATCH --error=gibuu_mefhc_%a_%A.err

# GiBUU 2019 (NOvA CVMFS, native) MINERvA ME FHC nu_mu CC generation.
# Each array task is one independent GiBUU run (numEnsembles=4000,
# num_runs_SameEnergy=1) with a UNIQUE random seed -> work_gibuu_arr/task<N>/
# FinalEvents.dat. ~24k events / ~11.6k in-PS per task (~7 min); 80 tasks ->
# ~0.9M in-PS, comparable to the GENIE/NuWro samples. Combine all FinalEvents.dat
# with gibuu_to_xsec3d.py (divides by the number of files = runs).
#
# perweight already includes 1/numEnsembles, so each run's sum(perweight) is a
# full sigma estimate; averaging over runs = dividing by N files (the converter
# does this). Keep num_runs_SameEnergy=1 so that statement stays exact.

set -eo pipefail
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-16}

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
G=$REPO/3d-unfolding/genie
source "$G/setup_gibuu.sh"

N=${SLURM_ARRAY_TASK_ID}
SEED=$(( N * 7919 + 12345 ))
WORK="$G/work_gibuu_arr/task${N}"
SHORT_INPUT=/pscratch/sd/j/josephrb/gbi          # short path -> buuinput_local (avoids GiBUU filename truncation)
OUT="$WORK/FinalEvents.dat"

if [[ -s "$OUT" ]]; then echo "[gibuu] SKIP task $N: $OUT exists"; exit 0; fi
mkdir -p "$WORK"; cd "$WORK"

# per-task jobcard: base ME jobcard + a unique &initRandom seed prepended
{
  echo "&initRandom"
  echo "      SEED=${SEED}"
  echo "/"
  cat "$G/work_gibuu/gibuu_mefhc_numu.job"
} > task.job
# ensure path_to_input points at the short writable mirror
sed -i "s|path_to_input='[^']*'|path_to_input='${SHORT_INPUT}'|" task.job

echo "[gibuu] task $N seed=$SEED node=$(hostname) start $(date -u '+%F %T UTC')"
"$GIBUU_BIN" < task.job > gibuu.log 2>&1
RC=$?
echo "[gibuu] task $N rc=$RC end $(date -u '+%F %T UTC')"
grep -iE "error opening|Directory does not|STOP:" gibuu.log | head -3 || true
ls -la "$OUT" 2>/dev/null && grep -vc '^#' "$OUT"
