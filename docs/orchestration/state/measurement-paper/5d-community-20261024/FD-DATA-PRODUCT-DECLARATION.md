# DECLARATION DATA-PRODUCT: the 5D result's reported covariance, as a committed readout (2026-10-27)

**By** the measurement session, for the director to bind.

**Under:**
- `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` (PR #408), item 2: the 5D result is
  integrated into the paper and the note, with "the 16-cell result and its reported covariance".
- The director's request of 2026-10-27: nothing in git holds the 16 × 16 matrices today, so the integration needs a
  committed data-product readout.
  <!-- absence-ok: search 2026-10-27 on the declaration's base: `git ls-files '*.npz'` matching s1_assembly|cresp|C_total|covar lists only the per-universe unfold products under s1/readout/s1_assembly/ and the 2D release package's covariance_eavailW.npz; `git grep -lE '"(C_total_resp|C_total|C_resp|C_e)"\s*:\s*\[\s*\[' -- '*.json'` finds no file; the 16 x 16 matrices are in the two pscratch npz -->

**Sibling:** [`FD-G-FIGURES-DECLARATION.md`](FD-G-FIGURES-DECLARATION.md), in the same PR. The two share the deploy
and its tests (that declaration's §2.1).

**Declares:**
- a tool, `nd-unfolding/fd_data_product.py`, and its tests;
- the exact argv, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The tool has not run on S1's or C_resp's products. It has read only synthetic products, in its
tests.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit; its tests open no real product and read the committed readouts for their digests and chain only (CommittedPins) -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- shipping the product as supplemental material, which is Joseph's release decision;
- a reading, a claim or printed wording.

**CITABLE FOR:** what the readout will hold, from which products, and what makes the tool stop.

**NOT CITABLE FOR:** any result; and, once run, coverage.

## 0. Summary

**The readout** is `fd_data_product.json` (schema `fd-data-product/1`), with one CSV per matrix and one for the cells.
It holds:
- **the cells:** R00–R15, each with its H2 boxes and its box edges, from the H2 definition;
- **how the cells relate to the note's H2:** the 32 H2 boxes, Stage 1's supported ones and the definition's
  unreported ones, checked against both records (§4);
- **f**, S1's cell integrals;
- **the matrices**, in S1's absolute units:
  - C_e;
  - C_model_abs;
  - C_resp;
  - C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance: Stage G's `reported_covariance`
    (`DECISION-20261026-joseph-adopt-cresp.md`). Stage G's χ² is against C_total + C_resp + V_g, which adds each
    prediction's own finite-MC variance. V_g is not in this product, and the label says so;
- **the correlation matrix** of C_total + C_resp;
- **the per-cell relative σ**, √diag/f, of each of the four matrices.

**Its labels:**
- "data product: the 5D result's reported covariance";
- NOT CITABLE FOR coverage;
- the fake-data limitation travels with it, citing `FD-F0b-REPORT.md`.

**Sources:** S1's `s1_assembly.npz` (`db000707…`) and C_resp's `cresp.npz` (`4d8b5797…`), both pinned by digest.

**What is checked against committed records** (§3):
- every diagonal, as relative σ, against S1's, C_resp's and Stage G's readouts and `CRESP-REPORT.md`'s table;
- the off-diagonals through the spectra's extremes, which S1's and C_resp's readouts record;
- the sum, against `cresp.npz`'s own C_total_resp.

No committed record holds the off-diagonal elements themselves.
<!-- absence-ok: search 2026-10-27 on the declaration's base: `git ls-files '*.npz'` matching s1_assembly|cresp|C_total|covar lists only the per-universe unfold products under s1/readout/s1_assembly/ and the 2D release package's covariance_eavailW.npz; `git grep -lE '"(C_total_resp|C_total|C_resp|C_e)"\s*:\s*\[\s*\[' -- '*.json'` finds no file; the 16 x 16 matrices are in the two pscratch npz -->

**No new statistic.** The matrices are copied. The only arithmetic is the sum C_total + C_resp, which Stage G already
formed, and, for display, √diag/f and the correlation.

**Cost:** 0 node-h, on a login node, with no Slurm job and nothing written to CFS.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

| input | path | sha256 | schema / checked against |
|---|---|---|---|
| S1's assembly | `$P/s1-20261024/s1_assembly.npz` (on pscratch, 119,273 B, 53 keys) | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` | keys `f`, `C_e`, `C_model_abs`, `C_total` read |
| S1's readout | `$T/s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` | `s1-readout/1`, with `meta.schema` `s1-assembly/1`; its `assembly_sha256` is S1's assembly |
| C_resp's assembly | `$P/cresp-20261026/out/cresp.npz` (on pscratch, 12,952 B, 8 keys) | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` | keys `C_resp`, `C_total_resp` read |
| C_resp's readout | `docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json` | `19bb2ee12827207fa346242ac901af48f6c80785eff5a14ff54133dff1ea01f0` | `cresp-readout/1`; it names this C_resp, built on S1's assembly and the definition |
| C_resp's report | `docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md` | `f41e5f0c607ecf1499b576d89688249a6bc025ca3ed29803b29a1a9dcd95d5a2` | its §2 per-cell table, in %, to 2 dp |
| Stage G's readout | `$T/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` | `fd-g-readout/2`; it ran on S1's assembly, the definition and this C_resp, adopted |
| the H2 definition | `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | `h2-definition/1`; it names the Stage-1 receipt |
| the Stage-1 receipt | `docs/orchestration/state/s5p/stage1/stage1_inspect.json` | `def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d` | `s5p-stage1-inspect/1`; `mc.H2` read |

`$P` and `$T` are as in the sibling's §2.

**The two `.npz` files' headers** are recorded in
[`fd/receipts-g-figures/declaration/npz_headers.txt`](fd/receipts-g-figures/declaration/npz_headers.txt) (login24,
2026-10-27T09:59Z): their sizes, their sha256, which are the pins, and the names, shapes and dtypes of the keys read.
The receipt was made from the zip headers only, by `npz_headers.sh`, and no array value was read.

The files stay on pscratch; the readout copies their four matrices into git.

## 2. Exact commands

### 2.1 Deploy and tests

This is the sibling's §2.1, which runs `test_fd_data_product` with the figure tests.

### 2.2 The run (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 75 $PY $D/nd-unfolding/fd_data_product.py \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cresp-npz $P/cresp-20261026/out/cresp.npz \
  --cresp-json $D/docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json \
  --cresp-report $D/docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/CRESP-REPORT.md \
  --g-readout $T/fd/readout/fd_g_readout.json --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --stage1 $D/docs/orchestration/state/s5p/stage1/stage1_inspect.json \
  --out-dir $B/data-product > $B/logs/data-product.out 2> $B/logs/data-product.err; echo "rc=$?" >> $B/logs/data-product.out
```

- **Projected wall:** 60 s, as the sibling's; the synthetic runs take well under 1 s. The timeout is 75 s.
- **Exit codes:**
  - 0: every control passed and the seven files were written;
  - 1: a control refused, or an output already exists (nothing written);
  - 2: argparse;
  - 124: past the timeout.

  Any exit other than 0 is a STOP.
- **What is committed** (the report's PR):
  - the seven files, as `fd/data-product/`;
  - the logs under `fd/receipts-g-figures/`;
  - a ledger row.
- **The results index:** the readout's keys include relative σ. If it enters the index population, the index is
  regenerated in-branch under the director's standing ruling (a).

## 3. Controls

Every control runs before anything is written, and each refuses: exit 1, nothing written.

| control | checks | tests (each planted defect asserts its own clause) |
|---|---|---|
| **Q0** | No output exists. Each of the eight inputs' sha256 is its pin, and each readout's schema the declared one. **The chain:** <ul><li>S1's readout names S1's assembly, and its `meta.schema` is `s1-assembly/1`.</li><li>C_resp's readout names C_resp's assembly, built on S1's assembly and the definition.</li><li>The definition names this Stage-1 receipt.</li><li>Stage G ran on S1's assembly, the definition and this C_resp, adopted.</li></ul> | `test_q0` (each of the eight pins; 12 chain and schema sub-tests, with a wrong schema for S1's, C_resp's and Stage G's readouts and S1's `meta.schema`); `test_no_overwrite` (the JSON and two CSVs) |
| **Q1** | <ul><li>f is 16 cells, every matrix is 16 × 16, and all are finite.</li><li>f is positive.</li><li>The definition reports R00–R15 in order, and the three readouts name the same cells.</li><li>**The H2 boxes:** Stage 1's supported count is 32 less its unsupported boxes. The definition's unreported boxes are exactly the boxes in no cell, and all are unsupported in Stage 1. Every box is in the cell that `h2_to_reporting_cell` names.</li></ul> | `test_q1` (a 15-cell f, a negative f, a 15 × 15 C_resp, a NaN, reversed cells, and a Stage-1 flag flipped on box 17 and on box 3) |
| **Q2** | **The sum of its parts:** C_total + C_resp equals C_e + C_model_abs + C_resp, and cresp.npz's own `C_total_resp`, to 10⁻¹² of its largest diagonal | `test_q2_the_sum_of_its_parts` (C_total off by 10⁻⁹ on one diagonal, with every readout's σ matching it, so Q2 alone fires; `C_total_resp` off by 10⁻⁶) |
| **Q3** | **The committed relative σ, to 10⁻¹² relative:** <ul><li>C_e's and C_model_abs's are S1's readout's `C_e` and `C_model`.</li><li>C_resp's is C_resp's readout's `C_resp`.</li><li>C_total + C_resp's is C_resp's readout's `C_total_resp`, the values `CRESP-REPORT.md` tabulates, and Stage G's `sigma_total_over_f`.</li><li>C_total's is both readouts'.</li><li>f is Stage G's.</li><li>**`CRESP-REPORT.md`'s per-cell table:** C_resp's, C_total's and C_total + C_resp's relative σ are its values, to its 2 dp (|100σ − table| ≤ 0.005).</li><li>**The spectra's extremes,** which depend on the off-diagonals: C_e's and C_total's minimum and maximum eigenvalues are S1's readout's `eigen`, C_total's and C_total + C_resp's minimum and maximum, and C_resp's maximum, are C_resp's readout's, to 10⁻⁹ relative. Each is computed as the builders computed it, `eigvalsh` of the absolute matrix.</li></ul> | `test_q3_each_committed_sigma` (12 sub-tests: each committed σ × (1 + 10⁻⁹), a spectrum extreme in each readout, a table row dropped, one table value + 0.02) |
| **Q4** | Every matrix is symmetric to 10⁻¹². C_total + C_resp is positive definite. C_e, C_model_abs and C_resp are positive semidefinite (relative eigenvalues ≥ −10⁻¹² of the largest) | `test_q4` (an asymmetric C_e; an indefinite C_total + C_resp; an indefinite C_model_abs and C_resp, each alone) |
| **Q5** | The correlation is C_total + C_resp's, ρᵢⱼ √(MᵢᵢMⱼⱼ) = Mᵢⱼ to 10⁻¹² of the largest diagonal, and it is symmetric, within [−1, 1], with a unit diagonal | `test_q5_and_q6` (the correlation of C_total; a matrix that is not a correlation) |
| **Q6** | Every number written reads back from its CSV and from the JSON, bit for bit: the four matrices, the correlation, f and every relative σ | `test_q5_and_q6` (a matrix CSV rounded to 6 digits; f rounded to float32 in the cells CSV) |

**The Q4 tolerance.** Q4 tests the f-scaled matrices: a parts matrix is semidefinite if its smallest relative
eigenvalue is at least −10⁻¹² of its largest. That is far above the round-off in the committed spectra:
- C_resp has rank 4. `cresp.json` `eigen` gives its minimum eigenvalue as −3.0 × 10⁻⁹⁶ against a maximum of
  3.5 × 10⁻⁸⁰ in absolute units, a ratio of −8.5 × 10⁻¹⁷.
- C_model_abs has rank 3. Its fractional matrix's minimum eigenvalue is −7.4 × 10⁻¹⁸, in
  `nd-unfolding/pv-ladder/readouts/cmodel_5d.json` `psd_min_eigenvalue`.

## 4. The readout, `fd-data-product/1`

```text
schema, labels{what, covariance, units, not_citable_for, limitation, not, cells}, controls_passed[Q0..Q6],
cells[16 x {cell, h2_boxes, box{pt, pz, eavail, q3, W}}],
h2{unsupported_stage1, in_cells, unreported_boxes, absorbed, h2_to_reporting_cell},
f[16], matrices{C_e, C_model_abs, C_resp, C_total_plus_C_resp: 16 x 16}, correlation (16 x 16), correlation_of,
relative_sigma{the four: 16}, files_sha256{the six CSVs}, inputs_sha256{the eight}, code_sha256{fd_data_product.py, fd_g_compare.py, s1_assemble.py, s5p_stage1_inspect.py},
argv
```

**The CSVs**, in the same directory:
- `fd_data_product_C_e.csv`, `_C_model_abs.csv`, `_C_resp.csv`, `_C_total_plus_C_resp.csv` and
  `_corr_C_total_plus_C_resp.csv`. Each has a header row `cell,R00,…,R15`, then one row per cell. The values are
  written with Python's `repr`, which reads back bit for bit (Q6).
- `fd_data_product_cells.csv`: `cell`, the ten box edges, `f`, and the four relative σ.

**The labels**, verbatim from the tool:

| key | text |
|---|---|
| `what` | data product: the 5D result's reported covariance |
| `covariance` | C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance (Stage G's reported_covariance; DECISION-20261026-joseph-adopt-cresp.md), from S1's assembly and C_resp's, in S1's absolute units. Stage G's chi2 is against C_total + C_resp + V_g, which adds each prediction's own finite-MC variance V_g (Stage G's sigma_Vg_over_f); V_g is not in this product |
| `units` | f: each cell's integral sum_f xsec_flat_f * vol_f in cm^2/nucleon (S1's meta.integral); each matrix in (cm^2/nucleon)^2; relative sigma: sqrt(diag)/f; box edges as in the H2 definition, whose largest edges (4.5 for p_T, 60 for p_parallel, 100 for E_avail, q3 and W) are the analysis grid's outer edges |
| `not_citable_for` | coverage |
| `limitation` | the fake-data study of this estimator, graded against C_total + C_resp, is state/measurement-paper/5d-community-20261024/FD-F0b-REPORT.md, whose grades travel with this product; the limitation's wording is Joseph's (state/2d-closeout/stageF/methods/5d-fd-presentation/DRAFT.md) |
| `not` | no reading, claim or release text; whether it ships as supplemental material is Joseph's |
| `cells` | built from the definition and the Stage-1 receipt, and checked by Q1. On the committed records it reads: "R00-R15 are the definition's 16 reporting cells: the 32 H2 boxes (s5p_stage1_inspect.H2_EDGES) after its purity merges (steps, tau 0.1). Stage 1 (state/s5p/stage1/stage1_inspect.json mc.H2) supports 27 of the 32 boxes before merging (the note's 27 supported H2 cells); its unsupported boxes are 2, 6, 10, 14, 17. 28 boxes enter the 16 cells; the definition's unreported boxes are 2, 6, 10, 14; box 17, unsupported alone, enters R09 (17, 19, 21, 23) by the merges" |

The `cells` label answers the director's question of 2026-10-27 on the note's "27 supported cells"
(`sec_5d.tex:113`). Its numbers are computed from the two committed records, which are simulation-only, and a test
asserts them as literals. The note's appendix (`app_statmethods_nd.tex:25`) gives the same H2 interior edges and
support rule.

## 5. Code and tests

### 5.1 `nd-unfolding/fd_data_product.py` (new, 334 lines)

| part | what |
|---|---|
| constants | `INPUTS`, `PINS`, `SCHEMAS`, `MATRICES` (each matrix and where its committed σ is), `LABELS` |
| `load` | Q0, then reads the four S1 arrays and the two C_resp arrays |
| `build` | Q1–Q5; `report_table` (`CRESP-REPORT.md`'s per-cell table); `h2_relation` (the H2 boxes and the `cells` label); `correlation` |
| `outputs`, `matrix_csv`, `cells_csv`, `read_matrix_csv`, `check_readback` | the CSVs and Q6 |
| `run` | writes `.partial` files and then uses `os.replace`, after every control has passed |

It imports `fd_g_compare` (`Stop`, `report`) and `s1_assemble` (`sha256`, `s1.AXES`). It computes no covariance.

### 5.2 `nd-unfolding/tests/test_fd_data_product.py` (new, 11 tests)

`DPTree` builds synthetic S1 and C_resp products, three readouts and a report table consistent with them as the
committed ones are. It uses the committed definition and Stage-1 receipt.

| class | what it shows |
|---|---|
| `EndToEnd` (2) | <ul><li>**Every number:** every matrix, the correlation, f and every relative σ is parsed from its CSV and from the JSON, and asserted bit for bit against the synthetic products, recomputed here. C_total + C_resp equals its parts to 10⁻¹². The cells CSV's header and box edges match the definition, and the digests match the files.</li><li>**The declared labels**, including the `cells` label and the H2 relation, as literals.</li><li>`FD-F0b-REPORT.md` exists.</li><li>No overwrite, of the JSON or a CSV.</li></ul> |
| `Controls` (6) | Each control Q0–Q6 refuses its planted defects, with its own clause and nothing written (§3) |
| `Invocation` (2) | As written (`-I -B`, cwd outside `nd-unfolding`), the real pins refuse the synthetic products at Q0 with no traceback. A missing input exits 2 |
| `CommittedPins` (1) | <ul><li>The committed readouts' and records' digests are `PINS`, and their schemas are `SCHEMAS`, with S1's `meta.schema`.</li><li>Their chain fields name the two pinned products.</li><li>They hold every relative σ and eigen key that Q3 reads.</li><li>`CRESP-REPORT.md`'s table equals `cresp.json`'s relative σ to its 2 dp.</li></ul> |

Locally, the tests ran with the sibling's (that declaration's §6.4).

## 6. For the director

1. **The matrices included** are the four requested. C_total itself, S1's 46 component blocks (38 band, 5 lateral, normalization, seed and
   stat; `s1_assembly.json` `meta.blocks`) and C_resp's species blocks are not written. Adding C_total, or the seven S1 groups G-DIAG uses, is an amendment.
2. **The units** are S1's absolute: cell integrals in cm²/nucleon, not cross-section densities. A density would need
   each cell's five-dimensional volume. The cells are unions of H2 boxes, and the boxes' outer edges are the grid's,
   so that would be a new convention. It is not offered.
3. **The precision:** the CSVs carry full double precision, 17 significant digits. A rounded, printable table is the
   note's, from these.
4. **Where it goes:** `fd/data-product/` in the report PR. Whether it ships as supplemental material is Joseph's.
5. **The H2 relation** goes into the labels (`cells`) and as fields (`h2`), as the director asked.

## 7. Pinned bytes

| file | sha256 |
|---|---|
| `nd-unfolding/fd_data_product.py` | `1a42264faf4d8f3977a1eb5d66fa75604066200ac06e9034188860f9ff6ba8df` (new) |
| `nd-unfolding/tests/test_fd_data_product.py` | `1595ff05e66ffb59121e97fd611e77afcfad30e88fc6c0a4e195177c3c71d270` (new) |
| the seven inputs | §1 |

## 8. Ledger, storage and stops

- **Ledger:** a row in `fd/LEDGER.tsv` for §2.2. There is no Slurm job, so 0 node-h.
- **Storage:** the seven files are under 100 kB, in `$B/data-product`. Nothing goes to HPSS or CFS.
- **Stops:** any STOP is reported to the director unrepaired.

## 9. Not changed

- S1's and C_resp's products and readouts, Stage G's readout, the definition and the Stage-1 receipt.
- `docs/analysis-note/**`.
- Claims, release text, data availability and printed wording are Joseph's.

## 10. Review dispositions

Review C (read-only, on this declaration and its sibling) found:

| # | finding | disposition |
|---|---|---|
| C-M1 | Q0 expected S1's readout schema `s1-assembly/1`; the committed readout's is `s1-readout/1` (`s1-assembly/1` is its `meta.schema`), so the real run would have refused at Q0. The fixture wrote the tool's wrong value, and no test read the committed schemas | Q0 expects `s1-readout/1` and checks `meta.schema`. The fixture writes both, and `CommittedPins` asserts every committed schema against `SCHEMAS` |
| C-M2 | The `covariance` label called C_total + C_resp "the covariance of Stage G's reported comparison"; that comparison is against C_total + C_resp + V_g | The label names it the data's reported covariance (Stage G's `reported_covariance`) and states that Stage G's χ² adds V_g, which is not in the product |
| C-m1 | Q2 cannot catch a wrong C_resp, and off-diagonals were compared against nothing committed | Q3 adds the spectra's extremes from S1's and C_resp's readouts, and Q5 ties the correlation to the matrix. §0 says what is and is not checked against committed records |
| C-m2 | Q5 checked the correlation's form only | Q5 requires ρᵢⱼ √(MᵢᵢMⱼⱼ) = Mᵢⱼ; the correlation of C_total refuses |
| C-m3 | Planted defects were missing for most schema, digest and symmetry clauses, and for f's shape | Each has one (§3) |
| C-m4 | `eigen_min_relative` put new numbers in the product | Removed |
| C-m5 | The `limitation` label pointed to F0b without saying what travels | It says F0b's grades travel with the product and that the limitation's wording is Joseph's, citing the draft |
| C-m6 | §3's tolerance paragraph: a wrong exponent, absolute versus relative units, and C_model_abs omitted | Corrected (§3) |
| C-m7 | The npz sizes and hashes had no committed receipt; the test docstring cited the wrong section | `npz_headers.txt` (headers only); the docstring corrected |
| C-m8 | Q3 checked `cresp.json`, not `CRESP-REPORT.md`, which the director named | `CRESP-REPORT.md` is a pinned input, and Q3 checks its table to its 2 dp |
| C (H2) | The `cells` label is true against both records and matches the note's definition | No change |
