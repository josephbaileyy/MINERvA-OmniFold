# IBU-1 report: binned iterative unfolding against OmniFold on the same pseudo-experiments (2026-10-23)

**By** the validation lane, for the director. This report records the result of the declaration
[`DECLARATION.md`](DECLARATION.md) as bound in [`BINDING.md`](BINDING.md), [`BINDING-C.md`](BINDING-C.md) and
[`BINDING-READER-FIX.md`](BINDING-READER-FIX.md). The rule was fixed before any result (DECLARATION §5) and was applied
unchanged.

**CITABLE FOR:**
- the IBU-1 verdict under the frozen rule, with each per-truth reading and the numbers behind it;
- the descriptive readouts the declaration lists without a rule;
- the run's compute, its products and controls, and the reader fix.

**NOT CITABLE FOR:**
- an OmniFold coverage claim beyond its committed receipts;
- a measured cross section, or IBU as an estimator for the paper;
- IBU's own coverage (IA-12) and the data ratios (IA-11) beyond description;
- any change to a claim. Claims are Joseph's.

All numbers come from [`receipts/ibu1_read.json`](receipts/ibu1_read.json), the reader's output, unless another source
is named. **(inference)** marks a reading beyond the rule.

## 1. Verdict: UNRESOLVED

The verdict is descriptive, for the methods paper. It authorizes nothing (DECLARATION.md:153).

At K = 5, on the primary variants (P `pur`, N `fold`; IA-5):

| deformed truth | per-truth reading | the set the ranges allow |
|---|---|---|
| tilt (`eavail_tilt` a = 0.2, KI 98's rate change; n = 400) | **unresolved** (mixed at the point values) | {consistent, mixed} |
| GiBUU (n = 60, paired with s5n) | **consistent** | {consistent} |
| W1 (n = 20, paired with (e)) | **consistent** | {consistent} |
| W2 (n = 20, paired with (e)) | **consistent** | {consistent} |
| W3 (n = 20, paired with (e)) | **consistent** | {consistent} |

**How the rule gives "unresolved"** (DECLARATION §5; `overall` in `nd-unfolding/ibu1/ibu1_read.py`):
- "Inverse-problem limited" needs every deformed truth's set to be {consistent}. Tilt's set also holds "mixed", so it
  is not decided.
- "Implementation specific" needs GiBUU's and tilt's sets to be {IBU better}. GiBUU's set is {consistent}, so it is
  excluded.
- "Consistent" is in every truth's set, so "inverse-problem limited" remains possible and the verdict is
  **unresolved**, not mixed.
- **(inference)** The verdicts the rule leaves open are inverse-problem limited (if tilt is consistent) and mixed (if
  tilt is mixed). Implementation specific is excluded by GiBUU whatever tilt does.

**Why tilt is unresolved.**
- Its residual reading is resolved: IBU's residual is 0.57 × OmniFold's, with interval [0.53, 0.81], inside the
  factor-2 band.
- At n = 400 the below-gate count also decides (IA-10).
  - IBU's count is 1, with interval [1, 80] (point 12).
  - OmniFold's is 35, with interval [35, 90] (point 52). `definite` is the Tier-S futility definition, here over the
    109 J functionals and either gate (IA-10).
  - At the point values that is "IBU better", which combined with the residual's "within" gives "mixed".
  - The four corners of the two intervals give better, within and worse, so the count is not resolved.

**(inference) What the verdict says in plain terms.**
- At the four generator-sized departures (GiBUU, W1–W3), exact binned IBU leaves the same median residual as
  OmniFold to within a factor 2. Its median residual is 0.77–1.31 × OmniFold's, every interval inside [0.75, 1.48].
  The maxima differ more: at W3 IBU's is 1.88 × OmniFold's, at W2 1.61 ×.
- That agrees with D-ID: the GBDT's median residual is about exact binned IBU's at K = 5
  (`docs/orchestration/state/next-preparation-20261009/d-id/REPORT.md:432-440`), and the label-stable J residuals
  sit in weakly identified functionals, branch C (`:514-519`). Here the agreement extends to pseudo-data noise and to
  arm N's template background, in its `fold` treatment (and in `sub`, secondary). The generator-sized departures
  exist only in arm N; arm P has only the rate change and nominal (DECLARATION.md:102-116).
- At the rate change the residuals agree to a factor 2. IBU has far fewer functionals that are definitely below the
  gate (1 against 35), but the intervals are too wide to call that a resolved difference.

## 2. Numbers at K = 5 (primary variants)

Residual = median over the 109 J functionals of |mean over seeds of f̂/f_true − 1|, raw (IA-4). Count = J functionals
below a coverage gate, as `definite` [`definite`, `possible`] with the point count (IA-10). The count is decisive only
at n = 400 and is descriptive below it.

| truth | n | residual, % IBU / OmniFold | ratio [95%] | residual | count IBU / OmniFold | count relation, corners | reading | max residual, % IBU / OmniFold | oracle floor, max |
|---|---:|---|---|---|---|---|---|---|---:|
| **tilt** | 400 | 0.082 / 0.143 | 0.571 [0.534, 0.810] | within | 1 [1, 80] pt 12 / 35 [35, 90] pt 52 | better; better, within, worse; decisive | unresolved (mixed) | 0.74 / 2.64 | 7.5e-07 |
| **GiBUU** | 60 | 7.300 / 9.508 | 0.768 [0.757, 0.805] | within | 98 [98, 109] pt 106 / 107 [107, 109] pt 109 | within; descriptive | consistent | 43.36 / 51.68 | 2.6e-04 |
| **W1** | 20 | 5.560 / 5.988 | 0.929 [0.875, 0.959] | within | 85 [85, 109] pt 107 / 106 [106, 109] pt 109 | within; descriptive | consistent | 21.39 / 23.71 | 7.7e-04 |
| **W2** | 20 | 0.733 / 0.560 | 1.309 [1.146, 1.473] | within | 30 [30, 109] pt 95 / 80 [80, 109] pt 109 | better; better, within; descriptive | consistent | 8.08 / 5.02 | 1.4e-04 |
| **W3** | 20 | 5.034 / 5.395 | 0.933 [0.861, 0.957] | within | 91 [91, 109] pt 109 / 108 [108, 109] pt 109 | within; descriptive | consistent | 63.08 / 33.57 | 1.4e-03 |

The oracle floor (IA-14) is the residual of the exact departed J totals through the same spreading and extraction. It
is at most 0.14% at every truth, far below the residuals. **(inference)** So the J-cell estimator's own floor does not
drive any reading.

**What the comparators are** (DECLARATION.md:31-38). At GiBUU and W1–W3 OmniFold's side is a small ensemble (60 and
20 experiments) with negative-weight background and uncorrected f̂ ± σ intervals. No OmniFold 400-seed ensemble
exists there, so at those truths the count is descriptive and the residual alone decides (IA-10).

**(inference) How firm the residual intervals are.** The paired seed-bootstrap percentile interval can exclude its own
point estimate. For the nominal_N reference it does so at K = 1 (0.251 against [0.256, 0.514]), K = 10 (1.027 against
[1.052, 2.192]) and K = 20 (1.471 against [1.555, 3.326]). At K = 5 tilt's point, 0.571, sits near the lower edge of
[0.534, 0.810]. The verdict does not depend on this: if tilt's residual set also held "better", "consistent" would
still be in every set and the verdict would stay unresolved.

## 3. Preconditions (IA-13): all pass

`preconditions` in `ibu1_read.json`:
- every paired experiment passed its comparator gate (`pairing_gates`);
- the three bootstraps passed their base gates (`bootstrap_gates`: P_sigma, N_sigma_s5n, N_sigma_R). Only P_sigma
  carries a control (`replica_capture`, passed); the other two have none, so their control check is empty;
- every truth used all 109 J rows (`J_rows_109`);
- the paired OmniFold estimates reproduce the committed receipts (`omnifold_receipts_reproduced`):
  - tilt and nominal hits equal `interim_400` exactly;
  - the s5n and R mean residuals agree to at most 1.7e-16.

## 4. Reported without a rule

- **References** (K = 5, primary; the same readout as §2, DECLARATION.md:156):

  | reference | n | residual, % IBU / OmniFold | ratio [95%] | residual | count IBU / OmniFold | count relation, corners | reading | max residual, % IBU / OmniFold | oracle floor, max |
  |---|---:|---|---|---|---|---|---|---|---:|
  | nominal, P | 400 | 0.050 / 0.053 | 0.939 [0.802, 1.474] | within | 1 [1, 93] pt 34 / 1 [1, 100] pt 12 | within; better, within, worse; decisive | unresolved (consistent at the point values) | 0.52 / 2.58 | 1.2e-17 |
  | nominal, N (s5n) | 60 | 0.071 / 0.094 | 0.763 [0.707, 1.469] | within | 1 [1, 109] pt 76 / 21 [21, 109] pt 72 | better; better, within, worse; descriptive | consistent | 0.68 / 1.00 | 2.6e-17 |
  | nominal, N (R = (e)) | 40 | 0.080 / 0.022 | **3.618 [2.617, 6.267]** | worse | 0 [0, 109] pt 66 / 0 [0, 109] pt 60 | within; better, within, worse; descriptive | **IBU worse** | 1.80 / 0.10 | 3.9e-17 |
  | GiBUU under (e) | 20 | 7.290 / 9.360 | 0.779 [0.752, 0.840] | within | 94 [94, 109] pt 106 / 105 [105, 109] pt 109 | within; within; descriptive | consistent | 43.60 / 51.72 | 6.0e-04 |

  - At nominal P the point counts are IBU 34 against OmniFold 12 (2.8×). The definite counts are equal (1 and 1), so
    the count's relation is "within"; its corners span better, within and worse (possible counts 93 and 100), so it
    does not resolve.
  - At nominal under (e), IBU's maximum residual is 1.80% against (e)'s 0.10%.
  - **(inference)** (e)'s nominal residual, about 0.02%, is smaller than IBU's. This is the nominal background repair
    the s5e diagnosis records (`docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md:45-48`). At
    generator-sized departures the two median residuals agree.
- **The K scan** (primary). Each cell gives the point word, the residual ratio and the set the ranges allow; the last
  column is the nominal-under-(e) reference's residual ratio. Everything else per K is in `ibu1_read.json`
  `primary.per_K`.

  | K | verdict | tilt | GiBUU | W1 | W2 | W3 | nominal under (e) |
  |---:|---|---|---|---|---|---|---:|
  | 1 | mixed | consistent, 0.546 {IBU better, consistent, mixed} | consistent, 1.423 | consistent, 1.223 | **IBU worse, 2.364** {IBU worse} | consistent, 1.350 | 1.52 |
  | 2 | unresolved | mixed, 0.532 {IBU better, consistent, mixed} | consistent, 0.906 | consistent, 1.040 | consistent, 1.247 | consistent, 1.052 | 2.41 |
  | 3 | unresolved | mixed, 0.556 {IBU better, consistent, mixed} | consistent, 0.840 | consistent, 0.970 | consistent, 1.156 | consistent, 1.028 | 2.91 |
  | 4 | unresolved | mixed, 0.656 {consistent, mixed} | consistent, 0.817 | consistent, 0.983 | consistent, 1.232 | consistent, 0.849 | 3.35 |
  | **5** | **unresolved** | mixed, 0.571 {consistent, mixed} | consistent, 0.768 | consistent, 0.929 | consistent, 1.309 | consistent, 0.933 | 3.62 |
  | 10 | unresolved | mixed, 1.087 {consistent, mixed} | consistent, 0.760 | consistent, 0.845 | consistent, 1.070 | consistent, 1.119 | 4.95 |
  | 20 | unresolved | mixed, 1.856 {IBU worse, consistent, mixed} | consistent, 0.587 | consistent, 0.932 | consistent, 1.261 | consistent, 1.340 | 7.48 |

  GiBUU, W1 and W3 have the set {consistent} at every K, and W2 at every K except K = 1.
  - K = 5 is primary and the only K the rule reads.
  - For K ≥ 2 every K gives the verdict unresolved. GiBUU and W1–W3 are consistent at every K ≥ 2.
  - At K = 1 W2 reads IBU worse, so the verdict there is mixed.
  - IBU's disadvantage at nominal under (e) grows with K, from 1.52× at K = 1 to 7.48× at K = 20.
- **Secondary variants at K = 5** (P `fold`, N `sub`): verdict unresolved. Each deformed truth has the same set as on
  the primary variants (tilt {consistent, mixed}; the others {consistent}):

  | | tilt | GiBUU | W1 | W2 | W3 | nominal P | nominal N (s5n) | nominal under (e) | GiBUU under (e) |
  |---|---|---|---|---|---|---|---|---|---|
  | residual ratio | 0.589 | 0.786 | 0.918 | 1.180 | 0.956 | 1.036 | 0.759 | **3.781** | 0.796 |
  | reading | unresolved (mixed) | consistent | consistent | consistent | consistent | unresolved (consistent) | consistent | **IBU worse** | consistent |

- **IBU's own amendment-4-corrected coverage at 400 seeds** (IA-12; σ from s5n's bootstrap, β from 300000–300059;
  no OmniFold comparator and no rule):

  | truth (arm N) | median J 68% coverage | median J 95% coverage | count below a gate, definite [definite, possible], point |
  |---|---:|---:|---|
  | nominal (300060–300459) | 0.653 | 0.935 | 3 [3, 104], 70 |
  | GiBUU | 0.000 | 0.000 | 103 [103, 109], 104 |
  | W1 | 0.000 | 0.000 | 99 [99, 109], 106 |
  | W2 | 0.505 | 0.848 | 65 [65, 107], 98 |
  | W3 | 0.000 | 0.000 | 100 [100, 109], 109 |

  - At GiBUU, W1 and W3 the median J functional is covered in none of the 400 experiments.
  - At nominal the medians, 0.653 and 0.935, are just below both gates (0.66 and 0.94).
  - These are IBU intervals with the amendment-4 correction at n = 400. OmniFold's intervals at these truths are
    uncorrected f̂ ± σ at n = 60 or 20 (IA-6), so the two are not the same construction and this table compares
    nothing with OmniFold.
- **Data at K = 5** (IA-11; per J cell):

  | | against | ratio median | range | median \|ratio − 1\| |
  |---|---|---:|---|---:|
  | IBU, arm P | (a) `hXSecND_flat` | 0.9994 | 0.802–1.340 | 4.58% |
  | IBU, arm N | (e) `data_b-_j-.npz` | 1.0034 | 0.801–1.368 | 4.75% |

## 5. The run

**Compute** ([`LEDGER.tsv`](LEDGER.tsv); charge = ElapsedRaw × billing/256/3600; full-step sacct in
[`receipts/sacct.txt`](receipts/sacct.txt)):

| job | QOS | state | elapsed, s | CPU node-h |
|---|---|---|---:|---:|
| 60130813 A (smoke) | debug | COMPLETED | 248 | 0.0689 |
| 60130899 B1 | regular | TIMEOUT at its 0:19 limit ([`LEDGER-NOTES.md`](LEDGER-NOTES.md)) | 1155 | 0.3208 |
| 60130900 B2 | regular | cancelled while pending | 0 | 0 |
| 60140294 K-B1 (control) | debug | COMPLETED | 70 | 0.0194 |
| 60140287 C | regular | COMPLETED 0:0, all 124 sacct rows; 39.4 min against its 1:26 limit | 2362 | 0.6561 |
| **total** | | | | **1.0652** |

The total is within BINDING-C's worst case of 1.82, the declared worst case of 3.5 and the 10 granted. Every job ran
on account m3246, under 12 h, never on premium.

**Products.**
- Location: `/pscratch/sd/j/josephrb/ibu1-20261022/run/products/`, 2,934 files.
- Checksums: [`receipts/SHA256SUMS`](receipts/SHA256SUMS), sha256 `0e45d41c4a0d0970e5c8fef90a79cf41b2faefc7430985f95c9bc0dcbb4d789d`.
- The local copy that was read verifies 2,934/2,934.
- Both data comparators match their config pins: (a) `630306e2…` and (e) `fb5cc679…`.
- Every declared unit is complete, so no unit is INCOMPLETE.
- The launcher refuses a dirty tree or a different HEAD (DECLARATION §6). After C the deploy was still at
  `7ea30e3d` and clean, and no `.partial` file remains ([`receipts/deploy_state.txt`](receipts/deploy_state.txt),
  read 2026-10-23).

**Products by the job that wrote them** (BINDING-C ruling 2):

| unit | A | B1 | C |
|---|---:|---:|---:|
| P_d1 | 9 | | |
| D_P, D_N | 1 + 1 | | |
| P_nominal, P_tilt | | 400 + 400 | |
| N_nominal_dev | | 60 | |
| N_nominal_val | | 192 | 208 |
| N_gibuu | | 22 | 378 |
| N_sigma_R | | 1 | |
| N_gibuu_R, N_nominal_R | | | 20 + 40 |
| N_w1, N_w2, N_w3 | | | 400 each |
| P_sigma, N_sigma_s5n | | | 1 + 1 |
| **total** | **11** | **1,075** | **1,848** |

**Meta checks** ([`receipts/ibu1_metacheck.py`](receipts/ibu1_metacheck.py), output
[`receipts/metacheck.json`](receipts/metacheck.json)): **PASS, 2,934/2,934.**
- The script uses the bound code's own `unit_seeds` and `comparator_path`, imported from the deploy, not retyped.
- **Per product:**
  - the schema; the unit; the arm;
  - the seed is declared, equal to `pseudo_seed`, with the declared split key;
  - truth, amplitude and ratio as configured;
  - the comparator is present exactly where declared, and passes.
  - For bootstraps: the seed, split key and replica range, a row per replica, the base gate and the controls.
- **Per writing job**, since code and input digests are checked at process start and refuse before any write
  (`ibu1.py:68-69`, `:546-561`):
  - no `refusing` line in any task log;
  - every OI-136 guard line at `outside_expect_root=0`: 3 lines in A, 41 in B1, 121 in C. So every module loaded
    from the pinned deploy.
- **Attribution:** each product's (unit, seed) is printed by exactly one job's task log. Data units are attributed by
  their task log's guard line, since `run_data` prints none.
- **Tested in both directions** ([`receipts/metacheck_mutation_tests.sh`](receipts/metacheck_mutation_tests.sh),
  output [`receipts/metacheck_mutation_tests.txt`](receipts/metacheck_mutation_tests.txt)):
  it passes a baseline of real products and fails each of five mutations: a wrong truth, an unattributed product, a
  product claimed by two jobs, a refusal line, and a guard line outside the root.

**Gates.** All 1,049 experiment comparator gates pass:

| unit | gates |
|---|---:|
| P_nominal | 400 |
| P_tilt | 400 |
| N_gibuu | 60 |
| N_nominal_dev | 60 |
| N_nominal_R | 40 |
| N_gibuu_R | 20 |
| N_w1, N_w2, N_w3 | 20 each |
| P_d1 | 9 |

The three bootstrap base gates also pass, and so does P_sigma's `replica_capture` control.

**Control K-B1** (BINDING-C ruling 2; launcher, comparator and result in [`receipts/kb1/`](receipts/kb1/)).
- **Reading fixed with the director before any result.** It is recorded only in the cross-session exchange, not in a
  committed director record. The director's message, verbatim, received 2026-10-22 19:00:32 PDT:
  > Director: your K-B1 reading is accepted, with two tightenings fixed now, before any result: (1) the set of array
  > names and the set of meta keys must be identical in both files (no extra or missing key passes); (2) the only
  > meta keys exempt are exactly seconds_build and seconds_ibu — any other differing meta field fails. Arrays:
  > np.array_equal plus identical dtype and shape, as you said. Choosing the last two products B1 wrote is a good
  > choice. Record this reading in the report as fixed before the result.
- **Timeline** (PDT). From sacct and cluster mtimes:
  - K-B1 (60140294) started at 19:00:25, 7 s before the director's message;
  - the comparator implementing the reading was in place at 19:01:07;
  - K-B1 wrote its two products at 19:01:24 and 19:01:27.

  From this lane's session transcript only, with no committed timestamped record: the comparison was first run at
  about 22:30 (2026-10-23T05:30Z). The job itself contains no comparison step (`receipts/kb1/sbatch_kb1.sh`). So the
  reading was fixed before the products existed and before any comparison. BINDING-C says "compared bitwise"; the files themselves are
  not byte-identical, because each records its own timings. The reading's terms:
  - the array names and the meta keys must be the same sets in both files;
  - every array must match in dtype, shape, bytes and `np.array_equal`;
  - every meta field must be equal, except exactly `seconds_build` and `seconds_ibu`, which must be present in both.
- **What was recomputed:** the last-written kept product of each partial line, `N_nominal_val` seed 300285 and
  `N_gibuu` seed 301100. (By mtime 300285 is B1's last product overall; 301100 ties at one-second resolution with
  300260 and 300435.) The bound code at the same deploy recomputed them in `kb1/`.
- **Result: PASS for both.**
  - All six arrays are identical (`F_fold`, `F_sub`, `f_oracle`, `f_true`, `f_true_A`, `ks`), and `differing_meta`
    is empty.
  - Only the timings differ: 24.6 s against 8.6 s build and 8.4 s against 1.6 s IBU for 300285; 31.0 s against
    10.3 s and 14.9 s against 3.0 s for 301100.
  - So no B1 product is voided.

## 6. The reader fix (BINDING-READER-FIX.md)

**The defect.**
- The frozen reader raised `ValueError` at `:76` in `load_unit` on the real products, reached from the IA-12 loop at
  `:293` ([`receipts/read_frozen_reader.stderr.txt`](receipts/read_frozen_reader.stderr.txt)). That was before any output:
  stdout was empty and no output file was written, so no result was seen.
- The IA-12 loop loads all 400 seeds of N_gibuu and N_w1–w3. Only 60 or 20 of those carry `f_of`, so `np.array`
  received a mix of arrays and `None`.
- The end-to-end test missed it because its fixture gave every unit's seed range a comparator, which the real config
  does not.

**Hashes.**

| file | frozen (DECLARATION §4) | fixed (this PR) |
|---|---|---|
| `nd-unfolding/ibu1/ibu1_read.py` | `2214d4877d0351fa3a4d3b6fb4c37f191d4b029eda82b4630ba1ab18fbfe6b48` | `620cad5c9445d36a5e4d22f0fc635c60603cade13de1f24452fca17e2aceb03a` |
| `nd-unfolding/ibu1/test_ibu1.py` | `1af9889230c2ebf4ae3221510d02de845adf56bd622266cdfbd0e594d6ca0c49` | `d06eb6c453bb496a73be2cafaad0fc605c9b81ffc22bae17e648438353b95f9e` |

**What changed.**
- Condition 1: `load_unit` returns `"of": None` when any row lacks `f_of`. It also records the unit's name, which the
  assertion uses.
- Condition 2: the paired path calls `require_of(unit)` at each former use of `u["of"]`: the residual in `evaluate`,
  and the mean residual and hits in `of_receipt_controls`. It raises `AssertionError("unit <name>: a paired product
  has no f_of …")`.
- Condition 3, tests:
  - `EndToEnd` builds its synthetic products once (`setUpClass`).
  - N_gibuu and N_w1–w3 now straddle the end of their paired range, with 5 seeds and comparators on 2, as in
    `config.json`. The fake receipts are sized to n = 2.
  - `test_units_then_read` asserts deformed n = 2, IBU-own n = 5, and `of` = `None` for a mixed unit.
  - The new `test_paired_load_missing_f_of_is_explicit` removes `f_of` from one paired product. It expects the
    assertion, naming `N_w1`, from `evaluate` and from `of_receipt_controls`.

**Full diff of the reader** (verbatim `git diff`; the reader and test diff together is
[`receipts/reader-fix.diff`](receipts/reader-fix.diff), sha256 `4f9df2e6…`):

```diff
diff --git a/nd-unfolding/ibu1/ibu1_read.py b/nd-unfolding/ibu1/ibu1_read.py
index 1de27c7d..a3cbc373 100644
--- a/nd-unfolding/ibu1/ibu1_read.py
+++ b/nd-unfolding/ibu1/ibu1_read.py
@@ -71,13 +71,21 @@ def load_unit(outdir: Path, name: str, variant: str, seeds: list[int] | None = N
     if not rows:
         raise SystemExit(f"no products for unit {name}")
     ks = rows[0][4]
-    return {"seeds": [r[0]["pseudo_seed"] for r in rows], "F": np.array([r[1] for r in rows]),
+    return {"unit": name, "seeds": [r[0]["pseudo_seed"] for r in rows], "F": np.array([r[1] for r in rows]),
             "t": np.array([r[2] for r in rows]),
-            "of": None if rows[0][3] is None else np.array([r[3] for r in rows]),
+            "of": None if any(r[3] is None for r in rows) else np.array([r[3] for r in rows]),
             "gates": [r[0]["comparator"] for r in rows], "ks": [int(k) for k in ks],
             "oracle": np.array([r[5] for r in rows]), "t_A": np.array([r[6] for r in rows])}
 
 
+def require_of(unit: dict) -> np.ndarray:
+    """The paired OmniFold estimates; a paired comparison without them fails here, naming the unit (reader fix,
+    BINDING-READER-FIX.md condition 2)."""
+    if unit["of"] is None:
+        raise AssertionError(f"unit {unit['unit']}: a paired product has no f_of (OmniFold comparator estimate)")
+    return unit["of"]
+
+
 def load_boot(outdir: Path, name: str, variant: str) -> dict:
     z = np.load(outdir / f"{name}.npz", allow_pickle=True)
     return {"F": z[f"F_{variant}"], "meta": json.loads(str(z["meta"])), "ks": [int(k) for k in z["ks"]]}
@@ -231,10 +239,10 @@ def of_hits(src: tuple, receipts: dict, names: list[str], n: int) -> np.ndarray:
 def of_receipt_controls(src: tuple, receipts: dict, unit: dict, k5: int, corr_of=None) -> dict:
     """The paired OmniFold estimates in our products reproduce the committed receipt (population check)."""
     kind, key = src
-    relO = unit["of"] / unit["t"] - 1.0
+    relO = require_of(unit) / unit["t"] - 1.0
     if kind == "interim":
         sig = np.asarray(receipts["interim"]["sigma"], float)
-        h = hits(unit["of"], unit["t"], sig, corr_of)
+        h = hits(require_of(unit), unit["t"], sig, corr_of)
         g = next(x for x in receipts["interim"]["grid"] if x["truth"] == key)
         return {"hits_equal_receipt": bool(np.array_equal(h, np.array([g["hits68"], g["hits95"]])))}
     p = (receipts["s5n"]["grid"][key] if kind == "s5n" else receipts["R"]["points"][key])["per_functional"]
@@ -270,7 +278,7 @@ def evaluate(outdir: Path, receipts: dict, names: list[str], variant: dict, k_li
                 hO = of_hits(spec["of"], receipts, names, n)
                 rows = J[np.all(t[:, J] != 0, axis=0)]  # IA-4: the 109 supported cells all have truth (checked)
                 cI, cO = count_interval(hI, n, rows), count_interval(hO, n, rows)
-                relI, relO = est / t - 1.0, u["of"] / t - 1.0
+                relI, relO = est / t - 1.0, require_of(u) / t - 1.0
                 res = residual_reading(relI, relO, rows)
                 cnt = count_reading(cI, cO)
                 floor = (u["oracle"] / u["t_A"] - 1.0)[:, rows].mean(0)
```


**Tests, in both directions** (`pytest -v`; full output with both files' sha256 on its first lines):

| reader | straddling fixture | missing `f_of` | suite | receipt |
|---|---|---|---|---|
| frozen `2214d487…` | FAILED, the real run's `ValueError` | FAILED, `TypeError` | 2 failed, 34 passed | [`tests_frozen_reader.txt`](receipts/tests_frozen_reader.txt) |
| `:76` fix only `2cc0d8ba…` | passed | FAILED, `TypeError` | 1 failed, 35 passed | [`tests_line76_only.txt`](receipts/tests_line76_only.txt) |
| fixed `620cad5c…` | passed | passed | **36 passed** | [`tests_fixed_reader.txt`](receipts/tests_fixed_reader.txt) |

The middle row shows that condition 2 is needed: with the `:76` change alone, a missing comparator reaches `relO` as
a `TypeError`.

**Statement.**
- No rule, threshold, unit, seed or comparator changed.
- `DEFORMED`, `REFERENCE`, `IBU_OWN`, `GATES`, `Z`, `FAMILY_ALPHA`, `FACTOR`, `SMALL`, `COUNT_DECISIVE_N`, `BOOT` and
  `BOOT_SEED`, and every reading function, are byte-identical to the frozen reader. The diff above is the whole change.
- Every value the rule reads comes from the paired loads, where every row has `f_of` (`metacheck.json`
  `f_of_present` on every gated product). So the fix cannot change any of them.
- **The read.**
  - It was rerun once, from the pinned products (SHA256SUMS `0e45d41c…`), with the fixed reader. It ran on the report
    branch, where everything the reader imports is unchanged since `7ea30e3d`; only `nd-unfolding/re1/` differs.
  - It exited 0 with empty stderr.
  - Output: [`receipts/ibu1_read.json`](receipts/ibu1_read.json), sha256 `40599d24…`.
  - No further reader defect appeared.

## 7. Evidence in this directory

- [`receipts/ibu1_read.json`](receipts/ibu1_read.json): the reader's full output.
- [`receipts/k5_tables.npz`](receipts/k5_tables.npz) (7.2 MB, sha256 `5eae8897…`), with its producer
  [`receipts/consolidate_k5.py`](receipts/consolidate_k5.py):
  - the rule's float64 operands at K = 5, per unit;
  - for experiments: seeds, the primary-variant F, `f_true`, and `f_of` with its seeds;
  - for bootstraps: the primary-variant F per replica; for data units: the primary-variant F.
  - The secondary variants and oracle arrays stay in the pinned products, which keeps the file under the declared
    10 MiB. They are summarized in the read output.
  - Spot checks against the products are bitwise equal.
- [`receipts/SHA256SUMS`](receipts/SHA256SUMS), [`receipts/sacct.txt`](receipts/sacct.txt), and
  [`receipts/inventory/`](receipts/inventory/): 124 OI-136 guard inventory files of A, B1 and C, holding 165 records
  (3 + 41 + 121).
- [`receipts/deploy_state.txt`](receipts/deploy_state.txt), [`receipts/metacheck_mutation_tests.txt`](receipts/metacheck_mutation_tests.txt),
  [`receipts/read_frozen_reader.stderr.txt`](receipts/read_frozen_reader.stderr.txt) and
  [`receipts/reader-fix.diff`](receipts/reader-fix.diff).
- [`receipts/ibu1_metacheck.py`](receipts/ibu1_metacheck.py) (sha256 `7dba1812…`) and
  [`receipts/metacheck.json`](receipts/metacheck.json). The committed version records each product's full cluster path
  and the run directories, so the repository's receipt checker sees them as cluster products. Its check results are
  unchanged from the version first run (2,934/2,934; A 11, B1 1,075, C 1,848).
- [`receipts/kb1/`](receipts/kb1/): K-B1's launcher, comparator, result, logs and inventories.
- The three test receipts of §6.

## 8. Independent review (DECLARATION §7 step 4)

**Reviewer.** A fresh, read-only Claude subagent (Opus 5.5), the same model family as the author, so the review is
not cross-provider independent. It was given the sources and the draft, and no briefing beyond them.

**Verdict: ACCEPT WITH CORRECTIONS.** It found nothing BLOCKING.
- It re-derived the verdict and every K = 5 per-truth reading from `ibu1_read.json` under §5 and IA-10, and agreed
  with them.
- It reran the fixed reader from the pinned products: output byte-identical to `ibu1_read.json`, exit 0, empty
  stderr.
- It checked every number in §1–§5 against its source, recomputed four residual medians from the raw products, and
  verified every hash.
- It confirmed the reader diff stays within BINDING-READER-FIX, and that the three test receipts support §6's table.

**Second pass.** The same reviewer then checked each disposition at its new lines: **CORRECTIONS VERIFIED**, with five
further MINOR points from the edits, all fixed:
- the reason nominal P's count does not resolve;
- the reason the optional test was declined;
- the K-B1 timeline, which now separates sacct and mtimes from the transcript-only 22:30 and adds the job's 19:00:25
  start;
- a contradiction inside LEDGER-NOTES about N_sigma_R's guard record;
- this section's description of the reviewer's brief.

The reviewer verified the cluster mtimes itself, read-only over ssh. It could not verify the director's message time
or the 22:30 comparison time, which have no committed timestamped record.

**Its findings, and what was done** (5 MAJOR, 11 MINOR; none changes the verdict):

| # | finding | disposition |
|---|---|---|
| 1 | MAJOR: the declaration's "authorizes nothing", §8's full list, and the comparators' small-ensemble caveat (`:31-38`) were missing | added: §1, §2 "What the comparators are", §10, and NOT CITABLE FOR |
| 2 | MAJOR: the references lacked "the same readout" (`:156`), hiding awkward numbers (nominal P point count 34 against 12; nominal (e) max 1.80% against 0.10%) | §4 now gives the full readout, with those numbers stated |
| 3 | MAJOR: "both background constructions" overstated; the generator-sized departures are arm N only | rewritten in §1 |
| 4 | MAJOR: the IA-12 inference compared unlike constructions and named a verdict the rule did not return | the label is removed, the construction difference stated, and the nominal medians below both gates noted |
| 5 | MAJOR: the K-B1 reading had no committed record | §5 now quotes the director's message verbatim, says it is not a committed record, and gives the mtime timeline; it states the files are not byte-identical |
| 6 | MINOR: "consistent at every K" is false at K = 1 (W2) | scoped to K ≥ 2 |
| 7 | MINOR: the K scan omitted the reading sets and the nominal-(e) trend | added |
| 8 | MINOR: the percentile interval can exclude its point estimate | added as an (inference) caveat in §2, with why the verdict survives |
| 9 | MINOR: three wording points in §1–§2 | fixed |
| 10 | MINOR: two bootstraps have no control, so "controls pass" was vacuous for them | stated in §3 |
| 11 | MINOR: the "full diff" was abridged | replaced with verbatim `git diff`; reader plus test diff committed as `receipts/reader-fix.diff` |
| 12 | MINOR: three claims had no receipt (deploy state, meta-check mutation tests, frozen crash) | receipts committed and cited |
| 13 | MINOR: "last two products B1 wrote", and the inventory count | rephrased; 124 files, 165 records |
| 14 | MINOR: LEDGER-NOTES' step counts (41/20) disagree with sacct (40/21) | noted in §9; a dated correction note added to LEDGER-NOTES |
| 15 | MINOR: the D-ID branch-C citation | `:514-519` added |
| 16 | MINOR: smaller omissions (the `f_of` evidence, secondary references, IA-12 point counts) | added. Its optional extra test (a missing `f_of` in a non-first paired row) was declined as optional: the fix tests `any(...)` over all rows, and the straddling fixture already mixes rows with and without `f_of` inside one unit |

## 9. Incidents

- **B1's time-out and B2's cancellation** are recorded in [`LEDGER-NOTES.md`](LEDGER-NOTES.md) and bound in
  BINDING-C. One correction to it, from `receipts/sacct.txt`: B1 had 40 steps COMPLETED and 21 CANCELLED, not 41
  and 20. The three bootstraps' steps were all cancelled, N_sigma_R's (`.2`) included, though it had already written
  its product. A dated correction note is added there.
- **Stash incident** (recorded in BINDING-READER-FIX).
  - While testing the reader fix, a `git stash push` with a wrong pathspec stashed nothing. The `git stash pop` that
    followed applied the repository-wide `stash@{0}` (someone else's) into this lane's detached read worktree, with a
    conflict.
  - The file was restored to HEAD in that worktree.
  - The director confirmed both stash entries intact and the shared checkout unchanged.
  - Since then, files are swapped by copying, never by stash.

## 10. Not done here

From DECLARATION §8 (`:200-204`), carried unchanged:
- total (statistical plus systematic) coverage; nuisance settings away from nominal;
- the q3-conditional point, a recorded construction defect;
- OmniFold at 400 seeds for GiBUU and W1–W3: no such products exist, and producing them is not IBU-1's scope;
- unbinned or prior-free IBU variants, other truth grids (T2/T3), and other K than the scan;
- any statement about real data beyond the descriptive ratios of IA-11.

Also not done:
- Resolving tilt. That would need more seeds or another rule, which the declaration does not provide; any such step
  is the director's or Joseph's to propose.
