# OmniFold multi-account orchestration

The primary Fable session is the sole orchestrator, router, independent verifier, and final synthesizer.
Token-heavy implementation, auditing, literature work, and repeat runs should be delegated to the
available external accounts with one bounded task per dispatch.

## Control topology

- Keep the topology flat. Workers must not spawn subagents or route work to one another.
- Give workers exact inputs, owned paths, a falsifiable question, verification requirements, and a
  required final-report format.
- Use distinct worktrees and output directories for concurrent writers.
- Do not modify shared account configuration to pin models; use invocation flags and live-check availability.
- Never treat a past quota observation as current state.

## Verification

- A delegate result is a hypothesis until the orchestrator independently checks it.
- For code or numerical claims, use a minimal synthetic case with known truth when possible.
- Require an adversarial self-revision pass before promotion.
- After per-result audits, dispatch one cross-result task asking whether all results can be made coherent.
- Use graders as fatal-error filters, not as fine rankers.
- Label claims `PROVED`, `VERIFIED-NUMERIC`, `VERIFIED-CODE`, `CITED`, `ASSUMED`, `OPEN`, or `REFUTED`.

## Perlmutter safety

- Submit substantial computation through Slurm; do not train on login nodes.
- Preserve job scripts, scheduler IDs, logs, checkpoints, exit status, resource usage, and environment capture.
- Never cancel, reprioritize, or alter another agent's jobs without explicit user authorization.
- Treat active agents' branches, worktrees, manifests, logs, and output directories as read-only.
- Do not write two jobs into the same checkpoint or result directory.

## OmniFold acceptance discipline

Training completion or decreasing loss is not scientific validation. Promotion requires the applicable
closure tests, prior/model-dependence checks, seed stability, finite-sample assessment, leakage audit,
weight diagnostics, uncertainty propagation, and reproducible provenance described in the dossier.

## Improve the orchestration method

Treat `docs/orchestration/` as a living research artifact. When an episode produces a verified, reusable
lesson about routing, prompting, verification, convergence, account behavior, or HPC coordination:

1. Preserve the episode's prompt, outputs, ledger, and decisive verification.
2. Add a concise entry to `docs/orchestration/FINDINGS.md` with an episode/evidence pointer.
3. Update the relevant guide or template if the lesson changes future behavior.
4. Mark provisional observations as provisional; do not promote a rule from one unverified anecdote.
5. Keep OmniFold scientific results in `CLAIMS.md` and general orchestration lessons in the orchestration docs.

