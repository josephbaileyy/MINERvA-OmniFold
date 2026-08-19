# FINDING 2026-08-19 — an injected reader is untestable for what it DISCARDS

**BEN-454.** Lane D (verifier), read-only, from an independent review of stage 1's anchor comparator
at the mediator's request. **The defect was invisible to a careful author, a full stub suite, and two
prior readers, and it took ninety seconds to see once the code ran against a real file.**

## The shape

Dependency injection makes a component testable by substituting its collaborator. The fixture supplies
what the real collaborator would **return**.

> **A fixture cannot supply what the real collaborator would DROP, because the dropped information
> never enters the fixture's world at all.** Every test therefore passes on a reduced object that the
> test itself constructed as complete.

This is not "the stub is unrealistic". A stub can be arbitrarily realistic about its **output** and
remain structurally silent about its **input**, and a lossy reader's defect lives entirely in the gap
between the two.

## The instance

`mii_anchor_comparator.read_keys_pyroot` returns, for every `TH2D`, **its diagonal**. `compare_files`
digests that; `mii_root_payload_classes.compare` compares the digests. So a PAYLOAD-class covariance
matrix is compared on its diagonal alone. Measured against the real archive
(`uq_5d/unified_throw_cov_5d.root`, `C_unified`), first execution of that function anywhere:

```
compared elements   10,694
total elements      114,361,636          ->  0.00935%
12 sampled full rows: sum|diag| 3.317e-79   sum|off-diag| 3.307e-76   ratio 997x
```

**The unchecked part carries roughly a thousand times the mass of the checked part**, in a gate whose
entire purpose is deciding whether member 0 reproduced the archive bit-exactly.

**The author's care is what makes this worth filing.** The docstring *justifies* the diagonal —
*"enough for every recomputation this comparator performs and avoids materializing a 34.7 GB matrix"* —
and that is **true**. It is true of the recomputation half, which needs only `trace(C) = sum(diag(C))`.
The same function is then reused as the payload extractor, where it is 0.00935% sufficient.
[`BEN-256`](FINDING-20260817-one-field-two-roles.md) at function scope: **a projection justified for
consumer A, silently inherited by consumer B.** The justification is not wrong; its *scope* is.

## Why the usual instruments miss it

- **Stub tests**: the fixture hands back an array named "the diagonal". There is no off-diagonal for
  the reader to lose, so no assertion can notice a loss. Not an oversight — **the discard is not
  representable in the fixture's type.**
- **Mutation review**: the real reader is **never executed by the suite**. Mutating it changes no
  observable, exactly as in [`BEN-452`](FINDING-20260818-a-probe-that-forces-a-guard-false-cannot-test-it.md).
  Distinct from `BEN-452` though: there the code ran in one direction only; **here the code under
  discussion does not run at all**, and something else stands in its place.
- **Reading it**: two prior readers and I all read the docstring's justification as covering the
  function. It does cover *a* use. Prose cannot tell you how many consumers a return value has.

## The check

1. **Ask what the collaborator DISCARDS, not what it returns.** Write the discard down explicitly —
   *"this reader drops every off-diagonal element"* — because it is the one property a fixture cannot
   carry. If you cannot state the discard, you have not read the collaborator.
2. **If a reduction was justified for one consumer, enumerate every other consumer and re-justify.**
   A projection is a claim about sufficiency, and sufficiency is per-consumer.
3. **Make the coverage a reported quantity, not an assumption.** A gate that says "bit-exact" should
   print the fraction it compared, which is `BEN-077`'s ingredients rule applied to a verdict.

## And the general lesson about first contact with real data

The parse was **fine**. `read_keys_pyroot` executed correctly on first contact — `TParameter<double>` →
`float`, `TParameter<int>` → `int`, TH2D → diagonal, TH1D → contents, no zombie, no `kRecovered`, two
files, 14.9 s and 20.6 s. The author's flagged worry ("my least-tested code") was **unfounded**.

> **First contact with real data is not a robustness test. It is a COVERAGE test.** What the real file
> supplies that no fixture can is *ground truth about size and structure* — and every claim keyed to
> that ground truth had drifted.

Second instance in the same act, same cause: `mii_root_payload_classes.FLAT_NBINS = 65856` describes
**no artifact**. Every matrix and per-bin array in all four archive files is **10694** — the `cv>0`
support, 16.24% of the 65,856-bin grid. So the docstring's "34.7 GB" matrix is 914 MB (37.9x over) and
its "0.527 MB" per-bin array is 85.6 kB (6.2x over), which **mis-costs a retention remedy awaiting a
ruling**. Both errors are conservative, so no decision inverts.

The constant's own comment says it was recorded explicitly *because* a per-bin array had been sized off
the wrong grid and was wrong by 230x. **Same defect, second instance, inside the fix for the first** —
and it survived because no test knew the real dimension either.

## Family

- [`BEN-256`](FINDING-20260817-one-field-two-roles.md) — one field, two roles. **This is the same at
  function scope**, and the tell is identical: a correct justification whose scope nobody re-derived.
- [`BEN-452`](FINDING-20260818-a-probe-that-forces-a-guard-false-cannot-test-it.md) — a harness that
  makes a branch unreachable. Here the harness makes the whole collaborator unreachable.
- [`BEN-450`](FINDING-20260818-detection-without-propagation.md) — computed and not reported. Here:
  **read and not compared.**
- `BEN-255` — a check on the wrong population. Here, on the wrong **sub-object**.
