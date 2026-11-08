#!/bin/bash
# Mac side of ENS1 stage-1 dry-run connect 1. It refuses unless ens1_dry1_submit.sh has the sha256 the director was sent ($1).
# It ships the script to a /dev/shm copy on a login node and runs it there with stdin from /dev/null, so nothing in it
# can eat its own script. ssh's rc is read unpiped.
HERE=$(cd "$(dirname "$0")" && pwd)
S=$HERE/ens1_dry1_submit.sh
want=${1:?sha256 sent to the director}
got=$(shasum -a 256 "$S" | cut -d' ' -f1)
[ "$got" = "$want" ] || { echo "refusing: ens1_dry1_submit.sh is $got, not $want" >&2; exit 2; }
ssh -o ControlPath=none -o BatchMode=yes saul.nersc.gov \
  'f=$(mktemp /dev/shm/ens1_dry1.XXXXXX) && cat > "$f" && bash "$f" "$f" < /dev/null' < "$S"
rc=$?
echo "ssh rc=$rc"
exit $rc
