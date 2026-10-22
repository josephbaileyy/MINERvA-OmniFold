# Glossary inventory, batch 0 (note register pass)

**Source.** The note at origin/main `38a53a53` (`base/` holds `git show 38a53a53:docs/analysis-note/<f>` for the 21
files below). **Population.** The editable files, in `files.txt`: the 13 body chapters `sec_execsummary` ...
`sec_summary`, `app_guide`, `app_statmethods`, `app_statmethods_nd`, `app_negweight`, `app_response_mismatch`,
`app_landscape`, `app_pet_pointer`, and `main_note.tex` (abstract only). Not scanned for editing: Apps. G-J
(`app_provenance`, `app_release`, `app_codebase`, `app_history`), the paper, primer, PET note (`sec_pet*.tex` belong to
`pet_note.tex`), `values*.tex`, `preamble.tex`.

**Method.** `scan_terms.py <dir> --md` counts each term in the *printed* text: comments removed; the arguments of
`\label`, `\ref`, `\cite`, `\input` and similar commands removed (so `sec:eavailw-adopted` is not counted as prose);
whitespace collapsed (a term split over two lines counts once). The verbatim quotation of the joint-test specification
in `sec_joint.tex` is counted in its own column because it must stay verbatim. `scan_terms.py <dir> --show '<term>'`
lists every line. The term list was built in three passes:

1. the terms the baseline named (labels.py JARG/HIST/BOOK/CODE examples, the brief's list);
2. a scripted frequency list of every hyphenated compound in the printed text of the 21 files (400 most frequent,
   reproduced by the one-liner in REPORT.md section 6), read by hand for coined terms (found: `report-only`,
   `record-only`, `selection-complete`, `active-lateral`, `support-limited`, `universe-complete`, `exact-GBT`,
   `first-built`, `same-ensemble`, `ours-only`, `five-axis`, `scalar-5D`);
3. a list of every `\texttt{...}` argument in prose (98 distinct), read for code identifiers and repository tags.

## Counts before (base 38a53a53)

Row labels name the pattern; the pattern itself is in `scan_terms.py` (`TERMS`). "Status sense" rows also count plain
English uses (for example "the most widely adopted method"); GLOSSARY.md says which uses are kept.

| term | total | by file | in verbatim quote |
|---|---|---|---|
| in use | 25 | sec_3d 7, sec_systematics 5, sec_5d 5, sec_summary 3, sec_execsummary 1, sec_intro 1, sec_validation 1, sec_joint 1, sec_fps 1 |  |
| adopt* (status sense) | 26 | app_negweight 9, app_statmethods 5, app_statmethods_nd 4, sec_method 3, sec_intro 2, sec_fps 1, app_response_mismatch 1, main_note 1 |  |
| constructed but not adopted / in use | 1 | sec_3d 1 |  |
| adoption gate | 1 | app_negweight 1 |  |
| quotable | 2 | sec_3d 2 |  |
| candidate (covariance/product) | 17 | sec_5d 4, sec_systematics 3, app_statmethods_nd 3, sec_execsummary 2, sec_experiment 1, sec_3d 1, sec_summary 1, app_statmethods 1, app_negweight 1 |  |
| report-only | 6 | sec_joint 6 |  |
| frozen | 32 | sec_joint 27, sec_method 2, sec_eavailw 1, app_statmethods_nd 1, app_response_mismatch 1 | 2 |
| re-qualify | 1 | sec_joint 1 |  |
| footing / footed | 30 | app_negweight 28, sec_5d 1, sec_fps 1 |  |
| negweight-refined (label in prose) | 4 | app_negweight 3, sec_5d 1 |  |
| dump-all | 3 | sec_systematics 1, sec_3d 1, sec_5d 1 |  |
| dump(s) (event-loop output) | 8 | sec_3d 2, sec_eavailw 2, sec_experiment 1, sec_systematics 1, sec_5d 1, app_statmethods 1 |  |
| selection-complete | 12 | sec_systematics 5, app_statmethods 3, sec_3d 1, sec_fps 1, sec_summary 1, app_negweight 1 |  |
| active-lateral / active-universe | 6 | sec_5d 2, app_negweight 2, sec_systematics 1, sec_3d 1 |  |
| support-limited | 3 | sec_systematics 1, sec_3d 1, sec_5d 1 |  |
| universe-complete | 1 | sec_experiment 1 |  |
| J28 | 1 | app_negweight 1 |  |
| VL/OI/KI tracker id | 4 | app_statmethods 4 |  |
| KNOWN_ISSUES | 3 | app_statmethods 3 |  |
| Stage-1/Stage-2 | 2 | app_statmethods 2 |  |
| standard-P4 | 1 | app_statmethods_nd 1 |  |
| Q (2D covariance name) | 1 | app_statmethods 1 |  |
| B3 label | 1 | sec_joint 1 |  |
| FPS (abbrev.) | 2 | app_negweight 2 |  |
| cv / mean variant label | 6 | sec_5d 5, sec_systematics 1 |  |
| lgbm / exact / hist (backend names in prose) | 17 | app_statmethods 7, app_negweight 6, sec_validation 2, sec_method 1, sec_results 1 |  |
| digest | 5 | sec_5d 2, app_negweight 2, sec_method 1 |  |
| receipt / receipted | 4 | app_negweight 2, sec_method 1, app_statmethods_nd 1 |  |
| lane | 1 | app_negweight 1 |  |
| gate (process sense) | 4 | app_negweight 3, sec_systematics 1 |  |
| discharge | 2 | app_negweight 2 |  |
| ledger | 1 | app_negweight 1 |  |
| NONQUOTABLE | 1 | app_response_mismatch 1 |  |
| the design record | 1 | sec_method 1 |  |
| self-validated | 1 | sec_joint 1 |  |
| campaign's | 1 | sec_joint 1 |  |
| contract | 1 | sec_fps 1 |  |
| sibling | 1 | sec_5d 1 |  |
| these bytes / this object | 5 | sec_5d 5 |  |
| rollup | 7 | app_statmethods 6, sec_systematics 1 |  |
| omnifile | 1 | app_statmethods 1 |  |
| headline (as jargon) | 7 | app_statmethods 4, app_landscape 2, sec_3d 1 |  |
| anchor | 6 | sec_3d 3, sec_method 1, sec_eavailw 1, sec_fps 1 |  |
| home(s) | 2 | sec_intro 2 |  |
| truth-tree authoritative / invariants | 3 | sec_experiment 2, sec_validation 1 |  |
| record-only | 4 | app_response_mismatch 3, sec_validation 1 |  |
| replay | 6 | sec_joint 5, sec_eavailw 1 |  |
| launcher | 3 | app_negweight 2, sec_method 1 |  |
| MnvTune | 6 | sec_experiment 3, sec_fps 2, sec_method 1 | 2 |
| exact-split (kept term) | 34 | app_statmethods 12, sec_method 6, sec_systematics 5, sec_results 5, sec_execsummary 2, sec_validation 1, sec_3d 1, sec_fps 1, sec_summary 1 |  |
| CVUniverse:: | 6 | sec_3d 4, sec_eavailw 2 |  |
| hXSec | 3 | sec_results 3 |  |
| --bkg-mode | 2 | app_negweight 2 |  |
| App. G tag pointer (kept) | 29 | app_negweight 6, sec_systematics 5, sec_validation 5, app_statmethods 3, sec_method 2, sec_3d 2, sec_eavailw 2, sec_5d 2, sec_joint 1, app_statmethods_nd 1 |  |

## Terms the baseline named that no longer occur in the editable files

`receiving-cells`, `destination-mask`, `declared-dst-cv` (and the "pre-J28 ... construction-cause quarantine" passage):
0 in the editable files at 38a53a53; they occur only in `app_history.tex` (App. J), which this batch may not edit.
"(App. G, statband-retest)": the tag pointers are counted in the last row (29 in prose; kept, see GLOSSARY.md G1).

## Candidates found by the scan and judged standard (no change)

| term | count (base) | why kept |
|---|---|---|
| universe, systematic universe, band, vertical / lateral band | 137 (universe) | MINERvA/MAT vocabulary for the multi-universe systematic method, used in the collaboration's publications; *lateral* is now defined at first use (sec_experiment) |
| push-weight, step 1 / step 2, miss | 17+ | OmniFold's own terminology (Andreassen et al.) |
| CV (central value) | 60 | MINERvA usage; defined by context ("central value (CV)") |
| block, block sum, unified throw | many | defined in sec_systematics (sec:uq-combine) |
| exact-split | 34 | the name of configuration (b), defined at sec:method-config; kept and made uniform (`exact-GBT` and bare `exact` became `exact-split`) |
| J, H2, EW cells; D1, W1-W3; R; RD1-RD3 | -- | defined in the label table of sec:gbdt-model-dependence |
| July sweep, May sweep | 9 | dataset names needed to tell the two universe productions apart; listed in the new app_guide label table |
| seed 42, seed-1 | 15 | literal seed values |
| same-ensemble, ours-only, first-built, split-sample, fixed-truth | -- | descriptive compounds, each defined where used |
| five-axis / five-dimensional | 21 / 38 | synonyms; unifying them is register work for the chapter batches (open question in REPORT) |
| driver, event loop, engine, omnifiles | 18 / 15 / -- / 1 | defined in App. I (not editable); `omnifile` in prose replaced, the rest kept |
| production, pilot, battery, sweep | 44 / 6 / -- / 21 | ordinary HEP English |
| record(ed) | 52 | ordinary English in nearly every use; the BOOK sense ("receipt", "ledger-verified") was replaced |
| headline | 7 | kept where it means a measurement's main result (app_landscape, sec_3d); replaced in app_statmethods where it meant "the quoted number" |
