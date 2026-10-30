# r22 gap classification: the brief

You classify each gap a rater named, using the rules below and nothing else. Read-only: change no file except the one
output file you are told to write.

## Inputs

- `gap/gaps.tsv`: one row per gap. Columns: id, input, model, n, share, located, scope, quote, problem, change.
  The rater's CHANGE is what you classify. QUOTE and PROBLEM tell you which text it is about.
- The rated texts, to read each quote in context:
  - the paper: `gap/inputs/paper/manuscript.txt`;
  - the note pieces: `gap/inputs/<B01..B15>/chapter.txt`. Each is one part of the analysis note (the long companion
    document). B01 holds the note's abstract.
- The protections, in the repository at `REPO=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`:
  - `$REPO/docs/orchestration/state/2d-closeout/stageF/methods/protections-inventory-20261028/REPORT.md`. Items A1–A8,
    B1–B5, C1–C23 and D1–D7, with where each prints (its file:line refers to an older commit; match by wording). §4 lists
    the HONESTY-required items: B1, B2, B3, C1–C9, C11–C17, C20–C22.
  - `$REPO/docs/orchestration/state/2d-closeout/stageF/methods/r21/ledger.md`: the paper's fact ledger, one row per
    fact, with status KEEP, HONESTY, GATE, FROZEN, ORDINARY, STRUCTURE or PROTECTED, and each fact's sentence as it now
    prints in the paper. It covers the paper only.
  - Gate-bound phrases (B4). Paper: the eight GATE phrases listed at the top of `r21/ledger.md`. Note: in
    `sec_validation.tex`, "lies entirely below its window (Gaussian …)" and "removes the tail undercoverage: C2=… […]
    and C1=…".
  - The FROZEN sentence (paper): "Interval coverage has not been validated."
    <!-- absence-ok: names a protected printed sentence; not a claim that something has not been run -->

## The rules (RULES.md §5, verbatim in substance)

Each gap gets exactly one class.

1. **PROTECTED** if the rater's CHANGE would do any of these:
   - reword text whose wording is Joseph's: inventory A1 (Data Availability), A4 (the abstracts: the paper's abstract
     and the note's abstract), A5 (the title);
   - change what a claim states (A7);
   - reword a gate-bound phrase (B4; the ledger's GATE rows) or the FROZEN sentence;
   - drop or weaken a KEEP or guardrail qualifier (B1: a qualifier stays where leaving it out would make the printed
     sentence false as read; B3: the KEEP list);
   - remove an HONESTY-required fact from the document, or move it to the note where the result it bounds stays
     (inventory §4: C1, C5, C7, C8, C11, C12, C17, C20). "Remove" includes deleting it, or sending it to "the
     records", "the repository" or "supplementary material" outside the two documents. B2 ("no fact leaves both
     documents") is HONESTY-required: a fact deleted from the note, or sent from the note to the records, leaves both
     documents unless the paper also states it; a fact deleted from the paper leaves both unless the note states it.

   One exception is decided: **records** may leave the note for the repository records
   (`$REPO/docs/orchestration/DECISION-20261021-joseph-da-and-note-records.md` item 2: "The records leave the note's
   published build: provenance tags, struck and superseded values, withdrawn results, commit and record chronology").
   Sending records of that kind (commit hashes, file or script paths, receipt or job identifiers, record chronology)
   from the note to the repository is STRUCTURE, not PROTECTED, whether or not the CHANGE names the repository as the
   destination. A limitation, a disclosure, a qualifier or a result is not a record in this sense, and C2's history
   must stay printed in the note (inventory C2).

   **How B2 is applied here.** A CHANGE that deletes, or generalizes away, a limitation, a disclosure, a qualifier, or
   a reported number or finding, with no copy left in either document, is PROTECTED (B2, plus the C item if one governs
   it). A CHANGE that deletes implementation detail (a code flag, a file size, a merge step, a software name) that is
   none of those is STRUCTURE; write `cut` in `item` so the report can list these separately, since a strict reading
   of B2 would need Joseph's lift for them too.

   Each PROTECTED record names the inventory item or ledger row (for example "B1", "C9", "B2", "A4", "F184 GATE"),
   with the exact sentence (the QUOTE, or the sentence the change would alter).
2. **STRUCTURE** if it is not PROTECTED and the change moves, cuts, merges or splits passages or sections, converts
   prose to a list or table, or sends text to the note, an appendix or the records. A cut of words that carry no fact
   (for example a repeated statement whose fact stays elsewhere in the same document, or a sentence that only says where
   something is) is STRUCTURE.
3. **WORDING** otherwise: a rewrite in place that keeps every fact and qualifier. Replacing an internal label with a
   standard term, splitting a long sentence into two in place, or removing a word that carries no fact is WORDING.

- A mixed change takes the highest class: PROTECTED > STRUCTURE > WORDING.
- A gap these rules cannot place is UNRESOLVED. Give the reason.
- A gap whose `located` is UNVERIFIED is not classified: write UNVERIFIED.

**How to decide hard cases.** Judge what the CHANGE, carried out as written, would do to the quoted text. Do not
judge whether the rater is right about the register. If the CHANGE says "delete" or "remove" a sentence or clause,
ask what fact it carries and whether that fact still prints elsewhere in the same document after the change (read the
rated text). If it says "condense", "trim" or "state once", ask whether a qualifier or fact would go. Hedges that
the guardrail keeps are qualifiers whose omission makes the sentence false: for example "has not been tested",
"descriptive", "within the implemented simulation model", "conditionally on …", "not held-out", "does not cover …".
<!-- absence-ok: lists printed qualifiers as examples; not a claim that a result is absent -->
A qualifier that only repeats a scope already stated in the same sentence or paragraph is not one.

## Output

A TSV with header `id	class	item	reason`, one row per gaps.tsv row, in the same order:
- `class`: PROTECTED, STRUCTURE, WORDING, UNRESOLVED or UNVERIFIED;
- `item`: for PROTECTED, the inventory item(s) or ledger row(s), comma-separated; otherwise empty;
- `reason`: one short sentence; for PROTECTED, name the fact or qualifier the change would drop, move or reword.
