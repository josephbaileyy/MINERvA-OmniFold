# s5n Stage 1, allocation 3 (GPU pool, stage development; CPU-only steps with --gres=none): the prior-matches-truth diagnostic, 4 steps.
S5C_CAMPAIGN=s5n bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" gpu development 1 s5n_dev_3 56G "s5n Stage-1 diagnostic: departures with the prior equal to the truth model (defect vs prior dependence)" dev-diag-tasks.tsv:diag:4:0:3
