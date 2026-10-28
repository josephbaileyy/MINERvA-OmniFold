# Step 3 (FD-F1-BINDING.md section 4.3): F1b, only on F1a's GO, through the declared helper.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
PIN=5015535e5567c42827e2b618b9b679d534ec47cf
D=$OUT/deploy/5015535e
date -u +%FT%TZ; hostname
grep -o '"decision": "[A-Z]*"' $OUT/f1a/budget.json
bash $D/nd-unfolding/submit_fd_f1.sh f1b $D $PIN $OUT
