# s5c CPU Tier-S validation lane. Run by nd-unfolding/s5c_queue.sh. Lines 0-119 are the first 400 seeds of
# every grid point (the table interleaves the three points), which the futility look needs.
# Line 1 holds the lane until allocation 58861566 (lines 0-31) ends, so the construction lane takes the
# slot that construction allocation 58857523 frees.
while :; do ids=$(squeue -h --me -o %i) || { sleep 60; continue; }; echo "$ids" | grep -qx 58861566 || break; sleep 60; done
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 32 63
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 64 95
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 96 127
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 128 159
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 160 191
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 192 223
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 224 255
bash "$S5C_DEPLOY/nd-unfolding/s5c_valid_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu 256 287
