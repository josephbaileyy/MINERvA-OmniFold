# Publication critical-path scheduler study

Continue as the existing `agy-publication-redteam` persistent reviewer. The
user's explicit objective is a publication-ready result as soon as possible,
with as much safe parallelism as possible. This is a read-only scheduling
study: do not edit files, dispatch agents, submit/cancel Slurm, or mutate
scientific products.

Use current repository state plus live/read-only Slurm evidence (`squeue`,
`sacct`, `scontrol show job` where available) to build an empirical scheduling
policy. Analyze relevant campaign jobs from roughly 2026-07-11 onward,
including submit-to-start latency, run time, QOS/partition, resource request,
success/failure, and whether work was actually on the publication critical
path. Include current hash job 56090791.

Deliver:

1. A dependency DAG from current gates T1/T2/T5/T6 through T7/T8/T9/T10,
   identifying the true critical path and independent lanes.
2. A task-class routing table: login-safe, held interactive, shared/regular
   batch, GPU batch, array, and a first-start-wins batch/interactive hedge.
3. Exact conditions for a hedge that cannot double-write: shared lock,
   collision-free staging, winner receipt, loser cancellation, and ownership.
4. A maximum-parallelism schedule for the next 24 hours and the later
   production phase. Explicitly pipeline A's Codex verifier while C writes,
   C's verifier while B writes, and any other safe cross-provider overlap;
   identify shared-worktree/git operations that must remain serialized.
5. Checkpoint ETAs as ranges, separated into queue delay, execution time, and
   dependency/provider uncertainty. Do not invent an ETA for Claude-personal
   while its monthly limit has no reset time.
6. Metrics to append for every dispatch so the routing policy improves:
   provider/account, role continuity, submit/start/end, queue reason, QOS,
   requested/used resources, artifact count, failure class, retry/resume
   behavior, and critical-path time saved/lost.
7. A recommendation for current job 56090791: leave in batch, hedge with an
   interactive request, or cancel/move—using live evidence and the rule that
   an allocation must have an immediate productive workload.

Respect durable role ownership and no duplicate writers. Maximize useful
concurrency, not merely concurrent processes. End with `SCHEDULER-STUDY PASS`
or `SCHEDULER-STUDY BLOCK`, then the immediate next three dispatch decisions.
