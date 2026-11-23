<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
# Review of COVFIX Pre-Registration Declaration (Draft Rev 7)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** Antigravity (agy) — Confirming Technical Read  
**Target:** [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md) (Draft Rev 7, 2026-11-23)  
**Baseline Documents:** [codex2-rev6-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/codex2-rev6-REPORT.md), [rev6-to-rev7.diff](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/rev6-to-rev7.diff), [DECISION-20261123.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/DECISION-20261123.md)  
**Report Destination:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/report.md`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Executive Summary

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative binding prerequisites (§9 item 3: committed iris receipt, fresh PG session, and director's passphrase piping wrapper), **Draft Rev 7 is NO-GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
Rev 7 makes outstanding progress by successfully closing all 12 of codex-school2's Rev 6 issues. In particular, the adoption of the spectral map $L$ resolves the drawn-covariance decomposition conflict, the 20,000-draw reference bank puts fallback cutoffs on sound ground, the replacement of the inner bootstrap with analytic delta-method guards eliminates 319 million inner resamples, the fixed grid for $K_C$ ($k \in \{25, 50, 73\}$) bounds P2 workload, the salt-committed seeds and authenticated writer manifest plug custody loopholes, and the three-part outcome table provides an exhaustive outcome taxonomy.

<!-- absence-ok: verbatim third-party read report -->
However, the new diff introduces **two MAJOR mathematical/specification defects**, leaves an **unresolved MAJOR textual contradiction in the policy bars summary in §9**, and introduces **three MINOR drafting defects**:
1. **MAJOR (Internal Policy Bar Contradiction):** Line 1029 (§9 item 4) explicitly states *"testability at 0.20 false-FAIL and 0.10 deficit pass"*, directly contradicting the newly calibrated Rev 7 gates bound in §6.2 (line 895) and §6.5 (line 933), which set the per-truth deficit pass gate to **0.05** (at most 12 of 400).
2. **MAJOR (Dimensional Error in ST1 N5 Guard):** Lines 426–427 state that for N5, the sampling variance of the ratio $\hat{s}_i / (u_i^\top S1_B u_i)$ *"is added with the analytic variance of a sample covariance's projection, $2(u_i^\top S1_B u_i)^2/(R - 1)$"*. This directly adds an unnormalized quantity with dimensions of covariance-squared to a dimensionless ratio variance. The correct delta-method formulation adds the *relative* variance $2/(R - 1)$.
3. **MAJOR (Incomplete Algebraic Specification of Scenario D2):** Unlike D1 and D3, which provide explicit algebraic formulas and scale definitions ($s = 1.25/a$ and $\beta^2 = (1.25 - a)\mathrm{ndf}/(w_j^\top V^+ w_j)$), scenario D2 (lines 889–890) specifies scaling only in words without defining the total band projector $P_R^{\mathrm{tot}}$, the band fluctuation share $a_R$, or the scale factor $s_R = 1.25/a_R$.
4. **MINOR (Omission of Band Spread $\tilde{F}_R$ in Influence Function Specification):** Line 282 explicitly specifies $\mathrm{SE}(\tilde{F}) = \mathrm{SE}(F^F)/F_{\exp}$ but omits the explicit band analogue $\mathrm{SE}(\tilde{F}_R) = \mathrm{SE}(F_R^F)/F_{\exp, R}$.
5. **MINOR (All-Block Rebuild Cost Discrepancy in ST1 Scale Note):** Line 454 quotes $202.35$ node-h for an all-block rebuild plus redraw. This figure was inherited from Rev 6 and omits the 200 N5 replicas (38.00 node-h) added to PX in Rev 7 line 474 (which raises the all-block rebuild plus redraw to $240.35$ node-h).
6. **MINOR (Sign Ambiguity in Scenario D3):** Line 891 defines $\beta^2$ but does not explicitly specify whether both signs $b = \pm \beta w_j$ or only the positive root are simulated.

<!-- absence-ok: verbatim third-party read report -->
Because a pre-registration must be unambiguous and internally self-consistent before cryptographic sealing and execution, these defects must be surgically corrected in a Rev 7.1 before binding.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of codex-school2 Rev 6 Fixes 1–12

<!-- absence-ok: verbatim third-party read report -->
| Fix # | Severity (Rev 6) | Status in Rev 7 | Key Lines in [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md) | Disposition Summary |
|---|---|---|---|---|
| **Fix 1** | BLOCKING | **CLOSED** | Lines 708–714, 807–814, 864–878 | Bound one decomposition via spectral map $L = \sum_R \sqrt{\phi_R} P_R$. Applied $L(\cdot)L^\top$ to constituent blocks; defined undrawn part $U = L(C_{\mathrm{PL}} + c08)L^\top$ and drawn part $V_{\mathrm{drawn}} = V_F - U$; used in $u$, $u_R$, $F_{\exp}$, and calibration law. Defined $\delta$ as probability-centered shifts from G2R `data_g2r.npz`; mapped by $L$ and carried by $D_t$; bound fallback to $N(0, V_{\mathrm{drawn}}(t))$; and refused $F_{\exp} \le 0$. |
| **Fix 2** | BLOCKING | **CLOSED** | Lines 820–839, 913–916 | $q$ and $p_i$ reference probabilities are always estimated from the 20,000-draw single-error bank at seed 9_992_000 under $b = 0$, including fallback (analytic 0.6827 removed). 0.6827 is named a fixed content target. Conservative 95% Clopper–Pearson interval endpoints used (lower for "under", upper for "over"). Sentinels ($-1, N+1$) reported as "no under-flag (flag impossible at this N)". Size guarantees explicitly conditioned on interval coverage. |
| **Fix 3** | BLOCKING | **CLOSED** | Lines 276–284, 876–899, 930–935 | Inner bootstrap eliminated; grading and calibration unified with identical analytic delta-method guards. Ensembles increased to 400. Per-truth gates bound to 0.10 (not-PASS) and 0.05 (deficit pass) using one-sided 95% Clopper–Pearson bounds (permitting $\le 29/400$ and $\le 12/400$, respectively), giving candidate-level false-FAIL $\le 0.20$ via union bound. Defined explicit deficit scenarios D1–D3; recorded P-2 pass rate separately from whole-rule PASS; excised 0.025/0.075 guarantee claims; made all rate statements conditional on surrogate scenarios. |
| **Fix 4** | MAJOR | **CLOSED** | Lines 562–564, 765, 770–773, 900–904 | $K_C$ top-$k$ search restricted to fixed grid $k \in \{25, 50, 73\}$. Bound evaluation order: cheap bars (P-1 to P-4 without simulation) evaluated first from largest to smallest $k$, running simulation only for the single passing $k$. Bound P2 synthetic benchmark (stop for priced allocation if $> 8$ CPU-hours). Timed PV path via synthetic seal test on exclusive node. |
| **Fix 5** | BLOCKING | **CLOSED** | Lines 545–559, 621–627, 639–642, 653–658 | Director-held seeds committed with random salt ($\mathrm{sha256}(\mathrm{seed\ base} \parallel \mathrm{salt})$) and revealed after PV readout. Seed-bearing job scripts and logs captured into encrypted seal. Cooperative assumption explicitly recorded for shared Unix account. Writer writes authenticated manifest binding ciphertexts, IDs, inputs, and outputs to seal and freeze digests. Readout verifies writer manifest and `P2-FREEZE.sha256` before decryption. Replaced interactive `age` with batch `gpg --batch --passphrase-fd 0 --symmetric --cipher-algo AES256`. Cleanup limited to campaign-owned temporary paths. |
| **Fix 6** | BLOCKING | **CLOSED** | Lines 496–505 | Consumption record keyed by **seal digest and role** (PV writer, PV readout). Freeze digest bound to seal at first acquisition; later freeze digest never resets consumption. Transition to "spent" atomically persisted before releasing plaintext. Post-decrypt crash is terminal stop with no retries. Executability fixes barred from altering grading after exposure or amending §§5–7 after seal decryption. |
| **Fix 7** | BLOCKING | **CLOSED** | Lines 423–428, 439–475 | Projected denominator modes filtered at $> 10^{-12} \times$ maximum. Specified analytic variance addition for $N_4 - N_2$ and $N_5$. Bound explicit sequences for W1 trigger, W2 trigger, unexplained firing, and later firing. Formulated post-fix acceptance check in common basis requiring "covers" in every band. Itemized PX regeneration (including N5 replicas at 38.00 node-h). Bound stop and repricing before any new paid work. Highlighted scale thresholds (202.35 and 420.09 node-h). |
| **Fix 8** | MAJOR | **CLOSED** | Lines 333–336, 481–489, 517–522 | Excised prefix polling from sacct in favor of serialized reservation ledger under `flock`. Pinned cumulative ceiling at 409.22 node-h. Persisted intent entries before submission; bound reconciliation of lost job IDs via sacct submit window before subsequent submissions. Kept reservations open through accounting lag. Removed 6-missing-toys allowance: required 100% completeness for all P1 arms, N5 replicas, PX diagnostics, and PV truths (max 2 same-seed retries; missing toy is terminal UNRESOLVED). |
| **Fix 9** | MAJOR | **CLOSED** | Lines 607–609, 664–667, 942–979 | Excised §4.3 model family license; confined license strictly to the two named deformations under the declared toy law. Replaced outcome table with exhaustive three-part taxonomy: Part 1 (construction finding), Part 2 (baseline challenge), Part 3 (selected candidate). Bound coexistence of Part 1 and Part 3. Resolved 02a fallback to substitute only for 02b absence, clarifying that novelty exclusion of 02b excludes 02a too. Restricted UNRESOLVED resolution to newly authorized tests. |
| **Fix 10** | MAJOR | **CLOSED** | Lines 251–253, 380–388, 405–413 | Bound lateral and normalization shifts to act on unfolded outputs, matching COV2D §4.2. Pinned sim random stream to `[seed_s, DRAW_SALT, 2]`. Formulated non-cancelling rounding check $\sum_{\mathrm{rows}} \vert \mathrm{round}(\lambda^+) - \lambda^+ \vert / \sum_{\mathrm{rows}} \lambda^+$ per cell with $\sum \lambda^+ > 0$ ($> 10^{-3}$ refuses; zero-count cells counted). Bound A1f and A1p side-by-side reporting in common carried $K_0$ basis. Pinned A1 ratio file sha256 digests; designated $C_{\mathrm{model}}$ lineage as RE-2 part C §7 statement unverified here; named them the named deformations. |
| **Fix 11** | MAJOR | **CLOSED** | Lines 706–707, 733–735, 751–754, 762–769, 817–819 | Bound directed residual $\|(I - P_{B,\mathrm{kept}}) U_{A,\mathrm{well}}\|_2 \le 0.1$ in reference frame at $x_R$. Bound single cutoff rule ($10^{-12} \times \lambda_{\max}$) across rank checks, grading, and calibration. Assigned degenerate edge clusters straddling band edges to lower-rank (higher-variance) band, and top-$k$ clusters included whole. Bound measurability study inputs (committed records only), commit sha provenance, and freeze timing. Introduced $C_b^0 = \sum_t \beta_t \beta_t^\top$ for member-wise bound; restricted frame identity to ordinary inverses. Defined outside-span fraction in whitened retained coordinates $W_F \hat{\beta}_u$. |
| **Fix 12** | MINOR | **CLOSED** | Lines 212–214, 936–938 | Corrected 142-eigenvector wording: rank fell by one (from 205 to 204), eigenvectors had components outside new span, and trace is a separate diagnostic. Qualified Gaussian SE formula $\sqrt{2/((N-1)k)}$ as an equal-variance benchmark illustration, noting unequal variances alter effective dimension. |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Technical Audit of New Machinery in Rev 7

<!-- absence-ok: verbatim third-party read report -->
### 2.1 Analytic Delta-Method Guards (§2 lines 276–284)
- **Mean Ratio $M$ Influence Function:**
  $$M = \frac{1}{\mathrm{ndf}} \sum_{i=1}^{\mathrm{ndf}} q_i = \frac{1}{N} \sum_{s=1}^N \left( \frac{1}{\mathrm{ndf}} \sum_{i=1}^{\mathrm{ndf}} z_{s,i}^2 \right) = \frac{1}{N} \sum_{s=1}^N \frac{\chi^2_s}{\mathrm{ndf}}$$
  Because $M$ is identically the sample mean of independent per-toy terms $Y_s = \chi^2_s/\mathrm{ndf}$, the per-toy influence term $\psi_s = \chi^2_s/\mathrm{ndf}$ has $\mathrm{sd}_s(\psi_s)/\sqrt{N} = \sqrt{\frac{1}{N(N-1)}\sum_{s=1}^N (\psi_s - M)^2}$. This is **exact** for the standard error of the sample mean. The total band analogue is identically exact.
- **Spread Ratio $F$ Influence Function:**
  The mode spread is $v_i = \frac{1}{N} \sum_{s=1}^N (z_{s,i} - m_i)^2$. The statistical functional for variance $\sigma^2(P) = \int (z - \int z' dP)^2 dP$ has empirical influence function $\mathrm{IF}(z_s; \sigma^2) = (z_{s,i} - m_i)^2 - v_i$. Averaging across modes $i \in R$:
  $$\psi_s = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} \left[ (z_{s,i} - m_i)^2 - v_i \right]$$
  Notice that $\sum_{s=1}^N \psi_s = 0$ identically, so $\mathrm{mean}_s(\psi_s) = 0$. The sample standard deviation $\mathrm{sd}_s(\psi_s) = \sqrt{\frac{1}{N-1}\sum_{s=1}^N \psi_s^2}$. Dividing by $\sqrt{N}$ yields the standard first-order delta-method / empirical influence function standard error for the sum of sample variances. Crucially, summing across modes $i \in R$ *before* taking $\mathrm{sd}_s$ naturally and rigorously captures all mode-mode covariance in the toy fluctuations.
- **Normalized Ratio $\tilde{F}$:**
  $\tilde{F} = F^F / F_{\exp}$. The denominator $F_{\exp} = \frac{N-1}{N}(1 - u)$ is a deterministic scalar constant computed strictly from the frozen candidate matrix $V_F$, $U = L(C_{\mathrm{PL}} + c08)L^\top$, and $N$. Because $F_{\exp}$ is non-stochastic, $\mathrm{Var}(\tilde{F}) = \mathrm{Var}(F^F) / F_{\exp}^2$, and $\mathrm{SE}(\tilde{F}) = \mathrm{SE}(F^F)/F_{\exp}$.
- **Defects Identified:**
  1. **MINOR:** Line 282 states `for F̃, SE(F^F)/F_exp`, but omits the explicit band formula `and for a band F̃_R, SE(F_R^F)/F_exp,R`. Because band spread $\tilde{F}_R$ is an active guarded reading in P-1 (line 909), this should be explicitly stated.
  2. **MAJOR (ST1 N5 Guard Formulation):** Lines 426–427 state: *"For N5, S1_B is itself estimated from the 200 replicas. Its sampling variance is added with the analytic variance of a sample covariance's projection, $2(u_i^\top S1_B u_i)^2/(R - 1)$, with $R = 200$."* In ST1, the reading is the ratio $r_i = \hat{s}_i / (u_i^\top S1_B u_i)$, where the estimated block sits in the **denominator**. The variance of a Wishart projection $D_i = u_i^\top S1_B u_i$ is $\operatorname{Var}(D_i) = 2(u_i^\top S1_B u_i)^2 / (R - 1)$. Directly adding this dimensional covariance-squared quantity to the variance of a dimensionless ratio is dimensionally incorrect. By the delta method, the relative variances add:
     $$\frac{\operatorname{Var}(r_i)}{r_i^2} \approx \frac{\operatorname{Var}(\hat{s}_i)}{\hat{s}_i^2} + \frac{\operatorname{Var}(D_i)}{D_i^2} = \frac{\operatorname{Var}(\hat{s}_i)}{\hat{s}_i^2} + \frac{2}{R - 1}$$
     Under the null $r_i \approx 1$, the variance increment to $r_i$ is $2/(R - 1)$, NOT $2(u_i^\top S1_B u_i)^2/(R - 1)$.

<!-- absence-ok: verbatim third-party read report -->
### 2.2 The Spectral Map $L$ (§5.2 lines 708–714)
- **Mathematical Soundness:**
  $L = \sum_R \sqrt{\phi_R} P_R$, where $P_R = \sum_{i \in R} u_i F_A u_i^\top$ is the orthogonal projector onto $F_A$'s band-$R$ eigenspace at $x_R$, and $\phi_R = \hat{f}_R$ where triggered and $1$ elsewhere. Because $F_A$ is symmetric, eigenspaces are mutually orthogonal, so $L = L^\top$ and $L F_A L^\top = \sum_R \phi_R P_R F_A P_R$, exactly scaling the eigenvalues of $F_A$ by $\hat{f}_R$ in band $R$.
- **Consistency of Constituent Blocks:**
  Mapping every constituent block via $L(\cdot)L^\top$ yields:
  $$V_F = L F_A L^\top = L(\mathrm{universe} + \mathrm{stat} + c08 + C_{\mathrm{PL}})L^\top = V_{\mathrm{drawn}} + U$$
  where $U = L(C_{\mathrm{PL}} + c08)L^\top$ and $V_{\mathrm{drawn}} = L(\mathrm{universe} + \mathrm{stat})L^\top$. Both $U$ and $V_{\mathrm{drawn}}$ carry via $D_t (\cdot) D_t$ and project for $K_C$ via $C^\top (\cdot) C$.
- **Resolution of Edge Cases:**
  Lines 706–707 resolve degenerate clusters straddling band edges by assigning the entire cluster to the lower-rank (higher-variance) band. This removes all sorting ambiguity for degenerate subspaces.

<!-- absence-ok: verbatim third-party read report -->
### 2.3 The 20,000-Draw Reference Bank (§6.1 lines 836–850)
- **Procedure:**
  20,000 single-error draws are simulated under §6.2's law at $b = 0$, at seed 9_992_000, per candidate and truth. This estimates joint $q$ and per-mode $p_i$ directly, eliminating the flawed Gaussian fallback assumption that $H = W V_{\mathrm{drawn}} W^\top = I$.
- **Conservative Cutoffs & Sentinels:**
  Cutoffs use the conservative end of each 95% Clopper–Pearson interval (lower end for "under" at level 0.025, upper end for "over"). If no integer $k$ satisfies $P(\mathrm{Bin}(N, q) \le k) < 0.025$, the sentinel $-1$ is assigned, and lines 845–846 and 913–916 explicitly mandate reporting *"no under-flag (flag impossible at this N)"*.
- **Conditional Scope:**
  Lines 847–848 correctly state that flag size guarantees are conditional on the bracketing event of the Clopper–Pearson intervals.

<!-- absence-ok: verbatim third-party read report -->
### 2.4 The 400-Ensemble Gates & Clopper–Pearson Endpoints (§6.2 lines 876–897, §6.5 lines 930–935)
- **Exact Binomial Calculations ($n = 400$):**
  - **False-FAIL Gate (0.10 one-sided 95% Clopper–Pearson upper bound):**
    For $k$ "not PASS" outcomes out of 400, the one-sided 95% Clopper–Pearson upper bound $p_U$ satisfies $\mathrm{Beta}(0.95; k + 1, 400 - k) \le 0.10$.
    - For $k = 29$: $p_U = 0.097539 \le 0.10$ (**passes**).
    - For $k = 30$: $p_U = 0.100355 > 0.10$ (**fails**).
    Therefore, the gate permits **at most 29 of 400**.
  - **False-PASS Deficit Gate (0.05 one-sided 95% Clopper–Pearson upper bound):**
    For $k$ whole-rule pass outcomes out of 400 in any defined deficit scenario, $p_U$ satisfies $\mathrm{Beta}(0.95; k + 1, 400 - k) \le 0.05$.
    - For $k = 12$: $p_U = 0.048154 \le 0.05$ (**passes**).
    - For $k = 13$: $p_U = 0.051176 > 0.05$ (**fails**).
    Therefore, the gate permits **at most 12 of 400**.
- **Union Bounds:**
  - False-FAIL: $0.10$ per truth $\implies \le 0.20$ candidate-level false-FAIL over two truths via Bonferroni union bound.
  - False-PASS: $0.05$ per truth in each scenario $\implies \le 0.05$ validation probability for a candidate failing at either truth, and $\le 0.15$ union bound across at most three candidates.
- Both gate counts (29/400 and 12/400) and stated union bounds are **mathematically exact**.

<!-- absence-ok: verbatim third-party read report -->
### 2.5 Deficit Scenarios D1–D3 (§6.2 lines 886–897)
- **Baseline Expectation:**
  With drawn fluctuation $\phi = \delta + g$, $\operatorname{Cov}(\phi) = V_{\mathrm{drawn}}$. The expected contribution to $M = \frac{1}{\mathrm{ndf}} \sum_s e_s^\top V^+ e_s$ is $a = \operatorname{tr}(V^+ V_{\mathrm{drawn}})/\mathrm{ndf}$.
- **Scenario D1 (Global Fluctuation):**
  $\phi \to \sqrt{s}\phi$ with $s = 1.25/a$ at $b = 0$. $\mathbb{E}[M] = s \cdot a = 1.25$. Defined if $a > 0$. Exact.
- **Scenario D2 (Band-Confined Fluctuation):**
  Lines 889–890 specify: *"for each total band R with at least 10 modes, φ scaled only within R's eigenspace, so that R's expected band mean is 1.25. Defined if R's fluctuation share is positive."*
  - **Defect (MAJOR):** Unlike D1 and D3, D2 gives no algebraic formula. It leaves unspecified the total band projector $P_R^{\mathrm{tot}} = \sum_{i \in R} u_i u_i^\top$, the band fluctuation share $a_R = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} u_i^\top V_{\mathrm{drawn}} u_i / \lambda_i$, the scale factor $s_R = 1.25 / a_R$, the transformed vector $\phi \to (I - P_R^{\mathrm{tot}})\phi + \sqrt{s_R} P_R^{\mathrm{tot}} \phi$, and confirmation that $b = 0$.
- **Scenario D3 (Bias-Driven Deficit):**
  For each grid direction $w_j$, $b = \beta w_j$ with $\beta^2 = (1.25 - a)\mathrm{ndf}/(w_j^\top V^+ w_j)$.
  Because $\mathbb{E}[M] = a + b^\top V^+ b/\mathrm{ndf} = a + \beta^2 (w_j^\top V^+ w_j)/\mathrm{ndf} = 1.25$, this is algebraically exact. It is defined if $a < 1.25$ and $w_j^\top V^+ w_j > 0$.
  - **Defect (MINOR):** Does not explicitly specify whether both signs $b = \pm \beta w_j$ or only $b = +\beta w_j$ are evaluated.

<!-- absence-ok: verbatim third-party read report -->
### 2.6 Custody & Blindness Protocol (§3.4 lines 538–560, §4.2 lines 620–648)
- **Hiding Commitment:** Nonce/salt is added to the seed commitment: $\mathrm{sha256}(\mathrm{seed\ base} \parallel \mathrm{salt})$, published before PG and revealed after PV readout.
- **Job Artifacts:** Generator command arguments contain seeds; PG job scripts and logs are captured into the encrypted seal.
- **Writer Manifest & Two-Stage Verification:** Writer generates an authenticated encrypted manifest binding graded ciphertexts, toy IDs, central inputs, and public outputs to the seal digest and freeze digest. Readout verifies the writer manifest and `P2-FREEZE.sha256` before decrypting graded truths.
- **Encryption Tooling:** Interactive `age --passphrase` is completely excised. Batch non-interactive `gpg --batch --passphrase-fd 0 --symmetric --cipher-algo AES256` is bound, stopping if `gpg` is absent.
- **Scope of Cleanup:** Cleanup on failure is strictly confined to campaign-owned temporary paths.
- The custody protocol is **fully sound and robust**.

<!-- absence-ok: verbatim third-party read report -->
### 2.7 ST1 Sequences & Node-Hour Accounting (§3.3 lines 439–458)
- **Sequence Logic:**
  - W1 firing: W2 not submitted; investigation; PX priced (regeneration + acceptance check + first-time W2 work under corrected builder); remaining campaign repriced.
  - W2 firing (`universe`): P2 does not start; PX covers regeneration + redraw of N4/A1p (95.00 node-h) + acceptance check; campaign repriced.
  - Repricing stop: If repriced remainder exceeds ceiling, branch goes to Joseph or terminates.
  - Firing after sole exception: Terminal stop to director.
- **Accounting Derivations:**
  - **420.09 node-h:** P1 through W2 costs $162.07 + 129.77 = 291.84$ node-h. If `universe` fires on W2, rebuilding `universe` is $33.25$ node-h, and redrawing N4 and A1p is $95.00$ node-h.
    $$291.84 + 33.25 + 95.00 = 420.09\ \text{node-h}$$
    This exceeds the pinned cumulative ceiling of $409.22$ node-h before lateral rebuild ($1.90$), diagnostics, PG ($1.33–2.0$), or PV ($115.38$). The text correctly concludes that a W2 firing of `universe` cannot proceed under the current ceiling without an explicit authorization increase from Joseph.
  - **202.35 node-h:** Rebuilding `universe` ($33.25 + 1.90$), `stat` ($57.00$), and `c08` ($15.20$) equals $107.35$ node-h. Adding the $95.00$ redraw equals $202.35$ node-h.
    - **Defect (MINOR):** Line 454 describes $202.35$ node-h as *"the all-block rebuild plus the redraw"*. However, Rev 7 added line 474: `- the N5 replicas: 200 (38.00) if the data-stream method is corrected`. With N5 replicas included, the true all-block rebuild plus redraw is $202.35 + 38.00 = 240.35$ node-h.

<!-- absence-ok: verbatim third-party read report -->
### 2.8 The Three-Part Outcome Table (§7 lines 942–979)
- **Structure:**
  - **Part 1 (Construction Finding):** Reports ST1 outcome independently (did not fire, unexplained, defect corrected & passed acceptance + whether $K_A$ eligible at P2, defect found but unresolved).
  - **Part 2 (Baseline Challenge):** Evaluates $K_0$'s PV verdict (challenge if $K_0$ FAILS at $\ge 1$ truth; no deficit shown if $K_0$ VALIDATED at both; unchallenged if $K_0$ is INFLATED, UNRESOLVED, or NOT TESTABLE).
  - **Part 3 (Selected Candidate):** First VALIDATED in order $K_A, K_B, K_C$ among eligible candidates, licensed **only with a challenge** (Outcomes A, B, C, or none).
- **Completeness:** Covers all edge combinations, eliminates the ambiguous "A, partial" row by decoupling Part 1 from Part 3, and explicitly documents coexistence (e.g. corrected defect with $K_A$ ineligible at P2, and B selected).

<!-- absence-ok: verbatim third-party read report -->
### 2.9 Contradictions with Changed Text Elsewhere in Rev 7
- **Defect (MAJOR — Numerical Gate Conflict in §9):**
  Line 1029 (§9 Open items, item 4) reads:
  ```markdown
  - testability at 0.20 false-FAIL and 0.10 deficit pass;
  ```
  This is a direct leftover from Rev 6! In Rev 7:
  - §6.2 line 882 gates per-truth not-PASS at **0.10** (at most 29/400), yielding a candidate union bound of **0.20**;
  - §6.2 line 895 and §6.5 line 933 gate deficit whole-rule pass at **0.05** (at most 12 of 400), yielding a candidate union bound of **0.15**;
  - Rev 7 header line 160 explicitly declares: *"per-truth gates of 0.10 (not-PASS) and 0.05 (deficit pass)"*.
  Leaving "0.10 deficit pass" in §9 item 4 creates a glaring internal numerical conflict in the document's summary of binding bars.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Binding Readiness & Actionable Findings

<!-- absence-ok: verbatim third-party read report -->
Rev 7 cannot be bound until the following findings are resolved:

<!-- absence-ok: verbatim third-party read report -->
### 3.1 Itemized Findings by Severity

<!-- absence-ok: verbatim third-party read report -->
#### Finding 1: Contradiction in §9 Policy Bar Summary (MAJOR)
- **Location:** Line 1029 ([COVFIX-DECLARATION.md line 1029](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L1029)).
- **Issue:** Lists *"testability at 0.20 false-FAIL and 0.10 deficit pass"*, directly conflicting with §6.2 line 895, §6.5 line 933, and Rev 7 summary line 160, which set the deficit pass gate to 0.05 per truth ($\le 12/400$).
- **Fix:** Update line 1029 to read:
  `- testability at 0.10 per-truth false-FAIL (0.20 candidate union bound) and 0.05 per-truth deficit pass;`

<!-- absence-ok: verbatim third-party read report -->
#### Finding 2: Dimensionally Broken Variance Addition for ST1 N5 Guard (MAJOR)
- **Location:** Lines 426–427 ([COVFIX-DECLARATION.md lines 426–427](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L426-L427)).
- **Issue:** States that the sampling variance of $S1_B$ is added as $2(u_i^\top S1_B u_i)^2 / (R - 1)$ to the variance of the ratio $\hat{s}_i / (u_i^\top S1_B u_i)$. This adds a quantity with dimensions of covariance-squared to a dimensionless ratio variance.
- **Fix:** Update lines 426–427 to state:
  `- For N5, S1_B is itself estimated from the 200 replicas. Under the delta method for the ratio ŝ_i / u_iᵀ S1_B u_i, the denominator's relative variance 2/(R − 1) (with R = 200) is added to ŝ_i's relative sampling variance, scaled by the squared ratio (or 2/(R − 1) under the null).`

<!-- absence-ok: verbatim third-party read report -->
#### Finding 3: Incomplete Formula Specification for Scenario D2 (MAJOR)
- **Location:** Lines 889–890 ([COVFIX-DECLARATION.md lines 889–890](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L889-L890)).
- **Issue:** D2 specifies scaling only in words, leaving the projector, fluctuation share, and scale factor unwritten.
- **Fix:** Update lines 889–890 to provide the exact algebraic formulas:
  `- **D2, band-confined:** for each total band R with at least 10 modes, with P_R = Σ_{i∈R} u_i u_iᵀ the projector onto total band R's eigenspace, φ → (I − P_R)φ + √s_R P_R φ at b = 0, with s_R = 1.25/a_R, where a_R = (1/ndf_R) Σ_{i∈R} u_iᵀ V_drawn u_i / λ_i. Defined if a_R > 0.`

<!-- absence-ok: verbatim third-party read report -->
#### Finding 4: Omission of Band Spread $\tilde{F}_R$ in Influence Function Specification (MINOR)
- **Location:** Line 282 ([COVFIX-DECLARATION.md line 282](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L282)).
- **Issue:** States `- for F̃, SE(F^F)/F_exp`, omitting the band spread $\tilde{F}_R$ guarded in P-1.
- **Fix:** Update line 282 to read:
  `- for F̃, SE(F^F)/F_exp, and for a band F̃_R, SE(F_R^F)/F_exp,R.`

<!-- absence-ok: verbatim third-party read report -->
#### Finding 5: Stale All-Block Rebuild Node-Hour Figure in ST1 Scale Note (MINOR)
- **Location:** Line 454 ([COVFIX-DECLARATION.md line 454](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L454)).
- **Issue:** Quotes 202.35 node-h as the all-block rebuild plus redraw. This excludes N5 replicas (38.00 node-h) added in Rev 7 line 474.
- **Fix:** Update line 454 to clarify:
  `- For scale: the rebuild of universe, stat and c08 plus the redraw is 202.35 node-h before diagnostics (240.35 node-h if N5 replicas are also rebuilt).`

<!-- absence-ok: verbatim third-party read report -->
#### Finding 6: Omission of Explicit Sign Convention for D3 (MINOR)
- **Location:** Line 891 ([COVFIX-DECLARATION.md line 891](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix7/inputs/COVFIX-DECLARATION.md#L891)).
- **Issue:** Specifies $\beta^2$ but does not state whether both signs $\pm \beta w_j$ or only $+\beta w_j$ are evaluated.
- **Fix:** Clarify line 891 to state: `b = ±β w_j` (or `b = +β w_j`).

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Conclusion & Verdict

<!-- absence-ok: verbatim third-party read report -->
Rev 7 successfully resolves all 12 prior findings from codex-school2's Rev 6 review, establishing a coherent and scalable framework for the 2D covariance fix. However, because a formal pre-registration cannot be bound with internal numerical contradictions in its stated bars (§9 vs §6.2/§6.5) or dimensionally flawed statistical guard formulas (ST1 N5), the confirmation verdict is **NO-GO**. 

<!-- absence-ok: verbatim third-party read report -->
Applying the six concise, surgical edits listed above in a **Draft Rev 7.1** will immediately render the pre-registration text fully ready to bind.
