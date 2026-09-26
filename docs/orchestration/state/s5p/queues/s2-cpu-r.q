# s5p Stage 2 (amendment 2), CPU lane, CORRECTIVE RESUBMISSION (see s2-gpu-r.q). Waits for allocation 58904837 (lane A) to leave
# the queue (the 2-node concurrency), then: B = C1 (36-51), C3 (62-65) and the failed N1 control/jitter lines 0-3; C = C2 (52-61), C4 (66-70).
while squeue -h -j 58904837 2>/dev/null | grep -q .; do sleep 60; done; echo "58904837 left the queue"
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 4.0 s5p_s2_num_b 56G "s5p study C1/C3 and the N1 data control/jitter lines" s2-num-tasks.tsv:s2/num-logs-b:5:36:51 s2-num-tasks.tsv:s2/num-logs-b2:1:62:65 s2-num-tasks.tsv:s2/num-logs-b3:2:0:3
S5C_CAMPAIGN=s5p bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 4.0 s5p_s2_num_c 56G "s5p study C2 (nominal ensemble) and C4 (W3 departure bootstrap)" s2-num-tasks.tsv:s2/num-logs-c:6:52:61 s2-num-tasks.tsv:s2/num-logs-c2:2:66:70
