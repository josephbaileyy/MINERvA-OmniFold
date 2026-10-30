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
record adds the block because of that outcome, as decision item 2 requires. It says so in every product's label (§2.3).

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

Every with-block readout's label set gains two `context` strings, copied from the audit report and marked "descriptive;
not a reason for the addition":
- **the DR pair:** "the best detector-response pair (GEANT_Pion#1 with C_resp:meson#1) explains 0.853, 0.560 and 0.617
  of PA's, PB's and PC's noise-weighted offset patterns at |a| ≤ 1.51, reproducing PA's to within noise and not PB's or
  PC's; pairs have no stop role (FD-CT-5B-AUDIT-REPORT.md section 4)";
- **5A against 5B:** "5A's and 5B's mean period offsets agree, PB −2.724 % against −2.699 % and PC +4.671 % against
  +4.806 %, while their patterns about the mean differ beyond the combined noise, with Σ(Δ/σ)² of 81.6 and 192.8 over 16
  cells (FD-CT-5B-AUDIT-REPORT.md section 6)".

The two strings are pinned in the code and tested against the committed audit readout's numbers (§5, control L).

### 2.3 The decision

Every with-block readout's labels carry "added under DECISION-20261030 item 2 after the audit's stop condition did not
fire (FD-CT-5B-AUDIT-REPORT.md); the decision followed the data; published with and without".

## 3. The chain: every consumer, with and without

`fd_cpl_addition.py chain` runs the steps below in order. Each step is a subprocess, `python3 -I -B`, of the deploy's own
tool. The chain stops at the first nonzero exit and writes nothing more.

**The pins.** Each tool already takes a pin set through `run(a, pins=...)` (`fd_g_compare.py:240`,
`fd_g_diag.py:391`, `fd_g_followup.py:367`, `fd_flux_boot.py:251`, `fd_g_figures.py:865`,
`fd_data_product.py:296`, `fd_f0_regrade.py:524`). In the with arm, a downstream step's pins are its default pins with
only the upstream readout's sha256 replaced, by the sha256 the chain itself computed of the file the previous step just
wrote. No pin comes from the command line. The chain writes every pin set it used into its receipt.

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
| 9 | the data product | `fd_cpl_addition.py product` | new (the bound tool, `fd/receipts-g-figures/run/s2.sh`, for the without arm) | `cpl_block.npz`; Stage G = 4's |
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
- **σ per cell:** √diag/f of C_total + C_resp, C_PL,5D and C_rep,PL, and the ratio of the last to the first;
- **Stage G:** every prediction's χ², ndf and p, total and shape-only;
- **G-DIAG, G-FOLLOWUP and G-SENS2:** every χ² and every per-mode or per-block share that each readout prints at its
  top level, by key;
- **F0b and F1:** each truth's χ², p and |z|-trigger count, and the triggers by group;
- **the flux bootstrap:** every prediction's χ² band percentiles and the uniform-replicate χ².

The field lists are fixed in the code, by readout key, and tested against the committed readouts (§5, control T). The
table is a state artifact. `values_fived16.tex` is the paper lane's later step.

## 4. The code

**New:** `nd-unfolding/fd_cpl_addition.py`, with four subcommands:
- `block` (§1);
- `product`, the data product with the block. It reuses `fd_data_product.py`'s own functions (`h2_relation`,
  `correlation`, `matrix_csv`, `cells_csv`, `read_matrix_csv`) by import, not retyped. It writes the four matrices of
  the current product plus `C_PL5D` and `C_total_plus_C_resp_plus_C_PL5D`, the correlation of the latter, and every
  relative σ;
- `table` (§3.1);
- `chain` (§3).

**Parametrized, each keeping its current output under its default arguments** (control R tests that):
- `fd_flux_boot.py`: its labels at `:22-24`, `:96` and `:355` name "C_resp" literally. They are built from
  `--extra-block-name` instead. With the name `C_resp`, every label string is unchanged;
- `fd_g_figures.py`: K1's `xb["name"] == "C_resp"` (`:181-183`), K2's literal covariance names and its F0b key
  `relative_sigma_plus_C_resp` (`:275-283`), and `REPORTED` (`:76`) follow a new `--reported-block-name`, which
  defaults to `C_resp`;
- `fd_deposit_candidate.py`: the matrix key `C_total_plus_C_resp` (`:146`, `:161`, `:240`), the covariance label
  (`:77-81`), the source paths (`:163`, `:189`) and `PINS` (`:60-61`) become a variant passed into `package`,
  `reference` and the checks. The CLI gains `--variant with-cpl`, and in that variant the pins are read from the chain's
  receipt. The default variant is today's.

**Unchanged:** `fd_g_compare.py`, `fd_g_diag.py`, `fd_g_followup.py`, `fd_f0_regrade.py`, `fd_g_figures_check.py`,
`fd_data_product.py`, and every committed readout.

**Tests:** `nd-unfolding/tests/test_fd_cpl_addition.py`, plus additions to the three parametrized tools' suites.
- Each of the three tools' suites must still pass unchanged.
- **Mutation receipt** and **independent review:** as for the audit, under `fd/receipts-ct/5b/addition/`.

## 5. Controls (each refuses with nothing further written)

| | control |
|---|---|
| **A** | the audit readout's sha256 is `6d34d7f8…`, its `stop_condition.stop` is false, and its `inputs_sha256` name this S1 assembly, C_resp and 5B readout |
| **B0** | every input's sha256 is its pin: `s1_assembly.npz`, `cresp.npz`, `fd_ct_5b_periods.json`, the audit readout, the definition |
| **B1** | P is 16 × 16, symmetric, PSD and of rank 2; √diag(P) equals the 5B readout's `sigma_rel` to 10⁻¹²; its trace share of M + P equals the 5B readout's `trace_share` |
| **B2** | C_rep,PL = C_e + C_model_abs + C_resp + C_PL,5D,abs = cresp.npz's C_total_resp + C_PL,5D,abs, to 10⁻¹² relative; C_rep,PL is positive definite |
| **B3** | the npz is read back key by key, and its sha256 equals the readout's |
| **R** | each without-arm output's numbers equal its committed readout's, to 10⁻¹² relative. Every int, float and bool leaf is compared; strings, argv, paths and code digests are listed and excluded. For the data product and the deposit candidate, the files are byte-compared, except the code digest field |
| **C** | in the with arm, each step's readout names X's sha256, key, name and role, and the upstream readouts' sha256, as the chain computed them |
| **S** | the with arm's reported relative σ equals √diag(C_rep,PL)/f from `cpl_block.npz`, to 10⁻¹², in Stage G's, F0b's, the data product's and the deposit's readouts |
| **L** | the label and context strings (§2) are present in every with-arm readout the chain writes itself (block, product and table). The context numbers equal the audit readout's to their printed digits |
| **T** | the table's field lists exist in the committed readouts; each "without" number is the committed readout's, byte for byte as printed |
| — | each tool's own controls, unchanged |

Any refusal is reported unrepaired, and the addition is not complete until a bound rerun passes.

## 6. Order, cost and platform

1. this declaration, with its code, bound once;
2. a deploy at the bound pin into `BA=$P/fd-ct-5b-addition-<date>`, which must not exist beforehand. The deploy must
   show HEAD = pin, 0/0 porcelain lines, the §8 digests, and every test module named in §4 passing with no skip;
3. `fd_cpl_addition.py chain`, once, on a login node;
4. `FD-CT-5B-ADDITION-REPORT.md` as a PR to the director.

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

To be filled when the code is committed. Inputs pinned now:

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
4. **Code in this PR,** bound once, as with the audit (#546), unless you would rather bind this design first.

## 10. Not changed

- every committed readout, data product, deposit file and figure, and the reported matrix C_total + C_resp until the
  paper lane's step;
- `docs/analysis-note/**`, claims and printed wording;
- 1B's matrix; the §8.3 (B) readouts; κ; the 2D result.

Nothing is submitted, deposited or tagged.
