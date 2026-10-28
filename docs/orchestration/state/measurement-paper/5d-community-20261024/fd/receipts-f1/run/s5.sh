# Step 5 (FD-F1-BINDING-AMENDMENT-1.md section 4.2): submit F1a', the re-pilot, with the bound prices.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
PIN=4b7a9892ef4d739afc45f6bfb6cc5f8d7a36fe54
D2=$OUT/deploy/4b7a9892
date -u +%FT%TZ; hostname
bash $D2/nd-unfolding/submit_fd_f1.sh f1a2 $D2 $PIN $OUT 2.0 2.5
