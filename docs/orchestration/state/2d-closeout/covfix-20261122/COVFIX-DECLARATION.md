# COVFIX declaration, DRAFT rev 4.1: the 2D covariance fix (2026-11-22)
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
- **Rev 4** answers their NO-GO reads of rev 3 (`reads/*-rev3-REPORT.md`):
  - **The residual stop** (Grok N3-1, agy Defect 1):
    - the cut is referenced to each candidate's own λ₁(V_F);
    - the residual rule checks only well-determined modes (λ ≥ 1e-6·λ₁);
    - an ndf change is printed, not a stop;
    - the rule does not apply to K_C;
    - P0 calibrates it on the committed C_T vs C_T + C_run pair.
    §2, §3.1, §5.2.
  - **C_b's frame** (N3-2b). Each bias is mapped to x_R by D_t⁻¹ before the sum. §5.2.
  - **Outcome B** (N3-3):
    - G18 and AR23 are out of C_b, which now sums nominal and the three C_model vertices;
    - rows A, B and C say "matches (two-sided)" for the fluctuation block and "does not under-cover (one-sided)" for the
      total;
    - B carries the held-out bias statistics.
    §5.2, §7.
  - **KI 85** (N3-4b). Without both sentences superseded, no block is regenerated and outcome A is not licensed. §3.3.
  - **The null** (N3-2). It is written out: carried G2R band shifts plus a Gaussian remainder, with controls and a
    labelled Gaussian fallback. §6.1.
  - **The ST1 exception** (N3-4, agy Defects 2 and 4):
    - it changes code only;
    - it is bound before the f̂_R and C_b ensembles are drawn, and those are redrawn under it;
    - the regeneration is priced;
    - it can name more than one block.
    §3.3.
  - **Custody** (N3-5):
    - the writer and the readout run on exclusive compute nodes, through `srun` stdin pipes;
    - the scan is by content, and covers /dev/shm, /tmp and the campaign directory;
    - the readout gets its own pipe;
    - the lock file's limit is stated.
    §3.4.
  - **x̂_t** (N3-6). It is defined as the unfold of round(λ⁺). P0 carries with both vectors. §2, §3.1.
  - **§6.4's false-PASS boundary** (N3-7). Corrected. §6.4.
  - **The band factor's basis** (N3-8). Stated. §5.2.
  - **Minor:**
    - K_C's floor is k ≥ 25, for 5σ at N = 100 (N3-9);
    - the G18_02 wording (N3-10);
    - `--time` at 1.5× the price, with chunked submission (N3-11);
    - the price sentences and the no-N5 totals (N3-12);
    - the C_PL τ_F clause (N3-13);
    - a fixed bootstrap basis, and the glosses as v3.2.0 descriptions (N3-14);
    - agy Defects 3 and 5.
- **Rev 4.1** answers agy's read of rev 4 (`reads/agy-rev4-REPORT.md`). Grok could not read rev 4: its usage balance was
  exhausted (HTTP 402, `reads/grok-rev4-ERROR.txt`). agy closed every rev 3 BLOCKING and MAJOR finding and raised five:
  - §8 now names the exclusive-node writer (Defect 1);
  - §6.4 separates the far and near false-PASS boundaries and states the near one's 0.07 (Defect 2);
  - the per-mode binomial parameter is renamed p_i (Defect 3);
  - row "A, partial" carries the KI 85 condition (Defect 4);
  - P-3's count K_J is written (Defect 5).

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
3. **G18 and AR23 are spent.** COVFIX uses them only to calibrate (P0) and to describe. They enter no candidate block,
   no bar and no choice.
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

- x̂_t is the central unfold, with E_R's argv, of t's expected pseudo-data rounded to integers: round(λ⁺) on every
  signal and background row, with λ⁺ as in §3.4 and round-half-to-even. The data tree holds integer counts only, so a
  fractional Asimov file is not constructible. This costs one unfold per truth.
- The formula has the shape REGRADE §2 used for C_run and COV2D §4.4 used for C08. Its reference vector is §2's x̂_t,
  not REGRADE's x_T or COV2D's realization-based x̂_T.
- **The carry is not COV2D's remake.** COV2D remade the blocks at each tune with 486 unfolds per truth. COVFIX tests the
  reported covariance carried in relative form, which is the object a user applies. P0 measures the difference at
  G18 and AR23 (§3.1).

**Every candidate** is V = V_F + V_b, a fluctuation block plus a bias block, carried by the formula above.

**Notation.**
- **Truth and toys.** For a truth t and a toy s = 1…N, the error is e_s = σ̂_s − σ_t on the 205 reported cells.
- **One divisor.** b̂_t = (1/N) Σ_s e_s, and S_t = (1/N) Σ_s (e_s − b̂_t)(e_s − b̂_t)ᵀ.
- **The eigenbasis and the cut.** V(t) = Σ λ_i u_i u_iᵀ, with rank 1 the largest. For every candidate, total or
  fluctuation, the kept modes are those with λ_i > 1e-12·λ₁(V_F(t)), referenced to the candidate's own fluctuation block.
  A large bias block therefore cannot shift the truncation of the fluctuation modes. The number kept is ndf. Every
  bootstrap holds the eigenbasis fixed at the full-sample matrix.
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

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
| phase | what | price, full (node-h) | price, lean | cap, full / lean |
|---|---|---|---|---|
| **P0** | re-analysis of committed records (§3.1) | 0 (local) | 0 | 0 |
| **PG** | generate, encrypt and seal two validation truths (§4) | 1.33–2.0 | 1.33–2.0 | 3.0 |
| **P1 W1** | N1, N2, N5, N3, plus the nominal central unfold and the §2-vector unfolds at G18 and AR23 (§3.2) | 162.07 | 124.07 | — |
| **P1 W2** | N4, A1f, A1p, plus three A1 central unfolds, after ST1 is read on W1 | 129.77 | 86.07 | — |
| **P1** | total | 291.84 | 210.14 | 330 / 240 |
| **P2** | build and freeze the candidates (§5) | 0 (local) | 0 | 0 |
| **PV** | 600 validation toys, 2 central unfolds, and the exclusive-node writer and readout (about 1.0, an unmeasured estimate) (§3.4, §6) | 115.38 | 115.38 | 135 |

- **Totals:** full 408.55–409.22; lean 326.85–327.52.
  - The ranges come from PG's range only. The printed range starts at 1.33, above F1's measured 1.3275 node-h for two
    tunes.
  - Without N5 (§9.1): full 332.55–333.22; lean 269.85–270.52.
- **Every cell is priced at n × 0.19** node-h per unfold, with no rounding. That is the director's planning figure:
  COV2D's 112.74 node-h over 600 toys is 0.188, including pilots and retries.
- **Lean** sets N1, N2 and N4 to 150 toys each and N5 to 150 + 150, and drops A1f. Cell 4 then rests on IBUKT A2's
  committed 5-draw means at genie_mec and nuwro only. **gibuu has no fixed-response ensemble in the lean campaign.**
- **The balance.** The director's message of 2026-11-22 gives 725.6 node-h, from the iris row read at limitation-
  resolver's S1 survey (login23, 2026-11-22T22:01:53Z). That row is not committed. **Binding requires a committed iris
  receipt.** Half of 725.6 is 362.8.
- **Against half the balance:**
  - every phase price and every phase cap is below 362.8;
  - the caps' sums (full 468, lean 378) are not, and neither is the full total with N5;
  - the lean total, and either total without N5, is below it;
  - Joseph chooses full or lean before any compute, and ST6 keeps the campaign inside his approved total.
- **ST6, the cumulative ceiling** (§3.3).
  - Joseph's approved total is pinned in every connect.
  - Each submission's charge ceiling is its nodes × its `--time`. Each toy job's `--time` is 1.5 × its priced per-toy
    time (0.19 node-h is a mean), so a slow job is not killed, and a stalled one cannot charge more than its ceiling.
  - A phase is submitted in chunks small enough that ended charges plus unended ceilings stay within its cap (ST3).
  - Before submitting, each connect sums sacct's charges over the job-name prefix `covfix_`, plus the ceilings of jobs
    not yet ended, plus the new submission's ceiling. It refuses if that sum exceeds the approved total.

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

- **Controls:** Q_rep's two block identities, its sha256, C_model's sha256, and C-PSD on every block:
  λ_min ≥ −1e-12·λ_max. **A failure stops at P0.**
- **The carry check.** At G18 and AR23, K0 carried by §2's formula is compared with COV2D's remade C_T.
  - The carry is done twice: with COV2D's committed realization-based x̂_T from `blocks_<T>.npz`, and with §2's round(λ⁺)
    vector, whose two unfolds run in W1. The P0 readings that need the second vector are completed after W1.
  - The readings are COV2D's committed errors `E_<T>.npz` under each, the eigenvalue ratio per band, and the principal
    angles between the kept spans.
  - This is descriptive. It states the size of the carry approximation and of the difference between the two vectors.
- **The residual rule's calibration.** §5.2's residual rule is applied to the committed regrade case, C_T against
  C_T + C_run(T) at G18 and AR23 (REGRADE run2d and run2d-g18). If the rule fires there, P0 stops and goes to the
  director: a rule that rejects that pair would reject K_B for no reason.
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
| **central unfolds** | nominal; the three vertices; G18 and AR23 | round(λ⁺) pseudo-data (§2), one unfold each, for D_t | 1 + 3 + 2 | — | 1.14 / 1.14 |
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
| `stat`'s data-stream part, through the bootstrap method that builds it | N5: v_i against u_iᵀ S1_B u_i (S1_B from N5's own replicas) | "under" or "over" |
| `stat`, all three streams | N2: v_i against u_iᵀ stat u_i | "under" only. Same-event pseudo-data under-scatter (KI 85), so an N2 "over" is recorded and does not fire. |
| `c08` | N3: v_i against u_iᵀ c08 u_i | "under" or "over" |
| `universe` (universe, lateral and normalization; `s5_total` = `universe` + `stat` + `c08`) | (ŝ_i^{N4} − ŝ_i^{N2}) / u_iᵀ universe u_i, with ŝ_i = λ_i v_i | "under" or "over" |

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
- N1 is never a construction-error reading. Its spread is recorded, and N1/N5 is reported as the same-event factor.
- The N4 − N2 difference assumes the added sources are independent of the base ones, so variances add. That is the
  blocks' own additive model, and it is disclosed.
- **When ST1 fires,** P2 and PV wait, and the firing rows name the blocks.
- **ST1's named exception, the only post-binding amendment to §5–§7.**
  - It may change only the code that generates the block or blocks that fired, never a substituted matrix, and it names
    the bug it corrects.
  - It may not change any bar, seed, the validation family, the §5.2 factor rule, C_b's rule, the k rule, or the order
    in §7.
  - It is bound before any ensemble that enters f̂_R or C_b is drawn: if W1 fires, before W2; if N4 fires, N4 and A1p
    are redrawn under the amended code.
  - It prices the regeneration at 0.19 node-h per unfold (`universe` 175 unfolds, `stat` 300 replicas, `c08` 80) and
    the redraw of the affected cells. That price must fit Joseph's approved total under ST6, or it goes to Joseph.
  - K_A is Q_rep with those blocks regenerated, plus C_model_abs.
- **KI 85 governs whether any block may be regenerated.** Unless Joseph supersedes **both** of KI 85's sentences (§9.1),
  ST1 records every row it can read and regenerates nothing, and §7 does not license outcome A. Without that decision
  N5 is not run either, so the data-stream row is not read.

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
1. **The writer** runs on an exclusive compute node, not a shared login node. The bound PV connect takes an exclusive
   allocation (`salloc --exclusive -N 1`), and the director's wrapper pipes the passphrase into
   `srun --exclusive -N 1 <writer>` (srun forwards stdin to the task). The decrypted r_u lives only in that node's private
   /dev/shm.
2. In that one process the writer produces, for all 600 toys, the pseudo-data files (reco-level counts, which the
   compute jobs need) and the graded truths, plus the two round(λ⁺) files for D_u. The graded truths are encrypted under
   the same passphrase before they touch disk.
3. Before exiting, it wipes /dev/shm and /tmp on that node and scans them and the campaign directory **by content**:
   every file's sha256 is compared against the sealed plaintext hashes, and every file is checked for an unencrypted
   graded-truth array. A hit stops the study.
4. The compute jobs unfold the pseudo-data only.
5. **The readout** is its own bound connect, on its own exclusive node. It receives a fresh pipe from the director's
   wrapper and decrypts the graded truths in-process.

**After the freeze, custody's job is spent-once.** The unfolded outputs alone are not graded errors, and nothing they
reveal can change a frozen candidate (ST4).

**A limit, stated.** The account owner can delete the readout's lock file. "Spent once" is therefore the binary's
refusal plus the committed record. It is not an access control.

**One difference from COV2D is disclosed:** PV adds sim, so PV is comparable with COV2D's G18 and AR23 toys up to sim's
share, which N2 measures.

## 4. The validation truths

### 4.1 Which, and how many

- **Two never-read GENIE v3 tunes,** each with a CCQE or 2p2h model that the spent tunes do not use:
  1. `G21_11b_00_000`;
  2. `G18_02b_02_11b`, or `G18_02a_02_11b` only if 02b is absent: the same G18_02 construction, with a different
     intranuclear transport.
- **Both are required.** If either family is absent from the genie_xsec `v3_04_00` product on Perlmutter, PG stops and
  goes to the director. No FSI twin of a spent tune may replace it.
- **What the names mean,** as v3.2.0 descriptions pending PG's probe of v3_04_00, from GENIE's "Global Fits and Physics Tunes" page (https://genie-mc.github.io/tunes.html,
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

**The build data** are N1–N5, A1f and A1p. COV2D's G18 and AR23 toys are descriptive only. **The selection data**, which any P2 bar,
choice or k reads, are N4 and A1p only. G18 and AR23 never enter a bar or a choice; their readings under each candidate
are printed descriptively. Nothing in PG's seal is read.

### 5.1 K0, the control, and K_A

- **K0** = Q_rep + C_model_abs(x_R), carried (§2): fluctuation block Q_rep, model block C_model_abs. Its expected PV
  reading is "under". **If K0 passes at both sealed truths (§6.2),** the validation family did not test the covariance,
  and PV is inconclusive (§7).
- **K_A** is Q_rep with ST1's firing block regenerated (ST1's named exception), plus C_model_abs. **If ST1 does not fire,
  K_A = K0, and K_A is not read separately.** Outcome A is then unavailable.

### 5.2 K_B: the fluctuation block and the bias block

**Fluctuation block.** F_A is K_A's fluctuation block: Q_rep, or Q_rep with ST1's blocks regenerated. It is absolute at
x_R.

- **Measured.** For each ensemble E with truth t_E, F_A is carried to t_E (§2) and diagonalized there. F_R(E) is E's
  band mean of v_i in that carried basis, for the rank bands R1, R2 and R3.
- **The pooled spread ratio:**

  f̂_R = (1/4) Σ_{E ∈ {N4, A1p(genie_mec), A1p(nuwro), A1p(gibuu)}} (N_E/(N_E − 1)) · F_R(E)

  The factor N/(N − 1) removes the 1/N divisor's bias, so each term is unbiased for the band's mean variance ratio.
- **SE(f̂_R)** is the standard deviation of f̂_R over 2,000 joint bootstrap replicates, each resampling every ensemble
  inside itself at seed 9_991_000, with every eigenbasis held fixed at its full-sample matrix. No independence between
  modes is assumed. Ensemble independence holds by construction, since the seeds are disjoint.
- **Applied.** F_A is diagonalized at x_R. Its eigenvalues in ranks 1–73, 74–139 and ≥ 140 are multiplied by the
  corresponding f̂_R, but only where f̂_R − 1 > 3·SE(f̂_R); they are never lowered. The result is V_F at x_R, which is
  then carried. f̂_R is a rank-band summary transferred across bases. It is not a mode-matched estimate, and that is
  disclosed.
- **Why this is not the rejected scaling:**
  - f̂_R is measured on fluctuation ensembles at nominal and at three non-spent truths;
  - G18 and AR23 do not enter it;
  - it is one pre-registered factor per band, never searched until a bar passes.
  This is disclosed beside any result.

**Bias block, in the reference frame.** F_bias = {nominal (N4's mean), genie_mec, nuwro, gibuu (A1p means)}: the
non-spent build truths only. Each member is mapped to x_R before the sum:

β_t = D_t⁻¹ b̂_t, Σ_t = D_t⁻¹ S_t D_t⁻¹, and C_b = [ Σ_{t ∈ F_bias} (β_t β_tᵀ − Σ_t/(N_t − 1)) ]₊

- [·]₊ is the positive part: the eigen-decomposition with negative eigenvalues set to 0. Its rank is at most 4.
- **It is the sum, not the mean,** so no member is diluted. For the undebiased sum, β_tᵀ C_b⁺ β_t ≤ 1 for each member.
- **The carried test uses β.** b̂_tᵀ V(t)⁻¹ b̂_t = β_tᵀ V⁻¹ β_t, with V the matrix at x_R.
- **G18 and AR23 are not in C_b.** Their biases are large; T2A's mean-error parts against C_T are 13.61 and 20.97 per
  ndf. In the sum they would set the bias block's width in exactly the directions a GENIE tune's bias is expected to
  lie, and the one-sided total bar would then pass by their size. Their mapped biases β_G18 and β_AR23 are printed
  against C_b descriptively: β ᵀC_b⁺β, the fraction outside C_b's span, and M under K_B.
- **The price is disclosed:** C_b over-covers truths whose bias is smaller than the family's. That is why the total is
  barred one-sided (§5.4, §6.2).

**K_B = V_F + C_b** at x_R, carried by §2's formula. It must pass C-PSD and print its cut diagnostic against K_A's:
- the kept sets under §2's cut, which is referenced to each candidate's own λ₁(V_F);
- the kept modes of K_A outside K_B's kept span, and their maximum residual;
- the smallest kept and the largest dropped eigenvalue.

**Residual rule (K_B against K_A only):**
- Only K_A's well-determined modes are checked: those with λ_i ≥ 1e-6·λ₁(F_A).
- If any such mode has a component outside K_B's kept span of norm above 0.1, K_B is not admissible.
- An ndf difference alone is printed, not a stop; tail modes below 1e-6·λ₁(F_A) are printed, not stopped on.
- P0 calibrates this rule on the committed regrade pair (§3.1).
- It does not apply to K_C.

### 5.3 K_C: reduced reporting (outcome C)

- **The subspace P_k:**
  - the measurability study's well-constrained directions, if its result is committed before P2's freeze, with k from
    that study's own rule;
  - otherwise K_B's top-k eigen-directions at x_R.
- **The choice of k** (top-k case) is the largest k ≥ 25 such that §5.4's bars hold, projected onto P_k, at N4 and at
  each A1p truth.
- **The measurability case** must have k ≥ 25 and meet the same bars, or K_C is not admissible.
- **The floor k ≥ 25** keeps the guarded "covers" edges at least 5σ from 1 at the smallest admission ensemble (A1p,
  N = 100): SE = √(2/(100·25)) ≈ 0.028 and h ≈ 0.056, so the low edge 0.8 + h is 5.1σ below 1 and the high edge
  1.25 − h is 6.9σ above. At PV (N = 300), SE ≈ 0.016 and h ≈ 0.032, giving 10.3σ and 13.3σ.
  - These use the χ²-mean SE; the operational guard is the bootstrap SE, which they approximate.
  - The bands of P_k are its own ranks 1–k, with R1 = 1…min(k, 73). R2 and R3 are used only if they hold at least
    10 modes.
- **What K_C reports:** K_B restricted to P_k, plus the combinations' definitions. No uncertainty is reported outside
  P_k.

### 5.4 Admission bars (P2, on the selection data only)

A candidate V = V_F + V_b is admissible only if, at N4 and at each A1p truth:
- **Fluctuation, two-sided:** F^F (spread against V_F, in V_F's carried basis) reads "covers", and no band of it reads
  "under" or "over";
- **Total, one-sided:** M against V reads "not under";
- the joint rule of §6.1 does not flag "under";
- no mode is flagged "under";
- C-PSD passes, and for K_B, §5.2's residual rule.

These bars are in-sample, so they admit a candidate; they never pass one. G18's and AR23's readings under every
candidate are printed and decide nothing.

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
  - C_PL is in V_F and is not drawn, so a correct V_F's expected F^F is the drawn share, slightly below 1.
  - τ_F = tr(V_F⁺ C_PL(t))/ndf_F is printed beside F^F. (REGRADE's analogue was 0.0098.)
- **Total readings,** against V = V_F + V_b: M and its bands, with guard and labels; the split M = (1/ndf)Σm_i² + (1/ndf)Σv_i,
  exact under §2's divisor; and the cut diagnostic of §5.2.
- **The held-out bias comparison:** with β_u = D_u⁻¹ b̂_u, the debiased β_uᵀ C_b⁺ β_u and the fraction of β_u's V_F-norm
  outside C_b's span. It enters §7's B sentence, and decides nothing.
- **The joint region** is χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827) against V(t).
- **The null law,** written here, not cited. For a candidate V at truth t, with the ensemble's frozen draw law:
  - **The band part δ.** The 38 bands' universe shift vectors are taken at the data's point from G2R's `data_g2r.npz`
    (keys `band__<BAND>`; sha256 `3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b`; on pscratch and as
    cov2d's sha-verified laptop copy). They are centred as re2c_rollup centres them, carried by D_t, and composed per
    null replicate exactly as `cov2d.draw` composes them: Flux by constraint weight, 2p2h 1 of 3, the 36 others one
    endpoint each.
  - **The Gaussian part.** g ~ N(0, G(t)), with G(t) = V(t) − C_δ(t), where C_δ(t) is δ's exact covariance under that law.
    G(t) carries lateral, norm, stat, seed, C_PL and the bias block.
  - **Its controls:**
    - P0 rebuilds G2R's `C_univ_new` from the `band__` arrays by re2c_rollup's formulas, to 1e-10 relative. If that
      fails, every joint null is the Gaussian N(0, V(t)) (q = 0.6827), labelled as such.
    - If G(t) fails C-PSD at a given t, that null falls back the same way, labelled as such.
  - **Not modelled:** clipping. That is disclosed.
- **Thresholds.** 20,000 null replicates at seed 9_992_000 give q, the in-region probability, and k_J and k_J⁺: the
  largest k with P(Bin(N, q) ≤ k) < 0.025, and the smallest with P(Bin(N, q) ≥ k) < 0.025.
- **The joint reading** is the count K_J = #{s : χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827)}. It flags "under" if K_J ≤ k_J, and "over"
  if K_J ≥ k_J⁺.
- **Where it runs.**
  - At PV, inside the readout binary, after decryption and before any residual is formed, with every candidate frozen.
    The same replicates also give the false-FAIL rate for §6.2's rule. A candidate whose rate exceeds 0.20 is labelled
    NOT TESTABLE at u before its residuals are formed, and is not VALIDATED.
  - At P1 and P2, for N4 and A1p, at the ensemble's own truth.
  - N1, N2, N3 and N5 draw fluctuation only, so they use the Gaussian N(0, ·) null, labelled as such.
- **Per-mode coverage:** the count #{s : |z_{s,i}| ≤ 1}. It is flagged "under" at ≤ k_c, the largest k with
  P(Bin(N, p_i) ≤ k) < 0.025/ndf, and "over" symmetrically. Here p_i = P_null(|z_{s,i}| ≤ 1), simulated from the same
  null replicates. p_i is not §2's q_i. The flags are reported per band.
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

- **False PASS.** VALIDATED needs every check at both truths.
  - "Not under" fails when M − h > 1.25, so the critical value is 1.25 + h.
  - At ndf 204 and N 300, SE(M) = √(2/(N·ndf)) ≈ 0.0057 and h ≈ 0.011.
  - **Far from the critical value.** A candidate with M_true ≥ 1.25 + h + 3·SE (about 1.279) fails "not under" with
    probability at least Φ(3) ≈ 0.9987 per truth.
    - The two truths' toys are independent draws, so it passes both with probability at most (0.00135)² ≈ 1.8e-6.
    - Over the at most three candidates (K_A, K_B, K_C), the familywise chance is at most about 5.4e-6.
  - **Near the critical value, false PASS is not negligible.** At M_true = 1.25 + 3·SE (1.267), which is about 1·SE above
    the critical value 1.25 + h:
    - "not under" fails with probability about 0.85 per truth, so a pass has probability about 0.15 per truth;
    - it passes both truths with probability about 0.023;
    - the familywise bound over three candidates is about 0.07.
    That is the stated tolerance's precision. A VALIDATED candidate's true total ratio may be up to a few SE above 1.25,
    and every licensed sentence carries M with its guard.
  - A candidate inside tolerance can pass by design; the tolerance is the stated model class's precision.
  - A candidate whose bias block is wide passes the total bar by design. It must still match the fluctuation two-sided
    (P-1), and its bias block is fixed by §5.2's rule, never tuned.
- **False FAIL for a correctly covering V,** under the draw-matched null.
  - P-3 contributes at most 0.025 (binomial, discrete, at or below nominal).
  - P-4 contributes at most 0.025: the expected number of false under-flags is at most 0.025 by linearity, whatever the
    dependence between modes.
  - P-1 and P-2 are negligible at ndf ≈ 204.
    - P-1, the two-sided fluctuation "covers" label, at K_C's floor k = 25 and N = 300: losing it needs a reading above
      1.25 − h or below 0.8 + h, with h ≈ 0.032. That is 13.3σ on the high side and 10.3σ on the low side.
    - P-2, "not under", fails only above 1.25 + h.
  - So per truth, P(not PASS) ≤ about 0.05 and P(FAILS) ≤ about 0.05. **By the union bound over two truths** (no
    independence assumed), P(not VALIDATED) ≤ 0.10 and P(FAILS) ≤ 0.10. Both are below the director's 20 % mark
    (`reads/director-rev0-items.md`, item 5).
- **Real toys are not Gaussian.** These bounds hold under the draw-matched null's law. The PV binary simulates that law's
  false-FAIL rate per candidate and truth before forming residuals (§6.1), and the 0.20 rule applies there.

## 7. What each outcome licenses (adoption and wording remain Joseph's and the director's)

The candidates are read in the fixed order K_A (only if ST1 fired), K_B, K_C. The first VALIDATED is the result. The
others are reported descriptively, with §6.4's multiplicity.

**In-sample disclosure.** K_B's bias block uses nominal and the three C_model vertices, not G18 or AR23. Its fluctuation
factors use N4 and A1p. Every licensed B or C sentence says so: "built in-sample on <F_bias> and <the P1
ensembles>; validated out of sample on <the two sealed tunes>, with <the overlaps of §4.3>; the covariance is the
reported one carried in relative form (§2)".

<!-- absence-ok: outcome licensing table for a future result -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | ST1 fired, KI 85 was superseded (§9.1), its named exception was bound, and K_A is VALIDATED | "The 2D covariance's <block> had a construction error, located at nominal truth by <ST1 row>. Regenerated, its fluctuation block matches the held-out scatter at two GENIE v3 tunes (two-sided), and the total does not under-cover there (one-sided)." | a claim about non-GENIE truths; coverage at the data; that the total is tight |
| **A, partial** | ST1 fired, KI 85 was superseded (§9.1), and its named exception was bound and applied, but K_A is not VALIDATED | "A construction error in <block> was found and corrected; the corrected covariance still does not cover held-out tunes." Then B and C are read. | "fixed" in the coverage sense |
| **B** | K_B is VALIDATED | "The fluctuation block, measured on nominal and alternative-truth ensembles, matches the held-out scatter at two GENIE v3 tunes (two-sided). With a truth-model bias block built in-sample from nominal and the three C_model vertices and reported separately, the total does not under-cover there (one-sided). The held-out biases against that block are β_uᵀC_b⁺β_u = <value>, with <fraction> outside its span." The band factors f̂_R and C_b's rank and trace are printed with it. | "covers" for the total; coverage outside the GENIE v3 family; a cause of the bias; that the bias block is tight |
| **C** | K_B is not VALIDATED and K_C is VALIDATED | "Uncertainties are reported for the k combinations P_k. On them, the fluctuation block matches the held-out scatter (two-sided) and the total does not under-cover (one-sided) at two GENIE v3 tunes. Finer combinations carry no validated uncertainty." | any statement about directions outside P_k; "covers" for the total |
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
  and `cov2d.draw`'s composition law for §6.1's null (whose band part reads G2R's `data_g2r.npz`).
- **New code:**
  - the N-cell and A1 toy writers, with a fixed-response mode and the 2D-map truth deformation;
  - the N3 seed arm;
  - the N5 half split;
  - the §2 carry;
  - the §3.3 ST1 readings;
  - the §5 builders and the residual stop;
  - the §6 readout, single-invocation and summary-only, with the in-binary null and the 0.20 check;
  - PG's probe, capture wrapper, piped encryption, seal checker and plaintext scan;
  - PV's exclusive-compute-node writer (§3.4) with encrypted graded truths;
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
2. **Joseph: full or lean:** about 409.2 or 327.5 node-h at PG's top with N5, or 333.2 or 270.5 without it. Only full
   with N5 is above half the balance.
3. **Binding prerequisites:**
   - a committed iris receipt;
   - the fresh PG session named;
   - the director's passphrase generated, with the director's piping wrapper, and never shown to cov2d.
4. **The bars:** 0.8 / 1.25 with the guard; the fluctuation two-sided and the total one-sided; no under-flagged mode;
   the residual rule at 0.1 on modes with λ ≥ 1e-6·λ₁; K_C's floor k ≥ 25. These are proposals for the reads to
   challenge.
5. **Truth-dependent spread.** If A1p's band ratios differ strongly between truths, pooling makes V_F over-cover at some
   truths and under-cover at others. §5.4's two-sided fluctuation bar will then refuse K_B, and outcome C or none
   follows. That is intended.
6. **The carry.** COVFIX tests the reported covariance carried in relative form, not remade at each truth. P0 measures
   the difference at G18 and AR23. If the director wants the remade object instead, that is 486 unfolds per truth (about
   92 node-h each), and it changes the price.
