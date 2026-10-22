# Review: records move (PLAN.md option C, commits 1–2), uncommitted in `S/wt-rec`

**Reviewer.** An independent, read-only review. Nothing in any worktree was edited and nothing was committed.
`git -C S/wt-rec status --short` gives the same 28 entries before and after this review.

**Where my checks ran.**
- Scratch copies only:
  - `S/notes-records/rv/tc/`, a copy of the worktree, for the tests;
  - `S/notes-records/rv/mut/`, a copy of the after build, for the real-LaTeX mutants.
- Tools and outputs are in `S/notes-records/rv/`.
- I did not use the implementer's probe (`check_note_records.py`) for any finding.

**Base.** 4ba0dd2f. Every source in `builds/note-g0-rb` equals `git show 4ba0dd2f:` (`cmp`). Every source in
`builds/rec` equals the worktree (`cmp`). `wt-rec` is 2 commits behind `origin/main`. Neither of those commits touches
`docs/analysis-note/`.

File:line references are to the worktree files unless they say "base".

---

## Results of the nine checks

### 1. Nothing moved was edited: confirmed
- `app_provenance.tex` and `app_history.tex` are byte-identical to 4ba0dd2f (`git diff --quiet`).
- `main_records.tex` inputs both. The `.fls` closure confirms it.
- `app_release_records.tex` lines 6–102 equal base `app_release.tex` 122–173 followed by 244–287. My `diff` shows one
  difference only: a blank line inserted between the two ranges.
- `app_codebase_records.tex` lines 5–22 equal base `app_codebase.tex` 55–72 exactly.
- The range boundaries are right:
  - 122 is `\subsection{Identities already fixed}`;
  - 173 is `\end{center}`;
  - 244 is `\subsection{Construction and audit record…}`;
  - 287 is end of file.

### 2. Nothing was lost: confirmed
- **Labels.** My own label census used the `.fls` closures of `main_note` and `main_records`, excluding shared
  preamble and values files. Every base label is defined exactly once across the note and the records. No label
  is missing or duplicated. The only new label is `app:release-edges`.
- **Paragraphs.** I split base H and I into paragraphs and checked each one.
  - Every paragraph is either verbatim in the posted file or verbatim in the records file, except 4 edited ones.
    Those are the H intro, the schema lead, the enumerate block (items 7 and 8) and I's `seedscan` paragraph.
  - All 4 edits are pointer rewrites.
- **Added lines.** Every line added to a posted `.tex` file is accounted for: a `NoteRecords2026` citation, a
  comment, or one of the known edits (the guide, the roadmap, the hold, the bin-edges heading, the deleted
  parenthesis).

### 3. Classification
Most of the split is right: the audit record and test discipline moved, and the scope, schema, edges, example and
acceptance field stayed. Three items are worth a ruling. They are findings F3, F4 and N5 below.

### 4. Pointer rewrites: checked
- I read all 82 citations in the word diff, not just a sample of 25. I also checked every cited tag against
  `app_provenance.tex`: 82 citations, 0 missing tags.
- Most read correctly and name the right record.
- **Defects.** They are listed as F2, F5 and N1–N3.
  - "the retired 2D construction" names no heading in the records.
  - "the struck-values table" is not a heading; the heading is "Struck values".
  - `sec_5d.tex:566` lost its specific target.
  - Two limitations are now delegated to an unposted document.

### 5. The Q4 deletion: the pair is current, not superseded
See F1.

### 6. The snapshot hold
See F6, which includes the proposed wording.

### 7. Gates
- **Test suite.** `test_build_all.py` gives 63/63 OK, run in a copy.
- **Mutation suite.** `--mutate` catches 10/10.
- **Body-pointer lint.** The lint and its self-test PASS. A planted `VL175` and `KNOWN_ISSUES` in `sec_systematics.tex`
  FAIL, as they should.
- **Containment on a real build.** I added mutants to a copy of `app_statmethods.tex`, rebuilt `main_note` with
  latexmk, and ran `check_dead_containment.py`.
  - It caught `0.386`, `0.406` and `1.008 %`.
  - It stayed silent on the bare live `1.008` and on `C$_2=0.912$`, as designed.
  - It missed `…ratio of 1.014.` and `…ratio of 0.912.`. That is a pre-existing boundary bug, F7.
- **xr duplicates.** A real xr collision (`\label{sec:pull}` planted in the records copy) prints
  `Label 'sec:pull' multiply defined`. The new log check matches that line, so the gate's premise holds with real
  LaTeX, not only with the fake.
- **Exemptions.** They are narrow in the build that matters. F8 covers their staleness guard and N6 their scope.

### 8. The paper: confirmed
- **Text diff.** A plain `pdftotext` diff of `main_paper.pdf`, base against after, has 2 changed lines: 1546 and 1554,
  both "App. H" → "App. G".
- **Layout diff.** Both changes fall on one physical line (809).
- **Sources and other PDFs.**
  - The paper sources are unchanged.
  - The primer's PDF text is identical.
  - No `??` prints in the paper, note or records.
- **Paper claim still supported.** The paper says the 2,374 checksums are "in the records cited in App. G". Posted
  `app_release.tex:68` still supports that.

### 9. Superseded values left in the posted prose
See F4 for the full list.

---

## Findings

### F1. SHOULD-FIX: the Q4 deletion removed a current value
**Evidence.**
- **The deleted parenthesis** (base `app_statmethods.tex:687–688`, now `app_statmethods.tex:677`) held three objects:
  - the VL175 construction, 0.048/0.406;
  - the pre-flux-constraint-repair values, 0.041/0.386;
  - the exact-split cross-check, 0.051/0.405.
- **The first two are superseded.** They are struck in App. J:
  - `app_history.tex:61`, `\dead{0.386}`;
  - `:63`, `\dead{0.041}`;
  - `:72`, `\dead{0.048}`, `\dead{0.406}`.
- **The exact-split pair is never struck.**
  - It appears only as a replacement value: rows `:46` (0.051), `:47` (0.405) and `:55` (0.405, "the pull mean 0.051
    does not move").
  - `:215` gives it as the value "since the 2026-10-06 bootstrap rebuild".
  - No later row replaces it. The cross-check was not recomputed after the switch to LightGBM.
- **The posted note still quotes that cross-check's other numbers on the same earlier covariance:**
  - `app_statmethods.tex:603`: "the exact-split cross-check's 1.47, against an earlier covariance built before the
    flux-band repair". This is row 55's 1.472.
  - `:990`: 3.66 / 0.598.
  - `sec_systematics.tex:181–184`.
- So the pair is the current value for a comparator that is still quoted. Q4's premise, "the parenthesis of
  superseded values", does not hold for it.

**Fix.** Restore the pair alone, worded as current and without history:
> …and RMS $\boxed{0.398}$. For the exact-split cross-check, on the earlier covariance built before the flux-band
> repair, they are $0.051$ and $0.405$.

- **Containment.** Neither `0.051` nor `0.405` is a struck literal, so containment stays clean. The `0.406` of the
  VL175 row is a different token.
- **Ledger.** Update ledger row L8. Its `X:…exact-split cross-check $0.051$ and $0.405$` probe would otherwise go red.
- **Authority.** This needs the director to confirm, because it narrows Q4.

### F2. SHOULD-FIX: a limitation now prints only in the unposted document
**Evidence.**
- **The sentence.** `app_negweight.tex:23–24` reads: "Their provenance and the two limits attached to the production
  numbers are in Ref.~\cite{NoteRecords2026} (`negweight-hpss`, `negweight-toy`)."
- **Where the limits are.** They are stated only in `app_provenance.tex:182–191`:
  - the driver was uncommitted, so the executing revision is corroborated by a log string, not pinned by a digest;
  - no output carries a producing job identifier.
- **Where they used to print.** Before the move, they printed in posted App. G.
- **Why this matters.** G's own rule (`app_provenance.tex`, "This appendix is provenance, not evidence" paragraph) says
  that limitations that matter are stated at the claim. This sentence instead delegated them, and the delegation now
  points out of the posted note.
- **Related, a lesser case.** `app_statmethods.tex:794–796` ("what they do and do not license, are recorded in Ref.").
  Its conclusion still prints at `:787–790`, so I rate it only a NIT. The "Resolution" heading now heads a pointer.

**Fix.** Print the two limits at the claim, with no repository identifiers:
> …not quoted uncertainties. Two provenance limits travel with the production numbers: the driver was uncommitted when
> they were written, so its executing revision is corroborated by a version-specific log line rather than pinned by a
> digest, and no output records the job that produced it. Their records are in Ref.~\cite{NoteRecords2026}
> (\texttt{negweight-hpss}, \texttt{negweight-toy}).

### F3. SHOULD-FIX (director decision): the posted note no longer identifies the adopted covariance
**Evidence.**
- **Gone from the posted note.** After the move the posted PDF prints none of:
  - the `C_Z` digest prefix `3d7465f6`;
  - the `C_EW` prefix `835828bf`;
  - `M`'s prefix `64fec490`;
  - the revision `fb9ec356` or the jobs;
  - `√Tr C_Z = 5.6742e-38`;
  - the file size.

  I counted each in the PDF text: 1 in the base note, 0 in the after note, 1 in the records.
- **Yet the posted note depends on that identity:**
  - `sec_5d.tex:558` says the adoption is limited "to this file and its projection";
  - `sec_5d.tex:621` says the mean variant is "7.13% lower", but the reference value no longer prints;
  - the reader's own worked example, `app_release.tex:159` (step 2), says "Load … $C_{Z}$" but gives no posted check
    value for the file.
- **The record's own reason, now out of the posted note.** `app_provenance.tex:253–262` states that these digests
  "remain the identity of the object every quoted five-dimensional uncertainty is computed from, checkable by anyone
  holding the file". It also says the deposit pass moved them from the body to the posted App. H for that reason.
- **Within the ruling.** The director's reading classes "fixed-identity tables" as records, so the implementer followed
  the ruling. The issue is that the ruling also removes the reader's check value.

**Fix (if the director agrees).** Keep the table in the records, and add one reader sentence to `app:release-example`
step 2. For example:
> $C_{Z}$ is \texttt{z-cv.npz} (sha256 prefix \zcvDigest, $\sqrt{\Tr C}=\SI{5.6742e-38}{}$); $M$ has prefix
> \texttt{64fec490}.

- **The lint.** It does not cover the appendices, so this passes. Containment is also unaffected.
- **If declined.** Record the reversal of the deposit-pass placement in the commit 4 OUTCOME.

### F4. SHOULD-FIX (director decision): superseded values still in the posted prose (check 9)
These print, unstruck, in the posted note. I found them with a sentence-level sweep of the posted PDF text for
words such as earlier, superseded and legacy next to a number, and confirmed each at its source.

**(a) Earlier-version disclosures.** These are record-type by the Q4 wording, "records print only in the records
document".

| site | text | status |
|---|---|---|
| `sec_results.tex:157–159` | "an earlier version omitted them and quoted 6.87%" | **6.87% is the rounded print of the struck `\dead{6.871\%}`** (`app_history.tex:58`, "printed as 6.87% in the article and primer"). Containment cannot see it, because `6.87` ≠ `6.871` as a token. |
| `app_statmethods.tex:292–294` | "An earlier version of this sentence used a legacy grouping…" | It prints no number, but it is a pure "this sentence used to say" disclosure. The struck values (`3.366%`, `2.034%`, row 62) are not printed. |

**(b) Measurements made on a superseded object, presented as such.** These are reader material by my reading, so
keep them. They are listed so the director can rule.
- `app_statmethods.tex:603`: the exact-split 1.47 on an earlier covariance.
- `app_statmethods.tex:545`: the exact-split truncation scan, 0.69→3.66.
- `app_statmethods.tex:812–818`: the regularization scans "on an earlier $C^{\rm ours}$".
- `app_statmethods.tex:990`: the exact-split row, "quoted until 2026-10-11", 3.66 / 0.598.
- `sec_systematics.tex:174–176`: the block is 0.30 of the earlier ten-seed block.
- `sec_systematics.tex:182–184`: the earlier ten-seed mean differs from the exact-split cross-check by 0.99%.
- `sec_systematics.tex:297`: χ² 33.8 "against the earlier budget".
- `sec_systematics.tex:473–476`: 1.24–1.33 × σ of the earlier ten-seed block.
- `sec_systematics.tex:257–258`: "left the earlier printed budget unchanged".
- `app_statmethods_nd.tex:44–46`: "The superseded unified-throw 5D covariance has N=160 … 0.363 … 2.76".
- `sec_3d.tex:310–314`: pion-FSI shifts ≤0.74% and ≤0.82% on the pre-repair GENIE sample.
- `sec_execsummary.tex:118` and `sec_method.tex:103–105`: the earlier statistical band, C2 = 0.912 and seed-1
  offsets. These are live results about the only coverage test.

**Fix.**
- **(a)** Either delete both sentences, or keep `sec_results:158` without the number: "an earlier version omitted
  them (Ref.~\cite{NoteRecords2026}, superseded values)". Ledger row L9 records the earlier W5 ruling to keep it,
  so the director must choose.
- **(b)** No change recommended.

### F5. SHOULD-FIX: the body's "the retired 2D construction" matches no records heading
**Evidence.**
- **The body citations.** `sec_systematics.tex:71`, `:119` and `:183` cite "superseded values: the retired 2D
  construction".
- **The records heading.** It is "The VL175 construction: retired material" (`app_history.tex:324`).
  - `pdftotext` of the records PDF has 0 hits for "retired 2D".
  - The appendices cite the same target as "the VL175 construction" (`app_statmethods.tex:127`, `:789`, `:796`).
  - So one record has two names in one posted document.
- **The contract it breaks.** The citation form promises "by tag or by heading" (`app_guide.tex`). A reader searching
  the records for these words finds nothing.

**Fix.** In the body, cite by the heading's lint-safe words: "superseded values: retired material". The other option
is a short form that is a substring of the heading. Do the same in the three appendix sites, so the posted note
uses one name. The `SILENT_IN_BODY` case at `check_body_pointers.py:186` changes to match.

### F6. SHOULD-FIX: the snapshot hold says "tracker rows below", but nothing below has any
**Evidence.**
- **The text.** `app_release.tex:43–44` reads: "All paths, commits and tracker rows below refer to the snapshot …:
  \depositsnapshot."
- **What follows it.** The posted App. G after line 44, and App. H, contain code paths and file names but no tracker
  rows and no commits. The revision and jobs left with the identity table.
- **Where it sits.** The sentence is also glued to the end of the release-status paragraph.

**Fix.** Keep the hold's own text, `\depositsnapshot`, and the clause around it byte-identical. Change only the
subject, in its own paragraph after the intro:
> The code paths and file names in this appendix and in App.~\ref{app:codebase} refer to the snapshot of the code
> repository, \repolink, identified at deposit: \depositsnapshot.

- **What stays byte-identical.** The tail "refer to the snapshot of the code repository, \repolink, identified at
  deposit: \depositsnapshot." is unchanged from `app_provenance.tex:9–10`.
- **Do not include the records citation in this sentence.** Commit 3 will pin `NoteRecords2026` to a merge sha. That
  sha is not the deposit snapshot, so the sentence would assert two identities for one thing.
- **Authority.** The release-state wording is Joseph's (plan Q2), so route the change through the director.
- **Ledger.** Update the L7 probe.

### F7. SHOULD-FIX (pre-existing, now load-bearing): containment misses a struck value at the end of a sentence
**Evidence.**
- **The regex.** `check_dead_containment.py:233` `token_hit` uses `(?![\d.])`. A struck literal followed by a full
  stop is therefore never a hit.
- **Measured on a real rebuild of the note.** `…ratio of 1.014.` and `…ratio of 0.912.` passed. `rms 0.406.` also
  fails to match in a direct probe, while `rms 0.406)` matches.
- **It is not new.** Base `check_dead_containment.py:221` is identical.
- **Why it matters now.** This change makes 118 pages of posted prose outward-facing and relies on this check for them.

**Fix.**
- Use `(?!\d|\.\d)`. Apply the same change to the `CONTEXT_EXEMPT` patterns at `:270–271`.
- **Cost today: nothing.** I re-ran the corrected boundary over the after `main_note`, `main_paper` and
  `main_primer` text against all 69 literals. It gives 0 new hits in each.
- Add a test: "a struck literal at sentence end FAILS".

### F8. SHOULD-FIX: the exemptions' staleness guard runs only in the test suite, not in the build gate
**Evidence.**
- **Where the guard lives.** `ContextExemptLiteralTest.test_each_source_text_still_prints_and_each_literal_is_still_struck`
  (`test_build_all.py`) is what stops an exemption outliving its reason. `build_all.sh` runs
  `check_dead_containment.py`, not that test.
- **The scenario it allows.** Suppose `\covTwoDCTwo` is rebuilt and the old C2 = 0.912 becomes superseded. A stale
  "C2 = 0.912" left in prose would then pass `build_all.sh`, because the context is exempt.
- **Narrowness otherwise.** In every other respect the exemptions are narrow:
  - one build only;
  - an anchored context;
  - the literal elsewhere in the same PDF still hits, and my mutant `C2 = 0.912 and PET 0.912 now` hits.

**Fix.** In `check_dead_containment.py`'s own `main()`, fail if, for any `CONTEXT_EXEMPT` entry:
- the declared source text no longer occurs in its source file; or
- the literal is no longer struck.

Keep the unit test as the check that the gate itself works.

---

## NITs

- **N1.** `sec_5d.tex:566–567`. The specific target `\S\ref{sec:eavailw-cov}` was folded into a generic
  "superseded values". Use "superseded values: the earlier direct $(\Eavail,W)$ block sum", which is the records
  heading at `app_history.tex:498`.
- **N2.** `app_statmethods.tex:392` and `:878` say "the struck-values table". The heading is "Struck values".
- **N3.** `sec_validation.tex:215` and `sec_systematics.tex:119` read "…; its repository label is listed there,
  \texttt{coverage-fixed-truth}". After F5's rename, "there" reads as the VL175 subsection. Write "(Ref.~[n],
  superseded values and \texttt{coverage-fixed-truth})".
- **N4.** `app_release.tex`:
  - `:1`: the title "Result package and fixed identities" now misdescribes the appendix, because the identities left.
  - `:5–6`: "including the full digests" implies abbreviated ones still print.
  - `:129`: "for completeness" refers to a table that is gone.
  - `:4`: "three PDFs" is pre-existing and already noted.

  Fix these in the register batch.
- **N5.** Classification in the other direction. `app_guide.tex:49` still decodes VL170 and VL172. The posted PDF uses
  them only in that row, so the row is record residue. Trim it to the labels the posted text still uses: J28, the
  July and May sweeps, and VL175 until F5.
- **N6.** `UNIT_REQUIRED` (`check_dead_containment.py:254`) is global. The three new keys were needed only for
  `main_note`. For the paper and primer this slightly weakens a check that was stricter before: a bare `1.008` there
  failed at base and now passes. Neither prints the bare tokens today, which I measured. Make the keys per-build,
  like `CONTEXT_EXEMPT`, or record the widening.
- **N7.** `check_note_records.py` is not wired into `build_all.sh` or `test_build_all.py`, so the "nothing lost" proof
  is a one-off run. P1 and P3 are covered by the build anyway, through undefined or duplicate refs and the `\dead`
  source check. Plan commit 3 is the place to wire it.
- **N8.** `technote.bib` `NoteRecords2026` points to `tree/main` until commit 3. The posted note must not leave with it.
- **N9.** Some comments are stale, as the implementer listed. For example, `app_statmethods.tex` comments still name
  "App. history-vl175".

---

## Verdict: ADOPT-AFTER-FIXES

The move itself is clean:
- verbatim, byte for byte;
- every label defined once;
- no paragraph lost;
- the paper changes only "App. H" → "App. G", twice;
- the gates fire in the directions I tested.

No finding is BLOCKING. Before commit, fix F1, F2, F5, F6, F7 and F8. F3 and F4 need the director's rulings, and the
resulting edits can go in the same commit.

## What I checked, and what I did not

**Checked:**
- byte identity of all four moved blocks;
- the label census over both closures;
- paragraph accounting for H and I;
- every added line in the posted sources;
- all 82 citations, and every cited tag's existence;
- heading-word matches against the records PDF;
- the paper and primer PDF text against the base;
- `??` counts;
- the Q4 pair against App. J's rows;
- a sentence-level sweep of the posted PDF for superseded values;
- `test_build_all.py` (63 OK) and `--mutate` (10/10), in a copy;
- the lint, its self-test and a planted body pointer;
- containment on a real rebuild with six planted mutants;
- a real xr duplicate-label build;
- the corrected token boundary against all three outward PDFs;
- that the repository is public, so the `NoteRecords2026` URL is reachable.

**Not checked:**
- `check_note_records.py`'s own logic and its self-test. I used my own checks instead.
- `test_check_sec4_receipts.py` and its 3 failures, which the implementer says predate the move.
- `--export-deposit`.
- The PET note, which Q1 put out of scope.
- The records document read as a whole for register.
- Page-by-page visual inspection of either PDF.
- The standalone note repository sync.
