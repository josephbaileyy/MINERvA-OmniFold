# DECLARATION G-DIAG: a descriptive breakdown of Stage G's χ² (2026-10-26)

**By** the measurement session, for the director to bind.

**Amended 2026-10-26 (amendment 1, §12),** at the director's ruling on §7: the block-removed records no longer carry a
p-value. §§0, 2.1, 4, 5, 6, 7 and 8 are changed in place, each change marked "(amendment 1)".

**Under:** the director's request of 2026-10-26, after Stage G's report ([`FD-G-REPORT.md`](FD-G-REPORT.md), PR #378,
main `b6bca37f`).
- Every prediction's χ² is large under the reported covariance, while its diagonal pulls are modest.
- So the χ² is carried by correlated directions. Before anyone reads it, the director wants to know which directions.

**Declares:**
- the tool `nd-unfolding/fd_g_diag.py` and its tests `nd-unfolding/tests/test_fd_g_diag.py`;
- the exact argv, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The tool has not run on Stage G's inputs.
<!-- absence-ok: a scoping statement about this session's own work: the tool is new in this commit and has run only on synthetic fixtures -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- any reading of Stage G's comparison, of these modes or blocks, any claim, and any paper text.

**CITABLE FOR:** what G-DIAG will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

- **What it does:** it takes Stage G's existing total χ², for each of the five predictions and under both of G's
  matrices, and breaks it down:
  - the reported matrix, C_total + C_resp + V_g;
  - the variant without C_resp, C_total + V_g.
- **It adds no statistic.**
  - Its χ² is Stage G's. Two controls check this at run time against G's committed readout:
    - **D5** recomputes Stage G's numbers with Stage G's own code;
    - **D7** checks that every breakdown's own χ² is G's, to 10⁻¹⁰.
  - Everything else is labelled descriptive: the spectrum, the per-mode χ², the block shares, and the χ² with a
    block removed.
- **Two unit systems, both reported.** The total χ² is the same in both. The eigenmodes, the per-mode χ², the
  mode counts and the shares are not. Review A's synthetic check, with f's committed shape, found the 90 % mode count
  differing in 155 of 200 draws. The director chooses which to read (§7 item 1).
  - **Relative to f:** d = (f − g)/f and M = (C + V_g)/(f fᵀ). √λ is a relative σ, which the request asks for.
  - **Absolute:** d = f − g and M = C + V_g. This is the request's (vᵢᵀ(f−g))²/λᵢ literally.
- **The five items,** in each unit system:
  1. M's eigenvalues λ_i (descending), √λ_i along each mode, and M's condition number.
  2. The χ² by mode, c_i = (v_iᵀd)²/λ_i, sorted descending, with each mode's projection, fraction and cumulative
     fraction, and the fewest modes that carry 50 %, 90 % and 99 % of the χ².
  3. For the three modes with the largest c_i: the eigenvector's loading on each cell, √λ, and each block's share
     v_iᵀBv_i/λ_i. The blocks are:
     - S1's seven C_e groups (stat, interaction, flux, detector, lateral, normalization, seed, by
       `s1_assemble.group_of`);
     - the three C_model,5D vertices, s_j s_jᵀ (GENIE+MEC, NuWro, GiBUU);
     - C_resp, where the comparison carries it;
     - V_g.

     They partition M exactly (control D6), so the shares sum to 1. The largest is named `dominant`.
  4. The χ² with each block removed in turn, with its ndf and the condition number of what is left, and no p-value
     (amendment 1), labelled
     "descriptive breakdown, not an alternative result".
     - If M − B is not positive definite, the record says so and carries no χ².
     - If its condition number exceeds 10¹², it is marked `ill_conditioned`.
  5. **Stability**, in float64: the χ² by Cholesky, by the mode sum and by least squares, and against a ridge
     M + 10⁻¹⁰·mean(diag M)·I. Three flags:
     - `ridge_sensitive`: the ridge moves the χ² by more than 10⁻³ relative;
     - `methods_disagree`: the three methods differ by more than 10⁻⁸ relative;
     - `unstable`: either of those, or a Cholesky failure.
- **GiBUU** is on its eight p_∥ < 4.5 cells only, as in Stage G. Its modes are 8 × 8.
- **The shape-only χ²** is not decomposed (§7).
- **Cost:** 0 node-h, on a login node, with no Slurm job and nothing written to CFS. It reads Stage G's 6.8 MB and
  writes one JSON of about 280 kB (276 kB on the synthetic tree).
- **Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

Stage G's inputs and pins, unchanged (`FD-G-DECLARATION.md` §1), plus two:

| input | where | checked against (control D0) |
|---|---|---|
| Stage G's committed readout | `$T/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee`, pinned in the tool |
| C_resp | `$P/cresp-20261026/out/cresp.npz`, key `C_resp` | `4d8b5797…a8a20a`, on the command line, as in Stage G |

**What else it reads, all from files Stage G pinned:**
- S1's 46 named blocks (`C_<block>` in `s1_assembly.npz`, named by its `meta.blocks`; `:` is written `_`, as
  `s1_assemble.py` saves them), and `C_model_frac`;
- `cmodel_5d.json`'s `S` (3 × 16, relative to f) and `vertices`.

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`.
- `B=$P/fd-g-diag-20261026`. It does not exist yet (login37, 2026-10-26T10:42Z).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-g-diag-20261026` on login37 at 2026-10-26T10:42Z printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY` as for Stage G.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_diag.py nd-unfolding/tests/test_fd_g_diag.py nd-unfolding/fd_g_compare.py \
    nd-unfolding/tests/test_fd_g_compare.py nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py \
    nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-G-DIAG-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after;
- the §8 digests;
- `tests rc=0` with "Ran 90 tests … OK" (41 G-DIAG + 27 Stage G + 22 S1, locally on 2026-10-26; amendment 1, was 89).

Anything else is a STOP.

### 2.2 The breakdown (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_g_diag.py \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --out-json $B/fd_g_diag_readout.json > $B/logs/diag.out 2> $B/logs/diag.err; echo "rc=$?" >> $B/logs/diag.out
```

- **Projected wall:** 5 minutes. Stage G took 1 s on the same inputs. The timeout is 375 s, 1.25 × that.
- **The five extra-block arguments** are Stage G's, exactly, and all five are required (exit 2 otherwise). D5
  refuses unless the committed Stage G readout ran with the same digest, key, name and role.
- **Exit codes:**
  - 0: every control passed and the readout was written;
  - 1: a control refused, an overwrite was refused, or an unexpected error occurred (nothing written);
  - 2: argparse;
  - 124: past the timeout.
  Any exit other than 0 is a STOP.
- **What is committed** (the report's PR):
  - `$B/fd_g_diag_readout.json`, as `fd/readout/fd_g_diag_readout.json`;
  - the logs and step scripts under `fd/receipts-g-diag/`;
  - ledger rows.
- **The results index:** if the readout enters the index population, it is regenerated in-branch under the
  director's standing ruling (a) of 2026-10-26.

## 3. Controls

All of them run before anything is written, and each refuses: exit 1, nothing written. Every refusal test asserts the
named check, so a different check firing does not pass it.

| control | checks | tests |
|---|---|---|
| **D0** | Stage G's G0 digests, plus the committed Stage G readout (pinned) and the extra block (`--extra-block-sha256`) | `test_d0_stage_g_readout_pin`, `test_d0_extra_block_digest` |
| **D1** | Stage G's G1, each prediction's structure (`fd_g_compare.prediction_problems`) | `test_d1_prediction_structure` (a short edge array, re-pinned) |
| **D2** | **S1:** U, f > 0, f = x, C_total = C_e + C_model_abs, the committed σ. **S1's blocks:** `meta.blocks` exists and all named blocks are present, each maps to one of the seven groups, and C_e is their sum (10⁻¹²). **C_model:** its vertices are GENIE+MEC, NuWro and GiBUU in that order, C_model = SᵀS with S from `cmodel_5d.json` (10⁻¹²), and C_model_abs = diag(f) C_model diag(f). **The extra block:** its key exists, and it is finite 16 × 16, symmetric and PSD | 7 tests: a missing block; no block list; one block off by 10⁻⁹; S off by 10⁻⁹; the vertices reordered; an unknown group; and the extra block asymmetric (with a PSD symmetric part, so only the symmetry check can refuse it), not PSD, or the wrong shape |
| **D3** | GiBUU's eight cells are the p_∥ < 4.5 boxes | `test_d3_gibuu_cells` |
| **D4** | each prediction's integrals are positive on its cells, which are integrated only there | `test_d4_a_non_positive_integral` (one cell negative, re-pinned) |
| **D5** | **Stage G is reproduced with Stage G's code.** The committed readout is `fd-g-readout/2`, ran with this extra block's digest, key, name and role, and has the same cell sets. For every prediction and both comparisons, its total and shape-only χ² and every pull reproduce to 10⁻¹⁰ relative | `test_d5_each_sub_check` (the role, name, key, digest and schema, each alone); `test_d5_numbers_to_1e_10` (a 10⁻⁸ change to the variant's total χ², either shape-only χ² or a pull refuses; 10⁻¹² passes); `test_d5_another_cell_set` |
| **D6** | **The blocks partition M.** For every comparison and both units, the sum of the blocks equals M to 10⁻¹² of its largest entry | `test_d6_a_block_left_out_or_off_by_1e_9` (V_g dropped, or scaled by 1 + 10⁻⁹) |
| **D7** | **The breakdown's χ² is Stage G's.** For every comparison and both units, the breakdown's Cholesky χ² equals the committed readout's total χ² to 10⁻¹⁰, unless that breakdown is flagged `unstable`, in which case its flags are reported instead | `test_d7_the_breakdowns_residual_is_not_stage_gs` (d = (f − g)/g: D5 passes, D7 refuses) |

## 4. Statistics, as built

- **Eigen-decomposition:** `numpy.linalg.eigh` of the symmetrized M.
  - λ is sorted descending.
  - Each eigenvector is signed so that its largest-|loading| cell is positive. Signs are conventional, and only the
    pattern of a mode is meaningful.
- **Per-mode χ²:**
  - c_i = (v_iᵀd)²/λ_i, and Σc_i is the mode sum.
  - The fractions and cumulative fractions are of the mode sum.
  - "Modes for q" is the fewest leading modes, in c order, whose cumulative fraction reaches q. It is null if a
    λ ≤ 0 makes the fractions non-finite.
- **The top three modes** are those with the largest c_i. Shares are v_iᵀBv_i/λ_i, and `dominant` is the largest.
- **Block removal:**
  - Cholesky of M − B. If it fails, the record has `positive_definite: false` and no χ².
  - No p-value is computed or written (amendment 1).
  - `condition` is the eigenvalue ratio of M − B, and `ill_conditioned` is set above 10¹².
- **Stability:**
  - Cholesky, mode sum, `lstsq` and the ridge, each with its relative difference from the Cholesky value.
  - The ridge is 10⁻¹⁰·mean(diag M), in the breakdown's own units.
  - The flags are as in §0 item 5.
- **Non-finite numbers** (∞ or NaN, from an indefinite M) are written as null, and `non_finite_written_as_null`
  counts them. The JSON is written with `allow_nan=False`.

## 5. The readout, `fd-g-diag-readout/1`

```text
schema, labels{what, units, modes, shares, removed, stability, not}, controls_passed[D0..D7],
blocks{groups[7], vertices[3], extra, finite_mc, s1_blocks_per_group{group: [S1 block names]}},
constants{ridge, unstable, methods, ill_conditioned, top, fractions, reproduction, units},
predictions[5 x {name, label, cells[n],
  comparisons[2 x {comparison (reported | variant), matrix, ndf, chi2_stage_g,
    relative_to_f | absolute: {chi2 (Cholesky), chi2_mode_sum, ndf,
      eigen{lambda[n], sigma[n], condition, rank},
      modes_by_chi2[n x {mode, lambda, sigma, projection, chi2, fraction, cumulative}],
      modes_needed{50%, 90%, 99%},
      top_modes[3 x {mode, sigma, chi2, fraction, loadings{cell: v}, block_shares{block: share}, share_sum, dominant}],
      removed[blocks x {removed, positive_definite, chi2, ndf, condition, ill_conditioned, label}],   (no p; amendment 1)
      stability{chi2_cholesky, chi2_mode_sum, chi2_lstsq, chi2_ridge, ridge, rel_*, ridge_sensitive,
                methods_disagree, unstable}}}]}],
non_finite_written_as_null, inputs_sha256, code_sha256{fd_g_diag.py, fd_g_compare.py, s1_assemble.py}, argv
```

**What stdout prints:**
- one PASS line per control check;
- one line per prediction and comparison (`summary_line`):
  - the χ²;
  - in relative units: the condition number, the modes for 50/90/99 %, and the top mode's fraction, σ and dominant
    block;
  - in absolute units: the modes for 90 % and the top mode's dominant block;
  - the ridge change, and `UNSTABLE (flags)` if set;
- a `wrote` line.

**What it carries:**
- **Relative-to-f breakdown:** relative quantities only.
- **Absolute breakdown:** absolute projections, d's components along each mode, and absolute eigenvalues. These are
  absolute cell-level quantities, as Stage G's unguarded readout also prints.

## 6. Code and tests

- **New:** `nd-unfolding/fd_g_diag.py` and `nd-unfolding/tests/test_fd_g_diag.py`.
- **Reused unchanged:** `fd_g_compare.py` (the pins, predictions, G0–G4 helpers, `compare` for D5, and `chi2_sf`);
  `s1_assemble.py` (`group_of`, `fine_map`, `functional_matrix`, `load_manifest`, `sha256`).
- **Test inputs:**
  - synthetic matrices with a known decomposition;
  - Stage G's synthetic tree, extended with S1's named blocks and S. Two blocks share the interaction group, so the
    group sum is exercised.

  No real prediction, covariance or data value is read.

| class | what it shows |
|---|---|
| `Analytic` (9) | **The director's well-conditioned case:** M = Q diag(λ) Qᵀ from a known orthonormal Q, split 0.25/0.75 into two blocks, and d = Q a. The tool returns exactly: <ul><li>λ (descending), √λ and the condition number;</li><li>c_i = a_i²/λ_i in order, with the projections, fractions and cumulative fractions;</li><li>the modes for 50/90/99 % by hand;</li><li>the top-three choice, and each top mode's loadings equal to its known basis vector under the sign rule;</li><li>shares of 0.25/0.75;</li><li>χ² with each block removed equal to χ²/0.75 and χ²/0.25, with the ndf and condition number of what is left;</li><li>no flags.</li></ul> **Disjoint blocks:** each top mode's block owns it, with share 1. **The director's near-singular case:** λ_min = 10⁻¹⁹ with a 10⁻⁸ component of d along it. <ul><li>float64 Cholesky misses the analytic χ² by over 10 %;</li><li>the three methods disagree;</li><li>the ridge moves χ² by over 90 %;</li><li>the χ² sits in the near-null mode.</li></ul> So item 5 exposes the artefact, not only ridge sensitivity. **The thresholds:** a diagonal M whose ridge response is known in closed form pins RIDGE (times the *mean* diagonal), UNSTABLE (2×10⁻³ flags, 5×10⁻⁴ does not) and the change's denominator. **Also:** an ill-conditioned removal is flagged; an indefinite M carries no χ²; the stdout line carries the flags and the dominant block; non-finite numbers become null and are counted; `modes_needed` by hand |
| `PlantedDefects` (8) | One or more per item. The defect is patched into the tool's own function, and that item's validator is silent on the correct output and reports the defect: <ol><li>the spectrum ascending;</li><li>the per-mode χ² over √λ, and the mode count off by one;</li><li>shares not divided by λ;</li><li>the block added instead of removed; and a p-value planted back into the removal record (amendment 1), which `check_no_p` reports;</li><li>no ridge, and the method comparison switched off, each leaving the near-singular artefact unflagged</li></ol> |
| `EndToEnd` (3) | **As invoked** (`-I -B`, cwd outside nd-unfolding), after running Stage G itself on the tree. D0–D7 PASS, and `constants` are the declared values. For every prediction, both comparisons and **both units**: <ul><li>χ² equals Stage G's readout to 10⁻¹⁰, and the mode sum equals χ²;</li><li>λ equals the eigenvalues of M built by hand, and the condition number their ratio;</li><li>the cumulative fraction ends at 1;</li><li>3 top modes, each with the right block set (C_resp only where carried), shares summing to 1, loadings on the prediction's cells (GiBUU's 8) under the sign rule, and vᵀMv = σ²;</li><li>V_g removed is recomputed by hand, with its ndf, and no removal record carries a p (amendment 1), and the removal χ² agree between units;</li><li>each stdout line equals `summary_line`.</li></ul> **The sensitivity role** swaps which comparison is reported. No overwrite |
| `Controls` (17) | D0 (2), D1 (1), D2 (7), D3 (1), D4 (1), D5 (3), D6 (1) and D7 (1). Each refuses with the named check, and nothing is written |
| `Invocation` (2) | **The real script:** `--help`; a missing `--extra-block-role` exits 2; on the synthetic tree it reaches D0 and refuses there (the real pins), with no traceback and nothing written |
| `CommittedPins` (2) | The Stage G readout pin is the committed file's, and its argv carries C_resp's digest, key, name and role `adopted`. Stage G's pins are carried unchanged. All 46 committed S1 blocks map onto exactly the seven groups, which are S1's committed `relative_sigma` groups. `cmodel_5d.json`'s vertices are the tool's |

**Locally** (2026-10-26: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), `python3 -B -m unittest test_fd_g_diag
test_fd_g_compare test_s1_assemble test_s1_scripts_isolated` ran 90 tests, OK (amendment 1, was 89). The cluster run is reported in the PR.

## 7. For the director

1. **Units.**
   - **The request's formula** is in absolute units, while "relative σ along each mode" is natural only relative to
     f.
   - **The two give different modes:** the eigenvectors, per-mode χ², mode counts, shares and top three differ,
     though the total χ² does not. Review A's synthetic check found a median |cos| of 0.34 between the top
     relative-unit and absolute-unit eigenvectors.
   - **So both are reported,** each complete. Which one is read is the director's choice. The stdout line leads with
     relative units.
2. **The shape-only χ² is not decomposed.** Its matrix adds 100 f fᵀ, a different M. If wanted, the same breakdown on
   M + 100 f fᵀ is a few lines, and its blocks would include the free normalization.
3. **The blocks are S1's seven groups, not its 46 blocks.** "Each C_e systematic group" was read as S1's grouping
   (`group_of`, the groups of S1's own readout). The readout lists each group's member blocks. Per-block shares would
   be 46 numbers per mode.
   - "Stat" is its own group, holding exactly S1's `stat` block.
4. **C_resp enters as one block:** its sum of four species, as adopted. Cross-talk is not in it. Splitting C_resp
   into species is possible but undeclared here.
5. **The removal χ² are not alternative results.** Removing a block changes the covariance, not the estimate. The
   label says so on every record.
   - *Amendment 1:* the p-values are dropped, by the director's ruling 5 below. χ², ndf and the condition number
     remain.
6. **The ridge's size is a choice.** The request says "a 10⁻¹⁰ ridge". It is applied as 10⁻¹⁰ times the mean diagonal
   of M, in each breakdown's units. A literal 10⁻¹⁰·I in relative units would be about 10³ times larger, and in
   absolute units negligible.
7. **What `ridge_sensitive` means.** It means the χ² moves under the ridge by more than 10⁻³. That is not proof of a
   numerical artefact. An accurate χ² on a matrix with one very small eigenvalue can be ridge-sensitive: review A's
   example had λ_min = 10⁻¹², Cholesky accurate to 4 × 10⁻⁸, and a 6.9 % ridge change. `methods_disagree` (the three
   float64 methods differ by more than 10⁻⁸) is the direct artefact signal. Both are reported.
8. **Item 1's "C"** is read as Stage G's comparison matrix M = C + V_g, the matrix whose inverse enters the χ².

**The director's rulings on this section** (relayed 2026-10-26):
1. **Units:** relative to f is the reading, and absolute is reported in full, as disclosed. The cells' rates differ
   by large factors, so absolute modes are dominated by the highest-rate cells. The uncertainty model is built in
   relative terms. A mode's relative σ is comparable with the per-cell σ of about 7 %. The report leads with relative
   units and labels absolute as "the same χ² decomposed in absolute units (different modes)".
2. **Shape-only is not decomposed,** accepted. The report states total − shape-only per prediction, as the
   normalization's share.
3. **S1's seven groups,** accepted, with their member blocks listed. Splitting a dominant group is a follow-up for
   the director to decide, not part of this run.
4. **C_resp as one block,** accepted, as adopted.
5. **The removal p-values are dropped** (amendment 1). χ², ndf and the condition number are kept. A p on a matrix that
   is not a reported uncertainty would be the first number a reader quotes, and the label beside it would not survive
   that.
6. **The ridge,** 10⁻¹⁰ × mean diag in each unit, accepted.
7. **The flags,** accepted as defined. The report presents `methods_disagree` as the numerical-artefact signal and
   `ridge_sensitive` as conditioning sensitivity, and does not call a ridge-sensitive χ² an artefact.
8. **M = C + V_g,** accepted.

## 8. Pinned bytes

Their sha256 at this declaration's commit (re-pinned by amendment 1):

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_diag.py` | `7c1612806efd7ab5c3ae65be1f36944683e6f2cafdb42ba6b46c41825051fec3` (amendment 1; was `85738098…`) |
| `nd-unfolding/tests/test_fd_g_diag.py` | `870564f5bf85c17b6e68212ab95663f6fd201969abc6d9f9d1b08261f368d525` (amendment 1; was `010a4c08…`) |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` (unchanged, Stage G's) |
| `nd-unfolding/tests/test_fd_g_compare.py` | `b4d0ff2611bcc6226e215e57023002025682aebea49ec1f2c06f3c61a9d7d9a8` (unchanged) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged) |
| `…/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` (input) |

## 9. Ledger, storage and stops

- **Ledger:** rows in `fd/LEDGER.tsv` for §2.1 and §2.2. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 1 GB), the logs and a readout of about 280 kB. Nothing goes to HPSS
  or CFS. `$B` joins the pscratch retention list.
- **Stops:** any STOP is reported to the director unrepaired. Nothing is rerun without the director.

## 10. Not changed

- Stage G's readout and report, S1's covariance, C_model,5D, C_resp, R00–R15, κ = 1 and the route decision.
- No GPU and no premium QOS.
- The reading of any of this, claims, printed wording and publication are Joseph's. The report gives numbers only.

## 11. Review dispositions

Two independent read-only reviews ran on the first draft:
- **A** checked it against the director's request and the records;
- **B** attacked the code, with 88 single mutations in a mirror. 37 of them survived.

| # | finding | disposition |
|---|---|---|
| A-M1 | The per-mode breakdown was in units relative to f only; the request's formula is absolute, the two give different modes, and the declaration did not say so | Both units are now reported in full, and §7 item 1 puts the choice to the director |
| A-M2, B-M1 | Nothing at run time checked the breakdown's own χ² against Stage G's (a d = (f − g)/g mutant passed every control) | New control **D7**, tested by that mutant |
| B-M2 | Most D5 sub-checks, its tolerance, the shape-only and pull comparisons and the cell-set check had no test | `test_d5_each_sub_check`, `test_d5_numbers_to_1e_10` (10⁻⁸ refuses, 10⁻¹² passes), `test_d5_another_cell_set` |
| B-M3 | D6's tolerance had no test | V_g scaled by 1 + 10⁻⁹ now refuses |
| B-M4 | Item 5's constants were unpinned (UNSTABLE, RIDGE, the mean against the max, the denominator) | A closed-form diagonal fixture pins all four, and `constants` is asserted |
| B-M5 | The fraction, the absolute condition number, σ and the projection had no test | All asserted, analytically and end to end |
| B-M6 | D1, D3, D4 and five D2 sub-checks had no test | One refusal test each |
| A-m1 | The near-singular test showed ridge sensitivity, not an artefact; `unstable` fired on an accurate χ² | The test now shows Cholesky missing the analytic χ² and the methods disagreeing; `methods_disagree` is a separate flag; §7 item 7 states the meaning |
| A-m2 | The ridge scaling was not raised as a choice | §7 item 6 |
| A-m3 | D3 and D4 were copied code without tests | Tests added (B-M6) |
| A-m4 | The absolute eigenvalues were missing | The absolute breakdown carries them |
| A-m5, B-m | An indefinite M wrote NaN and Infinity | Written as null, counted, and `allow_nan=False` |
| A-m6 | The removal p-values went beyond the request | §7 item 5; dropped by amendment 1 |
| B-m | The sign rule, `share_sum`, the removal ndf and p (p since dropped, amendment 1), the stdout content, the group summation, and a missing `meta.blocks` (a traceback) | Each is tested; the group sum through a second interaction block in the fixture; a missing `meta.blocks` is now a D2 refusal |
| B-m | A removal that leaves a near-singular M − B was unflagged | `condition` and `ill_conditioned` per removal, tested |
<!-- absence-ok: these rows restate the two reviews' findings on the uncommitted first draft of 2026-10-26 (each named mutation passed every test there); they describe that draft's coverage, now closed, not the absence of a result -->

**After the fixes, 34 mutations covering B's survivors were run** in a mirror against a clean baseline. 33 are
caught, each by the test written for it. The 34th sets `share_sum` to the constant 1. It is equivalent whenever the blocks partition M,
and D6 refuses whenever they do not.

## 12. Amendment 1 (2026-10-26): no p-value on a block-removed χ²

**Why:** the director's ruling 5 on §7, quoted above.

**What changed:**
- **The tool:** `fd_g_diag.removal_record` builds each removal record with χ², ndf, the condition number,
  `ill_conditioned` and the label, and no `p`.
- **The tests:** `PlantedDefects.test_item_4_no_p_value_on_a_removal` checks:
  - the removal record's exact key set;
  - that `check_no_p` is silent on the tool's output;
  - that `check_no_p` reports a p-value patched back into `removal_record`.

  The validators that previously checked p now check the ndf and assert that there is no p.
- **The counts:** G-DIAG has 41 tests, and the deploy expects "Ran 90 tests".
- **§8** is re-pinned.

**What did not change:** controls D0–D7, the statistics of items 1–3 and 5, the two units, the argv and the readout
apart from the removed key.
