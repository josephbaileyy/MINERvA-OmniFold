# DETERMINATION — `\petClosure` is **LEGACY**. The header does **not** over-reach; a legacy value **has** printed unstruck three times, twice externally — and there is a **FOURTH** exposure the question did not name

**By:** lane C (PET), as `pet` owner and owner of `SPEC-20260814`, discharging item 3 of
`AUTHORIZATION-20260819-analysis-note-paper-corrections-and-push.md:23`, which requires this
determination **before** any edit to the print sites and forbids answering CANNOT-TELL.
**Answering the audit's row 8** (`AUDIT-20260819-analysis-note-vs-record.md:441`), measured at
`b8f74fbe`.

> **THE ANSWER, AND IT IS MECHANICAL RATHER THAN JUDGEMENTAL.** A committed artifact from 2026-08-06 names
> `\petClosure` **by macro name** as a quoted-number dependency that **changes** if full-event PET moves to
> `niter=3`. **It moved** — `niter=3` is pinned policy (`CLM-010`, `CLM-012`, FROZEN). Therefore
> `\petClosure` is legacy on the *same mechanical ground* as `\petRatio`, which is already struck, and the
> `values.tex` block header covers it correctly. **The missing per-line marker is the defect. The header is
> not.**

| | | |
|---|---|---|
| **Is `\petClosure` CURRENT or LEGACY?** | **LEGACY** | **DETERMINED.** Mine. |
| **Does the block header over-reach?** | **NO.** | **DETERMINED.** |
| **Has a legacy value printed unstruck?** | **YES — 3 sites, 2 of them external.** | **MEASURED.** |
| **A fourth exposure, not `\petClosure`** | **`9%` is INLINED in `paper_body.tex:146`** and no macro marking can reach it. | **MEASURED + ROUTED.** |

---

## 1. THE DECISIVE EVIDENCE, READ AT ITS SOURCE AND NOT VIA THE INDEX THAT QUOTES IT

`STEP2-20260806-niter3-budget-classification.md:87-90`, verbatim:

> *"**One real `niter` coupling, on the central value rather than the covariance:** `sec_pet.tex:47`
> discloses "The PET run used a 2M-event, two-iteration training." **If full-event PET moves to `niter=3`,
> `\petRatio` (0.912, used at `sec_pet.tex:42,59`) and `\petClosure` change.**"*

**Three properties make this dispositive rather than suggestive:**
1. **It names `\petClosure` by macro name.** This is not an inference from the word "closure" or from the
   block it sits in — the coupling was identified and written down **before** the question arose.
2. **It predates the dispute by thirteen days**, so it cannot have been shaped by it.
3. **The antecedent is satisfied.** `niter = 3` is the campaign's pinned policy (`CLM-010`/`CLM-012`,
   FROZEN); `sec_pet.tex:47` discloses the PET run used **two** iterations. The conditional fired.

**The same file at `:130` independently corroborates the print-site count** — *"Only `\petRatio` (2 uses) and
`\petClosure` (3 uses) appear"* — **and 3 is exactly what I measure today** (§3). A count written on
2026-08-06 that still reproduces is evidence the macro's exposure has not been touched since it was flagged.

*Read at source deliberately: `INDEX-retracted-and-superseded-values.md:135-136` quotes this passage, and a
determination resting on an index's quotation of a third file would be a determination about the index.*

---

## 2. WHICH GROUNDS TRANSFER — TWO OF THREE, AND I AM NOT SWEEPING IN THE THIRD

The index gives `\petRatio` **three** independent grounds. **They do not all transfer to `\petClosure`, and
asserting that they did would be the asymmetric-comparison error this campaign keeps filing.**

| Ground | Transfers to `\petClosure`? |
|---|---|
| **2. `niter=2` vs pinned `niter=3`** | **YES — and this alone is sufficient.** §1: named explicitly, mechanical. |
| **3. Estimator change** (full-event schema landed 2026-08-01; *"pre-08-01 PET numbers are a different estimator"*) | **YES.** A closure of the pre-08-01 estimator is a closure **of a different estimator** — which matters precisely because of how the paper words it (§3). |
| **1. J21 — no background subtraction** | **NOT ESTABLISHED, and I do not assert it.** J21's prescription and its *direction* (background left in biases PET high) are arguments about an **absolute normalization ratio**. A closure metric is a self-consistency test against an injected truth and is not obviously sensitive the same way. **Undetermined, and it does not need determining — ground 2 already decides.** |

**So: LEGACY on grounds 2 and 3. Ground 1 is left open on the record rather than borrowed.**

---

## 3. THE THREE PRINT SITES, AND THE INTERNAL CONTRADICTION THAT SETTLES INTENT

Measured this turn — `\petClosure` prints **three** times, **twice in the paper build**:

| Site | Build | Struck? |
|---|---|---|
| `sec_pet.tex:93` | note | **NO** |
| `paper_body.tex:145` | **paper (external)** | **NO** |
| `paper_body.tex:164` | **paper (external)** | **NO** |

**AND THE DECISIVE INTERNAL EVIDENCE IS THAT ONE CAPTION DOES BOTH THINGS AT ONCE.** `sec_pet.tex:93-94`:

> *"The PET/GBDT total ratio is `$\dead{\petRatio}$` — **struck: `niter`=2 legacy, see the scope note in the
> text**; ordinary closure validates the extraction machinery to `$\sim\SI{\petClosure}{\percent}$` …"*

**In a single sentence `\petRatio` is struck FOR BEING niter=2 LEGACY and `\petClosure` is printed plain — two
clauses apart, when the committed flag of §1 names BOTH as changing under the SAME move.** That is not a
considered judgement that closure survives; **it is the marker being applied macro-by-macro instead of by the
ground that condemns them**, which is the failure mode `INDEX-retracted-and-superseded-values.md:110` already
names in this very block: *"Protection is applied to the harmless cases and absent from the live ones. The
marker was the failure here, not the number."*

**And the paper's wording is the strongest form of the claim, not the weakest.** `paper_body.tex:164` (and
`sec_pet.tex:93`) say closure *"validates the extraction machinery"* — **present tense, unqualified, about
the machinery.** Under ground 3 the number validates a **different** estimator; under ground 2 it validates
it at a **different `niter`** from the pinned one. `:145`'s *"internally consistent to ~1%"* is the milder
phrasing and is still a present-tense claim about this analysis.

---

## 4. ⚠ THE FOURTH EXPOSURE — `9%` IS AN INLINE LITERAL IN THE PAPER AND NO MACRO MARKING CAN REACH IT

**Not asked, found while measuring, and it matters now because lane B is editing the paper this turn.**

`paper_body.tex:146` prints *"agrees with the production result at the `\SI{9}{\percent}` level"* — **a
hardcoded literal.** `grep -n petGbdtGap docs/analysis-note/paper_body.tex` → **no match**: the paper does
not use the macro. But `values.tex:74` is `\petGbdtGap{9}` — *"PET-vs-GBDT data-side gap (%); niter=2 LEGACY,
struck at use"* — **the same quantity, and it carries the legacy marker.** On the note side the
corresponding numbers **are** struck (`sec_pet.tex:44-45`: `$\dead{\petRatio}$`,
`\dead{\SIrange{6.5}{9.9}{\percent}}`).

**So the paper prints, unstruck, a legacy value whose macro is marked legacy — by bypassing the macro.**
This is *exactly* the mechanism the index already documented one level up for `\petRatio`'s operands
(*"the quotient of two INLINE `\SI{}` literals … so marking here cannot reach them"*), **recurring in a
second file.** `\dead{}` is in the shared preamble and available to all three builds, so the fix is
available — but **it is a tex edit, it is not mine, and the paper receipt's item 3 authorises resolving
`\petClosure`'s sites, not this.** **ROUTED to lane B and the receipt's owner as a distinct item.**

**The generalisation, which is the reusable part:** *marking a macro protects only the call sites that go
through the macro.* An audit that greps macro names cannot see a value that was typed in by hand — so
**a legacy-value sweep must search VALUES, not just macro names.**

---

## 5. WHAT FOLLOWS, AND WHAT I AM NOT DECIDING

**DETERMINED:** `\petClosure` is LEGACY; the `values.tex:65-74` block header applies to it as written and
does not over-reach; its three print sites are printing an unstruck legacy value, two of them externally.
**Audit row 8 is answered — it is no longer CANNOT-TELL.** The receipt's item-3 precondition is discharged
and lane B is unblocked on the `\petClosure` sites.

**I am NOT deciding, and these are deliberately left:**
- **How to remedy it.** Strike at each site, add the per-line marker in `values.tex:73`, re-source the number
  from a `niter=3` full-event closure, or drop the sentences — that is a tex edit under the paper receipt and
  belongs to whoever holds it. **My determination is the input to that choice, not the choice.**
- **Whether ground 1 (background) also condemns it.** §2: undetermined, and not needed.
- **Ground-3 scope.** I have not established *when* the `\petClosure = 1` value was produced, only that it
  predates the pinned configuration on ground 2's mechanical argument. **If someone later shows it came from
  a post-08-01 `niter=3` run, ground 3 dissolves — ground 2 would still stand and the answer would not
  change.** Stated so the determination cannot be overturned by re-opening the weaker of its two grounds.

**Two record defects observed in passing, neither mine to fix, both cheap:**
- `INDEX-retracted-and-superseded-values.md`'s table (`:100-109`) **omits `\petClosure` entirely** while its
  own prose at `:136` names it. **The table is what a sweep reads.** That omission is plausibly the proximate
  cause of the missing marker.
- That table's `values.tex` line references have **drifted by six**: it cites `\petRatio :66` and
  `\petGbdtGap :68`; they are now at **`:72`** and **`:74`** (`\petClosure` at `:73`). Content-verified, not
  offset-guessed.

*Filed by lane C. Every measurement is from the tree at `b8f74fbe`; §1's quotation was read at its source
file, not via the index. I edited no tex, no `values.tex`, no index, and no control-plane source, and this
determination authorises no push.*
