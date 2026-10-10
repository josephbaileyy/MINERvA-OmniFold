# 2D publication path after keep-and-disclose: route design and the next experiment

**CITABLE FOR:** the declared 2D measurement and claim family (§2); the read-only and synthetic
measurements in §3 (each with its operand file); the route comparison, uncertainty treatment,
population audit, proposed criteria, assurance and prices (§4–§9, all from `design_arith.json`); the
preregistration-ready specification of the next experiment XR (§10); and the proposed register
changes for the integration owner (§11).
**NOT CITABLE FOR:** any cross section, uncertainty, coverage or calibration result; an adoption, a
re-quote, a band replacement or a changed gate; a transfer between estimators; compute authority.
Every tolerance below is a **proposal**. The §3.6 pair-band figures are post hoc and descriptive.
Publication readiness is **not achieved** by this design.

| field | content |
|---|---|
| `Lane` | `two-d-path` (next session registered by the integration of the next-preparation batch, §7 of its report) |
| `Decision` | Which complete 2D procedure has a defensible, affordable route to a reproducible central estimator, matched total uncertainties and validation supporting explicitly declared publication claims? What single next experiment would distinguish the leading options or retire an infeasible route? |
| `Branch` / `Base` / `Head` | `prep/two-d-publication-path-20261009` / `a16d578646936a0cc6eca41e3e0350e756ee0dca` (`origin/main` at 2026-10-10T04:30Z, the merged integration PR #68) / the commit carrying this revision; reviewed commits in §12 |
| `Owned files` | `docs/orchestration/state/next-preparation-20261009/two-d-path/` only: this report; `design_arith.py`, `design_arith.json`; `seed_mechanism_check.py`; `remote_reduce.py`, `remote_reduce_pn.py`, `remote_reduce_pairs.py`; `operands/` (four JSON files); `logs/`; `review/` (reviewer output) |
| `Pinned inputs` | §1 table |
| `Resources` | §14. Cluster jobs, GPU, training on production data, toys, event loops: **0**. Read-only login-node reductions: ≈ 5.6 CPU-min |
| `Review` | §12 |
| `Model / effort` | owner Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §15: **PASS** (route L42 is a complete design for the claims declared in §2); **INCONCLUSIVE** for the exact-central route X (its decisive inputs are unmeasured; on current forecasts it costs 13–90× more); **NO-GO** for an empirical total-interval coverage claim with the existing populations; **PASS** for the next-experiment specification XR |
| `Next action` | §16: Joseph decides whether to authorize XR (≤ 3.0 CPU node-h, 0 GPU, ≈ 20 h wall) and whether the §2 claim scope is acceptable |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = this directory.

## 0. Setup

- **Roles.** One owner (this session). One fresh read-only reviewer at a fixed commit: one initial review
  and one focused re-review after a single repair batch (§12). No other agent, no peer message.
- **Terminal outcomes.** PASS: a complete route and a named next experiment are ready for Joseph's
  decision. FAIL: the evaluated route cannot meet its declared requirements. INCONCLUSIVE: a named
  input or method prevents a decision.
- **Budget.** 8 active hours, 3 local CPU core-hours, two threads per command, 8 GiB RAM, 2 GiB new
  scratch, 10 MiB tracked. No scientific production.
- **Authority.** The prohibitions of Joseph's 2026-10-09 ruling stand (closeout REPORT §11): no re-quote,
  transfer measurement, N2, KI-85 lift, changed gate or reopened campaign. A changed central estimator
  is reserved to him.

## 1. Baseline and inputs

- `origin/main` = `a16d5786` (PR #68). The six lane heads (publication `78837efe`, guard `63257cd4`,
  structure `0f4a059f`, speed `318d3e45`, gbdt `d6652270`, pet `d9a460c6`) are ancestors of it, and each
  lane `REPORT.md` is blob-identical between its head and `a16d5786`. Integration is therefore verified
  for this design; the base is the integrated main, not `5ac9706a`.
- Records read (blob at `a16d5786`): A pairing `05356fbf`; B design `fc2a5d9a`; C feasibility `921bb325`;
  DELIVERY `554f391c`; successor proposal `25c53d4c`; closeout REPORT `bd7ce9a7` (§11 ruling);
  integration REPORT `88cd3d5a`; speed REPORT `56d0bfb7` and `results/costs.json` `63aaff60`; 2D STATUS
  `547b2530`; REFERENCE `b7251698`; `KNOWN_ISSUES.md` `5e377f0f` (rows 84, 85, 88–91); campaign review;
  `docs/CURRENT_WORK.md`; DISPATCH.
- Products read on Perlmutter (sha256, measured 2026-10-10): `E_C` `142a45b0…`; seed-42 CV `4f5a1b6d…`;
  seedscan seed 1 `d7fe901f…` (seeds 2–10 in `operands/remote_reduce.json`); `VL170` `71a75821…`;
  `C_ML` `3b6b48ec…`; universe covariance `62590df7…`; July CV `purity_newomni/…_pn_uni_CV.root`
  (digest in `operands/remote_reduce_pn.json`); both omnifiles (CV file `43f8cc16…`, B's digest).

## 2. The declared measurement and claim family (item 1)

| element | declaration |
|---|---|
| measurand | flux-averaged ν_μ CC-inclusive d²σ/dp_T dp_∥ per nucleon, ME FHC, θ_μ < 20°, in cm² (GeV/c)⁻² nucleon⁻¹ |
| reporting map | all 205 reported cells of the paper's 14 × 16 grid (`2D_OMNIFOLD_STUDY_STATUS.md` "Paper binning"), row-major paper `GlobalID` order, cell identity from `uq/reported_cells.py`; plus the area-weighted integral over those cells; plus the 14 p_T and 16 p_∥ projections. No coarsening, no dropped cell |
| normalization | absolute: data POT 1.0574e21, MC POT 4.9782e21, N_nucleons 3.2352943e30, flux integral 8.7407e-3 m⁻²/POT with the per-p_T `hFlux_pt` (A §2.2) |
| estimator `E_L42` | the driver at a commit ≥ `355174fe` (records `runConfig`, driver and helper digests), helper `omnifold.py` `e96234124a31…`, `--estimator lgbm --seed 42 --iters 5 --use-weights`, `--bkg-mode purity`, `root_6_28` (LightGBM 4.6.0, numpy 1.26.4), CV-level arrays of either omnifile (row-identical, §3.1), 64 or 128 threads (§3.2) |
| seed and internal randomness | one fixed seed (42), part of the estimator definition. The seed acts only through LightGBM's 200,000-row histogram-binning sample (§3.3). Seed arbitrariness is carried as the probabilistic block `C_ML` (the existing seeds 1–10 scan). No seed averaging |
| interval and covariance use | I68 = x ± σ_tot and I95 = x ± 1.96 σ_tot from the diagonal of `C_tot = C_S + C_U + C_ML`; the full 205 × 205 `C_tot` for χ² model comparisons; σ_stat shown separately; the model allowance B± shown beside, never inside, `C_tot` |

**Claims, separated.**

- **K1 per cell (205 + integral).**
  - The statistical width σ_stat is a *precision* claim, not truth coverage. It is calibrated against
    independent-sample variability on the real data (§6, SD/SM).
  - The total σ_tot is the MAT-convention, nuisance-averaged propagation of a declared nuisance law
    through the same estimator, with the checks in §5. It is **not** an empirical coverage claim.
- **K2 regional.** The projections and the integral take their covariance from `C_tot` by exact linear
  projection; their validity is inherited from K1's components.
- **K3 simultaneous.** χ² use of `C_tot` is conditional on the MAT convention for `C_U` (rank-deficient,
  `2D_OMNIFOLD_STUDY_STATUS.md` χ² caveats). The statistical block's simultaneous calibration is testable
  only at the per-cell tier (M > 205, §8).
- **Truth notions.** The estimand is the population truth at the fixed simulated response under the
  declared nuisance law. Finite-sample truth (an MC bank's own truth) appears only in development closures.
- **Calibration notions.**
  - The data stream is calibrated conditional on the MC bank.
  - The MC stream is calibrated over independent half-banks drawn from the production (§7).
  - The systematic block is nuisance-averaged by convention.
  - None is conditional-on-θ coverage.
- **Not claimed (stated in the publication).**
  - empirical coverage of total intervals;
  - a validated or guaranteed model-dependence bound (B± is a development envelope);
  - response departures outside the simulated family (C's C10).

This is narrower than the successor proposal's §5 toy-coverage criteria for the total. §7 gives the
reason: the systematic block carries about 99 % of the median cell's variance (f_s median 0.0084, `C_ML`
share median 0.0006), and the systematic part's coverage is a
property of the declared law, which toys drawn from that same law do not test. Accepting this scope is
Joseph's decision (§16).

## 3. Measurements this design rests on (read-only or synthetic)

1. **Row identity of the inputs.** Every CV-level column of all four trees (17 columns: the
   `mc_signal_reco`, `mc_truth_denom`, `data` and `mc_background` branches the driver reads) has an
   identical float64 sha256 in the CV omnifile and in the current 171 GB universe omnifile.
   - Entry counts are equal: 32,849,103 / 32,849,103 / 4,119,797 / 658,227.
   - Source: `operands/remote_reduce.json` `omnifile_columns`; `logs/remote_reduce.txt`.
   - Consequence: a CV run sees identical training arrays from either file, row for row.
2. **Reproducibility of the seed-42 realization.**
   - The July background-aware sweep's CV (`purity_newomni`, current file, July driver, 128 threads)
     equals the May seed-42 CV `4f5a1b6d` to **1.4e-11** relative (max over 205 cells; `design_arith.json`
     `per_cell.central_diffs_in_sigma_tot.pn_CV_minus_CV42_max_rel`).
   - Thread count: the 300 VL170 replicas (shared, 64 threads) reproduce the 128-thread VL162 replicas'
     `hUnfold2D` to ≤ **5.8e-9** (median 1.3e-12; `state/ki84-rebuild-20261006/compare_full.json`).
3. **Where the seed acts** (synthetic, LightGBM 4.6.0 and sklearn 1.6.1 locally,
   `operands/seed_mechanism_check.json`).
   - With the production defaults on 400,000 rows, seeds 1 and 2 change predictions by up to 0.151.
     With all-row binning, or with 120,000 rows, the change is exactly 0.
   - At a fixed seed, Poisson(1) bootstrap weights leave the bin mappers unchanged; a different seed
     changes them.
   - sklearn's exact `GradientBoostingClassifier` gives identical predictions for `random_state` 1, 2 and
     `None`, including with tied (rounded) features.
   - These are synthetic data at reduced size and do not prove behaviour on production inputs.
4. **The exact central's environment.** On the cluster, `scikit_learn-1.8.0.dist-info` is dated
   2026-01-09 and `numpy-1.26.4` 2025-12-18, before `E_C` (written 2026-05-19T15:15Z); LightGBM 4.6.0 is
   dated 2026-05-21. A dist-info date is evidence, not proof, that the run used today's versions; the
   executed bytes of `E_C` remain unavailable (A `P01`).
5. **A matched, background-aware seed-42 sweep already exists** (`uq/purity_newomni/`, July, current
   file; `operands/remote_reduce_pn.json`).
   - All 187 universes are present.
   - The 100 Flux universes carry their own flux integral (native 1/Φ_u), and the background prediction
     varies in 43 of 44 bands.
   - Its MAT-convention σ_U is median **1.021×** the adopted block's (p16 0.985, p84 1.055, range
     0.70–1.20). Median σ_tot is 6.94 % (pn) against 6.87 % (adopted).
   - One Flux universe moves the background by up to 62 % of the CV maximum in one reco cell (the
     `Flux_0` change at the largest cell is +7.3 %). This is unexplained and must be inspected before use.
6. **Structure of the ±1σ pair bands** (both seed-42 sweeps; `operands/remote_reduce_pairs.json`;
   `design_arith.json` `pair_structure`). Descriptive and post hoc.
   - Of 42 pair bands, 6 (MaRES, MaCCQE, MvRES, CCQEPauliSupViaKF, LowQ2, Rvp2pi) have a common
     displacement A = (x₊ + x₋)/2 − x_CV that reproduces across the two sweeps (corr ≥ 0.75). The MAT
     pair convention does not count it as variance.
     - It is median **0.13 σ_tot** (p84 0.26, max 0.63).
     - Added in quadrature it would raise σ_tot by median 0.85 % (max 18 %).
   - In the other 36 the displacement does not reproduce (corr −0.08 to 0.72). Their half-differences
     also reproduce poorly (median correlation 0.60), except the three dominant pair bands below. They
     behave like a fresh estimator perturbation per run.
     - Read as noise, they inflate σ_tot by median **1.25 %** (p84 3.1 %, max 44 %).
     - This is an upper bound where background treatment differs between the sweeps.
     - It is internal randomness inside `C_U` that `C_ML` counts again.
   - The dominant bands are stable. Half-difference correlation: Muon_Energy_MINOS 0.983, MinosEfficiency
     0.997, Muon_Energy_MINERvA 0.972.
   - `Rvn1pi` and `Rvp1pi` give median widths equal to 1e-11 in the July sweep: the same shift may be
     counted twice. It is a 0.088 % band, so the effect is negligible, but it is unexplained.
7. **The statistical block barely moves the total.** The stat share of each cell's total variance, f_s,
   has median 0.0084 (p90 0.042, max 0.585).
   - Cells with f_s ≥ 0.05: 15; f_s ≥ 0.1: 5.
   - A KI-85-sized error (σ_stat off by 1.6×) changes σ_tot by more than 5 % in 11 cells
     (`mappings.total_sigma_ratio_if_stat_kappa_1.6`).
   - The two LightGBM seeds' centrals differ by median 0.026 σ_tot (max 0.14). The exact and LightGBM
     centrals differ by median 0.136 σ_tot (max 1.46).

## 4. Route comparison (item 2)

| | **L42: prospective matched LightGBM** | **X: existing exact central** |
|---|---|---|
| central | `E_L42` = seed-42 CV, reproduced across file, driver and run to 1.4e-11 (§3.2); not quoted, and a re-quote is Joseph's | `E_C` `142a45b0…`, frozen and quoted; executed bytes unavailable; `random_state=None` (synthetic evidence of seed invariance, §3.3); environment dates consistent (§3.4); reproduction unmeasured |
| statistical block | **new**: 300 Poisson replicas with VL170's recipe at `--seed 42` (shared 64 threads). The thread envelope (§3.2) makes them the central's realization family | **new**: 300 exact replicas (N > 205 for a full-rank `C_S`); N = 50 gives rank ≤ 49, per-cell only |
| systematic block | **existing, matched by construction**: `purity_newomni` (background-aware, native flux) or the adopted flux-fixed sweep (background frozen, `P06`). Both share the central's CV realization | **new**: 187 exact universe unfolds + CV; or a demonstrated transfer (XR stage T, §10) |
| seed/ML block | existing seeds 1–10. No overlap with `C_S` or vertical deltas through the binning sample (§3.3); the overlap is inside small `C_U` bands (§3.6) | `P09b`: XR measures whether the exact backend has any seed dependence |
| seed-1 stats / seed-42 systematics (`P07`) | **removed by construction**: every block at seed 42. The alternative L1 (seed 1, VL170 kept, new seed-1 sweep) costs 68–191 admitted node-h for the sweep against 25–93 for the seed-42 band | not applicable |
| matching cost (admitted, node-h) | **25–93** | **467–2,964**, forecast: no exact universe unfold has run; universe-file RSS 65–187 GB under today's driver; prototype 1 needs SB1 |
| wall per unfold | 9–32 min | 19.3–19.8 h |
| continuity | changes the quoted central (median 0.99 % per bin against seed 42, 0.136 σ_tot) | keeps it |

No numerical transfer tolerance is set from observed differences. XR stage T's tolerance (§10) is
declared here, before any transfer quantity exists.

## 5. Uncertainty sources and their treatment (item 3)

R = recomputed by the reported procedure; C = conditioned on; P = propagated (MAT); A = approximated or
bounded; — = not covered.

| source | treatment | reusable product | missing matching evidence or new construction | validation of the approximation |
|---|---|---|---|---|
| data statistics | R: Poisson data stream, 300 replicas, purity fixed per replica (VL170 recipe) | VL170 recipe | the seed-42 band (new) | SD (§6). Fixed purity scales the data-stream σ by the reco-bin purity (median 0.975), recorded as conditioning |
| signal-MC statistics | R: Poisson MC stream on `w_truth`/`w_reco`, completeness from un-resampled truth (KI-84 fix) | recipe | — | SM (§6) |
| background-template statistics | A: not resampled by production (C03) | — | analytic bound from the 658,227-row template and the purity (zero compute), or an SM arm that also splits `mc_background` | the bound must be < 10 % of σ_stat in every cell (proposal); otherwise construct a stream |
| background model | P: knob universes that vary the background prediction | `purity_newomni` (43/44 bands vary it) | inspection of the 62 % Flux-universe change (§3.5) | zero-compute comparison with the adopted sweep (§3.5 done; ratio median 1.021) |
| flux | P: 100 PPFX universes with native 1/Φ_u; flux-integral identity | `purity_newomni` Flux | KI-91 identity receipt (owner: 2D lane, zero compute) | identity proof, not the Pearson 0.96 correlation |
| targets | P: 1.4 % rank-1, counted once (C Audit 1) | analytic | — | Audit 1 CONFIRMED |
| detector response, vertical | P: weight universes (MinosEfficiency, GEANT) | sweep | — | §3.6 stability (MinosEfficiency h-corr 0.997) |
| detector response, lateral | A: CV-selected shadow support (C05a) | sweep | selection-complete laterals: the 5D `MNV101_ACTIVE_UNIVERSE` loops with a 2D selection and phase-space equality check (C's S-b) | per-lateral σ against shadow σ; replace if they differ by > 10 % of σ_tot in any cell (proposal) |
| interactions | P: GENIE/FSI knob universes, response and background together (C06) | sweep | the omitted reproducible displacements of 6 bands (§3.6) | report A beside the variance, as the MAT convention says; disclose its size |
| flux × muon-energy (X01) | A: the rank-2 fallback (`rederive_flux_muonE_cross.py` route B) with its transfer assumption stated, or a disclosed omission | script | coherent joint throws need the unbuilt M1 generator | not validated; disclosed |
| training randomness | P: `C_ML` (seed arbitrariness); A: estimator perturbation inside small `C_U` bands (§3.6, conservative, median +1.25 % σ_tot) | seedscan | a debiasing estimator would need its own error design; not proposed | disclosed as a measured double count in the conservative direction |
| regularization / model dependence | — in `C_tot`; B± as a nonprobabilistic development envelope beside it | closures in 2D STATUS "Validation" | 2D truth maps for the successor's GENIE+MEC and NuWro truths (location unverified) | **NO UNTOUCHED VALIDATION DOMAIN** (§7) |
| response departures outside the family | — (C10) | — | no method | declared assumption |

`C_tot` stays a block sum. Dependence that the sum omits is handled as follows:
- X01 by the fallback;
- the seed overlap is shown absent for `C_S` and vertical deltas (§3.3);
- noise inside small `C_U` bands is measured and disclosed rather than subtracted (§3.6).

## 6. Per-experiment reporting procedure, and the alternatives to full nesting (item 4)

**The reported procedure on the real data** (one experiment):
- one central unfold;
- 300 bootstrap replicas, which recompute the unfold;
- the universe deltas against the matched CV, propagated by MAT;
- `C_ML` from the existing scan;
- the analytic norm term;
- B± reported beside the result.

A fully nested validation would repeat all of this inside every pseudo-experiment. C prices that (P1)
at 0.29–1.21 million admitted node-h, and it would still need independent populations.

**Two affordable alternatives, tied to existing inputs:**

1. **Split-sample width calibration (SD/SM) of the statistical block, on the real data.**
   - *SD.* Split the 4,091,707 in-phase-space data rows into random halves by a salted hash.
     - Bernoulli thinning gives two independent Poisson samples at exactly half exposure.
     - Unfold each with the full bank and fixed purity (the band's conditioning), at POT/2.
     - Over R random splits, mean (U_A − U_B)²/2 measures the half-exposure sampling variance with no
       resampling model, no truth and no reservoir.
     - Compare it with a data-only bootstrap (M replicas) of one half.
   - *SM.* The same with the signal MC: two disjoint half-banks (MC/data 2.354 each), `--bootstrap-streams
     mc` on one half, and real data in both arms.
   - *What it validates and what it cannot.*
     - It validates the width of each stream at half size, on the real operating point.
     - It does not test bias or truth coverage.
     - Its MC-stream claim extends to the full bank by the bootstrap's own 1/n scaling, an assumption.
   - *Implementation.* It needs two driver options (`--data-split`, `--mc-split`), byte-identical when
     unset, and an equivalence test. The split mode takes completeness from `mc_signal_reco`'s own truth,
     using the Phase-17 bijection (c ≡ 1).
   - *KI-85.* It answers KI-85's question on real data. It is therefore KI-85-adjacent and needs
     Joseph's explicit ruling, as the deferral covers held-out re-tests.
2. **Structure checks in place of nested systematic recomputation.**
   - The MAT propagation of `C_U` is accepted as the convention. Its approximation errors are then
     measured on existing products at zero compute:
     - pair displacement A and its reproducibility (done, §3.6);
     - the per-run estimator perturbation (done, §3.6);
     - Flux identity (KI-91);
     - selection-complete lateral support (S-b).
   - The control is the criteria in §8. If a check fails, the component is rebuilt, or the claim is
     narrowed and disclosed.

A fixed transferred band (C's P2) would answer a different question: whether one frozen band covers
pseudo-data drawn from the declared law. It is not proposed; §7 gives the reason.

## 7. Populations and identities (item 5)

- **What one MC production supports.**
  - B's count is right for B's design: zero disjoint pairs of a production-size bank and a data-size
    reservoir.
  - It is not universal. A width calibration needs only one disjoint pair at a time: two half-banks
    (2 × 2.354), or two half-data samples.
  - Each random split is one 1-dof draw. The average over R splits is exchangeable, not R independent
    experiments. Its precision follows the half-sample (balanced repeated replication / delete-half
    jackknife) variance of a linear statistic. `design_arith.py` self-test: a seeded simulation agrees
    with the SE formula within 10 %.
- **Identity.**
  - Data rows are distinct events; (run, subrun, gate) is not an event key.
  - MC rows are deduplicated events: Phase 18.2 removed 133 truth and 7 reco duplicates on the packed
    ID. The trees are not row-aligned (`mc_signal_reco` appends misses), so the split uses
    `mc_signal_reco` alone.
  - Overlay dependence between halves is untestable here, as in B.
  - R0 (an identity-carrying rebuild) is not needed for SD or SM. It is needed for any reservoir design.
- **Why no empirical total coverage.**
  - With f_s at median 0.0084, a total-interval coverage experiment is almost entirely a test of the
    systematic block under the declared nuisance law.
  - Pseudo-data drawn from the sweep's own universes reproduce the band by construction.
  - New continuous throws need the unbuilt M1 generator, and PPFX has a fixed set of 100 throws.
  - Pseudo-data drawn on the training events are also circular in the MC stream (PREREG A1.3).
  - So repeated sampling from this inspected finite bank cannot give unconditional population
    validation of the total. A conditional version would test linearity, which §6 alternative 2 measures
    directly at zero compute. **NO-GO for the empirical total-coverage claim**, unchanged from C, now
    with this reason.
- **Model allowance.**
  - Every truth available for 2D is either inspected development evidence or inside the covariance:
    - Tune v1 and the STATUS closures (gauss_pt, tilt_pz, dpT, MaCCQE:0, Flux:50);
    - the s5p P1r–P3r ratios;
    - the knob universes, which are in `C_U`.
  - The 2D ancillary holds only the Tune v1 prediction. **NO UNTOUCHED VALIDATION DOMAIN** for B±: it is
    a development envelope.
  - Lifting this needs new simulation for a named design: truth-level samples from independent
    generators (e.g. GiBUU, NEUT), applied by truth-ratio reweighting. Analyst time and generator setup
    are unpriced. Compute is assumed ≤ 50 CPU node-h (ASSUMED, not a quote).
- **Response tests.** None exist outside the simulated family (C10). Declared.

## 8. Proposed criteria and assurance (item 6)

All are proposals, frozen here for review. All inspected cases are development evidence. SD and SM run
on the production data and MC, but no recipe choice may follow their outcome, and each has one final look.

| criterion | rule (proposed) | assurance (`design_arith.json`) |
|---|---|---|
| R reproduction (XR) | max over the 205 cells and the integral of \|x_new/x_ref − 1\| ≤ 1e-8 | measured envelopes: 5.8e-9 cross-thread (max of 300), 1.4e-11 cross-file. The exact backend is single-threaded and expected bitwise. False-fail probability: no observed pair above 0.58 of the tolerance |
| M matching | every block's CV equals the central to ≤ 1e-8; identical cell sets (refused otherwise by `reported_cells.py`); recipe identical except the seed | deterministic |
| W-regional (SD, SM) | per stream, per region (the 15 cells with f_s ≥ 0.05, and the remaining 190): faithful if the 95 % interval of the median κ̂ = σ_split/σ_boot lies inside [0.80, 1.25]; FAIL (direction) if entirely outside; else INCONCLUSIVE. Four tests at Bonferroni 0.0125 | R = M = 100: half-width of ln(median κ̂) 0.055 (if n_eff = 20) to 0.111 (n_eff = 5), against ln 1.25 = 0.223. n_eff is assumed, not measured. Kurtosis from the 100 VL169 toys: median 0.02 |
| W-cell (optional tier) | per cell with f_s ≥ 0.05 (15 cells × 2 streams = 30 tests): accept \|ln κ̂\| ≤ 0.158 | R = M = 399: familywise false-fail ≤ 0.05 at κ = 1; pass probability ≤ 0.10 at κ = 0.8 or 1.25. All 205 cells would need R = M = 535 |
| K3-stat (descriptive) | Q_r = d_rᵀ(2Ĉ_half)⁻¹d_r over splits against the Hotelling reference | only at the per-cell tier (M = 399 > 205) |
| systematic structure | Flux identity proved (KI-91); selection-complete lateral σ within 10 % of σ_tot of the shadow σ in every cell; the background bound < 10 % of σ_stat in every cell; the reproducible displacement A reported beside the variance | deterministic reads; no sampling |
| usefulness | median relative I68 half-width ≤ 10 % and 90th percentile ≤ 25 % over 205 cells; integral ≤ 10 %; median B± ≤ 5 % (successor §5) | current construction: median 6.87–6.94 %, p90 11.6–11.9 % (pass); integral and B± not computed |
| missing results | infrastructure failure: ≤ 3 identical-seed reruns. Numerical failure: one rerun, then the cell counts against the test. > 1 % missing, or a verdict that differs between all-hit and all-miss imputation: INCONCLUSIVE. XR: any missing comparison is INCONCLUSIVE | — |

**Relation to the 0.63 / 0.92 proposals.** They are lower bounds for direct coverage counting. They
correspond to κ ≤ 1.116 (I68) and κ ≤ 1.120 (I95) on the under-coverage side. This route counts no
coverage, so they are context, not rules. κ ∈ [0.80, 1.25] spans I68 coverage 0.789 to 0.576 and I95
coverage 0.986 to 0.883.

No statistical-only result here may become a total-uncertainty claim.

## 9. Prices (item 7)

Admitted = subtotal / 0.8, with a 5 % retry and a 10 % verification rerun inside the subtotal.
- Units: CPU node-h; core-h = 128 × node-h (two 64-core EPYC 7763 per node); A100-h 0 throughout.
- Rates (`design_arith.json` `costs.rates_node_h`):
  - LightGBM CV-file unfold: 0.0591 (shared 64, 300 measured) or 0.216 (full node, 1 measured);
  - LightGBM universe-file unfold: 0.7075 (374 measured);
  - exact unfold: 0.666 packed (forecast) or 19.31 as run;
  - exact universe-file unfold: 0.667 (prototype 1) / 2.83 / 4.95 / 9.91 (forecasts by RSS).

| item | admitted node-h (opt – cons) | depends on |
|---|---|---|
| **XR** (next experiment, §10) | **2.77** as specified (exact jobs on shared at `--mem 24G`, 12/256 billing); 2.08 at the 29-per-node packing forecast; 55.7 if the exact jobs needed full nodes. Hard cap by job limits 2.94 | shared-QOS memory billing |
| L42 matching: seed-42 band (300 runs) | 25.5 – 93.2 | nothing new |
| L1 alternative: seed-1 sweep (188 universe-file runs) | 67.6 (prototype 1, needs SB1) – 191.2 | SB1 for the low end |
| L42 complete (matching + S-b + 10 lateral + 6 B± unfolds + SD/SM) | regional tier **79 – 314**; per-cell tier **232 – 871** | S-b 1.3–23.8 (C, billing assumed) |
| X matched construction (300 exact replicas + 188 exact universe unfolds) | 467 – 2,964 (forecast) | exact-universe RSS unmeasured; SB1 / prototype 1 for the low end |
| X complete (matched + S-b + laterals + B± + SD/SM at exact rates) | regional tier **1,059 – 28,136**; per-cell tier **2,776 – 77,939** | as above; 19.3 h per unfold |
| XR stage T (conditional, §10) | 63 – 276 (forecast) | exact-universe RSS |

- **Comparators, not ceilings.** `m3246` CPU balance 3,040.6 node-h (iris, 2026-10-09T06:15Z, B; to be
  re-measured before any admission); annual allocation 20,000.
- **SB1 sensitivity.** L42 runs no universe-file unfold, so its price does not depend on SB1 or on speed's
  I/O finding. X's sweep moves between 180 (prototype 1, forecast) and 765–2,677 admitted (today's
  driver). SB1 itself is 1.3, cap 2.0 node-h.
- **Storage.** L42 reads the 2.14 GB CV omnifile. Outputs are 0.06 MB per unfold: ≤ 2,394 SD/SM runs make
  ≤ 0.15 GB. XR stage T reads the 171 GB universe file. The CV omnifile has no CFS copy recorded here;
  make one (2.1 GB) before admission, since `/pscratch` is purgeable.
- **Identity construction** is not needed for L42 or XR (§3.1, §7). Independent verification is a local
  recomputation of every comparison from the outputs (0 node-h) plus the 10 % rerun already priced.

## 10. The next experiment: XR, reproduction of both candidate centrals (item 8)

**Question.**
- Can today's checkout, environment and inputs regenerate the quoted exact central byte for byte (to
  1e-8), and is the exact backend independent of its seed?
- Does a CV-file seed-42 LightGBM run reproduce the seed-42 realization that both existing sweeps are
  matched to?

**Why this one.**
- Every route-discriminating unknown sits on the X side. L42's central reproducibility is already
  evidenced by existing products (§3.2).
- The keep-and-disclose central needs a reproducibility statement for publication whichever route is
  chosen.
- It is the cheapest measurement that can retire route X. It is a reproduction, not a transfer
  measurement, and no tolerance is fitted to an observed difference.
- N2 is not proposed. Its held-out data-stream diagnostic bears on a block that carries a median 0.84 %
  of each cell's total variance. SD answers the same question more directly, on real data, without R0.

**Runs** (four; guarded launch through `nd-unfolding/mnv_guarded_run.py --require-provenance`, with the
executed-module expectations stated; driver at a commit ≥ `355174fe`):

| run | arguments | hardware | reference |
|---|---|---|---|
| X0 | the central launcher's arguments unchanged (`sbatch_unfold_2d_MEFHC.sh`: `--omnifile <CV> --mcfile baseline_flux/runEventLoopMC_MEFHC.root --iters 5 --use-weights`; no `--estimator`, no `--seed`) | shared, `-c 2`, `--mem 24G`, 26 h limit | `E_C` `142a45b0…` |
| X1 | X0 plus `--seed 1` | same | X0 |
| L0 | `--estimator lgbm --seed 42`, CV file, no `--universe` | shared 64, 1 h limit | `4f5a1b6d…` and the `purity_newomni` CV |
| L1 | `--estimator lgbm --seed 1`, CV file | shared 64, 1 h limit | seedscan seed 1 `d7fe901f…` |

**Manifest.**
- Pin the commit and every input digest in the record before submission: CV omnifile `43f8cc16…` (and its
  CFS copy), flux file `baseline_flux/runEventLoopMC_MEFHC.root` (digest to be measured), helper
  `e96234124a31…`, driver blob.
- Environment `root_6_28`: sklearn 1.8.0, LightGBM 4.6.0, numpy 1.26.4. Record `threadpoolctl` output.
- Each output's `runConfig`, argv and digests; `sacct` State, Elapsed, MaxRSS and billing.

**Criteria.**
- Each comparison passes if every one of the 205 cells and the integral agree to ≤ 1e-8 relative, on
  identical cell sets.
- X0 and X1 also report the maximum absolute difference as a number.

**Outcomes and the decision each changes.**

| X0 vs `E_C` | X1 vs X0 | L0, L1 | decision |
|---|---|---|---|
| pass | pass | pass | Both centrals are reproducible, and `P09b` is resolved (no seed dependence at 1e-8). Joseph chooses L42 (re-quote, 79–314 admitted to completion) or XR stage T (63–276) to learn whether X can borrow L42's blocks. The keep-and-disclose text may state that the quoted central is reproducible |
| fail | pass | pass | The quoted bytes cannot be regenerated in today's environment. Route X **FAIL** for "reproducible central": an exact route would need a new exact central plus the full exact construction, so L42. The interim publication text must say the central is not reproducible |
| any | fail | pass | The exact backend is seed-dependent. The quoted central is one unrecorded draw, and a 10-seed exact scan (≈ 6.7 node-h) and a seed policy are needed: X dominated, L42 |
| any | any | L0 fail | Contradicts §3.1–§3.2. Stop. Diagnose the driver revision before building the seed-42 band; L42's band would then run on the universe file (≈ 212 node-h) or fall back to L1 |
| missing | | | INCONCLUSIVE for that comparison; no substitution |

**XR stage T (preregistered here, not part of the request; released only by a separate authorization
after X0/X1 pass).** Exact unfolds on the universe file:
- 10 Flux throws, chosen by `int(sha256("xr-T" ‖ u)[:8], 16)` order;
- both universes of Muon_Energy_MINOS, MinosEfficiency and Muon_Energy_MINERvA (16 runs);
- 50 exact Poisson replicas.

The tolerance is declared now, before any transfer quantity exists. Replace the tested bands' widths in
`C_tot` by the exact ones (pair half-differences; the Flux width scaled by the paired ratio
√(Σδ_X²/Σδ_L²) over the 10 throws), and the statistical width by the exact replicas' in proportion to
f_s. PASS iff the relative change η in σ_tot satisfies max |η| ≤ 0.05 and median |η| ≤ 0.02, which keeps
I68 coverage within 0.659–0.707 and I95 within 0.938–0.961. The tested bands carry a median 86 % of each
cell's variance (min 24 %), so a PASS covers the rest only by assumption, and that must be disclosed.

**What XR cannot authorize.** It cannot re-quote, replace a band, claim a transfer, lift KI-85, run N2,
adopt anything or change a gate.

**Remaining authorization (Joseph).**
- XR compute: ≤ 3.0 CPU node-h on `m3246` (two shared jobs of ≤ 1.22 node-h each, two of ≤ 0.25), 0 GPU,
  ≈ 20 h wall.
- An explicit statement that this reproduction is outside the 2026-10-09 prohibition on transfer
  measurements.
- One owner and one fresh reviewer for the record.

## 11. Proposed register and routing changes (for the integration owner; not applied)

1. **`KNOWN_ISSUES.md` 88, append:** *"2026-10-10 (`state/next-preparation-20261009/two-d-path/REPORT.md`):
   the design proposes route L42 — LightGBM seed 42, whose CV realization both existing seed-42 sweeps
   share (reproduced to 1.4e-11 across files and drivers) — with a new seed-42 statistical band
   (25–93 admitted node-h). The next experiment XR (≤ 3.0 node-h) tests whether the quoted exact central
   can be regenerated. Nothing is authorized; no number changes."*
2. **New `KNOWN_ISSUES.md` row (LOW, owner: 2D lane), descriptive:** *"2D universe sweeps: in 36 of 42
   ±1σ pair bands the deltas behave as a fresh estimator perturbation per run (cross-sweep correlation of
   the common displacement < 0.75), inflating σ_tot by a median 1.25 % (max 44 %, upper bound) and
   double-counting internal randomness with C_ML. In 6 bands a reproducible one-sided displacement of
   median 0.13 σ_tot (max 0.63) is omitted by the MAT pair convention and not reported. Rvn1pi and
   Rvp1pi give median widths equal to 1e-11. Route: two-d-path REPORT §3.6."*
3. **C's assessment, Audit 4 and `components.tsv` X02/X03 (annotation):** *"LightGBM's seed acts only
   through the 200,000-row binning sample (synthetic check, two-d-path §3.3). A fixed-seed bootstrap and
   vertical-universe runs share bin edges, so there is no seed-noise overlap with C_S or vertical deltas
   through that mechanism. The overlap that exists is a per-run estimator perturbation inside small C_U
   bands (§3.6)."*
4. **A's `pairings.tsv` `P07` (annotation):** *"Avoidable by construction for a seed-42 estimator. Both
   seed-42 sweeps share one CV realization (1.4e-11), and the CV-level arrays of the two omnifiles are
   row-identical (two-d-path §3.1–§3.2)."* `P06` annotation: *"A background-aware seed-42 sweep exists
   (`uq/purity_newomni/`, 187/187, native flux, background varies in 43 of 44 bands; σ_U ratio median
   1.021)."*
5. **B's DESIGN §1 ground 1 (scope note):** *"The zero count applies to production-size outer coverage
   experiments; a split-sample width calibration needs one disjoint half-size pair at a time
   (two-d-path §6–§7)."*
6. **2D STATUS (one line under the Stage-2 envelope):** row identity of the CV-level columns of the two
   omnifiles; the existence and properties of `purity_newomni`.
7. **CATALOG:** the existing two-d-path route stands. If XR is admitted, add its record under § Current
   work.

## 12. Verification and review

- **Self-checks.**
  - `design_arith.py --self-test` PASS: 14 checks, including the T/0.8 reserve (with a ×1.2 negative
    control), the coverage inversions, the monotonicity of the assurance design and a seeded simulation of
    the split-sample SE.
  - `design_arith.json` is regenerated from the committed operands.
  - `seed_mechanism_check.py` exit 0.
- **Review.** Pending at the freeze commit. Recorded in `review/` and in this section after the review.

## 13. Limitations

- **Seed mechanism.** §3.3 is synthetic and small. Production-scale confirmation is an XR-adjacent
  measurement, not run.
- **§3.6 pair figures.** They are single-realization, per-cell estimates. The noise share is an upper
  bound where background treatment differs between the sweeps. The mechanism (estimator instability
  against one-sided response) is inferred from reproducibility, not established.
- **Split-sample precision.** The global tier assumes n_eff between 5 and 20 for the cell correlation.
  The per-cell tier assumes near-Gaussian replicas (toy kurtosis median 0.02, p84 0.60).
- **Exact backend.** Every exact-universe price is a forecast. The 0.666 packed rate is a memory-share
  billing forecast; contention is unmeasured.
- **Not measured here.** The integral's width, B± and the background-template bound.

## 14. Resources

| item | measured | cap |
|---|---|---|
| active time | 2026-10-10, first tool call ≈ 04:20Z (worktree created 04:33:53Z); the delivery time is in §12 | 8 h |
| local CPU | ≈ 0.02 core-h (seed check 24 s user; arithmetic < 1 s per run; git and hooks) | 3 core-h |
| threads | 2 | 2 |
| peak RAM | 0.34 GB (seed check) | 8 GiB |
| scratch | ≈ 25 MB (LightGBM venv 23 MB, JSON copies) | 2 GiB |
| tracked | ≈ 1.8 MB (operands 1.6 MB, of which the two per-band per-cell reductions are 1.5 MB) | 10 MiB |
| Perlmutter | login node only, read-only: 9 runs of 3 scripts, ≈ 5.6 min wall at ≈ 95 % of one core, ≤ 1.4 GB RSS. The first run failed after 23 s on a char-branch conversion. Five ran earlier script versions, superseded by extended or digest-only versions; their extra fields (data-tree values and sums, one reco-cell data count) were not committed, and every retained field is identical (`logs/`). Plus `ls`/`stat` reads. No job, no allocation charge | 0 node-h |

## 15. Disposition

| decision | disposition | reason |
|---|---|---|
| a complete route for declared claims | **PASS: L42** | Matched by construction at seed 42. The central is reproduced across files, drivers and threads (§3.1–§3.2). Every source has a treatment and evidence (§5). Criteria and assurance are frozen (§8). Complete for 79–314 admitted node-h (regional tier) |
| exact-central route X | **INCONCLUSIVE** | Reproducibility of `E_C`, its seed dependence and the exact-universe memory are unmeasured. On current forecasts its matched construction costs 467–2,964 admitted node-h and its completion 1,059–28,136. XR retires it or keeps it |
| empirical total-interval coverage | **NO-GO** | §7: circular in the declared law; no independent populations for the MC stream at production size; a linearity test is what remains, and it is measured at zero compute |
| model-dependence validation stage | **NO-GO** | no untouched domain (§7); B± is a development envelope |
| next experiment | **PASS: XR** | preregistration-ready (§10). Every outcome changes a named decision. ≤ 3.0 node-h |
| publication-ready measurement | **NOT ACHIEVED** | nothing here is executed or adopted |

## 16. Next action

Joseph decides three things. None needs compute until he authorizes it.
1. **The claim scope (§2).** Accept per-cell and regional claims with a convention-defined total and a
   development-envelope B±, or require empirical total coverage. The latter is NO-GO until new
   populations or a validated generative law exist.
2. **XR.** ≤ 3.0 CPU node-h, ≈ 20 h wall, guarded, one owner and one reviewer.
3. **After XR,** route L42 (re-quote, then 79–314 admitted to completion) or XR stage T (63–276) if
   keeping the quoted central is worth its price.

The integration owner applies §11 if accepted. The 2D lane owns KI-91, the background bound, the 62 %
Flux-universe change and the Rvn1pi/Rvp1pi question.
