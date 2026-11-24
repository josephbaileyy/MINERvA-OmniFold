#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=11:29:00
#SBATCH --job-name=ibub_run
# IBUB's job (IBUB-DECLARATION.md section 8): one exclusive CPU node, four lanes of 64 CPUs, in two phases.
#
# **Before any unit,** each failure refuses with rc 2 and runs nothing:
# - the namespace is $N, not a symlink, and is its own real path;
# - units/, logs/, stage/ and TMPDIR resolve under it, and units/ is new or empty;
# - the deploy is a clean clone at M (the third argument): HEAD is M, and `git status --porcelain --ignored` succeeds
#   and prints nothing;
# - $N/stage/stage.json reads PASS;
# - **the allocation**, read from one successful `scontrol show job`, is exactly as declared: JobName=ibub_run,
#   QOS=regular, TimeLimit=11:29:00, NumNodes=1, OverSubscribe=NO (exclusive), and StdOut and StdErr each a regular file
#   of its own in the connect's fresh, private $N/slurm. Four steps of 112G
#   and 64 CPUs must also fit its AllocTRES;
# - the lane table checks (ibub_lanes.py verify);
# - the root_6_28 environment activates.
#
# **The reference phase:** central on lane 0 and central_df on lane 1, one srun step each, at the same time. Then
# **the barrier**, ibub_unit.py refcheck. It is given each reference step's /usr/bin/time file, so the re-price
# trigger reads the full step's wall time. Unless it exits 0, the job ends (rc 3) before any toy starts.
#
# **The toy phase:** each lane's 150 toys, in sequential srun steps of at most CHUNK units, one process each. The four
# lanes run concurrently.
#
# Each step is `srun --exclusive -n1 -c 64 --mem=112G`, named ibub_<tag>, at OMP/MKL/OPENBLAS/NUMEXPR 64/1/1/1. Every
# unit is bound to this job (SLURM_JOB_ID) and to IBUB_M=M. Every srun reads /dev/null as stdin.
#
# **At the end:**
# - ibub_unit.py complete checks the exact 600 markers, the job and deploy binding, the absence of undeclared markers
#   and the barrier receipt;
# - the deploy must still be clean, with no exception;
# - IBUB-DONE is then written once, atomically (a temporary file renamed), with the completion record.
#
# The job writes only under $N. It never runs squeue.
#
# Arguments: <deploy> <N> <M>. Test mode (IBUB_TEST=1, for test_ibub_job.py only) swaps in the interpreter, srun and
# scontrol, and skips the conda activation. Every check runs either way. NOT set -u, because the conda activation
# would abort under it.
set -o pipefail
set -o noclobber   # from the first line. Exactly what bash's noclobber does: a `>` to a path that does not exist opens
#                    O_CREAT|O_EXCL, so a dangling symlink planted there is refused; an existing regular file, or a
#                    symlink to one, is refused. An existing non-regular file (a FIFO, a device), or a symlink to one, is
#                    still opened. That residual is held by the fresh mode-700 directories the connect makes ($N,
#                    $N/logs, $N/slurm).
C="${1:?deploy}"; N="${2:?namespace}"; M="${3:?commit}"
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
SRUN=srun; SCONTROL=scontrol
NS=/pscratch/sd/j/josephrb/ibub-20261123
RUNNER=2d-unfolding/ibub/ibub_unit.py
if [ "${IBUB_TEST:-0}" = 1 ]; then
  PY=${IBUB_PY:?test mode needs IBUB_PY}; SRUN=${IBUB_SRUN:?test mode needs IBUB_SRUN}
  SCONTROL=${IBUB_SCONTROL:?test mode needs IBUB_SCONTROL}; NS=${IBUB_NS:?test mode needs IBUB_NS}
  RUNNER=${IBUB_RUNNER:-$RUNNER}     # tests only: the run steps' runner; refcheck and complete are always the deploy's
fi
NL=4; MEM=112G; MEM_MB=114688; CHUNK=${IBUB_CHUNK:-10}; LIMIT=11:29:00; JOBNAME=ibub_run
U="$N/units"; L="$N/logs"
say() { echo "[ibub] $*"; }
fresh() { [ ! -e "$1" ] && [ ! -L "$1" ]; }   # a path about to be created is absent and not a symlink (noclobber holds)
refuse() { say "refusing: $*"; exit 2; }
under() { case "$1" in "$2"|"$2"/*) return 0;; esac; return 1; }     # under <real path> <real root>

# ---- the namespace and its subdirectories, resolved
[ "$N" = "$NS" ] || refuse "N is $N, not $NS"
[ -d "$N" ] && [ ! -L "$N" ] || refuse "$N is not a directory, or is a symlink"
RN=$(realpath "$N") && [ "$RN" = "$N" ] || refuse "$N is not its own real path ($RN)"
[[ "$M" =~ ^[0-9a-f]{40}$ ]] || refuse "M '$M' is not a commit sha"
[ ! -e "$N/IBUB-DONE" ] || refuse "$N/IBUB-DONE exists"
mkdir -p "$U" "$L" || refuse "mkdir units/logs"
for d in "$U" "$L" "$N/stage"; do
  r=$(realpath "$d") && under "$r" "$RN" && [ ! -L "$d" ] || refuse "$d resolves outside $N or is a symlink"
done
entries=$(ls -A "$U") || refuse "listing $U failed"
[ -z "$entries" ] || refuse "$U is not empty: every job starts from a new units directory"

# ---- the deploy: HEAD M, clean, each git call's status checked
head=$(git -C "$C" rev-parse HEAD) || refuse "git rev-parse failed"
[ "$head" = "$M" ] || refuse "the deploy HEAD $head is not M"
gs=$(git -C "$C" status --porcelain --ignored) || refuse "git status failed (before)"
[ -z "$gs" ] || refuse "the deploy is not clean: $(printf '%s\n' "$gs" | head -3 | tr '\n' ' ')"
say "start $(date -u +%FT%TZ) job=${SLURM_JOB_ID:-none} node=$(hostname) nproc=$(nproc 2>/dev/null) M=$M chunk=$CHUNK"

# ---- the allocation, from one successful scontrol query
[[ "${SLURM_JOB_ID:-}" =~ ^[0-9]+$ ]] || refuse "SLURM_JOB_ID '${SLURM_JOB_ID:-}' is not a job id"
SREC="$L/scontrol-batch-$SLURM_JOB_ID.txt"   # the batch's own name: the connect writes scontrol-connect-<id>.txt
fresh "$SREC" || refuse "$SREC exists or is a symlink"
info=$("$SCONTROL" show job "$SLURM_JOB_ID") || refuse "scontrol show job failed"
printf '%s\n' "$info" > "$SREC" || refuse "writing the scontrol record"
key() { printf '%s\n' "$info" | tr ' ' '\n' | sed -n "s/^$1=//p" | head -1; }
[ "$(key JobName)" = "$JOBNAME" ] || refuse "JobName is '$(key JobName)', not $JOBNAME"
[ "$(key QOS)" = regular ] || refuse "QOS is '$(key QOS)', not regular"
[ "$(key TimeLimit)" = "$LIMIT" ] || refuse "TimeLimit is '$(key TimeLimit)', not $LIMIT"
[ "$(key NumNodes)" = 1 ] || refuse "NumNodes is '$(key NumNodes)', not 1"
[ "$(key OverSubscribe)" = NO ] || refuse "OverSubscribe is '$(key OverSubscribe)', not NO (exclusive)"
# StdOut: the connect submits --output into $N/slurm, a directory it creates fresh with mode 700 just before sbatch, so
# nothing can be planted there before Slurm opens the files. The job checks two things:
# - that directory is a real directory, not a symlink, mode 700, and owned by the job's user;
# - StdOut and StdErr (the connect pins both) are each a regular file, not a symlink, owned by the job's user, in
#   exactly that directory.
SD="$N/slurm"
[ -d "$SD" ] && [ ! -L "$SD" ] || refuse "$SD is not a real directory (a symlink?)"
[ -O "$SD" ] && [ -n "$(find "$SD" -maxdepth 0 -perm 700)" ] || refuse "$SD is not private (mode 700, owned by the job's user)"
in_sd() {  # in_sd <scontrol key>: that file is a regular file of the job's own, not a symlink, in exactly $SD
  local f r; f=$(key "$1"); r=""
  [ -n "$f" ] && [ -f "$f" ] && [ ! -L "$f" ] && [ -O "$f" ] && r=$(realpath "$f") || r=""
  [ -n "$r" ] && [ "$(dirname "$r")" = "$(realpath "$SD")" ] || refuse "$1 '$f' is not a regular file of its own in $SD"
}
in_sd StdOut
in_sd StdErr      # the connect pins --error beside --output, so an inherited SBATCH_ERROR cannot send it elsewhere
tres=$(key AllocTRES)
amem=$(printf '%s\n' "$tres" | tr ',' '\n' | sed -n 's/^mem=\([0-9][0-9]*\)M$/\1/p')
case "$(printf '%s\n' "$tres" | tr ',' '\n' | sed -n 's/^mem=//p')" in *G) amem=$(( $(printf '%s\n' "$tres" | tr ',' '\n' | sed -n 's/^mem=\([0-9][0-9]*\)G$/\1/p') * 1024 ));; esac
acpu=$(printf '%s\n' "$tres" | tr ',' '\n' | sed -n 's/^cpu=\([0-9][0-9]*\)$/\1/p')
for v in "$amem" "$acpu"; do case "$v" in ''|*[!0-9]*) refuse "the allocation is not readable from AllocTRES '$tres'";; esac; done
[ $((NL * MEM_MB)) -le "$amem" ] && [ $((NL * 64)) -le "$acpu" ] || refuse "$NL steps do not fit (mem ${amem}M, cpu $acpu)"
say "allocation: $JOBNAME regular $LIMIT 1 node exclusive; fit $NL x $MEM_MB MB within ${amem}M, $NL x 64 CPUs within $acpu"

if [ "${IBUB_TEST:-0}" != 1 ]; then
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" || refuse "conda hook"
  conda activate "$HOME/.conda/envs/root_6_28" || refuse "activation failed"
fi
"$PY" -c "import json, sys; sys.exit(0 if json.load(open('$N/stage/stage.json'))['verdict'] == 'PASS' else 1)" \
  || refuse "$N/stage/stage.json is not PASS"
export TMPDIR="$N/tmp-$SLURM_JOB_ID" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 IBUB_M="$M"
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" && r=$(realpath "$TMPDIR") && under "$r" "$RN" || refuse "TMPDIR $TMPDIR is not under $N"
cd "$C" || refuse "cd $C"
"$PY" -B 2d-unfolding/ibub/ibub_lanes.py verify > "$L/lanes-verify.txt" 2>&1 || refuse "the lane table does not verify"
all_zero() { local r; for r in "$@"; do [ "$r" = 0 ] || return 1; done; [ "$#" -gt 0 ]; }

step() {  # step <tag> <unit>...: one srun step running these units in one process; its rc is the step's
  local tag=$1; shift
  local args=(); for u in "$@"; do args+=(--unit "$u"); done
  [ ! -e "$L/$tag.time" ] && [ ! -L "$L/$tag.time" ] || { say "refusing step $tag: $L/$tag.time exists"; return 2; }
  "$SRUN" --exclusive -n1 -c 64 --mem=$MEM --job-name="ibub_$tag" \
    /usr/bin/time -v -o "$L/$tag.time" "$PY" -B "$RUNNER" run "${args[@]}" --out "$U" \
    < /dev/null > "$L/$tag.log" 2>&1
}

lane_units() {  # lane_units <phase> <lane>: sets UNITS from the lane table, or returns non-zero if the table failed
  UNITS=()
  local f="$TMPDIR/lane-$1-$2.txt" u
  "$PY" -B 2d-unfolding/ibub/ibub_lanes.py "$1" "$2" > "$f" || return 1
  while IFS= read -r u; do [ -n "$u" ] && UNITS+=("$u"); done < "$f"
  return 0
}

publish_done() {  # publish_done <stage> <rc> <completion JSON or empty>: IBUB-DONE, written once by a rename, then
  # read back. Its status is 0 only if the published file is exactly what was written.
  local tmp="$N/IBUB-DONE.tmp.$$" body
  body=$(printf '{"job": "%s", "M": "%s", "stage": "%s", "rc": %s, "ref_rcs": "%s", "toy_rcs": "%s", "completion": %s}' \
    "$SLURM_JOB_ID" "$M" "$1" "$2" "${REF_RCS# }" "${TOY_RCS# }" "${3:-null}") || return 1
  [ ! -e "$N/IBUB-DONE" ] && [ ! -L "$N/IBUB-DONE" ] || { say "could not publish: IBUB-DONE exists"; return 1; }
  printf '%s\n' "$body" > "$tmp" || { say "could not publish: writing $tmp failed"; rm -f -- "$tmp"; return 1; }
  mv -- "$tmp" "$N/IBUB-DONE" || { say "could not publish: the rename failed"; rm -f -- "$tmp"; return 1; }
  [ "$(cat "$N/IBUB-DONE" 2>/dev/null)" = "$body" ] || { say "could not publish: IBUB-DONE does not read back"; return 1; }
  printf '%s\n' "$body"
}

# ---- the reference phase
REF_RCS=""; TOY_RCS=""; pids=()
for l in 0 1; do
  lane_units refs "$l" || { say "STOP: the refs lane $l table failed"; publish_done refs 3; exit 3; }
  [ "${#UNITS[@]}" -eq 1 ] || { say "STOP: refs lane $l has ${#UNITS[@]} units"; publish_done refs 3; exit 3; }
  step "refs_l$l" "${UNITS[@]}" & pids+=($!)
done
wait "${pids[0]}"; r0=$?; wait "${pids[1]}"; r1=$?; REF_RCS="$r0 $r1"
say "references done $(date -u +%FT%TZ); srun rcs: central $r0, central_df $r1"
for l in 0 1; do tail -3 "$L/refs_l$l.log" | sed "s/^/[ibub]   refs_l$l: /"; done
"$PY" -B 2d-unfolding/ibub/ibub_unit.py refcheck --out "$U" --time "central=$L/refs_l0.time" \
  --time "central_df=$L/refs_l1.time" --step-rc "central=$r0" --step-rc "central_df=$r1" > "$L/refcheck.log" 2>&1; brc=$?
cat "$L/refcheck.log"
if [ "$brc" -ne 0 ] || ! all_zero "$r0" "$r1"; then
  say "STOP: the barrier did not pass (refcheck rc $brc; reference rcs$REF_RCS); no toy starts"
  publish_done refs 3; exit 3
fi
say "barrier PASS $(date -u +%FT%TZ)"

# ---- the toy phase: four lanes, each a sequence of steps of at most CHUNK units
lane() {
  local l=$1 rc=0 i=0 k=0
  lane_units toys "$l" || return 2
  local units=("${UNITS[@]}")
  [ "${#units[@]}" -gt 0 ] || return 2
  while [ "$i" -lt "${#units[@]}" ]; do
    step "toys_l${l}_c$(printf '%02d' $k)" "${units[@]:$i:$CHUNK}" || rc=1
    i=$((i + CHUNK)); k=$((k + 1))
  done
  return $rc
}
pids=()
for l in $(seq 0 $((NL - 1))); do lane "$l" & pids+=($!); done
lrcs=()
for p in "${pids[@]}"; do wait "$p"; lrcs+=($?); done
TOY_RCS="${lrcs[*]}"
say "toys done $(date -u +%FT%TZ); lane rcs: $TOY_RCS"

# ---- the completion: the exact marker set, then the deploy still clean, then IBUB-DONE once
comp=$("$PY" -B 2d-unfolding/ibub/ibub_unit.py complete --out "$U" 2> "$L/complete.err"); crc=$?
ok=1
printf '%s\n' "$comp" > "$L/complete.json" || { ok=0; say "writing complete.json failed"; }
gs=$(git -C "$C" status --porcelain --ignored); grc=$?
[ "$crc" -eq 0 ] || ok=0
[ "$grc" -eq 0 ] && [ -z "$gs" ] || { ok=0; say "the deploy is not clean after the run (git rc $grc)"; }
all_zero "${lrcs[@]}" || ok=0
"$PY" -c "import json, sys; json.loads(sys.argv[1])" "$comp" 2> /dev/null || { ok=0; comp=null; say "complete printed no JSON"; }
if [ "$ok" = 1 ]; then
  publish_done toys 0 "$comp" || { say "end: IBUB-DONE was not published"; exit 1; }
  say "end PASS"; exit 0
fi
publish_done toys 1 "$comp" || say "IBUB-DONE was not published"
say "end: not every check held (complete rc $crc, lane rcs $TOY_RCS, git rc $grc)"; exit 1
