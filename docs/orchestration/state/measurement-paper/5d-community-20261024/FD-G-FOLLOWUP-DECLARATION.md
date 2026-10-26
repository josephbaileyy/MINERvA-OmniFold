# DECLARATION G-FOLLOWUP: a per-cell look at R04 (G-R04) and the correlation sensitivity of Stage G's χ² (G-SENS) (2026-10-26)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's approval, `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §2 (PR #387, main
  `c6f96f97`): "yes lets look at R04 and do the sensitivty check". It approves (a) a per-cell look at R04 and (b) a
  sensitivity check that weakens the cell-to-cell correlations of the interaction-model uncertainty. Both are
  descriptive, neither is a claim, and the interpretation is Joseph's.
- The director's request of 2026-10-26, which sets the items below.

**After:** G-DIAG ([`FD-G-DIAG-REPORT.md`](FD-G-DIAG-REPORT.md), PR #383). Each 16-cell prediction's χ² is carried by
two or three cell-contrast modes with relative σ of about 0.6–3 %. R04 leads the largest mode of three of the four
16-cell predictions.

**Declares:**
- the tool `nd-unfolding/fd_g_followup.py` and its tests `nd-unfolding/tests/test_fd_g_followup.py`;
- a refactor of `nd-unfolding/fd_g_diag.py` that moves its controls D0–D5 into a function the new tool calls (§6.1);
- the exact argv, the controls, the readout schema and the stop rule.

One binding covers both parts, and one invocation runs both.

**MEASURES:** nothing. The tool has not run on Stage G's inputs.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit and has run only on synthetic fixtures; §6.3 lists what the tests read from committed records -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- any reading of Stage G's comparison, of R04 or of the sensitivity, any claim, and any paper text.

**CITABLE FOR:** what G-FOLLOWUP will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

**Inputs.** The same pinned inputs as Stage G and G-DIAG, with role `adopted`. The reported matrix is
M = C_total + C_resp + V_g. The tool also reads two committed readouts: Stage G's (`75a9ddee…`) and G-DIAG's
(`680dc5ef…`). It reads no data tuple and no new product.

**Cost:** 0 node-h, on a login node, with no Slurm job and nothing written to CFS. On the synthetic tree the run takes 0.2 s and
writes a readout of 131 kB.

### G-R04: numbers only, for R04 and the cells that load with it

The cells are R04, R08, R01, R14, R10 and R00 (the director's list; §7 item 1).

0. **Provenance** (added; §7 item 2). From G-DIAG's committed readout, each 16-cell prediction's three top modes
   under the reported matrix, relative to f: the mode, its σ and χ² fraction, R04's rank by |loading|, and the six
   cells' loadings.
1. **The definition.** Each cell's:
   - box edges in (p_T, p_∥, E_avail, q₃, W);
   - H2 boxes;
   - fine-bin count;
   - face neighbours on the 2⁵ H2 grid, each with its axis. An unreported H2 box is named as such.
2. **f's relative σ, √diag(B)/f, for each block B:**
   - S1's seven groups (stat, interaction, flux, detector, lateral, normalization, seed);
   - each C_model vertex (|s_j|);
   - C_resp;
   - the totals C_e, C_model, C_total and C_total + C_resp.

   Each is given for the six cells, beside its median over all 16 cells.
3. **R04's correlation with each of the other five cells,** B_ij/√(B_ii B_jj), under:
   - C_total + C_resp, the reported covariance of f;
   - each 16-cell prediction's reported matrix C_total + C_resp + V_g;
   - each block of item 2 alone, and each total.

   Each matrix's rank is written beside it. A vertex alone, and normalization, are rank one, so their correlations
   are ±1 by construction. S1's seed group is exactly zero (its committed relative σ is 0 on every cell), so its
   correlations are null.
4. **For each prediction,** read from the Stage G readout's reported comparison at each of the six cells: g/f − 1,
   the pull, σ_total/f, σ_Vg/f and the MC event count. GiBUU is compared on its eight p_∥ < 4.5 cells only. Its R04
   and R14 entries say "not compared" and carry no number, so no GiBUU value is formed on them.
5. **The search for a data or reco event count or an efficiency.**
   - **What is searched:** the last key of every key path of every pinned product, case-insensitive. A key matches if
     one of the words data, reco, eff, efficiency, count(s), nevt, n_ev, event(s), purity, stability, truth, signal
     or accept(ance) stands in it with no letter on either side. So `data_b0_j100.npz` and `expected_reco_signal`
     match, while `recovery` and `records` do not.
     - The products are the definition, S1's readout, `cmodel_5d.json`, the two committed readouts, S1's npz, C_resp's
       npz and the five prediction npz files.
     - npz members are listed from their `.npy` headers. Only a scalar string member is loaded, and it is read as
       JSON. One that is not JSON is listed under `string_members_not_json`.
     - The pinned s5p manifest's file names are also searched, as "listed, not opened".
   - **Keys only.** A match is a key whose name contains a word. It is not a count unless its value is one. Matches
     will include file names under S1's `meta.inputs_sha256`, such as `data_b0_j100.npz`, which are digests, not
     counts.
   - **What is reported:** every match, the number of keys searched in each product, and the definition's per-cell
     value of every matching field for the six cells, with its median over 16. Nothing else is opened.
   - **What the committed records hold** (§6.3): the definition is `simulation_only: true`. Its matching per-cell
     fields are purity, stability, expected_reco_signal, truth_selected and mc_neff_truth. Stage G's readout carries
     the MC `n_mc_events_in_cells`.
   - No data event count or efficiency key is known in them. The run's search is the record. The report says what it
     found, and if nothing it says so with the search.
     <!-- absence-ok: a pre-run statement of what this session's reading of the committed records found, scoped to them; the run's own search (item 5) is the record. Search: key_paths over h2_definition.json, s1_assembly.json, cmodel_5d.json, fd_g_readout.json and fd_g_diag_readout.json at c6f96f97 by eye, 2026-10-26 -->

### G-SENS: the correlation sensitivity of Stage G's reported χ²

- **The shrinkage.** For a family of S1 groups, each group C_g in it is replaced by
  C_g(α) = D^½[(1 − α)ρ + αI]D^½, with D = diag(C_g) and ρ its correlation. This is (1 − α)·C_g off the diagonal and
  C_g's own diagonal on it, bit for bit.
- **The α values:** 0 (the reference and control S0), 0.1, 0.25, 0.5 and 1.
- **Two families:**
  - `interaction`, the primary;
  - `c_e_systematic`: interaction, flux, detector, lateral and normalization, shrunk jointly.
- **Unchanged in both:** stat, seed (§7 item 3), the three C_model vertices, C_resp and V_g.
- **For each family, α and prediction:**
  - the total χ², the ndf and the condition number of M;
  - λ_min;
  - the fewest modes carrying 50 %, 90 % (and 99 %) of the χ²;
  - the top mode (largest χ² contribution): its relative σ, its χ² and fraction, its three leading cells by |loading|
    with signs, and all its loadings;
  - the stability record and flags, as in G-DIAG;
  - the χ² at α = 0, beside it;
  - each shrunk group's smallest eigenvalue.

  Each record also carries the family's role (`primary` or `second`). A top mode's index is its place in that
  matrix's own eigen-order, so the same index does not name the same mode across α.
- **Units:** everything is relative to f, per the G-DIAG ruling. The χ² and ndf are unit-free.
- **No p-value**, for the same reason as G-DIAG's removals. Every record carries the label "descriptive sensitivity
  of the reported χ², not an alternative result", exactly as requested. Stdout prints it once, before the
  `[G-SENS]` lines.
- **GiBUU** is on its eight cells, as in Stage G.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

Stage G's and G-DIAG's inputs and pins, unchanged (`FD-G-DIAG-DECLARATION.md` §1), plus one:

| input | where | checked against |
|---|---|---|
| G-DIAG's committed readout | `$T/fd/readout/fd_g_diag_readout.json` | `680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88`, pinned in the tool (control F0) |

Everything else is G-DIAG's, checked by G-DIAG's own D0–D5:
- S1's npz and readout;
- `cmodel_5d.json`;
- the s5p manifest and the five predictions;
- the definition;
- Stage G's readout (`75a9ddee…`);
- C_resp (`4d8b5797…a8a20a`, on the command line).

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`.
- `B=$P/fd-g-followup-20261026`. It does not exist yet (login33, 2026-10-26T17:33Z).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-g-followup-20261026` on login33 at 2026-10-26T17:33:04Z printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY` as for Stage G: `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_followup.py nd-unfolding/tests/test_fd_g_followup.py nd-unfolding/fd_g_diag.py \
    nd-unfolding/tests/test_fd_g_diag.py nd-unfolding/fd_g_compare.py nd-unfolding/tests/test_fd_g_compare.py \
    nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_diag_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-G-FOLLOWUP-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_followup test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after;
- the §8 digests;
- `tests rc=0` with "Ran 146 tests … OK" (56 G-FOLLOWUP + 41 G-DIAG + 27 Stage G + 22 S1, locally on 2026-10-26).

Anything else is a STOP.

### 2.2 The run (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_g_followup.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json --g-diag-readout $T/fd/readout/fd_g_diag_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --out-json $B/fd_g_followup_readout.json > $B/logs/followup.out 2> $B/logs/followup.err; echo "rc=$?" >> $B/logs/followup.out
```

- **Projected wall:** 5 minutes, as for G-DIAG, which took about 1 s on the same inputs. The timeout is 375 s, 1.25 ×
  that.
- **The five extra-block arguments** are Stage G's exactly, and all are required (exit 2 otherwise). D5 refuses unless
  the committed Stage G readout ran with the same digest, key, name and role. F0 refuses unless the G-DIAG readout ran
  on the same Stage G readout and extra block.
- **Exit codes:**
  - 0: every control passed and the readout was written;
  - 1: a control refused, an overwrite was refused, or an unexpected error occurred (nothing written);
  - 2: argparse;
  - 124: past the timeout.
  Any exit other than 0 is a STOP.
- **What is committed** (the report's PR):
  - `$B/fd_g_followup_readout.json`, as `fd/readout/fd_g_followup_readout.json`;
  - the logs and step scripts under `fd/receipts-g-followup/`;
  - ledger rows.
- **The results index:** if the readout enters the index population, it is regenerated in-branch under the
  director's standing ruling (a) of 2026-10-26.

## 3. Controls

All run before anything is written, and each refuses: exit 1, nothing written. Every refusal test asserts the named
check, so a different check firing does not pass it.

| control | checks | tests |
|---|---|---|
| **D0–D5** | G-DIAG's, unchanged, through `fd_g_diag.load` (FD-G-DIAG-DECLARATION.md §3): the digests (with C_resp's on the command line); each prediction's structure; S1, its 46 blocks and seven groups, C_model = SᵀS and the extra block; GiBUU's cells; positive integrals; and Stage G reproduced from its committed readout to 10⁻¹⁰ | G-DIAG's 17 control tests; `test_d0_runs_first` here |
| **F0** | the G-DIAG readout's digest is the pinned one; its schema is `fd-g-diag-readout/1`; it ran on this Stage G readout and extra block; it has the same predictions; its first comparison is the reported matrix | `test_f0_the_g_diag_readout_pin`, `test_f0_each_sub_check` (5 sub-checks, each alone) |
| **R1** | **The definition.** The six cells are reported cells. Every cell's box is the bounding box of its H2 boxes, which fill it and map to it. The fine-bin counts of R00–R15 are U's nonzero entries, and with the unreported fine bins they cover the fine grid | `test_r1_a_cell_not_reported`, `test_item_1_the_h2_bit_order_reversed`, `test_r1_u_disagrees_with_the_fine_map`, `test_r1_a_fine_bin_mapped_outside_the_cells` |
| **R2** | **Item 2's σ.** S1's committed readout carries every group's and total's σ and median. Every one, and item 2's own median of it, equals the tool's to 10⁻¹². Entries are compared as \|a − b\|/max(\|a\|, \|b\|), with equal entries counting 0, so S1's all-zero seed group passes and a NaN refuses. The three vertices' variances sum to S1's C_model variance. σ(C_total + C_resp) equals Stage G's reported `sigma_total_over_f` | `test_r2_a_group_off_by_1e_9_or_a_median_missing` (10⁻¹³ passes), `test_r2_a_median_or_stage_gs_sigma_total_off_by_1e_9`, `test_r2_item_2s_median_is_a_mean`, `test_r2_vertices_do_not_sum_to_c_model`, `test_r2_not_stage_gs_sigma_total`, `test_item_2_variance_not_sigma`, `test_item_2_not_divided_by_f` |
| **R3** | **Item 3's correlations.** Every one is within [−1, 1]. The blocks rebuild the correlations of C_total + C_resp, to 10⁻¹² | `test_item_3_*` |
| **R4** | **Item 4's source.** In the Stage G readout, every reported pull is −(g/f − 1)/√(σ_total² + σ_Vg²), to 10⁻¹⁰. This ties the values read per cell to one another; D5 does not read σ_total/f or σ_Vg/f | `test_item_4_a_readout_whose_pulls_do_not_follow_from_its_sigmas`, `test_r4_and_s0_tolerances` (σ_Vg × (1 + 10⁻⁷)) |
| **S0** | **α = 0 reproduces Stage G.** For every family and prediction, the χ² of the summed, unshrunk blocks equals the committed reported χ² to 10⁻¹⁰ relative | `test_sens_c_resp_dropped`, `test_r4_and_s0_tolerances` (× (1 + 10⁻⁸) refuses, × (1 + 10⁻¹²) passes) |
| **S1** | every shrunk M is positive definite: Cholesky succeeds and λ_min > 0. A shrunk group alone is only positive semidefinite (normalization is rank one), so its smallest eigenvalue is reported, not tested (§7 item 12) | `test_sens_an_indefinite_shrunk_matrix` |
| **S2** | **The shrinkage is the declared one.** Every shrunk group's diagonal, and every shrunk M's, is the unshrunk one bit for bit. Every shrunk group's off-diagonal is (1 − α) times the unshrunk one (10⁻¹⁵ of its largest entry). Every block outside the family is unchanged bit for bit | `test_sens_the_diagonal_scaled_too`, `test_sens_the_wrong_group_shrunk`, `test_sens_a_group_outside_the_family_shrunk_too` |

## 4. Statistics, as built

- **Neighbours.** H2 box b's bin on axis k is bit (4 − k) of b, with the axes in the order (p_T, p_∥, E_avail, q₃, W).
  A neighbour is a box of another cell, or an unreported box, that differs from one of the cell's boxes in exactly one
  bit. R1 checks the bit order against every cell's box, and a test checks the neighbours against the boxes' geometry.
- **Fine-bin count:** the number of fine cells the fine map assigns to the cell.
- **σ:** √diag(B)/f. A vertex's is |s_j|, since S is relative to f.
- **Correlation:** B_ij/√(B_ii B_jj), or null where a variance is zero.
- **Medians:** `numpy.median` over all 16 cells.
- **G-SENS:**
  - The blocks are G-DIAG's (`comparison_blocks`, relative to f). M is their sum, in G-DIAG's order.
  - The eigenvectors follow G-DIAG's sign rule (`eigen`). The per-mode χ² is `mode_chi2`, the mode counts
    `modes_needed`, and the stability record `chi2_ways`.
  - The top mode is the one with the largest χ² contribution.
  - Leading cells are the three largest |loading|, ties broken by cell order.
  - The condition number is the eigenvalue ratio of M, relative to f.
- **Non-finite numbers** are written as null and counted, and the JSON is written with `allow_nan=False`.

## 5. The readout, `fd-g-followup-readout/1`

```text
schema, labels{what, r04, sens, units, not}, controls_passed[D0..D5, F0, R1..R4, S0..S2],
constants{cells, alphas, families, lead, fractions, search, reproduction},
r04{
  provenance_g_diag_top_modes{prediction: [3 x {mode, sigma, fraction, rank_of_R04_by_abs_loading, loadings{6}}]},
  item1_definition{cell: {id, h2_boxes, box{axis: [lo, hi]}, n_fine_bins, neighbours[{neighbour, axis, h2_pairs}]}},
  item2_relative_sigma{cell | median_over_16: {block: sigma/f}},
  item3_correlation_with_R04{under{matrix: {cell: rho | null}}, rank{matrix: n}, under_prediction{prediction:
                             {matrix, cell: rho}}, note},
  item4_stage_g{prediction: {label, matrix, cells{cell: {compared, g_over_f_minus_1, pull, sigma_total_over_f,
                                                         sigma_Vg_over_f, n_mc_events} | {compared: false, why}}}},
  item5_search{pattern, flags, matched_on, keys_searched{product: n}, matches{product: [key path]},
               string_members_not_json, note, s5p_manifest_paths_matching{note, paths},
               definition_values{simulation_only, fields, cells, median_over_16}}},
sens{reported_matrix, label, mode_index, unchanged[7], records[2 families x 5 alphas x 5 predictions x
  {family, family_role, alpha, prediction, cells, chi2_stage_g, chi2_at_alpha_0, chi2, ndf, condition, lambda_min,
   modes_needed{50%, 90%, 99%}, top_mode{mode, sigma, chi2, fraction, leading_cells[3 x {cell, loading}], loadings},
   stability{chi2_mode_sum, chi2_lstsq, rel_*, ridge_sensitive, methods_disagree, unstable},
   shrunk_group_lambda_min{group: lambda}, label}]},
inputs_sha256, code_sha256{fd_g_followup.py, fd_g_diag.py, fd_g_compare.py, s1_assemble.py}, argv,
non_finite_written_as_null
```

No key `p` appears anywhere in the readout, and a test asserts this.

**What stdout prints:**
- one PASS line per control check;
- one `[G-R04]` line per cell: its fine bins, its neighbours, σ/f of C_total + C_resp against the median, and its
  correlation with R04;
- the label line, then one `[G-SENS]` line per family, α and prediction (`summary_line`);
- a `wrote` line.

Every line is built before the readout is written, and printed after it.

**What it carries:** relative quantities, correlations, definition geometry and MC counts. Item 4 also carries the
Stage G readout's relative values. No absolute cell value is copied.

## 6. Code and tests

### 6.1 The `fd_g_diag.py` refactor

- **What moved:** `run()`'s D0–D5 block, unchanged line for line, into `load(a, pins, predictions)`. It returns what
  the controls checked. `run()` calls `load()` and continues as before. `fm`, the fine map, is kept as a name.
- **Why:** the new tool needs the same inputs under the same controls. Calling them avoids a second implementation of
  D0–D5.
- **The proof that nothing changed:**
  - G-DIAG's 41 tests pass unchanged.
  - The receipt [`fd/receipts-g-followup/declaration/refactor_identity.py`](fd/receipts-g-followup/declaration/refactor_identity.py)
    and its log run main's `fd_g_diag.py` (`7c161280…`) and the refactored one (`241bfd02…`). They use the same six
    synthetic trees: seeds 0–2, roles adopted and sensitivity. Both versions exit 0 and write identical readouts,
    compared as parsed JSON with exact float equality, `code_sha256` and `argv` aside.
  - Review B also ran both versions on refused trees (a D5 χ² tamper and a schema tamper). The exit codes and
    refusal messages were identical.
- **G-DIAG's bound bytes** (`7c161280…`, named in its declaration §8 and its readout's `code_sha256`) stay in its
  own deploy at `d02ce2f2`, from which G-DIAG reproduces. Its readout and report are unchanged. `fd_g_diag.py` on
  main becomes `241bfd02…` (§7 item 11).

### 6.2 Tests (`test_fd_g_followup.py`, 56)

**Test inputs:**
- G-DIAG's synthetic Stage G tree, with the seed block exactly zero, as in the committed S1, and with S1's readout
  carrying every group's σ and median as `s1_assemble` writes them;
- Stage G and G-DIAG run on that tree.

No real prediction, covariance or data value is read.

| class | what it shows |
|---|---|
| `Shrink` (10) | **The diagonal is kept bit for bit** for every α, at scales 1, 10⁻⁸⁰ and 3.7 × 10⁻⁴¹ (the director's diagonal control). **Also:** the off-diagonal is exactly (1 − α) times; the literal D^½[(1 − α)ρ + αI]D^½ agrees to 10⁻¹⁴; α = 0 is the identity and α = 1 the diagonal; positive semidefiniteness is kept at ranks 1, 3 and 16; only the family is shrunk, and the other blocks are the same objects; the declared constants. **The helpers:** the search matches whole words only, and each of its 16 words alone; key paths through lists, dedup, the leaf rule, and an npz's JSON and bytes members, with a non-JSON string member listed; the comparison counts equal zeros as agreement and NaN as failure |
| `Definition` (4) | R04's neighbours by hand: R00 (p_∥), R12 (p_T), R06 and R07 (E_avail), R05 and the unreported H2 box 10 (q₃). Every listed cell's reporting neighbours agree with the boxes' geometry. The H2 boxes rebuild every cell's box. The definition's search fields |
| `PlantedDefects` (21) | **One or more per item.** The defect is patched into the tool's own function, and a control at run time, or the item's validator, reports it. The validators are silent on the correct output (EndToEnd). <ul><li>**Caught by a run-time control:** the H2 bit order reversed (R1); the variance for σ, or σ not divided by f (R2); the correlation without its square root, or the reported covariance without C_resp (R3); a readout whose pulls do not follow from its σ (R4); the diagonal scaled too, the wrong group shrunk, or a group outside the family shrunk too (S2); C_resp dropped (S0); an indefinite shrunk M (S1).</li><li>**Caught by a validator** (the item has no run-time check of that kind): the variant's modes read as the reported comparison's (item 0); neighbours across two axes, and fine bins counted over the whole grid (item 1); the median over the six cells (item 2); the variant's pulls, and a GiBUU value formed on R04 (item 4); a case-sensitive search, and a dotted key name split as a path (item 5); the modes in absolute units, and a p-value in a record (G-SENS).</li></ul> |
| `EndToEnd` (4) | **As invoked** (`-I -B`, cwd outside nd-unfolding). D0–D5, F0, R1–R4 and S0–S2 PASS. Every number is recomputed by hand: <ul><li>items 0–2: provenance and rank, boxes, H2 boxes, sorted neighbours and their H2 pairs, σ and medians, with seed exactly 0;</li><li>item 3's correlations and ranks under every matrix, with null under seed;</li><li>item 4 by cell name;</li><li>GiBUU not compared on exactly R04 and R14;</li><li>item 5's matches;</li><li>every G-SENS record's χ², ndf, condition number, λ_min, top-mode index, σ, χ², fraction, loadings, leading cells and mode counts, each group's λ_min, and the family's role, against M built by hand from the tree with the family shrunk;</li><li>α = 0 equal to Stage G to 10⁻¹⁰, and α = 1 moving the χ²;</li><li>the labels, `controls_passed`, the `inputs_sha256` keys, and no p.</li></ul> **Stdout:** each line is read against its record, not against `summary_line`. **Also:** the sensitivity role reports the matrix without C_resp; a non-finite number is written as null and counted; no overwrite |
| `Controls` (12) | D0 first; F0 (the pin, and each of 5 sub-checks alone); R1 (a cell not reported; U against the fine map; a fine bin outside the cells); R2 (10⁻⁹ refuses and 10⁻¹³ passes, on a group, a median and Stage G's σ_total; a missing median; item 2's median as a mean; the vertices' sum; Stage G's σ_total); R4's and S0's tolerances |
| `Invocation` (2) | **The real script:** `--help`; a missing `--g-diag-readout` exits 2; on the synthetic tree it reaches D0 and refuses there (the real pins), with no traceback and nothing written |
| `CommittedPins` (3) | The G-DIAG readout pin is the committed file's, and it ran on Stage G's readout and C_resp. R04 is the largest-\|loading\| cell of a reported top mode of every 16-cell prediction, and each listed cell loads at \|v\| ≥ 0.25 in one of those modes. S1's readout carries what R2 checks |

**Locally** (2026-10-26: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_g_followup
test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated` ran 146 tests, OK
([`fd/receipts-g-followup/declaration/tests-local.log`](fd/receipts-g-followup/declaration/tests-local.log)). The
cluster run is reported in the PR.

### 6.3 What the tests read from committed records

- **The definition:** Stage G's and G-DIAG's tests already read it, because the fine map is pinned to it. Item 1 for
  R04 is therefore known at declaration: 11,520 fine bins, and the neighbours listed in `Definition`. These are
  geometry of the binning, not a result.
- **G-DIAG's committed readout:** `CommittedPins` reads it for its pin and for the provenance of the cell list (§7
  item 1).
- **S1's committed readout:** `CommittedPins` reads its keys.

No test reads a prediction, C_resp or S1's npz.

## 7. For the director

1. **The cell list.**
   - **The tool takes the director's five cells as given.** In G-DIAG's reported, relative-to-f top modes of the four
     16-cell predictions, consider the modes in which R04 loads at |v| ≥ 0.3. These cells load in them at |v| ≥ 0.25:

     | cell | modes | largest \|v\| |
     |---|---|---|
     | R00 | 5 | 0.35 |
     | R07 | 4 | 0.30 |
     | R09 | 4 | 0.39 |
     | R08 | 3 | 0.42 |
     | R14 | 3 | 0.41 |
     | R10 | 3 | 0.37 |
     | R01 | 2 | 0.37 |
     | R12 | 1 | 0.26 |
     | R15 | 1 | 0.33 |

   - **R09 and R07 load with R04 as often as R08, R14 and R10, but are not in the list.**
   - **Recommendation:** add R09 and R07. It is one constant, and item 0 shows the loadings either way.
2. **Item 0 (provenance)** is added: the six cells' loadings in G-DIAG's top modes, read from its committed readout.
   It is not in the request. It shows why each cell is in the list. It can be dropped.
3. **Seed is unchanged in both families.** It is not in the request's list of five systematic groups, nor in its list
   of unchanged blocks. It is the unfolding-seed variance, closer to statistics than to a systematic. If wanted, it
   joins `c_e_systematic` by one constant.
4. **"The reported matrix" in item 3** is given two ways:
   - C_total + C_resp, the reported covariance of f, which is prediction-independent;
   - each 16-cell prediction's Stage G matrix C_total + C_resp + V_g. Its diagonal V_g lowers the correlation
     slightly.

   GiBUU has no R04, so it has no item 3 row.
5. **Item 3 under each block alone** includes the three vertices and the totals, as well as the seven groups and
   C_resp. A vertex, and normalization, are rank one, so their correlations are ±1 by construction, and each
   matrix's rank is written beside it. They are kept because a vertex's signs show its pattern.
6. **Only the reported comparison is shrunk,** C_total + C_resp + V_g, as the request says "Stage G's reported χ²".
   The without-C_resp variant is outside this declaration's scope.
   <!-- absence-ok: a scoping statement about what this declaration computes, not a claim that a result does not exist -->
7. **A group is shrunk as one matrix,** the sum of its S1 blocks; interaction has 33. By linearity this is the same as
   shrinking each block, since diagonal-keeping shrinkage is linear in C.
8. **"Leading cells" are the three largest |loading|,** with signs, and all loadings are written. The 99 % mode count
   is written beside the requested 50 % and 90 %, as G-DIAG's `modes_needed` returns it.
9. **The stability flags** (G-DIAG's `chi2_ways`) are written on every record, so a shrunk χ² that is numerically
   unsafe would be visible. A flag does not refuse.
10. **Item 5's search is by key name,** a whole-word regex over the last key of every key path. It finds a field
    only if its name says what it is. A count stored under an unrelated name would be missed. The values reported are the definition's per-cell
    fields. For other matches, the key path is reported and nothing is opened. The pinned s5p manifest's paths are
    searched as "listed, not opened".
11. **The `fd_g_diag.py` refactor** (§6.1) changes the bytes of a file that a run is bound to. G-DIAG reproduces
    from its own deploy at `d02ce2f2`, and the identity receipt shows the outputs unchanged. The alternative is a
    copy of D0–D5 in the new tool, which would be a second implementation of the same controls.
12. **"Each shrunk matrix must be positive definite"** is read as each shrunk M, which S1 refuses on. A shrunk group
    alone is only positive semidefinite: normalization, shrunk in the second family, is rank one at α = 0. So each shrunk
    group's smallest eigenvalue is reported, not tested.
13. **S0's 10⁻¹⁰ is relative,** as in G-DIAG's D5 and D7.
14. **The second family diagonalizes normalization at α = 1.** Normalization is a rank-one block, 0.014² f fᵀ, fully
    correlated across cells. At α = 1 it becomes an independent 1.4 % per cell. This is as requested, and the reader
    should know it.
15. **Seed** (item 3 above) is exactly zero in S1, so including it in or excluding it from the second family changes
    nothing.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_followup.py` | `f767afa37617b405e2652b44cccf588249ee20f38bbd48d04778b1b5f7eb93f4` |
| `nd-unfolding/tests/test_fd_g_followup.py` | `3477c274b5fb96bbf0f69db7a2275db1bd1644f4ca97700a85d700b41ef186ed` |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` (the §6.1 refactor; was `7c161280…`) |
| `nd-unfolding/tests/test_fd_g_diag.py` | `870564f5bf85c17b6e68212ab95663f6fd201969abc6d9f9d1b08261f368d525` (unchanged) |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` (unchanged) |
| `nd-unfolding/tests/test_fd_g_compare.py` | `b4d0ff2611bcc6226e215e57023002025682aebea49ec1f2c06f3c61a9d7d9a8` (unchanged) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged) |
| `…/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` (input) |
| `…/fd/readout/fd_g_diag_readout.json` | `680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88` (input) |

## 9. Ledger, storage and stops

- **Ledger:** rows in `fd/LEDGER.tsv` for §2.1 and §2.2. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 1 GB), the logs and a readout of about 130 kB (131 kB on the synthetic tree). Nothing goes to HPSS or
  CFS. `$B` joins the pscratch retention list.
- **Stops:** any STOP is reported to the director unrepaired. Nothing is rerun without the director.

## 10. Not changed

- Stage G's and G-DIAG's readouts and reports, S1's covariance, C_model,5D, C_resp, R00–R15, κ = 1 and the route
  decision. Neither part changes the reported covariance or any cell (decision §2 item 2).
- No GPU and no premium QOS.
- The reading of any of this, claims, printed wording and publication are Joseph's. The report gives numbers only.

## 11. Review dispositions

Two independent read-only reviews ran on the first draft:
- **A** checked it against the request and the records;
- **B** attacked the code with 137 single mutations in a mirror. 91 were killed, 12 survivors are equivalent or
  nearly so, and 34 were coverage gaps.

| # | finding | disposition |
|---|---|---|
| A-1, B-1 (MAJOR) | R2 divided by the committed S1 seed group's σ, which is 0 on every cell, so the real run would have ended in a `ZeroDivisionError` traceback after F0 and R1. The fixture's seed block was 10⁻⁸·I | R2 now compares by \|a − b\|/max(\|a\|, \|b\|), with equal entries counting 0 and NaN refusing (`worst_rel`). The fixture's seed block is now exactly zero, as in S1, and the end-to-end test asserts seed σ = 0 and null correlations |
| A-2 | The label said "chi2", not "χ²" | The exact text |
| A-3 | The `[G-SENS]` stdout lines carried no label | A label line before them |
| A-4, B-2 | Item 5's substring regex matched `recovery` in 598 manifest paths and `records`; it searched keys only | Whole-word matching; "keys only" stated in the readout and §0; file names labelled as such |
| A-5 | Rank-one blocks give ±1 by construction | Each matrix's rank is written, with a note |
| A-6 | Several planted defects reach only a test validator; item 2's median was outside R2 | R2 now checks item 2's own median; §6.2 separates the defects caught at run time from those caught by a validator |
| A-7 | Two R1 sub-checks had no refusal test | `test_r1_a_cell_not_reported`; the fine-grid check now counts R00–R15 only, so it is independent of the U check, tested by `test_r1_a_fine_bin_mapped_outside_the_cells` |
| A-8 | R2's vertex sum was compared with the tool's own C_model σ (a tautology) | Compared with S1's committed C_model σ |
| A-9, B-4 | The refactor changes `fd_g_diag.py`'s sha256; the identity evidence was in scratch only | The committed receipt (§6.1); §7 item 11 |
| A-11, A-12 | A top mode's index is not comparable across α; the primary family was not marked | `mode_index` note; `family_role` on every record |
| A-13, B-3 | `npz_key_paths` loaded every member; an object member would crash; a bytes JSON member was silently skipped | Members are listed from their headers, and only scalar string members are loaded, with bytes decoded; a non-JSON string member is listed |
| A §7, B-5 | Shrunk groups are only PSD; S0's tolerance; normalization at α = 1; seed | §7 items 12–15; each shrunk group's λ_min is reported |
| B-6 | Stdout was formatted after the readout was written | Lines are built first |
| B gaps | Search words, key-path rules, npz JSON (C11, C12, C15, K01, K03, K04, K06); top-mode index, χ² and loadings, R04's rank, σ_total in item 4, H2 boxes and pairs, sorted neighbours, record cells (T09–T11, F10, F11, P03, H05, H06, H09, Y15); tolerances (Q02, Q05, V03, Y12); the sensitivity role (F02); stdout against itself (L01, L02, O08, O10); labels, `controls_passed`, `inputs_sha256`, the null count (C17, O01–O03, O12) | Each has a test now (§6.2) |
| B gaps | K08 (the definition's median as a mean) | `test_the_definitions_search_fields` checks the median |
| B gap not closed | K11 (a manifest directory name matching) | Left as noted: the manifest list is file names only, and no number reads it |
| B equivalent | R02, R03, K10, G01, G02, Y06, Y07, Y09, Y14, Y16, O04, T05 | No change; each is equivalent or covered by another check, as review B states |
<!-- absence-ok: these rows restate the two reviews' findings on the uncommitted first draft of 2026-10-26 (each named gap passed every test there); they describe that draft's coverage, now closed, not the absence of a result -->
