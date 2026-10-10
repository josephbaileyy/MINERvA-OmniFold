# 2D follow-up: what the proposed calibration supports, and XR (central reproduction)

**CITABLE FOR:**
- Task A: the derivation of the split-sample (SD/SM) target, and the analytic and synthetic controls
  with known answers;
- the read-only resolutions of the Flux-background anomaly, the cross-sweep pair changes and the
  duplicate bands;
- the admission matrix;
- Task B: the XR package, its admission evidence, its scheduler record, its comparisons against the
  frozen 1e-8 criterion, and the independent numerical verification.

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
| `Review` | §B4, §B7 |
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
fixed at its full-data value.

**For a linear statistic** T(w) = Σ w_i x_i, with x fixed by the mappers and purity
(`methods/analytic_checks.py`, all 2^12 masks enumerated, exact):

1. E_m[(U_A − U_B)²/2 | D] = 2 Σ w_i² x_i². The split target **given D** is the delete-half
   (jackknife) variance at half exposure. It is a function of the one observed D.
2. Var_m(U_A | D) = Σ w² x² = −Cov_m(U_A, U_B | D). **Given D the two halves are perfectly
   anticorrelated** (corr −1): they are not two experiments.
3. The masked Poisson(1) bootstrap of a half has the same target, 2 Σ w² x². So **κ = 1 identically**
   for any linear statistic, and the test has power only against the estimator's non-linear
   response: tree splits, the instability of A4 item 3, iteration.
4. Over **new productions** (a Poisson process) the halves are independent by thinning, each with
   variance 2·E[Σ w² x²]. The split's expectation over productions is therefore the true
   half-exposure variance at fixed mappers. This was checked by Monte Carlo against the known
   answer.

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
| halves of a new production are independent; SD's expectation over productions is the half-exposure variance at fixed mappers (linear T) | **proven** | thinning; `analytic_checks.py` |
| given D, corr(U_A, U_B) = −1 and κ ≡ 1 for linear T | **proven** | exact enumeration |
| the masked design's conditioning equals the fixed-seed bootstrap's | **proven for the toy; synthetic evidence for LightGBM** (weights do not move bin mappers, `T` §3.3) | — |
| the SE formula for ln κ̂ with R splits and M replicas, including the finite-sample term | **empirically controlled (toy)** | A3 C5 |
| κ̂ is unbiased when the bootstrap is right | **empirically controlled (toy)** | A3 C3, C5 |
| half-to-full scaling by a factor 2 | **not supported as exact** (toy 1.78 data / 1.88 MC, ±0.2) | A3 C4 |
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
| C4: half / full variance, data stream | 1.78 | 1.88 | not a clean factor 2 (±0.23) |
| C4: half / full variance, MC stream | 1.88 | 1.62 | below 2 by up to ≈ 2σ: **the half-to-full extrapolation is a source of error, not an identity** |
| C5: sd over productions of ln κ̂ (R = 40, M = 60), data / MC, against the formula 0.145 | 0.149 / 0.146 | 0.150 / 0.141 | the SE formula, *including* the finite-sample term, holds within ≈ 4 % |
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
   - EtaNCEL_0 and MaNCEL_0 are identical to each other (2.6e-12) and both differ from CV42 by
     median ≈ 1 σ_ML (max 1.8 % per cell).
   - That common offset correlates 0.68 with the common mode of all 37 vertical pair displacements.
     It cancels in the band-mean-centred MAT variance to first order, but the adopted CV is not the
     universes' zero point.
   - The July sweep does not have this defect: its EtaNCEL_0 reproduces its CV to 3.0e-7. The May
     file and code revision are unavailable, so the cause cannot be pinned further.
3. **The cross-sweep pair changes are, in large part, an instability of the fixed-seed trainer under
   small input changes.**
   - In the July sweep, EtaNCEL changes the background by 7.9e-6 and the training input by 8.9e-7,
     and moves the output by 3.0e-7: a smooth response.
   - NormNCRES changes only the background, by 2.6e-4 (the training input by 6.3e-5), and moves the
     output by up to 1.47 % (median |A| 0.76 σ_ML).
   - The response therefore has a threshold: once split choices flip, an output change of seed-noise
     size follows. Together with item 2's common offset, this explains the non-reproducible part of
     the 36 small pair bands (`T` §3.6) without a background-model effect.
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
| model / regularization bias | development closures only | the unknown truth lies within the development set's behaviour | **no untouched domain**: truth-level samples from independent generators (new simulation) | Joseph: whether to commission it |
| χ² / simultaneous use | conditional on the convention and on `C_U`'s rank | the same as the two rows above | K3 statistics at the declared tier (descriptive) | follows the above |

**The original objective has no feasible route under current inputs.** The three components that
validation must support beyond the convention are repeated-sampling coverage, total coverage and the
model-bias allowance. Each needs evidence the current inputs cannot produce: independent productions
or a validated generative law, an M1 throw generator, and independent-generator truths.
**Disclosure does not discharge them.** The narrowest change that would reopen it is named in §E.

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
| `xr_run.py` | the guarded wrapper. It runs one frozen run name only. Code is loaded from hashed bytes (`n2/execution.py`), the helper registered as `sys.modules["omnifold"]` **before** the driver, so the driver's rooted `sys.path` insert of the canonical tree never resolves an import. The production driver and the helper are not edited, and the 2026-09-03 ruling stands. Strict provenance, under the OI-136 guard, on the admitted commit. The working directory must be `<checkout>/2d-unfolding`. Outputs are `<outroot>/<RUN>/a<n>/`: lexically equal to their realpath, outside the checkout, the canonical tree and the input directories, not a frozen reference product, and created exclusively. Inputs are hashed at start and end. Every GBDT `fit` is recorded with class and `random_state`, and a wrong class or seed stops the run before training (exit 6). Fit counts, normalization (7 parameters) and the reported cells are checked against the frozen references afterwards |
| `record/unfold_2d_omnifold_unbinned_d1bc8813.py.record` | the historical driver, byte-identical to `d1bc8813` (git blob `0f87330b`, sha256 `447288e2…`). It is stored with a non-`.py` suffix because it is a record, not an importable module: `xr_run.py` compiles it from verified bytes, with the helper pre-registered and under the guard. As a `.py` it registered as a new OI-136 fail-open site (inventory 16 → 17, both ratchets red); with the suffix, both ratchets pass (10 and 7 tests). **For the OI-136 owner:** classify execution-only record copies explicitly, rather than rely on the suffix |
| `manifest/runs.json` | the frozen runs: driver, driver digest, argv template, backend, seeds and iterations per run; the inputs (path, size, sha256); the kinds (QOS, CPUs, memory, time, billing cap, attempt cap); the comparisons and the negative control; the 1e-8 criterion |
| `manifest/references.json` | the four frozen reference products (path, sha256, normalization parameters, the 205 reported GlobalIDs) |
| `manifest/expected-code.json` | sha256 of every package file, the four executed repository modules, the guard and its shim (`xr_admit.py manifest`) |
| `xr_admit.py` | `manifest`; `check` (the authorization binding: repository-relative, not a symlink, committed, names the package commit (40 hex) and the manifest digest (64 hex) in full; the package unchanged since; clean tree); `draft`; `verify`; `jobcheck` (inside a job: QOS, CPUs, billing and time limit read from `scontrol`, against the frozen caps); `next-attempt` (counts every attempt directory per kind, so failures and cancellations count; refuses a rerun of a completed run); `ledger` (charged node-h from `sacct` plus the ceilings of unfinished jobs, against 6.4) |
| `xr_compare.py` | the comparisons: the receipt is complete; the output and reference digests match; the reported-cell sets equal the frozen 205; max \|x_new/x_ref − 1\| over the 205 cells and the area-weighted integral ≤ 1e-8. Every exceeding cell is listed, with the maximum, the median and the integral difference |
| `launch/xr_job.sbatch`, `launch/xr_submit.sh` | one job per run and attempt. The allocation is checked before anything else; the environment-setup digest is checked, then the setup sourced; the wrapper runs under the guard. The submit script takes every `#SBATCH` value from `runs.json`, refuses queued duplicates, appends `submissions.jsonl`, and cancels this invocation's jobs if `sbatch` fails |

**Two wrapper-side measures that change no estimator setting:**
- **LightGBM's core count.** LightGBM's default `n_jobs` asks joblib/loky for a physical-core count,
  and loky obtains it from a child process (`lscpu` on Linux, `sysctl` on macOS). The OI-136 guard
  refuses that child: neither is a leaf tool, and the guard says not to widen its table. This was
  found by the test suite, where L0 and L1 were refused under the guard.
  - The wrapper reads the same number from `/proc/cpuinfo`, or from `sysctlbyname` through ctypes,
    and seeds loky's own cache with it. loky's rule is unchanged: the affinity count when it is
    below the OS count, which is the shared-64 case, else the physical count. The receipt records
    the values.
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
  - Exact kind: `--cpus-per-task=12 --mem=22860M`, i.e. 12 × 1,905 MB, billing 12/256, for a measured
    exact peak of 17.2 GB.
  - LightGBM kind: 64 CPUs and 121,920M, billing 64/256, for a measured peak of 14.4–17.2 GB.
  - `jobcheck` refuses a job whose actual `scontrol` QOS, CPU count, billing or time limit exceeds
    the kind's frozen value, before any input is read.
- **Ceiling, from these settings.** 4 exact attempts × 30 h × 12/256 = 5.625, plus 3 LightGBM
  attempts × 1 h × 64/256 = 0.75, gives **6.375 ≤ 6.4** node-h. `next-attempt` enforces "one extra
  exact attempt across all exact arms, one extra LightGBM attempt across both", counting failures and
  cancellations. There is no full-node path: the submit script has no QOS other than the kind's.
- **The CV input is protected.** One verified CFS copy, 2,144,008,221 B, sha256 `43f8cc16…` equal to
  the source and to B's digest, mode 0440:
  `/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/`. XR reads that copy. The flux
  input (5,143 B, `d40aea69…`) is read in place and not copied (not authorized).
- **Deployment.**
  - The canonical checkout is not clean (733 status lines), so it **cannot** be moved and is not
    used.
  - XR runs from a new detached worktree at the authorization commit, with the helper pre-registered
    (the reviewed SB1 technique). No checkout is moved.
  - SB1's session runs in its own detached worktree (`MINERvA-OmniFold-sb1-2b35ba52`) and reads the
    universe omnifile. XR reads the CFS CV copy and the flux file, and writes `/pscratch/…/xr-<head>`.
  - There is no shared mutable resource, so concurrent running is safe and no serialization is
    needed. The canonical checkout's environment-setup file is read by both; its digest is bound at
    admission.

## B3. Local verification (synthetic fixture only; no cluster)

Environment: Homebrew Python 3.13.7 with PyROOT 6.36.000, numpy 2.4.6, scikit-learn 1.8.0 and LightGBM
4.6.0 (the cluster's two ML versions), in a scratch venv. `OMP_NUM_THREADS=1`, scratch `TMPDIR`.

- **`xr/tests/test_xr.py`: 24 tests OK, 0 skipped** (`logs/xr-tests.txt`).
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
    - an input with other bytes (refused before the receipt is written).
  - **Refusals (exit 6):** a backend other than the frozen one and a wrong seed (both before any
    fit); a normalization that differs from the reference.
  - **The binding:** an abbreviated commit, another manifest digest, an absolute path, a path outside
    `docs/orchestration/`, `..`, an uncommitted record, a symlinked record, and a package change
    after the package commit are all refused.
  - **Fake Slurm:** the submit script uses only `--qos=shared` with the frozen CPUs, memory and time.
    It allows exactly 4 exact and 3 LightGBM attempts in total and refuses the next. A failed second
    `sbatch` cancels the first job.
  - **`jobcheck`** refuses billing 14 at 14 CPUs, billing 13 at 12 CPUs, a regular QOS, a 31 h limit
    and 16 CPUs.
  - **`ledger`** computes the charge exactly and flags a billing above the cap.
- **OI-136 ratchets** on the staged tree: rooted-insert 10 passed, fail-open inventory 7 passed.
- **The receipt-binding inventory.** The first commit attempt was refused by the pre-commit
  hash-binding gate: the inventory moved from 144 to 146. `runs.json`'s repository-relative `driver` /
  `driver_sha256` pairs had the shape the verifier harvests as live receipt bindings.
  - They are package pins, enforced by `xr_run.py`'s and `xr_admit.py`'s own checks, not receipts.
    The inventory's constants belong to another owner and say not to be updated to pass.
  - So the key is `driver_digest`. `verify_hash_bindings.py` then reports ALL BINDINGS INTACT.
  - The suite (24 OK) and the `driver-pin-unchecked` mutant (caught) were re-run after the rename.
- **Mutation controls**, measured before the record copy's rename, which touched no mutated anchor (`xr/tests/mutation.py`; `logs/xr-mutation-results.json`, rerun
  `-rerun2.json`).
  - The first run caught **17 of 19**. Two mutants survived, and both exposed weak tests:
    - `input-digest-unchecked`: the end-of-run re-hash still refused, but only after training on the
      wrong bytes;
    - `billing-unchecked`: the only billing case also tripped the CPU check.
  - Both tests were strengthened: the receipt must still be empty at the refusal, and a billing-only
    case was added. A rerun of those two caught **2 of 2**.
  - So every one of the 19 mutants is caught by its targeted test, the two survivors by the
    strengthened tests.

(B4–B8 below)
