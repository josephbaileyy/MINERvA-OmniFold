#!/bin/bash
# The launcher for vf_inputs_check.sh. saul, then a loginNN (inner hop's host key checked strictly). The script goes on
# stdin into a shell variable on the node; its sha256 must equal the approved one, or the node exits 8 before anything
# runs; it runs by eval of that variable in a subshell (no exec, so no argument-size limit), so nothing is written. Output: stdout only, saved here.
# Usage: bash vf_inputs_launch.sh <new empty local dir> <loginNN> <window_end_epoch> <fence prefixes, comma-sep>
F=${1:?session dir}; NODE=${2:?loginNN}; WEND=${3:?window end epoch}; FENCE=${4:?fence}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/vf_inputs_check.sh"; SHA=6d0725c11de27eaa63592e33e0127b9c0eaf29ebe070c373ca6387087c082640
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || { echo "STOP: window end '$WEND'"; exit 9; }
[ "$(date +%s)" -le "$WEND" ] || { echo "STOP: the window has ended"; exit 9; }
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || { echo "STOP: fence '$FENCE'"; exit 9; }
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local check script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
R="s=\$(cat; echo x); s=\${s%x}; h=\$(printf '%s' \"\$s\" | sha256sum | cut -d' ' -f1); if [ \"\$h\" != 6d0725c11de27eaa63592e33e0127b9c0eaf29ebe070c373ca6387087c082640 ]; then echo \"STOP: stdin script sha256 \$h is not 6d0725c11de27eaa63592e33e0127b9c0eaf29ebe070c373ca6387087c082640\"; exit 8; fi; echo \"node \$(hostname) script sha256 \$h\"; ( set -- $WEND $FENCE; eval \"\$s\" ) < /dev/null; r=\$?; echo \"script rc=\$r\"; exit \$r"
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE $(printf '%q' "$R")" < "$S" > "$F/session.out" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -q '^script rc=' "$F/session.out" || { echo "STOP: the session did not report a script rc"; exit 9; }
grep -q '^BAIL ' "$F/session.out" && { echo "STOP: the check bailed before reading anything"; grep '^BAIL ' "$F/session.out"; exit 9; }
awk -F'\t' 'NF==10' "$F/session.out" > "$F/vf_inputs_check.tsv"
echo "rows $(($(wc -l < "$F/vf_inputs_check.tsv") - 1))"
awk -F'\t' 'NR>1 {c[$1" "$9]++} END {for (k in c) print k, c[k]}' "$F/vf_inputs_check.tsv" | sort
exit $rc
