#!/bin/bash
# REF-C2C1 step two, stage 2 (the units), part 1: the centrals connect (REF-C2C1-BINDING-2.md ruling 2.2; #814 at main
# 410c4868; code at M = 77d76cfc), on a login node, detached, under the binding's fixed conditional sequence:
#   - the gate: stage 1's PASS record is on main: `git show origin/main:<stage.json>` hashes to 559da9e8..., equal to
#     the record the staging wrote on pscratch, and the two staged copies are present;
#   - the COV2D fence (#798): refuses before writing anything if any cov2d-* job is queued or running;
#   - a fresh clean clone at M into $O/deploy-units, porcelain --ignored 0, the binding's 8 blobs;
#   - libRooUnfold.so (config.json inputs.roounfold_lib) copied by an O_NOATIME read into $O/libcheck/ and checked
#     against config.json's full sha256 0b34e1e3...fefd (F2's interim; the units dlopen the configured path itself);
#   - the price: --time=01:00:00 on 1 node is at most 1.0 node-h; with C-DRAW's 0.1789 spent, under the 12.5 cap; the
#     iris half-balance check;
#   - the job script (refc2c1_centrals_job.sbatch) written from this file and refused unless its sha256 is the
#     reviewed one; one sbatch; scontrol's TimeLimit must read 01:00:00, else scancel, rc 6.
# Writes only under $O (deploy-units, libcheck, logs-units, units, tmp-units). No set -u. Launched from a /dev/shm copy
# of itself ($1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
D=$O/deploy-units
L=$O/logs-units
M=77d76cfc2d621f8faa010b75006811868494652a
STAGE_JSON=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/stage/stage.json
STAGE_SHA=559da9e806ccf4a24c70279bd70564ff96074fe6aec2d2df0e9b62370426479d
LIB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
LIB_SHA=0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
TLIMIT=01:00:00
PRICE=1.0
SPENT=0.1789
CAP=12.5
JOB_SHA=de0b6321b6cc36ac2069eaa66d2ecf4d58871b1b13d19fb86c228c15ad259294
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -d "$O/stage" ] && [ -x "$PY" ] || bail
for x in deploy-units libcheck logs-units units tmp-units CENTRALS-DONE; do [ ! -e "$O/$x" ] || bail; done
[ -z "$(squeue --me -h -n fd_c2c1u -o %i)" ] || bail
fence=$(squeue -u josephrb -h -o '%i|%j|%T') || bail                  # the COV2D fence (#798)
printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/ {f=1} END {exit f}' || bail
mkdir -p "$L" "$O/libcheck" || bail
exec > "$L/connect.log" 2>&1
finish() { echo "ref-c2c1 centrals connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refc2c1_centrals_submit.sh"
echo "COV2D fence: no cov2d-* job in squeue at $(date -u +%FT%TZ)"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$L/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin main >> "$L/clone.log" 2>&1 || { echo "STOP: fetch origin main"; finish 3; }
onmain=$(git -C "$D" show "origin/main:$STAGE_JSON" 2>/dev/null | sha256sum | cut -d' ' -f1)
local_stage=$(dd if="$O/logs-stage/stage.json" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "gate: origin/main $(git -C "$D" rev-parse origin/main) stage.json sha256 $onmain; pscratch record $local_stage; expected $STAGE_SHA"
[ "$onmain" = "$STAGE_SHA" ] && [ "$local_stage" = "$STAGE_SHA" ] || { echo "STOP: stage 1's PASS record is not on main (the units wait for the merge)"; finish 4; }
for f in runEventLoopOmniFold_MEFHC.root runEventLoopMC_MEFHC.root; do [ -s "$O/stage/$f" ] || { echo "STOP: staged $f missing"; finish 4; }; done
echo "staged copies present: $(ls "$O/stage" | tr '\n' ' ')"
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
cfglib=$("$PY" -I -c 'import json,sys; c=json.load(open(sys.argv[1]))["inputs"]; print(c["roounfold_lib"], c["roounfold_lib_sha256"])' "$D/2d-unfolding/ref_c2c1/config.json")
echo "config.json roounfold_lib: $cfglib"
[ "$cfglib" = "$LIB $LIB_SHA" ] || { echo "STOP: config.json's library path or sha is not this connect's"; finish 9; }
dd if="$LIB" iflag=noatime status=none of="$O/libcheck/libRooUnfold.so" || { echo "STOP: copying the library"; finish 4; }
lsrc=$(dd if="$LIB" iflag=noatime status=none | sha256sum | cut -d' ' -f1); lcopy=$(sha256sum "$O/libcheck/libRooUnfold.so" | cut -d' ' -f1)
echo "libRooUnfold.so: source sha256 (O_NOATIME read) $lsrc; copy $lcopy; config.json $LIB_SHA; atime $(stat -c %X "$LIB")"
[ "$lsrc" = "$LIB_SHA" ] && [ "$lcopy" = "$LIB_SHA" ] || { echo "STOP: libRooUnfold.so is not the bound library"; finish 4; }
echo "== price: limit $TLIMIT on 1 node = at most $PRICE node-h; spent $SPENT; cap $CAP"
awk -v p=$PRICE -v s=$SPENT -v c=$CAP 'BEGIN{exit !(p + s <= c)}' || { echo "STOP: the projection is over the cap"; finish 9; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
cat > "$O/refc2c1_centrals_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 step two, stage 2 (the units), part 1: the three centrals, timed (REF-C2C1-BINDING-2.md ruling 2.2; code at
# M = 77d76cfc from the fresh clean clone, with -B). er, c2_central and c1_central run concurrently, one srun step each,
# `srun --exclusive -n1 -c 64 --mem=120G`, at OMP/MKL/OPENBLAS = 64/1/1 (NUMEXPR 1, as part B's re2_env.sh): each unit
# refuses (rc 4) unless its affinity is exactly 64 and those three variables match config.json e_r. The units read only
# the staged copies under the staging root (C-IN) and the repository; the c2 units dlopen config.json's libRooUnfold.so,
# whose full sha256 the connect checked. Their seconds price the replicas (part 2), which are submitted only if the
# projection is within the 12.5 cap. Porcelain, with --ignored, before and after. Writes only under <O>.
# Arguments: <deploy> <O>. NOT set -u.
set -o pipefail
C="${1:?deploy}"; O="${2:?out}"
M=77d76cfc2d621f8faa010b75006811868494652a
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
U="$O/units"; L="$O/logs-units"
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261106 ] || { echo "[c2c1u] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[c2c1u] refusing: deploy HEAD is not M"; exit 2; }
[ ! -e "$U" ] || { echo "[c2c1u] refusing: $U exists"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1u] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[c2c1u] refusing: the deploy is not clean"; exit 2; }
echo "[c2c1u] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
echo "[c2c1u] squeue cov2d-* at start: $(squeue -u josephrb -h -o '%i|%j|%T' | awk -F'|' '$2 ~ /^cov2d-/' | tr '\n' ' ')"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "[c2c1u] refusing: activation failed"; exit 2; }
export TMPDIR="$O/tmp-units" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" "$U"
echo "[c2c1u] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
cd "$C" || exit 2
pids=""
for u in er c2_central c1_central; do
  srun --exclusive -n1 -c 64 --mem=120G --job-name="$u" \
      /usr/bin/time -v -o "$L/$u.time" "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1.py --unit "$u" --out "$U" \
      > "$L/$u.log" 2>&1 &
  pids="$pids $!"
done
rcs=""
for p in $pids; do wait "$p"; rcs="$rcs $?"; done
echo "[c2c1u] units done $(date -u +%FT%TZ); rcs:$rcs"
for u in er c2_central c1_central; do
  echo "[c2c1u] $u: $(grep -E 'Elapsed|Maximum resident|Exit status' "$L/$u.time" | tr -s ' \t' ' ' | tr '\n' ';')"
  tail -2 "$L/$u.log"
  [ -s "$U/$u.done" ] && echo "[c2c1u] $u.done: $(cat "$U/$u.done")"
done
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[c2c1u] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
pass=0; for u in er c2_central c1_central; do grep -q '"verdict": "PASS"' "$U/$u.done" 2>/dev/null && pass=$((pass + 1)); done
printf '{"job": "%s", "rcs": "%s", "pass_markers": %s, "porcelain_after": %s}\n' "$SLURM_JOB_ID" "${rcs# }" "$pass" "$na" > "$O/CENTRALS-DONE"
cat "$O/CENTRALS-DONE"
[ "$pass" = 3 ] && [ "$na" = 0 ] && [ "$(echo $rcs | tr -d ' 0')" = "" ]
JOBEOF
j=$(sha256sum "$O/refc2c1_centrals_job.sbatch" | cut -d' ' -f1); echo "refc2c1_centrals_job.sbatch sha256 $j"
[ "$j" = "$JOB_SHA" ] || { echo "STOP: the job script is not the reviewed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_c2c1u --output="$L/%x_%j.out" "$O/refc2c1_centrals_job.sbatch" "$D" "$O" > "$L/submit.out" 2>&1
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
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after submission: $n"
finish 0
