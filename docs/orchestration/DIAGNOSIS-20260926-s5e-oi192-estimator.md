# DIAGNOSIS 2026-09-26 — s5e (`OI-192`): why the 5D estimator misses physical departures, and where the nominal background bias comes from

**CITABLE FOR:** the diagnosis items D0–D7 of [`state/s5e/contract.json`](state/s5e/contract.json)
(amendments 1–2), measured on development seeds and noise-free constructions. The numbers come from the
receipt [`state/s5e/diag/diag_receipt.json`](state/s5e/diag/diag_receipt.json) (sha256 `f0880725…`),
produced by `nd-unfolding/s5e_analyze_diag.py` at `700797e3` from the committed-table products under
`/pscratch/sd/j/josephrb/s5e-20260925/runs/diag/`. The record also states which causes the contract's
attribution rule lets it name.

**NOT CITABLE FOR:** a coverage verdict, a corrected central value, or a measured bias of the real
data. It changes no adopted product and no s5c/s5n grade. **Status:** development evidence; the
independent review is pending (see the campaign index).

## 1. What ran

| allocation | contents | CPU node-h (meter, closed) |
|---|---|---:|
| `58881080` | D3 traced pseudo-experiments (24, K = 20); D7 background pairing (40) | 1.587 |
| `58881083` | D5 probes; D4 noise-free scans (K = 30); D2 asimov and data probes; D1 driver runs; D6 geometry | 2.092 |
| `58886919` | amendment-2 repairs: edge-safe precision probe, sentinel mask probe, driver parity | 0.253 |
| **diagnosis total** | 83 products + geometry | **3.932 of 10.0** |

Every traced unfold passed the tracer's per-iteration bitwise checks (its rebuilt `w_pull`/`w_push` equal
the weights the production loop passed to its next step), so the traces describe the unfolds that ran.

## 2. D0 — the evidence reproduces

**28 of 28** traced iteration-5 unfolds equal their s5n development products bitwise. These are 12
background-inclusive (nominal, E_avail shape, q3; four seeds each), 8 signal-only, and the 8 D7 re-runs
at seeds 300004–300011. For each, `xsec` and `xtrue` both match. The traced real-data unfold equals the
s5n `c7` npz product bitwise.

## 3. Pipeline differences (D1, D2 and the amendment-2 repairs)

**The departure failure is the same on the driver path: now measured, not inferred from code identity.**
The unmodified driver ran in `--closure` mode with the F2 configuration, with the deformation injected
after a bitwise row-alignment proof. It reproduces the npz path's noise-free residuals:

| departure | driver: median / max \|EW residual\| | npz, k = 5 | max \|difference\| | correlation (42 EW cells) |
|---|---|---|---:|---:|
| E_avail shape (GiBUU/GENIE, a = 1) | 10.50% / 73.78% (EW29) | 10.85% / 73.51% (EW29) | 1.78 pp (EW17) | 0.9998 |
| repaired q3 (a = 0.3) | 4.95% / 37.63% (EW36) | 5.00% / 37.77% (EW36) | 0.87 pp | 0.9999 |
| nominal | ≤ 1e-7 | ≤ 1e-7 | — | — |

**Input parity (repaired, amendment 2).** The driver admits 2,801 fewer truth-passing rows than the npz,
exactly the rows with a −9999 truth sentinel (`KNOWN_ISSUES.md` 76). With those rows removed, every
array matches:

- pass masks and both weight arrays are bitwise equal;
- every coordinate's float32 cast is equal;
- coordinates differ only at float32 rounding (≤ 7.6e-6 absolute).

The sentinel rows carry 389 events of reco-passing weight (0.011%).

**`KNOWN_ISSUES.md` 79 (driver versus npz on data, 1.29%): no pipeline factor is named.** One factor at a
time:

- **Per-estimator random states** (42/43/44 against 42/42/42): bitwise inert, on asimov and on data.
- **float64 upcast of the same values:** bitwise inert.
- **Edge-safe float32-ulp perturbation:** moves the data result by up to 1.23% and 0.98% (two seeds;
  median 0.18%/0.19%), and the noise-free E_avail departure by up to 0.97% (median 0.09%).
- **The driver's sentinel mask applied to the npz path:** moves the data result by up to 1.14% (median
  0.14%). It does not shrink the driver–npz difference: 1.29%/0.19% (max/median) before, 1.04%/0.28%
  after.

The difference therefore sits at the scale at which the deterministic estimator responds to
rounding-scale input changes, so the D2 rule names no factor for it. On the noise-free E_avail departure
the mask does account for the largest path difference (1.78 → 0.92 pp, within the 0.97% probe scale).

The refinement differences on data are consistent with the same input differences, and no separate
refinement defect appears:

- refined sum 3,972,466.85 (driver) against 3,972,476.93 (npz);
- clipped rows 1,279 against 1,313.

**A new estimator property follows, and it matters beyond `KNOWN_ISSUES.md` 79.** The F2 estimator's
real-data output has a numerical reproducibility floor of about 1% (max) and 0.2% (median) under input
changes of float32-rounding size. That is comparable to the statistical σ (≈ 0.2%). No covariance
carries it.

**Withdrawn.** The original D2(b) jitter probe moved exact zeros on the grid edge 0 out of the grid:

- 293,292 MC truth E_avail values;
- 231,685 MC reco W values;
- 48,082 data reco W values.

Its data result (up to 30%) is therefore not a rounding measurement. It stays in the receipt, labelled
as confounded.

## 4. The estimator's response to departures (D3–D6)

**Step 1 fits the reco data; step 2 transfers it faithfully in truth cells; the result folds back almost,
but not exactly, onto the data.** On the four-seed background-inclusive E_avail departure (D3):

- **Step 1.** Its reco-level forward fold agrees with the measured side at noise level. The EW-projection
  χ² between measured side and step-1 fold is 84, against 119 between the measured side and the folded
  truth model.
- **Step 2.** It reproduces step 1's truth-cell weight sums to 0.11% (median) and 0.49% (max) at k = 5.
- **The unfolded result folded back.** It misses the data: χ² 254 at k = 5, 219 at k = 20.
- **Residual.** Median 10.7%, max 74.5% (EW29) at k = 5. It is identical against the unfolding half's own
  reweighted truth, so the MC split is not involved. The signal-only runs show the same (10.5%, 74.1%).
- **q3 departure.** Same pattern, except that its residual grows with iterations: median 3.4% → 5.9%,
  max 21.5% → 40.3% from k = 1 to 20.

**Noise-free (D4, asimov_same, B0, K = 30).** Both departures are highly visible at reco. At the
analysis exposure, the reco-level χ² between departed and nominal truth folds is:

- E_avail shape: 83,379 (EW projection), 92,364 (5D);
- q3: 26,863 (EW projection), 92,245 (5D).

| | k = 1 | k = 5 | k = 10 | k = 20 | k = 30 |
|---|---|---|---|---|---|
| E_avail: median / max \|EW residual\| | 14.3 / 69.5% | 10.9 / 73.5% | 9.6 / 69.7% | 9.1 / 64.3% | 8.1 / 60.0% |
| E_avail: explained fraction of the reco departure (EW) | 0.943 | 0.998 | 0.999 | 0.999 | 0.999 |
| E_avail: χ²(unfolded fold, truth fold), EW | 4,736 | 144 | 111 | 84 | 68 |
| q3: median / max | 3.3 / 21.2% | 5.0 / 37.8% | 5.8 / 40.2% | 6.3 / 41.3% | 6.6 / 41.5% |
| q3: explained fraction (EW) | 0.942 | 0.992 | 0.994 | 0.995 | 0.995 |

From k = 5 on, the estimator reproduces ≥ 99.2% of each departure's reco-level signal while
truth-level residuals remain (median 5–11%, maximum 38–74% over the 42 EW cells). The remaining reco-level imprint is small but not zero. At the analysis exposure it is still
detectable in the EW projection (χ² 68–144 over 42 cells). More iterations move the E_avail residual down
slowly (−26% between k = 5 and 30), and move the q3 residual up (+31%).

**One-factor probes (D5, noise-free).**

- **Capacity (400 trees, 31 leaves, all three estimators).** It improves the reco fit (E_avail fold χ² 103
  against 144 at k = 5) but not the E_avail truth residual: median 10.7% against 10.9% at k = 5, and
  10.3% against 9.2% at k = 15. It lowers the q3 median (3.5% against 5.0% at k = 5; 3.1% against 6.2% at
  k = 15) without lowering the q3 maximum (41.7% against 40.6% at k = 15).
- **Missed events kept at new_w = 1** (no regressor). No better:
  - E_avail median 9.1% against 8.1% at k = 30;
  - q3 5.6% against 6.6% (−15%), with a worse fold.

  In the traced runs, the regressor's fill differs from the mean reco-passing `new_w` of the same truth
  cell by 1.4% (median) and 5.4% (max), where the truth reweight is identical for both. Step 1's own
  truth-cell departure from the truth reweight is 13% (median) and 49% (max).

**Input geometry (D6(i), held-out R², 1M test rows).**

| target | from (pT, p‖, E_avail) | from all five truth axes |
|---|---:|---:|
| reco q3, from reco axes | 0.735 | — |
| reco W, from reco axes | 0.728 | — |
| truth q3, from truth axes | 0.877 | — |
| truth W, from truth axes | 0.866 | — |
| reco E_avail, from truth axes | 0.746 | 0.799 |
| reco W, from truth axes | 0.617 | 0.690 |

Reco E_avail correlates more strongly with truth q3 (Pearson 0.895) than with truth E_avail (0.867).
Reco W is exactly 0 for 1.1% of reco-passing MC rows and 1.2% of data events.

## 5. The nominal background-related bias (D7): a cause is named

Paired over 12 s5n seeds, each variant minus the signal-only experiment with the same signal draws:

| variant of the background-inclusive experiment | max \|t\| | functionals with \|t\| > 3.6 | max \|mean\| | total | J80 / J161 / EW40 |
|---|---:|---:|---:|---:|---|
| B0 (s5n family N) | 11.2 | 57 | 1.46% | +0.123% | +0.78 / +0.64 / +0.26% |
| **refinement classifier 400 trees, 31 leaves** | 4.0 | 1 (J58, +0.038%) | 0.15% | +0.008% | +0.03 / +0.01 / +0.05% |
| expectation template (source rows at expected weight) | 15.3 | 61 | 1.58% | +0.127% | +0.81 / +0.73 / +0.25% |

Against truth (the C3 pattern on 12 seeds), the results are:

| experiment | max \|t\| | functionals with \|t\| > 3.6 |
|---|---:|---:|
| B0 | 6.9 | 41 |
| refinement-capacity variant | 2.8 | 0 |
| signal-only | 3.0 | 0 |

**Named cause, by the contract's rule.** The Stay-Positive refinement classifier underfits at the F2
setting (100 trees, 8 leaves). Changing that one factor removes the background-related nominal bias. The
paired max \|t\| falls from 11.2 to 4.0, and the biased cells' mean shifts fall by more than 90%, in the
predicted direction.

**Excluded:** the source/template split of the background MC. The expectation template leaves the bias
unchanged.

The reco-level subtraction residual of B0 is up to ±4% per EW reco cell (the s5n review's 4.2%), and
it anti-correlates with the truth-level paired difference (Spearman −0.32). The refinement's reco-level
error is what propagates, through the unfold, to the truth-level excess.

## 6. Interpretation rules (predeclared, evaluated mechanically)

| rule | E_avail shape (the physical anchor) | q3 (declared stress amplitude) |
|---|---|---|
| under-converged (≥ 30% drop k = 5 → best k ≤ 30, fold improving) | **no** (−25.8%) | **no** (residual grows) |
| capacity-limited (≥ 30% drop at equal k) | **no** (k = 5: −1.5%; k = 15: +12%) | k = 5 **no** (−29.1%); k = 15 **yes** (−49%, median only) |
| missed-event-limited | **no** | **no** |
| observability-limited (at the best tested estimator: explained fraction ≥ 0.95, residual ≥ 50% of k = 5) | **yes**: best is B0 at k = 30, explained fraction 0.998 (5D), residual 74% of k = 5 | **yes, marginally**: best is the capacity probe at k = 1 (median 2.9%), explained fraction 0.956 (5D), residual 58% of k = 5 |

## 7. What is established, what is not

- **Named:** the refinement classifier's capacity, for the nominal background-related bias
  (`KNOWN_ISSUES.md` 75's residual; s5n C3).
- **Excluded at the measured resolution, for the departure failure:**
  - the background method (signal-only reproduces it);
  - the MC split (the residual is identical against the unfolding half's own truth);
  - the driver-versus-npz path (D1);
  - per-estimator seeds and dtype (bitwise inert);
  - the missed-event regressor (removing it does not help);
  - classifier capacity (for the physical E_avail departure);
  - iteration count within 30 (a 26% reduction for E_avail, and the wrong direction for q3).
- **Not named, INCONCLUSIVE for a single factor:** what makes the departure residual large. What is
  measured is that it lies in directions that leave a small reco-level imprint (from k = 5 on, ≥ 99.2% of each
  departure's reco signal is reproduced, and truth residuals of median 5–11%, maximum 38–74%, remain), along which iteration
  converges slowly or not at all. The input geometry is an **association**, not a tested mechanism:
  - reco q3 and W are only ≈ 73% determined by reco (pT, p‖, E_avail);
  - reco E_avail tracks truth q3 more closely than truth E_avail;
  - reco W is poorly determined by the truth axes.
- **`KNOWN_ISSUES.md` 79:** not a pipeline defect. The difference sits at the estimator's
  rounding-sensitivity floor (≈ 1% max, 0.2% median on data), itself a new, uncovered estimator property.
- **Withdrawn:** the confounded jitter probe (§3).

## 8. Consequences for candidates (the decision record follows the independent review)

- The only intervention that moves a decisive quantity by the rule's margin is the refinement-capacity
  repair, and it addresses the nominal background bias, not the departures.
- No authorized estimator change is supported for the physically anchored E_avail departure.
- Capacity is supported only for the q3 stress deformation, and only in its median.
- The departure residual is therefore an unfolding-model (regularization) dependence, to be reported
  separately from statistical uncertainty.
