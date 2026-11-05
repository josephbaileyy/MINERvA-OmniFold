#!/bin/bash
# REF-G1 step two, the timing connect (REF-G1-BINDING-2.md rulings 2, 3 and 5; #786, main 87ae7102; code at M =
# 609d8f24), on a login node, detached: ONE universe unit (universe:Flux:0), timed, before the batch is priced under
# the 5.0 CPU node-h cap. A fresh clean clone at M into $O/deploy-M, porcelain --ignored 0 and the 5 bound blobs
# checked; the iris half-balance check; the job script (refg1_timing_job.sbatch, sha256 3bd7a60a...) written from this
# file and refused unless it is those bytes; one sbatch, --time=00:45:00 (at most 0.75 node-h, against the cap);
# scontrol's TimeLimit must read 00:45:00, else scancel, rc 6. Writes only under $O. No set -u. Any stop is final.
# Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-g1-20261105/timing
D=$O/deploy-M
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
TLIMIT=00:45:00
PRICE=0.75
JOB_SHA=3bd7a60a446ccd0dc6bec0c408b98b0675cede02a12abda5177744b592052945
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$O" ] || bail
[ -z "$(squeue --me -h -n fd_refg1_timing,fd_refg1 -o %i)" ] || bail
mkdir -p "$O/logs" || bail
exec > "$O/logs/connect.log" 2>&1
finish() { echo "refg1 timing submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$O/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$O/logs/refg1_timing_submit.sh"
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$O/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
cfe089d466fa8cb1926d6665fbae65b5d269eaeb nd-unfolding/ref_g1/ref_g1.py
e49ab974598ea3d15663f61da538fad3c9c8f12a nd-unfolding/ref_g1/ref_g1_read.py
2a14b22f169b9a5e616a5498dcba79c682d6766b nd-unfolding/ref_g1/config.json
c68198177807a39d41114c8286edd3d23bc6ab18 nd-unfolding/ref_g1/test_ref_g1.py
4ad3b92570b2196737df57944f94300a90d9ecc5 nd-unfolding/ref_g1/ref_g1_mutation.py
BLOBS
echo "bound blobs: 5 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
cat > "$O/refg1_timing_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 step two, the timing unit (REF-G1-BINDING-2.md ruling 3): ONE universe unit, universe:Flux:0, by the bound
# driver at M from a fresh clean clone, with -B, under the exact interpreter ruling 2 names, 32 threads (config.json
# resources.max_threads_per_task). Porcelain, with --ignored, is recorded before and after. The unit's product goes to
# <O>/units, outside the deploy. Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261105/timing ] || { echo "[refg1t] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[refg1t] refusing: deploy HEAD is not M"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1t] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[refg1t] refusing: the deploy is not clean"; exit 2; }
echo "[refg1t] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
source "$C/setup_salloc_env.sh" > "$O/env.log" 2>&1   # root_6_28, as the s5p and RE-2 jobs source it
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 NUMEXPR_NUM_THREADS=32
mkdir -p "$TMPDIR" "$O/units"
echo "[refg1t] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
t0=$(date +%s.%N)
/usr/bin/time -v -o "$O/unit.time" "$PY" -B "$C/nd-unfolding/ref_g1/ref_g1.py" --unit universe:Flux:0 --out "$O/units" \
    --threads 32 > "$O/unit.log" 2>&1
rc=$?
t1=$(date +%s.%N)
echo "[refg1t] unit rc=$rc wall_s=$(awk -v a=$t0 -v b=$t1 'BEGIN{printf "%.1f", b-a}') end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$O/unit.time"
tail -3 "$O/unit.log"
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1t] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
exit $rc
JOBEOF
j=$(sha256sum "$O/refg1_timing_job.sbatch" | cut -d' ' -f1); echo "refg1_timing_job.sbatch sha256 $j"
[ "$j" = "$JOB_SHA" ] || { echo "STOP: the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
date -u +%FT%TZ
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_refg1_timing --output="$O/logs/%x_%j.out" "$O/refg1_timing_job.sbatch" "$D" "$O" > "$O/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$O/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$O/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "timing job $job"; echo "$job" > "$O/logs/timing.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after submission: $n"
finish 0
