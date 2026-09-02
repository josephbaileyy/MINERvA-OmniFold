# DECISION PACKET 2026-09-02 — six rulings reserved for Joseph: cause 7's subject and magnitude,
# cause 3's seed scan, the campaign stop rule, and PET's posture

**STATUS: RECOMMENDATION ONLY. UNSIGNED. Nothing below is a ruling until Joseph rules it.**

**CITABLE FOR:** the six recommendations `R1`–`R6` and the three questions in §7, as **this lane's
recommendations**. **NOT CITABLE FOR:** any authorization. Not a discharge, a grade, an adoption, a
gate movement, a launch, a pin move, a scheduler write, a count change, or a publication claim.
**Gate 2 remains FAIL. Quarantine counts hold at CAND `1 of 7`, QUOTED `0 of 7`. No scalar-5D
covariance is adopted. PET `C_stat` remains `EXISTS — UNVERIFIED, PAIRING DECLINED`** — its
existence, digest and ledger row supply neither the independent check nor the central pairing.
The five Gate-6 prohibitions are reproduced in `R6` as keys and must not be paraphrased.

**This lane computed nothing and implemented nothing.** Every figure is read from a committed artifact
named beside it. Three operational figures come from `HANDOFF-20260902-operational-baseline-snapshot.md`,
which is **untracked and therefore routing only, not live evidence**; each is labelled where it is used.

**Why one packet rather than six rows.** Five of the six questions are already reserved for Joseph in
writing by the documents that raised them, and they interact: `R1`/`R2` fix the subject that `R3`
grades, and `R4` and `R5` spend the same finite budget. Ruling them separately invites a subject
ruling whose magnitude leg has no criterion, or a seed scan bought after the campaign's stop has passed.

---

## R1 — REJECT cause-7 discharge on G's own bytes, and RETAIN G

> **RECOMMENDED RULING.** Cause 7 cannot be discharged on **G** —
> `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root`,
> sha256 `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2`, job `56720356`,
> 10,694 reported bins. That leg is closed as **unsatisfiable in principle**, not left open pending
> work. **G is RETAINED**: not deleted, not moved, not overwritten. It remains causes 1–6's grading
> subject and `R2`'s required digest-bound parent and comparison baseline.

**Basis.** `PREDECLARE-20260901-cause7-discharge-criteria.md` §0 measures that the selection-complete
lateral replacement does not exist inside G and never traversed G's path: G's committed readback names
`uq_universe_5d_covariance_combined_bkgaware.root` as its `combined_source`
(`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json:28-34`), and the adopter leaves the
detector/lateral bands already inside that source untouched (`nd-unfolding/adopt_unified_5d.py:17-20`).
Correcting the lateral block changes the bytes, hence the artifact. *"No future receipt can make the
existing G bytes have been produced by a path they did not traverse."* This is the same shape as
`DECISION-20260831`'s finding that X's provenance leg is unsatisfiable **in principle** — a permanent
property, not a gap awaiting work.

**AUTHORIZES:** recording cause 7 as permanently OPEN **against G's bytes**, so no lane spends further
effort attempting that discharge.

**LEAVES UNCHANGED:** `DECISION-20260831-joseph-quarantine-graded-against-the-candidate.md` §1 in
full — the seven causes are graded against the stamped candidate, X is retained, and the only
disposition ever authorized for X is demotion **after** adoption. Counts, Gate 2, and `values.tex`
untouched. F's discharge stays FPS-only (266 ≠ 10,694; `OI-5`, `VL68`); J cannot supply a leg for G;
S is not G and its validation proves nothing about G's bytes.

**SUPERSEDES:** nothing. It answers the first half of the question `PREDECLARE-20260901-cause7` §0/§2
reserved for Joseph.

---

## R2 — AUTHORIZE EXACTLY ONE successor Y, for cause 7 only

> **RECOMMENDED RULING.** **Exactly one** cause-7-only successor **Y**, carrying G's full sha256 as
> `parent_candidate`, may inherit G's role as the grading subject **for cause 7 and no other cause**.
> A second successor, or an extension of Y's role to another cause, requires a new ruling.

**AUTHORIZES:** naming Y, and drafting its producing path, receipt schema and test contract to the
`C`/`P`/`T` criteria already written in `PREDECLARE-20260901-cause7` §1 — the closure identity
`C_Y = C_G - L_support + L_active`, the exact five-band inventories, the bit-identity of every
non-lateral block against G, and the two-direction power test. **It authorizes no construction and no
compute.** Building Y is a separate authorization with its own pre-execution cost declaration (see Q3).

**LEAVES UNCHANGED:** causes 1–6 continue to be graded against **G itself**; this moves the subject
for cause 7 and nothing else. Y does not exist, is not adopted, and is not a covariance candidate. A
receipt about S proves S; a receipt about F proves F; neither is `P` for Y. Counts and Gate 2 unchanged.

**SUPERSEDES:** nothing. It closes the second half of the reserved question — *"whether a
cause-7-corrected successor Y can inherit G's role as the grading subject"* — and **extends**
`DECISION-20260831` by one named successor rather than overturning it.

---

## R3 — cause 7's `M` is MEASUREMENT-AND-DISCLOSURE, not a smallness gate

> **RECOMMENDED RULING.** Cause 7's `M` leg carries **no materiality threshold**. It is MET when the
> full measured set is delivered in Y's committed receipt **and** the result is stated in the note.
> A large measured difference satisfies `M` exactly as a small one does.

**The required set is the predeclaration's own, unchanged:** `delta_full`, `delta_lateral`, the
reported-bin ratio `sqrt(diag(C_Y))/sqrt(diag(C_G))` as a **distribution** (min, p05, median, p95,
max, with zero/invalid counts), `||C_Y - C_G||_F / ||C_G||_F`, the largest absolute correlation-matrix
change, and every operand.

**Basis.** No pre-observation rule connects any value of those quantities to cause-7 discharge. The
existing standard-P4 validator records the active/support trace ratio and explicitly labels it
**diagnostic and unbounded** (`p4_validate_active_lateral.py:240-248`; receipt key
`support_ratio_is_diagnostic_not_bounded`), and `CRITERIA-20260811` §0 already holds that size neither
repairs nor excuses a construction defect. Choosing a boundary now, with the standard-P4 comparison
already visible, would be a threshold placed to obtain today's preferred verdict rather than a
criterion.

**AUTHORIZES:** grading `M` on delivery and disclosure, and nothing else.

**LEAVES UNCHANGED:** `C`, `P` and `T` remain OPEN and independent; a disclosed magnitude discharges
nothing by itself, and `CRITERIA-20260811` §0's rule that **all four legs must hold** stands unamended.
**This does not reopen `OI-172`**: `DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` RULING 1
found cause 1's magnitude *material enough to need its own statement in the note*, and therefore did
**not** close cause 1. This ruling uses the same instrument — a magnitude that is **disclosed** rather
than gated — where no principled cutoff exists at all. It neither weakens nor extends that finding.

**SUPERSEDES:** nothing. It exercises the explicit either/or `PREDECLARE-20260901-cause7` §1 `M` and
§2 reserved for Joseph, taking the second branch: *"rule explicitly that M is measurement-only under
§0 and carries no smallness requirement."*

---

## R4 — a VALUE-OF-INFORMATION decision is required before ANY cause-3 seed scan

> **RECOMMENDED RULING.** No cause-3 estimator-seed scan may be submitted until a written
> value-of-information note is signed, stating **what decision the number changes** and **under which
> outcome branch**. **The 2026-09-01 launch authorization is SUSPENDED, not void**, and revives on
> that signature.

**This is the only ruling in the packet that takes something back, and it says so plainly.**
`PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` §6c records Joseph's *"relaunch it"*,
given after he was shown the corrected cost: **≈8.7 GPU task-hours over 13 scheduler tasks, `18` GPU
task-hours worst case** against a ratified arm-1 envelope of `20` — **10% headroom**, with that
document's own rule that any resubmission after a failure voids the declaration again.

**Nothing is interrupted.** Measured by this lane at `52cbda90`: `nd-unfolding/uq_5d/` contains no
`cause3_mii_20260901/`, and no `RECEIPT-20260901-cause3-mii-estimator-seed-magnitude.json` exists
under `docs/orchestration/state/`. **The run has not launched.** (Corroborating, from the untracked
snapshot and therefore routing only: no non-cron job has run on the cluster since
2026-09-01T03:58:02Z.)

**Why value-of-information and not affordability.** The scan is affordable; the open question is what
a result buys. Its own §5 already states it cannot discharge cause 3, close another cause, change a
count, adopt a covariance, move a gate, touch `values.tex`, or add `C_seed` to the budget — and §4's
four unfavourable branches all terminate in a disclosure rather than a discharge. A number that
changes no decision under any branch should not be bought, however cheap. The discipline also catches
the expensive sibling before it is proposed: §5 flags the full two-baseline composite scan as a
separate question, and `INDEX-retracted-and-superseded-values.md:78` prices **one additional estimator
seed across all four blocks** at **`39.223` A100-h PLUS `55.337` CPU task-hours** — two units, the
second larger, against a `24` A100-h grant that does not reach the second at all.

**AUTHORIZES:** nothing to run. It requires one document before submission.

**LEAVES UNCHANGED:** §1's quantity, §2's footing falsifiers, §3's thresholds `f_agg <= 0.0415` and
`f_med <= 0.0274` with their publication-precision derivation, §4's branches and §5's limits stand
exactly as written — **the criterion is not being retuned; only the purchase is being gated.** `M(i)`
remains satisfied and is not reopened.

**SUPERSEDES:** the launch authorization in `PREDECLARE-20260901-cause3-mii` §6c, **by suspension**.
Joseph's own words are what would be held, so only he can hold them — hence Q2.

---

## R5 — a DATE/RESOURCE STOP whose default outcome is the central-value Letter

> **RECOMMENDED RULING.** The seven-cause discharge campaign runs until **either** a named date **or**
> a named resource ceiling is reached, whichever comes first. On reaching either, the campaign
> **stops** and the default outcome is the Letter **as scoped** — every non-2D result a central value,
> the joint high-`E_avail`/high-`W` generator deficit reported without a significance. Continuing past
> the stop requires a fresh decision; continuation is **not** the default.

**Basis.** `DECISION-20260901-joseph-oi187-upgrade-not-blocker.md` ruled **(a)** the scalar-5D
covariance gates a claim **upgrade**, not submission, and **(b)** the dependency is **retained by
choice** — *"The intention is to be done with the uncertainties before publication."* Half (b) has no
terminal condition, so *"elective, not structural"* has no date on which the election is actually
made. The Letter already stands without the covariance (`paper_body.tex:145-148`: *"Every non-two-
dimensional result in this Letter is a central value… no superseded or historical covariance is used
here"*), and every object it quotes is graded VALIDATED.

**AUTHORIZES:** the stop itself, once its two blanks are filled (Q1). It authorizes **no submission**:
reaching the stop selects the Letter's *scope*, and submission remains a separate decision with its
own prerequisites — including the three things `OI-187`'s row explicitly did not measure (note
completeness, co-author review, MINERvA collaboration review).

**LEAVES UNCHANGED:** both halves of `OI-187`. The covariance work continues **at full weight** until
the stop; this is not a stand-down, a deprioritisation, or a reopening of half (a). Gate 2 FAIL and
the counts are untouched.

**SUPERSEDES:** nothing. It supplies the terminal condition half (b) lacks.

---

## R6 — PET remains DIAGNOSTIC unless the named ladder passes on its merits

> **RECOMMENDED RULING.** PET stays **diagnostic and method-development, not a publication
> uncertainty product**, and must read that way in note, primer **and** paper. Only the ladder already
> named in `OI-126` reopens it — **estimator-equivalence PLUS coverage**, where **coverage is a
> different object from verifying the construction**. Passing a Gate-6 leg, verifying `C_stat`, or a
> favourable typed-descriptor result is **not** a promotion and must not be reported as one.

**AUTHORIZES:** nothing. It is a reaffirmation, filed because the reversal path is what gets read
loosely.

**LEAVES UNCHANGED:** Joseph's 2026-08-20 ruling; `OI-126`'s declined pairing and demotion — **a fourth
move, not a choice among the three refuted branches**; PET `C_stat` `EXISTS — UNVERIFIED, PAIRING
DECLINED` (`VL132`); no PET total covariance adopted; the corrected recoil-only budget a legacy
representation cross-check that cannot satisfy or feed the full-event DAG; and Gate 6 **BLOCKED** under
its five prohibitions, reproduced as keys from
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

## §7. What this packet does NOT do, and the three questions

It grades no leg, discharges no cause, adopts no artifact, constructs nothing, launches nothing,
writes no scheduler state, moves no pin, changes no publication claim, and closes no `OI-*`. It does
not expire `FREEZE-20260830-k0-deployment-7ac0edec.md`, which remains live — no round-2 `F-1(b)`
producer filing is tracked, so `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2 has not taken
effect. It regenerates no state: `generate_live_state.py --check-freshness` returns **STALE** at
`52cbda90` (recorded `Git: 712de1b`), and the authored input `state/live-state.json` is newer than the
rendered `LIVE-STATE.md`, so regeneration is withheld pending `OI-73`'s owner.

**Questions that require Joseph's authority — three, and no others.**

1. **`R5`'s two blanks.** What **date**, and what **resource ceiling** (in GPU task-hours and CPU
   task-hours — the unit ruled on 2026-09-01)? Both are needed: a date alone does not bound spend, and
   a ceiling alone does not bound calendar. Context rather than recommendation, and from the untracked
   snapshot so re-measure before relying on it: pscratch stood at **80.0%** of 20 TiB on 2026-09-02,
   against the **79.9%** committed in `OI-131`.
2. **`R4`'s suspension.** Do you withdraw, until the value-of-information note is signed, the
   *"relaunch it"* authorization you gave on 2026-09-01 against ≈8.7 GPU task-hours? It is your own
   authorization, so only you can hold it.
3. **`R2`'s scope.** Does authorizing one successor Y authorize its **construction**, or only its
   **specification**? This lane recommends **specification only**, with construction returning as a
   separate pre-execution cost declaration.

Everything else here is a recommendation you can sign or reject without further input.
