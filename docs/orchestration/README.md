# OmniFold orchestration kit

Unpack this directory into `docs/orchestration/` in the OmniFold repository.

## Start here

1. Copy `CLAUDE.project-template.md` to the repository root as `CLAUDE.md`, merging it with any existing instructions.
2. Copy `AGENTS.project-template.md` to the repository root as `AGENTS.md`, likewise merging rather than overwriting.
3. Fill in `OMNIFOLD-DOSSIER.template.md` and rename it `OMNIFOLD-DOSSIER.md`.
4. Initialize `CLAIMS.md` and `RUNS.tsv` from the supplied templates.
5. Give Fable the prompt in `FABLE-BOOTSTRAP.md`, substituting the real background-document path.

The files `orchestration-guide.md`, `technique.md`, `strategy-comparison.md`,
`novelty-per-round.md`, `FINDINGS.md`, `round-ledger.md`, `personas.md`, and
`persona-debate-technique.md` record the validated workflow from the new-physics project.

`run_leads.sh` is a reference launcher only. It contains machine-specific paths and model names;
adapt it to the Perlmutter environment before use.

## Core rules

- Fable is the sole router, verifier, and final synthesizer.
- Workers receive one bounded, falsifiable task each and may not sub-delegate.
- Delegate agreement is not verification. Promote a result only after an independent calculation,
  test, or primary-source check.
- Use independent methods for theorem- or implementation-shaped questions.
- Require one adversarial self-revision pass and one cross-result coherence pass.
- Keep code, data, configurations, Slurm jobs, and conclusions recoverably linked.
- Report a clean null or failed closure honestly.
- Never interfere with an active run. Use isolated worktrees and output namespaces, and ask before
  touching any path or job whose ownership is unclear.
- Treat these documents as a living, evidence-backed method. When a run reveals a reusable orchestration
  lesson, update the appropriate guide and `FINDINGS.md`, naming the episode and evidence. Keep OmniFold
  scientific conclusions in `CLAIMS.md`; do not generalize one anecdote into a method rule.

