#!/bin/bash
# RS1 dry run, connect 1: the submission (RS1-BINDING-2.md rulings 1, 2 and 4; RS1-BINDING-1.md; RS1-DECLARATION.md
# §7). Runs on a login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   the COV2D fence: josephrb's squeue is saved and every cov2d-* job is listed. It is recorded, not a stop: RS1 reads the
#     5D bank and the s5p background dump, not a COV2D input (declaration §7). A failed squeue is a stop;
#   iris: stop if the 8.0 node-h cap is above half of m3246's remaining balance;
#   a stat of both inputs (of_inputs_5d.npz, bkg_dump.npz) and of FD-STAB's 21 G1 references (the control base and
#     jitters 1-20); a missing file is a stop;
#   a fresh clone at M into $OUT/deploy: clean, the five code blobs, FD-STAB's pinned SHA256SUMS, the declaration's and
#     binding 1's sha256;
#   the 21 G1 references copied into $OUT/refs with dd iflag=noatime. Each original's atime must not move, and each copy
#     must match its line in FD-STAB's SHA256SUMS;
#   the environment pre-check (0 node-h): setup_salloc_env.sh in a subshell; lightgbm, scipy and numpy must import;
#   the probe's own `tasks` writes queue.tsv (66 tasks, 229 unfolds) and dry.tsv (9). Both must equal the sha256 the
#     director was sent, which were built from the same paths at M;
#   one sbatch: sbatch_rs1.sh dry, --time=00:45:00, from the plain login environment. scontrol's TimeLimit must read
#     00:45:00, or the job is cancelled at once and the connect stops.
# The deploy stays: the job runs from it. Writes only under $OUT (new; refused if it exists). No set -u. Any stop is
# final.
SELF=$1
M=e306087e68fd497541d32b440848a40f7f29611e
OUT=/pscratch/sd/j/josephrb/rs1-20261106
D=$OUT/deploy
PRICE=8.0                                                        # RS1-BINDING-1 ruling 2: dry + full together
TLIMIT=00:45:00                                                  # RS1-BINDING-2 ruling 2
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
NPZ_SHA=07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
BKG_SHA=2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955
REFSRC=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/runs/control/stability
S=docs/orchestration/state/measurement-paper/5d-community-20261024
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
QUEUE_SHA=58c213a24da0366ef27194ecea9fb247c6698819c5eb374f538e85e0df2fd22b
DRY_SHA=5579ea8c2b228b13df33b77d71018a14a347c26e2b6d25b5e17ce7ace2b5e8d6
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$OUT" ] || bail
[ -z "$(squeue --me -h -n rs1_dry,rs1_full -o %i)" ] || bail
mkdir "$OUT" && mkdir "$OUT/logs" "$OUT/refs" || bail
LOG=$OUT/logs/connect-dry.log
exec > "$LOG" 2>&1
finish() { echo "rs1 dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-dry.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/rs1_dry_submit.sh"

# ---- the COV2D fence, recorded
echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$OUT/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$OUT/logs/squeue-before.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded; RS1 reads no COV2D input):"; printf '%s\n' "$hits"
else echo "FENCE: no cov2d-* job queued or running"; fi
echo "squeue lines: $(wc -l < "$OUT/logs/squeue-before.txt")"

# ---- the balance: iris's m3246 row, Allocated - Charged
echo "== iris"; timeout 120 iris < /dev/null > "$OUT/logs/iris.txt" 2>&1; head -2 "$OUT/logs/iris.txt"
row=$(grep -E '^m3246 ' "$OUT/logs/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b="$bal" -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price $PRICE is above half the balance $bal"; finish 9; }

# ---- stat: the inputs and the G1 references (retention, declaration §7)
echo "== stat"
REFS="stab_control_b-_j-.npz"; for s in $(seq 1 20); do REFS="$REFS stab_control_b-_j$s.npz"; done
miss=0
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || miss=$((miss + 1)); done
for r in $REFS; do stat -c '%n size=%s mtime=%y atime=%x' "$REFSRC/$r" || miss=$((miss + 1)); done
echo "stat: 23 files, $miss missing"
[ "$miss" -eq 0 ] || { echo "STOP: an input or G1 reference is missing"; finish 9; }

# ---- the deploy: a fresh clone at M, clean, the bound blobs
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
d58c241eff687a96bda94812d145a90d9f4790ed nd-unfolding/rounding_mechanism_analyze.py
9ad7dece80ba4ca7a6a0548c02c07bae4c947d2b nd-unfolding/sbatch_rs1.sh
8c35d8ca69913e901918945483fd40b9ad100999 nd-unfolding/tests/test_rounding_mechanism.py
ac69daf63d14af940650966a3b4e8ba1009db7db nd-unfolding/tests/rounding_mechanism_mutation.py
bdc79a29ad90e110413898f42c81178410f7269c $SUMS
BLOBS
decl=$(sha256sum "$D/$S/fd/rounding-stability-20261106/RS1-DECLARATION.md" | cut -d' ' -f1)
b1=$(sha256sum "$D/$S/fd/rounding-stability-20261106/RS1-BINDING-1.md" | cut -d' ' -f1)
sums=$(sha256sum "$D/$SUMS" | cut -d' ' -f1)
echo "bound blobs: 6 checked, $bad mismatches; declaration sha256 $decl; binding 1 sha256 $b1; FD-STAB SHA256SUMS $sums"
[ "$bad" -eq 0 ] && [ "$decl" = dbfb0c941b2ad6999b2edb3b8bf77ca735b2f01f86ca593425e44c2ad5c91e76 ] \
  && [ "$b1" = 947fd2750343ead7aff5281af8bfb03a137f76346071a84233b62ebf12744255 ] \
  && [ "$sums" = e2c35e55402b809f522c86f597df20b058fc0c49596b9595448c4a944be333ee ] || { echo "STOP: bound bytes"; finish 9; }

# ---- the G1 references: dd iflag=noatime copies; the original's atime must not move; each copy at its pin
echo "== G1 references"
bad=0
for r in $REFS; do
  a0=$(stat -c %X "$REFSRC/$r")
  dd if="$REFSRC/$r" iflag=noatime of="$OUT/refs/$r" bs=4M status=none || { echo "COPY FAILED $r"; bad=$((bad + 1)); continue; }
  a1=$(stat -c %X "$REFSRC/$r")
  want=$(awk -v n="runs/control/stability/$r" '$2 == n {print $1}' "$D/$SUMS")
  got=$(sha256sum "$OUT/refs/$r" | cut -d' ' -f1)
  [ "$a0" = "$a1" ] || { echo "ATIME MOVED $r ($a0 -> $a1)"; bad=$((bad + 1)); }
  [ -n "$want" ] && [ "$got" = "$want" ] || { echo "NOT PINNED $r ($got vs '$want')"; bad=$((bad + 1)); }
done
echo "G1 references: 21 copied, $bad problems"
( cd "$OUT/refs" && sha256sum $REFS ) > "$OUT/logs/refs-SHA256SUMS"
[ "$bad" -eq 0 ] || { echo "STOP: a G1 reference"; finish 9; }

# ---- the environment the job will source: lightgbm, scipy and numpy must import (the job checks again)
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

# ---- the queue, from the probe's own tasks command, at the sha256 the director was sent
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-tasks.log" 2>&1
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/rounding_mechanism_probe.py tasks \
    --out "$OUT/queue.tsv" --dry-out "$OUT/dry.tsv" --npz "$NPZ" --bkg "$BKG" \
    --expect-npz-sha256 "$NPZ_SHA" --expect-bkg-sha256 "$BKG_SHA" --runs "$OUT/runs" ) || { echo "STOP: tasks"; finish 5; }
nq=$(grep -vc '^#' "$OUT/queue.tsv"); nd=$(grep -vc '^#' "$OUT/dry.tsv")
echo "queue: $nq tasks; dry: $nd tasks: $(grep -v '^#' "$OUT/dry.tsv" | cut -f1 | tr '\n' ' ')"
qs=$(sha256sum "$OUT/queue.tsv" | cut -d' ' -f1); ds=$(sha256sum "$OUT/dry.tsv" | cut -d' ' -f1)
echo "queue.tsv sha256 $qs (expected $QUEUE_SHA); dry.tsv sha256 $ds (expected $DRY_SHA)"
[ "$nq" -eq 66 ] && [ "$nd" -eq 9 ] && [ "$qs" = "$QUEUE_SHA" ] && [ "$ds" = "$DRY_SHA" ] \
  || { echo "STOP: the queue is not the one sent"; finish 5; }

# ---- the submission, from the plain login environment
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=rs1_dry --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_rs1.sh" dry "$D" "$M" "$OUT" > "$OUT/logs/submit-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry run job $job"; echo "$job" > "$OUT/logs/dry.jobid"
# ---- the limit Slurm actually parsed: anything but 00:45:00 is cancelled at once
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
