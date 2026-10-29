# r21 writer brief: the paper body, rewritten from a reverse outline and a fact ledger

**For:** the r21 writer, one Opus 5.5 session for all four batches (director's ruling 3, 2026-10-29). This brief, the
reverse outline (`reverse-outline.md`) and the fact ledger (`fact-ledger.md`) are your only inputs. **You do not see the current prose of the paper,** and you
must not open `docs/analysis-note/paper_body.tex`, its PDF or any earlier version of them. You may open the shared
preamble and the value files, to learn what each macro prints.

## What the paper is

It is a Physical Review D article of about 11 pages: an unbinned OmniFold measurement of the ν_μ charged-current
inclusive cross section on hydrocarbon in five observables, from MINERvA open data, reported in sixteen cells with a
covariance, with a two-dimensional benchmark and validation studies. A long companion analysis note holds the detail.
The paper points to the note with `\nsec{label}` (a section of the note), `\napp{label}` (an appendix of the note) and
`Ref.~\cite{AnalysisNote2026}`. The title, the abstract, the acknowledgments and Data Availability are not yours.

## The target

It should read like a well-edited PRD measurement paper:
- the measurement first, then how it was made, then how it was checked, then the result and its comparisons;
- methods and results stated directly, each claim once, with its scope built into the sentence;
- each limitation stated once, at its home: the body section with the evidence, and the one numbered Limitations
  subsection;
- one pointer to the note about once per subsection, as a plain clause at the end of a paragraph;
- no bookkeeping, history or process narrative.

The rules R1–R10 of `../register-prd-study/REPORT.md` (lines 305–380) are your style rules. They are already applied
to the structure; apply them to every sentence you write.

## Hard rules

1. **Every fact in the ledger prints.** Each row's atoms (macros, numbers, citations, references and qualifier words)
   must appear in your text, in a sentence that states that row's fact. No fact may be added, strengthened, broadened
   or dropped. If two rows are one fact, keep both atoms in one sentence.
2. **The guardrail:** a qualifier stays wherever leaving it out would make a sentence false as read. KEEP rows are
   these qualifiers. HONESTY rows are disclosures and limitations; state each once, plainly, beside the result it
   bounds.
3. **Verbatim rows:**
   - GATE rows are phrases that a check binds exactly. Print each GATE atom verbatim.
   - The FROZEN row, "Interval coverage has not been validated.", prints verbatim as its own sentence in Sec. I.
   - Tables and figure environments are copied verbatim from their ledger rows; you may reword their captions only
     under rule 1.
4. **No new number.**
   - Where a ledger atom is a macro, print the macro, never its value.
   - Where an atom is a literal number (for example `$4.12$`, `20 pseudo-experiments` or `10--13\%`), type it exactly
     as the atom gives it.
   - Never type a number that no atom holds. The checker fails any numeral in your prose that the base does not print.
5. **Structure:**
   - Keep every `\section`, `\subsection` and `\label` of the outline, in the outline's order, with the same label
     names. The note and the checks refer to them.
   - Paragraph order inside a subsection may change, and paragraphs may be merged or split.
6. **Do not touch** `main_paper.tex`, the note's files, `values*.tex`, the figures, the `.bib` files or any check.
   Write only to your output directory.
7. **No outside models, no git, no outward act.**
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## APS mechanical conventions (added by the director's ruling 1; the r21 report credits them separately)

- Numerals with units, and for numbers 10 and above. Spell out one to nine for counts without units, except in a
  series that also holds larger numbers ("10, 15, or 20 iterations"; "two tunes").
- The serial comma: "A, B, and C".
- "Fig.", "Figs.", "Eq.", "Sec." and "Ref." inside a sentence, with a nonbreaking space (`Fig.~\ref{…}`). The full word
  "Figure" or "Section" at the start of a sentence.
- No semicolon to splice a result to its caveat (R10). Use two sentences.
- No parentheticals nested in parentheticals, and no colloquial intensifiers ("far", "so it keeps").
- Hyphenate compound modifiers before a noun ("five-observable result", "sixteen-cell covariance").

## Batches (one session, in order)

- **b1:** Sec. I (Introduction), Sec. II (Data, simulation, and observables), Sec. III (Cross-section extraction).
- **b2:** Sec. IV (Uncertainties and validation).
- **b3:** Sec. V (The sixteen-cell cross section).
- **b4:** Sec. VI (Discussion and conclusions), including the Limitations subsection.

After each batch, stop. Deliver `b<k>.tex`, the LaTeX of your sections, and `b<k>-ledger.md`, the ledger rows of
those sections with an `after` column: for each row, the exact sentence of yours that states the fact. A fresh
reviewer then reads the batch before you write the next.

## Checks you run before delivering a batch

- Every atom of every row of the batch occurs in `b<k>.tex`, checked by script, not by eye.
- Every numeral in your prose is one the ledger's atoms hold.
- Every GATE and FROZEN atom occurs verbatim.
