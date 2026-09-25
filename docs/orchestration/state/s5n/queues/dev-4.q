# s5n Stage 1, allocation 4 (GPU pool, stage development; CPU-only steps): signal-only departure diagnostic, 8 unfolds, 4 steps wide.
S5C_CAMPAIGN=s5n bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu development 1 s5n_dev_4 56G "s5n Stage-1 diagnostic: departures signal-only (estimator response without background)" dev-diag2-tasks.tsv:diag2:4:0:7
