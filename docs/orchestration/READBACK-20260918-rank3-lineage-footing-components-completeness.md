# READBACK 2026-09-18 — rank 3: lineage, footing, component compatibility, endpoint completeness

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Scope:** rank 3 of the designated audit
`ebba67ab6af17a159ae395cb06312b0dcbdca841:docs/literature/2026-09-18-scalar5d-covariance-inference-audit.md`,
row at `:74`. **Four parts, four verdicts.**

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the four part verdicts and findings `R1`–`R9`, with the measurements each rests on.

**NOT CITABLE FOR:** adoption, grading, projection production, or covariance adoption. No cell of Z
is graded. `ε` NOT adopted; `θ` closed and **not** a floor; `[B, S]` proposed, not governing
(`SPEC:1552`); `B` unestablished; full `S` OPEN. **No requirement to regenerate the campaign is
inferred or implied anywhere below.**

## THE THREE CATEGORIES, KEPT VISIBLY DISTINCT

- **SOURCE** — committed blobs read at a named sha.
- **PAYLOAD (MEASURED BY ME)** — cluster-resident ROOT/NPZ read by this lane on a login node with
  `uproot 5.6.9`. **Read-only: `uproot.open`, `find`, `stat`, `sha256sum`, `git hash-object`. No
  `sbatch`, no `srun`, no job attempt — `R5`'s accounting is untouched.** Writes only to `/tmp`.
- **NEW COMPUTATION** — named where a question needs it; none was performed.

**Nothing below is relayed.** Every product number is one I read myself.

## Verdict table

| part | verdict |
|---|---|
| **1 — lineage** | **TRACED, and the parent is NOT the object a reader would assume.** Two distinct unified-throw ensembles are in the chain, and the parent's `upstream_*` scalars describe the older one. **Disposition routed, not issued** (`R1`–`R4`) |
| **2 — footing** | **CLOSED, ELEMENTWISE AND BITWISE.** CV, support mask and row order all verified against the *production* object, not by digest — **and this performs the external CV cross-check that stood UNPERFORMED** (`R5`, `R6`) |
| **3 — component compatibility** | **ONE field verifiable and it PASSES; EIGHT are not payload-checkable at all** because the components carry no metadata. One measured disagreement on a declared fingerprint field (`R7`, `R8`) |
| **4 — endpoint completeness** | **TWO DIFFERENT PHENOMENA, WRONGLY POOLED.** The central product's above-one readings are **1–49 ULP** — rounding, not a defect. The endpoint readings are `11` orders larger and are **not** rounding. Neither is normalized into range (`R9`) |

---

# PART 1 — LINEAGE

## `R1` (PAYLOAD) — the parent names its own sources, and they are not the pilot's

The designated parent
`uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` carries three `TNamed`
lineage fields. **Read by me:**

| field | title |
|---|---|
| `centering_convention` | **`mean-centered`** |
| `uthrow_source` | **`unified_throw_cov_5d_fluxfix_20260806_full160.root`** |
| `combined_source` | **`uq_universe_5d_covariance_combined_bkgaware.root`** |

**The pilot's throw input is a different object.** `z-manifest.json` `/sources/throw/path` is
`uq_5d/z_precursor_20260914/unified_throw_cov_5d.root` — the **2026-09-14 precursor**. The parent's
`uthrow_source` is the **2026-08-06 `fluxfix_full160`** object. **So two distinct unified-throw
ensembles are in the chain**, and a digest on the parent binds the identity of the wrong-era one for
any question about the throw ensemble.

**Measured corroboration that they really are different objects**, from the two files' own scalars:

| scalar | parent's `upstream_*` | the precursor throw root's own |
|---|---|---|
| fixed-seed null norm | `5.8223488501140625e-50` | `1.4301832847122437e-50` |
| joint mean-shift norm | `1.878696733368378e-38` | `1.8786967332845478e-38` |
| `n_throws` | `160` | `160` |

The first pair are **different numbers** — the parent's is G's committed null, which this campaign has
quoted for weeks. The second pair **agree only to 10 significant figures** (relative `4.5e-11`), which
is far too coarse for the same computation and is the signature of two separate ensembles.

**Consequence, stated as a routing fact and not a grade:** any comparison of the pilot's null against
the parent's `upstream_fixed_seed_null_norm` compares two different objects. **`5.8223e-50` is not
this pilot's null and must not be read as its predecessor value.**

## `R2` (SOURCE + PAYLOAD) — the inflation difference is CORRECT, and it is the evidence that the pilot did not inherit the parent's covariance

**Measured:** the pilot's persisted `hInflation_g` and the parent's `hInflation_g` are **both length
`10694` and NOT elementwise identical — max `|Δ| = 2.329`.** On its face that looks like a defect.
**It is not.** `z_assembly.py:64` defines `compute_g(v_uni, v_blk)` and `z_build.py:587` stores the
**computed** `g`, so the pilot **recomputes** the inflation from its *own* operands rather than
reading the parent's.

**So the difference is the expected consequence of `R1`**: the parent's `g` was computed against the
2026-08-06 ensemble, the pilot's against the 2026-09-14 one. **This is the correct behaviour** and I
record it as a resolved anomaly rather than a finding, because a reader meeting the `2.329` alone
would reach the opposite conclusion.

## `R3` (SOURCE + PAYLOAD) — what the parent actually IS, which is narrower than "the parent"

Given `R2`, the parent supplies **no covariance and no inflation** to the pilot. Measured, its 13
keys are the footing fields, the two `sqrt_tr_*` scalars, the `upstream_*` copies, and
`hCov_combined5d_total_uthrow` / `hInflation_g` which the pilot does not consume. **Its operative
contribution is the `sqrt_tr_old` bar (`4.357790406860002e-38`, read by me) and the lineage names.**

**Whether a bar computed on the 2026-08-06 ensemble is the right bar for a 2026-09-14 one is a
scientific question, and it is not mine to answer.** I record that it is open and that nothing in the
pilot's records addresses it.

## `R4` (SOURCE + PAYLOAD) — the combined source is the NON-`_uthrow` file while the registry's adopted 5D covariance is the `_uthrow` one

`docs/ESTIMATOR_REGISTRY.md:29` names the `omnifold-5d-lgbm` covariance product as
**`uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root`**,
`√tr 5.8077e-38`, status **ADOPTED**. The parent's `combined_source` and the pilot's
`/sources/support/path` are both the **same directory's file WITHOUT the `_uthrow` suffix**.

**These are different files with different roles** — `mii_anchor_comparator.py:20-24` makes the
non-`_uthrow` file the sole ingredient of `sqrt_tr_old` — **so this is not an error on its face.** It
is exactly the audit's point in its sharpest available form: **a digest binds
`…_bkgaware.root`; the registry's adopted object is `…_bkgaware_uthrow.root`; and no digest can tell
you which one the science required.** Now that both names are on the record, the selection question
is answerable by a ruling rather than by a hash.

⚠ **And the trace scalars do not line up across the chain either:** the registry records the adopted
`√tr` as `5.8077e-38` (CV-centered variant `6.2367e-38`), while the parent's `sqrt_tr_new` is
**`5.269625166386846e-38`** (read by me). Three different eras, three different numbers. **Recorded;
no disposition offered.**

---

# PART 2 — FOOTING, VERIFIED ELEMENTWISE

## `R5` (PAYLOAD) — CLOSED. All three comparisons are bitwise identical against the production object

The audit asked for row order and mask verified **elementwise against the production objects, not by
digest comparison**. Done, with `uproot` against
`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`:

| comparison | result |
|---|---|
| production `hXSecND_flat` vs persisted `hXSecND_flat` (`65856` bins) | **ELEMENTWISE BITWISE IDENTICAL, 65856 of 65856**; `max|Δ| = 0.000e+00` |
| support mask recomputed as `production > 0` vs persisted `hSupportMask` | **ELEMENTWISE IDENTICAL**, `10694` each |
| `flatnonzero(persisted mask)` vs persisted `hRowIndex5D` | **ELEMENTWISE IDENTICAL**, strictly increasing |
| rows recomputed from the **production** vector vs persisted `hRowIndex5D` | **ELEMENTWISE IDENTICAL** |

**`component_footing`'s footing leg is therefore closed on evidence, not on a matching digest.**

## `R6` (PAYLOAD) — this also performs the external CV cross-check that stood UNPERFORMED

`z_assembly.py:493` sets `"stored_cv_cross_checked": diag_c_unified_cv is not None`, so the recorded
`false` means an operand was not supplied — a declared non-check, as the audit says at `:141-142`.
Separately, `SPEC` condition `11c` requires an external check against a production ROOT's
`hXSecND_flat` be reported as agreement **only where elementwise identity is established**.

**`R5`'s first row establishes exactly that identity, bitwise, over all `65856` bins.** So the
external CV cross-check moves from **UNPERFORMED** to **PERFORMED AND AGREEING**. ⚠ **It does not
make `G3R.stored_cv_cross_checked` true** — that flag records whether the producer was handed an
operand, and it was not. **The check is satisfied; the flag remains an accurate record that the
producer did not perform it.** Those are different statements and I keep them apart.

---

# PART 3 — COMPONENT COMPATIBILITY

## `R7` (SOURCE) — the criterion, which the registry already states

`docs/ESTIMATOR_REGISTRY.md:17-22`: *"every covariance component must carry the identical estimator
fingerprint as its central product (reject on mismatch). Fingerprint fields = {estimator ID,
backend+version, feature schema, preprocessing, iters, estimator seed, train_frac (ML band),
reported-bin mask/order, input NPZ/bank}."* **Nine fields.** That is `component_footing`'s
source-bound criterion and it does not need inventing.

## `R8` (PAYLOAD) — ONE field is checkable and passes; EIGHT are not checkable at all

**Measured key inventories:**

| component | file | payload metadata |
|---|---|---|
| central | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | 13 keys; scalars are **exactly** `dataPOT`, `globalCompleteness`, `ndim` |
| `C_stat` | `uq_cov_stat_5d.root`, 891.7 MB | **ONE key**: `hCov_stat5d_reported`, TH2D, `n = 10694`. **No scalars, no TNamed** |
| `C_ML` | `uq_cov_mlsplit_5d.root`, 892.1 MB | **ONE key**: `hCov_mlsplit5d_reported`, TH2D, `n = 10694`. **No scalars, no TNamed** |
| active | `std_final5_candidate.root`, 42.3 GB | 49 keys, all `hCov_retained5d_<band>` TH2D, `n = 10694` |
| parent | as Part 1 | 13 keys **including** the three lineage `TNamed` and eight scalars |
| throw | `z_precursor_20260914/unified_throw_cov_5d.root` | 157 keys, rich: `estimator_seed`, `draw_seed`, `est_seed_offset`, `n_throws`, `cv_code_revision`, `cv_producer_sha256`, `cv_bank_path`, `cv_bank_cv_sha256`, `n_band_donors = 124`, per-band donor names |

**Reported-bin dimension is uniform at `10694` across `C_stat`, `C_ML`, active, parent and throw, and
the reported-bin mask/order is closed by `R5`. That fingerprint field PASSES.**

**The other eight are not payload-checkable for the components that matter**, because
`C_stat` and `C_ML` carry **one histogram and nothing else** — no estimator ID, no backend or
version, no feature schema, no preprocessing, no iteration count, no seed, no `train_frac`, no input
bank. The central product carries three scalars and **none of them is a fingerprint field.** So a
"reject on mismatch" rule cannot be executed against the payload for five of the seven components.

**That is the substance of the rank-3 `component_footing` gap, and it is a WRITER gap, not a
verification gap.** It is closed by a writer change, not by reading harder. **No new computation is
required to identify it; a writer change would be Tier-2 work and is not mine to specify.**

⚠ **One measured disagreement on a declared fingerprint field, routed and not graded.** The registry
declares the 5D central at **`5 iter, est seed 42`** (`:29`). The throw component records
**`estimator_seed = 1000`, `draw_seed = 1000`, `est_seed_offset = 0`** (read by me). Under the
registry's own rule that is a fingerprint mismatch and the rule says *reject*. **But cause 3 is
literally "varying estimator seeds", so the difference may be the design rather than a defect.** I
state the measurement and the rule, and **the disposition is the owner's.**

---

# PART 4 — ENDPOINT COMPLETENESS

## `R9` (SOURCE + PAYLOAD) — the semantics, and then two phenomena that must not be pooled

**Semantics, from source.** `unfold_nd_omnifold_unbinned.py:1079-1085`:

```
of_in,    _ = histnd(tcols, tw, edges)          # tcols/tw: truth kinematics of sig["pass_truth"]
denom_nd, _ = histnd(dcols, td["w"], edges)     # td = collect_truth_denom_nd(t_td, ...)
completeness[nz] = of_in[nz] / denom_nd[nz]
c_global = of_in.sum() / denom_nd.sum()
```

- **numerator** `of_in` — truth-level histogram of events passing truth selection **in the signal
  tree**, weight `w_truth`.
- **denominator** `denom_nd` — truth-level histogram from the **separate `mc_truth_denom` tree**
  (`:277`, *"truth-only … for the completeness denom"*), weight `td["w"]`, both POT-scaled.
- **They are two different trees**, so `of_in ≤ denom_nd` is **not** guaranteed by construction, and
  a value above one is not a priori a defect. That is the disposition question.
- **`:1074-1076` — the closure branch sets `completeness = np.ones(...)` and `c_global = 1.0` literally**,
  so an exactly-1.0 reading has two possible origins and they must be told apart.

**Disposition (a) — the 5D central product: the above-one readings are ROUNDING. MEASURED BY ME:**

| | |
|---|---|
| `globalCompleteness` | **exactly `1.0`** |
| per-bin `n > 1` | **`2768`** of `10694` support bins (`25.9%`) |
| **max excess `(c − 1)`** | **`1.088e-14`** — i.e. **49 ULP** |
| **median excess** | **`2.220e-16`** — **exactly 1 ULP** |
| `n == 1.0` exactly | `5236`; `n < 1`: `2690`; off-support `c` is `0.0` everywhere (`55162`) |

**So the central product's "above one" is floating-point rounding and is NOT a defect.** And because
the scatter exists at all, the central product did **not** take the closure branch — it computed the
ratio and got `1 ± ULP` across the support.

⚠ **But that produces a larger finding, and it is not the one the audit was looking for.**
`of_in` and `denom_nd` are numerically equal to the last bit across essentially the whole reported
support, so **`completeness ≡ 1` and the completeness division in `extract_cross_section_nd` applies
no correction in 5D.** Whether that is intended — the 5D phase space defined so completeness is unity
— or indicates the denominator tree is filled from the same population as the numerator, is a
**scientific disposition I do not issue.** It is a bigger question than the one asked and it is now
on the record with its measurement.

**Disposition (b) — the ENDPOINT readings are a different phenomenon and are NOT rounding.**
`Z_BUILD_PACKET.md:160-162` records `EP_Muon_Energy_MINOS_0 = 1.001824`, `_1 = 1.000521`, the other
eight exactly `1.0`. Those excesses are `1.8e-3` and `5.2e-4` — **eleven orders of magnitude above
the central product's `1.088e-14`.** **Pooling them under one heading "`globalCompleteness > 1`"
compares two populations.** The endpoint excesses cannot be rounding and require the
numerator/denominator population disposition.

**And that disposition cannot be obtained from retained bytes. SOURCE:**
`mii_anchor_comparator.py:20` classifies `globalCompleteness` as `NEITHER … ingredients unwritten`,
and `:125-128` as **`NOT_RECOMPUTABLE, WRITER_GAP`** — *"`of_in.sum()/denom_nd.sum()`; NEITHER IS
WRITTEN, and `sweep_bank_5d.py` emits NO completeness histogram (0 occurrences of `hCompleteness`)
though `unfold_nd_omnifold_unbinned.py` has one. Writing either closes this."*

**VERDICT on part 4: UNRESOLVED for the endpoints, with its reason — the ingredients are unwritten,
so no read can settle it and the closure is a writer change.** Resolved for the central product:
rounding. **Nothing was normalized into range, and the eight exactly-`1.0` endpoint readings are NOT
cited as evidence of health**, because an exactly-1.0 value is also what the closure branch writes
and which branch produced them is unestablished.

---

## What is owed, by category

- **SOURCE, available now:** nothing outstanding in this scope.
- **PAYLOAD:** the endpoint products were not located under a bounded search of the 5D tree, so
  disposition (b) could not be attempted on their own bytes; and per `R9` it would not settle it
  anyway.
- **NEW COMPUTATION:** none is required to *report* any cell above. Closing `R8` and `R9(b)` needs
  **writer changes** — component fingerprint fields, and either completeness ingredient — which are
  Tier-2 code and belong to `lane_b`. **I specify neither, and I infer no requirement to regenerate
  anything.**

## What this readback does not do

- Adopts nothing, grades no cell, licenses no projection, and does not resolve rank 3 — it closes
  part 2 on evidence, resolves part 4(a), and hands parts 1, 3 and 4(b) back with dispositions named.
- Issues no scientific disposition on the seed mismatch, the two throw ensembles, the `_uthrow`
  selection, or the completeness definition. Each is the owner's.
- Ran no compute and no job. Read-only login-node access only.
