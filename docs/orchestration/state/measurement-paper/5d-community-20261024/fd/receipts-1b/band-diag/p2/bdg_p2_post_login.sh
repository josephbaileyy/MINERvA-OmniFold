#!/bin/bash
# Band diagnosis, P2 post (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 4.3, 5 and 7; BINDING-1 rulings 2 and 5). Login
# node, nice 19, 0 node-h, after job fd1b_bdg_p2 has ended. Every step stamped to the second. In order:
#   1. the job: its id from $W/p2/logs/submit-p2.out; squeue must no longer list it; sacct's record (state, exit code,
#      start, end, elapsed, node-h);
#   2. the deploy is still M clean, and the module still 658ca918;
#   3. section 4.3: $W/p2/inputs.json printed (verdict EQUAL or DIFFER; DIFFER is a STOP);
#   4. section 7's pilot reading: `fd_1b_band_diag.py pilot` on $W/unf, $V/stage and $V/unf, writing
#      $W/p2/pilot.json (the E and B rebuild controls bitwise, the walls, the verdict PASS, REPRICE or INVALID; rc 0, 1
#      or 2; a refusal is rc 4). It reads only through O_NOATIME;
#   5. section 5: the 73 sources re-stat'd into $W/p2/logs/stat-post.txt and compared byte for byte with P1's
#      stat-before.txt (7986e2bf); any difference, a moved atime included, is printed and is a STOP (rc 4);
#   6. every product in $W/unf listed with size and sha256 (the npz bytes are not sent);
#   7. a base64 tar of the records: the tables, the logs (the job's output, the submit record, the stats), the lanes
#      (thread probe, inputs and line logs, inventories), inputs.json, pilot.json and the module's atime records.
# Nothing is deleted or written under $V. The clone is not re-made: the deploy at $W/deploy is the job's. Launched from
# a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
ts() { date -u +%FT%TZ; }
finish() { echo "== bdg-p2-post rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/p2/pilot.json" ] || { echo "STOP: $W/p2/pilot.json already exists"; finish 9; }
echo "== 1. the job $(ts)"
job=$(awk '/^Submitted batch job/ {print $4}' "$W/p2/logs/submit-p2.out")
echo "job id [$job]"; [ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
if squeue -h -j "$job" 2>/dev/null | grep -q .; then echo "STOP: job $job is still queued or running"; finish 9; fi
sacct -j "$job" -X -n -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,ElapsedRaw,NNodes,NodeList,TimelimitRaw
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS,TotalCPU
echo "== 2. the deploy"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
mod=$(sha256sum "$W/deploy/nd-unfolding/fd_1b_band_diag.py" | cut -d' ' -f1)
echo "deploy HEAD $head; tracked porcelain $porc; module $mod"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] && [ "$mod" = "$MOD_SHA" ] || { echo "STOP: the deploy is not M clean"; finish 5; }
echo "== 3. section 4.3: inputs.json $(ts)"
if [ -s "$W/p2/inputs.json" ]; then
  echo "inputs.json sha256 $(sha256sum "$W/p2/inputs.json" | cut -d' ' -f1)"
  env -u PYTHONPATH "$PY" -B -c 'import json,sys; d=json.load(open(sys.argv[1])); print("inputs verdict:", d.get("verdict"), "| atime:", json.dumps(d.get("atime"))[:300])' "$W/p2/inputs.json"
else
  echo "inputs.json absent"
fi
echo "== 4. section 7's pilot reading $(ts)"
cd "$W/deploy/nd-unfolding" || finish 5
export PYTHONDONTWRITEBYTECODE=1
nice -n 19 env -u PYTHONPATH "$PY" -B fd_1b_band_diag.py pilot --unfolds "$W/unf" --staged "$V/stage" --part1-unfolds "$V/unf" --out "$W/p2/pilot.json"
p=$?
echo "pilot rc=$p $(ts)"
echo "== 5. section 5: the 73 sources against P1's stat-before.txt (stat only) $(ts)"
env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
  | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$W/p2/logs/stat-post.txt"
echo "stat-post.txt: $(wc -l < "$W/p2/logs/stat-post.txt") lines; sha256 $(sha256sum "$W/p2/logs/stat-post.txt" | cut -d' ' -f1)"
moved=0
if cmp -s "$W/stat-before.txt" "$W/p2/logs/stat-post.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved:"; diff "$W/stat-before.txt" "$W/p2/logs/stat-post.txt" | head -40; moved=1; fi
echo "== 6. products in $W/unf"
find "$W/unf" -maxdepth 1 -type f -name '*.npz' -printf '%s %f\n' | sort -k2 | while read -r s f; do echo "$s $(sha256sum "$W/unf/$f" | cut -d' ' -f1) $f"; done
echo "products: $(find "$W/unf" -maxdepth 1 -type f -name '*.npz' | wc -l)"
echo "== 7. records $(ts)"
cd "$W" || finish 9
list=$(find p2/tables p2/logs p2/lanes -type f | sort; [ -f p2/inputs.json ] && echo p2/inputs.json; [ -f p2/pilot.json ] && echo p2/pilot.json; find unf -maxdepth 1 -type f -name 'atime-*.json' | sort)
printf '%s\n' "$list" | while read -r f; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
printf '%s\n' "$list" | tar -cf - -T - | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[1]}"
[ -f p2/pilot.json ] && { echo "== pilot.json"; cat p2/pilot.json; }
[ "$moved" -eq 0 ] || finish 4
finish "$p"
