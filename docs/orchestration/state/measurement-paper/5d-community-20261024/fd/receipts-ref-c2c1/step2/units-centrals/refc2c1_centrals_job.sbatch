#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 1: the three centrals, timed (REF-C2C1-BINDING-2.md ruling 2.2; code at
# M = 77d76cfc from the fresh clean clone, with -B). er, c2_central and c1_central run concurrently, one srun step each,
# `srun --exclusive -n1 -c 64 --mem=120G`, at OMP/MKL/OPENBLAS = 64/1/1 (NUMEXPR 1, as part B's re2_env.sh): each unit
# refuses (rc 4) unless its affinity is exactly 64 and those three variables match config.json e_r. The units read only
# the staged copies under the staging root (C-IN) and the repository; the c2 units dlopen config.json's libRooUnfold.so,
# whose full sha256 the connect checked. Their seconds price the replicas (part 2), which are submitted only if the
# projection is within the 12.5 cap. Porcelain, with --ignored, before and after. Writes only under <O>.
# Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
U="$O/units"; L="$O/logs-units"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1u] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1u] refusing: deploy HEAD is not M"; exit 2; }
[ ! -e "$U" ] || { echo "[c2c1u] refusing: $U exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1u] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1u] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1u] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[c2c1u] squeue cov2d-* at start: $(squeue -u josephrb -h -o '%i|%j|%T' | awk -F'|' '$2 ~ /^cov2d-/' | tr '\n' ' ')"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[c2c1u] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp-units" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" "$U"
echo "[c2c1u] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
pids=""
for u in er c2_central c1_central; do
  srun --exclusive -n1 -c 64 --mem=120G --job-name="$u" \
      /usr/bin/time -v -o "$L/$u.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py --unit "$u" --out "$U" \
      > "$L/$u.log" 2>&1 &
  pids="$pids $!"
done
rcs=""
for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1u] units done $(date -u +%FT%TZ); rcs:$rcs"
for u in er c2_central c1_central; do
  echo "[c2c1u] $u: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/$u.time" | tr -s ' \t' ' ' | tr '\n' ';')"
  tail -2 "$L/$u.log"
  [ -s "$U/$u.done" ] && echo "[c2c1u] $u.done: $(cat "$U/$u.done")"
done
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1u] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
pass=0; for u in er c2_central c1_central; do grep -q '"verdict": "PASS"' "$U/$u.done" 2>/dev/null && pass=$((pass + 1)); done
printf '{"job": "%s", "rcs": "%s", "pass_markers": %s, "porcelain_after": %s}\n' "$SLURM_JOB_ID" "${rcs# }" "$pass" "$na" > "$O/CENTRALS-DONE"
cat "$O/CENTRALS-DONE"
[ "$pass" = 3 ] && [ "$na" = 0 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
