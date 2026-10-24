# Model dependence in 2D and in 5D: the prior-variation envelope compared (director, 2026-10-24)

**By** the paper-tighten lane, as director. Joseph asked for this comparison on 2026-10-23 (`ASSIGNMENT.md`: "You own
the comparison between 2D and 5D"). It is descriptive. It changes no claim and no uncertainty; any change is Joseph's.

**Sources.**
- **2D:** [`REPORT.md`](REPORT.md) (PV-2D, PR #300) and the readouts `2d-unfolding/pv2d/readouts/readout_{a,ref}.json`.
  The director re-read the medians from the readouts.
- **5D:** `RECORD-20260927-s5p-stage2-exit.md` §4 (`:126-131`), and `state/s5p/contract-amendment-6-review1-repairs.json`
  (`:17`, `:44`).

## The numbers

h is the envelope of the per-cell |shift| when the prior is varied, relative to the cell's central value.

| | estimator | cells | vertices | h median | h p90 | h max | coverage: \|shift\| ≥ \|bias\| |
|---|---|---|---|---|---|---|---|
| **2D** (a) | configuration (a), adopted `E_U` | 205 | GENIE+MEC, NuWro, GiBUU shapes vs GENIE CV, on the Tune v1 prior | **3.00 %** | 8.30 % | 21.4 % | 61.4 % (positive-control cells, NuWro) |
| **2D** refined | the refined 2D estimator (RE-2's) | 205 | same | **3.13 %** | 7.55 % | 21.0 % | — |
| **5D** RD1 (J) | R = configuration (e) | 109 | D1–D5 | **12.0 %** | 38.6 % | — | 52–78 % (amendment 6) |
| **5D** RD2 (H2) | R | 27 | D1–D5 | **9.6 %** | 22.5 % | — | |
| **5D** RD3 (EW) | R | 39 | D1–D5 | **13.4 %** | 39.2 % | — | |
| 5D without D1 | R | J / H2 / EW | D2–D5 | 11.25 / 4.28 / 9.90 % | | | |

## Against each result's own uncertainty

- **2D.** The adopted Q has a median per-cell σ_Q of 6.45 %.
  - The median h/σ_Q is 0.44, and 0.43 refined.
  - h > σ_Q in 30 of 205 cells, 26 refined.
  - Against the published per-bin σ the median ratio is 0.45, with h > σ in 28 cells.
  - Most of the h > σ_Q tail sits beside a step in r drawn by the declared noise gate (REPORT §5, post hoc). The median
    is little affected.
- **5D.** The total σ is at least 6 % in every definition (`stage2-exit:52`), while h's medians are 9.6–13.4 %. So h is
  larger than the quoted 5D total in the typical cell. That is why the 5D design is built around a calibrated model
  term (DESIGN §2).

## Reading

- **Model dependence grows strongly with dimension.**
  - **2D:** about 3 % median, roughly half the quoted uncertainty, with a NuWro- and GiBUU-led tail above it in about
    15 % of cells. It is in no 2D uncertainty construction (`uncertainty-preparation-20261008/c/components.tsv` C09:
    "none in the adopted construction").
  - **5D:** about 10–13 % median, the dominant uncertainty.
  - This agrees with D-ID's reading that finer joint cells leave more freedom to the prior (`d-id/REPORT.md:424-425`).
- **The estimator matters little in 2D.** The refined arm's h agrees with (a)'s, with a median per-cell Δshift of
  0.35–0.43 %, so the move to the refined estimator does not change this picture.
- **In both dimensions, h is not a per-cell bound on the bias.** The coverage fraction is 61 % in 2D and 52–78 % in 5D.
  A component built from h measures model dependence; it does not guarantee coverage.

## Comparability limits (stated, not corrected)

- **The vertex sets differ.**
  - 2D uses three generator shapes relative to GENIE CV.
  - 5D uses s5p's D1–D5. D1 was flux-contaminated (KNOWN_ISSUES 83), and later repaired in Stage 0c.
  - GiBUU lacks E_ν ≳ 20 GeV in both (KNOWN_ISSUES 82).
- **The estimators differ:** (a) and refined in 2D, R in 5D.
- **Cell granularity differs,** and so does each dimension's σ construction.
- So the 2D-to-5D ratio of about 3–4× in the median is indicative, not a controlled comparison.

## What adding h to the 2D uncertainty would do (director's arithmetic from `readout_ref.json`)

| | median per cell | p84 |
|---|---|---|
| σ_Q alone | 6.45 % | 9.20 % |
| √(σ_Q² + h²), refined h | **7.69 %** | 12.40 % |
| √(σ_Q² + Σ_k s_k²), the M2 form decided on 2026-10-24 | **7.95 %** | 13.0 % |
| σ_Q + h, linear | 9.95 % | |

- In quadrature the per-cell median increase is 0.59 percentage points.
- An earlier estimate the director gave Joseph from the two medians alone (about 7.1 %) was low. The per-cell figure
  above replaces it.

**Added 2026-10-24.** The M2 row was re-measured by the 2d test lane while building C_model,2D. The decided form,
M2, sums the three vertices' shifts in quadrature, so its total is larger than the envelope total. 7.95 % is the users'
total under the decision; 7.69 % is the envelope total only.
