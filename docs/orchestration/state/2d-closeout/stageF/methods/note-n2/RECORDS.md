# Note register round n2: the records additions (first commit, 2026-10-26)

**Base:** origin/main `be045af4`. This commit changes the records document and the records checker only. No note
prose changes; the prose commits follow, after the pin.

**Authority:** the director's rulings of 2026-10-26 on the n2 outline: N2-1(a), R-N2b (b), and the six conditions
on N2-1(a). They are recorded in the n2 outline.

## What is added

**App. G (`app_provenance.tex`).** A second full-width list follows the first, with a one-sentence lead-in. Its six
entries are new paragraphs, so no existing record paragraph changes (P5 PASS, no R-EDIT row).

| entry | what it holds | source |
|---|---|---|
| `2d-central-value` | its table row's record cell, then the note's provenance sentences for the purity-subtracted seed-42 central value | row: `tab:prov-paths`; sentences: `sec_method.tex:144-148` |
| `flux-index` | its tracker row's two record cells, joined by a colon | the tracker table row |
| `response-diagnostic` | its table row's record cell | `tab:prov-paths` row |
| `rank-inversion` | its table row's record cell | `tab:prov-paths` row |
| `july-sweep` (**new tag**) | the July sweep's provenance | `sec_systematics.tex:214-218` |
| `bkg-mode-elimination` (**new tag**) | how purity is established for the July 2026 endpoint unfolds | `app_negweight.tex:284-291` |

**The two new tags are additions, not renames.** No existing tag changes (P2 PASS). Each new tag is lower-case and
hyphenated, like the existing ones. The records' tag list, `g_tags`, which RECORDS-PIN Q3 reads at the pin, now
contains both.

**N2-1, the numbering (`main_records.tex`).**
- Both full-width lists are wrapped in a group whose description label format steps a counter and writes
  `\label{rec:<tag>}`. The entries print as R1.1–R1.17, after the records section that holds them (Section R1,
  "Provenance"), and `\ref{rec:<tag>}` prints the same number.
- Each label must hold exactly one `\texttt{<tag>}`. The tag is reset for every item, and a label with none or two
  stops the build with a named error. A scratch test confirmed both stops; a good list builds and numbers.
- `app_provenance.tex` is not edited for this, so P5 sees no change.
- The records PDF has 56 pages, up from 55, with 0 undefined references.

## The director's conditions

**1. A repeated record can't drift.**
- `check_note_records.py` gains **P9**, which has three parts:
  - every App. G table row parses into cells. Rows and cells split only outside braces, so a `\\` inside a
    `\shortstack` cell or an escaped `\&` splits nothing;
  - every tag that the posted note cites with NoteRecords2026 has a full-width entry, which the records number;
  - every full-width entry whose tag has a table row with a record other than "see below" contains that row's record
    cell(s), normalized.
- P9 checks 11 cited tags and 4 repeated records, and prints both counts on the probe's summary line. The 11 tags
  with "see below" rows are skipped.
- `2d-central-value` carries more than its row, and P9 checks the row part.
- Four self-test plants, each firing its own P9 message:
  - `flux-index`'s entry changed from "row 91" to "row 92";
  - `flux-index`'s entry deleted;
  - a record put into the `\shortstack` row of `flux-repair`;
  - a table row merged into the one before it, so it no longer parses.
- **The copies are protected.** `records-move-ledger.md` gains rows L-n2-1 to L-n2-6. Each carries an R: probe of its
  entry's whole printed text, so an edit to any copy fails P7.
  - Test: changing july-sweep's "$10^{-11}$" to "$10^{-10}$" in a scratch copy fails row L-n2-5.

**2. (A), (C) and (D) are copies, not paraphrases.**
- Each entry contains its note source verbatim. A mechanical check found each normalized source span inside its
  entry. The one change: (A)'s citation of its own tag `2d-central-value` was dropped inside that entry.
- agy checked each entry against its source, quoted with file:line, plus the three repeated rows (`records-agy/`).
  - **Run 1:** 3 AGREE, 4 REVISE. All four REVISEs were my input errors, not entry defects:
    - for REC-2 and REC-3, my source line ranges stopped one line short, so the entries' last words looked added;
    - for REC-1 and REC-4, I split the composite `2d-central-value` entry into two sources, so each half looked
      added to the other.
  - **Run 2**, with exact source spans and one composite source: **6 of 6 AGREE.**
- The R: probes come with the prose commits. Each removes or compresses a note sentence only once an R: probe shows
  the record prints the fact. n2's `check_ledger.py` supports R: probes, restricted to the records files.

**3. What the records already held, found by meaning.** For each fact the note can drop because the records already
hold it, here is the matching records sentence:

| note text | records text that holds it |
|---|---|
| "Its ten endpoint unfolds used the driver's purity default and are recorded as purity controls, not publication inputs" (`app_negweight.tex:357-359`) | "Both FPS unfold launchers omitted `--bkg-mode` entirely, so the ten endpoint unfolds ran on the driver default `--bkg-mode=purity`; they are recorded as purity controls at …" (`app_provenance.tex:203-205`, fps-battery) |
| "Two provenance limits travel with the production numbers: the driver was uncommitted when they were written, so its executing revision is corroborated by a version-specific log line rather than pinned by a digest, and no output records the job that produced it" (`app_negweight.tex:36-39`) | "Two provenance limits travel with the production numbers: the driver was uncommitted when those outputs were written, so the executing revision is corroborated by a version-distinct log string rather than pinned by a digest, and no output carries a producing job identifier, which no later run can supply." (`app_provenance.tex`, negweight-hpss) |

My first search for the fps-battery fact used the literal words "purity default" and missed the record. The
condition exists because of that miss. Every later "already held" decision in n2 is entered in this table, with
the matching sentence.

**4. Consequences that stay in the note.** These parts bear on printed numbers and stay in the note, compressed:
- "reproduced to $1.4\times10^{-11}$";
- "seven universes reproduced, the others accepted by inference";
- "its seed was not fixed".
The prose commits keep them, each with an N: probe.

**5. The pin.** After this commit, NoteRecords2026's URL (`technote.bib`) moves to this commit's sha, in its own
commit. This commit is never amended, rebased or squashed. The PR body names the sha and the ancestor check.

**6. Tags.** Covered above.

## Not added: (B), the exact-split seed

The outline put (B) in the `2d-central-value` entry. That was my error.
- (B) is about the exact-split cross-check: "Its seed was not fixed: its production job script passed no seed, and
  the driver version it ran had no seed option, so scikit-learn's `random_state` was `None`; the run's own log was
  not found" (`sec_method.tex:175-178`).
- `2d-central-value` is the record of the LightGBM file `2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root`.
- So (B) is not added here.
- **Director's ruling (2026-10-26): (B) stays in the note.** The seed sentence explains the status of a printed
  number, the exact-split $\chi^{2}$, so under ruling 1 it stays in the note. It is compressed only as far as the
  guardrail allows, keeping "its seed was not fixed" and its reason, the missing seed option. No tag is added.

## Checks at this commit

- **`check_note_records.py`:**
  - probe: PASS (P1–P9);
  - `--self-test`: PASS, 34 of 34 planted defects fired and 3 of 3 silent. The four P9 plants are included, and so is
    the digest-message check.
  - pin: PASS;
  - `--self-test-pin`: 9 of 9.
- **One existing plant was repaired** (a change to the checker's tests; accepted by the director, 2026-10-26).
  - **Before the repair**, with the new entries in place, the self-test failed:

    ```
    FAIL lost repository path: expected a failure starting 'P4 repository path', got ["P5 RECORD paragraph not verbatim in the records closure: …
    RECORDS-MOVE SELF-TEST :: FAIL (delivered move silent: True; 30 of 31 planted defects fired their probe; …)
    ```

  - **The reason.** The plant replaced only the first `\repopath{` in App. G. That path, `response-diagnostic`'s,
    now prints twice: in the table row and in its repeated entry. Losing one copy no longer loses the path, so P4
    stays silent.
  - **The repair.** The plant now removes every copy of that path, which is the defect it names: a path lost from
    the records. After the repair: `fired  lost repository path -> P4 repository path docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md missing from …`,
    and the self-test gives 31 of 31.
- **`build_all.sh`:** rc 0.
  - Pages: note 120, records 56.
  - 0 undefined references.
  - RESULT, SEC4-RECEIPTS 15/15, RECORDS-PIN and BODY-POINTERS all pass.

## The two-direction review of the first version (before the pin)

The review was a fresh reviewer, working from the commit and the rules only. **Verdict: ADOPT-AFTER-FIXES.** It found
that every copy is verbatim, every repeated row exact, and no existing paragraph changed. Its findings, and what was
done with each:

| finding | what was done |
|---|---|
| B1: the committed MANIFEST.tsv listed an untracked file, so `generate_manifest.py --check --at-sha <commit>` failed | regenerated with `--committed-only`; `--check --at-sha HEAD` passes |
| S1: "G.n" clashed with the posted note's own App. G (its subsections G.1–G.4) | the entries now print as R1.n, after their records section; a records number always begins with R |
| S2: P9 dropped a table row with `\\` inside a cell (flux-repair), and "the other 10" was 11 | rows and cells now split only outside braces (29 rows parsed, flux-repair included); corrected to 11 above; a plant covers it |
| S3: P9 could pass while checking nothing (a renamed or deleted entry, a label without its period, a table that no longer parses), and printed no count | parse floor; every cited tag must have an entry; labels without the period recognised; counts printed; plants for a deleted entry and an unparsable row |
| S4: the lead-in said "the tables above", but one table prints after the list | now "this section's tables", in the lead-in and its comment |
| N1: P9's containment runs one way only, so a shortened table cell passes | kept: P5 freezes the table paragraphs, so a shortened cell fails P5. Recorded here. |
| N2: `\&` split cells | fixed with S2 |
| N3: the label macro carried the previous tag over, and the last of two tags won | fixed (see the numbering above) |
| N4: the six new paragraphs had no protection | R: probe rows L-n2-1 to L-n2-6 (see condition 1) |
| N5: a garbled comment; `main_records.tex` still said R1–R4 were "moved without edits" | comment rewritten; the front matter now says R1 has had one pointer retargeted and six entries added, each recorded |
| N6: the verbatim copies keep the note's referents ("the existing endpoint unfolds", "the quoted universe block") | kept: condition 2 requires copies, not paraphrases, and each entry's tag names its subject. Listed here for the director. |
| N7: the rank-inversion entry's line is stretched in the PDF | kept: the entry must contain its row's cell verbatim (P9) |
