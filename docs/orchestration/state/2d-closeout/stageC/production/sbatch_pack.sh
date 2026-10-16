#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/logs/%x_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/logs/%x_%j.err
# Stage C production pack dispatcher (AUTHORIZATION-20261016-2d-closeout-stageC-regular-packing.md §4; DESIGN §14).
# One regular-QOS node runs up to NODE_CPUS/cpus jobs.tsv rows ("members") of one class (cpus, mem, cap) side by
# side, each as its own `srun --exact` step running sbatch_prod.sh --member <name>. Submitted only by launch.py,
# which passes the member names as arguments and records them in $NS/packs/<job name>.members before sbatch.
# Refuses before any step starts unless: every member is exactly one jobs.tsv row, no member repeats, the members
# share one class, they fit the node (count and summed memory <= RealMemory 515100 MB), the arguments equal the
# launcher's record, and the allocation is QOS regular, 256 CPUs, billing 256, TimeLimit = the members' cap (or
# their common retry record). One member failing never stops the others; each member's rc is appended to
# $NS/packs/<job id>.status as it ends, and the step states are appended at the end. Every path is absolute: sbatch
# runs a COPY of this script. No `set -u` before anything that may source the root_6_28 activation.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015
REPO=$NS/repo_k
PKG=$REPO/docs/orchestration/state/2d-closeout/stageC/production
JOBS_SHA=c4f1b7082fac3635be78622cb9b9a5f71103789337bbc29e7dd29684e9b4d3a4    # jobs.tsv (unchanged by packing)
MEMBER_SHA=885dd7f28191a1e51b411358eaeef55a3db037b17fbd526aa9d8410f6c64a73d                                                    # sbatch_prod.sh (the member runner)
PACK_QOS=regular; NODE_CPUS=256; NODE_MEM_MB=515100; PACK_BILLING=256
JID=${SLURM_JOB_ID:?not a Slurm job}
PNAME=${SLURM_JOB_NAME:?no job name}   # the PACK's name only; a member's identity comes from its argument
refuse() { echo "REFUSE: $*"; exit 4; }

echo "$JOBS_SHA  $PKG/jobs.tsv" | sha256sum -c -
echo "$MEMBER_SHA  $PKG/sbatch_prod.sh" | sha256sum -c -
[ "$#" -ge 1 ] || refuse "no members"
# ---- identity: each argument is exactly one jobs.tsv row, none repeats ----------------------------------------------
[ "$(printf '%s\n' "$@" | sort | uniq -d | grep -c .)" = 0 ] || refuse "a member repeats: $*"
CLASS=""; MEMSUM=0
for M in "$@"; do
  ROW=$(awk -F'\t' -v n="$M" 'NR>1 && $1==n' "$PKG/jobs.tsv")
  [ "$(printf '%s\n' "$ROW" | grep -c .)" = 1 ] || refuse "member '$M' is not exactly one jobs.tsv row"
  IFS=$'\t' read -r R_NAME R_ITEM R_BATCH R_QOS R_CPUS R_MEM R_TIME R_BILL R_ENF R_AFTER R_WHAT <<< "$ROW"
  WANT_TIME=$R_TIME; [ -f "$NS/retries/$M.time" ] && WANT_TIME=$(cat "$NS/retries/$M.time")
  C="$R_CPUS $R_MEM $WANT_TIME"
  [ -z "$CLASS" ] || [ "$C" = "$CLASS" ] || refuse "members differ in class: '$C' vs '$CLASS'"
  CLASS=$C
  MEMSUM=$((MEMSUM + ${R_MEM%M}))
done
read -r CPUS MEM TIME <<< "$CLASS"
[ "$#" -le $((NODE_CPUS / CPUS)) ] || refuse "$# members of $CPUS CPUs exceed one $NODE_CPUS-CPU node"
[ "$MEMSUM" -le "$NODE_MEM_MB" ] || refuse "summed member memory ${MEMSUM}M exceeds RealMemory ${NODE_MEM_MB}M"
# ---- the launcher's record --------------------------------------------------------------------------------------------
REC=$NS/packs/$PNAME.members
[ -f "$REC" ] || refuse "no launcher record $REC"
[ "$(cut -f3 "$REC")" = "$(IFS=,; echo "$*")" ] || refuse "arguments '$*' differ from $REC"
# ---- the allocation -----------------------------------------------------------------------------------------------------
JOBINFO=$(scontrol show job "$JID")
G_QOS=$(grep -o 'QOS=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_CPUS=$(grep -o 'NumCPUs=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_TIME=$(grep -o 'TimeLimit=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_BILL=$(grep -o 'AllocTRES=[^ ]*' <<< "$JOBINFO" | grep -o 'billing=[0-9]*' | head -1 | cut -d= -f2)
[ "$G_QOS" = "$PACK_QOS" ] || refuse "QOS $G_QOS != $PACK_QOS"
[ "$G_CPUS" = "$NODE_CPUS" ] || refuse "NumCPUs $G_CPUS != $NODE_CPUS"
# The charge gate counts a pack at PACK_BILLING x TimeLimit / 256 (one node); refuse any other billing.
[ "$G_BILL" = "$PACK_BILLING" ] || refuse "allocated billing '$G_BILL' != pack billing $PACK_BILLING"
[ "$G_TIME" = "$TIME" ] || refuse "TimeLimit $G_TIME != the members' cap $TIME"

ST=$NS/packs/$JID.status
echo "[pack] $PNAME job=$JID node=$(hostname) members=$* class=$CLASS start=$(date -u +%FT%TZ)"
printf '#pack\t%s\t%s\t%s\n' "$PNAME" "$(IFS=,; echo "$*")" "$(date -u +%s)" >> "$ST"
pids=()
for M in "$@"; do
  (   # a member's rc is recorded the moment it ends; a failure never touches the other steps
    rc=0
    srun --exact -N1 -n1 -c "$CPUS" --mem="$MEM" --job-name="$M" \
      --output="$NS/logs/${M}_${JID}.out" --error="$NS/logs/${M}_${JID}.err" \
      bash "$PKG/sbatch_prod.sh" --member "$M" || rc=$?
    printf '%s\t%s\t%s\n' "$M" "$rc" "$(date -u +%s)" >> "$ST"
  ) &
  pids+=($!)
done
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
for M in "$@"; do
  rc=$(awk -F'\t' -v m="$M" '$1==m {r=$2} END {print r}' "$ST")
  [ "$rc" = 0 ] || fail=1
done
sleep 5   # let the step records reach the accounting database
sacct -j "$JID" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw | sed 's/^/#step\t/' >> "$ST" || true
echo "[pack] done $PNAME fail=$fail $(date -u +%FT%TZ)"
exit "$fail"
