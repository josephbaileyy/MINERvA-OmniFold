# ASSESSMENT 2026-09-18 — the replacement L3 statistic, and its four attack lines

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subject:** §10 of
`PACKET-20260918-scalar5d-completion-inventory-and-null-route.md` at `3ebfd407`, with
`probes/probe-20260918-l3-statistic-diagonal-breach-and-repair.py`. **Author:** the assembly-pilot
lane, which supplied the statistic after I declined to — so **it cannot assess it and I can**, having
refuted the predecessor at `8df3b173` `C1` without proposing a successor.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the verdict on the replacement statistic and findings `L1`–`L7`.

**NOT CITABLE FOR:** adoption of the statistic, any `τ_p`, any boundary value, or any grade. All four
`Z_BOUNDARIES` keys stay **WITHHELD**. `renorm(C_k)` is a **diagnostic transform and is not a
covariance** for any other use. No member is requested.

## Evidence classes

- **CONSTRUCTION** — exact algebra, no measurement needed.
- **PROBE (MINE)** — my own synthetic-matrix arithmetic, preserved at
  `probes/probe-20260918-L3-disjoint-vs-actual-and-reference-dependence.py`.
- **PROBE (THEIRS, RUN BY ME)** — their probe executed here, not taken on report.
- **PAYLOAD (MEASURED BY ME)** — `z-cv.npz` read read-only on a login node; no `sbatch`, no `srun`,
  `R5` untouched.

---

# VERDICT

**ENDORSE the replacement as the L3 instrument, conditional on three statements being made on the
artifact** (`L3`, `L4`, `L5`). Its invariance is exact **by construction**, not by measurement, which
is the right kind of ground. And its stated cost — the hybrid — is not a concession to be weighed but
**a theorem**: I tested the author's claim 1 as they asked, and it is true and provable (`L2`).

---

## `L1` (CONSTRUCTION + PROBE, THEIRS, RUN BY ME) — the invariance holds, exactly

`corr(D C_k D) = corr(C_k)` identically for positive diagonal `D`, so
`renorm(D C_k D) = D0 · corr(D C_k D) · D0 = D0 · corr(C_k) · D0 = renorm(C_k)` **identically**, and
the statistic that follows is therefore invariant by algebra rather than by sampling. **That is
strictly better than the predecessor's ground**, which was an empirical claim about the wrong object.

**I ran their probe rather than accepting its output.** Reproduced: source-correlation drift
`4.441e-16` throughout; the **proposed** statistic breached at
`0.0004 / 0.0034 / 0.0179 / 0.0753 / 0.1854` for rescale sd `1e-3 … 0.70`; the **repaired** statistic
invariant at `3.3e-16`–`4.4e-16` at every scale **including sd = 2.0**; and responsive to genuine
correlation change at `0.0021 / 0.0108 / 0.0454`. **So it is invariant and it is not vacuous.**

## `L2` (PROBE, MINE) — their claim 1 is TRUE, and it is a theorem rather than a design judgement

They asked me to test *"the actual projected correlation cannot be disjoint from L1/L2 … if a
statistic exists that is both disjoint and actual, my argument is wrong."* **Tested, and the argument
is right — more strongly than they put it.**

**Construction.** Two independent PSD sources `C_a`, `C_b` with `max|corr(C_a) − corr(C_b)| = 0.562`,
a positive-weight **marginalisation** map (every source bin to exactly one destination cell — the
real 5D → `(E_avail, W)` structure), `n = 60 → m = 3`. I then optimised the **source diagonal only**
to drive `C_b`'s actual projected correlation onto `C_a`'s:

| | off-diagonal triple |
|---|---|
| target, from `C_a` at unit diagonal | `[ 0.20703538, −0.10239616, −0.14434288]` |
| achieved from `C_b`, diagonal alone | `[ 0.20703538, −0.10239616, −0.14434288]` |
| **residual** | **`9.322e-11`** |

with a **modest** rescale, `exp` range `[0.187, 4.133]` — not a pathological one.

**What that proves.** The actual projected correlation is a function of **both** the source
correlation and the source diagonal, and **neither determines it**. So any statistic that is (i) a
function of the actual projected correlation and (ii) invariant under `C → D C D` must return the
**same value** for source correlations differing by `0.562`. **It is not merely non-disjoint — it is
provably uninformative.** Disjointness and actuality are not a trade to be balanced; **they are
mutually exclusive, and the hybrid is forced.**

**Consequence for the packet:** §10's *"anyone wanting the actual object must give up §4.1's
invariance requirement and say so"* is exactly right, and should be read as a theorem, not a
preference.

## `L3` (PROBE, MINE) — attack line 2 CONFIRMED, and the reference can change the VERDICT

The statistic privileges `k = 0`. **Measured over 300 trials**, four members each, evaluating
`max_k ‖R_k − R_ref‖_max` under each possible choice of reference:

| | |
|---|---|
| trials where the value depends on the reference | **300 of 300** |
| worst ratio `max_ref / min_ref` | **`1.973`** |
| that trial's per-reference values | `0.19307 / 0.12627 / 0.09849 / 0.19431` |
| symmetric in a pair? | **No** — `0.249690` vs `0.258080` |

**So any `τ_p` strictly between `0.0985` and `0.1943` PASSES under one declared reference and FAILS
under another, on the same member set.** The reference is **load-bearing, not an implementation
detail.**

⚠ **This is a statement requirement, not a defect.** `k = 0` is the archive — a prospective,
non-gameable, already-declared choice — so the criterion is well posed. **What must be said is that
the reference is part of the criterion and that `τ_p` is reference-specific and does not transfer.**
And the statistic must not be read as *"how far do the members disagree among themselves"*, which is
reference-free and is a different quantity.

## `L4` (PAYLOAD, MEASURED BY ME) — attack line 3 ANSWERED: the precondition HOLDS on the real object

They are right that `x_cv > 0` is a predicate on the **central value** and does not establish that the
**variance** diagonal is positive, and right that they had not checked it. **I read the diagonal of
`hCov_combined5d_total_uthrow` from `z-cv.npz`** (matrix loaded, diagonal extracted, matrix
released):

| | |
|---|---|
| entries on the reported support | `10694` |
| `n ≤ 0` / `n < 0` / `n == 0` | **`0` / `0` / `0`** |
| all finite | **`True`** |
| min / max | `1.306681e-102` / `7.088712e-77` |

**So `corr(C_Z)` is well defined on the reported support and the statistic's precondition holds.**
Their caution was correct to raise and is now discharged by measurement rather than assumption.

⚠ **And the same read carries a second fact they should have, which is about sensitivity rather than
definedness.** The variance diagonal spans **`5.425e+25`** — about `12.5` orders in `σ`. So `D0`
spans `12.5` orders, and within each destination cell `M · renorm(C_k) · Mᵀ` is dominated entirely by
its highest-`σ` source bins. **The statistic is defined everywhere and sensitive only where the
variance lives:** a correlation change confined to low-`σ` bins is invisible to it. That is arguably
the correct weighting — those bins barely enter the published number — but **a PASS then means "no
correlation change among the dominant bins", not "no correlation change", and it must be stated that
way.**

**The other half of attack line 3 — `n_empty`, every destination cell receiving ≥1 source bin — is
map-dependent and cannot be checked until `P1` binds the maps.** Labelled, not closed.

## `L5` (PAYLOAD + SOURCE) — attack line 4: keep DEFINEDNESS and CONDITIONING apart

`λ_min = −1.2750516323643892e-90` with `λ_max = 2.229223998752954e-75`, which I read from
`z-receipt-cv.json` at `e393ad5e` and confirm. **But non-definiteness does not threaten the
statistic's definedness** — `L4` settles that independently, since `corr` needs a positive diagonal,
not a positive spectrum. **What `λ_min < 0` costs is the condition-number bound on the cancelling
channel**, which is already established and unchanged. **The two should not be conflated on the
artifact**, because a reader meeting "`C_Z` is not PSD" next to "`corr(C_Z)` is used" will infer a
definedness problem that does not exist.

## `L6` (PROBE, BOTH) — the `≈ 0.3 × sd` addition: the CONCLUSION holds, the CONSTANT does not

Their addition — the breach is bounded, so the refutation is fatal to disjointness and not to
diagnostic usefulness — **is right and I endorse it.** At `δ_bin ≈ 1e-3` the leak is `≈ 4e-4`, far
below any plausible `τ_p`, in **both** ensembles.

⚠ **But `"≈ 0.3× sd across three orders"` should not travel as a constant.** Their own probe's
per-sd column, which I ran, is `0.351 / 0.344 / 0.358 / 0.377 / 0.265 / 0.127` — it **breaks above
sd `0.2` and falls by nearly `3×` by sd `2.0`.** My independent ensemble gives `0.234 / 0.202 / 0.569`,
rising where theirs falls. **Across both, the ratio spans `0.13` to `0.57`.**

**This is their own §10.1 lesson applied to their own new claim**: a one-directional scan confirmed a
near-linear law cleanly, and the other axis — here the ensemble and the range — shows there is no
constant there. **Keep the bounded-leak conclusion; drop the coefficient**, exactly as the `≈ N ×`
framing was dropped.

## `L7` — §10.2's registry disposition STRENGTHENS my `C7`, and I adopt it

At `8df3b173` `C7` I called the est-seed disagreement a **record collision**. §10.2 is sharper and
correct: applied literally the rule rejects **every** throw component at **every** offset `k`
**including `k = 0`**, because the `42`-vs-`1000` difference is offset-invariant — so the rule
**rejects the very product the registry exists to describe and cannot be satisfied at any `k`.**
**That is unsatisfiable by construction**, the same class as the `1e-12` clamp, which is a stronger
statement than "collision" and I adopt it. The disposition — amend the rule on the estimator-seed
field, **do not unify the seeds**, record declared heterogeneity pending amendment — is consistent
with `sweep_bank_5d.py:354-357`, which I verified.

---

## One error of my own, caught before it became a finding

My probe also printed *"identical sets: False"* for `flatnonzero(support_mask)` against
`flatnonzero(diag > 0)`. **That is my own index-basis error, not a result:** the first is in **grid**
indices (`0…65855`) and the second in **row** indices (`0…10693`). Both counts are `10694` and the
sets coincide by construction through `hRowIndex5D`. **It is the support-index-versus-grid-index
confusion I flagged in another document a day ago**, committed by me in the probe that was checking
someone else's work. Recorded rather than deleted.

## What is required before the statistic is used

1. **Name the reference in the criterion** and state that `τ_p` is reference-specific (`L3`).
2. **State the hybrid on the artifact** — and, per `L2`, state it as forced rather than chosen.
3. **State the sensitivity concentration** (`L4`), so a PASS is not over-read.
4. `n_empty` stays open until `P1` binds the maps.

## What this assessment does not do

- Adopts nothing, sets no `τ_p`, grades no cell, and creates no boundary key.
- Does not design a further statistic. `L2` establishes that the alternative the author invited me to
  find **does not exist**, which is a closure rather than a gap.
- Ran no compute: read-only login-node payload reads and synthetic-matrix arithmetic here.
