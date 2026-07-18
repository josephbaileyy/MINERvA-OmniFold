# Use the reset gap: exact early-batch plan

Continue as the existing `agy-publication-redteam` session. The user has
explicitly asked us to use agy and batch work during the Claude-school reset
gap instead of leaving dependency-safe work idle.

Perform a read-only repository and filesystem audit. Do not edit files or
submit Slurm yourself. Determine the exact immutable, collision-free work that
the orchestrator can queue now without taking Agent A/C/B/E ownership or
bypassing a verifier gate.

Priority target: the full-file SHA256 evidence needed by both queued standard
and FPS P4 repairs. Inspect the current launchers, manifests, status/receipts,
and actual filesystem. Report:

1. the exact ten standard merged ROOT paths and exact ten FPS merged ROOT paths
   (or say precisely why either inventory cannot yet be resolved);
2. sizes, immutability/dependency footing, whether A and C need the same or
   distinct inventories, and whether any current process/job can write them;
3. a concrete one-node batch layout (QOS, CPUs, wall, array or bounded
   parallelism), exact collision-free output/receipt paths, and an atomic
   publication pattern;
4. whether an existing committed launcher can be reused unchanged; if not,
   the smallest owner-neutral launcher contract the orchestrator should add;
5. any other genuinely owner-neutral batch or login-safe task worth running
   before 18:00 UTC.

Apply the campaign rule: queue early only with immutable prerequisites and no
duplicate writers. Do not recommend interactive merely because it is normally
fast—the current state has no holder and queue overlap is the point. End with
`EARLY-BATCH PASS` plus exact submission commands, or `EARLY-BATCH BLOCK` plus
the missing evidence.
