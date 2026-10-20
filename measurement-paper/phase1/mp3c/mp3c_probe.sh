#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:20:00
#SBATCH -J mp3cprobe
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/logs/mp3cprobe-%j.out
# MP3-C probe: ONE GiBUU 2019 task on a free proton (the frozen C12 production jobcard with only target_Z/A = 1,
# include2p2hQE = F, numEnsembles x12; seed declared in SEEDS.txt), run as sbatch_gibuu_mefhc.sh runs a C12 task
# (setup_gibuu.sh, the short input mirror, OMP_NUM_THREADS=16). Then the probe readout against frozen C12 task1.
# Writes only under $D. No set -u. Absolute paths.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
JOB=$G/work_gibuu/gibuu_mefhc_numu.job
W=$D/probe/task1000
[ -e "$W" ] && { echo "STOP: $W exists"; exit 2; }
mkdir -p "$W" || exit 2
SEED=$(awk '$1=="PROBE" && $2=="1000" {print $3}' "$D/code/SEEDS.txt")
[ "$SEED" = 7931345 ] || { echo "STOP: probe seed not declared"; exit 2; }
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} seed $SEED"
sha256sum "$JOB" "$G/setup_gibuu.sh" "$D"/code/* "$G/work_gibuu_arr/task1/FinalEvents.dat"
python3 -B "$D/code/mp3c_card.py" write "$JOB" "$SEED" "$W/task.job" || exit 2
python3 -B "$D/code/mp3c_card.py" check "$JOB" "$SEED" "$W/task.job" || { echo "STOP: C0 card check failed"; exit 2; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"   # GiBUU.x's ROOT (cling) needs the env's C++ toolchain on PATH:
                                               # without it GiBUU segfaults at start (job 60029251, C12 card too)
(
  export OMP_NUM_THREADS=16
  source "$G/setup_gibuu.sh"
  cd "$W" || exit 2
  /usr/bin/time -v "$GIBUU_BIN" < task.job > gibuu.log 2> time.txt
)
rc=$?
echo "GIBUU rc=$rc $(date -u +%FT%TZ)"
ls -la "$W"; grep -iE "error|STOP|traceback" "$W/gibuu.log" | head -5
[ -s "$W/FinalEvents.dat" ] || { echo "STOP: no FinalEvents.dat"; exit 3; }
sha256sum "$W/FinalEvents.dat"
python3 -B "$D/code/mp3c_probe.py" "$W/FinalEvents.dat" "$G/work_gibuu_arr/task1/FinalEvents.dat" "$W/time.txt" "$D/probe/probe.json"
echo "PROBE rc=$? end $(date -u +%FT%TZ)"
