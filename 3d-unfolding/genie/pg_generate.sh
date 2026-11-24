#!/bin/bash
# pg_generate.sh --workdir W --seeds W/seeds.json -- COVFIX PG: the two validation truths through F1's bound GENIE v3
# pipeline (state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md sections 4.1-4.2; README-pg.md beside this file).
#
# Run only by cov2d's bound PG binary, as a subprocess on one exclusive CPU node: cwd W, TMPDIR=W/tmp, stdin
# /dev/null, stdout and stderr captured by the parent, a scrubbed environment (README-pg.md lists what it needs).
# It is F1's pipeline with only the tune names and the seeds changed, and F1b''s layout (FD-F1-DECLARATION-AMENDMENT-2
# section 4): per tune, run_gevgen_v3.sh reduce, gen5d_v3.py spline-check, run_gevgen_v3.sh graphs; once,
# gen5d_v3.py make-flux; 14 gevgen tasks of 160,000 events (7 per tune) at once, each under /usr/bin/time -v and
# timeout; the NOWIDTH flux-check on all 14; hadd; gen5d_v3.py convert (sampling test included); fd_f1_prep.py
# --truth-set pg. Then W/PRODUCTS.json (pg_lib.py products) and W/out/PG-SHA256SUMS.
#
# Every product, log, job input and meta file is written under W/out, W/run or W/tmp. Its own stdout carries only
# step names with pass/STOP and file counts: no seed, no path from W, no physics number. Work directories are named
# u<u>/t<k>, never by seed. gevgen's genie-mcjob-<seed>.status and any gntp.<seed>.ghep.root left by a failed gntpc
# are renamed to gevgen.status and gntp.ghep.root inside W, by each task as it ends and again on every exit (trap).
# Exit 0 on success, 1 on a failed step (a STOP), 2 on a refusal before any step.
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$(cd "$HERE/../.." && pwd)"
NT=7; NEV=160000; P=14; TO=5115     # F1b''s tasks, events, concurrency and per-task timeout (budget3.json)
PHIT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
X=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL
PRIV=/pscratch/sd/j/josephrb/covfix-pg/products   # slot 1's private genie_xsec (run_gevgen_v3.sh, setup_genie_v3.sh)

refuse() { echo "[pg] refusing: $1" >&2; exit 2; }
W=""; SEEDS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --workdir) W="$2"; shift 2 ;;
    --seeds) SEEDS="$2"; shift 2 ;;
    *) refuse "unknown argument" ;;
  esac
done
[ -n "$W" ] && [ -n "$SEEDS" ] || refuse "usage: --workdir W --seeds W/seeds.json"
case "$W" in /*) ;; *) refuse "W must be absolute" ;; esac
[ -d "$W" ] || refuse "W does not exist"
[ "$(cd "$W" && pwd -P)" = "$(pwd -P)" ] || refuse "cwd is not W"
[ "$SEEDS" = "$W/seeds.json" ] || refuse "--seeds must be W/seeds.json"
[ "$TMPDIR" = "$W/tmp" ] && [ -d "$TMPDIR" ] || refuse "TMPDIR must be the existing W/tmp"
for d in out run PRODUCTS.json; do [ ! -e "$W/$d" ] || refuse "W/$d already exists"; done
[ -n "$PG_DEPLOY_PIN" ] || refuse "PG_DEPLOY_PIN is not set"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
[ "$head_sha" = "$PG_DEPLOY_PIN" ] && [ "$dirty" -eq 0 ] || refuse "the deploy is not the pinned commit, or is modified"

O="$W/out"; R="$W/run"; G="$D/3d-unfolding/genie"
REC="$D/docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
pin() { python3 -I -c 'import json,sys; v=json.load(open(sys.argv[1]))[sys.argv[2]]; print(v or "")' "$G/pg_pins.json" "$1"; }
STRACE=$(pin strace_path); STRACE_SHA=$(pin strace_sha256); DBCONFIG_SHA=$(pin dbconfig_sha256)
[ -n "$STRACE" ] && [ -n "$STRACE_SHA" ] && [ -n "$DBCONFIG_SHA" ] || refuse "pg_pins.json is not filled (R1)"
mkdir -p "$O/logs" "$O/splines" "$O/gst" "$O/gen5d" "$O/work" "$O/traces" "$R" || refuse "cannot create W/out and W/run"
git -C "$D" status --porcelain --untracked-files=all --ignored > "$R/deploy-status-before.txt" 2>&1
need() { [ "$1" -eq 0 ] || { echo "[pg] STOP: $2 rc=$1"; exit 1; }; }
deploy_unchanged() {   # nothing may be written into the deploy (every output stays under W)
  git -C "$D" status --porcelain --untracked-files=all --ignored > "$R/deploy-status-$1.txt" 2>&1
  cmp -s "$R/deploy-status-before.txt" "$R/deploy-status-$1.txt" || need 1 "the deploy changed ($1)"
}
pass() { echo "[pg] $1: pass${2:+ ($2)}"; }
seedfree() {   # gevgen names files by its run number (= the seed): rename them inside W, in one directory or all
  local d f
  [ $# -gt 0 ] || set -- "$O"/work/u*/t*
  for d in "$@"; do
    [ -d "$d" ] || continue
    for f in "$d"/genie-mcjob-*.status; do [ -e "$f" ] && mv -f "$f" "$d/gevgen.status"; done
    for f in "$d"/gntp.*.ghep.root; do [ -e "$f" ] && mv -f "$f" "$d/gntp.ghep.root"; done
  done
  return 0
}
cleanup() {    # on every exit: stop this script's background steps, then leave no seed in a file name
  local j
  for j in $(jobs -p); do pkill -TERM -P "$j" 2>/dev/null; kill -TERM "$j" 2>/dev/null; done
  seedfree
  return 0
}
trap cleanup EXIT
trap 'exit 143' TERM INT
export -f seedfree
anaenv() {
  source "$D/setup_salloc_env.sh" > "$O/logs/env-$1.log" 2>&1
  export TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1
  case "$(python3 -V 2>&1)" in *3.11*) ;; *) exit 7 ;; esac
}
echo "[pg] start $(date -u +%FT%TZ) host=$(hostname)"

# The first compute step (R1; the director's answer 2): strace is opened once, on fd 9. Its sha256 is read through
# that descriptor and the same descriptor is executed, by the self-test here and by every traced command below.
exec 9< "$STRACE" || need 1 "open strace"
FDD=/proc/self/fd; [ -d "$FDD" ] || FDD=/dev/fd
python3 -I -B "$G/pg_verify.py" tool-check --path "$FDD/9" --sha256 "$STRACE_SHA" --self-test \
  > "$O/tool_check_strace.json" 2> "$O/logs/tool_check_strace.log"
need $? "strace (its pinned sha through the descriptor, and the self-test)"
pass "strace"
python3 -I -B "$G/pg_verify.py" members-check --root "$PRIV" --members "$REC/G2111a-members.json" \
  > "$O/members_check_G21_11a_00_000.json" 2> "$O/logs/members_check.log"
need $? "slot 1's private product against its pinned members"
python3 -I -B "$G/pg_verify.py" tool-check --path "$PRIV/.upsfiles/dbconfig" --sha256 "$DBCONFIG_SHA" \
  > "$O/dbconfig_check.json" 2> "$O/logs/dbconfig_check.log"
need $? "slot 1's UPS database file"
pass "slot 1's private product" "$(python3 -I -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["members"]))' "$REC/G2111a-members.json") members"
export PG_STRACE_FD=9
xroot() { if [ "$1" = G21_11a_00_000 ]; then echo "$PRIV/genie_xsec/v3_04_00/NULL"; else echo "$X"; fi; }
tcheck() {   # tcheck ROLE TUNE TRACE SPLINE SPLINE_SHA CWD OUT
  python3 -I -B "$G/pg_verify.py" trace-check --trace "$3" --rc 0 --role "$1" --tune "$2" --spline "$4" \
    --spline-sha256 "$5" --cwd "$6" --record "$REC/PG-RECORD.json" --manifest "$REC/genie-manifest.json" \
    --private-members "$REC/G2111a-members.json" --w-root "$W" --w-pin "$O/splines/${2}_CH.xml.gz=$(reduced_sha "$2")" \
    --out "$7"
}
reduced_sha() { [ -s "$O/spline_check_$1.json" ] && python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reduced"]["sha256"])' "$O/spline_check_$1.json" || echo none; }
source_sha() { python3 -I -c 'import ast,sys
t = ast.parse(open(sys.argv[1]).read())
pins = next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PG_SPLINE_PINS")
print(pins[sys.argv[2]][0])' "$G/gen5d_v3.py" "$1"; }

( anaenv q; python3 -B "$G/pg_lib.py" queue --seeds "$SEEDS" --out "$R/queue.txt" ) > "$O/logs/queue.log" 2>&1
need $? "seeds.json"
TUNES=$(awk '{print $1}' "$R/queue.txt" | awk '!seen[$0]++' | tr '\n' ' ')
[ "$(wc -l < "$R/queue.txt")" -eq $((2 * NT)) ] || need 1 "the task queue"
pass "seeds.json" "$(wc -l < "$R/queue.txt" | tr -d ' ') tasks"

pids=(); for T in $TUNES; do PG_TRACE_DIR="$O/traces" bash "$G/run_gevgen_v3.sh" reduce "$T" "$O/splines" > "$O/logs/reduce_$T.log" 2>&1 & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; need $? "spline reduce"; done
pass "spline reduce"
( anaenv a1
  python3 -B "$G/gen5d_v3.py" make-flux --phi-t-dir "$PHIT" --out "$O/flux_phi_t_0_100.root" || exit 1
  for T in $TUNES; do
    Q=$(echo "$T" | tr -d '_')-k250-e1000; XT=$(xroot "$T")
    python3 -B "$G/gen5d_v3.py" spline-check --tune "$T" --source "$XT/$Q/data/gxspl-NUsmall.xml" \
      --reduced "$O/splines/${T}_CH.xml.gz" --readme "$XT/$Q/data/README" --out "$O/spline_check_$T.json" || exit 1
  done ) > "$O/logs/flux_and_splines.log" 2>&1
need $? "flux file or spline check"
pass "flux file and spline check"
pids=(); for T in $TUNES; do PG_TRACE_DIR="$O/traces" bash "$G/run_gevgen_v3.sh" graphs "$T" "$O/splines" "$O/graphs_$T.root" > "$O/logs/graphs_$T.log" 2>&1 & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; need $? "gspl2root"; done
pass "gspl2root"
for T in $TUNES; do   # conditions 2 and 3 before any generation: the reduce awk read the pinned source, gspl2root the
  Q=$(echo "$T" | tr -d '_')-k250-e1000   # reduced spline and the pinned configuration
  tcheck reduce "$T" "$O/traces/reduce_$T.trace" "$(xroot "$T")/$Q/data/gxspl-NUsmall.xml" "$(source_sha "$T")" \
    "$W" "$O/trace_check_reduce_$T.json" >> "$O/logs/trace_check.log" 2>&1 || need 1 "trace check (reduce $T)"
  tcheck graphs "$T" "$O/traces/graphs_$T.trace" "$O/splines/${T}_CH.xml.gz" "$(reduced_sha "$T")" "$W" \
    "$O/trace_check_graphs_$T.json" >> "$O/logs/trace_check.log" 2>&1 || need 1 "trace check (graphs $T)"
done
pass "trace check before generation" "$(echo $TUNES | wc -w | tr -d ' ') tunes"
deploy_unchanged setup
pass "the deploy unchanged by the environments"

export G O NEV TO
xargs -P "$P" -L 1 bash -c 'mkdir -p "$O/work/$2" && PG_TRACE_DIR="$O/work/$2" /usr/bin/time -v -o "$O/work/$2/task.time" timeout "$TO" \
    bash "$G/run_gevgen_v3.sh" genie "$0" "$O/splines" "$NEV" "$1" "$O/work/$2" "$O/flux_phi_t_0_100.root" \
    > "$O/work/$2/task.log" 2>&1; rc=$?; seedfree "$O/work/$2"; [ "$rc" -eq 0 ] || exit 255' \
    < "$R/queue.txt" > "$O/logs/xargs.log" 2>&1
need $? "generation"
seedfree
pass "generation" "$(ls "$O"/work/u*/t*/genie_v3.gst.root 2>/dev/null | wc -l | tr -d ' ') gst"
while read -r T _ k; do   # condition 3 from the run itself: each gevgen opened the reduced spline and the pinned configs
  tcheck gevgen "$T" "$O/work/$k/gevgen.trace" "$O/splines/${T}_CH.xml.gz" "$(reduced_sha "$T")" "$O/work/$k" \
    "$O/work/$k/trace_check.json" >> "$O/logs/trace_check.log" 2>&1 || need 1 "trace check (gevgen ${k})"
done < "$R/queue.txt"
pass "trace check of every gevgen task" "$(wc -l < "$R/queue.txt" | tr -d ' ') tasks"
( anaenv fc; python3 -B "$G/gen5d_v3.py" flux-check --flux "$O/flux_phi_t_0_100.root" --work "$O"/work/u*/t* ) \
  > "$O/logs/flux_check.log" 2>&1
need $? "the sampled-spectrum check (NOWIDTH)"
pass "the sampled-spectrum check (NOWIDTH)"

for u in 0 1; do   # every tune's count before any conversion starts, as sbatch_fd_f1b3.sh
  n=$(ls "$O/work/u$u"/t*/genie_v3.gst.root 2>/dev/null | wc -l | tr -d ' ')
  [ "$n" -eq "$NT" ] || need 1 "u$u has $n of $NT gst files"
done
pids=(); u=0
for T in $TUNES; do
  case "$T" in   # pg_lib.TRUTH, fd_f1_prep.PG_TRUTHS
    G21_11a_00_000) N=genie_v3_g21 ;;
    G18_02a_00_000) N=genie_v3_g18_02a ;;
    *) need 1 "truth name" ;;
  esac
  ( anaenv "c_u$u"
    hadd "$O/gst/${N}_ALL.gst.root" "$O/work/u$u"/t*/genie_v3.gst.root > "$O/logs/hadd_u$u.log" 2>&1 || exit 1
    python3 -B "$G/gen5d_v3.py" convert --tune "$T" --gst "$O/gst/${N}_ALL.gst.root" --graphs "$O/graphs_$T.root" \
      --flux "$O/flux_phi_t_0_100.root" --out "$O/gen5d/${N}_xsec5d.npz" ) > "$O/logs/convert_u$u.log" 2>&1 & pids+=($!)
  echo "$N" >> "$R/truths.txt"; u=$((u + 1))
done
for p in "${pids[@]}"; do wait "$p"; need $? "hadd or conversion"; done
pass "hadd and conversion"
( anaenv p
  args=()
  for N in $(cat "$R/truths.txt"); do Q="$O/gen5d/${N}_xsec5d.npz"; args+=(--pred "$N=$Q=$(sha256sum "$Q" | cut -d' ' -f1)"); done
  python3 -B "$D/nd-unfolding/fd_f1_prep.py" --truth-set pg "${args[@]}" --out "$O/prep" ) > "$O/logs/prep.log" 2>&1
need $? "prep"
pass "prep"
( anaenv w; python3 -B "$G/pg_lib.py" products --workdir "$W" --seeds "$SEEDS" ) > "$O/logs/products.log" 2>&1
need $? "PRODUCTS.json"
pass "PRODUCTS.json"
( cd "$O" && find . -type f ! -path './logs/*' ! -name PG-SHA256SUMS ! -name '*.ghep.root' -print0 | sort -z \
  | xargs -0 sha256sum ) > "$O/PG-SHA256SUMS" 2> "$O/logs/sums.log"
need $? "the sums file"
deploy_unchanged after
pass "the deploy unchanged"
( anaenv i; python3 -B "$G/pg_lib.py" inventory --workdir "$W" ) > "$O/logs/inventory.log" 2>&1
need $? "the required inventory"
pass "the required inventory"
echo "[pg] done $(date -u +%FT%TZ) files=$(find "$W" -type f | wc -l | tr -d ' ')"
exit 0
