# Decision rule — KNOWN_ISSUES 85 bootstrap-on-one-toy diagnostic (2026-10-06)

Committed before any job runs. Approved by Joseph on 2026-10-06, in the 2D lane's session: arms B + T,
100 runs, at most 12 CPU node-hours on m3246, shared and regular lanes only, no premium or overrun.

## No outcome changes any quoted number

No outcome of this diagnostic changes the quoted 2D statistical band (`VL170`) or any printed number
before publication. Outcome (a) would open a **method question**: why the production data bootstrap
scatters more than genuine Poisson fluctuations in this unfolding. It would **not** trigger a rescale.
Outcome (b) means **the bootstrap is faithful on same-event pseudo-data**. It does not show that the band
is calibrated for real data, and it is not to be described as "the band is fine".

## Question

`KNOWN_ISSUES.md` 85 measured that the data-statistics part of `VL170` is about 1.6× wider in σ than the
scatter of the VL169 closure toys (toy-to-band data-variance ratio g, median 0.40). Two explanations are
untested:

- **(a)** the production data bootstrap over-scatters;
- **(b)** the closure toys under-scatter, because their pseudo-data sit on the training MC events.

## Design

The driver is `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`, with the production estimator and
arguments (`--iters 5 --estimator lgbm --seed 1`). The MC is unresampled in both arms
(`--no-mc-bootstrap`), so only the data stream varies.

- **Arm T** (true scatter), 50 runs: toys 301–350. Each draws fresh pseudo-data
  `k_i ~ Poisson(w_reco_i)` on the closure events. These toy indices are unused by the coverage study,
  which reserved 1–200 and 9001–9003.
- **Arm B** (bootstrap), 50 runs: one base pseudo-data sample, toy 1's counts. Each replica S = 1–50
  resamples every event's count as `Poisson(k_i)`, which is the production per-event Poisson(1)
  bootstrap summed over the event's k copies (`toy_design.draw_data_bootstrap`). Seeds come from a
  disjoint namespace (`toy_design.bootstrap_seed`).
- **Real-data bootstrap** (exists, no new runs): `uq/boot_data/`, 200 data-only production replicas.
  KNOWN_ISSUES 84 did not touch that stream, and its mean equals `VL170`'s to 1%.

## Statistics

Per reported bin b (the 205 bins of `VL169`), the relative spread is σ = std(hXSec2D, ddof = 1) / mean
over each arm's replicas.

**Size correction.** It goes in one direction only, and arms B and T need none between them. The toy
pseudo-data are MC-sized and background-free, while the real-data bootstrap varies p_b · D_b with fixed
purity p_b. So a toy's relative data-stat σ exceeds a real-data one by √(r_b / p_b), where
r_b = `prod_mean` / T is the data/MC ratio per truth bin (median 1.145) and p_b is the reco-bin purity at
the same index (median 0.975). Before any comparison with the real-data bootstrap, **toy-side σ is divided
by √(r_b / p_b)**. In the median bin the correction is about 8%, small against the factor of 1.6 that
the rule has to resolve.

The three per-bin ratios:

- ρ₁ = σ_B / σ_T (no correction);
- ρ₂ = (σ_B / √(r_b / p_b)) / σ_realboot;
- ρ_T = (σ_T / √(r_b / p_b)) / σ_realboot.

Per bin, ρ₂ = ρ₁ · ρ_T exactly. For each ratio we report the median and p16/p84 over the 205 bins, and a
95% interval for the median from resampling replicas within each arm (2000 resamples). M₁, M₂ and M_T
denote the medians.

## Rule

Applied in this order.

0. **Premise check.** M_T must lie in [0.50, 0.80]. KNOWN_ISSUES 85 implies about 0.64 by a different
   route. If it does not, the outcome is **"premise not reproduced"** and no attribution is made.
1. **Consistent with (b), "the bootstrap is faithful on same-event pseudo-data":** the 95% interval of M₁
   lies within [0.90, 1.10], **and** M₂ ≤ 0.80.
2. **Consistent with (a), "the production data bootstrap over-scatters":** M₁ ≥ 1.30 with its 95%
   interval above 1.20, **and** M₂ lies in [0.90, 1.10].
3. **Mixed:** anything else. The share of the log-gap attributed to (a) is reported as
   ln M₁ / ln(1 / M_T), with the remainder attributed to (b).

The share in step 3 is reported for every outcome.

## Limits

- One base pseudo-data sample, so arm B measures the bootstrap at one point.
- Purity is per reco bin, used at the truth-bin index.
- The diagnostic tests the data stream only.
- It is not the held-out-MC re-test, which stays deferred past the publication package
  (Joseph, 2026-10-06).

## Budget

The pilot is one arm-T and one arm-B job on the shared lane (64 CPUs). It stops if the projection for
100 jobs exceeds 12 node-h. The balance is measured before and after with `iris`. Node-hours are
ElapsedRaw/3600 × billing/256 from sacct.
