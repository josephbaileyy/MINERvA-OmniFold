# PROPOSAL 2026-09-16 — one bounded route to `B`, and what remains of `S`

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the materiality analysis in §2, measured from the implementation; the
scope limits in §1 and §3; the enforced caps in §4.

**NOT CITABLE FOR:** any value of `B`, any value or grade of `ε`, any adoption. **`B` and the
full scientific cap `S` are both UNESTABLISHED.** `ε = 1e-9` remains **PROPOSED and UNGRADED**;
`S` is discharged **for the F7 channel only**. **A1 is OPEN.** Gate 2 **FAIL**, `cause3_corr`
**WITHHELD**, endpoint B **DEFERRED NOT PASSED**.

**This authorizes nothing.** No compute is requested or held. Z's own bank may be **specified as an
input** to this prospective control; that permission does not authorize compute, tolerance
selection from its results, grading the precursor, or adopting a modified estimator.

Measured at `c539da5d74b56e3ae8a508d9ae22a6d775ffdf5d` unless another sha is named.

---

## 1. What bitwise agreement can support, and what it cannot

The predeclared estimator is boolean: `IDENTICAL → B = 0`, otherwise route (i) falsified, with the
observed magnitude explicitly excluded. That is the right shape — reading no *value* off Z's null
is what makes it admissible where declaring `B` from the precursor's executions is barred. But
three limits must travel with any result, and the first two were not stated in the predeclaration:

**(a) Observed agreement supports only the CONFIGURATIONS ACTUALLY TESTED.** `n` runs that agree
bitwise establish agreement for the `n` allocation shapes sampled, and nothing about shapes not
sampled. It is an existence statement over a finite sample, not a property of the envelope.

**(b) `B = 0` ACROSS A DECLARED ENVELOPE IS A SEPARATE CLAIM, and it needs an enforcement
argument, not more runs.** To say "B = 0 for this envelope" is to say the implementation *enforces*
bitwise reproducibility for every configuration the envelope admits. Observation cannot deliver
that; only a documented guarantee from the implementation, checked against how it is invoked, can —
and it must be checked against the **installed** version, not a general claim. §2 sets out what that
guarantee does and does not cover here. **Absent it, the defensible statement is `B = 0` for the
tested configurations, and the envelope is defined by enumeration rather than by property.**

**(c) THREE RUNS ARE A BOUNDED FALSIFICATION EXPERIMENT, NOT A PROOF AND NOT COVERAGE.** Their
power is one-directional: disagreement **falsifies** route (i) decisively, agreement **fails to
falsify** it over three shapes. No coverage or confidence statement follows from three trials under
the declared deterministic model, because that model has no sampling distribution to cover — which
is exactly why the declaration had to choose a model before choosing a count. A result of
"3 of 3 identical" must be reported as *did not falsify*, never as *established*.

---

## 2. Which runtime settings materially affect THIS implementation

⚠ **CORRECTION.** I relayed, and this lane's earlier text carried, the claim that every proposed
control "pins thread COUNTS only". **That is false.** The proposed set is `num_threads`,
**`deterministic`** and **`force_row_wise`** — the latter two are not counts, and `deterministic`
is the only one that is a reproducibility guarantee at all. The correction matters because it was
used to argue the pin set is inadequate, and the real inadequacy is different and narrower.

⚠ **And absence from a text search does not establish a requirement.** That four `OMP_*` names
appear nowhere in `nd-unfolding/` shows they are **unrecorded**; it does not show they are
**material**. Materiality has to come from the implementation. Below it does.

### What the implementation says about itself

`omnifold_nn_core.py:203-204`: *"LightGBM at these settings is otherwise **nearly** deterministic
in `seed` alone."* The hedge is the implementation's own, and the residual it hedges about is
exactly what `B` must bound.

`make_estimators` (`omnifold_nn_core.py:143-148`) passes **five** kwargs for the lgbm branch —
`n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1`, plus `random_state` — and
**no** `n_jobs`, `num_threads`, `deterministic`, or `force_row_wise`. So thread count is governed
by the OpenMP environment, and the histogram construction method is chosen by LightGBM at runtime.

### The CV numerical path — a BOUNDED TRACE, replacing a two-file name search

⚠ **My earlier evidence was a name search over two files and it missed the kernel.** I grepped
`omnifold_nn_core.py` and `unified_throw_cov.py` for `.dot(`/`matmul`/`einsum`, found zero, and
concluded the BLAS variables were immaterial. The conclusion happens to survive, but the search
did not cover the path: `_xsec_for_weights` is **imported**, not defined in either file
(`unified_throw_cov.py:75`), and at `unified_throw_cov_5d.py:91` the base module's symbol is
**monkey-patched** — `base._xsec_for_weights = _xsec_for_weights_5d` — so the function that
actually runs is in a third file I never opened, and it contains both the histogramming and the
completeness division.

The path, traced:

| stage | site | what it does |
|---|---|---|
| 1 | `unified_throw_cov.py:907` | calls `_xsec_for_weights(...)` — resolved to the 5D kernel by the patch at `unified_throw_cov_5d.py:91` |
| 2 | `unified_throw_cov_5d.py:57-62` | `omnifold_loop(...)` from `omnifold_nn_core` → `w_pull`, `w_push`. LightGBM fits live here |
| 3 | `unified_throw_cov_5d.py:66-68` | `np.histogramdd(sample, bins, weights=w_push * wt_sig[m])` → `unfold_nd` |
| 4 | `unified_throw_cov_5d.py:68`, `:76-77` | `np.histogramdd(..., weights=wt_sig[m])` → `of_in`; `np.histogramdd(..., weights=wt_td)` → `denom_nd` |
| 5 | `unified_throw_cov_5d.py:78-80` | `completeness[nz] = of_in[nz] / denom_nd[nz]` |
| 6 | `xsec_nd.py:54-83` | `extract_cross_section_nd(unfold_nd, completeness, flux, pot, nucleons, edges)` |

**Five modules, not two.** `unified_throw_cov.py` → `unified_throw_cov_5d.py` → `omnifold_nn_core.py`
→ `numpy.histogramdd` (three calls) → `xsec_nd.py`.

### DEMONSTRATED versus NOT ESTABLISHED

**DEMONSTRATED source of variation — exactly one.** Stage 2, the LightGBM fits. Evidence: the
module's own hedge (`omnifold_nn_core.py:203-204`, "**nearly** deterministic in `seed` alone") and
the precursor's measured `operands_bitwise_identical: False` at relative L2
`4.4520002137582904e-14`.

**ESTABLISHED DETERMINISTIC-AND-LINEAR.** Stage 6. `xsec_nd.py:79-82` computes
`denom = completeness * flux_b * n_nucleons * data_pot * vol` and then
`np.divide(counts * 1.0e4, denom, out=xsec, where=good)` — elementwise only, with `denom`
independent of `counts`. Measured through the real function on synthetic arrays: the per-bin
relative deviation in `xsec` equals that in `counts` to **2e-16** at perturbation scales `1e-3`
through `1e-12`.

**NOT ESTABLISHED — behaviour not determined, and recorded as such rather than assumed.**
Stages 3-5, the three `np.histogramdd` calls and the division. NumPy's `histogramdd` is expected
to be single-threaded with an accumulation order fixed by input order, but **I have not measured
it**, so it is not claimed. Stage 1's `np.column_stack` and the boolean indexing are copies, not
reductions.

**So the BLAS conclusion stands but on different evidence:** no stage in the traced path performs
a matrix product. The relevant variables are immaterial to the CV numerics because the path has no
BLAS reduction, not because two files lacked a substring.

### Classification

| class | settings | why |
|---|---|---|
| **MANDATED BY THE DOCUMENTATION** | `force_row_wise=true` **or** `force_col_wise=true`, together with `deterministic=true` | LightGBM v4.5.0's `deterministic` entry, Note 2: *"to avoid potential instability due to numerical issues, please set `force_col_wise=true` or `force_row_wise=true` when setting `deterministic=true`"*. Not advisory — it is the documented precondition of the guarantee. |
| **THE GUARANTEE ITSELF** | `deterministic=true` | *"used only with `cpu` device type"*; absent it, LightGBM promises nothing. |
| **USEFUL, NOT REQUIRED BY THE GUARANTEE** | `num_threads` | See the correction below. |
| **MUST BE RECORDED** | `OMP_NUM_THREADS`, `OMP_DYNAMIC`, `OMP_THREAD_LIMIT`, and the thread count the process resolves | Cheap, and it is what distinguishes the failure modes in §4. |
| **NOT ESTABLISHED AS MATERIAL** | `OMP_PROC_BIND`, `OMP_PLACES` | Affinity and placement, not reduction order. Listing them as required pins over-claims. |
| **UNDETERMINABLE FROM THIS TREE** | `OMP_SCHEDULE` | Affects only `schedule(runtime)` loops; whether the installed build has any is not answerable here. |

### ⚠ CORRECTION: I had the thread-count claim BACKWARDS

I wrote that `deterministic=true` is *"documented as reproducible for the same data and the same
number of threads"* and therefore *"does not extend across thread counts, so the thread count must
be a fixed member of the envelope"*. **The documentation says the opposite.** LightGBM **v4.5.0**,
`deterministic`, bullet 2, verbatim:

> setting this to `true` should ensure the stable results when using the same data and the same
> parameters (**and different `num_threads`**)

So the guarantee **explicitly covers differing thread counts**, and pinning `num_threads` is not
required by it. Pinning it remains harmless and removes one variable from the receipt, but it is
not the load-bearing pin — `deterministic` plus a `force_*_wise` flag is. (Text verified identical
on the pinned `v4.5.0` page and on `latest`; the `latest` page states no version, which is why the
citation is to v4.5.0.)

### ⚠ AND THE REAL OBSTACLE IS THE ONE I MISSED — "different systems"

The same entry, bullet 3, verbatim:

> when you use the different seeds, **different LightGBM versions**, the binaries compiled by
> **different compilers**, or **in different systems**, the results are expected to be different

**This is in direct tension with `§4.4a` item 2**, which requires the repeats to **span DIFFERENT
ALLOCATIONS** on the ground that *"repeats on one node do not test it — they test in-process
determinism, which is the easy half."* If different allocations deliver different systems —
different CPU models, which `--qos=shared --constraint=cpu` neither controls nor guarantees — then
**LightGBM's documentation PREDICTS disagreement**, and a cross-allocation disagreement would
*confirm documented behaviour rather than falsify the pinning*.

That matters because `§4.4a`'s closing line says *"if item 1 or 2 fails — the pinned chain is not
bit-identical — route (i) does **not** deliver a design property at all."* Under this reading item 2
can fail for a reason that is **not a defect in the pin set**, and the closing line would retire
route (i) on evidence that never bore on it.

**So the envelope has to be defined, and the definition is now a substantive choice, not a
formality:**

- **Scoped envelope** — same CPU model, same LightGBM build, same compiler. `B = 0` is then
  claimable **within that class only**, and cross-class variation becomes a separate term that is
  *not* bounded by this experiment and would need its own argument. This is the only option the
  documentation supports.
- **Allocation-spanning envelope** — what item 2 asks for. The documentation declines to support
  it, so route (i) cannot deliver a design property over it, and `B` would have to be measured
  (route (ii), gated) rather than argued.

**The per-run CPU-model receipt is therefore necessary for a different and stronger reason than I
first gave:** not merely to disambiguate a failure after the fact, but because **the envelope
cannot be stated without it.** The LightGBM version and compiler identity belong in the same
receipt, for the same reason.

**And this is why the installed build must be read before any run.** The quoted text is v4.5.0's;
the installed version is not readable from this checkout (`import lightgbm` →
`ModuleNotFoundError` here). If the installed build predates the `deterministic` parameter, or
documents it differently, every line above is void. That check is a prerequisite and costs no
compute.

---

## 3. What a pinned-chain result can establish about the EXISTING UNPINNED PRECURSOR

**Explicitly: nothing about the precursor's own determinism.** Stated plainly because the
temptation runs the other way.

- The precursor ran **unpinned** — arm 7 sets none of the five thread variables.
- A pinned-chain result characterises the **pinned** configuration. The precursor is not in it.
- The precursor's own record, `operands_bitwise_identical: False` at relative L2
  `4.4520002137582904e-14`, is a **measured baseline for the unpinned arm** — the arm the pinned
  experiment does not describe.
- So a pinned `IDENTICAL` result would establish that the chain *can* be made bitwise reproducible.
  It would **not** retroactively give the precursor a bound, **not** grade the precursor, and
  **not** make its null a `B`.
- Conversely a pinned **disagreement** would show the chain cannot be pinned by these settings, and
  would leave the precursor exactly where it is.

The precursor is **not reopened** by any outcome here. Its persistence obligation is separately
already discharged: `hCvExecution{k}` / `hCvSupportMask` are absent at `923e1323` and present at the
precursor's producing revision `e09513d8`.

---

## 4. The bounded experiment — outcomes, limits, enforced caps, follow-on

**Prerequisites, all zero compute, all before any run:**

1. Read the **installed** LightGBM version and its `deterministic` guarantee text (`lane_b`, on the
   cluster). §1(b) cannot be answered without it.
2. Fix `num_threads`, `deterministic=True`, `force_row_wise=True` in `make_estimators`' lgbm branch,
   Z-scoped (`lane_b`). Fix or record the **MUST BE RECORDED** row of §2.
3. A per-run receipt capturing node name, **CPU model**, and process-visible thread settings.
4. Whether arm 7 may run on **Z's own bank** — now permitted as an input to this prospective
   control, which removes the `SPEC:3140` obstruction for *this* predeclared, boolean-estimator
   design only.

**Design:** `n = 3` pinned executions of the **full CV unfold chain** — two on the same node shape,
one on a different node — compared **bitwise elementwise over the `x_cv > 0` predicate**, never a
hardcoded bin count. Two same-shape runs test same-shape determinism; the third tests cross-shape.
Requires **≥ 2 distinct node names**; fewer means the cross-shape arm is **NOT TESTED** and the run
is **INCONCLUSIVE, not a pass**. If CPU models do not differ, the cross-microarchitecture arm is
**UNEVALUATED** and is stated as such, never folded into a pass.

**Outcomes, and what each licenses:**

| outcome | licenses |
|---|---|
| 3 of 3 identical, ≥2 node names, ≥2 CPU models | route (i) **not falsified** for the tested shapes. `B = 0` for those configurations by enumeration. Extension to the envelope requires §1(b)'s enforcement argument, separately. |
| 3 of 3 identical, 1 node name or 1 CPU model | **INCONCLUSIVE.** Same-shape determinism only; the cross-shape or cross-microarchitecture arm is unevaluated. |
| any disagreement | route (i) **FALSIFIED**, and the receipt says which of the three causes in §2 applies. `B` is **UNDEFINED** and is **not** set to the observed difference. |

**In no outcome does `ε` follow.** `B = 0` gives `B ≤ S` trivially for non-negative `S`, but a gate
at `ε = 0` fails on any nonzero deviation whatever — the mirror of the `1e-12`-clamp defect §3.1a
measures — and `SPEC:1410` forbids reading `ε` off Z's null. **`ε = 1e-9` continues to stand or fall
on its own transfer argument, with its own falsifier still unevaluated.**

### Enforced resource caps — priced by the cap, not by history

Arm 7's launcher enforces `--time=03:00:00` with `--cpus-per-task=16`
(`sbatch_uthrow_combine_5d_fast.sh:4`). Priced at the launcher's own enforced wall cap, three runs
reserve **9.0 CPU task-hours**. That is the number to admit against R5, because it is what the
scheduler will permit to be consumed.

**The cap can and should be lowered, and lowering it is the price control.** Submitting with an
explicit `--time` shorter than the script's own directive enforces the tighter bound. Historical
arm-7 elapsed times — `0.3875` / `0.4239` / `0.5764` CPU task-hours, three runs — are offered only
as **corroboration that a chosen cap is not absurd**, never as the reservation: three
measurements of a requeueing chain bound nothing about a fourth, and this campaign has now had
five submissions fail for reasons no elapsed-time series would have predicted.

**Recommended request when the prerequisites are met: `--time=01:00:00` × 3 = 3.0 CPU task-hours
reserved**, which is ~1.7× the largest historical elapsed and materially below the 9.0 the
unmodified launcher would reserve. **Not requested here.**

**Follow-on work this does not cover:** §4.4a items 1–3 as code (`lane_b`); item 6, `S` argued
independently; and §7 item 4, below.

---

## 5. `S` — the completeness channel, BOUNDED, with the premise named

`S` is discharged for the F7 channel. §C.2 named **two** uncovered channels by which a CV
perturbation reaches `C_unified`: the **throw deviations** and the **completeness division**. This
section closes the second. **It does not close the first.**

Restating that no `n`-dependent bound exists does not finish the task, so here is the premise that
does, and the measurement of it.

### The premise

**(i) The perturbation enters through `unfold_nd` ALONE.** Of the three histograms in the kernel,
only `unfold_nd` carries the OmniFold output: `weights=w_push * wt_sig[m]`
(`unified_throw_cov_5d.py:66-68`). `of_in` uses `weights=wt_sig[m]` and `denom_nd` uses
`weights=wt_td` — the **input** weights. So `completeness = of_in/denom_nd` is
**independent of `w_push`**, and a null-comparison perturbation, which by construction differs
only through the estimator while holding the input weights identical, **cannot move it**.

**(ii) The cross-section is EXACTLY LINEAR in that histogram, with a perturbation-independent
gain.** `xsec_nd.py:79-82`:

```python
denom = completeness * flux_b * n_nucleons * data_pot * vol
np.divide(counts * 1.0e4, denom, out=xsec, where=good)
```

`denom` is a function of `completeness`, the flux, the POT, the nucleon count and the bin volume —
**none of which depends on `counts`**. So `xsec = counts · 1e4 / denom` is linear with per-bin
gain `1e4/denom_i`.

### What follows, and it is the answer

Under (i) and (ii), a perturbation `Δ` in `unfold_nd` produces `Δxsec_i = 1e4·Δ_i/denom_i`, so the
**per-bin RELATIVE deviation is preserved exactly**: `Δxsec_i/xsec_i = Δ_i/unfold_nd_i`. **The gain
cancels.** And `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` is an `x²`-weighted RMS of per-bin relatives, so
it is a convex combination of preserved quantities.

**Therefore the completeness division contributes gain exactly 1 to the statistic the null
criterion grades, and needs no `n`-dependent bound for it.**

### Measured, not just read

Through the real `extract_cross_section_nd`, on synthetic arrays with `completeness` spanning four
orders of magnitude including a `1e-12` bin:

```
per-bin relative deviation, xsec vs counts:  max|difference| = 2e-16  at eps = 1e-3 … 1e-12
r_null-shaped statistic, completeness as-is:  8.037319650110e-10
                         completeness x1e-3:  8.037317394100e-10
                         completeness x1e3 :  8.037318622973e-10
```

**Rescaling the completeness by six orders of magnitude moves the statistic in the seventh
significant figure** — round-off, not amplification.

The `1e-12` bin was **not** excluded by `where=good` (its `denom` is still positive); it yields a
*tiny* `xsec`, which the `x²` weighting then **down**-weights. So the pathological case is
suppressed in this statistic rather than amplified — the opposite of the concern.

### So what is `SPEC:1662` right about?

It is right, and about a different quantity. *"An elementwise division by a quantity that can be
small"* bounded by *"nothing, and it is an amplification channel with no `n`-dependent bound"*
describes the **absolute** cross-section scale: a small `completeness_i` does make `xsec_i` large,
without bound. **That characterisation simply does not reach a RELATIVE statistic**, because the
same factor sits in numerator and denominator.

**The consequence for `S` is conditional and worth stating precisely.** If `S` is expressed as a
cap on a **relative** CV movement — which is the form `r_null` takes, and the form §C.1 adopted —
the completeness channel is bounded and the F7 argument extends through it. If `S` were expressed
as an **absolute** cap, as the withdrawn `5.00e-41` was, the amplification is real and unbounded,
and this section does not help. **The relative form is therefore not merely convenient; it is what
makes this channel boundable at all.**

### What remains uncovered

- **The throw-deviation channel.** Not addressed here, and I make no claim about it. §7 item 4.
- **Stages 3-5 of the trace** are *not established* deterministic (§2). The bound above is on
  **propagation** of a perturbation, and assumes the histogramming is a fixed linear map of its
  weights. That is a property I have not measured.
- **Premise (i) is specific to the NULL comparison.** Two executions differing in their input
  weights — a different throw — *would* move `completeness`, and then it is not perturbation-
  independent. The bound covers the null, not the throw ensemble.

## 6. The independent assessor — resolved operationally

`owners.tsv:15` names `z-independent-assessor session [cb0b6b]`, a historical identifier the
responding session could not resolve to itself from any artifact. **It does not need to.**
Identity and independence are established from committed evidence:

| check | result |
|---|---|
| identity | `owners.tsv:15`'s `[cb0b6b]` matches the live `z-independent-assessor [cb0b6b]` row, and the bare name resolves to exactly one session. Row 14 corroborates the same ref namespace, so it is two rows, not one. |
| requirements predeclared | `923a321c` (prereg, 10:54:21) is an **ancestor** of `fdf5e510` (assessment, 11:06:37) — declared 12 minutes earlier, in ancestry order, not retrofitted. |
| authorship separation | **0** commits touching `RECOMMENDATION-20260910-…` on `lane/z-criteria-independent-assessment-20260910`, against 15 elsewhere. The assessor never authored or edited what it graded. |
| lane separation | tips `8a42f8ea25b1` (criteria owner) and `fdf5e5101fbb` (assessor) are distinct, both pushed. |

**No replacement is nominated; the existing reviewer stands.** The unresolvable session identifier
does not block review, because the properties review needs — predeclaration and non-authorship —
are checkable in git and check out.
