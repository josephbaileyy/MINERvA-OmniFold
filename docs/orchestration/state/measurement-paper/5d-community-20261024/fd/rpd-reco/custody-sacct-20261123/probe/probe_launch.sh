#!/bin/bash
# probe_launch.sh: runs custody_sacct_probe.sh on a Perlmutter login node (limitation-resolver, 2026-11-23; e1_survey_launch.sh
# 24dddd72 with the remote script's name changed).
# usage: bash probe_launch.sh <expected sha256 of custody_sacct_probe.sh> <out dir>
# It refuses unless the remote script's sha256 equals the expected one (the sha the director approved), and unless the
# cert is valid for at least 30 more minutes, read in UTC. It runs the script once over ssh with a fresh connection
# (ControlPath=none) and records ssh's rc unpiped. It writes only into <out dir>, and nothing on the cluster.
set -eu
EXP=$1; OUT=$2
HERE=$(cd "$(dirname "$0")" && pwd)
REM="$HERE/custody_sacct_probe.sh"
got=$(shasum -a 256 "$REM" | awk '{print $1}')
[ "$got" = "$EXP" ] || { echo "REFUSED: remote script sha256 $got, expected $EXP"; exit 2; }
mkdir -p "$OUT"
[ -z "$(ls -A "$OUT")" ] || { echo "REFUSED: $OUT is not empty"; exit 2; }
to=$(TZ=UTC ssh-keygen -L -f "$HOME/.ssh/nersc-cert.pub" | awk '/Valid:/ {print $NF}')
to_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%S' "$to" +%s)
now=$(date -u +%s)
echo "cert valid to ${to}Z (UTC); now $(date -u +%FT%TZ)" | tee "$OUT/cert.txt"
[ $((to_s - now)) -ge 1800 ] || { echo "REFUSED: cert expires within 30 minutes"; exit 3; }
cp "$REM" "$OUT/custody_sacct_probe.sh"
echo "$got  custody_sacct_probe.sh" > "$OUT/remote.sha256"
set +e
ssh -o ControlPath=none -o BatchMode=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=4 \
  josephrb@saul.nersc.gov 'bash -s' < "$REM" > "$OUT/survey.log" 2> "$OUT/survey.stderr"
rc=$?
set -e
echo "$rc" > "$OUT/ssh_rc.txt"
echo "ssh rc=$rc; log $(wc -l < "$OUT/survey.log") lines"
exit "$rc"
