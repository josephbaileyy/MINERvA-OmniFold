# V-HALF-R (#1016): the choices for Joseph (decision packet, 2026-11-10)

**By** the limitation-resolver lane, at the director's request on Joseph's go. This packet changes nothing in #1016's
declaration and ran no compute. It sets out each open choice in the declaration's §7, with options, trade-offs, a
recommendation and what the choice commits the follow-up paper to.

**Citations.** **D** is `v-half-r/DECLARATION.md` at #1016's head `b7d7ac2dc`. **A** is `v-half-r/consult-astra/answer.txt`
at the same head. **T3** is `fd/tier3-20261110/T3-PIPELINE-TESTS-DECLARATION.md` at #1038's head `cbb7278e5`. Other
paths are at main `88bf25892`, relative to `docs/orchestration/` unless they start with `nd-unfolding/` or
`docs/analysis-note/`.

## Summary

| # | choice | recommendation |
|---|---|---|
| 1 | the binning criterion and τ_R | min(purity, diagonal fraction) ≥ 0.5 (the draft recommends purity alone) |
| 2 | the candidate list | C0-C8 as drafted |
| 3 | the candidates the follow-up must include | C6 (p_T, p_∥) and C7 (E_avail, q3), if Joseph confirms C7's physics reason |
| 4 | the phase space | the 16-cell reported domain |
| 5 | the disclosure | the draft's text, plus one sentence on what else was known |
| 6 | whether the criterion is a final requirement | yes |
| 7 | the cancellation level for C1-C8 | fine cells (R-cells for C0) |

**When it runs.** Every choice above reads only simulation, so it can be decided now. The study itself (binnings,
grading and read) should run only after Tier 3 reports and Joseph has decided whether the estimator changes
(section "When it runs" below).

## What has changed since #1016 was drafted

1. **V-HALF's 16-cell result: 5 valid, 9 not valid, 2 unresolved** (`state/2d-closeout/valid-region-20261107/v-half/receipts/read/readout.txt:10`).
   - The draft's disclosure already states it (D:49-52).
   - Joseph has since put V-HALF into the methods paper as a diagnostic on R00-R15. He also resolved the rebinning
     question for that paper: there is none (`DECISION-20261110-joseph-paper-asap-vhalf-diagnostic.md:28-31`). V-HALF-R
     is follow-up work only.
   - **How it bears here.** The result is the reason the disclosure (choice 5) is required. This packet bases no
     recommendation on any cell's class.
2. **The referees on low-stability cells.** The confirming round's referee noted that R02 and R06 "are exactly the
   cells flagged at the GiBUU hybrid", and quoted the paper: "the cells are formed without a stability criterion." The
   referee added: "Rebuilding the cells with a stability criterion would cost little." The referee recommends this
   but does not require it
   (`state/2d-closeout/stageF/methods/secondary-results/referee-methods-confirm-20261110/claude.txt:174-176`).
   - The paper's "diagonal fraction" (`docs/analysis-note/paper_body.tex:50` at #977 `10b88ad9b`) is the quantity the
     draft calls stability: same / truth_reco (`nd-unfolding/pv-ladder/h2_definition.py:72`; D:102).
   - The H2 cells were merged on purity alone, at τ = 0.1 (`nd-unfolding/pv-ladder/h2_definition.py:7-8`, :35).
   - **How it bears here:** choices 1 and 6.
3. **T2A (#1041).** The director's reading is that the two-dimensional coverage test's bias sits in the poorly
   determined directions of C_T.
   - The receipt describes the split and names no cause (`state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2a/README.md:50-57`).
   - **How it bears here.** V-HALF-R's grading reads no covariance (D:184), so T2A changes no grading choice. It bears
     on a coverage test of any candidate reported as a measurement, C6 especially, because C6 has the same axes as the
     two-dimensional test (choice 3).
4. **T2B (#1039).** The director's reading is that the fake-data passes do not depend on C_model, cell by cell.
   - V-HALF reads F0b's bias and noise. It does not read F0b's grades or any covariance (D:157-168, :184), so T2B
     changes no V-HALF-R choice.
   - The per-candidate covariance (D §3) still includes C_model. T2B is not citable for C_model being redundant
     (`state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2b/README.md:34-35`).
5. **Tier 3 (#1038, rev 1, a draft).** Its corrected question is where configuration (e)'s retained prior stops
   falling, and which pipeline component sets that limit (T3:177-190).
   - A Tier 3 reading changes no estimator by itself. Adopting a changed arm would need Joseph's decision and its own
     held-out test (T3:40-42, :423-424). So Tier 3 can lead to a changed estimator.
   - V-HALF-R grades the reported estimator's bias. Its inputs are F0b's bias and noise, made from that estimator's
     unfolds, and FD-PRR's departures (D:165-172). A changed estimator changes those inputs.
   - **How it bears here:** the run order. It does not affect the choices, which read only simulation (D:84-90).

## The choices

### 1. The binning criterion and τ_R (D:96-103, :289)

| option | trade-offs |
|---|---|
| (a) purity ≥ 0.5 alone; diagonal fraction printed beside it (the draft, D:97-103; the consult, A:22) | one quantity, the same as H2's rule. A bin can pass with a low diagonal fraction, which is the property the referee named. |
| (b) purity ≥ 0.3 | keeps more, finer bins. It is further from "at least half", and it answers the referee less. |
| (c) min(purity, diagonal fraction) ≥ 0.5 | both fractions at least one half. Of the signal reconstructed in the bin, at least half was generated there. Of the signal generated there and reconstructed, at least half is reconstructed there. Bins come out coarser, and more candidates may fall below the minimum bin count. That outcome is known from the binning alone, before grading (D:202). |

**Recommendation: (c) at 0.5.**
- It answers the referee's remark (claude.txt:174-176) for every candidate, and it uses a single threshold. The
  consult's objection was to adding another adjustable acceptance rule (A:22). Option (c) adds no second number.
- The join step should use the same quantity: take the bin with the lowest min(purity, diagonal fraction), and merge
  it with the neighbour whose union has the highest value. This replaces the purity ordering at D:91-92, so §1.2
  would need amending.
- 0.5 remains a design convention. It is not shown to guarantee a valid unfolding (D:98-100). It was chosen after the
  V-HALF classes and the referee's remark were known, and the disclosure says so (choice 5).

**It commits the follow-up to:**
- a builder that computes both fractions for every union. Both are additive sums already (`nd-unfolding/pv-ladder/h2_definition.py:67-73`);
- a purity-only mode kept for the reproduction test of R00-R15 at τ = 0.1 (D:264);
- printing both fractions for every final bin of every candidate.

### 2. The candidate list (D:113-142, :290)

| option | trade-offs |
|---|---|
| (a) C0-C8 as drafted | the reasons are comparability and physics (D:127-132). Nine results to report. |
| (b) fewer candidates | fewer results and fewer chance passes (D:209-211). Removing candidates now, with the 16-cell classes known, is itself a selection. |
| (c) more candidates (other 2D pairs, 3D projections) | more chance passes and more results to explain. Each candidate is cheap to grade, about 0.15 node-h of IBU (D:229). |

**Recommendation: (a).** Grading cost is small, so the real costs of a longer list are the number of results and
the chance passes. Every candidate's result prints, the failures included (D:207-208). A change made now would add
a selection step with no new physics reason. A change for a physics reason Joseph or Ben states remains open until
the bind.

**It commits the follow-up to:** a list fixed at the bind, with no re-binning after grading (D:136-142), and nine
reported outcomes.

### 3. The candidates the follow-up must include (D:144-153, :291)

| option | trade-offs |
|---|---|
| (a) C6 and C7 | C6 ties the follow-up to the published two-dimensional observable, and C7 carries the hadronic-energy and momentum-transfer contrast (D:146-149). If either fails, the outcome is "this declared rule produced no reportable binning for a required observable". A passing candidate does not replace it (D:150-151). A coverage test for the pair costs about 46 node-h for gates only, or 120-126 in full (D:243). |
| (b) C6 only | half the coverage cost. It keeps comparability and drops the physics contrast. |
| (c) none | the most freedom. The follow-up's observables would then be whichever pass, which is the selection the declaration tries to constrain (D:26-27). |

**Recommendation: (a), if Joseph confirms C7's physics reason.** The draft marks that reason as an inference
(D:131-132, :148-149), so it is Joseph's or Ben's to confirm. Option (a) also supplies the physics basis that two
open questions wait on: V-HALF-R's minimum-bin count, and BV96's deferred physics contrasts (D:152-153;
`DECISION-20261110-joseph-bv96-stop-defer.md:31-34`).

**On T2A.** C6 has the axes of the two-dimensional coverage test, whose bias the director reads as lying in C_T's
poorly determined directions. A C6 binning made under choice 1 would be a new binning on the 5D fine grid. If C6 is
reported and goes to a coverage test, that test should declare the T2A split (the mean χ² by eigenvalue rank) as a
print-only output, so the two can be compared.

**It commits the follow-up to:**
- grading both candidates and reporting their outcomes as the follow-up's outcome;
- for each reportable one, an LL5D-type test with its cell-count rules re-declared for that candidate (D:246-250);
- about 46 node-h (gates) to 120-126 node-h (full) for the pair.

### 4. The phase space (D:76-80, :293)

| option | trade-offs |
|---|---|
| (a) the 16-cell reported domain (the union of R00-R15's fine cells) | one domain for every candidate and the 16-cell result. The unreported boxes stay out, as the consult advised for C0 (A:28). A 1D distribution is the distribution within that domain (D:79). |
| (b) the full fine-grid support | inclusive distributions. It adds the boxes H2 left unreported, which fail its support rule (`nd-unfolding/pv-ladder/h2_definition.py:6-8`; `docs/analysis-note/paper_body.tex:50` at #977 `10b88ad9b`). More candidates would likely end with a low bin [inference], and comparison with the 16-cell result is harder. |

**Recommendation: (a).**

**It commits the follow-up to:**
- labelling every candidate with its domain;
- checking, from the binning output (simulation only), how C6's domain compares with the published two-dimensional
  phase space, and stating it. That has not been checked [inference: the two need not coincide].
  <!-- absence-ok: this packet's own scope; it ran no comparison of the two domains -->

### 5. The disclosure's wording (D:47-64, :294)

| option | trade-offs |
|---|---|
| (a) the draft's text (D:49-52) | it states the 16-cell result and the reuse of the development truths. |
| (b) the draft's text plus what else was known | it also covers the referee's remark, which informs choice 1. |

**Recommendation: (b).** Proposed first sentence, in place of the draft's:

> The candidate list, its binning rules and the binning threshold were set after the 16-cell V-HALF result was known,
> and after the methods paper's referees remarked that its cells were formed without a stability criterion.

The rest of the draft's text follows unchanged. If Tier 3 leads to a changed estimator, the disclosure also names
the estimator that was graded.

**It commits the follow-up to:** printing the disclosure wherever any candidate's result prints (D:47).

### 6. Whether the criterion is a final requirement (D:104-106, :203, :297-298)

| option | trade-offs |
|---|---|
| (a) final requirement: every final bin meets the criterion and the support rule, or the candidate ends at T3 before grading | a reportable bin always meets the stated convention. The outcome is known from the binning, before any V-HALF quantity. |
| (b) merge trigger only: a flagged low bin may remain, and the candidate is reportable if every bin is V-HALF-valid | fewer terminal candidates. A reportable candidate can then hold a bin below the threshold, which is the ambiguity the consult flagged (A:38). |

**Recommendation: (a), with choice 1's criterion.** It keeps the threshold meaningful for every reported bin, and it
settles each candidate's terminal status before grading.

**It commits the follow-up to:** reporting by name the candidates that end at T3 before grading.

### 7. The cancellation level for C1-C8 (D:212-215, :295)

| option | trade-offs |
|---|---|
| R-cells | a short listing, in the cells readers know. |
| fine cells | a longer listing, defined for any bin. |

**Recommendation: fine cells for C1-C8, and R-cells for C0.** C1-C8's bins are generally not unions of R-cells
(D:188), so their contributions cannot be assigned to R-cells without splitting cells. C0's bins are unions of
R-cells.

**It commits the follow-up to:** a per-bin listing over each bin's fine cells, for C1-C8.

## When it runs

1. **Now:** Joseph's choices. The valid-region lane then amends the declaration for them (§1.2 changes under choice 1).
   After that come the code (D §6, one to two weeks), coverage-5b-audit and the director's bind. Whether the code
   starts before Tier 3 reports is the director's call.
2. **The study runs after Tier 3 reports.** Tier 3 itself runs only after LL5D's readout (T3:17). After Tier 3
   reports, Joseph decides whether the estimator changes (T3:40-42). V-HALF-R then grades the estimator that is
   reported at that point.
   - If the estimator changes, F0b's bias and noise and FD-PRR's products are remade for it before grading, and
     D §5's price is redone.
3. **Still named and not drafted:** the confirmatory test of a frozen candidate at reserved truths (D:28-30).

## What this packet did not do

- It changed no line of #1016 and ran no compute.
- It did not tabulate any cell's purity or diagonal fraction against a V-HALF class, and it used no class in any
  recommendation.
  <!-- absence-ok: a statement of this packet's own process -->
- The readings of T2A and T2B are the director's (each receipt's binding ruling 4). This packet quotes them as the
  director's.
