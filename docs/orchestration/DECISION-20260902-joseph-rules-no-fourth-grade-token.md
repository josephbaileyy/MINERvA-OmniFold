# DECISION 2026-09-02 — Joseph rules that `CRITERIA` §0's grade vocabulary is NOT extended: no fourth token

**CITABLE FOR:** the ruling in §1, the census numbers in §2, and the two deferrals in §4–§5.

**NOT CITABLE FOR:** a grade on any leg; discharge of any cause; a change to either quarantine count;
a Gate-1 or Gate-2 clause; adoption; a change to `values.tex`; resolution of the scope question in §4;
or repair of the defect in §5. **Gate 2 remains FAIL. CAND `1 of 7`, QUOTED `0 of 7`.**

## 1. The ruling

Joseph, 2026-09-02, in his own turn, on this lane's recommendation against a fourth grade token:

> ***"okay I also agree"***

**Those are his words.** Everything else here is this lane's drafting.

> **`CRITERIA-20260811` §0's vocabulary — `MET` / `OPEN` / `UNRESOLVED`, discharge on four `MET`s —
> STANDS UNCHANGED. No token is added for the *permanently unmeetable* state.** The annotation
> convention already in use carries that state in cell prose instead.

## 2. WHAT DECIDED IT — a census, run before the ruling rather than after

The question was put the other way round at first: the `minerva-omnifold-38` lane offered enumeration
as the **cost** of ruling for a fourth token. It was re-framed as the **input** to the ruling, on the
ground that the case for a token is empirical, and Joseph took that framing. Census filed by that lane
at `0d946c1a`, amended at `ac846f37`; **verified against the bytes by this lane**, including the
column mapping, every hit, both exclusions and the denominator.

| quantity | value |
|---|---|
| denominator: graded (cause × leg × artifact) cells | **46** (rows 63–85 × two artifact columns) |
| bucket (i): permanence asserted **and carried in the cell** | **1** — `SCOREBOARD:78`, cause 4 `M` CAND |
| bucket (ii): permanence asserted, **cell reads bare** | **4** — `:68`, `:72`, `:73`, `:77` |

**The shape of the 4 is what defeated the token, not the count.** By the rule set in advance, 4 is
"several" and the token had an empirical case — and the census lane reported that plainly against its
own stated lean. But **all four are the same column under the same statement**: they are the QUOTED-side
`P` legs of causes 2/3/4, and the permanence is asserted at `SCOREBOARD:5`, in a warning box that
precedes every cell. **So the harm is grep-scale, not read-scale** — a top-to-bottom reader is not
misled, only a single-cell reader. **The population a fourth token would uniquely help, that nothing
else already covers, is ONE — and that one is already annotated.**

**The census's own negative control is the strongest evidence for the ruling:** `SCOREBOARD:74` reads
*"`OPEN` and NOT CURRENTLY MEASURABLE"*, costed at ~1 GPU-node-hour and temporary on its face. **The
board already distinguishes temporary from permanent in its own cell language**, which is the
annotation convention working without a vocabulary change.

**A correction to a number given to Joseph earlier:** the board runs **seven** distinct grade forms,
not six — `MET`, `OPEN`, `UNRESOLVED`, `PARTIAL`, `INAPPLICABLE`, `MEASURED`/`MEASURED-not-MET`, `N/A`.
Annotated `OPEN`s are not separate tokens; they are the convention working.

## 3. Why a fourth token was the wrong instrument even where the gap is real

**No code parses any of these tokens** — measured by the census lane — so a token buys convention, not
enforcement. The operational harm is a lane spending compute closing an unclosable leg, and on the one
known cell that is already prevented in prose. Discharge is four `MET`s under any vocabulary. And
adding a fourth token to a scheme that **declares three and runs seven** patches the smallest leak
while the larger one stands: **if §0 is ever opened, the better-motivated change is reconciling
declared-against-used**, which is a different act and not this one.

## 4. DEFERRED — the remedy is agreed in principle and NOT applied, for a reason found while applying it

The agreed remedy for bucket (ii) is a **pointer in each of the four cells** to `SCOREBOARD` §1's
column-level statement. It costs no `§0` change and Joseph agreed to it.

**It is not applied here, and the reason is that applying it would silently settle an open question.**
`SCOREBOARD:5` says ***"THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION"*** — on its face a claim about
the **whole column**, with an artifact-level mechanism (*"X predates the stamping… X gets replaced,
not repaired"*). Read that way it also reaches `:69` (cause 2 `M` QUOTED) and `:78`'s QUOTED cell
(cause 4 `M` QUOTED), both bare `OPEN`. The census scoped bucket (ii) to `P` legs, which is defensible
because the claim's evidence is entirely stamp-specific and stamps are the `P` criterion.

**Both readings are live. Annotating exactly the four `P` cells and not the two `M` cells would encode
the `P`-only reading into the board as a fact.** Resolving it means judging whether `M` is measurable
on X — a grade on a cause-4 leg, which `BEN-381` puts beyond both lanes that measured here.

> **Routed: a lane that took none of the deciding measurements should settle whether §1's permanence
> claim is `P`-scoped or column-wide. The pointers follow that, not the reverse.**

**It does not disturb §1's ruling.** At six hits rather than four the population is *more* uniformly
one column under one statement, so the argument against the token strengthens.

## 5. ROUTED, not filed — a live board asserts an impossibility that is not true

The census lane measured, as an exclusion rather than a finding, that `SCOREBOARD:73`'s premise —
*"value CANNOT be recorded on the dominant arm"* — is **FALSE at HEAD**, four write sites existing.
That cell is cause 3's `P-ii`, and the premise is load-bearing for its stated remedy.

**This belongs in its own route rather than an exclusions footnote**, and it is neither lane's to
repair: it is a third party's cell, and correcting it changes what a remedy costs.

## 6. What this does NOT do

It does not grade any leg, move any cell, discharge any cause, change either count, move any gate,
adopt anything, or touch `values.tex`. It does not resolve §4's scope question or repair §5's defect.
It does not reopen `DECISION-20260831`, whose §2(b) mechanism flag remains **surfaced, not filed**. The
**historical-ratio reading** for cause 4's `M` remains **undisposed**. And it authorizes no compute.
