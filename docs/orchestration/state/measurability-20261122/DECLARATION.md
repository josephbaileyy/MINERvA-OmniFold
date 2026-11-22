# MSR DECLARATION: which combinations of the reported cells do the detector-level inputs constrain, and where do the known biases sit? (rev 1, 2026-11-22)

**By** tier3-design, for the director. **Authority:** Joseph via the director, 2026-11-22 ("yes can we do the measurability study"),
from an outside review of the note (Fix 2). **Base:** origin/main `7d5a98361`. **Compute:** the projections are local, at 0 node-h.
The two responses (2D and 5D) are built on the cluster in one login-node step (§8) under a separate go, with the fence and fresh
acks. Nothing is computed before this declaration, its read and the director's GO.

**Rev 1 (2026-11-22, the director's four items on rev 0 `889d9302`, before any computation):**
1. a floor on ‖β‖ below which S_poor is not read (§3.6);
2. a noise-max bar on Z_well for the noisy vectors (§3.6, §5.1);
3. k = 50 printed for T3's arms, with a rule against pairing it with M2's k = 5 sentence (§4, §5.2);
4. the C-DID construction check as a scripted, sha-compared test in connect P (§1, §6, §8).
<!-- absence-ok: a statement of this study's own order of work, not a claim that a result does not exist -->

**Rulings folded in (the director, 2026-11-22):**
- Q1: a cluster build of R, on a login node if light, otherwise one shared-QOS job of at most 0.1 node-h;
- Q2: T3's B0, MO and OP arms are operands;
- Q3: H2 truth cells, with the 16-cell biases taken through S1's functional map and R00–R15 printed alone;
- V_r includes the background and is at the data exposure;
- a split-half MC control;
- the cut, fixed with its basis;
- a section on how this differs from D-ID and FD-PRR's R-ID;
- C-RID as a STOP control;
- R-ID's use fixed before its values are seen (§5.2).

## 0. What this can say, and what it cannot

**It can say:**
- for each tested bias vector, how its size divides between the combinations of reported cells that the binned
  detector-level inputs constrain to 10 % or better at the data exposure, and those they constrain worse or not at all;
- whether, in the well-constrained combinations, the bias exceeds what the data could resolve (in units of the binned
  Cramér–Rao width);
- for T3's oracle arms (MO, OP), which of the two parts the true missed-event weights remove;
- how many combinations of the 16 reported cells each reco feature set (3D, 4D, 5D) constrains to 10 % or better.

**It cannot say:**
- a cause beyond "consistent with". "Consistent with an information limit" names where the bias lies. It is not a
  proof that no estimator could remove it, because binned Fisher information does not bound unbinned estimators or
  estimators that use prior information (D-ID §5);
- that any estimator change would fix a bias, or which one. Nothing is adopted;
- coverage or the validity of any interval;
- anything about the data. No data count, data unfold or data residual is read. The data enter only through the exposure
  scale of V_r (§3.2);
- note wording. Results go to the director first.

**NOT CITABLE FOR:** a cause beyond "consistent with", an estimator change, coverage, any data quantity, or note wording.

**What I saw before writing this.**
- Committed readouts: field names and structure only, with no values, for
  - FD-PRR (`readings`, `table`, `R-ID`, `R-SUP`; the R-ID field names `label`, `sigma_rel`, `null_fraction`,
    `n_cells_grid`, `n_null_modes`);
  - F0b (`truths[].bias`, `noise_sigma`; the truth names, groups, estimators and `n_experiments`);
  - T3 (top-level keys `schema`, `labels`, `verdict`, `controls`, `readings`, `table`; the table's arm, truth and split
    keys; the per-k field names). **T3's readout has no R-ID block**, and no per-cell bias vector;
  - IBUKT A2 (truth names; per-method `residuals`, `mean`, `noise_guard`, `departure`).
- The values I know from the note or the records: D-ID's published outcome (branch C; 121 of 144; the medians quoted in
  `sec_5d.tex:84`), and FD-PRR's B0 ρ(50) at A7 GiBUU and q3 as T3's declaration quotes them.
- No response, spectrum, width or projection has been computed.
<!-- absence-ok: a statement of this study's own order of work and of which fields were seen, not a claim that a result does not exist -->

## 1. Prior art, and how this differs

| study | what it did | how this study differs |
|---|---|---|
| **D-ID** (2026-10-10; `state/next-preparation-20261009/d-id/`, note `sec_5d.tex:84`) | Exact binned response from `of_inputs_5d.npz` at the 10,499 occupied reco cells; truth grids T1 (109 J cells), T2 (J split), T3 (fine). Fisher F = Rᵀ diag(1/(Rt+b)) R, which is the Gram matrix of the whitened R, so its eigenvectors are the right singular vectors and its eigenvalues are Σ². Per-functional CR widths, null fractions (cut 1e-12 relative), invisible share. Branch C: 121 of 144 eligible J residuals in functionals with CR width > 10 % at both truth resolutions | (a) **estimator:** the current reported route, FD-PRR / T3 configuration (e) and F0b's ensembles, in place of the retired GBDT; (b) **background:** V_r includes the expected background, where D-ID was signal-only; (c) **exposure:** the data exposure, the same as D-ID's "analysis exposure", but with background; (d) **truths:** FD-PRR / T3 at A7 GiBUU and q3, F0b's graded truths, A2's at 2D, in place of D1/W1/W3/q3/W2; (e) **2D:** new; (f) **cells:** the 16 reported cells R00–R15 on H2 truth cells, in place of the J cells; (g) **combinations:** it reads the bias along the constrained and unconstrained *combinations* of reported cells, not per functional; (h) **feature sets:** the 3D/4D/5D reco comparison is new |
| **FD-PRR R-ID** (2026-11-08; `FD-PRR-DECLARATION.md:201-208`, `prr_ibu.py:252`) | D-ID's `did.fisher` and `did.widths_from_eig` on the H2 response, prior and known term captured from the nominal truth's fold unfold (REF-G1's `unfold_experiment` on half A, ×2). Per reported cell: sigma_rel, null_fraction; n_cells_grid, n_null_modes. "Descriptive, read by nothing"; the note does not cite it | This study's 5D response **is that capture** (§3.1). R-ID enters only as the STOP control C-RID, under R-ID's own settings. The reading uses the full MC at weight ×1 with background, and combinations rather than cells |
| Coverage scoping R1, "identifiability ladder" (2026-10-22, `measurement-scoping/SCOPING.md:43,108,363`) | Proposed D-ID's Fisher at 2D–5D. Never run | This study is the first run of that question at 2D, and at 5D for the current estimator |
| pv2d/cmodel, pv-ladder H2, DECISION-20261024 | Singular values of S, the generator-spread factor of C_model (rank 3) | Not the response. Not used |
| s5e diagnosis (DIAGNOSIS-20260926 :145) | A capacity probe gave a better reco fit with no better truth, read as "part of the residual is weakly constrained" | Qualitative precursor only |
Search: identifiability ladder; singular value; response SVD; identifiab; weakly constrained; poorly constrained; Fisher; R-ID; Cramér–Rao (CATALOG, OUTCOME-*, DECISION-*, state/**/*.md, docs/analysis-note on main and on rewrite/journal-voice-20261121) @ 7d5a98361

**Does the new builder reproduce D-ID?** It is tested as C-DID (§6), at T1 with D-ID's own settings (full MC, same
sample, signal only, nominal weights). Whether C-DID gates is decided by a scripted test, not a judgment.
- **The test, C-DID-CONS, in connect P** (`msr_probe.py did-cons`):
  - it builds IBU-1's J world and D-ID's T1 grid, each through its own unchanged code, from the same events;
  - it writes four sorted lists: the J-cell truth definitions (fine-cell membership per J cell) and the occupied reco
    cells (flat indices), from each path;
  - it prints the sha256 of each list and their equality.
- **If both pairs are equal,** C-DID is a STOP control. **If either differs,** C-DID is a printed comparison, and the
  differing list is named.
- Rev 2 records which branch holds, from the probe's log, before connect B runs. The director sees that before giving the
  connect B go.

## 2. Operands

| operand | identity | role |
|---|---|---|
| 5D events | `of_inputs_5d.npz` sha256 `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f`, read from `/pscratch/sd/j/josephrb/t3p-20261121/stage/of_inputs_5d.npz` (T3's stage, this lane's) | R, t0, halves (§3.1) |
| 5D background | the bank `cv.npz` beside it, `t3p-20261121/stage/bank/cv.npz`, at the digest T3's stage recorded | b (§3.2) |
| 2D events | the CFS CV omnifile `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root` sha256 `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df`; the flux file `…/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root` `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` | R, t0, b at 2D through IBUKT's capture (§3.1) |
| T3 products | `t3p-20261121/runs/*.npz` for arms B0, MO, OP at A7 GiBUU (splits 991000, 994001–994004) and q3 (991000), at the sha256 in `run-20261121/cluster/log-floor/SHA256SUMS` | MO and OP bias vectors (§4) |
| FD-PRR readout | `fd/receipts-prr/read/cluster/readout.json` sha256 `9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead` | B0 bias and departure vectors (`table`); R-ID (control only, §5.2) |
| F0b readout | `fd/readout/fd_f0b_readout.json` `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b`; the with-C_PL copy `fd/with-cpl/readout/fd_f0b_readout.json` `5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6` (C-F0B only) | F0b bias vectors (§4) |
| T3 readout | `fd/tier3-20261110/run-20261121/cluster/read/readout.json` `b0362c387ec3d8fd48616abe5dcf589407fd007b62214d6297b47418d1a9ecce` | control C-T3 only (§6) |
| IBUKT A2 readout | `state/2d-closeout/ibukt-a2/readout.json` `dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6` | 2D bias vectors (§4) |
| D-ID tables | `d-id/outputs/tables.npz` `2aab22703747bfbc33247fe015213c5d9d0a65dcfc0074f0e3c53a1de29327a4` | control C-DID only |
| 3D/4D inputs | `methods-paper/re1-20261022/out/{3d,4d}/of_inputs_{3d,4d}.npz` on pscratch | sha256 and size recorded in the probe (§8), for the inventory. Not used: the feature-set comparison marginalizes the 5D reco cells (§3.4) |

Code reused unchanged and pinned at these sha256:
- `did.py` `d918c816…` (`fisher`, `widths_from_eig`, `share_matrix`);
- `prr_ibu.py` `fa913945…` (the capture and `r_id`);
- `ibu1.py` `f862a953…`;
- `ref_g1.py` `8e34c485…`;
- `s1_assemble.py` `b157250a…`;
- `t3p_read.py` `f4c221dd…`, for b_c on T3 products;
- `ref_c2c1.py` `285dd138…` (`binned_problem`);
- `run_ibukt.py` `f2b4c017…` and IBUKT `config.json` `60d6c4d7…`;
- `b1_projection.py` `b0cf7d0d…`, for `band_of`, `label`, `guard` and the two-driver pattern, imported, not copied.

## 3. Definitions

### 3.1 The response

- **5D.** The H2 truth cells (n_H = `n_cells_grid`, as the capture builds them) and the occupied reco cells of the capture's
  World, read from prr_ibu's capture path unchanged: REF-G1's World, `ibu1.half_from_experiment`, and the problem the fold
  unfold hands `did.ibu`.
  - R_ij is the expected reco count in cell i per unit truth count in H2 cell j, at the nominal within-cell prior shape.
  - t0 is the nominal truth count per H2 cell.
  - The reported-cell map L (16 × n_H) is prr_ibu's `maps`: each H2 cell spread over its fine cells by the prior shape
    (`did.share_matrix`), summed over the fine cells of each S1 row.
  - The main build uses the **full MC at weight ×1** (§3.2). The halves use the MC halves A and B, each at ×2 (§3.5).
- **2D.** IBUKT's capture (`run_ibukt.py:270-300`): `ref_c2c1.binned_problem` on the arrays the 2D driver hands OmniFold,
  with 224 reco bins and truth on `driver.PT_EDGES × PZ_EDGES`.
  - L is the selection of A2's 205 reported cells (`signed_identity.truth_indices`) from the truth grid. Truth bins outside
    the 205 are kept as parameters and marginalized.
- **Relative coordinates.** θ_j = t_j / t0_j. The reported quantities are φ_c = f_c / f0_c, with f = L t and f0 = L t0.
  The Jacobian is G = diag(1/f0) · L · diag(t0).

### 3.2 V_r: background included, data exposure

- **μ = R t0 + b** over reco cells, where b is the expected background per reco cell, the template the analysis subtracts.
- V_r = diag(μ). The data counts are Poisson, and only cells with μ > 0 enter (D-ID's AM-15).
- **Exposure.** The MC weights at ×1 are the data-exposure expectation. The data unfold uses the full MC at weight ×1, and
  the pseudo-data use half B at ×2 for the same reason (`M2-AUDIT.md` §Q1; `s5n_pseudo.build_data`). At 2D, the driver's
  POT scale is the one IBUKT's capture records, and the build prints it.
- **No data count enters.**
- **Printed variants, read by nothing except C-RID:**
  - signal-only (b = 0), as in D-ID;
  - half A at ×2 with the known term, as in R-ID.

### 3.3 Information, widths and combinations

- A = V_r^{-1/2} R diag(t0), and F = AᵀA. That is `did.fisher(R, t0, b)` with diag(t0) on both sides.
- **The constrained subspace.**
  - F's eigenvectors with eigenvalue ≤ 1e-12·max (D-ID's cut) span its null space N.
  - G_N is G's component in N. Its left singular vectors with singular value > 1e-6·‖G‖₂ span the **unconstrained
    subspace** U∞ of φ-space. A combination in U∞ moves the truth along a direction the binned inputs cannot see.
  - Q is the orthogonal complement of U∞.
- **The constrained widths.** C_φ = G F⁺ Gᵀ restricted to Q, where F⁺ is the pseudo-inverse on F's range. Its eigenpairs
  (s_k², w_k) give unit-norm combinations w_k of the reported cells, each with binned Cramér–Rao width s_k in relative units.
- **The cut.** Combination k is **well-constrained** if s_k ≤ 0.10. It is **poorly constrained** if s_k > 0.10 or it lies
  in U∞.
- **Basis of the cut.** It is D-ID's 10 % CR-width criterion, the same number, applied to a unit-norm combination of
  reported cells instead of to a single functional.
  - Relation to D-ID: a single cell c has width² = Σ_k (w_k·e_c)² s_k², so a cell is weak in D-ID's sense if, and in
    proportion as, it loads on poorly constrained combinations.
  - The threshold is fixed here and not tuned.
  - The partition at 0.05 and at 0.20 is printed and read by nothing.

### 3.4 The feature sets (5D only)

- The 3D and 4D reco feature sets are the 5D reco cells **summed** over the dropped reco coordinates: W for 4D; q3 and W
  for 3D. The 3D set is (p_T, p∥, E_avail), the 4D set adds q3 and the 5D set adds W (`nn_dump_inputs.py --axes eavail`
  and `eavail,q3`, RE1-AMENDMENT §2.2).
- The truth (H2), the reported cells (L), t0 and b are the same for all three sets, so the comparison isolates what each
  reco variable adds.
- The summation needs the reco cells to lie on a product grid. The build exports each occupied cell's multi-index and the
  reco edges, and the control C-MARG checks it.

### 3.5 The bias vectors (relative to the prior, on reported cells)

- **δφ_c = (X̂_c − X_c) / P_c**, FD-PRR's b_c (§4.1 there), with P the nominal prior and X the known truth.
- A bias given relative to the truth, e_c = X̂_c/X_c − 1 (F0b's `rel`, A2's e), is converted as δφ_c = e_c (1 + d_c), with
  d_c = X_c/P_c − 1:
  - for F0b, d from FD-PRR's table entry of the same truth name at split 991000 (the same truth files; control C-D);
  - for A2, d from A2's own `departure` (`ibukt.py:197`, truth/prior − 1).

### 3.6 The statistics

For a bias vector β (= δφ) with P_poor and P_well the orthogonal projectors onto the poorly and well-constrained
combinations (U∞ is part of P_poor):
- **S_poor = ‖P_poor β‖² / ‖β‖²**, the share of the bias's size in poorly constrained combinations (Euclidean, relative
  units). The isotropic reference dim(P_poor)/n_cells is printed beside it.
- **The floor on ‖β‖ (rev 1).** S_poor is undefined in the limit ‖β‖ → 0 and ill-conditioned near it. Its reading takes
  one of three forms:
  - **"no bias to locate":** ‖β‖₂ + h_β < 0.01, where h_β is the guard on ‖β‖₂ (§3.6 guard; 0 for a noise-free
    vector). No S_poor label is read.
  - **"unresolved at the floor":** the interval [‖β‖₂ − h_β, ‖β‖₂ + h_β] contains 0.01. No S_poor label is read.
  - **read normally:** ‖β‖₂ − h_β > 0.01.
- **Basis of the floor:** 0.01 is a 1 % relative norm over the reported cells, the scale of the 0.005 floor on r_well
  (§3.6) doubled. It is fixed here.
- **Z_well = max over well-constrained k of |w_k·β| / s_k**, the largest bias component in a well-constrained
  combination in units of its CR width at the data exposure. The χ² Σ_well (w_k·β)²/s_k², with dof n_well, is printed.
- **Z_well's multiplicity (rev 1).** Z_well is a maximum over n_well combinations, so a noisy vector has a positive
  expected Z_well even at zero bias.
  - **For a noisy vector** (F0b; A2), the same perturbations as its guard are applied to a **zero** vector, giving
    Z_noise = the 97.5 % point of Z_well under noise alone, printed beside each Z_well.
    - For F0b: 2,000 Gaussian draws with per-cell SD `noise_sigma`.
    - For A2: 2,000 Gaussian draws with per-cell SD equal to the sample SD of the five trials over √5, seed 20261122.
  - **FD-PRR and T3 vectors** are noise-free constructions at fixed splits (their split-to-split spread enters through
    the guard). They keep the plain rule, with no Z_noise.
- **For an arm A against B0** (T3, at the same truth and split):
  - r_poor = 1 − ‖P_poor β_A‖ / ‖P_poor β_B0‖;
  - r_well = 1 − ‖P_well β_A‖ / ‖P_well β_B0‖.

  r_well is computed only if ‖P_well β_B0‖ > 0.005 (half a percent of the relative scale); otherwise it is "no
  well-constrained component to remove".
- **The noise guard** (b1's, by its function):
  - **5-split / 5-trial vectors** (T3 at A7 GiBUU; A2): the statistic is computed on the mean vector, and also on each
    draw. h = 2.7764451051977987 · sd(per-draw values) / √5. The statistics are not linear, so the mean-vector value is
    read and the guard is descriptive.
  - **F0b vectors:** 2,000 Gaussian perturbations with per-cell SD `noise_sigma`, independent across cells (a declared
    approximation, since F0b's covariance N is not committed). h is half the 2.5–97.5 % range, and RNG seed 20261122.
  - **Single-split vectors** (T3 and FD-PRR at q3) have no guard and are secondary.

## 4. The tested bias vectors

| set | vectors | role |
|---|---|---|
| **5D-B0** | FD-PRR `table["B0/A7_gibuu/s<split>"].b` at the five splits (equal to T3's B0 by T3's C-PAIR, rechecked by C-T3) | **primary** |
| **5D-ARMS** | T3 MO and OP at A7 GiBUU, five splits, k = 5 (configuration (e)'s iteration count) | **primary** (M2) |
| 5D-ARMS at k = 50 | T3 B0, MO and OP at A7 GiBUU, five splits, and at q3, at k = 50, the k at which the note prints T3's values | **printed secondary**, under §5.2's pairing rule |
| **5D-F0b** | F0b's graded truths with n_experiments ≥ 16: nominal, W1, W2, W3, q3, stage0c_gibuu, A7_mnvtune, A7_genie_cv, A7_genie_mec, A7_nuwro, A7_gibuu | **primary** |
| 5D secondary | FD-PRR B0 and T3 B0/MO/OP at q3 (one split); F0b closure_nuwro (N = 0); F0b P-sets (ungraded) | printed, marked secondary |
| **2D-A2** | A2 OmniFold mean at nominal, genie_mec, nuwro (5 trials) | **primary** |
| 2D secondary | A2 OmniFold at bump, tilt, within_plus, within_minus; IBU K=5 and K=10 at every truth | printed, marked secondary |

No vector, truth, split, k or set not listed here is computed for reading.
<!-- absence-ok: a pre-declared scoping rule about this study's own vectors, not a claim that a result does not exist -->

## 5. Readings, fixed before any computation

### 5.1 Bands and labels

| statistic | band | range | sentence it licenses (t = the truth, D = 2D or 5D) |
|---|---|---|---|
| S_poor | **poor-dominated** | ≥ 0.8 | "At truth t (D), at least four fifths of the bias's size lies in combinations of the reported cells that the binned detector-level inputs constrain to worse than 10 % at the data exposure, or not at all." |
| | **mixed** | 0.2 to 0.8 | "…between a fifth and four fifths of the bias's size lies in poorly constrained combinations." |
| | **well-dominated** | ≤ 0.2 | "…at least four fifths of the bias's size lies in combinations the binned inputs constrain to 10 % or better." |
| Z_well | **below** | < 1 | "In every well-constrained combination, the bias is below one binned Cramér–Rao width at the data exposure." |
| | **intermediate** | 1 to 2 | "In at least one well-constrained combination, the bias is between one and two binned CR widths." |
| | **resolvable** | ≥ 2, and for a noisy vector also > Z_noise (§3.6) | "In at least one well-constrained combination, the bias is at least two binned CR widths: a component the binned data could resolve carries it." For a noisy vector that is ≥ 2 but ≤ Z_noise, the label is **"intermediate (within the noise maximum)"**. |
| r_poor, r_well | **removes most** | ≥ 0.5 | "Arm A removes at least half of B0's bias in the poorly (well-) constrained combinations." |
| | **removes part** | 0.2 to 0.5 | "…between a fifth and a half…" |
| | **no change** | −0.2 to 0.2 | "…changes it by at most a fifth, either way." |
| | **increases** | < −0.2 | "…increases it by more than a fifth." |

- **Edges.** An edge belongs to the band nearer the middle band (mixed, intermediate, no change).
- **A label is read only if [f − h, f + h] lies inside one band.** Otherwise it reads "unresolved across ⟨bands⟩", with
  b1's sentence form. A statistic that N-PREC (§6) or the MC control (§5.3) marks reads "numerically unresolved" or
  "MC-unresolved", with no reading.

**Combined statement per truth** (both statistics resolved). A vector below the floor reads **"no bias to locate"**
(or "unresolved at the floor") as its combined statement, whatever Z_well reads. Z_well is still printed.
- **consistent with an information limit:** S_poor poor-dominated **and** Z_well below. "At truth t, the bias lies in
  combinations the binned inputs constrain poorly, and is below the binned resolution in every well-constrained one.
  This is consistent with an information limit of the binned inputs; it does not show that no estimator could remove it."
- **points at a resolvable component:** Z_well resolvable, whatever S_poor reads. "At truth t, a well-constrained
  combination carries at least two binned CR widths of bias. This points at an estimator effect that the binned data
  could in principle resolve; it does not show that it is fixable, or how."
- **intermediate** in every other resolved case, with both labels reported and no summary sentence.

**Across truths, per set:** the same rule as b1's §3:
- "unresolved at ⟨truths⟩" if any primary truth is unresolved;
- otherwise "⟨label⟩ at every tested truth" if all agree;
- otherwise "truth-dependent", with each label reported.

### 5.2 Readings

- **M1 (primary):** S_poor, Z_well and the combined statement for every 5D-B0, 5D-F0b and 2D-A2 vector.
- **M2 (primary, the oracle arms):** r_poor and r_well for MO and OP against B0 at A7 GiBUU, by the bands above.
  - The licensed summary for MO: "the true missed-event weights remove mainly the poorly constrained part" if r_poor is
    "removes most" and r_well is "no change" or "removes part" (or there is no well-constrained component). The mirror
    sentence applies for the well-constrained part. Every other resolved combination is reported label by label.
  - OP is the bound on what step 2 can reach (T3 §3.3). It is read by the same bands and stated as that bound.
  - **The pairing rule (rev 1).** M2 reads k = 5, the reported estimator's iteration count. The note prints T3's values at
    k = 50. An M2 sentence at k = 5 must never be paired or juxtaposed with the note's k = 50 values, or with this
    study's k = 50 printout, as if they described the same unfold.
    - Every k = 50 line in the readout carries "k = 50, secondary; not M2".
    - Every M2 sentence names "k = 5".
- **M3 (5D, feature sets):** n_well and dim U∞ for the 3D, 4D and 5D reco feature sets, counting only MC-resolved
  combinations (§5.3). The licensed sentence: "With the ⟨D⟩ reco feature set, n combinations of the 16 reported cells
  are constrained to 10 % or better at the data exposure, and m are unconstrained." The difference between sets is
  stated as a count, with no cause attached. The principal angles between the well-constrained subspaces of
  consecutive sets are printed.
- **M4 (2D):** n_well and dim U∞ at 2D, by the same rule.
- **R-ID.** FD-PRR's committed R-ID values are used **only** as the STOP control C-RID (§6): reproduce them under R-ID's
  own settings.
  - They are not an operand, they enter no reading, and no new sentence about them is licensed.
  - I have seen the R-ID field names (`label`, `sigma_rel`, `null_fraction`, `n_cells_grid`, `n_null_modes`) and not
    their values.
  - The run prints them only inside C-RID's comparison.
- **Printed and read by nothing:**
  - the spectra s_k and the H2-level spectrum of F;
  - the partitions at 0.05 and 0.20;
  - the signal-only variant;
  - per-cell D-ID-style widths and null fractions at the data exposure with background;
  - R00–R15 alone (L = identity on the 16 cells, truth = the 16 cells), as Q3's comparison;
  - every secondary vector.

No band, cut, set, truth, k or exposure is changed after any statistic is computed.
<!-- absence-ok: a pre-declared rule about this study's own readings, not a claim that a result does not exist -->

### 5.3 The finite-simulation control (split-half R): only MC-resolved quantities are read

- The 5D and 2D responses, t0, b and L are also built from MC half A and half B, each at ×2.
  - 5D uses the split key of seed 991000, FD-PRR's.
  - 2D uses `s5c_pseudo.half_mask` at key 20261122.
- **A reading is MC-resolved** only if its band label is the same at full, half A and half B, and the partition is stable:
  - dim P_poor is equal at full and both halves;
  - ‖P_poor^A − P_poor^B‖₂ ≤ 0.2 and ‖P_poor^full − P_poor^X‖₂ ≤ 0.2 for X = A, B.

  Otherwise it reads "MC-unresolved".
- **A combination counts in M3/M4** only if:
  - it is matched across the halves (|w_k^A·w_j^B| ≥ 0.9 for its best partner j);
  - its widths at full, A and B lie on the same side of 0.10.
- Each half has half the MC, so this test is conservative for the full build.

## 6. Controls (a STOP control's failure stops every reading and goes to the director with its values; no repair round)

| id | check | bar | STOP? |
|---|---|---|---|
| C-OPS | every operand and pinned code file at its sha256 (§2) | exact | STOP |
| C-RID | under R-ID's own settings (half A at ×2, the fold unfold's prior and known term, `did.fisher`, `widths_from_eig`), the 5D capture reproduces FD-PRR's committed R-ID: `sigma_rel[16]` and `null_fraction[16]`, with ∞ matching ∞; `n_null_modes` and `n_cells_grid` exactly | finite sigma_rel relative ≤ 1e-6; null_fraction absolute ≤ 1e-6; the counts exact | STOP |
| C-DID-CONS | connect P: IBU-1's J-world and D-ID's T1 J-cell definitions and occupied reco cells, as four sorted lists compared by sha256 (§1) | exact | decides whether C-DID gates; recorded in rev 2 before connect B |
| C-DID | the J world at T1 under D-ID's settings (full MC, same sample, signal only) reproduces `tables.npz` `T1/nominal/widths_nom/{sigma_rel,null_fraction}` on the 183 functionals | as C-RID | STOP if C-DID-CONS is equal; otherwise printed |
| C-T3 | B0 at A7 GiBUU (five splits) and q3 recomputed from T3's products by `t3p_read`'s b_c equals FD-PRR's committed `table` b; the T3 readout's verdict is COMPLETE | 1e-12 absolute; exact | STOP |
| C-F0B | `truths[].bias` equal in the two F0b readouts | exact | STOP |
| C-D | for each F0b truth used, FD-PRR's table holds an entry of the same name at split 991000 with a 16-vector d | exact | STOP |
| C-A2 | A2's means recomputed from the five residuals equal `mean` (b1's C-A2) | 1e-15 | STOP |
| C-2D | the 2D capture's R, prior and nominal target reproduce A2's `signed_identity.checks` (`row_sum`, `numpy_K5`, `numpy_K10`) | relative ≤ 1e-9 | STOP |
| C-MARG | 5D reco cells lie on a product grid, and summing over W (or over q3 and W) conserves Σμ | exact cell map; relative ≤ 1e-12 | STOP |
| C-ROUTE | S_poor and Z_well by the eigen route equal those by an independent route (projectors from an SVD of A restricted through G) | 1e-10 + 1e-8·\|a\| | STOP |
| **N-PREC** | every eigen-decomposition with two LAPACK drivers (numpy `eigh`, scipy `eigh(driver="evr")`). A partition that differs, an S_poor or r that differs by > 0.01, or a Z_well that differs by > 1 % reads "numerically unresolved" for that vector | as stated | per reading |

**Synthetic tests before any real input** (`test_msr.py`):
- a toy R with a planted spectrum:
  - β in the poor subspace gives S_poor = 1, and β in the well subspace gives S_poor = 0;
  - Z_well equals the planted ratio;
  - a duplicated column puts its difference combination in U∞;
- the C-RID path on a fixture reproduces `prr_ibu.r_id`'s output exactly;
- the 3D/4D summation on a toy product grid equals direct binning;
- every band edge against §5.1;
- the ‖β‖ floor's three branches, and Z_noise on a zero vector (a fixture with a planted n_well, where Z_noise rises with
  n_well);
- the guard, the MC-resolution rule and the combined statements on hand-built cases;
- a line tracer runs every new line before the read.

## 7. Products and limits carried to the result

- **Products.** Code (`msr_build.py` for the cluster step, `msr_project.py` for the local step, `test_msr.py`), the
  fetched response files, `readout.json`, `readout.txt` and a REPORT go under this directory. They are committed before the
  results go to the director.
- **Limits:**
  - **Binned, local information.** Fisher widths assume the Poisson Gaussian limit and are local at the nominal
    expectation. They do not bound unbinned estimators or estimators that use prior information. Coarse truth cells hide
    within-cell freedom (optimistic), and binned reco hides reco information (conservative). Neither error is bounded
    here (D-ID §5).
  - **V_r** is at the nominal expectation for every truth, a linearization. Detector-systematic covariance is not in V_r.
    Only statistical constrainability at the data exposure is measured.
  - **The cut** is D-ID's number applied to unit combinations. It is a convention with a stated basis, not a physical
    threshold.
  - **The bias vectors** are those already measured, at development truths, on one simulated bank. Their noise is
    guarded as stated, not sampled anew.
  - **"Consistent with an information limit"** says where the bias lies, not that it cannot be removed.

## 8. The cluster step (scripts follow, each sha to the director before it runs)

- **Connect P, the probe** (0 node-h, login node). It also runs C-DID-CONS (§1, §6).
  - The fence: cov2d rev 2 at `3fbc9cbd`, plus an overlap check of this study's declared input set (§2) against the
    cov2d and rpd protected paths and limitation-resolver's flux2 input set, on fresh acks.
  - stat and sha256, with O_NOATIME, of every §2 input and of the 3D/4D inputs (for the inventory).
  - A PyROOT open of the 2D flux file with a real MnvH1D read, testing whether the MAT dictionaries are needed (the
    earlier lesson).
  - A timed build on a 2 % row subsample of each response under `/usr/bin/time -v`, printing wall time and peak RSS, with
    the full build's extrapolation.
  - It writes only under a fresh `$OUT` on pscratch, and nothing to CFS.
- **Connect B, the build.** On a login node if the probe's extrapolation is under about 30 min and 8 GB per response.
  Otherwise one shared-QOS job of at most 0.1 node-h, job name prefix **`msr_`**, which the director announces to every
  fenced lane first.
  - It builds the full, half-A and half-B responses at 5D and 2D, the R-ID-settings capture, the T1 capture and T3's
    B0/MO/OP b vectors. All are small npz files under `$OUT`, with a SHA256SUMS.
  - It reads with O_NOATIME, from pinned shas, in a fresh clone at a pinned commit, with nothing written to CFS. The
    files are fetched by dd streaming with a sha check.
- Everything after the fetch is local.

<!-- absence-ok: a declaration of an unrun study; "nothing is computed" describes its own order of work -->
