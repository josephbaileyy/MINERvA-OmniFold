# DECISION 2026-10-11 — quote the LightGBM 2D central value (seed 42)

**Ruling (Joseph, 2026-10-11, in session):** "switch to the LightGBM central value as I see theres no
reason not to". This was in reply to the improvement list, which put the choice to him: switch the headline
2D central value to LightGBM, or keep exact-split and quote the spread between learners.

**What it supersedes.** The interim disposition of `KNOWN_ISSUES.md` 88 (Joseph, 2026-10-09: "keep and
disclose") listed "a LightGBM re-quote" as not authorized. This ruling authorizes that re-quote. Nothing
else listed there is authorized by it: no transfer measurement, N2 or KI-85 lift, no gate change, and no
terminal campaign reopened.

## The product

The quoted 2D central value becomes the LightGBM matched central value of the systematic-universe sweep:

| field | value |
|---|---|
| file | `2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` (pscratch; CFS copies, same hash, under `m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/uq/`) |
| sha256 | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` |
| estimator | LightGBM, 100 trees, 8 leaves, learning rate 0.1, `--seed 42`, purity subtraction, five iterations |
| launcher | `2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh` |
| reproduction | equals the July CV (`uq/purity_newomni/…_pn_uni_CV.root`, a different file, driver and thread count) to 1.4e-11 (`two-d-path/REPORT.md` §3.2) |

**Why seed 42 (the lane's choice; the ruling names no seed).**
- It is the systematic sweep's matched CV (same estimator and seed). It is not the universes' zero point: KI 93, a different truth input, which cancels to first order in the mean-centred band variance.
- It is the denominator of the printed 6.87% budget, so that number becomes self-consistent. The 6.827%
  figure, which the budget gives against the exact-split central value, goes away.
- It is route L42 of the 2D publication-path design, which chose seed 42 by matching cost, not by the
  central values. That cost argument presumed a new seed-42 statistical band, which has not been built,
  so `P07` remains. The REPORT also records CV42's mild over-dispersion against seeds 1–10 (RMS z 1.28,
  max 4.25); the note now states it.
- It is not the lowest-χ² LightGBM draw: it ranks 4th of 11.
- Seed 1 would have matched the statistical band's training seed instead, but no other block.

## The new numbers

All are measured by the committed producers at `e1216e9c`, on saul login05 with ROOT 6.28/12. The receipts
are in `docs/orchestration/receipts/2d-lgbm42-20261011/`, with checksums in `SHA256SUMS`.

| quantity | exact-split (was) | LightGBM seed 42 (now) | receipt |
|---|---|---|---|
| integral (cm²/nucleon) | 3.0733e-38 | 3.0730e-38 (prints 3.073e-38) | agreement windows |
| ratio to published | 1.0113 | 1.0112 (prints 1.011) | agreement windows |
| median bin ratio | 1.0064 | 1.0081 | agreement windows |
| bins within 5/10/20 % | 77.6/94.1/98.5 | 82.9/95.6/99.0 (170/196/203 of 205) | agreement windows |
| pull mean / RMS (published σ) | 0.089/0.598 | 0.074/0.564 | `chi2_lgbm42_paperonly.txt` |
| χ²/ndf, published covariance | 3.661 | 2.654 | same |
| χ²/ndf, combined (published + ours) | 1.472 | 0.914 | `chi2_lgbm42.txt` |
| log-normal combined | 1.455 | 0.932 | `chi2_lgbm42_lognormal.txt` |
| stat-subtracted combined | 6.79 | 4.128 | `chi2_lgbm42_substat.txt` |
| combined pull mean / RMS | 0.051/0.405 | 0.041/0.386 | `chi2_lgbm42.txt` |
| ours vs Tune v1 χ²/ndf | 26.49 | 29.75 (data vs Tune v1 control 33.04, unchanged) | `receipt_model_chi2_2d_lgbm42.json` |
| diagonal-only χ²/ndf vs published | 0.37 | 0.324 | same |

**Control.** The same producers on the exact-split file reproduce 3.661 and 0.089/0.598
(`chi2_exact_paperonly_control.txt`).

**Two receipt-metadata caveats.**
- `receipt_model_chi2_2d_lgbm42.json` records `repo_commit` 32e403b8, the deployed checkout's HEAD read
  through `MNV_REPO`, not the clone that ran. The five producers are byte-identical between 32e403b8 and
  e1216e9c.
- Its "identity" field is the producer's fixed text for the exact-split file and does not describe CV42.

**Pairing (local, committed operands).** `lgbm_central_metrics.py` reads `remote_reduce.json` (committed)
and `fig_arrays.npz` (sha256 `72394a2b…`); its output is `lgbm_central_metrics.out`.
- Seed-42 central vs the seed-1 statistical band's central value: median per-bin difference 0.18%
  (max 1.79%), or 0.30 statistical standard deviations (max 1.28).
- Exact-split vs seed 42: 0.98% median per bin (max 12.2%), 1.32 statistical standard deviations.
- The ten LightGBM seeds 1–10 give χ²/ndf 2.64–2.75 against the published covariance.

## Disclosures this requires

1. **Post hoc choice.** The switch was decided after both learners' comparisons with the publication were
   known, and it lowers the published-covariance χ²/ndf from 3.66 to 2.65. The roughly one-unit
   learner dependence was documented before the decision (note, tension anatomy).
2. **A residual seed mismatch remains.** The statistical band was trained at seed 1, the systematic block
   at seed 42, and the ML block over seeds 1–10. The seed-42 central value differs from the seed-1 one by
   0.30 statistical standard deviations (median). The seed-1/seed-42 pairing (`P07`) is still unresolved.
3. **Reproducibility.** This file has no execution log or `runConfig` (it predates `971fc00c`). Its
   reproduction rests on the 1.4e-11 agreement with the July CV.
4. **Unchanged by the switch.** Coverage of the rebuilt band is still untested (KI 85). The universes'
   zero-point issue (KI 93) remains. The two-d-followup still finds no feasible route to the original
   objective under current inputs.
5. **Exact-split becomes a cross-check.** The note's 2D figures (cross section, slices, pulls, model
   comparison, tension maps) and its §6.4 tension numbers were regenerated from CV42 by the committed
   producers (`SHA256SUMS.figures`). Studies computed only on the exact-split central value are labelled as
   such and not recomputed: App. A's tension appendix, edge-bin table, shape-only χ², regularization scans
   and iteration scan (seed 1).
6. **Stale release artifacts.** RC7 and `fig_arrays.npz` (`72394a2b`) carry the exact-split curve for Fig. 1.
   The article's Fig. 1 is regenerated from the committed `remote_reduce.json` seed-42 values (float64, the
   same 205 cells). The release export (`export_fig_arrays.py`, which hard-codes the exact-split file) has
   not been rebuilt.
7. **Fig. 1 now shows this analysis's own ±1σ band.** It is drawn from `cov2d_blocks_205.npz`, the VL170/VL172
   universe+bootstrap rollup plus the ML block, exported read-only on NERSC; identities are in
   `cov2d_blocks_205.json`. The blocks reproduce the committed per-cell σ to 2e-16 and the 6.8707% median.
   `make_figs.py` draws the band only when the arrays carry `cov_ours`, and old arrays still give the old
   figure byte-identically.

## Not changed

- No covariance, band, or uncertainty number.
- No 3–5D result or joint test.
- No gate.
