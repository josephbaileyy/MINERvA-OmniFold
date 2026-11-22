# COVFIX declaration, DRAFT rev 3: the 2D covariance fix (2026-11-22)
<!-- absence-ok: a draft declaration of studies not yet run; every existing study is routed to INVENTORY.md -->

<!-- absence-ok: status line of an unrun draft -->
**Status: DRAFT.** Not bound. No code is written, nothing is computed, and no cluster connect is made under it.

**By** the `cov2d` session, at the director's request of 2026-11-22 (`reads/director-rev0-items.md` quotes its items on
rev 0). Joseph authorized starting the design phase, via the director, after an outside review of the note asked for
its "Fix 1". The inventory is `INVENTORY.md` in this directory, read at origin/main `7d5a98361`.

**CITABLE FOR:** nothing yet. Once bound and run: the readings in §6 and only the sentences §7 licenses for them.

**NOT CITABLE FOR:**
- any note or paper wording;
- adopting any covariance (adoption is Joseph's);
- a cause of the under-coverage;
- coverage at the data's own point, or for generators outside the validation family (§4.3);
- a p-value.

**Revision history.**
- **Rev 1** answered the director's seven items on rev 0.
- **Rev 2** answered Grok's and agy's NO-GO reads of rev 1 (`reads/*-rev1-REPORT.md`).
- **Rev 3** answers their NO-GO reads of rev 2 (`reads/*-rev2-REPORT.md`):
  - **Grok N-1, the block structure.** K0 is now named by its blocks: Q_rep, the adopted G2R covariance, which equals
    s5_total + C_PL exactly, plus C_model_abs beside it. The carry is an explicit formula, and every candidate is the sum
    of a fluctuation block and a bias block. The carried-versus-remade difference is measured at G18 and AR23 in P0.
    §2, §3.1, §5.1.
  - **Grok N-2, the ST1 amendment.** It is a single named exception, confined to the generator of the firing block and
    written before P2. §3.3.
  - **Grok N-3, agy MINOR-2.** SE(f̂_R) is defined, with the N/(N−1) correction. §5.2.
  - **Grok N-4.** "C_b can only add" is gone, replaced by a residual stop. §5.2.
  - **Grok N-5.** Any band with at least 10 modes can fire ST1. §3.3.
  - **Grok N-6.** The draw-matched null and its 0.20 check run inside the PV binary, after decryption and with the
    candidates frozen. §5.5, §6.1.
  - **Grok N-7.** The false b1 attribution of the guard is removed. §2.
  - **Grok N-8.** The lean campaign's cell 4 covers genie_mec and nuwro only. §3.
  - **Grok N-9, agy MAJOR-1 and MAJOR-3.** The passphrase is piped, never written to a file. Decryption and the toy
    writer run on the login node in /dev/shm, which is wiped. Graded truths are encrypted, and the job ends with a
    plaintext scan. §3.4, §4.2.
  - **agy MAJOR-2, agy MINOR-3.** C_b is the sum, not the mean, of the family's debiased outer products, so it is not
    diluted, and the family includes nominal closure bias. §5.2.
  - **A design consequence both reads point to.** A bias block necessarily over-covers truths whose bias is smaller than
    the family's. The bars are now two-sided on the fluctuation part and one-sided ("not under") on the total. That is
    Fix 1's decomposition: the bias block is a stated model-class bound, and the fluctuation must match. §5.4, §6.2.
  - **Minor:** N-10's σ sides; M-11, which asks that KI 85's no-change rule be superseded explicitly; M-12 (G18_02);
    M-13 (the PG floor and a per-job walltime ceiling); M-14 (the k floor in the measurability case); M-15 (cap sums);
    M-16 (a descriptive held-out bias comparison); M-17 (the 20 % mark, now cited to a committed quote).
  - agy's three BLOCKINGs are binding prerequisites, already listed in §9, not defects of the text.

<!-- absence-ok: rule statement -->
**Rules are fixed before computation.** Every reading, bar, candidate rule, seed and stop rule below is fixed at
binding, before P0. After binding, §5–§7 may not be amended except by ST1's named exception (§3.3). Any other amendment
names every output already seen.

## 1. What the review asked, and what the inventory already settles

The review's Fix 1 separates bias from fluctuation:
E[(σ̂ − σ)(σ̂ − σ)ᵀ] = C_fluct + b bᵀ.

Its acceptable outcomes:
- **(A)** a construction error, found and fixed;
- **(B)** the covariance holds for a stated model class, with the truth-model bias quantified separately;
- **(C)** reported uncertainties for coarser or selected combinations only.

It rejects scaling the covariance until the two tunes pass.

The inventory settles four points:
1. **The fluctuation is under-described, not only the bias** (T2A, against COV2D's remade C_T). At the spent tunes the
   spread per component is 1.6 / 3.0 / 4.4 (AR23) and 1.5 / 3.6 / 4.7 (G18) over ranks 1–73 / 74–139 / ≥ 140. So every
   candidate has a fluctuation part, and P1 measures whether that excess exists at nominal (N4) and at other truths
   (A1p).
2. **C_run's trace is small in 2D:** τ = 0.0098 per ndf at both tunes (REGRADE 2D). The G18 regrade still moved C_T's
   kept subspace (142 kept modes outside the new span), so every candidate prints the cut diagnostic.
3. **G18 and AR23 are spent.** They may build; they may not validate or select.
4. **Never-read truths are cheap.** F1 generated both GENIE v3 tunes for 1.3275 node-h in total.

## 2. The covariances, the carry, and notation

**The reported matrices.**
- **Q_rep** is the adopted 2D covariance, COV2D-G2R's rebuild (DECISION-20261114-joseph-d1-g2r-adopted.md). Its file is
  key `Q` of #1167's run2 `g2r/outA/cov2d_Q_205.npz`, sha256
  `ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295`
  (`fd/receipts-cov2d/g2r/re2shapes/run2/NODE-SHA256.txt:222`). cov2d holds a sha-verified laptop copy.
- **Its blocks:** `Q` = `s5_total` + `C_PL`, and `s5_total` = `universe` + `stat` + `c08`. Both identities were
  measured exact (maximum relative difference 0) on that copy on 2026-11-22. P0 re-checks them as a control.
- **C_model** is RE-2 part C's relative matrix, sha256 `11fe6818…3470` (RE2/RE2-PARTC-REPORT.md:250), reported beside
  Q_rep. Absolute at a central value x: C_model_abs(x) = diag(x) C_model diag(x).

**K0, the matrix under test.** COV2D graded C_T = (remade S5 blocks) + C_model_abs at each tune, without C_PL. COVFIX's
reported-procedure analogue at the data's point is:

K0_R = V_F,0 + V_b,0, with V_F,0 = Q_rep (the fluctuation block) and V_b,0 = C_model_abs(x_R) (the model block).

**The carry to a truth t.** All of COVFIX's blocks are absolute at x_R, and they are carried by one formula:

V(t) = D_t V D_t, with D_t = diag(x̂_t / x_R).

- x̂_t is the central unfold of t's noise-free expected pseudo-data (Asimov), with E_R's argv: one unfold per truth.
- This is the form REGRADE §2 used for C_run and COV2D §4.4 used for C08, applied here to every block.
- **The carry is not COV2D's remake.** COV2D remade the blocks at each tune with 486 unfolds per truth. COVFIX tests the
  reported covariance carried in relative form, which is the object a user applies. P0 measures the difference at
  G18 and AR23 (§3.1).

**Every candidate** is V = V_F + V_b, a fluctuation block plus a bias block, carried by the formula above.

**Notation.**
- **Truth and toys.** For a truth t and a toy s = 1…N, the error is e_s = σ̂_s − σ_t on the 205 reported cells.
- **One divisor.** b̂_t = (1/N) Σ_s e_s, and S_t = (1/N) Σ_s (e_s − b̂_t)(e_s − b̂_t)ᵀ.
- **The eigenbasis.** V(t) = Σ λ_i u_i u_iᵀ, with rank 1 the largest. Modes below 1e-12·λ₁ are dropped, giving ndf.
- **Per mode and toy:** z_{s,i} = u_iᵀ e_s / √λ_i.
- **Per mode:**
  - m_i = mean_s z_{s,i};
  - v_i = (1/N) Σ_s (z_{s,i} − m_i)²;
  - q_i = mean_s z²_{s,i}.
  - Then q_i = m_i² + v_i exactly.
- **The fluctuation readings use V_F's own eigenbasis.** Writing λ_i^F and u_i^F, the per-mode spread is v_i^F, and
  F^F = (1/ndf_F) Σ v_i^F.
- **Bands:** R1 = ranks 1–73, R2 = 74–139, R3 = ≥ 140. A band is used only if it holds at least 10 kept modes;
  otherwise it is dropped and named as dropped. Q_R, F_R and B_R are the band means of q_i, v_i and m_i².
- **The mean ratios:** M = (1/ndf) Σ q_i, the mean χ²/ndf.
- **The guard** (COVFIX's own rule): h(X) = t_{0.975, N−1} · SE(X), with SE from 2,000 toy-bootstrap resamples of that
  ensemble at seed 9_990_000. For a combination of independent ensembles, each is resampled inside itself and the SE is
  that of the combination.
- **Labels** for any ratio X:

  | label | X |
  |---|---|
  | over | < 0.8 |
  | covers | [0.8, 1.25] |
  | under | > 1.25 |

  A label is read only if [X − h, X + h] lies inside one label's interval. Otherwise the reading is "unresolved across
  <labels>". Bands use the same rule and edges.
- **"Not under"** means X − h ≤ 1.25.

## 3. Phases, in order

| phase | what | price, full (node-h) | price, lean | cap, full / lean |
|---|---|---|---|---|
| **P0** | re-analysis of committed records (§3.1) | 0 (local) | 0 | 0 |
| **PG** | generate, encrypt and seal two validation truths (§4) | 1.33–2.0 | 1.33–2.0 | 3.0 |
| **P1 W1** | N1, N2, N5, N3, plus the nominal central unfold (§3.2) | 161.69 | 123.69 | — |
| **P1 W2** | N4, A1f, A1p, plus three A1 central unfolds, after ST1 is read on W1 | 129.77 | 86.07 | — |
| **P1** | total | 291.46 | 209.76 | 330 / 240 |
| **P2** | build and freeze the candidates (§5) | 0 (local) | 0 | 0 |
| **PV** | 600 validation toys plus 2 central unfolds, then the readout (§3.4, §6) | 114.38 | 114.38 | 135 |

- **Totals:** full 407.17–407.84; lean 325.47–326.14. The ranges come from PG's range only, floored at F1's measured
  1.3275 node-h for two tunes.
- **Every cell is priced at n × 0.19** node-h per unfold, with no rounding. That is the director's planning figure:
  COV2D's 112.74 node-h over 600 toys is 0.188, including pilots and retries.
- **Lean** sets N1, N2 and N4 to 150 toys each and N5 to 150 + 150, and drops A1f. Cell 4 then rests on IBUKT A2's
  committed 5-draw means at genie_mec and nuwro only. **gibuu has no fixed-response ensemble in the lean campaign.**
- **The balance.** The director's message of 2026-11-22 gives 725.6 node-h, from the iris row read at limitation-
  resolver's S1 survey (login23, 2026-11-22T22:01:53Z). That row is not committed. **Binding requires a committed iris
  receipt.** Half of 725.6 is 362.8.
- **Against half the balance:**
  - every phase price and every phase cap is below 362.8;
  - the caps' sums (full 468, lean 378) are not, and neither is the full total;
  - the lean total is below it;
  - Joseph chooses full or lean before any compute, and ST6 keeps the campaign inside his approved total.
- **ST6, the cumulative ceiling** (§3.3).
  - Joseph's approved total is pinned in every connect.
  - Each submission's charge ceiling is its nodes × its `--time`, and each toy job's `--time` is set from its priced
    per-toy time. A stalled job therefore cannot charge more than its ceiling.
  - Before submitting, each connect sums sacct's charges over the job-name prefix `covfix_`, plus the ceilings of jobs
    not yet ended, plus the new submission's ceiling. It refuses if that sum exceeds the approved total.

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

- **Controls:** Q_rep's two block identities, its sha256, C_model's sha256, and C-PSD on every block:
  λ_min ≥ −1e-12·λ_max. **A failure stops at P0.**
- **The carry check.** At G18 and AR23, K0 carried by §2's formula (using COV2D's committed x̂_T from `blocks_<T>.npz`)
  is compared with COV2D's remade C_T. The readings are COV2D's committed errors `E_<T>.npz` under each, the
  eigenvalue ratio per band, and the principal angles between the kept spans. This is descriptive, and it states the
  size of the carry approximation.
- The per-mode profiles (m_i, v_i, q_i) of COV2D's committed errors under the carried K0, under C_T, and under G2R's
  C_T′.
- IBUKT A2's mean residuals (`state/2d-closeout/ibukt-a2/readout.json`), times E_R, in K0's modes: m_i only.
- c2 as scoped: T2A's mean error projected on C_PL's two directions.

These validate nothing.

### 3.2 P1: the construction measurements

Each cell is a toy ensemble unfolded by the production procedure (re2_driver.py, E_R's argv). The seeds are
pre-committed and disjoint from every committed ensemble; a test checks them against COV2D's, C08's and S1's seed lists.

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
| **N5** data stream, held-out | nominal, MC half A | pseudo-data from half A, unfolded with half B's response; plus half-B data-stream bootstrap replicas (`--bootstrap-streams data`) for that configuration's own data-stream block S1_B | 200+200 / 150+150 | 9_500_000 (toys), 9_510_000 (replicas), 9_520_000 (split) | 76 / 57 |
| **N3** estimator seed | nominal | one fixed N1 pseudo-dataset (seed 9_300_100); estimator seeds 9_300_000–9_300_049 | 50 / 50 | — | 9.5 / 9.5 |
| **N4** all sources at nominal | nominal | the full source list, with r ≡ 1 | 200 / 150 | 9_400_000 | 38 / 28.5 |
| **A1f** alternative truth, fixed response | genie_mec, nuwro, gibuu (C_model's three PV2D vertices) | N1 only, response nominal, truth deformed by the vertex's 2D map | 3 × 60 / 0 | 9_600_000 + 10_000·j | 34.2 / 0 |
| **A1p** alternative truth, perturbed response | the same three | the full source list at the deformed truth | 3 × 100 / 3 × 100 | 9_700_000 + 10_000·j | 57 / 57 |
| **central unfolds** | nominal; the three vertices | noise-free expected pseudo-data, one unfold each, for D_t | 1 + 3 | — | 0.76 / 0.76 |
| **existing** | G18, AR23 | COV2D's toys (data Poisson + bands + lateral + norm; no sim) | 300 + 300 | committed | 0 |

- j = 0, 1, 2 for genie_mec, nuwro, gibuu.
- **A1f and A1p are in-sample.** Their truths are the shifts that define C_model. A1f measures the estimator's bias
  there (the review's cell 4, in-sample), and A1p the truth-dependent spread. The held-out alternative truths are PV's.
- **C_PL and C_run are not drawn,** because they have no generative law (SCOPING a3). They enter V_F as covariance.

### 3.3 Stop rules

**ST1, construction error.** It is read on W1 (N2, N3, N5) before W2 is submitted, and on W2 for N4.
- Each reading uses the spread only (v_i in the block's own carried eigenbasis at x̂_MC), never q, because nominal
  closure bias (IBUKT A2: up to 1.708 % noise-free) would otherwise enter.
- Nominal bias is reported separately (m_i, B_R).
- Every band with at least 10 modes can fire, under the same guard.

| block under test (keys of Q_rep's file) | reading: band mean of the per-mode ratio, guarded | ST1 fires if any band reads |
|---|---|---|
| the data-stream bootstrap method | N5: v_i against u_iᵀ S1_B u_i (S1_B from N5's own replicas) | "under" or "over" |
| `stat`, all three streams | N2: v_i against u_iᵀ stat u_i | "under" only. Same-event pseudo-data under-scatter (KI 85), so an N2 "over" is recorded and does not fire. |
| `c08` | N3: v_i against u_iᵀ c08 u_i | "under" or "over" |
| `universe` (universe, lateral and normalization; `s5_total` = `universe` + `stat` + `c08`) | (ŝ_i^{N4} − ŝ_i^{N2}) / u_iᵀ universe u_i, with ŝ_i = λ_i v_i | "under" or "over" |

- N1 is never a construction-error reading. Its spread is recorded, and N1/N5 is reported as the same-event factor.
- The N4 − N2 difference assumes the added sources are independent of the base ones, so variances add. That is the
  blocks' own additive model, and it is disclosed.
- **When ST1 fires,** P2 and PV wait, and the firing row names the block.
- **ST1's named exception, the only post-binding amendment to §5–§7.** It may change only the generator of the block
  that fired: the code or inputs that produce that block. It may not change any bar, seed, the validation family, the
  §5.2 factor rule, C_b's rule, the k rule, or the order in §7. It is written and bound before P2's first computation.
  K_A is Q_rep with that block regenerated, plus C_model_abs.
- **Without N5** (if Joseph does not supersede KI 85, §9), the data-stream row is not read.

**ST2, no admissible candidate.** If at P2 neither K_B nor K_C meets §5.4, PV does not run. The result is "none" (§7).

**ST3, caps.** Every submission is gated against its phase cap from sacct, as COV2D's gate did.

**ST4, validation is spent once.**
- PV's readout is one invocation of one bound binary at the frozen shas. It writes one JSON of summary statistics:
  every §6 reading, its guard, and the counts. Per-toy residuals and z arrays stay inside the process.
- A second invocation on the same seal is a guard refusal: the binary refuses if its output record, or a lock file
  written at its start, exists.
- §5–§7 cannot be amended after binding, except by ST1's named exception, or by an executability fix (a crash or a
  typo) that changes no number, bar, family, seed or choice rule, under the director's ruling.
- **The limit of the rule:** a published PV result may inform a later construction. That construction needs new
  sealed truths, and the GENIE v3_04_00 catalog may not supply a third distinct family (§4.1).

**ST5, guard refusals are terminal** for their phase: fences, atime, provenance, the A0 controls, the seal, decryption
and plaintext-scan checks, and C-PSD.

**ST6, the cumulative ceiling,** as in §3.

### 3.4 What a PV toy draws, and where

PV draws the full source list of §3.2, the same as N4 and A1p, at a sealed truth u.

- **The truth deformation.** r_u is u's own bridged ratio, applied per row by
  `s5e_deform.ratio_weight(gen, FINE, w_truth, ratio, 1.0)`, computed once with the CV `w_truth` and its rescale constant
  from `mc_truth_denom`'s rows (COV2D §4.1). The same per-row factor applies to every `mc_signal_reco` row. Rows outside
  the 5D grid and background rows get r = 1.
- **The natures.** The bands, lateral and norm are drawn by `cov2d.draw` and composed on reco and truth alike
  (COV2D §4.2). Sim is S1's simulation-weight redraws, on a separate stream.
- **The pseudo-data** are Poisson at λ⁺ = max(·, 0), on a count stream separate from the draw stream.
- **The graded truth** is each toy's own clipped composite truth, normalized with the drawn Flux universe's integral and
  completeness ≡ 1 (COV2D §4.2).
- **The estimator seed** is fixed at 42, and C_seed is in every candidate.
- **Count:** 300 toys per sealed truth, seed base 9_800_000 + 10_000·u (u = 0, 1), plus one central unfold per truth.

**Where, in order:**
1. The bound PV connect, on a login node, receives the passphrase on a pipe from the director's wrapper (§4.2) and
   decrypts r_u into login-node /dev/shm.
2. In that one process it writes, for all 600 toys, the pseudo-data files (reco-level counts, which the compute jobs
   need) and the graded truths. The graded truths are encrypted under the same passphrase before they touch disk.
3. It computes D_u's Asimov input.
4. It wipes /dev/shm, and scans the campaign directory for plaintext ratios and plaintext graded truths. A hit stops the
   study.
5. The compute jobs unfold the pseudo-data only.
6. The bound readout decrypts the graded truths in-process, from the same pipe.

**After the freeze, custody's job is spent-once.** The unfolded outputs alone are not graded errors, and nothing they
reveal can change a frozen candidate (ST4).

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
  - G18_02* is "similar to G18_01* CMCs, but upgrade[s] the resonance and coherent pion production models (RS → BS)".
    The page says G18_10* adds to it "a consistent theory-based model of interactions around the quasi-elastic peak (NAV
    QE and NSV 2p2h model)", so G18_02 does not carry spent G18_10a's NAV QE and NSV 2p2h. The page does not name
    G18_02's own QE and 2p2h models.
- **PG's stat-only probe,** before any generation:
  - it lists the product's tune qualifiers;
  - it prints, for each chosen tune, the CCQE and 2p2h model class names from GENIE's own tune configuration (public
    configuration, not generated content);
  - it confirms an encryption tool (§4.2).
- **The exclusion rule,** applied to the probe's output: a chosen tune that uses **both** the CCQE and the 2p2h class of
  one spent tune is excluded, and PG stops. Partial overlaps are recorded and disclosed in §4.3.
- FD-F1-DECLARATION.md:76 is cited only for the product, path and qualifier convention.

### 4.2 Custody

**Who generates.** A session that is not cov2d and has read none of COV2D, T2A, G2R, REGRADE or this declaration's
§5–§7: a fresh session Joseph opens, which the director names at binding. **Binding requires it.** That session runs
F1's bound pipeline (`gen5d_v3.py`, `run_gevgen_v3.sh`, the pv-ladder ratios and the bridge), unchanged except for the
tune names and the pre-committed seeds: tune u's task seed = 8_310_000 + 10_000·u + task index.

**What it sees.** Its connect captures every stdout, stderr, log and meta file into the sealed set. The session sees
only a final summary of booleans (each step's pass/fail) and file counts. Physics outputs, such as f_MEC, process
fractions, CC counts and the ratio normalization k, are in the sealed meta only.

**The passphrase** is generated and held by the director. It reaches a connect only on a pipe from the director's
wrapper into the bound binary's stdin. It is never an argument, an environment variable or a file, so it never enters
shell history or the Slurm spool.

**Seal and encryption.**
1. The plaintext sha256 of every product is computed with O_NOATIME reads.
2. Each product is encrypted with `gpg --batch --passphrase-fd 0 --symmetric --cipher-algo AES256`, or
   `openssl enc -aes-256-cbc -pbkdf2 -pass stdin` if the probe finds no gpg.
3. A decrypt-and-hash round trip must reproduce each plaintext sha256.
4. The plaintext is deleted.
5. A plaintext scan of the PG directories and /dev/shm must come back empty.
6. `PG-SEAL.sha256` (plaintext and ciphertext sha256 per product) is committed **before P1's first connect**.

**Copies.** The ciphertext sits on pscratch and, **required**, on HPSS (htar from a login node, then hashverify). The
ratio files are not committed to the repo until PV's readout is. A missing or altered ciphertext stops the study. There
is no regeneration.

**Limits, disclosed.**
- All sessions share one Unix account.
- Before PV, the barrier against cov2d is the director's key, not file permissions. Atime does not detect O_NOATIME
  reads, so it is housekeeping only.
- The generating session saw the plaintext and is retired after PG.

### 4.3 What the validation family can and cannot show

Both truths are GENIE v3 configurations. G21_11b shares AR23's 2p2h class, and G18_02's models will be named by the
probe. A pass licenses the covariance for this family (outcome B's "stated model class"), with those overlaps stated
beside it. It does not license any generator. A non-GENIE validation truth would need a sample this project does not
have; that is disclosed, not tested.

## 5. Candidate constructions, built from P0 and P1, frozen at P2

**The build data** are N1–N5, A1f, A1p, and COV2D's G18 and AR23 toys. **The selection data**, which any P2 bar,
choice or k reads, are N4 and A1p only. G18 and AR23 never enter a bar or a choice; their readings under each candidate
are printed descriptively. Nothing in PG's seal is read.

### 5.1 K0, the control, and K_A

- **K0** = Q_rep + C_model_abs(x_R), carried (§2): fluctuation block Q_rep, model block C_model_abs. Its expected PV
  reading is "under". **If K0 passes at both sealed truths (§6.2),** the validation family did not test the covariance,
  and PV is inconclusive (§7).
- **K_A** is Q_rep with ST1's firing block regenerated (ST1's named exception), plus C_model_abs. **If ST1 does not fire,
  K_A = K0, and K_A is not read separately.** Outcome A is then unavailable.

### 5.2 K_B: the fluctuation block and the bias block

**Fluctuation block.** F_A is K_A's fluctuation block: Q_rep, or Q_rep with ST1's block regenerated.
- For each band R of F_A's carried eigenbasis at each ensemble's truth, the pooled spread ratio is:

  f̂_R = (1/4) Σ_{E ∈ {N4, A1p(genie_mec), A1p(nuwro), A1p(gibuu)}} (N_E/(N_E − 1)) · F_R(E)

  F_R(E) is ensemble E's band mean of v_i against F_A. The factor N/(N − 1) removes the 1/N divisor's bias, so each term
  is unbiased for the band's mean variance ratio.
- **SE(f̂_R)** is the standard deviation of f̂_R over 2,000 joint bootstrap replicates, each resampling every ensemble
  inside itself at seed 9_991_000. No independence between modes is assumed. Ensemble independence is by construction,
  since the seeds are disjoint.
- **The factor is applied only past a guard:** F_A's eigenvalues in band R are multiplied by f̂_R only if
  f̂_R − 1 > 3·SE(f̂_R). They are never lowered. The result is V_F.
- **Why this is not the rejected scaling:**
  - f̂_R is measured on fluctuation ensembles at nominal and at three non-spent truths;
  - G18 and AR23 do not enter it;
  - it is one pre-registered factor per band, never searched until a bar passes.
  This is disclosed beside any result.

**Bias block.** F_bias = {nominal (N4's mean), genie_mec, nuwro, gibuu (A1p means), G18, AR23 (COV2D's means)}:

C_b = [ Σ_{t ∈ F_bias} (b̂_t b̂_tᵀ − S_t/(N_t − 1)) ]₊

- [·]₊ is the positive part: the eigen-decomposition with negative eigenvalues set to 0. Its rank is at most 6.
- **It is the sum, not the mean.** Each member's own bias then contributes at most about 1 to its χ², in total over all
  modes (b̂_tᵀ C_b⁺ b̂_t ≤ 1 for the undebiased sum), so no member's direction is diluted.
- **The price is disclosed:** C_b over-covers truths whose bias is smaller than the family's. That is why the total is
  barred one-sided (§5.4, §6.2).
- G18 and AR23 enter C_b as building data, which the review allows. They select nothing.

**K_B = V_F + C_b,** carried by §2's formula. It must pass C-PSD and print its cut diagnostic against K_A's:
- the kept-set difference;
- the kept modes of K_A outside K_B's kept span, and their maximum residual;
- the smallest kept and the largest dropped eigenvalue.

**Residual stop:** if ndf differs from K_A's, or any kept mode of K_A has a component outside K_B's kept span with norm
above 0.1, K_B is not admissible.

### 5.3 K_C: reduced reporting (outcome C)

- **The subspace P_k:**
  - the measurability study's well-constrained directions, if its result is committed before P2's freeze, with k from
    that study's own rule;
  - otherwise K_B's top-k eigen-directions.
- **The choice of k** (top-k case) is the largest k ≥ 10 such that §5.4's bars hold, projected onto P_k, at N4 and at
  each A1p truth.
- **The measurability case** must have k ≥ 10 and meet the same bars, or K_C is not admissible.
- **The floor k ≥ 10.** For the χ² mean, SE(M) = √(2/(300·10)) ≈ 0.026 and h ≈ 0.051 at N = 300. The operational guard is
  the bootstrap SE, which this analytical value approximates. The bands of P_k are its own ranks 1–k, with
  R1 = 1…min(k, 73); R2 and R3 are used only if they hold at least 10 modes.
- **What K_C reports:** K_B restricted to P_k, plus the combinations' definitions. No uncertainty is reported outside
  P_k.

### 5.4 Admission bars (P2, on the selection data only)

A candidate V = V_F + V_b is admissible only if, at N4 and at each A1p truth:
- **Fluctuation, two-sided:** F^F (spread against V_F, in V_F's basis) reads "covers", and no band of it reads "under"
  or "over";
- **Total, one-sided:** M against V reads "not under";
- the joint rule of §6.1 does not flag "under";
- no mode is flagged "under";
- C-PSD passes, and so does §5.2's residual stop.

These bars are in-sample, so they admit a candidate; they never pass one. G18's and AR23's readings are printed and
decide nothing.

### 5.5 Freeze

At P2's end, the code and arrays defining K0, K_A (if any), K_B and K_C are committed with sha256 in
`P2-FREEZE.sha256`, and bound by the director before PV's first connect.

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
The draw-matched null depends on r_u, so it is not computed at P2. It is computed inside the PV readout binary, after
decryption and before any residual is formed, with every candidate already frozen (§6.1). Its false-FAIL check
therefore cannot change §5.

## 6. Readings and bars, fixed now

### 6.1 Per ensemble and per truth

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
- **Fluctuation readings,** against V_F in V_F's carried basis: F^F and its bands, with guard and labels.
- **Total readings,** against V = V_F + V_b: M and its bands, with guard and labels; the split M = (1/ndf)Σm_i² + (1/ndf)Σv_i,
  exact under §2's divisor; and the cut diagnostic of §5.2.
- **The held-out bias comparison** (descriptive): b̂_uᵀ C_b⁺ b̂_u (debiased), and the fraction of b̂_u's V_F-norm outside
  C_b's span. It decides nothing.
- **Joint coverage, draw-matched,** at PV.
  - Inside the PV readout binary, after decryption and before any residual, COV2D's phase-N null procedure
    (`cov2d_readout.py` phase N, addendum A4) runs with each frozen candidate and u's draw list. That gives the null's
    in-region probability q and the thresholds k_J and k_J⁺: the largest k with P(Bin(N, q) ≤ k) < 0.025, and the
    smallest with P(Bin(N, q) ≥ k) < 0.025.
  - It also simulates that null's false-FAIL rate for §6.2's rule. A candidate whose rate exceeds 0.20 is labelled NOT
    TESTABLE at u before its residuals are formed, and is not VALIDATED.
  - At P1 and P2, whose ensembles draw no sealed truth, the same phase-N procedure runs at the ensemble's own truth.
    N1, N2, N3 and N5 draw fluctuation only, so they use the Gaussian 0.6827 null, labelled as such.
- **Per-mode coverage:** the count #{s : |z_{s,i}| ≤ 1}, flagged "under" at ≤ k_c, the largest k with
  P(Bin(N, q_i) ≤ k) < 0.025/ndf (q_i from the same null), and "over" symmetrically. The flags are reported per band.
- **Joint "over" and per-mode "over"** are reported. They refuse only through the fluctuation reading (§6.2), because
  the bias block over-covers by design.

### 6.2 PASS at a sealed truth (PV)

A candidate passes at truth u if all of the following hold:
- **P-1, fluctuation:** F^F against V_F reads "covers", and no band of it reads "under" or "over";
- **P-2, total:** M against V reads "not under", and no band of the total reads "under";
- **P-3:** the draw-matched joint rule does not flag "under";
- **P-4:** no mode is flagged "under".

For K_C, every reading is taken on P_k with ndf = k.

### 6.3 The PV verdict per candidate

| verdict | condition |
|---|---|
| **VALIDATED** | PASS at both sealed truths |
| **FAILS** | P-2 reads "under" (total or a band), P-3 flags "under", P-4 flags a mode, or P-1 reads "under" (fluctuation or a band), at either truth |
| **INFLATED** | no failure above, and P-1 reads "over" (fluctuation or a band) at either truth |
| **NOT TESTABLE** | the null's false-FAIL rate exceeds 0.20 at either truth (§6.1) |
| **UNRESOLVED** | otherwise |

A total reading "over" with the fluctuation reading "covers" is reported as "conservative through the bias block". It
is not INFLATED.

### 6.4 Multiplicity: false PASS and false FAIL

- **False PASS.** VALIDATED needs every check at both truths. A candidate whose true total mean ratio is materially above
  tolerance (M_true > 1.25 + 3·SE, with SE(M) = √(2/(N·ndf)) ≈ 0.006 at ndf 204 and N 300) fails "not under" with
  probability near 1 at each truth. The result takes the first VALIDATED of at most three candidates (K_A, K_B, K_C), so
  the familywise chance that such a candidate is VALIDATED is at most the sum of three negligible terms.
  - A candidate inside tolerance can pass by design; the tolerance is the stated model class's precision.
  - A candidate whose bias block is wide passes the total bar by design. It must still match the fluctuation two-sided
    (P-1), and its bias block is fixed by §5.2's rule, never tuned.
- **False FAIL for a correctly covering V,** under the draw-matched null.
  - P-3 contributes at most 0.025 (binomial, discrete, at or below nominal).
  - P-4 contributes at most 0.025: the expected number of false under-flags is at most 0.025 by linearity, whatever the
    dependence between modes.
  - P-1 and P-2 are negligible at ndf ≈ 204. At K_C's floor k = 10, losing the guarded "covers" label needs
    M > 1.25 − h or M < 0.8 + h, with h ≈ 0.051: about 7.7σ on the high side and 5.8σ on the low side.
  - So per truth, P(not PASS) ≤ about 0.05 and P(FAILS) ≤ about 0.05. **By the union bound over two truths** (no
    independence assumed), P(not VALIDATED) ≤ 0.10 and P(FAILS) ≤ 0.10. Both are below the director's 20 % mark
    (`reads/director-rev0-items.md`, item 5).
- **Real toys are not Gaussian.** These bounds hold under the draw-matched null's law. The PV binary simulates that law's
  false-FAIL rate per candidate and truth before forming residuals (§6.1), and the 0.20 rule applies there.

## 7. What each outcome licenses (adoption and wording remain Joseph's and the director's)

The candidates are read in the fixed order K_A (only if ST1 fired), K_B, K_C. The first VALIDATED is the result. The
others are reported descriptively, with §6.4's multiplicity.

**In-sample disclosure.** K_B's bias block uses nominal, the three vertices, and G18 and AR23 as building data, and its
fluctuation factors use N4 and A1p. Every licensed B or C sentence says so: "built in-sample on <F_bias> and <the P1
ensembles>; validated out of sample on <the two sealed tunes>, with <the overlaps of §4.3>; the covariance is the
reported one carried in relative form (§2)".

<!-- absence-ok: outcome licensing table for a future result -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | ST1 fired, its named exception was bound, and K_A is VALIDATED | "The 2D covariance's <block> had a construction error, located at nominal truth by <ST1 row>; regenerated, the covariance covers two held-out GENIE v3 tunes at the stated level." | a claim about non-GENIE truths; coverage at the data |
| **A, partial** | ST1 fired and was fixed, but K_A is not VALIDATED | "A construction error in <block> was found and corrected; the corrected covariance still does not cover held-out tunes." Then B and C are read. | "fixed" in the coverage sense |
| **B** | K_B is VALIDATED | "With the fluctuation block measured on nominal and alternative-truth ensembles, and a truth-model bias block built in-sample from <F_bias>, the covariance covers two held-out GENIE v3 tunes out of sample; the bias block is reported separately." The band factors f̂_R and C_b's rank and trace are printed with it. | coverage outside the GENIE v3 family; a cause of the bias; that the bias block is tight |
| **C** | K_B is not VALIDATED and K_C is VALIDATED | "Uncertainties are reported for the k combinations P_k, which cover the held-out tunes; finer combinations carry no validated uncertainty." | any statement about directions outside P_k |
| **none** | nothing VALIDATED, or ST2 | Nothing new. The note's "coverage remains unvalidated" stands, with P1's matrix readings as description. | any covariance change |
| **inconclusive** | K0 passes at both sealed truths | Nothing. The validation family did not test the covariance. | — |

<!-- absence-ok: reading rules for future verdicts -->
**A FAILS from P-3 or P-4 alone,** with P-1 and P-2 passing at both truths, is reported as "FAILS (P-3/P-4 only, at
<u>)", with §6.4's false-FAIL bound beside it. The candidate is not VALIDATED, and ST4 forbids a re-read.

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
**INFLATED** is reported as "the fluctuation block is wider than the held-out scatter by <F^F, bands>". It is not
VALIDATED.

**UNRESOLVED** means more toys could resolve it. That needs an amendment and a price, never a re-read of the same toys
with a changed rule.

## 8. Code, tests and audit before any compute

- **Reused unchanged where possible:** re2_driver.py `--data-file`, cov2d_writer, `cov2d.draw` (with r ≡ 1 for N4),
  S1's three-stream bootstrap code (for sim, and with `--bootstrap-streams data` for N5's replicas), F1's pipeline (PG),
  and COV2D's phase-N null.
- **New code:**
  - the N-cell and A1 toy writers, with a fixed-response mode and the 2D-map truth deformation;
  - the N3 seed arm;
  - the N5 half split;
  - the §2 carry;
  - the §3.3 ST1 readings;
  - the §5 builders and the residual stop;
  - the §6 readout, single-invocation and summary-only, with the in-binary null and the 0.20 check;
  - PG's probe, capture wrapper, piped encryption, seal checker and plaintext scan;
  - PV's login-node writer with encrypted graded truths;
  - the ST6 gate.
- **Each needs** unit tests, a line trace of every new line, hand mutants (all killed), a Grok and an agy read, the
  director's binding, and per-connect fences.
- **A0-type controls in every readout:**
  - the readout reproduces COV2D's committed mean χ² at G18 and AR23 from E_<T>.npz against C_T, to the κ-scaled
    tolerance max(1e-9, 10 κ₂ ε) (REGRADE-AMENDMENT-1, which adopts T2-BINDING-1 addendum 1's form);
  - numpy against scipy `evr` mode agreement, as in T2A.

## 9. Open items, for the director, and for Joseph where marked

1. **Joseph: KI 85.** KI 85 defers the held-out-MC re-test until after the publication package, says it is not
   pre-registered, and says no outcome changes a quoted band or printed number before publication. N5 is that re-test,
   and outcome A would change a covariance. Binding N5 and outcome A needs Joseph's decision superseding **both**
   sentences. Without it, N5 is dropped (saving 76 / 57 node-h), the data-stream ST1 row is not read, and outcome A
   cannot change a quoted band before publication.
2. **Joseph: full or lean** (about 407.8 or 326.1 node-h at PG's top). The full total is above half the balance.
3. **Binding prerequisites:**
   - a committed iris receipt;
   - the fresh PG session named;
   - the director's passphrase generated, with the director's piping wrapper, and never shown to cov2d.
4. **The bars:** 0.8 / 1.25 with the guard; the fluctuation two-sided and the total one-sided; no under-flagged mode;
   residual 0.1. These are proposals for the reads to challenge.
5. **Truth-dependent spread.** If A1p's band ratios differ strongly between truths, pooling makes V_F over-cover at some
   truths and under-cover at others. §5.4's two-sided fluctuation bar will then refuse K_B, and outcome C or none
   follows. That is intended.
6. **The carry.** COVFIX tests the reported covariance carried in relative form, not remade at each truth. P0 measures
   the difference at G18 and AR23. If the director wants the remade object instead, that is 486 unfolds per truth (about
   92 node-h each), and it changes the price.
