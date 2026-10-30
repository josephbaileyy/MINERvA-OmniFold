# DECLARATION 1B with 4A, stage 1: the coverage protocol, fixed before any toy, and the stages that follow (2026-10-30)

**By** the measurement session `coverage-5b` (ListAgents), for the director to bind.

**Under** [`DECISION-20261030-joseph-fund-1b-with-4a.md`](../../../DECISION-20261030-joseph-fund-1b-with-4a.md)
(Joseph: "Fund it (Recommended)"): 1B runs with 4A as
[`LIMITATION-PLAN-ADDENDUM-20261028.md`](LIMITATION-PLAN-ADDENDUM-20261028.md) §1 and §4.2 scope them, "declared and
bound in stages; the nominal control must pass before the production toys run", about 44.5–145 CPU node-h, every job
under 12 h, CPU only. Item 3 of
[`DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md`](../../../DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md)
fixes which matrix 1B tests (§2 below).

**After:** the addendum's §1.1–§1.5 and §4.2–§4.3; the design it re-costs, `LIMITATION-PLAN.md:181-237`; F1's report
(`FD-F1-REPORT.md`); VL169's pre-registration, whose rule form this follows
(`docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md` §5–§6); the consult's recommendation
(`state/2d-closeout/stageF/methods/secondary-results/astra-consult-cheap-tier-20261030/answer.txt:17`).

**This stage declares:**
- the coverage protocol for every later stage: the covariance under test, the arms, the statistics, their standard
  errors, the windows and verdict rules, the positive controls, the stop rules and what a pass or fail means (§2–§5).
  None of it may change after a toy output exists;
- the stages, each with its own declaration and binding, priced from measured walls (§6–§7);
- stage 1's own work: the toy mode's code and tests, and the derivation of the expected spread, on a login node at
  **0 node-h** (§8).

**MEASURES:** nothing. No job ran. The cluster reads were `iris`, `ls` of the s5p lateral directories and `squeue`
(`fd/receipts-1b/stage1/cluster-reads.out`, login37, 2026-10-30T16:26:44Z). The arithmetic is
`fd/receipts-1b/stage1/arith.py`, output `arith.out`.

**CANNOT AUTHORIZE:** any job. Stage 2 and stage 3 each need their own declaration and the director's binding; stage
3 also needs the control's PASS (§5). Nor a change to the reported covariance, to κ, to any claim or printed wording.
The data have been read, so no 1B result changes an interval or a matrix (`LIMITATION-PLAN.md:235-237`).

## 1. What 1B asks, and what it cannot

- **The control arm** asks whether intervals built from the blocks the toys draw cover the nominal truth at the
  nominal rate. It is the machinery check: if it fails, no test arm is read.
- **The test arms** ask whether the **reported** 16-cell intervals undercover at two held-out GENIE v3 truths,
  G18_10a_02_11b and AR23_20i_00_000. Both are Joseph's choices (`FD-F1-DECLARATION.md:45`), and F1 measured their
  bias as at most |z| 0.644 (`FD-F1-REPORT.md:39`), so at these truths coverage turns on spread against width
  (addendum §1.1).
- **4A** asks whether the 16 × 16 drawn-block matrix describes the toys' scatter in all 16 dimensions, correlations
  included (addendum §4.2).
- **The scope is the nominal detector response** (the decision, item 2). C_resp is not drawn (§3).
- **It cannot speak to:** GiBUU-like or q3-tilt truths; another detector response; whether C_model, V_g or the flux
  model's correlations are right; Stage G's p values (4B is not funded:
  `DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md` item 1).

## 2. The covariance 1B tests

**The reported covariance as it stands on `main` at this declaration (`91a27ad1`):** C_total + C_resp =
C_e + C_model_abs + C_resp, the data product's matrix.
- File: `fd/data-product/fd_data_product.json`, sha256 `b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072`,
  schema `fd-data-product/1`; its matrix as `fd_data_product_C_total_plus_C_resp.csv`, sha256
  `20a4b9d8e41c2b53a65b20beebf7abcb2bf46d5fb4de2a30af1ca8e327361ad8`. Both re-hashed on this branch.
- Its inputs, as the product records them: S1's assembly npz `db000707…` and readout `81e5ef3f…`; C_resp's npz
  `4d8b5797…` and readout `19bb2ee1…`.
- **It holds no run-period block.** 5B's block is to be audited and then added (that decision's item 2). If it is
  added, every 1B report states that 1B tested the matrix above, not the revised one (item 3). 1B is not re-run for
  the revision unless a later decision says so.
- The per-cell interval of a test arm uses this matrix's diagonal. 4A at a test arm uses the drawn-block matrix
  (§4.2), as the addendum designs it.

**The control arm's matrix M_d** is the sum of the drawn blocks (§3), taken from the same S1 assembly npz
(`db000707…`, on pscratch and HPSS), never recomputed. Its blocks are the ones the S1 readout lists
(`s1/readout/s1_assembly.json`, `meta.blocks`).

**Transfer to a truth.** A matrix M on the data's f is applied at truth T in relative form, as VL169 did
(`PREREG-20261005-2d-fixed-truth-coverage.md` §5) and as F1 graded: M^T = diag(x_T / f) M diag(x_T / f), so
σ_c^T = (√M_cc / f_c) x_{T,c}. x_T is the truth's 16 cell integrals, built as F1's grade builds X_true.

## 3. The arms, and what each toy draws

| arm | truth | intervals scored | sided | toys | seeds |
|---|---|---|---|---:|---|
| control | nominal (MnvTune v1, the MC CV) | M_d, the drawn blocks only | two-sided | 300 | 2,610,000–2,610,299 |
| G18 | G18_10a_02_11b, F1's gated, k-normalised ratio | the reported C_total + C_resp | one-sided | 300 | 2,620,000–2,620,299 |
| AR23 | AR23_20i_00_000, the same | the reported C_total + C_resp | one-sided | 300 | 2,630,000–2,630,299 |

The seed ranges have no match in the repository's `.tsv`, `.py`, `.sh`, `.json` or `.md` files (`git grep -E
'\b26[0-3]0[0-9]{3}\b'` at `91a27ad1`, empty). The truths are F1's prep ratios, with the sha256 in the committed
`f1-prep-SHA256SUMS`.

**The estimator the toys represent: production (e) with all of the MC,** because the reported intervals are those of
the full-MC data unfold (`FD-PLAN.md:137-138`). The unfolding MC carries the MC Poisson(1) stream and the template
Poisson(1) stream of set A, the streams C_stat was built from (`S1-DECLARATION.md` §2 choice 6). The half-MC mode of
A7, F0 and F1 runs only as a paired correspondence measurement in stage 2a, described there, never scored. This
settles the addendum's half-MC question (§1.3) **for the director to confirm**.

**The draws,** proposed to mirror S1's block estimators. Stage 1's derivation (§8) tests each against its S1 block,
and stage 2's declaration fixes them:

| block (S1 trace share) | drawn how | why this form |
|---|---|---|
| stat (0.0010) | Poisson pseudo-data at data size, plus set A's MC and template streams | the streams C_stat was built from |
| flux (0.1881) | one of the 100 PPFX universes, with probability w_u / Σw from `sorted_NuEConstraint_FHC_RHC_IMD.txt`'s first 100 entries; the source's reco weights × (wr_u / w_reco) | S1's flux block is the constraint-weighted, weighted-mean-centred covariance of those universes (choice 10). Drawing u with probability w_u / Σw gives that covariance exactly, if S1 normalises by Σw; stage 1 checks this |
| interaction (0.1705) | each of the 32 paired bands at one endpoint with probability ½; 2p2h at one of its 3 universes; Rvp1pi not drawn; truth kept fixed in every fine cell (A7's g_f factor, `s5p_nullexp.py:15-24`) | a ½–½ endpoint draw has exactly the mean-centred ¼ΔΔᵀ of S1's pair estimator (choice 2), with no interpolation assumed; Rvp1pi follows S1 (choice 4) |
| detector (0.0525) | the 4 weight-only bands (MinosEfficiency and 3 GEANT) from the detector dump, at one endpoint each with probability ½ | S1's source and estimator (choice 7) |
| lateral (0.1406) | **a declared surrogate:** x̂ += Σ_b s_b Δ_b / 2, s_b = ±1 with probability ½, Δ_b the endpoint difference of S1's lateral unfolds (X01 applied) | **the 5D lateral dumps no longer exist.** `$P/s5p-20260926/lateral/` is empty, and only the 10 lateral unfolds remain (`cluster-reads.out`; S1-DECLARATION choice 11). Re-dumping would need new event loops. The surrogate carries the block exactly and tests nothing about it |
| normalization (0.0276) | x̂ × (1 + 0.014 z), z ~ N(0, 1) | S1's 1.4 % (`meta.normalization_fraction`) |
| seed (0.0000) | not drawn; estimator seed 42 | S1 measured the block as exactly zero (S1-REPORT §7) |
| C_model (0.4196 of C_total) | not drawn | a fixed-truth draw cannot produce it (`LIMITATION-PLAN.md:193-194`) |
| C_resp | not drawn | the decision's nominal-response scope |

**The consequence, by arithmetic on S1's trace shares:**
- stat, flux, interaction and detector are 0.4121 of C_total's trace, **71.0 % of C_e's**. The control tests their
  propagation through the estimator.
- The two surrogates are 29.0 % of C_e's trace. The control carries them but does not test them. Every report says so.
- **The alternative, for the director:** leave the laterals out of the toys and out of M_d. The control would then
  test the same 71 %, and the test arms would over-cover further. This declaration recommends the surrogate, so that
  the test arms' toys carry the lateral spread the reported intervals include.

**The first-order gap the derivation must size.** S1's interaction bands reweight the whole unfolding MC, prior
included. A fixed-truth toy moves only the response (FD-PLAN §3.4). If the prior part of a band is material, the
control's intervals hold spread the toys cannot produce, and the control over-covers in those cells by construction.
Stage 2a measures this before any coverage toy runs (gate D, §5).

## 4. The statistics, fixed now

### 4.1 Coverage, per cell and pooled

For toy t, cell c and k = 1, 2: z_tc = (x̂_tc − x_{T,c}) / σ_c^T.
- **The per-cell coverage statistic:** ĉ_c(k) = (1/N) Σ_t 1{|z_tc| ≤ k}.
- **Its standard error:** the binomial SE_c(k) = √(ĉ_c(k)(1 − ĉ_c(k)) / N), printed beside every ĉ_c(k) with its
  Wilson 95 % interval.
- **The study's sensitivity, fixed now:** at N = 300 and nominal coverage the per-cell SE is **0.0269** (k = 1) and
  **0.0120** (k = 2). In units of the ratio of interval to true scatter, one per-cell SE is 0.056. Pooled over 16
  cells, the SE lies between 0.0067 (cells independent) and 0.0269 (cells fully correlated) at k = 1
  (`arith.out`; `LIMITATION-PLAN.md:213-214`).
- **The pooled statistics:** C1 = mean of 1{|z| ≤ 1} and C2 = mean of 1{|z| ≤ 2} over all (toy, cell) pairs. Nominal
  values are 0.682689 and 0.954500.
- **Their intervals:** a toy bootstrap that resamples toys with replacement, never cells, so each toy keeps its 16
  cells. 20,000 resamples, generator seed 20261030, percentile intervals: 99.5 % at the interim look, 95 % at the
  final look.
- **The window** (the control only): the interval counts as nominal if its ratio to the true scatter lies in
  [0.9, 1.1]. Under Gaussian scatter that gives **C1 ∈ [0.631880, 0.728668] and C2 ∈ [0.928139, 0.972193]**,
  VL169's windows recomputed (`arith.out`).
- **Per-cell flags,** a reporting trigger, not a gate: cell c is flagged *measured undercoverage at k* if its Wilson
  99.5 % upper bound lies below nominal. At N = 300 that means ĉ_c(1) ≤ 182/300 = 0.6067 or ĉ_c(2) ≤ 276/300 = 0.9200.
- **Secondary, reported with no verdict role:** pull mean and RMS per cell and pooled; the per-cell median, minimum
  and maximum of ĉ.

### 4.2 4A: each toy's χ² against its truth

χ²_t = (x̂_t − x_T)ᵀ (M_d^T)⁻¹ (x̂_t − x_T), with no ridge or eigenvalue floor. The reader refuses if M_d^T is not
positive definite; C_e's condition number is about 2.0 × 10⁴ (addendum §4.2).
- **At the control** it is graded two-sided, against χ²₁₆ with the same scale tolerance [0.9, 1.1]:
  - the mean χ² must lie in **[13.223, 19.753]** (SE at N = 300: 0.33);
  - the fraction above 26.296, χ²₁₆'s 95th percentile, must lie in **[0.0106, 0.1673]** (SE 0.013);
  - with 95 % toy-bootstrap intervals and the same PASS / FAIL / INCONCLUSIVE rule as §5.1. A KS distance to χ²₁₆ is
    printed, with no verdict role.
- **At a test arm,** F1's measured bias enters χ² about the truth by construction. So:
  - the graded statistic is the mean-subtracted χ², about the arm's toy mean, × N/(N − 1), against the same windows;
  - χ² about the truth is printed under M_d^T and under the reported matrix, with no verdict. Under the reported
    matrix it is expected below χ²₁₆, because that matrix holds C_model (addendum §4.2).
- **What 4A gates:** nothing. A 4A failure while the control's coverage passes is reported as a failure in the
  correlations (addendum §4.3). It does not stop stage 3.

## 5. Verdicts, stops and what they mean

### 5.1 The control arm: two-sided, VL169's rule

- **PASS:** both the C1 and C2 intervals lie inside their windows.
- **FAIL-undercoverage or FAIL-overcoverage:** at least one interval lies wholly below (or above) its window, and none
  lies on the other side. **FAIL-mixed:** they lie on opposite sides. **INCONCLUSIVE:** anything else.
- **The positive control,** on the same toys with σ scaled × 0.7 and × 1.3: at × 0.7 both intervals must lie wholly
  below the × 1.0 point estimates, and at × 1.3 wholly above. A PASS also needs × 0.7 to grade FAIL-undercoverage and
  × 1.3 FAIL-overcoverage. If not, the PASS is void and reads INCONCLUSIVE (positive control failed).
- **Interim look at toys 1–100,** with 99.5 % intervals: any FAIL ends the arm, and that FAIL is the verdict.
- **INVALID:** if any two toys' stored truths differ, or any toy's stored draw record departs from its declared
  priors. INVALID is a stop.
- **Validity:** a toy is scored if and only if its step finished with rc 0 and a complete product. A failed step is
  rerun with the same seed. No toy is excluded for its values.

**The control is the gate.** Any verdict other than PASS (any FAIL, INCONCLUSIVE, INVALID, a voided PASS, or too few
toys) is a **STOP**. No production toy runs, the test arms are not declared, and the control is reported unrepaired.
On a FAIL the report says the machinery is ungraded and nothing about the reported intervals.

### 5.2 The test arms: one-sided against nominal

- **FAIL (measured undercoverage):** the pooled C1 or C2 interval lies wholly below nominal, 0.682689 or 0.954500.
  The report then gives the measured coverage as measured: pooled C1 and C2 with intervals, and every ĉ_c(k) with its
  SE. That replaces "not validated" at that truth (addendum §1.5).
- **PASS:** otherwise. Its meaning is fixed now: **"no undercoverage detected at the study's sensitivity"**, at that
  truth, under the nominal detector response. The sensitivity is stated beside it as the pooled interval's half-width
  and the per-cell SEs of §4.1. A pass is not a validation of coverage.
- **Flagged cells on a pass** are reported as *measured undercoverage at that cell* (§4.1), with their ĉ and SE.
- **The positive control** is × 0.7 only: it must grade FAIL, or the arm's PASS reads INCONCLUSIVE. A × 1.3 control
  cannot fail a one-sided rule (`LIMITATION-PLAN.md:210-211`).
- **The expected over-coverage,** printed per cell as context and never as the reference: at zero bias, if the spread
  is C_e, C1 averages 0.791 (minimum 0.701) and C2 0.983 (`LIMITATION-PLAN.md:198-200`). These follow from C_model
  being in the reported matrix and not in the toys. Their excess is not evidence that the intervals are adequate,
  since adding C_model widens the intervals without guaranteeing coverage (consult `answer.txt:23`).
- **Interim look at toys 1–100 of each arm,** with 99.5 % intervals: a FAIL ends that arm, and the FAIL is its
  verdict.
- **The two arms are never pooled** and are not two independent tests: they share their CCQE model
  (`FD-F1-REPORT.md:94-99`).

## 6. The stages

| stage | what | compute | gate to the next |
|---|---|---|---|
| **1** (this declaration) | the protocol (§2–§5); the toy mode, its scorer and tests; the derivation (§8) | 0 node-h, login node | the stage-2 declaration, with the code pinned, bound by the director |
| **2a** | derivation runs: one noise-free toy per S1 universe and the CV (176), at the nominal truth; a pilot of 16 full-MC toys (seeds 2,600,000–2,600,015); 8 half-MC toys at the pilot's first 8 seeds; 2 reproduction runs | job 2a | **gate D**, and the pilot's walls (below) |
| **2b** | control toys 1–100, then the interim look | job 2b | a FAIL is a STOP |
| **2c** | control toys 101–300, then the final look and 4A at the control | job 2c | **the control's verdict.** Anything but PASS is a STOP |
| **3** | the two test arms: toys 1–100 of each, the interim look, then 101–300 of each, the final look and 4A there | jobs 3i, 3f | none; stage 4 follows |
| **4** | the readout and the report | 0 node-h, login node | — |

**Gate D, fixed now** (stage 2a, login node, before any coverage toy). From the derivation runs, the reader builds each
drawn block with S1's own estimator for that block, from the toys' own shifts x̂(u) − x̂(CV). That gives E_d, the
toys' expected covariance (stat, lateral and normalization taken from M_d, as §3 sets them). Per cell,
ρ_c = √(E_d,cc / M_d,cc).
- **PASS** iff every ρ_c lies in [0.9, 1.1], the window the control is scored against. ρ_c and the per-block ratios are
  printed in all cases.
- **FAIL is a STOP** before any coverage toy runs: the control would be predicted to fail by construction. It is
  reported as a measurement of how far the fixed-truth mechanics reproduce S1's blocks, the first-order h = −d
  comparison that 3b made for C_resp.

**The reproduction runs:** the toy mode with every draw off, in half-MC mode, at two F1c lines (one per truth), must
reproduce F1c's products' `xsec_flat` bitwise. A mismatch is a STOP. **The half-MC toys** are paired with the pilot's
first 8 seeds and are printed as per-cell paired differences, with no verdict, to tie 1B's estimator to F0's and F1's.

**The pilot's walls re-price stages 2b–3.** If the pilot's median toy wall exceeds 1.25 × the 832 s assumed in §7, or
any lane's peak RSS exceeds 75 % of its 56 GB, the stage-2b binding is re-priced before it is submitted.

## 7. Price, from measured walls

**The toy unit** (`arith.out`, **(arithmetic)** on measured walls):
- (e)'s full-MC unfold took 648–657 s at 32 CPUs, 8 lanes per node: S1's production steps took 7,129–7,227 s for 11
  universes (`S1-REPORT.md` §3). S1's P1 charged 2.00889 node-h for 88 universes, 0.0228 each.
- A7's nuisance-drawn experiment took about 720 s against a `seconds_unfold` median of 545–641 s, so building the
  pseudo-data and applying the draws adds 79–175 s (`FD-PLAN.md` §5.1).
- So one toy is **727–832 s**, or **0.0253–0.0289 node-h** at 8 lanes per node. The addendum's 0.025
  (`LIMITATION-PLAN-ADDENDUM-20261028.md` §1.4) is at the low end. The full-MC pseudo-data build has not been timed,
  so it is an ESTIMATE until the pilot measures it.

**Jobs:** one exclusive CPU node per 8 lanes of 32 CPUs and 56 GB, `-A m3246 -q regular -C cpu --exclusive
--no-requeue`, through the committed packer as S1 and F1c ran. The projected wall is the most toys on any lane × 832 s.
The enforced cap is nodes × time limit.

| job | unfolds | nodes | most per lane | projected wall | projected node-h | limit | **enforced cap** |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2a | 202 | 3 | 9 | 2.08 h | 6.24 | 3.0 h | **9.00** |
| 2b | 100 | 2 | 7 | 1.62 h | 3.24 | 2.5 h | **5.00** |
| 2c | 200 | 3 | 9 | 2.08 h | 6.24 | 3.0 h | **9.00** |
| 3i | 200 | 3 | 9 | 2.08 h | 6.24 | 3.0 h | **9.00** |
| 3f | 400 | 5 | 10 | 2.31 h | 11.56 | 3.5 h | **17.50** |
| **all** | 1,102 | | | | **33.51** | | **49.50** |

- **Per stage:** stage 1, 0; stage 2 (2a–2c), projected 15.7 and capped at 23.0; stage 3, projected 17.8 and capped at
  26.5; stage 4, 0 **(arithmetic)**. Production, the 900 coverage toys, is 22.7–26.0 node-h projected at the unit
  above, against the addendum's 22.5.
- **Against the funded range of 44.5–145:** every enforced cap together is **49.50**, inside it. The projection, 33.5,
  falls below the range's low end. That low end carries the MP1-A-full analogue's 15–40 node-h of development and 7–70
  of verification (addendum §1.4, both ASSUMPTIONS). Here development is login-node work (§8), and the derivation's
  compute is job 2a, priced above. Nothing is padded to reach the low end.
- **Repair** is not pre-allocated. Any rerun beyond a failed step's same-seed rerun, or any repair, needs a declared
  amendment and the director's binding. Together with the caps above it stays under 145.
- **Every job is under 12 h** (the longest limit is 3.5 h). No GPU, no premium QOS. Products go to pscratch, with an
  HPSS copy at each stage's end; nothing goes to CFS. Storage is about 0.6 GB (1,102 products of about 0.53 MB,
  65,856 float64 each) **(arithmetic)**.
- **The balance:** `iris` at 2026-10-30T16:26:44Z shows m3246 at 17,915.0 of 20,000.0 charged, so 2,085.0 left and
  half of it 1,042.5 (`cluster-reads.out`; the director's half-of-remaining rule, addendum §7). No job of this lane was
  queued.

## 8. Stage 1's work (login node, 0 node-h)

1. **The toy mode,** in a new `nd-unfolding/fd_1b_toys.py`, built on `s5p_nullexp.py`'s draw and source-factor code
   and on `s5e_candidate.py`'s `ratio_nd` truth, imported, not copied:
   - full-MC unfolding with set A's MC and template streams; the draws of §3; the lateral and normalization
     surrogates;
   - a noise-free mode for the derivation runs, and the half-MC mode for the correspondence runs;
   - every draw recorded in the product, with refusals on a missing pin, a non-finite value, or a truth that differs
     from the declared one.
   `s5p_nullexp.py`, `s5e_candidate.py` and every module s5p's records depend on stay unchanged.
2. **The scorer,** `nd-unfolding/fd_1b_score.py`: §4 and §5 exactly, with the windows, the seed 20261030 and the
   flags as constants that a test holds against this declaration's numbers. It reads only products and the two
   matrices, and it prints no cross-section value.
3. **The gate-D reader,** in the scorer, computing E_d with S1's block estimators. It imports `s1_assemble`'s
   functions rather than reimplementing them.
4. **Tests:**
   - synthetic coverage fixtures that must PASS at scale 1.0 and FAIL at 0.7 and 1.3, in both directions (VL169's
     `test_coverage_fixed_truth.py` is the pattern);
   - a test that the ½–½ endpoint draw and the w_u / Σw flux draw reproduce S1's block estimators on fixtures;
   - the reproduction of F1c's argv with every draw off;
   - a mutation receipt over the toy mode, the scorer and the submit line.
5. **The derivation record:** for each block of §3, whether the toy's draw reproduces S1's estimator, by algebra or
   by test, and the prior-versus-response question that gate D measures.
6. **An independent read-only review** of the code and the stage-2 declaration, dispositioned in it.
7. **The stage-2 declaration:** the pinned code, tables and argv, the derivation record, and §6's jobs 2a–2c with
   their limits. No toy runs before its binding.

**Reads in stage 1:** the code, the committed records, and S1's assembly npz and lateral unfolds for the derivation.
No toy output exists, and no data result is read beyond the blocks already in the committed readouts.

## 9. Not changed

- The reported covariance, κ, every claim and number, and the data product. Nothing is submitted, deposited or
  tagged.
- F1's grade, 3a–5B's readouts and 4B's deferral.
- The paper's existing statement that coverage was not validated
  (`DECISION-20261024-joseph-5d-community-standard-route.md:46-47`) stands until a 1B report lands and Joseph rules on
  its wording. <!-- absence-ok: a reference to the decision record's own wording, quoted at its cited lines; it claims no search -->


## 10. For the director to rule

1. The toys' estimator: full MC as production, half MC only as a paired correspondence measurement (§3).
2. The laterals: the surrogate (recommended) or left out of toys and M_d (§3).
3. Gate D as the stop before any coverage toy (§6).
4. 4A gates nothing (§4.2).
5. The stage ceilings of §7, or others within 145.
