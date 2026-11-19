#!/bin/bash
# PILOT-FB's copy connect launcher (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3): RS1's 21 A0 products and the sigma
# receipt copied, O_NOATIME, into the stage the smoke created. The local pfb_copy_remote.py, whose sha256 must be the
# approved one, goes over ssh's stdin to /usr/bin/python3 on NODE (saul, then a loginNN), with the deploy as its one
# argument. No job and no sbatch; the fence is sacct only (a 14-day read, each State classified, before and after).
# Nothing is written on the cluster outside the stage's a0-refs/ and assess_receipt.json, and nothing on CFS. The inner
# ssh writes nothing on saul (no control socket, no known_hosts entry, no host-key update). ssh's rc is read unpiped;
# the manifest is then verified on the laptop (pfb_copy_remote.py verify).
# Usage: bash pfb_copy_launch.sh <new empty dir> <loginNN> <deploy: an absolute /pscratch/sd/j/josephrb/... checkout>
F=${1:?session dir}; NODE=${2:?loginNN}; DEPLOY=${3:?deploy}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$DEPLOY" =~ ^/pscratch/sd/j/josephrb/[A-Za-z0-9._/-]+$ ]] && [[ "$DEPLOY" != *..* ]] \
    || { echo "STOP: the deploy '$DEPLOY' is not an absolute /pscratch/sd/j/josephrb path"; exit 9; }
S="$HERE/pfb_copy_remote.py"; SHA=2f5e8c79ba4d2154f0807f8b7e63933ae2427705b403fd4b783fdc13f1413570
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local copy script is not the approved one"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o LogLevel=ERROR)
HOP=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8
     -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o LogLevel=ERROR)
echo "launch $(date -u +%FT%TZ) node $NODE deploy $DEPLOY script sha256 $SHA"
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE /usr/bin/python3 - $DEPLOY" < "$S" > "$F/copy-manifest.json" 2> "$F/copy.err"
rc=$?
echo "ssh rc=$rc"
if [ "$rc" -ne 0 ]; then echo "STOP: the copy exited $rc"; grep -v '^\*\|^$' "$F/copy.err" | tail -5; exit "$rc"; fi
python3 "$S" verify "$F/copy-manifest.json"
vrc=$?
echo "verify rc=$vrc"
shasum -a 256 "$F/copy-manifest.json"
exit "$vrc"
