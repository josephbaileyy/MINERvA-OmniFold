#!/bin/bash
# go.sh <N> <connect sha256 the director approved>: checks the launcher and connect-<N>.sh against the digests the
# director named, then runs launch-s5.sh <N>. Refuses (exit 2) on any mismatch; launches nothing.
LAUNCHER_SHA=314fa64d950770dd527fae1f01f1cf9efe6e6394b25f7d7ca00bd9f0ba74f26f   # director 2026-11-07 (fence: rs1_*, ens1_*)
N=$1; WANT=$2; H=$(cd "$(dirname "$0")" && pwd)
[ -n "$N" ] && [ ${#WANT} = 64 ] || { echo "usage: go.sh <N> <connect sha256>"; exit 2; }
SRC=$H/connect-$N.sh; case "$N" in n*|s*) SRC=$H/connect-${N:0:1}-${N:1}.sh ;; esac   # as launch-s5.sh:33-34
[ -f "$SRC" ] || { echo "REFUSED no $SRC"; exit 2; }
got_l=$(shasum -a 256 "$H/launch-s5.sh" | cut -c1-64); got_c=$(shasum -a 256 "$SRC" | cut -c1-64)
[ "$got_l" = "$LAUNCHER_SHA" ] && echo "LAUNCHER-SHA OK $got_l" || { echo "REFUSED launch-s5.sh is $got_l, not $LAUNCHER_SHA"; exit 2; }
[ "$got_c" = "$WANT" ] && echo "CONNECT-SHA OK $SRC $got_c" || { echo "REFUSED $SRC is $got_c, not $WANT"; exit 2; }
exec bash "$H/launch-s5.sh" "$N"
