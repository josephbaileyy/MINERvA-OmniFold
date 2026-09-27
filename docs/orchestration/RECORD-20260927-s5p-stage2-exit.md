# RECORD 2026-09-27 — s5p (`OI-193`) Stage 2 exit: construction questions answered; no useful measurement design at the frozen targets; the joint-test branch is feasible

**CITABLE FOR:** the Stage-2 results of campaign `s5p-20260926` under contract amendments 1–3:
- the numerical/bootstrap overlap (study N);
- the six s5e calibration failures (study C);
- the convergence and capacity study (study K);
- the prior-variation linearity check (study P);
- the rule-based configuration decisions of amendment 2;
- the development estimates of the frozen targets T1–T3 and T5;
- the remaining-work forecast.

Every number is from the committed receipt
[`state/s5p/stage2/stage2_receipt.json`](state/s5p/stage2/stage2_receipt.json) (sha256 `0daa7cd8…`), produced
by `nd-unfolding/s5p_stage2_analyze.py` at `da53a9f1` from the Stage-2 products under
`/pscratch/sd/j/josephrb/s5p-20260926/runs/`, or from the forecast
[`state/s5p/stage2/forecast.json`](state/s5p/stage2/forecast.json) (inputs
[`forecast-inputs.json`](state/s5p/stage2/forecast-inputs.json)).

**NOT CITABLE FOR:** any coverage verdict, adopted product, corrected central value or generator comparison.
No observed-data central value was compared with any prediction. The data shifts in study P are widths.
**Status:** development evidence. It is not yet independently reviewed; the Stage-3 admission review covers it.

## 1. What ran (development stage, all admitted by the s5p meter)

| study | products | notes |
|---|---|---|
| N numerical/bootstrap overlap | N1 data: base, 20 edge-safe jitters, 50 replicas paired with the s5e replicas; N2 nominal pseudo 930000; N3 GiBUU pseudo 931000 (each 20 jitters, 40 paired replicas) | controls: the N1 base equals s5e `data_R` bitwise, and replicas b1, b2 equal s5e `boot_b1`, `boot_b2` bitwise; no jitter changed grid membership |
| C calibration failures | C1 bootstraps of 930001–930004 (40 replicas each); C2 100 nominal experiments (930100–930199); C3 40 fixed-split experiments; C4 W3 pseudo 932000 (40 replicas) | 160 nominal experiments in total with the s5e K1/assessment sets |
| K convergence and capacity | noise-free B0 traces to k = 200: nominal and W3 complete; GiBUU, q3 and W1 from checkpoints, k ≤ 40/30/40 at the receipt and still running; capacity 400/31 to k = 10 for GiBUU, q3, W3 | the first B0 departure traces hit their 10 h limit (incident in the state file); re-run with checkpoints and a 24 h limit |
| P prior variations on data | R on the data with the MC prior reweighted to D1–D5, plus CV and nominal-prior controls | the first run had a denominator defect: repaired, test red on the defect, re-run once |
| I input-dump pilots | one lateral endpoint (12 min, 1.55 GB); detector dump refused as designed (row alignment), repaired and queued | — |

Row-order and estimator checks: 628 products re-read from metadata. Every refinement classifier carries R's
400/31, random_state 45; every OmniFold estimator carries F2. Violations: 0.

## 2. Answers

**N — the numerical floor is inside the data bootstrap.** On the data, the edge-safe rounding spread per
reported functional has these medians:
- J 0.233%, H2 0.177%, EW 0.151%;
- the refit-per-replica bootstrap σ is 0.368% / 0.291% / 0.254%.

Each bootstrap replica carries the base construction's rounding noise at the same size: σ_num,rep / σ_num,base
has median 1.02 (J), 0.96 (H2), 1.07 (EW), and σ_boot² ≥ σ_num,rep² for 100% of functionals. So the
component is **ABSORBED**: about 37% of the data bootstrap variance on J is rounding noise.

On nominal pseudo-data the same spread is 20× smaller (0.016% on J against a 0.20% bootstrap σ). At the GiBUU
departure it is 7× larger than nominal (0.114%). The estimator's chaotic sensitivity grows as the data move
away from the MC prior, and the real data behave like a departure. This explains the s5e review's M3
observation (data σ 1.57× pseudo σ).

T3 is evaluated relative to the TOTAL σ, which is ≥ 6% in every definition (§4). The numerical spread
(median 0.2%, max 0.62%) is below 0.1 of it, so **T3 is met**.

**C — the six s5e calibration failures are addressed.** EW41, J85, J162, J206, J215 and J232 all fall inside
T5's [0.80, 1.25] over 160 nominal experiments (SE 0.056) with the statistical width taken as the mean of six
per-experiment bootstrap widths (700000, 930000–930004) instead of the one development experiment's:

| functional | pull SD, single σ | pull SD, mean σ | mean pull |
|---|---:|---:|---:|
| EW41 | 1.406 | 1.188 | +0.08 ± 0.09 |
| J85 | 1.197 | 1.091 | +0.01 ± 0.09 |
| J162 | 0.882 | 0.954 | −0.09 ± 0.08 |
| J206 | 1.444 | 1.065 | −0.05 ± 0.08 |
| J215 | 1.522 | 1.079 | −0.05 ± 0.09 |
| J232 | 1.294 | 0.998 | 0.00 ± 0.08 |

- **The cause is the σ estimate, not bias.** A single experiment's bootstrap σ is not every experiment's:
  per-functional σ varies by 12–19% (CV) from experiment to experiment. Every mean pull is consistent with 0.
- **With the mean σ,** 98% of J, 95% of EW and 100% of H2 functionals lie in T5's band.
- **The MC split contributes** about 33% of the pseudo-experiment variance (fixed/varying split SD 0.82).
- **At physical departures** the bootstrap σ is 1.5–1.9× the nominal σ. It stays calibrated there: ensemble
  SD / departure bootstrap σ is 1.06–1.16. So σ must be evaluated at the experiment's own truth, which the
  real-data bootstrap does.

**K — iterations and capacity do not reduce the model dependence at the rule's resolution.** The noise-free
T2 proxy is the median over reported cells with a > 1% departure of |bias| / |departure|. M is its maximum
over the development alternatives:

| k | B0, M_J | B0, M_H2 | capacity 400/31, M_J (3 truths) | capacity, M_H2 |
|---:|---:|---:|---:|---:|
| 1 | 0.712 | 0.565 | 0.700 | 0.557 |
| 5 | **0.626** | **0.314** | 0.606 | 0.288 |
| 10 | 0.635 | 0.384 | 0.550 | 0.288 |
| 20 | 0.650 | 0.398 | — | — |
| 30 | 0.682 | 0.392 | — | — |

- **W3 (NuWro/GENIE 3D) sets M and does not converge.** Its J median bias stays at 5.6–6.6% from k = 5 to 200,
  and its 5D reco-fold χ² plateaus near 4,700 against a departure visibility S_dep = 68,263. The estimator
  reaches a fixed point that does not reproduce the departed reco distribution. That is a representation
  limit of the step-1 classifier, not an iteration limit.
- **GiBUU and W1 improve slowly** (GiBUU H2 0.314 → 0.244 at k = 20; W1 H2 0.225 → 0.184).
- **q3 does not improve.**
- **Capacity 400/31 changes M by 3–8% at k = 5.**

T2 needs ≤ 0.25. No configuration reaches it on J at any tested k (to 200) or capacity. H2 reaches 0.244 for
GiBUU alone, but W3's H2 ratio is ≥ 0.31 at every k ≥ 5 for B0.

**P — the data-side prior variation measures the bias.** After the denominator repair, the shift of the
real-data result when the MC prior is reweighted to a vertex agrees with minus the bias at that vertex:
- W3: correlation 0.92, slope 1.12 on J; 0.92 and 1.07 on EW;
- W2: 0.73 / 0.94 (J / EW), slope 0.92 / 0.99;
- the pre-repair diagnosis gave 0.94–0.96 for GiBUU and W1 after restoring the reweight.

So max_k |shift_k| over the vertices is an empirical, slightly conservative bound on the regularization
bias over their hull. The nominal-prior control differs from the CV path only through float64 weights: it is
equal on every reported functional to < 1e-5 relative, not bitwise.

## 3. Configuration decisions (amendment 2 rule, applied mechanically)

- **K_afford.** The forecast gives ≈ 20 iterations at B0 capacity: all remaining work is 222.6 CPU-equivalent
  node-h at k = 20 against ≈ 239 available after reserves, and 328.7 at k = 30. For capacity 400/31 it is 5
  iterations: 190.8 at k = 5, 371.1 at k = 10.
- **Configuration 2: NOT FROZEN.** No k ≤ 20 gives M_J ≤ 0.25 or M_H2 ≤ 0.25. The minimizer of M_H2 over
  k ∈ {10, 15, 20} (0.384) does not improve on k = 5 (0.314) for J or H2. The rule's clause *"If K2 = 5 is not
  improved upon … no configuration 2 is frozen"* applies.
- **Configuration 3: NOT FROZEN.** Capacity at the affordable k = 5 lowers M by 8% (H2) and 3% (J), against
  the rule's ≥ 20%.
- **Selected estimator: configuration 1 = R** (5 iterations). No development revision was used or is
  available that the rules support.

## 4. The frozen targets at development resolution

The bounded unfolding-model component at R, with scale s = 1 (the smallest envelope the vertices allow), is
h_f = max_k |shift_k,f| over D1–D5 (reported cells):

| definition | h median | h 90% | dominant vertex |
|---|---:|---:|---|
| RD1 J | **12.0%** | 38.6% | GiBUU (60 of 109 cells) |
| RD2 H2 | **9.6%** | 22.5% | GiBUU (13 of 27) |
| RD3 EW | **13.4%** | 39.2% | GiBUU (29 of 39) |

- **T1** (median total 68% half-width ≤ 10%) is **unattainable in RD1 and RD3 from h alone**, because the
  half-width is σ_prob + h ≥ h. RD2 fails as well: every functional's σ_prob contains at least the flat 1.4%
  normalization block, so its half-width is ≥ h_f + 1.4% cell by cell, and the median is ≥ 11.0%.
- **T2** fails in every definition:
  - model component median ≤ 5% (it is 9.6–13.4%);
  - recovery ≥ 75% of a generator-sized departure (0.25 against the measured 0.31–0.63).
- By the amendment-1 selection procedure, RD1 and RD2 fail T2, so RD3 is the fallback. RD3 fails T1.

**Disposition of the measurement branch: no reporting definition can meet the frozen useful-precision
targets with any configuration the rules support within the budget.** Handoff Stage 2: *"If no useful
affordable design is supported, finish independent work and record the limitation."* The limitation is
scientific, not financial. The measurement's prior dependence is ≈ 10–13% per coarse joint cell, comparable
to the generator differences a user needs to resolve (3.7–16%, Stage 1). Nothing is constructed for the
measurement branch. The targets were frozen before Stage 2 and are not relaxed; the retrospective motivations
recorded in amendment 1 stand. The adopted trunk `3d7465f6…` and its projection are unchanged.

## 5. What stays feasible: the calibrated joint test

A test of H0(G) is calibrated by simulating the complete procedure (pseudo-data at G's truth, background,
refinement, R, statistic) with the nuisances drawn from their priors. Its validity does not rest on the
measurement's bounded model component: the estimator's bias under G is part of the simulated null.

- **Power.** The prior dependence costs power, not validity. It is measured against the frozen P1–P3 at
  Stage 5/7.
- **Cost.** The forecast prices the inference branch at 26.5 CPU-equivalent node-h at k = 5 (5 nulls × (199 +
  100) experiments plus 600 power experiments), before the lateral surrogate inputs and verification.
- **Inputs built.** The five 5D generator predictions are built and validated (`state/s5p/gen5d/`), as is the
  MnvTune v1 prediction.
- **Stage 3 for this branch:** the joint design, its nuisance treatment, its size, precision and power
  requirements, and costs, independently reviewed before any null ensemble is run.

## 6. Unresolved uncertainty sources (map)

| source | status |
|---|---|
| statistical (data, MC, template, refinement refit) | refit bootstrap; calibrated at nominal and at departures (C) |
| numerical (rounding-scale) | inside the data bootstrap (N); ≤ 0.1 of the total σ |
| regularization / unfolding model | measured: h 9.6–13.4% median at R, by data-side prior variation (P, linear response verified) — the limiting source |
| flux, GENIE model, detector (weight-only), lateral, normalization | infrastructure built (`s5p_universe.py`, `s5p_input_dumps.py`, `s5p_assemble.py`), not run: no measurement production is admitted |
| background model | per-universe background weights in the bank (refit per universe) |
| MC-split / finite-MC | inside the pseudo-experiment ensembles; the data bootstrap resamples MC Poisson(1) |

## 7. Spend at this record

Development stage, meter (see the state file's measure receipt): within 46.527 CPU and 17.235 GPU node-h. The
running checkpointed traces (`58932367`) and the capacity array (`58904836`) are still open, and their
reservations are counted until they close.
