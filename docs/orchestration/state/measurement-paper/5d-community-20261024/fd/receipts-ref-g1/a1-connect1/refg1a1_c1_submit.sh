#!/bin/bash
# REF-G1 A1 connect 1 (REF-G1-BINDING-2-A1.md, #814 at main 410c4868, ruling 4.1; A1 section 5 step 2), on a login node,
# detached, under the binding's fixed conditional sequence (sha256 and result reported, no go awaited):
#   - the COV2D fence (#798): refuses before writing anything if any cov2d-* job is queued or running;
#   - a fresh clean clone at M' = 0bb9a1bf into $O/deploy, porcelain --ignored 0, the 5 blobs the binding lists;
#   - `ref_g1_read.py reads` (the code's own enumeration of the gibu1 unit's and the reader's staged set) and a stat
#     (no read) of every path in it: owner, mode, atime, bytes; the deadline = the earliest atime + 56 days (A1 sec. 4);
#     a path not owned by josephrb is a STOP (O_NOATIME needs the owner);
#   - the price: --time=00:30:00 on 1 node is at most 0.5 node-h; with the 0.1517 spent, under the 5.0 cap; the iris
#     half-balance check;
#   - the job script (refg1a1_c1_job.sbatch) written from this file and refused unless its sha256 is the reviewed one;
#     one sbatch; scontrol's TimeLimit must read 00:30:00, else scancel, rc 6.
# Writes only under the NEW $O. No set -u. Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-g1-20261106
D=$O/deploy
L=$O/logs
M=0bb9a1bfcb462ebd171d337ae1c8b2e2d0905e93
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
TLIMIT=00:30:00
PRICE=0.5
SPENT=0.1517
CAP=5.0
JOB_SHA=f9017bf9d257f56016aa642a5d115beb5dd5f0abfaed859a6cee9c50215b2a1d
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$O" ] && [ -x "$PY" ] || bail
[ -z "$(squeue --me -h -n fd_refg1a1 -o %i)" ] || bail
fence=$(squeue -u josephrb -h -o '%i|%j|%T') || bail                  # the COV2D fence (#798)
printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/ {f=1} END {exit f}' || bail
mkdir -p "$L" || bail
exec > "$L/connect.log" 2>&1
finish() { echo "refg1 a1 connect 1 rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refg1a1_c1_submit.sh"
echo "COV2D fence: no cov2d-* job in squeue at $(date -u +%FT%TZ)"
echo "== price: limit $TLIMIT on 1 node = at most $PRICE node-h; spent $SPENT; cap $CAP"
awk -v p=$PRICE -v s=$SPENT -v c=$CAP 'BEGIN{exit !(p + s <= c)}' || { echo "STOP: the projection is over the cap"; finish 9; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$L/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M'"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
d015a352e0e1789f88f4bd45c088850453850c7f nd-unfolding/ref_g1/ref_g1.py
e045d96215ab266a8b16347ed9b03561a23658d5 nd-unfolding/ref_g1/ref_g1_read.py
245697523a76b7f2a6839f0f70569df73898886e nd-unfolding/ref_g1/config.json
820d4afdede7bf49bd4e19df3d36af1554452f36 nd-unfolding/ref_g1/test_ref_g1.py
2d29a9151d27a85f2ba3d65a48a8a744cf95302a nd-unfolding/ref_g1/ref_g1_mutation.py
BLOBS
echo "bound blobs: 5 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || exit 2
  export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
  cd "$D" && "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py reads > "$L/reads.tsv" 2> "$L/reads.err"
)
rc=$?; echo "reads rc=$rc; $(wc -l < "$L/reads.tsv") paths; roles: $(cut -f1 "$L/reads.tsv" | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
[ $rc = 0 ] && [ -s "$L/reads.tsv" ] || { echo "STOP: reads failed"; cat "$L/reads.err"; finish 4; }
cut -f2 "$L/reads.tsv" | xargs -d '\n' stat -c '%U %a %X %s %n' > "$L/reads-stat-before.txt" 2>&1
[ "$(wc -l < "$L/reads-stat-before.txt")" -eq "$(wc -l < "$L/reads.tsv")" ] || { echo "STOP: a path in the set did not stat"; grep -v '^[a-z]' "$L/reads-stat-before.txt"; finish 4; }
notown=$(awk '$1 != "josephrb"' "$L/reads-stat-before.txt" | wc -l); echo "paths not owned by josephrb: $notown"
[ "$notown" -eq 0 ] || { echo "STOP: O_NOATIME needs the owner:"; awk '$1 != "josephrb"' "$L/reads-stat-before.txt"; finish 4; }
old=$(sort -k3,3n "$L/reads-stat-before.txt" | head -1)
oa=$(echo "$old" | awk '{print $3}')
echo "earliest atime: $(date -u -d @$oa +%FT%TZ) ($(echo "$old" | awk '{print $5}'))"
echo "DEADLINE (earliest atime + 56 days): $(date -u -d @$((oa + 56 * 86400)) +%FT%TZ)"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after reads: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
cat > "$O/refg1a1_c1_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 A1 connect 1, the job (REF-G1-BINDING-2-A1.md ruling 4.1; A1 sections 1, 3, 5): from the fresh clean clone at
# M' (0bb9a1bf), with -B, root_6_28:
#   1. the gibu1 unit ALONE in IBU-1's recorded environment: srun --exclusive -n1 -c 2 (sbatch_ibu1.sh:37; sacct
#      60130813.0 cpu=2), OMP/OPENBLAS/MKL_NUM_THREADS=1 (sbatch_ibu1.sh:25), into the NEW <O>/gibu1; ref_g1.py's
#      gibu1_environment() refuses (rc 4) unless the three variables are exactly "1" and the affinity is exactly 2;
#   2. the bars by the new reader into the NEW read directory <O>/read (bars.json, staged inputs-bars/), from the
#      batch's units (job 60857388, SHA256SUMS 6a4c1929), at 4 threads, as the bars of #791 were made;
#   3. the stat (no read) of `ref_g1_read.py reads`' set again, compared with the connect's stat before the job: every
#      declared input is read through O_NOATIME (A1 section 2), so no atime may move.
# Porcelain, with --ignored, before and after. TMPDIR is <O>/tmp (the units' staging, about 1.5 GB). Writes only under
# <O>. Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"
M=0bb9a1bfcb462ebd171d337ae1c8b2e2d0905e93
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
B=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
L="$O/logs"
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261106 ] || { echo "[a1c1] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[a1c1] refusing: deploy HEAD is not M'"; exit 2; }
for d in gibu1 read; do [ ! -e "$O/$d" ] || { echo "[a1c1] refusing: $O/$d exists"; exit 2; }; done
[ -s "$L/reads.tsv" ] && [ -s "$L/reads-stat-before.txt" ] || { echo "[a1c1] refusing: no stat set from the connect"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[a1c1] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[a1c1] refusing: the deploy is not clean"; exit 2; }
echo "[a1c1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[a1c1] squeue cov2d-* at start (recorded; every read here is O_NOATIME): $(squeue -u josephrb -h -o '%i|%j|%T' | awk -F'|' '$2 ~ /^cov2d-/' | tr '\n' ' ')"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[a1c1] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
unset NUMEXPR_NUM_THREADS
mkdir -p "$TMPDIR"
echo "[a1c1] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
# 1. gibu1, alone, in IBU-1's environment
(
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  srun --exclusive -n1 -c 2 --mem=20G --job-name=gibu1 \
      /usr/bin/time -v -o "$L/gibu1.time" "$PY" -B nd-unfolding/ref_g1/ref_g1.py --unit gibu1 --out "$O/gibu1" \
      --threads 1 > "$L/gibu1.log" 2>&1
)
grc=$?
echo "[a1c1] gibu1 rc=$grc end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$L/gibu1.time"
tail -3 "$L/gibu1.log"
[ -s "$O/gibu1/gibu1.done" ] && echo "[a1c1] gibu1.done: $(cat "$O/gibu1/gibu1.done")"
[ -s "$O/gibu1/gibu1.npz" ] && echo "[a1c1] gibu1.npz sha256 $(sha256sum "$O/gibu1/gibu1.npz" | cut -d' ' -f1) bytes $(stat -c %s "$O/gibu1/gibu1.npz")"
# 2. the bars, by the new reader, into the new read directory
(
  export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
  /usr/bin/time -v -o "$L/bars.time" "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py bars --run "$B/units" \
      --out "$O/read/bars.json" > "$L/bars.log" 2>&1
)
brc=$?
echo "[a1c1] bars rc=$brc end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$L/bars.time"
tail -3 "$L/bars.log"
[ -s "$O/read/bars.json" ] && echo "[a1c1] bars.json sha256 $(sha256sum "$O/read/bars.json" | cut -d' ' -f1)"
# 3. the stat set again: no atime may move
cut -f2 "$L/reads.tsv" | xargs -d '\n' stat -c '%U %a %X %s %n' > "$L/reads-stat-after.txt" 2>&1
if cmp -s "$L/reads-stat-before.txt" "$L/reads-stat-after.txt"; then moved=0; echo "[a1c1] stat set: no atime moved ($(wc -l < "$L/reads-stat-after.txt") files)"
else moved=1; echo "[a1c1] STOP: the stat set changed:"; diff "$L/reads-stat-before.txt" "$L/reads-stat-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[a1c1] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
printf '{"job": "%s", "gibu1_rc": %s, "bars_rc": %s, "atime_moved": %s, "porcelain_after": %s}\n' \
    "$SLURM_JOB_ID" "$grc" "$brc" "$moved" "$na" > "$O/DONE"
cat "$O/DONE"
[ "$grc" = 0 ] && [ "$brc" = 0 ] && [ "$moved" = 0 ] && [ "$na" = 0 ]
JOBEOF
j=$(sha256sum "$O/refg1a1_c1_job.sbatch" | cut -d' ' -f1); echo "refg1a1_c1_job.sbatch sha256 $j"
[ "$j" = "$JOB_SHA" ] || { echo "STOP: the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_refg1a1 --output="$L/%x_%j.out" "$O/refg1a1_c1_job.sbatch" "$D" "$O" > "$L/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$L/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$L/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "job $job"; echo "$job" > "$L/job.id"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
finish 0
