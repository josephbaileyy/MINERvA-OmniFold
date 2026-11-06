#!/bin/bash
# 1B binding 3, stage 3's readout (A2.1 §11; amendment 2 §12 item 2), a login step after the receipt job ends: its
# sacct; the receipt record read through O_NOATIME, its sha256 from those bytes, and PASS, STOP or INVALID (amendment
# 2 §4: no receipt.json is INVALID); the validation, the floor check, the pair counts, N_clip, the cross terms and the
# record's own atime check; then the stat-after over connect-receipt.sh's source list, compared with its stat-before.
# Stage 3's PASS record is a PASS here with no atime moved and every source's stat unchanged. Argument 1: the receipt's
# job id (connect-receipt.log). Writes only $W/logs/readout.*; refuses if they exist. Not under set -u.
set -o pipefail
J=$1
case "$J" in *[!0-9]*|"") echo "STOP the job id is not a number: '$J'"; exit 2 ;; esac
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102/stage1/a2; DD=$W/deploy
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -d "$W/logs" ] || { echo "STOP $W/logs is absent"; exit 2; }
[ -e "$W/logs/readout.log" ] && { echo "STOP $W/logs/readout.log exists"; exit 2; }
st=$(sacct -j "$J" -X -n -P -o State | head -1)
case "$st" in PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|"") echo "not ended: job $J state '$st'; nothing written"; exit 1 ;; esac
exec >> "$W/logs/readout.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) job=$J"
grep -q "^Submitted batch job $J$" "$W/logs/connect-receipt.log" || stop "job $J is not the one connect-receipt submitted"
sacct -j "$J" -n -P -o JobID,JobName,State,Elapsed,Start,End,NodeList,NNodes,ExitCode,MaxRSS
sacct -j "$J" -X -n -P -o JobID,ElapsedRaw,TimelimitRaw,AllocTRES%80,Partition,QOS
echo "state=$st"
grep -hE "refusing|Traceback|Error|Killed|oom" "$W"/lanes/line0-"$J".log "$W"/lanes/logs/*.log 2>/dev/null | head -8
source "$DD/setup_salloc_env.sh" > "$W/logs/readout.env.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
python3 -B - "$W/receipt.json" "$st" > "$W/logs/readout.out" 2>&1 <<'PYR'
import hashlib, json, os, sys
path, state = sys.argv[1], sys.argv[2]
if not os.path.exists(path):
    print("RECEIPT-READOUT verdict=INVALID why=no receipt.json (job state %s)" % state)
    sys.exit(3)
fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
with os.fdopen(fd, "rb") as fh:
    raw = fh.read()
r = json.loads(raw.decode())
print("receipt.json sha256 %s bytes %d" % (hashlib.sha256(raw).hexdigest(), len(raw)))
print("step", r["step"], "schema", r["schema"], "n1_bound", r["n1_bound"], "max_abs_ratio", json.dumps(r["max_abs_ratio"]))
for k, v in r["exact"].items():
    print("exact", k, json.dumps({x: v[x] for x in ("rows", "pairs_past_screen", "rows_above") if x in v}))
for k, v in r["validation"].items():
    print("validation", k, json.dumps(v)[:300])
d = r["denominator"]
print("denominator draws_with_nonpositive_cells", len(d["draws_with_nonpositive_cells"]), "n1", json.dumps(d["n1"])[:300])
print("n_clip", json.dumps(r["n_clip"]))
print("crossterm", json.dumps(r["crossterm"])[:600])
print("negative_weight_universes", len(r["negative_weight_universes"]))
moved = r["atime"]["moved"]
print("atime opened", len(r["atime"]["files"]), "moved", len(moved), moved[:4])
print("stop_reasons", r["stop_reasons"])
ok = r["verdict"] == "PASS" and not moved and state == "COMPLETED"
print("RECEIPT-READOUT verdict=%s atime_moved=%d state=%s -> %s" % (r["verdict"], len(moved), state,
                                                                    "PASS" if ok else "NOT PASS"))
sys.exit(0 if ok else 1)
PYR
rc=$?; cat "$W/logs/readout.out"; echo "readout rc=$rc"
xargs -a "$W/logs/sources.txt" -d '\n' stat -c '%X %Y %s %n' > "$W/logs/readout.stat-after.txt" || stop "a source is missing"
if cmp -s "$W/logs/stat-before.txt" "$W/logs/readout.stat-after.txt"; then
  echo "sources atime/mtime/size: UNCHANGED ($(wc -l < "$W/logs/stat-before.txt"))"
else
  diff "$W/logs/stat-before.txt" "$W/logs/readout.stat-after.txt" | head -20; stop "a source's stat moved (a deviation, not restored)"
fi
[ "$rc" = "0" ] || stop "the receipt is not PASS (rc=$rc)"
echo "end=$(date -u +%FT%TZ)"
