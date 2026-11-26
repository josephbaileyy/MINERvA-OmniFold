# Test 1 of the Gemini Hydrogen-high read r1: a smooth E_vis weight

**A smooth weight in visible energy, fitted at reconstructed p∥ 20–40 GeV/c, does not reproduce the excess at ≥60 GeV/c. It overpredicts every higher band by 1.5–24×. A weight in E_avail alone leaves the ≥60 excess unchanged.** Section C of the read reproduces numerically, but its inference does not hold. At fixed E_vis, Data/fold depends strongly on p∥. The 20–40 turn-on is a rise with E_avail at fixed p∥. That rise appears in every band. Separately, the excess at ≥50 GeV/c is present at the lowest E_avail. Neither weight describes that second part.

Everything here is local and uses 0 node-hours. Inputs are the saved `../inputs/events/*.csv.gz` and `../inputs/replay/`. The per-event fold weight is `classify()` from `../score.py`, imported unchanged. Run `bash run.sh` to regenerate every `.txt` and `.json` here. Tested with the versions in `versions.txt`.

## 1. Section C numbers

Scripts: `sectionc.py` → `sectionc.txt`. All 12 playlists use merged-POT scaling, as in `../README.md`. Negative-sign tracks, and "good" means |σ(q/p)/(q/p)| < 0.30.

| Read's number | Recomputed | Status |
|---|---|---|
| Good negative, reco 20–40, Data/fold for E_vis < 40: 0.94–1.00 | 1.006 (20–30), 0.941 (30–40) | Reproduced |
| … E_vis 40–50 / 50–60 / 60–70 / 70–80: 1.15 / 2.53 / 3.81 / 7.17 | 1.151 / 2.530 / 3.805 / 7.173 | Reproduced |
| … Data/nomMC "1.15 → 3.16 → 4.45 → 8.11" | 1.157 (30–40), 1.518 (40–50), 3.158, 4.452, 8.105 | Reproduced, but the first value is the 30–40 bin. At 40–50 the value is 1.52 |
| … frac(true p∥ ≥ 60) = 0.000 | 0.00025 overall, ≤ 0.001 in every E_vis bin | Reproduced |
| Reco 40–50 / 50–55 / 55–60 Data/fold 0.968 (−495) / 1.250 (+694) / 1.533 (+740) | 0.968 (−495.3) / 1.250 (+694.1) / 1.533 (+739.9) | Reproduced |
| Reco 40–60, E_avail < 5: 0.943 (−872); ≥ 5: 1.436 (+1,810) | 0.943 (−870.8); 1.436 (+1,809.5) | Reproduced. −872 is off by one |
| Reco ≥ 60 good 2,306 vs 1,214.1; poor 604 vs 631.4 | 2,306 vs 1,214.1; 604 vs 631.4 | Reproduced (already in `../README.md`) |
| Reco ≥ 60, p_curv 55–58: 456 vs 0.0; 80–120: 250 vs 241.7; ≥ 120: 76 vs 74.7 | 456 vs 0; 250 vs 241.7; 76 vs 74.7 | Reproduced for **all precisions**. The read's sentence is about good tracks. Good tracks alone give 422 vs 0, 99 vs 87.4 and 15 vs 13.7 |

## 2. Test 1

Scripts: `test1.py` → `test1.txt`, `test1.json`; `summary.py` → `summary.txt`.

**Construction.** The fit uses good negative tracks at reco p∥ [20, 40) in the six training playlists (`1A 1C 1E 1G 1M 1O`), with each playlist's own data/MC POT. The fit variable is E_vis = reco p∥ + E_avail, in 2 GeV bins from 20 to 100. The model is fold × w(E_vis), with a binned Poisson likelihood. Three smooth forms of log w were fitted: quadratic, cubic and piecewise-linear with five interior knots. Beyond E_vis = 80, w is held at its value there, so the fit's slope is not extrapolated. Each fitted w multiplies every simulated track in the six held-out playlists (`1B 1D 1F 1L 1N 1P`): both signs, all precisions, signal and background. As a swap check, the piecewise-linear fit was also run the other way round. The same construction with w(E_avail) separates an E_vis dependence from a recoil-only dependence. Errors combine the fit parameters (linear propagation of the Hessian covariance), MC statistics and data Poisson statistics. Correlated systematics are not propagated, so the pulls are diagnostic.

**Held-out negative-sign yields, all precisions** (from `summary.txt`):

| Reco p∥ | Data | Fold | w(E_vis) quad | cubic | pw-linear | pw-linear, swapped* | w(E_avail) pw-linear |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20–40 | 64,059 | 63,849.5 | 64,163.5 | 64,156.9 | 64,170.3 | 74,271.3 vs 73,726 | 64,241.4 |
| 40–50 | 6,820 | 7,119.8 | 10,326.2 | 10,609.5 | 11,798.5 | 13,658.7 vs 7,935 | 7,032.2 |
| 50–60 | 2,617 | 1,939.2 | 5,198.2 | 5,193.0 | 6,379.5 | 6,909.8 vs 2,983 | 1,904.2 |
| 60–80 | 1,181 | 688.8 | 6,607.2 | 5,079.5 | 3,018.2 | 4,375.6 vs 1,314 | 674.6 |
| ≥80 | 192 | 162.9 | 4,675.7 | 2,766.3 | 1,400.9 | 896.4 vs 223 | 158.8 |
| ≥60 total | 1,373 | 851.7 | 11,282.9 | 7,845.8 | 4,419.1 | 5,272.0 vs 1,537 | 833.3 |

\*Fit on the held-out six and predict the training six. Data for that direction follow "vs".

- **The ≥60 excess is not reproduced.** Every w(E_vis) form closes 20–40 (held-out pull −0.3 in the training direction). It then overpredicts ≥60 by 3.2–8.2× against data, where the excess is +521 over the fold. At 40–50 it predicts a 45–66% excess where the data sit 4% below the fold. The piecewise-linear fit has the best training deviance (35.5/25), and its pulls at 40–50, 50–60, 60–80 and ≥80 are −23.5, −15.4, −5.5 and −2.5. The swap gives the same picture.
- **E_avail distributions.** At 40–50 and 50–60, the piecewise-linear w(E_vis) overpredicts every E_avail bin, including E_avail < 1 GeV: 2,455 vs 1,608 and 1,551 vs 667. The 40–60 recoil excess it was meant to explain becomes an overall overprediction (`test1.txt`).
- **Good/poor curvature ratio.** In data, the good/poor ratio rises well above the fold at 50–60 (18.1 vs 10.9) and 60–80 (6.43 vs 2.65). The training-direction w(E_vis) folds move it the wrong way, to 10.0–10.5 and 1.9–2.3. Poor-curvature yields are overpredicted 1.6–30× at ≥40, where the data match the nominal fold to within 17%.
- **Positive-sign rate.** The weight carries the simulated sign mixture along, so the w(E_vis) positive/negative ratio stays within 8% of the plain fold's. It does not discriminate. The absolute positive yields are overpredicted 2.1–23× at ≥50.
- **w(E_avail).** Every form leaves the band totals within 3.5% of the plain fold. The ≥60 excess remains: 1,373 vs 833.3 for the piecewise-linear form, with pulls +12.0, +13.4 and +2.1 at 50–60, 60–80 and ≥80. The swap gives +12.2, +12.8 and +2.4. This weight partly fixes the E_avail ≥ 10 bins at 40–50. At 50–60 a residual rise with E_avail remains (`test1.txt`).

**Why it fails** (`evis_by_pz.py` → `evis-by-pz.txt`, good negative tracks, all playlists). At fixed E_vis, Data/fold falls steeply with p∥. At E_vis 55–60 it is 3.35 at p∥ 20–40, 1.69 at 40–50 and 1.37 at 50–60. At E_vis 60–70 the values are 3.80, 2.35, 1.81 and 1.78 at 60–80. In every band the ratio rises along E_vis, which at fixed p∥ means rising E_avail. The held-out lowest E_avail bin (< 1 GeV) is a separate feature. There Data/fold is 0.85 at 40–50, 1.23 at 50–60 and 1.51 at 60–80, with 0.97 at ≥80 (`test1.txt`, fold columns). A rate change that depends only on neutrino energy, through the E_vis proxy, cannot produce both trends.

<!-- absence-ok: scopes this test's own construction (reco E_vis proxy); it claims no result elsewhere is missing -->
**Limits.** The tables carry no true neutrino energy, so E_vis stands in for a truth-level flux weight, as the read proposed. A truth-E_ν reweight could act differently through the E_vis resolution. That would need the AnaTuples and is not tested here. The weight is held constant beyond the fitted support, so the overprediction at ≥80 depends on that choice. The overprediction at 40–60 does not, because it lies inside the fitted E_vis range.

## 3. The read's corrections

Script: `corrections.py` → `corrections.txt`. It runs `../inputs/replay/replay.py` in-process with its assertions. `../ibu-chi2-20261123` is present on `main`, so the "absent dependency" in section A.1 refers to the read's copied workspace, not this repository.

**365.3 weight mismatch: reproduced.** The bound subtracts reco-weighted destinations (1,051.0) from a truth-weighted denominator (1,416.3). Using truth weights on both sides gives 352.0. Scaling the denominator by the selected reco/truth weight ratio (0.98750) to use reco weights on both sides gives 347.6. The read's decomposition reproduces: 262.8 unselected, 14.4 weight difference, 41.8 reconstructed below 40 and 46.3 outside acceptance. The MC statistical error on the denominator is ±17.9. The bound is overstated by 13–18 events, and the comparison against 2,003.2 missing is unaffected.

**Valencia flux +1,456: reproduced, and both numbers stand.** With in-domain reweighting, the raw selected MC at 40–60 changes from 13,283.2 to 14,739.1 (+1,455.9). The published-spectrum fold changes from 18,475.7 to 18,539.2 (+63.5). `../HANDOFF.md` quotes the second number correctly as a fold. The fold divides by the reweighted generated truth, so it is nearly flux-invariant. The raw-MC change bears on the headline comparison with Fig. 2. It closes 76.5% of the 1,902.0 gap to the fine-copy Tune v1 count of 15,185.2, and 446.1 (2.9%) remains. "Nearly the entire" overstates that, and the 11% difference between the two printed copies limits the comparison. The same swap also raises raw MC at 20–40 by 10,041.7 (8.9%), so on raw MC it is largely a normalization change. `flux.npz` holds no true ≥60 or background rows. The nominal true-≥60 feed (590.6 at 40–60) therefore stays unreweighted inside the background term in both versions, as the read noted.

## Files

`events.py` loads the tables and adds E_vis and p_curv. It caches to a git-ignored `.events-cache.pkl`, which `run.sh` deletes before and after the run. The other files are `sectionc.py`, `evis_by_pz.py`, `test1.py`, `summary.py`, `corrections.py`, `run.sh`, their outputs and `versions.txt`.
