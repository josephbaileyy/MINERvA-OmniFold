# COVFIX declaration, DRAFT rev 0: the 2D covariance fix (2026-11-22)
<!-- absence-ok: a draft declaration of studies not yet run; every existing study is routed to INVENTORY.md -->

<!-- absence-ok: scoping statement about studies not yet run or not run as scoped, each routed to its record -->
**Status: DRAFT.** Not bound. No code is written, nothing is computed, and no cluster connect is made under it.

**By** the `cov2d` session, at the director's request of 2026-11-22. Joseph authorized starting the design phase, via
the director, after an outside review of the note asked for its "Fix 1". The inventory this draft builds on is
`INVENTORY.md` in this directory, read at origin/main `7d5a98361`.

**CITABLE FOR:** nothing yet. Once bound and run: the readings in §6 and only the sentences §7 licenses for them.

**NOT CITABLE FOR:**
- any note or paper wording;
- adopting any covariance (adoption is Joseph's);
- a cause of the under-coverage;
- coverage at the data's own point, or for generators outside the validation family (§4.3);
- a p-value.

**Rules are fixed before computation.** Every reading, bar, candidate rule and stop rule below is fixed before the
first toy. A change after any phase's output exists needs a numbered amendment that names the output already seen.

## 1. What the review asked, and what the inventory already settles

The review's Fix 1 separates bias from fluctuation:
E[(σ̂ − σ)(σ̂ − σ)ᵀ] = C_fluct + b bᵀ.

Its acceptable outcomes:
- **(A)** a construction error, found and fixed;
- **(B)** the covariance holds for a stated model class, with the truth-model bias quantified separately;
- **(C)** reported uncertainties for coarser or selected combinations only.

It rejects scaling the covariance until the two tunes pass.

The inventory settles four points before any design choice:
1. **The fluctuation is under-described, not only the bias** (T2A). At the held-out tunes the spread per component in
   C_T's eigenbasis is 1.6 / 3.0 / 4.4 (AR23) and 1.5 / 3.6 / 4.7 (G18) over ranks 1–73 / 74–139 / ≥ 140. A fix that adds
   only b bᵀ is therefore ruled out, and every candidate in §5 has a fluctuation part.
2. **C_run is negligible in 2D**: τ = 0.0098 per ndf at both tunes (REGRADE 2D).
3. **G18 and AR23 are spent.** COV2D, T2A, G2R, REGRADE and LL5D have all read them. They may build a construction; they
   may not validate one.
4. **Never-read truths are cheap.** F1 generated both GENIE v3 tunes for 1.3275 node-h in total.

## 2. Notation and the carried covariance

- **Truth and toys.** For a truth t and a toy s, the error is e_s = σ̂_s − σ_t on the 205 reported cells.
- **Bias and spread.** b̂_t = mean_s e_s, and S_t = the sample covariance of e_s.
- **The carried covariance.** V_t is a candidate covariance carried to truth t by REGRADE's fractional carry
  (REGRADE-DECLARATION.md §2). For nominal truth, t is the MC truth x_MC.
- **The eigenbasis.** V_t = Σ λ_i u_i u_iᵀ, with rank 1 the largest. The cut is REGRADE's: modes below 1e-12·λ₁ are
  dropped, giving ndf.
- **Per mode and toy:** z_{s,i} = u_iᵀ e_s / √λ_i.
- **Per mode:**
  - m_i = mean_s z_{s,i} (bias);
  - v_i = var_s z_{s,i} (fluctuation ratio);
  - q_i = mean_s z²_{s,i} (total).
- **Bands:** R1 = ranks 1–73, R2 = 74–139, R3 = ≥ 140, which are T2A's split. Q_R, F_R and B_R are the band means of
  q_i, v_i and m_i².
- **The mean ratio:** M = (1/ndf) Σ_i q_i, the mean χ²/ndf.
- **The guard,** in the b1 style: h(X) = t_{0.975, N−1} · SE(X), with SE from 2,000 toy-bootstrap resamples at a fixed
  seed. A label is read only if [X − h, X + h] lies inside one label's interval. Otherwise the reading is "unresolved
  across <labels>".

## 3. Phases, in order

| phase | what | node-h price | cap |
|---|---|---|---|
| **P0** | re-analysis of committed records (§3.1) | 0 (local) | 0 |
| **PG** | generate and seal the validation truths (§4) | 2.0–2.5 | 3.0 |
| **P1** | construction measurements: the matrix cells at nominal and at the build truths (§3.2) | 200 (+76 if N5 runs) | 320 |
| **P2** | build and freeze the candidates (§5) | 0 (local) | 0 |
| **PV** | validation toys at the sealed truths, then the readout (§6) | 171 | 200 |

- **Totals:** 373 without N5 and 449 with it, against the balance of 725.6 node-h.
- **The half-balance rule.** Every phase is below half the balance (362.8). P1's cap of 320 is under it, but the total is
  not. The director brings Joseph the total before any compute.
- **A lean option,** for Joseph to choose instead: two validation truths (PV 114) and no N5 gives a total of about 316.
- **The toy price** is the director's planning figure of 0.19 node-h per toy, from COV2D's 112.74 node-h over 27
  attempts. That figure includes pilots and retries, so it is conservative per toy. Each phase's gate re-prices from
  sacct before submission, as COV2D's did.

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

These numbers are needed to set P1's expectations and to build the candidates; they validate nothing.
- The per-mode profiles (m_i, v_i, q_i) of COV2D's committed errors, `fd/tier2-20261110/t2a/<T>/E_<T>.npz`, under:
  - Q_R carried to T;
  - C_T;
  - G2R's C_T′.
- IBUKT A2's seven mean residual vectors (`state/2d-closeout/ibukt-a2/readout.json`), times E_R, in Q_R's modes: m_i only,
  since there are 5 draws.
- c2 as scoped: T2A's mean error projected on C_run's two directions.

### 3.2 P1: the construction measurements (the review's matrix, plus the never-drawn sources)

Each cell is a toy ensemble unfolded by the production procedure (re2_driver.py, E_R's argv). Each toy has its own
seeds, disjoint from every committed ensemble. Every cell's reading is §6.1's, against the named reference block.

| cell | truth | what each toy draws | toys | reference block it tests | node-h |
|---|---|---|---|---|---|
| **N1** data stream | nominal (MC truth) | Poisson pseudo-data at data size, from the MC reco weights | 200 | S1's data stream | 38 |
| **N2** data + simulation statistics | nominal | N1, plus Poisson redraws of the signal and background simulation weights by S1's three-stream code at fresh seeds (the response's simulation statistics) | 200 | S1 (all three streams) | 38 |
| **N3** estimator seed C08 | nominal | one fixed N1 pseudo-dataset; estimator seed varied over 50 seeds disjoint from C08's | 50 | C_seed (C08) | 10 |
| **N4** coherent nuisances | nominal | N2, plus all 38 systematic bands drawn per toy by COV2D's `cov2d.draw` at r_T ≡ 1 | 200 | S1 + C_syst + C_seed | 38 |
| **A1** alternative truth, fixed response | genie_mec, nuwro, gibuu, tune_v1 (the PV2D maps, C_model's members) | N1 only, response nominal | 4 × 100 | S1's data stream (spread); C_model (bias) | 76 |
| **N5** held-out simulation (KI 84/85) | nominal, MC half A | pseudo-data from half A, unfolded with half B's response, plus 200 half-B bootstrap replicas for that configuration's own S1 | 200 + 200 | the half-B S1 | 76, conditional |
| **existing** alternative truth, perturbed response | G18, AR23 | COV2D's toys (data Poisson + 38 bands) | 300 + 300 | C_T, Q_R (P0) | 0 |

- **N5 runs only if** N1 or N2 reads "under" or "over" in R1 (§6.1). It separates KI 85's explanations: (a) the
  bootstrap over-scatters, or (b) same-event pseudo-data under-scatter.
- **Without N5,** N1 and N2 carry KI 85's caveat. Same-event pseudo-data may under-scatter, so a ratio below 1 there is a
  bound, not a measurement.
- **C_PL and C_run are not drawn,** because they have no generative law (SCOPING a3). They enter every V as covariance
  only. τ = 0.0098 says they cannot move any reading here.

### 3.3 Stop rules

- **ST1, construction error.**
  - Trigger: N1, N2, N3 or N4 reads "under" or "over" in R1 against its own reference block, at nominal truth, where
    nothing but the drawn sources acts.
  - Action: P2 and PV wait. The cell that first moves the reading localizes the block. A fix goes to the director as an
    amendment before any further compute; this is outcome A's path, §7.
  - R2 and R3 readings at nominal are recorded but do not trigger ST1, since those modes are poorly determined by
    construction.
- **ST2, no admissible candidate.**
  - Trigger: at P2, no candidate meets §5.4's build-set bars.
  - Action: PV does not run. The result is "none" (§7), at the P1 spend.
- **ST3, caps.** Every submission is gated against its phase cap from sacct, as COV2D's gate did. Exceeding a cap stops
  the phase and goes to the director.
- **ST4, validation is spent once.**
  - PV's toys are read once, at the frozen candidates' shas.
  - After the read, no candidate may be changed and re-read against the same truths. Any later construction needs new
    sealed truths.
- **ST5, guard refusals are terminal** for their phase, as in every lane connect: the fence, atime, provenance and A0
  controls.

## 4. The validation truths

### 4.1 Which, and how many

- **Three** never-read GENIE v3 tunes, so that no single tune decides the result.
- **They are chosen by rule, before anything is generated,** from the tune qualifiers the genie_xsec `v3_04_00` product
  on Perlmutter actually provides, which F1's source is (FD-F1-DECLARATION.md:76). The order of preference, fixed now,
  is:
  1. `G21_11b_00_000` (SuSAv2 quasielastic and 2p2h: a family outside C_model and outside G18/AR23);
  2. `G18_10b_02_11b` (G18's model with hN intranuclear cascade, where G18_10a uses hA);
  3. `G18_02b_02_11b` (the empirical-MEC "GENIE 2-like" configuration with hN);
  4. `G18_02a_02_11b`, as a fallback only. It is closest to C_model's GENIE 2.12 member, and its use is disclosed.
- The first three present are used. The check is a stat-only login probe that lists the qualifiers, and it reads no
  spline content.
- **If fewer than two are present,** PG stops and goes to the director.

### 4.2 Custody: generated and sealed before any candidate exists

- **Who generates.** PG is run by a session other than cov2d (proposed: tier3-design or limitation-resolver, whichever
  the director names), with F1's bound pipeline unchanged except for the tune names and fresh seeds. F1 is
  `gen5d_v3.py`, `run_gevgen_v3.sh`, the pv-ladder ratios and the bridge, and it costs about 0.66 node-h per tune.
- **What is sealed.**
  - Each tune's products are the reduced splines, gst, gen5d and the bridged 5D ratio, plus its 2D map.
  - Their sha256 list is committed as `PG-SEAL.sha256` **before P1's first connect**.
  - The products stay on pscratch and HPSS. The ratio files are not committed to the repo until PV's readout is
    committed.
- **Who may read them.** No one reads a sealed product's content until PV. That includes cov2d and the generating
  session beyond its own sampled-spectrum and header checks, whose outputs are pass/fail and counts only.
- **Seen versus touched.** The seal is checked by sha256 at PV's connect. Atime on the sealed set is recorded at seal
  time and checked unmoved at PV, with O_NOATIME reads, as the COV2D connects did. A moved atime is a guard refusal.
- **Which code reads them.** PV's bulk and readout read the sealed truths only at the bound, frozen candidate shas of §5.

### 4.3 What the validation family can and cannot show

The three tunes are GENIE v3 configurations, and they share GENIE's framework with G18 and AR23. A pass licenses the
covariance for this family of models (outcome B's "stated model class"), not for any generator. A non-GENIE validation
truth would need a generator sample this project does not have; that is disclosed, not tested.

## 5. Candidate constructions, built only from P0 and P1, frozen at P2

**The build set** is N1–N5, A1's four truths, and COV2D's G18 and AR23 toys. Nothing in PG's seal is read.

### 5.1 K0, the control

K0 is the current Q_R, unchanged. Its expected reading at the unseen truths is "under", as at G18 and AR23. **If K0 reads
"covers" at all three, the validation family is too close to nominal to test anything.** That makes PV inconclusive,
and §7 licenses nothing.

### 5.2 K_B: fluctuation fixed, bias added (one candidate, chosen at P2 by rule)

**Fluctuation part V_F.** Start from Q_R with any ST1 fix applied (K_A). Then, in V's eigenbasis, set each mode's
fluctuation variance to max(λ_i, ŝ_i), with ŝ_i = u_iᵀ Ŝ u_i from N4's toys (all drawable sources at nominal).
- This is measured at nominal truth from fluctuation sources only. It is not tuned to any tune's pass.
- It is per-mode, not a uniform scale; the review rejects a uniform scale.
- N3's seed spread enters through C_seed, as measured.
- **Shrinkage.** Ŝ is shrunk toward diag(Ŝ) by the Ledoit–Wolf estimator. N4 has 200 toys on 205 cells, so Ŝ is
  rank-deficient.

**Bias part C_b,** from the truth family F = {genie_mec, nuwro, gibuu, tune_v1 (A1), G18, AR23 (COV2D)}. Each b̂_t is
debiased by its own sampling term (b̂ b̂ᵀ − S_t/N_t). There are three variants, fixed now:
- **B1 (mean outer product):** C_b = (1/|F|) Σ_t b̂_t b̂_tᵀ (debiased).
- **B2 (envelope):** C_b = Σ_i max_t (u_iᵀ b̂_t)² u_i u_iᵀ, the per-mode maximum over F.
- **B3 (eigenvalue floor):** no explicit b. Instead λ′_i = max(λ_i^F, φ · λ_73^F) for ranks above 73, with φ the smallest
  value on the grid {1, 2, 5, 10, 20, 50, 100} that meets §5.4 on the build set.

**The P2 choice among B1–B3** is the variant that meets §5.4 on the build set with the smallest log det(V)/ndf increase
over K_A, that is, the least inflation. Ties go in the order B1, B2, B3. The chosen variant is K_B, and only K_B goes to
PV.

### 5.3 K_C: reduced reporting (outcome C)

- **The subspace P_k:**
  - the measurability study's well-constrained directions of the response, if its result is committed before P2's
    freeze, with k fixed by that study's own rule;
  - otherwise K_B's top-k eigen-directions.
- **The choice of k** is the largest value such that, on every build truth, the projected readings meet §5.4.
- **What K_C reports:** K_B restricted to P_k, plus the combinations' definitions. No uncertainty is reported outside P_k.

### 5.4 Build-set bars (P2 admission, in-sample)

A candidate is admissible only if, at every build truth and at N4:
- M lies in [0.8, 1.25];
- every band Q_R is at most 1.5;
- under the joint rule of §6.1, the reading is not "under".

These are in-sample, so they admit a candidate; they never pass one.

### 5.5 Freeze

At P2's end, the code and the arrays defining K0, K_A, K_B and K_C are committed, with sha256, in `P2-FREEZE.sha256`,
and bound by the director before PV's first connect. Nothing in §5 may change afterwards (ST4).

## 6. Readings and bars, fixed now

### 6.1 Per cell (P1) and per truth (PV), against a covariance V

**Mean ratio M.** It is labelled by the interval in which [M − h, M + h] lies:

| label | M |
|---|---|
| over | < 0.8 |
| covers | [0.8, 1.25] |
| under | > 1.25 |

Otherwise the reading is "unresolved across …". The 1.25 is the practical tolerance: 25 % excess χ² is about 12 % excess
σ.

**Band readings.** Q_R, F_R and B_R are reported for R1, R2 and R3, each with the same guard. A band reads "under" if
Q_R − h > 1.5, and "over" if Q_R + h < 0.67.

**Joint coverage.**
- The region is χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827).
- Under-coverage is flagged if the joint count ≤ k_J, the largest k with P(Bin(N, 0.6827) ≤ k) < 0.025.
- Over-coverage is flagged if the joint count ≥ k_J⁺, the smallest k with P(Bin(N, 0.6827) ≥ k) < 0.025.

**Per-mode coverage.**
- The count is #{s : |z_{s,i}| ≤ 1} per mode.
- A mode is flagged "under" if that count ≤ k_c, the largest k with P(Bin(N, 0.6827) ≤ k) < 0.025/ndf, and "over"
  symmetrically.
- Flags are reported per band.

**The split** of M into (1/ndf)Σm_i² (bias) and (1/ndf)Σv_i (spread) is reported with its guard. It is descriptive.

### 6.2 PASS at an unseen truth (PV)

A candidate passes at truth u if all of the following hold:
- **P-1:** M reads "covers";
- **P-2:** no band reads "under";
- **P-3:** joint coverage is flagged neither "under" nor "over";
- **P-4:** at most 2 modes are flagged "under". Under correct coverage the expected number of false flags across all modes
  is at most 0.025.

For K_C, every reading is taken on P_k with ndf = k.

### 6.3 The PV verdict per candidate

| verdict | condition |
|---|---|
| **VALIDATED** | PASS at all three truths (or at both, in the lean option) |
| **FAILS** | P-1 reads "under" at any truth, or P-3 flags "under" at any truth |
| **INFLATED** | P-1 reads "over", or P-3 flags "over", at any truth, with no "under" |
| **UNRESOLVED** | otherwise |

## 7. What each outcome licenses (b1 style; adoption and wording remain Joseph's and the director's)

The candidates are read in the fixed order K_A, K_B, K_C. The first VALIDATED is the result. The others are reported
descriptively, and the multiplicity of three candidates is disclosed.

<!-- absence-ok: scoping statement about studies not yet run or not run as scoped, each routed to its record -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | ST1 fired, the fix was amended in, and K_A is VALIDATED | "The 2D covariance had a construction error in <block>, located at nominal truth by cell <N>; corrected, it covers three held-out GENIE v3 tunes at the stated level." | a claim about non-GENIE truths; coverage at the data |
| **A, partial** | ST1 fired and was fixed, but K_A is not VALIDATED | "A construction error in <block> was found and corrected; the corrected covariance still does not cover held-out tunes." Then B or C is read next. | "fixed" in the coverage sense |
| **B** | K_B is VALIDATED | "With a truth-model bias term built from <F> and the fluctuation part measured at nominal, the covariance covers three held-out GENIE v3 tunes; the bias term is reported as a separate block." | coverage outside the GENIE v3 family; a cause of the bias |
| **C** | K_B is not VALIDATED and K_C is VALIDATED | "Uncertainties are reported for the k combinations P_k, which cover the held-out tunes; finer combinations carry no validated uncertainty." | any statement about directions outside P_k |
| **none** | nothing VALIDATED, or ST2 | Nothing new. The note's "coverage remains unvalidated" stands, with P1's matrix readings as description. | any covariance change |
| **inconclusive** | K0 reads "covers" at all validation truths | Nothing. The validation family did not test the covariance. | — |

**UNRESOLVED** at any truth means more toys could resolve it. That needs an amendment and a price, never a re-read.

## 8. Code, tests and audit before any compute

- **Reused unchanged where possible:** re2_driver.py `--data-file`, cov2d_writer, `cov2d.draw` (with r_T ≡ 1 for N4),
  S1's three-stream bootstrap code (for N2's simulation streams), F1's pipeline (PG), and the REGRADE carry.
- **New code:**
  - the N-cell and A1 toy writers (a fixed-response mode with no band draw);
  - the N3 seed arm;
  - the N5 split;
  - the §6 readout;
  - the §5 builders;
  - the PG seal checker.
- **Each needs** unit tests, a line trace of every new line, hand mutants (all killed), a Grok and an agy read, the
  director's binding, and per-connect fences.
- **A0-type controls in every readout:**
  - the readout reproduces COV2D's committed M at G18 and AR23 from E_<T>.npz to the κ-scaled tolerance
    max(1e-9, 10 κ₂ ε) (T2-BINDING-1 addendum 1);
  - numpy against scipy `evr` mode agreement, as in T2A.

## 9. Open items for the director's read

1. **Who runs PG** (§4.2), and whether the sealed products may sit only on pscratch plus HPSS until PV.
2. **The bars:** 0.8 / 1.25 for M, 1.5 for a band, ≤ 2 flagged modes. These are proposals for the reads to challenge.
3. **Full or lean:** three validation truths and N5 conditional (up to 449 node-h), or the lean option (about 316).
4. **N2's simulation streams.** Is S1's three-stream code the right model for the response's simulation statistics,
   given that C_stat's MC part is that code's output? It measures how well the bootstrap predicts the estimator's
   scatter under fresh redraws. It is not circular in the KI 85 sense, because the toys' seeds are disjoint from S1's.
5. **The tune descriptions in §4.1** (SuSAv2, hN against hA, empirical MEC) are from memory of GENIE's tune list. They
   must be checked against GENIE's documentation before binding; the choice rule uses only the names.
6. **Whether the measurability study's directions** (tier3-design) should be K_C's only subspace, or one of two frozen
   options.
