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
# --truth-set pg. Then W/PRODUCTS.json (pg_lib.py products), W/out/PG-SHA256SUMS (every file; it stays in W, being
# seed-bearing) and W/out/PG-PUBLISH-SHA256SUMS (pg_lib.py publish: the files that may leave W, leak-scanned for the
# seeds). Round 3 (RULINGS-A2.md) adds, before generation: the CVMFS revision, the reduce's completeness for F1's argv,
# the argv check, and a one-event public-seed coverage run per tune; after it, every gntpc's trace and the revision.
# Round 4 adds: the coverage messenger pinned in the check; tasks in their own process group (setsid), the survivor
# scan by group and cwd (this shell's ancestors excluded) and a bounded drain before publication; seedfree failures
# STOP without a path; git's own status checked; W/tmp a private directory; the node's /proc and allocation recorded;
# a CVMFS revision change accepted only with every CVMFS file read re-hashed; publication by the export allowlist with
# ROOT objects inflated, int64 forms STOP and int32 counted, each gst's schema equal to B3's (RULINGS-A2.md, round 4).
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
GENIE_CFG=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config
CVMFS_REPO=/cvmfs/larsoft.opensciencegrid.org
PY=/usr/bin/python3.11   # the checks' interpreter outside the analysis environment (the probe's; not the node's python3)

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
[ -x "$PY" ] || refuse "$PY is missing"
for v in LD_PRELOAD LD_AUDIT BASH_ENV ENV PYTHONPATH PYTHONSTARTUP PYTHONUSERBASE GXMLPATHS GALGCONF; do   # hooks no
  # trace attributes, and GENIE's XML lookups other than GXMLPATH (XmlParserUtils GetXMLPathList)
  [ -z "${!v:-}" ] || refuse "$v is set"
done
case "$W" in /*) ;; *) refuse "W must be absolute" ;; esac
[ -d "$W" ] || refuse "W does not exist"
[ "$(cd "$W" && pwd -P)" = "$(pwd -P)" ] || refuse "cwd is not W"
[ "$(cd "$W" && pwd -P)" = "$W" ] || refuse "W must be its own physical path"   # a linked W would mis-gate its files
[ "$SEEDS" = "$W/seeds.json" ] || refuse "--seeds must be W/seeds.json"
[ "$TMPDIR" = "$W/tmp" ] && [ -d "$TMPDIR" ] || refuse "TMPDIR must be the existing W/tmp"
"$PY" -I -c 'import os, stat, sys
s = os.lstat(sys.argv[1])
sys.exit(0 if stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode) == 0o700 and s.st_uid == os.getuid() else 1)' "$W/tmp" \
  || refuse "W/tmp must be a real directory of this user's, mode 0700"
for d in out run PRODUCTS.json; do [ ! -e "$W/$d" ] || refuse "W/$d already exists"; done
O="$W/out"; R="$W/run"; G="$D/3d-unfolding/genie"
REC="$D/docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
[ -n "$PG_DEPLOY_PIN" ] || refuse "PG_DEPLOY_PIN is not set"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null) || refuse "git cannot read the deploy's HEAD"
dirty=$(git -C "$D" status --porcelain --untracked-files=all --ignored 2>/dev/null) || refuse "git status failed"
[ "$head_sha" = "$PG_DEPLOY_PIN" ] && [ -z "$dirty" ] || refuse "the deploy is not the pinned commit, or is modified"

pin() { "$PY" -I -c 'import json,sys; v=json.load(open(sys.argv[1]))[sys.argv[2]]; print(v or "")' "$G/pg_pins.json" "$1"; }
STRACE=$(pin strace_path); STRACE_SHA=$(pin strace_sha256); DBCONFIG_SHA=$(pin dbconfig_sha256)
SYSPINS=$("$PY" -I -c 'import json,sys
v = json.load(open(sys.argv[1])).get("system_tools") or {}
print("".join(f"--system-pin\n{k}={h}\n" for k, h in sorted(v.items()) if k and h))' "$G/pg_pins.json")
[ -n "$STRACE" ] && [ -n "$STRACE_SHA" ] && [ -n "$DBCONFIG_SHA" ] && [ -n "$SYSPINS" ] || refuse "pg_pins.json is not filled (R1)"
"$PY" -I -c 'import json, sys; d = json.load(open(sys.argv[1])); sys.exit(0 if d.get("gst") and d.get("gst_merged") else 1)' \
  "$REC/root-schemas.json" 2>/dev/null || refuse "root-schemas.json lacks B3's gst or gst_merged schema"
mkdir -p "$O/logs" "$O/splines" "$O/gst" "$O/gen5d" "$O/work" "$O/traces" "$R" || refuse "cannot create W/out and W/run"
git -C "$D" status --porcelain --untracked-files=all --ignored > "$R/deploy-status-before.txt" 2>&1 \
  || refuse "git status failed"
need() { [ "$1" -eq 0 ] || { echo "[pg] STOP: $2 rc=$1"; exit 1; }; }
deploy_unchanged() {   # nothing may be written into the deploy (every output stays under W)
  git -C "$D" status --porcelain --untracked-files=all --ignored > "$R/deploy-status-$1.txt" 2>&1 \
    || need 1 "git status failed ($1)"
  cmp -s "$R/deploy-status-before.txt" "$R/deploy-status-$1.txt" || need 1 "the deploy changed ($1)"
}
pass() { echo "[pg] $1: pass${2:+ ($2)}"; }
seedfree() {   # gevgen names files by its run number (= the seed): rename them inside W, in one directory or all;
  local d f bad=0   # a failed rename's message would carry the name, so it is silenced and counted, and 1 returned
  [ $# -gt 0 ] || set -- "$O"/work/u*/t*
  for d in "$@"; do
    [ -d "$d" ] || continue
    for f in "$d"/genie-mcjob-*.status; do [ -e "$f" ] || continue; mv -f "$f" "$d/gevgen.status" 2>/dev/null || bad=1; done
    for f in "$d"/gntp.*.ghep.root; do [ -e "$f" ] || continue; mv -f "$f" "$d/gntp.ghep.root" 2>/dev/null || bad=1; done
    for f in "$d"/genie-mcjob-*.status "$d"/gntp.*.ghep.root; do [ ! -e "$f" ] || bad=1; done
  done
  return $bad
}
freeze() {     # freeze PID: stop PID, then each descendant (a stopped parent cannot fork), printing every pid stopped
  kill -STOP "$1" 2>/dev/null || return 0
  echo "$1"
  local c; for c in $(pgrep -P "$1"); do freeze "$c"; done
}
alive() {      # alive PID: running or stopped, not a zombie (kill -0 succeeds on a zombie)
  local st; st=$(ps -o stat= -p "$1" 2>/dev/null) || return 1
  case "$st" in Z*|"") return 1 ;; esac
}
kill_tree() {  # kill_tree PID: end PID and every descendant, and wait (30 s at most) until none is left alive (KILL
  local all i p live   # after 15 s); the job is reaped only once it is dead, so an unkillable one cannot hang this
  all=$(freeze "$1")
  [ -n "$all" ] || return 0
  kill -TERM $all 2>/dev/null; kill -CONT $all 2>/dev/null
  for i in $(seq 1 60); do
    live=""; for p in $all; do alive "$p" && live="$live $p"; done
    [ -n "$live" ] || break
    [ "$i" -le 30 ] || kill -KILL $live 2>/dev/null
    sleep 0.5
  done
  [ -z "$live" ] || echo "[pg] cleanup: $(echo $live | wc -w | tr -d ' ') processes of a tree outlived KILL by 15 s"
  if alive "$1"; then echo "[pg] cleanup: a job is left unreaped, still alive after KILL"   # the guard: no wait on it
  else wait "$1" 2>/dev/null; fi   # reap the job itself
  return 0
}
ANCESTORS=""; a=$PPID   # this shell's parent chain (the bound binary among it), which the scan never kills
while [ -n "$a" ] && [ "$a" -gt 1 ] 2>/dev/null; do ANCESTORS="$ANCESTORS $a"; a=$(ps -o ppid= -p "$a" 2>/dev/null | tr -d ' '); done
XSID=0      # the generation's session (setsid), once started: GNU timeout gives each task a process group of its own
drain() {      # end every background step and its tree; then KILL the generation session's survivors until none is
  local j out rc n   # left or 30 s (monotonic) have passed; a process outside this run with a cwd in W is a STOP,
  for j in $(jobs -p); do kill_tree "$j"; done   # and is not killed: it may be the parent's
  out=$("$PY" -I -B "$G/pg_verify.py" drain --w "$W" --sid "$XSID" --skip "$$ $ANCESTORS" 2>/dev/null); rc=$?
  n() { "$PY" -I -c 'import json,sys; print(json.loads(sys.argv[1]).get(sys.argv[2], 0))' "$out" "$1" 2>/dev/null || echo 0; }
  [ "$rc" -ne 2 ] && [ -n "$out" ] || { echo "[pg] cleanup: the process list could not be read"; return 1; }
  [ "$(n own)" -eq 0 ] || echo "[pg] cleanup: $(n own) processes outlived their trees"   # the backstop
  if [ "$(n own)" -gt 0 ] && [ "$(n left)" -eq 0 ]; then
    echo "[pg] cleanup: the survivors ended after $(n polls) polls (0.5 s each, 30 s at most)"
  fi
  [ "$(n left)" -eq 0 ] || echo "[pg] cleanup: $(n left) survivors still alive 30 s after KILL"
  [ "$(n foreign)" -eq 0 ] || echo "[pg] cleanup: $(n foreign) processes outside this run have a cwd in W (not killed)"
  return $([ "$rc" -eq 0 ] && echo 0 || echo 1)
}
cleanup() {    # on every exit: end this script's background steps and everything under them, verify nothing is left
  local rc=$? ok=0   # running in W, then leave no seed in a file name (a live task could otherwise write one after
  drain || ok=1      # seedfree); on any STOP the publication set is withdrawn
  seedfree || { echo "[pg] STOP: seedfree could not rename every seed-named file"; ok=1; }
  if [ "$ok" -ne 0 ] || [ "$rc" -ne 0 ]; then rm -f "$W/out/PG-PUBLISH-SHA256SUMS" "$W/out/leak_scan.json"; fi
  if [ "$ok" -ne 0 ]; then echo "[pg] STOP: processes survived the cleanup, or a rename failed"; exit 1; fi
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
ulimit -c 0 || refuse "cannot set the core limit to 0"   # Q2: no core file; a piped core handler ignores the limit (recorded, out of scope)
echo "[pg] start $(date -u +%FT%TZ) host=$(hostname)"

# The first compute step (R1; the director's answer 2): strace is opened once, on fd 9. Its sha256 is read through
# that descriptor and the same descriptor is executed, by the self-test here and by every traced command below.
exec 9< "$STRACE" || need 1 "open strace"
"$PY" -I -B "$G/pg_verify.py" tool-check --fd 9 --sha256 "$STRACE_SHA" --self-test \
  > "$O/tool_check_strace.json" 2> "$O/logs/tool_check_strace.log"
need $? "strace (its pinned sha through the descriptor, and the self-test)"
pass "strace"
V() { "$PY" -I -B "$G/pg_verify.py" "$@"; }
V revision --repo "$CVMFS_REPO" > "$O/revision_start.json" 2> "$O/logs/revision.log"
need $? "the CVMFS revision (start)"
"$PY" -I -B "$G/pg_verify.py" node-record > "$O/node_check.json" 2> "$O/logs/node.log"   # C3: recorded, not a gate
pass "the node's /proc and allocation recorded"
"$PY" -I -B "$G/pg_verify.py" members-check --root "$PRIV" --members "$REC/G2111a-members.json" \
  > "$O/members_check_G21_11a_00_000.json" 2> "$O/logs/members_check.log"
need $? "slot 1's private product against its pinned members"
"$PY" -I -B "$G/pg_verify.py" tool-check --path "$PRIV/.upsfiles/dbconfig" --sha256 "$DBCONFIG_SHA" \
  > "$O/dbconfig_check.json" 2> "$O/logs/dbconfig_check.log"
need $? "slot 1's UPS database file"
pass "slot 1's private product" "$("$PY" -I -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["members"]))' "$REC/G2111a-members.json") members"
export PG_STRACE_FD=9
xroot() { if [ "$1" = G21_11a_00_000 ]; then echo "$PRIV/genie_xsec/v3_04_00/NULL"; else echo "$X"; fi; }
qual() { echo "$(echo "$1" | tr -d '_')-k250-e1000"; }
xpins() {    # a CVMFS tune's source spline and README at their exact paths (PG_SPLINE_PINS); slot 1's are its members
  [ "$1" != G21_11a_00_000 ] || return 0
  local Q; Q=$(qual "$1")
  printf -- '--pin\n%s\n--pin\n%s\n' "$X/$Q/data/gxspl-NUsmall.xml=$(source_sha "$1" 0)" "$X/$Q/data/README=$(source_sha "$1" 1)"
}
tcheck() {   # tcheck ROLE TUNE TRACE SPLINE SPLINE_SHA CWD OUT [--messenger M | --output F]
  local xp=() sp=() l; while IFS= read -r l; do xp+=("$l"); done < <(xpins "$2")
  while IFS= read -r l; do [ -z "$l" ] || sp+=("$l"); done <<< "$SYSPINS"
  [ "$2" = G21_11a_00_000 ] || [ "${#xp[@]}" -eq 4 ] || { echo "no exact pins for $2" >&2; return 1; }
  "$PY" -I -B "$G/pg_verify.py" trace-check --trace "$3" --rc 0 --role "$1" --tune "$2" --spline "$4" \
    --spline-sha256 "$5" --cwd "$6" --record "$REC/PG-RECORD.json" --manifest "$REC/genie-manifest.json" \
    --private-members "$REC/G2111a-members.json" --w-root "$W" --w-pin "$O/splines/${2}_CH.xml.gz=$(reduced_sha "$2")" \
    --gxmlpath "$(cat "$R/gxmlpath_$2.txt")" --xsec-data "$(xroot "$2")/$(qual "$2")/data" "${xp[@]}" "${sp[@]}" \
    --out "$7" "${@:8}"
}
reduced_sha() { [ -s "$O/spline_check_$1.json" ] && "$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reduced"]["sha256"])' "$O/spline_check_$1.json" || echo none; }
source_sha() { "$PY" -I -c 'import ast,sys
t = ast.parse(open(sys.argv[1]).read())
pins = next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PG_SPLINE_PINS")
print(pins[sys.argv[2]][int(sys.argv[3])])' "$G/gen5d_v3.py" "$1" "${2:-0}"; }

( anaenv q; python3 -B "$G/pg_lib.py" queue --seeds "$SEEDS" --out "$R/queue.txt" ) > "$O/logs/queue.log" 2>&1
need $? "seeds.json"
TUNES=$(awk '{print $1}' "$R/queue.txt" | awk '!seen[$0]++' | tr '\n' ' ')
[ "$(wc -l < "$R/queue.txt")" -eq $((2 * NT)) ] || need 1 "the task queue"
pass "seeds.json" "$(wc -l < "$R/queue.txt" | tr -d ' ') tasks"
pinhash() {   # Q1 (the director, 2026-11-25): every pinned CVMFS file, the genie manifest's and each CVMFS tune's
  local xp=() l T   # spline and README, hashed at the start and the end; each must equal its pin, and both sets are kept
  for T in $TUNES; do while IFS= read -r l; do xp+=("$l"); done < <(xpins "$T"); done
  V pin-hash --manifest "$REC/genie-manifest.json" --products "$CVMFS_REPO/products" "${xp[@]}" \
    > "$O/pin_hash_$1.json" 2>> "$O/logs/pin_hash.log"
  need $? "every pinned CVMFS file against its pin ($1)"
  pass "every pinned CVMFS file ($1)"
}
pinhash start

for T in $TUNES; do   # the programs the traced steps run, as their own setup resolves them (no trace shows an exec)
  ( source "$G/setup_genie_v3.sh" "$T" "$O/splines" > /dev/null 2>&1 || exit 1
    command -v gevgen && command -v gspl2root || exit 1
    printf '%s\n' "${LD_LIBRARY_PATH-}" > "$R/ld_library_path_$T.txt"; command -v awk > "$R/awk_$T.txt"
    printf '%s\n' "${GXMLPATH-}" > "$R/gxmlpath_$T.txt" ) \
    > "$R/exe_$T.txt" 2> "$O/logs/exe_$T.log" || need 1 "resolve gevgen and gspl2root ($T)"
  "$PY" -I -B "$G/pg_verify.py" exe-check --manifest "$REC/genie-manifest.json" $(sed 's/^/--path /' "$R/exe_$T.txt") \
    --ld-library-path "$(cat "$R/ld_library_path_$T.txt")" --system-path "$(cat "$R/awk_$T.txt")" \
    > "$O/exe_check_$T.json" 2>> "$O/logs/exe_$T.log" || need 1 "gevgen, gspl2root, awk and LD_LIBRARY_PATH ($T)"
done
pass "gevgen and gspl2root against the manifest, awk and LD_LIBRARY_PATH"
pids=(); for T in $TUNES; do PG_TRACE_DIR="$O/traces" bash "$G/run_gevgen_v3.sh" reduce "$T" "$O/splines" > "$O/logs/reduce_$T.log" 2>&1 & pids+=($!); done
for p in "${pids[@]}"; do wait "$p"; need $? "spline reduce"; done
pass "spline reduce"
for T in $TUNES; do   # D3' (i): for every (probe, target) pair in F1's argv the reduce kept every spline, knots and all
  V reduce-check --source "$(xroot "$T")/$(qual "$T")/data/gxspl-NUsmall.xml" --reduced "$O/splines/${T}_CH.xml.gz" \
    --script "$G/run_gevgen_v3.sh" > "$O/reduce_check_$T.json" 2>> "$O/logs/reduce_check.log" || need 1 "reduce completeness ($T)"
done
V argv-check --script "$G/run_gevgen_v3.sh" > "$O/argv_check.json" 2>> "$O/logs/reduce_check.log" || need 1 "the coverage argv"
pass "reduce completeness and the coverage argv"
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
    "$O/trace_check_graphs_$T.json" --output "$O/graphs_$T.root" >> "$O/logs/trace_check.log" 2>&1 \
    || need 1 "trace check (graphs $T)"
done
pass "trace check before generation" "$(echo $TUNES | wc -w | tr -d ' ') tunes"
V messenger --laconic "$GENIE_CFG/Messenger_laconic.xml" --out "$O/Messenger_pg.xml" > "$O/messenger_check.json" \
  2>> "$O/logs/coverage.log" || need 1 "the coverage messenger"
for T in $TUNES; do   # D3' (ii): one public-seed event per tune, before any sealed seed is used; GEVGDriver at DEBUG
  C="$O/coverage/$T"; mkdir -p "$C"    # names every spline it needs and whether the pinned file supplied it
  PG_TRACE_DIR="$C" bash "$G/run_gevgen_v3.sh" coverage "$T" "$O/splines" "$C" "$O/flux_phi_t_0_100.root" \
    "$O/Messenger_pg.xml" > "$O/logs/coverage_$T.log" 2>&1 || need 1 "the coverage run ($T)"
  tcheck coverage "$T" "$C/coverage.trace" "$O/splines/${T}_CH.xml.gz" "$(reduced_sha "$T")" "$C" \
    "$O/trace_check_coverage_$T.json" --messenger "$O/Messenger_pg.xml" >> "$O/logs/trace_check.log" 2>&1 \
    || need 1 "trace check (coverage $T)"
  V coverage-log --log "$C/gevgen.log" --script "$G/run_gevgen_v3.sh" --reduced "$O/splines/${T}_CH.xml.gz" \
    > "$O/coverage_check_$T.json" 2>> "$O/logs/coverage.log" || need 1 "spline coverage ($T)"
  rm -f "$C/gevgen.log" "$C/gntp.123456789.ghep.root" "$C/genie-mcjob-123456789.status" "$C/input-flux.root"
  extra=$(ls -A "$C" | grep -vx coverage.trace | tr '\n' ' ')   # the public seed's run: its names may be shown
  [ -z "$extra" ] || need 1 "the coverage run's outputs ($T): unexpected $extra"   # its log's sha is in the check
done
pass "spline coverage" "$(echo $TUNES | wc -w | tr -d ' ') tunes"
deploy_unchanged setup
pass "the deploy unchanged by the environments"

export G O NEV TO
"$PY" -I -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' xargs -P "$P" -L 1 bash -c 'mkdir -p "$O/work/$2" && PG_TRACE_DIR="$O/work/$2" /usr/bin/time -v -o "$O/work/$2/task.time" timeout "$TO" \
    bash "$G/run_gevgen_v3.sh" genie "$0" "$O/splines" "$NEV" "$1" "$O/work/$2" "$O/flux_phi_t_0_100.root" \
    > "$O/work/$2/task.log" 2>&1; rc=$?; seedfree "$O/work/$2"; [ "$rc" -eq 0 ] || exit 255' \
    < "$R/queue.txt" > "$O/logs/xargs.log" 2>&1 &
XP=$!; XSID=$XP     # its own session, which the survivor scan covers whatever process group a task is in
wait "$XP"          # a job, not the foreground: a TERM is handled now, and cleanup can reach every task
need $? "generation"
seedfree || need 1 "seedfree: a seed-named file could not be renamed"
pass "generation" "$(ls "$O"/work/u*/t*/genie_v3.gst.root 2>/dev/null | wc -l | tr -d ' ') gst"
while read -r T _ k; do   # condition 3 from the run itself: each gevgen opened the reduced spline and the pinned configs
  tcheck gevgen "$T" "$O/work/$k/gevgen.trace" "$O/splines/${T}_CH.xml.gz" "$(reduced_sha "$T")" "$O/work/$k" \
    "$O/work/$k/trace_check.json" >> "$O/logs/trace_check.log" 2>&1 || need 1 "trace check (gevgen ${k})"
done < "$R/queue.txt"
pass "trace check of every gevgen task" "$(wc -l < "$R/queue.txt" | tr -d ' ') tasks"
while read -r T _ k; do   # gntpc, which writes the gst the pipeline consumes, is traced and checked too (D1)
  tcheck gntpc "$T" "$O/work/$k/gntpc.trace" "" "" "$O/work/$k" "$O/work/$k/trace_check_gntpc.json" \
    --ghep-from-trace "$O/work/$k/gevgen.trace" \
    >> "$O/logs/trace_check.log" 2>&1 || need 1 "trace check (gntpc ${k})"
done < "$R/queue.txt"
pass "trace check of every gntpc task" "$(wc -l < "$R/queue.txt" | tr -d ' ') tasks"
pinhash end
V revision --repo "$CVMFS_REPO" > "$O/revision_end.json" 2>> "$O/logs/revision.log"
need $? "the CVMFS revision (end)"
tcs=(); for f in "$O"/trace_check_*.json "$O"/work/u*/t*/trace_check*.json; do [ -e "$f" ] && tcs+=(--trace-check "$f"); done
V revision-compare --start "$O/revision_start.json" --end "$O/revision_end.json" "${tcs[@]}" \
  > "$O/revision_compare.json" 2>> "$O/logs/revision.log"
need $? "the CVMFS revision changed and a file the run read no longer matches its pin"
pass "the CVMFS revision, or every file read re-hashed"
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
drain || need 1 "a process outlived its step before publication"   # D6/C13: nothing runs in W from here on
[ -z "$(jobs -p)" ] || need 1 "a background step is still listed"
( cd "$O" && find . -type f ! -path './logs/*' ! -name PG-SHA256SUMS ! -name '*.ghep.root' -print0 | sort -z \
  | xargs -0 sha256sum ) > "$O/PG-SHA256SUMS" 2> "$O/logs/sums.log"
need $? "the sums file"
deploy_unchanged after   # its snapshot is published, so it is taken before the publish set is listed and scanned
pass "the deploy unchanged"
( anaenv l; python3 -B "$G/pg_lib.py" publish --workdir "$W" --seeds "$SEEDS" --schemas "$REC/root-schemas.json" ) \
  > "$O/logs/publish.log" 2>&1
need $? "the publish set and its leak scan"
pass "the publish set and its leak scan"
git -C "$D" status --porcelain --untracked-files=all --ignored > "$W/tmp/deploy-status-final.txt" 2>&1 \
  || need 1 "git status failed (final)"
cmp -s "$R/deploy-status-before.txt" "$W/tmp/deploy-status-final.txt" || need 1 "the deploy changed (publish)"
( anaenv i; python3 -B "$G/pg_lib.py" inventory --workdir "$W" ) > "$O/logs/inventory.log" 2>&1
need $? "the required inventory"
pass "the required inventory"
echo "[pg] done $(date -u +%FT%TZ) files=$(find "$W" -type f | wc -l | tr -d ' ')"
exit 0
