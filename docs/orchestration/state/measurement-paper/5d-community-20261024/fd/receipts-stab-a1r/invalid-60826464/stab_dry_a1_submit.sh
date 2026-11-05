#!/bin/bash
# FD-STAB dry run under ADDENDUM A1, step 2 of 2: the submission (FD-STAB-BINDING-1-A1.md rulings 1-4, under
# FD-STAB-BINDING-1.md rulings 2 and 3; FD-STAB-DECLARATION.md sections 7 and 11), on a login node, detached. The A1
# binding is merged at ff6ba188538a50af785d56657de01fbe1832d94c; the code pin stays M_A1. In order:
#   the DTN pins record $OUT/pins/pins-check.json (step 1, stab_pins_a1_dtn.sh): its sha256 must equal $2, the sha the
#   director was sent; schema fd-stab-pins-check/2, verdict PASS, made at M_A1, 734 pinned directory files, the npz,
#   bkg, closure ratio (truth kind pvl_ratio) and F0b closure product at their pins, written after RPD job B's End;
#   the allocation balance from iris (stop if the 8.0 node-h cap is above half of m3246's remaining CPU balance);
#   a fresh clone at M_A1 into $OUT/deploy, clean, the A1 binding's code blobs, the declaration's and addendum's sha256;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell, lightgbm, scipy, numpy import;
#   estimator_stability_probe.py tasks writes queue.tsv (128 tasks) and dry.tsv (the 9 DRY_TASKS, closure_nuwro among
#   them);
#   one sbatch: sbatch_fd_stab.sh dry with the F0b closure product as its sixth argument (the job runs the truth
#   control C1/C2 before any task and STOPs on a fail), --time=0:45, from the plain login environment (the job is
#   --export=ALL, so none of the login steps' thread caps or conda activation reaches it).
# Step one's /pscratch/sd/j/josephrb/fd-stab-20261104 (its pins STOP record and deploy) is not read or touched.
# The deploy stays: the job runs from it. Writes only under $OUT. No set -u. Any stop is final. Launched from a
# /dev/shm copy of itself (its path is $1, the record's sha256 $2), which it deletes at exit.
SELF=$1
PINS_SHA=$2
M=cc54d86f7ac66c1346fa69e5894b2d2f000fb09c
OUT=/pscratch/sd/j/josephrb/fd-stab-a1-20261104
D=$OUT/deploy
RPD=/pscratch/sd/j/josephrb/fd-rpd-20261103
PRICE=8.0                                                        # the probe's cap, node-h (binding 1 ruling 5)
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
PVL=/pscratch/sd/j/josephrb/pv-ladder-20261024
F0B=$PVL/products/L-5D-PV_e_closure_nuwro.npz                  # fd_f0_regrade.PINS["closure"], checked by step 1
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
PINS=$OUT/pins/pins-check.json
case "$PINS_SHA" in [0-9a-f]*) [ ${#PINS_SHA} = 64 ] || bail ;; *) bail ;; esac
[ -e "$PINS" ] && [ "$(dd if="$OUT/pins/check.done" iflag=noatime status=none)" = 0 ] || bail
for x in deploy logs queue.tsv dry.tsv runs log-dry; do [ ! -e "$OUT/$x" ] || bail; done
[ -z "$(squeue --me -h -n fd_stab_dry,fd_stab_full,fd_rpd_b -o %i)" ] || bail   # no probe job, RPD job B gone
jb=$(dd if="$RPD/logs/jobB.jobid" iflag=noatime status=none)
case "$(sacct -j "$jb" -X -n -P -o State | head -1)" in PENDING|RUNNING|REQUEUED|"") bail ;; esac
[ -e "$RPD/logs/mwdiag.done" ] || bail                                          # RPD's diagnostic ran
mkdir "$OUT/logs" || bail
LOG=$OUT/logs/connect-dry.log
exec > "$LOG" 2>&1
finish() { echo "stab dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-dry.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/stab_dry_a1_submit.sh"
echo "RPD job B $jb: $(sacct -j "$jb" -X -n -P -o JobID,State,ExitCode,Elapsed,End | head -1)"
# ---- the DTN pins record: this sha, PASS, at M, 734 files, written after job B ended
got=$(dd if="$PINS" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "pins record sha256 $got (expected $PINS_SHA)"
[ "$got" = "$PINS_SHA" ] || { echo "STOP: the pins record is not the one sent"; finish 4; }
endB=$(date -d "$(sacct -j "$jb" -X -n -P -o End | head -1)" +%s) || { echo "STOP: job B End unreadable"; finish 4; }
dd if="$PINS" iflag=noatime status=none | env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -c "
import json, sys
r = json.load(sys.stdin)
checks = {'schema': r.get('schema') == 'fd-stab-pins-check/2' and r.get('addendum') == 'A1', 'verdict PASS': r.get('verdict') == 'PASS',
          'at M_A1': r.get('M') == '$M',
          '734 files': r.get('pinned_dir_files') == 734 and r['bank']['ok'] and r['detector']['ok'],
          'npz bkg ratio product': all(r['files'][k]['ok'] for k in ('npz', 'bkg', 'closure_ratio', 'f0b_product')),
          'ratio kind pvl_ratio': r['files']['closure_ratio'].get('truth_kind') == 'pvl_ratio',
          'product path': r['files']['f0b_product'].get('path') == '$F0B',
          'written after job B ended': float(r.get('written_epoch', 0)) > $endB}
print('pins record:', checks, 'host', r.get('host'), 'written', r.get('written_utc'))
sys.exit(0 if all(checks.values()) else 1)" || { echo "STOP: the pins record does not pass"; finish 4; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"

# ---- the balance (coverage-5b's method, as in RPD): iris's m3246 row, Allocated - Charged
echo "== iris"; timeout 120 iris < /dev/null 2>&1 | head -2; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price $PRICE is above half the balance $bal: to Joseph"; finish 9; }

# ---- the deploy: a fresh clone at M, clean, the binding's blobs
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
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
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

# ---- the queue, from the probe's own tasks command
( eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" && cd "$D" && \
  nice -n 19 env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 python3 -I -B nd-unfolding/estimator_stability_probe.py tasks \
    --out "$OUT/queue.tsv" --dry-out "$OUT/dry.tsv" --npz "$NPZ" --bkg "$BKG" --bank "$BANK" --detector-dir "$DET" \
    --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 \
    --closure-ratio-dir "$PVL" --runs "$OUT/runs" ) || { echo "STOP: tasks"; finish 5; }
nq=$(grep -vc '^#' "$OUT/queue.tsv"); nd=$(grep -vc '^#' "$OUT/dry.tsv")
echo "queue: $nq tasks; dry: $nd tasks: $(grep -v '^#' "$OUT/dry.tsv" | cut -f1 | tr '\n' ' ')"
[ "$nq" -eq 128 ] && [ "$nd" -eq 9 ] || { echo "STOP: the queue is not 128 tasks with 9 dry ones"; finish 5; }
grep -q '^stab_control_closure_closure_nuwro	' "$OUT/dry.tsv" || { echo "STOP: closure_nuwro is not a dry task"; finish 5; }
sha256sum "$OUT/queue.tsv" "$OUT/dry.tsv"

# ---- the submission, from the plain login environment
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=0:45 --job-name=fd_stab_dry --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_fd_stab.sh" dry "$D" "$M" "$OUT" 8.0 "$F0B" > "$OUT/logs/submit-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry run job $job"; echo "$job" > "$OUT/logs/dry.jobid"
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
