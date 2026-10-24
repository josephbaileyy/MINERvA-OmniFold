# Declaration: the prior-variation dimension ladder (2026-10-24, session "2d test", awaiting binding)

**Under** [`ASSIGNMENT.md`](ASSIGNMENT.md) Part 1 (PR #306). **Written before any output.** No ladder job has been
submitted, and none will be until the director binds this record and it is on `main`.

**The test** is PV-2D's, unchanged, at each new rung (`../../2d-closeout/stageF/methods/pv2d/BINDING.md`):
- unfold the real data with the Tune v1 prior reweighted by each generator's shape relative to GENIE CV, for
  GENIE+MEC, NuWro and GiBUU;
- apply the same 5 % noise gate and the same nominal and positive controls;
- read out the per-vertex shift and the envelope h.

What changes between rungs is the set of observables, and with it the cells. §1 lists the rungs and §2 the
construction. §3 gives the control rules, §4 the readouts, §5 the compute and §6 the deviations. §7 has the choices
the director is asked to bind.

## 1. The rungs

| rung | unfolded observables (classifier features) | estimator | input | recorded central value (NC target) | status |
|---|---|---|---|---|---|
| **L-EW** | (E_avail, W) only | **(e)**, primary arm; **(c)**, second arm (§6, D1) | the 5D npz, features restricted (§2.3) | none exists; see D2 | new |
| L-2D | (p_T, p_∥) | (a) and refined | — | — | PV-2D, reused |
| **L-3D** | (p_T, p_∥, E_avail) | (e) | RE-1's `3d/of_inputs_3d.npz` `ecbff9f8…`, `3d/bkg_3d.npz` `b99a19ef…` | RE-1's **P3**, `3d/p3.npz` `8bc7e2d3…` | new |
| **L-4D** | (p_T, p_∥, E_avail, q₃) | (e) | RE-1's `4d/of_inputs_4d.npz` `a15cc690…`, `4d/bkg_4d.npz` `2c3cc1a8…` | RE-1's **P4**, `4d/p4.npz` `2a18599f…` | new |
| L-5D | all five | R = (e) | — | — | s5p, on record (D1–D5); reused, not rerun |
| *L-5D-PV* | all five | (e) | `of_inputs_5d.npz` `07fccc1a…`, `bkg_dump.npz` `2addac8f…` | **P5** `fb5cc679…`, read as RE-1's `5d/k1_p5_rerun.npz` `e36f3b25…`, equal to P5 bit for bit in `xsec_flat` | **optional; only if bound (D3)** |

- **Inputs.** RE-1's files are under `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/`, with their sha256s
  in `re1/run2/receipts/SHA256SUMS.{inputs,nd}`. The 5D npz is
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` and its background dump is
  `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz`. These are the s5p task rows' inputs
  (`state/s5p/s2-prior-tasks.tsv`) and RE-1's (`re1/run2/launch/re1_nd.sbatch`). Every job re-hashes every input
  and refuses on a mismatch.
- **Estimators** follow `docs/analysis-note/sec_method.tex:231-257`, with every configuration at 100 trees and 8 leaves (`:190-191`):
  - **(e)** is deterministic LightGBM OmniFold at 100/8 with the unbinned negative-weight background refinement at
    400/31. That is s5e candidate R, the path RE-1 used for P3, P4 and P5
    (`s5e_candidate.py --candidate R -- … --data --bkg-mode negweight-refined`).
  - **(c)** is deterministic LightGBM at 100/8 with purity subtraction (`s5n_pseudo.py … --bkg-mode purity`), the
    path of RE-1's P3c, P4c and P5c.
  - Every run uses estimator seed 42, 5 iterations and 32 LightGBM threads.

## 2. Construction

### 2.1 Cells and binning

All rungs use the fine grid of the 5D analysis, restricted to the rung's axes (`nd-unfolding/s5p_stage1_inspect.py:38-44`,
the `EXTRA_AXES` registry):
- p_T: the paper's 14 bins;
- p_∥: the paper's 16 bins;
- E_avail: `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100]` GeV;
- q₃: `[0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100]` GeV;
- W: `[0, 1.1, 1.4, 1.8, 2.2, 3.0, 100]` GeV.

| rung | fine grid | **headline cells** | declared secondary cells |
|---|---|---|---|
| L-EW | 7 × 6 = 42 | **the 39 EW cells s5p's support rule keeps**: all but EW11, EW36 and EW37 (`state/s5p/contract-amendment-1-use-case-and-targets.json:47`). These are the note's EW cells and RD3's (`sec_eavailw.tex:235-238`, `sec_5d.tex:281,337`). | — |
| L-3D | 14 × 16 × 7 = 1,568 | **the supported cells:** P3 > 0, and the expected reco-level signal and the truth-selected weight at data POT are both ≥ 1000 (s5p's `SUPPORT_MIN`, applied to this rung's cells from its own npz) | (i) the J-coarse cells on (p_T, p_∥, E_avail), 3 × 3 × 3, supported by the same rule; (ii) the projection onto the 205 (p_T, p_∥) cells of L-2D |
| L-4D | 14 × 16 × 7 × 7 = 10,976 | the supported cells, by the same rule, with P4 > 0 | (i) the J-coarse cells, 3⁴; (ii) the projection onto the 205 (p_T, p_∥) cells |
| *L-5D-PV* | 65,856 | the 39 EW cells, so it is directly comparable with L-EW, and the 109 supported J cells (RD1) | the projection onto the 205 (p_T, p_∥) cells |

- **Cell semantics** are `np.histogramdd`'s, with the last edge closed: the s5 stack's convention, not ROOT's.
- **Projections** are cell-integrated cross sections, summed over the dropped axes. This is s5p's RD3 convention
  (`s5p_assemble.py:5-7`), so an L-EW cell and an RD3 cell are the same functional.
- **EW cell index:** EWi = i_E · 6 + i_W (`s5p_stage1_inspect.py:99-102`).
- **The cell counts of the supported sets** are written by the pilot job, before any vertex run (§5). The pilot
  only fixes them; it does not choose them.

### 2.2 The vertex reweights

These are the PV-2D construction (`2d-unfolding/pv2d/make_ratios.py`), on each rung's cells.
- **Inputs:** the same flux-repaired gen5d predictions, with their sha256s from PV-2D's `projections.json`:
  - GENIE 2.12 CV, the reference: `genie_cv_xsec5d_full.npz` `cfa42210…`;
  - GENIE+MEC: `c179855d…`;
  - NuWro: `475a2871…`;
  - GiBUU: `48917692…`.
  These are full 5D densities, so each rung's predictions are exact integrals over its dropped axes.
- **Per vertex k and fine cell c:**
  - ρ_kc = g_kc / gref_c, gated (`pv2d_lib.gated_shape_ratio`, unchanged):
    - a cell keeps its own ratio where its relative statistical error is ≤ 5 %;
    - otherwise it takes the pooled ratio of its J-coarse cell on the rung's axes, under the same bound (`J_EDGES`,
      `s5p_stage1_inspect.py:45-46`; PV-2D's coarse cells are the J edges on p_T and p_∥);
    - otherwise r = 1.
  - r_kc = ρ_kc × k_k on the assigned cells, and 1 elsewhere. k_k fixes the rung's own prior truth weight
    (`w_truth` on truth-passing rows) summed over the assigned cells, so each vertex is a pure shape departure.
- **Region:** the rung's cells with recorded central value > 0 where both predictions are positive. For L-EW, the
  42 cells where both predictions are positive.
- **GiBUU** only below truth p_∥ = 10 GeV/c, as in PV-2D (KNOWN_ISSUES 82).
  - In L-3D and L-4D that is a cell cut.
  - L-EW has no p_∥ axis. There, GiBUU's and the reference's EW predictions are integrated over p_∥ < 10 GeV/c
    only. The reweight is applied to truth rows with p_∥ < 10 GeV/c, and r = 1 elsewhere.
  - So the reweight uses a truth variable that is not an L-EW feature. That is allowed, because the prior is the
    full MC truth distribution.
- **Application:**
  - r multiplies `w_truth` and `w_reco` of every truth-passing MC row.
  - The binned truth denominator is rescaled cell by cell by the ratio of truth-passing weights, so completeness
    stays the nominal value. This is s5p's `prior_inputs`, `s5p_universe.py:131-147`, after the 2026-09-26 repair.
  - The background, the flux and the data are unchanged.
  - **A completeness guard** requires the reweighted completeness to equal the nominal one on every cell to 1e-9,
    as in PV-2D, and the run refuses otherwise.
- **Gate tiers** (cells and share of prior weight in own-ratio, coarse and r = 1) are written by the ratio builder
  for every vertex and rung, as the PV-2D binding requires.

### 2.3 Restricting L-EW's features

L-EW must differ from L-5D-PV only in the classifier's features.
- **Kept the same:** the events, the selection, the weights, the background template, the flux and the
  normalization.
- **Restricted:** every classifier, the refinement classifier included, sees only the (E_avail, W) columns of the
  MC truth, the MC reco, the data and the background template.
- **Histogrammed in full:** the unfolded per-event weights are histogrammed on the full 5D fine grid, the cross
  section is extracted there (`xsec_nd.extract_cross_section_nd`, per-p_T-bin flux), and the result is projected to
  the 42 EW cells.
- **So L-EW is a direct 2D unfolding of (E_avail, W).** The unfolding never conditions on p_T, p_∥ or q₃. Its
  cross section is the same functional as RD3's.

### 2.4 Code

- **Location:** a new `nd-unfolding/pv-ladder/`, with copies only; no existing producer is edited.
- **The driver** wraps the s5 stack that RE-1 and s5p ran:
  - `s5c_unfold.load_inputs`;
  - `s5n_pseudo.build_data`;
  - `s5e_candidate.install("R")` for (e);
  - `s5p_numerics.unfold_one`;
  - `xsec_nd`.
- **What it adds:**
  - a dimension-generic cell reweight, replacing `s5n_pseudo.truth_weight`, whose maps assume 5D axis positions;
  - the copied `prior_inputs` with the completeness guard;
  - `--features` (all, or a named subset) for §2.3;
  - a noise-free closure mode (§3.2).
- **What it drops:** `s5p_universe.check_alignment`, which checks a 5D bank. The input sha256s replace it.
- **Tests:** numpy-only, run locally, written before the pilot. They cover the reweight on toy cells (edges,
  outside cells, the GiBUU p_∥ cut, k normalization), the completeness guard firing and staying silent, and the
  feature restriction leaving the histogramming columns untouched.

## 3. Controls (numeric rules)

### 3.1 Nominal control (NC), per rung and arm

| rung, arm | run | target | rule |
|---|---|---|---|
| L-3D (e) | the prior path at r = 1 | P3 `8bc7e2d3…` | max relative difference over the headline cells < **1e-5** |
| L-4D (e) | the same | P4 `2a18599f…` | < 1e-5 |
| L-EW (e) | the L-EW code with `--features all`, r = 1 | P5 (`k1_p5_rerun.npz` `e36f3b25…`) | < 1e-5 over the 39 EW cells and over the 109 J cells |
| L-EW (c) | the same, purity | P5c `1fa60dfc…` | < 1e-5, same cells |
| *L-5D-PV (e)* | the prior path at r = 1 | P5 | < 1e-5, same cells |

- **The tolerance is s5p's.** s5p's nominal-prior control differed from the CV path only through float64 weights,
  and it matched to < 1e-5, not bitwise (`RECORD-20260927-s5p-stage2-exit.md:105-107`). Bitwise equality is also
  reported.
- **L-EW's NC tests the code path,** not an EW central value, because no recorded one exists (D2). The full-feature
  run must reproduce P5, and P5c for (c), through every step the restricted run uses. Then the run with
  `--features eavail,W` at r = 1 is recorded as L-EW's central value E_EW, the zero of its shifts.
- **The NC runs are the pilot** (§5). No vertex run is submitted before every NC in the pilot passes.

### 3.2 Positive control (PC) at NuWro, per rung, arm (e)

- **Closure.** The noise-free, signal-only closure is PV-2D's. The pseudo-data are the MC's signal reco rows, with
  weights `w_reco` × r_NuWro and no background. They are unfolded with the nominal prior and the rung's estimator,
  with no template to subtract. The truth reference is the MC truth at `w_truth` × r_NuWro, through the rung's
  completeness.
  - bias = x_closure / x_true − 1 per headline cell;
  - the closure floor is the same closure at r = 1.
- **Rule** (`pv2d_lib.positive_control`, unchanged):
  - on the headline cells with |bias| > 1 %, if there are at least 20 of them,
  - the data shift at NuWro against −bias must have correlation ≥ **0.7** and slope in **[0.67, 1.5]**.
  - That is **PASS**. Fewer than 20 cells is **NOT_POWERED**, which triggers the ρ² fallback (r_NuWro squared,
    renormalized), run once with the same rule. Otherwise it is **FAIL**.
- **If a rung's PC does not pass,** its h is reported under the label "positive control not passed" and is not
  evidence, as the PV-2D binding requires.
- **The secondary cell sets are not graded:** the PC verdict is on the headline cells only. On the J-coarse cells
  the same statistic is reported, ungraded.
- **The (c) arm of L-EW has no PC of its own,** like PV-2D's refined arm. Its h is labelled so.

### 3.3 Integrity

Each product records:
- its input sha256s, the ratio file's sha256, the code sha256s, the estimator parameters as built (the s5 factory
  checks), the refinement evidence, and the completeness guard's value;
- the job id;
- the features used.

The analysis refuses on a mismatch, on the PV-2D model (`pv2d_analyze.py`).

## 4. Readouts

Per rung and arm, on the headline cells and on each secondary set:
- per vertex, the |shift| median, p90 and max, and the signed median;
- h = max_k |shift_k|: its median, p90 and max, and the dominant-vertex counts;
- the PC: n, correlation, slope and verdict, and the fraction of PC cells with |shift| ≥ |bias|, the PV-2D caveat
  statistic;
- the closure floor;
- the gate tiers per vertex, with cells and prior-weight shares.

**h/σ:**
- **L-EW:** against the note's adopted (E_avail, W) covariance, √diag(C_eavailW) / cv_marginal on the 39 cells.
  - It is the projection of the adopted Z-cv trunk `3d7465f6…`, as shipped in
    `docs/analysis-note/release-package-20260922/covariance_eavailW.npz` (`94679d6d…`).
  - **Named with its qualifications:** it is used under the 6.4 exception, its metadata records it as not passing
    (`sec_5d.tex:565-577`), and it belongs to the 5D-projection estimator, not to L-EW's.
- **L-3D and L-4D:** none. The note quotes no 3D or 4D uncertainty (`sec_3d.tex:331-334`, `:502-509`;
  `sec_method.tex:224-225`). h is reported relative only, and the readout says so. The 3D projection of the 5D
  covariance (`PROJ3D-20260922`, `adoptable = False`) is not used.

**The comparison table** sets h across L-EW, L-2D, L-3D, L-4D, L-5D (s5p) and, if bound, L-5D-PV. Each row gives the
cell set, the estimator, the vertex set and the PC verdict.
- **L-EW against 13.4 %:** the two use the same estimator, R = (e), and the same 39 cells. The **vertex sets
  differ:** s5p's D1–D5 against PV's three generator shapes. With L-5D-PV, the comparison L-EW against L-5D-PV on
  the 39 cells differs in the features alone.
- **3D and 4D against L-2D,** on the 205-cell projection: the same functional, with more conditioning variables.
- **The comparability limits** PV-2D's comparison names are restated: vertex sets, estimators, cell granularity and
  σ constructions.

## 5. Compute

- **Scale:** each unfold is one `srun` step at 42 CPUs, `--cpu-bind=cores`. Up to six run at once on one exclusive
  regular-QOS node, as RE-1's `re1-nd` did. That job made six data unfolds (5D, 4D and 3D) in 913 s and charged
  0.2536 node-h.
- **Closure runs** train step 1 on signal MC against signal MC. The data rows are replaced by about as many MC
  rows, so the cost per run is close to a data run.

| job | runs | projected | limit |
|---|---|---|---|
| **J1 pilot** (alone, first) | NC: L-3D, L-4D, L-EW (e) all-features, L-EW (c) all-features; and E_EW (e), E_EW (c) | 0.40 node-h | 0:38 |
| J2 | L-3D: 3 vertices, 2 closures; L-4D: NuWro | 0.40 | 0:38 |
| J3 | L-4D: GENIE+MEC, GiBUU, 2 closures; L-EW (e): NuWro, GiBUU | 0.40 | 0:38 |
| J4 | L-EW (e): GENIE+MEC, 2 closures; L-EW (c): 3 vertices | 0.40 | 0:38 |
| *J5, if D3 is bound* | L-5D-PV: NC, 3 vertices, 2 closures | 0.45 | 0:42 |
| fallback, only on NOT_POWERED | ρ² data run and closure per affected rung | 0.40 each | 0:38 |

- **The cap is 4.0 CPU node-h** in all: the jobs above with every fallback, and one rerun. That is under the
  assignment's 18.
- **The ratio builder** runs on a login node or a short debug job. It does no unfolding, and its time is ledgered
  anyway.
- **Stopping:**
  - I stop and report past 1.25× any job's projection.
  - The projections are revised from J1's measured time before J2 is submitted, and each revision is recorded
    with its reason.
  - I ask the director before exceeding the cap.
- **Storage:** `$PSCRATCH/pv-ladder-20261024/` only, with every job ledgered in `LEDGER.tsv` (`sacct` charge).
  Nothing goes to CFS.
- **QOS:** regular, each job under 12 h, never premium.

## 6. Deviations from the assignment, proposed for binding

- **D1. L-EW's estimator is (e), with (c) as a second arm, not (a).**
  - (a) on the 2D result is the ROOT driver's path, which keeps (p_T, p_∥) as features (`unfold_nd_omnifold_unbinned.py:5-9`,
    `:1035-1037`). No code path runs (a) on (E_avail, W) alone.
  - In the s5 stack, (e) is the 5D's own estimator (R), so with (e) L-EW differs from the 5D in features only. That
    is the separation Ben's question needs.
  - (c) differs from (a) only in LightGBM's determinism settings (the same 100/8, learning rate, seed and purity;
    `sec_method.tex:190-191`, `:243-254`), and it has a recorded target, P5c.
  - (a) itself in the s5 stack (`s5c_unfold`'s `production` configuration with purity) has no recorded ND target to
    control against. It is not proposed.
- **D2. L-EW has no recorded central value.** Its NC reproduces P5 (or P5c) through the full code path instead
  (§3.1), and E_EW is recorded here.
- **D3. L-5D-PV, optional.** It is a rerun of the 5D under PV's vertices, at about 0.45 node-h. Without it, L-EW
  can be compared with the 5D only across different vertex sets.
- **D4. Headline cells for 3D and 4D** are the support-rule cells, not all positive cells, with the J-coarse cells
  and the 205-cell projection as declared secondaries. Sparse fine cells carry the classifier's response to any
  reweight, and that is not resolved model dependence.

## 7. Asked of the director

1. Bind D1 to D4, or amend them.
2. Bind the control rules of §3 and the cap of §5 (4.0 CPU node-h, within the assignment's 18).
3. Confirm the h/σ denominator for L-EW (§4), or name another.

Then the code and its tests are committed, J1 runs alone, and every NC must pass before J2 to J4 are submitted.
