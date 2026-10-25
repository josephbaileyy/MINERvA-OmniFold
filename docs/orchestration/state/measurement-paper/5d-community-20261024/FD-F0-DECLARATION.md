# DECLARATION F0: re-grade of the existing (e) fake-data products on the 16 H2 cells (2026-10-25)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's approval, [`DECISION-20261025-joseph-approve-5d-fd-f0.md`](../../../DECISION-20261025-joseph-approve-5d-fd-f0.md)
  (PR #354, main `f1cd6487`);
- the plan, [`FD-PLAN.md`](FD-PLAN.md) §§3 and 5.2 (PR #352, `a54a10be`);
- every ruling in [`FD-DIRECTOR-RULINGS.md`](FD-DIRECTOR-RULINGS.md) (PR #353, `9e84f797`).

**Declares:**
- the tool `nd-unfolding/fd_f0_regrade.py` and its tests `nd-unfolding/tests/test_fd_f0_regrade.py`;
- the exact argv, the interpreter and how the deploy is pinned;
- the order of the HPSS copy of the 80 `f4` products and the re-grade;
- the readout schema.

**MEASURES:** nothing. Neither the tool nor the HPSS copy has run.

**CANNOT AUTHORIZE:**
- running anything: the director binds first (decision item 2);
- Stage G, F1, F1-W or any cell merge, none of which is approved;
- a claim, printed wording or a publishability conclusion, which are Joseph's.

**CITABLE FOR:**
- what F0 will compute, from which inputs, in which order, and what makes it stop;
- the readout's schema, and the guard that keeps f, absolute cell values and f − g out of every output;
- the synthetic tests, and what each one shows.

**NOT CITABLE FOR:**
- any result: none exists;
- any authorization to run.

## 0. Summary

- **What it does:** F0 re-grades 18 truths on R00–R15 against S1's C_total, as FD-PLAN §3 declares. It reads 8,545
  existing products and no new unfold.
  - The tests are S-1, per-cell pulls, and S-2, the χ² with ndf 16. A vertex-family truth is graded with its own
    vertex left out of C_model.
  - Beside each grade it prints the in-sample, sensitivity, model-only and GiBUU eight-cell variants. All of them are
    descriptive.
  - Row 6 is offset-corrected, and controls 0–8 run first.
- **Cost:** 0 node-h. Everything runs on a login node, with no Slurm job.
- **Storage:**
  - HPSS gets the 14,738,583 B of `f4` products, plus tar headers.
  - pscratch gets under 10 MB.
  - Nothing goes to CFS.
- **The order:**
  1. deploy, with the tests in the deploy;
  2. the HPSS copy, whose first step is control 0 against the committed inventory;
  3. the re-grade, which repeats control 0 against the D16 records and then runs controls 1–8;
  4. the report.
- **Stop rule:** any refusal, any non-zero exit, or any step past 1.25 × its projected wall is reported unrepaired.
- **Ruling 6 is enforced in code.**
  - Every line printed after the cell integrals are formed, the readout JSON and the per-experiment table all pass a
    leak guard before anything is written (§5.3).
  - The tests show that it fires on each forbidden form and stays silent on a correct run, in physical units and in
    O(1) units (§6).
- **Departures from the plan's letter** are listed for the director in §7. Two matter:
  - Control 6's bound "≤ 3.2e-5" is a rounding of the recorded 3.218e-5, so it would fail as written.
  - The per-experiment table holds relative residuals only, not absolute integrals.

## 1. Inputs

`P=/pscratch/sd/j/josephrb`. Every input below is checked against the sha256 shown, or against the record named,
before it is used. The checks are controls 0 and 1.

| input | where | checked against |
|---|---|---|
| H2 definition | `$D/nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b6790761…` and its fine map `930326a3…` (`s1_assemble.fine_map`) |
| S1 assembly | `$P/s1-20261024/s1_assembly.npz` | `db000707…`, which the committed `s1_assembly.json` names (`assembly_sha256`) |
| S1 readout | `$T/s1/readout/s1_assembly.json` | `81e5ef3f…` |
| C_model,5D | `$P/cmodel5d-20261024/out/cmodel_5d.npz`, key `S` | `3008d8f6…` (`BUILD-REPORT.md:94`) |
| C_model,5D readout | `$D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json` | `3cfdc6a5…` |
| NuE constraint | `$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d2…` (`s1_assemble.flux_weights`, S1's choice 10) |
| row 1: s5e assessment, 120 products | `$P/s5e-20260925/runs/cand/assess/{nominal,W1,W2,W3,q3}/` | `5d-design-20261023/stage0/INVENTORY.sha256` `267c6c7c…` |
| row 2: Stage 0c GiBUU, 20 products | `$P/5d-stage0-20261023/runs/new_gibuu/` | `stage0/receipts-A/products.sha256` `e7148c9d…` |
| row 3: closure at NuWro, and its floor | `$P/pv-ladder-20261024/products/L-5D-PV_e_closure_{nuwro,tune_v1}.npz` | `fff9030e…`, `eb3e2188…` (`cmodel_5d.json` `inputs.products_sha256`) |
| row 4: A7 `f4`, 80 products | `$P/s5p-20260926/runs/s3r/f4/<truth>_half/` | `state/s5p/stage3/f4/D16-<truth>.json` `inputs[].a_sha256`; the five D16 files are pinned in the tool |
| rows 5–6: A7 calibration (7,176) and power (1,147) | `$P/s5p-20260926/runs/prod/{cal,pow}/<set>/` | `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` `1a72cb43…` |

- **The truths' identities** are checked in each product's meta (control 2) against digests pinned in the tool.
- **A test checks those pins against the committed files** (`CommittedPins`):
  - the hypothesis files in `state/s5p/ratios/null{sJ,sF}/` (`ceea00e7`, `8c37f545`, `9033c952`, `9297a698`,
    `0080495c`);
  - the alternatives in `ratios/altR/` (`9240e4b3`, `6a36c9bc`, `b3108969`);
  - the W1–W3 ratios (`2a208df9`, `80e16f95`, `3455daf3`) and Stage 0c's (`c001dce8`);
  - the closure's ratios, in `pv-ladder/prep-SHA256SUMS` (`38e47eb6`, `13bb1eae`).
- **Volume read:** about 1.6 GB.

## 2. Exact commands

**Definitions:**
- `B=$P/fd-f0-20261025`. It does not exist yet (checked on login37, 2026-10-25).
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit, which the binding names.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"`. That interpreter is Python 3.11.14 with numpy
  1.26.4 and scipy 1.16.3 (login37, 2026-10-25).
- **Every Python command carries `-B`,** the S1 `.pyc` lesson (`S1-REPORT.md` §1). The tool is also run with `-I`, so no
  cwd or user-site module can shadow its imports.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_f0_regrade.py nd-unfolding/tests/test_fd_f0_regrade.py nd-unfolding/s1_assemble.py \
    nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/F4-PRESERVE-INVENTORY.sha256 \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F0-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_f0_regrade test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after the tests;
- the §8 digests;
- `tests rc=0` with "OK";
- the expected count: 60 tests locally on 2026-10-25, of which 38 are in `test_fd_f0_regrade`.

Anything else is a STOP.

### 2.2 The HPSS copy of the `f4` products (login node, after §2.1)

This is the committed Stage 0 preserve script, unchanged. Its first step, `sha256sum --quiet -c` of the committed
inventory, is **control 0 in its shell form**.

```bash
cd $B && setsid nohup bash -c "timeout 1500 bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
  $T/fd/F4-PRESERVE-INVENTORY.sha256 $B/preserve /home/j/josephrb/mnv-5d-fd-f4-20261025; echo rc=\$?" \
  > $B/logs/preserve.out 2>&1 < /dev/null &
# PASS = the last line "rc=0" in $B/logs/preserve.out and "[P] ... PASS: HPSS copy verified ..." in $B/preserve/preserve.log
```

- **The inventory:** `fd/F4-PRESERVE-INVENTORY.sha256`. It has 80 lines, `a_sha256  a`, taken from the five D16
  records in tool order. A test checks that it equals `fd_f0_regrade.f4_inventory_lines` over the committed D16 files.
- **What the script does:**
  - one uncompressed tar of exactly those paths;
  - `hsi put`, `hashcreate` and `hashverify`;
  - a retrieval with `hsi get`, compared to the tar by sha256;
  - removal of the retrieved copy only.
- **Exit codes:**
  - 0 is PASS;
  - 3: an input no longer matches its D16 digest, which is control 0 failing;
  - 4–8: tar, put, hashcreate, hashverify, get or compare failed;
  - 124: past 1,500 s.
  Any non-zero exit is a STOP.
- **Projected wall:** 20 minutes. The timeout is 1,500 s, which is 1.25 × that.
- **Space:**
  - on HPSS, 89.2 GiB is free (`hpssquota`, 422.78 of 512.00 GiB used, 2026-10-25), and the copy needs about 15 MB;
  - pscratch needs room for two 15 MB tars.
- **Names:** the script calls its tar `stage0-inputs.tar` and its inventory copy `INVENTORY.sha256`. The HPSS
  directory name identifies this copy, as for S1 (`S1-BINDING.md` §3, item 4). The report states the mismatch.
- **After PASS:** delete `$B/preserve/stage0-inputs.tar`. Keep `stage0-inputs.tar.sha256`, `paths.list` and
  `preserve.log`. The 80 inventoried files are not touched.

### 2.3 The re-grade (login node, after §2.2 exits 0)

```bash
cd $B && TMPDIR=$B/tmp timeout 1140 $PY $D/nd-unfolding/fd_f0_regrade.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-npz $P/cmodel5d-20261024/out/cmodel_5d.npz --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --flux-constraint $P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt \
  --d16-dir $D/docs/orchestration/state/s5p/stage3/f4 --f4-root $P/s5p-20260926/runs/s3r/f4 \
  --stage0-inventory $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256 \
  --s5e-assess $P/s5e-20260925/runs/cand/assess \
  --stage0c-sums $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/receipts-A/products.sha256 \
  --stage0c-root $P/5d-stage0-20261023 --pvl-products $P/pv-ladder-20261024/products \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --out-json $B/fd_f0_readout.json --out-npz $B/fd_f0_experiments.npz \
  > $B/logs/f0.out 2> $B/logs/f0.err; echo "rc=$?" >> $B/logs/f0.out
```

- **Projected wall:** 15 minutes. That rests on A7's evaluation of the row 5 products on a login node in about 2
  minutes (`state/s5p/campaign-state.json:527`), plus about 1.6 GB hashed twice over. The timeout is 1,140 s, which
  is 1.25 × that, so exit 124 is a STOP.
- **Exit codes:**
  - 0: every control passed, or control 7 failed as declared, and the readout was written;
  - 1: a control refused, or an unexpected error occurred. Its message has all digits redacted. Nothing is written;
  - 2: an argparse error;
  - 3: the leak guard refused. Nothing more is written (§5.3).
- **What is committed** (the report's PR):
  - `$B/fd_f0_readout.json`, as `fd/readout/fd_f0_readout.json`;
  - `logs/{deploy.log,deploy-tests.log,preserve.out,f0.out,f0.err}` and `preserve/preserve.log`, under `fd/receipts/`.
  The table `fd_f0_experiments.npz`, about 2 MB, stays on pscratch. Its sha256 is in the readout.

## 3. Controls, in order

Controls 0–6 and 8 refuse: exit 1, nothing written. Control 7 gates row 6 only, as FD-PLAN §3.1 declares. **No cell
value is read before control 4 passes, and nothing is written before control 8 passes.**

| # | what it checks | refuses when | test |
|---|---|---|---|
| **0** | each D16 record against its pinned sha256; its 16 `a` paths in `<truth>_half/`; each product against `a_sha256`; the directory holds exactly those 16 | any mismatch. It runs **before any other input is opened**: the test points `--s1-npz` at a missing file and still gets control 0's refusal | `test_control_0_*` (3) |
| **1** | the seven committed or pscratch records above; then every other product against its manifest; the closure and floor against `cmodel_5d.json`'s digests; the constraint file | any mismatch, **or a product file in a set directory that the manifest does not list, or a listed one that is missing** | `test_control_1_*` (3) |
| **2** | each product's meta and `.npy` headers, read without loading the arrays (detail below) | any field off | `test_control_2_*` (2 tests, 14 cases) |
| **3** | counts: row 1 at 40/20/20/20/20 within the declared seed ranges; row 2 at 20; row 4 at 16 per truth; row 5 at 1,365/1,366/1,343/1,751/1,351; row 6 at 193/195/195/199/193/172; seeds unique | any count off | `test_control_3_counts` |
| **4** | matrices: see below | any check off | `test_control_4_matrices` (3 cases) |
| **5** | the closure's 16-cell bias, recomputed, equals `cmodel_5d.json` `positive_control.reporting16.bias_cells` to 10⁻¹² | a difference | `test_control_5_closure_bias` |
| **6** | the closure floor's max \|bias\| on the 16 cells, recomputed, equals the recorded `closure_floor_max_abs` 3.2179640496732276e-05 to 10⁻¹² (§7 item 1). It is printed first and not graded | a difference | `test_control_6_floor` |
| **7** | the offset control of FD-PLAN §3.1: Δ = O_MnvTune − O_GENIE CV; χ²_Δ = Δᵀ(N_O,MnvTune + N_O,GENIE CV)⁻¹Δ, ndf 16; pass if P(χ²_16 > χ²_Δ) ≥ 0.01 | **it does not refuse.** On FAIL, row 6 is printed as "descriptive and ungraded", leaves the trigger counts and denominators, and the failure is reported | `test_a_failed_offset_control_leaves_row_6_ungraded` |
| **8** | every product's truth integral is positive on all 16 cells | any cell ≤ 0 | `test_control_8_truth_integral` |

**Control 2 in detail (`estimator_problems`, `meta_problems`):**
- **Every product:**
  - `estimator_seed` 42 and `iters` 5;
  - three estimators, each with `n_estimators` 100, `num_leaves` 8, `random_state` 42,
    `bin_construct_sample_cnt` 2147483647, `deterministic`, `force_row_wise`, and `subsample` = `colsample_bytree` =
    1;
  - refinement: it ran, with 400/31 at `random_state` 45, all-row binning and `deterministic`. The closure and its
    floor must instead record "no negative weights (signal-only reference)";
  - `code_sha256.candidate` "R" with the 400/31 override;
  - `input_npz_sha256` `07fccc1a…` and `bkg_dump_sha256` `2addac8f…`;
  - `xsec_flat` and `xtrue_flat` both `<f8` of shape (65,856,).
- **Rows 1–2:**
  - `s5n-unfold/1`, `config` "deterministic", `negweight-refined`, `no_background` false;
  - `truth`, `amplitude` and `eavail_ratio_sha256` per truth;
  - `pseudo_seed` within the declared range and equal to the filename's.
- **Row 3:** `pvl-unfold/1`, rung L-5D-PV, arm e, closure true, the five features, and the ratio digest.
- **Rows 4–6:**
  - `s5p-null-experiment/1`, `config` "R", `capacity` null, and the hypothesis digest. Row 6's is the reference truth's;
  - **row 4:** `s5p_nullexp.py` `ac929ea7…` or `4cfed582…`, expectation mode, no nuisance draw, no alternative, and
    seed 970000–970015;
  - **rows 5–6:** `789271bb…`, Poisson mode, and a flux universe in 0–99;
  - **row 6:** its alternative's `truth`, amplitude 1.0 and digest.
- **A full meta census before this declaration** (login37, 2026-10-25, the `meta` member only): rows 5–6 are uniform
  in every one of these fields, with flux universes 0–99 and filenames equal to seeds. Row 4 is 4 × `ac929ea7` + 12 ×
  `4cfed582` per truth, except NuWro, which is 16 × `4cfed582`.

**Control 4 in detail.** In S1's npz:
- U equals the definition's functional matrix in float32;
- f > 0;
- C_e is the sum of S1's 46 blocks to 10⁻¹², and C_total = C_e + C_model_abs;
- C_model_abs = diag(f) C_model diag(f);
- S in `cmodel_5d.npz` equals the committed `cmodel_5d.json` `S` bitwise, and SᵀS = C_model;
- √diag(C_total)/f equals the committed `relative_sigma.C_total` to 10⁻¹².

Then, for C_e and each leave-out matrix:
- σ from the npz equals σ from the committed JSONs to 10⁻¹²;
- **the FD-PLAN §2.1 row reproduces exactly at two decimals.** A test checks the same table from the committed
  records alone;
- C_stat,rel has full rank 16;
- the p_∥ < 4.5 cells are R00–R03 and R08–R11.

## 4. Statistics, as built

As FD-PLAN §3.1–3.3, with no change of estimator.

**Definitions:**
- **Integrals:** X = U·x, the S1 rule Σ_f x_f vol_f, for `xsec_flat` and `xtrue_flat`. Then r_i = X_i/Xtrue_i − 1.
- **The bias:**
  - rows 1, 2 and 4: b = mean_i r_i, with N = Cov_i(r)/B (ddof 1);
  - row 3: b = r, with N = 0;
  - row 5 at G: b̃ = Σw r/Σw, with w the NuE weight of each experiment's flux universe, and the ratio-estimator
    noise N = Σw²(r − b̃)(r − b̃)ᵀ/(Σw)². Then O_G = b̃_G − b_G(row 4) and N_O = N(b̃_G) + N(b_G);
  - row 6: b = b̃_T − O_ref, with N = N(b̃_T) + N_O,ref. ref is MnvTune for P1r–P3r and GENIE CV for P1g–P3g.
- **Matrices:** C^(−k) = C_e/(f fᵀ) + Σ_{j≠k} s_j s_jᵀ. The model-only matrix is C^m = C_stat/(f fᵀ) + Σ_{j≠own} s_j s_jᵀ.
- **The grade:** z_c = b_c/√(C + N)_cc, and χ² = bᵀ(C + N)⁻¹b with ndf 16.
  - p = P(χ²_16 > χ²), computed exactly for even ndf as e^(−x/2) Σ_{i<ndf/2} (x/2)^i/i!. A test checks it against
    scipy.
  - A p below 10⁻³⁰ is written as 0.0 with `p_below_floor` true (§5.3).

**The 18 truths and their matrices (FD-PLAN §2.1; ruling 2's groups):**

| group | truth (row) | grade matrix | beside it, all descriptive |
|---|---|---|---|
| vertex-family, NuWro | W1, W3 (1); closure (3); A7 NuWro (4); P1r, P2r, P1g, P2g (6) | C^(−NuWro) | in-sample C_total; model-only |
| vertex-family, GENIE MEC | W2 (1); A7 MEC (4); P3r, P3g (6) | C^(−GENIE+MEC) | in-sample; model-only |
| vertex-family, GiBUU | Stage 0c (2); A7 GiBUU (4) | C^(−GiBUU) | in-sample; model-only; the eight p_∥ < 4.5 cells, ndf 8 |
| non-vertex | q3 (1); A7 GENIE CV (4) | C_total | sensitivity C^(−NuWro) for q3 and C^(−GENIE+MEC) for GENIE CV; model-only |
| prior | nominal (1); A7 MnvTune (4) | C_total | model-only |

**Triggers (ruling 2):**
- A truth is "listed" if any cell has |z| > 2 or p < 0.01 under its grade matrix.
- Counts are printed per group, and per family inside the vertex group:
  - cells with |z| > 2, out of 16 × (truths graded);
  - truths with p < 0.01, out of the truths graded;
  - each beside its Gaussian reference, cells × 2Φ(−2) = cells × 0.0455 and truths × 0.01. The reference is context
    only.
- One all-graded line carries ruling 2's denominators, 288 and 18, with references 13.10 and 0.18. It is labelled
  "read by group, never pooled".
- If control 7 fails, those denominators become 192 and 12.
- The model-only, in-sample, sensitivity and eight-cell variants carry no trigger.

**Not in F0:** S-3 (ruling 3), any merge (ruling 1), and any generator prediction. No g is read.

## 5. Outputs

### 5.1 The readout, `fd-f0-readout/1`

```text
schema, labels{what, not, thresholds, gaussian_reference}, cells[R00..R15]
controls{passed[0..6,8], closure_floor_max_abs,
         offset_control_7{pass, pair, rule, chi2, p, p_below_floor, B_eff_calibration{truth: B_eff},
                          pairs_descriptive[9 x {a, b, chi2, ndf, p, p_below_floor}]}}
relative_sigma{C_e, C_total, minus_genie_mec, minus_nuwro, minus_gibuu: [16]}
relative_sigma_summary_percent{same keys: [median, min, max]}
truths[18 x {name, row, group, own_vertex, n_experiments, B_eff, estimator, graded, grade_matrix,
             bias[16], noise_sigma[16],
             grade{cells, z[16], chi2, ndf, p, p_below_floor, p_lt_0.01, cells_abs_z_gt_2[]},
             model_only{... , label}, in_sample{... , label}?, sensitivity{... , matrix, label}?,
             p_parallel_lt_4p5{... ndf 8, label}?, bias_uncorrected[16]?, offset_from?, label?, listed}]
triggers{rule, by_group{vertex-family|non-vertex|prior: {truths, cells, cells_abs_z_gt_2, truths_p_lt_0.01,
         gaussian_reference_cells, gaussian_reference_truths, by_family{...}}},
         all_graded{same counts, label}, listed[{truth, cells, p_lt_0.01}]}
inputs_sha256{...}, code_sha256{fd_f0_regrade.py, s1_assemble.py, s5p_stage1_inspect.py}, argv, table_sha256
```

- Every number in it is relative or a count: biases, noises and σ as fractions, z, χ² and p.
- The test `test_a_run_prints_no_f…` also checks that no key named `f`, `x`, `X`, `x_true`, `xtrue`, `f_minus_g` or
  `data` appears at the top level or in any truth record.

### 5.2 The per-experiment table, `fd_f0_experiments.npz` (pscratch only)

- `r_<set>`: B × 16 relative residuals, for every graded set and every `cal_<truth>` set.
- `seed_<set>` and `flux_<set>`: integers.
- `names`: strings.
- **No absolute integral** (§7 item 2).

### 5.3 The leak guard (ruling 6)

**`LeakGuard` is built once the integrals exist,** from:
- f;
- every product's two integral vectors X (8,545 × 2);
- f − X, X − f, f/X, X/f, f/X − 1 and X/f − 1.

**What it refuses:**
- any output number within 10⁻¹³ relative of one of those values. A 16-vector is matched cell by cell, and any other
  number against every cell;
- **any finite non-zero number below 10⁻³⁰ in magnitude.** Every absolute cross-section quantity here is of order
  10⁻³⁸–10⁻⁴¹. S1's absolute eigenvalues are 10⁻⁸⁴–10⁻⁷⁹ (`s1_assembly.json` `eigen`). So this floor catches absolute
  values the list does not name, such as an absolute σ.

**What it scans:**
- every control line printed after the integrals;
- the readout before it is written, and again with `table_sha256` added;
- the table before it is written;
- the summary lines before anything is written.

On a hit it exits 3. Nothing more is written.

**Why per cell and at 10⁻¹³:**
- **The problem:** a run holds about 137,000 legitimate residuals among about 3 × 10⁶ forbidden ratios.
- **A global 10⁻⁹ match** would refuse a correct run with near certainty: about 30 expected hits.
- **Matching per cell at a few ulps** gives an expected false refusal of order 10⁻⁴ **(arithmetic, §7 item 7)**.
- **What it still catches:** a leak computed by another arithmetic path differs by about 10⁻¹⁵ relative, so the
  10⁻¹³ match still catches it. The test plants each form computed independently.

**What it cannot catch:** a dimensionless quantity derived from f by some other formula, such as an average of f/X.
F0 forms no such quantity. f enters only as the divisor of C_e, C_stat and the σ ratios.

## 6. Code and tests

- **New:** `nd-unfolding/fd_f0_regrade.py` and `nd-unfolding/tests/test_fd_f0_regrade.py`.
- **Reused unchanged:** `s1_assemble.py` (`sha256`, `fine_map`, `functional_matrix`, `flux_weights`,
  `load_manifest`), `s5p_stage1_inspect.py` and `stage0_preserve.sh`.
- **Test inputs:** the synthetic tree (`Tree`) builds every input F0 reads: products of the true size, manifests,
  D16 records, the S1 and C_model files, and the constraint file. It reads only committed records and the real H2
  definition, never a product, covariance or data value.

| class | what it shows |
|---|---|
| `Statistics` (4) | the χ² survival function equals scipy's for ndf 2, 8 and 16; the unweighted and weighted means and noises are the declared formulas; leave-out and grade, including the eight-cell subset and the p floor, are recomputed by hand |
| `Guard` (4) | each of f, X, f − g, g − f, f/g, g/f, f/g − 1 and g/f − 1 is refused as a 16-vector, a scalar, inside a printed line and as a table row; absolute magnitudes are refused even when not listed; relative outputs pass; `check` exits 3 |
| `EndToEnd` (7) | **the module run as invoked** (`-I -B`, cwd outside nd-unfolding, the wrapper sets only the synthetic pins): <ul><li>stdout, stderr, the readout and every float array of the table carry no f, absolute value or f − g, by **this test's own scan**, built from the fixture's construction and not from the guard;</li><li>the same in O(1) units, where the 10⁻³⁰ floor cannot help;</li><li>six planted leaks exit 3 with nothing written;</li><li>**negative control:** with the guard disabled, a planted f/g − 1 reaches the readout and the scan finds it;</li><li>grades, the model-only χ² and the offset control recomputed by hand;</li><li>a failed offset control leaves row 6 ungraded, with denominators 12 and 192;</li><li>no overwrite</li></ul> |
| `Controls` (13) | each of controls 0–6 and 8 refuses a one-entry defect, and nothing is written |
| `Invocation` (3) | **the real script as declared:** `--help`; an argparse error exits 2; on the synthetic tree it reaches control 0 and refuses there (the real pins), with no traceback and nothing written |
| `CommittedPins` (7) | every identity digest is the committed file's; the record pins are the committed files'; the declared counts are the manifests' (8,545 in all); the committed `f4` inventory equals the D16 records; FD-PLAN §2.1 reproduces from the committed JSONs; the groups are §2.1's table; the eight GiBUU cells are the p_∥ < 4.5 boxes |

**Locally** (2026-10-25: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_f0_regrade
test_s1_assemble test_s1_scripts_isolated` ran 60 tests, all OK. The F0 suite alone is 38 tests in about 90 s.

## 7. Departures from the plan's letter, for the director

1. **Control 6's bound.**
   - FD-PLAN §3.5 item 6 says "≤ 3.2e-5 (`BUILD-REPORT.md` §3)". The recorded 16-cell floor is
     `closure_floor_max_abs` = 3.2179640496732276e-05, and the 27-cell one is 3.2346e-05. BUILD-REPORT rounds both to
     "at most 3.2e-5".
   - As written, the control would FAIL on the recorded value.
   - Declared instead: reproduce the recorded value to 10⁻¹². That is the check the plan intended, and it fails
     closed on any change.
2. **The per-experiment table.**
   - FD-PLAN §5.2 sizes it as "8,545 × 16 × 2", meaning x̂ and x_true.
   - Under ruling 6 it holds r only (§5.2). The absolute integrals stay in memory and feed only the guard.
3. **The descriptive offset pairs** number 9, not the "eight" of FD-PLAN §3.1. Five truths give 10 pairs, and one of
   them gates.
4. **Listing equality.**
   - Control 1 also refuses a product file in a set directory that its manifest does not list, or a listed one that is
     missing.
   - Control 0 does the same for each `f4` directory against its D16 record.
5. **Denominators if control 7 fails.** Row 6 then leaves the counts, giving 12 truths and 192 cells. The readout
   prints the actual denominators and labels them.
6. **The all-graded line.** Ruling 2 asks for "out of 288" and "out of 18", and also for counts "by truth family … not
   pooled". The readout gives both:
   - the per-group counts, with the per-family split inside the vertex group;
   - one denominator line labelled "read by group, never pooled".
   If the director wants the 288/18 line dropped, it is one key.
7. **The leak guard** is new mechanism for ruling 6 (§5.3). Its numbers are a floor of 10⁻³⁰ and a per-cell match at
   10⁻¹³.
   - **The false-refusal estimate,** per cell: about 8,544 residuals of size about 0.03. The density of the f/X − 1 and
     X/f − 1 forms near them is about 8.5 × 10⁴ per unit, and the match width is 2 × 10⁻¹³ × 0.03. That gives about
     4 × 10⁻⁶ per cell, so about 7 × 10⁻⁵ over 16 cells. The JSON vectors add much less **(arithmetic)**.
   - A false refusal would be exit 3, reported unrepaired.
8. **The p floor.** A p below 10⁻³⁰ is written as 0.0 with `p_below_floor` true, because the guard refuses numbers
   below 10⁻³⁰.
9. **Order inside the run.**
   - The cell integrals are formed after control 4 and before control 5, which needs them.
   - Control 8 is evaluated after controls 5–7, in the declared order. It covers every product, including those that
     controls 5–7 divide by.
   - Nothing is written until every refusing control has passed.
10. **Control 0 runs twice.**
    - The preserve script runs it against the committed inventory, before the copy.
    - The tool runs it against the D16 records themselves, before anything else.
11. **A statistical note on control 7.**
    - The offset χ² uses noise covariances estimated from the same draws. B_eff is 256–334 per calibration truth
      (FD-PLAN §3.1), plus row 4's 16 split seeds.
    - For a 16-dimensional estimated covariance, the inverse is biased upward by about n/(n − 17). At n ≈ 300 that is
      about 6 %, so χ²_Δ reads slightly high, and the control leans toward failing **(inference)**.
    - It is not corrected, because the rule is FD-PLAN's. It is reported beside the result.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_f0_regrade.py` | `38ef7dfb993f5d580ffa145ed5fc49f38089a854361690228f57a928773ceb3d` |
| `nd-unfolding/tests/test_fd_f0_regrade.py` | see the PR; it changes with the review |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged since S1's assembly) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |
| `…/5d-design-20261023/stage0/stage0_preserve.sh` | `27ccc04a8c14d640efe1657b3d04b657f61a682db381c105daee82f901ea5d68` |
| `…/5d-community-20261024/fd/F4-PRESERVE-INVENTORY.sha256` | `c3c245cfe026c9ef559d56dc112df71280d27d92b306e44992dad8b7a7a4057c` |

## 9. Ledger, storage and stops

- **Ledger:** no Slurm job, so 0 node-h. `fd/LEDGER.tsv` records the two login-node steps, with host, start, end, exit
  code and wall.
- **Storage:**
  - pscratch `$B`: the deploy, about 15 MB of transient tar, the 2 MB table, logs;
  - HPSS `/home/j/josephrb/mnv-5d-fd-f4-20261025`: the tar, its `.sha256` and the inventory;
  - CFS: nothing.
- **Stops:** any STOP named in §2 or §3 is reported to the director unrepaired. Nothing is rerun without the director.
- **Watch:** both steps are short enough to supervise directly. Each runs under `timeout` at 1.25 × its projected
  wall.

## 10. Not changed

- **Unchanged:** the S1 covariance, C_model,5D, R00–R15, κ = 1, the route decision and FD-PLAN's statistics.
- **Not approved:** Stage G, F1, F1-W and any merge.
- **Rules:** no GPU and no premium QOS.
- **Joseph's:** claims, KI-85, printed wording and publication.
