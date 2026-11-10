# V-HALF-R: V-HALF on a pre-declared list of candidate observables (DRAFT declaration)

**Status: DRAFT, for Joseph's review before coverage-5b-audit.** Nothing is computed, run or bound by this file.
Choices that stay Joseph's are marked **[JOSEPH]** with the lane's recommendation and its reason (§7); he may take
them to the advisor.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

**History of this draft.** The valid-region lane wrote it on 2026-11-10, at the director's request.
- **Merges only.** It began as a merge-only rebinning of R00-R15. It was then revised after an independent review
  (`consult-astra/`), and Joseph's LL5D decision (#1018) was recorded.
- **Widened to candidate observables,** on Joseph's instruction after Ben's reply, for the follow-up paper. Ben wrote:
  "you can just pick different observables so they all pass … It's ok if we can't measure the cross section of every
  possible observable."

The review's fixes are kept throughout. File:line citations are at main `308eb66dca6e0ee27b919d895b84d6851ad094f4`
unless stated. [INF] marks an inference. Costs come from `../v-half/rebin-assessment-20261109/README.md` (#1011) and
its existence check (`purge-check/`, #1012).

## What this is: a development study, not a confirmation

- **What it does.** V-HALF-R applies the bound V-HALF rule to a fixed list of candidate observables. Each candidate has
  its own binning, made from simulation-level quantities only. They are graded at the **same 12 graded truths** the
  16-cell result used, which are not held out (`../v-half/DECLARATION.md` §10).
- **What a pass means.** A candidate that passes is a development result: the observable is a candidate for the
  follow-up measurement. It is not an independent validation.
- **Selection by passing.** Ben's suggestion amounts to choosing observables by whether they pass, which is a
  selection. This declaration constrains that selection (§1.3 and §4) but cannot remove it.
- **Before any confirmatory claim,** a frozen candidate is tested at **reserved truths** that played no part in its
  design (`consult-astra/answer.txt`; `stageF/methods/secondary-results/consult-astra-vhalf-20261109/answer.txt`).
  That step is named here, not drafted.

**CITABLE FOR** (once approved, audited and bound): **the V-HALF classification of each declared candidate's bins (the
specified integrals) at the tested truths**, with the candidate list, the binning rules, the outcomes, pipeline and
price.

**NOT CITABLE FOR:**
- coverage, or a validated measurement;
- restored fine structure: a passing bin does not validate the fine cells inside it;
- a failure mechanism;
- an observable not on the list;
- any V-HALF class before the read;
- any paper or note sentence.

FD-PRR's other diagnostics gain no claim from its regenerated readouts (§2). Until Joseph approves, coverage-5b-audit
returns GO and the director binds it, nothing here is citable.

## 0. Disclosure (prints wherever any candidate's result prints; final wording [JOSEPH], §7)

> **The candidate list and its binning rules were set after the 16-cell V-HALF result was known.** The 16-cell counts
> (5 valid, 9 not valid, 2 unresolved) and each cell's class had been reported to the director and Joseph before this
> declaration was drafted. Every candidate is graded at the same 12 development truths. A passing bin does not validate
> the finer cells inside it. Every declared candidate's result is reported, the failures included.

- **Its author knew the classes.** The lane that drafted the list ran the 16-cell V-HALF read
  (`../v-half/receipts/read/`, #1009) and has seen each cell's class.
- **Not tabulated or computed.** The lane did not tabulate any bin's purity, stability or support against the
  thresholds, and computed no candidate's binning.
  <!-- absence-ok: a statement of the lane's own process while drafting -->
- **Not blindness.** The R-cells' own purities are committed in `h2_definition.json`; for example R02 is 0.392 and R08
  is 0.510 (as the reviewer notes). What is not committed is the reco–truth migration matrix that any other binning's
  purity needs (`nd-unfolding/pv-ladder/h2_definition.py:62-88`).
- **What the rules depend on.** They read only simulation-level quantities, so they cannot see a V-HALF outcome or a
  fake-data bias (§1.2). But people who knew the 16-cell result chose which observables to list. The disclosure states
  this.

## 1. The candidates and their binning rules

### 1.1 The common ground

- **The fine grid.** Every candidate is built on the 5D fine grid: p_T 14 bins, p_∥ 16, E_avail 7, q3 7, W 6, so
  65,856 fine cells (`nd-unfolding/project_cov_nd.py:46-53`; `nd-unfolding/s5p_stage1_inspect.py:37-38`).
  - A candidate's bin is a union of fine cells. Its edges are fine edges, along the candidate's own axes, integrated
    over the others.
  - Its row of U is the fine-bin volume where the fine cell belongs to the bin, as for R00-R15
    (`nd-unfolding/s1_assemble.py:119-122`).
- **The phase space, recommended.** Every candidate integrates over the 16-cell result's reported phase space, the
  union of R00-R15's fine cells (h2_definition.json, sha256 `b6790761…`). So all candidates and the 16-cell result share
  one domain, and the unreported boxes stay out.
  - Consequence: a 1D distribution here is the distribution within that domain, not the fully inclusive one. The
    alternative, the full fine-grid support, is listed in §7.

### 1.2 The binning rule: the H2 definition's purity rule, generalized

The rule is `h2_definition.py`'s merge (:5-13, `merge` :90-118), applied to each candidate's own starting bins.
- **Start.** The candidate's starting bins (§1.3).
- **Test.** A bin is low if its purity is below τ_R, or if it fails s5p's support rule: expected reco signal and
  truth-selected weight both ≥ 1000 (`SUPPORT_MIN`, `s5p_stage1_inspect.py:49`; `h2_definition.py:72-74`).
  - Purity, stability and support are additive sums over the bin's fine cells, from the simulation's reco–truth
    migration (`h2_definition.py:62-88`, built on `s5p_stage1_inspect.mc_properties`, :121).
  - Only the MC arrays are read (`MC_KEYS`, :37): no data, unfold product, fake-data bias or V-HALF quantity (:14-17).
- **Join.** While a low bin exists, take the one of lowest purity (ties: lowest first fine index). Merge it with the
  allowed neighbour whose union has the highest purity (ties: lowest axis, then lowest first index).
  - A neighbour is allowed when the union is a box on the candidate's axes, that is, adjacent intervals in 1D and
    rectangles in 2D (`joinable`, :53-59; `box_of`, :46-50).
  - Re-test and repeat. A low bin with no allowed neighbour is kept and flagged.
- **τ_R, [JOSEPH].**
  - **Recommendation: purity alone at τ_R = 0.5,** a design convention: at least half of a bin's reco-selected signal
    originates inside its own truth bin.
  - It is not a demonstrated threshold for unfolding validity. Its timing is not a priori (§0).
  - Purity depends on the simulated population and migrations, not only on resolution.
  - The same τ_R applies to every candidate.
- **Printed beside purity, with no acceptance rule.** Stability (`same / truth_reco`, :72, the reconstructed
  truth-selected signal, not total efficiency) and support (:72-74).
- **Purity is also a final requirement (recommendation to Joseph).** A candidate is reportable only if every final bin
  has purity ≥ τ_R and passes the support rule, as well as being V-HALF-valid (§4). A flagged low bin makes the
  candidate terminal, known from its binning alone.
- **Minimum bins per candidate** (an operational floor). Fewer is terminal for that candidate.
  - 1D: at least 3 bins.
  - 2D: at least 6 bins.
  - The 16-cell merges: at least 8 cells, 4 on each side of p_∥.
  - The scientific basis is the physics contrasts in §1.4, [JOSEPH].

### 1.3 The candidate list (fixed before any candidate is graded; contents [JOSEPH], §7)

| id | candidate | axes | starting bins | allowed joins |
|---|---|---|---|---|
| **C0** | the 16-cell merges | the 5 axes, H2 boxes | the bound R00-R15 (and the 4 unreported boxes, which may not join) | unions of R-cells that are boxes; none along p_∥ (the GiBUU p_∥ < 4.5 domain, `../v-half/v_half.py:15`, :176-182; `fd_f0_regrade.py:74`) |
| **C1** | dσ/dp_T | p_T | its 14 fine bins | adjacent intervals |
| **C2** | dσ/dp_∥ | p_∥ | its 16 fine bins | adjacent intervals |
| **C3** | dσ/dE_avail | E_avail | its 7 fine bins | adjacent intervals |
| **C4** | dσ/dq3 | q3 | its 7 fine bins | adjacent intervals |
| **C5** | dσ/dW | W | its 6 fine bins | adjacent intervals |
| **C6** | d²σ/dp_T dp_∥ | p_T, p_∥ | its 14 × 16 fine bins | rectangles |
| **C7** | d²σ/dE_avail dq3 | E_avail, q3 | its 7 × 7 fine bins | rectangles |
| **C8** | d²σ/dE_avail dW | E_avail, W | its 7 × 6 fine bins | rectangles |

Why these 2D projections [INF where marked]:
- **(p_T, p_∥)** is the companion 2D measurement's observable (`2d-unfolding/`), so C6 is directly comparable to it.
- **(E_avail, W)** is the adopted reporting projection of the s5c line, its 42 "EW" cells
  (`s5p_stage1_inspect.py:8`).
- **(E_avail, q3)** is the low-recoil projection on which nuclear-effect and 2p2h-sensitive comparisons are usually
  shown [INF; a physics rationale for Joseph to confirm].
- **Not listed: the other seven 2D pairs and any 3D projection.** [JOSEPH] may add or remove candidates before the
  bind. The list is then fixed.

**What fixed means.**
- **Only before the bind.** No candidate is added, removed or re-binned after the bind.
- **One shot.** Every binning is computed once, by the bound builder, from the simulation only, and committed and bound
  by sha256 before any candidate is graded.
- **No re-binning after grading.** A failing candidate's binning is not changed in response to its result.
- **Later declarations.** Any new declaration after this one is labelled a **further development attempt**, not a fresh
  confirmatory test, and prints as such.

### 1.4 The candidates the follow-up must include, [JOSEPH]

- **Recommendation:** the follow-up measurement must include **C6 (p_T, p_∥)** and **C7 (E_avail, q3)**.
  - C6 ties the follow-up to the published 2D observable.
  - C7 carries the physics contrast the 5D measurement was built to resolve: the energy transfer and momentum transfer
    of the hadronic system together [INF; a physics rationale for Joseph].
- **If a must-include candidate fails,** the outcome for the follow-up is "this declared rule produced no reportable
  binning for a required observable". Other passing candidates do not replace it.
- **This choice also answers** two open questions: V-HALF-R's minimum-cell question (§1.2) and BV96's deferred
  "physics contrasts" (`DECISION-20261110-joseph-bv96-stop-defer.md:32`).

## 2. What stays fixed

- **V-HALF's rule as bound** (`../v-half/DECLARATION.md` §1, BINDING 1 at M_VH `ae0ec714`), applied to every candidate's
  bins:
  - F0b's 12 graded truths;
  - the 1 % floor;
  - HALF 0.5 and K = 2;
  - the noise treatment;
  - b = r(1 + d);
  - the classes and their precedence.
- **H1/H2's provenance.**
  - H1: F0b's bias and noise, made by the bound F0b code on the candidate's U.
  - H2: d, made by the bound `prr_read.py` (M_A4's bytes) on the candidate's U.
  - No other source of r or d.
- **The merged quantities are recomputed from fine products, not averaged from cell ratios.**
  - F0b's r = X̂_B/X_B − 1 is recomputed per experiment from that experiment's integrals over the candidate's bins, and
    its noise is the covariance over experiments (`fd_f0_regrade.py:207-212`).
  - Each FD-PRR split's d is recomputed on the bins before its spread over the five splits.
- **The noise limits carry over unchanged** (`../v-half/DECLARATION.md` §4 and §10):
  - d's hybrid source;
  - σ_d from a single truth;
  - no bias–departure covariance term;
  - the K = 2 band is not calibrated coverage.
- **FD-PRR's other diagnostics are not read.** The candidate readouts' PR-1 to PR-3 and R-ID/R-SUP are not read or
  reported, and gain no claim.
- **The 16-cell result stands** and is reported beside the candidates.

## 3. Covariance, per candidate (needed only for a candidate reported as a measurement)

V-HALF itself reads no covariance block. It uses F0b's bias and noise and FD-PRR's d. A candidate reported as a
measurement needs its covariance, rebuilt on its bins:
- **C0 (unions of R-cells):** A·C·Aᵀ, exact for the linear blocks (C_stat, the universe bands, the laterals, C_norm,
  C_seed, C_resp, C_model_abs). C_model is re-fractionalized afterwards. C_PL,5D is rebuilt.
- **C1-C8 (fine-edge bins, generally not unions of R-cells):** A·C·Aᵀ on the 16-cell matrices does not apply. Each
  linear block is recomputed from its fine replicas with the candidate's U (exact; login arithmetic):
  - C_stat: b1-b20 committed, b21-b50 on pscratch;
  - the 175 universes, 10 laterals and 80 seed replicas: committed (`s1/readout/s1_assembly/`);
  - C_resp: 8 endpoints, committed;
  - C_model: the pv-ladder products on pscratch;
  - C_PL,5D: rebuilt from its 34 period unfolds and 4 MC truths (cellwise ratios, `fd_ct_periods.py:411`, :422-427).
- **The odd-ndf bug.** F0b's χ² survival function rejects odd degrees of freedom (`fd_f0_regrade.py:194-197`, used by
  `grade` :225-232). Candidates with odd bin counts need it fixed (§6). No bin count is forced even.

## 4. Outcomes, per candidate

| outcome | when | reported as |
|---|---|---|
| **T2: below the minimum** | fewer final bins than §1.2's floor | "this declared rule produced no acceptable binning for <candidate> (minimum)"; known from the binning alone |
| **T3: a bin below τ_R or support** | a flagged low bin remains (with §1.2's final requirement) | "this declared rule produced no acceptable binning for <candidate> (a bin below τ_R)"; known from the binning alone |
| **T1: not every bin valid** | any bin's V-HALF class is anything but "valid" | "this declared rule produced no acceptable binning for <candidate>", with every bin's class |
| **R: reportable** | every bin "valid" and (with §1.2) every bin purity ≥ τ_R | the candidate, its binning and its bins' classes |

- **Everything is reported.** Every candidate's outcome and every bin's class, beside the 16-cell result. The failures
  are listed by name. No candidate is withheld because it failed.
- **The multiplicity is named, not corrected** [INF]. With nine candidates and tens to hundreds of bins, some bins may
  read "valid" partly by chance at the noise band. Reporting every candidate, fixing the list first, and testing
  confirmatorily at reserved truths are the answers. No multiplicity correction is declared.
- **Cancellation is listed** for every graded candidate's bins:
  - each bin's fine-cell contributions to b and to d, both signed and as absolute totals, aggregated to the bin's
    constituent R-cells, or to its fine cells for C1-C8 [JOSEPH: either level];
  - the truths at which the rule applied to a constituent but not to the bin.
- **What a terminal outcome means.** The rule is a greedy search, so a terminal outcome means this declared rule
  produced no acceptable binning. It does not mean that none exists.
- **The consequence is Joseph's** (`DECISION-20261109-joseph-bias-half-rule.md`, item 5). The outcome of §1.4 for the
  follow-up is reported with it.

## 5. Pipeline and price (same fine grid, no new unfold)

| step | what | compute | source |
|---|---|---|---|
| 0. inputs re-checked | every input re-checked by content (sha256 against its pin) immediately before execution; #1012 showed existence on 2026-11-10 only, and the MC npz `07fccc1a` was not in it | login | `purge-check/README.md` |
| 1. the nine binnings | the generalized builder (§1.2) on the MC npz; each binning committed and bound | login, minutes [INF] | `h2_definition.py:130-160` |
| 2. F0b per candidate | the per-experiment ratios on each candidate's U, from the 8,545 fine products | login, about 70 s each [INF], so about 10 min for nine | `FD-F0b-REPORT.md:41` |
| 3. FD-PRR route 1 per candidate | d on each candidate's U, from the 181 route-1 products | login, about 80 s each [INF] | `fd/receipts-prr/read/` |
| 4. FD-PRR route 2 (IBU) | `prr_read` requires route 2 (C-IBU). Route 2 unfolds on the H2 truth grid and integrates to R00-R15 (`prior_retention/prr_ibu.py:14-16`), so C1-C8 need IBU on their own truth bins; one prr_ibu job can run every candidate's binning | about 0.15 node-h per candidate binning [INF from 0.1517 for one], so about 1.4 node-h for nine | `fd/receipts-prr/ibu/attempt3/` |
| 5. V-HALF per candidate | `v_half.py` generalized to the candidate's bins, with §4's cancellation listing | 0, local | `../v-half/receipts/read/` |
| 6. covariance per reported candidate | §3 | login | assessment §2 |

**The bias check costs about 0 node-h, plus about 1.4 node-h of IBU for all nine.** Every pscratch input of steps 2-4
and 6 was present at 2026-11-10T04:16Z (#1012).

**A coverage test (LL5D-type) per candidate reported as a measurement**, priced from the 2026-11-10 gates (21.9 node-h
for the pair, `fd/receipts-ll5d/gate-ar23/README.md:8`, `gate-g18/README.md:8`):

| per reported candidate | node-h | source |
|---|---|---|
| gates only (two truths, both readings) | about 21.9, plus 1.18 calibration if required | measured; `calib-2/README.md:9-10` |
| a full run (calibration, gates, pilot, bulk) | about 60-63 | `LL5D-DECLARATION.md:589-593`, A1a |
| the must-include pair C6 + C7 (§1.4) | about 46 for gates only; about 120-126 in full | [INF] the above × 2 |
| all nine, if all were reported | about 210 for gates only; about 560 in full | [INF], against a balance of about 1,600 (half about 800) |

- **Before each candidate's LL5D run,** LL5D's cell-count rules are re-declared for that candidate:
  - "at most 2 of 16" (`LL5D-DECLARATION.md:365-372`);
  - the per-cell 0.025/16 allocation and the union-bound size (:469-483);
  - the cell-wise clipping readings (:477-481);
  - "the χ² region carries over only if both matrices have ndf = 16" (:320).
- **What LL5D does and does not certify.** LL5D transfers to the procedure's covariance at the tested truth, not to the
  reported covariance (:317-324, :758-769).
- **Joseph's decision of 2026-11-10 stands** (#1018 at `799e16c7`): LL5D reruns on R00-R15 after A1a.2. A candidate's
  LL5D run is conditional and later, with separate claims and a declared comparison, never a selection of whichever
  passes.

## 6. Code that must change before any of this runs (written, tested and audited after Joseph's review)

- **The generalized builder.** For each candidate, from the MC rows:
  - the bin-level migration matrix for its starting bins;
  - §1.2's merge under its allowed joins;
  - its fine map, U and sha256, and its steps and flags.

  Its tests: R00-R15 reproduces from the H2 boxes at τ = 0.1. Every refusal (support, allowed joins, minimum) has a
  test. There are mutants.
- **Generalize the 16-cell code to a definition file of any size.** These modules hardcode 16 cells or the H2
  definition:
  - `s1_assemble.py:43-44`, :51, :103-122;
  - `prr_read.py:61`;
  - `prr_probe.py:147`;
  - `fd_f0_regrade.py:67`, :74;
  - `fd_cpl_addition.py:44`;
  - `fd_ct_periods.py:54`;
  - `build_cmodel5d.py:50`;
  - `ref_g1/config.json:22`.
- **V-HALF.** `CELLS` (`v_half.py:35`), C-CELLS (:239-241), C-PRR (:264), C-DOMAIN (:284) and C-HAND on R06 (:323) become
  functions of the candidate's definition. C-HAND is re-declared per candidate, and the cancellation listing is added.
  - C-DOMAIN's GiBUU p_∥ < 4.5 domain applies as a print-only section only to candidates that keep the p_∥ split: C0,
    C2 and C6.
- **The odd-ndf fix** (§3): a general χ² survival function, tested against the even-ndf closed form.
- **Route 2's IBU on a candidate truth binning** (§5, step 4), with C-IBU re-declared per candidate.
- **The binding path.** Each changed study (the builder, S1, F0b, FD-PRR, V-HALF, and LL5D per reported candidate)
  gets an addendum, coverage-5b-audit's read and the director's bind.
- **[INF] Calendar:** one to two weeks, which is more than the merge-only draft's several days. It is set by the
  generalization from 16 cells to definition files of any size.

## 7. Decisions for Joseph (and the advisor) before audit

1. **τ_R:** 0.5 with purity alone (recommended), 0.3, or min(purity, stability) (§1.2).
2. **The candidate list** (§1.3): add or remove candidates before the bind.
3. **The must-include candidates** (§1.4): C6 and C7 recommended. This also sets the minimum-bins basis and answers
   BV96's physics contrasts.
4. **The phase space:** the 16-cell reported domain (recommended) or the full fine-grid support (§1.1).
5. **The disclosure's wording** (§0).
6. **The cancellation level for C1-C8:** R-cells or fine cells (§4).

Also before Joseph: **the lane's recommendation that purity ≥ τ_R and support be final requirements** for a reportable
candidate (§1.2, T3).

Decided: **the LL5D option (i)** (Joseph, #1018). Declared here, with the reviewer's concurrence for C0: unions of
R-cells, no p_∥ joins, unreported boxes excluded.
