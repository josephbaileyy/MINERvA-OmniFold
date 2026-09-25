#!/bin/bash
# Claim the next Tier-S validation lines and launch them (s5c_valid_launch.sh), so several lanes
# share one declared population without overlap and fill it in table order (lines 0-119 first: the
# futility look needs them).
#
# Usage (login node, a queue line):  s5c_valid_next.sh <deploy_tree> <pinned_sha> <pool cpu|gpu>
# A claim is a file $NS/runs/s_valid/claims/<first>-<last> holding the job id (or pending:<pid> while
# the launch waits for a node), taken under a lock. The next claim is the lowest unclaimed line and
# the lines after it up to 32 (cpu) or 16 (gpu), stopping at the next claim. When every line is
# claimed, the first claim whose job has left the scheduler (or whose launcher died) and whose
# declared seeds are not all present is re-launched on the same lines: products already present are
# skipped by s5c_pseudo.py, never overwritten. With nothing left it prints NOTHING-TO-DO and exits 0.
# A failed launch releases its claim and returns the launcher's exit code (4 = concurrency).

DEPLOY=${1:?deploy}; PIN=${2:?sha}; POOL=${3:?cpu|gpu}
NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5c-20260924}
TABLE="$DEPLOY/docs/orchestration/state/s5c/s-valid-tasks.tsv"
CL="$NS/runs/s_valid/claims"
mkdir -p "$CL"
[ "$POOL" = cpu ] && SIZE=32 || SIZE=16
ids=$(squeue -h --me -o %i 2>/dev/null) || { echo "squeue failed; not choosing" >&2; exit 7; }

# The lock lives on fd 9 and must never reach the launcher: its nohup'd steps runner would inherit
# the open file description and keep the lock held for its whole allocation (it did: 2026-09-25,
# the GPU lane's runner blocked the CPU lane for 46 min). Hence `9>&-` on the launch below, and a
# lock file (.lock2) that no process of the defective version can still be holding.
exec 9> "$CL/.lock2"
flock 9
choice=$(/usr/bin/python3.11 - "$TABLE" "$CL" "$NS/runs/s_valid" "$SIZE" "$ids" <<'EOF'
import os, re, sys
from pathlib import Path
table, cl, out, size, ids = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]), set(sys.argv[5].split())
lines = [l for l in open(table) if l.strip() and not l.startswith("#")]
n = len(lines)
claims = []
for f in cl.iterdir():
    m = re.fullmatch(r"(\d+)-(\d+)", f.name)
    if m:
        claims.append((int(m.group(1)), int(m.group(2)), f.read_text().strip()))
claims.sort()
covered = [False] * n
for a, b, _ in claims:
    for i in range(a, b + 1):
        covered[i] = True
free = [i for i in range(n) if not covered[i]]
if free:
    a = free[0]
    b = a
    while b + 1 < n and b + 1 - a < size and not covered[b + 1]:
        b += 1
    print(f"NEW {a} {b}")
    sys.exit(0)
def seeds_present(i):
    f = lines[i].split("\t")
    arg = dict(zip(f, f[1:]))
    s0, s1 = map(int, arg["--pseudo-seeds"].split(":"))
    tag = f"{arg['--truth']}_a{float(arg['--amplitude']):g}"
    return all((out / f"{tag}_s{s}.npz").exists() for s in range(s0, s1 + 1))
def alive(holder):
    if holder.startswith("pending:"):
        try:
            os.kill(int(holder.split(":")[1]), 0)
            return True
        except (OSError, ValueError):
            return False
    return holder in ids
for a, b, holder in claims:
    if not alive(holder) and not all(seeds_present(i) for i in range(a, b + 1)):
        print(f"RETRY {a} {b}")
        sys.exit(0)
print("NOTHING-TO-DO")
EOF
)
rc=$?
if [ $rc -ne 0 ] || [ -z "$choice" ]; then echo "claim choice failed (exit $rc)" >&2; exit 2; fi
read -r kind first last <<< "$choice"
if [ "$kind" = NOTHING-TO-DO ]; then echo NOTHING-TO-DO; exit 0; fi
claim="$CL/$first-$last"
prev=$(cat "$claim" 2>/dev/null)
echo "pending:$$" > "$claim"
flock -u 9
echo "[valid-next] $kind lines $first..$last pool=$POOL${prev:+ (previous holder $prev)}"

out=$(bash "$DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$DEPLOY" "$PIN" "$POOL" "$first" "$last" 2>&1 9>&-)
lrc=$?
echo "$out"
job=$(echo "$out" | sed -n 's/.*LAUNCHED job=\([0-9]*\).*/\1/p' | head -1)
flock 9
if [ -n "$job" ]; then
    echo "$job" > "$claim"
    exit 0
fi
if [ -n "$prev" ]; then echo "$prev" > "$claim"; else rm -f "$claim"; fi
exit $((lrc ? lrc : 7))
