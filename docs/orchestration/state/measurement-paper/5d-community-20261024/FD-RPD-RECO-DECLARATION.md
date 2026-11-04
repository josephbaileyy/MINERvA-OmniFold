# DECLARATION: d1 and d2. Reconstruction-level data/MC per playlist, and the flux-swap test (2026-11-04)

**Commissioned by** Joseph, `DECISION-20261104-joseph-referee-analysis-commission.md` item 1 (#759, merged at
`1a87d209a9fc337c49d40ae3114d51312a45e132`; his answer's sha256 begins `1b4d8a744aad9c24`), from the designs
d1 and d2 of `state/2d-closeout/stageF/methods/secondary-results/scope-referee-analysis-20261104/REPORT.md` §5 (#758).

**Owner:** limitation-resolver. **Route:** this declaration, then an audit, then the director's binding, then each
connect's sha256 to the director for a go.

**Frozen before any comparison is read.**
- No ratio, offset or step in this declaration's sense has been computed from these inputs.
  <!-- absence-ok: scoped to the readers of these 24 files: RPD's check and readout read `measured` only to recompute measured_weights and to unfold (nd-unfolding/fd_rpd.py:789-810), and the mwdiag runs compared measured_weights shares; none forms a data/MC ratio -->
- Its recipe, readings and licences change only by a new declaration.

**CITABLE FOR, once run under a binding:** the reco-level per-playlist data/MC offsets and the swap fractions, as
defined here, and the reading each produced.

**NOT CITABLE FOR:**
- which period or which flux is correct;
- a correction or an exclusion (scope §5 d3, not commissioned);
- any change to the result, C_PL,5D or any covariance;
- "validated", "covers" or "coverage".

## 1. Inputs, pinned

**The run-period diagnosis's own per-playlist dumps**, written by its job A 60786801. They are 24 files under
`/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps/`:
- `lat_<PL>.npz` and `lat_<PL>_bkg.npz`, for PL ∈ {1A … 1G, 1L, 1M, 1N, 1O, 1P}.
- The sha256 of each is in `fd/rpd-reco/INPUTS.sha256`, copied from job A's lane logs
  (`fd/receipts-rpd/run/jobA/line*-60786801.log`).
- Every file is checked against its pin before use. A mismatch is a STOP.

**Their weights.** In each `lat_<PL>` the MC weights are already scaled to that playlist's own data POT
(`FD-RPD-DECLARATION.md:288`), so data/MC is absolute per playlist.

**Keys read, and only these:**
- from `lat_<PL>`: `MCreco`, `MCgen`, `w_reco`, `pass_reco`, `measured`, `axes`;
- from `lat_<PL>_bkg`: `bkg_reco`, `bkg_w`.

Each key is read alone. The files hold object arrays (`axes`), so `allow_pickle=True` is used, as in `fd_rpd.load_all`.
Every read is O_NOATIME. The tests must load real `.npz` files in this format (§5).

**d2's flux spectra.** These are the three files that MAT's `FluxReweighter` maps to the playlists:
- 1A–1F → 1D;
- {1G, 1L, 1M} → 1M;
- 1N–1P → 1N.

The mapping is from `FluxReweighter.cxx:1936-1976`, as read in `2d-closeout/playlist-spread-20261014/REPORT.md:154-161`.
- **Pre-binding inventory P0** (login, 0 node-h, read-only). It lists, for each file:
  - its path in the cluster MAT checkout;
  - its sha256;
  - the name and Eν binning of the CV-reweighted flux histogram that `FluxReweighter` applies.

  It also opens each histogram once with the run's own Python environment, because a MINERvA histogram class may need
  the MAT dictionaries. P0's record goes into the binding. These files are simulation inputs, not data.

## 2. The recipe

**Prediction and ratio.** For playlist X and bin b:
- data count: N_X(b) is the number of `measured` rows in b;
- prediction: P_X(b) = Σ `w_reco` over the `pass_reco` rows of `MCreco` in b, plus Σ `bkg_w` over the `bkg_reco` rows
  in b;
- ratio: r_X(b) = N_X(b) / P_X(b).

**The reference** for X is leave-one-out: r_ref,−X(b) = Σ_{Y≠X} N_Y(b) / Σ_{Y≠X} P_Y(b).
- The offset is o_X(b) = r_X(b) / r_ref,−X(b) − 1.
- Its σ is analytic: the data Poisson term plus the MC Σw² term, for both X and the reference.

**Bins, fixed before any data row is read:**
- **p_∥** (GeV/c): 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20, 60. These are the edges of the 2D reco-level comparison
  (`playlist-spread-20261014/REPORT.md:140`).
- **p_T** (GeV/c): 0, 0.15, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5.
- **E_avail, q₃ and W:** ten bins each, at the pooled-MC weighted deciles of the `pass_reco` rows.
  - Step 0 computes them from MC keys only (`MCreco`, `w_reco`, `pass_reco`) and writes them to the run record.
  - Only then does step 1 open any `measured` key. The code enforces the order: step 1 refuses to run without step 0's
    record.
- **The 16 cells:** `nd-unfolding/pv-ladder/readouts/h2_definition.json`'s boxes and `h2_to_reporting_cell` map,
  applied to the reconstructed values.

**Shape statistic** per (X, axis a): χ²_{X,a} = Σ_b (o_X(b) − ō_X)² / σ_X(b)².
- ō_X is X's σ-weighted mean offset on that axis, so normalisation is removed and ndf = n_b − 1.
- The cell axis is the 16 cells, with ndf 15.

**The null control C-N** (run before any reading):
- The pooled data rows are split at random (seed `SeedSequence([20261104, 7, 1])`) into 12 pseudo-playlists, each with
  its real playlist's data count.
- Each is compared, by the same code, with the pooled prediction scaled to its count.
- **Pass:** at most 1 of the 72 pseudo tests (12 playlists × 6 axes) has p < 0.001.
- **On a fail, STOP:** no d1 reading is computed. The KS distance of the 72 p-values from uniform is reported in every
  outcome.

## 3. d1 readings, fixed

- **R-d1.0, the p_∥ step at reco.**
  - The statistic: s_G = [R_G(8–15) / R_G(1.5–8)] / [R_PA(8–15) / R_PA(1.5–8)] − 1. R_G is Σ_{X∈G} N_X / Σ_{X∈G} P_X
    over the p_∥ range, with PA = 1A–1F, PB = {1G, 1L, 1M} and PC = 1N–1P.
  - **SEES-RECO** if s_PB ≥ 3σ (σ analytic, as above); otherwise **NOT-SEEN**.
  - This axis was already read in 2D (`playlist-spread-20261014/REPORT.md:126-148`), so R-d1.0 is not blind.
- **R-d1.1, which playlists are shaped.** X is **SHAPED** on axis a if P(χ²_{ndf} > χ²_{X,a}) < 0.001. The readout
  lists the set S_a for each of the 6 axes.
- **R-d1.2, carriers.** For each axis, S_a ∩ {1L, 1M} (RPD's CARRIES set) and S_a ∖ {1L, 1M}. Descriptive.
- **R-d1.3, the hadronic axes.** **HADRONIC-STRUCTURED** if any of E_avail, q₃ or W has S_a non-empty; otherwise
  **HADRONIC-FLAT** at this sensitivity. This is the new part, which no earlier study read.
  <!-- absence-ok: scoped to the two reco-level period studies, which compare p_T and p_∥ only (playlist-spread-20261014/REPORT.md:126-148; period-unfold-20261014/REPORT.md:50-60) -->

## 4. d2, the flux swap

**Eν per MC row**, by inverting the simulation's own truth W.
- The forward map is `CVUniverse.h:396-409`:
  - W² = M² + 2(Eν − Eμ)M − Q²;
  - Q² = 4 Eν Eμ sin²(θ/2).
- Inverted: Eν = (W² − M² + 2EμM) / (2M − 4Eμ sin²(θ/2)), with θ = atan2(p_T, p_∥) and Eμ = √(p_T² + p_∥² + m_μ²),
  all from `MCgen`'s truth columns.
- The struck-nucleon mass is not in the dumps, so Eν is computed at M = M_p and at M = M_n. The mean is used.

**Its controls, each a STOP on failure:**
- **C-E1:** the denominator is positive and Eν ≥ Eμ for at least 99.9% of the `pass_reco` weight.
- **C-E2:** |Eν(M_n) − Eν(M_p)| / Eν < 0.5% for at least 99% of that weight.
- **C-E3:** q₃ is recomputed from Eν in the same convention, q₃′ = √(Q² + (Eν − Eμ)²). The median |q₃′ / q₃ − 1| over
  the weight is ≤ 0.01, against `MCgen`'s stored q₃ (MAT `Getq3True`).
  - C-E3 tests the inversion against a quantity it did not use.
  - If C-E3 fails, d2 stops, and an event-loop Eν branch would be priced separately.

**The swap.**
- Each signal MC row of playlist X gets the weight φ_T(Eν) / φ_own(X)(Eν), read as a step function in P0's Eν bins.
  Here φ is the P0 histogram, normalised to unit integral over its range.
- Rows outside the range keep weight 1 and are counted.
- Background rows (`bkg_*`) carry no truth and are not swapped. Their share of P_X is reported.

The three swaps, each reported both shape-only (renormalised to X's unswapped total) and unnormalised:
1. PB's MC to PA's file (1D);
2. the mirror, PA's MC to PB's file (1M);
3. PC's MC to 1D, descriptive only.

**Readings, fixed:**
- **The statistics:**
  - s_obs = s_PB as in R-d1.0;
  - s_swap = the same with PB's MC swapped;
  - s_mirror = the same with PA's MC swapped instead.
  - f = 1 − s_swap / s_obs, read shape-only.
- **The outcomes:**

  | outcome | condition |
  |---|---|
  | **NOT-SEEN** | R-d1.0 is NOT-SEEN. d2 has nothing to test, and no further reading is made |
  | **TRACKS** | f ≥ 0.75, and \|s_swap\| < 2σ, and \|s_mirror\| < 2σ |
  | **PARTIAL** | 0.25 ≤ f < 0.75, or TRACKS fails only on the mirror |
  | **DOES-NOT-TRACK** | f < 0.25 |

  σ is the analytic σ of each step. f's σ is propagated from s_obs and s_swap, which share the data.

## 5. Code, tests, price, admissibility, calendar

**Code.** One new script, `nd-unfolding/fd_rpd_reco.py`, with these steps:
- `p0` (inventory only);
- `step0` (the MC deciles);
- `cn` (the null control);
- `d1`;
- `d2`.

Each step writes a record with its inputs' sha256, its code sha256 and its argv. It imports only committed modules.

**Tests**, `nd-unfolding/tests/test_fd_rpd_reco.py`:
- real `.npz` fixtures with object arrays, in the dumps' own format;
- step 1 refuses without step 0's record;
- a pin mismatch refuses;
- the Eν inversion round-trips the forward W map to 10⁻⁹ on synthetic kinematics;
- the swap weight is identity when T = own;
- C-N passes on a structure-free fixture and fails on one with a planted 5% shape offset in one pseudo-playlist;
- each refusing control is exercised in the direction it acts.

**Price: 0 node-h.**
- Both run on a login node, with threads 1, nice 19 and every read O_NOATIME, from a fresh clone at the bound sha.
- The 24 inputs are about the size of `lat_zero` (1.55 GB, `FD-RPD-DECLARATION.md:158`). The wall-clock is unmeasured
  and expected well under an hour.
  <!-- absence-ok: a price estimate for an unrun step, not a claim that a result is absent -->
- No job and no write to CFS.

**Admissibility.**
- **A reconstruction-level read of the data**, so the recipe is frozen and bound before any ratio is computed
  (`FD-DIRECTOR-RULINGS.md:63-68`).
- **Not blind on muon kinematics.** p_T and p_∥ were already read at reco level in 2D. E_avail, q₃ and W were not.
- **Simulation only.** The flux ratio and the Eν inversion use simulation alone.
- **No reported number, estimator or covariance changes in any outcome.**

**Calendar.**
- The dumps were written on or after 2026-11-03, so exposure is not before about 2026-12-29 (arithmetic, from 8 weeks
  after the oldest possible atime).
- The MAT flux files' location and retention are recorded at P0.
- The run waits for B4 to finish, unless the director orders otherwise.

## 6. What each outcome licenses

Every licence covers a statement in the note first. Any paper use goes to Joseph through the PRD-referee read
(`DECISION-20261104-joseph-referee-analysis-commission.md` item 4). **No outcome names a cause except TRACKS, and TRACKS
names only a coincidence with the simulation's flux-file assignment.**

| outcome | may be stated | may not |
|---|---|---|
| C-N or a C-E control STOP | that the declared test stopped, at which control | any reading |
| R-d1.0 SEES-RECO | the p_∥ step is present at reconstruction level before unfolding, with s_PB ± σ | that the unfolding did not create it; that is a further inference |
| R-d1.0 NOT-SEEN | not seen at reco level at this sensitivity | that it is absent |
| R-d1.3 HADRONIC-STRUCTURED / -FLAT | the axes and playlists in S_a, with χ² and p | any localisation in the detector |
| d2 TRACKS | reweighting the 1G–1M simulation to the 1A–1F flux file removes the fraction f of the reco-level step, and the mirror removes it too. **The step coincides with the difference between the flux files the simulation assigns to these periods** | which flux or period is correct; that the flux is wrong; "explained" or "corrected" |
| d2 PARTIAL | the fraction f, descriptively | any mechanism wording |
| d2 DOES-NOT-TRACK | the flux-file difference does not reproduce the step (f, with σ) | anything beyond excluding that candidate |

**In every outcome:**
- "The cause is not known" stays, unless Joseph rules otherwise on a TRACKS result.
- C_PL,5D, its wording, and RPD's licensed sentence are unchanged.
