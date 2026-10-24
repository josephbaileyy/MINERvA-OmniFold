# Assignment: the prior-variation dimension ladder, and the 2D model-dependence covariance (2026-10-24)

**Assigned by** the paper-tighten lane, as director. **Assigned to** the session "2d test", which ran PV-2D
(`state/2d-closeout/stageF/methods/pv2d/`).

## Why

- **Ben's questions** reached the director through Joseph, 2026-10-24. Ben asked "What does it look like if you study
  closure in 2D for E_avail and W? Is it that those two are especially bad or somehow the correlations are hard in
  5D?", and "let's see the maximal phase space we can probe that we understand and for which the methods seem to
  work!".
- **What is on record:**
  - the 2D (p_T, p_∥) envelope h has a median of 3.1 % (PV-2D);
  - the 5D envelope h is 9.6–13.4 % (s5p stage 2 §4). The 13.4 % for EW is the (E_avail, W) projection of the 5D
    unfold, not a direct 2D unfolding.
  - so nothing separates "E_avail and W are poorly resolved" from "the 5D correlations are hard".
- **Joseph's answer**, verbatim:

  > yes start the ladder, do you want me to open up a new session for that?

  The text plus a final newline has sha256 beginning `4c6dd8a33c5e69c3`. The director answered that no new session is needed:
  this lane has the machinery.

## Part 1: the ladder

**The test.** Run PV-2D's test unchanged at each rung: the same prior-variation construction, vertices, noise gate,
controls and readouts (`pv2d/BINDING.md`).
- The vertices are GENIE+MEC, NuWro and GiBUU, taken as shapes relative to GENIE CV on the Tune v1 prior.
- Each rung carries its own nominal control, which must reproduce that rung's recorded central value, and its own
  positive control at NuWro, with the declared rule.

| rung | observables | estimator | status |
|---|---|---|---|
| L-EW | 2D (E_avail, W), **unfolded directly** | configuration (a), as the 2D (p_T, p_∥) result; name the code path (e.g. the ND driver's `--axes`) and cells | **new**: Ben's question |
| L-2D | 2D (p_T, p_∥) | (a) and refined | done (PV-2D); reused |
| L-3D | (p_T, p_∥, E_avail) | configuration (e) (RE-1's P3) | new |
| L-4D | (p_T, p_∥, E_avail, q₃) | configuration (e) (RE-1's P4) | new |
| L-5D | all five | R = (e) | on record (s5p); reused, not rerun |

**Readouts at each rung:**
- per vertex, the |shift| median, p90 and max;
- h, and h/σ against that rung's own quoted uncertainty, where one exists.
- 3D and 4D have no validated covariance. Use what the note quotes for them, name it, and say where none exists.

**The comparison table** sets h across the rungs, and states the comparability limits PV-2D's comparison names. For L-EW,
also compare its h with the 5D EW projection's 13.4 %. That isolates "variables" from "correlations".

**Declare before any output:**
- the cells and binning of each rung, including L-EW's (E_avail, W) binning and how it relates to the note's EW cells;
- the numeric pass rules for the controls;
- the compute cap.

## Part 2: C_model,2D

Under `DECISION-20261024-joseph-2d-model-dependence-component.md`, build the 2D model-dependence covariance from PV-2D's
refined-arm products. It costs 0 node-h.
- **Form:** C_model = Σ_k s_k s_kᵀ (M2, κ = 1), with s_k the refined arm's per-cell shift for vertex k.
- **Products:** the matrix, its sqrt-diagonal per cell, and Q + C_model's per-cell total.
  - Q's per-cell total should reproduce the director's median of 7.69 % in quadrature (`pv2d/COMPARISON-2D-5D.md`).
  - State the matrix's rank, which is at most 3.
- **Label:** "generator-shape model dependence; not a calibrated bound", with the noise-gate tail caveat.
- **After RE-2:** Q_R replaces Q when RE-2 lands, and the director integrates both.

## Compute and rules

- **Cap:** at most **18 CPU node-h** under the measurement phase-1 grant (`BINDING-PHASE1-20261019.md:53`).
  - 35 are granted. About 13.2 are charged or reserved: the ledgers sum to 11.86, and R10 has a worst case of 1.36.
  - Regular QOS, each job under 12 h. Pilot first.
  - Stop and report past 1.25×; ask the director before exceeding the cap.
- **Storage:** `$PSCRATCH` only, with every job ledgered.
- **Files:**
  - records go under `docs/orchestration/state/measurement-scoping/pv-ladder/`;
  - code goes under a new `nd-unfolding/pv-ladder/` (copy; do not edit existing producers);
  - the C_model products go under `pv2d/cmodel/`.
- **Do not touch:** `re1/`, `re2/`, `r10/` or `docs/analysis-note/`.
- **Process:** declare, the director binds, run, then REPORT.md with an independent review and a PR.
  - Run `bash .githooks/pre-commit` and `python3 tools/registry/absence_claims.py --base origin/main` before pushing.
  - No `git stash`.
