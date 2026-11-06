#!/bin/bash
# 1B binding 3, stage 3 (A2.1 §11; amendment 2 §12 item 1): one connect, on a login node, each step gated on the one
# before: the m3246 balance against what binding 3 has left at caps; a fresh clone at M in a new pscratch directory;
# every bound blob, the five gate files at the gate's blobs among them (the director's ruling on the auditor's P1,
# 2026-11-06: M is a commit on the binding-3 branch carrying the gate pin, never a merge with main); the guard's
# real-O_NOATIME test on this login node (§11's residual); the stat-before over every file under the guard's declared
# roots and i2's products; the bound generator's tables at --plugin no; then the receipt job's submission (amendment 2
# §4's line, 1 node, 2:00:00). The receipt's readout is connect-receipt-readout.sh, a separate step after the job.
# Argument 1: M, the full sha of the binding-3 commit with the gate pin. W is new (the generator fixes the receipt's
# path, $P/fd-1b-staged-20261102/stage1/a2/receipt.json, so W is that a2 directory). Writes only under $W. Nothing to
# CFS. Not under set -u (the root_6_28 activation aborts under it).
# v2 (the director, 2026-11-06, on job 60889950, INVALID: its step asked --mem=480G, 491520M, over the allocation's
# 487802M, and never started): the step is 448G; before the submission every srun step's CPUs and memory, from the
# table's lines and the launcher's per-step arguments, must fit the partition's node (sinfo CPUs, MaxMemPerNode);
# after it, the job's ReqTRES memory and Partition are checked, with scancel on a miss. W = a2 is the generator's, so
# the INVALID a2 of 60889950 is first moved to a2-invalid-60889950, only if it holds no receipt.json, its readout.log
# records INVALID for 60889950, and sacct has that job ended.
# Run in the foreground over ssh (a refusal before the log exists prints only to stdout): bash connect-receipt.sh M
set -o pipefail
M=$1
case "$M" in *[!0-9a-f]*|"") echo "STOP M is not a lowercase sha: '$M'"; exit 2 ;; esac
[ ${#M} = 40 ] || { echo "STOP M is not 40 hex: '$M'"; exit 2; }
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102/stage1/a2; DD=$W/deploy; V=$P/fd-1b-inv-20261101
BR=decl/1b-staged-a2-1-20261103
B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/b3
GEN=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py
PIN=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/BOUND_GATE.sha256
GATE_SHA=6a832bf0692864aefb5f7e97e22f3c8025d87679561463358550dc12b090b062   # stage 2's merged record (b3/merge-run)
FSHA=cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5       # stage1/in/flux_universes.npz
CAP_NODE_H=53.5                                     # binding 3's stages 3-6 at caps: 2.0 + 2.0 + 1.5 + 48.0
PART=regular_milan_ss11                             # where -q regular -C cpu lands (60880988, 60889950)
CPT=256; MEM=448G; FIRST=0; LAST=0                  # the launcher's per-step -c and --mem, and the table's lines
OLDJ=60889950; OLD=$W-invalid-$OLDJ                 # the INVALID receipt job (b3/receipt-run-60889950)
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
mib() { [[ "$1" =~ ^([1-9][0-9]*)([MGT])$ ]] || return 0              # integer M/G/T to MiB; anything else, nothing
        case "${BASH_REMATCH[2]}" in M) echo "${BASH_REMATCH[1]}" ;; G) echo $(( BASH_REMATCH[1] * 1024 )) ;;
                                     T) echo $(( BASH_REMATCH[1] * 1048576 )) ;; esac; }
moved=""
if [ -e "$W" ]; then
  [ -e "$OLD" ] && { echo "STOP $W and $OLD both exist"; exit 2; }
  [ -e "$W/receipt.json" ] && { echo "STOP $W holds a receipt.json"; exit 2; }
  grep -qE "^host=[^ ]+ start=[^ ]+ job=$OLDJ$" "$W/logs/readout.log" 2>/dev/null \
    && grep -q "^RECEIPT-READOUT verdict=INVALID why=no receipt.json" "$W/logs/readout.log" \
    || { echo "STOP $W exists and its readout.log does not record job $OLDJ INVALID"; exit 2; }
  ost=$(sacct -j "$OLDJ" -X -n -P -o State | head -1)
  case "$ost" in PENDING|RUNNING|REQUEUED|SUSPENDED|CONFIGURING|COMPLETING|"") echo "STOP job $OLDJ is '$ost'"; exit 2 ;; esac
  mv "$W" "$OLD" || { echo "STOP mv $W $OLD"; exit 2; }
  moved="moved the INVALID $W (job $OLDJ, sacct '$ost', no receipt.json, readout INVALID) to $OLD"
fi
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-receipt.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ M=$M"
[ -n "$moved" ] && echo "$moved"
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
# The COV2D fence covers plain readers of COV2D inputs; every 1B read is O_NOATIME under the guard, so the queue at
# launch, cov2d jobs included, is recorded, not refused (the director, 2026-11-06).
echo "squeue at launch: [$(squeue --me -h -o "%i %j %T" | tr '\n' ';')]"

# 1. The balance: stop if binding 3's remaining cap is above half of what m3246 has left.
echo "== iris"; iris 2>&1 | head -2; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP_NODE_H"
awk -v b=$bal -v c=$CAP_NODE_H 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP_NODE_H is above half the balance $bal: to Joseph"

# 2. The deploy: a fresh clone detached at M, clean, on the binding-3 branch, carrying the gate pin.
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
git -C "$DD" merge-base --is-ancestor "$M" "origin/$BR" || stop "M is not on origin/$BR"
echo "M on origin/$BR (tip $(git -C "$DD" rev-parse "origin/$BR"))"
cmp -s "$0" "$DD/$B/connect-receipt.sh" || stop "this script is not M's $B/connect-receipt.sh"
got=$(cat "$DD/$PIN"); echo "gate pin: $got"
[ "$got" = "$GATE_SHA" ] || stop "M's gate pin is not stage 2's merged record"
cat > "$W/bound.sha256" <<SUMS
522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f  nd-unfolding/fd_1b_c2.py
062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67  nd-unfolding/fd_1b_mc.py
0d852a6992398b6b1ba7956b2e8d74accc2b6f1aa7b7909a6ef7d6d7f0dcd756  2d-unfolding/cov2d/cov2d.py
b95c562916091b910a5ca8d874d83296035690cb8784db3d318b2f07fed28182  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip/clip_probe2.py
869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08  nd-unfolding/fd_1b_toys.py
ee20534c20504aa1335bad4e75be067c0465c7faaa60d2a14a47abb81e22f60c  nd-unfolding/fd_1b_noatime_guard.py
f6edf4b0116d2ef0058bb790ddc94c1d678ce8d5b798825069f7b343c03bab31  nd-unfolding/fd_1b_cal300_pins.json
84a6750bdf9b6c04872968c39a8785b497beb1b8404ebb33a35d490c7255d47e  $B/guard_scan.py
9c7f1541777bd8bb5a62bd96f747b5431e295ff18e732a1b4cb9f09cd6c850a8  $GEN
fbcb786923cabd8ab9177525a4b95afaec60486b2a0670ca598d048ebe835a7c  nd-unfolding/fd_f1_lane.py
dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f  nd-unfolding/s5c_array.sh
30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b  nd-unfolding/mnv_guarded_run.py
b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3  docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"

# 3. The environment the jobs use, then the guard's tests here, its real-O_NOATIME test among them (Linux only).
source "$DD/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
(cd "$DD/nd-unfolding/tests" && nice -n 19 python3 -B -m unittest -b test_fd_1b_guard) > "$W/logs/test-guard.out" 2>&1
rc=$?; tail -3 "$W/logs/test-guard.out"; [ "$rc" = "0" ] || stop "the guard's tests rc=$rc"
(cd "$DD/nd-unfolding/tests" && python3 -B -m unittest -v test_fd_1b_guard.RealFlag) > "$W/logs/test-realflag.out" 2>&1
rc=$?; cat "$W/logs/test-realflag.out"
[ "$rc" = "0" ] && grep -q "^Ran 1 test" "$W/logs/test-realflag.out" && [ "$(tail -1 "$W/logs/test-realflag.out")" = "OK" ] \
  || stop "the real-O_NOATIME test did not run and pass (rc=$rc)"

# 4. The stat-before, written before the first read of an input: every file under the guard's declared roots (the
#    deploy's ROOTS) and every file of i2's products, which S1-0's controls compare with.
python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import fd_1b_noatime_guard as g; print("\n".join(g.ROOTS))' \
  "$DD/nd-unfolding" > "$W/logs/roots.txt" || stop "the guard's roots"
while read -r r; do [ -e "$r" ] || stop "a declared root is missing: $r"; done < "$W/logs/roots.txt"
[ -d "$V/i2/unf" ] || stop "$V/i2/unf is missing"
{ xargs -a "$W/logs/roots.txt" -I{} find {} -type f; find "$V/i2/unf" -type f; } | LC_ALL=C sort -u > "$W/logs/sources.txt" \
  || stop "the source list"
echo "roots=$(wc -l < "$W/logs/roots.txt") sources=$(wc -l < "$W/logs/sources.txt") i2_unf=$(find "$V/i2/unf" -type f | wc -l)"
xargs -a "$W/logs/sources.txt" -d '\n' stat -c '%X %Y %s %n' > "$W/logs/stat-before.txt" || stop "a source is missing"
echo "stat-before lines=$(wc -l < "$W/logs/stat-before.txt") at $(date -u +%FT%TZ)"

# 5. The bound generator's tables at --plugin no (no clip seed yet: the receipt and S1-0's only), and the guard scan
#    over this directory's scripts and those rows.
mkdir "$W/tables" || stop "mkdir tables"
python3 -B "$DD/$GEN" "$DD" "$W/tables" --plugin no --flux-table-sha256 "$FSHA" --estimator R > "$W/logs/tables.out" 2>&1 \
  || { cat "$W/logs/tables.out"; stop tables; }
cat "$W/logs/tables.out"
(cd "$W/tables" && sha256sum *.tsv > SHA256SUMS && cat SHA256SUMS)
[ "$(grep -vc '^#' "$W/tables/receipt-steps.tsv")" = "1" ] && [ "$(grep -vc '^#' "$W/tables/tasks-receipt.tsv")" = "1" ] \
  || stop "the receipt is not one step of one lane"
[ "$(grep -vc '^#' "$W/tables/s1-0-steps.tsv")" = "8" ] || stop "S1-0 is not 8 lanes"
for x in s1-0b-steps.tsv s1-bulk-steps.tsv; do [ -e "$W/tables/$x" ] && stop "$x was made before its inputs"; done
python3 -B "$DD/$B/guard_scan.py" "$W/tables" > "$W/logs/guard-scan.out" 2>&1; rc=$?; cat "$W/logs/guard-scan.out"
[ "$rc" = "0" ] || stop "guard_scan rc=$rc"
cut -f1-6 "$W/tables/receipt-steps.tsv"

# 6. The steps fit the node, before anything queues: sbatch_timing_packed.sh runs lines FIRST..LAST of the table at
#    once, each as `srun --exact -c $CPT --mem=$MEM`, so their sums must fit one node of $PART.
rows=$(grep -vc '^#' "$W/tables/tasks-receipt.tsv"); nst=$(( LAST - FIRST + 1 ))
[ "$FIRST" -ge 0 ] && [ "$nst" -ge 1 ] && [ "$LAST" -lt "$rows" ] || stop "lines $FIRST..$LAST are not in the table's $rows"
ncpu=$(sinfo -p "$PART" -h -o %c | sort -u); maxmem=$(scontrol show partition "$PART" | grep -oE 'MaxMemPerNode=[0-9]+')
maxmem=${maxmem#MaxMemPerNode=}; stepmib=$(mib "$MEM")
case "$ncpu" in *[!0-9]*|"") stop "the node CPUs of $PART are not one number: '$ncpu'" ;; esac
case "$maxmem" in *[!0-9]*|"") stop "MaxMemPerNode of $PART is not a number: '$maxmem'" ;; esac
[ -n "$stepmib" ] || stop "the step memory $MEM is not an integer M/G/T"
echo "steps=$nst cpus=$nst*$CPT=$(( nst * CPT )) of $ncpu; mem=$nst*${stepmib}M=$(( nst * stepmib ))M of ${maxmem}M ($PART)"
[ $(( nst * CPT )) -le "$ncpu" ] || stop "the steps' CPUs exceed the node's"
[ $(( nst * stepmib )) -le "$maxmem" ] || stop "the steps' memory exceeds MaxMemPerNode"

# 7. The receipt job (amendment 2 §4's line): one exclusive node, line 0 of the table, 256 CPUs and 448G.
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -t 02:00:00 -J fd1b_mc_receipt_a2 -o "$W/logs/%x_%j.out" \
  "$DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
  "$DD" "$M" "$W/tables/tasks-receipt.tsv" "$W/lanes" "$CPT" "$MEM" "$FIRST" "$LAST" inherit) || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=02:00:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 02:00:00: cancelled $jid"; }
pt=$(scontrol show job "$jid" | grep -oE "(^| )Partition=[^ ]*" | head -1); pt=${pt# }
rq=$(scontrol show job "$jid" | grep -oE "ReqTRES=[^ ]*" | head -1)
rqm=$(echo "$rq" | grep -oE "mem=[^,]*"); rqmib=$(mib "${rqm#mem=}"); echo "$pt $rq"
[ "$pt" = "Partition=$PART" ] || { scancel "$jid"; stop "the job is in '${pt#Partition=}', not $PART: cancelled $jid"; }
[ -n "$rqmib" ] && [ $(( nst * stepmib )) -le "$rqmib" ] \
  || { scancel "$jid"; stop "the steps' $(( nst * stepmib ))M do not fit the job's ${rqm:-no mem}: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_mc_receipt || true
echo "end=$(date -u +%FT%TZ)"
