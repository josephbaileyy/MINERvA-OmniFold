#!/bin/bash
#SBATCH --job-name=rpd_flux1
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=03:00:00
#SBATCH --chdir=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111
#SBATCH --output=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.out
#SBATCH --error=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.err
# rpd_flux1: RPD-RECO flux connect 1, the job half, written by rpd_flux1_connect.sh. #848's wrapper runs unchanged.
umask 077
made=0
fin() {  # job.rc is written last: its presence means the job's own steps, the /dev/shm removal included, are done
  [ "$made" -eq 1 ] && { rm -rf -- /dev/shm/limres-rpd-flux1; echo "removed /dev/shm/limres-rpd-flux1 rc=$?"; }
  echo "end=$(date -u +%FT%TZ) rc=$1" >> /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job-host.txt
  echo "rc=$1 end=$(date -u +%FT%TZ)" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc.partial
  mv -- /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc.partial /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc
  exit "$1"
}
echo "jobid=$SLURM_JOB_ID host=$(hostname) start=$(date -u +%FT%TZ)" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job-host.txt
echo "== rpd_flux1 job $SLURM_JOB_ID on $(hostname) $(date -u +%FT%TZ)"
[ ! -e /dev/shm/limres-rpd-flux1 ] || { echo "STOP: /dev/shm/limres-rpd-flux1 exists on this node"; fin 9; }
mkdir -m 700 /dev/shm/limres-rpd-flux1 || fin 9
made=1
cp -a /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone /dev/shm/limres-rpd-flux1/repo || { echo "STOP: copy of the clone"; fin 5; }
head=$(git -C /dev/shm/limres-rpd-flux1/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-rpd-flux1/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "@@S@@" ] && [ "$porc" -eq 0 ] || { echo "STOP: the copy is not clean at the pinned head"; fin 5; }
while read -r want f; do
  got=$(sha256sum "/dev/shm/limres-rpd-flux1/repo/$f" | cut -d' ' -f1)
  echo "sha256 $got $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not at its pinned sha256 $want"; fin 5; }
done <<'PINS'
@@PINS@@
PINS
cp /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/production-config.ready.json /dev/shm/limres-rpd-flux1/production-config.ready.json || fin 5
got=$(sha256sum /dev/shm/limres-rpd-flux1/production-config.ready.json | cut -d' ' -f1)
echo "config sha256 $got"
[ "$got" = cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b ] || { echo "STOP: config digest"; fin 5; }
/usr/bin/strace -f -yy -e trace=openat -o /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/strace-probe.txt /bin/true
p=$?; echo "strace probe rc=$p"
[ "$p" -eq 0 ] || { echo "STOP: strace probe"; fin 6; }
outer() {  # stat only (no open): the exception file, for the whole job window
  /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -S -c 'import os,sys,time; s=os.stat(sys.argv[1]); print(sys.argv[2], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "device", s.st_dev, "inode", s.st_ino, "bytes", s.st_size, "mtime_ns", s.st_mtime_ns, "atime_ns", s.st_atime_ns)' \
    /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt "$1" \
    >> /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/exception-stat-outer.txt
}
outer before
echo "== the wrapper $(date -u +%FT%TZ)"
bash /dev/shm/limres-rpd-flux1/repo/nd-unfolding/fd_rpd_reco_flux_connect.sh /dev/shm/limres-rpd-flux1/repo \
  /dev/shm/limres-rpd-flux1/production-config.ready.json \
  cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run \
  /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.log 2>&1
rc=$?
echo "== wrapper rc=$rc $(date -u +%FT%TZ)"
outer after
fin "$rc"
