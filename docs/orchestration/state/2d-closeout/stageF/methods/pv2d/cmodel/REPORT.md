# C_model,2D: the 2D generator-shape model-dependence covariance (2026-10-24, session "2d test")

**Label:** generator-shape model dependence; not a calibrated bound.

C_model,2D is a constructed covariance for the 2D (p_T, p_∥) cross section's dependence on the prior's generator
shape. It is built as `DECISION-20261024-joseph-2d-model-dependence-component.md` item 2 sets it (M2, κ = 1):

  C_model = Σ_k s_k s_kᵀ, k ∈ {GENIE+MEC, NuWro, GiBUU},

with s_k the per-cell relative shift of PV-2D's refined arm at vertex k. That arm unfolds with the Tune v1 prior
reweighted by each generator's shape relative to GENIE CV (`../REPORT.md`, PR #300).
- Each vertex is one fully correlated mode at its measured size, and the three are summed as if independent.
- The build costs 0 node-h; it is arithmetic on committed products.
- Assignment: `state/measurement-scoping/pv-ladder/ASSIGNMENT.md` Part 2 (PR #306). The conventions below were
  accepted by the director on 2026-10-24.

**Q + C_model, the users' total, has a per-cell median of 7.95 %** (p84 13.00 %), against 6.45 % for Q alone. The
7.69 % first quoted for it is the envelope total √(σ_Q² + h²), a different object (§3). The DECISION carries the
director's dated correction (PR #307).

## 1. Products

| product | where | sha256 |
|---|---|---|
| builder | `2d-unfolding/pv2d/cmodel/build_cmodel.py` | in git |
| tests | `2d-unfolding/pv2d/cmodel/test_cmodel.py` | in git |
| summary, with the exact factor S (3 × 205) | `2d-unfolding/pv2d/cmodel/cmodel_2d.json` | in git |
| C_model, fractional (205 × 205) | `cmodel_2d.npz` key `C_model` | matrix bytes `11fe6818…3470` |
| C_abs = diag(x) C_model diag(x), x = Q's x (E_U) | `cmodel_2d.npz` key `C_abs` | matrix bytes `b11b10a0…2d77` |
| the npz (C_model, C_abs, S, cells, x) | `$PSCRATCH/pv2d-20261023/cmodel/cmodel_2d.npz` | file `b3b276c9…a373` |

- **Why the matrix is not in git.** The repo ignores `*.npz` (`.gitignore:30`), with one narrow exception for the
  Appendix F package. C_model is exactly SᵀS, so the committed S carries it in full.
  - `cmodel()` sums the outer products elementwise in a fixed order, not through BLAS, so the matrix sha256 is the
    same on any platform. `test_cmodel.py` rebuilds it from the committed S and checks it.
  - A second build wrote an npz file with the same sha256 (`np.savez` fixes the zip members' dates). The matrix
    sha256 is the identity to cite, since the file's also depends on the numpy and zlib versions.
- **Inputs, each checked by the builder:**
  - `2d-unfolding/pv2d/readouts/readout_ref.json`, sha256 `d220abaa…fd59`.
    - Its arm must be "refined", and each shift array must have one entry per cell.
    - Its own envelope h must equal max_k |s_k| of its own shifts, so an edited shift is refused.
  - `2d-unfolding/pv2d/readouts/readout_a.json`, sha256 `6a0e75f1…e4a6`. Its arm must be "a". It supplies the
    positive control's bias for §5.
  - Q, `cov2d_Q_205.npz`, sha256 `771e49a5…168ced`, which must equal the refined readout's `inputs.Q`.
    - Its cells must be the readout's.
    - Its σ_Q = √diag(Q)/x must reproduce the readout's σ_Q, which it does exactly.
    - The builder was run on a local copy; the CFS path the readout records is in the JSON beside it.
  - `2d-unfolding/pv2d/ratios/projections.json`, sha256 `8241807f…2f05c3`. It must equal both readouts'
    `ratios_projection_sha256`, and it supplies the post-hoc step classes of §4.
- **Units.**
  - C_model is fractional and multiplies the central value on both sides.
  - C_abs scales by Q's x, which is E_U (`2d-unfolding/pv2d/pv2d_analyze.py:113` checks Q's x against E_U to 1e-12), so Q + C_abs adds two
    covariances of the same vector.
  - The s_k are relative to the refined arm's Tune v1 run, which reproduces D2, not E_U. The difference between D2
    and E_U on data has a median of 0.44 %, p84 1.13 % and max 10.1 % at cell 0 (`../../re1/RE1-REPORT-2.md:288-294`). At
    cell 0, scaling by E_U rather than D2 therefore changes C_abs's diagonal by about 20 %.
  - When Q_R replaces Q after RE-2, C_abs should be rescaled by Q_R's x. The fractional C_model does not change.

## 2. The matrix

- **Rank 3.** The form allows at most 3; the rank is 3 here because the three shift vectors are linearly
  independent. The singular values of S are 0.6135, 0.4333 and 0.2830, so C_model's three nonzero eigenvalues are
  their squares (0.376, 0.188, 0.080).
- **Positive semidefinite to rounding.** C_model's smallest computed eigenvalue is −8.6e-17. That figure and the
  singular values come from LAPACK, so their last digits depend on the platform.
- **Share of the trace by vertex:** NuWro 56.6 %, GiBUU 29.2 %, GENIE+MEC 14.2 %.
- **Conditioning, in fractional units.**
  - Q's smallest eigenvalue is 7.4e-7 and its condition number is 6.0e5.
  - Q + C_model's smallest eigenvalue is 8.0e-7 and its condition number is 5.7e5.
  - So the sum is positive definite, and adding C_model does not worsen Q's conditioning.
  - In absolute units the condition numbers are about 8.6e11, set by the dynamic range of x.

## 3. Per-cell totals

On the 205 reported cells, relative to the central value. Each percentile uses numpy's default (linear) method, with
the Weibull method in brackets. For the envelope total's p84, Weibull gives 12.40 % and linear gives 12.37 %.
Weibull is the method that reproduces the director's earlier figure.

| | median | p84 | p90 | max |
|---|---|---|---|---|
| σ_Q alone | 6.45 % | 9.18 % (9.20 %) | | |
| √diag C_model | 3.71 % | 7.10 % (7.13 %) | 8.50 % | 21.10 % |
| **√(σ_Q² + diag C_model), Q + C_model** | **7.95 %** | 13.00 % (13.02 %) | 14.06 % | 24.50 % |
| *for comparison:* h = max_k \|s_k\| | 3.13 % | 6.31 % (6.40 %) | 7.55 % | 21.01 % |
| *for comparison:* √(σ_Q² + h²), the envelope total | 7.69 % | 12.37 % (12.40 %) | 13.52 % | 24.21 % |

- **The envelope total reproduces** `COMPARISON-2D-5D.md`'s figures: median 7.694 %, p84 12.40 % by Weibull.
- **M2 is larger.** Its diagonal is Σ_k s_k², which is at least h² in every cell. So the median of Q + C_model is
  7.95 %, where the envelope total's is 7.69 % and σ_Q's is 6.45 %.
- **The director corrected the DECISION and the comparison** with dated sections (PR #307). This report quotes
  7.95 % as the Q + C_model total.

## 4. The tail caveat (post hoc, descriptive)

PV-2D REPORT §5 found that most of the large shifts sit beside a step in the reweight r larger than 0.1, drawn by the
noise gate or a cut. Per the DECISION, those cells go into C_model as measured. Quantified with the same rule
(`report_tables.classify_cell`, any vertex):
- the 52 step-adjacent cells (25 % of 205) hold **59.4 %** of tr C_model;
- on the other 153 cells, √diag C_model has a median of 3.05 % (p90 6.45 %, max 14.6 %), and Q + C_model a median of
  7.28 %. σ_Q's median on those cells is 6.24 %, so part of the drop from 7.95 % is Q's, not C_model's.

This was not declared before the PV-2D output. It describes where the matrix's weight sits. It removes nothing and
rescales nothing.

## 5. What this is and is not

- **It measures** the unfolded 2D result's dependence on the prior's shape at three generator shapes, on the refined
  estimator, with κ = 1 unscaled.
- **It is not a calibrated bound.** The coverage figures below are on PV-2D's 127 positive-control cells, those with a
  NuWro closure bias above 1 %. The bias is configuration (a)'s, the only arm with a closure. The shifts are the
  refined arm's.

  | σ per cell | cells where σ ≥ \|bias\| (of 127) |
  |---|---|
  | NuWro's own \|shift\| | 67 (52.8 %) |
  | √(s_GENIE+MEC² + s_GiBUU²), leaving the bias's own vertex out | 72 (56.7 %) |
  | √diag C_model | 116 (91.3 %), but **not evidence of coverage** |

  - The last row includes the NuWro shift, which tracks the NuWro bias by construction: that is what the positive
    control tests. Only the first two rows test coverage of a bias C_model was not partly built from.
  - On configuration (a)'s own shifts, NuWro's |shift| reaches |bias| in 78 of 127 cells, the 61.4 % of PV-2D
    REPORT §4.
- **Three vertices span it.** A fourth generator shape would add a fourth direction. Being rank 3, C_model cannot be
  inverted alone; Q + C_model can (§2).
- **Integration** into the note, paper and primer, with Q_R in place of Q, is RE-2's and the director's (DECISION
  item 4). The printed wording goes to Joseph first.

## 6. Reproduce

```
cd 2d-unfolding/pv2d
python3 cmodel/build_cmodel.py --readout readouts/readout_ref.json --readout-a readouts/readout_a.json \
    --q <cov2d_Q_205.npz> --projections ratios/projections.json \
    --out-json cmodel/cmodel_2d.json --out-npz <out>/cmodel_2d.npz
cd cmodel && python3 -m unittest test_cmodel -v     # 14 tests
```

- **The rebuild** here, with the same arguments, reproduced `cmodel_2d.json` byte for byte. The JSON records the
  paths as given, so other arguments change those fields. The LAPACK-derived fields (§2) may differ in their last
  digits on another platform.
- **What the tests pin:**
  - the form;
  - the C_abs scaling;
  - each of the builder's own refusals (arm, array length, an edited shift, Q's sha256, cells and σ_Q) firing on bad
    inputs and staying silent on good ones, and `report_tables`' arm and projections checks firing;
  - the matrix sha256 rebuilt from S;
  - the totals, quantiles, trace share and coverage counts, each recomputed from the committed S, σ_Q,
    projections and PC bias;
  - the numbers this report quotes.

## 7. Review

An independent read-only reviewer recomputed every number and sha256 above from the readouts, Q and the npz,
including the step classification, which it reimplemented on its own. All matched. It found no major defect, and it
flagged the 7.69 % versus 7.95 % conflict as needing a ruling, which PR #307 gave. Its minor findings are fixed:
- the coverage figure was attached to the wrong object. §5 now names each population and adds the leave-out row. The
  reviewer's leave-out count of 78 was on configuration (a)'s shifts; on the refined arm's it is 72.
- the units paragraph cited the wrong section;
- the npz sha256 was wrongly called unreproducible;
- the invertibility claims had no producer. They are now computed and recorded in the JSON.
- the tests had gaps. They now recompute the derived fields and test the refusals and C_abs.

Its nits are fixed too: the platform scope of the LAPACK fields, the recorded input paths, "the covariance", the rank
wording and a dangling section reference.
