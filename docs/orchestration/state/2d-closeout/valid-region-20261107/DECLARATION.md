# DECLARATION: valid regions of the sixteen-cell result, and where the data's departure from the prior sits (2026-11-07)

**By:** the valid-region lane (session director-helper-2).

**Under:** the director's assignment of 2026-11-07. It carries Joseph's direction to fold his advisor's
suggested story into the current work, as Joseph relayed it to the director. The suggestion is in three parts:
1. 5D reproduces 2D;
2. show closure across the fake-data studies, with the regions where the detector response is not good enough,
   using "a spread in bias comparable to the prior spread" as the metric for which regions are valid, as in the
   ATLAS Z+jets OmniFold User Guide;
3. in the identified region of the 2D mismodeling, the mismodeling is localized in the extra dimensions, inside
   the valid regions.

The director made two rulings on this lane's two questions of 2026-11-07, both given in §1:
- option (R), two separately labelled rules;
- V-PRIOR's threshold direction.

**Status:**
- This is a declaration for coverage-5b-audit's read and then the director's binding.
- **Nothing in §§4–6 has been computed.** No S_b, S_g, ρ, quadrant departure or contrast has been formed from the
  inputs.
- The work is records-only: arithmetic on six committed files, on a local machine, at 0 node-h, with no cluster
  contact.

**MEASURES (once bound and run):** for each of the 16 reporting cells R00–R15:
- whether it is valid under two separately labelled rules, V-ATLAS (§4) and V-PRIOR (§5);
- within the valid cells under each rule, descriptively, the data's departure from the simulation's prior and its
  contrasts between cells of the same (p_T, p_∥) quadrant, which are distinguished only by E_avail, q_3 or W (§6).
  Reading (3) has no class and no sentence (audit VR-1).

**CANNOT AUTHORIZE:** any paper or note wording; any change to the reported result, its cells or its covariance;
any reading of non-valid cells as excluded, wrong or unreported; anything outward. Wording comes later, through a
referee read and Joseph.

## 0. Disclosure: what was seen before this metric was chosen

**The form of the metric** is not taken from our data:
- **V-PRIOR's form is the advisor's,** as relayed by Joseph and then the director.
- **V-ATLAS's three thresholds are ATLAS's,** quoted in §1.
- **V-PRIOR's threshold (0.5) is this lane's.** It was fixed with the director before any ρ was computed (§5.4).

**The underlying per-cell numbers were seen before the metric was chosen.** Specifically, before this declaration
the lane's session had read:
- **FD-F0b-REPORT.md §§2–6:** the per-truth χ² and p, and the listed cells. A7 GiBUU is flagged in R02, R06 and
  R07, and Stage 0c GiBUU in R06.
- **The paper's tab:fd16 and the comments beside it** (`docs/analysis-note/paper_body.tex:168-200` @ `7db5cb80`),
  including the comment at :194 with the R06 z values of 2.01 and 1.76 without and with C_PL,5D.
- **`fd/with-cpl/readout/fd_f0b_readout.json` and `fd/readout/fd_f0b_readout.json`:** their structure, and the
  first three entries of some bias, noise and z arrays, printed while the keys were being mapped.
- **`fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json`:** the full per-cell pull vectors of the data
  against all five predictions, Tune v1 included. They are the `variant` record's pulls, against C_total + V_g,
  without C_resp + C_PL5D. They were printed in full while the keys were being mapped on 2026-11-07.
  - **Reading (3) is therefore not blind.** The pulls against Tune v1 that were seen are largest in R08 and R14
    (both above 3.9).
- **The 16-cell f, and the per-cell relative σ of C_e, C_model, C_resp and their sum.** These were all 16 rows of
  `fd/data-product/fd_data_product_cells.csv`, the product without C_PL,5D.
- **The statistical σ in `values_fived16.tex`:** 0.2–0.3 % in R00–R03.

**What this means for each rule:**
- **A1 and A2 (§4) are likely to pass everywhere,** judging from the values already seen, though not all of them
  were read:
  - A2 is 0.2–0.3 % in R00–R03, the only cells read, against a 15 % bar;
  - A1's mc_neff_truth is 2.93 × 10⁶ in R00, the only cell read, against 5,000.

  If they do pass everywhere, V-ATLAS rests in practice on A3, the closure rule, whose inputs were read in
  FD-F0b-REPORT.
- **V-PRIOR's own quantities, S_b, S_g and ρ, have not been formed by this lane.** The bias arrays have been seen in
  part, but not their root mean square over the truth set.
  <!-- absence-ok: a statement about this lane's own process before the declaration, not a claim that a result does not exist -->

## 1. The metric's source (task A), and the director's rulings

**The source read** is the published Supplemental Material of Phys. Rev. Lett. 133, 261803 (2024),
https://journals.aps.org/prl/supplemental/10.1103/PhysRevLett.133.261803/SM.pdf.
- Its sha256 is `efb5beef…99478`.
- Section 2, "Usage recommendations", is committed verbatim with line numbers in
  [`source/SM_section2_lines25-75.txt`](source/SM_section2_lines25-75.txt).
- Its provenance and the arXiv v3 copy (`d845e257…`) are in [`source/README.txt`](source/README.txt).

**The guide's validity rules, verbatim:**

| item | rule (SM.pdf text lines) |
|---|---|
| 1 | "a jet p_T threshold should be applied of at least 5 GeV" (l.34–37) |
| 2 | "Each bin should contain a minimum of 5,000 effective events defined by n_eff ≡ (Σ_i w_i)²/Σ_i w_i²" (l.38–41) |
| 3 | "Each bin should further have a data statistical uncertainty smaller than 15%, which ensures that the kinematic region probed has sufficient support by the data" (l.47–50) |
| 4 | "Any analysis should always be checked using the pseudo-measurement against the target … a standard, binned χ² compatibility test between the pseudo-measurement and the target" (l.51–59) |
| 5 | "any correlation assumption must be tested on the pseudodata before it can be used to extract information from the actual data" (l.60–75) |

**The finding:** the User Guide states no rule that compares a bias spread with a prior spread. The words "prior"
and "spread" do not occur in it (`pdftotext -layout SM.pdf - | grep -c -i -E 'prior|spread'` gives 0). <!-- absence-ok: the claim is scoped to the one document read, and the re-runnable check that measures it is given in source/README.txt -->
- The Letter uses "unfolding prior" only as an uncertainty source. The simulation is reweighted at particle level
  to agree with data, and the closure difference is taken as the uncertainty (arXiv v3 text, l.218–224, in
  [`source/arXiv-2405.20041v3_letter_excerpts.txt`](source/arXiv-2405.20041v3_letter_excerpts.txt)).
- That is the conceptual cousin of V-PRIOR, and it is cited only as such.
- The repo's earlier reading of the same paper agrees with this:
  `state/2d-closeout/stageF/methods/register-prd-study/notes/2405.20041.md:20-23` @ `7db5cb80`.

**Ruling (R), the director, 2026-11-07:** declare two separately labelled rules.
- **V-ATLAS** is the guide's own thresholds, adapted per cell (§4).
- **V-PRIOR** is the advisor's idea as relayed (§5). Its threshold is labelled as this lane's operationalization
  of "comparable", not ATLAS's.
- Reading (3) is made within the cells valid under each rule, and reported separately for each. Revision 2 makes
  it descriptive only, after audit VR-1, which the director accepted (§6).
- The director is asking Joseph whether the advisor had a specific source for the prior-spread metric. If one is
  named, V-PRIOR is adjusted before the binding.

**The threshold ruling, the director, 2026-11-07,** is in §5.4. **The director's first wording, "valid meaning a
ratio ≤ 1", was withdrawn,** because a cell whose result is its prior has ρ ≈ 1 and would have counted as valid.

## 2. Inputs

All six are committed. They are listed with their sha256 in [`INPUTS.sha256`](INPUTS.sha256), checked by
`shasum -a 256 -c` at `7db5cb80`. `$FD` is `docs/orchestration/state/measurement-paper/5d-community-20261024`.

| # | file | sha256 | used for |
|---|---|---|---|
| I1 | `$FD/fd/with-cpl/readout/fd_f0b_readout.json` | `5f542830…` | per truth: `bias`, `noise_sigma`, and `grade.z` against the reported covariance (`labels.grade_matrix`: C^(T) + C_resp + C_PL5D, own-generator leave-out on C_model only); `p_parallel_lt_4p5.cells` |
| I2 | `$FD/fd/readout/fd_f0b_readout.json` | `b9db935a…` | control C-BIAS only. Its bias and noise must equal I1's |
| I3 | `$FD/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json` | `a19009e0…` | the five predictions in the analysis definitions, with NuWro and GiBUU corrected to CH: `g`, `f`, `sigma_Vg_over_f`, `cells` |
| I4 | `$FD/fd/with-cpl/data-product/fd_data_product_cpl.json` | `d6752d2c…` | f, the cell boxes, and the reported covariance `matrices.C_total_plus_C_resp_plus_C_PL5D` |
| I5 | `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b6790761…` | `reporting_cells[].mc_neff_truth` and the boxes |
| I6 | `$FD/s1/readout/s1_assembly.json` | `81e5ef3f…` | `relative_sigma.stat`, the data's bootstrap statistical σ/f (50 replicas) |

These are the paper's own pins (`docs/analysis-note/make_values_fived16.py:30-43` @ `7db5cb80`), except I2, which
is the readout without C_PL,5D.

**What the six quantities are, as defined at their producers:**
- **Bias:** b_T(c) is the mean over pseudo-experiments of X/X_true − 1 at truth T in cell c
  (`nd-unfolding/fd_f0_regrade.py:6-14` @ `c4396756`, sha `37427d9d`, the pinned F0b code). It is relative, and
  carries no f.
- **ν_T(c)** is `noise_sigma`, the standard error of that mean. It is zero for the noise-free closure.
- **The per-cell pull** is z = b/√diag(C + N) (`fd_f0_regrade.py:211-224` @ `c4396756`).
- **mc_neff_truth** is (Σw)²/Σw² over the simulation's selected truth events in the cell, with the simulation's
  weights (`nd-unfolding/pv-ladder/h2_definition.py:73` @ `7db5cb80`; `nd-unfolding/s5p_stage1_inspect.py:144`).
- **The prior** P is `mnvtune_v1` in I3: "MINERvA Tune v1, the analysis MC truth: prior".
- **The generators** G are `genie_cv`, `genie_mec` and `nuwro` on all 16 cells, and `gibuu` on its eight
  p_∥ < 4.5 cells only. I3 `labels.gibuu`, and `FD-DIRECTOR-RULINGS.md:70-78` @ `7db5cb80`, say: "no GiBUU value
  above p_parallel 4.5 is formed".

## 3. Cells and quadrants

**The cells.** R00–R15 are the definition's 16 reporting cells. The quadrants are read from I4's boxes, and
control C-BOX checks them against I5.

| quadrant | p_T (GeV/c) | p_∥ (GeV/c) | cells |
|---|---|---|---|
| Q1 | 0–0.7 | 1.5–4.5 | R00 R01 R02 R03 |
| Q2 | 0–0.7 | 4.5–60 | R04 R05 R06 R07 |
| Q3 | 0.7–4.5 | 1.5–4.5 | R08 R09 R10 R11 |
| Q4 | 0.7–4.5 | 4.5–60 | R12 R13 R14 R15 |

**What a quadrant resolves.**
- Within a quadrant every cell has the same (p_T, p_∥) box. So any difference between two cells of one quadrant is
  carried by E_avail, q_3 or W, which is a difference "in the extra dimensions" by construction.
- The quadrant is the only (p_T, p_∥) region that the 16 cells resolve.
- Summed over each quadrant, the 16-cell result agrees with the two-dimensional result
  (`docs/analysis-note/paper_body.tex:139` @ `7db5cb80`). So a quadrant's departure from the prior is the
  two-dimensional-level departure at this granularity.

## 4. V-ATLAS: the guide's thresholds, adapted per cell

A cell is **V-ATLAS-valid** if it meets A1, A2 and A3.

**A1, from guide item 2:** mc_neff_truth(c) ≥ 5,000, from I5.
- **The deviation.** ATLAS's n_eff is over the published event weights, which are the unfolded nominal weights.
  Ours is over the simulation's own weights before unfolding.
- The n_eff of the unfolded weights per cell is not in the committed records, and it is not computed here, because
  nothing new is run.
  - The search was the committed JSON keys matching n_eff at `7db5cb80`. It finds per-cell n_eff only as
    `mc_neff_truth` (the simulation's).
  - The refined weights' n_eff appears only for the whole sample: `n_eff_refined` ≈ 4.26 × 10⁶ in
    `state/s5e/diag/diag_receipt.json` and the gencmp-e2 probe.
  - The other keys are flux-universe and development records.
  - Search: git grep -o -i -E '"[a-z0-9_]*n_?eff[a-z0-9_]*"' 7db5cb80 -- '*.json' (keys mc_neff_truth, n_eff, n_eff_refined, n_eff_signed_abs, per_cell_n_eff, kish_neff_signal, n_eff_tr2_over_sum_sq) @ 7db5cb8003a0

**A2, from guide item 3:** the data statistical σ/f in the cell, `relative_sigma.stat[c]` from I6, is below 0.15.
This matches the guide's rule directly.

**A3, from guide item 4, adapted per cell:** at every graded truth of I1 (12 truths: `graded` is true), the cell's
pull against the reported covariance satisfies |z_T(c)| ≤ 2. The pull is `grade.z`, with the truth's own generator
left out of C_model as in the paper's tab:fd16.
- **The adaptation is ours.** Guide item 4 is a χ² test of a whole distribution, and the guide fixes no threshold.
  The Letter reports its outcomes as p-values: "> 0.07, except for p_T^j1, with a p-value of 0.038", and in subregions "greater than 0.05" except one 0.02 (excerpt l.418–421, 436–437).
- **The per-cell bar of 2 is the paper's own trigger.** It was bound before F0 was graded
  (`FD-DIRECTOR-RULINGS.md:35-39`; `fd_f0_regrade.py:60` @ `c4396756`). It is not ATLAS's.
- **The two prior truths (closures) are included.**
- **GiBUU-family truths are graded on all 16 cells,** as the paper grades them. A print-only variant drops them on
  the eight p_∥ ≥ 4.5 cells.
- Each truth's p, and whether it is below 0.01, is printed beside the class. The per-truth p does not enter the
  per-cell class, because it cannot be assigned to a cell.

**Guide items 1 and 5:**
- **Item 1** (jet p_T) does not apply.
- **Item 5 is not met in ATLAS's sense.** No reported interval of the 16-cell result has validated coverage
  (`paper_body.tex:297` @ `7db5cb80`). The correlation model has therefore not been "tested on the pseudodata" as
  item 5 asks. V-ATLAS does not claim item 5, and the readout prints that it is not met.

## 5. V-PRIOR: the bias spread against the prior spread (the lane's operationalization)

### 5.1 The truth set

**T** is the graded truths of I1 outside the prior group: those with `graded` true and `group` ≠ `"prior"`. There
are 10 of them:
- W1, W2, W3 and q3;
- Stage 0c GiBUU;
- closure NuWro;
- A7 GENIE CV, A7 GENIE+MEC, A7 NuWro and A7 GiBUU.

**Row 6 (P1r–P3g) is excluded.** It is ungraded and descriptive, because control 7 failed (FD-F0b-REPORT §2).

**The per-cell truth set T_c** is T, with the GiBUU-family truths (`own_vertex` = `"gibuu"`) counted only on their
`p_parallel_lt_4p5.cells`, the eight p_∥ < 4.5 cells. So |T_c| is 10 on those eight cells and 8 on the others.
- This matches the generator domain (§5.2), so that S_b and S_g are taken over the same families in every cell.
- A print-only variant keeps the GiBUU-family truths on all 16 cells.

### 5.2 The prior spread, from the predictions, not from C_model

**The generator set G_c:** `genie_cv`, `genie_mec` and `nuwro`, plus `gibuu` on its eight cells. So |G_c| is 4 or
3.

**The departure from the prior,** δ_G(c) = g_G(c)/g_P(c) − 1. The data does not enter.

**Why the predictions and not C_model's generator components:**
1. **The predictions are literally "the spread of the generator predictions about the prior".** They are in the
   analysis definitions with CH corrections, the same objects as Table gen16.
2. **C_model's components are not predictions.** Each is a data shift unfolded through the chain (I3
   `labels.covariance`: "Each vertex is a data shift unfolded …"). They therefore already carry the unfolding's
   response, which is the quantity V-PRIOR is meant to test, and the comparison would be partly circular.
3. **C_model's per-cell relative σ** (I4 `relative_sigma.C_model_abs`) is printed beside S_g as context only. It
   does not enter any class.

### 5.3 The spreads and the four noise combinations

Each spread is a root mean square about zero, because both the bias and the departure are measured from their
reference, the truth and the prior respectively.

- **The bias spread**, over the truths in the cell:
  - S_b,raw(c)² = mean over T ∈ T_c of b_T(c)²;
  - S_b,sub(c)² = max(0, mean over T ∈ T_c of [b_T(c)² − ν_T(c)²]).
- **The prior spread**, over the generators in the cell:
  - S_g,raw(c)² = mean over G ∈ G_c of δ_G(c)²;
  - S_g,sub(c)² = max(0, mean over G ∈ G_c of [δ_G(c)² − v_G(c)]), with
    v_G(c) = (1 + δ_G(c))² · (s_G(c)² + s_P(c)²).
  - s_X(c) is the prediction's relative finite-sample σ: s_X = `sigma_Vg_over_f`_X · f / g_X, where f is I3's f
    for the same prediction.
- **ρ(c) = S_b/S_g** is formed for each of the four combinations (b raw or sub) × (g raw or sub). A combination
  whose S_g is 0 has ρ undefined.

### 5.4 The threshold, and why it runs this way

**The derivation.** Suppose the unfold returns its prior in cell c, which is the case of a detector response "not
good enough".
- Then X ≈ X_prior, so b_T(c) ≈ X_prior/X_true − 1 ≈ −δ_T(c), where δ_T is the truth's departure from the prior.
- For truths whose departures spread like the generators' (the A7 hybrid truths are generator predictions,
  `paper_body.tex:168`), S_b ≈ S_g, and **ρ ≈ 1 means "the result is the prior".**
- When the unfold recovers the truth, b ≈ 0 and ρ ≈ 0.
- So "a spread in bias comparable to the prior spread" describes cells that are **not** valid.

**The rule, the lane's operationalization of "comparable", not ATLAS's:** "comparable" means within a factor of 2.
- **V-PRIOR-valid ⇔ ρ < 0.5:** the unfold removes more than half of the prior spread.
- **Not valid ⇔ ρ ≥ 0.5.**
- **Classes and agreement.** A cell's V-PRIOR class is read only where all four combinations of §5.3 agree, with
  every ρ defined. If they disagree, or any ρ is undefined, the cell is **"unresolved (noise)"**, and it is not
  counted as valid.
- **Print-only sensitivity:** the class at thresholds 1/3 and 1, by the same four-combination rule. It enters no
  reading.

**The withdrawn wording.** The director's first wording, valid ⇔ ρ ≤ 1, would have counted a cell that returns its
prior (ρ ≈ 1) as valid. It was withdrawn for that reason (§1).

**The calibration limit, stated plainly:** "ρ ≈ 1 means the prior" holds exactly only if the truths' departures
from the prior spread like the generators' departures.
- The truth set includes synthetic shapes (W1–W3, the q_3 tilt), whose departures δ_T are not in the committed
  records. I1 carries no absolute truth value, by its leak guard.
- **So ρ compares two spreads over different sets.** It is an indicator of the size of the bias relative to the
  model spread, not a measured fraction of the prior that is retained.

## 6. Reading (3): descriptive only (audit VR-1)

**Revision 2, coverage-5b-audit's VR-1 on #892 at `91c99caf`, accepted by the director on 2026-11-07:** reading
(3) carries no class and no combined sentence. It prints the quantities below and nothing else.

**Why:** the full per-cell pulls of the data against the prior were seen before this declaration (§0). Reading (3)'s
z_c is the same contrast against a larger covariance. A class such as "localized in the extra dimensions", which
needs only one valid pair at 3σ, was therefore foreseeable in some quadrants. A class name or a sentence would be
cited alone as a test result.

**Every operand of reading (3) was seen before,** as the per-cell pulls against Tune v1. So no blind version of
this reading is possible with these inputs.

**The revision-1 classes and sentence are withdrawn:**
- the quadrant status ("2D departure" and the others);
- the per-quadrant classes ("localized in the extra dimensions", "not localized at the resolved size", "not
  testable", "unresolved");
- the per-rule combined sentence.

No bar applies in this section.

**Its inputs:** f and the reported covariance C (I4); the prior g_P and its V_P = (`sigma_Vg_over_f`_P · f)² (I3).

**What is printed:**
- **Per cell, for all 16 cells:** the departure r_c = f_c/g_P,c − 1. Its covariance is
  R = diag(1/g_P) C diag(1/g_P) + diag(f² V_P / g_P⁴), and the pull is z_c = r_c/√R_cc.
- **Per quadrant**, over all four cells, the two-dimensional-level quantity (§3): r_Q = Σ_Q f / Σ_Q g_P − 1, its σ_Q
  from the same linearization with the full C on the quadrant's cells, and z_Q = r_Q/σ_Q.
- **Per rule X (V-ATLAS, V-PRIOR) and quadrant,** the cells valid under X. For every pair (i, j) of them:
  - the contrast r_i − r_j;
  - its σ_ij = √(R_ii + R_jj − 2R_ij), with the full covariance, including the correlation between i and j;
  - z_ij = (r_i − r_j)/σ_ij;
  - the resolved size 3σ_ij;
  - the axes, among E_avail, q_3 and W, on which the boxes of i and j differ. By §3, these are the only axes on
    which they can differ.
- **Per rule:** the number of contrasts printed. At most 4 × 6 = 24 per rule. Taken independently, the chance of
  at least one |z| ≥ 3 by chance among 24 is at most about 0.065.

**What reading (3) is citable for:** the printed quantities, labelled "computed after the pulls against the prior
were seen (L4)". It is not citable as a test, or for the words "localized" or "not localized".

## 7. Controls (any failure: exit 3, nothing classified, no reading printed)

| control | check |
|---|---|
| C-PIN | each of I1–I6 equals its `INPUTS.sha256` digest |
| C-CELLS | I1, I3 (each prediction except gibuu), I4 and I6 list R00–R15 in order; I5 has `reporting_cells` ids 0–15, each `reported` |
| C-BOX | I4's boxes equal I5's. The quadrants derived from the boxes equal §3's table. Within each quadrant, the (p_T, p_∥) box is identical, and any two cells differ in at least one of E_avail, q_3 and W |
| C-DOMAIN | gibuu's cells, each GiBUU-family truth's `p_parallel_lt_4p5.cells`, and the cells with p_∥ upper edge ≤ 4.5 are the same eight |
| C-TRUTHS | the T selection of §5.1 returns exactly the 10 named truths; I1 has 12 graded truths |
| C-BIAS | I1 and I2 have identical `bias` and `noise_sigma` for every truth, exactly |
| C-F | each prediction's f in I3 equals I4's f, to a relative 10⁻¹² |
| C-GF | each prediction's `g_over_f_minus_1` equals g/f − 1, to 10⁻¹² |
| C-COV | the reported covariance is symmetric to a relative 10⁻¹² and has a Cholesky factor; √diag/f equals I4 `relative_sigma.C_total_plus_C_resp_plus_C_PL5D` to a relative 10⁻¹² |
| C-RHO | the §5 classifier run on synthetic inputs: with b_T := −δ and the truth set equal to the generator set, ρ = 1 and the class is "not valid"; with b = 0, ρ = 0 and the class is "valid" |
| C-FINITE | every input array used is finite. Every stat σ, n_eff and g is positive |

## 8. The run, the outputs and the receipts

**The run.** It is made locally from a fresh clone at the bound commit with empty porcelain, after the pins are
compared:
`python3 -B valid_region.py read --repo <clone> --out <dir>`
- Exit codes: 0 readings; 3 STOP (a control failed); 4 refused (input or usage).
- No network, no cluster contact, and no file outside `<dir>` is written.

**The outputs** are `readout.json` and `readout.txt`:
- the controls;
- per cell: the A1–A3 inputs and class, the V-ATLAS class, S_b and S_g (four values each), ρ (four), the
  V-PRIOR class, the sensitivity classes, C_model's relative σ, r_c and z_c;
- per quadrant: r_Q and z_Q;
- per rule: V_Q, and every contrast with its axes and resolved size;
- the numbers of contrasts.

Reading (3) prints no class and no sentence (§6).

**The receipts** go in `receipts/read/`: the stdout and stderr of the run, the environment (Python and numpy
versions), and a `SHA256SUMS`.

## 9. Code, tests and mutation (before the binding)

**The code.** `valid_region.py` and `test_valid_region.py` land on this PR before the binding.
- **Every guard and every class boundary is tested in both directions:** each control fails on a perturbed input
  and passes on the clean one, and each bar is tested at, just inside and just outside its value.
- The tests use synthetic fixtures with the inputs' schema.

**The mutation harness,** `mutate_valid_region.py`, follows the per-period lane's design:
- in place, with the sha checked before and after;
- the child run with `PYTHONDONTWRITEBYTECODE`;
- a mutant counts only on the runner's "Ran N" line.

It has one mutant per control, per bar, per noise term, per domain rule, and for the threshold's direction. Every
mutant must be killed.

**As committed (revision 2):**
- `valid_region.py`, sha256 `896201cc9d03754ddac5185f548b1b7e3a56183dbb0fe6503fcd75c5c59d5433`;
- `test_valid_region.py`, sha256 `0df3207292ebd8c9e302f263eaa38e0012ef755940c95d311603d22916064580`, with 56 tests,
  all OK;
- `mutate_valid_region.py`: 48 mutants, 48 killed ([`mutants.txt`](mutants.txt)), run with Python 3.12.2 on the
  lane's machine on synthetic fixtures. No real input was read.

The mutants include the VR-1 guard: a reinstated class key in reading (3) is killed by `test_vr1_no_class_no_sentence`.

## 10. Licences

**CITABLE FOR:**
- per cell, the V-ATLAS and V-PRIOR classes, with their inputs as defined here;
- reading (3)'s printed quantities only: r_c, z_c, r_Q, z_Q and the contrasts, each labelled "computed after the
  pulls against the prior were seen (L4)";
- the record that the ATLAS User Guide states no prior-spread validity rule (§1, re-runnable).

**NOT CITABLE FOR:**
- **coverage.** No interval is validated, and the fake-data tests grade bias, not coverage;
- **a measurement.** The classes are diagnostics of the estimator on committed fake-data products and committed
  predictions. They are not a measured quantity, and they change no reported value;
- **any physics claim about the generators,** or about which model is right;
- **the cause of a departure,** or its location finer than the 16 cells;
- **V-PRIOR, or its threshold of 0.5, as ATLAS's,** or as the advisor's own formulation, which is known only as
  relayed;
- **a non-valid cell as excluded, wrong or unreported.** The reported result and its covariance are unchanged;
- **held-out truths.** The truths are not held out (`paper_body.tex:168`);
- **that the 2D mismodeling is localized in the extra dimensions, or that it is not,** in either direction;
- **reading (3) as a test** (§6, audit VR-1);
- **guide item 5.** It is not met (§4).

## 11. Limits

**L1: V-ATLAS likely rests in practice on A3,** if A1 and A2 pass everywhere as the values seen suggest (§0). A1's n_eff is the
simulation's, not the unfolded weights' (§4).

**L2: ρ compares two spreads over different sets** (§5.4). Its "≈ 1 means the prior" reading is exact only for
truths whose departures match the generators'.

**L3: few elements per spread.** S_g rests on 3 or 4 generators per cell, and S_b on 8 or 10 truths. Those truths
are correlated by family: four share the NuWro vertex.

**L4: reading (3) is not blind** (§0). The pulls against Tune v1 were seen before this declaration, so reading (3) is
descriptive only (§6).

**L5: the quadrant is the coarsest two-dimensional region.** "The identified region of the 2D mismodeling" is read
at quadrant granularity, because that is what the 16 cells resolve (§3). A finer two-dimensional region is outside
this reading.

## 12. Not changed

Nothing outside this directory is changed. In particular, these are unchanged: the reported result, R00–R15, every
covariance block, every fake-data readout, the paper and the note.
