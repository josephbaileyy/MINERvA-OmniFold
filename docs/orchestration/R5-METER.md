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

On Perlmutter, query accounting in UTC. `measure` on its own writes nothing and prints the receipt:

```bash
python3 docs/orchestration/r5_meter.py measure
python3 docs/orchestration/r5_meter.py measure --write /tmp/r5-receipt-check.json
```

**Use one of those two forms to verify the meter.** `--write` has no default, so neither can arm
anything. To read the boundary against whatever receipt is committed:

Before a proposed run, declare its maximum GPU and CPU task-hour costs and check the boundary
(`--receipt` defaults to the committed receipt path; with no receipt there, this fails closed at
exit 4, which is the correct shut):

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

## Writing the receipt to `state/` arms compute admission

`campaignctl` admits a compute item only against an R5 receipt **committed** at
`docs/orchestration/state/r5-meter-receipt.json`. There is no such file today, so every compute item
is refused. Writing a valid receipt there and committing it does not merely record a measurement —
**it opens compute admission for the whole queue**, for the 24 hours until the receipt goes stale.

That is a deliberate decision with its own weight, and it is two ordinary-looking commands away:

```bash
# THIS ARMS COMPUTE ADMISSION QUEUE-WIDE. It is not a smoke test and not routine hygiene.
python3 docs/orchestration/r5_meter.py measure \
  --write docs/orchestration/state/r5-meter-receipt.json
git add docs/orchestration/state && git commit
```

Neither step announces itself. Nothing ignores that path (`git check-ignore` finds no rule), and
`docs/orchestration/state/` already holds 150 tracked `.json` files, so committing the directory is
the norm — a `git add -A` completes the arming. **The person most at risk is a careful reviewer
following this runbook to confirm the meter works.** Verify with the two forms above instead, and do
not commit `docs/orchestration/state/` afterwards without looking at what is in it.

The receipt expires 24 hours after its `measured_at_utc`, not after its commit, so an accidental
arming heals itself within a day. It heals the receipt; it does not heal the jobs that ran under it.
The commit is reversible. The compute is not.

The meter **authorizes** nothing: R5 is a prohibition and an accounting boundary, and every run still
needs its own declaration and authorization. That is a statement about authorization and it is
**silent about admission**, which is the one thing a committed receipt does control. Do not read the
first sentence as covering the second.
