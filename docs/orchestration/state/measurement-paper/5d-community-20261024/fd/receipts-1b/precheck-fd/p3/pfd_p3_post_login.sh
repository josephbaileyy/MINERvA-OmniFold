#!/bin/bash
# 1B pre-check Part 1, after P3 (jobs 60991405 60991413 60991415 60991418 60991419 60991420 60991421): the receipt's
# records. Login node, 0 node-h. In order:
#   1. the COV2D fence (rs1_* and ens1_* allowed; an fd1b job still queued refuses); all 7 jobs terminal in sacct;
#   2. FIRST, before any P3 result is read: each job's in-lane probe against P2's (job 60990199) on the four thread
#      variables, SLURM_CPUS_PER_TASK, the affinity size and threadpool_info. A difference, or a missing or failed
#      probe, STOPs here (rc 5) and nothing else is read;
#   3. sacct for the jobs and their steps, with ElapsedRaw, and the node-h charged; Part 1's total with P2's 0.2631;
#   4. the wrapper's job logs, each lane's s5c lines, refusals or tracebacks;
#   5. the products: the 327 expected names, present or missing;
#   6. per product, meta only (no array is read), written to $V/p3/logs/meta-p3.jsonl, and summarised: threads,
#      seconds_unfold, peak_rss_kib, slurm_job, the module digest;
#   7. the module's atime sidecars;
#   8. stat-after vs P3's stat-before: an original's stat moving is reported as a STOP (rc 4) after printing; the
#      staged flux copy may move (ROOT reads it plainly);
#   9. a base64 tar of an explicit list of the small records (no product, no inventory).
# It writes only $V/p3/logs/{sacct-p3.psv,meta-p3.jsonl,stat-after.txt,probe-compare.txt}. Launched from a /dev/shm
# copy of itself ($1), which it deletes.
SELF=$1
JOBS="60991405 60991413 60991415 60991418 60991419 60991420 60991421"
P2JOB=60990199
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== pfd-p3-post rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. fence and the jobs' states"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$out"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear (or a P3 job is still queued)"; finish 3; }
for j in $JOBS; do
  st=$(sacct -X -j "$j" -n -P -o State | head -1); echo "job $j state: $st"
  case "$st" in PENDING*|RUNNING*|"") echo "STOP: job $j has not ended"; finish 3 ;; esac
done
echo "== 2. probes against P2's (before any P3 result is read)"
env -u PYTHONPATH "$PY" -I - "$V" "$P2JOB" $JOBS > "$V/p3/logs/probe-compare.txt" 2>&1 <<'PYEOF'
import json, sys
V, p2, jobs = sys.argv[1], sys.argv[2], sys.argv[3:]
KEYS = ("thread_variables", "SLURM_CPUS_PER_TASK", "affinity_size", "threadpool_info")
def load(path):
    try:
        return json.load(open(path))
    except Exception as e:
        return {"status": f"unreadable: {type(e).__name__}: {e}"}
ref = load(f"{V}/p2/lanes/threadprobe-{p2}.log")
print(f"P2 probe {p2}: status {ref.get('status')}")
bad = 0
for j in jobs:
    d = load(f"{V}/p3/lanes/threadprobe-{j}.log")
    diffs = [k for k in KEYS if d.get(k) != ref.get(k)]
    ok = d.get("status") == "ok" and ref.get("status") == "ok" and not diffs
    print(f"P3 probe {j}: status {d.get('status')}; differing keys {diffs}; {'MATCH' if ok else 'DIFFERS'}")
    for k in diffs:
        print(f"  {k}: P2 {json.dumps(ref.get(k), sort_keys=True)}")
        print(f"  {k}: P3 {json.dumps(d.get(k), sort_keys=True)}")
    bad += not ok
print("PROBES:", "ALL MATCH P2" if bad == 0 else f"{bad} DIFFER")
sys.exit(0 if bad == 0 else 5)
PYEOF
pc=$?
cat "$V/p3/logs/probe-compare.txt"
[ "$pc" -eq 0 ] || { echo "STOP: a P3 probe differs from P2's or is missing; nothing else is read (to the director)"; finish 5; }
echo "== 3. sacct"
: > "$V/p3/logs/sacct-p3.psv"
for j in $JOBS; do sacct -j "$j" -n -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,AllocCPUS,MaxRSS,Start,End >> "$V/p3/logs/sacct-p3.psv"; done
cat "$V/p3/logs/sacct-p3.psv"
awk -F'|' '$1 !~ /\./ { s += $6 * $7; n++ } END { printf "P3 charged node-h = sum(ElapsedRaw x NNodes) / 3600 = %d / 3600 = %.4f over %d jobs (reserved 17.5); Part 1 total with P2 0.2631 = %.4f (cap 18.5)\n", s, s/3600, n, s/3600 + 0.2631 }' "$V/p3/logs/sacct-p3.psv"
echo "== 4. logs"
for j in $JOBS; do echo "-- job log $j"; cat "$V"/p3/logs/fd1b_pfd_p3_j*_"$j".out 2>&1; done
echo "-- lanes"; for f in "$V"/p3/lanes/line*-*.log; do echo "## $(basename "$f")"; grep -E '^\[s5c\]|^\{"out"|refusing|DEVIATION' "$f"; done
echo "-- refusals or tracebacks in lane logs"; grep -l -i -E 'Traceback|refusing' "$V"/p3/lanes/line*-*.log "$V"/p3/lanes/logs/*.log 2>/dev/null
echo "== 5-7. products, meta (meta only) and atime sidecars"
env -u PYTHONPATH "$PY" -I - "$V" "$P2JOB" $JOBS <<'PYEOF'
import json, sys
from pathlib import Path
import numpy as np
V, p2, jobs = Path(sys.argv[1]), sys.argv[2], set(sys.argv[3:])
det = ["GEANT_Neutron_0", "GEANT_Neutron_1", "GEANT_Pion_0", "GEANT_Pion_1", "GEANT_Proton_0", "GEANT_Proton_1",
       "MinosEfficiency_0", "MinosEfficiency_1"]
expect = [f"fd1b_pfd_{m}_{u}.npz" for m in ("A", "B", "Dnom") for u in ["CV"] + [f"Flux_{i}" for i in range(100)] + det]
present = [n for n in expect if (V / "unf" / n).exists()]
extra = sorted(p.name for p in (V / "unf").glob("fd1b_pfd_*.npz") if p.name not in set(expect))
missing = [n for n in expect if n not in set(present)]
print(f"products: expected {len(expect)}, present {len(present)}, missing {len(missing)} {missing[:10]}, extra {extra}")
rows = []
with open(V / "p3" / "logs" / "meta-p3.jsonl", "w") as fh:
    for n in present:
        with np.load(V / "unf" / n, allow_pickle=False) as z:
            m = json.loads(str(z["meta"]))
        r = {"product": n, "mode": m.get("mode"), "universe": m.get("universe"), "threads": m.get("threads"),
             "seconds_unfold": m.get("seconds_unfold"), "peak_rss_kib": m.get("peak_rss_kib"), "slurm_job": m.get("slurm_job"),
             "fd_1b_precheck_fd.py": m.get("code_sha256", {}).get("fd_1b_precheck_fd.py")}
        rows.append(r)
        fh.write(json.dumps(r) + "\n")
p3 = [r for r in rows if r["slurm_job"] in jobs]
print(f"meta: {len(rows)} products read (meta only); from P3 jobs {len(p3)}, from P2 {sum(r['slurm_job'] == p2 for r in rows)}, "
      f"other jobs {sorted({r['slurm_job'] for r in rows} - jobs - {p2})}")
print(f"threads values {sorted({r['threads'] for r in rows})}; module digests {sorted({r['fd_1b_precheck_fd.py'] for r in rows})}")
if p3:
    s = sorted(r["seconds_unfold"] for r in p3); q = sorted(r["peak_rss_kib"] for r in p3)
    print(f"P3 seconds_unfold min {s[0]} median {s[len(s)//2]} max {s[-1]} (unit 1370); peak_rss_kib max {q[-1]} (limit 44040192)")
moved, files = [], 0
for f in sorted((V / "unf").glob("atime-*.json")):
    d = json.load(open(f)); files += 1
    if d["moved"]:
        moved.append((f.name, d["moved"]))
print(f"atime sidecars: {files}; with moved files: {len(moved)} {moved[:5]}")
PYEOF
echo "== 8. stat-after vs P3's stat-before"
cut -d'|' -f1 "$V/p3/logs/stat-before.txt" | while read -r f; do stat -c '%n|%s|%Y|%X' "$f" 2>&1; done > "$V/p3/logs/stat-after.txt"
cat "$V/p3/logs/stat-after.txt"
orig_moved=$(diff <(grep -v '/stage/' "$V/p3/logs/stat-before.txt") <(grep -v '/stage/' "$V/p3/logs/stat-after.txt") | grep -c '^>')
staged_moved=$(diff <(grep '/stage/' "$V/p3/logs/stat-before.txt") <(grep '/stage/' "$V/p3/logs/stat-after.txt") | grep -c '^>')
echo "originals changed: $orig_moved; staged flux copy changed: $staged_moved"
rc=0
[ "$orig_moved" -eq 0 ] || { echo "STOP (report): an original's stat moved:"; diff "$V/p3/logs/stat-before.txt" "$V/p3/logs/stat-after.txt"; rc=4; }
echo "== 9. records (base64 tar, explicit list)"
list=(p3/logs/submit-p3.txt p3/logs/submit-p3.out p3/logs/stat-before.txt p3/logs/stat-after.txt p3/logs/sacct-p3.psv
      p3/logs/meta-p3.jsonl p3/logs/probe-compare.txt p3/tables/tasks-p3.tsv)
for f in "$V"/p3/logs/fd1b_pfd_p3_j*.out "$V"/p3/lanes/threadprobe-*.log "$V"/p3/lanes/line*-*.log "$V"/p3/lanes/logs/*.log "$V"/unf/atime-*.json; do
  [ -f "$f" ] && list+=("${f#$V/}")
done
present=(); for f in "${list[@]}"; do [ -f "$V/$f" ] && present+=("$f"); done
echo "files in the tar: ${#present[@]}"
for f in "${present[@]}"; do echo "sha256 $(sha256sum "$V/$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
tar -C "$V" -cf - "${present[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
finish "$rc"
