<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
# Review of COVFIX Pre-Registration Declaration (Draft Rev 10)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** Antigravity (agy) — Confirming Technical Read  
**Target:** [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md) (Draft Rev 10, 2026-11-23)  
**Baseline Documents:**
- [rev9-to-rev10.diff](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/rev9-to-rev10.diff)
- [agy-rev9-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/agy-rev9-REPORT.md)
- [codex2-rev9-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/codex2-rev9-REPORT.md)
- [DECISION-20261123.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/DECISION-20261123.md)  
**Report File:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/report.md`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Executive Summary

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative binding prerequisites (§9 item 3: committed iris receipt, fresh PG session, and director's passphrase piping wrapper), **Draft Rev 10 is NO-GO for binding** until four targeted textual defects (one **MAJOR** numerical contradiction in §9.2 and three **MINOR** drafting/notation cleanups) are resolved.

<!-- absence-ok: verbatim third-party read report -->
Draft Rev 10 achieves full structural, algorithmic, and statistical convergence. It successfully **CLOSES all findings from both Rev 9 reports**:
1. **$K_B$ Reference Fallback:** [Lines 904–918](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L904-L918) explicitly define $K_{\mathrm{ref}} = F_A + C_{\mathrm{model\_abs}}(x_R)$ (evaluating to $K_0$ when $K_A$ is omitted). Both the cut diagnostic and the residual rule reference $K_{\mathrm{ref}}$ and its well-determined modes $U_{\mathrm{ref,well}}$, rendering every branch (including unfunded PX) fully executable.
2. **Consistent Reference Covariance ($V_+$):** The sole Gaussian reference law uses $V_+$ ([lines 992–994](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L992-L994)), expected spread $F_{\exp}$ is formulated directly from $V_+$ ([lines 948–951](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L948-L951)), non-positive fit denominators refuse $K_B$ construction ([lines 952–953](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L952-L953)), zero $V_+$ is caught prior to norm division ([lines 999–1000](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L999-L1000)), and stress scenario D2 uses $V_+$ ([line 1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015)).
3. **Execution Chain Integrity:** Compute jobs hash the actual input, complete output, and the launched executable and resolved argument vector ([lines 683–686](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L683-L686)); readout verifies these against the freeze's expected invocation and rehashes consumed outputs ([lines 686–687](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L686-L687)); and failed attempts are excluded by the ledger so only accepted attempts count ([lines 688–689](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L688-L689)).
4. **Targeted Refusal Scoping:** Refusals are strictly scoped to the quantities they affect ([lines 1032–1040](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1032-L1040)). A reference failure refuses reference-dependent quantities ($\tilde{F}$, bands, flags) while leaving total covariance readings ($M$, total bands) valid. Valid total deficits trigger `FAILS` first ([lines 1048](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1048)) and activate the baseline challenge ([line 1080](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1080)).
5. **Operational Safeguards:** Synthetic-seal test advance reservation of 2.0 node-h is explicitly included under the PV cap ([lines 385, 602–604](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L385)); exact eigenspace ties are canonicalized via cell-axis Gram–Schmidt ([lines 862–864](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L862-L864)); all pre-grade terminal stops route to "none, PV ungraded" ([lines 1085–1087, 1099](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1085-L1087)); and verified grades are persisted before running descriptive stress runs ([lines 697–699](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L697-L699)).

<!-- absence-ok: verbatim third-party read report -->
**Why NO-GO remains necessary:**  
A pre-registration declaration cannot be bound with internal contradictions or undefined mathematical symbols in text that is permanently locked against post-binding amendment (§5–§7):
- **MAJOR:** In §9.2 [line 1148](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1148), the text quotes Joseph's size decision with a stale parenthetical `(408.6–409.2)`, directly contradicting the updated Section 3 total price table of `410.55–411.22` ([line 387](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L387)) and the binding ceiling of `409.22` node-h ([line 414](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L414)).
- **MINOR:** In §6.1 [line 954](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L954), the text requires that `u, u_R and F_exp are printed`, and in §5.2 [line 875](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L875) references `§6.1's u, u_R and F_exp`. However, the definition of the scalars $u$ and $u_R$ was removed when $F_{\exp}$ was reformulated directly in terms of $V_+$, leaving $u$ and $u_R$ undefined in §6.1.
- **MINOR:** In §6.2 [line 1012](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1012), the stress deficit parameter still writes `a = tr(V⁺V_drawn)/ndf` instead of `V₊`, inconsistent with [lines 993–994](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L993-L994) and [line 1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015).
- **MINOR:** In §5 [line 820](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L820), the deletion of "or k" left a grammatical omission (`which any P2 bar, choice reads`).

<!-- absence-ok: verbatim third-party read report -->
Applying these four drop-in surgical text edits will immediately render **Draft Rev 10.1 GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of All Findings from Both Rev 9 Reports

<!-- absence-ok: verbatim third-party read report -->
### 1.1 Findings from agy-rev9-REPORT.md

<!-- absence-ok: verbatim third-party read report -->
| Finding | Prior Severity | Status in Rev 10 | Exact Rev 10 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **Defect 2.1: Inexecutable Reference for Cut Diagnostic & Residual Rule when $K_A$ is Omitted** | **MAJOR** | **CLOSED** | [Lines 904–918](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L904-L918) | **Fully resolved.** Lines 904–906 define the reference total as $K_{\mathrm{ref}} = F_A + C_{\mathrm{model\_abs}}(x_R)$, which equals $K_0$ when $K_A$ is omitted. Lines 907–910 specify cut diagnostic against $K_{\mathrm{ref}}$'s kept sets referenced to its own $\lambda_1(F_A)$ vs $V_F$ for $K_B$. Lines 912–918 define the residual rule against $K_{\mathrm{ref}}$'s well-determined modes $U_{\mathrm{ref,well}}$. $K_B$'s admission check at P2 ([line 929](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L929)) is fully executable on every branch. |
| **Defect 2.2: Notation Discrepancy in Scenario D2 Formula ($V_{\mathrm{drawn}}$ vs $V_+$)** | **MINOR** | **CLOSED** | [Line 1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015) | **Fully resolved.** Line 1015 replaces $V_{\mathrm{drawn}}$ with $V_+$: `where a_R = (1/ndf_R) Σ_{i∈R} u_iᵀ V₊ u_i / λ_i; defined if a_R > 0;`, aligning D2 with the sampled reference covariance defined in line 993. |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 1.2 Findings from codex2-rev9-REPORT.md

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.1 Codex Rev 9 Minimum Changes Before Binding (§1)

<!-- absence-ok: verbatim third-party read report -->
| Item | Prior Severity | Status in Rev 10 | Exact Rev 10 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **1. Finish the $K_B$ fallback** | **BLOCKING** | **CLOSED** | [Lines 904–918](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L904-L918) | **Fully resolved.** $F_A$ is used as the reference fluctuation block, $K_{\mathrm{ref}} = F_A + C_{\mathrm{model\_abs}}(x_R)$ is used as reference total, and cut spans are explicitly identified ($F_A$ for $K_{\mathrm{ref}}$, $V_F$ for $K_B$). The directed residual checks $U_{\mathrm{ref,well}}$. Unfunded branch is executable and accepted correction is preserved if $K_A$ fails P2. |
| **2. Use the sampled covariance consistently** | **BLOCKING** | **CLOSED** | [Lines 948–954](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L948-L954), [992–1005](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L992-L1005), [1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015) | **Fully resolved.** The sole Gaussian law is defined with $V_+$ ([lines 992–994](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L992-L994)). $F_{\exp}$ computes $((N-1)/N) \frac{1}{\mathrm{ndf}_F} \sum_i u_i^\top V_+ u_i / \lambda_i^F$ (and per band). Unusable fit denominator refuses $K_B$ construction ([line 953](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L953)). Zero $V_+$ refuses reference-dependent readings before norm division ([line 999](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L999)). D2 uses $V_+$ ([line 1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015)). |
| **3. Verify the invocation that produced each unfold** | **BLOCKING** | **CLOSED** | [Lines 683–692](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L683-L692) | **Fully resolved.** Unfold jobs record the sha256 of actual input, complete output, and actual launched invocation (executable sha256 + resolved argv). Readout checks against authenticated writer manifest and freeze's expected invocation, and rehashes output products. Applies identically to central unfolds. |
| **4. Make refusal apply to the readings it affects** | **BLOCKING** | **CLOSED** | [Lines 1004–1005](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1004-L1005), [1032–1040](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1032-L1040), [1048](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1048) | **Fully resolved.** Per truth: carry failure refuses all; reference failure refuses $\tilde{F}$, bands, and flags, but leaves total covariance readings ($M$, total bands) valid; SE or $F_{\exp}$ non-positivity refuses only its own reading. `FAILS` takes precedence over `REFUSED` ([line 1048](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1048)), ensuring an observed total deficit triggers the baseline challenge ([line 1080](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1080)). |

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.2 Codex Rev 9 Regressions and Nonblocking Fixes (§3)

<!-- absence-ok: verbatim third-party read report -->
| Item | Prior Severity | Status in Rev 10 | Exact Rev 10 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **5. Give the synthetic test an advance reservation** | **MAJOR** | **CLOSED** | [Lines 385](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L385), [602–604](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L602-L604), [703–705](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L703-L705) | **Fully resolved.** PV table row explicitly includes `the synthetic-seal test (a fixed 2.0 reservation, §3.3)`, raising PV price to 117.38 (under 135 cap). Line 602 binds fixed 2.0 advance reservation. Lines 603–604 and 704–705 specify that test measurements reprice the production writer and readout before PV submission. |
| **6. Count accepted attempts in the chain** | **MAJOR** | **CLOSED** | [Lines 601](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L601), [688–689](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L688-L689) | **Fully resolved.** Lines 688–689 explicitly instruct: `The ledger marks a failed attempt's records as excluded, and exactly one verified product per expected ID must come from an accepted attempt.` Line 601 guarantees one accepted product per ID. |
| **7. Fix the basis for exact eigenvalue ties** | **MAJOR** | **CLOSED** | [Lines 862–864](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L862-L864) | **Fully resolved.** Lines 862–864 specify a canonical basis for degenerate clusters: ordered cell axes $e_1, e_2, \dots$ are projected into the eigenspace and orthonormalized by Gram–Schmidt in that order (skipping null projections), eliminating solver-dependent eigenspace rotations. |
| **8. Route every terminal stop before complete PV grades** | **MAJOR** | **CLOSED** | [Lines 1085–1087](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1085-L1087), [1099](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1099) | **Fully resolved.** Ungraded condition explicitly covers every stop before complete grades: ST2 leaving no eligible candidate, integrity failures, and ST5 terminal incompleteness after retries. Outcome row is renamed `none, PV ungraded`. |
| **9. Finalize grades before descriptive stress work** | **MAJOR** | **CLOSED** | [Lines 697–699](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L697-L699) | **Fully resolved.** Lines 697–699 dictate that the readout decrypts graded truths, executes controls, grades, and persists verified grades. Only then does it run descriptive stress runs, reporting failed scenarios as omitted. |
| **10. Delete stale wording** | **MINOR** | **CLOSED** | [Lines 820](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L820), [1059](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1059) | **Fully resolved.** "or k" removed from line 820. "The size statements of §6.1 are conditional..." replaced in line 1059 with "§6.1's cutoffs are a fixed recipe against the zero-bias Gaussian reference." |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Audit of the Diff: Section 3 Prices, Header Numbers, and Text Inconsistencies

<!-- absence-ok: verbatim third-party read report -->
### 2.1 Complete Audit of Every Price Number and Cap

<!-- absence-ok: verbatim third-party read report -->
All price products, phase allocations, and cap totals in Section 3 and the Rev 10 Header were audited:

<!-- absence-ok: verbatim third-party read report -->
1. **Unit Planning Figure:**
   - Priced at $n \times 0.19$ node-h per unfold, with no rounding ([line 394](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L394)), grounded in COV2D historical benchmark of $112.74 / 600 = 0.1879 \approx 0.188$ node-h.
2. **Phase P1 Breakdown (Full / Lean):**
   - **W1 Full:** $200\text{ (N1)} + 200\text{ (N2)} + 400\text{ (N5)} + 50\text{ (N3)} + 3\text{ (central: nominal, G18, AR23)} = 853$ unfolds $\times 0.19 = \mathbf{162.07}$ node-h ([line 381](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L381)).
   - **W1 Lean:** $150\text{ (N1)} + 150\text{ (N2)} + 300\text{ (N5)} + 50\text{ (N3)} + 3\text{ (central)} = 653$ unfolds $\times 0.19 = \mathbf{124.07}$ node-h ([line 381](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L381)).
   - **W2 Full:** $200\text{ (N4)} + 180\text{ (A1f)} + 300\text{ (A1p)} + 3\text{ (central: vertices)} = 683$ unfolds $\times 0.19 = \mathbf{129.77}$ node-h ([line 382](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L382)).
   - **W2 Lean:** $150\text{ (N4)} + 0\text{ (A1f)} + 300\text{ (A1p)} + 3\text{ (central)} = 453$ unfolds $\times 0.19 = \mathbf{86.07}$ node-h ([line 382](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L382)).
   - **P1 Sums:** Full $162.07 + 129.77 = \mathbf{291.84}$ node-h (cap 330). Lean $124.07 + 86.07 = \mathbf{210.14}$ node-h (cap 240) ([line 383](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L383)). Exactly verified.
3. **Phase PV Breakdown:**
   - 600 validation toys $\times 0.19 = 114.00$ node-h.
   - 2 central unfolds $\times 0.19 = 0.38$ node-h.
   - Synthetic-seal test advance reservation = $2.00$ node-h ([line 385](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L385)).
   - Production writer and readout unmeasured estimate = $1.00$ node-h.
   - **PV Total:** $114.00 + 0.38 + 2.00 + 1.00 = \mathbf{117.38}$ node-h for both Full and Lean (cap 135) ([line 385](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L385)). Exactly verified.
4. **Campaign Price Totals:**
   - **Full Campaign:**
     - At measured PG lower bound ($1.33$ node-h): $0 + 1.33 + 291.84 + 0 + 117.38 = \mathbf{410.55}$ node-h.
     - At priced PG upper bound ($2.00$ node-h): $0 + 2.00 + 291.84 + 0 + 117.38 = \mathbf{411.22}$ node-h.
     - Stated Range: **410.55–411.22** node-h ([lines 258, 387](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L258)). Exactly verified.
   - **Lean Campaign:**
     - At PG $1.33$: $0 + 1.33 + 210.14 + 0 + 117.38 = \mathbf{328.85}$ node-h.
     - At PG $2.00$: $0 + 2.00 + 210.14 + 0 + 117.38 = \mathbf{329.52}$ node-h.
     - Stated Range: **328.85–329.52** node-h ([line 387](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L387)). Exactly verified.
   - **Totals Without N5:**
     - Full without N5 ($76.00$ node-h deducted): $410.55 - 76.00 = \mathbf{334.55}$ to $411.22 - 76.00 = \mathbf{335.22}$ node-h ([lines 258, 393](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L258)). Exactly verified.
     - Lean without N5 ($57.00$ node-h deducted): $328.85 - 57.00 = \mathbf{271.85}$ to $329.52 - 57.00 = \mathbf{272.52}$ node-h ([line 393](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L393)). Exactly verified.
5. **Ceiling and ST6 Enforcement Arithmetic:**
   - Joseph's approved total and binding ceiling: **409.22** node-h ([lines 259, 414](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L259)).
   - Stated arithmetic in [lines 417–421](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L417-L421):
     - At measured PG ($1.33$), expected total is $410.55$, which is $410.55 - 409.22 = \mathbf{1.33}$ node-h above the ceiling.
     - Margin between PG's priced top ($2.00$) and F1's measured ($1.33$) is $2.00 - 1.33 = \mathbf{0.67}$ node-h.
     - Synthetic test reservation adds $2.00$ node-h. $2.00 - 0.67 = 1.33$ node-h.
     - Total unfolds across P1 ($1536$) and PV ($602$) equal $2138$ unfolds. If actual unfolds spend the measured $0.188$ node-h rather than the priced $0.190$, the saving is $2138 \times 0.002 = 4.276$ node-h, which easily absorbs the $1.33$ node-h delta.
     - ST6 is the hard stop ([line 421](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L421)): if `sacct` spend reaches 409.22, the run stops and goes to the director.
   - All arithmetic in Section 3 and the header is mutually consistent.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 2.2 Audit of Defects Introduced by the Diff and Remaining Contradictions

<!-- absence-ok: verbatim third-party read report -->
#### Defect 1: MAJOR — §9.2 Line 1148 Stale Price Parenthetical & Textual Contradiction with Section 3
- **Location:** Section 9 item 2, [line 1148](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1148):
  ```markdown
  2. **Size: decided.** Full, as designed (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`, Joseph's governing re-confirmation): two sealed tunes, full P1 toy counts, and N5 always, at about 409 node-h at most (408.6–409.2). That is above half the balance, and Joseph approved it.
  ```
- **Issue:**
  The parenthetical `(408.6–409.2)` was inherited from Rev 9 when the price was 408.55–409.22 node-h. In Rev 10, the synthetic test was priced into PV, raising the expected price in Section 3 [line 387](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L387) and Rev 10 header [line 258](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L258) to **410.55–411.22**, while the ceiling remained pinned at **409.22** node-h. Quoting `(408.6–409.2)` in §9.2 contradicts Section 3 and the header.
- **Severity:** **MAJOR**
- **Surgical Fix:**
  In §9.2 [line 1148](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1148), change:
  `at about 409 node-h at most (408.6–409.2).`
  to:
  `at about 409 node-h at most (ceiling 409.22; expected price 410.55–411.22, §3).`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
#### Defect 2: MINOR — §6.1 Line 954 and §5.2 Line 875 Undefined Diagnostic Variables $u, u_R$
- **Locations:**
  - Section 5.2, [line 875](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L875):
    `- §6.1's u, u_R and F_exp, and §6.2's law, all use this U and this drawn part.`
  - Section 6.1, [line 954](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L954):
    `- **What is labelled** is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. u, u_R and F_exp are printed.`
- **Issue:**
  In Rev 9, $u$ and $u_R$ were explicitly defined in §6.1 as the undrawn shares $u = (1/\mathrm{ndf}_F) \sum_i u_i^\top U u_i / \lambda_i^F$, and $F_{\exp} = ((N-1)/N)(1-u)$. In Rev 10, the definition of $F_{\exp}$ was rewritten to use $V_+$ directly ([lines 948–951](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L948-L951)). As a result, the symbols $u$ and $u_R$ were deleted from the mathematical formulation of §6.1, but line 954 still requires that `u, u_R and F_exp are printed`, and line 875 still references them. A strict automated implementation of the readout has no defined formula for $u$ and $u_R$.
- **Severity:** **MINOR**
- **Surgical Fix:**
  1. In §6.1 [line 954](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L954), change:
     `- **What is labelled** is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. u, u_R and F_exp are printed.`
     to:
     `- **What is labelled** is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. F_exp and F_exp,R are printed.`
  2. In §5.2 [line 875](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L875), change:
     `- §6.1's u, u_R and F_exp, and §6.2's law, all use this U and this drawn part.`
     to:
     `- §6.1's F_exp and §6.2's law use this U and this drawn part (via V₊).`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
#### Defect 3: MINOR — §6.2 Line 1012 Residual Notation Discrepancy in Stress Parameter $a$ ($V_{\mathrm{drawn}}$ vs $V_+$)
- **Location:** Section 6.2, [line 1012](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1012):
  ```markdown
  - three deficit scenarios, with φ the drawn fluctuation and a = tr(V⁺V_drawn)/ndf:
  ```
- **Issue:**
  Rev 10 updated [lines 993–994](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L993-L994) to state that $V_+$ is the sole reference covariance for stress runs, and updated scenario D2 ([line 1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1015)) to use $V_+$. However, line 1012 still writes $V_{\mathrm{drawn}}$ in the definition of the scalar $a$ used for D1 and D3.
- **Severity:** **MINOR**
- **Surgical Fix:**
  In §6.2 [line 1012](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L1012), change `a = tr(V⁺V_drawn)/ndf` to `a = tr(V⁺V₊)/ndf`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
#### Defect 4: MINOR — §5 Line 820 Grammar Hitch from Incomplete Deletion of "or k"
- **Location:** Section 5, [line 820](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L820):
  ```markdown
  **The selection data**, which any P2 bar, choice reads, are N4 and A1p only.
  ```
- **Issue:**
  The deletion of "or k" in diff hunk 7 left `, choice reads,` without a coordinating conjunction.
- **Severity:** **MINOR**
- **Surgical Fix:**
  In §5 [line 820](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix10/inputs/COVFIX-DECLARATION.md#L820), change `any P2 bar, choice reads,` to `any P2 bar or choice reads,`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Binding Readiness & Summary of Required Fixes

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative prerequisites (§9 item 3: committed iris receipt, fresh PG session, and director's passphrase piping wrapper), **Draft Rev 10 is NOT ready to bind as written**.

<!-- absence-ok: verbatim third-party read report -->
Because pre-registration declarations are permanently frozen at binding and govern irreversible compute spend, binding cannot occur while Section 9 contains an internal price contradiction against Section 3 and the Header, or while Section 6.1 instructs the readout to print undefined variables.

<!-- absence-ok: verbatim third-party read report -->
Applying the following four surgical edits will immediately resolve all remaining defects and make **Draft Rev 10.1 fully GO for binding**:

<!-- absence-ok: verbatim third-party read report -->
1. **§9.2 Line 1148 (MAJOR):** Replace `(408.6–409.2)` with `(ceiling 409.22; expected price 410.55–411.22, §3)`.
2. **§6.1 Line 954 & §5.2 Line 875 (MINOR):** In line 954, replace `u, u_R and F_exp are printed.` with `F_exp and F_exp,R are printed.`; in line 875, replace `§6.1's u, u_R and F_exp, and §6.2's law, all use this U and this drawn part.` with `§6.1's F_exp and §6.2's law use this U and this drawn part (via V₊).`
3. **§6.2 Line 1012 (MINOR):** Replace `a = tr(V⁺V_drawn)/ndf:` with `a = tr(V⁺V₊)/ndf:`.
4. **§5 Line 820 (MINOR):** Replace `any P2 bar, choice reads,` with `any P2 bar or choice reads,`.
