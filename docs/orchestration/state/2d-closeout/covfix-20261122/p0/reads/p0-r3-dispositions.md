# P0 code, read round 3: dispositions (cov2d, 2026-11-23)

Round 3 read `4cbb0fab3`. codex-school2 returned NO-GO with 5 blocking items. agy returned GO with no blocking items,
its third GO. Every item is accommodated below, or kept with its reason. The round 4 code's receipts are in
`../code-receipts/`:

- 95 tests OK;
- 100 % of lines and branches traced;
- 78/78 hand mutants killed, each by a named failing test. A run that also shows a discovery failure counts as a harness
  failure.

## codex-school2, blocking

1. **A carry refusal is scoped to its truth.** §2 says "or the carry refuses at that truth".
   - `carry_factor` now runs per tune inside its own handler. A refusal is recorded as `controls.carry_<T>`, and that
     tune's carried K0 and Q are neither formed nor C-PSD-checked. Its `carry_check` and `profiles.K0_carried` read
     "refused".
   - Everything else still runs: the other tune, C-PSD on the remaining blocks, A0, the C_T and G2R profiles, and c2.
   - C_run is now formed by REGRADE's formula exactly (`regrade_c_run`, as `regrade_crep.carry_frac`), with no COVFIX
     refusal on a zero numerator. A zero cell of x_T therefore still forms the regrade pair.
   - If x_T/x_R is not finite, the pair cannot be formed. The residual control and c2 at that tune are then recorded as
     "unavailable", not fired.
   - Tests:
     - a zero x_T cell at AR23: done, AR23's carry refused, G18 intact, the residual still formed;
     - a zero x_R cell: both pairs unavailable;
     - the helper directly.
2. **The tied-space null test is now relative to the projection.**
   - A projection that is exactly zero is skipped.
   - Otherwise, e_j is null only if orthogonalisation leaves at most GS_NULL = 100 ε of its own norm, meaning it lies in
     the span already built, to roundoff. A small but genuine projection is kept in its order.
   - Tests:
     - a 1e-15 first projection;
     - a three-dimensional tie where a 1e-13 relative residual decides the order. This kills both a fixed absolute
       threshold and an n-scaled one.
     - an exactly repeated row, which stays finite and orthonormal;
     - the codex fixture through `eig_basis`, asserting the tied rank order whenever numpy returns an exact tie.
   - This is a convention for exact floating-point ties only. The record prints `exact_tie_groups_kept` for every
     reading, so it shows whether the convention touched the real data at all.
3. **λ₁ comes from the grading routine.** `lambda_1` now uses `np.linalg.eigh`, the routine `eig_basis` grades with. When
   V is V_F, the cut's reference is therefore bitwise the graded λ₁. The test is codex's non-diagonal fixture: a block
   with exact largest eigenvalue 16 and a mode at 1.6e-11.
4. **A0's order and zero reference.**
   - `a0_control` now establishes the positive grading spectrum (`a0_tol`, a STOP) before it calls the grader. A test
     makes the grader raise, and still gets the named A0 STOP.
   - A committed value of exactly zero is matched only by zero: rel 0 or ∞, with no division. A test covers both.
5. **The digest is of the bytes consumed.** `read_pinned` reads each input once, checks the sha256 of those bytes and
   returns them. `load_npz` and `json.loads` parse the same buffer. A test replaces every input file on disk right after
   its check: the run completes on the checked bytes, and each input is read exactly once.

## codex-school2, non-blocking

1. **Excluded ranks cannot move max_d.** A test injects garbage on the ranks whose tie partitions differ and asserts
   that max_d is unchanged. The projector comparison over an enclosing interval is not added: the unmatched ranks are
   listed and given no d_k, which is the descriptive diagnostic §8 asks for. `ndf_evr` 0 is reported only for an
   actual evr refusal.
2. **More independent oracles.**
   - A three-toy spread oracle with a positive SE.
   - A0 at literal scores: rows (2, 1) and (0, 1) under diag(4, 1) give 0.75, tested at 1 + 5e-10 (pass) and 1 + 2e-9
     (STOP) against the 1e-9 floor.
   - Every guard now carries `"coverage": "approximate for quadratic toy scores (section 2)"` in the JSON.
3. **Inputs and empty readings.**
   - IBUKT's E_R arm must be a one-dimensional vector aligned with Q's cells. A column array, or a missing arm, is a
     C-MAP STOP; tests cover both.
   - An empty K0 basis gives IBUKT an explicit local "refused".
   - The G2R frame comparisons are exercised by `g2r_map_off`.
4. **Receipts.**
   - The G2R digests' producer lines are in round 2's dispositions, item NB3.
   - The harness now classifies any run that shows a discovery or `_FailedTest` failure as a harness failure, even if it
     also shows a named failure.
5. **Audit clarity.**
   - The residual rule now takes the exact `C_T + C_run` and `F_T + C_run` arrays that C-PSD checked.
   - The cut diagnostic prints `outside_span_threshold`.

## agy (GO), non-blocking

All three items are kept, as in rounds 1 and 2:

- the G2R literals are the declared values;
- A0 and C-MAP are input validity under ST5;
- exclusive creation protects a committed record.
