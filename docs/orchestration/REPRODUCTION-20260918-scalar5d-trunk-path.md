# THE SUPPORTED REPRODUCTION PATH for the scalar-5D trunk

**Why this document exists.** Joseph's completion clause requires *"an explicitly adopted scalar-5D
covariance **with a supported reproduction path**."* A covering search found **no such document** —
the repository's seven `reproduc*` files are PET-scoped or generic, and the orchestration catalogue
had no entry. The ingredients existed scattered across a run log, a receipt, two assessments and a
predeclaration; **this assembles them and, more importantly, states what the path does and does not
establish.**

**CITABLE FOR:** the five ingredients in §1 and the measured reproduce/does-not-reproduce split in
§2. **NOT CITABLE FOR:** adoption, or any claim that reproducibility is established. **The trunk is
not adopted.** No compute was run to produce this.

---

## 1. The five ingredients

| # | Ingredient | Value |
|---|---|---|
| 1 | **Code identity** | Deployment `zdeploy-fb9ec356` at revision `fb9ec356`; the assembly closure is **fifteen modules**, read from the pilot's own `metadata_json` with measured import digests |
| 2 | **Inputs** | Eight consumed paths, digest-bound. `parent` declares `centering_convention = mean-centered`, `uthrow_source = unified_throw_cov_5d_fluxfix_20260806_full160.root`, `combined_source = uq_universe_5d_covariance_combined_bkgaware.root` |
| 3 | **Environment** | `Z_REPRO_KNOBS` — `deterministic=True`, `force_row_wise=True`, `num_threads=1`, the **estimator** parameter and not `OMP_NUM_THREADS`, which this repository has measured LightGBM to ignore |
| 4 | **Invocation** | `z_build.py` with its declared operands. Exit-code contract: **1** = construction failed, **2** = completed-non-passing, **0** only for `--help`. So `sacct`'s `FAILED` is not the verdict |
| 5 | **Resource envelope** | Job `58454524` on `nid004093`, `AllocCPUS 36`, `ElapsedRaw 1037 s` of a 5400 s wall (19.2%), `MaxRSS 49.73 GiB` of a 64 G request (77.7%) |

⚠ **Ingredient 3 is INCOMPLETE, and that is the load-bearing defect.** Measured **repo-wide**:
`OMP_DYNAMIC`, `OMP_SCHEDULE`, `OMP_PROC_BIND` and `OMP_PLACES` have **zero occurrences**, against a
positive control of 43 `OMP_NUM_THREADS` hits in `nd-unfolding/` alone. Every pin set proposed so far
pins **thread counts only**, and thread count is necessary but not sufficient for reduction-order
determinism. A reproduction path whose premise is *"the configuration is fixed"* cannot rest on
runtime defaults that appear nowhere in the tree and are captured in no receipt.

⚠ **Ingredient 2 carries a compatibility finding, not a defect.** The parent's `uthrow_source` is the
2026-08-06 ensemble while the pilot's throw input is the 2026-09-14 precursor — **two distinct
unified-throw ensembles in one chain.** Corroborated from the files' own scalars: the parent's
upstream null is `5.8223488501140625e-50` (G's) against the precursor's `1.4301832847122437e-50`. So
a reproduction attempt must name **which** ensemble it reproduces against.

---

## 2. What reproduces, and what does not — measured, not asserted

**Reproduces EXACTLY (`0.0`), from the pilot's own gates:** `G1_closure_identity` `max_rel_residual`
**0.0**; `G3_g_reconstruction` `max_rel_diff` **0.0**; `active_total_eq_sum5` **0.0**, so the five
active lateral blocks sum precisely to the declared active total.

**Reproduces EXACTLY on payload, independently:** production `hXSecND_flat` versus the persisted
vector, **65,856 of 65,856 identical, `max|Δ| = 0.000e+00`**; the support mask recomputed as
`production > 0` identical at 10,694; `flatnonzero(mask)` identical to `hRowIndex5D`. Measured by a
non-owning lane with read-only cluster access.

**Reproduces to 1.00 ULP:** `r_null = 4.45200021375829101e-14` in three independent summation orders
and **bitwise** against the blob-pinned instrument, against the build's `…9038e-14`. Three
reconstructions exist within 2 ULP and **none is bitwise** to each other.

⚠ **DOES NOT reproduce bitwise — and this is the open question, not a footnote.** The null pair
itself differs by `4.452e-14`, and `sbatch_uthrow_combine_5d_fast.sh:9` asserts *"`--null` repeats CV
at the identical seed and **must be zero**"*. The deviating pair is the **strictest case available**:
`z_statistics.py:87-89` records that the numerator compares *"two INTERNALLY re-unfolded CVs"* — one
process, one seed, one node.

⚠ **UNTESTED, not passing:** cross-process, cross-node and cross-allocation reproduction has **never
been run**. `B`'s predeclared estimator ranges over *n* arm-7 runs and **none exist**, so `B` is
**UNEVALUATED** — not refuted. Reporting an unevaluated arm as clean is a defect this campaign has
been corrected for.

---

## 3. So what does this path support, stated plainly

**It supports:** rebuilding the assembled covariance from digest-bound operands with a named code
revision, a named environment as far as the pin set goes, a named invocation, and a measured resource
envelope — with four internal identities reproducing exactly and the central vector reproducing
bitwise on payload.

**It does NOT support:** a claim of **bitwise** reproducibility, because the null pair is not bitwise
within a single process; nor a claim over any **envelope wider than one process**, because that has
never been tested; nor a **numerical-agreement** claim within a justified tolerance, because no
tolerance exists — every route to `ε` named in the contract is closed, and `SPEC:1410` forbids reading
one off Z's own null regardless of sample size.

**Therefore the required reproducibility property is BITWISE IDENTITY, and that is a consequence
rather than a preference:** the tolerance route is closed, so bitwise is the only route that does not
require an unobtainable number. That is the answer to Joseph's standing question about whether
numerical agreement or bitwise identity is required, and *why*.

---

## 4. What would complete it, in order

1. **Complete the pin set** — set or capture `OMP_DYNAMIC`, `OMP_SCHEDULE`, `OMP_PROC_BIND`,
   `OMP_PLACES`. **Code, not compute**, and `lane_b`'s to make. Without it, a negative repeat result
   is **ambiguous** between *"the design cannot be pinned"* and *"the design was never fully pinned."*
2. ~~**P0 — diagnose the `4.452e-14`.**~~ ⚠ **DONE, 2026-09-18, at zero compute — and it returned the
   UNFAVOURABLE branch. See §5.**
3. **P2 — the repeat. §5 says DO NOT BUY IT YET.** `78a8c2ee` §2.2's Model-A minimum: `n = 3`,
   **reservation bound 1.73 CPU task-h**; `n = 4` at **2.31** to make a single-run anomaly separable.
   `§2.3`'s receipt requirement is binding: **≥ 2 distinct node names, or item 2 is INCONCLUSIVE —
   not a pass.**
4. **Joseph's §6.4 route ruling**, and the `SPEC:3140` question of whether the control may run on Z's
   own bank. Neither is a lane's call.

**Nothing in §4 is requested here.** Step 2 is the cheapest decision-relevant item in the whole
package and it needs no allocation.


---

## 5. ⚠ P0 EXECUTED — the pair IS like-for-like, so the nondeterminism is real, and the guard that should have caught it CANNOT FIRE

Source only, zero compute, no payload read. Two findings, and the second explains why the first
survived into production.

**5.1 The two CV executions are LIKE-FOR-LIKE. Verified.** In `unified_throw_cov.py` — whose null
path `unified_throw_cov_5d.py:10` inherits *"unchanged"*:

    :846    base = x_cv[rep]
    :1011   x_cv2_full = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters,
                                           args.estimator_seed).ravel(order="C")
    :1017   x_cv2 = x_cv2_full[rep]
    :1018   null_norm = float(np.linalg.norm(x_cv2 - base))

**The second call passes the identical arguments** — same data, edges, truth and reco weights, `td_cv`,
`iters` and `estimator_seed` — to the same function, in the same process. There is no argument
difference for the deviation to come from.

**So the `4.452e-14` is genuine within-process nondeterminism of `_xsec_for_weights`, not an artifact
of comparing two different things.** The launcher's *"`--null` repeats CV at the identical seed and
must be zero"* is **not mis-stated — it is violated.** That is the unfavourable branch of the two P0
outcomes.

**5.2 ⚠ And the guard is the §3.1a defect, so it passes with ~10^38 of slack.** `:1019-1021`:

    tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)
    if null_norm > tol:  raise SystemExit("[FAIL] CV re-unfold is non-deterministic ...")

`max(…, 1.0)` clamps the tolerance to an **absolute `1e-12`**, while `null_norm` is the **absolute**
norm of the difference. `SPEC` §6.4 records this same vector's norm as order `1e-37`, so the absolute
deviation is about `4.45e-51` against a tolerance of `1e-12`:

    norm(base)=1e-37   tol=1.000e-12   |CV2-CV|=4.452e-51   fires? NO   slack 2.25e+38 x

**The check that exists precisely to refuse a non-deterministic re-unfold cannot fail on this
object.** This is the defect `SPEC` §3.1a names and §6.4 was written to replace — §6.4 measures it as
*"roughly `10^25` times the scale it is meant to bound"* for the general case; on the **null**
comparison it is about `10^38`. **That is why a violated assertion reached production unremarked: the
guard reported a pass.**

*(Incidentally, `SPEC:1193` cites this tolerance at `:517` and it now lives at `:1019`. Only one
occurrence exists, so it is the same construct moved, not two sites — `uq_math.py` warns in terms that
this file is prepend-ordered and *"every line-number citation into it decays (BEN-103)"*.)*

**5.3 THE DECISION THIS CHANGES: do not buy P2 yet.** The arm-7 repeat was priced at **1.73–2.31 CPU
task-h** to test determinism **across allocations**. But determinism **within a single process** is now
known to fail, and the design's own guard cannot detect it. Spending an allocation to test the wider
envelope while the narrower one is broken measures the wrong thing, and a *"not identical"* result
would be uninterpretable.

**The next step is smaller than P2 and is not a measurement of Z:** identify what inside
`_xsec_for_weights` is not deterministic at a fixed seed. `Z_REPRO_KNOBS` pins `deterministic`,
`force_row_wise` and `num_threads=1` for the estimator, and §1's finding stands — the **four OpenMP
variables are unpinned repo-wide**, which is the leading candidate and is a code change rather than
compute. **That ordering is now evidence-backed rather than precautionary.**

⚠ **What this does NOT establish:** that the deviation is *caused* by the unpinned OpenMP variables. I
have not run anything. It establishes that the pair is like-for-like, that the deviation is therefore
real, and that the guard cannot see it.
