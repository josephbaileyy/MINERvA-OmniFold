# FINDING 2026-08-20 — the evidence that settles a referent question is usually inside one of the candidates

**`BEN-492`.** Lane B's nomination, from the `sec_systematics` PSD row.

## The move

A referent dispute asks which of N objects a sentence points at. Adjudicating compares the candidates
against the sentence and needs an external tiebreaker. But **each candidate carries its own
provenance** — a before-column, a creation date, an operand list — and reading one can contain the
sentence's own value and decide it outright. That is cheaper than adjudication and available more
often than it is used.

## The instance

The question: which matrices does *"Both were positive semidefinite"* refer to? It decides whether
`VL16`/`VL17`'s ratios may be quoted beside it. Two admissible resolutions were offered to the editor
and **guessing was forbidden**.

It was settled by reading a candidate. **`VALIDATION_LEDGER.md:187` records `VL16`'s median as
"13.36% → 13.57%", and 13.36% IS the struck `\gbdtFiveBlockMedian`.** So the struck block is
literally `VL16`'s **before** column, and `VL16`/`VL17` measure the **successors** of exactly those
matrices. That settles **direction**, not merely difference — which no external argument had managed.

Confirmed independently by chronology: the sentence entered `957c655f` on 2026-07-14 together with
the now-struck values, while `VL16` first appears at `1ec042e9` on 2026-08-12. **The sentence is a
month older than the rows it would have cited and cannot have been about them.**

## The failure it averted was live

The obvious edit — appending the two ratios to the past-tense sentence — would have attached
**new-product measurements to superseded matrices**: the inheritance error that procedure row exists
to prevent, running backwards. The row states the PSD claim is *"a property of the new matrices."*
