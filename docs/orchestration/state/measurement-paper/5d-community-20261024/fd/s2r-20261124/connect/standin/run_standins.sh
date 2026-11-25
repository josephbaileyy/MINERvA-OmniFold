#!/bin/bash
# Host side: one fresh container per variant, every writable path bind-mounted from a fresh scratch directory (the
# Docker VM's own disk is full), the host object store read-only, the connect directory read-only.
# Usage: run_standins.sh <scratch dir under $HOME, which colima shares with the VM> <submit|fetch> <variant>...
S=${1:?scratch}; W=${2:?which}; shift 2
HERE=$(cd "$(dirname "$0")" && pwd); C=$(dirname "$HERE")
for v in "$@"; do
  R="$S/standin-$W-$v-$(date +%s)"; mkdir -p "$R"/{root,global,stub}
  V="s2r-standin-$W-$v-$(date +%s)"
  docker volume create "$V-ps" > /dev/null && docker volume create "$V-tmp" > /dev/null || { echo "STOP: volume create"; exit 9; }
  # /pscratch and /tmp on named volumes (ext4 on the VM's data disk): O_NOATIME holds there, while a bind of a host
  # directory (macOS virtiofs) moves atime on every read and would trip the connect's stat-unmoved check
  docker run --rm -v /Users/josephbailey/local-research/MINERvA-OmniFold/.git:/hostgit:ro -v "$C":/connect:ro \
    -v "$HERE":/standin:ro -v "$V-ps":/pscratch -v "$V-tmp":/tmp -v "$R/root":/root -v "$R/global":/global \
    -v "$R/stub":/stub s2r-standin:local bash /standin/standin.sh "$W" "$v" > "$HERE/standin-$W-$v.log.txt" 2>&1
  echo "$W $v: docker rc=$? $(grep -m1 '^=== script rc=' "$HERE/standin-$W-$v.log.txt")"
  docker volume rm "$V-ps" "$V-tmp" > /dev/null; rm -rf -- "$R"   # each run's ~1 GB clone is removed at once
done
