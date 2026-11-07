#!/bin/bash
# Per-period 2D benchmark, CONNECT 3: delete the operand copies under a ledger row (the director's ruling of 2026-11-07,
# after the outcome record is on main). Uploads delete_copies.py to a new path, COMPARES its sha256 on the cluster,
# runs it at nice 19 under /usr/bin/python3 on a login node, and fetches the ledger. 0 node-h.
# Usage: bash connect3.sh <dir holding delete_copies.py> <workdir>. No set -e/-u; every rc read unpiped.
HOST=saul.nersc.gov
SSH=(ssh -o ControlPath=none -o BatchMode=yes "$HOST")
NS=/pscratch/sd/j/josephrb/per-period-benchmark-20261106
C3=$NS/delete-code
SRC=${1:?usage}; W=${2:?usage}
[ -e "$W" ] && { echo "STOP: $W exists"; exit 2; }
mkdir -p "$W" || exit 2
SHA=$(shasum -a 256 "$SRC/delete_copies.py" | awk '{print $1}')
echo "delete_copies.py sha256 $SHA" | tee "$W/connect3.log"
"${SSH[@]}" "test ! -e $C3 && mkdir -p $C3 && cat > $C3/delete_copies.py" < "$SRC/delete_copies.py" >>"$W/connect3.log" 2>&1; rc=$?
[ $rc -eq 0 ] || { echo "STOP: upload rc $rc" | tee -a "$W/connect3.log"; exit 4; }
"${SSH[@]}" bash -s > "$W/remote3.out" 2>&1 <<REMOTE
got=\$(sha256sum $C3/delete_copies.py | awk '{print \$1}')
echo "on \$(hostname): delete_copies.py sha256 \$got"
[ "\$got" = "$SHA" ] || { echo "STOP: uploaded digest differs"; exit 11; }
nice -n 19 /usr/bin/python3 -B $C3/delete_copies.py; rc=\$?
echo "delete_copies rc \$rc"
exit \$rc
REMOTE
rrc=$?
cat "$W/remote3.out" | tee -a "$W/connect3.log"
"${SSH[@]}" "tar -C $NS -cf - delete-ledger" > "$W/ledger.tar" 2>>"$W/connect3.log"; frc=$?
[ $frc -eq 0 ] && mkdir -p "$W/receipt" && tar -xf "$W/ledger.tar" -C "$W/receipt"
echo "remote rc $rrc; fetch rc $frc" | tee -a "$W/connect3.log"
exit $rrc
