# BEN-244 — A decision that reached its own record and nowhere else, and the citation that outlived it

**Filed 2026-08-14 by lane B, at the mediator's request, against a question the mediator raised.**
Read-only documentary work; no job, no artifact, nothing on the cluster touched.

**One line.** Gate 4's estimator-arm disposition was **decided 2026-08-13** and the artifact was
**promoted the same hour**, each with its own committed record — and **twelve live references written
AFTER both acts still call it an unmade user decision, four of them mine.** `BEN-201` was a retraction
that reached the index but not the point of use. This is the same shape on a **decision**, and it was
load-bearing: two lanes and the mediator each independently reported it as *the* remaining Gate-6
blocker, and none of us opened the authorization record.

---

## 1. Both acts happened, and each has a committed record

| act | when (UTC) | record | authority |
|---|---|---|---|
| **arm selected** — the annealed arm | 2026-08-13 | `AUTHORIZATION-20260813-gate4-estimator-disposition.md:12` | **Joseph, verbatim: *"Okay do the annealed"*** |
| launch authorization | 2026-08-13 | same file, `:251-256` | Joseph, verbatim: *"Launch it"* — correctly **not acted on**, because nothing was launchable (`:258-284`) |
| **promoted to canonical** | **02:53** | `state/p3f-pet-gate4-nominal-promotion-56563761.json`, `verdict: PROMOTED`, `promoted_at_utc 2026-08-13T02:52:32Z`, commit `6b68d12` | **the mediator**, under Joseph's delegated go — *"if all you need is a go command, feel free to authorize it yourself"* (`:16`) |
| `artifact_promoted` flipped | 02:50 | `state/annealed-nominal-complete-56563761.json:144`, commit `156d1d6` | same delegation (`:216-222`) |

**Both promotion records refuse the credit they could have taken.** `p3f-…-promotion:17` and
`annealed-nominal-complete:220` each carry a `DO_NOT_RECORD_AS` field reading *"Joseph authorized the
promotion. He did NOT… Two acts, two parties."* That distinction is the reason this finding can be
written precisely instead of argued.

---

## 2. The twelve references, each measured with `git blame`, each written AFTER 02:53 UTC

Sorted by authorship time. **Not one is dated or superseded text** — every one was live when written
and is live now.

| # | reference | authored (UTC) | author | says |
|---|---|---|---|---|
| 1 | `PREDECLARATION-20260813-gate6-member-trajectories.md:52-54` | 08:39 | `3c5c307` | *"does not move the **promoted** nominal central. Gate 4's estimator-arm disposition remains an independent user decision"* |
| 2 | `VALIDATION_LEDGER.md:70` | 09:44 | `19585b7` | *"remains an independent user decision"* |
| 3 | `nd-unfolding/ND_OMNIFOLD_STATUS.md:37` | 09:44 | `19585b7` | same sentence |
| 4 | `state/gate6-member-trajectories-result-56847059.json:119` | 09:44 | `19585b7` | `gate4_user_disposition_remains_independent: true` |
| 5 | `state/live-state.json:56` → `LIVE-STATE.md:53` | 10:48 | `9c6fd3a` | *"remains an independent user decision"* |
| 6 | `PLAN-20260813-gate6-cml-retry-design.md:255` | 12:54 | **lane B** | *"an independent user decision that **blocks construction**"* |
| 7 | `ND_OMNIFOLD_RUN_LOG.md:5913` | 12:54 | **lane B** | *"remains an independent user decision and **blocks `C_ML` construction**"* |
| 8 | `PREDECLARATION-20260813-gate6-floor-replication.md:14` | 13:21 | **lane B** | *"remains an independent user decision that blocks construction"* |
| 9 | `ND_OMNIFOLD_RUN_LOG.md:6124` | 22:09 | **lane B** | *"blocks construction independently regardless"* |
| 10 | `PREDECLARATION-20260813-gate6-legX-2x2.md:15` | 22:25 | **lane B** | same |
| 11 | `state/gate6-floor-replication-active-56863958.json:158` | 08-14 | **lane B** | `gate4_user_disposition_remains_independent: true` |
| 12 | `docs/OPEN_ITEMS.md:78` (OI-23) | 08-13 | — | *"contingent only on `56563761` REMAINING the final nominal, which is Joseph's promotion decision (`artifact_promoted: False`)"* — **quotes the superseded field value** |

**Row 1 is the sharpest.** It says *"the **promoted** nominal central"* and *"remains an independent
user decision"* **one clause apart**. Its author knew about the promotion in the sentence where it
denied it. Nothing was misunderstood; the two facts were held simultaneously and never compared.

**Lane B authored five of the twelve** (6–10, plus 11). Two of them, 8 and 10, are inside frozen
`PREDECLARATION-*` documents whose runs have since completed, so **they cannot be edited** — the
correction has to live here and in the RUN_LOG, which is why this file exists rather than a patch.

**One document got it right, 55 minutes after the promotion and before any of the twelve:**
`HANDOFF-20260813-0600Z-gate5-replica-driver.md:97` (05:58 UTC, lane A) reads *"**annealed**,
recorded; artifact `56563761` **promoted** at `6b68d12`"*. **So the resolution did reach a point of
use.** It reached exactly one, and it was the one nobody's read path names.

---

## 3. The claim also drifted while it propagated, and the drift is the part that did damage

The **only** machine-readable statement anywhere is
`gate6-member-trajectories-result-56847059.json:119` —
`gate4_user_disposition_remains_independent: true`. Measured: that receipt mentions Gate 4 **exactly
once**, and this is it (`grep -c` = 1).

That field asserts **scope independence**: *this Gate-6 result does not resolve Gate 4, and Gate 4
does not change this result.* It says nothing about blocking. Lane B's citations 6–10 render it as
*"an independent user decision that **blocks** construction"*, and `PLAN:257` names the receipt field
as the source for that sentence. **`independent` became `blocking` in transit, and the receipt it
cites does not contain the stronger word.** A stale fact is recoverable by re-reading the source; a
fact that got *stronger* on the way to its citation is not, because re-reading the source no longer
looks like a contradiction.

---

## 4. What the citation was standing in front of

Working forward from the contract rather than backward from the citation:

- `PUBLICATION_COMPLETION_RUNBOOK.md:223-224` — *"`C_ML`: no Poisson variation. Use a predeclared
  crossed seed design and compare with the P5A floor."* No user decision named.
- `RUNBOOK:213-214` — *"Every component uses the P5A central/mask/order."* **This is the real link to
  Gate 4**, and it is discharged: the central is decided.
- `nd-unfolding/pet/combine_cml_bkgsub.py:75,81-82` — the builder reads
  `--cv products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz` and takes its mask from `cv > 0`. So the
  dependency on the nominal is **the mask and the reference**, an *extraction product*, not an
  authorization. `annealed-nominal-complete-56563761.json:142` records `extraction_run: false`, and
  extraction is on the promotion receipt's `NOT_authorized` list (`:81`).
- `combine_cml_bkgsub.py:84-86` — a member-count mismatch is a **`WARN`, not a `FAIL`**: it builds
  from whatever it finds and prints *"NOT final until complete"*. **The code would build `C_ML` from
  the one passing member.** `do_not_select_passing_subset` is enforced on people, not by the builder
  (the `BEN-023` / `ISSUE-46` arm-A class).
- The live blocker is `state/gate6-member-trajectories-result-56847059.json:109-118`:
  `family_verdict BLOCK_GATE6_ML_ENSEMBLE`, `passing_members [1]`, `failing_members [2,3,4,5]`, five
  prohibitions applied. **A measurement failure, not a user decision** — and clearing it needs
  `do_not_retry_unchanged` satisfied, which is what the retry PLAN exists to propose and what Joseph
  has not authorized.

**So the answer is not "there is no blocker."** It is that the blocker is `BLOCK_GATE6_ML_ENSEMBLE`
plus two missing inputs, and the Gate-4 citation was standing in front of all three wearing the
wrong name.

---

## 5. And the guard that was supposed to make the promotion safe has been red ever since

`nd-unfolding/pet/check_canonical_designation.py` is a **fail-closed postcondition for exactly this
designation**. Its own docstring (`:2-10`): *"The safety of that choice rests entirely on the
reference inventory being COMPLETE."*

**Run at `849b70f`: exit 1.** 59 files, 184 occurrences, 54 inventory entries, and:

```
UNACCOUNTED  docs/orchestration/state/p3f-pet-gate4-nominal-promotion-56563761.json:67
UNACCOUNTED  docs/orchestration/AUTHORIZATION-20260813-gate4-estimator-disposition.md:271
COUNT DRIFT  state/annealed-nominal-complete-56563761.json [RECORD-FROZEN]: expected 1, found 2 (lines 63, 226)
+ 5 more unaccounted files, 2 stale inventory entries
```

**The two records of the promotion are themselves among the occurrences the guard cannot account
for,** and the `COUNT DRIFT` is line 226 — the `baseline_untouched` prose the supersession added. The
acts that needed the guard are what broke it.

`VERDICTS-20260811-session-D.md:452` records this same script at **`exit=0, PASS`** on 2026-08-11. So
it passed, then went red at the designation, and **nothing has run it since** — it is absent from
`.githooks/pre-commit`'s check list *and* from its declined list. That dispatcher's own comment at
`:25-27` describes this exact failure: *"`verify_hash_bindings.py` was in neither list, so a Gate-4
code binding stayed broken ~18 h across four lanes' commits, every one of which printed 'pre-commit:
N checks passed'. If you decline a check, say so HERE — an unlisted check is not a decision."*
**Second instance, in the same gate's namespace, of the defect that comment was written to prevent.**

**And zero references are dispositioned `RETARGET`.** The token appears exactly once in the file, in
the legend defining it (`:98`). Every one of the 54 entries is `STAYS-*` or `RECORD-*`, and `:127-131`
says of the extraction launchers: *"pinned to the already-quarantined 08-08 artifact and **must not
acquire a newly-canonical one by default**."* So **the promotion is documentary in the strong sense —
no consumer in the tree follows it**, which both receipts state (`p3f-…-promotion:65`,
`annealed-nominal-complete:225`) and which is easy to under-read as bookkeeping pedantry rather than
as the reason "canonical" does not yet reach any `--cv`.

---

## 6. What is genuinely still open, named narrowly

Not the disposition. Three things, and none is *"Gate 4's estimator-arm disposition."*

1. **Quotability of the recovery number the disposition was argued on.** `VL100 = 0.512603276` comes
   from closure `56552326`, whose every artifact is prefixed `NONQUOTABLE-DIAGNOSTIC.` with
   `quotable: False` (`AUTHORIZATION…:492-494`). The promotion receipt declines to discharge it
   (`:95`), and the authorization record assigns it to the PET lane (`:498-500`). **It is tracked
   under no `OI-*` id** — measured: `grep quotable docs/OPEN_ITEMS.md` returns only `OI-40` and
   `OI-46`, neither of which is this.
2. **`recovery_evaluated: false` at the promoted configuration** (`annealed-nominal-complete:141`),
   deliberately left false.
3. **`VL101`'s baseline `0.546853` is not established as uninflated** —
   `VALIDATION_LEDGER.md:1811` says so in the same annotation that marks the row adjudicated, and
   `AUTHORIZATION…:452-454` states it as an open dependency.

**Two bookkeeping defects, worth naming because each reads as a live block:**
`annealed-nominal-complete-56563761.json:152-156` still carries
`next_dependency.state: BLOCKED_ON_USER` — untouched by the supersession that flipped
`artifact_promoted` 8 lines above it — and its `declaration` pointer
`state/waker/BLOCKED-ON-USER.json` **does not exist** (untracked at `a45f17b`). A receipt that
declares itself promoted and blocked-on-user in the same object, pointing at a file that is gone.

---

## 7. The lesson, and why it is not just `BEN-201` again

`BEN-201`: a **retraction** reached the index and not the point of use. Here a **decision** reached
its own authorization record, its own promotion receipt, and one handoff table — and twelve live
references written afterwards still describe it as unmade.

**The asymmetry that makes this worse than BEN-201.** A stale *retraction* leaves a claim standing
that is too strong, and someone eventually tries to use it and fails. A stale *blocker* leaves work
stopped, which produces **no error and no symptom** — the campaign simply does not advance, and every
reader who checks the citation finds eleven documents agreeing with it. **Consensus among citations of
a single source is not corroboration**, and here all eleven trace to one receipt field that does not
say what they say.

**The check.** A decision's record is the *last* place its consequences appear, not the first. So:
**when you cite a blocker you did not decide, open the record that would have closed it, and cite that
record's absence or its content by `file:line`.** Cost, measured this turn: one `ls`, one `git log`.
Against it: three sessions, two lanes, and one mediator all reporting a closed decision as the
campaign's remaining blocker for 36 hours.

**And a corollary I am the evidence for.** `BEN-241` is *an absence claim needs a stated search that
would have found the thing*; `BEN-243` is *a disagreement is closed by the decider*. This is the third
in the family and the same operation on a third object: **I asserted a decision's state from
downstream text rather than from the decision's own record**, in five documents, two of them frozen.
The instrument that catches all three is identical — go to the canonical home named in `CLAUDE.md`'s
routing table and read it — and I did not use it on any of the three.

---

## 8. Corrections owed, with owners, so this does not become the thing it describes

Lane B corrects rows 6, 7, 9 and 11 (`PLAN:255` in place; `RUN_LOG` by append, it is append-only) and
**cannot** correct 8 and 10 — frozen predeclarations of completed runs, where a post-hoc edit would
destroy the property that makes them worth having. Those two are recorded here instead.

Rows 1–5 and 12 belong to other authors: `VALIDATION_LEDGER.md:70`, `ND_OMNIFOLD_STATUS.md:37` and
`state/gate6-member-trajectories-result-56847059.json:119` (`19585b7`); `state/live-state.json:56`
(regenerate, do not hand-edit); `PREDECLARATION-…-member-trajectories.md:52` (frozen, same
constraint as 8 and 10); `OPEN_ITEMS.md:78` / `OI-23`, whose residual **is now dischargeable** and
whose row still quotes `artifact_promoted: False`.

`PET_UQ_REMEDIATION_STATUS.md` needs a Gate-4 paragraph and does not need a correction: `:139-141`
already says the disposition *"is answered (the **annealed** arm)"*, and `:334-342` is explicitly
headed **"2026-08-10 one-liner"** — dated text, correctly dated, in a reverse-chronological section.
What is missing is any 2026-08-13 line at all in the Gate-4 section, so a `*_STATUS.md` whose
canonical role is *"current state per workstream"* has a three-day-old newest Gate-4 sentence reading
*"Gate 4 remains blocked."* **That is `BEN-098`'s shape, in a file that documents `BEN-098` about
itself 200 lines earlier** (`:156-161`). The `:143-154` correction block is a separate matter: written
**02:01 UTC, 52 minutes before the promotion**, it quotes `artifact_promoted: False` and
`.status COMPLETE_PREDECLARED_FINDING_CODE_PATHS_DISAGREE_NO_DOWNSTREAM` and closes *"That is with
Joseph."* It was true when written and was falsified within the hour. Both belong to the PET lane.
