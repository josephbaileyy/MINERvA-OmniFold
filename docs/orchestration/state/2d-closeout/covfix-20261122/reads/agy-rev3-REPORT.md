<!-- absence-ok: verbatim third-party read report -->
NO-GO

# Review of COVFIX Pre-Registration Declaration (DRAFT rev 3, 2026-11-22)

**Document Under Review:** [inputs/COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md)  
**Review Baseline:** [inputs/grok-rev2-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/grok-rev2-REPORT.md), [inputs/agy-rev2-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/agy-rev2-REPORT.md), [inputs/director-rev0-items.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/director-rev0-items.md), and cited project records.  
**Review Mandate:** Verification against external review Fix 1 ($\mathbb{E}[ee^T] = C_{\text{fluct}} + b b^T$; testing the matrix of cases along $V$'s eigenmodes; acceptable outcomes A, B, C; rejection of scaling the covariance until tunes pass).

---

## 1. Audit of Rev-2 BLOCKING and MAJOR Findings in Rev 3

Every BLOCKING and MAJOR finding from both rev-2 review reports ([grok-rev2-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/grok-rev2-REPORT.md) and [agy-rev2-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/agy-rev2-REPORT.md)) was audited against [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md) rev 3.

### 1.1 Grok Rev-2 Findings

| ID | Severity in Rev 2 | Summary of Finding | Status in Rev 3 | Exact Line(s) in Rev 3 & Remediation Details |
|---|---|---|---|---|
| **N-1** | **BLOCKING** | Fluctuation part subtracts relative $C_{\text{model}}$ from absolute $Q_R$, which $Q_R$ did not contain; carry formula uncited. | **CLOSED** | [Lines 24–27, 80–105, 369–378](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L24-L27): $K0$ explicitly defined by blocks: $K0_R = V_{F,0} + V_{b,0}$ with $V_{F,0} = Q_{\text{rep}}$ and $V_{b,0} = C_{\text{model\_abs}}(x_R)$. Carry is unified as $V(t) = D_t V D_t$ with $D_t = \text{diag}(\hat{x}_t / x_R)$. Fluctuation base $F_A$ is defined directly as $Q_{\text{rep}}$ (or with ST1's block regenerated), without invalid block subtraction. |
| **N-2** | **BLOCKING** | Outcome A amendment contradicts §5–§7 post-binding freeze, creating an unscoped pre-PV modification hatch. | **CLOSED** | [Lines 28–29, 51–53, 232–236, 247–248](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L28-L29): Confined to a single named exception. ST1 may amend only the code or inputs generating the firing block; all bars, seeds, validation truths, factor rules, and outcome hierarchies remain permanently frozen. Bound prior to P2. |
| **N-3** | **MAJOR** | 3-SE significance guard on pooled factor $\hat{f}_R$ lacked an operational SE definition; $1/N$ sample divisor introduced variance bias. | **CLOSED** | [Lines 30, 378–386](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L30): $\text{SE}(\hat{f}_R)$ explicitly defined as standard deviation over 2,000 joint bootstrap replicates at pre-committed seed `9_991_000`, resampling each ensemble within itself. $N_E/(N_E - 1)$ bias-correction factor applied to each term in the pooled average. |
| **N-4** | **MAJOR** | Justification that "C_b can only add" was false (eigenbasis rotation and $\lambda_1$ increase can drop ndf); subspace departure waved through. | **CLOSED** | [Lines 31, 406–413, 437](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L31): "C_b can only add" deleted. A formal residual stop is pre-committed: requires $\text{ndf}(K_B) == \text{ndf}(K_A)$ and that no kept mode of $K_A$ has a component outside $K_B$'s kept span with norm exceeding 0.1. (Note: The specific formulation introduces a new defect audited in §3). |
| **N-5** | **MAJOR** | ST1 construction error check was confined to band R1, ignoring tail bands R2 and R3 where T2A identified the largest excess. | **CLOSED** | [Lines 32, 219–226](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L32): ST1 expanded to fire if *any* band with at least 10 modes reads "under" or "over" under the guarded rule. |
| **N-6** | **MAJOR** | Joint null called phase N but claimed blind to truth at P2; phase N requires truth ratio $r_u$, violating seal. | **CLOSED** | [Lines 33–34, 448–450, 463–471](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L33-L34): Phase-N draw-matched null computation moved inside the sealed PV readout binary after decryption, with candidates frozen in `P2-FREEZE.sha256`. At P1/P2, ensembles use their own truths or the Gaussian null. |
| **N-7** | **MAJOR** | Guard falsely cited b1 declaration, which used a 5-draw Student-$t$ rather than a 2,000-draw bootstrap. | **CLOSED** | [Lines 35, 121–124](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L35): Erroneous b1 attribution removed; guard specified as COVFIX's own pre-committed operational rule ($t_{0.975, N-1} \cdot \text{SE}(X)$ via 2,000 bootstrap resamples at seed `9_990_000`). |
| **N-8** | **MAJOR** | Lean cell 4 claimed to rest on IBUKT A2 for all three vertices, but A2 contains no GiBUU draw. | **CLOSED** | [Lines 36, 152–153](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L36): Text explicitly states that lean cell 4 covers `genie_mec` and `nuwro` only, disclosing that GiBUU has no fixed-response ensemble in the lean campaign. |
| **N-9** | **MAJOR** | Encryption passphrase written to a filesystem file accessible to the shared Unix account. | **CLOSED** | [Lines 37–39, 274–283, 331–333](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L37-L39): Passphrase delivered strictly via piped stdin from director's wrapper; never touches disk, environment, arguments, or Slurm spool. Login node `/dev/shm` wiped in-process; plaintext scan enforced at job completion. |

---

### 1.2 agy Rev-2 Findings

| ID | Severity in Rev 2 | Summary of Finding | Status in Rev 3 | Exact Line(s) in Rev 3 & Remediation Details |
|---|---|---|---|---|
| **BLOCKING-1** | **BLOCKING** | Uncommitted allocation balance receipt (725.6 node-h uncited in repo). | **CLOSED in text** | [Lines 48, 154–156, 582–583](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L48): Explicitly recognized as a binding prerequisite: "Binding requires a committed iris receipt." Formally listed in §9.3. |
| **BLOCKING-2** | **BLOCKING** | Standing KI 85 policy defers held-out MC re-test; requires Joseph's ruling superseding deferral and no-change rules. | **CLOSED in text** | [Lines 45, 48, 237, 576–580](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L45): Explicitly stated in §9.1 that binding N5 and Outcome A requires Joseph's formal decision superseding both sentences of KI 85. Without it, N5 is dropped and Outcome A cannot change quoted bands. |
| **BLOCKING-3** | **BLOCKING** | PG generating session unnamed; director's passphrase uncommitted. | **CLOSED in text** | [Lines 48, 322–323, 331–333, 584–585](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L48): Formally designated as binding prerequisites in §4.2 and §9.3 (fresh session to be named at binding; director passphrase to be piped). |
| **MAJOR-1** | **MAJOR** | Execution architecture gap: batch worker jobs on Slurm compute nodes cannot access login-node `/dev/shm`. | **CLOSED** | [Lines 37–39, 274–283](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L37-L39): Resolved by pipeline restructuring: login-node connect uses `/dev/shm` to generate pseudo-data files and encrypt graded truths to disk; Slurm batch jobs unfold pseudo-data only without needing `/dev/shm` or secret keys; readout decrypts graded truths in memory from stdin pipe. |
| **MAJOR-2** | **MAJOR** | Bias under-coverage: averaging outer products ($1/|F_{\text{bias}}|$) dilutes model-specific variance by $1/5$. | **CLOSED** | [Lines 40–44, 397–404](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L40-L44): $C_b$ redefined as the SUM, not the mean, of debiased outer products over $F_{\text{bias}}$ ($|F_{\text{bias}}| = 6$). Each member's bias contributes at most $\approx 1$ to $\chi^2$, preventing dilution. Resulting over-coverage for smaller biases is addressed by one-sided total bar. |
| **MAJOR-3** | **MAJOR** | Intermediate unfolded toy cross sections on pscratch could be inspected prior to single-invocation readout. | **CLOSED** | [Lines 37–39, 276–277, 281–285, 444–446](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L37-L39): Graded truths $\sigma_t$ are encrypted on disk; intermediate unfolded vectors $\hat{\sigma}_s$ alone cannot reveal errors $e_s = \hat{\sigma}_s - \sigma_t$. Candidates are frozen in `P2-FREEZE.sha256` before PV runs, rendering intermediate inspection incapable of altering candidate definitions. |

---

## 2. Evaluation of the New Candidate and Verdict Structure

### 2.1 Soundness of Matrix Formulation and Relative Carry
1. **The Nominal Matrix $K0$:**
   $$K0_R = V_{F,0} + V_{b,0} = Q_{\text{rep}} + C_{\text{model\_abs}}(x_R)$$
   This directly repairs rev 2's dimensional error. $Q_{\text{rep}}$ (from `#1167` run2 `cov2d_Q_205.npz`) is the adopted G2R covariance and represents absolute detector/systematic/statistical fluctuations ($s5\_total + C_{\text{PL}}$). $C_{\text{model\_abs}}(x_R) = \text{diag}(x_R) C_{\text{model}} \text{diag}(x_R)$ is the absolute model covariance. This formulation is clean, exact, and matches the reported object applied by data users.
2. **The Relative Carry Formula:**
   $$V(t) = D_t V D_t, \quad D_t = \text{diag}(\hat{x}_t / x_R)$$
   Applying this single transformation to every candidate block reflects how cross-section uncertainties are propagated across truths in practice. Testing the carried covariance—rather than remaking 486 unfolds per truth as in COV2D—tests the precise object delivered to physics analyses, saving $\sim 184$ node-h while Phase P0 quantifies the approximation error at G18 and AR23.
3. **Candidate Decomposition ($V = V_F + V_b$):**
   Candidate $K_B = V_F + C_b$ strictly realizes external review Fix 1: $V_F$ scales baseline fluctuation $F_A$ by empirical spread $\hat{f}_R$ (measured on spread alone), while $C_b$ captures model-to-model displacement. The components occupy distinct mathematical representations.

### 2.2 Asymmetric PASS Architecture: Two-Sided Fluctuation and One-Sided Total
The PASS criteria at PV require:
- **Fluctuation ($V_F$), Two-Sided (P-1):** Pooled spread $F^F$ and all bands must read "covers" ($[0.8, 1.25]$ guarded; neither "under" nor "over").
- **Total ($V = V_F + V_b$), One-Sided (P-2, P-3, P-4):** Mean ratio $M$ must read "not under" ($M - h \le 1.25$); bands, joint test, and individual modes must not flag "under". Over-coverage is explicitly permitted and reported as "conservative through the bias block".

#### Does the one-sided total let a bad candidate through?
- **Under-described Fluctuation Cannot Pass:** Fluctuation is decoupled and evaluated against $V_F$ alone in $V_F$'s eigenbasis. An under-covering fluctuation block fails P-1 regardless of $V_b$.
- **Artificial Fluctuation Inflation Cannot Pass:** Inflating $V_F$ causes P-1 to read "over", failing PASS and routing to the INFLATED verdict.
- **Uncovered Bias Directions Cannot Pass:** $C_b$ is low-rank ($\text{rank} \le 6$). In the remaining 199 dimensions orthogonal to $F_{\text{bias}}$, $V_b = 0$. If a validation truth exhibits bias along any of these 199 dimensions, $V_F$ alone must absorb it. If $V_F$ is inadequate, total $M$ exceeds 1.25 or P-4 flags under-covering modes.
- **Arbitrary Inflation of $V_b$ is Prevented:** $C_b$ is deterministically generated by §5.2 without adjustable parameters.

### 2.3 Effect of $C_b$ as a Sum Over Six Truths
$$C_b = \left[ \sum_{t \in F_{\text{bias}}} \left( \hat{b}_t \hat{b}_t^T - \frac{S_t}{N_t - 1} \right) \right]_+, \quad F_{\text{bias}} = \{\text{nom}, \text{mec}, \text{nuwro}, \text{gibuu}, \text{G18}, \text{AR23}\}$$
1. **Trivial Total Pass Along Bias Subspace:**
   In T2A, G18 and AR23 generated large mean-error projections ($\bar{e}^T C^+ \bar{e} / \text{ndf} = 20.97$ and $13.61$, representing thousands in raw $\chi^2$). Summing their outer products endows $C_b$ with large eigenvalues along their bias vectors. Consequently, within $\text{span}(F_{\text{bias}})$, each member's bias contributes at most $\approx 1$ to $\chi^2$. Because validation truth `G21_11b` shares SuSAv2 MEC with AR23, its bias projection into this subspace will be heavily covered by $C_b$.
2. **Total Bar is Not Trivially Passed Overall:**
   Because $\text{rank}(C_b) \le 6$, $C_b$ offers zero protection across the orthogonal 199 dimensions. If validation tunes introduce novel kinematic distortions outside the 6-model span, the total bar will be challenged.
3. **Role of the Two-Sided Fluctuation Bar:**
   The two-sided fluctuation bar P-1 prevents $C_b$'s generous bias envelope from trivializing the validation test. P-1 tests whether the empirical scatter around shifted means matches $V_F$. If an analyst attempted to mask mis-modeled scatter with bias, or inflated fluctuation to pass total $\chi^2$, P-1 would refuse it.

### 2.4 What Outcome B Actually Certifies
Outcome B does **not** certify that the total covariance is minimal, tight, or optimal, nor does it certify coverage for arbitrary generator models outside GENIE v3.  
Outcome B certifies:
1. The detector and statistical fluctuation covariance $V_F$ is quantitatively calibrated (two-sided) to the empirical scatter observed across the model class.
2. Systematic generator model choice is bounded by a low-rank truth-model bias covariance $C_b$ constructed from the model family $F_{\text{bias}}$.
3. The carried covariance $V_F + C_b$ provides conservative coverage (does not under-cover) for the held-out validation tunes within the stated model class.

---

## 3. Technical Audit of Rev 3: Defects in Fidelity, Logic, Statistics, Prices, Custody, and ST1

### 3.1 Fidelity Against Inputs and Records
1. **Model Overlaps (§4.1, [lines 304–310](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L304-L310)):** Faithful to [FD-F1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/FD-F1-REPORT.md) §1.3. Discloses that `G21_11b` shares `SuSAv2MECPXSec` with AR23 while CCQE differs. Accurately quotes the official GENIE tune page regarding G18_02 vs G18_10.
2. **Key Check and Identies (§2, [lines 81–85](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L81-L85)):** Matches [run2-NODE-SHA256-excerpt.txt](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/run2-NODE-SHA256-excerpt.txt) line 8 (`ff66b91d...`) and [Q_rep-identity-check.txt](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/Q_rep-identity-check.txt).
3. **Trace and Subspace Diagnostics (§1, [line 72](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L72)):** $\tau = 0.0098$ and 142 kept modes match [regrade_2d_G18.json](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/regrade_2d_G18.json).
4. **F1 Generation Cost (§1, [line 75](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L75)):** Matches 1.327500 node-h in [FD-F1-REPORT.md:143](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/FD-F1-REPORT.md#L143).
5. **Director's 20% Mark (§6.4, [line 515](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L515)):** Matches [director-rev0-items.md:10](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/director-rev0-items.md#L10).

---

### 3.2 Verification of Node-Hour Pricing and Accounting
Every product, subtotal, wave total, and grand total in Section 3 ([lines 138–168](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L138-L168)) and Section 3.2 ([lines 196–207](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L196-L207)) was verified.

| Component | Unfolds (Full / Lean) | Unit Price | Full Total (node-h) | Lean Total (node-h) | Text Matches Exact Arithmetic |
|---|---|---|---|---|---|
| **N1** | $200 / 150$ | 0.19 | 38.00 | 28.50 | Exact match ([line 198](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L198)) |
| **N2** | $200 / 150$ | 0.19 | 38.00 | 28.50 | Exact match ([line 199](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L199)) |
| **N5** | $400 / 300$ | 0.19 | 76.00 | 57.00 | Exact match ([line 200](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L200)) |
| **N3** | $50 / 50$ | 0.19 | 9.50 | 9.50 | Exact match ([line 201](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L201)) |
| **Nominal Central** | $1 / 1$ | 0.19 | 0.19 | 0.19 | Included in P1 W1 ([line 142](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L142)) |
| **P1 Wave 1 Subtotal** | — | — | **161.69** | **123.69** | $38+38+76+9.5+0.19 = \mathbf{161.69}$; $28.5+28.5+57+9.5+0.19 = \mathbf{123.69}$ ([line 142](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L142)) |
| **N4** | $200 / 150$ | 0.19 | 38.00 | 28.50 | Exact match ([line 202](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L202)) |
| **A1f** | $180 / 0$ | 0.19 | 34.20 | 0.00 | Exact match ([line 203](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L203)) |
| **A1p** | $300 / 300$ | 0.19 | 57.00 | 57.00 | Exact match ([line 204](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L204)) |
| **A1 Central Unfolds** | $3 / 3$ | 0.19 | 0.57 | 0.57 | Included in P1 W2 ([line 143](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L143)) |
| **P1 Wave 2 Subtotal** | — | — | **129.77** | **86.07** | $38+34.2+57+0.57 = \mathbf{129.77}$; $28.5+0+57+0.57 = \mathbf{86.07}$ ([line 143](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L143)) |
| **P1 Total** | — | — | **291.46** | **209.76** | $161.69 + 129.77 = \mathbf{291.46}$; $123.69 + 86.07 = \mathbf{209.76}$ ([line 144](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L144)) |
| **PV** | $600 + 2$ central | 0.19 | **114.38** | **114.38** | $600 \times 0.19 + 2 \times 0.19 = 114.00 + 0.38 = \mathbf{114.38}$ ([line 146](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L146)) |
| **PG Range** | 2 tunes | actuals | **1.33–2.00** | **1.33–2.00** | Floored at F1 actuals ($1.3275$) ([line 141](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L141)) |
| **Grand Total (Full)** | — | — | **407.17–407.84** | — | $1.3275/2.0 + 291.46 + 114.38 = \mathbf{407.17} / \mathbf{407.84}$ ([line 148](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L148)) |
| **Grand Total (Lean)** | — | — | — | **325.47–326.14** | $1.3275/2.0 + 209.76 + 114.38 = \mathbf{325.47} / \mathbf{326.14}$ ([line 148](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L148)) |

- **Allocation and Caps:**
  - Balance = 725.6 node-h; Half-balance = 362.8 node-h.
  - Phase caps: PG (3.0), P1 (330 full / 240 lean), PV (135) are all individually $< 362.8$.
  - Phase cap sums: Full = $468$, Lean = $378$ ([line 159](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L159)). Correctly noted that cap sums exceed half-balance.
  - Lean grand total ($326.14 < 362.8$) satisfies the half-balance constraint unconditionally.

---

### 3.3 Statistical Formulas and Multiplicity in Section 6.4
1. **SE of Mean Ratio $M$ ([line 502](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L502)):**
   $$\text{SE}(M) = \sqrt{\frac{2}{N \cdot \text{ndf}}} = \sqrt{\frac{2}{300 \times 204}} = 0.005717 \approx 0.006 \quad (\text{Exact}).$$
2. **Excursion Limits at $k = 10, N = 300$ ([lines 424, 512–513](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L424)):**
   - $\text{SE}(M) = \sqrt{2 / (300 \times 10)} = 0.025820$.
   - $t_{0.975, 299} \approx 1.96793 \implies h = 1.96793 \times 0.025820 = 0.05081 \approx 0.051$.
   - High side edge: $1.25 - h = 1.19919 \implies (1.19919 - 1.0) / 0.025820 = \mathbf{7.71\sigma}$.
   - Low side edge: $0.8 + h = 0.85081 \implies (1.0 - 0.85081) / 0.025820 = \mathbf{5.78\sigma}$.
   - Text [line 513](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L513) states: *"about 7.7σ on the high side and 5.8σ on the low side"*. This corrects rev 2's typographical inversion.
3. **P-3 and P-4 Error Contributions ([lines 509–515](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L509-L515)):**
   - In rev 3, P-3 is one-sided ("does not flag under", [line 481](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L481)); P-3 over-coverage does not refuse. Thus P-3 false rejection size is $\le 0.025$.
   - P-4 per-mode critical size is $\alpha_i = 0.025/\text{ndf}$. By linearity of expectation, $P(\ge 1 \text{ false under-flag}) \le \mathbb{E}[\sum I_i] \le 0.025$.
   - Negligible P-1/P-2 tails ($> 5.7\sigma$) yield:
     $$P(\text{not PASS per truth}) \le 0.025 + 0.025 = 0.050$$
     $$P(\text{FAILS per truth}) \le 0.025 + 0.025 = 0.050$$
   - Over two truths by union bound:
     $$P(\text{not VALIDATED}) \le 2 \times 0.05 = \mathbf{0.10}; \quad P(\text{FAILS}) \le 2 \times 0.05 = \mathbf{0.10}$$
     Both strictly comply with the director's 20% ceiling ([line 515](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L515)).
4. **Debiased Outer Product ($C_b$):**
   With $S_t = \frac{1}{N_t} \sum_s (e_s - \hat{b}_t)(e_s - \hat{b}_t)^T$, $\mathbb{E}[S_t] = \frac{N_t - 1}{N_t} \Sigma_t$, so $\mathbb{E}\left[\frac{S_t}{N_t - 1}\right] = \frac{\Sigma_t}{N_t} = \text{Cov}(\hat{b}_t)$. Thus $\mathbb{E}\left[\hat{b}_t \hat{b}_t^T - \frac{S_t}{N_t - 1}\right] = b_t b_t^T$ exactly.

---

### 3.4 New Defects Identified in Rev 3

#### Defect 1: Fatal Over-Constraint in the Residual Stop (BLOCKING)
- **Reference:** Lines 410–413 (§5.2) and Line 437 (§5.4).
- **Analysis:**
  Section 5.2 states:
  > *"Residual stop: if ndf differs from K_A's, or any kept mode of K_A has a component outside K_B's kept span with norm above 0.1, K_B is not admissible."*
  
  And §5.4 lists this as a mandatory admission bar:
  > *"A candidate V = V_F + V_b is admissible only if, at N4 and at each A1p truth: ... C-PSD passes, and so does §5.2's residual stop."*

  This rule creates a catastrophic mathematical trap that will almost certainly terminate the study at P2:
  1. In $Q_{\text{rep}}$, the smallest eigenvalue ratio is $\lambda_{205} / \lambda_1 = 1.18 \times 10^{-12}$ ([Q_rep-identity-check.txt:5](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/Q_rep-identity-check.txt#L5)), which barely exceeds the cutoff threshold $10^{-12} \lambda_1$ ([line 109](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L109)).
  2. When $C_b$ (the sum of 6 large model-bias dyads) is added to $V_F$ to form $K_B$, $\lambda_1(K_B)$ increases substantially (typically by $20\%\text{--}50\%$).
  3. Because $C_b$ has rank $\le 6$, it contributes identically zero variance to the 199 orthogonal directions, meaning $\lambda_{205}(K_B)$ is not increased.
  4. Consequently, the relative eigenvalue $\lambda_{205}(K_B) / \lambda_1(K_B)$ drops below $10^{-12}$, automatically reducing $\text{ndf}(K_B)$ from 205 to 204.
  5. Because $\text{ndf}(K_B) \ne \text{ndf}(K_A)$, the residual stop fires unconditionally, declaring $K_B$ inadmissible!
  6. Furthermore, §5.4 applies the residual stop to *every* candidate $V$. If applied to $K_C$, its dimension $\text{ndf}(K_C) = k \le 205$ automatically violates $\text{ndf} == \text{ndf}(K_A)$, making $K_C$ inadmissible as well.
  7. Under ST2 ([line 238](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L238)), having no admissible candidate aborts the study at P2 with verdict "none" before PV ever runs.
  
  In project history, dropping mode 205 is standard floating-point regularization: in COV2D, AR23 dropped to ndf 204 while G18 had ndf 205 ([OUTCOME-20261108-cov2d.md:41](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/OUTCOME-20261108-cov2d.md#L41)), and in REGRADE 2D, G18 dropped from 205 to 204 ([regrade_2d_G18.json:52–53](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/regrade_2d_G18.json#L52-L53)) and was formally adopted by Joseph ([DECISION-20261114-g2r-adopted.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/DECISION-20261114-g2r-adopted.md)). Making a single near-cutoff mode an automatic disqualifier for candidate admission is statistically and numerically unsound.
- **Concrete Fix:**
  1. Base the relative cutoff $10^{-12}$ on $\lambda_1(V_F)$ or $\lambda_1(F_A)$ rather than $\lambda_1(K_B)$, preventing $C_b$'s large bias eigenvalues from artificially shifting the truncation boundary of orthogonal fluctuation modes; OR allow $\text{ndf}(K_B)$ to differ by $\pm 1$ from $\text{ndf}(K_A)$ when the dropped mode has eigenvalue $< 2 \times 10^{-12} \lambda_1$.
  2. Restrict the residual norm check ($\|u_i^{A, \perp}\| \le 0.1$) to the well-conditioned physical subspace (e.g., modes with $\lambda_i / \lambda_1 \ge 10^{-6}$, encompassing the top $\sim 113$ modes), preventing pure cutoff noise from triggering the stop.
  3. Clarify in §5.4 that the residual stop applies specifically to $K_B$ against $K_A$, and does not apply to $K_C$ (whose dimension $k$ is intentionally reduced).

---

#### Defect 2: ST1 Named Exception Lacks Compute Phase and Allocation Allocation for Block Regeneration (MAJOR)
- **Reference:** Lines 138–147 (§3 table), Lines 232–236 (§3.3), Line 372 (§5.1).
- **Analysis:**
  Section 3.3 authorizes a named exception to regenerate the generator of a block that fires ST1 (`universe`, `stat`, or `c08`). However:
  1. Blocks such as `universe` (100 Flux universes + 38 bands) and `stat` (300 bootstrap replicas) require substantial cluster computing to rebuild.
  2. Phase P2 is budgeted at 0 node-h (local), and no contingency allocation or execution phase is defined for regenerating a firing block.
  3. Under ST6 ([lines 164–168](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L164-L168)), any unbudgeted Slurm job submission will be rejected by the cumulative sacct ceiling if it exceeds Joseph's approved total.
- **Concrete Fix:** Add an explicit provision in §3.3 stating that if ST1's named exception requires Perlmutter compute to regenerate the firing block, the amendment must define a dedicated regeneration wave with an explicit node-hour price and ceiling, requiring Joseph's prior authorization and verifying headroom against the Iris balance.

---

#### Defect 3: ST1 Table First Row Name Mismatch with Q_rep File Keys (MINOR)
- **Reference:** Lines 221–226 (§3.3 Table).
- **Analysis:**
  The column header states `block under test (keys of Q_rep's file)`. The first row is labelled `the data-stream bootstrap method`. As established in §2 ([line 84](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L84)) and [Q_rep-identity-check.txt](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/Q_rep-identity-check.txt), the actual keys are `Q, s5_total, universe, stat, c08, C_PL`. If this row fires, the block to be regenerated in $Q_{\text{rep}}$ is `stat`.
- **Concrete Fix:** Update the row label to: `stat (data-stream bootstrap component; key stat)`.

---

#### Defect 4: Ambiguity Regarding Multiple ST1 Firing Triggers (MINOR)
- **Reference:** Line 28, Lines 231–235 (§3.3).
- **Analysis:**
  The text states: *"When ST1 fires, P2 and PV wait, and the firing row names the block. ST1's named exception... may change only the generator of the block that fired..."* The phrasing is strictly singular. If both `stat` and `universe` read "under" or "over", it is ambiguous whether the exception licenses regenerating both blocks or only one.
- **Concrete Fix:** Revise phrasing to: *"the generator(s) of the block(s) that fired"*.

---

#### Defect 5: Section 6.4 Low-Side Excursion Description on One-Sided Total Bar (MINOR)
- **Reference:** Lines 512–513 (§6.4).
- **Analysis:**
  Line 512 states: *"losing the guarded 'covers' label needs M > 1.25 − h or M < 0.8 + h... about 7.7σ on the high side and 5.8σ on the low side."*  
  Under §6.2, total check P-2 requires only "not under" ($M - h \le 1.25$). A low-side excursion ($M < 0.8 + h$) reads "over", which passes P-2. While mathematically descriptive of the interval $[0.8, 1.25]$, the low-side excursion is relevant to the two-sided fluctuation check P-1, not the one-sided total bar.
- **Concrete Fix:** Clarify that the $5.8\sigma$ low-side excursion applies to fluctuation check P-1 where "covers" is mandatory, whereas total check P-2 requires only "not under".

---

## 4. Binding Prerequisites and Final Recommendations

### 4.1 Status of Section 9 Prerequisites
As confirmed by the user prompt, the Section 9 prerequisites are known policy items rather than textual defects:
1. **Iris Balance Receipt (§9.3, [line 583](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L583)):** Requires committing `BALANCE-RECEIPT.txt` from a live Iris query before binding.
2. **KI 85 Joseph Ruling (§9.1, [lines 576–580](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L576-L580)):** Joseph must formally sign off on superseding both the deferral and the pre-publication no-change rule.
3. **Session and Passphrase Custody (§9.3, [lines 584–585](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L584-L585)):** Fresh PG session to be named by the director; director's piping wrapper prepared.
4. **Campaign Scale Choice (§9.2, [line 581](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix3/inputs/COVFIX-DECLARATION.md#L581)):** Joseph to select full ($\sim 407.8$ node-h) or lean ($\sim 326.1$ node-h).

The declaration text correctly identifies and routes each of these items.

---

### 4.2 Summary of Findings and Verdict

| Finding | Severity | Description | Concrete Fix Summary |
|---|---|---|---|
| **Defect 1** | **BLOCKING** | Residual stop in §5.2 and §5.4 unconditionally disqualifies $K_B$ (and $K_C$) when mode 205 drops below $10^{-12} \lambda_1$ due to $C_b$'s $\lambda_1$ increase, aborting study at P2. | Reference $10^{-12}$ cutoff to $\lambda_1(V_F)$, restrict residual norm check to physical modes ($\lambda \ge 10^{-6}\lambda_1$), and exempt $K_C$ from §5.2 stop. |
| **Defect 2** | **MAJOR** | ST1 named exception allows block regeneration but provides no compute budget or phase under ST6 cumulative ceiling. | Add provision in §3.3 that block regeneration requiring cluster compute must declare a dedicated wave with approved allocation. |
| **Defect 3** | **MINOR** | First row of ST1 table names method rather than `cov2d_Q_205.npz` file key (`stat`). | Update row label to `stat (data-stream bootstrap component; key stat)`. |
| **Defect 4** | **MINOR** | Singular phrasing in ST1 named exception leaves multiple simultaneous block triggers ambiguous. | Revise phrasing to "generator(s) of the block(s) that fired". |
| **Defect 5** | **MINOR** | Section 6.4 attributes low-side $5.8\sigma$ excursion to total ratio $M$ losing "covers", whereas P-2 is one-sided. | Clarify that low-side excursion is relevant to two-sided fluctuation check P-1. |

**Final Verdict:** **NO-GO.**  
Draft rev 3 represents outstanding progress: all rev-2 findings from both readers are resolved, the block structure and carry are mathematically unified, and custody enforceability is airtight. However, binding must be withheld until **Defect 1 (the residual stop fatal over-constraint)** is repaired to prevent an unintended automatic study termination at P2.
