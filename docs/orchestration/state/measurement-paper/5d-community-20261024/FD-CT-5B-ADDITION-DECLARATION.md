# DECLARATION: the addition of C_PL,5D to the 16-cell reported covariance, with every product recomputed with and without it (2026-10-30)

**By** the measurement session `coverage-5b-audit` (ListAgents), for the director to bind.

**Under** [`DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md`](../../../DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md)
(PR #542, sha256 `2c3031d1…`), item 2: "the block is added unless the audit's stop condition fires. The results are
published with and without it, and the record states that the decision followed the data. The revised covariance flows
through every downstream product".

**After:**
- [`FD-CT-5B-AUDIT-DECLARATION.md`](FD-CT-5B-AUDIT-DECLARATION.md) (`65213f15…`) §8, which fixed the matrix, its label and
  the products before the audit ran;
- [`FD-CT-5B-AUDIT-BINDING.md`](FD-CT-5B-AUDIT-BINDING.md) (PR #552), which bound it;
- [`FD-CT-5B-AUDIT-REPORT.md`](FD-CT-5B-AUDIT-REPORT.md) (PR #555, `ff01a7a3…`), whose readout
  `fd/readout/fd_ct_5b_audit.json` (`6d34d7f8…`) records **`stop` = false**;
- the director's message of 2026-10-30 asking for this declaration. Its scope is quoted in §0.

**The addition followed the data.** The block was constructed after the period double ratios were seen
(`FD-CT-5B-REPORT.md`). Its audit's stop condition was fixed before any audit number was read, and it did not fire. This
record adds the block because of that outcome, as decision item 2 requires. It says so in the label of every product
this record's code writes: the block, the data product, the deposit candidate and the table (§2.3). The bound tools'
readouts keep their own labels, and each names the block's file and sha256.

**Declares:**
- the revised matrix, exactly, and the file that carries it (§1);
- its label (§2);
- every §8.3 (A) consumer, recomputed with the block and, at the same code, reproduced without it (§3);
- the code: one new module and three parametrized tools (§4);
- the controls (§5), the order and cost (§6), and the committed outputs (§7).

**MEASURES:** nothing. No product with the block has been computed.

**CANNOT AUTHORIZE:**
- any change to the paper, the note or `docs/analysis-note/**`. They change later, through the usual truth and register
  checks, as a separate step for the paper lane;
- any write over a committed product. Every new output goes to a new path (§7);
- a reading, a claim or printed wording;
- a change to 1B's tested matrix, which is C_total + C_resp by its binding (decision item 3);
- recomputing the readouts in §8.3 (B), which stay in M as recommended;
- any Slurm job, GPU use or write to CFS.

**CITABLE FOR:** what will be computed, from which inputs and code, with which controls, and where it is written.

**NOT CITABLE FOR:** any result; a validated size for C_PL,5D, since a block built from the observed differences contains
them by construction; the cause of a period difference; a coverage or calibration statement.

**Paths:** a bare `.md` name is in this directory. Paths beginning `docs/`, `nd-unfolding/` or `publication/` are from
the repository root. `$P` = `/pscratch/sd/j/josephrb`. `fd/` is this directory's `fd/`.

## 0. Summary

**The director's scope** (message of 2026-10-30):
- "Build C_total + C_resp + C_PL,5D exactly as §8.1 states. Write it as a NEW data product beside the current one, never
  over it."
- "Recompute every §8.3 (A) consumer with and without the block, each labelled with its matrix: the data product, the
  deposit candidate, the result table, the generator χ², and the F1 and flux-bootstrap readouts where they use the
  matrix."
- "Include the descriptive DR-pair finding and the 5A-vs-5B pattern difference as labelled context, not as reasons."
- "Login node only."

**The plan:**

| §8.3 (A) | consumer | code | with the block | without the block |
|---|---|---|---|---|
| 1 | data product | new, in `fd_cpl_addition.py` | `fd/with-cpl/data-product/` | the committed `fd/data-product/`, reproduced by the bound tool |
| 2 | deposit candidate | `fd_deposit_candidate.py`, parametrized | `fd/with-cpl/deposit-candidate/` | the committed `fd/deposit-candidate/`, reproduced |
| 3 | the result table | new, in `fd_cpl_addition.py` | `fd/with-cpl/table/`: every matrix-dependent number, with and without | (in the same table) |
| 4 | Stage G | unchanged | `fd/with-cpl/readout/fd_g_readout.json` | the committed readout, reproduced |
| 4 | G-DIAG, G-FOLLOWUP, G-SENS2 | unchanged | `fd/with-cpl/readout/` | the committed readouts, reproduced |
| 4 | the figures | `fd_g_figures.py`, parametrized; the check unchanged | `fd/with-cpl/figures/` | the committed sidecars, reproduced |
| 5 | F0b and F1 | unchanged | `fd/with-cpl/readout/` | the committed readouts, reproduced |
| 6 | the flux bootstrap | `fd_flux_boot.py`, labels parametrized | `fd/with-cpl/readout/` | the committed readout, reproduced |

**"Reproduced"** means that the chain reruns the bound tool, at this record's deploy pin, on the committed inputs with
C_resp alone. Every number must equal the committed readout's to 10⁻¹² relative (control R, §5). So the with-and-without
difference is the block's alone, not a difference of code versions. That matters here: the committed F0b readout records
`fd_f0_regrade.py` `37427d9d…`, while main is `0dfa722c…`, and the flux bootstrap's readout records `f82bd4f4…`, from
before its label fix.

**Cost:** 0 node-h. One chain on a login node, CPU only, under 30 minutes in all (§6).

## 1. The matrix, exactly

As `FD-CT-5B-AUDIT-DECLARATION.md` §8.1:

  **C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs,** on R00–R15, in S1's absolute units (cm²/nucleon)².

- C_e, C_model_abs, C_total = C_e + C_model_abs and f are `s1_assembly.npz`'s (`db000707…`). C_resp and C_total_resp
  are `cresp.npz`'s (`4d8b5797…`).
- **(C_PL,5D,abs)_ij = f_i f_j P_ij,** with P being `C_PL5D.C_PL5D_rel` of `fd/readout/fd_ct_5b_periods.json`
  (`a5b17895…`), read from its JSON floats and not rebuilt. It is undebiased and of rank 2.
- **The combined block** that every tool takes as its one extra block is **X = C_resp + C_PL,5D,abs**, named
  **`C_resp + C_PL5D`**. Then every tool's reported matrix C_total + X is C_rep,PL.
- **Its name in matrices and files** is `C_total_plus_C_resp_plus_C_PL5D`. For a prediction g, Stage G's matrix is
  C_total + X + V_g.

**The file** is `cpl_block.npz`, written by `fd_cpl_addition.py block`, with these keys:

| key | content |
|---|---|
| `f` | S1's f |
| `P_rel` | P, 16 × 16 |
| `C_PL5D` | C_PL,5D,abs |
| `C_resp` | cresp.npz's `C_resp`, copied |
| `C_resp_plus_C_PL5D` | X, the extra block |
| `C_total_plus_C_resp_plus_C_PL5D` | C_rep,PL |

- **Written byte-reproducibly:** a stored (uncompressed) zip with fixed member order and timestamps, float64
  little-endian arrays. The same inputs give the same sha256 (tested), so the binding's later steps can pin it from the
  builder's own readout.
- **The builder's readout** is `cpl_block.json`. It holds the npz's sha256, the inputs' sha256, the controls passed,
  and C_PL,5D's relative σ, rank and trace share.

## 2. Its label

### 2.1 The block

The audit's §8.2 label, as fixed before the audit ran:
- 5B's NOT CITABLE FOR, except "a covariance component or a change to the reported matrix", which decision item 2 and
  the audit's outcome supersede;
- "audited (FD-CT-5B-AUDIT-REPORT.md); added after the data were seen; published with and without";
- the three-period interval [0.73, 2.56] on its σ;
- the noise-dominated cells R00 and R08.

### 2.2 Context, labelled as context and not as a reason (the director's instruction)

The label set of every product this record's code writes (the block, the data product, the deposit candidate and the
table) gains two `context` strings, copied from the audit report and marked "descriptive; not a reason for the
addition":
- **the DR pair:** "the best detector-response pair (GEANT_Pion#1 with C_resp:meson#1) explains 0.853, 0.560 and 0.617
  of PA's, PB's and PC's noise-weighted offset patterns at |a| ≤ 1.51, reproducing PA's to within noise and not PB's or
  PC's; pairs have no stop role (FD-CT-5B-AUDIT-REPORT.md section 4)";
- **5A against 5B:** "5A's and 5B's mean period offsets agree, PB −2.724 % against −2.699 % and PC +4.671 % against
  +4.806 %, while their patterns about the mean differ beyond the combined noise, with Σ(Δ/σ)² of 81.6 and 192.8 over 16
  cells (FD-CT-5B-AUDIT-REPORT.md section 6)".

The two strings are pinned in the code and tested against the committed audit readout's numbers (§5, control L).

### 2.3 The decision

The same products' labels carry "added under DECISION-20261030 item 2 after the audit's stop condition did not
fire (FD-CT-5B-AUDIT-REPORT.md); the decision followed the data; published with and without".

## 3. The chain: every consumer, with and without

`fd_cpl_addition.py chain` runs the steps below in order. Each step is a subprocess, `python3 -I -B`, of the deploy's own
tool. The chain stops at the first nonzero exit and writes nothing more.

**The pins.** Each tool already takes a pin set through `run(a, pins=...)` (`fd_g_compare.py:240`,
`fd_g_diag.py:391`, `fd_g_followup.py:367`, `fd_flux_boot.py:251`, `fd_g_figures.py:865`,
`fd_data_product.py:296`, `fd_f0_regrade.py:524`). In the with arm, a downstream step's pins are its default pins with
only the upstream readout's sha256 replaced, by the sha256 the chain itself computed of the file the previous step just
wrote. No downstream pin comes from the command line. The extra block's `--extra-block-sha256`, which F0b, F1, Stage G
and the others take on their command line as before, is the chain's own digest of `cpl_block.npz`, as is F1's
`--f0b-readout-sha256` of step 2's readout. The chain writes every pin set it passes in-process into its receipt and
`pins/`. The without arm passes none: its tools run as their CLIs, on their default pins.

**The without arm** runs each tool with its default pins, on its committed inputs and C_resp, as its last bound run did.
Its outputs go to `without/` and are compared by control R with the committed readouts. They are receipts, not new
products: the committed readouts remain the "without" products.

**The steps** (argv as each last bound run's, cited; only the extra block, the upstream readouts and the output paths
change in the with arm):

| # | step | tool | argv as | with-arm inputs changed |
|---|---|---|---|---|
| 1 | the block | `fd_cpl_addition.py block` | new | — |
| 2 | F0b | `fd_f0_regrade.py` | `fd/receipts-f0b/step3.sh` | `--extra-block` X (`C_resp_plus_C_PL5D`, name `C_resp + C_PL5D`) |
| 3 | F1 | `fd_f0_regrade.py` (F1 options) | `fd/receipts-f1/run/s12.sh` | X; `--f0b-readout` = step 2's, with its sha256 |
| 4 | Stage G | `fd_g_compare.py` | `fd/receipts-g/g2.sh` | X, role `adopted` |
| 5 | G-DIAG | `fd_g_diag.py` | `fd/receipts-g-diag/d2.sh` | X; `g_readout` = step 4's |
| 6 | G-FOLLOWUP | `fd_g_followup.py` | `fd/receipts-g-followup/f2.sh` | X; `g_readout` = 4's, `g_diag_readout` = 5's |
| 7 | G-SENS2 | `fd_g_followup.py --part sens2` | `fd/receipts-g-sens2/s2.sh` | X; `g_readout` = 4's, `g_followup_readout` = 6's |
| 8 | the flux bootstrap | `fd_flux_boot.py` | `fd/receipts-flux-boot/run/amended/logs/s2-body.sh` | X; `g_readout` = 4's |
| 9 | the data product | `fd_cpl_addition.py product` | new (the bound tool, `fd/receipts-g-figures/run/s2.sh`, for the without arm) | the committed data product, `cpl_block.npz` and `.json`, Stage G = 4's, the audit readout |
| 10 | the deposit candidate | `fd_deposit_candidate.py build`, then `check` | `fd/deposit-candidate/README.md`, `fd/receipts-deposit/check-login36.sh` | data product = 9's; Stage G = 4's |
| 11 | the figures | `fd_g_figures.py`, then `fd_g_figures_check.py` | `fd/receipts-g-figures/run/s3.sh`, `s4.sh` | readouts 4–7 and F0b = 2's; reported block name `C_resp + C_PL5D` |
| 12 | the table | `fd_cpl_addition.py table` | new | the with-arm readouts and the committed ones |

**Why the steps are in this order:** F1 reads F0b's readout (its control 9). Every Stage G tool reads Stage G's readout.
G-FOLLOWUP reads G-DIAG's, and G-SENS2 reads G-FOLLOWUP's. The data product reads Stage G's, the deposit candidate reads
the data product and Stage G, and the figures read 4–7 and F0b.

**What one combined block costs in detail.** Each tool sees X as one block. So:
- G-DIAG's block shares report `C_resp + C_PL5D` as one block. The table's σ columns separate them (§3.1);
- Stage G's in-readout variant is C_total alone. The "without C_PL,5D" comparison is the committed readout's reported
  one, and the table sets the two side by side.

### 3.1 The table (step 12)

`fd/with-cpl/table/fd_cpl_table.json` and `fd_cpl_table.md`. Each row gives the number without the block (from the
committed readout), the number with it (from the with arm), and their matrices' names.
Its named rows (`curated`, and the `.md`):
- **σ per cell:** √diag/f of C_total + C_resp, C_PL,5D and C_rep,PL, and the ratio of the last to the first;
- **Stage G:** every prediction's χ², ndf and p, total and shape-only, each side with its matrix's name;
- **F0b and F1:** each graded truth's χ², p and count of cells with |z| > 2, with each side's grade matrix, and the
  triggers by group;
- **the flux bootstrap:** each variant's and prediction's total-χ² replicate percentiles 16, 50 and 84.

**Every other number,** G-DIAG's, G-FOLLOWUP's and G-SENS2's included, is in `leaves`: each numeric leaf of each
readout, without and with, at the same path, with keys built from the block's name renamed to the committed spelling. The
committed leaves without a partner are listed (`unpaired_without_leaves`).

The named fields are read from the committed readouts in a test (`Committed`). The table is a state artifact.
`values_fived16.tex` is the paper lane's later step.

## 4. The code

**New:** `nd-unfolding/fd_cpl_addition.py`, with four subcommands:
- `block` (§1);
- `product`, the data product with the block, derived from the committed data product (`b79556f0…`, which passed its
  Q0–Q6) and `cpl_block.npz`. Its cells, boxes, H2 relation, f, C_e, C_model_abs, C_resp and C_total_plus_C_resp are the
  committed product's; C_PL5D and the revised matrix are the block's. It reuses `fd_data_product.py`'s own functions
  (`correlation`, `csv_text`, `matrix_csv`, `read_matrix_csv`, `worst`) by import, not retyped. It writes six matrices,
  the revised one's correlation and every relative σ, as `fd_data_product_cpl*` (controls K0–K6, §5);
- `table` (§3.1);
- `chain` (§3).

**Parametrized, each keeping its current output under its default arguments** (control R tests that):
- `fd_flux_boot.py`: its `units` label and B6's printed line named "C_resp" literally. The label is now built from
  Stage G's reported matrix name (G-DIAG's `comps`, `C_total + <extra block name>`), and B6's line from
  `--extra-block-name`. With the name `C_resp`, adopted, every written string is unchanged. A run with the role
  `sensitivity`, none of them bound, would now read "C_total", which is its reported matrix;
- `fd_g_figures.py`: K1's `xb["name"] == "C_resp"` (`:181-183`), K2's literal covariance names and its F0b key
  `relative_sigma_plus_C_resp` (`:275-283`), and `REPORTED` (`:76`) follow a new `--reported-block-name`, which
  defaults to `C_resp`. The option enters the sidecar's `options` only when it is not the default, and a caller
  whose options lack it (the existing tests' mocks) gets the default, so the default call is today's;
- `fd_deposit_candidate.py`: the matrix key `C_total_plus_C_resp` (`:146`, `:161`, `:240`), the covariance label
  (`:77-81`), the source paths (`:163`, `:189`) and `PINS` (`:60-61`) become a `Variant` passed into `package`,
  `reference` and `check`. `main` is split into `build_args` and `run(a, pins=None, variant=None)`. **The CLI is
  unchanged**: the variant is passed in-process only, by the chain's bootstrap, built by
  `fd_cpl_addition.deposit_variant` with the chain's pins. So the deposit tool names no CPL string. The default
  `Variant` is today's constants.

**Unchanged:** `fd_g_compare.py`, `fd_g_diag.py`, `fd_g_followup.py`, `fd_f0_regrade.py`, `fd_g_figures_check.py`,
`fd_data_product.py`, and every committed readout.

**Tests:** `nd-unfolding/tests/test_fd_cpl_addition.py`, 67 tests, each check in both directions:
- **pure parts:** the npz's bytes (two calls, two processes, a changed array); R's comparison on a committed readout
  (equal to itself; a changed number at 10⁻⁹ found and a last bit not; structure; bools and nulls by type; the
  exclusions); the labels' context numbers against the committed audit readout, and a changed number, a missing label
  and an unmarked context each firing L;
- **the block** on synthetic inputs: written, read back and byte-reproduced; refused on a fired stop, an audit on
  another 5B readout, a pin, rank 3, a σ or trace share not the 5B readout's, an asymmetric P and an existing output;
- **the product:** written beside the without matrix and read back; refused without the chain's pins, on a Stage G σ
  not the revised matrix's, a Stage G on another block name, and a data product whose C_resp or sum is not the block's;
- **the deposit candidate, both directions:** the variant builds and checks the revised matrix and carries the labels;
  the default refuses the revised product; the variant refuses another Stage G pin; the variant's package fails the
  default check; an edited package fails the variant's; the default `Variant` is today's constants;
- **the figures, both directions:** a renamed tree draws under its name; the default name refuses the renamed tree and
  the new name the default tree (K1); the old F0b key and an old matrix name in G-SENS2 each refuse; the default
  records no new option;
- **the flux bootstrap, both directions:** the default `units` label equals the committed readout's; a run on a block
  renamed in Stage G names it in `units`, changes no other label and no number; a name not Stage G's refuses (D5);
- **the chain:** the runner passes pins in-process and sets the tool's argv, and stops on an exit code, a missing output
  or a failed check; the deposit variant reaches the tool through the bootstrap; every step's flags equal its bound
  run's script, in both arms (`StepArgv`); the without arm with each tool replaced by a copy of its committed output
  passes every R check, and one planted difference in a readout, a data product CSV, deposit.json's labels or a PDF
  fires R, while a changed code digest does not (`DryWithout`); the with arm with fakes that record their pins shows
  each step's pins are the files the steps before wrote, and a stale upstream, a readout on another block and a Stage G
  σ off the revised matrix each fire C or S (`DryWith`).

**The three tools' own suites pass,** with one existing test changed: `test_fd_deposit_candidate`'s
`test_the_committed_package_is_what_build_writes` compared deposit.json's bytes, including the tool's own code digest,
which moves with any edit. It now compares the CSVs byte for byte and each JSON by the tool's own `without_code` (P7's
rule), and requires the same `code_sha256` keys.

**Mutation receipt:** `fd/receipts-ct/5b/addition/mutants_5b_addition.{py,log}`, 51 mutants over the four files.
**Independent review:** as for the audit, under `fd/receipts-ct/5b/addition/review/`.

## 5. Controls (each refuses with nothing further written)

| | control |
|---|---|
| **A** | the audit readout's sha256 is `6d34d7f8…`, its `stop_condition.stop` is false, and its `inputs_sha256` name this S1 assembly, C_resp and 5B readout |
| **B0** | every input's sha256 is its pin: `s1_assembly.npz`, `cresp.npz`, `fd_ct_5b_periods.json` and the audit readout; no output exists |
| **B1** | P is 16 × 16, symmetric, PSD and of rank 2; √diag(P) equals the 5B readout's `sigma_rel` to 10⁻¹²; its trace share of M + P equals the 5B readout's `trace_share` |
| **B2** | C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs = cresp.npz's C_total_resp + C_PL,5D,abs, to 10⁻¹² relative; C_rep,PL is positive definite |
| **B3** | the npz is the same bytes when written twice, reads back key by key bit for bit, and its sha256 is the readout's |
| **K0–K6** | the product: no output exists and the chain's pins hold (K0); the committed product passed Q0–Q6 on this S1 and C_resp, the block names its npz, and Stage G adopted this block by name and key (K1); the block's f and C_resp are the product's bit for bit, and the revised matrix is the product's C_total_plus_C_resp + C_PL5D and the sum of its parts to 10⁻¹² (K2); Stage G's σ is √diag(C_rep,PL)/f to 10⁻¹² on every prediction's cells, with its covariance named (K3); symmetry, positive definiteness and C_PL5D's rank 2 (K4); the correlation, and the without matrix's σ the committed product's (K5); every CSV and the JSON read back bit for bit (K6) |
| **R** | each without-arm output against its committed file. **Readouts** (F0b, F1, Stage G, G-DIAG, G-FOLLOWUP, G-SENS2, the flux bootstrap): the same structure (every dict's keys, every list's length) and every int, float, bool and null equal to 10⁻¹² relative (bools and nulls by type); strings are not compared, and `argv`, `code_sha256`, `code` and `versions` are excluded. **The data product:** every CSV byte for byte, and its JSON's numbers and strings equal but `argv`. **The deposit candidate:** the CSVs byte for byte, and deposit.json and predictions-reference.json equal under the tool's own `without_code`, which excludes `code_sha256` only. **The figures:** each PDF byte for byte, and each sidecar's numbers and strings equal but `argv`, `code` and `versions` |
| **C** | a step exits 0 and writes every declared output; the block's readout names the npz it wrote; in the with arm, each readout names the block's sha256 wherever it records the extra block, and each upstream readout's sha256 as the chain computed it (G-DIAG, G-FOLLOWUP, G-SENS2, the flux bootstrap) |
| **S** | the with arm's reported relative σ equals √diag(C_rep,PL)/f from `cpl_block.npz`, to 10⁻¹²: in Stage G's readout on every prediction's cells and in F0b's `relative_sigma_plus_C_resp + C_PL5D`; in the product by K3; in the deposit by its own P2 and P3 |
| **L** | the block, decision and context strings (§2) are in the labels of the block, the product and the table, the contexts marked descriptive; every number a context quotes is the committed audit readout's as printed |
| **T** | the table's "without" pins are the committed readouts'; Stage G's predictions and F0b's and F1's truths are the same, in the same order, on both sides; each Stage G row's without matrix begins C_total + C_resp + V_g, and its with matrix is the without's with C_resp read as `C_resp + C_PL5D` (so the shape-only rows keep Stage G's "+ 100 f f^T (free normalization)") |
| — | each tool's own controls, unchanged |

Any refusal is reported unrepaired, and the addition is not complete until a bound rerun passes.

## 6. Order, cost and platform

1. this declaration, with its code, bound once;
2. a deploy at the bound pin into `BA=$P/fd-ct-5b-addition-<date>`, which must not exist beforehand. The deploy must
   show HEAD = pin, 0/0 porcelain lines, the §8 digests, and these test modules passing with no skip:
   `test_fd_cpl_addition test_fd_deposit_candidate test_fd_g_figures test_fd_flux_boot test_fd_data_product
   test_fd_g_compare test_fd_g_diag test_fd_g_followup test_fd_f0_regrade`, run with root_6_28 activated by prefix;
3. `fd_cpl_addition.py chain`, once, on a login node;
4. `FD-CT-5B-ADDITION-REPORT.md` as a PR to the director.

**The chain's command** (step 3), with `D=$BA/deploy/<pin8>`:

```bash
mkdir -p $BA/tmp && cd $BA && eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" \
  && conda activate $HOME/.conda/envs/root_6_28 && TMPDIR=$BA/tmp timeout 1800 env -u PYTHONPATH python3 -I -B \
  $D/nd-unfolding/fd_cpl_addition.py chain --scratch /pscratch/sd/j/josephrb --run-dir $BA \
  > $BA/logs/chain.out 2> $BA/logs/chain.err; echo "rc=$?" >> $BA/logs/chain.out
```

- **Exit codes:** 0 done; 1 a refusal (any control, in any step), reported unrepaired; 2 argparse; 124 the timeout.
- **What it writes:** `$BA/without/` and `$BA/with/` (each refused if it exists), `$BA/logs/<arm>-<step>.{out,err}`,
  `$BA/pins/<arm>-<step>.json` and `$BA/chain.json`, the receipt of every step and check.
- Every step runs as a subprocess of the same interpreter, with `PYTHONPATH` removed, under its last bound run's
  timeout.

**Cost:** 0 node-h. The last bound runs took 70 s (F0b), 71 s (F1) and at most 7 s each for the rest. Two arms make
about 5 minutes. Each step runs under its last run's timeout, and the chain under 1,800 s.

**Platform:** CPU only, with root_6_28 activated by prefix, as the last runs. Nothing goes to CFS. Every input is on
pscratch: the 10 paths read by F0b and F1 were listed with `ls` on login37 on 2026-10-30.

## 7. Committed outputs (in the report's PR)

- `fd/with-cpl/block/`: `cpl_block.npz` (force-added, about 13 KB) and `cpl_block.json`;
- `fd/with-cpl/readout/`: the with-arm readouts of steps 2–8, under their tools' names;
- `fd/with-cpl/data-product/`, `fd/with-cpl/deposit-candidate/`, `fd/with-cpl/figures/` and `fd/with-cpl/table/`;
- `fd/receipts-ct/5b/addition/run/`: the chain's receipt, the logs, and the without arm's comparisons;
- a ledger row.

F0b's and F1's experiment tables (`--out-npz`) stay on pscratch, as before. Nothing is written into `fd/readout/`,
`fd/data-product/`, `fd/deposit-candidate/`, `fd/figures/` or `docs/analysis-note/`.

## 8. Pinned bytes

### 8.1 The code (repository paths; the deploy checks each)

| file | sha256 |
|---|---|
| `nd-unfolding/fd_cpl_addition.py` | `4eb7c4352400205f2059c891774c42245070af411ca0cf62baafd087e4a6a67a` |
| `nd-unfolding/tests/test_fd_cpl_addition.py` | `26ab33fd175cae1f99754e7778eaf3530777f013e2450f66dac4ab5c2635214b` |
| `nd-unfolding/fd_deposit_candidate.py` | `d50c11ebc1ebc6a99c3004d6844dea7eb6dce065abdc99713edd8f9d4675468a` (was `3f4c5d51…`) |
| `nd-unfolding/tests/test_fd_deposit_candidate.py` | `bd36fe80b02afa4a02409de1a08c84e58e903f67c68f3181b281f47923d6ce68` |
| `nd-unfolding/fd_g_figures.py` | `9c1697f25b00824d58db64dc5aeaf2ba895b9b4e4c4fc6c784807ecc38c9fb81` (was `06233dd9…`) |
| `nd-unfolding/fd_flux_boot.py` | `d5b4bb095b526ad0aa79d09c9d26626ff624acb93fc9bac836b5c0167c769040` (was `cbd5ac9c…`) |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/addition/mutants_5b_addition.py` | `bc8c3e8dc21666aad1e6971a3cfe72cbcb22872effa731ee4d93fd41069d05d0` |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` (unchanged) |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` (unchanged) |
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` (unchanged) |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` (unchanged) |
| `nd-unfolding/fd_data_product.py` | `1a42264faf4d8f3977a1eb5d66fa75604066200ac06e9034188860f9ff6ba8df` (unchanged) |
| `nd-unfolding/fd_g_figures_check.py` | `95cf26811993772063a9d64d862fcde041ec3321f1f69874b99034d88c17d341` (unchanged) |
| `nd-unfolding/tests/test_fd_g_figures.py` | `fb3dcc86e01eb48aaf7bed36bf5f1f25d624e3a6216ba5fddecc892347172fd9` (unchanged) |
| `nd-unfolding/tests/test_fd_flux_boot.py` | `5b585d378fee6c15faad6c94c86c400ddd496dff90e172845bc1cceacacbc280` (unchanged) |

**Locally,** with `-B` and a TMPDIR: `test_fd_cpl_addition` ran 67 tests, OK; with the three tools' and the unchanged
consumers' suites, 403 ran (`test_fd_deposit_candidate`, `test_fd_g_figures`, `test_fd_flux_boot`,
`test_fd_data_product`, `test_fd_g_compare`, `test_fd_g_diag`, `test_fd_g_followup`, `test_fd_f0_regrade`), all OK.
**Mutation:** pass 1 at the working tree, 50 of 51 killed (`mutants_5b_addition-pass1.log`; the survivor, B1's symmetry,
was a test gap and was fixed); pass 2 at `9113a84f`, **51 of 51 killed**, every file restored
(`mutants_5b_addition.log`).

### 8.2 The inputs (as each step reads them)


| file | sha256 |
|---|---|
| `fd/readout/fd_ct_5b_audit.json` | `6d34d7f8034ea956cf22c092fb31d608f330daabdd721285302868806d50692c` |
| `fd/readout/fd_ct_5b_periods.json` | `a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db` |
| `$P/s1-20261024/s1_assembly.npz` | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` |
| `$P/cresp-20261026/out/cresp.npz` | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` |
| `fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` |
| `fd/readout/fd_g_diag_readout.json` | `680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88` |
| `fd/readout/fd_g_followup_readout.json` | `cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379` |
| `fd/readout/fd_g_sens2_readout.json` | `0f6568aba032e5d9a85f945048494d8fccde3525bb45a1762d6f5d5aaf15b77f` |
| `fd/readout/fd_f0b_readout.json` | `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b` |
| `fd/readout/fd_f1_readout.json` | `cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7` |
| `fd/readout/fd_flux_boot_readout.json` | `b7b5652cbd163b6830655250c18bbcfd65f87bb199821c97c7abdbd671e70001` |
| `fd/data-product/fd_data_product.json` | `b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072` |

## 9. For the director

1. **One combined extra block** (§3) keeps five tools unchanged. The cost is that G-DIAG reports C_resp and C_PL,5D as
   one block, and that the table carries the separation. Two blocks would need code in every Stage G tool.
2. **The without arm** doubles a cheap chain to make the difference the block's alone (§0). Without it, F0b's and the
   flux bootstrap's "without" numbers come from older code.
3. **The 5B records' label.** 5B's NOT CITABLE FOR includes "a covariance component". This record supersedes that clause
   for C_PL,5D, as the C_resp adoption did for its records, without editing them. Should the report add a dated status
   line to `FD-CT-5B-REPORT.md`, as CRESP-REPORT.md gained one?
4. **Code in this PR: ruled.** On 2026-10-30 the director asked for the code in this PR, bound once.

## 10. What writing the code found

1. **The committed readouts' strings do not all reproduce.** The flux bootstrap's readout keeps its band records' old
   `LABEL`, by record (`FD-FLUX-BOOT-LABEL-FIX.md`, "That readout keeps the old label"), and F0b's was written by
   `fd_f0_regrade.py` `37427d9d…`. So R compares the readouts' numbers and structure, as §5 always stated, and compares
   strings only on the products: the data product, the deposit candidate and the figures.
2. **The products' JSONs name their run.** The data product's JSON and the sidecars record `argv`, and the sidecars also
   the deploy commit (`code`) and the library versions. Byte equality is impossible across deploys, so R names those
   fields as its only exclusions. deposit.json and predictions-reference.json record no argv, so the tool's own
   `without_code` is their whole rule, as the director asked.
3. **The tools record `sys.argv`,** and G-DIAG's and the flux bootstrap's D5 read Stage G's recorded argv. So the chain's
   bootstrap sets `sys.argv` to the tool's path and its argv before calling `run`, and a test checks it.
4. **One existing test changed** (§4): the deposit candidate's committed-package test compared the code digest.
5. **The figures' existing tests call `MODEL` with mocks** that lack the new option, and plant `ratio_model` with three
   arguments. So the name is passed as a keyword only when it is not the default, and a missing option means the
   default.
6. **The design freeze said the deposit CLI would gain `--variant with-cpl`.** It does not: the variant is in-process
   only, so no pin of the with-block product can come from a command line (§4).
7. **The product is derived from the committed data product,** not rebuilt from S1 and C_resp, so its cells, boxes
   and H2 relation keep the committed product's Q1 checks, and K2 ties the block to it bit for bit.

### 10.1 The independent review and its dispositions

A read-only review in its own detached worktree at `9113a84f`, given the code and this record. Its report is
`fd/receipts-ct/5b/addition/review/REVIEW.txt` (verbatim), with its probes beside it.

| # | finding | disposition |
|---|---|---|
| 1 | **High:** T required every Stage G row's matrix to be "C_total + C_resp + V_g", so the shape-only rows, which Stage G names "... + 100 f f^T (free normalization)", would stop the real chain at its last step; the product fixture agreed with the code, not with Stage G | **Fixed.** T now requires the with matrix to be the without's with C_resp read as the block's name (§5). The fixture uses Stage G's own `compare()` names. A `Table` test runs `table` on the committed readouts: it writes, pairs every leaf, and refuses a with side that kept the old shape-only name, a reordered side, and a without pin not the committed one |
| 2 | **Medium:** T, B2, K4, K5, K6, K0's overwrite, A's `which` and A's 5B-readout clause had no firing test or mutant | **Fixed.** Each has a test in the firing direction and a mutant (63 mutants in all) |
| 3 | Low: pass 1's receipt fails; one mutant was killed by a SyntaxError | Pass 1 is kept as the record of its survivor, which is now killed. The mutant now replaces the clause with `*[]`. Pass 2 is rerun at the final code |
| 4 | Low: three tests refused for another reason (a KeyError; P0 pins) | **Fixed.** The figures report a missing F0b key as K2, and the test asserts it. The two deposit tests are renamed "at its pins", and a new test passes the variant's pins to the default check, which refuses at P2 on the content |
| 5 | Low: `StepArgv` compares flag names only | Kept. The review's probe compared every flag's value for all ten scripts and found them equal (`review/probe_argv.out`) |
| 6 | Low: R does not compare the readouts' strings | **Not changed:** the director accepted R's exclusions as listed, on 2026-10-31. The numbers behind those strings (z, shares, loadings) are compared |
| 7 | Low: R is near bit-exact, so it can fail on environment drift; the PDFs need matplotlib 3.10.8 | Accepted. A spurious R failure is loud and is reported unrepaired, which is the safe direction. root_6_28 on the cluster has Python 3.11.14, numpy 1.26.4 and matplotlib 3.10.8, the versions the committed sidecars record (read on 2026-10-31). An absolute floor would blind comparisons of the cross sections (about 10⁻³⁹) |
| 8 | Low: the table paired predictions and truths by position | **Fixed:** T checks the names and their order (§5) |
| 9 | Low: L tested each quoted number as a substring | **Fixed:** the numbers must appear in the readout's order, and a test swaps PB's and PC's values |
| 10 | Low: R's committed files are not sha-pinned at chain start; the without arm writes no pins | The deploy's HEAD = pin with 0 porcelain lines fixes every committed file to the bound commit. §3 now says the without arm passes no pins |
<!-- absence-ok: the review's findings 2 and 10 describe this PR's own test suite and chain at 9113a84f, as its report states; each is fixed or dispositioned in its row -->

## 11. Not changed

- every committed readout, data product, deposit file and figure, and the reported matrix C_total + C_resp until the
  paper lane's step;
- `docs/analysis-note/**`, claims and printed wording;
- 1B's matrix; the §8.3 (B) readouts; κ; the 2D result.

Nothing is submitted, deposited or tagged.
