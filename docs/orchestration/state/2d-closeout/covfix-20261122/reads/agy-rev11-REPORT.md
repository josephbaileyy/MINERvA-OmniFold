<!-- absence-ok: verbatim third-party read report -->
GO

<!-- absence-ok: verbatim third-party read report -->
# Review of COVFIX Pre-Registration Declaration (Draft Rev 11)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** Antigravity (agy) — Confirming Technical Read  
**Target Document:** [`inputs/COVFIX-DECLARATION.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md) (Draft Rev 11, 2026-11-23)  
**Baseline Documents:**
- [`inputs/rev10-to-rev11.diff`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/rev10-to-rev11.diff)
- [`inputs/agy-rev10-REPORT.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/agy-rev10-REPORT.md)
- [`inputs/codex2-rev10-REPORT.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/codex2-rev10-REPORT.md)
- [`inputs/DECISION-20261123.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/DECISION-20261123.md)  
**Report Output:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/report.md`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Executive Summary

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative prerequisites in §9 item 3 (committed iris receipt, naming the fresh PG session, and the director's passphrase piping wrapper), **Draft Rev 11 is GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
Draft Rev 11 incorporates all required fixes from both Rev 10 reports ([`inputs/agy-rev10-REPORT.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/agy-rev10-REPORT.md) and [`inputs/codex2-rev10-REPORT.md`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/codex2-rev10-REPORT.md)). Specifically:
1. **$K_B$ Construction Refusal Rule (Codex BLOCKING 1):** Explicitly specifies in §5.2 ([lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872)) that every ensemble entering a fitted band requires a successful carry, a successful PSD projection of $F_A - U$ (with $L=I$) to $V_+$, and a finite positive $F_{\exp,R}$; otherwise $K_B$ is omitted and reported.
2. **Readout Isolation & Stress Decoupling (Codex BLOCKING 2):** In §3.4 ([lines 713–717](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L713-L717)), the secret-bearing readout role persists grades, cleans up, scans, publishes the grades, and terminates. Descriptive stress runs are completely relocated to a subsequent, separate job with no seal access, ensuring that any stress timeout or failure cannot touch or invalidate published grades ([line 619](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L619), [lines 1144–1145](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1144-L1145)).
3. **Ledger Keying & Attempt Filtering (Codex MAJOR):** In §3.4 ([lines 699–705](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L699-L705)), chain records are explicitly keyed by the ledger's allocation job ID. Failed attempts are marked excluded by the ledger, and missing, extra, and mismatch checks apply strictly to accepted records.
4. **Canonical Tied Basis (Codex MAJOR):** In §5.2 ([lines 882–885](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L882-L885)), ordered-axis Gram–Schmidt orthonormalization is strictly restricted to equal eigenvalues to floating-point equality, while the $10^{-9}$ near-tie convention is used solely for band edge assignment.
5. **ST6 Trigger Harmonization (Codex MAJOR):** In §3 ([lines 434–436](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L434-L436)), ST6 is defined solely as the ledger's atomic reservation gate at the 409.22 node-h ceiling, removing the competing description of a remaining-phases projection stop.
6. **Section 9.2 Price Harmonization (Agy MAJOR / Codex MINOR):** In §9.2 ([lines 1169–1171](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1169-L1171)), the stale parenthetical `(408.6–409.2)` is replaced with an explicit pointer to §3 and confirmation of the 409.22 node-h binding ceiling enforced by ST6.
7. **Minor Textual and Notational Cleanups (Agy & Codex MINOR):**
   - Deletion of undefined symbols $u, u_R$ in §5.2 ([line 896](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L896)) and §6.1 ([line 975](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L975)).
   - Alignment of stress parameter $a = \operatorname{tr}(V^+ V_+)/\mathrm{ndf}$ in §6.2 ([line 1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033)).
   - Correction of the selection data grammatical phrasing in §5 ([lines 837–838](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L837-L838)).

<!-- absence-ok: verbatim third-party read report -->
The surgical diff rev 10 → rev 11 introduces **no new defects** and leaves **no internal contradictions**. A single residual minor item—a non-operational notation slip in an explanatory phrase in §6.1 [line 998](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L998) (`W V_drawn Wᵀ` where $V_+$ is sampled)—is identified and provided with a drop-in edit. Because it has zero operational, algorithmic, or gating effect, it does not impede binding.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of All Findings from Both Rev 10 Reports

<!-- absence-ok: verbatim third-party read report -->
### 1.1 Findings from agy-rev10-REPORT.md

<!-- absence-ok: verbatim third-party read report -->
| Finding ID & Title | Prior Severity | Status in Rev 11 | Exact Rev 11 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **Defect 1: §9.2 Line 1148 Stale Price Parenthetical & Textual Contradiction with §3** | **MAJOR** | **CLOSED** | [Lines 1169–1171](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1169-L1171) | **Fully resolved.** Line 1169 replaces `at about 409 node-h at most (408.6–409.2)` with: `at about 409 node-h at most. The current estimate is in §3; the binding ceiling is 409.22 node-h, enforced by ST6. That is above half the balance, and Joseph approved it.` Completely eliminates the contradiction with §3 price table (410.55–411.22) and aligns with the 409.22 ceiling. |
| **Defect 2: §6.1 Line 954 & §5.2 Line 875 Undefined Diagnostic Variables $u, u_R$** | **MINOR** | **CLOSED** | [Line 896](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L896), [Line 975](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L975) | **Fully resolved.** In §6.1 line 975, `u, u_R and F_exp are printed` was replaced by `F_exp and each F_exp,R are printed.` In §5.2 line 896, `§6.1's u, u_R and F_exp, and §6.2's law, all use this U and this drawn part` was replaced by `§6.1's F_exp and §6.2's law use this drawn part, through its PSD-handled form V₊.` Undefined symbols are completely eliminated. |
| **Defect 3: §6.2 Line 1012 Residual Notation Discrepancy in Stress Parameter $a$ ($V_{\mathrm{drawn}}$ vs $V_+$)** | **MINOR** | **CLOSED** | [Line 1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033) | **Fully resolved.** Line 1033 updates the definition of the deficit scenario trace scalar: `three deficit scenarios, with φ the drawn fluctuation and a = tr(V⁺V₊)/ndf:`, matching lines 1014–1015 and line 1036. |
| **Defect 4: §5 Line 820 Grammar Hitch from Incomplete Deletion of "or k"** | **MINOR** | **CLOSED** | [Lines 837–838](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L837-L838) | **Fully resolved.** Replaced `which any P2 bar, choice reads,` with `**The selection data**, the only data any P2 bar or choice reads, are N4 and A1p.` The sentence is fully grammatical. |
| **Inherited Items (agy-rev9 Defect 2.1 & 2.2; Codex Rev 9 Items 1–10)** | **VARIOUS** | **CLOSED** | [Lines 616–625](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L616-L625), [697–708](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L697-L708), [713–717](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L713-L717), [882–885](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L882-L885), [924–939](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L924-L939), [969–974](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L969-L974), [1053–1077](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1053-L1077), [1100–1121](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1100-L1121) | All items confirmed closed in Rev 10 were re-verified against Rev 11 and remain fully closed. |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 1.2 Findings from codex2-rev10-REPORT.md

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.1 Codex Rev 10 Minimum Changes Before Binding (§ Minimum changes)

<!-- absence-ok: verbatim third-party read report -->
| Finding / Item | Prior Severity | Status in Rev 11 | Exact Rev 11 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **1. Finish the $K_B$ fit refusal rule** | **BLOCKING** | **CLOSED** | [Lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872), [Lines 973–974](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L973-L974) | **Fully resolved.** Lines 870–872 explicitly state: `- **construction inputs:** every ensemble that enters a fitted band needs a successful carry, a successful PSD projection of F_A − U (with L = I) to its V₊, and a finite, positive F_exp,R. If any of those fails for an ensemble the band needs, K_B is omitted, and that is reported;`. Lines 973–974 confirm: `In the fit, it refuses K_B's construction.` Existing exclusion for bands with $<10$ modes is preserved ([lines 873–874](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L873-L874)). |
| **2. Complete PV before optional stress work** | **BLOCKING** | **CLOSED** | [Lines 713–717](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L713-L717), [Line 619](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L619), [Lines 1144–1145](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1144-L1145) | **Fully resolved.** Lines 713–714 mandate: `It then decrypts the graded truths in-process, runs §6.2's controls, grades, persists the verified grades, cleans up, scans, and publishes the grades. Then it ends.`. Lines 715–717 define: `6. **The descriptive stress runs** are a separate job, after publication, with no seal access. They need only V₊, the candidates and D_u, none of which is secret. Their failure, timeout or crash leaves the published grades untouched, and failed scenarios are reported as omitted.`. Line 619 confirms: `A descriptive stress run's failure never blocks a completed grade.` Section 8 ([lines 1144–1145](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1144-L1145)) enumerates them as distinct jobs. |

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.2 Codex Rev 10 Section "Rev 9 findings in rev 10" (Tables 1 & 2)

<!-- absence-ok: verbatim third-party read report -->
| Table & Item | Rev 10 Disposition | Status in Rev 11 | Exact Rev 11 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **Table 1 Item 1: $K_B$ fallback** | **CLOSED** | **CLOSED** | [Lines 851–855](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L851-L855), [924–939](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L924-L939) | Re-verified: $F_A$ and $K_{\mathrm{ref}}$ provide unambiguous fallback reference for unfunded branches and preserve accepted corrections if $K_A$ fails P2. |
| **Table 1 Item 2: Sampled covariance** | **PARTLY CLOSED · BLOCKING** | **CLOSED** | [Lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872), [969–974](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L969-L974), [1013–1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1013-L1015), [1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033) | Change 1 applied ([lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872)); fit denominators and spread ratios use $V_+$ ([lines 969–974](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L969-L974)); trace parameter $a$ uses $V_+$ ([line 1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033)). |
| **Table 1 Item 3: Actual unfold invocation** | **CLOSED** | **CLOSED** | [Lines 697–708](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L697-L708) | Re-verified: Executable sha256 and resolved argv hashed and checked against freeze; applies to central unfolds. |
| **Table 1 Item 4: Same-truth refusal scope** | **CLOSED** | **CLOSED** | [Lines 1053–1077](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1053-L1077) | Re-verified: Carry, reference, and reading-specific refusals strictly scoped. Total deficit triggers FAILS first. |
| **Table 2 Item 1: Drawn covariance and spectral map** | **PARTLY CLOSED · BLOCKING** | **CLOSED** | [Lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872), [886–897](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L886-L897) | Full-space map $L$ and projected covariance formulas in place; Change 1 applied at lines 870–872. |
| **Table 2 Items 2–7, 9, 10, 12: Reference probabilities, guards, budget, custody, spend, ST1/PX, outcomes, toy law, benchmark** | **CLOSED** | **CLOSED** | Relevant sections throughout §2, §3, §4, §6, §7 | All previously closed inherited items remain completely intact and verified in Rev 11. |
| **Table 2 Item 8: Reservations and completeness (Attempt filtering)** | **PARTLY CLOSED · MAJOR** | **CLOSED** | [Lines 699–700](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L699-L700), [Lines 703–705](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L703-L705) | **Fully resolved.** Chain record tuple explicitly expanded to include `allocation job ID from the ledger` ([lines 699–700](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L699-L700)). Lines 703–705 state: `Records are keyed by allocation job ID; the ledger marks a failed attempt's job ID as excluded. The missing, extra and mismatch checks apply to the accepted records, and exactly one verified product per expected ID must come from them.` |
| **Table 2 Item 11: Retained-space conventions (Tied bases)** | **PARTLY CLOSED · MAJOR** | **CLOSED** | [Lines 882–885](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L882-L885) | **Fully resolved.** Lines 882–885 state: `- **For an exactly tied eigenspace** (equal eigenvalues to floating-point equality, in a grading eigensystem), the basis is canonical: the ordered cell axes e_1, e_2, … are projected into the eigenspace and orthonormalized in that order by Gram–Schmidt, skipping null projections. The per-mode flags then do not depend on the solver. - The 1e-9 near-tie convention above is used **only** for band assignment, never for basis rotation.` |

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.3 Codex Rev 10 Section "Other rev 10 defects"

<!-- absence-ok: verbatim third-party read report -->
| Finding / Item | Prior Severity | Status in Rev 11 | Exact Rev 11 Line(s) | Technical Verification & Disposition |
|---|---|---|---|---|
| **ST6 has two different triggers** | **MAJOR** | **CLOSED** | [Lines 434–436](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L434-L436) | **Fully resolved.** Replaced lines 421–422 with: `- **ST6 is the hard stop:** the ledger's atomic gate (§3.3) at 409.22 node-h. A submission it refuses stops the run, and that goes to the director, not to Joseph as a re-approval. The price table above is an estimate, not a trigger; PX keeps its own repricing rule.`. Harmonizes §3 with §3.3 ([lines 624–625](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L624-L625)). |
| **Finish the reference notation cleanup** | **MINOR** | **PARTLY CLOSED** | [Line 896](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L896), [Line 975](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L975), [Line 1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033); [Line 998](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L998) | **Substantially closed.** Deficit trace parameter $a = \operatorname{tr}(V^+ V_+)/\mathrm{ndf}$ is **CLOSED** at line 1033; deletion of print instruction for $u, u_R$ is **CLOSED** at line 975; deletion of $u, u_R$ in §5.2 is **CLOSED** at line 896. Line 998 explanatory sentence still reads `The whitened covariance W V_drawn Wᵀ is not the identity`, remaining **OPEN** as a MINOR non-operational text notation item (see Section 2). |
| **Update the live price summary** | **MINOR** | **CLOSED** | [Lines 1169–1171](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1169-L1171) | **Fully resolved.** Replaced stale `(408.6–409.2)` in §9.2 with pointer to §3 and explicit statement of the 409.22 node-h ceiling enforced by ST6. |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Audit of New Defects Introduced by the Diff & Remaining Internal Contradictions

<!-- absence-ok: verbatim third-party read report -->
### 2.1 Complete Audit of Every Diff Hunk in `rev10-to-rev11.diff`

<!-- absence-ok: verbatim third-party read report -->
All 13 diff hunks in [`inputs/rev10-to-rev11.diff`](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/rev10-to-rev11.diff) were checked against first principles and surrounding text:

<!-- absence-ok: verbatim third-party read report -->
1. **Hunk 1 (Title, line 7):** Updates title to `COVFIX declaration, DRAFT rev 11: the 2D covariance fix (2026-11-23)`. Clean.
2. **Hunk 2 (Revision History, lines 261–273):** Records Rev 11 changes, explicitly detailing the resolution of agy's 1 MAJOR and 3 MINOR defects and Codex's 2 BLOCKING defects. Clean.
3. **Hunk 3 (Section 3, lines 434–436):** Unifies ST6 as the ledger's atomic reservation gate at 409.22 node-h. Clean.
4. **Hunk 4 (Section 3.4, lines 699–705):** Adds allocation job ID to chain record tuple; specifies ledger exclusion for failed attempt job IDs; bounds missing/extra/mismatch checks to accepted records. Clean.
5. **Hunk 5 (Section 3.4, lines 713–717):** Moves descriptive stress runs to an independent post-publication job without seal access, ensuring readout ends immediately after publication of grades. Clean.
6. **Hunk 6 (Section 5, lines 837–838):** Resolves grammar hitch in selection data specification (`the only data any P2 bar or choice reads, are N4 and A1p`). Clean.
7. **Hunk 7 (Section 5.2, lines 870–872):** Implements $K_B$ fit refusal rule on failed carry, PSD projection of $F_A - U$ (with $L=I$), or non-positive $F_{\exp,R}$. Clean.
8. **Hunk 8 (Section 5.2, lines 882–885):** Canonicalizes basis rotation via ordered cell-axis Gram–Schmidt for floating-point equal eigenvalues only; reserves $10^{-9}$ convention solely for band assignment. Clean.
9. **Hunk 9 (Section 5.2, line 896):** Deletes undefined symbols $u, u_R$, referencing $V_+$ directly. Clean.
10. **Hunk 10 (Section 6.1, line 975):** Deletes print instruction for $u, u_R$, requiring $F_{\exp}$ and each $F_{\exp,R}$ to be printed. Clean.
11. **Hunk 11 (Section 6.2, line 1033):** Corrects deficit stress parameter trace formulation to $a = \operatorname{tr}(V^+ V_+)/\mathrm{ndf}$. Clean.
12. **Hunk 12 (Section 8, lines 1144–1145):** Separates §6 readout and descriptive stress runs in code audit manifest. Clean.
13. **Hunk 13 (Section 9.2, lines 1169–1171):** Updates Joseph size decision summary to point to §3 and state 409.22 node-h ceiling enforced by ST6. Clean.

<!-- absence-ok: verbatim third-party read report -->
**Result:** The diff introduces **no new defects** whatsoever.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 2.2 Mathematical and Price Consistency Audit

<!-- absence-ok: verbatim third-party read report -->
1. **Phase Arithmetic and Caps (§3):**
   - **PG:** Priced 1.33–2.00 node-h (Cap 3.0 node-h).
   - **P1 W1:** $853 \text{ unfolds} \times 0.19 = \mathbf{162.07} \text{ node-h}$ (Full) / $653 \text{ unfolds} \times 0.19 = \mathbf{124.07} \text{ node-h}$ (Lean).
   - **P1 W2:** $683 \text{ unfolds} \times 0.19 = \mathbf{129.77} \text{ node-h}$ (Full) / $453 \text{ unfolds} \times 0.19 = \mathbf{86.07} \text{ node-h}$ (Lean).
   - **P1 Total:** $162.07 + 129.77 = \mathbf{291.84} \text{ node-h}$ (Full, Cap 330) / $124.07 + 86.07 = \mathbf{210.14} \text{ node-h}$ (Lean, Cap 240).
   - **PV Total:** $600 \text{ toys} \times 0.19 = 114.00$, $2 \text{ central} \times 0.19 = 0.38$, synthetic test fixed reservation $2.00$, writer/readout estimate $1.00 \implies \mathbf{117.38} \text{ node-h}$ (Cap 135).
   - **Campaign Price Range:**
     - Full: $0 + [1.33, 2.00] + 291.84 + 0 + 117.38 = \mathbf{410.55–411.22} \text{ node-h}$.
     - Lean: $0 + [1.33, 2.00] + 210.14 + 0 + 117.38 = \mathbf{328.85–329.52} \text{ node-h}$.
     - Without N5: Full 334.55–335.22 node-h; Lean 271.85–272.52 node-h.
   - **Sum of Caps:** Full $3.0 + 330 + 135 = \mathbf{468} \text{ node-h}$; Lean $3.0 + 240 + 135 = \mathbf{378} \text{ node-h}$.
   - **Ceiling and ST6 Enforcement:** Joseph approved 409.22 node-h ceiling. ST6 is the ledger's atomic reservation gate at 409.22 node-h ([lines 434–436](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L434-L436), [624–625](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L624-L625)).
   - Every number in the header, Section 3, Section 3.3, and Section 9.2 is in exact arithmetic harmony.

<!-- absence-ok: verbatim third-party read report -->
2. **Residual Minor Notation Item in Section 6.1 Line 998:**
   - **Location:** Section 6.1, [line 998](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L998):
     ```markdown
     The reference probabilities q (joint) and p_i (per mode) are estimated from 20,000 draws of §6.2's Gaussian law at
     zero bias, at seed 9_992_000, per candidate and truth. The whitened covariance W V_drawn Wᵀ is not the identity, so no
     analytic 0.6827 is assumed.
     ```
   - **Issue:** Section 6.2 ([lines 1013–1015](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1013-L1015)) defines $V_+$ as the sole reference covariance for the Gaussian law draws ($e \sim N(0, V_+(t))$). The whitened covariance of the simulated draws is therefore $W V_+ W^\top$. In Rev 10, Codex noted that $V_+$ should be used in the trace and in the whitening explanation. Rev 11 updated the trace in line 1033, but left `W V_drawn Wᵀ` in line 998.
   - **Impact Assessment:** This sentence is purely narrative and explanatory—it provides the rationale for why Monte Carlo draws are used to estimate $q$ and $p_i$ rather than relying on an analytic standard-normal or $\chi^2$ CDF. It has zero operational, algorithmic, or gating effect on the computation.
   - **Severity:** **MINOR**.
   - **Drop-in Fix:** In §6.1 line 998, replace `W V_drawn Wᵀ` with `W V₊ Wᵀ`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Binding Readiness & Summary of Findings

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative and credential prerequisites stated in §9 item 3 (committed iris receipt, naming the fresh PG session, and piping the director's passphrase wrapper):

<!-- absence-ok: verbatim third-party read report -->
### **Draft Rev 11 IS READY TO BIND (GO).**

<!-- absence-ok: verbatim third-party read report -->
All prior BLOCKING and MAJOR findings from both Rev 10 reports are completely **CLOSED**. The campaign design is structurally, algorithmically, and statistically sealed.

<!-- absence-ok: verbatim third-party read report -->
### Summary of Findings & Recommended Actions

<!-- absence-ok: verbatim third-party read report -->
| Item | Prior / Assigned Severity | Scope & File Location | Status | Recommended Fix / Note |
|---|---|---|---|---|
| **$K_B$ construction refusal rule** | **BLOCKING** | §5.2 [lines 870–872](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L870-L872) | **CLOSED** | Fully articulated in text. No action needed. |
| **Complete PV before stress work** | **BLOCKING** | §3.4 [lines 713–717](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L713-L717) | **CLOSED** | Readout role terminates at grade publication; stress decoupled to seal-free job. No action needed. |
| **ST6 ledger gate trigger** | **MAJOR** | §3 [lines 434–436](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L434-L436) | **CLOSED** | Harmonized to atomic ledger gate at 409.22 node-h alone. No action needed. |
| **Chain records keyed by job ID** | **MAJOR** | §3.4 [lines 699–705](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L699-L705) | **CLOSED** | Ledger job ID in chain record; checks bounded to accepted records. No action needed. |
| **Gram–Schmidt only on exact ties** | **MAJOR** | §5.2 [lines 882–885](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L882-L885) | **CLOSED** | Basis rotation restricted to floating-point equality; $10^{-9}$ for bands only. No action needed. |
| **§9.2 live price pointer** | **MAJOR** | §9.2 [lines 1169–1171](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1169-L1171) | **CLOSED** | Stale parenthetical removed; points to §3 and 409.22 ceiling. No action needed. |
| **Undefined variables $u, u_R$** | **MINOR** | §5.2 [line 896](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L896), §6.1 [line 975](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L975) | **CLOSED** | References and print instruction removed. No action needed. |
| **Deficit trace parameter $a$** | **MINOR** | §6.2 [line 1033](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L1033) | **CLOSED** | Trace formula updated to $a = \operatorname{tr}(V^+ V_+)/\mathrm{ndf}$. No action needed. |
| **Selection data grammar** | **MINOR** | §5 [lines 837–838](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L837-L838) | **CLOSED** | Grammatical omission corrected. No action needed. |
| **Whitening explanation notation** | **MINOR** | §6.1 [line 998](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix11/inputs/COVFIX-DECLARATION.md#L998) | **OPEN** | In §6.1 line 998, replace `W V_drawn Wᵀ` with `W V₊ Wᵀ`. (Non-operational; optional editorial polish before binding). |
