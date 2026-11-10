# Figure caption repair

Baseline: d53af941a. The repair restores the figure-specific qualifications listed in
pairs.json, items 1–10. The before/after text is recorded for every item, including
all four paragraph moves. Figure producers, PDFs, values, tables and the Supplement
are unchanged in this commit.

- Figure 1 names the ratio denominator and scopes the four-block covariance to the
  unfolded band. Its correlation qualification is part of the benchmark paragraph.
- Figure 2 defines the difference as that of the two-dimensional result.
- Figure 3 states the changed truth, explicitly identifies panel (a) as a lower-capacity
  variant rather than the reported estimator, and names the reported comparator in
  table 2. The sixteen-cell and truth-selection qualifications join the citing paragraph.
- Figure 4 defines z as bias divided by uncertainty, restores the covariance's
  leave-own-generator-out construction, and explains why the p-only q3 flag has no
  outline. The residual/noise definition joins the paragraph immediately above it.
- Figure 5 restores that the requirements were fixed before the test. Its population
  and perturbation definitions join the citing paragraph, after its protected sentences,
  which are retained verbatim.
- Figure 6 identifies the horizontal axis's NuWro-shape truth and restores the statement
  that cells are not independent repeated experiments. The other two qualifications
  remain in section 7: shifts are not measured bias, and correlation supplies no
  per-cell bias bound.

Checks against the baseline are recorded in checks.json: every fvval/fvcase occurrence
is unchanged, every reference target remains, both table blocks are byte-identical,
the protected stability paragraph is byte-identical, and no numeric literal is new.
The redundant self-citation attached to the cells/not-experiments sentence is removed
when the sentence returns to the caption; its figure target remains cited in section 7.

| Figure | Before | After |
|---|---:|---:|
| 1 | 52 | 57 |
| 2 | 35 | 37 |
| 3 | 64 | 80 |
| 4 | 51 | 86 |
| 5 | 65 | 68 |
| 6 | 65 | 76 |

Counts use texcount -sum -brief on standalone caption fragments. Figure 4 is longer
than the earlier approximate 80-word target because the requested self-contained
qualifications are restored.

Validation: make_values_fived16.py --check passes all 3811 values, its two source-figure
checks and ten listed-truth sentences. main_paper.tex builds successfully with latexmk;
the final log has no overfull box, undefined reference or oversized float. The existing
note auxiliary file and bibliography were copied as untracked build aids from the
previously built figures worktree. Rendered figure/caption pages were inspected for
clipping, overlap and paragraph placement. Final check_round, check_restyle, blind-copy
verification and standalone-note synchronization remain with the paper integrator.
