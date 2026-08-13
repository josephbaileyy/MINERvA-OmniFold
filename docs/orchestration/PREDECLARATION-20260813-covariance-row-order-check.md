# PREDECLARATION 2026-08-13 — the diagonal-vs-central row-order check

**Written and committed BEFORE the check is run.** Nothing here was chosen after seeing a number.
The previous mapping test's ordering slipped and cost the *status* of a correct answer; this one is
predeclared in the tree so that cannot recur.

## The residual being tested

D found, and the mediator confirmed, that **nothing verifies that the covariance matrix's ROW ORDER
matches the mask's enumeration.** The only binding is `p4_lib.py:1300`:

```
require(M.shape[1] == C_high.shape[0], f"M cols {M.shape[1]} != C dim {C_high.shape[0]}")
```

**A shape check cannot see a permutation.** Under a consistent row+column reordering `P C Pᵀ`:
`trace`, `sqrt_tr_old`, `sqrt_tr_new` and the multiset of diagonal entries are all preserved
**exactly**, the shape check passes, and per-bin assignment is destroyed with nothing looking at it.

**Two things that must NOT be cited as covering it — BOTH CORRECTED 2026-08-13 after D read the
source and Session A verified it. My first version was wrong about both, and in each case the accurate
version is the more useful defect.**

**1. The `:1298` docstring — a says-vs-read gap, NOT a false assertion.** I called
*"(preserves density/order)"* a prose claim the code does not verify. **D's correction: the sentence is
arguably TRUE.** Read in full — *"5D->4D (or any) projection C_low = M C_high M^T (preserves
density/order)"* — it is a true statement about **the operation**: `M C Mᵀ` does preserve the ordering
of the output relative to `M`'s rows. **A reader takes it as a claim about the INPUT.** That is a
different and harder defect than a wrong assertion, because **auditing it for truth returns "true."**
It also changes the fix: framed my way, someone reworks a sentence that is not wrong; framed
accurately, **order-of-input is simply nowhere claimed and nowhere checked, and a docstring is not
where that belongs.**

**2. `check_projection_validity` (`:1318`) DECLARES ITS OWN BLINDNESS, so nothing in it needs
changing.** I implied it can be mistaken for coverage. Its first line, verbatim:

> *"GATE: the projection itself is valid. Recomputation identities only -- nothing here compares
> against an independently-produced product."*

It states precisely, in advance, that it is not the thing someone would cite it as. **The real risk is
that someone cites it WITHOUT OPENING IT** — `BEN-172`'s mechanism, a citation resolving to a real,
true, plausible thing that stops the reader. Third appearance tonight. The saving property: **such a
citation is refutable by reading the function**, because its own docstring disqualifies it.

**And it carries a second assertion I originally omitted (`:1330-1338`)**, which a reader will find and
must not mistake for coverage either: it recomputes `M C Mᵀ` by **independent row-block accumulation**
and requires agreement to `1e-9`. That is a genuine check, not a restatement — its docstring explains
that a bug in `project()` would still yield a symmetric PSD matrix. **It is nonetheless blind to THIS
failure**, because both routes consume the same `C` and the same `M`, so a permuted `C` produces the
same wrong answer twice and the identity holds exactly.

**Noted while reading: `crosscheck_marginal_vs_independent` (`:1343`) is `REPORT ONLY -- no pass/fail,
by specification`.** It is the 5D-vs-independent-4D comparison this session performed by hand as the
volume-weighting check. Worth knowing it exists and that it gates nothing.

**Why materiality does not cover it, which is where D declined the mediator's reading:**
promote-on-margin absorbs a small shared convention error — 4.4× is ample. It does **not** absorb a
permutation, because **a permutation preserves the SCALE of the projected uncertainty while destroying
its per-bin meaning.** The marginal lands plausibly inside 4.4× and is wrong anyway.

## The instrument, and why it is a third one

Correlate the covariance **diagonal** against the **central values**, bin by bin, over the 10,694
reported bins. The central values are a **third instrument**, distinct from both the mask and the 4D
chain used in the earlier checks — and they are themselves pinned (`p4_evidence.py:409`,
`central5d_sha256 == OBS["central5d"]`), so the instrument is not floating.

## PREDECLARED EXPECTATIONS — stated before the run

Let `s_i = sqrt(diag(C))_i` and `x_i = |central_i|` over the reported bins, and
`f_i = s_i / x_i` the per-bin fractional uncertainty.

**Statistic 1 — Spearman rank correlation `rho(s, x)`.**
- **Correct order: `rho > 0.90`.** Cross sections span orders of magnitude across the 5D grid and the
  per-bin fractional uncertainty is O(10%) with limited spread, so `s` must track `x` near-monotonically.
- **Permuted: `|rho| < 0.05`.** Pairing `s` with unrelated `x` destroys the rank relation; for
  n = 10,694 the sampling scatter on a null correlation is ~1/sqrt(n) ≈ 0.01.

**Statistic 2 — the median of `f`, against an independently recorded number.**
- **Correct order: `median(f)` reproduces the ledger's recorded per-bin median to within ~1 percentage
  point.** `uq_universe_5d_summary.txt` records `combined ... median rel=13.432%` over these 10,694
  bins, and `VALIDATION_LEDGER.md:1043` records `13.69%` over the 10,550 PET-common subset. This is
  the strongest arm: it is a match against a number written by a different producer at a different
  time.
- **Permuted: `median(f)` moves off that value and need not stay near it.**

**Statistic 3 — the SPREAD of `f`, which is the sharpest discriminator.**
- **Correct order: `f` is tightly clustered** — predeclared as `IQR(f) / median(f) < 1`, i.e. the
  interquartile range is smaller than the median itself.
- **Permuted: the spread explodes over orders of magnitude**, because `x` spans orders of magnitude and
  `s` is then paired with the wrong scale. Predeclared as `IQR(f)/median(f) > 3`.

## POSITIVE CONTROL — mandatory, not optional

A random consistent permutation `P C Pᵀ` will be applied and all three statistics recomputed.
**If the control does NOT collapse on all three, the check is not discriminating and the result is
VOID — not a pass.** Same rule as the amended mapping test: an exclusion or a statistic that cannot
fail proves nothing.

## ADJUDICATION, fixed in advance

| outcome | ruling |
|---|---|
| control collapses on all three AND real order passes all three | **ROW ORDER CONFIRMED** |
| control collapses AND real order fails any one | **REFUTED** — report raw, do not reinterpret |
| control does NOT collapse on all three | **VOID** — the statistic lacks power; needs a different instrument |

**Do not renegotiate these thresholds after seeing the numbers.** That is what writing them first is
for. D adjudicates; a disagreement goes to the mediator and is not resolved by either party alone.

## Scope

This tests **row order only**. It does not revisit the axis assignment (closed by the amended mask
test) or the volume weighting (closed by the 4D cross-check). A pass here would license `22.7%` for
**per-bin** use; without it, `22.7%` remains scoped to the aggregate order-of-magnitude materiality
question it was computed for, per D's ruling `9a84b6d`.

---

# RESULT — run 2026-08-13 after the above was committed at `3de5143`

**VERDICT: ROW ORDER CONFIRMED.** All three predeclared thresholds met on the real order; the positive
control collapsed on both statistics required of it.

| statistic | real order | control (`P C Pᵀ`, seed 20260813) | predeclared threshold |
|---|---|---|---|
| S1 Spearman `rho(sqrt(diag), \|central\|)` | **+0.9947** | **−0.0106** | >0.90 / \|rho\|<0.05 |
| S2 median `frac` | **13.761%** | 14.746% | within 1 pp of 13.432% |
| S3 `IQR/median` | **0.770** | **279.5** | <1 / >3 |

`n = 10,694` both arms. S2's real value **13.761%** sits 0.33 pp from the `13.432%` written into
`uq_universe_5d_summary.txt` by a different producer at a different time — the third-instrument anchor
the check was built around.

## THREE THINGS THE RUN EXPOSED THAT THE VERDICT DOES NOT CARRY

**1. S2 HAS ALMOST NO DISCRIMINATING POWER AND MUST NOT BE REUSED AS A ROW-ORDER TEST.** The control's
median `frac` came out at **14.746%** against the real **13.761%** — it barely moved. A median of a
ratio is robust to permutation when both distributions have similar medians, so **S2 would have passed
a permuted matrix.** The predeclaration did not require S2 to collapse (it says the permuted median
"need not stay near it"), so the adjudication is unaffected — but that was foresight, not margin.
**S1 and S3 carried this result alone.** Anyone reusing this check should keep S2 as an *anchor* to an
independently recorded number and never as a discriminator.

**2. My invariant check was malformed, for the third time tonight.** I compared
`np.trace(C)` against `d_perm.sum()` with exact equality and it printed `False` — but the two sum in
different orders, so bitwise equality is not expected and the comparison was meaningless. The
meaningful invariant, `sorted(diag) identical`, returned **True**, which is the one that actually
demonstrates why trace-based checks cannot see a permutation. **This is my third exact-equality-on-
floats error in one session** (after the projected-covariance symmetry check, and the same construction
again). Recording it as a personal pattern rather than three isolated slips: I reach for
`rtol=0, atol=0` when I mean "should be identical," and for a float reduction that is almost never the
right test.

**3. ~~The real-order fractional uncertainty spans 3.47% to 213.8%~~ — SUPERSEDED 2026-08-13, and the
span was the wrong shape of answer.** A span is a **max-shaped summary**: it says extremes exist and
nothing about how much of the deliverable they are. `crosscheck_marginal_vs_independent`
(`p4_lib.py:1350-1351`) already refuses exactly this, verbatim — *"returns the full distribution rather
than a max, because on the real products the max is owned by a handful of near-empty bins and is
actively misleading about the body of the comparison (BEN-064)"* — and `BEN-064` reads *"a `max`-shaped
guard lets its worst bin choose the headline, and five numerically irrelevant bins hid a 62% failure."*
**The codebase had already solved this and I re-derived a worse answer.** Replaced below with the
distribution, per that convention.

### Per-bin fractional uncertainty — the distribution

| percentile | frac |
|---|---|
| p1 | 4.757% |
| p5 | 6.417% |
| p10 | 7.620% |
| p25 | 10.125% |
| **p50** | **13.761%** |
| p75 | 20.726% |
| p90 | 34.992% |
| p95 | 53.637% |
| p99 | 88.125% |
| p99.9 | 140.422% |

**Count share vs WEIGHT share — the distinction a granularity decision actually turns on.** Weight is
`central × cell-volume`, i.e. the bin's contribution to the integrated cross section (the stored
central is a density), total `3.069928e-38`:

| frac threshold | n bins | % of bins | **% of integrated xsec** |
|---|---|---|---|
| >25% | 1,959 | 18.319% | **2.018%** |
| >50% | 634 | 5.929% | **0.510%** |
| >75% | 185 | 1.730% | **0.068%** |
| **>100%** | **56** | **0.524%** | **0.0486%** |
| >150% | 8 | 0.075% | 0.00051% |
| >200% | 2 | 0.019% | 0.00009% |

**The >100% set is 56 bins of 10,694 carrying 0.0486% of the deliverable.** Their central values run
`1.335e-48` to `6.475e-39`, and their median central is **0.59×** the median over all reported bins —
so they are genuinely the near-empty tail `BEN-064` describes, not a broad problem. **18.3% of bins
exceed 25% fractional uncertainty while carrying 2.0% of the cross section**, which is the same lesson
one threshold down: numerous in count, negligible in weight.

**WHERE THEY LIVE, and this one is worth Joseph's attention rather than mine.** The >100% bins are not
uniform across the `E_avail` axis:

| E_avail bin | n>100% | n reported | % of slice's bins | **% of slice's xsec** |
|---|---|---|---|---|
| 1 `[0,0.1)` | **28** | 2,023 | 1.384% | **0.707%** |
| 2 | 7 | 2,003 | 0.349% | 0.00047% |
| 3 | 14 | 1,993 | 0.702% | 0.00147% |
| 4 | 5 | 1,822 | 0.274% | 0.00008% |
| 5 | 2 | 1,377 | 0.145% | 0.00003% |
| 6 | 0 | 961 | 0% | 0% |
| 7 | 0 | 515 | 0% | 0% |

**Half of them (28 of 56) sit in `E_avail` bin 1, and they carry 0.707% of that slice's cross section —
15× the global 0.0486%.** Bin 1 is also where the pion-mass shift is largest (`+1.049%`). Flagged
because it is the one place the two questions touch; **not adjudicated — that is the granularity call
routed to Joseph.**

**D's standing requirement, which holds whichever way that call goes: a per-bin number must not travel
without its own fractional uncertainty.**

## What this licenses

Row order is now checked by an instrument (**central values**, pinned at `p4_evidence.py:409`) distinct
from both the mask and the 4D chain. Together with the amended mask test (axis assignment) and the 4D
cross-check (volume weighting), the three residuals D and the mediator named are each closed by a
different instrument. **D HAS RULED (`19b68c4`), IN TWO PARTS THAT MUST NOT BE MERGED INTO ONE WORD:**

1. **The per-bin VERIFICATION gate LIFTS.** Residual 2 is closed; nothing in the verification blocks
   per-bin use. All three residuals are closed by three different instruments, and on correctness this
   is as independent as the artifact admits.
2. **Whether per-bin is the right GRANULARITY is not a verification question and D is not deciding
   it.** Above 100% the central is roughly consistent with zero, and quoting such a bin invites a
   reader to treat it as measured. That is a physics call, routed to Joseph, **not decided tonight.**

**So: verification PASSES, granularity is ROUTED. "Per-bin is cleared" is NOT the ruling.** Folding
part 2 into part 1 would decide a physics question invisibly inside a verification pass.
