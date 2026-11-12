#!/bin/bash
# RSN J1 connect (RSN-BINDING-1 ruling 3; RSN-DECLARATION.md rev 3 §6 step 3, last two bullets), on one Perlmutter
# login node, at 0 node-h for itself; it submits J1 (rsn_nc, one step, limit 0:19:00). It runs only on the director's
# go for this script's sha256 and the launcher's, which the director gives after the LL5D gates end, with the rsn_
# announcement to every fenced lane.
#   1 refusals before anything is written: the host is not loginNN; a Slurm job is set; the deploy is not clean at
#     M_RSN; $OUT has no rsn-nc-r/1 PASS, or its recorded rsn_regrade.py sha256 is not the deployed and bound one
#     (ruling 4, rechecked); $OUT/fence.txt exists; a J1 product exists; a job whose name starts with any of
#     cov2d, t2a, ll5d, e96data, rpd_ or rsn_ is queued or running (the director's ruling of 2026-11-12);
#   2 $OUT/fence.txt is written with the five fenced prefixes, one per line (cov2d, t2a, ll5d, e96data, rpd_), and its
#     sha256 must equal the pinned one;
#   3 the bound launcher's own smoke mode (RSN_SMOKE=1, outside Slurm) runs every refusal of sbatch_rsn.sh for J1 and
#     prints the step; it reads no npz;
#   4 J1 is submitted: sbatch --parsable --job-name=rsn_J1 --time=0:19:00 --output=$OUT/logs/%x_%j.out
#     $D/nd-unfolding/rsn/sbatch_rsn.sh $D M_RSN $OUT J1, and squeue prints the job.
# Any failure before the submit is a STOP; nothing is repaired or retried. It does not wait for the job.
# Launched from a /dev/shm copy of itself ($1), deleted at exit. No set -u.
SELF=$1
PIN=af7112989417f180e846573c31d101e44e6b02f9
B=/pscratch/sd/j/josephrb/rsn-20261112
D=$B/deploy
OUT=$B/out
REGRADE_SHA=661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652
LAUNCHER_SHA=f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6
FENCE_SHA=5934e32776a9142661188f2239bb91c1fb3f276f50afdbd666f1030d4cfa5894
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3

bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"
head=$(git -C "$D" rev-parse HEAD 2>/dev/null)
porc=$(git -C "$D" status --porcelain --untracked-files=all 2>/dev/null | wc -l)
[ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || bail "the deploy is not $PIN clean (HEAD=$head, $porc porcelain lines)"
[ "$(sha256sum "$D/nd-unfolding/rsn/sbatch_rsn.sh" | cut -d' ' -f1)" = "$LAUNCHER_SHA" ] || bail "sbatch_rsn.sh is not the bound one"
grep -q '"schema": "rsn-nc-r/1"' "$OUT/nc_r.json" 2>/dev/null && grep -q '"verdict": "PASS"' "$OUT/nc_r.json" \
  || bail "$OUT/nc_r.json records no rsn-nc-r/1 PASS"
rec=$("$PY" -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["code_sha256"]["rsn_regrade.py"])' "$OUT/nc_r.json")
dep=$(sha256sum "$D/nd-unfolding/rsn/rsn_regrade.py" | cut -d' ' -f1)
[ "$rec" = "$dep" ] && [ "$dep" = "$REGRADE_SHA" ] || bail "r1: recorded $rec, deployed $dep, bound $REGRADE_SHA"
[ ! -e "$OUT/fence.txt" ] || bail "$OUT/fence.txt exists"
[ ! -e "$OUT/products/rsn_nc.npz" ] || bail "$OUT/products/rsn_nc.npz exists"
q=$(squeue --me -h -o '%i|%j|%T') || bail "squeue failed"
hit=$(printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')
[ -z "$hit" ] || bail "fenced or rsn_ jobs are queued or running: $hit"

echo "node $(hostname) $(date -u +%FT%TZ) slurm_job='$SLURM_JOB_ID'; connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "deploy HEAD $head, porcelain $porc; sbatch_rsn.sh $LAUNCHER_SHA; r1 recorded=deployed=bound $dep"
echo "squeue --me:"; printf '%s\n' "$q"
printf '%s\n' cov2d t2a ll5d e96data rpd_ > "$OUT/fence.txt" || { echo "STOP: fence.txt write failed"; rm -f -- "$SELF"; exit 8; }
fs=$(sha256sum "$OUT/fence.txt" | cut -d' ' -f1); echo "fence.txt sha256 $fs:"; cat "$OUT/fence.txt"
[ "$fs" = "$FENCE_SHA" ] || { echo "STOP: fence.txt is not the pinned bytes ($FENCE_SHA)"; rm -f -- "$SELF"; exit 8; }
mkdir -p "$OUT/logs" || { echo "STOP: mkdir $OUT/logs"; rm -f -- "$SELF"; exit 8; }

echo "== the bound launcher's smoke mode for J1 (no npz read)"
RSN_SMOKE=1 bash "$D/nd-unfolding/rsn/sbatch_rsn.sh" "$D" "$PIN" "$OUT" J1 > "$OUT/logs/j1-smoke.txt" 2>&1; r=$?
cat "$OUT/logs/j1-smoke.txt"; echo "smoke rc=$r"
[ $r = 0 ] && grep -q '^\[rsn\] smoke: checks passed, 1 steps' "$OUT/logs/j1-smoke.txt" \
  || { echo "STOP: the launcher's smoke did not pass for J1"; rm -f -- "$SELF"; exit 8; }

q2=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; rm -f -- "$SELF"; exit 8; }
hit=$(printf '%s\n' "$q2" | awk -F'|' '$2 ~ /^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')
[ -z "$hit" ] || { echo "STOP: fenced or rsn_ jobs appeared: $hit"; rm -f -- "$SELF"; exit 8; }
echo "== submit J1 $(date -u +%FT%TZ)"
jid=$(sbatch --parsable --job-name=rsn_J1 --time=0:19:00 --output="$OUT/logs/%x_%j.out" \
      "$D/nd-unfolding/rsn/sbatch_rsn.sh" "$D" "$PIN" "$OUT" J1); r=$?
echo "sbatch rc=$r jobid=$jid"
[ $r = 0 ] && [ -n "$jid" ] || { echo "STOP: sbatch failed"; rm -f -- "$SELF"; exit 8; }
squeue -j "$jid" -o '%i|%j|%T|%l|%P|%q|%D' 2>&1
echo "J1 SUBMITTED: jobid $jid, rsn_J1, limit 0:19:00, deploy $D at $PIN, out $OUT"
rm -f -- "$SELF"; exit 0
