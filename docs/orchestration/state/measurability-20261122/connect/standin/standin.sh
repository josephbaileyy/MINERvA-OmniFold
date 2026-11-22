#!/bin/bash
# Stand-in of msr_probe_connect.sh in Debian. Stubs: sacct (states from the variant) and git clone's URL (a --shared
# clone of the read-only host object store). Inputs are fake bytes at the real paths, so the run stops at the first
# input pin. Variant: $1 = ok | window | cov2d_running | msr_running | out_exists
V=${1:?variant}
git config --global --add safe.directory '*'
mkdir -p /stub /root/.conda/envs/root_6_28/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
cat > /stub/git <<'G'
#!/bin/bash
if [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q --shared /hostgit "$dest"; fi
exec /usr/bin/git "$@"
G
C2=COMPLETED; MS=COMPLETED
[ "$V" = cov2d_running ] && C2=RUNNING
[ "$V" = msr_running ] && MS=PENDING
cat > /stub/sacct <<S2
#!/bin/bash
echo "61000001|cov2d_g2r|$C2"
echo "61000002|t2a_x|COMPLETED"
echo "61731751|t3p_floor|COMPLETED"
echo "61800000|rpd_flux2|RUNNING"
echo "61800001|msr_build|$MS"
S2
chmod +x /stub/git /stub/sacct
export PATH=/stub:$PATH HOME=/root
U=/pscratch/sd/j/josephrb; T3=$U/t3p-20261121
mkdir -p $T3/stage $T3/log-floor $U/ibukt-20261119-d/prep $U/methods-paper/re1-20261022/out/3d $U/methods-paper/re1-20261022/out/4d
for f in $T3/stage/of_inputs_5d.npz $T3/stage/bkg_dump.npz $T3/stage.json $T3/log-floor/SHA256SUMS \
  $U/methods-paper/re1-20261022/out/3d/of_inputs_3d.npz $U/methods-paper/re1-20261022/out/4d/of_inputs_4d.npz \
  $U/ibukt-20261119-d/prep/bank.npz; do echo "stand-in $(basename $f)" > $f; done
[ "$V" = out_exists ] && mkdir -p $U/msr-p-20261122
cp /connect/connect.sh /dev/shm/msrp.1.sh
WEND=$(( $(date +%s) + 900 )); [ "$V" = window ] && WEND=$(( $(date +%s) - 10 ))
bash /dev/shm/msrp.1.sh /dev/shm/msrp.1.sh $WEND "cov2d,ll5d_,ibukt,prr_,e96,ens1_,t3p_"
rc=$?
echo "== script rc=$rc; self copy left: $(ls /dev/shm/msrp.1.sh 2>&1 | head -1); shm dir: $(ls -d /dev/shm/msr-connect 2>&1)"
echo "== the connect log"; cat $U/msr-p-20261122/logs/connect-probe.log 2>&1 | sed 's/^/  /'
echo "== done: $(cat $U/msr-p-20261122/logs/connect-probe.done 2>&1)"
exit 0
