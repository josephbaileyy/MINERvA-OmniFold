# s5p (`OI-193`): transition r2 — budget revision 6 and the coordinated six-runner move (PREPARED, NOT EXECUTED)

**CITABLE FOR:** the prepared budget revision 6 (production 200 → 209.647 CPU node-h, from the unallocated 9.647);
the coordinated six-runner transition that makes it effective (finding s5p-F5); its preflight, dry runs, readiness,
execution steps, checks and rollback; what does and does not change. **NOT CITABLE FOR:** an authorization. Nothing
here has been executed. Execution needs the owner's approval, given in the campaign session and recorded verbatim.
The campaign session (`gbdt worker [dfdda9]`) is the sole production operator.

**Requested:** Joseph, relayed on 2026-09-30 by a peer session ("Could you do both?", answering its suggestion to
prepare this transition and to assess whole-node packing). Packing is being assessed read-only by that peer and is
not implemented here.

## 1. Why, and what changes

`REPORT-20260930-s5p-batch1-throughput-eta-cost.md` §2 shows why:
- **The squeeze.** Under the frozen meter every open batch is charged its 8.5 reservation, against a measured cost
  of about 4.7. Near the end this refuses a submission, and the frozen queue then drains and retries once, at about
  10-05.
- **The risk.** If cost per batch exceeds about 4.8, the retry fails and one external null ends with a terminal
  `budget` status at 6 batches.
- **The fix.** With production at 209.647 the forecast has no refusal up to about 4.83 per batch, no `budget` stop up
  to about 4.95, and terminal about a day earlier.

| changes | unchanged |
|---|---|
| `budget.json` revision 6: `pools.cpu.stages.production` 200.0 → 209.647 (the unallocated CPU 9.647 → 0) | the design, tables, seeds, batches, estimator settings, claims, statistics, stopping rules, terminal statuses (`state/s5p/prod/`, amendment 7) |
| the ledger's budget binding (one `rebind` record) | the campaign CPU cap 310.184, the cumulative envelope 345.27, the verification/repair floor 62.037, GPU, the concurrency cap (2 nodes), every lane's throttle (3/3/3/3/2/2), the retry rules |
| the runners' deploy (a new clean clone), their queue files (`prod/queues-r2/`, `s5p_requeue.py` resumes) and log/STOP names (`-r2-`) | every array already queued or running (none is stopped, cancelled or resubmitted) |

**Disclosure.** Decided after the controllers' looks were visible (k = 0 at every null through batch 1). It changes
only whether a late submission is refused, and so the B a null can reach. No statistic or decision rule changes.

## 2. Prepared and verified (2026-09-30)

- **The budget:** `state/s5p/transition-r2/budget-rev6-PREPARED.json`.
  - Its stages sum to 310.184, which equals the campaign cap. Nothing else changes except the rule text and the
    history.
  - The live copy is written at execution, with its utc and the "PREPARED" wording replaced.
- **Queue resumes (dry run):** `s5p_requeue.py` was run on all six current queues at their current labels (pow P3;
  every calibration lane b2). Each output starts at that batch's wait line and keeps every later line byte for byte,
  throttles included.
- **Rebind (dry run, on a copy of the ledger in `$NS/diag-20260929/transition-dry/`):**
  1. revision 5 measures rc 0, production 200;
  2. the rebind to revision 6 gives rc 0;
  3. revision 6 measures rc 0: production 209.647, open admissions (6), charges and open concurrency (2.0) unchanged;
  4. **revision 5 is then refused (rc 5, binding mismatch)**;
  5. rolling back by rebinding to revision 5 gives rc 0, and revision 5 measures rc 0 again.

  The real ledger's sha256 was identical before and after (`a941a218…`).
- **Code:** `origin/main`'s `nd-unfolding/` differs from the running deploy `55a41765` only by the non-production
  `s5p_robust_labels.py` and its test. The frozen `s5p_joint`, `s5p_inference` and `s5p_seqstop` are identical to
  `4f5a613f`.
- **Preflight** (`state/s5p/transition-r2/s5p_transition_r2_preflight.sh`, read-only; 2026-09-30T22:36Z): **READY**.
  - Six runners, one per lane, each on its wait line.
  - Every array has 10–31 pending tasks.
  - The ledger is bound to revision 5 (`f29db389…`), and the meter measures rc 0.

## 3. Execution (only after approval; each step is checked before the next)

- **E0. Record the approval.** Put the owner's approval verbatim in the execution record.
- **E1. Preflight.** Run `ssh saul.nersc.gov 'bash -s' < state/s5p/transition-r2/s5p_transition_r2_preflight.sh`,
  which must print READY. Choose a time when no array is near its end; the script refuses one with no pending task.
- **E2. Stop the six runners, one lane at a time, on login33.**
  1. Re-read the lane's log: the last line must be its wait line.
  2. Run `kill -TERM -- -<PGID>`.
  3. Confirm no process is left in that PGID and that the log's last line is unchanged.
  4. If a lane is mid-look or mid-submit (last line not a wait line), wait for its next wait line.
  5. Never kill a look.

  Stopped runners submit nothing. The arrays keep running, and any look that falls due waits for the new runner.
- **E3. Two commits, in the campaign worktree.** Stage explicit paths, use the campaign identity, regenerate the
  manifest, and verify each push with `git branch -r --contains`.
  - **Commit A:** `prod/queues-r2/<lane>.q`, generated by `s5p_requeue.py --resume-label <observed label> --throttle
    <current>` with the note "transition r2, <utc>", plus the incident record. The budget is unchanged, so this is
    the **rollback target**.
  - **Commit B:** revision 6 made live in `state/s5p/budget.json`, plus the record. This is the **execution target**.
- **E4. Deploy both.** On the cluster, clone A and B into new `$NS/deploy/<sha>` directories, never touching an
  existing deploy. Run the preflight with the argument `<B>`: the new deploy must be clean at HEAD = B, with no extra
  `nd-unfolding` changes, identical frozen modules, revision 6 with production 209.647 and stages summing to the cap,
  and the queues present.
- **E5. Rebind, from deploy B.**
  1. Run `s5c_meter.py --budget docs/orchestration/state/s5p/budget.json --ledger $NS/ledger/admissions.jsonl rebind
     --reason "revision 6 (owner decision <date>): production 209.647; transition r2"`.
  2. Then `measure` from B: rc 0, production 209.647, the same six open admissions, open concurrency 2.0.
- **E6. Start one runner per lane on login33, from deploy B.** The command, per handoff §6:
  `cd $NS; S5C_NS=$NS setsid nohup bash $B/nd-unfolding/s5c_queue.sh $B/docs/orchestration/state/s5p/prod/queues-r2/<lane>.q
  $NS/runs/STOP-prod-r2-<lane> >> runs/queue-prod-r2-<lane>.log 2>&1 < /dev/null &`
- **E7. Post-checks.**
  - Exactly six session leaders, one per `queues-r2` lane.
  - Each log shows `deploy=$B pin=<B>` and its first line waiting on the observed label.
  - `squeue` shows the same arrays, with nothing new submitted.
  - The monitor already reads `queue-prod-r2-*.log`.
- **E8. Records and notices.**
  - Record the incident: times, old and new PGIDs, deploy shas, meter receipts.
  - Tell the recompute lane that **`meter measure` must now run from deploy B**, because the old deploys' budget no
    longer binds (step 4 of the dry run). Its terminal check §5.1 changes accordingly.
  - Update the handoff §7 commands likewise.

Expected downtime is about 20–40 minutes, during which no submission is possible. Arrays that finish in that window
have their looks delayed until E6, not lost.

## 4. Rollback

- **R1: failure before E5 (the ledger is still bound to revision 5).** Start the six runners from deploy A, whose
  queues are identical and whose budget is revision 5. Production continues under the frozen cap of 200. Record it.
- **R2: failure after E5.**
  1. From deploy A, `rebind` to revision 5 (dry-run step 5).
  2. `measure` from A.
  3. Start the runners from A.
  4. Record it.
- **Never** restart an old `queues-r1` / `queues` runner or run any queue file from its start: their earlier lines
  would resubmit batches.
- **If a duplicate submission appears** (impossible by construction, since every resumed queue starts with the wait
  line), stop the new runners and bring it to the owner. Do not cancel jobs without an owner decision.

## 5. Decision needed

The owner is asked: **approve budget revision 6 (production 209.647 from the unallocated 9.647) and its execution by
the transition above**, in a window the campaign chooses when the preflight is READY and before about
2026-10-04T12Z. Alternatively: **decline**, and keep the frozen cap of 200 (the forecast's option A).

- **Recommendation:** approve. It removes a forecast `budget` ending, which is about one SE of cost drift away, and
  gains about a day. The transition repeats the 2026-09-28T20:50Z procedure, which moved four lanes, now for six.
- **Its risk:** the downtime, and any error in the stop/start steps. The checks and the pre-deployed rollback target
  bound it.
- **Not included:** whole-node packing, which is the peer's separate, read-only assessment.
