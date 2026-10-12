# Paper-covariance χ² of XR's reseeded exact-split run (2026-10-12)

- **What was run.** `2d-unfolding/compare_to_paper_fullcov.py`, from a clean clone at `40641efd` on saul,
  with the deployed `2d-unfolding/` as the working directory (its `minerva_paper_anc/` inputs). Two invocations:
  - `--ours XR-X1.root`, the seeded exact-split run (`random_state` 1/2/3);
  - `--ours XR-X0.root`, the unseeded control.
  There was no `--omnifold-cov`, so these are the published-covariance χ² and pulls.
- **Inputs.** Both files are read-only XR outputs at `/global/cfs/cdirs/m3246/josephrb/xr-linux-20261011/outputs/`.
  Their sha256 values are in `SHA256SUMS` and equal XR's receipts.
- **Result.** X1 gives 3.565 (pulls 0.087/0.596). The X0 control gives 3.661 (0.089/0.598), equal to the
  exact-split E_C value it regenerates.
- **Scope.** One seed triple; not a seed spread. Ledger row VL174.
