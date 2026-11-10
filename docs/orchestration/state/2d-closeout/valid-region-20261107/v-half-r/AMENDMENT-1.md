# V-HALF-R AMENDMENT 1: Joseph's choices and the three clarifications (DRAFT, 2026-11-10)

**Status: DRAFT, for coverage-5b-audit and the director's binding.** Nothing is computed, run or bound by this file.
The binding binds #1016's `DECLARATION.md` together with this amendment. Where they differ, this amendment governs.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

**By** the limitation-resolver lane, at the director's request. `DECLARATION.md` is the valid-region lane's, and this
file changes none of its lines.

**Authority.** `DECISION-20261110-joseph-vhalfr-choices.md` (#1045):
- item 1, the must-include candidates;
- item 2, the six design choices as the packet recommends;
- item 3, three clarifications before audit and binding;
- item 4, the run order.

And `DECISION-20261110-joseph-vhalfr-a33-a82.md` (#1047), which settles A3.3 and A8.2.

**Inputs to this amendment.**
- the packet, `CHOICES-FOR-JOSEPH-20261110.md` (**P**);
- the independent consult, `consult-sol-20261110/answer.txt` (**S**), and the second one on A3.3 and A8.2,
  `consult-sol-a1-20261110/answer.txt` (**S2**);
- the declaration at #1016's head `b7d7ac2dc` (**D**);
- **H**, `nd-unfolding/pv-ladder/h2_definition.py`;
- **G**, `nd-unfolding/s5p_stage1_inspect.py`.

Other paths are at main `7c1e5440d`, relative to `docs/orchestration/` unless they start with `nd-unfolding/`.
Every choice is now decided. Joseph settled A3.3 and A8.2 in the second decision.

## A1. What this amendment fixes

| D section | change | source |
|---|---|---|
| §0 disclosure | a new first sentence | decision item 2 (5); A6 |
| §1.1 phase space | the domain is a fixed 5D mask; the boundary accounting is explicit | decision item 2 (4), item 3 (b); A2 |
| §1.2 binning rule | one criterion, min(purity, diagonal fraction) ≥ 0.5, for the test, the join order and the final requirement | decision item 2 (1), (6); A4 |
| §1.3 candidates | C0-C8 frozen; C2 and C6 keep the p_∥ = 4.5 GeV/c edge; C6 and C7 keep two-dimensional resolution | decision item 2 (2), item 3 (a), (c); A3, A5 |
| §1.4 must-include | C6 and C7, decided | decision item 1 |
| §4 outcomes | the table restated with both fractions and support; the cancellation listing specified and reconciled | decision item 2 (6), (7); S:33, :37; A7 |
| new | the graded estimator frozen by name and digest | decision item 3 (c); A8.1 |
| new | the reserved-truth confirmatory step, specified now | decision item 3 (c); A8.2 |
| §6 code | the tests these changes need | A9 |
| §7 | every choice is decided | both decisions |

## A2. The domain and its boundary (D §1.1; clarification (b))

**The mask.**
- Ω is the set of fine cells of the 5D grid (14 × 16 × 7 × 7 × 6, `G:38-44`) whose H2 box is reported. A fine cell's
  H2 box is assigned by the cell's centre (`G:77-96`).
- The unreported H2 boxes are 2, 6, 10 and 14 (`nd-unfolding/pv-ladder/readouts/h2_definition.json`,
  `unreported_boxes`). With the box index 16 i_pT + 8 i_p∥ + 4 i_E + 2 i_q3 + i_W (`H:41-43`), all four are the region
  p_T < 0.7 GeV/c, q3 ≥ 2.0 GeV and W < 1.8 GeV, at every p_∥ and E_avail.
- So Ω is the fine grid less that region. It is fixed by the pinned `h2_definition.json` (sha256 `b6790761…`) and
  does not depend on any candidate.

**A candidate's bins.**
- A bin is a rectangle on the candidate's axes, intersected with Ω: the fine cells of Ω whose centres lie in the
  rectangle. It integrates over the other axes within Ω only.
- **Consequence, stated wherever a candidate prints.** A bin that overlaps the excluded region's projection on its
  axes integrates only over the part of Ω inside it. For example, a C7 bin at q3 ≥ 2.0 GeV excludes the events with
  both p_T < 0.7 GeV/c and W < 1.8 GeV, and a C6 bin at p_T < 0.7 GeV/c excludes those with both q3 ≥ 2.0 GeV and
  W < 1.8 GeV. Each candidate's bin definitions name the excluded region.

**The response populations.** These generalize `H:77-87` and `G:121-147`. Each sum is over the simulation's rows,
with the row's fine indices ft (truth) and fr (reco); −1 means outside the fine grid.

| quantity | events | weight | located by |
|---|---|---|---|
| same_B | pass_reco and pass_truth; truth fine cell in B and reco fine cell in B | w_reco | both |
| reco_all_B (purity's denominator; support's reco signal) | pass_reco, with any truth: another bin, outside Ω, outside the grid, or failing pass_truth | w_reco | reco fine cell in B |
| truth_reco_B (diagonal fraction's denominator) | pass_truth and pass_reco, with the reco anywhere: another bin, outside Ω, or outside the grid | w_reco | truth fine cell in B |
| truth_sel_B (support's truth weight) | pass_truth | w_truth | truth fine cell in B |

- purity_B = same_B / reco_all_B, and diagonal fraction_B = same_B / truth_reco_B. These are the formulas of `H:72`
  and `G:141`.
- The support rule is reco_all_B ≥ 1000 and truth_sel_B ≥ 1000 (`G:49`, :273).
- **The two directions across the mask, printed for every bin with no acceptance rule:**
  - **in:** the share of reco_all_B whose truth lies outside Ω, outside the grid, or fails pass_truth;
  - **out:** the share of truth_reco_B whose reco lies outside Ω or outside the grid.
- The numerator and the two denominators stay three distinct populations, as in `H:84-86`. No denominator is replaced
  by a sum of the migration matrix's rows or columns restricted to Ω.

## A3. Two-dimensional resolution for C6 and C7 (clarification (a))

The rule reads only the binning's geometry, so no candidate's bias or V-HALF quantity can enter it.

**A3.1 No strips (binding).** For C6 and C7, a join is allowed only if the union spans less than the full range of
each of the candidate's two axes within Ω.
- A bin that would span the whole p_T range, or the whole p_∥ range (C6), or the whole E_avail or q3 range (C7), is
  never formed. It is excluded as an allowed join: a join that would form it is refused, in addition to D:93-94's box
  condition.
- So every row and every column of a final C6 or C7 partition crosses at least two bins. The joint dependence on both
  axes then survives at every value of each axis, and six strips cannot meet the six-bin floor (S:43).
- A low bin whose only box-forming partners are refused stays low and flagged. Under A4.3 the candidate then ends at
  T3, known from the binning alone.

**A3.2 Fixed edge for C6 (binding).** C6 keeps the edge p_∥ = 4.5 GeV/c (A5).

**A3.3 No fixed q3 edge for C7 (decided, `DECISION-20261110-joseph-vhalfr-a33-a82.md` item 1).**
- C7's binning is set by A4's criterion, the floor and A3.1 alone.
- **Landmarks, printed as a description only.** The record prints where each of C7's final q3 edges falls relative to
  q3 = 0.8 GeV and 1.2 GeV, the published low-recoil limits. Both are fine-grid edges (`G:42`).
- No edge is added, moved or removed after the binning is seen.
- The consult recommended a fixed edge at 1.2 GeV (S2:13). Joseph judged the published limits specific to their
  analyses, and the decision records that.

**The floors stay** (D:107-111): 3 bins in 1D, 6 in 2D, and 8 for C0 with 4 on each side of p_∥.

## A4. The binning criterion (D §1.2; decision item 2 (1), (6))

1. **Test.** A bin is low if min(purity_B, diagonal fraction_B) < 0.5, or if it fails the support rule (A2). This
   replaces "purity below τ_R" at D:86 and D:96-101.
2. **Join order.** While a low bin exists, take the one with the lowest min(purity, diagonal fraction). Ties go to
   the lowest first fine index. Merge it with the allowed neighbour whose union has the highest min(purity, diagonal
   fraction). Ties go to the lowest axis, then the lowest first index. This replaces D:91-92.
   - "Allowed" means: a box on the candidate's axes (D:93-94), plus A3.1 for C6 and C7, plus A5 for C0, C2 and C6.
3. **Final requirement.** A candidate is reportable only if every final bin has min(purity, diagonal fraction) ≥ 0.5
   and passes the support rule, as well as being V-HALF-valid (A7.1). This replaces D:104-106.
4. **The meaning of 0.5.** It is a design convention: at least half of what is reconstructed in a bin was generated
   there, and at least half of what was generated there and reconstructed is reconstructed there.
   - It does not guarantee conditioning. Two indistinguishable bins with a 50:50 migration pass both thresholds with
     a singular response (S:13).
   - The diagonal fraction's denominator is reconstructed, truth-selected signal. It is not total efficiency (S:11).
5. **The builder keeps a purity-only mode** for the reproduction test of R00-R15 at τ = 0.1 (D:264, `H:35`).

## A5. Freezing the p_∥ = 4.5 GeV/c edge (clarification (c), first part)

- **The inconsistency.** D:119 allows C2 to join adjacent p_∥ intervals, and D:123 allows C6 to join any rectangles,
  so both may join across p_∥ = 4.5 GeV/c. D:278-279 then applies the GiBUU p_∥ < 4.5 domain section "only to
  candidates that keep the p_∥ split: C0, C2 and C6" (S:45).
- **The resolution.** C2 and C6 may not join across p_∥ = 4.5 GeV/c, as C0 may not (D:117).
- **The reasons:**
  - C-DOMAIN's print-only GiBUU section stays defined for all three;
  - GiBUU is compared on p_∥ < 4.5 GeV/c only;
  - C0, C2 and C6 share one boundary.
- C1, C3, C4, C5, C7 and C8 have no p_∥ axis and are unaffected.

## A6. The disclosure (D §0; decision item 2 (5))

Its first sentence becomes:

> The candidate list, its binning rules and the binning threshold were set after the 16-cell V-HALF result was known,
> and after the methods paper's referees remarked that its cells were formed without a stability criterion.

The rest of D:49-52 follows unchanged. If Tier 3 leads to a changed estimator, the disclosure also names the graded
estimator (A8.1).

## A7. Outcomes and the cancellation listing (D §4; decision item 2 (6), (7))

**A7.1 The outcome table.** This replaces D:200-205.

| outcome | when | reported as |
|---|---|---|
| **T2: below the floor** | fewer final bins than A3's floor | "this declared rule produced no acceptable binning for <candidate> (minimum)"; known from the binning alone |
| **T3: a bin fails the response or support requirement** | a final bin with purity < 0.5, diagonal fraction < 0.5, reco_all < 1000 or truth_sel < 1000 | "this declared rule produced no acceptable binning for <candidate> (a bin below the response or support requirement)", naming each failing quantity per bin; known from the binning alone |
| **T1: not every bin valid** | the binning meets T2's and T3's requirements, and some bin's V-HALF class is other than "valid" | "this declared rule produced no acceptable binning for <candidate>", with every bin's class |
| **R: reportable** | every final bin has min(purity, diagonal fraction) ≥ 0.5, passes the support rule and is V-HALF-valid | the candidate, its binning, both fractions, its support and its bins' classes |

- T2 and T3 are decided before any V-HALF quantity is formed for that candidate.
- **The required pair.** If C6 or C7 ends at T2, T3 or T1, the follow-up's outcome is "this declared rule produced no
  reportable binning for a required observable". A passing optional candidate does not replace it (decision item 1;
  D:150-151).

**A7.2 The cancellation listing, and how it reconciles to the scored quantities** (D:212-215; S:37).

Notation, for bin B, its fine cells f ∈ B and each F0b experiment e at a graded truth:
- P_f, the prior's integral; X_f, the truth's; X̂_{f,e}, experiment e's unfolded integral. Each is a fine product
  integrated with the candidate's U (D:72-75).
- The bin integrals are P_B = Σ_f P_f, X_B = Σ_f X_f and X̂_{B,e} = Σ_f X̂_{f,e}. The bound construction recomputes r
  per experiment from these integrals (D:169-171).

The scored quantities, as bound (D:157-172):
- d_B = (X_B − P_B)/P_B, from FD-PRR's split;
- r_B = mean over e of (X̂_{B,e}/X_{B,e} − 1), from F0b;
- b_B = r_B (1 + d_B).

The listed contributions:
- c^d_f = (X_f − P_f)/P_B, so that Σ_{f∈B} c^d_f = d_B.
- c^b_f = (1 + d_B) × mean over e of (X̂_{f,e} − X_{f,e})/X_{B,e}, so that Σ_{f∈B} c^b_f = b_B. The truth integrals
  X_{·,e} are F0b's, as its r uses them.

The rules for the listing:
- **Reconciliation control (a STOP on failure).** For every bin and graded truth, |Σ_f c^d_f − d_B| and
  |Σ_f c^b_f − b_B| are at most 1e-12 × max(1, |d_B|) and 1e-12 × max(1, |b_B|). Averaging constituent ratios is
  never used (S:37).
- **Listed:**
  - each c^d_f and c^b_f, signed;
  - Σ_f |c^d_f| and Σ_f |c^b_f|;
  - the truths at which the rule applies to some constituent but not to the bin (D:212-215).
- **The level.** Per fine cell for C1-C8. For C0, the fine contributions are summed to each constituent R-cell, which
  is exact because C0's bins are unions of R-cells.
- **Format.** Machine-readable (JSON beside the readout), with a compact per-bin summary in the readout text.
- d's hybrid source and the single-truth σ_d are unchanged (D:173-177). The listing describes the scored numbers and
  adds no class.

## A8. Freezing the estimator, and the reserved-truth step (clarification (c), second and third parts)

**A8.1 The graded estimator.**
- V-HALF-R grades the estimator that is reported when its grading starts. The binding names it, and pins by sha256:
  - the estimator's code and configuration files, as F0b's and FD-PRR's bindings pinned them;
  - every product V-HALF-R reads, in a `v-half-r/INPUTS.sha256` written before grading. This covers F0b's 8,545 fine
    products, FD-PRR's 181 route-1 products and route 2's IBU outputs (D:225-229).
  The code refuses a missing, extra or mismatched digest.
- **Today** that estimator is configuration (e), with H1 = `fd_f0b_readout.json` `5f542830…` and H2 = the PRR readout
  `9238f22b…` (`v-half/INPUTS.sha256`; `v-half/PRR-READOUT.sha256`).
- **If Tier 3 leads Joseph to change the estimator** (`fd/tier3-20261110/T3-PIPELINE-TESTS-DECLARATION.md:40-42` at
  #1038's head `cbb7278e5`):
  - the graded estimator is the one his decision names;
  - F0b's and FD-PRR's products are remade for it and pinned before grading;
  - D §5's price is redone;
  - the disclosure names it (A6).
- **No grading starts** while that decision is pending (decision item 4).

**A8.2 The reserved-truth confirmatory step, specified before any reserved truth is examined** (D:28-30; S:29, :45).

1. **Who it applies to.** Each candidate that reaches R in the development read, and the required pair, whatever its
   development outcome. The confirmatory read reports C6 and C7 either way.
2. **The reserved truths (decided, option (a), `DECISION-20261110-joseph-vhalfr-a33-a82.md` item 2).**
   - **The confirming set:** three new synthetic tilts of the nominal truth, T_pT, T_p∥ and T_W, frozen in item 2a.
     None has been generated.
   - **A disclosed descriptive extra:** the two GENIE v3 tunes, G18 and AR23, as their gated ratios. Their sixteen-cell
     fake-data grades are known (F1), and they share their CCQE model (S2:21). Their results are reported prominently
     beside the tilts', and they cannot rescue a failed tilt.
   - No candidate-level bias at any of these truths has been formed.
     <!-- absence-ok: scoped to the reserved truths named here; V-HALF-R has formed no candidate-level quantity -->

2a. **Each tilt, frozen here before it is generated** (decision item 2, "frozen before any tilt is generated").
   - **Coordinate.** The true p_T (GeV/c), p_∥ (GeV/c) or W (GeV) of the row, from `MCgen`.
   - **Standardization population: global over Ω.** The rows whose true coordinates lie inside the fine grid on every
     axis and whose true fine cell is in Ω (A2), weighted by w_truth. μ and σ are that population's weighted mean and
     standard deviation of the coordinate.
     - The reason: each tilt then changes its own axis's distribution across the whole domain, which is what C1, C2,
       C5 and the 2D candidates resolve.
     - The other axes change only through their correlations with the tilted one. In particular, the p_T, p_∥ and W
       tilts reach C7 only that way (S2:19), and the record says so.
     - The q3 tilt's within-cell form (`nd-unfolding/s5c_pseudo.py:54-95`) is not used for these three.
   - **The weight.** z = clip((x − μ)/σ, −2, 2), and then z′ = z − z̄. Here z̄ is z's w_truth-weighted mean over the
     same population, and r = 1 + 0.3·z′. The sign is + for all three tilts.
   - **Normalization.** The recentring keeps the population's w_truth-weighted total in Ω exactly. A control STOPs if
     the total changes by more than 1e-12 relative, or if any r ≤ 0.
   - **Domain.** r applies to the rows of the population only. Rows outside Ω or outside the grid, including the
     −9999 gen sentinels, keep r = 1, as the q3 tilt treats out-of-grid rows (`nd-unfolding/s5c_pseudo.py:60-62`). So
     migration into Ω from outside it is the nominal simulation's at every tilt, and the record states this.
   - These definitions are bound with this amendment. A tilt that needs any change is a new declaration.
3. **Order.**
   - The development read and every candidate's binning are committed first.
   - Then this step's addendum is bound, with its code, its digests, d's construction at these truths and its price.
   - Only after that are the reserved truths' pseudo-data generated and unfolded.
   - Nobody reads a reserved truth's unfold, bias or departure before the confirmatory read.
4. **The rule.** V-HALF as bound: the same floor, HALF 0.5, K = 2, the same noise treatment and classes (D:157-164).
   It is applied to each frozen binning, with no re-binning.
5. **Acceptance, over the three confirming tilts only** (decision item 2):
   - **Not confirmed:** any frozen bin that fails, or is unresolved, at an applicable confirming tilt, or that lacks
     departure information at a confirming tilt.
   - **Untested:** a bin with no applicable reserved departure at any confirming tilt. An untested bin does not count
     as a pass. A candidate with an untested bin is reported as untested in that bin, and it is not confirmed.
     <!-- absence-ok: "untested" names an outcome class of this step, not a claim that a result does not exist -->
   - **Confirmed:** every frozen bin is V-HALF-valid at every applicable confirming tilt, and no bin is untested.
   - **G18 and AR23** are classified and reported beside the tilts by the same rule. They change no candidate's
     confirmation class.
   - **C6 and C7 each confirm separately.** Both are reported whatever their classes. No rebinning follows the
     confirmation read.
   - A candidate that is not confirmed is not reported as a measurement candidate. Every outcome is reported, and no
     multiplicity correction is declared.
6. **What it licenses.** "Confirmed at the three tested tilts" for the frozen binning, beside the development result,
   and reported as limited to those tested truths. The tilts are a substantial stress at amplitude 0.3 on a
   standardized coordinate. They are not a realistic generator envelope (decision item 2). The step licenses neither
   coverage nor a measurement.

## A9. Code and tests this amendment adds to D §6

- **The builder:**
  - the mask Ω and A2's four populations, with the "in" and "out" shares printed;
  - A4's criterion, join order and final requirement;
  - A3.1's refusal and A5's edge as join constraints; A3.3's landmark print for C7.
- **Tests:**
  - R00-R15 reproduce from the H2 boxes in purity-only mode at τ = 0.1 (D:264).
  - Each population on a fixture where:
    - a truth-outside-Ω event reconstructs inside a bin, which enters reco_all and not same;
    - a truth-inside event reconstructs outside Ω, which enters truth_reco and not same.
  - A C6 fixture whose only box-forming partner would be a full p_T strip is refused and ends flagged.
  - A C2 or C6 fixture whose best partner crosses p_∥ = 4.5 is refused.
  - A T3 fixture for each failing quantity (purity, diagonal fraction, reco support, truth support).
  - A7.2's reconciliation control STOPs on a planted 1e-9 drift. Its fixture has bins where the mean of constituent
    ratios differs from the ratio of sums.
- **Mutants** for each refusal and for the join ordering, as D:264 requires.
- **Before grading:** the estimator pin of A8.1, with a refusal test.
- **The confirmation step's addendum** carries A8.2 2a's tilt code, with tests:
  - the Ω total is unchanged to 1e-12, and the STOP fires on a planted drift;
  - rows outside Ω keep r = 1;
  - r ≤ 0 STOPs;
  - the "untested" and "missing departure" classes are each reachable on a fixture.
  <!-- absence-ok: "untested" names an outcome class of the confirmation step, not a claim that a result does not exist -->

## A10. Unchanged

- Everything else in D, including V-HALF's rule as bound (D:157-164), the noise limits (D:173-177), the pipeline
  (D §5), the LL5D conditions (D:246-255) and the licences (D:32-45).
- The run order. The study runs only after Tier 3 reports and Joseph has decided whether the estimator changes
  (decision item 4). Tier 3 itself runs after LL5D's readout.
- V-HALF in the methods paper stays a diagnostic on R00-R15, with no rebinning (decision item 5).
