# DECISION 2026-09-20 — Joseph rules the §6.4 clause-(c) disposition: `V2` cleared, `V6` outside scope, the ordering defect ratified

**THIS RECORD DISPOSES OF CLAUSE (c).** It closes the `BLOCK` reported at
[`DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md`](DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md).

**CITABLE FOR:** the disposition of clause (c) for the digest `3d7465f6…`, and the two limitations
§5 records.
**NOT CITABLE FOR:** any other candidate, any re-grade, any claim that the verification preceded
the adoption, or any general rule about what independence requires elsewhere.

---

## 0. ⚠ HOW THIS RULING WAS TAKEN, stated first because the provenance of a ruling is part of it

Joseph ruled **in session on 2026-09-20**, in the working session that produced this record, by
selecting one of three dispositions put to him. **He was shown the alternatives and the cost of
each.** The option he selected, reproduced verbatim as it was put:

> **Rule V6 outside clause (c).** `V6`'s six are reproductions of already-committed receipts, not
> verdicts — the assessor itself said re-measuring a digest or a count is fine and only judgement
> needs independence. I write the `DECISION` recording clause (c) satisfied as to independence, with
> the ordering defect (verification followed adoption) ratified retrospectively and named as a
> limitation.

The two he declined were **commission a fourth independent lane on `V6`**, and **draft only, leave
unsigned**.

**This is a selection, not dictated text.** The decision is his; the reasoning below, the
measurements, and every word of the wording are this lane's, written after the selection and not
approved by him line by line. **A reader must not attribute any sentence below §0 to Joseph as his
own phrasing.** What is his is the disposition itself, and §4's ratification.

---

## 1. The condition being disposed of

`AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md`, sub-clause **(c)**, verbatim:

> **(c)** **Adoption of this digest may proceed notwithstanding (a)** if and only if the remaining
> required evidence is complete and independently verified. **(c) is a permission to decide, not a
> decision, and not evidence.**

Two things had to be settled: **what "the remaining required evidence" is** — the amendment gives a
definite description and never enumerates it — and **who may certify it**.

## 2. `V2` — DISCHARGED by the third lane

`VERIFICATION-20260918-scalar5d-adopt-clause-c.md` (`lane/z-criteria-independent-assessment-20260910`,
head `935b75585a7b9cc39cd52d4aa001df4edbea875f`) returned `BLOCK`, and after `V1` closed and `V3`
was reclassified, **the `BLOCK` stood on `V2` alone**: C5's and C7's evidence in the blocker table
was that assessor's own work, so signing those two rows would make clause (c) inert for them.

`V2` is now discharged. [`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md)
is a third lane — a different model on a different account, which authored none of the C5/C7
evidence and does not own cause 5, and which states so in its own words and names what it did not
inherit. It re-measured from bytes:

| row | third-lane result |
|---|---|
| **C5** | **NOT FALSIFIED** on the assembly import closure at `fb9ec356`, all **15** repository modules matched against their Git blobs with no missing module on the assembly path, `adopt_unified_5d.py` genuinely in the closure and covered (blob `e1260e8d…`, matching the receipt), and all **eight** manifest sources opened and fully hashed. The producer-chain residual is preserved exactly as the 09-18 ruling stated it, and named as a residual rather than a missing sixteenth module. |
| **C7** | **REPRODUCES.** 45 unique band keys, V 13 / R 27 / A 5, disjoint and exhaustive; the four weight-only bands present in `R`; ten endpoints with distinct SHA-256s matching `p4_standard_manifest.json`; the ten migration censuses agreeing with the declared policies at `p4_lib.py:64-65`; the §1.3b identities at `1e-16`; PSD checked by an independent eigensolve. `SPEC:802`'s abort condition does not trigger in either direction. |

⚠ **And the third lane did not sign more than it measured.** It states that *"measured twice, two
files"* is **not** two independent physical origins — both records take the inventory from the
support file's keys — and it therefore read the original support file itself rather than counting
the agreement as corroboration. It also confirmed, independently, the historical `G5` limitation
already recorded in `OPERATIVE-SHEET` §3: at `fb9ec356` a one-for-one residual substitution survived
`exhaustive: true`, and the repair at `check_declared_residual` is **not retroactive evidence** about
the old guard.

## 3. `V6` — RULED OUTSIDE clause (c)'s "remaining required evidence"

`V6` names six items the 09-18 assessor could not reproduce **from where it sat**, each explicitly
*"not doubted"*: C4's jitter receipt from job `58547629`; C2's declared `0.168` and measured
`2.6739`; NULL's `4.4311e-14`; the seven boundaries' `read_by_production: no`; the historical
absence of `--run-class` from `run_m1_projection.sh`; and whether `58549890`'s control arms
discriminate.

**RULED: these are not within clause (c)'s independence requirement.** The ground is the
distinction the 09-18 assessor drew against itself, applied consistently:

> re-measuring **a digest or a count** they previously measured is fine, because independence is
> about **judgement**, not arithmetic. What they cannot do is certify their own **verdicts**.

Each `V6` item is a **reproduction of an already-committed receipt value**, not a verdict. `V2`
disqualified the assessor from certifying **its own judgements** on C5 and C7, and that
disqualification does not extend to arithmetic nobody disputes and no lane authored as a conclusion.

⚠ **Two things this ruling is careful not to say.**

1. It does **not** say the `V6` items are verified. They are **unreproduced by a second lane**, and
   that is now a recorded limitation (§5), not a discharged requirement.
2. It does **not** establish a general rule that receipt reproductions are always outside an
   independence requirement. It disposes of `V6` **for this digest**, on the six named items.

**Joseph's own 2026-09-19 §7 stopping rule bears directly on the alternative** and is quoted because
it was the reason the second option was declined rather than merely unattractive: *"Reopen this
concern only for new contradictory implementation evidence, a material change to the analysis, or a
concrete missing physical uncertainty. The provenance gap accepted here, **repeated summaries of
existing evidence**, and the absence of optional studies are not grounds for another review cycle."*
A fourth lane re-reading `58547629`'s receipt is a repeated summary of existing evidence.

## 4. THE ORDERING DEFECT — ratified retrospectively, and it is not cured

**Clause (c) is an iff, and an iff about a precondition.** The independent verification was required
**before** the adoption. It did not happen before the adoption:

| | |
|---|---|
| `V2`'s `BLOCK` recorded | 2026-09-18 |
| Joseph's adoption of `3d7465f6…` | **2026-09-20**, `60ecbcd5` — with clause (c), the verification and the `BLOCK` appearing **nowhere** in the adoption record |
| the omission disclosed | 2026-09-20, `72a2ada5` |
| the third lane's verification completed | **2026-09-20**, after the adoption |

**RULED: the adoption stands, and the out-of-order verification is ratified retrospectively.**
The substance clause (c) demanded — independent verification of the rows an interested lane could
not sign — exists and is negative for both rows. What cannot be manufactured is the **sequence**.

⚠ **This is a ratification, not a repair, and the difference is the whole point of recording it.**
An auditor is entitled to know that the permission to decide was exercised before the condition on
it was met. The third lane says so itself, unprompted: this verdict *"does not … make verification
have preceded the adoption."* Nothing here contradicts that sentence and nothing may be cited as
doing so.

## 5. THE TWO LIMITATIONS THAT TRAVEL WITH THIS DISPOSITION

**L1. `V6`'s six items have no second-lane reproduction.** Ruled outside clause (c), not verified.
Anyone re-opening C2's `0.168`, C4's jitter print, NULL's `4.4311e-14`, the `read_by_production`
census, or `58549890`'s control arms is reading single-lane evidence.

**L2. The verification followed the adoption.** §4. Clause (c) was satisfied in substance and
violated in order.

⚠ **And one that is NOT new but must not be lost in this record's own scope:** the third lane
verified **two rows**. It states that it *"does not independently certify every other requirement of
§6.4 clause (c)"*, and that it *"does not certify publication readiness."* This decision supplies
the missing half of the iff by **ruling on what the requirement covers**; it does not claim a lane
measured every row.

## 6. Consequent state

- **§6.4 clause (c): DISPOSED.** `V2` discharged by measurement, `V6` ruled outside scope, ordering
  ratified with L2 recorded.
- **The `BLOCK` at `VERIFICATION-20260918-scalar5d-adopt-clause-c.md` is answered**, not overridden.
  Question (1)'s sole surviving ground was `V2`; `V2` is gone.
- **The adoption of `3d7465f6…` is unchanged**, and so are its four measurements as corrected by
  [`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md).
- **`V5` was already discharged** before this decision: its two wording defects — the dtype claim and
  the `metadata_json` claim — are corrected in `OPERATIVE-SHEET` §4 and have been since 09-18.
- **Nothing here discharges cause 3.** `M(i)` stays `UNRESOLVED` on `4c`; `C3` stays *predeclared and
  not computed* for this digest.

**Co-Authored-By: Claude Opus 5 (1M context)**
