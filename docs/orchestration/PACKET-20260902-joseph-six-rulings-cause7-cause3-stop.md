# DECISION PACKET 2026-09-02 (rev. 3) — six rulings reserved for Joseph: cause 7's subject and
# magnitude, cause 3's seed scan, the campaign stop rule, and PET's posture

**STATUS: RECOMMENDATION ONLY. UNSIGNED. Nothing below is a ruling until Joseph rules it.**

**CITABLE FOR:** the six recommendations `R1`–`R6`, their branch sets in §0, and the routing table in
§7, as **this lane's recommendations**. **NOT CITABLE FOR:** any authorization. Not a discharge, a
grade, an adoption, a gate movement, a launch, a pin move, a scheduler write, a count change, a
spending grant, or a publication claim. **Gate 2 remains FAIL. Counts hold at CAND `1 of 7`, QUOTED
`0 of 7`. No scalar-5D covariance is adopted. PET `C_stat` remains `EXISTS — UNVERIFIED, PAIRING
DECLINED`** (`VALIDATION_LEDGER.md` `VL132`) — its existence, digest and ledger row supply neither the
independent check nor the central pairing. The five Gate-6 prohibitions are reproduced in `R6` as keys
and must not be paraphrased.

**This lane computed nothing and implemented nothing.** Every figure is read from a committed artifact
named beside it. Three operational figures come from `HANDOFF-20260902-operational-baseline-snapshot.md`,
which is **untracked and therefore routing only, not live evidence**; each is labelled where used.

**REVISION 2, 2026-09-02 — seven corrections from an independent audit of rev. 1, all adopted.**
Rev. 1 is superseded in full and must not be quoted. What changed, so no reader carries a rev-1
sentence forward: (i) `R1` no longer leans on `DECISION-20260831` §2(b)'s *"unsatisfiable in
principle"* analogy, which `OI-188(d)` records as argued on stamps alone while `CRITERIA` §0 gives `P`
three routes — *"by stamp, receipt **or hash**"*; (ii) `R2` now creates a **separate** `(cause 7, Y)`
record instead of moving G's, and states that it prospectively **amends** the 2026-08-31 ruling for
cause 7 only; (iii) `R3` no longer creates a note obligation and no longer grades `M` on delivery;
(iv) `R4`'s branch arithmetic was **wrong** — see the correction in `R4`; (v) `R5` now states that it
**is** the later exception `OI-187` half (b) reserved, and that a ceiling is not a spending grant;
(vi) `R6`'s *"verifying `C_stat`"* is corrected to *"independently verifying the existing
construction"*; (vii) §0 and §7 add exhaustive branches and an owning record with a fallback state for
each ruling, because *"sign or reject"* is not an operational branch set.

**REVISION 3, 2026-09-02 — five narrow corrections from a second audit, all adopted.** Rev. 2's six
rulings are substantively unchanged; what was wrong was the §0 branch table contradicting the rulings
it summarises, and §7's placeholder routing. (i) `R5`(b) said *"stop now, submit as scoped"*, which
contradicted `R5`'s own statement that submission remains a separate decision — it now reads *stop now
and select the scoped Letter; submission remains separately authorized*. (ii) `R2`(b) and §7 called
cause 7 *"ungradable"* without a successor, which is **false** — G remains the historical grading
subject; both now say no successor `Y`, with `(cause 7, G)` in the state `R1` or its fallback selects.
(iii) `R2`(c) now carries the same four guards as (a): separate cell, cause 7 only, specification only,
no cross-artifact aggregation. (iv) `R1`'s fallback said lanes *"may keep spending on it"*, which read
as a resource grant; it now reads *work remains open; no new compute or resource authority follows*.
(v) §7's `DECISION-2026xxxx` placeholders are replaced by records that exist today, and §8's *"two
blanks"* is corrected to **three**, matching §9.

---

## §0. How to rule — the branches, and what happens to each if you rule nothing

**An unsigned packet is not a null state.** Each row's fallback is what remains true if you never rule
it, and in every case the fallback is the status quo, which is why nothing here is urgent in the sense
of degrading.

| | branches | fallback if unruled |
|---|---|---|
| `R1` | **(a)** grade `(cause 7, G)` permanently OPEN · **(b)** leave it OPEN-pending-work · **(c)** reject and require a different cause-7 route on G's bytes | **(b)** — **work remains open; no new compute or resource authority follows** |
| `R2` | **(a)** authorize one successor `Y` — separate cell, cause 7 only, **specification only**, no cross-artifact aggregation · **(b)** authorize none · **(c)** authorize a different successor by name, **under the same four guards as (a)** | **(b)** — no successor `Y`; `(cause 7, G)` remains in the state `R1` or its fallback selects, and **G stays the historical grading subject** |
| `R3` | **(a)** `M` carries no smallness requirement · **(b)** set a numerical threshold yourself · **(c)** leave the threshold open | **(c)** — `M` stays OPEN *regardless of any measured value*, per the predeclaration's own terminal sentence |
| `R4` | **(a)** retain the 2026-09-01 authorization · **(b)** suspend it pending a Joseph-signed VOI note **and** a separate committed reauthorization · **(c)** withdraw it outright | **(a)** — the authorization stands and the scan may be submitted at any time |
| `R5` | **(a)** no stop; continue open-ended · **(b)** stop now and select the scoped Letter — **submission remains separately authorized** · **(c)** a future stop with **every** field in §8 filled | **(a)** — open-ended continuation, which is the current state |
| `R6` | **(a)** reaffirm · **(b)** decline to reaffirm | **(b)**, and it changes nothing: `OI-126`'s ruling stands on its own authority either way |

**Why one packet rather than six rows.** Five of the six questions are already reserved for you in
writing by the documents that raised them, and they interact: `R1`/`R2` fix the subject that `R3`
grades, and `R4` and `R5` draw on the same finite budget.

---

## R1 — grade `(cause 7, G)` permanently OPEN, on the direct byte evidence, and RETAIN G

> **RECOMMENDED RULING.** Cause 7 can never be discharged for **G** —
> `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root`, sha256
> `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`, 10,694 reported
> bins. `(cause 7, G)` is graded **permanently OPEN** and kept as an immutable historical cell.
> **G is RETAINED**: not deleted, not moved, not overwritten. It remains causes 1–6's grading subject
> and `R2`'s required digest-bound parent and comparison baseline.

**Basis — cause-7-specific and direct, not an analogy.** The chain is three committed readings, each
about G's own bytes:

1. The cause-7 defect **is on G's path**: G's committed readback names
   `uq_universe_5d_covariance_combined_bkgaware.root` as its `combined_source`
   (`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-34`), and the adopter leaves the
   detector/lateral bands already inside that source untouched
   (`nd-unfolding/adopt_unified_5d.py:17-20`). G therefore carries the support-limited lateral block.
2. The correction is a **different operation on different inputs** — remove five named support-limited
   bands, add five selection-complete active-universe MAT blocks
   (`nd-unfolding/p4_build_components.py:11-18`). It produced S, not G.
3. Therefore correcting cause 7 **changes G's content**, and G is identified by an immutable digest.
   *"No future receipt can make the existing G bytes have been produced by a path they did not
   traverse"* (`PREDECLARE-20260901-cause7-discharge-criteria.md` §0).

Discharge would require the corrected construction; the corrected construction is not G. That is the
whole argument and it needs no other.

**EXPLICITLY NOT RELIED ON, and this is a correction to rev. 1.** `DECISION-20260831` §2(b)'s
*"Against X the provenance leg is unsatisfiable IN PRINCIPLE"* is **not** cited as precedent here.
`OI-188(d)` records that its headline argues **stamps only**, while `CRITERIA` §0 (`:49`) gives `P`
three routes — *"by stamp, receipt **or hash**"* — and its one clause reaching past stamps (*"a re-run
yields a different artifact"*) is **unmeasured**; `OI-188(b)` further records that §2(b)'s stated
36.5-hour mechanism is refuted by `VALIDATION_LEDGER.md:484` (`VL40`). Rev. 1 borrowed that framing.
It is withdrawn. `R1` stands or falls on the three readings above.

**AUTHORIZES:** recording `(cause 7, G)` as permanently OPEN, so no lane spends further effort
attempting that discharge on G's bytes.

**LEAVES UNCHANGED:** `DECISION-20260831` §1 in full — the seven causes are graded against the stamped
candidate, X is retained, and X's only authorized disposition is demotion **after** adoption. **No
count moves**: cause 7 was already OPEN for G, and `permanently` narrows the reason, not the tally.
Gate 2, `values.tex` and the adoption case untouched. F's discharge stays FPS-only (266 ≠ 10,694;
`OI-5`, `VL68`); J cannot supply a leg for G; S is not G and its validation proves nothing about G's
bytes.

**SUPERSEDES:** nothing.

---

## R2 — authorize EXACTLY ONE successor Y as a SEPARATE record, cause 7 only, SPECIFICATION only

> **RECOMMENDED RULING.**
> **(i)** **Exactly one** cause-7-only successor **Y**, carrying G's full sha256 as
> `parent_candidate`, may be named as a grading subject **for cause 7 and no other cause**.
> **(ii)** `(cause 7, Y)` is a **new and distinct** grade cell. **G's cell is never overwritten,
> reused, or retired** — `R1`'s permanently-OPEN `(cause 7, G)` stands beside it as the historical
> record, per `CRITERIA` §0: *"discharge is a property of a (cause × artifact) pair, never of a cause
> alone… the same cause can be discharged for one product and open for another."*
> **(iii)** **A cause-7 grade on Y may never be combined with G's causes 1–6 grades**, nor rolled into
> the CAND/QUOTED counts, Gate 2, or any adoption case for G. A mixed-artifact tally is exactly the
> flat *"1 of 7 done"* reading `CRITERIA` §0 warns against.
> **(iv)** This authorizes **specification only**. Constructing Y is a separate act requiring its own
> committed authorization.

**AUTHORIZES:** naming Y, and drafting its producing path, receipt schema and test contract to the
`C`/`P`/`T` criteria in `PREDECLARE-20260901-cause7` §1 — the closure identity
`C_Y = C_G − L_support + L_active`, the exact five-band inventories, the bit-identity of every
non-lateral block against G, and the two-direction power test.

**AUTHORIZES NO CONSTRUCTION AND NO COMPUTE, and rev. 1's question about this is withdrawn rather than
re-asked.** `PREDECLARE-20260901-cause7` §2 records that *"the exact Y output path, receipt
schema/version, and producing revision do not exist in this draft."* An authorization to build must
name path, schema, producing revision, cost and action; none of those objects exists, so there is
nothing for you to authorize the construction **of**. It returns as its own pre-execution declaration
when they do.

**LEAVES UNCHANGED:** causes 1–6 continue to be graded against **G itself**. Y does not exist, is not
adopted, is not a covariance candidate, and its eventual cause-7 grade carries no implication for any
other cause or artifact. A receipt about S proves S; a receipt about F proves F; neither is `P` for Y.
Counts, Gate 2 and `values.tex` unchanged.

**SUPERSEDES — and this is a correction to rev. 1, which wrongly claimed it superseded nothing.**
`R2` **prospectively amends** `DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md`
§1's *"the seven quarantine causes are graded against `stamped_bkgaware_meancentered_20260812.root`"*
**for cause 7 only**. After `R2`, that sentence reads seven-minus-one: six causes against G, cause 7
against G (permanently OPEN, `R1`) **and** against Y (a new open cell). Every other clause of the
2026-08-31 ruling — X retained, demotion only after adoption, the ordering — is untouched.

---

## R3 — SELECT the no-smallness criterion for cause 7's `M`. Nothing else.

> **RECOMMENDED RULING.** Cause 7's `M` leg carries **no materiality threshold**: a large measured
> difference satisfies the criterion exactly as a small one does. This ruling **selects a criterion
> and does nothing more.**

**The measured set the criterion is read against is the predeclaration's own, unchanged:**
`delta_full`, `delta_lateral`, the reported-bin ratio `sqrt(diag(C_Y))/sqrt(diag(C_G))` as a
**distribution** (min, p05, median, p95, max, with zero/invalid counts), `||C_Y − C_G||_F / ||C_G||_F`,
the largest absolute correlation-matrix change, and every operand.

**Basis.** No pre-observation rule connects any value of those quantities to cause-7 discharge. The
standard-P4 validator records the active/support trace ratio and explicitly labels it **diagnostic and
unbounded** (`p4_validate_active_lateral.py:240-248`; receipt key
`support_ratio_is_diagnostic_not_bounded`), and `CRITERIA` §0 holds that size neither repairs nor
excuses a construction defect. Choosing a boundary now, with the standard-P4 comparison already
visible, would be a threshold placed to obtain today's preferred verdict rather than a criterion.

**TWO THINGS REV. 1 BUNDLED IN, BOTH REMOVED:**

- **No note obligation.** Rev. 1 required the result to be *"stated in the note."* That appears
  nowhere in `PREDECLARE-20260901-cause7` §1 `M`, and it would have created a publication obligation
  inside a criterion selection. **Note wording is a separate editorial and publication decision** and
  is not before you here.
- **No automatic grade on delivery.** Rev. 1 made `M` MET when a receipt was delivered. **A receipt is
  evidence, not a grade.** Grading `M` remains a separate act on a delivered receipt, by a lane
  eligible to perform it — `BEN-381` disqualifies any lane that measured the leg from grading it.

**LEAVES UNCHANGED:** `C`, `P` and `T` remain OPEN and independent; `CRITERIA` §0's rule that **all
four legs must hold** stands unamended. **This does not reopen `OI-172`**:
`DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` RULING 1 found cause 1's magnitude *material
enough to need its own statement in the note* and therefore did **not** close cause 1. `R3` decides a
different cause's criterion where no principled cutoff exists at all, and neither weakens nor extends
that finding.

**SUPERSEDES:** nothing. It exercises the explicit either/or `PREDECLARE-20260901-cause7` §1 `M` and
§2 reserved for you — *"rule explicitly that M is measurement-only under §0 and carries no smallness
requirement."*

---

## R4 — decide the cause-3 seed scan's authorization explicitly. Recommended: SUSPEND.

> **RECOMMENDED RULING (branch b).** The 2026-09-01 *"relaunch it"* authorization is **SUSPENDED**.
> The scan may be submitted only after **both**: a value-of-information note signed by Joseph, and a
> **separate committed reauthorization** naming the run. **A VOI signature does not by itself revive
> compute authority.** Branches (a) retain and (c) withdraw are equally available; see §0.

**REV. 1 GOT THE FACTS WRONG HERE AND THE CORRECTION MATTERS.** Rev. 1 wrote that §4 has *"four
unfavourable branches"* and that the scan *"changes no decision."* Both are false.
`PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` §4 has **six exhaustive branches**: two
INCONCLUSIVE (wrong footing; vacuous seed variation), **one MET**, and **three NOT MET** (aggregate,
per-bin, both). **The scan therefore does change a named decision — it grades cause 3's `M(ii)` for
this candidate** — and any argument premised on it changing nothing is withdrawn.

**What survives, stated at its true strength.** The scan grades **one leg of one cause for one
artifact**. Its own §5 records that it cannot discharge cause 3, close another cause, change a count,
adopt a covariance, move a gate, touch `values.tex`, or add `C_seed` to the budget; and §5 flags the
full two-baseline composite scan as a **separate** and much larger question —
`INDEX-retracted-and-superseded-values.md:78` prices one additional estimator seed across all four
blocks at **`39.223` A100-h PLUS `55.337` CPU task-hours**, two units, the second larger, against a
`24` A100-h grant that does not reach the second at all. So the honest VOI question is not *"does this
buy anything"* — it buys an `M(ii)` grade — but **whether one leg's grade is worth this spend now, and
whether buying it commits the campaign to the composite sibling.** That is a judgement, and it is yours.

**The cost you would be re-authorizing.** §6c records your *"relaunch it"* given after the corrected
figure: **≈8.7 GPU task-hours over 13 scheduler tasks, `18` GPU task-hours worst case**, against a
ratified arm-1 envelope of `20` — **10% headroom**, with that document's own rule that any
resubmission after a failure voids the declaration again.

**Nothing is interrupted by suspending it.** Measured by this lane at `52cbda90`:
`nd-unfolding/uq_5d/` contains no `cause3_mii_20260901/`, and no
`RECEIPT-20260901-cause3-mii-estimator-seed-magnitude.json` exists under `docs/orchestration/state/`.
**The run has not launched.** (Corroborating, from the untracked snapshot and therefore routing only:
no non-cron job has run on the cluster since 2026-09-01T03:58:02Z.)

**AUTHORIZES:** nothing to run, under any branch. Branch (b) requires two documents before submission
and grants no compute itself.

**LEAVES UNCHANGED:** §1's quantity, §2's footing falsifiers, §3's thresholds `f_agg <= 0.0415` and
`f_med <= 0.0274` with their publication-precision derivation, §4's six branches and §5's limits stand
exactly as written — **the criterion is not retuned; only the purchase is gated.** `M(i)` remains
satisfied and is not reopened.

**SUPERSEDES:** under branch (b), the launch authorization in `PREDECLARE-20260901-cause3-mii` §6c, by
**suspension**; under branch (c), by **withdrawal**; under branch (a), nothing. Your own words are
what would be held, so only you can hold them.

---

## R5 — a DATE/RESOURCE STOP whose default outcome is the central-value Letter

> **RECOMMENDED RULING (branch c).** The seven-cause discharge campaign runs until **either** a named
> date **or** a named resource ceiling is reached, whichever comes first. On reaching either, the
> campaign **stops** and the default outcome is the Letter **as scoped** — every non-2D result a
> central value, the joint high-`E_avail`/high-`W` generator deficit reported without a significance.
> Continuing past the stop requires a fresh decision; continuation is **not** the default.
> **A ceiling is a prohibition and an accounting boundary. It is NOT authorization to spend up to
> it** — every run still needs its own pre-execution declaration and authorization.

**Basis.** `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` ruled **(a)** the scalar-5D
covariance gates a claim **upgrade**, not submission, and **(b)** the dependency is retained by
choice — *"The intention is to be done with the uncertainties before publication."* The Letter already
stands without the covariance (`paper_body.tex:145-148`), and every object it quotes is graded
VALIDATED.

**SUPERSEDES — and this is a correction to rev. 1, which wrongly claimed it superseded nothing.**
That decision states half (b) *"cannot slip by default — it slips only if he says so later."*
**`R5` is exactly that later saying.** Under branch (c) it **conditionally supersedes half (b)**: the
intention to finish the uncertainties before publication holds **until** the stop fires, and is
released at the stop in favour of the scoped Letter. Half **(a)** is untouched and is not reopened.
Rev. 1's *"leaves both halves unchanged"* is withdrawn.

**AUTHORIZES:** the stop, once **every** field in §8 is filled. It authorizes **no submission**:
reaching the stop selects the Letter's *scope*, and submission remains a separate decision with its
own prerequisites — including the three things `OI-187`'s row explicitly did not measure (note
completeness, co-author review, MINERvA collaboration review).

**LEAVES UNCHANGED:** half (a) of `OI-187`. Before the stop fires, the covariance work continues at
full weight; this is not a stand-down or a deprioritisation. Gate 2 FAIL and the counts untouched.

---

## R6 — PET remains DIAGNOSTIC unless the named ladder passes on its merits

> **RECOMMENDED RULING.** PET stays **diagnostic and method-development, not a publication
> uncertainty product**, and must read that way in note, primer **and** paper. Only the ladder already
> named in `OI-126` reopens it — **estimator-equivalence PLUS coverage**, where **coverage is a
> different object from verifying the construction**. Passing a Gate-6 leg, **independently verifying
> the existing `C_stat` construction**, or a favourable typed-descriptor result is **not** a promotion
> and must not be reported as one.

**Terminology, corrected from rev. 1.** Rev. 1 wrote *"verifying `C_stat`"*, which reads as though the
artifact could become verified. It cannot by that route: PET `C_stat` is
`EXISTS — UNVERIFIED, PAIRING DECLINED` (`VALIDATION_LEDGER.md` `VL132`, whose own cell records
*"THE RECEIPT MAY NOT CLAIM INDEPENDENT CONSTRUCTION OR INDEPENDENT VERIFICATION: there was ONE
builder"*). What is available is an **independent verification of the existing construction**, and
`AGENTS.md` already holds that this is *distinct from scientific adoption or pairing*.

**AUTHORIZES:** nothing. It is a reaffirmation, filed because the reversal path is what gets read
loosely.

**DECLINING TO REAFFIRM CHANGES NOTHING.** `OI-126`'s 2026-08-20 ruling stands on its own authority;
`R6` cannot strengthen it and rejecting `R6` cannot undo it. Reversal requires a **separate** decision,
taken after estimator-equivalence **and** coverage evidence exist.

**LEAVES UNCHANGED:** `OI-126`'s declined pairing and demotion — **a fourth move, not a choice among
the three refuted branches**; no PET total covariance adopted; the corrected recoil-only budget a
legacy representation cross-check that cannot satisfy or feed the full-event DAG; and Gate 6
**BLOCKED** under its five prohibitions, reproduced as keys from
`docs/orchestration/state/gate6-member-trajectories-result-56847059.json` rather than paraphrased:

```
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

**SUPERSEDES:** nothing.

---

## §7. Routing — owning record and fallback state, per ruling

**This packet has no single governing `OI-*` row, and that is a property of the questions, not an
omission.** It cross-cuts `OI-126`, `OI-172`, `OI-173`, `OI-187` and the live qualifications in
`OI-188`. It is **absent from `docs/CURRENT_WORK.md`**, which is generated from
`control-plane/work-items.tsv` and renders only promoted leaves; promoting an unsigned recommendation
would put a lane's proposal in the routed queue. Each ruling therefore routes to the record that will
own it **once signed**:

| | owning record once signed — **all exist today** | where the substance lives now | fallback if unruled |
|---|---|---|---|
| `R1` | `docs/orchestration/PREDECLARE-20260901-cause7-discharge-criteria.md` §2 bullet 2 (the sentence reserving the question), by an appended dated ruling section; **and** the cause-7 grade row at `docs/orchestration/SCOREBOARD-20260817-quarantine-seven-causes.md:85` | same predeclaration §0, §2 | work remains open; no new compute or resource authority follows |
| `R2` | the same predeclaration §2 bullet 2; an amendment note **on** `docs/orchestration/DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md` §1; and a **new** `(cause 7, Y)` row beside `SCOREBOARD…:85`, which is **not** edited | same predeclaration §0, §2 | no successor `Y`; `(cause 7, G)` in the state `R1` or its fallback selects |
| `R3` | `docs/orchestration/PREDECLARE-20260901-cause7-discharge-criteria.md` §1 `M` — the *"the threshold is **LEFT OPEN**"* passage is the exact text the ruling replaces — and §2 bullet 3 | same predeclaration §1 `M`, §2 | `M` OPEN regardless of any measured value |
| `R4` | an amendment to `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` §6c | that document §4, §5, §6c | §6c authorization stands; scan submittable |
| `R5` | an amendment to `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` half (b); `OI-187`'s row | `OI-187`; `paper_body.tex:145-148` | open-ended continuation |
| `R6` | `OI-126`'s row; `AGENTS.md`'s PET line | `OI-126`; `VL132`; the Gate-6 receipt | unchanged — `OI-126` stands either way |

**No placeholder records.** Every owning record named above exists at `52cbda90`; none is a
`DECISION-2026xxxx` to be invented later. If you would rather these rulings live in a standalone
`DECISION` record, that record must first be created **and routed** — a `MANIFEST-overrides.tsv` row
and a `CATALOG.md` entry — or it is invisible to the router and owns nothing. Naming it here before it
exists would be the placeholder this table is meant to avoid.

**Owner eligibility.** `BEN-381` disqualifies a lane that measured a leg from grading it. This lane
measured the cause-3 launch absence and re-read every artifact cited here, so it must not grade any
leg these rulings enable.

---

## §8. `R5`'s meter — the fields that must be filled, or branch (c) is not defined

A stop rule with an undefined meter is not a stop rule. Under branch (c) **all seven** are required;
proposed defaults are this lane's recommendation, not a ruling.

| field | proposed default |
|---|---|
| **unit** | **task-hours** — sum of `ElapsedRaw` over **distinct task identities**, `.batch`/`.extern` and array-bracket rows excluded (`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`; `AMENDMENT-20260831-oi177` §1). Not core-hours, not `TotalCPU`, not `AllocCPUS`-weighted |
| **baseline / t0** | the commit instant of the signed stop ruling; spend before t0 is not metered |
| **timezone** | **UTC** throughout; `sacct` queried with explicit UTC, per the snapshot's own clock caveat |
| **boundary** | **inclusive** — the stop fires at the first instant `now >= date T00:00:00Z`, or at the first accounting query where cumulative spend `>=` a ceiling |
| **GPU/CPU trigger logic** | **OR** — either ceiling firing stops the campaign. They are different units and a ceiling in one does not cover the other |
| **failed and retried tasks** | **counted in full**, including `FAILED`, `CANCELLED` and `TIMEOUT`. A failed task spends; excluding it would make the ceiling unreachable by retrying |
| **jobs already running at the stop** | allowed to run to completion, their spend counted; **no new submission after the stop** |

**Three blanks only you can fill: the date, the GPU task-hour ceiling, and the CPU task-hour
ceiling.** (§9 counts them the same way; a date without both ceilings does not define branch (c).) Context rather than recommendation, and from the untracked snapshot, so re-measure before
relying on it: pscratch stood at **80.0%** of 20 TiB on 2026-09-02, against the **79.9%** committed in
`OI-131`.

---

## §9. What this packet does NOT do

It grades no leg, discharges no cause, adopts no artifact, constructs nothing, launches nothing, grants
no spend, writes no scheduler state, moves no pin, changes no publication claim, and closes no `OI-*`.
It does not expire `FREEZE-20260830-k0-deployment-7ac0edec.md`, which remains live — no round-2
`F-1(b)` producer filing is tracked, so `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2 has
not taken effect. It regenerates no state: `generate_live_state.py --check-freshness` returns
**STALE** at `52cbda90` (recorded `Git: 712de1b`), and the authored input `state/live-state.json` is
newer than the rendered `LIVE-STATE.md`, so regeneration is withheld pending `OI-73`'s owner.

**The questions that require your authority are the six branch choices in §0 and the three blanks in
§8.** There are no others.
