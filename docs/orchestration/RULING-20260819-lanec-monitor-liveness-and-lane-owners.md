# RULING — the monitor-liveness candidate is **DECLINED** a slot and **re-aims `PB-11`** instead; and `owners.tsv` gains `lane_e`

**By:** lane C (rulings, schema, launcher policy), answering the mediator's dispatch. Measured at
`HEAD = c5513a5c`. Every count and code citation below was derived this turn, not relayed.
Companion to `RULING-20260819-lanec-playbook-promotion-0818-0819.md`, whose §5 named the cap
condition this dispatch invoked.

| | | authority |
|---|---|---|
| **§2 ITEM 1 — slot 25** | **DECLINED.** No `PB-25`. | **RULED.** |
| **§3 ITEM 1 — disposition** | `PB-11` **re-aimed at the monitor**; `PB-02` amended with params-vs-context. Zero slots spent. | **RULED.** |
| **§4 RETIREMENT** | **none.** `PB-17` survives; the cap never bound because nothing was promoted. | **RULED.** Consistent with the prior ruling's §5. |
| **§5 checks** | `C10`–`C13` named, with homes. Authorship is not mine. | **NAMED, NOT WRITTEN.** |
| **§6 ITEM 2 — owner** | `owners.tsv` gains `lane_e`; the OI-134 disagreement was **already dissolved** by `c5513a5c`. | **RULED**, with the premise corrected. |
| **§7 ITEM 2 — schema** | `owners.tsv` is a **routing registry**, not a lane-definition document. Rules (i)/(ii) do **not** go in it. | **RULED**, and this is the schema call the dispatch delegated. |
| **§8** | four places the dispatch's evidence was wrong or has gone stale | **CORRECTIONS.** |

---

## 1. WHAT I VERIFIED MYSELF, AND WHAT I COULD NOT

Verified in the tree at `HEAD`:

- **`tasks` is a task-ID SPEC, not a count.** `slurm_array_status.py:49-64`: `expand_spec` splits on
  `,`, expands `a-b` ranges, and otherwise appends `int(part)`. So `expand_spec("1") == [1]`. **TRUE.**
- **The routing to `monitor-error` is as described.** `wakerctl.py:434-447` — the `slurm-array` branch
  builds a snapshot over `expand_spec(params["tasks"])`, and `if snapshot.get("observer_errors") or
  snapshot.get("unknown_tasks"): return unreliable_step()`. `unreliable_step` (`:412-417`) increments
  and emits `monitor-error` at `max_unreliable`, whose default is `10` (`:410`). A watch on a
  nonexistent task therefore **cannot** reach `slurm-array-complete` or `slurm-array-error` in either
  direction. **TRUE.**
- **THE DISPATCH'S STRONGEST ARGUMENT IS TRUE, AND I CHECKED IT BEFORE RELYING ON IT.**
  `wakerctl.py:1076` — `def preflight(ctx, quiet=False, control_plane=False)`, and the new checks are
  behind `if control_plane:` at `:1105-1107`. There are exactly three call sites
  (`grep -n "preflight(" docs/orchestration/wakerctl.py`): the definition; `:1250` inside
  `dispatch_one`, which passes no `control_plane` and so gets the default **OFF**; and `:1873`, the CLI
  subcommand. **So the only caller that enables the `a0a31176` checks is a human typing
  `wakerctl preflight`.** The docstring says so in its own words and gives the reason — a dispatch must
  not fail closed on `squeue` reachability. I agree with that design and am not asking for it to change.

  **One correction to the dispatch's phrasing:** on the CLI the control-plane checks are ON by
  **default** — `control_plane=not args.env_only` (`:1873`), with `--env-only` as the opt-out
  (`:1808-1812`). There is no `--control-plane` flag; `OI-134`'s prescribed
  `wakerctl preflight --control-plane` would not parse. That is a records defect in someone else's
  file, so it is recorded here and not edited.

**NOT verified, and I say so rather than confirming the framing.** Everything cluster-side — the watch's
stored `params`, `last-tick.json`'s stamps, scron `56585597`'s held state, "42 held rows / 28 distinct
users", and the live `overall=UNOBSERVED, unknown_tasks=[1]` measurement — lives under
`state/waker/`, which is **not in this checkout** (`find` for `last-tick.json` returns nothing), and I am
forbidden the cluster this turn. I accept those as **CITED**, on lane B's transcript-derived fixtures
(`a0a31176` states its healthy negative is spec `0-0` against the **same** array) and on `ISSUE-52`. They
are not independently verified by me, and my ruling does not depend on them: the *code* facts above are
sufficient, because they establish the defect class regardless of which watch instance carried it.

**One sub-claim I could not verify and would flag against the framing:** the dispatch asserts the
disarmed predecessor `gate5-do-train-57266000` "carried the identical defect". `72af9374`'s diff contains
no `--tasks` value, and `HANDOFF-20260819-...-57266000.md:31` records the array's spec as **`0-0`, ONE
member** — so the repo's own handoff and the watch's alleged `params` disagree. `OI-134` asserts the
predecessor carried `tasks:"1"` too, measured live. **Only that live read supports it**, and I could not
repeat it. It matters only for blame allocation, which is not what I am ruling on.

## 2. ITEM 1 — DECLINED. The gap is a missing SCHEDULER, and prose is the weakest scheduler available

The candidate — *"before trusting any watch, read `last-tick.json`'s age and the watch's `params` — not
its `action.context` and not `state` alone"* — states a real defect and a correct diagnosis. **Its
diagnosis of `PB-11` is right and I have acted on it (§3).** What it does not earn is a slot, for four
reasons, in descending weight.

**(a) The remedy for "a detector nobody is scheduled to run" is to schedule it.** The dispatch's
strongest argument is that `a0a31176`'s checks fire only on human invocation. Granted, verified, §1.
But a prose row asking every session to remember to run a check is *strictly weaker* than the check
being wired to something that already runs. It has the same failure mode as the one it is diagnosing —
`ISSUE-52` records that `WAKER.md:52` **already stated the tick-liveness rule in prose** and the peer's
own commit message draws the conclusion: *"A rule that exists only as prose is not a control."* **The
candidate's argument for a prose row is an argument the candidate's own evidence refutes.**

**(b) There is a home that fires on the default read path with zero new discipline, and it is currently
teaching the two wrong fields.** `CLAUDE.md` orders every session to read `LIVE-STATE.md` **first**.
`generate_live_state.py:181-183` renders each watch as `` `watch_id`(kind:state) `` — **`state`, and
never `params`** — and `:192` prints `Last tick: {last_tick.at_utc}` **verbatim, with no comparison to
now**. So the cheapest orientation surface in the repo hands every session exactly the `state`-alone and
unjudged-timestamp reading the candidate wants to forbid. Fixing those two render sites (`C10`) makes
the correct reading the *only* reading available, for free, in every future session — which is more than
a 25th row could achieve, because a row can be skipped and a rendered `STALE 45h` cannot.

**(c) The general mechanism is already in two slots, and one of them I bought yesterday.** The
ticker half is `BEN-456` mode (i) — *a control that never executed* — which the peer itself filed there,
and which is the first of `PB-23`'s three detection questions (*what proves the PRIMARY path ran*). The
`params` half is `PB-02` — *read the artifact that governs the decision, not merely a related artifact*;
`action.context` is the related artifact and `params` is the governing one, which is the same axis
`c5513a5c` has since amended into `BEN-478` a second time (the unreachable `sandbox` key). **Promoting
would put a third row on a mechanism that already holds two.**

**(d) The candidate is tool-specific where the playbook is mechanism-general.** It names
`last-tick.json`, `params`, and `action.context`. Every one of the 24 active rows is a mechanism; a
`wakerctl` operating procedure's home is `WAKER.md` and `ISSUE-52`, both of which now carry it.

**And a fact from `c5513a5c`, which landed while I was writing, decides the marginal-value question.**
The prescribed remedy `scontrol release 56585597` is **structurally impossible** — Slurm answers *"Cannot
modify scrontab jobs through scontrol"*. It was prescribed by **three independent parties** (this repo's
records, the mediator's report to Joseph, an audit lane) and **tested by none**. That is `PB-07` —
*"Run a command before embedding it in an authorization or procedure"* — verbatim, already active, in a
slot, for the whole episode. **The costliest error in this incident was already covered by a prose row
and the prose row did not fire.** I decline to spend the last slot on the theory that a 25th one would.

## 3. DISPOSITION — `PB-11` re-aimed, `PB-02` widened. Zero slots, no retirement

**The candidate's best sentence is that `PB-11` aims the liveness question at JOBS and nothing aims it
at the MONITOR.** That is a defect in an existing row, and the fix for a mis-aimed row is to re-aim it,
not to add a second row beside it that a reader must know to consult.

| row | before | after |
|---|---|---|
| `PB-11` rule | *Judge **job** liveness from resource use and products, not log quietness.* | *Judge liveness from resource use and products, not quietness — **and ask it of the MONITOR as well as the job**.* |
| `PB-11` check | *Query scheduler CPU/state and count validated artifacts.* | + *For any monitor, watch, or scheduled control, additionally confirm its evaluator is **RUNNABLE in the scheduler (not merely scheduled)** and that **its own heartbeat artifact is younger than its declared interval**; **a stored status field is not a liveness claim**.* |
| `PB-11` evidence | `BEN-028` | `BEN-028, BEN-456, BEN-478` |
| `PB-02` check | …*re-read any predicate an error message or refusal cites*… | + *when a record has a **human-readable half and a half the code dereferences**, verify the half the code dereferences.* |
| `PB-02` evidence | `BEN-205, BEN-383, BEN-476` | + `BEN-478` |

*Runnable, not merely scheduled* and *heartbeat younger than its declared interval* are the two
distinctions the episode actually turned on: `read_scrontab()` confirmed the schedule and never asked
Slurm about the job the schedule creates, and `status()` returned `last_tick` unjudged. *A stored status
field is not a liveness claim* is the `state == "armed"` half. **The word "job" is deleted from the
rule**, which is the whole of the peer's objection, granted in full.

`PB-07` is **not** amended despite §2's `scontrol` instance, and the reason is a constraint, not
oversight: `control_plane_lint.py:290-295` requires every cited id to match `BEN-\d{3}` and exist in
`FINDINGS.md`, and that fact's home is `ISSUE-52`/`OI-134` with **no `BEN` id**. Citing it is
impossible without another lane filing one. Recorded here so it is reachable.

**Surface is unchanged at 24 of 25.** The prior ruling's §5 candidate — `PB-17` into `PB-16` — is
**untouched and still the named candidate**, because the cap still has not bound. Retiring a live rule
to make room for a promotion I declined would have been the exact defect that ruling's §1 corrected:
an action whose safety was checked and whose necessity was not.

## 4. WHAT WOULD CHANGE MY MIND

Stated so this decline is falsifiable. Promote a monitor-liveness row if **either** holds:
(1) `C10` is refused or fails, so no automatically-executing surface renders a judged tick age — then
prose is the best remaining instrument and the row is worth the last slot and a retirement; or
(2) a second, *independent* instance appears in which a session read `state`/`action.context` while the
governing field was wrong **after** `PB-02` and `PB-11` carried these clauses — which would be evidence
the amendments are unreadable where a row would not be.

## 5. NOT PROMOTED — BETTER SERVED BY AN EXECUTABLE CHECK

Continuing the prior ruling's numbering. **Named, with a home, and NOT written here** — my file set is
the control plane, and every home below belongs to another lane.

| # | check | home | from |
|---|---|---|---|
| C10 | **The default read path must judge, not transcribe.** In `generate_live_state.py`: at `:187-192` compare `last_tick.at_utc` against the interval parsed from the managed scrontab block and render `STALE (<age>)` rather than a bare timestamp; at `:181-183` render each **armed** watch's resolved subject (`job_id` + the **expansion** of `params.tasks`), not `kind:state` alone. **This is the highest-value item in this ruling** — it is the only remedy that fires in every session without anyone remembering it. | `docs/orchestration/generate_live_state.py` (lane B / repo-infra) | `BEN-456`, `BEN-478` |
| C11 | **Wire the `a0a31176` checks to something that runs.** Call `preflight(control_plane=True)` from the **watch-add** path (a Slurm round trip is already paid there and failing closed is safe) and from the scrontab'd tick job's wrapper (where a held ticker's successor can report on its predecessor). **Explicitly NOT `dispatch_one`** — that exclusion is correct and must be preserved. | `docs/orchestration/wakerctl.py` + the cron wrapper (lane B) | `BEN-456` |
| C12 | **A named owner must not resolve to an UNASSIGNED bucket.** In `control_plane_lint.py`, error when a work item whose `OPEN_ITEMS.md` row names a specific accountable party carries an `owner_id` whose `assignment_state` is `unassigned` — because `:265-269` then forces `queue=WAITING-JOSEPH` and prefixes *"Designate an accountable owner, then: "* onto an action that is actionable now. §6 is an instance; `OI-70`, `OI-73`, `OI-127` are three more. | `docs/orchestration/control_plane_lint.py` (lane B / D) | §6 of this ruling |
| C13 | **The two lane rules, in the receipt schema rather than in prose** (§7): a gate receipt whose `verifier` resolves to the same `owner_id` as its `builder` fails; and a gate receipt with no **pre-registered expected value, timestamped before the run's submit time**, is rendered as a **READING**, not as a gate outcome. Per lane D, the second is the load-bearing half — separation without pre-specification yields a second opinion, not a test. | the gate-receipt verifier (`verify_receipt_artifacts.py` and the gate precondition scripts) — **not** `owners.tsv` | mediator's lane rules (i), (ii) |

## 6. ITEM 2 — the owner is reconciled, and the disagreement I was sent to fix had already dissolved

**THE DISPATCH'S PREMISE IS STALE, and this is the second consecutive ruling in which that was the
deciding fact.** `c5513a5c` landed **while I was reading the evidence** (my first `git status` was clean;
my fourth showed six files mid-commit; the commit appeared between them). It **discharged `OI-134`** with
the sanctioned terminal prefix — both actions executed on Joseph's key, the ticker resubmitted
`56585597 → 57275989`, `last-tick.json` advanced to `2026-08-19T12:40:28+00:00`, and watch `r3` armed
**add-then-retire** with a correct spec — and **removed its `work-items.tsv` row**. So at `HEAD`:

```
$ grep -c OI-134 docs/orchestration/control-plane/work-items.tsv docs/CURRENT_WORK.md
docs/orchestration/control-plane/work-items.tsv:0
docs/CURRENT_WORK.md:0
```

**There is no longer a live registry row to disagree with `OI-134`'s owner field.** Retagging the row
was therefore not possible and is not what I did.

**I added the owner anyway, and the reason is not `OI-134`.** The registry defect is real and outlives
the item: `repo_infra` was chosen *because it existed*, it is `assignment_state=unassigned`, and
`control_plane_lint.py:265-269` therefore **forced** `OI-134` to `WAITING-JOSEPH` and prefixed
*"Designate an accountable owner, then: "* onto item (1), **which was actionable by lane E that hour**.
The generated queue said the campaign's only live compute needed Joseph to name an owner when it needed
lane E to type one command. That misrouting recurs for any future execution item, so:

```
lane_e	lane E (execution / freezes / submissions)	lane E	Joseph	assigned
```

`accountable_holder=lane E`, `escalation=Joseph`, `assigned` — so the next submission/freeze item routes
`NOW` to lane E instead of `WAITING-JOSEPH` to nobody. It is inserted after `cstat` so the two
lane-keyed rows sit together. **It currently has zero work items and that is intended**: an empty
registry row costs nothing and the lint does not require owners to be referenced (verified: `PASS` with
the row unused).

**One thing I did not do and want on the record.** `OI-134`'s owner field reads *"lane E (waker /
control plane); item (2) **Joseph**"* — a **split** owner, and `work-items.tsv` has one `owner_id` per
item. A split-ownership item is not expressible in this schema; the peer's `repo_infra` choice was
partly forced by that, not only by the missing id. I am **not** adding a second owner column (§7), so
the standing convention is: **split-owner items are filed under the party who acts first, with the
escalation carrying the rest.** `OI-134`'s discharge shows why that is the right side to pick — item (1)
was actionable, and filing under the waiting half hid it.

## 7. SCHEMA RULING — `owners.tsv` is a routing registry, and the lane rules do not belong in it

The dispatch delegated this to me, so it is decided here rather than deferred.

**RULED: `owners.tsv`'s `owner_id` names the accountable ROLE for a queue row. A lane id is admissible
in that namespace; a lane DEFINITION is not.** The file's five columns
(`control_plane_lint.py:47`) are `owner_id, display_name, accountable_holder, escalation,
assignment_state` — every one of them answers *"who receives this row and who is escalated to."* Nothing
in it is read by anything but the queue renderer.

Two consequences, both deliberate:

1. **Mixing lane keys with workstream keys in one namespace is accepted, not tolerated.** `pet`,
   `cstat`, `gate6`, `standard_p4` are workstreams; `joseph` is a person. The mixing already happened —
   `cstat`'s `display_name` and `accountable_holder` are both literally *"lane B"* — so `lane_e` adds a
   third key **shape** to a namespace that already has two, and the alternative (renaming `cstat` to
   `lane_b`) would rewrite a key referenced by live work items for cosmetic uniformity. **The invariant
   that matters is that `owner_id` is opaque and stable; it is not that it is uniform.**
2. **Rules (i) and (ii) are NOT encoded here, and I decline to add a column for them.** Adding one would
   require editing `OWNER_COLUMNS` in `control_plane_lint.py` — outside my file set — and backfilling
   eight rows. But the file-set constraint is not the reason; the merits are. **(i)** *the party that
   verifies a gate is never the party that built it* and **(ii)** *a gate's expected value is named
   before the run, or the run is a reading* are constraints on **how a gate is conducted**, evaluated
   per-gate against a receipt. `owners.tsv` has no gate, no run, and no receipt; a row in it could
   record an intention about lane E and could never fail. **Putting a gate protocol in a routing table
   produces a rule that cannot be violated by construction** — which is this repo's recurring defect,
   not a fix for it. Their home is `C13`: the receipt verifier, where `builder`, `verifier`, and a
   pre-run expected value are all fields that exist and can be compared. **Lane D's judgment that (ii)
   is the load-bearing half is adopted**, and `C13` states it as the half that changes the receipt's
   *rendering* — a run without a pre-registered expectation is labelled a READING — because a rule that
   downgrades an artifact is enforced, and a rule that asks for a habit is not.

## 8. WHERE THE DISPATCH'S EVIDENCE WAS WRONG

1. **`wakerctl preflight --control-plane` does not exist** (§1). The CLI has `--env-only`, and
   control-plane checks are ON by default there. `OI-134`'s prescribed command would fail to parse.
   Not my file; recorded, not edited.
2. **`OI-134` was discharged mid-turn** (§6), so the reconciliation as framed was unperformable. `c5513a5c`.
3. **`scontrol release 56585597` is structurally impossible**, not merely unauthorised — and the dispatch
   relayed it as pending authorisation. Three parties prescribed it untested (`c5513a5c`). This is
   `PB-07`, and §2 uses it as the argument *against* the promotion the dispatch favoured.
4. **The predecessor-watch claim is CITED, not verified** (§1): `HANDOFF-…-57266000.md:31` records the
   array spec as `0-0`, and only a live read supports `tasks:"1"` on the disarmed predecessor. I could
   not repeat it and did not need to.

Also: the dispatch said the surface "is now 24/25 — so the NEXT promotion is genuinely AT the cap." That
is right, and it is still true after this ruling, because **declining is what keeps it true.**

## 9. WHAT WAS CHECKED

```
BEFORE (HEAD = c5513a5c, tree clean but for an untracked log_test.txt)
$ python3 docs/orchestration/control_plane_lint.py --self-test
control-plane self-test: PASS                                    # rc=0
$ python3 docs/orchestration/control_plane_lint.py
CONTROL-PLANE PASS: 15 selected; 0 overflow; 61 backlog; 97 source records; 24 playbook rules   # rc=0
   (the 15 -> 14 shift below is c5513a5c's OI-134 discharge landing mid-turn, not this change)

AFTER edits, BEFORE regeneration
$ python3 docs/orchestration/control_plane_lint.py
CONTROL-PLANE FAIL: generated output stale: docs/orchestration/PLAYBOOK.md; run --write   # rc=1

AFTER
$ python3 docs/orchestration/control_plane_lint.py --write
CONTROL-PLANE WROTE: 14 selected; 0 overflow; 61 backlog; 97 source records; 24 playbook rules  # rc=0
$ python3 docs/orchestration/control_plane_lint.py
CONTROL-PLANE PASS: 14 selected; 0 overflow; 61 backlog; 97 source records; 24 playbook rules   # rc=0
$ python3 docs/orchestration/control_plane_lint.py --self-test
control-plane self-test: PASS                                    # rc=0
```

Every status above was read **unpiped**, with `echo $?` on its own line — `PB-10`, and the hazard the
dispatch warned about. `PLAYBOOK.md` was regenerated by its documented generator and never hand-edited;
its diff touches exactly the `PB-02` and `PB-11` rows. **`git status` was re-read immediately before
`--write`** and showed only my two TSVs dirty, so the regeneration swept nothing of another lane's —
which mattered, because the tree was mid-commit by a peer minutes earlier. `generate_manifest.py --check`
was not run to green: its staleness is pre-existing and owned elsewhere.

**Playbook rule count is 24 before and 24 after.** Nothing was promoted, nothing retired, nothing
deleted; two rows carry more evidence and one carries a wider subject.
