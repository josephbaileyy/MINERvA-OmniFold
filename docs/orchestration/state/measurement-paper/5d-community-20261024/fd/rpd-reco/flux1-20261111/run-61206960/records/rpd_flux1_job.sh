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
#SBATCH --signal=B:TERM@300
#SBATCH --chdir=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111
#SBATCH --output=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.out
#SBATCH --error=/pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.err
# rpd_flux1: RPD-RECO flux connect 1, the job half, written by rpd_flux1_connect.sh. #848's wrapper runs unchanged.
# Traps: Slurm sends TERM to this shell 300 s before the TimeLimit (--signal=B:TERM@300) and on scancel. The TERM/INT
# trap stops the wrapper's own process group (TERM, up to 10 s, then KILL) and calls fin. The EXIT trap calls fin on
# any exit that did not pass through it. fin removes /dev/shm/limres-rpd-flux1, then writes job-host.txt's end line and
# job.rc (rc and cause). A SIGKILL to this shell (Slurm after KillWait, or the OOM killer) cannot be caught: then no
# job.rc is written, the fetch reads sacct's state and reports the /dev/shm cleanup as unverified.
umask 077
made=0
child=0
cause=exit
finished=0
fin() {  # job.rc is written last: its presence means the job's own steps, the /dev/shm removal included, are done
  [ "$finished" -eq 1 ] && exit "$1"
  finished=1
  trap '' TERM INT
  [ "$made" -eq 1 ] && { rm -rf -- /dev/shm/limres-rpd-flux1; echo "removed /dev/shm/limres-rpd-flux1 rc=$?"; }
  echo "end=$(date -u +%FT%TZ) rc=$1 cause=$cause" >> /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job-host.txt
  echo "rc=$1 cause=$cause end=$(date -u +%FT%TZ)" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc.partial
  mv -- /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc.partial /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job.rc
  exit "$1"
}
on_signal() {
  cause=signal-$1
  echo "== caught $1 $(date -u +%FT%TZ); stopping the wrapper's process group [$child]"
  if [ "$child" -gt 0 ]; then
    kill -TERM -- "-$child" 2>/dev/null
    for _ in $(seq 1 10); do kill -0 "$child" 2>/dev/null || break; sleep 1; done
    kill -KILL -- "-$child" 2>/dev/null
  fi
  fin 143
}
trap 'on_signal TERM' TERM
trap 'on_signal INT' INT
trap 'r=$?; [ "$finished" -eq 1 ] || { cause=exit-trap; fin "$r"; }' EXIT
echo "jobid=$SLURM_JOB_ID host=$(hostname) start=$(date -u +%FT%TZ)" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/job-host.txt
echo "== rpd_flux1 job $SLURM_JOB_ID on $(hostname) $(date -u +%FT%TZ)"
[ ! -e /dev/shm/limres-rpd-flux1 ] || { echo "STOP: /dev/shm/limres-rpd-flux1 exists on this node"; fin 9; }
mkdir -m 700 /dev/shm/limres-rpd-flux1 || fin 9
made=1
cp -a /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/clone /dev/shm/limres-rpd-flux1/repo || { echo "STOP: copy of the clone"; fin 5; }
head=$(git -C /dev/shm/limres-rpd-flux1/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-rpd-flux1/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6" ] && [ "$porc" -eq 0 ] || { echo "STOP: the copy is not clean at the pinned head"; fin 5; }
while read -r want f; do
  got=$(sha256sum "/dev/shm/limres-rpd-flux1/repo/$f" | cut -d' ' -f1)
  echo "sha256 $got $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not at its pinned sha256 $want"; fin 5; }
done <<'PINS'
7302cc1df71758cfae6bdcfba031d37cc78902beaf454b29e12f3e053d44f141 nd-unfolding/fd_rpd_reco.py
867822e3cbf7063088717565d2be4e68ae3625cb24ce468255d98ba8fd59bdb5 nd-unfolding/fd_rpd_reco_custody.py
6e4ed0f1d7f55b7bfe2f26752eeb28bb9cbe33325a9d91cc7c06d9494a0b0a70 nd-unfolding/fd_rpd_inputs.py
32db52355a4811bd4bf5f8b8cc0b5c397c7b403a0996048bcafd8c8c665cc76e nd-unfolding/fd_rpd_reco_flux_connect.sh
06360100038f0203b0d994f71c171b12cd955697edf32d1d744c4ce271ceb26d nd-unfolding/tests/fd_rpd_reco_mat_check.py
d9704aa45c016b044284d9e3cfc8c6d5c07cda0835a445866d5f792c8ac82840 docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root
7638f94f56ad0471769445cffe68ff538c9b68158f48415e7c3cafa7ee95a295 docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/INPUTS.sha256
b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89 nd-unfolding/pv-ladder/readouts/h2_definition.json
e60609e756e35fbc9846ae5983c1d848999bc17c7504e3ca876c22c9bcc0e88f docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/flux-pot-provenance-20261104/energy-spectrum-candidates.tsv
900d7368d6184d503399bd99c0fd30085212df0327b8be374182495b85a3677d MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h
b056487e592e7704c2a98c14243b26f44c82821382837a263b75c169859cce0b docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/code-audit-fix-20261106/MAT-DATA-DEPENDENCIES.json
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
# In its own process group (setsid), in the background, so the trap runs during wait and can stop the whole group.
# The pgid check (f3): the child holds at a gate until this shell has seen its process group id equal its pid ($!),
# that is, setsid ran in place. A mismatch (setsid forked) STOPs with cause=pgid-check before the wrapper starts. The
# gate gives up when /dev/shm/limres-rpd-flux1 is removed or after 30 s, so a forked waiter cannot linger.
setsid bash -c 'for _ in $(seq 1 150); do [ -e /dev/shm/limres-rpd-flux1/wrapper.go ] && exec bash "$@"; [ -d /dev/shm/limres-rpd-flux1 ] || exit 1; sleep 0.2; done; exit 1' rpd_flux1_gate \
  /dev/shm/limres-rpd-flux1/repo/nd-unfolding/fd_rpd_reco_flux_connect.sh /dev/shm/limres-rpd-flux1/repo \
  /dev/shm/limres-rpd-flux1/production-config.ready.json \
  cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run \
  /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.log 2>&1 &
child=$!
pg=""
for _ in $(seq 1 25); do  # up to 5 s for setsid() to take effect; stop early if the process is gone
  pg=$(ps -o pgid= -p "$child" 2>/dev/null | tr -d ' ')
  [ "$pg" = "$child" ] && break
  kill -0 "$child" 2>/dev/null || break
  sleep 0.2
done
echo "wrapper pid $child; its process group [$pg]"
if [ "$pg" != "$child" ]; then
  echo "STOP: the wrapper's process group [$pg] is not its pid $child (setsid did not run in place); the wrapper was not started"
  cause=pgid-check
  kill -TERM -- "$child" 2>/dev/null
  fin 8
fi
echo "wrapper pid/pgid $child (checked)"
touch /dev/shm/limres-rpd-flux1/wrapper.go
wait "$child"
rc=$?
echo "== wrapper rc=$rc $(date -u +%FT%TZ)"
outer after
fin "$rc"
