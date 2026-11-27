#!/bin/bash
# Stand-in of q0_connect.sh in Debian (python 3.11, numpy, uproot): sacct stubbed, the omnifile replaced by a synthetic
# one at the real path, the cluster interpreter path linked to the container's python. Variant $1:
#   ok         the STAND-IN connect (its embedded extractor pins the synthetic file's sha and count): the full path
#   pin        the REAL connect: the extractor must STOP at the omnifile's sha pin (records still written)
#   out_exists $OUT exists: BAIL before anything is written
#   fenced     sacct shows a running ibub_ job: BAIL
#   window     the window has ended: BAIL
V=${1:?variant}
mkdir -p /stub /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin
ln -sf /usr/local/bin/python3 /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
if [ "$V" = fenced ]; then printf '#!/bin/bash\necho "61911111|ibub_run|RUNNING"\n' > /stub/sacct
else printf '#!/bin/bash\necho "61000001|cov2d_g2r|COMPLETED"\necho "61908135|ibuchi_ana|COMPLETED"\n' > /stub/sacct; fi
chmod +x /stub/sacct; export PATH=/stub:$PATH HOME=/root
U=/pscratch/sd/j/josephrb; N=$U/MINERvA-OmniFold/nd-unfolding
mkdir -p $N && cp /w/omni.root $N/runEventLoopOmniFold_5D_MEFHC.root
[ "$V" = out_exists ] && mkdir -p $U/q0study-20261124
S=/w/q0_connect.standin.sh; [ "$V" = pin ] && S=/w/q0_connect.real.sh
cp $S /dev/shm/q0s.1.sh
WEND=$(( $(date +%s) + 900 )); [ "$V" = window ] && WEND=$(( $(date +%s) - 10 ))
bash /dev/shm/q0s.1.sh /dev/shm/q0s.1.sh $WEND "cov2d,rpd_,ibub_,ibuchi_,d2s0,covfix"
echo "== script rc=$?"
echo "== the connect log"; cat $U/q0study-20261124/logs/connect-q0.log 2>&1 | sed 's/^/  /'
echo "== done: $(cat $U/q0study-20261124/logs/connect-q0.done 2>&1)"; ls $U/q0study-20261124 2>&1 | head
[ -f $U/q0study-20261124/fetch-q0.tar ] && { echo "== tar members"; tar -tf $U/q0study-20261124/fetch-q0.tar; }
ls /dev/shm
