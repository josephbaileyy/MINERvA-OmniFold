#!/bin/bash
# pg_replay.sh --workdir R -- COVFIX PG's B3 replay for slot 1 (state/2d-closeout/covfix-20261122/pg/PLAN-SLOT1-PROBE.md,
# approved; COVFIX rev 12 section 4.1, 783188cd), on a login node, from a git-archive deploy of the pinned commit.
#
# It runs pg_generate.sh's checks for slot 1 (G21_11a_00_000) and slot 2 (G18_02a_00_000), each step under the same
# strace prefix and checks (README-pg.md lists them), in this order:
#   strace (pinned sha through fd 9, self-test); CVMFS's revision; slot 1's private product and its UPS file; both
#   slots' setups (programs, awk, LD_LIBRARY_PATH, GXMLPATH); slot 1's reduce, its completeness, the argv check, the
#   flux and spline check, gspl2root; slot 1's one-event coverage run (public seed, GEVGDriver at DEBUG); one
#   100-event gevgen and its gntpc at seed 123456789 (public, below the sealed range; F1's flux, target and energy
#   range); slot 2's reduce at its real CVMFS path, its completeness and its coverage run (nothing generated for slot
#   2); the four real-shape checks and the three host checks; CVMFS's revision again.
# All of it must pass here before slot 2 is generated. A trap deletes every event and status file of the public-seed
# runs on any exit, STOP included; their sha256, size and whether they hold the public seed are kept in R/deleted.json.
# R/replay.json holds every check's pass, the spline opens, the gated files, the programs run, the revision values and
# the coverage logs' hashes, with the gst's schema (trees, branches, streamer info) that every sealed gst must match.
# Round 4: each public-seed ROOT file is also decoded (pg_lib.py's leak scan, inflated objects included) as the positive
# control of the publication scan, and a deletion that fails is retried on exit and leaves a STOP.
# Exit 0 when every step and check passes, 1 on a STOP, 2 on a refusal before any step.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D="$(cd "$HERE/../.." && pwd)"
T=G21_11a_00_000; Q=G2111a00000-k250-e1000
SEED=123456789; NEV=100; TO=3600
PHIT=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
PRIV=/pscratch/sd/j/josephrb/covfix-pg/products   # slot 1's private genie_xsec (run_gevgen_v3.sh, setup_genie_v3.sh)
REC="$D/docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
CVMFS_REPO=/cvmfs/larsoft.opensciencegrid.org
PY=/usr/bin/python3.11   # the checks' interpreter outside the analysis environment (the probe's; not the node's python3)

refuse() { echo "[replay] refusing: $1" >&2; exit 2; }
[ "$1" = "--workdir" ] && [ $# -eq 2 ] || refuse "usage: --workdir R"
R=$2
case "$R" in /*) ;; *) refuse "R must be absolute" ;; esac
[ -d "$R" ] && [ -z "$(ls -A "$R")" ] || refuse "R must be an existing empty directory"
[ "$(cd "$R" && pwd -P)" = "$(pwd -P)" ] || refuse "cwd is not R"
[ "$(cd "$R" && pwd -P)" = "$R" ] || refuse "R must be its own physical path"
[ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] || refuse "TMPDIR must exist"
[ -x "$PY" ] || refuse "$PY is missing"
for v in LD_PRELOAD LD_AUDIT BASH_ENV ENV PYTHONPATH PYTHONSTARTUP PYTHONUSERBASE GXMLPATHS GALGCONF; do   # hooks no
  # trace attributes, and GENIE's XML lookups other than GXMLPATH
  [ -z "${!v:-}" ] || refuse "$v is set"
done
pin() { "$PY" -I -c 'import json,sys; v=json.load(open(sys.argv[1]))[sys.argv[2]]; print(v or "")' "$HERE/pg_pins.json" "$1"; }
STRACE=$(pin strace_path); STRACE_SHA=$(pin strace_sha256); DBCONFIG_SHA=$(pin dbconfig_sha256)
SYSPINS=$("$PY" -I -c 'import json,sys
v = json.load(open(sys.argv[1])).get("system_tools") or {}
print("".join(f"--system-pin\n{k}={h}\n" for k, h in sorted(v.items()) if k and h))' "$HERE/pg_pins.json")
[ -n "$STRACE" ] && [ -n "$STRACE_SHA" ] && [ -n "$DBCONFIG_SHA" ] && [ -n "$SYSPINS" ] || refuse "pg_pins.json is not filled (R1)"
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
spin() { "$PY" -I -c 'import ast,sys
t = ast.parse(open(sys.argv[1]).read())
print(next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PG_SPLINE_PINS")[sys.argv[2]][int(sys.argv[3])])' "$HERE/gen5d_v3.py" "$1" "$2"; }
ulimit -c 0 || refuse "cannot set the core limit to 0"   # Q2: no core file; a piped core handler ignores the limit (recorded, out of scope)
echo "[replay] start $(date -u +%FT%TZ) host=$(hostname)"
T2=G18_02a_00_000; Q2=G1802a00000-k250-e1000
X1="$PRIV/genie_xsec/v3_04_00/NULL/$Q/data"; X2="$CVMFS_REPO/products/genie_xsec/v3_04_00/NULL/$Q2/data"
W1="$R/work/t0"; C1="$R/coverage/$T"; C2="$R/coverage/$T2"; M1="$R/gst"
DELETED=""
delete_events() {   # D5: on every exit, once the writers have ended (every step here runs in the foreground), the event
  # and status files of the public-seed runs are deleted; R/deleted.json keeps each file's sha256 and size, whether
  # its bytes hold the public seed as text, and for a ROOT file the decoded scan and (the gst) its schema. Every file's
  # unlink is tried even if reading it fails; any file left is a failure, and the trap tries again on exit
  [ -z "$DELETED" ] || return 0
  "$PY" -I -B - "$R/deleted.json" "$HERE" "$W1" "$C1" "$C2" "$M1" <<'EOF' || return 1
import glob, hashlib, json, os, sys
out, here, dirs = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, here)
import pg_lib
forms = [b"123456789", format(123456789, "x").encode(), format(123456789, "X").encode()]
pats = ("genie_v3.gst.root", "gntp.*.ghep.root", "genie-mcjob-*.status", "input-flux.root", "*_ALL.gst.root")
try:
    rec = json.load(open(out)) if os.path.exists(out) else {}
except Exception:
    rec = None
if not (type(rec) is dict and all(type(v) is dict for k, v in rec.items() if not k.startswith("_"))):
    rec = {"_prior": "unreadable"}                   # a broken earlier record, or one of the wrong shape: say so
bad = 0
def save():                                          # whole or not at all: a write cut short leaves the last one
    tmp = out + ".tmp"
    with open(tmp, "w") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, out)
for key, w in zip(("t0", "coverage_slot1", "coverage_slot2", "merged"), dirs):
    got = rec.setdefault(key, {})
    for p in sorted(sum((glob.glob(os.path.join(w, x)) for x in pats + (("gevgen.log",) if key.startswith("cov") else ())), [])):
        name = "gevgen.status" if "mcjob" in p else "gntp.ghep.root" if ".ghep.root" in p else os.path.basename(p)
        e = {}
        try:
            with open(p, "rb") as f:
                data = f.read()
            e = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                 "holds_public_seed": any(x in data for x in forms)}
            if p.endswith(".root"):
                try:
                    hits, st = pg_lib.leak_scan(os.path.dirname(p), [os.path.basename(p)], [123456789],
                                                decode_all=True)             # decoded even after a raw hit (K6)
                    e["decoded"] = {"holds_seed": any(r is not None for r, _ in hits),       # the bytes, decoded
                                    "name_holds_seed": any(r is None for r, _ in hits),      # the name, apart
                                    "int32_count": st["int32_count"], "codecs": st["codecs"],
                                    "bytes_inflated": st["bytes_inflated"], "hits": st["hits"]}
                    if name.endswith(".gst.root"):
                        e["schema"] = pg_lib.root_schema(p)
                except pg_lib.Refusal as r:
                    e["decoded"] = {"error": str(r).split(":")[0]}
                    bad = 1
        except Exception as x:                       # whatever fails, the file is still unlinked below
            e, bad = {"error": f"unreadable: {type(x).__name__}"}, 1
        got[name] = e
        try:
            save()                                   # the record first, so an abort cannot lose what was read
        except Exception:
            bad = 1
        try:
            os.remove(p)
        except OSError:
            bad = 1
    left = sum(len(glob.glob(os.path.join(w, x))) for x in pats)
    if left:
        got["_left"], bad = left, 1
save()
sys.exit(bad)
EOF
  DELETED=1
}
trap delete_events EXIT

exec 9< "$STRACE" || need 1 "open strace"
V tool-check --fd 9 --sha256 "$STRACE_SHA" --self-test > "$R/tool_check_strace.json" 2> "$R/logs/tool.log"
need $? "strace (its pinned sha through the descriptor, and the self-test)"
V revision --repo "$CVMFS_REPO" > "$R/revision_start.json" 2> "$R/logs/revision.log"
need $? "the CVMFS revision (start)"
pinhash() {   # Q1: every pinned CVMFS file (the genie manifest's, slot 2's spline and README) at the start and the end
  V pin-hash --manifest "$REC/genie-manifest.json" --products "$CVMFS_REPO/products" \
    --pin "$X2/gxspl-NUsmall.xml=$(spin "$T2" 0)" --pin "$X2/README=$(spin "$T2" 1)" > "$R/pin_hash_$1.json" \
    2>> "$R/logs/pin_hash.log"
  need $? "every pinned CVMFS file against its pin ($1)"
}
pinhash start
V members-check --root "$PRIV" --members "$REC/G2111a-members.json" > "$R/members_check.json" 2> "$R/logs/members.log"
need $? "slot 1's private product against its pinned members"
V tool-check --path "$PRIV/.upsfiles/dbconfig" --sha256 "$DBCONFIG_SHA" > "$R/dbconfig_check.json" 2> "$R/logs/dbconfig.log"
need $? "slot 1's UPS database file"
for TU in "$T" "$T2"; do   # each slot's setup: its programs, awk, LD_LIBRARY_PATH and GXMLPATH as the traced steps see them
  ( source "$HERE/setup_genie_v3.sh" "$TU" "$R/splines" > /dev/null 2>&1 || exit 1
    command -v gevgen && command -v gspl2root || exit 1
    printf '%s\n' "${LD_LIBRARY_PATH-}" > "$R/ld_library_path_$TU.txt"; command -v awk > "$R/awk_$TU.txt"
    printf '%s\n' "${GXMLPATH-}" > "$R/gxmlpath_$TU.txt" ) > "$R/exe_$TU.txt" 2>> "$R/logs/exe.log" || need 1 "resolve the programs ($TU)"
done
V exe-check --manifest "$REC/genie-manifest.json" $(sed 's/^/--path /' "$R/exe_$T.txt") \
  --ld-library-path "$(cat "$R/ld_library_path_$T.txt")" --system-path "$(cat "$R/awk_$T.txt")" > "$R/exe_check.json" 2>> "$R/logs/exe.log"
need $? "gevgen, gspl2root, awk and LD_LIBRARY_PATH"
pass "strace, the private product, the programs"
export PG_STRACE_FD=9

PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" reduce "$T" "$R/splines" > "$R/logs/reduce.log" 2>&1
need $? "spline reduce"
V reduce-check --source "$X1/gxspl-NUsmall.xml" --reduced "$R/splines/${T}_CH.xml.gz" --script "$HERE/run_gevgen_v3.sh" \
  > "$R/reduce_check.json" 2>> "$R/logs/reduce_check.log" || need 1 "reduce completeness"
V argv-check --script "$HERE/run_gevgen_v3.sh" > "$R/argv_check.json" 2>> "$R/logs/reduce_check.log" || need 1 "the coverage argv"
( anaenv a || exit 1
  python3 -B "$HERE/gen5d_v3.py" make-flux --phi-t-dir "$PHIT" --out "$R/flux_phi_t_0_100.root" || exit 1
  python3 -B "$HERE/gen5d_v3.py" spline-check --tune "$T" --source "$X1/gxspl-NUsmall.xml" \
    --reduced "$R/splines/${T}_CH.xml.gz" --readme "$X1/README" --out "$R/spline_check.json" ) > "$R/logs/flux_and_spline.log" 2>&1
need $? "flux file or spline check"
PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" graphs "$T" "$R/splines" "$R/graphs_$T.root" > "$R/logs/graphs.log" 2>&1
need $? "gspl2root"
RED=$("$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["reduced"]["sha256"])' "$R/spline_check.json")
SRC=$(spin "$T" 0)
tcheck() {   # tcheck ROLE TRACE SPLINE SPLINE_SHA CWD OUT [ARG ...]; TT selects the tune (slot 1 by default)
  local tu="${TT:-$T}" sp=() l
  while IFS= read -r l; do [ -z "$l" ] || sp+=("$l"); done <<< "$SYSPINS"
  V trace-check --trace "$2" --rc 0 --role "$1" --tune "$tu" --spline "$3" --spline-sha256 "$4" --cwd "$5" \
    --record "$REC/PG-RECORD.json" --manifest "$REC/genie-manifest.json" --private-members "$REC/G2111a-members.json" \
    --w-root "$R" --w-pin "$R/splines/${T}_CH.xml.gz=$RED" --gxmlpath "$(cat "$R/gxmlpath_$tu.txt")" \
    --xsec-data "$([ "$tu" = "$T" ] && echo "$X1" || echo "$X2")" "${sp[@]}" "${@:7}" --out "$6" >> "$R/logs/trace_check.log" 2>&1
}
tcheck reduce "$R/traces/reduce_$T.trace" "$X1/gxspl-NUsmall.xml" "$SRC" "$R" "$R/trace_check_reduce.json" \
  || need 1 "trace check (reduce)"
tcheck graphs "$R/traces/graphs_$T.trace" "$R/splines/${T}_CH.xml.gz" "$RED" "$R" "$R/trace_check_graphs.json" \
  --output "$R/graphs_$T.root" || need 1 "trace check (graphs)"
pass "reduce, its completeness, spline check, flux, gspl2root, and their traces"

GENIE_CFG="$CVMFS_REPO/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
V messenger --laconic "$GENIE_CFG/Messenger_laconic.xml" --out "$R/Messenger_pg.xml" > "$R/messenger_check.json" \
  2>> "$R/logs/coverage.log" || need 1 "the coverage messenger"
mkdir -p "$C1"
PG_TRACE_DIR="$C1" bash "$HERE/run_gevgen_v3.sh" coverage "$T" "$R/splines" "$C1" "$R/flux_phi_t_0_100.root" \
  "$R/Messenger_pg.xml" > "$R/logs/coverage_slot1.log" 2>&1 || need 1 "the coverage run (slot 1)"
tcheck coverage "$C1/coverage.trace" "$R/splines/${T}_CH.xml.gz" "$RED" "$C1" "$R/trace_check_coverage.json" \
  --messenger "$R/Messenger_pg.xml" || need 1 "trace check (coverage)"
V coverage-log --log "$C1/gevgen.log" --script "$HERE/run_gevgen_v3.sh" --reduced "$R/splines/${T}_CH.xml.gz" \
  > "$R/coverage_check.json" 2>> "$R/logs/coverage.log" || need 1 "spline coverage (slot 1)"
pass "slot 1's spline coverage, before its gevgen"

mkdir -p "$W1"
PG_TRACE_DIR="$W1" timeout "$TO" bash "$HERE/run_gevgen_v3.sh" genie "$T" "$R/splines" "$NEV" "$SEED" "$W1" \
  "$R/flux_phi_t_0_100.root" > "$R/logs/genie.log" 2>&1
need $? "gevgen ($NEV events, the public seed)"
ls "$W1"/gntp.*.ghep.root > /dev/null 2>&1 && need 1 "the wrapper left t0's GHEP"   # gntpc read it; the wrapper removes it
pass "t0's GHEP removed by the wrapper"
tcheck gevgen "$W1/gevgen.trace" "$R/splines/${T}_CH.xml.gz" "$RED" "$W1" "$R/trace_check_gevgen.json" \
  || need 1 "trace check (gevgen)"
tcheck gntpc "$W1/gntpc.trace" "" "" "$W1" "$R/trace_check_gntpc.json" --ghep-from-trace "$W1/gevgen.trace" \
  || need 1 "trace check (gntpc)"
mkdir -p "$M1"   # B6: hadd's output, under pg_generate's own name for slot 1's, so its schema is B3's too
( anaenv h || exit 1; hadd "$M1/genie_v3_g21_ALL.gst.root" "$W1/genie_v3.gst.root" ) > "$R/logs/hadd.log" 2>&1
need $? "hadd of the public gst"
pass "gevgen, gntpc, hadd and their traces"

PG_TRACE_DIR="$R/traces" bash "$HERE/run_gevgen_v3.sh" reduce "$T2" "$R/splines" > "$R/logs/reduce_slot2.log" 2>&1
need $? "slot 2's spline reduce"
S2=$(spin "$T2" 0)
RED2=$("$PY" -I -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$R/splines/${T2}_CH.xml.gz")
TT=$T2 tcheck reduce "$R/traces/reduce_$T2.trace" "$X2/gxspl-NUsmall.xml" "$S2" "$R" "$R/trace_check_reduce_slot2.json" \
  --pin "$X2/gxspl-NUsmall.xml=$S2" --pin "$X2/README=$(spin "$T2" 1)" || need 1 "trace check (slot 2's reduce)"
V reduce-check --source "$X2/gxspl-NUsmall.xml" --reduced "$R/splines/${T2}_CH.xml.gz" --script "$HERE/run_gevgen_v3.sh" \
  > "$R/reduce_check_slot2.json" 2>> "$R/logs/reduce_check.log" || need 1 "reduce completeness (slot 2)"
mkdir -p "$C2"
PG_TRACE_DIR="$C2" bash "$HERE/run_gevgen_v3.sh" coverage "$T2" "$R/splines" "$C2" "$R/flux_phi_t_0_100.root" \
  "$R/Messenger_pg.xml" > "$R/logs/coverage_slot2.log" 2>&1 || need 1 "the coverage run (slot 2)"
TT=$T2 tcheck coverage "$C2/coverage.trace" "$R/splines/${T2}_CH.xml.gz" "$RED2" "$C2" "$R/trace_check_coverage_slot2.json" \
  --w-pin "$R/splines/${T2}_CH.xml.gz=$RED2" --pin "$X2/gxspl-NUsmall.xml=$S2" --pin "$X2/README=$(spin "$T2" 1)" \
  --messenger "$R/Messenger_pg.xml" || need 1 "trace check (slot 2's coverage)"
V coverage-log --log "$C2/gevgen.log" --script "$HERE/run_gevgen_v3.sh" --reduced "$R/splines/${T2}_CH.xml.gz" \
  > "$R/coverage_check_slot2.json" 2>> "$R/logs/coverage.log" || need 1 "spline coverage (slot 2)"
pass "slot 2's reduce at its real path, its completeness and its spline coverage"

V shape-check --fd 9 --members "$REC/G2111a-members.json" --members-check "$R/members_check.json" \
  --tool-check "$R/tool_check_strace.json" --traces "$R/trace_check_reduce.json" "$R/trace_check_graphs.json" \
  "$R/trace_check_gevgen.json" --slot2-reduce "$R/trace_check_reduce_slot2.json" > "$R/shape_check.json" 2> "$R/logs/shape.log"
need $? "the four real-shape checks"
mkdir -p "$R/host"
V host-check --fd 9 --tmp "$R/host" --root "$CVMFS_REPO/products/genie/v3_04_00" --root "$PRIV" \
  --root "$CVMFS_REPO/products/genie_xsec/v3_04_00/NULL" > "$R/host_check.json" 2> "$R/logs/host.log"
need $? "the three host checks"
pinhash end
V revision --repo "$CVMFS_REPO" > "$R/revision_end.json" 2>> "$R/logs/revision.log"
need $? "the CVMFS revision (end)"
tcs=(); for f in "$R"/trace_check_*.json; do [ -e "$f" ] && tcs+=(--trace-check "$f"); done
V revision-compare --start "$R/revision_start.json" --end "$R/revision_end.json" "${tcs[@]}" > "$R/revision_compare.json" \
  2>> "$R/logs/revision.log"
need $? "the CVMFS revision changed and a file the replay read no longer matches its pin"
pass "the real-shape and host checks, and the CVMFS revision (or every file read re-hashed)"

delete_events || need 1 "deleting the event and status files"
"$PY" -I - "$R" <<'EOF' > "$R/replay.json" || need 1 "the replay record"
import json, os, sys
r = sys.argv[1]
def load(n):
    t = open(os.path.join(r, n)).read()
    try:
        return json.loads(t)
    except ValueError:
        return json.loads(t.splitlines()[-1])
names = ("tool_check_strace.json", "revision_start.json", "members_check.json", "dbconfig_check.json", "exe_check.json",
         "reduce_check.json", "argv_check.json", "trace_check_reduce.json", "trace_check_graphs.json",
         "messenger_check.json", "trace_check_coverage.json", "coverage_check.json", "trace_check_gevgen.json",
         "trace_check_gntpc.json", "trace_check_reduce_slot2.json", "reduce_check_slot2.json",
         "trace_check_coverage_slot2.json", "coverage_check_slot2.json", "shape_check.json", "host_check.json",
         "revision_end.json", "revision_compare.json", "pin_hash_start.json", "pin_hash_end.json")
checks = {n: load(n) for n in names}
traces = [n for n in names if n.startswith("trace_check")]
deleted = json.load(open(os.path.join(r, "deleted.json")))
rec = {"schema": "covfix-pg-replay-run/4", "tune": "G21_11a_00_000", "slot2": "G18_02a_00_000", "seed": 123456789,
       "events": 100, "checks": {n: c.get("pass") is True for n, c in checks.items()},
       "execs": {n: [{k: x.get(k) for k in ("path", "real", "sha256", "bound_by")} for x in checks[n].get("execs", [])]
                 for n in traces},
       "revision": {w: {k: checks[f"revision_{w}.json"].get(k) for k in ("revision", "root_hash")} for w in ("start", "end")},
       "gst_schema": deleted.get("t0", {}).get("genie_v3.gst.root", {}).get("schema"),
       "gst_merged_schema": deleted.get("merged", {}).get("genie_v3_g21_ALL.gst.root", {}).get("schema"),
       "gated": {n: [{"path": g["path"], "sha256": g["sha256"], "pinned_by": g["pinned_by"]} for g in checks[n].get("gated", [])]
                 for n in traces},
       "spline_opened": {n: checks[n].get("initial_opened_spline") for n in traces if n != "trace_check_gntpc.json"},
       "real_shapes": checks["shape_check.json"].get("checks"), "host": checks["host_check.json"].get("checks"),
       "coverage_log_sha256": {n: checks[n].get("log_sha256") for n in ("coverage_check.json", "coverage_check_slot2.json")}}
rec["pass"] = (all(rec["checks"].values()) and all(v is True for v in rec["spline_opened"].values())
               and all(isinstance(rec[k], dict) and bool(rec[k].get("keys")) for k in ("gst_schema", "gst_merged_schema"))
               and all(x["bound_by"] for v in rec["execs"].values() for x in v) and all(rec["execs"].values())
               and isinstance(rec["real_shapes"], dict) and len(rec["real_shapes"]) == 4
               and all(v is True for v in rec["real_shapes"].values())
               and isinstance(rec["host"], dict) and len(rec["host"]) == 3 and all(v is True for v in rec["host"].values()))
print(json.dumps(rec, indent=1, sort_keys=True))
EOF
[ "$("$PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["pass"])' "$R/replay.json")" = True ] || need 1 "the replay"
pass "the replay"
echo "[replay] done $(date -u +%FT%TZ)"
exit 0
