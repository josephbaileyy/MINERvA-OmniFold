# DECLARATION G: the data result on the 16 H2 cells against five generator predictions (2026-10-25)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's approval,
  [`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md`](../../../DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md)
  item 2 (PR #364, main `a2dae50e`);
- [`FD-PLAN.md`](FD-PLAN.md) §4;
- [`FD-DIRECTOR-RULINGS.md`](FD-DIRECTOR-RULINGS.md) §5.

**Declares:**
- the tool `nd-unfolding/fd_g_compare.py` and its tests `nd-unfolding/tests/test_fd_g_compare.py`;
- the exact argv, the interpreter, the deploy, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The tool has not run, and no data-against-prediction quantity has been formed.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit, and the only cluster reads were the prediction files' headers and meta -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- any reading of the comparison, any claim, and any paper text. Those go through the director to Joseph;
- F1 or F1-W, which are skipped or deferred (decision item 3).

**CITABLE FOR:** what Stage G will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

- **What it compares:** S1's data result f on R00–R15 against the five 5D predictions of FD-PLAN §4. The covariance is
  S1's C_total, with all three C_model,5D vertices, plus each prediction's finite-MC V_g.
- **The statistics,** for each prediction:
  - the total χ², with ndf 16;
  - the shape-only χ², with Stage 0's free-normalization mode of variance 100, with ndf 15;
  - the per-cell pulls.
- **GiBUU** is compared on the eight p_∥ < 4.5 cells only, with ndf 8 (7 shape-only). Its prediction is integrated on
  those cells alone, so no GiBUU value above p_∥ 4.5 is formed, printed or written, and no 16-cell GiBUU χ² exists.
- **Every χ²** is written beside the matrix it used, the matrix's size and its numerical rank.
- **An optional declared sensitivity variant** (`--extra-block`, §2.3). A second covariance, such as the U-PLAN's
  species-response band C_resp, can be passed with its file sha256.
  - Every comparison is then also reported against C_total + C_x, beside the primary one.
  - Its construction and digest must be fixed in the binding before the run, so the variant is not post hoc.
  - **Whether to use it is Joseph's choice, relayed by the director.** The PR waits for that answer.
- **What the outputs contain:** this stage reads the data, so f, g and f − g appear in its outputs. F0's leak guard
  does not apply here (the director's instruction).
- **Cost:** 0 node-h, one login-node step projected at under 5 minutes, no Slurm job. It writes one JSON of about 50 kB, and nothing
  goes to CFS.
- **Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired. Nothing is
  rerun without the director.

## 1. Inputs

`P=/pscratch/sd/j/josephrb`.

| input | where | checked against (control G0) |
|---|---|---|
| H2 definition | `$D/nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b6790761…` and its fine map `930326a3…` (`s1_assemble.fine_map`) |
| S1 assembly: f, C_e, C_model_abs, C_total, U | `$P/s1-20261024/s1_assembly.npz` | `db000707…`, pinned, and named by the committed S1 readout's `assembly_sha256` |
| S1 readout | `$T/s1/readout/s1_assembly.json` | `81e5ef3f…` |
| C_model,5D readout (its `x`, P5's integrals) | `$D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json` | `3cfdc6a5…` |
| s5p archive manifest | `$D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` | `1a72cb43…` |
| GENIE 2.12.10 CV, no MEC (CH) | `$P/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210…`, pinned **and** the manifest's line |
| GENIE 2.12.10 + Valencia MEC (CH) | `…/gen5d_fluxfix/genie_mec_xsec5d_full.npz` | `c179855d…`, the same |
| NuWro 21.09 (**C12**) | `…/gen5d_fluxfix/nuwro_cv_xsec5d_full.npz` | `475a2871…`, the same |
| GiBUU 2019 (**C12**, no E_ν > 20 GeV) | `…/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz` | `48917692…`, the same |
| MnvTune v1, the analysis MC truth (**the prior**) | `$P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz` | `bf7bd278…`, the same |

**What the prediction files are** (headers and meta read on login37, 2026-10-25; no values read):
- each holds `xsec_flat`, `sumw2_flat` and `nevt_flat` (65,856, `<f8`), the five fine-grid edge arrays, and
  `meta_json`;
- the quantity is d⁵σ/(dp_T dp_∥ dE_avail dq₃ dW) in cm²/nucleon per unit volume, the same density as the data
  products;
- the four generator files name themselves in `meta_json.generator`: `genie_cv`, `genie_mec`, `nuwro_cv` and
  `gibuu_cv`;
- MnvTune's `meta_json.schema` is `s5p-mc-truth-pred/1`;
- together they are 6,842,609 B (`du -cb` on login37, 2026-10-25; not a committed receipt).

**A committed-record test** checks the five digests against both the s5p archive manifest and
`2d-unfolding/pv2d/config.json` (`CommittedPins`).

## 2. Exact commands

**Definitions:**
- `B=$P/fd-g-20261025`. It does not exist yet (login37, 2026-10-25).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-g-20261025` on login37 (2026-10-25) printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit, which the binding names.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B"`. That is Python 3.11.14 with numpy 1.26.4
  (login37, 2026-10-25). The tool needs numpy only.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_compare.py nd-unfolding/tests/test_fd_g_compare.py nd-unfolding/s1_assemble.py \
    nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-G-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after the tests;
- the §8 digests;
- `tests rc=0` with "Ran 46 tests … OK" (24 Stage G + 22 S1, locally on 2026-10-25).

Anything else is a STOP.

### 2.2 The comparison (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_g_compare.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --out-json $B/fd_g_readout.json > $B/logs/g.out 2> $B/logs/g.err; echo "rc=$?" >> $B/logs/g.out
```

- **Projected wall:** 5 minutes. The run reads 6.8 MB of predictions and the 0.12 MB S1 npz. The timeout is 375 s,
  which is 1.25 × that.
- **Exit codes:**
  - 0: every control passed, and the readout was written;
  - 1: a control refused, an overwrite was refused, or an unexpected error occurred (nothing written);
  - 2: an argparse error;
  - 124: past the timeout.
  Any exit other than 0 is a STOP.
- **With the variant** (§2.3), the same command, plus four arguments inserted before `--out-json`.
- **What is committed** (the report's PR):
  - `$B/fd_g_readout.json`, as `fd/readout/fd_g_readout.json`;
  - the logs, under `fd/receipts-g/`;
  - a ledger row in `fd/LEDGER.tsv`.

### 2.3 The declared sensitivity variant (only if the binding names one)

```bash
  --extra-block <npz> --extra-block-sha256 <its file sha256> --extra-block-key <key> --extra-block-name <name, e.g. C_resp>
```

**The four go together;** any one without the others is an argparse error (exit 2).

**What the binding must fix before the run:**
- the npz's path and sha256;
- its key;
- its construction record;
- that it is a 16 × 16 covariance on R00–R15 in **absolute units**, the same as C_total.

**What the readout then adds:**
- an `extra_block` record: name, file, sha256, key, per-cell relative σ, and a "declared before this run" label;
- for every prediction, a `sensitivity` record: total and shape-only χ², ndf, p, matrix name, size and rank, plus pulls,
  cells with |pull| > 2 and σ/f, all against C_total + C_x + V_g.

The primary comparison against C_total + V_g is unchanged.

## 3. Controls

All of them run before anything is written, and each refuses: exit 1, nothing written.

| control | checks | test |
|---|---|---|
| **G0** | the sha256 of the S1 readout, the C_model readout, the s5p manifest and the S1 npz against their pins; the S1 readout names that npz; the definition and fine map (`s1_assemble.fine_map`); each prediction file against its pinned digest **and** the manifest's line; the extra block, if given, against `--extra-block-sha256` | `test_g0_digests`: 7 cases, including a file that matches its pin while the manifest line does not, and a changed definition; `test_g0_s1_readout_names_the_npz`; `ExtraBlock.test_refusals` |
| **G1** | each prediction: `xsec_flat`, `sumw2_flat` and `nevt_flat` are `<f8` (65,856,) by header; the five edge arrays equal the fine grid's; `meta_json` names it; every entry is finite; sumw2 ≥ 0 | `test_g1_structure`: 6 cases |
| **G2** | S1: U is the definition's functional matrix in float32; f > 0; f equals `cmodel_5d.json`'s `x` (P5's integrals) to 10⁻¹²; C_total = C_e + C_model_abs; √diag(C_total)/f equals the committed `relative_sigma.C_total`; C_total is positive definite with rank 16. If an extra block is given: the key exists; it is a finite 16 × 16 matrix, symmetric to 10⁻¹² and positive semidefinite; C_total + C_x is positive definite | `test_g2_s1` (3 cases) and `test_g2_one_entry_defects` (3: one C_e entry, one U entry, a non-positive-definite C_total with its diagonal unchanged); `ExtraBlock.test_refusals`: 4 G2 cases |
| **G3** | GiBUU's eight cells are exactly the boxes with p_∥ upper edge ≤ 4.5 (R00–R03, R08–R11) | `test_g3_gibuu_cells`; `CommittedPins` |
| **G4** | each prediction's integral is positive on every cell it is compared on | `test_g4_positive_integrals`; and `test_g4_a_high_gibuu_cell_is_never_integrated`, where a non-positive GiBUU value above p_∥ 4.5 does not stop the run, because it is never integrated |

## 4. Statistics (FD-PLAN §4)

**Definitions,** on the cells of a comparison:
- cell integrals: X = Σ_f x_f vol_f (S1's rule), for the prediction g;
- f: S1's data result;
- **finite MC:** V_g = diag(Σ_f sumw2_f vol_f²) per cell. This is A7's condition 6 in diagonal form;
- d = f − g;
- M = C_total + V_g, the sub-block on the comparison's cells.

**The statistics:**
- **Total:** χ² = dᵀ M⁻¹ d, with ndf n. n is 16, or 8 for GiBUU.
- **Shape-only:** χ² = dᵀ (M + 100 f fᵀ)⁻¹ d, with ndf n − 1.
  - This is Stage 0's mode, `stage0_analysis.dchi2`: 100·11ᵀ on the scale relative to f.
  - In absolute units, a pure normalization difference g = c f gives (1 − c)² a / (1 + 100 a), with a = fᵀM⁻¹f.
    That is at most (1 − c)²/100. A test checks it.
- **p:** P(χ²_ndf > χ²), computed exactly for every integer ndf (erfc plus a finite series for odd ndf). A test
  checks it against scipy at ndf 1, 2, 3, 7, 8, 15 and 16.
- **Pulls:** z_c = d_c / √M_cc.
- **Rank:** the number of eigenvalues above 10⁻¹² of the largest, for M and for M + 100 f fᵀ. It is written beside
  each χ².

**No leave-out.** C_total includes all three vertices for every comparison (route item 3; FD-PLAN §4). The readout's
covariance label says that each vertex is a data shift unfolded with a prior reweighted by that generator's ratio to
GENIE 2.12.10 CV (`pv-ladder/config.json`).

## 5. The readout, `fd-g-readout/1`

```text
schema, labels{what, covariance, shape_only, gibuu, not}, cells[R00..R15], controls_passed[G0..G4]
predictions[5 x {name, file, sha256, label, n_mc_events_in_cells[n], cells[n], n_cells,
                 total{chi2, ndf, p, matrix, matrix_size, matrix_rank},
                 shape_only{chi2, ndf, p, matrix, matrix_size, matrix_rank},
                 pulls[n], f[n], g[n], f_minus_g[n], g_over_f_minus_1[n],
                 sigma_total_over_f[n], sigma_Vg_over_f[n]}]
extra_block: null | {name, file, sha256, key, relative_sigma[16], label}
predictions[i].sensitivity (only with an extra block): {name, total{...}, shape_only{...}, pulls[n],
                                                        sigma_total_over_f[n]}
inputs_sha256{...}, code_sha256{fd_g_compare.py, s1_assemble.py, s5p_stage1_inspect.py}, argv
```

**The prediction labels** (as the director ruled on §7):
- GENIE CV: "CH";
- GENIE MEC: "CH";
- NuWro: "C12 target; no correction to CH applied";
- GiBUU: "C12 target; no correction to CH applied; no events above E_ν = 20 GeV, so it is compared on the eight
  p_∥ < 4.5 cells only and not shown above p_∥ 4.5";
- MnvTune: "prior (not an independent prediction)".

**Beside every shape-only χ²** the readout carries `shape_only.mode`, and stdout says "mode along f". The note reads:
the free normalization is along f, Stage 0's precedent (ruled), and a mode along g gives a different χ² whenever
f ≠ g; review A's synthetic check measured 2.4 % (16 cells) and 7 % (8 cells).

**What stdout prints:**
- one PASS line per control check;
- one line per prediction, carrying both χ², ndf, p, the matrix name, size and rank;
- a `wrote` line with the readout's sha256.

**GiBUU's high-p_∥ cells are absent from every output.** The test `test_no_gibuu_value_above_p_parallel_4p5_is_shown`
shows it. It builds, from the fixture, every GiBUU quantity on the eight high cells: g, f − g, g/f − 1, σ_V/f and the
pull. It then finds none of them in the readout or in stdout. Its negative control finds the same quantities on the
eight low cells.

## 6. Code and tests

- **New:** `nd-unfolding/fd_g_compare.py` and `nd-unfolding/tests/test_fd_g_compare.py`.
- **Reused unchanged:** `s1_assemble.py` (`sha256`, `fine_map`, `functional_matrix`, `load_manifest`) and
  `s5p_stage1_inspect.py`.
- **Test inputs:** the fixture builds every input on the real fine map and definition, with known cell integrals, V_g
  and event counts. It reads no real prediction, covariance or data value.

| class | what it shows |
|---|---|
| `Statistics` (4) | the χ² survival function equals scipy's at every ndf used, to 10⁻¹⁰ relative; total and shape-only χ², pulls, ndf and rank are recomputed by hand on 16 and on 8 cells; the rank of a rank-5 matrix is 5; the shape-only mode removes a pure normalization by the closed form |
| `EndToEnd` (3) | **the module as invoked** (`-I -B`, cwd outside nd-unfolding; the wrapper sets only the synthetic pins and prediction digests): <ul><li>all five comparisons recomputed by hand: g, V_g, both χ² and both p (against scipy), ndf, matrix name, size and rank, pulls, σ/f, and the event counts;</li><li>**GiBUU above p_∥ 4.5:** none of its eight high cells' g, f − g, g/f − 1, σ_V/f or pull, and no 16-cell GiBUU χ² or p, appears in the readout or on stdout. Every ndf in the GiBUU record is 8 or 7. Every number on stdout is one the readout carries as printed, or a fixed constant of the control lines. A negative control finds the low-cell values;</li><li>no overwrite</li></ul> |
| `ExtraBlock` (4) | <ul><li>run as invoked with a synthetic C_resp: each prediction's variant χ² (both forms), ndf, rank and pulls recomputed by hand; the primary comparison unchanged; a PSD addition never raises χ²;</li><li>without the option, no variant appears;</li><li>a wrong digest refuses at G0; an asymmetric, a non-PSD, a wrong-shape or a missing-key block refuses at G2;</li><li>the four options go together (exit 2)</li></ul> |
| `Controls` (8) | G0 (8 cases), G1 (6), G2 (6), G3 (1) and G4 (1) each refuse with nothing written. The last G4 test spies on the comparison: GiBUU's g and V_g are zero above p_∥ 4.5, so they are never formed there |
| `Invocation` (2) | **the real script as declared:** `--help`; an argparse error exits 2; on the synthetic tree it reaches G0 and refuses there (the real pins), with no traceback and nothing written |
| `CommittedPins` (3) | the five prediction digests equal the s5p archive manifest's lines and `2d-unfolding/pv2d/config.json`'s; the record pins equal the committed files; the GiBUU cells are the definition's p_∥ < 4.5 boxes |

**Locally** (2026-10-25: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_g_compare
test_s1_assemble test_s1_scripts_isolated` ran 46 tests, OK (24 Stage G + 22 S1). The cluster run is reported in
the PR.

## 7. For the director

1. **The shape-only mode's direction.**
   - It is along f, the data, as Stage 0's relative-unit mode is: 100·11ᵀ in units relative to f.
   - A mode along g gives a different χ² whenever f ≠ g. Review A's synthetic check with 10 % shape scatter found
     differences of 2.4 % (16 cells) and 7 % (8 cells).
   - FD-PLAN does not choose between them, and I took Stage 0's.
2. **Only the prediction's finite MC is added (V_g).** The data's statistical part is already in C_total.
3. **The C_model vertices and the generators.**
   - C_total includes the GENIE+MEC, NuWro and GiBUU vertices.
   - Each is a data shift unfolded with a prior reweighted by that generator's ratio to GENIE 2.12.10 CV. It is not
     g − f.
   - So the χ² of the data against GENIE+MEC, NuWro or GiBUU carries, in its covariance, an uncertainty built from that
     generator. The GENIE CV comparison does too, through the ratios' common reference (review A).
   - FD-PLAN §4 declared no leave-out. The readout labels this.
4. **MnvTune v1 is the unfolding prior.** Its comparison is of the data with its own prior, and it is labelled so.
5. **Targets.**
   - The data are per nucleon on CH.
   - NuWro and GiBUU are on C12, and no target correction is applied.
   - The labels say so.
6. **GiBUU.** As ruled: it is compared on eight cells, no 16-cell χ² exists, and nothing is shown above p_∥ 4.5. There
   is therefore no figure to mark.
7. **No guard.** f, g and f − g are printed. The report will quote the readout's numbers without any reading.
8. **The sensitivity variant (§2.3)** is built in, but no block is named.
   - If Joseph chooses the director's option (ii), the binding names C_resp's file, digest, key and construction record
     before the run, and G reports both matrices.
   - Under option (ii), C_resp's construction is the director's: the mean-centred ±1σ half-span per species over the
     11 MP-1 S1 (e) unfolds, using s1_assemble's lateral convention. It is not built here.
   - The tool checks only the block's digest, shape, symmetry and positive semidefiniteness. It does not check how the
     block was made.

**The director's rulings on this section** (relayed 2026-10-25):
1. **The shape-only mode along f is accepted,** following Stage 0. The 2.4 % and 7 % mode-direction differences are
   printed beside it. No along-g variant is added, since that would be an undeclared second statistic.
2. **MnvTune v1** is labelled "prior (not an independent prediction)".
3. **NuWro and GiBUU** carry "C12 target; no correction to CH applied".
4. **Review A's two points are accepted:** the GENIE CV covariance note, and the removal of the undeclared |pull| > 2
   list.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_compare.py` | `fe233935339acd73851ebe129810ee6ad95e1878d18690c35d0bb4132c8fbb2c` |
| `nd-unfolding/tests/test_fd_g_compare.py` | `4fa952762ac6ef20b4458c0c3f38117bef00291b4e1c669af036a9eceb1195f0` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |

## 9. Ledger, storage and stops

- **Ledger:** one row in `fd/LEDGER.tsv`, with host, start, end, rc and wall. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 1.0 GB; F0's deploy measured 997 MB by `du -sh` on login37, 2026-10-25, not a committed
  receipt), the logs, and the readout of about
  50 kB. Nothing goes to HPSS or CFS. The
  inputs are already archived: the predictions in `s5p-archive-20261006.tar`, and S1's assembly as S1 recorded it.
- **Stops:** any STOP in §2 or §3 is reported to the director unrepaired.

## 10. Not changed

- **Unchanged:** the S1 covariance, C_model,5D, R00–R15, κ = 1 and the route decision.
- **Not approved:** F1, F1-W and any merge.
- **Rules:** no GPU and no premium QOS.
- **Joseph's:** claims, printed wording and publication. The report gives the numbers only.

## 11. Review dispositions

Two independent read-only reviews ran on `7fd3688d`:
- **A** checked the build against the plan and rulings;
- **B** started from the code and attacked it, with mutations.

Neither found a defect in the code.

**B's four MATERIAL findings, all on test power, all fixed:**

| # | the gap | the fix |
|---|---|---|
| B-M1 | A 16-cell GiBUU χ² would have passed every test | The scan forbids the 16-cell GiBUU χ² and p (both forms), and every ndf in the GiBUU record must be 8 or 7 |
| B-M2 | The stdout scan had no power against formatted values | Every number on stdout must be one the readout carries, as printed, or a fixed constant of the control lines |
| B-M3 | "Never integrated above 4.5" had no test | A spy on `compare` checks that GiBUU's g and V_g are exactly zero on the high cells |
| B-M4 | The readout's p was never checked | Every p is checked against `chi2_sf` and scipy |
<!-- absence-ok: these rows restate review B's mutation findings on the test suite at 7fd3688d (each mutation passed every test there); they are statements about that suite's coverage, now closed, not claims that a result does not exist -->

**Mutation check of the fixes,** in scratch copies of the module: each of B's mutations is now caught:
- a 16-cell GiBUU χ²;
- high-cell GiBUU values printed;
- GiBUU integrated on all cells;
- p at the wrong ndf;
- rank equal to the matrix size;
- the C_total sum, U, positive-definite, readout-names-npz and G3 checks removed;
- σ/f from M.

**B's MINOR points:**
1. **Rank:** a rank test was added.
2. **Controls no test noticed** (G2 sum, U and positive definite; G0 names; G3): one-entry tests were added for each.
3. **σ/f:** it is now tested.
4. **The scipy tolerance:** it is now relative.

**A's MINOR points:**
1. **The covariance label left out GENIE CV.** The label and §7.3 now say every vertex is a ratio to GENIE CV.
2. **The stdout shape-only line** now carries the matrix name and size.
3. **The g-mode difference** is stated with A's numbers.
4. **The undeclared |pull| > 2 cell list is removed,** since no trigger is ruled for G.
5. **Exit 1's causes** are listed in full, and an explicit G2 shape check was added.
6. **The 997 MB and 6,842,609 B figures** are marked as measured on login37 and not committed receipts. §0's wall now matches §2.2. EndToEnd now checks the shape-only size and rank, and the pulls.

**A and B both noted that the worktree changed during their reviews.** The change was the `--extra-block` variant (§2.3), added at the director's request. Its tests are in `ExtraBlock`, and B's mutation run covered the module with it in place.

