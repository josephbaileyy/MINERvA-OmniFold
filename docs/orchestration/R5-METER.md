# R5 spend meter

`r5_meter.py` measures cumulative GPU and CPU task-hours from the R5 decision's t0 and enforces the
inclusive date and spend boundaries.

## The metered unit is an execution attempt

A requeued job keeps one `JobID` and runs many times, and each run burns real wall time on a real
node. The meter therefore charges **execution attempts**, and `sacct` is queried with `-X -D`
(`--allocations --duplicates`); without `--duplicates` Slurm returns only a requeued job's most
recent record.

- **An attempt is `(JobID, Start, End)`.** With this field list `Start` is the only attempt
  discriminator `sacct` returns; `End` is carried too so a same-start/different-end pair cannot
  collapse. `ElapsedRaw` on those rows is per-attempt, not cumulative.
- **Attempts are summed.** R5 §3 counts a retried task "in full" and says "a failed task spends", so
  every attempt of one job id is added. "Distinct task identities" in §3's unit stops the several
  *representations* of one execution being counted twice; it does not collapse several distinct
  *executions* of one job id.
- **What is deduplicated.** Two rows agreeing on all three fields are one observation of one attempt
  and are charged once. `.batch`, `.extern`, numbered steps and array-bracket summary rows
  (`123_[1-100]`) are excluded outright — a step row is a representation, never an attempt. A row
  whose `Start` is `Unknown` (a PENDING job) is skipped.
- **What fails closed.** Two observations of one attempt that disagree about `ElapsedRaw` or about
  GPU classification raise `MeterError` naming the job id and the field. A `schema_version` 1
  receipt is refused. A missing, malformed, or older-than-24-hours receipt is treated as a stop.

The t0 rules apply **per attempt**, not per job: an attempt straddling t0 is clipped at t0, one that
ended at or before t0 is excluded, and the later attempts of that same job id are still charged in
full. An attempt is GPU work when `AllocTRES` holds a positive `gres/gpu` count, including typed
entries such as `gres/gpu:a100=1`, or when its partition starts with `gpu` as a secondary signal;
attempts of one job id may differ here, because a requeue can land elsewhere. CPU cores attached to
a GPU allocation are not also charged as CPU task-hours.

## The receipt

`schema_version` is **2**. `spend` reports both identities:

| field | question it answers |
|---|---|
| `task_count`, `metered_task_ids` | which SCHEDULER TASKS were counted — bare job ids, `^[0-9]+(?:_[0-9]+)?$` |
| `attempt_count`, `attempts_by_task_id` | how many EXECUTION ATTEMPTS were charged, in total and per task id |
| `gpu_task_hours`, `cpu_task_hours` | the summed charge |
| `by_state` | attempts per Slurm state, so it sums to `attempt_count` |

`campaignctl.py`'s reservation release compares a producer's declared ids against
`metered_task_ids` and never consults `attempts_by_task_id`: one job id may carry many attempts, and
an item must not become releasable because its job requeued.

**A version-1 receipt is refused, not migrated.** It counted at most one attempt per job id, so it
under-counts every requeued job — an under-count against a prohibition. Both `r5_meter.py` and
`campaignctl.py` refuse it with a message that says so. Re-measure.

## Use

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

A copied cluster dump can be measured elsewhere with `measure --from-file PATH`.

NERSC refuses any `sacct` window wider than 30 days. `measure` queries t0 → now, so its span crosses
30 days at **2026-10-02T13:44:27Z**, which is after the R5 stop date; from that instant `sacct`
errors and the meter fails closed. The final measurement of jobs still running at the stop must be
taken before it — see `FINDING-20260906-r5-meter-undercounted-requeue-attempts.md`.

The meter authorizes nothing. R5 is a prohibition and an accounting boundary; every run still needs
its own declaration and authorization.
