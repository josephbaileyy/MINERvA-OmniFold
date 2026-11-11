#!/bin/bash
# RPD-RECO flux connect 1 (revision 2): the login-node half. It prepares and submits ONE Slurm batch job, rpd_flux1,
# which runs #848's fd_rpd_reco_flux_connect.sh at @@S8@@ with the READY config production-config.ready.json
# (sha256 cde8d029..., "20261111" a fixed label naming this config, not the run's date). DRAFT for coverage-5b-audit;
# it runs only on the director's go for its exact sha256, after the director announces the job name rpd_flux1.
# On the login node (light: no input read, no MAT, no ROOT), in order:
#   1. refuses unless on a login node with the literal root /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 absent;
#   2. the fence: any queued or running job of ours named cov2d*, t2a* or rpd* refuses (ruling (a)); LL5D and E96D
#      jobs pass (director, 2026-11-11). The launcher's fence mode runs cov2d_fence.sh first;
#   3. a fresh clone at @@S8@@ into the root, HEAD and porcelain checked, and 11 sha256s;
#   4. the READY config, written from this script and checked against its sha256;
#   5. the overlap fence, tools/fence_overlap.py (rulings (b) and (c)): STOP if either write root overlaps any of
#      cov2d's 30 protected paths, or if any original prepare stages overlaps one, except exactly
#      /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt,
#      which custody prepare stages once: one stat-bracketed staging, with two O_NOATIME reads (noatime_digest,
#      then stage_copy), its stat_before and stat_after (device, inode, bytes, mtime_ns, atime_ns) compared by
#      STAGE_SOURCE_STAT and recorded with the UTC staging window;
#   6. the job script, written from this script, then sbatch; scontrol's TimeLimit, JobName, QOS and account are
#      checked, and the job is cancelled if any differs.
# The job (rpd_flux1_job.sh, on its compute node): copies the clone to /dev/shm/limres-rpd-flux1/repo (the path the
# config binds) and rechecks HEAD, porcelain and the pins; the strace probe; an outer stat of the exception file before
# and after; #848's wrapper unchanged, in its own process group. On every exit it can catch (its own exits, an EXIT
# trap, and TERM/INT: scancel, or Slurm's TERM 300 s before the TimeLimit) it removes its /dev/shm directory, then
# writes job-host.txt's end line and job.rc (rc and cause). An uncatchable kill (SIGKILL, OOM) skips that; the fetch
# then reports the cleanup as unverified. Shared QOS, 4 CPUs, 16G, --time 03:00:00, --signal=B:TERM@300.
# Writes only under the root on pscratch (and the job's /dev/shm). Nothing is written to CFS. umask 077. No set -u.
# Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
S=@@S@@
CFG_SHA=cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b
FENCE_SHA=@@FENCE_SHA@@
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-flux1-connect rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
[ ! -e /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 ] || { echo "STOP: /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 exists"; finish 9; }
echo "node $(hostname) $(date -u +%FT%TZ); connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 2. the fence (cov2d*, t2a*, rpd* refuse)"
q=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; finish 3; }
printf '%s\n' "$q" | sed '/^$/d; s/^/squeue: /'
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a|rpd)/ {f=1} END {exit !f}' && { echo "STOP: a cov2d/t2a/rpd job is queued or running"; finish 3; }
echo "FENCE: clear"
mkdir -m 700 /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 || finish 9
echo "== 3. fresh clone at $S"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone || { echo "STOP: clone failed"; finish 5; }
git -C /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone fetch --quiet origin "$S" || { echo "STOP: fetch of $S failed"; finish 5; }
git -C /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone -c advice.detachedHead=false checkout --quiet "$S" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone rev-parse HEAD)
porc=$(git -C /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "$S" ] && [ "$porc" -eq 0 ] || { echo "STOP: the clone is not $S clean"; finish 5; }
while read -r want f; do
  got=$(sha256sum "/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone/$f" | cut -d' ' -f1)
  echo "sha256 $got $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not at its pinned sha256 $want"; finish 5; }
done <<'PINS'
@@PINS@@
PINS
echo "== 4. the READY config"
printf '%s' '@@CONFIG_B64@@' | base64 -d > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/production-config.ready.json || { echo "STOP: config decode"; finish 5; }
got=$(sha256sum /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/production-config.ready.json | cut -d' ' -f1)
echo "sha256 $got (expected $CFG_SHA) production-config.ready.json"
[ "$got" = "$CFG_SHA" ] || { echo "STOP: config digest"; finish 5; }
echo "== 5. the overlap fence"
mkdir /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/tools || finish 9
printf '%s' '@@FENCE_B64@@' | base64 -d > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/tools/fence_overlap.py
got=$(sha256sum /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/tools/fence_overlap.py | cut -d' ' -f1)
echo "sha256 $got (expected $FENCE_SHA) tools/fence_overlap.py"
[ "$got" = "$FENCE_SHA" ] || { echo "STOP: fence tool digest"; finish 5; }
"$MAT_PYTHON" -I /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/tools/fence_overlap.py \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/production-config.ready.json \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/fence-overlap.txt 2>&1
frc=$?
cat /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/fence-overlap.txt; echo "overlap fence rc=$frc"
[ "$frc" -eq 0 ] || { echo "STOP: the overlap fence did not clear; nothing is submitted"; finish 3; }
echo "== 6. the job"
cat > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/rpd_flux1_job.sh <<'JOB'
@@JOB@@
JOB
echo "job script sha256 $(sha256sum /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/rpd_flux1_job.sh | cut -d' ' -f1)"
jid=$(cd /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 && sbatch --parsable rpd_flux1_job.sh)
src=$?
echo "sbatch rc=$src jobid [$jid] $(date -u +%FT%TZ)"
[ "$src" -eq 0 ] && [[ "$jid" =~ ^[0-9]+$ ]] || { echo "STOP: sbatch failed"; finish 6; }
echo "$jid" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.id
info=$(scontrol show job "$jid" -o)
printf '%s\n' "$info" | tr ' ' '\n' | grep -E '^(JobId|JobName|UserId|Account|QOS|Partition|TimeLimit|NumNodes|NumCPUs|MinMemoryNode|JobState|StdOut|StdErr|WorkDir)='
want_ok=1
for kv in JobName=rpd_flux1 TimeLimit=03:00:00 QOS=shared Account=m3246; do
  printf '%s\n' "$info" | tr ' ' '\n' | grep -qx -- "$kv" || { echo "MISMATCH: $kv not in scontrol's record"; want_ok=0; }
done
if [ "$want_ok" -ne 1 ]; then
  scancel "$jid"; echo "scancel rc=$? for $jid"; echo "STOP: the job's record differs; cancelled"; finish 6
fi
echo "job $jid submitted and checked; the fetch reports it"
finish 0
