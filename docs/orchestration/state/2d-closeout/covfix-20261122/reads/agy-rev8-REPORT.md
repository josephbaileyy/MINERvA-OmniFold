<!-- absence-ok: verbatim third-party read report -->
NO-GO

<!-- absence-ok: verbatim third-party read report -->
# Review of COVFIX Pre-Registration Declaration (Draft Rev 8)

<!-- absence-ok: verbatim third-party read report -->
**Reviewer:** Antigravity (agy) — Confirming Technical Read  
**Target:** [COVFIX-DECLARATION.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md) (Draft Rev 8, 2026-11-23)  
**Baseline Documents:**
- [rev7-to-rev8.diff](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/rev7-to-rev8.diff)
- [agy-rev7-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/agy-rev7-REPORT.md)
- [codex2-rev7-REPORT.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/codex2-rev7-REPORT.md)
- [DECISION-20261123.md](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/DECISION-20261123.md)  
**Report Destination:** `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/report.md`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## Executive Summary

<!-- absence-ok: verbatim third-party read report -->
Setting aside the three administrative binding prerequisites (§9 item 3: committed iris receipt, fresh PG session, and director's passphrase piping wrapper), **Draft Rev 8 is NO-GO for binding**.

<!-- absence-ok: verbatim third-party read report -->
Rev 8 faithfully adopts the director's scope ruling following the Rev 7 reviews:
1. If PX has no funded path, the ST1 branch cleanly ends at the construction finding and $K_A$ is omitted;
2. A single Gaussian reference law $N(0, V_{\mathrm{drawn}})$ with C-PSD and sampled-covariance controls replaces the hybrid band bank, remainder, and fallback;
3. The surrogate testability veto and all campaign operating-rate claims are excised; surrogate runs are descriptive stress tests only; PASS rests solely on the affirmative bars applied to the real toys; and $K_0$ is reported as observed;
4. Candidate $K_C$ and outcome C are dropped entirely;
5. Codex item 4 (single PV toy law recipe), agy's three MAJORs (bars summary in §9, N5 guard, D2 formula) and three MINORs ($\tilde{F}_R$ SE, PX scale note, D3 signs), and the outcome rows for "PV never ran" and "no challenge" are incorporated;
6. Custody adopts codex-school2's simpler form (one durable spend record, one authenticated writer manifest with chained unfold outputs, ciphertext hashes only published, pinned GPG flags, terminal rules, and the cooperative assumption stated).

<!-- absence-ok: verbatim third-party read report -->
However, rigorous inspection of the new diff and the resulting declaration reveals **one BLOCKING defect, two MAJOR defects, and three MINOR defects**:
1. **BLOCKING (Suppression of Baseline Challenge via Precedence in §6.4 & §7):** In §6.4 (line 920), `REFUSED` precedes `FAILS` in the verdict precedence table. In §7 (line 955), `REFUSED` is classified as `unchallenged`. If $K_0$ observes a deficit on the real toys ($M - h > 1.25$ or under-flags), but encounters a control refusal (e.g. §6.2's 20,000-draw check fails), $K_0$'s verdict becomes `REFUSED`, classifying the baseline as `unchallenged` and suppressing all candidate adoptions. This directly contradicts line 928 (*"K0's verdict is reported as observed. No control or simulation can suppress an observed deficit"*).
2. **MAJOR (Logical Contradiction in §7 Part 1 Outcome Template):** Lines 943–945 state: *"A construction defect in <block>'s builder was found... the corrected block passed the acceptance check. Then whether K_A was eligible at P2, or 'PX had no funded path, and K_A was omitted for this run'"*. The acceptance check is executed on Perlmutter as part of phase PX (§3.3 lines 471, 494–495). If PX had no funded path, PX never ran, no block was regenerated, and the acceptance check was never performed. Asserting that the acceptance check passed when PX was unfunded is a direct logical impossibility.
3. **MAJOR (Passphrase Piping Contradiction: Slurm `srun` Stdin vs GPG `passphrase-fd 3`):** Lines 692–693 state: *"The passphrase is on fd 3 from the director's wrapper, and the payload streams on stdin and stdout: gpg ... --passphrase-fd 3"*. However, lines 585, 586, and 685 explicitly specify that the passphrase reaches the remote task via a pipe into the binary's stdin (`srun ... forwards stdin to the task`). Slurm's `srun` does not forward arbitrary file descriptors like fd 3 across nodes. The binary must receive the passphrase on stdin (fd 0) and pipe it internally to `gpg`'s fd 3 while streaming payload on `gpg`'s stdin/stdout.
4. **MINOR (Notation Inconsistency in §3.3 Line 450):** Line 450 writes `band mean Ā_R/B̄`, suggesting a ratio of band sums, whereas lines 447, 452, 455, and the table define the reading as the band mean of per-mode ratios $\frac{1}{\mathrm{ndf}_R}\sum_{i \in R} \hat{A}_i/\hat{B}_i$ with derivative $-\hat{A}_i/\hat{B}_i^2$.
5. **MINOR (Stale "no challenge" Outcome Reference in §5.1 Line 735):** Line 735 cites `and the outcome is "no challenge" (§7)`, but in §7 the baseline verdict is named `no deficit shown` (line 953) and the Part 3 table row is named `descriptive only` (line 969).
6. **MINOR (Stale "the k rule" Reference in §3.3 Line 499):** Line 499 lists `, the k rule` among elements ST1's exception may not change, even though $K_C$ and the $k$ rule were dropped.

<!-- absence-ok: verbatim third-party read report -->
These surgical defects must be corrected before cryptographic sealing and binding.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 1. Disposition of Surviving Findings from Rev 7 Reports

<!-- absence-ok: verbatim third-party read report -->
Per the director's scope ruling, items removed by the ruling (the testability veto, campaign operating-rate bounds, band bank, remainder, fallback, $K_C$, outcome C, and heavy custody) are not re-raised; rev 8 is judged as scoped.

<!-- absence-ok: verbatim third-party read report -->
### 1.1 Findings from agy-rev7-REPORT.md (§3.1)

<!-- absence-ok: verbatim third-party read report -->
| Finding | Severity (Rev 7) | Status in Rev 8 | Rev 8 Lines | Disposition Analysis |
|---|---|---|---|---|
| **Finding 1: Contradiction in §9 Policy Bar Summary** | MAJOR | **CLOSED** | 1026–1031 | Old line 1029's stale text (*"testability at 0.20 false-FAIL and 0.10 deficit pass"*) was completely excised. Line 1030 now aligns with the scoped bars: `- §6.2's sampled-covariance check at 0.05;`. |
| **Finding 2: Dimensionally Broken Variance Addition for ST1 N5 Guard** | MAJOR | **CLOSED** | 450–455 | The dimensional addition of covariance-squared $2(u_i^\top S1_B u_i)^2/(R-1)$ was replaced by band-level influence scores using the delta method on the band mean of ratios. Toy-side and replica-side ensemble variances add under conditional independence, with the replica-side influence term using derivative $-\hat{A}_i/\hat{B}_i^2$. |
| **Finding 3: Incomplete Formula Specification for Scenario D2** | MAJOR | **CLOSED** | 901–903 | Explicit algebraic formulas are now bound: with $P_R = \sum_{i \in R} u_i u_i^\top$ in $V$'s basis, $\phi \to (I - P_R)\phi + \sqrt{1.25/a_R} P_R \phi$ at zero bias, where $a_R = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} u_i^\top V_{\mathrm{drawn}} u_i / \lambda_i$ (defined if $a_R > 0$). |
| **Finding 4: Omission of Band Spread $\tilde{F}_R$ in Influence Function Specification** | MINOR | **CLOSED** | 305 | Explicitly added: `and for a band F̃_R, SE(F_R^F)/F_exp,R;`. |
| **Finding 5: Stale All-Block Rebuild Node-Hour Figure in ST1 Scale Note** | MINOR | **CLOSED** | 484–485 | Updated to state: `rebuilding universe (with laterals), stat and c08, plus the redraw, is 202.35 node-h before diagnostics, or 240.35 if the N5 replicas are rebuilt too.` |
| **Finding 6: Omission of Explicit Sign Convention for D3** | MINOR | **CLOSED** | 904 | Both signs are now explicitly evaluated: `b = ±β w_j with β² = (1.25 − a)·ndf / (w_jᵀV⁺w_j)`. |

<!-- absence-ok: verbatim third-party read report -->
### 1.2 Findings from codex2-rev7-REPORT.md (§2: New Defects & Minimum Changes)

<!-- absence-ok: verbatim third-party read report -->
| Item | Severity (Rev 7) | Status in Rev 8 | Rev 8 Lines | Disposition Analysis |
|---|---|---|---|---|
| **Item 1: Grading guard executability & ST1 ratio uncertainty** | BLOCKING | **CLOSED** | 306–307, 450–455, 480–485, 495, 506 | Guard specifies sample SD (divisor $N-1$), non-finite/zero SE refusal, and approximate coverage description (306–307). ST1 uses band-level influence scores on the band mean of ratios, with toy and replica ensembles adding under conditional independence with derivative $-\hat{A}_i/\hat{B}_i^2$ (450–455). N4−N2 calculated on each side. Unfunded PX cleanly ends ST1 at construction finding with $K_A$ omitted (481–482). Reused inputs itemized (506). Acceptance check requires "covers" in every band (495). W2 first-time work counted once (483). |
| **Item 2: Fix spectral map & identify drawn covariance** | BLOCKING | **CLOSED** | 766–770, 884–893 | Scoped per director ruling (2) taking Codex's simpler change: one Gaussian reference law $N(0, V_{\mathrm{drawn}}(t))$ with $V_{\mathrm{drawn}} = V_F - U$ carried. Retained space C-PSD control and 20,000-draw sampled covariance check $\le 0.05$ bound. Constituent blocks mapped by $L$. Band bank, remainder, and fallback dropped. |
| **Item 3: Remove testability veto & rate claims** | BLOCKING | **CLOSED** | 880–881, 894–905, 909, 928, 930–934 | Testability veto excised; §6.2 stress runs are descriptive only and veto nothing (894–905). PASS rests solely on real toys (909). Operating-rate claims excised (§6.5). $K_0$ reported as observed (928). Reference probability shift described as changing probabilities (880–881). *(Note: Precedence interaction between REFUSED and FAILS is audited as a new defect below).* |
| **Item 4: Specify one PV toy law** | BLOCKING | **CLOSED** | 570–575 | Single recipe in §3.2 referenced: 38 bands on reco/truth, lateral and norm on unfolded output, sim on unfolding side, Poisson on pseudo-data. Lateral carried in relative form from Part B products without remake. Draw order pinned to `cov2d.draw`. |
| **Item 5: Chained unfold outputs & durable custody** | BLOCKING | **CLOSED** | 538–550, 591–607, 689–703, 712–714 | Spend durably fsynced and mirror-committed before plaintext release under lock (539–540). Terminal crash rules (541–546). Plaintext hashes never published, held in encrypted PG manifest (689–691). Authenticated writer manifest (591–593). Unfold compute jobs append chain records verifying (toy ID, pseudo-data hash, output hash, invocation hash) before readout decryption (600–607). Pinned GPG flags (694–695). Cleanup of enumerated paths (594–595). Cooperative assumption stated (712–714). *(Note: fd 3 piping over srun is audited as a new defect below).* |
| **Item 6: Outcome table for stopped & completed campaigns** | MAJOR | **CLOSED** | 853, 940–980 | Three-part taxonomy updated: Part 1 includes unfunded PX branch; Part 2 includes `unchallenged` and `ungraded`; Part 3 includes `none, with a challenge`, `descriptive only`, and `none, PV never ran`. Policy on baseline challenge gating A and B sentences stated explicitly (960–961). In-sample disclosure tailored to candidates that use them (972–975). Readings reported separately per truth and band (853). UNRESOLVED explained as sampling ambiguity only when unresolved across labels (978–980). *(Note: Part 1 unfunded acceptance phrasing is audited as a new defect below).* |
| **Item 7: Simplify $K_C$ & close execution choices** | MAJOR | **CLOSED** | 522–534, 556–561, 826–827, 859–861 | Candidate $K_C$ and outcome C dropped per director ruling (4) (826–827). Outside-span fraction whitened in same frame at $x_R$ (859–861). Reservation ledger under `flock` with pre-submission intent persistence and sacct reconciliation bound (522–534). 100% completeness required (556–561). |

<!-- absence-ok: verbatim third-party read report -->
### 1.3 Codex Rev 7 Table (Rev 6 Fixes 1–12)
All 12 items from the Rev 6 table survive either as CLOSED in Rev 7 or are CLOSED under the director's Rev 8 scope:
- **Fix 1 (Drawn covariance):** CLOSED via $V_{\mathrm{drawn}} = V_F - U$ under single Gaussian law with controls (766–770, 884–893).
- **Fix 2 (Fallback probabilities & cutoff error):** CLOSED in Rev 7; shift wording corrected in Rev 8 (880–881).
- **Fix 3 (Calibrate guard & rate claims):** CLOSED via analytic delta-method guards with sample SD (306–307) and removal of rate claims (930–934).
- **Fix 4 (Budget P2 & PV):** CLOSED by dropping $K_C$ and making surrogate runs descriptive (209–210, 826–827).
- **Fix 5 (Custody & manifests):** CLOSED via Codex simpler form with authenticated writer manifest and chained unfold records (591–607, 689–703).
- **Fix 6 (Spent once):** CLOSED via durable fsync/commit spend record before decryption and terminal rules (538–550).
- **Fix 7 (ST1 & PX):** CLOSED via band-level influence scores (450–455) and unfunded PX stop rule (481–482).
- **Fix 8 (Reservations & sample integrity):** CLOSED via serialized ledger, 409.22 ceiling, and 100% completeness rule (522–534, 556–561).
- **Fix 9 (Outcome scope & exhaustiveness):** CLOSED via exhaustive three-part taxonomy covering stopped/completed campaigns (940–980).
- **Fix 10 (Toy specification & A1 evidence):** CLOSED via shared §3.2 recipe, relative lateral fallback carry, and pinned draw order (570–575).
- **Fix 11 (Retained-space conventions):** CLOSED via dropping $K_C$ and whitening outside-span in same frame at $x_R$ (859–861).
- **Fix 12 (Benchmark descriptions):** CLOSED in Rev 7; guarded margins labeled in outcome sentences (966–967).

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 2. Technical Audit of New Machinery in Rev 8

<!-- absence-ok: verbatim third-party read report -->
### 2.1 Band-Level Influence Scores for ST1 (§3.3 lines 450–455)
- **Mathematical Formulation:**
  In ST1, the reading is the band mean of per-mode ratios:
  $$X_R = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} \frac{\hat{A}_i}{\hat{B}_i}$$
  where $\hat{A}_i = \hat{s}_i = \lambda_i v_i$ is the projected sample variance from the toys, and $\hat{B}_i$ is the denominator projection ($u_i^\top S1_B u_i$ for N5, or a fixed matrix projection for N2, N3, universe).
  - **Toy-Side Influence:** For toy $s \in \{1, \dots, N\}$, the influence on sample variance $\hat{s}_i$ is $\psi_{s,i}^A = \lambda_i [(z_{s,i} - m_i)^2 - v_i]$. Linearly propagating through the band mean:
    $$\psi_s^{\mathrm{toy}} = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} \frac{\lambda_i \left[ (z_{s,i} - m_i)^2 - v_i \right]}{\hat{B}_i}$$
    This accounts exactly for all mode-mode covariance across toys in band $R$.
  - **Replica-Side Influence (N5):** For replica $r \in \{1, \dots, R_{\mathrm{rep}}\}$, with denominator estimated from bootstrap replicas, the partial derivative with respect to $\hat{B}_i$ is $-\frac{1}{\mathrm{ndf}_R} \frac{\hat{A}_i}{\hat{B}_i^2}$. The replica influence score is:
    $$\psi_r^{\mathrm{replica}} = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} \left( -\frac{\hat{A}_i}{\hat{B}_i^2} \right) \cdot \mathrm{IF}(r; \hat{B}_i)$$
  - **Variance Addition:** Because toys and replicas are drawn independently, conditional independence guarantees that the sampling variances add:
    $$\mathrm{SE}^2(X_R) = \frac{\mathrm{sd}_s^2(\psi_s^{\mathrm{toy}})}{N} + \frac{\mathrm{sd}_r^2(\psi_r^{\mathrm{replica}})}{R_{\mathrm{rep}}}$$
  - **N4 − N2:** Computed independently on each side with fixed denominators ($u_i^\top \mathrm{universe} u_i$), and the two independent ensemble variances add.
- **Audit Assessment:** This is mathematically and dimensionally exact, eliminating the dimensional error in Rev 7.

<!-- absence-ok: verbatim third-party read report -->
### 2.2 The Gaussian Reference Law & Controls (§6.2 lines 884–905)
- **Gaussian Reference Law:** Errors are sampled as $e \sim N(0, V_{\mathrm{drawn}}(t))$ with $V_{\mathrm{drawn}}(t) = D_t (V_F - U) D_t$, with $U = L(C_{\mathrm{PL}} + c08)L^\top$.
- **C-PSD Control:** $V_{\mathrm{drawn}}(t)$ must satisfy $\lambda_{\min} \ge -10^{-12} \lambda_{\max}$ on its retained space, refusing the candidate at truth $t$ if violated.
- **Sampled Covariance Check:**
  $$\max_i \left| \frac{u_i^\top \hat{S} u_i}{\lambda_i} - 1 \right| \le 0.05$$
  over $V_{\mathrm{drawn}}$'s kept modes.
  - For $M = 20,000$ draws, along eigenvector $u_i$ with eigenvalue $\lambda_i$, $(u_i^\top e)/\sqrt{\lambda_i} \sim N(0, 1)$.
  - The sample variance has variance $2/M = 2/20000 = 10^{-4}$, so the standard deviation is $\sqrt{2/20000} = 0.01$.
  - The bound $0.05$ corresponds to $5.0\,\sigma$.
  - For $d \approx 204$ modes, the probability of exceeding $5\sigma$ by chance is $1 - (1 - 2\Phi(-5))^{204} \approx 1.17 \times 10^{-4}$ (less than 1 in 8,500). Across at most 3 candidates and 2 truths, false refusal probability is $< 0.07\%$. This is an exceptional, scale-invariant numerical check.
- **Descriptive Deficit Scenarios (D1–D3):**
  - **D1:** Scales $\phi$ by $\sqrt{1.25/a}$ where $a = \operatorname{tr}(V^+ V_{\mathrm{drawn}})/\mathrm{ndf}$, yielding $\mathbb{E}[M] = 1.25$.
  - **D2:** Total band projector $P_R = \sum_{i \in R} u_i u_i^\top$ scales $\phi \to (I - P_R)\phi + \sqrt{1.25/a_R} P_R \phi$ with $a_R = \frac{1}{\mathrm{ndf}_R} \sum_{i \in R} u_i^\top V_{\mathrm{drawn}} u_i / \lambda_i$, yielding $\mathbb{E}[M_R] = 1.25$ and leaving outer modes invariant.
  - **D3:** Shift $b = \pm \beta w_j$ with $\beta^2 = (1.25 - a)\mathrm{ndf}/(w_j^\top V^+ w_j)$, yielding $\mathbb{E}[M] = a + \beta^2(w_j^\top V^+ w_j)/\mathrm{ndf} = 1.25$.
- **Audit Assessment:** The mathematical and statistical definitions are fully closed and sound.

<!-- absence-ok: verbatim third-party read report -->
### 2.3 Custody Architecture, Writer Manifest & GPG Flags (§3.4 & §4.2)
- **Hiding Commitment:** Seed commitments use $\mathrm{sha256}(\mathrm{seed\ base} \parallel \mathrm{salt})$ with private random salt revealed only after readout.
- **Encrypted PG Manifest:** Plaintext hashes of seed-bearing job scripts and products are sequestered inside the encrypted PG manifest; only ciphertext hashes are published in `PG-SEAL.sha256`. This eliminates seed-guessing attack vectors.
- **Writer Manifest & Chain of Custody:** The exclusive-node writer generates an authenticated manifest binding pseudo-data file hashes and central inputs to the PG manifest digest and freeze digest. Unfold compute jobs append chain records:
  $$(\text{toy ID},\ \text{pseudo-data sha256 from manifest},\ \text{unfold output sha256},\ \text{bound invocation sha256})$$
  The readout verifies every chain record against the writer's manifest before decrypting graded truths.
- **Durable Spend Record:** Under lock, the wrapper appends `"spent"` for the original seal and role, fsyncs the record, and commits the mirror before releasing any plaintext. Crash after decryption is terminal.
- **GPG Invocations:**
  - Encrypt: `gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc`
  - Decrypt: `gpg --batch --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --decrypt`
  - Synthetic round trip and non-zero exit on MDC failure verified.
- **Audit Assessment:** The cryptographic and custody protocol is exceptionally tight, subject only to the Slurm stdin/fd 3 interface clarification identified below.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 3. Itemized New Defects & Surgical Fixes

<!-- absence-ok: verbatim third-party read report -->
### 3.1 BLOCKING Defect

<!-- absence-ok: verbatim third-party read report -->
#### Defect 1: Baseline Challenge Suppression via REFUSED Precedence in §6.4 & §7
- **Locations:**
  - §6.4 Table (lines 920–926) & line 928 ([COVFIX-DECLARATION.md lines 920–928](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L920-L928))
  - §7 Part 2 line 955 ([COVFIX-DECLARATION.md line 955](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L955))
- **Issue:**
  In §6.4, the verdict precedence table specifies: *"Read in this order; the first condition that holds is the verdict:"*
  - Row 1 is `REFUSED`: *"a control refuses the candidate at either truth: §6.2's checks, a non-positive F_exp, the carry checks (§2), or C-PSD"*
  - Row 2 is `FAILS`: *"at either truth: M − h > 1.25 or a total band does so; P-3 or P-4 flags 'under'; or F̃ or a band reads 'under'"*
  
<!-- absence-ok: verbatim third-party read report -->
  Line 928 states: *"K0's verdict is reported as observed. No control or simulation can suppress an observed deficit."*
  
<!-- absence-ok: verbatim third-party read report -->
  However, in §7 (line 955), Part 2 defines:
  `- unchallenged: K0 is INFLATED, UNRESOLVED or REFUSED;`
  
<!-- absence-ok: verbatim third-party read report -->
  If $K_0$ observes a deficit on the real toys ($M - h > 1.25$, which is expected for $K_0$ per line 734), but also fails a control (e.g., §6.2's 20,000-draw sampled covariance check fails on surrogate draws, or $F_{\exp} \le 0$), reading the precedence table in order classifies $K_0$ as `REFUSED`. Under §7 line 955, $K_0$ is then classified as `unchallenged`, which forces Part 3 into `descriptive only` (line 969) and suppresses any candidate adoption!
  This creates a direct contradiction with line 928 and revives the exact challenge-suppression loophole that the director's scope ruling (3) ordered removed.
- **Fix:**
  1. In §6.4 (immediately below the precedence table or in the table condition), add:
     `For K0, an observed deficit on the real toys (FAILS) takes precedence over REFUSED; no control or simulation can suppress an observed deficit.`
  2. In §7 (line 955), clarify:
     `- unchallenged: K0 is INFLATED, UNRESOLVED, or REFUSED without an observed deficit;`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 3.2 MAJOR Defects

<!-- absence-ok: verbatim third-party read report -->
#### Defect 2: Logical Contradiction in §7 Part 1 Outcome Template for Unfunded PX
- **Location:**
  - §7 lines 943–945 ([COVFIX-DECLARATION.md lines 943–945](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L943-L945))
- **Issue:**
  Lines 943–945 formulate the Part 1 construction finding template as:
  ```markdown
  - "A construction defect in <block>'s builder was found (a reproducing test fails on the old builder and passes on the
    corrected one); the corrected block passed the acceptance check." Then whether K_A was eligible at P2, or "PX had no
    funded path, and K_A was omitted for this run".
  ```
  Phase PX is explicitly defined in §3.3 line 471 as covering:
  `- the regeneration; the post-fix acceptance check; W2's first-time work...`
  And lines 494–495 define the acceptance check as:
  `That check is the firing row's reading recomputed with the regenerated block, in the same common basis, on the same toys or on the redrawn cell. It must read "covers" in every band.`
  If PX has no funded path (§3.3 line 481), PX is never bound and never executed. Therefore, no block is regenerated on Perlmutter and the acceptance check is never run. Asserting that *"the corrected block passed the acceptance check"* while simultaneously concluding that *"PX had no funded path, and K_A was omitted for this run"* is an impossible contradiction in the pre-registered reporting text.
- **Fix:**
  Replace lines 943–945 with two clean, mutually exclusive outcome sentences:
  ```markdown
  - "A construction defect in <block>'s builder was found (a reproducing test fails on the old builder and passes on the
    corrected one); the corrected block passed the acceptance check." Then whether K_A was eligible at P2.
  - "A construction defect in <block>'s builder was found (a reproducing test fails on the old builder and passes on the
    corrected one); PX had no funded path, so no block was regenerated, and K_A was omitted for this run."
  ```

<!-- absence-ok: verbatim third-party read report -->
#### Defect 3: Passphrase Piping Contradiction: Slurm `srun` Stdin vs GPG `passphrase-fd 3`
- **Locations:**
  - §3.4 line 585 & line 586 ([COVFIX-DECLARATION.md lines 585–586](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L585-L586))
  - §4.2 line 685 & lines 692–695 ([COVFIX-DECLARATION.md lines 685, 692–695](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L685-L695))
- **Issue:**
  Line 692 states:
  `The passphrase is on fd 3 from the director's wrapper, and the payload streams on stdin and stdout: gpg ... --passphrase-fd 3`
  However:
  - Line 685 states: *"It reaches a connect only on a pipe from the director's wrapper into the bound binary's stdin."*
  - Line 585 states: *"The wrapper ... pipes the passphrase on stdin."*
  - Line 586 states: *"srun --exclusive -N 1 <writer>, which forwards stdin to the task."*
  
<!-- absence-ok: verbatim third-party read report -->
  Slurm's `srun` connects standard streams (`stdin` on fd 0, `stdout` on fd 1, `stderr` on fd 2). Slurm does not multiplex or forward file descriptor 3 from the submission environment to a remote compute node.
  Therefore, the director's wrapper delivers the passphrase to the bound binary via `stdin` (fd 0). The binary holds the passphrase in memory, opens an internal pipe to `gpg` on fd 3, and feeds the passphrase to `gpg`'s fd 3 while streaming ciphertext/plaintext on `gpg`'s stdin/stdout. Stating that the passphrase is on fd 3 *from the director's wrapper* contradicts the Slurm invocation specification.
- **Fix:**
  Update line 692 to read:
  `2. Each product is encrypted with pinned flags. The passphrase received on stdin by the bound binary is piped to gpg on fd 3, while the payload streams on gpg's stdin and stdout:`

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
### 3.3 MINOR Defects

<!-- absence-ok: verbatim third-party read report -->
#### Defect 4: Notation Inconsistency in §3.3 Line 450 ("Ā_R/B̄")
- **Location:**
  - §3.3 line 450 ([COVFIX-DECLARATION.md line 450](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L450))
- **Issue:**
  Line 450 states: *"For each row's band mean Ā_R/B̄ (numerator per toy, denominator per replica or block)... by the delta method on the band mean of ratios."*
  The expression `Ā_R/B̄` denotes the ratio of band means $\frac{\bar{A}_R}{\bar{B}_R}$, which has derivative $-\frac{\bar{A}_R}{\bar{B}_R^2} \frac{1}{\mathrm{ndf}_R}$. This conflicts with line 447, line 452, line 455 (which explicitly specifies derivative $-\hat{A}_i/\hat{B}_i^2$), and the table header (*"band mean of the per-mode ratio"*), which define the reading as $\frac{1}{\mathrm{ndf}_R}\sum_{i \in R} \frac{\hat{A}_i}{\hat{B}_i}$.
- **Fix:**
  In line 450, change `band mean Ā_R/B̄` to `band mean of per-mode ratios (1/ndf_R) Σ_{i∈R} Â_i/B̂_i`.

<!-- absence-ok: verbatim third-party read report -->
#### Defect 5: Stale "no challenge" Outcome Citation in §5.1 Line 735
- **Location:**
  - §5.1 line 735 ([COVFIX-DECLARATION.md line 735](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L735))
- **Issue:**
  Line 735 states:
  `If K0 is VALIDATED at both sealed truths (§6.4), the comparison showed no need for a change at those truths, and the outcome is "no challenge" (§7).`
  In §7, there is no outcome row or verdict named `"no challenge"`. When $K_0$ is VALIDATED at both sealed truths, Part 2 reports `no deficit shown` (line 953), and Part 3 assigns the outcome `descriptive only` (line 969).
- **Fix:**
  In line 735, update the citation to read:
  `and the outcome is "no deficit shown" (descriptive only) (§7).`

<!-- absence-ok: verbatim third-party read report -->
#### Defect 6: Stale "the k rule" Reference in §3.3 Line 499
- **Location:**
  - §3.3 line 499 ([COVFIX-DECLARATION.md line 499](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-covfix8/inputs/COVFIX-DECLARATION.md#L499))
- **Issue:**
  Line 499 states:
  `It may not change any bar, seed, the validation family, the §5.2 factor rule, C_b's rule, the k rule, or §7's order.`
  Candidate $K_C$ and the $k \in \{25, 50, 73\}$ rule were excised from Rev 8 per director ruling (4).
- **Fix:**
  In line 499, delete `, the k rule`.

<!-- absence-ok: verbatim third-party read report -->
---

<!-- absence-ok: verbatim third-party read report -->
## 4. Conclusion & Binding Readiness

<!-- absence-ok: verbatim third-party read report -->
Draft Rev 8 achieves major structural convergence by implementing the director's scope reductions: eliminating surrogate testability gates and operating-rate bounds, adopting a clean single Gaussian reference law with C-PSD and sampled covariance controls, excising $K_C$, tightening custody via chained manifests and durable spend fsyncs, and formulating band-level influence scores for ST1.

<!-- absence-ok: verbatim third-party read report -->
However, because a formal pre-registration cannot be bound with:
- a precedence flaw in §6.4 and §7 that could inadvertently suppress an observed baseline challenge on real toys;
- a logically contradictory outcome sentence in §7 Part 1 asserting that an unfunded acceptance check passed; and
- an executable discrepancy in Slurm `srun` passphrase delivery on fd 3 vs stdin,

<!-- absence-ok: verbatim third-party read report -->
the confirming technical verdict is **NO-GO**.

<!-- absence-ok: verbatim third-party read report -->
Applying the six targeted, surgical edits detailed in Section 3 will immediately render **Draft Rev 8.1** ready to bind.
