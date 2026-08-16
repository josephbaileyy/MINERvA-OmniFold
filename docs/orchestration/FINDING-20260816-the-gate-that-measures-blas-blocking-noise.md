# A gate whose only measurable quantity is BLAS accumulation order — and a `BLOCK` that quoted a disclaimer as a promise

**Filed 2026-08-16 by the executor (`Assistant`) lane.** Row: `BEN-316`. An independent second read of
defect `N3` in `runs/standard-p4-verifier/20260816T062458Z-repair10-verdict.json`, the defect that
verdict says its `BLOCK` rests on.

**Disposition first, so nothing below is mistaken for a challenge to it: the defect is REAL, it is
CONFIRMED at `HEAD`, and the `BLOCK` is not disturbed by this finding.** What is corrected is the
verdict's *quotation* and its *stated basis* — the first is inverted, the second is too strong — and
neither correction reduces the defect. This is `AGREED-WITH-CORRECTION`, the verdict shape `BEN-352`
recorded as unexpressible by a plain agree/disagree bit.

---

## 1. The defect, confirmed by measurement rather than by reading

`p4_lib.py:1413-1435`, `check_projection_validity`. `project()` at `:1392-1396` is `M @ C_high @ M.T`.
The second leg is:

```python
MH = M @ np.asarray(C_high, dtype=float)
for i in range(C_low.shape[0]):
    direct[i, :] = MH[i, :] @ M.T
```

**`direct[i,:] = MH[i,:] @ M.T` for every `i` IS `MH @ M.T`, by the definition of matrix
multiplication.** The loop is not a second route to the quantity; it is the same product written out one
row at a time. So the only thing `err` can ever measure is the difference between how BLAS accumulates a
row-at-a-time `GEMV` and a whole-matrix `GEMM`.

Measured on a `240→60` block-sum `M` with a random symmetric PSD `C`. **Provenance stated as shas, not as
"`HEAD`", because `HEAD` moved twice during this work** — the verifier lane landed its own verdict at
`758f069` mid-measurement. `git diff --stat` for `nd-unfolding/p4_lib.py` is **empty across
`0e83b54` (the verdict's `code_rev`) → `78467b0` (where the measurement ran) → `758f069`**, so all three
reads are of the same bytes:

| quantity | measured |
|---|---|
| `projection_identity_relerr` | **1.851e-16** |
| gate threshold | `1e-9` |
| **headroom** | **5.40e+06 ×** |
| `project()` vs one-shot `MH @ M.T` | `0.0`, **bit-identical** |
| row-loop `direct` vs one-shot | `8.882e-16`, not bit-identical |

**The gate is set seven orders of magnitude above the largest number it can produce.** And on the
repo's own test fixture (`tests/test_p4_repair.py:136-143`, `C = diag(4,9,16)`, `M` a 2×3 sum-drop) the
error is **exactly `0.0`** — the two forms agree bit-for-bit at that size, so the suite's
`assertLess(relerr, 1e-12)` compares zero against a tolerance.

**So the docstring's justification is false as written.** It says *"Recomputing the same quantity by an
independent route is what makes this a check rather than a restatement"*, and calls the leg *"a direct
block-sum recomputation."* There is no block sum and no independent route. `N3` is right.

## 2. The verdict's quotation is INVERTED, and this is the part a later reader would carry forward

`N3` states that the docstring *"promises its second leg 'compares against an independently-produced
product ... a direct block-sum recomputation'."*

**The docstring's first sentence is the negation of that phrase.** Verbatim, `p4_lib.py:1414-1415`:

> `GATE: the projection itself is valid. Recomputation identities only -- nothing here`
> `compares against an independently-produced product.`

**The function explicitly disclaims comparing against an independently-produced product, and the
verdict quotes the disclaimer as the promise it broke.** The words match because the verdict lifted them
from the sentence that negates them.

This matters beyond tidiness. The overclaim in that docstring is **narrower and different**: not *"I
compare against an independent product"* (it says it does not), but *"my second leg is an independent
**route** to the same quantity."* A repair aimed at the quoted promise would build a product comparison
the function deliberately does not want; a repair aimed at the real overclaim either **writes an
actually independent recomputation** (an explicit `sum_{a,b} M[i,a] C[a,b] M[j,b]` accumulation, which
is what "block sum" describes) **or deletes the sentence and the leg together** and lets symmetry, PSD
and shape/coverage carry the gate honestly. **The two repairs are different work, and the inverted quote
points at the wrong one.**

## 3. "A check that cannot fail" is too strong, and it is the load-bearing clause

`N3`'s `why_it_blocks_stages_4_6` reads: *"A projection run authorized on a check that cannot fail is
authorized on nothing."*

**It can fail.** Mutation-tested at `HEAD`:

| mutation to `project()` | result |
|---|---|
| returns `2.0 * (M C M^T)` — still symmetric, still PSD | **CAUGHT**, `rel 5.000e-01 > 1e-09` |
| corrupted `M` (row 0 scaled ×3), `project()` untouched | **NOT caught**, `relerr 3.033e-17` |

So the leg is a **source-drift regression guard on `project()`**: it detects an edit that changes
`project()`'s value away from the formula the check re-encodes. That is a real, if modest, function, and
it is exactly the class the docstring's *other* sentence claims — *"a bug in it would produce a matrix
that is still symmetric and still PSD"* — which the ×2 mutation confirms is caught.

**What it cannot do is anything about projection validity**, which is what the surrounding comment at
`:1410-1412` asserts is gated. Both legs encode the same formula on the same `M`, so **every error in
the shared premise passes**, demonstrated: a corrupted `M` sails through at `3e-17`.

**The precise statement, which is the one a repair should be scoped against:**

> It is not a check that cannot fail. It is a check that cannot fail **for any reason connected to the
> validity of the projection** — it guards `project()`'s source against drift, and is silent on whether
> `M C M^T` with this `M` is the right thing to compute.

`N3`'s severity survives that narrowing intact, because stages 4–6 need the second thing and the gate
supplies only the first. **But "cannot fail" is checkable and false, and a defect stated in a falsifiable
form that turns out false is the kind a repair lane can dismiss wholesale** — including the two-thirds of
it that is correct.

## 4. The test inherits the same property

`tests/test_p4_repair.py:136-145` is the suite's coverage of this gate. Its docstring is careful and
correct — *"what is gated is the projection's own validity, which is a recomputation identity, not
agreement with a separately-produced product"* — and it carries one assertion that **can** fail
(`assertRaises` on a non-PSD input, which is a genuine check of the symmetry/PSD leg).

Its identity assertion cannot. `assertLess(st["projection_identity_relerr"], 1e-12)` runs against a
measured **`0.0`** on that fixture. **Same family as `BEN-314`** — a suite exercising something adjacent
to the claim rather than the claim — and same family as `BEN-312`: an assertion that *looks* like
verification of the identity leg while being satisfied by construction.

**Not filed as a separate defect**, because it is downstream of `N3`: an identity leg that cannot fail
cannot be given a test that can. Fix `N3` and the test becomes writable.

## 5. What this finding does not do

- **It does not disturb the `BLOCK`.** `N3` stands, six other defects stand, `self_guards_adequate: NO`
  and `authorizes_covariance_stages_4_6: false` are untouched. This lane holds no `P4_VERIFIER_PASS`
  token, was not asked to adjudicate, and does not.
- **It does not repair anything.** `p4_lib.py` is not edited. The two candidate repairs in §2 are
  described so the scope is legible, not proposed for execution.
- **It does not re-litigate the 2026-08-09 gate removal** at `:1399-1412`, which is Joseph's
  re-specification and is a separate question from whether what replaced it does what it says.
- **The defect was already on the record** — `ND_OMNIFOLD_RUN_LOG.md:8805` names *"`check_projection_validity`'s
  non-independent second leg"* from repair-8. **This is the second lane to read it and the first to
  measure it**; nothing here is a new discovery of the defect.

## 6. Reproduce it — the executable form

`docs/orchestration/state/probe-projection-identity-leg-20260816.py`, runnable from any working
directory, no arguments, writes nothing, restores `P.project` in a `finally`:

```
$ python3 docs/orchestration/state/probe-projection-identity-leg-20260816.py
  PASS  row loop equals the one-shot product to float noise only :: max|direct - MH@M.T| = 8.882e-16 ...
  PASS  project() is bit-identical to the one-shot :: max|diff| = 0.0
  PASS  threshold is >=1e6x the measured error :: relerr = 1.851e-16 vs threshold 1e-9 -> headroom 5.40e+06 x
  PASS  relerr is EXACTLY zero there ... asserts 0.0 < 1e-12
  PASS  scale-x2 edit to project() is caught :: rel 5.000e-01 > 1e-09
  PASS  corrupted M passes -- shared-premise errors are invisible :: relerr = 3.033e-17
PROBE RESULT :: ALL REPRODUCED -- BEN-316 stands as filed
```

**It exits non-zero if the leg's behaviour changes**, including if `N3` is repaired — at which point the
probe's §3/§4 expectations become the wrong ones and it should be retired with the defect, not silenced.
Written per `CLAUDE.md`'s standing preference for the executable form of any rule one is tempted to write
down: this table of numbers goes stale invisibly, and the probe does not.

## 7. Cross-reference

- `BEN-314` — a suite that could not fail on the interface it existed to protect. §4 is that shape.
- `BEN-312` — an assertion that names its method and not its target, satisfied by the defect it should
  have caught.
- `BEN-300` — consensus among restatements of one source is not corroboration. **A recomputation that
  re-encodes the formula it is checking is the single-source case of exactly that.**
- `BEN-352` — `AGREED-WITH-CORRECTION`: agreeing a disposition while refuting its basis, which a plain
  agree/disagree bit cannot express. This finding is that verdict shape.
- `BEN-315` — a claim about code inferred from its structure. **§1's numbers exist because this lane
  refused to file §2 from a 400-character truncated dump of the verdict**, which is the failure that
  finding records.
