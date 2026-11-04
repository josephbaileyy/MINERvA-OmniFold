# 1B staged, addendum A2.1 to amendment 2: Joseph's clip rule through C2's code, the 16-cell variance gate, and its calibration

**Status: a draft declaration, in progress.** It is on branch `decl/1b-staged-a2-1-20261103`, from #717 at
`fea7946a`. Sections marked **(to come)** are not written yet. Nothing in it is bound, and binding 3 waits on B4
(#714) for everything that depends on the estimator.

**MEASURES:** the code, the runs and the measurements listed in §6. **CANNOT AUTHORIZE:** a launch, a threshold, a
change to S1, or a verdict on 1B's coverage.

## 1. The rulings it implements

- **Joseph's clip rule (#718, merged `1e74f819`).** The bulk runs `nature` only if 1B's own pre-bulk check reads
  "option (1)" under C2's fixed reading (`c2_reading.txt`, `b5b4fc4b…`), computed with cov2d's code. Any other
  reading is a hard stop.
- **Joseph's variance gate (#724, merged `20b86dac`).** Per truth, C2's clipped-composition variance ratio passes
  only if:
  - (i) at most 2 of the 16 cells have |r − 1| > 0.20;
  - (ii) |mean log r| ≤ 0.07;
  - (iii) max |r − 1| ≤ 0.35.

  The calibration comes first.
- **The director's rulings of 2026-11-03 and 2026-11-04, from correspondence:**
  - #724 applies to the clipped ratio, and the multiplicative ratio is descriptive.
  - The calibration reports (a)–(c), with (c)(iii) = (α), and (β) and (γ) descriptive.
  - The receipt counts as examination, so the calibration is committed first.
  - P1, with Q2: G18 and AR23 are calibrated now, and the plug-in after B4 and the capture.
  - R2: one compute node.
  - D1(b): the gate measures 1B's own x_T.
  - S3 (d1), with the float32 rule (e2) and B's attribution rule.
  - W1: the law control is hard at z = 4, and the linearisation tolerance is 0.02.
  - The nominal basis question is ruled; see §4.
  - The U check is a fix to bound code; see §5.

  Each ruling is quoted where it is used.

## 2. The code (to come in full)

- **`fd_1b_c2.py`:**
  - `gate_724`;
  - `reading_1b`, which equals `clip_probe2.reading` under C2's gate over an edge grid of more than 20,000
    records; it reads option (1) ⟺ q1 ∧ bounded;
  - `band_reference`, with the layout as a parameter;
  - `xt_flat` and `xt_packed`, which equal `true_xsec` bitwise;
  - `prepare`, shared by the calibration and `c2check`;
  - the calibration job;
  - `c2_truth`, `c2_block`, `row_match` and `c2check_main`.
- **`fd_1b_cvdenom.py`:** the CV per-row denominator read.
- **`fd_1b_binning.py`:** the director's items 3 and 4.
- **`fd_1b_mc.py`:**
  - C2's `nature` rule in `clip_draw`;
  - the denominator's row clip;
  - (e2) in `compose` and the receipt;
  - `same_functional`;
  - `truth_weight`'s install.

## 3. The named departures from C2's literal quantities (to come in full)

- **D1(b).** The gate's truth is 1B's graded x_T, not C2's denominator-tree count. The m_all analogue is signed.
  R subtracts a reco-side count fraction from an x_T-relative fraction.
- **The denominator's row clip is on tdw_D's own sign.** The denominator is not r-weighted, so this is 1B's rule,
  where C2 clips on w_truth·r·s. The two agree where r ≥ 0, and D8 names the rows where r < 0.
- **(e2).** d_CV := hist_f32(tdw_CV), and each detector universe's denominator is the same, under both rules. This
  departs from the npz's `denom_nd` in 32 of 65,856 cells, attributed to 16 rows.
- **The bank's tdw files are pinned by size and mtime against the pins file.** That is `toys.check_pins`'
  convention for the bound bank, and weaker than a sha256 of the bytes.

## 4. The nominal basis (the director's ruling, 2026-11-04)

- **The ruling.** The central values and the stat role stay on the npz's float64 `denom_nd`. The toys' composites
  use (e2)'s float32.
- **The measured gap,** binning3-run `binning.json` `726a0f4c…`: at most **3.67e-5 σ_c**, in R7. It comes from row
  7,692,246 (R3→R7, weight 0.180). This is a named, measured departure, carried to the note with the clipping facts.
- **σ_c** is S1's reported `C_total_plus_C_resp`, a proxy for C_T. Binding 3 carries that record (D6). Until then
  the citation is the director's message.

## 5. Fixes to bound code

- **The U check.** S1 stores U as float32 (`s1_assemble.py:370`). U's entries reach 3.69e7, and float32 rounding
  moves them by up to 0.050, so `np.allclose(U, s1["U"], rtol=0, atol=1e-6)` refuses every real assembly.
  - **The fix:** one helper, `fd_1b_mc.same_functional`, exact equality in float32 (as `build_cresp.py:139` already
    checks).
  - **The sites:** the search (`git grep -n "s1\[.U.\]\|allclose(U" -- nd-unfolding`, with its output in
    `fd/receipts-1b/staged/a2-1/u-check-grep.txt`) found six:
    - amendment 2's receipt, clipcheck, null_step and readout (`fd_1b_mc.py:959`, `:1110`, `:1274` and `:1381` at
      `fea7946a`);
    - binding 2's null_step and readout (`:733` and `:789` at `24c83ab8`);
    - `fd_1b_binning` and `fd_1b_c2.c2check_main`.
  - **Nothing already produced is affected.** None of the bound sites ran on real data: binding 2's stage-1 receipt
    had no U check, and null and readout are post-bulk.
  - **Binding 3 re-pins those files.**
- **`truth_weight` installs `s5e_deform`'s `ratio_nd` itself.** The bulk installs it in `run_unfold`. A2.1's jobs
  don't call `run_unfold`, and fell through to `ValueError("ratio_nd")`. The install is idempotent, so the bulk path
  is unchanged.

## 6. Runs so far

All runs used a fresh clone at the bound commit, with its sha verified on the node, and moved no atime.

| run | commit | where, when | outcome |
|---|---|---|---|
| CV denominator read, 1 | `435d8957` | login02, 2026-11-03 22:03–22:19Z | TO_DIRECTOR on B's bitwise rule (32 cells, float32 binning). No weights written. |
| CV denominator read, 2 (e2) | `5e1162ff` | login23, 23:25–23:27Z | PASS. 16 moved rows attribute all 32 cells. `cvdenom.npy` `0bc70d62…`; record `156b963d…` kept on pscratch. |
| binning, 1 | `e7641a9b` | login23, 23:44Z | refused at the float32-U check, before measuring anything |
| binning, 2 | `663a7609` | login23, 23:54Z | `ValueError("ratio_nd")`, before measuring anything |
| binning, 3 | `917907aa` | login23, 2026-11-04 00:02–00:03Z | items 3 and 4 measured (§4; the director's message of 2026-11-04) |

## 7. The mock audit (the director's request, 2026-11-04)

Two refusals in a row came from defects the tests couldn't see, because they mocked a production function. Both
refused good inputs, and the suite had tested only the refuse direction. So this audit lists every stand-in in
A2.1's tests that replaces a production function, what it hides, and whether an unmocked end-to-end test now covers
that function, with the directions tested. It also covers the one-off scripts' import and install paths.

**The unmocked end-to-end suite,** `nd-unfolding/tests/test_fd_1b_a21_e2e.py`, runs on a toy world written
consistently to disk:
- `cv.npz`'s `td_*` rows;
- `denom_nd`, their histogram at CV weight 1;
- the bank's tdw within 2 %, crc32-seeded;
- the detector denominators equal to the CV's;
- a staged flux table and S1 assembly;
- regenerated pins.

It runs `calibrate_main`, `c2check_main`, `fd_1b_binning.main` and `fd_1b_mc.receipt` through the production loaders:
`_load_world` with its digest and pin checks, `verified_weights`, `_single`, `truth_ratio` on the toy F1 prep,
`truth_weight` with its install, `fs.load_s1` and `fs.reported_matrix` on the committed data product.

Its only stand-ins:
- `World.patches()` and the S1 assembly's digest, which are constant re-pins to the toy files, as every 1B job test
  does;
- `sa.fine_map` and `sa.functional_matrix` (`test_fd_1b_a21_e2e.py:101–102`), because the committed H2 definition
  is built on the real 65,856-cell grid and can't map the toy's 48 cells. Their real form is covered by
  `test_fd_1b_mc.py` `Functional.test_the_real_definitions_u` on the committed definition.

| stand-in (file:line) | replaces | what it hides | unmocked end to end now | directions tested |
|---|---|---|---|---|
| `test_fd_1b_c2.py:394` `mc._load_world` | the world loader | the digest checks, the pins, the CV-tdw load | e2e calibration, c2check, receipt | pass on good: e2e. Refuse without `--cv-tdw`: e2e receipt, and the mocked calibration `Job` |
| `test_fd_1b_c2.py:394` `mc._single` | per-universe arrays | the real denominators, Flux Φ_u | e2e (all three) | pass: e2e. Detector ≠ CV refuses: the mocked calibration `Job`, and `compose`'s own tests |
| `test_fd_1b_c2.py:395`, `test_fd_1b_binning.py:123`, `test_fd_1b_a21_e2e.py:101` `sa.fine_map` / `functional_matrix` | the H2 map | the real U's magnitudes (this hid the float32 defect) | no: the toy grid can't take it. The real definition's U is tested directly (`Functional`), both ways | real U passes the new check and fails the old; one ulp off fails both |
| `test_fd_1b_c2.py:396–397`, `test_fd_1b_binning.py:126–127` `mc.truth_ratio` / `truth_weight` | F1's ratio truth | s5e_deform's install (this hid `ValueError("ratio_nd")`) | e2e (all three), and `TruthWeight` on a freshly reloaded `s5n_pseudo` | pass on good; the e2e G18 and AR23 single_x differ |
| `test_fd_1b_binning.py:122` `inv.load_inputs`; `:124` `via_noatime`; `:125` `reported_matrix` | loaders | the real npz keys, the data product's f check | e2e binning | pass |
| `test_fd_1b_binning.py:128` `TOY_SEEDS` | the declared draws | the 300-draw loops | e2e binning (all 300 per truth) | pass |
| `test_fd_1b_cvdenom.py:300` `uproot` (a stand-in module) | the ROOT read | uproot's own reading | no: there is no toy ROOT file, and uproot can't write the TParameter POT objects. The two real runs (§6) are the end-to-end evidence | both: TO_DIRECTOR (run 1), PASS (run 2) |
| `test_fd_1b_cvdenom.py:143`, `:264`, `test_fd_1b_binning.py:84` `NOATIME` / `NOATIME_FLAG` | the O_NOATIME flag | macOS lacks the flag | the node runs used it; `atime_moved` was [] in every run | n/a |
| `test_fd_1b_c2.py:186` `CAL_SALT` | a constant | none (a refusal test) | n/a | refuse at 0 |
| `test_fd_1b_mc.py:1720` (amendment 2's receipt test) `_load_world`, `_single`, `load_s1`, `fine_map`, `functional_matrix` | the receipt's loaders | gave a float64 U, so the U defect was invisible | e2e receipt | pass, and refuse without `--cv-tdw` |
| `test_fd_1b_mc.py:749–752` (the toy clip-rule test) `truth_ratio`, `truth_weight`, `_weights`, `toy_experiment` (spy) | the toy path | the real truth weight | e2e toy item under both rules through `mc.main` (`test_a_toy_item_under_nature_end_to_end`); one stand-in, the estimator `_unfold` (needs ROOT; A2.1 doesn't change it, and no A2.1 check reads its output) | pass under data and nature; nature without `--cv-tdw` refuses |

**Job functions without an unmocked end-to-end test, with the reason:**
- `clipcheck`, `null_step` and `readout` need S1-0b or bulk products, which the toy world doesn't produce. Their A2.1
  change is the U check through the one tested helper.
- `run_unfold`'s toy item, under `nature` with `--cv-tdw`, is now covered end to end (the row above), as the
  director required before binding 3.

**The one-off scripts' import and install paths:**
- **`connect-cvdenom.sh`** runs in `omnifold_py310`, with uproot and no ROOT. `fd_1b_cvdenom.py` imports only NumPy
  and uproot, and restates the two writers' row gates. Those restatements are checked on the real files by A and C
  (row by row, and bitwise), and against `u2d.in_truth_phase_space` by a ROOT-only test, which runs in root_6_28
  before binding 3.
- **`connect-binning.sh` and the calibration** run in the 1B jobs' environment (`setup_salloc_env.sh`, Python
  3.11), and import `fd_1b_mc`, `fd_1b_c2` and `fd_1b_score` as the jobs do. Their one divergence from the bulk
  (no `run_unfold`, so no `s5e_candidate.install`) is now covered inside `truth_weight`. They install no estimator,
  since they unfold nothing.

## 8. The calibration (to come in full)

- **The design:** §5 of the design record, as ruled.
- **The job:** `fd/receipts-1b/staged/a2-1/sbatch-calibrate.sh` and `connect-calibrate.sh`.
- **The price** (an estimate):
  - one CPU node, QOS regular, `--time 4:00:00`, which is 2× a 2 h estimate. The basis: stage 1's receipt read the
    same universe files in 1:26:25 on a login node, and 2 × 10⁴ sets at about 2.1 s each, measured locally on
    63,168 cells, over 64 workers is about 11 min;
  - the job measures one set on the real fine-cell count before the pool, and refuses if the projection passes its
    13,500 s budget;
  - **the exposure:** at most 4.0 node-h, added to amendment 2's 76.0 with P1's capture (about 1 node-h).

## 9. Tests and mutation (to come)

The owed mutation work, going into A2.1's receipt:
- the mutant that restores the absolute-tolerance U check;
- re-anchoring `mutation_mc.py:69/82` and `mutation_mc_a2.py:81/94`;
- mutants for #724 (i)–(iii), in both directions.
