# COVFIX declaration, DRAFT rev 8: the 2D covariance fix (2026-11-23)
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
- **Rev 5** answers codex-school2's read of rev 4.1 (`reads/codex2-rev4.1-REPORT.md`; NO-GO). codex-school2 is the
  second reader named in `DECISION-20261123-joseph-covfix-ki85-size-reader.md`, which is now cited in §3, §3.3, §7 and
  §9.
  - **Outcome licences** (its BLOCKINGs on A and B, and MAJORs on C and none):
    - A needs code-level evidence;
    - "A, partial" reports the actual verdict;
    - B and C license only the observed affirmative readings at the two named tunes under the declared toy law, not a
      model class;
    - a baseline challenge (K0 FAILS somewhere) is required for B and C;
    - "inconclusive" becomes "no challenge". §7.
  - **Affirmative bars.**
    - The total is barred by its upper guarded bound, M + h ≤ 1.25.
    - The fluctuation is barred by F̃ "covers", with every band affirmative.
    - P2 uses PV's bars exactly.
    - False PASS is about 0.025 at the boundary, at either truth, by construction, and calibrated. §6.3–§6.5.
  - **The null** (BLOCKING): a written calibration law with fixed bias alternatives and centred drawn-only
    fluctuation; a whole-rule ensemble simulation (200 ensembles × grid, bootstraps included) with Clopper–Pearson
    bounds; conservative cutoffs; analytic Gaussian fallback; sentinels. §6.1–§6.2.
  - **F̃ normalizes** the spread by its expected (N − 1)/N and its undrawn share (C_PL, C08). §6.1.
  - **Custody and spent-once** (BLOCKING):
    - director-run writer, readout and PG, through the wrapper;
    - director-held seeds, committed by digest;
    - authenticated encryption only, with manifests verified before decrypt;
    - scans after both roles, with trap cleanup;
    - a director-controlled atomic consumption record, with crash semantics;
    - a synthetic-seal wrapper test;
    - the cooperative assumption stated. §3.3, §3.4, §4.2.
  - **ST1 and the exception** (BLOCKING): ST1 is a diagnostic trigger; the exception needs code-level evidence; one
    exception only; its branch stops as its own priced phase PX outside P1's cap. §3.3.
  - **Majors:**
    - where each source acts (§3.2);
    - ST2 eligibility and precedence (§3.3, §6.4);
    - the reservation ledger (§3.3);
    - missing toys (§3.3);
    - the C-PSD fallback scope (§6.2);
    - C_b as a fitted allowance, with the held-out quadratic and outside-span metric (§5.2, §6.1);
    - f̂_R edge cases (§5.2);
    - K_C's fixed combinations and rank check, and measurability eligibility frozen before the seal (§5.3);
    - a span-level residual rule (§5.2);
    - the carry's finiteness and rounding checks (§2);
    - P0's go/no-go control matrices (§3.1);
    - the novelty test (§4.1).
  - **Fidelity:** the 142-eigenvector wording; F1's 1.3275 context; the RE-2 part C citation; PV vs COV2D differences;
    A0's tolerance origin.
- **Rev 6** answers agy's delta read of rev 5 (`reads/agy-rev5-REPORT.md`; NO-GO):
  - the bias grid uses each candidate's own bias block, so it is defined for K0 and K_A (BLOCKING 1);
  - the 20,000-replicate budget, seed and b = 0 setting for q̂ and p̂_i are restored (BLOCKING 2);
  - F_exp is per band (u_R) and defined for K_C (MAJOR 3);
  - the k ≥ 25 SE formula is the normalized one (MAJOR 4);
  - the simulation's inner bootstrap is cut to 200 resamples, with its cost and place stated (MAJOR 5);
  - the stale "inconclusive" in §5.1 and "Grok" in §8 are fixed, and the seed block is named c08 throughout (MINOR).
- **Rev 7** answers codex-school2's confirming read of rev 6 (`reads/codex2-rev6-REPORT.md`; NO-GO, 11 bind-readiness
  fixes; agy's delta read of rev 6 was GO, `reads/agy-rev6-REPORT.md`). Following the director's convergence rule, it
  removes machinery where it can rather than defend it:
  - **Fix 1:** one drawn-covariance decomposition through the spectral map L, used in V_F, u, u_R, F_exp and the law;
    δ is defined as independently drawn, probability-centred shifts; a non-positive F_exp is a refusal (§5.2, §6.1–§6.2).
  - **Fix 2:** q and p_i always come from the 20,000-draw bank, the fallback included (no analytic 0.6827); 0.6827 is
    named a content target; the size statement is conditional on the Clopper–Pearson endpoint event; zero-bias cutoffs
    are a reference, gated over the bias grid; sentinels are reported (§6.1).
  - **Fix 3:**
    - analytic delta-method guards, identical in grading and calibration, replace the bootstrap guard, so no inner
      bootstrap exists;
    - 400 ensembles;
    - per-truth gates of 0.10 (not-PASS) and 0.05 (deficit pass), one-sided Clopper–Pearson, allocated so that a
      candidate stays at or below 0.20 false-FAIL;
    - explicit deficit scenarios D1–D3, with the P-2 pass rate recorded separately;
    - no 0.025/0.075 guarantees;
    - every rate conditional on the surrogate (§2, §6.2, §6.5).
  - **Fix 4:** K_C's k comes from the fixed grid {25, 50, 73}, with the cheap bars evaluated first; a benchmark gates P2
    (§5.3, §6.2).
  - **Fix 5:**
    - a seed‖salt sha256 commitment, per the director;
    - seed-bearing job scripts and logs captured into the encrypted seal;
    - a writer manifest, encrypted and verified before readout decryption, together with the frozen digests;
    - gpg only (age is interactive);
    - cleanup limited to campaign-owned paths (§3.4, §4.2).
  - **Fix 6:** consumption keyed by seal and role; the freeze digest bound at first acquisition; the transition
    persisted before plaintext; any post-decrypt crash is terminal (§3.3).
  - **Fix 7:** ST1 denominators, guards and sequences for a W1 trigger, a W2 trigger, an unexplained firing and a later
    firing; the post-fix acceptance check; PX items; a reprice before any new paid work (§3.3).
  - **Fix 8:** prefix polling removed; the 409.22 ceiling pinned; intents persisted before submission; lost IDs
    reconciled; terminal incompleteness after same-seed retries, for P1 arms and PV (§3, §3.3).
  - **Fix 9:** §4.3 licenses the two named deformations only; §7 is exhaustive in three parts (construction finding,
    baseline challenge, selected candidate); the 02a fallback is for absence only (§4.1, §4.3, §7).
  - **Fix 10:** lateral and norm act on the unfolded output, as in COV2D; the sim stream is pinned; A1f and A1p are
    reported in a common basis; a non-cancelling rounding measure; the A1 map digests, with the C_model lineage named
    as RE-2's statement (§2, §3.2).
  - **Fix 11:** a directed residual; one cutoff rule; degenerate edges assigned to the lower-rank band or included
    whole; measurability inputs and provenance; the C_b⁰ symbol; the frame identity restricted; the outside-span
    fraction in whitened retained coordinates (§5.2, §5.3, §6.1).
  - **Fix 12:** the 142-eigenvector wording (rank fell by one), and the illustration's equal-variance qualifier.
- **Rev 8** applies the director's scope ruling on the rev 7 reads (`reads/*-rev7-REPORT.md`; agy NO-GO on majors only,
  codex-school2 NO-GO with 5 blocking). It takes codex-school2's simpler cuts in full:
  - **ST1:** if PX has no funded path, the branch ends at the construction finding and K_A is omitted. The N5 and
    N4 − N2 guards use band-level influence scores (§3.3).
  - **One Gaussian reference law,** N(0, V_drawn). The band bank, the remainder and the fallback are dropped. V_drawn has
    a C-PSD control and a sampled-covariance control (§6.2).
  - **The testability veto and every rate claim are removed.** The surrogate runs are descriptive stress tests, printed
    and read by nothing. PASS rests only on the fixed affirmative bars applied to the real toys. K0's verdict is reported
    as observed (§6.2–§6.5).
  - **K_C and outcome C are dropped.** The outcomes are A, B or none, plus the construction finding. The measurability
    study stays separate (§5.3, §7). The director informs Joseph of this scope change.
  - **Fixed as written:** codex's PV toy-law sentence (§3.4); agy's three MAJOR (the §9 bars, the N5 guard, D2's
    formula) and three minor (F̃_R's SE, the PX scale note, D3's signs); the outcome rows "PV never ran" and
    "no challenge" (§7).
  - **Custody, in codex's simpler form:**
    - one durable spend record, fsynced and committed before any decryption;
    - one authenticated writer manifest, with every unfold output chained to it;
    - ciphertext hashes only published;
    - pinned gpg flags;
    - terminal rules;
    - the cooperative assumption stated (§3.3, §3.4, §4.2).
  - **The price is unchanged:** 408.55–409.22 node-h. K_C and the testability simulation were laptop-only work, and PV's
    readout gets lighter.

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
2. **C_run's trace is small in 2D:** τ = 0.0098 per ndf at both tunes (REGRADE 2D). In the G18 regrade, 142 of C_T's kept
   eigenvectors had a component outside the new kept span, with maximum residual near 1, and the rank fell by one, from
   205 to 204. The trace reading is a separate diagnostic. So every candidate prints the cut diagnostic.
3. **G18 and AR23 are spent.** COVFIX uses them only to calibrate (P0) and to describe. They enter no candidate block,
   no bar and no choice.
4. **Never-read truths are cheap.** F1's whole recorded charge was 1.3275 node-h for both GENIE v3 tunes. That
   includes failed attempts and 0.609167 node-h of downstream closure and pseudo-experiment jobs, so it is historical
   context for PG's estimate, not its price.

## 2. The covariances, the carry, and notation

**The reported matrices.**
- **Q_rep** is the adopted 2D covariance, COV2D-G2R's rebuild (DECISION-20261114-joseph-d1-g2r-adopted.md). Its file is
  key `Q` of #1167's run2 `g2r/outA/cov2d_Q_205.npz`, sha256
  `ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295`
  (`fd/receipts-cov2d/g2r/re2shapes/run2/NODE-SHA256.txt:222`). cov2d holds a sha-verified laptop copy.
- **Its blocks:** `Q` = `s5_total` + `C_PL`, and `s5_total` = `universe` + `stat` + `c08`. Both identities were
  measured exact (maximum relative difference 0) on that copy on 2026-11-22. P0 re-checks them as a control.
- **C_model** is RE-2 part C's relative matrix: "C_model = sum_k s_k s_k^T (M2), kappa = 1, fractional", sha256
  `11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470`
  (`state/2d-closeout/stageF/methods/re2/RE2-PARTC-REPORT.md` §7; `cmodel_R.json`), reported beside
  Q_rep. Absolute at a central value x: C_model_abs(x) = diag(x) C_model diag(x).

**K0, the matrix under test.** COV2D graded C_T = (remade S5 blocks) + C_model_abs at each tune, without C_PL. COVFIX's
reported-procedure analogue at the data's point is:

K0_R = V_F,0 + V_b,0, with V_F,0 = Q_rep (the fluctuation block) and V_b,0 = C_model_abs(x_R) (the model block).

**The carry to a truth t.** All of COVFIX's blocks are absolute at x_R, and they are carried by one formula:

V(t) = D_t V D_t, with D_t = diag(x̂_t / x_R).

- x̂_t is the central unfold, with E_R's argv, of t's expected pseudo-data rounded to integers: round(λ⁺) on every
  signal and background row, with λ⁺ as in §3.4 and round-half-to-even. The data tree holds integer counts only, so a
  fractional Asimov file is not constructible. This costs one unfold per truth.
- x̂_t uses t's CV nature: no band draw and no sim, with r_t applied.
- **Rounding check:** per reco cell with Σλ⁺ > 0, the non-cancelling measure Σ_rows |round(λ⁺) − λ⁺| / Σ_rows λ⁺ is
  reported. A cell above 1e-3 is a refusal. Cells with Σλ⁺ = 0 are excluded and counted.
- **D_t must be finite and nonzero** on all 205 aligned cells, or the carry refuses at that truth.
- The formula has the shape REGRADE §2 used for C_run and COV2D §4.4 used for the seed block c08. Its reference vector is §2's x̂_t,
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
- **The guard** (COVFIX's own rule) is analytic, and the same in every reading and in §6.2's stress runs: h(X) =
  t_{0.975, N−1} · SE(X), where SE(X) = sd_s(ψ_s)/√N and ψ_s is X's per-toy influence term:
  - for M or a total band mean, ψ_s = χ²_s/ndf, or its band analogue. M is a mean of independent per-toy terms, so this
    is exact;
  - for a spread F or a band F_R, ψ_s = (1/ndf_R) Σ_{i∈R} [(z_{s,i} − m_i)² − v_i], the delta-method influence function
    of the sum of 1/N variances;
  - for F̃, SE(F^F)/F_exp, and for a band F̃_R, SE(F_R^F)/F_exp,R;
  - sd_s is the sample SD (divisor N − 1). A zero or non-finite SE refuses that reading;
  - it is a fixed rule with approximate coverage for quadratic toy scores, and is described as such.
  - For a difference of two independent ensembles (ST1), SE² is the sum.
  - Bootstrap SEs are used only for the construction quantity f̂_R and the descriptive bias statistics (§5.2, §6.1).
- **Labels** for any ratio X:

  | label | X |
  |---|---|
  | over | < 0.8 |
  | covers | [0.8, 1.25] |
  | under | > 1.25 |

  A label is read only if [X − h, X + h] lies inside one label's interval. Otherwise the reading is "unresolved across
  <labels>". Bands use the same rule and edges.
- **The total's affirmative bar** is X + h ≤ 1.25: the upper guarded bound lies at or below the tolerance.

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
  - **Joseph chose full** (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`, his governing re-confirmation: "Full, as designed"), with N5, at about 409 node-h
    at most. ST6 keeps the campaign inside that approved total. The lean columns are kept as the record of the
    alternative he did not choose.
- **ST6, the cumulative ceiling** (§3.3).
  - Joseph's approved total is pinned in every connect.
  - Each submission's charge ceiling is its nodes × its `--time`. Each toy job's `--time` is 1.5 × its priced per-toy
    time (0.19 node-h is a mean), so a slow job is not killed, and a stalled one cannot charge more than its ceiling.
  - A phase is submitted in chunks small enough that ended charges plus unended ceilings stay within its cap (ST3).
  - The admission check is ST3/ST6's reservation ledger (§3.3), not a prefix poll of sacct.
  - **The ceiling is pinned in the binding:** 409.22 node-h, Joseph's approved total
    (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`). That is separate from the expected price and from the 468
    sum of caps.

### 3.1 P0: what the committed records give (0 node-h, local, descriptive)

- **Controls:** Q_rep's two block identities, its sha256, C_model's sha256, and C-PSD on every block:
  λ_min ≥ −1e-12·λ_max. **A failure stops at P0.**
- **The carry check.** At G18 and AR23, K0 carried by §2's formula is compared with COV2D's remade C_T.
  - The carry is done twice: with COV2D's committed realization-based x̂_T from `blocks_<T>.npz`, and with §2's round(λ⁺)
    vector, whose two unfolds run in W1. The P0 readings that need the second vector are completed after W1.
  - The readings are COV2D's committed errors `E_<T>.npz` under each, the eigenvalue ratio per band, and the principal
    angles between the kept spans.
  - This is descriptive. It states the size of the carry approximation and of the difference between the two vectors.
- **The residual rule's go/no-go control on spent data.** §5.2's residual rule is applied to the committed regrade
  pair at G18 and AR23:
  - "old" is COV2D's C_T from `blocks_<T>.npz`, with its fluctuation reference C_T − C_model_abs(T);
  - "new" is C_T + C_run(T), with C_run carried from Q_rep's `C_PL` exactly as REGRADE carried it;
  - both are evaluated at the tune's frame, with C_T's own x̂_T.
  The rule's maximum principal angle between the well-determined spans is printed. If the rule fires there, P0 stops
  and goes to the director: a rule that rejects that pair would reject K_B for no reason.
- The per-mode profiles (m_i, v_i, q_i) of COV2D's committed errors under the carried K0, under C_T, and under G2R's
  C_T′.
- IBUKT A2's mean residuals (`state/2d-closeout/ibukt-a2/readout.json`), times E_R, in K0's modes: m_i only.
- c2 as scoped: T2A's mean error projected on C_PL's two directions.

These validate nothing.

### 3.2 P1: the construction measurements

Each cell is a toy ensemble unfolded by the production procedure (re2_driver.py, E_R's argv). The seeds are
pre-committed and disjoint from every committed ensemble; a test checks them against COV2D's, c08's and S1's seed lists.

**The full source list** is "data Poisson + bands + lateral + norm + sim", where:
- the bands are COV2D's 38: Flux (one of 100 universes, constraint-weighted), 2p2h (1 of 3), and the 36 others (one
  endpoint each), composed first-order on `w_reco`, `w_truth` and `w_bkg` by `cov2d.draw` (COV2D §4.2);
- lateral is COV2D's surrogate over 5 bands;
- norm is x̂ × (1 + 0.014 z);
- sim is S1's signal and background simulation-weight Poisson redraws at fresh seeds.

**Where each source acts.** COV2D's `--data-file` replaces the data tree and leaves the unfolding simulation in
`--omnifile`.
- **Data Poisson** acts on the pseudo-data only.
- **The 38 weight bands and the truth deformation r_t** act on the toy's nature: its pseudo-data and its graded truth,
  as COV2D §4.2 composes them. The unfolding uses the CV simulation, so a band draw makes the nature differ from the
  unfolding model. That is the sense of "perturbed response" here; the unfolding response itself is not redrawn by a
  band.
- **Lateral and norm act on the unfolded output,** as COV2D §4.2 applies them, after the unfold: x̂ += Σ_b s_b Δ_b(t)/2,
  then x̂ × (1 + 0.014 z). They do not touch the graded truth.
- **Sim** acts on the unfolding side only. It redraws the simulation weights the unfold uses, as S1's three-stream
  bootstrap does, multiplying the CV simulation weights, independently of the nature's band draws. It changes neither
  the pseudo-data nor the graded truth.
  - Toy s's sim stream is `numpy.random.default_rng([seed_s, DRAW_SALT, 2])`. That is the third stream beside COV2D's
    draw stream `[seed_s, DRAW_SALT]` and count stream `[seed_s, DRAW_SALT, 1]`.
  - The redrawn weights reach the unfold through the bootstrap-weight hook S1's code already uses.
- **N4 − N2** is the incremental change in scatter from the nature-side sources. It is read as additive only under the
  blocks' own additive model, which is disclosed, not verified.

| cell | truth | what each toy draws | toys full / lean | seed base | node-h full / lean |
|---|---|---|---|---|---|
| **N1** data stream, same-event | nominal | Poisson pseudo-data at data size from the MC reco weights | 200 / 150 | 9_100_000 | 38 / 28.5 |
| **N2** + simulation statistics | nominal | N1 + sim | 200 / 150 | 9_200_000 | 38 / 28.5 |
| **N5** data stream, held-out | nominal, MC half A | pseudo-data from half A, unfolded with half B's response; plus half-B data-stream bootstrap replicas (`--bootstrap-streams data`) for that configuration's own data-stream block S1_B | 200+200 / 150+150 | 9_500_000 (toys), 9_510_000 (replicas), 9_520_000 (split) | 76 / 57 |
| **N3** estimator seed | nominal | one fixed N1 pseudo-dataset (seed 9_300_100); estimator seeds 9_300_000–9_300_049 | 50 / 50 | — | 9.5 / 9.5 |
| **N4** all sources at nominal | nominal | the full source list, with r ≡ 1 | 200 / 150 | 9_400_000 | 38 / 28.5 |
| **A1f** alternative truth, fixed response | genie_mec, nuwro, gibuu (the three named PV2D deformations) | N1 only, response nominal, truth deformed by the vertex's 2D map | 3 × 60 / 0 | 9_600_000 + 10_000·j | 34.2 / 0 |
| **A1p** alternative truth, perturbed response | the same three | the full source list at the deformed truth | 3 × 100 / 3 × 100 | 9_700_000 + 10_000·j | 57 / 57 |
| **central unfolds** | nominal; the three vertices; G18 and AR23 | round(λ⁺) pseudo-data (§2), one unfold each, for D_t | 1 + 3 + 2 | — | 1.14 / 1.14 |
| **existing** | G18, AR23 | COV2D's toys (data Poisson + bands + lateral + norm; no sim) | 300 + 300 | committed | 0 |

- j = 0, 1, 2 for genie_mec, nuwro, gibuu.
- **The named deformations** are PV2D's ratio files `2d-unfolding/pv2d/ratios/{genie_mec,nuwro,gibuu}.json`, sha256
  `cfaaf4d663a392ce…`, `785180dd9dba80a0…` and `b62c224ac4321f38…`, each matching `projections.json`
  (`8241807f4dddf678…`).
  - That these are the shifts behind C_model ("C_model = sum_k s_k s_k^T") is RE-2 part C §7's statement, and is not
    re-verified here. The text calls them the named deformations.
- **A1f and A1p are in-sample.** A1f measures the estimator's bias at those truths (the review's cell 4, in-sample), and
  A1p the truth-dependent spread. Both are reported in one common basis, K0's fluctuation block carried to each truth,
  as bias (m_i) and centred scatter (v_i) side by side. The held-out alternative truths are PV's.
- **C_PL and C_run are not drawn,** because they have no generative law (SCOPING a3). They enter V_F as covariance.

### 3.3 Stop rules

**ST1, a diagnostic trigger for a construction-defect investigation.** It is read on W1 (N2, N3, N5) before W2 is
submitted, and on W2 for N4. A firing row flags a discrepancy; it does not by itself identify a defect.
- Each reading uses the spread only, never q, because nominal closure bias (IBUKT A2: up to 1.708 % noise-free) would
  otherwise enter. Nominal bias is reported separately (m_i, B_R).
- **The common basis** is K0's fluctuation block Q_rep, carried to x̂_MC and diagonalized there.
- **The ratio:** each row's per-mode ratio is ŝ_i over the row's denominator, projected in that basis, with
  ŝ_i = λ_i v_i. Only modes whose projected denominator exceeds 1e-12 × its maximum over modes are used.
- **The guard is §2's analytic SE.**
  - **Band-level influence scores.** For each row's band mean Ā_R/B̄ (numerator per toy, denominator per replica or
    block), one influence score per toy and, where the denominator is estimated, one per replica, by the delta method on
    the band mean of ratios. The modes share toys and replicas, so the scores are computed for the band as a whole.
  - N4 − N2 is computed this way on each side, and the two independent variances add.
  - For N5, the toy-side and replica-side variances add, under conditional independence of the two ensembles. The
    replica-side term uses the derivative −Â_i/B̂_i² of each ratio with respect to its denominator.
- Every band with at least 10 modes can fire.

| block | reading (band mean of the per-mode ratio, guarded) | ST1 fires if any band reads |
|---|---|---|
| `stat`'s data-stream part, through its bootstrap method | N5: ŝ_i / u_iᵀ S1_B u_i, with S1_B from N5's own 200 replicas | "under" or "over" |
| `stat` (three streams) | N2: ŝ_i / u_iᵀ stat u_i | "under" only. An N2 "over" is recorded and does not fire, because KI 85's earlier-band finding allows same-event under-scatter; that is a possibility, not a guarantee of direction. |
| `c08` (the seed block) | N3: ŝ_i / u_iᵀ c08 u_i. One pseudo-dataset with the seed varied, against the production seed block. | "under" or "over" |
| `universe` | (ŝ_i^{N4} − ŝ_i^{N2}) / u_iᵀ universe u_i. This includes interactions between draws, clipping and the response, disclosed. | "under" or "over" |

N1 is never a construction-error reading. N1/N5 is reported as the same-event factor.

**The ST1 sequences,** fixed now. In every branch, no new paid work starts before the director's ruling.
1. **A W1 row fires.** W2 is not submitted. cov2d investigates the firing blocks' builders and reports.
   - **With code-level evidence,** the named exception below is written, and PX is priced. PX covers:
     - the regeneration;
     - the post-fix acceptance check;
     - W2's first-time work, already in the plan, recounted under the corrected builder.
     The whole remaining campaign (PX + W2 + PV) is repriced against the ceiling.
   - **Without code-level evidence,** the firing is "unexplained". The campaign continues without K_A only if the
     director rules so.
2. **The W2 row (`universe`) fires.** P2 does not start. The same investigation follows.
   - With evidence, PX covers the regeneration, the redraw of N4 and A1p (95.00), and the acceptance check, and the rest
     of the campaign is repriced.
   - Without evidence, the firing is "unexplained", as in 1.
3. **Repricing.** If the repriced remainder fits the ceiling, the director binds PX.
   - If it does not, PX has **no funded path**, and the ST1 branch ends at the construction finding, reported as a
     finding (§7, Part 1). K_A is omitted for this run, and the campaign continues with K0 and K_B.
   - W2's first-time work is counted once in the remainder, never as part of PX.
   - For scale: rebuilding `universe` (with laterals), `stat` and `c08`, plus the redraw, is 202.35 node-h before
     diagnostics, or 240.35 if the N5 replicas are rebuilt too.
   - After W2, `universe` alone plus the redraw brings P1 + PX to 420.09, which exceeds the 409.22 ceiling before PG and
     PV.
4. **A row fires after the sole exception has been bound.** The campaign stops and goes to the director.

**ST1's named exception, the only post-binding amendment to §5–§7.**
- **It needs code-level evidence:**
  - a reproducing unit test that fails on the old builder and passes on the corrected one;
  - the named bug;
  - the post-fix acceptance check. That check is the firing row's reading recomputed with the regenerated block, in
    the same common basis, on the same toys or on the redrawn cell. It must read "covers" in every band.
- **If the bug reproduces but acceptance fails,** the finding is "defect found; correction did not resolve the
  discrepancy". K_A is not formed, and the branch ends.
- **It may change** only the code that generates the firing blocks, never a substituted matrix. It may not change any
  bar, seed, the validation family, the §5.2 factor rule, C_b's rule, the k rule, or §7's order. One exception covers
  every row that fired by then.
- **PX's itemized regeneration:**
  - `universe`: 175 unfolds (33.25), plus 10 lateral (1.90) if laterals are rebuilt;
  - `stat`: 300 replicas (57.00);
  - `c08`: 80 unfolds (15.20);
  - the N5 replicas: 200 (38.00) if the data-stream method is corrected.
  The amendment states which constituents are reused. PX is outside P1's cap and inside the ledger.
- K_A is Q_rep with the corrected blocks, plus C_model_abs.

**KI 85.** Joseph superseded **both** of KI 85's sentences for COVFIX
(`DECISION-20261123-joseph-covfix-ki85-size-reader.md`). So N5 runs, and outcome A may change the 2D covariance; a change
enters the journal paper or a later Zenodo version, not the first release. Had he not superseded them, ST1 would record
and regenerate nothing, and N5 would not run. That gate is kept for the record.

**ST2, eligibility for PV.**
- The eligible candidates are K_A (if formed and PX was funded) and K_B, each only if it meets §5.3 at P2.
- K0 always runs as the baseline.
- A K_A that fails P2, or one omitted because PX had no funded path, is recorded in §7's construction finding.
- If no candidate is eligible, PV does not run. The baseline is then ungraded (§7).
- **If PX has no funded path,** the ST1 branch ends at the construction finding, reported as a finding, and K_A is
  omitted for this run.

**ST3 and ST6, one reservation ledger.**
- The ledger is serialized under flock in the campaign directory, and keyed by allocation job ID.
- **Before any submission,** an intent entry with the job name, phase and reservation is persisted. After submission,
  the job ID is recorded.
- **Lost IDs.** If a connect dies between submitting and recording, the next connect first reconciles every open intent
  from sacct, by job name and submit window. Until that is done, no submission proceeds.
- **Reservations:** nodes × `--time` (1.5 × the priced per-toy time), including exclusive allocations, with
  allocation-level walltime rounding. Jobs run with `--no-requeue`.
- **Accounting lag.** A reservation stays open until sacct shows the job terminal, and its charge is then reconciled
  once.
- **The gate,** atomic under the flock: reconciled charges plus open reservations plus the new reservation must stay
  within both the phase cap and the pinned 409.22 node-h ceiling.

**ST4, validation is spent once.**
- **The consumption record** is controlled by the director: append-only, in the director's scratchpad, mirrored in a
  commit, and keyed by **seal digest and role** (PV writer, PV readout).
- **The freeze digest is bound** to the seal at its first acquisition. A later freeze digest never resets consumption.
- **The spend is durable before any plaintext exists.** Under one lock, the wrapper appends "spent" for the original
  seal and role, fsyncs the record, and commits its mirror. Only then does it start decryption.
- **Terminal rules:**
  - an uncertain spend, from a lock or write failure, is terminal;
  - restoring a copy of the record, or changing the freeze, cannot create a fresh role;
  - a crash after decryption is a terminal stop for that role, with no retries;
  - same-seed retries apply only to the ordinary unfold jobs, never to the two secret-bearing roles;
  - any break in the seal, the manifest or the chain is terminal.
- An executability fix never permits a grading change after exposure.
- PV's readout writes one JSON of summary statistics; per-toy residuals and z arrays stay inside the process.
- §5–§7 cannot be amended after binding, except by ST1's exception, or an executability fix before any seal is
  decrypted that changes no number, bar, family, seed or choice rule.
- **The limit:** a later construction needs new sealed truths, and the catalog may not supply a third distinct family.

**ST5, guard refusals are terminal** for their phase: fences, atime, provenance, the A0 controls, the seal and
decryption checks, the manifest and chain checks, the scans, and C-PSD on the input blocks and candidates. §6.2's
controls refuse a candidate at a truth (§6.4) rather than stop the phase.
- **Completeness:** every P1 arm (including N5's replicas and PX's diagnostics) and every PV truth needs all of its toys.
- A job that ends other than COMPLETED may be resubmitted with identical seeds, at most twice, decided before any
  reading of that arm.
- If any toy is still missing after that, the phase is **incomplete and terminal**, and goes to the director. There is
  no grading on a subset; a failure can depend on a toy's input even when no residual has been read.

### 3.4 What a PV toy draws, and where

PV draws the full source list of §3.2, the same as N4 and A1p, at a sealed truth u.

- **The truth deformation.** r_u is u's own bridged ratio, applied per row by
  `s5e_deform.ratio_weight(gen, FINE, w_truth, ratio, 1.0)`, computed once with the CV `w_truth` and its rescale constant
  from `mc_truth_denom`'s rows (COV2D §4.1). The same per-row factor applies to every `mc_signal_reco` row. Rows outside
  the 5D grid and background rows get r = 1.
- **The toy law is §3.2's single recipe:** the 38 bands composed on the nature's reco and truth; lateral and norm on
  the unfolded output; sim on the unfolding side; Poisson on the pseudo-data.
  - **The lateral Δ_b(t)** are carried in relative form from part B's lateral products, Δ_b ∘ (x̂_t / x_R), as COV2D §4.4's
    fallback carries them, so no remake is priced.
  - **The draw order** is `cov2d.draw`'s: Flux, then the other 37 bands sorted, then the lateral signs, then norm. Sim
    and counts use their own streams.
- **The pseudo-data** are Poisson at λ⁺ = max(·, 0), on a count stream separate from the draw stream.
- **The graded truth** is each toy's own clipped composite truth, normalized with the drawn Flux universe's integral and
  completeness ≡ 1 (COV2D §4.2).
- **The estimator seed** is fixed at 42, and the seed block c08 is in every candidate.
- **Count:** 300 toys per sealed truth, seed base 9_800_000 + 10_000·u (u = 0, 1), plus one central unfold per truth.

**Who runs it, and where, in order.** cov2d writes and tests the bound PV code; it does not run the secret-bearing
roles. The **writer** and the **readout** are run by the director, or a session the director controls, through the
director's wrapper. The wrapper acquires ST4's consumption record, verifies every ciphertext's sha256 against
`PG-SEAL.sha256` before decrypting, and pipes the passphrase on stdin.
1. **The writer** runs on an exclusive compute node (`salloc --exclusive -N 1`, then `srun --exclusive -N 1 <writer>`,
   which forwards stdin to the task). The decrypted r_u lives only in that node's /dev/shm.
2. In that one process it writes, for all 600 toys, the pseudo-data files (reco-level counts, which the compute jobs
   need) and the graded truths, plus the two round(λ⁺) files for D_u. The graded truths are encrypted (§4.2) before they
   touch disk.
   - It also writes **one authenticated manifest**, encrypted with the same flags. The manifest binds the graded
     ciphertexts, the toy IDs, the hash of each pseudo-data file, and the central inputs, to the original PG manifest's
     digest and to the director-authorized freeze digest. Both digests are pinned in the binding.
3. Before exiting, and through a trap on failure, it removes its enumerated campaign-owned temporary paths on that node
   (in /dev/shm and /tmp). It then scans those paths and the campaign directory **by content**: every file's sha256 is
   compared against the plaintext hashes in the PG manifest, and every file is checked for an unencrypted graded-truth
   array. A hit stops the study. An exact-hash scan detects exact copies only, not repacked or partial plaintext, and
   that is disclosed.
4. The compute jobs unfold the pseudo-data only.
   - **The chain:** each job appends a chain record of (toy ID, pseudo-data sha256 from the manifest, unfold output
     sha256, the bound unfold invocation's sha256).
   - The readout verifies every record against the writer's manifest before grading. A missing or mismatched record
     is a break, and terminal.
5. **The readout** runs on its own exclusive node, from a fresh pipe. Before decrypting any graded truth, it verifies:
   - the writer's manifest;
   - the frozen code and arrays against `P2-FREEZE.sha256`.
   - the chain from the writer's manifest to every unfold output.
   It then decrypts the graded truths in-process, runs §6.2's controls and stress runs, and grades. Its summary is
   published only after the authentication checks and the scans succeed. Cleanup and scans cover enumerated
   campaign-owned paths only.

<!-- absence-ok: reading rule, scoping statement or verbatim review text about studies not yet run -->
**The wrapper is tested** before PV on a synthetic seal: a dummy truth, encrypted and sealed the same way, run end to
end. That test also measures the writer and readout allocation time, which replaces PV's unmeasured 1.0 node-h estimate
in a re-price before PV is submitted.

**After the freeze,** the unfolded outputs alone are not graded errors, and nothing they reveal can change a frozen
candidate (ST4).

**PV differs from COV2D's G18 and AR23 toys in more than sim:**
- different tunes;
- a different grading matrix (the carried K0 or a candidate, not COV2D's remade C_T);
- a different central-vector convention (round(λ⁺) and its unfold, not one Poisson realization);
- a different null (§6.2) and decision rule (§6.3).

The shared toy ingredients are the nature draws (`cov2d.draw`), the Poisson pseudo-data, the graded-truth construction
and the estimator. N2 probes sim's increment at nominal truth; it cannot establish sim's share at the alternative truths.

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
- **The novelty test,** applied to the probe's output: a chosen tune qualifies only if at least one of its CCQE class
  and its 2p2h class is used by **neither** spent tune. A tune whose two classes both appear among the spent tunes'
  classes is excluded, even in a new pairing. The 02a fallback substitutes only for 02b's **absence** from the product.
  02a shares 02b's CCQE and 2p2h classes, so a novelty exclusion of 02b excludes 02a too. If no qualifying tune
  remains for a slot, PG stops.
- The probe's output, the fallback taken and the overlap record are committed before generation. Partial overlaps are
  disclosed in §4.3.
- FD-F1-DECLARATION.md:76 is cited only for the product, path and qualifier convention.

### 4.2 Custody

**Who generates.** A session that is not cov2d and has read none of COV2D, T2A, G2R, REGRADE or this declaration's
§5–§7: a fresh session Joseph opens, which the director names at binding. **Binding requires it.** That session runs
F1's bound pipeline (`gen5d_v3.py`, `run_gevgen_v3.sh`, the pv-ladder ratios and the bridge), unchanged except for the
tune names and the seeds.
- **The seeds are director-held,** so a builder cannot regenerate the truths from public tune names and public seeds.
  - The director draws PG's seed base and a random salt.
  - Before generation, the director publishes sha256(seed base ‖ salt), and reveals both after PV's readout.
  - Tune u's task seed = base + 10_000·u + task index.
  - F1's generator takes the seed in its command arguments. PG's job scripts and logs therefore stay in the PG
    session's directory and are captured into the encrypted sealed set, under the cooperative assumption below.
- The director runs PG's connect through the director's wrapper, with the PG session's working directories private to
  that session by convention. That privacy rests on the one-account limit below.

**What it sees.** Its connect captures every stdout, stderr, log and meta file into the sealed set. The session sees
only a final summary of booleans (each step's pass/fail) and file counts. Physics outputs, such as f_MEC, process
fractions, CC counts and the ratio normalization k, are in the sealed meta only.

**The passphrase** is generated and held by the director. It reaches a connect only on a pipe from the director's
wrapper into the bound binary's stdin. It is never an argument, an environment variable or a file, so it never enters
shell history or the Slurm spool.

**Seal and encryption.**
1. The plaintext sha256 of every product is computed with O_NOATIME reads. **The plaintext hashes are never
   published.** A plaintext hash of a seed-bearing product, such as a predictable job script, would let anyone check
   seed guesses. They go only into an encrypted PG manifest.
2. Each product is encrypted with pinned flags. The passphrase is on fd 3 from the director's wrapper, and the payload
   streams on stdin and stdout:
   - encrypt: `gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc`;
   - decrypt: `gpg --batch --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --decrypt`.
   gpg's non-zero exit on an integrity (MDC) failure is a refusal. PG stops if the probe does not find gpg, or if a
   synthetic round trip with these flags fails.
3. A decrypt-and-hash round trip must reproduce each plaintext sha256.
4. The plaintext is deleted.
5. A content scan, of enumerated PG-owned paths only, against the plaintext hash list must come back empty, with
   cleanup through a trap on failure.
6. `PG-SEAL.sha256` (**ciphertext** sha256 per product, plus the encrypted PG manifest's ciphertext sha256) is committed
   **before P1's first connect**.

**Copies.** The ciphertext sits on pscratch and, **required**, on HPSS (htar from a login node, then hashverify). The
ratio files are not committed to the repo until PV's readout is. A missing or altered ciphertext stops the study. There
is no regeneration.

**Limits, disclosed.**
- All sessions share one Unix account. An exclusive node limits scheduling; it does not isolate a shared identity,
  filesystem, logs or process access.
- Before PV, the barriers against cov2d are the director's key and the director-held seeds, not file permissions.
  Beyond those, the design rests on a cooperative assumption: no builder reads another session's private directories
  or processes. That assumption is stated, not enforced.
- Atime does not detect O_NOATIME reads, so it is housekeeping only.
- The generating session saw the plaintext and is retired after PG.

### 4.3 What the validation family can and cannot show

Both truths are GENIE v3 configurations. G21_11b shares AR23's 2p2h class, and G18_02's models will be named by the
probe. A pass licenses readings at the **two named deformations under the fixed toy law** only, with those overlaps
stated beside it. It does not license a GENIE v3 model family, or any other generator. A non-GENIE validation truth would
need a sample this project does not have; that is disclosed, not tested.

## 5. Candidate constructions, built from P0 and P1, frozen at P2

**The build data** are N1–N5, A1f and A1p. COV2D's G18 and AR23 toys are descriptive only. **The selection data**, which any P2 bar,
choice or k reads, are N4 and A1p only. G18 and AR23 never enter a bar or a choice; their readings under each candidate
are printed descriptively. Nothing in PG's seal is read.

### 5.1 K0, the control, and K_A

- **K0** = Q_rep + C_model_abs(x_R), carried (§2): fluctuation block Q_rep, model block C_model_abs. Its expected PV
  reading is "under". **If K0 is VALIDATED at both sealed truths (§6.4),** the comparison showed no need for a change
  at those truths, and the outcome is "no challenge" (§7).
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
  inside itself at seed 9_991_000, with every eigenbasis held fixed at its full-sample matrix.
  - No independence between modes is assumed.
  - The disjoint seeds give independent random streams **conditional on the one shared simulation bank**; independence
    over alternative banks is not claimed.
  - The 3·SE trigger is a construction rule, with no stated error-rate guarantee.
- **Edge cases, fixed:**
  - an ensemble whose carried band holds fewer than 10 kept modes is left out of that band's mean, and the equal
    weights go to the rest;
  - if none remain, the band's factor is 1;
  - ranks are by eigenvalue, and only kept modes count;
  - **degenerate edges:** if eigenvalues within 1e-9 relative of each other straddle a band edge, the whole cluster is
    assigned to the lower-rank (higher-variance) band.
- **One decomposition, through the spectral map L.** With P_R the projector onto F_A's band-R eigenspace at x_R,
  L = Σ_R √φ_R P_R, where φ_R = f̂_R where the factor applies and 1 elsewhere.
  - V_F = L F_A Lᵀ.
  - Every constituent block is mapped the same way: L·universe·Lᵀ, L·stat·Lᵀ, L·c08·Lᵀ and L·C_PL·Lᵀ. So the undrawn part
    is U = L(C_PL + c08)Lᵀ, and the drawn part is V_F − U.
  - Both are carried by the same formula.
  - §6.1's u, u_R and F_exp, and §6.2's law, all use this U and this drawn part.
- **The post-carry fit** of V_F is reported per ensemble truth and per band.
- **Applied.** F_A is diagonalized at x_R. Its eigenvalues in ranks 1–73, 74–139 and ≥ 140 are multiplied by the
  corresponding f̂_R, but only where f̂_R − 1 > 3·SE(f̂_R); they are never lowered. The result is V_F at x_R, which is
  then carried. f̂_R is a rank-band summary transferred across bases. It is not a mode-matched estimate, and that is
  disclosed.
- **Why this is not the rejected scaling:**
  - f̂_R is measured on fluctuation ensembles at nominal and at three non-spent truths;
  - G18 and AR23 do not enter it;
  - it is one pre-registered factor per band, never searched until a bar passes.
  This is disclosed beside any result.

**The fitted bias allowance C_b, in the reference frame.** F_bias = {nominal (N4's mean), genie_mec, nuwro, gibuu (A1p means)}: the
non-spent build truths only. Each member is mapped to x_R before the sum:

β_t = D_t⁻¹ b̂_t, Σ_t = D_t⁻¹ S_t D_t⁻¹, and C_b = [ Σ_{t ∈ F_bias} (β_t β_tᵀ − Σ_t/(N_t − 1)) ]₊

- [·]₊ is the positive part: the eigen-decomposition with negative eigenvalues set to 0. Its rank is at most 4.
- **It is the sum, not the mean,** so no member is diluted. Writing C_b⁰ = Σ_t β_t β_tᵀ for the undebiased sum,
  β_tᵀ (C_b⁰)⁺ β_t ≤ 1 for each member. C_b itself, debiased and projected, need not keep that bound.
- **The frame identity** b̂_tᵀ V(t)⁻¹ b̂_t = β_tᵀ V⁻¹ β_t holds for ordinary inverses with D_t nonsingular. The grading
  pseudoinverses, with their own cuts, are computed directly in the truth's frame.
- **G18 and AR23 are not in C_b.** Their biases are large; T2A's mean-error parts against C_T are 13.61 and 20.97 per
  ndf. In the sum they would set the bias block's width in exactly the directions a GENIE tune's bias is expected to
  lie, and the one-sided total bar would then pass by their size. Their mapped biases β_G18 and β_AR23 are printed
  against C_b descriptively: β ᵀC_b⁺β, the fraction outside C_b's span, and M under K_B.
- **What C_b is, and is not.** C_b is a fitted bias allowance.
  - The positive-part projection changes its expectation, and it can lose the undebiased sum's member-wise bound.
  - It is not claimed to bound any model class, nor to over-cover every smaller bias.
  - The total is barred by an affirmative upper bound (§6.3). The fluctuation is barred two-sided and separately.

**K_B = V_F + C_b** at x_R, carried by §2's formula. It must pass C-PSD and print its cut diagnostic against K_A's:
- the kept sets under §2's cut, which is referenced to each candidate's own λ₁(V_F);
- the kept modes of K_A outside K_B's kept span, and their maximum residual;
- the smallest kept and the largest dropped eigenvalue.

**Residual rule (K_B against K_A only):**
- Only K_A's well-determined modes are checked, those with λ_i ≥ 1e-6·λ₁(F_A), evaluated at x_R.
- With U_A,well their orthonormal basis and P_B,kept the orthogonal projector onto K_B's kept span, K_B is not
  admissible if the directed residual ‖(I − P_B,kept) U_A,well‖₂ exceeds 0.1. It is directed, so a smaller new span
  lying inside the old one cannot pass by dropping an old direction.
- An ndf difference alone is printed, not a stop; tail modes below 1e-6·λ₁(F_A) are printed, not stopped on.
- P0 calibrates this rule on the committed regrade pair (§3.1).

### 5.3 Admission bars (P2, on the selection data only)

A candidate V = V_F + V_b is admissible only if, at N4 and at each A1p truth, it passes **the same bars as PV** (§6.3,
P-1 to P-4):
- F̃ and every band with at least 10 modes read "covers";
- M + h ≤ 1.25, and the same for every total band;
- no joint or per-mode under-flag;
- §6.2's controls pass.

It must also pass C-PSD, and, for K_B, §5.2's residual rule. These bars are in-sample, so they admit a candidate; they
never pass one. G18's and AR23's readings under every candidate are printed and decide nothing.

There is no reduced-reporting candidate. The measurability study is a separate study, and no COVFIX reading depends on
it.

### 5.4 Freeze

At P2's end, the code and arrays defining K0, K_A (if any) and K_B are committed with sha256 in `P2-FREEZE.sha256`, and
bound by the director before PV's first connect.

## 6. Readings and bars, fixed now

### 6.1 Per ensemble and per truth

<!-- absence-ok: reading rules for future measurements -->
**Fluctuation readings,** against V_F in V_F's carried basis (u_i^F, λ_i^F).
- **The undrawn part** is U = L(C_PL + c08)Lᵀ carried (§5.2). C_PL is not drawn, and c08 is not drawn because the seed
  is fixed at 42.
- **For a correct V_F,** the expected 1/N spread ratios are:
  - total: F_exp = ((N − 1)/N)(1 − u), with u = Σ_i u_iᵀU u_i / λ_i^F / ndf_F;
  - band R: F_exp,R = ((N − 1)/N)(1 − u_R), with the same sum restricted to i ∈ R.
  - A denominator at or below zero refuses the candidate at that truth.
- **What is labelled** is F̃ = F^F / F_exp, and per band F̃_R = F_R^F / F_exp,R. u, u_R and F_exp are printed.

**Total readings,** against V = V_F + V_b:
- M and its bands;
- the split M = (1/ndf)Σm_i² + (1/ndf)Σv_i, exact under §2's divisor. The m_i² part includes the noise of the
  estimated mean;
- §5.2's cut diagnostic.
- Every reading is stated separately for each sealed truth and each band with at least 10 modes.

**The held-out bias against the fitted allowance** (descriptive, K_B only). With β̂_u = D_u⁻¹ b̂_u and
Σ_u = D_u⁻¹ S_u D_u⁻¹:
- **Q_u** = β̂_uᵀ C_b⁺ β̂_u − tr(C_b⁺ Σ_u)/(N_u − 1), with C_b⁺ the pseudoinverse at cutoff 1e-12 × C_b's largest
  eigenvalue.
- **The outside-span fraction.** y = W_F β̂_u, with W_F whitening V_F's kept modes at x_R. The fraction is
  ‖(I − P)y‖² / ‖y‖², with P the projector onto the range of W_F C_b W_Fᵀ, whose rank is set by the 1e-12 cutoff. Both are
  in that one frame. A zero denominator is reported as undefined.
- Both carry toy-bootstrap SEs (seed 9_993_000). They enter §7's sentences, and decide nothing.

**Joint and per-mode readings.**
- **The joint reading** is the count K_J = #{s : χ²_s ≤ F⁻¹_{χ²(ndf)}(0.6827)} against V(t). Here 0.6827 is a fixed
  content target.
- **The per-mode reading** is #{s : |z_{s,i}| ≤ 1}.
- **The reference probabilities** q (joint) and p_i (per mode) are estimated from 20,000 draws of §6.2's Gaussian law at
  zero bias, at seed 9_992_000, per candidate and truth. The whitened covariance W V_drawn Wᵀ is not the identity, so no
  analytic 0.6827 is assumed.
- **The cutoffs:**
  - "under" at a count ≤ k_J, the largest k with P(Bin(N, q) ≤ k) < 0.025; per mode, the largest k with
    P(Bin(N, p_i) ≤ k) < 0.025/ndf;
  - "over" symmetrically;
  - each uses the conservative end of its 95 % Clopper–Pearson interval: the lower end for "under" and the upper end
    for "over";
  - a cutoff no k satisfies has a sentinel, −1 or N + 1, which never flags. P-3 and P-4 then report "no under-flag
    (flag impossible at this N)".
- **The size statement is conditional.** Each flag's size is at most nominal on the event that the endpoints bracket
  the true probabilities in the required direction, and only for the zero-bias Gaussian reference. A nonzero bias
  changes those probabilities.

### 6.2 The reference law and its controls

**The law,** for a candidate V at truth t: e ~ N(0, V_drawn(t)), with V_drawn = V_F − U (§5.2) carried. There is no band
bank, no remainder and no fallback.

**Controls:**
- V_drawn(t) must pass C-PSD on its retained space (the 1e-12 cutoff), or the candidate is refused at that truth.
- **The sampled covariance check:** the 20,000 draws' sample covariance Ŝ must satisfy max_i |u_iᵀŜu_i / λ_i − 1| ≤ 0.05
  over V_drawn's kept modes. That is five times the per-mode sampling SD √(2/20000) = 0.01. Otherwise the candidate is
  refused at that truth.

**Descriptive stress runs,** printed and read by nothing. For each candidate and truth, 400 ensembles of N errors per
scenario (seed 9_994_000) are graded by §6.3's rule, and the pass fractions are printed:
- zero bias;
- b = ±√κ_j w_j for each eigenpair of the candidate's own bias block, with eigenvalues above 1e-12 × the largest and each
  sign fixed so the largest-magnitude component is positive;
- three deficit scenarios, with φ the drawn fluctuation and a = tr(V⁺V_drawn)/ndf:
  - **D1:** φ scaled by √(1.25/a), if a > 0;
  - **D2:** for each total band R with at least 10 modes, with P_R = Σ_{i∈R} u_i u_iᵀ in V's basis,
    φ → (I − P_R)φ + √(1.25/a_R) P_R φ at zero bias, where a_R = (1/ndf_R) Σ_{i∈R} u_iᵀ V_drawn u_i / λ_i; defined if
    a_R > 0;
  - **D3:** for each bias direction w_j, b = ±β w_j with β² = (1.25 − a)·ndf / (w_jᵀV⁺w_j), if a < 1.25.
- They veto nothing, and no rate is claimed from them.

### 6.3 PASS at a sealed truth (PV)

Every check is affirmative, applied to the real toys:
- **P-1, fluctuation:** F̃ reads "covers", and every band F̃_R with at least 10 modes reads "covers". An unresolved band
  fails.
- **P-2, total:** M + h ≤ 1.25, and the same for every total band with at least 10 modes.
- **P-3:** no joint under-flag, reported as in §6.1 when a sentinel applies.
- **P-4:** no per-mode under-flag, reported the same way.

### 6.4 The PV verdict per candidate, and precedence

Read in this order; the first condition that holds is the verdict:

| verdict | condition |
|---|---|
| **REFUSED** | a control refuses the candidate at either truth: §6.2's checks, a non-positive F_exp, the carry checks (§2), or C-PSD |
| **FAILS** | at either truth: M − h > 1.25 or a total band does so; P-3 or P-4 flags "under"; or F̃ or a band reads "under" |
| **INFLATED** | no FAILS, and F̃ or a band reads "over" at either truth |
| **VALIDATED** | P-1 to P-4 hold at both truths |
| **UNRESOLVED** | otherwise, for example a band unresolved across labels, or M + h > 1.25 with M − h ≤ 1.25 |

K0's verdict is reported as observed. No control or simulation can suppress an observed deficit.

### 6.5 No operating rates are claimed

PASS rests on the fixed affirmative bars applied to the real toys. The size statements of §6.1 are conditional on the
zero-bias Gaussian reference. §6.2's stress runs are descriptive. COVFIX claims no false-PASS or false-FAIL operating
rate.

## 7. What each outcome licenses (adoption and wording remain Joseph's and the director's)

The result has three independent parts, each reported.

**Part 1: the construction finding** (ST1 and its exception), licensed by its own evidence, whatever PV finds:
- "ST1 did not fire."
- "ST1 fired at <rows>; unexplained."
- "A construction defect in <block>'s builder was found (a reproducing test fails on the old builder and passes on the
  corrected one); the corrected block passed the acceptance check." Then whether K_A was eligible at P2, or "PX had no
  funded path, and K_A was omitted for this run".
- "A defect in <block>'s builder was found; the correction did not resolve the discrepancy."

Any covariance change from Part 1 enters the journal paper or a later Zenodo version, not the first release
(`DECISION-20261123-joseph-covfix-ki85-size-reader.md`).

**Part 2: the baseline** (K0's PV verdict, as observed):
- **challenge:** K0 FAILS at one sealed truth at least;
- **no deficit shown:** K0 is VALIDATED at both. "At the two named sealed tunes, the reported covariance showed no
  deficit under these bars."
- **unchallenged:** K0 is INFLATED, UNRESOLVED or REFUSED;
- **ungraded:** PV did not run, because ST2 left no eligible candidate, or a stop or terminal rule ended the campaign
  first.

**Part 3: the selected candidate:** the first VALIDATED, in the fixed order K_A, K_B, among the eligible candidates.
**A or B licenses its sentence only with a challenge.** That is policy. Without a challenge, Part 1's finding still
stands alone, and each candidate's PV verdict is reported descriptively.

<!-- absence-ok: outcome licensing table for a future result -->
| outcome | condition | licensed sentence (substance, not wording) | not licensed |
|---|---|---|---|
| **A** | challenge; K_A selected | "With the corrected <block>, at each of the two named sealed tunes under the declared toy law, the fluctuation block's mean ratio <F̃ ± h> and every band read 'covers', and the total's guarded upper bound is <M + h> ≤ 1.25 (and per band), with no joint or mode under-flag." | a model-class claim; coverage at the data; that the total is tight |
| **B** | challenge; K_B selected | "At each of the two named sealed tunes under the declared toy law: the fluctuation block, measured on nominal and alternative-truth ensembles, has mean ratio <F̃ ± h> and every band reads 'covers'; with a fitted bias allowance from nominal and the three named PV2D deformations, reported separately, the total's guarded upper bound is <M + h> ≤ 1.25 (and per band), with no joint or mode under-flag. The held-out biases against the allowance: Q_u = <value ± SE>, outside-span fraction <value ± SE>." The factors f̂_R and C_b's rank and trace are printed with it. | coverage of any model family; "covers" for the total beyond the printed bound; a cause of the bias; that the allowance bounds a model class |
| **none, with a challenge** | challenge; no candidate VALIDATED | Nothing new. "Coverage remains unvalidated" stands, with P1's readings and every candidate's verdict as description. | any covariance change |
| **descriptive only** | no deficit shown, or unchallenged | Part 2's sentence, if any, and each candidate's verdict as description. A VALIDATED candidate is reported as such, but licenses no A or B sentence. | any covariance change; an A or B sentence |
| **none, PV never ran** | ungraded | Part 1's finding, and P1's readings as description. | any statement about the sealed tunes |

- **In-sample disclosure.** An A sentence states its corrected block. A B sentence states that C_b was fitted from
  nominal and the three named deformations (not G18 or AR23), and that the factors f̂_R came from N4 and A1p. Both name
  the two sealed tunes and their overlaps (§4.3), and say that the covariance is the reported one carried in relative
  form (§2).
- **Coexistence.** Part 1's finding and Part 3's outcome are reported together.
- **INFLATED** is reported as "the fluctuation block is wider than the held-out scatter by <F̃, bands>".
- **UNRESOLVED** is explained as sampling ambiguity only when a band or the total is unresolved across labels. Resolving
  it needs a newly authorized test, with an amendment and a price, never a re-read of the same toys under a changed
  rule.

## 8. Code, tests and audit before any compute

- **Reused unchanged where possible:** re2_driver.py `--data-file`, cov2d_writer, `cov2d.draw` (with r ≡ 1 for N4),
  S1's three-stream bootstrap code (for sim, and with `--bootstrap-streams data` for N5's replicas), F1's pipeline (PG),
  and `cov2d.draw`'s composition law for the toys.
- **New code:**
  - the N-cell and A1 toy writers, with a fixed-response mode and the 2D-map truth deformation;
  - the N3 seed arm;
  - the N5 half split;
  - the §2 carry;
  - the §3.3 ST1 readings;
  - the §5 builders and the residual stop;
  - the §6 readout, summary-only, with §2's analytic guards, §6.2's Gaussian reference law and its controls, and the
    descriptive stress runs;
  - PG's probe (with the novelty test), capture wrapper, authenticated encryption, seal checker and content scans;
  - PV's exclusive-compute-node writer (§3.4) with encrypted graded truths;
  - the director's wrapper, with ST4's consumption record, manifest verification before decrypt, and the synthetic-seal
    end-to-end test;
  - the ST3/ST6 reservation ledger;
  - ST1's reproducing-test harness for the named exception.
- **Each needs** unit tests, a line trace of every new line, hand mutants (all killed), a codex-school2 and an agy read (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`), the
  director's binding, and per-connect fences.
- **A0-type controls in every readout:**
  - the readout reproduces COV2D's committed mean χ² at G18 and AR23 from E_<T>.npz against C_T, to the κ-scaled
    tolerance max(1e-9, 10 κ₂ ε), with κ₂ on the actual non-null grading subspace and ε = float64 epsilon. The
    tolerance's origin is COV2D addendum A5; REGRADE-AMENDMENT-1 is its retained-subspace variant;
  - numpy against scipy `evr` mode agreement, as in T2A.

## 9. Open items, for the director, and for Joseph where marked

1. **KI 85: decided.** Joseph superseded both of KI 85's sentences for COVFIX (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`).
   - N5 is bound and runs unconditionally.
   - Outcome A may change the 2D covariance. Any change enters the journal paper or a later Zenodo version, not the
     first release. Adoption and wording remain Joseph's.
   - When N5 is bound, KI 85's row in `KNOWN_ISSUES.md` is updated to point to that decision. Until then the row is
     left unchanged.
2. **Size: decided.** Full, as designed (`DECISION-20261123-joseph-covfix-ki85-size-reader.md`, Joseph's governing re-confirmation): two sealed tunes, full P1 toy
   counts, and N5 always, at about 409 node-h at most (408.6–409.2). That is above half the balance, and Joseph
   approved it. Each phase is still capped from sacct, and ST6 holds the approved total. The second reader is
   codex-school2, alongside agy, by the same decision.
3. **Binding prerequisites:**
   - a committed iris receipt;
   - the fresh PG session named;
   - the director's passphrase generated, with the director's piping wrapper, and never shown to cov2d.
4. **The bars:**
   - the fluctuation affirmative and two-sided (F̃ and every band "covers");
   - the total affirmative (M + h ≤ 1.25);
   - no under-flag;
   - §6.2's sampled-covariance check at 0.05;
   - the residual rule at 0.1 on modes with λ ≥ 1e-6·λ₁.
   These are policy choices, open to challenge.
5. **Truth-dependent spread.** If A1p's band ratios differ strongly between truths, pooling makes V_F over-cover at some
   truths and under-cover at others. §5.3's two-sided fluctuation bar will then refuse K_B, and "none" follows. That is
   intended.
6. **The carry.** COVFIX tests the reported covariance carried in relative form, not remade at each truth. P0 measures
   the difference at G18 and AR23. If the director wants the remade object instead, that is 486 unfolds per truth (about
   92 node-h each), and it changes the price.
