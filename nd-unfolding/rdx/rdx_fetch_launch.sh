#!/bin/bash
# RDX's read-only fetch launcher (RDX-BINDING-1 addendum J7, ruling 2): the 15 products, 15 inventories and two job logs,
# read O_NOATIME on a login node and streamed back as one tar. Nothing is staged or written on the cluster: the local
# rdx_fetch_remote.py, whose sha256 must be the approved one, goes over ssh's stdin to /usr/bin/python3 on NODE (the
# connect launcher's hop: saul, then a loginNN). No job; the fence is sacct only. ssh's rc is read unpiped. The tar is
# unpacked into <dir>/fetched only if every sha256 matches the manifest, O_NOATIME was used, no file's stat moved
# during its read and both fence reads were clear. The inner ssh writes nothing on saul either: no control socket, a
# host key that saul does not already know refuses (no known_hosts write), and no host-key update.
# Usage: bash rdx_fetch_launch.sh <new empty dir> <loginNN>
F=${1:?session dir}; NODE=${2:?loginNN}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
S="$HERE/rdx_fetch_remote.py"; SHA=93ddb2643c7b5a3b9690752f07d01f87d7aa3add7cd369a522cf1b248aff7d5d
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local fetch script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8)
HOP=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8
     -o StrictHostKeyChecking=yes -o UpdateHostKeys=no)
echo "launch $(date -u +%FT%TZ) node $NODE script sha256 $SHA"
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE /usr/bin/python3 -" < "$S" > "$F/fetch.tar" 2> "$F/fetch.err"
rc=$?
echo "ssh rc=$rc"
if [ "$rc" -ne 0 ]; then echo "STOP: the fetch exited $rc"; grep -v '^\*\|^$' "$F/fetch.err" | tail -5; exit "$rc"; fi
mkdir "$F/fetched"
python3 "$S" unpack "$F/fetch.tar" "$F/fetched"
urc=$?
echo "unpack rc=$urc"
shasum -a 256 "$F/fetch.tar"
exit "$urc"
