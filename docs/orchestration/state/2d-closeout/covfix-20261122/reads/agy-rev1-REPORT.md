<!-- absence-ok: verbatim third-party read report -->
# NO-GO

**Document Reviewed:** `inputs/COVFIX-DECLARATION.md` (DRAFT rev 1, 2026-11-22)  
**Inventory Baseline:** `inputs/INVENTORY.md` (read at `7d5a98361`)  
**Review Type:** Read-only Pre-Registration Technical Review for Fix 1 (2D Cross-Section Covariance)  
**Verdict:** **NO-GO (BLOCKING deficiencies identified; binding must not proceed until remediated)**

---

## Executive Summary

The draft pre-registration `COVFIX-DECLARATION.md` (rev 1) proposes a systematic plan to address the 2D cross-section covariance under-coverage at held-out generator tunes (G18 and AR23), aiming to satisfy an external review's requirement for "Fix 1" (separating fluctuation $C_{\text{fluct}}$ from truth-model bias $b b^T$). While the multi-phase framework (P0 through PV) and the design of the measurement matrix (N1–N5, A1) are conceptually ambitious, this audit identifies **six BLOCKING technical, mathematical, and procedural defects**, along with several **MAJOR** and **MINOR** vulnerabilities.

Most critically:
1. Candidate **B3** is a disguised eigenvalue tail scaling ($\phi$ up to 100 on modes above rank 73) without any measured bias vector, violating the review's explicit rejection of covariance scaling.
2. The fluctuation construction for candidate $K_B$ ($\max(\lambda_i, \hat{s}_i)$ with Ledoit–Wolf shrinkage toward $\text{diag}(\hat{S})$ in cell space) is mathematically defective for $p=205$ cells with $N=200$ toys, causing spurious variance inflation via finite-sample noise floors and Jensen bias, while destroying the physical correlation structure.
3. Candidate **B1** computes an unregularized debiased outer product $(\hat{b} \hat{b}^T - S_t/N_t)$ that is strictly negative definite along at least 199 dimensions, violating positive semi-definiteness and guaranteeing a fatal runtime failure under control C-PSD.
4. Stop rule **ST1** and its condition to skip **N5** ("over needs N5, under stands without it") contain a severe logical inversion given Known Issue 85: same-event pseudo-data under-scatter by a factor of $\sim 0.44$, which depresses $M$ and masks under-coverage. Skipping N5 when N1/N2 read "covers" skips the held-out simulation test precisely when severe under-coverage on independent data is hidden.
5. The custody and blindness protocols in §4.2 rely on Lustre/pscratch filesystem `atime`, which is completely bypassed by the standard `O_NOATIME` reads used across the repository. Furthermore, validation tune #2 (`G18_10b_02_11b`) shares its primary CCQE and 2p2h physics models with the spent build tune `G18_10a_02_11b`.
6. The claimed allocation balance of 725.6 node-h is unsupported by any committed record, the cumulative caps (523.0 node-h) represent 72% of that unverified balance, and P1 contains no intra-phase accounting waves to prevent silent overruns during concurrent execution.

Binding must be refused until these issues are resolved. Concrete remediations are detailed below for each finding.

---

## 1. Fidelity: Verification of Numbers and Claims Against Records

Every claim and figure in `inputs/COVFIX-DECLARATION.md` and `inputs/INVENTORY.md` was cross-checked against the underlying records (`OUTCOME-20261108-cov2d.md`, `READING-T2-20261110.md`, `regrade_2d_AR23.json`, `regrade_2d_G18.json`, `OUTCOME-20261005.md`, `KNOWN_ISSUES-rows-84-85.md`, `OUTCOME-20261119-ibukt-a2.md`, `FD-F1-REPORT.md`, `FD-F1-DECLARATION.md`, `G2R-readout-README.md`, and `methods-SCOPING.md`).

### Verified Numbers and Claims
- **T2A Component Spread:** Lines 45–47 cite component spread in $C_T$'s eigenbasis as 1.6 / 3.0 / 4.4 (AR23) and 1.5 / 3.6 / 4.7 (G18) for ranks 1–73 / 74–139 / $\ge 140$. This matches `READING-T2-20261110.md:35` exactly.
- **Negligibility of $C_{\text{run}}$ in 2D:** Line 48 cites $\tau = 0.0098$ per ndf at both tunes. In `regrade_2d_AR23.json:25` $\tau = 0.0097667$ and in `regrade_2d_G18.json:44` $\tau = 0.0097675$. Both round to 0.0098.
- **F1 Spend for GENIE v3 Generation:** Line 51 and `INVENTORY.md:93` cite 1.3275 node-h for generating both GENIE v3 tunes. This matches `FD-F1-REPORT.md:143` exactly ("total charge is 1.327500 node-h").
- **KI 85 Same-Event Under-Scatter:** Lines 85–86 cite same-event toys scattering at a corrected median $\sigma_T / \sigma_{\text{realboot}} = 0.661$ (variance ratio near 0.44). This matches `KNOWN_ISSUES-rows-84-85.md:2` ("median 0.661", $0.661^2 = 0.4369 \approx 0.44$).
- **COV2D Spend and Per-Toy Cost:** Line 92 and `INVENTORY.md:98` cite 112.74 node-h over 27 attempts (600 toys plus pilots), giving $112.74 / 600 = 0.1879 \approx 0.19$ node-h per toy. This matches `methods-SCOPING.md:117` and `INVENTORY.md:98`.
- **IBUKT A2 Nominal Residual:** Line 103 and `INVENTORY.md:76` cite nominal max residual of 1.708%. This matches `OUTCOME-20261119-ibukt-a2.md:23` (1.708252%).
- **G2R Coverage and Metrics:** `INVENTORY.md:23–26` cites G18 0/300 (cell 29), AR23 0/300 (cells 29, 56), and $\varepsilon = 25.833$ (5.999 on top 73). This matches `G2R-readout-README.md:36–51` exactly.
- **10-05 Closure Test Metrics:** `INVENTORY.md:28–35` cites C1 = 0.679, C2 = 0.912 [0.928, 0.972] (FAIL), pull RMS = 1.6, pull mean consistent with 0, and post-hoc rescoring C1 = 0.781, C2 = 0.977. This matches `OUTCOME-20261005.md:37–40` and `KNOWN_ISSUES-rows-84-85.md:1`.

### Erroneous, Unsupported, or Misquoted Claims
1. **Unsupported Allocation Balance and Half-Balance [Lines 83, 88]:**
   - *Claim:* "against the balance of 725.6 node-h" (line 83) and "half the balance (362.8)" (line 88).
   - *Factual Defect:* **Unsupported.** Neither `INVENTORY.md` nor any cited record contains 725.6 node-h. In `methods-SCOPING.md:20–24`, the authors explicitly documented: *"The allocation balance cannot be read without a connect. The last committed reading is the iris row `m3246 2531.9 10000.0 18671.2 20000.0`... gate computed `balance_node_h=1328.8`... Since then, the rest of G2R, the LL5D bulk end and readout, IBUKT (3.345), RDX and others have run. The current balance is lower, and a figure needs an iris read on a connect."* Because COVFIX line 5 states that no cluster connect has been made under it, the 725.6 figure is an unverified, uncommitted number. *(Severity: BLOCKING)*
2. **Misattribution of Available Tune Qualifiers to F1 Declaration [Lines 187–188]:**
   - *Claim:* "from the tune qualifiers the genie_xsec v3_04_00 product on Perlmutter actually provides, which F1's source is (FD-F1-DECLARATION.md:76)."
   - *Factual Defect:* **Misquoted / Unsupported.** `FD-F1-DECLARATION.md:76` only lists two specific tune qualifiers: `G1810a0211b-k250-e1000` and `AR2320i00000-k250-e1000`. It does *not* document the existence or qualifiers for `G21_11b_00_000`, `G18_10b_02_11b`, `G18_02b_02_11b`, or `G18_02a_02_11b`. While lines 195 and 209 acknowledge that PG must confirm them with a probe, citing line 76 of F1 as the source for these specific qualifiers is factually inaccurate. *(Severity: MINOR)*
3. **Internal Inconsistency in Lean Option Pricing [Line 90]:**
   - *Claim:* Lean option total is "about 393, or 316 if N5 is skipped" with PV = 114.
   - *Factual Defect:* **Arithmetic Inconsistency.** If P1 = 276 and PV = 114, then $276 + 114 = 390$. For the total to be 393, PG is priced at 3.0 node-h. But if N5 is skipped, P1 = 200 and PV = 114 ($200 + 114 = 314$); for the total to be 316, PG is priced at 2.0 node-h. Furthermore, for two validation truths, PG generating 2 tunes at 0.66 node-h each should cost $\approx 1.33$ node-h (Table 3 lists PG as 2.0–2.5). The lean numbers 393 and 316 are internally inconsistent by 1–2 node-h. *(Severity: MINOR)*

---

## 2. Blindness and Custody

### Can Candidate Constructions be Tuned on Validation Truths?
**Yes, indirect tuning and physics leakage are present in rev 1.**
- In §4.1 (lines 191, 202–203), preference #2 for validation is `G18_10b_02_11b`. The declaration notes: *"G18_10b differs from the spent G18_10a_02_11b in its intranuclear model only. It tests sensitivity to FSI at a seen quasielastic model and is disclosed as close to G18."*
- In §5.2 (lines 263–264), candidate $K_B$ constructs its truth-model bias term from the family $F = \{\text{genie\_mec}, \text{nuwro}, \text{gibuu}, \text{tune\_v1}, \mathbf{G18}, \mathbf{AR23}\}$.
- Because $F$ explicitly includes the spent tune `G18_10a_02_11b`, the bias vector $\hat{b}_{\text{G18}}$ already encodes the interaction physics (NAV CCQE and Nieves 2p2h) that `G18_10b_02_11b` shares. Testing $K_B$ on `G18_10b` does not test generalization to an unseen interaction model; it tests only intranuclear cascade variation (hN vs hA) around an interaction model upon which the covariance was explicitly constructed.
- Furthermore, under candidate **B3** (line 267), the parameter $\phi$ is tuned on the build set (which includes G18 and AR23) until the build set passes §5.4. Tuning $\phi$ on G18 directly tunes the tail eigenvalues to absorb the G18 bias, ensuring `G18_10b` will pass.

### Is Custody in Section 4.2 Sufficient?
**No. The custody mechanism is technically ineffective as specified.**
- **Bypass of `atime` via `O_NOATIME`:** Section 4.2 (lines 229–231) specifies: *"Atime on the sealed set's pscratch copies is recorded at seal time and checked unmoved at PV, with O_NOATIME reads, as the COV2D connects did. A moved atime is a guard refusal."* However, all production and inspection tools across this workflow open files with `O_NOATIME`. An `O_NOATIME` read operation **does not update file access times**. Consequently, any process, subagent, or developer running on Perlmutter under the same user account can read, inspect, or extract the plaintext 5D ratio files on `/pscratch/sd/j/josephrb/...` using `O_NOATIME` without triggering an `atime` modification.
- **Shared POSIX Environment:** The session executing PG (whether tier3-design, limitation-resolver, or a fresh session) operates under the exact same UNIX UID/GID (`josephrb:wheel`) as the cov2d session on Perlmutter. Files placed on pscratch without cryptographic protection have no operating system access barrier separating the sessions.
- **Pscratch Purge Vulnerability:** Section 4.2 (line 225) notes: *"An HPSS copy at seal time is proposed... It is not yet required."* NERSC pscratch directories are subject to automated purging. If files are purged or corrupted prior to PV, the uncommitted validation truths would have to be regenerated, breaking the seal timestamp and provenance chain.

### Is "Validation is Spent Once" Enforceable as Written?
**No. It is an administrative policy assertion, not a technically enforceable control.**
- Section 3.3 (lines 151–154) defines ST4: *"PV's toys are read once, at the frozen candidates' shas. After the read, no candidate may be changed and re-read against the same truths. Any later construction needs new sealed truths."*
- This rule is unenforceable against unrecorded looks: because the toys are unfolded and written to pscratch during PV, intermediate toy outputs or residual distributions could be evaluated prior to triggering the formal readout script.
- **Model Exhaustion Problem:** More fundamentally, ST4's mitigation—*"Any later construction needs new sealed truths"*—is **physically impossible within the declared family**. Section 4.1 lists only four GENIE v3 tune qualifiers in the `genie_xsec v3_04_00` product on Perlmutter. If three are generated in PG and spent in PV, exactly one qualifier remains in the product catalog. The validation resource is completely exhausted in a single evaluation.

---

## 3. Design Soundness

### Separation of Bias from Fluctuation
- The prompt asks whether the plan separates $E[(\hat{\sigma} - \sigma)(\hat{\sigma} - \sigma)^T] = C_{\text{fluct}} + b b^T$.
- In §5.2, candidate $K_B$ attempts this by constructing $V_F$ (fluctuation) from nominal toys (N4) and $C_b$ (bias) from the alternative truth family $F$.
- However, for candidate **B3** (lines 267–268), no separation exists. B3 sets an eigenvalue floor $\lambda_i' = \max(\lambda_i^F, \phi \cdot \lambda_{73}^F)$ for ranks $> 73$, where $\phi \in \{1, 2, 5, 10, 20, 50, 100\}$. B3 contains **no explicit bias vector $b$ and no outer product $b b^T$**. It treats the structural failure of the covariance as an eigenvalue deficit, inflating the tail variance to cover the mean shift.

### Is B3 a Disguised Scaling that the Review Rejects?
**Yes. B3 is unambiguously a disguised scaling.**
- The outside review explicitly *"rejects scaling the covariance until the two tunes pass."*
- B3 takes the eigenvalue at rank 73 and scales it by an arbitrary factor $\phi$ (up to a factor of 100) across all 132 tail modes, selecting the smallest $\phi$ on a discrete grid that forces the build set to pass §5.4.
- While line 258 asserts *"It is per-mode, not a uniform scale; the review rejects a uniform scale"*, applying a uniform scalar multiplier $\phi$ to the tail modes is functionally identical to tail scaling. It is an ad-hoc inflation parameter tuned directly to overcome the under-coverage. *(Severity: BLOCKING)*

### Soundness of the $K_B$ Fluctuation Rule: $\max(\lambda_i, \hat{s}_i)$ and Ledoit–Wolf
**The $K_B$ fluctuation rule in §5.2 (lines 255–262) is mathematically and statistically invalid for $p=205$ cells with $N=200$ toys.**
1. **Jensen's Inequality Bias:**
   In any finite sample, the sample eigenvalue projection $\hat{s}_i = u_i^T \hat{S} u_i$ is a random variable with standard error $\approx \lambda_i \sqrt{2/N} \approx 0.10 \lambda_i$ under Gaussian assumptions. Even if the true fluctuation is perfectly modeled by $\lambda_i$, setting each mode to $\max(\lambda_i, \hat{s}_i)$ introduces a strictly positive Jensen bias:
   $$E[\max(\lambda_i, \hat{s}_i)] > \lambda_i$$
   Applying this per-mode maximum across 205 modes guarantees systematic over-estimation of the fluctuation variance.
2. **Singularity and Noise Floor in Tail Modes ($p > N$):**
   The sample covariance $\hat{S}$ is formed from $N=200$ toys on $p=205$ dimensions; it is rank-deficient ($\text{rank} \le 199$). In the tail modes ($i \ge 74$), the nominal eigenvalues $\lambda_i$ drop steeply (reaching $10^{-4}$ to $10^{-12}$ of $\lambda_1$).
   Projecting $\hat{S}$ onto $u_i$ in finite samples will pick up a finite-sample noise floor from dominant mode fluctuations leaking into empirical sample vectors. Consequently, for small modes, $\hat{s}_i$ will almost always exceed $\lambda_i$ purely due to sample noise, replacing physical eigenvalues with the statistical noise floor of 200 toys.
3. **Distortion from Ledoit–Wolf Shrinkage in Cell Space:**
   Line 261 states: *"$\hat{S}$ is shrunk toward $\text{diag}(\hat{S})$ by the Ledoit–Wolf estimator."*
   The standard Ledoit–Wolf target $\text{diag}(\hat{S})$ shrinks off-diagonal covariances toward zero **in the cell basis**. Unfolding introduces severe anti-correlations between adjacent bins and complex kinematic correlations. Shrinking off-diagonal elements in cell space drastically distorts the eigenvector structure $u_i$ and artificially spreads the eigenvalue spectrum. Projecting this distorted matrix back onto $V$'s eigenbasis via $u_i^T \hat{S} u_i$ produces an unphysical hybrid variance estimate. *(Severity: BLOCKING)*

### Positive Semi-Definiteness Failure in B1 Debiasing
- In §5.2 (line 265), variant B1 defines $C_b = \frac{1}{|F|} \sum_{t} (\hat{b}_t \hat{b}_t^T - S_t / N_t)$.
- The outer product $\hat{b}_t \hat{b}_t^T$ has rank 1. The sampling covariance $S_t / N_t$ has full rank (or rank $N_t - 1 \gg 1$).
- Therefore, for any truth $t$, the debiased matrix $(\hat{b}_t \hat{b}_t^T - S_t / N_t)$ has at most one positive eigenvalue and up to 204 strictly negative eigenvalues.
- Summing over $|F| = 6$ truths leaves $C_b$ strictly negative-definite on at least $205 - 6 = 199$ dimensions orthogonal to the subspace spanned by $\{\hat{b}_t\}$.
- Adding $C_b$ to $V_F$ risks producing negative eigenvalues in $V$, and will trigger an immediate STOP under control C-PSD (REGRADE-DECLARATION §6: *"min eigenvalue $\ge -10^{-12} \lambda_{\max}$"*). The declaration specifies no spectral truncation or positive-part projection $[C_b]_+$. *(Severity: BLOCKING)*

### Do Candidates Risk Passing by Inflation, and Do the Bars Catch It?
- **Risk of Inflation:** Yes. Inflating the tail eigenvalues (as in B3 or via the noise floor of $K_B$) suppresses the large $\chi^2$ contributions from ranks $> 73$, lowering $M$ from $\sim 20$ into the nominal range $[0.8, 1.25]$.
- **Do the Bars Catch It?** **Only partially, and with major blind spots.**
  - **P-1 ($M \in [0.8, 1.25]$):** Allows up to a 20% deficit in mean $\chi^2$ ($M=0.80$) without flagging "over".
  - **P-2 (Band Means):** Line 313 defines band over-coverage as $Q_R + h < 0.67$. However, P-2 in line 332 states: *"P-2: no band reads 'under'"*. **P-2 checks only for under-coverage, never for over-coverage.** A band can have $Q_R = 0.10$ (extreme inflation) and pass P-2 without restriction.
  - **P-3 (Joint Coverage):** Flags "over" if joint count in the 68.27% contour $\ge k_J^+ = 221$ (for $N=300$). If inflation is uniform, P-3 has high power to catch it. However, if inflation is concentrated in the tail modes while R1 remains slightly over-spread (as observed in T2A where ranks 1–73 have spread 1.6), the two effects cancel in the scalar $\chi^2$ sum:
    $$\sum_{i=1}^{73} z_i^2 \approx 73 \times 1.4 \approx 102, \quad \sum_{i=74}^{204} z_i^2 \approx 131 \times 0.7 \approx 92 \implies \chi^2 \approx 194 \approx \text{ndf}$$
    The total $\chi^2$ falls into the center of the distribution, joint coverage lands near $68\%$, and P-3 fails to flag over-coverage despite severe tail inflation.
  - **P-4 (Per-mode):** Line 334 checks only that *"at most 2 modes are flagged 'under'"*. **P-4 never checks for modes flagged "over".**
  - **Build-Set Admission (§5.4):** Line 288 requires only that *"under the joint rule of §6.1, the reading is not 'under'"*. It does not require that candidates avoid being flagged "over" on the build set. *(Severity: MAJOR)*

---

## 4. Stop Rule ST1 and Known Issue 85

### The Asymmetric Rule: "Over Needs N5, Under Stands Without It"
Section 3.3 (lines 135–139) establishes the stop rule for construction error:
- *"Under stands without N5. Same-event pseudo-data can only under-scatter (KI 85 (b)), so they can hide under-coverage but not create it."*
- *"Over needs N5. An 'over' at N1 or N2 is a construction error only if N5... also reads 'over' in R1... If N5 reads 'covers', the 'over' is recorded as KI 85's same-event effect. ST1 does not fire..."*
- Lines 87 and 121 establish the execution condition: *"N5 is skipped only if N1 and N2 both read 'covers' or 'under' in R1."*

### Is This Rule Correct Given KI 85's Finding?
**No. The rule contains a fatal logical contradiction that defeats the purpose of N5.**

1. **The "Covers" Trap (Skipping N5 Masks Under-Coverage):**
   - Known Issue 85 found that same-event pseudo-data under-scatter with a data-variance ratio of $g \approx 0.40$ (median $\sigma_T / \sigma_{\text{realboot}} = 0.661$, variance ratio $\approx 0.44$).
   - This means same-event toys produce an empirical variance that is **suppressed by a factor of $\approx 2.3$** relative to genuine independent data.
   - Now consider an estimator whose true covariance under-covers on independent data by a factor of 2.0 ($M_{\text{true}} \approx 2.0$).
   - When evaluated with same-event pseudo-data in N1, the empirical scatter is suppressed by $0.44$, yielding:
     $$M_{\text{obs}} \approx 0.44 \times 2.0 = 0.88$$
   - Since $0.88 \in [0.8, 1.25]$, cell N1 reads **"covers"**!
   - Under lines 87 and 121, because N1 reads "covers", **N5 is skipped!**
   - The workflow proceeds to P2 and PV under the false conclusion that the statistical block $S1$ is calibrated, when in reality $S1$ under-covers by 100% on independent data.
   - **Conclusion:** Skipping N5 when N1/N2 read "covers" skips the validation precisely when same-event under-scattering is masking true under-coverage.

2. **Can Same-Event Toys Never Create Apparent Under-Coverage?**
   - Line 135 asserts: *"Same-event pseudo-data can only under-scatter... so they can hide under-coverage but not create it."*
   - This assumption is demonstrably false when the unfolding estimator possesses nominal closure bias.
   - In `OUTCOME-20261119-ibukt-a2.md:23`, refined OmniFold exhibits a noise-free nominal residual of up to 1.708%.
   - In N1, the error is $e_s = \hat{\sigma}_s - \sigma_{\text{MC}}$. The expectation of $z_{s,i}^2$ is $v_i + m_i^2$, where $m_i$ is the projection of the estimator's nominal closure bias onto $u_i$.
   - Because $S1$ is a pure fluctuation covariance (Poisson data bootstrap) that contains **no bias term**, any non-zero closure bias $m_i^2$ adds directly to $M$. In small eigenvalue modes, $m_i^2 / \lambda_i$ can easily push $M > 1.25$, causing N1 to read "under".
   - If N1 reads "under", ST1 immediately fires, halting the pipeline to report a "construction error" in $S1$, even though $S1$'s fluctuation scale may be perfectly accurate and the excess was driven by nominal estimator bias.
   - Calling an "under" reading an automatic construction error without confirming it on N5 is unsound. *(Severity: BLOCKING)*

3. **Incomplete Specification of N5 Outcomes:**
   - Line 137 defines what happens if N5 reads "over" (construction error) or "covers" (KI 85 same-event effect, ST1 does not fire).
   - The declaration **completely fails to specify what happens if N5 reads "under"**. If N1 reads "over" (due to same-event suppression) but N5 reads "under" (revealing that on independent data the covariance is severely under-covering), the stop rule provides no decision path. *(Severity: MAJOR)*

---

## 5. Statistical Checks: Multiplicity, Arithmetic, and Approximations

### Verification of Formulas and Arithmetic in Section 6.4
- **Formula for $\text{SE}(M)$:**
  For $N$ toys on $\text{ndf}$ modes with $\chi_s^2 \sim \chi^2(\text{ndf})$, $\text{Var}(\chi_s^2) = 2 \cdot \text{ndf}$. Since $M = \frac{1}{N \cdot \text{ndf}} \sum_{s=1}^N \chi_s^2$:
  $$\text{Var}(M) = \frac{1}{N^2 \cdot \text{ndf}^2} (N \cdot 2 \cdot \text{ndf}) = \frac{2}{N \cdot \text{ndf}} \implies \text{SE}(M) = \sqrt{\frac{2}{N \cdot \text{ndf}}}$$
  For $N=300$ and $\text{ndf}=204$, $\text{SE}(M) = \sqrt{2 / (300 \times 204)} = \sqrt{2 / 61200} = 0.005717 \approx 0.006$. This matches line 353.
- **Guard $h(M)$ for $\text{ndf}=204$:**
  $t_{0.975, 299} = 1.9679$. $h(M) = 1.9679 \times 0.005717 = 0.01125 \approx 0.011$. Matches line 357.
- **$\text{SE}(M)$ for $K_C$ at $k=5$:**
  $\text{SE}(M) = \sqrt{2 / (300 \times 5)} = \sqrt{2/1500} = 0.03651 \approx 0.037$. $h(M) = 1.9679 \times 0.03651 = 0.07186 \approx 0.072$. Matches line 357.
- **Band Mean $\text{SE}(Q_R)$ for 66 Modes:**
  $\text{SE}(Q_R) = \sqrt{2 / (300 \times 66)} = \sqrt{2/19800} = 0.01005 \approx 0.01$. Matches line 359.
- **Familywise Probability Bounds:**
  - $1 - 0.95^3 = 0.1426 \approx 0.14$ (three truths, not VALIDATED). Matches line 364.
  - $1 - 0.975^3 = 0.0731 \approx 0.07$ (three truths, FAILS). Matches line 364.
  - $1 - 0.95^2 = 0.0975 \approx 0.10$ (lean option, not VALIDATED). Matches line 364.
  - $1 - 0.975^2 = 0.0494 \approx 0.05$ (lean option, FAILS). Matches line 364.

### Statistical Errors, Omissions, and Breakdown Points

1. **Severe Mathematical Error in the Excursion Calculation for $K_C$ [Line 358]:**
   - *Claim:* *"for $K_C$ at $k = 5$, $\text{SE} \approx 0.037$ and $h \approx 0.072$, so leaving $[0.8, 1.25]$ needs about a $5\sigma$ excursion."*
   - *Error:* **Mathematically False.** To avoid reading "unresolved across covers and under", the interval $[M - h, M + h]$ must lie **entirely inside** $[0.8, 1.25]$. Therefore, the upper boundary for $M$ is not $1.25$, but $1.25 - h = 1.25 - 0.0719 = 1.1781$.
   - The distance from the nominal value $M=1.0$ to the unresolved boundary is:
     $$\Delta = 1.1781 - 1.0 = 0.1781$$
     $$\text{Excursion in SE} = \frac{0.1781}{0.03651} = \mathbf{4.88\sigma}$$
   - While $4.88\sigma \approx 5\sigma$ for $k=5$, consider smaller $k$ values permitted by §5.3:
     - For $k=2$: $\text{SE} = 0.0577$, $h = 0.1136$. Upper bound for $M$ is $1.25 - 0.1136 = 1.1364$. Distance from 1.0 is $0.0864$, which is **only $1.50\sigma$**! The probability that a perfectly calibrated candidate reads "unresolved" is **13.5% per truth**, leading to a **35% false-failure rate** across three truths!
     - For $k=1$: $\text{SE} = 0.0816$, $h = 0.1607$. Upper bound is $1.25 - 0.1607 = 1.0893$. Distance is $0.0393$, which is **only $0.48\sigma$**! The probability of reading "unresolved" is **63% per truth** ($95\%$ failure rate across three truths!).
   - The author forgot that the guard $h$ subtracts from the acceptance window, which collapses catastrophic for small $k$. *(Severity: MAJOR)*

2. **Degeneracy of Bands for $K_C$ ($k \le 73$):**
   - Section 2 (line 66) defines bands R1 (1–73), R2 (74–139), and R3 ($\ge 140$).
   - For candidate $K_C$, if $k \le 73$, bands R2 and R3 **contain zero modes**.
   - The declaration does not define $Q_R$ for an empty band. In standard implementations, computing the mean of an empty slice yields `NaN` or raises an exception.
   - In Python, `NaN - h > 1.5` evaluates to `False`. Consequently, bands R2 and R3 would vacuously pass P-2 without any check. *(Severity: MAJOR)*

3. **Breakdown of P-4 (Per-mode Coverage) for Small $k$:**
   - Section 6.2 (line 334) specifies: *"P-4: at most 2 modes are flagged 'under'."*
   - For $K_C$ with $k=5$, allowing 2 modes to fail under-coverage allows **40% of the reported subspace to fail**.
   - For $k \le 2$, allowing 2 modes to fail allows **100% of the reported modes to fail**, and the candidate still passes P-4!
   - Furthermore, for $k=1$, the per-mode test $|z_1| \le 1$ and the joint test $\chi^2(1) \le 1.000$ test the **exact same statistical event**, yet P-3 applies a two-sided $\alpha=0.05$ threshold ($k_J=188, k_J^+=221$) while P-4 applies a Bonferroni-adjusted one-sided threshold $\alpha=0.025/1$ ($k_c=186$). Having different acceptance bars for the identical observable is statistically incoherent. *(Severity: MAJOR)*

4. **Assumption of Independence Between Modes Under Non-Gaussianity:**
   - Section 6.4 (line 360) states that P-4's expected false flags are at most 0.025 per truth, relying on Bonferroni's inequality: $\sum_{i=1}^{\text{ndf}} P(\text{flag}_i) \le \text{ndf} \times (0.025/\text{ndf}) = 0.025$.
   - While Markov's inequality ensures $P(\ge 3 \text{ flags}) \le 0.025 / 3 = 0.0083$ regardless of correlation, the joint distribution of mode failures in real neural network unfolding is highly clustered: non-linear threshold effects, training instabilities, and clipping induce correlated tail excursions across multiple modes simultaneously.
   - P-2 (band means) is similarly vulnerable: if modes within a band share common normalization fluctuations, the effective degrees of freedom in R1 is far less than 73, and $\text{SE}(Q_R)$ will be substantially larger than 0.01. *(Severity: MINOR)*

---

## 6. Prices, Accounting, and Stop Rules

### Consistency of Node-Hour Pricing
| Component | Expression | Stated (node-h) | Exact Arithmetic | Status |
|---|---|---|---|---|
| Toy Unit Price | COV2D receipts ($112.74 / 600$) | 0.19 | 0.1879 | Consistent (conservative rounding) |
| N1 | $200 \times 0.19$ | 38 | 38.0 | Consistent |
| N2 | $200 \times 0.19$ | 38 | 38.0 | Consistent |
| N3 | $50 \times 0.19$ | 10 | 9.5 | Consistent (rounded up) |
| N4 | $200 \times 0.19$ | 38 | 38.0 | Consistent |
| A1 | $4 \times 100 \times 0.19$ | 76 | 76.0 | Consistent |
| N5 | $(200 + 200) \times 0.19$ | 76 | 76.0 | Consistent |
| **P1 Total** | $38+38+10+38+76+76$ | **276** | **276.0** | **Consistent** |
| P1 (no N5) | $276 - 76$ | **200** | **200.0** | **Consistent** |
| PV Total | $3 \times 300 \times 0.19$ | **171** | **171.0** | **Consistent** |
| PV (lean) | $2 \times 300 \times 0.19$ | **114** | **114.0** | **Consistent** |
| PG | Generation of 3 tunes | **2.0–2.5** | $3 \times 0.6638 = 1.99$ | Consistent |
| **Grand Total** | $\text{PG}(2.0) + \text{P1}(276) + \text{PV}(171)$ | **449** | **449.0** | **Consistent** |
| Grand Total (no N5) | $\text{PG}(2.0) + \text{P1}(200) + \text{PV}(171)$ | **373** | **373.0** | **Consistent** |
| Lean Total | $\text{PG}(3.0) + \text{P1}(276) + \text{PV}(114)$ | **393** | **393.0** | Inconsistent PG baseline (uses 3.0) |
| Lean (no N5) | $\text{PG}(2.0) + \text{P1}(200) + \text{PV}(114)$ | **316** | **316.0** | Inconsistent PG baseline (uses 2.0) |

### Phase Caps and the Half-Balance Rule
- **Individual Phase Caps:** PG cap = 3.0; P1 cap = 320; PV cap = 200.
- **Stated Allocation Balance:** 725.6 node-h.
- **Half-Balance Threshold:** $725.6 / 2 = 362.8$ node-h.
- While each individual phase cap ($3.0 < 362.8$, $320 < 362.8$, $200 < 362.8$) satisfies the half-balance constraint, the **sum of the phase caps is $3.0 + 320 + 200 = 523.0$ node-h**.
- 523.0 node-h represents **72.1% of the entire unverified balance**, leaving a margin of only 202.6 node-h for all remaining project activities.
- The expected total spend of 449 node-h represents **61.9% of the balance**, which directly violates the principle of the half-balance rule for the campaign as a whole.

### Can Any Phase Overrun Silently?
**Yes. Phase P1 is highly vulnerable to silent, un-gated overruns.**
1. **Lack of In-Flight Job Accounting:**
   - Stop rule ST3 (lines 149–150) states: *"Every submission is gated against its phase cap from sacct, as COV2D's gate did."*
   - As in COV2D, the `sacct` gate executes **only at submission time**.
   - Phase P1 entails 1,450 unfolding toys ($200+200+50+200+400+400$). If these jobs are submitted as a large array or concurrently in Slurm, they run simultaneously in the queue.
   - If Perlmutter compute nodes encounter I/O contention on Lustre/pscratch, memory thrashing, or prolonged GPU/CPU execution loops, jobs can run up to their individual Slurm walltime limits (`#SBATCH -t`).
   - The declaration does not specify the per-job walltime limit or a watchdog mechanism. If the per-job limit is set to the standard 1–2 hours instead of a tight 20-minute bound, a batch of stalling jobs can consume hundreds of node-hours beyond the 320 node-h cap before any post-execution gate checks `sacct`.
2. **Missing Wave Structure and N5 Submission Race:**
   - Table 3.2 lists N1 through N5 together in P1.
   - Line 121 states that N5 is skipped if N1 and N2 read "covers" or "under".
   - If P1 is submitted as a monolithic batch, N5 (76 node-h) will be submitted and executed **concurrently with N1 and N2**, burning 76 node-h before N1/N2 outputs have even been extracted or scored.
   - P1 lacks explicit wave dependencies requiring N1/N2 extraction, scoring, and gate approval prior to the submission of N5. *(Severity: BLOCKING)*

---

## 7. Categorized Findings and Concrete Remediations

### BLOCKING Findings (Must be resolved before binding)

1. **[BLOCKING-1] Candidate B3 is an Ad-Hoc Tail Scaling Rejected by External Review**
   - *Location:* §5.2, lines 267–268; §7, line 385.
   - *Defect:* B3 introduces an arbitrary eigenvalue inflation multiplier $\phi \in \{1, \dots, 100\}$ on modes above rank 73 without any physical model or measured bias vector. The review explicitly rejects scaling the covariance to pass held-out tunes.
   - *Fix:* Strike candidate B3 entirely from the pre-registration. Restrict candidate $K_B$ to explicit, debiased truth-model bias constructions (B1 and B2). If full-space coverage cannot be achieved via B1/B2, the workflow must route exclusively to Outcome C ($K_C$, subspace reporting).

2. **[BLOCKING-2] The $K_B$ Fluctuation Rule is Mathematically Defective for $p=205, N=200$**
   - *Location:* §5.2, lines 255–262.
   - *Defect:* $\max(\lambda_i, \hat{s}_i)$ induces severe positive Jensen bias; finite-sample noise from dominant modes in 200 toys replaces small tail eigenvalues with a statistical noise floor; Ledoit–Wolf shrinkage toward $\text{diag}(\hat{S})$ in cell space destroys physical off-diagonal correlations and distorts $V$'s eigenbasis.
   - *Fix:* Replace the per-mode maximum and cell-diagonal shrinkage. Calibrate the fluctuation correction using a parametric model or a broad band-scale factor across T2A's three principal bands (R1, R2, R3) with an unbiased estimator:
     $$\hat{s}_R = \frac{1}{|R|} \sum_{i \in R} \frac{u_i^T \hat{S} u_i}{\lambda_i}$$
     Apply a band scaling factor only if $\hat{s}_R - 1 > 3 \cdot \text{SE}(\hat{s}_R)$, preserving the relative eigen-spectrum within each band.

3. **[BLOCKING-3] Debiased Outer Product in B1 Violates Positive Semi-Definiteness (C-PSD Failure)**
   - *Location:* §5.2, lines 264–265.
   - *Defect:* $\hat{b}_t \hat{b}_t^T - S_t/N_t$ has up to 204 negative eigenvalues. Summing over 6 truths produces a matrix strictly negative definite on at least 199 dimensions, which will fail control C-PSD and cause a runtime crash in `numpy.random.multivariate_normal`.
   - *Fix:* Enforce positive semi-definiteness on $C_b$ via spectral truncation. Compute the eigendecomposition of the debiased sum and truncate negative eigenvalues to zero:
     $$C_b = \left[ \frac{1}{|F|} \sum_{t \in F} \left( \hat{b}_t \hat{b}_t^T - \frac{S_t}{N_t} \right) \right]_+ = \sum_{\mu: \kappa_\mu > 0} \kappa_\mu w_\mu w_\mu^T$$

4. **[BLOCKING-4] Logical Inversion in ST1 and the N5 Skip Condition**
   - *Location:* §3.2, line 121; §3.3, lines 135–139.
   - *Defect:* Same-event toys under-scatter by a factor of 0.44 in variance (KI 85). An estimator that severely under-covers on independent data will exhibit $M \approx 0.88$ on same-event toys, reading "covers". Skipping N5 when N1/N2 read "covers" skips the independent MC benchmark exactly when severe under-coverage is masked. Furthermore, nominal closure bias can push same-event toys to read "under" against $S1$, triggering a false construction error stop without checking N5.
   - *Fix:* Make N5 mandatory for all paths. Remove the conditional skip rule in line 121. Require N5 to establish the baseline ratio of held-out to same-event scatter before ST1 can evaluate whether an "over" or "under" reading in N1/N2 constitutes a construction error.

5. **[BLOCKING-5] Ineffective Custody via `O_NOATIME` and Validation Physics Leakage**
   - *Location:* §4.1, lines 191, 202–203; §4.2, lines 215–231.
   - *Defect:* File access times (`atime`) are not updated by `O_NOATIME` reads, rendering the custody check incapable of detecting read access on pscratch. In addition, validation tune #2 (`G18_10b`) shares its primary CCQE and 2p2h interaction models with build tune `G18_10a`, creating a direct physics leakage from the build set to the validation set.
   - *Fix:*
     (a) Implement cryptographic custody: encrypt the sealed 5D ratio files using `gpg` or `age` with a passphrase held exclusively by Joseph or the director; commit `PG-SEAL.sha256` and the ciphertext to HPSS; decrypt only during PV's bound execution.
     (b) Replace `G18_10b_02_11b` with a tune that does not share G18's CCQE/2p2h interaction models, or mandate that Outcome B disclose that the covariance is validated only against FSI variations of the seen Valencia/Nieves interaction model.

6. **[BLOCKING-6] Unsupported Allocation Balance and Un-Gated Batch Execution**
   - *Location:* §3, lines 83, 88; §3.2, lines 114–119; §3.3, lines 149–150.
   - *Defect:* The 725.6 node-h balance is unverified in committed records. Total caps equal 523.0 node-h (72% of claimed balance). Monolithic submission of P1's 1,450 toys can silently overrun caps if cluster jobs stall.
   - *Fix:*
     (a) Execute an authenticated iris balance connect and commit `BALANCE-RECEIPT.txt` before binding.
     (b) Partition P1 into strict, sequential Slurm job waves: Wave 1 (N1, N2), Wave 2 (N5, if retained), Wave 3 (N3, N4), Wave 4 (A1). Mandate pre-wave `sacct` gate checks and set strict `#SBATCH -t 00:25:00` walltime limits per toy job.

---

### MAJOR Findings (Design flaws requiring revision)

1. **[MAJOR-1] Mathematical Failure of Guard Arithmetic for $K_C$ at Small $k$**
   - *Location:* §6.4, lines 357–358.
   - *Defect:* The text asserts that leaving $[0.8, 1.25]$ requires a $5\sigma$ excursion for $k=5$. Because the guard $h = 0.072$ must be contained entirely within the interval, the distance to an "unresolved" reading is only $4.88\sigma$ at $k=5$, $1.50\sigma$ at $k=2$ (13.5% false failure rate), and $0.48\sigma$ at $k=1$ (63% false failure rate).
   - *Fix:* Enforce a minimum subspace dimension for $K_C$ ($k \ge 10$). Re-derive the exact analytical excursion distances accounting for $h(M)$, and tabulate the false-unresolved probability as a function of $k$.

2. **[MAJOR-2] Degeneracy of Band Means and P-4 for Reduced Subspaces ($K_C$)**
   - *Location:* §5.3, lines 276–282; §6.1, line 313; §6.2, lines 332, 334.
   - *Defect:* When $k \le 73$, bands R2 and R3 are empty, causing $Q_{R2}$ and $Q_{R3}$ to evaluate to `NaN` (vacuous pass). Furthermore, P-4 allows up to 2 modes to fail under-coverage; for $k \le 2$, 100% of the reported modes can fail while P-4 passes.
   - *Fix:* Specify that band checks P-2 apply only to non-empty bands ($|R| > 0$). Scale the allowed number of flagged modes in P-4 with $k$: allow 0 flagged modes for $k < 20$, 1 flagged mode for $20 \le k < 73$, and at most 2 modes for $k \ge 73$.

3. **[MAJOR-3] Execution Order Contradiction for Simulation Statistics in N4**
   - *Location:* §3.2, line 117; §3.4, lines 176–178.
   - *Defect:* Table 3.2 defines N4 as drawing N2 (simulation statistics) + 38 systematic bands. But line 176 states that simulation statistics enter N4 and PV only conditionally based on an R1 spread test. If the condition fails, N4 has already been generated with simulation statistics, and no budget exists to rerun N4 without them.
   - *Fix:* Redefine N4 in Table 3.2 to draw systematic bands on top of N1 (nominal response without simulation redraws). If N2's condition fires, add N2's measured variance matrix $\hat{S}_{\text{sim}} = \hat{S}_{\text{N2}} - \hat{S}_{\text{N1}}$ modularly to $V_F$ during P2.

4. **[MAJOR-4] Build-Set Admission Bar Omits Over-Coverage Check**
   - *Location:* §5.4, lines 285–289.
   - *Defect:* Section 5.4 requires candidates on the build set to not read "under", but completely omits checking whether candidates are flagged "over". Candidates that achieve passing $M$ by severely over-covering can pass admission into PV.
   - *Fix:* Update §5.4 to require that candidates on the build set are flagged neither "under" nor "over" by the joint binomial test.

5. **[MAJOR-5] Single-Run Exhaustion of the Validation Tune Catalog**
   - *Location:* §4.1, lines 186–193; §3.3, lines 153–154.
   - *Defect:* Only 4 GENIE v3 tune qualifiers exist in Perlmutter's `v3_04_00` product. Consuming 3 tunes in PG/PV leaves only 1 tune remaining, rendering ST4's mandate ("any later construction needs new sealed truths") impossible.
   - *Fix:* Adopt the Lean Option (2 validation truths: `G21_11b_00_000` and `G18_02b_02_11b`) as the primary design, reserving the remaining qualifiers for a second iteration if an unforeseen defect occurs.

---

### MINOR Findings (Editorial, typographical, and notation cleanups)

1. **[MINOR-1] Harmonize Lean Option Cost Accounting**
   - *Location:* §3, line 90.
   - *Defect:* The lean totals (393 with N5, 316 without N5) imply inconsistent PG costs of 3.0 node-h and 2.0 node-h, respectively.
   - *Fix:* Fix PG at $2 \times 0.66 = 1.33 \approx 1.5$ node-h for two tunes, setting the lean totals to 391.5 node-h (with N5) and 315.5 node-h (without N5).

2. **[MINOR-2] Correct Citation for GENIE v3 Qualifiers**
   - *Location:* §4.1, line 188.
   - *Defect:* `FD-F1-DECLARATION.md:76` does not list the four candidate qualifiers.
   - *Fix:* Cite the Perlmutter CVMFS path `/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/` directly.

3. **[MINOR-3] Explicit Variance Divisor Notation in Section 2**
   - *Location:* §2, line 63.
   - *Defect:* `v_i = var_s z_{s,i}` does not state whether the sample variance divisor is $N$ or $N-1$.
   - *Fix:* Explicitly specify divisor $N$ (`ddof=0`), ensuring the exact identity $q_i = v_i + m_i^2$ holds as in REGRADE.

4. **[MINOR-4] Missing Attenuation Rule for Empty Bands**
   - *Location:* §6.1, lines 312–314.
   - *Defect:* Handlers for empty slices in band evaluation are unspecified.
   - *Fix:* Add an explicit software specification: *"If $|R| = 0$, band $R$ is marked not applicable and omitted from P-2 evaluation."*

---

## 8. Final Recommendation

**Verdict: NO-GO.**

The draft pre-registration `COVFIX-DECLARATION.md` rev 1 must **not be bound**. Binding should remain blocked until a revised draft (rev 2) is prepared that:
1. Strikes candidate B3 and replaces the $K_B$ fluctuation rule with a sound, regularized estimator;
2. Enforces positive semi-definiteness on candidate B1 via spectral clipping;
3. Mandates N5 execution to resolve the KI 85 masking effect;
4. Implements cryptographic file custody and resolves the G18 interaction-model physics leakage;
5. Verifies the actual NERSC allocation balance via an authenticated connect and establishes intra-phase Slurm job waves.

Report completed: `2026-11-22`.
