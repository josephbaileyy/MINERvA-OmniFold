# RDX code6: the reader, `rdx_read.py`, rev 2 (receipt)

**By** session tier3-design, at the director's ruling of 2026-11-17 on the readings step. That ruling took the fetch
route at 0 node-h:
1. this reader, numpy only, modelled on `rsn/rsn_read.py`, with tests and a mutation harness;
2. independent audits (Codex and Grok), then addendum J7. J7 binds the reader's sha, the fetch connect's sha, the
   laptop read in a clean clone at the bound sha, and the route of the outcome record;
3. the fetch connect, whose sha goes to the director before it runs.

**Rev 1** (`372bd471`, PR #1216) was audited by both readers at `03e43c91`. Codex read FAIL and Grok PASS WITH FIXES.
They agree that §4's formulas are right and that the gaps are in input validation. **Rev 2** (`47f0bb30`) makes the
director's seven fixes (below). The reports are `~/codex-reports/rdx-read-audit/{codex,grok}/report.md`.

**Nothing has been read.** No product has been fetched. This receipt is of the code only.
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `47f0bb30`

| file | sha256 | role |
|---|---|---|
| `nd-unfolding/rdx/rdx_read.py` | `47cc508df3d59c5db7ab2a9ab1520ed524b84e6d58f7199295657f9d84e94d6c` | the reader |
| `nd-unfolding/rdx/test_rdx_read.py` | `1ed6f037a5666e9d5c7bba72565e495cfa71e05b8c6b1835d1f592f338e96687` | 30 tests |
| `nd-unfolding/rdx/rdx_read_mutation.py` | `b0fdaf752900fe304239f2a74011e8501dfc8c9729a0b6f09477153ecbb413e1` | 44 mutants |

It imports, unchanged: `rsn/rsn_read.py` (`4dd37197…`) for the W and T classes, the rounding floor and the committed
record paths, and `pv-ladder/build_cmodel5d.py` (`aaa81575…`) and `pv-ladder/pvl_lib.py` for the definition, the fine
grid and the cell integrals.

## What it does (RDX-DECLARATION.md §4)

**Refusals, each a `[FAIL]` before anything is written:**
- **The task table.** `rdx_tasks.tsv` must be at its bound sha256 (`3ec50691…`, `RDX-DECLARATION.md:240`), with §4's
  fifteen tasks once each and jobs S3a or S3b. A sums manifest that repeats a key refuses.
- **The products and logs:**
  - the product directory must hold exactly the fifteen `.npz`;
  - each job log (`--log-s3a`, `--log-s3b`) must print each of its own tasks' `sha256sum` line exactly once
    (`sbatch_rdx_arms.sh:129`);
  - a line naming `/products/` that is not `<sha256>  <path>/products/<task>.npz` is malformed and refuses, while
    ordinary chatter is ignored;
  - an undeclared task refuses, and so does a task printed in the other job's log;
  - each product's sha256 must be the one its job printed.
- **The arrays, as the producer writes them** (`pvl_unfold.py:198-200`):
  - `xsec_flat` is float64 of the fine grid's 65,856 cells and finite;
  - `shape` equals the fine grid (14, 16, 7, 7, 6);
  - `xtrue_flat` is present on exactly the eight closures, with the same rules;
  - no other array is present.
- **The meta, as the producer writes it** (`pvl_unfold.py:189-197`, `rdx_unfold.py:230-240`):
  - rung, arm, features, closure, the tune_v1 ratio, seed 42, 5 iterations, 32 threads, and the input and background
    pins;
  - X0's estimator and refinement parameters, which must be present, and every other product's equal to X0's;
  - the RDX options;
  - for an instrumented step, fit and predict counts of 5, a row count, and five positive weight sums on a weighted
    step; an uninstrumented step records none of these;
  - the A7 hypothesis pin (`0080495c…`, `rsn_unfold.py:60`) on exactly the A7 GiBUU step;
  - on exactly the two transfer steps, five records with `rsn_unfold.summarize`'s fields, iterations 0–4 in order, 16
    cells each finite or None, 10 deciles and 11 edges.
- **NC-X, bitwise.** "The product" here means the arrays a product carries besides its meta: `xsec_flat` and `shape`.
  The meta differs between X0 and X0_lat by the declared input pins. Both arrays must match in dtype, shape and bytes,
  so +0 against −0 refuses, and so does a dtype change. "If NC-X fails, nothing is read."
- **The closure families.** §4 calls X0c, X1c, X1pc and X1wc "the same closure", and likewise each GiBUU pair and each
  q3 pair. Their `xtrue_flat` must be bitwise equal within each family.
- **φ_c, σ_c and the integrals.**
  - φ_c and σ_c must be 16 finite positive values; a NaN or inf σ could otherwise license.
  - Every cell integral must be 16 finite values.
  - A relative difference needs a positive reference.
  - Every computed value must be finite, and the JSON is written with `allow_nan=False`.

**φ_c and σ_c are read only from their committed records,** through RSN's bound reader:
- φ_c is `i0.json`'s data jitter over `cmodel_5d.json`'s P5 integrals. `rounding_floor` refuses unless it reproduces
  the printed 0.133 / 0.055 / 0.252 %.
- σ_c is `fd_f1_readout.json`'s `relative_sigma_plus_C_resp + C_PL5D` C_total.
- The reader has no option to substitute either.

**The readings:**
- **R1p:** δp = X1p/X0 − 1.
- **R1:** δ1 = X1/X0 − 1, with the excess e_c = |δ1_c| − |δp_c| against 0.5 σ_c; cells are named.
- **R2:** X1w/X1 − 1.
- **R3:** the last iteration's t_c for X1t and X0t and their difference, with a bitwise check of whether the probe
  left the loop untouched.
- **R4:** the closures against their family's truth. The prior's attributable change is stored exactly as it is
  classed, clipped.

The W and T classes are RSN's. The outcome follows §4, in its own characters:
- **REFIT NULL W2**, which takes precedence;
- **LICENSED**, with §4's sentence (E_ν, σ), tested against the declaration's text;
- **STATED SENSITIVITY**, with the cells named.

## The six reader choices, with the auditors' views

The director's reading is that choices 1, 2, 5 and 6 are consistent with §4. Choices 3 and 4 can flip an outcome, so
the auditors' views are set out in full here, for J7.

| # | choice | Codex | Grok |
|---|---|---|---|
| 1 | a cell is named when e > 0.5σ strictly | decided by §4 (D:501 licenses equality, D:505 says >) | decided by §4; it is RSN's W2 boundary. A test now hits the exact tie (`test_an_excess_exactly_at_half_sigma_is_licensed`) |
| 2 | R4 against each closure's truth, b = X/X_true − 1 | decided for normalization; "own truth" means the family's common truth, which must be enforced | decided by §4 and RSN §3.3:277. **Rev 2 enforces the family truth (fix 3)** |
| 3 | prior: max(0, \|Δb(X1c)\| − \|Δb(X1pc)\|) | **not explicitly decided.** "Beyond" gives no formula. The clip is conservative against a false sensitivity but **not** against licensing. Example: change 0, null 0.02, φ 0.001, σ 0.02 gives W0 clipped, W2 unclipped. Bind it rather than assume it | **the one choice §4 does not settle.** It applies R1's excess formula to the closures. It is the **less conservative** algebra when the null exceeds the signal, or when the two are equal and of opposite sign; a signed residual Δb − Δb_null would flag that case. J7 has to accept it. Rev 2 stores the clipped vector that is classed (fix 2), and a test covers \|change\| < null |
| 4 | GiBUU and q3 read in full, with no null | **decided** (D:470-473, :495; D:580-581 "unadjusted"). Conservative against subtracting an undeclared null | **decided.** There is no "beyond" at those truths and no null arm in the task table. The conservative direction |
| 5 | X1wc − X1c qualifies; it is not an outcome change | not unambiguous: it is listed in R4, but D:507 names only R2 and R3 as qualifiers. Including it could flip the outcome to a sensitivity | decided by the outcome rule, which names "all three truths"; the weight is the closure analogue of R2 |
| 6 | a cell with no masked rows fails T0 and T1 | decided by incorporating RSN; cannot change the outcome | decided by incorporating RSN §3.5:337; conservative for the T label |

**For J7,** in short:
- Choice 4 is decided by §4, per both auditors.
- Choice 3 is the open one. The reader implements R1's clipped magnitude excess. The alternative is the signed
  residual Δb(X1c) − Δb(X1pc), W-classed. It would flag a change of equal size and opposite sign to the null, and it is
  the more conservative toward licensing.
- Choice 5 is read differently by the two auditors.

## The receipts, in a clean clone at `47f0bb30` (`receipts.sh`, sha256 `e3498ff1…`)

| file | result |
|---|---|
| `tests.txt` | Python 3.12.2, numpy 1.26.4: 30 tests OK, exit 0 |
| `tests_py310.txt` | a uv venv matching omnifold_py310's versions (Python 3.10.20, numpy 2.2.6): 30 tests OK, exit 0 |
| `mutation.txt` | the unmutated suite: 30 tests OK. Mutation check PASS: 44 of 44 killed, each by its named test |
| `committed_path.txt` | the committed-record path with no products: the task table at its bound sha; the fine grid (14, 16, 7, 7, 6) = 65,856 cells, which the definition maps to 16 cells, so `main`'s check passes; φ_c reproduces 0.133 / 0.055 / 0.252 %; σ_c gives 16 values; the pins load. The clone is clean after it |

**What the tests cover, each guard in both directions.** On synthetic products, with the cell integrals as the
identity:
- NaN, inf and length-1 inputs, in σ, φ, `xsec_flat`, the integrals and `cell_bias`;
- the family truths, both within a family (refuse) and between families (the declared design);
- NC-X on a one-ulp change, on +0 against −0, and on `shape`'s dtype;
- duplicate and wrong-job log lines, malformed product lines, extra and missing products, and a modified task table;
- the transfer schema;
- absent parameters;
- the exact half-σ tie;
- R4 at W1 still licensing, and R2 at W2 and R3 at T2 leaving the label unchanged;
- refit-null precedence over a simultaneous sensitivity;
- the clipped prior excess.

`committed_path.txt` covers what the tests cannot: the real definition, floor and σ, loaded through the reader.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the reader's code and its shas, its refusals, its interpretations as listed, and these receipts.
- **Not citable for:**
  - any RDX reading or outcome: nothing has been fetched or read;
  - a ruling on choices 3 and 5, which is J7's.

  The outcome record, once J7 binds the read, goes to main. Any note-facing text goes to a side branch, off
  `draft/note-round2` until after 2026-11-19.
