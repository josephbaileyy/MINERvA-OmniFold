#!/bin/bash
# Band diagnosis, P3 post (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 5 and 7). Login node, 0 node-h, after the four
# fd1b_bdg_p3 jobs have left the queue; every step stamped to the second. In order:
#   1. the jobs, from $W/p3/logs/jobs.txt: none may still be listed by squeue; sacct's record for each;
#   2. the deploy still M with no tracked change, and the module still 658ca918;
#   3. section 5's final comparison: the 73 sources re-stat'd into $W/p3/logs/stat-after-p3.txt and compared byte for
#      byte with P1's stat-before.txt (7986e2bf); any difference, a moved atime included, is printed and is a STOP (rc 4);
#   4. every product in $W/unf listed with size and sha256; 126 are expected (14 pilot + 112 bulk); the count is printed;
#   5. a base64 tar of the records: the table, the logs, the lanes (thread probes, line logs, inventories) and the
#      module's atime records. The npz bytes are not sent.
# Nothing is deleted or written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
ts() { date -u +%FT%TZ; }
restat() {  # $1 = output file: the 73 sources of P1's stat-before.txt, stat only
  env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
    | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$1"
}
finish() { echo "== bdg-p3-post rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
echo "== 1. the jobs $(ts)"
[ -s "$W/p3/logs/jobs.txt" ] || { echo "STOP: no jobs.txt"; finish 9; }
while read -r job; do
  if squeue -h -j "$job" 2>/dev/null | grep -q .; then echo "STOP: job $job is still queued or running"; finish 9; fi
  sacct -j "$job" -X -n -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,ElapsedRaw,NNodes,NodeList,TimelimitRaw
  sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
done < "$W/p3/logs/jobs.txt"
echo "== 2. the deploy"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
mod=$(sha256sum "$W/deploy/nd-unfolding/fd_1b_band_diag.py" | cut -d' ' -f1)
echo "deploy HEAD $head; tracked porcelain $porc; module $mod"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] && [ "$mod" = "$MOD_SHA" ] || { echo "STOP: the deploy is not M clean"; finish 5; }
echo "== 3. section 5's final comparison: the 73 sources against P1's stat-before.txt $(ts)"
restat "$W/p3/logs/stat-after-p3.txt"
echo "stat-after-p3.txt: $(wc -l < "$W/p3/logs/stat-after-p3.txt") lines; sha256 $(sha256sum "$W/p3/logs/stat-after-p3.txt" | cut -d' ' -f1)"
moved=0
if cmp -s "$W/stat-before.txt" "$W/p3/logs/stat-after-p3.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved:"; diff "$W/stat-before.txt" "$W/p3/logs/stat-after-p3.txt" | head -40; moved=1; fi
echo "== 4. products in $W/unf $(ts)"
find "$W/unf" -maxdepth 1 -type f -name '*.npz' -printf '%s %f\n' | sort -k2 | while read -r s f; do echo "$s $(sha256sum "$W/unf/$f" | cut -d' ' -f1) $f"; done
np=$(find "$W/unf" -maxdepth 1 -type f -name '*.npz' | wc -l); echo "products: $np (126 expected)"
echo "== 5. records $(ts)"
cd "$W" || finish 9
list=$(find p3/tables p3/logs p3/lanes -type f | sort; find unf -maxdepth 1 -type f -name 'atime-*.json' | sort)
printf '%s\n' "$list" | while read -r f; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
printf '%s\n' "$list" | tar -cf - -T - | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[1]}"
[ "$moved" -eq 0 ] || finish 4
[ "$np" -eq 126 ] || { echo "STOP: $np products, not 126"; finish 6; }
finish 0
