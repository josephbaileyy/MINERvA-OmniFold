# Short methods paper: figures lane

Baseline: PR #977, e97d2b20d. This branch changes no manuscript source. director-helper-3 integrates;
journal-editor reviews. Owner: figures lane (Codex). Decision: which existing diagnostics can support
three additional figures for the reported estimator? No new training, unfolding, ensembles or scheduler
work. Terminal condition: reproducible assets or an explicit operand gap. Review budget: one referee
pass and at most two focused repair cycles. This is figure preparation, not scientific adoption.

## Delivery

`make_figures.py` is the plotting producer. Run with a Python containing NumPy, SciPy and Matplotlib:

```
MPLCONFIGDIR=/private/tmp/minerva-mpl /Users/josephbailey/miniconda3/bin/python3 publication/methods-figures/make_figures.py
```

Every input is SHA256-pinned in `inputs.json`; changes fail closed. The output PDFs and PNG previews
are generated in code, never edited. `numbers.json` preserves every plotted number. `captions.tex`
provides self-contained captions and proposed citation positions, for the integrator. No Table 2 move:
the director's bridge ruling keeps all three column groups intact. No submission or deposit.

### Bias by reported cell

`paper_bias_cells.pdf`: signed z, paired heatmaps with/without the run-period block, 12 graded truths
in Table 2's names and order. All six descriptive alternatives are excluded. Black outlines mean |z|>2.
Readouts are precisely the with/without F0b products pinned by `make_values_fived16.py`. The numerical
producer is `nd-unfolding/fd_f0_regrade.py`: its header defines bias, noise of the mean, leave-own-generator
out, and z. Its `estimator_problems` requires configuration (e): five iterations; seed 42; deterministic
all-row LightGBM classifiers 100 trees/8 leaves; refinement 400 trees/31 leaves at seed 45; candidate R.
The readout records that producer's code digest. The plotting script checks byte identities rather than
revalidating raw cluster metadata or rerunning the producer's grading.

Checks: all 384 plotted z are the committed readouts' values with no rounding; all 24 arm/truth maximum
|z| values equal the generated `values_fived16.tex` values at two decimals; all flagged-cell lists equal
the readouts; all twelve biases are identical across arms; the Table 2 truth order is parsed and checked.
Table 2 prints maximum |z| only in the primary group, not every per-cell z; the other maxima are generated
keys in values_fived16.tex. This is the precise meaning of agreement, not a claim that the table prints
384 z values. The plot does not encode the joint p criterion: Table 2 remains essential.

### Prior sensitivity

`paper_prior_response.pdf`: same numbers as the note's `gbdt_prior_response.pdf` in sec_5d,
sec:gbdt-model-dependence. Numerical producer: `gbdt_model_dependence/analyze.py`, `_prior_rows`;
plot logic mirrors that producer's `_figures` prior-response panel, resized for the article.
Its horizontal is minus `trace_b0_w3`'s fifth-iteration noise-free relative residual; vertical is
`(prior_d4-CV)/CV`. W3/D4 is the historical NuWro (pT,p_parallel,E_avail) deformation.
The frozen operand archive is checked against the inventory's own full digest. The selected prior
product's committed metadata are checked for R, five iterations, seed 42 and refinement override
400/31. `s5e_candidate.py` defines R by that override; the OmniFold classification remains 100/8.
The noise-free convergence comparator is signal-only (`asimov_same`) so no background refinement runs;
its b0 name does not imply the lower-capacity background refinement. The prior product includes R's
background refinement. The three maps have 109/27/39 supported cells, not the sixteen-cell product.
This is exactly the note diagnostic cited in section 7; no inferred real-data bias is plotted.

## Rounding figure: exact operand gap

The paper's 0.8/2.6 statement comes from `s5e_analyze_candidate.py` A3, not from the later mechanism
study. It computes, for each of 153 functionals (42 EW + 109 J + two totals), the larger absolute shift
under real-data edge-safe jitters 1 and 2, relative to the float64 upcast baseline, divided by the
SD of 100 real-data bootstrap replicas (ddof=1). `assess_receipt.json` preserves only median
0.7829505732456221, maximum 2.5837789197284393 and argmax J145. These are not enough to reconstruct
a distribution. Independent `review2/r2_recompute.json` agrees and records 51 values above 1, but
also does not preserve the array. `review2/r2_recompute.py` reads cluster `r2_cache.npz`; no such
cache is tracked at the baseline.

The available committed `gbdt_model_dependence/inputs/operands.npz` has 20 different real-data
jitters and 50 bootstrap replicas and adds H2 integrals. FD-STAB's `estimator_stability_analyze.py`
uses one GiBUU-like simulated pseudo-experiment and 51 jitters, evaluated as 25 consecutive pairs,
with a nominal pseudo-data bootstrap sigma; its committed fd_stab.json stores summaries. RS1's
`rounding_mechanism_analyze.py` uses 20 jitters on a simulated pseudo-experiment, not the original
two real-data perturbations. These cannot honestly be labelled the requested distribution.

Needed: a committed array/cache containing the original two data jitters, baseline and 100-replica
sigma (or the 153 computed maxima), with their identities and configuration. No extraction, training
or new compute was run to fill this gap. Director notified over bridge before rendering any substitute.

## Validation and integration

Both PNGs visually inspected: labels visible, no clipping. Plot script completes with all assertions.
Only plotting and handover files under publication/methods-figures are changed; scientific analysis
modules, manuscript sources, hash-bound numerical producers and note sources are untouched. Integration
must include the paper builds/check_round/check_restyle/check_registry and the repository's standalone
note synchronization rule for any source/assets director-helper-3 adds under docs/analysis-note.
The lane has not performed that manuscript integration or claimed standalone synchronization.

Additional checks: all 175 prior-response points reproduce `results/prior.csv` exactly in both
coordinates. A deliberately wrong input pin is rejected. Python compilation and `git diff --check`
pass. Ruff, Black and mypy are not installed in the available plotting environment; those checks
were attempted and could not run. The repository's scientific test suite does not import this
standalone plotting script, which imports only NumPy/Matplotlib and the pure prior reduction;
no scientific implementation changed.
