# P0 code, read round 1: dispositions (cov2d, 2026-11-23)

Round 1 read commit `b2f30dc1b`'s code. codex-school2 returned NO-GO with 8 blocking items. agy returned GO with no
blocking items. Every item was accommodated, or is kept with the reason given. The round 2 code is in the next commit;
its receipts are in `../code-receipts/`:
- 61 tests OK;
- 100 % of lines and branches traced;
- 58/58 hand mutants killed, each by a named failing test.

## codex-school2, blocking

1. **C-PSD on every block.** `psd_all` now checks all 31 blocks P0 uses or forms, and any failure STOPs. The 31 are:
   - the 9 reference-frame blocks;
   - per tune: C_T, C_model_abs(T), F_T, C_T′, G2R's C_model_abs, F_T′, carried K0, carried Q, C_run(T), C_T + C_run
     and F_T + C_run.

   The stop message names each failing block with λ_min and λ_max. Tests cover a G2R block and a derived F_T.
2. **The residual rule stops before the readings.** It is now stage 3, after the controls. If it fires at either tune,
   P0 STOPs with the residual and the director routing, and no carry check, profile, c2 or IBUKT reading is computed.
   The test asserts that those sections are absent.
3. **The W1 vector.** The `--xhat-round` input is removed. The record is P0's pre-W1 part, with status `done (pre-W1
   part)`, and every second-vector reading says "pending W1". The completing step's input contract is written with the
   W1 code: the W1 receipt, its aligned digest, §2's per-cell rounding check with the 1e-3 refusal, and the
   zero-denominator count.
4. **Dropped bands.** `mode_readings` emits Q_R, F_R, B_R and the guard for used bands only. A dropped band carries only
   its count and the name of why it was dropped.

   The eigenvalue ratio documents its pairing: common rank, banded by C_T's kept spectrum. A band with fewer than 10
   common ranks is dropped and named. The per-rank ratios are kept.

   Tests cover 9 versus 10 modes and a near-tie cluster at a band edge, including a chained cluster.
5. **Gram–Schmidt and evr.**
   - The null threshold is now 10·n·ε, the roundoff scale of unit vectors, with two orthogonalisation passes. A test
     uses a genuine 1e-11 projection and keeps it first, in order.
   - The evr comparison now runs the same readings through `eig_basis(driver="evr")`, with the same tie
     canonicalisation and sign rule. In a test, an exactly tied 3-dimensional space agrees to 1e-12.
6. **Named modes.**
   - `residual_rule` lists each tail mode with its rank, λ and residual.
   - `cut_diagnostic` emits both kept spectra and lists each reference kept mode outside the new kept span, with its
     rank, λ and residual.
7. **IBUKT and c2.**
   - IBUKT emits m_i only.
   - c2 uses the declared rank-two block's top two directions whatever their size. A test uses a 1e-14 second
     eigenvalue.
   - c2 prints the third-to-first eigenvalue ratio.
   - A zero mean error gives `share_of_ebar2` null. A test covers this.
8. **Strict JSON and edge cases.**
   - `jsonable` writes every non-finite value as null, under `allow_nan=False`.
   - A refused guard carries null X and SE where they are non-finite.
   - A reading with no kept mode is refused, so the angles never see an empty span. The unreachable empty branch was
     removed.
   - An evr rank with b + f = 0 is counted, not divided.

## codex-school2, non-blocking

1. The wording is now "exact numerical equality (np.array_equal), summed in the declared order". Each identity is
   falsified separately in the tests (`break_q`, `break_s5`).
2. The G2R `rep` mask is now checked against COV2D's, and G2R's path and sha256 are recorded in `inputs`. A missing
   input is a C-PIN STOP.

   The map's rationale is in `cell_map`'s docstring: every reading pairs cells across the three files and carries by
   x_T/x_R.
3. **One representation.** Every COVFIX computation uses the symmetric part (C + Cᵀ)/2: C-PSD, the cut, the readings,
   λ₁ and the residual rule. The raw asymmetry is printed. A test checks that the matrix graded is the matrix checked.

   A0 keeps COV2D's legacy path (`chi2_nonnull` on the raw C_T), as COV2D and REGRADE graded.
4. **Kept as is.** A0's form is REGRADE amendment 1's, already tested there. The fixture tests a 1 % mismatch and an
   ndf mismatch.
5. Added:
   - a hand-calculated b/z/m/v/q oracle;
   - exact equality at the well-determined cut;
   - the chained near-tie fixture;
   - an explicit `OUTSIDE_SPAN = 1e-6` (REGRADE's convention);
   - the evr threshold, recorded in the output;
   - the mutation harness now prints the failing test that killed each mutant.

   An exact-equality case at the 0.1 residual bar was not added: exact 0.1 is not constructible in floating point. The
   strict-inequality mutant is therefore equivalent at measure zero, and the bar is tested at 0.0999.
6. The production pin audit is now its own file, `test_covfix_p0_pins.py`. The driver suite is synthetic only.

## codex-school2, interpretations

- (1) The convention text now says "an E_R-scaled residual … equal to the absolute error only where x_R equals the
  truth".
- (6) Changed, as item 5 above.
- (2)–(5), (7) and (8) agreed.

## agy (GO), non-blocking

1. **The A0 stop.** Kept. §8 requires A0 in every readout, and codex-school2 notes that A0 is terminal under ST5.
2. **The C-MAP and IBUKT cell stops.** Kept. A misaligned cell order or frame makes every paired reading invalid, so
   the stop is an input-validity condition, not a reading bar.
3. **The `--out`-exists refusal.** Kept. It protects a committed record from overwrite and produces no reading.
