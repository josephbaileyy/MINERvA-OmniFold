# 5B step 6 (section 2.5; binding condition 4, after the director's reply): submit job B once, login node.
set -o pipefail
P=/pscratch/sd/j/josephrb; B=$P/fd-ct-5b-20261030; PIN=2c96065956d59b29a1ec0e7c611d52536f92a785; D=$B/deploy/2c960659
[ -e "$B/logs/submit-periods.out" ] && { echo "STOP: already submitted"; exit 2; }
bash $D/nd-unfolding/submit_fd_ct.sh 5b-periods $D $PIN $B > $B/logs/submit-periods.out 2>&1; echo "rc=$?" >> $B/logs/submit-periods.out
{ date -u +%FT%TZ; hostname; } >> $B/logs/submit-periods.out
cat $B/logs/submit-periods.out; cat $B/control/gate-5b-periods.out
squeue -u josephrb -o "%.12i %.20j %.8T %.10M %.6D %R" | head
