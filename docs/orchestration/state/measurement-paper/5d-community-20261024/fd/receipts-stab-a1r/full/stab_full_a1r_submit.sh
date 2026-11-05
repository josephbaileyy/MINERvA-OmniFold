#!/bin/bash
# FD-STAB full run (step two) under ADDENDUM A1 and the Director's correction (FD-STAB-BINDING-1-A1.md, merged at
# ff6ba188538a50af785d56657de01fbe1832d94c, corrected at c6f104ee/#766; code pin M_A1), on a login node, detached,
# into the SAME $OUT as the accepted dry run 60827080, so the gate skips its nine tasks and carries their timings.
# In order, every pscratch read through O_NOATIME:
#   the dry run's records against the committed receipts (fd/receipts-stab-a1r/): log-dry/DONE, log-dry/SHA256SUMS
#   and each product it lists, queue.tsv and dry.tsv by sha256; all nine dry tasks ended; no log-dry/STOP or FAILED;
#   no log-full; the DTN pins record by sha256, PASS, and at most 48 h old (else a fresh pins check comes first);
#   the charges so far from sacct (60826464, TIMEOUT; 60827080, COMPLETED): the cap's remainder must cover 07:15:00;
#   the allocation balance from iris (stop if the 8.0 node-h cap is above half of m3246's remaining CPU balance);
#   a fresh clone at M_A1 into $OUT/deploy-full, clean, the A1 binding's code blobs, the declaration's and addendum's
#   sha256 (the dry run's $OUT/deploy is not touched);
#   the environment pre-check: setup_salloc_env.sh sourced in a subshell, lightgbm, scipy and numpy must import;
#   one sbatch: sbatch_fd_stab.sh full <deploy> <M_A1> <OUT> 7.2500, --time=07:15:00, from the plain login environment.
#   The gate's cap argument is 7.2500, equal to the Slurm limit in node-hours on one node, so the gate stops before
#   Slurm would kill a task (the director's ruling). Full mode takes no sixth argument: the F0b product is read only
#   by the dry run's truth control (sbatch_fd_stab.sh blob 9defbb44, lines 22-31, 51-60);
#   then scontrol's TimeLimit must read 07:15:00, or the job is cancelled at once (scancel) and the connect stops.
# Writes only under $OUT (deploy-full, logs/connect-full.*, the job's own log-full and runs). No set -u. Any stop is
# final. Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
M=cc54d86f7ac66c1346fa69e5894b2d2f000fb09c
OUT=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104
D=$OUT/deploy-full
PRICE=8.0                                                        # the probe's cap, node-h (binding 1 ruling 5)
TLIMIT=07:15:00                                                  # the full run's limit (correction item 2)
GATECAP=7.2500                                                   # the gate's cap, equal to TLIMIT on one node
DONE_SHA=ed98090ecfb32c6977256c57b5266183bcd77acf5dbdd5170d02422c4a61e504
SUMS_SHA=fb379aa50b03cfeb46b2eb178918d57fe73c0a05538d1b7f54358d33f96722a4
QUEUE_SHA=d391858c1f5f2655f9fbc9d38beff29d9a4ae830ea7b3cf9365a2d2f4958bfeb
DRY_SHA=afc36dc309afb494ae33c99d06467c63ce850a79e4a1dbfc7e326c24110f10b4
PINS_SHA=2e0a0b2100ac72a9b733e4cf3b4f2b5f76ff5e43bc94a4c1a8ef91ce451410f9
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
nsha() { dd if="$1" iflag=noatime status=none | sha256sum | cut -d' ' -f1; }
[ -s "$OUT/log-dry/DONE" ] && [ -s "$OUT/queue.tsv" ] && [ -s "$OUT/pins/pins-check.json" ] || bail
for x in log-full deploy-full logs/connect-full.log logs/connect-full.done log-dry/STOP log-dry/FAILED; do [ ! -e "$OUT/$x" ] || bail; done
[ -z "$(squeue --me -h -n fd_stab_dry,fd_stab_full -o %i)" ] || bail            # no probe job queued or running
LOG=$OUT/logs/connect-full.log
exec > "$LOG" 2>&1
finish() { echo "stab full submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-full.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/stab_full_a1r_submit.sh"

# ---- the dry run's records, against the committed receipts
bad=0
for pair in "log-dry/DONE $DONE_SHA" "log-dry/SHA256SUMS $SUMS_SHA" "queue.tsv $QUEUE_SHA" "dry.tsv $DRY_SHA" "pins/pins-check.json $PINS_SHA"; do
  set -- $pair; got=$(nsha "$OUT/$1"); echo "$1 sha256 $got $([ "$got" = "$2" ] && echo '== receipt' || echo "!= receipt $2")"
  [ "$got" = "$2" ] || bad=$((bad + 1))
done
np=0
while read -r h p; do
  np=$((np + 1)); got=$(nsha "$OUT/$p"); [ "$got" = "$h" ] || { echo "PRODUCT MISMATCH $p"; bad=$((bad + 1)); }
done < <(dd if="$OUT/log-dry/SHA256SUMS" iflag=noatime status=none)
echo "dry products: $np listed, checked by sha256"
[ "$np" -eq 9 ] || bad=$((bad + 1))
nd=0; for id in $(dd if="$OUT/dry.tsv" iflag=noatime status=none | grep -v '^#' | cut -f1); do
  [ -e "$OUT/log-dry/$id.end" ] && [ -e "$OUT/log-dry/$id.start" ] && nd=$((nd + 1)) || { echo "dry task $id has no start/end"; bad=$((bad + 1)); }
done
echo "dry tasks ended: $nd of 9"; [ "$nd" -eq 9 ] || bad=$((bad + 1))
[ "$bad" -eq 0 ] || { echo "STOP: the dry run's records are not the committed ones ($bad problems)"; finish 4; }
dd if="$OUT/pins/pins-check.json" iflag=noatime status=none | env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -c "
import json, sys, time
r = json.load(sys.stdin)
age_h = (time.time() - float(r.get('written_epoch', 0))) / 3600
checks = {'verdict PASS': r.get('verdict') == 'PASS', 'at M_A1': r.get('M') == '$M', 'schema': r.get('schema') == 'fd-stab-pins-check/2',
          'at most 48 h old': 0 <= age_h <= 48}
print('pins record:', checks, 'written', r.get('written_utc'), 'age_h %.1f' % age_h)
sys.exit(0 if all(checks.values()) else 1)" || { echo "STOP: the pins record does not pass or is over 48 h old (a fresh pins check comes first)"; finish 4; }

# ---- the charges so far, and the cap's remainder (corrections 2 and 4)
c1=$(sacct -j 60826464 -X -n -P -o State,ElapsedRaw,NNodes | head -1); c2=$(sacct -j 60827080 -X -n -P -o State,ElapsedRaw,NNodes | head -1)
echo "invalid 60826464: $c1; dry 60827080: $c2"
case "$c1" in TIMEOUT\|*) ;; *) echo "STOP: 60826464 is not TIMEOUT"; finish 9 ;; esac
case "$c2" in COMPLETED\|*) ;; *) echo "STOP: 60827080 is not COMPLETED"; finish 9 ;; esac
REM=$(printf '%s\n%s\n' "$c1" "$c2" | awk -F'|' -v p=$PRICE '{c += $2 * $3 / 3600} END {printf "%.4f", p - c}')
echo "charged_node_h=$(awk -v p=$PRICE -v r=$REM 'BEGIN{printf "%.4f", p - r}') remainder_node_h=$REM gate_cap=$GATECAP time_limit=$TLIMIT"
awk -v r=$REM -v g=$GATECAP 'BEGIN{exit !(g <= r)}' || { echo "STOP: the remainder $REM is below the gate cap $GATECAP"; finish 9; }

# ---- the balance (coverage-5b's method): iris's m3246 row, Allocated - Charged
echo "== iris"; timeout 120 iris < /dev/null 2>&1 | head -2; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price $PRICE is above half the balance $bal: to Joseph"; finish 9; }

# ---- the deploy: a fresh clone at M_A1, clean, the binding's blobs
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-full.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
S=docs/orchestration/state/measurement-paper/5d-community-20261024
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
9defbb44e99d0dcc538b7254ab998ba13feb354a nd-unfolding/sbatch_fd_stab.sh
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
22e211a20514f9a3c10145085f813c9f5f63f6f2 nd-unfolding/tests/test_estimator_stability_probe.py
9ab35c9839fc38322c47fedf95b774ea25d8942f nd-unfolding/tests/estimator_stability_mutation.py
27947e1add4dd5fbda17a17020976fd30bea1061 $S/fd/stab/no-ratio.json
dc2ac4e4f3098ce59a81fc043526d87b5c49ec77 $S/s1/PRESERVE-INVENTORY.sha256
BLOBS
decl=$(sha256sum "$D/$S/FD-STAB-DECLARATION.md" | cut -d' ' -f1)
add=$(sha256sum "$D/$S/FD-STAB-ADDENDUM-A1.md" | cut -d' ' -f1)
echo "binding blobs: 7 checked, $bad mismatches; declaration sha256 $decl; addendum A1 sha256 $add"
[ "$bad" -eq 0 ] && [ "$decl" = 6c91c0ccbb8061c0dfe755f2283ecbf0f12ba001737876df09f8882eca4ca2b4 ] \
  && [ "$add" = 277f6c799aca808315ce519f427007b7dec5da0c514dc5d0c229841ec01e23b2 ] || { echo "STOP: bound bytes"; finish 9; }

# ---- the environment the job will source: lightgbm, scipy and numpy must import (the job checks again)
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck-full.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck-full.log)"; finish 7; }

# ---- the submission, from the plain login environment
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=fd_stab_full --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_fd_stab.sh" full "$D" "$M" "$OUT" "$GATECAP" > "$OUT/logs/submit-full.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-full.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-full.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "full run job $job"; echo "$job" > "$OUT/logs/full.jobid"
# ---- the limit Slurm actually parsed (correction item 3): anything but 07:15:00 is cancelled at once
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
