# Plan: move the record-keeping appendices (Apps. G–J) out of the posted analysis note

Read-only plan. No worktree was edited, nothing was committed, no one was contacted.

**Governing record.** `docs/orchestration/DECISION-20261021-joseph-da-and-note-records.md`, item 2 (lines 44–61), and
the director's reading at lines 47–53.

## What was measured, and on which tree

- **The tree.** `S/wt-da` is a shared, live worktree. During this session another lane committed `f60b5c61` ("Record
  Joseph's third decision") on top of `58fe8a61`, and it has two files staged: `app_release.tex` and `main_paper.tex`,
  which hold the Data availability change under decision item 1.
- **The snapshot.** Every number below is measured on a frozen snapshot: `git archive f60b5c61` with the two staged
  files overlaid, at `S/notes-records/snap/`, plus `KNOWN_ISSUES.md` and `VALIDATION_LEDGER.md` from the same commit.
- **The snapshot is now a commit.** Before this plan was finished, the other lane committed the staged files as
  `abd93f36` ("Adopt the shorter Data availability paragraph"). Both files in `abd93f36` are byte-identical to the
  snapshot (`cmp`), so the snapshot is exactly `abd93f36`.
- **Line numbers.** File:line references are to that snapshot. The staged `app_release.tex` adds 6 lines (12–17) that
  `HEAD` does not have.
- **The build.** The four-PDF scratch build is a copy of the snapshot at `S/notes-records/build/`. `latexmk -pdf` was run
  once each for `main_note` and `main_paper`. Both exited 0, with no unresolved references and no multiply-defined
  labels.
  - `main_note.pdf` has 136 pages.
  - `main_paper.pdf` has 13 pages.
- **Measurement tools,** all read-only, in `S/notes-records/tools/`:

  | tool | what it measures |
  |---|---|
  | `outline.py` | per-section texcount word counts |
  | `refs_into.py` | every `\ref`, `\napp` and `\nsec` into Apps. G–J |
  | `gtags.py` | App. G tag pointers |
  | `macros.py` | values macros used by Apps. G–J |
  | `struck_elsewhere.py` | struck literals against the trackers |
  | `check_note_records.py` | the inventory and probe proposed in §6 |

- **Word counts.** Unless stated otherwise, counts are `texcount -1 -sum`: text, headers and captions. texcount
  undercounts `tabular` cells, so the App. H identity table shows 21 words for 6 rows.
- **Page ranges,** from `main_note.aux`/`.toc`:

  | App. | label | pages |
  |---|---|---|
  | G | `app:provenance` | 108–112 |
  | H | `app:release` | 112–116 |
  | I | `app:codebase` | 116–117 |
  | J | `app:history` | 117–131 |

  References start on p. 131. Apps. G–J are about 23 of 136 pages, and G+J about 18.

---

## 0. Short answer to Joseph's question

**Is the existing archival system already good enough?** Partly. The answer differs by piece.

| piece | is the content already recorded elsewhere? | is the existing system enough? |
|---|---|---|
| **App. G** (provenance) | **Yes**, measured: all 30 `\repopath` targets exist at `f60b5c61`, and every `KNOWN_ISSUES` row and `VALIDATION_LEDGER` row G names exists. | **No, for one thing:** the *index* from note claims to records (29 tags, each with a "Cited at" column) exists nowhere else. `CATALOG.md` routes by task and `MANIFEST.tsv` classifies by path. Neither maps a note sentence to its record. |
| **App. H record parts** (identity table, construction/audit record) | **Yes:** the digests, jobs and revisions are in `state/PROJ-20260920-m1-publication-receipt.json`, `VALIDATION_LEDGER.md` and `DECISION-20260920-joseph-adopts-z-cv-…`. | Yes, for content. |
| **App. I record part** (test-suite discipline) | **Yes:** `DRAFT-SPEC-20260921-what-the-pipeline-refuses.md` §2. | Yes, but that record is a DRAFT with its own CITABLE FOR scope. |
| **App. J** (struck values, withdrawn arguments, superseded constructions) | **No.** | **No.** The per-value struck ledger exists only in App. J. The containment gate also derives its struck literals from App. J's `\dead{}` marks and checks them against a rendered PDF. |

App. J in detail:
- The ledger has 39 rows and 97 `\dead{}` bodies, each with its quantity, replacement, reason and record.
- `INDEX-retracted-and-superseded-values.md` holds only 23 of the 64 PDF-coverable struck literals. It was last changed
  on 2026-10-11 (`25720215`), so it predates the 9-row block struck on 2026-10-18. One literal, `3.214` (×10⁻³⁹), occurs
  in no tracker and no orchestration markdown file.
- The verbatim withdrawn passages are recoverable only from git history, at `152ef7a6`, `95d03169^` and `ae198cc1`.

**So the internal ledger cannot simply be "the existing records".** Recommendation: a separately built, never-posted
records document (§5, option C). It holds G, J and the record parts of H and I, moved verbatim. It is built and gated by
`build_all.sh`, and the posted note cites it by tag at a pinned commit.

---

## 1. What Apps. G–J contain

The four files total 1,479 + 1,608 + 474 + 5,504 = **9,065 texcount words**. In `wc -w` source tokens, that is 1,490,
1,929, 468 and 6,896.

### App. G — `app_provenance.tex`, 262 lines, 1,479 words

| lines | unit | words | class |
|---|---|---|---|
| 1–28 | intro, 4 paragraphs: why records are collected; "not the reproduction path" (routes to H); "provenance, not evidence"; tag conventions. Line 10 renders the visible hold `\depositsnapshot`. | 274 | RECORD |
| 29–103 | `tab:prov-paths`: **24 tags** (tag, cited at, record path) | 203 | RECORD |
| 104–215 | "see below" descriptions for **11 tags**: `coverage-fixed-truth`, `coverage-toys`, `flux-repair`, `z-cv-record`, `joint-5d`, `variance-sources`, `negweight-hpss`, `oi6-oi8-oi126`, `fps-battery`, `z-projection`, `z-conditioning` | 783 | RECORD |
| 216–251 | `tab:prov-trackers`: **5 tags** (`rvp1pi`, `flux-index`, `statband-retest`, `pot-ratio`, `bkg-mode-pins`) | 132 | RECORD |
| 253–262 | ¶ "The identity of the five-axis covariance" (a change log of the deposit pass) | 87 | RECORD |

G defines 29 tags, 30 `\repopath`s and 3 labels.

### App. H — `app_release.tex`, 287 lines staged, 1,608 words

| lines | unit | words | class |
|---|---|---|---|
| 1–9 | intro. Line 5, "App. G lists the supporting internal records", is a record pointer. | 48 | MIXED |
| 10–41 | ¶ Release status: RC7, what it reproduces, not deposited. Lines 15–17 are the decision-1 D-2 sentence. | 191 | READER |
| 42–72 | H.1 `app:release-scope`, "What today's reader can and cannot recompute". It holds the paper's Data availability facts: 2,374/1,885/489 AnaTuples and `\cite{AnaTuplePreservation2026}`. | 253 | READER |
| 73–121 | H.2 `app:release-schema`, the release schema. Item 7 (line 107) points to G `flux-repair`; item 8 (lines 110–115) states which identities are fixed. | 326 | READER (two pointers to fix) |
| 122–173 | H.3 `app:release-identities`, the identity table: 6 rows of digests, jobs and revisions for `C_Z`, the `z-mean` sibling, `C_EW`, `M`, the row index and the central values | 21 (table cells uncounted) | RECORD (fixed-identity table) |
| 174–193 | H.3 continued: the bin edges of all five axes ("the one thing a reader cannot recover from a digest") | 124 | READER |
| 194–236 | H.4 `app:release-example`, one minimal projection example | 290 | READER |
| 237–243 | ¶ Undeclared acceptance field (a requirement on the package) | 53 | READER |
| 244–287 | H.5 `app:release-audit`, the construction and audit record: Adoption (100), Assembly and centering (75), Projection (39), Conditioning (74) | 302 | RECORD (audit, implementation refusals) |

**Check against the lint.** A probe lint over the posted appendices found 12 hits in App. H. All 12 sit in the two
RECORD ranges, at lines 136–166 and 263–268. The READER ranges have 0.

### App. I — `app_codebase.tex`, 72 lines, 474 words

| lines | unit | words | class |
|---|---|---|---|
| 1–31 | the four components (event loop, omnifiles, driver, engine) and the PET code location | 159 | READER (where the code lives) |
| 32–38 | the `seedscan` code name and the training-seed variation. Line 36 points to G `variance-sources`. | 40 | MIXED |
| 39–54 | ¶ "Code identifiers cited in the note" (paths, tree names, figure producers) | 67 | READER; see open question Q3 on "markers" |
| 55–72 | ¶ "Test-suite discipline: what the pipeline refuses to do" (five rules) | 208 | RECORD (implementation refusals) |

### App. J — `app_history.tex`, 772 lines, 5,504 words. All of it is RECORD.

| lines | unit | words |
|---|---|---|
| 1–22 | intro (verbatim provenance: `152ef7a6`, `95d03169^`) | 225 |
| 23–88 | J.1 `app:history-errata`, the struck-values longtable: **39 data rows**, 3 dated blocks | 1,288 |
| 89–173 | J.1.1, the struck entries in context: 7 paragraphs | 453 |
| 174–317 | J.2 `app:history-withdrawn`, withdrawn arguments: 11 paragraphs, including the 401-word `app:history-combine` quote | 1,092 |
| 318–421 | J.3.1 `app:history-vl175`, the VL175 construction | 822 |
| 422–497 | J.3.2, the historical 3D scan and budget (`sec:3d-syst`, `fig:3dfullcov`, `fig:3dbands`) | 470 |
| 498–539 | J.3.3 `sec:eavailw-cov` and J.3.4 `app:history-5dcandidates` | 314 |
| 540–638 | J.3.5, disclosures shortened in the body: 4 superseded-caption figures | 540 |
| 639–772 | J.3.6 `app:history-prerepair`, pre-repair values | 255 |

Other contents of App. J:
- 97 `\dead{}` bodies. They yield 64 PDF-coverable literals and 8 bodies that only the source check covers.
- 9 `\href` links to preserved graphics: 7 at `3892e769` and 2 at `ae198cc1`. App. J calls no `\includegraphics`.
- Lines 656–749 are a 94-line source-only comment block that renders nothing. It is the reduction record for the corner
  ratios, moved from `sec_eavailw.tex`.

---

## 2. What else already records the RECORD content

| RECORD unit | where the repository already holds it (measured at `f60b5c61`) | only in the appendix |
|---|---|---|
| G `tab:prov-paths`, `tab:prov-trackers` | **30 of 30** `\repopath` targets exist (`git ls-tree`). KNOWN_ISSUES rows 81, 82, 83, 84, 85, 91, 92 and J36 exist. The cited VL rows exist: VL35, VL38, VL145, VL156, VL160, VL162, VL169, VL170, VL172, VL175, VL16 and VL17; "FPS MEFHC battery" is at `VALIDATION_LEDGER.md:1611`. | **The claim → record index:** 29 tags × "Cited at" |
| G "see below" (11 tags) | 17 identity strings were spot-checked. **13** are in the record G cites, for example `4f5a613f`, `466b427b` and `b9604502` in `RECORD-20261005-…` and `00009056` in `RECORD-20261006-…`. The other **4** are elsewhere in the repository: `0f04abce` and `58655509` in `VALIDATION_LEDGER.md`, `cf8a4a6` in `KNOWN_ISSUES.md` and `OPEN_ITEMS.md`, and "producing job" in 18 files. This was a spot check, not every sentence. | The curated one-paragraph summaries |
| G ¶ five-axis identity | `state/2d-closeout/stageF/methods/METHODS-IMPLEMENTATION.md` §9: "The z-cv and 2D digests moved from the body to Apps. H and G" | — |
| G visible hold `\depositsnapshot` | It renders **only** in G (`app_provenance.tex:10`; `main_note.tex:45` defines it). | The posted note's only "[snapshot identifier pending deposit]" |
| H.3 identity table | `state/PROJ-20260920-m1-publication-receipt.json` has `64fec490`, `9eb9d216`, `acceptance_question`, `835828bf` and `3d7465f6`. `VALIDATION_LEDGER.md` has `0f04abce` and `58655509`. `DECISION-20260920-joseph-adopts-z-cv…` has `fb9ec356` and `58454524`. | — |
| H.5 audit record | `DECISION-20260920-…`, `EVIDENCE-20260920-…`, `CORRECTION-20260920-…`, `PLAN-20260918-…` §16.1a and VL145, all cited from G. Not checked sentence by sentence. | — |
| I test-suite discipline | `DRAFT-SPEC-20260921-what-the-pipeline-refuses.md` §2: five rules from 1,061 tests. It mentions "segfault" 3× and "argparse" 1×. | The note's phrasing |
| J.1 struck table | `INDEX-retracted-and-superseded-values.md` has 36 table rows and **23 of 64** literals, last changed 2026-10-11. `VALIDATION_LEDGER.md` carries 32 of 64 as values, not as struck values with a reason. | **The 39-row struck ledger.** The 2026-10-18 block. `3.214` appears in no tracker and no orchestration markdown file. |
| J.1.1–J.3 verbatim passages | Git history: `152ef7a6` (referenced nowhere outside the note), `95d03169^` and `ae198cc1` | The curated, current selection |
| J preserved graphics | The files exist at `3892e769` and `ae198cc1`. | The list of 9 links and their historical captions |
| J comment block 656–749 | Only in `app_history.tex`, as comments | All of it |

**Content recorded only in Apps. G–J:**
1. the 29-tag claim → record index;
2. the 39-row struck ledger and its 2026-10-18 block;
3. the curated verbatim passages and the list of preserved graphics;
4. the 94-line corner-ratio comment record;
5. the `\depositsnapshot` hold.

The plan moves all five verbatim, so none is lost. It does not try to re-home them into the existing records.

---

## 3. What reads Apps. G–J

### Builds

| build | dependence on Apps. G–J |
|---|---|
| `main_note` | `\input`s them at `main_note.tex:182–185`. Their letters G–J follow 6 numbered appendices; `app_guide` is `\section*`. **84** printed references from the rest of the note land on labels that would move to the records (§4). |
| `main_paper` | `\externaldocument[N-]{main_note}` (`main_paper.tex:26–28`), with `\napp`/`\nsec` defined at `paper_body.tex:23–24`. **2 references into H:** `\napp{app:release}` at `main_paper.tex:158` and `:166` (staged DA text). None into G, I or J. The paper's other `\napp`s are `app:negweight` (App. C) and `sec:joint5d-fwer` (App. B), which come before G and keep their letters. The scratch build's `pdftotext` prints `App. B`×1, `App. C`×1 and `App. H`×2. No printed paper text names a letter literally; the only literal "App. G/H/J" strings in sources are in comments (11 hits). |
| `main_primer` | No reference into the note (no xr). `primer_body.tex:268` is a comment: a clause was dropped because "the chain is in the note's App. history". After the move, that chain is only in the records (Q4). |
| `pet_note` | Its `app:provenance` and `app:history` labels are its **own** files, `app_provenance_pet.tex:5` and `app_history_pet.tex:7`. `sec_pet`, `app_cstat` and those files point only to them. It does not depend on main-note Apps. G–J. It has the same G/J structure (Q1). |

### Gates in `build_all.sh`

| gate | lines | reads Apps. G–J? |
|---|---|---|
| (5) body-pointer lint `check_body_pointers.py` | `build_all.sh:113–115` | **No.** Its population is the body only: `main_note.tex` from `\title` to `\appendix` (`check_body_pointers.py:113–140`). It does not *require* App. G pointers; it forbids internal pointers in the body. It *names* App. G as the place they go: the docstring at :5–8, the routed-form silent case `(App.~\ref{app:provenance}, \texttt{joint-5d}…)` at :184, and the FAIL text at :251–252. Measured on the snapshot: `BODY-POINTERS :: PASS (0 internal pointers in 17 body files)`. |
| latexmk, marker and log (1–4) | :127–178 | Builds the 4 `targets` (:94). Checks unresolved references and citations (:124). It does **not** check multiply-defined labels; the measured logs have 0 today. |
| struck-value containment `check_dead_containment.py` | :204–205 | **Yes, structurally.** `STRUCK_ALLOWED = {"main_note": "app_history.tex", "pet_note": …}` (:79). The positive control fails if `main_note` has zero `\dead` (:565–569). The struck literals are derived from `\dead` bodies in the closure, resolved through `values.tex` (:563–584). Outward builds are checked against the literals a note PDF was shown to render (:654–697). `BUILDS` is asserted equal to the drivers on disk (:536–543). Removing App. J from `main_note` without a new home fails the build, and also drops all 64 main-note literals from the outward check. The documented route is at :78: "To make a note build strike-free, delete its entry -- it is then checked as outward." |
| Sec. IV receipts `check_sec4_receipts.py` | :212–213 | **No.** It reads only `paper_body.tex` and `values.tex` (:182) and checks macros such as `\uqMedian`. |
| page counts | :216–227 | It iterates over `targets`. |
| `--export-deposit` | :229–274 | It flattens `main_note.tex` and copies the figures in `main_note.fls`. Apps. G–J have no `\includegraphics`. |

### Tests under `docs/analysis-note/`

`test_build_all.py`:
- `TARGETS` is 4 (:39).
- `ResultLineNamesItsObjectTest` hard-codes `main_note` → `app_history` (:589–596).
- `StruckOnlyInHistoryTest` writes a `main_note` that inputs `app_history` (:681–750).
- `UnitRequiredLiteralTest.test_every_key_is_struck_with_its_unit_in_app_history` reads `app_history.tex` (:779–784).
- The 8 mutants do not involve the appendices (:441–455).

`test_check_sec4_receipts.py`: no dependence.

### Values macros (`macros.py`)

| macro | used only in |
|---|---|
| `\covTwoDNodeH` | G |
| `\zcvDigest`, `\zprojDigest` | H.3 |
| `\gbdtFiveBlockMedian`, `\gbdtFiveAdoptTrace`, `\gbdtFiveMeanShift`, `\gbdtFiveCVTrace` | J |

Four more are used by H or J and also elsewhere: `\latBins`, `\zprojCells`, `\fpsSigma`, `\pullFrac` and `\uqPaper`.
`values.tex` stays shared. A records build that inputs it resolves all of these, and so does the containment check's
macro table (:277–281).

### SEC4 receipts

SEC4 does not depend on Apps. G–J.

---

## 4. Pointers into Apps. G–J, by target

Counts are printed `\ref`s, with comments stripped. "Posted appendices" means Apps. A–F plus the parts of H and I that
stay. PET files are excluded because their labels are their own.

| target | from the body | from Apps. A–F | from G/H/I/J (internal) | from the paper | total |
|---|---|---|---|---|---|
| **G** `app:provenance` (+ `tab:prov-*`) | **20**: 19 tagged + 1 roadmap (`sec_intro:136`) | **11**: `app_guide` 1, `app_statmethods` 3, `app_statmethods_nd` 1, `app_negweight` 6 | 11: H 6, I 1, J 2, G 2 | 0 | 42 |
| **H** `app:release*` | **13**: `app:release` 5, `release-audit` 6, `release-identities` 2 | 1 (`app_guide`) | 11 | **2** (`main_paper:158`, `:166`) | 27 |
| **I** `app:codebase` | **5** (`sec_method` 3, `sec_experiment` 1, `sec_intro` 1) | 1 (`app_guide`) | 0 | 0 | 6 |
| **J** `app:history*`, `sec:3d-syst`, `sec:eavailw-cov`, `fig:*` | **22**: `app:history` 15, `history-vl175` 3, `history-5dcandidates` 1, `history-withdrawn` 1, `sec:3d-syst` 1, `sec:eavailw-cov` 1 | **18**: `app_statmethods` 14, `app_negweight` 3, `app_guide` 1 | 33 (2 from G, 31 inside J) | 0 | 73 |

**App. G tag pointers in the body** (`gtags.py`), per tag:

| pointers | tags |
|---|---|
| 4 | `coverage-fixed-truth` |
| 2 each | `rvp1pi`, `statband-retest`, `flux-repair` |
| 1 each | `2d-central-value`, `bin-mapping`, `flux-index`, `coverage-toys`, `q3-excess`, `eavailw-excess`, `response-diagnostic`, `z-cv-record`, `joint-5d` |

- 16 of the 29 tags are cited from appendices only.
- Every one of the 29 tags is cited at least once.
- Across the note there are 40 printed G pointers: 20 in the body and 20 in appendices.

**What breaks if the records leave.** A simulated move (§6) takes G, J, H.3's table, H.5 and I's test discipline out
of `main_note`. That leaves **84 references from the posted note into 22 moving labels: 50 from the body and 34 from
posted appendices.**

| file | breaking references |
|---|---|
| `sec_systematics` | 11 |
| `sec_3d` | 10 |
| `sec_5d` | 10 |
| `sec_validation` | 8 |
| `sec_eavailw`, `sec_intro`, `sec_method` | 3 each |
| `sec_joint`, `sec_results` | 1 each |
| `app_statmethods` | 17 |
| `app_negweight` | 9 |
| `app_release` | 4 |
| `app_guide` | 2 |
| `app_codebase`, `app_statmethods_nd` | 1 each |

The paper has **0** references into moving labels.

---

## 5. Options for the internal ledger, and what each costs

Every option must rewrite the 84 posted-note references and the 3 whole-appendix pointers:
- the roadmap rows `sec_intro.tex:136–137`;
- the "Records" bullet `app_guide.tex:15–19`;
- `app_release.tex:5`.

Every option must also delete or move the superseded VL175 parenthesis that App. A prints unstruck,
`app_statmethods.tex:687–688`: "VL175 0.048 and 0.406; before the flux-constraint repair 0.041 and 0.386". All four
values are already struck in J's table rows, so deleting it loses nothing.

**The citation form, for every option.** The body cites `(Ref.~\cite{NoteRecords2026}, \texttt{<tag>})`.
- This is lint-safe: `\cite` arguments do not print, and tags such as `joint-5d` match no pattern. Every body tag
  already passes the lint today in the `\ref` form.
- There is precedent for a pinned-commit record entry. `technote.bib:983–987` (`ReleaseCandidate2026`, `blob/3892e769/…`)
  and `publication.bib:160–164` (`JointTestRecord2026`, `blob/5f4ec13a/…`) put the URL in `howpublished`, because
  biblatex runs with `url=false` (`technote.bib:989–991`).
- The new entry is `NoteRecords2026`, pinned to a commit on `origin/main`.

**Renumbering, the same for every option.** Once G leaves, H becomes **G** and I becomes **H**.
- The paper's two `\napp{app:release}` then print "App. G". xr resolves this automatically, because `build_all.sh:94`
  builds `main_note` first and `-g` forces a fresh `.aux`.
- The paper's `App. B` and `App. C` are unchanged.
- **Residual risks:**
  - an arXiv or standalone source of the paper must ship the new `main_note.aux` (`main_paper.tex:22–25`);
  - review copies already circulated, and dated records, say "App. H": `r13/REVIEW.md:155,195` and
    `r13/DA-proposal.md:73–101`. These are dated records and are left as they are.
- The `\nsec` references to body sections do not move.

### (A) Delete G and J from the posted build; content goes to existing records plus one new record file

- **Files:**
  - Drop `\input{app_provenance}` and `\input{app_history}` (`main_note.tex:182,185`).
  - Delete H.3's table, H.5 and I's ¶ test discipline from `app_release.tex` and `app_codebase.tex`.
  - Write one new markdown record, for example `docs/orchestration/RECORD-2026MMDD-analysis-note-records.md`. It holds the
    29-tag index with its 11 contexts, the J table (39 rows, 97 struck bodies with math), about 45 J passages, the
    preserved-graphic links and the 94-line comment block.
  - `git rm` the two `.tex` files, so they are not kept as unbuilt duplicates.
  - Add rows to CATALOG and `MANIFEST-overrides`, and regenerate `MANIFEST.tsv`.
- **Gates:**
  - **Containment loses its main-note half.** With no `.tex` carrying the main note's `\dead`, `STRUCK_ALLOWED` keeps only
    `pet_note`. The paper, primer and posted note are then checked only against PET literals, and the 64 main-note struck
    literals stop being checked anywhere. Keeping them requires a new markdown-table parser in
    `check_dead_containment.py`. That parser has no rendered positive control, which is the checker's own design premise
    (:22–27).
  - `UnitRequiredLiteralTest` (:779) breaks when `app_history.tex` is deleted.
  - The lint changes text only.
  - The test harness changes little.
- **Paper risk:** as above.
- **Pointer form:** `NoteRecords2026` → `blob/<sha>/docs/orchestration/RECORD-…md`. GitHub renders it, which is the one
  real advantage.
- **Cost:**
  - About 5,500 words of LaTeX are hand-converted, including 97 strikes and the math.
  - Translation errors are likely, and checking them needs a LaTeX-to-markdown diff tool.
  - J's own claim to be "reproduced verbatim from the note … 152ef7a6" (`app_history.tex:12–17`) is false in markdown.
  - G's "Cited at" cross-references (`\S\ref{…}`) become static text that nothing checks.

### (B) A separately built internal document, `main_records.tex`, never posted, read by the gates

- **Files:**
  - New `main_records.tex`: `\usepackage{xr-hyper}` before `\input{preamble}` (hyperref loads at `preamble.tex:25`),
    `\externaldocument{main_note}`, `values`/`values_inference`, the bib resources, and `\input` of `app_provenance`,
    `app_release_records`, `app_codebase_records` and `app_history`.
  - New `app_release_records.tex` (H lines 122–173 and 244–287, verbatim).
  - New `app_codebase_records.tex` (I lines 55–72, verbatim).
  - `main_note.tex` drops the two inputs.
  - `app_release.tex` and `app_codebase.tex` lose those ranges. The bin edges (174–192) stay in the note under a new label
    `app:release-edges`, because `sec_method.tex:349–350` relies on them.
- **Gates:**
  - `build_all.sh` `targets+=(main_records)`, placed **last**. This follows the precedent at :92–93, so every existing
    target's messages and order stay the same.
  - Records-build check: add a multiply-defined-label pattern to the log check. The current logs have 0, measured on the
    note and paper; the primer and PET note are to be measured.
  - Containment:
    - `BUILDS["main_records"]="records"`, which the on-disk assert at :536–543 forces anyway.
    - `STRUCK_ALLOWED={"main_records": "app_history.tex", "pet_note": …}`, so `main_note` becomes **outward**: the posted
      note is then checked against all 64 literals.
    - `UNIT_REQUIRED` gains 3 keys.
    - One context exemption is needed (measured below).
  - Lint: text only.
  - Tests: `TARGETS`; the two containment test classes; a new test that a `\dead` or a struck literal in `main_note` now
    **fails**.
- **Paper risk:** as above.
- **Pointer form:** `NoteRecords2026` → `tree/<sha>/docs/analysis-note`, noting that `main_records.tex` is built by
  `build_all.sh`.
- **Cost:**
  - A fifth build. The records PDF is estimated at about 20–25 pages from the page ranges; it was not built.
  - An xr dependency from the records doc onto the note. G and J make **180 references into the note** (45 from G and 135
    from J), and xr resolves them with **no edits to the record text**.
  - A reader without TeX sees LaTeX source at the URL.

**Measured consequence of making `main_note` outward.** I checked the PDF text of the current note minus J's pages
(1–116 and 131–136) against the 64 literals, using the checker's own `outward_hit`. **6 hit:**

| literals | what they are | fix |
|---|---|---|
| `0.386`, `0.406` | real: the App. A superseded parenthesis above | delete it |
| `1.008` | coincidence: `\medianBinRatio`, `values.tex:83`; struck as `1.008\%` | `UNIT_REQUIRED` |
| `0.563` | coincidence: the App. A table at `app_statmethods.tex:1003`; struck as `0.563\%` | `UNIT_REQUIRED` |
| `2.26` | coincidence: `sec_systematics.tex:404`; struck as `2.26\%` | `UNIT_REQUIRED` |
| `1.014` | coincidence: "mean weight 1.014", `sec_validation.tex:143`; struck bare, as a χ²/ndf | one declared context exemption, with a test |

The other 58 literals print nowhere in the posted note. The positive control was confirmed: all 64 render on J's pages.

### (C, recommended) Records companion build: option B, refined

This is option B with five refinements:
1. **A verbatim move.** `app_provenance.tex` and `app_history.tex` are not edited. Only `\input` lines move. H and I are
   split by line range.
2. **Tags as the citation key.** The posted note never cites a numbered section of an unposted document, and there is
   no circular aux dependency between the note and the records.
3. **The posted note becomes outward for containment,** as above.
4. **An inventory and probe script** proves that nothing was lost (§6).
5. **The pin is set after merge.** The pin must be on `origin/main` and must contain every cited tag, and code checks
   both.

I considered and rejected two alternatives:
- **C1: one `main_note` source with `\ifRECORDS`.** The deposit export (`build_all.sh:233`) runs
  `latexpand --empty-comments` over `main_note.tex`. That keeps both branches of a conditional, so the deposited source
  would still contain the records. `check_dead_containment.py:9–20` also records why this repository rejects
  build-conditionals for containment.
- **C2: G as a markdown index plus J in a records build.** This creates two homes for one ledger. G's "Cited at" column
  is checkable only while it is LaTeX built against `main_note.aux`, where a removed note section becomes an unresolved
  reference that fails the records build.

---

## 6. Recommendation and implementation plan

**Recommendation: option C.**
- J cannot go to the existing records without losing a checked gate and the verbatim-ness of its own text (§2).
- G's and H/I's content is already recorded, but the index the note's pointers need is not.
- One built, gated, never-posted document holds all of it with zero edits to the record text.

The work goes on a branch from `main` **after** the DA commit `abd93f36` reaches `origin/main`, in a dedicated worktree. `wt-da` is
shared and live. Stage explicit paths only, and pass the session's own git identity on each commit. Every commit ends
green on the five builds. Each `docs/analysis-note/` change is then synchronized to the standalone private
`MINERvA-OmniFold-Analysis-Note` repository (`AGENTS.md:146`).

**Commit 1: `[tools] Inventory the note's record appendices before the move`**
- **Files.**
  - `docs/analysis-note/check_note_records.py`, the draft at `S/notes-records/tools/check_note_records.py`.
  - The frozen base inventory, `docs/orchestration/state/note-records-2026MMDD/inventory-base.json`, which names the base
    sha.
  - A `--self-test` with planted trees.
- **The inventory** is derived, not typed: 27 labels, 20 of them in G or J; 29 tags; 97 struck bodies; 30 paths; 84
  record paragraphs and 20 reader paragraphs; and the App. G pointers, 39 file-and-tag keys counting 43.
- **Checks.**
  - The self-test fires for each of: a dropped `\dead`, a dropped or edited paragraph, a renamed tag, a G or J label left
    in the note, and a lost pointer.
  - It stays silent on a verbatim move.
- **Measured on the draft.**
  - A naive simulated move (records moved verbatim, pointers not rewritten) passes P1–P5 silently and fires P6 36 times.
  - Adding one dropped strike fires P3. A renamed `see below` item fires P5.
  - The silent direction of P6 is **not yet exercised**, because that needs the real rewrite.

**Commit 2: `[note] Move the records out of the posted note into a records build`**

This commit is atomic, because a half-move leaves undefined references. Its contents:

- **The records build.**
  - `main_records.tex` (option B layout). Its title marks it "internal record, not posted". One front-matter sentence says
    that bare section, table and equation numbers are the note's.
  - `app_release_records.tex` and `app_codebase_records.tex`, as verbatim line ranges.
- **The posted note's sources.**
  - `main_note.tex` drops `\input{app_provenance}` and `\input{app_history}`.
  - `app_release.tex` and `app_codebase.tex` lose those ranges. `app_release.tex` gains `\subsection{Bin edges}`
    `\label{app:release-edges}` over its existing list.
- **The rewrites.**
  - The 84 references and 3 whole-appendix pointers are rewritten to the `NoteRecords2026` form.
  - J targets carry the records' heading words, for example "(Ref.~[n], superseded values: the VL175 construction)".
    J's labels do not print.
  - The App. A parenthesis at `app_statmethods.tex:687–688` is deleted.
- **The citation.** `technote.bib` gains `NoteRecords2026`, temporarily at `tree/main`. That is the
  `AnalysisNote2026` precedent, `publication.bib:212–218`.
- **The gates and tests.**
  - `build_all.sh`: `main_records` added to `targets`, the multiply-defined pattern added, and a comment item 7.
  - `check_dead_containment.py`: `BUILDS`, `STRUCK_ALLOWED`, `UNIT_REQUIRED` += {`1.008`, `0.563`, `2.26`} → `%`, the
    `1.014` context exemption, and its docstring.
  - `check_body_pointers.py`: the docstring at :5–8, the silent case at :184, and the FAIL text at :251.
  - `test_build_all.py`: `TARGETS`; `ResultLineNamesItsObjectTest` (`main_records` strikes in `app_history`, `main_note`
    is a clean body); `StruckOnlyInHistoryTest` on `main_records`; and new tests "a `\dead` in `main_note` FAILS" and "a
    struck literal in `main_note.pdf` FAILS".
- **The docs.** `README.md` rows :18, :131–134; `app_guide.tex` "Records" bullet; and the roadmap rows at
  `sec_intro.tex:136–137`.
- **A ledger file,** `records-move-ledger.md`, in `check_ledger.py` style. It has one row per non-mechanical edit,
  each with a probe, for example `R:app_history.tex::\dead{0.406}` for the deleted parenthesis.

The checks for commit 2, each against the delivered files:
1. `bash build_all.sh` exits 0 with 5 targets: 0 unresolved references and 0 multiply-defined labels.
2. Containment:
   - `records.pdf` carries 64/64 (positive control);
   - `note.pdf` 0 of 64;
   - paper and primer 0;
   - PET unchanged.
3. The lint and its self-test pass.
4. `test_build_all.py` passes, and `--mutate` catches 8/8.
5. `test_check_sec4_receipts.py` passes.
6. `check_note_records.py probe <base> <new>` passes P1–P6.
7. `pdftotext` checks:
   - `main_note.pdf` has no "Provenance" or "Superseded values and withdrawn results" section and no G tag table;
   - `main_paper.pdf` prints "App. G" 2× and "App. H" 0×;
   - the H.1 sentence "SHA256 identities for all 2,374" still prints, which the paper's Data availability relies on;
   - page counts are recorded. My estimates from the page ranges are about 118 for the note and 20–25 for the
     records. Report the measured numbers, not these estimates.
8. `--export-deposit` into an empty directory builds, and its text contains no G tag (`coverage-fixed-truth`) and no
   struck literal.

**Commit 3: `[note] Pin the records citation to the merged commit`**
- **Precondition.** Commit 2 has merged to `origin/main`. Pin to that sha, because a branch sha can be rebased away.
- **The check.** It goes in `check_note_records.py`, run from `build_all.sh`, and reports SKIP outside the canonical
  layout, like SEC4 (`check_sec4_receipts.py:31–32`). It requires:
  - the pinned sha is an ancestor of HEAD;
  - `git show <sha>:docs/analysis-note/app_provenance.tex` contains every tag the note cites.
- **The mutation tests.** A pin lacking a tag fails. A non-ancestor sha fails.

**Commit 4: `[orchestration] Record the answer and route the records build`**
- An OUTCOME record answering Joseph's question with §0 and §2.
- A CATALOG task-route row for the records build.
- A `MANIFEST-overrides.tsv` row if it is LIVE, and a regenerated `MANIFEST.tsv` (a coupled generated file).
- **Check:** `generate_manifest.py` reports no diff after regeneration, and `live_doc_indexed.py` passes.

**Commit 5 (optional, needs a ruling): extend the lint to the posted appendices.**
- **Measured.** A probe that lints everything `main_note` inputs finds **39** hits today:

  | file | hits |
  |---|---|
  | `app_statmethods` | 13 |
  | `app_codebase` | 13 |
  | `app_release` | 12 |
  | `app_pet_pointer` | 1 |

- **After commit 2** the count would be about 27, because App. H's 12 leave with its record parts.
- **What it needs.** App. I's 13 are its reader-facing code paths, and App. A's include public data-release file names.
  The lint would need an explicit reader-facing form, such as a `\codepath{}` macro the lint allows.
- **What it routes.** App. A's `KNOWN_ISSUES` and VL pointers go to `NoteRecords2026`.

**Later, a separate lane:** rewrite the reader parts of H and I in register, per the decision.

**How the move proves no record was lost.**
- `check_note_records.py` is derived from the base sources, not from a typed list.
- It gates commits 2 and 3. Its probes:

  | probe | what it requires |
  |---|---|
  | P1 | every base label is defined exactly once over note+records, and none of G's or J's is left in the note |
  | P2, P4 | every tag and every `\repopath` is present |
  | P3 | the `\dead` multiset is identical, with zero in the posted closure |
  | P5 | every RECORD paragraph is verbatim in the records closure, and every READER paragraph is in the note or listed as a REWRITE in the ledger with a probe |
  | P6 | every App. G tag pointer survives as a `NoteRecords2026` citation naming the same tag |

- The containment gate independently proves the rendered direction: the 64 literals render in records and nowhere in
  the posted note.

---

## 7. Open questions for Joseph or the director

These are not decided here.

- **Q1. The PET note.** It has the same structure, `app_provenance_pet.tex` and `app_history_pet.tex`, and Joseph plans
  to post both notes (`DECISION-20261021-joseph-register-loop-2.md` item 2). Does the ruling extend to it? Option C would
  take the PET history as a second records driver, or as a second part of `main_records`.
- **Q2. The `\depositsnapshot` hold.** "[snapshot identifier pending deposit]" renders only in App. G. After the move,
  the posted note loses that visible hold. The `NoteRecords2026` pin takes its role. Is that acceptable, given that the
  release-state wording is Joseph's (`METHODS-IMPLEMENTATION.md:254`)?
- **Q3. "Markers" in the director's reading.** Does it include App. I's "Code identifiers cited in the note" (lines
  39–54) and the `seedscan` naming? This plan keeps both as READER, as "where the code lives".
- **Q4. Two facts that would print in neither posted document.**
  - The primer dropped a clause because its chain is in App. J (`primer_body.tex:268`). After the move, that chain prints
    in neither the primer nor the posted note.
  - The 4 App. A superseded pull values would also print in neither.

  Decision 2 appears to allow this for records. `DECISION-20261021-joseph-register-loop-2.md` item 4 ("no fact leaves
  both documents") was written about limitations and disclosures. Is this confirmed?
- **Q5. An earlier open item.** "Where App. J goes. The superseded values are not moved" (`METHODS-IMPLEMENTATION.md:252`)
  is superseded by this decision. It should be closed in the commit 4 record.

## 8. Stale or unused material noticed

- `S/notes-records/snap/`, `build/`, `sim/` and `lintprobe/` are measurement copies made by this session, not deliverables.
- The comments that say "App. H" for history are already stale from an older lettering scheme:
  `sec_3d.tex:256`, `sec_eavailw.tex:258,264`, `sec_summary.tex:121` and `sec_systematics.tex:541,548`.
