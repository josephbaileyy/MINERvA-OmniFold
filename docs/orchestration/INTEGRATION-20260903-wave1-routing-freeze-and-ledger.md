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

## 12. Reviewer round 6 (2026-09-04) — verdict BLOCK on `744660d8`, and what this revision changed

`744660d8` is **withdrawn**. Round 6 carried four BLOCKs: three against the queue's R5 enforcement
(findings 1–3, the table below) and one against the guard's coverage of shell script files
(finding 4, the rest of this section, written by the guard lane and adopted as written).

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **the "global" queue can still be split** (two clones, two `MNV_CAMPAIGN_STATE_ROOT` values, both six-hour items admitted against one 490-hour receipt) | the state root is a function of the **uid**: `pwd.getpwuid(os.getuid()).pw_dir/.mnv_campaign/<key>/campaign-queue`, read through one in-process function the suite patches; no environment variable, option, file or working directory changes it; a process whose environment still carries `MNV_CAMPAIGN_STATE_ROOT` is refused on every queue operation, naming the variable; claims and outcomes record `state_dir`, `uid` and `hostname` | `2692a67a` | reviewer mutation rerun: both clones refuse while the variable is set; with it absent exactly one item is admitted; a process whose `$HOME` differs from the passwd home still resolves the passwd home |
| **concurrent items corrupt task-id attribution** (shared `accounting.task_ids_file`; both outcomes recorded `8202_0` with one digest) | contract schema **v2**: `accounting.task_ids_file` is refused as queue-owned, and a v1 contract refuses with the same message; on claim the queue creates `<state>/runs/<item>/` with an exclusive `mkdir`, records it in the claim, and hands `<run dir>/scheduler-task-ids.json` to producer **and** validator as `MNV_CAMPAIGN_TASK_IDS_FILE`; nothing is deleted before a run; the outcome records path, ids, digest and run directory | `5eac935e` | reviewer interleaving rerun: alpha records `7101_0`, beta `8202_0`, different digests, each under its own run directory; a contract carrying `task_ids_file` refuses with the v2 message; guarded producers still launch (the campaign suite runs real ones) |
| **`release` bypassed receipt inclusion for identifiable spend** (a succeeded alpha with its id absent from the receipt was released by a typed phrase; beta was admitted) | `release` refuses when the outcome recorded **any** task id (only a committed receipt listing them releases it), refuses an `expects_scheduler_tasks: false` item (it releases on the timestamp), and applies only to a claimed, terminal, id-less run; `--reason` is gone — `--record <docs/orchestration/DECISION-*.md or AUTHORIZATION-*.md>` must be committed at HEAD with worktree-identical bytes (the receipt's own identity check, reused, not a second one) and contain `RELEASE-RESERVATION <item> outcome-sha256 <digest of the canonical outcome>`; the TTY phrase is in addition, never instead | `4c8667ca` | reviewer mutation rerun: succeeded alpha with `7101_0` absent from the receipt — release refuses and beta stays refused; an id-less item: an uncommitted record refuses, a committed record naming the wrong outcome digest refuses, the correct committed record releases and beta is admitted; an expects-false item refuses as nothing-to-release |

**Residual for finding 1, stated exactly:** admission is global per (host, uid). Two hosts, or
two uids, hold two queues; the committed receipt is the only cross-host object. The queue claims
nothing beyond that.

**Finding 4** — the closed child model — follows in the guard lane's own words.


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

### 12.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record. Verified there,
clean worktree, macOS default `TMPDIR`:

| check | result |
|---|---|
| pre-commit hook | 12 checks passed |
| `generate_manifest.py --check --committed-only` | OK, fixed point |
| control-plane and R5 meter self-tests | PASS, PASS |
| `probe-oi136-sys-path-hijack-20260826.py` | exit 0; FAIL-OPEN SET exactly 9 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT |
| nine-suite matrix on 3.11 (guard, k0 two-roots, N2 boundary, census, both ratchets, campaign, meter, routes) | 426 passed, 862 subtests passed, 1 failed: `TheRefusalIsUnchanged::test_site_packages_is_still_ignored_and_absent`, which fails identically at `744660d8` because the ephemeral `uv` build environment has an empty `site-packages` (the arm is vacuous) and passes under the system interpreter — an environment artefact, not a regression |
| `docs/orchestration` whole-directory run | the same 40 environment-dependent failures and errors as at `744660d8`; none new, none fixed |
| `generate_live_state.py --check-freshness` | STALE — deliberate; the OI-73 owner hold stands |

**Twelve real `git` spellings in non-test code are now refused under the guard** (`log`, `show`
and `diff` without `--no-ext-diff`; `git config user.name`). They are pinned as a live census in
the guard suite and listed there by `path:line`. None of them runs inside a guarded process today —
the queue is not itself guarded, its producers and validators are — and none is respelled here;
that is each owner's edit, not the integrator's.

**Dispatch record.** Findings 1–3 were implemented by codex-personal, which hit its usage limit
after its third commit and before its report; the integrator ran its verification (79 campaign
tests, the whole-directory diff against `744660d8`, both self-tests) and regenerated the MANIFEST
its last commit left stale. Finding 4 was implemented by claude-school, which committed eight times
(including this section's finding-4 text) before the dispatch's wall clock ended; the integrator
ran the matrix on that branch and again on the integrated tip. Worker branches `w1r8-contract` and
`w1r8-guard` remain local as provenance.

**What this round did not do:** no receipt committed; no compute, scheduler or cluster contact; no
ref deleted; `main` untouched; no OI-* row edited (OI-136's row still says the guard does not cross
a subprocess boundary, and that sentence is now false in the direction of understatement); the
`GIT_EDITOR` narrowing above is left untaken; LIVE-STATE.md not regenerated.

## 13. Reviewer round 7 (2026-09-04) — verdict BLOCK on `656ff895`, and what this revision changed

`656ff895` is **withdrawn**. Round 7 carried four BLOCKs: three against the guard (findings 1–3)
and one against the queue (finding 4). **Two models were replaced, not patched.** The guard's model
of shell syntax stops being the enforcement — every admitted shell now runs as bash's own
restricted mode with a wrapper-only `PATH`, and the scanner is the first refuser. The queue's
notion of "one namespace" stops being a directory on a host — it is the pinned origin remote, and
every admission is a compare-and-swap on one ref there.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **1. the exec'd file is not scanned** (`subprocess.run(["ls","-I","child.py"], executable=sys.executable)` ran Python as a leaf tool) | every wrapped primitive scans `(the real executable, argv[1:])`: `executable=` for subprocess (with `shell=True` the shell **is** the executable and `executable=` replaces it), the path argument for `exec*`/`spawn*`/`posix_spawn*`, the child's `PATH` resolution for the `p` spellings, `/bin/sh` for `os.system`; `argv[0]` is a display name and is ignored | `7db26bb2` | the reproducer refused on every primitive that takes an executable apart from argv: exit 3, `[oi136 launch]`, REFUSED-launch record, sentinel absent |
| **2. runtime-built arguments bypass the scan** (`FLAG=-I; /usr/bin/python3 "$FLAG" child.py`) | inside a shell program a token holding an expansion, backtick, glob or leading `~` refuses wherever it can select a program or an interpreter option: every token of a wrapper prefix, every token up to and including the first operand of Python or a shell, every token of `sbatch`/`srun`, every token of `git` except a literal-operand subcommand's operands after `--`; `xargs` refuses any non-leaf command; `python3 x.py "$@"` stays admitted, `python3 "$@"` refuses — **and** the restricted rewrite refuses the slash in `/usr/bin/python3` regardless | `7db26bb2`, `40987967` | refused by the static layer; refused again by restricted bash with the static layer disabled through a suite-only knob (both layers measured independently) |
| **3. `cd` before a relative script** (benign `child.sh` scanned, malicious `sub/child.sh` run) | the scanner keeps a **set** of candidate working directories that `cd`/`pushd` grows and that `CDPATH`, `cd -`, `cd ~x`, a bare `cd` or a runtime operand marks unknown; a relative operand is resolved against every candidate and every existing resolution is read and scanned; write-then-execute (a redirection or `cp`/`mv`/`ln`/`tee`/`sed -i`/`chmod` target that is also a script operand) refuses — **and** restricted bash refuses `cd` outright | `7db26bb2`, `40987967` | the pair refused statically (the malicious candidate is found); with the scanner disabled, bash refuses the `cd`; the all-benign pair is likewise refused by bash, reported as the model rather than smoothed over |
| **the model behind all three** | `install()` pins a real bash from a named system prefix with its sha256; every admitted shell launch (`bash`/`sh`/`dash` with `-c` or a script, shebang scripts, `shell=True`, `os.system`) is rewritten to `<that bash> -r [--posix] …` with `PATH` = the guard's wrapper directories only and `SHELLOPTS`, `BASH_ENV`, `ENV`, `CDPATH`, `BASH_FUNC_*`, `LD_PRELOAD`, `DYLD_*`, `PYTHONHOME`, `PYTHONEXECUTABLE` removed; bash itself then refuses slashes in command names, `cd`, `exec`, `PATH`/`ENV` assignment, `command -p`, `hash -p`, `enable -f`, redirection and `set +r`, and everything not in the wrapper directory is `command not found`; committed wrappers for `bash`, `sh`, `git`, `sbatch`, `srun` and the five reporting Slurm clients delegate to `wrapper_exec.py`, and `install()` generates one forwarder per leaf tool present under a system prefix; `zsh` is refused (its restricted mode is not modelled); a shell started **by** a restricted shell re-enters restricted mode; every record carries `shell`, `real_bash`, `static_scan`; all sixteen committed shim files are bound by the queue | `7db26bb2`, `71834b05`, `d2e456b2` | nine existing arms changed verdict and each says why in its docstring (`zsh -f` refused; `-o`/`+r`/`-O restricted_shell` refused; the all-admissible pipeline lost its `cd` and `> /dev/null`; the decoy-interpreter arm moved to a non-shell child); no rule was weakened to keep an assertion |
| **4. R5 splittable across passwd homes** (two hosts, one 490-hour receipt, 502 projected) | every admission-deciding family — items, approvals, claims, outcomes, releases, revocations, the admission log — lives in a git tree on `refs/campaign/<key>/queue` at the origin pinned in the committed `control-plane/campaign-origin.json` (campaign key, ruling record and its sha256, the URL `git remote get-url origin` prints, the ref name); every operation fetches the ref, makes the cache exactly that tree, acts, and lands the mutation with `--force-with-lease` against the fetched sha — the reservation scan and the claim are **one push**; a fetch that cannot reach the origin refuses; a rejected lease discards the mutation and refuses with a lost-race reason a later tick may retry, nothing is merged; an outcome, release or revocation whose push does not land waits in the cache and the item keeps reserving in the ref; only the lease and non-fast-forward reasons mean the ref moved (a server ruleset's `[remote rejected]` is a refusal, not a race); `GIT_TERMINAL_PROMPT=0` and the hook-redirecting `GIT_*` variables cleared on every git call; the pin is a new receipt binding (119 → 120, the delta enumerated) | `4f5abf70`, `f51e3273`, `53c6ac8c` | reviewer mutation rerun with two **different** passwd homes and one bare origin: exactly one item admitted, the other's producer never ran; the lost lease and its retry; the unpushed outcome; the unreachable origin; the URL mismatch; the uncommitted and mis-keyed pin; the checked-in pin's agreement with the module; the campaign suite is 91 tests |

**Residuals, stated exactly.** Guard (`DECLARED_GAP`, on every record): (1) trust by location — a
leaf tool, read-only `git`, `sbatch` and the real bash are run because their file was found under a
named system prefix with no shebang, so a tampered prefix or a repository-local `.git`
configuration naming an external program is outside the guard; (2) the restricted-shell guarantee
is bash's own (manual §6.10), so a defect there is the residual for shells; (3) an `sbatch` job
script runs on the cluster outside this process tree, where the static model is the enforcement
and its residual is a **refusal** — a job script built at run time is refused, not read; (4) an
admitted Python child is guarded by the shim and these hooks in turn. Queue: the origin remote
named in the pin is the namespace; a clone whose origin is a different repository is a different
repository and its receipts are its own; the ref moves only by lease, so a force-push of the ref
without a lease is a repository write outside this tool; the ticker now needs push permission for
`refs/campaign/*`, and a ruleset or an expired credential refuses every admission rather than
admitting silently.

### 13.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record. Verified there,
clean worktree, macOS default `TMPDIR`:

| check | result |
|---|---|
| pre-commit hook | 12 checks passed |
| `generate_manifest.py --check --committed-only` | OK, fixed point |
| control-plane and R5 meter self-tests | PASS, PASS |
| `probe-oi136-sys-path-hijack-20260826.py` | exit 0; FAIL-OPEN SET exactly 9 (the ratchet test pins it) |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT (120 receipt bindings) |
| nine-suite matrix on 3.11 (guard, k0 two-roots, N2 boundary, census, both ratchets, campaign, meter, routes) | 463 passed, 1 skipped, 944 subtests passed, 1 failed: `TheRefusalIsUnchanged::test_site_packages_is_still_ignored_and_absent`, the same environment artefact as §12.1 (empty `site-packages` in the ephemeral `uv` build environment; passes under the system interpreter) |
| `docs/orchestration` whole-directory run | the same 40 environment-dependent failures and errors as at `744660d8` and `656ff895`; none new, none fixed |
| `generate_live_state.py --check-freshness` | STALE — deliberate; the OI-73 owner hold stands |

**One integration conflict, resolved as a union and named in the pick.** The guard lane batched
the queue's committed-file lookups (`git cat-file --batch`, because sixteen bound shim files made
the one-wall-deadline control drift past its budget) while the queue lane rewrote the same
methods for the origin model; `40987967` keeps both — the batched lookup with the queue lane's
git environment, and the queue lane's blob-id helper — and the 91-test campaign suite passes on
the union.

**Dispatch record.** Both pieces ran on claude-school in parallel off `656ff895`, detached from
any tool timeout; both hit the account's session limit after committing with clean worktrees and
before reporting, so the integrator ran every verification on each branch and again on the
integrated tip. Worker branches `w1r9-contract` and `w1r9-guard` remain local as provenance.

**What this round did not do:** no receipt committed; no push to `refs/campaign/*` at the real
origin (the pin names it; nothing has been written there); no compute, scheduler or cluster
contact; no ref deleted; `main` untouched; no OI-* row edited; LIVE-STATE.md not regenerated.

## 14. Reviewer round 8 (2026-09-04) — verdict BLOCK on `9c2969fa`, and what this revision changed

`9c2969fa` is **withdrawn**. Round 8 carried two findings, and they are the narrowest of the eight
rounds: a configuration asymmetry in the queue's push destination, and a coverage claim in §13 that
the guard's public-API enumeration did not support.

**§13 is corrected, not merely extended.** Its residual paragraph was written as exhaustive
("stated exactly and no wider"), and residual (4) said an admitted Python child is guarded by the
shim and these hooks in turn. The reviewer reached the kernel below the enumerated primitives —
`_posixsubprocess.fork_exec` directly, and `multiprocessing.set_executable`, which is public API —
and a `python3 -I` child ran with no refusal and no record. Residual (4) as written implied
coverage the code did not have. It is replaced below, and the layer it names is now hooked.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **the push destination is not the pinned one** (`GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL` each landed the lease-protected push in a second bare repository while `ls-remote` and `fetch` still answered from the pin; `stage()` returned success and the pinned origin's queue ref did not exist afterwards) | the asymmetry is closed at both ends. **The environment:** every git invocation the module makes runs with `GIT_INJECTING_ENVIRONMENT` removed — the six configuration-injecting names, the numbered `GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*` half by pattern because it cannot be enumerated, and the ten program-selecting names the guard lane already refuses — and with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` **set**, so only repository-local configuration applies, which is the one scope the destination check can enumerate. **The destination:** `QueueSync` reads both `git remote get-url origin` and `git remote get-url --push origin` **in the scratch bare repository that actually pushes**, and refuses unless both normalise equal to the pin; it refuses configuration in its own git directory that the queue did not write, and `core.hookspath`, `core.sshcommand`, and a `!`-spelled `credential.helper` outright **(SUPERSEDED BY §15: as written here this was a namespace rule over `remote.origin.*` and `url.*` plus a two-item forbidden list, and the claim that "a key git adds later cannot slip through" was FALSE of the list half — `core.fsmonitor` slipped it and ran. §15 replaces both with an allowlist of the keys the queue itself writes.)**; the push goes to the literal pinned URL rather than to the remote name, and the admission log records the resolved push destination beside `origin_url` | `08d184ea`, `a8ebd393`, `95c0976c` | each of the three environment vectors and both configuration routes measured against a diverted second origin, with a no-injection control that lands on the pinned origin and a positive control proving the injection really diverts an unsanitised push; the diverted repository holds no refs afterwards; campaign suite 98 passed (+36 subtests), was 91 — **103 after §15** |

**One deliberate departure from the integrator's brief, and it matches the reviewer's own remedy.**
The brief said the three environment vectors must *refuse on presence*. The lane made them **inert**
instead, and it is right: git **exports** `GIT_CONFIG_PARAMETERS` to its hooks, and campaignctl is a
supported hook invocation, so refusing on presence would refuse every correct run from a hook — the
same reason `GIT_REDIRECTING_ENVIRONMENT` has always cleared `GIT_DIR` rather than refusing it. The
reviewer's stated remedy was to add the family to that clearing set, which is what was done. The
"must refuse" half is measured on the two routes clearing cannot reach: a `pushurl` written into the
scratch repository behind the queue's back, and a checkout whose own config sets one. Measured
separately, either layer catches all three vectors without the other.

**An operational consequence, reported rather than smoothed over.** `~/.gitconfig` and
`/etc/gitconfig` are now invisible to campaignctl, and the pinned origin is an `https://` URL. If a
ticker host's credentials come from a **global** helper (the macOS keychain, the `gh` helper), its
first unattended tick will refuse with `campaign origin is unreachable` rather than authenticate.
That is fail-closed and correct, and the remedy is in OPERATOR-GUIDE — a non-`!` helper in the
queue's own local config, or an SSH identity with `BatchMode` in `~/.ssh/config` — but **it must be
done on each ticker host before the first unattended tick**, and this lane could not verify which
mechanism the Perlmutter checkout uses.

| reviewer BLOCK | resolution | commit | proof |
|---|---|---|---|
| **the record claims coverage the code does not have** (`_posixsubprocess.fork_exec` and `multiprocessing.set_executable` both started a `python3 -I` child with no refusal and no record, while the reviewer's controls through `subprocess.run`, `os.posix_spawn` and `executable=` all refused) | **the floor is hooked, so coverage stops being an enumeration of public APIs.** `_posixsubprocess.fork_exec` is wrapped in **both** bindings CPython gives it — the module attribute that `multiprocessing.util.spawnv_passfds` calls, and the `_fork_exec` alias `subprocess` binds at import, which rebinding the first does not touch — so `subprocess.Popen`, multiprocessing's spawn **and** forkserver, `concurrent.futures` and a direct caller are all scanned with the executable and argv they pass. `multiprocessing.set_executable` is classified where the choice is made. A covering search of each interpreter's stdlib finds `fork_exec` named in exactly two files, both hooked; a floor around a floor is a no-op by marker | `37e05a84`, `a31ab5f6` | both reproducers inverted (exit 3, refusal reason, record, sentinel absent); the reviewer's three controls unchanged; every start method and `ProcessPoolExecutor` still runs with a depth-1 guarded-child record; the four argument positions re-derived in the test by parsing `Popen._execute_child`'s own callsite; identical on 3.11, 3.12 and 3.13 |
| *(integrator finding on that work, not the reviewer's)* **the new approval ticket was keyed on the argv alone** — round 8's own lesson is that the argv is not the executable, and the ticket's docstring claimed a `preexec_fn` launch "does not match and is scanned", which is false whenever the argv is the same | the approval is keyed on **`(argv, realpath of the resolved file)`**, computed by one function at every issue and consume site so the two halves cannot drift, with `None` matching only an equally unnameable file and never acting as a wildcard; `preexec_fn` is refused outright at the `Popen` hook with its own reason | `9d14e7c0` | the gap reproduced as a regression test and **proven load-bearing by reverting each half separately**: with the argv-only key restored the callback test goes red printing `HIJACK-LOADED WRONG TREE`, and with the `preexec_fn` check removed only its own test goes red; the reproducer uses `stdout.fileno()`, which `Popen._get_handles` calls inside the window in the same thread, rather than a `preexec_fn` that the new refusal would catch first and so would have measured the wrong half; no launcher in the repository passes `preexec_fn`, measured over tracked and untracked files, and a census arm goes red if one grows |

**Residual (4) replaced, and this is the correction §13 needed.** It now reads: an admitted Python
child is guarded by the shim and these hooks in turn **down to `_posixsubprocess.fork_exec`, the
last Python-visible layer before the kernel on POSIX**; what remains is a caller that reaches the
kernel without that layer — `ctypes` or `cffi` calling `execve`/`posix_spawn` in libc directly, a C
extension doing the same, or a rebuilt interpreter whose `_posixsubprocess` is not the module object
this process patched. That is named and not covered, and it is **measured rather than asserted**: a
test runs a `ctypes` `execve` of `python3 -I` and pins that it succeeds. Residuals (1) to (3) are
unchanged. Four residuals, not five.

### 14.1 Proposed tip, revised

The last commit of `wave1-integration-20260903` as force-pushed after this record. Verified there,
clean worktree, macOS default `TMPDIR`:

| check | result |
|---|---|
| pre-commit hook | 12 checks passed |
| `generate_manifest.py --check --committed-only` | OK, fixed point, 727 rows |
| control-plane and R5 meter self-tests | PASS, PASS |
| `probe-oi136-sys-path-hijack-20260826.py` | exit 0; FAIL-OPEN SET exactly 9 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT |
| nine-suite matrix on 3.11 | 500 passed, 1 skipped, 985 subtests, 1 failed — `test_site_packages_is_still_ignored_and_absent`, the same `uv` artefact recorded in §12.1 and §13.1 (empty `site-packages` in the ephemeral build environment; passes under the system interpreter) |
| `docs/orchestration` whole-directory run | the same 40 environment-dependent failures and errors as at `744660d8`, `656ff895` and `9c2969fa`; none new, none fixed |
| `generate_live_state.py --check-freshness` | STALE — deliberate; the OI-73 owner hold stands |

**Dispatch record.** Both round-8 pieces ran on claude-school in parallel off `9c2969fa`, detached.
Both reported cleanly this time. The integrator then read the guard lane's new approval ticket,
found the argv-only key described above, and dispatched a third, narrow piece to the same lane;
that fix and its load-bearing proof are `9d14e7c0`. Worker branches `w1r10-contract` and
`w1r10-guard` remain local as provenance.

**What this round did not do:** no receipt committed; nothing pushed to `refs/campaign/*` at the
real origin (`ls-remote` still shows none); no compute, scheduler or cluster contact; no ref
deleted; `main` untouched; no OI-* row edited; LIVE-STATE.md not regenerated.

### 14.2 What the next round should grade against

Eight rounds have moved from missing mechanism (no meter, no atomic admission, no shell coverage)
to replaced models (restricted bash, the origin-ref lease) to, in this round, one configuration
asymmetry and one private C primitive. Each remaining finding has been smaller and deeper in the
interpreter than the last, and the next one down is `ctypes`, which residual (4) now names and
measures rather than claims.

That is convergence, but the criterion the rounds are graded against has no floor: an in-process
adversary who declines every Python-visible API can always reach lower. This lane therefore
proposes, and does **not** assume, the boundary the next verdict should be given against:

* **In scope, and expected to hold absolutely:** a cooperating launcher that reaches a wrong tree,
  a wrong interpreter or an unaccounted spend through any documented or ordinarily-used route —
  every public launch API, every shell spelling, the scheduler clients, and the whole of the
  queue's accounting.
* **Out of scope, by declaration and recorded as residuals (1) to (4):** code inside an already
  guarded process that deliberately bypasses the interpreter to reach the kernel (`ctypes`, `cffi`,
  a C extension, a rebuilt interpreter), and files rather than argv on a trusted system prefix (a
  tampered prefix, a repository-local `.git` configuration).

The lane asks the reviewer to grade the next revision against that boundary and to say plainly
either that it is met, or which specific route the boundary must still be widened to cover. The
remaining hardening below that line belongs to OI-136's owner and its row, not to this integration.

## 15. Reviewer round 9 (2026-09-05) — three findings on `5d294883`, and the boundary corrected

`5d294883` is **withdrawn**. The round-9 report closed both round-8 BLOCKs against the reviewer's own
unedited reproducers, confirmed the two queue layers are independent rather than one claim measured
twice (a `include.path` pointing at a file carrying `url.*.pushInsteadOf` slips the namespace rule and
is still caught by the destination check), and raised three findings. All three are taken here.

### 15.1 The boundary, corrected — §14.2 is superseded

§14.2 proposed grading against two halves: cooperating launchers in scope absolutely, and code
bypassing the interpreter to reach the kernel out of scope by declaration. **The reviewer's answer is
that the line is in the wrong place, and this lane accepts it without reservation.** Findings 1 and 2
below are neither cooperating launchers nor kernel bypasses: both travel through layers this guard
hooks — the `fork_exec` floor, and the queue's own `git` invocations. `9d14e7c0`, the fix this lane
disclosed and proved load-bearing last round, lives in that same gap, so §14.2 as written would have
excluded a fix it had just shipped. A boundary that excludes your own last correction is the wrong
boundary.

**The in-scope half is therefore widened, in the reviewer's words:** *any route that reaches the
kernel or the origin through a layer this guard hooks, cooperating or not.* The out-of-scope half is
unchanged and stays measured rather than asserted: `ctypes`/`cffi` calling libc directly, a C
extension doing the same, a rebuilt interpreter whose `_posixsubprocess` is not the patched module
object, and files rather than argv on a trusted system prefix. Residuals (1)–(4) already name exactly
that, and the `ctypes` arm asserts the hijack **succeeds**, so it goes red if the residual ever
silently closes.

**The reviewer also corrected its own round-7 record**, and it belongs here because it changes what a
prior certification meant: that round's "guard suite 172 OK" was 172 of 221 declared arms, truncated
by the same mid-file entry point that finding 3 describes. This lane's own matrix invokes the file a
way that collects everything, so the 500-passed figure in §14.1 stands as written.

### 15.2 The three findings

| reviewer finding | resolution | commit | proof |
|---|---|---|---|
| **1. the ticket key omits the environment.** Keyed on `(argv, file)`, the floor's ticket path returned `original(*call_args, **call_kwargs)` — the caller's own `env_list`, never checked and never re-armed. Through the lane's own `stdout.fileno()` seam, an in-window call matching both halves of the key while stripping only `MNV_GUARD_*`/`PYTHONPATH` produced `CHILD-ENV-UNGUARDED / HIJACK-LOADED WRONG TREE / exit 0 / no refusal recorded`; the same call with the full environment gave `CHILD-ENV-GUARDED / TICKET-SPENT 3 / no hijack`. One field, both directions | the reviewer's remedy taken literally: the environment is **checked on the ticket path, not added to the identity** — which cannot reintroduce the false refusal the ticket exists to prevent, because a correct launch's environment already is the armed one. The identity stays `(argv, file)`. `_environment_reaching_child_is_armed` now runs at **both** consume sites before the launch: the kernel floor's `guarded()`, and the `_prepare_launch` ticket path that `os.posix_spawn` reaches on every `close_fds=False` launch — a second site the integrator's brief did not name and the lane found. New reason `LAUNCH_REASON_TICKET_ENV`, distinct from `LAUNCH_REASON_ENV` because the claim differs: the older one says the scan read this launch and its argv or environment strips the contract; this one says a layer above approved this argv and this file and the contract went missing **between the layers**, which is where a reader of the record must look. `env=None` is admitted, because at both layers it means inherit and what an inheriting child receives is this armed process's own environment — the very thing the helper reads. `_ApprovedLaunch`'s docstring is rewritten: the sentence the reviewer quoted is gone, and the replacement states that the ticket certifies only that the layer above scanned this argv and this file, never the environment | `00ad57cb` | reproducer red before the fix with the hijack verbatim (`HIJACK-LOADED WRONG TREE / TICKET-SPENT 0 / OUTER-EXIT 3`), green after; reverting **only** the `_prepare_launch` call turns only the `os.posix_spawn` arm red, attributing each arm to its own site; the inheriting launch has its own arm driving `env_list=None` through the floor; 26 named controls re-run, including `subprocess.run("ls", shell=True, close_fds=False)`, spawn, forkserver, `ProcessPoolExecutor`, both `fork_exec` bindings refusing `-I`, `preexec_fn`, and every round-6/7/8 reproducer |
| **2. the program-installing config category is a list of two.** The namespace rule was justified as "a rule spelled as a list has to be extended for every key git adds, and the failure of the missing entry is a diverted push that reports success" — and then the forbidden keys were a two-item list. `core.fsmonitor`, pointed at a script in the scratch repository's own config, **was executed twice** by the queue's own read-tree/add/write-tree, and the operation was admitted | the lane's own design taken literally, as the reviewer prescribed: the queue creates that directory and writes a known set, so **any key outside `QUEUE_SCRATCH_WRITTEN_CONFIG_KEYS` refuses**, with the single exception of `credential.helper` when its value does not begin with `!` **(SUPERSEDED BY §16: that exception admitted an ABSOLUTE PATH, which git executes on the queue's own `ls-remote`; the value is now constrained character by character)**. Both `QUEUE_SCRATCH_GUARDED_CONFIG_PREFIXES` and `QUEUE_SCRATCH_FORBIDDEN_CONFIG_KEYS` are deleted, with no remaining reference in the tree; the category is retired rather than extended. The written set gains the four keys `git init --bare` writes itself, each commented as such, and a completeness arm reads a freshly created scratch repository with a plain subprocess — not through the queue's own reader, so the fixture is not derived from the code it checks — and asserts nothing outside the set is present. A git version writing a key the set lacks **refuses rather than admits**, which is the right direction, and the docstring says so. `verify_push_destination` is untouched: both layers still run | `020ebaec` | `core.fsmonitor` refuses **before its program runs** (sentinel absent), and load-bearing: with `campaignctl.py` reverted the sentinel is present carrying two lines, the script having executed twice while `stage` built its state commit; `core.sshcommand`, `core.hookspath` and a `!` helper each with their own sentinel; `core.pager`, `alias.x` and `protocol.ext.allow` refuse though no rule ever named them; a non-`!` helper still admitted through a whole cycle; campaign suite 103 passed (+46 subtests), was 98 |
| **3. `unittest.main()` sat mid-file**, so the guard suite's own entry point ran 202 of 251 arms and exited 0, truncating away `TheDefectMutationFires`, `TheInnocentMutationStaysGreen` and `TheRefusalIsUnchanged` — the arms that prove the detectors still fire. Pre-existing at `656ff895`, `9c2969fa` and `5d294883` alike | the entry point moves to the end of the file, and a regression guard reads **this module's own source** through `inspect.getsource` (so it reads whichever file is running, under either route), parses it, and asserts one top-level `if __name__` block that is the **last top-level statement** — the actual invariant, since `sys.exit` does not care whether what follows is a class, a constant or a second `unittest.main()` | `1325d6b7` | arms collected by the file's own entry point: **202 before, 261 after**, equal to `-m unittest` and to pytest collection on both 3.11 and 3.12; the guard parses rather than greps, proven by an opposite-direction arm whose source carries `if __name__ == "__main__":` **inside a string** and must not count — this suite writes dozens of child programs containing that line, so a regex version would refuse every future commit |

**A record item the guard lane could not write and this lane owes it:** `LAUNCH_REASON_TICKET_ENV` is
new, and it takes the existing `refused:launch-python-startup-flags` outcome rather than a new
literal, so no ratchet re-routes. The residual **count is unchanged** — this closes a live defect
rather than declaring a new residual — and residuals (1) to (4) stand exactly as §14 states them.

**§14 is corrected in place, not merely superseded.** Its queue row asserted "a namespace rule, not a
list, so a key git adds later cannot slip through" — the precise claim finding 2 refuted — and quoted
a campaign-suite count that has moved. Both are amended where they stand, so the row cannot be read
in isolation and believed.

### 15.3 Proposed tip

The last commit of `wave1-integration-20260903` as force-pushed after this record. Verified there,
clean worktree, macOS default `TMPDIR`:

| check | result |
|---|---|
| pre-commit hook | 12 checks passed |
| `generate_manifest.py --check --committed-only` | OK, fixed point, 727 rows |
| control-plane and R5 meter self-tests | PASS, PASS |
| `probe-oi136-sys-path-hijack-20260826.py` | exit 0; FAIL-OPEN SET exactly 9 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT |
| nine-suite matrix on 3.11 | 515 passed, 1 skipped, 996 subtests, 1 failed — the `site-packages` `uv` artefact recorded since §12.1 (empty purelib in the ephemeral build environment; passes under the system interpreter) |
| guard suite via **the file's own entry point** | Ran 261 tests, OK (skipped=1) — the number finding 3 was about, now equal to `-m unittest` and to pytest collection |
| `docs/orchestration` whole-directory run | the same 40 environment-dependent failures and errors as at every tip since `744660d8`; none new, none fixed |
| `generate_live_state.py --check-freshness` | STALE — deliberate; the OI-73 owner hold stands |

**Dispatch record.** Both pieces ran on claude-school in parallel off `5d294883`, detached, and both
reported cleanly. Each carried a load-bearing check performed by reverting the fix and watching the
new arm reproduce the reviewer's own output, then restoring byte-identically; neither revert is
committed. Worker branches `w1r11-contract` and `w1r11-guard` remain local as provenance.

**What this round did not do:** no receipt committed; nothing pushed to `refs/campaign/*` at the real
origin, which still holds none; no compute, scheduler or cluster contact; no ref deleted; `main`
untouched at `dae18f22` with its seven untracked paths; no OI-* row edited; LIVE-STATE.md not
regenerated.

**Where this leaves the campaign.** R1–R4 and R6 have passed unchanged since round 3. R5 and the
deployment guard are now closed against every route the corrected boundary admits, and what remains
below it is named in residuals (1)–(4) and measured rather than asserted. The remaining hardening —
`ctypes`/`cffi`, a C extension, a rebuilt interpreter, a tampered system prefix — belongs to OI-136's
owner and its row, not to this integration. **(CORRECTED BY §16: the sentence about R5 was false as
written. Round 10 found a route the corrected boundary admits and R5 did not cover — a
`credential.helper` spelled as an absolute path, which git executes on the queue's own `ls-remote`.
The guard half held: round 10 returned no live guard finding. This lane also read the hand-off
sentence as the campaign's stop signal, and it was the wrong lane to read it in; §16.4 says where
the stop signal actually was.)** Nothing here is admissible for compute regardless: the
queue admits no item until a receipt measured on Perlmutter is committed, cause-3 compute is
suspended by §5 of the ruling record, and PET remains diagnostic.

## 16. Reviewer round 10 (2026-09-05) — one finding on `d78a2d37`, in the queue lane

The verdict was BLOCK with a single finding, and everything else the reviewer re-ran came back
closed against its own reproducers, unedited: the ticket now refuses an approved launch whose child
environment is not the armed one, its matching-file control is still ADMITTED with a guarded child so
the fix bought no false refusal, all five configuration arms refuse with `core.fsmonitor` refusing
before its program runs, and the file's own entry point and `-m unittest` both collect 261. Three of
those checks went past what this lane had proved, and each is recorded because it changes what the
certification means:

* **The environment check reads the EFFECT, not the names.** The reviewer kept every `MNV_GUARD_*`
  variable intact and rewrote only `PYTHONPATH` to an empty directory; the launch still refuses. A
  check that had compared variable names would have passed that mutation.
* **`env_list=None` is admitted and the child is really guarded** — `CHILD-HOOKS True`,
  `SHIM-ON-PATH True` — which confirms this lane's inherit arm from outside it.
* **The AST entry-point guard was mutation-tested.** One class appended after the block turns it red
  naming the exact line; an unmodified copy of the same file stays green, so the arm fires on the
  defect and not on the copying.

One consequence of round 9 the reviewer recorded rather than filed: an `include.path` now refuses at
the **configuration rule** instead of at the push-destination comparison, because the allowlist runs
first. `verify_push_destination` still stands behind it, and both layers still run.

### 16.1 The finding, and what makes it the same actor as `core.fsmonitor`

The allowlist's one exception admitted a `credential.helper` whose value did not begin with `!`. A
leading `!` is the spelling git hands to a shell — and it is not the only spelling git RUNS. An
absolute path is executed directly. Measured by the reviewer against a loopback origin answering 401,
which is what makes git consult a helper at all, and reproduced independently here on a second
account before the fix was written (git 2.39.3, Apple Git-146; one execution per `ls-remote`, with no
configuration rule in the way so git saw every value):

| `credential.helper` value | round-9 config rule | the program |
|---|---|---|
| `/abs/path/helper-A.sh` | **admitted** | **RAN** — the finding |
| `!/abs/path/helper-B.sh` | refused | RAN when git saw it (see below) |
| `store; /abs/path/helper-C.sh` | **admitted** | **RAN** |
| `store --file=$(/abs/path/helper-D.sh)` | **admitted** | **RAN**, through the substitution |
| `store` + newline + `/abs/path/helper-E.sh` | **admitted** | **RAN** as the shell's second command |
| `store` + tab + `/abs/path/helper-F.sh` | admitted | did not run — the tab stayed inside one word |
| `sub/dir/helper-G.sh` (relative) | admitted | did not run — `git credential-sub/dir/...` is no command |
| `store --file=/abs/path/creds` | admitted | `git credential-store`, which is the point |
| `mnvprobe`, `git-credential-mnvprobe` on `PATH` | admitted | RAN — the legitimate case |

One correction to the reviewer's own table, in the direction that makes the rule stricter rather than
looser: `!/abs/path/helper-B.sh` was recorded as `never ran`. What never ran is the whole operation —
the config rule refused that spelling first. With no rule in the way git executes it, so `!` and an
absolute path are the same kind of thing to git and the old rule's distinction between them was not
about what runs.

The reusable half is the reviewer's, and it is why round 9's fixture could not see this: **the
fixture's origin is a local path, so every credential route is inert in it by construction.** Round
9's own honesty note had already said that of `core.sshCommand` and the `!` helper — the identical
reasoning applied to the one key still being admitted, and that is the key where it mattered, because
the production pin is `https` and OPERATOR-GUIDE tells operators to put a helper in exactly this
local config. The exception is therefore present in production scratch directories BY DESIGN.

### 16.2 The rule, and the two places it goes past the stated remedy

The remedy asked for a slash-free bare helper name with arguments allowed. That is adopted, and
extended by two measurements, because a rule that constrained only the first token would have had
this finding's shape one layer in. git assembles the value into ONE command string — the value itself
when bang-prefixed or absolute, otherwise `git credential-<value>` — and hands that string to `sh -c`
as soon as it holds a space or a shell metacharacter, so the argument half of a value is shell source
and not data.

`credential_helper_is_a_bare_name` splits the value on SINGLE spaces and admits it only when the
first token matches `[A-Za-z0-9][A-Za-z0-9._-]*` and every later token matches
`[A-Za-z0-9._,:+@=/~-]+`. So:

* the NAME may not hold a slash, which refuses an absolute path, `../x` and a bang;
* an ARGUMENT may hold a slash, so `store --file=/etc/mnv/creds` keeps working, but may not hold
  `$`, a backtick, `;`, `&`, `|`, a parenthesis, a redirection, a quote or a glob — rows C and D
  above, both of which RAN;
* the SEPARATOR is a single space, not generic whitespace. That is row E: a config value may hold a
  newline, which is why `scratch_config` reads `-z`, and a whitespace split would have read the
  second line as an ARGUMENT — where slashes are legal — and git ran it. Splitting on single spaces
  leaves the newline inside a token, where the character allowlist refuses it;
* an empty value refuses.

Rows F and G are refused too, though neither executes on this git; for those two the arms are
REGRESSION GUARDS and their docstrings say so, in the same sense round 9 used for `core.sshCommand`.
`CREDENTIAL_HELPER_SHELL_PREFIX` is retired with no remaining reference in the tree, and the sentence
"does not begin with `!`" is gone from `campaignctl.py`, `test_campaignctl.py` and OPERATOR-GUIDE.

**The fixture is an HTTP PIN with a positive control.** A `ThreadingHTTPServer` on `127.0.0.1` port 0
answers every request 401 with a Basic challenge — no network, no external process, torn down by
`addCleanup`. Its positive control is `credential.helper = mnvprobe` with an executable
`git-credential-mnvprobe` on `PATH`: admitted by the new rule, sentinel APPEARS, operation then fails
at the unreachable origin. Without it, "the sentinel is absent" in the refusal arms would hold just
as well in a fixture where no helper could ever run — which is exactly the defect being fixed.

**Load-bearing.** With only `campaignctl.py` reverted to `d78a2d37` the absolute-path arm goes red
with the sentinel PRESENT carrying two `ran get` lines from a single `summary` — one `ls-remote` in
`QueueSync.refresh`, one in the `discard` that `queue_operation` runs on the way out — and the bang
arm goes red on the refusal text. Restored byte-identically, not committed.

### 16.3 The operational cost, which is an operator's decision and not a defect

A helper installed as an absolute path — Git Credential Manager, or
`/usr/libexec/git-core/git-credential-libsecret` — is now REFUSED in the queue's git directory and
must be respelled as the bare name whose `git-credential-<name>` is on `PATH`. This stacks with the
round-8 consequence that `~/.gitconfig` is no longer read at all. Both are stated in OPERATOR-GUIDE.
A URL-scoped `credential.<url>.helper` is refused as well, and has been since round 9's allowlist,
because only the exact key `credential.helper` is excepted. **No ticker host has been configured, so
nothing is broken today; the decision of what a Perlmutter ticker host's credential is belongs to
Joseph or the site owner.**

### 16.4 Where the stop signal actually was

This lane proposed after round 9 that the campaign stop and the residual hardening pass to OI-136's
owner. The reviewer showed the reasoning pointed at the wrong lane: against the boundary adopted in
§15.1 the guard passes and returned no live finding this round, while every finding since round 7 has
been in the queue's configuration surface — fetch-versus-push, then an incomplete denylist, then the
last unconstrained value inside the allowlist that replaced it. Each is strictly narrower than the
one before, and after this fix the allowlist admits no unconstrained value at all: every admitted key
is a key campaignctl wrote, and the one exception's value is now constrained character by character.
The hand-off of residuals (1)–(4) to OI-136's owner still stands on its own merits; it is not what
ends the campaign.

### 16.5 Proposed tip

The last commit of `wave1-integration-20260903` as force-pushed after this record. Verified there,
clean worktree, macOS default `TMPDIR`:

| check | result |
|---|---|
| pre-commit hook | 12 checks passed |
| `generate_manifest.py --check --committed-only` | OK, fixed point, 727 rows |
| control-plane and R5 meter self-tests | PASS, PASS |
| campaign suite | 106 passed (+90 subtests), was 103 (+46) |
| `probe-oi136-sys-path-hijack-20260826.py` | exit 0; FAIL-OPEN SET exactly 9 |
| `verify_hash_bindings.py` | ALL BINDINGS INTACT |
| nine-suite matrix on 3.11 | **522 passed**, 1 skipped, 1040 subtests, 1 failed — the `site-packages` `uv` artefact recorded since §12.1. Measured against a SAME-SET baseline taken at `d78a2d37` in this same environment rather than against the published number: **519 passed, 996 subtests, the same 1 failed**, so the delta is exactly **+3 arms and +44 subtests, zero new failures**. §15.3's 515 is not that baseline — this lane could not recover the exact file list behind it and rebuilt the set from the ledger's own parenthetical, which turns out to hold four tests more; the honest comparison is the one taken here, and the only suite this change can reach is the campaign suite, whose own delta is +3 |
| guard suite via the file's own entry point | Ran 261 tests, OK (skipped=1) — unchanged, and the guard was not touched this round |
| `docs/orchestration` whole-directory run | 23 failures, and `comm` against the saved 40-failure baseline reports **none new**. The count moves run to run in this directory, which is why the comparison is against a saved set and not against a number |
| `generate_live_state.py --check-freshness` | STALE — deliberate; the OI-73 owner hold stands |

**Dispatch record.** The fix ran on claude-school in a worktree off `d78a2d37` and reported cleanly;
the measurement of what git does with each helper spelling ran in parallel on codex-school, in a
throwaway directory with no repository access, so the rule's justification comes from two accounts
that did not see each other's work. Their tables agree on every row. The worker's commit is on the
branch VERBATIM — it was written on top of the accepted tip, so there was no rebase and the sha that
was tested is the sha that is proposed. Worker branch `w1r12-credential` remains local as provenance.

**What this round did not do:** no receipt committed; nothing pushed to `refs/campaign/*` at the real
origin, which still holds none; no compute, scheduler or cluster contact; no ref deleted; `main`
untouched at `dae18f22` with its seven untracked paths; no OI-* row edited; LIVE-STATE.md not
regenerated; the guard lane not touched, because it had no finding.
