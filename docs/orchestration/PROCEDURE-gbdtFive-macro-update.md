# PROCEDURE — updating the four `\gbdtFive*` macros when the J28 re-roll is adopted

**Written cold, 2026-08-11, before the adoption and before the edit.**

> **STATUS, CORRECTED 2026-08-11 — read §4a FIRST.** An earlier revision of this header said Packet B's
> closure made the adoption gate "actionable rather than blocked". **That was my error and it is withdrawn.**
> Packet B (`1440b58`) verified the pipeline and J28 fixed the flux defect; the binding gate is the
> 2026-07-12 quarantine, of whose **seven** construction causes exactly **one** is discharged. This is a
> contingency again, not a procedure about to be used. Nothing below authorizes an edit.

Re-read §3 and §5 before editing, and note that two of the six rows (PSD, and the "neither is adopted" sentence) cannot be discharged by arithmetic at all. BEN-087 says attributions must be
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

> ### ⚠ THE PARAGRAPH ABOVE IS WRONG, corrected 2026-08-11 by the uncertainty-construction lane
>
> *"No source claim can be silently re-pointed"* is false for this block, and the search that produced it
> is why. The keyword list — `from`, `summary`, `rollup`, `artifact`, `ledger`, `taken`, `\ref` — is a list
> of ways to cite **a file**, and it was run correctly and found none. But `sec_systematics.tex:162` reads:
>
> > *"the **background-aware** block sum has median per-bin uncertainty `\gbdtFiveBlockMedian`"*
>
> **That is an attribution — to a SAMPLE AND A FOOTING rather than to a file.** So is `:170-173`'s
> *"Repeating all 188 universe unfolds with per-universe background subtraction changes the combined block
> sqrt-trace by only `0.30%`"*. Both name the population the number came from, and **no filename-shaped
> search can see either.**
>
> This is live, not theoretical. The J28 replacement pair `5.2600e-38` / `5.6609e-38` is footed on the
> **non**-background-aware sweep (block sum `4.3455e-38`, median `13.432%`), while the values it would
> replace, `5.81e-38` / `6.24e-38`, are **background-aware** (`4.3578e-38`, median `13.359%`) — because
> `sbatch_j28_adopt_5d.sh` never passes `--combined` and `adopt_unified_5d.py:76-77` defaults to the
> non-bkgaware product (`grep -n -- '--combined' nd-unfolding/sbatch_j28_adopt_5d.sh` returns nothing).
> **Writing the J28 pair under the sentence at `:162` would make that sentence false**, which is exactly
> BEN-087's trap, in exactly the block BEN-087(iii) named as the forward-looking instance — reached by a
> carrier §2 was not looking for. BEN-102.
>
> **Consequence for §4's table, and it inverts this document's advice on the fourth macro:**
> `\gbdtFiveBlockMedian` `13.36` **is** the background-aware median `13.359%` (committed at
> `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt`, and `VALIDATION_LEDGER.md:333`);
> its non-bkgaware counterpart is `13.43`. So the four macros are **not** "three that change and one that
> holds" — that is the reading to guard against. Either the three are re-derived on the bkgaware footing, or
> the fourth changes too. See the footing note beside the J28 table in `VALIDATION_LEDGER.md`.
>
> **The rule this yields, which is the part worth carrying past this document:** an attribution search must
> cover **populations, footings and samples**, not only filenames, citations and `\ref`s. Grepping for
> citation *verbs* finds attributions to artifacts; attributions to **which data** are made with ordinary
> adjectives — *background-aware*, *selection-complete*, *full-event*, *recoil-only*, *five-band* — and are
> invisible to that search while being every bit as falsifiable by a value swap.

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

**CORRECTED 2026-08-11 by the oversight session, against its own numbers.** This section previously carried
*estimates* I had relayed to this lane (*"adopt ~5.29 cv ~5.68 meanshift ~1.87"*, derived from "~9% down /
~13.6% up"). **The exact values already exist in `VALIDATION_LEDGER.md` and should be read from there, never
from this table** — an estimate standing where an authoritative value exists is how a near-right number gets
written into a paper. The ledger states the mapping explicitly: *"the corrected totals are ~9% SMALLER than
the values currently in `values.tex`."*

| macro | current `values.tex` | corrected (ledger, full-160) | change |
|---|---|---|---|
| `\gbdtFiveAdoptTrace` | 5.81e-38 | **5.2600e-38** (mean-centered combined) | −9.47% |
| `\gbdtFiveCVTrace` | 6.24e-38 | **5.6609e-38** (CV-centered combined) | −9.28% |
| `\gbdtFiveMeanShift` | 1.65e-38 | **1.878696733368378e-38** (`joint_mean_shift_norm`) | **+13.56%** |
| `\gbdtFiveBlockMedian` | 13.36 | **ESTABLISHED AS A DIFFERENT QUANTITY, 2026-08-11 — this row previously read "not established as the same quantity", which was too weak.** `13.36` **is** the **background-aware** syst+stat+ML block-sum median `13.359%`, committed at `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt` and at `VALIDATION_LEDGER.md:333`; the note's own prose at `sec_systematics.tex:162` says *"the background-aware block sum"*. The ledger's `13.43%` is **the same quantity on the NON-bkgaware sweep** (`…/universe_stage2_5d/uq_universe_5d_summary.txt`, `median rel=13.432%`). **So this macro is not one that can be left alone while the other three change** — the three replacements are non-bkgaware and this value is bkgaware. See the §2 correction box and BEN-102 | **depends on the footing decision, not on J28** |

Recomputed from the exact values rather than the estimates:

    ordering CVTrace > AdoptTrace     5.6609 > 5.2600     PRESERVED
    meanshift / adopt      28.47%  ->  35.72%             a 25% RELATIVE change in that ratio

So: **anyone applying a single scale factor to all four gets the mean shift backwards** — it is the only one
that rises. And although every *worded* claim in §3 survives the rescaling, the mean shift grows from ~28% to
~36% of the covariance it is *"reported separately rather than folded into"* — a material change in the
qualitative picture that the unchanged sentence will not convey. Whether that warrants a wording change is the
writer's call; it should be a *decision*, not an oversight.

**§3's PSD row is already discharged in the ledger, so do not re-derive it as if open:** the J28 section states
*"both are PSD"* for the two conventions, and the five-band lateral entry records p4 validation `RESULT PASS`
with `PSD (min/max eig −3.87e-16)` on 266×266. That does **not** remove the §3 obligation — those are the
*current* products, and PSD must be re-established for whatever is finally adopted — but the check has been run
once and the owner should start from that result, not from zero.

## 4a. THE BINDING GATE IS NOT J28 AND NOT PACKET B — corrected 2026-08-11

I told Joseph that Packet B closing (`1440b58`) made this adoption *actionable*. **That was wrong, and it is
the correction that matters most in this document.** Packet B verified the *pipeline*; J28 fixed the *flux
defect*. Neither is what gates these four macros.

The gate is the **2026-07-12 uncertainty-remediation quarantine** (`VALIDATION_LEDGER.md:60-88`), which names
**seven** construction causes:

    1. one-sided endpoint interpolation          OPEN
    2. CV centering                              OPEN
    3. varying estimator seeds                   OPEN
    4. scalar jitter subtraction                 OPEN
    5. frozen PET weights                        OPEN
    6. incomplete statistical projection         OPEN
    7. CV-support-limited lateral selection      DISCHARGED 2026-08-07 (five-band FPS active lateral,
                                                 job 56431823, gate chain PASSED)

**One of seven.** And the ledger forecloses the inference I made, in its own words: the lateral replacement
*"discharges the specific precondition this paragraph named … it does **not** by itself lift this quarantine,
whose other listed causes and whose PET / 4D-FPS / significance scope are untouched, and **no scale in this
section becomes quotable on the strength of it**."* The lateral entry's own Scope repeats it: *"The 2026-07-12
quarantine above is not lifted by this entry."*

**Consequence for anyone reaching this document expecting to adopt:** you cannot, and no verification pass
changes that. A PSD re-check, a seed ensemble, or an independent re-roll would all pass and none of them
touches causes 1–6. The distance to adoption is six remediations, not a job submission. **This procedure stays
valid and stays unused until they are closed** — which is the right state for it to be in, and better than
discovering the gate after the macros were edited.

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
