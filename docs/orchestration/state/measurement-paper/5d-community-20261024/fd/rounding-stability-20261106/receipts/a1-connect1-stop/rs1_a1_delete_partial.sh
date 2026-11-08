#!/bin/bash
# Delete the partial RS1 A1 root that connect 1 (stop rc 6, 2026-11-07T22:47:39Z) left: no products, no staging (the
# director's ruling, item 4). Literal paths only. It refuses unless the root holds exactly the five entries the stop left
# and no runs/, log-dry/, plan.tsv or log-full/; lists every file with its size and sha256 first; deletes; then checks
# each path is gone. Prints to stdout (the receipt). Attempt 1's root /pscratch/sd/j/josephrb/rs1-20261106 is not touched.
# Run from the Mac: ssh -o ControlPath=none saul.nersc.gov bash -s < rs1_a1_delete_partial.sh
date -u +%FT%TZ; hostname
R=/pscratch/sd/j/josephrb/rs1-a1-20261107
[ -d "$R" ] || { echo "REFUSE: $R absent"; exit 2; }
[ -z "$(squeue --me -h -n rs1_dry,rs1_full,rs1_a1 -o %i)" ] || { echo "REFUSE: an rs1 job is queued"; exit 2; }
top=$(cd "$R" && ls -A | sort | tr '\n' ' ')
echo "top-level entries: $top"
[ "$top" = "a1 deploy dry.tsv logs queue.tsv " ] || { echo "REFUSE: the root is not what the stop left"; exit 2; }
for x in runs log-dry plan.tsv log-full copies.sha256 stage.json runs-attempt1; do
  [ ! -e "$R/$x" ] || { echo "REFUSE: $R/$x exists"; exit 2; }
done
[ "$(cat "$R/logs/connect-a1.done")" = 6 ] || { echo "REFUSE: connect-a1.done is not 6"; exit 2; }
echo "== listing (files: $(find "$R" -type f | wc -l), bytes: $(du -sb "$R" | cut -f1))"
( cd "$R" && find queue.tsv dry.tsv logs -type f -print0 | sort -z | xargs -0 sha256sum )
for d in deploy a1; do
  echo "$d: HEAD $(git -C "$R/$d" rev-parse HEAD), files $(find "$R/$d" -type f | wc -l), porcelain --ignored $(git -C "$R/$d" status --porcelain --ignored | wc -l)"
done
echo "== delete"
rm -rf -- /pscratch/sd/j/josephrb/rs1-a1-20261107/deploy
rm -rf -- /pscratch/sd/j/josephrb/rs1-a1-20261107/a1
rm -f -- /pscratch/sd/j/josephrb/rs1-a1-20261107/queue.tsv
rm -f -- /pscratch/sd/j/josephrb/rs1-a1-20261107/dry.tsv
rm -rf -- /pscratch/sd/j/josephrb/rs1-a1-20261107/logs
rmdir -- /pscratch/sd/j/josephrb/rs1-a1-20261107
echo "== gone?"
gone=0
for p in /pscratch/sd/j/josephrb/rs1-a1-20261107/deploy /pscratch/sd/j/josephrb/rs1-a1-20261107/a1 \
         /pscratch/sd/j/josephrb/rs1-a1-20261107/queue.tsv /pscratch/sd/j/josephrb/rs1-a1-20261107/dry.tsv \
         /pscratch/sd/j/josephrb/rs1-a1-20261107/logs /pscratch/sd/j/josephrb/rs1-a1-20261107; do
  if [ -e "$p" ]; then echo "STILL THERE: $p"; else echo "gone: $p"; gone=$((gone + 1)); fi
done
echo "attempt 1 root still present: $([ -d /pscratch/sd/j/josephrb/rs1-20261106/runs ] && echo yes || echo NO)"
date -u +%FT%TZ
[ "$gone" -eq 6 ] && { echo "DELETE: PASS"; exit 0; } || { echo "DELETE: INCOMPLETE"; exit 1; }
