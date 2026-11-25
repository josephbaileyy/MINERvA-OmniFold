# regenA4: STOP before E (2026-11-25)

The run followed AMENDMENT-A4 under the director's GO. Only the OLD input has been run. The E input has **not**
been run, because the GO's condition is to stop before E on any C-OLD, C-SL-a or C-SL-b failure.

**Pre-run** ([`receipts/prerun.txt`](receipts/prerun.txt)):
- A4_VENV was unset; `env | grep A4_` was empty;
- every pin equalled the amendment's;
- the producer worktree W was at 06893b0a, with porcelain 0 and ignored 0.

**Step 1:** TIER2-ARGV-EQUAL :: PASS ([`receipts/step1_tier2_argv_equal.out`](receipts/step1_tier2_argv_equal.out)). The
real ~/cov2d-work/figrun/tension was hash-checked unchanged.

**Step 2, OLD** ([`out/old/steps.log`](out/old/steps.log)): fig2 rc 1; fig3, the slices (markers and strip) and tension
rc 0.

**Gate, OLD-side controls** ([`receipts/gate_controls_old.out`](receipts/gate_controls_old.out)):

| figure | control | result |
|---|---|---|
| MEFHC_5iter_pull_full | C-OLD | EQUAL-BUT-DATE |
| tension_spectrum, _chi2_map, _mode_maps | C-OLD | EQUAL-BUT-DATE, all three |
| xsec_paper_pt/pz_slices, markers layer | C-SL-a | EQUAL-BUT-DATE against figs-r2, both |
| xsec_paper_pt/pz_slices, strip of the committed figs-r2 | C-SL-b | BYTE-EQUAL to the installed 58e4d16a / 4216003c |
| MEFHC_5iter_xsec_proj_pt / _pz | C-OLD | **FAIL: no file**. The fig2 step stopped before saving |

**C-PINS:** equal before and after. W after: porcelain 0. Its ignored files are only `__pycache__` that the steps
wrote ([`receipts/postrun_W.txt`](receipts/postrun_W.txt)).

## Why fig2 stopped

[`out/old/fig2_log.txt`](out/old/fig2_log.txt) ends with:

> edges: MEFHC_5iter_xsec_proj_pt: the check before the fix should flag the published-prediction line only; it gave
> {'top': ["line 'Published (PRD 104, 092007)': x values off the bin edges and centres", "line 'Tune v1: published
> prediction': steps-mid steps change or end off the bin edges"], 'ratio': []}

The source is the installed Fig. 2 chain's edge-fix layer, `note-figfix-20261120/tools/compose_fig2_edges.py:109-116`.
That layer reads the projection's edges from its prior histogram, and its pre-check must flag only the Tune v1
published-prediction line, or the layer stops. The published points ('Published (PRD 104, 092007)') come from Fig.
13's producer, `plot_2d_threeway_fig13.py`. Since #1318 it draws them on the release TH2D's own pT axis (0.075 /
0.325 / 0.475). On OLD, the projection's bins are ours (0.07 / 0.33 / 0.47), so the published points sit at the
release's bin centres, which are off OLD's grid, and the pre-check flags a second line.

Main's producers on OLD therefore cannot reproduce the installed Fig. 2. What this shows is that the installed Fig. 2
was drawn with Fig. 13's code from before #1318, which placed the published points on our pT bin centres. It does not
show a fault in the fix.

The p∥ projection was never reached (the step stops at the first failure). Its edges are the same on both grids.

Under the GO, this failure is terminal for xsec_proj_pt/pz without the director, so nothing was rerun.
