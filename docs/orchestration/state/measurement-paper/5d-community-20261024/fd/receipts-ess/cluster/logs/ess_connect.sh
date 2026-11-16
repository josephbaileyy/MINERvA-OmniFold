#!/bin/bash
# ESS rerun of configuration (e)'s central data unfold: the connect, on a Perlmutter login node, in the foreground,
# after the director's go on this script's sha256, the tool commit's two files and the launcher.
# In order, each failure a final stop before anything is submitted:
#   preconditions (nothing written): $OUT absent; no ess_* job queued or running (squeue --me, fails closed); the three
#     shared inputs present at their recorded sizes, by stat of each explicit path (no directory is listed);
#   then $OUT/logs and this connect's log; the stat records of the three inputs (stat does not move atime);
#   the balance from iris: the job's bound, 0.5 node-h (one node x --time 00:30:00), at most half of m3246's balance;
#   a fresh clone into $OUT/deploy at the code pin abdc88c5 (the producer's code), clean (porcelain --ignored 0), the
#     eleven producer files and setup_salloc_env.sh at their recorded sha256; the main pin and the tool commit present;
#   the tool: ess_capture.py and sbatch_ess.sh taken from the tool commit by git show into $OUT/tool, each at its
#     approved sha256;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell, python3 = root_6_28's, and
#     numpy, lightgbm and ROOT import (versions printed);
#   one sbatch, from the plain login environment: --job-name=ess_e --time=00:30:00 sbatch_ess.sh; then scontrol's
#     TimeLimit must read 00:30:00 or the job is cancelled at once.
# Writes only under $OUT. No set -u (it kills setup_salloc_env.sh). Launched from a /dev/shm copy of itself, whose path
# is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/ess-e-20261110
D=$OUT/deploy
PIN=abdc88c52b909cfc1eb658ae97bd9defc8f640e7
MAIN=025459c8f4a92d65239cecc3cc3a09cd5de13c15
TOOLC=96a13a792e4e010aa895f47fb5915d6ef9987d1f
CAPTURE_SHA=4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da
SBATCH_SHA=7ceb35bbc839ae3c7a1d7937ac3d7b07c431cf14f0bc8f7e44ab80eb313909c2
BOUND=0.5
TLIMIT=00:30:00
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REF=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
bail() { rm -f -- "$SELF"; exit 9; }                # a precondition failed: nothing written
[ ! -e "$OUT" ] || bail
q=$(squeue --me -h -o '%j') || bail                 # fails closed
[ -z "$(printf '%s\n' "$q" | grep -E '^ess_')" ] || bail
[ "$(stat -c %s "$NPZ" 2>/dev/null)" = 1548438020 ] || bail
[ "$(stat -c %s "$BKG" 2>/dev/null)" = 16017201 ] || bail
[ "$(stat -c %s "$REF" 2>/dev/null)" = 95564 ] || bail
mkdir -p "$OUT/logs" || bail
LOG=$OUT/logs/connect.log
exec > "$LOG" 2>&1
finish() { echo "ess connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/ess_connect.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
echo "== the shared inputs (stat: name|bytes|atime|mtime|inode)"
stat -c '%n|%s|%X|%Y|%i' "$NPZ" "$BKG" "$REF" | tee "$OUT/logs/stat-connect.txt"

# ---- the balance (coverage-5b's method): iris's m3246 row, Allocated - Charged
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') bound=$BOUND"
awk -v b=$bal -v c=$BOUND 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the bound $BOUND is above half the balance $bal"; finish 9; }

# ---- the deploy: a fresh clone at the code pin, clean, the producer's bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$PIN" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "STOP: HEAD is not the code pin"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $PIN; porcelain --ignored lines before: $n"
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
git -C "$D" cat-file -e "$TOOLC^{commit}" || { echo "STOP: the tool commit is not in the clone"; finish 9; }

# ---- the tool, from the tool commit, at the approved bytes
mkdir "$OUT/tool" || finish 9
git -C "$D" show "$TOOLC:nd-unfolding/ess_e/ess_capture.py" > "$OUT/tool/ess_capture.py" || { echo "STOP: git show ess_capture.py"; finish 9; }
git -C "$D" show "$TOOLC:nd-unfolding/ess_e/sbatch_ess.sh" > "$OUT/tool/sbatch_ess.sh" || { echo "STOP: git show sbatch_ess.sh"; finish 9; }
( cd "$OUT/tool" && sha256sum -c ) <<SUMS || { echo "STOP: the tool is not the approved bytes"; finish 9; }
$CAPTURE_SHA  ess_capture.py
$SBATCH_SHA  sbatch_ess.sh
SUMS

# ---- the environment the job will source (0 node-h)
out=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1; rc=$?
       echo "SOURCE_RC=$rc"
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo NOT_ROOT628; exit 98; }
       PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys, numpy, lightgbm, ROOT; print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'lightgbm', lightgbm.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 97 )
erc=$?
echo "$out"
[ "$erc" -eq 0 ] || { echo "STOP: the environment pre-check failed (rc $erc; see env-precheck.log)"; finish 7; }
n=$(git -C "$D" status --porcelain --ignored | wc -l)
[ "$n" -eq 0 ] || { echo "STOP: the pre-check changed the deploy ($n lines)"; finish 9; }

# ---- the submission, from the plain login environment
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; finish 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^ess_')" ] || { echo "STOP: an ess_* job appeared"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=ess_e --output="$OUT/logs/%x_%j.out" \
  "$OUT/tool/sbatch_ess.sh" "$D" "$PIN" "$OUT" "$OUT/tool" > "$OUT/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "ess_e job $job"; echo "$job" > "$OUT/logs/ess.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
finish 0
