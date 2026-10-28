# Step 8 (FD-F1-BINDING-AMENDMENT-2.md section 4.2): F1b', by the bound submit stage only. The stage itself refuses
# unless the re-pilot is FAILED|3:0 with batch MaxRSS <= 75 % of the node, runs fd_f1_budget3.py on the deploy's
# committed records, and submits only on GO with budget3.json's time limit.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
PIN=5f5e392c4be9c6f8bb035a72d4a60f7dd8be8803
D3=$OUT/deploy/5f5e392c
date -u +%FT%TZ; hostname
bash $D3/nd-unfolding/submit_fd_f1.sh f1b3 $D3 $PIN $OUT 2.0 2.5; echo "submit rc=$?"
cat $OUT/gate3/budget3.log 2>/dev/null
