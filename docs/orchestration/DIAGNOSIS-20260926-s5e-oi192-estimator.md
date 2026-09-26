# DIAGNOSIS 2026-09-26 — s5e (`OI-192`): why the 5D estimator misses physical departures, and where the nominal background bias comes from

**CITABLE FOR:** the diagnosis items D0–D7 of [`state/s5e/contract.json`](state/s5e/contract.json)
(amendments 1–2), measured on development seeds and on noise-free constructions. The record also states
which causes the contract's attribution rule lets it name.

- Numbers come from the receipt [`state/s5e/diag/diag_receipt.json`](state/s5e/diag/diag_receipt.json)
  (sha256 `f0880725…`), produced by `nd-unfolding/s5e_analyze_diag.py` at `700797e3` from the
  committed-table products under `/pscratch/sd/j/josephrb/s5e-20260925/runs/diag/`.
- They were independently reproduced from operands, and the record revised under that review:
  [`state/s5e/diag/review-round-1.md`](state/s5e/diag/review-round-1.md), findings F1–F7, all accepted.

**NOT CITABLE FOR:** a coverage verdict, a corrected central value, or a measured bias of the real
data. It changes no adopted product and no s5c/s5n grade. **Status:** development evidence,
independently reviewed.

## 1. What ran

| allocation | contents | CPU node-h (meter, closed) |
|---|---|---:|
| `58881080` | D3 traced pseudo-experiments (24, K = 20); D7 background pairing (40) | 1.587 |
| `58881083` | D5 probes; D4 noise-free scans (K = 30); D2 asimov and data probes; D1 driver runs; D6 geometry | 2.092 |
| `58886919` | amendment-2 repairs: edge-safe precision probe, sentinel mask probe, driver parity | 0.253 |
| **diagnosis total** | 87 products (83 traced, 4 driver-departure) and the geometry receipt | **3.932 of 10.0** |

Every traced unfold passed the tracer's per-iteration bitwise checks: its rebuilt `w_pull`/`w_push` equal
the weights the production loop passed to its next step. The traces therefore describe the unfolds that
ran.

## 2. D0 — the evidence reproduces

**28 of 28** traced iteration-5 unfolds equal their s5n development products bitwise, `xsec` and `xtrue`
alike. They are:

- 12 background-inclusive (nominal, E_avail shape, q3; four seeds each);
- 8 signal-only;
- the 8 D7 re-runs at seeds 300004–300011.

The traced real-data unfold equals the s5n `c7` npz product bitwise.

## 3. Pipeline differences (D1, D2 and the amendment-2 repairs)

**The departure failure is the same on the driver path: now measured, not inferred from code identity.**
The unmodified driver ran in `--closure` mode with the F2 configuration, with the deformation injected on
the pseudo-data weights. It reproduces the npz path's noise-free residuals:

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

**`KNOWN_ISSUES.md` 79 (driver versus npz on data, 1.29%): no pipeline factor is named.**

- **Per-estimator random states** (42/43/44 against 42/42/42): bitwise inert, on asimov and on data.
- **float64 upcast of the same values:** bitwise inert.
- **Edge-safe float32-ulp perturbation:** moves the data result by up to 1.23% and 0.98% (two seeds;
  median 0.18%/0.19%). The two seeds differ from each other by up to 1.42% (median 0.16%).
- **The driver–npz difference itself:** up to 1.29% (median 0.19%). The same size.
- **The driver's sentinel mask applied to the npz path:** moves individual functionals by more than the
  per-functional probe in 45 of 153 cases, but shrinks the driver–npz difference in only 12 of them. In
  aggregate the difference goes from 1.29%/0.19% (max/median) to 1.04%/0.28%.
- **On the noise-free E_avail departure:** the mask's moves are symmetric (34 functionals shrink, 32
  grow, each beyond the probe), which is noise.

The D2 rule therefore names the mask on neither path. The refinement differences on data are consistent
with the same input differences, and no separate refinement defect appears:

- refined sum 3,972,466.85 (driver) against 3,972,476.93 (npz);
- clipped rows 1,279 against 1,313.

**A new estimator property follows, and it matters beyond `KNOWN_ISSUES.md` 79.** The F2 estimator's
real-data output has a numerical reproducibility floor of about 1% (max) and 0.2% (median) under input
changes of float32-rounding size. That is comparable to the statistical σ (the median per-seed spread of
nominal closure is 0.21%). Whether a data bootstrap that refits everything per replica already absorbs it
is not established (candidate review round 2, M3).

**Withdrawn.** The original D2(b) jitter probe moved exact zeros on the grid edge 0 out of the grid:

- 293,292 MC truth E_avail values;
- 231,685 MC reco W values;
- 48,082 data reco W values;
- further, smaller zero sets in reco E_avail.

Its data result (up to 30%) is therefore not a rounding measurement. It stays in the receipt, labelled
as confounded.

## 4. The estimator's response to departures (D3–D6)

**Step 1 fits the reco data, and step 2 transfers it faithfully in truth cells; yet the unfolded result
does not reach a data-consistent solution.** On the four-seed background-inclusive E_avail departure (D3):

- **Step 1.** Its reco-level fold agrees with the measured side at noise level. The EW-projection χ²
  between measured side and step-1 fold is 84, against 119 between the measured side and the folded
  truth model.
- **Step 2.** It reproduces step 1's truth-cell weight sums to 0.11% (median) and 0.49% (max) at k = 5.
- **The unfolded result folded back.** It fits the data significantly worse than the truth model does:
  χ² 254 against 119 at k = 5, and 219 at k = 20. Signal-only gives 160 against 53 at k = 5, and 125 at
  k = 20.
- **Residual.** Median 10.7%, max 74.5% (EW29) at k = 5. It is identical against the unfolding half's own
  reweighted truth, so the MC split is not involved. The signal-only runs show the same (10.5%, 74.1%).
- **q3 departure.** Same pattern, except that its residual grows with iterations: median 3.4% → 5.9%,
  max 21.5% → 40.3% from k = 1 to 20.

**Noise-free (D4, asimov_same, B0, K = 30).** Both departures are highly visible at reco. At the
analysis exposure, the reco-level χ² between departed and nominal truth folds (S_dep) is:

- E_avail shape: 83,379 (EW projection), 92,364 (5D);
- q3: 26,863 (EW projection), 92,245 (5D).

| | k = 1 | k = 5 | k = 10 | k = 20 | k = 30 |
|---|---|---|---|---|---|
| E_avail: median / max \|EW residual\| | 14.3 / 69.5% | 10.9 / 73.5% | 9.6 / 69.7% | 9.1 / 64.3% | 8.1 / 60.0% |
| E_avail: explained fraction of the reco departure (EW) | 0.943 | 0.998 | 0.999 | 0.999 | 0.999 |
| E_avail: χ²(unfolded fold, truth fold), EW / 5D | 4,736 / 5,553 | 144 / 368 | 111 / 284 | 84 / 206 | 68 / 164 |
| q3: median / max | 3.3 / 21.2% | 5.0 / 37.8% | 5.8 / 40.2% | 6.3 / 41.3% | 6.6 / 41.5% |
| q3: explained fraction, EW (5D) | 0.942 (0.940) | 0.992 (0.986) | 0.994 (0.989) | 0.995 (0.989) | 0.995 (0.989) |

Read together:

- From k = 5 on, the unfolded result reproduces ≥ 99.2% (EW; ≥ 98.6% in 5D) of each departure's
  reco-level signal, while truth-level residuals remain (median 5–11%, maximum 38–74% over the 42 EW
  cells).
- The remaining imprint is small relative to the departure's own signal, but **not small statistically**.
  On a noise-free construction χ²(unfolded fold, truth fold) is the noncentrality a data fit would see.
  For E_avail it is λ_EW = 144 → 68 (roughly 12σ → 8σ) and λ_5D = 368 → 164 between k = 5 and 30.
- Convergence is **slow and incomplete** within 30 iterations. The E_avail median falls 26% (max 18%) and
  is still falling at k = 30 (≈ 0.1 pp per iteration), while the q3 residual grows by 31%.

**One-factor probes (D5, noise-free).**

- **Capacity (400 trees, 31 leaves, all three estimators).** It improves the reco fit (E_avail fold χ²
  103 against 144 at k = 5; 63 against 95 at k = 15) without improving the E_avail truth residual: median
  10.7% against 10.9% at k = 5, and 10.3% against 9.2% at k = 15. Better fit with no better truth is
  direct evidence that part of the residual is weakly constrained. It lowers the q3 median (3.5% against
  5.0% at k = 5; 3.1% against 6.2% at k = 15) without lowering the q3 maximum (41.7% against 40.6% at
  k = 15).
- **Missed events kept at new_w = 1** (no regressor). Worse for E_avail (median 9.1% against 8.1% at
  k = 30). For q3, a measured partial improvement of 13–15% in the median at k = 5, 15 and 30 (max 41.5%
  → 36.5% at k = 30), with a worse fold (χ² 172 against 132 at k = 30).
  - In the traced runs at k = 1, the regressor's fill differs from the mean reco-passing `new_w` of the
    same truth cell by 1.4% (median) and 5.4% (max) for E_avail signal-only, 1.4%/5.8% background-inclusive,
    and 4.8%/9.2% for q3. At k = 5 the E_avail gap is 0.09%/0.45%.
  - Step 1's own truth-cell departure from the truth reweight is 13% (median) and 49% (max) at k = 1.

**Input geometry (D6(i), held-out R², ≈ 1M test rows).**

| target | from (pT, p‖, E_avail) | from all five truth axes |
|---|---:|---:|
| reco q3, from reco axes | 0.735 | — |
| reco W, from reco axes | 0.728 | — |
| truth q3, from truth axes | 0.877 | — |
| truth W, from truth axes | 0.866 | — |
| reco E_avail, from truth axes | 0.746 | 0.799 |
| reco W, from truth axes | 0.617 | 0.690 |

Reco E_avail correlates more strongly with truth q3 (Pearson 0.895) than with truth E_avail (0.867).
Reco W is exactly 0 for 1.14% of reco-passing MC rows and 1.18% of data events.

## 5. The nominal background-related bias (D7): a cause is named

Paired over 12 s5n seeds, each variant minus the signal-only experiment with the same signal draws:

| variant of the background-inclusive experiment | max \|t\| | functionals with \|t\| > 3.6 | max \|mean\| | total | J80 / J161 / EW40 |
|---|---:|---:|---:|---:|---|
| B0 (s5n family N) | 11.2 | 57 | 1.46% | +0.123% | +0.78 / +0.64 / +0.26% |
| **refinement classifier 400 trees, 31 leaves** | 4.05 | 1 (J58, +0.038 ± 0.009%) | 0.15% | +0.008% | +0.03 / +0.01 / +0.05% |
| expectation template (source rows at expected weight) | 15.3 | 61 | 1.58% | +0.127% | +0.81 / +0.73 / +0.25% |

Direct comparison, refinement-capacity variant minus B0 (paired): max \|t\| 12.5, with 61 functionals
beyond 3.6.

Against truth (the C3 pattern on 12 seeds):

| experiment | max \|t\| | functionals with \|t\| > 3.6 |
|---|---:|---:|
| B0 | 6.9 | 41 |
| refinement-capacity variant | 2.8 | 0 |
| signal-only | 3.0 | 0 |

Over B0's 12 worst cells the mean shift falls by a median of 93% (minimum 82%). The variance cost is
modest: the per-seed closure spread of the variant is 1.12× B0's in the median over all functionals, and
1.055× over the EW cells. The reco-level subtraction residual falls from 4.13% (max) and 0.52% (median)
per EW reco cell to 1.68% and 0.07%. The variant's products differ from B0's only in the refinement
override.

**Named cause, by the contract's rule.** The Stay-Positive refinement classifier underfits at the F2
setting (100 trees, 8 leaves). Raising its capacity alone reduces the background-related nominal bias by
more than 80% in every one of the worst cells, and makes the 12-seed closure pass the C3 pattern. One
functional (J58, +0.04%) remains beyond t = 3.6 in the paired comparison.

**Excluded:** the source/template split of the background MC. The expectation template leaves the bias
unchanged.

The relation between the reco-level residual map and the truth-level excess is weak (Spearman −0.32 in
the EW projection), so the propagation path is not demonstrated beyond the intervention itself.

## 6. Interpretation rules (predeclared screens, evaluated mechanically)

| rule | E_avail shape (the physical anchor) | q3 (declared stress amplitude) |
|---|---|---|
| under-converged (≥ 30% drop k = 5 → best k ≤ 30, fold improving) | **no**, by the K_max = 30 cap: −25.8% and still falling (≈ 0.1 pp per iteration) | **no**: the residual grows; stopping earlier lowers it (−34% at k = 1) with a far worse fold |
| capacity-limited (≥ 30% drop at equal k) | **no** (k = 5: −1.5%; k = 15: +12%) | k = 5 **no** (−29.1%); k = 15 **yes** (−49%, median only) |
| missed-event-limited | **no** (worse) | **no** (−13 to −15%, below the screen, with a worse fold) |
| observability-limited (at the best tested estimator: explained fraction ≥ 0.95 and residual ≥ 50% of k = 5) | **fires**: B0 at k = 30, 0.998 (5D), 74% | **fires**: capacity at k = 1, 0.956 (5D), 58%; also at capacity k = 15, 0.998, 63% |

The screen's name overstates what it measures. It fires on a small *relative* imprint, while the
absolute imprint is statistically strong (§4). It therefore does not establish observability as the sole
cause.

## 7. What is established, what is not

- **Named, by intervention:** the refinement classifier's capacity, for the nominal background-related
  bias (`KNOWN_ISSUES.md` 75's residual; s5n C3).
- **Excluded (the intervention moved nothing beyond noise), for the departure failure:**
  - the background method (signal-only reproduces it);
  - the MC split (the residual is identical against the unfolding half's own truth);
  - the driver-versus-npz path (D1);
  - per-estimator seeds and float64 handling (bitwise inert).
- **Measured partial effects, below the predeclared 30% screen, for the departure failure:**
  - iteration count for E_avail (−26% median, −18% max from k = 5 to 30, still falling);
  - early stopping for q3 (−34% at k = 1, with a far worse fold);
  - the missed-event treatment for q3 (−13 to −15% without the regressor; for E_avail it is worse);
  - classifier capacity for the q3 median (−49% at k = 15, the maximum unchanged; for E_avail none).
- **Not named, INCONCLUSIVE for a single factor:** what makes the departure residual large. What is
  measured:
  - It lies in directions whose reco-level imprint is ≤ 0.8% (EW) of each departure's own signal, yet
    detectable at the analysis exposure (λ_EW 68–144 for E_avail).
  - The estimator converges along them slowly (E_avail) or away from them (q3).
  - Improving the reco fit by capacity does not improve the E_avail truth residual.
  - The input geometry is an association, not a tested mechanism: reco q3 and W are ≈ 73% determined by
    reco (pT, p‖, E_avail); reco E_avail tracks truth q3 more closely than truth E_avail; reco W is poorly
    determined by the truth axes.
- **`KNOWN_ISSUES.md` 79:** not a pipeline defect. The difference sits at the estimator's
  rounding-sensitivity floor (≈ 1% max, 0.2% median on data), itself a new, uncovered estimator property.
- **Withdrawn:** the confounded jitter probe (§3).

## 8. Consequences for candidates (decided in contract amendment 3)

- The only intervention that moves a decisive quantity by the rule's margin, with a named cause, is the
  refinement-capacity repair. It addresses the nominal background bias, not the departures.
- For the physically anchored E_avail departure, no authorized estimator change passes its predeclared
  screen within the tested ranges:
  - iterations give a continuing partial effect whose extrapolation, even to ~50 iterations, leaves
    residuals of several percent in the median and tens of percent at high W, against a statistical σ of
    ≈ 0.2%, while worsening q3;
  - capacity does not help.
- The departure residual of this estimator is therefore measured and reported as an estimator-dependent
  model dependence, separately from statistical uncertainty. A dedicated convergence study (many more
  iterations on the noise-free construction) is a separately costed next step, not a candidate here.
