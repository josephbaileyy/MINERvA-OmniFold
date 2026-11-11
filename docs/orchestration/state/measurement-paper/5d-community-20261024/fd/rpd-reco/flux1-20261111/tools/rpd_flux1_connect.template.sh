#!/bin/bash
# RPD-RECO flux connect 1: #848's fd_rpd_reco_flux_connect.sh at #848's head a4c3e556, with the READY candidate config
# production-config.ready.json (sha256 cde8d029...), on one Perlmutter login node, at 0 node-h, with no Slurm job.
# DRAFT for coverage-5b-audit and the director's go. It runs only on that go.
# The wrapper is #848's, unchanged: check-mat-setup, the MAT setup, the real-MnvH1D check on the committed probe,
# custody prepare (fresh staging under O_NOATIME, its own COV2D fence, NATIVE_SELECTION, the 15-file MAT inventory),
# the missing-dependency check, flux-extract under strace, and trace-check.
# This script, in order:
#   1. refuses unless on a login node, with both literal roots absent:
#      /dev/shm/limres-rpd-flux1 (the clone the config binds) and /pscratch/sd/j/josephrb/rpd-reco-flux-20261111;
#   2. the COV2D fence, inline: any queued or running job of ours named cov2d* or t2a* refuses
#      (the launcher's fence mode runs the committed cov2d_fence.sh first; custody prepare runs its own fence too);
#   3. a fresh clone at a4c3e556, HEAD and porcelain checked, and the sha256 of the four code files, the flux
#      wrapper, the class check, the probe and the five files the config binds by path;
#   4. the READY config, written from this script and checked against its sha256;
#   5. the strace probe;
#   6. the runner, written from this script, launched detached (setsid nohup) with its stdout and stderr in
#      connect.log and its exit status in connect.rc, both under the pscratch root. This script then waits 30 s,
#      prints the log's size (its content only after the fetch's redaction check, as in prologue 5) and exits;
#      the runner keeps going.
# Writes: /dev/shm/limres-rpd-flux1 (the clone, the config) and /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 (the
# run, the private record, the log). Nothing is written to CFS. Both roots are left in place: the fetch script reads
# them, and they are deleted after the receipt merges, by a separate connect.
# umask 077. No set -u. Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
S=a4c3e556e7ccf915d103eaeba77ab31ed06b98cc
CFG_SHA=cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
finish() { echo "== rpd-flux1-connect rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
[ ! -e /dev/shm/limres-rpd-flux1 ] || { echo "STOP: /dev/shm/limres-rpd-flux1 exists"; finish 9; }
[ ! -e /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 ] || { echo "STOP: /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 exists"; finish 9; }
echo "node $(hostname) $(date -u +%FT%TZ); connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 2. COV2D fence (inline)"
q=$(squeue --me -h -o '%i|%j|%T') || { echo "STOP: squeue failed"; finish 3; }
printf '%s\n' "$q" | sed '/^$/d; s/^/squeue: /'
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && { echo "STOP: a cov2d/t2a job is queued or running"; finish 3; }
echo "FENCE: clear"
mkdir -m 700 /dev/shm/limres-rpd-flux1 || finish 9
mkdir -m 700 /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 || finish 9
echo "== 3. fresh clone at $S"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-rpd-flux1/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-rpd-flux1/repo fetch --quiet origin "$S" || { echo "STOP: fetch of $S failed"; finish 5; }
git -C /dev/shm/limres-rpd-flux1/repo -c advice.detachedHead=false checkout --quiet "$S" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C /dev/shm/limres-rpd-flux1/repo rev-parse HEAD)
porc=$(git -C /dev/shm/limres-rpd-flux1/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"
[ "$head" = "$S" ] && [ "$porc" -eq 0 ] || { echo "STOP: the clone is not $S clean"; finish 5; }
while read -r want f; do
  got=$(sha256sum "/dev/shm/limres-rpd-flux1/repo/$f" | cut -d' ' -f1)
  echo "sha256 $got $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not at its pinned sha256 $want"; finish 5; }
done <<'PINS'
7302cc1df71758cfae6bdcfba031d37cc78902beaf454b29e12f3e053d44f141 nd-unfolding/fd_rpd_reco.py
2c087d8fde379cb2ceea62183e7a9c2c5f9c18a1b3f3367b112566f77db3ab7f nd-unfolding/fd_rpd_reco_custody.py
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
echo "== 4. the READY config"
printf '%s' '@@CONFIG_B64@@' | base64 -d > /dev/shm/limres-rpd-flux1/production-config.ready.json || { echo "STOP: config decode"; finish 5; }
got=$(sha256sum /dev/shm/limres-rpd-flux1/production-config.ready.json | cut -d' ' -f1)
echo "sha256 $got (expected $CFG_SHA) production-config.ready.json"
[ "$got" = "$CFG_SHA" ] || { echo "STOP: config digest"; finish 5; }
echo "== 5. strace probe"
/usr/bin/strace -f -yy -e trace=openat -o /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/strace-probe.txt /bin/true
src=$?
echo "strace probe rc=$src; lines $(wc -l < /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/strace-probe.txt)"
[ "$src" -eq 0 ] || { echo "STOP: strace probe"; finish 6; }
echo "== 6. the runner"
cat > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/runner.sh <<'RUNNER'
#!/bin/bash
# The detached runner of rpd_flux1_connect.sh: #848's flux wrapper with five literal arguments, then the exit status.
umask 077
echo "== runner start $(date -u +%FT%TZ) host $(hostname) pid $$"
bash /dev/shm/limres-rpd-flux1/repo/nd-unfolding/fd_rpd_reco_flux_connect.sh /dev/shm/limres-rpd-flux1/repo \
  /dev/shm/limres-rpd-flux1/production-config.ready.json \
  cde8d02904b0257d82745b03fd61c1aef1a50270f14f36ad7f38c8b3f235f50b \
  /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/run \
  /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
rc=$?
echo "== runner end rc=$rc $(date -u +%FT%TZ)"
echo "rc=$rc end=$(date -u +%FT%TZ)" > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.rc.partial
mv -- /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.rc.partial /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.rc
RUNNER
echo "runner sha256 $(sha256sum /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/runner.sh | cut -d' ' -f1)"
setsid nohup bash /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/runner.sh \
  > /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.log 2>&1 < /dev/null &
echo "runner launched, pid $!, $(date -u +%FT%TZ)"
sleep 30
echo "== after 30 s: connect.log $(wc -c < /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.log) bytes, $(wc -l < /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.log) lines (its content is printed only by the fetch, after the redaction check)"
[ -f /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.rc ] && { echo "connect.rc already written:"; cat /pscratch/sd/j/josephrb/rpd-reco-flux-20261111/connect.rc; }
ps -o pid,etime,stat,args -u "$(id -un)" | grep -E 'limres-rpd-flux1/|rpd-reco-flux-20261111/runner' | grep -v grep
finish 0
