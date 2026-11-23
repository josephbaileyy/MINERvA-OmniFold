<!-- absence-ok: verbatim third-party read report -->
NO-GO

Draft rev 2 should not be bound. The rev-1 blockers on the validation twin, B3, the per-mode max, the N5 skip, and the missing PSD projection are closed in the text. Two new blockers replace them: the fluctuation matrix subtracts the wrong block from the wrong covariance, and outcome A's amendment path contradicts the freeze of §5–§7. The price products, the split identity, the C_b rank claim, and the §6.4 union bounds check out. The §6.4 sigma labels are swapped, and that swap does not move the bounds.

Line numbers are from `inputs/COVFIX-DECLARATION.md`.

---

## 1. Rev-1 BLOCKING and MAJOR findings

### Grok

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
| finding | status | where it stands |
|---|---|---|
| B1 validation twin; spent tunes choose | CLOSED | G18_10b is gone (22–23, 248–252). A tune that uses both the CCQE class and the 2p2h class of one spent tune stops PG (268–269). Bars and k read N4 and A1p only (315–317, 369–377). G18 and AR23 still enter C_b (340–345), which is building, and the review allowed building. |
| B2 custody | CLOSED | Fresh session that has not read COV2D, T2A, G2R, REGRADE, or §5–§7, named at binding (274–276, 502–505). Seeds pre-committed (278, table at 165–173). HPSS htar plus hashverify required; a missing ciphertext stops the study and is not regenerated (293–295). Hashes use O_NOATIME (285). Logs are booleans; physics stays in sealed meta (280–282). Encryption replaces atime (284–291, 300–303). |
| S-ST1 N5 skip; KI 85 | CLOSED | N5 always runs (35, 169, 184). No N1 or N2 label is a construction error (35, 196–197). Binding N5 needs Joseph to supersede the deferral (498–500). The deferral sentence in KI 85 matches that paraphrase. |
| D2 / B3 φ floor | CLOSED | Deleted (26). No φ grid remains. |
| D1 max and Ledoit–Wolf | CLOSED | Per-band factor, no per-mode max, no Ledoit–Wolf (27–29, 328–337). N4, A1p, and PV draw the same full source list (32–33, 158–163, 226). |
| F1 SuSAv2 overlap | CLOSED | 258–260 matches FD-F1-REPORT.md §1.3 and the tunes page: G21_11* uses SuSAv2 QE and 2p2h; AR23_20i_00_000's 2p2h is `SuSAv2MECPXSec`; both spent tunes use `NievesQELCCPXSec`. |
| F2 nearest GENIE 2.12 | CLOSED | The neighbour claim is gone. G18_02a is only the fallback if 02b is absent (250). The tunes page identifies G00_00b_00_000 as the preserved v2.12 Default+MEC tune, and the draft does not use it. |
| F3 KI 85 0.661 | CLOSED | 0.661 and 0.44 are not used. The header's "quoted exactly" (50) overstates a paraphrase; see M-11. |
| F4 tune_v1 and `_sq` | CLOSED | Vertices are genie_mec, nuwro, gibuu (172), matching `pv2d_report_tables_excerpt.py` `VERTICES`. `tune_v1` is the r=1 control in `pv2d_analyze_head.py`; `_sq` files are the ρ² fallbacks in `make_ratios_excerpt.py`. Both are dropped (51). |
| F5 b1 had not run | CLOSED | b1-REPORT.md records a completed projection (code `a843ae65`, exit 0). The inventory cites that report. |
| F6 τ "cannot move any reading" | PARTLY CLOSED | The claim is gone. τ = 0.0098 and 142 kept modes (78–79) match `regrade_2d_G18.json` (τ 0.0097675, `C_T_kept_modes_outside_C_prime_kept_span` 142) and AR23's τ 0.0097667. The cut diagnostic is required (80, 347–350). A large residual is still not a stop, and the reason given is false (351–352). That remainder is N-4. |
| F7 balance 725.6 | CLOSED | Cited as the director's 2026-11-22 message, marked uncommitted, and binding requires a committed iris receipt (132–134). Half of 725.6 is 362.8. |
| B3 spent-once | PARTLY CLOSED | One JSON, no per-toy arrays, a second invocation refused, two tunes only, later seal may be impossible (209–218). The ST1 amendment reopens the rules after data. That remainder is N-2. |
| D3 nominal-only fluctuation | CLOSED | A1p is the perturbed-response ensemble at the three vertices and enters the factor (30–31, 173, 329–331). |
| D4 lateral and normalization | CLOSED | Both are in the full source list (158–163) and in every PV toy (232–233). |
| D5 one-sided bars | CLOSED | Joint "over" and band "over" refuse at P2 and at PV; any under-flagged mode refuses (42–44, 369–373, 407–411). |
| D6 A1 called held-out | PARTLY CLOSED | A1f and A1p are marked in-sample, and PV is the held-out cell (177–179). The split stays descriptive (403). There is still no pass bar that the bias block matches the held-out bias. See M-16. |
| D7 band "covers" | CLOSED | Bands use the same edges and the same interval rule as M (104–113). |
| S2 no floor on k | CLOSED | k ≥ 10, and a band under 10 modes is dropped (98–99, 362–363). The floor arithmetic holds for the claim that is printed; the sigma labels do not (N-10). The measurability branch is outside the floor (M-14). |
| S3 Gaussian 0.6827 null | CLOSED for PV | PV uses the draw-matched phase-N null (394–399). P1's N-cells use the Gaussian null and say so (400). The union bound replaces an independence claim (439–441). P2 computes the false-FAIL rate and refuses a candidate above 0.20 (442–444). The blindness sentence attached to that null is a new defect (N-6). |
| P2 no cumulative ceiling | CLOSED | ST6 sums `covfix_` sacct and refuses above Joseph's approved total (137–139, 223). P1 is two waves, and W2 waits on the W1 reading (121–123). N3 is priced at 9.5. |

### agy

| finding | status | where it stands |
|---|---|---|
| BLOCKING-1 B3 tail scale | CLOSED | Same as Grok D2. |
| BLOCKING-2 max, rank, Ledoit–Wolf | CLOSED | Replaced by the band factor agy asked for (328–333). The SE in that guard is not defined (N-3). |
| BLOCKING-3 C_b not PSD | CLOSED | The positive-part projection is in the formula (342–344). Rank at most 5 is true: each S_t is a Gram matrix, so on the complement of the five mean vectors the quadratic form is ≤ 0, and the positive part has rank ≤ 5. |
| BLOCKING-4 N5 skip inversion | CLOSED | Same as Grok S-ST1. |
| BLOCKING-5 atime and G18_10b | CLOSED | Same as Grok B1 and B2. |
| BLOCKING-6 balance and un-gated batch | PARTLY CLOSED | The receipt is a binding prerequisite (133–134) and ST6 is a cumulative gate. A wave can still run past its priced charge until the next submission, because no per-job walltime is set (137–139). See M-13. |
| MAJOR-1 small-k guard | CLOSED for the top-k case | k ≥ 10 (362). At N = 300, SE(M) = √(2/3000) = 0.02582 and t_{0.975, 299} ≈ 1.9679, so h ≈ 0.0508, which is within the printed h ≤ 0.06. The printed sigma sides are reversed (N-10). |
| MAJOR-2 empty bands; P-4 at small k | CLOSED | Bands with fewer than 10 modes are dropped (98–99, 363). P-4 refuses any under-flag (373, 411). |
| MAJOR-3 sim-stat switch | CLOSED | The full source list always includes sim (158–163, 226). The ST1 rows subtract N2−N1 and N4−N2 (190–193). |
| MAJOR-4 admission ignores "over" | CLOSED | §5.4 refuses joint "over" and band "over" (371–372). |
| MAJOR-5 catalog exhausted in one pass | PARTLY CLOSED | The design uses two tunes and states that the v3_04_00 catalog may not supply a third family (217–218). No third qualifier is reserved. |

---

## 2. New defects in rev 2

### N-1. BLOCKING. The fluctuation part subtracts a block the cited Q_R does not contain.

Lines 88–89, 145–146, 321, 328.

COV2D-DECLARATION.md §1 defines Q_R = S5_R + C_PL_R, with C_model beside it. Adding C_model raises the median per-cell relative width from 6.41% (Q_R) to 7.90% (COV2D §13). The matrix that under-covered is C_T = C_univ + C_lat + C_norm + C_stat + C08 + C_model_abs, and C_model_abs = diag(x̂) C_model diag(x̂) with C_model the relative part-C matrix (COV2D §4.4). REGRADE §2 defines a fractional carry only for C_run.

The draft sets K0 to Q_R, sets F_Q = Q_R − C_model, and cites REGRADE §2 as the carry of every candidate. Part C's C_model is relative. Q_R and C_T are absolute and of order 10⁻⁷⁸ (`regrade_2d_G18.json`, C_run λ_max ≈ 5×10⁻⁷⁹). Subtracting the relative matrix from Q_R is a different object from removing C_model_abs from C_T. P0 stops if that difference fails C-PSD (145–146), so this definition either aborts the study or grades the wrong matrix. Line 328 then says F_A = K_A − C_model "is PSD by P0's check", which is P0's check only when K_A = Q_R.

Fix: write one block equation for K0. For the matrix that under-covered, subtract C_model_abs from C_T, and write the carry as V(t) = diag(x_t / x_ref) V diag(x_t / x_ref) for blocks that are already absolute at x_ref. Point that formula at the candidate, not at REGRADE §2.

### N-2. BLOCKING. Outcome A's amendment is forbidden by the freeze that is supposed to make spent-once real.

Lines 59–60, 200–201, 215–216, 457–458.

After binding, §5–§7 cannot be amended. The only exception is an executability fix that changes no number, bar, family, seed, or choice rule. ST1 sends "a fix" to the director as an amendment, and outcome A requires that fix to be amended in. A construction-error fix changes the covariance. K_A is defined in §5.1. The two rules cannot both be followed: either the fix is illegal and outcome A cannot happen, or the fix is an unscoped amendment after W1 has been read, which is the pre-PV hatch rev 1 called blocking.

Fix: one named exception. An ST1 amendment may change only the generator of the block named by the firing row. It may not change a bar, a seed, the validation family, k, or the §5.2 factor. It is written down before P2. Every other change to §5–§7 stays forbidden.

### N-3. MAJOR. The 3-SE guard on the pooled factor has no SE.

Lines 329–333, and the guard definition at 101–103.

f̂_R is the equal-weight mean of four ensembles: N4 at 200 toys and three A1p ensembles at 100. The rule scales a band only when f̂_R − 1 > 3·SE(f̂_R). Nothing says how that SE is computed. Section 2's guard is a 2,000-draw toy bootstrap of one ensemble, at seed 9_990_000. It does not define the SE of an equal-weight mean of four ensembles with different N, in a carried basis. An independent-mode calculation gives SE ≈ 0.0077 on R1 (3·SE ≈ 0.023). A bootstrap that ignores the unequal variances, or that treats the four ensembles as one pooled sample, gives a different threshold and a different V_F.

The phrase "unbiased by construction, with the 1/N divisor" matches the split identity. It does not match an unbiased variance: with divisor 1/N, E[v_i] = ((N−1)/N) σ², about 0.5% low at N = 200 and 1% low at N = 100. That bias sits inside the 3-SE gate and will not by itself flip the scale. The missing SE definition will.

Fix: write SE(f̂_R) as the toy-bootstrap SE of the equal-weight mean, resampling each ensemble inside itself, at a pre-committed seed, and state that the four ensembles are not assumed independent beyond that resampling.

### N-4. MAJOR. "C_b can only add" is false, so an ndf change is waved through on a wrong reason.

Lines 351–352. This is the open half of Grok F6.

The cut keeps λ_i > 10⁻¹² λ_1. Adding a PSD C_b can raise λ_1 by more than it raises a marginal eigenvalue, and it rotates the basis. ndf can fall. The kept-span residual can be large while the trace of C_b is small, which is the G18 regrade fact the draft itself cites (142 modes, max residual 0.99999, τ = 0.0098). The draft prints the diagnostic and does not stop.

Fix: delete "because C_b can only add". Pre-commit a residual bar. A kept mode of K_A whose component outside K_B's kept span exceeds that bar, or an ndf change, stops P2.

### N-5. MAJOR. ST1 can fire only in R1, and T2A's excess is in R2 and R3.

Lines 188–201, against the spreads at 75–77 (1.6 / 3.0 / 4.4 and 1.5 / 3.6 / 4.7).

Each block test is an R1 band mean. R2 and R3 are recorded and do not fire ST1. A data-stream or nuisance block that is wrong in the tail is then absorbed by f̂_R2 or f̂_R3 and reported as fluctuation rather than as outcome A. With the guard, a 66-mode band at N = 200 has an analytical SE near 0.01, so a real tail failure is not a close call.

Fix: any band with at least 10 modes can fire ST1, under the same guard.

### N-6. MAJOR. The draw-matched null is cited as phase N and also as blind to the truth. Phase N needs the truth.

Lines 381–386 and 394–399.

COV2D §5.2 builds the phase-N null from the tune's remade band-shift vectors and from a Gaussian that includes C_stat(T) + C_norm(T) + C08(T) + C_model_abs(T), before any toy error is read. Those shifts are functions of r_T. The draft says the null needs only the draw list and V, so it is computed blind at P2, and a candidate whose false-FAIL rate exceeds 0.20 does not go to PV. A null that follows the citation opens the seal at P2. A null that ignores r_u is not the cited procedure. The 0.20 refusal is then a decision taken with seal information, or a decision about a different null.

Fix: pick one. Either define an explicit null that uses carried nominal shifts and no r_u, and stop calling it phase N, or compute phase N inside the PV binary after decryption and before any residual is written, with the candidate list already frozen, so a 0.20 refusal cannot change §5.

### N-7. MAJOR. The guard is attributed to b1's declaration, and b1's guard is a different formula.

Lines 101–103.

b1-DECLARATION.md rev 2, lines 64–65, sets h = 2.7764451051977987 · sd / √5. That is t_{0.975, 4} for A2's five draws. It is not t_{0.975, N−1} times a 2,000-draw bootstrap SE, and seed 9_990_000 is not in that declaration. The formula in the COVFIX sentence is usable on its own. The citation tells an implementer to copy the wrong guard. This replaces rev 1's unsupported "b1 style" label with a specific false pointer.

Fix: drop the "as in b1" clause. Cite b1 only for the projection it ran. Keep the bootstrap sentence as COVFIX's own rule.

### N-8. MAJOR. Lean cell 4 cannot rest on A2 for all three vertices.

Lines 130–131.

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
A1f's truths are genie_mec, nuwro, and gibuu. IBUKT A2's seven truths are nominal, genie_mec, nuwro, bump, tilt, and within± (INVENTORY.md:83; OUTCOME-20261119-ibukt-a2.md). There is no GiBUU draw. Lean drops A1f and then has no fixed-response measurement at gibuu.

Fix: say that lean cell 4 has A2's five-draw means at genie_mec and nuwro only, and that gibuu has no fixed-response ensemble in the lean campaign.

### N-9. MAJOR. The passphrase is a file on the shared account the draft says the key is supposed to lock.

Lines 286–288, 297–298, 300–302.

The generating session has to hold the passphrase in order to encrypt, and the draft does not say how it arrives or how shell history, Slurm spool, and the environment are scrubbed when that session is retired. At PV the director writes the passphrase to a file for the life of the connect. Decryption goes to /dev/shm. Every session is the same Unix account, which the draft states. Mode bits do not hide a file from that account. Spent-once refuses a second invocation of the bound binary (213–214). It does not refuse a copy of the passphrase file or of /dev/shm.

Fix: deliver the passphrase on a pipe from the director's wrapper, wipe /dev/shm in the same binary, and scan the campaign directory for plaintext ratios and per-toy arrays before the job exits. A hit stops the study.

### What was checked and holds

Section 6.4, lines 424–444:

- SE(M) = √(2/(300·204)) = 0.00572, which rounds to the printed 0.006.
- A candidate with M_true > 1.25 + 3·SE (about 1.267) fails to land the whole interval inside [0.8, 1.25] with probability essentially 1. "Under" alone is the stricter event; the printed claim is "under or unresolved".
- P-3's two tails are each at most 0.025 for a strict binomial critical value. P-4's expected false under-flags are at most 0.025 by linearity, so P(at least one) ≤ 0.025. Per truth, 0.075 and 0.05 follow by the union bound. Over two truths, 0.15 and 0.10 follow the same way.
- At k = 10 and N = 300, h ≈ 0.0508, so "h ≤ 0.06" and "h ≈ 0.051" hold. The distance to 1.25 − h is 7.71σ. The distance to 0.8 + h is 5.77σ. Line 438 assigns 5.7σ to the high side and 7.7σ to the low side.

The split M = (1/ndf) Σ m_i² + F is exact under the 1/N divisor (87, 97, 403). The debias term S_t/(N_t − 1), with S_t defined at divisor N, is unbiased for bbᵀ: E[S_t] = ((N−1)/N) C and E[S_t]/(N−1) = C/N = Cov(b̂).

Prices, every n × 0.19 product, with no rounding in the cells:

| cell | product | printed |
|---|---|---|
| N1, N2, N4 | 200 × 0.19 and 150 × 0.19 | 38 and 28.5 |
| N5 | 400 × 0.19 and 300 × 0.19 | 76 and 57 |
| N3 | 50 × 0.19 | 9.5 |
| A1f | 180 × 0.19 | 34.2 |
| A1p | 300 × 0.19 | 57 |
| PV | 600 × 0.19 | 114 |
| P1 W1 | 38+38+76+9.5 and 28.5+28.5+57+9.5 | 161.5 and 123.5 |
| P1 W2 | 38+34.2+57 and 28.5+57 | 129.2 and 85.5 |
| P1 | | 290.7 and 209.0 |
| full total | 290.7+114 plus PG 1.3 to 2.0 | 406.0–406.7 |
| lean total | 209.0+114 plus PG 1.3 to 2.0 | 324.3–325.0 |

112.74/600 = 0.1879, printed as 0.188 (129). F1's 1.327500 node-h matches FD-F1-REPORT.md:143 (82).

---

## 3. The pooled per-band factor

Yes. The factor in §5.2 is acceptable under the review's refusal to scale the covariance until the two tunes pass.

The rejected procedure chooses a scale so that G18 and AR23 stop reading "under". f̂_R is a pre-registered average of centered spread ratios on N4 and on A1p at genie_mec, nuwro, and gibuu (329–331). G18 and AR23 do not enter it (336, 315–317). It is applied only when it clears a one-sided 3-SE gate, and it is never fit by searching until a bar passes. If the resulting K_B misses §5.4, K_B is refused (369–375, 508–510). Refusal does not raise the factor. That is an estimate of extra fluctuation on ensembles other than the two spent tunes. It is the fluctuation term Fix 1 asks for.

N-3 still has to define SE(f̂_R) before binding. An undefined SE does not turn this rule into the rejected scale. It makes the gate unreproducible.

---

## 4. Removing C_model and replacing it with C_b

The replacement is the right decomposition, and it double-counts the three vertices only if the subtracted block is not the block that was in the matrix. As written, that identification fails (N-1). Read as "remove the model piece from the fluctuation matrix and put the measured bias second moment in its place", the construction drops something specific and double-counts nothing.

C_model, in COV2D, is the covariance of the three PV2D shifts (GENIE+MEC, NuWro, GiBUU), carried as C_model_abs and used as a Gaussian fluctuation. It is not an unfolding bias. C_b averages the debiased outer products of unfolding means at those three A1p truths plus G18 and AR23 (340–344). The vertices therefore change role: their shift covariance leaves the fluctuation part, and their measured b̂b̂ᵀ enters the bias part. Those are different functions of the same truths. G18 and AR23 were not in C_model, so their terms are new. The centered spreads of the same A1p toys enter f̂_R through v_i, and the means enter C_b. The split q_i = m_i² + v_i keeps those two pieces from being added twice.

What it drops:

- Any direction of C_model orthogonal to the five measured bias vectors. The positive part has rank at most 5, so that drop is real. It is also what a bias block is: model difference that did not show up as an unfolding bias is not kept as fake fluctuation.
- A1f's fixed-response means. C_b uses A1p (340). For coverage at a perturbed response, A1p is the matching bias. A1f stays a diagnostic (177–178). Lean's claim that cell 4 survives on A2 is a separate defect (N-8).

The PSD projection zeros noise eigenvalues outside that span. It widens C_b relative to the indefinite unbiased matrix inside the span. That is the regularization agy's BLOCKING-3 required, and the rank claim at 344 is correct.

Weighting five truths equally lets the two spent biases dominate C_b if they are as large as the recorded χ². §5.4 then has to pass at nominal N4, which refuses a C_b so wide that nominal toys read "over". That limit should be stated next to §9.5. It is not a double-count.

---

## 5. What blocks binding, and what does not

BLOCKING:

1. N-1. Name K0's blocks and subtract C_model_abs from the matrix that actually contains it. Write the carry formula.
2. N-2. Confine the ST1 amendment to the named block, and leave the rest of §5–§7 frozen.

MAJOR, in this revision, before binding:

3. N-3. Define SE(f̂_R) for the four-ensemble mean.
4. N-4. Replace "C_b can only add" with a residual stop. This closes the rest of Grok F6.
5. N-5. Let R2 and R3 fire ST1.
6. N-6. Make the pre-PV null either blind and not called phase N, or phase N and inside the sealed PV binary.
7. N-7. Remove the false b1 guard citation.
8. N-8. Stop saying A2 covers gibuu in the lean campaign.
9. N-9. Keep the passphrase off a file the shared account can copy, and scan for plaintext at job end.

MINOR:

10. N-10. Line 438. The high side at k = 10 is 7.7σ (the edge 1.25 − h) and the low side is 5.7σ (the edge 0.8 + h). Both are negligible for the 0.075 budget. Separately, h ≈ 0.0508 meets h ≤ 0.06 and misses h ≤ 0.05; k ≥ 11 is the smallest integer with h ≤ 0.05 at N = 300. Fix the labels. Keep k ≥ 10 if 0.06 is the intended bar.
11. M-11. Line 50 says KI 85 is quoted exactly. Section 9 paraphrases the deferral and does not mention the same row's rule that no outcome changes a quoted band or a printed number before publication. The Joseph decision should supersede that sentence explicitly, because outcome A is such a change.
12. M-12. Lines 261–262 say the tunes page does not name G18_02's QE or 2p2h. The same page says G18_10 adds NAV QE and NSV 2p2h on top of G18_02. Quote that bullet. The probe and the exclusion rule can stay.
13. M-13. Lines 120 and 127 price PG from 1.3 node-h. The only measurement is 1.3275 (82). Raise the floor to 1.33. ST6 still needs a per-job walltime so a stalled wave cannot pass the priced-charge check and overrun before the next submission (agy BLOCKING-6's remaining piece).
14. M-14. Lines 357–361. The k ≥ 10 floor is stated for the top-k case. A measurability study can still supply a smaller k. Apply the same floor, or state that the P2 0.20 rate check is what refuses that branch.
15. M-15. Line 135. Each cap is below 362.8. The full caps sum to 468 and the lean caps sum to 378. ST6 on the approved total is what keeps the campaign inside the chosen total. Say that the cap sum is not itself under the half-balance.
16. M-16. Line 403 and the open half of Grok D6. The split is reported and decides nothing. Add a descriptive comparison of the held-out b̂b̂ᵀ with C_b, and keep it out of the PASS rule unless a later draft wants it as a bar.
17. M-17. Line 441. The 20% mark is still only "the director's request of 2026-11-22". It is not in this packet. Attach the request, or drop the number from the bound text until the receipt exists.
18. The floor sentence uses the χ² SE, while the operational guard uses a bootstrap SE (101–103, 362). Say so in the floor sentence. The §6.4 products 0.006, 0.051, 0.075, 0.05, 0.15, and 0.10 can stay.

The factor question in §3 is not a reason to refuse. The C_b replacement in §4 is not a reason to refuse once N-1 names the subtracted block. Binding waits on N-1 and N-2.
