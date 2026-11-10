# V-HALF-R: a pre-specified, merge-only rebinning of R00-R15 for V-HALF (DRAFT declaration)

**Status: DRAFT, for Joseph's review of the merge design before coverage-5b-audit.** Nothing is computed, run or bound
by this file. Three choices stay Joseph's, and he may take them to the advisor; each is marked **[JOSEPH]** with the
lane's recommendation and its reason (§6). The rest of the design is declared here, revised on 2026-11-10 after an
independent review (`consult-astra/`) at the director's instruction.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

The valid-region lane wrote this on 2026-11-10 at the director's request. It is Joseph's parallel track: the paper does
not wait on rebinning, but the rebinning is prepared so that a result could arrive before submission. File:line
citations are at main `fd10736458b9e7db5b0b08aeb758ec2aa383361c` unless stated. [INF] marks an inference. Costs come
from `../v-half/rebin-assessment-20261109/README.md` (#1011) and its existence check (`purge-check/`, #1012).

**What this is: a development study, not a confirmation.**
- V-HALF-R re-applies V-HALF to a coarser, merged set of cells, at the **same 12 graded truths** the 16-cell result
  used. Those truths are not held out (`../v-half/DECLARATION.md` §10).
- A pass on the merged cells is therefore a development result. It is not an independent validation of a rescued
  measurement.
- **The next step** before any confirmatory claim: a frozen merged binning would be tested at **reserved truths** that
  played no part in its design (`consult-astra/answer.txt`; the earlier consult's safeguard,
  `stageF/methods/secondary-results/consult-astra-vhalf-20261109/answer.txt`). Nothing for that step is drafted here.

CITABLE FOR (once approved, audited and bound): **the V-HALF classification of the specified coarse integrals at the
tested truths**, with the merge design, its fixed elements, outcomes, pipeline and price.
NOT CITABLE FOR: coverage; restored fine structure, so a passing merged cell does not validate its constituent cells; a
failure mechanism; a validated measurement; any V-HALF class before the merged read; any paper or note sentence. FD-PRR's
other diagnostics gain no claim from its regenerated readout (§2). Until Joseph approves, coverage-5b-audit returns GO
and the director binds it, nothing here is citable.

## 0. Disclosure (prints wherever a merged result prints; final wording [JOSEPH], §6)

> **The merge rule was set after the 16-cell V-HALF result was known.** The 16-cell counts (5 valid, 9 not valid, 2
> unresolved) and each cell's class had been reported to the director and Joseph before this declaration was drafted.
> The merged cells are graded at the same 12 development truths, and a passing merged cell does not validate its
> constituent cells.

- **Its author knew the classes.** The lane that drafted the rule ran the 16-cell V-HALF read
  (`../v-half/receipts/read/`, #1009) and has seen each cell's class.
- **What the lane did not do while drafting.** It did not tabulate any cell's purity, stability or n_eff against the
  thresholds below, and did not compute which cells any option would merge.
  <!-- absence-ok: a statement of the lane's own process while drafting -->
  - This is not blindness. Each R-cell's own purity is committed in `h2_definition.json`; for example R02 is 0.392 and
    R08 is 0.510 (as the reviewer notes, `consult-astra/answer.txt`). So which cells start a merge can be partly
    anticipated.
  - What is not committed is the 32 × 32 migration matrix (`nd-unfolding/pv-ladder/h2_definition.py:62-88`), which the
    purity of a union needs.
- **What the rule depends on.** It reads only simulation-level, definition-level quantities, so it cannot see a V-HALF
  outcome or a fake-data bias (§1.1). But people who knew the 16-cell result chose the rule, the threshold, the axes
  and the minimum. The disclosure states this.

## 1. The merge rule

### 1.1 The criterion: definition-level quantities only

- **The statistic.** The criterion is the H2 definition's own: a box's **purity**, the share of its reco-selected
  signal whose truth lies in the same box. It comes from the simulation's reco–truth migration matrix
  (`h2_definition.py:62-88`).
- **What it may not read.** Purity uses only the MC arrays of the 5D npz (`MC_KEYS`, :37). It never reads the data
  arrays, any unfold product, any fake-data estimate or bias, or any V-HALF quantity (:14-17).
- **Why this statistic.** The 16-cell definition was made by exactly this rule at τ = 0.1 (:5-13, `TAU` :35).
  V-HALF-R changes its threshold, its starting point and its allowed partners (§1.2), and nothing else.
- **The threshold τ_R, [JOSEPH].**
  - **Recommendation: purity alone, τ_R = 0.5,** a design convention: at least half of a reported cell's reco-selected
    signal originates inside its own truth region.
  - It is not a demonstrated threshold for unfolding validity. Its timing is not a priori: it was chosen after the
    16-cell result was known (§0).
  - Purity depends on the simulated population and its migrations, not only on detector resolution.
  - The alternatives are 0.3, or a test on min(purity, stability). The latter changes the test and the partner score,
    so it is a code change.
- **Printed beside purity, with no acceptance rule.** For each merged cell: its stability (`same / truth_reco`, :72,
  the reconstructed truth-selected signal, not total truth efficiency) and its support (`expected_reco_signal`,
  `truth_selected`, `mc_neff_truth`, :72-74). These are not adjustable cuts.

### 1.2 The units and allowed merges (declared; the reviewer concurs)

**Unions of R-cells only, starting from the bound 16-cell definition.**
- Every merged cell is a union of cells already reported, so the merged result nests in the 16-cell one as a
  coarsening.
- The 16 → M matrix A is 0/1, so A·C·Aᵀ applies wherever the assessment found it exact.
- The rule cannot undo or re-split the τ = 0.1 merges that made R00-R15 (h2_definition.json `steps`). Starting again
  from the 32 single boxes could give a different, non-nested partition.

The rule:
- **Start.** The bound definition's final boxes: the 16 reported cells and the 4 unreported boxes 2, 6, 10 and 14
  (`nd-unfolding/pv-ladder/readouts/h2_definition.json`, `reporting_cells` and `unreported_boxes`, sha256 `b6790761…`).
- **Test.** A reported box is low if its purity is below τ_R.
- **Adjacency.** Two boxes may join only if their union is a box, equal on four axes and complementary on the fifth
  (`joinable`, `h2_definition.py:53-59`; `box_of`, :46-50). This is the existing rule.
- **Axes.** Joins along p_T, E_avail, q3 and W; **none along p_∥.**
  - The p_∥ < 4.5 / ≥ 4.5 split is the domain of V-HALF's GiBUU-family print-only section (`../v-half/v_half.py:15`,
    :176-182). It is also F0b's GiBUU cell list (`nd-unfolding/fd_f0_regrade.py:74`).
  - This argues for consistency of that domain; it does not prove an optimal physics resolution.
  - GiBUU-family truths stay graded on every merged cell under the main rule; the domain exclusion stays print-only.
- **Unreported boxes may not join.** The merged cells then cover exactly the 16-cell result's reported phase space, and
  the data, F0b and every covariance block re-aggregate over the same fine cells. The existing rule would let a
  reported box take an unreported partner (:103-108); V-HALF-R excludes them.
- **Order and tie-break** (unchanged, `merge`, :90-118):
  - while a low reported box exists, take the one of lowest purity (ties: lowest first H2 index);
  - among the reported boxes it may join, take the one whose union has the highest purity (ties: lowest axis, then
    lowest first H2 index);
  - merge them, re-test, and repeat;
  - a low box with no allowed partner is kept and flagged.
- **Report.** The reported boxes after the merges, ordered by their lowest H2 index, as cells M00…M(n−1).
- **Purity is also a final requirement (recommendation to Joseph, §6).** As drafted, a flagged low box would stay in
  the merged set, and outcome A could accept a cell below τ_R. The lane recommends that purity ≥ τ_R be required of
  **every** merged cell for outcome A, as well as being the merge trigger. A flagged cell is then terminal outcome T3
  (§3), known from the definition alone.
- **The minimum, [JOSEPH].** Recommendation: **at least 8 merged cells, with at least 4 on each side of p_∥ = 4.5,** as
  an operational floor only.
  - A count alone does not preserve useful 5D shape information: eight boxes can keep little discrimination along a
    given axis.
  - The scientific basis is Joseph's: which physics contrasts or boundaries the follow-up measurement must resolve.
    The merged partition is judged against that requirement before any of its biases is seen.
  - Breaching the floor is terminal outcome T2.

### 1.3 One shot

- **Once.** The merged definition is computed once, by the bound builder, from the simulation only. It is committed
  and bound by sha256 before any re-aggregated product or merged V-HALF quantity is computed.
- **No iteration.** No second rule, threshold or merge is tried after any merged result is seen.
- **After an unsuccessful outcome** (T1, T2 or T3), any new declaration is labelled a **further development attempt**,
  not a fresh confirmatory test, and prints as such.

## 2. What stays fixed

- **V-HALF's rule as bound** (`../v-half/DECLARATION.md` §1, BINDING 1 at M_VH `ae0ec714`):
  - F0b's 12 graded truths, in its order;
  - the 1 % floor (inclusive, two-sided);
  - HALF = 0.5 and K = 2;
  - the noise treatment;
  - b = r(1 + d);
  - the cell classes and their order of precedence.
- **H1/H2's provenance.**
  - H1 is F0b's readout made by the bound F0b code, here on the merged cells.
  - H2 is FD-PRR's readout made by the bound `prr_read.py` (M_A4's bytes), here on the merged cells. Its d comes from
    route 1's existing products.
  - No other source of r or d may be used.
- **How the merged quantities are computed** (not averaged from cell ratios):
  - **F0b's bias and noise** are recomputed per experiment from that experiment's **merged integrals**, r = X̂_M/X_M − 1,
    with the noise its covariance over experiments (`fd_f0_regrade.py:207-212`). They are not averaged from the
    16-cell ratios.
  - **d and σ_d.** Each FD-PRR split's merged d = (X_M − P_M)/P_M is recomputed before the spread over the five splits
    at A7_gibuu.
- **The noise limits carry over unchanged** (`../v-half/DECLARATION.md` §4 and §10):
  - d's hybrid source;
  - σ_d from a single truth;
  - the formula has no bias–departure covariance term;
  - the K = 2 band is not calibrated coverage.
- **Only V-HALF reads the merged PRR readout's d.** FD-PRR's other diagnostics in the regenerated readout (PR-1 to PR-3,
  R-ID and R-SUP) are not read or reported, and gain no claim from it.
- **The 16-cell result stands.** It is reported beside the merged one, unchanged.

## 3. Outcomes

| outcome | when | what is reported |
|---|---|---|
| **T0: the rule changes nothing** | no reported box has purity < τ_R, or no low box has an allowed partner and none is flagged | "V-HALF-R merges no cell"; the 16-cell result alone; no re-read |
| **T2: minimum breached** | the merged definition has fewer cells than the minimum (§1.2) | "this declared rule produced no acceptable binning (minimum count)"; known from the definition alone |
| **T3: a merged cell below τ_R** | a flagged low box remains (if Joseph adopts §1.2's final requirement) | "this declared rule produced no acceptable binning (a cell below τ_R)"; known from the definition alone |
| **T1: not every merged cell valid** | any merged cell's V-HALF class is anything but "valid" ("not valid", "unresolved (noise)", "no d", "rule applies at no truth") | "this declared rule produced no acceptable binning", with every merged cell's class, beside the 16-cell result |
| **A: acceptable binning** | every merged cell is "valid" (and, with §1.2's requirement, has purity ≥ τ_R) | the merged binning and its classes, beside the 16-cell result, with §0's disclosure |

- **What a terminal outcome means.** The rule is a greedy search, so a terminal outcome means this declared rule
  produced no acceptable binning. It does not mean no acceptable binning exists.
- **T2 and T3 are decided before compute.** Both are checked on the bound merged definition, at no cost beyond the
  definition step.
- **Cancellation is reported with every merged result (A or T1).** Merging sums signed quantities: b_M = Σ (X̂_c − X_c)/
  Σ P_c, and d_M likewise. So opposite biases can cancel, and departures can cancel and fall below the 1 % floor. For
  each merged cell and truth the report gives:
  - each constituent's signed contribution to b_M and to d_M, and the totals of their absolute values;
  - the truths at which the rule applied to some constituent (|d_c| ≥ 0.01) but no longer applies to the merged cell
    (|d_M| < 0.01).

  The "rule applies at no truth" class catches the complete loss of applicable truths. This listing shows when only some
  of them drop out.
- **The consequence is Joseph's.** Neither A nor a terminal outcome decides what the paper does. That stays with
  Joseph (the decision's item 5, `DECISION-20261109-joseph-bias-half-rule.md`).

## 4. Pipeline and price (merge-only, same fine grid; best case of the assessment)

| step | what | compute | source |
|---|---|---|---|
| 0. inputs re-checked | every input of steps 1-8 re-checked by **content** (sha256 against its committed pin), immediately before execution; the purge check (#1012) showed existence on 2026-11-10 only | login | `purge-check/README.md` |
| 1. merged definition | V-HALF-R's builder from the bound definition's boxes, at τ_R, under §1.2; reads the MC npz `07fccc1a` on pscratch | login, minutes [INF] | `h2_definition.py:130-160` (`main`) |
| 2. S1 on the merged cells | C_e and its groups by A·C·Aᵀ, or by s1_assemble on the new definition (re-pinned) from the committed fine products plus C_stat b21-b50 on pscratch | login | assessment §2 |
| 3. C_model,5D | `build_cmodel5d.py` on the new definition (it reads `n_reporting_cells`); absolute A·C_abs·Aᵀ, then re-fractionalized | login | assessment §2 |
| 4. C_resp | A·C·Aᵀ, exact | 0 | `build_cresp.py:108-114` |
| 5. C_PL,5D | rebuilt by `fd_ct_periods.py` from its 34 period unfolds and 4 truths (ratios; not A·C·Aᵀ) | login | `fd_ct_periods.py:411`, :422-427 |
| 6. F0b on the merged cells | `fd_f0_regrade.py` on the new definition and rebuilt blocks, per experiment from merged integrals (§2), over the 8,545 fine products | login, about 70 s | `FD-F0b-REPORT.md:41` |
| 7. FD-PRR route 1 | `prr_read.py` on the new definition; C-CT checks against step 6's matrices; per-split merged d (§2) | login, about 80 s | `fd/receipts-prr/read/` |
| 8. FD-PRR route 2 (IBU) | one prr_ibu job, since route 2 stored only 16-cell values | 0.1517 node-h measured | `fd/receipts-prr/ibu/attempt3/` |
| 9. V-HALF on the merged cells | `v_half.py` re-read, with §3's cancellation listing | 0, local | `../v-half/receipts/read/` |

- **The data central value** re-aggregates exactly (f = U·x).
- **The MC npz.** `07fccc1a`, needed by step 1, was not in the purge check. It is an unverified dependency until step 0.
  <!-- absence-ok: a stated dependency, not a claim that a file is absent -->

**The LL5D coupling.** The LL5D gate rerun after amendment A1a.2 is about to be decided. Both gates of 2026-11-10 ended
verdict=STOP. They ran 11:00:23 and 10:52:09 (`fd/receipts-ll5d/gate-ar23/README.md:8`, `gate-g18/README.md:8`), 21.9
node-h for the pair. Priced per option at the measured gate time per definition [INF]:

| option | the gates test | expected node-h | needs first |
|---|---|---|---|
| (i) 16 cells now; merged later, conditionally | R00-R15 | about 21.9, plus a calibration rerun if A1a.2 requires one (1.18, `calib-2/README.md:9-10`) | A1a.2 alone |
| (ii) merged cells only | M00… | about 21.9 (+1.18) | V-HALF-R bound, steps 1-3 (C_e(T) needs S1's merged blocks), LL5D re-pinned to the new definition, the multiplicity rules below |
| (iii) both | R00-R15 and M00… | about 43.8 (+2.4) | both of the above |

- **Pilot and bulk.** If the gates pass, LL5D's pilot and bulk (about 38 node-h, `LL5D-DECLARATION.md:556-560`) run
  per tested definition: once for (i) or (ii), twice for (iii).
- **[INF] Gate time** is set by the block count, not the cell count (G(N), `LL5D-DECLARATION.md:570`).
- **What changes for any merged LL5D run.** LL5D's rules that depend on the cell count need explicit treatment, declared
  before that run:
  - the gate's "at most 2 of 16 cells have |r_c − 1| > 0.20" (`LL5D-DECLARATION.md:365-372`);
  - the per-cell under-coverage allocation 0.025/16 and the union-bound size statement (:469-483);
  - the cell-wise clipping readings (:477-481);
  - "the χ² region carries over only if both matrices have ndf = 16" (:320).
- **What LL5D does and does not test.** LL5D transfers to the procedure's covariance at the tested truth. It does not
  certify the reported data covariance (`LL5D-DECLARATION.md:317-324`, :758-769, as the reviewer notes).
- **The recommendation now before Joseph.** The reviewer recommends option (i): keep the 16-cell study, and add a merged
  test later only if a scientifically useful merged candidate survives. A test of both would carry separate claims and
  a declared comparison, never a selection of whichever passes. The director has put this to Joseph.
- **Totals.** V-HALF-R's own pipeline is about 0.15 node-h. With LL5D: (i) or (ii) about 22-23 node-h, (iii) about
  44-46, plus pilot and bulk if the gates pass. The m3246 balance was 1,627.4 on 2026-11-09
  (`fd/receipts-prr/ibu/attempt3/cluster/logs/connect-ibu-3.log.txt:12`), less the two gates [INF].

## 5. Code that must change before any of this runs (written, tested and audited after Joseph's review)

- **The merge.** A V-HALF-R mode or module beside `h2_definition.py`. It:
  - starts from the bound definition's boxes;
  - tests against τ_R;
  - takes only reported partners and excludes p_∥ joins;
  - prints stability and support beside purity;
  - writes a new `h2-definition`-schema file with its `steps`, flags and fine-map sha256.

  Its tests: the 16-cell definition reproduces at τ = 0.1 from single boxes, and every declared refusal has a test.
  There are mutants.
- **A bug to fix: F0b's χ² survival function rejects odd degrees of freedom.**
  - `chi2_sf_even` raises unless ndf is even (`fd_f0_regrade.py:194-197`), and `grade` passes it the number of cells
    graded (:225-232).
  - The merged definition, and its p_∥ subsets, may have odd counts. The fix is a general χ² survival function, tested
    against the even-ndf closed form.
  - The cell count is not forced even to suit the software.
- **Re-pins and cell counts.** The pins to the new definition, and the hardcoded 16 in the modules the assessment lists
  (§1 there): `s1_assemble.py:43-44`, :51, :110; `prr_read.py:61`; `prr_probe.py:147`; `fd_f0_regrade.py:67`, :74;
  `fd_cpl_addition.py:44`; `fd_ct_periods.py:54`; `build_cmodel5d.py:50`; `ref_g1/config.json:22`.
- **V-HALF's 16-cell controls.** `CELLS` (`v_half.py:35`), C-CELLS (:239-241), C-PRR (:264), C-DOMAIN's 8 GiBUU cells
  (:284) and C-HAND on R06 (:323) become functions of the merged definition, and C-HAND is re-declared on a merged
  cell. §3's cancellation listing is added as a print-only section.
- **LL5D, only for option (ii) or (iii).** Its dimension-dependent rules (§4) are re-declared for the merged count.
- **The binding path.** Each changed study (S1, F0b, FD-PRR, V-HALF, and LL5D for (ii) or (iii)) gets an addendum,
  coverage-5b-audit's read and the director's bind.
- **[INF] Calendar:** several days.

## 6. Decisions for Joseph (and the advisor) before audit

1. **τ_R, [JOSEPH]:** 0.5 with purity alone (recommended), 0.3, or min(purity, stability) (§1.1).
2. **The minimum and its basis, [JOSEPH]:** which physics contrasts or boundaries the follow-up must resolve. The
   operational floor of 8 cells, 4 per p_∥ side, is recommended (§1.2).
3. **The disclosure's wording, [JOSEPH]** (§0).

Also before Joseph:
- **The lane's recommendation that purity ≥ τ_R be a final requirement for outcome A** (§1.2, outcome T3).
- **The LL5D option,** put to him by the director with the reviewer's recommendation (i) (§4).

Declared here, with the reviewer's concurrence: unions of R-cells, no p_∥ joins, and unreported boxes excluded (§1.2).
