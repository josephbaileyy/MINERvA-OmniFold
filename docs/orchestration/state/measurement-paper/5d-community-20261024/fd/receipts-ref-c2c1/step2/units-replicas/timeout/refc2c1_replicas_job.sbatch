#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas, one of 4 single-node jobs (REF-C2C1-BINDING-2.md
# ruling 2.2; the director's ruling of 2026-11-06 on the centrals and the fence; code at M = 77d76cfc from the fresh
# clean clone, with -B). This job runs its 4 lanes of lanes.tsv (column 1 = <J>) concurrently, one srun step per lane,
# `srun --exclusive -n1 -c 64 --mem=120G`, each lane one process running its units in order, at OMP/MKL/OPENBLAS =
# 64/1/1 (NUMEXPR 1, as part B): each unit refuses (rc 4) unless its affinity is exactly 64 and those three variables
# match config.json e_r. The units read only the staged copies (C-IN) and the repository; the c2 units dlopen
# config.json's libRooUnfold.so, whose full sha256 the connect checked. The fence is a recorded line: the full squeue
# at the start. The 303 COV2D inputs (cov2d-watch-paths.txt) are stat'd (no read) before and after; a moved atime is
# a STOP. Porcelain, with --ignored, before and after. Writes only under <O>. Arguments: <deploy> <O> <J>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"; J="${3:?job index}"
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
U="$O/units"; L="$O/logs-replicas"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1r$J] refusing: O is $O"; exit 2; }
case "$J" in 0|1|2|3) ;; *) echo "[c2c1r] refusing: job index $J"; exit 2;; esac
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1r$J] refusing: deploy HEAD is not M"; exit 2; }
[ -s "$L/lanes.tsv" ] && [ -s "$L/cov2d-watch-paths.txt" ] && [ -d "$U" ] || { echo "[c2c1r$J] refusing: lanes, watch list or units missing"; exit 2; }
[ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "[c2c1r$J] refusing: REPLICAS-DONE-j$J exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1r$J] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1r$J] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[c2c1r$J] fence, recorded (the director's ruling: guarded readers record, not refuse): squeue -u josephrb:"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed "s/^/[c2c1r$J]   /"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-before.txt" 2>&1
echo "[c2c1r$J] COV2D inputs stat'd before: $(wc -l < "$L/j$J-watch-before.txt")"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[c2c1r$J] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp-replicas-j$J" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR"
echo "[c2c1r$J] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
pids=""; n=0
for l in 0 1 2 3; do
  args=(); while IFS=$'\t' read -r jj ll u; do [ "$jj" = "$J" ] && [ "$ll" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$L/lanes.tsv")
  n=$((n + ${#args[@]} / 2))
  echo "[c2c1r$J] lane $l: $(( ${#args[@]} / 2 )) units"
  srun --exclusive -n1 -c 64 --mem=120G --job-name="r$J-l$l" \
      /usr/bin/time -v -o "$L/j$J-lane$l.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py "${args[@]}" --out "$U" \
      > "$L/j$J-lane$l.log" 2>&1 &
  pids="$pids $!"
done
rcs=""; for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1r$J] lanes done $(date -u +%FT%TZ); rcs:$rcs"
for l in 0 1 2 3; do
  echo "[c2c1r$J] lane $l: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/j$J-lane$l.time" | tr -s ' \t' ' ' | tr '\n' ';')"
done
pass=0; for u in $(grep -v '^#' "$L/lanes.tsv" | awk -F'\t' -v j="$J" '$1 == j {print $3}'); do
  name=$(echo "$u" | sed 's/:\(.*\)/_b\1/'); grep -q '"verdict": "PASS"' "$U/$name.done" 2>/dev/null && pass=$((pass + 1))
done
echo "[c2c1r$J] PASS markers: $pass of $n"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-after.txt" 2>&1
if cmp -s "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt"; then moved=0; echo "[c2c1r$J] COV2D inputs: no atime moved"
else moved=1; echo "[c2c1r$J] STOP: a COV2D input's atime moved:"; diff "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
printf '{"job": "%s", "index": %s, "units": %s, "pass_markers": %s, "rcs": "%s", "watch_moved": %s, "porcelain_after": %s}\n' \
    "$SLURM_JOB_ID" "$J" "$n" "$pass" "${rcs# }" "$moved" "$na" > "$O/REPLICAS-DONE-j$J"
cat "$O/REPLICAS-DONE-j$J"
[ "$pass" = "$n" ] && [ "$moved" = 0 ] && [ "$na" = 0 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
