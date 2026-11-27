#!/bin/bash
# OOFVC cleanup: the Mac-side launcher (oofvc_launch.sh's staging, unchanged in form). One ssh session per call: it
# enters at saul.nersc.gov and hops to NODE; stdin carries oofvc_cleanup.sh, staged in a private mktemp file in /dev/shm
# whose sha256 must equal the approved one, or NODE deletes it and exits 8 before anything runs.
# Usage: bash oofvc_cleanup_launch.sh manifest <new empty session dir> <login node>
#        bash oofvc_cleanup_launch.sh remove   <new empty session dir> <login node> <LISTING_SHA from the manifest>
MODE=${1:?manifest|remove}; F=${2:?session dir}; NODE=${3:-}; WANT=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd)
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
S="$HERE/oofvc_cleanup.sh"; SHA=0a6b59ec3b33990c4a351fcf4ae2dd0e9cc7e0307fd22562738a8619b3270a65
case "$MODE" in
  manifest) [ -z "$WANT" ] || { echo "STOP: manifest takes no listing sha"; exit 9; }; ARG=manifest ;;
  remove) case "$WANT" in *[!0-9a-f]*|'') echo "STOP: remove needs the 64-hex listing sha"; exit 9 ;; esac
          [ ${#WANT} = 64 ] || { echo "STOP: listing sha must be 64 hex"; exit 9; }; ARG="remove $WANT" ;;
  *) echo "STOP: mode $MODE"; exit 9 ;;
esac
case "$SHA" in *__*) echo "STOP: the approved sha256 is not filled in"; exit 9;; esac
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
h=$(shasum -a 256 "$S" | cut -d' ' -f1) && [ "$h" = "$SHA" ] || { echo "STOP: the local cleanup script is not the approved one"; exit 8; }
R="umask 077; f=\$(mktemp /dev/shm/oofvc-cleanup.XXXXXXXX) || exit 8; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: staged copy sha256 \$h is not $SHA\"; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\"; bash \"\$f\" \"\$f\" $ARG; r=\$?; rm -f -- \"\$f\"; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -v '^[fdl]|' "$F/session.out"
exit $rc
