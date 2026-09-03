# INTEGRATION 2026-09-03 — Wave 1: frozen structured-routing interface, conflict matrix, and ledger

**CITABLE FOR:** the frozen routing interface in §1, the conflict/dependency matrix in §2, the
integration order in §3, and the per-output ledger in §5. **NOT CITABLE FOR:** any acceptance grade
of this integration (an independent reviewer grades it), any discharge, adoption, gate movement,
launch, spending grant, or publication claim. **Gate 2 remains FAIL. CAND `1 of 7`, QUOTED `0 of 7`.**
No scalar-5D covariance is adopted. PET `C_stat` remains `EXISTS — UNVERIFIED, PAIRING DECLINED`
(`VL132`). The five Gate-6 prohibitions stand exactly as keyed in
`state/gate6-member-trajectories-result-56847059.json`.

**Authority enforced throughout:** `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
(sha256 `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064`, verified against the
committed blob). `R1`: G stays causes 1–6's subject and is retained. `R2`: Y is a separate,
specification-only cause-7 cell that contributes nothing to G's counts or adoption. `R4`: cause-3
compute is suspended. `R5`: a stop, not spending authority. `R6`: PET is diagnostic.

**Context, not authority:** `HANDOFF-20260902-operational-baseline-snapshot.md` (untracked, sha256
`bc9867edba2c730b6beb9e0b5e2d82cc0d01a3295667804892585e4a860573b4`, verified). Its anchor is
`52cbda90`; the integration base is **not** the snapshot anchor.

## 0. Base — re-measured, and the delta from the snapshot anchor

`git fetch origin` then `git rev-parse origin/main` on 2026-09-03: **`dae18f226a5c679e3a60ba7d875e3bfbf43f96ac`**.
The snapshot anchor `52cbda90` is five commits behind it:

```
dae18f22 [fix] Rename the ruling record out of the campaign-token trap, and regenerate MANIFEST
9ce59a59 [decision] Joseph rules all six packet rulings: cause 7's subject and magnitude, cause 3's VOI gate, the stop
d484b812 [packet] Rev. 3: five narrow corrections; the branch table no longer contradicts the rulings
f5a8b905 [packet] Rev. 2: adopt seven audit corrections; rev. 1 is superseded in full
4e3ec826 [packet] Six rulings for Joseph: cause 7's subject and magnitude, cause 3's VOI gate, the campaign stop rule
```

Every Wave 1 envelope that named an actual base named `dae18f22`; session 4 built on session 3's
tip `56b13be1`, whose parent is `dae18f22`. Baseline measured in a clean worktree at `dae18f22`:
pre-commit **12 checks passed**; `generate_manifest.py --check --committed-only` **OK** (708 rows);
`generate_live_state.py --check-freshness` **STALE** (`Git: 712de1b`), as every envelope reported.

Integration branch: `wave1-integration-20260903`, rooted at `dae18f22`, in an isolated worktree.
`main` and the shared primary checkout are not written by this integration.

## 1. THE FROZEN STRUCTURED-ROUTING INTERFACE

Frozen before any code was integrated. The interface is the one session 4 implemented from session
3's design; session 5's renderer is adapted **to** it, not the other way round.

### 1.1 `control-plane/work-items.tsv` — the declared register, 14 columns

```
item  source_record  lifecycle  queue  promotion  owner_id  impact  urgency  artifact
next_action  authority  terminal_criterion  evidence  state_digest
```

- `queue_override` is **removed**. There is no override column; `queue` is the declared value.
- `lifecycle` ∈ `{active, deferred, retired}`; non-active rows carry `-` in the routed columns.
- `promotion` ∈ `{promoted, backlog}` for active rows, `-` otherwise. Only `promoted` rows are
  routes; backlog rows are inventory.
- `queue` ∈ the five-token vocabulary of §1.2; `-` for non-active rows.
- `authority` and `terminal_criterion` carry `migration-carried-forward` until an owner declares
  them; that token is a declared placeholder, not a classification result.
- `state_digest` is `sha256:` over the source row and is what a renderer checks for staleness.

### 1.2 `control-plane/policy.json` — the `routing` block owns the vocabulary

`source_classification` (the prose regex classifier) is **deleted**. `routing` declares:
`migration_open`, `unregistered_record` (`fail`), `lifecycles`, `queues` =
`[NOW, WAITING-JOSEPH, BLOCKED-DECISION, BLOCKED-INTERNAL, BLOCKED-EXTERNAL]`, `authority_kinds`,
`terminal_criterion_kinds`. `queue_weights` prices only `NOW`/`WAITING-JOSEPH`/`BLOCKED-EXTERNAL`;
the two new `BLOCKED-*` tokens are **unweighted and unused** at this tip, exactly as delivered.

### 1.3 `control-plane/source-record-inventory.tsv` — generated, 6 columns

```
source_record  lifecycle  queue  classification_rule  source_row_sha256  state_prefix
```

`classification_rule` ∈ `{declared, migration-carried-forward}`. Written only by
`control_plane_lint.py --write`, never by hand.

### 1.4 Consumers bound by the freeze

| consumer | binds to | obligation |
|---|---|---|
| `control_plane_lint.py` | §1.1–§1.3 | owner; the only writer of §1.3 and of the three `CURRENT_WORK*` views and `PLAYBOOK.md` |
| `generate_live_state.py` | §1.1 (`item`, `source_record`, `lifecycle`, `queue`, `promotion`), §1.3 | read-only; routes = `promoted` ∧ `active` rows; queue read from `queue`; vocabulary = §1.2's five tokens |
| `docs/OPEN_ITEMS.md` | `source_record` ids and hashed rows | unchanged; no row is edited by this integration |
| `MANIFEST.tsv` | every file above | regenerated by `generate_manifest.py --committed-only` in the same commit as any change |

## 2. Conflict / dependency matrix — built from the return envelopes only

Sessions: **S3** routing design; **S4** routing register implementation; **S5** LIVE-STATE
structured-routing renderer; **S6** campaign contract; **S7** cluster read-only audit and guarded-run
design; **S8.1/8.2/8.3** PET branch salvage audits; **S9** salvage preservation and removal proposal.

### 2.1 Files touched by more than one contribution

| file | S3 | S4 | S5 | S6 | S9 | resolution |
|---|---|---|---|---|---|---|
| `MANIFEST.tsv` | regen | regen | regen | stale | stale | **generated** — never merged; regenerated by its tool at every commit |
| `MANIFEST-overrides.tsv` | – | – | +1 row | – | +1 row | both rows appended; textual, non-semantic |
| `control-plane/work-items.tsv` | schema | **writes** (schema + rows) | **reads** (old 8-column shape, `queue_override`) | – | – | **SEMANTIC**: S5 adapted to §1.1 in its own commit (§3 step 8) |
| `control-plane/source-record-inventory.tsv` | schema | regenerates | reads | – | – | S5 already reads the 6-column shape S4 emits |
| `control-plane/policy.json` | schema | rewrites | – | – | – | S4's is the frozen block |
| `LIVE-STATE.md` | – | – | regenerates | must not regen | must not regen | generated by S5's tool **after** S4 and S5 land (§3 step 9); see §2.3(c) |
| `state/live-state.json` | – | – | rewrites to schema v2 | – | – | S5's authored-input redesign; this is the OI-73 structural subject |
| `CATALOG.md` | – | – | – | – | +38 lines | textual; indexed pointer for this record added alongside |

### 2.2 Dependencies

| contribution | depends on | because |
|---|---|---|
| S4 schema commit `67404125` | S3 design `56b13be1` | S4's base is S3's tip; the design is the register's specification |
| S4 behavior commit `864496a2` | S4 schema commit | the behavior commit deletes the classifier the schema commit left running |
| S5 adaptation (new, §3 step 8) | S4 behavior commit | the generator must read `queue` and `promotion`, not `queue_override` |
| S5 regeneration (§3 step 9) | S5 schema, generator, tests, adaptation | the owning tool must be the integrated one |
| S6 | none (base `dae18f22`) | disjoint files; `campaignctl.py`, its tests, guide, one fixture |
| S9 | none (base `dae18f22`) | documentary; the two tags already exist on `origin` |
| S7, S8.1–8.3 | none | audits with **NO COMMIT** — nothing to integrate; findings are ledgered |

### 2.3 Semantic conflicts surfaced by the envelopes, and how each is enforced

- **(a) S5 reads a column S4 removed** (S4 envelope conflict 1; S5 fails soft to `UNAVAILABLE`).
  Enforced by rebasing S5 onto S4's tip and landing a separate behavioral commit that adopts §1.1.
  No textual merge touches this.
- **(b) `MANIFEST.tsv` regenerated by two lanes** (S4 conflict 2). Enforced by regeneration only.
- **(c) LIVE-STATE regeneration is withheld by five envelopes and by the decision record §5
  "pending `OI-73`'s owner"**, while S5's whole deliverable is the redesign of that authored input
  into a closed measurement schema whose routes are registry-derived. This integration regenerates
  `LIVE-STATE.md` with the integrated tool because (i) the user's integration instruction requires
  generated files to be recreated by their owning tools, (ii) after S5's schema commit the old
  rendered file is the output of a generator that no longer exists, and (iii) the result lives on a
  review branch, not `main`. **`OI-73` is not closed, edited, or discharged here**; whether S4+S5
  satisfy §5's condition is the reviewer's and the row owner's call. Flagged again in §5.
- **(d) The redesigned `LIVE-STATE.md` no longer carries "Exact blockers" or "Next authorized
  action".** `AGENTS.md` ("Next-action discipline"; evidence route "What is happening now?") still
  routes readers to `LIVE-STATE.md` for *the exact authorized action*. `AGENTS.md` is **not** edited
  by this integration; the routing gap is a reviewer item. Under S5's design those fields were the
  authored prose `OI-181` showed cannot be revalidated by regeneration.
- **(e) The R5 meter (decision §4 item 6) was delivered by no Wave 1 session.** S6's contract carries
  per-item `maximum_cost` ceilings, which is a per-run declaration, not the cumulative
  task-hours-from-t0 meter §3 of the decision specifies. Recorded as a **gap**; not built here.
- **(f) S7's "integrator selects the authoritative root/interface names"**: no Wave 1 session
  proposed a competing `MNV_*` root interface, so there is nothing to select; S7 claimed no names.
  No guard code was delivered. Recorded; nothing integrated.
- **(g) S8.1's salvage manifest lives only in a session scratchpad**, outside the repository. S9
  states it recovered two of the three manifests from transcripts and consolidated them into its
  proposal, which is the durable record.
- **(h) S9 versus S8.2/8.3 on `45d55f13` and `ed8244d3`**: S9's proposal §9 records the
  adjudication and what was deliberately left open. Not re-adjudicated here.

## 3. Integration order — as executed

1. This record (freeze + matrix), LIVE, indexed. *(structural)*
2. S3 design doc `56b13be1`, cherry-picked; `MANIFEST.tsv` regenerated. *(structural)*
3. S4 schema commit `67404125`, cherry-picked; MANIFEST regenerated; the five views byte-identical. *(structural)*
4. S4 behavior commit `864496a2`, cherry-picked; views and inventory regenerated by
   `control_plane_lint.py --write`; MANIFEST regenerated. *(behavioral)*
5. S6 campaign contract, applied from its uncommitted worktree as one commit; MANIFEST regenerated. *(behavioral)*
6. S5 schema/config `d980c0eb`, cherry-picked. *(structural)*
7. S5 generator `774df323` and tests `857f212f`, cherry-picked. *(behavioral)*
8. S5 adaptation to §1: the generator reads the frozen register. *(behavioral; new)*
9. `LIVE-STATE.md` regenerated by the integrated generator from a clean tree; MANIFEST regenerated. *(generated)*
10. S9 preservation record `93a75cf6`, cherry-picked; MANIFEST regenerated. *(structural)*
11. §5 of this record filled; proposed tip named. *(structural)*

No PET strategy branch is merged. No ref is deleted. The scheduler and every cluster checkout are
untouched. No grade, launch, adoption, or publication claim.

## 4. Decision-record enforcement — what the integrated code may and may not say

| ruling | enforcement in this integration |
|---|---|
| `R1` | no file names G as anything but causes 1–6's subject; no cause-7 grade on G; G's digest untouched |
| `R2` | Y is named in no integrated code, test, fixture, or view; nothing combines a Y grade with G's counts |
| `R3` | no materiality threshold introduced anywhere |
| `R4` | no cause-3 scan staged, contracted, or launched; `campaignctl` gained a contract schema, not a run |
| `R5` | nothing spent; no submission; the missing meter is a gap (§2.3(e)), not an authorization |
| `R6` | PET stays diagnostic; S9's proposal §6 blocks the one route by which a quarantined PET receipt could be ported; the five Gate-6 keys are rendered verbatim from their receipt by the new `LIVE-STATE.md` |

## 5. Integration ledger

*Filled in the closing commit of the integration branch.*
