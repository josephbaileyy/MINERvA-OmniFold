# 5B step 3 (section 2.3; binding condition 3): submit job A once, login node.
set -o pipefail
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; PIN=2c96065956d59b29a1ec0e7c611d52536f92a785; D=$B/deploy/2c960659
[ -e "$B/logs/submit-inputs.out" ] && { echo "STOP: already submitted"; exit 2; }
bash $D/nd-unfolding/submit_fd_ct.sh 5b-inputs $D $PIN $B > $B/logs/submit-inputs.out 2>&1; echo "rc=$?" >> $B/logs/submit-inputs.out
{ date -u +%FT%TZ; hostname; } >> $B/logs/submit-inputs.out
cat $B/logs/submit-inputs.out; cat $B/logs/stage-flux.out; cat $B/control/gate-5b-inputs.out
ls $B; sha256sum $B/flux/*.root
squeue -u josephrb -o "%.12i %.20j %.8T %.10M %.6D %R" | head
