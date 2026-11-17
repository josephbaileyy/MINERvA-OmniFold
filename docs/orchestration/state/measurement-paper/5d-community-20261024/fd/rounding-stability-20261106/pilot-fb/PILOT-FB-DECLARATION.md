# PILOT-FB DECLARATION: fixed bin edges against the rounding instability, on RS1's pseudo-experiment (2026-11-17)

**For** audit by `coverage-5b-audit` and the director's go. **Nothing has run, and nothing runs before the go.** DESIGN
ONLY: the code plan (§8) is written after this is audited.

**Written by** session tier3-design, at the director's brief of 2026-11-17. All repository citations are at
`origin/main` `c87508d1` unless stated.

**Authority.**
- Joseph's instruction of 2026-11-11, as the director relays it: new analyses that are not too costly. A grep of
  `docs/orchestration/DECISION-2026111*.md` for "costly" finds no record of it. The director is asked to name the
  record (§10).
  Search: grep -il costly docs/orchestration/DECISION-2026111*.md @ c87508d1
- Compute: `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` item 2. Each campaign is declared,
  priced and bound. This one is capped at 0.9 CPU node-h (§7), under the director's "under 1 node-h".

**CITABLE FOR:** the design, readings, price and code plan of the pilot, as declared.

**NOT CITABLE FOR:**
- any result. Only PILOT-FB's outcome record can state one;
- any statement about the real data;
- any change to the reported estimator, to `OUTCOME-20261105-fd-stab-none-pass.md`, to RS1's or ENS1's records, or to
  any note or paper wording. **No outcome changes any wording.** The outcome goes to Joseph and Ben, through the
  director, as an option.

## 1. The question

RS1 found (`OUTCOME-20261108-rs1-rounding-mechanism.md`, K1 SUPPORTED) that on this pseudo-experiment, "the
perturbation reaches the estimator by breaking ties among equal float32 values, which changes LightGBM's histogram
bins; a perturbation that keeps the ties removes the spread". Its tie-preserving jitter V left a spread ratio of about
10⁻⁶.

V is a diagnostic, not a remedy: it changes the perturbation, not the estimator. **The remedy tested here changes the
estimator so that no rounding-scale perturbation can change its bins.** Every LightGBM model is given bin edges
computed once from the unperturbed inputs.

**Two questions:**
1. **Does the rounding spread vanish** under fixed edges, against the same jitters that give configuration (e) its
   spread?
2. **How much does the result depend on which fixed edges are used?** That dependence would be the remedy's honest
   systematic, the price of removing the instability.

**What it cannot answer:**
- whether the remedy keeps (e)'s bias at the F0b truths, or its coverage. A remedy that changes the estimator needs both
  before it could be adopted (`FD-STAB-DECLARATION.md:33-34`). They are later steps, each declared separately;
- anything about the real data.

## 2. What the code implies (readings of source, each tested in §5 or §8)

1. **Four LightGBM models see the coordinates** (RS1 §2 item 3):
   - OmniFold's step-1 classifier, on reco coordinates: MC reco and measured rows (`omnifold_nn_core.py:251`);
   - its regressor, on truth coordinates: fit on the reco-passing MC truth rows and predicting the reco-failing ones
     (`:259-260`);
   - its step-2 classifier, on truth coordinates (`:263`);
   - the Stay-Positive refinement classifier, on reco coordinates: observed and template rows (`s5n_pseudo.py:226`;
     parameters from `refine_params`, `:234-236`).
2. **In histogram mode, a model sees a coordinate only through its bin**, and the bins are built from the training
   sample's distinct values and their counts (RS1 §2 item 4, LightGBM v4.6.0 `src/io/bin.cpp`, sha256 `3386767e…`).
3. **LightGBM's forced bins do not fix the bins by themselves.** `FindBinWithPredefinedBin` (`bin.cpp:157-235`):
   - it first places the zero bounds ±`kZeroThreshold` (only for the signs present) and +∞;
   - it then inserts the forced bounds in file order, up to `max_bin` minus those, and silently drops the rest
     (`:199-211`);
   - **it fills every remaining bin greedily from the data** (`:213-232`), which is the data-dependent step RS1 found.

   So the edges must number exactly `max_bin` − 1 − z per feature, where z is the number of zero bounds placed. Then no
   free bin is left and the data choose nothing. G3 (§5.1) measures this on every fit.
4. **The protocol's jitter** moves each value by u · spacing(|x|) in float32, with u uniform in [−½, ½)
   (`s5e_trace.py:362-364`). Values on an analysis-grid edge are not moved (`:365-367`). At a power of two, the spacing
   below is half the spacing above, so a value can reach the adjacent lower float32 value (RS1 §4, "Why ulp↓").
5. **So an edge is admissible only if no jitter can cross it.** Between adjacent distinct pooled values a < b, the
   interval (a + ½ spacing(a), b − ½ spacing(b)) must be non-empty. The edge is that interval's midpoint, in float64.
   An edge in an admissible gap keeps every row in its bin under any jitter of this protocol. Then every fit sees the
   same binned inputs, labels and weights. Predictions on untrained rows (the regressor's) compare raw values with the
   same fixed thresholds, so they cannot cross either.

## 3. The remedy and its edge sets

**Pools.** Edges are computed once, inside the job, from the unjittered float32 values of the built pseudo-experiment:
- **reco pool:** every row of MC reco, measured, observed and template, per axis;
- **truth pool:** every MC truth row, per axis.

Each model gets the pool of its space, for its five features in their order (§2 item 1). The edges are written to one
JSON before any fit, with their sha256 recorded, and every task checks that sha.

| set | max_bin | edges per feature | placement |
|---|---|---|---|
| **E1** (primary) | 255 | 255 − 1 − z | at the admissible gap nearest each equal-count quantile i/(n+1) of the pool's rows, i = 1…n |
| **E2** | 255 | the same | at quantiles (i + ½)/(n+1): E1 offset by half a step |
| **E3** | 127 | 127 − 1 − z | equal-count, as E1, with half as many bins |

- **Distinct edges:** if two quantiles map to one gap, the later takes the next admissible gap above. If a feature has
  fewer admissible gaps than it needs edges, the job refuses (G0).
- **Why forced bins, and not a pre-quantization of the inputs.** Rounding each coordinate to a coarse grid keeps most
  ties, but a row within ½ ulp of a grid midpoint still changes its quantized value under the jitter. RS1's readouts
  show that a few rows changing bin can move a functional by a statistical σ. Admissible forced edges leave no such
  row. The director may substitute a quantization arm (§10).

## 4. The arms and their inputs

**The input is RS1's pseudo-experiment, unchanged** (RS1 §4):
- FD-STAB's GiBUU-like stability truth, pseudo-seed 990000;
- configuration (e), estimator R, with 5 iterations and 32 threads per lane;
- inputs `of_inputs_5d.npz` (sha256 `07fccc1a…`) and `bkg_dump.npz` (`2addac8f…`), through the production loaders;
- the protocol's jitter seeds 1–20 (RS1 §4).

| arm | what runs | products | unfolds |
|---|---|---|---:|
| **A0** (baseline, reused) | nothing: RS1's A0, float32 base and jitters 1–20, pinned in RS1's `receipts/full-a1/read/runs-SHA256SUMS` (`runs/A0/rs1_A0_b-_j-.npz` `fd9f4b35…`, `…_j1.npz` `80c2a710…`, …) | read by O_NOATIME copy | 0 |
| **A0R** (G1) | RS1's A0 float32 base, rerun unchanged at this deploy | base | 1 |
| **E1** | the remedy with E1 | float32 base; jitters 1–20 | 21 |
| **E2**, **E3** | the remedy with E2 or E3 | float32 base each | 2 |
| **total** | | | **24** |

E2 and E3 are run at their bases only. The edge-set dependence (question 2) is a property of the bases. Their own
removal of the spread is not measured, only E1's (§9).
<!-- absence-ok: scope of this design; it states which arms the pilot runs, not that a result does not exist -->


## 5. The statistics and the readings

**Functionals:** the 153 s5e reported functionals (`s5c_coverage.reported_functionals`), RS1's and FD-STAB's set.
**σ:** FD-STAB's committed pseudo-data σ, `state/s5e/cand/assess_receipt.json` `sigma_rel_pct` (sha256 `84266e30…`,
`FD-STAB-DECLARATION.md:146-156`). The 16 cells R00–R15 are a readout (§6).

**S1, the removal ratio** (RS1 §5, unchanged):
- s_{a,j} is the SD, with ddof = 1, of F_{a,j,s} / mean_s F_{a,j} − 1 over seeds 1–20.
- M_E1 = median_j s_{E1,j} / s_{A0,j}, with A0 from the reused products.
- Its 90 % interval: 2,000 paired bootstrap resamples of the seeds, E1 with A0, at bootstrap seed 20261117.
- The bands are RS1's: R ≤ 0.10 < P < 0.70 ≤ C. A reading is DEFINITE only when the interval lies inside one band.
- Power is RS1's: at 20 paired seeds a true M = 0 reads R DEFINITE in every trial (`RS1-DECLARATION.md:230-238`).
- Excluded functionals (s_{A0,j} = 0) are RS1's G2 count, 0 of 153.

**S2, the stability statistic, like for like with RS1's A0 readout** (`FD-STAB-DECLARATION.md:158-165`):
- r_j = F_j / F_{E1 base} − 1.
- On each of the 10 disjoint pairs (1, 2) … (19, 20), per functional, take the larger |r_j| / σ_j of the two jitters.
- Take the median and maximum over the 153, then the mean over the pairs, with the standard error.
- RS1's A0 read 0.760 and 6.78 on this statistic (`rs1_read.json` `readouts.A0_pair_statistic_10_pairs`).

**S3, the edge-set dependence:**
- d_j = max over the pairs (E1, E2), (E1, E3), (E2, E3) of |F_a,j / F_b,j − 1| / σ_j, over the three float32 bases.
- Then the median and maximum over the 153.
- **Not like for like with S2:** three bases and a maximum over three pairs, against jitter pairs. It is read only
  against the bars.

**The bars** are s5e's A3 bars: median ≤ 0.3 and maximum ≤ 1.0 (`FD-STAB-DECLARATION.md:33-34`).

### 5.1 Gates, before any reading

- **G0, the edges.** Every edge is admissible (§2 item 5), recomputed from the pools. Each feature has exactly
  `max_bin` − 1 − z distinct edges. Otherwise the job refuses before any fit.
- **G1, reproduction.** A0R's `xsec_flat` equals RS1's pinned `rs1_A0_b-_j-.npz` bitwise. It is compared as arrays,
  since the metadata carries timings, with the same 32 threads and 8 lanes. **If G1 fails, nothing is read:** the run is
  NOT REPRODUCED and goes to the director.
- **G2, the bins hold.** For E1 jitters 1–4 and every pool array and axis, each row's forced-bin index equals the
  unjittered row's. The count of changed rows must be 0. If it is not, the remedy's premise failed: S1–S3 are not read,
  and the run goes to the director.
- **G3, no free bins.** For every LightGBM fit in round 1 (§7), a Dataset built with the fit's parameters on the fit's
  matrix reports `feature_num_bin` = the forced count + z + 1 for every feature. If any fit does not, nothing is read.
- **G4, the inputs.** Every reused A0 product and the σ receipt equal their pins.

G0–G3 are checked inside the job after round 1. Rounds 2–3 run only if all pass, so a failure costs at most a third of
the run (§7).

### 5.2 The readings, fixed before anything runs

| reading | when |
|---|---|
| **REMOVED** | M_E1 reads R, DEFINITE |
| **REDUCED** | M_E1 reads P, DEFINITE |
| **NOT REMOVED** | M_E1 reads C, DEFINITE |
| INCONCLUSIVE | otherwise |
| **STAB_PASS / STAB_FAIL** | S2's mean median ≤ 0.3 and mean maximum ≤ 1.0, or not |
| **EDGE-STABLE / EDGE-SENSITIVE** | S3's median ≤ 0.3 and maximum ≤ 1.0, or not |

**What the outcome record may say,** as an option for Joseph and Ben:

| outcome | the option statement |
|---|---|
| REMOVED, STAB_PASS, EDGE-STABLE | "On this pseudo-experiment, fixing every LightGBM model's bin edges once, from the unperturbed inputs, removes the rounding spread. Across three edge sets the result moves by at most S3's maximum, in pseudo-data σ, which is within the stability bars." |
| REMOVED or REDUCED, STAB_PASS, EDGE-SENSITIVE | "Fixed edges remove (or reduce) the rounding spread but trade it for an edge-choice dependence of S3's median and maximum, in pseudo-data σ, beyond the bars." |
| NOT REMOVED, or STAB_FAIL | "Fixed edges, as declared, are not a remedy on this pseudo-experiment." |
| INCONCLUSIVE | no option statement; the numbers are reported. |

- **Every option statement** carries the limits of §9 and the next steps it would need: bias at the F0b truths,
  coverage, and a data run, each declared separately.
- **It may not say** that the remedy works on the data, that it keeps (e)'s bias, or that it should replace (e).

### 5.3 Predictions, stated before anything runs

These are this lane's expectations from §2, not criteria:
- REMOVED, with M_E1 near 0. Most or all of E1's jitters should equal E1's float32 base bitwise in `xsec_flat`.
  Admissible forced edges should close even the regressor channel that left V's 10⁻⁶ residual (RS1 §5.3).
- STAB_PASS.
- S3: no expectation.

## 6. Readouts, with no criterion

- **The remedy's shift from (e):** each E-set base against A0's float32 base, as the median and maximum over the 153 of
  |F_E / F_A0 − 1| / σ. On one pseudo-experiment this is a shift, not a bias. Bias needs the truths (§1).
- **E1's jitters bitwise equal to its base:** how many of the 20.
- **The 16 cells:** M_E1 and S3 on R00–R15, by S1's integration rule (RS1 §5).
- **G2's count, per axis and pool**, and the admissible-gap shares per feature.
- **The time per unfold** of each arm, against the unit.

## 7. Compute

**Unit:** FD-STAB's, 657 s per unfold on one of 8 lanes, which is 0.022828 CPU node-h (`RS1-DECLARATION.md:356-358`),
+10 % for the gate checks.

| | unfolds | rounds of 8 lanes | wall at unit +10 % | node-h |
|---|---:|---:|---:|---:|
| round 1: A0R; E1, E2, E3 bases; E1 jitters 1–4 | 8 | 1 | 723 s | 0.201 |
| rounds 2–3: E1 jitters 5–20 | 16 | 2 | 1,446 s | 0.402 |
| **expected** | **24** | **3** | **2,168 s** | **0.602** |

FD-STAB measured about 408 s per unfold (RS1 §7), which would give about 0.37 node-h.

**Cap: 0.9 CPU node-h.**
- One exclusive node, `--time=0:50:00` (H:MM:SS, 3,000 s = 0.833 node-h), `--no-requeue`, QOS regular, CPU only. The
  charge cannot exceed `--time`.
- No dry run: G0–G3 gate rounds 2–3 inside the job.
- The charge is read from `sacct` after the job ends.
- No resume without the director. A stopped run is INCOMPLETE and not read.
- 0.9 is far below half the group balance. The cluster lane reads `iris` before the connect.

**Reads, and the fences.**
- The job reads `of_inputs_5d.npz` and `bkg_dump.npz` plainly through the production loaders, as RS1 and FD-STAB did.
  Those two files are on other lanes' atime lists: E96D's runs atime-check them
  (`fd/referee-sensitivity-20261111/connect-post/README.md:21`), and RDX's declaration never reads them.
- **So before the go, the director confirms that no live atime watch names them.** The connect stats both and refuses
  on a moved size or mtime.
- RS1's A0 products and the σ receipt are read by O_NOATIME copy, checked against their pins.
- **The job family is `pfb_`.** Before any connect, cov2d and every fenced lane are told of it and acked. The connect's
  fence refuses if any `cov2d`, `t2a`, `ll5d`, `e96data`, `rpd_`, `rsn_`, `rdx_` or `pfb_` job is queued or running.
- Status is read with `sacct` over the job id, never `squeue` alone.
- Products go to `/pscratch/sd/j/josephrb/pfb-20261117/`. Nothing is written to CFS from the job.
- Every connect script's sha256 goes to the director before it runs.
- Receipts are committed as PRs.

## 8. Code plan (written after this declaration is audited)

**No bound module is edited.** One new wrapper, `nd-unfolding/fb_pilot_probe.py`, runs every arm through RS1's
`rounding_mechanism_probe.py run --arm A0` path, with one rebinding per FB arm:
- `omnifold_nn_core.make_estimators`: clf1 gets the reco edges, clf2 and the regressor get the truth edges, each as
  `forcedbins_filename` with the set's `max_bin`;
- `s5n_pseudo.refine_params`: the refinement gets the reco edges and `max_bin`.

`s5c_unfold.unfold` already checks that every built estimator carries the composed parameters (`s5c_unfold.py:119-134`).
There is one new job script, `sbatch_pfb.sh`, on RS1's pattern (deploy pin, log refusal, environment check,
`SHA256SUMS`, DONE receipt), with the round-1 gate. There is one analysis, `fb_pilot_analyze.py`.

**Tests, local, with LightGBM 4.6.0 on toy data**, each in the direction it acts and in the other:
- **admissibility:** the protocol's jitter, at u = −½ and at a power of two, never moves a row across an admissible
  edge. A gap that touches a power of two is refused;
- **the edge count:** with exactly `max_bin` − 1 − z edges, `feature_num_bin` has no free bin. With one fewer,
  LightGBM fills one greedily, and the test sees it;
- **the remedy:** a toy fit with E1-style edges gives bitwise identical predictions, on training and untrained rows,
  under the protocol's jitter. Without forced bins, the same toy and jitter differ;
- **the readings:** every band boundary, the bars, INCONCLUSIVE, and the G0–G4 refusals;
- **a mutation harness:** one planted defect per guard and per reading, each killed by a named test.

## 9. Limits and disclosures

- **One pseudo-experiment and 20 jitters.** The intervals cover the jitters, not the realization.
- **The remedy's removal is measured for E1 only.** E2 and E3 are bases.
- **Three edge sets are a sample of the choices, not a bound** on the edge dependence.
- **Admissibility is against this protocol's jitter only.** A real rounding difference larger than ½ spacing, such as
  driver against npz (`KNOWN_ISSUES.md` 79), could still cross an edge.
- **On data, the edges would come from the data's own unperturbed inputs.** Whether that is stable from one data
  version to the next is not tested here.
- **The remedy changes the estimator.** Bias, coverage and the data result are untested here (§1).
<!-- absence-ok: limits of this design's scope; they name what the pilot does not measure, not missing results elsewhere -->


## 10. Open items for the audit and the director

1. **The record of Joseph's 11-11 instruction**, for the authority line.
2. **The live atime watches** on `of_inputs_5d.npz` and `bkg_dump.npz` (§7).
3. **The arms.** Forced bins with E1–E3, as declared, or a pre-quantization grid in place of E3. Jitters for E2 and
   E3 would add 40 unfolds (5 more rounds, about +1.0 node-h, about 1.6 in all), beyond the cap.
4. **The bands and bars** are RS1's and s5e's, unchanged. The audit may tighten them.
