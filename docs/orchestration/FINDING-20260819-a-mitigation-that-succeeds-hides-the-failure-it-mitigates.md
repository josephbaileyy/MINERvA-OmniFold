# FINDING 2026-08-19 — a mitigation that succeeds hides the failure it mitigates

**BEN-455.** Lane D (verifier), read-only, authored at lane C's request after a gate-2 pass against
the real archive. **The correctness of the fallback is the active ingredient** — an incorrect fallback
would have failed loudly and been fixed in an hour.

## The shape

> A fallback exists so that a failure of the primary is survivable. If the fallback is **correct**, a
> failure of the primary produces **no observable at all** — not a slow path, not a warning, not a
> wrong answer. The primary can be permanently, unconditionally broken and every run is green.
>
> **The wider the `except`, the more complete the concealment.**

The usual reading of a bare `except` is *"it might hide a bug."* That understates it. It does not hide
a bug in the fallback; it hides the **death of the thing the fallback was written to back up**, and it
hides it forever, because nothing about a correct answer is anomalous.

## The instance

`mii_anchor_comparator._th2_content` reads a TH2D's contents via a buffer fast path, with a row-loop
fallback under `except Exception`. Measured on Perlmutter, ROOT 6.28/12 — the only interpreter this
repo has:

```
h.GetArray()  ->  <class 'cppyy.LowLevelView'>
    attrs: ['format', 'reshape', 'typecode']
    has SetSize:  False
```

`buf.SetSize(...)` is the **first** statement in the try block and raises `AttributeError`. So the fast
path **has never executed and cannot**, the fallback runs on every invocation, and every run returns
the right answer. `SetSize` was the old PyROOT buffer API: the code is not wrong in general, it is
wrong for the interpreter it runs on, which is the only kind of wrong that matters.

**The counterfactual is measured, not argued.** Without the `except`, the first real run dies with
`AttributeError: 'cppyy.LowLevelView' object has no attribute 'SetSize'` — a **five-second**
diagnosis. With it, five days of stub tests, two reviewers and a formal gate ruling all passed over a
dead branch.

### The concealment propagated backwards into the test suite

The sharpest consequence, and it nearly cost a fixture. The author observed that its **local stub also
lacked `SetSize`**, and read that as *the stub being deficient*. The stub was **faithful to the
interpreter**. One more step and a fixture would have been "fixed" to green a route that cannot
execute — a test edited to certify a dead code path, on evidence produced by the concealment itself.

### And the mitigation was protecting nothing

Measured on the real `C_unified` (10694², 114,361,636 elements):

```
fallback rate            2,147,141 elem/s   ->  0.8 min per matrix, ~5 min for all six, once
peak RSS, loop           3,819 MB
peak RSS, diagonal       3,773 MB           ->  the whole benefit is +46 MB
```

`key.ReadObj()` materialises the matrix regardless, so the buffer route saves **numpy** copies, not
**ROOT** memory. The primary that never ran was optimising neither the dominant memory cost nor a
material time cost. C ruled deletion on those numbers.

## The trap inside the repair, which is worse than the bug

The one-line fix is `np.frombuffer(buf, dtype=np.float64, count=(nx+2)*(ny+2))`, and **`count=` is
mandatory**:

```
len(buf)  = 268,435,455      <- 2**28 - 1, a cppyy sentinel
true N    = 114,404,416      <- (10694 + 2)**2
```

A repair that trusts `len(buf)` over-reads **154,031,039 elements = 1.23 GB** past the array and
**succeeds silently**. That is succeeds-but-wrong arriving through the *fix* rather than the bug — the
sharpest form, because the person writing it has just been told to be careful about this exact thing.
`2**28 - 1` is not recognisable as a sentinel unless somebody has written it down.

## The check

1. **For every fallback, ask what proves the PRIMARY ran.** A counter, a log line, or a mode flag that
   disables the fallback in CI. A fallback with no such evidence is indistinguishable from a
   reimplementation of the primary that replaced it.
2. **Narrow the `except` to the exception the fallback exists for.** This one spanned five operations
   and could not tell *"this ROOT build lacks the fast API"* from *"the array is the wrong dtype."*
   Those need opposite responses: the first is a migration, the second is a fail-closed.
3. **When a stub disagrees with your expectation, suspect the expectation.** A fixture that fails to
   support an API may be reporting that the API does not exist.

## Scope of the verification, stated against my own result

I cross-checked the buffer route and the row loop bit-exactly on the real matrix — identical
`sha256 de32843b…`, `array_equal True`, C's `np.shares_memory(out, flat) is False` pin holding. **But I
exercised the REPAIRED route; the code in the tree cannot reach the line I checked.** So that pass does
not discharge the gate either, and gate 2 stays UNMET until the change lands. A label is not a
discharge, and neither is a review of an artifact that differs from the tree by the defect.

## Family

C's observation, and it is the reason this is a family and not an incident — **three instances in one
day of *a mitigation that succeeds hides the failure it mitigates***:

- `BEN-023` — a resume guard validating **existence** rather than completeness: it succeeded, and
  7 partial slabs permanently blocked their own repair.
- [`BEN-454`](FINDING-20260819-an-injected-reader-is-untestable-for-what-it-discards.md) — the
  diagonal reduction defended as a memory saving **that saved nothing**, while costing the comparison
  99.99% of its coverage.
- **`BEN-455`** — a correct fallback concealing a primary that never ran.

Distinct from `BEN-454`: that is a reader untestable for what it **discards**; this is a mitigation
that conceals what it **mitigates**. And distinct from `BEN-450`: there a guard computed the right
thing and reported it nowhere; here nothing is computed at all and the report is correct.
