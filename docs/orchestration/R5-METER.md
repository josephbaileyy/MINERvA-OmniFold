# R5 spend meter

`r5_meter.py` measures cumulative GPU and CPU task-hours from the R5 decision's t0. It sums
the post-t0 portion of `ElapsedRaw` once per eligible Slurm task identity, including failed and
running work. A task that straddles t0 is clipped at t0, while one that ended at or before t0 is
excluded. A task is classified as GPU work when `AllocTRES` contains a positive `gres/gpu` count,
including typed entries such as `gres/gpu:a100=1`, or when its partition starts with `gpu` as a
secondary signal. CPU cores attached to a GPU allocation are not also charged as CPU task-hours.
The meter also enforces the inclusive date and spend boundaries.

On Perlmutter, query accounting in UTC and atomically refresh the default receipt:

```bash
python3 docs/orchestration/r5_meter.py measure \
  --write docs/orchestration/state/r5-meter-receipt.json
```

Before a proposed run, declare its maximum GPU and CPU task-hour costs and check the boundary:

```bash
python3 docs/orchestration/r5_meter.py check \
  --gpu-task-hours 12 \
  --cpu-task-hours 8
```

A missing, malformed, or older-than-24-hours receipt fails closed and is treated as a stop. A copied
cluster dump can be measured elsewhere with `measure --from-file PATH`.

The meter authorizes nothing. R5 is a prohibition and an accounting boundary; every run still needs
its own declaration and authorization.
