# 1B staged, stage 1, connect 33 (after connect 32's receipt STOP; binding 2 STOP accepted, director's approval:
# read-only, nothing written on the cluster): no fd1b job, the stat-after over connect 32's 1,513-path list against
# its stat-before (metadata only, no content opened; printed here, so it lands only in this connect's local .out), and
# the digests of this lane's own outputs under $W1. No HPSS (RECORD-20261102-director-hpss-deferral).
P=/pscratch/sd/j/josephrb; W1=$P/fd-1b-staged-20261102/stage1
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "== squeue"; squeue --me -h -o "%i %j %T %l %D %R"
echo "fd1b jobs queued=$(squeue --me -h -o %j | grep -c '^fd1b')"
echo "== sacct fd1b since 2026-11-02T16:00"; sacct -X -n -S 2026-11-02T16:00:00 -o JobID,JobName%30,State 2>&1 | grep fd1b | head
after=$(xargs -a $W1/logs/stage1-sources.txt stat -c '%X %Y %s %n'); rc=$?
echo "stat-after rc=$rc lines=$(printf '%s\n' "$after" | wc -l) stat-before lines=$(wc -l < $W1/logs/stat-before.txt)"
if [ "$(printf '%s\n' "$after")" = "$(cat $W1/logs/stat-before.txt)" ]; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $W1/logs/stat-before.txt))"
else echo "sources CHANGED (a deviation, not restored):"; diff $W1/logs/stat-before.txt <(printf '%s\n' "$after") | head -40; fi
echo "== stat-after (full)"; printf '%s\n' "$after"
echo "== the lane's own outputs"
ls -la $W1 $W1/in $W1/logs $W1/tables $W1/unf $W1/lanes 2>&1
cd $W1 && sha256sum receipt.json in/flux_universes.npz logs/*.txt logs/*.out logs/*.time logs/*.sh logs/env.log
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
