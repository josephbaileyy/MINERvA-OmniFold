# A recomputation identity cannot validate its own premise

**`BEN-328`. 2026-08-16, lane A, N3 repair. Episode `EP-2026-08-16-n3-n4-repair`.**

The `N3` brief prescribed a fix, invited argument rather than compliance, and the argument turned out
to be load-bearing: **the prescribed fix could not have met the bar `N3` was written against.** Not
because it was badly specified — it correctly identifies and repairs a real dishonesty — but because
the bar asks for something no function of that signature can deliver.

## What was wrong

`p4_lib.check_projection_validity`'s second leg claimed an independent recomputation:

```python
C_low = project(C_high, M)          # M @ C_high @ M.T
direct = np.zeros_like(C_low)
MH = M @ np.asarray(C_high, dtype=float)
for i in range(C_low.shape[0]):
    direct[i, :] = MH[i, :] @ M.T   # the SAME product, re-associated
```

`direct` is `M C_high M^T` with a different loop order. Its `relerr` therefore measured
floating-point accumulation order: **~1.9e-16 against a 1e-9 threshold — 5.4e6× headroom — and
exactly `0.0` on the repo test's own fixture**, where `assertLess(relerr, 1e-12)` could not fail.

The docstring supported two incompatible readings, which is why the text could not be trusted:
`:1414-1415` disclaimed any independent comparison, `:1420-1422` promised that "an independent route
is what makes this a check rather than a restatement", and `repair-10` quoted the promise as the
contract. A third line, `:1410-1411`, advertised "a direct block-sum recomputation" the code did not
perform.

## Why the prescribed repair could not reach the bar

`B1`, predeclared at `bf97279` before any repair existed:

> `N3` closed **by measurement** — not "the code changed", but a test that fails on the pre-fix form
> **and on a wrong `M`**, which the current form cannot detect.

The prescription was to accumulate the block sum from `M`'s structure with no matrix multiplication.
Measured first, on the working tree, before writing any repair:

| route / corruption | relerr | verdict |
|---|---|---|
| block sum vs `project()`, correct `M` | `4.99e-16` | agrees, so it is a valid route |
| block sum vs a **doubled** `project()` | `5.00e-01` | **catches a `project()` expression bug** |
| row of `M` scaled by 3 (the probe's corruption) | `1.50e-16` | **invisible** |
| one weight of `M` scaled by 3 | `4.17e-16` | **invisible** |
| one column moved to the wrong row | `4.99e-16` | **invisible** |
| two rows of `M` swapped | `4.99e-16` | **invisible** |
| same, on the real width-weighted `M` | `3.29e-17` | **invisible** |

A block sum that reads its groups **and its weights** off `M` computes `M C M^T` by definition, for
any `M` with one nonzero per column — which is every `M` this lane builds. It is a genuinely
independent route with respect to `project()`'s *expression* and a tautology with respect to `M`.

**The general statement, which is the transferable part: "wrong" is not a property of `M`. It is a
relation between `M` and the recipe that produced it.** So no function of `(C_high, M)` can decide
it. Both legs sharing `M` is not an implementation weakness to engineer around — it is the premise,
and a premise is not checkable from inside the computation that assumes it.

## The repair: two gates, not a better version of one

**`_block_sum_projection`** — `C_low[a,b] = Σ_i Σ_j M[a,i] M[b,j] C_high[i,j]` by weighted block
sums, numpy reductions only, no matrix multiplication anywhere in the path. This makes the
"direct block-sum recomputation" claim true for the first time since 2026-08-09, and it catches an
error in `project()`'s expression. **Measured at the real stage-6 shape (10,694 reported 5D → 4,825
reported 4D): 1.00 s, against 6.62 s for the BLAS `M C_high M^T`**, because `M` holds one nonzero per
column. The honest route is also the cheaper one; nothing was traded for it.

**`check_projection_matrix_matches_recipe`** — rebuilds `M` from `(edges, drop_axis, mask_high,
mask_low)` and requires **exact** equality. The reconstruction (`projection_M_from_recipe`) uses
`unravel_index` / `ravel_multi_index` / `searchsorted`, deliberately **not** `build_projection_M`'s
per-column loop over `//` and `%` with a dict lookup — if it called that, the comparison would be a
tautology of a different kind, and a construction bug would be invisible rather than a copy error.
Catches the probe's corruption at **`max|diff| 3.0`**, where every recomputation-identity route
reports `~1e-16`.

Exactness is available and is used deliberately: both routes read the same width array
(`edges[drop_axis][1:] - edges[drop_axis][:-1]`) and **store** its entries verbatim without
combining them arithmetically, so they agree bit for bit. Any tolerance on that comparison would be
a number nobody can justify.

`M` carries **width weights, not 0/1 membership** — `M[row,col] = wdrop[k]` — so the test fixture
uses unequal `W` widths (`0.5, 1.0, 1.5`), making a weight error distinguishable from a mapping
error. A 0/1 fixture would have been degenerate on the axis under test (`BEN-342`'s shape).

The gate is called from `p4_project_4d.py` **at construction**, where the ingredients are in hand. A
library gate nobody invokes is precisely the defect class this repair is about.

## The docstring is resolved by scoping, not deleting

The promise is **kept and scoped**, because deleting it would lose a true claim and keeping it
unqualified would restate the falsehood:

* the gate re-derives **the product** independently, so it can catch an error in `project()`;
* it **cannot** catch a wrong `M`, and no recomputation identity can.

That limit is now **asserted in a test** and **reported in the receipt**
(`projection_identity_gates_M: False`) rather than living in prose, so a reader cannot infer from a
green identity that the map was checked. A test also pins the blindness in place: if someone later
makes the identity gate `M`-sensitive, it fails and the docstring gets revisited.

## Before/after is one command, not a narrative

Lane D built the probe at `3fe11de` with a `P4LIB_DIR` override *before* the repair could overwrite
its own baseline — `BEN-317`'s rule applied to its author's own numbers, and it paid off exactly as
intended. Extended here with a section 5 and run twice:

* **pre-repair** `p4_lib.py`, `sha256 aa3470e45040398a00064f83fef853cffc3172e27fce2ff0d19ac1258bd7de65`
  — matching the baseline recorded in the probe itself — exits **2**:
  `PRE-REPAIR TREE -- the defect is live and M is ungated`, reproducing the **`3.033e-17`**
  corrupted-`M` pass;
* **repaired** tree exits **0**.

`BEN-316`'s sections 1–4 are **expected** to keep passing after the repair, and do. Section 4 is "a
corrupted `M` passes the identity leg" — still true, by construction, and that is the point. So the
probe now keeps its two expectation sets in **separate buckets** with distinct exit codes: one code
meaning both "`BEN-316` no longer reproduces" and "the repair has not landed yet" would license
opposite conclusions from the same number.

## What was verified, and how

Six new tests. Full suite **1461 passed / 2 failed / 1 skipped**, against `HEAD`'s **1455 / 2 / 1**
run at the **same selection** — the whole suite both times, not one file against a subset, which is
this lane's own recurring error. Both failures are identical and pre-existing: an absent `/pscratch`
path, and the known order-dependent pollution in `test_pet_fullevent_nominal_launcher` (it passes
when its file is selected alone). `TMPDIR` set explicitly.

The 14 new recorded fields tripped `test_p4_sweep_snapshots` — the drift watcher doing its job.
Regenerated via the documented `--update` (`115 → 129` fields, `28 → 29` gates), which then tripped
the test binding the inventory *document* to the snapshot, so
`REPAIR6-RECORDED-NOT-CHECKED-INVENTORY.md` is updated and **names** the new fields. Recorded there:
the sweep is grep-level and cannot see `n_over_3pct_finite_only` and its two siblings, written
through an f-string key — a pre-existing limit of the extractor, named because a field the inventory
cannot see is what the inventory exists for.

`p4_project_4d.py` insertions move the repair-8 verdict's line anchors. **Derived rather than
computed**, because arithmetic on three insertion points gets it wrong: `:130`/`:132`/`:133`
unchanged, `:182 → :204`, `:193 → :218`, `:197 → :222`. The verdict JSONs are receipts and were
**not** edited.

## Not done

No run, no `sbatch`, no covariance construction. The repair-10 `BLOCK` stands and this repair does
not lift it; `authorizes_covariance_stages_4_6` remains `False` and only the verifier can change
that. `P4_VERIFIER_PASS` untouched. The outstanding-defect total is the verifier's to restate — lane
B refuted `#7` by measurement — and this lane asserts none.

**One exposure is left open deliberately.** `check_projection_validity` still has a signature that
cannot see the recipe, so a *future* caller can gate the product without gating the map. Wiring the
one production caller plus a source-level non-regression test is what is achievable without breaking
the pipeline or the probe; making the recipe mandatory in that function would break both. The
docstring says so explicitly: "a caller that calls only this one has gated the product and not the
map."

Related: `[[BEN-316]]`, `[[BEN-344]]` (a null must be shown capable of being non-null by the same
instrument in the same run — honoured inside the corrupted-`M` test, which shows the same gate
passing the good `M` in the same run), `[[BEN-077]]` (ship the ingredients), `[[BEN-329]]` from the
same episode.
