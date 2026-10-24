# PV-ladder binding (2026-10-24)

**By** the paper-tighten lane, as director. **Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #311
(`ec0f7ad7`; the file's sha256 begins `532e3efc2917de96`). The declaration's commit is `c72a950c`.
It runs under [`ASSIGNMENT.md`](ASSIGNMENT.md) (PR #306).

## Rulings on D1–D4 and the denominator

- **D1, L-EW's estimator: accepted.** Configuration (e) is the headline arm, with (c) as a second arm. No code path runs
  (a) on (E_avail, W) alone. (c) differs from (a) only in LightGBM's determinism settings and has a recorded target,
  P5c. Using (e) also matches the 3D and 4D rungs.
- **D2, L-EW's nominal control: accepted.** The same code run with `--features all` must reproduce P5 and P5c to
  < 1e-5 relative, with bitwise equality reported. This tests the code path; the EW-only run has no recorded target of
  its own.
- **D3, L-5D-PV: admitted.** This is the 5D unfold under PV's three vertices, at about 0.45 node-h.
  - L-EW against L-5D-PV on the 39 RD3 cells differs in the features alone. That is the controlled answer to Ben's
    question, "variables or correlations".
  - The comparison with s5p's 13.4 % (D1–D5) is reported as secondary, with its vertex-set caveat.
- **D4, headline cells: accepted.** The 3D and 4D headline cells are s5p's support-rule cells. The J-coarse cells and
  the 205-cell (p_T, p_∥) projection are declared secondary readouts.
- **The denominator for L-EW's h/σ: accepted.** It is C_eavailW, the note's adopted EW projection, named with its
  6.4-exception qualifications. 3D and 4D report relative h only, because the note quotes no uncertainty for them.

## Before any job (pre-bound)

1. Commit the pv-ladder code and its tests in `nd-unfolding/pv-ladder/`.
2. Record `RUN.md` here: the code commit sha, the sha256 of every script, the exact sbatch commands and the pilot's
   projection.
3. Tell the director. If `RUN.md` matches this binding and the declaration, submit the pilot, with all the nominal
   controls, first and alone.
4. Rungs are submitted only after their own nominal control passes.

## Compute

- **Cap:** at most **4.0 CPU node-h** as declared, inside the assignment's 18, under the measurement phase-1 grant.
- Regular QOS, each job under 12 h.
- Stop and report past 1.25× a job's projection.
- `$PSCRATCH` only, and every job is ledgered.
- **The report:** a defect found after output comes to the director before any re-read. The report sets h across the
  rungs, against PV-2D and the 5D record, and states the comparability limits.
