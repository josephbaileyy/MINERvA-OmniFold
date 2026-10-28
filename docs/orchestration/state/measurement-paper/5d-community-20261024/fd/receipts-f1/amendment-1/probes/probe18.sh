W=/pscratch/sd/j/josephrb/fd-f1-20261027/f1b/work/G18_10a_02_11b
for s in 60010 60011 60050; do echo "=== s$s"; ls -la $W/s$s; wc -l $W/s$s/gevgen.log; tail -25 $W/s$s/gevgen.log | cut -c1-220; grep -ciE "bad_alloc|std::|abort|terminate|FATAL|killed|segment" $W/s$s/gevgen.log; grep -iE "bad_alloc|std::|abort|terminate|FATAL|segment" $W/s$s/gevgen.log | head -5 | cut -c1-220; done
echo "=== a finished one for comparison"; tail -5 $W/s60001/gevgen.log | cut -c1-200
