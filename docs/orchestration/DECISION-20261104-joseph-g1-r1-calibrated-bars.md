# DECISION 2026-11-04 — Joseph: REF-G1's R1 bars are calibrated by simulation, fixed before Δ is formed

**Recorded by** the paper-tighten lane, as director.

## What led to it

**REF-G1** is the 16-cell binned head-to-head (`REF-G1-DECLARATION.md`, PR #763; commissioned by
`DECISION-20261104-joseph-referee-analysis-commission.md`). Its reading R1 is T = Δᵀ C_Δ⁻¹ Δ over R00–R15, where
Δ = f_IBU − f_(e) and C_Δ = C_Δ,stat + C_Δ,univ + C_Δ,norm. As declared at #763's head 716e86df, R1 read the
uncorrected T against χ²₁₆ quantiles: agree at T ≤ 26.30, marginal up to 35.89, differ above. §8 left the bars open for
the director, who ruled them fine and undertook to put them to Joseph if the audit disputed them.

**The audit's dispute** (coverage-5b-audit, #763 comment 6645264150). C_Δ,stat is the sample covariance of 50 paired
replicas in 16 dimensions, so in the stat-dominated limit T's null is Hotelling's, (16·49/34) F(16, 34) = 23.06
F(16, 34), not χ²₁₆. When the estimators agree exactly:
- "differ" fires with probability 0.136, against the nominal 0.003;
- "marginal or differ" fires with probability 0.360, against the nominal 0.05;
- with the Hartlap-corrected T, the rates are 0.016 and 0.085.

The F quantiles of the Hartlap T are 29.39 and 46.09. The director reproduced every figure with `scipy.stats.f`. The
bias runs toward a false "differ", which licenses "the reported cells depend on the unfolding algorithm".

**The independent read** (Sonnet) is in `state/measurement-paper/5d-community-20261024/fd/consult-g1-r1-bars-20261104/`,
verbatim with SHA256SUMS. It confirms the numbers and recommends a Monte Carlo null at the realized composition, fixed
now, with the Hartlap/F bars as the fallback. Its findings:
- A finite-universe C_univ adds its own Hotelling-type inflation.
- C_norm is rank one along Δ. It shrinks T monotonically by about 0.4 % at T₀ = 36, so it cannot move the null.
- Every option leans toward "agree" if Δ's systematic part is smaller than the null assumes. That should be stated.

REF-G1 is declared and unbound at the time of this decision, so its readings have not been run.
<!-- absence-ok: scoping statement about an unbound declaration (#763 open), not a claim that a result is absent -->

## Joseph's answer, verbatim

Asked which thresholds REF-G1's R1 should use:

> Calibrated by simulation (Recommended)

sha256 of the text plus a final newline begins `a7ac558c5449d451`.

The option as put to him: the thresholds are set by simulating the comparison under "no difference" at the actual
uncertainty sizes, with the seed and recipe fixed now. They are committed before the difference itself is computed.
The textbook thresholds are printed but not used. The declaration states that the null leans slightly toward "agree"
if the two methods respond to systematics alike.

## What is decided

1. **R1's bars are the 0.95 and 0.997 quantiles of T's own simulated null** at the realized covariance blocks. The
   words and the licences (§5: agree, marginal, differ) are unchanged.
2. **The recipe is fixed in the declaration before binding.**
   - **Draws:** Δ* ~ N(0, Ĉ_stat + Ĉ_univ), and Ĉ_stat* re-estimated from 50 vectors (equivalently Wishart(49,
     Ĉ_stat)/49).
   - **C_univ:** Ĉ_univ* is resampled band by band with each band's declared universe count and S1's estimator. A
     deterministic ±1σ band is held fixed, and the declaration names which bands are which.
   - **C_norm:** C_norm* is formed from each draw's Δ*. The null never reads the realized Δ.
   - **T:** T* uses the production formula, uncorrected.
   - **Settings:** a fixed seed, and enough draws for the 0.997 quantile, at least 10⁶ unless the declaration shows
     a smaller count bounds its Monte Carlo error.
3. **Order.** The bars are computed from the covariances and committed, with their sha, before Δ is formed. The run
   stops if Δ is formed first.
4. **Self-check.** In the stat-only limit, the procedure's quantiles must match the F law's (29.39 and 46.09 for the
   Hartlap T, or 23.06 F(16, 34) for the raw T) within Monte Carlo error, or the run stops. A mutant that swaps in the
   χ² quantiles must be killed.
5. **Printed beside the reading, read by nothing:**
   - the χ²₁₆ bars (26.30, 35.89);
   - the Hartlap T against its F quantiles;
   - the bars under a stat-only null for Δ, as a labelled sensitivity.
6. **A stated direction.** The declaration says that the null treats the paired universe differences as scatter in Δ.
   If the two estimators respond to systematics alike, the reading leans toward "agree".
7. **Process.** limitations-catalog's commit a56db1c4d on #763 is the base. It is revised to items 2–6, and the
   auditor checks the delta. Then the director binds it.

Nothing is submitted, deposited or tagged.
