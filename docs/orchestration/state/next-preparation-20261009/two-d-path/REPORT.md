# 2D publication path after keep-and-disclose: route design and the next experiment

**CITABLE FOR:**
- the declared 2D measurement and claim family (§2);
- the read-only and synthetic measurements in §3, each with its operand file;
- the route comparison, uncertainty treatment, population audit, proposed criteria, assurance and
  prices (§4–§9, from `design_arith.json` unless another committed source is named);
- the preregistration-ready specification of the next experiment XR (§10);
- the proposed register changes for the integration owner (§11).

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- an adoption, a re-quote, a band replacement or a changed gate;
- a transfer between estimators;
- compute authority.

Every tolerance below is a **proposal**. The §3.6 pair-band figures are post hoc and descriptive.
Publication readiness is **not achieved** by this design.

| field | content |
|---|---|
| `Lane` | `two-d-path` (next session registered by the integration of the next-preparation batch, §7 of its report) |
| `Decision` | Which complete 2D procedure has a defensible, affordable route to a reproducible central estimator, matched total uncertainties and validation supporting explicitly declared publication claims? What single next experiment would distinguish the leading options or retire an infeasible route? |
| `Branch` / `Base` / `Head` | `prep/two-d-publication-path-20261009` / `a16d578646936a0cc6eca41e3e0350e756ee0dca` (`origin/main` at 2026-10-10T04:30Z, merged integration PR #68) / the commit carrying this revision. Reviewed commits are in §12 |
| `Owned files` | `docs/orchestration/state/next-preparation-20261009/two-d-path/` only: this report; `design_arith.py`, `design_arith.json`; `seed_mechanism_check.py`; `remote_reduce.py`, `remote_reduce_pn.py`, `remote_reduce_pairs.py`; `operands/` (four JSON files); `logs/`; `review/` (the reviewer's documents, verbatim) |
| `Pinned inputs` | §1 |
| `Resources` | §14. Cluster jobs, GPU, training on production data, toys and event loops: **0**. Read-only login-node reductions: ≈ 5.6 CPU-min |
| `Review` | §12: initial review **FAIL** (9 MATERIAL); one repair batch; focused re-review **PASS WITH CHANGES** (N1, N2 MATERIAL, text only). The post-review edits for N1–N7 are not re-reviewed |
| `Model / effort` | owner Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §15: **PASS** — route L42 is a complete design for the claims declared in §2, priced at the declared-family tier. **INCONCLUSIVE** — the exact-central route X: its decisive inputs are unmeasured, and on current forecasts it costs 12–90× more. **NO-GO** — an empirical total-interval coverage claim, and the model-allowance validation stage. **PASS** — the specification of the next experiment XR |
| `Next action` | §16: Joseph decides on the claim scope (§2), and on XR (≤ 6.4 CPU node-h hard cap, 2.8 expected, 0 GPU, ≈ 20–30 h wall). That includes an explicit ruling on XR's one-seed `P09b` arm and the deployment of the canonical checkout |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = this directory.

## 0. Setup

- **Roles.** One owner (this session). One fresh read-only reviewer at a fixed commit, with one initial
  review and one focused re-review after a single repair batch (§12). No other agent, no peer message.
- **Terminal outcomes.**
  - PASS: a complete route and a named next experiment are ready for Joseph's decision.
  - FAIL: the evaluated route cannot meet its declared requirements.
  - INCONCLUSIVE: a named input or method prevents a decision.
- **Budget.** 8 active hours, 3 local CPU core-hours, two threads per command, 8 GiB RAM, 2 GiB new
  scratch, 10 MiB tracked. No scientific production.
- **Authority.** The prohibitions of Joseph's 2026-10-09 ruling stand (closeout REPORT §11): no re-quote,
  no transfer measurement, no N2, no KI-85 lift, no changed gate, no reopened campaign. A changed central
  estimator is reserved to him.

## 1. Baseline and inputs

- **Integration is verified for this design.** `origin/main` = `a16d5786` (PR #68). The six lane heads
  (publication `78837efe`, guard `63257cd4`, structure `0f4a059f`, speed `318d3e45`, gbdt `d6652270`, pet
  `d9a460c6`) are ancestors of it, and each lane `REPORT.md` is blob-identical between its head and
  `a16d5786`. The base is therefore the integrated main, not `5ac9706a`.
- **Records read** (blob at `a16d5786`):
  - A pairing `05356fbf`; B design `fc2a5d9a`; C feasibility `921bb325`; DELIVERY `554f391c`;
  - successor proposal `25c53d4c`; closeout REPORT `bd7ce9a7` (§11 ruling); integration REPORT `88cd3d5a`;
  - speed REPORT `56d0bfb7` and `results/costs.json` `63aaff60`;
  - 2D STATUS `547b2530`; REFERENCE `b7251698`; `KNOWN_ISSUES.md` `5e377f0f` (rows 84, 85, 88–91);
  - the campaign review, `docs/CURRENT_WORK.md` and DISPATCH.
- **Products read on Perlmutter** (sha256, 2026-10-10):
  - `E_C` `142a45b0…`; seed-42 CV `4f5a1b6d…`;
  - seedscan seed 1 `d7fe901f…` (seeds 2–10 in `operands/remote_reduce.json`);
  - `VL170` `71a75821…`; `C_ML` `3b6b48ec…`; universe covariance `62590df7…`;
  - the July CV `purity_newomni/…_pn_uni_CV.root` (digest in `operands/remote_reduce_pn.json`);
  - both omnifiles (CV file `43f8cc16…`, B's digest).

## 2. The declared measurement and claim family (item 1)

| element | declaration |
|---|---|
| measurand | flux-averaged ν_μ CC-inclusive d²σ/dp_T dp_∥ per nucleon, ME FHC, θ_μ < 20°, in cm² (GeV/c)⁻² nucleon⁻¹ |
| reporting map | all 205 reported cells of the paper's 14 × 16 grid (`2D_OMNIFOLD_STUDY_STATUS.md` "Paper binning"), in row-major paper `GlobalID` order, with cell identity from `uq/reported_cells.py`; the area-weighted integral over those cells; the 14 p_T and 16 p_∥ projections. That is 236 functionals. No coarsening and no dropped cell |
| normalization | absolute: data POT 1.0574e21, MC POT 4.9782e21, N_nucleons 3.2352943e30, flux integral 8.7407e-3 m⁻²/POT with the per-p_T `hFlux_pt` (A §2.2) |
| estimator `E_L42` | the driver at a commit ≥ `355174fe`, which records `runConfig` and the driver and helper digests; the helper `omnifold.py` `e96234124a31…`; `--estimator lgbm --seed 42 --iters 5 --use-weights --bkg-mode purity`; `root_6_28` (LightGBM 4.6.0, numpy 1.26.4); the CV-level arrays of either omnifile (row-identical, §3.1); 64 or 128 threads (§3.2) |
| seed and internal randomness | one fixed seed (42) as part of the estimator definition, with no seed averaging. The probabilistic block `C_ML` (the existing seeds 1–10 scan) carries the arbitrariness of the seed choice. Synthetic evidence (§3.3), not a production measurement, places the seed's action in LightGBM's 200,000-row binning sample |
| interval and covariance use | I68 = x ± σ_tot and I95 = x ± 1.96 σ_tot, from the diagonal of `C_tot = C_S + C_U + C_ML`; the full 205 × 205 `C_tot` for χ² model comparisons; σ_stat shown separately; the model allowance B± shown beside `C_tot`, never inside it |

**Claims, separated.**

- **K1, per functional (205 cells + integral).**
  - σ_stat is a *precision* claim, not truth coverage. Its per-functional width is calibrated against
    independent-sample variability on the real data at half size, for both streams (§6, SD/SM, declared
    tier).
  - σ_tot is the MAT-convention, nuisance-averaged propagation of a declared nuisance law through the
    same estimator, with the checks in §5. It is **not** an empirical coverage claim.
- **K2, regional (the 30 projections).** Their covariance comes from `C_tot` by exact linear projection.
  Their statistical widths are tested directly as functionals in the declared tier, which tests the
  off-diagonal statistical structure along those directions. Their systematic part inherits the K1
  convention.
- **K3, simultaneous.** χ² use of `C_tot` is conditional on the MAT convention for `C_U`, which is
  rank-deficient (`2D_OMNIFOLD_STUDY_STATUS.md` χ² caveats). For the statistical block a split-sample
  Hotelling-type statistic is reported descriptively (M = 540 > 205). It has no verdict role.
- **Truth notions.** The estimand is the population truth at the fixed simulated response, under the
  declared nuisance law. Finite-sample truth (an MC bank's own truth) appears only in development
  closures.
- **Calibration notions.** These are distinct claims, and none is conditional-on-θ coverage:
  - the data stream is calibrated conditional on the MC bank;
  - the MC stream is calibrated over disjoint half-banks drawn from the one production (§7);
  - the systematic block is nuisance-averaged by convention.
- **Not claimed (stated in the publication):**
  - empirical coverage of total intervals;
  - a validated or guaranteed model-dependence bound (B± is a development envelope);
  - response departures outside the simulated family (C's C10).

**This is an explicit narrowing, and accepting it is Joseph's decision (§16).** The successor proposal's
§5 required toy coverage of the total; this declaration does not.

- The reason (§7): the systematic block carries about 99 % of the median cell's variance (f_s median
  0.0084, `C_ML` share median 0.0006).
- The systematic part's coverage is a property of the declared law, which toys drawn from that law do not
  test.

A **narrower alternative** is the regional tier (§8). It validates the statistical width only through
region medians. It is cheaper, but it would also narrow K1 and K2's statistical claim from per-functional
to regional. It is not the PASS basis.

## 3. Measurements this design rests on (read-only or synthetic)

1. **Row identity of the inputs.**
   - Every CV-level column of all four trees (17 columns of `mc_signal_reco`, `mc_truth_denom`, `data` and
     `mc_background` read by the driver) has an identical float64 sha256 in the CV omnifile and in the
     current 171 GB universe omnifile.
   - Entry counts are equal: 32,849,103 / 32,849,103 / 4,119,797 / 658,227 (`operands/remote_reduce.json`;
     `logs/remote_reduce.txt`).
   - A CV run therefore sees identical training arrays from either file.
   - The universe-weight columns were **not** compared, and the May universe file is not available.
2. **Reproducibility of the seed-42 realization.**
   - The July sweep's CV (`purity_newomni`, current file, 128 threads) equals the May seed-42 CV `4f5a1b6d`
     to **1.4e-11** relative, max over 205 cells (`per_cell.central_diffs_in_sigma_tot.pn_CV_minus_CV42_max_rel`).
   - The 300 VL170 replicas (shared, 64 threads, October driver) reproduce the 128-thread VL162 replicas'
     `hUnfold2D` to ≤ **5.8e-9** (median 1.3e-12; `state/ki84-rebuild-20261006/compare_full.json`).
3. **Where the seed acts** (synthetic: LightGBM 4.6.0 and sklearn 1.6.1 run locally,
   `operands/seed_mechanism_check.json`).
   - With the production defaults on 400,000 rows, seeds 1 and 2 change predictions by up to 0.151. With
     all-row binning, or on 120,000 rows, they change nothing.
   - At a fixed seed, Poisson(1) weights, including zeros, leave the bin mappers unchanged; a different
     seed changes them. Reruns at identical arguments, and 1 against 2 threads, are bitwise equal.
   - sklearn's exact `GradientBoostingClassifier` gives identical predictions for `random_state` 1, 2 and
     `None`, including with tied features.
   - The data are synthetic and small. This is evidence about mechanism, not proof on production inputs.
4. **The exact central's environment.**
   - `scikit_learn-1.8.0.dist-info` is dated 2026-01-09 and `numpy-1.26.4` 2025-12-18, both before `E_C`
     (written 2026-05-19T15:15Z). LightGBM 4.6.0 is dated 2026-05-21.
   - These dates are evidence, not proof, of the run's environment.
   - `E_C`'s executed bytes are unavailable (A `P01`). The driver has had nine commits since; the first,
     `baa0a76f`, landed the same day.
   - Both the E_C-era driver and today's insert the canonical cluster checkout's
     `unbinned_unfolding/python` at `sys.path[0]` (`unfold_2d_omnifold_unbinned.py` at `d1bc8813`, lines
     820–822), so a run of either driver is expected to import that checkout's helper.
   - The insert is conditional, and another `omnifold` package exists in the repository. The guard
     inventory's resolved origin is therefore the evidence of which helper ran, not this reading.
5. **A background-aware seed-42 sweep exists** (`uq/purity_newomni/`, July, current file;
   `operands/remote_reduce_pn.json`).
   - It is complete: 187 of 187 universes.
   - The 100 Flux universes carry their own flux integral (native 1/Φ_u).
   - The background prediction varies in 43 of 44 bands.
   - Its MAT-convention σ_U is median 1.021× the adopted block's (p16 0.985, p84 1.055, range 0.70–1.20).
     That comparison is confounded in the same way as §3.6 and validates nothing by itself.
   - One Flux universe moves the background by up to 62 % of the CV's largest cell. `Flux_0` moves that
     cell by +7.3 %. This is unexplained and must be inspected before use.
   - **Frozen fallback.** If the inspection shows a defect, the systematic block reverts to the adopted
     flux-fixed seed-42 sweep, with the background-model omission (`P06`) disclosed. That sweep shares the
     same CV realization.
6. **±1σ pair bands across the two seed-42 sweeps** (`operands/remote_reduce_pairs.json`;
   `pair_structure`). Descriptive and post hoc.
   - **What separates the sweeps.** They share one CV realization, but they differ in background
     treatment, in the universe omnifile (regenerated 2026-07-08, after the adopted sweep ran; the July
     rebuild record calls it "the Jul-04 event-loop binary drift",
     `2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh`) and in the driver revision.
   - **6 of 42 bands reproduce.** In MaRES, MaCCQE, MvRES, CCQEPauliSupViaKF, LowQ2 and Rvp2pi the common
     displacement A = (x₊ + x₋)/2 − x_CV reproduces across the sweeps (corr ≥ 0.75). The MAT pair
     convention does not count A as variance, and it is not reported anywhere.
     - It is median **0.13 σ_tot** (p84 0.26, max 0.63).
     - Added in quadrature it would raise σ_tot by median 0.85 % (max 18 %).
   - **36 bands do not reproduce.**
     - The displacement correlation is −0.08 to 0.72.
     - Their half-differences correlate with median 0.60. The three dominant pair bands are the exception:
       Muon_Energy_MINOS 0.983, MinosEfficiency 0.997, Muon_Energy_MINERvA 0.972.
     - The non-reproducible variance is median 2.5 % of a cell's total (p84 6.3 %), and exceeds it in one
       cell: reported index 126, bins (7, 14).
     - If it were additive inside the total, σ_tot would be inflated by median 1.27 % (p84 3.25 %). It is
       unbounded in that one cell.
     - **The mechanism is unknown.** By §3.3, fixed-seed weight-only runs share bin mappers and LightGBM
       is deterministic, so the binning sample does not explain it; differences of input do.
     - It is not shown to double-count `C_ML`.
   - **Rvn1pi and Rvp1pi** have pair half-differences equal to 1.4e-9 (adopted) and 2.6e-9 (July), so one
     shift may be counted twice. It is a 0.088 % band, so the effect is negligible, but it is unexplained.
7. **The statistical block barely moves the total.**
   - f_s, the stat share of a cell's total variance, has median 0.0084 (p90 0.042, max 0.585).
   - 15 cells have f_s ≥ 0.05 with the adopted σ_U, 16 with the July σ_U; the latter is frozen as family F.
   - KI-85's data-stream discrepancy points to a band about 1.6× too *wide* (κ ≈ 0.63). Applied to the
     whole statistical block, it changes σ_tot by more than 5 % in 2 cells
     (`mappings.total_sigma_ratio_if_stat_kappa_0.63`).
   - The two LightGBM seeds' centrals differ by median 0.026 σ_tot (max 0.14). The exact and LightGBM
     centrals differ by median 0.136 σ_tot (max 1.46), or 0.99 % per bin.
   - The seed-42 CV sits within the seeds 1–10 spread with rms z 1.28 (t₉ expectation 1.13) and max
     4.25: mild over-dispersion, disclosed.

## 4. Route comparison (item 2)

| | **L42: prospective matched LightGBM** | **X: existing exact central** |
|---|---|---|
| central | `E_L42` = the seed-42 CV, reproduced across file, driver and run to 1.4e-11 (§3.2). Not quoted; a re-quote is Joseph's decision | `E_C` `142a45b0…`, frozen and quoted. Executed bytes unavailable. `random_state=None` (synthetic evidence of seed invariance, §3.3). Environment dates consistent (§3.4). Reproduction unmeasured; nine later driver commits |
| statistical block | **new**: 300 Poisson replicas, VL170's recipe at `--seed 42` (shared 64 threads). They belong to the central's realization family within the 5.8e-9 envelope | **new**: 300 exact replicas (N > 205 for a full-rank `C_S`). 50 replicas cannot resolve a width transfer (§10 stage T) |
| systematic block | **existing, matched by construction**: `purity_newomni`, frozen as the choice (background-aware, native flux, current inputs; its inspection items are in §5). The adopted flux-fixed sweep (background frozen, `P06`) is the documented alternative | **new**: 187 exact universe unfolds plus a CV; or a demonstrated transfer (stage T, §10) |
| seed/ML block | existing seeds 1–10, non-overlapping with `C_S` and with vertical deltas through the binning mechanism (synthetic, §3.3) | `P09b`: XR's X1 arm measures one seed |
| seed-1 stats / seed-42 systematics (`P07`) | **removed by construction**, every block at seed 42. Seed 42 is chosen by matching cost, not by central values: the alternative L1 (VL170 kept plus a new seed-1 sweep) costs 67.6–191.2 admitted node-h for the sweep, against 25.5–93.2 for the seed-42 band | not applicable |
| matching cost (admitted node-h) | **25.5–93.2** | **467–11,005**. This is a forecast: no exact universe unfold has run; universe-file RSS is 65–187 GB under today's driver; prototype 1 needs SB1; the high end uses as-run exact replicas |
| wall per unfold | median 14 min (544–1,900 s, shared 64; speed REPORT §3) | 19.3–19.8 h (full node; shared-QOS wall unmeasured) |
| continuity | changes the quoted central by 0.99 % median per bin (0.136 σ_tot) | keeps it |

No numerical transfer tolerance is set from observed differences. Stage T's tolerance (§10) is declared
before any transfer quantity exists.

## 5. Uncertainty sources and their treatment (item 3)

Treatment codes: **R** recomputed by the reported procedure; **C** conditioned on; **P** propagated
(MAT); **A** approximated or bounded; **—** not covered.

| source | treatment | reusable product | missing matching evidence or new construction | validation of the approximation |
|---|---|---|---|---|
| data statistics | R: Poisson data stream, 300 replicas; purity fixed at its full-data value (VL170 recipe) | VL170 recipe | the seed-42 band (new) | SD (§6). Fixed purity is conditioning: it scales the data-stream σ by the reco-bin purity (median 0.975) |
| signal-MC statistics | R: Poisson MC stream on `w_truth`/`w_reco`; completeness from un-resampled truth (KI-84 fix) | recipe | — | SM (§6) |
| background-template statistics | A: not resampled by production (C03) | — | an analytic bound from the 658,227-row template and the purity (zero compute), or an SM arm that also masks `mc_background` | bound < 10 % of σ_stat in every cell (proposal); otherwise construct a stream |
| background model | P: knob universes vary the background prediction | `purity_newomni` (43 of 44 bands) | inspection of the 62 % Flux-universe change (§3.5); a digest comparison of the universe-weight columns is impossible, because the May file is gone | not validated beyond §3.5 |
| flux | P: 100 PPFX universes with native 1/Φ_u | `purity_newomni` Flux | KI-91 identity receipt (owner: 2D lane, zero compute) | the identity proof, not the Pearson 0.96 correlation |
| targets | P: 1.4 % rank-1, counted once (C Audit 1) | analytic | — | Audit 1 CONFIRMED |
| detector response, weight-only | P: weight universes (MinosEfficiency, GEANT) | sweep | — | §3.6: MinosEfficiency half-difference correlation 0.997 |
| detector response, lateral (event moves) | A: CV-selected shadow support (C05a) | sweep | selection-complete laterals: the 5D `MNV101_ACTIVE_UNIVERSE` loops with a 2D selection and phase-space equality check, C's S-b (it includes its 10 lateral unfolds) | per lateral, σ against the shadow σ; replace if they differ by > 10 % of σ_tot in any cell (proposal) |
| interactions | P: GENIE/FSI knob universes, response and background together (C06) | sweep | the omitted reproducible displacements of 6 bands (§3.6) | report A beside the variance and disclose its size |
| flux × muon-energy (X01) | A: the rank-2 fallback (`rederive_flux_muonE_cross.py` route B) with its transfer assumption stated, or a disclosed omission | script | coherent joint throws need the unbuilt M1 generator | not validated; disclosed |
| training randomness | P: `C_ML` (seed arbitrariness) | seedscan | the cross-sweep non-reproducibility of small bands (§3.6), mechanism unknown | disclosed with its measured size; no subtraction |
| regularization / model dependence | — in `C_tot`; B± is a nonprobabilistic development envelope beside it | closures in 2D STATUS "Validation" | 2D truth maps for the successor's GENIE+MEC and NuWro truths (location unverified) | **NO UNTOUCHED VALIDATION DOMAIN** (§7) |
| response departures outside the family | — (C10) | — | no method | declared assumption |

`C_tot` stays a block sum.
- X01 is handled by the fallback.
- The seed overlap with `C_S` and with vertical deltas is absent through the binning mechanism (synthetic
  evidence).
- §3.6 is measured and disclosed, with no claimed mechanism.

## 6. Per-experiment reporting procedure, and alternatives to full nesting (item 4)

**The reported procedure on the real data, one experiment:**
- one central unfold;
- 300 bootstrap replicas, each recomputing the unfold;
- the universe deltas against the matched CV, propagated by MAT;
- `C_ML` from the existing scan;
- the analytic norm term;
- B± reported beside the result.

A fully nested validation would repeat all of this inside every pseudo-experiment. C prices that as P1, at
0.29–1.21 million admitted node-h, and it would still need independent populations.

**Two affordable alternatives, tied to existing inputs:**

1. **Split-sample width calibration (SD/SM) of the statistical block, on the real data.**
   - **SD.** Split the 4,091,707 in-phase-space data rows into two halves by a salted hash.
     - Each half is a Bernoulli thinning, hence an independent Poisson sample at exactly half exposure,
       normalized at POT/2.
     - The split is a 0/1 multiplier on the retained rows; no row is dropped. The binning sample (§3.3)
       and the bin mappers are therefore those of the full input, matching the fixed-seed bootstrap's
       conditioning.
     - A bin-mapper digest of each masked input against the unmasked one is a pre-run check.
     - Both halves use the full-data purity per reco bin, again the band's conditioning.
     - Over R random splits, mean (U_A − U_B)²/2 measures the half-exposure sampling variance with no
       resampling model, truth or reservoir.
     - It does so *conditional on* bin mappers and row-count constraints shared through the retained
       zero-weight rows. That is the same conditioning as the fixed-seed bootstrap, so the estimates of
       the two halves are not fully independent, even though their samples are.
     - It is compared with M data-only bootstrap replicas of one half.
   - **SM.** The same for the signal MC: a 0/1 mask on `mc_signal_reco` rows (MC/data 2.354 per half,
     MC POT/2), with `--bootstrap-streams mc` on one half and the real data in both arms. In split mode,
     completeness comes from the masked `mc_signal_reco` truth, misses included (the Phase-17 bijection,
     c ≡ 1), because the trees are not row-aligned.
   - **What it validates.** The width of each stream at half size, on the real operating point. It does
     not test bias or truth coverage. Both streams' claims extend to full size by the bootstrap's 1/n
     scaling, which is an assumption.
   - **Exposure, per role (to be bound in the equivalence test).**
     - SD: data-side normalization and the final division use data POT/2; the signal-MC and background
       scaling use the production `pot_scale` recomputed with data POT/2; purity is computed once from
       the full, unmasked data and background.
     - SM: the signal-MC scaling uses MC POT/2; the background template and purity keep full exposure and
       are computed before masking; completeness is c ≡ 1 from the masked `mc_signal_reco` truth; the
       final division uses the full data POT.
     - The helper does not normalize class totals (`reweight` = p/(1 − p)). Each choice above must
       therefore be checked against the driver's `get_pot_scales` and `fill_bkg_reco_2d` paths.
   - **Implementation.** Two driver options (`--data-split`, `--mc-split`), byte-identical when unset,
     with an equivalence test. The driver is claimed by no lane; its owner and the
     `verify_hash_bindings.py` exception are needed.
   - **KI-85.** SD answers KI-85's question on real data, so it is KI-85-adjacent and needs Joseph's
     explicit ruling.
2. **Structure checks in place of nested systematic recomputation.**
   - The MAT propagation of `C_U` is the declared convention. Its approximation errors are measured on
     existing products at zero compute, where a measurement exists:
     - pair displacement A and its reproducibility, for the 42 pair bands only (§3.6). Flux and the
       multi-universe bands have no such measurement, and A has no pass/fail rule; it is reported;
     - the Flux identity (KI-91);
     - selection-complete lateral support (S-b).
   - The control is §8's criteria. A failure rebuilds the component, or narrows the claim and discloses
     it.

A fixed transferred band (C's P2) answers a different question: whether one frozen band covers pseudo-data
drawn from the declared law. It is not proposed (§7).

## 7. Populations and identities (item 5)

- **What one MC production supports.**
  - B's count is right for B's design: zero disjoint pairs of a production-size bank and a data-size
    reservoir. It is not universal.
  - A width calibration needs one disjoint pair at a time: two half-banks of 2.354 each, or two
    half-data samples.
  - Each random split contributes one degree of freedom. The average over R splits is exchangeable, not R
    independent experiments.
  - The SE formula treats the splits as independent draws, which is exact for a linear statistic and an
    assumption here. The self-test checks only the formula's arithmetic, not this premise.
- **Identity.**
  - Data rows are distinct events; (run, subrun, gate) is not an event key.
  - MC rows are deduplicated events: Phase 18.2 removed 133 truth and 7 reco duplicates on the packed ID.
  - Overlay dependence between halves is untestable, as in B.
  - R0 (an identity-carrying rebuild) is not needed for SD or SM. It is needed for any reservoir design.
- **Why no empirical total coverage.**
  - With f_s at median 0.0084, a total-interval coverage experiment mostly tests the systematic block
    under the declared law.
  - Pseudo-data from the sweep's own universes reproduce the band by construction.
  - New continuous throws need the unbuilt M1 generator, and PPFX has a fixed set of 100 throws.
  - Pseudo-data drawn on the training events are circular in the MC stream (PREREG A1.3).
  - Repeated sampling from this inspected finite bank therefore cannot validate the total
    unconditionally. **NO-GO for the empirical total-coverage claim**, as C found, now with this reason.
  - What can be measured is listed in §6, alternative 2. It is a partial linearity measurement with no
    pass/fail rule for A.
- **Model allowance.**
  - Every truth available for 2D is either inspected development evidence or inside the covariance:
    - Tune v1 and the STATUS closures (gauss_pt, tilt_pz, dpT, MaCCQE:0, Flux:50);
    - the s5p P1r–P3r ratios;
    - the knob universes, which are in `C_U`.
  - The 2D ancillary holds only the Tune v1 prediction.
  - **NO UNTOUCHED VALIDATION DOMAIN** for B±, so B± is a development envelope.
  - Lifting this needs new simulation for a named design: truth-level samples from independent generators
    (e.g. GiBUU, NEUT), applied by truth-ratio reweighting. Analyst time and generator setup are
    unpriced; compute is ASSUMED ≤ 50 CPU node-h.
- **Response tests.** None exist outside the simulated family (C10). Declared.

## 8. Proposed criteria and assurance (item 6)

All criteria are proposals, frozen here, and all inspected cases are development evidence. SD and SM run on
the production data and MC: no recipe choice may follow their outcome, and each has one final look.
- **Family F** is frozen as the 16 paper `GlobalID`s (0-based) [1, 2, 11, 13, 14, 15, 31, 47, 63, 79, 95,
  111, 143, 159, 179, 216]. They have f_s ≥ 0.05 with VL170, `purity_newomni` and `C_ML`
  (`per_cell.frozen_family_F`). The new seed-42 band will move f_s; the family does not move with it.
- **Kurtosis** comes from the 100 VL169 toys: median 0.02.

| criterion | rule (proposed) | assurance |
|---|---|---|
| R, reproduction (XR) | max over the 205 cells and the integral of \|x_new/x_ref − 1\| ≤ 1e-8, on identical cell sets | measured envelopes: 5.8e-9 cross-thread (max of 300), 1.4e-11 cross-file. The exact backend is single-threaded and expected bitwise. No observed pair exceeds 0.58 of the tolerance |
| M, matching | every block's CV equals the central to ≤ 1e-8; identical cell sets (refused otherwise by `reported_cells.py`); recipe identical except the seed | deterministic |
| **W-declared** (SD, SM; the PASS basis) | each of the 236 functionals × 2 streams (m = 472): accept \|ln κ̂\| ≤ 0.168, with κ̂ = σ_split/σ_boot | R = M = 540: familywise false-fail ≤ 0.05 at κ = 1; per-functional pass probability ≤ 0.10 at κ = 0.8 or 1.25 (`declared_family_per_functional`). The SE formula is an assumption (§7) |
| W-regional (the narrower alternative, §2) | per stream × region (F; the other 189), 4 tests at Bonferroni 0.0125. FAITHFUL if the interval of the median ln κ̂ lies inside [ln 0.80, ln 1.25]; FAIL in that direction if it lies entirely outside; else INCONCLUSIVE. The interval is a 98.75 % percentile bootstrap over the splits and the replicas jointly, 2,000 resamples | R = M = 239, sized with n_eff = 3 (F) and 5 (rest), both assumed and capped at the region size. P(all four FAITHFUL \| κ = 1) = 0.95. At κ = 0.63 (KI-85 size), P(FAIL-low) ≥ 0.995. At κ = 0.8 or 1.25, P(FAITHFUL) = 0.006 and INCONCLUSIVE 0.988. At R = 100, P(all four FAITHFUL) would be 0.13 |
| K3-stat (descriptive) | Q_r = d_rᵀ(2Ĉ_half)⁻¹d_r over splits, against the Hotelling reference | declared tier only (M = 540 > 205) |
| systematic structure | Flux identity proved (KI-91); selection-complete lateral σ within 10 % of σ_tot of the shadow σ in every cell; background bound < 10 % of σ_stat in every cell; A reported beside the variance (no rule) | deterministic reads |
| accuracy / bias | no verdict: **NO UNTOUCHED VALIDATION DOMAIN** (§7). B± is reported as a development envelope | — |
| usefulness | median relative I68 half-width ≤ 10 % and 90th percentile ≤ 25 %, with half-width = (upper − lower)/2 **including B±**; integral ≤ 10 %; median B± ≤ 5 % (successor §5) | **INCONCLUSIVE** until B± and the integral exist. From σ_tot alone: median 6.87–6.94 %, p90 11.6–11.9 % |
| missing results | infrastructure failure: ≤ 3 identical-seed reruns. Numerical failure: one rerun, then the functional counts against the test. > 1 % missing, or a verdict that differs between all-hit and all-miss imputation: INCONCLUSIVE. XR: §10 | — |

**Relation to the 0.63 / 0.92 proposals.** They are lower bounds for direct coverage counting, equivalent
to κ ≤ 1.116 (I68) and κ ≤ 1.120 (I95) on the under-coverage side. This route counts no coverage, so they
are context, not rules. κ ∈ [0.80, 1.25] spans I68 coverage 0.789 to 0.576 and I95 coverage 0.986 to 0.883.

No statistical-only result here may become a total-uncertainty claim.

## 9. Prices (item 7)

**Convention.** Admitted = runs × rate × 1.15 / 0.8: a 5 % retry and a 10 % verification rerun inside
the subtotal, then a protected 20 % reserve.
- Units: CPU node-h; core-h = 128 × node-h (two 64-core EPYC 7763 per node); A100-h is 0 throughout.
- Rates (`costs.rates_node_h`):
  - LightGBM CV-file unfold: 0.0591 (shared 64, 300 measured) or 0.216 (full node, 1 measured);
  - LightGBM universe-file unfold: 0.7075 (374 measured);
  - exact CV unfold: 0.666 packed (forecast), 0.905 on shared at `--mem 24G` (12/256 billing), or 19.31 as
    run;
  - exact universe-file unfold: 0.667 (prototype 1) / 2.83 / 4.95 / 9.91 (forecasts by RSS).

| item | admitted node-h (opt – cons) | depends on |
|---|---|---|
| **XR** (next experiment, §10) | expected subtotal **2.83** (2.83 / 0.8 = 3.54); request = hard cap **6.375** from job limits, including one rerun of each kind; 58.1 if the exact jobs needed full nodes | shared-QOS memory billing; unmeasured shared-node wall |
| L42 matching: the seed-42 band (300 runs) | 25.5 – 93.2 | nothing new |
| L1 alternative: the seed-1 sweep (188 universe-file runs) | 67.6 (prototype 1, needs SB1) – 191.2 | SB1 for the low end |
| **L42 complete**: matching, S-b with its laterals, 6 B± unfolds, SD/SM | declared tier (3,240 SD/SM runs) **303 – 1,131**; regional alternative (1,434 runs) 149 – 570 | S-b 1.3–23.8 (C, billing assumed) |
| X matched construction: 300 exact replicas + 188 exact universe unfolds | 467 – 11,005 (packed replicas with today's driver: 1,052–2,964) | exact-universe RSS unmeasured; SB1/prototype 1 for the low end |
| **X complete**, same items at exact rates | declared tier **3,576 – 101,147**; regional 1,848 – 51,011 | as above; 19.3 h per unfold |
| XR stage T (conditional, §10; 16 exact universe-file unfolds) | 15.3 – 227.8 (forecast) | exact-universe RSS |
| fallbacks named in §10 | the seed-42 band on the universe file 305.1; a 10-seed exact scan 9.6 (packed) / 13.0 (`--mem 24G`) | — |

- **Comparators, not ceilings.** The `m3246` CPU balance was 3,040.6 node-h (iris, 2026-10-09T06:15Z, B);
  re-measure before any admission. The annual allocation is 20,000.
- **X against L42.** At the same tier, X costs 11.8–89× L42.
- **SB1 sensitivity.** L42 runs no universe-file unfold, so its price depends neither on SB1 nor on speed's
  I/O finding. X's sweep moves between 180 (prototype 1, forecast) and 765–2,677 admitted (today's driver).
  SB1 itself is 1.3 node-h, capped at 2.0.
- **Storage.**
  - L42 reads the 2.14 GB CV omnifile.
  - Outputs are 0.06 MB per unfold, so 3,240 SD/SM runs make ≈ 0.19 GB.
  - Stage T reads the 171 GB universe file.
  - No CFS copy of the CV omnifile is recorded here. Make one (2.1 GB) before admission, since `/pscratch`
    is purgeable.
- **Identity construction** is not needed for L42 or XR (§3.1, §7).
- **Independent verification** is a local recomputation of every comparison from the outputs (0 node-h),
  plus the 10 % rerun already priced.

## 10. The next experiment: XR, reproduction of both candidate centrals (item 8)

**Questions.**
1. Can the available code, environment and inputs regenerate the quoted exact central to 1e-8? If not,
   is the failure in today's driver?
2. Does the exact backend depend on its seed? Run X1 answers this; it is a one-seed `P09b` (below).
3. Does a CV-file LightGBM run reproduce the seed-42 realization that both existing sweeps share, and the
   seed-1 seedscan central?

**Why this experiment.**
- Every route-discriminating unknown sits on the X side; L42's central reproducibility is already
  evidenced (§3.2).
- The keep-and-disclose central needs a reproducibility statement whichever route is chosen.
- It is the cheapest measurement that can retire route X.
- No tolerance is fitted to an observed difference.
- N2 is not proposed. Its held-out data-stream diagnostic bears on a block carrying a median 0.84 % of a
  cell's variance; SD answers the same question on real data, without R0.

**Launch.**
- Every run uses the canonical checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, whose helper both
  drivers import (§3.4).
- The checkout is moved to the pinned XR commit only after the checks under "Before the move" below.
  `git rev-parse HEAD` is recorded.
- Each run is
  `python3 nd-unfolding/mnv_guarded_run.py --expect-root /pscratch/sd/j/josephrb/MINERvA-OmniFold --inventory <record>/inventory.jsonl --label XR-<run> -- <driver> <args>`
  (the guard's flags are `--expect-root`, `--allow`, `--inventory`, `--label`, then `--`).
- X0′'s driver is the `d1bc8813` blob, committed as a record file under the XR record directory. It imports
  today's helper, so X0′ isolates driver drift only. Helper drift remains A's static argument ("unchanged
  in effect").
- **Working directory and paths.** Every run uses `2d-unfolding/` as its working directory, so the
  relative `--mcfile baseline_flux/…` resolves. Drivers are given by absolute path.
- **Outputs.** Each run writes to an explicit, distinct `--out <record>/XR-<run>.root`. The central
  launcher's own `--out` is *not* reused: it is the quoted product `E_C`. A pre-run check refuses any run
  whose `--out` resolves to an existing file or to `2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root`.
- **Before the move.** `squeue` shows no pending **or running** job using the canonical tree, and its
  `git status --porcelain` is empty. Both are recorded, then checked again after the move.

| run | driver and arguments | hardware | reference |
|---|---|---|---|
| X0 | today's driver, the central launcher's estimator arguments (`--omnifile <CV> --mcfile baseline_flux/runEventLoopMC_MEFHC.root --iters 5 --use-weights`; no `--estimator`, no `--seed`), with `--out <record>/XR-X0.root` | shared, `-c 2`, `--mem 24G`, 30 h limit | `E_C` `142a45b0…` |
| X0′ | the `d1bc8813` driver, same arguments, `--out <record>/XR-X0p.root` | same | `E_C` |
| X1 | X0 plus `--seed 1`, `--out <record>/XR-X1.root`: **a one-seed `P09b`** | same | X0 |
| L0 | today's driver, `--estimator lgbm --seed 42`, CV file, `--out <record>/XR-L0.root` | shared 64, 1 h limit | `4f5a1b6d…` and the `purity_newomni` CV |
| L1 | today's driver, `--estimator lgbm --seed 1`, CV file, `--out <record>/XR-L1.root` | shared 64, 1 h limit | seedscan seed 1 `d7fe901f…` |

**Manifest.**
- Before submission the record pins: the commit; the CV omnifile `43f8cc16…` and its CFS copy; the flux
  file (digest to be measured); the helper `e96234124a31…` as found in the canonical tree; both driver
  blobs; the `root_6_28` versions (sklearn 1.8.0, LightGBM 4.6.0, numpy 1.26.4) and the `threadpoolctl`
  output.
- After each run it records: the output's `runConfig`, argv and digests (today's driver only), the guard
  inventory, and `sacct` State, Elapsed, MaxRSS and billing.

**Criteria.** A comparison passes if all 205 cells and the integral agree to ≤ 1e-8 relative on identical
cell sets. The maximum absolute difference is always reported.

**Failures.**
- One rerun is allowed per kind, within the cap.
- A run still missing, or one exceeding its time limit, makes that comparison INCONCLUSIVE, with no
  substitution.

**Outcomes and the decision each changes.**

| outcome | meaning | decision |
|---|---|---|
| X0 pass | today's code and environment regenerate `E_C` | X keeps a reproducible central. With X1 below, Joseph chooses L42 (re-quote; 303–1,131 to completion) or stage T (15–228) to see whether X can borrow L42's systematic block, once stage T's assurance is computed (N1). The keep-and-disclose text may say the quoted central is reproducible |
| X0 fail, X0′ pass | today's driver changed the exact path | `E_C` is reproducible at its own driver revision. X remains possible, pinned to `d1bc8813`, and the drift is diagnosed before any X construction. `P09b` for that pinned path stays open: the `d1bc8813` driver has no `--seed` option, and X1 runs today's driver |
| X0 fail, X0′ fail | not reproducible by any available code path. The cause lies in helper drift, environment drift or unrecorded run conditions, and cannot be separated | route X **FAILS** the "reproducible central" requirement with the available means; recommend L42. The interim text must say the quoted central could not be regenerated |
| X1 fail (X0 pass) | the exact backend is seed-dependent; `E_C` is one unrecorded draw | X needs a seed policy and a 10-seed exact scan (9.6–13.0 admitted): X dominated, recommend L42 |
| L0 fail | contradicts §3.1–§3.2 | stop and diagnose the driver revision before building the seed-42 band. The fallbacks are that band on the universe file (305.1) or L1 |
| L1 fail (L0 pass) | the seedscan seed-1 central is not reproducible | L1 and any reuse of VL170 are retired; L42 is unaffected |
| a comparison missing or over its limit | — | INCONCLUSIVE for that question only |

**Stage T** is preregistered here but is not part of the request. A separate authorization releases it,
and only after X0 or X0′ passes.
- **Runs.** Exact universe-file unfolds of:
  - 10 Flux throws, ordered by `int(sha256("xr-T" ‖ u)[:8], 16)`;
  - both universes of Muon_Energy_MINOS, MinosEfficiency and Muon_Energy_MINERvA.
- **Tolerance, declared before any transfer quantity exists.**
  - Replace the tested bands' widths in `C_tot` by the exact ones: pair half-differences, and the Flux
    width scaled by the paired ratio √(Σδ_X²/Σδ_L²) over the 10 throws.
  - Evaluated in this order:
    1. **INCONCLUSIVE** if a leave-one-throw-out jackknife's 98.75 % interval for the Flux ratio straddles
       the tolerance edge in any cell, whatever η is;
    2. otherwise **PASS** iff max |η| ≤ 0.05 and median |η| ≤ 0.02, which keeps I68 coverage within
       0.659–0.707 and I95 within 0.938–0.961;
    3. otherwise **FAIL**.
- **Assurance: not quantified.** η = 0 holds only if the two estimators' deltas were identical universe by
  universe. Whether they are is unmeasured: no exact universe unfold has been run.
  - *Corrected 2026-10-10 by the follow-up integration (`integration-followup/REPORT.md` §3), and not part of
    either review. This bullet continued: "Two different estimators cannot meet that null: their centrals
    already differ by median 0.136 σ_tot." That inference, carried over from the re-review's N1 rationale, is
    invalid. A difference of central values does not imply different nuisance deltas: a constant additive
    offset c between the estimators (x_u^X = x_u^L + c for every universe and the CV) shifts both centrals
    apart by c and cancels in every delta δ_u = x_u − x_CV.
    The 0.136 σ_tot is therefore no evidence about the deltas in either direction. The conclusions below do
    not rest on it: the transfer stays unmeasured, and stage T's assurance stays unestablished. In the next
    bullet, §3.6 compares two LightGBM sweeps. It shows that cross-sweep delta scatter exists for LightGBM;
    no between-estimator scatter has been measured (follow-up review F2).*
  - Under the decision-relevant null (the widths transfer within tolerance), η carries between-estimator
    scatter from 10 throws and 3 single pairs. §3.6 shows such scatter exists. Its false-fail rate is not
    quantified, and neither is the power.
  - XR does not establish the determinism of exact universe-file runs.
  - Stage T is therefore not preregistration-ready for a verdict. Its assurance must be computed, for
    example from a model of the per-universe scatter, before stage T is offered as a decision option.
- **Coverage of the test.** The tested bands carry median 86 % of a cell's variance (min 24 %). A PASS
  covers the rest only by assumption, and that must be disclosed.
- **The statistical block is not in stage T.** With 50 exact against 300 LightGBM replicas, the regional
  rule would return FAITHFUL under a perfect transfer with probability only 0.43 (F) and 0.84 (rest)
  (`stage_T.T_stat_*`). X's statistical block must be the matched 300-replica band.

**What XR cannot authorize.** A re-quote, a band replacement, a transfer claim, a KI-85 lift, N2, an
adoption or a changed gate.

**Remaining authorization (Joseph).**
- **Compute.** ≤ 6.4 CPU node-h on `m3246` (four exact jobs, including one rerun, ≤ 1.41 each; three
  LightGBM jobs ≤ 0.25 each; 2.8 expected). 0 GPU. ≈ 20–30 h wall.
- **A ruling on the prohibition.** X1 is a one-seed `P09b`, and `P09b` belongs to DELIVERY §6 option (b),
  "measure the transfer". The 2026-10-09 ruling prohibits that, so X1 runs only if he authorizes it
  specifically. Without that ruling, XR runs X0, X0′, L0 and L1, and the X1 rows stay open.
- **The deployment.** Moving the canonical checkout to the XR commit.
- **The record.** One owner and one fresh reviewer.

## 11. Proposed register and routing changes (for the integration owner; not applied)

1. **`KNOWN_ISSUES.md` 88, append:**
   *"2026-10-10 (`state/next-preparation-20261009/two-d-path/REPORT.md`): the design proposes route L42 —
   LightGBM seed 42, whose CV realization both existing seed-42 sweeps share (reproduced to 1.4e-11) — with
   a new seed-42 statistical band (25.5–93.2 admitted node-h; complete route 303–1,131). The next
   experiment XR (≤ 6.4 node-h) tests whether the quoted exact central can be regenerated; its X1 arm is a
   one-seed P09b and needs a specific ruling. Nothing is authorized; no number changes."*
2. **New `KNOWN_ISSUES.md` row (LOW, owner: 2D lane), descriptive:**
   *"2D universe sweeps: of 42 ±1σ pair bands, 6 carry a reproducible one-sided displacement of median
   0.13 σ_tot (max 0.63). The MAT pair convention omits it, and it is not reported. In 36, the band deltas
   do not reproduce between the adopted and the July seed-42 sweeps. The non-reproducible variance is a
   median 2.5 % of a cell's total and exceeds it in one cell; the cause is confounded (background
   treatment, the 2026-07-08 omnifile regeneration, the driver revision) and unknown. Rvn1pi and Rvp1pi
   are equal to ≈ 1e-9 in both sweeps. Route: two-d-path REPORT §3.6."*
3. **C's assessment, Audit 4 (annotation):**
   *"Synthetic evidence (two-d-path §3.3): LightGBM's seed acts through the 200,000-row binning sample.
   Fixed-seed bootstrap and weight-only universe runs share bin mappers, so that mechanism gives no
   seed-noise overlap with C_S or with vertical deltas. The cross-sweep non-reproducibility of small bands
   (§3.6) has no established mechanism."*
4. **A's `pairings.tsv` `P07` (annotation):**
   *"Avoidable by construction for a seed-42 estimator: both seed-42 sweeps share one CV realization
   (1.4e-11), and the CV-level arrays of the two omnifiles are row-identical (two-d-path §3.1–§3.2)."*
   **`P06`:** *"A background-aware seed-42 sweep exists (`uq/purity_newomni/`, 187/187, native flux,
   background varies in 43 of 44 bands)."*
5. **B's DESIGN §1, ground 1 (scope note):**
   *"The zero count applies to production-size outer coverage experiments. A split-sample width
   calibration needs one disjoint half-size pair at a time (two-d-path §6–§7)."*
6. **2D STATUS (one line under the Stage-2 envelope):** the row identity of the CV-level columns of the two
   omnifiles, and the existence and properties of `purity_newomni`.
7. **CATALOG:** the two-d-path route stands. If XR is admitted, add its record under § Current work.

## 12. Verification and review

- **Self-checks.**
  - `design_arith.py --self-test` PASS, 16 checks. They are arithmetic and internal-consistency checks
    only: they include the T/0.8 reserve with a ×1.2 negative control, the coverage inversions, the
    regional verdict probabilities and design monotonicity. They do not test the split-sample premise
    (§7).
  - `design_arith.json` is regenerated from the committed operands.
  - `seed_mechanism_check.py` exited 0.
- **Initial review.**
  - Reviewer: one fresh read-only Claude Opus 5.5 subagent (not cross-provider) at `ebcba79c`,
    05:17–05:33Z. Its worktree was empty at start and end and was then removed.
  - Preserved verbatim: `review/review.md` (sha256 `a95a66eb…`).
  - **Verdict FAIL.** It found 9 MATERIAL and 14 MINOR/NOTE findings, and reproduced every number.
- **Repair batch.** One batch, in the commit carrying this section. Dispositions:

  | finding | disposition |
  |---|---|
  | F1 | §3.6, §5 and §11 restated as confounded non-reproducibility with unknown mechanism; the double-count claim removed; inflation formula 1/√(1−s) − 1, with the s ≥ 1 cell named |
  | F2 | SD/SM specified as 0/1 masks on retained rows (bin mappers unchanged, digest pre-check) with full-data purity |
  | F3 | a declared-family tier (236 functionals × 2 streams) is the PASS basis and is priced; the regional tier is an explicit narrower alternative |
  | F4 | regional tier sized at its declared level, with verdict probabilities at κ = 1, the edges and 0.63; n_eff capped; interval construction specified |
  | F5 | stage T restricted to the deterministic systematic arm; the statistical transfer shown unresolvable with 50 replicas |
  | F6 | X0′ (the `d1bc8813` driver) added, with its outcome rows, and an L1 row added |
  | F7 | X1 named as a one-seed `P09b`, with a specific authorization request |
  | F8 | cap raised to 6.375, including one rerun of each kind, at a 30 h limit |
  | F9 | every price under one convention, with as-run replicas in X's conservative figure |
  | F10 | κ = 0.63 (2 cells) |
  | F11 | wall figure sourced; the 0.99 % is a JSON field |
  | F12 | usefulness is INCONCLUSIVE |
  | F13 | family frozen as 16 GlobalIDs; `purity_newomni` chosen |
  | F14 | guard command corrected |
  | F15 | accuracy row added |
  | F16 | linearity stated as partial, with no rule |
  | F17 | "synthetic" qualifier added throughout |
  | F18 | self-test described as arithmetic only; split kurtosis factor 1 + γ/4 |
  | F19 | duplicate lateral unfolds removed |
  | F20 | Rvn1pi/Rvp1pi equal in both sweeps |
  | F21 | extrapolation stated for both streams |
  | F22 | CV42 dispersion and the cost-based seed choice disclosed |
  | F23 | none |

- **Focused re-review** (the one allowed). Same reviewer, at `0a2e0f41`, 05:41–05:47Z, worktree empty at
  start and end. Preserved verbatim: `review/review-cycle1.md` (sha256 `8788f23c…`).
  - **Verdict PASS WITH CHANGES.** F1–F23: 20 RESOLVED; F2, F5 and F6 PARTIAL; none UNRESOLVED. Every
    moved number reproduced.
  - **New findings.** Two are MATERIAL:
    - N1: stage T's "false-fail 0" holds only under a degenerate null;
    - N2: XR's manifest reused the central launcher's `--out`, which would overwrite `E_C`; it had no
      distinct outputs or working directory, and no running-job check.
  - Five are MINOR or NOTE:
    - N3: dependence through shared mappers;
    - N4: exposure per role;
    - N5: stale JSON field;
    - N6: `P09b` open for the pinned path;
    - N7: the helper-origin evidence.
  - The owner's byte comparison confirms the preserved initial review is identical to the reviewer's
    returned text, which settles the one item the reviewer could only check by reading.
- **Post-review edits.** These are **not re-reviewed**; no cycles remain.
  - N1: stage T's assurance is withdrawn and the verdict precedence fixed. Stage T is not
    preregistration-ready for a verdict.
  - N2: distinct outputs, a refusal check, the working directory and pre-move checks.
  - N3–N7: one sentence each. N5: the JSON range now prices the universe arm only, 15.3–227.8.
  - Residuals of F1 (the s ≥ 1 cell identified) and F13 (a frozen fallback for the systematic block).
  - No number moved except the N5 field.
- **Commits.**
  - `ebcba79c`: freeze, initial review.
  - `0a2e0f41`: repair batch, re-review.
  - `b38c909c`: post-review edits and the preserved re-review. Its message is malformed ("Checks: 13
    passed", no trailer) because the owner omitted the message body. It is left as pushed, not rewritten
    (no force-push); this note is its description.
  - The commit carrying this line: the delivery record.
- **Gates.**
  - The pre-commit hook passed (13 checks) on every commit.
  - `generate_manifest.py --check` is OUT OF DATE only because of this lane's new files: it is OK at the
    base `a16d5786`. The integration owner regenerates the manifest (DISPATCH rule).
- **Delivery.** Draft PR #69.

## 13. Limitations

- **Seed mechanism.** §3.3 is synthetic and small. It has not been confirmed at production scale.
- **§3.6.** These are single-realization per-cell estimates. Their causes are confounded, and the
  universe-weight columns of the May file cannot be compared.
- **Split-sample.** The independence of random half-splits and the n_eff values are assumptions. Kurtosis
  comes from 100 toys. The half-to-full extrapolation is assumed for both streams.
- **Exact backend.** Every exact-universe price is a forecast. The shared-QOS wall time and contention of
  a single-threaded exact unfold are unmeasured.
- **Not computed here.** The integral's width, B± and the background-template bound.

## 14. Resources

| item | measured | cap |
|---|---|---|
| active time | 2026-10-10, first tool call ≈ 04:20Z (worktree created 04:33:53Z) → delivery ≈ 2026-10-10T05:51Z, about 2 h including both reviews | 8 h |
| local CPU | ≈ 0.03 core-h (seed check 24 s user; arithmetic < 1 s per run; git and hooks) | 3 core-h |
| reviewer CPU | < 0.02 core-h over both cycles (its own figures; 05:17–05:33Z and 05:41–05:47Z) | (included) |
| threads | 2 | 2 |
| peak RAM | 0.34 GB | 8 GiB |
| scratch | ≈ 25 MB (LightGBM venv 23 MB, JSON copies; reviewer 32 KB) | 2 GiB |
| tracked | ≈ 1.9 MB (operands 1.6 MB) | 10 MiB |
| Perlmutter | login node only, read-only: 9 runs of 3 scripts, ≈ 5.6 min wall at ≈ 95 % of one core, ≤ 1.4 GB RSS, plus `ls`/`stat` reads. The first run failed after 23 s on a char-branch conversion. Five runs used earlier script versions that were later extended or made digest-only; their extra fields (data-tree values and sums, one reco-cell data count) were not committed, and every retained field is identical (`logs/`). No job, no allocation charge | 0 node-h |

## 15. Disposition

| decision | disposition | reason |
|---|---|---|
| a complete route for declared claims | **PASS: L42** | matched by construction at seed 42; the central reproduced across files, drivers and threads (§3.1–§3.2); every source has a treatment and evidence (§5); criteria and assurance frozen over the declared family (§8); complete for 303–1,131 admitted node-h |
| exact-central route X | **INCONCLUSIVE** | `E_C`'s reproducibility, its seed dependence and the exact-universe memory are unmeasured. On current forecasts its matched construction costs 467–11,005 admitted node-h and its completion 3,576–101,147. XR retires X or keeps it |
| empirical total-interval coverage | **NO-GO** | §7: circular in the declared law; no production-size independent populations for the MC stream; only a partial linearity measurement remains |
| model-dependence validation stage | **NO-GO** | no untouched domain (§7); B± is a development envelope |
| next experiment | **PASS: XR** | preregistration-ready (§10) after the N2 manifest repair, which is not re-reviewed; every outcome changes a named decision; ≤ 6.4 node-h; its X1 arm needs a specific ruling. Stage T is **not** preregistration-ready for a verdict (N1) |
| publication-ready measurement | **NOT ACHIEVED** | nothing here is executed or adopted |

## 16. Next action

Joseph decides three things. None needs compute until he authorizes it.
1. **The claim scope (§2).**
   - Accept the per-functional statistical width claim and the convention-defined total with a
     development-envelope B± (complete for 303–1,131 admitted node-h);
   - or the narrower regional alternative (149–570);
   - or require empirical total coverage, which is NO-GO until new populations or a validated generative
     law exist.
2. **XR.** ≤ 6.4 CPU node-h, guarded, with a deployment of the canonical checkout, and a specific ruling
   on its one-seed `P09b` arm.
3. **After XR.** Route L42 (a re-quote, then completion), or, if keeping the quoted central is worth its
   price, stage T (15–228 admitted) once its assurance is computed (N1).

The integration owner applies §11 if it is accepted. The 2D lane owns KI-91, the background bound, the
62 % Flux-universe change, the §3.6 pair-band question and Rvn1pi/Rvp1pi.
