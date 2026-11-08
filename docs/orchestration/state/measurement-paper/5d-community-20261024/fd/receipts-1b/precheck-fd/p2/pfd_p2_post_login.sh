#!/bin/bash
# 1B pre-check Part 1, after P2 (job 60990199): the receipt's records. Login node, 0 node-h. In order:
#   1. the COV2D fence (rs1_* and ens1_* allowed); job 60990199 must have ended (sacct state not PENDING or RUNNING);
#   2. sacct for the job and its steps, with ElapsedRaw, and the node-h it charged (ElapsedRaw x NNodes / 3600);
#   3. the wrapper's job log, the in-lane thread probe, each lane's s5c lines, refusals or tracebacks, the products;
#   4. walls: the bound module's `walls` subcommand from the deploy (writes $V/p2/walls.json, refuses to overwrite);
#   5. per product, from its meta only: mode, universe, threads, seconds_unfold, peak_rss_kib, slurm_job, module digest
#      (no product array is read);
#   6. the module's atime sidecars;
#   7. stat-after of the same five files as stat-before, compared: an original's (npz, bkg, pins, bank cv.npz) atime,
#      mtime or size moving is reported as a STOP; the staged flux copy is read plainly by ROOT, so its atime may move;
#   8. a base64 tar of an explicit list of the small records (no product, no inventory).
# It writes only $V/p2/walls.json and $V/p2/logs/{sacct-p2.psv,stat-after.txt}. Launched from a /dev/shm copy ($1).
SELF=$1
J=60990199
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== pfd-p2-post rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. fence and the job's state"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$out"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear (or job $J is still queued)"; finish 3; }
state=$(sacct -X -j "$J" -n -P -o State | head -1)
echo "job $J state: $state"
case "$state" in PENDING*|RUNNING*|"") echo "STOP: job $J has not ended"; finish 3 ;; esac
echo "== 2. sacct"
sacct -j "$J" -n -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocCPUS,MaxRSS,Start,End | tee "$V/p2/logs/sacct-p2.psv"
read -r er nn <<< "$(sacct -X -j "$J" -n -P -o ElapsedRaw,NNodes | head -1 | tr '|' ' ')"
awk -v e="$er" -v n="$nn" 'BEGIN { printf "charged node-h = ElapsedRaw %d x NNodes %d / 3600 = %.4f (reserved 1.0; cap 18.5)\n", e, n, e*n/3600 }'
echo "== 3. logs"
echo "-- job log"; cat "$V/p2/logs/fd1b_pfd_p2_$J.out" 2>&1
echo "-- thread probe"; cat "$V/p2/lanes/threadprobe-$J.log" 2>&1
echo "-- lanes"; for f in "$V"/p2/lanes/line*-"$J".log; do echo "## $(basename "$f")"; grep -E '^\[s5c\]|^\{"out"|refusing|DEVIATION' "$f"; done
echo "-- refusals or tracebacks in lane logs"; grep -l -i -E 'Traceback|refusing' "$V"/p2/lanes/line*-"$J".log "$V"/p2/lanes/logs/*.log 2>/dev/null
echo "-- products"; ls -l "$V/unf"
echo "== 4. walls"
nice -n 19 env -u PYTHONPATH "$PY" -I "$V/deploy/nd-unfolding/fd_1b_precheck_fd.py" walls --unfolds "$V/unf" --out "$V/p2/walls.json"
echo "walls rc=$?"
cat "$V/p2/walls.json" 2>&1
echo "== 5. per-product meta (meta only)"
env -u PYTHONPATH "$PY" -I - "$V/unf" <<'PYEOF'
import json, sys
from pathlib import Path
import numpy as np
for p in sorted(Path(sys.argv[1]).glob("fd1b_pfd_*.npz")):
    with np.load(p, allow_pickle=False) as z:
        m = json.loads(str(z["meta"]))
    print(json.dumps({"product": p.name, "mode": m.get("mode"), "universe": m.get("universe"), "threads": m.get("threads"),
                      "seconds_unfold": m.get("seconds_unfold"), "peak_rss_kib": m.get("peak_rss_kib"),
                      "slurm_job": m.get("slurm_job"), "numpy": m.get("numpy_version"),
                      "fd_1b_precheck_fd.py": m.get("code_sha256", {}).get("fd_1b_precheck_fd.py")}))
PYEOF
echo "== 6. atime sidecars"
for f in "$V"/unf/atime-*.json; do
  env -u PYTHONPATH "$PY" -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1].rsplit("/",1)[1], "files", len(d["files"]), "moved", d["moved"])' "$f"
done
echo "== 7. stat-after vs stat-before"
cut -d'|' -f1 "$V/p2/logs/stat-before.txt" | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > "$V/p2/logs/stat-after.txt"
cat "$V/p2/logs/stat-after.txt"
orig_moved=$(diff <(grep -v '/stage/' "$V/p2/logs/stat-before.txt") <(grep -v '/stage/' "$V/p2/logs/stat-after.txt") | grep -c '^>')
staged_moved=$(diff <(grep '/stage/' "$V/p2/logs/stat-before.txt") <(grep '/stage/' "$V/p2/logs/stat-after.txt") | grep -c '^>')
echo "originals changed: $orig_moved; staged flux copy changed: $staged_moved"
rc=0
[ "$orig_moved" -eq 0 ] || { echo "STOP (report): an original's stat moved:"; diff "$V/p2/logs/stat-before.txt" "$V/p2/logs/stat-after.txt"; rc=4; }
echo "== 8. records (base64 tar, explicit list)"
list=(p2/logs/submit-p2.txt p2/logs/submit-p2.out p2/logs/stat-before.txt p2/logs/stat-after.txt p2/logs/sacct-p2.psv
      "p2/logs/fd1b_pfd_p2_$J.out" "p2/lanes/threadprobe-$J.log" p2/tables/tasks-p2.tsv p2/walls.json)
for f in "$V"/p2/lanes/line*-"$J".log "$V"/p2/lanes/logs/*.log "$V"/unf/atime-*.json; do [ -f "$f" ] && list+=("${f#$V/}"); done
for f in "${list[@]}"; do [ -f "$V/$f" ] && echo "sha256 $(sha256sum "$V/$f" | cut -d' ' -f1) $f" || echo "ABSENT $f"; done
present=(); for f in "${list[@]}"; do [ -f "$V/$f" ] && present+=("$f"); done
echo "== TAR BEGIN"
tar -C "$V" -cf - "${present[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
finish "$rc"
