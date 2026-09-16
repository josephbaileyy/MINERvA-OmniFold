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

### What is in the CV path, measured

- **The CV repeat runs at `train_frac=1.0`**, which the docstring says "reproduces the original loop
  exactly". At that setting `keep` is all-true, so **the split RNG does not enter the CV path.** The
  dominant ML variance the module describes is therefore *not* the channel `B` must bound.
- **No BLAS-threaded reduction exists in the CV path.** `.dot(`, `np.matmul` and `np.einsum` each
  occur **0** times in `omnifold_nn_core.py` and **0** times in `unified_throw_cov.py`. So
  `OPENBLAS_NUM_THREADS` / `MKL_NUM_THREADS` are **not material to the CV numerics**. (They are
  material to the assembly's eigensolve — a different step, and not what `B` bounds.)
- **Prediction is a per-row map.** `_reweight` (`:152-155`) uses `clf.predict_proba` with clipping
  and `nan_to_num`; there is no cross-row reduction, so thread count does not change it.

**So the material channel is narrow and specific: LightGBM's training-time histogram construction,
which is where the cross-thread reduction lives.**

### Classification

| class | settings | why |
|---|---|---|
| **MUST BE FIXED — changes numerics** | LightGBM `num_threads`; `force_row_wise` (or `force_col_wise`); `deterministic=True` | Thread count changes histogram reduction **order**. The row/col-wise choice is selected **at runtime from data shape and thread count**, so without fixing it the *algorithm* can differ between allocations, not merely the summation order. `deterministic` is the only documented reproducibility guarantee, and LightGBM requires one of the force flags for it. |
| **MUST BE RECORDED — can change the effective TEAM SIZE, hence numerics** | `OMP_NUM_THREADS`, `OMP_DYNAMIC`, `OMP_THREAD_LIMIT`, and the process-visible value of whatever LightGBM resolves as its thread count | `OMP_DYNAMIC` permits the runtime to return a **smaller** team than requested; a varying team size varies reduction order even with everything else pinned. Recording is sufficient where fixing is a code change. |
| **NOT ESTABLISHED AS MATERIAL — do not require on present evidence** | `OMP_PROC_BIND`, `OMP_PLACES` | Affinity and placement. For a **fixed team size** they change performance and NUMA locality, not floating-point reduction order. Listing them as required pins over-claims. |
| **UNDETERMINABLE FROM THIS TREE** | `OMP_SCHEDULE` | Affects only loops compiled `schedule(runtime)`. Whether the installed LightGBM contains any cannot be answered from this checkout. Record it; do not assert it matters or does not. |

### ⚠ The enforcement gap that §1(b) requires, named

`deterministic=True` is documented as reproducible **for the same data and the same number of
threads**. It therefore does **not** extend across thread counts, so the thread count must be a
**fixed member of the envelope** rather than something the envelope ranges over. And it says nothing
about **different CPU models**: a build may dispatch different SIMD widths on different
microarchitectures, changing reduction order at identical thread count.

**Consequence, and it upgrades the receipt requirement from good practice to necessity:** if the
runs disagree, "route (i) is falsified" is ambiguous between *the design cannot be pinned*, *the
design was never fully pinned*, and *the envelope spans microarchitectures the guarantee never
covered*. Recording node name, **CPU model**, and process-visible thread settings per run is what
separates the three. Without the CPU model, a disagreement is uninterpretable.

**The guarantee must be checked against the INSTALLED LightGBM**, whose version is not readable
from this checkout (it is not importable here). That check is a prerequisite, not a result.

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

## 5. What remains of `S`

`S` is discharged **for the F7 channel only**. The uncovered channel is not a rounding detail:
`SPEC:1662` records the completeness division `completeness[nz] = of_in[nz] / denom_nd[nz]` as
*"an elementwise division by a quantity that can be small"* bounded by **"nothing, and it is an
amplification channel with no `n`-dependent bound"**.

**So `ε ≤ S` is also undemonstrated, and the defensible sentence is "`S` is not binding THROUGH THE
F7 CHANNEL".** The unqualified form — "`S` is not binding" — is the sentence that travelled into a
decision-support record, and it is the stated reason `ε` is argued from `B`'s side at all. If an
uncovered channel's cap were tight, `S` could be binding after all. **§7 item 4 is upstream of more
than its placement suggests**, and it is arithmetic plus one code read.

---

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
