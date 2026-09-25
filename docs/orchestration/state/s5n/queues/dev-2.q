# s5n Stage 1, allocation 2 of 2 (CPU pool, stage development): control C6, the 200-replica bootstrap of development
# experiment nominal/349999 under the repaired resampling, 8 steps of 32 CPUs.
S5C_CAMPAIGN=s5n bash "$S5C_DEPLOY/nd-unfolding/s5c_launch.sh" "$S5C_DEPLOY" "$S5C_PIN" cpu development 3.5 s5n_dev_2 56G "s5n Stage-1 control C6: bootstrap sigma of development experiment nominal 349999" dev-sigma-tasks.tsv:sigma:8:0:15
