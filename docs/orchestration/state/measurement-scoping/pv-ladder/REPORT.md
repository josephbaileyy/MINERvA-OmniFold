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

**The declared results.**
- **Controls:** every nominal control (NC) reproduces its recorded central value bit for bit. Every positive control
  (PC), at NuWro, passes the declared rule.
- **h** is the per-cell envelope of the |shift| over the three vertices. Its median on each rung's headline cells:

  | rung | cells | median h |
  |---|---|---|
  | L-2D | 205 | 3.0 % |
  | L-EW | 39 EW | 18.6 % |
  | L-3D | 690 fine | 10.4 % |
  | L-4D | 761 fine | 12.0 % |
  | L-5D-PV | 39 EW | 12.6 % |

- **Projected onto L-2D's 205 (p_T, p_∥) cells,** the median h is 3.0, 3.7, 3.5 and 3.3 % for L-2D, L-3D, L-4D and
  L-5D-PV.
- **h is not a per-cell bias bound:** |shift| ≥ |bias| holds in 47–71 % of PC cells.
- **Compute:** 1.2611 CPU node-h of the 4.0 cap.

**Ben's questions.** Each part below says whether it rests on declared or post-hoc numbers.
- **"Maximal phase space."**
  - **Declared:** the muon-kinematic (p_T, p_∥) observable's raw h stays at the 2D level when E_avail, q₃ and W are
    added to the unfolding, at 3.0–3.7 %. The finer joint cells carry the larger model dependence: 10–14 % medians
    in 3D to 5D.
  - **Post hoc:** normalized by the prior departure, the (p_T, p_∥) response is about 0.43 in 3D to 5D, against
    0.29 in 2D, with signs near chance.
- **"E_avail and W, or the 5D correlations?"**
  - **Declared:** the direct (E_avail, W) unfolding's envelope is the larger: median per-cell ratio 1.63 against
    L-5D-PV on the same 39 cells.
  - **Post hoc:** L-EW's reweight is also the stronger truth-level departure, 1.67× at the median. Normalized by that
    departure, the median ratio is 1.02. So at the median the two envelopes are similar for the departure applied,
    but per cell the agreement is loose (§4).
  - **Post hoc, sign-aware and same-vertex:** the 5D projection follows the prior's departure less, with a median
    response of 0.52 against 0.87. That is the strongest single indication here that conditioning on the other axes
    helps.
  - **Post hoc, on both measures:** a large part of the prior's departure reaches the result on the EW cells (h/D
    0.92 and 0.97), against about 0.43 on the (p_T, p_∥) cells.

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
- **The vertex reweights** are built on each rung's own fine cells (DECLARATION §2.2), from the flux-repaired gen5d
  predictions.
  - PV-2D's 5 % noise gate is pooled over s5p's J-coarse cells.
  - GiBUU is used below p_∥ = 10 GeV/c only: as a cell cut where p_∥ is a reweight axis, and as a truth cut in L-EW.
  - The gate tiers per rung and vertex are in RUN.md §3.
- **The reweight's application:**
  - r multiplies `w_truth` and `w_reco` of truth-passing rows inside the npz's grid.
  - The binned denominator is rescaled so completeness is unchanged. On all 22 prior runs, r's spread inside a cell
    was 0, and completeness held to 2.2e-16.
- **The closure** is noise-free and signal-only: reco- and truth-passing rows, 20.4 M of them in every rung, with no
  background.
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
  exists (D2).
- L-EW (e)'s NC and L-5D-PV's are the same computation, and they are bit-identical.

### Positive controls at NuWro

The rule: on the headline cells with |bias| > 1 %, at least 20 cells, correlation ≥ 0.7 and slope in [0.67, 1.5].

| rung | n | corr | slope | verdict | \|shift\| ≥ \|bias\| | bias median / p90 / max | closure floor median / max |
|---|---:|---:|---:|---|---:|---|---|
| L-2D (a) (PV-2D) | 127 | 0.878 | 1.152 | PASS | 61.4 % | 1.3 / 5.3 / 14.0 % | 1.8e-15 / 1.4e-11 |
| L-EW (e) | 36 | 0.933 | 1.216 | PASS | 66.7 % | 7.6 / 27.3 / 43.7 % | 1.0e-5 / 3.8e-4 |
| L-3D (e) | 641 | 0.891 | 1.049 | PASS | 60.1 % | 5.2 / 12.6 / 34.4 % | 3.1e-6 / 4.6e-4 |
| L-4D (e) | 667 | 0.925 | 0.874 | PASS | 46.9 % | 5.9 / 24.6 / 62.3 % | 1.1e-5 / 5.6e-4 |
| L-5D-PV (e) | 35 | 0.982 | 1.206 | PASS | 71.4 % | 9.2 / 19.2 / 26.5 % | 1.0e-5 / 1.3e-4 |

- **No fallback was needed.**
- **The closure floors are 1e-5 level, not PV-2D's 1e-15.** These closures run the LightGBM path on 20.4 M
  pseudo-data rows, and the floors sit far below the biases they are compared with.
- **Ungraded secondary PCs** (corr, slope):
  - L-3D: J 0.917, 1.219; (p_T, p_∥) 0.787, 0.864.
  - L-4D: J 0.954, 1.067; (p_T, p_∥) 0.832, 0.960.
  - L-5D-PV: J 0.920, 0.863; (p_T, p_∥) 0.850, 1.150.
- **L-EW (c)** has no PC of its own, as declared.

## 3. The ladder (declared readouts)

h is the per-cell envelope max_k |shift_k| over the three vertices, relative to each cell's central value, on each
rung's headline cells. The numbers come from `readouts/tables.md`, written by `pvl_report.py`.

| rung | arm | cells | vertex set | h median / p90 / max | dominant (GENIE+MEC / NuWro / GiBUU) | PC | pooled share | step-adjacent share | h / σ median (cells h > σ) |
|---|---|---:|---|---|---|---|---|---:|---|
| L-2D (a) | | 205 | PV | 3.00 / 8.30 / 21.4 % | 30 / 88 / 87 | PASS | 13.4–35.5 % | 17.5 % | 0.44 vs σ_Q (30) |
| L-2D refined | | 205 | PV | 3.13 / 7.55 / 21.0 % | 34 / 79 / 92 | on (a) | 13.4–35.5 % | 17.5 % | 0.43 (26) |
| **L-EW** | (e) | 39 EW | PV | **18.65** / 76.9 / 207 % | 2 / 14 / 23 | PASS | 0.0–0.5 % | 25.5 % | 1.99 vs C_eavailW (32) |
| L-EW | (c) | 39 EW | PV | 18.53 / 77.8 / 211 % | 1 / 15 / 23 | none (arm (c)) | 0.0–0.5 % | 25.5 % | 2.06 (32) |
| **L-3D** | (e) | 690 fine | PV | **10.40** / 19.7 / 53.4 % | 38 / 292 / 360 | PASS | 28.3–49.1 % | 75.2 % | none quoted |
| **L-4D** | (e) | 761 fine | PV | **11.99** / 27.6 / 56.8 % | 38 / 372 / 351 | PASS | 44.0–51.6 % | 88.4 % | none quoted |
| **L-5D-PV** | (e) | 39 EW | PV | **12.58** / 27.0 / 38.8 % | 2 / 21 / 16 | PASS | 56.6–60.3 % | 94.4 % | 1.71 vs C_eavailW (29) |
| L-5D (s5p) | R | 39 EW (RD3) | D1–D5 | 13.4 / 39.2 / — % | | | | | |
| L-5D (s5p) | R | 109 J (RD1) | D1–D5 | 12.0 / 38.6 / — % | | | | | |

**Per vertex, |shift| median / p90 / max, and the signed median, on the headline cells:**

| rung | GENIE+MEC | NuWro | GiBUU |
|---|---|---|---|
| L-EW (e) | 1.76 / 4.62 / 8.53 % (+0.37 %) | 9.26 / 26.0 / 82.4 % (−0.46 %) | 13.9 / 76.9 / 207 % (+3.52 %) |
| L-EW (c) | 1.74 / 4.43 / 9.61 % (+0.02 %) | 8.48 / 26.3 / 82.4 % (+0.22 %) | 14.3 / 77.8 / 211 % (+3.21 %) |
| L-3D (e) | 1.99 / 5.39 / 11.7 % (−0.04 %) | 6.10 / 14.7 / 53.4 % (−1.68 %) | 7.07 / 17.6 / 28.5 % (+0.53 %) |
| L-4D (e) | 1.87 / 5.42 / 16.8 % (+0.05 %) | 6.67 / 21.9 / 56.8 % (−2.65 %) | 6.25 / 22.1 / 38.7 % (−0.02 %) |
| L-5D-PV (e) | 0.50 / 1.80 / 2.30 % (−0.07 %) | 12.4 / 23.3 / 38.8 % (+5.58 %) | 6.55 / 27.0 / 35.5 % (+1.20 %) |

The secondary spaces' per-vertex tables, the J space included, are in each readout's `spaces` field
(`nd-unfolding/pv-ladder/readouts/`).

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
- **L-EW and L-5D-PV:** against the note's adopted (E_avail, W) covariance C_eavailW, √diag / cv_marginal, median
  8.06 %.
  - C_eavailW belongs to the 5D-projection estimator, not L-EW's.
  - It is the Z-cv trunk projection, used under the 6.4 exception; its metadata records it as not passing.
  - The declared readout is L-EW's. L-5D-PV's is given for comparison.
- **L-3D and L-4D:** the note quotes no uncertainty (`sec_3d.tex:331-334`, `:502-509`), so their h is relative only.

## 4. Ben's question: variables or correlations

L-EW and L-5D-PV share the events, the selection, the weights, the background template, the flux, the normalization,
the estimator (e) and the 39 cells. The direct unfolding's classifiers see only (E_avail, W); the 5D's see all five
axes.

**Limit 2: the two rungs differ in features and in reweight strength.**
- Each rung's reweight is built on its own cells (DECLARATION §2.2):
  - L-EW applies each generator's full (E_avail, W) shape;
  - L-5D-PV applies the gated 5D shape, with 57–60 % of the prior weight on pooled ratios and, for GiBUU, 20.6 % at
    r = 1.
- **The error started in this lane's declaration.** DECLARATION.md:110 says L-EW "must differ from L-5D-PV only in
  the classifier's features", and :213-214 says the comparison "differs in the features alone".
- **The binding repeated it** ("differs in the features alone", BINDING.md:16), and so did `pvl_report.py`'s heading
  until this report's review.
- The director asked that the binding's wording be recorded as an error (message of 2026-10-24).

**The declared comparison.**

| on the 39 RD3 cells | L-EW (e), direct | L-5D-PV (e), 5D projected | s5p RD3 (D1–D5) |
|---|---|---|---|
| h median / p90 / max | 18.65 / 76.9 / 207 % | 12.58 / 27.0 / 38.8 % | 13.4 / 39.2 / — % |
| h / σ (C_eavailW) median; cells h > σ | 1.99; 32 | 1.71; 29 | |

- **Raw:** the median per-cell ratio h(L-EW) / h(L-5D-PV) is **1.63**. L-EW is lower in 12 of 39 cells, and the
  ratio of the medians is 1.48.
- **The gate-construction tail:**
  - L-EW's three largest shifts, h of 155–207 %, are at E_avail < 0.4 GeV and W > 2.2 GeV (EW10, EW17, EW5). There
    GiBUU's ratio is the pooled J-coarse value 3.05.
  - Without the 23 of 39 cells beside a construction-drawn step, L-EW's h is 11.5 / 24.9 / 50.7 % (median / p90 /
    max).

**Post hoc: normalized by the prior's departure.** This is descriptive and was requested by the director after the
output. `pvl_departure.py` computes it from the 5D npz, the frozen reweights and the committed readouts, with no
unfold rerun; the output is `readouts/departure.json`.
- **Definitions:**
  - For vertex k and EW cell c, d_kc = Σ w_truth·r_k / Σ w_truth − 1 over the cell's truth-passing rows. It is the
    truth-level EW-marginal departure the reweight induces.
  - D_c = max_k |d_kc|.
- **D is larger for L-EW:** median 27.2 % against 18.1 %. The median per-cell ratio D(L-EW)/D(L-5D-PV) is 1.67.

| | L-EW (e) | L-5D-PV (e) |
|---|---|---|
| h / D median (cells with D > 1 %) | 0.917 (37) | 0.974 (37) |
| … at D > 3, 5, 10 % | 0.899, 0.899, 0.881 | 0.974, 0.856, 0.800 |
| same-vertex signed response s_k*/d_k*, k* = argmax_k \|d_kc\|: median (IQR) | **0.87** (0.40–1.07) | **0.52** (0.02–0.97) |
| cells where the vertex setting h also sets D | 32 of 39 | 16 of 39 |

Per vertex, on cells with |d| > 1 %:

| vertex | rung | \|d\| median | response \|s\|/\|d\| median | signed s/d median | same sign |
|---|---|---|---|---|---|
| GENIE+MEC | L-EW | 2.43 % | 0.26 | 0.07 | 17 of 27 |
| | L-5D-PV | 3.30 % | 0.11 | 0.00 | 18 of 35 |
| NuWro | L-EW | 12.5 % | 0.71 | 0.63 | 27 of 31 |
| | L-5D-PV | 9.20 % | 1.12 | 0.97 | 29 of 36 |
| GiBUU | L-EW | 17.8 % | 0.87 | 0.87 | 29 of 33 |
| | L-5D-PV | 15.8 % | 0.58 | 0.25 | 25 of 34 |

**The normalized ratio,** (h/D)_L-EW / (h/D)_L-5D-PV per cell:
- Its median is **1.02** on the 36 cells where both D exceed 1 % (IQR 0.66–1.39). It stays at 1.02–1.06 for D > 3,
  5 and 10 %.
- Only 16 of 36 cells lie within [0.8, 1.25].
- The log-correlation between the raw h ratio and the D ratio is 0.58.

**What the normalization supports.**
- **At the median,** the direct unfolding's larger envelope is consistent with its stronger prior departure. For
  the departure applied, the two envelopes are similar.
- **Per cell and per vertex the agreement is loose,** and the measures differ:
  - h and D come from the same vertex in only 16 of 39 L-5D-PV cells;
  - the per-vertex response ratios L-EW/L-5D-PV are 2.4, 0.63 and 1.5 for GENIE+MEC, NuWro and GiBUU;
  - GENIE+MEC's shifts follow its departure's sign at chance in 5D (18 of 35).
- **On the sign-aware same-vertex measure,** the 5D projection follows the prior's departure about 0.6× as much as
  the direct unfolding (0.52 against 0.87). That is the strongest single indication that conditioning on the other
  axes helps.
- **On both measures,** a large part of the departure reaches the EW cells' result: h/D 0.92 and 0.97, and signed
  responses of 0.5–0.9 at the leading vertex.

**Caveats.**
- All of this is post hoc.
- h/D mixes vertices.
- GiBUU's extreme pooled ratio dominates the tail.
- The vertex sets differ from s5p's: PV's three full generator shapes against s5p's axis-specific D1–D5. L-5D-PV's
  12.6 % against s5p's 13.4 % on the same 39 cells is a match in size, not a controlled comparison.

## 5. The (p_T, p_∥) projection across dimension

**Declared, raw h** on L-2D's 205 cells, each rung's result projected onto (p_T, p_∥):

| rung | h median / p90 / max | GENIE+MEC / NuWro / GiBUU median \|shift\| |
|---|---|---|
| L-2D (a) | 3.00 / 8.30 / 21.4 % | 1.26 / 1.69 / 1.85 % |
| L-2D refined | 3.13 / 7.55 / 21.0 % | 0.94 / 1.62 / 1.78 % |
| L-3D (e) | 3.73 / 7.26 / 12.9 % | 0.95 / 1.52 / 2.44 % |
| L-4D (e) | 3.45 / 6.30 / 12.7 % | 1.06 / 1.76 / 2.73 % |
| L-5D-PV (e) | 3.31 / 7.40 / 15.9 % | 0.84 / 1.90 / 2.28 % |

**Post hoc, the same normalization on the (p_T, p_∥) cells,** at the director's request so that it is not applied
to one space only.
- For L-3D, L-4D and L-5D-PV, `pvl_departure.py` takes the departure from each rung's reweight-cell prior truth
  weight. That is exact because r is constant on each reweight cell. For L-2D, `pvl_response_2d.py` uses PV-2D's
  committed ratios, where the departure is r − 1.

| rung | D median | h / D median (cells D > 1 %) | … at D > 10 % | same-vertex signed response median (IQR) | signed s/d median, GENIE+MEC / NuWro / GiBUU | same sign (of cells \|d\| > 1 %) |
|---|---|---|---|---|---|---|
| L-2D (a) | 8.63 % | 0.29 (184) | 0.17 (91) | 0.12 | 0.08 / 0.03 / 0.19 | 84/150, 86/163, 74/113 |
| L-2D refined | 8.63 % | 0.29 (184) | 0.16 (91) | 0.10 | 0.09 / 0.03 / 0.18 | 85/150, 88/163, 76/113 |
| L-3D (e) | 8.05 % | 0.42 (204) | 0.28 (81) | 0.17 (0.01–0.41) | 0.08 / 0.07 / 0.23 | 115/182, 101/164, 97/138 |
| L-4D (e) | 8.19 % | 0.45 (205) | 0.27 (74) | 0.23 (−0.05–0.43) | −0.07 / 0.05 / 0.25 | 79/179, 96/182, 97/138 |
| L-5D-PV (e) | 7.60 % | 0.43 (199) | 0.30 (64) | 0.20 (−0.03–0.41) | 0.01 / 0.04 / 0.21 | 88/168, 94/171, 92/138 |

**Reading.**
- **Raw h is stable from 2D to 5D:** a median of 3.0–3.7 %. The p90 falls from 8.3 % to 6.3–7.4 %, and the
  maximum from 21 % to 13–16 %. On this declared measure the (p_T, p_∥) observable stays at the 2D level when the
  hadronic variables are added to the unfolding.
- **Normalized by the departure, the response is higher above 2D:** h/D about 0.43 against 0.29. The same-vertex
  signed response is 0.17–0.23 against 0.10–0.12.
- **The signs are near chance** for GENIE+MEC and NuWro in every rung, so these responses are mostly magnitude, not a
  systematic pull toward the prior.
- So the (p_T, p_∥) stability holds for raw h. A modest rise in the normalized response above 2D is not excluded.
- **Against the EW cells,** the contrast survives in weaker form: normalized about 0.43 here against 0.92–0.97 on
  EW, and raw about 3 % here against 12–19 % on EW.
- **The finer joint cells carry the larger model dependence:**
  - J-coarse: L-3D 6.4 % (27 cells), L-4D 13.2 % (62), L-5D-PV 14.1 % (109); s5p's J 12.0 % (D1–D5);
  - fine headline: 10.4 % in 3D and 12.0 % in 4D;
  - EW: 12.6 % in 5D and 18.6 % direct.
- The pooled-share caveat of §3 applies: the higher rungs' reweight is coarser.

## 6. The cells beside a construction-drawn step (descriptive)

| rung | arm | cells beside a step | h all: median / p90 / max | h rest: median / p90 / max |
|---|---|---:|---|---|
| L-2D (a) | | 52 of 205 | 3.00 / 8.30 / 21.4 % | 2.59 / 6.29 / 15.5 % |
| L-EW | (e) | 23 of 39 | 18.65 / 76.9 / 207 % | 11.5 / 24.9 / 50.7 % |
| L-EW | (c) | 23 of 39 | 18.53 / 77.8 / 211 % | 11.4 / 24.5 / 51.2 % |
| L-3D | (e) | 587 of 690 | 10.40 / 19.7 / 53.4 % | 7.99 / 18.2 / 28.5 % |
| L-4D | (e) | 711 of 761 | 11.99 / 27.6 / 56.8 % | 4.53 / 13.6 / 18.7 % |

- In 3D and 4D, 75 % and 88 % of the prior weight sits beside a step drawn by the gate or a cut, against 17.5 % in
  2D.
- At fine resolution the gate draws steps almost everywhere, so the "rest" subsets are small: 103 of 690 cells in 3D,
  50 of 761 in 4D.
- The split is barely informative there.
- The rule is PV-2D REPORT §5's, generalized to N dimensions (`pvl_lib.classify_cells`, tested equal to PV-2D's on
  the (p_T, p_∥) grid). The rule and the table code were committed (`c6007dea`) before any vertex readout was read.

## 7. Comparability limits

These are stated, not corrected:
- **Vertex sets:** PV's three generator shapes here, against s5p's D1–D5 in its 5D record. GiBUU lacks
  E_ν ≳ 20 GeV (KNOWN_ISSUES 82) and is used below p_∥ = 10 GeV/c only.
- **Estimators:** (e) here, (a) and refined in L-2D. L-EW's arms (e) and (c) agree to about 0.1 percentage point in
  the median.
- **Cell granularity** differs by rung: 39, 205, 690 and 761 headline cells, and J at 27, 62 and 109.
- **The reweights** are built on each rung's own cells, so their strength differs. The pooled share rises with
  dimension (§3), and L-EW departs more strongly than L-5D-PV (§4).
- **σ:** only L-2D and L-EW have a declared σ readout, and the EW σ belongs to another estimator.
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
- The post-hoc departure runs were on a login node, with no charge.
- **Products:** 30 unfolds on pscratch, with every sha256 in [`receipts/SHA256SUMS`](receipts/SHA256SUMS). The
  readouts, the departure output and the 2D-response output are committed in `nd-unfolding/pv-ladder/readouts/`.
- Nothing was written to CFS.

## 9. Deviations

All are recorded in RUN.md:
1. **The guard amendment (PR #313, bound):** r must be constant on each fine cell. The completeness guard alone is
   vacuous with a binned denominator.
2. **L-5D-PV's NC moved into J1,** so that every rung ran only after its own NC passed.
3. **J1 ran seven concurrent steps at 36 CPUs,** not the declared "42 CPUs, up to six". LightGBM's `num_threads` is
   fixed at 32 either way, and every NC is bitwise.
4. **`--time` set at 1.25× each projection,** tighter than the declared limits.
5. **The reweights kept on pscratch,** read-only and identified by the committed `prep-SHA256SUMS`, instead of being
   committed (22 MB).
6. **The closure cost basis corrected:** 20.4 M pseudo-data rows. The measured closure/data step time ran 0.75–1.39×
   (3D) and about 1.0× (4D).
7. **One launcher defect fixed before any step ran** (J1 60202408, `SLURM_MEM_PER_NODE`). New pin `ee299e10`.
8. **`pvl_report.py` was edited after the outputs:**
   - the pooled-share precision, from 0 to 1 decimal (`2d6829ba`);
   - its §2 heading, from "(the features alone differ)" (this review).

   No number changed.
9. **The departure normalization** (§4, §5) is post hoc, at the director's request after the output. It was extended
   to the (p_T, p_∥) cells after this report's review, again at the director's request.

## 10. Reproduce

`$OUT` = `/pscratch/sd/j/josephrb/pv-ladder-20261024`.

```
# the readouts, at the run pin ee299e10 (pvl_analyze.py refuses any file that differs from prep-SHA256SUMS)
python nd-unfolding/pv-ladder/pvl_analyze.py --rung <rung> --arm <e|c> --products $OUT/products \
    --ratios $OUT/prep/ratios/<rung>/ratios.json --cells nd-unfolding/pv-ladder/cells/<rung>.json \
    [--cov-ew docs/analysis-note/release-package-20260922/covariance_eavailW.npz] --out <file>
# the tables and the post-hoc measures, at 595930c1 or later on this branch
python nd-unfolding/pv-ladder/pvl_report.py --readouts nd-unfolding/pv-ladder/readouts --ratios $OUT/prep/ratios
python nd-unfolding/pv-ladder/pvl_departure.py --npz <of_inputs_5d.npz> --expect-npz-sha256 07fccc1a… \
    --ratios $OUT/prep/ratios --out <file>
python3 nd-unfolding/pv-ladder/pvl_response_2d.py --out <file>
cd nd-unfolding/pv-ladder && python3 -m unittest test_pvl -v     # 25 tests
```

## 11. Review

**The first independent review** was read-only and used its own code. It recomputed every declared number
(NC, PC, h, σ, shares, step split, compute) and the post-hoc departures, and all matched.
- It found four major problems in an earlier draft's reading of the post-hoc normalization. All are fixed above:
  - the normalization mixed vertices and ignored sign;
  - it was applied to the EW cells only;
  - some post-hoc numbers were unlabelled;
  - the "features alone" error was attributed incompletely.
- Its minors and nits are fixed too: signed medians, the PC and vertex-set columns, deviations 3 and 8, RUN.md's stale
  lines, recorded inputs and outputs for the post-hoc scripts, the reproduce block, and the L-5D-PV h/σ consistency.

§12 is added after the confirmation review.
