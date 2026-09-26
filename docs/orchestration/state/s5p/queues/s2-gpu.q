# s5p Stage 2 (amendment 2), GPU lane: CPU-only steps on one GPU node (--gres=none). Run with S5C_NS=/pscratch/sd/j/josephrb/s5p-20260926.
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu development 4.0 s5p_s2_num_g 56G "s5p study N3: numerical and bootstrap overlap on the GiBUU departure pseudo 931000" s2-num-tasks.tsv:s2/num-logs-g:4:25:35
