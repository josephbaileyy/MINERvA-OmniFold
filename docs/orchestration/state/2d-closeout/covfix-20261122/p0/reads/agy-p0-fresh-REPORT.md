BLOCKING:
None.

NON-BLOCKING:
1. [covfix_core.py:101](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-p0-fresh/covfix_core.py#L101), Section 5.2.
   The canonical basis construction for tied eigenspaces uses `GS_NULL = 100.0 * EPS` to identify and skip null projections in Gram–Schmidt (`nc > GS_NULL * n0`). For an adversarial input with an extremely small but nonzero projection relative norm $\le 100\epsilon \approx 2.22 \times 10^{-14}$, the direction would be skipped. On real physical inputs on 205 aligned cells, genuine projections of coordinate axes into degenerate eigenspaces cannot fall in this gap without being machine roundoff.
   *Fix:* If a strictly zero-only cut is desired regardless of cancellation roundoff, change line 121 to `if nc > 0.0:` or expose `GS_NULL` as a configurable parameter, though the current $100\epsilon$ threshold is standard numerical practice for modified Gram–Schmidt with re-orthogonalization.

2. [covfix_core.py:38](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-p0-fresh/covfix_core.py#L38), Section 5.2.
   `cut_diagnostic` classifies reference kept modes as "outside" the new kept span using `OUTSIDE_SPAN = 1e-6` (`res > OUTSIDE_SPAN`). Section 5.2 requires printing the reference kept modes outside the new kept span and their maximum residual, but does not define an explicit numerical threshold for the discrete indicator. The code follows REGRADE's convention and also reports continuous residuals and `max_residual_of_ref_kept_modes`.
   *Fix:* If all nonzero residuals should be flagged without an arbitrary cutoff, set `OUTSIDE_SPAN = 0.0`, or document `outside_span_threshold` in the output JSON schema.

3. [covfix_p0.py:270](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-p0-fresh/covfix_p0.py#L270), Section 3.1.
   `c2` computes projections of T2A's mean error onto $C_{\text{PL}}$'s top two eigenvectors both carried to the tune frame (`carried_to_tune`) and in the uncarried reference frame (`uncarried_read_by_nothing`). Section 3.1 states "c2 as scoped: T2A's mean error projected on C_PL's two directions" without explicitly specifying whether the directions are carried by $D_T = \text{diag}(\hat{x}_T / x_R)$. Both are calculated, and the uncarried direction is clearly labeled as read by nothing.
   *Fix:* If only the tune-carried projection is intended by the declaration, remove the `("uncarried_read_by_nothing", C_PL)` iteration in `c2()`.

4. [covfix_core.py:80-90](file:///private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/agy-p0-fresh/covfix_core.py#L80-L90), Section 3.1 / Section 6.2.
   `psd_check` computes relative asymmetry `asymmetry_rel = np.max(np.abs(C - C.T)) / scale` and prints it, but bars only on the symmetric part's minimum eigenvalue $\lambda_{\min} \ge -10^{-12} \lambda_{\max}$. Section 3.1 specifies only "C-PSD on every block: $\lambda_{\min} \ge -10^{-12} \lambda_{\max}$" and specifies no matrix asymmetry tolerance (unlike REGRADE's `SYM_TOL = 1e-12`).
   *Fix:* If a strict symmetry bar matching REGRADE is desired, add `and rec["asymmetry_rel"] <= 1e-12` to `rec["pass"]` on line 89.

VERDICT: GO
