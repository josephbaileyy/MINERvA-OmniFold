#!/bin/bash
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas' completion connect (REF-C2C1-BINDING-2.md ruling 2.2; the
# director's ruling of 2026-11-06: the four TIMEOUT jobs 60890529-32 are INVALID, the 303 PASS units stand, one completion
# job for the 47 missing c2_replica units, a fit check before submission and in the job), on a login node, detached.
# As the replicas connect (b9642fcf) with these changes:
#   - the gate adds the TIMEOUT record: in a fresh clone, `git fetch origin main`, each committed
#     units-replicas/timeout/REPLICAS-TIMEOUT-j<J> hashes equal to the pscratch record; then (O_NOATIME reads) lanes.tsv
#     is the reviewed one (7b737d0c), the four PASS sets are disjoint and each unit's .done is PASS, and lanes-j4.tsv's
#     47 units are exactly the 350 minus those sets, none with any file under units/;
#   - THE FIT, before sbatch: NL x MEM within the partition's MaxMemPerNode (scontrol show partition) and NL x 64
#     within its CPUs per node (sinfo), else no submission; after sbatch the job's Partition must be that one;
#   - one job, index 4, --time=01:30:00: at most 1.5 node-h; spent 10.4156 (C-DRAW 0.1789, the centrals 0.2050, the
#     TIMEOUT jobs 10.0317), so at most 11.9156 of the 12.5 cap;
#   - lanes-j4.tsv and the job script refc2c1_completion_job.sbatch, each refused unless its sha256 is the reviewed one;
#   - deploy, logs and library check in their own directories (deploy-completion, logs-completion, libcheck-completion);
#     the watch list rebuilt and required byte-equal to the replicas' one.
# Unchanged: the CENTRALS-DONE gate, the clean clone at M with the 8 blobs, libRooUnfold.so's O_NOATIME check, the fence
# a recorded line, the iris half-balance check, TimeLimit checked (scancel, rc 6). Writes only under $O. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
D=$O/deploy-completion
L=$O/logs-completion
M=77d76cfc2d621f8faa010b75006811868494652a
LIB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
LIB_SHA=0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
TLIMIT=01:30:00
PRICE=1.5
SPENT=10.4156
CAP=12.5
PART=regular_milan_ss11
NL=4
MEM_MB=114688
LANES_SHA=7b737d0c4bb5e547adae0376f9c50da00cc1ec9a08d7dc2c892804e0b968524c
LANES4_SHA=b6d66658d2cdd438e202f2194c8c93a36ae7ee9af7cb0c51c452657c7069cae3
JOB_SHA=c82055f6f8dea72a2e16fb4722d1613610576e929209b4a7c5eea0123b24589f
TP=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/units-replicas/timeout
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -d "$O/stage" ] && [ -d "$O/units" ] && [ -s "$O/CENTRALS-DONE" ] && [ -x "$PY" ] && [ -s "$O/logs-replicas/lanes.tsv" ] || bail
for x in deploy-completion libcheck-completion logs-completion tmp-replicas-j4 REPLICAS-DONE-j4; do [ ! -e "$O/$x" ] || bail; done
for J in 0 1 2 3; do [ -s "$O/REPLICAS-TIMEOUT-j$J" ] && [ ! -e "$O/REPLICAS-DONE-j$J" ] || bail; done
[ -z "$(squeue --me -h -n fd_c2c1r -o %i)" ] || bail
mkdir -p "$L" "$O/libcheck-completion" || bail
exec > "$L/connect.log" 2>&1
finish() { echo "ref-c2c1 completion connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refc2c1_completion_submit.sh"
echo "fence, recorded (the director's ruling of 2026-11-06): squeue -u josephrb at $(date -u +%FT%TZ):"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed 's/^/  /'
cd_rec=$(cat "$O/CENTRALS-DONE"); echo "gate: CENTRALS-DONE $cd_rec"
[ "$cd_rec" = '{"job": "60889566", "rcs": "0 0 0", "pass_markers": 3, "porcelain_after": 0}' ] || { echo "STOP: part 1's record is not the accepted one"; finish 4; }
for f in runEventLoopOmniFold_MEFHC.root runEventLoopMC_MEFHC.root; do [ -s "$O/stage/$f" ] || { echo "STOP: staged $f missing"; finish 4; }; done
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$L/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin main >> "$L/clone.log" 2>&1 || { echo "STOP: fetch origin main"; finish 3; }
echo "origin/main $(git -C "$D" rev-parse origin/main)"
for J in 0 1 2 3; do
  ms=$(git -C "$D" show "origin/main:$TP/REPLICAS-TIMEOUT-j$J" 2>/dev/null | sha256sum | cut -d' ' -f1)
  ps=$(dd if="$O/REPLICAS-TIMEOUT-j$J" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
  echo "gate: REPLICAS-TIMEOUT-j$J origin/main $ms; pscratch $ps"
  [ "$ms" = "$ps" ] && [ "$ms" != e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 ] || { echo "STOP: REPLICAS-TIMEOUT-j$J is not on main (the completion waits for the merge)"; finish 4; }
done
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
e51367aa3d9d68b8c89f76cd7f556c70bd4a226f 2d-unfolding/ref_c2c1/ref_c2c1_read.py
96dbbaa223a3dec4ceba80686f07721e87ec9045 2d-unfolding/ref_c2c1/config.json
0d2f1a2445fe22130be94635cabb280837be4edb 2d-unfolding/ref_c2c1/test_ref_c2c1.py
0e80efd2d927390e4360cf10134e5b74e7554deb 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
f4dbaf1fe57bcf4ab0f128d70c1725aa64ae8d29 2d-unfolding/ref_c2c1/run_tests.sh
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
echo "bound blobs: 8 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
dd if="$LIB" iflag=noatime status=none of="$O/libcheck-completion/libRooUnfold.so" || { echo "STOP: copying the library"; finish 4; }
lsrc=$(dd if="$LIB" iflag=noatime status=none | sha256sum | cut -d' ' -f1); lcopy=$(sha256sum "$O/libcheck-completion/libRooUnfold.so" | cut -d' ' -f1)
echo "libRooUnfold.so: source sha256 (O_NOATIME read) $lsrc; copy $lcopy; config.json $LIB_SHA"
[ "$lsrc" = "$LIB_SHA" ] && [ "$lcopy" = "$LIB_SHA" ] || { echo "STOP: libRooUnfold.so is not the bound library"; finish 4; }
{ echo /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
  echo /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root
  ls -d /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_*/xsec.root
  echo /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root; } > "$L/cov2d-watch-paths.txt"
echo "COV2D inputs listed for the job's stat: $(wc -l < "$L/cov2d-watch-paths.txt")"
cmp -s "$L/cov2d-watch-paths.txt" <(dd if="$O/logs-replicas/cov2d-watch-paths.txt" iflag=noatime status=none) || { echo "STOP: the watch list differs from the replicas' one"; finish 4; }
cat > "$L/lanes-j4.tsv" <<'LANESEOF'
# job	lane	unit (REF-C2C1 step two, the replicas' completion: the 47 c2_replica units without a PASS marker after the four TIMEOUT jobs, REPLICAS-TIMEOUT-j0..3; round-robin over 4 lanes, all c2 at about 178 s)
4	0	c2_replica:108
4	1	c2_replica:120
4	2	c2_replica:124
4	3	c2_replica:128
4	0	c2_replica:132
4	1	c2_replica:136
4	2	c2_replica:140
4	3	c2_replica:144
4	0	c2_replica:148
4	1	c2_replica:152
4	2	c2_replica:156
4	3	c2_replica:160
4	0	c2_replica:164
4	1	c2_replica:168
4	2	c2_replica:172
4	3	c2_replica:176
4	0	c2_replica:180
4	1	c2_replica:184
4	2	c2_replica:188
4	3	c2_replica:192
4	0	c2_replica:196
4	1	c2_replica:200
4	2	c2_replica:204
4	3	c2_replica:208
4	0	c2_replica:212
4	1	c2_replica:216
4	2	c2_replica:220
4	3	c2_replica:224
4	0	c2_replica:228
4	1	c2_replica:232
4	2	c2_replica:236
4	3	c2_replica:240
4	0	c2_replica:244
4	1	c2_replica:248
4	2	c2_replica:252
4	3	c2_replica:256
4	0	c2_replica:260
4	1	c2_replica:264
4	2	c2_replica:268
4	3	c2_replica:272
4	0	c2_replica:276
4	1	c2_replica:280
4	2	c2_replica:284
4	3	c2_replica:288
4	0	c2_replica:292
4	1	c2_replica:296
4	2	c2_replica:300
LANESEOF
lt=$(sha256sum "$L/lanes-j4.tsv" | cut -d' ' -f1); echo "lanes-j4.tsv sha256 $lt; units $(grep -vc '^#' "$L/lanes-j4.tsv")"
[ "$lt" = "$LANES4_SHA" ] || { echo "STOP: lanes-j4.tsv is not the reviewed one"; finish 9; }
"$PY" -B -I - "$O" "$L" "$LANES_SHA" <<'PYEOF'
import hashlib, json, os, sys
O, L, lanes_sha = sys.argv[1:4]
def rd(p):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f: return f.read()
def table(b):
    return [ln.split("\t")[2].replace(":", "_b") for ln in b.decode().splitlines() if ln.strip() and not ln.startswith("#")]
lanes = rd(os.path.join(O, "logs-replicas", "lanes.tsv"))
if hashlib.sha256(lanes).hexdigest() != lanes_sha: print("STOP: lanes.tsv is not the reviewed one"); sys.exit(4)
declared = table(lanes)
sets = [set(json.loads(rd(os.path.join(O, f"REPLICAS-TIMEOUT-j{j}")))["pass_units"]) for j in range(4)]
union = set().union(*sets)
j4 = table(rd(os.path.join(L, "lanes-j4.tsv")))
present = set(os.listdir(os.path.join(O, "units")))
notpass = [u for u in sorted(union) if json.loads(rd(os.path.join(O, "units", u + ".done"))).get("verdict") != "PASS"]
started = [u for u in j4 if any(f == u or f.startswith(u + ".") for f in present)]
print(f"gate: declared {len(declared)} ({len(set(declared))} distinct); TIMEOUT PASS sets {[len(s) for s in sets]}, "
      f"disjoint {sum(map(len, sets)) == len(union)}, union {len(union)}, not PASS {notpass}; "
      f"lanes-j4 {len(j4)} ({len(set(j4))} distinct), equal to declared minus union {set(j4) == set(declared) - union}, "
      f"with files under units/ {started}")
ok = (len(declared) == len(set(declared)) == 350 and sum(map(len, sets)) == len(union) and union <= set(declared)
      and not notpass and len(j4) == len(set(j4)) and set(j4) == set(declared) - union and not started)
sys.exit(0 if ok else 4)
PYEOF
[ $? -eq 0 ] || { echo "STOP: the completion's unit set is not the 350 minus the TIMEOUT PASS sets"; finish 4; }
pmax=$(scontrol show partition "$PART" | sed -n 's/.*MaxMemPerNode=\([0-9][0-9]*\).*/\1/p' | head -1)
pcpu=$(sinfo -h -p "$PART" -o '%c' | sort -n | head -1)
echo "fit: $NL steps x $MEM_MB MB = $((NL * MEM_MB)) MB vs $PART MaxMemPerNode=$pmax; $NL x 64 CPUs = $((NL * 64)) vs CPUs per node $pcpu"
for v in "$pmax" "$pcpu"; do case "$v" in ''|*[!0-9]*) echo "STOP: the partition's limits are not readable"; finish 9;; esac; done
[ $((NL * MEM_MB)) -le "$pmax" ] && [ $((NL * 64)) -le "$pcpu" ] || { echo "STOP: the steps do not fit the node's allocatable resources"; finish 9; }
echo "== price: 1 x $TLIMIT on 1 node = at most $PRICE node-h; spent $SPENT; cap $CAP"
awk -v p=$PRICE -v s=$SPENT -v c=$CAP 'BEGIN{exit !(p + s <= c)}' || { echo "STOP: the projection is over the cap"; finish 9; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
cat > "$O/refc2c1_completion_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 2: the replicas' completion, one single-node job (REF-C2C1-BINDING-2.md
# ruling 2.2; the director's ruling of 2026-11-06 on the four TIMEOUT jobs: INVALID, the 303 PASS units stand, one
# completion job for the 47 missing c2_replica units; code at M = 77d76cfc from the fresh clean clone, with -B). As the
# replicas job (4f38fc64) with these changes: the job index is 4 and its lanes come from lanes-j4.tsv; each step is
# `srun --exclusive -n1 -c 64 --mem=$MEM`, MEM=112G; THE FIT: before any srun, NL x MEM must be within the job's
# allocated memory (AllocTRES mem, and SLURM_MEM_PER_NODE when set) and NL x 64 within its allocated CPUs (AllocTRES cpu,
# and SLURM_CPUS_ON_NODE), else it refuses (rc 2); THE CONCURRENCY CHECK: 90 s after the
# launches, every lane step <job>.0..NL-1 must read State=RUNNING in `scontrol -o show step <job>` (attempt 2: attempt
# 1's `squeue -s` lists no srun steps on Perlmutter and fired on a correct run; `sstat -a` is recorded as a cross-check
# only), else it records a STOP, cancels its steps and fails; and
# REPLICAS-DONE-j4 adds "unit_list", the sorted unit names, which the 3b read gate unions. Everything else unchanged:
# OMP/MKL/OPENBLAS = 64/1/1 (NUMEXPR 1), each unit refusing (rc 4) unless its affinity is exactly 64 and those match
# config.json e_r; the fence a recorded line; the 303 COV2D inputs stat'd (no read) before and after, a moved atime a
# STOP; porcelain --ignored before and after. Writes only under <O>. Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"; J=4
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
NL=4; MEM=112G; MEM_MB=114688
U="$O/units"; L="$O/logs-completion"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1r$J] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1r$J] refusing: deploy HEAD is not M"; exit 2; }
[ -s "$L/lanes-j4.tsv" ] && [ -s "$L/cov2d-watch-paths.txt" ] && [ -d "$U" ] || { echo "[c2c1r$J] refusing: lanes, watch list or units missing"; exit 2; }
[ ! -e "$O/REPLICAS-DONE-j$J" ] || { echo "[c2c1r$J] refusing: REPLICAS-DONE-j$J exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1r$J] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1r$J] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
amem=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=[^ ]*mem=\([0-9][0-9]*\)M.*/\1/p' | head -1)
acpu=$(scontrol show job "$SLURM_JOB_ID" | sed -n 's/.*AllocTRES=cpu=\([0-9][0-9]*\).*/\1/p' | head -1)
echo "[c2c1r$J] fit: $NL steps x $MEM_MB MB = $((NL * MEM_MB)) MB within SLURM_MEM_PER_NODE=$SLURM_MEM_PER_NODE and AllocTRES mem=$amem;" \
     "$NL x 64 CPUs = $((NL * 64)) within SLURM_CPUS_ON_NODE=$SLURM_CPUS_ON_NODE and AllocTRES cpu=$acpu"
for v in "${SLURM_MEM_PER_NODE:-$amem}" "${SLURM_CPUS_ON_NODE:-$acpu}" "$amem" "$acpu"; do case "$v" in ''|*[!0-9]*) echo "[c2c1r$J] refusing: the allocation is not readable"; exit 2;; esac; done
[ $((NL * MEM_MB)) -le "${SLURM_MEM_PER_NODE:-$amem}" ] && [ $((NL * MEM_MB)) -le "$amem" ] && [ $((NL * 64)) -le "${SLURM_CPUS_ON_NODE:-$acpu}" ] && [ $((NL * 64)) -le "$acpu" ] || { echo "[c2c1r$J] refusing: the steps do not fit the allocation"; exit 2; }
echo "[c2c1r$J] fence, recorded (the director's ruling: guarded readers record, not refuse): squeue -u josephrb:"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed "s/^/[c2c1r$J]   /"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-before.txt" 2>&1
echo "[c2c1r$J] COV2D inputs stat'd before: $(wc -l < "$L/j$J-watch-before.txt")"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[c2c1r$J] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp-replicas-j$J" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR"
echo "[c2c1r$J] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
# >>> lane-step guard
# Reads `scontrol -o show step <job>` on stdin; prints how many of the steps <job>.<i>, for the indices given, read
# State=RUNNING. Each step is counted once; batch, extern and other indices are ignored.
running_lane_steps() {
  awk -v job="$1" -v want="${*:2}" '
    BEGIN { n = split(want, w, " "); for (i = 1; i <= n; i++) W[job "." w[i]] = 1 }
    { sid = ""; st = ""
      for (i = 1; i <= NF; i++) { if ($i ~ /^StepId=/) sid = substr($i, 8); else if ($i ~ /^State=/) st = substr($i, 7) }
      if ((sid in W) && st == "RUNNING") { c++; delete W[sid] } }
    END { print c + 0 }'
}
# <<< lane-step guard
cd "$C" || exit 2
pids=""; n=0
for l in $(seq 0 $((NL - 1))); do
  args=(); while IFS=$'\t' read -r jj ll u; do [ "$jj" = "$J" ] && [ "$ll" = "$l" ] && args+=(--unit "$u"); done < <(grep -v '^#' "$L/lanes-j4.tsv")
  n=$((n + ${#args[@]} / 2))
  echo "[c2c1r$J] lane $l: $(( ${#args[@]} / 2 )) units"
  srun --exclusive -n1 -c 64 --mem=$MEM --job-name="r$J-l$l" \
      /usr/bin/time -v -o "$L/j$J-lane$l.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py "${args[@]}" --out "$U" \
      > "$L/j$J-lane$l.log" 2>&1 &
  pids="$pids $!"
done
sleep 90
scontrol -o show step "$SLURM_JOB_ID" > "$L/j$J-steps-at-90s.txt" 2>&1
running=$(running_lane_steps "$SLURM_JOB_ID" $(seq 0 $((NL - 1))) < "$L/j$J-steps-at-90s.txt")
echo "[c2c1r$J] concurrency: $running of $NL lane steps RUNNING at +90 s ($(date -u +%FT%TZ)), from scontrol show step:"
awk '{ for (i = 1; i <= NF; i++) if ($i ~ /^(StepId|State|Name)=/) printf "%s ", $i; print "" }' "$L/j$J-steps-at-90s.txt" | sed "s/^/[c2c1r$J]   /"
echo "[c2c1r$J] cross-check (recorded, not gating): sstat -a lists $(sstat -n -P -a -j "$SLURM_JOB_ID" -o JobID 2>/dev/null | grep -cE "^$SLURM_JOB_ID\.[0-9]+$") numbered steps"
conc=1
if [ "$running" -ne "$NL" ]; then
  conc=0; echo "[c2c1r$J] STOP: not every lane step is RUNNING; cancelling the steps"
  for p in $pids; do kill "$p" 2>/dev/null; done
fi
rcs=""; for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1r$J] lanes done $(date -u +%FT%TZ); rcs:$rcs"
for l in $(seq 0 $((NL - 1))); do
  echo "[c2c1r$J] lane $l: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/j$J-lane$l.time" | tr -s ' \t' ' ' | tr '\n' ';')"
done
pass=0; names=""; for u in $(grep -v '^#' "$L/lanes-j4.tsv" | awk -F'\t' -v j="$J" '$1 == j {print $3}'); do
  name=$(echo "$u" | sed 's/:\(.*\)/_b\1/'); names="$names $name"; grep -q '"verdict": "PASS"' "$U/$name.done" 2>/dev/null && pass=$((pass + 1))
done
echo "[c2c1r$J] PASS markers: $pass of $n"
xargs -d '\n' stat -c '%X %n' < "$L/cov2d-watch-paths.txt" > "$L/j$J-watch-after.txt" 2>&1
if cmp -s "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt"; then moved=0; echo "[c2c1r$J] COV2D inputs: no atime moved"
else moved=1; echo "[c2c1r$J] STOP: a COV2D input's atime moved:"; diff "$L/j$J-watch-before.txt" "$L/j$J-watch-after.txt" | head -20; fi
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1r$J] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
list=$(printf '%s\n' $names | sort | sed 's/.*/"&"/' | paste -sd, - | sed 's/,/, /g')
printf '{"job": "%s", "index": %s, "units": %s, "pass_markers": %s, "rcs": "%s", "watch_moved": %s, "porcelain_after": %s, "concurrent": %s, "unit_list": [%s]}\n' \
    "$SLURM_JOB_ID" "$J" "$n" "$pass" "${rcs# }" "$moved" "$na" "$conc" "$list" > "$O/REPLICAS-DONE-j$J"
cat "$O/REPLICAS-DONE-j$J"
[ "$pass" = "$n" ] && [ "$moved" = 0 ] && [ "$na" = 0 ] && [ "$conc" = 1 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
JOBEOF
j=$(sha256sum "$O/refc2c1_completion_job.sbatch" | cut -d' ' -f1); echo "refc2c1_completion_job.sbatch sha256 $j"
[ "$j" = "$JOB_SHA" ] || { echo "STOP: the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_c2c1r --output="$L/%x_%j.out" "$O/refc2c1_completion_job.sbatch" "$D" "$O" > "$L/submit-j4.out" 2>&1
rc=$?; echo "sbatch j4 rc=$rc: $(cat "$L/submit-j4.out")"
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$L/submit-j4.out")
[ $rc = 0 ] && [ -n "$job" ] || { echo "STOP at sbatch j4"; finish 9; }
echo "4 $job" > "$L/jobs.tsv"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
pt=$(scontrol show job "$job" | sed -n 's/.*Partition=\([^ ]*\).*/\1/p' | head -1)
echo "j4 job $job scontrol TimeLimit=$tl (declared $TLIMIT); Partition=$pt (fit checked against $PART)"
if [ "$tl" != "$TLIMIT" ] || [ "$pt" != "$PART" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl or Partition $pt is not the declared one; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a %P"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after submission: $n"
finish 0
