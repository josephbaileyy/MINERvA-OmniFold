#!/bin/bash
# Stand-in of msr_build_connect.sh in Debian; stubs as standin.sh (sacct, git clone URL). The probe's staged copies are
# fake bytes, so the run stops at their O_NOATIME re-check. Variant: $1 = ok | out_exists | no_stage
V=${1:?variant}
git config --global --add safe.directory '*'
mkdir -p /stub /root/.conda/envs/root_6_28/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
printf '#!/bin/bash\nif [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q --shared /hostgit "$dest"; fi\nexec /usr/bin/git "$@"\n' > /stub/git
printf '#!/bin/bash\necho "61000001|cov2d_g2r|COMPLETED"\necho "61806073|rpd_flux2|COMPLETED"\n' > /stub/sacct
chmod +x /stub/git /stub/sacct
export PATH=/stub:$PATH HOME=/root
U=/pscratch/sd/j/josephrb; P=$U/msr-p-20261122/stage
mkdir -p $U/t3p-20261121
[ "$V" = no_stage ] || { mkdir -p $P; for f in of_inputs_5d.npz bkg_dump.npz bank.npz; do echo "stand-in $f" > $P/$f; done; }
[ "$V" = out_exists ] && mkdir -p $U/msr-b-20261123
cp /connect/connect-b.sh /dev/shm/msrp.1.sh
WEND=$(( $(date +%s) + 900 ))
bash /dev/shm/msrp.1.sh /dev/shm/msrp.1.sh $WEND "cov2d,ll5d_,ibukt,prr_,e96,ens1_,t3p_"
echo "== script rc=$?"
echo "== the connect log"; cat $U/msr-b-20261123/logs/connect-build.log 2>&1 | sed 's/^/  /'
echo "== done: $(cat $U/msr-b-20261123/logs/connect-build.done 2>&1)"; ls $U/msr-b-20261123 2>&1 | head
