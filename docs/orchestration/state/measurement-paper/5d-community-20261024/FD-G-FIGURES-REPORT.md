# REPORT G-FIGURES and DATA-PRODUCT: the 5D figures and the reported-covariance readout (2026-10-27)

**By** the measurement session.

**Under** [`FD-G-FIGURES-AND-DATA-PRODUCT-BINDING.md`](FD-G-FIGURES-AND-DATA-PRODUCT-BINDING.md) (PR #412, main
`265c899e`), which binds [`FD-G-FIGURES-DECLARATION.md`](FD-G-FIGURES-DECLARATION.md) and
[`FD-DATA-PRODUCT-DECLARATION.md`](FD-DATA-PRODUCT-DECLARATION.md) at deploy pin `933cfe35`.

**MEASURES:** nothing. It draws three figures from committed readouts, and copies the reported covariance from two
pinned products into git.

**CANNOT AUTHORIZE:** a caption, an axis label or legend wording as final, a reading, a claim, or shipping the data
product as supplemental material. These are Joseph's.

**CITABLE FOR:**
- the outputs' digests;
- the controls' outcomes;
- the run's steps and times.

**NOT CITABLE FOR:**
- any reading of a figure;
- coverage. The product's label says so.

## Outcome

**Every step exited 0, in the bound order,** on login24 at 0 node-h, with no Slurm job and nothing written to CFS:

| step | what | UTC | rc | outcome |
|---|---|---|---|---|
| §2.1 (figures) | deploy and tests | 13:36:49 to 13:38:20 | 0 | HEAD `933cfe354ba6…`; porcelain 0 before and after; the §8 digests and the binding's two declaration prefixes (`91ea2406…`, `6444fb77…`); "Ran 85 tests in 73.210s, OK" |
| §2.2 (data product) | `fd_data_product.py` | 13:38:20 | 0 | Q0–Q6 PASS, 48 lines; 7 files |
| §2.2 (figures) | `fd_g_figures.py --figures ratio modes sens --ratio-form data-over-prediction --gibuu-axis separate` | 13:38:30 to 13:38:37 | 0 | K0–K8 PASS, 576 lines; 3 PDFs and 3 sidecars |
| §2.3 (figures) | `fd_g_figures_check.py` | 13:38:47 | 0 | "OK: 495 checks, 0 failed, 3 sidecars"; porcelain 0 after |

**Times.** Each step stamped its start and end into `<step>.start`. The deploy's first stamp follows the clone, and its
end is bounded by the next step's start.

**stderr.** The figure run's stderr holds only the 24 expected fontTools "'created' timestamp seems very low" lines
(§2.2). The data product's stderr is empty.

**The files** are fetched byte-identical. Their sha256 on pscratch (`logs/outputs-sha256.txt`) equal the committed
files'.

## 1. The figures (`fd/figures/`)

| figure | PDF sha256 | PDF bytes | drawn items | sidecar sha256 |
|---|---|---|---|---|
| `fd_g_fig_ratio` | `6372244f9e15f065d4f2b99d6c82f6eaf4e7c5dc0fa87cd5ebba545229f81531` | 29,325 | 111 | `d91d2a29e1eb4cb3218b02c49ad9f8bd713072705c39284a8178366e70cc8a5d` |
| `fd_g_fig_modes` | `5421815f4dfdfb4c972ef7bb9c0f4c4682c16333052ad59ad6215bc43d9a0748` | 32,043 | 95 | `d567dd6fff01d3554c4c25ef31d1033365fbe227d512999e8d64cd7129630131` |
| `fd_g_fig_sens` | `96af0ed9dc2be870509f4a3ac5cb4afdfc57a717ffbd9b2556834e9d4cb29e6d` | 35,089 | 57 | `dc40d8e1a79221c9c047a2225b6db89ab417c9a4f41da39d42df2365ec9859bf` |

**Each sidecar records:**
- `code.commit` `933cfe35…` with `clean` true;
- the six inputs' pins (§1 of the declaration);
- Python 3.11.14, numpy 1.26.4 and matplotlib 3.10.8;
- the options `data-over-prediction` and `separate`, as rulings 1 and 2 set them.

**Rulings 1–10 as drawn:**
- data/prediction, with V_g not drawn;
- GiBUU on its own axes, on its eight p∥ < 4.5 cells only;
- the declared colours, grey prior and markers;
- the declared names and qualifiers;
- three modes per 16-cell prediction;
- all three figures, in the article's style and the declared order;
- no χ² on any figure.

**The paper rewrite lane** installs the figures it uses; this session does not edit `docs/analysis-note/**`.

**Per ruling 10,** the ratio figure's caption, which is Joseph's, should say that the χ² uses the full covariance.

## 2. The data product (`fd/data-product/`)

| file | sha256 |
|---|---|
| `fd_data_product.json` | `b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072` |
| `fd_data_product_cells.csv` | `e7582bfec1f572df389fb6a7f9f087511eb87a67db87db625f2035eff28cd0f2` |
| `fd_data_product_C_e.csv` | `222c4dd4efef0780c408b82caa8d360723bc8b73b784885789f374a624e6c715` |
| `fd_data_product_C_model_abs.csv` | `ad179dea32b1360083f5f69df9ae051f2486abc90354fee9b6a514736eac0e63` |
| `fd_data_product_C_resp.csv` | `35bfcb2a332b8b5aff4c9f14a14ccb63787082e49814962d2e5de0e40659cc62` |
| `fd_data_product_C_total_plus_C_resp.csv` | `20a4b9d8e41c2b53a65b20beebf7abcb2bf46d5fb4de2a30af1ca8e327361ad8` |
| `fd_data_product_corr_C_total_plus_C_resp.csv` | `838f16617ed88f86329ee4eb9c2955e16ffe99e14791890b786c7548b35cd171` |

**The per-cell relative σ,** from the readout's `relative_sigma`, over R00–R15:

| matrix | median | min | max |
|---|---|---|---|
| C_e | 6.45 % | 4.05 % (R04) | 8.47 % (R13) |
| C_model_abs | 3.34 % | 0.43 % (R00) | 11.36 % (R02) |
| C_resp | 2.14 % | 0.70 % (R04) | 3.71 % (R05) |
| C_total + C_resp | 7.29 % | 4.20 % (R04) | 14.00 % (R02) |

The C_resp and C_total + C_resp medians are `CRESP-REPORT.md`'s 2.14 % and 7.29 %. Q3 checked every cell of its table,
to its 2 dp.

**The labels are the declared ones** (the declaration's §4):
- `what`: "data product: the 5D result's reported covariance";
- `not_citable_for`: "coverage";
- `limitation` cites `FD-F0b-REPORT.md`.

**The `cells` label and the `h2` fields** give the 32 H2 boxes:
- 27 supported in Stage 1, with boxes 2, 6, 10, 14 and 17 unsupported;
- 28 in the 16 cells;
- unreported boxes 2, 6, 10 and 14;
- box 17 enters R09 (`h2.absorbed` `{"17": "R09"}`).

## 3. The receipts (`fd/receipts-g-figures/run/`)

- **The step scripts and their local captures:**
  - `s1.sh`: the deploy and tests, which refuses if `$B` exists;
  - `s2.sh`: the data product;
  - `s3.sh`: the figures;
  - `s4.sh`: the check and the output digests;
  - `s1.out` to `s4.out`: what each step printed back through ssh.
- **`logs/`:**
  - `deploy.log` and `deploy-tests.log`;
  - `data-product.{start,out,err}`, `figures.{start,out,err}` and `check.{start,out}`;
  - `outputs-sha256.txt`.
- **The ledger:** four rows in `fd/LEDGER.tsv`, 0 node-h.
- **Retention:** `/pscratch/sd/j/josephrb/fd-g-figures-20261027` (the deploy clone, the figures at 244 kB, the data
  product at 96 kB, and the logs) joins the pscratch list (binding condition 5).

## 4. Not changed

- Every readout, covariance and cell, and `docs/analysis-note/**`.
- No step was rerun or repaired.
- Captions, the reading of any figure, claims, release text and printed wording are Joseph's.
