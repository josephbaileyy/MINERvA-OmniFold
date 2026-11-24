<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
# Review of COVFIX Pre-Registration Declaration (Draft Rev 9)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** Antigravity (agy) — Confirming Technical Read  
**Target:** [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md) (Draft Rev 9, 2026-11-23)  
**Baseline Documents:**
- [rev8-to-rev9.diff](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/rev8-to-rev9.diff)
- [agy-rev8-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/agy-rev8-REPORT.md)
- [codex2-rev8-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/codex2-rev8-REPORT.md)
- [DECISION-20261123.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/DECISION-20261123.md)  
**Report Destination:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/report.md`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Executive Summary

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative binding prerequisites (§9 item 3: committed iris receipt, fresh PG session, and director's passphrase piping wrapper), **Draft Rev 9 is NO-GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
Rev 9 makes tremendous progress, closing nearly all surviving findings from the Rev 8 reports within the director's scope:
1. **Precedence & Baseline Challenge Protection:** In §6.4, `FAILS` is moved to row 1 of the verdict precedence table, ensuring an observed deficit on real toys is never masked by a control refusal. In §7 Part 2, a baseline challenge is triggered whenever any valid $K_0$ reading shows a `FAILS` condition.
2. **Unfunded PX Branch & Reporting:** §5.2 lines 800–804 explicitly define the fluctuation reference $F_A$ without $K_A$ ($F_A = Q_{\mathrm{rep}}$ if PX is unfunded, unexplained, or acceptance fails), allowing $V_F = L F_A L^\top$ and $K_B = V_F + C_b$ to be constructed cleanly. §7 Part 1 provides an independent, non-contradictory reporting sentence for a reproduced defect where PX had no funded path.
3. **Spectral Map & Pooled Spread Ratio:** $L = I + \sum_{R\ \mathrm{active}} (\sqrt{\phi_R} - 1) P_R$ is bound on the full space, constituent blocks are mapped consistently, the separate rank-wise "Applied" text is excised, and $\hat{f}_R$ pools the normalized spread ratio $\tilde{F}_R = F_R / F_{\exp,R}$ with finite-$N$ correction applied once inside $F_{\exp,R}$.
4. **Gaussian Covariance Control:** Full 205-eigenvalue C-PSD is enforced, eigenvalues within $\pm 10^{-12}\lambda_{\max}$ are zeroed giving $V_+$, and the Cholesky/sampling factor $A$ must reconstruct $V_+$ to within $10^{-10}$ in Frobenius norm before 20,000-draw marginal checks and cutoff generation proceed.
5. **End-to-End Custody Chain:** Compute jobs hash actual inputs and complete outputs, readout rehashes outputs and verifies one complete product per expected ID against authenticated writer manifest and freeze, original PG seal is pinned at PG close, freeze is pinned at P2 close, and Slurm `srun` stdin passphrase delivery to internal `gpg --passphrase-fd 3` is fully specified with mandatory zero-exit integrity gating.
6. **Ledger & Completeness:** A unique 128-bit hex intent ID embedded in Slurm job names enables robust `sacct` reconciliation, reservations remain open during accounting uncertainty, and synthetic seal test allocations are priced under the ledger.

<!-- absence-ok: verbatim third-party read report -->
However, a strict technical audit reveals **one remaining MAJOR defect** and **one MINOR cosmetic inconsistency**:
- **MAJOR (Inexecutable Reference for Cut Diagnostic & Residual Rule when $K_A$ is Omitted):** While lines 800–804 define the fluctuation reference $F_A$ without $K_A$, lines 866–874 still literally instruct P2 to evaluate the cut diagnostic and the residual rule ($K_B$ against $K_A$ only) against $K_A$ and $U_{A,\mathrm{well}}$. On the authorized unfunded-PX path, $K_A$ is omitted and does not exist. P2 admission of $K_B$ (§5.3 line 888) is therefore inexecutable without specifying that the reference candidate is $K_0$ ($K_{\mathrm{ref}} = F_A + C_{\mathrm{model\_abs}}(x_R)$) when $K_A$ is omitted.
- **MINOR (Notation Discrepancy in D2):** Line 970 writes $V_{\mathrm{drawn}}$ in the definition of $a_R$, whereas line 957 specifies that $V_+$ is used for stress runs.

<!-- absence-ok: verbatim third-party read report -->
Applying the targeted surgical fix to §5.2 will resolve this final defect and render **Draft Rev 9.1 GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of Findings from Both Rev 8 Reports

<!-- absence-ok: verbatim third-party read report -->
### 1.1 Findings from agy-rev8-REPORT.md (§3)

<!-- absence-ok: verbatim third-party read report -->
| Finding | Severity (Rev 8) | Status in Rev 9 | Rev 9 Lines | Disposition Analysis |
|---|---|---|---|---|
| **Defect 1: Baseline Challenge Suppression via REFUSED Precedence in §6.4 & §7** | BLOCKING | **CLOSED** | 997–1005, 1030–1034 | In §6.4 (lines 997–1002), `FAILS` is placed in row 1 of the verdict precedence table before `REFUSED` (`"at either truth, a valid reading shows: M − h > 1.25..."`). In line 1004, the declaration states: *"A refusal cannot hide a valid observed deficit, because FAILS is read first, and every refusal is printed beside it."* In §7 Part 2 (lines 1030–1031), a baseline challenge is triggered if *"at one sealed truth at least, a valid K0 reading shows a FAILS condition, whatever K0's other readings are."* |
| **Defect 2: Logical Contradiction in §7 Part 1 Outcome Template for Unfunded PX** | MAJOR | **CLOSED** | 1020–1024 | Lines 1020–1024 provide two separate, mutually exclusive reporting sentences: one for a funded path where acceptance passed, and an independent sentence for the unfunded path: *"'A construction defect in <block>'s builder was reproduced (reproducing test as above); PX had no funded path, so the correction and its acceptance check did not run, and K_A was omitted for this run.'"* |
| **Defect 3: Passphrase Piping Contradiction: Slurm `srun` Stdin vs GPG `passphrase-fd 3`** | MAJOR | **CLOSED** | 750–756 | §4.2 lines 750–753 now explicitly specify the stream architecture: *"The passphrase reaches the bound binary on its stdin: the director's wrapper pipes it into srun, which forwards stdin to the task. The binary hands it to gpg on fd 3 through an internal pipe, and streams the payload on gpg's stdin and stdout. srun does not forward other file descriptors."* Line 755 adds that no decrypted product is used before `gpg` exits 0. |
| **Defect 4: Notation Inconsistency in §3.3 Line 450 ("Ā_R/B̄")** | MINOR | **CLOSED** | 484–487 | Line 484 replaces `Ā_R/B̄` with exact notation: *"Each row's guarded quantity is the band mean of per-mode ratios, (1/ndf_R) Σ_{i∈R} Â_i/B̂_i, with Â_i from toys and B̂_i from a block or, for N5, from replicas."* |
| **Defect 5: Stale "no challenge" Outcome Citation in §5.1 Line 735** | MINOR | **CLOSED** | 794 | Line 794 updates the citation from `"no challenge"` to `("no deficit shown", §7)`, matching §7 Part 2 line 1032. |
| **Defect 6: Stale "the k rule" Reference in §3.3 Line 499** | MINOR | **CLOSED** | 539 | The stale phrase `, the k rule` was completely deleted from the list of immutable items in ST1's exception (lines 538–540). |

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 1.2 Findings from codex2-rev8-REPORT.md

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.1 New Rev 8 Defects (§2)

<!-- absence-ok: verbatim third-party read report -->
| Item | Severity (Rev 8) | Status in Rev 9 | Rev 9 Lines | Disposition Analysis |
|---|---|---|---|---|
| **1. The unfunded branch cannot build $K_B$ as written** | BLOCKING | **PARTLY CLOSED** | 515–516, 800–804, 866–874, 1022–1024 | **Closed for construction & reporting:** §5.2 lines 800–804 define $F_A = Q_{\mathrm{rep}}$ if PX is unfunded, unexplained, or acceptance failed, and declare $F_A$ as the reference throughout §5.2. $V_F = L F_A L^\top$ and $K_B = V_F + C_b$ are fully defined. §7 lines 1022–1024 provide the dedicated unfunded finding sentence.<br>**Open for P2 residual rule:** Lines 866–874 still literally state *"print its cut diagnostic against K_A's"* and *"Residual rule (K_B against K_A only): Only K_A's well-determined modes are checked... With U_A,well their orthonormal basis..."*. When $K_A$ is omitted, the reference candidate is $K_0$, but this is not explicitly named in lines 866–874 (see Defect 1 below). |
| **2. The Gaussian covariance control can pass a wrong sampler** | BLOCKING | **CLOSED** | 953–960 | Lines 953–960 enforce C-PSD across all 205 eigenvalues on the full carried matrix ($\lambda_{\min} \ge -10^{-12}\lambda_{\max}$), set eigenvalues within $\pm 10^{-12}\lambda_{\max}$ to 0 to yield $V_+$, require the Cholesky/sampling factor $A = U_+ \operatorname{diag}(\sqrt{\lambda_+})$ to reconstruct $V_+$ with $\|AA^\top - V_+\|_F / \|V_+\|_F \le 10^{-10}$, use $V_+$ for $F_{\exp}$, cutoff draws, and stress runs, and apply the 0.05 marginal check on $V_+$'s nonzero modes. |
| **3. `REFUSED` can erase an observed baseline challenge** | MAJOR | **CLOSED** | 987–1005, 1030–1036 | §6.4 lines 987–993 separate candidate-level refusals from phase-terminal integrity failures and grade every valid reading per truth. `FAILS` precedes `REFUSED` in the precedence table (line 998). §7 line 1030 defines challenge from any valid reading showing `FAILS` at either truth. Line 1035 extends `ungraded` to PV terminating early from phase-terminal integrity failures. |
| **4. The new chain can attest to an input the job never checked** | MAJOR | **CLOSED** | 571, 652–659 | §3.4 lines 652–654 require each unfold job to hash the actual input file it unfolds and its complete output, recording `(expected truth and toy ID, input sha256 as computed, output sha256 as computed, bound unfold invocation sha256)`. Readout rehashes each output and requires exactly one complete product per expected ID (lines 571, 655–657), including central unfolds. Original PG seal and P2 freeze are pinned at phase close (line 659). |
| **5. The descriptive and scope text still has gaps** | MINOR | **CLOSED** | 539, 944–945, 968–973 | D1 restores zero-bias condition (line 968). D3 restores positive-denominator guard $w_j^\top V^+ w_j > 0$ and $a < 1.25$ (line 972). Undefined scenarios are printed as omitted (line 973). Prose flag-size claims are deleted, replaced by a fixed recipe against zero-bias reference (lines 944–945). Live references to $k$ rule are removed (line 539). |

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.2 Remaining Minimum Changes Before Binding (§3)

<!-- absence-ok: verbatim third-party read report -->
| Minimum Change | Severity (Rev 8) | Status in Rev 9 | Rev 9 Lines | Disposition Analysis |
|---|---|---|---|---|
| **1. Bind one spectral map and one block decomposition** | BLOCKING | **CLOSED** | 806–838 | §5.2 lines 828–838 bind $L = I + \sum_{R\ \mathrm{active}} (\sqrt{\phi_R} - 1) P_R$ on the full space, with $L = I$ on cut complement and for $K_0, K_A$. Constituent blocks are mapped via $L \cdot (\cdot) \cdot L^\top$. Separate rank-wise "Applied" text is excised. In lines 806–811, $\hat{f}_R$ pools normalized band spread $\tilde{F}_R = F_R / F_{\exp,R}$ against reference $F_A$, with finite-$N$ correction applied once inside $F_{\exp,R}$. |
| **2. Finish the funded PX acceptance rule** | BLOCKING | **CLOSED** | 484–487, 505–507, 517, 528–535 | First-time W2 work is deleted from PX costs and counted once in remainder (lines 507, 517). Acceptance check inputs are explicitly itemized for N5, N2, N3, and `universe` rows (lines 528–534). Guarded quantity is defined as band mean of per-mode ratios (line 484). Acceptance requires at least one band with $\ge 10$ modes and "covers" in every such band (line 535). |
| **3. Close remaining custody details in wrapper** | MAJOR | **CLOSED** | 244–247, 596–598, 729–731, 750–756 | Seed-and-salt encoding is explicitly defined: decimal seed base, ':', 64 lowercase hex characters, no newline (lines 729–731). Passphrase reaches binary on stdin via `srun` and is piped to `gpg` on fd 3 internally (lines 750–753). Successful integrity verification (`gpg` exit 0) is mandatory before decrypted products are used (lines 755–756). Narrow executability exception deadline is unified across rules paragraph (lines 245–246) and ST4 (lines 597–598) as before the first spend of the real PV seal. |
| **4. Make existing cap and completeness rules executable** | MAJOR | **CLOSED** | 564–574 | Unique 128-bit hex intent ID embedded in Slurm job name `covfix_<phase>_<intent>` persisted before submission (lines 564–566) and reconciled via `sacct` against active/terminal jobs on reconnect (lines 567–569). Uncertainty keeps reservations open (line 570). Each expected toy ID accepted exactly once with verified complete product (line 571). Synthetic-seal test allocation and writer/readout priced and reserved under ledger from measured time (lines 572–573). Descriptive stress-run failures never block completed grades (line 574). |
| **5. Pin toy inputs and mode conventions** | MAJOR | **CLOSED** | 463–466, 622–625, 823–827 | Full 64-character sha256 digests bound for `genie_mec`, `nuwro`, `gibuu`, and `projections.json` (lines 463–466). Five lateral endpoint differences pinned by sha256 from Part B list with orientation and X01 treatment pinned to `re2c_rollup.py` (lines 622–623). Rounding preflight on nominal inputs at login node before paid submission (lines 624–625). Degenerate edge convention (assigning whole cluster to lower-rank band) unified across construction, admission, and grading (lines 823–825). Deterministic basis via `numpy.linalg.eigh` with positive sign on largest component (lines 826–827). |

<!-- absence-ok: verbatim third-party read report -->
#### 1.2.3 Codex Rev 7 Dispositions Table (Rev 6 Fixes 1–12)

<!-- absence-ok: verbatim third-party read report -->
All 12 items from the Codex Rev 7 table survive as **CLOSED** under Rev 9:
1. **Drawn covariance:** **CLOSED** (lines 806–838, 953–960). Full-space $L$, normalized spread target, full 205-eigenvalue C-PSD, and sampling reconstruction check.
2. **Reference probabilities and cutoff error:** **CLOSED** (lines 933–945). Zero-bias Gaussian reference recipe, conservative Clopper–Pearson intervals, sentinels, no prose flag-size claims.
3. **Grading guard and operating claims:** **CLOSED** (lines 331–341, 962–975, 1007–1011). Analytic delta-method influence scores with sample SD ($N-1$), non-finite/zero SE refusal, stress runs descriptive only, operating-rate claims excised.
4. **P2 and PV budget:** **CLOSED** (lines 365, 572–573, 669–671). $K_C$ dropped, synthetic-seal test allocation and production writer/readout reserved under ledger from measured test time.
5. **Custody and manifests:** **CLOSED** (lines 582–599, 638–666, 746–766). Chained unfold input/output hashes, authenticated writer manifest, encrypted PG manifest, ciphertext-only publication, pinned GPG flags, cooperative assumption stated.
6. **Spent once:** **CLOSED** (lines 244–247, 582–600). Durable fsync and commit before decryption, terminal crash rules, single amendment deadline (first spend of real PV seal).
7. **ST1 and PX:** **CLOSED** (lines 484–491, 502–548, 800–804). Exact band-level influence scores, W2 first-time work counted once, itemized acceptance inputs, $F_A$ defined without $K_A$.
8. **Reservations and completeness:** **CLOSED** (lines 562–581, 604–609). 128-bit intent ID, `sacct` reconciliation, 409.22 ceiling, 100% complete products per expected ID.
9. **Outcomes:** **CLOSED** (lines 1013–1060). Exhaustive three-part taxonomy, separate unfunded sentence, `FAILS` precedence over `REFUSED`, explicit `challenge` and `ungraded` definitions.
10. **Toy law and A1 evidence:** **CLOSED** (lines 461–472, 618–632). Single §3.2 recipe, relative lateral carry with pinned sha256 digests and orientation, full A1 digests, nominal rounding preflight.
11. **Retained-space conventions:** **CLOSED** (lines 823–827, 924–926). Degenerate edge cluster convention unified across construction/admission/grading, deterministic eigenvector basis, outside-span whitened in single frame.
12. **Benchmark wording:** **CLOSED** (lines 266–268, 1045–1046). Rank drop correctly described, guarded margins labeled in outcome sentences.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Technical Audit: New Defects & Internal Contradictions

<!-- absence-ok: verbatim third-party read report -->
### 2.1 MAJOR Defect: Inexecutable Reference for Cut Diagnostic & Residual Rule when $K_A$ is Omitted

<!-- absence-ok: verbatim third-party read report -->
- **Locations:**
  - §5.2 lines 866–870 ([COVFIX-DECLARATION.md lines 866–870](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md#L866-L870))
  - §5.2 lines 871–876 ([COVFIX-DECLARATION.md lines 871–876](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md#L871-L876))
  - §5.3 line 888 ([COVFIX-DECLARATION.md line 888](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md#L888))
- **Issue:**
  In Rev 9, lines 800–804 successfully resolve the construction of $K_B$'s fluctuation block by defining $F_A$ without $K_A$:
  ```markdown
  Fluctuation block. The reference F_A is defined without K_A:
  - if ST1's exception was applied and its acceptance check passed, F_A is that corrected matrix's fluctuation block,
    whether or not K_A later passes P2;
  - otherwise (no firing, unexplained, unfunded, or acceptance failed), F_A = Q_rep.
  F_A is absolute at x_R, and it is the reference throughout §5.2.
  ```
  And lines 515–516, 559–560, and 1022–1024 explicitly state that when PX has no funded path, $K_A$ is omitted and the campaign continues with $K_0$ and $K_B$.
  
<!-- absence-ok: verbatim third-party read report -->
  However, in lines 866–876, the cut diagnostic and the residual rule still explicitly and exclusively reference $K_A$:
  ```markdown
  K_B = V_F + C_b at x_R, carried by §2's formula. It must pass C-PSD and print its cut diagnostic against K_A's:
  - the kept sets under §2's cut, which is referenced to each candidate's own λ₁(V_F);
  - the kept modes of K_A outside K_B's kept span, and their maximum residual;
  - the smallest kept and the largest dropped eigenvalue.

<!-- absence-ok: verbatim third-party read report -->
  Residual rule (K_B against K_A only):
  - Only K_A's well-determined modes are checked, those with λ_i ≥ 1e-6·λ₁(F_A), evaluated at x_R.
  - With U_A,well their orthonormal basis and P_B,kept the orthogonal projector onto K_B's kept span, K_B is not
    admissible if the directed residual ‖(I − P_B,kept) U_A,well‖₂ exceeds 0.1.
  ```
  In §5.3 line 888, candidate admission at P2 requires: *"It must also pass C-PSD, and, for K_B, §5.2's residual rule."*
  
<!-- absence-ok: verbatim third-party read report -->
  If ST1 fires and PX is unfunded (or if acceptance fails, or firing is unexplained), $K_A$ was omitted / not formed. At P2, an automated execution script evaluating $K_B$'s admission has no candidate named $K_A$. If the script looks for `K_A`, it will raise an error or crash. If the script skips the residual rule because the heading states `(K_B against K_A only)`, $K_B$ is admitted without passing the mandatory residual rule. If the script attempts to evaluate against $K_0$, it lacks textual authority because lines 866–874 do not state that $K_0$ serves as the reference candidate when $K_A$ is omitted.
  
<!-- absence-ok: verbatim third-party read report -->
  Codex explicitly raised this in Rev 8: *"Define the reference as the accepted corrected matrix when one exists and K_0 otherwise. Use that reference throughout §5.2, even if an accepted K_A later fails P2."* While Rev 9 defined $F_A$, it left the total reference candidate undefined in lines 866–874.
- **Severity:** **MAJOR**
- **Surgical Fix:**
  In §5.2 lines 866–874, define the reference candidate $K_{\mathrm{ref}}$ as $K_A$ if formed, and $K_0$ ($Q_{\mathrm{rep}} + C_{\mathrm{model\_abs}}(x_R)$) otherwise, and update the diagnostic and residual rule to reference $K_{\mathrm{ref}}$:
  1. In line 866, change:
     `print its cut diagnostic against K_A's:`
     to:
     `print its cut diagnostic against the reference candidate's (K_A if formed, else K0):`
  2. In line 868, change:
     `- the kept modes of K_A outside K_B's kept span, and their maximum residual;`
     to:
     `- the kept modes of the reference candidate outside K_B's kept span, and their maximum residual;`
  3. In line 871, change:
     `Residual rule (K_B against K_A only):`
     to:
     `Residual rule (K_B against the reference candidate only):`
  4. In line 872–873, change:
     `- Only K_A's well-determined modes are checked, those with λ_i ≥ 1e-6·λ₁(F_A), evaluated at x_R.`
     `- With U_A,well their orthonormal basis and P_B,kept the orthogonal projector onto K_B's kept span...`
     to:
     `- Only the reference candidate's well-determined modes are checked (K_A if formed, else K0), those with λ_i ≥ 1e-6·λ₁(F_A), evaluated at x_R.`
     `- With U_ref,well their orthonormal basis and P_B,kept the orthogonal projector onto K_B's kept span...`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 2.2 MINOR Defect: Notation Discrepancy in Scenario D2 Formula (§6.2 Line 970 vs Line 957)

<!-- absence-ok: verbatim third-party read report -->
- **Locations:**
  - §6.2 line 957 ([COVFIX-DECLARATION.md line 957](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md#L957))
  - §6.2 line 970 ([COVFIX-DECLARATION.md line 970](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix9/inputs/COVFIX-DECLARATION.md#L970))
- **Issue:**
  Line 957 explicitly states:
  `V₊ is the covariance actually sampled, and it is the one used for F_exp's drawn part, the cutoff draws and the stress runs.`
  However, in the descriptive stress run scenario D2 (line 970), the formula for $a_R$ writes:
  `where a_R = (1/ndf_R) Σ_{i∈R} u_iᵀ V_drawn u_i / λ_i; defined if a_R > 0;`
  Because stress runs are descriptive only and veto nothing (line 974), and eigenvalues below $10^{-12}\lambda_{\max}$ contribute negligibly, this has no numerical impact on any decision or bar. However, for strict algebraic consistency with line 957, the formula should reference $V_+$.
- **Severity:** **MINOR**
- **Surgical Fix:**
  In line 970, replace `V_drawn` with `V₊`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Binding Readiness & Conclusion

<!-- absence-ok: verbatim third-party read report -->
Draft Rev 9 represents an outstanding technical achievement. It incorporates all major policy cuts mandated by the director:
- excises surrogate testability vetoes and operating-rate claims;
- drops $K_C$ and outcome C;
- adopts a clean, single Gaussian reference law with full 205-mode C-PSD and sampling factor reconstruction checks;
- locks down custody via chained input/output hashes, authenticated manifests, Slurm stdin passphrase piping to internal GPG fd 3 with integrity verification, and durable spend fsyncs;
- binds the full-space spectral map $L$ and normalized pooled spread ratio $\hat{f}_R$; and
- protects baseline challenge reporting via affirmative `FAILS` precedence in §6.4 and §7.

<!-- absence-ok: verbatim third-party read report -->
However, because a formal pre-registration declaration governs irreversible compute and cannot be bound with an ambiguous reference candidate in P2's admission rule for $K_B$ on the authorized unfunded path, the confirming technical read is **NO-GO**.

<!-- absence-ok: verbatim third-party read report -->
Applying the single surgical clarification to §5.2 lines 866–874 (and aligning $V_+$ in D2) will immediately render **Draft Rev 9.1 fully GO for binding**.
