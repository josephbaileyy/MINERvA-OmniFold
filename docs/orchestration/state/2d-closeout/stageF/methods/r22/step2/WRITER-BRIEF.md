# r22 Step 2: the note writer's brief (common to all 15 pieces)

You rewrite one piece of a long technical companion note (an analysis note posted to arXiv beside a PRD paper, on an
unbinned OmniFold cross-section measurement with MINERvA open data). The goal is register: make the prose read like a
well-edited long technical write-up in particle physics, such as a long PRD or JINST paper. Two raters named the gaps,
and your piece's list gives them (`step2/briefs/<piece>.md`). You fix those gaps, and only those, in the LaTeX
sources. Every fact stays.

Paths:
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  is the repository worktree. Your files are in `$WT/docs/analysis-note/`.
- `R=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/4834bf2d-a370-41b8-ae11-7b9d48874031/scratchpad/r22`
  holds the briefs and tools.

## What you may change

- **Only the .tex files your list names.** Never edit any other file in the repository, including `main_note.tex`,
  `values*.tex`, the records files (`app_provenance.tex`, `app_history.tex`, `*_records.tex`, `records_*.tex`) and the
  paper (`main_paper.tex`, `paper_body.tex`).
- **Wording:** rewrite a sentence in place. This covers:
  - replacing internal labels and shorthand with standard terms, or defining them at first use;
  - splitting long sentences;
  - removing evaluative or conversational wording;
  - stating a result before its qualifications.
- **Structure,** where the gap's CHANGE asks for it: merge, move or cut passages within your files, or convert a list
  to prose and back.
  - A cut must leave each fact printing somewhere in the note (an `N:` probe), or, for the cases below, in the internal
    ledger (an `R:` or `L:` probe).
  - The ledger cases are:
    - records: provenance tags, record identifiers, commit and record chronology, and superseded values, whose home is
      the records document (`R:`);
    - implementation detail (code flags, class and function names, file paths, file sizes, merge steps), only where
      your list names a ledger home (`L:` or `R:`);
    - gap B04-g-09's history, whose home is named in the B04 list.
- **Your list's "pattern" gaps:** the rater saw several passages like the quote. Fix the like passages in your files
  too, with each in the ledger.

## What you must not change

- **No claim and no number changes.**
  - Keep every macro (`\covTwoDCTwo`, `\SI{…}`, `\uqMedian`, …) as a macro; never type its value.
  - Keep every `\label`, `\ref`, `\cite` and equation.
  - Add no new fact, citation or claim.
- **The truth guardrail.** A qualifier stays where leaving it out would make the sentence false as read. Examples:
  "has not been tested", "not validated", "descriptive", "conditionally on …", "within the implemented simulation
  model", "not held-out", "does not cover …", "for reporting only". You may reword a qualifier and attach it more
  tightly to its claim, but not drop or weaken it.
  <!-- absence-ok: quotes printed qualifiers and limitations of the note as examples or as gaps; not a claim that a result is absent -->
- **Disclosures and limitations stay printed in the note.** This covers post hoc choices, things not run or not
  validated, missing logs or provenance limits, and the reasons a result is not graded. You may state each once, in a
  cleaner form, where it qualifies its result, and cut pure repetitions whose fact still prints elsewhere in the note.
- **The out-of-scope sentences** in your list stay exactly as they are.
- **Gate-bound phrases** in `sec_validation.tex` stay byte-identical: "lies entirely below its window (Gaussian 0.954)"
  and "removes the tail undercoverage: $C_2=0.977$ $[0.974,0.980]$ and $C_1=0.781$".
- **Length:** do not lengthen the piece overall. A definition you add at first use should be short.

## Special cases

- **B01:**
  - **The two abstract gaps (B01-s-04, B01-s-10).** Do NOT edit `main_note.tex`. Write proposed before/after pairs to
    `$R/step2/abstract-pairs.md`. Each `before` is the exact current source text of the abstract sentence, and each
    `after` is your proposed text, with every fact kept. The director pins them and passes them to Joseph before
    adoption.
  - **B01-s-02 and B01-s-06** may be reworded. Your ledger rows must probe the facts:
    - B01-s-02: every lost draw was rerun and observed, for reporting only;
    - B01-s-06: readiness for publication as a measurement has not been established, with exactly that meaning.
- **app_release.tex (B15):** every claim about the release package must stay true of the package. Do not change what
  is said to exist, be deposited or be reproduced.

## The fact ledger: write `$R/step2/ledger-<piece>.md`

One markdown table: `| id | fact | before | disposition | after | probe |`.
- **id:** `<piece>-<n>`, for example B03-1.
- **before:** the sentence id or ids from the checker's `--list` (a file prefix and an index, such as SY12), for every
  base sentence you changed. Each changed base sentence must appear in some row's `before`.
- **disposition:** REWORDED, MERGED, MOVED, CUT-NOTE (the fact prints elsewhere in the note), CUT-RECORDS (`R:`),
  CUT-LEDGER (`L:`) or SPLIT.
- **after:** the new text, briefly.
- **probe:** one or more, joined by ` && `:
  - `N:<file>::<text>` prints in `docs/analysis-note/<file>`;
  - `X:<file>::<text>` no longer prints there;
  - `R:<records file>::<text>` prints in a records file;
  - `L:<repository path>::<text>` prints in that repository file at HEAD (the ledger homes named in your list).

  The text is the comment-stripped, whitespace-collapsed LaTeX source, so write macros as they appear in the source.
  Every fact a changed sentence carried needs a probe at its home after your change.

Check your work with the checker, until it reports 0 failures:

```
python3 -I $R/step2/check_ledger.py $WT --no-n4-frozen --files <your files, comma-separated> --ledger $R/step2/ledger-<piece>.md
python3 -I $R/step2/check_ledger.py $WT --no-n4-frozen --files <your files> --list   # your changed base sentences
```

## Rules of work

- Read-only outside your files and your ledger file (plus `abstract-pairs.md` for B01).
- No git command that writes. No build. No model, CLI or network call.
- Other writers are editing other files at the same time. Do not touch them.
- If a gap cannot be fixed without breaking a rule above, skip it and say why.
- **Report back** in under 250 words:
  - each in-scope gap, as fixed, partly fixed or skipped, with the reason for any skip;
  - the checker's last line;
  - your words-before and words-after for your files (`wc -w`);
  - anything you were unsure of.
