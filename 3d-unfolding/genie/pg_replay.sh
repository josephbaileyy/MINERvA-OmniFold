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

refuse() { echo "[replay] refusing: $1" >&2; exit 2; }
[ "$1" = "--workdir" ] && [ $# -eq 2 ] || refuse "usage: --workdir R"
R=$2
case "$R" in /*) ;; *) refuse "R must be absolute" ;; esac
[ -d "$R" ] && [ -z "$(ls -A "$R")" ] || refuse "R must be an existing empty directory"
[ "$(cd "$R" && pwd -P)" = "$(pwd -P)" ] || refuse "cwd is not R"
[ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] || refuse "TMPDIR must exist"
pin() { python3 -I -c 'import json,sys; v=json.load(open(sys.argv[1]))[sys.argv[2]]; print(v or "")' "$HERE/pg_pins.json" "$1"; }
STRACE=$(pin strace_path); STRACE_SHA=$(pin strace_sha256); DBCONFIG_SHA=$(pin dbconfig_sha256)
[ -n "$STRACE" ] && [ -n "$STRACE_SHA" ] && [ -n "$DBCONFIG_SHA" ] || refuse "pg_pins.json is not filled (R1)"
mkdir -p "$R/logs" "$R/splines" "$R/traces" "$R/work" || refuse "cannot create R's directories"
need() { [ "$1" -eq 0 ] || { echo "[replay] STOP: $2 rc=$1"; exit 1; }; }
pass() { echo "[replay] $1: pass"; }
anaenv() { source "$D/setup_salloc_env.sh" > "$R/logs/env-$1.log" 2>&1; export TMPDIR PYTHONDONTWRITEBYTECODE=1; }
V() { python3 -I -B "$HERE/pg_verify.py" "$@"; }
echo "[replay] start $(date -u +%FT%TZ) host=$(hostname)"

exec 9< "$STRACE" || need 1 "open strace"
FDD=/proc/self/fd; [ -d "$FDD" ] || FDD=/dev/fd
V tool-check --path "$FDD/9" --sha256 "$STRACE_SHA" --self-test > "$R/tool_check_strace.json" 2> "$R/logs/tool.log"
need $? "strace (its pinned sha through the descriptor, and the self-test)"
V members-check --root "$PRIV" --members "$REC/G2111a-members.json" > "$R/members_check.json" 2> "$R/logs/members.log"
need $? "slot 1's private product against its pinned members"
V tool-check --path "$PRIV/.upsfiles/dbconfig" --sha256 "$DBCONFIG_SHA" > "$R/dbconfig_check.json" 2> "$R/logs/dbconfig.log"
need $? "slot 1's UPS database file"
( source "$HERE/setup_genie_v3.sh" "$T" "$R/splines" > /dev/null 2>&1 || exit 1; command -v gevgen && command -v gspl2root ) \
  > "$R/exe.txt" 2> "$R/logs/exe.log" || need 1 "resolve gevgen and gspl2root"
V exe-check --manifest "$REC/genie-manifest.json" $(sed 's/^/--path /' "$R/exe.txt") > "$R/exe_check.json" 2>> "$R/logs/exe.log"
need $? "gevgen and gspl2root against the manifest"
pass "strace, the private product, the programs"
export PG_STRACE_FD=9

PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" reduce "$T" "$R/splines" > "$R/logs/reduce.log" 2>&1
need $? "spline reduce"
( anaenv a
  python3 -B "$HERE/gen5d_v3.py" make-flux --phi-t-dir "$PHIT" --out "$R/flux_phi_t_0_100.root" || exit 1
  python3 -B "$HERE/gen5d_v3.py" spline-check --tune "$T" --source "$PRIV/genie_xsec/v3_04_00/NULL/$Q/data/gxspl-NUsmall.xml" \
    --reduced "$R/splines/${T}_CH.xml.gz" --readme "$PRIV/genie_xsec/v3_04_00/NULL/$Q/data/README" \
    --out "$R/spline_check.json" ) > "$R/logs/flux_and_spline.log" 2>&1
need $? "flux file or spline check"
PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" graphs "$T" "$R/splines" "$R/graphs_$T.root" > "$R/logs/graphs.log" 2>&1
need $? "gspl2root"
RED=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reduced"]["sha256"])' "$R/spline_check.json")
SRC=$(python3 -I -c 'import ast,sys
t = ast.parse(open(sys.argv[1]).read())
print(next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PG_SPLINE_PINS")[sys.argv[2]][0])' "$HERE/gen5d_v3.py" "$T")
tcheck() {   # tcheck ROLE TRACE SPLINE SPLINE_SHA CWD OUT
  V trace-check --trace "$2" --rc 0 --role "$1" --tune "$T" --spline "$3" --spline-sha256 "$4" --cwd "$5" \
    --record "$REC/PG-RECORD.json" --manifest "$REC/genie-manifest.json" --private-members "$REC/G2111a-members.json" \
    --w-root "$R" --w-pin "$R/splines/${T}_CH.xml.gz=$RED" --out "$6" >> "$R/logs/trace_check.log" 2>&1
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

# the event and status files, deleted unread: sha256 and size kept in R/deleted.json only
python3 -I - "$W1" "$R/deleted.json" <<'EOF' || need 1 "deleting the event and status files"
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
python3 -I - "$R" <<'EOF' > "$R/replay.json" || need 1 "the replay record"
import json, os, sys
r = sys.argv[1]
def load(n):
    t = open(os.path.join(r, n)).read()
    try:
        return json.loads(t)
    except ValueError:
        return json.loads(t.splitlines()[-1])
checks = {n: load(n) for n in ("tool_check_strace.json", "members_check.json", "dbconfig_check.json", "exe_check.json",
                               "trace_check_reduce.json", "trace_check_graphs.json", "trace_check_gevgen.json")}
rec = {"schema": "covfix-pg-replay-run/1", "tune": "G21_11a_00_000", "seed": 123456789, "events": 100,
       "checks": {n: c.get("pass") is True for n, c in checks.items()},
       "gated": {n: [{"path": g["path"], "sha256": g["sha256"], "pinned_by": g["pinned_by"]} for g in c.get("gated", [])]
                 for n, c in checks.items() if n.startswith("trace_check")},
       "spline_opened": {n: c.get("initial_opened_spline") for n, c in checks.items() if n.startswith("trace_check")}}
rec["pass"] = all(rec["checks"].values()) and all(rec["spline_opened"].values())
print(json.dumps(rec, indent=1, sort_keys=True))
EOF
[ "$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["pass"])' "$R/replay.json")" = True ] || need 1 "the replay"
pass "the replay"
echo "[replay] done $(date -u +%FT%TZ)"
exit 0
