# s5p Stage 2 (amendment 2), CPU lane, CORRECTIVE RESUBMISSION (the one permitted for these tables): the abdc88c5 table passed
# --pairs values beginning with '-' as a separate argv token, which argparse read as an option (rc 2 before any unfold;
# allocation 58904837). Repaired as --pairs=<value> at 8af5d746. The GPU lane (s2-gpu-r.q) is NOT used: the interactive QOS
# refused a second allocation (QOSMaxSubmitJobPerUserLimit, MaxSubmitPU 2). Waits for 58904837 (lane A) to leave the queue
# (2-node concurrency: the two pending shared arrays already reserve 1.0 node), then
#   B = C1 (36-51), C3 (62-65) and the failed N1 control/jitter lines 0-3 and N2 base/jitter lines 14-16;
#   C = C2 (52-61), C4 (66-70) and N3 (25-35).
while squeue -h -j 58904837 2>/dev/null | grep -q .; do sleep 60; done; echo "58904837 left the queue"
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 4.0 s5p_s2_num_b 56G "s5p study C1/C3 and the N1/N2 control and jitter lines" s2-num-tasks.tsv:s2/num-logs-b:4:36:51 s2-num-tasks.tsv:s2/num-logs-b2:1:62:65 s2-num-tasks.tsv:s2/num-logs-b3:2:0:3 s2-num-tasks.tsv:s2/num-logs-b4:1:14:16
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 4.0 s5p_s2_num_c 56G "s5p study C2 (nominal ensemble), C4 (W3 departure bootstrap) and N3 (GiBUU pseudo 931000)" s2-num-tasks.tsv:s2/num-logs-c:3:52:61 s2-num-tasks.tsv:s2/num-logs-c2:1:66:70 s2-num-tasks.tsv:s2/num-logs-c3:4:25:35
