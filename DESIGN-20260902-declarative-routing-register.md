# DESIGN 2026-09-02 — replacing prose-derived routing in the control plane

**CITABLE FOR:** the measurements in §1, taken at `dae18f22` in an isolated worktree; the two designs
in §3 and §4; the recommendation in §5; the migration, compatibility, rollback, mutation-test and
acceptance specifications in §6–§10.

**NOT CITABLE FOR:** any authorization. This is **design only**. Nothing here adopts an artifact,
closes an `OI-*`, moves a gate, re-classifies a row, launches compute, changes a publication claim,
or discharges `OI-73`. **Gate 2 remains FAIL.** PET `C_stat` remains
`EXISTS — UNVERIFIED, PAIRING DECLINED`. The five Gate-6 prohibitions stand unmodified; this
document does not reproduce, paraphrase, or depend on them.

**STATUS: UNTRACKED and UNCOMMITTED, deliberately.** Under `AGENTS.md`'s rule that a result is live
only once its records land in a commit, nothing here is live evidence. It sits at the repository root
alongside the other untracked proposal files rather than in `docs/orchestration/`, because a new `.md`
there is born `ARCHIVAL` (`generate_manifest.py:141`) and would need a `MANIFEST-overrides.tsv` row
plus a `CATALOG.md` route to be visible to the router at all. §6.6 states what landing it requires.

**Governing record: `OI-73`** (`docs/OPEN_ITEMS.md:118`), owner *repo infrastructure / control plane*.
It is the only `OI-*` row that names `source_classification` or `ordered_rules`. It already contains
the diagnosis and a **binding constraint on the remedy**, quoted verbatim in §2.3.

**Superior authority checked: `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`**,
sha256 `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064`, verified against the
committed blob at `dae18f22` (`git cat-file -p HEAD:<path> | shasum -a 256` — identical, so the
worktree copy is not a local edit). Read in full. **It does not conflict with this design**, which
touches no covariance subject, no compute, no spend and no publication claim; §12 records the
per-ruling impact. Two of its clauses bear on this work and are honoured:

- **§5** withholds regeneration of `LIVE-STATE.md` *"pending `OI-73`'s owner"* — independent
  corroboration, from a record Joseph ruled, that `OI-73` is the governing row here and that its
  owner holds the decision this design defers to.
- **§4 item 6** assigns the orchestration lane a meter for `R5`'s stop, and flags it as *"the one
  that fails silently"*. §3.3's typed `terminal_criterion` is a place such a criterion could be
  declared **if** that lane files a row for it. This design neither discharges item 6 nor claims to.

---

## 1. The defect, measured

Measured at `dae18f22` (`HEAD == origin/main`, fetched 2026-09-02), in the isolated worktree
`.claude/worktrees/routing-redesign-20260902`. Every command is given so it can be re-run.

Generated state was **not** regenerated: `generate_live_state.py --check-freshness` reports
`STALE :: Git: 712de1b, HEAD dae18f22`, and the instruction to withhold regeneration pending
`OI-73`'s authored-input defect is honoured. Nothing below reads `LIVE-STATE.md`.

### 1.1 Routing today is a regex over free prose, with a permissive default

`control_plane_lint.py:139-156` classifies each `OI-*` row by applying
`policy.json → source_classification.ordered_rules` — four unanchored-or-`^`-anchored regexes — to
**column 2 of `docs/OPEN_ITEMS.md`**, a free-prose cell up to 3,940 characters wide. No match falls
through to `default`, which is `{"lifecycle": "active", "queue": "NOW", "rule": "safe-default-active"}`.

```
python3 docs/orchestration/control_plane_lint.py --coverage-report
```

| classification rule | records | share |
|---|---:|---:|
| `safe-default-active` → `active/NOW` | **65** | 47.4% |
| `explicit-terminal-prefix` → `retired` | 30 | 21.9% |
| `explicit-blocker` → `active/BLOCKED-EXTERNAL` | 20 | 14.6% |
| `explicit-user-decision` → `active/WAITING-JOSEPH` | 19 | 13.9% |
| `explicit-deferred-prefix` → `deferred` | 2 | 1.5% |
| `pointer-to-canonical-OI-122` (the one human override) | 1 | 0.7% |
| **total** | **137** | |

**136 of 137 routing decisions are machine-inferred from English. One is declared.**

### 1.2 Ten of the thirteen rows on `CURRENT_WORK.md` are there because no rule matched

`docs/CURRENT_WORK.md` is the page `AGENTS.md` routes every session to for "what should happen next".
Per-row provenance of its current membership:

| promoted item | rule that set its source queue | derived | override | effective |
|---|---|---|---|---|
| OI-71, OI-75 | `explicit-user-decision` | WAITING-JOSEPH | – | WAITING-JOSEPH |
| OI-73 | `explicit-blocker` | BLOCKED-EXTERNAL | – | BLOCKED-EXTERNAL |
| OI-131(a) | `safe-default-active` | NOW | WAITING-JOSEPH | WAITING-JOSEPH |
| OI-131(b) | `safe-default-active` | NOW | BLOCKED-EXTERNAL | BLOCKED-EXTERNAL |
| OI-70, 93, 123, 125, 127, 128, 129, 130 | `safe-default-active` | NOW | – | NOW |

**10 of 13** rest on `safe-default-active`. `queue_override` is used **twice**, both on the one split
record (`OI-131`). The human declaration channel that exists today is almost entirely unused; the
regex is doing the work.

### 1.3 Four measured failure modes, not hypotheticals

**(a) The rule reads a buried historical sentence as the current state.** `OI-126`'s state cell is
3,659 normalized characters. Its head reads *"RULED BY JOSEPH 2026-08-20 — THIS ROW NO LONGER NEEDS A
RULING AND IS NOT A LIVE SCIENTIFIC QUESTION."* `AGENTS.md:74` says it *"has left the routed queue."*
The classifier matches `NEEDS JOSEPH'S RULING` at **offset 2868** — inside a superseded narrative
paragraph — and routes it `active/WAITING-JOSEPH`.

`docs/CURRENT_WORK_BACKLOG.md:94` therefore renders, on one line, a derived queue of `WAITING-JOSEPH`
beside that row's own printed state prefix saying it no longer needs a ruling. **The generated view
contradicts itself and the front door, in the same row.**

**(b) `BLOCKED-EXTERNAL` is a keyword artifact across up to 20 rows.** The entire rule is
`\bBLOCKED\b`. It cannot distinguish genuinely external (`OI-135`, *"BLOCKED ON
maintenance_20260819"*) from blocked on our own code (`OI-73`, *"BLOCKED BY A CODE DEFECT"* in a file
this repo owns) from blocked on a decision (`OI-3`, *"the blocker is a decision not compute"*). It
also matches inside a negation: `OI-60` reads *"IT IS NOT 'BLOCKED ON NOTHING'"*. `BLOCKED-EXTERNAL`
carries queue weight 10 against `NOW`'s 30, so an unanchored regex demotes `P1` work — including
`OI-73` itself, the row that documents the defect.

**(c) The terminal rule is `^`-anchored, so terminal prose that is not first does not retire.**
Rows whose heads read `FIXED AND LANDED 2026-08-21 … NO LONGER AWAITING A USER DECISION` (`OI-149`),
`COMPLETE 2026-08-21` (`OI-147`), `DECIDED 2026-08-15` (`OI-6`) all fall to `safe-default-active` and
render as `NOW`. Conversely `OI-140` and `OI-141` are routed `WAITING-JOSEPH` off a bare trailing
`WAITING-USER` token appended after 560–667 characters of "LANDED"/"FIXED" narrative.

**(d) The default is silently permissive in the direction that costs the most.** An unrecognised
state — including a brand-new row typed as `OPEN` and a row someone rewrote in a hurry — becomes
`active/NOW`, the highest-weight queue. There is no state a lane can write that means *"I have not
classified this."* Absence of classification is indistinguishable from a positive claim of urgency.

### 1.4 Root cause

`docs/OPEN_ITEMS.md`'s own header records the mechanism this design must not reproduce:

> *"Before 2026-08-20 all nine READ as live because their corrections were appended at the END of
> multi-thousand-character fields, so a session working the list top-to-bottom worked the wrong queue."*

A single prose cell is being asked to carry **two incompatible things**: an immutable narrative
history, and a current machine-readable routing state. Any reader — human or regex — must decide
which sentence in it is the live one, and the cell provides no marker. The regexes are not badly
written; **the input has no current-value field to read.**

---

## 2. Requirements and constraints

### 2.1 Target (from the request)

Explicit structured **lifecycle, queue, owner, artifact, action, authority, terminal criterion,
evidence route**; ordinary English in `OPEN_ITEMS.md` must never change routing; zero
`safe-default-active`; no regex-derived queue decisions; historical prose preserved, not rewritten.

### 2.2 What "no regex-derived queue decision" must mean precisely

A regex will still appear in the instrument, and the claim must be scoped to survive that. The
testable form:

> **No character of `docs/OPEN_ITEMS.md` outside the `| OI-N |` id token may influence any rendered
> `lifecycle` or `queue` value.**

Residual regexes and why each is permitted:

| site | purpose | decides a queue? |
|---|---|---|
| `source_oi_rows` `^\|\s*(OI-\d+)\s*\|` | **enumerates** which records exist and assigns `#k` occurrence keys | no — identity only |
| `natural_item_key`, `parent_item` | key syntax validation and sort order | no |
| `terminal_criterion` prefix check (§3.3) | shape validation of a declared field | no — validates, never selects |
| `normalize_state` + `ordered_rules` | **classification** | **yes — deleted** |

Mutation test M1 (§9) is the executable form of the claim.

### 2.3 The governing constraint from `OI-73`, verbatim

> *"**NOT FIXED HERE, DELIBERATELY:** refining the rule re-classifies up to 20 rows and therefore
> changes the work queue every future session reads, and at least one of the 20 is correctly
> classified — so it wants a **deliberate per-row pass by the `policy.json` owner**, not a regex swap."*

Three consequences that bind this design:

1. **A better regex is disqualified by the governing row.** Any design whose migration is "swap the
   pattern" is out of scope regardless of its merits.
2. **The re-classification is the owner's act, not the instrument's.** The design may supply the
   worksheet and the mechanism; it may not decide the 137 values. §6 keeps those in separate commits.
3. **Landing the structure must not silently move the queue.** Hence the structural/behavioural split
   in §6, with a byte-identity acceptance test on the first stage.

### 2.4 Blast radius of the vocabulary — measured, and small

```
grep -rln --include='*.py' --include='*.json' --include='*.sh' --include='*.tsv' \
     -e 'source_classification' -e 'ordered_rules' -e 'BLOCKED-EXTERNAL' .
```

Code and config consumers of the classification vocabulary are **`control_plane_lint.py` and
`control-plane/policy.json` only**. `source-record-inventory.tsv` and `work-items.tsv` are data;
`state/RECEIPT-20260828-user-authorized-root-probe.json` contains the token as recorded text, not as
a control input.

Incidental, reported not repaired: `MANIFEST.tsv:248` lists `usagectl.py` and `test_usagectl.py` as
consumers of `control-plane/policy.json`, but `usagectl.py:26` reads `usage-policy.json` — a
different file. The consumer column looks substring-derived. Same class as `OI-70`; it makes the
manifest **overstate** this design's blast radius, so no plan here depends on it.

---

## 3. Design A — the declarative routing register (extend `work-items.tsv`)

**One sentence:** promote `work-items.tsv` from a 13-row *promotion* table into the 138-row *routing
register* that declares every record's routing outright, and reduce the classifier to a lookup.

### 3.1 Shape

`policy.json` loses `source_classification.ordered_rules` and `source_classification.default`
entirely. It keeps the vocabularies and weights and gains one switch:

```json
"routing": {
  "unregistered_record": "fail",
  "lifecycles": ["active", "deferred", "retired"],
  "queues": ["NOW", "WAITING-JOSEPH", "BLOCKED-DECISION",
             "BLOCKED-INTERNAL", "BLOCKED-EXTERNAL"],
  "authority_kinds": ["record", "self-filed", "unassigned", "migration-carried-forward"],
  "terminal_criterion_kinds": ["commit", "measure", "ruling", "build", "never"]
}
```

`classify_source_records()` becomes:

```python
def declared_routing(record_key, register):
    row = register.get(record_key)          # no fallback, no default, no regex
    if row is None:
        raise Unregistered(record_key)      # -> CONTROL-PLANE FAIL, exit 1
    return row.lifecycle, row.queue
```

`normalize_state()` and the four patterns are **deleted**, not disabled. Deletion is what makes
mutation test M1 pass by construction rather than by configuration.

### 3.2 Register schema — 14 columns, one row per work item

`docs/orchestration/control-plane/work-items.tsv`. Columns 1–2 and 6–8 and 13 exist today; the rest
are new. `queue_override` is **removed**: `queue` is now primary, not a correction to an inference.

| # | column | domain | required when |
|---:|---|---|---|
| 1 | `item` | `OI-N` \| `OI-N(a)` | always |
| 2 | `source_record` | `OI-N` \| `OI-N#k` | always |
| 3 | `lifecycle` | `active` \| `deferred` \| `retired` | always |
| 4 | `queue` | one of `routing.queues`, or `-` | `-` unless `active` |
| 5 | `promotion` | `promoted` \| `backlog` \| `-` | `-` unless `active` |
| 6 | `owner_id` | key in `owners.tsv` | always |
| 7 | `impact` | key in `impact_weights`, or `-` | non-`-` iff `promoted` |
| 8 | `urgency` | key in `urgency_weights`, or `-` | non-`-` iff `promoted` |
| 9 | `artifact` | repo-relative path, `sha256:<64hex>`, `job:<id>`, or `-` | non-`-` iff `promoted` |
| 10 | `next_action` | 1–260 chars, or `-` | non-`-` iff `promoted` |
| 11 | `authority` | `<tracked-path>#<anchor>` \| `self-filed:<YYYY-MM-DD>` \| `unassigned` \| `migration-carried-forward` | always |
| 12 | `terminal_criterion` | `<kind>: <text>` with kind in `terminal_criterion_kinds`, or `-` | non-`-` iff `active` |
| 13 | `evidence` | must contain `OPEN_ITEMS.md` | always |
| 14 | `state_digest` | sha256 of the normalized state cell at declaration time, or `-` | optional, **report-only** |

Worked rows (illustrative; the values are the owner's to set, not this design's):

```
OI-73   OI-73  active  BLOCKED-INTERNAL  promoted  lane_c  infrastructure  P1  docs/orchestration/generate_manifest.py  Correct the live-state.json lifecycle classification and distinguish authored input from generated output.  self-filed:2026-08-14  commit: MANIFEST.tsv row for state/live-state.json reads a non-generated event_status and live-state.json is editable by its owner  docs/OPEN_ITEMS.md (`OI-73`)  sha256:…
OI-126  OI-126 retired -                 -         joseph  -               -   -                                        -                                                                                                              docs/OPEN_ITEMS.md#OI-126-ruling-2026-08-20  -                                                                                                                       docs/OPEN_ITEMS.md (`OI-126`)  sha256:…
OI-131(a) OI-131 active WAITING-JOSEPH   promoted  joseph  provenance      P1  nd-unfolding/uq_5d/                       Decide whether an irreplaceable subset of the CFS-only P3F objects warrants a second copy.                     self-filed:2026-08-18  ruling: Joseph rules on the second copy                                                                                docs/OPEN_ITEMS.md (`OI-131`)  sha256:…
```

### 3.3 The eight target fields, and where each lands

| target | column | enforcement |
|---|---|---|
| lifecycle | 3 | closed vocabulary |
| queue | 4 | closed vocabulary; `-` iff not `active` |
| owner | 6 | foreign key into `owners.tsv`; unassigned owners still auto-route per existing policy |
| artifact | 9 | shape-checked (path / `sha256:` / `job:`); path existence checked for repo-relative forms |
| action | 10 | length-bounded, required for promoted |
| authority | 11 | closed kinds; `record` form must name a **tracked** path |
| terminal criterion | 12 | typed prefix + non-empty body |
| evidence route | 13 | must route to `OPEN_ITEMS.md` (existing rule, retained) |

`terminal_criterion` is deliberately shape-checked, not semantically checked. The lint can prove a
criterion is **typed and present**; it cannot prove it is the right criterion. Stated plainly so a
green run is not over-read.

### 3.4 Cardinality and coherence rules (all lint-enforced)

1. Exactly one register row per `item`; `item` unique.
2. Every `source_record` enumerated in `OPEN_ITEMS.md` has **at least one** register row. Violation →
   `CONTROL-PLANE FAIL: OI-189 has no routing declaration` — the fail-closed rule that makes
   `safe-default-active` structurally unreachable, now and for every future row.
3. Every register row's `source_record` exists in `OPEN_ITEMS.md` (existing orphan check, retained).
4. `lifecycle` is **identical across all rows sharing a `source_record`.** Queue may differ per item
   (that is what `OI-131(a)`/`(b)` needs); lifecycle may not.
5. `lifecycle != active` ⇒ columns 4, 5, 7, 8, 9, 10, 12 are all `-`. A retired row cannot carry a
   score, an action, or a queue.
6. `promotion == backlog` ⇒ `impact` and `urgency` are `-`, so an unpromoted row cannot carry a
   latent score that a later promotion silently inherits unreviewed.
7. `authority == migration-carried-forward` is accepted only while `policy.routing.migration_open`
   is `true` (§6, Stage 3 flips it and the value becomes an error).

### 3.5 What the queue vocabulary gains, and who decides it

`OI-73` names three things `BLOCKED-EXTERNAL` conflates. The register can express them:
`BLOCKED-EXTERNAL` (a third party or facility), `BLOCKED-INTERNAL` (our own code or tree),
`BLOCKED-DECISION` (a ruling, distinct from `WAITING-JOSEPH` when the decider is not Joseph).

**This design does not set their weights.** `queue_weights` are what order `CURRENT_WORK.md`, and
`OI-73` reserves that to the `policy.json` owner. The migration (§6) therefore lands the two new
tokens **unused, with weights absent**, and adds them to `queue_weights` only in the behavioural
stage, in a commit the owner signs. A queue token with no weight is a lint error, so the two cannot
be used before they are priced — the guard and the vocabulary land together.

### 3.6 Honest costs

- **`work-items.tsv` grows from 2.4 KB / 13 rows to roughly 40–50 KB / 138 rows.** It is
  `read_policy=route-only` and is not on the prescribed reading path, so this does not move
  `--entrypoint-report`. It does become a much larger merge surface — see §7.3.
- **Filing an `OI-*` row becomes a two-file edit, enforced.** It is already a two-file edit in
  practice (the row must reconcile with `source-record-inventory.tsv`); this makes the coupling
  explicit and mechanical instead of discovered at commit time.
- **104 `terminal_criterion` values must be authored** (the current active population). That is the
  bulk of the migration labour and is the point of it: a record with no statable terminal criterion
  is a record nobody can close.

---

## 4. Design B — the append-only routing-event ledger

**One sentence:** routing state stops being a stored value and becomes the **fold of an append-only
ledger of authorized transitions**; `work-items.tsv` becomes a generated projection.

### 4.1 Shape

New file `docs/orchestration/control-plane/routing-events.tsv`, append-only, one row per transition:

```
event_id  at_utc  actor  source_record  item  to_lifecycle  to_queue  owner_id
          impact  urgency  artifact  next_action  authority  terminal_criterion  evidence
```

- Current routing for an item = the **last event by `at_utc`, tie-broken by `event_id`**.
- `authority` is mandatory on every event; there is no way to change routing without citing a record.
- Retirement is an event, never a deletion; the ledger is never rewritten.
- `work-items.tsv` and `source-record-inventory.tsv` both become **generated** from the fold, and
  `CURRENT_WORK.md` renders from the fold.
- A ruling that moves many rows — e.g. `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
  — lands as one batch of events sharing one `authority`, which is a genuinely nice property.

### 4.2 What B does better than A

1. **Authority is intrinsic, not a column that can be left stale.** A row's routing cannot exist
   without the event that created it, and the event carries who authorized it and when.
2. **"Why is this `WAITING-JOSEPH`?" is answerable by query, not by prose archaeology.** That is the
   precise question §1.3(a) shows nobody can currently answer for `OI-126` without reading 3,659
   characters and guessing which sentence is live.
3. **History is preserved by construction**, which sits well with
   `CONVENTION-document-retention.md:49` — *"Do not move, rename, or delete to express retirement.
   Paths are provenance."*
4. **It matches the repository's existing idiom** — `RUNS.tsv`, receipts, `DECISION-*` records are all
   append-only evidence.

### 4.3 Why it is nonetheless the wrong instrument here

1. **It re-creates the exact failure mode being removed, one layer up.** `OPEN_ITEMS.md` already *is*
   an append-only log inside a cell. Its measured defect is that corrections appended at the end of a
   long field were not recognised as the live value. A fold makes "which entry is current" a
   computed property again — correct in the instrument, but the moment a lane reads the ledger
   directly (and they will; it is the interesting file) the same ordering trap is back. Design A's
   register has exactly one row per item and no ordering semantics at all.
2. **`git revert` stops restoring routing.** Rollback needs a compensating event. For a control plane
   whose stated integrity rule is that a result is live only once committed, losing revert as the
   rollback primitive is a serious regression (§8).
3. **Concurrent lanes conflict at the tail.** The snapshot records 43 `claude|codex` processes and a
   shared `main`. Every lane appends to the same last line of the same file; a mis-resolved conflict
   silently reorders the fold and therefore silently changes routing. Design A's conflicts are
   line-local to the row being edited and are caught by the uniqueness rule.
4. **It is a new framework.** It adds a derivation layer under `CURRENT_WORK.md`, makes two currently
   hand-authored files generated, needs its own `MANIFEST` classification, its own freshness story,
   and its own compaction policy once the ledger passes a few thousand rows.
5. **Unbounded growth on a file the pre-commit hook parses on every commit** in every lane.

B is the better *record*. A is the better *control plane*. The failure being fixed is a control-plane
failure.

---

## 5. Recommendation

**Adopt Design A.** It is smaller on every axis that matters here: one file gains columns, one
function is deleted, no file changes from authored to generated, no new derivation layer, no new
document class, and `git revert` remains the rollback primitive. It satisfies all eight target
fields, and — the decisive property — it makes `safe-default-active` **structurally unreachable**
rather than merely currently-empty, because an unregistered record fails the commit.

It also composes with `OI-73`'s constraint instead of fighting it: the deliberate per-row pass the row
reserves to the `policy.json` owner **is** Design A's Stage 2, and the design supplies the worksheet
and the mechanism without making any of the 137 decisions.

Keep one idea from B: `authority` and `terminal_criterion` as mandatory columns. They are most of B's
value and cost A nothing structurally.

---

## 6. Migration

Five stages. **Structural and behavioural changes are in separate commits throughout**; no stage both
moves a queue and changes the instrument.

### Stage 0 — worksheet (no commit)

Run the current classifier and emit a candidate register to the scratchpad, one proposed row per
item, each tagged with the rule that produced it and the full state cell for review. Deliverable: a
137-row review worksheet grouped by owner.

**This worksheet must not be committed as the answer.** Committing it directly would convert 65
unexamined defaults into 65 apparent declarations and destroy the very distinction the redesign
exists to create. It is an input to human review, nothing else.

### Stage 1 — structural, behaviour-preserving

- Add columns 3–5, 9, 11, 12, 14 to `work-items.tsv`; remove `queue_override` (fold its two `OI-131`
  values into `queue`).
- Populate all 138 rows from the Stage-0 worksheet **transcribed exactly**, reviewed for transcription
  fidelity only, not for correctness. Rows whose values came from a regex or the default carry
  `authority = migration-carried-forward`.
- Replace `classify_source_records` with the register lookup; delete `normalize_state`,
  `ordered_rules`, `default`. Add `policy.routing` with `migration_open: true`.
- Land the `BLOCKED-INTERNAL` / `BLOCKED-DECISION` tokens in the vocabulary **with no weights and no
  users** (§3.5).

**Acceptance:** `docs/CURRENT_WORK.md`, `docs/CURRENT_WORK_OVERFLOW.md` and
`docs/CURRENT_WORK_BACKLOG.md` are **byte-identical** to their bytes at the parent commit.
`source-record-inventory.tsv` differs in the `classification_rule` column only, whose values become
`declared` / `declared-override` / `migration-carried-forward`. That byte-identity is the proof the
structural change moved nothing.

### Stage 2 — behavioural, per-row, batched by owner

The deliberate pass `OI-73` reserves. One commit per owner batch; each changed row's `authority`
moves off `migration-carried-forward` and names a committed record or `self-filed:<date>`.

Rows the measurement in §1.3 says will be examined first — **none of these is decided here**:

- `OI-126` — head and `AGENTS.md:74` both say it has left the queue; currently `WAITING-JOSEPH`.
- The 20 `\bBLOCKED\b` rows — the three-way split, including `OI-73`, `OI-60`, `OI-7`.
- `OI-140`, `OI-141`, `OI-143` — trailing `WAITING-USER` after "LANDED"/"FIXED" narrative.
- `OI-149`, `OI-147`, `OI-6`, `OI-57` — terminal-reading heads currently rendering `NOW`.
- The remaining `safe-default-active` rows, which have never been classified by anyone.

`queue_weights` for the two new tokens are set here, in the owner's commit, and only if the owner
uses them.

### Stage 3 — ratchet

Flip `policy.routing.migration_open` to `false`. `authority == migration-carried-forward` becomes a
lint error. Assert `classification_rule` values are drawn only from the declared set. After this
commit the permissive default cannot be reintroduced without a policy change that fails its own
self-test.

### Stage 4 — documentation

Update the "Machine-enforced contract" block in `render_current()`, which currently states *"Source
lifecycle and queue are derived from explicit OI state language"* and *"`policy.json` classifies
explicit source state"*. Both become false at Stage 1 and must change in the same commit that makes
them false — this is a Stage-1 obligation, listed here only so it is not lost.

### 6.5 Coupled files — every stage

`source-record-inventory.tsv` is generated and `MANIFEST.tsv` pins its line and byte counts
(`MANIFEST.tsv:249`, currently `138` lines / `24363` bytes), as it does for `work-items.tsv`
(`:250`) and `policy.json` (`:248`). Any stage that changes those files must regenerate `MANIFEST.tsv`
**in the same commit**, and the regeneration must run from a clean checkout per `OI-73`'s stated
precondition. A stage that edits only the control-plane TSVs is not a complete file-set.

### 6.6 What landing this design document itself would require

A `MANIFEST-overrides.tsv` row declaring it `LIVE`, a `CATALOG.md` route (else
`live_doc_indexed.py --check` fails the commit), and a `MANIFEST.tsv` regeneration. Not done here —
this is design only, and the document is deliberately untracked.

---

## 7. Compatibility

### 7.1 Unchanged

`docs/CURRENT_WORK.md`, `CURRENT_WORK_OVERFLOW.md`, `CURRENT_WORK_BACKLOG.md` and `PLAYBOOK.md` keep
their paths, table shapes and column headers. `source-record-inventory.tsv` keeps its path and its six
column names. `owners.tsv` and `playbook.tsv` are untouched. `AGENTS.md`'s evidence routes are
untouched. The bootstrap contract, the entrypoint report and the orchestration-volume measurement are
untouched.

### 7.2 Changed, with the consumer set measured in §2.4

- `work-items.tsv` column set changes → the only reader is `control_plane_lint.py`.
- `policy.json` loses `source_classification`, gains `routing` → the only reader is
  `control_plane_lint.py` (`usagectl.py` reads a different file; §2.4).
- `source-record-inventory.tsv`'s `classification_rule` **values** change vocabulary; the column and
  its position do not. Documents that cite the file by name (`CATALOG.md`,
  `AUDIT-FINDINGS-20260820.md`, three `FINDING-*`/`GRADE-*` records) cite the artifact, not the
  vocabulary, and are unaffected.

### 7.3 The one real regression, stated

`work-items.tsv` becomes a hot shared file: 138 rows written by every lane that files an `OI-*`,
against 13 rows written rarely today. Mitigations: one line per item, stable sort key, and a
uniqueness rule that turns a duplicated line from a bad merge into a lint failure rather than a
silent double declaration. This does not eliminate conflicts, it makes them line-local and loud. If
that proves too painful, the register can be sharded by owner into `work-items.d/<owner>.tsv` without
any change to the schema or the classifier — noted as a known escape hatch, not proposed now.

---

## 8. Rollback

| stage | rollback | restores routing? |
|---|---|---|
| 1 | `git revert` the single commit; generated outputs regenerate | yes, exactly — byte-identity is the Stage-1 acceptance test in both directions |
| 2 | `git revert` the owner batch commit, or edit the specific row back | yes, per row |
| 3 | `git revert`; `migration_open` returns to `true` | yes |
| any | partial: set one row's `authority` to `migration-carried-forward` and its values back | yes, and the row is then visibly unreviewed again |

Rollback is `git revert` throughout because routing is a **stored current value in tracked lines**, not
a fold. Per-row history is `git log -L` on the register line, or simply the `authority` column, which
is self-describing and needs no archaeology. Do not use `git log -S` to date when a routing state
existed; it dates the commit, not the state.

---

## 9. Mutation tests

Extending `control_plane_lint.py --self-test`, which runs as a pre-commit check in every lane. Every
case asserts the **specific error text**, not merely a non-zero exit, because a mutation can be
refused by an earlier column validator and produce the right exit code for the wrong reason.

Fixtures are built from the **producer**: the OPEN_ITEMS rows used below are copied verbatim from real
rows (notably `OI-126`'s actual state cell), never hand-written to match the rule under test.

**The claim under test — prose is inert:**

- **M1 (the acceptance test for the whole redesign).** Take a real declared row. Apply, one at a
  time: prepend `CLOSED`, prepend `FROZEN`, insert `WAITING-USER`, insert `BLOCKED`, delete the
  existing `NEEDS JOSEPH'S RULING`, replace the whole cell with `OPEN`. **Assert the rendered
  lifecycle and queue are identical in all six.** Each of these flips the queue under the current
  engine; that is what makes this a power test and not a tautology.
- **M2 (both directions of contradiction).** A row whose prose says `CLOSED` and whose declaration
  says `active/NOW` renders `active/NOW` with **no error**; its mirror — prose `OPEN`, declaration
  `retired` — renders `retired` with no error. Prose that contradicts the declaration is not a defect;
  it is the design working.

**The claim under test — declarations are live:**

- **M3 (the guard fires).** Change the register's `queue` cell; assert the rendered queue changes,
  and the score changes by exactly the weight delta.
- **M4 (fail-closed on absence).** Add `| OI-999 | OPEN | … |` to the fixture with no register row;
  assert exit 1 and a message naming `OI-999`. This is the test that `safe-default-active` is
  unreachable.
- **M5 (orphan).** A register row for a record absent from `OPEN_ITEMS.md` → error naming it.
- **M6 (duplicate).** Two rows for one `item` → error. Simulates the bad-merge case from §7.3.

**Vocabulary and coherence:**

- **M7.** `queue = SOON`; `lifecycle = maybe`; `owner_id = nobody`; `authority = handwave`;
  `terminal_criterion = someday it will be fine` (no typed prefix) — each its own error.
- **M8.** `lifecycle = retired` with a non-`-` queue → error. `lifecycle = active` with `queue = -` →
  error. Both directions of rule 5.
- **M9.** Two rows for one `source_record` with different `lifecycle` → error (rule 4). Two rows with
  the same lifecycle and **different queues** → accepted (the `OI-131` case must keep working).
- **M10.** `promotion = promoted` with `next_action = -` → error. `promotion = backlog` with
  `impact = publication` → error (rule 6).
- **M11.** A queue token present in `routing.queues` but absent from `queue_weights` → error. This is
  what stops `BLOCKED-INTERNAL` being used before it is priced.
- **M12.** `authority = migration-carried-forward` with `migration_open: false` → error; with
  `migration_open: true` → accepted. Both arms, or Stage 3's ratchet is untested.

**Report-only, must not route:**

- **M13.** Edit a state cell so `state_digest` no longer matches. Assert **(a)** the rendered queue is
  unchanged, **(b)** the run still exits 0, **(c)** the summary line reports the drift count.
  `state_digest` must never fail a commit: corrections appended to active rows are this repository's
  normal working mode, and a guard that fires on every correct run is not a guard.

**Instrument integrity:**

- **M14 (negation).** Assert the module defines no `normalize_state` and that `policy.json` contains
  no `ordered_rules` key — a direct test that the classifier was deleted rather than bypassed.
- **M15 (reachability).** For each of M4–M12, assert the error is the *expected* one, so a case
  refused by an earlier validator cannot pass as a success of the rule it was written for.

---

## 10. Acceptance criteria

Measured, in this order, on a clean checkout:

1. `control_plane_lint.py --coverage-report` prints **`safe-default-active: 0`**, and after Stage 3
   the rule histogram contains only `declared` and `declared-override`.
2. `137/137` records classified; **0** unregistered; **0** orphan; **0** duplicate.
3. `grep -c 'ordered_rules\|source_classification' docs/orchestration/control-plane/policy.json` → 0.
4. `grep -c 'def normalize_state' docs/orchestration/control_plane_lint.py` → 0.
5. Every `active` row carries a typed non-empty `terminal_criterion`; every row carries an
   `authority`; **0** rows carry `migration-carried-forward` after Stage 3.
6. Stage 1 only: the three rendered work surfaces are byte-identical to the parent commit's.
7. `control_plane_lint.py --self-test` passes with M1–M15 added, and each of M4–M12 is verified to
   fail for its own stated reason.
8. All 12 pre-commit checks pass (`.githooks/pre-commit:222-256`), including `--adoption-check`, `live_doc_indexed.py --check` and
   `generate_manifest.py --self-test`.
9. `MANIFEST.tsv` is regenerated in the same commit as every control-plane file change, from a clean
   main checkout.
10. `OI-73`'s row is updated to record what this discharges and what it does not. **It is not
    closed here**: `OI-73` also carries the `live-state.json` authored-input half, which this design
    does not touch, and closure is its owner's classification call.

---

## 11. What this design does not do

It does not decide any of the 137 routing values, re-classify the 20 `BLOCKED` rows, set weights for
the two new queue tokens, close or downgrade any `OI-*`, touch `live-state.json` or its generator,
regenerate any state, alter `AGENTS.md`'s routes, or change what any scientific record claims.

`OI-126` remains routed as it is today until its owner declares otherwise in Stage 2; §1.3(a)
measures the contradiction between the generated view and the front door, and does not resolve it.
**Nothing here reopens the PET question.** `R6` reaffirms that PET is diagnostic and
method-development, that only estimator-equivalence **plus** coverage reopens it, and that coverage
is a different object from verifying the construction. A *routing* declaration that `OI-126` is
`retired` — if its owner makes one — would record that the row needs no further turn, and would be
neither a scientific promotion nor a statement about `C_stat`, which remains
`EXISTS — UNVERIFIED, PAIRING DECLINED`.

## 12. `R1`–`R6` impact

| ruling | subject | impact on this design |
|---|---|---|
| `R1` | `(cause 7, G)` permanently OPEN, G retained | none — no covariance subject is named or moved |
| `R2` | one cause-7-only successor `Y`, specification only | none — `Y` is not referenced; no construction, no adoption, and this design does not treat `Y` as a whole-covariance or adoption subject |
| `R3` | cause 7's `M` carries no smallness requirement | none — no leg is graded |
| `R4` | cause-3 seed scan **SUSPENDED** | honoured — no compute is launched, requested, or scheduled |
| `R5` | stop `2026-09-30`, `500`/`500` task-hours; a prohibition, **not** spending authority | honoured — nothing here spends. §4 item 6's meter is noted as another lane's, not discharged |
| `R6` | PET remains **DIAGNOSTIC** | honoured — see above; `C_stat` is never called verified or paired, and the five Gate-6 prohibitions are neither reproduced nor relied on |
