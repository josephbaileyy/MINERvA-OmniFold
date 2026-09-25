# s5n Stage 1, allocation 1 of 2 (CPU pool, stage development): controls C0/C2/C4-C5 check/C7/C8, then the
# C3-C5 development grid lines 0-35, 8 steps of 32 CPUs. Run by nd-unfolding/s5c_queue.sh with S5C_NS set to the s5n namespace.
S5C_CAMPAIGN=s5n bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 4 s5n_dev_1 56G "s5n Stage-1 controls C0 C2 C7 C8, truth check, development grid C3-C5 (60 seeds per point)" dev-controls-tasks.tsv:controls:4:0:12,dev-grid-tasks.tsv:grid_a:4:0:17 dev-grid-tasks.tsv:grid_b:4:18:35
