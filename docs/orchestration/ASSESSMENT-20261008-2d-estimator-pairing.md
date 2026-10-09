# ASSESSMENT 2026-10-08 — 2D estimator pairing and engineering (uncertainty preparation, lane A)

**CITABLE FOR:** which estimator produced each existing 2D central-value and uncertainty product, with
the evidence class of each identification; the frozen estimator contract in §2; the row outcomes in
`state/uncertainty-preparation-20261008/a/pairings.tsv`; the engineering checks in
`state/uncertainty-preparation-20261008/a/verification.md`. **NOT CITABLE FOR:** coverage, a
calibration verdict, a seed or backend transfer, any change to a quoted number, adoption, a new
estimator, compute, or publication scope. It grants nothing, reruns nothing and replaces no band.

Base `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c` (plan pin `ad2716d8` plus E's coordination commit),
branch `prep/uncertainty-a-pairing-20261008`. Plan: `PLAN-20261008-uncertainty-investigation-preparation.md`
(blob `fbbc0d65`), goal A. `P` = `docs/orchestration/state/uncertainty-preparation-20261008/`.

## 1. Decision

*Does each central-value/uncertainty pairing describe the same intended 2D estimator, and is an
engineering repair needed before a new statistical test is designed?*

The quoted 2D central value and the quoted 2D uncertainty come from **two different estimators**.
The central value (`3.073e-38 cm²/nucleon`, product sha256 `142a45b0…`) was produced by the
sklearn exact-split `GradientBoosting` backend with an unpinned `random_state`. Every uncertainty
block (statistical `VL170`, systematic universes, ML seed noise) was produced by the LightGBM backend
with pinned seeds: seed 1 for the statistical band, seed 42 for the systematic sweep and its matched
CV, seeds 1–10 for the ML scan. The two backends' central values differ by a median **1.3** (p84 2.8,
max 8.3) statistical-band σ per bin, and by a median **5.1** LightGBM seed σ, so the difference is not
LightGBM seed noise. Neither the exact backend's own seed variation nor whether the LightGBM
covariances describe the exact estimator's uncertainty has been measured. Section 2 states this as
the contract; §3 gives the row outcomes.

Within the LightGBM family the blocks are mutually consistent at every level that can be checked
from existing bytes: identical deterministic inputs, identical 205-bin masks and order, identical
normalization, and covariances that reproduce independently to ≤4e-16 (`P/a/verification.md` §3). The seed-1/seed-42
split is unmeasured at the covariance level.

## 2. Frozen estimator contract (for B and C)

This section is frozen at the `[uncprep-A] CONTRACT` commit. A later change appears only in A's
`FREEZE` commit, flagged as a change.

### 2.1 The four estimators that exist

| id | role | backend and seeds | input | settings | product (sha256) | evidence class |
|---|---|---|---|---|---|---|
| `E_C` | quoted central value | sklearn `GradientBoostingClassifier`/`Regressor`, library defaults (100 trees, depth 3, learning rate 0.1, subsample 1.0), `random_state=None` | `runEventLoopOmniFold_MEFHC.root` (CV omnifile) | `--iters 5 --use-weights`, background purity down-weight, no bootstrap | `2d_crossSection_omnifold_MEFHC_5iter.root` `142a45b0efc753d9…` | launcher + revision + wall-time signature; **executed-bytes origin unavailable** (job `53116554` log not found) |
| `E_S` | statistical band `VL170` (adopted) | LightGBM (`n_estimators 100, num_leaves 8, learning_rate 0.1`, other library defaults), `--seed 1` → step-1/step-2/regressor `random_state` 1/2/3 | CV omnifile | `--iters 5 --use-weights --bootstrap-seed b` (b = 1…300), streams `both`, purity, CPU | 300 replicas → `uq_covariance_boot300.root` (VL170) `71a75821ceeb6587…` | executed-bytes for the driver: the pilot log (`boot_1_59409026.out`, same launcher, regular lane) prints checkout HEAD `bb4b0b6f`, `GBDT estimator: lgbm`, `Pinned GBDT seeds: 1/2/3`, `streams=both`, `bkg-mode=purity`. The 300 replicas ran as array `59410433` (shared lane, 64 CPUs) under the same launcher, which exits 3 unless the checkout is clean at the expected HEAD; all 303 tasks COMPLETED (`state/ki84-rebuild-20261006/sacct_all.txt`). The per-replica log sweep is in `verification.md` |
| `E_U` | systematic universes + matched CV | LightGBM as `E_S`, `--seed 42` | `runEventLoopOmniFold_MEFHC_universes_full.root` (its CV-level histograms are bitwise those of the CV omnifile) | `--iters 5 --use-weights --universe BAND:IDX`, purity; matched CV omits `--universe` | 187 universes (44 bands) in `uq/universe_sweep_fluxfix/`; CV `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` `4f5a1b6d44b9e721…` | launcher + run log + product inputs; executed-bytes logs not located |
| `E_ML` | ML seed-noise block | LightGBM, `--seed 1…10` | CV omnifile | as `E_S` without bootstrap | `uq/seedscan_lgbm_ml/uq_covariance_ml.root` `3b6b48ec89207ae2…` | launcher + run log; recomputed from the 10 trial products to 3.3e-16 |

`E_S` imports `unbinned_unfolding/python/omnifold.py` through the driver's rooted `sys.path` insert,
so the helper came from the canonical checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold/`, not from
the frozen code checkout the launcher verified. The helper's bytes at run time were not recorded; its
runtime origin is **unavailable** beyond that path. The exact-split path of the helper is unchanged in
effect between `E_C`'s revision and today (`git diff d3239355 HEAD` only wraps it in a backend switch).

### 2.2 Output, binning, order and units (all four estimators)

- `hXSec2D`, `TH2D` 14 (p_T) × 16 (p_∥), edges exactly the paper's (`2D_OMNIFOLD_STUDY_STATUS.md`
  "Paper binning"); units cm² (GeV/c)⁻² nucleon⁻¹; total = Σ x · ΔpT · Δp∥.
- Reported set: **205 bins**. The five masks in use are identical bin for bin: `E_C > 0`,
  `E_U` CV `> 0`, the `VL170` replica mean `> 0`, the ML-scan mean `> 0`, and the paper's
  `StatOnlyCovariance` diagonal `> 0`.
- Covariance index order: row-major over (p_T bin, p_∥ bin), which equals the paper's
  `GlobalID = (Ptbin−1)·16 + (P∥bin−1)` restricted to the reported set. The consumer
  `compare_to_paper_fullcov.py` aligns covariances to the paper by ordinal position and checks only
  the count. Any new covariance must therefore be built over this identical set and order.
- Normalization is identical in `E_C`, `E_U`'s CV and the replicas: data POT `1.0574e21`, MC POT
  `4.9782e21`, nucleons `3.2352943e30` (geometry constant), flux integral `8.7407e-3 m⁻²/POT`,
  identical `hFlux_pt`.

### 2.3 The statistical band's sampling law (`E_S`)

- **Data stream.** One Poisson(1) factor per `data` row inside 0 ≤ p_T ≤ 4.5, 1.5 ≤ p_∥ ≤ 60
  (4,091,707 rows), from `np.random.default_rng(b)`, multiplied into the purity-weighted measured
  weights. The per-reco-bin purity `max(0, (D − B)/D)` is computed once from the observed data and is
  **not** recomputed per replica. The background MC (`mc_background`) is **not** resampled.
- **MC stream.** One Poisson(1) factor per `mc_signal_reco` row (32,849,103 rows, including the
  8,999,007 truth-only miss entries), from `np.random.default_rng(b + 10,000,000)`, applied to
  `w_truth` and `w_reco` of the same row. `mc_truth_denom` is not resampled.
- **Completeness.** Computed from the un-resampled MC truth weights, so each replica divides by the
  central value's completeness. Measured: max |c − 1| = 1.6e-14 over all 300 replicas and in `E_C`.
- The draws are positional over the tree rows in read order after the phase-space masks. Reproducing a
  replica requires the same input file and row order.
- **Band.** Per-bin mean and standard deviation (ddof 1) over the 300 replicas; `C_S` = sample
  covariance (ddof 1) about the replica mean on the 205 bins. √tr `C_S` = 1.9312e-40; median σ/mean
  0.674 %.
- Known conditioning consequences, recorded rather than repaired: fixed purity scales the data-stream
  σ by p per bin (median 0.975, `state/ki84-adopt-20261006/purity_datastream_check.json`).
  Background-MC statistics are absent from the band (driver comment at the deferred-subtraction
  block).

### 2.4 What a statistical validation can and cannot inherit from this contract

1. The adopted band is a property of `E_S`. A validation of the band must run `E_S`'s settings
   (LightGBM, `--seed 1`, purity, both streams, 5 iterations, `--use-weights`). The existing toy
   producer `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py` defaults to LightGBM with seed 1.
   It is one of the nine new `OI-136` rooted-insert sites (verification §3), so the executed helper's
   origin is not established by the launching tree.
2. **The quoted central is `E_C`.** Validating `E_S`'s band does not validate the uncertainty attached
   to the quoted central value. That needs either (a) a separately established `E_S`→`E_C` transfer
   with a declared observable and tolerance (pairing `P02`, unmeasured), or (b) a decision by Joseph to
   change the quoted central estimator, which this preparation cannot make. A design must name which
   one it assumes.
3. Seeds: `E_S` uses seed 1 and `E_U` seed 42. No covariance-level evidence relates them (`P04`). At
   the central-value level, the seed-42 CV and the seed-1 run differ by a median 0.30 σ_S (max 1.28).
   Re-running the same arguments reproduces a replica to ≤5.8e-9 relative (`VL170`).
4. The ML seed noise of `E_S` is small against its band: σ_ML/σ_S median 0.26 (p84 0.42, max 0.73).
5. A toy design that re-estimates purity per toy, or resamples background MC, tests a different
   conditional variance from the band's. State the difference rather than absorbing it.
6. Event identity keys and population roles are B's to establish. The driver carries no event
   identifier into its outputs.

## 3. Pairing outcomes

One row per pairing in `P/a/pairings.tsv` (23 columns: digests, command, population, masks,
normalization, completeness, backend, seeds, sampling law, covariance centre and denominator,
consumer, measurement, consequence, missing operand, price). The outcomes are mixed and are not
collapsed into one grade: **10 VERIFIED, 4 DISPROVED, 3 UNRESOLVED.**

| id | pairing | outcome | consequence |
|---|---|---|---|
| P01 | quoted central ↔ producing estimator | VERIFIED | `E_C` is exact GBT, unseeded. Executed-bytes origin unavailable. STATUS headline "lgbm" is wrong for this product |
| P02 | `E_C` ↔ statistical band: same estimator? | **DISPROVED** | the adopted band was computed for LightGBM seed 1 |
| P03 | statistical band applies to `E_C` | **UNRESOLVED** | no exact-backend bootstrap exists. Missing operand and price in the table |
| P04 | `E_C` ↔ systematic covariance: same estimator? | **DISPROVED** | the sweep and its CV are LightGBM seed 42 |
| P05 | systematic covariance applies to `E_C` | **UNRESOLVED** | the dominant block's transfer is assumed, not measured |
| P06 | universes ↔ matched CV | VERIFIED | internally matched. Background frozen at CV in all 87 non-Flux universes |
| P07 | seed-1 statistics ↔ seed-42 systematics summed | **UNRESOLVED** | consistent at the central level (median 0.30 σ_S). Covariance level unmeasured |
| P08 | ML block ↔ LightGBM family | VERIFIED | it is LightGBM seed noise |
| P09 | ML block as `E_C`'s ML uncertainty | **DISPROVED** | `E_C` sits 5.1 σ_ML (median) from the LightGBM seed mean. Its own seed noise is unmeasured |
| P10 | statistical covariance ↔ its 300 replicas | VERIFIED | reproduced to 4e-16; completeness 1.6e-14 |
| P11 | band centre ↔ `E_S` nominal | VERIFIED | 0.23 σ_S median offset |
| P12 | combined covariance ↔ paper bins | VERIFIED | five masks identical; ordinal alignment correct for these bytes |
| P13 | combined χ² ↔ operands | VERIFIED | 1.4716 / 1.4548 / 0.051 / 0.405 reproduced. Meaning inherits P03, P05 |
| P14 | 6.87 % budget ↔ denominator | VERIFIED | divides by CV42. With `E_C` as denominator it is 6.83 % |
| P15 | Fig. 6/7 ↔ operands | VERIFIED | reproduced. Divides by `E_C`, unlike P14 |
| P16 | normalization band ↔ central | VERIFIED | scaled by CV42; ≤0.17 pp effect |
| P17 | coverage evidence ↔ adopted band | **DISPROVED** | no coverage measurement of `VL170` exists (`VL169` graded `VL162`) |

**Labels resolved against producers, not by majority vote.** The backend has three labels in the
documents. STATUS "Headline (MEFHC 5-iter lgbm)" is wrong for the central product. STATUS "Phase
18.2 pipeline … exact GBT" and the frozen run log's "exact-GBT production" are right. "lgbm" is
correct for every uncertainty block. The reference's bootstrap item 4 (`--seed N`) contradicted every
producer, which all pass `--seed 1`. D's correction `00803510` is factually right
(`verification.md` §5).

**Historical filename, launcher text, executed bytes.** The central product was written as
`2d_crossSection_omnifold_MEHFC_5iter.root` by `sbatch_unfold_2d_MEHFC.sh` at `d1bc8813`. Both were
renamed `MEFHC` on 2026-05-28 (`c7ae2206`), and products made before that date record the flux file
as `runEventLoopMC_MEHFC.root`. Today's launcher text is therefore evidence of intent, not of the
command that ran. Only the VL170 replicas have executed-bytes evidence for the driver (HEAD-checked
launcher, logs). For the OmniFold helper, no product has it.

## 4. Engineering checks

Details, commands and exit codes: `P/a/verification.md` §1.

- **The repaired completeness path holds.** `test_bootstrap_completeness_ki84.py`: 8/8 at the base.
  The pre-fix negative control fails exactly the two expected tests (boot7 max |c−1| = 2.48 over 198
  bins, the recorded value), so those failures are old-code failures, not regressions. The
  production operands agree: all 300 replicas and `E_C` have max |c−1| = 1.6e-14, and replica 1's
  truth-denominator, input-truth, background and flux histograms are bitwise `E_C`'s. The test stubs
  the classifier, so it verifies extraction, not coverage.
- **One behavior fix** (`971fc00c`, driver + test, no structural change). Every output now records
  `runConfig` (all effective arguments, defaults included), `runArgv`, the driver's path and sha256,
  and the path and sha256 of the OmniFold helper module that was actually imported. This was the
  defect behind four "unavailable" runtime origins above: an omitted `--estimator` left no trace,
  and the rooted insert can load another checkout's helper. No histogram, weight or estimator
  changes. The pre-fix bit-identity tests pass, and deleting the write loop fails 5 of the 6 new
  tests. Existing products do not gain the records.
- **`OI-136`.** The driver's insert stays inside `main()` and `omnifold.py` keeps digest
  `e96234124a31…`. Both 2D-arm assertions pass. Both ratchet suites are **red at the base**: nine
  October 2D sites, one of them the coverage toy producer, are unlisted. Raised to E as an observed
  constraint with an owner (`verification.md` "For E", item 1). They are byte-identical after A's edit.
- **Shared callers.** k=0 separated roots 4/4, flux-universe 51/51, P4 resume closure 50/50, hash
  bindings 33/33 with `ALL BINDINGS INTACT`, full-event extractor 28/28. No Gate-2 pin was advanced
  and no receipt was edited.
- **No change** to `analyze_uq.py`, `analyze_universes.py` or `rollup_vl170_adoption.sh`. Their
  outputs reproduce independently, and the latent count-only mask alignment spans a file outside
  A's set. Proposed to E as a cross-owner design (`verification.md` "For E", item 4).

## 5. Consequences for B and C

1. **B must choose the estimator a statistical validation targets, and say so.** A validation scoped
   to `E_S` can rest on established pairings (P10, P11, contract §2). Its PASS would describe the
   LightGBM-seed-1 band, not the uncertainty attached to the quoted central value. Covering `E_C`
   needs P03 resolved first, or a decision by Joseph to change the quoted central estimator.
2. **Prices for C** (from `pairings.tsv`; node-h on Perlmutter CPU; nothing here authorizes them):
   - P03, exact-backend replicas: one exact unfold is 69,523 s wall, single-threaded, MaxRSS 16.8 GB.
     Packed by memory, N = 50 costs about 34–39 node-h and N = 300 about 205–215 node-h. Unpacked as
     originally run, it is 19.3 node-h per replica.
   - P05, exact-backend universes: about 128 node-h for all 187 plus CV (memory on the 119 GB omnifile
     unmeasured); a dominant-band subset is cheaper.
   - P07, seed transfer: LightGBM replicas at seed 42 cost 0.059 node-h each on shared (VL170
     measured): N = 100 is about 6 node-h and N = 300 about 18 node-h.
   - P09, exact seed noise: 10 exact unfolds, about 7 node-h packed.
   - Background-aware systematics: comparing the existing July sweep (`uq/purity_newomni/`) with
     `C_U` is a read-only reduction, 0 node-h.
3. **A component in no block.** The exact-vs-LightGBM difference (median 0.97 %, p84 2.7 %, max
   12.5 % per bin) is carried by no covariance. STATUS records it qualitatively as a "~1 χ²-unit
   GBDT-estimator regularization band". Whether it is an uncertainty, a bias or a choice is C's and
   then Joseph's question. This assessment only measures it.

## 6. Comparisons that remain unmeasured

Any covariance of `E_C` (statistical, systematic or ML); `E_C` at a pinned `random_state`; `C_S` at
seed 42 or `C_U` at seed 1; separability of `C_S` and `C_ML`; the product-level Flux rescale factor;
background-aware 2D systematics against `C_U`; a coverage test of `VL170`; the held-out-MC re-test
(deferred by Joseph, unregistered); the executed bytes of the central, systematic, matched-CV and ML
runs and of any historical OmniFold helper.

## 7. Terminal disposition

**FAIL**, by the plan's definition: pairings P02, P04 and P09 are disproved. The quoted central value
and its quoted uncertainty describe different estimators. P17, also disproved, restates the input
correction that `VL169` does not grade `VL170`. Mixed rows: 10 VERIFIED, 3 UNRESOLVED (P03, P05,
P07, each with a missing operand and a price). Engineering: the completeness repair and
its negative control pass. The provenance gap is fixed going forward. One necessary check is red and
outside A's paths: the `OI-136` ratchets, which include the coverage toy producer. Even a validation
scoped to `E_S` therefore has an engineering item open with its owner.

**Next decision (Joseph, routed by E):** which estimator a statistical validation targets. (a) `E_S`
only, stated as not covering the quoted central value: no new compute for pairing. (b) Resolve P03
with exact-backend replicas: about 34–39 node-h for N = 50, needing its own authorization. (c) Change
the quoted central estimator to the LightGBM family: a publication-scope and estimator decision,
with zero compute for the seed-1 central product (it exists, `seedscan_lgbm/…seed1.root`) but
re-derived comparisons and figures.

## 8. What this cannot authorize

No seed or backend transfer, no change to the frozen central estimator or to any quoted number, no
production rerun, no band replacement, no coverage or calibration claim, no compute, and no lifting
of the held-out-test deferral. A disproved pairing is a measured fact about existing products. It
does not show that the quoted uncertainty is numerically wrong for `E_C`, only that this has not been
measured.

## 9. Session record

Owner: lane A, a single session; the independent review is E's (`CAMPAIGN-REVIEW-20260929` §1). No
reviewer or worker agent was spawned. Model: Claude Opus 5.5 (`claude-opus-5-5`), reasoning-effort
setting 15 (harness). Session id `edb72d69-5a74-49f8-9124-1db2071391ec`. Base `f8e2bf85`; outputs
`acb338a2` (CONTRACT), `971fc00c` (behavior fix), and the FREEZE commit that carries this section.
Resources against A's row (6 h, 4 core-h, 8 GiB, 2 GiB): active time about 1.5 h by FREEZE; local CPU
well under 0.2 core-h (the largest single check, the hash-binding suite, took 83 s wall); peak RAM
under 1 GiB; scratch 34 MB of byte-copied products plus logs. The cited logs were copied to `P/a/logs/`, then the
scratch directory was deleted. Cluster: 0 node-h, 0 GPU-h, no training, no toys.
