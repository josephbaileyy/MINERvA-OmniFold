# Publication critical-path scheduling strategy

Objective: minimize wall-clock time to a publication-ready result while
preserving scientific gates, durable worker identity, and single-writer output
ownership. Concurrency is useful only when it advances an unblocked DAG lane.

Compute and LLM time are separate resources. Once a validated launcher is
submitted, Slurm should make unattended progress without a provider turn or
LLM polling. The placement score therefore includes **LLM-free progress per
wall hour**, adjustable parallelism/resource fit, maximum wall time, queue
overlap, and the downstream gates the result unlocks—not queue latency alone.

Last reconciled: 2026-07-18 15:39 UTC.

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
