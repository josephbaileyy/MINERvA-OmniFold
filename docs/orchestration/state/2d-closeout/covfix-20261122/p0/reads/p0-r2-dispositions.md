# P0 code, read round 2: dispositions (cov2d, 2026-11-23)

Round 2 read `207e20c7f`. codex-school2 returned NO-GO (7 blocking, 5 non-blocking, and several round 1 items NOT
RESOLVED). agy returned GO with no blocking items. Every item is accommodated below, or kept with its reason. The round 3
code is in the next commit. Its receipts are in `../code-receipts/`:
- 80 tests OK;
- 100 % of lines and branches traced;
- 69/69 hand mutants killed, each by a named failing test. The harness now refuses to count an import or crash failure
  as a kill.

## codex-school2, blocking (B) and the round 1 items it reopened

1. **C-PSD (B1; r1 B1).**
   - The rebuilt tune model block `C_model_abs rebuilt(T)` = diag(x_T) C_model diag(x_T) is now formed once and
     checked, so C-PSD covers 33 blocks.
   - C-PSD now runs before A0, so a C_T that would fail both reports the named C-PSD failure. A test sets `nonpsd` and
     `a0_off` together.
   - The blocks-versus-rebuilt discrepancy compares symmetric parts, after C-PSD, reusing the checked arrays.
2. **Angles and the below-well list (B2; r1 B6).**
   - The record now prints both angles, with their spans named:
     - `directed_angle_deg`, arcsin of the residual: from the reference's well-determined span to the new kept span;
     - `well_spans_max_angle_deg`: between the two well-determined spans. This is §3.1's "maximum principal angle
       between the well-determined spans".
   - The directed residual stays the sole trigger.
   - Codex's example is a test: C = diag(1, 1e-7) with C_run = diag(0, 1e8). The directed angle is 0°, so the rule
     does not fire, while the well-determined spans are 90° apart.
   - `below_well_modes` now lists every reference mode below the well-determined cut, including those the reference
     itself drops, with rank, λ, residual and `ref_kept`.
   - The STOP message prints residuals by `repr` (full precision).
3. **Tie canonicalisation (B3; r1 B5, interp. 6).** Gram–Schmidt now runs in span(U)'s own coordinates. Each projected
   axis is U c_j with c_j = U[j, :], so an accepted vector is U times an orthonormal k-vector and cannot leave the span.
   The null test is a fixed GS_NULL = 100 ε on the unit scale; it is no longer scaled by n. New tests:
   - a genuine 1e-13 first projection in 205 cells is kept first;
   - nearly dependent rows (1e-9) stay orthonormal and inside the span to 1e-13.
4. **evr partitions (B4; r1 B5).** The comparison now finds each driver's exact-tie groups (`tie_groups`). A rank in a
   group the other driver does not reproduce is listed in `partition_differs_ranks` and given no d_k. A test injects a
   tie that one driver lacks.
5. **The spread guard (B5).**
   - `mode_readings` prints the guard for the total spread F = mean v_i and for each used band's F_R
     (`guard_F_R`). Each uses §2's delta-method influence term ψ_s = (1/ndf_R) Σ_i [(z_{s,i} − m_i)² − v_i], with X =
     the spread itself.
   - These guards carry no label, because only a normalised spread (F̃) is labelled, and F̃ needs V₊, which is outside
     P0.
   - Tests: a hand-calculated SE, and a zero-SE refusal.
   - The guard docstring states that the interval is approximate for quadratic scores, as §2 does.
6. **Scoped refusal (B6; r1 B8).**
   - A declared refusal inside one carry comparison or profile is now recorded for that reading only (`scoped`), and P0
     continues. A test uses a zero G2R covariance, which passes C-PSD and has no kept mode.
   - A refused evr reading is a diagnostic (`ndf_evr` 0 plus a note), not a stop. A test covers this.
7. **Input controls (B7; r1 NB2, interp. 8; agy r1 NB2).**
   - The G2R x_R and x_T equalities are no longer STOPs. They are printed under "printed, not barred", because G2R's
     frame vectors enter no reading: its profile uses C_T′ and its C_model_abs only.
   - What remains as STOPs is what the readings depend on:
     - the cell order: Q's cells against COV2D's reported cells, and G2R's rep against COV2D's rep;
     - Q's x against COV2D's x_R, since the carry divides COV2D's x_T by it.
   - IBUKT's pin, cell order and arm length now run in preflight (`ibukt_load`), before any control. A provenance STOP
     therefore cannot leave partial readings. A test checks that C-PSD is absent after an IBUKT STOP.

## codex-school2, non-blocking

1. **A0 (r1 NB4).**
   - κ now comes from the same `np.linalg.eigh` spectrum that `chi2_nonnull` grades with, so the kept set is the
     grader's.
   - REGRADE's no-positive-eigenvalue refusal is restored.
   - New tests with an independent committed value: the floor branch (1e-9), the κ branch (κ = 1e9, giving 10κε), a
     mode under the cut excluded from κ, scores at 0.5 tol (pass) and 2 tol (STOP), and the no-positive refusal.
2. **Boundaries at the public readers (r1 B4, r1 NB5).**
   - The carry ratio is tested at 9 and 10 common ranks and with a straddling near-tie at the R1/R2 edge.
   - Codex's exact-0.1 construction computes a residual of exactly 0.1 and does not fire, and the `>=` mutant is now
     killed.
   - The hand oracle asserts z explicitly. The 1/N covariance S_t is not formed in P0; the spread v_i is its diagonal
     in the mode basis and is asserted.
3. **Artifact semantics.** Kept, with the evidence named here:
   - `blocks_<T>["x_T"]` and `["x_R"]` are the vectors REGRADE's C-MAP used to carry C_PL (`regrade_crep.py:266–277`).
   - Q_rep's `x` is E_R's reported spectrum at the data, since Q_rep is COV2D-G2R's rebuild there (declaration §2).
   - The G2R digests are the ones listed in `receipts-cov2d/g2r/readout/<T>/README.md:32` and `out.sha256.txt:1`. The
     pin test repeats them as the declared values, and the receipt lines are their source.
4. **The mutation harness (r1 NB5).** A non-zero exit that names no failing test, including unittest's `_FailedTest`
   import errors, is now classified as HARNESS FAILURE and not counted as a kill.
5. **Exclusive creation.** The record is written with `open(out, "x")`. A writer that lands first makes this run return
   2 without overwriting; a test simulates the race. The earlier existence pre-check was redundant with this, and its
   mutant survived, so it was removed.

## codex-school2, interpretation 1 (production mapping x → E_R)

Q_rep's `x` equals COV2D's `x_R` bitwise (C-MAP), which is E_R's data spectrum. The record states that the IBUKT
vector is an E_R-scaled residual.

## agy (GO), non-blocking

Both items were kept, as in round 1. A0 is terminal under ST5, and the cell-map STOPs are input validity. The
`--out` protection is now exclusive creation.
