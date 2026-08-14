# ISSUE-46 — `mat_gates` records a diagnostic it never gates, and infers a count it should be told

**File:** `nd-unfolding/p4_validate_active_lateral_fps.py`, function `mat_gates` (`:62-74`).
**Found:** 2026-08-14 by lane B while writing the `C_stat` assembly conventions (`OI-121`), from two
directions; both arms independently confirmed by the personal-account mediator the same turn.
**Severity:** MEDIUM. **Status:** OPEN. **Not fixed here — this file is not lane B's**, and the fix is
a threshold decision for its owner, not a mechanical edit.

**Why this is filed rather than only described.** Both arms existed until now only inside
`docs/orchestration/REQUIREMENTS-20260814-cstat-assembly-conventions.md` and in two cross-session
messages. That is `BEN-201`'s shape: a fact held only by live sessions disappears when they end. This
file is the durable home; `KNOWN_ISSUES.md` indexes it.

---

## Arm A — the PSD gate is a negativity test, so it passes a rank-deficient matrix silently

```python
67:    r["min_over_max_eig"] = float(ev[0] / max(1e-300, abs(ev[-1])))
68:    r["psd"] = bool(ev[0] >= -1e-12 * abs(ev[-1]))
```

`ev` is ascending from `eigvalsh`, so `ev[0]` is the minimum eigenvalue. An **exact zero satisfies
`0 >= -1e-12 * |λ_max|`**, so `psd` reads `True` for a matrix of any rank. This is correct as far as it
goes — the gate is asking *"are there negative eigenvalues?"*, and the relative tolerance is the right
form for that question, since an absolute one would be meaningless against a `~1e-76` covariance scale.

**The defect is that nothing else asks about rank**, and rank is the property that matters for a
component built from a finite ensemble. A `C_stat` from 50 replicas is rank ≤ 49 on ~262 reported bins;
`combine_cstat_bkgsub_100rep.py:90-93` states the reason as construction, not accident — *"`C = Z^T Z /
(n-1)` is a Gram matrix … full-space min eig = 0 by construction."* Such a matrix passes `psd` and
`diag_finite_nonneg` and reports a healthy `sqrt_trace`, and **no field in the receipt says how many
directions were actually estimated.**

**The evidence is already written; only the threshold is missing.** `min_over_max_eig` is recorded at
`:67` and is exactly the quantity a rank check would use. So the fix is additive and cheap: record a
**measured rank at a declared threshold** — the campaign's declared convention is a truncated-spectral
treatment retaining `λ > 1e-10 λ_max` (`docs/COLLABORATOR_QUESTIONS.md:36-42`, recorded at `:131-136`
as confirmed collaboration practice) — and let the consumer gate on it. **Do not tighten `psd`**; it is
answering its own question correctly. Add a sibling.

**Why it matters downstream and not just cosmetically.** `2d-unfolding/receipt_model_chi2_2d.py:32-35`
justifies `ndf = n_reported` by a rank-truncation scan and states the condition it relies on —
*"effective rank is not far below `n_reported`"* (rank 204/205). A validator that reports `psd: true`
and no rank is the instrument by which a covariance violating that condition reaches a χ²/ndf consumer
unflagged.

---

## Arm B — `n_reported` is inferred from the diagonal, and the inference can undercount

```python
72:    r["n_reported"] = int(np.sum(d > 0))
```

**`sum(diag > 0)` is not the reported-bin count.** A cell is *reported* when the central value's
acceptance is nonzero — the PET rule is `reported = comp > 0` at
`nd-unfolding/pet/extract_fullevent_fps.py:517-519`. A reported cell nonetheless has a **zero diagonal
entry** whenever the ensemble puts zero variance in it: all N members landing on the identical value.
For a 50-replica Poisson bootstrap that is unlikely per cell but not impossible, and it is **likeliest
exactly where the extended FPS grid is thinnest** — the catch bins `[4.5, 30]` in p_T and
`[0, 0.75, 1.5]` / `[60, 120]` in p_∥, which exist to hold sparse population
(`nd-unfolding/pet/fullevent_fps_dataloader.py:64-72`).

When it happens the count silently drops. The value is both **reported** in the receipt and **gated on**
at `:125`:

```python
125:    if out["active"]["sqrt_trace"] <= 0 or out["active"]["n_reported"] == 0:
```

which tests only `== 0`. So an undercount of a few cells passes every gate while a wrong `n_reported`
is published — and `n_reported` is the natural candidate for a χ²'s `ndf`.

**Fix:** take `n_reported` from the **shipped boolean reported mask** and require it, rather than
deriving it from the matrix. The mask is already the campaign's carrier for this
(`nd-unfolding/pet/assemble_ctotal_bkgsub.py:24-26,105-107` requires each component to ship
`reported_mask` and compares masks by exact `np.array_equal`). If the two disagree, that is a finding:
**a zero on a reported diagonal is a fact to report, not a cell to drop.**

---

## Shared root, stated once because it is the reusable part

Both arms are the same operation: **a validator that derives a property from the object under test
instead of being told it independently.** Arm A derives "is this acceptable?" from a spectrum without
being told what rank is required. Arm B derives "how many bins are reported?" from the matrix instead of
from the mask that defines it.

This is the family the repo has recorded three times already — `BEN-196` (a denominator computed by the
same broken parser it was guarding), `BEN-186` (a check fed input built by the code it re-derives with),
and `BEN-230` (a receipt whose numbers all re-derive being evidence of arithmetic, not of measurement).
**Ask what independent source the validator is comparing against.** Here, for both arms, the answer is
none.

## Related

- `docs/orchestration/REQUIREMENTS-20260814-cstat-assembly-conventions.md` §3, §3.1 — where both arms
  became requirements on `C_stat`: declare `n_reported` from the mask, declare `rank_at_1em10_lambda_max`.
- `BEN-189` — a *relative* eigenvalue metric on a rank-deficient object divides `~1e-18` by `~1e-18` and
  returns `~1.0` for any input. Bears on Arm A: `min_over_max_eig` is safe as a recorded ratio, but a
  comparison built on relative eigenvalue differences is not.
- `combine_cstat_bkgsub_100rep.py:20-22` — the sibling tolerance trap in the same subject area: an
  `atol=1e-8` default inherited into a problem whose natural scale is `~1e-80`.
