#!/bin/bash
# GENCMP amendment E: HPSS copy of both runs and C-R (binding ruling 6), deploy clones excluded (git holds them).
B=/pscratch/sd/j/josephrb/gencmp-e-20261101
H=$B/rerun1/hpss
D=/home/j/josephrb/mnv-gencmp-e-20261101
T=$D/gencmp-e-20261101.tar
mkdir -p $H || exit 2
hpssquota > $H/quota-before.txt 2>&1
cd /pscratch/sd/j/josephrb || exit 2
find gencmp-e-20261101 -type f -not -path "*/deploy/*" -not -path "gencmp-e-20261101/rerun1/hpss/*" | sort > $H/htar_files.txt
wc -l < $H/htar_files.txt
hsi -q "mkdir -p $D" 2>&1 | tail -2
htar -Hcrc -Hverify=1 -cvf $T -L $H/htar_files.txt > $H/htar.log 2>&1; echo "htar rc=$?"; tail -2 $H/htar.log
hsi -q "hashcreate $T" > $H/hashcreate.log 2>&1; echo "hashcreate rc=$?"
hsi -q "hashverify $T" > $H/hashverify.log 2>&1; echo "hashverify rc=$?"; tail -2 $H/hashverify.log
hsi -q "ls -l $T $T.idx" 2>&1 | tail -3
mkdir -p $H/retrieve && cd $H/retrieve || exit 2
F="gencmp-e-20261101/c-r/overlap_refined.json gencmp-e-20261101/rerun1/chain/chain.json gencmp-e-20261101/rerun1/chain/chdefs/with/readout/fd_g_readout.json gencmp-e-20261101/rerun1/pred/SHA256SUMS gencmp-e-20261101/chain/chain.json"
htar -xf $T $F > $H/retrieve.log 2>&1; echo "retrieve rc=$?"
for f in $F; do a=$(sha256sum $f | cut -c1-64); b=$(sha256sum /pscratch/sd/j/josephrb/$f | cut -c1-64); [ "$a" = "$b" ] && echo "same $f" || echo "DIFF $f"; done
cd $H && rm -rf retrieve
hpssquota > $H/quota-after.txt 2>&1
echo end
