#!/bin/bash
#SBATCH -A m3246
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH --no-requeue
#SBATCH -J oofvc_dump
#SBATCH -o /pscratch/sd/j/josephrb/oofvc-20261126-r2/logs/dump-%A_%a.log
# OOFVC step 1A: one MC playlist per task (PLS[i]). The time limit is set per submission by oofvc_dump.sh.
# Writes only $R/dump/<pl>.{root,log,sha256,done}.
set -u
R=/pscratch/sd/j/josephrb/oofvc-20261126-r2
NUE_DECLARED=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
# fence check (RDX-BINDING-1's terms, as geanttw applied them): no live cov2d or t2a job, read from sacct (never
# squeue); a state outside the terminal set, or an empty one, counts as live
fence_check() {
  local since out live
  since=$(date -u -d '14 days ago' +%F) || { echo "[oofvc_dump] STOP: date failed ($1)"; exit 2; }
  out=$(sacct -X -n -P -S "$since" -o JobID,JobName,State 2>&1) || { echo "[oofvc_dump] STOP: sacct failed ($1)"; exit 2; }
  live=$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ { split($3, s, " ");
    if (s[1] !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) print }')
  [ -z "$live" ] || { echo "[oofvc_dump] STOP: a fenced job is live ($1): $live"; exit 2; }
  echo "fence check ($1): no live cov2d or t2a job $(date -u +%FT%TZ)"
}

MAN=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/manifests
PLS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)
pl=${PLS[$SLURM_ARRAY_TASK_ID]}
cd "$R/dump" || exit 2
[ -s "$R/gates/ll5d_atime_post.txt" ] || { echo "[oofvc_dump] STOP: no LL5D atime-post record"; exit 2; }
fence_check "job start"
echo "[oofvc_dump] $pl node=$(hostname) job=${SLURM_JOB_ID} start=$(date -u +%FT%TZ)"
sha256sum -c built.sha256 || exit 3
grep -q " $MAN/${pl}_MC.txt\$" manifests.sha256 && sha256sum -c <(grep " $MAN/${pl}_MC.txt\$" manifests.sha256) || exit 3
[ ! -e "$pl.root" ] && [ ! -e "$pl.tmp.root" ] || { echo "STOP: $pl output exists"; exit 2; }
set +u; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null; set -u
export OPENBLAS_NUM_THREADS=1
# cov2d's condition (c): the NuE constraint file that SetNuEConstraint(true) makes the flux reweighter read (plainly;
# cov2d-protected) is the declared one, and its atime_ns and mtime_ns are logged with UTC before and after the run
NUE="${MPARAMFILESROOT:-$MINERVA_PREFIX/etc/MParamFiles}/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
# the same file, canonical against canonical: the declared path reaches it through the MParamFiles symlink (the
# 62053260 pilot's false STOP compared the canonical path with the literal one); both must exist
nue_path_ok() {
  [ -f "$1" ] && [ -f "$2" ] && [ -n "$(readlink -f "$1")" ] && [ "$(readlink -f "$1")" = "$(readlink -f "$2")" ]
}
nue_path_ok "$NUE" "$NUE_DECLARED" || { echo "[oofvc_dump] STOP: the NuE file $NUE is not the declared one"; exit 2; }
echo "[oofvc_dump] NUE path declared=$NUE_DECLARED canonical=$(readlink -f "$NUE_DECLARED") resolved=$NUE" >> "$pl.nue.log"
nue() {
  python3 -c "
import os, sys, time
s = os.stat(sys.argv[1])
print('[oofvc_dump] NUE %s utc=%s atime_ns=%d mtime_ns=%d size=%d' % (
    sys.argv[2], time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), s.st_atime_ns, s.st_mtime_ns, s.st_size))" \
    "$NUE_DECLARED" "$1" >> "$pl.nue.log" || { echo "[oofvc_dump] STOP: the NuE log failed"; exit 2; }
}
fence_check "immediately before the binary"
nue before
./oofvc_dump "$pl" "$MAN/${pl}_MC.txt" "$pl.tmp.root" > "$pl.log" 2>&1
rc=$?
nue after
cat "$pl.nue.log"
echo "[oofvc_dump] $pl rc=$rc $(tail -1 "$pl.log")"
[ $rc = 0 ] || exit $rc
mv "$pl.tmp.root" "$pl.root" && sha256sum "$pl.root" > "$pl.sha256" && touch "$pl.done" \
  || { echo "[oofvc_dump] $pl STOP: finalizing the output failed"; exit 4; }
echo "[oofvc_dump] $pl done=$(date -u +%FT%TZ)"
exit 0
