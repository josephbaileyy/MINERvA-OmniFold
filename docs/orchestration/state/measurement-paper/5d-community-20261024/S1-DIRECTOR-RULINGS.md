# S1: the director's rulings, and the seed block (2026-10-25)

**By** the paper-tighten lane, as director.

**Under** [`S1-BINDING.md`](S1-BINDING.md) and [`S1-BINDING-AMENDMENT-1.md`](S1-BINDING-AMENDMENT-1.md).

**Rules on** [`S1-REPORT.md`](S1-REPORT.md), PR #348, merged at `d4bc7fbe`.

**Purpose:** to put into a committed record the rulings that the report cites "by correspondence", and to rule on
the seed block, which the report left open.

**MEASURES:** nothing.

**CANNOT AUTHORIZE:**
- compute;
- a claim, or printed wording;
- a publishability conclusion, which is Joseph's.

## 1. Rulings given by correspondence, now recorded

Each was given before or during the run, as the report states. None changes a declared choice, gate, cap or value.

1. **The `.pyc` files** (report §1). G1 and G2 wrote bytecode of the pinned sources into the first deploy. It was
   removed before production, and every later step used `-B`. **Accepted.** The pilot's products are unaffected:
   Python validates bytecode against its source's mtime and size, and G4 reproduced the central value bitwise.
2. **`-I -B` for `-I`** (report §§4–5). `-B` only stops bytecode writes. **Accepted** as within the declared `$PY`.
3. **The products' HPSS copy despite the STOP** (report §4). This is recorded in amendment 1 §2.2. The copy ran 89 s
   after the STOP, on the ruling given by correspondence. **Accepted as disclosed.**
4. **The module-resolution rule** (amendment 1 §4.2). Its intent was repo code. **The director's reading:**
   - "every non-standard-library module" in amendment 1 §4.2 means every module that is neither standard library
     nor installed in the declared interpreter's `site-packages`;
   - so numpy, from the `root_6_28` env, is outside it.
   - The session applied this reading before the run, and both repo modules resolved under the new deploy.
     **Accepted.**
   - Future module-resolution rules in this lane's bindings say "repo modules" explicitly.
5. **Ruling (B): the tracked npz** (report §5). The receipt-artifact check requires that every file a committed
   readout names be obtainable. So the 285 npz that `s1_assembly.json`'s `meta.inputs_sha256` names are tracked in
   the companion directory `s1/readout/s1_assembly/`, 27,179,746 B in all.
   - **Conditions:** explicit-path `git add -f`, unique basenames, and sha256 equal to the readout's value and to the
     pscratch source, with `SHA256SUMS` checked. All were met.
   - **Precedent:** the tracked 2D `production_cov.npz`, 16,877,824 B.
   - **This exceeds the declaration's §3.1 commit set, by this ruling.** Option (C), renaming the readout so that the
     check does not scan it, was refused.
6. **The scratch clone** `$B/tmp/fixcheck-fe5d79c6` and the reviewer's `/tmp` write (report §§1, 4). **Accepted as
   disclosed.** Neither touched an S1 input or product.

## 2. The seed block: ruling

**The finding** (report §7):
- All 80 seed-block products are bitwise equal to seed 42's at the same replicas, so C_seed = 0 in every cell.
- **D1:** the seed reaches every booster. `seed` and every seed derived from it differ between seeds, and nothing
  else does.
- **D2:** with one stochastic setting turned on, the fits respond to the seed. With the production settings they are
  bitwise invariant.
- **D3:** configuration (e) builds every fit's histogram bins from all rows (`s5c_unfold.py:57` at `d5617470`). It
  runs with bagging and feature subsampling off, and with `deterministic` and `force_row_wise` on. s5c P1
  (`state/s5c/p1/p1_summary.json` at `6fab459b`) had already isolated that setting on 5D:
  - with full binning only, seeds 42 and 43 differ by a median of 1.3 × 10⁻¹³;
  - with `deterministic` on, they are bitwise equal.
- **D4:** the code-byte differences between set A and S1 cannot touch the fit (read from code).

**Ruling:**
1. **The seed block's zero is a measurement, not a defect.** Configuration (e)'s estimator-seed main effect on these
   inputs is zero by construction.
   - C_seed = 0 is kept in C_e and C_total as computed.
   - The readout (`81e5ef3f…`) and the npz (`db000707…`) **stand**. Nothing is rerun.
2. **Choice 9 is discharged.** The declaration added the seed block to measure an effect that had never been
   measured for (e) in 5D. It is now measured, and found to be zero.
   - The 1.83 CPU node-h it cost bought that measurement.
   - The plan priced the seed block as an add-on; Joseph approved it as one. A zero result is a result.
3. **Where the estimator's numerical variation is carried.** Set A, the C_stat set, is refit-per-replica with jitter.
   The numerical component is absorbed there (declaration choice 6). The zero seed term therefore does not leave the
   estimator's numerical variation uncounted.
4. **The 2D precedent is unchanged.**
   - 2D's `a-refined-400-31` does not set `bin_construct_sample_cnt`. Its bin sample of 200,000 rows is drawn by
     seed, and its C08 is nonzero but small: per-bin median **0.048 %** for the refined estimator. That is `RE2-PARTC-REPORT.md:452`, whose values table carries no unit, and `docs/analysis-note/sec_results.tex:200` at `d4bc7fbe`, which prints it in percent.
   - `S1-REPORT.md` §7 D3 says that 0.057 is "now printed". That was true before the RE-2 integration merged (PR #343). Main now prints 0.048 % (`sec_results.tex:200`, `sec_systematics.tex:173`).
   - That this sample is *why* 2D's C08 is nonzero is an inference. It is consistent with D2, s5c P1 and
     `next-preparation-20261009/two-d-path/REPORT.md:133-141`, but no 2D full-binning run is recorded (D3's Search
     line). <!-- absence-ok: restates S1-REPORT.md §7 D3, whose Search line covers it -->
   - 2D's C08 measures its own estimator's seed dependence, and it stays as adopted.
5. **For the paper,** when Joseph takes up wording:
   - the 5D seed main effect is stated as measured and zero, with the reason: full-sample binning and deterministic
     training;
   - the 2D seed term is described as arising from the estimator's seed-dependent binning sample. That causal step
     is labelled an inference unless it is tested.
   - Any printed wording follows the PRD-style and agy review rule (DECISION-20261024, `-adopt-re2-2d-refined`).

## 3. Not changed

- **The readout, the covariance, the declaration and every gate.**
- **Claims, KI-85 and publication** are Joseph's.
- **No GPU.**
- **The S1 compute closes at 6.04167 CPU node-h, against the 15.5 cap.**
