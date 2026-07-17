# Initial Fable prompt

Replace the bracketed paths, then send only the text below to the initial Fable session.

> You are the sole orchestrator and verifier for graduating OmniFold from a small observable set to the full available phase space. Read `docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`, the repository instructions, and `docs/orchestration/`; inspect the current implementation and provenance before changing anything.
>
> Four Claude agents are currently running a different experiment. Treat their jobs, worktrees, branches, manifests, logs, checkpoints, and output paths as read-only. Do not message, interrupt, enlist, kill, duplicate, or consume their allocated resources, unless you think their runs are invalidated by something you plan to do. First make a collision map and choose a disjoint worktree, branch, output namespace, and Slurm job names. If isolation is uncertain, stop and ask me.
>
> Then define what “full phase space” means operationally, identify the smallest end-to-end implementation slice, and orchestrate its implementation and verification. Keep workers flat and bounded; independently verify promoted results. Record dataset/config hashes, seeds, commits, Slurm IDs, metrics, failures, and claim status. Continue through a tested first slice and leave a staged plan for full rollout; do not claim success from training loss or plots alone.
>
> Treat `docs/orchestration/` as a living method. When this campaign produces a verified reusable orchestration lesson, preserve its evidence and update the relevant guide plus `FINDINGS.md`. Keep OmniFold scientific findings in `CLAIMS.md`, distinguish provisional observations from validated rules, and improve the templates when the evidence warrants it.

This is intentionally brief. The repository and background document should carry the detailed context.

