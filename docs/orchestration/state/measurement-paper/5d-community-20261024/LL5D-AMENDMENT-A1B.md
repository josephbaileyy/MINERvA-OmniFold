# AMENDMENT A1b: LL5D's unfolds, walls, clipcheck, null and readout (2026-11-08)

**By** the `cov2d` session, for `coverage-5b-audit` to audit and the director to bind as **LL5D binding 3**. Nothing
under it runs before binding 3: not the pilot, the rebuild, the toys or the grading.

**Under:**
- [`LL5D-DECLARATION.md`](LL5D-DECLARATION.md), as bound by [`LL5D-BINDING-1.md`](LL5D-BINDING-1.md) at
  M = `1acdee665ea162b2b5a2026ab620990a116c6092`. Its sections are cited as "§n".
- **Binding 1, ruling 4.** A1b implements the declaration as bound at M. It may not change in response to anything A1a's
  jobs produce. Its audit checks that it refers to no A1a output beyond the gate's PASS or STOP, apart from the director's
  two named exceptions below.
- **LL5D BINDING 2** (#948): A1a at M_A1a = `e92e946759772d13e21055b21c69189c8b007183`, the seal, POWER_SHORT, and STOPs
  under #939.
- **The director's rulings on A1b (2026-11-08, by message):**
  - **§5.3's inputs come from A1a's sealed clip-prep file** (A1a §5j). A1b reads it only by the sha256 the gate record
    gives, only in the clipmean and clipcheck, and refuses a mismatch.
  - **The weakened label** (the 11-03 clip rule, item 4) reads, from the gate record, only each evaluation's per-cell
    clipped variance ratio r_c. The rule is a strict < 0.9, per cell and per evaluation, and is descriptive only. A
    key allowlist enforces the read. If r_c values become visible before binding 3, the label code may not change after
    that point, except on an audit finding that the audit records.
  - **A new module, `nd-unfolding/ll5d_b.py`,** imports A1a's `ll5d.py` unchanged. This is a named departure from §12's
    single-module wording, to be named in binding 3 too.

**MEASURES:** nothing. No job has run for A1b. Every number below is a test result on synthetic fixtures.

**CANNOT AUTHORIZE:**
- any job before binding 3;
- a coverage statement beyond §13's licences;
- any change to the reported covariance;
- any repair after a STOP (#939);
- any opening of the sealed clip-prep file outside `read_clip_prep` in a bound job.

**CITABLE FOR:**
- the code and tests at the digests in §1;
- the mapping onto the declaration (§2);
- the named choices (§3).

**NOT CITABLE FOR:**
- any coverage statement, in either direction;
- any measured cost;
- the estimator's behaviour, since the tests replace it with a stand-in.

## 1. Files and digests

All digests are sha256. The receipts were made at the commit the receipts README names, from a clean checkout of it
(`fd/receipts-ll5d/a1b/README.md`).

| file | role | sha256 |
|---|---|---|
| `nd-unfolding/ll5d_b.py` | A1b's module: `unfold`, `walls`, `clipcheck`, `null`, `readout` | `24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb` |
| `nd-unfolding/tests/test_ll5d_b.py` | the 28 tests | `642a45b84fd2b70103f5180203c4ade8302eb7ed3d0cec77df8ac86a116936ab` |
| `nd-unfolding/tests/ll5d_a1b_mutation.py` | the mutation check (26 mutants) | `f5e683bb1892b7f6661ef1037c5b7c7c9c08dad87d55e8c6b35a2b9640da807f` |
| `nd-unfolding/ll5d.py` | A1a's, imported unchanged | `9dbf9cf499f2c709ed7cffe809336a9dfd2122d34185d433036944c6927bf8fc` |

## 2. What A1b implements, by section

| declaration | A1b |
|---|---|
| §3.2–§3.4, the nature | `nature_inputs`: each universe of the draw streamed once, its arrays as `fd_1b_mc._single` gives them, a detector universe's tdw rows tdw_ref; compose's order per row; each tree clipped on its own composite (wt⁺, tdw⁺ through `s5p_universe.denominator`, w_reco⁺ and bkg_w⁺, which are λ⁺ since r_T > 0); the truth's flux Φ_u |
| §3.5, the pseudo-data and the unfold | `fd_1b_mc.toy_experiment` on the clipped nature: Poisson at λ⁺ on the toy's stream, the nominal MC with Φ_CV (`with_mc`), set A's MC and template streams; S1's estimator through `fd_1b_mc._unfold`, the toy path 1B used |
| §3.6, seeds | `ll5d`'s constants, unchanged (A1a's tests pin them): the stat realization's and the nulls' seeds per truth and evaluation |
| §4, C_T at each truth | the `central` and `seed` roles (d_T at its means, S1's path, seeds 42 and 45), the 175 `block` items (`fd_1b_mc.compose` of one universe, which is `universe_inputs` bitwise, then `with_mc`), the 50 `stat` items (`fd_1b_mc.stat_experiment` at LL5D's stat seed); `remade` builds every block by S1's procedure over the reading's bands; `removal_control` holds C_T⁽⁻²⁾ against C_T − C_GN − C_GP to 10⁻¹² of max \|C_T\| |
| §5.3, clipcheck | the `clipmean` role (d_T plus each row's mean \|λ⁻\| over the declared draws, from the sealed file, S1's path, as 1B's clipmean was); `clip_offset` (τ_c, o_c); `clipcheck`: TO_JOSEPH at \|o_c\| ≥ 0.667 at any (truth, reading), else PROCEED |
| §6, grading | `null_step` (per reading, the reading's laws, at the evaluation's seed, `check_matched` at 10⁻¹², for C_T and C_T⁻); `readout` with `fd_1b_mc.grade` under A5's tolerance (`cholesky_tol`), the Cholesky reading rule (`reading_rule`), the weakened label (`weakened`), and the flagged-cell clipping-artefact reading with o_c recomputed under C_T |
| §7, readouts | the spread alone against C_e, the bias, the predicted offset of the uncentred draws, the leave-out-MEC grade, the clipping record (o_c, clipped fractions, the fine cells emptied), the realization check (§3c), and the differences between the readings, which describe; neither reading tests the other |
| §9, walls | `walls`: the pilot's 13 products, each unfold within 1,062 s and the RSS limit, else REPRICE |
| §10, controls | the procedure controls (the `control` role, on the data); r_T > 0 on every row; the seed check; the k = 1 and `d_experiment` controls (tests); the removal control; the null's match; the Cholesky reading rule; exactly the declared toys, no partials; O_NOATIME, with exit 8 on an atime move |

The 829 products per truth and the pilot's 13 items are `items` and `PILOT`, tested against §9's counts.

## 3. Named choices

**a. The new module.** `ll5d_b.py` imports `ll5d.py` unchanged. Its `code_digests` records `ll5d.py`'s digests beside
its own, which a test checks.

**b. The clip-prep consumer.**
- `read_clip_prep` reads the sealed file once through O_NOATIME. It requires the sha256 the gate record gives, and
  that each reading holds the declared 300 draws.
- The clipmean divides the per-row sums by 300.
- clipcheck takes τ_c from the clipped and unclipped U·T_D, and records both shifts in absolute units, so the readout can
  recompute o_c under C_T.

**c. The realization check** (§7) is defined here as x̂_T, the central unfold of d_T at its means, against U·T, per cell
in σ_c.
- COV2D's realization check unfolds the stat realization d̃_T itself. LL5D's 227 priced items per truth include no such
  unfold: the stat block bootstraps d̃_T.
- It is descriptive.

**d. The unfold paths.**
- The central value, the seed check, the blocks and the clipmean take S1's path (`fd_1b_mc._unfold_s1`), as 1B's did.
- The toys take 1B's toy path (`fd_1b_mc._unfold`).
- The stat replicas and set A's control take `_unfold_one64`, and the other controls `_unfold_one32`, as in main's
  `fd_1b_mc.run_item`.

**e. k = 1 without a Flux universe** (§10's control on MaRES_0 and GEANT_Pion_0) keeps Φ_CV in the truth, as
`universe_inputs` does. A toy's draw must hold exactly one Flux universe, or the item refuses.

**f. The readout reads three things from A1a's jobs, each by sha256:**
- the gate record, only through `gate_ratios`: its verdict must be PASS, and only r_c is read, behind the `GATE_KEYS`
  allowlist;
- the sealed clip-prep file, in the clipmean and clipcheck only;
- nothing else.

  The bulk's precondition, the gate's PASS, is the connect's to check.

**g. A refusal is INVALID** (§10), written as `<out>.invalid.json` with rc 5, and unrepaired.

## 4. The tests (the declaration's REQUIRED list, A1b's part)

| REQUIRED | test(s) | mutant(s) |
|---|---|---|
| §10's k = 1 control (MaRES_0, Flux_0: all four arrays with the denominator; GEANT_Pion_0: wt, wr, bkgw) | `Nature.test_k1_gives_universe_inputs_arrays_bitwise` | a detector's tdw not tdw_ref |
| the experiment at r = 1 equals `fd_1b_moded.d_experiment`'s bitwise | `Nature.test_the_experiment_at_r1_is_d_experiments` | (the nature's mutants) |
| per-row first order and each tree clipped on its own composite, in both readings | `Nature.test_compose_order_and_each_tree_clipped_on_its_own_composite` | the reference dropped; the truth tree unclipped |
| Φ_u in the truth, Φ_CV in the unfolding (Part 1 §2.1's inherited defect killed) | `Nature.test_the_toys_truth_is_the_receipts_and_takes_phi_u` (the toy's truth also equals A1a's receipt truth to 10⁻¹²) | the truth takes Φ_CV |
| the paired draw and the `minus2` removal | `Unfold.test_each_role_writes_its_arrays` (a `minus2` toy holds neither band); `Pipeline.test_minus2_rebuilds_without_the_two_bands_and_the_removal_is_exact` | a toy ignoring its reading; `minus2` keeping every band; the removal tolerance loosened |
| the stat realization at §3.6's seed | `Unfold.test_each_role_writes_its_arrays` (the seed `stat_experiment` receives) | 1B's stat seed |
| r_T > 0 | `Unfold.test_r_t_must_be_positive_everywhere` | unchecked |
| clipcheck's δ* and its σ proxy | `ClipOffset.*`; `Unfold.test_the_clipmean_adds_the_mean_clipped_mass_and_reads_only_the_sealed_digest` | τ added; δ* strict; the mean a sum; the seal's digest unchecked |
| the walls | `Walls.*` | the unit strict |
| the null per reading at its seed | `Pipeline.test_the_null_is_per_reading_at_the_declared_seeds` | 1B's null seed |
| the Cholesky reading rule's failure modes, and A5's tolerance | `CholeskyRule.test_the_rule_both_ways` (NaN, inf, max_rel_diff > tol, the grade's tol different, no compared values, ndf ≠ 16 exempt), `…test_the_tolerance_is_a5s` (equal to `cov2d_readout.cholesky_tol` at κ₂ ≈ 10¹⁰) | the bound doubled; the grade's tol unchecked; A5 without its factor 10 |
| **the weakened label** (the director's REQUIRED mutants) | `Weakened.test_strictly_below_0_9`; `Pipeline.test_each_reading_takes_its_own_ratio_for_the_weakened_label`; `Pipeline.test_the_weakened_label_moves_no_verdict`; `Pipeline.test_the_gate_record_is_read_only_through_its_allowlist` | ≤; 0.85; 0.95; a wrong evaluation's r_c; the label moving the verdict; another gate key read |
| O_NOATIME | `NoAtime.test_the_clip_prep_the_gate_and_the_products_are_read_with_o_noatime_only` | the seal read plainly |
| INVALID on a refusal | `ExitCodes.test_a_refusal_is_invalid_with_its_record` | a refusal not INVALID |

The other tests cover `Items` (829 per truth, 13 in the pilot), the readout end to end over synthetic products, and
`Module` (A1a imported unchanged, no constant redeclared).

**The fixture.**
- It is A1a's toy world (`test_ll5d.Fixture`).
- The estimator is replaced by a deterministic stand-in (`fake_unfold`). The null and readout run on synthetic products
  written to the declared names.
- The declared seeds are taken from `ll5d`, so no literal of §3.6's range appears in A1b's files, and A1a's
  seed-collision test passes with them tracked. `tests-a1a-with-a1b.txt` shows A1a's whole suite passing.

**Results** (`fd/receipts-ll5d/a1b/`, from a clean checkout):
- `test_ll5d_b.py`: 28 tests, OK, at PYTHONHASHSEED 0, 1 and 2 under numpy 1.26.4, and under numpy 2.4.4.
- `ll5d_a1b_mutation.py`: 26 mutations, all killed. The unmutated control runs all 28 tests, none skipped, rc 0.

## 5. What A1b does not contain

- The pilot's, the bulk's and the readout's connects and sbatch files, including the bulk's lane partition (§9: at most
  22 items per lane). Each comes with its connect's sha256 and the director's go.
- The HPSS copies.

## 6. For the auditor

- **Ruling 4:** grep `ll5d_b.py` for every read of an A1a output. There are three: `gate_ratios`, `read_clip_prep`, and
  the clipmean's metadata check of the clip-prep sha256. Each is by digest.
- **§3c's realization check** is the one place A1b defines a readout the declaration names without defining.
- **The estimator stand-in** means that no test here exercises OmniFold. The pilot's walls and the procedure controls
  are where the real estimator meets this code first.

Nothing is submitted, deposited or tagged.
