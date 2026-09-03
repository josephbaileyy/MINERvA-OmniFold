# R5 spend meter

`r5_meter.py` measures cumulative GPU and CPU task-hours from the R5 decision's t0. It sums
`ElapsedRaw` once per eligible Slurm task identity, including failed and running work, and separates
the two columns by partition name. It also enforces the inclusive date and spend boundaries.

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
