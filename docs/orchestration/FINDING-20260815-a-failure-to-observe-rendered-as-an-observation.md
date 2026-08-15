# A failure to observe, rendered as an observation — and it was the ELSE branch

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-323`, block `320-329`). Raised by the
mediator after a fictional scheduling constraint reached Joseph. **Rendering fix authorized by the
mediator and applied**; the falsifying `sacct` rows below were re-measured in this session rather than
taken from the report.

## 1. The defect: `ACTIVE` was the fallthrough of a three-way classification

`slurm_array_status.py:173-179`, before this change:

```python
if error_tasks:
    overall = "ERROR"
elif complete == len(tasks):
    overall = "COMPLETE"
else:
    overall = "ACTIVE"        # <- everything else, including "we could not look"
```

**This is not a mapping rule from `UNKNOWN` to `ACTIVE`. It is worse: `ACTIVE` is what is left over.**
`UNKNOWN` is explicitly excluded from the error branch (`elif state not in ACTIVE_STATES and state !=
"UNKNOWN"`), so an unobservable task raises no error, is not complete, and lands in the same bucket as a
task positively seen `RUNNING`. **"Looked and saw running" and "could not look" were the same
classification.**

## 2. The falsifying measurement, re-run here

Read-only `ssh` to NERSC, `sacct` only — no `sbatch`, `scancel` or `scontrol`:

```
56863958_2|COMPLETED|0:0|03:15:09|2026-08-13T14:08:51
56863958_3|COMPLETED|0:0|03:15:26|2026-08-13T14:16:55
56863958_4|COMPLETED|0:0|03:12:35|2026-08-13T18:35:57
56863958_5|COMPLETED|0:0|03:17:24|2026-08-14T09:02:08
```

**Leg F terminated at `2026-08-14T09:02:08`** — over 24 hours before the snapshot that called it
`ACTIVE`. It matches the mediator's paste, which is stated because independently derived agreement is the
thing `BEN-300` says to check for.

## 3. Answer to "does this affect other rows": IT IS THE WHOLE TABLE

Both other jobs measured the same way:

```
56936015  ->  50 tasks, all COMPLETED 0:0
56936016  ->  COMPLETED 0:0, ended 2026-08-14T07:31:33
```

**All three rows of the compute table were rendered `ACTIVE`, and all three jobs are long terminal.** Not
one bad row — **zero of the three states in that table were observations.**

## 4. Answer to "can the generator reach Slurm at all": NO, NOT FROM HERE

```
$ which sacct squeue scontrol sbatch
sacct not found
squeue not found
scontrol not found
sbatch not found
```

There are no Slurm binaries on this host. So `runner([...])` raises `OSError`, both `queue_text` and
`acct_text` are `""`, every task parses `UNKNOWN` with `reason: not-visible`, and the else-branch fires.

**Therefore the compute table has never been evidence when generated from a developer machine, and it
never could have been.** It is not a live view that went stale; it is a rendering of "no data" that has
always read as a state. **That is the finding's most durable half**, and it is why the fix includes a
table-level warning rather than only a per-row one.

## 5. The evidence of non-observation was captured, and then discarded

`build_snapshot` returns `observer_errors` — here, `squeue:[Errno 2] No such file or directory: 'squeue'`
and the same for `sacct` — and `unknown_tasks`. **The renderer used neither.** Its Errors column printed
`error_tasks` only, which is empty in exactly this case, so the cell read `none`.

**So the one artifact proving Slurm was never reached existed in the snapshot dict and was dropped one
function later.** This is `BEN-322`'s shape one layer up: there the guard's accounting had **no cell** for
what it could not see; here the cell exists, is populated correctly, and is not rendered.

**And the row printed its own refutation:**

```
| `56863958_[2-5]` | **ACTIVE**: UNKNOWN=4 | none | ? CPU, ?, ?; ? batch array |
```

`**ACTIVE**: UNKNOWN=4` is self-contradicting on one line. **The bold word is what a scanning reader
takes, and the qualifier that negates it is unbolded two characters later.** Likewise `? CPU, ?, ?`
renders absence as tabular data. A format that puts the claim in bold and the reason to disbelieve it in
plain text will be read as the claim.

## 6. What it cost, including my own share

The `OI-124` peer reported Leg F running while costing a Gate-5 re-issue; the mediator relayed it; the
`Assistant` lane built *"re-issue the dataloader binding after Leg F terminates"* on it; the mediator
carried that to Joseph as a scheduling constraint on a **~39 GPU-h** experiment. **The constraint was
fictional and four parties propagated it.**

**My part, stated because a finding that only indicts others is a suppressor.** I wrote, in `BEN-322`'s
report: *"Leg F's liveness is quoted from the control plane's job list, not measured; no cluster command
was run."* That was correct provenance and it was **not enough** — I had `ssh sacct` available, it cost
one command, and I flagged the gap instead of closing it. **Labelling a claim unverified is cheaper than
verifying it and does not substitute for it.** The mediator passed the caveat on; I had already decided
not to spend the command. Both failures were needed.

## 7. Fresh and wrong — the irony is structural, not incidental

`LIVE-STATE.md` is the file `CLAUDE.md` routes every session to **first**, and it carries a freshness
test in its own header. At the moment it asserted Leg F was ACTIVE it was **`FRESH :: Git == HEAD`**.

**Freshness and truth are different properties, and the header already knows this for one field and not
for the other.** `--check-freshness` prints:

> `NOTE: regeneration fixes the sha and timestamp; it does NOT revalidate 'Declared state', which is
> authored prose the generator carries forward.`

That warning is scoped to `Declared state` — the **hand-authored** part. The compute table is the part a
reader trusts *because* it looks machine-derived, and nothing warned that it can be machine-derived from
nothing. **The most-trusted region of the file was the least-caveated.**

## 8. A test asserted the defect, and its name stated the right principle

`test_missing_is_active_unknown_not_false_terminal` demanded `overall == "ACTIVE"` for a task nothing
could see. **Its intent was correct**: an unobserved task must not be reported terminal, because a false
*"done"* licenses reading a result. **`ACTIVE` was the wrong safe side** — it defends against a false
terminal by asserting a false liveness, and that is the hazard that fired.

The test is **rewritten, not deleted**, asserting the intent (`!= COMPLETE`) *and* the defect it permitted
(`!= ACTIVE`), with the old assertion recorded in its docstring. **A test can pin a defect while its name
states a correct principle** — and it will be read as ratifying the behaviour it happens to assert.

## 9. What was changed

* **`slurm_array_status.py`** — `ACTIVE` now requires **positive evidence** (`any(state in
  ACTIVE_STATES)`); unknowns with no positive evidence give a new **`UNOBSERVED`**. `ERROR` and `COMPLETE`
  keep precedence. Partial visibility (some `COMPLETED`, some `UNKNOWN` — `BEN-229`'s split-array trap) is
  `UNOBSERVED`, not `ACTIVE`, because a task invisible to `sacct` is not thereby running.
* **`generate_live_state.py`** — an `UNOBSERVED` row renders as **`STATE UNAVAILABLE — NOT A LIVENESS
  CLAIM`**, its Errors cell carries the `observer_errors` verbatim, and its resources read `declared (not
  observed):`. **Chosen over a bare `UNKNOWN` state deliberately:** `UNKNOWN` is a word a reader can skim
  past, and the failure mode here was precisely skimming. The cell must be unusable as a liveness claim.
* **A table-level warning** above the compute table whenever any row is unobserved, because a per-row
  caveat is read *after* the eye has taken the bolded state.
* **Tests** — 7 added, plus the rewrite. Includes a **power test that re-implements the pre-fix
  classification and asserts it reproduces `ACTIVE`**, so this suite is known to be able to fail rather
  than assumed to; and a true-positive test that one observed `RUNNING` task still yields `ACTIVE`, so the
  fix is not just uniformly pessimistic. `18 tests OK` across
  `test_slurm_array_status` + `test_generate_live_state`.

**Two pre-existing failures in `test_watch_slurm_array_resume.py` are NOT from this change** — they
preflight `$MNV_REPO/docs/orchestration/slurm_array_status.py` under `/pscratch`, which does not exist on
this host. **Verified by running that suite at `HEAD` in a clean throwaway `git worktree`: the same 2
failures.** Recorded rather than left for the next reader to attribute to this commit.

## 10. What this does not do

* **It does not make the table evidence.** On a host without Slurm it now says so, loudly. Making it a
  live view requires regenerating **from a host that can reach Slurm**, and nothing here does that.
* **It does not audit the wake/waker table** or the usage-gate rows for the same pattern; only the compute
  table was examined.
* **It does not change any physics, receipt or verified number**, and it reclassifies none — it is a
  classification-and-display change to a generated artifact.
* **`UNOBSERVED` is a new token, and there ARE two machine consumers that branch on `overall`.** Both were
  traced rather than assumed, and in both the new token is **behaviour-identical to the old `ACTIVE`
  path for an unobserved job**:
  * `watch_slurm_array_resume.sh:85-95` — a `case` whose `ACTIVE` arm increments `unreliable` when
    `observer_errors > 0 || unknown_tasks > 0`, and whose `*)` default increments it unconditionally.
    `UNOBSERVED` falls to `*)` and increments. Same count, same escalation to
    `slurm-array-monitor-error`.
  * `wakerctl.py:440-446` — after `COMPLETE`/`ERROR` it tests
    `if snapshot.get("observer_errors") or snapshot.get("unknown_tasks"): return unreliable_step()`.
    `UNOBSERVED` is only set when `unknown_tasks` is non-empty, so it takes that branch, as `ACTIVE` did.

  **`schema_version` was therefore not bumped — but the reason that matters is the opposite of "no
  consumers": the machine consumers were already written to DISTRUST `overall` and gate on
  `observer_errors`/`unknown_tasks` instead.** The evidence fields were there, and two of three consumers
  used them. **Only the human-facing generator trusted `overall`** — so this was never a missing-data
  problem, it was a rendering that ignored data its own siblings relied on.

* **A correction to this finding's own method, recorded because it is the same class as the defect.** The
  bullet above first read *"no consumer was found that branches on `overall`"*, on the strength of a
  `grep` I piped through `head -15`. **The truncation dropped both real consumers** — the 15 shown hits
  were unrelated `overall_ratio`/`overall scale` matches from `2d-unfolding/` and `nd-unfolding/`. That is
  `BEN-026` (*never truncate a diagnostic at read time*) applied to my own search, and it would have put a
  false claim into a finding whose subject is tools asserting states they do not have. **Caught by
  grepping the two known consumers by name instead of trusting a truncated sweep.** Third instrument of
  mine to misreport today, after the `| tail` exit code and the `split('|')` cell counter.
