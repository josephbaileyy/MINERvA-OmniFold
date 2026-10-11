# 2D follow-up: what the proposed calibration supports, and XR (central reproduction)

**CITABLE FOR:**
- Task A: the derivation of the split-sample (SD/SM) target, and the analytic and synthetic controls
  with known answers;
- the read-only resolutions of the Flux-background anomaly, the cross-sweep pair changes and the
  duplicate bands;
- the admission matrix;
- Task B: the XR package, its admission evidence, its scheduler record, the refusal of all five runs
  by the package's own allocation check (B7), the comparisons' INCONCLUSIVE outcomes, and the XR
  reopening requirements (§E.3).

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- a re-quote, an adoption, a narrowed claim or a changed gate;
- seed invariance in general, or a resolution of the 2D pairing issue;
- an uncertainty transfer between estimators;
- compute authority beyond the recorded XR grant.

The original publication objective is retained. **Publication readiness is not achieved.**

| field | content |
|---|---|
| `Lane` | `two-d-followup` (2D methodology and XR owner; registered by the follow-up integration, §8 of its report) |
| `Decision` | Task A: what does the proposed SD/SM calibration actually support, and does the original objective have a feasible route under current inputs? Task B: do the available code paths regenerate the quoted exact central and the seed-42/seed-1 LightGBM centrals to 1e-8, and does one exact-backend seed comparison agree? |
| `Branch` / `Base` / `Head` | `prep/two-d-followup-20261010` / `016265cceadbd0f38de31e7f4956377f3d3c5e82` (`origin/main`, PR #72; no newer delta at 19:5xZ) / the commit carrying this revision; pins in §B1 |
| `Owned files` | `Q/two-d-followup/` (this report, `methods/`, `xr/`, `logs/`, `review/`); `docs/orchestration/AUTHORIZATION-20261010-xr.md` and its scoped registration (one `MANIFEST-overrides.tsv` row, one `CATALOG.md` row) |
| `Pinned inputs` | §1 |
| `Resources` | §C |
| `Review` | §B4, §B6, §B8 |
| `Model / effort` | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §D |
| `Next action` | §E |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `T` = `Q/two-d-path` (immutable); `F` = this directory.

## 0. Setup

- **Roles.** One owner, and one fresh read-only reviewer for this assignment: one admission review of
  the method and the frozen XR package, one final numerical verification, and at most one focused
  repair and re-review in total. No other agent and no peer message.
- **Verdicts.** The two tasks have separate verdicts. An unresolved method does not block a correctly
  admitted reproduction.
- **Budget.** 10 active hours, 4 local core-hours, two local threads, 8 GiB, 3 GiB new scratch,
  ≤ 20 MiB tracked. XR: ≤ 6.4 charged CPU node-h on m3246, zero GPU, a stop at 72 h after the first
  submission.

## 1. Baseline and inputs

- `origin/main` = `016265cc` (PR #72), with no newer delta.
- Read:
  - `AGENTS.md`, the campaign review, `CURRENT_WORK.md`;
  - `Q/integration-followup/REPORT.md`, including its §3.1 correction of the stage-T inference;
  - `T/REPORT.md`, the operands, and both reviews;
  - the SB1 package and its run record on `run/sb1-20261010` (`f7135d31`), for deployment
    coordination.
- The two-d-path evidence is used as is and not edited.

---

# Part A — what the proposed calibration supports

## A1. The objective, retained, and four claims that must not be merged

The objective stays as Joseph stated it: *a publication-ready measurement with a reproducible central
estimator, matched uncertainty construction, and validation supporting the claims actually made*.
That means all 205 cells, the integral and the projections, with total uncertainties that the
publication may use as intervals and covariances. Four different statements are involved, and the
two-d-path design (`T/REPORT.md` §2) let the first stand in for the second:

| notion | what it asserts | what can establish it |
|---|---|---|
| **conditional width agreement** | a resampling width (the bootstrap) equals the variance of the *same* estimator under a stated conditioning: one fixed MC bank, fixed bin mappers and row structure, fixed purity, half exposure | split-sample comparisons on the one production (SD/SM). Proven for linear statistics; empirically controlled in toys for the estimator's structure (A2, A3) |
| **repeated-sampling coverage** | over new data **and** new MC productions, I68/I95 cover the population truth at the nominal rate | independent productions, or a validated generative law; no route with current inputs (`T` §7; A5) |
| **nuisance-law assumptions** | the MAT universes represent a declared nuisance law, and the propagation through the estimator is adequate (linear enough, complete support, all sources) | structure checks on existing products (A4); a coverage test under the same law cannot test the law itself |
| **model / regularization bias** | the unfolded value's bias at the true (unknown) truth is within an allowance | closures at development truths only; no untouched domain (`T` §7) |

Any narrower claim built from the first row is a **proposal for Joseph** (A5), not the endpoint.
Disclosing that the second, third and fourth rows are untested does not discharge them.

## A2. What SD/SM targets: the derivation

**Setup.** The data rows i, with weights w_i, are fixed (the one observed data set D; likewise the
one MC bank S for SM). A split is complementary 0/1 masks m_i ~ Bernoulli(1/2) (a salted hash), with
the half estimates

  U_A = 2·U(w·m), U_B = 2·U(w·(1−m)).

The factor 2 is the POT/2 normalization. Every row is retained with zero weight, so the bin mappers
and LightGBM's row-count constraints are those of the full input (`T` §3.3, synthetic). Purity is
MC-derived and is held at its full-bank value in both halves. The production MC bootstrap must hold
it fixed in the same way: if a replica recomputed purity while SM held it fixed, the two would
target different conditional variances and their ratio would not test the bootstrap.

**For a linear statistic** T(w) = Σ w_i x_i, with x fixed by the mappers and purity
(`methods/analytic_checks.py`, all 2^12 masks enumerated, exact):

1. E_m[(U_A − U_B)²/2 | D] = 2 Σ w_i² x_i². The split target **given D** is the delete-half
   (jackknife) variance at half exposure. It is a function of the one observed D.
2. Var_m(U_A | D) = Σ w² x² = −Cov_m(U_A, U_B | D). **Given D the two halves are perfectly
   anticorrelated** (corr −1): they are not two experiments.
3. The masked Poisson(1) bootstrap of a half has the same target, 2 Σ w² x². So **κ = 1 identically**
   for any linear statistic. For a correctly implemented bootstrap the test therefore has power only
   against the estimator's non-linear response: tree splits, the instability of A4 item 3,
   iteration. It also detects implementation defects, such as a stream left unresampled or
   correlated replicas.
4. Over **new productions drawn as a Poisson process** the halves are independent by thinning,
   each with variance 2·E[Σ w² x²]. The split's expectation over productions is therefore the true
   half-exposure variance at fixed mappers. This was checked by Monte Carlo against the known
   answer.
   - **The production model matters.** A fixed-N MC bank (multinomial) gives anticorrelated halves,
     Cov(U_A, U_B) = −Nμ² with μ the per-event mean of w·x (Cov(T_A, T_B) = −Nμ²/4 before the
     factor 2). For a non-normalized linear statistic the split target then
     overstates the half variance: the reviewer measured E[split]/true = 1.508 (theory 1.500).
   - MC-scale-invariant functionals, such as the shape cells after the per-replica normalization,
     are unaffected at first order. Normalization-sensitive functionals, such as the integral, are
     not. Data are Poisson; the MC bank's production model must be stated for SM.

**What more splits cannot remove.** As R → ∞ the split statistic converges to 2 Σ w² x² for the
observed D (and to the corresponding function of S for SM), not to its expectation over productions.
The remaining difference is a finite-sample error of the one data set or bank, of relative size
~ 1/√n_eff per functional. Neither more splits nor more replicas reduce it.

**The conditioning, stated exactly.** SD/SM with masks targets

  Var(U_half | fixed mappers, row structure, purity, S [SD] or D [SM]),

which is also the fixed-seed bootstrap's conditioning. A genuine new production changes the rows,
so it re-draws the 200,000-row binning sample and the mappers. **Its repeated-sampling variance
contains a binning component that neither SD/SM nor the bootstrap sees.** SD/SM agreement therefore
validates the bootstrap *as an estimate of that conditional variance*. It does not validate the
repeated-sampling width of the production estimator, and still less coverage.

**The seed-variation block for a fixed-seed estimator.**
- At fixed data, a new seed re-draws the binning sample from the same rows. `C_ML` therefore samples
  binning variability, which is one candidate for the component above.
- It equals that component only if seed-induced and data-induced binning variability have the same
  distribution, and C_S + C_ML is a valid sum only if the two do not interact. **Neither is
  established.** The synthetic mechanism shows *where* the seed acts, not that the blocks are
  independent, and A3 measures the question only in a toy.

**Proven, empirically controlled, assumed.**

| statement | status | basis |
|---|---|---|
| halves of a new production are independent; SD's expectation over productions is the half-exposure variance at fixed mappers (linear T) | **proven for a Poisson production** (data); for a fixed-N MC bank, false for normalization-sensitive functionals (split/true 1.5 for a non-normalized sum) | thinning; `analytic_checks.py`; review A-1 |
| given D, corr(U_A, U_B) = −1 and κ ≡ 1 for linear T | **proven** | exact enumeration |
| the masked design's conditioning equals the fixed-seed bootstrap's | **proven for the toy; synthetic evidence for LightGBM** (weights do not move bin mappers, `T` §3.3) | — |
| the SE formula for ln κ̂ with R splits and M replicas: its split (R) and replica (M) χ² terms | **empirically controlled (toy)** | A3 C5 |
| the finite-sample error of the one data set or bank (the term more splits cannot remove) | **not tested.** It cancels in ln κ̂, because split and bootstrap target the same D-dependent quantity; the formula has no such term (γ = 0) | derivation above; review A-2 |
| κ̂ is unbiased when the bootstrap is right | **empirically controlled (toy)** | A3 C3, C5 |
| half-to-full scaling by a factor 2 | **not established as exact**, by the analytic argument that the binning component does not scale with exposure. The toy's precision cannot resolve it (1.62–2.01, each ±0.23) | A2; A3 C4 |
| bootstrap + `C_ML` ≈ repeated-sampling variance of the fixed-seed estimator | **assumed** (toy: consistent within ±8 %; A3 C1, C1B) | — |
| toy behaviour transfers to 5-iteration LightGBM OmniFold on production inputs | **assumed** | none available |
| SD/SM agreement implies calibrated repeated-sampling widths or coverage | **false as an inference** | derivation above |

## A3. Controls with known answers (`methods/`)

**Analytic** (`analytic_checks.py` → `results/analytic_checks.json`; exact enumeration of 4,096 masks,
plus 20,000 Poisson-process productions). For a linear statistic:
- split target / 2Σw²x² = 1.000000;
- corr(U_A, U_B | D) = −1.000000;
- masked-bootstrap target / 2Σw²x² = 1.000000;
- over productions, the halves have corr 0.004 (SE 0.007) and variance / known answer 0.990.

All four identities of A2 hold.

**Synthetic, no training** (`synthetic_controls.py` → `results/synthetic_controls_{A,B}.json`).
- **The toy.**
  - Bin edges are quantiles of a seeded binning sample of all retained rows, ignoring weights, as
    LightGBM's are.
  - A per-bin data/MC ratio reweight is pulled to truth: a one-step unfold, invariant to the MC
    weight scale.
  - 20,000 expected data events, MC/data 4.7, 16 bins.
  - The known answers are Monte Carlo variances over 300 independent productions at fixed seed, with
    relative SE 8 %.
- **The two configurations.** A uses a 400-row binning sample; B uses a 60-row sample, deliberately
  binning-sensitive.

| control | A (400-row sample) | B (60-row sample) | reading |
|---|---|---|---|
| C1: bootstrap (data + MC) / true repeated-sampling variance | 0.931 | 0.907 | the fixed-row bootstrap misses part of the variance, more when binning matters, within the ±8 % precision |
| C1: (bootstrap + seed block) / true | 0.943 | 0.948 | the seed block moves toward closing the gap (seed share 1.2 % and 4.1 % of the true variance). **Consistent, not established** |
| C3: κ̂ of masked split against masked bootstrap, data / MC | 1.008 / 0.994 | 1.006 / 0.996 | the two estimate the same conditional variance, as derived |
| C4: half / full variance, data stream | 1.78 | 1.88 | each ≈ ±0.23, within 1–1.7σ of 2 |
| C4: half / full variance, MC stream | 1.88 | 1.62 | the same. A and B share production seeds, so they are not independent, and the reviewer's 60-production subset gives MC 2.01. **The toy cannot resolve a departure from 2.** That the factor is not exact rests on the analytic argument (A2) |
| C5: sd over productions of ln κ̂ (R = 40, M = 60), data / MC, against the formula 0.145 | 0.149 / 0.146 | 0.150 / 0.141 | the formula's split and replica terms hold within ≈ 4 %. The finite-sample term cancels in ln κ̂ and is **not** tested here (A2 table) |
| C6: corr of the halves over splits, given the production | −1.0 | −1.0 | the halves are anticorrelated given the data, as derived (exact here because the toy is linear in the data weights) |

**Limits.**
- The toy is a single-step, binned-ratio estimator. The production estimator is 5-iteration
  LightGBM OmniFold, with the trainer instability measured in A4 item 3.
- The toy can test *formulas and conditioning*. It cannot test the production estimator's
  non-linear response, which is exactly where A2 says SD/SM has its only power.
- The 1.2–4.1 % seed shares are smaller than production's σ_ML²/σ_S², median 0.07 (`T` §3).
- Under the stated limits, the toy supports no conclusion about block independence.

**The exact backend's seed path** (from the XR test fixture, B1). With ties, `random_state=None` makes
sklearn's exact backend irreproducible run to run (33 %), while seeded runs are bitwise identical.

## A4. Read-only resolutions (saved products and construction code only)

All reads are login-node reads of saved products, with no event loop, unfold or training:
`methods/remote_probe.py` and three short ad hoc reads, whose outputs are quoted below, in
`logs/remote-reads.txt` and in `methods/results/remote_probe.json`.

1. **Rvn1pi and Rvp1pi are one shift counted twice, by MAT construction.**
   - Their weight columns in the current universe omnifile are byte-identical: `w_truth_Rvn1pi_i` and
     `w_truth_Rvp1pi_i` in `mc_signal_reco`, and the `w_bkg_` pair in `mc_background`, for i = 0, 1.
     The sha256 of the float64 arrays match.
   - The cause is in `MINERvA101/MAT-MINERvA/universes/GenieSystematics.cxx:658–671`
     (`GenieRvx1piUniverse::GetGenieWeight`). With the MINERvA Tune v1 non-resonant-pion reweight
     on, every event with `IsNonResPi` (either knob's weight < 1) gets the same constant
     `kNonResPiWeight ± kNonResPiWeightShift` in **both** bands.
   - So the adopted `C_U` sums one shift twice. It is a 0.088 % band, so the variance effect is
     negligible, but the construction defect is real. Whether the published analysis did the same
     is outside this evidence.
2. **The adopted (May) sweep's universes were unfolded on a different MC truth input from their
   matched CV.**
   - In `uq/universe_sweep_fluxfix/…EtaNCEL_0.root` against `CV42`, every reco-level saved input is
     identical (`hBkgReco2D`, `hDataReco2D`, `hMeasSub2D`, `hMeasTrain2D`, `hEff*`,
     `hOFTruthDenom2D`).
   - But `hTruth2D` and `hOFInputTruth2D` differ in all 205 cells: integral ratio 0.879, median
     6.3 %, maximum 37 %.
   - EtaNCEL is a no-op knob: in the current file `w_truth_EtaNCEL_*` equals `w_truth` exactly. So
     the May universe path did not reproduce the CV's truth input.
   - EtaNCEL_0 and MaNCEL_0 are identical to each other (2.6e-12; their pair displacements differ by
     at most 2.9e-10 σ_ML) and both differ from CV42 by median 0.98 σ_ML (max 1.8 % per cell).
   - That common offset correlates 0.68 with the common mode (cell-wise mean) of all 37 vertical pair
     displacements, and 0.64 with the mean of the other 35. In the July sweep the same correlation is
     0.13. It cancels in the band-mean-centred MAT variance to first order, but the adopted CV is not
     the universes' zero point.
   - Producer: `methods/a4_pair_offsets.py` → `methods/results/a4_pair_offsets.json`, from the
     immutable `T/operands/remote_reduce{,_pairs,_pn}.json` (digests recorded in the output).
   - The July sweep does not have this defect: its EtaNCEL_0 reproduces its CV to 3.0e-7. The May
     file and code revision are unavailable, so the cause cannot be pinned further.
3. **The cross-sweep pair changes are, in large part, an instability of the fixed-seed trainer under
   small input changes.**
   - In the July sweep, EtaNCEL changes the background by 7.9e-6 and the training input by 8.9e-7,
     and moves the output by 3.0e-7: a smooth response.
   - NormNCRES changes only the background, by 2.6e-4 (the training input by 6.3e-5), and moves the
     output by up to 1.47 % (median |A| 0.76 σ_ML; `results/a4_pair_offsets.json`).
   - The response therefore has a threshold: once split choices flip, an output change of seed-noise
     size follows. Together with item 2's common offset, this is **consistent with**, for the two
     universes examined (EtaNCEL, NormNCRES), the non-reproducible part of the 36 small pair bands
     (`T` §3.6) arising without a background-model effect. It does not establish that for the other
     bands.
   - It is evidence, not a proof of mechanism. Its consequence for the construction is that small
     `C_U` bands carry trainer-instability variance of the same order as `C_ML`. That is a modelling
     question for the uncertainty owner, not a number to subtract.
4. **The Flux-background "62 %" is a large high-energy PPFX excursion, not a file defect.**
   - The change is in reco cell (12, 14) (p_T 1.5–2.5 GeV/c, p_∥ 20–40 GeV/c), for universes 65, 93,
     38, 27 and 23, with +75 %, +62 %, +60 %, +55 % and +55 %. The median universe's maximum change is
     15 %.
   - `w_bkg_Flux_65 / w_bkg` reaches 4.87, with 17,437 background rows (2.6 %) above 2. In the median
     universe (18) the ratio stays in 0.20–1.35.
   - This is consistent with a PPFX throw raising the high-energy flux tail that this corner
     samples. **Not established:** that the signal weights of universe 65 carry the matching
     excursion. The next read is `w_truth_Flux_65 / w_truth` against true E_ν, which is not in the
     omnifile and needs the flux identity below.
5. **Background-template statistics at reco level** (bin errors of the July CV's `hBkgReco2D`, ratios
   only).
   - The template's statistical error against the data's Poisson error, eB/√D, has median 0.072, p84
     0.125 and maximum 0.30, and exceeds 0.1 in 60 of 205 bins.
   - Against the subtracted yield the error is median 7.7e-4, but 0.108 in one low-purity bin.
   - The two-d-path proposal "< 10 % of σ_stat in every cell" therefore **fails** in 60 bins at reco
     level. A template stream, or a bound propagated through the unfold, is required; this is not a
     disclosure item.

**Missing evidence, specified (no construction here):**

| item | missing evidence | how to obtain it | blocks |
|---|---|---|---|
| selection-complete laterals (C05a) | that the 5D `MNV101_ACTIVE_UNIVERSE` per-playlist loops apply the 2D selection and phase space; that their CV-level columns equal the 2D CV file row for row (the §3.1 digest test of `T`); the events that migrate in and out per lateral universe; a finite-support closure | a column-digest read and a cut-by-cut comparison of the two event-loop configurations, then lateral unfolds under a separate authorization | the lateral bands (Muon_Energy_MINOS 2.3 %, Muon_Energy_MINERvA 1.3 %, MuonResolution, BeamAngleX/Y) |
| flux identity (KI-91) | that universe u in `hFluxUniv` and in `w_*_Flux_u` index the same PPFX throw | a code-path proof: both built from the same `FluxReweighter` universe index in the event loop and in `build_flux_universe_band.py`. Plus a numeric check: for each u, the integrated weight ratio over a flux-dominated population against Φ_u/Φ_CV | the Flux band (5 %, the largest), and item 4's signal-side check |
| background-template statistics (C03) | a stream or a propagated bound in the unfolded cells | an SM-type arm that masks `mc_background`, or the reco-level bound propagated through the response | 60 reco bins (item 5) |

The old background-frozen sweep is **not** a complete construction substitute. It carries item 2's
input mismatch and `P06`'s omission.

## A5. Admission matrix (all 205 cells, the integral and the 30 projections; no scope change)

| claim component | supported now | remaining assumption | required evidence | minimum next decision |
|---|---|---|---|---|
| reproducible central | seed-42 LightGBM realization reproduced across file, driver and threads (1.4e-11; ≤ 5.8e-9) by existing products | the exact central's environment and seed path | XR (Part B) | none: XR is authorized |
| matched systematic block (`C_U`) | `purity_newomni` is matched to the seed-42 CV and background-aware; the adopted sweep is **not** matched at the input level (A4 item 2) | that small-band deltas are physics rather than trainer instability (A4 item 3); Rvn1pi/Rvp1pi counted once; laterals complete; flux identity; template statistics | A4's "missing evidence" table; a decision on how trainer instability inside `C_U` is to be treated | Joseph: whether to commission the construction repairs (no compute is authorized now) |
| per-functional statistical width, **conditional** (fixed bank, mappers, purity; half exposure) | nothing is measured yet. SD/SM are specified, and their formulas are controlled in a toy (A3) | that the toy transfers to the production estimator; the half-to-full extrapolation (toy: not a factor 2) | SD/SM at the declared tier, plus a binning-component control (for example, SD repeated at a second seed) | Joseph: whether a conditional-width statement is acceptable as an *additional* claim (a proposal, below) |
| repeated-sampling coverage of the statistical intervals | **no route** with current inputs | — | independent MC productions (for the MC stream and the binning component), or a validated generative law | a collaboration-level resource decision |
| total-interval coverage (205 cells, integral, projections) | **no route**: circular in the declared law; the M1 continuous-throw generator is unbuilt; no production-size independent populations (`T` §7) | — | new populations, an M1 generator, and a coverage design sized for 236 functionals × 2 levels | the same, plus the method development |
| systematic propagation as a convention (MAT, nuisance-averaged) | the construction exists, with the defects of A4 listed | law adequacy and linearity: 6 bands carry reproducible one-sided displacements (median 0.13 σ_tot), omitted by the convention | A4 items 1–5; reporting A beside the variance | Joseph: whether a convention-level total claim is acceptable (a proposal) |
| model / regularization bias | development closures only | the unknown truth lies within the development set's behaviour | **no untouched domain**: truth-level samples from independent generators (new simulation). A partial, same-generator-family route: truth warps of the current bank, pre-registered and never used in development | Joseph: whether to commission it |
| χ² / simultaneous use | conditional on the convention and on `C_U`'s rank | the same as the two rows above | K3 statistics at the declared tier (descriptive) | follows the above |

**The original objective has no feasible route under current inputs.** The three components that
validation must support beyond the convention are repeated-sampling coverage, total coverage and the
model-bias allowance. Each needs evidence the current inputs cannot produce: independent productions
or a validated generative law, an M1 throw generator, and independent-generator truths.
**Disclosure does not discharge them.** The narrowest change that would reopen it is named in §E.2.

**A proposal for Joseph, not an endpoint.** A scientifically defensible *additional* claim is
available, and it narrows nothing. It would state:
- the per-functional statistical width as a **conditional precision** (fixed MC bank, fixed binning
  and purity), validated by SD/SM at the declared tier, with the binning component bounded by a
  second-seed SD;
- the total as a **MAT-convention propagation** with A4's repairs applied and its assumptions listed;
- no coverage claim, and B± as a development envelope.

It is offered for his decision. The two-d-path L42 program (303–1,131 node-h) is not commissioned,
and nothing here relies on it.

# Part B — XR

## B1. The package (`F/xr/`)

| file | role |
|---|---|
| `xr_run.py` | the guarded wrapper. It runs one frozen run name only. Code is loaded from hashed bytes (`n2/execution.py`), the helper registered as `sys.modules["omnifold"]` **before** the driver, so the driver's rooted `sys.path` insert of the canonical tree never resolves an import. The production driver and the helper are not edited, and the 2026-09-03 ruling stands. Strict provenance, under the OI-136 guard, on the admitted commit. The working directory must be `<checkout>/2d-unfolding`. Outputs are `<outroot>/<RUN>/a<n>/`: lexically equal to their realpath, outside the checkout, the canonical tree and the input directories, not a frozen reference product, and created exclusively. Inputs are hashed at start and end. The admission must name the outroot frozen in `runs.json`. Before any fit, the interpreter, ROOT and six package versions must equal `runs.json`'s frozen environment (exit 6); module origins and threadpoolctl's pools are recorded. Every GBDT `fit` is recorded with class and `random_state`, and a wrong class or seed stops the run before training (exit 6). Afterwards: exactly 10 classifier and 5 regressor fits, the normalization (7 parameters) and the reported cells against the frozen references |
| `record/unfold_2d_omnifold_unbinned_d1bc8813.py.record` | the historical driver, byte-identical to `d1bc8813` (git blob `0f87330b`, sha256 `447288e2…`). It is stored with a non-`.py` suffix because it is a record, not an importable module: `xr_run.py` compiles it from verified bytes, with the helper pre-registered and under the guard. As a `.py` it registered as a new OI-136 fail-open site (inventory 16 → 17, both ratchets red); with the suffix, both ratchets pass (10 and 7 tests). **For the OI-136 owner:** classify execution-only record copies explicitly, rather than rely on the suffix |
| `manifest/runs.json` | the frozen runs: driver, driver digest, argv template, backend, seeds and iterations per run; the inputs (path, size, sha256); the kinds (QOS, CPUs, memory, time, billing cap, attempt cap); the comparisons and the negative control; the 1e-8 criterion; the **outroot** `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010` (independent of HEAD); the grant date; the **environment** (Python 3.11.14, ROOT 6.28/12, numpy 1.26.4, scikit-learn 1.8.0, LightGBM 4.6.0, joblib 1.5.3, threadpoolctl 3.6.0, scipy 1.16.3) and the five nested setup scripts |
| `manifest/references.json` | the four frozen reference products (path, sha256, normalization parameters, the 205 reported GlobalIDs) |
| `manifest/expected-code.json` | sha256 of every package file, the four executed repository modules, the guard and its shim (`xr_admit.py manifest`) |
| `xr_admit.py` | standard library only and Python 3.6-compatible (the launch scripts run it under the cluster's `/usr/bin/python3`, 3.6.15). `manifest`; `check` (the authorization binding: repository-relative, not a symlink, committed, names the package commit (40 hex) and the manifest digest (64 hex) in full; the package unchanged since; clean tree); `draft` (creates the frozen outroot **exclusively** and writes `admission.json` in it, so a second admission for the grant is refused; binds the setup script and its five nested scripts by sha256); `verify` (re-runs `check`, and re-hashes the setup and nested scripts; the admission must be the outroot's own); `jobcheck` (inside a job: QOS, CPUs, billing and time limit read from `scontrol`, against the frozen caps); `next-attempt` (attempts per kind over the grant = the largest of the attempt directories, `submissions.jsonl`, and every `xr_*` job `sacct` lists since the grant date, so failures and cancellations count; refuses a rerun of a completed run, a submission after the stop, and one whose time limit could end past it; prints the stop as Slurm's `--deadline`); `ledger` (charged node-h from `sacct` plus the ceilings of unfinished jobs, against 6.4; flags billing above a cap and unfinished jobs past the stop) |
| `xr_compare.py` | the comparisons: the receipt is complete, names its run, and cites the outroot's own `admission.json` by path and sha256; the output and reference digests match; the histogram axes (bin counts and edges) are equal; the reported-cell sets equal the frozen 205; max \|x_new/x_ref − 1\| over the 205 cells and the area-weighted integral ≤ 1e-8. Every exceeding cell is listed, with the maximum, the median and the integral difference |
| `launch/xr_job.sbatch`, `launch/xr_submit.sh` | one job per run and attempt. The allocation is checked before anything else; the admission is re-verified (binding, clean HEAD, setup and nested digests); the setup is sourced; the wrapper runs under the guard. The submit script takes every `#SBATCH` value from `runs.json`, passes the stop as `--deadline` (Slurm never starts a job that cannot end before it), refuses queued duplicates, appends `submissions.jsonl`, and cancels this invocation's jobs if `sbatch` fails |

**Two wrapper-side measures that change no estimator setting:**
- **LightGBM's core count.** LightGBM's default `n_jobs` asks joblib/loky for a physical-core count,
  and loky obtains it from a child process (`lscpu` on Linux, `sysctl` on macOS). The OI-136 guard
  refuses that child: neither is a leaf tool, and the guard says not to widen its table. This was
  found by the test suite, where L0 and L1 were refused under the guard.
  - The wrapper reads the same number from `/proc/cpuinfo`, or from `sysctlbyname` through ctypes,
    and seeds loky's own cache with it. loky's rule is unchanged: the affinity count when it is
    below the OS count, which is the shared-64 case, else the physical count. The receipt records
    the values.
  - On shared-64 the seed is a **no-op**: joblib 1.5.3 returns the affinity count (64 < 256) before
    any physical-core query (the reviewer read `cpu_count`'s source on the cluster). So it changes no
    estimator setting and no thread count relative to an unguarded run.
  - **Threads differ from the references.** L0 and L1 run with 64 threads; CV42, SEED1 and PN_CV ran
    with 128 (a full regular node, or `srun --cpus-per-task=128`). That is §10's hardware choice, not
    the wrapper's. The only measured thread effect is ≤ 5.8e-9 (VL170 against VL162), close to 1e-8.
    **Pre-registered:** an L-arm FAIL is first examined for a thread-count cause, by its cell pattern
    against that 5.8e-9 prior. It is not attributed to the driver revision without that check, and
    the criterion does not change.
  - **For other owners:** any LightGBM run under the guard without such a seed would be refused when
    loky queries physical cores. That includes SB1's C job, if loky reaches the physical-core query
    there. It is recorded here and not acted on.
- **An exact-backend finding from the tests.** On the synthetic fixture, whose boundary rows create
  ties, sklearn's exact backend with `random_state=None` is **not reproducible run to run**: two
  identical unseeded runs differ by up to 33 %, while seeded runs are bitwise identical.
  - So X0 and X0′ failing to reproduce `E_C` could be caused by unseeded tie-breaking alone, even
    with identical code and environment.
  - It also means X1 (seed 1) and X0 (seed `None`) need not agree even if seeds have no systematic
    effect.
  - The earlier synthetic seed-invariance (`T` §3.3), on continuous features, could not see this.

## B2. Admission evidence (measured 2026-10-10, read-only; `logs/remote-reads.txt`)

- **Allocation.** m3246 had 16,976.9 of 20,000 CPU node-h charged, leaving 3,023.1. The m3246
  association includes the `shared` QOS (MaxWall 2 days).
- **Billing rule.** `shared_milan_ss11` uses CR_CORE_MEMORY with DefMemPerCPU = MaxMemPerCPU =
  1,905 MB, and billing equals allocated CPUs (the reference job `59410433_1`: cpu = 64, mem =
  121,920M, billing = 64).
  - Exact kind: `--cpus-per-task=12 --mem=22860M`, i.e. 12 × 1,905 MB, billing 12/256. The measured
    exact peak is MaxRSS 16,786,760K = 17.2 GB (`E_C`'s job `53116554.batch`,
    `Q/speed/operands/sacct_exact_pilots_ki85_steps.psv` line 3; `Q/speed/REPORT.md` §3).
    - **Deviation from §10, recorded.** §10's literal `-c 2 --mem 24G` would bill 13–14 CPUs under
      CR_CORE_MEMORY with MaxMemPerCPU 1,905 MB (1.52–1.64 node-h per 30-h attempt), and four
      attempts would exceed 6.4. Twelve CPUs at the per-CPU maximum bill exactly what the memory
      needs. The exact backend is single-threaded, so the extra CPUs change nothing in the estimator.
  - LightGBM kind: 64 CPUs and 121,920M, billing 64/256. The measured peak of CV-file LightGBM
    replicas on shared-64 is 14.4–17.2 GB (`59410433`, `Q/speed/REPORT.md` §3).
  - `jobcheck` refuses a job whose actual `scontrol` QOS, CPU count, billing or time limit exceeds
    the kind's frozen value, before any input is read.
    **As deployed it refused every correct allocation too:** it reads a `TRES` field that
    Perlmutter's `scontrol` does not print (B7).
- **Ceiling, from these settings.** 4 exact attempts × 30 h × 12/256 = 5.625, plus 3 LightGBM
  attempts × 1 h × 64/256 = 0.75, gives **6.375 ≤ 6.4** node-h.
  - **What enforces it.** One admission per grant: the outroot is frozen in `runs.json`, and `draft`
    creates it exclusively, so a second admission (and with it a fresh attempt count) is refused.
    Within it, `next-attempt` counts attempts per kind as the largest of three independent records
    (attempt directories, `submissions.jsonl`, and `sacct`'s `xr_*` jobs since the grant date). So
    "one extra exact attempt across all exact arms, one extra LightGBM attempt across both" holds
    even if a directory or the submissions record is lost. Failures and cancellations count.
  - Each attempt is capped by `jobcheck` in the job (billing and time limit), so its charge is at
    most its kind's ceiling. There is no full-node path: the submit script has no QOS other than
    the kind's.
  - **Residual:** a submission made outside `xr_submit.sh`, by hand, is outside this enforcement.
    The operator does not do that; `ledger` would show it.
- **The stop.** `next-attempt` refuses any submission after 72 h from the first, and any whose time
  limit could end past that point. Slurm gets the same point as `--deadline`, so a job still pending
  when it can no longer finish is never started. Running jobs past the stop are cancelled by
  verified id (`ledger` flags them).
- **Runtime headroom.** `E_C` took 69,523 s = 19.3 h on a full regular node (one busy core). The
  exact limit is 30 h. A slower shared node could time out, and one TIMEOUT uses the only spare
  exact attempt.
- **The CV input is protected.** One verified CFS copy, 2,144,008,221 B, sha256 `43f8cc16…` equal to
  the source and to B's digest, mode 0440:
  `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/`. XR reads that copy.
  - Group write was removed from the copy's two directories (`drwxr-s---`, 2026-10-10T21:52Z;
    review B-8). The parent `/global/cfs/cdirs/m3246/josephrb` is group-writable, so the group
    could still rename the directory. A missing or substituted file is refused by the start and end
    hashes.
  - The flux input (5,143 B, `d40aea69…`) is read in place and not copied (not authorized).
    `E_C`, `CV42` and `SEED1` record `baseline_flux/runEventLoopMC_MEHFC.root`, the name before the
    rename in `c7ae2206` (2026-05-28); that file no longer exists. The reviewer compared its content
    on the cluster: `pTmu_reweightedflux_integrated` in the MEFHC file against `hFlux_pt` in all four
    references, 14 bins, max relative difference 0.0 (review B-7).
- **Deployment.**
  - The canonical checkout is not clean (733 status lines), so it **cannot** be moved and is not
    used.
  - XR runs from a new detached worktree at the authorization commit,
    `/pscratch/sd/j/josephrb/MINERvA-OmniFold-xr-<sha8>` (a sibling, not nested under the canonical
    tree, which the guard and `check_out_path` treat as foreign), with the helper pre-registered (the
    reviewed SB1 technique). No checkout is moved.
  - The environment is the canonical checkout's `setup_salloc_env.sh` (sha256 `ea3c6998…`). It
    sources `unbinned_unfolding/build/setup.sh`, which prepends the canonical build directory to
    `PYTHONPATH`. That directory holds `RooUnfold/omnifold.py`, a package submodule, and no top-level
    `omnifold.py`; the helper is pre-registered regardless. The setup and its five nested scripts are
    hashed into the admission and re-hashed in every job.
  - SB1's session runs in its own detached worktree (`MINERvA-OmniFold-sb1-2b35ba52`) and reads the
    universe omnifile. XR reads the CFS CV copy and the flux file, and writes `/pscratch/…/xr-<head>`.
  - There is no shared mutable resource, so concurrent running is safe and no serialization is
    needed. The canonical checkout's environment-setup file is read by both; its digest is bound at
    admission.

## B3. Local verification (synthetic fixture only; no cluster)

Environment: Homebrew Python 3.13.7 with PyROOT 6.36.000, numpy 2.4.6, scikit-learn 1.8.0 and LightGBM
4.6.0 (the cluster's two ML versions), in a scratch venv. `OMP_NUM_THREADS=1`, scratch `TMPDIR`.

- **`xr/tests/test_xr.py`: 32 tests OK, 0 skipped** after the repair batch (`logs/xr-tests.txt`;
  24 at `8378ec23`).
  - All five runs complete under the real guard, in strict mode, with the real driver, the real
    helper and the `d1bc8813` record copy. Each fits its frozen classes with its frozen seeds
    (10 classifier and 5 regressor fits). Normalization and cells equal the references. The X0′
    receipt records the record copy's sha256 and git blob.
  - Fixture comparisons: L0 and L1 reproduce their unwrapped references, and X1 its seeded exact
    reference, exactly in every cell. The negative control (X0 against the LightGBM reference) FAILs,
    as it must.
  - **Refusals (exit 3), all before training:**
    - no guard;
    - an existing output (its bytes preserved);
    - a symlinked attempt directory;
    - an output equal to a frozen reference path;
    - an outroot inside the checkout;
    - the wrong working directory;
    - an unknown run, or an attempt over the cap;
    - a non-admitted admission, or one whose `runs.json` digest differs;
    - a changed driver or helper;
    - an input with other bytes (refused before the receipt is written);
    - an admission naming another outroot (its attempt directory exists and stays empty);
    - a second `draft` for the grant (the first admission is unchanged);
    - `verify` with a changed untracked nested setup script, or with a copied admission.
  - **Refusals (exit 6):** a backend other than the frozen one, a wrong seed, and a package or
    interpreter version other than the frozen one (all before any fit); a normalization that
    differs from the reference; a regressor fit count other than 5.
  - **The binding:** an abbreviated commit, another manifest digest, an absolute path, a path outside
    `docs/orchestration/`, `..`, an uncommitted record, a symlinked record, and a package change
    after the package commit are all refused.
  - **Fake Slurm:** the submit script uses only `--qos=shared` with the frozen CPUs, memory and time.
    It allows exactly 4 exact and 3 LightGBM attempts in total and refuses the next, queries `sacct`
    from the grant date, and passes `--deadline`. A failed second `sbatch` cancels the first job.
  - **`next-attempt`**: four exact `xr_*` jobs in `sacct` (steps and other jobs ignored) exhaust the
    exact cap with no directory; an exact submission at exactly 42 h (42 + 30 = 72) is allowed and
    one second later refused; a LightGBM submission is refused after the stop. The printed deadline
    is the stop in local time.
  - **The comparator**: a receipt naming another run, another admission digest or path, or another
    output digest is not used; different histogram edges are INCONCLUSIVE.
  - **Python 3.6**: `xr_admit.py` parses under `ast.parse(feature_version=(3, 6))` and uses no 3.7+
    `subprocess` keyword.
  - **`jobcheck`** refuses billing 14 at 14 CPUs, billing 13 at 12 CPUs, a regular QOS, a 31 h limit
    and 16 CPUs.
    Every one of these cases used a fixture that prints `TRES=`, and the cluster prints `ReqTRES=`/`AllocTRES=`.
    So none of them tested the real format (B7).
  - **`ledger`** computes the charge exactly, and flags a billing above the cap and an unfinished
    job past the stop.
- **OI-136 ratchets** after the repair batch: 17 passed (rooted-insert 10, fail-open inventory 7).
  `verify_hash_bindings.py`: ALL BINDINGS INTACT.
- **The receipt-binding inventory.** The first commit attempt was refused by the pre-commit
  hash-binding gate: the inventory moved from 144 to 146. `runs.json`'s repository-relative `driver` /
  `driver_sha256` pairs had the shape the verifier harvests as live receipt bindings.
  - They are package pins, enforced by `xr_run.py`'s and `xr_admit.py`'s own checks, not receipts.
    The inventory's constants belong to another owner and say not to be updated to pass.
  - So the key is `driver_digest`. `verify_hash_bindings.py` then reports ALL BINDINGS INTACT.
  - The suite (24 OK) and the `driver-pin-unchecked` mutant (caught) were re-run after the rename.
- **Mutation controls** (`xr/tests/mutation.py`).
  - At `8378ec23` the first run caught 17 of 19. `input-digest-unchecked` (the end-of-run re-hash
    still refused, but only after training on the wrong bytes) and `billing-unchecked` (the only
    billing case also tripped the CPU check) exposed weak tests. Both were strengthened, and a rerun
    caught 2 of 2.
  - **After the repair batch, all 29 mutants** (19 old and 10 new: sacct count, stop, deadline,
    outroot reuse, nested setup, environment, outroot binding, regressor count, receipt binding,
    axes) were run in one pass (`logs/xr-mutation-results.json`, 28:31 wall). **28 of 29 caught.**
    `outroot-unchecked` survived: its test's other outroot had no attempt directory, so the run was
    refused by the directory check instead. The test now creates that directory and requires the
    frozen-outroot message. A rerun caught 1 of 1 (`logs/xr-mutation-results-rerun-outroot.json`),
    and the full suite passed again (32 OK).

## B4. Admission review (use 1 of 3)

The fresh read-only reviewer reviewed the method and the frozen package at `8378ec23`. The review is
preserved verbatim in `review/admission-review-8378ec23.md`.

- **XR: ADMIT WITH CHANGES.** Four MATERIAL findings:
  - B-1: `xr_admit.py` used Python 3.7 `subprocess` arguments, while the cluster's `/usr/bin/python3`
    is 3.6.15;
  - B-2/B-4: the outroot depended on HEAD, so a second admission would reset the attempt count, and
    the 72-h stop was not enforced;
  - B-3: package versions were not frozen, and the nested setup scripts were unbound.
- **Method: PASS WITH CHANGES.** Eight MINOR or NOTE findings (A-1 to A-8), all wording, scope or
  provenance. None changes a conclusion.
- The reviewer reproduced the suite (24 OK), three mutants, the analytic identities, a 60-production
  synthetic rerun, the A4 numbers from the probe outputs, and the cluster facts (environment, billing
  rule, CFS copy, SB1 queue, flux-file content).

## B5. The repair batch (the one allowed)

Every finding was repaired in one batch; the re-review covers all of them.

| finding | repair |
|---|---|
| B-1 | `xr_admit.py` uses only 3.6 `subprocess` arguments and `str.format`. A test parses it with `ast.parse(feature_version=(3, 6))` and refuses 3.7+ keywords. The cluster run of `manifest --check`, `jobcheck` outside a job, `draft` and `verify` under `/usr/bin/python3` is recorded in B7 |
| B-2, B-4 | outroot frozen in `runs.json`; `draft` creates it exclusively (a second draft is refused, tested); `--outroot-base` removed; `next-attempt` counts `sacct`'s `xr_*` jobs since the grant date and refuses past the stop or a limit ending past it (tested at the boundary); `--deadline` passed to Slurm; `xr_run.py` refuses an admission naming another outroot; B2 restated |
| B-3 | interpreter, ROOT and six package versions frozen; `xr_run.py` refuses (exit 6) before any fit on a mismatch (tested for a package and the interpreter); module origins and threadpoolctl info recorded; the setup and five nested scripts hashed into the admission and re-hashed by `verify` in every job (tested with an untracked nested script) |
| B-5 | B1: the 64-vs-128-thread difference, the ≤ 5.8e-9 prior, and the pre-registered thread-cause check |
| B-6 | B2: the deviation from §10's `-c 2 --mem 24G` and its reason; MaxRSS sources cited |
| B-7 | B2: the MEHFC/MEFHC name and the reviewer's content check |
| B-8 | `chmod g-w` on both CFS directories; the parent's group write disclosed |
| B-9 | B2: the worktree path and the TIMEOUT risk |
| B-10 | the comparator checks the receipt's run, admission path and sha256, and equal axes (tested) |
| B-11 | exactly 5 regressor fits (tested) |
| A-1 | A2 item 4 and the status table: the production model, the fixed-N counterexample |
| A-2 | the status table: the R/M terms are controlled; the finite-sample term is untested; C5 relabelled |
| A-3 | the scaling statement rests on the analytic argument; C4 relabelled |
| A-4 | `methods/a4_pair_offsets.py` → `results/a4_pair_offsets.json`. It reproduces 0.68 (0.64 without the two offset universes), 0.98 and 0.76 σ_ML; "explains" scoped to the two universes examined |
| A-5 | §B6–§E written |
| A-6 | the purity wording and the bootstrap's matching condition |
| A-7 | the model-bias row mentions pre-registered truth warps |
| A-8 | the defect-detection wording |

## B6. Focused re-review (use 2 of 3)

At `06eae0fe` (manifest `fbca1be8…`), preserved verbatim in `review/rereview-06eae0fe.md`.

- **XR: ADMIT.** B-1 to B-11 are all REPAIRED, and there is no new MATERIAL defect. Among the
  checks:
  - the reviewer ran `xr_admit.py` under the cluster's Python 3.6.15;
  - it re-measured the frozen environment, the nested-setup chain and its digests, and the CFS
    permissions;
  - it reran the suite (32 OK) and four new mutants (4 of 4 caught).
- **Method: PASS WITH CHANGES.** A-1 to A-4 and A-6 to A-8 are REPAIRED. A-5 (and N-3) remained:
  §B6–§E were not yet written at the fixed commit. They are written here (documentation only; no
  package file changed).
- **New notes, not repaired** (no repair was required for admission):
  - N-1: the stop's start is read only from `submissions.jsonl`;
  - N-2: a refused `next-attempt` leaves the invocation's earlier jobs queued.

## B7. Deployment and the runs

**Authorization and admission** (`logs/xr-deploy.txt`).
- `docs/orchestration/AUTHORIZATION-20261010-xr.md` quotes the grant verbatim (sha256 `4c469151…`)
  and binds package `06eae0fede3508419f235f8cbe61954b33de8497` and manifest
  `fbca1be80d56b09751bcd9f8fbe698ac65786ebe08e21ae04e561e5c73dd06b8`. It is committed at
  `b838fc02d599947858daae4778bb31d1f01f2856` with its two scoped registration rows.
- **Worktree.** At 2026-10-10T22:34:09Z a detached worktree
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold-xr-b838fc02` was created at `b838fc02`, with 0 status
  lines. The canonical checkout stayed at `32e403b8`, and no checkout was moved.
  - The first attempt named the remote `origin`, which does not exist there (it is `github`), and
    failed before any change.
- **Checks under `/usr/bin/python3` 3.6.15 on login23:** `manifest --check` current; `check`
  holds; `jobcheck` outside a job refuses with exit 3. This is the cluster record B5 promised for
  B-1.
- **Admission.** `draft` created the outroot and
  `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010/admission.json` (sha256 `ef8b49b3…`). It binds
  the setup `ea3c6998…` and its five nested scripts. `verify` held, and the ledger was empty.
- **SB1 at submission:** four `sb1_*` jobs PENDING in their own worktree. They share no mutable
  resource with XR.

**Submission** (2026-10-10T22:34:53Z to 22:35:09Z; `xr_submit.sh`, all five in one invocation).

| run | attempt | job | QOS / CPUs / mem / limit | Deadline (PDT) |
|---|---|---|---|---|
| X0 | a1 | 59648608 | shared / 12 / 22,860M / 30 h | 2026-10-13T15:34:49 |
| X0′ | a1 | 59648610 | shared / 12 / 22,860M / 30 h | 2026-10-13T15:34:53 |
| X1 | a1 | 59648611 | shared / 12 / 22,860M / 30 h | 2026-10-13T15:34:53 |
| L0 | a1 | 59648616 | shared / 64 / 121,920M / 1 h | 2026-10-13T15:34:53 |
| L1 | a1 | 59648617 | shared / 64 / 121,920M / 1 h | 2026-10-13T15:34:53 |

The stop is 2026-10-13T22:34:53Z. X0's deadline is 4 s earlier: it was computed before the first
submission was recorded, which is conservative.

**Outcomes: all five runs were refused at start, by a defect in the admitted package.** Nothing was
computed. The record is in `logs/xr-deploy.txt` (OUTCOME), and the job logs, sacct, ledger and
comparator output are in `results/xr/`. The admission itself is not tracked, because it would add receipt
bindings to the shared inventory. `results/xr/README.txt` gives its sha256 and the values it binds.

| run | job | started (PDT) | elapsed | State / exit | refusal |
|---|---|---|---|---|---|
| X0 | 59648608 | 2026-10-10T15:45:15 | 19 s | FAILED 3:0 | allocation check: `billing` False |
| X0′ | 59648610 | 2026-10-10T15:45:15 | 19 s | FAILED 3:0 | same |
| X1 | 59648611 | 2026-10-10T16:06:03 | 7 s | FAILED 3:0 | same |
| L0 | 59648616 | 2026-10-10T16:35:32 | 7 s | FAILED 3:0 | same (lgbm caps) |
| L1 | 59648617 | 2026-10-10T17:23:52 | 4 s | FAILED 3:0 | same (lgbm caps) |

- **What ran.** Each job's first step is the in-job allocation check (`xr_admit.py jobcheck`).
  - It found QOS, CPU count and time limit within the frozen caps.
  - It found billing `None`, and refused with exit 3.
  - `verify`, the environment check, the loky seed, the guard and `xr_run.py` never ran. No fit
    started and no receipt was written.
- **Root cause.** `jobcheck` reads billing from a field named `TRES` in `scontrol show job <id> -o`
  (`xr_admit.py:241–243`). Perlmutter prints no such field: it prints
  `ReqTRES=cpu=64,mem=121920M,node=1,billing=64` and `AllocTRES=…` (measured on 59648617). The
  billing clause was therefore False on every correct allocation: a fail-closed guard that could
  never pass on this cluster.
- **Why no control saw it.** The suite's fake `scontrol` (`tests/test_xr.py:543`) prints `TRES=`,
  the field name the code expects. So the fixture agreed with the code, not with the cluster.
  The 29 mutants could not detect this, because every check of `jobcheck` was against that
  fixture. Neither review **did** detect it, though a review could have: one read-only `scontrol
  show job <id> -o` on a login node shows the field names (F-1, F-2 of the final verification).
  B7's cluster check ran `jobcheck` only **outside** a job, where it
  refuses before reading the field.
- **No resubmission.**
  - The admitted package (`06eae0fe`, manifest `fbca1be8…`) cannot change, so a resubmission would
    refuse identically and spend the last attempts.
  - A repaired package would be a new, unadmitted package, and this assignment's one
    repair/re-review is spent.
  - The remaining attempts (exact 1 of 4, LightGBM 1 of 3) are left unused.
  - The last job ended 1.82 h after the first submission. The stop (2026-10-13T22:34:53Z) never
    bound, so nothing needed cancelling.
- **What this does not show.**
  - Nothing about any reproduction question.
  - It shows nothing about the parts of the package that never ran inside an allocation: `verify`
    in a job, the environment refusal, the loky seed, the guarded driver import and the regressor
    count.
  - The parts that ran outside a job on the cluster did hold, under `/usr/bin/python3`:
    - `manifest --check`, `check`, `draft`, `verify`, `ledger` (on the real sacct, with
      `AllocTRES` parsed correctly);
    - `next-attempt`, on the real `sacct -X -n -P` output after the failures (`logs/xr-deploy.txt`, last
      entry). It offers each run
      attempt 2 with the deadline at the stop, read-only.

## B8. Comparisons and the independent numerical verification

**Comparisons.** The frozen comparator (`xr_compare.py --outroot /pscratch/sd/j/josephrb/xr-two-d-followup-20261010`,
root_6_28 Python on a login node, 0.13 s) returns, for every comparison and the control:

| comparison | question | outcome |
|---|---|---|
| X0_vs_E_C | today's driver regenerates the quoted exact central | **INCONCLUSIVE** (no complete attempt of X0) |
| X0p_vs_E_C | the `d1bc8813` driver (today's helper) regenerates it | **INCONCLUSIVE** (no complete attempt of X0p) |
| X1_vs_X0 | one-seed P09b: `random_state` 1/2/3 vs `None` | **INCONCLUSIVE** (no complete attempt of X1) |
| L0_vs_CV42 | a CV-file seed-42 run reproduces CV42 | **INCONCLUSIVE** (no complete attempt of L0) |
| L0_vs_PN_CV | the same against the July CV | **INCONCLUSIVE** (no complete attempt of L0) |
| L1_vs_SEED1 | a seed-1 run reproduces the seed-1 central | **INCONCLUSIVE** (no complete attempt of L1) |
| NC_X0_vs_CV42 (negative control) | the comparator must FAIL different estimators | **INCONCLUSIVE**: not exercised (`control_met` false only because nothing ran) |

There are no maxima and no affected cells to report, because no run produced a histogram. The
pre-registered thread-count check on an L-arm FAIL (B1) did not arise.

**Independent numerical verification (review use 3 of 3).** Preserved verbatim in `review/final-verification-eb145ba6.md`. The same
reviewer worked read-only at `eb145ba6`, 2026-10-11T00:33–00:36Z, under 0.01 local core-hours.

- **Method: PASS.**
- **Admission outcome as recorded: CONFIRMED.**
- **Deployment: FAIL CONFIRMED.**
- **All seven comparisons INCONCLUSIVE,** re-derived by rerunning the frozen comparator on the
  cluster.
- **Numerical verification: CONFIRMED WITH DISCREPANCIES.** The discrepancies are documentary.

The reviewer re-measured, among other things:
- sacct;
- all ten job-log digests;
- the absence of any receipt or fit;
- the ledger sum (1,244 / 921,600 = 0.0013498 node-h);
- the attempt counts;
- the stop, and that it never bound (last job ended at 1.8175 h);
- the Perlmutter field names, on another job;
- the in-job step order.

**F-1 (MATERIAL, recorded, not repaired).** The reviewer missed the `TRES` defect in both earlier
reviews, though one read-only `scontrol` read would have shown it. Only `jobcheck`'s `TRES` read was
taken from a fixture rather than the cluster. The other in-job steps are low-risk, but none has run
inside an allocation.

**Post-verification corrections** (documentary only; nothing under `xr/` changed; no further review
is available, so these are not re-reviewed):
- F-2: B7 now says the reviews did not detect the defect, not that they could not;
- F-3: §E.3 item 6 states both ceilings;
- F-4: §C's measured share is now 1.315 h, with the 19-mutant pass marked measured;
- F-5: the `next-attempt` run, its input digest and its outputs are now in `logs/xr-deploy.txt`;
- F-6, F-7 and F-8: added to §E.3 items 1 and 3.

# C. Resources

**Remote (m3246, Perlmutter), from sacct and the frozen ledger** (`results/xr/ledger.txt`, `results/xr/sacct.psv`).

| item | grant limit | used |
|---|---|---|
| charged CPU node-hours | 6.4 | **0.00135** (5 jobs, 4–19 s each, billing 12 or 64 of 256) |
| GPU | 0 | 0 |
| exact jobs | 4, each ≤ 30 h at ≤ 12/256 | **3** (all FAILED 3:0 at start; counted) |
| LightGBM jobs | 3, each ≤ 1 h at ≤ 64/256 | **2** (both FAILED 3:0 at start; counted) |
| full-node substitution | none | none |
| elapsed after first submission | stop at 72 h (2026-10-13T22:34:53Z) | last job ended at 1.82 h; nothing cancelled |

- Every job's QOS, CPU count and time limit were measured by the in-job check and agreed with the frozen caps. The
  allocation's billing (12 and 64, from sacct `AllocTRES`) was inside the cap; only the check's reading of it was
  wrong (B7).
- **Remote storage.**
  - CFS input copy `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/` (2.14 GB, mode 0440,
    directories `g-w`).
  - The detached worktree `/pscratch/sd/j/josephrb/MINERvA-OmniFold-xr-b838fc02`.
  - The outroot `/pscratch/sd/j/josephrb/xr-two-d-followup-20261010` (admission, submissions, 10 job logs).
  - The reduction directory `/pscratch/sd/j/josephrb/xr-reduce.4fPw` (5 small text files).
  - All of these are left in place as evidence; none is shared.
- **Login-node work** (`logs/remote-reads.txt`, `logs/xr-deploy.txt`):
  - read-only reads;
  - the CFS copy and its `sha256sum`;
  - the worktree creation;
  - `manifest --check`, `check`, `draft` and `verify`;
  - after the runs: one `sacct`, one `scontrol`, the ledger, `next-attempt` (read-only) and the comparator.
  - Every step took seconds, except the copy and its hash.

**Local.**

| item | limit | used |
|---|---|---|
| active hours | 10 (last quarter protected) | grant received 19:58:09Z. Counting all wall-clock time as active, including queue waits, about 4.6 h at 00:35Z; the value at delivery is in the commit message |
| local CPU core-hours | 4 | **≈ 2.35**, including the final verification (< 0.01). Of this, 1.315 h was measured and the rest is estimated, as itemized below |
| concurrent compute threads | 2 | ≤ 2 processes, `OMP_NUM_THREADS=1` |
| RAM | 8 GiB | not instrumented; the largest local processes were the unit suite and the synthetic controls on small fixtures |
| new local scratch beyond worktrees | 3 GiB | 202 MiB (`scratchpad/fu/`, incl. the test venv) |
| tracked evidence | ≤ 20 MiB | `F/` 0.56 MiB on disk |

Local CPU items, all `user+sys` unless marked:
- synthetic controls A + B: 0.403, measured;
- one earlier aborted synthetic run: ≤ 0.22, bound from wall time;
- the first 19-mutant pass: 0.374, measured (`user+sys` 1,347 s), and its 2-mutant rerun: ≈ 0.04;
- the 29-mutant pass: 0.518, measured;
- the outroot rerun: 0.020, measured;
- 8 unit-suite runs: ≈ 0.32 (138–159 s each);
- the reviewer: 0.2 + 0.15, as self-reported;
- other (A4 producer, AST checks, git, hooks): ≤ 0.1.

# D. Disposition

Separate outcomes. Each verdict word stands alone, and the line under it says what it covers.

| object | outcome | basis |
|---|---|---|
| **Task A — method** | **PASS** (final verification at `eb145ba6`; the re-review's PASS WITH CHANGES left only A-5, now applied) | derivation, status classification, controls, read-only resolutions, admission matrix |
| Task A — the original objective | **no feasible route under current inputs** (A5); reopening needs new inputs (§E.2) | the admission matrix over all 205 cells |
| **XR — admission review** | **PASS (ADMIT)** at `06eae0fe`, after the one repair batch | `review/rereview-06eae0fe.md` |
| XR — the admitted package in deployment | **FAIL**: all five runs refused at the in-job allocation check by the package's own defect (B7). The admission did not catch a MATERIAL defect | `logs/xr-deploy.txt`, `results/xr/` |
| X0_vs_E_C | **INCONCLUSIVE** | no run completed |
| X0p_vs_E_C | **INCONCLUSIVE** | no run completed |
| X1_vs_X0 | **INCONCLUSIVE** | no run completed |
| L0_vs_CV42 | **INCONCLUSIVE** | no run completed |
| L0_vs_PN_CV | **INCONCLUSIVE** | no run completed |
| L1_vs_SEED1 | **INCONCLUSIVE** | no run completed |
| NC_X0_vs_CV42 (control) | **INCONCLUSIVE** (not exercised) | no run completed |

No scientific status changes. No reproduction question is answered either way. In particular:
- whether `E_C` is regenerable;
- whether `random_state=None` matters on the production input;
- whether CV42 or SEED1 are reproducible.

# E. Next action, reopening requirements and proposed shared-status updates

## E.1 What happens next

Nothing starts automatically. No stage T, statistical-band production, N2, KI-85 lift, re-quote,
adoption, gate change or publication edit follows from this report. The branch is pushed for
review; merging and every status change belong to their owners.

## E.2 The original objective: the narrowest change that would reopen it

Under current inputs the objective has no feasible route (A5). It reopens only with **new inputs**,
not with more compute on the current ones:

1. **Repeated-sampling coverage of the statistical intervals.** Either independent MC productions
   (each a fresh bank, so the binning sample and mappers re-draw), enough to estimate the
   per-functional repeated-sampling variance at the declared tier, or a generative law validated
   against the bank. Only that sees the binning component that SD/SM and the bootstrap cannot.
2. **Total-interval coverage.** A built M1 continuous-throw generator, and populations independent
   of the declared law, with a design sized for 236 functionals × 2 levels.
3. **The model-bias allowance.** Truth-level samples from at least one independent generator, an
   untouched domain. Pre-registered truth warps of the current bank are a partial route only.
4. **The construction repairs of A4,** in any case: Rvn1pi/Rvp1pi counted once; universe and CV on
   one truth input; selection-complete laterals; flux identity; a template-statistics stream or
   bound.

Without items 1–3, the only publishable statement is a different claim (A5's proposal: conditional
precision plus a convention-level total, no coverage). That is a scope decision for Joseph, not an
approved endpoint.

## E.3 Reopening requirements for XR

XR reopens only under a **new or amended grant**. It cannot reopen inside this one:
- the admitted package cannot change;
- the review budget (1 + 1 + 1) is spent;
- the frozen outroot is consumed by design (`draft` refuses an existing one);
- the remaining attempts (exact 1, LightGBM 1) cannot cover five runs.

The exact requirements:

1. **Repair** (`xr_admit.py` `jobcheck`, lines 241–249). Read billing from `AllocTRES`, the allocation actually
   granted, which is always present for a running job. Keep it fail-closed: absent or unparsable means refuse.
   No other field changes. Parse the named key explicitly, not by splitting the whole line on spaces (F-8).
   `ReqTRES` also carries billing; `AllocTRES` is `(null)` until the job runs (F-6).
2. **A fixture from the cluster, not from the code.**
   - The fake `scontrol` in `tests/test_xr.py` must print the recorded Perlmutter field set (`ReqTRES=…
     AllocTRES=…`, no `TRES=`; B7).
   - It needs one test in each direction: a correct allocation in that real format **passes**, and billing over
     the cap refuses.
   - It needs one new mutant (read `TRES` again) that must be caught.
   - Audit every other parser of scheduler output against a recorded real line: `sacct -X -n -P` for
     `next-attempt`, which held on the real output (B7), and the ledger's `AllocTRES`, which held.
3. **An in-allocation preflight** before any frozen run.
   - One shared-QOS job of ≤ 5 minutes, at the exact kind's caps (12 CPUs). It runs `jobcheck`, `verify` and
     `xr_run.py`'s environment check, then stops before any fit.
   - It must pass, and it is counted in the charged node-hours, with its own line in the grant.
   - Its point is to exercise the steps that have never run inside an allocation: `verify` in a job, the
     environment refusal, the loky seed and the guarded driver import.
   - It should go through `xr_job.sbatch` itself (F-7): the setup `source` in the job, the guard, the CFS
     input hash in the job, then `check_environment` and the loky seed, stopping before the first fit.
   - The stop-before-fit mode is new code and belongs to item 4's package.
   - It uses its own outroot or attempt namespace, so it consumes no run attempt.
4. **A new package commit and manifest sha256**, a new frozen outroot (for example `…-20261010b`), and a new
   AUTHORIZATION record binding them.
5. **One independent admission review of the delta** (items 1–4), with its own review budget.
6. **Attempt caps that cover the five runs.** For example, 4 exact and 3 LightGBM again, counted over the new
   grant. The current grant's 0.00135 node-h is already spent.
   - Ceilings (F-3):
     - one attempt per run: 3 × 30 h at 12/256 plus 2 × 1 h at 64/256 is ≤ 4.72 charged node-h;
     - the full caps (4 exact, 3 LightGBM): ≤ 6.375;
     - the preflight: ≈ 0.004.
     - Both fit in a 6.4 node-h grant.
   - The new 72-h window starts at the new first submission.
7. Everything else in the package, and every comparison and criterion (1e-8, the negative control, the
   pre-registered thread-count check), stays as admitted.

## E.4 Proposed shared-status updates, for their owners (not applied here)

| owner / surface | proposed update |
|---|---|
| `KNOWN_ISSUES.md` owner | **New row:** in the current universe omnifile, `w_*_Rvn1pi_i` and `w_*_Rvp1pi_i` are byte-identical (MAT `GenieSystematics.cxx:658–671` under the NonResPi reweight), so `C_U` counts one shift twice (0.088 % band; negligible in variance, a construction defect) |
| `KNOWN_ISSUES.md` owner | **New row:** the adopted (May) sweep's universes were unfolded on a different MC truth input from CV42 (`hTruth2D` integral 0.879, median 6.3 %); the universes' common offset is a median 0.98 σ_ML from the adopted CV. The July sweep does not have this defect |
| `KNOWN_ISSUES.md` / `OPEN_ITEMS.md` owner | the reco-level background-template statistical error exceeds 10 % of the data's Poisson error in 60 of 205 bins (max 0.30). The two-d-path "< 10 % of σ_stat" proposal fails; a template stream or propagated bound is required (C03) |
| `CURRENT_WORK.md` / integration owner | the `two-d-followup` row: method verdict, XR admission and comparison outcomes (§D), the authorization record, and that no follow-on is authorized |
| OI-136 owner | (a) classify execution-only record copies (`*.py.record`) explicitly, rather than rely on the suffix; (b) LightGBM's default core count under the guard reaches loky's `lscpu`/`sysctl` child **only when the affinity count equals the OS count** (a full node). Shared-QOS jobs, including SB1's C, take the affinity branch and are unaffected; a full-node LightGBM run under the guard would be refused without a cache seed like XR's |
| `E_C` / 2D estimator owner | sklearn's exact backend with `random_state=None` is irreproducible run to run when features tie (33 % on the synthetic fixture); how much that matters on the production input is still untested: X0/X0′/X1 did not run (§D) |
| receipt-binding inventory owner (pre-commit hook) | whether to admit `xr-two-d-followup-20261010/admission.json` as a tracked receipt. It adds two live bindings (authorization, setup; 144 → 146). Here it is held off the tracked tree, and `results/xr/README.txt` gives its sha256 and the values it binds |
| two-d-path owner (immutable evidence) | A4 items 2–3 change the reading of `T` §3.6's cross-sweep pair changes; `T` is not edited |
