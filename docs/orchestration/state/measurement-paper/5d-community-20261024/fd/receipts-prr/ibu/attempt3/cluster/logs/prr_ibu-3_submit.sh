#!/bin/bash
# FD-PRR job prr_ibu (route 2), attempt 3: the connect, on a Perlmutter login node, detached, after the director's go for this
# connect
# (FD-PRR BINDING 1 rulings 4, 5 and 7, addendums A1, A3 and A4: attempt 3 runs from M_A4 = cb13a644). In order, each
# failure a final stop before anything is submitted:
#   preconditions: $OUT and the dry run's DONE (no STOP) exist; nothing of attempt 3 exists yet (its deploy-ibu-3,
#     connect-ibu-3 log, ibu-3.jobid); log-ibu and $OUT/route2 are absent, attempt 2's moved into $OUT/ibu-attempt2; no prr_* job queued or running (squeue --me; fails closed). ll5d_*,
#     ens1_* and fd1b_* jobs are listed, not refused: this job reads nothing outside $OUT and the deploy (prr_ibu.py
#     reads the queues, stage.json and the staged copies, under REF-G1's read guard) and copies nothing;
#   (no login-node sweep: login07, login17 and login19 were closed as unreached on two sweeps, the director's ruling)
#   the balance from iris: the cap 27.0 at most half of m3246's remaining balance; and the study's charge so far
#     (sacct, every ended prr_* job's ElapsedRaw x NNodes; prr_dry 61022062, prr_iter 61024185, prr_cap 61028298
#     and prr_misc 61030122 as recorded, and attempts 1 and 2, prr_ibu 61035510 FAILED in 41 s and 61043652 in 132 s)
#     plus this job's --time at most the cap 27.0;
#   a fresh clone at M_A4 into $OUT/deploy-ibu-3, clean (porcelain --ignored 0), the six FD-PRR files at their bound
#     sha256 and the declaration, addendums A1, A3 and A4 and BINDING 1 at theirs; stage-a4.json and its four rho
#     copies at the staging connect's digests (Addendum A4 section 5);
#   the inputs this job starts from, at the digests the dry run recorded: the four queues prr_ibu.py reads its B0
#     lines from (prr_probe.JOBS: dry, iter, cap, misc), stage.json and log-dry/DONE; the queues carry 20 B0 lines,
#     one per route-2 experiment (prr_ibu.experiments(): 12 truths at 991000, A7_gibuu and nominal at 4 floor seeds);
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell; lightgbm, scipy, numpy import;
#   the job's first python calls, after sourcing with root_6_28's python3 (the source's rc checked on its own):
#     `prr_probe.py limit ibu` must print the declared 0:30:00, and it is the --time submitted. There is no gate
#     projection: route 2 runs as one call, not through the gate (sbatch_prr.sh:104-112 @ M_A4, unchanged from M_A3), and the dry run has no
#     ibu record, so its wall time is unmeasured; the --time bounds the charge at 0.5 node-h;
#   one sbatch, from the plain login environment: --job-name=prr_ibu --time=00:30:00 sbatch_prr.sh ibu; then
#     scontrol's TimeLimit must read 00:30:00 or the job is cancelled at once.
# The job (sbatch_prr.sh) re-checks the name, the TimeLimit, the dry run's DONE and its 15 ends, re-verifies every staged
# copy, then runs prr_ibu.py once into $OUT/route2. Writes only under $OUT. No set -u (it kills setup_salloc_env.sh).
# Attempts 1's and 2's files (deploy-ibu, deploy-ibu-2, logs/*ibu*, $OUT/ibu-attempt2) are not touched: every connect-side
# name here carries TAG=ibu-3; the job keeps the name prr_ibu and writes log-ibu and route2, so prr_read is unchanged.
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit. The deploy stays.
SELF=$1
MODE=ibu
TAG=ibu-3
NB0=20
DECL_LIMIT=0:30:00
M=cb13a6443a457bd3887d1c421723dfcdb1909ec8
OUT=/pscratch/sd/j/josephrb/fd-prr-20261108
D=$OUT/deploy-$TAG
CAP=27.0
DECL_SHA=5be1e19cb8db67064cb0f90382ed7ac2365a2ed4841d9b498f323ed2761b64ce
A1_SHA=ca6b8457e74c9323fcb985766a88f404038f6f16c3e822a67bf2606af223f38b
BIND_SHA=634cded38a1780286d24941ce567c174ff17ccc1b6af640f24129c5e6275b613   # FD-PRR-BINDING-1.md at main, with A4 bound
A3_SHA=48641cf9ba6a6e30856dc3447412cca777bcc0b75f84566db9f4463d9e646db1
A4_SHA=3ba2f47ba0d9b40155d6840ca22f665051a4f6cdaf15fd0efe24564929bdc6a8
STAGE_A4_SHA=00457e58f135c6bff0207901f9bb977ce6338d9b01971df376d2fe333750d7df
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
[ -d "$OUT" ] && [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] && [ ! -e "$OUT/log-dry/FAILED" ] || bail
[ -d "$OUT/ibu-attempt2/log-ibu" ] && [ -d "$OUT/ibu-attempt2/route2" ] && [ -s "$OUT/stage-a4.json" ] || bail   # the move and the staging are done
for p in "$OUT/log-$MODE" "$OUT/route2" "$D" "$OUT/logs/connect-$TAG.log" "$OUT/logs/connect-$TAG.done" "$OUT/logs/$TAG.jobid"; do
  [ ! -e "$p" ] || bail
done
q=$(squeue --me -h -o '%j') || bail                 # fails closed: no answer from squeue, no connect
[ -z "$(printf '%s\n' "$q" | grep -E '^prr_')" ] || bail
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
finish() { echo "prr $TAG submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$TAG.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/prr_${TAG}_submit.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
echo "other lanes' families (listed, not refused; this job reads nothing outside \$OUT and the deploy):"
printf '%s\n' "$q" | grep -E '^(ll5d_|ens1_|fd1b_)' || echo "  none"

# ---- the balance (coverage-5b's method): iris's m3246 row, Allocated - Charged; and the study's charge against the cap
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b=$bal -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap $CAP is above half the balance $bal: to the director"; finish 9; }
echo "== the study's charge so far (sacct, prr_* jobs since 2026-11-08)"
sacct -X -n -P -S 2026-11-08T00:00:00 -o JobID,JobName,State,ElapsedRaw,NNodes --name=prr_dry,prr_iter,prr_cap,prr_misc,prr_ibu \
  > "$OUT/logs/charge-before-$TAG.txt" 2>&1 || { echo "STOP: sacct did not answer"; cat "$OUT/logs/charge-before-$TAG.txt"; finish 9; }
cat "$OUT/logs/charge-before-$TAG.txt"
grep -q '^61022062|prr_dry|COMPLETED|3648|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show the dry run 61022062 as recorded"; finish 9; }
grep -q '^61024185|prr_iter|COMPLETED|9038|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show prr_iter 61024185 as recorded"; finish 9; }
grep -q '^61028298|prr_cap|COMPLETED|5220|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show prr_cap 61028298 as recorded"; finish 9; }
grep -q '^61030122|prr_misc|COMPLETED|8657|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show prr_misc 61030122 as recorded"; finish 9; }
grep -q '^61035510|prr_ibu|FAILED|41|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show attempt 1, prr_ibu 61035510, as recorded"; finish 9; }
grep -q '^61043652|prr_ibu|FAILED|132|1$' "$OUT/logs/charge-before-$TAG.txt" || { echo "STOP: sacct does not show attempt 2, prr_ibu 61043652, as recorded"; finish 9; }
awk -F'|' '$3 ~ /^(PENDING|RUNNING|REQUEUED)/ {bad=1} END {exit bad}' "$OUT/logs/charge-before-$TAG.txt" \
  || { echo "STOP: a prr_* job is not ended"; finish 9; }
spent=$(awk -F'|' '{s += $4 * $5 / 3600} END {printf "%.4f", s}' "$OUT/logs/charge-before-$TAG.txt")
lim_h=$(echo "$DECL_LIMIT" | awk -F: '{printf "%.4f", $1 + $2/60 + $3/3600}')
echo "charged_node_h=$spent this_job_limit_h=$lim_h sum=$(awk -v a=$spent -v b=$lim_h 'BEGIN{printf "%.4f", a+b}') cap=$CAP"
awk -v a=$spent -v b=$lim_h -v c=$CAP 'BEGIN{exit !(a + b <= c)}' || { echo "STOP: the charge so far plus this --time is above the cap"; finish 9; }

# ---- the deploy: a fresh clone at M_A4, clean, the bound bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-$TAG.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A4"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/prior_retention" && sha256sum -c ) <<SUMS || { echo "STOP: the FD-PRR files are not the bound ones"; finish 9; }
f87ee90c58d2b8904fe881931edc61966a6adda8be7eb503da6644797a3d1232  prr_probe.py
fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0  prr_ibu.py
d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe  prr_read.py
4493aad5dff0a8a0316c0f8b4d159c8f08c7666856474b5cf9c4c963a3a7e975  sbatch_prr.sh
fad928d85c9183ac525ffabcd809d6968afab6aead4a2ad2aa13202b788eef40  test_prr.py
e088406cd47ef88c8e47b988e7f684f8c29b74a620fa65d101ac790ca7892d5f  prr_mutation.py
SUMS
S=$D/docs/orchestration/state/measurement-paper/5d-community-20261024
decl=$(sha256sum "$S/FD-PRR-DECLARATION.md" | cut -d' ' -f1); echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }
a1=$(sha256sum "$S/FD-PRR-ADDENDUM-A1.md" | cut -d' ' -f1); echo "addendum A1 sha256 $a1"
[ "$a1" = "$A1_SHA" ] || { echo "STOP: Addendum A1 is not the bound one"; finish 9; }
a3=$(sha256sum "$S/FD-PRR-ADDENDUM-A3.md" | cut -d' ' -f1); echo "addendum A3 sha256 $a3"
[ "$a3" = "$A3_SHA" ] || { echo "STOP: Addendum A3 is not the bound one"; finish 9; }
a4=$(sha256sum "$S/FD-PRR-ADDENDUM-A4.md" | cut -d' ' -f1); echo "addendum A4 sha256 $a4"
[ "$a4" = "$A4_SHA" ] || { echo "STOP: Addendum A4 is not the bound one"; finish 9; }
bmain=$(git -C "$D" show origin/main:docs/orchestration/state/measurement-paper/5d-community-20261024/FD-PRR-BINDING-1.md | sha256sum | cut -d' ' -f1)
echo "FD-PRR-BINDING-1.md at origin/main $(git -C "$D" rev-parse origin/main) sha256 $bmain"
[ "$bmain" = "$BIND_SHA" ] || { echo "STOP: BINDING 1 on main is not the one this connect was made against: to the director"; finish 9; }

# ---- the inputs this job starts from, at the dry run's recorded digests (fd/receipts-prr/dry/cluster/SHA256SUMS)
( cd "$OUT" && sha256sum -c ) <<SUMS || { echo "STOP: an input differs from the dry run's record"; finish 9; }
9fb47269c466f908c815702e90a3d41b714b7311031b3a937fe37afab13e2825  queues/dry.tsv
e0f02c1c817175bd7ceaa9a92bb815c486569264b5acc33aa8e17c30d816d357  queues/iter.tsv
480b124df882d6df2df6e3b6815d97d2f81055246cc65e735b11e7a8636945c6  queues/cap.tsv
4ed1579298adb43b0ef4f7d4595c179696018c6245474a6c7dc37b597521d969  queues/misc.tsv
657add98261173ac5c8dbfe52cb62edfbdcf27cff22388002b9f9e31fb5b8fd0  stage.json
1400ecdef09a3c910fad21b3c8436221a4cef9cead757f291253d26578998ed2  log-dry/DONE
$STAGE_A4_SHA  stage-a4.json
124e726163b38d24735bacfc67e2d88bec1e47634dc5d294f6460fe4223efb8b  stage/s5p-nullsF/rho-genie_cv-F.npz
2945a15a54dcf71f7ff495555f3cd0efb6c486232c2ddc18d6bbad46579e09b3  stage/s5p-nullsF/rho-genie_mec-F.npz
d8f52112b010e5adb6a56fa4aa3629b4c98ab62a1cea3b4190af77c3ac33491b  stage/s5p-nullsF/rho-gibuu_cv-F.npz
c5e10bd0edf70b8aced95ab8214630998fd1c903683570be30b85e25c12637fd  stage/s5p-nullsF/rho-nuwro_cv-F.npz
SUMS
n=$(cat "$OUT"/queues/dry.tsv "$OUT"/queues/iter.tsv "$OUT"/queues/cap.tsv "$OUT"/queues/misc.tsv | grep -v '^#' | cut -f2 | grep -cx B0)
echo "B0 lines in the four queues: $n"
[ "$n" -eq "$NB0" ] || { echo "STOP: the queues do not carry $NB0 B0 lines"; finish 5; }

# ---- the environment the job will source: lightgbm, scipy and numpy must import (the job checks again)
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck-$TAG.log" 2>&1
  python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck-$TAG.log)"; finish 7; }

# ---- the job's first python calls, as the job runs them under Addendum A1: in a subshell, after sourcing (rc checked on
# its own), with root_6_28's python3: the declared limit, which is the --time submitted (no projection for ibu).
echo "plain python3 (not used by any call below): $(command -v python3) $(python3 -V 2>&1)"
out=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/connect-source-$TAG.log" 2>&1; rc=$?
       [ "$rc" -eq 0 ] || { echo "SOURCE_RC=$rc" >&2; exit 97; }
       echo "sourced python3: $(command -v python3) $(python3 -V 2>&1)" >&2
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "NOT_ROOT628" >&2; exit 98; }
       export PYTHONDONTWRITEBYTECODE=1   # no __pycache__ in the deploy, whose porcelain --ignored is checked after
       lim=$(python3 "$D/nd-unfolding/prior_retention/prr_probe.py" limit "$MODE") || exit 96
       echo "LIMIT $lim"
     ) 2> "$OUT/logs/sourced-python-$TAG.err"
lrc=$?
cat "$OUT/logs/sourced-python-$TAG.err"; echo "$out"
[ "$lrc" -ne 97 ] || { echo "STOP: setup_salloc_env.sh failed to source ($(grep SOURCE_RC "$OUT/logs/sourced-python-$TAG.err")); see logs/connect-source-$TAG.log"; finish 7; }
[ "$lrc" -ne 98 ] || { echo "STOP: after sourcing, python3 is not root_6_28's"; finish 7; }
[ "$lrc" -ne 96 ] || { echo "STOP: prr_probe.py limit $MODE failed after sourcing"; finish 7; }
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
  "$D/nd-unfolding/prior_retention/sbatch_prr.sh" "$MODE" "$D" "$M" "$OUT" > "$OUT/logs/submit-$TAG.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-$TAG.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-$TAG.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "$TAG job $job"; echo "$job" > "$OUT/logs/$TAG.jobid"
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
