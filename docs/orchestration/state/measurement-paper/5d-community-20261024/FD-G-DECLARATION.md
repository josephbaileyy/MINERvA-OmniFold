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
- **What the outputs contain:** this stage reads the data, so f, g and f − g appear in its outputs. F0's leak guard
  does not apply here (the director's instruction).
- **Cost:** 0 node-h, one login-node step of seconds, no Slurm job. It writes one JSON of about 50 kB, and nothing
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
- together they are 6,842,609 B.

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
- `tests rc=0` with "Ran 38 tests … OK" (16 Stage G + 22 S1, locally on 2026-10-25).

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
  - 1: a control refused (nothing written);
  - 2: an argparse error;
  - 124: past the timeout.
  Any exit other than 0 is a STOP.
- **What is committed** (the report's PR):
  - `$B/fd_g_readout.json`, as `fd/readout/fd_g_readout.json`;
  - the logs, under `fd/receipts-g/`;
  - a ledger row in `fd/LEDGER.tsv`.

## 3. Controls

All of them run before anything is written, and each refuses: exit 1, nothing written.

| control | checks | test |
|---|---|---|
| **G0** | the sha256 of the S1 readout, the C_model readout, the s5p manifest and the S1 npz against their pins; the S1 readout names that npz; the definition and fine map (`s1_assemble.fine_map`); each prediction file against its pinned digest **and** the manifest's line | `test_g0_digests`: 7 cases, including a file that matches its pin while the manifest line does not, and a changed definition |
| **G1** | each prediction: `xsec_flat`, `sumw2_flat` and `nevt_flat` are `<f8` (65,856,) by header; the five edge arrays equal the fine grid's; `meta_json` names it; every entry is finite; sumw2 ≥ 0 | `test_g1_structure`: 6 cases |
| **G2** | S1: U is the definition's functional matrix in float32; f > 0; f equals `cmodel_5d.json`'s `x` (P5's integrals) to 10⁻¹²; C_total = C_e + C_model_abs; √diag(C_total)/f equals the committed `relative_sigma.C_total`; C_total is positive definite with rank 16 | `test_g2_s1`: 3 cases |
| **G3** | GiBUU's eight cells are exactly the boxes with p_∥ upper edge ≤ 4.5 (R00–R03, R08–R11) | `CommittedPins` |
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
covariance label says that the NuWro, GENIE+MEC and GiBUU vertices are data shifts built from those generators'
shapes.

## 5. The readout, `fd-g-readout/1`

```text
schema, labels{what, covariance, shape_only, gibuu, not}, cells[R00..R15], controls_passed[G0..G4]
predictions[5 x {name, file, sha256, label, n_mc_events_in_cells[n], cells[n], n_cells,
                 total{chi2, ndf, p, matrix, matrix_size, matrix_rank},
                 shape_only{chi2, ndf, p, matrix, matrix_size, matrix_rank},
                 pulls[n], cells_abs_pull_gt_2[], f[n], g[n], f_minus_g[n], g_over_f_minus_1[n],
                 sigma_total_over_f[n], sigma_Vg_over_f[n]}]
inputs_sha256{...}, code_sha256{fd_g_compare.py, s1_assemble.py, s5p_stage1_inspect.py}, argv
```

**The prediction labels:**
- GENIE CV: "CH";
- GENIE MEC: "CH";
- NuWro: "C12, not CH";
- GiBUU: "C12, not CH; no events above E_ν = 20 GeV, so it is compared on the eight p_∥ < 4.5 cells only and not shown
  above p_∥ 4.5";
- MnvTune: "the unfolding prior, not an independent generator".

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
| `Statistics` (3) | the χ² survival function equals scipy's at every ndf used; total and shape-only χ², pulls, ndf and rank are recomputed by hand on 16 and on 8 cells; the shape-only mode removes a pure normalization by the closed form |
| `EndToEnd` (3) | **the module as invoked** (`-I -B`, cwd outside nd-unfolding; the wrapper sets only the synthetic pins and prediction digests): <ul><li>all five comparisons recomputed by hand: g, V_g, both χ², ndf, the matrix name, size and rank, and the event counts;</li><li>no GiBUU value above p_∥ 4.5 in any output, with a negative control;</li><li>no overwrite</li></ul> |
| `Controls` (5) | G0 (7 cases), G1 (6), G2 (3) and G4 (2) each refuse a one-entry defect with nothing written. The second G4 case shows a high-p_∥ GiBUU cell is never integrated |
| `Invocation` (2) | **the real script as declared:** `--help`; an argparse error exits 2; on the synthetic tree it reaches G0 and refuses there (the real pins), with no traceback and nothing written |
| `CommittedPins` (3) | the five prediction digests equal the s5p archive manifest's lines and `2d-unfolding/pv2d/config.json`'s; the record pins equal the committed files; the GiBUU cells are the definition's p_∥ < 4.5 boxes |

**Locally** (2026-10-25: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_g_compare
test_s1_assemble test_s1_scripts_isolated` ran 38 tests, OK. The cluster run is reported in the PR.

## 7. For the director

1. **The shape-only mode's direction.**
   - It is along f, the data, as Stage 0's relative-unit mode is: 100·11ᵀ in units relative to f.
   - A mode along g would differ slightly for large normalization differences. FD-PLAN does not choose between them,
     and I took Stage 0's.
2. **Only the prediction's finite MC is added (V_g).** The data's statistical part is already in C_total.
3. **The C_model vertices and the generators.**
   - C_total includes the GENIE+MEC, NuWro and GiBUU vertices. Each is a data shift unfolded with that generator's
     shape as prior. It is not g − f.
   - So the χ² of the data against that generator carries, in its covariance, an uncertainty built from that
     generator.
   - FD-PLAN §4 declared no leave-out. The readout labels this.
4. **MnvTune v1 is the unfolding prior.** Its comparison is of the data with its own prior, and it is labelled so.
5. **Targets.**
   - The data are per nucleon on CH.
   - NuWro and GiBUU are on C12, and no target correction is applied.
   - The labels say so.
6. **GiBUU.** As ruled: it is compared on eight cells, no 16-cell χ² exists, and nothing is shown above p_∥ 4.5. There
   is therefore no figure to mark.
7. **No guard.** f, g and f − g are printed. The report will quote the readout's numbers without any reading.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_compare.py` | `722cdca5c5ff8b53139e9bb183217f6d9bf6fd00de3c2919eb65723d9e18bb7c` |
| `nd-unfolding/tests/test_fd_g_compare.py` | `0fc98dbfa9018fb7a0480938ae56f5cfc7bde90c8c7e37aa2f1361fa8d690af9` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` |

## 9. Ledger, storage and stops

- **Ledger:** one row in `fd/LEDGER.tsv`, with host, start, end, rc and wall. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 1.0 GB; F0's measured 997 MB), the logs, and the readout of about
  50 kB. Nothing goes to HPSS or CFS. The
  inputs are already archived: the predictions in `s5p-archive-20261006.tar`, and S1's assembly as S1 recorded it.
- **Stops:** any STOP in §2 or §3 is reported to the director unrepaired.

## 10. Not changed

- **Unchanged:** the S1 covariance, C_model,5D, R00–R15, κ = 1 and the route decision.
- **Not approved:** F1, F1-W and any merge.
- **Rules:** no GPU and no premium QOS.
- **Joseph's:** claims, printed wording and publication. The report gives the numbers only.
