# Note compression outline (director, 2026-11-19) — DRAFT for Joseph's approval

Joseph, 2026-11-19: the target is "as small as possible ... not sacrificing ease of reading"; the three questions are
an idea, "we should definitely go with whatever is the best idea".

Measured at draft cd5226e05: 166 pp, about 85,300 words, of which front matter 8,200, body 52,200, appendices 24,900.
Target: about 30,000–35,000 words in all, with the body under 20,000.

## The organizing questions (the note's framing)

1. Does unbinned OmniFold reproduce MINERvA's published two-dimensional muon cross section?
2. What does extending the unfolding to five observables give, and where does it stop being reliable?
3. What do the validation tests show about the method's bias, stability and uncertainty?

Each part opens with its question and its answer in two or three sentences. Figure and table captions lead with the
takeaway, in words, not labels.

## New structure

| New | Content | Built from | Budget (words) |
|---|---|---|---|
| Abstract | One paragraph: what is measured, the answer to each question, the one overriding caveat (no validated coverage). No configuration letters, no § pointers. | Abstract | 200 |
| 1 Introduction | Why unbinned, multi-observable unfolding; the three questions and their short answers; how the note is organized. | §1, exec summary | 1,000 |
| 2 Data, simulation and method | Sample, selection, simulation; OmniFold in brief; the estimator configurations as ONE table (Tables 4 and 6 merged); detail to App. A. | §§2–3 | 3,000 |
| 3 Reproducing the MINERvA measurement (Q1) | The 2D result against the published result and binned IBU; its uncertainty (one budget table); its validation (closure, held-out tunes, coverage), all in one place. | §6, with the 2D parts of §§4–5 | 3,500 |
| 4 Extending to five observables (Q2) | One progression: (E_avail, q3) → W and the (E_avail, W) plane → the sixteen five-observable cells → the calibrated generator tests. | §§7, 8, 9, 11 | 6,000 |
| 5 What the validation shows (Q3) | One home for every test that limits a result: fake-data bias, rounding stability, the prior retained, coverage in 2D, 5D and the sixteen cells, the IBU comparison. One test table. | §10, the validation parts of §§5, 9, 12, Apps. A–B | 4,000 |
| 6 Results and their validity; outlook | One table, one row per result: what is reported, what is validated, the main limit, where tested. A short outlook. | §§12–13, Table 37 | 1,200 |
| App. A Statistical methods | Covariance construction, tests and their calibration, condensed. | Apps. A–B | 5,000 |
| App. B Background subtraction | Negative-weight injection. | App. C | 2,000 |
| App. C Further studies | Detector-response closure; extended fiducial (preliminary). | Apps. D, J | 1,000 |
| App. D Release package and code | Including terminology. | Apps. G–H | 1,200 |
| App. E Development history | Choices made after results were seen; stops and reruns. | App. I | 2,500 |
| App. F How the numbers and statements are checked | Condensed; a claim-type → check table. | App. K | 1,500 |

Cut or moved to the records document (not deleted from the repository): the executive summary (absorbed by §1 and
§6), the reader's guide (the outline itself guides), the what-is-measured box (becomes §6's table), the
dimensionality survey (App. E, one sentence in §1), point-cloud work (App. F, one sentence in App. E), long procedural
passages that remain after the history cut.

## What protects the claims (code, not prose reads)

- The limitations register: all 93 rows of limitations-export.tsv must still be stated, or each dropped row moves to
  the records document with its reason. limitations_export.py --check fails otherwise.
- Numbers: every printed number still comes from values macros or a committed record. The freeze numbers diff runs
  against the current draft; each removed number is listed as removed-with-its-section or as still printing.
- Removed text goes to the records document (main_records), with a move-manifest row, so nothing leaves the repository.
- Model meaning reads only where results are restated in new words: the abstract, §1, each part's opening answer, §6's
  table. Two readers on those; none on verbatim moves or cuts.
- Gemini readability and skim graders once, on the finished draft. Then Joseph's own read.

## Lanes

| Part | Owner |
|---|---|
| Abstract, §1, §6, the structural skeleton | director-helper-3 |
| §2 and App. A | limitation-resolver (method and statistics) |
| §3 (Q1) | director-helper-3 (results), with cov2d (2D validation) |
| §4 (Q2) | limitation-resolver (5D, sixteen cells), journal-editor (generator tests) |
| §5 (Q3) | cov2d |
| Apps. B–F | journal-editor |
| Figures and tables, moved with their content | cov2d |

Order: (1) Joseph approves this outline; (2) helper-3 commits the skeleton: new section files, every existing label kept
so references still resolve; (3) the lanes rewrite in parallel, each against its budget; (4) the director merges each part
on the code gates; (5) the two-reader reads on the restated results; (6) graders, then Joseph's read.
