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
| 1. distortion library (`distortions.py`) + unit tests | done — 33 distortions (28 predeclared + 5 post-hoc), 38 cases |
| 2. replicate drawing (`replicates.py`) + unit tests | done — golden-pinned; importable by Phase D/E and the confirmatory stage |
| 3. identifiability table | done — §3, `results/identifiability.json` |
| 4. scalar references under distortion | done — 114/114 case × replicate runs, both miss-handling modes, §4 |
| 5. reference assessment (a)(b)(c) | done — (a) cited from B1, (b) pool S 1× and 8×, (c) toy; §5 |
| 6. this document + `results/*.json` | done |

**Headline (all simulation, all MEASURED unless labelled):** every predeclared truth distortion is
distinguishable at the historical pseudodata size; R2 (±1 % muon scale) and R3 (10 % cluster
smearing) are not, and are reported as unprobed at that size. The scalar yardsticks at k = 3 span
0.34–0.62 (IBU, misses carried) and 0.22–0.57 (GBDT) across D1–D3, D4a/b and D5, fall to 0.11–0.30
under the proton multiplicity (D4c) and below zero under D4d; efficiency correction reaches
0.84–0.96 on the `E_avail` tilts and pion multiplicities but fails on within-bin shape changes
(D5 NuWro −0.20). Under D4d (neutrons) every estimator ends farther from the target than the prior. A ±5 %
hadronic-scale error moves measured recovery by ±0.06. On pool S, 8× more events close only 0.008
of the 0.223 gap between the response-aware IBU and the historical reference at k = 3; the
reference model's own realization on the scored object is 0.53, not 0.695; and a known-function toy
shows `1-(1-a)^k` overstates the engine rule's attainable recovery at small k even when its
assumptions hold, while efficiency correction exceeds it — it is neither a bound nor a match.

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

All MEASURED by job `58780643` at commit `bf1f11e7` (2 min 11 s on one exclusive CPU node;
`results/prepare.json`), before anything was scored. The caches are
`/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseE1/prep/pool{T,S}.npz`
(sha256 `4dbbfb670095…`, 1.44 GB; `57a0a78c8a41…`, 2.30 GB).

| | pool T (STRESS) | pool S (SCALE) |
|---|---:|---:|
| events (all `pass_truth`) | 8,018,001 | 18,861,069 |
| selected (`pass_reco`) | 3,356,843 | 7,893,556 |
| w-weighted accepted fraction | 0.41583 | 0.41565 |
| region: low acceptance / poor / moderate / good | 2,533,077 / 556,412 / 1,132,536 / 3,795,976 | 5,956,870 / 1,311,213 / 2,664,944 / 8,928,042 |
| truth off the reporting grid | 0 | 0 |
| non-finite true `q3` (D3 gives them weight 1) | 197 | 477 |
| non-finite or sentinel reco values on selected rows | 0 | 0 |

The accepted fraction matches the historical prior half's 0.4155 (B1), as it should: the pools are
disjoint draws from the same inventory.

**D1's frozen standardization against pool T's own.** Pool T's true-`E_avail` quartiles are
p25 0.53108, p50 1.45949, p75 3.16153 GeV (IQR 2.63044), against the frozen development constants
p50 1.46537, IQR 2.63367 — 0.4 % and 0.1 % apart. D1 is therefore one fixed function everywhere,
at a cost of well under a percent of its coordinate.

**D3's standardization** (`calibration/d3_standardization.json`, digest `dc53c373…`): the quartiles
of true `E_avail`/`q3` over the 8,017,804 usable pool-T rows are p25 0.40408, p50 0.64921,
p75 0.82325 (IQR 0.41916).

**The `RecoQ3` inversion** that R1–R3 need: on the 3,356,843 selected pool-T rows, 17 (5·10⁻⁶) have
no non-negative root and take q0 = q3; the recomputed q3 reproduces the stored one to
2.8·10⁻¹⁴ GeV. The recovered q0 has quartiles 0.569 / 1.284 / 2.772 GeV, and 916 rows have
q0 below `E_avail`/1.17 (q0 is the full calorimetric recoil, so it should normally exceed it).

**What the stored tokens hold, which is what R3 acts on.** 3,350,456 selected events have stored
cluster energy and 6,387 have none (their reco `E_avail` is exactly 0, and R3 leaves them alone).
The ratio reco `E_avail` / Σ(stored token energy) has quartiles 1.63 / 2.58 / 3.97: with the 1.17
calorimetric factor, the ≤ 12 stored clusters hold a median ≈ 45 % of the tracker+ECAL recoil
energy, and 2,856,291 events (85 %) fill all 12 slots. R3's ρ is therefore built from the
highest-energy clusters, which dominate the quadrature sum but are not all of it (§1.3, §6).

**`part_gen` truncation, which is what D4 counts through.** 200,368 events (2.5 %) fill all 12
truth-hadron slots and may have lost hadrons below the 12th; mean stored counts are 1.213 (π±),
0.626 (π⁰), 1.428 (p), 0.988 (n).

**D5's coverage:** 6,300,197 pool-T events (78.9 % of the truth weight) fall inside the 3D
phase space where the generator predictions are defined; the remaining 1,717,804 keep weight 1.

**The committed D5 tables were rebuilt from the canonical ROOT files on Perlmutter** and every
table digest and source sha256 agreed (`results/d5_rebuild_check.json`). The rebuild ran through
the OI-136 guard on a login node because `root_6_28`'s PyROOT segfaults in cling on this machine
(job `58756787`) and the NERSC python module supplies `uproot` instead.

## 3. Identifiability

MEASURED by jobs `58780734` (the null) and `58780834` (the distortions) at commit `eba430eb`, on
one replicate of the `E1-identifiability` family: two disjoint 600,111-event samples from pool T,
the probe distorted, a HistGradientBoosting classifier on (reco p_T, p‖, `E_avail`, `q3`, stored
token count, stored token ΣE), 50/50 train/test, statistic = weighted test AUC − 0.5.

**The null** (20 equal-model splits, both samples undistorted): mean +0.00021, sd 0.00128, 95 %
band [−0.00191, +0.00197], max +0.00202. Two undistorted samples of this size differ in the
seven-bin reco `E_avail` spectrum by L1 = 0.0059 on average (max 0.0089) — the noise floor any
reco-level displacement has to clear. The **positive controls are in the same table**: D1 at
±0.70 gives AUC − 0.5 = +0.17 and +0.077, so the machinery has power where power is expected, and
a "not distinguishable" verdict below is not a silent failure of the measurement.

**Every truth distortion is distinguishable** at the historical pseudodata size, by 2.6× to 78× the
threshold. The weakest is D4d (neutron multiplicity), the predeclared hidden-variable test:
+0.0126 (×1.3) and +0.0055 (÷1.3) against a threshold of ≈ 0.0022, with a reco `E_avail`
displacement of only 0.009–0.011 — it is detectable, but through the parts of the event that are
not `E_avail`.

**The response distortions are at or below the floor.** R1 (±5 % hadronic scale) is clearly
distinguishable (+0.022, +0.024; reco `E_avail` L1 0.034–0.036). R2 at +1 % sits on the threshold
(+0.00229 against 0.00213) and R2 at −1 % does not clear it (−0.00019); **R3 as implemented does
not clear it either** (−0.00137, reco `E_avail` L1 0.0008). R3's predeclared σ = 10 % per cluster
becomes a much smaller displacement of the `E_avail` marginal: smearing ~12 clusters independently
and summing averages the fluctuation down to a few percent, and a symmetric convolution barely
moves a seven-bin marginal. **These are reported as unprobed at this sample size, not as harmless**
(protocol §7): the recovery numbers for them in §4 are measured under a distortion the data cannot
distinguish from no distortion at all.

**The weighted-sample correction is real but small.** The ESS-scaled threshold rises from 0.00197
(raw 97.5th percentile) to at most 0.00274 (D1 at +0.70), and the permutation null run for the
three most weight-dispersed cases (D1 ±0.70, D5 GiBUU, 5 splits each) lands in the same band as the
equal-model null (e.g. D5 GiBUU: −0.0013 … +0.0020), so the scaling is not doing hidden work. No
verdict in the table differs between the raw and the scaled threshold.

Null (20 equal-model splits): mean +0.00021, sd 0.00128, 95th-percentile band [-0.00191, +0.00197], max +0.00202; reco E_avail L1 between two undistorted samples 0.0059 (max 0.0089).

| distortion | AUC − 0.5 | threshold (ESS-scaled) | distinguishable | reco E_avail L1 (pool T) | truth injected L1 (pool T) |
|---|---:|---:|---|---:|---:|
| `D1_m0.175` | +0.01869 | 0.00214 | yes | 0.0748 | 0.1078 |
| `D1_m0.350` | +0.03987 | 0.00216 | yes | 0.1379 | 0.2054 |
| `D1_m0.700` | +0.07678 | 0.00220 | yes | 0.2383 | 0.3714 |
| `D1_p0.175` | +0.02583 | 0.00215 | yes | 0.0951 | 0.1270 |
| `D1_p0.350` | +0.06772 | 0.00222 | yes | 0.2154 | 0.2731 |
| `D1_p0.700` | +0.17107 | 0.00274 | yes | 0.5357 | 0.6048 |
| `D2_bump_c0.3` | +0.01714 | 0.00215 | yes | 0.0776 | 0.0791 |
| `D2_bump_c1.0` | +0.01922 | 0.00213 | yes | 0.0721 | 0.1077 |
| `D3_m0.35` | +0.03106 | 0.00217 | yes | 0.1059 | 0.1447 |
| `D3_p0.35` | +0.02774 | 0.00214 | yes | 0.1005 | 0.1343 |
| `D4a_pipm_down` | +0.03237 | 0.00218 | yes | 0.1168 | 0.1337 |
| `D4a_pipm_up` | +0.04833 | 0.00219 | yes | 0.1623 | 0.1681 |
| `D4b_pi0_down` | +0.02134 | 0.00216 | yes | 0.0872 | 0.0974 |
| `D4b_pi0_up` | +0.03068 | 0.00216 | yes | 0.1165 | 0.1231 |
| `D4c_p_down` | +0.02223 | 0.00215 | yes | 0.0298 | 0.0231 |
| `D4c_p_up` | +0.03901 | 0.00235 | yes | 0.0230 | 0.0282 |
| `D4d_n_down` | +0.00554 | 0.00216 | yes | 0.0105 | 0.0072 |
| `D4d_n_up` | +0.01257 | 0.00227 | yes | 0.0088 | 0.0110 |
| `D5_fsi_frabs` | +0.06961 | 0.00216 | yes | 0.1186 | 0.1145 |
| `D5_fsi_frinel` | +0.06855 | 0.00217 | yes | 0.1179 | 0.1134 |
| `D5_genie_mec` | +0.06931 | 0.00217 | yes | 0.1346 | 0.1181 |
| `D5_gibuu` | +0.04941 | 0.00220 | yes | 0.0993 | 0.0877 |
| `D5_nuwro` | +0.07008 | 0.00220 | yes | 0.0962 | 0.0865 |
| `D5p_fsi_frabs` *(post-hoc)* | +0.04240 | 0.00216 | yes | 0.0965 | 0.0991 |
| `D5p_fsi_frinel` *(post-hoc)* | +0.04222 | 0.00217 | yes | 0.0956 | 0.0982 |
| `D5p_genie_mec` *(post-hoc)* | +0.04124 | 0.00217 | yes | 0.1086 | 0.1044 |
| `D5p_gibuu` *(post-hoc)* | +0.04747 | 0.00220 | yes | 0.0952 | 0.0826 |
| `D5p_nuwro` *(post-hoc)* | +0.04386 | 0.00219 | yes | 0.0756 | 0.0822 |
| `R1_x0.95` | +0.02410 | 0.00213 | yes | 0.0358 | 0.0000 |
| `R1_x1.05` | +0.02177 | 0.00213 | yes | 0.0344 | 0.0000 |
| `R2_x0.99` | -0.00019 | 0.00213 | **no** | 0.0000 | 0.0000 |
| `R2_x1.01` | +0.00229 | 0.00213 | yes | 0.0000 | 0.0000 |
| `R3_s0.10` | -0.00137 | 0.00213 | **no** | 0.0008 | 0.0000 |

Permutation null for `D1_p0.700` (5 splits): mean +0.00162, max +0.00280, against the ESS-scaled threshold 0.00274 and the observed +0.17107.

Permutation null for `D1_m0.700` (5 splits): mean +0.00132, max +0.00235, against the ESS-scaled threshold 0.00220 and the observed +0.07678.

Permutation null for `D5_gibuu` (5 splits): mean +0.00067, max +0.00200, against the ESS-scaled threshold 0.00220 and the observed +0.04941.

## 4. The scalar references under distortion

MEASURED: 38 cases (33 predeclared + 5 post-hoc `D5p_*`) × 3 disjoint pool-T replicates of the
`E1-references` family (prior 600,130 + pseudodata 600,111 events each), 114 of 114 complete; nine
debug-QOS jobs at commit `972ab5d4` (§7). Binned IBU on (p_T, p‖) cells × reco `E_avail`, in BOTH
miss-handling modes, k = 1..30; GBDT OmniFold on (reco p_T, p‖, `E_avail`) → the four truth scalars,
k = 1..10, one estimator seed per replicate. Target: the case's truth spectrum over all of pool T.
Entries are mean ± sd over the three replicates (each replicate is an independent event draw AND an
estimator seed, §6.5); "best" is the best k in 1..30 and the mean best k. Per-bin signed residuals
at k = 3 and 10, per-region values, weight summaries and the step-1 reco-level check are in
`results/references.json`.

| case | IBU carry k=3 | k=10 | best | IBU eff.-corr. k=3 | k=10 | best | GBDT k=3 | k=10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `D1_m0.175` | 0.376 ± 0.008 | 0.532 ± 0.016 | 0.583 ± 0.039 @22 | 0.919 ± 0.059 | 0.621 ± 0.101 | 0.923 ± 0.052 @3 | 0.281 ± 0.012 | 0.358 ± 0.013 |
| `D1_m0.350` | 0.382 ± 0.002 | 0.524 ± 0.005 | 0.566 ± 0.022 @27 | 0.913 ± 0.050 | 0.779 ± 0.053 | 0.936 ± 0.046 @4 | 0.340 ± 0.005 | 0.430 ± 0.007 |
| `D1_m0.700` | 0.392 ± 0.001 | 0.513 ± 0.004 | 0.549 ± 0.011 @30 | 0.876 ± 0.033 | 0.880 ± 0.056 | 0.936 ± 0.048 @6 | 0.363 ± 0.004 | 0.459 ± 0.005 |
| `D1_p0.175` | 0.450 ± 0.018 | 0.623 ± 0.030 | 0.657 ± 0.022 @20 | 0.883 ± 0.053 | 0.792 ± 0.084 | 0.898 ± 0.040 @4 | 0.341 ± 0.011 | 0.409 ± 0.014 |
| `D1_p0.350` | 0.483 ± 0.012 | 0.661 ± 0.019 | 0.699 ± 0.010 @16 | 0.932 ± 0.021 | 0.857 ± 0.097 | 0.953 ± 0.024 @4 | 0.414 ± 0.004 | 0.501 ± 0.009 |
| `D1_p0.700` | 0.563 ± 0.010 | 0.741 ± 0.015 | 0.782 ± 0.007 @16 | 0.955 ± 0.010 | 0.858 ± 0.043 | 0.964 ± 0.006 @3 | 0.509 ± 0.006 | 0.603 ± 0.007 |
| `D2_bump_c0.3` | 0.514 ± 0.019 | 0.682 ± 0.016 | 0.721 ± 0.022 @20 | 0.596 ± 0.052 | 0.512 ± 0.103 | 0.648 ± 0.079 @9 | 0.322 ± 0.034 | 0.371 ± 0.054 |
| `D2_bump_c1.0` | 0.352 ± 0.008 | 0.510 ± 0.005 | 0.565 ± 0.038 @30 | 0.543 ± 0.008 | 0.518 ± 0.049 | 0.593 ± 0.037 @11 | 0.224 ± 0.022 | 0.299 ± 0.038 |
| `D3_m0.35` | 0.344 ± 0.003 | 0.440 ± 0.009 | 0.474 ± 0.029 @30 | 0.708 ± 0.069 | 0.717 ± 0.131 | 0.754 ± 0.109 @7 | 0.260 ± 0.016 | 0.310 ± 0.024 |
| `D3_p0.35` | 0.405 ± 0.007 | 0.512 ± 0.018 | 0.533 ± 0.028 @26 | 0.678 ± 0.063 | 0.576 ± 0.129 | 0.712 ± 0.078 @10 | 0.316 ± 0.012 | 0.369 ± 0.007 |
| `D4a_pipm_down` | 0.496 ± 0.003 | 0.627 ± 0.010 | 0.669 ± 0.028 @30 | 0.868 ± 0.039 | 0.663 ± 0.024 | 0.921 ± 0.010 @2 | 0.395 ± 0.016 | 0.473 ± 0.019 |
| `D4a_pipm_up` | 0.573 ± 0.011 | 0.714 ± 0.018 | 0.747 ± 0.023 @27 | 0.871 ± 0.084 | 0.780 ± 0.153 | 0.912 ± 0.050 @2 | 0.488 ± 0.004 | 0.560 ± 0.014 |
| `D4b_pi0_down` | 0.515 ± 0.008 | 0.671 ± 0.020 | 0.733 ± 0.012 @30 | 0.841 ± 0.097 | 0.542 ± 0.065 | 0.914 ± 0.035 @2 | 0.385 ± 0.018 | 0.469 ± 0.042 |
| `D4b_pi0_up` | 0.560 ± 0.011 | 0.743 ± 0.022 | 0.789 ± 0.039 @27 | 0.919 ± 0.018 | 0.761 ± 0.072 | 0.939 ± 0.022 @3 | 0.456 ± 0.010 | 0.536 ± 0.012 |
| `D4c_p_down` | 0.295 ± 0.049 | 0.405 ± 0.101 | 0.436 ± 0.100 @22 | 0.263 ± 0.155 | -0.396 ± 0.480 | 0.331 ± 0.159 @4 | 0.197 ± 0.042 | 0.201 ± 0.037 |
| `D4c_p_up` | 0.197 ± 0.057 | 0.185 ± 0.123 | 0.243 ± 0.123 @8 | 0.314 ± 0.146 | -0.399 ± 0.503 | 0.455 ± 0.089 @1 | 0.112 ± 0.045 | 0.127 ± 0.057 |
| `D4d_n_down` | -0.411 ± 0.515 | -0.896 ± 0.985 | -0.168 ± 0.291 @2 | -1.947 ± 1.752 | -4.908 ± 2.708 | -0.982 ± 0.903 @2 | -0.061 ± 0.144 | -0.088 ± 0.226 |
| `D4d_n_up` | -0.323 ± 0.192 | -0.592 ± 0.240 | -0.168 ± 0.101 @1 | -0.458 ± 0.624 | -2.124 ± 1.349 | -0.218 ± 0.357 @2 | -0.153 ± 0.107 | -0.149 ± 0.118 |
| `D5_fsi_frabs` | 0.611 ± 0.011 | 0.816 ± 0.003 | 0.884 ± 0.027 @28 | 0.857 ± 0.009 | 0.672 ± 0.047 | 0.873 ± 0.029 @3 | 0.554 ± 0.021 | 0.711 ± 0.024 |
| `D5_fsi_frinel` | 0.611 ± 0.010 | 0.811 ± 0.006 | 0.881 ± 0.030 @29 | 0.855 ± 0.012 | 0.668 ± 0.044 | 0.871 ± 0.035 @3 | 0.556 ± 0.024 | 0.708 ± 0.025 |
| `D5_genie_mec` | 0.620 ± 0.015 | 0.804 ± 0.008 | 0.865 ± 0.032 @30 | 0.841 ± 0.057 | 0.649 ± 0.015 | 0.879 ± 0.048 @3 | 0.572 ± 0.016 | 0.722 ± 0.025 |
| `D5_gibuu` | 0.546 ± 0.022 | 0.688 ± 0.041 | 0.776 ± 0.069 @30 | 0.645 ± 0.052 | 0.503 ± 0.115 | 0.680 ± 0.058 @5 | 0.441 ± 0.023 | 0.499 ± 0.027 |
| `D5_nuwro` | 0.475 ± 0.029 | 0.651 ± 0.056 | 0.777 ± 0.100 @30 | -0.201 ± 0.169 | -0.002 ± 0.212 | 0.092 ± 0.266 @16 | 0.430 ± 0.020 | 0.503 ± 0.019 |
| `D5p_fsi_frabs` *(post-hoc)* | 0.531 ± 0.011 | 0.765 ± 0.015 | 0.843 ± 0.018 @27 | 0.796 ± 0.078 | 0.599 ± 0.068 | 0.843 ± 0.096 @3 | 0.447 ± 0.028 | 0.609 ± 0.044 |
| `D5p_fsi_frinel` *(post-hoc)* | 0.531 ± 0.010 | 0.762 ± 0.016 | 0.842 ± 0.021 @27 | 0.791 ± 0.079 | 0.595 ± 0.071 | 0.838 ± 0.093 @3 | 0.449 ± 0.032 | 0.607 ± 0.034 |
| `D5p_genie_mec` *(post-hoc)* | 0.527 ± 0.013 | 0.752 ± 0.012 | 0.830 ± 0.028 @28 | 0.779 ± 0.119 | 0.586 ± 0.058 | 0.845 ± 0.075 @3 | 0.454 ± 0.027 | 0.604 ± 0.034 |
| `D5p_gibuu` *(post-hoc)* | 0.549 ± 0.027 | 0.704 ± 0.043 | 0.799 ± 0.073 @30 | 0.633 ± 0.040 | 0.461 ± 0.124 | 0.665 ± 0.051 @4 | 0.441 ± 0.020 | 0.510 ± 0.038 |
| `D5p_nuwro` *(post-hoc)* | 0.414 ± 0.030 | 0.603 ± 0.062 | 0.749 ± 0.111 @30 | -0.062 ± 0.149 | 0.119 ± 0.213 | 0.213 ± 0.261 @17 | 0.360 ± 0.030 | 0.440 ± 0.033 |
| `R1_x0.95` | -9.497 ± 4.227 | -13.550 ± 5.773 | -4.849 ± 2.525 @1 | -21.665 ± 5.992 | -31.522 ± 10.120 | -13.845 ± 5.144 @1 | -3.863 ± 1.591 | -4.355 ± 1.760 |
| `R1_x0.95+D1_p0.350` | 0.418 ± 0.012 | 0.557 ± 0.018 | 0.591 ± 0.009 @17 | 0.803 ± 0.042 | 0.854 ± 0.010 | 0.880 ± 0.012 @15 | 0.356 ± 0.007 | 0.422 ± 0.012 |
| `R1_x1.05` | -9.506 ± 4.344 | -13.390 ± 5.990 | -4.575 ± 2.087 @1 | -16.983 ± 9.955 | -21.582 ± 14.164 | -10.887 ± 5.457 @1 | -4.137 ± 2.465 | -4.488 ± 2.532 |
| `R1_x1.05+D1_p0.350` | 0.546 ± 0.012 | 0.759 ± 0.018 | 0.797 ± 0.016 @17 | 0.870 ± 0.017 | 0.691 ± 0.068 | 0.939 ± 0.008 @2 | 0.476 ± 0.008 | 0.588 ± 0.009 |
| `R2_x0.99` | -0.837 ± 0.995 | -2.078 ± 1.363 | -0.211 ± 0.485 @1 | -3.432 ± 2.970 | -11.497 ± 8.140 | -2.389 ± 2.333 @2 | -0.341 ± 0.571 | -0.496 ± 0.725 |
| `R2_x0.99+D1_p0.350` | 0.484 ± 0.012 | 0.666 ± 0.019 | 0.700 ± 0.009 @16 | 0.952 ± 0.015 | 0.808 ± 0.094 | 0.952 ± 0.015 @3 | 0.417 ± 0.007 | 0.504 ± 0.009 |
| `R2_x1.01` | -0.754 ± 1.049 | -1.785 ± 1.088 | -0.141 ± 0.512 @2 | -6.238 ± 2.549 | -19.973 ± 12.795 | -3.557 ± 1.460 @1 | -0.332 ± 0.358 | -0.421 ± 0.673 |
| `R2_x1.01+D1_p0.350` | 0.482 ± 0.012 | 0.658 ± 0.019 | 0.700 ± 0.010 @17 | 0.917 ± 0.032 | 0.888 ± 0.088 | 0.954 ± 0.016 @6 | 0.414 ± 0.008 | 0.501 ± 0.011 |
| `R3_s0.10` | -0.730 ± 1.035 | -1.800 ± 1.293 | -0.135 ± 0.488 @2 | -3.394 ± 1.847 | -11.952 ± 5.363 | -1.405 ± 1.134 @1 | -0.318 ± 0.671 | -0.432 ± 0.710 |
| `R3_s0.10+D1_p0.350` | 0.483 ± 0.012 | 0.661 ± 0.018 | 0.699 ± 0.010 @16 | 0.934 ± 0.014 | 0.848 ± 0.093 | 0.952 ± 0.025 @4 | 0.413 ± 0.007 | 0.501 ± 0.011 |

Per region at k = 3 (low / moderate / good), mean over replicates:

| case | IBU carry | IBU eff.-corr. | GBDT |
|---|---|---|---|
| `D1_m0.175` | 0.005 / 0.515 / 0.843 | 0.733 / 0.876 / 0.919 | 0.036 / 0.309 / 0.635 |
| `D1_m0.350` | 0.005 / 0.501 / 0.865 | 0.710 / 0.921 / 0.949 | 0.023 / 0.388 / 0.740 |
| `D1_m0.700` | 0.004 / 0.490 / 0.859 | 0.634 / 0.929 / 0.954 | 0.015 / 0.411 / 0.779 |
| `D1_p0.175` | 0.009 / 0.561 / 0.880 | 0.671 / 0.886 / 0.915 | 0.034 / 0.393 / 0.659 |
| `D1_p0.350` | 0.009 / 0.582 / 0.896 | 0.751 / 0.917 / 0.946 | 0.042 / 0.470 / 0.753 |
| `D1_p0.700` | 0.012 / 0.629 / 0.913 | 0.787 / 0.925 / 0.965 | 0.049 / 0.547 / 0.810 |
| `D2_bump_c0.3` | -0.002 / 0.361 / 0.625 | -0.362 / 0.481 / 0.667 | 0.027 / 0.192 / 0.409 |
| `D2_bump_c1.0` | 0.004 / 0.292 / 0.523 | 0.307 / 0.457 / 0.563 | 0.044 / 0.156 / 0.358 |
| `D3_m0.35` | 0.003 / 0.363 / 0.718 | 0.398 / 0.647 / 0.792 | 0.013 / 0.206 / 0.536 |
| `D3_p0.35` | 0.005 / 0.397 / 0.762 | 0.280 / 0.671 / 0.843 | 0.005 / 0.281 / 0.575 |
| `D4a_pipm_down` | 0.007 / 0.600 / 0.891 | 0.607 / 0.826 / 0.916 | 0.028 / 0.385 / 0.727 |
| `D4a_pipm_up` | 0.012 / 0.634 / 0.923 | 0.644 / 0.850 / 0.936 | 0.025 / 0.494 / 0.761 |
| `D4b_pi0_down` | 0.008 / 0.683 / 0.897 | 0.730 / 0.683 / 0.841 | 0.037 / 0.377 / 0.669 |
| `D4b_pi0_up` | 0.011 / 0.696 / 0.919 | 0.676 / 0.695 / 0.845 | 0.029 / 0.490 / 0.727 |
| `D4c_p_down` | 0.001 / 0.067 / 0.501 | -0.178 / 0.045 / 0.510 | 0.018 / -0.036 / 0.329 |
| `D4c_p_up` | 0.009 / -0.242 / 0.337 | -1.039 / -0.611 / 0.316 | 0.029 / 0.012 / 0.148 |
| `D4d_n_down` | -0.001 / -0.300 / -0.515 | -0.670 / -0.778 / -0.582 | -0.007 / 0.008 / -0.152 |
| `D4d_n_up` | 0.000 / -0.375 / -0.724 | 0.054 / -0.710 / -0.880 | 0.005 / -0.126 / -0.197 |
| `D5_fsi_frabs` | 0.030 / 0.486 / 0.726 | -0.323 / 0.771 / 0.825 | 0.428 / 0.435 / 0.629 |
| `D5_fsi_frinel` | 0.029 / 0.486 / 0.726 | -0.215 / 0.767 / 0.822 | 0.412 / 0.439 / 0.629 |
| `D5_genie_mec` | 0.025 / 0.484 / 0.757 | -0.214 / 0.787 / 0.857 | 0.382 / 0.424 / 0.668 |
| `D5_gibuu` | 0.017 / 0.261 / 0.657 | -0.285 / 0.447 / 0.729 | 0.155 / 0.179 / 0.520 |
| `D5_nuwro` | -0.030 / 0.321 / 0.601 | -4.885 / 0.527 / 0.675 | 0.260 / 0.286 / 0.527 |
| `D5p_fsi_frabs` | 0.025 / 0.411 / 0.659 | -1.387 / 0.754 / 0.775 | 0.363 / 0.326 / 0.494 |
| `D5p_fsi_frinel` | 0.024 / 0.410 / 0.657 | -1.167 / 0.750 / 0.770 | 0.373 / 0.325 / 0.494 |
| `D5p_genie_mec` | 0.020 / 0.414 / 0.684 | -0.943 / 0.771 / 0.798 | 0.202 / 0.330 / 0.537 |
| `D5p_gibuu` | 0.016 / 0.243 / 0.638 | -0.365 / 0.435 / 0.712 | 0.224 / 0.176 / 0.499 |
| `D5p_nuwro` | -0.047 / 0.261 / 0.528 | -6.261 / 0.499 / 0.604 | 0.071 / 0.216 / 0.441 |
| `R1_x0.95` | 0.076 / -4.953 / -9.446 | -11.970 / -9.834 / -10.762 | -0.142 / -0.870 / -3.911 |
| `R1_x0.95+D1_p0.350` | 0.007 / 0.451 / 0.774 | 0.601 / 0.787 / 0.833 | 0.035 / 0.370 / 0.657 |
| `R1_x1.05` | 0.064 / -4.405 / -9.182 | -7.298 / -8.934 / -10.651 | -0.221 / -1.104 / -3.437 |
| `R1_x1.05+D1_p0.350` | 0.012 / 0.707 / 0.922 | 0.849 / 0.717 / 0.858 | 0.049 / 0.568 / 0.850 |
| `R2_x0.99` | 0.077 / -0.558 / -0.829 | -3.663 / -1.356 / -1.073 | 0.064 / 0.018 / -0.086 |
| `R2_x0.99+D1_p0.350` | 0.010 / 0.577 / 0.897 | 0.812 / 0.913 / 0.945 | 0.040 / 0.467 / 0.757 |
| `R2_x1.01` | 0.056 / -0.310 / -0.778 | -4.760 / -0.978 / -0.998 | -0.141 / 0.004 / -0.102 |
| `R2_x1.01+D1_p0.350` | 0.009 / 0.586 / 0.894 | 0.731 / 0.915 / 0.948 | 0.043 / 0.470 / 0.755 |
| `R3_s0.10` | 0.075 / -0.292 / -0.674 | -3.294 / -0.985 / -0.912 | -0.130 / 0.029 / -0.048 |
| `R3_s0.10+D1_p0.350` | 0.009 / 0.580 / 0.896 | 0.750 / 0.918 / 0.947 | 0.041 / 0.468 / 0.752 |

### 4.1 What the table says (all MEASURED on these replicates unless labelled)

1. **The development point reproduces B1 on fresh events.** D1 at +0.35: IBU (misses carried)
   0.483 ± 0.012 at k = 3, GBDT 0.414 ± 0.004 — against B1's 0.472 and 0.412 on the historical
   halves. The yardsticks transfer from the DEV halves to independent pool-T draws within ≈ 0.01.
2. **Recovery depends on the direction and shape of the distortion, not only its size.** At k = 3
   the carried-misses IBU ranges from 0.35 (D2 bump at 1 GeV) through 0.38 (every negative tilt)
   to 0.56–0.62 (positive tilts at 0.70, pion multiplicities, the D5 generator shapes). A negative
   tilt moves mass into the low-acceptance, low-`E_avail` cells, where carrying misses at their
   prior weight moves almost nothing: the low-acceptance region scores 0.004–0.012 at k = 3 for
   every D1 magnitude.
3. **Efficiency correction is far better on smooth `E_avail` distortions and fragile elsewhere.**
   At k = 3 it reaches 0.88–0.96 on every D1 magnitude (against 0.38–0.56 carried), including
   0.63–0.79 in the low-acceptance region — the Phase-F contrast, confirmed on independent events
   and for both signs. It then degrades with k (D1 +0.35: 0.932 → 0.857 by k = 10). But where the
   distortion changes the event composition inside a truth bin it loses its advantage or fails:
   D2 bump at 0.3 GeV 0.60 (carried 0.51), D3 0.68–0.71, D4c (protons) 0.26–0.31 with k = 10 at
   −0.40, D5 GiBUU 0.65, and **D5 NuWro −0.20 ± 0.17 at k = 3** (carried 0.48), with the
   low-acceptance region at −4.9. This is the mechanism the toy (§5c) isolates: a binned response
   taken from the prior is biased when the injected shape moves events within a bin, and dividing
   by a small acceptance amplifies that bias.
4. **D4d (neutron multiplicity, the hidden-variable test): every estimator ends farther from the
   target than the prior did.** The injected displacement of the `E_avail` marginal is tiny
   (0.012 for ×1.3, 0.007 for ÷1.3, against a 0.0024 prior-to-pool sampling floor), yet the reco
   distribution changes enough to be distinguished (§3). The estimators read that reco change as an
   `E_avail` change that is not there. In absolute terms (table below), at k = 3 the carried IBU
   residual is 0.016 / 0.009 and GBDT 0.014 / 0.007 — at or above the injected displacement, where
   the null cases (R2, R3, whose truth is unchanged) sit at 0.003–0.004 — and the projection on
   the injected direction is negative (the wrong way) in 14 of the 18 estimator × replicate cells
   (D1 +0.35: positive in 9 of 9). **Efficiency correction does not break *more* under D4d than it
   does on a null case at this size**: its residual (0.017 at k = 3, 0.037 at k = 10) matches its
   own null-case residual (0.008–0.017 at k = 3, 0.025–0.042 at k = 10) — its failure here is its
   general noise amplification, and a D4d-specific failure is **not established** at 600 k events.
5. **The post-hoc D5p variants** (p‖ marginal removed) are recovered less well than the
   predeclared D5 by the carried IBU (0.53 vs 0.61 at k = 3 for the GENIE-based ones): part of what
   made D5 easy was its large, well-accepted p‖-driven top-`E_avail` displacement.
6. **Response mismodeling biases the recovery by more than the historical margins.** Combined with
   D1 at +0.35, a ±5 % hadronic scale (R1) moves the carried IBU from 0.483 to 0.546 / 0.418 and
   the GBDT from 0.414 to 0.476 / 0.356 — shifts of ±0.06, three times the 0.02 non-inferiority
   margin, in the direction of the scale error. R2 (±1 % muon scale) and R3 move them by ≤ 0.003,
   consistent with §3's finding that they are not distinguishable at this size.

Absolute L1 distances (normalized seven-bin spectra, mean of 3 replicates): injected =
|target − prior|, residual = |unfolded − target|.

| case | injected L1 | IBU carry residual k=3 / k=10 | IBU eff.-corr. residual k=3 / k=10 | GBDT residual k=3 / k=10 |
|---|---:|---|---|---|
| `D1_p0.350` | 0.2721 | 0.1407 / 0.0922 | 0.0184 / 0.0389 | 0.1594 / 0.1359 |
| `D1_p0.175` | 0.1260 | 0.0693 / 0.0475 | 0.0147 / 0.0263 | 0.0830 / 0.0745 |
| `D4d_n_up` | 0.0122 | 0.0159 / 0.0192 | 0.0171 / 0.0369 | 0.0139 / 0.0139 |
| `D4d_n_down` | 0.0066 | 0.0088 / 0.0115 | 0.0176 / 0.0370 | 0.0069 / 0.0070 |
| `D4c_p_up` | 0.0278 | 0.0223 / 0.0227 | 0.0191 / 0.0390 | 0.0247 / 0.0243 |
| `D4c_p_down` | 0.0235 | 0.0165 / 0.0140 | 0.0173 / 0.0326 | 0.0188 / 0.0187 |
| `R2_x0.99` | 0.0024 | 0.0036 / 0.0063 | 0.0084 / 0.0246 | 0.0028 / 0.0031 |
| `R3_s0.10` | 0.0024 | 0.0034 / 0.0057 | 0.0094 / 0.0274 | 0.0027 / 0.0030 |
| `R2_x1.01` | 0.0024 | 0.0034 / 0.0058 | 0.0165 / 0.0421 | 0.0029 / 0.0030 |
| `R1_x1.05` | 0.0024 | 0.0219 / 0.0301 | 0.0366 / 0.0442 | 0.0106 / 0.0113 |

**Response-only cases (the null: truth unchanged, so doing nothing is correct).** Spurious
displacement of the unfolded spectrum from the undistorted pool-T target at k = 3, beside the
prior's own finite-sample distance to it:

| response case | estimator | unfolded − target L1 | prior − target L1 | unfolded − prior L1 |
|---|---|---:|---:|---:|
| `R1_x0.95` | IBU carry k=3 | 0.0219 | 0.0024 | 0.0217 |
| `R1_x0.95` | GBDT k=3 | 0.0104 | 0.0024 | 0.0102 |
| `R1_x1.05` | IBU carry k=3 | 0.0219 | 0.0024 | 0.0222 |
| `R1_x1.05` | GBDT k=3 | 0.0106 | 0.0024 | 0.0105 |
| `R2_x0.99` | IBU carry k=3 | 0.0036 | 0.0024 | 0.0036 |
| `R2_x0.99` | GBDT k=3 | 0.0028 | 0.0024 | 0.0017 |
| `R2_x1.01` | IBU carry k=3 | 0.0034 | 0.0024 | 0.0035 |
| `R2_x1.01` | GBDT k=3 | 0.0029 | 0.0024 | 0.0017 |
| `R3_s0.10` | IBU carry k=3 | 0.0034 | 0.0024 | 0.0034 |
| `R3_s0.10` | GBDT k=3 | 0.0027 | 0.0024 | 0.0015 |

A ±5 % hadronic scale mismodeling, uncorrected, makes the carried IBU manufacture an `E_avail`
displacement of L1 0.022 and the GBDT 0.010 — 8 % and 4 % of the development tilt's 0.27 —
where the truth has none. R2 and R3 stay within 0.001 of the floor. (Their "recovery" entries in
the main table are ratios of a residual to a 0.0024 sampling-floor "injection" and carry no meaning;
they are listed only for completeness.)


## 5. Reference assessment (prospective recommendations only)

### 5a. The reference model on the scored object — already measured by B1, cited

B1 (`phase_b/scalar/SCALAR_REFERENCES-20260922.md` §4.2, `results/reference_decomposition.json`,
job 58748456) evaluated the historical reference model `1-(1-a)^k` under its own assumptions on the
seven-bin `E_avail` marginal that is actually scored: **0.578 at k = 3**, against **0.695** on the
(p_T, p‖) cell displacement the historical construction used. Not re-derived here; §5b re-measures
the same construction on pool S's own maps.

### 5b. Response-aware references at the historical size and at 8× (pool S)

MEASURED by job `58782099` at commit `09dc2f2e` (`results/reference_assessment.json`): the
development injection (D1 at +0.35) on pool S, target = the tilted spectrum over all 18.86 M pool-S
events; three replicates at the historical size (disjoint) and three at 8× (4.80 M + 4.80 M events,
which pool S can only supply with a measured 51 % pairwise overlap, so their sd is a lower bound).

| estimator | size | k=1 | k=3 | k=10 | k=20 | k=30 |
|---|---|---:|---:|---:|---:|---:|
| IBU reco E_avail, misses carried | 1x | 0.265 ± 0.002 | 0.472 ± 0.004 | 0.647 ± 0.011 | 0.692 ± 0.008 | 0.685 ± 0.007 |
| IBU reco E_avail, misses carried | 8x | 0.267 ± 0.001 | 0.480 ± 0.001 | 0.662 ± 0.002 | 0.696 ± 0.001 | 0.686 ± 0.001 |
| IBU reco E_avail, eff.-corrected | 1x | 0.674 ± 0.037 | 0.904 ± 0.051 | 0.768 ± 0.198 | 0.717 ± 0.276 | 0.684 ± 0.289 |
| IBU reco E_avail, eff.-corrected | 8x | 0.655 ± 0.016 | 0.951 ± 0.022 | 0.770 ± 0.043 | 0.656 ± 0.073 | 0.605 ± 0.109 |
| *reference model realized (`diag`)* | 1x | 0.346 ± 0.005 | 0.523 ± 0.007 | 0.609 ± 0.007 | 0.644 ± 0.004 | 0.669 ± 0.002 |
| *reference model realized (`diag`)* | 8x | 0.348 ± 0.001 | 0.528 ± 0.002 | 0.618 ± 0.004 | 0.656 ± 0.006 | 0.682 ± 0.007 |
| *analytic reference model* `1-(1-a)^k` | population | 0.510 | 0.695 | 0.742 | 0.755 | 0.765 |

1x draws: 600130 prior + 600111 pseudodata events per replicate, disjoint=True, max pairwise overlap 0.000.

8x draws: 4801040 prior + 4800888 pseudodata events per replicate, disjoint=False, max pairwise overlap 0.509.

* **The historical reference construction is stable across populations:** built on pool S's own
  acceptance and displacement maps it gives 0.6950 at k = 3 (historical 0.69497) and the same
  regional values (low 0.014, moderate 0.776, good 0.976).
* **The finite-sample part of the gap is small.** The response-aware IBU (misses carried, the
  engine's rule) gives 0.472 ± 0.004 at k = 3 at the historical size and 0.480 ± 0.001 at 8×:
  8× more events close 0.008 of the 0.223 between it and the 0.695 reference (0.015 at k = 10).
  **At least 96 % of the gap at k = 3 is definitional**, not statistical.
* **The reference model does not describe its own scored realization.** Its assumptions (acceptance
  only, no smearing, misses carried) realized on the actual events and scored by the actual
  statistic (`diag`) give 0.523 at 1× and 0.528 at 8× — below the 0.556 floor derived from the
  model itself — against 0.695 for the analytic construction on the (p_T, p‖) cells. This is B1's
  0.523 on the DEV halves, reproduced on independent pool-S events and shown not to be a
  finite-sample effect.
* **Efficiency correction** reaches 0.904 ± 0.051 at 1× and 0.951 ± 0.022 at 8× at k = 3 — above
  the reference, so the reference is not a bound — and then declines with k at both sizes
  (0.60 by k = 30 at 8×), so the decline is not only statistical noise either (§5c gives the
  mechanism).

**Prospective recommendation (not a verdict, and no change to the historical floor):** a reference
for this endpoint should be computed for the estimator rule and normalization actually used, on
the seven-bin marginal actually scored — e.g. the `diag` realization (0.52–0.53 at k = 3) or the
attainable recovery of §5c — and quoted at the iteration count actually run. The historical
0.695 overstates what its own model delivers on the scored object by ≈ 0.17 at k = 3, and more
events do not close that.

### 5c. A known-function toy: does `1-(1-a)^k` bound, match or undershoot what is attainable?

`run_toy_reference.py`, jobs `58781107` (at `972ab5d4`, engine normalization) and `58782108` (at
`09dc2f2e`, adding the rate-matched variant; `results/toy_reference.json`); the toy is
deterministic and both cluster runs reproduced a local run bit for bit. One
variable x with a gamma truth density, a logistic efficiency from 0.02 to 0.75 (midpoint 0.8), and
Gaussian smearing σ = f·(x + 0.1); the historical tilt at amplitude 0.35 standardized by the toy's
own quartiles; the endpoint's seven bins. The iteration runs on **expected** histograms, so each
number is the attainable recovery of that estimator on that response, with no sampling noise.

| smearing σ/(x+0.1) | estimator | k=1 | k=3 | k=10 | k=30 |
|---|---|---:|---:|---:|---:|
| 0.00 | IBU, misses carried (engine norm.) | 0.434 | 0.659 | 0.926 | 0.992 |
| 0.00 | IBU, misses carried (rate-matched) | 0.542 | 0.762 | 0.950 | 0.992 |
| 0.00 | IBU, efficiency-corrected (engine norm.) | 0.991 | 0.991 | 0.991 | 0.991 |
| 0.00 | *reference model* `1-(1-a)^k` | 0.503 | 0.788 | 0.962 | 0.999 |
| 0.05 | IBU, misses carried (engine norm.) | 0.431 | 0.655 | 0.920 | 0.976 |
| 0.05 | IBU, misses carried (rate-matched) | 0.539 | 0.760 | 0.939 | 0.976 |
| 0.05 | IBU, efficiency-corrected (engine norm.) | 0.960 | 0.977 | 0.976 | 0.976 |
| 0.05 | *reference model* `1-(1-a)^k` | 0.503 | 0.788 | 0.962 | 0.999 |
| 0.15 | IBU, misses carried (engine norm.) | 0.410 | 0.645 | 0.870 | 0.929 |
| 0.15 | IBU, misses carried (rate-matched) | 0.517 | 0.753 | 0.889 | 0.930 |
| 0.15 | IBU, efficiency-corrected (engine norm.) | 0.884 | 0.948 | 0.930 | 0.930 |
| 0.15 | *reference model* `1-(1-a)^k` | 0.503 | 0.788 | 0.962 | 0.999 |
| 0.30 | IBU, misses carried (engine norm.) | 0.356 | 0.613 | 0.818 | 0.895 |
| 0.30 | IBU, misses carried (rate-matched) | 0.459 | 0.728 | 0.848 | 0.896 |
| 0.30 | IBU, efficiency-corrected (engine norm.) | 0.763 | 0.939 | 0.904 | 0.896 |
| 0.30 | *reference model* `1-(1-a)^k` | 0.503 | 0.788 | 0.962 | 0.999 |

Finite sample (the historical size, σ/(x+0.1) = 0.15, 3 draws):

| estimator | k=3 | k=10 | k=30 |
|---|---:|---:|---:|
| misses carried | 0.656 ± 0.005 | 0.879 ± 0.013 | 0.919 ± 0.011 |
| efficiency-corrected | 0.936 ± 0.007 | 0.917 ± 0.012 | 0.916 ± 0.013 |

**Answer (MEASURED on the toy):** the reference model is **neither a bound nor a match**.

* In its own zero-smearing limit it **overstates** what the engine's rule (misses carried) attains at
  small k: 0.788 against 0.659 at k = 3. The gap splits into 0.025 from the score's renormalization
  (the law moves only accepted mass, so the total drifts; rate-matched 0.763) and 0.104 from the
  engine's pseudodata normalization, which equates accepted totals that the injection made unequal
  — the same mechanism B1 measured on the real halves (accepted-fraction ratio 0.898).
* It **understates** what an efficiency-corrected estimator attains: 0.991 at k = 1 with no
  smearing, 0.939 at k = 3 with the largest smearing tried.
* With smearing, **neither rule converges to 1**: both approach the same fixed point (0.976, 0.930,
  0.896 for f = 0.05, 0.15, 0.30), because a binned response computed from the prior is biased when
  the injected shape changes the event composition inside a bin. Efficiency correction reaches that
  point at k ≈ 3 and then drifts down to it; carrying misses approaches it from below at the rate
  (1 − a). The reference model has no such floor.
* At the historical size (600,111 events per sample, f = 0.15, three draws) finite statistics cost
  ≈ 0.01: carried 0.656 ± 0.005 at k = 3 (expected 0.645), efficiency-corrected 0.936 ± 0.007
  (expected 0.948).

**Prospective recommendation (not a verdict):** a like-for-like adequacy reference for this
endpoint should be the estimator rule's own attainable recovery on the actual response — computed
with the engine's normalization and the score's renormalization — not `1-(1-a)^k` on the cell
displacement, which overstates it by 0.13 at k = 3 even when its assumptions hold exactly.

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

| item | value |
|---|---|
| code | branch `pet-improvement-20260922-phaseE1`; the jobs ran pinned clean checkouts at `bf1f11e7` (prep), `eba430eb` (identifiability), `972ab5d4` (references), `09dc2f2e` (assessment, toy) under `/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/`; every entrypoint through `nd-unfolding/mnv_guarded_run.py`, guard inventories beside the outputs |
| historical code | `68cf9d29` (blob ids checked at run time by `scalar_common.verify_historical_sources`) |
| inventory | `G2_FPS_MEFHC_P12.npz`, sha256 `fa6b3463…a29625` (re-hashed by the prep job); identity sidecar `01e07412…`; pools `pools.npz` `3d8faeb1…` against `pools/POOL_MANIFEST.json` |
| caches | `phaseE1/prep/poolT.npz` `4dbbfb670095…`, `poolS.npz` `57a0a78c8a41…` |
| generator predictions (D5) | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie/*_xsec3d.root`, sha256s in `calibration/d5_tables.json`; rebuilt and matched on Perlmutter (`results/d5_rebuild_check.json`) |
| task directory | `/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseE1/` (raw per-job outputs, logs, guard inventories) |
| results | `results/*.json`, digests in `results/summary.json`; tables rendered by `make_tables.py` |
| environment | `root_6_28` conda python 3.11.14, numpy 1.26.4, sklearn 1.8.0 (jobs); tests also under the NERSC python module (numpy 2.5.2, sklearn 1.9.0) and locally |

**Cost.** 30 jobs recorded in `resources-E1.tsv`, 15 completed. **451.8 CPU core-hours** as
allocated hardware threads × elapsed, i.e. **1.76 CPU node-hours** of `m3246` (the allocation's
unit; 3,463 node-hours remained on it at the end). 31.1 core-hours (0.12 node-hours) went to four
failed jobs: a PyROOT segfault in `root_6_28` (58756787), a missing `uproot` in the same
environment (58780644), a 0/0 in a diagnostic ratio that the fail-closed JSON writer refused
(58780737), and a hand-typed pin SHA the wrapper refused (58781324). Eleven jobs were cancelled
without running: the shared QOS left them PENDING on Resources for six hours, and the work was
re-cut into ≤ 30-minute pieces for the `debug` QOS (one exclusive node each, two at a time), which
is why each completed job is charged a whole node. No GPU was used.
