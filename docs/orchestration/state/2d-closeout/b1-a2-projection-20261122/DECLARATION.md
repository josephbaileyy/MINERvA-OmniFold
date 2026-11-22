# b1 DECLARATION: IBUKT A2's mean OmniFold residual pattern, projected onto Δ = E_R − published in V_pub's modes (2026-11-22)

**By** the `cov2d` session, for the director. **Authority:** Joseph's go of 2026-11-22 ("i authorizeit"), relayed by the
director with the scope in `~/codex-reports/note-measurement/methods-scoping-20261121/SCOPING.md` §b
(sha256 `64948c485de3df693c370f15c08cc07d9e2bb4d39a0ab27935b8edca718cb46c`), item b1. **Base:** origin/main `9ff419415`.
**Compute:** 0 node-h, local, no cluster connect.

**What this can say:** whether the E_R estimator's measured known-truth residual pattern, at the size A2 measured it, lies
along the 2D difference from the published result in V_pub's modes. **What it cannot say:**
- a cause of the shape difference. The note's "origin undetermined" stands unless Joseph decides otherwise;
- that E_R or the published result is right;
- the bias at the true data spectrum. A2 measured bias at seven fixed truths, not at nature's;
- anything about coverage, an estimator choice or note wording. Results go to the director first.

A decisive test needs MINERvA's unreleased intermediates (B-C, diagnosis-three-items §B3), which would need a contact. That is out
of bounds here.

**What I saw before writing this.** A structure dump of `readout.json` printed the first ~70 entries of the nominal truth's
trial-1 OmniFold residual vector. I know the published facts of the anatomy (χ² 465.415, K₇₃, the mode set M below) and the
A2 outcome's tables. Nothing below has been computed: not Δ, not V_pub's modes on this machine, and no projection.

## 1. Operands

| operand | identity | source |
|---|---|---|
| E_R | `xsec.root` sha256 `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef`, object `hXSec2D` | local copy `~/cov2d-work/figfetch/er-anc/xsec.root`; the digest bound in `2d-unfolding/ibukt/config.json:91` and the per-period `INPUTS.sha256:2` |
| p, V_pub | `cov_ptpl_minerva_inclusive_6GeV.root` sha256 `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3`: `pt_pl_cross_section`, `TotalCovariance`, `StatOnlyCovariance` | local copy `~/cov2d-work/figfetch/er-anc/`; bound at `ibukt/config.json:99`, `INPUTS.sha256:1`. The rounded text release is refused in its place |
| A2 residuals | `state/2d-closeout/ibukt-a2/readout.json` sha256 `dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6` (`OUTCOME-20261119-ibukt-a2.md`, "Score readout") | committed |

Loaders: `compare_to_paper_fullcov.flatten_ours`, `flatten_th2d`, `tmatrix_to_numpy` and `chi2_with_cov`, imported unchanged,
with ROOT 6.40.04, numpy 1.26.4 and scipy 1.17.1 (local figenv `rootmpl3108`). Global cell id = (p_T bin − 1)·16 + (p∥ bin − 1), the same
p_T-major order A2 uses. The run is pinned to one BLAS thread.

## 2. Definitions

- **Δ** = E_R − p on the 205 reported cells.
- **Modes.** V_pub = Σ λ_i u_i u_iᵀ by `np.linalg.eigh` (rank 0 = smallest), as the per-period benchmark
  (`per-period-benchmark-20261106/DECLARATION.md` §4) and `diagnose_tension.py:138` do. The sign of each u_i is fixed so that
  z_Δ,i = u_i·Δ/√λ_i > 0.
- **Mode sets, as the per-period benchmark fixed them before any group reading:**
  - **K₇₃**: the 73 largest-λ modes;
  - **K̄**: the other 132;
  - **M**: Δ's six largest contributors, eigh ranks {23, 9, 118, 2, 79, 121} (`tension_report.txt:18-23`). All six are in K̄;
  - K₂₀₅: all modes. Printed only.
- **The bias pattern.** For method m, truth t and trial s, A2's signed fractional residual is e_s,c = estimate/known − 1
  (IBUKT-DECLARATION §6). The pattern in cross-section units is **β_s = e_s ⊙ E_R**, and **β = mean over the 5 trials**. That is
  A2's mean b times E_R: the shift E_R would carry if the estimator's fractional bias at truth t held on data. As a sensitivity,
  e ⊙ p is printed and read by nothing.
- **Primary statistic, the share along Δ:** over a mode set K,

  g_K = Σ_{i∈K} z_β,i z_Δ,i / Σ_{i∈K} z_Δ,i²,  with z_β,i = u_i·β/√λ_i.

  This is the fraction of Δ's whitened component along itself that the bias pattern supplies, at the size A2 measured. g = 1:
  the pattern alone supplies Δ's component along Δ. g = 0: it is orthogonal, or too small to matter. g < 0: it points away from Δ.
  g is linear in β, so the five trials' noise does not bias it.
- **Per mode:** ρ_i = z_β,i / z_Δ,i for i ∈ M. This is the same share in a single mode.
- **Noise guard:** A2's own: h = 2.7764451051977987 · sd_s(f_s)/√5, with f_s the statistic on trial s's β_s and sample sd
  (ddof 1). By linearity, f(β) equals the mean of the f_s. As in A2, this is a descriptive guard, not a confidence interval.
- **Printed and read by nothing:**
  - the cosine in whitened K coordinates;
  - q_K = S_K(β)/S_K(Δ), raw and with the noise term removed (S_K of each trial's deviation from the mean, averaged with
    divisor 4, divided by 5);
  - the unit-amplitude remainder S_K(Δ − β)/S_K(Δ);
  - K₂₀₅;
  - the e ⊙ p sensitivity;
  - the same quantities for IBU K=5 and IBU K=10 at every truth.

## 3. Readings, fixed before any projection

**Primary truths** (SCOPING §b names "nominal and generator truths"): **nominal, genie_mec, nuwro**, method **OmniFold** (A2's
E_R-configuration workflow). **Secondary truths**, labelled by the same bands and marked secondary: bump, tilt, within_plus,
within_minus.

**Bands** for g_K and for each ρ_i:

| band | range | sentence it licenses (t = the truth, K = the mode set) |
|---|---|---|
| **candidate** | ≥ 0.5 | "At truth t, the E_R estimator's A2 mean residual pattern supplies at least half of Δ's component along Δ in K. Estimator bias of this pattern is a candidate contributor to the difference in these directions. It is not shown to be the cause." |
| **partial** | 0.2 to 0.5 | "…supplies between a fifth and a half of Δ's component in K: a partial contributor at most." |
| **minor** | −0.2 to 0.2 | "…supplies at most a fifth of Δ's component in K, either way. This weakens this bias pattern as a main contributor in these directions." |
| **opposite** | < −0.2 | "…points away from Δ in K. Removing it would increase the distance." |

**A label is read only if the whole interval [f − h, f + h] lies inside one band.** Otherwise the reading is **"unresolved
between ⟨band⟩ and ⟨band⟩"**, naming the bands the interval touches. A band edge belongs to the band nearer zero, except 0.5,
which belongs to candidate.

**Readings:**
- **R1 (primary):** g_K₇₃ at each primary truth.
- **R2:** g_K̄ at each primary truth. K̄ is where V_pub is poorly determined. R2 is read by the same bands, and its sentence says
  "in the 132 poorly determined directions of the published covariance".
- **R3:** ρ_i for each i ∈ M at each primary truth: "reproduces mode i" only in the candidate band.
- **Secondary truths:** R1–R3 labelled in the same way and marked secondary. They do not enter the combined statement.

**Combined statement, per mode set (R1 and R2 separately):**
- all three primary truths candidate → "candidate at every tested truth";
- all three minor → "weakened at every tested truth";
- all three opposite → "opposite at every tested truth";
- anything else → "truth-dependent". Each truth's label is then reported, and no summary sentence is drawn.

No band, set, truth, scaling or mode is changed after the projection. A mode-set or truth not listed here is not computed for
reading.
<!-- absence-ok: a pre-declared scoping rule about this projection's own sets and truths, not a claim that a result does not exist -->

## 4. Controls (any failure stops the run before a reading, and goes to the director with its values; no repair round here)

| id | check | bar | basis |
|---|---|---|---|
| C-OPS | sha256 of the two ROOT copies and of `readout.json` equal §1 | exact | |
| C-CELLS | `StatOnlyCovariance` diag > 0 gives 205 cells; `TotalCovariance` diag > 0 gives the same set; every A2 truth's `cells` vector equals that set in ascending order | exact | A2 used "the exact positive-StatOnlyCovariance 205-cell publication mask; pT-major order" (IBUKT-DECLARATION §3) |
| C-PUB | `chi2_with_cov(E_R − p, TotalCovariance)` reproduces 465.4152721915331 | relative ≤ max(1e-8, 10 κ₂ ε) on the 205-cell block | per-period C-PUB. The κ-scaled bar is COV2D's A5 rule as `fd/tier2-20261110/T2-BINDING-1.md` Addendum 1 ruling 1 applies it, since this machine's LAPACK differs from the cluster's |
| C-SUM | the eigenmode sum over 205 modes equals the C-PUB χ² | relative ≤ max(1e-6, 10 κ₂ ε) | per-period C-SUM, same κ scaling |
| C-K | the count of λ/λ_max > 1e-4 is 73, and S₇₃(Δ)/205 is within 0.0005 of 0.662 | exact; print precision | per-period C-K |
| C-M | at eigh ranks {2, 9, 23, 79, 118, 121}, λ/λ_max and \|z_Δ\| reproduce `tension_report.txt:18-23` | 4 significant figures; ±0.005 | per-period C-M. It identifies M; a rotated or reordered mode fails here, not silently. A failure confined to modes that N-PREC marks numerically unresolved is recorded, and those modes are not read. Any other failure stops |
| C-A2 | the mean and noise guard recomputed from the five OmniFold residuals equal `readout.json`'s `mean` and `noise_guard` at every truth and cell | absolute ≤ 1e-15 | the operand is the committed readout |
| C-LIN | g_K(β) equals the mean of g_K(β_s), and the same for ρ_i | relative ≤ 1e-10 | code check of the linearity the guard rests on |

**N-PREC, the numerical-precision rule** (T2-BINDING-1 Addendum 1 ruling 3, applied here before any projection). Every
quantity is computed with two LAPACK drivers: numpy `eigh` and scipy `eigh(driver="evr")`, signs fixed by z_Δ,i > 0 in both.
- A mode i ∈ M whose z_Δ,i or z_β,i (at any primary truth) differs by more than 1 % between the drivers is **numerically
  unresolved**. Its ρ_i is printed, and no R3 label is read.
- A g_K that differs by more than 0.01 (absolute) between the drivers, or whose band label differs between them, reads
  **"numerically unresolved"** for that truth and set.
- The per-mode driver differences are printed for all 205 modes.

**Tests before the run:** synthetic inputs where β = Δ gives g = 1 and every ρ_i = 1; β = −Δ gives −1; and β orthogonal to Δ in
the whitened K coordinates gives 0. Each band edge is tested against the rules of §3.

## 5. Products and limits carried to the result

- Code, outputs and a REPORT go under this directory: `b1_projection.py`, its test, `readout.json`, `readout.txt`.
  They are committed before the results are read out to the director.
- **Limits:**
  - Δ is treated as fixed. E_R's own noise is not propagated, as in the per-period readings, which are conditional on p.
  - A2's bias comes from 5 Poisson draws on one simulated bank with the nominal response. The bank's finite-simulation and
    learner-seed effects are not sampled.
  - The truths are development stresses (IBUKT-DECLARATION §4), not the data's truth.
  - A candidate reading names a candidate. A minor reading weakens only this pattern at these truths. Neither one is a cause.
