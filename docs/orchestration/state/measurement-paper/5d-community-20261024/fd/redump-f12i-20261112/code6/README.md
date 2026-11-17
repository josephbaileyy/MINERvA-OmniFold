# RDX code6: the reader, `rdx_read.py` (receipt)

**By** session tier3-design, at the director's ruling of 2026-11-17 on the readings step. That ruling took the fetch
route at 0 node-h:
1. this reader, numpy only, modelled on `rsn/rsn_read.py`, with tests and a mutation harness;
2. independent audits (Codex and Grok), then addendum J7. J7 binds the reader's sha, the fetch connect's sha, the
   laptop read in a clean clone at the bound sha, and the route of the outcome record;
3. the fetch connect, whose sha goes to the director before it runs.

**Nothing has been read.** No product has been fetched. This receipt is of the code only.
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `372bd471`

| file | sha256 | role |
|---|---|---|
| `nd-unfolding/rdx/rdx_read.py` | `3ff59b611e50558654485cb83ecd5fc8bb1b1fbe837b2e0efb3dfd3ae12ba9fb` | the reader |
| `nd-unfolding/rdx/test_rdx_read.py` | `403933879eeabbeed69655aca52198df17a125f398b53a6eb311a52d674f6e03` | 18 tests |
| `nd-unfolding/rdx/rdx_read_mutation.py` | `cad7fe4ab6ad37d8ed7665e630bb3583c9bc61af05a062091e0624a0d1da2b83` | 22 mutants |

It imports, unchanged: `rsn/rsn_read.py` (`4dd37197…`) for the W and T classes, the rounding floor and the committed
record paths, and `pv-ladder/build_cmodel5d.py` (`aaa81575…`) for the definition and the cell integrals.

## What it does (RDX-DECLARATION.md §4)

**Refusals, each before anything is written:**
- **A product whose sha256 is not its job's.** `sbatch_rdx_arms.sh:129` prints `sha256sum` of every product it wrote
  into the job log, and the reader takes both job logs. Each of the fifteen tasks must be printed exactly once, and no
  undeclared product may appear.
- **A product whose meta is not its declared task's** (`rdx_tasks.tsv`), checked on:
  - rung L-5D-PV, arm e, the five features;
  - closure or not;
  - the tune_v1 ratio (`13bb1eae…`);
  - seed 42, 5 iterations, 32 threads;
  - the input and background pins of `rdx-inputs-SHA256SUMS`, with `lat_zero` for X0_lat;
  - X0's estimator and refinement parameters;
  - the RDX options (features, permutation seed, weight, truth, transfer, the sidecar's sha);
  - the fit, predict and transfer-record counts;
  - a truth reference on exactly the eight closures.
- **NC-X:** X0's `xsec_flat` must equal X0_lat's bitwise. "If NC-X fails, nothing is read."

**φ_c and σ_c are read only from their committed records,** through RSN's bound reader:
- φ_c is `i0.json`'s data jitter over `cmodel_5d.json`'s P5 integrals. `rounding_floor` refuses unless it reproduces
  the printed 0.133 / 0.055 / 0.252 %.
- σ_c is `fd_f1_readout.json`'s `relative_sigma_plus_C_resp + C_PL5D` C_total.
- The reader has no option to substitute either one.

**The readings:**
- **R1p:** δp = X1p/X0 − 1.
- **R1:** δ1 = X1/X0 − 1, with the attributable excess e_c = |δ1_c| − |δp_c| against 0.5 σ_c; cells are named.
- **R2:** X1w/X1 − 1.
- **R3:** the last iteration's t_c for X1t and X0t, and their difference. It also reports whether X1t = X1 and
  X0t = X0 bitwise, that is, whether the probe left the loop untouched.
- **R4:** the closures, each against its own truth.

The W and T classes are RSN's. The outcome follows §4:
- **REFIT NULL W2**, when R1p is W2;
- **LICENSED**, with §4's sentence verbatim;
- **STATED SENSITIVITY**, with the cells named.

## The choices §4 leaves to the reader (for the audits and J7)

The readout records these as `interpretations`:
1. **R1's excess:** a cell is named when e_c > 0.5 σ_c. Equality is not named, as in RSN's W classes.
2. **R4 against each closure's own truth:** b = X/X_true − 1 on the 16 cells, rsn_cmodel's closure bias. A change is
   the difference of two such biases.
3. **R4 at the prior:** the attributable change is |b(X1c) − b(X0c)| − |b(X1pc) − b(X0c)| per cell, clipped at 0, then
   W-classed.
4. **R4 at the A7 GiBUU hybrid and the q3 tilt:** no refit null was declared there, so b(X1) − b(X0) is read in full.
   That is the conservative choice.
5. **R4's X1wc − X1c** (the weight at the prior) is reported and W-classed beside R2, as a qualifier. It is not one of
   the outcome's "attributable changes at all three truths".
6. **R3's difference:** t_c(X1t) − t_c(X0t), T-classed. A cell with no masked rows is None and fails T0 and T1, as in
   RSN.

## The receipts, in a clean clone at `372bd471` (`receipts.sh`, sha256 `ff9d8019…`)

| file | result |
|---|---|
| `tests.txt` | Python 3.12.2, numpy 1.26.4: 18 tests OK, exit 0 |
| `tests_py310.txt` | a uv venv matching omnifold_py310's versions (Python 3.10.20, numpy 2.2.6): 18 tests OK, exit 0 |
| `mutation.txt` | the unmutated suite: 18 tests OK. Mutation check PASS: 22 of 22 killed, each by its named test |
| `committed_path.txt` | the committed-record path with no products. The definition gives 16 reporting cells; φ_c reproduces 0.133 / 0.055 / 0.252 %; σ_c gives 16 values; the 15 tasks and the pins load. The clone is clean after it |

The tests exercise every refusal and every outcome on synthetic products, with the cell integrals as the identity.
`committed_path.txt` is what they cannot show: that the real definition, floor and σ load through the reader.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the reader's code and its shas, its refusals, its interpretations as listed, and these receipts.
- **Not citable for:** any RDX reading or outcome. Nothing has been fetched or read. The outcome record, once J7 binds
  the read, goes to main. Any note-facing text goes to a side branch, off `draft/note-round2` until after 2026-11-19.
