# Redundancy that arises by construction is a free internal check — and a cross-check must share exactly what it is not testing

**Filed 2026-08-16 by the executor (`Assistant`) lane.** Row: `BEN-318`. Filed as its own row at the
mediator's direction rather than as a clause inside `BEN-360`, for the reason `BEN-361` had to be separated
from `BEN-360`: **a clause inside another finding reads as an illustration of that finding, not as a rule in
its own right.**

**Two rules, and the second is the one that took work.** The first is a habit. The second resolves what
looks like a direct contradiction between this finding and `BEN-316`, filed by the same lane the same day.

---

## 1. Redundancy that arises by construction is a free internal check

`67c94df` added a `RunStep2` hook to the fold-forward recorder to capture the end-of-run push. It produces
`niter` rows where `niter-1` of them **duplicate rows the existing `RunStep1` hook already records** — the
push `RunStep2(i)` leaves *is* the push `RunStep1(i+1)` consumes.

**The duplication was not designed. It fell out of hooking two adjacent points in one loop**, and there
were two things to do with it:

| | |
|---|---|
| **trim it** — emit only the one new row (`is_end_of_run_push`), since the other `niter-1` are already in the report | smaller output, no new information lost, *and no check* |
| **enforce it** — gate the overlapping rows to EXACT equality, `!=` on floats with no tolerance | the instrumentation now **fails if either hook reads at the wrong moment** |

**Trimming is the tempting move and it is the wrong one.** It looks like housekeeping — a reviewer
optimising for concision would ask for it, and the argument *"those rows are already in the report"* is
true. What it discards is the only thing in the run that can catch the failure `BEN-360` documents: a
recorder capturing the neighbouring quantity. **Before this, "the recorder might read at the wrong moment"
was a paragraph in a finding. After it, the run refuses.** That is `CLAUDE.md`'s own trade — a document
costs tokens in every future session, a check costs zero and cannot be skipped — arrived at from the other
direction.

**The gate was free.** No extra computation, no extra run, no reviewer time: the two numbers were already
being produced and the only decision was whether anything compared them.

> **RULE: when two parts of a system compute the same quantity by construction, do not deduplicate —
> compare. Redundancy that arises by construction is a free internal check, and trimming it is the
> tempting mistake.**

Gated twice here, in the wrapper and again independently in the launcher's `G3`, which does not take the
wrapper's word for it.

## 2. THE HARDER RULE: share exactly what you are not testing, differ in exactly what you are

**This finding appears to contradict `BEN-316`, filed hours earlier by the same lane, and a later reader
will notice.** So it is resolved here rather than left to them.

`BEN-316` condemns `p4_lib.check_projection_validity` for checking `M C M^T` against a second computation
that **re-encodes the same formula**, and says so in the strongest terms: *"a recomputation that re-encodes
the formula it is checking is `BEN-300`'s single-source case."*

**And then this finding's own gate deliberately makes both sides share one implementation** — `_ff_reduce`
was *extracted* to a single function precisely so the two hooks cannot compute the fold-forward
differently. Two copies would have been more independent. **The lane argued for independence in the
morning and against it in the evening.**

**Both are right, and the resolution is what the check is FOR.**

| check | what it claims | therefore must SHARE | therefore must DIFFER in |
|---|---|---|---|
| `check_projection_validity`'s identity leg | *the formula `M C M^T` is correctly implemented* | the inputs `C`, `M` | **the route to the answer** — an independent recomputation |
| the fold-forward overlap gate | *two hooks read the same array at the same logical moment* | **the reduction**, exactly | the moment of reading |

`BEN-316`'s gate fails because it shares the route, which is the thing it claims to test. **This gate would
fail in the mirror-image way if the reduction were duplicated:** any difference between two
implementations would surface as a value difference, and a value difference is **indistinguishable from a
timing error**. The check would fire on a formatting change and stay silent on nothing — it would report
"the hooks disagree" when what disagreed was the arithmetic. **A confounded check is not a weaker check;
it is a check of a different proposition.**

> **RULE: a cross-check must share exactly what it is not testing and differ in exactly what it is. Ask
> what the check CLAIMS before deciding whether to reuse the implementation — "more independent" is not
> automatically stronger, and "shared" is not automatically a restatement.**

**This is the part the lane nearly got wrong.** `_ff_reduce` was extracted for tidiness first; only
afterwards did it become clear that with two copies the gate would have been comparing implementations
rather than moments, **while looking identical in the report and in the test names.** The right decision was
reached for the wrong reason, which is worth recording because the wrong reason does not generalise.

## 3. Where each rule applies, so neither is over-applied

- **`§1` applies whenever a quantity is computed twice as a by-product.** It does not license *manufacturing*
  redundancy: a second computation written on purpose is `§2`'s problem, and whether it is a check or a
  restatement depends entirely on what differs.
- **`§2` applies to every gate.** The question *"what does this check claim, and does the pair share the
  thing it claims?"* is the one `BEN-316` answers badly and this one answers deliberately. It is also the
  cheapest way to spot the `BEN-316` family in future: **a check whose two sides differ in nothing that
  matters cannot fail, and a check whose two sides differ in too much cannot localise.**

## 4. Cross-reference

- `BEN-360` — the recorder captured the neighbouring quantity. `§1` is that finding's executable form; it
  is filed separately because a rule inside another finding is read as its illustration.
- `BEN-361` — a predeclared pessimism is the least-checked claim; the precedent for separating a rule from
  the finding that occasioned it.
- `BEN-316` — the gate whose only measurable quantity is BLAS accumulation order. **`§2` exists because
  this finding and that one give opposite advice on reusing an implementation, and both are correct.**
- `BEN-300` — consensus among restatements of one source is not corroboration. `§2` is the rule that says
  when a shared implementation *is* a restatement and when it is a control.
- `BEN-314` — power-test the guard. `§1`'s gate is power-tested by
  `test_the_overlap_gate_REFUSES_a_disagreement`, which exercises the comparison on a deliberately
  mismatched pair rather than only on a passing one.
