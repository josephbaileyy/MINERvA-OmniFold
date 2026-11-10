#!/bin/bash
# T2B's fetch, the Mac side (T2-BINDING-1.md ruling 3). One ssh session: it enters at saul.nersc.gov and hops to NODE;
# stdin carries t2b_fetch_remote.sh through both hops; on NODE the /dev/shm copy's sha256 must equal the approved one,
# or NODE deletes it and exits 8 before anything runs. The tar comes back on stdout into a new empty directory; ssh's
# rc is read unpiped. Then, locally, under python -I: the tar must hold exactly the five declared basenames as regular
# files; each member's bytes are written to <dir>/files/<its declared name> (never by tar path, no links), and each
# file's sha256 is checked against the declaration's table. Any
# mismatch or a non-zero remote rc: the unpacked files are deleted and the run exits non-zero.
# Usage: bash t2b_fetch.sh <new empty dir> <login node, e.g. login27>
F=${1:?new empty dir}; NODE=${2:?login node}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/t2b_fetch_remote.sh"; SHA=b407d055376cdf473598146c847f445e9353fda588e60c41b3613018fd666034
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local remote-half script is not the approved one"; exit 8; }
R="f=/dev/shm/t2b-fetch.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\" >&2; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\" >&2; bash \"\$f\" \"\$f\"; r=\$?; echo \"script rc=\$r\" >&2; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/fetch.tar" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
cat "$F/session.err"
shasum -a 256 "$F/fetch.tar"
[ $rc = 0 ] || { echo "STOP: the remote half exited $rc; nothing is unpacked"; exit $rc; }
mkdir "$F/files" || exit 9
cd "$F" || exit 9
/usr/bin/python3 -I - fetch.tar files <<'PY'
import hashlib, sys, tarfile
from pathlib import Path
want = {
    "s1_assembly.npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
    "cmodel_5d.npz": "3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882",
    "cresp.npz": "4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a",
    "fd_f1_experiments.npz": "997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc",
    "fd_f0b_experiments.npz": "7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9",
}
def want_name(n, want):
    if n not in want:
        raise SystemExit(f"STOP: unexpected member {n!r}")
    return n
tar, dest = sys.argv[1], Path(sys.argv[2])
with tarfile.open(tar, "r:") as tf:
    members = tf.getmembers()
    names = [m.name for m in members]
    if sorted(names) != sorted(want) or not all(m.isreg() for m in members):
        print(f"STOP: the tar holds {names}, not the five declared regular files"); sys.exit(7)
    for m in members:          # names are exactly the five declared basenames: written by name, never by tar path
        (dest / want_name(m.name, want)).write_bytes(tf.extractfile(m).read())
bad = 0
for n, s in want.items():
    got = hashlib.sha256((dest / n).read_bytes()).hexdigest()
    print(f"{'OK ' if got == s else 'BAD'} {n} {got}")
    bad += got != s
sys.exit(7 if bad else 0)
PY
v=$?
if [ $v != 0 ]; then rm -rf -- "$F/files"; echo "STOP: the fetched files are not the declared ones (rc $v); removed"; exit $v; fi
echo "T2B-FETCH OK"
exit 0
