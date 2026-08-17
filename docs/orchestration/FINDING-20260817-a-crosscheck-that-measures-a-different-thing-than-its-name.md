# A cross-check reported as estimator disagreement that identically measures a support mismatch

**Filed 2026-08-17 by the executor (`Assistant`) lane.** Row: `BEN-319`. Found while answering Joseph's
question *"is the stage-6 marginal-vs-direct disagreement mathematics or a defect?"* — the answer is
**neither as posed**, and the reason is this finding.

**The physics is sound, the projector is exonerated at `3.1e-16`, and the convention is intact.** What is
defective is what the number is *called*.

---

## 1. The number, and what it is reported as

`p4_project_4d.py` prints, and the manifest records:

```
[xcheck] marginal vs INDEPENDENT 4D (no pass/fail, cross-check only):
  n=4825  median=0.0443  p90=0.2083  max=0.7285  over3%=3009  integral_ratio=1.005578
```

Read as it is written, that says **two estimators of the same quantity disagree by a median 4.4%, with
3009 of 4825 bins over 3% and a worst bin at 72.9%** — while their integrals agree to 0.56%. That is a
physics discrepancy, and it is how the question reached this lane: as a question about whether unfolding
and marginalization commute.

## 2. What it identically measures instead

```
frac_seen[r]  =  sum(reported 5D hUnfoldND over the W bins of column r)  /  (4D hUnfoldND in r)

max | rel - (frac_seen - 1) |  =  1.187e-14        against  max|rel| = 0.7285
median | rel - (frac_seen - 1) |  =  1.804e-16
```

**The cross-section conversion cancels exactly.** The comparison is the per-column *unfolded-content
ratio* minus one, to machine precision, and carries no information beyond it. `corr = 1.000`, checked
**algebraically** rather than relied on — a correlation of 1 can still hide an offset, and this one does
not.

**So the quantity is not a disagreement between two answers about the same content. It is a statement
about how much content each product covers.**

```
W-coverage of the 5D reported support per 4D column:  median 0.333, fully covered 3.56%
                                                      -- a typical column reports 2 of its 6 W bins

commensurable subset (frac_seen within 1% of 1):  n=702 of 4825 (14.5%)
                                                  median |rel| = 0.00449   p90 0.00887   max 0.00999
```

**Where the two products cover the same content they agree to `0.45%` median and never exceed `1.0%`.**

## 3. Why this is a defect and not merely imprecise wording

**Because the reported framing licenses a conclusion the measurement does not support, and it did.** The
mediator handed this to a lane as a physics question with three candidate mechanisms — nonlinearity of
the iterative update, prior-weighted response collapse, and regularization mismatch — all of which are
about *marginalization*. None is the driver. One table ends all three:

| reported W bins feeding the column | n | median \|rel\| |
|---|---|---|
| **1** | 1309 | **0.0572** |
| 2 | 2036 | 0.0519 |
| 3 | 1027 | 0.0363 |
| 4 | 205 | 0.0215 |
| 5 | 76 | 0.0190 |
| **6** | 172 | **0.0264** |

**At `nW=1` the row of `M` has one entry: the "marginalization" is multiplication by a single width, and
no marginalization occurs. Those bins disagree the MOST.** A commutation effect must *vanish* where there
is nothing to marginalize; this one is maximal there. **That is the wrong sign of dependence, which no
coupling strength can repair.**

**The cost of the mislabel was a whole hypothesis space aimed at the wrong question**, and the reader who
was misdirected is the campaign's most careful one. A number whose name implies the wrong referent does
not fail loudly — it fails by being investigated.

## 4. The convention is intact, and its wording needs one correction

`crosscheck_marginal_vs_independent`'s docstring is **right** that this is *"a cross-check between two
DIFFERENT estimators, not a consistency requirement"* and that the marginal is the deliverable. Retiring
the `3%` gate on 2026-08-09 was correct: **bin-by-bin equality was never a coherent requirement between
two products on different supports.**

**The correction is to what the number is a property OF.** The docstring says the comparison
*"characterises the independent unfold."* It does not. It characterises **the support difference between
the two products** — a third thing, belonging to neither estimator. Attributing it to the independent
unfold overstates what it says, and that attribution is what invites the next reader to re-ask this
question.

## 5. The fix, which this lane did not implement

**Report `frac_seen` alongside the summary, or restrict the quoted summary to the commensurable subset.**
Either makes the number mean what its name implies. Not patched: repair-12 was under verification by this
same lane when this was found, and **the lane that verifies a gate should not also be editing the module
under it.**

## 6. What is NOT resolved, stated so it is not read as closed

`frac_seen > 1.01` in **1876 of 4825 columns (39%)** — the summed *reported* 5D content **exceeds** the 4D
content there, which *"the 5D reports a subset"* cannot explain. **So the well-posed question survives:
why do the two unfolds distribute content differently across columns, given different supports?** That is
where mechanisms (1) and (3) could legitimately live. It is smaller and better posed than the question
this lane was handed, and **saying so is not a claim to have answered it.**

## 7. Cross-reference

- `BEN-064` — the convention this confirms; §4 corrects one clause of its wording, not its substance.
- `BEN-316` — a check whose two sides share the thing it claims to test. **The same shape appeared in this
  lane's own instrument while producing this finding:** a completeness probe returned exactly `0.0000` on
  all 4825 bins, which is the signature of an identity rather than an agreement, and three weightings —
  including uniform — all gave `~1e-14`. **A quantity that does not move when you change its own weights
  is not measuring the weighting.** The failed probe's real content: completeness has **no W-dependence**
  within a column, so mechanism 2 via efficiency is *structurally absent* rather than small.
- `BEN-300` — two views of one measurement is not corroboration. Applied against this lane's own evidence:
  a "|rel| grows with W-shape concentration" result was withdrawn on noticing its top quartile
  `[1.00,1.00]` was exactly the `nW=1` bins.
- `BEN-025` — realized exceedance rather than a fitted tail. The noise hypothesis was excluded by data:
  flat across cross-section quartiles, and `|rel|>10%` bins **3.6× brighter** than typical.
- `BEN-077` — a receipt whose numbers cannot contradict each other is unfalsifiable. The identity in §2 is
  what makes this one falsifiable: `rel` and `frac_seen` are published together and must agree.
