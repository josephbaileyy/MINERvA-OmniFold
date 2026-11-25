#!/bin/bash
# EVW5D: the connect, on a Perlmutter login node, in the foreground, after the director's binding and GO on this
# script's sha256, the tool commit and the launcher. ESS's connect (fd/receipts-ess/cluster/logs/ess_connect.sh),
# adapted. In order, each failure a final stop before anything is submitted:
#   preconditions (nothing written): the tool pin is filled in; $OUT absent; no evw5d job queued or running (squeue
#     --me, fails closed); the three shared inputs present at their recorded sizes (stat of each explicit path);
#   then $OUT/logs and this connect's log; the stat records of the three inputs (stat does not move atime);
#   the balance from iris: the job's bound, 0.5 node-h (one node x --time 00:30:00), at most half of m3246's balance;
#   a fresh clone into $OUT/deploy at the code pin abdc88c5, clean (porcelain --ignored 0), the eleven producer files
#     and setup_salloc_env.sh at their recorded sha256; the main pin present;
#   a fresh clone into $OUT/toolclone at the tool commit, clean, with evw5d.py, sbatch_evw5d.sh and ess_capture.py at
#     their approved sha256;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell, python3 = root_6_28's, numpy,
#     lightgbm and ROOT import (versions printed), and os.O_NOATIME exists;
#   one sbatch, with every inherited SBATCH_/SLURM_/SALLOC_ variable removed and the allocation, output and error
#     given explicitly (--nodes=1 --ntasks=1 --time=00:30:00 --parsable); then scontrol must show one node, no array
#     and TimeLimit 00:30:00, or the job is cancelled at once.
# $OUT itself is the lane's claim: created with mkdir (no -p), so a second connect cannot share it.
# Writes only under $OUT (on $SCRATCH; nothing on CFS). No set -u (it kills setup_salloc_env.sh). Launched from a
# /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/evw5d-20261125
D=$OUT/deploy
TC=$OUT/toolclone
PIN=abdc88c52b909cfc1eb658ae97bd9defc8f640e7
MAIN=025459c8f4a92d65239cecc3cc3a09cd5de13c15
TOOLC=__TOOL_COMMIT__
EVW_SHA=__EVW5D_PY_SHA256__
SBATCH_SHA=__SBATCH_SHA256__
CAPTURE_SHA=4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da
BOUND=0.5
TLIMIT=00:30:00
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REF=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
LANE_PARENT=/pscratch/sd/j/josephrb
[ -d "$LANE_PARENT" ] && [ ! -L "$LANE_PARENT" ] && [ "$(cd "$LANE_PARENT" && pwd -P)" = "$LANE_PARENT" ] || bail
case "$TOOLC$EVW_SHA$SBATCH_SHA" in *__*) bail;; esac
[ ! -e "$OUT" ] || bail
q=$(squeue --me -h -o '%j') || bail                 # fails closed
[ -z "$(printf '%s\n' "$q" | grep -E '^evw5d$')" ] || bail
[ "$(stat -c %s "$NPZ" 2>/dev/null)" = 1548438020 ] || bail
[ "$(stat -c %s "$BKG" 2>/dev/null)" = 16017201 ] || bail
[ "$(stat -c %s "$REF" 2>/dev/null)" = 95564 ] || bail
mkdir "$OUT" || bail                               # the exclusive claim
mkdir "$OUT/logs" || bail
[ "$(cd "$OUT" && pwd -P)" = "$OUT" ] && [ "$(cd "$OUT/logs" && pwd -P)" = "$OUT/logs" ] || bail   # the job's own check
LOG=$OUT/logs/connect.log
exec > "$LOG" 2>&1
finish() { echo "evw5d connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/evw5d_connect.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
echo "== the shared inputs (stat: name|bytes|atime|mtime|inode)"
stat -c '%n|%s|%X|%Y|%i' "$NPZ" "$BKG" "$REF" | tee "$OUT/logs/stat-connect.txt"

# ---- the balance (ESS's method): iris's m3246 row, Allocated - Charged
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') bound=$BOUND"
awk -v b=$bal -v c=$BOUND 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the bound $BOUND is above half the balance $bal"; finish 9; }

# ---- the deploy: a fresh clone at the code pin, clean, the producer's bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$PIN" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "STOP: HEAD is not the code pin"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "deploy HEAD $PIN; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D" && sha256sum -c ) <<SUMS || { echo "STOP: a producer file is not the recorded one"; finish 9; }
8981f97b96b418cfe46f1e940cb120f174053d7d3429f3b0b01a229c6c02ee6c  nd-unfolding/s5n_pseudo.py
d81d4f46fb55f25fdf7ce2e4b9a9a63bf876beaf754bdc250eee974579e11f5d  nd-unfolding/s5c_pseudo.py
510d749a2e82fa448de6172753ae2adc9ebd81a89d4f18bf76beb5faa8bb3968  nd-unfolding/s5c_unfold.py
24f87f119073c4f125c2f753310507d4375b6f8a1b7751e59d3615dd50e90582  nd-unfolding/omnifold_nn_core.py
454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5  nd-unfolding/xsec_nd.py
8ebe0277ee4c277f6f697712a901b14d6ba24ed5dcadfc3c66b29276acf81b5e  2d-unfolding/unfold_2d_omnifold_unbinned.py
bda8c48ce2365e173bbba083b18233d6f6b7c2dfbab5179156073860c8281ec7  nd-unfolding/s5e_candidate.py
6726ff99c7787d1ee6dff7fa5d08df88f9df76285d98c4c462f964ac6164779f  nd-unfolding/s5e_deform.py
c47e9dd3feef9eab323e40f4e0da770ad67e86431a1ce95f99a10007decc66c1  nd-unfolding/s5e_trace.py
9d7c12322200dc2dca2944883ad0f51e41e58a70d5ac3d87991c3bb85611630a  nd-unfolding/s5p_numerics.py
26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71  nd-unfolding/s5p_stage1_inspect.py
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
SUMS
git -C "$D" cat-file -e "$MAIN^{commit}" || { echo "STOP: the main pin is not in the clone"; finish 9; }

# ---- the tool: a second fresh clone at the tool commit, clean, the approved bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$TC" > "$OUT/logs/toolclone.log" 2>&1 || { echo "STOP: tool clone"; finish 3; }
git -C "$TC" -c advice.detachedHead=false checkout -q "$TOOLC" || { echo "STOP: tool checkout"; finish 3; }
[ "$(git -C "$TC" rev-parse HEAD)" = "$TOOLC" ] || { echo "STOP: the tool clone's HEAD is not the tool commit"; finish 9; }
n=$(git -C "$TC" status --porcelain --ignored | wc -l); echo "tool HEAD $TOOLC; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the tool clone is not clean"; finish 9; }
( cd "$TC" && sha256sum -c ) <<SUMS || { echo "STOP: the tool is not the approved bytes"; finish 9; }
$EVW_SHA  nd-unfolding/evw5d/evw5d.py
$SBATCH_SHA  nd-unfolding/evw5d/sbatch_evw5d.sh
$CAPTURE_SHA  nd-unfolding/ess_e/ess_capture.py
SUMS

# ---- the environment the job will source (0 node-h)
out=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1; rc=$?
       echo "SOURCE_RC=$rc"; [ "$rc" -eq 0 ] || exit 96
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo NOT_ROOT628; exit 98; }
       PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import os, sys, numpy, lightgbm, ROOT; assert hasattr(os, 'O_NOATIME'); print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'lightgbm', lightgbm.__version__, 'ROOT', ROOT.gROOT.GetVersion(), 'O_NOATIME', os.O_NOATIME)" || exit 97 )
erc=$?
echo "$out"
[ "$erc" -eq 0 ] || { echo "STOP: the environment pre-check failed (rc $erc; see env-precheck.log)"; finish 7; }
for c in "$D" "$TC"; do
  st=$(git -C "$c" status --porcelain --ignored) || { echo "STOP: git status failed in $c"; finish 9; }
  [ -z "$st" ] || { echo "STOP: the pre-check changed $c"; finish 9; }
done

# ---- the submission, from the plain login environment
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; finish 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^evw5d$')" ] || { echo "STOP: an evw5d job appeared"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
for v in $(env | sed -n 's/^\(\(SBATCH\|SLURM\|SALLOC\)_[A-Za-z0-9_]*\)=.*/\1/p'); do unset "$v"; done
echo "inherited scheduler variables left: $(env | grep -cE '^(SBATCH|SLURM|SALLOC)_')"
sbatch --parsable --nodes=1 --ntasks=1 --time=$TLIMIT --job-name=evw5d \
  --output="$OUT/logs/%x_%j.out" --error="$OUT/logs/%x_%j.err" \
  "$TC/nd-unfolding/evw5d/sbatch_evw5d.sh" "$D" "$PIN" "$OUT" "$TC" "$TOOLC" "$EVW_SHA" > "$OUT/logs/submit.out" 2> "$OUT/logs/submit.err"
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit.out" "$OUT/logs/submit.err"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^\([0-9][0-9]*\)\(;.*\)\{0,1\}$/\1/p' "$OUT/logs/submit.out")
[ -n "$job" ] && [ "$(wc -l < "$OUT/logs/submit.out")" -eq 1 ] || { echo "STOP: not one job id"; finish 9; }
echo "evw5d job $job"; echo "$job" > "$OUT/logs/evw5d.jobid"
sj=$(scontrol show job "$job")
tl=$(printf '%s\n' "$sj" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
nn=$(printf '%s\n' "$sj" | sed -n 's/.*NumNodes=\([^ ]*\).*/\1/p' | head -1)
arr=$(printf '%s\n' "$sj" | grep -c 'ArrayJobId=')
echo "scontrol TimeLimit=$tl (declared $TLIMIT) NumNodes=$nn array_lines=$arr"
if [ "$tl" != "$TLIMIT" ] || [ "$nn" != 1 ] || [ "$arr" != 0 ]; then
  scancel "$job"; echo "STOP: the allocation is not one 30-minute node; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
finish 0
