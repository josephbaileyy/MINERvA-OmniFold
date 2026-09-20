# OUTCOME 2026-09-20 — **(B) ASSESSABLE FAIL.** `s_proj` exceeds its bound; the diagonal legs do not

**CITABLE FOR:** the verdict, its operands and its scope.
**NOT CITABLE FOR:** an adoption. Gate 2 remains **FAIL**. **Recorded once. No retry, no re-seeding,
no reconfiguration** — Joseph's `(B)`: *"recorded once. No retries, re-seeding or reconfiguration to
change it."*

Grade receipt: [`state/GRADE-20260920-cause3-two-member.json`](state/GRADE-20260920-cause3-two-member.json),
`sha256 f272a7729006c6ec9dff74df8961161a78ac79f564e9c7b3bd37f5aae8769387`.

## 1. The verdict

```
scientific_acceptance : NON-PASSING
branch                : 5   NOT MET - PER-BIN
assessable            : True        reject_conditions: []
failing legs          : ['s_proj']
```

| leg | class | statistic | bound | verdict |
|---|---|---:|---:|---|
| `s_agg` | aggregate | **`0.00471447`** — 0.471% | `0.05` | within limit |
| `s_med` | per-bin | **`0.00485229`** — 0.485% | `0.05` | within limit |
| **`s_proj`** | per-bin | **`0.06145388`** — **6.145%** | `0.05` | **EXCEEDS** |

`r_null = 2.442032658261136e-13`, **within bound** against `ε = 1e-9` — measured in the graded
product's own production and bound to it by digest, recomputed `r_null` and mask equality.

## 2. ⚠ THE CAMPAIGN IS FULLY VALID. This is a measurement, not a footing failure

```
branch1_failures   : []
branch2_failures   : []
invalid_statistics : {}
```

**All nine `Validity` fields passed**, each re-measured by `z_grade` from the members' own bytes:
footing digests equal across members, product digests recomputed against their receipts, the band
partition identical, symmetry/PSD re-run and the `g`-domain conditions re-derived per member, the
reconstruction gate proved from each receipt's measured residual, `hXSecND_flat` byte-identical
across members, **offsets read back as exactly `{0, 1200}`**, **both members declared** and **three
distinct digests** — covariance, throw source re-hashed from disk, and manifest.

This is what the previous goal could not obtain at any price: a **gradable two-member campaign**.
It graded, and it graded against.

## 3. What the result means, and why the third leg is the one that caught it

**The two diagonal legs agree to about half a percent. The correlation-sensitive leg moves twelve
times further.**

`SPEC` §3.7d's finding was that `s_agg` and `s_med` are **blind to correlations** — `I₂` and
`[[1, 0.9], [0.9, 1]]` give identical trace and identical per-bin statistics, both legs returning
exactly `0.0`, while the sd of their sum and difference move by `+37.8%` and `−68.4%`. Joseph's
ruling (b) on 2026-09-18 **added `s_proj`** on the ground that *"projections are a required
deliverable, so (a) was never available."*

> **This campaign is the first measurement in which that ruling changed the answer.** On the two
> diagonal legs alone the result would have been **MET**. The leg that fails is the one that reads
> the off-diagonal structure — and the required deliverable **is** a projection, `M1`, `5D →
> (E_avail, W)`, whose rows are 42 of the 43 declared functionals.

Corroborating, and **grading nothing**: the per-bin movement distribution is **concentrated**, which
is precisely what a median hides. Median `2.66%`, p90 `9.46%`, **max `37.0%`** at grid index `7307`.
`s_med` sees `0.485%` because it is a median; `s_proj` sees `6.145%` because a projection sums over
bins and their correlations.

The worst functional is **index 2 of 43** — an `M1` destination row, **not** the all-ones total-rate
vector. So the failure localises to a specific `(E_avail, W)` destination cell rather than being a
uniform normalisation drift.

## 4. ⚠ THE DISCLOSED SCOPE LIMITATION CANNOT EXPLAIN THIS AWAY — it can only understate it

[`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`](EVIDENCE-20260919-lateral-bands-are-seed-pinned.md):
five of `C_Z`'s 45 bands are produced at a literal `--seed 42` that the offset hook cannot reach —
**26.0% of `√Tr`, 6.75% of the trace**. Those bands contribute **zero** movement by construction.

**So the measured `6.145%` is what 93.2% of the trace produces on its own.** Letting the remaining
bands vary could only add movement, not remove it. **The FAIL is robust to the limitation; a PASS
would not have been.**

## 5. What was spent

| | reserved | measured actual |
|---|---:|---:|
| CPU task-hours | `347.00` | **`68.17`** |
| GPU task-hours | `161.25` | **`53.75`** |

Against Joseph's `A1` cap of **600 CPU / 400 GPU**. R5 headroom after: `311.03` CPU / `424.92` GPU
of `500`/`500`, stop date not fired. **394 scheduler tasks, zero failures** — every arm ran inside
its cap, and `uthrow5d_block`'s observed maximum of **`3.54` h exceeded the packet's recommended
`3.00` h cap**, so raising it to `7.00` h is what kept the campaign alive.

## 6. What follows

- **No retry.** `(B)` forbids it, and there is nothing to retry: the campaign is valid and the
  measurement is what it is.
- **The exception route is the live one.** The fallback deliverables are complete —
  [`DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md`](DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md)
  is prepared to the point where only Joseph's act is missing, and it is built so a script cannot
  read it as an adoption until he makes that act.
- **Neither new product is adoptable, and neither has an exception available.** The §6.4 exception
  attaches to `3d7465f6…` and nothing else. `361090f9…` and `7e4636a3…` are graded, recorded, and
  **not** put forward.
- **The result is about `(cause 3, Z)`'s `M(ii)` and authorizes nothing else.** It does not regrade
  `M(i)`, which stays `UNRESOLVED` on reject condition `4c`.

## 7. The decision this leaves

`s_proj`'s bound is `cause3_corr = 0.05`, approved by Joseph on 2026-09-18 as *"a direct movement
bound, never quadrature"*, on the ground that a drift below the `~5.6%` precision the 160-throw
ensemble imposes is not resolvable. **The measurement is `6.145%` — above the bound, and of the same
order as that precision figure.** Whether that is a real sensitivity or a statement about the
ensemble's own resolution is a scientific question this lane does not answer and must not: the
bound was fixed before production, and the result is reported against it as written.

**Co-Authored-By: Claude Opus 5 (1M context)**
