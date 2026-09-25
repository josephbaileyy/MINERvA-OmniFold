# OUTCOME 2026-09-25 — s5n (`OI-191`) Stage 1: STAGE1_FAIL; no Stage 2; campaign CLOSED

**CITABLE FOR:** the development-stage results of the `negweight-refined` successor family `N`
(contract [`state/s5n/contract.json`](state/s5n/contract.json), frozen `75bd22c0`), each independently
re-measured from operands. It also records the terminal branch those results select, the recomputed
feasibility, and the costed next increments. Headline results:

- `negweight-refined` reduces the purity method's nominal-truth highest-W closure bias about fifteen-fold;
- a residual background-related bias of up to ≈ 1% remains in a set of joint cells;
- the F2 estimator itself does not follow physically anchored truth departures (up to 74%);
- the real-data method sensitivity (purity versus `negweight-refined`) is measured.

**NOT CITABLE FOR:** any coverage verdict, since no validation seed was run; a measured bias of the
real-data result; a corrected central value; or any change to the adopted trunk `3d7465f6…` or to the
s5c/Z grades. **Status:** development evidence, independently verified (two rounds,
[`state/s5n/stage1/review-round-1.md`](state/s5n/stage1/review-round-1.md)). Receipt
[`state/s5n/stage1/dev_receipt.json`](state/s5n/stage1/dev_receipt.json), produced by
`nd-unfolding/s5n_analyze_dev.py` at `e76cb126`.

Campaign: [`CAMPAIGN-s5n-20260925-index.md`](CAMPAIGN-s5n-20260925-index.md). Authority:
[`AUTHORIZATION-20260925-negweight-refined-successor.md`](AUTHORIZATION-20260925-negweight-refined-successor.md).

## 1. What ran

The estimator is family `N`: the s5c F2 deterministic LightGBM OmniFold (5 iterations) with the driver's
`negweight-refined` measured side. The refinement is the driver's own `refine_stay_positive`, run with the
F2 parameters. The runs were:

- 180 background-inclusive development experiments (60 each at nominal truth, an E_avail shape departure
  and the repaired q3 departure);
- a 200-replica bootstrap under the repaired resampling;
- the controls, the real data, and two diagnostics;
- **no validation seed.**

Development seeds were 300000–349999. Deploys: `bd0faf0b` (controls, grid, σ), `82dc1517` and
`cac87ced` (diagnostics). The departures are:

- **E_avail shape:** a per-bin truth reweight equal to the GiBUU / GENIE v2 (untuned) E_avail shape
  ratio, 0.70–1.33, with the in-grid total preserved. This is the *physically anchored* departure
  ([`state/s5n/eavail-ratio-gibuu-over-genie.json`](state/s5n/eavail-ratio-gibuu-over-genie.json)).
- **q3:** the repaired `q3_given_eavail_w` deformation at a = 0.3, a declared stress amplitude, not an
  anchor. It preserves the (E_avail,W) weight marginal to 6e-14, and all 42 physical (E_avail,W)
  cross-section functionals to ≤ 3.8e-7.
- Only the non-physical `EW_all_ones` row, a plain sum of differential values, changes (0.903). An
  interim reading that the M1 functionals move by 9.7% was the author's error and is withdrawn.

Receipt: [`state/s5n/stage1/truth_check.json`](state/s5n/stage1/truth_check.json).

## 2. Controls (contract `stage_1_development`)

| control | result | numbers (full n, independently reproduced) |
|---|---|---|
| C0 baseline reproduction | **PASS** | purity mode reproduces s5c `d1_split_s4` bitwise (xsec and xtrue) |
| C1 refinement in every path | **PASS** | 385 products (plus 4 diagnostics) carry content-checked refinement evidence. Over nominal products: refined/signed sum 0.999994–1.000020, clipped fraction 8.4e-5–5.4e-4. The driver arm, under `s5c_with_estimator.py`, ran the refinement with the F2 parameters (no problems) |
| C2 equivalence and reproducibility | **PASS** | no second implementation exists (the successor calls the driver's function; `test_s5n_cluster.py` checks it bitwise against a direct call). Repeat and estimator-seed-43 products are bitwise equal. Row permutation moves functionals by at most 4.1e-11 σ |
| C3 nominal background-inclusive closure | **FAIL** | max \|t\| = 14.4 (J88 +0.91%, mean pull 2.02). 89 of 153 functionals have \|t\| > 3.6, and 78 have \|mean pull\| > 0.5 with \|t\| > 3. Pooled coverage 0.603 / 0.870; minimum 0.183 / 0.467 |
| C4 E_avail shape departure | complete | pooled 68% coverage 0.027; 136 of 153 functionals have zero 68% hits in 60 experiments; EW29 +74.1% |
| C5 q3 departure | complete | pooled 68% coverage 0.027; 141 of 153 functionals with zero hits; largest residual EW36 37.4% |
| C6 σ calibration | pooled calibration correct, per-functional not | pull SD median 0.960, but min 0.558 and max 1.725, outside ±3 sampling SE (0.092) |
| C7 real-data method sensitivity | measured | §4 |
| C8 signal-only reference | description only | n = 4; max \|mean residual\| 0.31%; highest-W column −0.06% to −0.20% |

## 3. What the development evidence establishes

1. **`negweight-refined` removes most of the purity method's nominal-truth bias.** The highest-W column of
   the (E_avail,W) projection moves from −3.5% to −4.1% under purity (s5c D1) to +0.11% to +0.24%. The
   corner EW41 moves from +1.66% to +0.24%. The remainder is still significant (EW41 t = 5.5).
2. **A background-related nominal bias of up to ≈ 1% remains.**
   - A set of joint cells is +0.6% to +1.1% high with t ≈ 14: J85, J88, J89, J93, J94, J97, J98, J106,
     J107, among others. The total is +0.13% (mean pull 1.5).
   - Signal-only on the same functionals is ≈ −0.2%.
   - **The mechanism is not established.** The biased cells are not the background-rich ones (Spearman
     0.38 with the background fraction). The refinement's own reco-level local subtraction error (median
     0.48%, max 4.2%, the same pattern on data) does not track the truth-level excess (Spearman 0.07).
3. **The F2 estimator does not follow physically anchored truth departures.** This is the decisive result.
   - At the E_avail shape departure, the unfolded (E_avail,W) cells deviate from truth by a median 9.7%
     and up to 74% (EW29). The largest cells are several percent off (EW7 1.188 × nominal against a truth
     of 1.273).
   - At the q3 departure the (E_avail,W) truth equals nominal, yet the unfold carries a reco-level
     (E_avail,W) distortion into truth (EW36 +37%).
   - **Signal-only experiments on the same seeds reproduce both** (correlation 0.9994 and 0.9993; largest
     differences 3.0 and 1.45 pp). It is therefore a property of the estimator, not of the background
     method.
   - The npz loop (`omnifold_nn_core.omnifold_loop`) and the driver's loop
     (`unbinned_unfolding/python/omnifold.py`) were compared line by line and are algorithmically
     identical. The behaviour is **measured on the npz loop and transfers to the driver by code
     identity**, not by measurement.
   - Not yet separated: step-1 underfit, the regressor's extrapolation for the ≈ 38% of events that fail
     reconstruction, and the 5-iteration stopping.
   - **Withdrawn:** the author's interim reading "prior dependence, not a defect", based on a
     prior-equals-truth diagnostic. That diagnostic's agreement with 1/r − 1 is forced by its own
     normalization; review round 1, F1.
4. **The repaired resampling.** Each pseudo-event is resampled individually (Poisson(k)), the template MC
   gets Poisson(1), and the refinement is refit on every replica. This is the unit-weight real-data
   bootstrap. The s5c pseudo-data bootstrap (k × Poisson(1)) over-dispersed the data-statistical variance
   by 1.415 (measured on the input npz; `KNOWN_ISSUES.md` 78). Limitation: the bootstrap omits two
   finite-MC terms present in the ensemble (B-half migration; source-versus-template variance), so
   pseudo-experiment coverage reads slightly low (review F6).

## 4. Real data: method sensitivity, not a measured bias

Negweight-refined minus purity on the real data, relative, with the same estimator and inputs (npz path):

- highest-W column: EW5 +0.60%, EW11 +0.03%, EW17 +0.06%, EW23 +0.07%, EW29 +0.73%, EW35 +1.12%;
- EW41 −1.22%; total −0.12%;
- median |difference| over the 153 functionals 0.36%; maximum 1.42% (J93);
- refinement on data: refined/signed sum 1.0000029, clipped fraction 2.8e-4.

The signs match the purity bias seen in simulation, but the sizes are an order of magnitude smaller. This
compares two methods. It does not measure the real data's bias. The driver path and the npz path differ on
data by up to 1.29% (median 0.19%, `KNOWN_ISSUES.md` 79), which is comparable to the method sensitivity
itself.

## 5. Terminal branch, and why no revision is used

The contract's Stage-2 precondition requires C0–C3 to pass. **C3 fails, so the branch is `STAGE1_FAIL`.**
Two blockers are separable:

- **(i) The C3 nominal bias.** It is background-related (+1% with background against −0.2% signal-only). A
  background-treatment revision might plausibly reduce it.
- **(ii) Coverage under the declared physical departures.** This is what makes any revision pointless.
  - Tier-S assurance is **0.000** at every n up to 40,000 at the development estimates: the minimum
    per-functional coverage is 0.18 at nominal and 0.00 at both departures
    ([`state/s5n/stage1/feasibility.json`](state/s5n/stage1/feasibility.json), `nd-unfolding/s5n_feasibility.py`).
  - Blocker (ii) belongs to the estimator. The family fixes 5 iterations and the F2 parameters. The
    contract's revision rule covers the background treatment, sampling model, σ object and interval
    construction, and bars architecture and hyperparameter change. **Changing iterations or classifier
    capacity is outside this delegation and is Joseph's decision.**
- **The one in-rule option, disposed.** An interval-construction revision could add a model-dependence
  allowance, calibrated on the GiBUU anchor and validated on the committed NuWro anchor. It is not
  attempted, for three reasons:
  - The allowance would have to be ≈ 10% (median) up to 74%, against a statistical σ ≈ 0.2%.
  - The resulting bands would over-cover at nominal, so the 68% and 95% labels would not describe them.
    The s5c review-round-2 objection to amendment 3 applies directly.
  - Their widths would exceed the adopted total σ in the highest-W cells (3.7%–9.8%). Such a band is a
    model-uncertainty component (Tier-T territory) with a physical scope of one generator pair. It is not
    a qualified statistical-scope interval.

No development revision was used (0 of 2). No validation look occurred.

## 6. Feasibility and cost of the complete remaining work (recomputed; the old forecast is not a guarantee)

Measured cost is 0.0136 CPU node-h per development experiment and 0.0099 per bootstrap replica, including
whole-node idle tails. The complete Stage 2 at the s5c design (n = 4,000 per grid point, m = 459):

| item | CPU node-h |
|---|---:|
| Tier S | ≈ 163 |
| Tier T at two nuisance points | ≈ 109 |
| σ bootstraps | ≈ 5 |
| driver-path systematic construction | ≈ 4 |
| 20% verification floor | 65 |
| **total** | **≈ 346** |

That exceeds the 320.6 CPU node-h remaining, and fits only by also using the GPU pool (115.2 GPU node-h).
It would buy a pass probability of **0** at the development estimates.

Even perfectly calibrated intervals would need **21,248** experiments per grid point for 80% assurance at
the 68% gate (11,789 at 95%), about **867 CPU node-h** for Tier S alone, more than twice the successor cap.
**Affordability is not the binding constraint. The scientific result is.**

## 7. Consequences

- **No measurement uncertainty checkpoint qualifies. Nothing is adopted.** The adopted-under-exception
  state is retained with its four travelling measurements.
- The deliverables' statement that closure tests validate the 5D central values carries two new
  qualifications, recorded in `KNOWN_ISSUES.md` 75 and 77. The first is the background method's nominal
  bias: ≈ 4% under purity, ≤ ≈ 1% under `negweight-refined`. The second, more serious, is the estimator's
  response to physically anchored E_avail shape departures: several percent in the largest (E_avail,W)
  cells and up to 74% in the highest-W column, carried by no covariance.
- **Spend (Stage 1 = the whole successor):** 4.601 CPU plus 0.309 GPU node-h (1.24 A100-h), all in stage
  `development` (limits 32.52 / 11.52), measured by the meter at 22:06:24Z. Every admission is closed
  ([`state/s5n/stage1/meter-measure-20260925T2206Z.json`](state/s5n/stage1/meter-measure-20260925T2206Z.json)).
  Envelope totals including s5c: 24.687 of 345.27 CPU node-h, and 10.095 of 125 GPU node-h (40.38 of 500
  A100-h).

## 8. Costed next increments (each a separate decision)

| # | increment | what it buys | forecast (CPU node-h) |
|---|---|---|---:|
| 1 | Unfolding-model (regularization) uncertainty for the published 5D and (E_avail,W) products: unfold generator-anchored pseudo-data (GiBUU, NuWro and GENIE E_avail/q3 shapes; ≈ 20 truths × 20 experiments), fold the residual into a declared model component | the missing component in §7, for the adopted result's quoted uncertainty | ≈ 6 |
| 2 | Separate the estimator failure: forward-fold check, the reco-failing regressor, a fixed iteration scan (diagnostic only) | which part of the loop fails; input to a new family | ≈ 2–4 |
| 3 | A new estimator family (more iterations under a frozen stopping rule, or a higher-capacity classifier), with its own development and fresh validation. Outside this delegation: Joseph | a chance of coverage under physical departures | development ≈ 20–40; Tier S ≈ 163 at conservative coverage, ≈ 867 if exactly nominal |
| 4 | The C3 residual mechanism (refinement capacity, reco-level forward-fold) | whether a background revision can close nominal to < 0.2% | ≈ 2 |
| 5 | Driver-path versus npz-path parity (1.3% on data) | which path an adopted product may use | ≈ 1 |
| 6 | Joint-5D inference | unchanged from the s5c closeout: needs a qualified covariance first | ≈ 440 per generator |
