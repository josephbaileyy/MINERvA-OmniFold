# DECLARATION IBUB: binned IBU's method bias at the two held-out tunes, beside OmniFold's, on COV2D's 600 toys (2026-11-23)

**By** `director-helper-3`, for the director's review, an agy read, then the director's binding. Nothing has run.

**Under:** the director's work order of 2026-11-23 to this session (Joseph via the director). It passes on Ben's request (a):
IBU's method bias at the two held-out GENIE v3 tunes, computed the same way as OmniFold's, so that the two methods can
be compared within their bias uncertainties.

**After:**
- [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md) §4 (the truths, the natures, the pseudo-data, the surrogates) and §6 (its
  bias readout). The verdict is in [`OUTCOME-20261108-cov2d-both-tunes-under-cover.md`](../../../OUTCOME-20261108-cov2d-both-tunes-under-cover.md).
- [`REF-C2C1-DECLARATION.md`](REF-C2C1-DECLARATION.md) §1.1, the frozen c2 estimator, and
  [`OUTCOME-20261106-ref-c2c1-read.md`](../../../OUTCOME-20261106-ref-c2c1-read.md). Its §3 says that no follow-up run
  is made unless a new declaration binds it. This is that declaration, for one new question.

**MEASURES:** once bound, IBU at K = 10 on the 600 toys. A readout then reads IBU's and OmniFold's per-toy errors
before the surrogates.

**CANNOT AUTHORIZE:**
- any job before the director's binding and GO;
- any change to E_R, Q_R, C_model, COV2D's verdicts or any reported number;
- any paper or note text.

**NOT CITABLE FOR:**
- any note or paper wording;
- any adoption: of IBU as a 2D estimator, of a bias correction, or of a covariance term;
- any coverage statement;
- any statement about either method's bias at the data, or at any truth other than these two tunes under COV2D's toy
  law.

Paths: `$O` = `/pscratch/sd/j/josephrb/cov2d-run-20261104` (COV2D's namespace, read only). `$N` =
`/pscratch/sd/j/josephrb/ibub-20261123` (this lane's new namespace). `R` = `fd/receipts-cov2d/` beside this file. Code
is cited at main `2f37c18a9` unless a sha is given.

## 1. The question, and what is fixed

- **The question.** At each tune T ∈ {G18, AR23}, what is the mean error of each method over COV2D's 300 toys, and are
  the two methods' mean errors distinguishable at this ensemble's noise?
- **The methods:**
  - **OmniFold** is E_R's production procedure, as COV2D ran it: one unfold per toy, at estimator seed 42, through the
    `--data-file` hook. Its 600 outputs already exist. This lane runs no OmniFold unfold.
  - **IBU** is REF-C2C1's c2 estimator, frozen there (§1.1), with nothing reselected. It is E_R's driver with the one
    OmniFold call replaced by binned D'Agostini IBU (RooUnfoldBayes) on the same arrays. It uses E_R's 14 × 16 grid,
    E_R's response and prior from the signal-MC rows, E_R's in-process Stay-Positive refinement of the toy's signed
    sample, and E_R's own extraction.
    - **K = 10 is the primary.** REF-C2C1's `config.json` sets `c2.iterations.primary` to 10.
    - K = 5 is reported beside it under the same readings, and is never chosen between.
    - The other K of the frozen scan (1, 2, 3, 4, 15, 20) are recorded per toy and read by nothing.
- **The toys** are COV2D's, unchanged: 300 per tune at seeds 5,720,000–5,720,299 (G18) and 5,730,000–5,730,299 (AR23)
  (`cov2d.TOY_SEEDS`), as `data_<seed>.root` in `$O/pseudo/G18/b/` and `$O/pseudo/AR23-a2/b/`.
  - Each file's sha256 is in step B's committed record: `R/pseudo/G18/pseudo_b.json` (sha256
    `230f6918…a54296`) and `R/pseudo/AR23/pseudo_b.json` (`d50ef13a…682bb5`). Both verdicts are PASS, with 301 files
    each.
  - The realization d̃_T (seed 5,721,000 / 5,731,000) is not a toy, and it is not read.
- **The graded truth** of toy t is COV2D's: `truth_xsec.npz` in the same `b/` directory, the row whose seed is t. It is
  pinned by the null records' inventory: G18 `8bf3f0c8…ba2cd7`, AR23 `b3895fbb…54dca1`
  (`R/readout/<T>/null_<T>.json`, `inventory.truth_xsec_npz`). It is method-independent (`cov2d_pseudo_write.py:282`):
  the nature's clipped composite truth through the driver's own extraction with the nature's flux.
- **The cells** are E_R's 205 reported cells (`hXSec2D > 0`), read with `re2c_rollup.Cells`. Both tunes' blocks
  records have the same `rep`.

## 2. Before the surrogates

The comparison is made **before** COV2D's post-unfold surrogates, as the work order directs.
- COV2D's error is taken after two surrogates (`cov2d_score.surrogate`, COV2D §4.2): the lateral term
  x̂ += Σ_b s_b Δ_b(T)/2, then the normalization x̂(1 + 0.014 z).
- Each term has zero mean over its own law (s_b = ±1 at ½ each; z ~ N(0, 1)). So it adds noise to a mean error and no
  bias. Over 300 draws its realized mean is not exactly zero; §6 prints it.
- The surrogate is applied after the unfold, the same way for any method, so it carries no information about the
  method. Applying it to IBU would also need IBU's own Δ_b(T), which means 20 IBU lateral unfolds. This lane does not
  run them.
- **So, per toy t and cell c:** e^m_tc = x̂^m_tc − x_true,tc, for m ∈ {OF, IBU}. Here x̂^OF is `hXSec2D` of
  `$O/out/T_<T>_<t>/xsec.root`, with no surrogate applied, and x̂^IBU is the IBU unit's `hXSec2D` at K = 10 (§3).

## 3. The IBU toy unit (code to come, §9)

- **A new module, `2d-unfolding/ibub/ibub_unit.py`, with its own `config.json` and tests.** It imports
  `2d-unfolding/ref_c2c1/ref_c2c1.py` and uses that file unchanged: `run_driver`, `roounfold_bayes`, `dagostini`,
  `xsec_at_every_k`, `own_hxsec`, the read guards and `copy_noatime`. No byte of `ref_c2c1.py` or its `config.json`
  changes.
- **Its units:**
  - `toy:<T>:<seed>`, one per toy. This is E_R's argv (`ref_c2c1/config.json` `e_r.argv`, which equals COV2D's toy argv
    `cov2d_jobs.argv("toy", …)` minus `--data-file`), plus `--data-file <the toy's staged copy>`.
  - `central`, once, with no `--data-file`. It is control C-REP (§5).
- **Like for like with COV2D's toys:**
  - 64 CPUs per unit, with OMP/MKL/OPENBLAS/NUMEXPR at 64/1/1/1. These are COV2D's toy lanes (`cov2d_jobs.pack`, 4 ×
    64) and REF-C2C1's c2 units.
  - The unit refuses any other affinity or thread environment, as `ref_c2c1.run_unit` does.
- **Per toy, before the driver opens anything:**
  1. The unit copies `data_<seed>.root` once, through `O_NOATIME`, into `$N/stage/data/`, under the staging root.
     `ref_c2c1`'s TFile guard lets the driver read only under that root.
  2. It requires the copy's sha256 to equal that seed's line in `pseudo_b.json`, or it refuses.
  3. It deletes the copy after the unit's products are written and hashed.
- **What it writes,** per unit, in `$N/units/`:
  - `<unit>.root`, the driver's own output;
  - `<unit>.npz`, holding `xsec` at every K of the scan, the unfolded vectors, T, y, and meta. The meta records the
    argv, the code and input digests, the data copy's sha256, the CPU count, the thread environment and the seconds;
  - a done-marker with its control verdict and both products' sha256.
- **The driver blob.** COV2D's toys and REF-C2C1's units ran `re2_driver.py` blob sha256 `938c53c5…8b5a3b`. Main
  now has `e226daf3…09971dd67`. The difference is COV2D-G2R's amendment 1 (`0f57c22a`, `62864b16`): 79 lines added
  and 2 changed. Every added line falls into one of these:
  - a line tagged `# G2R`;
  - a docstring or help-text line;
  - the body of the new function `g2r_miss_override`, which is called only when `--miss-map` is given. The flag
    defaults to off.

  The two changed lines add the keyword `miss_weight_override=None` and pass `**g2r_kw`, which is empty without the
  flag. Without the flag, the loader's production path is unchanged.
  - **Declared route (A):** the unit runs main's blob, pinned in its config by sha256. C-REP (§5) must then reproduce
    REF-C2C1's c2_central, which was produced with the old blob.
  - **Alternative (B), for the director:** vendor the `938c53c5` blob and run that instead.
  - §11 asks which to use.

## 4. The readings (fixed before any IBU output exists)

The readout runs on a login node at 0 node-h, per tune T, with n = 300 toys.

**Per cell c, and per band:**
- **Mean bias per method:** b̄^m_c = (1/n) Σ_t e^m_tc. It is reported in three ways:
  - absolute;
  - relative to the toys' mean truth x̄_true,c = (1/n) Σ_t x_true,tc, in %;
  - in σ_c = √diag(C_T), from the committed blocks record, for comparison with COV2D's own `readouts.bias`.
- **Its uncertainty:**
  - SE_boot(b̄^m_c), from a toy bootstrap: B = 10,000 resamples of the 300 toy indices with replacement, from
    `numpy.random.default_rng([5_760_000, k])` at tune index k (G18 0, AR23 1);
  - the analytic SE, sd(ddof 1)/√n, printed beside it.
- **The method difference:** d̄_c = b̄^IBU_c − b̄^OF_c = (1/n) Σ_t (x̂^IBU_tc − x̂^OF_tc). The truth cancels toy by toy,
  so the difference is paired.
  - Its SE is SE_boot(d̄_c), taken on the same resampled indices for both methods. The analytic paired SE is printed
    beside it.
  - z_c = d̄_c / SE_boot(d̄_c).
  - The unpaired form, |b̄^IBU − b̄^OF| / √(SE_IBU² + SE_OF²), which ignores the shared toys, is printed and read by
    nothing.
- **The bands** are area-weighted integrals over the reported cells, Σ_c x_c ΔpT_c Δp∥_c, using `Cells.area`. They are
  never bare sums. Their errors are e_t,band = Σ_{c ∈ band} A_c e_tc, with the same statistics as the cells. There are
  three families:
  - the 14 p_T bands (each p_T bin over its reported p∥ cells: 16, 16, 16, 16, 16, 16, 16, 16, 16, 15, 14, 13, 11,
    8);
  - the 16 p∥ bands (each p∥ bin over its reported p_T cells);
  - the total.

**The rule, per tune: "within their bias uncertainties".** It is one family of 205 + 14 + 16 + 1 = **236 tests** per
tune, each two-sided, Bonferroni at familywise α = 0.05: z* = Φ⁻¹(1 − 0.025/236) = **3.7044**.

| reading at T | condition |
|---|---|
| **DIFFER at T** | some test has \|z\| > z*. The report names every such cell and band, with d̄, its SE and the sign |
| **NOT RESOLVED APART at T** | no test has \|z\| > z*. The report prints the resolution beside it: per cell and band, the smallest difference this ensemble would resolve, z* · SE_boot(d̄), relative to x̄_true |
| **INVALID at T** | any §5 control fails for T. It is reported unrepaired, and no reading is made |

- **NOT RESOLVED APART is not "equal".** It says only that no difference is resolved at the printed resolution. No
  equivalence bound is declared, and the report never writes "the methods agree".
- **Per method, descriptively:** the cells and bands whose own |b̄^m| / SE_boot(b̄^m) exceeds z*, labelled "bias
  resolved" for that method. A summary per method and tune gives:
  - the RMS over cells of the relative bias;
  - the median |relative bias|;
  - the count of cells where |b̄^IBU| < |b̄^OF|.

  These are descriptive and decide nothing.
- **Descriptive joint statistic:** Hotelling's T² = n d̄ᵀ S⁻¹ d̄ on the 205 cells. S is the sample covariance (ddof 1) of
  the paired differences, and the reference is F(205, 95) after the usual scaling. It is printed with S's condition
  number and read by nothing, because S comes from 300 toys in 205 dimensions.
- **K = 5** gets the same table, reported beside K = 10 and never chosen between.
- **The two tunes** are read separately. With two truths there is no rate, as COV2D §1 says.

## 5. Controls (each must pass at T, or T reads INVALID, unrepaired)

- **C-OF, reproducing COV2D's committed errors.** From the stored OmniFold outputs and the recorded surrogate terms,
  the readout rebuilds COV2D's post-surrogate errors E with `cov2d_score.errors`, imported unchanged. Its inputs are:
  - x̂^OF, the 300 toys' `xsec.root`, each checked against its digest in `R/a2/bulk/completeness/completeness.tsv`
    (`401e9d97…8230ae`);
  - x_true, from the pinned `truth_xsec.npz`;
  - the natures' `lateral_signs` and `norm_z`, from `R/pseudo/<T>/pseudo_a.json` (`163cf1aa…f416` /
    `bdb7a57d…5994`);
  - Δ_b(T) and C_T, from `R/readout/<T>/blocks_<T>.npz` (`7eb657b8…0ea3d` / `abaebaea…15ee`).

  Then `cov2d_readouts.bias(E, σ)` and `spread_alone(...)["pull_mean"]` must equal the committed score record's
  `readouts.bias` and `readouts.spread_alone.pull_mean` to 1e-12 absolute (in σ_c units), cell by cell. The score
  records are `score_G18.json` `84976694…9088ec` and `score_AR23.json` `fe5263e9…4f5ce1`. This ties the
  pre-surrogate x̂^OF used here to the errors COV2D graded.
- **C-TRUTH:** the order checks of `cov2d_readout.phase_score`, carried over:
  - `truth_xsec.npz`'s seeds are `pseudo_a.json`'s natures in order;
  - the toys are `cov2d.TOY_SEEDS[T]` in order;
  - the 205 cells equal the blocks record's `rep`.
- **C-REP, the IBU unit against REF-C2C1.** The `central` unit, on the real data with no `--data-file`, must reproduce
  REF-C2C1's `c2_central.npz` (sha256 `929d0e78…43b76f4`, in `/pscratch/sd/j/josephrb/ref-c2c1-20261106/units/`, read
  through `O_NOATIME`). The bar is 1e-8 relative (RE-2's rule, as REF-C2C1's C-REF uses it), on the 205 cells, for
  `xsec` at every K of the scan, and for `y` and T. This covers the driver blob (§3, route A) and the new unit's wiring.
  - If the reference is gone or its digest differs, C-REP is UNAVAILABLE. The run stops before any toy unit, and the
    question goes to the director.
- **C-DATA, per toy unit:**
  - the staged copy's sha256 equals `pseudo_b.json`'s line for the seed before the driver opens it;
  - the driver's recorded `dataFileSha256` equals the same digest;
  - the output's argv equals the declared one.
- **C-FILL and C-ROO, per toy unit:** `ref_c2c1`'s C-FILL (the driver's own fill against the recorded extraction of
  IBU's unfolded vector, 1e-9). Also C-ROO: RooUnfoldBayes against `ref_c2c1.dagostini` on the same M, T and y at every
  K, 1e-9. In REF-C2C1, C-ROO ran on the central only. Here it runs on every unit, because it is numpy and cheap.
- **C-SIM, on the `central` unit**, as `ref_c2c1.c_sim`, 1e-9.
- **C-COMPLETE:** exactly 300 PASS done-markers per tune, one per declared seed, each from the bound job at the bound
  deploy, with its products' digests equal to the marker's.
  - A missing or failed unit is reported by seed. It is never silently dropped.
  - The readings need all 300. A tune with fewer reads INCOMPLETE, and is reported with no reading unless the
    director rules otherwise.
- **C-CELLS:** IBU's `hXSec2D` at K = 10 is finite on all 205 cells, in every toy. Any non-finite value is counted and
  reported, and T is INVALID.

## 6. Descriptive readouts (no reading)

- **The surrogates' realized mean.** Per cell, in σ_c: mean_t(post-surrogate e^OF) − mean_t(pre-surrogate e^OF). This
  shows what the surrogates would have added to OmniFold's mean.
- **The comparison with COV2D's flagged cells.** COV2D attributed its flags to bias: cell 29 at both tunes, and cell 56
  at AR23. Their b̄^OF, b̄^IBU and d̄ are printed by name. Nothing is graded on them.
- **Bootstrap against analytic SE:** the ratio's median and range over cells and bands.
- **The weakened cells.** COV2D's clipping-weakened lists (§5.2 there) mark the cells where clipping truncates the
  nature's spread. They are printed beside the per-cell table. Clipping acts on the truth and on the pseudo-data, which
  both methods share.

## 7. What IBUB can and cannot say

- **It can say:**
  - each method's mean error at each tune, over COV2D's toy law, with its toy-bootstrap uncertainty;
  - whether their difference is resolved at the stated resolution.
- **The mean error is conditional on COV2D's toy law.** That law draws the systematic natures (Flux, 2p2h and the 36
  pair bands, all un-centred, COV2D §6) and the Poisson data, but it does not resample the unfolding's simulation
  (COV2D §4.2, "known difference"). So:
  - b̄^m mixes the method's prior-dependence at T with the mean of its response to the drawn universes;
  - both methods see the same draws, and d̄ isolates the difference between the methods;
  - SE_boot covers the toys' noise only. It does not cover the statistics of the fixed response MC, which both methods
    share.
- **It cannot say:**
  - which method is correct, or that either is unbiased at the data;
  - anything about K other than 10 and 5;
  - anything about E_R's or Q_R's adequacy;
  - anything about COV2D's verdicts, which stand as recorded;
  - anything that would move IBU toward a reported estimator. REF-C2C1 §3's admissibility rule still holds.
- **Agreement between the methods does not validate either one,** and a difference does not show that either is wrong.
  This follows REF-C2C1's wording (`OUTCOME-20261106-ref-c2c1-read.md`).
- **Ben's (a), as asked, is answered by the §4 table per tune.** Any sentence for Ben, Joseph or the note is the
  director's to draft, from the committed record.

## 8. Price, I/O and retention

- **Unit time:** REF-C2C1 measured c2_central at 186.3 s and projected c2 replicas at 217 s, at 4 units per node
  (`receipts-ref-c2c1/step2/units-centrals/README.txt`). A toy unit is a central-shaped c2 unit with a different data
  file, so it is priced at 217 s, plus the data copy (one file, read once).
- **The job:** one exclusive CPU node, regular QOS, 4 lanes × 64 CPUs. The `central` unit runs first on lane 1. The
  600 toy units are dealt round-robin, 150 per lane. The longest lane is 151 × 217 = 32,767 s, plus a 300 s preflight.
  - The limit is ceil-to-the-minute of 1.25 × 33,067 s: **11:29:00**.
  - The charge is about **9.2 node-h**.
  - **The cap is 11.5 node-h** (1.25 × 9.2). Nothing reruns without the director.
- **The re-price trigger:** if the `central` unit's wall is above 1.25 × 217 s, the job's lanes stop before the toys,
  and the question goes to the director.
- **Staging (login node, 0 node-h, before the job):** `$CV` (`43f8cc16…`) and `$MC` (`d40aea69…`) are copied from
  their CFS originals (`ref_c2c1/config.json` `inputs.CV_source`, `MC_source`). `libRooUnfold.so` (`0b34e1e3…`) is
  copied from the shared checkout. Each copy:
  - is read once through `O_NOATIME` into `$N/stage/`;
  - is re-hashed against its pin;
  - is made read-only.

  The units read only these copies. After the readout, the copies and the per-unit data copies are deleted, with a
  B9-form ledger row.
- **Reads of COV2D's namespace** are through `O_NOATIME` only, and nothing is written there. `$O` has no HPSS copy.
  The reads are:
  - the job reads the 600 `data_<seed>.root`;
  - the readout reads the 600 OmniFold `out/T_*/xsec.root` and the two `truth_xsec.npz`.

  Every ROOT open is of a private copy, never of `$O` itself.
- **Nothing is written to CFS.** Products stay in `$N`. Results and receipts are committed in a records PR before they
  go to the director. That includes the per-tune JSON, the per-toy errors as an npz, and the job's logs and sacct.
- **The connect package** (step 5) includes:
  - a sacct-only fence that embeds cov2d's fence rev 3 (`7e81a721`), with `ibuchi_` on its name list;
  - an overlap check against the other lanes' protected sets;
  - the new job-name prefix **`ibub_`**;
  - fresh acks from cov2d, limitation-resolver and tier3-design.

## 9. Code (step 4, after this declaration's review)

- **`2d-unfolding/ibub/ibub_unit.py`** and its `config.json`: the units (§3). It pins every imported file by sha256:
  - the driver blob (§3);
  - `ref_c2c1.py`;
  - the OmniFold helper (`e9623412…`, which the driver imports);
  - `s5c_unfold.py` and `compare_to_paper_fullcov.py`, as `ref_c2c1`'s pins.
- **`2d-unfolding/ibub/ibub_readout.py`:** §4–§6, on a login node. It imports, unchanged:
  - `cov2d_score` (`errors`, `lateral_deltas`);
  - `cov2d_readouts` (`bias`, `spread_alone`);
  - `cov2d_readout` (`read_pinned`, `completeness`, `plan`, `inventory_paths`);
  - `re2c_rollup.Cells`.

  Every pscratch read goes through `O_NOATIME`, under `cov2d_blocks`' open audit, as COV2D's readout does.
- **Tests** cover both modules:
  - a fixture driver run of both unit kinds;
  - C-OF on a synthetic ensemble, with a perturbed surrogate that must fail it;
  - the bootstrap on a known case;
  - the rule's threshold;
  - each control's refusal.
- **Then** a line trace with a `main()` stub over every new line, hand mutants all killed, and an agy read. A
  codex-school2 read, if wanted, runs through cov2d.

## 10. Order

1. This declaration: its sha to the director, then an agy read, then revision and binding.
2. The code and its tests, trace, mutants and agy read; the shas to the director.
3. The connect package (§8); the shas to the director for binding and GO. The NERSC certificate expires
   2026-11-24T05:57:28Z, so the run may wait for Joseph's renewal. The reads are not rushed to beat it.
4. Staging, the job, then the readout on a login node.
5. A records PR holding the results and receipts, before they go to the director.

## 11. For the director

1. **The driver blob:** route (A), main's `e226daf3` with C-REP, or route (B), the vendored `938c53c5`? I recommend
   (A). The diff is inert without its flag, and C-REP tests that directly.
2. **"Per band":** I read it as kinematic bands (p_T, p∥ and the total, area-weighted), not COV2D's systematic bands.
   If systematic bands were meant, that changes §4.
3. **The rule:** one Bonferroni family of 236 two-sided tests per tune, with a paired bootstrap SE. Is that
   acceptable, or should the bands be a separate family?
4. **C-REP's reference** is on pscratch, with no HPSS copy. If it has been purged, does the run stop (as declared), or
   is C-REP replaced by an `er`-style check?
