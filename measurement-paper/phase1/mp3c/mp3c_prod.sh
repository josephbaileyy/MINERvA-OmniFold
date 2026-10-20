#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J mp3cprod
#SBATCH -o /pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/logs/mp3cprod-%j.out
# MP3-C production: every TASK line of SEEDS.txt is one GiBUU 2019 free-proton run (the declared H card, its own
# seed), as sbatch_gibuu_mefhc.sh runs a C12 task; all tasks run concurrently on this one node, each exactly once.
# A task that does not exit 0 is DISCARDED WHOLE (FinalEvents.dat renamed .discarded) and recorded. Then the
# MP3-C pipeline: mp3c_build.py (C0, C1', B1, B2, B3'), mp3c_eval.py (B4 gating, readout, beside-A7 replay).
# Writes only under $D. No set -u. Absolute paths.
set -o pipefail
D=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c
G=/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie
S5P=/pscratch/sd/j/josephrb/s5p-20260926
JOB=$G/work_gibuu/gibuu_mefhc_numu.job
SEEDS=$D/code/SEEDS.txt
[ -e "$D/prod" ] || [ -e "$D/out" ] && { echo "STOP: $D/prod or $D/out exists"; exit 2; }
mkdir -p "$D/prod" "$D/out" "$D/tmp" || exit 2
mapfile -t TASKS < <(awk '$1=="TASK" {print $2, $3}' "$SEEDS")
echo "host $(hostname) start $(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} tasks ${#TASKS[@]} SEEDS $(sha256sum "$SEEDS" | cut -c1-64)"
[ ${#TASKS[@]} -gt 0 ] || { echo "STOP: no TASK lines"; exit 2; }
sha256sum "$JOB" "$G/setup_gibuu.sh" "$D"/code/* "$D"/inputs/* > "$D/prod/input_sha256.txt"; cat "$D/prod/input_sha256.txt"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"   # GiBUU.x's ROOT needs the env's C++ toolchain on PATH (60029251)
unset PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1
task() {  # N SEED
  local N=$1 SEED=$2 W=$D/prod/task$1 rc
  mkdir -p "$W" || return 2
  python3 -B "$D/code/mp3c_card.py" write "$JOB" "$SEED" "$W/task.job" || return 2
  python3 -B "$D/code/mp3c_card.py" check "$JOB" "$SEED" "$W/task.job" > "$W/c0.json" || return 2
  ( export OMP_NUM_THREADS=${GIBUU_OMP:-16}; source "$G/setup_gibuu.sh" > "$W/setup.log"; cd "$W" || exit 2
    /usr/bin/time -v "$GIBUU_BIN" < task.job > gibuu.log 2> time.txt )
  rc=$?
  echo "$N $SEED $rc" > "$W/RESULT"
  # keep what the C12 task directories keep (FinalEvents.dat) plus the card, logs and receipts; GiBUU's ~1.5k
  # analysis files (~1.6 GB per task) are not used by the chain
  find "$W" -maxdepth 1 -type f ! -name FinalEvents.dat ! -name task.job ! -name gibuu.log ! -name time.txt \
    ! -name setup.log ! -name c0.json ! -name RESULT -delete
  if [ $rc != 0 ]; then [ -e "$W/FinalEvents.dat" ] && mv "$W/FinalEvents.dat" "$W/FinalEvents.dat.discarded"; fi
  return 0
}
pids=()
for t in "${TASKS[@]}"; do read -r n s <<< "$t"; ( task "$n" "$s" ) & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; done
echo "GEN done $(date -u +%FT%TZ)"
cat "$D"/prod/task*/RESULT | awk '{n++; if ($3==0) ok++; else bad=bad" "$1"(rc="$3")"} END {print "tasks", n, "ok", ok+0, "discarded:" bad}'
sha256sum "$D"/prod/task*/FinalEvents.dat > "$D/prod/output_sha256.txt" 2>/dev/null
grep -h -E "Elapsed|Maximum resident|Percent of CPU" "$D"/prod/task*/time.txt | sort | uniq -c | sort -rn | head -6
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 TMPDIR=$D/tmp
mkdir -p "$D/run"; cd "$D/run" || exit 2
python3 "$D/code/mp3c_build.py" --out "$D/out/build" --h-glob "$D/prod/task*/FinalEvents.dat" --frozen-jobcard "$JOB" \
  --seeds "$SEEDS" --nproc 96
rb=$?; echo "BUILD rc=$rb $(date -u +%FT%TZ)"
re=skipped
if [ $rb = 0 ]; then
  python3 "$D/code/mp3c_eval.py" --design "$D/inputs/design.json" --s5c-contract "$D/inputs/s5c_contract.json" \
    --v "$S5P/stage3/V/V-s3v.npz" --frozen-eval "$D/inputs/joint-evaluate.json" --build-dir "$D/out/build" \
    --out "$D/out/eval" --fine mp3c_fine_gibuu.npz --variant "GiBUU-on-CH (GiBUU C12 frozen + GiBUU free proton)" \
    --b4-gating yes --null-key GiBUU_2019
  re=$?
fi
echo "EVAL rc=$re end $(date -u +%FT%TZ)"
[ "$rb" = 0 ] && [ "$re" = 0 ]
