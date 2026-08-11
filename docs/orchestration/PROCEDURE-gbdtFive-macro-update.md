# PROCEDURE — updating the four `\gbdtFive*` macros when the J28 re-roll is adopted

**Written cold, 2026-08-11, before the adoption and before the edit.** **STATUS CHANGED the same day:** Packet B closed on an independent PASS (`1440b58`), so the pipeline-debt standard is met and the adoption gate is actionable rather than blocked behind verification. **This is now a procedure about to be used, not a contingency** — re-read §3 and §5 before editing, and note that two of the six rows (PSD, and the "neither is adopted" sentence) cannot be discharged by arithmetic at all. BEN-087 says attributions must be
re-verified alongside numbers; it does not say *which* sentences. This enumerates them, sourced by `git grep`
rather than recall, so the check exists when the pressure is to just change the number.

**Not an authorization.** The values are the GBDT/close-out lane's and are quarantined on two grounds (the
2026-07-12 class and J28). Nothing here supplies a replacement magnitude.

## 1. The four macros and their single consuming block

    values.tex:57  \gbdtFiveBlockMedian  13.36     syst+stat+ML block sum, median/bin (%)
    values.tex:58  \gbdtFiveAdoptTrace   5.81e-38  adopted mean-centered sqrt(trace)
    values.tex:59  \gbdtFiveCVTrace      6.24e-38  conservative CV-centered variant
    values.tex:60  \gbdtFiveMeanShift    1.65e-38  separately reported joint mean-shift norm

**All four are consumed in one continuous prose block, `sec_systematics.tex:162-170`** — at `:163`, `:165`,
`:166` and `:168` respectively. There is **no second consumption site anywhere in the note.** So this is one
sentence-chain to re-read, not four independent edits, and the risk is that a per-macro search-and-replace
leaves the chain internally inconsistent.

## 2. BEN-087 applies in a MODIFIED form here, and the modification is worse

BEN-087's trap needs a sentence that **names a source**, so that swapping the value silently re-points the
claim. Checked line by line across `:158-172` for attribution language (`from`, `summary`, `rollup`,
`artifact`, `ledger`, `taken`, `\ref`): **there is none.** The block states four magnitudes and attributes
them to nothing.

So the good news is that no source claim can be silently re-pointed. **The bad news is the reason: the numbers
have no attribution at all**, which means (a) a reader cannot check them, and (b) an updater has nothing to
re-verify against. **The fix at update time is therefore to ADD provenance, not merely to preserve it** — write
the artifact path beside each macro in `values.tex`, as the `pc*` block had done for it on 2026-08-11.

## 3. The RELATIONAL claims — the part a number-only edit breaks

The prose does not merely print four values; it asserts relations between them. Each must be re-checked
against the new numbers:

| line | claim in words | what it requires |
|---|---|---|
| `:162-164` | *"the background-aware block sum has median per-bin uncertainty `\gbdtFiveBlockMedian`; including cross-source nonlinear response **raises** the candidate mean-centered covariance to `\gbdtFiveAdoptTrace`"* | a **direction**: adopt-trace is the *raised* quantity. If the re-roll inverts that, the verb is wrong |
| `:167-168` | *"A CV-centered construction gives **the larger** `\gbdtFiveCVTrace`"* | **`CVTrace > AdoptTrace`.** Holds now (`6.24 > 5.81`) and holds under the reported directions (`~5.68 > ~5.29`), but it is an ordering assertion and must be re-checked, not assumed |
| `:165-167` | *"The joint mean shift, norm `\gbdtFiveMeanShift`, is **reported separately rather than folded into** that covariance"* | a **treatment** claim, not a magnitude — survives any rescaling, but see §4 |
| `:169` | *"**Both are positive semidefinite**"* | a property of the new matrices. **Must be re-established from the new products; it does not survive by inheritance.** **OWNER: the GBDT/close-out lane**, which holds the covariance products — this lane does not have them and cannot check it. **The check is an eigenvalue computation on each of the two new matrices** (`numpy.linalg.eigvalsh`, assert `min(eig) >= -tol` with `tol` stated, since exact zeros are expected for a rank-deficient block). **If nobody runs it, the sentence must be deleted rather than carried** — an unverified PSD claim about a published covariance is worse than no claim |
| `:169-170` | *"neither is **adopted for publication** until the selection-complete lateral replacement lands"* | **This sentence must be DELETED OR REWRITTEN — not "updated".** It contains no number, so every number-oriented sweep skips it, and the natural move is to leave it and change the values around it: **that publishes an adoption while the prose still denies it.** There is no mechanical edit — **rewriting this sentence IS the act of asserting adoption**, so whoever rewrites it is making that claim and should be the party entitled to |
| `:170-173` | *"Repeating all 188 universe unfolds with per-universe background subtraction changes the combined block sqrt-trace by only `0.30%`"* | a **derived comparison against the old products.** `0.30%` is not a `\gbdtFive*` macro, so a macro-only edit leaves it stale and silently attached to superseded inputs |

**`0.30%` at `:171-172` is the one a macro-based search will miss entirely** — it is an inline literal, not a
macro, exactly the structural hole recorded for `\petRatio`'s operands.

## 4. The directional trap, and why no uniform factor works

Reported to this lane by the oversight session: **`\gbdtFiveMeanShift` moves UP ~13.6% while the other three
move DOWN ~9%.** Consequences, computed here:

    if the directions hold:  adopt ~5.29   cv ~5.68   meanshift ~1.87
    ordering CVTrace > AdoptTrace           PRESERVED
    meanshift / adopt   28.4%  ->  35.5%    a 25% RELATIVE change in that ratio

So: **anyone applying a single scale factor to all four gets the mean shift backwards.** And although every
*worded* claim above survives the rescaling, the mean shift grows from ~28% to ~36% of the covariance it is
*"reported separately rather than folded into"* — a material change in the qualitative picture that the
unchanged sentence will not convey. Whether that warrants a wording change is the writer's call; it should be
a *decision*, not an oversight.

## 5. The order to do it in

1. **Confirm the adoption exists** — the quarantine lifts only *"by adopting, in a commit that replaces the
   numbers"* (`VALIDATION_LEDGER.md`). A candidate magnitude is not an adoption.
2. **Add provenance to `values.tex:57-60`** — artifact path plus the derivation, per §2.
3. **Re-check every row of §3** against the new products, in order. The PSD claim and the *"neither is adopted"*
   sentence are the two that cannot be checked arithmetically.
4. **`grep` the new values against whatever file you cite**, per BEN-087.
5. **Handle `0.30%` at `:171-172` explicitly** — it is not a macro and will not be found by a macro sweep.
6. **Remove the four rows from `INDEX-retracted-and-superseded-values.md`** and say in the commit that they were
   removed because the adoption landed. A dead-value index that still lists live values trains its reader to
   discount it, the same failure recorded for `BLOCKED-ON-USER.json` (BEN-085).
7. **Re-check `docs/INTEGRATION_CHECKLIST.md:61`**, whose struck entry names these two scales and says
   explicitly that no replacement is written *"on purpose"*. That sentence becomes wrong once one is.

## 6. What this procedure does not cover

The `(E_avail,W)` covariance rows and the 4D/5D/FPS unified-throw adoptions are in the same quarantine class and
are **not** enumerated here — I have not sourced their consumption sites, and listing them from the class
description is the defect the index exists to prevent.
