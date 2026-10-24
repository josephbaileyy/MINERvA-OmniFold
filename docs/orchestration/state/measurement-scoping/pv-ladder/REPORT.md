# The prior-variation dimension ladder: report (2026-10-24, session "2d test")

The real data were unfolded with the Tune v1 prior reweighted by each generator's shape relative to GENIE CV, for
GENIE+MEC, NuWro and GiBUU. This is PV-2D's test, unchanged (`../../2d-closeout/stageF/methods/pv2d/`), run on more
observables:
- **L-EW:** a direct 2D (E_avail, W) unfolding;
- **L-3D:** (p_T, p_∥, E_avail);
- **L-4D:** adds q₃;
- **L-5D-PV:** the 5D unfolding under the same three vertices.

L-2D, PV-2D's (p_T, p_∥), and s5p's 5D record are reused. The run is under [`DECLARATION.md`](DECLARATION.md), as
amended by PR #313 and bound in [`BINDING.md`](BINDING.md). The run record is [`RUN.md`](RUN.md).

**Answer to Ben's two questions:**
- **"Are E_avail and W especially bad, or is it the 5D correlations?"** It is the variables. The direct (E_avail, W)
  unfolding is at least as prior-dependent as the 5D one projected onto the same 39 cells.
  - Raw, its envelope is larger, median per-cell ratio 1.63. Normalized by the strength of each rung's prior
    departure, the two are equal, median ratio 1.02.
  - On these cells nearly the whole truth-level departure of the prior reaches the result in both (h/D 0.92 and
    0.97). On the (p_T, p_∥) cells about 30 % does (h/D 0.29).
- **"What is the maximal phase space we can probe and understand?"** The (p_T, p_∥) observable's prior dependence
  barely changes as E_avail, q₃ and W are added to the unfolding. The median h on L-2D's 205 cells is 3.0, 3.7, 3.5
  and 3.3 % for L-2D, L-3D, L-4D and L-5D-PV.
  - The finer joint cells are what carry large model dependence: 10–14 % medians in 3D, 4D and 5D, and 18.6 % for
    direct (E_avail, W).

**Every control passes.** Every nominal control (NC) reproduces its recorded central value bit for bit. Every positive
control (PC), at NuWro, passes the declared rule. h is evidence about model dependence at these vertices, not a
per-cell bias bound: |shift| ≥ |bias| holds in 47–71 % of PC cells. The run charged 1.2611 CPU node-h of the 4.0
cap.

## 1. What ran

| rung | classifier features | estimator | npz | NC target | headline cells |
|---|---|---|---|---|---|
| L-EW | (E_avail, W) only; histogrammed on the 5D grid, projected to EW | (e); second arm (c) | `of_inputs_5d.npz` `07fccc1a…` | P5 `fb5cc679…` (read as `e36f3b25…`), P5c `1fa60dfc…` | the 39 RD3 EW cells |
| L-3D | (p_T, p_∥, E_avail) | (e) | RE-1's `of_inputs_3d.npz` `ecbff9f8…` | P3 `8bc7e2d3…` | 690 supported fine cells |
| L-4D | adds q₃ | (e) | RE-1's `of_inputs_4d.npz` `a15cc690…` | P4 `2a18599f…` | 761 supported fine cells |
| L-5D-PV | all five | (e) | `of_inputs_5d.npz` | P5 | the 39 RD3 EW cells; J (109) and (p_T, p_∥) (205) secondary |

- **Estimators:** (e) is s5e candidate R, deterministic LightGBM 100/8 with the 400/31 negative-weight refinement.
  (c) is deterministic LightGBM 100/8 with purity subtraction. Both use seed 42 and 5 iterations.
- **Code:** `nd-unfolding/pv-ladder/`, run pin `ee299e10`. It calls the s5 stack unchanged, with each module's sha256
  equal to the digest RE-1's P5 recorded.
- **Construction:**
  - The vertex reweights are on each rung's own fine cells, from the flux-repaired gen5d predictions. PV-2D's 5 %
    noise gate is pooled over s5p's J-coarse cells.
  - GiBUU is used below p_∥ = 10 GeV/c only: as a cell cut where p_∥ is a reweight axis, and as a truth cut in L-EW.
  - r multiplies `w_truth` and `w_reco` of truth-passing rows. The binned denominator is rescaled so completeness is
    unchanged. On all 22 prior runs, r's spread inside a cell was 0 and completeness held to at most 2.2e-16.
  - The closure is noise-free and signal-only (reco- and truth-passing rows, no background).
- **Cells:** s5p's support rule, applied by `pvl_cells.py`, reproduced s5p's 39 EW cells and s5c's 109 J cells as
  exact lists on the 5D npz.

## 2. Controls

### Nominal controls (rule: max relative difference < 1e-5 on the headline cells)

| rung, arm | target | cells | max rel. diff | bitwise |
|---|---|---|---|---|
| L-3D (e) | P3 | 690 | 0 | yes |
| L-4D (e) | P4 | 761 | 0 | yes |
| L-EW (e), all features | P5 | 39 EW, 109 J | 0, 0 | yes |
| L-EW (c), all features | P5c | 39 EW, 109 J | 0, 0 | yes |
| L-5D-PV (e) | P5 | 39 EW, 109 J | 0, 0 | yes |

- L-EW's NC tests its code path through every step the feature-restricted run uses. No recorded EW central value
  exists, as declared in D2.
- L-EW (e)'s NC and L-5D-PV's are the same computation, and they are bit-identical.

### Positive controls at NuWro

The rule: on the headline cells with |bias| > 1 %, at least 20 cells, correlation ≥ 0.7 and slope in [0.67, 1.5].

| rung | n | corr | slope | verdict | \|shift\| ≥ \|bias\| | bias median / p90 / max | closure floor median / max |
|---|---:|---:|---:|---|---:|---|---|
| L-2D (a) (PV-2D) | 127 | 0.878 | 1.152 | PASS | 61.4 % | | 1.8e-15 / 1.4e-11 |
| L-EW (e) | 36 | 0.933 | 1.216 | PASS | 66.7 % | 7.6 / 27.3 / 43.7 % | 1.0e-5 / 3.8e-4 |
| L-3D (e) | 641 | 0.891 | 1.049 | PASS | 60.1 % | 5.2 / 12.6 / 34.4 % | 3.2e-6 / 4.6e-4 |
| L-4D (e) | 667 | 0.925 | 0.874 | PASS | 46.9 % | 5.9 / 24.6 / 62.3 % | 1.1e-5 / 5.6e-4 |
| L-5D-PV (e) | 35 | 0.982 | 1.206 | PASS | 71.4 % | 9.2 / 19.2 / 26.5 % | 1.0e-5 / 1.3e-4 |

- **No fallback was needed.**
- **The closure floors are 1e-5 level, not PV-2D's 1e-15.** These are LightGBM-path closures on 20.4 M pseudo-data
  rows in every rung, and they sit far below the biases they are compared with.
- **Ungraded secondary PCs** (corr, slope):
  - L-3D: J 0.917, 1.219; (p_T, p_∥) 0.787, 0.864.
  - L-4D: J 0.954, 1.067; (p_T, p_∥) 0.832, 0.960.
  - L-5D-PV: J 0.920, 0.863; (p_T, p_∥) 0.850, 1.150.
- **L-EW (c)** has no PC of its own, as declared.

## 3. The ladder

h is the per-cell envelope max_k |shift_k| over the three vertices, relative to each cell's central value, on each
rung's headline cells. The table is `pvl_report.py`'s.

| rung | arm | cells | h median / p90 / max | dominant (GENIE+MEC / NuWro / GiBUU) | pooled share | step-adjacent share | h / σ |
|---|---|---:|---|---|---|---:|---|
| L-2D (a) | | 205 | 3.00 / 8.30 / 21.4 % | 30 / 88 / 87 | 13.4–35.5 % | 17.5 % | 0.44 vs σ_Q (30 cells > σ) |
| L-2D refined | | 205 | 3.13 / 7.55 / 21.0 % | 34 / 79 / 92 | 13.4–35.5 % | 17.5 % | 0.43 (26) |
| **L-EW** | (e) | 39 EW | **18.65** / 76.9 / 207 % | 2 / 14 / 23 | 0.0–0.5 % | 25.5 % | 1.99 vs C_eavailW (32) |
| L-EW | (c) | 39 EW | 18.53 / 77.8 / 211 % | 1 / 15 / 23 | 0.0–0.5 % | 25.5 % | 2.06 (32) |
| **L-3D** | (e) | 690 fine | **10.40** / 19.7 / 53.4 % | 38 / 292 / 360 | 28.3–49.1 % | 75.2 % | none quoted |
| **L-4D** | (e) | 761 fine | **11.99** / 27.6 / 56.8 % | 38 / 372 / 351 | 44.0–51.6 % | 88.4 % | none quoted |
| **L-5D-PV** | (e) | 39 EW | **12.58** / 27.0 / 38.8 % | 2 / 21 / 16 | 56.6–60.3 % | 94.4 % | — |
| L-5D (s5p, D1–D5) | R | 39 EW (RD3) | 13.4 / 39.2 / — % | | | | |
| L-5D (s5p, D1–D5) | R | 109 J (RD1) | 12.0 / 38.6 / — % | | | | |

**Per vertex, |shift| median / p90 / max on the headline cells:**

| rung | GENIE+MEC | NuWro | GiBUU |
|---|---|---|---|
| L-EW (e) | 1.76 / 4.62 / 8.53 % | 9.26 / 26.0 / 82.4 % | 13.9 / 76.9 / 207 % |
| L-3D (e) | 1.99 / 5.39 / 11.7 % | 6.10 / 14.7 / 53.4 % | 7.07 / 17.6 / 28.5 % |
| L-4D (e) | 1.87 / 5.42 / 16.8 % | 6.67 / 21.9 / 56.8 % | 6.25 / 22.1 / 38.7 % |
| L-5D-PV (e) | 0.50 / 1.80 / 2.30 % | 12.4 / 23.3 / 38.8 % | 6.55 / 27.0 / 35.5 % |

**Two properties of the reweight pull h in opposite directions** (the director's interpretation point):
- **The pooled share** is the prior's truth weight on pooled J-coarse ratios, ranged over the vertices. It rises with
  dimension: 13–36 % in 2D, 28–49 % in 3D, 44–52 % in 4D, 57–60 % in 5D.
  - A coarser effective reweight is a weaker shape departure, which can damp the shifts.
  - **The ladder's h at 4D and 5D may therefore be understated relative to 2D on this account.**
- **The step-adjacent share** is the prior's truth weight in reweight cells beside a step in r > 0.1 drawn by the
  gate or a cut, unioned over the vertices. It also rises: 17.5 % in 2D, 75 % in 3D, 88 % in 4D, 94 % in 5D.
  - PV-2D found its large-shift tail beside such steps (PV-2D REPORT §5), which pushes the other way.
- Neither effect is corrected here.

**h against σ.**
- **L-EW:** against the note's adopted (E_avail, W) covariance C_eavailW, √diag / cv_marginal, median 8.06 %. h/σ has
  a median of 1.99 and h > σ in 32 of 39 cells.
  - C_eavailW belongs to the 5D-projection estimator, not L-EW's.
  - It is the Z-cv trunk projection, used under the 6.4 exception; its metadata records it as not passing.
- **L-3D and L-4D:** the note quotes no uncertainty (`sec_3d.tex:331-334`, `:502-509`), so their h is relative only.

## 4. Ben's question: variables or correlations

L-EW and L-5D-PV share the events, the selection, the weights, the background template, the flux, the normalization,
the estimator (e) and the 39 cells. The direct unfolding's classifiers see only (E_avail, W); the 5D's see all five
axes.

| on the 39 RD3 cells | L-EW (e), direct | L-5D-PV (e), 5D projected | s5p RD3 (D1–D5) |
|---|---|---|---|
| h median / p90 / max | 18.65 / 76.9 / 207 % | 12.58 / 27.0 / 38.8 % | 13.4 / 39.2 / — % |
| h / σ (C_eavailW) median; cells h > σ | 1.99; 32 | 1.71; 29 | |
| **post hoc:** D, the largest truth-level departure, median / max | 27.2 / 191 % | 18.1 / 34.2 % | |
| **post hoc:** h / D median | 0.917 | 0.974 | |

**Limit 2: the two rungs differ in features and in reweight strength.**
- Each rung's reweight is built on its own cells, as declared (§2.2):
  - L-EW applies each generator's full (E_avail, W) shape;
  - L-5D-PV applies the gated 5D shape, with 57–60 % of the prior weight on pooled ratios and, for GiBUU, 20.6 % at
    r = 1.
- The binding's description of L-EW against L-5D-PV as differing "in the features alone" overstated the control. That
  wording was the director's error, and the director has said so (2026-10-24). The declaration's own "only in the
  classifier's features" (§2.3) listed events, weights and normalization, but not the reweight.

**Raw and normalized.** Both are descriptive; the normalization is post hoc, requested by the director after the
output, and computed by `pvl_departure.py` from the 5D npz and the frozen reweights with no rerun.
- **Raw:** the median per-cell ratio h(L-EW) / h(L-5D-PV) is **1.63**. L-EW is lower in 12 of 39 cells.
- **The departure:** for each cell, D = max_k |Σ w_truth·r_k / Σ w_truth − 1| is the largest EW-marginal departure
  the rung's reweight induces at truth level. L-EW's departure is the larger, by a median per-cell ratio of 1.67.
- **Normalized:** the median per-cell ratio (h/D)_L-EW / (h/D)_L-5D-PV is **1.02**, on the 36 cells where both D
  exceed 1 %. L-EW is lower in 16 of them.

**The gate-construction tail.**
- L-EW's three largest shifts, h of 155–207 %, are at E_avail < 0.4 GeV and W > 2.2 GeV (EW10, EW17, EW5). There
  GiBUU's ratio is the pooled J-coarse value 3.05.
- Without the 23 of 39 cells beside a construction-drawn step, L-EW's h is 11.5 / 24.9 / 50.7 % (median / p90 / max).

**The response,** |shift| / |departure| on cells with |departure| > 1 %, per vertex (post hoc):

| | GENIE+MEC | NuWro | GiBUU | h / D |
|---|---|---|---|---|
| L-EW (e), EW cells | 0.26 (27 cells) | 0.71 (31) | 0.87 (33) | 0.92 |
| L-5D-PV (e), EW cells | 0.11 (35) | 1.12 (36) | 0.58 (34) | 0.97 |
| L-2D (a), (p_T, p_∥) cells | 0.33 (150) | 0.20 (163) | 0.36 (113) | 0.29 |
| L-2D refined | 0.29 | 0.16 | 0.35 | 0.29 |

The L-2D rows come from `pvl_response_2d.py` on PV-2D's committed files. They go beyond the director's request and
are given as context. PV-2D's r is constant on each reported cell, so its departure is r − 1 exactly.

**Reading.**
- The direct (E_avail, W) unfolding's larger raw envelope is accounted for by its stronger prior departure.
  Normalized, it matches the 5D unfolding projected onto the same cells.
- In both, about the full departure of the prior reaches the result on these cells (h/D ≈ 0.9–1.0). On the
  (p_T, p_∥) cells about 30 % does.
- So within this test, E_avail and W are weakly constrained by the data whether or not the unfolding conditions on
  the muon kinematics. The 5D correlations neither cause nor cure it.
- **Caveats:**
  - The vertex sets differ from s5p's: three full generator shapes here against s5p's axis-specific D1–D5. L-5D-PV's
    12.6 % against s5p's 13.4 % on the same 39 cells is a coincidence of size, not a control.
  - The normalization uses magnitudes only.
  - GiBUU's extreme pooled ratio dominates the tail.

## 5. The (p_T, p_∥) projection across dimension

On L-2D's 205 cells, each rung's result projected onto (p_T, p_∥):

| rung | h median / p90 / max | GENIE+MEC / NuWro / GiBUU median \|shift\| |
|---|---|---|
| L-2D (a) | 3.00 / 8.30 / 21.4 % | 1.26 / 1.69 / 1.85 % |
| L-2D refined | 3.13 / 7.55 / 21.0 % | 0.94 / 1.62 / 1.78 % |
| L-3D (e) | 3.73 / 7.26 / 12.9 % | 0.95 / 1.52 / 2.44 % |
| L-4D (e) | 3.45 / 6.30 / 12.7 % | 1.06 / 1.76 / 2.73 % |
| L-5D-PV (e) | 3.31 / 7.40 / 15.9 % | 0.84 / 1.90 / 2.28 % |

- **The (p_T, p_∥) observable's model dependence is stable from 2D to 5D:** a median of 3.0–3.7 %, and the p90
  falls from 8.3 % to 6.3–7.4 %.
- **The tail shrinks:** the maximum is 21 % in 2D against 13–16 % above it. Unfolding more variables, and integrating
  them out, does not add prior dependence to this observable at these vertices.
- **What grows is the model dependence of the finer joint cells:**
  - J-coarse: L-3D 6.4 % (27 cells), L-4D 13.2 % (62), L-5D-PV 14.1 % (109); s5p's J 12.0 %;
  - fine headline: 10.4 % in 3D, 12.0 % in 4D;
  - EW: 12.6 % in 5D and 18.6 % direct.
- For Ben's "maximal phase space": the muon-kinematic projection stays at the 2D level, and the hadronic variables
  carry the dependence.
- The pooled-share caveat of §3 applies: the higher rungs' reweight is coarser.

## 6. The cells beside a construction-drawn step

| rung | arm | cells beside a step | h all: median / p90 / max | h rest: median / p90 / max |
|---|---|---:|---|---|
| L-2D (a) | | 52 of 205 | 3.00 / 8.30 / 21.4 % | 2.59 / 6.29 / 15.5 % |
| L-EW | (e) | 23 of 39 | 18.65 / 76.9 / 207 % | 11.5 / 24.9 / 50.7 % |
| L-EW | (c) | 23 of 39 | 18.53 / 77.8 / 211 % | 11.4 / 24.5 / 51.2 % |
| L-3D | (e) | 587 of 690 | 10.40 / 19.7 / 53.4 % | 7.99 / 18.2 / 28.5 % |
| L-4D | (e) | 711 of 761 | 11.99 / 27.6 / 56.8 % | 4.53 / 13.6 / 18.7 % |

- In 3D and 4D, 75 % and 88 % of the prior weight sits beside a gate step, against 17.5 % in 2D.
- At fine resolution the gate draws steps almost everywhere, so the "rest" subsets are small: 103 of 690 cells in 3D,
  50 of 761 in 4D.
- The split is barely informative there.
- It is descriptive, with the rule of PV-2D REPORT §5 generalized to N dimensions (`pvl_lib.classify_cells`, tested
  equal to PV-2D's on the (p_T, p_∥) grid). It was written before any vertex readout was read.

## 7. Comparability limits

These are stated, not corrected:
- **Vertex sets:** PV's three generator shapes here, against s5p's D1–D5 in its 5D record. GiBUU lacks
  E_ν ≳ 20 GeV (KNOWN_ISSUES 82) and is used below p_∥ = 10 GeV/c only.
- **Estimators:** (e) here, (a) and refined in L-2D. L-EW's arms (e) and (c) agree to 0.1 percentage point in the
  median.
- **Cell granularity** differs by rung: 39, 205, 690 and 761 headline cells, and J at 27, 62 and 109.
- **The reweights** are built on each rung's own cells, so their strength differs (§3, §4).
- **σ:** only L-2D and L-EW have a quoted uncertainty, and L-EW's belongs to another estimator.
- **h is not a per-cell bias bound** in any rung.

## 8. Compute

| job | what | elapsed | node-h | × projection |
|---|---|---:|---:|---:|
| 60201984 | prep (debug) | 318 s | 0.0883 | 0.33 |
| 60202408 | J1, failed before any step (launcher) | 21 s | 0.0058 | — |
| 60202786 | J1, every NC | 861 s | 0.2392 | 0.60 |
| 60203686 | J2 | 951 s | 0.2642 | 0.66 |
| 60203687 | J3 | 795 s | 0.2208 | 0.55 |
| 60206334 | J4 | 783 s | 0.2175 | 0.65 |
| 60206336 | J5 | 811 s | 0.2253 | 0.68 |
| | **total** | | **1.2611** of 4.0 | |

- Every job is in [`LEDGER.tsv`](LEDGER.tsv), from `sacct`. Every step in a job started at the same second.
- The departure normalization ran on a login node: 2:32, 6.4 GB, no charge.
- **Products:** 30 unfolds on pscratch, with every sha256 in [`receipts/SHA256SUMS`](receipts/SHA256SUMS). The
  readouts are committed in `nd-unfolding/pv-ladder/readouts/`. Nothing was written to CFS.

## 9. Deviations

All are recorded in RUN.md, with the director told before the step concerned:
1. **The guard amendment (PR #313, bound):** r must be constant on each fine cell. The completeness guard alone is
   vacuous with a binned denominator.
2. **L-5D-PV's NC moved into J1,** so that every rung ran only after its own NC passed.
3. **`--time` set at 1.25× each projection,** tighter than the declared limits.
4. **The reweights kept on pscratch,** read-only and identified by the committed `prep-SHA256SUMS`, instead of being
   committed (22 MB).
5. **The closure cost basis corrected:** 20.4 M pseudo-data rows. The measured closure/data time was at most 1.33×.
6. **One launcher defect fixed before any step ran** (J1 60202408, `SLURM_MEM_PER_NODE`). New pin `ee299e10`.
7. **The departure normalization** (§4) is post hoc, at the director's request after the output.

## 10. Reproduce

```
# the readouts, on Perlmutter at the run pin (pvl_analyze.py refuses any file that differs from prep-SHA256SUMS)
python nd-unfolding/pv-ladder/pvl_analyze.py --rung <rung> --arm <e|c> --products $OUT/products \
    --ratios $OUT/prep/ratios/<rung>/ratios.json --cells nd-unfolding/pv-ladder/cells/<rung>.json \
    [--cov-ew docs/analysis-note/release-package-20260922/covariance_eavailW.npz] --out <file>
python nd-unfolding/pv-ladder/pvl_report.py --readouts nd-unfolding/pv-ladder/readouts --ratios $OUT/prep/ratios
python nd-unfolding/pv-ladder/pvl_departure.py --npz <of_inputs_5d.npz> --expect-npz-sha256 07fccc1a… \
    --ratios $OUT/prep/ratios --out <file>
python3 nd-unfolding/pv-ladder/pvl_response_2d.py
cd nd-unfolding/pv-ladder && python3 -m unittest test_pvl -v     # 23 tests
```

`$OUT` = `/pscratch/sd/j/josephrb/pv-ladder-20261024`.

## 11. Review

See §12, added after the independent review.
