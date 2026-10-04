# s5p (`OI-193`) campaign: cold-start handoff for a replacement session (2026-09-29)

**CITABLE FOR:** where the campaign's authority, frozen specification, code, cluster state and operating procedure are;
what was measured at 2026-09-29T06:27–06:31Z; the commands to re-measure it; the next permitted action; the prohibitions.
**NOT CITABLE FOR:** any live state (re-measure it); any result, grade or authorization. This file grants nothing: it
continues the existing authorization.

Read `AGENTS.md` first. Everything below marked **MEASURED** was true at the time given. Everything marked
**ESTIMATE** is a projection. Re-measure both before acting.

## 1. Authority and governing artifacts (all on `origin/main`)

- **Authorization:** `docs/orchestration/AUTHORIZATION-20260926-precision-measurement-completion.md`.
  - The goal text is `docs/orchestration/GOAL-20260926-precision-measurement-completion.txt`, and the task handoff is
    `docs/orchestration/HANDOFF-20260926-precision-measurement-completion.md`. `OI-193` in `docs/OPEN_ITEMS.md` is
    OPEN.
  - Campaign index: `docs/orchestration/CAMPAIGN-s5p-20260926-index.md`. State:
    `docs/orchestration/state/s5p/campaign-state.json` (its `incidents` are the running log).
  - Budget: `docs/orchestration/state/s5p/budget.json`, revision 5.
- **Frozen specification:**
  - `state/s5p/contract.json` and amendments 1–8 (incl. 6b), `state/s5p/contract-amendment-*.json`.
  - **Amendment 7, the production admission, is FROZEN at `4f5a613f`.**
  - Frozen production set: `state/s5p/prod/` (`design.json` sha256 `404446eb…`, `spec.json`, `tables/`, `queues/`,
    `queues-r1/`).
- **Owner records made during production.** All are report-only, and none changes primary claims or stopping.
  - `EXCEPTION-20260927-s5p-pilot-negative-rate-resubmission.md` (development, spent).
  - The scheduling change at 2026-09-28T20:50Z: lane throttles raised, recorded in the campaign-state incidents. Its
    correction is dated 21:50Z.
  - `CLARIFICATION-20260928-s5p-recompute-A6-A8.md`: A6 (union) and A8 (the 99.5% look) are read as resolved by the
    frozen text. The independent lane agrees. **No owner ruling on A6/A8.**
  - `RULING-20260929-s5p-A7-robustness-flag.md`:
    - A7: the full Holm rerun at κ = 3, and the three labels.
    - A7-VS (≈04:33Z): the κ = 3 family keeps c·S and **replaces** ±2δ_M1 by ±3δ_M1.
    - Both are explicit report-only clarifications made after production outputs were visible and before any observed
      claim p.
  - Reviews: `REVIEW-20260927-s5p-{round1-…,round2-…,admission-confirmation}.md`.
- **Parallel-task pointers:** `HANDOFF-20260928-s5p-parallel-tasks.md`.

## 2. Repositories, branches, commits (MEASURED 06:27Z)

- **Campaign worktree:** `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p`, branch
  `campaign/s5p-precision-20260926`. At the start of this handoff `HEAD` = `origin/main` = `9dd32efe`, with a clean
  working tree. This handoff's commit follows; its hash is in the commit that adds this file.
  - The campaign pushes `HEAD:main` after `git fetch` plus an ancestry check. It merges `origin/main` first when other
    lanes have pushed, as note-sync `b53136f8` and reproduction `4c5b3047` did.
  - **Verify every push** with `git fetch origin && git branch -r --contains <sha>`. Two pushes here were silently
    skipped by an `&&` chain and noticed late.
- **The shared checkout `/Users/josephbailey/local-research/MINERvA-OmniFold` (main) is NOT the campaign's.** Do not
  work there. Other sessions' untracked files are there.
- **Other lanes:** they own their own branches, and they are NOT campaign state.
  - Recompute: `origin/s5p-parallel-recompute-20260928`, last seen `e8fbf321`, not merged. Worktree
    `../MINERvA-OmniFold-s5p-recompute`. Session name `gbdt independent`.
  - Note sync: merged at `b53136f8`; the standalone note mirrors `12991771`.
  - Reproduction: merged at `126525b3` and `4c5b3047`; it records the joint result as still pending.
- **Uncommitted work:** none in the campaign worktree. Scratch files in this session's scratchpad are copies only, and
  nothing depends on them.

## 3. Cluster state (MEASURED 06:14–06:31Z; namespace `/pscratch/sd/j/josephrb/s5p-20260926`, called `$NS`)

**Pinned deploys.** These are clean `git clone`s; never modify them.
- `$NS/deploy/4f5a613f` runs the NuWro and GiBUU lanes.
- `$NS/deploy/55a41765` runs the pow, MnvTune, GENIE CV and GENIE MEC lanes. It differs from `4f5a613f` only by
  `s5p_requeue.py` and its test.

**Runners, all on login33.** Reach them with `ssh saul.nersc.gov` then `ssh -q -o LogLevel=ERROR login33`; saul itself
lands on other login nodes. Each runner is `setsid nohup`, a session leader with PPID 1, and **independent of any Claude
session**. Each has exactly one child, the line it is currently executing.

| lane | runner PGID | queue file (in its deploy) | log | STOP file |
|---|---|---|---|---|
| pow (P1→P3g, 6 sets × 200) | 565706 | `…/55a41765/…/prod/queues-r1/pow.q` | `$NS/runs/queue-prod-r1-pow.log` | `$NS/runs/STOP-prod-r1-pow` |
| MnvTune_v1 | 565712 | `…/queues-r1/cal-MnvTune_v1.q` | `queue-prod-r1-MnvTune_v1.log` | `STOP-prod-r1-MnvTune_v1` |
| GENIE_2_12_10_CV | 565718 | `…/queues-r1/cal-GENIE_2_12_10_CV.q` | `queue-prod-r1-GENIE_2_12_10_CV.log` | `STOP-prod-r1-GENIE_2_12_10_CV` |
| GENIE_2_12_10_MEC | 565720 | `…/queues-r1/cal-GENIE_2_12_10_MEC.q` | `queue-prod-r1-GENIE_2_12_10_MEC.log` | `STOP-prod-r1-GENIE_2_12_10_MEC` |
| NuWro_21_09 | 1283647 | `…/4f5a613f/…/prod/queues/cal-NuWro_21_09.q` | `queue-prod-NuWro_21_09.log` | `STOP-prod-NuWro_21_09` |
| GiBUU_2019 | 1285855 | `…/4f5a613f/…/queues/cal-GiBUU_2019.q` | `queue-prod-GiBUU_2019.log` | `STOP-prod-GiBUU_2019` |

The logs `queue-prod-{pow,MnvTune_v1,GENIE_2_12_10_CV,GENIE_2_12_10_MEC}.log` (without `r1`) are the replaced runners,
which were stopped at the scheduling change. They are history.

**Slurm arrays.** Every lane is on its FIRST submission at throttle 2, and each runner waits for its array to leave the
scheduler.

| lane | array | label |
|---|---|---|
| pow | 59021632 | `s5p_pow_p1_a1p0` |
| MnvTune_v1 | 59021669 | `s5p_cal_mnvtune_v1_b0` |
| GENIE_2_12_10_CV | 59021681 | `s5p_cal_genie_2_12_10_cv_b0` |
| GENIE_2_12_10_MEC | 59021698 | `s5p_cal_genie_2_12_10_mec_b0` |
| NuWro_21_09 | 59021752 | `s5p_cal_nuwro_21_09_b0` |
| GiBUU_2019 | 59021765 | `s5p_cal_gibuu_2019_b0` |

At 06:15Z: 12 tasks RUNNING, 6 PENDING, no Traceback in `$NS/runs/prod/logs/`. The same account also runs non-s5p
`pfd-*` GPU jobs from another session; they are not the campaign's.

**Products at 06:14:56Z.** Excluding `*.partial-*`, 757 in total:
- calibration: CV 128, MEC 153, GiBUU 116, MnvTune 118, NuWro 124;
- power: `P1_a1.0` 118.

The rate was about 52/h over 04:15–06:15Z and 54–67/h earlier.

**Status files.** `$NS/runs/prod/status/` holds only the five `<null>-B0.json`, written 16:11–16:12Z with reason "no
calibration product yet". **No look has computed an observed statistic.** `$NS/stage7/joint/` does not exist, so the
evaluator has never run.

**Meter** (06:30Z, `$NS/measure/meter-measure-handoff-20260929T0630Z.json`):
- open CPU concurrency 1.5 of 2.0;
- production charged 51.0 of 200 CPU node-h. These are the six open reservations of 8.5 each, not measured cost; they
  reconcile at close;
- CPU charged, cumulative in the envelope: 124.49 of 345.27. GPU: 12.18 of 125 node-h (8.35 A100-h campaign);
- verification_repair 62.037 CPU, untouched;
- ledger `$NS/ledger/admissions.jsonl`.

**Scheduling change in flight.** pow, MnvTune, CV and MEC use throttle 3 from their NEXT submission (batch 1 / P2).
NuWro and GiBUU stay at 2. Total 2.0 of the 2-node cap. **Not yet measured:** throughput after the change. It is owed
to the owner once batch 1 / P2 run.

**ESTIMATES** (last-2-h rates, lower bounds; a batch's look waits for its slowest task):
- The first look with B > 0 is MEC, near 2026-09-29T11–12Z; then GiBUU and NuWro later that day.
- Nothing can stop at k = 0 before B ≈ 1200.
- The MnvTune and GENIE CV nulls may not stop before B = 1200.
- Total wall-clock per amendment 7: about 5 days expected, about 7 worst.

## 4. How production runs itself (why no action is needed between events)

Each queue line is: wait for batch *b* to leave the scheduler, then run the look (`s5p_seqstop.py`).
- **Look exits 0 (continue):** submit batch *b*+1 through `s5c_meter.py submit`.
- **Meter cap refusal (exit 3):** drain until no `s5p-s5p_(cal|pow)_` job is queued, retry once, and if refused again
  write a terminal `budget` final status.
- **Look exits 3 (stopped):** the line logs "`<null>` stopped before batch *b*+1". Every later look exits 3 at once
  ("already stopped"), nothing is submitted, and the runner ends with "`queue done`".
- **Last line:** force-stops with "batches exhausted".
- **Any other exit:** "`line N STOPPED the queue`", and the runner stops. That is an event needing diagnosis.

A final status is TERMINAL (amendment 7). The runner loop is `nd-unfolding/s5c_queue.sh`; the look/submit line format is
in `state/s5p/prod/queues-r1/*.q`.

## 5. What depends on the old session staying alive

1. **The local event monitor** (a background shell of the old session, polling every 20 min). **It dies with that
   session.** Re-arm your own (§7). It only observes.
2. **Cross-session messaging.** Peers address the old session as `gbdt [c5747d]`. Messages sent to it after it closes
   are lost. On takeover, send one message to `gbdt independent` (the recompute lane) naming yourself as the campaign
   session.
3. **Owed report.** Throughput after the throttle change and a revised ETA (see §3).

Nothing else depends on the old session: the runners, jobs, meter, statuses and products all live on the cluster.

**Persistence risk, not session-related:** the runners live on login33. If login33 reboots they die, the running
arrays continue, and nothing new is submitted. Detect it with §7's runner check.

## 6. Taking over ownership without duplicate submissions

- **Never start a runner for a lane that has one.** Check first with the §7 runner check: exactly one PGID per lane, on
  login33.
- **Never run a queue file from its start.**
  - Line 2 of an original calibration queue is the B = 0 look plus the batch-0 submission. Line 2 of `pow.q` submits P1.
  - Both are already done. Re-running either would write a spurious look and re-submit batch 0 / P1.
- **Never touch the STOP files, deploys, statuses or products.** A STOP file only skips `s5c_valid_*` lines; production
  lines ignore it.
- **If a runner is verified dead** (no process, the log not advancing, the lane not terminal):
  1. Resume with `nd-unfolding/s5p_requeue.py --queue <that lane's current queue> --resume-label <label of the batch
     whose array is queued or running, or the next unsubmitted one if none> --throttle <the lane's current throttle>
     --note <reason> --out <new queue>`. It keeps every line from that batch's wait line; the wait line holds until the
     array leaves, so nothing is re-submitted.
  2. Commit the new queue.
  3. Clone that commit into a NEW `$NS/deploy/<sha>`.
  4. Start ONE runner on login33, as the 20:50Z incident did:
     `cd $NS; S5C_NS=$NS setsid nohup bash $D/nd-unfolding/s5c_queue.sh $D/<queue> $NS/runs/STOP-prod-r2-<lane> >>
     runs/queue-prod-r2-<lane>.log 2>&1 < /dev/null &`
  5. Record an incident.
- **This recovery is a repair, not routine.** Do it only after a measured death, and never by moving or editing an
  existing deploy: a checkout-pinning runner kills pending jobs whose tree moved.

## 7. Re-measurement commands (use these; do not trust §3)

```bash
# heads
cd /Users/josephbailey/local-research/MINERvA-OmniFold-s5p && git fetch -q origin && git status --short && \
  echo "HEAD=$(git rev-parse --short HEAD) origin/main=$(git rev-parse --short origin/main)"
# runners (expect exactly six session leaders, one per lane)
ssh -o BatchMode=yes saul.nersc.gov 'ssh -q -o LogLevel=ERROR login33 "ps -eo pid,pgid,ppid,etime,args | grep [s]5c_queue.sh | cut -c1-230"'
# jobs, products, statuses, errors
ssh -o BatchMode=yes saul.nersc.gov 'NS=/pscratch/sd/j/josephrb/s5p-20260926; date -u +%FT%TZ;
  squeue -u josephrb -h -o "%i %j %T" | grep " s5p-"; echo squeue_rc=$?; ls $NS/runs/prod/status/;
  for d in $NS/runs/prod/cal/* $NS/runs/prod/pow/*; do echo "$(basename $d) $(ls $d | grep -v partial | grep -c npz$)"; done;
  for f in $NS/runs/queue-prod-r1-*.log $NS/runs/queue-prod-NuWro_21_09.log $NS/runs/queue-prod-GiBUU_2019.log; do echo "== $f"; tail -2 $f | cut -c1-200; done;
  grep -lE "^Traceback|\[s5c\] task=[0-9]+ name=.* rc=[1-9]" $NS/runs/prod/logs/*.out 2>/dev/null | head'
# meter (read-only: reads the ledger and sacct, writes only --out)
ssh -o BatchMode=yes saul.nersc.gov 'NS=/pscratch/sd/j/josephrb/s5p-20260926; cd $NS/deploy/55a41765 && /usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/s5p/budget.json --ledger $NS/ledger/admissions.jsonl measure --out $NS/measure/meter-measure-<UTC>.json'
```

Mind the `squeue` exit code: a `grep` with no match returns 1. Read `squeue` into a file and check its own rc (memory:
never pipe a command whose status you read).

**Event monitor to re-arm** (background, 20-min poll):
- It fires on:
  - a runner line `STOPPED the queue`, `refusing` or `queue done`;
  - a `Traceback` or a nonzero task `rc=` in `$NS/runs/prod/logs/*.out`.
- It must exclude lanes already recorded as terminal, or "queue done" re-fires every time it polls.
- It only observes.

## 8. Terminal conditions and the next permitted actions

**Now: monitor only.** Act only on an event.
- "`STOPPED the queue`" or `Traceback`: diagnose it. Retries follow the retry rules in the governing documents.
- A `budget` final status: record it.
- New `<null>-B<B>.json` files are expected looks; read them and record them.
- Report throughput and ETA after batch 1 / P2 start.

**Production is terminal when ALL of these hold:**
- five `$NS/runs/prod/status/<null>-final.json`;
- the pow runner logs "queue done", or pow has a budget or incomplete outcome;
- `squeue` (rc 0) shows no `s5p-s5p_(cal|pow)_` job;
- the meter's open concurrency is 0.

**Then, in order:**
1. **Evaluate.** It runs on a login node, taking minutes and no allocation. Use a NEW clean deploy of the current
   `origin/main` (it must contain `nd-unfolding/s5p_robust_labels.py`, schema 2, commit `67eadf25` or later):
   `cd $D && source ./setup_salloc_env.sh && PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_joint.py evaluate --design
   docs/orchestration/state/s5p/prod/design.json --v $NS/stage3/V/V-s3v.npz --out $NS/stage7/joint/joint-evaluate.json`
   - Verify first that `s5p_joint.py`, `s5p_inference.py` and `s5p_seqstop.py` are byte-identical to `4f5a613f`.
2. **Labels:**
   `PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_robust_labels.py --evaluate $NS/stage7/joint/joint-evaluate.json
   --design docs/orchestration/state/s5p/prod/design.json --out $NS/stage7/joint/robust-labels.json`
   - Commit copies under `docs/orchestration/state/s5p/stage7/joint/`.
3. **Independent verification.** Tell the recompute lane (`gbdt independent`) that production is terminal. Its exact
   final commands are in its handoff §5, on `origin/s5p-parallel-recompute-20260928`. Do not mark the joint result
   recorded before its report. Amendment 7 `validation_and_assurance` (v) requires it.
4. **Stage 7:**
   - the joint result with its conditions (amendment 7 `claims`);
   - power per null;
   - the ruled robustness labels;
   - the release materials;
   - a note/primer/paper build and a sync of the standalone repo (the note-sync lane precedent);
   - a reproduction update (the reproduction lane);
   - pushing and verifying both remote heads;
   - the final delivery: four status fields, paper-wide readiness, evidence, spend, heads, and costed remaining
     requirements.

**Owner decisions:** none is required now.
- **Optional:** R6 (cross product) and R8 (95% look precision) remain available to the owner. Both reviews read the
  text as resolving them.
- **Future:** a decision would be needed only for something the frozen rules do not cover, such as a repair after a
  runner-level failure beyond the retry rules. Identify it; do not decide it.

## 9. Prohibited

- **Owner-reserved:** no PET; no general cleanup; no external messages; no public deposit; no release tag; no
  submission.
- **Frozen rules:** no guard bypass, purchases or allocation transfers. No change to the frozen claims, statistics,
  stopping rules, terminal statuses, seeds, batches or estimator settings. Never rescue a failure by changing criteria.
- **Running work:** do not stop, restart or re-submit jobs merely for a handoff or tidiness. Do not edit or move any
  `$NS/deploy/*`, `$NS/runs/prod/*` or STOP file. Do not use the shared main checkout.
- **Git hygiene:** stage explicit paths only; pass an explicit git identity per commit (`-c user.name="scalar5d
  campaign" -c user.email="scalar5d-campaign@minerva-omnifold.invalid"`); regenerate `docs/orchestration/MANIFEST.tsv`
  after staging (a new doc needs `MANIFEST-overrides.tsv` and `CATALOG.md` rows).
- **Other lanes:** do not edit their branches. Relay to them with SendMessage.
- **Caps:** cumulative 345.27 CPU node-h and 500 A100-h; each new pool ≤ 10% of the uncommitted allocation; 20%
  verification/repair reserve; at most 2 CPU nodes and 4 GPUs concurrently.

## 10. Successor goal prompt

`docs/orchestration/GOAL-20260929-s5p-campaign-successor.txt`. It continues the existing authorization and grants
nothing new.

## Addendum 2026-09-30: transition r2 (budget revision 6) changed the runners, deploy and meter commands

This addendum is dated and does not edit the sections above. Owner-approved on 2026-09-30, and executed and verified
22:40–22:45Z (RUNBOOK-20260930-s5p-transition-r2-budget-rev6.md; `campaign-state.json` incidents):
- **The budget:** revision 6, production 209.647. The ledger is bound to it (`b9260acd…`).
- **The runners:** the six runners are now PGIDs 1174643–1174648 on login33, running deploy `$NS/deploy/c754f3cd`
  with `prod/queues-r2/<lane>.q`. Their logs are `runs/queue-prod-r2-<lane>.log` and their STOP files
  `runs/STOP-prod-r2-<lane>`. The PGIDs, logs and deploys in §3 and §7 are superseded.
- **The meter:** every meter call must run from `$NS/deploy/c754f3cd`, or from a later commit carrying revision 6.
  The §7 command from `deploy/55a41765` is now refused (rc 5, binding mismatch). The §6 recovery procedure is
  unchanged, except that it resumes from `queues-r2`.

## Addendum 2026-10-04: transition r3 (budget revision 7) changed the runners, deploy and meter commands again

This addendum is dated and does not edit the sections above. The owner decided on 2026-10-04
(`DECISION-20261004-s5p-production-budget-extension.md`), and the transition was executed and verified at
04:46–04:47Z:
- **The budget:** revision 7, with production 234.647, verification/repair 68.287, pool 341.434 and cumulative ceiling
  376.52. The ledger is bound to it (`be29f2c3…`).
- **The runners:** the six runners are now PIDs 1047835, 1047836, 1047838, 1047839, 1047840 and 1047841 on login33.
  They run deploy `$NS/deploy/e0d7b04a` with `prod/queues-r3/<lane>.q`. Their logs are
  `runs/queue-prod-r3-<lane>.log` and their STOP files `runs/STOP-prod-r3-<lane>`.
- **The meter:** every meter call must run from `$NS/deploy/e0d7b04a` or later. The r2 addendum's deploy `c754f3cd`
  is now refused (rc 5).
- **The rollback target** is deploy `ae85b7f2` (revision 6 plus queues-r3).

## Addendum 2026-10-04: transition r4 stage 1 moved NuWro to throttle 5

This addendum is dated and does not edit the sections above. On the owner's instruction ("Prepare and execute the
NuWro concurrency increase as other lanes finish, within the existing concurrency cap and budget …"), NuWro alone moved
to a new runner at 16:20Z, verified at 16:20:29Z (campaign-state incident 2026-10-04T16:21Z):
- **NuWro's runner** is now PID 669349 on login33, deploy `$NS/deploy/b93445c4`, queue
  `prod/queues-r4/cal-NuWro_21_09.q` (resumed at the `s5p_cal_nuwro_21_09_b5` wait line, `--throttle 5`), log
  `runs/queue-prod-r4-NuWro_21_09.log`, STOP file `runs/STOP-prod-r4-NuWro_21_09`. The r3 runner 1047840 is stopped.
- **The other runners** are unchanged (r3, deploy `e0d7b04a`); power's runner ended at `queue done` (15:42Z).
- **The budget** is unchanged: b93445c4 carries revision 7 byte-identical (`be29f2c3…`), so the meter runs from
  either deploy. No rebind.
- **Rollback:** `prod/queues-r4-rollback/cal-NuWro_21_09.q` (throttle 2), started by the same `transition-r4/runner_r4.sh`
  procedure. Do not restart the r3 queue: it would re-run the b4 look and resubmit b5.
- **Stage 2** (NuWro to throttle 16, 2.0 nodes alone) is planned only when MEC, MnvTune, CV and GiBUU are all terminal
  (final statuses, no queued arrays), as another one-lane transition while NuWro waits on a batch.
