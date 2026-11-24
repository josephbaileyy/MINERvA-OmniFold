#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# IBUB's job (IBUB-DECLARATION.md section 8): one exclusive CPU node, four lanes of 64 CPUs, in two phases.
#
# Before any unit, each failure refuses with rc 2:
# - the namespace is $N;
# - the deploy is a clean clone at M (the third argument): HEAD is M, and porcelain --ignored is 0;
# - $N/stage/stage.json reads PASS;
# - four steps x 112G and four x 64 CPUs fit the allocation (REF-C2C1's fit check);
# - the root_6_28 environment activates.
#
# **The reference phase:** central on lane 0 and central_df on lane 1 (ibub_lanes.py), one srun step each, at the same
# time. Then **the barrier:** ibub_unit.py refcheck. Unless it exits 0, the job ends (rc 3) before any toy starts.
#
# **The toy phase:** each lane's 150 toys, in sequential srun steps of at most CHUNK units, one process each. That
# bounds what one process accumulates. REF-C2C1's lane processes ran about 19 units each. The four lanes run
# concurrently.
#
# Each step is `srun --exclusive -n1 -c 64 --mem=112G` at OMP/MKL/OPENBLAS/NUMEXPR 64/1/1/1, and each unit refuses
# (rc 4) unless its affinity and those four variables are config.json's. Every srun reads /dev/null as stdin.
#
# At the end:
# - the count of PASS done-markers is taken: 600 toys;
# - porcelain --ignored is checked again, which must still be 0;
# - IBUB-DONE is written as one JSON line.
#
# The job writes only under $N. It never runs squeue.
#
# Arguments: <deploy> <N> <M>. NOT set -u, because the conda activation would abort under it.
set -o pipefail
C="${1:?deploy}"; N="${2:?namespace}"; M="${3:?commit}"
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ "${IBUB_TEST:-0}" = 1 ] && PY=${IBUB_PY:?test mode needs IBUB_PY}
NL=4; MEM=112G; MEM_MB=114688; CHUNK=${IBUB_CHUNK:-10}
U="$N/units"; L="$N/logs"
say() { echo "[ibub] $*"; }
[ "$N" = /pscratch/sd/j/josephrb/ibub-20261123 ] || [ "${IBUB_TEST:-0}" = 1 ] || { say "refusing: N is $N"; exit 2; }
[[ "$M" =~ ^[0-9a-f]{40}$ ]] || { say "refusing: M '$M' is not a commit sha"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { say "refusing: the deploy HEAD is not M"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); say "porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { say "refusing: the deploy is not clean"; exit 2; }
[ ! -e "$N/IBUB-DONE" ] || { say "refusing: $N/IBUB-DONE exists"; exit 2; }
mkdir -p "$U" "$L" || { say "refusing: mkdir"; exit 2; }
say "start $(date -u +%FT%TZ) job=${SLURM_JOB_ID:-none} node=$(hostname) nproc=$(nproc) M=$M chunk=$CHUNK"
if [ "${IBUB_TEST:-0}" != 1 ]; then
  amem=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=[^ ]*mem=\([0-9][0-9]*\)M.*/\1/p' | head -1)
  acpu=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=cpu=\([0-9][0-9]*\).*/\1/p' | head -1)
  for v in "$amem" "$acpu"; do case "$v" in ''|*[!0-9]*) say "refusing: the allocation is not readable"; exit 2;; esac; done
  [ $((NL * MEM_MB)) -le "$amem" ] && [ $((NL * 64)) -le "$acpu" ] || { say "refusing: $NL steps do not fit (mem $amem M, cpu $acpu)"; exit 2; }
  say "fit: $NL x $MEM_MB MB within $amem M; $NL x 64 CPUs within $acpu"
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { say "refusing: activation failed"; exit 2; }
fi
"$PY" -c "import json, sys; sys.exit(0 if json.load(open('$N/stage/stage.json'))['verdict'] == 'PASS' else 1)" \
  || { say "refusing: $N/stage/stage.json is not PASS"; exit 2; }
export TMPDIR="$N/tmp-${SLURM_JOB_ID:-test}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR"
cd "$C" || exit 2
SRUN=srun; [ "${IBUB_TEST:-0}" = 1 ] && SRUN=${IBUB_SRUN:?test mode needs IBUB_SRUN}

step() {  # step <tag> <unit>...: one srun step running these units in one process; its rc is the step's
  local tag=$1; shift
  local args=(); for u in "$@"; do args+=(--unit "$u"); done
  "$SRUN" --exclusive -n1 -c 64 --mem=$MEM --job-name="ibub-$tag" \
    /usr/bin/time -v -o "$L/$tag.time" "$PY" -B 2d-unfolding/ibub/ibub_unit.py run "${args[@]}" --out "$U" \
    < /dev/null > "$L/$tag.log" 2>&1
}

lane_units() {  # lane_units <phase> <lane>: sets the array UNITS to the lane's units. bash 3.2 has no mapfile. The read
  # loop only fills the array, and every srun runs later with stdin from /dev/null.
  UNITS=()
  local u
  while IFS= read -r u; do [ -n "$u" ] && UNITS+=("$u"); done < <("$PY" -B 2d-unfolding/ibub/ibub_lanes.py "$1" "$2")
}

done_json() {  # done_json <stage> <rc>
  local pass
  pass=$(ls "$U"/toy_*.done 2>/dev/null | xargs -r grep -l '"verdict": "PASS"' | wc -l)
  local na; na=$(git -C "$C" status --porcelain --ignored | awk 'NF && index($0, "__pycache__") == 0 { c++ } END { print c + 0 }')
  printf '{"job": "%s", "stage": "%s", "rc": %s, "ref_rcs": "%s", "toy_rcs": "%s", "toy_pass_markers": %s, "porcelain_after": %s}\n' \
    "${SLURM_JOB_ID:-test}" "$1" "$2" "${REF_RCS# }" "${TOY_RCS# }" "$pass" "$na" > "$N/IBUB-DONE"
  cat "$N/IBUB-DONE"
}

# ---- the reference phase
REF_RCS=""; TOY_RCS=""; pids=""
for l in 0 1; do
  lane_units refs "$l"
  [ "${#UNITS[@]}" -eq 1 ] || { say "STOP: refs lane $l has ${#UNITS[@]} units"; done_json refs 3; exit 3; }
  step "refs-l$l" "${UNITS[@]}" & pids="$pids $!"
done
for p in $pids; do wait "$p"; REF_RCS="$REF_RCS $?"; done
say "references done $(date -u +%FT%TZ); rcs:$REF_RCS"
for l in 0 1; do tail -3 "$L/refs-l$l.log" | sed "s/^/[ibub]   refs-l$l: /"; done
"$PY" -B 2d-unfolding/ibub/ibub_unit.py refcheck --out "$U" > "$L/refcheck.log" 2>&1; brc=$?
cat "$L/refcheck.log"
if [ "$brc" -ne 0 ] || [ "$(echo $REF_RCS | tr -d ' 0')" != "" ]; then
  say "STOP: the barrier did not pass (refcheck rc $brc; reference rcs$REF_RCS); no toy starts"
  done_json refs 3; exit 3
fi
say "barrier PASS $(date -u +%FT%TZ)"

# ---- the toy phase: four lanes, each a sequence of steps of at most CHUNK units
lane() {
  local l=$1 rc=0 i=0 k=0
  lane_units toys "$l"
  local units=("${UNITS[@]}")
  [ "${#units[@]}" -gt 0 ] || return 2
  while [ "$i" -lt "${#units[@]}" ]; do
    step "toys-l$l-c$(printf '%02d' $k)" "${units[@]:$i:$CHUNK}" || rc=1
    i=$((i + CHUNK)); k=$((k + 1))
  done
  return $rc
}
pids=""
for l in $(seq 0 $((NL - 1))); do lane "$l" & pids="$pids $!"; done
for p in $pids; do wait "$p"; TOY_RCS="$TOY_RCS $?"; done
say "toys done $(date -u +%FT%TZ); lane rcs:$TOY_RCS"
done_json toys 0 > /dev/null
pass=$("$PY" -c "import json; print(json.load(open('$N/IBUB-DONE'))['toy_pass_markers'])")
na=$("$PY" -c "import json; print(json.load(open('$N/IBUB-DONE'))['porcelain_after'])")
ok=1; [ "$pass" = 600 ] || ok=0; [ "$na" = 0 ] || ok=0; [ "$(echo $TOY_RCS | tr -d ' 0')" = "" ] || ok=0
if [ "$ok" = 1 ]; then done_json toys 0; say "end PASS"; exit 0; fi
done_json toys 1; say "end: not every toy passed (pass markers $pass, lane rcs$TOY_RCS, porcelain $na)"; exit 1
