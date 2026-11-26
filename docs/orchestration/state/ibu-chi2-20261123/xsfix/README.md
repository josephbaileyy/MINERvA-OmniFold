# plot_2d_cross_section on the input's own axes: review receipts (2026-11-25)

**By** the `ibu-chi-squared-issue` session. These are the code PR's receipts, ahead of regenA amendment A4 (the
note's figures on the paper's pT edges).

**Pins.** No runner, config or receipt pins `plot_2d_cross_section.py` or `plot_2d_paper_comparison.py` by sha. A git
grep for the 16- and 12-character prefixes of each file's sha at main 359ee648 found none. Nothing re-pins.

**Tests.** [`tests.log`](tests.log): `2d-unfolding/tests/test_published_axis_widths.py` and `test_reported_cells.py`,
72 passed, in ~/cov2d-work/figenv/rootmpl3108.

**Mutants.** [`mutants.py`](mutants.py), run by [`run_mutants.sh`](run_mutants.sh). Each mutant is applied to the
worktree, the `CrossSectionPlotEdges` tests run, and the files are restored; their shas are equal afterwards.
Result: [`mutants.out`](mutants.out), 25 of 25 killed. The first round left M24 surviving, because the flux-edge check
also refused its input, so an input whose truth differs only in p∥ was added.

**Reads.** agy, `gemini-4-hydrogen-xhigh`, two rounds. The reports are its verbatim output, kept as .txt like the logs:
- [`agy-read1.txt`](agy-read1.txt): no change on our grid. Its findings were the transposed-input assumption, no
  one-grid check, and test gaps; the second commit addresses them.
- [`agy-read2.txt`](agy-read2.txt): every first-round correctness finding addressed. The fallback-flux edge check and
  the remaining test gaps were addressed in the third commit. Its note about extra hunks comes from a two-dot diff
  taken after a shared-ref fetch moved origin/main.

Not changed:
- the p∥ labels stay `.1f`, which keeps "1.5 < p_|| < 2.0" on both grids;
- `edge_label`'s 1e-9 tolerance assumes TH2D (double) axes, which every input here has.
