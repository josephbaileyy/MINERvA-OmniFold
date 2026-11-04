#!/bin/bash
# RPD job A's submission (FD-RPD-BINDING-2.md and its addendum A1; FD-RPD-DECLARATION-PART2.md section 2), on a login
# node, detached. The director's go of 2026-11-04: one node, regular QOS, 1:00:00, inside the campaign's 3.0 node-h cap.
# In order: the allocation balance from iris (stop if 3.0 node-h is above half of m3246's remaining CPU balance); a fresh
# clone at M' into $R/deploy-5 and its 23 section 7 blobs; verify-staged; then submit_fd_ct.sh rpd-a, whose own refusals
# (deploy at M', the step and lane tables, every path under $R, fd_rpd.py gate a: F1's PASS and the stage 0 and stage D
# records made by this fd_rpd.py) all come before its sbatch. The deploy stays: job A runs from it. Writes only under
# $R; probe reads through O_NOATIME (dd iflag=noatime). No set -u (it aborts the root_6_28 activation). Any stop is
# final. Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
M=8727c63e1d32599039ea977d833c5de25a9089d6
D=$R/deploy-5
LOG=$R/logs/jobA-submit.log
PRICE=3.0                                                        # the campaign's cap, node-h (binding 2)
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
[ -e "$R/staged/STAGED.json" ] && [ -d "$R/tmp" ] && [ -d "$R/receipts" ] && [ ! -e "$D" ] && [ ! -e "$LOG" ] || bail
[ "$(dd if="$R/logs/stageD.done" iflag=noatime status=none)" = 0 ] || bail     # stage D wrote its record
[ -e "$R/control/stage0.json" ] && [ -e "$R/control/stageD.json" ] && [ -e "$R/flux/F1.json" ] || bail
for d in dumps truth inputs n0 unf-k2 lanes-a; do [ ! -e "$R/$d" ] || bail; done
[ -z "$(squeue --me -h -n fd_rpd_a -o %i)" ] || bail                           # no job A already queued
exec > "$LOG" 2>&1
finish() { echo "job A submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/logs/jobA-submit.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/receipts/rpd_jobA_connect.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"

# ---- the balance: stop if the price is above half of m3246's remaining CPU node-h
# coverage-5b's method (connect-calibrate.sh at 2c882d27): iris's m3246 row, Allocated - Charged (project); each iris
# call is bounded at 120 s here, since one hung for over 10 minutes on 2026-11-04 (an iris that times out is a STOP)
echo "== iris"; timeout 120 iris < /dev/null 2>&1 | head -2; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price $PRICE is above half the balance $bal: to Joseph"; finish 9; }

# ---- the deploy: a fresh clone at M', clean, every section 7 blob at M' and in the tree
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone-5.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M'"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
DECL=docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION-PART2.md
rows=0; bad=0
while read -r p b; do
  rows=$((rows + 1))
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done < <(sed -n '/^## 7\./,/^## 8\./p' "$D/$DECL" | sed -n 's/^| `\([^`]*\)` | `\([0-9a-f]\{40\}\)` |$/\1 \2/p')
echo "section 7: $rows blobs, $bad mismatches"
[ "$rows" -eq 23 ] && [ "$bad" -eq 0 ] || { echo "STOP: section 7 blobs"; finish 9; }

# ---- root_6_28 by prefix, one thread per library, niced: verify-staged
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; finish 2; }
export TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PY=(nice -n 19 env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -B)
cd "$R" || finish 9
"${PY[@]}" "$D/nd-unfolding/fd_rpd_inputs.py" verify-staged --r "$R" --deploy "$D" > "$R/logs/verify-staged-5.out" 2>&1
rc=$?; echo "verify-staged rc=$rc"; tail -2 "$R/logs/verify-staged-5.out"
[ $rc = 0 ] || { echo "STOP at verify-staged (final)"; finish $rc; }

# ---- the submission: submit_fd_ct.sh's refusals, its gate, then one sbatch
date -u +%FT%TZ
bash "$D/nd-unfolding/submit_fd_ct.sh" rpd-a "$D" "$M" "$R" > "$R/logs/submit-a.out" 2>&1
rc=$?
echo "submit_fd_ct.sh rpd-a rc=$rc"; cat "$R/logs/submit-a.out"; tail -3 "$R/control/gate-rpd-a.out" 2>/dev/null
[ $rc = 0 ] || { echo "STOP at submit (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$R/logs/submit-a.out")
[ -n "$job" ] || { echo "STOP: no job id in submit-a.out"; finish 9; }
echo "job A $job"; echo "$job" > "$R/logs/jobA.jobid"
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a" ; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
