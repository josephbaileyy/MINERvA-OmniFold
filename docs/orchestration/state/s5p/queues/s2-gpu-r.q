# NOT USED (see s2-cpu-r.q): the interactive QOS refused a second allocation. # s5p Stage 2 (amendment 2), GPU lane, CORRECTIVE RESUBMISSION (the one permitted for these tables): the abdc88c5 table passed
# --pairs values beginning with '-' as a separate argv token, which argparse read as an option (rc 2 before any unfold;
# allocation 58904837). Repaired as --pairs=<value>. This lane: N3 (lines 25-35) and the failed N2 base/jitter lines 14-16.
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu development 4.0 s5p_s2_num_g 56G "s5p study N3 (GiBUU pseudo 931000) and the N2 base/jitter lines" s2-num-tasks.tsv:s2/num-logs-g:4:25:35,s2-num-tasks.tsv:s2/num-logs-g2:4:14:16
