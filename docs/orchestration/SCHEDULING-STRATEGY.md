# Publication critical-path scheduling strategy

Objective: minimize wall-clock time to a publication-ready result while
preserving scientific gates, durable worker identity, and single-writer output
ownership. Concurrency is useful only when it advances an unblocked DAG lane.

Compute and LLM time are separate resources. Once a validated launcher is
submitted, Slurm should make unattended progress without a provider turn or
LLM polling. The placement score therefore includes **LLM-free progress per
wall hour**, adjustable parallelism/resource fit, maximum wall time, queue
overlap, and the downstream gates the result unlocks—not queue latency alone.

Last reconciled: 2026-07-18 15:52 UTC.

## Current critical path and parallel lanes

The publication PET critical path is:

`T6 G2 compile/smoke -> T7 full-schema P3F endpoints -> T8 PET nominal/UQ -> T9 projections -> T10 document freeze`.

T6 source is complete, but its same-UUID Claude-personal runtime turn is
provider-capped with no reset time. No ETA is assigned until availability is
evidenced. The following work remains useful in parallel:

- standard scalar lane: T2 repair/review, then T3 adoption;
- scalar FPS lane: T1 repair/review, then gated endpoints/covariance;
- PET interface lane: T5 F7/dumper/launcher repair and static review;
- owner-neutral evidence lane: immutable input hashes and provenance;
- publication-control lane: independent review and canonical-gate repair.

The 18:00 Claude-school wave serializes A, C, and B writers because they share
one provider account and one Git worktree. Cross-provider review is pipelined:
A's Codex verifier may run while C writes, and C's Codex verifier may run while
B writes, provided each verifier targets the committed owner packet and does
not inspect unrelated uncommitted work.

## Placement rules

| Task state | Preferred placement | Reason |
|---|---|---|
| Login-safe metadata, tests, manifests, review | login shell/provider turn | No scarce compute allocation needed. |
| Ready single-node work below the holder wall, with several follow-on tasks ready | existing owner-held interactive allocation | Low dispatch latency and a node that stays productively packed. |
| Ready single-node work with no holder and high queue uncertainty | first-start-wins hedge, if fully lock-safe | Retains batch queue position while testing interactive latency. |
| Large independent playlist/endpoint inventory | batch array | Natural adjustable parallelism and resumability; continues without LLM involvement. |
| Multi-hour/full-node CPU work | regular batch | Longer walls and tunable CPU/memory exceed or poorly utilize the interactive contract. |
| PET training/evaluation | gated GPU batch | Tunable GPU resource class and unattended execution; queue only after immutable estimator/input contracts. |
| Provider- or science-gated work | no allocation | A pending dependency cannot be accelerated by an idle node. |

Queue batch early only when its inputs are immutable or expressed by scheduler
dependencies and its staging/final paths cannot collide with another writer.
Interactive is not selected merely because its queue is often shorter; an
immediate productive workload and sufficient remaining wall are required.

Prefer a batch DAG (`--dependency=afterok`, arrays, immutable manifests, and
atomic receipts) whenever multiple compute stages can be validated and queued
up front. That lets hashing/event loops/unfolding/validation proceed across
provider resets and LLM pauses. An LLM should inspect milestone receipts or
failure notifications, not continuously poll healthy jobs.

## First-start-wins contract

A batch/interactive hedge is permitted only when both routes execute the same
owner/launcher and enforce all of:

1. one shared nonblocking `flock` before reading or writing;
2. a stable complete-result key plus a pre-lock/under-lock completed receipt;
3. run-ID-unique staging on the same filesystem as the final receipt;
4. content/inventory validation before atomic publication;
5. prompt cancellation of the still-pending loser once the winner is live;
6. a clean loser exit if the other route owns the lock or already completed.

The decision point must use a fresh scheduler read. If either route is already
RUNNING, it is the winner: do not cancel it merely to retrofit a hedge or switch
QOS. A hedge is established before either contender starts, never after. When
there is no ready follow-on workload for a held node, prefer the one-shot batch
route unless interactive latency materially changes the publication critical
path; batch releases its resources automatically when the task ends.

Scientific production additionally requires skip validation against the full
configuration/source/input fingerprint. A mere existing filename is never a
completion signal.

## Dispatch metrics

Every compute receipt records: task/DAG gate, owner, output namespace,
submission/start/end UTC, queue delay and reason, QOS/partition, requested and
used CPU/GPU/memory/wall, artifact count, exit/failure class, resume behavior,
duplicate-writer protection, LLM turns needed while running (normally zero),
unattended downstream stages, and estimated critical-path time saved or lost.
Provider rounds also record account, persistent role/UUID, start/end, cap
evidence, artifact/commit result, and whether the turn was writer or verifier.

## Quiet periods and rewakeup

An orchestrator quiet period begins when all currently runnable work is either
executing unattended, delegated to a preserved worker, or gated on a future
event, and another poll would not change a decision. Ending the LLM turn is the
preferred wait mechanism; detached, lock-protected watchers and Slurm continue
without LLM usage.

Valid wake triggers are: a terminal Slurm state plus artifact receipt, a
provider-limit/reset event, a saved-role turn completion, a verifier verdict,
or a scheduled dependency checkpoint. Do not wake merely to make a healthy
cache or progress display look fresh. Do not enter a quiet period while a
duplicate-writer race, failed atomic publication, provider error, or other
decision requiring immediate handling is unresolved.

`QUIET-PERIODS.tsv` is append-only and records start/end, trigger, unattended
work, provider capacity before/after, decisions avoided, and critical-path
effect. The productivity measure is not elapsed sleep alone: it is useful
compute/provider work completed per LLM-active interval, fewer cosmetic polls,
and whether the rewakeup exposed a decision-ready checkpoint.

Goal-mode continuation may resume immediately after an end-turn even without a
declared wake trigger. Record that as a false wake rather than pretending a
break occurred; redirect the forced-active interval only to already-scoped,
owner-neutral work. Detached watchers remain the reliable mechanism for
long-duration external progress.

## Historical Slurm telemetry (scheduler-local 2026-07-11 through 2026-07-18)

Reproducible source: `analyze_slurm_history.py`; committed summary:
`state/slurm-history-20260711-20260718.json`. The 1,460 rows are task-weighted,
so large arrays contribute one observation per task. Queue time is
`Start-Eligible`; `Submit-Start` is kept separately because it includes
dependency/ineligible holds.

| QOS | Tasks | Completed / failed / canceled / timeout | Eligible queue p50 | Eligible queue p90 | Placement implication |
|---|---:|---:|---:|---:|---|
| `interactive` | 37 | 3 / 3 / 7 / 23, plus 1 running | 0 s | 0.4 s | Near-zero dispatch latency, but holder wall expiry appears as TIMEOUT; request only with a packed ready workload. |
| `gpu_interactive` | 43 | 21 / 7 / 9 / 6 | 0 s | 1 s | Best for short GPU gates and debugging, not long unattended ensembles. |
| `gpu_shared_interactive` | 12 | 11 / 0 / 1 / 0 | 0 s | 0 s | Strong short GPU latency in this sample; retain strict wall/resource fit. |
| `regular_1` | 354 | 354 / 0 / 0 / 0 | 1,527 s (25.5 min) | 5,432 s (90.5 min) | Reliable for ready CPU arrays/full-node work; queue early once inputs are immutable. |
| `gpu_shared` | 450 | 390 / 3 / 57 / 0 | 5,087 s (84.8 min) | 22,418 s (6.23 h) | Submit validated PET arrays early and use dependencies; do not wait for an LLM turn to queue them. |
| `shared` | 559 | 481 / 31 / 46 / 1 | 8,785 s (2.44 h) | 46,685 s (12.97 h) | High variance: queue dependency-safe work early; use interactive only for a genuine critical gate with follow-on work. |

These are historical observations, not guaranteed future wait times. Job-name
families, dependency holds, runtimes and state counts remain in the JSON for
task-specific routing and future updates.

## Provider/account dispatch telemetry

Reproducible source: `analyze_dispatch_history.py`; committed summary:
`state/dispatch-history-through-20260718.json`. The 84 ledger rows include
provider, orchestrator and Slurm records. Exit zero means the dispatch/task
returned successfully, not that its scientific verdict was PASS. Claude-school
aliases are grouped as one shared account; no success count is interpreted as
a remaining-usage percentage.

| Account | Ledger rounds | Dispatch evidence | Median measured duration | Best routing role / caution |
|---|---:|---|---:|---|
| agy | 19 | 19 exit-zero; 9 PASS/complete, 7 useful scientific/evidence BLOCKs, 2 rejected overclaims | 60 s | Default cheap orthogonal red-team and prompt/preflight work. Independently verify ownership/authorization conclusions. |
| Claude school shared | 18 | 14 exit-zero, 2 exit-one provider/turn failures, 2 armed/open records | 660 s | Continuity-bound implementation A/B/C. One shared capacity pool and Git worktree require serialized writers. |
| Claude personal | 2 | G2 source complete, then explicit provider cap | 990 s | Preserve E's UUID/source ownership; no replacement and no runtime ETA until availability evidence. |
| Codex personal | 9 | 8 exit-zero; 5 substantive BLOCK verdicts | 570 s | Deep continuity verification and synthesis; preserve limited personal capacity and sole reset reserve. |
| Codex school | 7 | 7 exit-zero; 4 substantive BLOCK verdicts | 720 s | Same-verifier standard review where continuity matters; current weekly capacity is constrained. |

Duration reflects only ledger rows with parseable start/end times and is not a
latency guarantee. The JSON preserves exit, outcome and writer/reviewer class
counts so routing can be recalibrated after the post-reset wave.

## Empirical placement ledger

| UTC | Task | Routes | Result | Policy update |
|---|---|---|---|---|
| 2026-07-18 15:07 | Full SHA256 of 10 standard + 10 FPS merged ROOTs (~1.28 TB) | shared batch `56090791` | Started after 4m36s in Priority. It was already RUNNING when canceled after 7s to retrofit a hedge; only an incomplete temp receipt existed. | **Routing error:** a running route is already the first-start winner. Patch future launchers before submission; never cancel healthy running batch merely to add an interactive contender. |
| 2026-07-18 15:12 | Same hash task after the routing error | replacement shared batch `56090857` + urgent interactive `56090877` | Interactive had zero-second scheduler start latency, acquired the new lock, and completed 20/20 hashes over 1,286,623,855,676 bytes in 25m25s (~0.844 GB/s aggregate); pending replacement batch canceled. Receipt paths/inventory/digests and clean skip validated. | The receipt is valid, but interactive superiority was **not** demonstrated: the original batch had started first and a one-shot batch would have released resources automatically. With no ready follow-on task, batch was the better operational choice. A/C still avoid another 1.28-TB read by reusing the receipt. |

The hash launcher and completed receipt land together under the repository
commit gate. This is provenance evidence, not a new scientific number.

## Near-term maximum-parallel schedule

1. **Complete:** interactive `56090877` hashed immutable A/C inputs; both repair
   roles consume the committed receipt without another full-content pass.
2. At 18:00:30 UTC the saved-UUID school watcher runs A -> C -> B writer turns.
3. As soon as A commits, launch the same standard verifier while C works. As
   soon as C commits, launch the same FPS verifier while B works.
4. Queue no scalar endpoint production until its verifier PASS; then use
   collision-free arrays while independent adoption/projection work uses a
   holder or CPU batch.
5. Resume E only with the same UUID after Claude-personal availability
   evidence. Use interactive for compile + 1A smoke; after PASS, freeze the
   binary and immediately queue the 12-playlist G2 array.
6. While G2/P3F arrays run, close validated scalar lanes and prepare PET static
   contracts. PET GPU jobs begin only after full-schema/negweight gates PASS.
