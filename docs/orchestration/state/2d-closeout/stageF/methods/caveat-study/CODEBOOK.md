# Codebook: caveat inventory (caveat study, 2026-10-25)

You inventory every **caveat** in one document's text file. A caveat is a statement that limits, conditions, or
discloses a weakness of the document's own method, result, or claim. You classify each one. Read the whole file.

## What counts

Count a statement only if it qualifies **the document's own** work: its method, validation, result, uncertainty, or
claim. Do not count:
- results about other people's work;
- physics findings stated as findings (for example "the data lie below the prediction");
- ordinary uncertainty statements that just quote a number ("the flux uncertainty is 8%"), unless the sentence also
  says something is omitted, untested, assumed, or restricted.
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

## The five kinds (pick exactly one per instance; if two apply, pick the one the sentence is mainly about)

| kind | what it is | examples of the shape |
|---|---|---|
| (a) HISTORY | the history of superseded work by the authors: an earlier version of the method, selection, band, result or analysis that was replaced; what was tried and abandoned; development narrative ("initially", "an earlier version", "was later replaced", "in a previous iteration") | "An earlier version of this analysis used …"; "This supersedes the result of Ref. [x]" |
| (b) DEVIATION | a departure from a predeclared, planned or blind procedure, or a choice made after seeing the data or results (post hoc, after unblinding, changed after review), with or without its consequence | "After unblinding, we found … and corrected …"; "The binning was chosen after …" |
| (c) UNTESTED/OMITTED | a property that is not tested, validated, measured or shown; an effect, uncertainty or correlation that is not included, neglected or assumed away; an assumption the result rests on that is not demonstrated | "This effect is not included in the uncertainty"; "We assume …"; "has not been validated"; "is neglected" |
| (d) SCOPE | a restriction of the domain of a claim: phase space, conditions, configuration, "in simulation", "this is not a measurement", "the conclusions apply only to …", "within the model" | "The result is restricted to …"; "This study is limited to one-dimensional examples" |
| (e) PROCESS | vocabulary of the project's internal process, not of physics: workflow, review, approval, freezing, internal record or ticket names, decision or receipt language, "the collaboration decided" | "The analysis was frozen before …"; "approved by the collaboration"; "per the internal review" |
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

Process vocabulary that the field uses as method (for example "blind analysis", "the box was opened") is still (e):
record it, and note in `phrasing` that it is a standard field term.

## Fields, one row per instance (tab-separated, no tabs inside fields)

`n	kind	loc	polarity	quant	assigned	issue	quote`

- `n`: running number.
- `kind`: a, b, c, d or e.
- `loc`: where the statement is, one of
  - `abstract`;
  - `intro` (the introduction or overview);
  - `inline` (in the methods or results text, where the thing it qualifies is described);
  - `syst` (a section or paragraph devoted to systematic uncertainties);
  - `limits` (a section, list or paragraph devoted to limitations, caveats, discussion of weaknesses);
  - `concl` (conclusions or summary);
  - `appendix` (an appendix or supplement);
  - `caption` (a figure or table caption, or a footnote).
- `polarity`: `pos` if the sentence leads with what holds and puts the limit inside it ("The method is validated for
  X; Y is not tested"), or states the limit as a positive definition ("The result covers …"); `neg` if the sentence
  leads with or consists of a negation ("No … has been …", "It is not …", "cannot").
- `quant`: `yes` if the caveat carries a number that sizes it (a magnitude, a bound, a fraction, a count); `no`
  otherwise.
- `assigned`: `yes` if the document converts this caveat into an assigned uncertainty (a systematic, an error band,
  a non-closure uncertainty); `no` if it does not; `partly` if partially.
- `issue`: a short label (3-8 words) for the underlying caveat, the SAME label each time the same caveat is restated
  anywhere in the document, so repetitions can be counted. Example: "flux model dependence of unfolding".
- `quote`: the statement, copied **exactly, character for character** from the text file, as one contiguous
  substring of 6-40 words that lies on ONE line of the file or spans lines only at whitespace. Do not fix spelling,
  ligatures or hyphenation. Do not paraphrase. The quote is verified mechanically: a quote that is not a substring of
  the file (after whitespace is collapsed) is discarded.
<!-- absence-ok: names the caveat category "untested or omitted" used to classify statements; not a claim that any result is absent from the repository -->

## Rules

- One instance per sentence. If one sentence states two caveats of different kinds, make two rows with the same quote.
- A caveat restated in another section is a new instance with the same `issue` label.
- Be exhaustive. Read every section, including captions and appendices in the file.
- Do not judge whether the caveat is right. Classify only.
- Write nothing except your output file.

## Output

1. The TSV rows, written to the output path you are given, with the header line above.
2. A reply of at most 200 words: the counts per kind, the number of distinct `issue` labels, the sections where
   caveats cluster, and anything in the document that did not fit the codebook.
