# Figures 1–2 fetched-operand identity check: both stopped

No producer, PDF or caption was changed. No cluster connection was made. The four fetched files were
copied to task-owned `/private/tmp/minerva-figs12-operands/`, outside the repository, and checked against
the committed release manifest. All four hashes/sizes agree. `inputs.json` pins those external data paths
only. No raw operand is staged or committed. `check_operands.py` reproduces the local identity checks;
`identity-check.json` preserves the results. This is a presentation-input check, not a new physics result.

## Figure 1: base archive is not the drawn central value/covariance

The fetched base `fig_arrays.npz` has SHA256 72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8.
It computes published-sigma residual mean 0.08894542701552118 and SD 0.5981211651164514. The committed
printed PDF, SHA256 71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427, prints mean 0.060
and RMS 0.535. Even at printed precision the summaries differ. The base archive also lacks `cov_ours`,
which is needed for the printed result's uncertainty band.

The correct current entry point is `2d-unfolding/re2/partc/re2c_fig1.py --arm refined`. It loads the base
archive as a template, replaces `ours_v` with E_R from reduce.json, and adds cov_ours from Q_R. It then
calls `publication/release/figs/make_figs.py`. Thus a bare make_figs.py call on the fetched template
would move data and remove the displayed uncertainty band.

Evidence chain:

- `docs/analysis-note/make_figures.sh` lines 191–201 pins the installed 71a2ea48 PDF.
- `re2/RE2-PARTC-A3-REPORT.md` section 3 and `re2/run/partc_a3/RUN-fig1.txt` identify this redraw and its
  wrapper/library. Amendment 3 changed only sentence case in the legend from the preceding cabbbbc3
  asset, with text/pixel checks; no quantity changed.
- `re2/RE2-PARTC-REPORT.md` section 9 and `re2/run/partc_r2/partc-r2/fig1/RUN-fig1.txt` document E_R/Q_R,
  the inset summaries and the full input bundle. Paths here are under
  `docs/orchestration/state/2d-closeout/stageF/methods/`.

Needed to resume: the refined bundle pinned by the current RUN-fig1 record, rather than the template
alone. Canonical remote namespace in re2c_fig1_local.sh is
`/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/`:

- chain.json, reduce.json;
- outA/cov2d_Q_205.npz, outA/budget_Q.json, outA/SHA256SUMS;
- s5/production_cov.npz, playlist/playlist_term.npz, combination/combination.json.

The wrapper derives pins.json from chain.json and the uqMedian values file from budget_Q.json. The
base archive already supplied remains one required input. This list routes a future authorized fetch;
it grants no cluster access. Every bundle member must be matched to the committed current chain.

## Figure 2: fetched ROOT is a different estimator

Current printed tension_chi2_map.pdf is exactly SHA256
7161ded1a2a6666de6c04d55652c00bf2435a72a38e8ef0e422a6105c002ef08. This matches the installed restyle row
in `fig-restyle-20261031/DIGESTS.tsv`. Its run-a2/after/logs/inputs.sha256 pins the central input:

`/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/ER/xsec.root`

SHA256 **a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef**.

The fetched `2d_crossSection_omnifold_MEFHC_5iter.root` instead has SHA256
**142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5**. It is the manifest's old
exact-split input, not E_R. The source receipt `RE2-PARTC-REPORT.md` section 3's tension command also
explicitly uses `--ours $B/partb/out/ER/xsec.root`. Thus estimator identity fails, so Figure 2 is stopped
as instructed. No alternate inputs, recomputed map or paper-only output was substituted.

The fetched paper covariance does match the restyle receipt's 6c6dce72 hash. The model CSV also matches
the supplied release manifest. Neither repairs the central-input mismatch.

Execution environment note: the local plotting Python has NumPy/Matplotlib/uproot but no PyROOT;
`diagnose_tension.py` imports ROOT. This is secondary to the scientific input mismatch. No environment
or loader modification was attempted.

## Handover

Current font metrics for Figures 1–2 remain unchanged. Their producers and the note's shared tension
PDF remain untouched. Resume only with the matched refined operands and an identity-preserving path
through the current producers. All fetched raw data remain outside the repository.
