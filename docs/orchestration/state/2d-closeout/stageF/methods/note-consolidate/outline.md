# Content PR: merge the repeats (CONSOLIDATE rows of the cost list). Outline for the director (2026-10-27)

**Authority:** Joseph, `DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md` item 1.
**Base:** main `602ab31f`. **Branch:** `stageF/note-consolidate-20261027`, created with no commits. No edits come before you approve this outline.
**What it is:** a content PR, not a scored register round. There is no P2N or P1N.

## Scope

**In scope:** every `[C]` site of the CONSOLIDATE rows in `note-n3/content-reduction.md`. A `[C]` site is a restatement that is removed and replaced by a pointer to the fact's single home, marked `[keep]`.
- **54 `[C]` sites in 21 rows:** R01, R02, R03–R18, R21, R26 and R27.
  - This includes the single `[C]` sites the list allows inside rows marked BOUND or NO REDUCTION: R02 (1), R12 (1), R16 (2) and R21 (1).
  - R01 and R17's ES/§12 part are included, by Joseph's ruling.
- **By file:**

| file | sites |
|---|---:|
| sec_5d | 8 |
| sec_3d | 6 |
| sec_systematics | 5 |
| sec_joint | 5 |
| sec_execsummary | 4 |
| result_status_rows (Table 1) | 4 |
| app_statmethods | 4 |
| sec_summary | 3 |
| sec_intro | 3 |
| sec_eavailw | 3 |
| selection_features (§2's table) | 2 |
| sec_validation | 2 |
| sec_method | 2 |
| app_negweight | 1 |
| app_guide | 1 |
| app_codebase (App. H, not release text) | 1 |

- **Re-location.** The list was measured on `e8c76937`, before n3's reverts and the audit merges. I re-located every site at `602ab31f`:
  - 96 of the 108 `[C]` and `[keep]` quotes are found mechanically;
  - the other 12 carry figure placeholders or macros, and the writer locates them by hand;
  - a site whose text no longer prints is reported, not invented.

**Out of scope:**
- every `[D]` site, and the DROP-only rows R19, R20, R22–R25, R28 and R29. They wait for Joseph and Ben;
- the protected files: values, values_inference, app_history, app_release, main_note (the abstract), main_paper and paper_body;
- release text, claims, KI-85, `\pubhold` and data-availability text;
- §5.2's check-bound band history, the SEC4 phrases and the `\covTwoDCTwo` uses.

## The move

At each `[C]` site:
- the restated fact is removed, and a pointer to its single home takes its place: `(\S\ref{<home label>})`, or "(see \S\ref{…})" where a clause must stay grammatical;
- the sentence must still be true as read. Where the guardrail needs the qualifier in that sentence, the site stays, and the REPORT lists it as kept;
- the home is not edited, apart from being made the single home where the list says so.

A pointer replaces text; it never adds a claim.

## Guards (Joseph's item 1, and the standing rules)

1. **Ledger** (`note-consolidate/ledger.md`, checked by a copy of n3's `check_ledger.py`, base `602ab31f`). One row per changed base sentence, with:
   - an `X:` probe for the removed restatement;
   - an `N:` probe for **every kept fact at its home**.
2. **agy** on each changed passage, with the home quoted verbatim in its context.
3. **printed_diff** on every scripted edit (only the intended sentences change), and **`reflow_tex.py --note --check`**.
4. **The note's gates:**
   - `check_note_records.py` probe, its self-test and pin. The probe reads `records-inventory-base.json`, which holds R15's "Two provenance limits" sentence; R15's `[C]` sites are in the configuration lists, and its `[D]` part is not applied;
   - entry numbers, the registry, absence claims (a changed paragraph keeps its Search line), the build (0 undefined references, SEC4 15/15) and pytest.
5. **The recount, before and after:** the cost list's own measure, on `602ab31f` and on the delivered tree:
   - distinct caveats per 1,000 words;
   - caveat statements per 1,000 words;
   - restatements per caveat;
   - words.

   The list's tools (`impact.py`, `locate.py`) are scratch files with hard-coded paths. I would port them into the PR as `note-consolidate/recount.py`, taking paths as arguments, so the figures can be re-run. **The expected effect, from the list:** about 1,285 words fewer from the `[C]` rows (the sum of their sizes in the list; the list's 3,300 includes the drops). The distinct-caveat count does not fall, because consolidation removes no distinct caveat, so the distinct rate rises slightly as words fall. Statements per 1,000 words fall, and restatements per caveat fall toward 1.9.

## Process

- **Two writers in parallel** (Claude Opus 5.5 subagents of the claude-school session):
  - W1: §2–§10;
  - W2: App. A–H, the ES, §1 and §12. W2 is written last for the ES and §12, against W1's body.
- **A fresh two-direction reviewer per writer.**
- **Then:** integration, agy, the gates, the recount, one PR to you.

## Questions for you

1. **Table 1** (`result_status_rows.tex`) has 4 `[C]` sites: R07 "calibration adequacy remains conditional", R14 "Earlier statistical band failed fixed-truth coverage; …", R17 "injected-bump closures have no recorded threshold", and R18 "learner chosen after the comparisons were known".
   - Table 1 is the ES's one-glance status table, and a cell that reads "see §x" tells the reader less at a glance.
   - Options: **(a)** apply them like the rest; **(b)** keep Table 1's cells, as the summary of summaries.
   - **I recommend (b).** The ES text is already consolidated by R01, so Table 1 would be the one place each status prints in short form.
2. **The recount tool:** port it into the PR as above (my recommendation), or report the figures from the scratch tools with their outputs attached?
3. Anything in the 54 sites you want excluded beyond Table 1.

## The director's rulings on this outline (2026-10-27)

1. **Table 1:** option (b). `result_status_rows.tex` is not edited; its four `[C]` sites (R07, R14, R17, R18) are kept, and the REPORT lists them as kept by this ruling.
2. **The recount tool:** ported into the PR (`recount.py`), with its outputs committed.
3. **No further exclusions.**
4. **A pointer in the executive summary or §12 points to the body home,** never to another summary.
5. **The six added sites** (the re-extraction found 60 `[C]` sites, not 54) are within the approval. `check_sites.py` cross-counts the disposition table against the cost list's own `[C]` count and fails on any difference.
