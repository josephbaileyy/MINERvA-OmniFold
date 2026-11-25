#!/bin/bash
# One fresh container per variant; /pscratch and /tmp on named volumes (O_NOATIME holds on their ext4), removed after.
HERE=$(cd "$(dirname "$0")" && pwd); C=$(dirname "$HERE")
for v in "$@"; do
  V="bsel-standin-$v-$(date +%s)"
  docker volume create "$V-ps" > /dev/null && docker volume create "$V-tmp" > /dev/null || { echo "STOP: volume create"; exit 9; }
  docker run --rm -v "$C":/connect:ro -v "$HERE":/standin:ro -v "$V-ps":/pscratch -v "$V-tmp":/tmp \
    s2r-standin:local bash /standin/standin.sh "$v" > "$HERE/standin-$v.log.txt" 2>&1
  echo "$v: docker rc=$? $(grep -m1 '^=== script rc=' "$HERE/standin-$v.log.txt") | $(grep -m1 -E '^(BAIL|STOP)' "$HERE/standin-$v.log.txt")"
  docker volume rm "$V-ps" "$V-tmp" > /dev/null
done
