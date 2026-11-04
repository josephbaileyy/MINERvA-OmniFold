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
- **Joseph's large-sample gate** (`DECISION-20261104-joseph-1b-large-sample-gate.md`, #740, merged `7d798c3d`).
  This amends #724 after the 300-draw calibration (§8). Per truth, the gate reads the clipped law on a separate
  sample of about 3,000 draws, whose first 300 are the declared draws. (ii) and (iii) are recalibrated by null
  simulation at N to a joint noise-only STOP of at most 1 % over three truths, with (i) fixed. The gate must reach
  80 % power per truth against a uniform 8 % deflation. The large-N law control and linearisation come first. A
  loose backstop runs on the 300 declared draws, and a config hash is shared with the coverage draws.
- **The director's P1–P7 for that decision (2026-11-04, from correspondence):**
  - P1: GATE_N = 3,000. The gate seeds are the declared toys' 300, then GATE_SEED_BASE (G18 3,680,000, AR23
    3,690,000, plug-in 3,700,000).
  - P2: one multiple s on a 0.01 grid from 0.50 to 3.00. (ii) is at s·3.5·SD_ii(N), (iii) by (α) at s·4.3·SD_c(N),
    and the smallest s with a joint union ≤ 1 % is taken. Until the plug-in is calibrated it is projected as the
    mean of the other two, labelled.
  - P3: band_reference is the law's exact variance, so the reference carries no noise.
  - P4: the power is ≥ 80 % per truth against a uniform 8 %. Otherwise N goes to 6,000, then 12,000, each priced to
    the director. Concentrated deflations of 1, 2 and 4 cells at 20, 15 and 10 %, in 16 placements, are reported.
  - P5: the controls at N come first.
  - P6: the backstop is (i) at k = 2 and (iii) by (α) at 4.3·SD_c from the 300-draw calibration; a failure is a hard
    STOP. The config hash is shared.
  - P7: the cap is 1.5 node-h, about 0.7 expected, with a report if the run exceeds 1.0.
- **The bound gate's H1–H3 (the audit's review at `b9bd3158`; the director's rulings):**
  - H1: a hand-written record of the right form passes every field check, so the bulk admits only the record whose
    sha256 binding 3 declares. At `2c882d27` the audit found that a digest held in hashed code would need a sha256
    fixed point. The director ruled a one-line pins file outside every hashed byte, `a2-1/BOUND_GATE.sha256`, which
    binding 3 commits.
  - H2: the calibration, the union, the power, the backstop and the config hash are re-verified at launch.
  - H3: c2check's own record round-trips through the gate.
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
  - `c2_truth`, `c2_block`, `row_match` and `c2check_main`;
  - the large-sample gate:
    - `gate_seeds` (P1);
    - `null_stats`, `stops_at` and `threshold_rule`, which select s (P2);
    - `power_at` (P4);
    - `calibration_verdict_n`;
    - `gate_n`, the gate at the calibrated thresholds;
    - `backstop` (P6);
    - `config_hash` over `gate_code_digests()`, the inputs, the clip rule, the draw salt and the declared seeds.

    c2check refuses a gate sample whose first 300 differ from the declared draws.
- **`fd_1b_cvdenom.py`:** the CV per-row denominator read.
- **`fd_1b_binning.py`:** the director's items 3 and 4.
- **`fd_1b_mc.py`:**
  - S2's bound gate, `check_clip_gate`:
    - under `data`, only `pre_gate_items()` run;
    - under `nature`, only `BULK_ROLES` run, on `c2check`'s record pinned by digest and bound to the run. The
      checks are:
      - its schema, PASS and "option (1)";
      - this truth's reading;
      - the declared seeds;
      - `gate_code_digests()`;
      - the inputs;
      - a calibration digest;
      - (H2) the calibration CALIBRATED and named, its three-truth union measured and ≤ 1 %, its power met, the
        backstop passed at every truth, and the config hash equal to this run's;
    - (H1) the declared digest is read by `bound_gate_sha256()` from `GATE_PIN`. A missing, malformed or different pins
      file refuses. The file's git blob goes into each product's meta (`gate_pin_blob`). No pins file is committed, so
      the bulk refuses today;
    - the stub's three-field file alone refuses;
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
| calibration, G18 and AR23 | `02e71a0b` | job 60771025, nid006700, 02:10–02:32Z | TO_JOSEPH: (b)'s two-truth union 18.9 % (§8) |
| large-sample calibration, G18 and AR23 | `51d67b54` | job 60783756, nid004331, 06:35:57–07:19:12Z | CALIBRATED (G18 and AR23 measured, the plug-in projected), s = 0.92 (§8b) |

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
| `test_fd_1b_mc.py:1759–1763` (amendment 2's receipt test) `_load_world`, `_single`, `load_s1`, `fine_map`, `functional_matrix` | the receipt's loaders | gave a float64 U, so the U defect was invisible | e2e receipt | pass, and refuse without `--cv-tdw` |
| `test_fd_1b_mc.py:747–750` (the toy clip-rule test) `truth_ratio`, `truth_weight` (:747–748), `_weights` (:749), `toy_experiment` (spy, :750) | the toy path | the real truth weight | e2e toy item under both rules through `mc.main` (`test_a_toy_item_under_nature_end_to_end`); one stand-in, the estimator `_unfold` (needs ROOT; A2.1 doesn't change it, and no A2.1 check reads its output) | pass under data and nature; nature without `--cv-tdw` refuses |

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

## 8. The calibration (G18 and AR23; the plug-in after B4 and the capture)

**The design** is as ruled:
- null natures, unclipped and first order, from the streams [CAL_SEED, set, CAL_SALT], which no declared draw shares;
- 10⁴ sets of 300 draws per truth;
- the ratio is var (ddof 1) over the band_reference of the single-universe U·x_T;
- the outputs are the director's (a)–(c), and the power of (ii) against a uniform 10 % deflation;
- the law control (z = 4) and the linearisation (0.02).

**The run.** It was job 60771025: one regular CPU node (nid006700), 2026-11-04 02:10–02:32Z, 21:40, MaxRSS 84.8 GB,
at `02e71a0b`, about 0.36 node-h of the 4.0 cap.
- **Records:** `calib-run/calibration.json` `4b6a18b6…` and `calibration.npz` `a5279bc2…`.
- **Cost guard:** 10,693 fine cells were kept; one set took 0.241 s, projected 1,222 s against 1,287 s actual.
- **Checks:** no atime moved; D8, 0 rows with r < 0; check D, no detector denominator off the CV's.

**The readout** (rates ± binomial SE):

| | (i) | (ii) | (iii) | union |
|---|---:|---:|---:|---:|
| (b) at 2 / 0.07 / 0.35, G18 | 0.26 % | 9.62 % | 0 | 9.65 % |
| (b), AR23 | 0.27 % | 10.16 % | 0 | 10.17 % |
| **(b), two-truth union** | | | | **18.91 % ± 0.39** |
| (c), 3.5 SD and (α), two-truth union | | | | 0.58 % ± 0.08 |

- **(a), the null SDs:**
  - the mean log ratio: 0.0419 (G18) and 0.0426 (AR23), against the consult's independent-cell 0.020;
  - max |r − 1|: 0.039;
  - the per-cell ratio SD: median 0.065, against the analytic 0.082.
- **(ii)'s power against a 10 % deflation:** 78.7 % and 77.4 % at 0.07; 14.6 % and 13.7 % at 3.5 SD.
- **Both controls hold:** the law, max |z| = 2.60; the linearisation, max |mean − 1| = 0.0063.
- **The verdict is TO_JOSEPH.** A three-truth union can't be smaller, so it goes to Joseph without waiting for the
  plug-in (the director, 2026-11-04).
- **The mechanism:** the cells share the same 300 draws, so the mean log ratio carries a fluctuation common to all of
  them. That is cov2d's measured ±0.045 again.

**(ii)'s trade-off curve.** Recorded in `calib-run/tradeoff.json` `415a6f72…` (by `a2-1/tradeoff.py`, 0 compute), with
(i) and (iii) at #724's fixed numbers:

| (ii) threshold | two-truth noise | two-truth power, 8 % | two-truth power, 10 % |
|---|---:|---:|---:|
| 2.0 SD | 9.41 % | 70.4 % | 88.3 % |
| 2.5 SD | 2.65 % | 47.3 % | 71.4 % |
| 3.0 SD | 0.80 % | 26.0 % | 48.7 % |
| 3.5 SD | 0.55 % | 12.6 % | 28.4 % |
| fixed 0.07 | 18.91 % | 83.9 % | 95.1 % |

- **The projected three-truth 1 % point** is 3.16 SD, about 0.133, with 23–25 % power per truth at 10 % and 11 % at
  8 %. This assumes the plug-in behaves as the mean of G18 and AR23, independent of them (labelled; the plug-in is
  not calibrated).
- **The floor:** (i) or (iii) alone stops 0.26–0.27 % per truth.
- **The audit's reading** (arithmetic, an input and not a recommendation): this is a power limit of 300 draws.

## 8b. The large-sample calibration (Joseph's decision of 2026-11-04; P1–P7)

**The design:** the 300-draw calibration's nulls and controls, at GATE_N = 3,000 draws per set, 10⁴ sets per truth,
then the s rule (P2) and power (P4).

**The run.** It was job 60783756: one regular CPU node (nid004331), 2026-11-04 06:35:57–07:19:12Z, 43:15 (2,595 s),
at `51d67b54`.
- **Cost:** 0.721 node-h, against P7's 1.0 report line and 1.5 cap. m3246's uncharged balance went from 2,036.5 to
  2,035.8 (iris).
- **Records:** `calibN-run/calibration.json` `d4a4739e…` and `calibration.npz` `9047a6f7…` (committed at `20b5fab6`).
- **Cost guard:** one set took 2.52 s, projected 2,043 s against 2,565 s actual.
- **Checks:** no atime moved among 709 files; D8, 0 rows with r < 0; check D, no detector denominator off the CV's.
- **Peak memory:** the python process peaked at 10.0 GB (`time -v`). The batch step's MaxRSS was 131 GB.

**The readout:**

| | G18 | AR23 |
|---|---:|---:|
| law control, max \|z\| (against 4) | 2.11 | 1.85 |
| linearisation, max \|mean r − 1\| (against 0.02) | 0.0058 | 0.0055 |
| SD_ii, the mean log ratio's null SD | 0.01329 | 0.01354 |
| SD_c, per cell, min to max | 0.0161–0.0251 | 0.0160–0.0251 |
| (ii) threshold at s = 0.92 | 0.04278 | 0.04361 |
| (iii) by (α), at s·4.3 | 3.956 SD_c | 3.956 SD_c |
| noise-only STOP at s = 0.92 | 0.34 % (34 / 10⁴) | 0.26 % (26 / 10⁴) |
| power, uniform 8 % (≥ 80 %) | 99.68 % | 99.70 % |
| power, 4 cells at 10 %, min / mean over 16 placements | 96.2 % / 98.1 % | 96.0 % / 97.8 % |
| power, 1 cell at 20 % and 2 cells at 15 % | 100 % | 100 % |

- **s = 0.92** is the first grid point whose projected three-truth union is at most 1 %: 0.897 %, against 1.076 %
  at 0.91. The projection is labelled: "the plug-in's per-truth rate as the mean of the others', independent".
- **The measured two-truth union** is 0.59 % ± 0.08, per replicate. The audit's product of the marginals is 0.599 %.
- **(i) alone** stops none of the 2 × 10⁴ sets at N.
- **#724's fixed numbers at N:** union 0 at both truths. That is (b) at N, for comparison with §8.
- **Reproduced:** `threshold_rule` on the npz gives the record's s, grid and thresholds exactly, both locally and by
  the audit.
- **Not citable as a bulk admission.** `check_clip_gate` refuses a record whose three-truth union is not measured.
  The plug-in's calibration after B4 and the P1 capture is required, and s may move then.
  <!-- absence-ok: states check_clip_gate's refusal rule (fd_1b_mc.py:954 at 48ca04a1) and this record's own field ("three_truths_measured": false, calibN-run/calibration.json:5674 at 20b5fab6); the plug-in's calibration is declared to follow B4 (§1, P2), so no result is claimed absent -->
- **Sampling sensitivity (the audit, for information).** The margin is about one SE, so another seed set could
  plausibly pick 0.91 or 0.93. A split-half check shows no systematic in-sample optimism: G18 0.42 → 0.28 %, AR23
  0.24 → 0.26 %. The rule is a point-estimate rule, as ruled. The director carries this to Joseph as reported, not
  adjusted.

**The rerun at the final code (the director's ruling).** fd_1b_mc.py changed after `51d67b54`: H1 (`48ca04a1`), then
§10's resume check, the `nature` readout and clip_draw's two `nature` arrays (`8a9b8db9`, sha256 `5271782c…`). An AST
diff against `51d67b54` finds 12 changed or new definitions, and none is reachable from the calibration's calls into
fd_1b_mc. fd_1b_c2.py is unchanged (`f19adbda`). So the calibration reruns at the code binding 3 binds, with the same job script
(`sbatch-calibrate.sh` `a12799a4`) and the same seeds. `a2-1/compare_calibN.py` holds the rerun to `d4a4739e…`:
- `--old` must hash to job 60783756's record;
- the npz must be bitwise equal;
- the JSON must be canonical-equal after deleting exactly the pre-declared environment paths (listed in
  `calibN-keys.txt`), with the new fd_1b_mc.py digest checked against its expected value;
- the verdict line must be equal byte for byte.

Any other difference is a STOP to the director.

## 9. Tests and mutation (to come)

The owed mutation work, going into A2.1's receipt:
- the mutant that restores the absolute-tolerance U check;
- re-anchoring `mutation_mc.py:69/82` and `mutation_mc_a2.py:81/94`;
- mutants for #724 (i)–(iii), in both directions.

## 10. The stage 1 tables under S2 (the director's ruling (A), 2026-11-04)

**The question,** left to A2.1 by amendment 2: how S1-0's and S1-0b's graded items, which run under `data` before
the gate, relate to a `nature` bulk. `refuse_mixed_estimator` (`fd_1b_mc.py:1383`) refuses a truth whose products
mix clip rules, so `data` products cannot enter a `nature` grading.

**The ruling.** The `nature` bulk carries every graded item, so the graded set equals the declared one. That
includes the 5 graded items S1-0 and S1-0b run under `data`:
- without the plug-in: G18's central value and toy 3,620,000, AR23's stat replica 1, toy 3,630,000 and central value;
- with the plug-in: G18's central value and toy 3,620,000, AR23's stat replica 1 and central value, the plug-in's
  central value.

Their `data` products stay S1-0's checks and S1-0b's descriptive figure, and are never graded. The clipmeans, the
procedure controls and the capture are S1-0's and S1-0b's alone.

**The generator** (`stage1/tables/make_stage1_tables.py`, now with named arguments):
- s1-0 and s1-0b run under `data`, and the bulk under `nature`;
- every unfold and the receipt carry `--cv-tdw` with `0bc70d62…`, under (e2);
- every bulk step carries `--clip-gate` and `--expect-clip-gate-sha256`;
- no bulk table is written unless that digest is the record in `fd_1b_mc.GATE_PIN` (read by `bound_gate_sha256`), and
  the pins file is committed at the checkout's HEAD exactly as it stands on disk.

**The counts:**

| | items | one-node jobs | slots (8 lanes × 22) | most per lane |
|---|---:|---:|---:|---:|
| bulk without the plug-in | 1,054 (1,049 + 5) | 6 | 1,056 | 22 |
| bulk with the plug-in | 1,581 (1,576 + 5) | 9 | 1,584 | 22 |

**The price is unchanged.** The bulk stays at 9 jobs of 8:00:00, 72.0 node-h, because 1,581 ≤ 1,584. Amendment 2's
exposure stays 76.0 (§11 there: the receipt ≤ 2.0, S1-0 1.0, S1-0b 1.0, the bulk 72.0).

**The exposure against the director's 81.0.** The 81.0 is 76.0, plus P1's capture (about 1), plus the 300-draw
calibration's 4.0 cap. With the jobs since then at their measured cost, and the one still to run at its cap:

| item | node-h |
|---|---:|
| amendment 2 (receipt, S1-0, S1-0b, the bulk with the plug-in) | 76.0 |
| P1's capture (estimate) | ≈ 1.0 |
| 300-draw calibration, job 60771025 (21:40) | 0.361 |
| large-sample calibration, job 60783756 (43:15) | 0.721 |
| its rerun at the final code (cap) | 1.5 |
| **total** | **≈ 79.58**, within 81.0 by 1.42 |

The CV denominator reads and the binning runs ran on login nodes, at 0 node-h. **Not yet priced:** c2check at N
(G18 and AR23, then the plug-in) and the plug-in's large-sample calibration. Binding 3 gives an estimate for each,
based on 60783756's measured timings, and sets the total with the arithmetic shown. If it lands above 81.0, the
director sets the new total there and reports it to Joseph (the director, 2026-11-04).

**The path collision (the audit's finding at `1295f7e4`; the director's rulings).** Product names carry neither the
rule nor the estimator (`product_name`), and `run_unfold` skipped any existing target. So the five re-run items would
have written onto S1-0's and S1-0b's `data` products, unfolded nothing and exited 0. Only the readout would then have
refused (`refuse_mixed_estimator`), after the whole bulk had been spent. Two fixes, both ruled:
1. **Each rule and estimator gets its own directory:** `{W}/stage1/unf/<rule>-<estimator>/` (`unfolds_dir`). The
   product names are unchanged, so none of their consumers in `fd_1b_mc` changes. Each works within one
   `--unfolds` directory:
   - `run_unfold`, `pilot_walls`, `_cells`, `readout`'s plug-in control and the `walls` command build names with
     `product_name`;
   - `clipcheck`, `clipping_readout` and `clipping_readout_nature` glob `{tag}_{truth}_clipmean_*`;
   - `refuse_mixed_estimator` and `refuse_partials` glob `{tag}_{truth}_*`;
   - `toy_paths` globs `{tag}_{truth}_toy_*` and parses the seed with `rsplit("_", 1)`;
   - `products_digest` globs `{tag}_{truth}_*` and parses the role with `split("_")`.
2. **`resume_matches`.** An existing product is skipped (a resume) only if its meta matches the step's estimator,
   clip rule, CV tdw digest and gate config hash. Any mismatch refuses. The product meta now records
   `cv_tdw_sha256` and `gate_config_hash`.

**The readout's clipping section under `nature` (the director's ruling (iii), extended).** It is descriptive, for the
note, and changes no graded quantity. `clipping_readout_nature` reports three parts, each labelled with its rule:
- (a) the graded toys' own `nature` clip facts:
  - per component (signal, background, denominator, truth), the clipped fraction over toys;
  - per reporting cell, the median and max over toys of U applied to the pseudo-data's, the truth's and the
    denominator's clipped mass. clip_draw now writes `clip_truth_nature_flat` and `clip_denom_flat` under `nature`.
- (b) c2check's per-cell residual R (option (1), sigma_Q) and clipped-truth mean shift at N, from the gate record
  that binding 3 pins, read by `read_bound_gate`. That helper is now shared with `check_clip_gate`.
- (c) S1-0b's `data` offset o_c, from `--data-unfolds`, with σ_c from this grading's C_T, labelled "the data rule's
  offset, for reference; not the graded rule".

A `nature` readout refuses when:
- `--data-unfolds` is missing, is the graded directory, or holds a product that is not `data`;
- the gate record is not the bound one.

The C4 refusal at the readout is replaced by this. The C4 refusal still stands at `clipmean` and `clipcheck`.

**The tests:**
- `tests/test_fd_1b_tables.py`, 5 tests:
  - the `nature` bulk's graded set equals the declared set exactly, per truth: the central value, the seed check,
    175 blocks, 50 stat replicas and 300 toys (527 per truth, from the declaration's constants);
  - every generated step passes `fd_1b_mc`'s own parser with its rule, the CV tdw and, for the bulk, the gate pair;
  - the lane and node packing;
  - over every table, with and without the plug-in, no product path is shared between the rules, and each rule writes
    only to its own directory. The five re-runs share a name across the rules but not a path;
  - the bulk refuses without a pins file, with an uncommitted pins file, with one changed on disk, and with another
    record's digest. With no gate given, no bulk is written.
- `test_fd_1b_mc` `Jobs.test_a_resume_skips_only_its_own_product`: a matching product is skipped and left bitwise
  unchanged; another estimator, clip rule or gate config hash refuses; no refused step unfolds.
- `Pipeline.test_the_clipping_readout_under_nature`: null_step and readout end to end on rule-directory products.
  Each of (a)–(c) is checked against the fixture's own parts, and each refusal fires.
- The `nature` arrays are checked in clip_draw's unit tests: the truth clip's array sums to cov2d's own clipped sum,
  and the denominator's sits in its row's cell. They are also checked in the e2e toy item, where the truth clip is
  exercised (7 rows).
- `test_a_negative_composite_denominator_row_end_to_end` (the director's request) exercises the denominator clip
  end to end through `run_unfold`:
  - On a copied bank, two drawn universes' tdw are lowered on one row. Every universe's tdw stays ≥ 0 and the CV's is
    untouched, so the composite row is negative (−0.52) and its cell stays positive.
  - The record shows 1 negative row at the composite's value.
  - `clip_denom_flat` holds exactly the row's mass, in its cell only; that is what the readout's (a) aggregates.
  - The toy truth at that cell moves by (D − d_row)/D to 10 places, with D the composite cell, and no other cell
    moves beyond those the truth clip touches.
  - The composite is computed from the files, with detector universes bringing the CV's rows.
  - The toy World's weights are `hash()`-seeded (`test_fd_1b.py:106`, `:114`), so the fixture moves with
    PYTHONHASHSEED. The test therefore chooses the clipped cell among those the truth clip leaves alone, measured on
    the world's own bank first, and asserts the truth clip is unmoved by the tdw edit. It passes at seeds 0–4. The
    first version picked a fixed cell; it failed at seed 0 (the harness's) and passed without a seed.
  - Both of the director's mutants are killed by this test alone, at seeds 0 and 1, each because the clipped cell's
    truth no longer moves between the rules:
    - "S3: the denominator not clipped";
    - "S3: the denominator clipped under 'data' too", which is new in `mutation_a21.py` (319 mutants).
- **The generator on a fresh clone** (`a2-1/tables_clone_check.py`, the audit's Q3 and the director's request; local,
  0 compute):
  - It clones the repository at the given revision and commits a stand-in pins file at the clone's own `GATE_PIN`
    (local only).
  - It runs `make_stage1_tables.py` through its real CLI as a subprocess, and parses every written step with the
    clone's own `fd_1b_mc` parser in a second subprocess.
  - It checks the counts and the packing, that no path is written twice or under two rules, the rule directories,
    the gate pair on every bulk step and on no other, and the CV tdw pair everywhere.
  - At `abf95aed` it passes: s1-0 8, s1-0b 3/5, bulk 1,054/1,581 on 48/72 lanes, at most 22 per lane, 5 names in
    both rules and 0 shared paths (`tables-clone-check-abf95aed.out`).
  - At `1295f7e4`, before the fix, it fails: in each setting 5 paths are written twice and a path appears under both
    rules (`tables-clone-check-1295f7e4.out`).

"23 per lane" is equivalent on the declared inputs, and its output is byte-identical.
