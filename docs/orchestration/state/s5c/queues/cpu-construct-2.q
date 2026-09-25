# s5c CPU construction lane, part 2 (after cpu-construct.q). Run by nd-unfolding/s5c_queue.sh. Steps 56G.
# Sized from the production arm timings (AMENDMENT-20260831-oi177-per-arm-ceilings.md: throw slab 46-70 min,
# block task 86-100 min, split replica ~14.6 min), seven or eight wide. c-comb runs after the last block stage.
# Then the lane joins Tier-S validation.
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu measurement_construction 4 f2_construction_3 56G "F2 construction: c-throw lines 0-20, c-split lines 12-23" c-throw-tasks.tsv:construction/steps_throw:7:0:20 c-split-tasks.tsv:construction/steps_split:1:12:23
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu measurement_construction 4 f2_construction_4 56G "F2 construction: c-throw lines 21-39, c-block lines 0-1" c-throw-tasks.tsv:construction/steps_throw:7:21:39 c-block-tasks.tsv:construction/steps_block:1:0:1
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu measurement_construction 4 f2_construction_5 56G "F2 construction: c-block lines 2-17" c-block-tasks.tsv:construction/steps_block:8:2:17
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu measurement_construction 3 f2_construction_6 56G "F2 construction: c-block lines 18-22, then c-comb" c-block-tasks.tsv:construction/steps_block:5:18:22,c-comb-tasks.tsv:construction/steps_comb:1
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu
