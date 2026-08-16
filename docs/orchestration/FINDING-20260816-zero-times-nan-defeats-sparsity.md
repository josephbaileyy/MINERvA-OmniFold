# `0.0 * nan` is `nan`, so sparsity is not a containment argument

**`BEN-329`. 2026-08-16, lane A, N4 repair. Episode `EP-2026-08-16-n3-n4-repair`.**

Found because **my expectation was wrong and the code was right.** Writing `N4`'s test, I asserted
that one `nan` in `x_high` would leave 1 of 4 cross-check bins non-finite. Measured: **4 of 4.** The
assertion failed, and the failure was the finding.

## The mechanism

`crosscheck_marginal_vs_independent` starts with `proj = M @ x_high`. A zero entry of `M` does not
isolate a non-finite input, because

```
0.0 * nan  ->  nan
1.0 + nan  ->  nan
```

so **every output row that has any column at all** becomes `nan`. For a coverage-complete `M` — which
`build_projection_M` fails closed to guarantee, since an all-zero row is itself a defect
(`BEN-064`) — that is *every* row.

**Scale on the real products: one bad reported 5D bin of 10,694 takes all 4,825 reported 4D bins with
it.**

If you reason "the matrix is sparse, so only the affected block can be hit", you are wrong by the
size of the matrix. Sparsity localises *contributions*; it does not localise `nan`.

## Why that was worse than a wrong number

Downstream, every summary the function reports is computed over all bins:

| field | value with one `nan` present | how it reads |
|---|---|---|
| `median_abs_rel` | `nan` | broken, visibly |
| `p90_abs_rel`, `p99_abs_rel`, `max_abs_rel` | `nan` | broken, visibly |
| `signed_mean_rel` | `nan` | broken, visibly |
| **`n_over_3pct`** | **`0`** | **"no bins over tolerance"** |

`n_over_3pct` is `int((a > t).sum())`, and `nan > 0.03` is `False`. So the count silently reports the
**most reassuring possible value** for the condition "the input was unusable". A block whose
tolerance counts read zero while its medians read `nan` is not obviously broken to a scraper, and
`integral_ratio` was already documented as possibly `nan`, which makes one more `nan` look expected.

This block was printed and written into the projection receipt in that state. Nothing said whether
the numbers meant anything.

## The repair, and what it deliberately is not

**`REPORT ONLY` is unchanged.** The function still raises on nothing but a shape mismatch — that is
its specification (`:1439`, re-specified 2026-08-09 when the 3% gate was *removed* rather than
widened), and turning it into a gate would require a decision the function is specified not to make.
If that decision is ever wanted it belongs at the caller. Added instead:

* `n_nonfinite_rel`, `n_nonfinite_marginal`, `n_nonfinite_independent` — counts, not a flag;
* `all_finite`, `integral_ratio_defined` — the booleans a reader actually wants;
* `median_abs_rel_finite_only`, `p90_abs_rel_finite_only`, `max_abs_rel_finite_only`, and
  `n_over_*pct_finite_only` — usable summaries beside the poisoned ones;
* a `note` that leads with `NON-FINITE: … THE SUMMARY ABOVE IS POISONED` when any bin is bad.

**And the second-order trap, which is why counts are reported and not just a boolean.** When
*everything* is non-finite, the finite-only summaries are `nan` too and the finite-only counts are
`0` — so the fallback is indistinguishable from a clean result unless the excluded count is printed
beside it. Both regimes are pinned in one test, localised (a `nan` in the independent vector taints
its own bin) and amplified (a `nan` in `x_high` taints all four), so neither can be mistaken for the
other. `BEN-344`'s rule is honoured in the same test: the clean case runs in the same run, so
"the flag fired" is not confounded with "the flag always fires".

## The fact goes where the reader looks

The finiteness fields reach the receipt, but the `[xcheck]` line printed to stdout is what a human —
and every log-scraping check — actually reads, and a `nan`-poisoned median prints as a plausible
number. So `p4_project_4d.py` now prints either

```
[xcheck] all N bins finite -- the summary above is a measurement
```

or a loud `*** NON-FINITE: … THE SUMMARY LINE ABOVE IS POISONED AND IS NOT A MEASUREMENT` carrying
the counts and the finite-only values.

This is `[[BEN-327]]`'s shape exactly — a qualifying fact computed, persisted in JSON, and absent
from the line the verdict is read off — and it is the fifth-plus instance of that family
(`[[BEN-321]]`, `[[BEN-322]]`, `[[BEN-323]]`, `[[BEN-326]]`). The cost of the fix was one `if`.

## The transferable rule

**A non-finite value propagates through a sparse linear map as if the map were dense.** Before
believing that a bad input is confined to part of an output, check whether the arithmetic can carry
it — `0 * nan`, `0 * inf`, and `inf - inf` all defeat structural containment arguments. And when a
comparison's summary can be poisoned, **report the count of excluded elements next to the summary**,
because an aggregate over an empty finite set and an aggregate over a clean full set are reported by
the same fields with different meanings.

Related: `[[BEN-328]]` from the same episode, `[[BEN-323]]` (a failure to observe rendered as an
observation), `[[BEN-064]]` (why an all-zero row of `M` is itself a fail-closed condition).
