# DECLARATION IBUB: binned IBU's method bias at the two held-out tunes, beside OmniFold's, on COV2D's 600 toys (2026-11-23)

**By** `director-helper-3`, for the director's binding. Nothing has run.

**Revision 3.**
- Revision 1 (`0e7449c1`) went to the director, whose rulings are in §11.
- Revision 2 applied those rulings and went to an agy read.
- This revision applies every finding of that read (§12).

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
  the nature's clipped composite truth through the driver's own extraction with the nature's flux. Its `xsec` holds
  each nature on the full 14 × 16 grid. The 205 cells are taken with E_R's `rep`, as `cov2d_readout.phase_score`
  does.
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
  For K = 5, x̂^IBU is the unit's `xsec` row at K = 5 from `<unit>.npz`, on the full grid, masked with the same `rep`.
  The driver writes `hXSec2D` only at the primary K. The readout asserts that the npz row at K = 10, masked the same
  way, equals `Cells.vec` of `<unit>.root` to 1e-9, C-FILL's tolerance.

## 3. The IBU toy unit (code to come, §9)

- **A new module, `2d-unfolding/ibub/ibub_unit.py`, with its own `config.json` and tests.** It imports
  `2d-unfolding/ref_c2c1/ref_c2c1.py` and uses that file unchanged: `run_driver`, `roounfold_bayes`, `dagostini`,
  `xsec_at_every_k`, `own_hxsec`, the read guards and `copy_noatime`. No byte of `ref_c2c1.py` or its `config.json`
  changes.
  - `ref_c2c1`'s own `parse_units`, `resolve_argv`, `run_unit`, `check_code` and `main` are **not** used. They know
    only REF-C2C1's units, and `check_code` pins the old driver blob.
  - `ibub_unit.py` has its own unit parser and argv resolver, its own CPU and thread gate, and its own `check_code`
    against its `config.json`.
- **Its units:**
  - `toy:<T>:<seed>`, one per toy. This is E_R's argv (`ref_c2c1/config.json` `e_r.argv`, which equals COV2D's toy argv
    `cov2d_jobs.argv("toy", …)` minus `--data-file`), plus `--data-file <the toy's staged copy>`.
  - `central`, once, with no `--data-file`. It is control C-REP (§5).
  - `central_df`, once. This is E_R's argv plus `--data-file <a staged copy of $K2A>`, where `$K2A` =
    `/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root`, sha256 `7eb39088…9b9db` (`cov2d_jobs.PINS`).
    - `$K2A` is COV2D's control-(2a) file: `$CV`'s own data tree, written through `cov2d_writer` and shown bitwise
      equal to it (`R/control2a/`).
    - COV2D's pilot used it to reproduce E_R through the same hook, to 4.55e-15 (`R/pilot/README.md`, (2b)).
    - So `central_df` must equal `central` and REF-C2C1's `c2_central`. It is control C-REP-D (§5), which runs the
      `--data-file` path end to end on real data.
- **Like for like with COV2D's toys:**
  - 64 CPUs per unit, with OMP/MKL/OPENBLAS/NUMEXPR at 64/1/1/1. These are COV2D's toy lanes (`cov2d_jobs.pack`, 4 ×
    64; `cov2d_env.sh` sets all four) and REF-C2C1's c2 units.
  - The unit refuses any other affinity, or any other value of the four variables. `ref_c2c1.run_unit` checks only
    the first three; IBUB adds NUMEXPR, as COV2D set it.
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
- **The driver blob: the two methods run different blobs of `re2_driver.py`.**
  - The toys' OmniFold ran blob sha256 `938c53c5…8b5a3b`. COV2D's score records give it as `code.driverSha256`, after
    §9.9 read every toy's provenance with `problems: []` (300 per tune; `R/readout/<T>/score_<T>.json`). REF-C2C1's units ran the same blob, and its `config.json` pins it.
  - **IBUB's IBU runs main's blob, `e226daf3…09971dd67`** (route (A), the director's ruling of 2026-11-23). The unit's
    `config.json` pins it by sha256.
- **The diff between them is COV2D-G2R amendment 1** (`0f57c22a`, `62864b16`): 79 lines added and 2 changed. Every
  added line falls into one of these:
  - a line tagged `# G2R`;
  - a docstring or help-text line;
  - the body of the new function `g2r_miss_override`.

  The gate and the entry points, quoted from `git diff a6054769 2f37c18a9 -- 2d-unfolding/re2/re2_driver.py`:

  ```
  +    ap.add_argument("--miss-map", default=None, metavar="NPZ",  # G2R
  +    g2r_kw, g2r_prov = {}, None  # G2R
  +    if args.miss_map is not None:  # G2R
  -                      alt_universe_branch=alt_universe_branch, **loader_select)
  +                      alt_universe_branch=alt_universe_branch, **g2r_kw, **loader_select)
  -                              alt_universe_branch=None):
  +                              alt_universe_branch=None,
  +                              miss_weight_override=None):  # G2R
  ```

  `--miss-map` is the amendment's only new option. **Without it, `g2r_kw` is empty, `g2r_miss_override` is never
  called, `miss_weight_override` stays `None`, and every `# G2R` branch in the loader is skipped.** So the amendment
  is inert, and the loader's production path is the old blob's.
- **Two guards make that hold:**
  - **C-G2R:** before each driver call, the unit asserts that its argv contains no `--miss-map` and no other option
    the amendment added. The amendment adds no other option, and a test checks that set against the driver's
    argparse. A violation refuses the unit.
  - **C-REP (§5)** is the proof: on the real data, main's blob through the new unit must reproduce REF-C2C1's
    `c2_central`, made with the old blob, to 1e-8.

## 4. The readings (fixed before any IBU output exists)

The readout runs on a login node at 0 node-h, per tune T, with n = 300 toys.

**Per cell c, and per band.** Both are reported:
- **each method's own bias, with its own SE**, for every cell and band (Ben asked about each method's bias within its
  uncertainty);
- **the difference between the methods.**

The quantities:
- **Mean bias per method:** b̄^m_c = (1/n) Σ_t e^m_tc. It is reported in three ways:
  - absolute;
  - relative to the toys' mean truth x̄_true,c = (1/n) Σ_t x_true,tc, in %;
  - in σ_c = √diag(C_T), from the committed blocks record, for comparison with COV2D's own `readouts.bias`. For a
    band, σ_band = √(aᵀ C_T a), with a the band's area vector (A_c on its cells, 0 elsewhere).
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
- **The bands are kinematic regions,** as Ben's "bins/regions" are (the director's ruling of 2026-11-23). They are not
  COV2D's systematic bands. Each is an area-weighted integral over the reported cells, Σ_c x_c ΔpT_c Δp∥_c, using `Cells.area`. They are
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
- **On z\*.** The ratio uses a bootstrap SE from n = 300, so its tail is close to t₂₉₉'s, whose quantile here is about
  3.75 against z\* = 3.7044. z\* is kept as declared, and the report prints both quantiles. The union bound over the
  31 bands, which are positively correlated with the cells, is conservative by more than that difference.
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

  Then `cov2d_readouts.bias(E, σ)` and all three fields of `cov2d_readouts.spread_alone(E, C_T, C_model_abs)` must
  equal the committed score record's `readouts.bias` and `readouts.spread_alone`, cell by cell. Those fields are
  `p_hat`, `pull_mean` and `pull_sd`. The bias and the two pull fields must agree to 1e-12 absolute (in σ units).
  `p_hat` is a count over the toys and must agree exactly. The score records are `score_G18.json` `84976694…9088ec`
  and `score_AR23.json` `fe5263e9…4f5ce1`. This ties the pre-surrogate x̂^OF used here to the errors COV2D graded.
  - **Why `p_hat` and `pull_sd`, not only the means.** The bias and `pull_mean` are means over the toys, so a
    permutation of the toy-to-truth pairing leaves them unchanged. `pull_sd` and `p_hat` depend on each toy's own
    error, so a mispairing, a toy file swap or a cell reorder moves them (the agy read, finding 1).
- **C-TRUTH:** the order checks of `cov2d_readout.phase_score`, carried over:
  - `truth_xsec.npz`'s seeds are `pseudo_a.json`'s natures in order;
  - the toys are `cov2d.TOY_SEEDS[T]` in order;
  - the 205 cells equal the blocks record's `rep`;
  - **the pairing, per toy index k**, for both methods: the OmniFold product's label is `T_<T>_<TOY_SEEDS[T][k]>`.
    The IBU unit's done-marker and meta name the same seed. The IBU unit's recorded `dataFileSha256` equals
    `pseudo_b.json`'s line for that seed. The truth row is the one whose seed is that seed. Any mismatch refuses
    the readout.
- **C-REP, the IBU unit against REF-C2C1.** The `central` unit, on the real data with no `--data-file`, must reproduce
  REF-C2C1's `c2_central.npz` (sha256 `929d0e78…43b76f4`, in `/pscratch/sd/j/josephrb/ref-c2c1-20261106/units/`, read
  through `O_NOATIME`). The bar is 1e-8 relative (RE-2's rule, as REF-C2C1's C-REF uses it), on the 205 cells, for
  `xsec` at every K of the scan, and for `y` and T. This covers the driver blob (§3, route A) and the new unit's wiring.
  - **The reference is on pscratch only.** The repository holds its done-marker, which carries its sha256
    (`receipts-ref-c2c1/step2/units-centrals/c2_central.done`), but not the npz.
  - If the npz is gone or its digest differs, the run **STOPs** before any toy unit, and the director rules. No
    fallback is declared (the director's ruling of 2026-11-23).
- **C-REP-D, the `--data-file` path on real data.** The `central_df` unit (§3) must reproduce REF-C2C1's
  `c2_central.npz` to the same 1e-8, on the same quantities. It must also reproduce IBUB's own `central`, reported
  beside it.
  - Unlike C-REP, it runs every step the toys run: staging a data file under the staging root, the TFile guard on it,
    its digest check, the driver's `--data-file` reader and the recorded `dataFileSha256`.
  - So a wiring defect that appears only with `--data-file` fails it (the agy read, finding 2).
  - `$K2A`'s sha256 is checked by `O_NOATIME` before the copy. If the file is gone or its digest differs, the run
    STOPs before any toy unit, as for C-REP.
- **C-G2R, per unit** (§3): the argv carries no option added by G2R amendment 1. If it does, the unit refuses before
  the driver is imported.
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
- **C-CELLS:** IBU's cross section is finite on all 205 cells, in every toy, at both reported K: `hXSec2D` at K = 10,
  and the npz row at K = 5. Any non-finite value is counted and reported, and T is INVALID. Negative values are
  counted and printed. They are not a failure.

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
- **The job:** one exclusive CPU node, regular QOS, 4 lanes × 64 CPUs.
  - **The reference phase:** `central` runs on lane 1 and `central_df` on lane 2, at the same time. Lanes 3 and 4 wait.
  - **A barrier.** No toy unit starts on any lane until both references have finished, C-REP and C-REP-D have
    passed, and the re-price check below has passed. If any of these fails, the job ends before any toy (the agy
    read, finding 6).
  - **The toy phase:** the 600 toy units are dealt round-robin, 150 per lane.
  - The longest lane is 217 + 150 × 217 = 32,767 s, plus a 300 s preflight.
  - The limit is ceil-to-the-minute of 1.25 × 33,067 s: **11:29:00**.
  - The charge is about **9.2 node-h**.
  - **The cap is 11.5 node-h** (1.25 × 9.2). Nothing reruns without the director.
- **The re-price trigger:** if either reference unit's wall is above 1.25 × 217 s, the job ends at the barrier, and
  the question goes to the director.
- **A preflight in the connect (login node, before submission):**
  - the stat and `O_NOATIME` sha256 of C-REP's reference `c2_central.npz` and of `$K2A`;
  - the existence of all 600 toy data files, by stat.

  If either reference is missing or off its digest, the connect submits nothing and reports a STOP (the agy read,
  note 9).
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
  - C-OF on a synthetic ensemble. A perturbed surrogate must fail it, and so must a swap of two truth rows (which the
    means alone would pass);
  - the barrier: a failing reference unit must leave every toy unit unstarted;
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

## 11. The director's rulings (2026-11-23, by message, on revision 1 at `0e7449c1`)

1. **The driver:** route (A), main's `e226daf3`, with two additions: the C-G2R assertion, and C-REP at 1e-8 as the
   proof. The two blobs and the diff are recorded in §3.
2. **The bands** are kinematic: 14 p_T bands, 16 p∥ bands and the total (§4).
3. **One family of 236 tests per tune** is accepted. It is conservative for DIFFER, and the printed resolution covers
   the rest. Each method's own per-cell and per-band bias is printed with its SE, beside the difference (§4).
4. **C-REP's reference** is not committed, so it is read from pscratch. If it has been purged, the run STOPs and the
   director rules. No fallback (§5).

## 12. The agy read of revision 2 (2026-11-23)

- **The reader:** agy `gemini-3.8-flash-high`, given the revision-2 text (sha256 `92185843…98ca`), COV2D §4–§6,
  REF-C2C1 §1.1, `ref_c2c1.py` and config, and the COV2D code. It answered **VERDICT: REVISE**.
- **The second reader did not run.** agy `claude-opus-4-6-thinking` was refused with RESOURCE_EXHAUSTED (429). Its
  quota resets about 29 h after the run.
- **Every finding was taken as a fix in this revision:**
  1. MAJOR, C-OF was blind to a toy-to-truth mispairing, because the bias and `pull_mean` are means: fixed by adding
     `p_hat` and `pull_sd`, and the per-toy pairing check in C-TRUTH (§5).
  2. MAJOR, C-REP never runs `--data-file`: fixed by the `central_df` unit and C-REP-D (§3, §5).
  3. MAJOR, C-CELLS checked only K = 10: fixed to K ∈ {5, 10} (§5).
  4. MINOR, σ for bands was undefined: σ_band = √(aᵀ C_T a) (§4).
  5. MINOR, K = 5's extraction from the npz was unstated: the `rep` mask, and K = 10's npz row checked against
     `hXSec2D` (§2).
  6. MINOR, the re-price stop could race the toys on lanes 2–4: the barrier (§8).
  7. MINOR, `ref_c2c1`'s unit parser cannot take IBUB's units: IBUB's own parser and gates are stated (§3).
  8. NOTE, z\* against t₂₉₉: both quantiles are printed, and z\* is kept (§4).
  9. NOTE, a purged reference would waste a node: the connect's preflight (§8).
- **The reader's two fidelity notes are also fixed:** the 224-to-205 masking of `truth_xsec.npz` (§1), and NUMEXPR,
  which `ref_c2c1` does not check (§3).
