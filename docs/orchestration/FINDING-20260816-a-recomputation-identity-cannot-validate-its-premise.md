# A recomputation identity cannot validate its own premise

**`BEN-328`. 2026-08-16, lane A, N3 repair. Episode `EP-2026-08-16-n3-n4-repair`.**

The `N3` brief prescribed a fix, invited argument rather than compliance, and the argument turned out
to be load-bearing: **the prescribed fix could not have met the bar `N3` was written against.** Not
because it was badly specified — it correctly identifies and repairs a real dishonesty — but because
a block sum that reads its groups and weights off `M` reproduces `M C Mᵀ` for any `M` the lane builds.

> **CORRECTED 2026-08-16, before reading further.** This finding originally generalised that to *"no
> function of `(C_high, M)` can decide whether `M` is wrong."* **That is false**, and an independent
> second read refuted it by construction: `M`-only structural invariants catch 3 of the 4 corruptions
> below. Only the **relabeling** class provably needs the recipe. The remedy is unaffected — see
> [the correction section](#correction-2026-08-16-the-impossibility-claim-was-too-strong), which also
> shows the refuting invariant has no bite on the production mask.

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
relation between `M` and the recipe that produced it.** ~~So no function of `(C_high, M)` can decide
it.~~ **That last sentence is FALSE AS STATED and is corrected in the section below — it is retained,
struck, because it is what this finding originally asserted and what a later reader may have acted
on.** Both legs sharing `M` is not an implementation weakness to engineer around — it is the premise,
and a premise is not checkable from inside the computation that assumes it, **for the class where
that holds**, which the correction below delimits.

## CORRECTION, 2026-08-16: the impossibility claim was too strong

The independent second read on `N3`/`N4` **held the remedy and refuted the argument for it**, by
construction, which is the right way to attack a claim like this. Reproduced here before accepting
it — a reviewer's measurement is evidence, not a verdict, and this one turned out to be right.

**A function of `M` ALONE catches 3 of the 4 corruptions I chose.** The invariant:

* **(a)** exactly one nonzero per column;
* **(b)** all nonzeros positive;
* **(c)** every row carries the **same multiset** of nonzero values.

Clause (c) follows from my own construction, which is what makes the refutation sting:
`M[row,col] = wdrop[k]` depends on the **dropped index** and never on the row, so under full
drop-axis coverage every row carries the whole width multiset.

| corruption | identity leg | `M`-only invariant | recipe gate |
|---|---|---|---|
| row scaled by 3 | pass `1.4e-16` | **CATCHES** | **CATCHES** |
| one weight scaled by 3 | pass `9.5e-17` | **CATCHES** | **CATCHES** |
| one column to the wrong row | pass `9.5e-17` | **CATCHES** | **CATCHES** |
| two rows swapped | pass `9.5e-17` | misses | **CATCHES** |

**The row swap provably requires the recipe.** It is a pure relabeling — verified directly: the
swapped matrix is the same multiset of rows as the original, so every structural invariant survives
it. **So at least one corruption class genuinely cannot be caught from `(C_high, M)`, and the recipe
gate is necessary regardless. The remedy stands unchanged; only the argument narrows.**

### Why the overreach mattered

**As filed, this finding licensed a future lane to skip a cheap structural check on the grounds that
checking is impossible — when 3 of the 4 corruptions I myself chose are catchable without a recipe.**
That is the same shape as the docstring this repair fixed: a claim strong enough that a later reader
stops looking. Being wrong in the safe direction is not a defence, because the harm is not a bad gate
but an unbuilt one.

### The operational sharpening

The second read flagged clause (c) as **coverage-conditional** and explicitly declined to test the
production masks. Measured here, extending it:

* **the invariant's entire discriminating power is clause (c).** (a)+(b) alone catch **none** of the
  four corruptions;
* clause (c) dissolves as coverage falls — distinct row multisets: **1** at full coverage, **4** at
  10% of high bins dropped, **6** at 30%, **7** at 50%;
* **on the production configuration it cannot hold at all.** 10,694 reported 5D bins over 4,825
  reported 4D bins is a **mean W multiplicity of 2.216 of 6**, so almost no row is coverage-complete.

**Not measured on the real masks** — they require ROOT products that are not readable from this
checkout — so that last point is an *implication of committed counts*, and is stated as such rather
than as a measurement.

**The correct reading, then: the impossibility claim is false in general; the relabeling class is the
part that survives; and on this configuration the recipe gate is doing all of the work anyway.**

### A THIRD overreach of the same shape, 2026-08-16, and this one is about the author

While adjudicating the real-product `C4 = M C5 Mᵀ` identity I wrote that `AXIS_EDGES` *"sits outside
every gate on this path, before and after my repair."* **False, and checked rather than defended.**
Edge **drift** is gated in two independent places: `p4_project_4d.py:73-78` computes
`edges_bin_volume_hash(edges)` and requires both `edge_hash` and `bin_volume_hash` against the
manifest — mandatory, with `test_p4_repair.py:1188-1189` pinning that they are no longer optional —
and `project_cov_nd.py:62` carries an `np.allclose` drift check against `AXIS_EDGES` in the mirror.

**What survives is much narrower:** the identity cannot detect an edge array that is **wrong but
consistent**. `edge_hash`/`bin_volume_hash` bind *"the edges now"* to *"the edges when the manifest
was made"*; nothing on this path compares `AXIS_EDGES` to an authority outside the repo. Because the
same array feeds both the stored `C4` and any recomputation, the identity is blind to that class —
genuinely this finding's shape, but a far smaller claim. **Deliberately not filed as an `OI`:** "no
external authority for a frozen binning" is true of essentially every frozen binning in this
campaign, so it is a general property, not a defect in this path, and an `OI` would imply an
actionable owner that does not exist.

**The pattern is worth more than the three instances.** Same night: *"no function of `(C_high, M)` can
decide it"* (refuted by construction, above), *"no consumers exist"* (from a `| head`-truncated grep
that dropped both real hits), and now *"outside every gate."* Each is an **asserted absence** made
without the covering search that would bound it, and **each errs in the direction that makes the
author's own finding look larger.** `BEN-344` says a null must be shown capable of being non-null by
the same instrument in the same run; these are the author-side companion — **a claim that nothing
exists is a claim about the search, and the search was never described.** The habit that fixes it is
cheap: before writing "no X", run the grep that would find X and quote it.

### FOURTH instance, and it cost a consensus ruling: I confirmed a run that already existed

Lane B withdrew the real-product `C4 = M C5 Mᵀ` run at `4100331`, before execution, on grounds that
**the check already existed, had already been run, and could not have come out differently**: the
2026-08-10 `cross-object-script.py` records `identity_verdict = ESTABLISHED`, an independently
reconstructed `M` whose content hash matches the pipeline's, `max rel 3.7568690548899724e-16`, a 19/19
block census and rank `263 = 263 = 263`. **I confirmed that run.** So did B. Two lanes ratified it and
it went to Joseph.

**My share of the failure is specific and it is not "I trusted B".** I adjudicated the question I was
handed — *is this a different measurement, is it falsifiable, what does it share* — and answered all
three correctly. **I never asked whether the check already existed.** That is the omission, and it is
unforgivable in this particular session, because **I had filed the remedy for it hours earlier**: the
`BEN-300` addendum from the `OI-6` duplicate dispatch says that a task's *holder* has no
machine-derivable source but **whether the work is already done usually does**, and one
`git log -S` / `git grep` over the target answers it before dispatch. I wrote *"duplicate dispatch has
a cheap pre-check that duplicate assignment doesn't"* — and then adjudicated a request for compute
without running it. **A falsified_by sentence does not catch redundancy.** I even wrote *"different ≠
informative"* in the ruling and then failed to test informativeness.

**AND A SECOND, SHARPER ERROR OF MINE THAT B'S MEASUREMENT EXPOSED — the one worth the most.** My
prerequisite argued that if `C4` predated the C5 rebuild the identity *"MUST fail"*, resting on the
whole-file digest having moved (`602bbcf2… → 950f8cb1…`). B measured the objects: **the covariance
CONTENT is bit-identical across that change** — only ~24 KB of metadata/band-level bytes moved — so
the inference was invalid and its conclusion false. **A whole-file digest is not a digest of the object
you are asking about**, and `std_final5_candidate.root` holds many objects.

The self-indictment is that **`OI-129` is my own row recording that this pipeline never digests the
covariance object itself** — and in the same message I reasoned as though the file digest filled that
gap. I identified the missing content digest and then used the available file digest in its place. This
is [[my-recurring-failure-is-asymmetric-comparison]] in its purest form: two quantities that differ in
what they cover, compared as if they covered the same thing.

**What survives from the episode, and it is B's, not mine:** the 2026-08-10 audit's own
`gaps_remaining[0]` is still open, because `row_index_sha256` hashes the in-memory array that was used
to write `hRowIndex4D` rather than reading the histogram back — a circular digest that hashes the
intent instead of the artifact. `OI-129`'s fix is sharpened to say read-back explicitly. Seconds to
check, genuinely falsifiable, and the one thing in this whole thread that was worth doing.

### Where the overreach propagated, enumerated (`BEN-302`)

A retraction reaches only as far as the corrector's map of the corpus, so the sites are named rather
than counted. Covering search over `*.py`, `*.md`, `*.json`:

| site | status |
|---|---|
| `FINDINGS.md` `BEN-328` row | **corrected** (struck beside, not overwritten) |
| this file, intro + general statement | **corrected** |
| `ND_OMNIFOLD_RUN_LOG.md:9546` | **corrected by appended entry** — the log is append-only |
| `p4_lib.py:1417`, `:1485` | **NOT corrected, queued** — see below |
| `runs/standard-p4-verifier/20260816T220615Z-repair11-verdict.json:19` | **NOT correctable by this lane** — a receipt, cited not amended |
| `state/RECEIPT-n3-n4-second-read-20260816.json`, `state/probe-projection-M-only-invariant-20260816.py` | **no action** — these quote the claim as the thing under test, which is correct usage |

**The load-bearing copy is the one this lane cannot fix.** The repair-11 verdict — `48ac04d`,
`code_rev a8f7b2f`, `verdict PASS`, `authorizes_covariance_stages_4_6: True` — asserts at `:19` that
*"No function of `(C_high, M)` can decide whether `M` is the right matrix"*, as part of recording `B1`
as `UNSATISFIABLE-AS-WRITTEN`. That is the same unforced generalisation, in the document that
authorizes covariance stages 4–6, and it is the verifier's to correct. **Its `B1` finding is
unaffected:** `B1` aimed its demand at the identity route, which genuinely cannot meet it, and the
verifier's own fixture (`nb=[2,3,2,2,3]`, `drop_axis=2`, unequal dropped-axis widths, all corruptions
at `2.842e-14`) establishes that much. What it did not test is an `M`-only invariant, which is
exactly the step this correction supplies.

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

**QUEUED, NOT DONE — the same overreach is in the code, in two docstrings, and was deliberately left
there.** `p4_lib.py:1417` (*"`M` cannot be validated from `(C_high, M)` alone, because 'wrong' is only
defined against the recipe that produced it"*) and `:1485` (*"'Wrong `M`' is only definable against the
recipe"*) assert what the correction above narrows. **They are not edited because `p4_lib.py` is one of
the 20 standard-P4 execution-surface paths and lane C's repair-11 pass is in flight — rule 4b
invalidates that verdict on any in-scope edit, and a prose correction is not worth a re-verification.**
Both are wrong in the same direction as the row was: they license skipping a structural check. Two
nearby claims are correctly scoped and stay true as written — `:1530` (*"no identity of the form
'recompute `M C Mᵀ`' can see that `M` is wrong"*) and `:1550` (*"it CANNOT catch a wrong `M`, and no
recomputation identity can"*) — because both are about **recomputation identities**, not about all
functions of `(C_high, M)`. So the fix is two sentences at `:1417` and `:1485` only, after repair-11
lands.

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
