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

0. **`docs/orchestration/LIVE-STATE.md`** — GENERATED control-plane snapshot: current campaign, DAG
   node, declared state, owners, live Slurm jobs, armed `wakerctl` watches. ~70 lines, and the only
   file here that answers *"what is happening right now"* — every file below answers "what is true in
   general". Read it first because it is the cheapest orientation in the repo. Do not hand-edit;
   regenerate via `docs/orchestration/generate_live_state.py`. **Check its `Observed:` timestamp and
   `Git:` sha against `HEAD` before trusting it** — a stale snapshot is worse than none.
0b. **`docs/orchestration/CATALOG.md`** — pointer-only router for `docs/orchestration/`'s 498 files,
   of which ~14% are live. Routes by task; `MANIFEST.tsv` is the authority on what is LIVE vs
   ARCHIVAL vs MACHINE vs DEAD. Use it instead of reading the directory. Retention rules:
   `CONVENTION-document-retention.md`.
1. **`docs/CURRENT_WORK.md`** — the generated bounded attention queue: at most 15 actionable,
   waiting-Joseph, or externally blocked leaves. Never hand-edit it; change the checked-in
   `docs/orchestration/control-plane/` sources and regenerate. Open the cited `OI-*` row before acting.
2. **`docs/orchestration/PLAYBOOK.md`** — the generated 15–25 active process rules every session
   applies. Each rule points to its `BEN-*` evidence; read the full finding only when relevant.
3. **`KNOWN_ISSUES.md`** — how the *code* fails. Different axis from the playbook; read both.
4. **`docs/orchestration/CLAIMS.md`** — `CLM-*` physics claims and their verification status. Allowed
   states are `PROVED / VERIFIED-NUMERIC / VERIFIED-CODE / CITED / ASSUMED / OPEN / REFUTED`.
   **Worker agreement is not verification**; promotion needs a recoverable artifact + an independent check.

## Read ON DEMAND, not on entry

**`docs/OPEN_ITEMS.md` and `docs/orchestration/FINDINGS.md`** — the full item record and process
casebook. Search them by the `OI-*` or `BEN-*` routed from the compact views. They preserve amendments,
allocation state, and chronology; their value as evidence is exactly why they are not default context.

**`docs/CURRENT_WORK_BACKLOG.md`** — generated list of active source records not promoted into the
bounded queue. Consult it when reprioritizing; omission from `CURRENT_WORK.md` is not retirement.

**`AGENTS.md`** — the ~500-line domain reference: pipeline, contracts, bin edges, SLURM, and the
`salloc` section. **Read it when you touch the domain it describes, not to orient.** It was removed
from the default entry path on 2026-08-13 because almost none of it is needed to answer *"what should
I do next."*

**Nothing was deleted and no fact moved.** This is a read-ordering change and it is reversible in one
commit. The routing table below still names `AGENTS.md` as the canonical home for domain detail, so a
lane that needs it is one line away — and `CLAUDE.md` remains, per its own header, the only file you are
guaranteed to have read.

**The principle, which should govern the next such change:** a document costs tokens in *every* future
session forever; a check costs zero and cannot be skipped. **Prefer the executable form of any rule you
are tempted to write down.**

## Canonical home per kind of fact

Mirrors the table in `AGENTS.md`. Write a fact in its home; index it everywhere else.

| Kind of fact | Canonical home |
|---|---|
| Verified numbers (anything technote-quoted) | `VALIDATION_LEDGER.md` |
| Bugs, code debt, recurring traps | `KNOWN_ISSUES.md` |
| Current priority and routing | generated `docs/CURRENT_WORK.md`; unpromoted active records in generated `docs/CURRENT_WORK_BACKLOG.md` |
| Open / deferred item records | `docs/OPEN_ITEMS.md` |
| **Active operating lessons** | generated `docs/orchestration/PLAYBOOK.md` (source `control-plane/playbook.tsv`) |
| **How agents/campaigns fail — evidence/casebook** | `docs/orchestration/FINDINGS.md` (`BEN-*`) |
| **Physics claims + verification status** | `docs/orchestration/CLAIMS.md` (`CLM-*`) |
| Current state per workstream | `*_STATUS.md` |
| **What is happening right now** (campaign, DAG node, owners, live jobs, watches) | `docs/orchestration/LIVE-STATE.md` (generated) |
| Chronology | `*_RUN_LOG.md` (append-only) |
| Durable invariants & gotchas | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` |
| Deliverables | `docs/analysis-note/` (Overleaf subtree, three builds) |

## Hard rules

These are bootstrap and repository-integrity constraints that apply before task-specific work. Recurring
operating rules live only in the generated `PLAYBOOK.md`; do not copy them back into this section.

- **A result does not exist until its commit lands.** The commit introducing a campaign's
  scripts/launchers must also carry its products summary, the ledger entry, the RUN_LOG entry, and the
  STATUS one-liner. Other sessions run this repo concurrently — unpushed work is invisible to them.
- **Audit and review lanes get read-only tooling.** `codex exec --sandbox read-only`, or
  `claude -p --allowedTools "Read,Grep,Glob,Bash"`; give `agy` a throwaway `git worktree`. A pure audit
  prompt has already caused a delegate to silently refactor a training loss in a file that was
  hash-pinned into a gate two hours later. Always `git status` after a delegate finishes, and preserve
  the diff before reverting — parts of it may be real findings.
- **Deletions and top-level reorgs are frozen** behind `docs/POST_PUBLICATION_REORG_PLAN.md`'s freeze
  tag. `nd-unfolding/`'s root is at capacity — put new work in the subdirectory that owns it.
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

Search `FINDINGS.md`, its archives, and long-form findings before filing. Amend or cross-reference an
existing `BEN-*` when the reusable mechanism is already represented. Add a new row only when the
failure is a genuinely new reusable mechanism that changes an executable check, an active playbook
rule, or an existing BEN's scope. If it needs more than a compact row, write
`docs/orchestration/FINDING-<YYYYMMDD>-<slug>.md` **and add it to the index at the top of FINDINGS.md**.
Promote it to `PLAYBOOK.md` only if every new session should act differently because of it.
