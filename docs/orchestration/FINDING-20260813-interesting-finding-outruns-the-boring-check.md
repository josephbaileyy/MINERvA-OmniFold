# FINDING 2026-08-13 — The interesting finding arrives before the boring check and outruns it

**`BEN-206`.** Infrastructure block (`200-209`). **Four instances, four independent parties, one
session** — and a fifth added below, which occurred *while this file was being written*.

**Authorship, CORRECTED 2026-08-13 — the row is the MEDIATOR's, not D's.** A first recorded it as D's,
in a commit message, in this file, and in a message to the mediator. It was written by
`personal-orchestrator`, which had **staged but not committed** it; D's role was to flag that `BEN-206`
was claimed in prose while absent from the ledger, opening a live `BEN-167` window where
`max(existing)+1` computes to 206 for any infrastructure filer. This long-form is lane A's, written
independently in the same minutes. The mediator has since backed its own copy out.

**AND THE MISATTRIBUTION HAS A MECHANISM WORTH MORE THAN THE CORRECTION.** A found the row *in the
shared working tree* and read it as an already-filed, settled fact — then deleted its own row on that
basis. **It was uncommitted.** This repo's first hard rule is that *a result does not exist until its
commit lands*; A treated a not-yet-existing row as existing, and the deletion was taken on it. Six
sessions share this checkout, so **"present in the working tree" means "someone is mid-write," not
"someone has decided."** The correct read of an uncommitted peer edit is a race in progress, and the
correct response is to ask whose it is — not to yield to it. (A's commit then captured the mediator's
uncommitted row, which is why it is in the ledger at all.)

**Kept rather than reverted, because the outcome is right for a different reason than the one A had:**
the mediator's row *is* better — sharper specifics, and the voluntary-self-reports observation below.
A yielded to it for a bad reason and got a good result, which is luck and is recorded as such.

**A near-miss the collision exposed, flagged by the mediator: the FILENAME namespace has no allocator
at all.** The mediator's long-form was `FINDING-20260813-interesting-finding-outruns-check.md` against
this file's `...-outruns-the-boring-check.md` — one word apart, same date, same subject. **An id
duplicate is caught by a grep and by the pre-commit hook; two long-forms a word apart would both be
indexable, both plausible, and whichever a future reader grepped first would win.** `BEN-172`'s
mechanism in a namespace with no rule.

**D's observation, kept because it is the strongest thing about this finding:** the four instances were
**assembled from voluntary self-reports, not from an audit.** Each party surfaced its own case when
nobody would have asked. That is evidence of a different kind than an auditor's list — an audit finds
what it looks for, whereas four parties independently volunteering the same shape is evidence about
the shape's frequency.

## The pattern

A result arrives that is **satisfying** — it is decisive, it is quantitative, it resolves the thing
you were stuck on, and it points the direction you expected. **The satisfaction is what makes the
next check feel redundant.** The check is then skipped, or deferred past the point where the number
has already been quoted to someone.

In all four cases below the check was **cheap** — one command, or one file read — and would have
caught the error. In none of them was the error a lapse in care: every party was actively exercising
verification discipline at the time, and in two cases was writing about verification discipline in
the same message.

## The four instances

**1. Mediator (`personal-orchestrator`) — the 7.7% dimensional mismatch.** Handed lane A `13.69%` as
the denominator for a materiality ratio, correctly warning *in the same message* not to mix
dimensionalities — and then mixed them, comparing a count shift on the 1D truth `E_avail` marginal
against the fractional uncertainty of a single 5D bin. Its own framing: *"I supplied both the caveat
and the violation of it, and the violation was the part that carried a number."* Measured, the
correct denominator is `4.62%`, not `13.69%` — the ratio is **22.7%, not 7.7%**, a 3x underestimate
in the flattering direction.

**2. D (verifier) — a `BEN-086` citation wrong four times across three messages and a verdict.** D's
own report; carried forward repeatedly without the cited row being opened.

**3. Lane A — the unit-weight marginalisation prescription.** Wrote into the OI-30 advisory that
closing the materiality question required "summing the sub-blocks over the other four axes." The
stored cross-section is a **differential density per unit bin-volume**, so marginalising is a
**width-weighted** sum; `project_cov_nd.py`'s docstring states outright that *"unit-weight M would be
WRONG for this convention."* Priced: unit weights give bin 1 = `12.38%` and a ratio of **8.47%** — a
2.7x underestimate that sits plausibly beside the ledger's `13.69%`. **The only thing that stopped it
shipping was reusing the tracked tool's `build_projection` instead of writing a fresh M**, which is
reuse functioning as a correctness control rather than a convenience.

**4. Lane C — an unanchored `replace(needle, repl, 1)`** scoping to the whole file rather than to the
intended row. C's own report.

**5. Lane A, while writing this file — a check that RAN and could not gate.** Filing the `BEN-206`
row, A ran the mandated collision check (`grep '^| BEN-206'`) **in the same shell command as the
write**. The check printed `| BEN-206` — already present, from the mediator's staged edit — but its output arrived only after the
insertion had executed, producing a duplicate id. **The check was not skipped; it was placed where its
result could not act.** This is the sharpest instance in the set: the discipline was followed, the
command was run, the output was correct, and the batching made it decorative. **A check that cannot
gate the action it guards is a check nobody reads, with extra steps** — and it happened during the
filing of a finding about skipped checks, which is the propagation argument making itself.

## Why it is worth a ledger row

The ledger's cost is paid on **every future read**, so truth and generality alone do not justify a
row — they have no upper bound and would justify everything. **Propagation does have an upper bound,
and it is the scarce evidence.** Four independent instances, four parties, one session, none of whom
were being careless, is the strongest propagation evidence this campaign has produced for any single
pattern.

## The check

**When a result lands that resolves your question in the direction you expected, that is the moment
the next check is most valuable and feels least necessary.** Spend it there.

Concretely, and cheaply:

- **Before a number leaves your session**, name the one check you skipped to get it out, and run that
  one. Not a review pass — a single named check.
- **A denominator and a numerator must come from different instruments** (`BEN-196`), and "different"
  includes *different dimensionality* — instance 1 satisfied the letter and not the substance.
- **Prefer reuse of a validated implementation over a fresh one at the moment a fresh one looks
  cleaner.** Instance 3 was caught by reuse alone, and would not have been caught by review.
- **A gating check must be able to gate.** Never batch a collision/precondition check into the same
  command as the write it guards — read its output, then write. Instance 5 cost a duplicate id despite
  the check running correctly.

## Related

- `BEN-196` — denominator from a different instrument. Instance 1 is that rule violated by the party
  restating it.
- `BEN-205` — reading *some* artifact rather than the governing one. Adjacent but distinct: there the
  failure was *which* artifact; here it is *whether the check happens at all* once the answer is
  satisfying.
- `BEN-210` / `BEN-211` — the `sstat` aliasing and the defective fix. `BEN-211` is arguably a fifth
  instance: the fix was satisfying (distinct readings, uniformity tell gone) and the attribution check
  was skipped.
