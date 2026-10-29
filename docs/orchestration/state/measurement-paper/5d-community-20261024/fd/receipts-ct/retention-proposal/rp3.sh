P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
sha256sum $P/fd-f0-20261025/fd_f0_experiments.npz $P/fd-f0b-20261026/fd_f0b_experiments.npz $P/cmodel5d-20261024/out/* $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz 2>&1
ls -la $P/r10-20261024/run2 $P/r10-20261024/smoke 2>&1
