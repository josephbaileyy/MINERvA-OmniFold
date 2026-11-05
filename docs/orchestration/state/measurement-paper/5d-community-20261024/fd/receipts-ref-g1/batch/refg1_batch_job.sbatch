#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 step two, the batch (REF-G1-BINDING-2.md rulings 2, 3 and 6): the 233 declared units by the bound driver at
# M from a fresh clean clone, with -B, under the exact interpreter ruling 2 names, 8 lanes of 32 threads (config.json
# resources.max_threads_per_task), each lane ONE driver invocation over its units of <O>/lanes.tsv (the driver loads its
# inputs once per invocation). Products go to <O>/units, outside the deploy. A unit refused or failing a control gives a
# nonzero lane rc and is reported to the director unrepaired; nothing is rerun here. Porcelain, with --ignored, is
# recorded before and after. Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261105/batch ] || { echo "[refg1b] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[refg1b] refusing: deploy HEAD is not M"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1b] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[refg1b] refusing: the deploy is not clean"; exit 2; }
[ "$(grep -vc '^#' "$O/lanes.tsv")" -eq 233 ] || { echo "[refg1b] refusing: lanes.tsv is not 233 units"; exit 2; }
echo "[refg1b] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
source "$C/setup_salloc_env.sh" > "$O/env.log" 2>&1   # root_6_28, as the s5p and RE-2 jobs source it
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 NUMEXPR_NUM_THREADS=32
mkdir -p "$TMPDIR" "$O/units" "$O/lanes"
echo "[refg1b] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
pids=""
for l in 0 1 2 3 4 5 6 7; do
    args=(); while IFS=$'\t' read -r ln u; do [ "$ln" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$O/lanes.tsv")
    ( /usr/bin/time -v -o "$O/lanes/lane$l.time" "$PY" -B "$C/nd-unfolding/ref_g1/ref_g1.py" "${args[@]}" \
          --out "$O/units" --threads 32 > "$O/lanes/lane$l.log" 2>&1
      echo "$?" > "$O/lanes/lane$l.rc" ) &
    pids="$pids $!"
done
for p in $pids; do wait "$p"; done
echo "[refg1b] lanes done $(date -u +%FT%TZ)"
for l in 0 1 2 3 4 5 6 7; do
    echo "[refg1b] lane $l rc=$(cat "$O/lanes/lane$l.rc") units=$(grep -c "^$l	" "$O/lanes.tsv") $(grep -E 'Elapsed|Maximum resident' "$O/lanes/lane$l.time" | tr -s ' \t' ' ' | tr '\n' ' ')"
done
npass=$(cat "$O"/units/*.done 2>/dev/null | grep -c '"verdict": "PASS"'); ndone=$(ls "$O"/units/*.done 2>/dev/null | wc -l)
echo "[refg1b] done-markers: $ndone, PASS: $npass, of 233"
( cd "$O/units" && sha256sum *.npz ) > "$O/SHA256SUMS"
echo "[refg1b] products listed: $(wc -l < "$O/SHA256SUMS")"
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1b] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
bad=0; for l in 0 1 2 3 4 5 6 7; do [ "$(cat "$O/lanes/lane$l.rc")" = 0 ] || bad=1; done
[ "$bad" -eq 0 ] && [ "$npass" -eq 233 ] || { echo "[refg1b] STOP: a lane failed or a unit is not PASS (to the director, unrepaired)"; exit 1; }
echo "{\"units\": 233, \"pass\": $npass, \"job\": \"$SLURM_JOB_ID\", \"porcelain_after\": $na}" > "$O/DONE"
echo "[refg1b] done"
