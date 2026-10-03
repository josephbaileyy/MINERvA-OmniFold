# Scalar-5D model dependence, variability and resolution

The existing products **do not establish a bias–variance tradeoff across estimator settings**. Noise-free recovery improves for some historical truths, persists or deteriorates for others, and is sensitive to which integral is reported. Repeated experiments at five iterations measure small residual spread alongside material bias. There are no matched repeat ensembles at the other iteration/capacity settings. This is a delivered methodological synthesis, not a qualifying precision measurement.

**Next measurement: DEFERRED** until the current GBDT campaign (`s5p-20260926`, `OI-193`) finishes and its required independent terminal verification is recorded. The [proposal's scheduling disposition](PROPOSAL.md#scheduling-disposition-2026-10-03) defines the evidence needed before reconsideration; it grants no automatic launch. Review and integration of this existing-data synthesis can proceed meanwhile.

## Scope and frozen inputs

Authority: the user’s 2026-10-03 instruction to execute [the supplied handoff](HANDOFF.md). Baseline canonical `main`: `556d16373ae859e449b3fb71c1f61b14b7b61891`; standalone `main`: `9191693249d5af2dec8ddf20561119f8f1d84286`, both read from the remotes before work. One analyst owns code and text. Prior independent reviews support only their original operands. This task uses a separate implementation and numerical checks by the same analyst, **not a fresh independent review**. At most two focused review/repair cycles are budgeted. The terminal result is this synthesis, both manuscript deliveries and the costed proposal, even without a tradeoff or a useful total uncertainty. No extraction, training, unfolding, ensemble generation, allocation, production control or collaborator messaging is part of this task.

Canonical evidence: ledger VL153–VL155; s5e [outcome](../../docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md), candidate receipts and review round 2; s5p [Stage-2 exit](../../docs/orchestration/RECORD-20260927-s5p-stage2-exit.md), [independent review](../../docs/orchestration/REVIEW-20260927-s5p-round1-stage2-exit-and-joint-design.md), amendments 1–4 and **amendment 6's corrections**, envelope receipt, amendments 7/8 and terminal checklist. Later corrections outrank the initial exit record. Original files and verdicts are unchanged.

`definition.json` binds the fine grid, reporting maps, support and source identities. `inputs/inventory.json` identifies 376 distinct selected raw products (and 697 available exclusions), their SHA-256, size, producer-code digests, truth/seed/split/configuration metadata, completion and role. Null metadata fields mean not recorded in that product, not an inferred value. Product metadata carry input identities; the multi-GB raw event inputs were not downloaded or re-extracted. `inputs/operands.npz` preserves the sufficient projected arrays to regenerate every figure offline. Units are cell integrals in cm²/nucleon, before dimensionless residuals are formed. The source and preserved-operand hashes are enforced by the commands below.

The cluster freshness check returned FRESH on canonical cluster main `32e403b8`; that is a route-health observation only. The remote product hash read is timestamped in the inventory; every selected local copy matched it. No growing production ensemble was opened. Products were copied read-only into a separate local namespace. The reducer imports only the standard library and NumPy: no production module can resolve to a different checkout. The source receipt hashes are checked rather than importing receipt-bound code.

### Availability and exclusions

| Family | Selected content | Identity/access limitation and treatment |
|---|---|---|
| Noise-free baseline | nominal/W3 complete at 200; D1/W1 prefixes to 40; q3 prefix to 30 | Current partial files contain 100/125/100 iterations for D1/W1/q3. Their old exact checkpoint bytes are no longer at the routed path. Current prefixes reproduce **every committed series median and recovery proxy**; later entries are excluded. Partial files have no embedded metadata; settings are routed through the frozen task tables and original receipt, not invented from neighboring metadata. No final trace checks are asserted for partial runs. |
| Capacity | three complete 400-tree/31-leaf runs through 10 | Duplicate partials excluded. No 100-iteration capacity result exists in the inspected directory; an intended run length is not a completed length. |
| Candidate assessment | 40 nominal plus 20 at each of D1, q3, W1, W2, W3 | Exact frozen seed ranges 800000–805019, separate truth ensembles; no pooling. All are development reuse now. |
| Fixed statistical width | 100 nominal-bootstrap replicas of experiment 700000 | Shared width origin counted once; not 100 independent truth experiments and not a width refitted per assessment experiment. |
| Numerical overlap | base data, 20 jitters, 50 paired bootstrap/jitter replicas | Unjittered replicas are reused from s5e. Other nominal/departure numerical studies remain receipt/review context; they are not silently added to these 50 data pairs. |
| Prior study | CV, nominal control and five **denominator-fixed** priors | All six receipt-bound hashes match. Pre-fix products excluded. D1–D5 still use historical generator ratios: excluding D1 does not repair D2–D5. No corrected-prior scan is claimed. |
| Stage-3/production | none | All-band joint-test ensembles are outside the synthesis. They cannot supply a setting scan; scientific joint claims await their own terminal contract and independent recomputation. |
| Adopted covariance/PET | none | No borrowed uncertainty scale, adoption or regrading; no PET outputs read. |

Raw recovery routes remain in the original receipts. For downloading, map the receipt's s5e `runs/cand` to `<raw-root>/s5e`, and s5p `runs/s2/{conv,num,prior}` to `<raw-root>/s5p/{conv,num,prior}`. Copy, never move or overwrite originals. A separate remote hash read must supply `{"observed_utc": ..., "files": {"logical/path.npz": {"sha256": ..., "bytes": ...}}}`. The committed projected operands protect the manuscript against loss of purgeable raw files; they do not replace event-level inputs or reproduce the original training.

## Reproduction

From the repository root, with Python, NumPy, SciPy and Matplotlib installed:

```bash
python nd-unfolding/gbdt_model_dependence/analyze.py
pytest -q nd-unfolding/gbdt_model_dependence/test_reductions.py
```

To independently reconstruct the projected inputs from recovered raw products:

```bash
python nd-unfolding/gbdt_model_dependence/reduce.py --raw-root <raw-root> --remote-hashes <remote-hash-read.json> --out <new-input-directory>
```

Compare the resulting arrays and inventory identities with `inputs/`; the default build uses the committed copy. `analyze.py --out <directory>` writes CSV plot data, PDF and SVG figures, and `summary.json`. The manuscript PDFs are copies of the four analysis PDFs in `results/`. No stochastic reduction or new resampling is performed. The package uses only standard scientific dependencies; the delivery record captures tested versions.

## Definitions and consequential checks

- Fine densities are multiplied by all five widths and summed. EW trace values are densities in E_avail/W, converted by the EW area; J/H2 traces are already integrals. Index-map results agree with a separate tensor-slice implementation. All full maps conserve rate; unsupported J cells remain outside reported J but in the full-domain total. H2 is **not a merge of J**; both are integrations of the same fine grid. Cell boundaries are aligned, and no out-of-domain event is reassigned by this reduction.
- Complete trace final/true arrays agree with independently integrated saved fine-grid products. For partial traces, every committed checkpoint-series median and proxy agrees with its original receipt. There is no invented interpolation beyond available iterations.
- The historical T2 proxy is `median(abs(fhat/ftrue - 1) / abs(ftrue/fnominal - 1))` for supported cells with absolute departure greater than 1%. The two denominators differ. Its complement is **not the exact fraction of an injected change recovered**, despite that shorthand in earlier records. We preserve the historical metric and threshold, not reinterpret it. The q3 stress preserves the EW marginal and has no eligible EW cells.
- Repeat bias and SD are the mean and sample SD of `(fhat_i - ftrue_i)/ftrue_i`. `ftrue_i` changes with the MC source split. This is residual variability conditional on the saved MC population; it is not the unconditional variance of a fixed-truth estimator. Mean intervals use Student t; SD intervals use the normal chi-square formula. They are pointwise model-based intervals, not validated simultaneous bounds. All historical EW/J mean residuals, SDs and interval hit fractions reproduce the assessment receipt. H2 reductions are new descriptive outputs.
- Historical intervals are `fhat ± sigma` and `fhat ± 1.96 sigma`, with fixed sigma from 100 replicas of experiment 700000. Coverage CSVs preserve integer hits, denominators, exact pointwise 95% binomial bounds and relative half-widths. They condition on that width estimate, excluding its finite-replica uncertainty. No envelope is added and no total-coverage claim is made.
- Prior shifts and envelope values reproduce the receipt per cell, both including and excluding D1. The numerical overlap's per-cell base and paired spreads reproduce the Stage-2 receipt. The code never sums the rounding variance into the bootstrap again.

## Claims and evidence

| Supported statement | Operand/reduction | Limit |
|---|---|---|
| W3 residual persists through the tested scan | `recovery.csv`: J median 5.573% at 5, 6.573% at 200; max 32.904%→44.770%; H2 median 3.421%→3.680% | Finite scan on one historical truth and fixed response; no infinite-iteration or algorithm-wide impossibility. The wavy plateau is not proof of an exact fixed point. |
| Other truth/functionals behave differently | D1 J median 9.473%→4.904% at 5→40; W1 5.411%→4.092%; q3 EW 4.987%→6.423% at 5→30 | D1/W1 are historical ratios, not current generator differences. q3 joint medians need not worsen with EW. This reconciles earlier improvement and deterioration reports. |
| Capacity changes recovery, but historical admission still fails | Same three noise-free truths at 100/8 and 400/31, actual capacity limit 10 | Increasing the **background refinement** to 400/31 repaired nominal bias; increasing the **OmniFold estimators** to 400/31 is a different intervention. Neither is a matched variance scan. |
| Small repeat spread can coexist with large residual bias | `ensembles.csv`, W3 EW29: +23.665% mean residual, 0.558% SD; EW7: −6.812%, 0.299% SD | Same five-iteration R setting, n=20, historical truth; no cross-setting frontier. |
| Coarse reporting can reduce both summaries | Same fine arrays integrated into J and H2; plots and per-cell tables | Different estimands, support and cell counts; cancellation/averaging is not improved precision on unchanged functionals. |
| Fixed nominal intervals miss individual cells | Nominal EW41 15/40=37.5%, exact 95% [22.7%,54.2%]; departure examples zero of 20 have upper bound 16.8% | The historical interval, not a candidate-specific total band or per-experiment bootstrap; all cells in CSV. Pooled A2 PASS and A_FAIL preserved. |
| R bootstrap carries tested rounding variability | `overlap.csv`: J 0.228% base SD, 0.368% bootstrap SD, 1.018 consistency, 0.369 numerical variance share | Frozen jitter-model diagnostic; no regrading of stability failure, total coverage or transfer to adopted trunk. |
| Prior shifts correlate with residuals without bounding each cell | `prior.csv`: W3 J/H2/EW fractions above residual 70.6/51.9/53.8%; J r≈0.918 | Different denominators, shared origins, historical shapes. Data truth within the vertex span is unproved. Neither probabilities nor a covariance. |
| No measured tradeoff curve | Inventory has no matched repeat ensembles across settings | An unresolved relationship, not evidence of no possible tradeoff. |

`costs.csv` preserves **receipt-based measured unfold wall seconds**, including construction, sample counts and dtype grouping. Five-iteration float32 pseudo runs have median 293.973 s (423 records); float64 pseudo runs 339.244 s (120), and data 648.044 s (70 float64). Completed 200-iteration baseline traces have median 31,954.207 s (two truths); 10-iteration capacity traces 4,895.386 s (three truths). These heterogeneous workloads do not establish a paired speed ratio or billed node-hours. Forecast coefficients and packing are kept separate in [PROPOSAL.md](PROPOSAL.md).

Omitted: a cross-setting bias–variance frontier (missing variance axis); corrected-generator prior envelopes (no corrected scan); total-coverage plots (no adopted interval for these candidate products); new production-ensemble reductions (terminal ownership and different conditioning); uncertainty bands fabricated from noise-free summaries. Tails are retained in the CSVs and the W3 maximum quoted above rather than hidden by medians.

## Manuscript and review status

The main account is the new subsection in `sec_validation.tex`, after refinement-candidate diagnosis and before C2ST; the following pre-existing diagnostics have their own subsection so they do not become claims of the synthesis. `app_statmethods.tex` gives definitions, `sec_eavailw.tex` a short implication, and paper/primer wording is consistent. Four figures are in the note; concise paper/primer text avoids duplicating them. Builds and both remote branches are recorded in `DELIVERY.md`.

The first review/repair pass checked source identities, cell-integral units, non-nested reporting maps, completed ranges, all receipt comparisons, fixed-width coverage semantics and figure rendering. It caught an empty q3/EW departure set, handled explicitly rather than dividing by tiny departures. The second pass checks manuscript rendering, synchronized text and delivery integrity. **No fresh independent reviewer was authorized or used.** Original independent reviews plus same-analyst reproductions are not renamed an independent review of the new code. Publication use requiring such review remains outstanding.

The historical s5e `A_FAIL`, s5p measurement `NOT ADMITTED`, and the governing `publication_readiness: NOT READY` remain. The synthesis creates no new reportable uncertainty and changes no adopted bytes. Additional work is proposed, not launched.
