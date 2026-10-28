# Poll step 1 (read-only): print its stamps, and when it has ended, the deploy log and the test summary.
B=/pscratch/sd/j/josephrb/fd-flux-boot-20261028
cat $B/logs/s1.stamps 2>&1
if grep -q "s1 end" $B/logs/s1.stamps 2>/dev/null; then cat $B/logs/deploy.log; grep -E "^Ran |^OK|^FAILED|^FAIL:|^ERROR:" $B/logs/deploy-tests.log; fi
