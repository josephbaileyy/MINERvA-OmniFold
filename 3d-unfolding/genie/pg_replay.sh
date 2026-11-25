#!/bin/bash
# pg_replay.sh --workdir R -- COVFIX PG's B3 replay for slot 1 (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md,
# approved; COVFIX rev 12 section 4.1, 783188cd), on a login node, from a git-archive deploy of the pinned commit.
#
# It runs pg_generate.sh's checks before generation for G21_11a_00_000, then one public-seed gevgen, each under the
# same strace prefix and checks:
#   strace (pinned sha through fd 9, self-test); slot 1's private product and its UPS file; gevgen and gspl2root
#   against the manifest; run_gevgen_v3.sh reduce (traced) and gen5d_v3.py spline-check; gen5d_v3.py make-flux;
#   run_gevgen_v3.sh graphs (traced); run_gevgen_v3.sh genie with N=100 and seed 123456789 (public, below the sealed
#   range's smallest task seed; F1's flux, target and energy range), traced; trace-check of reduce, graphs, gevgen.
# Then the director's four real-shape checks (pg_verify.py shape-check), which must pass here before slot 2 is
# generated: the real member listing, the /proc/self/fd magic link, a real O_DIRECTORY open, and slot 2's (G18_02a_00_000)
# reduce traced and checked at its real CVMFS path (an awk over CVMFS's spline; nothing generated for slot 2).
# The event and status files of the 100-event run are deleted unread; their sha256 and size are kept in
# R/deleted.json only. R/replay.json holds the checks' passes and the gated files each traced run opened.
# Exit 0 when every step and check passes, 1 on a STOP, 2 on a refusal before any step.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$(cd "$HERE/../.." && pwd)"
T=G21_11a_00_000; Q=G2111a00000-k250-e1000
SEED=123456789; NEV=100; TO=3600
PHIT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
PRIV=/pscratch/sd/j/josephrb/covfix-pg/products   # slot 1's private genie_xsec (run_gevgen_v3.sh, setup_genie_v3.sh)
REC="$D/docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
PY=/usr/bin/python3.11   # the checks' interpreter outside the analysis environment (the probe's; not the node's python3)

refuse() { echo "[replay] refusing: $1" >&2; exit 2; }
[ "$1" = "--workdir" ] && [ $# -eq 2 ] || refuse "usage: --workdir R"
R=$2
case "$R" in /*) ;; *) refuse "R must be absolute" ;; esac
[ -d "$R" ] && [ -z "$(ls -A "$R")" ] || refuse "R must be an existing empty directory"
[ "$(cd "$R" && pwd -P)" = "$(pwd -P)" ] || refuse "cwd is not R"
[ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] || refuse "TMPDIR must exist"
[ -x "$PY" ] || refuse "$PY is missing"
for v in LD_PRELOAD LD_AUDIT BASH_ENV ENV; do   # a loader or shell hook would run code no trace attributes
  [ -z "${!v:-}" ] || refuse "$v is set"
done
pin() { "$PY" -I -c 'import json,sys; v=json.load(open(sys.argv[1]))[sys.argv[2]]; print(v or "")' "$HERE/pg_pins.json" "$1"; }
STRACE=$(pin strace_path); STRACE_SHA=$(pin strace_sha256); DBCONFIG_SHA=$(pin dbconfig_sha256)
[ -n "$STRACE" ] && [ -n "$STRACE_SHA" ] && [ -n "$DBCONFIG_SHA" ] || refuse "pg_pins.json is not filled (R1)"
mkdir -p "$R/logs" "$R/splines" "$R/traces" "$R/work" || refuse "cannot create R's directories"
need() { [ "$1" -eq 0 ] || { echo "[replay] STOP: $2 rc=$1"; exit 1; }; }
pass() { echo "[replay] $1: pass"; }
DRIVER_VARS="HERE D T Q SEED NEV TO PHIT PRIV REC R PY STRACE STRACE_SHA DBCONFIG_SHA TMPDIR"
snap() { local v; for v in $DRIVER_VARS; do printf '%s=%s\n' "$v" "${!v}"; done; }
anaenv() {   # the analysis environment. From a git archive, only the root_6_28 conda activation is needed; the two
  # build-tree setups git does not carry are the only tolerated messages, matched by path (the director's condition)
  local keep_tmp="$TMPDIR" before
  before=$(snap)
  source "$D/setup_salloc_env.sh" > "$R/logs/env-$1.log" 2>&1
  export TMPDIR="$keep_tmp" PYTHONDONTWRITEBYTECODE=1      # setup_salloc_env.sh sets TMPDIR=$SCRATCH/tmp
  [ "$(snap)" = "$before" ] || { echo "[replay] the environment changed a driver variable" >&2; return 1; }
  "$PY" -I - "$D" "$R/logs/env-$1.log" "$R/env_check_$1.json" <<'EOF' || return 1
import json, re, sys
d, log, out = sys.argv[1:]
allowed = [re.escape(f"{d}/setup_salloc_env.sh") + r": line \d+: " + re.escape(f"{d}/{p}") + ": No such file or directory"
           for p in ("unbinned_unfolding/build/setup.sh", "MINERvA101/opt/bin/setup.sh")]
lines = [ln for ln in open(log).read().splitlines() if ln.strip()]
tolerated = [ln for ln in lines if any(re.fullmatch(a, ln) for a in allowed)]
other = [ln for ln in lines if ln not in tolerated]
ok = not other and len(tolerated) == len(set(tolerated)) <= 2
open(out, "w").write(json.dumps({"tolerated": tolerated, "other": other, "pass": ok}, indent=1) + "\n")
sys.exit(0 if ok else 1)
EOF
}
V() { "$PY" -I -B "$HERE/pg_verify.py" "$@"; }
echo "[replay] start $(date -u +%FT%TZ) host=$(hostname)"

exec 9< "$STRACE" || need 1 "open strace"
V tool-check --fd 9 --sha256 "$STRACE_SHA" --self-test > "$R/tool_check_strace.json" 2> "$R/logs/tool.log"
need $? "strace (its pinned sha through the descriptor, and the self-test)"
V members-check --root "$PRIV" --members "$REC/G2111a-members.json" > "$R/members_check.json" 2> "$R/logs/members.log"
need $? "slot 1's private product against its pinned members"
V tool-check --path "$PRIV/.upsfiles/dbconfig" --sha256 "$DBCONFIG_SHA" > "$R/dbconfig_check.json" 2> "$R/logs/dbconfig.log"
need $? "slot 1's UPS database file"
( source "$HERE/setup_genie_v3.sh" "$T" "$R/splines" > /dev/null 2>&1 || exit 1
  command -v gevgen && command -v gspl2root || exit 1
  printf '%s\n' "${LD_LIBRARY_PATH-}" > "$R/ld_library_path.txt"; command -v awk > "$R/awk.txt" ) \
  > "$R/exe.txt" 2> "$R/logs/exe.log" || need 1 "resolve gevgen and gspl2root"
V exe-check --manifest "$REC/genie-manifest.json" $(sed 's/^/--path /' "$R/exe.txt") \
  --ld-library-path "$(cat "$R/ld_library_path.txt")" --system-path "$(cat "$R/awk.txt")" > "$R/exe_check.json" 2>> "$R/logs/exe.log"
need $? "gevgen, gspl2root, awk and LD_LIBRARY_PATH"
pass "strace, the private product, the programs"
export PG_STRACE_FD=9

PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" reduce "$T" "$R/splines" > "$R/logs/reduce.log" 2>&1
need $? "spline reduce"
( anaenv a || exit 1
  python3 -B "$HERE/gen5d_v3.py" make-flux --phi-t-dir "$PHIT" --out "$R/flux_phi_t_0_100.root" || exit 1
  python3 -B "$HERE/gen5d_v3.py" spline-check --tune "$T" --source "$PRIV/genie_xsec/v3_04_00/NULL/$Q/data/gxspl-NUsmall.xml" \
    --reduced "$R/splines/${T}_CH.xml.gz" --readme "$PRIV/genie_xsec/v3_04_00/NULL/$Q/data/README" \
    --out "$R/spline_check.json" ) > "$R/logs/flux_and_spline.log" 2>&1
need $? "flux file or spline check"
PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" graphs "$T" "$R/splines" "$R/graphs_$T.root" > "$R/logs/graphs.log" 2>&1
need $? "gspl2root"
RED=$("$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reduced"]["sha256"])' "$R/spline_check.json")
spin() { "$PY" -I -c 'import ast,sys
t = ast.parse(open(sys.argv[1]).read())
print(next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PG_SPLINE_PINS")[sys.argv[2]][int(sys.argv[3])])' "$HERE/gen5d_v3.py" "$1" "$2"; }
SRC=$(spin "$T" 0)
tcheck() {   # tcheck ROLE TRACE SPLINE SPLINE_SHA CWD OUT [ARG ...]
  V trace-check --trace "$2" --rc 0 --role "$1" --tune "${TT:-$T}" --spline "$3" --spline-sha256 "$4" --cwd "$5" \
    --record "$REC/PG-RECORD.json" --manifest "$REC/genie-manifest.json" --private-members "$REC/G2111a-members.json" \
    --w-root "$R" --w-pin "$R/splines/${T}_CH.xml.gz=$RED" "${@:7}" --out "$6" >> "$R/logs/trace_check.log" 2>&1
}
tcheck reduce "$R/traces/reduce_$T.trace" "$PRIV/genie_xsec/v3_04_00/NULL/$Q/data/gxspl-NUsmall.xml" "$SRC" "$R" \
  "$R/trace_check_reduce.json" || need 1 "trace check (reduce)"
tcheck graphs "$R/traces/graphs_$T.trace" "$R/splines/${T}_CH.xml.gz" "$RED" "$R" "$R/trace_check_graphs.json" \
  || need 1 "trace check (graphs)"
pass "reduce, spline check, flux, gspl2root, and their traces"

W1="$R/work/t0"; mkdir -p "$W1"
PG_TRACE_DIR="$W1" timeout "$TO" bash "$HERE/run_gevgen_v3.sh" genie "$T" "$R/splines" "$NEV" "$SEED" "$W1" \
  "$R/flux_phi_t_0_100.root" > "$R/logs/genie.log" 2>&1
need $? "gevgen ($NEV events, the public seed)"
tcheck gevgen "$W1/gevgen.trace" "$R/splines/${T}_CH.xml.gz" "$RED" "$W1" "$R/trace_check_gevgen.json" \
  || need 1 "trace check (gevgen)"
pass "gevgen and its trace"

T2=G18_02a_00_000; Q2=G1802a00000-k250-e1000; X2=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/$Q2/data
PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" reduce "$T2" "$R/splines" > "$R/logs/reduce_slot2.log" 2>&1
need $? "slot 2's spline reduce"
S2=$(spin "$T2" 0)
TT=$T2 tcheck reduce "$R/traces/reduce_$T2.trace" "$X2/gxspl-NUsmall.xml" "$S2" "$R" "$R/trace_check_reduce_slot2.json" \
  --pin "$X2/gxspl-NUsmall.xml=$S2" --pin "$X2/README=$(spin "$T2" 1)" || need 1 "trace check (slot 2's reduce)"
V shape-check --fd 9 --members "$REC/G2111a-members.json" --members-check "$R/members_check.json" \
  --tool-check "$R/tool_check_strace.json" --traces "$R/trace_check_reduce.json" "$R/trace_check_graphs.json" \
  "$R/trace_check_gevgen.json" --slot2-reduce "$R/trace_check_reduce_slot2.json" > "$R/shape_check.json" 2> "$R/logs/shape.log"
need $? "the four real-shape checks"
pass "slot 2's reduce at its real path, and the four real-shape checks"

# the event and status files, deleted unread: sha256 and size kept in R/deleted.json only
"$PY" -I - "$W1" "$R/deleted.json" <<'EOF' || need 1 "deleting the event and status files"
import glob, hashlib, json, os, sys
w, out = sys.argv[1], sys.argv[2]
rec = {}
for p in sorted(glob.glob(os.path.join(w, "genie_v3.gst.root")) + glob.glob(os.path.join(w, "gntp.*.ghep.root"))
                + glob.glob(os.path.join(w, "genie-mcjob-*.status")) + glob.glob(os.path.join(w, "input-flux.root"))):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    key = "gevgen.status" if "mcjob" in p else "gntp.ghep.root" if ".ghep.root" in p else os.path.basename(p)
    rec[key] = {"sha256": h.hexdigest(), "bytes": os.path.getsize(p)}
    os.remove(p)
open(out, "w").write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
EOF
"$PY" -I - "$R" <<'EOF' > "$R/replay.json" || need 1 "the replay record"
import json, os, sys
r = sys.argv[1]
def load(n):
    t = open(os.path.join(r, n)).read()
    try:
        return json.loads(t)
    except ValueError:
        return json.loads(t.splitlines()[-1])
checks = {n: load(n) for n in ("tool_check_strace.json", "members_check.json", "dbconfig_check.json", "exe_check.json",
                               "trace_check_reduce.json", "trace_check_graphs.json", "trace_check_gevgen.json",
                               "trace_check_reduce_slot2.json", "shape_check.json")}
rec = {"schema": "covfix-pg-replay-run/1", "tune": "G21_11a_00_000", "seed": 123456789, "events": 100,
       "checks": {n: c.get("pass") is True for n, c in checks.items()},
       "gated": {n: [{"path": g["path"], "sha256": g["sha256"], "pinned_by": g["pinned_by"]} for g in c.get("gated", [])]
                 for n, c in checks.items() if n.startswith("trace_check")},
       "spline_opened": {n: c.get("initial_opened_spline") for n, c in checks.items() if n.startswith("trace_check")},
       "real_shapes": checks["shape_check.json"].get("checks")}
rec["pass"] = (all(rec["checks"].values()) and all(v is True for v in rec["spline_opened"].values())
               and isinstance(rec["real_shapes"], dict) and len(rec["real_shapes"]) == 4
               and all(v is True for v in rec["real_shapes"].values()))
print(json.dumps(rec, indent=1, sort_keys=True))
EOF
[ "$("$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["pass"])' "$R/replay.json")" = True ] || need 1 "the replay"
pass "the replay"
echo "[replay] done $(date -u +%FT%TZ)"
exit 0
