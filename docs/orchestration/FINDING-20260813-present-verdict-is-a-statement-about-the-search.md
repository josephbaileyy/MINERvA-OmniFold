# A PRESENT verdict is also a statement about the search

**EP-2026-08-13-closeout. Four instances, two parties, one session.** Indexed from `FINDINGS.md` as
`BEN-207`. Pairs with `BEN-172` (a wrong citation to a REAL id resolves, and the reader stops) and
`BEN-086` (an `UNSOURCEABLE` verdict is a statement about the SEARCH, not about the value).

## The mechanism

`BEN-086` established that an ABSENT verdict describes the search rather than the value. **The other
half was never stated: a PRESENT verdict describes the search too.** A tool asked a narrow question
returns a narrow answer, and the answer gets read as covering the broader question that motivated it.

**This defeats the obvious defence.** `BEN-172`'s cite-without-opening is caught by "check your
sources" — the fix is to open the thing. This one is not. In all four instances below **the source
existed, was consulted, and the disqualifying content was inside the output already on screen.** The
citation is not to a wrong artifact; it is to the right artifact and the wrong content.

## The four instances

**1. Mediator — grepped a key, took its presence for a field.** Cited
`gate2_target_runtime.py:727` as evidence a receipt carried a TensorFlow version. The grep printed
`"tensorflow": "not imported/not required for target-only Gate-2 validation"` — the key and the
disqualifying constant on the SAME LINE of the output being read. Comparing that field between two
receipts returns MATCH for any two runs. Had it not been caught, it would have produced a vacuous
comparison that prints a pass, in a check whose whole purpose was to discriminate.

**2. Mediator — cited the producer the grep matched, not the producer that runs.** The Gate-6
members are trained by `train_fullevent_nominal.py`; the cited environment block lives in
`gate2_target_runtime.py`. The grep matched, so the file was cited. The correct file writes **no**
environment block at all — which turned out to be the sharper finding, and was reached only after
the citation was challenged.

**3. Session D — read a truncated row and concluded absence from the whole index.** Read index row
72 through `cut -c1-230`, saw five locations, and concluded the receipt was absent from the entire
index. The truncation was the searcher's own, applied one command earlier.

**4. Session D — tested membership against the wrong scope.** Evaluated `'56563761' in t` against
the ENTIRE document rather than the intended section, got `True`, and nearly reported the opposite
conclusion. The test answered exactly what it was asked.

## What is common to all four

| | |
|---|---|
| the tool | answered exactly the question posed |
| the answer | was read as covering a broader question |
| the correction | was already inside the output on screen |
| "check your sources" | would not have caught any of them |

## The check that does catch it

**Before citing a grep result, read the line the grep returned — not the fact that it matched.** And
name the scope the search actually covered, then ask whether it is the scope the claim needs:

- a key's presence is not a field's existence — read the value
- a match in file X is not evidence X is the producer — confirm what runs
- a truncated read supports no claim about what was truncated away
- a membership test against a document supports no claim about a section

## The camouflage case, which needs a different fix

Instance 1 is worth separating because the defect is not a wrong value. The block reads:

```python
"sklearn": __import__("sklearn").__version__,
"platform": platform.platform(),
"tensorflow": "not imported/not required for target-only Gate-2 validation",
```

Real call, real call, **constant sentence**. The literal is camouflaged by the two live fields above
it: a dict of environment values reads as a dict of environment values, and the third entry inherits
the credibility of the first two. Nothing here is false.

This is the same shape as `p4_lib.py:1298`'s `"(preserves density/order)"` — a true statement read as
a stronger one — and it needs the same treatment. **The fix is not to correct a wrong thing; it is to
stop a true-looking thing from being read as more than it is.** Auditing either for truth returns
"true."

## Provenance

Two instances are the mediator's and two are Session D's, contributed by D specifically so the tally
would not sit in commit bodies where it flatters by being invisible. Same construction as `BEN-206`:
a row naming only other parties' cases would be the failure in miniature.

## Related

`BEN-172`, `BEN-086`, `BEN-206` (the interesting finding outruns the boring check), `BEN-205`
(reading some artifact is not reading the governing one), `BEN-212` (a status field is not an
artifact).
