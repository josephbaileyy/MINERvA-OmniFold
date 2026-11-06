#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas' completion, one single-node job (REF-C2C1-BINDING-2.md
# ruling 2.2; the director's ruling of 2026-11-06 on the four TIMEOUT jobs: INVALID, the 303 PASS units stand, one
# completion job for the 47 missing c2_replica units; code at M = 77d76cfc from the fresh clean clone, with -B). As the
# replicas job (4f38fc64) with these changes: the job index is 4 and its lanes come from lanes-j4.tsv; each step is
# `srun --exclusive -n1 -c 64 --mem=$MEM`, MEM=112G; THE FIT: before any srun, NL x MEM must be within the job's
# allocated memory (AllocTRES mem, and SLURM_MEM_PER_NODE when set) and NL x 64 within its allocated CPUs (AllocTRES cpu,
# and SLURM_CPUS_ON_NODE), else it refuses (rc 2); THE CONCURRENCY CHECK: 90 s after the
# launches, every lane's step must be listed by `squeue -s` (only created steps are listed; a step whose
# creation is pending is not), else it records a STOP, cancels its steps and fails; and
# REPLICAS-DONE-j4 adds "unit_list", the sorted unit names, which the 3b read gate unions. Everything else unchanged:
# OMP/MKL/OPENBLAS = 64/1/1 (NUMEXPR 1), each unit refusing (rc 4) unless its affinity is exactly 64 and those match
# config.json e_r; the fence a recorded line; the 303 COV2D inputs stat'd (no read) before and after, a moved atime a
# STOP; porcelain --ignored before and after. Writes only under <O>. Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"; J=4
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
NL=4; MEM=112G; MEM_MB=114688
U="$O/units"; L="$O/logs-completion"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1r$J] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1r$J] refusing: deploy HEAD is not M"; exit 2; }
[ -s "$L/lanes-j4.tsv" ] && [ -s "$L/cov2d-watch-paths.txt" ] && [ -d "$U" ] || { echo "[c2c1r$J] refusing: lanes, watch list or units missing"; exit 2; }
[ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "[c2c1r$J] refusing: REPLICAS-DONE-j$J exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1r$J] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1r$J] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
amem=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=[^ ]*mem=\([0-9][0-9]*\)M.*/\1/p' | head -1)
acpu=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=cpu=\([0-9][0-9]*\).*/\1/p' | head -1)
echo "[c2c1r$J] fit: $NL steps x $MEM_MB MB = $((NL * MEM_MB)) MB within SLURM_MEM_PER_NODE=$SLURM_MEM_PER_NODE and AllocTRES mem=$amem;" \
     "$NL x 64 CPUs = $((NL * 64)) within SLURM_CPUS_ON_NODE=$SLURM_CPUS_ON_NODE and AllocTRES cpu=$acpu"
for v in "${SLURM_MEM_PER_NODE:-$amem}" "${SLURM_CPUS_ON_NODE:-$acpu}" "$amem" "$acpu"; do case "$v" in ''|*[!0-9]*) echo "[c2c1r$J] refusing: the allocation is not readable"; exit 2;; esac; done
[ $((NL * MEM_MB)) -le "${SLURM_MEM_PER_NODE:-$amem}" ] && [ $((NL * MEM_MB)) -le "$amem" ] && [ $((NL * 64)) -le "${SLURM_CPUS_ON_NODE:-$acpu}" ] && [ $((NL * 64)) -le "$acpu" ] || { echo "[c2c1r$J] refusing: the steps do not fit the allocation"; exit 2; }
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
for l in $(seq 0 $((NL - 1))); do
  args=(); while IFS=$'\t' read -r jj ll u; do [ "$jj" = "$J" ] && [ "$ll" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$L/lanes-j4.tsv")
  n=$((n + ${#args[@]} / 2))
  echo "[c2c1r$J] lane $l: $(( ${#args[@]} / 2 )) units"
  srun --exclusive -n1 -c 64 --mem=$MEM --job-name="r$J-l$l" \
      /usr/bin/time -v -o "$L/j$J-lane$l.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py "${args[@]}" --out "$U" \
      > "$L/j$J-lane$l.log" 2>&1 &
  pids="$pids $!"
done
sleep 90
running=$(squeue -s -j "$SLURM_JOB_ID" -h -o '%j' | grep -c "^r$J-l[0-9]*$")
echo "[c2c1r$J] concurrency: $running of $NL lane steps created at +90 s ($(date -u +%FT%TZ)):"
squeue -s -j "$SLURM_JOB_ID" -h -o '%i %j %M' | sed "s/^/[c2c1r$J]   /"
conc=1
if [ "$running" -ne "$NL" ]; then
  conc=0; echo "[c2c1r$J] STOP: not every lane step was created; cancelling the steps"
  for p in $pids; do kill "$p" 2>/dev/null; done
fi
rcs=""; for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1r$J] lanes done $(date -u +%FT%TZ); rcs:$rcs"
for l in $(seq 0 $((NL - 1))); do
  echo "[c2c1r$J] lane $l: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/j$J-lane$l.time" | tr -s ' \t' ' ' | tr '\n' ';')"
done
pass=0; names=""; for u in $(grep -v '^#' "$L/lanes-j4.tsv" | awk -F'\t' -v j="$J" '$1 == j {print $3}'); do
  name=$(echo "$u" | sed 's/:\(.*\)/_b\1/'); names="$names $name"; grep -q '"verdict": "PASS"' "$U/$name.done" 2>/dev/null && pass=$((pass + 1))
done
echo "[c2c1r$J] PASS markers: $pass of $n"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-after.txt" 2>&1
if cmp -s "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt"; then moved=0; echo "[c2c1r$J] COV2D inputs: no atime moved"
else moved=1; echo "[c2c1r$J] STOP: a COV2D input's atime moved:"; diff "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
list=$(printf '%s\n' $names | sort | sed 's/.*/"&"/' | paste -sd, - | sed 's/,/, /g')
printf '{"job": "%s", "index": %s, "units": %s, "pass_markers": %s, "rcs": "%s", "watch_moved": %s, "porcelain_after": %s, "concurrent": %s, "unit_list": [%s]}\n' \
    "$SLURM_JOB_ID" "$J" "$n" "$pass" "${rcs# }" "$moved" "$na" "$conc" "$list" > "$O/REPLICAS-DONE-j$J"
cat "$O/REPLICAS-DONE-j$J"
[ "$pass" = "$n" ] && [ "$moved" = 0 ] && [ "$na" = 0 ] && [ "$conc" = 1 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
