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

Branch `wave1-integration-20260903`, rooted at `dae18f22`. Every commit below passed the 12-check
pre-commit dispatcher (`Checks: 12 passed` trailer) and `generate_manifest.py --check
--committed-only` at its own tree. Cherry-picked commits keep their original author and carry
`(cherry picked from commit …)` plus an `INTEGRATION NOTE`. The two commits after this record —
the record's own commit and the final `[generated]` regeneration — are identified by position
because their hashes do not exist when this text is written; the return envelope names the tip.

### 5.1 Accepted

| wave 1 output | commit here | source | verification at this tree | reason |
|---|---|---|---|---|
| S3 design `56b13be1` | `52cf66fb` | cherry-pick | hook 12/12; MANIFEST regenerated (semantic cols 1–11 identical to `aefa34c3` except this record's row) | design only; the specification of §1 |
| S4 schema `67404125` | `25280c39` | cherry-pick; MANIFEST conflict only, regenerated | `control_plane_lint.py`, `--self-test`, `--adoption-check` PASS; **five views byte-identical to `dae18f22`**; `--write` a no-op; the three source blobs identical to S4's | structural, behaviour-preserving, exactly as the S3 stage rule requires |
| S4 behavior `864496a2` | `4e296f06` | cherry-pick; MANIFEST conflict only; views regenerated by `--write` | lint PASS (13 selected / 92 backlog / 137 records / 0 state cells drifted); **eight files byte-identical to S4's blobs** including all regenerated views; `source_classification` absent from `policy.json` | the classifier is deleted; routing is declared |
| S6 campaign contract (uncommitted) | `2209b0fc` | `git apply` of the worktree diff + fixture | `test_campaignctl.py` **16 passed** (py3.12); `py_compile`; `--help` | one behaviour unit, disjoint files; **not** the R5 meter |
| S5 schema `d980c0eb` | `8f8149ad` | cherry-pick; overrides union | `live-state.json` and `live-state.schema.json` identical to S5's blobs | closed measurement schema v2; the authored-prose fields are refused by `validate_config` |
| S5 generator `774df323` | `5c0c40b6` | cherry-pick, clean | tests at this step 52 passed; route registry UNAVAILABLE by design until the next-but-one commit | registry-derived routes |
| S5 tests `857f212f` | `4e8369ac` | cherry-pick, clean | 52 passed | |
| **integrator** adaptation to §1 | `2a49eb49` | new | **59 passed** (52 + 7 new); registry **HEALTHY, 13 routes / 137 records**, the same 13 items S5 rendered | resolves §2.3(a) as a separate behavioural commit, never a textual merge |
| S9 preservation `93a75cf6` | `7b527003` | cherry-pick; CATALOG union, overrides clean, MANIFEST regenerated | proposal blob identical to S9's; both `evidence/preserved-pet-gate6-*` tags present on `origin` (4 refs); all 7 `pet-gate6` branch refs intact | documentary; deletes nothing |
| this record | the commit after `7b527003` | new | hook 12/12 | ledger |
| `LIVE-STATE.md` | the final commit | **regenerated** by the integrated generator from a clean tree | `--check-freshness` green for the Git relationship; `live-state-last-known.json` unchanged (no measured probe on this host) | generated by its owning tool; see §2.3(c) |

### 5.2 Rejected as commits (content reproduced by tools instead)

| wave 1 output | disposition | reason |
|---|---|---|
| S4 `aefa34c3` (MANIFEST regen for the design commit) | not cherry-picked | generated file; regenerated at `52cf66fb` and corroborated column-wise |
| S5 `4d6f4720` (regenerated `LIVE-STATE.md` + MANIFEST) | not cherry-picked | generated files; regenerated by the integrated tool in the final commit. Masked diff against S5's rendering: same 13 routes, register order, timestamps and elapsed-hours only |
| every S4/S5/S9 `MANIFEST.tsv` hunk | overwritten by `generate_manifest.py --committed-only` in the same commit | never hand-merged |

### 5.3 Nothing to integrate (audits with NO COMMIT) — findings ledgered, not re-verified here

| session | disposition |
|---|---|
| S7 cluster audit + guarded-run design | no code delivered; the four-root run contract is a design; no competing interface names to select (§2.3(f)); the 3,473-entry dirty-checkout classification (digest `6275277a…`) is S7's fact, not re-measured here; **no cluster checkout touched** |
| S8.1 strategy-branch audit | salvage manifest not in the repository (§2.3(g)); its 21/21 digest matches and the 57644535 outcome are S8.1's facts, consolidated by S9 |
| S8.2 strategy-branch audit | findings (34 commits / 82 files; retry-3 schema mismatch; nonfinite KeyError; hardcoded scratch) carried by S9's proposal §8–§9 |
| S8.3 GAP-1 audit | findings (17 commits / 62 paths; `truth_denominator_coverage` has no producer) carried by S9's proposal §6; the R6 hard block on porting that receipt is enforced by **not porting it** |

### 5.4 Gaps and reviewer items — none of these is discharged here

1. **R5 meter — NOT DELIVERED** (§2.3(e)). `DECISION-20260902` §4 item 6 remains open with the
   orchestration lane. `RUNS.tsv` is not touched by this integration.
2. **`OI-73` / decision §5** (§2.3(c)). The regeneration is performed on this branch by the owning
   tool; whether S4+S5 satisfy "pending `OI-73`'s owner" is for the reviewer and the row owner.
   `OI-73`'s row still renders `BLOCKED-EXTERNAL`: that is S4's `migration-carried-forward` value,
   which S4 deliberately did not reclassify (136 of 137 records carry that token).
3. **`AGENTS.md` routes to a section `LIVE-STATE.md` no longer has** (§2.3(d)). Not edited here.
4. **`BLOCKED-DECISION` / `BLOCKED-INTERNAL`** are in the vocabulary, accepted by both consumers,
   and priced by neither `queue_weights` nor any row. Pricing is the `policy.json` owner's act.
5. **S3's `render_current()` obligation** (its conflict 2: the "derived from explicit OI state
   language" sentence) — verify S4's behavior commit updated it; this integration did not audit the
   view's prose beyond byte-identity with S4's blob.
6. **`MANIFEST.tsv:248` names `usagectl.py` as a consumer of `control-plane/policy.json`** (S3's
   incidental finding, substring-derived). Reported, not repaired.
7. **S6's worktree** `/private/tmp/minerva-campaign-contract-nlmg6I` still holds the uncommitted
   change set; it is not this integration's to remove. Two Wave 1 detached audit worktrees and the
   two live PET lane worktrees are likewise untouched.
8. **Python**: this host runs 3.12; `/usr/bin/python3.11` (the deployment interpreter) is absent.
   S6 asked for a rerun under 3.11 before deployment.

### 5.5 Explicit non-actions

No PET strategy branch merged (the three tips `a05baab1`, `310d7e63`, `0969e787` are on no commit
here). No ref deleted. No scheduler query or write. No cluster checkout read or written. No grade
applied. No compute staged, contracted, or launched. No artifact adopted. No `OI-*` row edited.
`AGENTS.md`, `CLAUDE.md`, `OPEN_ITEMS.md`, `VALIDATION_LEDGER.md`, `RUNS.tsv` untouched. No
publication claim changed. `main` not written; the shared primary checkout's seven untracked paths
untouched. Nothing pushed except this branch.

### 5.6 Proposed tip and how to check it

The proposed tip is the last commit of `wave1-integration-20260903` as pushed to `origin`, named in
the return envelope. An independent acceptance reviewer should, from a clean worktree at that tip:

```
bash .githooks/pre-commit                                   # 12 checks
python3 docs/orchestration/generate_manifest.py --check --committed-only
python3 docs/orchestration/generate_live_state.py --check-freshness
python3 docs/orchestration/control_plane_lint.py --self-test
python3 -m pytest -q docs/orchestration/test_campaignctl.py docs/orchestration/test_generate_live_state*.py
for f in docs/CURRENT_WORK.md docs/CURRENT_WORK_BACKLOG.md docs/CURRENT_WORK_OVERFLOW.md \
         docs/orchestration/PLAYBOOK.md docs/orchestration/control-plane/*; do
  git diff --quiet 864496a2 HEAD -- "$f" && echo "SAME  $f" || echo "DIFF  $f"; done   # expect SAME
```

This record grades nothing, including itself.

## 6. Reviewer round 1 (2026-09-03) — verdict BLOCK on `82f23914`, and what this revision changed

The independent acceptance reviewer graded `82f23914` **BLOCK** on five properties and PASS on
six. `82f23914` is **withdrawn**: the branch was reset to `8df9eb88` (the ledger commit) and the
commits below were added; the `[generated]` regeneration commit is gone. Every resolution below was
re-verified at the new tip; nothing below moves a gate, count, adoption, grade, or claim.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **R5 — no operational meter** | `r5_meter.py` implements decision §3 verbatim: t0 = the commit instant of `9ce59a59` (`2026-09-02T13:44:27Z`); task-hours over distinct task identities, step and array-bracket rows excluded; GPU/CPU by partition; failed tasks counted in full; inclusive `>=` ceilings; OR trigger; UTC; a missing, stale (>24 h) or malformed receipt is a **stop** (fail-closed). `check` exits 0/3/4/5. **No receipt is committed** — this host has no `sacct`, and a fabricated receipt would be a false measurement; the first measurement is a Perlmutter act (`R5-METER.md`) | `a0bde16a` | 16 tests (+9 subtests) on 3.12 and 3.11; `--self-test` PASS; the rows-vs-identities fixture reproduces the amendment's 447-rows/374-tasks inflation |
| **Campaign contracts declarative, not enforced** | (1) a bound `terminal_validator` always runs after the producer and **alone** resolves the terminal branch — the reviewer's exit-0-no-validator mutation now lands on the failure branch; (2) producer, validator, decision authority pairwise distinct; (3) compute producers must route through `nd-unfolding/mnv_guarded_run.py` and every binding must be byte-identical to its HEAD blob at staging and again before execution; (4) timeouts bounded by `maximum_cost.wall_hours`, and a **fail-closed R5 gate** on the meter receipt before any compute executes (missing/malformed/stale/fired/past stop date/headroom-exhausting each refuse with exit 6, item left retryable); (5) exactly-once, preserve-first, no automatic retraining kept | `06adaa53`, `f03b8468` | 31 tests on 3.12 and 3.11, including `MeterReceiptInteroperability`, which feeds the meter's real output to the gate (the two modules were written in parallel and had drifted on the `unit` value — caught by that test) |
| **Sensor-only LIVE-STATE: registry omissions read HEALTHY** | completeness in both directions: every `OPEN_ITEMS` record must be inventoried and every inventoried record must have a register row; either omission is CONTRADICTORY and withholds all routes. Both reviewer mutations are regression tests | `35c93775` | 61 tests; real registry 137 = 137 = 137, HEALTHY, 13 routes |
| **Sensor-only LIVE-STATE: regenerated despite the owner hold** | the regeneration is **withdrawn**. `LIVE-STATE.md` is the committed base file and reads STALE under the integrated generator, which is the lawful state until `OI-73`'s owner disposes of decision §5's hold. §2.3(c)'s reasoning for regenerating is superseded by the reviewer's reading, which is the stricter one | branch reset | `--check-freshness` → STALE at the tip, by design |
| **Generated-file reproduction** | the five views, the inventory and MANIFEST reproduce byte-clean by their writers (unchanged finding); LIVE-STATE is no longer claimed reproduced | — | §5.6 commands |
| **Immutable deployment/import guards** | the part inside this integration's authority: `campaignctl` now refuses unguarded, dirty or untracked executables (above), and the guard suites pass on macOS with the default `TMPDIR` after the tests resolve their temp root (10 + 2 failures were `/var` vs `/private/var`, not guard defects). **The 45 fail-open entrypoints are NOT repaired** — see §6.1 | `f808edd2` | `test_mnv_guarded_run.py` 99 passed; `test_k0_launcher_two_roots.py` + `test_k0_5ab_separated_roots.py` 68 passed |

Known conflicts the reviewer listed, and their state now:

| item | state |
|---|---|
| `AGENTS.md` routes to a removed live-state section | **resolved**, `ec7d24f8`: the authorized action is routed to `docs/CURRENT_WORK.md` and the governing `OI-*` row; `LIVE-STATE.md` is named as measurements and route health. Holds in both the STALE and the redesigned view |
| two queue tokens unpriced | **left to the `policy.json` owner, deliberately.** An attempt to price them by equivalence (`BLOCKED-DECISION`=40, `BLOCKED-INTERNAL`=30) was reverted because S4's self-test *proves* that an unpriced token is refused with a named error — the fail-closed behaviour is designed, and pricing is a routing decision the register's owner reserved |
| Python 3.11 unavailable | the deployment interpreter is still absent from `/usr/bin`; a `uv`-managed CPython 3.11.15 ran the full orchestration suite: **108 passed** |

### 6.1 Left out, with the reason — the reviewer and Joseph decide, not this lane

**The 45 fail-open entrypoints (`OI-136`) are not repaired here.** They are hash-pinned science
files inside frozen provenance; `test_oi136_failopen_inventory_ratchet.py` pins their count as an
identity and states that a repaired site is *also* red until the constants are updated in the same
reviewed commit, and `mnv_guarded_run.py`'s header records that the wrapper exists precisely so
those files need not be edited. `FREEZE-20260830-k0-deployment-7ac0edec.md` remains live. Editing
them is a change to deployed, pinned launchers and needs its own authorization and redeploy; the
integration's authority does not extend to it. What this branch does instead is make the guard the
only door: a compute item cannot be staged without routing through `mnv_guarded_run.py`.

### 6.2 Proposed tip, revised

The proposed tip is the last commit of `wave1-integration-20260903` as force-pushed to `origin`
after this record (the branch was reset, so the previous remote tip `82f23914` is intentionally
gone from it). The §5.6 commands apply unchanged, plus:

```
python3 -m pytest -q docs/orchestration/test_r5_meter.py
python3 docs/orchestration/r5_meter.py --self-test
(cd nd-unfolding && python3 -m pytest -q tests/test_mnv_guarded_run.py)      # default TMPDIR
python3 docs/orchestration/generate_live_state.py --check-freshness           # expect STALE: the hold stands
```

## 7. Reviewer round 2 (2026-09-03) — verdict BLOCK on `320d7c0a`, and what this revision changed

`320d7c0a` is **withdrawn**. Four commits were added on top of it; every reviewer mutation below
is now a named regression test at the tip.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **R5 meter misclassifies Perlmutter GPU jobs** (Partition-only; `regular` + `gres/gpu=1` for 499 h metered as CPU, and a 2-GPU-hour proposal passed) | GPU work is identified by `AllocTRES` `gres/gpu=N` (generic or typed) with the partition prefix only as a fallback | `824b521b` | fixture `perlmutter_regular_gpu.sacct`: 499.0 GPU / 0.0 CPU; `check --gpu-task-hours 2` → exit 5 (replayed by the integrator) |
| **R5 meter drops a task that started 1 s before t0** | straddling tasks are clipped to their post-t0 runtime; tasks ending at or before t0 are omitted | `824b521b` | 3599 s metered in the reviewer's mutation; start = t0 → full; 18 meter tests |
| **campaignctl receipt validator fail-open on t0 and future dates** | `t0_utc` must equal the ruled instant `2026-09-02T13:44:27Z` and `decision_record` the exact path; a receipt more than 60 s ahead of the queue clock is refused; every receipt fixture's midnight t0 corrected | `e58aa8ff` | the reviewer's midnight-t0 and one-day-ahead mutations → exit 6; a cross-module test pins the same instant and record in both modules |
| **terminal validators bypass the guard** (`require_guard=False`) | compute validators must route through `nd-unfolding/mnv_guarded_run.py` under the producer's rules; the guard's own refusal resolves to `otherwise`, never the pass branch; the suite copies the real guard into each fixture repo | `e58aa8ff` | the reviewer's outside-checkout-import validator is refused at staging; guarded, its exit 3 lands on `unexpected-terminal-result` |
| **wall limit applied twice** (1 s each, 2.09 s observed) | one deadline per execution; the validator gets only the remainder; nothing left → validator not started, `otherwise`, reason recorded | `e58aa8ff` | 1 s wall, 2 s producer: 1.10 s measured; 0.4 s producer left the validator ~0.5 s |
| **LIVE-STATE: misspelt lifecycle/promotion read HEALTHY; two copies of the schema** | the registry config names `policy.json`; lifecycles and queues are read from its `routing` block, not restated; every token is validated before any row is skipped, so `promtoed` and `activ` are CONTRADICTORY; non-active rows must carry `-`; a missing policy is UNAVAILABLE | `73dbd1cd` | both reviewer mutations verbatim; real registry HEALTHY, 13 / 137 unchanged; 65 tests |

Suite at the tip: **124 orchestration tests** on CPython 3.12 and on uv-managed 3.11.15 (+9 subtests).

### 7.1 The one BLOCK this lane cannot clear — an authorization request to Joseph

"Immutable deployment/import guards" is graded BLOCK on two grounds. The validator bypass is
closed above. **The 45 fail-open entrypoints (`OI-136`) remain unrepaired, and the reviewer has
now blocked on them twice.** They are not repaired here because:

1. they are hash-pinned science files inside frozen provenance, and `mnv_guarded_run.py`'s header
   records that the wrapper exists precisely so they need not be edited;
2. `test_oi136_failopen_inventory_ratchet.py` pins their count as an identity and states that a
   repaired site is *also* red until the constant is updated in a reviewed commit — the repair is
   designed to be a deliberate, authorized act, not a sweep;
3. `FREEZE-20260830-k0-deployment-7ac0edec.md` is live, so editing deployed launchers changes the
   pinned bytes the freeze protects and forces a redeploy.

**Requested ruling:** authorize a repair of the 45 sites (replace each absolute `sys.path.insert(0,
<cluster root>)` with a `__file__`-relative root, updating the two ratchet constants in the same
commit and naming every site), **or** rule that the guard is the accepted mechanism and the
inventory ratchet the accepted control, so the reviewer can grade the property against that ruling.
Until one of those lands, this branch's position is that the guard is the only door: no compute
item can be staged unless both its producer and its validator route through it.

### 7.2 Proposed tip, revised again

The last commit of `wave1-integration-20260903` as force-pushed after this record. §5.6 and §6.2
commands apply; add:

```
python3 docs/orchestration/r5_meter.py measure --from-file docs/orchestration/test_fixtures_r5_meter/perlmutter_regular_gpu.sacct --now 2026-09-10T00:00:00Z
```

## 8. Joseph's authorization (2026-09-03) and the OI-136 repair — the last BLOCK, cleared in scope

Joseph answered §7.1: *"I authorize it"* — recorded verbatim with its scope in
`AUTHORIZATION-20260903-oi136-failopen-repair.md` (`ce34a370`). `71839696` is **withdrawn**.

| what | commit | proof |
|---|---|---|
| authorization record, scope 36 of 45, nine exclusions each measured | `ce34a370` | the nine reasons: 3 probe records; the published 2D arm (Joseph's 2026-08-23 ruling); 5 receipt-bound files on which `verify_hash_bindings.py` reports BINDINGS BROKEN for any byte change |
| the repair: the import root derived from `__file__` at 36 entrypoints; sub-paths and data-path defaults unchanged; both ratchet constants moved in the same commit naming every site | `8ff5d843` | probe FAIL-OPEN SET = exactly the 9 exclusions (exit 0); `FAILOPEN_COUNT` 45 → 9; `KNOWN_UNREPAIRED` 46 → 10; 36/36 derived roots evaluate byte-identical to the literal on the canonical checkout; re-planting the literal is caught 36/36 by both the probe and the AST scanner; `py_compile` 36/36; `ALL BINDINGS INTACT`; 220 tests in the seven guard/ratchet/launcher suites at the worker's tree, 124 in the four fast suites re-run here |

Two residuals the worker surfaced, neither in the authorized scope and neither hidden:

- `nd-unfolding/pet/gate2_target_runtime.py` reaches a position-0 insert through a `pathlib`
  binding the probe's regex does not follow, so it is in the AST scanner's list and not the
  probe's. It stays listed as the PET lane's, unrepaired and unreclassified.
- Two of the nine residual files are the probe's own positive controls, so the fail-open set cannot
  reach 0 without new controls first — a probe-owner act.

**Freeze consequence, stated so it is not read as an oversight.** `FREEZE-20260830-k0-deployment-7ac0edec.md`
is not expired. The deployed cluster copies of the 36 files stay at their frozen bytes until an
authorized redeploy under that freeze's process, after which parity will honestly report the 36 as
changed relative to `7ac0edec`. Nothing was deployed by this integration.

### 8.1 Proposed tip, final for this round

The last commit of `wave1-integration-20260903` as force-pushed after this record. All prior
command lists apply; add:

```
python3 docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py     # FAIL-OPEN SET: the 9 named in AUTHORIZATION-20260903 §2
python3 docs/orchestration/verify_hash_bindings.py                            # ALL BINDINGS INTACT
(cd nd-unfolding && python3 -m pytest -q tests/test_oi136_failopen_inventory_ratchet.py tests/test_oi136_rooted_insert_ratchet.py)
```

## 9. Reviewer round 3 (2026-09-03) — verdict BLOCK on `d0fc1d07`, and what this revision changed

`d0fc1d07` is **withdrawn**. Every reviewer mutation below is a named regression test at the tip.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **R5 admission not atomic** (490 recorded; two six-hour items both admitted, projection 502) | headroom counts the receipt's spend, this item's `maximum_cost`, and the `maximum_cost` of every other compute item not in a terminal outcome (staged/approved/claimed reserve; refused/failed/succeeded/stale/revoked release), inclusive in either column with the reserving items named; the check and the claim run under one `O_EXCL` admission lock (owner host:pid, stale after timeout + wall, removal logged) | `ef7882fc` | the reviewer's mutation: exactly one item admitted, the other refused naming the reserver; a terminal outcome releases; a held lock admits nothing; an undatable lock is treated as held |
| **an uncommitted receipt can authorize compute** (a `/tmp` copy produced no refusal) | the receipt must be a repository-relative, tracked path byte-identical to its HEAD blob; `CAMPAIGN_R5_RECEIPT` may override only the relative path; absolute, outside-repo, untracked, or edited-after-commit receipts refuse with exit 6 | `ef7882fc` | the `/tmp` copy (first asserted schema-valid, so the refusal is provenance), untracked, edited-after-commit, and committed-accepted tests |
| **guard bypass via `--allow`** (staging accepted `--allow <foreign checkout>`; the guard's positive control then loaded the wrong tree) | guarded argv on producer AND validator must carry exactly one `--expect-root` equal to the queue root, no `--allow`, no `-S`/`-I`/`-E`, no `PYTHON…=` element; enforced at staging and again in `validate_unchanged` | `ef7882fc` | the reviewer's `--allow` mutation refused on both arms and after staging; foreign `--expect-root` refused; clean argv accepted |
| **guard cannot cross the adoption subprocess boundary** (`adopt_unified_5d.py` is run as a child; the child loaded the wrong tree and exited 0) | `mnv_guarded_run.py` now arms every environment-inheriting Python child through the tracked `nd-unfolding/mnv_guard_shim/sitecustomize.py`: the child installs the guard before its own script runs, refuses foreign resolved origins with exit 3 and `[oi136 child]`, and writes its own inventory record with `propagated_from` and `depth`; existing `sitecustomize` is preserved. **Declared uncovered, each with a test:** `-S`, `-I`, `-E` children; a cleared environment; non-Python children | `3eadd3f8` | `TheSubprocessBoundaryIsCovered`: child and grandchild refused; the exact parent-runs-child shape of `mii_adopt_unified_5d_stamped.py` refused; 200 tests in the worker's matrix; probe still exactly 9; bindings intact |
| **retired inventory row with queue NOW read HEALTHY** | every inventory row is validated against the policy vocabulary as it is read, before any record is skipped; non-active records must carry `-`; `classification_rule` must be declared or migration-carried-forward; the fixture's inconsistent combination corrected | `ed1312f6` | the reviewer's mutation verbatim; 68 live-state tests; real registry HEALTHY 13 / 137 |
| **`AGENTS.md` still says 59 fail-open** | the bullet routes the reader to the probe for the count and names the authorization record and the nine residual classes | `bbc70e63` | |
| (consequence) campaign fixture | the campaign tests copy the real guard into each fixture repository; they now copy the shim beside it | the commit after `54e6b8fb` | 13 failed at `54e6b8fb` (guard exit 2 read as `failed`), 55 passed here |
| (consequence) census power tests | the guard now refuses to run without its shim (exit 2, COULD NOT LOOK); the criterion-5 synthetic checkout copies the shim as the launcher fixture does | `54e6b8fb` | 25 passed at `ef7882fc`, 2 failed at `3eadd3f8`, 25 passed here |

Two fail-closed consequences the contract worker flagged, kept as specified rather than softened:
a committed receipt moves `HEAD`, and the existing drift rule stales items staged before it, so
metering precedes staging; and an over-committed queue refuses every affected item until an
operator revokes one or a fresh receipt lands. Both need an operator, not a tick.

### 9.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record. Prior command
lists apply; add:

```
(cd nd-unfolding && python3 -m pytest -q tests/test_mnv_guarded_run.py tests/test_k0_preflight_exclusion_census.py)
python3 -m pytest -q docs/orchestration/test_campaignctl.py      # includes the two-six-hour-items, /tmp receipt, and --allow mutations
```

## 10. Reviewer round 4 (2026-09-04) — verdict BLOCK on `4270bb0c`, and what this revision changed

`4270bb0c` is **withdrawn**. Every reviewer mutation below is a named regression test at the tip.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **reservations released before their spend reaches a receipt** (alpha terminal, receipt still 490, beta admitted → 502) | an item that RAN keeps reserving its full `maximum_cost` until a committed receipt whose `measured_at_utc` is later than the item's terminal outcome exists; items that never ran (refused, stale, revoked, unclaimed) release at once; outcomes carry their timestamp | `9ee0d600` | reviewer mutation: beta refused naming "alpha (terminal, not yet remeasured)"; a receipt measured after alpha's outcome admits beta; the old blessing test rewritten |
| **lock and reservations scoped to a user-selectable `--state-dir`** (two queues, one receipt, both admitted) | compute admission (R5 check, reservation scan, lock, claim) requires the queue's state dir to be the canonical `<repo>/docs/orchestration/state/campaign-queue`; any other state dir refuses compute with exit 6 and may run only non-compute items | `9ee0d600` | reviewer mutation: canonical queue admits alpha, the other refuses beta; two canonical queues share the lock; a `..`-spelled canonical path resolves to the same lock |
| **the shim is unbound and mutable** (replacing only the shim after staging let a child load the wrong tree, rc 0) | `nd-unfolding/mnv_guard_shim/sitecustomize.py` is bound wherever the guard is bound: tracked, HEAD-identical at staging, re-verified in `validate_unchanged`; the fixture commits it | `9ee0d600` | reviewer mutation: shim swap after staging → `(4, "stale")`, nothing ran, no claim; untracked shim refused at staging |
| **`-S`/`-I`/`-E`, cleared env, non-Python children declared uncovered** | the guard wraps 21 launch primitives (`subprocess.Popen`, `os.posix_spawn*`, `os.exec*`, `os.spawn*`, `os.system`) in every guarded interpreter: a Python child carrying `-S`/`-I`/`-E` — standalone, clustered, or hidden behind an option value, scanned with CPython's option grammar — is REFUSED before launch (exit 3, `[oi136 launch]`, a `REFUSED launch` inventory record); a child launched with a cleared or shim-less environment, or through `env -i` / `env -u` / `env PYTHONPATH=…`, is RE-ARMED; a parent that deletes the contract from its own environment cannot launch a Python child; non-Python children inherit the re-armed environment, so the Python they run is guarded; the shim verifies the guard module lies inside the expected root and both records carry the digest of the shim that ran | `5c522fa0` | 122 guard tests incl. each former gap; 240 in the seven-file matrix at the worker's tree; four mutation runs each killed the tests that exist for them; probe still exactly 9; bindings intact |

**The one declared gap that remains, stated so it is graded as what it is:** a non-Python child
that itself defeats the contract at its own launch site — a shell script that runs `python -I`, or
that clears its environment before running Python. Both are one cause (the guard is not in the
shell) and are measured by two tests that assert the wrong tree loads with exit 0. Closing it means
guarding the shell, which is a different instrument; the campaign queue's argv rules already forbid
those shapes on the producer and validator arms it admits.

Consequences surfaced by the workers, not hidden: `tests/test_n2_child_boundary.py` needed its
fixture to carry the shim (red at `4270bb0c`, green here); and the OI-136 row in `OPEN_ITEMS.md`
still states that the guard does not cross a subprocess boundary — true when written, stale since
`3eadd3f8`. That row is its owner's; this integration edits no `OI-*` row and records the
staleness here instead.

### 10.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record. Add:

```
python3 -m pytest -q docs/orchestration/test_campaignctl.py   # remeasure, canonical-state-dir, shim-swap mutations
(cd nd-unfolding && python3 -m pytest -q tests/test_mnv_guarded_run.py tests/test_n2_child_boundary.py)
```

## 11. Reviewer round 5 (2026-09-04) — verdict BLOCK on `180527b0`, and what this revision changed

`180527b0` is **withdrawn**. **A claim in §10 is retracted:** it said the queue's argv rules already
forbid the launch shapes of the declared gap. The reviewer drove `env -- python -I` through a fully
admitted item whose outer argv satisfied every queue rule, and the item reported success. The queue
validates the arm it launches; it cannot see what the arm's script launches. That is the guard's
job, and the guard's `env` grammar was incomplete.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **reservations release without evidence the spend was counted** (a fresh receipt still at 490, listing none of alpha's tasks, admitted beta) | contract schema v1 gains a required `accounting` object (`task_ids_file`, `expects_scheduler_tasks`); between producer and validator the queue reads the task-ids file (scheduler identities in the meter's exact grammar, cross-module tested), records them in the outcome with the file's digest, and removes any earlier copy first; missing, malformed, empty-when-expected or populated-when-not resolves through `otherwise`. Release requires a committed receipt measured after the outcome **and** listing every one of the item's ids; an arm that expects no tasks releases on the timestamp; an item that ran with no recorded ids never releases automatically — only `revoke` or the new interactive `release --id --reason` | `823e9c48` | reviewer mutation: beta refused naming alpha "not yet in a receipt"; a receipt listing alpha's ids admits beta; each accounting failure and the operator path tested; each fix mutation-verified by reverting it alone |
| **the queue is canonical only per checkout** (two clones each admitted) | the canonical queue lives outside every checkout at `${MNV_CAMPAIGN_STATE_ROOT:-~/.mnv_campaign}/<key>/campaign-queue`, key derived in a comment from the ruling record's sha256; every clone and worktree resolves one directory, so the lock, reservation scan and claims are shared; items record their `repo_path` and a ticker runs only its own repo's items while all reserve | `823e9c48` | reviewer mutation: two `git clone`s, one receipt, two six-hour items at 490 — exactly one admitted; two tickers cannot both hold the lock |
| **the guard's `env` parser was fail-open** (`env -- python -I`, `env -S 'python -I …'`) | `env` parsed with the full coreutils/BSD grammar and **fail-closed on anything unmodelled**; `-S` strings split and rescanned; `sh -c`/`bash -c` strings tokenised and each simple command scanned; `nohup`/`nice`/`stdbuf`/`timeout`/`time`/`command`/`exec` prefixes followed; absolute interpreter paths count as Python; a launch that strips the contract (`env -i`, `env -u`, `env PYTHONPATH=…`) is re-armed; PATH interpreter wrappers `mnv_guard_shim/bin/{python3,python}` with `scan_argv.py` refuse `-S/-I/-E` and re-inject the contract for non-Python children that launch Python via PATH | `fcf60b25` | both reviewer forms refused (exit 3, `[oi136 launch]`, REFUSED-launch record); bash child running `python3 -I` via PATH refused by the wrapper; bash child running `python3 x.py` via PATH guarded and its foreign import refused; 169 guard tests, 401 in the ten-suite matrix at the worker's tree; two further fail-opens found by measurement and pinned (`env -iv`; `env -i bash -c '…'`) |
| (integrator) the wrappers and scanner were unbound | all four shim files bound wherever the guard is bound; fixture commits them | `6f4686d7` | swapping only `bin/python3` after approval → `(4, "stale")`, nothing run |

> **SUPERSEDED 2026-09-04 BY §12 — DO NOT QUOTE THE RESIDUAL BELOW AS CURRENT.** Reviewer round 6
> found this sentence both incomplete and operationally fail-open, and both halves of it are now
> closed. The paragraph is left as written because it is the round-5 record of what was true at
> `fcf60b25`; the residual that is current is in §12 and, mechanically, in `DECLARED_GAP` — read that
> constant rather than any prose, including this document's.

**The residual, stated exactly and measured:** a non-Python child that invokes the interpreter by
an **absolute path** with `-S`/`-I`/`-E`, or that clears `PATH` or the environment before doing so.
The argv is built inside a process this interpreter does not guard; an absolute path consults no
`PATH` and therefore no wrapper; a cleared environment removes both the wrapper directory and the
contract. Every inventory record now carries a `declared_gap` field naming it. Closing it requires
guarding the shell or the kernel, not Python. `srun`/`mpirun` are deliberately not modelled as
wrappers (a fail-closed parser would refuse correct submissions); `srun python3 -I x.py` is caught
by the PATH wrapper and `srun /abs/python3 -I x.py` is the residual. The wrappers carry no `.py`/
`.sh` suffix, so the A-2(f) source manifest does not list them; every record carries
`path_shim_sha256` instead, and the campaign queue binds them.

### 11.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record.

## 12. Reviewer round 6 (2026-09-04) — finding 4, and the launch model it replaced

The reviewer's finding, verbatim: *"The guard's stated residual is incomplete and remains
operationally fail-open. Shell script files are not scanned; the implementation relies entirely on
the inherited PATH wrapper (`mnv_guarded_run.py:1212`, `:1493`). Three shell-script mutations
bypassed it: `command -p python3 -I ...`, reordered `PATH=/usr/bin:/bin python3 -I ...`, BSD
`env -P /usr/bin:/bin python3 -I ...`. All returned 0, ran the sentinel, loaded the wrong tree,
produced no child record, and were not described by the declared 'absolute path or cleared
environment' gap. The already-declared absolute-path route is itself also a fully admitted
fail-open path."*

**Both halves were right, and the second is the one that changed the design.** §11's model was
*scan Python launches; every other child inherits the re-armed contract and the wrapper directory on
`PATH`.* That is a coverage claim resting on a **PATH lookup the child can simply decline to make** —
and a shell script file was admitted **unread**, so there was nothing else to fall back on. The
old `_shell_command_string` docstring said so out loud: *"A shell invoked on a SCRIPT FILE has no
string here and is not refused — what that script does at ITS launch sites is the PATH wrapper's
half of the contract."*

| reviewer finding | resolution | proof |
|---|---|---|
| three shell-script mutations ran, unread, with no child record | **the closed child model.** `_scan_resolved_command` classifies every resolved child and admits exactly six things: a Python interpreter under the startup-flag grammar **in any path spelling**; a modelled shell (`sh`/`bash`/`dash`, `zsh` only behind `-f`/`--no-rcs`) whose `-c` string **or SCRIPT FILE operand** is read and scanned; read-only `git` on a subcommand allowlist plus a hostile-environment check; `sbatch` whose batch script or `--wrap` string is scanned; a leaf tool from a committed list, admitted only when found in a named system prefix with no shebang; and a file whose shebang names one of those. Everything else refuses with the new `LAUNCH_REASON_UNPROVEN`. Inside a shell program, an assignment/`export`/`unset` of `PATH`, `PYTHONPATH`, `BASH_ENV`, `ENV`, `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES` or any `MNV_GUARD_*` refuses **wherever it appears**, not only in front of an interpreter; `eval`, `alias`, `hash -p`, `enable -f`, `command -p`, `exec -a`/`-l`, `module load`, `conda`/`uv run` refuse; `source`/`.` reads and scans its single literal operand; `trap` handlers, function bodies and the insides of command substitutions are scanned; here-document bodies are data. `srun` joins the wrapper table, `mpirun` is refused, `--export` must be `ALL`; `ksh`/`mksh`/`fish`/`csh`/`tcsh` refuse as unmodelled shells | all three mutations refused (exit 3, `[oi136 launch]`, REFUSED-launch record, sentinel absent) in **both** spellings — `bash script.sh` and `./script.sh` behind a shebang with a relative operand under `cwd=`. `TheClosedChildModelRefusesWhatItCannotProve`, 17 named tests building real files and running the real guard in a subprocess |
| the declared absolute-path route was a fully admitted fail-open run | **retired, and the reasoning behind it was wrong rather than merely narrow.** The argument was "an absolute path consults no `PATH`, so no wrapper stands in front of it" — true and irrelevant: what guards a Python child is the shim on `PYTHONPATH`, and what defeats the shim is `-I`. So the question was never whether a PATH lookup happens, it was whether the launch was **read** | the arm that used to assert exit 0, a written sentinel and `ISOLATED-LOADED WRONG TREE` now asserts exit 3 with reason `python-startup-flags-bypass-the-shim`, in a script file **and** as a direct argv. `env -i <abs python> child.py` inside a script, the other arm of the old gap, likewise inverted |
| the PATH wrappers were carrying the coverage claim | **kept, and demoted to what they are:** a second, independent chance to refuse for children the scan admitted. A record saying `path_shim: not-armed` is now narrower by one redundant check rather than open | the wrapper is still exercised as a unit and, in the same arm as the script-file refusal, called directly on the same argv so both refusers stay live |

**The residual after this round, stated exactly and no wider — and neither arm is an unscanned
Python launch.** (1) **Trust by location:** a leaf tool or a read-only `git` is admitted because its
executable was found in a named system prefix (`/bin`, `/usr/bin`, `/sbin`, `/usr/sbin`,
`/usr/local/bin`, `/usr/local/sbin`, `/opt/homebrew/bin`, `/opt/local/bin`, `/opt/slurm/bin`,
`/usr/global/bin`) and carries no shebang; nothing about its behaviour is read. So a **tampered
system prefix**, or a **repository-local `.git` configuration** naming an external program
(`diff.external`, a hook, `core.pager`), is outside this guard — those are files rather than an
argv, and the environment variables that do the same job are refused where they can be seen.
(2) **Command words built at run time:** a shell script or `-c` string whose command word comes from
a variable, a command substitution, a glob or tilde expansion is **refused and not read**, so the
residual there is *a refused launch and never an unguarded one* — the cost is a correct launcher
that must be respelled, not a wrong-tree import that runs. Every inventory record carries this as
`declared_gap`; read that constant, not this paragraph, and read it beside `path_shim`.

**One operational consequence, reported rather than smoothed over.** The `git` rule refuses when the
child's environment carries any of `GIT_SSH`, `GIT_SSH_COMMAND`, `GIT_PAGER`, `GIT_EDITOR`,
`GIT_SEQUENCE_EDITOR`, `GIT_EXTERNAL_DIFF`, `GIT_ASKPASS`, `GIT_EXEC_PATH`, `GIT_CONFIG_PARAMETERS`,
`GIT_CONFIG_GLOBAL` or `GIT_CONFIG_SYSTEM`. On a machine that exports one of these — a Claude Code
session exports `GIT_EDITOR=true` — **every** guarded `git` launch refuses, including the admitted
read-only spellings. None of the allowlisted subcommands opens an editor, so `GIT_EDITOR` and
`GIT_SEQUENCE_EDITOR` are the two members of that set whose presence is not itself a route; narrowing
the set is a judgement about how much to trust the allowlist and is **not taken here**.
