<!-- absence-ok: verbatim third-party read report -->
NO-GO

Draft rev 1 should not be bound. The price arithmetic and most transcribed COV2D, T2A, REGRADE, G2R, and F1 numbers check out. The validation set, the ST1 skip rule, and K_B's fluctuation rule do not. A candidate can be fit to the spent G18 failure, "validated" on an FSI twin of that same tune, and either skip the held-out check that would have caught a masked under-coverage or be marked INFLATED by its own joint test for being a few percent wide. Those are binding blockers. Minor transcription nits are listed separately and are not the reason for the NO-GO.

Line numbers are from `inputs/COVFIX-DECLARATION.md` unless marked INV (`inputs/INVENTORY.md`).

---

## 1. Fidelity

Checked against the packet: T2A reading, COV2D declaration and outcome, G2R readout, REGRADE declaration, both 2D regrade JSONs, 10-05 outcome, KI 84/85, IBUKT A2 outcome, F1 report and declaration, methods scoping, and GENIE's tunes page (the page §4.1 cites).

These check out, to the rounding the draft prints: T2A's 16.55 / 24.17, 13.61 (82%) / 20.97 (87%), 2.94 / 3.21, 0.7% / 0.9%, 77% / 87%, spreads 1.6/3.0/4.4 and 1.5/3.6/4.7, truncated joint 0/0 of 300 (INV:12–18; decl:45–46). COV2D joint 0/300, k_J 190 and 192, χ²/ndf 16.55±0.17 and 24.17±0.37, |ē|/σ median 0.114 / 0.092 and max 1.039 / 0.964, spread-only median p̂ 0.673 / 0.653 (INV:42–44). G2R identical coverage, bias-driven flags, ε 25.833 on 205 and 5.999 on 73 (INV:24–26). 10-05 C1 0.679, C2 0.912 vs [0.928, 0.972], pull RMS 1.6, mean consistent with 0; VL170 rescore C1 0.781, C2 0.977; VL170 not re-tested (INV:29–35). REGRADE 2D: M′ 16.350 (0.170) and 22.776 (0.351), parts 13.469/2.881 and 19.644/3.132, τ 0.009767 and 0.009768, M_full 16.360 and 22.786, joint 0/300 at k′ 190 and 192, absolute-carry M_full 16.351 at AR23, first G18 A0(b) 1.730e-8 against flat 1e-9, κ₂ 9.496e11, codes `058bca19` and `479e03cc` (INV:51–64). F1 total 1.327500 node-h at report line 143; about 0.66 per tune (decl:51, 220). COV2D 112.74 node-h over 27 attempts (scoping §c); 112.74/600 = 0.188, so 0.19 is the right planning round. G2R cap 110 with 98.3 held (INV:99). IBUKT A2: 7 truths × 5 draws, nominal response, noise-free nominal max residual 1.708% (INV:76–79). The 1e-12·λ₁ cut matches REGRADE. √1.25 = 1.118, so "25% excess χ² is about 12% excess σ" (decl:309–310) is right, and 0.8 = 1/1.25 so the two M edges are the same σ factor.

**F1. MAJOR. AR23 already uses SuSAv2 2p2h, so the G21 distinctness claim is false.** Decl:199–200 says G21_11* "uses the SuSAv2 QE and 2p2h model" and that neither C_model's members nor G18/AR23 use it. The tunes-page sentence about G21 is quoted fairly. The "neither" sentence is not on that page. F1 report §1.3: both spent tunes use `NievesQELCCPXSec` for CCQE; G18_10a's 2p2h is Valencia (`NievesSimoVacasMECPXSec`); AR23_20i_00_000's 2p2h is `SuSAv2MECPXSec`. G21 shares its 2p2h model with the spent AR23 tune. Fix: replace the sentence with the F1 model split (QE and 2p2h separately), and treat G21_11b as partially overlapping AR23, not as an unseen interaction model.

**F2. MAJOR. G18_02a is not the tune nearest C_model's GENIE 2.12.** Decl:204–207. The tunes page identifies G00_00b_00_000 as the preserved GENIE v2.12 Default+MEC tune. G18_02* is an adiabatic update plus an RS→BS resonance/coherent change; the page does not give it Valencia MEC. F1 and COV2D §3 say the spent G18_10a tune is the one whose 2p2h sits in the GENIE+MEC family. The fallback is pointed at the wrong neighbour. Fix: if the fallback is "nearest the model term", name G00_00b and the reason; keep G18_02a only as a distance choice, with the F1 overlap stated the other way around.

**F3. MAJOR. "0.661 in data-dominated cells" misplaces KI 85.** Decl:85–86. KI 85's corrected median σ_T/σ_realboot of 0.661 is over all 205 reported bins. The same row's data-dominated statement is the earlier pull RMS (f>0.7: 0.710) and the solved variance ratio g, median 0.40 (p16 0.08, p84 0.86) over 192 bins. Squaring 0.661 gives 0.437, so "near 0.44" is a fair square of the median ratio and is not the variance ratio the row already prints. KI 85 also says the VL169/VL170 numbers do not grade S1, and that S1 has not been coverage-tested. Decl:85–86 uses 0.661 as if it were S1's data-dominated variance ratio. Fix: quote 0.661 as the all-bin σ ratio from the 2026-10-07 diagnostic on the old band, quote g = 0.40 if a variance ratio is wanted, and state that neither number grades S1.

**F4. MAJOR. tune_v1 and the `_sq` maps are not in the cited records.** INV:89–90 and decl:118, 263 list genie_mec, nuwro, gibuu, tune_v1 and `_sq` variants as C_model's members. COV2D §3 names three vertices only: GENIE 2.12+MEC, NuWro, GiBUU. A2's seven truths are nominal, genie_mec, nuwro, bump, tilt, within±. No tune_v1, no gibuu draw, no `_sq`. A1's bias reference "C_model" is then a test against a membership list the packet does not support. Fix: name the PV2D file and the rows that define each map; drop any map that file does not contain; do not call a map a C_model member unless that file builds C_model from it.

<!-- absence-ok: verbatim third-party read report -->
**F5. MAJOR. INV:79 says b1 already projected A2's residual onto Δ in V_pub.** Methods scoping §b lists that projection as a test that had not been run (recommendation "b1 now if the director wants"). The A2 outcome has no such projection. COVFIX itself schedules the projection as future P0 work (decl:103–104), so the declaration is clean and the inventory is not. Fix: mark b1 as not run, and point P0 at A2's `readout.json` only.

**F6. MAJOR. "τ = 0.0098 says they cannot move any reading" (decl:127–128) is stronger than the G18 regrade record.** τ is 0.0098 per ndf at both tunes, and M_full − M′ is that τ. The stored-toy mean against C′ is not the COV2D mean: G18 goes from 24.17 (C_T, ndf 205) to M′ 22.776 (C′, ndf 204), a drop of 1.39, about 3.8 times G2R's C_T SE of 0.37. AR23 goes from 16.55 to 16.350, about 1.2 times its SE of 0.17. The G18 cut block records `C_T_kept_modes_outside_C_prime_kept_span` = 142 and `max_residual_of_C_T_kept_modes` = 0.99999. A trace of 0.01 per ndf coexists with a kept subspace that moved. This plan decides on eigenmodes. Fix: delete "cannot move any reading". Require the REGRADE cut diagnostic (kept-set difference, smallest kept, largest dropped) on every candidate V, and treat a large residual as a stop, not as a negligible block.

**F7. MAJOR. The balance 725.6 is not in the packet.** Decl:83, 88. Half of 725.6 is 362.8, and that division is exact. Methods scoping says the balance cannot be read without a connect, and the last committed iris figure it prints is 1328.8 node-h at 2026-11-13, already stale after G2R, LL5D, IBUKT and others. Fix: cite the iris row and the connect that produced 725.6, or drop the number until a stat-only read is attached. Do not bind the half-balance rule to an uncited balance.

**F8. MINOR. Inventory claims that are not in this packet, and small citation slips.**
- INV:65–66, the 16-cell half (M_full 1.82 and 2.54; joint counts 75, 76, 20, 27; k′ 193). No 16-cell JSON is in the packet. The four-evaluation list matches REGRADE §4, so the shape is plausible and the figures are unchecked. They are labelled 5D context and do not enter the 2D price.
- INV:37–39, the 11-11 consult, "(a+)", and "gpt-6.1-sol". That README is not in the packet.
- Decl:412 cites the κ-scaled tolerance to "T2-BINDING-1 addendum 1". In this packet the rule is REGRADE-AMENDMENT-1, adopted after the G18 A0 STOP (REGRADE declaration, A0 row).
- Decl:194–198, "the final letter selects the intranuclear transport". On the tunes page the FSI letter is the last character of the CMC token (`10a`/`10b`/`11b`/`02a`). The last character of the full id `G18_10a_02_11b` is the `b` in `11b`, which the same page defines as the published 2020 retune, not hN. The four explicit qualifier strings are the right ids. The prose rule is not.
- Decl:69, "in the b1 style" for the t-guard. Scoping's b1 is a projection, not this guard. The guard is new, and the label is unsupported.
- Decl:363–365, "the 20% mark the director set". Not in the packet.

---

## 2. Blindness

**Yes. A candidate can be tuned on the validation truths before anyone opens the seal.** The file custody does not have to fail for that to happen. Three paths are open in the text as written.

**B1. BLOCKING. The sealed set is chosen to include a twin of spent G18.** Decl:186–211. The preference order is fixed in the draft, after G18 and AR23 have been read, and item 2 is `G18_10b_02_11b`. Decl:202–203 says this tune differs from spent G18_10a_02_11b in the intranuclear model only, tests FSI at a seen quasielastic model, and is close to G18. It is still a validation truth. With G21_11b absent from the product, the set collapses to G18_10b, G18_02b, and possibly the G18_02a fallback that §4.1 calls nearest the model term. K0 "covers at all three → inconclusive" (decl:249–251) trips only if every tune is too close. One close tune is enough for a construction fit on spent G18 to pick up a pass. The build set makes that fit explicit: F and the §5.4 bars include G18 and AR23 (decl:242, 263–272, 284–288). φ, the B1/B2 choice, and K_C's k are then chosen so the spent failure stops reading "under", and PV checks a tune the draft has already described as that failure's FSI twin. That is indirect tuning. The review allowed the spent tunes to build a construction and forbade them to validate it. Putting their twin in the validation list spends the validation in advance.

Fix: remove `G18_10b_02_11b` from the validation list. Pre-commit three qualifiers whose CMC tokens differ in the QE/2p2h model, not only in `a`/`b`/`c`/`d`, and state the F1 overlap for each before PG. If fewer than three distant qualifiers exist, stop (do not fill the list with a G18 twin). Keep G18 and AR23 out of the §5.4 pass/fail bars. They may be printed as a descriptive build check. They may not choose φ, k, or the B1/B2/B3 winner.

**B2. BLOCKING. Custody in §4.2 is not sufficient, and two of its holes are still open items.** Decl:213–232 and §9.1.
- The generating session may be tier3-design, which wrote the scoping that already contains the G18/AR23 anatomy. Session separation does not undo that.
- F1's own pipeline, which PG reuses unchanged except tune names and seeds (decl:218–220), writes f_MEC, process fractions, CC counts, and ratio normalisation k into meta and logs (F1 report §1.4 and §2). Decl:221–228 forbids committing the ratio file and forbids reading "content", and then allows "pass/fail and counts". Those counts fingerprint the tune. Atime on the pscratch copy does not move when someone reads the log.
- The HPSS copy is proposed and not required (decl:225–226, §9.1). Until it is required, a pscratch purge destroys the seal after the candidates exist, and the draft has no rule for regeneration. If the copy is made, pscratch atime does not see an `hsi get` of the HPSS member. The backup is a second door.
- Seeds are "fresh" and not pre-committed. The session that can see the failure mode picks them.
- Seal atime is specified for PV's reads. It is not specified for the sha256 that creates `PG-SEAL.sha256`.
- §9.1 leaves both the generating session and the HPSS requirement unnamed at bind time. A custody rule that still has "who" and "whether the only durable copy exists" open is not a custody rule.

Fix, before any PG job: name a session that has not read COV2D, T2A, G2R, or REGRADE; pre-commit seeds; require the HPSS `htar` plus `hashverify`; hash with `O_NOATIME`; define the PG log schema as pass/fail booleans with the physics counts omitted; record atime on every copy, including HPSS retrievals; make a purge or a moved atime a guard refusal that stops the study rather than a prompt to regenerate.

**B3. MAJOR. "Validation is spent once" (decl:151–154, 391–395) is not enforceable as written.**
- It does not define a read. One readout pass scores K_A, K_B, and K_C, and "the others are reported descriptively" (decl:373–374). A log that prints per-toy z_{s,i} is a full second copy of the validation errors. The rule does not say those arrays stay inside the readout process.
- Amendments are allowed after any phase whose output exists (decl:29–30). ST4 starts only at the PV read. Between P1 and PV an amendment can change §5 using G18 and AR23. Numbering the amendment makes the change visible. It does not make it illegal. That is the indirect-tuning hatch.
- Two qualifiers present is a legal PG outcome (decl:209–211 stops only below two). The verdict "PASS at all three" (decl:343) is then undefined, and the lean two-truth rule applies only if Joseph already chose lean (decl:90–91, 343). Spent-once does not say which rule binds.
- UNRESOLVED "needs an amendment and a price, never a re-read" (decl:395). That sentence is enforceable and is the right hard stop. Keep it. The gaps are the undefined read, the pre-PV amendment hatch, and the two-tune verdict.

Fix: one readout binary writes one JSON; per-toy residuals are not in it; a second invocation on the same seal is a guard refusal. Freeze §5 with P2, and forbid amendments that change a bar, φ's grid, F, or k after G18 or AR23 numbers have been used. If the probe finds two qualifiers, the lean verdict rule binds automatically or PG stops. State that a published FAIL may inform the design of a later construction, and that the later construction needs a new seal. That last part is already the intention. Write it as the limit of the rule, so "spent once" is not read as a claim it cannot enforce.

---

## 3. Design soundness

The identity in decl:34–35 is the right decomposition, and the per-mode (m_i, v_i, q_i) split (decl:62–68, 326) is the right measurement. P1 does put each drawable source on its own reference: N1 data stream, N2 simulation redraws, N3 seed, N4 nuisances, A1 fixed-response bias (decl:112–120). C_run and C_PL are the source that is never drawn (decl:127–128). That matches scoping a3. It does not match "cannot move any reading" (finding F6).

What the plan does not do is fit that split. PASS (decl:330–337) is entirely on the total q_i: M, band Q_R, joint χ², and per-mode |z|≤1. The bias/spread split is "descriptive" (decl:326). A candidate whose extra width is sitting in the fluctuation block, and whose bias block is wrong, passes on the same bars as a candidate that separated them. Outcome B's sentence says the bias is a separate block (decl:384). The bars do not check that the block is the bias.

**D1. BLOCKING. K_B's fluctuation rule is unsound at 205 cells with 200 toys, and P-3 will reject the candidate it produces.** Decl:255–261, 315–318.
- Only the diagonal in a pre-specified basis is needed: ŝ_i = Var(u_iᵀ e_s) is a one-dimensional variance on 200 draws. Its sampling sd is √(2/199) ≈ 10% if the mode is Gaussian and λ_i is correct. The 205×205 matrix is singular (rank ≤ 199). That singularity does not affect the 200 one-dimensional variances. Ledoit–Wolf on the matrix is unnecessary for this estimator.
- The named target is wrong. "Shrunk toward diag(Ŝ) by the Ledoit–Wolf estimator" is not the Ledoit–Wolf estimator. The standard estimator shrinks eigenvalues toward a scaled identity. `sklearn.covariance.LedoitWolf` will not do what this sentence asks. On a spectrum that is cut at 1e-12·λ₁, shrinkage toward a multiple of the identity pulls the small modes up to the mean variance, which the large modes dominate. max(λ_i, ŝ_i) then replaces the small-mode model with that target. Those are the modes T2A says carry the failure.
- max(λ_i, ŝ_i) is upward-biased even for a perfect λ. With a 10% noise sd, E[max(λ, ŝ)]/λ ≈ 1 + 0.10/√(2π) ≈ 1.04 on every mode that was already correct. The joint over-coverage flag is much tighter than the M window. For ndf 204 and N 300, the χ² 0.6827 quantile is c = 213.07. Reported variance inflated by a factor a gives joint coverage F_χ²(a·c). The over flag is count ≥ 221 (finding S1). At a = 1.02 (M = 0.98) that flag already has probability about 0.74. At a = 1.05 it is essentially 1. A 4% one-sided floor, applied to every mode, lands in INFLATED on a validation truth whose true fluctuation equals λ. The build bars do not stop this: §5.4 forbids joint "under" and does not forbid joint "over" (decl:284–288).
- V_F is always taken from N4, and N4 always includes N2's simulation redraws (decl:117, 256). PV adds those redraws only if N2's R1 spread exceeds N1's by more than the two guards (decl:176–178). The last sentence of that rule ("the redraw also enters K_B … if it fires") contradicts §5.2, where N4 is unconditional. If the R1 test does not fire, K_B is fit to a wider ensemble than PV draws, and P-3 reads the difference as inflation. R1 is the wrong place to look: T2A's spread excess grows toward the small modes (INV:20–21).

Fix: estimate each ŝ_i as the univariate sample variance of u_iᵀ e_s in the frozen basis. Raise λ_i only if ŝ_i − λ_i exceeds the guard h. Do not run a matrix shrinkage. Draw, in PV, exactly the sources that entered Ŝ, on every toy, with no R1 switch. Put the joint over-flag and the M > 0.8 edge on the same tolerance, or stop calling 0.8 an accepted over-coverage level (see S3).

**D2. BLOCKING. B3 is the scaling the review rejected.** Decl:267–272, 385. φ is the smallest value on {1, 2, 5, 10, 20, 50, 100} such that §5.4 passes on the build set. The build set includes G18 and AR23 (decl:242, 284). The floor applies for every rank above 73, which is where T2A puts 77% and 87% of the mean error. There is no measured b. Choosing the smallest φ that makes the two spent tunes stop reading "under" is scaling the covariance until those two tunes pass, restricted to a grid and to the small modes. The out-of-sample PV read does not undo the selection: φ was already fit to the spent failure, and finding B1 puts a near-copy of that failure in the validation list. The distinct sentence at decl:385 ("say floor, not measured bias") is an honest label on a procedure the review excluded. A label is not a different procedure.

The floor also fights the eigenvalue cut. λ′_i = max(λ_i^F, φ·λ_73^F) lifts ranks above 73 to at least φ·λ_73, far above the 1e-12·λ₁ drop. Modes that were numerical nulls become kept modes, ndf jumps, and the joint test starts scoring directions the cut exists to remove.

Fix: delete B3. If a floor is ever reintroduced, choose φ only on N4 and on A1's generator maps, never on G18 or AR23, and apply the cut after the floor with an explicit refusal if ndf changes.

**D3. MAJOR. Nominal N4 cannot see the fluctuation excess that §1 says rules out a bias-only fix.** Decl:45–47, 255–256. The spread ratios 1.6–4.7 are measured at G18 and AR23, with the response perturbed and with C_T remade at that truth. V_F is the nominal N4 ensemble (r_T ≡ 1, nominal response). bbᵀ does not add spread. No candidate has a term for truth-dependent extra variance except B3's floor. P0 computes the tune profiles (decl:99–102) and §5 then ignores them for Ŝ. PV can still FAIL a candidate that misses the excess. The candidate family cannot represent the excess the introduction calls decisive, short of the scaling in D2.

Fix: either add a pre-registered fluctuation component from a perturbed-response ensemble that is not the validation list and not G18/AR23, or state in §1 and in the outcome-B sentence that truth-dependent extra variance is unmodelled and that nominal N4 is only the nominal-fluctuation term.

**D4. MAJOR. N4 and PV name 38 bands; COV2D §4.2 also draws the lateral surrogate and the 1.4% normalization.** Decl:117, 160–174 says PV uses COV2D's model and then specifies Flux plus the other 37 bands, the composite, the Poisson draw, the clipped truth, and seed 42. The incorporating citation pulls in the rest of §4 only if a builder treats the bullets as incomplete. The reference block at N4 is "S1 + C_syst + C_seed". C_T's graded matrix is C_univ + C_lat + C_norm + C_stat + C08 + C_model (COV2D §4.4). Dropping C_lat and C_norm from the toys, while leaving them in V, moves the joint count toward over-coverage for a correct V. COV2D §5.2 already records that not-drawn positive components lower the under-coverage flag rate, which is the same shift.

Fix: in the N4 and PV bullets, list the lateral surrogate and the normalization draw beside the 38 bands, or say in one sentence that the reference excludes them and the candidate V excludes them too.

**D5. MAJOR. The inflation catches are real on the joint test and missing on the bands, the modes, and the build bars.**
- P-3 does catch a global scale. An M of 0.85, which P-1 still calls "covers", has joint coverage about 0.986 and is flagged over with probability essentially 1 (ndf 204, N 300). INFLATED (decl:345) therefore catches the inflation P-1's 0.8 edge would let through. The draft's worry about a uniform scale is answered by P-3, not by P-1.
- P-2 forbids a band "under" and allows a band "over" (decl:332). P-4 forbids more than two modes "under" and allows every mode to flag "over" (decl:334). A candidate can be VALIDATED with many over-wide modes as long as the joint count stays under 221.
- §5.4 admits a candidate whose joint reading is over (decl:288: "not under" only). The build can hand PV a matrix the validation rule will call INFLATED.
- P-4 allows two Bonferroni-significant under-modes and still PASS. COV2D called one flagged cell at G18, and two at AR23, UNDER-COVERS. P-3 would still catch those two tunes (joint count 0). A validation truth that is bad in one or two modes and nominal jointly would PASS. The allowance exists so that P-4 stays out of the §6.4 budget (expected false flags ≤ 0.025, while three flags are required to fail). That is the pass rule being loosened to fit the error budget.

Fix: at P2 and at PV, joint "over" is the same refusal as joint "under". P-2 refuses a band "over" on the same guard as "under". P-4 refuses any under-flagged mode. Recompute §6.4 after that change (the per-truth not-PASS bound picks up about 0.025 from P-4 and the three-truth figure moves by about a point).

**D6. MAJOR. A1 does not add an alternative truth outside C_model's inputs.** Decl:118, 263. genie_mec, nuwro, and gibuu are the vertices COV2D §3 says C_model is built from, subject to F4 on tune_v1. Unfolding them at fixed response is a real measurement of estimator bias, and 100 draws separate b from noise better than A2's 5. Scoring that bias against C_model is a test of the unfolding, and it is also a test of a covariance on the shifts that defined it. It is not cell 4 of the review for any generator outside that list. The new generators are reserved for PV, where only the total is barred (see the opening of this section).

Fix: keep A1 as the in-sample bias measurement. Do not describe it as the review's held-out alternative-truth cell. That cell is PV, and PV needs a bar on the split, not only on q_i.

---

## 4. ST1 and KI 85

**The direction of the slogan is right. The rule as written is not.** KI 85's mechanism (b) is that same-event pseudo-data under-scatter relative to a band built like the real-data bootstrap (median σ ratio 0.661, so a variance factor near 0.4). An observed "under" is then harder to produce, not easier. An observed "under" is evidence of a real deficit, and the measured deficit is a lower bound. An observed "over" can be mechanism (b) alone. That is the part of decl:135–139 that matches the row.

It does not support the operational rule.

**S-ST1. BLOCKING. "Covers" is treated as safe, and on the draft's own factor it is where a real under-coverage lands.** Decl:84–88, 122–126, 135–139.
- N5 is skipped when N1 and N2 both read "covers" or "under" in R1. "Under" fires ST1 without N5. "Covers" fires nothing.
- Apply the factor the draft asserts, 0.44. Observed M in the covers window [0.8, 1.25] is true M in about [1.82, 2.84]. The band "over" edge is Q+h < 0.67 and the band "under" edge is Q−h > 1.5, so an observed band that is called covers (see D7: that word is not defined) corresponds to a true band mean up to about 1.5/0.44 ≈ 3.4. A factor-of-two under-coverage is read as covers, N5 never runs, and ST1 never fires. The caveat at decl:125–126 ("a ratio below 1 is a bound, not a measurement") is not wired to the skip. Covers includes ratios down to 0.8 and, for bands, down to 0.67.
- "Can only under-scatter" (decl:135) overstates the row. g has p84 0.86. The row does not say every bin is below 1. The 0.661 figure is not an S1 result (finding F3).
- N3 is one fixed pseudo-dataset with the seed varied (decl:116, 140–141). The Poisson draw is common to all 50 seeds and cancels in the seed-to-seed variance. Mechanism (b) does not create an N3 "over" or hide an N3 "under". Sending N3's over reading to N5 "for the data-stream share" needs a share the draft never defines. N4's over reading has the same hole: no formula separates the data-stream piece from the 38 bands.
- KI 85's standing ruling is that the held-out re-test is deferred until after the publication package, is not pre-registered, and that no outcome changes a quoted band or a printed number before publication. Decl:7–8 records a later authorization to start the design. It does not record a reversal of that ruling. N5 plus ST1 is that re-test, and outcome A is a covariance change (decl:142–143, 382). Binding this path as written contradicts the KI row the draft cites.

Fix: N5 always runs. It is already the expected price. No N1 or N2 label is a construction error until N5 is read. An N1 "under" is recorded as a lower bound on the deficit. An N1 "over" or "covers" is recorded as uninterpretable until N5. N3 is judged against C_seed with no N5 gate. N4 is judged by a written subtraction, per mode, of the N5 (or N1) data-stream variance from the N4 variance, with the guard on the difference. Ask Joseph to supersede the KI 85 deferral in a decision, or schedule N5 after the publication package and drop it from this pre-registration.

**D7. MAJOR. The band label "covers" used by the skip rule is not defined.** Decl:87, 122, 312–313. For M, a label is issued only when the whole interval [X−h, X+h] lies inside one region. For a band, "under" means Q−h > 1.5 and "over" means Q+h < 0.67. The middle has no name, and the two conventions treat h in opposite ways: M's interval must fit inside the label, while a band flags only when the interval clears the bar. ST1 and the N5 skip need the word "covers" on R1. An implementer can assign it either way, and the two ways disagree whenever the interval crosses 0.67 or 1.5.

Fix: define the R1 reading with the same rule as M, name the middle "covers", and state the numeric edges.

---

## 5. Statistics

**The headline arithmetic is correct under the assumptions §6.4 states. Several of those assumptions are false for the candidates and the toy counts the plan actually runs.**

Checked:
- SE(M) = √(2/(N·ndf)). At N = 300 and ndf = 204 this is 0.00572, which rounds to 0.006. At ndf = 205 it is 0.00570 (decl:352).
- t_{0.975, 299} ≈ 1.968, so h(M) ≈ 0.0113, which rounds to 0.011 (decl:357).
- At k = 5, SE = 0.0365 and h = 0.0719, which round to 0.037 and 0.072 (decl:357–358).
- A 66-mode band of independent unit-mean q_i has SE 0.0100 (decl:359). R2 is ranks 74–139, which is 66 modes. R1 (73) is 0.0096. R3 is 65 modes if ndf is 204 and 66 if ndf is 205.
- Bin(N, 0.6827) at α = 0.025, strict inequality, N = 300: under flag at count ≤ 188 with size 0.0226; over flag at count ≥ 221 with size 0.0244. Both are at or below 0.025 (decl:361–362). The same under threshold k_J = 188 appears in COV2D's Gaussian power note. COV2D's actual k_J values of 190 and 192 are the draw-matched null, not this Gaussian one.
- Per-mode Bonferroni at 0.025/204 and N = 300: under flag at count ≤ 174, size 1.17e-4, which is below 0.025/204. Expected false under-flags across 204 modes ≤ 0.025 (decl:334–335, 360). Linearity gives that bound without independence of modes.
- 1 − 0.95³ = 0.1426 and 1 − 0.975³ = 0.0731. Lean: 1 − 0.95² = 0.0975 and 1 − 0.975² = 0.0494 (decl:363–364). The arithmetic printed as 0.14, 0.07, 0.10, and 0.05 is correct.
- A candidate with M_true > 1.25 + 3·SE (SE 0.00572, so M_true > 1.267) has P(the guarded interval lies above 1.25) ≈ 0.88 and P(it fails to lie inside [0.8, 1.25]) essentially 1. "Under or unresolved with probability near 1" (decl:351–352) is the right claim. "Under" alone would not be.

**S2. MAJOR. The 5σ sentence is the wrong threshold, and it is applied at a k the plan does not guarantee.** Decl:357–358. Leaving the covers label happens when M < 0.8 + h or M > 1.25 − h, because the whole interval has to sit inside [0.8, 1.25]. At k = 5 that is 3.5σ on the low side (h = 0.072, edge at 0.872), not 5σ. Five σ is the point estimate reaching 0.8, which is not the reading rule. At k = 5 the probability is still about 2×10⁻⁴, so "P-1 essentially never fails" survives for that example.

K_C's k is "the largest value such that the build bars are met" (decl:280), with no floor. At k = 1, SE(M) = 0.0816 and h ≈ 0.16. The covers interval then fails if M < 0.96 or M > 1.09, which is about half a standard deviation below the null mean. P(not PASS) is then tens of percent, and 1 − 0.95³ is not the false-FAIL rate. The χ² mean at k = 1 is an average of χ²(1) variables (skew √(8/300) ≈ 0.16); the normal tail used in §6.4 is already approximate there.

Bands are also undefined for K_C. R1/R2/R3 are ranks of the full matrix (decl:66–67). On a k-dimensional subspace with k ≤ 73, R2 and R3 are empty, and "a 66-mode band has SE ≈ 0.01" does not apply. P-2 has no rule.

Fix: floor k so that h(M) ≤ 0.05 (this needs k ≥ 8 at N = 300; publish the inequality). Recompute P(not covers) at that floor and put it in the 0.05. Define the projected bands, or drop band readings for K_C and say so in §6.2.

**S3. MAJOR. The 0.025 joint size is the Gaussian, draw-matched-to-V size. PV's toys are not those toys, and the candidates are built to be wider than V.** Decl:315–318, 366–369.
- COV2D §5.2 refused a fixed 0.6827 null for these draws. Flux and pair bands are un-centred, clipping truncates shifts, and C08, C_model, and the simulation-statistics part of C_stat sit in the matrix and not in the toys. The first two can move the flag rate either way. The not-drawn positive pieces push counts into the region, which is the over-flag. COVFIX grades PV with the fixed Gaussian 0.6827 anyway.
- The pre-binding check (decl:366–369) is Gaussian draws from V, plus residuals whitened and recoloured to V. Recolouring to V removes the covariance mis-match the check is supposed to measure. It does not run `cov2d.draw`, so it never sees clipping or the un-centred flux. A measured rate below 0.20 on that ensemble does not bound PV.
- Independence across the three truths (decl:363) is false: one V, one estimator, one GENIE family. For an upper bound, use the union bound 3×0.05 = 0.15 and 3×0.025 = 0.075. Those still round to the printed 0.14 and 0.07. The independence sentence is wrong; the number barely moves. This part is minor and is listed here so it is not "fixed" by repeating 0.14.
- P-3's over flag fires on about 2% extra variance (S-opening above, D1). Section 6.4's false-FAIL calculation is for a V that matches the toys exactly. K_B is built only to widen (max and, if it survived, B3). The calculated 0.025 is not the false-INFLATED rate of the candidate the plan submits.

Fix: grade PV with a draw-matched null, as COV2D did, built from the frozen draw list before any PV toy is read. Make the pre-binding ensemble that draw, including clipping, run before binding, and refuse to bind if its three-truth not-VALIDATED rate exceeds the director's mark. Quote the union bound, not an independence assumption.

**S4. MINOR. Mode dependence does not break the Bonferroni expectation, and the ndf used in §6.4 is the right one only for a frozen full-rank cut.** E[number of false under-flags] ≤ 0.025 by linearity, dependence or not, under the per-mode marginal null. Dependence does break SE(M) = √(2/(N·ndf)) when the z_i are not independent χ²(1) pieces, which is the non-Gaussian case S3 already covers. ndf after the cut is fixed before PV if V is frozen, so the "random ndf" worry does not arise for a frozen candidate. It does arise for B3 (D2), because the floor changes the cut. No separate fix beyond D2 and S3.

**S5. MINOR. The sample-covariance divisor in the debias step is unnamed.** Decl:264, "b̂b̂ᵀ − S_t/N_t". This is unbiased for bbᵀ when S is the 1/(N−1) sample covariance. REGRADE uses divisor n for its spread piece (REGRADE §4). One sentence should say which divisor §5.2 uses. Separately, q_i = mean z² equals m_i² + ((N−1)/N) v_i when v_i is the 1/(N−1) variance, so the reported split of M into mean m² and mean v (decl:326) does not add to M. Use one divisor everywhere and print the identity.

---

## 6. Prices and stop rules

**The node-hour products that use 0.19 are consistent, with one rounding.** 0.19 × 200 = 38, × 400 = 76, × 900 = 171, × 600 = 114. N1+N2+N4+A1+N5 = 38+38+38+76+76 = 266, plus N3. N3 is 50 × 0.19 = 9.5, printed as 10 (decl:116). The P1 total 276 uses 10, so 1450 × 0.19 = 275.5 is printed as 276. Skipping N5: 276 − 76 = 200 (decl:79). Totals with PG taken as 2.0: 2+276+171 = 449 and 2+200+171 = 373 (decl:83). Lean: 2+200+114 = 316 exactly; 276+114+2 = 392, and the draft says "about 393" (decl:90–91). Half of 725.6 is 362.8 (decl:88). Every listed phase price and every listed cap (PG 3, P1 320, PV 200) is below 362.8. The total 449 is not, and the draft says so and sends the total to Joseph. That part of the half-balance rule is internally consistent and depends on the uncited balance in F7.

**P1. MINOR. The PG range is not added the same way in the two totals.** The full total uses the bottom of PG's 2.0–2.5 range. The lean total's "about 393" is 392 at 2.0 and 392.5 at 2.5, or 393 if someone adds the cap 3. Fix: print both totals as a range over PG ∈ [2.0, 2.5], and price N3 at 9.5 or price every cell as n × 0.19 with one stated rounding rule.

**P2. MAJOR. A phase cannot pass its cap silently if ST3 is implemented. It can pass its quoted price, and the sum of phases has no gate.** Decl:149–150, 93–94, 88–89.
- ST3 stops a phase when sacct exceeds that phase's cap, and the gate re-prices before submission. That catches a cap overrun. It does not catch P1 spending 320 against a quoted 276 (44 node-h), or PV spending 200 against a quoted 171 (29 node-h). Those gaps are inside the cap and do not go back to the director.
- Nothing adds sacct across P0, PG, P1, and PV and refuses at 449 or at 362.8. "The director brings Joseph the total before any compute" (decl:89) is a social step. It is not one of the guard refusals in ST5.
- The sim-stat switch (decl:176–178) can make each PV toy heavier than the COV2D toy the 0.19 was measured on, after Joseph has been shown 171. The cap at 200 is the only backstop.
- N5's skip is decided after N1 and N2 are read (decl:122). The draft does not say N5's jobs are withheld until that read. A single P1 submission launches all 1450 toys, the skip never happens, and the spend is the high number by accident.
- Cap 0 on P0 and P2 is real only if the same gate wraps login work. The draft does not say it does.

Fix: Joseph's go on a named total is an ST5 control, checked on the connect before PG, P1, and PV. Cumulative sacct refuses at that total. The PV re-price after the sim-stat decision is a new number Joseph sees before PV is submitted, and a rise above the approved total stops the phase. N5 is a separate submission after the N1/N2 reading. Price N3 as 9.5 so the cell prices add to the phase price.

**P3. MINOR. PG's cap of 3.0 is tight only if the F1 OOM pattern returns.** The repaired F1 pipeline cost 1.3275 for two tunes, which is the 0.66 figure. Three tunes at that rate sit near 2.0, inside 2.0–2.5, under cap 3.0. The cap does not need a change. The regen-after-purge case in B2 is the way PG overruns for a reason other than gevgen.

---

## 7. What blocks binding, and what does not

**BLOCKING (do not bind until each has a numbered change in the draft):**
1. Validation list contains G18_10b, an FSI twin of spent G18, and §5.4 lets G18 and AR23 choose the candidate (B1). Fix: distant qualifiers only; spent tunes descriptive, not a pass/fail bar.
2. Custody is open and leaky: unnamed generator, optional HPSS, counts in the F1 logs, seeds uncommitted (B2). Fix: close §9.1 as specified there.
3. ST1 skips N5 on "covers", which is where the draft's own 0.44 factor hides a real under-coverage, and N5 plus outcome A contradicts the standing KI 85 deferral (S-ST1, F3). Fix: N5 always runs; no construction error from N1/N2 alone; a Joseph decision if this re-test is allowed before publication.
4. B3 is a φ grid fit until the spent tunes pass (D2). Fix: delete B3.
5. K_B's max(λ_i, ŝ_i) plus a mis-named Ledoit–Wolf step is upward-biased by enough that the joint over-flag fires, and PV's draw list does not match N4 (D1). Fix: univariate variances, raise λ only past the guard, same sources in Ŝ and in PV.

**MAJOR (fix in this revision; each one changes a bar, a citation, or a claim the readout would quote):**
- F1 SuSAv2 overlap, F2 the wrong "nearest GENIE 2.12" tune, F4 tune_v1 / `_sq` unsupported, F5 b1 stated as done, F6 τ "cannot move any reading" against the G18 cut block, F7 uncited balance 725.6.
- B3 spent-once has no definition of a read, no ban on pre-PV amendments that retune §5, and no verdict when only two qualifiers exist.
- D3 nominal-only fluctuation, D4 laterals and normalization not in the bullets, D5 one-sided build bars and P-2/P-4, D6 A1 is not an out-of-sample alternative truth, D7 band "covers" undefined.
- S2 no floor on K_C's k, S3 Gaussian 0.6827 null and a recolouring check that cannot see `cov2d.draw`.
- P2 no cumulative sacct ceiling and no hold on N5 until N1/N2 are read.

**MINOR (do not block; correct while editing):**
- F8 (16-cell figures absent from this packet, consult citation, tolerance document name, "final letter", "b1 style", the 20% mark).
- S4 mode-dependence does not break the Bonferroni expectation; S5 name the covariance divisor and make the m² + v split add to M.
- P1 print the PG range on both totals and stop rounding 9.5 to 10 in only one cell; P3 no cap change.
- The §6.4 products 0.006, 0.011, 0.037, 0.072, 0.01, 0.14, 0.07, 0.10, and 0.05 are arithmetically right under the Gaussian assumptions written next to them. Keep the numbers. Replace the assumptions that S2 and S3 show are false. The "about 5σ" clause at decl:358 should say "about 3.5σ to lose the guarded covers label at k = 5; the point estimate reaches 0.8 at about 5.5σ".

Nothing in the checked COV2D, T2A, REGRADE 2D, G2R, 10-05, or F1 charge figures needs a correction. The NO-GO is the design of the validation, the stop rule, and the fluctuation estimator, plus the citations in F1–F7 that those sections rest on.
