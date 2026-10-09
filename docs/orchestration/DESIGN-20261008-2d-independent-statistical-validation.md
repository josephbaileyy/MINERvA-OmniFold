# DESIGN 2026-10-08 — 2D repaired-bootstrap independent-population per-experiment interval validation

**DRAFT — NOT REGISTERED, NOT AUTHORIZED.** This is a preparation design (uncertainty preparation, lane B).
It registers nothing, authorizes no compute and admits no experiment. Every tolerance in it is
**proposed** and needs admission before execution. Nothing here lifts the `KNOWN_ISSUES.md` 85
deferral, establishes real-data or total coverage, admits a pilot, or spends a historical allocation.

**State: FINAL (lane-B FREEZE).** Provisional exchange with C at `f19084f4`; the estimator specification is
frozen against A's `[uncprep-A] CONTRACT` `acb338a2` and checked against A's FREEZE `9fab26e8`/`f762749d`;
reconciled once with C's `d07a3d33` (§14).

**CITABLE FOR:** the specification of the named experiment; the measured population inventory
([`populations.tsv`](state/uncertainty-preparation-20261008/b/populations.tsv)); the deterministic
assurance and cost arithmetic
([`assurance.py`](state/uncertainty-preparation-20261008/b/assurance.py),
[`assurance.json`](state/uncertainty-preparation-20261008/b/assurance.json)); and the disposition in §1.

**NOT CITABLE FOR:** any coverage result, any statement that the adopted `VL170` band is or is not
calibrated, any change to a quoted number, the total uncertainty (lane C), or authority to run anything.

## 0. Session setup and inputs

- **Decision answered.** Is a defensible, affordable next statistical-calibration experiment for the
  repaired 2D construction specifiable with independent populations and sufficient precision?
- **Owner / review** (`CAMPAIGN-REVIEW-20260929.md` §1). Owner: this session (lane B, Claude Opus 5.5).
  The single independent review and recomputation happen in E. No reviewer or worker agent was spawned.
- **Base.** `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c` on `prep/uncertainty-b-statval-20261008`. Remote
  `main` was not tracked (E reconciles).
- **Inputs read.** `PREREG-20261005-2d-fixed-truth-coverage.md` with Amendments 1–2;
  `OUTCOME-20261005-2d-fixed-truth-coverage-fail.md`; `KNOWN_ISSUES.md` 84–85;
  `DECISION-RULE-20261006-ki85-bootstrap-diagnostic.md` and `state/ki85-diag-20261006/`;
  `state/ki84-rebuild-20261006/` and `state/ki84-adopt-20261006/`;
  `2d-unfolding/uq/coverage_fixed_truth/{fixed_truth_toy,toy_design,score_coverage}.py`; the 2D status and
  reference; the production driver; the October 5 successor proposal (§5 criteria, which are **not**
  reused); C's assessment at `origin/prep/uncertainty-c-total-20261008` (`9204a390`, reconciled
  `d07a3d33`); A's assessment at `origin/prep/uncertainty-a-pairing-20261008` (`acb338a2`, `f762749d`).
  All historical toys and the KI-85 diagnostic are **development evidence**.
- **Measured for this design** (read-only, 2026-10-09 UTC, Perlmutter `login05`, no event loop): the
  production 2D omnifile's tree and branch lists and POT parameters (ROOT 6.28), three file digests
  (`sha256sum`), and the `m3246` balance (`iris`). Details are in `populations.tsv`.

## 1. Disposition (the full verdict is in §17)

**NO-GO** for the dispatched experiment. Ground 1 decides it; ground 2 is a supporting constraint:

1. **Production-equivalent independent populations do not exist.** The production statistical
   construction trains on the *entire* available signal MC (`mc_signal_reco`, 32,849,103 rows;
   MC/data exposure 4.708). An independent experiment needs a disjoint pseudo-data reservoir *and*
   an independent production-size training bank; the number of disjoint (production-size bank +
   data-size reservoir) sets the one MC production supports is **0**
   (`assurance.json` `max_disjoint_production_size_sets`).
   No second reconstruction-level ME-FHC MC production is held, and acquiring one is a MINERvA
   collaboration production that this project cannot price. In addition, the production omnifile
   carries **no event identity** on any tree, so even a held-out split needs an event-loop rebuild.
2. **Nested reconstruction is priced high (supporting constraint).** The coverage family needs
   N = 719 independent experiments (N = 1,116 to also give the bias test its power at the tolerance
   edge). With the measured 0.0591 node-h per production run, 719 × 301 runs cost **13,440 node-h**
   (1,116 experiments: 20,862 node-h). Against named comparators, that is **0.67–1.04 ×** `m3246`'s
   annual CPU allocation (20,000 node-h) and **4.4–6.9 ×** its CPU balance on 2026-10-09 (3,040.6
   node-h, all users, iris 06:15Z; a point-in-time balance of an allocation-year pool, not a ceiling —
   the same reading shows 55,107 GPU node-h remaining on `m3246_g`, and the plan defines no ceiling).
   The loosest scanned tolerance with I68 only (N = 172) is 3,215 node-h. These are at C's optimistic
   rate with a 5 % retry and no reserve; C's conservative per-experiment figure is 3.7× larger.

The narrower designs that remain specifiable are in §16. None of them validates the adopted
construction, and the cheapest informative one is the deferred `KNOWN_ISSUES.md` 85 held-out re-test.

## 2. The object under test (estimator specification)

**Frozen against A's `[uncprep-A] CONTRACT` (`acb338a2`, §2 of
`ASSESSMENT-20261008-2d-estimator-pairing.md`).** The object under test is A's estimator **`E_S`**,
the one that generates the adopted `VL170` band. It was measured from the producers, not from
document labels: the reference's bootstrap item 4 says *"`--bootstrap-seed N` and `--seed N`"*, and
the producers do not do that. A and this lane agree on every row below.

| Element | Value | Producer evidence |
|---|---|---|
| Driver | `2d-unfolding/unfold_2d_omnifold_unbinned.py`, blob `56c3b6c9` (identical at `bb4b0b6f` and at the base) | `git rev-parse` at both commits; A: pilot log prints HEAD `bb4b0b6f` |
| Backend and settings | LightGBM (`n_estimators 100, num_leaves 8, learning_rate 0.1`), `--iters 5 --use-weights`, `--bkg-mode purity`, `--bootstrap-streams both`, CPU | `state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh`; A §2.1 |
| Estimator randomness | fixed: `--seed 1` (step-1/step-2/regressor `random_state` 1/2/3) in every replica, not `--seed r` | same; A §2.1 |
| Thread count | the 300 replicas ran on the shared lane, 64 CPUs (`OMP_NUM_THREADS` = CPUs) | array `59410433`; PREREG A2.2 shows lgbm is not bit-identical across thread counts |
| Data stream | one `Poisson(1)` per data row in the phase space (4,091,707 rows) from `default_rng(r)`, multiplying the purity-weighted measured weights | driver 1606–1630; A §2.3 |
| MC stream | one `Poisson(1)` per `mc_signal_reco` row (32,849,103, including 8,999,007 misses) from `default_rng(r + 10_000_000)`, on `w_truth` and `w_reco` of the same row; `mc_truth_denom` and `mc_background` not resampled | same |
| Completeness | from the un-resampled MC truth weights (KI-84 fix): max \|c − 1\| = 1.6e-14 over 300 replicas | `KNOWN_ISSUES.md` 84; A §2.3 |
| Purity | per reco bin `max(0, (D − B)/D)`, computed once from the observed data, fixed across replicas | driver 1450–1501; A §2.3 |
| Covariance | sample covariance, `ddof = 1`, 300 replicas of `hXSec2D`, 205 bins in row-major `(p_T, p_∥)` order (the paper's GlobalID order restricted to the set) | `uq/analyze_uq.py`; A §2.2 |
| Normalization | data POT 1.0574e21, MC POT 4.9782e21, nucleons 3.2352943e30, flux integral 8.7407e-3 m⁻²/POT | A §2.2 |
| Central (in this design) | the unflagged `E_S` run on the same inputs (no `--bootstrap-seed`) | reference bootstrap item 5 |

**What the claim is about, and the admission items this creates.**

1. **The quoted central is not `E_S`.** A establishes that the quoted `3.073e-38` comes from `E_C`,
   the sklearn exact-split `GradientBoosting` backend with an unpinned `random_state`. `E_C` and
   `E_S` differ by a median 1.3 statistical σ per bin. This design therefore validates *the `E_S`
   interval-producing procedure with an `E_S` central*. It does **not** validate the uncertainty
   attached to the quoted central value. A's FREEZE records `P02` (`E_C` and the band are the same
   estimator) as **DISPROVED** and `P03` (the band applies to `E_C`) as **UNRESOLVED**: no exact-backend
   bootstrap exists (A prices 50 exact replicas at about 34–39 node-h packed). Covering `E_C` needs `P03`
   resolved or Joseph's decision to change the quoted central estimator. Using `E_C` as the
   per-experiment central instead costs one exact unfold per experiment (69,523 s single-threaded,
   MaxRSS 16.8 GB: about 0.7 node-h packed by memory, 19.3 node-h unpacked; A `f762749d` §5). C's
   REPAIR 1 (`57f6dd30` §6) prices its cheapest `E_C`-keeping route, the 4-case fixed-band P2, at
   5,728 node-h admitted if A's memory packing (0.68 node-h per exact unfold, contention unmeasured)
   holds, and 268,936 if the exact unfolds run as the central did, including a one-time exact rebuild
   of 292 / 8,298 node-h. `E_C`'s own seed
   variation has never been measured, so it could not be fixed estimator randomness.
2. **Purity is re-estimated per experiment, on purpose.** The procedure computes purity from the data
   it is given, so in the outer experiment it is computed from each pseudo-data set. The inner band
   holds it fixed (A §2.4 item 5). The outer scatter therefore contains a purity-fluctuation term that
   the band omits by construction (median purity 0.975, so expected to be small). That is part of what
   is tested, not a defect of the design.
3. **Thread count is part of the estimator.** Every run of every experiment is pinned to 64 threads.
4. **Helper origin.** The driver imports `omnifold.py` through its rooted `sys.path` insert inside
   `main()`, so the executed helper comes from the canonical cluster checkout, not from the launching
   tree (A §2.1; `fixed_truth_toy.py` is one of the new `OI-136` rooted-insert sites). The rooted
   import ruling (`AUTHORIZATION-20260903-oi136-failopen-repair.md` §2) is not changed here. Any future
   harness must record the helper's digest at run time and launch through
   `nd-unfolding/mnv_guarded_run.py`.

## 3. The stochastic experiment

**Notation.** `D` = data exposure (1.0574e21 POT). `M` = MC exposure (4.978e21 POT, `M = 4.708 D`).
Functionals `j = 1..206`: the 205 reported bins of `dσ/dp_T dp_∥` in the frozen order of
`populations.tsv` (row-major `(p_T, p_∥)` index, 19 empty cells excluded), and `j = 206`, the
area-weighted integral `F = Σ_b dσ_b Δp_T,b Δp_∥,b` over the same mask (cm²/nucleon). Levels
`q ∈ {I68, I95}` with multipliers `z_68 = 1` and `z_95 = 1.959963984540054` and nominal probabilities
**0.682689492** and **0.95** exactly. The 2σ interval (0.9545) is not used and is not interchangeable
with I95.

**Populations** (all disjoint by global event identity, §4):

- `S_e` — signal training/response bank (signal reco rows, truth-only misses, and the matching
  `mc_truth_denom` rows) of experiment `e`;
- `B_e` — background template (`mc_background`, which carries the signal fakes post Phase 18) used for
  the purity subtraction of experiment `e`;
- `R` — pseudo-data reservoir (signal and background events, with their reco and truth);
- `T` — fixed truth reference, computed once, before any draw.

**One outer experiment `e`.**

1. Pseudo-data: every reservoir event `i` (signal with `pass_reco`, and background with
   `sim_background_pass`, both inside the reco phase space) enters `k_i ~ Poisson(λ_i)` times,
   `λ_i = w_i · D / E_R`, `E_R` the reservoir exposure. Rows are **expanded** to one unit row per copy,
   so a pseudo-data set is a list of measured events exactly as the data tree is, and the production
   data bootstrap applies unchanged. (VL169 kept one row of weight `k`; for a weighted lgbm that is not
   the same input when leaf-size limits count rows.)
2. Purity from this experiment's pseudo-data histogram and `B_e`, by the production rule.
3. Central `U_e,j`: the unflagged driver run on (pseudo-data_e, `S_e`, `B_e`) with `--seed 1`.
4. Inner reconstruction: replicas `r = 1..300` with `bootstrap_seed = 20_261_008_200_000 + 1000 e + r`
   (both streams; MC stream at `+10_000_000`), `--seed 1`, purity fixed at step 2.
5. `σ̂_e,j` = sample sd (`ddof = 1`) of functional `j` over the 300 replicas (for `F`, the sd of each
   replica's integral, never a sum of bin variances).
6. Intervals `I_e,j,q = [U_e,j − z_q σ̂_e,j, U_e,j + z_q σ̂_e,j]`; hit `h_e,j,q = 1{T_j ∈ I_e,j,q}`.

**What is redrawn and what is conditioned on.**

| Element | Outer (per experiment) | Inner (per replica) | Conditioned on |
|---|---|---|---|
| Pseudo-data counts | `k_i ~ Poisson(λ_i)` on `R` | `Poisson(1)` per unit row, × purity | the reservoir `R` |
| Signal training bank | **an independent production-size `S_e`** (unavailable, §5) | `Poisson(1)` per event on `w_truth` and `w_reco` | — in the primary; `S` in N1 |
| Background template | independent `B_e` (unavailable) | not resampled (production) | template statistics: **conditioned out**, the claim excludes them (C owns any broader treatment) |
| Purity | recomputed from the experiment's pseudo-data | fixed at the central | the purity rule |
| Completeness | c from `S_e`'s un-resampled truth | same | — |
| Estimator randomness | `--seed 1`, 64 threads | `--seed 1`, 64 threads | the seed and thread count |
| Flux, target nucleons, `D`, bins | — | — | constants |
| Truth reference `T` | — | — | fixed before any draw |
| Generator (prior) | — | — | MINERvA Tune v1 = truth law: **prior equals truth**, no regularization bias under misspecification is tested |

**Why outer MC variability must be independent.** The inner MC stream is a Poisson(1) bootstrap of
the training bank. A design whose outer "MC variability" is the same bootstrap of the same bank
measures the bootstrap against itself (PREREG A1.3), so it cannot test the MC stream. The primary
therefore needs independently constructed banks `S_e`, or an explicit generative sampling law whose
validity is checked independently (§16, route G). With one fixed bank the test is conditional on it
and covers only the data stream (§16, N1/N2).

## 4. Event identity, grouping, split and contamination tests

**Measured identity state of the production 2D omnifile** (`runEventLoopOmniFold_MEFHC.root`, sha256
`43f8cc16…`, 2,144,008,221 B): `mc_truth_denom` has branches `MC, MC_pz, w_truth`;
`mc_signal_reco` has `sim, sim_pz, sim_pass, w_reco, MC, MC_pz, w_truth`; `mc_background` has
`sim_background, sim_background_pz, sim_background_pass, w_bkg`; `data` has
`measured, measured_pz, measured_pass`. **No tree carries an identity or a playlist branch.** The event
loop writes `mc_run, mc_subrun, mc_nthEvtInFile` only under `MNV101_DUMP_POINTCLOUD`
(`runEventLoopOmniFold.cpp` 460–474). Row order is not an identity, and different seeds, filenames
or row orders do not establish independent events.

**Required identity** (as in `nd-unfolding/pet/EVENT_IDENTITY_JOIN_CONTRACT.md`):
`(source, mc_run, mc_subrun, mc_nthEvtInFile, occurrence)` for MC, where `source` is the playlist,
recorded per row or derived from merge boundaries and verified against the playlist file, and
`occurrence` is 0 on clean MC (any MC duplicate is a stop condition, not a reason to use `occurrence`).
Real data are not a role here; their `(run, subrun, gate)` is not an event key (about 10.5 % of G2 data
rows repeat it).

**Rebuild prerequisite (R0).** Rebuild the 12-playlist 2D omnifile with identity branches, by the same
binary, inputs and environment, and prove it is the production file plus identity: every shared
branch of every tree equal row by row, bit for bit, to the production file, and the same POT
parameters. If equality fails, the rebuilt file is a new production and the design stops.

**Whole-event grouping and split.** An identity group is every row with the same identity across
`mc_signal_reco` (including truth-only misses), `mc_truth_denom` and `mc_background`. Each group is
assigned to a fold by `u = int(sha256(salt ‖ source ‖ run ‖ subrun ‖ nth)[:16], 16) / 2^64` against
fixed thresholds (development `[0, d)`, reservoir `[d, d + ρ)`, training `[d + ρ, 1)`). The salt is
written into the registration before the rebuilt file is opened. Bernoulli thinning with a known
probability gives each fold the unbiased exposure `fraction × M`, so no fold POT is estimated from
weights.

**Contamination tests** (each run with a negative control that must fire):

| Test | Requirement | Negative control |
|---|---|---|
| C1 | identity sets of the folds pairwise disjoint, per tree and across trees | move one reservoir key into the training list; C1 must fail |
| C2 | within each fold, `mc_signal_reco` and `mc_truth_denom` identity sets equal (the Phase-17 bijection, so c ≡ 1 per fold) | drop one truth-denominator row; C2 must fail |
| C3 | no identity in both the signal and the background tree | duplicate one key across the trees; C3 must fail |
| C4 | R0 row-by-row equality | perturb one value in a copy; C4 must fail |
| C5 | realized fold fractions of rows and of `Σ w_truth`, per playlist, within 5 binomial σ of the design | assign by a biased threshold; C5 must fail |
| C6 | the identity of every array handed to OmniFold in a development experiment, dumped as a sidecar, lies in the intended fold | feed one reservoir row to training; C6 must fail |
| C7 | no quantity is fitted on `R` except the pseudo-data draw (purity uses `B_e`; constants are constants; lgbm hyperparameters are production defaults) | code review against the frozen command line |

**Untestable here.** MINERvA simulation is described as overlaying data readouts for pile-up. This
repository holds no overlay identity, so dependence between folds through a shared overlay readout
cannot be tested. For muon kinematics it is expected to be small; it is unmeasured.

## 5. Exposure, effective sizes and support

| Quantity | Value | Source |
|---|---|---|
| Data exposure `D` | 1.057394e21 POT; 4,119,797 data rows before the phase-space mask | omnifile parameters and `data` tree |
| MC exposure `M` | 4.978198e21 POT = 4.708 `D` | omnifile parameter |
| Signal rows | 32,849,103, of which 8,999,007 truth-only misses | omnifile |
| Closure events (`pass_reco & pass_truth`) | 20,404,292; `Σ w_reco` (POT-scaled) 3,533,843 data-equivalent | VL169 manifest |
| Background rows | 658,227 | omnifile |
| Mean pseudo-data multiplicity on the closure events | 0.173 when the reservoir is the whole MC (VL169); `0.173/ρ` for a reservoir fraction ρ | ratio of the two rows above |

**Effective sample sizes are not measured.** Per bin, `ESS = (Σw)² / Σw²` over the training bank's
truth rows and over the reservoir's reco rows. They need a deterministic reduction on the rebuilt
file, which is not run here (no local copy; no login-node analysis). Proposed support rule, fixed
before any draw: a functional whose training-bank truth ESS or reservoir reco ESS is below 100 is
declared **unsupported** before validation and reported as outside the claim, never dropped
afterwards.

**What a split does to MC information.** A training bank of fraction `1 − ρ` carries MC-statistical
variance `1/(1 − ρ)` times production's. Doubling its weights restores the normalization, not the
information, so a half-sample bank tests a procedure at MC/data exposure 2.35, not 4.708. The frontier
(`assurance.json` `population_frontier`) has no production-equivalent point: for every ρ, either the
bank is smaller than production or the reservoir is small enough that the reference offset (§7)
dominates.

## 6. Backgrounds and signal fakes

The pseudo-data contain background events drawn from the reservoir's background fold, at the same
`λ_i` scaling as signal, and the signal fakes they carry (post Phase 18, fakes are in
`mc_background`; the VL169 toys had `n_fake = 0`). The subtraction uses the separate template `B_e`
under the production purity rule, recomputed from each experiment's pseudo-data histogram. VL169 had
no background in its pseudo-data (PREREG §3 (a)); this design does. The background template's own
statistics are not in the production recipe, so they stay conditioned out and the claim excludes
them.

## 7. Truth reference and finite-reference error

- **Primary.** The reference is the population truth `T_∞` of the generating law. With independent
  banks and a reservoir much larger than `D`, `T_R → T_∞`. Neither exists (§1).
- **Held-out conditional design (N1).** The only available reference is the reservoir's own truth
  `T_R` (its `mc_truth_denom` rows through `extract_cross_section_2d`, c = 1), fixed before any draw.
  It is a finite reference: `E[U | R, S] − T_R` contains the propagated detector-smearing realization
  of the reservoir's finite events, which is common to every outer experiment and does not average
  down. Its variance, in pull units, is at most `τ² ≈ (1/(ρ · 4.708)) · s · f_data`, with `s` the
  smearing share of the unfolded data variance and `f_data` the data-stream share of the band variance
  (0.52 from the KI-85 operands; median ratio, approximate).
- **Consequence, computed** (`assurance.json` `finite_reference_offset_N1`): at ρ = 0.5 and N = 719,
  an *exactly calibrated* procedure is expected to fail the coverage test in 11–103 of 206 functionals
  (`s` = 0.25–1) and the bias test in 108–154. **N1 fails as specified** — with `T_R` treated as an
  exact reference and the 0.2 σ bias test — with the MC that exists. Two variants are not ruled out
  and are **unpriced**: a *reference-aware* scorer that carries a per-functional model of `τ_ref` (which
  needs the unmeasured smearing share and ESS), and a *truth-free* scorer that compares the sd of
  `U_e − Ū` over experiments with `σ̂` (a width-calibration test with no coverage-of-truth claim, the
  per-experiment analogue of N2). VL169 avoided this only by making the reservoir the
  training bank (A1.3), which is the circularity KI-85 (b) names.

## 8. Reporting, intervals and failures inside an experiment

- Mask and order: `populations.tsv` "reporting mask" row; the integral uses the same mask.
- Intervals: §3 step 6, both levels, per functional.
- Empty or non-finite: if `U_e,j` or `σ̂_e,j` is non-finite, or `σ̂_e,j = 0`, the functional is a miss
  at both levels in that experiment and stays in the denominator. A reported functional with
  `T_j ≤ 0` makes the design invalid before any draw.
- Simultaneous coverage: the intervals are marginal. The per-experiment indicator "all 206 hit" is
  reported with its Clopper–Pearson interval and has no nominal target. The joint statistic
  `Q_e = r_eᵀ Ĉ_e⁻¹ r_e` (205 bins, `Ĉ_e` from the 300 replicas) is compared with its Hotelling
  reference `(B − p)/(p(B − 1)) Q ~ F(p, B − p)` (p = 205, B = 300) as a secondary with no verdict role.

## 9. Criteria (PROPOSED)

**Coverage tolerance.** A functional is calibrated within tolerance if the true sd of `U − T` over
experiments is between **0.80 and 1.25** times the replica-population σ (κ ∈ [0.80, 1.25]).

- *Motivation.* This is not the VL169 window (σ ratio 0.9–1.1) and not the successor's total-interval
  windows ([0.60, 0.80], [0.90, 0.99]). The question this experiment exists to settle is
  `KNOWN_ISSUES.md` 85: a data-stream σ ratio of about 1/1.6. The log-midpoint between calibration and
  that discrepancy is 1/√1.6 = 0.79. The tolerance is the widest log-symmetric band that still classes
  a KI-85-sized miscalibration as a failure.
- *Scale.* In the median bin the statistical block is 0.674 % of a 6.871 % budget. Within tolerance, a
  stat-σ error moves the median-bin total σ by −0.17 % to +0.27 % (`assurance.json`). The tolerance matters in statistics-dominated
  bins (high p_∥, the top p_T row), which is where VL169 failed.
- *Coverage edges* (exact; with σ̂ from 300 replicas): I68 [0.5757, 0.7877]; I95 [0.8821, 0.9851].
  At κ = 1 the 300-replica interval covers 0.68188 and 0.94907 (σ̂ noise), against nominal 0.682689
  and 0.95.

**Coverage test.** For each functional `j` and level `q`, `H_j,q = Σ_e h_e,j,q`. PASS iff
`a_q ≤ H_j,q ≤ b_q`. The family is 206 × 2 = 412 tests. The verdict is PASS if all 412 pass,
FAIL-undercoverage if some `H` lies below its region and none above, FAIL-overcoverage for the
reverse, FAIL-mixed if both. Pooled coverage (experiments resampled, never bins) is secondary.

**Accuracy (bias) test, separately sized.** Per functional, `m_j` = mean over experiments of
`(U_e,j − T_j)/σ̂_e,j`, with `t_j = m_j / (s_j/√N)`; FAIL iff `|t_j| > 4.0625` (familywise 0.01 over
206). Tolerance: a bias of **0.2 σ** must fail. Motivation: a 0.2 σ bias lowers I68 coverage to 0.673
and I95 to 0.945, under a tenth of the distance to the coverage edges, so a bias inside tolerance
cannot move a functional to a coverage edge by itself.

**Error allocation.** Familywise false-fail probability 0.05 under exact calibration: 0.04 to coverage
(two-sided 9.709e-5 per test, Bonferroni) and 0.01 to bias. Bonferroni is valid under any dependence
between functionals within an experiment; **the experiment, not the bin, is the sampling unit**, and
experiments are independent by construction. Power: at most 0.10 probability of passing a functional
whose true κ is at a tolerance edge.

## 10. Assurance arithmetic (`assurance.py`, deterministic, standard library)

| Quantity | Value |
|---|---|
| Experiments for the coverage family (stable for N..N+100) | **719** |
| Acceptance hits at 719 | I68 **[441, 539]**; I95 **[658, 703]** |
| Pass probability at an edge, one functional (N = 719) | I68 0.022 (κ = 1.25) / 0.008 (κ = 0.8); I95 0.0025 / 0.075 |
| Familywise pass, all functionals exactly nominal (union bound) | ≥ 0.969 (≥ 0.968 with 300-replica σ̂ noise) |
| Bias test: N for power 0.9 at 0.2 σ | 714 at κ = 1; **1,116** at κ = 1.25 |
| Bias power at N = 719 | 0.90 at κ = 1; 0.59 at κ = 1.25 |
| **Design N** = max(coverage, bias at the edge) | **1,116**; acceptance I68 [700, 822], I95 [1030, 1086]; familywise ≥ 0.967 |
| Mean-pull standard error at N = 719 | 0.037 |
| N sensitivity, κ ∈ [1/x, x] exactly (I68+I95 / I68 only) | x = 1.15: 1,632 / 1,248; 1.20: 1,030 / 755; 1.25: 719 / 519; 4/3: 504 / 322; 1.5: 329 / 172 |

The operating characteristic (pass probability of one functional against its true κ) is in
`assurance.json` `oc_curve_at_N_required`: above 0.99 for κ in [0.95, 1.05]; at κ = 0.9 and 1.1 it is
0.84–0.92. Self-test: `python3 assurance.py --self-test` runs 44 deterministic edge cases
(Student-t identities at 10 and 299 degrees of freedom, binomial boundary cases, the 2σ-versus-95 %
distinction, the offset-average identity, seed-namespace disjointness with its negative control, and
the experiment-index range).
E reproduces the consequential numbers independently from the raw operands at the top of the file.

## 11. Looks, stopping and failures

- **One fixed final look.** No interim look, no early stop, no extension and no criterion change after
  any validation output exists.
- **Infrastructure failures** (node failure, timeout, preemption): rerun with identical seeds and
  inputs, at most 3 times, outputs published atomically through the resume guard. **Numerical failures**
  (a deterministic error or non-finite output): one identical-seed rerun to exclude a transient, then
  the affected functionals count as misses.
- **Missing data.** At most 1 % of experiments (11 of 1,116) may remain missing after the retry limit.
  The verdict is computed with every missing experiment imputed all-hit and all-miss; it stands only if
  both agree, otherwise INCONCLUSIVE. More than 1 % missing is INCONCLUSIVE. No replacement experiment
  is drawn with a new seed.
- **Incomplete manifest** (missing seed, digest or identity sidecar): the experiment is missing.
- Scientifically failing experiments are never removed from the denominator.

## 12. Custody, seeds, pins and release conditions

- **Development/validation separation.** A development fold (`d` = 2 % of MC by the §4 hash) serves
  every pilot, timing and equivalence run. The reservoir is not opened until release.
- **Seeds** (`assurance.py` `seed_ranges`; collisions: none, with a negative control): outer pseudo-data
  `20_261_008_000_000 + e`; inner `20_261_008_200_000 + 1000 e + r` and its `+10_000_000` MC stream;
  `e ≤ 1,999`, `r ≤ 999`. These meet neither production (1–300; 10,000,001–300), the old toys, VL169
  (`20_261_005_…`) nor the KI-85 diagnostic (`20_261_006_…`).
- **Custody.** Validation outputs go to a path the scorer reads only after the full manifest exists and
  the scorer's code and digest are committed. No validation output informs any recipe choice.
- **Release conditions.** Joseph's admission (which for N2 also lifts the KI-85 deferral); A's frozen
  estimator identity at a commit; a driver at or after A's behavior fix `971fc00c`, so that every
  output records its effective `runConfig`, argv, driver sha256 and the sha256 of the OmniFold helper
  actually imported (A §4; the fix changes no histogram, weight or estimator); the helper digest
  (`e96234124a31…` at A's check; the rooted import stays inside `main()`,
  `AUTHORIZATION-20260903-oi136-failopen-repair.md` §2); the lgbm build, environment and thread count;
  the rebuilt omnifile and split-manifest digests; a named reviewer. The two `OI-136` ratchet suites are
  red at the base on nine unlisted October 2D sites, one of them the coverage toy producer (A raised
  this to E); a harness built on that producer inherits the finding.

## 13. Command templates, output schema and scorer (not built, not run)

```
# R0  identity-carrying rebuild (event loop; to be priced before admission)
MNV101_DUMP_POINTCLOUD=1 <production event-loop launcher, 12 playlists>  ->  merged omnifile ID
python3 check_identity_rebuild.py --production runEventLoopOmniFold_MEFHC.root --rebuilt ID     # C4
# R1  split manifest (hash folds; no RNG)
python3 make_split_manifest.py --omnifile ID --salt <registered> --dev 0.02 --rho <rho> --out split.npz
python3 check_split.py --omnifile ID --split split.npz                                          # C1-C3, C5
# R2  one experiment e (64 threads; central, then replicas 1..300)
python3 indep_pop_experiment.py --omnifile ID --split split.npz --experiment e --central --seed 1 --out exp_e/central.root
python3 indep_pop_experiment.py --omnifile ID --split split.npz --experiment e --replica r --seed 1 --out exp_e/rep_r.root
# R3  scoring after the full manifest exists
python3 score_indep_pop.py --manifest validation_manifest.json --mask populations.tsv --out score.json
```

Per-experiment output (`exp_e/summary.npz`): `U[206]`, `sigma_hat[206]`, replica functionals
`[300, 206]`, `T[206]` (identical in every experiment), seeds, input and code digests, thread count,
wall time and billing; plus an identity sidecar for development experiments (C6).

```
score(manifest):
    E = experiments listed in the manifest            # never filtered by values
    for e in E: require digests, seeds, T == T_frozen  # else e is missing (§11)
    for j in 1..206, q in {I68, I95}:
        H[j,q] = sum over e of 1{finite(U,σ̂) and σ̂>0 and |U[e,j]-T[j]| <= z_q σ̂[e,j]}
        pass[j,q] = a_q <= H[j,q] <= b_q              # a, b from assurance.json at N_design
    for j: t[j] = mean(z[:,j]) / (sd(z[:,j]) / sqrt(N)); bias_fail[j] = |t[j]| > 4.0625
    verdict = classify(pass, H); repeat with missing imputed all-hit and all-miss (§11)
    secondary: pooled coverage with experiment bootstrap, per-functional Clopper-Pearson,
               all-206 indicator, Hotelling Q_e
```

## 14. Cost

Per-run charges are measured from committed `sacct` receipts (C's table agrees): 0.0591 node-h per
production replica on the shared lane (300 tasks, `59410433`); 0.0708 per KI-85 run; 0.216 per
regular full-node replica. Every figure below adds a 5 % retry allowance and excludes R0.

| Option | Experiments | Runs | node-h | × remaining `m3246` |
|---|---:|---:|---:|---:|
| P, primary, B = 300 | 719 | 216,419 | 13,440 | 4.42 |
| P at design N (coverage + bias at edge) | 1,116 | 335,916 | 20,862 | 6.86 |
| P-floor: κ ∈ [2/3, 1.5], I68 only | 172 | 51,772 | 3,215 | 1.06 |
| P-B50 (a separate procedure) | 719 | 36,669 | 2,277 | 0.75 |
| N1, half-MC bank, B = 300 (extrapolated) | 719 | 216,419 | 6,720 | 2.21 |
| N1-B50 (extrapolated; separate procedure) | 719 | 36,669 | 1,139 | 0.37 |
| S, fixed-band transfer secondary | 719 | 719 | 45 | 0.015 |
| N2, held-out data-stream variance calibration | — | 100 | 7.4 | 0.002 |

- `m3246` remaining: 20,000.0 − 16,959.4 = **3,040.6 node-h** for all users (iris, 2026-10-09T06:15:10Z).
  It is a point-in-time balance of an allocation-year CPU pool, not a ceiling and not a grant; the
  annual allocation is 20,000 node-h (the primary is 0.67–1.04 × that), and the same iris reading shows
  55,107 GPU node-h remaining on `m3246_g`. The plan defines no ceiling for this experiment.
- C's provisional per-experiment figures (`9204a390` §9): reconstructed 1 + 300 = 17.8 (optimistic) to
  65.1 (conservative) node-h; mine is 18.7 with the retry allowance. At C's conservative rate the
  primary at N = 719 is about 46,800 node-h.
- Half-MC per-run cost is **extrapolated** (linear in training rows), not measured.
- Storage: 0.06 MB per output (C's measurement), so 216,419 runs need about 13 GB.
- **R0, priced by C** (`d07a3d33`, setup item S-r, billing ASSUMED): a CV-only identity-carrying
  rebuild is 0.4–2.3 node-h; with universe columns 2.8–27.0. It is needed once by every
  independent-population option and does not change the verdict.
- **Reconciliation with C (one, after A's FREEZE).** C reproduces this design's 719 / 1,116 at 206
  functionals and the primary's 13,440 node-h (`costs.json` `cross_check_B_primary`, 13,440.6). C's
  own counts size the same criteria for a 4-case total-uncertainty family (824 functionals: N 823,
  design N 1,250 per case); that family is C's, not this statistical-only design's. The differences
  C's FREEZE (`803f1dcc` §9) lists, exposed rather than merged: (1) retry and reserve — this design adds
  a 5 % retry and no reserve, C adds 2–10 % retry, 5–10 % verification and a 20 % protected reserve, so
  these figures are lower bounds on C's admitted totals; (2) rate — this design prices at the
  optimistic measured rate only; (3) family size — one case (206 functionals) here, four in C;
  (4) R0 — priced by C, verdict-neutral for both.

## 15. Secondary: fixed-band transfer (comparison only)

The historical design transfers the existing band (`r_b = σ_b / mean_b` from the VL170 rollup) to
each experiment and runs one unfold per experiment. It costs about 45 node-h at N = 719, but it tests
the transport of one band's relative widths, not the interval-producing procedure, and it never
validates the adopted band's bytes. With the populations that exist it is either the VL169 design
(circular in the MC stream) or a held-out version with the §7 reference offset. It is recorded as a
cost comparison and is **not** a substitute for the primary.

## 16. Narrower designs that remain specifiable

| Route | Claim it could support | Status |
|---|---|---|
| **N1** held-out conditional per-experiment intervals (fixed bank `S`, reservoir `R`, reference `T_R`; inner bootstrap **both streams**, the production procedure, since a data-only inner stream would be a different procedure) | conditional on `S` and `R`, at MC/data 2.35 | **Fails as specified** (`T_R` treated as exact, with the 0.2 σ bias test; §7); also 6,720 node-h. The reference-aware and truth-free variants (§7) are unpriced |
| **N2** held-out data-stream variance calibration: arm T, 50 pseudo-data sets from `R` unfolded with a fixed half-MC `S` and the MC stream held; arm B, 50 data-only bootstrap replicas of one of them; per-bin `σ_B/σ_T` and its median, as in the KI-85 rule | whether the production data bootstrap is faithful when the pseudo-data do **not** sit on the training events: the KI-85 (a)/(b) question with held-out MC | Specified (§16.1) at 7.8–9.7 node-h including R0; it **is** the deferred KI-85 held-out re-test, so it needs Joseph to lift the deferral; it validates no interval, no MC stream and no truth coverage |
| **G** surrogate world: truth from an independent generator run and reco from a smearing/efficiency law in `(p_T, p_∥)`, fit on the development fold and validated against the reservoir, so that both banks and pseudo-data can be redrawn | calibration of the procedure in the surrogate world, transferred to the real MC only as far as the surrogate's validity check reaches | NOT READY: the law, its validity criterion and the truth generation are undeveloped and unpriced; the nested cost (§14, P) still applies |

### 16.1 N2 specification (PROPOSED; it needs Joseph to lift the KI-85 deferral)

- **Populations.** The §4 folds after R0: development 2 %, reservoir ρ = 0.5, training bank the
  remaining 48 % (MC/data 2.26). Pseudo-data from the reservoir, with background, as in §3 step 1.
- **Arm T.** 50 pseudo-data sets (outer seeds `20_261_008_000_000 + e`, `e = 1..50`), each unfolded
  once with the fixed bank, central only. `σ_T,b` = sd (`ddof = 1`) over the 50.
- **Arm B.** 50 data-only bootstrap replicas (`--bootstrap-streams data`, inner seeds of `e = 1`) of
  arm T's first pseudo-data set. `σ_B,b` = sd over the 50.
- **Statistic.** `ρ_b = σ_B,b / σ_T,b` over the 205 bins; median `M` with a 95 % interval from 2,000
  resamples of replicas within each arm (the KI-85 construction). No truth is used, so §7 does not
  apply.
- **Rule.** Faithful if the interval of `M` lies inside [0.80, 1.25] (the §9 tolerance); over-scatter
  if it lies entirely above 1.25; under-scatter if entirely below 0.80; otherwise INCONCLUSIVE.
  Per-bin `ρ_b` and the comparison with the same-event KI-85 result (`M₁` 1.003, [0.955, 1.073]) are
  descriptive.
- **Precision.** The KI-85 diagnostic resolved its median to about ±6 % with these arm sizes
  (development evidence), well inside the tolerance.
- **What it answers.** Whether the production data bootstrap is faithful when the pseudo-data do not
  sit on the training events. It is conditional on one bank and one base pseudo-data set, it does not
  test the MC stream, and it is not a coverage test.
- **Cost.** 100 runs, 7.4 node-h at the measured KI-85 rate (full MC; a 48 % bank should be cheaper),
  plus R0 (0.4–2.3 node-h, C): 7.8–9.7 node-h, or **9.8–12.2 node-h with a 20 % protected reserve**
  (`assurance.json` `n2_total_with_r0_node_h_range`, `n2_total_with_r0_and_reserve_node_h_range`).
  Pre-execution items: the per-bin ESS reduction on the rebuilt file and the C1–C7 tests.

## 17. Verdict

**NO-GO** for "2D repaired-bootstrap independent-population per-experiment interval validation" with
the populations and resources that exist:

- *Population independence* — production-equivalent independent populations are unavailable (§1, §5);
  the production omnifile has no event identity (§4).
- *Feasibility (supporting)* — nested reconstruction at the required N is priced at 13,440–20,862
  node-h: 0.67–1.04 × `m3246`'s annual CPU allocation and 4.4–6.9 × its 2026-10-09 balance (§14).
- *Held-out conditional alternative* — N1 fails as specified against its only available reference
  (§7); its reference-aware and truth-free variants are unpriced.
- *Claim reach* — even a PASS would validate A's `E_S` procedure, not the uncertainty of the quoted
  `E_C` central value, until A's pairing `P03` is resolved or Joseph changes the quoted estimator (§2).

What would change it: (1) an identity-carrying rebuild (R0); **and** (2) either a second
production-size MC production or a validated generative law (G); **and** (3) about 13,000–21,000
node-h, or a validated cheaper inner procedure (e.g. B = 50, a separate procedure, 2,277 node-h).

**Next decision (Joseph) and its cost.** N2 is defined on `E_S`, so it presupposes a stage-0 scope
choice among A's options (`f762749d` "Next decision"): (a) validate `E_S` only, stated as explicitly not
covering the quoted central value; (b) resolve `P03` with exact-backend replicas; (c) change the quoted
central to the LightGBM family. N2 fits (a) as a test of `E_S` alone; under (c) its `E_S` scope would
also be the quoted central's; under (b) it reaches `E_C` only through a resolved `P03`. E composes the
single next decision: the scope choice first, then — only if it makes `E_S` the target — whether to
lift the KI-85 deferral for N2, the narrow held-out data-stream question, at about 9.8–12.2 node-h
including R0 and a 20 % reserve (7.8–9.7 without the reserve). N2 validates no interval, not the
adopted construction, not `E_C`'s uncertainty and not real-data calibration. It is specified to
admission level (§16.1) but not admitted. Otherwise nothing further is ready to admit.

**Cannot authorize.** Any compute, a pilot, a lift of the KI-85 deferral, a statement about the
coverage or calibration of VL170 or of real data, a change to the band, the estimator, the
uncertainty model or the publication scope.

## 18. Limitations

- ESS per bin and the smearing share `s` are not measured, and R0's price is C's with billing assumed;
  each is named where it is used.
- `f_data` = 0.52 is a ratio of medians from development evidence and only sizes the §7 offset.
- Bonferroni is conservative under positive dependence; the stated N is an upper bound for the
  requirement as written.
- The coverage edges assume Gaussian `U − T`; non-Gaussian tails change the exact coverages, not the
  binomial arithmetic.
- Prior equals truth everywhere; misspecified-truth coverage is outside this design (C's domain).

## For E

- C's `d07a3d33` cites the `E_S`→`E_C` transfer as `P02`; A's FREEZE numbers it `P03` (`P02` is the
  DISPROVED same-estimator row). The substance agrees; the label differs.
- A's two red `OI-136` ratchet suites (A's "For E" item 1) bind any harness built on
  `fixed_truth_toy.py`.
- If E wants the `populations.tsv` digests as verified receipt bindings, that is E's call; they are
  recorded as TSV on purpose.

## Session record (lane B)

- **Model and effort.** Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code; effort level not exposed to
  the session. Session id `c84d0399-39b1-4d30-a196-4ba43821f816`. Owner only; no reviewer or worker agent.
- **Commits.** Base `f8e2bf85`; PROVISIONAL `f19084f4`; contract freeze `ea6a154e`; this FREEZE is the
  commit that carries this section, on `prep/uncertainty-b-statval-20261008`.
- **Commands** (exit 0 unless stated): `python3 assurance.py --self-test` (44 checks);
  `python3 assurance.py --write assurance.json` (about 10 s); `python3 xcheck_scipy.py` (scipy 1.15.2,
  numpy 1.26.4; reproduces N, acceptance regions, bias N and the reference-offset failures); the first
  `--self-test` failed on a Student-t case with 1 degree of freedom, which exposed an inaccurate
  quadrature there; it is now refused below 3 degrees of freedom and tested. Pre-commit: 13 checks
  passed on each commit; the first PROVISIONAL attempt was refused for a bare-filename citation in
  `assurance.json`, fixed by full repo paths. Remote reads: `remote-reads-20261009.txt`. No test was
  skipped; no test that trains or reads validation samples exists in or was run by this lane.
- **Environment.** macOS, Python 3.12.2 (miniconda), `TMPDIR=/private/tmp/minerva-uncprep-b-20261008/tmp`,
  four-thread caps; Perlmutter `login05` via `ssh saul.nersc.gov` for the metadata reads (ROOT 6.28).
- **Resources against B's budget row** (6 h, 2 core-h, 4 GiB, 0.5 GiB): about 0.9 h active
  (06:09Z–07:02Z); under 0.05 local core-h; peak RAM under 0.3 GiB; new output under 0.2 MiB plus a
  0.4 GiB checkout; zero cluster node-hours, zero GPU-hours, no training, no toys. Login-node use: one
  ROOT key listing, three `sha256sum` reads (2.1 GB total) and one `iris` query.
- **Repair 1 (E-requested, cycle 1 of 2).** Wording repairs for E's review findings F1, F2, F3, F5, F6
  and F7: the `E_C` cost now cites C's FREEZE; the `m3246` balance is a named comparator, not a
  ceiling, and cost is a supporting constraint; N2's scope premise is named; C's listed differences
  are carried; N1 is "fails as specified", with its variants and inner stream named; the sensitivity
  scan uses exact reciprocals (1,632 and 1,030; x = 4/3 I68-only 330 → 322). No verdict change and
  no compute.
- **Additional operand fixtures under `P/b/`:** `remote-reads-20261009.txt`, `xcheck_scipy.py`,
  `xcheck_scipy_output.txt`.

