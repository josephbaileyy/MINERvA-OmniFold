#!/bin/bash
# 1B binding 3, stage 3 (A2.1 §11; amendment 2 §12 item 1): one connect, on a login node, each step gated on the one
# before: the m3246 balance against what binding 3 has left at caps; a fresh clone at M3 in a new pscratch directory;
# every bound blob, the five gate files at the gate's blobs among them (the director's ruling on the auditor's P1,
# 2026-11-06: M3 is a commit on the binding-3 branch carrying the gate pin, never a merge with main); the guard's
# real-O_NOATIME test on this login node (§11's residual); the stat-before over every file under the guard's declared
# roots and i2's products; the bound generator's tables at --plugin no; then the receipt job's submission (amendment 2
# §4's line, 1 node, 2:00:00). The receipt's readout is connect-receipt-readout.sh, a separate step after the job.
# Argument 1: M3, the full sha of the binding-3 commit with the gate pin. W is new (the generator fixes the receipt's
# path, $P/fd-1b-staged-20261102/stage1/a2/receipt.json, so W is that a2 directory). Writes only under $W. Nothing to
# CFS. Not under set -u (the root_6_28 activation aborts under it).
# Run detached: setsid nohup bash connect-receipt.sh M3 >/dev/null 2>&1 </dev/null &
set -o pipefail
M3=$1
case "$M3" in *[!0-9a-f]*|"") echo "STOP M3 is not a lowercase sha: '$M3'"; exit 2 ;; esac
[ ${#M3} = 40 ] || { echo "STOP M3 is not 40 hex: '$M3'"; exit 2; }
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102/stage1/a2; DD=$W/deploy; V=$P/fd-1b-inv-20261101
BR=decl/1b-staged-a2-1-20261103
B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/b3
GEN=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py
PIN=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/BOUND_GATE.sha256
GATE_SHA=6a832bf0692864aefb5f7e97e22f3c8025d87679561463358550dc12b090b062   # stage 2's merged record (b3/merge-run)
FSHA=cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5       # stage1/in/flux_universes.npz
CAP_NODE_H=53.5                                     # binding 3's stages 3-6 at caps: 2.0 + 2.0 + 1.5 + 48.0
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-receipt.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ M3=$M3"
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

# 2. The deploy: a fresh clone detached at M3, clean, on the binding-3 branch, carrying the gate pin.
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M3" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M3" ] || stop "deploy not clean at M3"
git -C "$DD" merge-base --is-ancestor "$M3" "origin/$BR" || stop "M3 is not on origin/$BR"
echo "M3 on origin/$BR (tip $(git -C "$DD" rev-parse "origin/$BR"))"
cmp -s "$0" "$DD/$B/connect-receipt.sh" || stop "this script is not M3's $B/connect-receipt.sh"
got=$(cat "$DD/$PIN"); echo "gate pin: $got"
[ "$got" = "$GATE_SHA" ] || stop "M3's gate pin is not stage 2's merged record"
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

# 6. The receipt job (amendment 2 §4's line): one exclusive node, 256 CPUs, 480G, line 0 of the table.
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
jid=$(sbatch --parsable -A m3246 -q regular -C cpu -t 02:00:00 -J fd1b_mc_receipt_a2 -o "$W/logs/%x_%j.out" \
  "$DD/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
  "$DD" "$M3" "$W/tables/tasks-receipt.tsv" "$W/lanes" 256 480G 0 0 inherit) || stop sbatch
jid=${jid%%;*}; echo "Submitted batch job $jid"
tl=$(scontrol show job "$jid" | grep -oE "TimeLimit=[^ ]*"); echo "$tl"
[ "$tl" = "TimeLimit=02:00:00" ] || { scancel "$jid"; stop "the time limit parsed as ${tl#TimeLimit=}, not 02:00:00: cancelled $jid"; }
scontrol show job "$jid" | grep -oE "(JobName|JobState|TimeLimit|Partition|QOS|NumNodes|Account|OverSubscribe)=[^ ]*" | tr '\n' ' '; echo
squeue --me -o "%i %j %T %M %l %R" | grep fd1b_mc_receipt || true
echo "end=$(date -u +%FT%TZ)"
