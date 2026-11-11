# ENS1 A1 stage-1 analysis: the receipt (2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The analysis was run under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`, on the director's go on the connect's sha256.
That go came after the full run's receipt (`../stage1-a1/`, #938) and its POST-RUN PASS.

**Result: `STAB_PASS`.** The bound `ensemble_estimator_analyze.py --stage 1` exited 0 with that verdict. The analysis
ran on a login node at 0 node-h, so stage 1's spend stays 38.9166 of its 55.0 cap.

**CITABLE FOR:**
- the stage-1 verdict of ENS1 (declaration §4): E₉₆ meets FD-STAB's stability bars on the declared input, and G0 holds;
- the numbers in `ens1_stage1.json`, as the bound tool wrote them;
- the records-only stat of stage 2's shared inputs (`stage2-inputs/`).

**NOT CITABLE FOR:**
- any bias or closure statement. `stability_truth_bias_descriptive` is the readout of declaration §7.4 ("Readouts with
  no criterion": "a description only: one truth, one experiment, and not an F0b truth") and moves no verdict. Stage 2's
  bias criterion (§5) has its own run and verdict.
- any absolute statement about E₉₆. The tool labels the file "relative only".
- a paper sentence. Wording is Joseph's, through the PRD read.

## The connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_s1_analysis.sh` is the copy the connect wrote, sha256 `2691cf9c…`.
- The launcher is `ens1_a1_s1_analysis_launch.sh`, `20911f17…`.
- The launcher rc and ssh rc were both 0 (`launch-analysis.out.txt` holds the ssh rc line).

**`connect-analysis.log.txt`** (login32, 2026-11-08T16:42:41Z–16:43:10Z, rc 0):
- **Its preconditions:** the post-run's done file read 0, and its `a1-full-read.json` (`daee5538…`) said PASS.
- **The fence:** pass. `squeue-before.txt` is empty.
- **The deploy:** HEAD is `f4d2d7f3` with 0 modified tracked files before and after.
- **The bound digests:** all seven sha256s match:

  | file | sha256 |
  |---|---|
  | `ensemble_estimator_analyze.py` | `1d6a0448…` |
  | probe | `807c40d3…` |
  | `estimator_stability_analyze.py` | `391fdc82…` |
  | s5c contract | `d54fd7c9…` |
  | sigma receipt | `84266e30…` |
  | h2 definition | `b6790761…` |
  | FD-STAB's SHA256SUMS | `e2c35e55…` |

- **The control-jitter copies:** the 20 copies are as at the dry connect (`refs-SHA256SUMS`).
- **The environment:** Python 3.11.14. `env-analysis.log.txt` shows the same two missing `setup.sh` warnings as the
  runs.
- **The output:** `ens1_stage1.json`, sha256 `7f5a9ce4da8f59f3284715ff6f14f8106034b42c0301ad04979a8ed6b461ad99`,
  8,184 bytes. It is committed here as the tool wrote it, with no key renamed.

## The readout (`ens1_stage1.json`)

The settings are N = 96 and 10 pairs. The bars are FD-STAB's: 0.3 on the median and 1.0 on the maximum.

| estimator | mean median (SE) | mean max (SE) | worst pair max | sd51 median | sd51 max | passes |
|---|---|---|---|---|---|---|
| E₉₆ | 0.0821 (0.0038) | 0.7586 (0.0723) | 1.0652 | 0.0648 | 0.3280 | true |
| F_P10 | 0.7598 (0.0262) | 6.7754 (0.4183) | 9.2197 | 0.5800 | 2.7982 | false |

- **G0** (`g0_informative`): true. F at P = 10 fails the bar, as §4.2 requires, so the verdict is not UNINFORMATIVE.
- **An observation, not a gate:** E₉₆'s worst single pair has a maximum of 1.0652, above the 1.0 bar. The bound
  criterion is the 10-pair mean, 0.7586, and that passes. This receipt records the worst pair and does not reinterpret
  the criterion.
- **ĉ** (§7.1, a readout with no criterion; per the tool's own note it never moves the verdict):
  - median over all functionals 0.00176;
  - median over the top ten 0.00435;
  - c\* 0.01104 and ε 0.00329;
  - `reading` null.
- **`cell_sd_E96`:** the 16 reporting cells' rounding SDs. Stage 2's s_E (§5.2) uses these.
- **`stability_truth_bias_descriptive`:** E₉₆'s and F₆₄'s b = X / X_true − 1 on the 16 cells, against the stability
  pseudo-experiment's `xtrue_flat`. This is declaration §7.4's readout, which has no criterion: "a description only:
  one truth, one experiment, and not an F0b truth". It moves no verdict, because the bound `stage1()` fixes `verdict`
  before it computes this key (`ensemble_estimator_analyze.py:246-250` against `:268-271`, at M_A1).
  - Its key name puts the file in the results index (below). There it is UNATTRIBUTED and unreviewed, which is accurate.

## The results index

`tools/registry/results_index.py --population` classes `ens1_stage1.json` as `included`, with 2 rows, because the key
`stability_truth_bias_descriptive` tokenizes to `bias`. FD-STAB's `readout-2/fd_stab.json` is included the same way.

**The director's ruling** (2026-11-08): commit the JSON as written, together with the four `--write` outputs:
- `RESULTS-INDEX.tsv` and `RESULTS-POPULATION.tsv`;
- `docs/analysis-note/records_results_index.tex` and `records_estimators.tex`.

`records_results_index.tex` is a generated records table, not authored paper text. There is no key rename and no waiver
row. `records_estimators.tex` regenerates unchanged.

## Stage 2's shared inputs: records-only stat (`stage2-inputs/stage2-inputs-stat.txt`)

The director's ruling 4 asked for this listing ahead of the ruling on sharing inputs with FD-PRR (`prr_*`). It was made
on login22 at 2026-11-08T16:51:53Z, at 0 node-h.
- **The method:** `stat -c` on each path. `find` listed the two directories, and nothing was written on pscratch.
- **The columns:** type, inode, nlink, size, and mtime/atime/ctime as epochs.
- **The listing:**
  - `of_inputs_5d.npz` and `bkg_dump.npz`;
  - `nd-unfolding/bank_sweep_5d_bkgaware/` (701 entries);
  - `s5p-20260926/bank_detector/` (33 entries).
- **What it found:**
  - 736 regular files, each with nlink 1, and 2 directories.
  - Neither directory has a subdirectory or a symlink.
- **What moved:**
  - No file was opened.
  - **Listing a directory reads it, so `bank_sweep_5d_bkgaware/`'s own atime reads 16:51:40Z.** That is this lane's two
    `find` passes (16:50–16:51Z). No file's atime moved.
  - The npz's and the bkg's atime, 15:42:54Z, is the stage-1 tasks' own read of their inputs.

FD-STAB's `runs/control/` products are not in this listing. Stage 2's connect copies them with `dd iflag=noatime`,
with stat records before and after (ruling 3):
- the base `stab_control_b-_j-.npz`;
- the 31 jitters j21–j51;
- the 18 closure lines §3.2 names.

The analysis judges 17 of the 18 closures. The A7_mnvtune line is the determinism duplicate of nominal: it is copied
and not judged.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has one row for this connect and one for the stat.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

**Next:** stage 2's dry run (§5, §8) is released by the director. The dry connect's sha256 goes to the director before
launch. The full stage 2 needs the dry receipt and a further go.
