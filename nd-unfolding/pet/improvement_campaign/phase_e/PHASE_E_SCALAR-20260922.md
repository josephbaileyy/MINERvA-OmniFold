# Phase E1 — distortion library, identifiability, and the scalar references under distortion

**Scope.** PET is diagnostic method development. Everything here is simulation only: the signal-MC
members of `G2_FPS_MEFHC_P12.npz` (`fa6b3463…`) and the standalone generator predictions of
`3d-unfolding/genie/`. No measured or background member of the inventory is opened, no real data is
unfolded, nothing here is a publication adoption, an uncertainty product, a Gate-6 action, a change
to the adopted scalar-5D covariance, or a change to the historical comparison's thresholds, report
or verdict. Every reference or threshold statement below is a **prospective recommendation**.

## Status

| item | state |
|---|---|
| 1. distortion library (`distortions.py`) + unit tests | committed |
| 2. replicate drawing (`replicates.py`) + unit tests | committed |
| 3. identifiability table | (filled when the job lands) |
| 4. scalar references under distortion | (filled when the jobs land) |
| 5. reference assessment (a)(b)(c) | (filled when the jobs land) |
| 6. this document + `results/*.json` | in progress |

## 1. What is implemented, and what it acts on

### 1.1 Pools, replicates and the target

Pool T (STRESS, 8,018,001 events) and pool S (SCALE, 18,861,069 events) come from
`pools/POOL_MANIFEST.json` and `pools.npz`, whose sha256 and per-pool counts are re-checked before
anything is read (`replicates.load_pool_codes`). A replicate is drawn inside a pool by two
identity hashes (protocol §3): a family hash ranks the pool and gives replicate *r* the *r*-th
disjoint block of `n_prior + n_pseudo` events; the replicate-salted second hash orders that block
and splits it into the prior sample (600,130 events) and the pseudodata sample (600,111 events) —
the historical sizes. Replicates of one family are therefore **disjoint event draws**, not seed
repetitions, and every draw is a pure function of the event identity `(mc_run, mc_subrun,
mc_nthEvtInFile)`. A family that cannot fit in its pool must declare `disjoint=False`; its measured
pairwise overlap is then reported with every number derived from it (this happens only for the 8×
pool-S family of §5b).

The **target** is the distorted truth spectrum computed on **all of pool T** (Amendment 1), not on
a second half: an estimator is scored against the population it is supposed to recover. The
statistic, the seven `E_avail` bins, the three historical regions and the region assignment are the
historical ones — `run_arm_evaluation.recovery`, `score_campaign._histogram`,
`score_campaign.overshoot_projection` and `characterize_regions.region_labels_for_events` under the
historical acceptance map, imported through `phase_b/scalar/scalar_common.py`, which refuses if any
loaded file differs from the comparison's code commit `68cf9d29`. `common.score` is tested
bit-identical to the historical scorer on the same spectra (`test_phase_e.py`).

### 1.2 Truth-model distortions (D1–D5)

Each is a per-event weight, a function of truth only, applied to the pseudodata and normalized to
unit mean over the pseudodata sample; the prior is never distorted.

| id family | definition | magnitudes |
|---|---|---|
| D1 | the historical clipped exponential tilt in true `E_avail`, `exp(A · clip((E − p50)/IQR, ±3))` | A = −0.70, −0.35, −0.175, +0.175, +0.35, +0.70 |
| D2 | `1 + A exp(−((E − c)/s)²)` | (0.5, 0.3, 0.15) and (0.5, 1.0, 0.4) GeV |
| D3 | the same tilt in the standardized ratio `E_avail/q3` | A = ±0.35 |
| D4a–d | `f^N`, N = stored truth hadrons with \|pdg\| = 211 / 111 / 2212 / 2112 | f = 1.3 and 1/1.3 |
| D5 | `σ_X/σ_TuneV1` per 3D bin, X ∈ {NuWro, GiBUU, GENIE+ValenciaMEC CV, GENIE FSI FrAbs_pi, FrInel_pi} | one per generator |

**D1's standardization is frozen** at the development injection's own constants (p50 = 1.46537 GeV,
IQR = 2.63367 GeV, the quartiles of the historical half A, replayed by B1), so D1 is one fixed
function of true `E_avail` — the same on every replicate and on the pool-T target. Pool T's own
quartiles are measured and reported beside them (§2). **D3's** standardization is pool T's own
quartiles of `E_avail/q3`, measured before any scoring and frozen into the spec; an event with
`q3 ≤ 0` or non-finite `q3` gets weight 1 and is counted. **D4** counts among the ≤ 12 stored truth
hadrons of `part_gen` (energy-ordered, so an event with more than 12 final-state hadrons is
truncated; the truncation rate is measured in §2).

**D5 and what it actually is.** The predeclared weight is the ratio of the two predictions' 3D
histograms on the analysis binning (14 p_T × 16 p‖ × 7 `E_avail` bins), taken as a *shape* ratio
(each prediction divided by its own total over the 3D phase space, so the in-phase-space weights
average ≈ 1 and events outside that phase space, which keep weight 1, are not moved by the
generators' different normalizations), after the stated merge rule (bins where either histogram's
relative statistical error exceeds 30 % are merged with neighbours along `E_avail` — top-down into
the lower neighbour — until neither does) and the stated clip to [0.2, 5]. A column that still fails
fully merged keeps weight 1. Two of the five predictions carry no bin errors; their event counts are
recovered exactly from the integer lattice of the filled histogram and the error is `1/√n` (the FSI
files are the same GENIE-CV events reweighted, so they use the CV counts).

**MEASURED, and it governs how D5 must be read:** above p‖ ≈ 8 GeV every standalone prediction falls
far below Tune v1. The p‖-marginal shape ratio (generator / Tune v1, normalized over the 3D phase
space) is 1.0–1.2 up to 8 GeV and then 0.37 (9–10 GeV), 0.15 (10–15), 0.10 (15–20), 0.04 (20–40),
0.005 (40–60) for NuWro and GENIE+MEC, and 0.77 / 0.39 / 0 / 0 for GiBUU. The predeclared D5 is
therefore dominated by that p‖ difference — a property of how the standalone predictions were
generated (flux handling / generation range; the cause is **not established** here), not an
interaction-model difference — and it clips ≈ 10 % of the Tune v1 in-phase-space mass at 0.2
(1.1 % for GiBUU). It is implemented exactly as predeclared. Beside it, a **post-hoc, not
predeclared** table normalizes each prediction within each p‖ slice, which removes that marginal and
keeps the `(p_T, E_avail | p‖)` shape; it is labelled `D5p_*` everywhere and enters no verdict.

### 1.3 Detector-response distortions (R1–R3), and exactly what is scaled

Reco `E_avail` is `NewEavail()` = 1.17 × (tracker + ECAL blob recoil − the muon fuzz in those
planes) (`CVUniverse.h:185–193`); reco `q3` is `RecoQ3()` = √(Q² + q0²) with q0 the calorimetric
`<tree>_recoil_E` and Q² = 2(E_μ + q0)(E_μ − p‖) − m_μ² (`CVUniverse.h:208–219`); the tokens are the
≤ 12 highest-energy reco recoil clusters (`part_reco[…,0]`, MeV → GeV). q0 is **not** stored; it is
recovered by inverting `RecoQ3` on the stored (p_T, p‖, q3), and rows with no non-negative root (the
Q² < 0 clip, where q3 = q0) take q0 = q3 and are counted (§2).

* **R1 (hadronic energy scale, ×1.05 / ×0.95):** every calorimetric energy is multiplied by s — the
  blob sums, the fuzz subtracted from them, and every cluster — so reco `E_avail` → s·`E_avail`
  exactly, each token energy → s·E_i, and q0 → s·q0; reco q3 is recomputed from the unchanged muon
  and the new q0. The token count is unchanged.
* **R2 (muon momentum scale, ×1.01 / ×0.99):** reco p_T and p‖ → s·(p_T, p‖) (p → s·p at fixed
  angle, E_μ = √(p² + m_μ²)); q0 unchanged; reco q3 recomputed; `E_avail` and the tokens unchanged.
  The reco reporting cell is recomputed, so events that cross a cell edge move.
* **R3 (hadronic resolution, σ = 10 %):** each stored token energy E_i → E_i·max(1 + σ g_i, 0) with
  g_i ~ N(0,1) independent per (event, token slot), drawn from the event identity by blake2b so the
  same event always receives the same smearing; reco `E_avail` and q0 are multiplied by
  ρ = ΣE_i′/ΣE_i over the stored tokens (ρ = 1 if an event has no stored energy). **Stated
  limitation:** the ≤ 12 stored tokens are neither all of the energy `E_avail` sums nor split by
  sub-detector, so R3 moves `E_avail` by the energy-weighted smearing of the stored clusters rather
  than by a full re-simulation of the calorimetric sum; the measured `E_avail`/Σtoken relation is in
  §2.

**What R1–R3 do not do:** they do not re-evaluate the reco selection. `pass_reco` and the extended
FPS domain gate are the inventory's own, computed on the undistorted quantities, so no event enters
or leaves the selected sample under a scale or a smearing; only the values of selected events move.
A real scale systematic would also migrate events across the selection boundary. What does move is
the reco reporting cell, and the number of pseudodata events whose cell changes is recorded per case
(`moved_reco_cells` in `results/references.json`).

Each R is run twice, as predeclared: alone (the **null**, where the correct answer is to do nothing
and what is reported is the spurious displacement) and combined with D1 at +0.35.

### 1.4 Content hashes

Every distortion carries a `content_hash`: the sha256 of the canonical JSON of its full spec — id,
family, kind, every parameter, and for D5 the digest of the weight table together with the sha256 of
the source ROOT files. A `Case` (a truth distortion, a response distortion, or both) hashes the pair.
The hashes are in `results/references.json` and `results/identifiability.json` beside every number.

## 2. The pool-T and pool-S input census

(filled from `results/prepare.json`)

## 3. Identifiability

(filled from `results/identifiability.json`)

## 4. The scalar references under distortion

(filled from `results/references.json`)

## 5. Reference assessment

(filled from `results/reference_assessment.json` and `results/toy_reference.json`)

## 6. What these numbers establish, and what they do not

**Not established by anything here** (independent of how the numbers come out):

1. **No bound.** A recovery in §4 or §5 is one estimator's performance on one population under one
   distortion. It is not an attainability limit, and the reference model is not a bound either —
   §5c shows an estimator that exceeds it.
2. **No threshold.** The historical reference (0.6949731569), the aggregate floor (0.5559785255),
   the regional floors, the non-inferiority margin (0.02) and the switching margin (0.04) are
   unchanged and are not re-derived here. Any alternative reference in §5 is a **prospective
   recommendation** for this campaign, never a retroactive change to the historical verdict.
3. **Nothing about PET.** These are scalar references. What a PET candidate does under these
   distortions is a later measurement against exactly these yardsticks, on the same replicates.
4. **"Not distinguishable at this sample size" is not "unrecoverable."** The identifiability
   statistic is a property of a classifier, a feature set and a sample size; a distortion below the
   null band is reported as unprobed at this size (protocol §7), and no recovery number for it
   carries a claim about what a better-powered experiment would find.
5. **Event-draw and estimator-seed variation are not separated here.** Each replicate is an
   independent event draw scored with one estimator seed, so a spread across replicates contains
   both. B1 measured the seed-only spread of the same GBDT reference on one fixed sample
   (sd ≤ 0.013 at k = 3).
6. **R3 is an approximation of a resolution systematic**, not a re-simulation: the ≤ 12 stored
   tokens are neither all of the calorimetric energy `E_avail` sums nor split by sub-detector, so
   the smearing is applied to the stored clusters and propagated to `E_avail` by their energy
   ratio (§1.3).
7. **D5 as predeclared is dominated by the standalone predictions' p‖ shortfall** above ≈ 8 GeV
   (§1.2), whose cause is not established here. The post-hoc per-p‖-slice variant separates the
   remaining `(p_T, E_avail | p‖)` difference; it is not predeclared and enters no verdict.
8. **The 8× pool-S replicates share events** (§5b) — their spread is a lower bound on the
   sampling spread of three independent 8× draws, which pool S cannot supply.

## 7. Provenance and cost

(filled)
