# Proposal — generated control plane over preserved evidence

## Decision

Separate **preservation**, **declared state**, and **organizational consequence**.

- `OPEN_ITEMS.md` and `FINDINGS.md` preserve the full evidence and history.
- `policy.json` classifies explicit leading OI state language with ordered rules and a conservative
  `active/NOW` default; the exact 94-record inventory and row digests are generated.
- Small TSV sources hold facts that cannot be derived: promotion, impact, urgency, accountable role,
  leaf-specific queue overrides, next action, and whether a playbook lesson is active.
- `control_plane_lint.py` deterministically applies classification, ownership escalation, ranking,
  caps, overflow, backlog visibility, and playbook retirement.

This does not infer scientific disposition from detail prose. Humans still write the scientific state
in `OPEN_ITEMS.md`; code converts only explicit state terms such as `CLOSED`, `WAITING-USER`, and
`BLOCKED` into routing consequences. Unknown wording defaults active rather than disappearing.

## Measured problem

At the proposal base (`be4e654b`, 2026-08-18):

| document | rows | words | problem on the live path |
|---|---:|---:|---|
| `docs/OPEN_ITEMS.md` | 94 records, including two duplicated ids | 37,002 | terminal, waiting, deferred, corrections, and chronology share one table |
| `docs/orchestration/FINDINGS.md` | 365 BEN rows; 173 sibling `FINDING-*.md` files | 110,250 | the evidence casebook is prescribed reading for every new session |
| `docs/orchestration/FINDINGS-ARCHIVE-2026-08.md` | historical archive | 57,007 | an earlier split preserved history, but later rows expanded in place again |

The generated layer contains 14 promoted leaves, 59 active unpromoted records, and 22 playbook rules.
All 94 source records are classified: 20 retired, 2 deferred, 16 waiting on Joseph, 19 externally
blocked, and 37 otherwise active. Duplicate ids are distinct occurrence keys. The long records remain
available by exact id. `control_plane_lint.py --entrypoint-report` measures the entire prescribed path,
including `CLAUDE.md`, `CATALOG.md`, `LIVE-STATE.md`, `KNOWN_ISSUES.md`, and `CLAIMS.md`; the
compact-layer count is never substituted for that decision-relevant denominator.

## Authority boundaries

| Question | Authority |
|---|---|
| What is happening right now? | generated `LIVE-STATE.md`, verified against its sources |
| What deserves default attention? | generated `CURRENT_WORK.md` |
| What eligible work fell below the cap? | generated `CURRENT_WORK_OVERFLOW.md` |
| What active source record was not promoted? | generated `CURRENT_WORK_BACKLOG.md` |
| How was every source record classified? | generated `control-plane/source-record-inventory.tsv` |
| What is the item's scientific state and evidence? | `OPEN_ITEMS.md` and cited artifacts |
| What process rules apply to every session? | generated `PLAYBOOK.md` |
| Why does a process rule exist? | `FINDINGS.md`, archives, and long-form findings |
| What values are verified? | `VALIDATION_LEDGER.md` |

`CURRENT_WORK.md` is authoritative only for routing. It cannot change or summarize away the
scientific state in `OPEN_ITEMS.md`. A disagreement sends the reader to the source and makes the
generated view stale; it never makes the shorter sentence win.

## Machine-readable governance

The source directory is `docs/orchestration/control-plane/`:

- `policy.json`: caps, allowed queues, score weights, tie-breaking, and owner-escalation behavior;
- `owners.tsv`: durable role id, display name, accountable holder, escalation, and assigned/unassigned;
- `work-items.tsv`: promoted item/sub-item, distinct source-record key, optional leaf queue override,
  owner id, impact, urgency, one next action, and evidence route;
- `playbook.tsv`: active/retired state, rule, observable check, BEN evidence, and retirement reason.

`source-record-inventory.tsv` is generated from `OPEN_ITEMS.md`; it carries occurrence key, derived
lifecycle/queue, rule name, exact source-row digest, and a short state prefix. It is output, not a
second hand-maintained registry.

The Markdown views are generated and must never be hand-edited.
`control_plane_lint.py --coverage-report` measures all-record classification and promotion coverage;
`--entrypoint-report` measures every prescribed default document; `--adoption-check` fails with the
exact missing occurrence keys until coverage and approval are complete.

### What code decides

1. Explicit terminal, deferred, waiting, and blocked state language maps through ordered checked-in
   rules; unmatched language safely remains `active/NOW`.
2. Duplicate `OI-64` and `OI-65` rows become stable `#1`/`#2` occurrence keys.
3. An unassigned owner is forced to `WAITING-JOSEPH`; it cannot render as `NOW`.
4. Active promoted items receive a score from checked-in impact, urgency, and effective-queue weights.
5. The highest-scoring 15 render in `CURRENT_WORK.md`; deterministic ties use numeric OI id and
   sub-item.
6. Every promoted item below the cutoff renders in `CURRENT_WORK_OVERFLOW.md`. Falling below the cap
   is not silently converted into deferral.
7. Every active source record without a promoted leaf renders in `CURRENT_WORK_BACKLOG.md`.
8. Deferred and retired records cannot enter the bounded queue.
9. Only active playbook rows render. At 25 active rules, promotion requires retirement or
   consolidation in the same source change.
10. A retired playbook row remains in the TSV with its BEN evidence and required reason.
11. The entry file keeps only bootstrap/repository-integrity constraints; BEN-backed recurring rules
   are generated from `playbook.tsv` rather than maintained in two prose copies.

### What humans still decide

- the scientific state language and evidence in `OPEN_ITEMS.md`;
- which active records deserve promotion into the bounded queue;
- whether an item is publication, provenance, safety, infrastructure, or maintenance impact;
- urgency;
- assignment of an accountable durable role;
- the one-sentence next action;
- whether a lesson belongs in every session's playbook.

Those decisions remain explicit and reviewable. Code applies their consequences, makes every
unpromoted active record visible, and refuses structural ambiguity.

## Ownership model

The registry names durable roles, not transient peer sockets or session names. Each assigned role has
an accountable holder and escalation. An unassigned role has no fictitious holder; generation routes
it to Joseph for designation automatically. Live reachability remains runtime state and is never
narrated into this registry.

The prototype deliberately demonstrates this behavior: the existing “repo infrastructure” and
unowned rows render as `WAITING-JOSEPH` with an assignment action rather than appearing actionable.

## BEN admission and playbook pressure

Before adding a BEN, search the ledger, archives, and long forms. A new BEN is admitted only when it
describes a genuinely new reusable mechanism that changes an executable check, an active playbook
rule, or an existing BEN's established scope. Otherwise append a scoped annotation or cross-reference
without rewriting protected historical evidence.

Promotion to the playbook is separate from BEN filing. The active-rule cap forces consolidation;
retirement removes default-read status while preserving the rule, reason, and evidence in the source.

## Adoption gates

The isolated final candidate is marked `canonical_adoption_allowed: true`; nothing is committed or
pushed until mediator approval. `--adoption-check` proves the structural gates below:

1. **Full item coverage — met.** All 94 source records classify mechanically, including occurrence
   keys `OI-64#1`/`#2` and `OI-65#1`/`#2`; 59 active unpromoted records remain visible in backlog.
2. **Policy review — external commit gate.** The mediator approves the ordered classification rules, one `OI-80` override,
   promotion list, impact/urgency weights, and playbook contents as one staged diff.
3. **Ownership behavior — met structurally.** Every promoted `NOW` item resolves through
   `owners.tsv`; unassigned items are
   visibly waiting for designation.
4. **Manifest semantics — repaired and measured.** The generator now inventories tracked plus
   nonignored intended files, emits `tracking`, and excludes ignored artifacts. Regeneration drops
   exactly five old rows, all independently verified ignored (four `.pyc`, one `.out`), and adds 38
   tracked paths accumulated since the stale manifest plus this change. No tracked path is dropped;
   the generated manifest has 1,029 unique tracked rows and zero unused overrides.
5. **Quiet cutover.** This worktree is based at `4ad061b0`; immediately before push, confirm `main`
   still names that commit. If it moved, rebase and rerun rather than landing a stale generated view.
6. **Entrypoint measurement.** Run `control_plane_lint.py --entrypoint-report`, which includes
   `CLAUDE.md` and `CATALOG.md`, rather than reporting only the ledger-to-view reduction.
7. **Explicit approval flag — met in the isolated candidate.** It authorizes generation of final
   canonical bytes, not a commit or push without mediator approval.

## Commit sequence

1. Land one atomic commit containing the manifest-semantics repair, regenerated manifest,
   control-plane generator and sources, generated views, entrypoint routing, and checks. Splitting it
   would require an intermediate generated artifact and create avoidable work.
2. This proposal and the mediator packet are already classified `ARCHIVAL / terminal` in that final
   manifest; neither becomes another standing live document.
3. During a later quiet window, compact the evidence ledgers without changing ids or paths.

Each commit is independently reviewable and reversible. No scientific result, receipt, or historical
row changes in the routing commit.

## Requested mediator ruling

Review this staged implementation in branch `codex/docs-control-plane` and return one of `APPROVE FOR
MIGRATION`, `REVISE`, or `DECLINE`. `APPROVE FOR MIGRATION` approves the classification policy,
promotion/weight choices, manifest repair, bounded playbook, and atomic landing commit as staged.

Approval authorizes push only if `main` still equals `4ad061b0` and the already-passing
automated adoption and repository checks remain green. Otherwise rebase and re-verify.

## Later quiet-window ledger compaction

1. Copy terminal OI rows byte-for-byte into `OPEN_ITEMS-ARCHIVE-YYYY-MM.md`.
2. Keep each cited `OI-*` in `OPEN_ITEMS.md` as a one-line terminal tombstone pointing to its archive
   record. Do not renumber the `OI-64`/`OI-65` collisions.
3. Move long active-item reasoning into `OPEN-ITEM-OI-<id>-<slug>.md`; leave current state, owner,
   one next action, and evidence pointer in the index row.
4. Move every long BEN body into its existing long form or a monthly append-only archive. Leave
   `FINDINGS.md` as the compact index and allocation surface.
5. Preserve old paths and ids; add stable item anchors so evidence routes do not depend on line numbers.

## Later allocation automation

Replace narrated BEN free lists with an allocator that parses filed ids and emits occupied/free
closed blocks. Keep lane ownership as hand-authored input and make freeness derived output. Add an
analogous collision-safe allocator for OI ids. Do not combine this enforcement change with the read
path cutover.

## Non-goals

- No semantic inference from long-form detail, blocker, action, or evidence cells; only explicit state
  language in the source state cell drives routing, with a safe-active default.
- No deletion, path move, renumbering, or reopening of terminal decisions.
- No claim that an unpromoted active record is retired or deferred; all 59 render in backlog.
- No new BEN merely for this information-architecture change.
