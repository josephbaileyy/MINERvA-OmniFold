W=/pscratch/sd/j/josephrb/fd-f1-20261027/f1b/work/G18_10a_02_11b
for s in 60010 60011 60050 60001; do echo "=== s$s"; stat -c '%y %n' $W/s$s/genie-mcjob-$s.status $W/s$s/gevgen.log; grep -iE "event|current|number|time" $W/s$s/genie-mcjob-$s.status | head -8; done
L=/pscratch/sd/j/josephrb/fd-f1-20261027/f1b/logs
for s in 60010 60011 60050; do echo "--- task log s$s"; cat $L/gen_G18_10a_02_11b_s$s.log | tail -4; done
grep -c "Killed" $L/gen_*.log | awk -F: '$2>0' | wc -l
stat -c '%y' /pscratch/sd/j/josephrb/fd-f1-20261027/logs/fd_f1b_60417614.out
