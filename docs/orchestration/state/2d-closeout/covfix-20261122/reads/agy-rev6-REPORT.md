<!-- absence-ok: verbatim third-party read report -->
GO

<!-- absence-ok: verbatim third-party read report -->
# Audit Report: COVFIX Pre-Registration Declaration (Draft Rev 6)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** agy (Independent Technical Review)  
**Target:** `inputs/COVFIX-DECLARATION.md` (Draft rev 6, 2026-11-23)  
**Prior Reports & Context:** `inputs/agy-rev5-REPORT.md` (NO-GO on rev 5), `inputs/rev5-to-rev6.diff`  
**Verdict:** **GO**. Setting aside the administrative binding prerequisites (committed iris receipt, fresh PG session, director's passphrase wrapper), draft rev 6 is **ready to bind**. All 2 BLOCKING, 3 MAJOR, and 3 MINOR findings from the rev 5 audit (Findings 1–8) are **CLOSED**. No new BLOCKING or MAJOR defects are introduced by the rev 6 diff. Two minor editorial/notational observations are documented below with concrete fixes, neither of which blocks binding.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of Rev 5 Findings (Findings 1–8)

<!-- absence-ok: verbatim third-party read report -->
Every finding from [inputs/agy-rev5-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/agy-rev5-REPORT.md) is resolved in rev 6:

<!-- absence-ok: verbatim third-party read report -->
| # | Prior Finding | Rev 5 Severity | Rev 6 Status | Rev 6 Location | Summary of Resolution |
|---|---|---|---|---|---|
| **1** | Calibration law bias grid undefined for $K_0$ and $K_A$ | **BLOCKING** | **CLOSED** | [Lines 754–759](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L754-L759) | Bias grid explicitly defined using each candidate's own bias block $V_b$ carried to $t$: $C_{\text{model\_abs}}$ (rank 3, 6 points) for $K_0$ and $K_A$; $C_b$ (rank $\le 4$, $\le 8$ points) for $K_B$; and projected $C^\top V_b C$ for $K_C$. |
| **2** | Replicate budget and seed omitted for binomial cutoff estimation | **BLOCKING** | **CLOSED** | [Lines 736–740](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L736-L740) | The 20,000 single-error replicate budget under §6.2's law with $b = 0$, random seed `9_992_000`, candidate/truth stratification, and Clopper–Pearson intervals for $\hat{q}$ and $\hat{p}_i$ are fully restored. |
| **3** | Per-band normalization ambiguity for $F_{\exp}$ | **MAJOR** | **CLOSED** | [Lines 703–710](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L703-L710) | Expected spread ratio is formalized per band as $F_{\exp,R} = \frac{N-1}{N}(1 - u_R)$ with band-specific undrawn share $u_R$, and normalized ratios $\tilde{F}_R = F_R^F / F_{\exp,R}$ labelled per band. Formula extended to $K_C$ on $P_k$. |
| **4** | Inconsistent SE formula in $k \ge 25$ reporting floor illustration | **MAJOR** | **CLOSED** | [Lines 831–834](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L831-L834) | Unnormalized SE formula replaced with normalized standard error $\sqrt{2/((N-1)k)}$ for independent Gaussian modes; edge distances (5.1/6.8 SE at $N=100$, 10.3/13.3 SE at $N=300$) are mathematically exact. |
| **5** | Computational explosion of whole-rule testability simulation in local P2 | **MAJOR** | **CLOSED** | [Lines 769–777](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L769-L777) | Disclosed approximation reduces inner bootstrap resamples within the simulation loop from 2,000 to 200 (a 10$\times$ reduction in evaluations); P2 laptop execution is bound with walltime recorded; formal escalation path to director-approved priced node run is provided. |
| **6** | Stale "inconclusive" reference in §5.1 line 580 | **MINOR** | **CLOSED** | [Lines 586–587](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L586-L587) | Line updated to: *"If K0 is VALIDATED at both sealed truths (§6.4), the comparison showed no need for a change at those truths, and the outcome is 'no challenge' (§7)."* Stale "inconclusive" removed. |
| **7** | Stale reference to Grok in §8 line 860 | **MINOR** | **CLOSED** | [Line 884](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L884) | Replaced with *"a codex-school2 and an agy read (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`)"*, aligning with Joseph's decision. |
| **8** | Seed block nomenclature standardization | **MINOR** | **CLOSED** | [Lines 187, 210, 317, 453, 614, 703, 705, 706, 749, 751](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L187) | Inconsistent variants (`C08`, `C_seed`, `seed term`) replaced throughout normative text with `c08` or "the seed block c08". |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Technical Audit of Rev 6 Diff & Detailed Checks

<!-- absence-ok: verbatim third-party read report -->
### 2.1 Ensemble Counts (26,400 at P2 and 17,600 at PV)
- **Diff Text (Lines 769–771):**
  > *"inside the simulation, each ensemble's guards use 200 bootstrap resamples (seed 9_995_000) instead of the readout's 2,000. That keeps the work to about 26,400 ensembles at P2 and about 17,600 at PV."*
- **Audit:**
  1. *Category / Phrasing Conflation:* The phrasing *"That keeps the work to about 26,400 ensembles at P2..."* conflates the number of simulated ensembles with the computational work per ensemble. Reducing the inner bootstrap resamples from 2,000 to 200 reduces the *total bootstrap evaluations* by a factor of 10 (from $\sim 52.8\text{M}$ to $\sim 5.28\text{M}$ at P2, and from $\sim 35.2\text{M}$ to $\sim 3.52\text{M}$ at PV). The number of simulated ensembles is determined by the outer simulation grid loop, which was already $\sim 26,400$ in rev 5.
  2. *Grid-Derived Arithmetic:*
     - In rev 5, agy derived 26,400 from: $3 \text{ candidates} \times 4 \text{ truths} \times 11 \text{ grid settings} \times 200 = 26,400$ ensembles.
     - In rev 6, because the bias grid is tailored to each candidate's own bias block (Finding 1):
       - $K_0$ and $K_A$ have $V_b = C_{\text{model\_abs}}$ (rank 3), yielding $b = 0$ plus $2 \times 3 = 6$ points $= 7$ false-FAIL points, plus 2 deficit false-PASS points $= 9$ total grid settings.
       - $K_B$ has $V_b = C_b$ (rank $\le 4$), yielding $b = 0$ plus $\le 8$ points $= 9$ false-FAIL points, plus 2 deficit points $= 11$ total grid settings.
       - $K_C$ has projected $C^\top V_b C$ (rank $\le 4$), yielding $\le 11$ total grid settings.
     - Consequently, the exact maximum ensemble counts are:
       - **At P2 (4 truths):** $K_A$ (4 truths $\times 9$ settings $\times 200 = 7,200$) + $K_B$ ($4 \times 11 \times 200 = 8,800$) + $K_C$ ($4 \times 11 \times 200 = 8,800$) = **24,800 ensembles**.
       - **At PV (2 truths):** $K_0$ ($2 \times 9 \times 200 = 3,600$) + $K_A$ ($2 \times 9 \times 200 = 3,600$, if ST1 fired) + $K_B$ ($2 \times 11 \times 200 = 4,400$) + $K_C$ ($2 \times 11 \times 200 = 4,400$) = **16,000 ensembles** (or **12,400 ensembles** if ST1 did not fire).
  3. *Severity & Assessment:* **MINOR**. The text explicitly qualifies both counts with *"about"* (24,800 is about 26,400; 16,000 is about 17,600). The simulation loop definition in §6.2 is algorithmic, unambiguous, and deterministic. Computational safety is guaranteed by lines 773–777, which bound P2 laptop runtime with recorded walltime and provide an explicit escalation path to a director-approved priced run if needed.

<!-- absence-ok: verbatim third-party read report -->
### 2.2 The Band Expected Spread ($u_R$) Formula
- **Diff Text (Lines 705–710):**
  > *- the total's expected 1/N spread ratio is F_exp = ((N − 1)/N)·(1 − u), with u = tr(V_F⁺ [C_PL(t) + c08(t)])/ndf_F;*  
  > *- a band R's is F_exp,R = ((N − 1)/N)·(1 − u_R), with u_R = Σ_{i∈R} u_iᵀ[C_PL(t) + c08(t)]u_i / λ_i^F / ndf_R;*  
  > *- both use the carried, unscaled blocks.*  
  > *- What is labelled is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. u, u_R and F_exp are printed. Where f̂_R scaled V_F, u and u_R are approximations, and that is disclosed.*  
  > *- For K_C, the same definitions apply on P_k, with Cᵀ(·)C in place of each block.*
- **Audit:**
  1. *Mathematical Exactness:* For an error vector drawn with covariance $V_{F,\text{drawn}} = V_F - [C_{\text{PL}} + c08]$, the $i$-th mode variance $v_i^F$ under $V_F$'s eigenbasis has expectation $\mathbb{E}[v_i^F] = \frac{N-1}{N} [1 - (u_i^F)^\top (C_{\text{PL}} + c08) u_i^F / \lambda_i^F]$. Averaging over the $ndf_R$ kept modes in band $R$ yields:
     $$\mathbb{E}[F_R^F] = \frac{N-1}{N} \left(1 - \frac{1}{ndf_R} \sum_{i \in R} \frac{(u_i^F)^\top [C_{\text{PL}}(t) + c08(t)] u_i^F}{\lambda_i^F}\right) = \frac{N-1}{N}(1 - u_R).$$
     Dividing by $F_{\exp,R}$ yields $\mathbb{E}[\tilde{F}_R] = 1$ for every band, resolving the $\sim 1\%$ to $2\%$ artificial bias present in rev 5.
  2. *Partition Consistency:* Summing across bands gives $\sum_R \frac{ndf_R}{ndf_F} u_R = \frac{1}{ndf_F} \operatorname{tr}(V_F^+ [C_{\text{PL}} + c08]) = u$, preserving total trace conservation.
  3. *Subspace Consistency:* For $K_C$, line 710 maps all blocks to $P_k$ via $C^\top (\cdot) C$, ensuring $u_R$ is rigorously evaluated on the projected subspace.
  4. *Notational Polish:* Line 706 writes $u_i$ rather than $u_i^F$ alongside $\lambda_i^F$. In context (§6.1 "Fluctuation readings, against V_F in V_F's carried basis"), this is unambiguous, but $u_i^F$ is preferable for strict consistency with line 231.
  5. *Severity & Assessment:* **Mathematically sound**. The notational polish is **MINOR**.

<!-- absence-ok: verbatim third-party read report -->
### 2.3 Normalized Standard Error Formula for $k \ge 25$ Reporting Floor
- **Diff Text (Lines 831–834):**
  > *- **K_C's floor k ≥ 25** is a reporting floor. For independent Gaussian modes, the SE of the normalized spread ratio F̃ is √(2/((N − 1)k)). The low and high "covers" edges then sit at about 5.1 and 6.8 SE at N = 100, and 10.3 and 13.3 SE at N = 300.*
- **Audit:**
  1. *Mathematical Derivation:* For $k$ independent Gaussian modes, the sample variance of mode $i$ is $v_i = \frac{N-1}{N} s_i^2$, where $(N-1) s_i^2 \sim \chi^2(N-1)$. The normalized ratio is $\tilde{F} = \frac{F}{(N-1)/N} = \frac{1}{k} \sum_{i=1}^k s_i^2$. Because $\operatorname{Var}(s_i^2) = \frac{2}{N-1}$, the variance of the average across $k$ independent modes is $\operatorname{Var}(\tilde{F}) = \frac{2}{(N-1)k}$, giving:
     $$\mathrm{SE}(\tilde{F}) = \sqrt{\frac{2}{(N-1)k}}.$$
  2. *Numerical Verification:*
     - At $N = 100, k = 25$: $\mathrm{SE} = \sqrt{2/2475} \approx 0.028427$. Guard $h = t_{0.975, 99} \cdot \mathrm{SE} \approx 1.9842 \times 0.028427 \approx 0.056405$.
       - Low edge distance: $(1.0 - 0.8 - h) / \mathrm{SE} = 0.143595 / 0.028427 = 5.051 \approx \mathbf{5.1}\text{ SE}$.
       - High edge distance: $(1.25 - 1.0 - h) / \mathrm{SE} = 0.193595 / 0.028427 = 6.810 \approx \mathbf{6.8}\text{ SE}$.
     - At $N = 300, k = 25$: $\mathrm{SE} = \sqrt{2/7475} \approx 0.016357$. Guard $h = t_{0.975, 299} \cdot \mathrm{SE} \approx 1.9679 \times 0.016357 \approx 0.032189$.
       - Low edge distance: $(1.0 - 0.8 - h) / \mathrm{SE} = 0.167811 / 0.016357 = 10.259 \approx \mathbf{10.3}\text{ SE}$.
       - High edge distance: $(1.25 - 1.0 - h) / \mathrm{SE} = 0.217811 / 0.016357 = 13.316 \approx \mathbf{13.3}\text{ SE}$.
  3. *Severity & Assessment:* **CLOSED**. Completely verified and mathematically rigorous.

<!-- absence-ok: verbatim third-party read report -->
### 2.4 Per-Candidate Bias Grids
- **Diff Text (Lines 752–759):**
  > *- **b,** a fixed bias, one per grid point:*  
  >   *- b = 0;*  
  >   *- b = ±√κ_j w_j for each nonzero eigenpair (κ_j, w_j) of the **candidate's own bias block** V_b, carried to t:*  
  >     *- for K0 and K_A, V_b = C_model_abs (rank 3, so 6 points);*  
  >     *- for K_B, V_b = C_b (rank at most 4, so at most 8 points);*  
  >     *- for K_C, the projected CᵀV_bC.*  
  >     *That is the bias at one allowance-σ along each of the block's directions, at most 9 grid points.*
- **Audit:**
  1. *Structural Completeness:* Baseline $K_0$ (unconditional) and repaired candidate $K_A$ (named exception) now have an explicitly specified bias block $V_b = C_{\text{model\_abs}}$ carried to $t$. Because $C_{\text{model}}$ is constructed from 3 vertices (§2 line 189), its carried rank is exactly 3, producing 3 nonzero eigenpairs and 6 grid points.
  2. *Allowance Calibration:* Each non-zero point sits at exactly one allowance-$\sigma$ along a principal axis ($b^\top V_b^+ b = 1$). Including $b = 0$, $K_0$ and $K_A$ evaluate 7 false-FAIL points; $K_B$ and $K_C$ evaluate at most 9 false-FAIL points.
  3. *Subspace Evaluation for $K_C$:* For $K_C$, line 757 specifies the projected block $C^\top V_b C$ on $P_k$, matching line 710 and line 800.
  4. *Deficit Evaluation:* The deficit false-PASS simulation (§6.2 line 780) evaluates $b = 0$ and the grid point maximizing pass rate (2 points), yielding a maximum of 9 total grid settings for $K_0/K_A$ and 11 for $K_B/K_C$.
  5. *Severity & Assessment:* **CLOSED**. Completely verified and mathematically sound.

<!-- absence-ok: verbatim third-party read report -->
### 2.5 Global Consistency Check Across the Full Document
A line-by-line cross-check of `COVFIX-DECLARATION.md` rev 6 confirms:
1. *No Stale Outcomes:* "inconclusive" appears only in historical changelog entries (lines 106, 147); §5.1 lines 586–587, §6.4 lines 806–813, and §7 lines 838–858 uniformly use "no challenge".
2. *Second Reader Identity:* Grok appears only in historical revision notes; §8 line 884 and §9.2 line 903 correctly specify `codex-school2` in alignment with `DECISION-20261123-joseph-covfix-ki85-size-reader.md`.
3. *Seed Block Nomenclature:* Standardized on `c08` or "the seed block c08" across all normative text (lines 187, 210, 317, 453, 614, 703, 705, 706, 749, 751).
4. *Budget, Ceilings, and Pricing:* Table 3 prices (lines 254–263) match phase specifications in §3.1–§3.4 and the ST6 cumulative ceiling ($\sim 409$ node-h).

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Binding Readiness & Open Prerequisites

<!-- absence-ok: verbatim third-party read report -->
Setting aside the binding prerequisites, **rev 6 is ready to bind**.

<!-- absence-ok: verbatim third-party read report -->
The three binding prerequisites identified in §9.3 ([lines 904–907](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix6/inputs/COVFIX-DECLARATION.md#L904-L907)) are administrative and procedural actions outside the text of the declaration:
1. **Committed iris receipt:** A committed cluster balance receipt confirming $\ge 409$ node-h available.
2. **Fresh PG session:** Designation and setup of the independent director session for seal generation.
3. **Director's passphrase wrapper:** Generation of the director's passphrase and wrapper script piping to stdin.

<!-- absence-ok: verbatim third-party read report -->
None of these represent defects in `COVFIX-DECLARATION.md`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 4. Summary of New Findings, Severity & Concrete Fixes

<!-- absence-ok: verbatim third-party read report -->
The rev 6 audit identifies two minor editorial/notational observations:

<!-- absence-ok: verbatim third-party read report -->
### New Finding 1: Conflation of Work Metric and Ensemble Count in §6.2
- **Severity:** **MINOR**
- **Location:** Line 770–771
- **Description:** Line 770 states: *"That keeps the work to about 26,400 ensembles at P2 and about 17,600 at PV."* Reducing inner bootstrap resamples from 2,000 to 200 reduces the *bootstrap evaluations per ensemble*, not the number of ensembles. Furthermore, with $K_0$ and $K_A$ having 9 grid settings instead of 11, the actual maximum ensemble counts are 24,800 at P2 and 16,000 at PV (or 12,400 if ST1 does not fire).
- **Concrete Fix:** Update lines 770–771 to read:
  > *"That keeps the bootstrap work to about 5.0 million resamples across the ~24,800 ensembles at P2 and about 3.2 million across the ~16,000 ensembles at PV."*

<!-- absence-ok: verbatim third-party read report -->
### New Finding 2: Eigenvector Subscript Consistency in $u_R$ Formula
- **Location:** Line 706
- **Severity:** **MINOR**
- **Description:** Line 706 writes $u_i^\top [C_{\text{PL}}(t) + c08(t)] u_i / \lambda_i^F / ndf_R$. Line 231 defines $u_i^F$ and $\lambda_i^F$ for $V_F$'s eigenbasis. Writing $u_i$ without superscript alongside $\lambda_i^F$ is slightly informal.
- **Concrete Fix:** Update line 706 to write $u_i^F$:
  > *"a band R's is F_exp,R = ((N − 1)/N)·(1 − u_R), with u_R = Σ_{i∈R} (u_i^F)ᵀ[C_PL(t) + c08(t)]u_i^F / λ_i^F / ndf_R;"*

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Conclusion & Recommendation

<!-- absence-ok: verbatim third-party read report -->
Draft rev 6 successfully closes all prior blocking and major issues. The statistical formulations, candidate-specific bias grids, binomial cutoff calibration budgets, normalized standard error bounds, and simulation workload approximations are sound, consistent, and ready for pre-registration.

<!-- absence-ok: verbatim third-party read report -->
**Verdict: GO.** Binding may proceed once the director supplies the administrative prerequisites (§9.3).
