# s5c CPU construction lane. Run by nd-unfolding/s5c_queue.sh. Steps 56G (8 x 56G fits the 476 GiB node).
# The sweep runs 7 wide beside one track of stab probes (boot, sweep, throw, split) then split replicas 0-11.
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu measurement_construction 4 f2_construction_2 56G "F2 construction: c-sweep lines 40-168, c-stab lines 0-3, c-split lines 0-11" c-sweep-tasks.tsv:construction/steps_sweep2:7:40:168 c-stab-tasks.tsv:construction/steps_stab:1:0:3,c-split-tasks.tsv:construction/steps_split:1:0:11
