# Existing-data synthesis delivery — 2026-10-03

The methodological synthesis is delivered. **A bias–variance tradeoff across settings is not established.** The noise-free scans are truth dependent; repeat ensembles exist at only one setting. This does not establish the absence of a possible tradeoff. The original precision-measurement objective remains unmet: s5e `A_FAIL`, s5p measurement `NOT ADMITTED`, and governing publication readiness `NOT READY` are unchanged. No adopted covariance, central estimator or historical verdict was replaced.

## Pushed source snapshots

Both remotes were queried directly after successful pushes. The common branch is `analysis/gbdt-model-dependence-20261003`.

| Repository | Pushed source commit / observed remote head before this delivery-record commit | Review route |
|---|---|---|
| [MINERvA-OmniFold](https://github.com/josephbaileyy/MINERvA-OmniFold/tree/analysis/gbdt-model-dependence-20261003) | `87032ae050582c275526fc263006158855ec8d2b` | [Draft PR #9](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/9), base `main` |
| [MINERvA-OmniFold-Analysis-Note](https://github.com/josephbaileyy/MINERvA-OmniFold-Analysis-Note/tree/analysis/gbdt-model-dependence-20261003) | `d8425a64ecf3347805f3a5dd1abcca969f7bb54e` | Synchronized source branch; merge pending |

The canonical follow-up commit containing this record changes only delivery evidence, not the analyzed operands, code, figures or manuscript. Its identity is available from this file's git history; the final delivery message reports the subsequently observed canonical remote head. A commit cannot embed its own hash. Neither main branch was merged or force-pushed. The first canonical push encountered HTTP 400; a per-command HTTP/1.1 and buffer adjustment succeeded, and `git ls-remote` verified both heads above. No persistent transport configuration was changed.

## Evidence and reproducibility

- [README.md](README.md): scientific interpretation, claim-to-evidence table, exclusions and reproduction commands.
- [inputs/inventory.json](inputs/inventory.json): 376 selected products, 697 exclusions, metadata, completion status and independently read remote hashes. Superseded partial-checkpoint bytes are explicitly unavailable; their selected prefixes reproduce the committed summaries.
- [inputs/operands.npz](inputs/operands.npz), [definition.json](definition.json), [reduce.py](reduce.py), [analyze.py](analyze.py): sufficient projected inputs, source identities and independent reduction implementation. Original training is not rerun or reproduced by this package.
- [results/](results/): five CSV tables, numerical summary and four PDF/SVG figures. All four analysis PDFs match the manuscript copies byte-for-byte.
- [PROPOSAL.md](PROPOSAL.md): prioritized missing quantities, precision assumptions, costs and terminal decisions.
- Ledger `VL161`, `ND_OMNIFOLD_RUN_LOG.md` and `ND_OMNIFOLD_STATUS.md`: scoped scientific record. Original receipt-bound production code and historical results remain unchanged.

From the repository root, run `python nd-unfolding/gbdt_model_dependence/analyze.py` to regenerate the tables and figures without cluster access. Rebuilding projected operands from raw products requires the original receipt-routed copies and a separate remote hash read, as documented in the README.

## Manuscript integration and synchronization

The main account is note §6.1, **Model dependence, variability and reporting resolution**, adjacent to the candidate diagnosis and before the other validation diagnostics. Appendix A.8 gives the reduction and interval definitions; the E_avail/W section links to the implications. The paper and primer give concise consistent statements, including the narrower rounding-containment result for candidate R. Four detailed figures appear in the note only.

The standalone baseline had no independent changes in corresponding tracked manuscript sources. Its own `AGENTS.md` and `.gitignore` were preserved. Six sources (`sec_validation.tex`, `app_statmethods.tex`, `sec_eavailw.tex`, `paper_body.tex`, `primer_body.tex`, `technote.bib`) and four new figure PDFs were synchronized. All corresponding tracked sources, bibliography, existing figures and wrappers were compared, not just the changed files; the two repository-specific instruction/ignore files were excluded from correspondence by design.

Both `bash docs/analysis-note/build_all.sh` in canonical and `bash build_all.sh` in standalone exited zero. Each produced **115-page note, 7-page primer and 4-page paper**, with containment/source/PDF checks and self-tests passing. No unresolved reference or citation remained. Existing font-shape substitutions persist. The Overleaf paper wrapper (`latexmk -pdf -jobname=output -interaction=nonstopmode -halt-on-error main_paper.tex`) also built in both checkouts and yielded the same paper text.

All three full extracted texts match across repositories. Nine selected rendered pages match pixel-for-pixel: note physical pages 31–35 and 86–87, primer page 3, paper page 2. The four standalone figures and the edited manuscript pages were visually inspected for legibility and clipping. [build_evidence.json](build_evidence.json) preserves source hashes, PDF hashes, text hashes, page counts and render hashes. PDF file hashes differ between checkouts because build metadata differ; the text and compared renderings agree. Build products were generated from the exact manuscript sources subsequently committed above.

## Verification and review limits

- Five focused numerical controls pass: cell-integral geometry, support versus conserved totals, incompatible boundaries, finite-sample coverage bounds, and cancellation under aggregation.
- All consequential receipt comparisons embedded in the reducer/analyzer pass, including the partial trace prefixes, complete trace endpoints, historical mean/SD/coverage, prior envelopes and rounding overlap.
- Ruff, Black and strict mypy checks pass for the new reduction code. Tested with Python 3.14, NumPy 2.5.3, SciPy 1.18.1 and Matplotlib 3.11.2; TeX Live 2024 builds the documents.
- All 33 existing hash-binding tests pass. The new inventory adds exactly five existing historical truth-definition bindings; excluding this package restores the original 127-binding digest exactly. A corrupted new paired pin produces a named MISMATCH and nonzero exit; restoring the original bytes passes. The exact delta and control outcome are recorded in `build_evidence.json`.
- The canonical source commit passed all 13 repository pre-commit checks. No hook was bypassed. Final CSV/SVG whitespace normalization leaves all numerical values and manuscript PDFs unchanged.

The two focused review/repair cycles are complete: first operand/metric and figure checks, then manuscript/synchronization/delivery checks. One analyst performed this work. Original independent reviews support their original operands; a separate implementation by the same analyst is **not fresh independent review**. Such review of the new synthesis remains outstanding before scientific use requiring it. Existing production pipelines were not modified or broadly retested; the new scripts import no production modules.

## Next measurement proposal

Request **70 CPU node-hours, zero GPUs, at most two CPU nodes and 10 GiB**, after a separately authorized frozen design and independent review: 160 paired repeats at three truths and three settings (R5, R20, and R5 with larger OmniFold capacity), plus a small separate estimator-seed diagnostic. The same samples, splits and functionals supply both bias and variability axes. Normal-model planning gives a mean SE of 0.079 repeat SD and approximately 5.6% relative SE on SD; it does not guarantee power for variance or MSE differences. The packing and capacity extrapolations must be checked during admission.

Fresh confirmation is a separate estimated **35–45 CPU node-hours**. Statistical-interval coverage is a different, much larger optional study; total-uncertainty coverage cannot be responsibly costed before its interval construction exists. A plateau, deterioration or inconclusive panel is terminal, not a reason for automatic extension. **No new training, unfolding, ensemble, allocation or benchmark was launched.**
