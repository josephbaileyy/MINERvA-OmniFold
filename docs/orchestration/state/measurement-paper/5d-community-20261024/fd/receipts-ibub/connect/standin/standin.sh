#!/bin/bash
# Stand-in of ibub_run_connect.sh in Debian (as MSR's standin.sh). Stubs: sacct (states from the variant; -j answers
# for the submitted id), sbatch (records its argv, prints an id), scontrol (the job's name, QOS and limit), and git
# clone's URL (a clone of the mounted depth-1 bare repo of the stand-in commit). The inputs are fake bytes at the
# real paths, and the stand-in commit's config pins those bytes.
# Variant ($1): ok | cov2d_running | ibub_running | ibuchi_running | ns_exists | ref_missing | cv_offpin |
#               sbatch_fails | scontrol_mismatch | window | connect_record_exists | qos_regular | qos_other
# In every variant that submits, the sbatch stub writes the batch's own scontrol record first, as a job that starts at
# once would (the batch-first ordering). In connect_record_exists it also plants the connect's own record.
V=${1:?variant}
git config --global --add safe.directory '*'
mkdir -p /stub /root/.conda/envs/root_6_28/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
cat > /stub/git <<'G'
#!/bin/bash
if [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q /hostgit "$dest"; fi
exec /usr/bin/git "$@"
G
C2=COMPLETED; IB=COMPLETED; IC=COMPLETED
[ "$V" = cov2d_running ] && C2=RUNNING
[ "$V" = ibub_running ] && IB=PENDING
[ "$V" = ibuchi_running ] && IC=RUNNING
cat > /stub/sacct <<S2
#!/bin/bash
for a in "\$@"; do [ "\$a" = -j ] && { echo "61900001|ibub_run|PENDING"; exit 0; }; done
echo "61000001|cov2d_g2r|$C2"
echo "61000002|t2a_x|COMPLETED"
echo "61800000|rpd_flux2|COMPLETED"
echo "61800001|msr_build|COMPLETED"
echo "61850000|ibub_run|$IB"
echo "61860000|ibuchi_evloop|$IC"
echo "61870000|unrelated_lane|RUNNING"
S2
SB=0; [ "$V" = sbatch_fails ] && SB=1
PC=0; [ "$V" = connect_record_exists ] && PC=1
cat > /stub/sbatch <<S3
#!/bin/bash
printf '%s\n' "\$@" > /tmp/sbatch.argv
[ $SB = 1 ] && { echo "sbatch: error: stand-in refusal" >&2; exit 1; }
echo "the batch's own record, written first" > /pscratch/sd/j/josephrb/ibub-20261124/logs/scontrol-batch-61900001.txt
[ $PC = 1 ] && echo "planted" > /pscratch/sd/j/josephrb/ibub-20261124/logs/scontrol-connect-61900001.txt
echo 61900001
S3
TL=11:29:00; [ "$V" = scontrol_mismatch ] && TL=12:00:00
Q=regular_1; [ "$V" = qos_regular ] && Q=regular; [ "$V" = qos_other ] && Q=regular_2
cat > /stub/scontrol <<S4
#!/bin/bash
echo "JobId=61900001 JobName=ibub_run"
echo "   UserId=root(0) Priority=1 QOS=$Q JobState=PENDING"   # regular_1 by default: Perlmutter's spelling (receipts-cov2d/a2/bulk/complete/connect-complete-1.log.txt:78)
echo "   RunTime=00:00:00 TimeLimit=$TL TimeMin=N/A"
S4
chmod +x /stub/git /stub/sacct /stub/sbatch /stub/scontrol
export PATH=/stub:$PATH HOME=/root
U=/pscratch/sd/j/josephrb
for f in /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root \
         /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root \
         $U/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so $U/ref-c2c1-20261106/units/c2_central.npz \
         $U/cov2d-2a/writer_control.root; do mkdir -p "$(dirname "$f")"; done
printf 'stand-in CV omnifile\n' > /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
printf 'stand-in MC flux\n' > /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
printf 'stand-in libRooUnfold\n' > $U/MINERvA-OmniFold/unbinned_unfolding/build/libRooUnfold.so
printf 'stand-in c2_central.npz\n' > $U/ref-c2c1-20261106/units/c2_central.npz
printf 'stand-in K2A\n' > $U/cov2d-2a/writer_control.root
mkdir -p $U/cov2d-run-20261104/pseudo/G18/b $U/cov2d-run-20261104/pseudo/AR23-a2/b
for s in $(seq 5720000 5720299); do echo x > $U/cov2d-run-20261104/pseudo/G18/b/data_$s.root; done
for s in $(seq 5730000 5730299); do echo x > $U/cov2d-run-20261104/pseudo/AR23-a2/b/data_$s.root; done
[ "$V" = ns_exists ] && mkdir -p $U/ibub-20261124
[ "$V" = ref_missing ] && rm $U/ref-c2c1-20261106/units/c2_central.npz
[ "$V" = cv_offpin ] && printf 'other bytes\n' > /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
cp /connect/connect.sh /dev/shm/ibubc.1.sh
WEND=$(( $(date +%s) + 900 )); [ "$V" = window ] && WEND=$(( $(date +%s) - 10 ))
bash /dev/shm/ibubc.1.sh /dev/shm/ibubc.1.sh $WEND > /tmp/session.out 2>&1
rc=$?
echo "== variant $V: script rc=$rc; session: $(tr '\n' ' ' < /tmp/session.out | cut -c1-300)"
echo "== self copy left: $(ls /dev/shm/ibubc.1.sh 2>&1 | head -1); shm dir: $(ls -d /dev/shm/ibub-connect 2>&1)"
echo "== the connect log"; cat $U/ibub-20261124/logs/connect-run.log 2>&1 | sed 's/^/  /'
echo "== done: $(cat $U/ibub-20261124/logs/connect-run.done 2>&1)"
echo "== sbatch argv: $(tr '\n' ' ' < /tmp/sbatch.argv 2>&1)"
echo "== stage: $(ls -l $U/ibub-20261124/stage 2>&1 | tail -n +2 | awk '{print $1, $NF}' | tr '\n' ' ')"
echo "== records tar: $(ls -l $U/ibub-20261124/fetch-run.tar 2>&1 | awk '{print $5}')"
echo "== stdout dir: $(stat -c '%a %U %F' $U/ibub-20261124/slurm 2>&1)"
echo "== batch record: $(cat $U/ibub-20261124/logs/scontrol-batch-61900001.txt 2>&1 | head -1)"
echo "== connect record: $(cat $U/ibub-20261124/logs/scontrol-connect-61900001.txt 2>&1 | head -1)"
exit 0
