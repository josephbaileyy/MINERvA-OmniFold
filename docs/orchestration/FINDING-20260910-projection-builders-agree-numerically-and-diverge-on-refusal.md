# FINDING 2026-09-10 — the two projection builders agree on the weights and disagree on refusal

**CITABLE FOR:** that `p4_lib.build_projection_M` and `project_cov_nd.build_projection` produce
BYTE-IDENTICAL `M` on canonical edges, for the single-axis `W` marginalisation, under masks whose
low support covers the high support's image; and that they take OPPOSITE actions when it does not.

**NOT CITABLE FOR:** equivalence over *"every projection the publication quotes"* — that is
`SPEC-20260906` §6's requirement and this does **not** meet it (see LIMITS). Not citable for any
implementation being the adopted `M`. Nothing here designates, adopts, or grades anything.

Measured 2026-09-10 against `origin/main` at `5580d1d5`, macOS arm64, numpy 1.26.4, no compute,
no cluster. Probes committed beside this file so the measurement can be re-run rather than believed.

## What §6 asked for

> Both builders instantiated on the same edges, masks and drop axis, and `M₁ − M₂` compared
> elementwise to zero at float64 tolerance, for **every** projection the publication quotes — not
> one exemplar, since they may agree on the 4D case and differ where support masks bite.

## Result 1 — the weights are identical

Canonical grid `[14, 16, 7, 7, 6]` = 65,856 high bins, 10,976 low; drop axis 4 (`W`).

| mask density | reported high / low | `M` shape | max abs diff | exact equal |
|---|---|---|---|---|
| 0.02 | 1304 / 1230 | (1230, 1304) | `0.000e+00` | yes |
| 0.05 | 3282 / 2911 | (2911, 3282) | `0.000e+00` | yes |
| 0.10 | 6545 / 5105 | (5105, 6545) | `0.000e+00` | yes |

sha256 over the float64 buffers matches in all three cases.

**The comparison can detect a difference**, which is the control without which the table above is
worthless. Perturbing ONE `W` edge by `1e-9` — inside `project_cov_nd.AXIS_EDGES`, restored
afterwards and verified restored — surfaces as `max|M₁ − M₂| = 1.000e-09`. So the zeros are a
measurement and not a broken harness reporting nothing.

## Result 2 — they take OPPOSITE actions where the support masks bite

This is the case §6 named, and it is the reason the elementwise test alone would not have found it.

Un-report five low bins that DO receive source cells, leaving the high mask unchanged:

```
builder 1  p4_lib.build_projection_M       RAISED P4GateError
                                           "high reported bin 6 maps to non-reported low bin 1"
builder 2  project_cov_nd.build_projection returned M (1225, 1304)
                                           and silently dropped 5 source cells
```

Same weights; opposite semantics. `p4_lib` refuses to build a map that would discard reported
source content (`p4_lib.py:1353`, the `require(row is not None, ...)` on the low lookup).
`project_cov_nd` builds one and returns the count as a second return value the caller is free to
ignore (`project_cov_nd.py:79`, the `keep = dst_row >= 0` filter and the `dropped` return).

**§6's stated check cannot see this.** `M₁ − M₂` is undefined when one builder raises, so an
equivalence harness that only differences the matrices reports nothing on the exact input class §6
was worried about. The check as written needs a second arm: agreement of REFUSAL, not only of value.

**§6's *"if they differ, no implementation takes automatic precedence"* does not bite in the form it
anticipated.** The two do not disagree about a number. They disagree about whether a configuration
is admissible. That is a designation question of a different kind and it is not resolved here.

## Does this reach the Z code path today? No — and one pointer says it would if wired

Measured at `5580d1d5`: no `z_*` module calls either builder. `z_contract.py:58` imports `p4_lib`
for constants (`BANDS`, the repro tolerances) and for the `P4GateError` idiom; `z_statistics.py`
NAMES `project_cov_nd.py` in prose at `:25` and `:202` but does not import it.

So the divergence is latent. The pointer that matters: `s_proj`'s own docstring
(`z_statistics.py:202`) names **`project_cov_nd.py`'s width-weighted `M`** as its map. If `s_proj`
is ever wired to a real projection, the builder it reaches is the PERMISSIVE one — the one that
drops unreported destinations and reports the count in a return value.

## LIMITS — what this does not establish

1. **One drop axis.** Only `W` (`axis 4`), the 5D→4D marginalisation. The publication also quotes
   3D, `(E_avail,W)` and declared FPS marginals; multi-axis drops are untested here.
2. **Synthetic masks, not G's.** The reported masks are pseudorandom at three densities, not the
   real support read from G. Real masks may exercise the biting case in production, or may not.
3. **The third builder is untouched.** `eavail_generator_significance.py:85-88` builds `M` inline,
   grouping `dpt·dpz·dq3` by `E_avail` bin. It needs a different harness and has not been compared
   to either of the other two.
4. **Float64 exactness here is not a promise elsewhere.** Both compute a product of bin widths;
   agreement follows from doing the same arithmetic in the same order, and a different axis
   ordering or a different drop set could reorder the product.

So §6's premise is **partially discharged in the numeric direction** and **newly complicated in the
semantic one**. It remains, as §6 puts it, `"the adopted M, implementation unidentified and
undesignated"` — this narrows which part of that is still open, and does not close it.

## Re-running

```
python3 docs/orchestration/measure_m_builder_equivalence.py
python3 docs/orchestration/measure_m_builder_equivalence_controls.py
```

Both are read-only, take seconds, require numpy only, and touch no cluster and no data root. The
controls script mutates `project_cov_nd.AXIS_EDGES` in memory and restores it in a `finally`,
asserting the restoration.
