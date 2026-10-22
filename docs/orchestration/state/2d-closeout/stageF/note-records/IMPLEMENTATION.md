# Implementation: records move, PLAN.md §6 option C, commits 1 and 2

> **Read the section "Review fixes (REVIEW.md, ADOPT-AFTER-FIXES)" at the end first.** It supersedes the check
> outputs, counts and items 5–6 of "Deviations" below, which describe the first delivery.

Worktree `S/wt-rec`, branch `stageF/note-records-move-20261021`, HEAD `4ba0dd2f`. Everything is uncommitted. I did not
touch git state, push, or contact anyone. `S` is the session scratchpad.

**Authority.** `DECISION-20261021-joseph-da-and-note-records.md` item 2, and the director's rulings Q1–Q4 from the
task brief.

**The base was re-measured on `4ba0dd2f`.** The frozen copy is `git archive 4ba0dd2f docs/analysis-note`, at
`S/notes-records/impl/base/`. The four record files are byte-identical to the plan's snapshot, so the record ranges
are unchanged: `app_release.tex` 122–173 and 244–287, and `app_codebase.tex` 55–72. Nineteen other chapter files
differ from the snapshot (the glossary batch), so I re-derived every pointer.

**`origin/main` moved during the session**, from `4ba0dd2f` to `125c67c8` (PR #214, an r14 record). That change
touches no file under `docs/analysis-note/`; `git diff --stat HEAD origin/main -- docs/analysis-note` is empty. Every
check below that names a base was also run against `4ba0dd2f`.

## Files changed

**New, in `docs/analysis-note/`:**

| file | what it is |
|---|---|
| `main_records.tex` | The records driver. It loads xr-hyper before the preamble and `\externaldocument{main_note}`. It defines `\depositsnapshot` verbatim. Its own section, table, figure and equation numbers carry an R. A front-matter sentence says every bare number is the note's. A TOC patch (article's `\l@section`, widened from 1.5em to 2.3em) keeps "R1" from running into its title. It inputs `app_provenance`, `app_release_records`, `app_codebase_records` and `app_history`, and prints a bibliography. |
| `app_release_records.tex` | A comment header plus `app_release.tex` 122–173 and 244–287, byte-identical (checked with `diff`). |
| `app_codebase_records.tex` | A comment header plus `app_codebase.tex` 55–72, byte-identical. |
| `check_note_records.py` | The inventory, the probes P1–P7 and `--self-test` (see "Deviations"). |
| `records-move-ledger.md` | The move ledger: 28 rows, 106 probes. |

**New, outside the note directory:** `docs/orchestration/state/2d-closeout/stageF/note-records/inventory-base.json` (moved by the director at commit time to `docs/analysis-note/records-inventory-base.json`: the receipt-artifact pre-commit check read it as a receipt naming untracked data files),
derived from `4ba0dd2f` with `_base_sha` recorded. It holds 27 labels (22 of them record labels), 29 tags, 97 struck
bodies, 30 paths, 84 record paragraphs, 20 reader paragraphs, and 40 pointer keys that count 44 App. G pointers. It
differs from the plan's inventory in one key only: a new `app_statmethods.tex|rvp1pi` pointer, added by the glossary
batch.

**Modified (22 files, +402/−256 against `4ba0dd2f`):**
- **Drivers and appendices.** `main_note.tex` drops the two record inputs. `app_release.tex` and `app_codebase.tex`
  lose the record ranges. `app_statmethods.tex`, `app_guide.tex` and `sec_intro.tex` are edited.
- **Pointer rewrites.** `sec_method`, `sec_systematics`, `sec_validation`, `sec_results`, `sec_3d`, `sec_eavailw`,
  `sec_5d`, `sec_joint`, `app_statmethods_nd` and `app_negweight`.
- **Other.** `technote.bib`, `build_all.sh`, `check_dead_containment.py`, `check_body_pointers.py`,
  `test_build_all.py` and `README.md`.

**Byte-identical to `4ba0dd2f`, checked with `git diff --quiet`:**
- the moved record text: `app_provenance.tex` and `app_history.tex`;
- the paper, primer and PET note: `paper_body`, `main_paper`, `primer_body`, `main_primer`, `pet_note`, `sec_pet`,
  `sec_pet_campaigns`, `app_cstat`, `app_provenance_pet` and `app_history_pet`;
- `values*.tex` and `publication.bib`.

The acknowledgments, the funding hold and `\pubhold` are untouched: the `main_note.tex` diff is only the two inputs
and a comment.

**Scratch tools**, not deliverables: `S/notes-records/impl/tools/rewrite.py` (the rewrite, which asserts each anchor's
count) and `moving_refs.py` (the census). I also extended the page-count loop of the scratch tool
`S/plain-language/build_copy.sh` by `main_records`; the original is kept at `impl/build_copy.sh.orig`.

## Rewrite counts

The census is `moving_refs.py` over the posted closure, with comments stripped.
- **Before:** 90 printed references into moving labels. By region, 50 are in the body and 40 in appendices. By
  label:

  | label | references |
  |---|---|
  | `app:provenance` | 35 |
  | `app:history` | 31 |
  | `history-vl175` | 7 |
  | `release-audit` | 6 |
  | `release-identities` | 4 |
  | `history-errata` | 2 |
  | `sec:3d-syst`, `sec:eavailw-cov`, `history-5dcandidates`, `history-withdrawn`, `history-superseded` | 1 each |

- **After:** `TOTAL 0`.

How the 90 were handled:
- 2 were deleted with the App. A parenthesis (Q4).
- 1 was retargeted to the new reader label: `sec_method`, to `\S\ref{app:release-edges}`.
- 87 became `Ref.~\cite{NoteRecords2026}` citations. Five pairs merged into one citation each:
  - `sec_intro` roadmap rows;
  - `app_guide` Records bullet;
  - `sec_5d` block sum;
  - `sec_systematics:119`;
  - `sec_validation:215`.

  That leaves **82** `\cite{NoteRecords2026}` in the posted sources.

The 90 include the 5 whole-appendix references, at 3 sites: `sec_intro:136–137`, `app_guide:15,18` and
`app_release:5`. The plan's "84 + 3" was measured on the earlier tree.

**Citation form.**
- **App. G tags:** `Ref.~\cite{NoteRecords2026}, \texttt{tag}`.
- **App. J targets:** `…, superseded values` for the whole appendix, or `…, superseded values: <heading words>`.
- **H targets:** `…, identities already fixed` and `…, construction and audit record`.
- **The VL175 subsection:** "the retired 2D construction" in the body, where the lint forbids "VL175", and "the VL175
  construction" in the appendices (ledger row L14).

## Checks, each run on the delivered files

### 1. Build

`bash S/plain-language/build_copy.sh rec "$S/wt-rec"` gives `build_all rc=0`. A `cmp` of every source in the build
copy against the worktree found no difference.

Gate lines from `build.log`:
```
BODY-POINTERS SELF-TEST :: PASS (25 cases: the appendix silent; 8 patterns fire in a body file and in a nested body file; a macro-printed digest fires; 7 legitimate forms silent)
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
  OK   main_note.pdf written by this run; no unresolved references and no multiply-defined labels in main_note.log after 1 latexmk invocation(s):
  OK   main_primer.pdf ... (same)
  OK   main_paper.pdf ... (same)
  OK   pet_note.pdf ... (same)
  OK   main_records.pdf written by this run; no unresolved references and no multiply-defined labels in main_records.log after 1 latexmk invocation(s):
RESULT :: PASS :: ... mode=strict products=main_records.pdf@sha256:d2627a7f…(fresh),pet_note.pdf@…(fresh),main_note.pdf@…(fresh),main_paper.pdf@…(fresh),main_primer.pdf@…(fresh)
SEC4-RECEIPTS :: PASS (15/15)
```

Measured independently from each log (`grep -a`) and each PDF:

| target | undefined | multiply-defined | `??` | pages |
|---|---|---|---|---|
| `main_note` | 0 | 0 | 0 | 118 |
| `main_paper` | 0 | 0 | 0 | 13 |
| `main_primer` | 0 | 0 | 0 | 15 |
| `pet_note` | 0 | 0 | 0 | 26 |
| `main_records` | 0 | 0 | 0 | 21 |

**Page counts, measured.** The base build of `4ba0dd2f` (`builds/rec-base`) gave a 138-page note, a 13-page paper, a
15-page primer and a 26-page PET note. After the move the note has **118** pages (−20) and the records document
**21**. The paper, primer and PET note are unchanged.

### 2. Containment

From the same log:
```
  ok   note: clean, 0 \dead{} in a 29-file closure
  ok   pet-note: 19 \dead{} uses across app_history_pet.tex
  ok   paper: clean, 0 \dead{} in a 4-file closure
  ok   primer: clean, 0 \dead{} in a 4-file closure
  ok   records: 97 \dead{} uses across app_history.tex
  ok   records.pdf carries 64/64 struck literals (positive control OK)
  ok   pet-note.pdf carries 5/5 struck literals (positive control OK)
  ok   note.pdf: 0 of 69 struck literals
  ok   paper.pdf: 0 of 69 struck literals
  ok   primer.pdf: 0 of 69 struck literals
```
The 69 literals are the records' 64 plus the PET note's 5.

The PET note is unchanged:
- its source files are identical;
- its `pdftotext` matches the base build's (0 differing lines);
- its control is 5/5, as before.

### 3. Lint

Run directly:
```
BODY-POINTERS SELF-TEST :: PASS (25 cases: …)   rc=0
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)   rc=0
```

### 4. `test_build_all.py`

```
Ran 63 tests in 41.422s
OK
```
63 tests are defined and 63 ran; the base had 49. The mutation run:
```
=== mutation run: 10 mutants against build_all.sh
m1 … m8   CAUGHT   (as before)
m9-drop-the-multiply-defined-check       CAUGHT <- FAIL: test_a_multiply_defined_label_FAILS_before_containment
m10-build-the-records-before-the-note    CAUGHT <- FAIL: test_the_clean_targets_before_it_still_report_ok
=== 10/10 mutants caught
```
The new tests:
- `TestMultiplyDefinedLabels`: 3 tests;
- `TestRecordsBuildOrder`;
- `PostedNoteIsOutwardTest`: 5 tests, covering a `\dead` in `main_note` (three forms), `app_history` re-input, a
  struck literal in `main_note.pdf` (records and PET), and the production maps;
- `ContextExemptLiteralTest`: 4 tests;
- one `UnitRequiredLiteralTest` test for the three new keys.

The fixtures of `ResultLineNamesItsObjectTest` and `StruckOnlyInHistoryTest` now use `main_records`.

### 5. `test_check_sec4_receipts.py`: does NOT pass, and the failures predate this move

```
3 failed, 13 passed
FAILED test_a_missing_value_fails                       (assert True is False)
FAILED test_a_value_kept_only_in_a_latex_comment_is_not_found   (paper_body.tex.count("differ by at most") == 0)
FAILED test_the_self_test_fails_cleanly_when_a_printed_value_is_missing
```
- The same run on the untouched base copy (`impl/sec4base`, state symlinked) gives the same 3 failures and 13 passes.
- The tests look for the phrase "differ by at most" in `paper_body.tex`. The paper's register rounds r12/r13
  (`d127e46a`, `50852bbd`) removed that phrase.
- The file is pytest-style: `unittest` reports "NO TESTS RAN", so I ran it with pytest.
- Not mine to fix: the paper and that test are outside my files. The build's own `check_sec4_receipts.py` gives PASS
  15/15.

### 6. `check_note_records.py`

The probe, against the frozen JSON, gives the same result when given the base directory:
```
RECORDS-MOVE :: PASS (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 0 failure(s))
```
This includes the silent direction of P6 on the real rewrite. The self-test:
```
  fired  dropped strike                 -> P3 \dead multiset changed: lost {'0.406': 1}, added {}
  fired  dropped record paragraph       -> P5 RECORD paragraph not verbatim in the records closure
  fired  edited record paragraph        -> P5 RECORD paragraph not verbatim in the records closure
  fired  record paragraph left in the note -> P5 RECORD paragraph still printed in the posted note
  fired  edited reader paragraph        -> P5 READER paragraph 06f284f7a786 neither in the note nor in the ledger
  fired  renamed tag (every occurrence) -> P2 tag joint-5d missing from the records' app_provenance.tex
  fired  lost repository path           -> P4 repository path … missing from the records closure
  fired  G label left in the note       -> P1 record label tab:prov-paths is still defined in the posted note
  fired  J label left in the note       -> P1 record label app:history-errata is still defined in the posted note
  fired  struck value in the note       -> P3 the posted note's closure still strikes values
  fired  lost tag pointer               -> P6 sec_joint.tex: 1 pointer(s) to tag joint-5d before, 0 after
  fired  false ledger probe             -> P7 ledger row L99: probe … does not hold
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
```
I also ran a naive move: the records moved verbatim, with no pointer rewrites. P1–P5 stay silent on it, and P6 fires
33 times.

### 7. `pdftotext`

**The posted note** (`main_note.pdf`):

| string | count |
|---|---|
| `^Provenance$` | 0 |
| "Superseded values and withdrawn results" | 0 |
| "Repository records with a path" | 0 |
| "Tracker rows and code identifiers" | 0 |
| "Identities already fixed" | 0 |
| "Construction and audit record of the" | 0 |
| "Test-suite discipline" | 0 |
| "SHA256 identities for all 2,374" | 1 |
| "[snapshot identifier pending deposit]" | 1 |

So the posted note has no provenance section, no superseded-values section and no tag table. The appendix letters are
now A–F, G (Result package) and H (Codebase).

**The records document** prints:
- "Superseded values and withdrawn results" 2× (the TOC and the heading);
- "Repository records with a path" 1×;
- "Identities already fixed" 2×;
- "Test-suite discipline" 1×;
- the snapshot hold 1×.

**The paper, against the base build:**
```
1546c1546
< cited in Ref. [14], App. H. A candidate release package
> cited in Ref. [14], App. G. A candidate release package
1554c1554
< analysis; Ref. [14], App. H states what each part of the
> analysis; Ref. [14], App. G states what each part of the
```
- The diff has no other line.
- `App. B` and `App. C` are unchanged.
- The 29 `Ref. [14], Sec.` pointers resolve identically.
- No `??` prints.

### 8. `swallowed_text.py`

`python3 S/tools/swallowed_text.py S/wt-rec origin/main` gives `flagged 0`. The run against `4ba0dd2f` also gives
`flagged 0`.

### Extra: plan check 8, not in my brief

`build_all.sh --export-deposit` into an empty directory gave rc 0:
```
  OK   deposit tree written: main_note.tex (flattened, comment-free), 2 .bib files, 39 figures;
       it builds alone, and its PDF text equals main_note.pdf's.
```
The export contains no `app_history`, `app_provenance` or `\dead`. It does print `coverage-fixed-truth` 4×. Those are
citation tags in the plan's own `(Ref.~\cite{NoteRecords2026}, \texttt{tag})` form, not a tag table, so the plan's
wording "contains no G tag" conflicts with its own citation form.

## Deviations from the plan, with reasons

1. **The posted note is also checked against the PET literals.** The containment check searches outward builds for
   every literal that any strike-carrying PDF renders. The plan measured only the 64 records literals.
   - The first build failed on the PET-struck `0.912` (`\petRatio`). The posted note prints the live coverage fraction
     "C2 = 0.912" (`\covTwoDCTwo`) 4×.
   - Fix: a second `CONTEXT_EXEMPT` entry, verified by eye and covered by tests. The paper avoids the same collision by
     printing 91.2%.
   - Raw bare-token hits in the posted PDF were 6: `0.563`, `0.564`, `0.912`, `1.008`, `1.014` and `2.26`. After
     `UNIT_REQUIRED` they were `0.912` and `1.014`; after `CONTEXT_EXEMPT`, none.
   - The exemption stores, per entry, a PDF regex, a source file and the source text that prints it. A test requires
     that source text to still exist and the literal to still be struck.
2. **`check_note_records.py` differs from the draft:**
   - `record_labels` includes H's 2 labels;
   - P5 also fails if a RECORD paragraph still prints in the note;
   - P6 credits a pointer whose paragraph moved verbatim, as the same `\ref` in the records (`MOVED_TO`), and checks
     whole-appendix files;
   - new P7 runs the ledger's N:/X:/R: probes;
   - the probe accepts the frozen JSON;
   - `--self-test` runs on the delivered pair and 12 plants.

   The first self-test run exposed a weak plant: renaming one occurrence of a tag is invisible to P2, because the tag
   occurs elsewhere. The plant now renames every occurrence. P2 checks presence, not count.
3. **`build_all.sh` changes beyond the targets entry:**
   - The multiply-defined check fails at once rather than retrying: a duplicate label does not converge.
   - Mutants m9 and m10 were added, so it is 10/10, not the plan's 8/8.
   - The banner texts that named "the provenance appendix" and "the NOTE build only" were updated.
4. **The ledger.** `records-move-ledger.md` is in `docs/analysis-note/`, where the draft probe reads it.
   - The brief's list of files did not name it, but plan commit 2 and Q4 require it.
   - The inventory is at the path the brief gave, not the plan's `state/note-records-2026MMDD/`.
5. **[Superseded by review F1: the pair is restored.] Q4: the deleted parenthesis held one pair that is not struck.** The App. A parenthesis (now
   `app_statmethods.tex:677–678`) also held "exact-split cross-check 0.051 and 0.405".
   - J does not `\dead` that pair. It records it in context as the value "since the 2026-10-06 bootstrap rebuild"
     (`app_history.tex:215`), and as replacement values in rows 46, 47 and 55.
   - I deleted the whole parenthesis, as ruled. The pair now prints only in the records (ledger L8 has R: probes on
     it).
   - Please confirm that this pair counts as superseded.
6. **[Superseded by review F6.] Q2: the hold sentence was placed at the end of the release-status paragraph.** It is byte-identical, so its
   "tracker rows below" now refers to the release appendix, which has none. This is a wording point for the later
   register batch; I did not edit it.
7. **The app_guide "Records" group was renamed "Release and code".** A sentence after the list now names the records
   document. The plan asked only for a rewrite of the bullet.
8. **Two small changes to the lint.** I added one silent case for the J heading form. The self-test message now reads
   "the appendix silent" instead of "App. G silent".

## Unresolved, or for review

- **`test_check_sec4_receipts.py`** has the 3 failures described under check 5. They predate this move; the owner of
  the paper or of that test should fix them.
- **The posted note still prints some superseded values in prose.** For example, `sec_results.tex:158` reads "an
  earlier version omitted them and quoted 6.87%", under the earlier W5 ruling. Q4 named only the App. A parenthesis, so
  I deleted only that. I did not sweep the body for other prose disclosures of earlier values.
- **`technote.bib` `NoteRecords2026`** is at `tree/main` until the director pins it (commit 3). The paper's xr
  dependency on `main_note.aux` is unchanged: App. H is now App. G there.
- **Stale comments** that say "App. H" or "App. E" are untouched:
  - in `sec_3d`, `sec_eavailw`, `sec_systematics` and `sec_summary` (plan §8);
  - in the comments at `sec_systematics.tex:529–530` and `:537`.
- **Pre-existing staleness in reader text, left for the register batch:** the release appendix still says "Rebuilding
  this note's three PDFs", and its title "Result package and fixed identities" is unchanged.
- **Not done, as briefed:** commits 3–5 and the register rewrite of the reader parts of H and I. The PET note was left
  as it is (Q1).

---

## Review fixes (REVIEW.md, ADOPT-AFTER-FIXES), applied on the director's instructions

All uncommitted in `S/wt-rec`. I ran no git command that writes. I used read-only `git show` and `git diff` to
inspect `e05c78c7`, and `git show` to copy one file from it.

### Does the diff still apply on `e05c78c7`? Yes

`git diff --name-only 4ba0dd2f e05c78c7` lists these files, and I edited none of them:
- `docs/analysis-note/test_check_sec4_receipts.py`;
- `docs/orchestration/CATALOG.md`, `MANIFEST-overrides.tsv` and `MANIFEST.tsv`;
- `docs/orchestration/state/2d-closeout/stageF/methods/METHODS-IMPLEMENTATION.md`;
- the r14 score files.

As instructed, I copied main's fixed `test_check_sec4_receipts.py` into the worktree with `git show e05c78c7:…`. That
file now equals `e05c78c7` (`git diff --quiet e05c78c7 -- …`), so it is a no-op after the rebase. My new directory
`docs/orchestration/state/2d-closeout/stageF/note-records/` does not collide with anything upstream.

### What changed

The scripted edits are in `S/notes-records/impl/tools/fixes.py`, which asserts each anchor's count.

| fix | file(s) | change |
|---|---|---|
| F1 | `app_statmethods.tex` | Restores the current exact-split pair as its own sentence, in the reviewer's wording: "For the exact-split cross-check, on the earlier covariance built before the flux-band repair, they are $0.051$ and $0.405$." The deleted superseded values stay deleted. Ledger L8 is rewritten: an N: probe on the new sentence, X: probes on the superseded clause. |
| F2 | `app_negweight.tex` | The two production-number limits print at the claim, in the reviewer's wording, followed by "Their records are in Ref.~[n] (`negweight-hpss`, `negweight-toy`)". Ledger L15. |
| F3 | `app_release.tex`, worked example step 2 | One sentence: "The five-axis covariance used in this note is the file `z-cv.npz`, with `sha256` \zcvDigest… and $\sqrt{\Tr C}=\SI{5.6742e-38}{}$, so a loaded $C_{Z}$ can be checked against both." Both values use the exact macros and forms of the records' identity table, and print as "sha256 3d7465f6…" and "5.6742 × 10⁻³⁸". Ledger L16. |
| F4 | `sec_results.tex`, `app_statmethods.tex` | Both disclosures are now citations. The records print both: the struck 6.871% row ("printed as 6.87% in the article and primer", with the omitted constraint weights as its reason) and the struck 3.366%/2.034% row ("under a legacy grouping that put the flat 1.4% band under Models"). Ledger L9 (which supersedes the earlier W5 note) and L17. The ~12 measurements on superseded objects are untouched. |
| F5 | `sec_systematics.tex` (3 sites), `app_statmethods.tex` (3 sites), `check_body_pointers.py` | One name everywhere: "superseded values: retired material". These are the lint-safe words of the records heading "The VL175 construction: retired material". The lint's silent case was updated to match. Ledger L14. |
| F6 | `app_release.tex` | The hold is now its own paragraph after the intro: "The code paths and file names in this appendix and in App.~\ref{app:codebase} refer to the snapshot of the code repository, \repolink,⏎identified at deposit: \depositsnapshot." From "refer to" on, the bytes are those of `app_provenance.tex:9–10`. It was removed from the release-status paragraph, and it carries no records citation (as the reviewer advised). Ledger L7. |
| F7 | `check_dead_containment.py` | `token_hit` now uses `TOKEN_END = (?!\d\|\.\d)`, and so do both `CONTEXT_EXEMPT` regexes. A test covers a value at sentence end and a point that continues the number. |
| F8 | `check_dead_containment.py` `main()` | The build gate FAILS on an exemption whose build is not outward, whose source text no longer occurs in its source file (or the file is gone), or whose literal is no longer struck. It also prints "… holds" for each live entry. |
| N1 | `sec_5d.tex` | "(Ref.~[n], superseded values: the earlier direct $(\Eavail,W)$ block sum)". |
| N2 | `app_statmethods.tex` (2 sites) | "struck values", the heading's words. |
| N3 | `sec_systematics.tex`, `sec_validation.tex` | "…, and `coverage-fixed-truth`" in place of "listed there". |
| N4 | `app_release.tex` | Title "Result package and reproduction limits". "three PDFs" → "PDFs". "the full digests" → "the digests". The bin-edge lead loses "for completeness". `main_records.tex`'s R2 intro now names the new title. |
| N5 | `app_guide.tex` | Deletes the glossary row VL170/VL172/VL175. After F5 the posted PDF prints none of these labels (0 hits for `VL1[0-9][0-9]`). The J28 and July/May rows stay. |
| N6 | `check_dead_containment.py` | Recorded in a comment: the three new `UNIT_REQUIRED` keys also widen the paper and primer check. Measured: neither PDF prints any of them bare. |

The F8 test fixtures needed a matching change. The synthetic directory of
`ResultLineNamesItsObjectTest`/`StruckOnlyInHistoryTest`/`PostedNoteIsOutwardTest` now carries each exemption's source
text, and strikes `1.014` (records) and `0.912` (PET), because the gate now refuses a directory where those are
missing. As a result, two assertions moved from "1/1" to "1/2" and from "reaches 1" to "reaches 2". The new
`ExemptionGuardTest` has 4 tests:
- live exemptions hold;
- a context that no longer prints FAILS;
- a missing source file FAILS;
- a literal no longer struck FAILS.

**Not done:**
- **N7** (wiring `check_note_records.py` into the build) and **N8** (the pin) belong to commit 3, and you are
  keeping the URL.
- **N9** covers about 20 comments that name `App. history`, `App. history-vl175` or `App. G/H`. They are dated
  provenance comments that print nothing, and the labels they name still exist in the records, so I left them. Say
  if you want them rewritten.

### The checks again, on the delivered files

Every source in the build copy `cmp`-equals the worktree.

**1. Build.** `bash S/plain-language/build_copy.sh rec "$S/wt-rec"` gives `build_all rc=0`:
```
BODY-POINTERS SELF-TEST :: PASS (25 cases: the appendix silent; 8 patterns fire in a body file and in a nested body file; a macro-printed digest fires; 7 legitimate forms silent)
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
  OK   main_note.pdf written by this run; no unresolved references and no multiply-defined labels in main_note.log after 1 latexmk invocation(s):
  OK   main_primer.pdf … / main_paper.pdf … / pet_note.pdf … (same)
  OK   main_records.pdf written by this run; no unresolved references and no multiply-defined labels in main_records.log after 1 latexmk invocation(s):
RESULT :: PASS :: … mode=strict products=main_records.pdf@sha256:25109440…(fresh),… all (fresh)
SEC4-RECEIPTS :: PASS (15/15)
  main_note.pdf  119 pp
  main_primer.pdf 15 pp
  main_paper.pdf 13 pp
  pet_note.pdf   26 pp
  main_records.pdf 21 pp
```

Measured from the logs and PDFs:

| target | undefined | multiply-defined | `??` | pages |
|---|---|---|---|---|
| `main_note` | 0 | 0 | 0 | 119 |
| `main_paper` | 0 | 0 | 0 | 13 |
| `main_primer` | 0 | 0 | 0 | 15 |
| `pet_note` | 0 | 0 | 0 | 26 |
| `main_records` | 0 | 0 | 0 | 21 |

The note is +1 page over the first delivery, from the restored and added sentences (base: 138).

**2. Containment.**
```
  ok   note: clean, 0 \dead{} in a 29-file closure
  ok   pet-note: 19 \dead{} uses across app_history_pet.tex
  ok   paper: clean, 0 \dead{} in a 4-file closure
  ok   primer: clean, 0 \dead{} in a 4-file closure
  ok   records: 97 \dead{} uses across app_history.tex
  ok   CONTEXT_EXEMPT[('main_note', '1.014')] holds: sec_validation.tex prints '(mean weight 1.014)' and 1.014 is still struck
  ok   CONTEXT_EXEMPT[('main_note', '0.912')] holds: values.tex prints '\\newcommand{\\covTwoDCTwo}{0.912}' and 0.912 is still struck
  ok   records.pdf carries 64/64 struck literals (positive control OK)
  ok   pet-note.pdf carries 5/5 struck literals (positive control OK)
  ok   note.pdf: 0 of 69 struck literals
  ok   paper.pdf: 0 of 69 struck literals
  ok   primer.pdf: 0 of 69 struck literals
```
The PET note is unchanged: its `pdftotext` has 0 lines of difference from the base build.

**F7 measured on the outward PDFs**, as bare-token hits over the 69 literals before units and exemptions:

| PDF | old boundary | new boundary | added | gate hits |
|---|---|---|---|---|
| `main_note` | 0.563, 0.564, 0.912, 1.008, 1.014, 2.26 | the same six | none | 0 |
| `main_paper` | 0.564 | 0.564 | none | 0 |
| `main_primer` | none | none | none | 0 |

**3. Lint.** `BODY-POINTERS SELF-TEST :: PASS (25 cases…)` and `BODY-POINTERS :: PASS (0 internal pointers in 17
body files)`.

**4. `test_build_all.py`.** `Ran 69 tests … OK`; 69 are defined. `--mutate` gives
`=== 10/10 mutants caught` (m1–m10 all CAUGHT).

**5. `test_check_sec4_receipts.py`** (main's fixed version, run with pytest): `16 passed in 1.65s`.

**6. `check_note_records.py`.**
```
RECORDS-MOVE :: PASS (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 0 failure(s))
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
```
- **The ledger caught the fixes before I updated it.** The first probe after them failed on 2 READER paragraphs (the
  bin-edge lead and the worked example) and on 8 stale ledger probes (L1, L6, L7, L8, L9, L12, L14).
- **The ledger now** has 35 rows and 131 probes.

**7. `pdftotext`.**
- **The posted note:**

  | string | count |
  |---|---|
  | `^Provenance$`, "Superseded values and withdrawn results", "Repository records with a path", "Tracker rows and code identifiers", "Identities already fixed", "Construction and audit record of the", "Test-suite discipline" | 0 each |
  | "SHA256 identities for all 2,374" | 1 |
  | "[snapshot identifier pending deposit]" | 1, line-wrapped |
  | "tracker rows below" | 0 |
  | "6.87", "An earlier version of this sentence", `VL1[0-9][0-9]`, "retired 2D", "struck-values table" | 0 each |
  | "retired material" | 5 |
  | the F1 sentence, the F2 sentence, "sha256 3d7465f6", "5.6742" | 1 each |

- **The records:** "retired material" 1 (the heading), the hold 1.
- **The paper**, against the base build: only `1546c1546` and `1554c1554`, "App. H" → "App. G". No other line
  differs, and no `??` prints.
- **The primer:** 0 lines of difference.

**8. `swallowed_text.py`.** `flagged 0` against `origin/main` (now `e05c78c7`), and also against `e05c78c7` and
`4ba0dd2f`.

### Found while checking, not changed: one more earlier-version disclosure

The executive summary, `sec_execsummary.tex:31`, prints "its flux band carries MAT's ν–e and inverse-muon-decay
constraint weights, which an earlier version omitted (\S\ref{sec:results-uq})". This is the same fact as F4's
`sec_results` sentence, and its pointer now lands on a sentence that no longer says it. The reviewer's list did not
include it, and the summary's wording is under its own page-count rulings, so I left it.

Proposed edit, if you extend F4 to it: delete ", which an earlier version omitted", so it reads "…constraint weights
(\S\ref{sec:results-uq})".

Two other "earlier version" phrases are not note-version disclosures, so I kept them:
- "An earlier version of the package was also replayed…" (`app_release.tex`, the RC1 replay, from the decision-1
  text);
- a bibliography title.

### Citation count now

There are 81 `\cite{NoteRecords2026}` in the posted sources. That is 82, less the one in the deleted N5 glossary row.
Against `4ba0dd2f` the diff is 23 tracked files (+507/−272), plus the 5 new note files and the state directory.
