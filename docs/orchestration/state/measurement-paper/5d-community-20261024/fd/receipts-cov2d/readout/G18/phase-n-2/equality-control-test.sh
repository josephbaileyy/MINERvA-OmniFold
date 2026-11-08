#!/bin/bash
# the CMP block of connect-n-G18.sh (extracted verbatim) on synthetic variants of the committed null_G18.json / blocks_G18.npz
W=/Users/josephbailey/cov2d-work; T=$W/a4/eqtest2; P=/opt/homebrew/bin/python3.13; M=b1d56e4f08e62983784e34b2278f38a09a68eca0
echo "connect-n-G18.sh $(shasum -a 256 $W/connect-n-G18.sh | cut -c1-64); cmp.py $(shasum -a 256 $T/cmp.py | cut -c1-64); old.json $(shasum -a 256 $T/old.json | cut -c1-64); old.npz $(shasum -a 256 $T/old.npz | cut -c1-64)"
awk '/<<.CMP.$/{f=1;next} /^CMP$/{f=0} f' $W/connect-n-G18.sh | cmp -s - $T/cmp.py && echo "cmp.py = the connect's CMP block"
echo "variants (from mk.py): equal = M_A5 + a new utc; host = login01; nested = null.q_joint + 1e-12; wrongM = 40 zeros; code = code.driverSha256 'x'; extra = a new top-level field; bad.npz = array C08 element 0 + 1"
for c in equal host nested wrongM code extra; do echo "== $c"; $P -B $T/cmp.py $T/$c.json $T/old.json $T/old.npz $T/old.npz $M | grep -E 'NULL-FIELDS|NULL-LEAVES|NULL-EQUALITY'; echo "rc=${PIPESTATUS[0]}"; done
echo "== bad blocks"; $P -B $T/cmp.py $T/equal.json $T/old.json $T/bad.npz $T/old.npz $M | grep -E 'BLOCKS|NULL-EQUALITY'; echo "rc=${PIPESTATUS[0]}"
