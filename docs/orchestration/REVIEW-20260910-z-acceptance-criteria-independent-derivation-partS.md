# PART S — the projection manifest: yardstick pre-registered BEFORE the manifest exists

**Owner:** independent-assessment lane. **Code base:** `6f24fb00`.
**Subject: NOT YET IN HAND.** The manifest is incomplete and held pending five completions Joseph
required. Designer at `cc2a71aa`, packet sha256
`41704ebeae762790cb967605a69c79d2598ffa7f21101b5eac3f49b2e211c309`, 1524 lines — **digested, NOT
read.** This part is written first so the verdict cannot be fitted to the answer, the same discipline
as Part A (`1508ead0`) and Part F (`c695f209`).

**Return format when it lands:** `READY FOR JOSEPH'S DECISION` or `BLOCK`, consequential issues only.
**Out of scope by Joseph's ruling:** the rejected yardsticks and the universal-bound approach — (A)'s
withdrawal is accepted and that investigation is closed. **Not mine:** the 1% accuracy criterion,
routed to the mathematical reviewer in parallel.

---

## S.1 — THE BLOCKER VERIFIES, AND ITS SHARPER FORM IS THAT NO EXISTING BUILDER HAS BOTH PROPERTIES

Verified at `6f24fb00`, `p4_lib.build_projection_M`:

- `:1354` — *"Deterministic 5D->4D map by WIDTH-WEIGHTED marginalization of **one** axis."*
- `:1361` — `require(len(nb) == 5, "expected 5 axes")`
- `:1365` — `nb_low = [n for i, n in enumerate(nb) if i != drop_axis]`, one axis removed
- `:1369` — `strides_l` over `range(4)`; the output arity is fixed at four
- `:1376` — `k = midx[drop_axis]`, a single scalar dropped index

And the four proposed maps, against the 5D order `(pt, pz, eavail, q3, W)`:

| map | keeps | drops |
|---|---|---|
| **P1** `(E_avail, W)` | `eavail, W` | **3** — `pt, pz, q3` |
| **P2** `E_avail` | `eavail` | **4** — `pt, pz, q3, W` |
| **P3** `p_T` | `pt` | **4** — `pz, eavail, q3, W` |
| **P4** `p_∥` | `pz` | **4** — `pt, eavail, q3, W` |

**None is a single-axis drop**, and `require(len(nb) == 5)` forbids calling the function on its own 4D
output, so iteration is closed off as written. The coordinator's blocker holds.

**The sharper form, which follows from both builders and not one.** The builder that *can* express
these maps is `project_cov_nd.build_projection` (`:79-84`): it takes `src_axes, keep_axes` and derives
`drop_axes` itself, i.e. **arbitrary keep-axis subsets** — exactly P1–P4's shape. But its own docstring
(`:81-82`) says `dst_index_of` maps a destination flat index *"to the destination reported row (**or
-1 to drop**)"* — **silent dropping by design**, and `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`
(in `main`) records that it performs neither of `p4_lib`'s orphan checks. `p4_lib` by contrast refuses
in **both** directions, at `:1380` and `:1395`, with `:1382-1393` recording `BEN-064` as a **masking
defect** that hid 5 orphan bins on real products.

**So the two properties the manifest needs — arbitrary keep-axis arity, and both-direction orphan
refusal — are currently in different functions, and no existing builder has both.** That is a
different problem from "the named builder does not deliver": it means the manifest cannot be completed
by naming a different existing builder either. **I am not designing the resolution** — extend one,
compose with an explicit check at each stage, or something else, is the designer's, and Part E prices
what supplying it would cost me.

## S.2 — PRE-REGISTERED: WHAT WOULD MAKE ME RETURN *BLOCK*

Committed before the manifest exists.

- **S1 — a builder that implements the declared arity WITH both-direction orphan refusal**, or an
  explicit statement of which property is being given up and what accounts for the bins it drops.
  §S.1 is why this is not satisfiable by a citation today. This is `F2` promoted from an unrecorded gap
  to the blocking condition.
- **S2 — ⚠ IF ANY MAP IS BUILT BY COMPOSING SINGLE-AXIS DROPS, THE COMPOSITION ORDER MUST BE
  DECLARED.** The width weights compose exactly (`w_a·w_b`), so the *mathematics* is order-independent
  — but the *arithmetic* is not. Measured in Part R §R.5a: at band-assembly scale, pairwise-versus-
  sequential summation is **bit-identical**, while **reversing the order moves the result by
  `~5e-16`–`1.3e-15` relative**. A composed projection is a summation over dropped-axis cells, so an
  undeclared order is an undeclared perturbation at that scale — small, and *exactly* the scale at
  which a reproducibility gate is set. **This is my own measurement transferred to a new subject, and
  nobody has raised it for the manifest.**
- **S3 — declared exclusion must be distinguishable from silent discard BY THE ARTIFACT**, not by
  prose. Joseph's worked example is the `[3,100] GeV` catch bin excluded from `fig:eavail`'s axis: a
  *declared* exclusion, not a dropped bin. The mechanism that makes the two indistinguishable is
  named in §S.1 — `dst_index_of` returning `-1` is how a discard becomes invisible, and a manifest
  that accounts for the catch bin as a dropped bin, or a dropped bin as a declared exclusion, would be
  **right about the count and wrong about the population.**
- **S4 — bar type declared for every map**, since `sec_3d.tex:261-265`'s caption makes P2 and P3
  *"Grouped fractional **systematic** bands"* while P1 and P4 are unstated. A total bar and a
  systematic-only bar are different quantities and the caption is currently the only declaration.
- **S5 — source AND destination artifacts bound, not pointed at.** A `--dst-cv` *policy* is sound
  reasoning and is not a bound artifact; `F2`'s builder-and-commit requirement applies to the
  destination product too.
- **S6 — Q3's rank declaration must not be read as an `ndf`.** Under Ruling 1 nothing is inverted, so
  a rank declaration is a property of the matrix and **not** clause (ii)'s retained-rank-as-`ndf`.
  `F18` and Part L §L.2 both bar inversion-grade obligations here; a rank *declaration* is admissible
  precisely because it makes no inversion claim, and it stops being admissible the moment it is cited
  as an `ndf`.

## S.3 — WHAT THE MANIFEST CLOSES, AND WHAT IT MAKES LOAD-BEARING

**It closes `F1`.** `F1` required the released set to be *enumerated, not described by role*, and Part
Q §Q.4 recorded that Joseph's *"explicitly named projections"* **entails** `F1` without supplying it.
`P1`–`P4` plus the disjoint `Q1`–`Q3` is that enumeration. **Its arrival is what makes `F1`
closable — and its completeness is the only thing standing between the entailment and the
satisfaction.**

**It makes `F-I` maximal rather than incidental.** Every one of P1–P4 is a marginalization dropping
three or four axes, so destination row support is enormous, and `F-I` says each released bar is a
linear functional of the off-diagonals over its own row:

| map | destination bins | mean row support | off-diagonal terms per released bar |
|---|---|---|---|
| P1 | 42 | 254.6 | ~32,000 |
| **P2** | **7** | **1527.7** | **~1,166,000** |
| P3 | 14 | 763.9 | ~291,000 |
| P4 | 16 | 668.4 | ~223,000 |

**P2's seven released error bars each aggregate over roughly 1,528 reported 5D cells**, so about 1.17
million off-diagonal entries enter one bar. `F-I` was filed when the only example was P1's 42-bin
case; P2 is an order of magnitude further in, and `cause3_corr` remains withheld.

## S.4 — NOT ASSESSED, AND NOT TO BE READ AS CLEARED

- **The manifest itself** — it does not exist in complete form and I have not read `cc2a71aa`'s body.
- **The 1% accuracy criterion** — the reviewer's.
- **The rejected yardsticks and the universal bound** — closed by ruling, and I am not reopening them.
- **`A-6(a)`, `A-6(b)`, the excluded producing execution, and the three-or-four block population** —
  all remain open and undischarged, per Joseph's standing note that the reuse-branch feasibility
  condition reading **NOT APPLICABLE** does not imply other numerical or finite-ensemble limitations
  disappear.
