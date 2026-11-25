# DECLARATION: V_F's adoption into the 16-cell reported covariance, with every product that depends on it recomputed (2026-11-25)

**By** tier3-design, for the director to bind.

**Under:**
- [`DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md`](../../../DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md)
  (#1326, sha256 `e1316f4a…`) §3: "**V_F is adopted** into the reported 16-cell covariance, with A1 §4's caveat stated
  (the factor measures the toy spread relative to LL5D's rebuilt reference block)";
- Joseph's choice of **C, Phase 1 + Phase 2, with B as the fallback** (the director's relay, 2026-11-25T13:07Z): GO for
  this declaration, the code, the NERSC runs, and a checkpoint by 2026-11-28T00:00Z.

**After:**
- B5D's record (`blocks5d-20261124/RECEIPT.md`, `6277f5cb…`; #1321, follow-ups #1324), which built V_F;
- the scope read (`blocks5d-20261124/vf-input-check-20261125/scope/`) and the input-existence check (#1327): every
  Phase 1 and Phase 2 NERSC input exists and equals its pin;
- codex-school's producer map at main `167b3e25` (`fd/receipts-vf/decl/map-codex.txt`, prompt beside it). Every
  file:line below that isn't otherwise sourced is from that map, re-checked where this record relies on it.

**What this declares:** the matrix (§1), the code (§2), Phase 1 (§3), Phase 2 (§4), the readings table (§5), the
controls (§6), order, cost and the checkpoint (§7), and what is not changed (§8).

**CANNOT AUTHORIZE:** a write over a committed product, any edit under `docs/analysis-note/` (the note lane repins from
the outputs), note or paper wording, a reading, or a claim. Readings go to the director first.

## 0. Summary

- **The matrix.** dF = V_F − C_e, from committed files only. It is added to every matrix that carries C_e, so the
  reported covariance becomes C_rep,F = V_F + C_model_abs + C_resp + C_PL5D = C_rep + dF. The arm without the
  run-period block becomes C_total + C_resp + dF. The note prints both arms, so both move.
- **No byte of any bound tool changes.** The analysis tools already take any extra block under any key and name, and
  take pins in-process. One new module, `nd-unfolding/fd_vf_addition.py`, writes the block, drives Phase 1 and does
  Phase 2's arithmetic by importing each producer's own functions. In this repo, "the fd_cpl_addition change" is
  therefore a new module that imports fd_cpl_addition's helpers; `fd_cpl_addition.py` itself is unchanged.
- **Phase 1** runs the bound producers once on login02 at 0 node-h, in four arms (OLD and V_F, each with and without
  C_PL5D). Every OLD arm must reproduce its pinned readout before any V_F arm runs.
- **Phase 2** recomputes each C_rep-dependent number of eleven readouts locally, with the producer's own functions on
  committed inputs plus one read-only fetch of a few intermediate files. Each recompute must first reproduce the
  committed number with the old matrix.
- **Three Phase 2 readouts are not C_rep-dependent** (ct3b, t2b, e96d; §4.3). They stay unchanged, and are listed for
  Joseph.
- **The readings table** lists every `\fvval` key whose value moves, OLD → V_F, with its print sites. Any
  decision-rule outcome change is listed first.

## 1. The matrix, exactly

**Inputs** (sha256, each checked by the code before use):

| input | path | sha256 |
|---|---|---|
| V_F | `blocks5d-20261124/record/V_F.csv` | `763f14c6ace6e69109fc11ded75d8654615fe55d5e53281e9911bc5318a03e93` |
| B5D's record (L, V_F) | `blocks5d-20261124/record/blocks5d.json` | `c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9` |
| C_e | `fd/with-cpl/data-product/fd_data_product_cpl_C_e.csv` | `222c4dd4efef0780c408b82caa8d360723bc8b73b784885789f374a624e6c715` |
| the with-block data product | `fd/with-cpl/data-product/fd_data_product_cpl.json` | `d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50` |
| the run-period block | `fd/with-cpl/block/cpl_block.npz` | `d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f` |

B5D built V_F = L C_e Lᵀ on this C_e CSV (`b5d_build.py`, its `PINS` and `C_e = scale² · read_csv_matrix(...)`).

**Arithmetic** (float64, in this order, with no symmetrization):
- dF = V_F − C_e;
- the three extra blocks the tools take:

| key in `vf_block.npz` | name in each readout | used by |
|---|---|---|
| `dF` | `dF` | F0, which grades against C_total alone |
| `C_resp_plus_dF` | `C_resp + dF` | every arm without C_PL5D |
| `C_resp_plus_C_PL5D_plus_dF` | `C_resp + C_PL5D + dF` | every reported arm |

  These are formed as `C_resp + dF` and `cpl_block[C_resp_plus_C_PL5D] + dF`;
- the two revised matrices: `C_total_plus_C_resp_plus_C_PL5D_plus_dF` = the data product's
  `C_total_plus_C_resp_plus_C_PL5D` + dF, and `C_total_plus_C_resp_plus_dF` = its `C_total_plus_C_resp` + dF.

`vf_block.npz` holds `f`, `C_e`, `V_F`, the three blocks and the two revised matrices, in that order. It is written
byte-reproducibly by `fd_cpl_addition.npz_bytes` (stored zip, fixed timestamps, `<f8`). `vf_block.json` records the
keys, names, relative σ of each matrix, the input shas and the code shas.

**The block is built locally, before any run, and committed** under `fd/with-vf/block/` with the code's PR. Every
later step reads it by that sha.

**Its label** (in the block, the product, the deposit candidate and the table): "dF = V_F − C_e, V_F = L C_e Lᵀ the 5D
fluctuation block (blocks5d-20261124/RECEIPT.md), adopted into the reported covariance by DECISION-20261125 section 3,
with A1 section 4's caveat: the factor measures the toy spread relative to LL5D's rebuilt reference block". **NOT
CITABLE FOR:** a validated size of V_F; a coverage or calibration statement.

## 2. The code

One new module, `nd-unfolding/fd_vf_addition.py`, with `nd-unfolding/tests/test_fd_vf_addition.py` and a mutation
runner. It imports `fd_cpl_addition` (npz writer, comparisons `compare_numbers`, `compare_strings`, `paired`, `Chain`,
`Paths`, `step_argv`, `extra`) and `fd_gencmp_e` (the chdefs prediction set's chain pieces). Nothing it imports is
edited.

| subcommand | what it does | runs |
|---|---|---|
| `block` | §1, controls V0–V4 | local |
| `chain` | Phase 1 (§3): the four arms, the V_F data product, the deposit candidate, the figures, the table | login02 |
| `p2` | Phase 2 (§4): each readout's recompute, with its OLD control, writing a V_F copy of the readout | local |
| `fetch-list` | prints Phase 2's fetch list (§4.2) with each file's pin, for the connect script | local |

**Overrides, all in-process, all recorded.** Where a producer's function is called with a pin set or a prediction set,
it is the same `run(a, pins=..., predictions=...)` entry that fd_cpl_addition's and fd_gencmp_e's chains already use
(`BOOT`). No module attribute of a bound tool is reassigned.

**Reads and tests before any run:**
- the unit tests;
- a mutation run in which every mutant compiles first, and one that doesn't compile is reported INVALID, never
  killed;
- a read of the code by codex-school `gpt-6.2-sol` (reasoning high), and a second read by claude-personal Sonnet 5.5
  (`claude -p --model claude-sonnet-5-5`, read-only tools, in a copy directory) or codex-school `gpt-6.1-terra`.
  `openusage` is run first, and each reader's model id is recorded;
- the director's binding of the code's sha.

The Phase 1 and Phase 2 parts may be bound separately. Phase 1's must not wait for Phase 2's.

## 3. Phase 1: the bound producers, rerun

`fd_vf_addition.py chain` runs every step as a subprocess (`python3 -I -B`) of the deploy's own tool, as
fd_cpl_addition's chain does (`Chain.run`). It stops at the first failure.

**The steps and their OLD files** (each OLD file is what `make_values_fived16.py` pins today; argv as the recorded
run's):

| set | step | tool | recorded argv | OLD with C_PL5D | OLD without C_PL5D |
|---|---|---|---|---|---|
| S | F0 | `fd_f0_regrade.py` | `fd/readout/fd_f0_readout.json` argv (:3840) | `fd/readout/fd_f0_readout.json` `6e7d718b` (no block) | — |
| S | F0b | `fd_f0_regrade.py` | `receipts-ct/5b/addition/run/chain.json` :640 | `with-cpl/readout/fd_f0b_readout.json` `5f542830` | `fd/readout/fd_f0b_readout.json` `b9db935a` |
| S | F1 | `fd_f0_regrade.py` (F1) | same, :697 | `with-cpl/readout/fd_f1_readout.json` `5ccc89e5` | `fd/readout/fd_f1_readout.json` `cbe411a9` |
| S | Stage G, original predictions (g0) | `fd_g_compare.py` | same, :768 | `with-cpl/readout/fd_g_readout.json` `b55366b3` | `fd/readout/fd_g_readout.json` `75a9ddee` |
| S | the data product | `fd_cpl_addition.py product` / `fd_vf_addition.py` | same, :1104 | `with-cpl/data-product/fd_data_product_cpl.json` `d6752d2c` | (the matrix without C_PL5D is in the same product) |
| S | the deposit candidate | `fd_deposit_candidate.py build`, `check` | same | `with-cpl/deposit-candidate/` | — |
| E | Stage G, CH analysis definitions (g) | `fd_g_compare.py` | `gencmp-e/rerun1/chain/chain.json` :1187 | `…/chdefs/with/readout/fd_g_readout.json` `a19009e0` | `…/chdefs/nopl/readout/fd_g_readout.json` `d9a1ce38` |
| E | G-DIAG | `fd_g_diag.py` | same, :1231 | `…/with/…/fd_g_diag_readout.json` `522bfafa` | `…/nopl/…` `4e77966e` |
| E | G-FOLLOWUP | `fd_g_followup.py` | same, :1278 | `…/fd_g_followup_readout.json` `586cd741` | `748f3af6` |
| E | G-SENS2 | `fd_g_followup.py --part sens2` | same, :1328 | `…/fd_g_sens2_readout.json` `4bc21dfd` | `6626cb73` |
| E | the flux bootstrap | `fd_flux_boot.py` | same, :1380 | `…/fd_flux_boot_readout.json` `5bb475ea` | `24ff27f9` |
| E | the figures, and their check | `fd_g_figures.py`, `fd_g_figures_check.py` | same | `…/chdefs/with/figures/` | `…/chdefs/nopl/figures/` |

**The four arms:**
- **OLD with** and **OLD without**: each step with the block its OLD file used. That is `cpl_block.npz`
  (`C_resp_plus_C_PL5D`, name `C_resp + C_PL5D`) with C_PL5D, `cresp.npz` (`C_resp`) without it, and none for F0. These
  are the controls (§6, R).
- **V_F with** and **V_F without**: the same steps with `vf_block.npz`. The key is `C_resp_plus_C_PL5D_plus_dF` with
  C_PL5D and `C_resp_plus_dF` without it; F0 takes `dF`.
- Each downstream step's pins are its defaults with only the upstream readouts' sha256 replaced, by the chain's own
  digests of the files the step before wrote. F1's `--f0b-readout` is its own arm's F0b.
- **No V_F arm starts until every OLD-arm control has passed.** A failed control is a STOP: terminal, reported to the
  director unrepaired.

**The V_F data product** comes from `fd_vf_addition.py`'s own `product` step, which mirrors fd_cpl_addition's:
- it starts from the committed with-block data product (`d6752d2c`) and `vf_block.npz`, with the V_F arm's Stage G (g0);
- its matrices are `C_e`, `V_F`, `dF`, `C_model_abs`, `C_resp`, `C_PL5D`, `C_total_plus_C_resp_plus_dF` and
  `C_total_plus_C_resp_plus_C_PL5D_plus_dF`, with the correlation of the last, every relative σ, and the CSVs;
- it checks the K controls (§6).

**The deposit candidate** uses a `with-vf` variant (the reported key, and the label of §1).

**Not in the chain, with the reason:**
- G-DIAG, G-FOLLOWUP, G-SENS2 and the flux bootstrap on the original predictions: the note pins none of them (codex
  map, `MV:40–46`);
- the EA2 label redraw of `fd_g_fig_modes` (`fd_gencmp_ea2.py`, whose control D allows only a label change);
- the note figures `fived16_headline` and `fived16_genresidual`, and `make_supplemental.py`. These pin the data
  product's sha and the old key. They belong to the note and figure lanes, which redraw from this record's outputs.
  The headline and residual figures are listed in §5 as follow-ups.

**Where and how:**
- a deploy of the bound commit into `BA=/pscratch/sd/j/josephrb/vf-20261125-p1`, which must not exist beforehand.
  It is a fresh clone with HEAD = pin, 0 porcelain lines, and each bound blob checked against the receipt list (the
  chain E pattern, `gencmp-e/rerun1/receipts/e_rerun.sh`);
- the test modules pass with no skip: `test_fd_vf_addition`, `test_fd_cpl_addition`, `test_fd_g_compare`,
  `test_fd_g_diag`, `test_fd_g_followup`, `test_fd_flux_boot`, `test_fd_f0_regrade`, `test_fd_g_figures`,
  `test_fd_deposit_candidate`, `test_fd_data_product`, `test_fd_gencmp_e`;
- `conda activate $HOME/.conda/envs/root_6_28`, `env -u PYTHONPATH`, `TMPDIR=$BA/tmp`, and the chain under
  `timeout 3600`;
- it reads only the pinned inputs that #1327 checked, writes only under `$BA`, and writes nothing to CFS.

## 4. Phase 2: each C_rep-dependent number, recomputed locally

### 4.1 The readouts and the method

`fd_vf_addition.py p2` writes, for each readout, `<name>.vf.json` under `fd/with-vf/p2/`. It is the committed readout
with **each C_rep-dependent field the note reads** replaced by its recomputation under C_rep,F, plus a `vf_patch`
block. That block lists every replaced path, the matrix used, and the OLD control's result. The note generator can
then read the V_F copy at the same paths.

**Each recompute calls the producer's own function**, imported unchanged, on its committed inputs. Phase 1's V_F
readouts are used where the producer reads one. The function is first called with the **old** matrix, and every
replaced field must equal the committed value (§6, P). Only then is it called with C_rep,F.

| readout | OLD (pin) | the numbers that move | recomputed from | inputs |
|---|---|---|---|---|
| gdefs | `gencmp/readout/defs.json` `544f4f43` | table χ², p, pulls; `delta_over_sigma`, `seed_spread_over_sigma`, the 0.2σ seed flags; `gdef-dmax`, `-dmax-bound`, `-seedmax` | each embedded comparison record (`cells`, `f`, `g`, `sigma_Vg_over_f`) by `fd_g_compare`'s comparison; the σ ratios by `fd_gencmp`'s functions | committed |
| gch | `gencmp/readout/ch.json` `cd111b8e` | χ², p and pulls of each carbon/CH/H alternative | the same | committed |
| gnat | `gencmp/readout/native.json` `df48fbeb` | the data-versus-prediction χ² | the same. Its "agree" rule (Σz² < 32, max \|z\| ≤ 3.5) uses generator variances only and does not move | committed |
| gover | `gencmp/readout/overlap.json` `82b3528a` | each quadrant's σ16, the agree / agree-below-a-correlation / differ label, ρ*, the 3D standardized differences | aᵀ C_rep,F a + Σ x_b² from the record's `quadrants[q].cells` and `unreported_boxes_P5`, with `fd_gencmp`'s reading function | committed |
| cr | `receipts-cov2d/g2r/cr/run/node/g2r/overlap_refined.json` `0734cf4a` | the same, with G2R's Q_R | the same | committed |
| xk | `receipts-cov2d/g2r/xk/run/node/run/k/k.json` `204e4c89` | every family's χ², p, z, ρ and bounds; X's agreement rule (p ≥ 0.05 and every \|z\| ≤ 2.50) | `fd_xcov` / `fd_xcov_steps`' own step-K functions, with A dF Aᵀ added to the 16-cell side. The r = 0 point is exact from the record (`d`, `own`, `crosses`); the bounded family needs its cross matrix M | committed + **fetch** |
| e2 | `gencmp-e2/rerun1/chi2/e2.json` `0aa73ebf` | both arms' χ², the Δ's, `e2-sig-*`; the "within seed variation" rule and the 2.3 flag | `fd_gencmp_e2`'s `chi2_rows` with the S arrays and V_g = (σ_Vg/f · f)², as E2 itself does | committed |
| e2sens | `gencmp-e2/rerun1/sens/x_e2_sens.out.txt` `223f3f88` | the removed, carbon and doubled-model χ² and σ changes | `x_e2_sens.py`'s arithmetic, on the V_F `e2` | committed |
| eav | `eavail-switch-pricing-20261031/step0/step0_metric.txt` `3e8bd546` | the full-covariance norm, the cell maximum | `step0_metric.py`'s arithmetic, with the matrix passed explicitly. Its "endswith plus_C_PL5D" selection would pick the old matrix | committed |
| prr | `receipts-prr/read/cluster/readout.json` `9238f22b` | PR-3's flags (p < 0.01 or any \|z\| > 2), cleared/retained/new, the χ² and z of each grade | `prr_read`'s grade functions, with X replaced by X_F. The (e) records are exact from `table[...].r` with N = 0. The IBU records need `route2.npz`'s residuals | committed + **fetch** |
| rsnregrade, rsn | `RSN/regrade.json` `cb5f5d17`, `RSN/rsn_readout.json` `6291f48d` | each arm's grades, listings and triggers; WR's and TR's half-σ classes; the G6/SM listing comparisons | `rsn_regrade`'s grade with X_F and the committed F1 experiment table (`selection-20261124/record/selection/fd_f1_experiments.npz` `997c7dae`) for N; then `rsn_read` on it, with Phase 1's V_F F1. The six descriptive row-6 records need the NuE weights | committed + **fetch** |
| V-ATLAS | `valid-region-20261107/receipts/read/readout.json` `91bb604e` | A3 (every graded \|z\| ≤ 2) and the validity list, its V-PRIOR intersection, the GiBUU z's; `reading3`'s cell, quadrant and pair σ | `valid_region`'s reading functions on Phase 1's V_F F0b and the V_F data product | committed + Phase 1 |

`ibu16-dsig-*` (REF-G1's shifts over the reported σ) is the note generator's own arithmetic on `refg1` and `dp`. It
moves with Phase 1's data product. Nothing in REF-G1's own readout moves: its T uses the paired-difference covariance.

### 4.2 The one Phase 2 connect: a read-only fetch

Three recomputes need intermediate files that are on pscratch only:
- xk's step-K cross matrices and bounds (its run directory `cov2d-xk-g2r-20261116/run`; the 171 GB
  `universes_full.root` is **not** read: it was the launcher's identity check, never an input of K);
- PRR's `route2/route2.npz`;
- the NuE flux constraint (`sorted_NuEConstraint_FHC_RHC_IMD.txt`, `e38ad7d2…`) for RSN's row-6 weights.

`fd_vf_addition.py fetch-list` prints the exact files, each with its committed pin and size. The connect is the B5D
fetch pattern:
- one login02 session at 0 node-h, `tar` to stdout of the listed files read through O_NOATIME, with the sha256 of
  each file checked locally against its pin;
- fences and acks: cov2d for its G2R paths and the flux constraint; limitation-resolver for the constraint;
  director-helper-3 if any IBUB path is read.

The list, with sizes, goes to the director before the connect. **If any listed file needs a compute node or an HPSS
stage,** it is priced and sent to the director before anything is submitted. #1327 found every one present on
pscratch.

If a fetched file's sha differs from its pin, that is a STOP. The recompute it serves is reported not done, and nothing
is substituted.

### 4.3 Not C_rep-dependent: unchanged, listed for Joseph

The scope read named these Phase 2 readouts. The producer map shows they don't use C_rep:
- **ct3b** (`fd/readout/fd_ct_mismatch.json`): the historical `C_total_resp` scale, from `cresp.npz`
  (`fd_ct_readers.py:46–49,118–139`). The note prints `abs_delta_over_sigma_total_resp`.
- **t2b** (`tier2-20261110/t2b/t2b.json`): the historical no-playlist grades, and C_e + C_resp, C_stat, C_stat +
  C_resp variants (`t2b_grade.py:22–35,102–127`).
- **e96d** (`e96-data-20261110/.../ANALYSIS.json.txt`): the original data product's `relative_sigma.C_e`
  (`ensemble_estimator_data.py:446–461`).

**Also unchanged:**
- s5p's joint tests and Holm (their own frozen V; `s5p_joint.py:314–323,340–349`);
- LL5D and REGRADE (`rg16`, `rg2d*`): truth-specific C_T. Substituting a nominal dF would need its own prescription
  (codex map, final note);
- the 1B gate; cov2d's 205-cell grading; ens1, rs1, fdstab; the geometry and model-only readouts.

**For Joseph, through the director:**
- whether any of ct3b, t2b or e96d should move to V_F, since each uses C_e or C_total alone rather than the reported
  covariance;
- the open presentation question of the S1 and C_resp σ rows: does the "C_e" row stay as C_e, or become V_F? Both are
  in the readings table (§5).

## 5. The readings table

`fd/receipts-vf/readings/vf_readings.py`, a reading tool, imports `docs/analysis-note/make_values_fived16.py` and
`make_values_landed.py` unchanged, and computes:
- **OLD:** `all_values()` on the pinned readouts, as the note builds them;
- **V_F:** the same functions on the V_F readouts of Phase 1 and the V_F copies of Phase 2, with `READOUTS` and
  `NOPL_READOUTS` replaced by the V_F files and `ARMS`' four matrix names replaced by their V_F names. All of this is
  done in the tool's own process; no file under `docs/analysis-note/` is written.

**It writes:**
- `vf_readings.json`: every key, OLD and V_F;
- `vf_readings.md`:
  1. **Decision-rule outcome changes, first.** This covers:
     - each F0/F0b/F1/PRR/RSN listing (p < 0.01 or any \|z\| > 2) and trigger count;
     - V-ATLAS's A3 and its validity list;
     - C-R's and gover's labels;
     - X's agreement;
     - E2's seed-variation rule;
     - the gdefs seed flags.

     Each change is named with its rule, OLD and V_F. A covariance that only grows can only clear a flag or raise a
     count; any change the other way is a STOP, reported first.
  2. every `\fvval` key that moves, OLD → V_F, with each `\fvval{key}` print site (file:line in
     `docs/analysis-note/*.tex`);
  3. the S1/C_resp σ rows both ways (C_e and V_F; §4.3);
  4. the follow-ups for other lanes: the note's repins (`make_values_fived16.py` `READOUTS`, `NOPL_READOUTS`, `ARMS`,
     `MATRIX_KEYS`), `make_supplemental.py`, `fived16_headline`, `fived16_genresidual`, the EA2 redraw, and
     `valid_region.py`'s `COV_KEY` for a bound rerun.

The table holds readings. They go to the director first, and the note's wording stays Joseph's.

## 6. Controls (each refuses, with nothing further written)

| | control |
|---|---|
| **V0–V4** | the block (§1): every input's sha is its pin; B5D's record names this V_F, and its V_F is the CSV's bit for bit (V0). The C_e CSV is the data product's C_e bit for bit; the cpl block's f, C_resp and C_PL5D are the product's bit for bit, and its X and reported matrix to 10⁻¹² (V1). L is symmetric, V_F = L C_e Lᵀ to 10⁻¹², and L commutes with C_e to 10⁻¹² (V2). dF is symmetric to 10⁻¹² and PSD; the two revised matrices are V_F + C_model_abs + C_resp (+ C_PL5D) to 10⁻¹² and positive definite (V3). The npz is the same bytes when written twice and reads back bit for bit (V4) |
| **R** | each OLD-arm output against its pinned file: the same structure, and every int, float, bool and null equal to 10⁻¹² relative. Strings, `argv`, `code_sha256`, `code` and `versions` are excluded (`fd_cpl_addition.compare_numbers`). The data product: its CSVs byte for byte, its JSON's numbers and strings but argv. The deposit candidate: CSVs byte for byte, JSON under `without_code`. The figures: each PDF byte for byte, sidecars but argv, code and versions |
| **C** | each step exits 0 and writes every declared output. In the V_F arms, each readout names `vf_block.npz`'s sha256 wherever it records the extra block, and each upstream readout's sha256 as the chain computed it |
| **S** | the V_F arms' reported relative σ equals √diag(C_rep,F)/f from `vf_block.npz` to 10⁻¹² in Stage G (g and g0, every prediction's cells) and in F0b's `relative_sigma_plus_C_resp + C_PL5D + dF`; the same for the arm without C_PL5D, with √diag(C_total + C_resp + dF)/f |
| **K** | the V_F product: the committed product's pin, the block's sha, and the V_F Stage G naming that block (K0–K1). Its C_e, C_model_abs, C_resp and C_PL5D are the committed product's bit for bit, and both revised matrices are the committed ones + dF to 10⁻¹² (K2). Stage G's σ is the product's (K3). Symmetry and positive definiteness (K4); the correlation (K5); every CSV and the JSON read back bit for bit (K6) |
| **P** | each Phase 2 recompute with the **old** matrix reproduces every field it will replace. Values computed from bit-identical inputs must match to 10⁻¹² relative. Where the producer's input was only round-tripped through its readout (V_g from σ_Vg/f), the tolerance is 10⁻¹⁰, and that tolerance is recorded per field. Then the V_F call replaces exactly those fields, and `vf_patch` lists them |
| **D** | in the readings, no flag appears and no agreement count falls under the larger matrix (any such change is a STOP) |
| **T** | Phase 1's table: the OLD pins are the committed ones; predictions and truths are the same, in the same order, on both sides; each side names its matrix |
| — | each producer's own controls, unchanged (in Phase 2, those its imported functions apply) |

Any refusal is reported to the director unrepaired. The recompute is not complete until a bound rerun passes.

## 7. Order, cost and the checkpoint

1. This declaration, committed; its sha to the director.
2. The block, the code, tests, mutants and two reads; the code's sha bound by the director. Phase 1's part goes first.
3. **Phase 1**, one login02 connect:
   - fences: sacct for every lane's job families, acks with `date -u` times, window = oldest ack + 900 s, a word to
     limitation-resolver right before connecting, END messages after;
   - expected time: the recorded runs took F0 44 s, F0b 43.4 s, F1 46.3 s and at most 5 s for each other step, so four
     arms take about 10 minutes, under `timeout 3600`; 0 node-h;
   - **the NERSC certificate expires at 2026-11-26T03:28:45Z** (checked by `ssh-keygen -L`). The connect needs a
     renewed one, which is Joseph's step.
4. **Phase 2:** the fetch-list to the director, then one fetch connect (§4.2), then the recompute locally.
5. The receipt and `vf_readings.md` to the director, each led by any decision-rule outcome change.
6. **Checkpoint: by 2026-11-28T00:00Z,** I tell the director whether C will finish with readings in JE's hands by
   the 29th. If not, it's B: Phase 1's readings become a disclosed v2 item, and v1 gets the disclosure paragraph
   (wording Joseph's).

**Committed outputs:**
- `fd/with-vf/block/`, `fd/with-vf/readout/` (each arm's readouts), `fd/with-vf/data-product/`,
  `fd/with-vf/deposit-candidate/`, `fd/with-vf/figures/` and `fd/with-vf/table/`;
- `fd/with-vf/p2/` (the V_F copies);
- `fd/receipts-vf/` (decl, code checks, reads, the chain's receipt and logs, the fetch, the readings).

Nothing is written into `fd/readout/`, `fd/with-cpl/`, `fd/data-product/`, `fd/deposit-candidate/`, `gencmp-e/` or
`docs/analysis-note/`.

## 8. Not changed

- No bound tool's bytes, including `fd_cpl_addition.py`, every Phase 1 producer, `fd_gencmp*.py`, `fd_xcov*.py`,
  `prr_read.py`, `rsn_*.py` and `valid_region.py`.
- B5D's record, C_b's status (reported descriptively, not adopted; DECISION-20261125 §3), and agy's C_b quadratic (not
  cited, B5D-BINDING-2 ruling 8).
- Nothing on NERSC is removed. The NERSC run roots are new (`vf-20261125-p1`). Phase 2's connect writes nothing on the
  cluster.
