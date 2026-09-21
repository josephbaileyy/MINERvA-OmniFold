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

## 5. `S`'s propagation — NOT CLOSED. What is bounded, and the one number still missing

⚠ **`S` IS NOT CLOSED AND THIS SECTION DOES NOT CLOSE IT.** An earlier revision of this section
claimed the completeness division contributes "gain exactly 1" to `r_null`. **That claim is
withdrawn — it is false**, and the test that appeared to support it could not have detected the
error. What follows is the bound that survives, the conversion to a threshold, and the single
declared quantity that remains open. No `τ` is proposed here.

### 5.1 ⚠ WITHDRAWN: "gain exactly 1", and why my test could not see it

The per-bin *relative* deviations are preserved exactly — that part stands (`xsec_nd.py:79-82` is
linear in `counts` with a `counts`-independent gain; measured to 2e-16). But

```
r_null² = Σ c_i² Δu_i² / Σ c_i² u_i²  =  Σ w_i ρ_i² / Σ w_i ,   w_i = x_i² ,  ρ_i = Δu_i/u_i
```

so `r_null` is an **`x²`-weighted** RMS of the `ρ`. **Unequal per-bin gains change the weights**,
and therefore change the statistic, even though every `ρ_i` is preserved. My test rescaled
completeness **uniformly**, which leaves the weights' proportions unchanged — it was structurally
incapable of detecting reweighting.

**Re-measured with unequal gains**, one fixed `ρ` pattern spanning `1e-12 … 1e-9`:

| completeness pattern | `r_null` | vs `max\|ρ\|` |
|---|---|---|
| uniform `1e-2` | 7.383940e-10 | 0.738 |
| uniform `1e-5` | 7.383940e-10 | 0.738 |
| unequal, weighting the SMALL-`ρ` bins | **3.318246e-10** | 0.332 |
| unequal, weighting the LARGE-`ρ` bins | **7.627275e-10** | 0.763 |
| unequal, 8 orders, random | 7.403422e-10 | 0.740 |

The two uniform rows are **identical**; the unequal rows move the statistic by a **factor 2.3**.

**THE BOUND THAT SURVIVES**, and it is all that survives:

> `min_i |ρ_i|  ≤  r_null  ≤  max_i |ρ_i|`   over the reported support.

Every row above respects the upper bound. So the completeness division **cannot amplify `r_null`
beyond the per-bin maximum relative deviation** — which is exactly `ε`'s step 1
(`r_null ≤ max_i |Δ_i/x_i|`). **The channel therefore adds nothing beyond what step 1 already
bounds, and it is subsumed rather than "closed with gain 1".**

### 5.2 The throw-deviation channel, exactly

`uq_math.py:107-116`: `joint_throw_covariance` returns `mat_covariance(X), mean - cv`, and
`mat_covariance` (`:96-104`) is universe-mean centered with the **CV absent**. The variants differ
by exactly the square of the shift — `z_assembly.py:182-215`, single-source, and
`check_variant_coupling` (`:221`, `:320`) **gates** `v_uni^cv == v_uni^mean + ms²`. So per bin,
under `cv → cv + δ` (hence `ms → ms − δ`):

| variant | movement |
|---|---|
| mean-centered | **Δv = 0, exactly** — the CV is not an input |
| CV-centered | **Δv = −2·ms·δ + δ²**, exactly |

Verified against the real `derive_variant_diagonals`: identity at `0.000e+00`,
`Δv_mean = 0.000e+00`, closed form to 1.4e-11 at `eps = 1e-3`. (Degradation at smaller `eps` is
cancellation in the *check* — `~2.2e-16/eps` — not in the algebra.)

### 5.3 Through inflation and assembly, with two exact attenuations

`z_assembly.py:4-8`: `C_Z^c = D_Z^c (Σ_V C_b) D_Z^c + Σ_R + Σ_A + C_stat + C_ML`, with
`g^c[i] = sqrt(max(v_uni^c[i], v_blk[i])) / sqrt(v_blk[i]) ≥ 1`, pinned to 1 where `v_blk[i] == 0`.

Measured against that construction:

| bin class | propagation |
|---|---|
| **active**, `v_uni^cv > v_blk > 0` | `diag(D_Z Σ_V C_b D_Z)[i] = g_i² v_blk[i] = v_uni^cv[i]` to **2.5e-16** — so `Δ diag(C_Z)[i] = Δv_i^cv`, **one-to-one** |
| **deadband**, `v_uni^cv ≤ v_blk` | `Δ = 0.000e+00` — the `max` **absorbs** the perturbation exactly |
| `v_blk[i] == 0` | `Δ = 0.000e+00` — `g` pinned to 1 |

The non-CV terms `Σ_R`, `Σ_A`, `C_stat`, `C_ML` are additive and CV-independent, so they do not
propagate the perturbation but **do** enter the denominator of any relative statement below.

### 5.4 The complete implication, null threshold → protected uncertainty claim

The protected claim is the **reported per-bin uncertainty** `σ_i = sqrt(diag(C_Z^c)[i])`.

**FORWARD** — what a measured `r_null` implies, for an active bin:

```
‖δ‖₂ = r_null · ‖x_cv‖₂          (definition of r_null)
|δ_i| ≤ ‖δ‖₂                      (crude, conservative, assumption-free)
|Δv_i^cv| ≤ 2|ms_i|·|δ_i| + δ_i²  (§5.2, exact)
Δ diag(C_Z)_i = Δv_i^cv           (§5.3, active bins; 0 elsewhere)
Δσ_i/σ_i = sqrt(1 + Δv_i^cv/diag(C_Z)_i) − 1   ≈ Δv_i^cv / (2 diag(C_Z)_i)
```

**BACKWARD** — a candidate **sufficient** threshold on `r_null` from a declared tolerance `θ`.

> ⚠ **NOT ESTABLISHED.** The formula below is arithmetically verified under a FIXED bin partition
> and a FIXED F7 branch, and it bounds the DIAGONAL. It is **not** established as a sufficient
> threshold until the three conditions in §5.8 are addressed. Do not cite it as a criterion.

```
require  |Δσ_i/σ_i| ≤ θ  for every active bin
  ⟹  |Δv_i^cv| ≤ ((1+θ)² − 1) · diag(C_Z)_i  =:  V_i
  ⟹  |δ_i|  ≤  Δ_i  :=  V_i / ( sqrt(ms_i² + V_i) + |ms_i| )
  ⟹  SUFFICIENT:   r_null  ≤  min_{i ∈ active} Δ_i  /  ‖x_cv‖₂
```

⚠ **`Δ_i` must be written in that quotient form, not as `sqrt(ms_i² + V_i) − |ms_i|`.** The two are
algebraically identical and the subtraction **silently violates its own cap** once `V_i ≪ ms_i²`.
Measured: the naive form holds at `1e-2` and `1e-6` and **fails at `1e-9`, `1e-12`, `1e-16`** — the
regime a determinism tolerance lives in — while the quotient form achieves exactly the target from
`1e-2` to `1e-20`. The naive form's apparent pass at `1e-20` is underflow to a zero cap: vacuous,
not correct. **Implemented the obvious way, the threshold would be looser than declared.**

### 5.5 Assumptions, stated because the conversion is only valid under them

1. **FIXED ENSEMBLE.** `ms_i`, `v_i^mean`, `v_blk_i` and the additive non-CV terms are held fixed.
   The **null comparison satisfies this by construction** — identical input weights, differing only
   through the estimator. A different throw ensemble violates it, and then `ms` and `v^mean` move
   too and none of §5.2 applies.
2. **SUPPORT.** The `min` runs over the **reported support** `x_cv > 0`, the same predicate
   `null_ratio` uses. **A bin outside the support does not enter `r_null` and cannot be constrained
   by any threshold on it** — such bins need a separate argument, not a tighter `r_null`.
3. **DENOMINATOR.** `‖x_cv‖₂` is `cv_norm` as `null_ratio` computes it, over that same support. A
   different normalizer rescales the conversion linearly.
4. **ZERO-VARIANCE AND DEADBAND CASES**, each with its own handling rather than one rule:
   - `v_blk_i = 0` → `g` pinned to 1 → `Δ = 0` **exactly**. Unconstrained, and needs no tolerance.
   - `v_uni^cv ≤ v_blk` (deadband) → absorbed by the `max` → `Δ = 0` **exactly**. Same.
   - `diag(C_Z)_i = 0` → `Δσ/σ` is `0/0`, **undefined**. These bins must be **excluded from the
     `min` and their count reported**; a relative tolerance cannot constrain them, and silently
     including them drives `min_i Δ_i` to 0 and makes the threshold unsatisfiable.
   - `ms_i = 0` → the first-order term vanishes, `Δv = δ²`, and the cap loosens to
     `|δ_i| ≤ sqrt(V_i)`. No special handling, but the bin is then far less sensitive.
   - `derive_variant_diagonals` already returns `n_clipped_unified` / `n_clipped_blocksum`, so the
     clipped population is tracked by the existing code rather than needing new instrumentation.
5. **THE F7 BRANCH CONDITION, EXPLICIT.** This entire channel exists only when
   `uq_math.f7_cv_centered_required` fires — `‖ms‖ > k · sqrt(Tr C)/sqrt(N)` with
   `k = F7_FLOOR_MULTIPLE = 2.0` (`uq_math.py:138`, a codification with an owner and a date, not a
   repo decision). **If F7 does not fire, only the mean-centered variant is required, `Δv^mean = 0`
   exactly, and no threshold is needed for this channel at all.** For G it fires at 4.69x the floor
   (4.83x after the flux correction), so for a G-like ensemble it is live.
6. **FIRST ORDER WHERE MARKED.** `Δσ/σ ≈ Δv/(2 diag C_Z)` is an expansion; the exact form is given
   above and should be used in any implementation.

### 5.6 The remaining limitation, precisely

**This traces the DIAGONAL only.** `C_Z`'s off-diagonal also moves — `D_Z` multiplies `Σ_V C_b` on
**both** sides, so `ΔC_Z[i,j] = (g_i g_j − g_i⁰ g_j⁰)·(Σ_V C_b)[i,j]` for `i ≠ j`, which the
per-bin variance tolerance `θ` does not bound. **The declared scientific use is not only per-bin
uncertainties:** `SPEC` requires 3D/4D covariances to be exact projections of the adopted trunk,
and a projection contracts the **full** matrix, correlations included. **So a `θ` on per-bin
uncertainty is necessary and not sufficient for the projected claim**, and a correlation-side
tolerance is a separate, unaddressed quantity.

Also unresolved: stages 3-5 of the CV trace remain *not established* deterministic (§2); `ε` still
does not follow, because this is `S`'s side and `SPEC:1410` stands; and **`θ` is undeclared**.

### 5.7 Can the EXISTING inflation-factor bound protect the projected claim?

Asked before proposing any second, correlation-side tolerance. **Yes — and it does so with ONE
tolerance rather than two, provided it is declared on `g` rather than on the per-bin variance.**

`C_Z^c = D_Z(Σ_V C_b)D_Z + (CV-independent terms)`, and the CV reaches the first term only through
`D_Z = diag(g)`. Writing a relative movement of the inflation as `D' = D(I + Γ)`, `Γ = diag(γ_i)`:

```
ΔC_infl  =  Γ C_infl  +  C_infl Γ  +  Γ C_infl Γ         (exact, all i,j)
```

Verified against a PSD `Σ_V C_b` with `g ≥ 1` as G2 gates: max relative error **4.5e-15** at
`γ ~ 1e-2`. So for any submultiplicative norm and `‖Γ‖ ≤ γ`:

```
‖ΔC_infl‖  ≤  ((1+γ)² − 1) · ‖C_infl‖
```

⚠ **"AND THE SAME FACTOR BOUNDS EVERY PROJECTION" IS FALSE, AND IT WAS MY CLAIM.** Refuted by
`owners.tsv:15` at `5a6d32fb34b99da2f3974e46e22082be0a746d3d` (T5d) and **re-measured independently
here** before accepting it. At `γ = 0.30`, limit `((1+γ)²−1) = 0.6900`, maximising
`|wᵀΔC w| / |wᵀC w|` over non-negative `w` and adversarial diagonal `Γ` at the cap:

| inflated block `C` | eigenvalues | PSD | worst projected ratio | verdict |
|---|---|---|---|---|
| `[[1, 0.5], [0.5, 1]]` entrywise non-negative | `+0.500, +1.500` | yes | **0.6900** | at the bound — **holds** |
| `[[1, −0.999], [−0.999, 1]]` | `+0.001, +1.999` | yes | **180.9** | **VIOLATES by 262×** |
| `[[1, −1], [−1, 1]]` exactly singular | `0.000, +2.000` | yes | **4.2e9** and rising with the draw count | **UNBOUNDED** |

**All three are PSD and all three `w` are non-negative**, so *"non-negative contracting weights"* is
**not** the sufficient condition I implied. The denominator `wᵀCw` can be driven toward zero while
the numerator is not, so the failure is **unbounded rather than gradual**. The missing condition:
the inflated block's entries must also be **non-negative on the projected directions**.

**And my own verification below could not have seen it.**

⚠ **AND THE REASON IT COULD NOT BE SEEN IS SHARPER THAN "THE FIXTURE WAS NON-NEGATIVE"**, and
`[91eaa2]` supplied it: **for UNIFORM `Γ` the bound holds with EXACT EQUALITY on every `C`**, because
`ΔC = γC + Cγ + γ²C = ((1+γ)²−1)C` identically. Re-measured: uniform `+γ` gives **`0.690000` on the
benign AND on the anti-correlated matrix**; only `(−γ, +γ)` separates them — `0.689993` versus
`180.905`. **So a search that varies only the MAGNITUDE of a uniform `γ` passes on every
counterexample.** Both conditions are needed to see the failure: **non-uniform `Γ` AND an
anti-correlated `C`.** My earlier diagnosis was half of it.

The honest reading of the table below is therefore *"confirms the bound for uniform `Γ` on
non-negative fixtures"* — not *"confirms the bound"*.

⚠ **This is LIVE, not hypothetical.** Unfolded covariances are strongly anti-correlated between
neighbouring cells, and `AGENTS.md:27` records the historical 3D block-sum object at **rank 247** —
exact null directions already exist in this family.

**What survives:** the factor bounds the **full matrix** in any submultiplicative norm, and it
bounds projections **whose directions keep `wᵀC_infl w` away from zero**. Measured over 300
adversarial `γ` draws per level on an **entrywise-non-negative** fixture, all at the bound:

| `γ` | limit `((1+γ)²−1)` | worst full-matrix | worst projected |
|---|---|---|---|
| 1e-2 | 2.010000e-02 | 1.988233e-02 ✓ | 1.851135e-02 ✓ |
| 1e-4 | 2.000100e-04 | 1.971528e-04 ✓ | 1.778063e-04 ✓ |
| 1e-6 | 2.000001e-06 | 1.987461e-06 ✓ | 1.670323e-06 ✓ |

**So an additional independent correlation tolerance is NOT required.** A tolerance on the relative
movement of `g` bounds the diagonal, the off-diagonal and every projected contraction by one
factor. That removes the §5.6 limitation as a *separate quantity* — it does not remove it as a
*condition*, because of the caveat below and §5.8 item 3.

⚠ **THE CONDITIONS ON THIS RESULT, and the second one narrows it substantially.**

**(a)** The projected bound is relative to `‖P C_infl Pᵀ‖`, so it degrades if a declared projection
nearly annihilates the inflated block. The draws above used non-negative contracting weights; a
near-annihilating projection is not covered, and the declared projection set has not been checked.

**(b) ⚠ IT HOLDS FOR A TOLERANCE DECLARED ON `g`, AND `g` IS AN INTERNAL QUANTITY.** The criteria
owner's reply identifies what that costs, and I have verified both halves:

- **A diagonal rescaling preserves correlations exactly — but only of the term it multiplies.**
  `corr(D Σ_V D) = corr(Σ_V)`, measured invariant to **4.4e-16**. If `C_Z` *were* `D_Z Σ_V D_Z`, a
  diagonal tolerance would control the whole matrix. It is not: `D_Z` multiplies `Σ_V` **alone**
  (`z_assembly.py:4`), and the **total** `C_Z` correlation moves by **1.3e-1** on the same fixture.
  The invariance is real and **confined to a term that is not the product**.
- **The per-bin grip decays as `1/f_i`.** With `f_i := g_i²(Σ_V C_b)_ii / (C_Z)_ii`, the V-fraction
  of bin `i`'s variance, `dσ_i/σ_i = f_i · (dg_i/g_i)` ⚠ **TO FIRST ORDER — the word "exactly" was
  wrong and is withdrawn (§5.8, T5a).** The exact relation is `√(1 + f((1+u)²−1)) − 1`. Measuring
  it *"to six decimals at `dg/g = 1e-6`"* verified nothing about finite changes: the two forms agree
  to `2.5e-7` there, which is inside the six decimals quoted. So a `θ` declared on `σ` permits
  `|dg_i/g_i| ≤ √(1 + ((1+θ)²−1)/f) − 1`, which the first-order `θ/f_i` **over**-states; the
  off-diagonal V-part still moves by a multiple of `θ` that grows as `f` falls.

**So the two parametrisations fail in opposite directions, and `f_i` is required either way.** A
tolerance on `g` is mathematically sufficient for the full matrix but has **no scientific
justification** until it is mapped to the protected claim, and that map *is* `f_i`. A tolerance on
`σ` is scientifically direct but **does not control the off-diagonal**, by the same `f_i`.

**`f_i` is unmeasured.** Therefore §5.7 does **not** make the correlation side free, and an earlier
reading of mine that implied it did is qualified here. What §5.7 establishes is narrower and still
useful: **no SECOND, independent correlation tolerance is needed** — one tolerance suffices
*provided* `f_i` is known — so the open item is a measurement, not another judgement.

**The measurement, as the owner states it:** the per-bin variance decomposition of `C_Z` into its
five terms. It settles `θ`'s correlation-side grip *and* `θ`'s own scientific scale together.
⚠ Whether the five per-term diagonals are **persisted** is NOT established — the 13-key inventory
carries `hCov_combined5d_total_uthrow`, but `Σ_V`, `Σ_R`, `Σ_A L`, `C_stat`, `C_ML` have not been
verified separately recoverable, and it cannot be checked from here. **If they are not persisted,
this is a writer requirement in the family of §7 item 1 — Tier-2, `lane_b` — and not a measurement
at all.**

### 5.8 ⚠ THREE UNRESOLVED CONDITIONS — recorded, and S analysis PAUSED here

The sufficient-threshold formula in §5.4 is **NOT ESTABLISHED** until all three are addressed.

**(1) DEADBAND BOUNDARY CROSSINGS.** The threshold takes `min over ACTIVE bins`, but a perturbation
can move `v_uni^cv` across the `v_blk` boundary and **change which bins are active** — so the
formula is evaluated over a partition the perturbation itself can alter.
*What is established:* `max(·, v_blk)` is 1-Lipschitz in its first argument, so
`|Δ diag(D_Z Σ_V C_b D_Z)_i| ≤ |Δv_i^cv|` holds **uniformly, including across a crossing**. The
upper bound survives.
*What is not:* the active/deadband dichotomy used to select the min's index set, and therefore the
value of the min. A bin sitting just above `v_blk` can leave the active set under the very
perturbation being bounded.

**(2) POSSIBLE F7 BRANCH CHANGES.** §5.5 item 5 treated the F7 condition as a *static*
precondition. It is not: `f7_cv_centered_required` compares `‖ms‖` against
`k·sqrt(Tr C)/sqrt(N)`, and the perturbation moves `ms` by `−δ`, so **the branch itself is
perturbation-dependent**. If it flips, the CV-centered variant stops being mandatory and the
channel's existence changes under the quantity being bounded.
*What is known:* §C.2 measured the `‖dx‖` that flips the branch at `1.7957e11`–`2.0433e11` × G's
null, so at the observed scale the flip is remote. **"Remote at the observed scale" is not a bound
at a declared tolerance**, and the observed scale may not be cited as one — `SPEC:1410`.

**(3) PROPAGATION TO THE DECLARED PROJECTIONS.** §5.7 shows a `g`-side tolerance bounds every
projection by one factor, which answers the *structural* question. It does **not** discharge this
condition: the bound is relative to `‖P C_infl Pᵀ‖` and has not been evaluated against the
**actual declared projection set**, and `SPEC` requires the 3D/4D covariances to be *exact
projections of the adopted trunk*. Until those projections are named and checked, propagation to
the declared claim is asserted structurally and unverified numerically.

**(4) THE PER-BIN VARIANCE FRACTION `f_i` IS UNMEASURED**, and §5.7(b) shows both tolerance
parametrisations depend on it — one for its scientific justification, the other for its
off-diagonal grip. This is the operative dependency: the open item is a measurement (or, if the
per-term diagonals are not persisted, a Tier-2 writer requirement), not a further judgement.

**(4a) AND "ONE TOLERANCE PLUS ONE MEASUREMENT" MUST NOT BE READ AS "THE CORRELATION SIDE IS
SETTLED ONCE `f_i` IS KNOWN".** The criteria owner adopted the §5.7 simplification into its own §1
and returned two qualifications it does not carry. Both verified here:

- ⚠ **CORRECTED: the table below used a FIRST-ORDER inversion and is too pessimistic.**
  `dσ_i/σ_i = f_i·(dg_i/g_i)` is **first order only** — the exact relation is
  `√(1 + f((1+u)²−1)) − 1`, which agrees with the linear form to `2.5e-7` at the `u = 1e-6`
  verification point (**which is why that point could not see it**) and differs by ~1.7% at
  `u = θ` and ~7% at `u = θ/f`. Inverting **exactly**:
  `|u| ≤ √(1 + ((1+θ)²−1)/f) − 1`, and the composition collapses to
  **`‖ΔC‖/‖C_infl‖ ≤ ((1+θ)²−1) / min_i f_i`**. Re-measured here:

  | `min_i f_i` | first-order (published) | **exact** |
  |---|---|---|
  | 1.00 | 14.7% | **14.7%** |
  | 0.50 | 30.4% | **29.4%** |
  | 0.20 | 83.7% | **73.6%** |
  | 0.10 | 192.6% | **147.2%** |
  | 0.01 | 6471.8% | **1471.8%** |

  **The exact bound is tighter everywhere, and the 100% crossing moves from `min_f = 0.1716` to
  `0.1472`** — so fixing the error **widens** the region where the bound settles something.
  ⚠ **And `θ/f` PERMITS MORE than a `σ` tolerance actually allows**: unsafe if used as a *gate*,
  conservative if used as a *bound input*, which is the only use made of it here.
  ⚠ **The inversion is also ONE-SIDED**: below `f = 1 − (1−θ)² = 0.1371` a `σ` tolerance bounds no
  **downward** `g` movement at all — `g` may fall toward zero while `σ_i` moves by less than `θ` —
  so `γ = max_i|u_i|` is **not finite from `θ` alone** on that population.
  **Below `min_f ≈ 0.147` the bound exceeds 100% and settles
  nothing.** Sufficiency is conditional on the measured value, and the conditional must travel
  with the simplification.
- ⚠ **THE MINIMISATION IS MIS-SPECIFIED BEFORE IT IS A POPULATION CHOICE (T5e), AND MY OWN TWO
  SECTIONS DISAGREED.** §5.8(1) above says the threshold takes `min over ACTIVE bins`; this bullet
  and the decision-support record took it over **all 10,694**. The active reading is the correct
  one, and the reason is mechanical rather than a matter of taste: `z_assembly.py:6-7` defines
  `g^c[i] = sqrt(max(v_uni^c[i], v_blk[i])) / sqrt(v_blk[i])`, so **wherever `v_uni ≤ v_blk` the
  `max` returns `v_blk` and `g` is clamped to exactly 1** — those bins contribute `u = 0` whatever
  their `f`. Relayed from the pilot receipt: `n_gt_one = 6528` and
  `n_saturated_v_uni_below_v_blk = 4166`, which **partition the support exactly**
  (`6528 + 4166 = 10694`), so **38.96% of the support is clamped**. Taking the min over the full
  support lets a bin the perturbation **provably cannot touch** set the bound.
  **The crossing caveat survives as the residual:** "active at the current CV" is not a
  prospectively safe index set, and what margin makes it safe is a design act not taken here.
- **`min_i f_i` is an extreme-order statistic over its population**, so a uniform-`γ` bound
  is set by the single worst bin — by construction a bin where the unified throw contributes
  almost nothing. Measured on a 4,000-bin fixture, `min f` falls monotonically with population
  size: `9.25e-2` over 100 active bins, `2.05e-2` over 1,000, `1.11e-2` over 1,975. A vacuous
  derived bound may therefore be an artifact of maximising over a large population rather than
  evidence of a defect.

**The owner's remedy — an active-set restriction rather than a tighter `θ` — is right in
principle, and I measure it to be PARTIAL.** Tightening `θ` below its scientific ceiling to rescue
a bound set by a dead bin would be choosing a tolerance to obtain a verdict. But the deadband
population and the small-`f` population are **not the same set**: on the fixture the global worst
bin *is* a deadband bin (`min f` all = `1.546e-3`, deadband = `1.546e-3`), yet **`min f` over the
ACTIVE bins is still `1.106e-2`**, giving `γ = 6.4` and a bound that remains vacuous. Excluding the
deadband is correct — those bins have `Δ = 0` exactly and `g` pinned, so they impose no constraint
— and it buys about an order of magnitude here, **but it does not by itself make the derived bound
non-vacuous.**

**So the joint character survives in a weaker form: not two tolerances, but a tolerance and a
POPULATION — and the population is a declaration.** Which further restriction beyond the deadband
is defensible is a scientific judgement about which bins' covariance is actually consumed, not
something derivable here.

**Analysis paused here** pending these four. Nothing in §5 is a criterion; nothing is adopted.

**One consequence recorded and deliberately NOT acted on.** The criteria owner states that §5.1's
withdrawal plus §5.2's exactness would together discharge `SPEC` §7 item 4 — its own recorded
residue on `S` — and declines to say so itself, because §C.2, §C.3 and item 4 are all its work and
judging that would be grading its own. Algebra accepted by it, **verdict withheld**, routed to
`owners.tsv:15`. Item 4 therefore stays OPEN, and `S` is not recorded closed.

### 5.9 `θ`/`γ` — routed, and what must not happen to it

The criteria owner (`owners.tsv:14`) may finish the already-requested recommendation. Per §5.7 it
should be expressed on `g`. No further review rounds and no tolerance decision are needed before
the pilot, which is measurement-only and unaffected by any of this.

It must **not** be chosen so the observed null passes: `SPEC` §6.4 and `:3584` forbid it, and
`r_null = 4.452e-14` is Z's own null, which `SPEC:1410` bars from setting anything.

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
