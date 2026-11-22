# COVFIX declaration, DRAFT rev 2: the 2D covariance fix (2026-11-22)
<!-- absence-ok: a draft declaration of studies not yet run; every existing study is routed to INVENTORY.md -->

<!-- absence-ok: status line of an unrun draft -->
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

**Rev 2** answers the Grok and agy reads of rev 1 (`5458805b4`). Both returned NO-GO, and both reports are in `reads/`.
The changes, each by finding:
- **The validation set** is two tunes whose CCQE or 2p2h model differs from the spent tunes'. G18_10b, an FSI twin of
  spent G18, is removed (Grok B1, agy B5b). §4.1.
- **The spent tunes no longer choose anything.** G18 and AR23 enter the bias term as building data, but every P2
  admission bar and choice uses only the P1 ensembles; G18 and AR23 are printed descriptively (Grok B1). §5.
- **B3, the eigenvalue floor, is deleted** (Grok D2, agy B1).
- **The fluctuation part is rebuilt.** Fluctuation and bias are now separate: C_model is removed from the fluctuation
  part, which is corrected by per-band factors from a pooled, unbiased spread estimator, applied only past a guard.
  There is no per-mode max and no Ledoit–Wolf (Grok D1, agy B2). The bias part is projected to PSD (agy B3). §5.2.
- **Truth-dependent spread** is measured at non-spent, non-validation truths: A1p, the C_model vertices with
  perturbed response (Grok D3). §3.2.
- **One source list everywhere.** N4, A1p and PV draw the same sources, including the lateral surrogate and the 1.4 %
  normalization, with no conditional switch (Grok D1, D4; agy MAJOR-3). §3.2, §3.4.
- **N5 always runs,** and no N1 or N2 label is a construction error. Construction-error readings use the spread only,
  each against its own block, with written subtractions (Grok S-ST1, agy B4). §3.3.
- **KI 85's deferral** needs Joseph's decision, because N5 is that re-test (Grok S-ST1). §9.
- **Custody:** a fresh generating session is required; seeds are pre-committed; the products are encrypted under a key
  the director holds; the HPSS copy is required; the PG logs are boolean only; a purge stops the study (Grok B2,
  agy B5a). §4.2.
- **"Spent once" is defined:** one readout JSON with no per-toy arrays, a guarded second invocation, and no amendment
  to §5–§7 after binding (Grok B3). §3.3.
- **The bars are symmetric:** joint "over" refuses at P2 and PV, a band "over" refuses, and P-4 allows no
  under-flagged mode. The joint null is draw-matched. K_C has a floor of k ≥ 10, and its empty bands are defined (Grok
  D5, S2, S3; agy MAJOR-1, 2, 4). §5.4, §6.
- **Prices:** P1 runs in two waves; a cumulative sacct ceiling at Joseph's approved total is a guard; the balance's
  source is cited (Grok P2, F7; agy B6). §3.
- **Fidelity:**
  - the SuSAv2 overlap with AR23 is stated (Grok F1);
  - the GENIE 2.12 neighbour claim is removed (F2);
  - KI 85 is quoted exactly (F3);
  - tune_v1 and `_sq` are dropped as truths (F4);
  - the τ claim is removed and cut diagnostics are added (F6);
  - citations are fixed (F8, agy MINOR-2);
  - F5 is answered with a citation, not a change: b1 did run (merged in #1242), and the inventory now cites its REPORT;
  - one divisor is used throughout (S5).

<!-- absence-ok: rule statement -->
**Rules are fixed before computation.** Every reading, bar, candidate rule, seed and stop rule below is fixed at
binding, before P0. After binding, §5–§7 may not be amended (§3.3, ST4). Any other amendment names every output
already seen.

## 1. What the review asked, and what the inventory already settles

The review's Fix 1 separates bias from fluctuation:
E[(σ̂ − σ)(σ̂ − σ)ᵀ] = C_fluct + b bᵀ.

Its acceptable outcomes:
- **(A)** a construction error, found and fixed;
- **(B)** the covariance holds for a stated model class, with the truth-model bias quantified separately;
- **(C)** reported uncertainties for coarser or selected combinations only.

It rejects scaling the covariance until the two tunes pass.

The inventory settles four points:
1. **The fluctuation is under-described, not only the bias** (T2A). At the spent tunes the spread per component in C_T's
   eigenbasis is 1.6 / 3.0 / 4.4 (AR23) and 1.5 / 3.6 / 4.7 (G18) over ranks 1–73 / 74–139 / ≥ 140. So every candidate
   has a fluctuation part, and P1 measures whether that excess exists at nominal (N4) and at other truths (A1p).
2. **C_run's trace is small in 2D:** τ = 0.0098 per ndf at both tunes (REGRADE 2D). The G18 regrade still moved C_T's
   kept subspace (142 kept modes outside the new span), so a small trace is not a small change of eigenbasis. Every
   candidate prints the cut diagnostic (§6.1).
3. **G18 and AR23 are spent.** They may build; they may not validate or select.
4. **Never-read truths are cheap.** F1 generated both GENIE v3 tunes for 1.3275 node-h in total.

## 2. Notation and the carried covariance

- **Truth and toys.** For a truth t and a toy s = 1…N, the error is e_s = σ̂_s − σ_t on the 205 reported cells.
- **One divisor throughout.** b̂_t = (1/N) Σ_s e_s, and S_t = (1/N) Σ_s (e_s − b̂_t)(e_s − b̂_t)ᵀ.
- **The carried covariance.** V_t is a candidate covariance carried to truth t by REGRADE's fractional carry
  (REGRADE-DECLARATION.md §2). For nominal truth, t is the MC truth x_MC.
- **The eigenbasis.** V_t = Σ λ_i u_i u_iᵀ, with rank 1 the largest. The cut is REGRADE's: modes below 1e-12·λ₁ are
  dropped, giving ndf.
- **Per mode and toy:** z_{s,i} = u_iᵀ e_s / √λ_i.
- **Per mode:**
  - m_i = mean_s z_{s,i};
  - v_i = (1/N) Σ_s (z_{s,i} − m_i)²;
  - q_i = mean_s z²_{s,i}.
  - Then q_i = m_i² + v_i exactly.
- **Bands:** R1 = ranks 1–73, R2 = 74–139, R3 = ≥ 140 (T2A's split). A band is used only if it holds at least 10 kept
  modes; otherwise it is dropped and named as dropped. Q_R, F_R and B_R are the band means of q_i, v_i and m_i².
- **The mean ratios:** M = (1/ndf) Σ q_i, the mean χ²/ndf, and the spread ratio F = (1/ndf) Σ v_i.
- **The guard,** as in b1's declaration (`state/2d-closeout/b1-a2-projection-20261122/DECLARATION.md` rev 2): h(X) =
  t_{0.975, N−1} · SE(X), with SE from 2,000 toy-bootstrap resamples at seed 9_990_000. For a difference of two
  independent ensembles, SE² is the sum.
- **Labels** for M, F, a band ratio, or a block ratio X:

  | label | X |
  |---|---|
  | over | < 0.8 |
  | covers | [0.8, 1.25] |
  | under | > 1.25 |

  A label is read only if [X − h, X + h] lies inside one label's interval. Otherwise the reading is "unresolved across
  <labels>". Bands use the same rule and the same edges; there is no separate band convention.

## 3. Phases, in order

| phase | what | price, full (node-h) | price, lean | cap, full / lean |
|---|---|---|---|---|
| **P0** | re-analysis of committed records (§3.1) | 0 (local) | 0 | 0 |
| **PG** | generate, encrypt and seal two validation truths (§4) | 1.3–2.0 | 1.3–2.0 | 3.0 |
| **P1 W1** | N1, N2, N5, N3 (§3.2) | 161.5 | 123.5 | — |
| **P1 W2** | N4, A1f, A1p (§3.2), after ST1 is read on W1 | 129.2 | 85.5 | — |
| **P1** | total | 290.7 | 209.0 | 330 / 240 |
| **P2** | build and freeze the candidates (§5) | 0 (local) | 0 | 0 |
| **PV** | validation toys at the two sealed truths, then the readout (§3.4, §6) | 114 | 114 | 135 |

- **Totals:** full 406.0–406.7; lean 324.3–325.0. The ranges come from PG's range only.
- **Every cell is priced at n × 0.19,** with no rounding. 0.19 node-h per toy is the director's planning figure:
  COV2D's 112.74 node-h over 600 toys is 0.188, and that includes pilots and retries.
- **Lean** sets N1, N2 and N4 to 150 toys each and N5 to 150 + 150, and drops A1f. Cell 4 then rests on IBUKT A2's
  committed 5-draw means, descriptively.
- **The balance.** The director's message of 2026-11-22 gives 725.6 node-h, from the iris row read at limitation-
  resolver's S1 survey (login23, 2026-11-22T22:01:53Z). That row is not yet committed. **Binding requires a committed
  iris receipt.** Half of 725.6 is 362.8.
- **Against half the balance:** every phase and every cap is below 362.8. The full total is above it and the lean total
  below it. Joseph chooses before any compute.
- **ST6, the cumulative ceiling,** is a guard (§3.3). Joseph's approved total is pinned in every connect. Each connect
  sums sacct over the campaign's job-name prefix `covfix_` before submission, and refuses if the sum plus the
  submission's priced charge exceeds that total.

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

- The per-mode profiles (m_i, v_i, q_i) of COV2D's committed errors, `fd/tier2-20261110/t2a/<T>/E_<T>.npz`, under Q_R
  carried to T, under C_T, and under G2R's C_T′.
- The fluctuation part F_Q = Q_R − C_model, checked PSD (C-PSD: λ_min ≥ −1e-12·λ_max), with its cut diagnostic.
  **A failure stops at P0.** C_model is the block RE-2 part C built, which COV2D's C_T also carries.
- IBUKT A2's mean residuals (`state/2d-closeout/ibukt-a2/readout.json`), times E_R, in Q_R's modes: m_i only.
- c2 as scoped: T2A's mean error projected on C_run's two directions.

These validate nothing.

### 3.2 P1: the construction measurements

Each cell is a toy ensemble unfolded by the production procedure (re2_driver.py, E_R's argv). The seeds are
pre-committed below and are disjoint from every committed ensemble; a test checks them against COV2D's, C08's and S1's
seed lists.

**The full source list** is "data Poisson + bands + lateral + norm + sim", where:
- the bands are COV2D's 38: Flux (one of 100 universes, constraint-weighted), 2p2h (1 of 3), and the 36 others (one
  endpoint each), composed first-order on `w_reco`, `w_truth` and `w_bkg` by `cov2d.draw` (COV2D §4.2);
- lateral is COV2D's surrogate over 5 bands;
- norm is x̂ × (1 + 0.014 z);
- sim is S1's signal and background simulation-weight Poisson redraws at fresh seeds.

| cell | truth | what each toy draws | toys full / lean | seed base | node-h full / lean |
|---|---|---|---|---|---|
| **N1** data stream, same-event | nominal | Poisson pseudo-data at data size from the MC reco weights | 200 / 150 | 9_100_000 | 38 / 28.5 |
| **N2** + simulation statistics | nominal | N1 + sim | 200 / 150 | 9_200_000 | 38 / 28.5 |
| **N5** data stream, held-out | nominal, MC half A | pseudo-data from half A, unfolded with half B's response; plus half-B bootstrap replicas for that configuration's own S1 | 200+200 / 150+150 | 9_500_000 (toys), 9_510_000 (replicas), 9_520_000 (split) | 76 / 57 |
| **N3** estimator seed | nominal | one fixed N1 pseudo-dataset (seed 9_300_100); estimator seeds 9_300_000–9_300_049 | 50 / 50 | — | 9.5 / 9.5 |
| **N4** all sources at nominal | nominal | the full source list, with r ≡ 1 | 200 / 150 | 9_400_000 | 38 / 28.5 |
| **A1f** alternative truth, fixed response | genie_mec, nuwro, gibuu (C_model's three PV2D vertices) | N1 only, response nominal, truth deformed by the vertex's 2D map | 3 × 60 / 0 | 9_600_000 + 10_000·j | 34.2 / 0 |
| **A1p** alternative truth, perturbed response | the same three | the full source list at the deformed truth | 3 × 100 / 3 × 100 | 9_700_000 + 10_000·j | 57 / 57 |
| **existing** | G18, AR23 | COV2D's toys (data Poisson + bands + lateral + norm; no sim) | 300 + 300 | committed | 0 |

- j = 0, 1, 2 for genie_mec, nuwro, gibuu.
- **A1f and A1p are in-sample.** Their truths are the shifts that define C_model. A1f measures the estimator's bias
  there (the review's cell 4, in-sample), and A1p measures the truth-dependent spread. Neither is a held-out truth; the
  held-out alternative truths are PV's.
- **C_PL and C_run are not drawn,** because they have no generative law (SCOPING a3). They enter every V as covariance.

### 3.3 Stop rules

**ST1, construction error.** It is read on W1 (N1, N2, N3, N5) before W2 is submitted, and on W2 for N4. Each reading
uses the spread only (v_i and F), never q, because nominal closure bias (IBUKT A2: up to 1.708 % noise-free) would
otherwise enter. Nominal bias is reported separately (m_i, B_R), descriptively.

| block under test | reading (R1 band mean of the per-mode ratio, guarded) | ST1 fires if |
|---|---|---|
| S1's data stream | N5: v_i against u_iᵀ S1_B u_i, with S1_B the half-B configuration's own bootstrap | N5 reads "under" or "over" |
| S1's simulation streams | (ŝ_i^{N2} − ŝ_i^{N1}) / u_iᵀ S1_sim u_i, with ŝ_i = λ_i v_i | it reads "under" or "over" |
| C_seed (C08) | ŝ_i^{N3} / u_iᵀ C08 u_i | it reads "under" or "over" |
| C_univ + C_lat + C_norm | (ŝ_i^{N4} − ŝ_i^{N2}) / u_iᵀ (C_univ + C_lat + C_norm) u_i | it reads "under" or "over" |

- The eigenbasis is Q_R's, carried to x_MC.
- **N1 is never a construction-error reading.** Its spread against S1's data stream is recorded with KI 85's caveat:
  same-event pseudo-data may under-scatter. The ratio N1/N5 is reported as the same-event factor.
- The differences assume the added sources are independent of the base ones, so variances add. That is the blocks'
  own additive model, and it is disclosed.
- **When ST1 fires,** P2 and PV wait. The block is named by the row that fires. A fix goes to the director as an
  amendment, and that is outcome A's path (§7). R2 and R3 readings are recorded and do not trigger ST1.
- **Without N5** (if Joseph does not supersede KI 85's deferral, §9), S1's data stream has no construction-error reading,
  and outcome A cannot name it.

**ST2, no admissible candidate.** If at P2 neither K_B nor K_C meets §5.4, PV does not run. The result is "none" (§7).

**ST3, caps.** Every submission is gated against its phase cap from sacct, as COV2D's gate did.

**ST4, validation is spent once.**
- PV's readout is one invocation of one bound binary at the frozen shas. It writes one JSON of summary statistics:
  every §6 reading, its guard, and the counts. Per-toy residuals and z arrays stay inside the process and are not
  written.
- A second invocation on the same seal is a guard refusal: the binary refuses if its output record, or a lock file
  written at its start, exists.
- §5–§7 cannot be amended after binding. The only exception is an executability fix (a crash or a typo) that changes
  no number, bar, family, seed or choice rule, and it needs the director's ruling.
- **The limit of the rule:** a published PV result may inform a later construction. That construction needs new
  sealed truths, and the GENIE v3_04_00 catalog may not supply a third distinct family (§4.1). That is disclosed.

**ST5, guard refusals are terminal** for their phase: fences, atime, provenance, the A0 controls, the seal and decryption
checks, and C-PSD.

**ST6, the cumulative ceiling,** as in §3.

### 3.4 What a PV toy draws

PV draws the full source list of §3.2, the same as N4 and A1p, at a sealed truth u:
- **The truth deformation.** r_u is u's own bridged ratio, decrypted at PV's connect (§4.2). It is applied per row by
  `s5e_deform.ratio_weight(gen, FINE, w_truth, ratio, 1.0)`, computed once with the CV `w_truth` and its rescale
  constant from `mc_truth_denom`'s rows (COV2D §4.1). The same per-row factor applies to every `mc_signal_reco` row.
  Rows outside the 5D grid and background rows get r = 1.
- **The natures.** The bands, lateral and norm are drawn by `cov2d.draw` and composed on reco and truth alike
  (COV2D §4.2).
- **Sim** is S1's simulation-weight redraws, on a separate stream.
- **The pseudo-data** are Poisson at λ⁺ = max(·, 0), on a count stream separate from the draw stream.
- **The graded truth** is each toy's own clipped composite truth, normalized with the drawn Flux universe's integral
  and completeness ≡ 1 (COV2D §4.2).
- **The estimator seed** is fixed at 42, and C_seed is in every candidate.
- **Count:** 300 toys per sealed truth, seed base 9_800_000 + 10_000·u (u = 0, 1): 600 toys at 0.19 node-h is 114.

**One difference from COV2D is disclosed:** PV adds sim, so PV is comparable with COV2D's G18 and AR23 toys up to sim's
share, which N2 measures.

## 4. The validation truths

### 4.1 Which, and how many

- **Two never-read GENIE v3 tunes,** each with a CCQE or 2p2h model that the spent tunes do not use:
  1. `G21_11b_00_000`;
  2. `G18_02b_02_11b`, or `G18_02a_02_11b` only if 02b is absent. They are the same CMC, differing in FSI.
- **Both are required.** If either family is absent from the genie_xsec `v3_04_00` product on Perlmutter, PG stops and
  goes to the director. No FSI twin of a spent tune may replace it.
- **What the names mean,** from GENIE's "Global Fits and Physics Tunes" page (https://genie-mc.github.io/tunes.html,
  read 2026-11-22; it covers v3.0.0–v3.2.0):
  - In the CMC token (`11b`, `02b`), the letter selects the intranuclear transport: a = INTRANUKE/hA,
    b = INTRANUKE/hN, c = Liège/INCL, d = Geant4 Bertini. The trailing `_02_11b` is GENIE's "final 2020 free-nucleon
    x-section retune".
  - G21_11* "uses the SuSAv2 QE and 2p2h model". **Overlap, disclosed:** spent AR23_20i_00_000's 2p2h is
    `SuSAv2MECPXSec` (FD-F1-REPORT.md §1.3), so G21_11b shares AR23's 2p2h. Its CCQE (SuSAv2) differs from both spent
    tunes' `NievesQELCCPXSec`.
  - G18_02* is "similar to G18_01* CMCs, but upgrade[s] the resonance and coherent pion production models (RS → BS)",
    and G18_01* are "adiabatic evolutions of the historic model". The page does not name G18_02's QE or 2p2h models.
- **PG's stat-only probe,** before any generation:
  - it lists the product's tune qualifiers;
  - it prints, for each chosen tune, the CCQE and 2p2h model class names from GENIE's own tune configuration (public
    configuration, not generated content);
  - it confirms an encryption tool (§4.2).
- **The exclusion rule,** applied to the probe's output: a chosen tune that uses **both** the CCQE and the 2p2h class of
  one spent tune is excluded, and PG stops. Partial overlaps are recorded and disclosed in §4.3.
- FD-F1-DECLARATION.md:76 is cited only for the product, path and qualifier convention. It names the spent tunes' two
  qualifiers, not these.

### 4.2 Custody

**Who generates.** A session that is not cov2d and has read none of COV2D, T2A, G2R, REGRADE or this declaration's
§5–§7: a fresh session Joseph opens, which the director names at binding. **Binding requires it.** That session runs
F1's bound pipeline (`gen5d_v3.py`, `run_gevgen_v3.sh`, the pv-ladder ratios and the bridge), unchanged except for the
tune names and the pre-committed seeds: tune u's task seed = 8_310_000 + 10_000·u + task index.

**What it sees.** Its connect captures every stdout, stderr, log and meta file into the sealed set. The session sees
only a final summary of booleans (each step's pass/fail) and file counts. Physics outputs, such as f_MEC, process
fractions, CC counts and the ratio normalization k, are in the sealed meta only.

**Seal and encryption.**
1. The plaintext sha256 of every product is computed with O_NOATIME reads.
2. Each product is encrypted with `gpg --symmetric --cipher-algo AES256`, or `openssl enc -aes-256-cbc -pbkdf2` if the
   probe finds no gpg, under a passphrase the director generates and holds. It is never written to the repo or to any
   cov2d environment before PV's connect.
3. A decrypt-and-hash round trip must reproduce each plaintext sha256.
4. The plaintext is then deleted.
5. `PG-SEAL.sha256` (plaintext and ciphertext sha256 per product) is committed **before P1's first connect**.

**Copies.** The ciphertext sits on pscratch and, **required**, on HPSS (htar from a login node, then hashverify). The
ratio files are not committed to the repo until PV's readout is. A missing or altered ciphertext stops the study. There
is no regeneration.

**At PV.** The director supplies the passphrase to the bound PV connect through a file created at connect start and
deleted at its end. Decryption goes to /dev/shm only, and every decrypted sha256 must equal the seal.

**Limits, disclosed.**
- All sessions share one Unix account.
- Before PV, the barrier against cov2d is the director's key, not file permissions. Atime does not detect O_NOATIME
  reads; atime is recorded on the ciphertext copies only as housekeeping.
- The generating session saw the plaintext and is retired after PG.

### 4.3 What the validation family can and cannot show

Both truths are GENIE v3 configurations. G21_11b shares AR23's 2p2h class, and G18_02's models will be named by the
probe. A pass licenses the covariance for this family (outcome B's "stated model class"), with those overlaps stated
beside it. It does not license any generator. A non-GENIE validation truth would need a sample this project does not
have; that is disclosed, not tested.

## 5. Candidate constructions, built from P0 and P1, frozen at P2

**The build data** are N1–N5, A1f, A1p, and COV2D's G18 and AR23 toys. **The selection data**, which are what any P2 bar,
choice or k reads, are N4 and A1p only. G18 and AR23 never enter a bar or a choice; their readings under each candidate
are printed descriptively. Nothing in PG's seal is read.

### 5.1 K0, the control, and K_A

- **K0** is the current Q_R, unchanged. Its expected PV reading is "under". **If K0 reads "covers" at both sealed truths,**
  the validation family did not test the covariance, and PV is inconclusive (§7).
- **K_A** is Q_R with an ST1 fix applied. **If ST1 does not fire, K_A = K0, and K_A is not read separately.** Outcome A
  is then unavailable.

### 5.2 K_B: the fluctuation part and the bias part, separated

**Fluctuation part.** F_A = K_A − C_model, which is PSD by P0's check.
- For each band R ∈ {R1, R2, R3} of F_A's eigenbasis (carried to each ensemble's truth), the pooled spread ratio is
  f̂_R = mean over E ∈ {N4, A1p(genie_mec), A1p(nuwro), A1p(gibuu)} of F_R(E), with equal weights per ensemble.
- Each F_R(E) is that ensemble's band mean of v_i: spread only, unbiased by construction, with the 1/N divisor.
- **The factor is applied only past a guard:** F_A's eigenvalues in band R are multiplied by f̂_R only if f̂_R − 1 >
  3·SE(f̂_R). They are never lowered. The result is V_F.
- **Why this is not the rejected scaling:**
  - f̂_R is measured on fluctuation ensembles at nominal and at three non-spent truths;
  - it is not chosen to make G18 or AR23 pass, and they do not enter it;
  - it is one factor per band, not a free uniform scale.
  This is disclosed beside any result.

**Bias part.** F_bias = {genie_mec, nuwro, gibuu (A1p means), G18, AR23 (COV2D means)}:

C_b = [ (1/|F_bias|) Σ_t (b̂_t b̂_tᵀ − S_t/(N_t − 1)) ]₊

- [·]₊ is the positive part: the eigen-decomposition with negative eigenvalues set to 0. Its rank is at most 5.
- G18 and AR23 enter C_b as building data, which the review allows. They select nothing.

**K_B = V_F + C_b.** It must pass C-PSD and print its cut diagnostic against K_A's:
- the kept-set difference;
- the kept modes outside K_A's kept span, and their maximum residual;
- the smallest kept and the largest dropped eigenvalue.

If ndf changes from K_A's, that is printed. It is not a stop, because C_b can only add.

### 5.3 K_C: reduced reporting (outcome C)

- **The subspace P_k:**
  - the measurability study's well-constrained directions, if its result is committed before P2's freeze, with k from
    that study's own rule;
  - otherwise K_B's top-k eigen-directions.
- **The choice of k** (top-k case) is the largest k ≥ 10 such that §5.4's bars hold, projected onto P_k, at N4 and at
  each A1p truth. In the measurability case, the same bars must hold at the study's k, or K_C is not admissible.
- **The floor k ≥ 10** keeps h(M) ≤ 0.06 at N = 300 (SE = √(2/(300·10)) ≈ 0.026). The bands of P_k are its own ranks
  1–k, with R1 = 1…min(k, 73); R2 and R3 are used only if they hold at least 10 modes.
- **What K_C reports:** K_B restricted to P_k, plus the combinations' definitions. No uncertainty is reported outside
  P_k.

### 5.4 Admission bars (P2, on the selection data only)

A candidate is admissible only if, at N4 and at each A1p truth:
- M reads "covers";
- no band reads "under" or "over";
- the joint rule of §6.1 flags neither "under" nor "over";
- no mode is flagged "under";
- C-PSD passes.

These bars are in-sample, so they admit a candidate; they never pass one. The readings at G18 and AR23 are printed and
decide nothing.

### 5.5 Freeze

At P2's end, the code and arrays defining K0, K_A (if any), K_B and K_C, with the draw-matched nulls of §6.1 computed
for each candidate at each sealed truth's draw list, are committed with sha256 in `P2-FREEZE.sha256`. They are bound by
the director before PV's first connect.

The draw-matched null needs only the draw list and V, not the truth, so it is computed blind. Its false-FAIL rate (§6.4)
is reported before PV.

## 6. Readings and bars, fixed now

### 6.1 Per ensemble and per truth, against a covariance V

- **M and F,** with guard and labels (§2), and the cut diagnostic of §5.2.
- **Band readings** Q_R, F_R and B_R, with guard and labels, for the bands that hold at least 10 modes.
- **Joint coverage, draw-matched.**
  - The region and the thresholds come from COV2D's phase-N null procedure (`cov2d_readout.py` phase N, addendum A4),
    run with V and the ensemble's own frozen draw list. That gives the null's in-region probability q and the
    thresholds k_J and k_J⁺: the largest k with P(Bin(N, q) ≤ k) < 0.025, and the smallest with
    P(Bin(N, q) ≥ k) < 0.025.
  - Under-coverage is flagged at a count ≤ k_J, over-coverage at a count ≥ k_J⁺.
  - For P1's N-cells, whose draws are fluctuation only, the Gaussian 0.6827 null is used and labelled as such.
- **Per-mode coverage:** the count #{s : |z_{s,i}| ≤ 1}, flagged "under" at ≤ k_c, the largest k with
  P(Bin(N, q_i) ≤ k) < 0.025/ndf (with q_i from the same null), and "over" symmetrically. The flags are reported per band.
- **The split** M = (1/ndf)Σm_i² + F, exact under §2's divisor, is reported with guards. It is descriptive.

### 6.2 PASS at a sealed truth (PV)

A candidate passes at truth u if all of the following hold:
- **P-1:** M reads "covers";
- **P-2:** no band reads "under" or "over";
- **P-3:** the draw-matched joint rule flags neither "under" nor "over";
- **P-4:** no mode is flagged "under".

For K_C, every reading is taken on P_k with ndf = k.

### 6.3 The PV verdict per candidate

| verdict | condition |
|---|---|
| **VALIDATED** | PASS at both sealed truths |
| **FAILS** | P-1 reads "under", P-3 flags "under", a band reads "under", or P-4 flags a mode, at either truth |
| **INFLATED** | no "under" anywhere, and P-1 or a band reads "over", or P-3 flags "over", at either truth |
| **UNRESOLVED** | otherwise |

### 6.4 Multiplicity: false PASS and false FAIL

- **False PASS.** VALIDATED needs every check at both truths. A candidate whose true mean ratio is materially above
  tolerance (M_true > 1.25 + 3·SE, with SE(M) = √(2/(N·ndf)) ≈ 0.006 at ndf 204 and N 300) reads "under" or
  "unresolved" at P-1 with probability near 1 at each truth. The result takes the first VALIDATED of at most three
  candidates (K_A, K_B, K_C), so the familywise chance that such a candidate is VALIDATED is at most the sum of three
  negligible terms. A candidate inside tolerance can pass by design; the tolerance is the stated model class's
  precision.
- **False FAIL for a correctly covering V,** under the draw-matched null.
  - P-3 contributes at most 0.025 for a false "under" and 0.025 for a false "over" (binomial and discrete, so at or
    below nominal).
  - P-4 contributes at most 0.025: the expected number of false under-flags is at most 0.025 by linearity, whatever the
    dependence between modes.
  - P-1 and P-2 are negligible at ndf ≈ 204. At K_C's floor k = 10, losing the guarded "covers" label needs
    M < 0.8 + h or M > 1.25 − h, with h ≈ 0.051: about 5.7σ on the high side and 7.7σ on the low side.
  - So per truth, P(not PASS) ≤ about 0.075 and P(FAILS) ≤ about 0.05. **By the union bound over two truths** (no
    independence assumed), P(not VALIDATED) ≤ 0.15 and P(FAILS) ≤ 0.10. Both are below the 20 % mark in the director's
    request of 2026-11-22.
- **Real toys are not Gaussian.** These bounds hold under the draw-matched null's law. P2's freeze computes the false-FAIL
  rate under that null for each candidate at each sealed truth's draw list, before PV (§5.5). If it exceeds 0.20, the
  candidate does not go to PV, and that is recorded.

## 7. What each outcome licenses (adoption and wording remain Joseph's and the director's)

The candidates are read in the fixed order K_A (only if ST1 fired), K_B, K_C. The first VALIDATED is the result. The
others are reported descriptively, with the multiplicity of §6.4.

**In-sample disclosure.** K_B's bias part uses G18 and AR23 as building data, and its fluctuation factors use N4 and A1p.
Every licensed B or C sentence says so: "built in-sample on <F_bias> and <the P1 ensembles>; validated out of sample on
<the two sealed tunes>, with <the overlaps of §4.3>".

<!-- absence-ok: outcome licensing table for a future result -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | ST1 fired, the fix was amended in, and K_A is VALIDATED | "The 2D covariance had a construction error in <block>, located at nominal truth by <row of ST1>; corrected, it covers two held-out GENIE v3 tunes at the stated level." | a claim about non-GENIE truths; coverage at the data |
| **A, partial** | ST1 fired and was fixed, but K_A is not VALIDATED | "A construction error in <block> was found and corrected; the corrected covariance still does not cover held-out tunes." Then B and C are read. | "fixed" in the coverage sense |
| **B** | K_B is VALIDATED | "With the fluctuation part measured on nominal and alternative-truth ensembles, and a truth-model bias block built in-sample from <F_bias>, the covariance covers two held-out GENIE v3 tunes out of sample; the bias block is reported separately." The band factors f̂_R are printed with it. | coverage outside the GENIE v3 family; a cause of the bias |
| **C** | K_B is not VALIDATED and K_C is VALIDATED | "Uncertainties are reported for the k combinations P_k, which cover the held-out tunes; finer combinations carry no validated uncertainty." | any statement about directions outside P_k |
| **none** | nothing VALIDATED, or ST2 | Nothing new. The note's "coverage remains unvalidated" stands, with P1's matrix readings as description. | any covariance change |
| **inconclusive** | K0 reads "covers" at both sealed truths | Nothing. The validation family did not test the covariance. | — |

<!-- absence-ok: reading rule for a future verdict -->
**A FAILS from P-3 or P-4 alone,** with P-1 "covers" at both truths, is reported as "FAILS (P-3/P-4 only, at <u>)", with
§6.4's false-FAIL bound beside it. The candidate is not VALIDATED, and ST4 forbids a re-read.

<!-- absence-ok: reading rule for a future verdict -->
**INFLATED** is reported as such: "the candidate covers but is wider than the held-out scatter by <M, bands>". It is
not VALIDATED.

**UNRESOLVED** means more toys could resolve it. That needs an amendment and a price, never a re-read of the same toys
with a changed rule.

## 8. Code, tests and audit before any compute

- **Reused unchanged where possible:** re2_driver.py `--data-file`, cov2d_writer, `cov2d.draw` (with r ≡ 1 for N4),
  S1's three-stream bootstrap code (for sim), F1's pipeline (PG), the REGRADE carry, and COV2D's phase-N null.
- **New code:**
  - the N-cell and A1 toy writers, with a fixed-response mode and the 2D-map truth deformation;
  - the N3 seed arm;
  - the N5 half split and its half-B bootstrap;
  - the §3.3 ST1 readings;
  - the §5 builders;
  - the §6 readout, single-invocation and summary-only;
  - PG's probe, capture wrapper, encryption and seal checker;
  - the ST6 cumulative gate.
- **Each needs** unit tests, a line trace of every new line, hand mutants (all killed), a Grok and an agy read, the
  director's binding, and per-connect fences.
- **A0-type controls in every readout:**
  - the readout reproduces COV2D's committed mean χ² at G18 and AR23 from E_<T>.npz, to the κ-scaled tolerance
    max(1e-9, 10 κ₂ ε) (REGRADE-AMENDMENT-1, which adopts T2-BINDING-1 addendum 1's form);
  - numpy against scipy `evr` mode agreement, as in T2A.

## 9. Open items, for the director, and for Joseph where marked

1. **Joseph: KI 85's deferral.** KI 85 defers the held-out-MC re-test until after the publication package and says it is
   not pre-registered. N5 is that re-test. Binding N5 needs Joseph's decision superseding the deferral. Without it, N5
   is dropped (saving 76 / 57 node-h), and S1's data stream has no construction-error reading (§3.3).
2. **Joseph: full or lean** (about 406 or about 325 node-h). The full total is above half the balance.
3. **Binding prerequisites:**
   - a committed iris receipt for the balance;
   - the fresh PG session named;
   - the director's encryption passphrase generated, and never shown to cov2d.
4. **The bars:** 0.8 / 1.25 with the guard, symmetric band and joint rules, and no under-flagged mode. These are
   proposals for the reads to challenge.
5. **Truth-dependent spread.** If A1p's band ratios differ strongly between truths, pooling makes K_B over-cover at
   some truths and under-cover at others. §5.4 will then refuse K_B, and outcome C or none follows. That is the
   intended behaviour, stated here so it is not mistaken for a defect.
