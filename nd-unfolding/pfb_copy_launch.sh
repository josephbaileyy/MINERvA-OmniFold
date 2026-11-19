#!/bin/bash
# PILOT-FB's copy connect launcher (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3; revision 2, K1): RS1's 21 A0
# products and the sigma receipt copied, O_NOATIME, into the stage the smoke created. One snapshot, verified at the
# endpoint: the launcher reads pfb_copy_remote.py ONCE into memory, refuses unless that capture's sha256 is SHA, and
# sends that capture over ssh's stdin (saul, then a loginNN). On the login node a fixed bootstrap (BOOT, hex below:
# /usr/bin/python3 -I -S) refuses (exit 10) unless stdin is a pipe or socket and the bytes it reads hash to the SHA on
# its own command line, then executes exactly those bytes with the deploy as their one argument. The laptop's verify
# runs from the same capture. No job and no sbatch; the fence is /usr/bin/sacct only, read before and after; nothing
# is written on the cluster outside the stage's a0-refs/ and assess_receipt.json, and nothing on CFS. The inner ssh
# writes nothing on saul. ssh's rc is read unpiped.
# Usage: bash pfb_copy_launch.sh <new empty dir> <loginNN> <deploy: an absolute /pscratch/sd/j/josephrb/... checkout>
F=${1:?session dir}; NODE=${2:?loginNN}; DEPLOY=${3:?deploy}
HERE=$(cd "$(dirname "$0")" && pwd)
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[[ "$DEPLOY" =~ ^/pscratch/sd/j/josephrb/[A-Za-z0-9._/-]+$ ]] && [[ "$DEPLOY" != *..* ]] \
    || { echo "STOP: the deploy '$DEPLOY' is not an absolute /pscratch/sd/j/josephrb path"; exit 9; }
S="$HERE/pfb_copy_remote.py"; SHA=d2d7043e799794b4f6f0b49a7a6dcba2f0f45a1a293194d1ecec607cce7b8d31
BOOT=696d706f727420686173686c69622c206f732c20737461742c207379730a6d6f6465203d206f732e66737461742830292e73745f6d6f64650a6966206e6f742028737461742e535f49534649464f286d6f646529206f7220737461742e535f4953534f434b286d6f646529293a0a202020207379732e7374646572722e77726974652822626f6f7473747261703a20737464696e206973206e6f7420612070697065206f7220736f636b65745c6e22290a202020207379732e65786974283130290a62203d207379732e737464696e2e6275666665722e7265616428290a696620686173686c69622e7368613235362862292e686578646967657374282920213d207379732e617267765b325d3a0a202020207379732e7374646572722e77726974652822626f6f7473747261703a2074686520726563656976656420736372697074206973206e6f74207468652070696e6e6564206f6e655c6e22290a202020207379732e65786974283130290a7379732e61726776203d205b227066625f636f70795f72656d6f74652e7079222c207379732e617267765b335d5d0a6578656328636f6d70696c6528622c20227066625f636f70795f72656d6f74652e7079222c20226578656322292c207b225f5f6e616d655f5f223a20225f5f6d61696e5f5f222c20225f5f66696c655f5f223a20227066625f636f70795f72656d6f74652e7079227d290a
CAP=$(cat "$S" && printf x) || { echo "STOP: cannot read $S"; exit 8; }
CAP=${CAP%x}
got=$(printf '%s' "$CAP" | shasum -a 256 | cut -d' ' -f1)
[ "$got" = "$SHA" ] || { echo "STOP: the captured copy script is not the approved one (sha256 $got)"; exit 8; }
SSH=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 -o LogLevel=ERROR)
HOP=(-o ControlPath=none -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=8
     -o StrictHostKeyChecking=yes -o UpdateHostKeys=no -o LogLevel=ERROR)
INNER="/usr/bin/python3 -I -S -c 'import sys;exec(bytes.fromhex(sys.argv[1]))' $BOOT $SHA $DEPLOY"
echo "launch $(date -u +%FT%TZ) node $NODE deploy $DEPLOY script sha256 $SHA"
ssh "${SSH[@]}" saul.nersc.gov "ssh ${HOP[*]} $NODE \"$INNER\"" < <(printf '%s' "$CAP") > "$F/copy-manifest.json" 2> "$F/copy.err"
rc=$?
echo "ssh rc=$rc"
if [ "$rc" -ne 0 ]; then echo "STOP: the copy exited $rc"; grep -v '^\*\|^$' "$F/copy.err" | tail -5; exit "$rc"; fi
python3 -I -S - verify "$F/copy-manifest.json" < <(printf '%s' "$CAP")
vrc=$?
echo "verify rc=$vrc"
shasum -a 256 "$F/copy-manifest.json"
exit "$vrc"
