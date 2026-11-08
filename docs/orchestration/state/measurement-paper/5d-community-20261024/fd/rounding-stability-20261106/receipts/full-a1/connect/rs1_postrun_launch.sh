#!/bin/bash
# Mac side of RS1 post-run connect. It refuses unless rs1_postrun.sh has the sha256 the director was sent ($1).
# It ships the script to a /dev/shm copy on a login node and runs it there with stdin from /dev/null, so nothing in it
# can eat its own script. ssh's rc is read unpiped.
HERE=$(cd "$(dirname "$0")" && pwd)
S=$HERE/rs1_postrun.sh
want=${1:?sha256 sent to the director}
got=$(shasum -a 256 "$S" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "refusing: rs1_postrun.sh is $got, not $want" >&2; exit 2; }
ssh -o ControlPath=none -o BatchMode=yes saul.nersc.gov \
  'f=$(mktemp /dev/shm/rs1_post.XXXXXX) && cat > "$f" && bash "$f" "$f" < /dev/null' < "$S"
rc=$?
echo "ssh rc=$rc"
exit $rc
