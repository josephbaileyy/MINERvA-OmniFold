# M2 archive checks: truth spread and the metric (report)

**Run by** a Claude agent for the director, 2026-10-19 17:08–17:13 UTC, on Perlmutter login nodes, about 2 CPU-minutes, no batch job. Scripts, outputs and input hashes are in [`m2-archive/`](m2-archive/). The agent could not write this file itself, so the director saved its final report verbatim below.

**What it changes in [`M2-AUDIT.md`](M2-AUDIT.md).**
- **Q1.** The per-experiment truth is not "a half-simulation realization of G". It equals G on every fine cell that the pseudo-data half populates. Unpopulated cells lower a J cell by at most 0.2%, which is at most 1.4% of the null SD.
- **Q4a.** "V is roughly twice the production covariance" is withdrawn. V's diagonal matches the production null variances (median ratio 1.00). The whitened trace of 47, against 109 cells, comes from the Ledoit–Wolf shrinkage (λ = 0.0155) flooring about 80 near-degenerate correlation directions. This affects power only.
- The audit's other Q1 text fix still stands: below the fine grid the null is a family.

**CITABLE FOR:** these two measurements and their suggested text.
**NOT CITABLE FOR:** power at other shrinkage values (not measured), or a per-band split of the difference between pilot and production.

---



Both checks ran to completion. Check 1 shows the per-experiment truth equals G almost exactly, so "a half-MC realization of G" overstates it. Check 2 shows V's scale matches the production covariance and is not twice it. The factor ~2 below 109 comes from the Ledoit–Wolf shrinkage. That withdraws the audit's Q4a sentence.

`archive/REPORT.md` was not written: the harness refused my write ("subagents should return findings as text"), so the full report is here instead. The scripts and outputs are in `scratchpad/methods-m2/archive/`. Nothing was written under CFS, and no git checkout was edited (the local worktree is clean).

**How it ran.** On 2026-10-19, 17:08–17:13 UTC, on Perlmutter login16 and login15, using about 2 CPU-minutes with no sbatch or GPU. The interpreter was NERSC python 3.13.15 (numpy 2.5.2, scipy 1.18.0):
```
ssh perlmutter 'bash -lc "module load python; python -I code/m2_archive_checks.py code ."'        # run.log
ssh perlmutter 'bash -lc "module load python; python -I code/m2_shrinkage_and_truth.py code ."'   # run2.log
```
- **Production code is imported, not retyped.** The scripts call `j_matrix`, `Model.apply`, `statistics`, `ledoit_wolf` and `prediction` from `s5p_joint.py`, `s5p_inference.py` and `s5p_stage1_inspect.py` at 19b46af9. These files are byte-identical to the frozen 4f5a613f (`git diff` is empty).
- **One copied function.** `lw_at` is `ledoit_wolf` with the shrinkage intensity fixed, used only for the shrinkage scan.

**Inputs and hashes.** Every file was hashed from the exact bytes parsed. The lists are `inputs_sha256.tsv` (7,408 rows) and `inputs_sha256_followup.tsv`.
- **Archive files (7,183):** all match the archive's `SHA256SUMS` (1a72cb43…), 0 mismatches.
  - Calibration products: 1365 / 1366 / 1343 / 1751 / 1351 (MnvTune / GENIE CV / MEC / NuWro / GiBUU), exactly the recorded B values.
  - V (`V-s3v.npz`): 35979ef7…, equal to the design's pinned sha.
  - The five predictions μ_G: mnvtune bf7bd278…, genie_cv cfa42210…, genie_mec c179855d…, nuwro 475a2871…, gibuu 48917692….
- **Pscratch-only files (225):** these are not in the archive.
  - 10 lateral endpoint unfolds.
  - 21 data jitter and central files; the central file (fb5cc679…) equals its archive copy.
  - The 194 V-pilot products (seeds 965000–965199).
- **Repository files:** design 404446eb… (matches the frozen sha), joint-evaluate.json b9604502…, s5c contract d54fd7c9….

**Pipeline control.**
- Run on the archived products, the production `statistics()` reproduces the recorded unshifted null for all five nulls to ≤ 1e-12 relative. For MnvTune: T_total median / SD 49.2148 / 13.5534, T_shape 48.6613 / 14.6909.
- Rebuilding V from the 194 pilot products reproduces the frozen V to 7e-17 (shrinkage 0.015495).

---

### Check 1: per-experiment truth x_true against G (J cells; GiBUU on its 72-cell domain)

Column meanings:
- **x̂** is the raw unfolded J-cell vector. Its own relative SD is about 7.4% at the median and 12% at p90.
- **"T residual"** is what the test actually uses: x̂ plus the additive terms, minus (μ_G + ε).

| null | rel. SD of x_true/G−1 (median / p90 / max) | mean x_true/G−1 (median / max \|·\|) | SD(x_true)/SD(x̂), median / max | SD(x_true)/SD(T residual), median / max |
|---|---|---|---|---|
| MnvTune | 6.0e-6 / 1.3e-4 / 6.5e-4 | −4.3e-6 / 2.1e-3 | 7.9e-5 / 0.011 | 6.9e-5 / 0.0097 |
| GENIE CV | 6.6e-6 / 1.4e-4 / 6.3e-4 | −4.4e-6 / 2.1e-3 | 7.4e-5 / 0.010 | 6.1e-5 / 0.0063 |
| MEC | 6.0e-6 / 1.3e-4 / 6.6e-4 | −4.9e-6 / 2.0e-3 | 7.3e-5 / 0.009 | 6.1e-5 / 0.0059 |
| NuWro | 5.7e-6 / 1.8e-4 / 6.9e-4 | −4.5e-6 / 2.2e-3 | 6.8e-5 / 0.014 | 6.3e-5 / 0.0094 |
| GiBUU | 1.0e-6 / 5.9e-5 / 3.1e-4 | −2.7e-7 / 7.7e-4 | 9.8e-6 / 0.006 | 8.3e-6 / 0.0029 |

- **Mean offset in null-SD units:** at most 0.039 (NuWro).
- **Contribution to the statistic:** tr(W⁻¹C_xtrue) is at most 0.008, against about 47 for the full residual.

**Why it is this small (measured at MnvTune).**
- `true_xsec` divides half B's reweighted truth by half B's own completeness (`s5n_pseudo.py:170-186`). Since r_h is constant on each fine cell, every fine cell that half B populates equals the full-MC null value exactly. Non-zero values are identical across the 1,365 seeds to 1e-15.
- The only variation comes from empty fine cells: 1,348 of the 26,752 fine cells inside reported J cells are empty in half B for some seeds (median 11% of seeds), and are then 0.
- Control: refilling those empty cells collapses the spread to 3.7e-14, and the mean then equals G to 3.7e-14.
- So the small mean offset is a deterministic one-sided deficit of at most 0.2% per cell, not noise around G. It is large against its own standard error (up to about 150 SE) but tiny in physical terms.

**Q1 implication.** The paper should not say "the per-experiment truth is a half-MC realization of G". Suggested replacement: "the truth equals G on every fine cell populated in the pseudo-data half; unpopulated cells lower a J cell by ≤0.2% (SD ≤7×10⁻⁴), ≤1.4% of the null SD of the unfolded result." The half-MC noise does enter the pseudo-data and the unfolding, just not the truth.

---

### Check 2: metric W = V + diag Var(μ_G) against the production covariance

**Setup.** C_R is the covariance of R = F − (μ_G + ε), where F is x̂ with the production additive terms applied. ε is reproduced exactly with the production seeds, so no ε-free fallback was needed.

**Decomposition.** E[T_tot] = tr(W⁻¹C_R)·(n−1)/n + bᵀW⁻¹b, where b is the ensemble mean residual.

| null | tr: x̂ only / + additive / Var μ term / **full C_R** | bias term bᵀW⁻¹b | predicted mean T (= observed mean) | recorded median | SD of T (Gaussian prediction) | whitened eigenvalues max / median / min; effective count |
|---|---|---|---|---|---|---|
| MnvTune | 27.9 / 37.6 / 9.2 / **46.8** | 4.1 | 50.84 | 49.2 | 13.6 (10.2) | 2.02 / 0.28 / 0.025; 53 |
| GENIE CV | 32.5 / 36.6 / 64.6 / 101.3 | 429 | 530.6 | 527.7 | 58.4 (57.1) | 8.7 / 0.76 / 0.14; 53 |
| MEC | 26.6 / 30.8 / 65.6 / 96.4 | 312 | 408.6 | 406.0 | 38.7 (40.4) | 5.0 / 0.77 / 0.15; 73 |
| NuWro | 47.3 / 51.9 / 58.8 / 110.6 | 6214 | 6324.3 | 6323.9 | 174 (180) | 13.3 / 0.72 / 0.044; 34 |
| GiBUU | 16.4 / 19.9 / 44.1 / 64.2 | 1732 | 1796.0 | 1791.4 | 88.8 (90.7) | 5.8 / 0.79 / 0.054; 42 |

- **Shape statistic:** the linearized analog at MnvTune is 45.4 + 3.7 bias, against a recorded median of 48.7.
- **Generator nulls:** their T levels are dominated by the bias term (the unfolding's prior dependence), not by variance.
- **MnvTune tail:** T is heavier-tailed than a Gaussian residual predicts (SD 13.6 vs 10.2). The largest production whitened norm is 125, against 57 in the pilot.

**Why about 47 and not 109.**
1. **V's scale is right (measured).** Per cell, diag C_F(prod) / diag V is 0.90 / 1.00 / 1.14 (p10 / p50 / p90). Pilot-to-production per-cell SD ratio has median 1.00, and the two means agree to ≤ 0.12 SD.
2. **The cause is Ledoit–Wolf shrinkage on a nearly singular correlation matrix (measured).**
   - On the standardized scale V = (1−λ)S + λI, with λ = 0.0155.
   - The pilot correlation spectrum is extremely concentrated: three modes (62.9, 22.8, 11.8) carry 89% of the trace. 82 of the 109 eigenvalues are below λ, and 36 are below 1e-3.
   - Each eigenvalue e contributes e/((1−λ)e + λ). So even in-sample, on the pilot that built V, tr(V⁻¹S_pilot) = 33.1; at λ = 0 it would be exactly 109.
   - In effect the shrinkage floors about 80 near-degenerate directions, where V exceeds the true covariance by up to about 80×.
   - Shrinkage scan:

     | λ | tr(V_λ⁻¹C_F,prod) | tr(W_λ⁻¹C_R,prod) |
     |---|---|---|
     | 0 | 254 | 149 |
     | 0.001 | 116 | 110 |
     | 0.003 | 78 | 84 |
     | **0.0155** (frozen) | **40.6** | **46.8** |
     | 0.03 | 31 | 36 |
     | 0.1 | 20 | 22 |

     At λ = 0 the metric is overfit out of sample. Using the production covariance itself as the metric gives 109 by construction.
3. **Pilot to production, 33.1 → 40.6.** Production has more variance than V in about 12 directions (whitened eigenvalues up to 2.06).
   - Pilot outliers do not explain it: dropping the 10 largest pilot draws only moves 33.1 to 32.0.
   - Attributing it to MinosEfficiency being absent from the pilot is inferred, not isolated.
4. **Prediction MC error and bias.** Var(μ_G) adds 9.2, giving 46.8, and the bias term adds 4.1, giving mean 50.8 and median 49.2. For the generator nulls the Var(μ_G) term is 44–66, because the prediction's MC error reaches about 35% of W on some cells (p90).

**Q4a implication.**
- **Size is unaffected.** V is fixed and p-values are ranks against the calibration ensemble.
- **A pure rescaling of W leaves every p-value unchanged.** So "V's scale" alone has no effect; only its shape matters.
- **Shape effect.** T is a weighted χ² with whitened weights from 0.025 to 2.0. Compared with the production covariance's own (Mahalanobis) metric, it down-weights about 80 low-variance directions by up to about 40×. That costs power along those directions in exchange for stability.
- **Recorded power at 0.05 / 0.005** (claim rule with determinacy):
  - P1 and P2: 1.0 at both levels, total and shape.
  - P3: total 0.99 / 0.86, shape 0.93 / 0.23.
  - P1g shape: 0.95 / 0.74.
  - P2g total: 0.53 / 0.09.
  - P3g: about 0.01.
- Whether a different λ would raise P2g or P3g was not measured.

**Suggested paper text.** "W is the Ledoit–Wolf-shrunk (λ = 0.015) covariance of an independent 194-experiment pilot. Its diagonal matches the production null variances (median ratio 1.00), but the shrinkage floors about 80 of 109 near-degenerate correlation directions, so the whitened trace of the production null covariance is 47, not 109 (median T_total = 49). This affects power only."

**Not done.** The pilot/production difference was not isolated per band (that needs new pilot products), and power was not re-evaluated at other λ (that would be a design change).

### Files (in `scratchpad/methods-m2/archive/`; also in `/pscratch/sd/j/josephrb/methods-paper/m2-archive-20261019/`)
- `m2_archive_checks.py`, `m2_shrinkage_and_truth.py`, `probe_meta.py`
- `m2_archive_results.json`, `m2_shrinkage_and_truth.json`
- `inputs_sha256.tsv`, `inputs_sha256_followup.tsv`, `code_and_script_sha256.txt`
- `run.log`, `run2.log`
- `code/` — copies of the imported production modules, the design, the s5c contract and joint-evaluate.json