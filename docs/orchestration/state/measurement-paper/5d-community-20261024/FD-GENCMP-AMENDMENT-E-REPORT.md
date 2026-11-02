# REPORT GENCMP amendment E: Stage G on the "CH, analysis definitions" predictions, and step C-R (2026-11-01)

**By** the limitation-resolver lane (Claude), for the director.

**Under** [`FD-GENCMP-AMENDMENT-E-BINDING.md`](FD-GENCMP-AMENDMENT-E-BINDING.md):
- #658 binds [`FD-GENCMP-AMENDMENT-E-DECLARATION.md`](FD-GENCMP-AMENDMENT-E-DECLARATION.md) at M = `6cd095d6`;
- its addendum, #661, binds E-A1 at M′ = `1d936338`.

**MEASURES:** E-S, E-M, E-R0 and E-1 as declared, run twice (the first run stopped, §5), and C-R once.
- Records are under `fd/gencmp-e/`:
  - `run1/`: the stopped run's chain receipt, pins, logs, receipts and staging record;
  - `rerun1/`: the full run's readouts, figures, chain receipt, pins, logs, receipts and HPSS receipts, plus
    `values_diff.tsv`;
  - `c-r/`: C-R's readout, environment, script and logs.
- The logs are force-added, because `*.log` and `logs/` are ignored.
- Each G-FOLLOWUP readout under `rerun1/chain/` has a companion `fd_g_followup_readout/` directory of 20 relative
  symlinks to S1's tracked replica files. Its item 5 names those files, and `verify_receipt_artifacts.py` resolves them
  there. The committed readout's companion directory does the same.

**CANNOT AUTHORIZE:** any paper edit, any reading or claim, or any change to the reported covariance.
- The paper lane re-pins under §8's row (binding ruling 5).
- C-R's numbers go to Joseph with X's (ruling 3), and `paper_body.tex:119` is not touched.

**CITABLE FOR:** the readouts below, as the committed files hold them.

**NOT CITABLE FOR:**
- a validation of the reported covariance or of `Q_R`;
- a generator exclusion;
- C_model's dependence on the target, since E2 has not run;
- C-R as a test, because its rule is step C's bound one. X is the test.
<!-- absence-ok: E2 is this amendment's own step, not run because its code is not yet bound (binding ruling 4); a statement of this run's scope, not a claim that a result does not exist -->

## 0. Outcome in brief

| part | outcome | §8 row |
|---|---|---|
| E-S, E-M | 42 inputs staged, all the pinned bytes, no atime moved. E0 held for all four corner predictions | — |
| E-R0 (the gate) | **PASS in both arms, in both runs.** All 10 readouts reproduce the committed ones: structure and numbers in nopl, plus strings in with. All 6 figures have equal sidecars and byte-identical PDFs | — |
| E-1 | **completes** (rerun1). P held. **XC passed** in both arms: Stage G's g and χ² on the corner equal `defs.json`'s for all four predictions. Both figure checks pass (498 checks each) | "E-1 completes": the paper lane re-pins and drops the scoping clause; the 316 changed values keys are in `rerun1/values_diff.tsv` |
| C-R | every control passed, on `E_R` with `Q_R`. **QA's reading changes** from #648's "agree below a correlation" to "agree" (at every ρ). QB, QC and QD stay "agree below a correlation" | "C-R, a quadrant's reading changes": to Joseph with X |
| E2 | not run: its code is not yet bound (binding ruling 4) | "E2 not run": #651 item 6's caveat stands |

**Cost: 0 node-h.** Every step ran on saul login node login37. No job was submitted.

## 1. Execution

| run | deploy | env | steps | UTC (2026-11-02) | result |
|---|---|---|---|---|---|
| first | `$P/gencmp-e-20261101/deploy`, a fresh clone at M; six blobs verified (`run1/receipts/deploy-blobs.txt`); porcelain empty before and after | root_6_28: Python 3.11.14, numpy 1.26.4, matplotlib 3.10.8 | E-S, E-M, chain | 02:30:25–02:31:04 | stopped at E-1's nopl figures (K6), as bound (§5) |
| C-R | the same deploy | **omnifold_py310** (§6, deviation 1): Python 3.10.19, numpy 2.2.6, uproot 5.6.9 (`c-r/environment.txt`) | `fd_gencmp.py overlap --arm refined` | 02:30:54–02:30:57 | rc 0 |
| rerun1 | `$P/gencmp-e-20261101/rerun1/deploy`, a fresh clone at M′; six blobs verified (`rerun1/receipts/deploy-blobs.txt`); porcelain empty before and after | root_6_28 (same versions) | E-S, E-M, chain | 02:50:36–02:51:34 | rc 0 at every step |

- **rerun1's chain:** 28 tool runs, every one rc 0. They took 53.0 s together; the longest was 5.8 s (figures), and
  every step was far inside its 375 s timeout. The receipt, `rerun1/chain/chain.json`, holds 40 checks, all ok.
- **The first run:** 20 tool runs and 29 checks, all ok, until the failing figures step.
- **Writes.** Everything was written under `$P/gencmp-e-20261101/`, which was absent before. Nothing was written to
  CFS. The first run's directory was not changed by the rerun, apart from §6's deviation 4.

## 2. Controls

- **E-S.** Each of the 42 copies was the pinned bytes. `STAGE.json` records no atime moved, in either run.
- **E0.** For each of the four predictions, g and the two χ² under both matrices equal `defs.json`'s to 1e-12
  (`rerun1/logs/e-materialize.out`). The rebuild directory is the one `defs.json` names, and MnvTune v1's staged file is
  Stage G's.
- **R0.** All 26 checks PASS in each run (`rerun1/logs/e-chain.out`, `run1/logs/e-chain.out`):
  - **nopl:** the 5 readouts equal the committed ones in structure and numbers;
  - **with:** the 5 readouts equal the committed ones in structure, numbers and strings;
  - **figures:** all 6 have the committed sidecar (but argv, code and versions) and the same PDF bytes;
  - each comparison was preceded by the committed file's pin check;
  - in the old set, every downstream step ran on the committed upstream readouts.
- **P.** The corner set holds Stage G's five names in order, and each file is its recorded bytes.
- **XC.** In both arms, the readout holds all four corner predictions. Each one's g and its total and shape-only χ²
  equal `defs.json`'s: the with arm against `reported`, the nopl arm against `without_C_PL5D`. That is 10 of 10 checks.
- **The figures.** In both arms of rerun1, the tool's K0–K8 passed, and `fd_g_figures_check.py --prediction-set
  gencmp-chdefs` reported "OK: 498 checks, 0 failed, 3 sidecars" (`rerun1/chain/logs/chdefs-*-figures_check.out`).
- **C-R** (`c-r/e_cr.out`). PASS for:
  - R, C0, C1, the structural checks and C3 at `E_R`'s 3.069e-38. The measured 2D total is 3.06874e-38, against step
    C's 3.07302e-38.
  - **the three new stops:** the arm key "refined"; `Q_R`'s central value is `E_R` (max |CV/`cells_x_EU` − 1| = 0.0);
    and every quadrant is covered;
  - **C-R3D:** the committed `overlap.json` is the pinned bytes, and every quadrant's 3D row equals it to 1e-12.
  - No atime moved.

## 3. Readouts

### 3.1 E-1 (rerun1): the five readouts in each arm, and the figures

The readouts are under `rerun1/chain/chdefs/{nopl,with}/readout/`, with sha256 prefixes:

| readout | with | nopl |
|---|---|---|
| `fd_g_readout.json` | `a19009e0` | `d9a1ce38` |
| `fd_g_diag_readout.json` | `522bfafa` | `4e77966e` |
| `fd_g_followup_readout.json` | `586cd741` | `748f3af6` |
| `fd_g_sens2_readout.json` | `4bc21dfd` | `6626cb73` |
| `fd_flux_boot_readout.json` | `5bb475ea` | `24ff27f9` |

The figures are under `chdefs/{nopl,with}/figures/` (ratio, modes and sens; PDF and sidecar). The old set's
reproductions are under `rerun1/chain/old/` as R0's evidence.

**The values diff (§8, mechanical).** I copied the ten readouts over the committed paths in a throwaway worktree of
`main` at `892f1444`, and repointed only `make_values_fived16.py`'s ten pins there. The generator ran ("wrote
values_fived16.tex: 2490 values"), and its output was diffed against the committed file.
- The key set is the same.
- **316 printed values change,** all in the families E recomputes:

  | family | changed keys |
  |---|---|
  | `sens-` | 201 |
  | `gs-` | 64 |
  | `diag-` | 28 |
  | `fb-` | 23 |

- No `g-`, `r04-` or `corr-` key changes. `g-` already carries Table IV from `defs.json` (the paper lane's #656), and
  XC shows Stage G's χ² equal it.
- Every changed key, with its committed and its E-1 value, is in `rerun1/values_diff.tsv`. The worktree was then
  removed.

**The keys the prose prints as summaries:**
- **unchanged:** `sens-flux-fall-lo/hi`, `sens-joint-chi2-min`, `fb-edge-max`, `fb-offset-relmax`;
- **changed:**
  - `sens-detlat-fall-max-nopl`: 18 → 19;
  - `fb-edge-min`: 1.6 → 1.4;
  - five mode counts:

    | key | committed | E-1 |
    |---|---|---|
    | `diag-gibuu-reported-modes99` | 6 | 7 |
    | `diag-gibuu-reported-modes99-nopl` | 6 | 7 |
    | `diag-gmec-reported-modes99-nopl` | 10 | 9 |
    | `diag-nuwro-variant-modes90` | 6 | 7 |
    | `diag-nuwro-variant-modes90-nopl` | 6 | 7 |

- **Stage G's own total χ² (`gs-*-total-chi2`)** become the corner's:

  | prediction | with arm | nopl arm |
  |---|---|---|
  | GENIE CV | 105.42 → 107.18 | 109.35 → 111.22 |
  | GENIE+MEC | 223.55 → 229.09 | 272.12 → 277.94 |
  | NuWro | 130.68 → 127.69 | 188.03 → 180.62 |
  | GiBUU (8 cells) | 45.25 → 47.78 | 58.46 → 61.41 |

  The with-arm values are the χ² of #651's adopted corner (FD-GENCMP-REPORT §2.2). After the re-pin, the `gs-` family
  duplicates `g-`, and the paper lane may merge them.

### 3.2 C-R: the sixteen cells per quadrant against E_R with Q_R

The readout is `c-r/overlap_refined.json`. It is read from the reported matrix C_total + C_resp + C_PL,5D, over
ρ ∈ [0, 1], by step C's bound rule.

| quadrant | S₁₆ (σ₁₆) | E_R: S (σ) | d, % | reading | ρ* | z at ρ = 0 | #648 (on E_U, Q): d, %, reading, ρ* |
|---|---|---|---:|---|---:|---:|---|
| QA | 7.9912e-39 (5.464e-40) | 7.9799e-39 (5.319e-40) | +0.141 | **agree** | 1.0003 | 0.015 | −0.279, agree below a correlation, 0.9999 |
| QB | 6.7751e-39 (3.276e-40) | 6.7899e-39 (3.280e-40) | −0.217 | agree below a correlation | 0.9997 | −0.032 | −0.187, the same, 0.9998 |
| QC | 6.6907e-39 (3.565e-40) | 6.7911e-39 (3.473e-40) | −1.478 | agree below a correlation | 0.9902 | −0.202 | −1.542, the same, 0.9892 |
| QD | 9.1925e-39 (5.036e-40) | 9.1265e-39 (5.152e-40) | +0.724 | agree below a correlation | 0.9982 | 0.092 | +0.648, the same, 0.9985 |

- **QA's reading changes.** Its |d| is now within 2|σ₁₆ − σ₂D|, the any-correlation band (ρ* > 1). So it agrees at
  every ρ. This is the §8 row "a quadrant's reading changes". It is named here and goes to Joseph with X.
- **The variant without C_PL,5D is printed only:** QA and QC read "agree below a correlation", QB and QD "agree".
- **The 3D rows** equal #648's (C-R3D), so the 3D note clause is unaffected.
- **These numbers supersede #648 §2.3's 2D numbers** in the records (binding ruling 3).

## 4. The §8 rows read

1. **"E-1 completes."**
   - The paper lane re-pins `READOUTS` and `NOPL_READOUTS` for `g`, `diag`, `fup`, `sens2` and `fboot` to rerun1's
     readouts and drops the scoping clause.
   - Every sentence that prints a key in `values_diff.tsv` goes to Joseph through the paper lane, with before and after.
   - The ratio and modes figures are replaced one for one, in the arm they print now. The sens figure is produced for
     the note.
   - Each replaced figure's caption states that the predictions are in the analysis definitions (addendum E-A1).
2. **"C-R, a quadrant's reading changes" (QA).** To Joseph together with X. `:119` is unchanged until X reports.
3. **"E2 not run."** #651 item 6's caveat stands until E2's code is bound and E2 runs (binding ruling 4).

## 5. The first run, which stopped

The first run (`run1/`) passed E-S, E-M and E-R0 in both arms: 29 checks, all ok. In E-1's nopl arm, the five readouts
were written. Then `fd_g_figures.py` exited 1 on K6: "ratio: every text lies on the page: off the page:
ratio:{genie_cv,genie_mec,nuwro,gibuu}:legend" (`run1/chain/logs/chdefs-nopl-figures.err`).
- **The cause:** the corner set's legend qualifiers were too long for the ratio figure. The fault was in the
  declaration's §4, and K6 caught it.
- **What it stopped:** the chain, as bound. XC did not run, the with arm did not start, and no number of that set has
  been used. Its corner readouts stay on pscratch and in the HPSS archive. They are not committed.
- **The response:** addendum E-A1 (#659), bound in #661, shortened only the qualifiers. rerun1 ran from a fresh clone
  at M′, in a fresh directory, with R0 re-gating.

## 6. Deviations, reported unprompted

1. **C-R ran in omnifold_py310, not root_6_28** (declaration §7, binding ruling 1).
   - **Why:** root_6_28 has no uproot, which `fd_gencmp.root_hist` imports. On the login node, `import uproot` gave
     ModuleNotFoundError.
   - **The director's ruling of 2026-11-01, verbatim:** "Approved: run C-R in omnifold_py310. My reasons: GENCMP step
     C ran there (FD-GENCMP-REPORT §1). C-R3D's 1e-12 comparison against that readout needs the same environment to be
     like for like. No chain tool imports uproot, so E-S, E-M, E-R0 and E-1 stay in root_6_28 as bound."
   - The interpreter, numpy and uproot versions are in `c-r/environment.txt`. The ruling asked for them "in C-R's
     readout", but the bound code's readout has no field for versions, and adding one would change bound code. So they
     sit beside it.
2. **The deploy tests.**
   - The cluster's environments have no pytest, so the bound suites ran under `python -B -m unittest`
     (`run1/logs/tests-*.log`).
   - **omnifold_py310** (the first deploy): 221 of 222 pass. The one error is in an unchanged `test_fd_cpl_addition`
     fixture, which writes `np.float64(…)` reprs under numpy 2.
   - **root_6_28:** 196 pass, and the 26 errors are all `ModuleNotFoundError: uproot`, in step C's fixtures.
   - **rerun1:** in root_6_28, `test_fd_gencmp_e` ran 43 tests, with 9 errors, all in its step C-R fixtures for the same
     uproot reason (`rerun1/logs/tests-root_6_28.log`).
   - Every test passes in at least one bound environment. The director accepted these notes.
3. **Writes to /dev/shm.** Scripts and two `stat` path lists were copied to `/dev/shm` on the login node and removed in
   the same command: the deploy script, the rerun script, and lists for the pre-binding `stat` checks. Nothing
   outside `$P/gencmp-e-20261101/` was written on pscratch or CFS.
4. **The rerun's launcher log** was first written to the first run's `logs/e_rerun.log`. It was moved to
   `rerun1/logs/e_rerun.log` when the run ended. The first run's directory gained, and then lost, that one file, and no
   existing file in it was changed.
5. **Labels in C-R's readout.** The readout's per-quadrant labels still say "Q" ("Q does not cover…", "against Q, which
   includes C_PL"). In the refined arm they mean `Q_R`, as the readout's `result_2d` = "E_R with Q_R" states. They are
   wording only.

## 7. HPSS

- **Quota first:** `hpssquota` read 446.01 of 512.00 GiB.
- **The archive.** It was made with `htar -Hcrc -Hverify=1` from an explicit list (`rerun1/hpss/htar_files.txt`, 351
  files: both runs and C-R, without the two deploy clones, which git holds). It went to
  `/home/j/josephrb/mnv-gencmp-e-20261101/gencmp-e-20261101.tar`: 137,320,448 B plus a 180,512 B index.
  - htar's verify reported "0 total errors, 352 total objects".
  - `hsi hashcreate` and `hsi hashverify` returned 0, with "(md5) OK".
- **Retrieval:** five files were extracted, and each equals its original by sha256:
  - `c-r/overlap_refined.json`;
  - `rerun1/chain/chain.json`;
  - rerun1's with-arm corner `fd_g_readout.json`;
  - `rerun1/pred/SHA256SUMS`;
  - the first run's `chain/chain.json`.
  The receipts are in `rerun1/hpss/`.

## 8. What goes to whom

- **To the paper lane, through the director:** the re-pin of §4.1, with `values_diff.tsv` as the list of every changed
  key.
- **To Joseph, with X:** C-R's table (§3.2), including QA's changed reading.
- **To Joseph, when E2 has run:** its Δ under binding ruling 4.

Nothing is submitted, deposited or tagged.
