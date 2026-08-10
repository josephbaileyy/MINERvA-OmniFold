# CLAUDE.md — entry point for Claude agents in MINERvA-OmniFold

**Why this file exists.** Until 2026-08-06 this repo had no `CLAUDE.md`. All project context lived in
`AGENTS.md`, which Codex reads and Claude Code does **not** auto-load — so every Claude session started
here with zero project context and re-derived (or re-broke) things the repo already knew. If you are a
Claude agent, this file is the only thing you are guaranteed to have read. Follow the routing below
before acting.

`AGENTS.md` is the full domain reference (~500 lines: pipeline, contracts, bin edges, SLURM). This file
is orientation + the rules that have actually been violated. Neither supersedes the other; both are kept
in sync, and per this repo's convention a fact is **written once and indexed elsewhere, never
re-narrated** — so where this file points somewhere, go there rather than trusting a summary.

## Read in this order

1. **`docs/orchestration/FINDINGS.md`** — the `BEN-*` ledger of how *agents on this campaign* fail.
   This is the highest-value file in the repo for a new session and the most frequently skipped.
   Long-form detail is in sibling `FINDING-<date>-<slug>.md` files, indexed at the top of `FINDINGS.md`.
2. **`KNOWN_ISSUES.md`** — how the *code* fails. Different axis from FINDINGS; read both.
3. **`docs/OPEN_ITEMS.md`** — the live to-do.
4. **`AGENTS.md`** — domain detail for whatever you are actually touching.
5. **`docs/orchestration/CLAIMS.md`** — `CLM-*` physics claims and their verification status. Allowed
   states are `PROVED / VERIFIED-NUMERIC / VERIFIED-CODE / CITED / ASSUMED / OPEN / REFUTED`.
   **Worker agreement is not verification**; promotion needs a recoverable artifact + an independent check.

## Canonical home per kind of fact

Mirrors the table in `AGENTS.md`. Write a fact in its home; index it everywhere else.

| Kind of fact | Canonical home |
|---|---|
| Verified numbers (anything technote-quoted) | `VALIDATION_LEDGER.md` |
| Bugs, code debt, recurring traps | `KNOWN_ISSUES.md` |
| Open / deferred items | `docs/OPEN_ITEMS.md` |
| **How agents/campaigns fail** | `docs/orchestration/FINDINGS.md` (`BEN-*`) |
| **Physics claims + verification status** | `docs/orchestration/CLAIMS.md` (`CLM-*`) |
| Current state per workstream | `*_STATUS.md` |
| Chronology | `*_RUN_LOG.md` (append-only) |
| Durable invariants & gotchas | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` |
| Deliverables | `docs/analysis-note/` (Overleaf subtree, three builds) |

## Hard rules

These are not style preferences. Each one is here because it was broken and cost real time.

- **A result does not exist until its commit lands.** The commit introducing a campaign's
  scripts/launchers must also carry its products summary, the ledger entry, the RUN_LOG entry, and the
  STATUS one-liner. Other sessions run this repo concurrently — unpushed work is invisible to them.
- **Never pipe a diagnostic run through `tail`/`head`.** Redirect the whole stream to a file, then
  filter *reads* of it. Truncating at write time destroys the evidence and buys a second 30–90 min run.
  (BEN-026 — this was done twice in one day.)
- **Every ID, rank, count, and queue name in a status report must come from a command run in the same
  turn.** Never from memory, never eyeballed off a listing. Another user's job has already been
  reported as this campaign's progress once. (BEN-027)
- **A quiet log does not mean a dead job.** On this Lustre filesystem `st_blksize` is 4 MiB, so Python
  block-buffers redirected stdout and a healthy multi-hour run can show *zero* progress lines until the
  process exits. Judge liveness by `sstat` CPU time and produced artifacts, never by log growth. A
  healthy q3 sweep was once cancelled for exactly this. (BEN-028, and `AGENTS.md` salloc lesson #2)
- **Do not let a small-sample spread estimate overturn a decision.** A 16-seed "sd grew 56%" reading
  inverted a correct ranking at p=0.093, with the eventual 48-seed answer inside the CI the whole time.
  Prefer realized exceedance over a fitted gaussian tail. (BEN-025)
- **Audit and review lanes get read-only tooling.** `codex exec --sandbox read-only`, or
  `claude -p --allowedTools "Read,Grep,Glob,Bash"`; give `agy` a throwaway `git worktree`. A pure audit
  prompt has already caused a delegate to silently refactor a training loss in a file that was
  hash-pinned into a gate two hours later. Always `git status` after a delegate finishes, and preserve
  the diff before reverting — parts of it may be real findings.
- **Resume guards must validate completeness, not existence.** `[[ -s $OUT ]] && skip` let 7 partial
  slabs permanently block their own repair. Validate content, or write-to-temp + rename-on-complete.
  (BEN-023)
- **Deletions and top-level reorgs are frozen** behind `docs/POST_PUBLICATION_REORG_PLAN.md`'s freeze
  tag. `nd-unfolding/`'s root is at capacity — put new work in the subdirectory that owns it.
- **Every derived quantity in a receipt ships its ingredients** — enough that the reported numbers can
  contradict each other. A verdict-only receipt is unfalsifiable, and this is the only heuristic that has
  caught a defect with nobody suspecting one: a first-leg-vs-end-to-end metric mismatch was found purely by
  failing to derive a published ratio from published operands. `docs/orchestration/CONVENTION-receipt-ingredients.md`
  (BEN-077).
- **Do not rename or delete a tracked script cited in a RUN_LOG, ledger, or receipt JSON.** 115
  `sbatch_*.sh` names are load-bearing provenance.

## Compute quick reference

- Env: `module load tensorflow/2.15.0`; set `MNV_REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold`.
- Long/parallel interactive work: read the `salloc` section at the end of `AGENTS.md` before using it.
  Run the orchestrator *inside* the salloc; never `srun --jobid=` from an outside shell.
- Durable notification across session death: `wakerctl` watches (Slurm cron job, 12 h walltime) under
  `docs/orchestration/state/waker/`. A session-local Monitor dies with the session; the watch does not.
- Storage: home is ~40 GB and has run tight. Scratch is large but **purgeable** — anything irreplaceable
  needs a copy off scratch.

## When you learn something

If you hit a failure that a future agent could hit, add a `BEN-*` row to `docs/orchestration/FINDINGS.md`
in the same turn you fix it. If it needs more than a table row, write
`docs/orchestration/FINDING-<YYYYMMDD>-<slug>.md` **and add it to the index at the top of FINDINGS.md** —
an unindexed finding is one nobody will read, which is how nine of them sat orphaned until 2026-08-06.
