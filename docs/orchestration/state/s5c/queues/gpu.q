# s5c GPU lane (one 4-GPU node at a time; the plan caps GPU concurrency at 4). Run by nd-unfolding/s5c_queue.sh.
# 1-2: construction steps that need ~70G (detector/lateral/central driver unfolds hit a 60G cap on 58857791),
#      three at a time (224 GiB node), steps without GPUs. Then Tier-S validation claims (s5c_valid_next.sh,
#      16 lines per node); the meter refuses past the measurement_tier_s GPU stage allocation.
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu measurement_construction 3 f2_construction_det3_lat1 70G "F2 construction: c-det lines 5-8, c-lat lines 0-4" c-det-tasks.tsv:construction/steps_det3:1:5:7 c-det-tasks.tsv:construction/steps_det3:1:8:8,c-lat-tasks.tsv:construction/steps_lat:1:0:1 c-lat-tasks.tsv:construction/steps_lat:1:2:4
bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu measurement_construction 3 f2_construction_lat2_stab 70G "F2 construction: c-lat lines 5-9, c-central, c-stab lines 4-5" c-lat-tasks.tsv:construction/steps_lat:1:5:7 c-lat-tasks.tsv:construction/steps_lat:1:8:9,c-central-tasks.tsv:construction/steps_central:1 c-stab-tasks.tsv:construction/steps_stab:1:4:5
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_next.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu
