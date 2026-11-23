<!-- absence-ok: verbatim third-party read report -->
NO-GO

# Review Report: COVFIX Declaration (DRAFT rev 4)

**Document Under Review:** `inputs/COVFIX-DECLARATION.md` (DRAFT rev 4, 2026-11-22)  
**Prior Reviews Audited:** `inputs/agy-rev3-REPORT.md`, `inputs/grok-rev3-REPORT.md`  
**Reviewer:** agy (Antigravity Agentic Assistant)  
**Date:** 2026-11-22  
**Final Verdict:** **NO-GO** (Draft rev 4 resolves all previous BLOCKING defects from rev 3, but contains three new MAJOR defects—including an internal text contradiction on PV custody node architecture, a mathematical/familywise error in the false-PASS multiplicity section, and a critical symbol collision in the per-mode null coverage rule—that must be repaired before binding).

---

## Executive Summary

Draft rev 4 represents outstanding technical progress toward satisfying the outside review's "Fix 1". It decisively resolves the critical blockers that halted rev 3:
1. **The fatal residual stop over-constraint** (agy Defect 1, Grok N3-1) is repaired: eigenvalue cuts are referenced to candidate-specific $\lambda_1(V_F)$, the residual norm threshold (0.1) is restricted to well-determined modes ($\lambda_i \ge 10^{-6}\lambda_1$), an ndf difference is made descriptive rather than terminal, $K_C$ is explicitly exempted, and P0 provides an empirical calibration on the historical regrade pair.
2. **The frame inconsistency in $C_b$** (Grok N3-2b) is eliminated: each bias vector and sample covariance is pulled back to $x_R$ by $D_t^{-1}$ before debiased summation, making the carried quadratic forms exact algebraic identities.
3. **The dilution and circularity of Outcome B** (Grok N3-3) are remedied: spent tunes G18 and AR23 are completely excluded from $C_b$ (leaving only nominal and the three $C_{\text{model}}$ vertices), and the licensed sentence in §7 has been rewritten to claim only one-sided non-undercoverage for the total matrix, stripping the unwarranted claim that the total covariance "covers".
4. **The KI 85 lock** (Grok N3-4b, agy BLOCKING-2) is made airtight across §3.3, §7, and §9.1: without Joseph superseding both sentences of KI 85, no block can be regenerated and Outcome A is legally unobtainable.
5. **The empirical null** (Grok N3-2) is fully specified in §6.1 using carried $G2R$ universe shifts from `data_g2r.npz` and an explicit Gaussian remainder with defined controls and fallbacks.

However, rev 4 cannot yet be declared ready to bind due to three new **MAJOR** defects and two **MINOR** defects:
- **Major Defect 1 (Fidelity/Custody Contradiction):** Section 8 [line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) still lists "- PV's login-node writer with encrypted graded truths;", directly contradicting §3.4 [lines 340–343](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L340-L343) and line 74, which mandate running the writer on an exclusive compute node under `salloc`/`srun`.
- **Major Defect 2 (Multiplicity Logic & Familywise Error):** In §6.4 [line 611](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611), the text quotes 0.85 as the per-truth failure probability at $M_{\text{true}} = 1.25 + 3\cdot\text{SE}$, but then asserts that the familywise false-PASS probability across three candidates is "at most the sum of three negligible terms". At that boundary, the per-truth pass probability is $\approx 15\%$, the joint two-truth pass probability is $\approx 2.3\%$, and the familywise union bound is $\approx 6.8\%$ (not negligible). The "negligible" bound ($\le 5.1 \times 10^{-6}$) holds only at the primary boundary $1.25 + h + 3\cdot\text{SE}$ ([line 609](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L609)).
- **Major Defect 3 (Symbol Collision in Per-Mode Coverage Null):** In §6.1 [line 577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L577), the binomial threshold uses parameter $q_i$ from the null (`Bin(N, q_i)`). In §2 [line 162](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L162), $q_i$ is explicitly defined as the sample mean squared pull $q_i = \text{mean}_s z_{s,i}^2 \approx 1.0$. Using $q_i$ to denote the null probability $P_{\text{null}}(|z_{s,i}| \le 1) \approx 0.6827$ creates a direct symbol collision that would crash or invalidate code implementation.
- **Minor Defects:** Row "A, partial" in §7 [line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644) omits the explicit condition "KI 85 was superseded (§9.1)" present in Row A; and §6.1 [line 568](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L568) defines $k_J$ and $k_J^+$ but omits the explicit operational formula for flagging P-3 "under".

Once these technical fixes are applied, the draft will be ready to bind as soon as the Section 9 prerequisites are met.

---

## 1. Audit of Rev-3 BLOCKING and MAJOR Findings in Rev 4

Every BLOCKING and MAJOR finding from both rev-3 review reports ([inputs/agy-rev3-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/agy-rev3-REPORT.md) and [inputs/grok-rev3-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/grok-rev3-REPORT.md)) was audited against `COVFIX-DECLARATION.md` rev 4.

### 1.1 agy Rev-3 Findings

| Finding ID | Severity in Rev 3 | Description | Status in Rev 4 | Exact Line(s) in Rev 4 & Technical Analysis |
|---|---|---|---|---|
| **Defect 1** | **BLOCKING** | Fatal over-constraint in residual stop: cut referenced to $\lambda_1(K_B)$ dropped mode 205 below $10^{-12}\lambda_1$, triggering an ndf mismatch and residual norm abort at P2. | **CLOSED** | [Lines 50–56, 154–156, 231–233, 489–500](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L50-L56): Cutoff is explicitly referenced to each candidate's own $\lambda_1(V_F(t))$ ([lines 154–156](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L154-L156)). Residual rule checks only well-determined modes with $\lambda_i \ge 10^{-6}\lambda_1(F_A)$ ([line 495](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L495)). An ndf difference alone is printed, not a stop ([line 497](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L497)). $K_C$ is explicitly exempted ([line 499](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L499)). P0 provides empirical calibration against historical $C_T$ vs $C_T + C_{\text{run}}$ ([lines 231–233](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L231-L233)). |
| **Defect 2** | **MAJOR** | ST1 named exception allowed block regeneration but lacked compute allocation, phase, and price under ST6 cumulative ceiling. | **CLOSED** | [Lines 70, 297–298](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L297-L298): Regeneration is explicitly priced at 0.19 node-h per unfold (`universe` 175 unfolds = 33.25 node-h; `stat` 300 replicas = 57 node-h; `c08` 80 unfolds = 15.2 node-h) plus the redraw of affected cells ([line 297](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L297)). Mandates that this price must fit within Joseph's approved total under ST6 or go to Joseph for authorization ([line 298](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L298)). |

*(Note: Prior Rev-2 items tracked in agy-rev3: BLOCKING-1 [iris receipt] remains an OPEN prerequisite parked in §3 [line 206] and §9.3 [line 694]; BLOCKING-2 [KI 85 waiver] is CLOSED in text via §3.3 [lines 300–303] and §9.1 [lines 686–690]; BLOCKING-3 [PG session and passphrase] remains an OPEN prerequisite parked in §4.2 [lines 396–398, 405–407] and §9.3 [lines 695–696]; MAJOR-1, MAJOR-2, and MAJOR-3 remain fully CLOSED).*

---

### 1.2 Grok Rev-3 Findings

| Finding ID | Severity in Rev 3 | Description | Status in Rev 4 | Exact Line(s) in Rev 4 & Technical Analysis |
|---|---|---|---|---|
| **N3-1** | **BLOCKING** | Residual stop rejects $K_B$, and §5.4 extends it to $K_C$ (same as agy Defect 1). | **CLOSED** | [Lines 50–56, 154–156, 231–233, 489–500](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L50-L56): Cut is referenced to $\lambda_1(V_F)$; residual check restricted to well-determined modes $\ge 10^{-6}\lambda_1(F_A)$; ndf shift is descriptive; $K_C$ exempted; calibrated at P0. |
| **N3-2b** | **BLOCKING** | $C_b$ sums absolute biases from multiple truths and is carried as a matrix at $x_R$, mixing coordinate frames in the quadratic forms. | **CLOSED** | [Lines 57, 474–481](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L474-L481): Exact pull-back mapping: $\beta_t = D_t^{-1} \hat{b}_t$, $\Sigma_t = D_t^{-1} S_t D_t^{-1}$, and $C_b = [\sum_{t \in F_{\text{bias}}} (\beta_t \beta_t^T - \Sigma_t/(N_t - 1))]_+$ ([line 477](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L477)). Algebraic identity $\hat{b}_t^T V(t)^{-1} \hat{b}_t = \beta_t^T V^{-1} \beta_t$ holds exactly ([line 481](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L481)). |
| **N3-3** | **BLOCKING** | Outcome B citable sentence claimed two-sided "coverage" for the total covariance while bars were one-sided, and $C_b$ contained spent failure tunes G18/AR23. | **CLOSED** | [Lines 58–63, 474, 482–485, 645](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L474): G18 and AR23 are completely removed from $C_b$ ([lines 482–485](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L482-L485)); $F_{\text{bias}}$ contains only nominal and the three $C_{\text{model}}$ vertices ([line 474](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L474)); row B licensed sentence explicitly licenses "matches (two-sided)" for fluctuation and "does not under-cover (one-sided)" for total, while explicitly barring "'covers' for the total" ([line 645](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L645)). |
| **N3-4b** | **BLOCKING** | KI 85 fallback mishandled: skipping N5 left ST1's `stat`, `c08`, and `universe` rows free to fire and license Outcome A without Joseph superseding both KI 85 sentences. | **CLOSED** | [Lines 64, 300–303, 643, 686–690](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L300-L303): Explicit lock in §3.3: "Unless Joseph supersedes both of KI 85's sentences (§9.1), ST1 records every row it can read and regenerates nothing, and §7 does not license outcome A." ([lines 300–302](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L300-L302)). Section 7 Row A condition explicitly requires "KI 85 was superseded (§9.1)" ([line 643](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L643)). |
| **N3-2** | **MAJOR** | Phase N cited for candidates and ensembles that lack its inputs; null law undefined. | **CLOSED** | [Lines 65–66, 555–575](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L555-L575): The null law is written out explicitly: 38 band shifts $\delta$ taken from G2R `data_g2r.npz` (keys `band__<BAND>`), carried by $D_t$, and composed per `cov2d.draw`; Gaussian remainder $g \sim \mathcal{N}(0, G(t))$ where $G(t) = V(t) - C_\delta(t)$ ([lines 556–562](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L556-L562)). P0 controls verify $C_{\text{univ\_new}}$ reconstruction to $10^{-10}$; fallbacks to $\mathcal{N}(0, V(t))$ if P0 or C-PSD fails ([lines 564–566](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L564-L566)). |
| **N3-4** | **MAJOR** | ST1 exception admitted numeric changes ("inputs") and factors were measured on pre-fix toys. | **CLOSED** | [Lines 67–71, 290–298](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L290-L298): Exception changes code only (never a substituted matrix), names the bug corrected ([lines 291–292](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L291-L292)), bound before drawing ensembles entering $\hat{f}_R$ or $C_b$ (if W1 fires, before W2; if N4 fires, N4 and A1p are redrawn under amended code) ([lines 295–296](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L295-L296)). |
| **N3-5** | **MAJOR** | Custody: sealed ratio was plaintext in login-node `/dev/shm` on shared account; PV scan did not check `/dev/shm`. | **PARTLY CLOSED** | [Lines 74–77, 340–353](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L340-L353): Architecture in §3.4 moved to an exclusive compute node (`salloc --exclusive -N 1` / `srun --exclusive -N 1`), wiping and scanning private `/dev/shm`, `/tmp`, and campaign directory by content ([lines 340–349](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L340-L349)). **However**, §8 [line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) still designates the code target as "PV's login-node writer", introducing a direct internal contradiction (see Defect 1 below). |
| **N3-6** | **MAJOR** | Carry vector $\hat{x}_t$ was unconstructible Asimov; P0 tested COV2D realization vector rather than carry vector. | **CLOSED** | [Lines 79, 140–144, 225–230](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L140-L144): $\hat{x}_t$ is defined as the central unfold of expected pseudo-data rounded to integers (`round(\lambda^+)` via round-half-to-even) ([lines 140–142](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L140-L142)). P0 carries with both COV2D's committed $\hat{x}_T$ and §2's rounded vector (unfolded in W1) and measures the difference ([lines 225–230](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L225-L230)). |
| **N3-7** | **MAJOR** | §6.4 false-PASS boundary was placed at $1.25 + 3\cdot\text{SE}$, claiming near-certain failure, which was wrong. | **PARTLY CLOSED** | [Lines 80, 609–613](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L609-L613): Primary boundary corrected to $1.25 + h + 3\cdot\text{SE}$ (about 1.279), where fail probability is $\ge \Phi(3) \approx 0.9987$ per truth and pass probability over both truths is $\le 1.7 \times 10^{-6}$ ([lines 609–610](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L609-L610)). **However**, [line 611](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611) introduces a new mathematical defect regarding the familywise bound at $1.25 + 3\cdot\text{SE}$ (see Defect 2 below). |
| **N3-8** | **MAJOR** | Band factor was measured in one eigenbasis (carried basis at truth) and applied in another (reference basis at $x_R$). | **CLOSED** | [Lines 81, 454–455, 464–467](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L454-L455): Explicitly stated and disclosed: $F_R(E)$ is measured in $F_A$'s carried eigenbasis at $t_E$; $\hat{f}_R$ is applied to $F_A$'s eigenvalues at $x_R$, and the resulting $V_F$ is carried. Disclosed that $\hat{f}_R$ is a rank-band summary transferred across bases rather than a mode-matched estimate ([lines 466–467](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L466-L467)). |

*(Note: All Rev-3 MINOR findings N3-9 through N3-14, as well as agy Defect 3, Defect 4, and Defect 5, were also verified as CLOSED in rev 4: N3-9 floor raised to $k \ge 25$ [lines 83, 507, 510–513]; N3-10 G18_02 wording fixed [lines 84, 369–370]; N3-11 walltime ceiling set to $1.5\times$ mean price [lines 85, 215–216]; N3-12 price start point 1.33 and no-N5 totals clarified [lines 86, 197–200, 691–692]; N3-13 $\tau_F$ printed beside $F^F$ [lines 87, 548–549]; N3-14 fixed bootstrap basis and v3.2.0 description scope added [lines 88, 157, 373–374, 462]; agy Defect 3 `stat` label fixed [lines 89, 280]; agy Defect 4 plural triggers supported [lines 89, 291]; agy Defect 5 low-side excursion mapped to P-1 [lines 89, 620–623]).*

---

## 2. New Defects in Rev 4 Only

This technical audit examined fidelity, logic, statistical derivations, all numbers in §5.3 and §6.4, prices and budget totals, the written null in §6.1, the residual rule, custody, the ST1 exception, and the KI 85 gate. Items listed as binding prerequisites in Section 9 (the iris receipt, naming the PG session, and generating the director's passphrase) are not re-raised as defects.

### 2.1 Major Defects

#### Defect 1: Text Contradiction Regarding PV Writer Execution Node (MAJOR — Fidelity / Custody)
- **Reference:** Section 8, [Line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) vs. Section 3.4, [Lines 340–343](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L340-L343) and Revision History, [Line 74](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L74).
- **Analysis:**
  In §3.4 [lines 340–341](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L340-L341), the declaration explicitly fixes Grok N3-5 by mandating that:
  > *"1. The writer runs on an exclusive compute node, not a shared login node. The bound PV connect takes an exclusive allocation (`salloc --exclusive -N 1`), and the director's wrapper pipes the passphrase into `srun --exclusive -N 1 <writer>`..."*
  
  This is reiterated in the Rev 4 revision summary at [line 74](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L74) (*"the writer and the readout run on exclusive compute nodes, through `srun` stdin pipes"*).
  
  However, in Section 8 ("Code, tests and audit before any compute"), [line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) still contains the unedited rev-3 code specification:
  > *"- PV's login-node writer with encrypted graded truths;"*
  
  This direct contradiction is dangerous: if an engineer builds according to §8's code manifest, they will construct a login-node writer, directly re-opening the shared `/dev/shm` custody vulnerability identified in Grok N3-5.
- **Concrete Fix:** Edit Section 8 [line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) to read:
  ```markdown
  - PV's exclusive-compute-node writer with encrypted graded truths;
  ```

---

#### Defect 2: Statistical Contradiction and Invalid Familywise Bound at $1.25 + 3\cdot\text{SE}$ (MAJOR — Statistics / Logic)
- **Reference:** Section 6.4, [Lines 609–613](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L609-L613).
- **Analysis:**
  Section 6.4 models the false-PASS probability for the one-sided total bar P-2 ("not under", which fails if $M - h > 1.25$, i.e. sample mean $M > 1.25 + h$, where $h \approx 1.968\cdot\text{SE}$).
  
  At [lines 609–610](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L609-L610), the draft correctly evaluates the boundary $M_{\text{true}} \ge 1.25 + h + 3\cdot\text{SE} \approx 1.279$:
  - The probability of failing P-2 is at least $\Phi(3) \approx 0.9987$ per truth.
  - The probability of falsely passing per truth is $\le 1 - 0.99865 = 0.00135$.
  - Across two independent validation truths, $P(\text{VALIDATED}) \le (0.00135)^2 \approx 1.8 \times 10^{-6}$ (text quotes $1.7 \times 10^{-6}$).
  - Across three candidate choices ($K_A, K_B, K_C$), the union bound is $\le 3 \times 1.7 \times 10^{-6} \approx 5.1 \times 10^{-6}$, which is genuinely "the sum of three negligible terms".
  
  However, [lines 611–612](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611-L612) state:
  > *"Just above the critical value, the probability is lower: at 1.25 + 3·SE (1.267) it is about 0.85 per truth. The result takes the first VALIDATED of at most three candidates (K_A, K_B, K_C), so the familywise chance that such a candidate is VALIDATED is at most the sum of three negligible terms."*
  
  This text contains two severe errors:
  1. **Conflating Fail and Pass Probabilities:** The phrase *"the probability is lower: at 1.25 + 3·SE (1.267) it is about 0.85 per truth"* refers to the probability of **failing** P-2 (rejection power), which dropped from 0.9987 to 0.849. However, the probability of **passing** (falsely accepting) is **higher**, jumping from $0.13\%$ to $1 - 0.849 = 15.1\%$ per truth!
  2. **Mathematically False Familywise Claim:** If the pass probability is $15.1\%$ per truth, the probability that a candidate passes both truths is $(0.151)^2 \approx 0.0228$ ($2.3\%$). For three candidates, the union bound on familywise false-PASS is:
     $$P(\text{at least one candidate VALIDATED}) \le 3 \times 0.0228 \approx 0.0684 \quad (\approx 6.8\%)$$
     A $6.8\%$ chance of false validation is **not** "the sum of three negligible terms". The author erroneously appended the "negligible" conclusion (which belonged to the $1.25 + h + 3\cdot\text{SE}$ boundary) to the $1.25 + 3\cdot\text{SE}$ discussion.
- **Concrete Fix:** Revise [lines 611–613](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611-L613) to cleanly separate the two boundaries:
  ```markdown
  - A candidate with M_true ≥ 1.25 + h + 3·SE (about 1.279) fails "not under" with probability at least Φ(3) ≈ 0.9987 per truth, so it is VALIDATED with probability at most about 1.7e-6 over both truths. The result takes the first VALIDATED of at most three candidates (K_A, K_B, K_C), so the familywise chance that such a candidate is VALIDATED is at most the sum of three negligible terms (about 5.1e-6).
  - Closer to the critical value 1.25 + h, rejection power is lower: at 1.25 + 3·SE (1.267, about 1·SE above critical), the probability of failing "not under" is about 0.85 per truth, giving a pass probability of about 0.15 per truth and 0.023 over two truths; the familywise chance of false validation is bounded by about 0.07.
  ```

---

#### Defect 3: Critical Symbol Collision on $q_i$ in §6.1 Per-Mode Coverage Rule (MAJOR — Logic / Statistics)
- **Reference:** Section 2, [Line 162](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L162) vs. Section 6.1, [Line 577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L577).
- **Analysis:**
  In Section 2 ("Notation"), [lines 160–163](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L160-L163), $q_i$ is explicitly defined as the sample mean squared normalized pull:
  $$q_i = \text{mean}_s z_{s,i}^2 = m_i^2 + v_i$$
  For a calibrated mode, $\mathbb{E}[q_i] = 1.0$.
  
  In Section 6.1 ("Per-mode coverage"), [lines 576–577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L576-L577) define the binomial cut for mode coverage flags:
  > *"Per-mode coverage: the count #{s : |z_{s,i}| ≤ 1}, flagged 'under' at ≤ k_c, the largest k with P(Bin(N, q_i) ≤ k) < 0.025/ndf (q_i from the same null), and 'over' symmetrically."*
  
  Here, the parameter of $\text{Bin}(N, \cdot)$ is intended to be the null probability that a toy falls in the $1\sigma$ interval, $p_i = P_{\text{null}}(|z_{s,i}| \le 1) \approx 0.6827$ (analogous to the scalar joint probability $q$ defined at [line 568](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L568)).
  
  Reusing the symbol $q_i$ creates an immediate mathematical collision: if an implementer passes §2's mode pull second moment $q_i$ (which is $\approx 1.0$ or $> 1.0$) into `scipy.stats.binom`, the distribution either crashes (for $q_i > 1$) or trivializes to a point mass at $N$.
- **Concrete Fix:** Rename the per-mode interval success probability in [line 577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L577) from $q_i$ to $p_i$ (or $q_{\text{mode}, i}$):
  ```markdown
  - **Per-mode coverage:** the count #{s : |z_{s,i}| ≤ 1}, flagged "under" at ≤ k_c, the largest k with P(Bin(N, p_i) ≤ k) < 0.025/ndf (with p_i = P_null(|z_{s,i}| ≤ 1) simulated from the same null replicates), and "over" symmetrically. The flags are reported per band.
  ```

---

### 2.2 Minor Defects

#### Defect 4: Section 7 Row "A, partial" Omission of Explicit KI 85 Prerequisite (MINOR — Logic / Gating)
- **Reference:** Section 7, [Line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644) vs. [Line 643](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L643) and Section 3.3, [Lines 300–302](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L300-L302).
- **Analysis:**
  Section 3.3 [lines 300–302](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L300-L302) states:
  > *"Unless Joseph supersedes both of KI 85's sentences (§9.1), ST1 records every row it can read and regenerates nothing, and §7 does not license outcome A."*
  
  In the §7 outcome table, row **A** ([line 643](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L643)) explicitly lists:
  > *"ST1 fired, KI 85 was superseded (§9.1), its named exception was bound, and K_A is VALIDATED"*
  
<!-- absence-ok: verbatim third-party read report -->
  However, row **A, partial** ([line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644)) lists only:
  > *"ST1 fired and was fixed, but K_A is not VALIDATED"*
  
<!-- absence-ok: verbatim third-party read report -->
  While "fixed" implies regeneration under the named exception (which itself requires KI 85 to be superseded), omitting the explicit phrase *"KI 85 was superseded (§9.1)"* from row "A, partial" leaves a slight loophole where an unauthorized code edit could attempt to claim "A, partial" without Joseph's formal decision.
- **Concrete Fix:** Update the condition column of row "A, partial" in §7 [line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644) to:
  ```markdown
  | **A, partial** | ST1 fired, KI 85 was superseded (§9.1), its named exception was bound and fixed, but K_A is not VALIDATED | ...
  ```

---

#### Defect 5: Missing Operational Formula for Joint Rule P-3 Under-Flag (MINOR — Statistics / Fidelity)
- **Reference:** Section 6.1, [Lines 568–570](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L568-L570) and Section 6.2, [Line 586](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L586).
- **Analysis:**
  Section 6.1 [lines 568–570](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L568-L570) defines the in-region probability $q$ and thresholds $k_J$ and $k_J^+$:
  > *"20,000 null replicates at seed 9_992_000 give q, the in-region probability, and k_J and k_J⁺: the largest k with P(Bin(N, q) ≤ k) < 0.025, and the smallest with P(Bin(N, q) ≥ k) < 0.025."*
  
  And Section 6.2 [line 586](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L586) states bar P-3:
  > *"P-3: the draw-matched joint rule does not flag 'under';"*
  
  Unlike per-mode coverage (which explicitly defines the test statistic #{s : |z_{s,i}| \le 1} and states that it is flagged "under" at $\le k_c$), §6.1 never explicitly writes down the sample statistic $K_J = \#\{s : \chi^2_s \le F_{\chi^2(\text{ndf})}^{-1}(0.6827)\}$ or states that P-3 flags "under" when $K_J \le k_J$. While obvious from statistical context, pre-registration rigor requires the operational definition to be explicit.
- **Concrete Fix:** Add an explicit operational sentence in §6.1 [line 570](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L570):
  ```markdown
  The joint reading is the count K_J = #{s : χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827)}; the rule flags "under" if K_J ≤ k_J and "over" if K_J ≥ k_J⁺.
  ```

---

### 2.3 Detailed Audit of Rev-4 Sections and Numbers

#### 1. Verification of Every Number in Section 5.3 ($K_C$)
- **Smallest admission ensemble ($A1p, N = 100, k = 25$):**
  - $\text{SE} = \sqrt{2 / (100 \times 25)} = \sqrt{0.0008} \approx 0.02828$ (Text: $0.028$). **Exact match.**
  - $t_{0.975, 99} = 1.9842 \implies h = 1.9842 \times 0.02828 \approx 0.05612$ (Text: $0.056$). **Exact match.**
  - Low edge: $0.8 + h = 0.85612$. Distance from 1.0: $(1.0 - 0.85612) / 0.02828 = 5.087\sigma$ (Text: $5.1\sigma$). **Exact match.**
  - High edge: $1.25 - h = 1.19388$. Distance from 1.0: $(1.19388 - 1.0) / 0.02828 = 6.855\sigma$ (Text: $6.9\sigma$). **Exact match.**
- **PV validation ensemble ($N = 300, k = 25$):**
  - $\text{SE} = \sqrt{2 / (300 \times 25)} = \sqrt{2 / 7500} \approx 0.01633$ (Text: $0.016$). **Exact match.**
  - $t_{0.975, 299} = 1.9679 \implies h = 1.9679 \times 0.01633 \approx 0.03214$ (Text: $0.032$). **Exact match.**
  - Low edge: $0.8 + h = 0.83214$. Distance from 1.0: $(1.0 - 0.83214) / 0.01633 = 10.279\sigma$ (Text: $10.3\sigma$). **Exact match.**
  - High edge: $1.25 - h = 1.21786$. Distance from 1.0: $(1.21786 - 1.0) / 0.01633 = 13.341\sigma$ (Text: $13.3\sigma$). **Exact match.**
- **Conclusion:** Every number in §5.3 is verified to full statistical precision.

#### 2. Verification of Every Number in Section 6.4 (Multiplicity)
- $\text{ndf} = 204, N = 300 \implies \text{SE}(M) = \sqrt{2 / (300 \times 204)} = \sqrt{2 / 61200} \approx 0.005715$ (Text: $0.0057$). **Exact match.**
- $h = t_{0.975, 299} \times 0.005715 = 1.9679 \times 0.005715 \approx 0.01125$ (Text: $0.011$). **Exact match.**
- Critical threshold for sample mean $M$: $1.25 + h \approx 1.26125$.
- Worked boundary $1.25 + h + 3\cdot\text{SE} = 1.26125 + 3(0.005715) \approx 1.2784$ (Text: $1.279$). **Exact match.**
- Failure probability per truth at $1.2784$: $\Phi(3) \approx 0.99865$ (Text: $\approx 0.9987$). **Exact match.**
- Joint two-truth pass probability: $(1 - 0.99865)^2 = (0.00135)^2 \approx 1.82 \times 10^{-6}$ (Text: $1.7 \times 10^{-6}$). **Matches within rounding.**
- Boundary $1.25 + 3\cdot\text{SE} = 1.25 + 3(0.005715) \approx 1.26715$ (Text: $1.267$). **Exact match.**
- At $1.26715$, difference from critical value is $(1.26715 - 1.26125)/\text{SE} = 1.032\sigma$. Rejection probability: $\Phi(1.032) \approx 0.849$ (Text: $0.85$). **Exact match.** *(See Defect 2 for the error in interpreting this value).*
- P-3 tail contribution: $\le 0.025$. Linearity bound on expected false under-flags for P-4: $\le 0.025$. Per-truth failure bound: $0.025 + 0.025 = 0.05$. Union bound over two truths: $0.05 + 0.05 = 0.10$. Both are below the director's 20% mark. **Exact match.**
- At $k = 25, N = 300$, covers-label edge distances: high-side $13.3\sigma$, low-side $10.3\sigma$. **Exact match.**

#### 3. Verification of Prices, Phase Allocations, and Totals
- Unit price: $0.19$ node-h per unfold (based on COV2D historical $112.74 / 600 = 0.1879$).
- **P1 Wave 1:**
  - $N1$: $200 \text{ full} / 150 \text{ lean} \times 0.19 = 38.0 / 28.5$ node-h.
  - $N2$: $200 / 150 \times 0.19 = 38.0 / 28.5$ node-h.
  - $N5$: $400 / 300 \times 0.19 = 76.0 / 57.0$ node-h.
  - $N3$: $50 / 50 \times 0.19 = 9.5 / 9.5$ node-h.
  - Central unfolds: 3 unfolds (nominal, G18, AR23) $\times 0.19 = 0.57$ node-h.
  - **W1 Total:** Full $= 38 + 38 + 76 + 9.5 + 0.57 = 162.07$; Lean $= 28.5 + 28.5 + 57 + 9.5 + 0.57 = 124.07$. (Text: $162.07 / 124.07$). **Exact match.**
- **P1 Wave 2:**
  - $N4$: $200 / 150 \times 0.19 = 38.0 / 28.5$ node-h.
  - $A1f$: $3 \times 60 = 180 \text{ full} / 0 \text{ lean} \times 0.19 = 34.2 / 0.0$ node-h.
  - $A1p$: $3 \times 100 = 300 \times 0.19 = 57.0 / 57.0$ node-h.
  - Central unfolds: 3 unfolds (the three vertices) $\times 0.19 = 0.57$ node-h.
  - **W2 Total:** Full $= 38 + 34.2 + 57 + 0.57 = 129.77$; Lean $= 28.5 + 0 + 57 + 0.57 = 86.07$. (Text: $129.77 / 86.07$). **Exact match.**
- **P1 Sum:** Full $= 162.07 + 129.77 = 291.84$; Lean $= 124.07 + 86.07 = 210.14$. (Text: $291.84 / 210.14$). Cap: $330 / 240$. **Exact match.**
- **PV Phase:**
  - 600 validation toys $+ 2$ central unfolds $= 602 \times 0.19 = 114.38$ node-h.
  - Plus estimated $1.0$ node-h for exclusive-node writer and readout $= 115.38$ node-h. Cap: $135.0$. **Exact match.**
- **PG Phase:** $1.33$ to $2.0$ node-h. Cap: $3.0$. **Exact match.**
- **Campaign Totals:**
  - **Full (with N5):** Low $= 1.33 + 291.84 + 115.38 = 408.55$; High $= 2.0 + 291.84 + 115.38 = 409.22$. (Text: $408.55\text{–}409.22$). **Exact match.**
  - **Lean (with N5):** Low $= 1.33 + 210.14 + 115.38 = 326.85$; High $= 2.0 + 210.14 + 115.38 = 327.52$. (Text: $326.85\text{–}327.52$). **Exact match.**
  - **Full (without N5):** Subtract $76.0 \implies 332.55\text{–}333.22$. (Text: $332.55\text{–}333.22$). **Exact match.**
  - **Lean (without N5):** Subtract $57.0 \implies 269.85\text{–}270.52$. (Text: $269.85\text{–}270.52$). **Exact match.**
  - **Caps sum:** Full $= 3.0 + 330 + 135 = 468$; Lean $= 3.0 + 240 + 135 = 378$. (Text: $468 / 378$). **Exact match.**
  - Iris balance: $725.6$ node-h; half-balance: $362.8$ node-h. Only full with N5 exceeds half-balance ([lines 205–211, 691–692](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L205-L211)). **Exact match.**

#### 4. The Written Null in §6.1
- Band vectors $\delta$ read from G2R's `data_g2r.npz` (keys `band__<BAND>`). Verified against `inputs/data_g2r-keys.txt`:
  - 38 bands present: `Flux` ($100 \times 205$), `2p2h` ($3 \times 205$), and 36 others ($2 \times 205$ each).
  - SHA256 `3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b` matches character for character.
- Band carrying and composition: shifted by $D_t$, composed per `cov2d.draw`.
- Gaussian remainder: $G(t) = V(t) - C_\delta(t)$. Since $V$ contains $C_{\text{univ\_new}}$ plus non-negative blocks (lateral, norm, stat, c08, $C_{PL}$, and $C_b$), $G(t)$ is positive semi-definite. P0 controls verify $C_{\text{univ\_new}}$ reconstruction to $10^{-10}$, and C-PSD failure triggers the pre-committed fallback to $\mathcal{N}(0, V(t))$ with mandatory logging.
- Simulation: 20,000 null replicates at pre-committed seed `9_992_000` (disjoint from all other seeds).
- False-FAIL threshold $\le 0.20$ evaluated before unfolding.

#### 5. The Residual Rule in §5.2 and §3.1
- Truncation cutoff: referenced to candidate-specific $\lambda_1(V_F(t))$, preventing $C_b$'s positive semi-definite eigenvalues from shifting the kept truncation threshold.
- Scope: restricted strictly to well-determined modes $\lambda_i \ge 10^{-6}\lambda_1(F_A)$.
- Threshold: component norm $> 0.1$ outside $K_B$'s span triggers inadmissibility.
- Ndf changes: recorded as descriptive diagnostics, never a stop.
- Calibration: P0 tests the exact rule against historical $C_T$ vs. $C_T + C_{\text{run}}$ at G18 and AR23. If the rule trips on that pair, P0 halts for director review.
- Exemptions: explicitly does not apply to $K_C$.

#### 6. Custody Architecture in §3.4 and §4.2
- Exclusive allocation: $salloc --exclusive -N 1$ and $srun --exclusive -N 1$ isolate writer and readout from shared login-node `/dev/shm`.
- Passphrase delivery: piped via stdin from director's wrapper (`--passphrase-fd 0`), never in environment or files.
- Disk encryption: graded truths are AES256-encrypted before touching disk. Pseudo-data on disk are Poisson integer counts (unfolded without secret keys).
- Cleanup and scan: node `/dev/shm` and `/tmp` are wiped and content-scanned against sealed plaintext hashes before release.
- Spent-once guarantee: atomic lock file and output JSON existence checks prevent re-execution.

#### 7. The ST1 Exception and KI 85 Gating
- Scope of amendment: code-only (never numeric matrix substitution); must name specific bug.
- Frozen parameters: bars, seeds, validation family, factor rules, $C_b$ rule, $k$ rule, and §7 order remain permanently immutable.
- Timing: bound before any ensemble entering $\hat{f}_R$ or $C_b$ is drawn; requires redraw of affected cells.
- Cumulative budget: regeneration and redraws must fit inside Joseph's approved total under ST6 or seek explicit authorization.
- Gating: without Joseph superseding both sentences of KI 85 (§9.1), ST1 records all rows but regenerates nothing, and Outcome A is legally prohibited.

---

## 3. Evaluation of Outcome B with G18 and AR23 Excluded from $C_b$

The outside review's Fix 1 requires separating bias from fluctuation:
$$\mathbb{E}[(\hat{\sigma} - \sigma)(\hat{\sigma} - \sigma)^T] = C_{\text{fluct}} + b b^T$$
and permits Outcome B if:
> *"(B) the covariance holds for a stated model class, with the truth-model bias quantified separately;"*

In Rev 3, $C_b$ summed outer products from six truths, including G18 and AR23. Because G18 and AR23 were the very tunes where the original covariance under-covered—and because their biases were massive ($T2A$ mean error parts against $C_T$ were $13.61$ and $20.97$ per ndf)—including them directly inside $C_b$ created an enormous envelope tailored to the historical failure. Passing a one-sided total bar with those spent biases inside $C_b$ was mathematically trivial and scientifically circular.

### 3.1 Does Outcome B Now Certify Something Meaningful?
**Yes.** With G18 and AR23 completely excluded, Outcome B achieves genuine, falsifiable scientific certification:
1. **Strict Model-Class Separation:** $C_b$ is constructed exclusively from non-spent build truths: nominal and the three alternative-physics vertices of $C_{\text{model}}$ (`genie_mec`, `nuwro`, `gibuu`). Its rank is at most 4 ([line 479](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L479)), forming a bounded low-rank cone in cross-section space representing known generator modeling spread.
2. **True Out-of-Sample Falsifiability:** The validation truths ($G21\_11b$ and $G18\_02b$) are held-out, sealed, and generated with distinct physical models (e.g. SuSAv2 CCQE, BS resonance/coherent pion production). Neither truth enters $\hat{f}_R$ or $C_b$. If the held-out validation tunes exhibit a bias pointing in an un-spanned direction or of a magnitude exceeding the $C_{\text{model}}$ vertices, the candidate **will fail** the total bar P-2, the joint rule P-3, or per-mode coverage P-4. Passing is therefore an empirical discovery, not a mathematical tautology.
3. **Rigorous Fluctuation Validation:** Crucially, candidate $K_B$ cannot pass by inflating $C_b$. Bar P-1 requires the fluctuation block $V_F$ (scaled by $\hat{f}_R$) to match the held-out scatter **two-sided** ($[0.8, 1.25]$) across the full spectrum and in every rank band. Over-inflation of fluctuation triggers the fatal `INFLATED` verdict ([line 597](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L597)).
4. **Transparent Residual Bias Accounting:** The held-out biases are explicitly projected against $C_b$ ($\beta_u^T C_b^+ \beta_u$ and the fraction of norm outside $C_b$'s span) and published directly in the result sentence ([lines 552–553, 645](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L552-L553)).

### 3.2 Does Its Licensed Sentence Match Its Bars Exactly?
**Yes.** In Rev 3, Grok correctly flagged that row B licensed the phrase "the covariance covers", which claimed two-sided coverage for the total matrix when only a one-sided non-undercoverage bar was enforced.

In Rev 4, Section 7 Row B ([line 645](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L645)) has been completely aligned with the underlying bars:
- **Fluctuation Bar (P-1):** Requires $F^F$ to read "covers" (two-sided $[0.8, 1.25]$) and no band to read "under" or "over".  
  *Licensed Sentence:* *"The fluctuation block, measured on nominal and alternative-truth ensembles, matches the held-out scatter at two GENIE v3 tunes (two-sided)."* $\implies$ **Exact match.**
- **Total Bar (P-2, P-3, P-4):** Requires $M$ to read "not under" (one-sided), no band to read "under", and joint/per-mode rules not to flag "under".  
  *Licensed Sentence:* *"With a truth-model bias block built in-sample from nominal and the three C_model vertices and reported separately, the total does not under-cover there (one-sided)."* $\implies$ **Exact match.**
- **Bias Quantification:** Requires reporting projections $\beta_u^T C_b^+ \beta_u$ and orthogonal fractions.  
  *Licensed Sentence:* *"The held-out biases against that block are β_uᵀC_b⁺β_u = <value>, with <fraction> outside its span." The band factors f̂_R and C_b's rank and trace are printed with it.* $\implies$ **Exact match.**
- **Negative Licensing Scope:** The "Not licensed" column explicitly forbids claiming:
  > *"'covers' for the total; coverage outside the GENIE v3 family; a cause of the bias; that the bias block is tight"* $\implies$ **Airtight protection against over-claiming.**
- **Mandatory In-Sample Disclosure:** Section 7 [lines 635–638](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L635-L638) mandates that every B sentence explicitly disclose that the blocks were built in-sample on $F_{\text{bias}}$ and validated out-of-sample on the two sealed tunes.

---

## 4. Readiness to Bind and Required Changes

### 4.1 Is the Draft Ready to Bind?
**NO.** The draft cannot be bound until the three MAJOR defects (Defects 1, 2, and 3) and the two MINOR defects (Defects 4 and 5) are corrected. 

Once those surgical edits are made to the text, and once the binding prerequisites listed in Section 9 (the committed iris receipt, naming the fresh PG session, and piping the director's passphrase) are formally met, the declaration will be fully ready to bind.

### 4.2 Required Changes Checklist

To achieve a GO verdict for binding, the following exact text modifications must be executed:

1. **Fix Defect 1 (PV Writer Execution Node Contradiction):**
   - **Target:** Section 8, [Line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675).
   - **Edit:** Replace:
     ```markdown
     - PV's login-node writer with encrypted graded truths;
     ```
     with:
     ```markdown
     - PV's exclusive-compute-node writer with encrypted graded truths;
     ```

2. **Fix Defect 2 (False-PASS Familywise Error in §6.4):**
   - **Target:** Section 6.4, [Lines 611–613](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611-L613).
   - **Edit:** Replace lines 609–613 with:
     ```markdown
     - A candidate with M_true ≥ 1.25 + h + 3·SE (about 1.279) fails "not under" with probability at least Φ(3) ≈ 0.9987 per truth, so it is VALIDATED with probability at most about 1.7e-6 over both truths. The result takes the first VALIDATED of at most three candidates (K_A, K_B, K_C), so the familywise chance that such a candidate is VALIDATED is at most the sum of three negligible terms (about 5.1e-6).
     - Closer to the critical value 1.25 + h, rejection power is lower: at 1.25 + 3·SE (1.267, about 1·SE above critical), the probability of failing "not under" is about 0.85 per truth, giving a pass probability of about 0.15 per truth and 0.023 over two truths; the familywise chance of false validation is bounded by about 0.07.
     ```

3. **Fix Defect 3 (Symbol Collision on $q_i$ in §6.1):**
   - **Target:** Section 6.1, [Line 577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L577).
   - **Edit:** Replace line 576–577 with:
     ```markdown
     - **Per-mode coverage:** the count #{s : |z_{s,i}| ≤ 1}, flagged "under" at ≤ k_c, the largest k with P(Bin(N, p_i) ≤ k) < 0.025/ndf (with p_i = P_null(|z_{s,i}| ≤ 1) simulated from the same null replicates), and "over" symmetrically. The flags are reported per band.
     ```

<!-- absence-ok: verbatim third-party read report -->
4. **Fix Defect 4 (Explicit KI 85 Prerequisite in Row "A, partial"):**
   - **Target:** Section 7, [Line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644).
   - **Edit:** Replace the condition column of row `A, partial`:
     ```markdown
     | **A, partial** | ST1 fired, KI 85 was superseded (§9.1), its named exception was bound and fixed, but K_A is not VALIDATED | "A construction error in <block> was found and corrected; the corrected covariance still does not cover held-out tunes." Then B and C are read. | "fixed" in the coverage sense |
     ```

5. **Fix Defect 5 (Explicit Flag Formula for Joint Rule P-3):**
   - **Target:** Section 6.1, [Line 570](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L570).
   - **Edit:** Append after line 570:
     ```markdown
     The joint reading is the count K_J = #{s : χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827)}; the rule flags "under" if K_J ≤ k_J and "over" if K_J ≥ k_J⁺.
     ```

---

## 5. Summary Table of Defect Classifications

| Defect ID | Severity | Category | Description | Exact Line(s) |
|---|---|---|---|---|
| **Defect 1** | **MAJOR** | Fidelity / Custody | §8 lists login-node writer, contradicting §3.4's mandate for an exclusive compute node. | [Line 675](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L675) |
| **Defect 2** | **MAJOR** | Statistics / Logic | Conflates fail/pass probabilities at $1.25 + 3\cdot\text{SE}$ and claims familywise false-PASS is negligible ($\approx 7\%$). | [Lines 611–613](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L611-L613) |
| **Defect 3** | **MAJOR** | Statistics / Code | Symbol collision: per-mode null interval probability named $q_i$, colliding with §2's mode pull second moment. | [Line 577](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L577) |
| **Defect 4** | **MINOR** | Logic / Gating | Row "A, partial" omits explicit condition that KI 85 must be superseded. | [Line 644](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L644) |
| **Defect 5** | **MINOR** | Statistics / Fidelity | Missing explicit test statistic and flag formula for joint coverage rule P-3. | [Lines 568–570](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix4/inputs/COVFIX-DECLARATION.md#L568-L570) |

---
*Report completed strictly in accordance with read-only review instructions.*
