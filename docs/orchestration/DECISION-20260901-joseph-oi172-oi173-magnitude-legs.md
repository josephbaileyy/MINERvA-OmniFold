# DECISION 2026-09-01 — Joseph rules `OI-172` and `OI-173`: the two magnitude legs

**CITABLE FOR:** the two rulings below and their stated consequences.
**NOT CITABLE FOR** discharging any cause, adopting any covariance, moving any gate, or altering
`values.tex`. Gate 2 remains **FAIL**. Counts hold at CAND `1 of 7`, QUOTED `0 of 7`.

## Authority, and exactly what he said

Joseph, 2026-09-01, in his own turn, directly to this lane — **not relayed, not inferred**:

> *"Okay I agree with your recommendations, I authorize you spend the hours and drafting to
> investigate and fix the causes"*

**The recommendations he agreed to are this lane's, and they are restated verbatim below so that no
future reader mistakes this lane's reasoning for his.** He adopted conclusions; the arguments under
them remain this lane's and are open to challenge on their merits.

Both rows were owned by *"Joseph / the delegated authority"* precisely because each is a judgement
rather than a computation, so this closes the ownership question as well as the substance.

## RULING 1 — `OI-172`, cause 1's magnitude

The question, verbatim from `DETERMINATION-20260817-cause1-census-and-magnitude-measured.md` §6:

> *"Does a `+3.1%`/`+5.9%` √Tr difference with a `1.7–2.0×` median per-band ratio constitute `M` MET
> under §0's 'measured, not necessarily small' rule — or does a difference this size mean the
> construction choice is material enough to need its own statement in the note?"*

> **RULED: MATERIAL ENOUGH TO NEED ITS OWN STATEMENT IN THE NOTE.**
>
> **CAUSE 1 THEREFORE DOES NOT CLOSE, AND THE NOTE ACQUIRES A NEW OBLIGATION.** This is the
> unfavourable branch of the two, and `OI-172` named it first for exactly this reason.

**The recommendation he agreed to, restated as it was put to him.** Three grounds, all measured from
the determination rather than from the row's summary of it:

1. **The total is small only because of aggregation.** √Tr moves `3.1%`/`5.9%` while the per-band
   ratio distribution runs median `2.0261`, p75 `2.6318`, **p90 `4.3256`, max `5.8024`**. A released
   covariance exists so consumers can use its per-band structure; a 2× median band movement is not
   made immaterial by cancelling in the trace.
2. **The effect changes sign.** The determination's own `:98-99`: *"one-sided overstates is true in
   aggregate and NOT universally"* — `MaCCQE` ep0 `0.6377` and `MaRES` ep1 `0.6111` are **understated**.
   A consumer assuming conservatism is wrong on those bands.
3. **The measurement backing a "MET" is itself partial** — diagonal-only by sufficiency, off-diagonal
   never compared, and the counterfactual excludes `Flux` (N=100), `2p2h` (N=3) and
   `__Normalization_flat`. Declaring a structure question settled on a diagonal-only comparison is
   weak.

**What this does NOT decide:** the wording of the note statement, where it goes, or whether it changes
any published number. Those are drafting decisions downstream of this ruling.

## RULING 2 — `OI-173`, cause 4's magnitude

The question: what does `M` mean when the defective construction was never applied to the artifact's
stored inputs? Measured basis, from the row: the retired `jit_trace` deflation reached exactly one
class of object — **reported prose ratios** — of which the recorded 5D value is the `1.539` at
`VALIDATION_LEDGER.md:1158-1159`. `--out-root` stored the **raw** values, `adopt_unified_5d.py` reads
only `diag(C_unified)`/`diag(C_blocksum)`, and `git log --all -S "sqrt_tr_unified" --
nd-unfolding/adopt_unified_5d.py` returns **zero** commits against a working positive control.

> **RULED: SPECIFY `M` AGAINST THE CLASS OF OBJECT THE DEFECT ACTUALLY REACHED — the reported ratio —
> NOT against the stored covariance.**
>
> **AND IF THE PRINTED `jit_trace` VALUE IS NOT RECOVERABLE FROM COMMITTED BYTES, `M` IS `NOT MET`
> — UNMEASURED — RATHER THAN `N/A`.** That is the correct outcome under this specification, not a
> failure of it.

**Why the specification is chosen this way**, as it was put to him: it follows the precedent
`SCOREBOARD` §2c set by CHOOSING a specification, under that section's own rule — ***do not let
measurability choose the specification***. Fixing the referent first and discovering afterwards
whether it is measurable is the order that keeps the criterion honest.

**AND IT DELIBERATELY DECLINES THE AVAILABLE SHORTCUT**, which `OI-173` named so that nobody would
take it silently: *"the subtraction never touched X, so cause 4 is `N/A` for X on the merits"* is
available and superficially resembles the move that settled cause 5. It is refused. Cause 5's `N/A`
rested on a traced construction path with a named falsifier; this would rest on X's inputs being
pre-deflation — **a claim about how X was built rather than about whether cause 4's defect is on its
path.** An argument whose payoff is its own premise belongs nowhere near a discharge.

**This row does not authorize a recomputation.** `jit_trace` is a one-sample estimate of a variance
whose expectation the source itself writes as `E‖x_cv2 − x_cv1‖²`, so a re-run is a different draw.

## What this decision does not do

It discharges nothing. Cause 1 explicitly does **not** close under Ruling 1. Cause 4's `M` becomes
*specified* rather than *satisfied*, and may well grade `NOT MET`. No covariance is adopted, no gate
moves, `values.tex` is untouched, and the counts are unchanged. Cause 3's `M(ii)` and cause 7's
missing criteria are separate work authorized in the same turn and are predeclared separately.
