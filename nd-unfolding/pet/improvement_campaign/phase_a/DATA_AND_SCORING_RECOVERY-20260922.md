# Data and Scoring Recovery (Part 1 & 2)

## Part 2: Data Path Verification

Evaluated against `G2_FPS_MEFHC_P12.npz` (sha: `fa6b3463...`) and the built comparison inputs:

*   **Event identity and join integrity**: PASS. `join_sig.npz` contains a `row_index` mapping of size `49,152,885`, exactly matching the length of `pass_reco` in `G2_FPS_MEFHC_P12.npz`, ensuring a perfect row-for-row alignment between the extractor's output and the canonical inventory.
*   **Dual-leg (reco/truth) weights**: PASS. `G2_FPS_MEFHC_P12.npz` carries both `w_reco` and `w_truth` explicitly.
*   **Pseudodata construction (tilt, clipped at 3.0)**: PASS. The E_avail tilt is NOT baked into the source data. It is constructed dynamically during the closure evaluation (`cp.clipped_exponential_tilt`) using a truth E_avail coordinate ceiling of 3.0 GeV and amplitude 0.35. The resulting tilt weights are stored verbatim as `tilt_a` in each run's weights artifact.
*   **Selection flags**: PASS. Both `pass_reco` and `pass_truth` exist as boolean arrays (sizes ~20.5M and ~49.1M out of 49.15M), enabling correct fake and miss handling without destructively dropping rows.
*   **Masks/padding**: PASS. Extracted tokens are zero-padded to a uniform `cap` block shape `np.zeros((cap, TOKEN_WIDTH), dtype=np.float32)` in `build_theirs_inputs.py`.
*   **Feature units**: PASS. Token inputs pass raw kinematic scales (momentum in GeV/c, log of energy). Global scalar summaries explicitly log-transform variables like `np.log(hadron_recoil + 1e-5)`.
*   **Split isolation (halves disjoint)**: PASS. Verified experimentally that `rows_a` (600,143 indices) and `rows_b` (600,143 indices) in the `final` artifacts have exactly 0 overlapping rows, proving the evaluation strictly enforces identity-disjoint populations.
