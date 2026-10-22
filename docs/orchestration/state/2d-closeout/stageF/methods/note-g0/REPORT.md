# Batch 0 report: one glossary for the analysis note

**Worktree** `S/wt-note1`, branch `stageF/note-register-g0-20261021`, base `38a53a53` (uncommitted; no git state was
touched). **Work directory** `S/wt-note1-work/`. `S` = the session scratchpad.

## 1. What was done

- **Inventory** (`glossary-inventory.md`, `scan_terms.py`): 57 project-internal terms, counted in the printed text of
  the 21 editable files.
- **Glossary** (`GLOSSARY.md`): for each term, its meaning (checked in the note, App. G or the record it cites),
  one plain replacement (or one per context), and whether it is a status that must survive. The status terms (A1-A9)
  keep their distinction in plain words: "used in this note", "computed but not used for any result in this note",
  "reported but not used for the decisions", "predeclared".
- **Application** (`apply_glossary.py`): 192 explicit edits (after the review fix round) and 1 comment-only edit in 19 files. The edits are not
  regex replaces. Each one is a literal before/after pair, read from the base commit and asserted:
  - it matches exactly once;
  - its numbers, `\ref`/`\cite` targets and value macros are unchanged, unless the edit is flagged with a reason;
  - its count of negation words does not fall, unless flagged;
  - it stays out of the protected spans (the verbatim specification quote, the release paragraph, and
    `main_note.tex` outside the abstract).
  The negation guard caught one of my edits (a heading where "not discharged" became "open"), and that edit was
  corrected. The apply script is deterministic: rerunning it rewrites the same bytes.
- **New table** "Labels used in the repository" in `app_guide.tex`. It is a non-float `tabular`, so no table number
  moves. It holds the labels a reader needs to find objects: `lgbm`/`exact`/`hist`, `purity`/`negweight-refined`,
  `cv`/`mean`, `MNV101_ACTIVE_UNIVERSE`, the July and May sweeps, J28, and VL170/VL172/VL175.
- **Ledger** (`ledger.md`, generated): 190 rows. Each row gives file:line, terms, before, after, a note, and two
  probes: the new text must print and the old text must not. The checker is `check_ledger.py`.

Scope held: no number, claim or scope changed. Every edit with a numeric or pointer exception is flagged in the edit
list with its reason; those reasons are labels dropped (B3, P4, VL1xx, KNOWN_ISSUES rows) or the "1" of "Tune v1".
Dates, history narrative, hedging and chapter-level register were left for the chapter batches.

**Two places where the obvious replacement would have been false.** Both are written out as notes in the ledger
(rows G012 and G179).
- sec_method "It is not adopted": the refined negative-weight treatment *is* used by the generator tests, so this
  became "The quoted central values, including the extended-fiducial value, do not use it".
- app_negweight "the refinement-capacity candidate, which is not adopted": that configuration is the joint-test
  estimator (Table estimators-matrix, row e), so this became "not used for the quoted central values".

## 2. Terms and counts, before and after

Counts are of printed text in the 21 editable files (`scan_terms.py base` vs `scan_terms.py after`; the quote column
is the verbatim specification quote in sec_joint, kept verbatim).

| term | before | after | where it remains (after) |
|---|---|---|---|
| in use | 25 | 0 | -- |
| adopt* (status sense) | 26 | 4 | sec_intro 2, sec_method 1, sec_fps 1 |
| constructed but not adopted / in use | 1 | 0 | -- |
| adoption gate | 1 | 0 | -- |
| quotable | 2 | 0 | -- |
| candidate (covariance/product) | 17 | 10 | sec_5d 4, sec_execsummary 1, sec_experiment 1, sec_systematics 1, sec_3d 1, sec_summary 1, app_statmethods 1 |
| report-only | 6 | 0 | -- |
| frozen | 32 | 0 (+2 in the verbatim quote) | -- |
| re-qualify | 1 | 0 | -- |
| footing / footed | 30 | 0 | -- |
| negweight-refined (label in prose) | 4 | 2 | sec_5d 1, app_guide 1 |
| dump-all | 3 | 0 | -- |
| dump(s) (event-loop output) | 8 | 0 | -- |
| selection-complete | 12 | 0 | -- |
| active-lateral / active-universe | 6 | 0 | -- |
| support-limited | 3 | 0 | -- |
| universe-complete | 1 | 0 | -- |
| J28 | 1 | 3 | app_guide 2, app_negweight 1 |
| VL/OI/KI tracker id | 4 | 3 | app_guide 3 |
| KNOWN_ISSUES | 3 | 0 | -- |
| Stage-1/Stage-2 | 2 | 0 | -- |
| standard-P4 | 1 | 0 | -- |
| Q (2D covariance name) | 1 | 0 | -- |
| B3 label | 1 | 1 | sec_joint 1 |
| FPS (abbrev.) | 2 | 0 | -- |
| cv / mean variant label | 6 | 6 | app_guide 3, sec_5d 2, sec_systematics 1 |
| lgbm / exact / hist (backend names in prose) | 17 | 3 | app_guide 2, sec_method 1 |
| digest | 5 | 0 | -- |
| receipt / receipted | 4 | 0 | -- |
| lane | 1 | 0 | -- |
| gate (process sense) | 4 | 0 | -- |
| discharge | 2 | 0 | -- |
| ledger | 1 | 2 | app_guide 1, app_negweight 1 |
| NONQUOTABLE | 1 | 0 | -- |
| the design record | 1 | 0 | -- |
| self-validated | 1 | 0 | -- |
| campaign's | 1 | 0 | -- |
| contract | 1 | 0 | -- |
| sibling | 1 | 0 | -- |
| these bytes / this object | 5 | 0 | -- |
| rollup | 7 | 0 | -- |
| omnifile | 1 | 0 | -- |
| headline (as jargon) | 7 | 3 | app_landscape 2, sec_3d 1 |
| anchor | 6 | 0 | -- |
| home(s) | 2 | 0 | -- |
| truth-tree authoritative / invariants | 3 | 0 | -- |
| record-only | 4 | 0 | -- |
| replay | 6 | 0 | -- |
| launcher | 3 | 0 | -- |
| MnvTune | 6 | 0 (+2 in the verbatim quote) | -- |
| exact-split (kept term) | 34 | 42 | app_statmethods 14, sec_method 6, sec_systematics 5, sec_results 5, app_negweight 3, sec_execsummary 2, sec_validation 2, app_guide 2, sec_3d 1, sec_fps 1, sec_summary 1 |
| CVUniverse:: | 6 | 6 | sec_3d 4, sec_eavailw 2 |
| hXSec | 3 | 3 | sec_results 3 |
| --bkg-mode | 2 | 2 | app_guide 1, app_negweight 1 |
| App. G tag pointer (kept) | 29 | 30 | app_negweight 6, sec_systematics 5, sec_validation 5, app_statmethods 4, sec_method 2, sec_3d 2, sec_eavailw 2, sec_5d 2, sec_joint 1, app_statmethods_nd 1 |

Rows marked "kept" or "status sense" still count legitimate uses:
- the 4 remaining `adopt*` are plain English ("most widely adopted method", "we do not adopt that recommendation",
  "we adopt two-tier reporting"), (the ambiguous use of Q1 is now "LightGBM", review S10);
- the 10 remaining `candidate` are the restored "candidate split-varied band" (review S3, Q11), estimator candidates, "neutrino candidate", "candidate model changes", and one in
  the protected release paragraph;
- the 3 remaining `headline` mean a measurement's main result.

In the built PDF of the whole note, outside Apps. G-J, the only remaining hits for these terms are:
- "frozen V", twice, in the verbatim quote;
- "Marginal anchors" in the result-status table, `result_status_rows.tex`, which the paper shares and which is
  outside this batch (Q5);
- "(a) anchor ratio" inside a figure image (Q6).
(The PDF grep for "in use" also matches the words "chain uses"; those hits are not the term.)

## 3. Files changed

`git diff --stat` (base 38a53a53): 19 files, 222 insertions, 324 deletions. Edits per file:

| file | edits | file | edits |
|---|---|---|---|
| main_note.tex (abstract) | 1 | sec_joint.tex | 32 |
| sec_execsummary.tex | 2 | sec_fps.tex | 6 |
| sec_intro.tex | 3 | sec_summary.tex | 4 |
| sec_experiment.tex | 5 | app_guide.tex | 1 (label table) |
| sec_method.tex | 10 | app_statmethods.tex | 33 |
| sec_systematics.tex | 13 (+1 comment) | app_statmethods_nd.tex | 7 |
| sec_validation.tex | 6 | app_negweight.tex | 29 |
| sec_results.tex | 2 | app_response_mismatch.tex | 5 |
| sec_3d.tex | 13 | | |
| sec_eavailw.tex | 3 | | |
| sec_5d.tex | 15 | | |

**Not touched:**
- app_landscape.tex and app_pet_pointer.tex (no change needed);
- Apps. G-J, the paper, primer, PET note, `values*.tex`, figures, bibliographies, `preamble.tex` and the build
  scripts;
- the acknowledgments, AI-use, funding and `\pubhold` text, and the release paragraph.

**Diff readability.** A changed span that crossed source line breaks is now one line, which makes the line diff
coarse. `git diff --word-diff` reads cleanly, and the ledger gives each change as a before/after pair.

**Structure.**
- No section or label was added, removed or reordered. The paragraph heading in app_guide is unnumbered.
- Three titles changed text only:
  - 10.3 "...and the frozen design" became "...and the predeclared design";
  - 9.6 "The five-axis covariance in use..." became "...used in this note...";
  - C.6, C.7 and C.8 (appendix subsection titles): "footing" became "background treatment".
- Every `\newlabel` number in main_note.aux is identical to the base build (all 205 labels).
- The paper, primer and PET-note text is byte-identical to the base build. The paper's `xr-hyper` pointers therefore
  resolve to the same numbers.
- main_note grew from 136 to 138 pages, from longer phrasings and the label table. The introduction still starts on
  p. 8, so the executive summary and table of contents did not move.

## 4. Every place an internal label was kept, and why

| label | where | why |
|---|---|---|
| App. G tag pointers `(App.~\ref{app:provenance}, \texttt{tag})` | 30, in sec_method (2), sec_systematics (5), sec_validation (5), sec_3d (2), sec_eavailw (2), sec_5d (2), sec_joint (1), app_statmethods (4), app_statmethods_nd (1), app_negweight (6) | the routed form `check_body_pointers.py` requires; it is the only route from a body claim to its record. Count 29 -> 30 because the KNOWN_ISSUES row 92 became the tag `rvp1pi`. Q3. |
| `CVUniverse::GetEAvailableTrue()`, `NewEavail()`, `Getq3True()`, `RecoQ3()`, `GetTrueExperimentersW()`, `RecoW()` | sec_3d (4), sec_eavailw (2) | the sections say the observable definitions *are* these functions' code; now one parenthetical each |
| `hXSec2D`, `hXSec_pt`, `hXSec_pz` | sec_results | they say which stored errors the figure draws; merged into one parenthetical |
| `negweight-refined` | sec:val-negweight (first use); label table | the mode name in the release and code |
| `--bkg-mode` | app_negweight (first use); label table | the option whose absence identifies the old unfolds' mode |
| `cv`, `mean` | sec_systematics, sec:eavailw-adopted (first uses); label table | the text says the variant must be read from the file's metadata, which uses these labels |
| `exact` | sec:method-config, where the backend is defined; label table | definition of the label |
| `MNV101_ACTIVE_UNIVERSE`, `--add-norm 0` | app_statmethods (one parenthetical each); label table (the first) | the event-loop mode and rollup option a reproducer must set |
| MAT classes (`MnvVertErrorBand::CalcCovMx`, `MnvH1D::GetTotalErrorMatrix`, `SetUnivWgts`, ...) | App. A.2.6 (sec:minerva) | that subsection's subject is MAT's implementation |
| NumPy calls (`np.linalg.pinv`, `np.cov(...)`, `default_rng().poisson`) | App. A | they define the estimator and inversion conventions exactly |
| J28 | app_negweight parenthetical; label table | App. J cites "J28" products; the reader needs the key |
| VL170, VL172, VL175 | label table only | App. J's rows and one heading use them |
| July sweep, May sweep | body; label table | names of two datasets that must be told apart |
| `MnvTune`, "frozen V" | verbatim specification quote (sec_joint) | verbatim by design; the note brackets editorial text there already |
| "candidate data package" | sec_summary, release paragraph | protected release text |
| universe names (`MaCCQE:0`, `2p2h:0`, `Flux:23`, `MaRES_0`, `NormDISCC`, `LowQ2_1`/`HighQ2_1`) | sec_systematics, sec_joint, App. A, App. C | GENIE/MAT knob names, needed to identify the universes tested |

## 5. Open questions

- **Q1.** app_negweight, sec. "Measured size": "At full statistics with the adopted estimator on 2D ME FHC" is left
  unchanged. The same appendix says the 2D comparison used the `hist` backend, which differs from the quoted
  LightGBM estimator. So "adopted" may mean the estimator of this comparison or the estimator used for results, and
  I cannot tell which from the text. The author should say which.
- **Q2.** app_negweight: I read "the ledger-verified central value from that gated battery" as "from that battery,
  which passed the analysis's validation checks and is recorded with them". Please confirm that "gated" means the
  battery passed its checks.
- **Q3.** App. G tag pointers (30) stay in the routed form. If App. G is removed, every one needs a new route. If it
  stays, moving them to footnotes would lift most of the BOOK complaint without losing the route. This depends on
  the author's pending decision about Apps. G-J.
- **Q4.** sec_joint, first paragraph, says "The tests evaluate simple hypotheses about five predictions". The section
  and the exec-summary source comment call the nulls *hybrid*, and that comment says "'Simple hypotheses' was
  wrong". This is a claim, so I did not change it. Needs a content decision.
- **Q5.** `result_status_rows.tex`, which the paper shares, prints "Marginal anchors agree" in the note's result-status
  table. The glossary replacement is "marginalization checks agree". It is outside this batch because the paper
  shares the file.
- **Q6.** The figure `fps_pilot_compare_MEFHC` has the panel label "(a) anchor ratio" baked into the image. The caption
  now reads "ratio to the control". Changing the image needs a figure regeneration.
- **Q7.** Apps. G-J still use the old vocabulary: "adopted covariance", "footing", "J28", VL rows, "frozen",
  "selection-complete", "Q". After the author's decision about those appendices, the glossary should be applied to
  whatever stays, or the body and appendices will use two vocabularies. App. I (`app_codebase.tex`) also defines
  "seedscan" and "omnifiles".
- **Q8.** "five-axis" (21 uses) and "five-dimensional" (38) are synonyms. I recommend that the chapter batches use
  "five-dimensional", as the paper does. "Scalar-5D" is redundant now that PET has left the note.
- **Q9.** "July sweep": I did not add the year, which the editable text does not state.
- **Q10.** origin/main has advanced from 38a53a53 to 58fe8a61 (#211, register round r13). That change touches only
  `paper_body.tex`, which this batch does not edit, so the two do not overlap. `swallowed_text.py` reports
  "flagged 0" against both origin/main and 38a53a53.

## 6. Check outputs (quoted)

Hyphenated-compound scan used for the inventory (pass 2):

```
python3 - <<'PY'   # in S/wt-note1-work; prints the 400 most frequent hyphenated compounds of the printed text
import re, collections; from pathlib import Path
c = collections.Counter()
for f in Path("files.txt").read_text().split():
    t = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in Path("base", f).read_text().splitlines())
    t = re.sub(r"\$[^$]*\$", " ", t); t = re.sub(r"\\[a-zA-Z]+", " ", t)
    c.update(w.lower() for w in re.findall(r"\b[A-Za-z]+(?:-[A-Za-z0-9]+)+\b", t))
print(" ".join(f"{w}:{n}" for w, n in c.most_common(400)))
PY
```

All checks, from `checks.out` (after the review fix round, section 8):

```
$ python3 apply_glossary.py $S/wt-note1 && python3 apply_s11.py $S/wt-note1   (run before the build)
APPLY :: PASS (192 edits and 1 comment-only edit(s) in 19 files)
S11 :: PASS (applied at docs/analysis-note/sec_joint.tex:9-10)

$ python3 check_ledger.py $S/wt-note1 ledger.md
ledger rows 192, probes 383, failures 0
$ python3 check_ledger.py $S/wt-note1 S11.md
ledger rows 1, probes 2, failures 0
$ python3 check_ledger.py $S/wt-note1 ledger.md --self-test
LEDGER SELF-TEST :: PASS (2 planted bad probes, rows ['G001', 'G097'], both fail; nothing else fails)
$ planted: G001 probe "10%" -> "11%"
G001 main_note.tex:100: NOT FOUND in main_note.tex: 'satisfies the predeclared 11\\% criterion.'
ledger rows 192, probes 383, failures 1
rc=1
$ apply_glossary.py variant whose B3 edits touch the label (negative test of the new protected span), --dry-run
APPLY :: FAIL
  E103 sec_joint.tex: edit touches a protected span
  E104 sec_joint.tex: edit touches a protected span
  E105 sec_joint.tex: edit touches a protected span
rc=1

$ python3 $S/tools/swallowed_text.py $S/wt-note1 origin/main
flagged 0
$ python3 $S/tools/swallowed_text.py $S/wt-note1 38a53a53
flagged 0

$ bash $S/plain-language/build_copy.sh note-g0 $S/wt-note1   (font-shape warnings removed)
build_all rc=0  log=S/plain-language/builds/note-g0/build.log
  OK   pet_note.pdf written by this run; no unresolved references in pet_note.log after 1 latexmk invocation(s):
SELF-TEST :: PASS
RESULT :: PASS :: head=unknown tree=unknown scope=? (tree_state.py helper not found) mode=strict products=main_note.pdf@sha256:3a95b0a3c816521c9a90bf66c15ec26b74b1bc8941fe40e10f79a4c222b62605(fresh),pet_note.pdf@sha256:80ceb7f0504238f35f6cfe964049317ab7517c008
  gzip receipt: PASS (equal to plain=True, missing raises=True)
SELF-TEST :: PASS (18 perturbations rejected)
SEC4-RECEIPTS :: PASS (15/15)
main_note pages=138
main_paper pages=13
main_primer pages=15
pet_note pages=26
BODY-POINTERS SELF-TEST :: PASS (24 cases: App. G silent; 8 patterns fire in a body file and in a nested body file; a macro-printed digest fires; 6 legitimate forms silent)
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
main_note: undefined=0  ??=0
main_paper: undefined=0  ??=0
main_primer: undefined=0  ??=0
pet_note: undefined=0  ??=0
$ pdftotext, base build (38a53a53) vs this build
main_paper: identical
main_primer: identical
pet_note: identical
$ diff of every \newlabel number in main_note.aux, base build vs this build
     205 labels: identical numbers
$ B3 label, worktree vs base, byte compare
B3 label occurrences: base 1, worktree 1, built copy 1 (byte-identical string)
```

The base build (before any edit, `note-g0-base`) also passed: build_all rc=0, RESULT PASS, BODY-POINTERS PASS,
SEC4-RECEIPTS 15/15, main_note 136 pp.

## 7. Reproduce

(Corrected by the director after the re-review: the S11 step and the counts.)

```
cd S/wt-note1-work
python3 apply_glossary.py S/wt-note1          # writes the 19 files from base 38a53a53 and regenerates ledger.md
python3 apply_s11.py S/wt-note1               # S11 (separate, reversible with --revert); apply_glossary.py alone UNDOES it
python3 check_ledger.py S/wt-note1 ledger.md  # 192 rows, 383 probes, 0 failures
python3 check_ledger.py S/wt-note1 S11.md     # 1 row, 2 probes, 0 failures
python3 check_ledger.py S/wt-note1 ledger.md --self-test
python3 scan_terms.py base ; python3 scan_terms.py after   # counts (after/ = copy of the edited files)
bash S/plain-language/build_copy.sh note-g0 S/wt-note1
python3 S/tools/swallowed_text.py S/wt-note1 origin/main
```

## 8. Review fix round (REVIEW.md, verdict ADOPT-AFTER-FIXES)

All findings were applied in `apply_glossary.py`, except S11, which is in `apply_s11.py` / `S11.md`. Each was checked
against the source the reviewer cites. Ledger ids were renumbered: G030 was withdrawn, and B1 and S10 add rows. The
ledger now has 192 rows; S11 has its own one-row table in S11.md.

| finding | worktree file:line | change |
|---|---|---|
| B1 | sec_joint.tex:733-734 | verbatim label restored byte for byte (also a protected span in apply_glossary.py, with a post-check that fails if the label is not present exactly once as in the base); a plain explanation follows it |
| S1 | sec_joint.tex:499 | "the power sets as evaluated for the decisions" |
| S2 | sec_joint.tex:534, :574, :540 | "the variant shifts of the primary evaluation" (twice); "the evaluation before recovery" (same sense) |
| S3 | sec_systematics.tex:518 | "candidate split-varied band" restored (edit withdrawn); tension with "the band used in this note" is Q11 |
| S4 | sec_fps.tex:79 | "not the full quoted band" |
| S5 | app_negweight.tex:273 | "... are designated different background treatments" |
| S6 | app_guide.tex:34 | three option values: purity, negweight, negweight-refined |
| S7 | app_statmethods.tex:28 | "the superseded 50-replica bootstrap"; "The 300-replica bootstrap" |
| S8 | app_negweight.tex:269 | "recorded in the validation ledger with its passed published-region check against the control" |
| S9 | sec_method.tex:73 | "The quoted central values and uncertainties, including the extended-fiducial value, do not use it" |
| S10 | app_negweight.tex:281, :286 | "with LightGBM, the estimator of the quoted 2D central value"; "Real-data totals (histogram backend)" |
| S11 | sec_joint.tex:10 | "hybrid null hypotheses ... (\S\ref{sec:joint5d-design})": separate, see S11.md |
| N1 | sec_joint.tex:250, :443 | "the stop set by its/the predeclared rule" |
| N2 | sec_fps.tex:88 | "MINERvA Tune~v1/bare-GENIE" |
| N3 + reg. 8 | sec_systematics.tex:496 | the paragraph opening is split: the two event-loop modes, then the production choice, then the status; "single-pass" is explained |
| N4 | sec_method.tex:117 | "with its run configuration recorded" |
| N5 | app_statmethods_nd.tex:172 | "... not replace the decision to use it" |
| N6 | app_statmethods.tex:199 | "run with one universe active at a time" |
| N7 | app_guide.tex:32 | lgbm row adds the 3D-5D central values and the joint-test estimator |
| N8 | GLOSSARY.md | A.2.6 |
| reg. 1 | app_negweight.tex:368 | heading "Background treatment chosen, its obligation not yet met; covariance choice separate."; "removes one blocking decision and leaves every other precondition ... in place" |
| reg. 2 | sec_joint.tex:333, :443, :477, :540, :720 | "for reporting only (outside the decision rule)" once, then "for reporting only" |
| reg. 3 | sec_joint.tex:717, :722 | "original Holm position(s)" |
| reg. 4 | sec_method.tex:317 | "stored lower-dimensional reference extractions" |
| reg. 5 | sec_experiment.tex:80-82 | "The systematic-universe trees also carry every universe's weight and each lateral band's shifted observables (in MAT's terms, ...)" |
| reg. 6 | sec_joint.tex:538 | "which only that run has checked" |
| reg. 7 | app_negweight.tex:256 | "Neither of the two possible job scripts ..." |

Open questions Q1, Q2 and Q4 are answered by the review (S10, S8 and S11). New: **Q11.** sec:uq-higherdim calls the
split-varied ML band a "candidate" (a status set in commit 6964af37), and the next sentence says it dominates "the
band used in this note". The author should say whether this band is a component of the five-axis covariance used.
