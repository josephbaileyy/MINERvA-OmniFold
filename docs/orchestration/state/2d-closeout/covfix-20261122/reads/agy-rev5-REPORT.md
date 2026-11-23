<!-- absence-ok: verbatim third-party read report -->
NO-GO

# Audit Report: COVFIX Pre-Registration Declaration (Draft Rev 5)

**Reviewer:** agy (Independent Technical Review)  
**Target:** `inputs/COVFIX-DECLARATION.md` (Draft rev 5, 2026-11-23)  
**Prior Reports & Context:** `inputs/codex2-rev4.1-REPORT.md` (NO-GO on rev 4.1), `inputs/rev4.1-to-rev5.diff`, `inputs/DECISION-20261123.md`  
**Verdict:** **NO-GO**. Setting aside binding prerequisites (committed iris receipt, fresh PG session, director's passphrase wrapper), rev 5 cannot be bound as written due to two BLOCKING defects and four MAJOR defects introduced in the statistical calibration, binomial cutoff specification, and simulation pricing.

---

## 1. Disposition of codex-school2 Rev 4.1 Findings

Below is the status of every BLOCKING and MAJOR finding from [codex2-rev4.1-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/codex2-rev4.1-REPORT.md):

### 1.1 Outcome Licenses & Scoping
1. **Matrix of cases (MAJOR, rev 4.1 lines 248–275, 332–368):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 319–330, 345–346, 355–356](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L319-L330)). The diff explicitly binds how each source acts across pseudo-data, graded-truth, and unfolding simulation sides. It binds Data Poisson to pseudo-data only, band draws/lateral/norm/truth deformation $r_t$ to the nature side, and sim to the unfolding response side. It discloses that $N_4 - N_2$ is incremental scatter under an unverified additive model, and grounds A1f/A1p as in-sample.
2. **A and A, partial (BLOCKING, rev 4.1 lines 279–306, 660–661):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 370–375, 828–830, 859](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L370-L375)). ST1 is made a diagnostic trigger. Outcome A requires code-level proof of a defect (a reproducing unit test failing on the old builder and passing on the corrected builder, a named bug, and a post-fix diagnostic). Outcome "A, partial" reports the actual PV verdict or that PV did not run, and explicitly forbids licensing "still does not cover" unless the verdict is FAILS.
3. **Outcome B (BLOCKING, rev 4.1 lines 435–440, 593–597, 652–662):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 242–243, 632–635, 770–775, 831](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L242-L243)). The total bar is converted to an affirmative upper-bound tolerance test ($M + h \le 1.25$ and the same for every band). The claim that $C_b$ bounds a model class is excised. Outcome B licenses only the observed affirmative readings at the two named deformations under the declared toy law, reporting the held-out bias statistics separately.
4. **Outcome C (MAJOR, rev 4.1 lines 508–524, 599, 663):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 664–665, 832](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L664-L665)). The wording correction from B is applied, requiring publication of coefficient vectors, projected covariance, effective rank, and affirmative test results on $P_k$, without claiming failure of finer combinations.
5. **None and inconclusive (MAJOR, rev 4.1 lines 311, 450–454, 649–676):**
   - **PARTLY CLOSED** ([COVFIX-DECLARATION.md lines 580, 814–817, 833–834](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L814-L817)). §7 and the table correctly replace "inconclusive" with "no challenge", and mandate an affirmative baseline under-coverage challenge ($K_0$ FAILS at $\ge 1$ sealed truth) to license B or C. However, §5.1 at line 580 was missed during editing and still states: *"the validation family did not test the covariance, and PV is inconclusive (§7)"*, creating an internal textual contradiction.

### 1.2 Statistical Audit
6. **Guards, labels, and carry (MAJOR, rev 4.1 lines 143–189, 526–534, 554–561, 593–612):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 199–202, 242, 669–675, 704, 770–775](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L199-L202)). Affirmative total bar ($M + h \le 1.25$) is adopted; unresolved bands fail; P2 and PV bars are unified; CV nature without draws is bound to $\hat{x}_t$; finite non-zero carry factors on all 205 cells are enforced; and a per-reco-cell relative rounding check ($< 10^{-3}$) is added.
7. **Pooled $\hat{f}_R$ (MAJOR, rev 4.1 lines 458–479):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 599–609](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L599-L609)). The 3-SE rule is explicitly noted as a construction convention without error guarantees; conditioning on the shared simulation bank is disclosed; edge cases for $< 10$ modes are handled; stable sorting for ties is fixed; post-carry fit per truth and band is reported; and the scaling accounting for undrawn components is acknowledged.
8. **$C_b$, PSD projection, and bias reporting (MAJOR, rev 4.1 lines 481–494, 559–560, 662):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 620–635, 708–713](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L620-L635)). $C_b$ is designated a fitted bias allowance; the held-out debiased quadratic $Q_u = \hat{\beta}_u^\top C_b^+ \hat{\beta}_u - \operatorname{tr}(C_b^+ \Sigma_u)/(N_u - 1)$ is explicitly formulated; the pseudoinverse cutoff ($10^{-12} \lambda_{\max}(C_b)$), $V_F^{-1}$ norm metric for outside-span projection, zero-denominator reporting, and bootstrap uncertainties are bound.
9. **Residual rule and $K_C$ (MAJOR, rev 4.1 lines 161–174, 230–240, 496–524, 599):**
   - **CLOSED** ([COVFIX-DECLARATION.md lines 293–299, 642–646, 652–658](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L293-L299)). P0 controls are fully specified with evaluation frames; a span-level principal-angle sine cutoff ($> 0.1$) on well-determined modes is adopted; $K_C$ combinations are fixed at $x_R$; both projected grading matrices must maintain rank $k$ ($> 10^{-12}$ condition); and measurability study provenance/eligibility rules are frozen before seal generation.
10. **The $k \ge 25$ floor (MAJOR, rev 4.1 lines 517–522, 637–640):**
    - **PARTLY CLOSED** ([COVFIX-DECLARATION.md lines 662, 808–810](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L808-L810)). 25 is retained as a reporting floor, and five-sigma claims are demoted to illustrations calibrated by whole-rule simulation. However, lines 808–810 introduce a mathematical contradiction by quoting the formula for the *unnormalized* spread SE while citing the normalized $\tilde{F}$ distances (see Section 2.1).
11. **Written null and false-FAIL simulation (BLOCKING, rev 4.1 lines 545–587, 633–645):**
    - **PARTLY CLOSED** ([COVFIX-DECLARATION.md lines 730–765](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L730-L765)). The structure is completely overhauled: a candidate-matched calibration law is specified with centered drawn-only fluctuation ($V_{F,\text{drawn}} = V_F - [C_{\text{PL}} + c08]$), fixed bias alternatives on an eigenpair grid, and an ensemble-based testability simulation (200 ensembles $\times$ $N$ toys with whole-rule bootstrap guards) recording both "not PASS" and "FAILS" with Clopper–Pearson bounds. However, new defects were introduced: the bias grid is undefined for $K_0$ and $K_A$ (which lack $C_b$), and the replicate count and seed for determining $q$ and $p_i$ were inadvertently dropped from the text (see Section 2.1).
12. **$K_J$, $p_i$, and binomial size (MAJOR, rev 4.1 lines 561–598, 633–642):**
    - **PARTLY CLOSED** ([COVFIX-DECLARATION.md lines 716–728, 802–807](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L716-L728)). No-cutoff sentinels are bound; analytic probabilities ($0.6827$) are set for the Gaussian fallback; conservative Clopper–Pearson bounds (lower end for under-cutoffs, upper end for over-cutoffs) are specified. But because the replicate bank definition was deleted, the estimation procedure for $q$ and $p_i$ is unexecutable.
13. **False-PASS bounds (BLOCKING, rev 4.1 lines 614–632):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 242, 757–760, 772, 796–801](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L796-L801)). The total bar is converted to an affirmative upper-bound check ($M + h \le 1.25$). A candidate with true ratio $\ge 1.25$ at either truth passes there with probability $\le 0.025$, giving a per-candidate validation probability $\le 0.025$ and a union bound of $\sim 0.075$ across three candidates. Gated by deficit simulation with a $0.10$ Clopper–Pearson upper bound.

### 1.3 Blindness and Custody
14. **Isolation, seeds, authenticated encryption, scans (BLOCKING, rev 4.1 lines 99–101, 347–365, 403–433, 444–446, 539–547):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 449–469, 524–560](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L449-L469)). PG, PV writer, and PV readout are run under director-controlled isolation via wrapper; seeds are director-held and committed by sha256 before PG; authenticated encryption (`gpg AES256` or `age`) is mandatory; synthetic seal wrapper test is added; campaign-owned paths are content-scanned after writer and readout with trap cleanup; cooperative no-regeneration assumption is stated.
15. **Spent-once protocol & crash semantics (BLOCKING, rev 4.1 lines 315–326, 358–365, 673–676):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 408–422](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L408-L422)). Append-only consumption record controlled by director, keyed by seal and candidate digests, acquired atomically (`mkdir`) before first decrypt; role spent at first decrypt; crash rerun policies defined; second grading of exposed toys strictly forbidden.
16. **Probe and novelty test (MAJOR, rev 4.1 lines 374–399, 435–446, 510–516):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 510–515, 653–655](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L510-L515)). The novelty test is formalized to require that at least one of CCQE or 2p2h is absent from *both* spent tunes; pairwise spent recombinations are rejected.

### 1.4 Prices and Stops
17. **ST1 and named exception (BLOCKING, rev 4.1 lines 279–309):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 351–378, 389–392](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L351-L378)). Common basis $Q_{\text{rep}}$ carried to $\hat{x}_{\text{MC}}$ is specified; spread-only reading is enforced; code-level reproducing unit tests are mandatory; a single exception covers all rows firing up to then, with subsequent firings halting the campaign; KI 85 supersession is recorded.
18. **Exception pricing (BLOCKING, rev 4.1 lines 198–202, 302–305):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 380–386, 467–469](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L380-L386)). The exception branch is moved into an independent phase PX outside P1's cap, with concrete itemized pricing and an explicit stop rule gating it against Joseph's cumulative ceiling.
19. **ST2 (MAJOR, rev 4.1 lines 311, 453–454, 528–537, 649–665):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 394–396, 780–790, 814–821](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L394-L396)). $K_A$ is included in PV eligibility; verdict precedence is formalized in §6.4.
20. **ST3 and ST6 reservation ledger (MAJOR, rev 4.1 lines 212–226, 313, 328):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 398–406](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L398-L406)). Serialized reservation ledger under `flock` keyed by allocation job ID; reserves nodes $\times$ `--time` (1.5$\times$ per-toy price); terminal charge reconciliation once per job; atomic gating against phase cap and approved cumulative ceiling.
21. **ST4 and ST5 guard refusals and missing toys (MAJOR, rev 4.1 lines 315–326, 571–573, 675–676):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 425–432, 748–750](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L425-L432)). Explicit distinction between candidate/input C-PSD failures (terminal ST5 refusal) and surrogate remainder $G(t)$ C-PSD failure (safe fallback to Gaussian $N(0, V_{F,\text{drawn}})$). Missing toys allowed $\le 2$ identical-seed retries; $> 6$ missing toys ($2\%$) triggers terminal UNRESOLVED.

### 1.5 Fidelity to the Records
22. **Old tunes & 142 eigenvectors (MAJOR, rev 4.1 lines 121–123, 238–244, 444–446):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 164–166, 293–294](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L164-L166)). Clarified that 142 kept eigenvectors had components outside the new span without loss of rank; P0 residual test identified as a go/no-go control on spent data.
23. **Part C report & A1 maps (MAJOR, rev 4.1 lines 135–136, 267–274, 481–492):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 182–185, 339–345](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L182-L185)). Section and file citations to `RE2-PARTC-REPORT.md §7` and `cmodel_R.json` provided; A1 explicitly defined as in-sample deformations matching $C_{\text{model}}$ vertices.
24. **Differences between PV and COV2D (MAJOR, rev 4.1 lines 367–368):**
    - **CLOSED** ([COVFIX-DECLARATION.md lines 474–482](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix5/inputs/COVFIX-DECLARATION.md#L474-L482)). Differences explicitly enumerated beyond simulation weights (tunes, grading matrix, central-vector convention, null/decision rules).

---

## 2. Technical Audit of Rev 5 Changes & New Defects

### 2.1 Statistics & Mathematical Formulations (§6.1–§6.5)

#### 1. Expected Spread $F_{\exp}$ and Normalized Ratio $\tilde{F}$ (Lines 696–700)
- **Mathematical Structure:** For an error vector $e_s$ drawn with covariance $V_{F,\text{drawn}} = V_F - [C_{\text{PL}} + c08]$, the mode variance $v_i^F$ under $V_F$'s eigenbasis has expected value $\mathbb{E}[v_i^F] = \frac{N-1}{N}[1 - u_i^\top(C_{\text{PL}} + c08)u_i / \lambda_i^F]$. Summing over all $ndf_F$ modes gives $\mathbb{E}[F^F] = \frac{N-1}{N}(1 - u) = F_{\exp}$, where $u = \operatorname{tr}(V_F^+ [C_{\text{PL}} + c08])/ndf_F$. Hence $\mathbb{E}[\tilde{F}] = 1$ globally.
- **Defect (MAJOR):** Line 699 states: *"What is labelled is the normalized ratio $\tilde{F} = F^F / F_{\exp}$, and the same per band."* If this means each band ratio $F_R^F$ is divided by the *global* $F_{\exp}$, this is statistically incorrect. $C_{\text{PL}}$ (rank 2) and $c08$ are concentrated in specific eigenmodes (typically in R1). For higher rank bands (e.g. R2 or R3) where $u_R = 0$, $\mathbb{E}[F_R^F] = \frac{N-1}{N}$. Dividing by $F_{\exp} = \frac{N-1}{N}(1 - u)$ introduces an artificial positive bias of $+u/(1 - u) \approx +1\%$ to $+2\%$. If the intention was for each band to compute its own $u_R = \operatorname{tr}_R(V_F^+ [C_{\text{PL}} + c08])/ndf_R$, the text never defines $u_R$ or band-specific $F_{\exp,R}$. Furthermore, for $K_C$ on subspace $P_k$, $u$ is undefined.

<!-- absence-ok: verbatim third-party read report -->
#### 2. The Calibration Law & Bias Grid (Lines 732–745)
- **Defect (BLOCKING):** Line 743 defines the bias grid:
  $$b = \pm \sqrt{\kappa_j} w_j \quad \text{for each eigenpair } (\kappa_j, w_j) \text{ of } C_b \text{ carried to } t.$$
  However, $C_b$ is constructed exclusively for candidate $K_B$ (§5.2). Baseline $K_0$ and repaired candidate $K_A$ have no $C_b$ block—their bias block is $V_b = C_{\text{model\_abs}}$ (§2, §5.1). When §6.2's testability simulation runs on $K_0$ (which runs unconditionally as the baseline under ST2) or on $K_A$, the calibration law cannot be evaluated because $C_b$ does not exist. The declaration must state whether $K_0$ and $K_A$ evaluate the grid over the eigenpairs of their own bias block $C_{\text{model\_abs}}(t)$ (which has rank 3, giving 6 non-zero grid points), borrow $K_B$'s $C_b$, or test $b = 0$ only.

#### 3. Binomial Cutoffs & Missing Replicate Specification (Lines 719–728)
- **Defect (BLOCKING):** Rev 4.1 explicitly declared the replicate budget in line 563: *"20,000 null replicates at seed 9_992_000 give q, the in-region probability, and $k_J$ and $k_J^+$."* Rev 5 replaced this with conservative Clopper–Pearson cutoffs (lines 726–728), but **completely deleted the sentence establishing the replicate sample size and seed**. Line 726 vaguely refers to *"the calibration law's replicates"*, but nowhere in §6.1 or §6.2 is the number of replicates or random seed specified. Without a declared replicate count and seed, the empirical probabilities $\hat{q}$ and $\hat{p}_i$ and their Clopper–Pearson intervals are non-deterministic and unexecutable. Furthermore, the text must clarify at which bias point $b$ the marginal probabilities $p_i$ are calibrated (at $b = 0$, or per grid point).

<!-- absence-ok: verbatim third-party read report -->
#### 4. Whole-Rule Simulation Computation & Pricing (Lines 753–765, 247–256)
- **Defect (MAJOR):** Line 753 specifies that for each candidate, truth, and grid point $b$, 200 simulated ensembles of $N$ errors are evaluated by the *entire* §6.3 rule, including the 2,000-resample bootstrap guards.
  - At P2 (lines 674, 765), this simulation runs on 4 truths ($N_4$ and 3 A1p truths) across 3 candidates ($K_A, K_B, K_C$). Across up to 11 grid settings (9 false-FAIL + 2 false-PASS), this yields $12 \times 11 \times 200 = 26,400$ simulated ensembles.
  - Running 2,000 bootstrap resamples on 26,400 ensembles requires **52.8 million bootstrap evaluations** across 205 modes.
  - Yet Table 3 (line 254) prices P2 as `0 (local)`. Running tens of millions of bootstrap resamples in a local unpriced session will cause severe walltime or memory exhaustion.
  - For PV, the readout is allocated an unmeasured estimate of 1.0 node-h on an exclusive compute node.
  - Concrete fix: The simulation must either use an analytic or plug-in approximation for the bootstrap guard within the outer simulation loop, or P2 must be given an explicit compute allocation.

#### 5. False-PASS Boundaries and Stated Rates (Lines 796–801)
- **Audit:** The shift to an affirmative upper-bound test ($M + h \le 1.25$) ensures that at the critical boundary (expected $M = 1.25$), the pass probability is governed by the lower $2.5\%$ tail of the studentized guard, $\mathbb{P}(M + t_{0.975} \mathrm{SE} \le 1.25) \approx 0.025$.
- Because VALIDATED requires passing at *both* truths, if a candidate has an under-coverage deficit at truth 1, its validation probability is $\le 0.025$. Across three candidates, the union bound is $\le 3 \times 0.025 = 0.075$.
- In the deficit simulation (§6.2), with 200 trials and true $p = 0.025$, the expected pass count is 5, yielding a 95% Clopper–Pearson upper bound of $0.0574$, safely below the $0.10$ testability gate. The probability of an empirical pass count $\ge 12$ (which would breach $0.10$) is $0.0048$. The logic and stated rates are sound.

#### 6. $k \ge 25$ Floor Illustration Arithmetic (Lines 808–810)
- **Defect (MAJOR):** Lines 808–810 state:
  $$\text{The SE of the } 1/N \text{ spread mean is } \sqrt{2(N - 1)/(N^2 k)}. \text{ With } \tilde{F}\text{'s normalization, the low and high 'covers' edges sit at about 5.1 and 6.8 SE at } N = 100\dots$$
  - $\sqrt{2(N - 1)/(N^2 k)}$ is the standard error of the *unnormalized* centered sample variance $F^F$.
  - When normalized as $\tilde{F} = F^F / (\frac{N-1}{N})$, the standard error of $\tilde{F}$ is:
    $$\mathrm{SE}(\tilde{F}) = \frac{\sqrt{2(N-1)/(N^2 k)}}{(N-1)/N} = \sqrt{\frac{2}{(N-1)k}}.$$
  - At $N = 100, k = 25$, $\mathrm{SE}(\tilde{F}) = \sqrt{2/2475} \approx 0.02843$. With $t_{0.975, 99} \approx 1.9842$, the guard is $h \approx 0.05641$. The distances from mean $1.0$ to the edges $0.8$ and $1.25$ are $(1.0 - 0.8 - h)/\mathrm{SE} = 5.05$ SE and $(1.25 - 1.0 - h)/\mathrm{SE} = 6.81$ SE (rounding to 5.1 and 6.8).
  - But evaluating the printed formula $\sqrt{2(N-1)/(N^2 k)}$ gives $\mathrm{SE} = 0.02814$ and distances $4.77$ and $7.25$ SE.
  - Stating the unnormalized formula while claiming it yields the normalized distance figures is an internal mathematical error.

---

### 2.2 Verdict Precedence & Candidate Selection (§6.4, §7)
- **Precedence Hierarchy (§6.4):**
  1. `NOT TESTABLE` (testability check fails at either truth)
  2. `FAILS` (affirmative under-coverage at either truth)
  3. `INFLATED` (over-coverage at either truth without failure)
  4. `VALIDATED` (P-1 through P-4 pass at both truths)
  5. `UNRESOLVED` (indeterminate band or margin)
- **Baseline Challenge Requirement (§7):** Outcomes B and C require that $K_0$ receives a `FAILS` verdict at $\ge 1$ truth. If $K_0$ is `NOT TESTABLE` at either truth, precedence rule #1 assigns `NOT TESTABLE` to $K_0$, treating the baseline as unchallenged. This strictly complies with codex2's mandate.

---

### 2.3 Pricing and Exception Phase PX (§3.3)
- **Arithmetic Check:** The itemized costs in PX at $0.19$ node-h/unfold are:
  - `universe`: $175 \times 0.19 = 33.25$ node-h
  - lateral rebuild: $10 \times 0.19 = 1.90$ node-h
  - `stat`: $300 \times 0.19 = 57.00$ node-h
  - `c08`: $80 \times 0.19 = 15.20$ node-h
  - redraw of $N_4$ (200) and $A1p$ (300): $500 \times 0.19 = 95.00$ node-h
  - Subtotal: $202.35$ node-h.
- **Budget Interaction with ST6:** Joseph approved a cumulative ceiling of $\sim 409$ node-h (`DECISION-20261123.md`).
  - If ST1 fires after W1 ($162.07$ node-h spent), adding PX ($202.35$ node-h) and PV ($115.38$ node-h) gives $479.80$ node-h, exceeding the 409 node-h ceiling.
  - If ST1 fires on W2 ($291.84$ node-h spent), adding even universe ($33.25$) and redraws ($95.00$) exceeds the ceiling before PV.
  - The declaration explicitly recognizes this (line 386): *"PX must fit Joseph's approved total under ST6, or it goes to Joseph. PX is not inside P1's cap."* This provides an unambiguous stop rule.

---

### 2.4 Custody, Blindness, and Spent-Once Protocol (§3.3, §3.4, §4.2)
- **Execution Boundary:** Director-controlled wrapper executes PG, PV writer, and PV readout. Passphrase is piped via stdin, never written to disk or environment.
- **Independent Generation Barrier:** Seeds for PG are director-held and committed by sha256 before generation, preventing pre-computation of validation truths.
- **Authentication & Scanning:** OpenPGP AES256 or `age` with mandatory integrity protection; unauthenticated CBC is rejected. Content-based scanning of `/dev/shm`, `/tmp`, and campaign paths with trap cleanup is enforced.
- **Spent-Once Protocol:** Append-only consumption record keyed by seal and candidate digests in director's workspace, locked atomically (`mkdir`), spending each role at first decrypt.
- The custody protocol is fully airtight.

---

### 2.5 Consistency with DECISION-20261123
- **Size:** Rev 5 commits to the Full campaign as designed, with two sealed tunes, full P1 counts, and $N_5$ unconditional, capped at $\sim 409$ node-h (lines 272–274, 876–879).
- **KI 85:** Both sentences of KI 85 are superseded; $N_5$ runs unconditionally; outcome A may modify the covariance for the journal or a subsequent Zenodo release (lines 389–392, 870–875).
- **Second Reader:** codex-school2 is officially designated as second reader alongside agy (lines 97–99, 879).
- All items align exactly with Joseph's decision.

---

### 2.6 Internal Contradictions and Stale Text

1. **Line 580 vs. §7 Line 834 ("inconclusive" vs. "no challenge"):**
   - Line 580: *"and PV is inconclusive (§7)."*
   - §7 line 834: outcome is officially titled `no challenge`. Line 580 was missed during editing.
2. **Line 860 Stale Reader Name:**
   - Line 860: *"a Grok and an agy read"*.
   - Grok's credit is exhausted; DECISION-20261123 and lines 97 & 879 appoint `codex-school2`. Line 860 must read: *"a codex-school2 and an agy read"*.
3. **Nomenclature Drift for Seed Block:**
   - The seed variance block is inconsistently referred to as `c08` (lines 180, 364, 382, 697, 738), `C08` (line 696), `C_seed` (line 446), and `seed term` (line 740).
4. **Citation Reference in Line 579:**
   - Line 579: *"If K0 passes at both sealed truths (§6.2)"*. PASS is defined in §6.3, and VALIDATED in §6.4.

---

## 3. Findings Summary, Severity & Concrete Fixes

Setting aside the binding prerequisites (iris receipt, PG session, passphrase), **rev 5 is NOT ready to bind**. The following issues must be resolved:

<!-- absence-ok: verbatim third-party read report -->
### Finding 1: Calibration Law Bias Grid Undefined for Baseline $K_0$ and $K_A$
- **Severity:** **BLOCKING**
- **Location:** Line 743
- **Description:** Line 743 constructs the bias grid from the eigenpairs of $C_b$. $C_b$ does not exist for $K_0$ or $K_A$, leaving the calibration law undefined for the mandatory baseline.
- **Concrete Fix:** Edit line 743 to read:
  > *"- $b = \pm \sqrt{\kappa_j} w_j$ for each eigenpair $(\kappa_j, w_j)$ of the candidate's own bias block $V_b$ carried to $t$ (for $K_0$ and $K_A$, $V_b = C_{\text{model\_abs}}(x_R)$, having rank 3; for $K_B$, $C_b$, having rank at most 4; for $K_C$, projected onto $P_k$); at most 9 grid points."*

### Finding 2: Replicate Budget and Seed Omitted for Binomial Cutoff Estimation
- **Severity:** **BLOCKING**
- **Location:** Lines 719–728
- **Description:** The text mandates estimating $q$ and $p_i$ and computing Clopper–Pearson intervals from the calibration law's replicates, but omits the sample size, seed, and bias setting.
- **Concrete Fix:** Insert in line 726:
  > *"- Where they are estimated from the calibration law, 20,000 null replicates are generated under the law with $b = 0$ at seed 9_992_000 to determine $\hat{q}$ and $\hat{p}_i$. The under-cutoffs use the lower end of the 95 % Clopper–Pearson interval and the over-cutoffs the upper end..."*

### Finding 3: Per-Band Normalization Ambiguity for $F_{\exp}$
- **Severity:** **MAJOR**
- **Location:** Lines 696–700
- **Description:** Applying a single global $F_{\exp}$ across all bands biases higher-rank bands where $C_{\text{PL}}$ and $c08$ have zero support by $\sim 1\%$.
- **Concrete Fix:** Update lines 697–700 to define band-specific expectations:
  > *"For a correct $V_F$, the expected spread ratio for a band $R$ (or total) is $F_{\exp,R} = ((N - 1)/N)(1 - u_R)$, with $u_R = \operatorname{tr}_R(V_F^+ [C_{\text{PL}}(t) + c08(t)])/ndf_R$ using the carried unscaled blocks (and $u$ for the total). What is labelled is $\tilde{F} = F^F / F_{\exp}$ and $\tilde{F}_R = F_R^F / F_{\exp,R}$. Where $\hat{f}_R$ scaled $V_F$, $u_R$ is an approximation, disclosed."*

### Finding 4: Inconsistent SE Formula in $k \ge 25$ Reporting Floor Illustration
- **Severity:** **MAJOR**
- **Location:** Lines 808–810
- **Description:** Stating the unnormalized spread SE formula $\sqrt{2(N - 1)/(N^2 k)}$ while quoting normalized $\tilde{F}$ distances (5.1/6.8 and 10.3/13.3 SE) is mathematically contradictory.
- **Concrete Fix:** Replace the formula in line 808 with:
  > *"The SE of the normalized spread ratio $\tilde{F}$ is $\sqrt{2/((N - 1)k)}$. With $\tilde{F}$'s normalization, the low and high 'covers' edges sit at about 5.1 and 6.8 SE at $N = 100$, and 10.3 and 13.3 SE at $N = 300$."*

### Finding 5: Computational Explosion of Whole-Rule Testability Simulation in Local P2
- **Severity:** **MAJOR**
- **Location:** Lines 254, 753–765
- **Description:** Running 200 ensembles $\times$ 2,000 bootstrap resamples across 11 grid points for 4 truths and 3 candidates requires 52.8 million resamples, which is unpriced (`0 (local)`) and computationally prohibitive.
- **Concrete Fix:** In §6.2, specify that during the inner ensemble loop of the testability simulation, the bootstrap guard is computed via an empirical standard error or analytic normal/studentized approximation, reserving the 2,000-resample bootstrap for the final empirical data readout. Alternatively, assign P2 an explicit compute allocation.

### Finding 6: Stale "inconclusive" Reference in §5.1 Line 580
- **Severity:** **MINOR**
- **Location:** Lines 579–580
- **Description:** Refers to §7's outcome as "inconclusive" and cites §6.2 for PASS.
- **Concrete Fix:** Edit lines 579–580 to read:
  > *"If $K_0$ is VALIDATED at both sealed truths (§6.4), the comparison showed no need for a change at those truths, and PV produces 'no challenge' (§7)."*

### Finding 7: Stale Reference to Grok in §8 Line 860
- **Severity:** **MINOR**
- **Location:** Line 860
- **Description:** Text cites "a Grok and an agy read", contradicting DECISION-20261123.
- **Concrete Fix:** Change line 860 to: *"a codex-school2 and an agy read"*.

### Finding 8: Seed Block Nomenclature Standardization
- **Severity:** **MINOR**
- **Location:** Lines 180, 446, 696, 697, 738, 740
- **Description:** Inconsistent naming (`c08`, `C08`, `C_seed`, `seed term`).
- **Concrete Fix:** Standardize throughout on `c08` (defining it at first mention as the estimator seed block).

---

## Conclusion & Recommendation

Draft rev 5 makes significant, commendable progress in resolving the architecture of Fix 1, adopting affirmative tolerance tests, formalizing custody under director-held isolation, and structuring the exception branch PX. However, because the calibration law's bias grid is undefined for the baseline $K_0$ and the replicate budget for the binomial cutoffs was dropped during editing, **the declaration is not ready to bind**. Implementing the concrete fixes above will produce an airtight rev 6 ready for binding.
