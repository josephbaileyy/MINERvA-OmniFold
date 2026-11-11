#!/bin/bash
# FD-PRR full job prr_cap: the connect, on a Perlmutter login node, detached, after the director's go for this connect
# (FD-PRR BINDING 1 rulings 4, 5 and 7, and addendum A1: every FD-PRR job runs from M_A1 = 6727020a). In order, each
# failure a final stop before anything is submitted:
#   preconditions: $OUT and the dry run's DONE (no STOP) exist; nothing of this mode exists yet (log-cap, its deploy,
#     its connect log, its jobid); no prr_* job queued or running (squeue --me; fails closed). ll5d_*, ens1_* and
#     fd1b_* jobs are listed, not refused: this job reads nothing outside $OUT (every queue path is under $OUT/stage or
#     $OUT/runs; the hypothesis files are in the deploy) and copies nothing;
#   (no login-node sweep: login07, login17 and login19 were closed as unreached on two sweeps, the director's ruling)
#   the balance from iris: the cap 27.0 at most half of m3246's remaining balance; and the study's charge so far
#     (sacct, every ended prr_* job's ElapsedRaw x NNodes; prr_dry 61022062 and prr_iter 61024185 as recorded)
#     plus this job's --time at most the cap 27.0;
#   a fresh clone at M_A1 into $OUT/deploy-cap, clean (porcelain --ignored 0), the six FD-PRR files at their bound
#     sha256 and the declaration, addendum A1 and BINDING 1 (with its addendum A1 and erratum E1) at theirs;
#   the inputs this job starts from, at the digests the dry run recorded: queues/cap.tsv (29 tasks), stage.json and
#     log-dry/DONE;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell; lightgbm, scipy, numpy import;
#   the job's first python calls, after sourcing with root_6_28's python3 (the source's rc checked on its own):
#     `prr_probe.py limit cap` must print the declared 6:30:00, and it is the --time submitted; then the gate's own
#     projection at t0 (prr_probe.project on queues/cap.tsv and the dry records) must have no unmeasured level and be
#     at most 0.9 x 6.5 h;
#   one sbatch, from the plain login environment: --job-name=prr_cap --time=06:30:00 sbatch_prr.sh cap; then
#     scontrol's TimeLimit must read 06:30:00 or the job is cancelled at once.
# The job (sbatch_prr.sh) re-checks the name, the TimeLimit, the dry run's DONE and its 15 ends, re-verifies every staged
# copy, and starts every task only through the gate. Writes only under $OUT. No set -u (it kills setup_salloc_env.sh).
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit. The deploy stays.
SELF=$1
MODE=cap
NQ=29
DECL_LIMIT=6:30:00
M=6727020a7c58b00dd00806151c627c8a24f72402
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
D=$OUT/deploy-$MODE
CAP=27.0
DECL_SHA=5be1e19cb8db67064cb0f90382ed7ac2365a2ed4841d9b498f323ed2761b64ce
A1_SHA=ca6b8457e74c9323fcb985766a88f404038f6f16c3e822a67bf2606af223f38b
BIND_SHA=04686d70ba8a6401669f1f7fa956c0e86785e362cb367bfe5653644184a8ee4d   # FD-PRR-BINDING-1.md at main 82ee901c (erratum E1)
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
[ -d "$OUT" ] && [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] && [ ! -e "$OUT/log-dry/FAILED" ] || bail
for p in "$OUT/log-$MODE" "$D" "$OUT/logs/connect-$MODE.log" "$OUT/logs/connect-$MODE.done" "$OUT/logs/$MODE.jobid"; do
  [ ! -e "$p" ] || bail
done
q=$(squeue --me -h -o '%j') || bail                 # fails closed: no answer from squeue, no connect
[ -z "$(printf '%s\n' "$q" | grep -E '^prr_')" ] || bail
LOG=$OUT/logs/connect-$MODE.log
exec > "$LOG" 2>&1
finish() { echo "prr $MODE submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$MODE.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/prr_${MODE}_submit.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
echo "other lanes' families (listed, not refused; this job reads nothing outside \$OUT):"
printf '%s\n' "$q" | grep -E '^(ll5d_|ens1_|fd1b_)' || echo "  none"

# ---- the balance (coverage-5b's method): iris's m3246 row, Allocated - Charged; and the study's charge against the cap
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap $CAP is above half the balance $bal: to the director"; finish 9; }
echo "== the study's charge so far (sacct, prr_* jobs since 2026-11-08)"
sacct -X -n -P -S 2026-11-08T00:00:00 -o JobID,JobName,State,ElapsedRaw,NNodes --name=prr_dry,prr_iter,prr_cap,prr_misc,prr_ibu \
  > "$OUT/logs/charge-before-$MODE.txt" 2>&1 || { echo "STOP: sacct did not answer"; cat "$OUT/logs/charge-before-$MODE.txt"; finish 9; }
cat "$OUT/logs/charge-before-$MODE.txt"
grep -q '^61022062|prr_dry|COMPLETED|3648|1$' "$OUT/logs/charge-before-$MODE.txt" || { echo "STOP: sacct does not show the dry run 61022062 as recorded"; finish 9; }
grep -q '^61024185|prr_iter|COMPLETED|9038|1$' "$OUT/logs/charge-before-$MODE.txt" || { echo "STOP: sacct does not show prr_iter 61024185 as recorded"; finish 9; }
awk -F'|' '$3 ~ /^(PENDING|RUNNING|REQUEUED)/ {bad=1} END {exit bad}' "$OUT/logs/charge-before-$MODE.txt" \
  || { echo "STOP: a prr_* job is not ended"; finish 9; }
spent=$(awk -F'|' '{s += $4 * $5 / 3600} END {printf "%.4f", s}' "$OUT/logs/charge-before-$MODE.txt")
lim_h=$(echo "$DECL_LIMIT" | awk -F: '{printf "%.4f", $1 + $2/60 + $3/3600}')
echo "charged_node_h=$spent this_job_limit_h=$lim_h sum=$(awk -v a=$spent -v b=$lim_h 'BEGIN{printf "%.4f", a+b}') cap=$CAP"
awk -v a=$spent -v b=$lim_h -v c=$CAP 'BEGIN{exit !(a + b <= c)}' || { echo "STOP: the charge so far plus this --time is above the cap"; finish 9; }

# ---- the deploy: a fresh clone at M_A1, clean, the bound bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-$MODE.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/prior_retention" && sha256sum -c ) <<SUMS || { echo "STOP: the FD-PRR files are not the bound ones"; finish 9; }
f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232  prr_probe.py
17acad82bad7c43f45c423e41039eb81381f5acab15ecdf983ad0d023848d046  prr_ibu.py
f35bc3282b50215dd583b76b0d6a747f90185e4b96b6e3f5b693d42c01166372  prr_read.py
10290087cdd57d972a4df5289f1910161373e8def3f44c15ba0682f9d14a0b85  sbatch_prr.sh
44223143a6982fb876e742fd910c3de46e48fb419da351b9ad9693186f791746  test_prr.py
4666aa0654dccbe999972642090cfc18ccac8d14d7fa4c5057be6e745520ef25  prr_mutation.py
SUMS
S=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
decl=$(sha256sum "$S/FD-PRR-DECLARATION.md" | cut -d' ' -f1); echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }
a1=$(sha256sum "$S/FD-PRR-ADDENDUM-A1.md" | cut -d' ' -f1); echo "addendum A1 sha256 $a1"
[ "$a1" = "$A1_SHA" ] || { echo "STOP: Addendum A1 is not the bound one"; finish 9; }
bmain=$(git -C "$D" show origin/main:docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-BINDING-1.md | sha256sum | cut -d' ' -f1)
echo "FD-PRR-BINDING-1.md at origin/main $(git -C "$D" rev-parse origin/main) sha256 $bmain"
[ "$bmain" = "$BIND_SHA" ] || { echo "STOP: BINDING 1 on main is not the one this connect was made against: to the director"; finish 9; }

# ---- the inputs this job starts from, at the dry run's recorded digests (fd/receipts-prr/dry/cluster/SHA256SUMS)
( cd "$OUT" && sha256sum -c ) <<SUMS || { echo "STOP: an input differs from the dry run's record"; finish 9; }
480b124df882d6df2df6e3b6815d97d2f81055246cc65e735b11e7a8636945c6  queues/cap.tsv
657add98261173ac5c8dbfe52cb62edfbdcf27cff22388002b9f9e31fb5b8fd0  stage.json
1400ecdef09a3c910fad21b3c8436221a4cef9cead757f291253d26578998ed2  log-dry/DONE
SUMS
n=$(grep -vc '^#' "$OUT/queues/$MODE.tsv"); echo "queue $MODE: $n tasks"
[ "$n" -eq "$NQ" ] || { echo "STOP: queue $MODE is not $NQ tasks"; finish 5; }

# ---- the environment the job will source: lightgbm, scipy and numpy must import (the job checks again)
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck-$MODE.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck-$MODE.log)"; finish 7; }

# ---- the job's first python calls, as the job runs them under Addendum A1: in a subshell, after sourcing (rc checked on
# its own), with root_6_28's python3: the declared limit, which is the --time submitted, then the gate's projection at t0.
echo "plain python3 (not used by any call below): $(command -v python3) $(python3 -V 2>&1)"
out=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/connect-source-$MODE.log" 2>&1; rc=$?
       [ "$rc" -eq 0 ] || { echo "SOURCE_RC=$rc" >&2; exit 97; }
       echo "sourced python3: $(command -v python3) $(python3 -V 2>&1)" >&2
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "NOT_ROOT628" >&2; exit 98; }
       export PYTHONDONTWRITEBYTECODE=1   # no __pycache__ in the deploy, whose porcelain --ignored is checked after
       lim=$(python3 "$D/nd-unfolding/prior_retention/prr_probe.py" limit "$MODE") || exit 96
       echo "LIMIT $lim"
       cd "$D" && python3 - "$OUT" "$MODE" <<'EOF'
import json, sys
from pathlib import Path
sys.path.insert(0, "nd-unfolding/prior_retention")
import prr_probe as p
out, mode = Path(sys.argv[1]), sys.argv[2]
rec = p.read_log(out / "log-dry")
pr = p.project(0.0, 0.0, p.read_queue(out / "queues" / f"{mode}.tsv"), rec)
lim = p.JOB_LIMIT_H[mode]
ok = not pr["unmeasured"] and pr["projected_h"] <= p.GATE_FRACTION * lim
print("PROJECTION " + json.dumps({"mode": mode, "projected_h": round(pr["projected_h"], 4), "limit_h": lim,
                                  "gate_h": p.GATE_FRACTION * lim, "unmeasured": pr["unmeasured"], "pass": ok}))
sys.exit(0 if ok else 95)
EOF
     ) 2> "$OUT/logs/sourced-python-$MODE.err"
lrc=$?
cat "$OUT/logs/sourced-python-$MODE.err"; echo "$out"
[ "$lrc" -ne 97 ] || { echo "STOP: setup_salloc_env.sh failed to source ($(grep SOURCE_RC "$OUT/logs/sourced-python-$MODE.err")); see logs/connect-source-$MODE.log"; finish 7; }
[ "$lrc" -ne 98 ] || { echo "STOP: after sourcing, python3 is not root_6_28's"; finish 7; }
[ "$lrc" -ne 96 ] || { echo "STOP: prr_probe.py limit $MODE failed after sourcing"; finish 7; }
[ "$lrc" -ne 95 ] || { echo "STOP: the gate's projection at t0 does not pass: to the director with the measured rates"; finish 4; }
[ "$lrc" -eq 0 ] || { echo "STOP: the sourced python calls failed (rc $lrc)"; finish 7; }
lim=$(printf '%s\n' "$out" | sed -n 's/^LIMIT //p')
echo "root_6_28 python3 prr_probe.py limit $MODE -> '$lim'"
[ "$lim" = "$DECL_LIMIT" ] || { echo "STOP: the bound code's limit is not the declared $DECL_LIMIT"; finish 7; }
TLIMIT=$(echo "$lim" | awk -F: '{printf "%02d:%02d:%02d", $1, $2, $3}')   # scontrol prints HH:MM:SS
echo "--time=$TLIMIT"

# ---- the submission, from the plain login environment (the job is --export=ALL, so no login-step setting reaches it)
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; finish 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^prr_')" ] || { echo "STOP: a prr_* job appeared"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=prr_$MODE --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/prior_retention/sbatch_prr.sh" "$MODE" "$D" "$M" "$OUT" > "$OUT/logs/submit-$MODE.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-$MODE.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-$MODE.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "$MODE job $job"; echo "$job" > "$OUT/logs/$MODE.jobid"
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
