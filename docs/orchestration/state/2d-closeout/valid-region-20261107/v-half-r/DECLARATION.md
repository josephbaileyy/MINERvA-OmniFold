# V-HALF-R: a pre-specified, merge-only rebinning of R00-R15 for V-HALF (DRAFT declaration)

**Status: DRAFT, for Joseph's review of the merge design before coverage-5b-audit.** Nothing is computed, run or bound
by this file. Which merges are allowed is a scientific choice that Joseph may take to the advisor. Each place that needs
his choice is marked **[JOSEPH]**, with the lane's recommendation and its reason.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

The valid-region lane wrote this on 2026-11-10 at the director's request (Joseph's parallel track: the paper does not
wait on rebinning, but the rebinning is prepared so that a result could arrive before submission). File:line citations
are at main `fd10736458b9e7db5b0b08aeb758ec2aa383361c` unless stated. [INF] marks an inference. Costs come from
`../v-half/rebin-assessment-20261109/README.md` (#1011) and its existence check (`purge-check/`, #1012).

CITABLE FOR: the proposed merge design, its fixed elements, its outcomes, pipeline and price, once bound.
NOT CITABLE FOR: any merged cell, any V-HALF class, any cell's validity, or any paper or note sentence. Until Joseph
approves, coverage-5b-audit returns GO and the director binds it, it is not citable for the design either.

## 0. Disclosure (prints verbatim wherever a merged result prints)

> **The merge rule was set after the 16-cell V-HALF result was known.** The 16-cell counts (5 valid, 9 not valid, 2
> unresolved) and each cell's class had been reported to the director and Joseph before this declaration was drafted.

- **Its author knew the classes.** The lane that drafted the rule ran the 16-cell V-HALF read
  (`../v-half/receipts/read/`, #1009) and has seen each cell's class.
- **What the lane did not do while drafting.** It did not tabulate any cell's purity, stability or n_eff against the
  thresholds below. It did not compute or project which cells any option would merge. The merged definition depends on
  the 32 × 32 migration matrix, which is not committed (`nd-unfolding/pv-ladder/h2_definition.py:62-88`), so no merge
  can be projected without running the bound builder.
  <!-- absence-ok: a statement of the lane's own process while drafting -->
- **What the rule depends on.** It reads only simulation-level, definition-level quantities. It cannot see a V-HALF
  outcome or a fake-data bias (§1.1). But the choice of rule and threshold was made by people who knew the 16-cell
  result. The disclosure states that and does not claim blindness.

## 1. The merge rule

### 1.1 The criterion: definition-level quantities only

- **The statistic.** The merge criterion is the H2 definition's own: a box's **purity**, the share of its reco-selected
  signal whose truth lies in the same box. It is computed from the simulation's reco–truth migration matrix
  (`h2_definition.py:62-88`).
- **What it may not read.** Purity uses only the MC arrays of the 5D npz (`MC_KEYS`, :37). It never reads the data
  arrays, any unfold product, any fake-data estimate or bias, or any V-HALF quantity (:14-17).
- **Why.** The existing 16-cell definition was made by exactly this rule at τ = 0.1 (:5-13, `TAU` :35). V-HALF-R
  changes its threshold and its starting point (§1.2), and nothing else.
- **The threshold τ_R, [JOSEPH].**
  - **Recommendation: τ_R = 0.5,** a majority-purity rule: a reported cell must take most of its reco-selected signal
    from its own truth. It is chosen on that a-priori ground, not from the cells' purities, which were not tabulated
    (§0).
  - **Alternatives:** 0.3; or a test on min(purity, stability) < τ_R. Stability is `same / truth_reco` (:72). The
    min(…) alternative changes the test, and the partner score with it, so it is a code change, not only a parameter.

### 1.2 The units and allowed merges, [JOSEPH]

**Recommendation: unions of R-cells only, starting from the bound 16-cell definition.** The alternative is unions of
the 32 H2 boxes, starting from the single boxes. The recommendation:
- **nests:** every merged cell is a union of cells already reported, so the merged result is a coarsening of the
  16-cell one;
- **re-aggregates exactly:** the 16 → M matrix A is 0/1, so A·C·Aᵀ applies wherever the assessment found it exact;
- **keeps the 0.1-step merges:** it cannot undo or re-split the merges that made R00-R15 (h2_definition.json `steps`).
  Starting from the 32 single boxes at τ_R would rerun those steps under a different threshold, and would not
  necessarily nest.

The rule:
- **Start.** The bound definition's final boxes: the 16 reported cells and the 4 unreported boxes 2, 6, 10 and 14
  (`nd-unfolding/pv-ladder/readouts/h2_definition.json`, `reporting_cells` and `unreported_boxes`, sha256 `b6790761…`).
- **Test.** A reported box is low if its purity is below τ_R.
- **Adjacency.** Two boxes may join only if the union is a box: equal on four axes and complementary on the fifth
  (`joinable`, `h2_definition.py:53-59`; `box_of`, :46-50). The existing rule already uses this.
- **Axes, [JOSEPH].** Recommendation: joins along p_T, E_avail, q3 and W, but **not along p_∥**.
  - The p_∥ < 4.5 / ≥ 4.5 split is the domain of V-HALF's GiBUU-family print-only section
    (`../v-half/v_half.py:15`, :176-182).
  - It is also F0b's GiBUU cell list (`nd-unfolding/fd_f0_regrade.py:74`).
  - Forbidding p_∥ joins keeps both defined on the merged cells.
- **Unreported boxes, [JOSEPH].** Recommendation: **they may not join.** The merged cells then cover exactly the
  16-cell result's reported phase space, so the data, F0b and every covariance block re-aggregate over the same fine
  cells. The existing rule would let a reported box take an unreported partner (:103-108); V-HALF-R excludes them.
- **Order and tie-break** (unchanged, `merge`, :90-118):
  - While a low reported box exists, take the one of lowest purity (ties: lowest first H2 index).
  - Among the reported boxes it can join under the allowed axes, take the one whose union has the highest purity
    (ties: lowest axis, then lowest first H2 index).
  - Merge them, re-test, and repeat.
  - A low box with no allowed partner is kept and flagged.
- **Report.** The reported boxes after the merges, ordered by their lowest H2 index, as cells M00…M(n−1).
- **Minimum count, [JOSEPH].** Recommendation: **at least 8 merged cells, with at least 4 on each side of p_∥ = 4.5.**
  Fewer is the terminal outcome T2 (§3). The reason is a-priori: half the 16-cell granularity, and enough cells to keep
  the 5D measurement's shape content on each side of the p_∥ split.

### 1.3 One shot

- **Once.** The merged definition is computed once, by the bound builder, from the simulation only. It is committed
  and bound by sha256 before any re-aggregated product or merged V-HALF quantity is computed.
- **No iteration.** No second rule, threshold or merge is tried after any merged result is seen. A change of rule after
  the bind is a new declaration and prints as such.

## 2. What stays fixed

- **V-HALF's rule as bound** (`../v-half/DECLARATION.md` §1, BINDING 1 at M_VH `ae0ec714`):
  - F0b's 12 graded truths, in its order;
  - the 1 % floor (inclusive, two-sided);
  - HALF = 0.5 and K = 2;
  - the noise treatment, with σ_d over FD-PRR's five splits at A7_gibuu;
  - b = r(1 + d);
  - the cell classes and their order of precedence.
- **H1/H2's provenance.**
  - H1 is F0b's readout made by the bound F0b code, here on the merged cells.
  - H2 is FD-PRR's readout made by the bound `prr_read.py` (M_A4's bytes), here on the merged cells. Its d is computed
    from route 1's existing products.
  - No other source of r or d may be used.
- **Only V-HALF reads the merged PRR readout's d.** The merged PRR readout's PR-1 to PR-3 and R-ID/R-SUP are not read
  for V-HALF-R and are not reported.
- **The 16-cell result stands.** It is reported beside the merged one, unchanged (§4).

## 3. Outcomes

| outcome | when | what is reported |
|---|---|---|
| **T0: the rule changes nothing** | no reported box has purity < τ_R, or no low box has an allowed partner | "V-HALF-R merges no cell"; the 16-cell result alone; no re-read |
| **T2: minimum count breached** | the merged definition has fewer than the minimum cells (§1.2) | "no acceptable binning (minimum count)"; known from the definition alone, before any V-HALF quantity |
| **T1: no acceptable binning** | any merged cell's V-HALF class is anything but "valid" ("not valid", "unresolved (noise)", "no d", "rule applies at no truth") | "no acceptable binning", with every merged cell's class, beside the 16-cell result |
| **A: acceptable binning** | every merged cell is "valid" | the merged binning and its classes, beside the 16-cell result, with §0's disclosure |

- **T2 is decided before compute.** It is checked on the bound merged definition, so it costs nothing beyond the
  definition step.
- **The consequence is Joseph's.** Neither A nor T1 decides what the paper does. That stays with Joseph (the decision's
  item 5, `DECISION-20261109-joseph-bias-half-rule.md`).

## 4. Pipeline and price (merge-only, same fine grid; best case of the assessment)

| step | what | compute | source |
|---|---|---|---|
| 1. merged definition | V-HALF-R's builder from the bound definition's boxes, at τ_R, under §1.2; reads the MC npz `07fccc1a` on pscratch | login, minutes [INF] | `h2_definition.py:130-160` (`main`) |
| 2. S1 on the merged cells | C_e and its groups by A·C·Aᵀ, or by s1_assemble on the new definition (re-pinned) from the committed fine products plus C_stat b21-b50 on pscratch | login | assessment §2 |
| 3. C_model,5D | `build_cmodel5d.py` on the new definition (it reads `n_reporting_cells`); absolute A·C_abs·Aᵀ, then re-fractionalized | login | assessment §2 |
| 4. C_resp | A·C·Aᵀ, exact | 0 | `build_cresp.py:108-114` |
| 5. C_PL,5D | rebuilt by `fd_ct_periods.py` from its 34 period unfolds and 4 truths (ratios; not A·C·Aᵀ) | login | `fd_ct_periods.py:411`, :422-427 |
| 6. F0b on the merged cells | `fd_f0_regrade.py` on the new definition and rebuilt blocks: the per-experiment ratios recomputed from the 8,545 fine products | login, about 70 s per regrade | `FD-F0b-REPORT.md:41` |
| 7. FD-PRR route 1 | `prr_read.py` on the new definition; C-CT checks against step 6's matrices | login, about 80 s | `fd/receipts-prr/read/` |
| 8. FD-PRR route 2 (IBU) | one prr_ibu job, since route 2 stored only 16-cell values | 0.1517 node-h measured | `fd/receipts-prr/ibu/attempt3/` |
| 9. V-HALF on the merged cells | `v_half.py` re-read | 0, local | `../v-half/receipts/read/` |

**The data central value** re-aggregates exactly (f = U·x). All pscratch inputs of steps 2-8 were present at
2026-11-10T04:16Z (`purge-check/`, 8,795 of 8,795). The MC npz `07fccc1a` of step 1 was not in that check; it is an
unverified dependency until checked.
<!-- absence-ok: a stated dependency, not a claim that a file is absent -->

**The LL5D coupling.** The LL5D gate rerun after amendment A1a.2 is about to be decided. Both gates of 2026-11-10 ended
verdict=STOP, measured at 11:00:23 and 10:52:09 (`fd/receipts-ll5d/gate-ar23/README.md:8`, `gate-g18/README.md:8`),
which is 21.9 node-h for the pair. Priced per option, at the measured gate time per definition [INF]:

| option | the gates test | expected node-h | needs first |
|---|---|---|---|
| (i) 16 cells only | R00-R15 | about 21.9, plus a calibration rerun if A1a.2 requires one (1.18, `calib-2/README.md:9-10`) | A1a.2 alone |
| (ii) merged cells only | M00… | about 21.9 (+1.18) | V-HALF-R bound, steps 1-3 (C_e(T) needs S1's merged blocks), LL5D re-pinned to the new definition |
| (iii) both | R00-R15 and M00… | about 43.8 (+2.4) | both of the above |

- **If the gates pass,** LL5D's pilot and bulk (about 38 node-h, `LL5D-DECLARATION.md:556-560`) run per tested
  definition: once for (i) or (ii), twice for (iii).
- **[INF] Gate time** is set by the block count, not the cell count (G(N), `LL5D-DECLARATION.md:570`). The merged
  definition's smaller matrices should not lengthen it.
- **Totals.** V-HALF-R's own pipeline costs about 0.15 node-h. With LL5D, (i) or (ii) is about 22-23 node-h and (iii)
  about 44-46, plus pilot and bulk if the gates pass. The m3246 balance was 1,627.4 on 2026-11-09
  (`fd/receipts-prr/ibu/attempt3/cluster/logs/connect-ibu-3.log.txt:12`), less the two gates [INF].
- **The lane's view.** (iii) tests the merged cells without giving up the 16-cell test the paper reports. (ii) alone
  would leave the reported 16-cell covariance untested by LL5D. The choice is the director's and Joseph's.
  <!-- absence-ok: a scoping statement about what option (ii) would test, not a claim about an existing result -->

## 5. Code that must change before any of this runs (written, tested and audited after Joseph's review)

- **The merge.** A V-HALF-R mode or module beside `h2_definition.py`:
  - start from the bound definition's boxes;
  - test against τ_R;
  - take only reported partners;
  - exclude the disallowed axes;
  - write a new `h2-definition`-schema file with its `steps` and fine-map sha256.
  Its tests: the 16-cell definition reproduces at τ = 0.1 from single boxes; each recommendation's refusal has a test;
  there are mutants.
- **Re-pins and cell counts.** The pins to the new definition and the hardcoded 16 in the modules the assessment lists
  (§1 there): `s1_assemble.py:43-44`, :51, :110; `prr_read.py:61`; `prr_probe.py:147`; `fd_f0_regrade.py:67`, :74;
  `fd_cpl_addition.py:44`; `fd_ct_periods.py:54`; `build_cmodel5d.py:50`; `ref_g1/config.json:22`.
- **V-HALF's 16-cell controls.** These are `CELLS` (`v_half.py:35`), C-CELLS (:239-241), C-PRR (:264), C-DOMAIN's 8
  GiBUU cells (:284) and C-HAND on R06 (:323). They become functions of the merged definition, and C-HAND is
  re-declared on a merged cell.
- **The binding path.** Each changed study (S1, F0b, FD-PRR, V-HALF, and LL5D if (ii) or (iii)) gets an addendum,
  coverage-5b-audit's read, and the director's bind.
- **[INF] Calendar:** several days.

## 6. Decisions for Joseph (and the advisor) before audit

1. τ_R, and purity alone or min(purity, stability) (§1.1).
2. Units: unions of R-cells (recommended) or of H2 boxes (§1.2).
3. Axes: no p_∥ joins (recommended) or all five.
4. Unreported boxes excluded (recommended) or allowed.
5. Minimum count: 8, with 4 per p_∥ side (recommended), or another.
6. The LL5D option: (i), (ii) or (iii) (§4).
7. That §0's disclosure prints wherever a merged result prints.
