# AMENDMENT A1a: LL5D's calibration and gate code (2026-11-08)

**By** the `cov2d` session, for `coverage-5b-audit` to audit and the director to bind as **LL5D binding 2**. Nothing runs
before binding 2.

**A1a → binding 2, A1b → binding 3.** This is the director's choice of 2026-11-08, recorded as ruling 4 of
[`LL5D-BINDING-1.md`](LL5D-BINDING-1.md) (#943). The declaration's "amendment A1 … binding 2" (§11, §12) becomes:
- **A1a (this amendment) → binding 2:** `calib`, `gate` (the receipt with D1–D3, N1 and T ≤ 0, the clipping gate, the
  cross terms), m2-a to m2-f and the auditor's RSS low. It is audited and bound before §11's steps 3–4.
- **A1b → binding 3:** `unfold`, `walls`, `clipcheck`, `null` and `readout`. It is audited and bound before the rebuild,
  the toys and the grading.
- **The condition (binding 1, ruling 4):**
  - A1b implements the declaration as bound at M = `1acdee66`. It cannot change in response to anything A1a's jobs
    produce.
  - A gate STOP goes to Joseph under "Decide at the STOP" (#939).
  - A gate PASS licenses only A1b running as declared.

**Under:**
- [`LL5D-DECLARATION.md`](LL5D-DECLARATION.md), as bound by binding 1 at M = `1acdee665ea162b2b5a2026ab620990a116c6092`
  (sha256 `6748d418…`). Its §3.4, §3.6, §5, §7, §9, §10 and §12 are cited below as "§n".
- **The director's rulings on A1 (2026-11-08, by message):**
  - **(1) The plan:** fd_1b_c2.py is copied verbatim, with a blob-digest test and its provenance. ll5d.py's own input
    builders are a fourth named departure. The all-path equality test runs as a subprocess against `342c0ce5`'s path,
    REQUIRED, with a mutant.
  - **(2) The split** above.
  - **(3) The cross terms are option (B):** §7's definition is kept, Joseph's 11-02 addition (i) word for word. It
    comes with four conditions, all met here (§5a, §8):
    - §9's error is corrected;
    - an equivalence test against `342c0ce5`'s crossterm is REQUIRED, with a mutant;
    - no array the size of V is held;
    - it stays a readout.
  - **(4) The receipt's exact pass** follows 1B's §2d (ii) / exact_n1 precedent. The near-zero recompute that makes clip
    signs exact is named as part of T ≤ 0's construction, with its own test.

**MEASURES:** nothing. No job has run for A1a. Every number below is a test result on synthetic fixtures, or arithmetic
on recorded timings.

**CANNOT AUTHORIZE:**
- any job before binding 2;
- A1b's code;
- any change to the declaration's design, thresholds, seeds, readings or licences beyond the textual corrections in §5,
  each of which is named;
- any repair after a STOP (#939).

**CITABLE FOR:**
- the code and tests at the digests in §1;
- the mapping of A1a onto the declaration (§3, §8);
- the named departures and corrections (§4, §5).

**NOT CITABLE FOR:**
- any coverage statement, in either direction;
- any measured cost: the cross terms' and the receipt's costs here are estimates until the gate jobs time themselves;
- anything A1b will do.

## 1. Files and digests

All digests are sha256 at this commit.
- **The receipts were made at `43b73ffa2224d1ce8e2fc9654fa94498cfbab01f`,** from a clean checkout of that commit
  (porcelain 0 before and after), so every tracked file was in scope (`fd/receipts-ll5d/a1a/README.md`).
- **The commit that adds them** changes only the receipts, their README, this file, CATALOG and MANIFEST. None of the
  code or tests changes.
- **Correction (coverage-5b-audit's NO-GO C1 on #945 at `73684077`):** the receipts at `73684077` were made on base
  `1acdee66`, before the PR's own files were tracked.
  - At that head the seed-collision test found those files (the test receipts printing its docstring, and the mutation
    script's mutant strings) and failed.
  - So the unmutated control failed, and the "killed" count meant nothing.
  - The check now excludes LL5D's own nine files by exact path, and a positive control shows it still catches a
    collision anywhere else (§7).

| file | role | sha256 |
|---|---|---|
| `nd-unfolding/ll5d.py` | A1a's module: `calib`, `gate`, `gate-merge` | `b7674f6729754616930944a32a71889ce599e8419cf539f792c180217f484f9a` |
| `nd-unfolding/fd_1b_c2.py` | verbatim copy of `342c0ce5`'s (§2) | `522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f` |
| `nd-unfolding/tests/test_ll5d.py` | the 67 tests | `c5fd4deba61abdc540c1f6f9c918812aa48f406c62eaa172c8f44e708be91b6f` |
| `nd-unfolding/tests/ll5d_a21_reference.py` | the all-path equality's subprocess runner | `8fbecaae657fa40015e51fb917422321734e3d1c79dcd6591efc42639bc2365a` |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | the mutation check (45 mutants) | `74c530e9debab593082e3b3c540be8a6d265e6643a2f89bf0b61229965732fd4` |
| `nd-unfolding/tests/data/fd_1b_mc_at_342c0ce5.py.txt` | `342c0ce5`'s fd_1b_mc, vendored for the equality test only | `062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67` |
| `fd/receipts-ll5d/a1a/tests-numpy126-seed{0,1,2}.txt`, `tests-numpy2-seed0.txt`, `mutation.txt`, `README.md` | the receipts (§7) | in MANIFEST.tsv |

## 2. fd_1b_c2.py: provenance

- **Source:** commit `342c0ce50cae80aa819ef931d7bdb7632279b6d9`, branch `decl/1b-staged-a2-1-20261103`.
  - That is the A2.1 code that the 1-thread probe (job 60870880) ran: probe.json records `fd_1b_c2.py` as
    `522d7edd…`.
  - Git blob `0cb727612a6658f27fe14e51f8120450da581a15`, sha256 `522d7edd…`.
  - The branch was read with `git show` and not touched.
- **Tests:** `Provenance.test_fd_1b_c2_is_342c0ce5s_bytes` checks the sha256 and the git blob. The vendored fd_1b_mc copy
  is checked against blob `e77fe6ba…` and sha256 `062628b6…`.
- **Why it imports on main:** its top-level imports (fd_1b_toys, s1_assemble, clip_probe2, cov2d) all resolve there.
  fd_1b_toys, s1_assemble and clip_probe2 are byte-equal to `342c0ce5`'s.
- **Not callable on main:** its drivers (`prepare`, `fine_sums`, `c2_inputs`, `calibrate_main`, `c2check_main`,
  `c2probe_main`) import fd_1b_mc lazily. They need six A2.1 functions that main's fd_1b_mc lacks: `flat_cells`,
  `verified_weights`, `td_cells`, `same_functional`, `draw_columns` and `check_clip_gate`.
  - ll5d never calls them. `Provenance.test_the_drivers_are_not_called` checks the source.

## 3. What A1a implements, by section

| declaration | A1a |
|---|---|
| §3.2–§3.3, the draw and per-row first order | `drop2`, `selection`, `compose_rows` (compose's order); the draw is `fd_1b_toys.draw_for_seed`, unchanged |
| §3.4, the denominator | tdw_ref = the bank's `GEANT_Neutron_0_tdw.npy`, pinned to the sf1 manifest's digest `c0ae3c18…` (§5f); a detector universe's tdw rows are tdw_ref (zero departure); `nature_truth` clips each tree on its own composite, row by row, then histograms |
| §3.6, seeds | `TOY_SEEDS`, `STAT_SEED`, `NULL_SEED`, `CAL_SEED`, `gate_seeds`, `check_n` (N in 300..9,000 in whole blocks of 20) |
| §5.1, the receipt | `receipt` (§6 below): N1 and T ≤ 0 STOPs; D1–D3 in `load_tdw_ref` and `denominator_controls`; the run halts at the first STOP |
| §5.2, the clipping gate and its calibration | `calib_main`, `one_set`, `threshold_rule`; `gate_main` with fd_1b_c2's `c2_truth`, `c2_block`, `reading_1b`, `gate_n`, `backstop` |
| §7, the cross terms (readout) | in `receipt`: `product_rows` (streamed) against the first-order composite, `cross_z` (§5a) |
| §9, `--time`, the projection lines | the in-job projections: the receipt after 20 natures, the gate after its first two blocks, the calibration after one set; each is a REPRICE past 0.9 × `--time-limit-seconds` |
| §10, the controls in A1a's jobs | D1–D3; r_T > 0 and finite on every row; the paired draw (m2-e); the calibration's single-universe U x_T bitwise in the gate; one BLAS thread; O_NOATIME; the atime sidecar, with an exit code carrying 8 on any move |
| §11, steps 3–4 | `ll5d calib`; `ll5d gate --truth g18` and `--truth ar23`; `ll5d gate-merge` |

The connect scripts and sbatch files are not in A1a. Each comes with its own connect's sha256 and the director's go
(binding 1, ruling 8).

## 4. The named departures from the verbatim gate code

1. **`layout_minus2`:** `fd_1b_c2.layout_1b()` with GEANT_Neutron and GEANT_Proton removed, and their four dump
   universes off the tags. That leaves 171 universes against 175.
2. **`drop2`:** an `all` draw less those universes, on the same stream, in the draw's order.
3. **`restrict`:** a reading's view of the one `all` pass.
   - The small per-universe sums (H, single_x, phi_single) are the `all` rows for the reading's tags, selected and not
     recomputed. The column map and flux_cols are rebuilt on those rows.
   - The calibration and the reference variances use this compact form.
4. **ll5d's own input builders** (`fine_sums`, `prepare`, `c2_inputs`): A2.1's, on the `all` and `minus2` layouts, with
   tdw_ref in place of A2.1's `--cv-tdw` array (§3.4's first option). The `all` path is held bitwise equal to
   `342c0ce5`'s by the REQUIRED equality test (§8).
5. **`threshold_rule`:** the 1 % over the four evaluations, measured jointly per replicate on the paired null. Both
   readings of a truth read the same replicate set, so their correlation is inside the budget, not bounded by a union.
   fd_1b_c2's `null_stats` and `stops_at` are used unchanged. `power_at`, `control`, `linearisation` and
   `calibration_verdict_n` run unchanged on the evaluation keys.

**The no-copy form of V (the auditor's RSS low on #936).**
- The gate's per-row arrays V are about 46 GB each on the real bank, which is why the probe peaked at 269 GiB. They are
  never copied for `minus2`.
- Its selection matrix is written over the `all` column map, with the removed universes' columns 0. That is the
  selected form's composite, since the zero columns add nothing.
- `Builders.test_m2g_…` holds c2_truth over (V, the padded S) equal to c2_truth over (V's selected rows, the compact S)
  to 1e-12 relative, and checks that `restrict` returns no row array.
- So the two-reading peak is the one-reading peak plus small arrays. The gate record writes `peak_rss_kib`
  (`getrusage` ru_maxrss) for the whole job, the cross terms included, which is the measurement the low asked for.

## 5. Corrections and choices, each named for binding 2

**a. The cross terms were wrongly priced in §9.**
- **The error:** §9 says "The cross terms are A2.1's multiplicative-against-additive comparison, inside c2_truth. The
  block time already includes them." That is wrong.
  - c2_truth's multiplicative composite is C2's truth-side U x_T with its floor.
  - §7's readout is the reco-weighted histogram under product against additive composition: Joseph's 11-02 addition
    (i), which A2.1 computed in fd_1b_mc's receipt (`crossterm`).
- **The memory problem:** ported as written, crossterm builds four arrays the size of V (ρ, logs, signs, zeros), about
  180 GB beside the gate's 269 GiB. It would not fit.
- **The director's option (B):** the product composite is computed per declared draw, streamed over the draw's own
  universes (`product_rows`), in the receipt's pass. It holds no array the size of V
  (`CrossTerms.test_the_streamed_product_holds_no_array_the_size_of_v`).
  - It is a readout: it moves no verdict and gates nothing.
- **Its cost, unmeasured until the gate job's own timing:**
  - about 1–1.5 h per truth;
  - that is 300 draws × 2 readings × about 37 universes × 3 arrays, memory-bound.
  <!-- absence-ok: a scoping statement about a projected cost; no LL5D job has run, so no timing exists to cite -->
- **The projection against the gate's 0.9 line of 100,440 s** (`--time` 31:00:00), with G(N) from §9:

  | N | G(N) | plus the cross terms | against 100,440 s |
  |---:|---:|---:|---|
  | 3,000 | 37,056.7 s | 40,657–42,457 s (11.3–11.8 h) | well inside |
  | 9,000 | 96,594.7 s (97,621.9 s at the slowest block) | 100,195–101,995 s (101,222–103,022 s at the slowest block) | at or above the line: a REPRICE near N = 9,000, as §9 declares |

- **The cap** stays at 148.0 node-h.
- **The expected totals** become about 62–63 node-h at N = 3,000 (1.44 + 2 × (10.29 + 1.0–1.5) + 0.4 + 37.64) and about
  98–99 at N = 9,000 (4.33 + 2 × (26.83 + 1.0–1.5) + 0.4 + 37.64). Both are under the cap and under half the balance
  (binding 1, ruling 6: half is 849.1).

**b. The receipt's exact float64 pass is 1B's §2d (ii), as the director ruled it** (A2.1's `fd_1b_mc.exact_n1`, which
§5.1 carries).
- **The composites:** each block of 20 draws is composed as S V − (k − 1) a_ref (float64 BLAS).
- **N1:** the rows past the screen |a_D| > 10 L(1 − 10⁻⁹) get the exact peak, and pairs within 10⁻⁹ of the bound are
  recomputed in compose's order. L is the max over the reading's bands of the min of |a_u| over the band's universes,
  which holds per reading because each reading's draw holds one universe of each of its bands.
- **T ≤ 0's construction (the director's naming):** every wt and tdw row with |a_D| ≤ 10⁻⁹ max_u |a_u| is recomputed
  in compose's order before the clip.
  - The rounding of a BLAS composite is many orders below that margin, so every clip sign is compose's.
  - T_D is therefore 0 in a reporting cell exactly when every row there clips in compose's order.
  - `Receipt.test_t_le_0_takes_composes_clip_sign_on_near_zero_rows` builds rows whose compose-order composite is
    exactly 0 while the BLAS composite rounds above 0, and requires the STOP. Its mutant (`ZERO_REL = 0`) passes
    instead and is killed.
- **Why the change:** my first, strictly sequential receipt would have run about 3–10 h per truth, against §9's
  allowance of 2 × 15 blocks. The BLAS form runs at the block rate §9 priced.
- **Recorded quantities** (masses, fractions, the cross terms) use the BLAS composites, after the sign recompute. They
  are descriptive.

**c. The backstop's 300-draw SDs.** These come from the first 300 draws of each calibration replicate set, a 300-draw
null of the same law, in place of A2.1's separate 300-draw calibration job. That adds 300/N of the set work, inside
C(N)'s overstatement (§9).

**d. N = 3,000 is fixed** (11-04 item 1).
- A calibration verdict of `POWER_SHORT_TO_DIRECTOR` goes to the director, not to Joseph.
- A rerun at a larger N ≤ 9,000 is inside the declared design (§3.6, §5.2), so it is an operational go by the director
  (the director, 2026-11-08). It runs the same code with `--draws`, and the director tells Joseph.
- Every N ≤ 9,000 is inside the cap.

**e. The calibration's streams** are A2.1's form, `default_rng([CAL_SEED[truth], set, CAL_SALT])`, with
CAL_SEED = 4,770,500 (G18) and 4,770,600 (AR23), and A2.1's CAL_SALT 202,611,037.
- I read §3.6's "from 4,770,500" as the stream's base. Ten thousand consecutive integer seeds from 4,770,500 would have
  run into AR23's 4,770,600.
- A three-word stream ending in a non-zero salt equals no two-word one (A2.1's argument), so the replicates are disjoint
  from every declared draw (`Calibration.test_the_calibration_streams_are_disjoint_and_fixed`).

**f. tdw_ref's digest.**
- The sf1 manifest (`state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt`) records all six bank GEANT tdw
  files at one sha256, `c0ae3c18…`.
- `load_tdw_ref` reads each through O_NOATIME, requires its bytes to be the manifest's, requires `GEANT_Neutron_0`'s to
  be `TDW_REF_SHA256`, and then checks D1 bitwise in the job. The pins file does not cover these six bank copies, since
  `fd_1b_toys.weight_files` takes the detector bands from the dump.

**g. Binning.** The receipt's denominators are binned by A2.1's `td_cells` and `bincount`, which reproduce
`np.histogramdd`'s bins (`Clip.test_the_bins_are_histogramdds`), rather than by calling `histogramdd` per nature.

**h. The definition** (the H2 JSON) is read plainly by `s1_assemble.fine_map`, as A2.1's gate read it. It is a
repository file at the deploy, not an input another lane made.

**i. r_T > 0 and finite is checked on every row** (§3.1, §10). A failure is INVALID before anything is read.

## 6. The jobs

**`ll5d calib`:** one job, two truths, four evaluations.
- It refuses unless every BLAS thread variable is 1.
- It loads the world (fd_1b_mc._load_world, tdw_ref with D1), r_T with its control, and one pass of every universe
  (`prepare`).
- Per truth it computes the single-universe U x_T, and per evaluation the reference variances.
- It times one replicate set. It reprices past min(`--budget-seconds`, 0.9 × `--time-limit-seconds`).
- It then runs CAL_SETS = 10,000 sets per truth in fork workers, each set in both readings.
- It writes the record (`ll5d-calibration/1`): the verdict, the rule, the power, the per-evaluation 300-draw SDs, the
  controls, the threads, the code digests, `fd_1b_c2_source` and the peak RSS. It also writes an npz of the ratios and
  the single-universe U x_T.

**`ll5d gate --truth T`:** one truth per job.
1. Threads, then the world and D1.
2. D2, D3 and r_T > 0. A failure writes the record as INVALID, before anything else is read.
3. `prepare` with rows. The tie to the calibration: its digests, CALIBRATED, this code's digests, a threshold and a
   backstop SD for every evaluation, N in range, and the single-universe U x_T bitwise.
4. The receipt (§5b), with the cross terms. A STOP writes the record and halts.
5. Per reading: C2's record on the declared 300 and on the gate sample of N. The first 300 must be bitwise the declared
   ones, or the job is INVALID. Then `reading_1b` with the large-sample gate at the calibration's thresholds, and the
   backstop.
6. PASS needs "option (1)" and the backstop passing in both readings; anything else is a STOP. The record
   (`ll5d-gate/1`) carries the receipt, the per-evaluation readings, the projections, the config hash, the peak RSS and
   the atime check. The receipt npz holds the clipped masses per fine cell.

**`ll5d gate-merge`:** two per-truth records with their digests give one record (`ll5d-gate-merged/1`). PASS needs PASS
at both truths, with every shared field equal. A STOP or INVALID is carried as it is.

**Exit codes:**
- 0: PASS or CALIBRATED;
- 3: STOP, or a calibration verdict to the director;
- 4: REPRICE (`*.reprice.json`);
- 5: INVALID (`*.invalid.json`);
- 8 is OR-ed in on any atime move.

## 7. The tests (the declaration's REQUIRED list, A1a's part)

| REQUIRED (§12, the director's rulings) | test(s) | its mutant(s) |
|---|---|---|
| per-row first-order composition, and the k = 1 reduction | `Composition.test_first_order_in_draw_order`, `…test_k1_is_the_universe_bitwise` | the reference dropped; k = 1 aliasing V |
| the tdw reference | `Builders.test_detector_rows_carry_tdw_ref_and_enter_with_zero_departure`, `…test_the_cv_denominator_is_hist_tdw_ref` | the detector rows not tdw_ref |
| each tree clipped on its own composite, and nowhere else | `Clip.test_each_tree_is_clipped_on_its_own_composite_and_nowhere_else` | tdw unclipped |
| the denominator ≥ 0 under adversarial composites | `Clip.test_the_denominator_is_never_negative_under_adversarial_composites` | tdw unclipped |
| D1, D2, D3 at one ULP, and D2 at its edges | `Denominator.test_d1_fires_on_one_ulp`, `…test_d2_at_its_cell_edge`, `…test_d2_at_its_total_edge`, `…test_d2_fires_on_a_one_ulp_support_change`, `…test_d2_fails_on_the_support_alone`, `…test_d3_fires_on_one_ulp` | allclose for D1 and D3; the edges widened; support ignored |
| the T ≤ 0 STOP and N1 at their edges | `Receipt.test_t_le_0_stops_and_halts_at_the_first`, `…test_t_le_0_takes_composes_clip_sign_on_near_zero_rows`, `…test_n1_stops`, `…test_n1_at_exactly_the_bound_does_not_stop`, `N1.test_the_bound_is_strict` | T = 0 missed; the run continuing after a STOP; ZERO_REL = 0; the bound loosened; the screen hiding a pair; N1 stopping at exactly 10 |
| the paired draw, and the `minus2` removal | m2-a, m2-b, m2-e below | as below |
| Φ_u in the truth | `Receipt.test_each_reading_composes_its_own_draw_and_the_truth_takes_phi_u` | phi = universe 0's |
| the gate's thresholds and the four-evaluation budget | `Rule.*` (5 tests), `Jobs.test_each_evaluation_reads_its_own_thresholds` | a non-joint union; any evaluation set accepted; a reading taking the other reading's thresholds |
| the seed ranges | `Seeds.*` (4 tests): §3.6's collision search repeated at this sha, excluding only LL5D's own nine files by exact path (`OWN_SEED_FILES`), and its positive control `test_the_seed_check_still_catches_a_real_collision` | a toy seed moved; the gate sample skipping the toys |
| O_NOATIME over the call graph, and an atime move exiting 8 | `NoAtime.*` (2), `ExitCodes.test_an_atime_move_sets_8` | plain reads; 8 not set |
| **m2-a** | `Layouts.test_m2a_minus2_is_s1s_layout_less_exactly_two_bands` | the tags kept; GEANT_Pion removed instead |
| **m2-b** | `Selection.test_m2b_selection_accepts_drop2_and_refuses_a_kept_band`, `Layouts.test_drop2_…` | drop2 keeping one band |
| **m2-c** (the auditor's low: the additive composite) | `Composition.test_m2c_minus2_is_all_less_the_two_terms_before_the_clip` (bitwise on integers, 10⁻¹² on floats), `…test_m2c_the_fine_sum_composites_too`, `…test_m2c_each_reading_is_clipped_on_its_own_composite` | the receipt composing `minus2` from the all draw |
| **m2-d** | `Builders.test_m2d_the_minus2_reference_is_all_less_the_two_bands_variances` (10⁻¹², atol 0) | the `all` reference used for `minus2` |
| **m2-e** | `Calibration.test_m2e_each_minus2_replicate_is_the_all_replicates_draws_less_two` | an independent `minus2` stream |
| **m2-f** (the auditor's low: source_factors off the nature path) | `SourceFactors.test_m2f_…`, `Provenance.test_the_drivers_are_not_called` | source_factors called |
| **the RSS low** | `Builders.test_m2g_restrict_copies_no_row_array_and_the_zero_columns_are_the_selected_form` | restrict copying the row arrays |
| **the all-path equality** (REQUIRED) | `A21Equality.test_the_all_path_equals_a21s_bitwise`: a subprocess runs `342c0ce5`'s prepare → c2_inputs → c2_truth → c2_block and c2_vi, with the vendored fd_1b_mc and `--cv-tdw` = tdw_ref. It compares H, cv, V, geo, the packing, single_x, ref_x, ref_count, every c2_truth quantity, the blocks and (vi) **bitwise** | Φ_u misplaced; the reco cells without the reco pass |
| **the cross terms** (REQUIRED, condition 2) | `CrossTerms.test_the_streamed_product_equals_a21s_crossterm`, `…holds_no_array_the_size_of_v` | the reference dropped from the product; first order not used where a_CV = 0 |

**Not bitwise in the cross terms, and why.** `crossterm` forms the product as a_CV exp(Σ log |ρ|) times its sign
parity. `product_rows` forms it by repeated multiplication. The two agree to rounding, about k × eps relative, so the
test holds them within 10⁻¹² relative with no absolute tolerance. The first-order histograms are held to the same
tolerance, because crossterm multiplies on the masked columns and the receipt on all of them.

**Other tests:**
- the gate end to end over the toy world (`Jobs.*`, 9 tests): the calibration; the gate; an uncalibrated, foreign or
  incomplete calibration refused; a failed control INVALID before anything is read; a failing reading a STOP; each
  evaluation reading its own thresholds; a gate sample whose first 300 differ refused (11-04 item 1, its mutant the
  check skipped); each projection repricing;
- the merge (`Merge.*`);
- the one-BLAS-thread refusal;
- `Selection`, `Clip.test_the_bins_are_histogramdds`.

**Results** (`fd/receipts-ll5d/a1a/`):
- All made at `43b73ffa`, from a clean checkout.
- `test_ll5d.py`: 67 tests, OK, at PYTHONHASHSEED 0, 1 and 2 under Python 3.12.2 and numpy 1.26.4 (the cluster's numpy).
  Also OK once under Python 3.13.7 and numpy 2.4.4.
- `ll5d_a1a_mutation.py`: **45 mutations, all killed.** The unmutated suite runs its 67 tests and passes, rc 0.
- Each receipt heads its file digests.
- The suite's fixture is A2.1's toy world (`test_fd_1b.World`), with the bank's tdw about tdw_ref within 2 % row by row
  (A2.1's fixture rule, centred on tdw_ref). The world's weights are hash-seeded, so each PYTHONHASHSEED is a
  different world.

## 8. What A1a does not contain

- **A1b:** `unfold`, `walls`, `clipcheck`, `null` and `readout`. These cover:
  - the 227-unfold rebuild per truth and C_T, C_T⁽⁻²⁾ with the block-removal control;
  - the toys;
  - the pilot's controls;
  - the grading and the Cholesky reading rule.
- **The connects and sbatch files,** which come with each connect's go.
- **The three mutants first left unplanted** at `73684077` are now planted, each with its test (the director,
  2026-11-08): P1's first-300 refusal, N1 at exactly the bound inside the receipt, and each evaluation reading its own
  thresholds.

## 9. For the auditor

- **The departures:** §4. The equality test is the check that departure 4 changes nothing on the `all` path.
- **The receipt's exactness argument:** §5b. The screen's proposition is A2.1's, applied per reading.
- **The no-copy V:** §4. m2-g's tolerance is 10⁻¹² relative, because BLAS sums over 175 and over 171 columns.
- **Costs that are unmeasured until the gate job:** the receipt per block, the screen and row-max one-offs (one pass per
  universe per array per reading), and the cross terms. The projections cover them, and a REPRICE is not a STOP.
  <!-- absence-ok: a scoping statement about costs that only the gate job can time; no LL5D job has run -->

Nothing is submitted, deposited or tagged.
