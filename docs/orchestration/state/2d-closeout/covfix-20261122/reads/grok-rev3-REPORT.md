<!-- absence-ok: verbatim third-party read report -->
NO-GO

Draft rev 3 should not be bound. The rev-2 algebra and custody repairs are largely in the text. Four things still block binding: the residual stop rejects the candidates it is meant to gate; C_b is assembled in the wrong absolute frame and then carried; the one-sided total bar, fed by a sum that includes the spent G18 and AR23 biases, does not support outcome B's sentence; and the KI 85 fallback does not do what §9.1 says it does. Prices, the split identity, and the §6.4 union bounds check. The §6.4 claim that a candidate just above `1.25 + 3·SE` fails "not under" with probability near 1 does not.

Line numbers are from `inputs/COVFIX-DECLARATION.md`. Record numbers cited below are from the regrade JSONs, T2A's reading, the Q identity check, and COV2D's declaration.

---

## 1. Rev-2 BLOCKING and MAJOR findings

### Grok

| finding | status | where it stands |
|---|---|---|
| N-1 block equation and carry | PARTLY CLOSED | The illegal subtraction is gone. K0 is named: `V_F,0 = Q_rep`, `V_b,0 = C_model_abs(x_R)` (89–92). The carry is a formula, `V(t) = D_t V D_t` (94–98). Q's file, sha256, and the two block identities match `run2-NODE-SHA256-excerpt.txt` and `Q_rep-identity-check.txt` (80–85). What remains: the matrix that under-covered is remade `C_T` without `C_PL` (COV2D-DECLARATION.md:221–224; this draft says so at 89–90). K0 is the data-point reported matrix, `Q_rep + C_model_abs`, which includes `C_PL`. P0 compares the carry with remade `C_T` and does not stop (173–176). |
| N-2 ST1 amendment | PARTLY CLOSED | There is one named exception, bound before P2, and it may not change a bar, a seed, the family, the factor rule, `C_b`'s rule, the k rule, or the §7 order (51–53, 232–236). It also allows "inputs", and it is not bound before the W2 ensembles that determine `f̂_R`. See N3-4. |
| N-3 SE(f̂_R) | CLOSED | `f̂_R` carries `N/(N−1)`, and `SE(f̂_R)` is the SD over 2,000 joint bootstrap replicates, each ensemble resampled inside itself, seed `9_991_000` (378–386). |
| N-4 residual stop | CLOSED as a replacement of the false sentence | The "can only add" sentence is gone. A stop is pre-committed (411–412). The stop's level is a new blocker. See N3-1. |
| N-5 ST1 bands | CLOSED | Any band with at least 10 kept modes can fire, under the same guard (219, 221–226). |
| N-6 draw-matched null | PARTLY CLOSED | The null runs inside the PV binary after decryption, with candidates frozen, and a 0.20 result cannot change §5 (447–450, 462–468). The inputs are still "u's draw list". COV2D phase N needs the tune's remade band-shift vectors and a Gaussian whose pieces sum to the graded matrix (COV2D-DECLARATION.md:259–263). §6.1 also runs that procedure at N4 and A1p (469–470), where those shifts are not produced. See N3-2. |
| N-7 b1 guard citation | CLOSED | The guard is stated as COVFIX's own rule (121). b1's formula is not cited. b1-DECLARATION.md:64–65 remains `t_{0.975,4} · sd/√5`. |
| N-8 lean gibuu | CLOSED | Lean cell 4 is A2's five-draw means at genie_mec and nuwro only, and gibuu has no fixed-response ensemble (152–153). OUTCOME-20261119-ibukt-a2.md has those two truths and no GiBUU row. |
| N-9 passphrase file | PARTLY CLOSED | The passphrase is piped, `/dev/shm` is wiped, graded truths are encrypted, and a scan is specified (274–282, 331–333). The PV scan does not cover `/dev/shm` or per-toy arrays, and the writer runs on a shared login node. See N3-5. |

### agy

| finding | status | where it stands |
|---|---|---|
| BLOCKING-1 iris receipt | OPEN | Still uncommitted. The text parks it correctly (154–156, 583). Not re-raised below. |
| BLOCKING-2 KI 85 waiver | PARTLY CLOSED | §9.1 names both sentences in KNOWN_ISSUES row 85 (the deferral, and no change to a quoted band or printed number) and requires a decision before N5 and outcome A (576–580). The fallback does not implement that claim. See N3-4b. |
| BLOCKING-3 PG session and passphrase | OPEN | Still unnamed, and binding still requires both (322–324, 584–585). Not re-raised below. |
| MAJOR-1 `/dev/shm` vs Slurm | CLOSED | Compute jobs unfold precomputed pseudo-data and do not read login-node `/dev/shm` (273–281). The login node itself is a new hole. See N3-5. |
| MAJOR-2 `1/\|F\|` dilution | CLOSED as dilution | `C_b` is the sum, and nominal closure bias is in the family (395–405). The sum creates the envelope in §2 below. |
| MAJOR-3 intermediate arrays | CLOSED for residual pre-grading | Per-toy graded truths are encrypted before they touch disk, and the readout decrypts in-process (277–282). Unfolded `σ̂` on disk is not an error without those truths (284–285). Reconstructing `r_u` from the writer is N3-5. |

---

## 2. The structure: carry, blocks, and outcome B

The skeleton is the right decomposition. `K0 = Q_rep + C_model_abs(x_R)` puts the adopted fluctuation matrix and the model piece side by side (89–92). One relative carry for every block, `V(t) = D_t V D_t` with `D_t = diag(x̂_t / x_R)`, is the right kind of formula (94–96). Every candidate is a fluctuation block plus a bias block (104, 375, 405). PASS requires the fluctuation piece two-sided ("covers", and no band "under" or "over") and the total one-sided ("not under") (431–434, 478–482). Joint "over" and per-mode "over" do not fail a candidate (473–474, 496–497). That split matches Fix 1's `E[eeᵀ] = C_fluct + bbᵀ`, provided the two blocks are in one absolute frame. They are not (§3, N3-2b).

**The one-sided total lets a bad bias block through.** P-2 fails only when `M − h > 1.25`. An arbitrarily wide bias block makes `M` small and passes. P-3 and P-4 are evaluated on `V = V_F + V_b`, so the same widening enlarges the joint region and the mode intervals along the bias. They do not put a ceiling on the bias block. P-1 does not see `V_b` at all: it is the centered spread against `V_F`. A fluctuation block that is too wide or too narrow still fails P-1. A bias block that is merely too wide does not fail anything in §6.2.

**The sum makes that hole decisive for K_B at the validation truths, inside the span of the six.** `C_b` sums six debiased outer products, including G18 and AR23 (395–397). For the undebiased sum, `b̂_tᵀ C_b⁺ b̂_t ≤ 1` for each member (401). That bound is a total χ², not a χ² per ndf. T2A, against `C_T`, gives a bias part of 13.61 per ndf at AR23 (ndf 204) and 20.97 per ndf at G18 (ndf 205): quadratic forms about 2.8×10³ and 4.3×10³. Once those vectors sit in the sum, a held-out bias parallel to them and of the same size contributes O(1) to the total χ² against `C_b`, which moves `M` by about `1/ndf ≈ 0.005`. P-2 starts to fail only when that quadratic form exceeds about `0.25 × ndf ≈ 50`, on the order of seven times the G18 bias if the held-out vector is parallel to it, or a component orthogonal to all six with that same form against `V_F`. A held-out GENIE bias that lives in the same poorly determined directions T2A already measured (77% and 87% of the mean-error part beyond rank 73) is the case the sum covers. For that case the total bar, the joint bar, and the per-mode bar pass by the size of the spent failures. The pass is not an identity: a large new direction still fails.

**The two-sided fluctuation bar is a real test, and it is what outcome B would actually certify.** P-1 asks `V_F` to match the centered scatter at both sealed truths, overall and by band, inside the guarded label `[0.8, 1.25]` (479). `f̂_R` is not fit to those truths (390–392). Refusal does not raise the factor (589–590). So a VALIDATED K_B certifies:

- `V_F`, the band-scaled reported matrix `Q_rep` (including undrawn `C_PL`), matches held-out centered scatter to that label;
- `V_F + C_b` does not under-cover the total second moment, where `C_b` is an in-sample envelope (the positive part of the sum of six biases, two of them the spent failures). Inside that span the check is far above the failure threshold those failures already set.

It does not certify that `C_b` matches the held-out bias. That comparison is descriptive and decides nothing (460–461). It does not certify the label "covers" for the total. §7 row B uses that verb anyway (535), and the label table defines "covers" as the guarded interval lying inside `[0.8, 1.25]` (126–133). Row A uses the same verb under the same one-sided total bar (533).

The fix is in N3-3.

---

## 3. New defects in rev 3

### BLOCKING

**N3-1. The residual stop rejects K_B, and §5.4 extends it to K_C.** Lines 109, 411–412, 420–422, 437.

The stop makes K_B inadmissible if ndf differs from K_A's, or if any kept mode of K_A has a component outside K_B's kept span of norm above 0.1. The cut is `λ > 1e-12·λ₁` (109). The G18 regrade, which added `C_run` at `τ = 0.00977`, moved ndf from 205 to 204, left 142 kept modes outside the new span, and had maximum residual 0.999987 (`regrade_2d_G18.json`). The adopted `Q` sits on the same cut: `λ_min/λ_max = 1.18e-12` (`Q_rep-identity-check.txt`). A one-mode flicker at that edge trips "ndf differs". `C_b` is a much larger perturbation than `C_run`: the spent bias forms above are O(10³), not a 1% trace. K_B fails this stop.

§5.3 sends K_C through the same §5.4 bars, projected onto `P_k` (420–422). §5.4 requires the residual stop (437). K_C's ndf is `k`, which is not K_A's ndf. On the literal chain, outcome C fails the stop by construction. Outcome B fails it because of the regrade fact the draft already cites (72–73).

Fix: delete ndf equality. Apply a residual only to modes that carry a pre-registered share of the trace (the leading band is the one T2A says is not where the bias sits), and print the tail residual without a 0.1 stop. Do not apply the stop to K_C. Re-read the stop against the committed G18 cut before binding: a rule that rejects `C_T + C_run` will reject `K_B`.

**N3-2b. C_b sums absolute biases from six truths and is then carried as a matrix at x_R.** Lines 94–96, 107–108, 395–405.

`e_s = σ̂_s − σ_t` is absolute at truth `t` (107–108). `C_b` sums those outer products and is declared absolute at `x_R` (94–95, 405), then carried by `D_u = diag(x̂_u / x_R)`. The member bound `b̂_tᵀ C_b⁺ b̂_t ≤ 1` is a statement about that uncarried sum (401). The χ² the bars actually compute is `b̂_tᵀ V(t)⁻¹ b̂_t` with `V(t) = D_t (V_F + C_b) D_t`. That equals `(D_t⁻¹ b̂_t)ᵀ (V_F + C_b)⁻¹ (D_t⁻¹ b̂_t)`. The vector in the quadratic form is not the vector that was summed, unless `x̂_t = x_R`. Cell-level tune ratios are not 1; transporting them by an extra `D_t` rescales each contribution by `(x̂_t / x_R)²`.

Fix: map every build truth into the reference frame before the sum. `β_t = D_t⁻¹ b̂_t` and `Σ_t = D_t⁻¹ S_t D_t⁻¹`, then `C_b = [Σ_t (β_t β_tᵀ − Σ_t/(N_t−1))]₊`. State the ≤1 bound for `β_t` against that `C_b`, and state that the carried test uses `β`, not `b̂`.

**N3-3. Outcome B's citable sentence is stronger than its bars.** Lines 126–134, 431–434, 473–474, 478–482, 496–497, 501–507, 533–535.

§6.2 VALIDATED requires total "not under", which includes "over" and "unresolved". The bias block is built to over-cover smaller biases (42–44, 402–403). With N3-2b fixed or not, a sum that includes the spent forms in §2 puts a parallel held-out bias of G18's size about fifty times below the P-2 threshold (`0.25 × ndf ≈ 50` versus a member contribution of about 1). §7 row B then licenses "the covariance covers". In this draft, "covers" means the guarded interval lies inside `[0.8, 1.25]` (126–133). P-2 does not require that. The held-out comparison that would show the slack decides nothing (460–461).

Fix: in rows A and B, replace "covers" for the total with the one-sided statement the bar implements, and put `b̂_uᵀ C_b⁺ b̂_u` and the out-of-span fraction into the licensed sentence. Keep P-1's two-sided "covers" as the fluctuation claim. If outcome B is supposed to be a calibrated bias for the stated class, drop G18 and AR23 from the sum that enters the PASS matrix and print them only as the descriptive envelope §5.1 already allows for spent tunes. Building on them can stay; letting them set the width of the matrix that is then called coverage is the step that empties the total bar.

**N3-4b. Without the KI 85 decision, outcome A can still change the quoted covariance.** Lines 224–226, 232–236, 576–580.

Row 85 says the held-out re-test is deferred and that no outcome changes a quoted band or any printed number before publication. §9.1 requires Joseph to supersede both sentences, then says that without the decision the data-stream row is unread and outcome A cannot change a quoted band. §3.3 implements only the first half: the data-stream row is skipped (236). The `stat`, `c08`, and `universe` rows still fire, and a firing row regenerates that block of `Q_rep` (224–226, 232–235). The `stat` row is the quoted statistical block in the re-scoped KI 85 text. An N2 "under" on `stat` is enough to license outcome A with no N5 and no waiver.

Fix: unless both sentences are superseded, ST1 may record every row and may not regenerate a block, and §7 does not license outcome A. The data-stream skip stays as the extra KI 85 measurement rule for N5, not as the only lock on a changed band.

### MAJOR

**N3-2. Phase N is cited for candidates and ensembles that do not have its inputs.** Lines 462–470.

COV2D phase N is built from the tune's remade centred band-shift vectors and from a Gaussian `C_stat + C_norm + C08 + C_model_abs`, and it refuses unless those pieces sum to `C_T` (COV2D-DECLARATION.md:259–263). A frozen `K_B` is band-scaled `Q_rep` plus a rank-at-most-6 `C_b`. It has no such decomposition, and this campaign does not remake the 175 universes (the remake is the 486 unfolds COVFIX chose not to run, 592–593). "u's draw list" does not supply the shifts. At P2 the same citation is applied to N4 (`r ≡ 1`) and to A1p (a 2D-map deformation of nominal). Those ensembles have no remade shifts either. The 0.20 simulation and the §6.4 false-FAIL bounds are statements about that undefined law (517–518).

Fix: write the null in the draft. For PV, after decryption: carried nominal band shifts deformed by `r_u`, plus a Gaussian equal to `V(u)` minus the covariance of those shifts, with a pre-registered refusal if the pieces miss `V(u)` by more than the C-PSD tolerance. For N4 and A1p, either the same construction from committed nominal shifts, or the Gaussian 0.6827 null already used for N1–N3 and N5, labelled as such. Point the 0.20 check at that written null.

**N3-4. The ST1 exception still admits a numeric change, and the factor is measured on the pre-fix toys.** Lines 141–143, 232–235, 377–388.

The exception may change "the code or inputs that produce" the firing block (232–233). "Inputs" includes replacing the block's numbers after W1 has been seen. That is a recalibration of the firing block, confined to one block and still required to pass PV, but it is wider than the generator. Separately, the exception is bound before P2 (234–235), while W2 is submitted after the W1 reading and before P2 (141–143). N4 and A1p are the ensembles inside `f̂_R` (378–380). Those toys are drawn with the generator that failed ST1, and the factor then multiplies the regenerated block. PV, if the code changed, draws with the new generator.

Fix: the exception amends code, not a substituted matrix, and it names the bug it corrects. Bind it before any ensemble that enters `f̂_R` or `C_b` is drawn again; rerun the firing cell under the amended generator. Price that rerun inside the cap (one cell is 9.5 to 76 node-h).

**N3-5. Custody: the sealed ratio is plaintext on a shared login node, and the PV scan does not look there.** Lines 274–282, 349–351.

The PV writer decrypts `r_u` into login-node `/dev/shm`, builds all 600 pseudo-data files and the Asimov input, then wipes and scans "the campaign directory" (274–280). PG's scan includes `/dev/shm` (341). PV's does not. `/dev/shm` on a login node is visible to every process of the shared account for the whole writer, which the draft already says is one Unix account (349–351). A same-uid read of `/dev/shm`, or of the writer's `/proc/<pid>/fd/0` while the passphrase is on stdin, copies `r_u` without touching the ciphertext. The scan's hit condition is undefined (name versus content). The readout's passphrase is "the same pipe" (282) after that process has exited; §4.2's per-connect pipe is the rule that actually works, and the readout sentence should say so.

The freeze still prevents a leak from amending §5 (284–285). It does not prevent a same-account copy, a private pre-grade once `r_u` is copied, or skipping the official binary. The lock file (245–246) is removable by its owner, so the single-invocation rule is a logged refusal rather than an access control. That last limit is acceptable if it is stated as such.

Fix: run the writer and the readout on an exclusive node with a private `/dev/shm`, not on a shared login node. Scan `/dev/shm`, `/tmp`, and the campaign directory by content against the sealed plaintext hashes. Pipe a fresh passphrase into the readout as its own connect. State that the owner can delete the lock, and that spent-once is the binary's refusal plus the committed record.

**N3-6. The carry vector P0 measures is not the carry §2 defines, and the Asimov file has no construction.** Lines 95–98, 173–174, 271.

§2 sets `x̂_t` to the unfold of noise-free expected pseudo-data. P0 carries with COV2D's committed `x̂_T` from `blocks_<T>.npz` (173–174). That committed vector is the unfold of one Poisson realization (COV2D-DECLARATION.md:200–203), which is also the vector REGRADE §2 scales by. COV2D §4.3: the data tree holds integer counts only, and the closure path that accepts weights refuses `--universe`. No rounding rule turns expected counts into the file `D_t` is computed from. P0 therefore reports a different operator from the one PV will grade, and it does not stop on the difference (175–176).

Fix: define `x̂_t` as one object. Either carry with the committed block key `x` wherever it exists, and define the new-truth vector as the unfold of `round(λ⁺)` (or the closure-path mean, if the driver is shown to accept it) under E_R's argv, with the rounding written in §2. Or keep the Asimov and add a P0 line that repeats the carry with both vectors on G18 and AR23 so the gap is a number. Point §2's citation at the formula shape only; the reference vector is not REGRADE's `x_T` and not COV2D's `x̂_T` until this is specified.

**N3-7. §6.4's false-PASS boundary is about one standard error past the bar, not near-certain failure.** Lines 501–504.

"Not under" fails when `M − h > 1.25`, so the critical value is `1.25 + h`, with `h = t_{0.975,N−1}·SE ≈ 1.968·SE`. At ndf 204 and N 300, `SE = √(2/61200) = 0.00572` and `h = 0.0112`. The draft's boundary `M_true > 1.25 + 3·SE = 1.267` lies 1.03 SE above the critical value 1.261. The normal probability of failing "not under" at that boundary is 0.85, not near 1. The probability of passing both truths is about 0.023 if the truths are independent, and the union over three candidates is about 0.07. The same arithmetic at `k = 10` (`SE = 0.0258`, `h = 0.0508`, boundary 1.327, critical 1.301) gives the same 0.85. A candidate with `M_true` at the historical 16–24 still fails with probability essentially 1. The sentence as written is the familywise argument, and it is wrong at the boundary it states.

The rest of §6.4 holds. `SE ≈ 0.006` is right. P-3's under-tail is at most 0.025 and P-4's expected false under-flags are at most 0.025, so per truth 0.05 and over two truths 0.10 follow by the union bound (508–516). At `k = 10`, `h ≈ 0.051`, the covers-label edges are 7.71σ on the high side (`1.25 − h`) and 5.78σ on the low side (`0.8 + h`). The rev-2 swap is fixed (512–513). Those two numbers are the covers label. P-2 fails only above `1.25 + h`, which is 11.7σ at `k = 10`. Calling both checks negligible remains true. The 0.05 and 0.10 bounds do not depend on the false-PASS sentence.

Fix: set the worked boundary at `1.25 + h + 3·SE` (about `1.25 + 5·SE`), and quote the tail probability at the boundary that is written.

**N3-8. The band factor is measured in one eigenbasis and applied in another.** Lines 378–388.

`f̂_R` averages band means of `v_i` in `F_A`'s carried eigenbasis at each ensemble's truth (378–382). Carrying by `D_t` does not preserve eigenvectors, so the rank band at genie_mec is not the rank band at `x_R`. The scale is then applied to "F_A's eigenvalues in band R" (387–388), which is the reference matrix that later gets carried again (405). An implementer can scale the reference eigenbasis, or scale each carried basis and then have no single `V_F` at `x_R`.

Fix: one sentence. Diagonalize `F_A` at `x_R`, multiply those eigenvalues in ranks 1–73, 74–139, and ≥140 by the corresponding `f̂_R`, and carry the result. State that the factor is a rank-band summary transferred across bases, so it is not a mode-matched estimate.

### MINOR

**N3-9. k ≥ 10 is justified at N = 300 and applied at N = 100.** Lines 420–425, 431–433.

The floor sentence uses `SE = √(2/(300·10)) ≈ 0.026` and `h ≈ 0.051`, and it correctly says the operational guard is the bootstrap SE (423–424). §5.4 applies the two-sided covers bar at A1p, where N = 100. There `SE = √(2/1000) = 0.0447` and `h ≈ 0.089`, so the low-side covers edge is 2.5σ and the high-side edge is 3.6σ. The PV false-FAIL bound at N = 300 is unchanged. The largest-k rule (420–421) freezes a subspace that was selected with that wider guard.

Fix: quote the excursion at N = 100 next to the N = 300 figure, or raise the floor until the admission edge is the one §6.4 claims (`k ≥ 25` is the smallest integer with a 5σ low-side edge at N = 100).

**N3-10. "Same CMC" for the G18_02 fallback.** Lines 296–302.

The draft's own gloss says the letter in the CMC token selects the transport model. `G18_02a_02_11b` and `G18_02b_02_11b` differ in that letter. The tunes page (read for this review) lists them as separate CMCs. The exclusion rule still runs on the probe's class names (316–317), so the fallback is caught if both QE and 2p2h classes match a spent tune.

Fix: "same G18_02 construction, different intranuclear transport."

**N3-11. Per-job walltime is the mean price.** Lines 164–165.

`--time` is "set from" the priced 0.19 node-h, which is a mean (COV2D's 112.74/600 = 0.1879, cited at 150–151 as 0.188). A job slower than the mean is killed. Replacements are extra submissions under ST6, and the draft gives no factor above the mean.

Fix: a pre-registered multiplier (for example 2) between the priced mean and `--time`, inside the phase cap.

**N3-12. Two price sentences are easy to misread. The products themselves match.** Lines 148–161, 579–581.

Every `n × 0.19` cell matches the printed node-h, including the central unfolds: W1 161.69 and 123.69, W2 129.77 and 86.07, P1 291.46 and 209.76, PV 114.38 = 602 × 0.19, full 407.17–407.84, lean 325.47–326.14, caps 468 and 378, half of 725.6 = 362.8. The range is said to be "floored at" F1's 1.3275 and is printed from 1.33; the sums use 1.33. §9.2 says the full total is above half the balance. That is true with N5 (407.8). Without N5, §9.1's saving of 76 node-h puts the full top at 331.8, which is below 362.8.

Fix: "the printed range starts at 1.33, above F1's 1.3275." In §9.2, give the no-N5 total next to the with-N5 total.

**N3-13. Undrawn `C_PL` sits inside the two-sided fluctuation block.** Lines 84–85, 211, 377.

`Q_rep = s5_total + C_PL`, and `C_PL` is not drawn (211; SCOPING a3). P-1's null is therefore a little below 1. `τ ≈ 0.0098` will not by itself push a band through 0.8. The eigenbasis change from that same addition is the regrade's 142 modes, which is N3-1's problem rather than a mean-ratio problem.

Fix: one clause at P-1 that the null ratio is the drawn share of `V_F`, with `τ` printed beside `F^F`.

**N3-14. Bootstrap basis, and the tunes-page scope.** Lines 299–310, 384–386.

The bootstrap sentence does not say the eigenbasis stays fixed at the full-sample `F_A` while toys are resampled. Hold it fixed, or the SE depends on a rediagonalization. The tunes page's physics bullets are for v3.2.0; the product is genie_xsec `v3_04_00` (FD-F1-DECLARATION.md:76, which is the product and spline path the draft cites). The page's G21 SuSAv2 sentence, the G18_02 RS→BS sentence, the G18_10 NAV/NSV sentence, and the `_02_11b` retune sentence match the page. The probe remains the exclusion input (311–317). Say the glosses are v3.2.0 descriptions pending that probe.

---

## 4. What blocks binding

BLOCKING:

1. N3-1. Replace the ndf-and-0.1 residual stop. As written it rejects the regrade's own `C_T + C_run`, so it rejects K_B, and §5.4 carries it onto K_C.
2. N3-2b. Build `C_b` from biases mapped to `x_R` by `D_t⁻¹`, then carry.
3. N3-3. Make §7 row B say what §2 of this report says a pass certifies, or take the spent biases out of the PASS matrix.
4. N3-4b. Without both KI 85 sentences superseded, no block is regenerated.

MAJOR before binding, after those four:

5. N3-2. Write the null. Do not cite phase N on `K_B` or on A1p until its inputs exist.
6. N3-4. ST1 amends code only, and the amended generator draws the ensembles inside `f̂_R`.
7. N3-5. Exclusive-node writer, content scan including `/dev/shm`, a separate pipe into the readout.
8. N3-6. One definition of `x̂_t`, constructible by the driver, and the same vector in P0 and in §2.
9. N3-7. Correct the `1.25 + 3·SE` probability.
10. N3-8. Say which eigenbasis the band factor multiplies.

MINOR: N3-9 through N3-14. The §6.4 figures 0.006, 0.051, 7.7σ high, 5.8σ low, 0.025, 0.05, and 0.10 can stay. The high/low assignment is now the right way around.

The open iris receipt, the unnamed PG session, and the existence of a KI 85 decision are prerequisites §9 already lists. They are not fixed by editing prose. N3-4b is the prose that mishandles the third one.

A pass of the fluctuation bar would be a meaningful result for `V_F`. Binding waits on the stop, the frame of `C_b`, the sentence in row B, and the KI 85 fallback.
