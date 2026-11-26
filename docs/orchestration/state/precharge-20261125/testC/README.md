# Test C: true-Eν reweight against the declared readings

**C contradicts a smooth true-Eν rate change as the explanation. The reweight is fitted at reco p∥ 20–40 and anchored to the published cross section inside the grid. In both directions it overpredicts the held-out negative tracks at 50–60, 60–80 and ≥80 by 2.7–8.3 times the data − fold excess, and it leaves the positive excess untouched.** The held-out p is 2.4×10⁻⁴⁴ in the primary direction and 6.7×10⁻⁶⁷ in the swap, for the primary form. Nothing here is a cause determination, and no note sentence follows from it.

The choices, controls and readings were declared in `DECLARATION.md` before any job ran. The first version was committed in #1380 and bound by `TESTC-BINDING-1.md` (#1382). The four pre-score corrections and `test_c.py`/`controls.py` were merged in #1383 before any output was fetched. The scripts were run once afterward with no code change. `sacct_summary.py` was added after the run and only tabulates `inputs/sacct.psv`.

## Cluster run

- **Jobs.** 24 tasks on Perlmutter CPU, account m3246, QOS shared, job name `precharge_c`, writing only under `/pscratch/sd/j/josephrb/precharge-testC-20261126/`.
  - Pilot: 62041128 (reco 1L) and 62041129 (truth 1L).
  - Remainder: 62041281 (reco) and 62041282 (truth), array 0–6 and 8–11.
- **Outcome.** All 24 tasks are COMPLETED with exit code 0:0. The first start was 15:22:34Z and the last end 16:27:43Z.
- **Elapsed.** Reco took 2,129 s in total, longest 356 s (1F). Truth took 1,146 s, longest 148 s (1E).
- **Charge.** It is 0.0142 node-hours, computed from `sacct` elapsed times and 4 logical CPUs (2 physical cores) per task. The declared bound was 0.94. Every task's Start and End in UTC is in `sacct.txt`.
- **Binaries.** The build took place on 2026-11-26 at 15:19Z. `inputs/built.sha256`:
  - `measure` fd4912ce890781b021cb98bf441bc6c343e7824783893bdc8dd7bf5afada1fc1
  - `truth` bf7b7b9c6bcfe4b85ca47671c935915aa95f260b71c18045f89ea57e9985488d

  There were no compiler warnings. Every task re-checked the staged and built sha256 before it started (`inputs/slurm/`).
- **Fetch.** The 48 outputs were copied by `scp`. All 48 sha256 match the remote `sha256sum` (`inputs/fetched.sha256`). Committed here are the `true_enu` column (`inputs/enu/`), the truth tables (`inputs/truth/`), the program logs (`inputs/logs/`), the Slurm logs with their remote sha256 (`inputs/slurm/`, `inputs/slurm.sha256`), and the raw `TZ=UTC sacct -X` record (`inputs/sacct.psv`).

**Undeclared read.** `measure.cpp:28` and `truth.cpp:63` call `CVUniverse::SetNuEConstraint(true)`. That makes each task open cov2d's protected NuE constraint file, `MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`, with a plain read. Neither the declaration nor the binding listed that read. The director recorded it as a binding miss and reported it to cov2d on 2026-11-26. The task Start and End times above are given so that the file's access-time changes can be matched. Nothing was changed or rerun. The original precharge scan has the same call (`../measure.cpp:24`).

## Positive controls (`controls.py` → `controls.txt`, `controls.json`)

- **P1.** The first 12 columns of every rerun MC table are byte-identical to `../inputs/events/<pl>_MC.csv.gz`. This holds for all 12 playlists, 617,032 rows in total.
- **P2.** Both versions are reported, as declared:
  - **Deduplicated.** It agrees with each playlist's nominal generated histogram to at most 4.6×10⁻¹⁵ relative in every checked cell, in all 12 playlists.
  - **With duplicates.** It passes in 11 playlists and fails in 1E, at a maximum of 1.05×10⁻³ against the 10⁻³ tolerance. 1E has 133 duplicate keys, the same AnaTuple double-fill that the `ibu-chi2-20261123` event loop deduplicates. The deduplicated version is used.
- **P3.** No truth signal event has Eν < E_μ, out of 32.86 million. No fiducial ν_μ CC reco row has a nonpositive or nonfinite Eν.

## Result (`analyze.sh` → `test-c.txt`, `test-c.json`; closure in `closure.txt`)

**Setup.** The support is lo = 20 GeV and hi = 70 GeV. The 99th percentile of fold-weighted Eν in the training fit sample is 66.2 GeV, which the declared rule rounds up to 70. The deduplicated in-grid generated weight is 27,209,979.

| Primary form (pwlinear) | Primary | Swap |
|---|---|---|
| Training fit deviance / ndf | 232.3 / 26 | 274.8 / 28 |
| Held-out χ², C | 284.9 / 28, p = 2.4×10⁻⁴⁴ | 400.2 / 29, p = 6.7×10⁻⁶⁷ |
| Contributions T1 / T2 / T3 | 244.0 / 19.2 / 21.6 | 302.6 / 45.3 / 52.4 |
| Held-out χ², nominal fold | 960.0 / 28, p = 4×10⁻¹⁸⁴ | 980.3 / 29, p = 1×10⁻¹⁸⁷ |

**Reading.** H_C is contradicted. The primary form's held-out p is below 0.001 in both directions. The "supports" clause fails on p, although C improves on the nominal fold by far more than 9 in χ². The training deviance per degree of freedom exceeds 3 in both directions, so the anchored reweight does not describe even the 20–40 E_vis shape it is fitted to. The quadratic and cubic forms also fail with p < 0.001 in both directions. The quadratic does best, at 99.0/28 primary and 159.3/29 swap. No form changes the category.

**Share of the excess carried.** Held-out negative tracks, all precisions, primary direction:

| Reco p∥ | Data | Fold | C (pwlinear) | Share of data − fold | Test 1 w(E_vis) |
|---|---:|---:|---:|---:|---:|
| 40–50 | 6,820 | 7,119.8 | 7,371.2 ± 48.1 | −0.84 | 11,798.5 |
| 50–60 | 2,617 | 1,939.2 | 3,791.1 ± 147.4 | +2.73 | 6,379.5 |
| 60–80 | 1,181 | 688.8 | 2,514.0 ± 158.0 | +3.71 | 3,018.2 |
| ≥80 | 192 | 162.9 | 403.2 ± 22.1 | +8.27 | 1,400.9 |

- The swap shares are −0.53, +3.00, +4.51 and +6.97. The quadratic form's shares at 50–60, 60–80 and ≥80 are +1.35, +1.35 and +2.68 primary, and +1.43, +1.65 and +2.46 swap.
- C overshoots in the same direction as Test 1 but by less.
- The largest T1 terms are at 60–80 and 50–60 across all E_avail bins. At 60–80 and E_avail 2–5 GeV, for example, 361 tracks are observed against 892.5 predicted.
- **Positives.** C leaves them at the fold, because high-p∥ positive tracks are mostly outside the reweighted ν_μ CC classes. At 40–50 primary, 509 are observed against 413.6 predicted.

**Caveats that do not change the reading.**
- Above hi, w is held constant, and true ≥60 rows carry w without an anchor (declared limitation). The fitted pwlinear w rises to 13.8 at Eν ≥ 70 GeV. Its last knot coefficient is 20.4 ± 6.3, so the ≥60 prediction rests on a poorly constrained top knot. The quadratic's top value is 4.7, and it also overshoots.
- BFGS ended with "precision loss" in 5 of the 6 primary-form and sensitivity fits. The quadratic primary fit converged cleanly. The closure fits ended the same way at their exact minima, where the injected coefficients were recovered (`closure.txt`).
- Correlated flux, detector and anchor uncertainties are not propagated, as for A and B, so the p-values are diagnostic. <!-- absence-ok: restates the declared scope of this test's own variance model; it claims nothing elsewhere is missing -->

## What follows

- **A** contradicted a muon-independent recoil function.
- **B** was inconclusive for a constant curvature offset, carrying about a third of the 50–80 excess.
- **C** contradicts a smooth Eν rate change that is fitted at 20–40 and transferred upward. Fitted to the 20–40 E_vis shape, such a change predicts far more high-p∥ negative tracks than the data hold, and it does not move the positive excess at all.

The pattern is therefore not a smooth function of Eν alone that 20–40 can calibrate. That leaves effects that depend on muon momentum at fixed Eν, or that are confined to where 20–40 has no lever. Choosing among these is Joseph's decision, through the director.

`bash analyze.sh` regenerates `closure.txt`, `test-c.txt` and `versions.txt` from the committed inputs. `python3 sacct_summary.py > sacct.txt` regenerates the job table. `controls.py` ran once on the fetched outputs, whose sha256 are in `inputs/fetched.sha256`.
