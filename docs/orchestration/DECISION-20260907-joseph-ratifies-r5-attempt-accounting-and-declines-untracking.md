# DECISION — Joseph ratifies R5's attempt-level accounting, and DECLINES untracking the admission gate path

**⚠ THE RULING WAS GIVEN 2026-09-06. THIS RECORD WAS WRITTEN 2026-09-07, AND ITS FILENAME CARRIES THE
RECORDING DATE, NOT THE RULING DATE.** Corrected in place — the first revision of this file was titled
*"DECISION 2026-09-07"*, which would read as **authorizing a landing that had already happened**: the
repair landed at `72bcd2f6` and reached `main` at `d4922b89` on **2026-09-06**, under this same
instruction. **It is not retroactive authorization.** The filename is left unchanged because
`6669ac3b` and the finding already point at it.

**Status:** RECORDED. **Owner of the decision:** Joseph.
**Ruling given:** 2026-09-06, on approving the landing — verbatim in the finding's **Appendix A**.
**Confirmed directly to this lane:** 2026-09-07 (§1).
**Recorded by:** the Z-specification lane (`lane/y-cause7-spec-and-scope`), which is **not** the lane
that wrote the repair. **Recorded at:** 2026-09-07T01:27:29Z, **tree at recording** `d4922b89`.
**Rules on:** `FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` **§5** and **§8** — two of
the three items that finding placed with the decision owner.
**De-staled against by:** `6669ac3b`, which points that finding's status line, §5 and §8 here.

**CITABLE FOR:** that R5's metered unit is the execution attempt, by decision and not only by code;
that the alternative reading of R5 §3 is overturned; that the admission gate path stays tracked and
`committed_r5_receipt`'s requirement is unchanged.

**NOT CITABLE FOR:** any spend figure, any authorization to run, any relaxation of R5, or any
statement that compute admission is armed. **It is not armed** — §4.

---

## 0. What this document is, and what it is NOT

**THIS LANE IS RECORDING JOSEPH'S RULING, NOT GRADING IT.** Neither ruling below is this lane's to
make, and neither is graded here. The finding being ruled on was written by the orchestration lane;
this record is written by a third lane, which is the separation the campaign's own conventions ask
for.

**AND THIS LANE HAS A DECLARED INTEREST, so it is declared rather than left for a reader to find.**
This lane is the one that reported the **absence** of this record. It re-measured a peer's relay of
these two rulings against `origin/main`, could not corroborate either, and recorded them as
`RELAYED AND UNCORROBORATED` in `SPEC-20260906-complete-scalar5d-successor-Z.md` §5.6c — leaving the
two items referred rather than closed. **So this lane wanted this file to exist.** What keeps that
from being a thumb on the scale is the direction of the outcome: **both rulings confirm the state
that specification already assumed**, so nothing in it moves because of them (§5).

## 1. The ruling, and the provenance chain that makes it citable

**Joseph, in his own turn, 2026-09-07, in session, unrelayed, answering a report that these two
rulings could not be corroborated in the tree:**

> Yes, I ratified both — write the decision record.

**"Both" is fixed by the report he was answering**, which named exactly two: the attempt-level
accounting reading, and the declining of the untrack. Those are §2 and §3. Nothing else is ruled here.

**⚠ AND THE PRIMARY TEXT IS NOW IN THE TREE — ADDED IN THIS AMENDMENT.** This record was written from
a direct confirmation of a summary, and the fuller instruction Joseph actually gave on 2026-09-06 is
recorded **verbatim** by the lane that received it, at the finding's **Appendix A** (`6669ac3b`). That
instruction also **authorized the landing** and carried the constraints it was performed under, which
this record had no basis to hold.

**PRECEDENCE, stated so two documents cannot both claim to govern:** on the **two rulings** in §2 and
§3, **this record governs**, because it rests on a direct answer rather than on a relay. On **anything
else the instruction said** — the landing authorization, the preservation of `t0`, the ceilings and the
stop date, the prohibitions on receipts, tickers and launches — **Appendix A is the source, and it is
not a second ruling.** Where the wording differs on the two rulings, this record governs; where this
record is silent, it is silent, and Appendix A is not overridden by that silence.

**The chain matters and is recorded, because the gap in it is the reason this file exists:**

| when | what happened |
|---|---|
| 2026-09-06 | the finding lands with **three** items *"with the decision owner, not settled here"* — the 30-day `sacct` window (§7), the alternative reading of R5 §3 (§5), and the declined untrack remedy (§8) |
| 2026-09-06 | item 1 is discharged by `FOLLOWUP-20260906-r5-sacct-window-and-post-stop-accounting.md`, which quotes the decision owner directly |
| 2026-09-06/07 | a peer session **relays** that Joseph had ratified the other two |
| 2026-09-07 | this lane **could not corroborate** the relay. Covering search: the finding, `R5-METER.md`, the `FOLLOWUP` record, and a grep over `docs/orchestration/*.md` for `execution attempt` / `requeue` (9 files, each opened). At `d4922b89` the finding's status line still read *"open — three things are with the decision owner"* and §8's remedy still read *"here as a live option for the decision owner"* |
| 2026-09-07 | Joseph confirms directly. **The relay was accurate; the record simply lagged it** |
| 2026-09-07 | **two lanes write the record at once.** This one landed first; the integration lane, holding a near-duplicate, **dropped its own unpushed** rather than leave two decision records for one ruling, and spent its commit on the part only it could do — de-staling the finding (`6669ac3b`) and publishing the verbatim instruction as Appendix A. **Recorded because the race is informative: the same gap was visible to two lanes simultaneously and both moved to close it** |
| 2026-09-07 | this amendment corrects the ruling date and adds the precedence rule above |

**Both halves of that are true and both are kept.** The relaying session was right on the merits, and
it flagged its own message as context rather than as authority. **And the ruling was still not
citable until this file existed** — which is the standard, not a criticism of the relay. A decision
that cannot be found by someone reading the tree cannot be relied on by them.

## 2. RULING 1 — the metered unit is the execution attempt. RATIFIED

**What is ratified, in Joseph's terms as reported to him:** *R5 charges every distinct execution
attempt exactly once — failed and requeued included — with repeated observations and task/step
representations not double-counted.*

**That is the reading the finding adopted, and §5 states it verbatim:**

> "Distinct task identities" sits in the same table cell as the exclusion of `.batch`, `.extern` and
> array-bracket rows, which is what fixes its subject: it is there to stop the several
> **representations** of one execution … from being counted more than once. It does not collapse
> several distinct **executions** of one job id.

**What this confirms, and it is all already in the code — this ruling adds authority, not behaviour:**

| | |
|---|---|
| the query | `sacct -X -D` — `--duplicates` present, so earlier attempts of a requeued job are visible |
| the attempt identity | `(JobID, Start)`. **Not** `(JobID, Start, End)`, which counted two *observations* of one execution as two executions — a defect found and fixed inside the repair |
| the summation | `r5_meter._sum_charged_seconds` |
| the exclusions | `.batch`, `.extern`, numbered steps and array-bracket summary rows — **representations, not executions** |
| the receipt | schema `2`; a version-1 receipt is **refused, not migrated**, because it under-counts every requeued job |

**On the one preserved capture** the ratified reading gives `57712764` = **`12.590278`** CPU
task-hours, against `0.0016667` under the plain query and `8.628611` under the largest-single-attempt
tie-break. **This is one waker job over one window and it is not a campaign total.**

**The reading this overturns**, named plainly by §5 so that it could be: *"distinct task identities"*
as the accounting unit itself — one charge per job id, whatever a requeue did.

**What ratification changes about overturning it.** §5 isolated the summing step in one function
precisely so a contrary ruling would be cheap, and **it still is cheap in code**. What has changed is
that the reading is now settled **by decision**, so reviving it needs **a new decision**, not an edit.
The tie-breaker Joseph accepted is recorded with it: under-counting is the fail-**open** direction
against a prohibition, and R5 §3 says retried tasks are *"counted in full"* and that *"a failed task
spends"*.

## 3. RULING 2 — the untrack remedy is DECLINED. The gate path stays tracked

**What is ratified:** the option §8 offered — untracking or `.gitignore`-ing
`docs/orchestration/state/r5-meter-receipt.json` — is **declined**. **The committed-receipt
requirement stands unchanged.**

**So `campaignctl`'s `committed_r5_receipt` keeps its present meaning:** the receipt must be
**committed** — tracked and byte-identical to its blob at `HEAD` — before any compute item is
admitted, and the `CAMPAIGN_R5_RECEIPT` override remains repository-relative only.

**What this preserves and what it does not.**

- **Preserved: the mechanism.** Arming admission stays possible, and stays a **deliberate, visible,
  reviewable act** — a commit of a tracked file, which leaves a record with an author. §8's own
  reasoning for declining is what is ratified: ignoring the path would change *"how compute admission
  can ever be armed, for anyone, in any future"*.
- **Not reduced: the hazard §8 names.** After the repair, the previously documented command produces
  a **valid, armable** receipt rather than a visibly wrong one. **The mitigation is the remedy that
  was taken** — `R5-METER.md` no longer defaults `--write`, its verification examples write to a
  scratch path or nothing, *"refresh"* is gone, and a dedicated section states that committing to the
  state path opens admission queue-wide. **This ruling does not soften any of that**; it decides that
  the second, mechanism-level remedy is not the answer.
- **Retired: §8's *"live option"*.** It is no longer live. It was decided, and it was declined.

**Measured at this tree, so the ruling is not mistaken for an arming act:**

| | |
|---|---|
| `git log --all -- docs/orchestration/state/r5-meter-receipt.json` | **`0` commits.** The path has never been written on **any** ref |
| `git cat-file -e d4922b89:docs/orchestration/state/r5-meter-receipt.json` | **absent** |

**Compute admission is unarmed, and this decision leaves it unarmed.**

## 4. What this decision does NOT do

1. **It authorizes no compute.** R5 is a prohibition and its ceilings are not permission to spend up
   to them. Every run still needs its own declaration and its own authorization.
2. **It arms no admission.** No receipt exists; none is created here; committing one remains a
   separate, deliberate, queue-wide act by whoever does it.
3. **It changes no ceiling, no gate, no count and no grade**, and it amends no prior ruling.
4. **It does not touch the 30-day `sacct` window.** That was the finding's third item and it is
   discharged separately by `FOLLOWUP-20260906-r5-sacct-window-and-post-stop-accounting.md`, which
   remains **OPEN** with two dated obligations. *A query limitation is not permission to omit
   expenditure*, and nothing here relaxes that.
5. **It produces no spend figure.** The `12.590278` in §2 is one waker job over one window, quoted to
   identify the reading, not to price anything.
6. **It does not edit the finding it rules on** — and **⚠ it no longer needs to.** When this record
   landed, `FINDING-20260906-…`'s status line still read *"open — three things are with the decision
   owner"* and its §8 still offered the untracking remedy as *"a live option"*, both stale in the two
   items ruled here. **That was its owning lane's to correct, and it did, at `6669ac3b`:** the status
   line, §5 and §8 now point here, with the overturned reading and the refused proposal **kept in
   place rather than deleted**, so a reader sees what was turned down as well as what was taken.

## 5. What moves downstream, and the answer is almost nothing

**Both rulings confirm the state the tree and its dependents already assumed**, which is why this
record can be written by a lane with a declared interest in it existing:

- `r5_meter` and `campaignctl` are **unchanged** — ruling 1 ratifies what they already do.
- `R5-METER.md` is **unchanged** — ruling 2 declines a change that was never made.
- `SPEC-20260906-complete-scalar5d-successor-Z.md` §5.6b's `D5` moves from *resolved by code* to
  *ratified*; its §7 item 19's second remedy moves from **referred** to **closed as declined**; and
  its §4 row 3 and Tier-3 prerequisite list are **unchanged**, because the committed-receipt
  requirement they rest on is exactly what ruling 2 preserves.

**The one thing that genuinely changes is citability.** Before this file, a reader of the tree found
an open finding and a relay. After it, the two rulings are where the finding is, with the words that
were ruled on quoted beside them.

## 6. The standard this record exists to meet

**A relay is not a ruling, and an accurate relay is still not a ruling.** The relaying session was
right about the merits and careful about its own status; the gap was that nothing in the tree carried
the decision. **What closes such a gap is a committed record, or the decision owner saying so
directly** — here it was the second, which produced the first.

**The failure this prevents is not disbelief; it is silent divergence.** Two sessions can each act
correctly on an uncorroborated ruling and record incompatible states, and neither will find the
disagreement, because there is nothing to check against. That is a defect in the record, not in
either session, and a file is the fix.
