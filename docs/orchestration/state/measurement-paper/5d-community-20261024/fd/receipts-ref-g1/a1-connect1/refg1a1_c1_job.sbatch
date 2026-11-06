#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 A1 connect 1, the job (REF-G1-BINDING-2-A1.md ruling 4.1; A1 sections 1, 3, 5): from the fresh clean clone at
# M' (0bb9a1bf), with -B, root_6_28:
#   1. the gibu1 unit ALONE in IBU-1's recorded environment: srun --exclusive -n1 -c 2 (sbatch_ibu1.sh:37; sacct
#      60130813.0 cpu=2), OMP/OPENBLAS/MKL_NUM_THREADS=1 (sbatch_ibu1.sh:25), into the NEW <O>/gibu1; ref_g1.py's
#      gibu1_environment() refuses (rc 4) unless the three variables are exactly "1" and the affinity is exactly 2;
#   2. the bars by the new reader into the NEW read directory <O>/read (bars.json, staged inputs-bars/), from the
#      batch's units (job 60857388, SHA256SUMS 6a4c1929), at 4 threads, as the bars of #791 were made;
#   3. the stat (no read) of `ref_g1_read.py reads`' set again, compared with the connect's stat before the job: every
#      declared input is read through O_NOATIME (A1 section 2), so no atime may move.
# Porcelain, with --ignored, before and after. TMPDIR is <O>/tmp (the units' staging, about 1.5 GB). Writes only under
# <O>. Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"
M=0bb9a1bfcb462ebd171d337ae1c8b2e2d0905e93
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
B=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
L="$O/logs"
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261106 ] || { echo "[a1c1] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[a1c1] refusing: deploy HEAD is not M'"; exit 2; }
for d in gibu1 read; do [ ! -e "$O/$d" ] || { echo "[a1c1] refusing: $O/$d exists"; exit 2; }; done
[ -s "$L/reads.tsv" ] && [ -s "$L/reads-stat-before.txt" ] || { echo "[a1c1] refusing: no stat set from the connect"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[a1c1] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[a1c1] refusing: the deploy is not clean"; exit 2; }
echo "[a1c1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[a1c1] squeue cov2d-* at start (recorded; every read here is O_NOATIME): $(squeue -u josephrb -h -o '%i|%j|%T' | awk -F'|' '$2 ~ /^cov2d-/' | tr '\n' ' ')"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[a1c1] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
unset NUMEXPR_NUM_THREADS
mkdir -p "$TMPDIR"
echo "[a1c1] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
# 1. gibu1, alone, in IBU-1's environment
(
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  srun --exclusive -n1 -c 2 --mem=20G --job-name=gibu1 \
      /usr/bin/time -v -o "$L/gibu1.time" "$PY" -B nd-unfolding/ref_g1/ref_g1.py --unit gibu1 --out "$O/gibu1" \
      --threads 1 > "$L/gibu1.log" 2>&1
)
grc=$?
echo "[a1c1] gibu1 rc=$grc end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$L/gibu1.time"
tail -3 "$L/gibu1.log"
[ -s "$O/gibu1/gibu1.done" ] && echo "[a1c1] gibu1.done: $(cat "$O/gibu1/gibu1.done")"
[ -s "$O/gibu1/gibu1.npz" ] && echo "[a1c1] gibu1.npz sha256 $(sha256sum "$O/gibu1/gibu1.npz" | cut -d' ' -f1) bytes $(stat -c %s "$O/gibu1/gibu1.npz")"
# 2. the bars, by the new reader, into the new read directory
(
  export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
  /usr/bin/time -v -o "$L/bars.time" "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py bars --run "$B/units" \
      --out "$O/read/bars.json" > "$L/bars.log" 2>&1
)
brc=$?
echo "[a1c1] bars rc=$brc end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$L/bars.time"
tail -3 "$L/bars.log"
[ -s "$O/read/bars.json" ] && echo "[a1c1] bars.json sha256 $(sha256sum "$O/read/bars.json" | cut -d' ' -f1)"
# 3. the stat set again: no atime may move
cut -f2 "$L/reads.tsv" | xargs -d '\n' stat -c '%U %a %X %s %n' > "$L/reads-stat-after.txt" 2>&1
if cmp -s "$L/reads-stat-before.txt" "$L/reads-stat-after.txt"; then moved=0; echo "[a1c1] stat set: no atime moved ($(wc -l < "$L/reads-stat-after.txt") files)"
else moved=1; echo "[a1c1] STOP: the stat set changed:"; diff "$L/reads-stat-before.txt" "$L/reads-stat-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[a1c1] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
printf '{"job": "%s", "gibu1_rc": %s, "bars_rc": %s, "atime_moved": %s, "porcelain_after": %s}\n' \
    "$SLURM_JOB_ID" "$grc" "$brc" "$moved" "$na" > "$O/DONE"
cat "$O/DONE"
[ "$grc" = 0 ] && [ "$brc" = 0 ] && [ "$moved" = 0 ] && [ "$na" = 0 ]
