# Assignment: the 2D prior-variation (model-dependence) test (2026-10-23)

**Assigned by** the paper-tighten lane, as director. **Assigned to** the session "2d test", which offered.

## Why

Joseph, 2026-10-23, verbatim:

> can you run the  prior-variation test on the 2D (p_T, p_∥) result? It has never been done. The 2D record has only knob-sized closure tests (2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:167-172), and docs/orchestration/state/uncertainty-preparation-20261008/c/components.tsv C09 says model dependence is in no 2D construction. An agent named 2d test will contact you offering to do this work. Give it this piece with the spec below, and fold its result into your report. You own the comparison between 2D and 5D.

The text plus a final newline has sha256 beginning `c4be658e12829acf`.

**The director's re-measurements on `origin/main`:**
- **The closure passage.** On main it is at `2D_OMNIFOLD_STUDY_STATUS.md:192-210`; lines 167-172 there are about the flux
  residual. Cite the passage where you find it.
- **C09.** `components.tsv` C09 reads "none in the adopted construction".
- **The quoted 2D central value** is `E_U`:
  - file: `2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`, sha256 `4f5a1b6d…`;
  - estimator: configuration (a), LightGBM with 100 trees and 8 leaves, learning rate 0.1, `--seed 42`, purity
    subtraction, five iterations;
  - launcher: `2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh`;
  - source: `docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md:18-22`.
- **The 2D result is moving.** RE-2 (re-1 lane; `re2/RE2-PLAN.md`) will move the adopted 2D result to the refined
  estimator (DECISION-20261023 second). Run this test on `E_U`'s estimator, as the spec says, and name it. If the
  refined arm can be added cheaply on the same vertices, propose it in your declaration, as an option.

## Spec (Joseph's, with the director's operational additions marked ◆)

- **Test.** Unfold the real 2D data with the MC prior reweighted to each generator vertex.
  - Follow the s5p design in `docs/orchestration/state/s5p/contract-amendment-3-stage2-supplement.json`: multiply
    `w_truth` and `w_reco` of every MC row by r(truth).
  - Watch for the denominator defect that s5p hit and repaired (`RECORD-20260927-s5p-stage2-exit.md` §1–2).
  - Use the estimator of the quoted 2D central value, and say which one it is.
  - ◆ Define r on the 2D truth binning you use, including the under- and overflow handling. State that composition
    below the 2D binning stays Tune v1's.
- **Vertices.** Project the flux-repaired generator predictions in `3d-unfolding/genie/gen5d_*` onto the 205 reported
  bins.
  - Use GENIE+MEC, NuWro, GiBUU and Tune v1, as available.
  - Carry the GiBUU E_ν > 20 GeV gap (KNOWN_ISSUES 82) and the flux caveat (KNOWN_ISSUES 83).
  - ◆ Record each projected prediction's source file and sha256, and the projection code.
- **Controls.**
  - **The nominal control.** A run at the nominal prior must reproduce the central value; s5p got below 1e-5
    relative.
  - **The positive control.** Show that the test can see a bias, for example by checking one vertex against the
    closure bias on pseudo-data. A null result without a positive control does not count.
  - ◆ Fix each control's pass rule, numerically, in your declaration before any output.
- **Report.**
  - For each vertex: the shift per bin (median, 90th percentile and maximum).
  - The envelope h = max over vertices of |shift|.
  - The comparison of h with σ_tot (median 6.87 %) and with the published per-bin uncertainties.
  - ◆ **Compare against the adopted σ_tot, not 6.87 %.** The director re-measured: the adopted Q = S5 + C_PL has a
    per-cell median of **6.45 %** (p84 9.18 %, max 23.6 %; `docs/analysis-note/values.tex:140`,
    `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:45`). The 6.87 % in the request is the superseded VL172 value
    6.8707 (`values.tex:143`). Report against 6.45 %, and add 6.87 % as a secondary reference if useful. State amendment 6's caveat
    (`state/s5p/contract-amendment-6-review1-repairs.json`, `LOW_items.bound_wording`): in 5D, |shift| ≥ |bias| held
    in only 52–78 % of cells, so h is evidence about model dependence, not a per-cell bias bound. If the positive
    control measures the 2D analogue, report it.
- **Budget.** Expected to be a few CPU node-h.
  - The CPU pool is nearly exhausted: check with the director before exceeding about 20.
  - ◆ The grant is at most 20 CPU node-h under the 2D closeout delegation
    (`AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2), regular or debug QOS, each job under 12 h.
    Today's units run about 1.4× slower than their September records (`state/gpu-timing-20261023/REPORT.md`), so
    size limits from a measured pilot.

## How the work runs (◆)

1. **Read.** `docs/orchestration/state/2d-closeout/stageF/lanes/COMMON-RULES.md` binds; read it first. Then read
   `AGENTS.md`.
2. **Declare before any output.** Commit `DECLARATION.md` in this directory, with:
   - the code shas and inputs with sha256;
   - the vertex projections;
   - the controls with their numeric pass rules;
   - the readouts;
   - the compute cap.

   Open a PR and message the director. The director binds it before any job runs.
3. **Files.**
   - Records go under `docs/orchestration/state/2d-closeout/stageF/methods/pv2d/`.
   - New code goes under a new `2d-unfolding/pv2d/`. Copy and extend existing producers; do not edit them.
   - Outputs go to `$PSCRATCH` (pscratch is 85 % full, so keep the footprint small). Nothing goes to CFS.
   - Do not touch the re-1 lane's `re1/`, `re2/` or `2d-unfolding/re1/` files, or `docs/analysis-note/`.
4. **Report.** Write `REPORT.md` here, with the numbers, the controls' outcomes, what was not done and the deviations.
   Have it independently reviewed in both directions. Open a PR; CI runs the record checks. The director merges it and
   writes the 2D-versus-5D comparison.

No claim change and no outward act.
