# RE-1 report: the higher-dimensional central values with the refined estimator (record)

**Run by** a Claude agent for the director, 2026-10-20, under the frozen [`RE1-SPEC.md`](RE1-SPEC.md). It used one debug job, 0.0531 CPU node-h. Scripts, numbers and the alternative figures are in [`re1/`](re1/); products are on pscratch. The agent could not write this file, so the director saved its report verbatim below.

**Outcome:**
- **P5 needs no rerun.** The existing s5p data unfold is configuration (e) on the full fine grid. Figs. 2 and 3 and their numbers were regenerated from it; every change is below 1%.
- **C2 (the 2D closure) and P3/P4 (3D/4D) need new code.** The frozen 2D and ND paths support the refinement only at 100/8, and no frozen 2D path draws pseudo-data that include background.
- **Side finding:** Fig. 1 and four of its printed numbers do not reproduce from current inputs. This is under investigation.

**CITABLE FOR:** the configuration and provenance of P5, the regenerated Fig. 2/3 numbers, and what C2/P3/P4 need.
**NOT CITABLE FOR:** any 2D conclusion, or any covariance for configuration (e).

---

RE-1 is finished as far as the spec allows: P5 needed no rerun, C2 is stopped because the frozen code cannot run it, P3/P4 are not possible unchanged, and F was produced for Figs. 2 and 3 of the paper and their quoted numbers. One debug job charged 0.0531 of the 30 node-h, and nothing was deferred for time. No RE-1 job is queued or running; it finished at 17:59 PDT, well before the 04:00 cutoff.

## Code and environment
- **Spec:** read in full at origin/main `2e2ffd20`, in the detached worktree `scratchpad/wt-re1`. The worktree is clean; nothing was committed or pushed, and no cluster checkout was edited.
- **Cluster code:** a fresh clone of `2e2ffd20` at `/pscratch/sd/j/josephrb/methods-paper/re1-20261020/deploy-2e2ffd20` (HEAD verified, porcelain empty). Cluster main has since moved to `13cb4a6a`; I did not use it.
- **Cluster environment:** `root_6_28`, activated by prefix as `setup_salloc_env.sh` does (Python 3.11.14, numpy 1.26.4, ROOT 6.28/12).
- **Figure rendering:** done locally in a venv built from `publication/release/requirements-lock.txt` (CPython 3.11.15, matplotlib 3.11.2, numpy 1.26.4), which matches how the current PDFs were built.

## 1. P5: the existing product is configuration (e); no rerun
- **Product:** `/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz`, sha256 `fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c`. It is the `data_central` in `prod/design.json:49`.
- **Metadata checked:**
  - `config` R (refinement override 400 trees / 31 leaves, deterministic LightGBM, random_state 45 = 42+3);
  - 5 iterations, `construction` data, full MC, estimator seed 42;
  - all three OmniFold estimators at 100 trees / 8 leaves, deterministic, `force_row_wise`, 32 threads, `bin_construct_sample_cnt` 2^31−1;
  - input sha256s match the expected `07fccc1a…` (npz) and `2addac8f…` (background dump).
- **Full fine grid:** `xsec_flat` has 65856 entries, shape [14,16,7,7,6]. The edges equal the producer grid exactly, and it has the same 10694-cell support as the current product.
- **Refinement evidence:** clipped fraction 4.6e-4, refined/signed sum 1.0000184.
- **Code record:** every module digest equals `4f5a613f`, except `s5p_numerics.py` (`9d7c1232`, from `abdc88c5`). That version differs only by the `s5p_truths.install` line, which affects pseudo-data only.
- **Producing job:** 58911473, step 6 COMPLETED. The array head reads "CANCELLED by 112498", which is campaign management after the step finished.
- K1 applies only to reruns, so it was not run.

## 2. C2 stopped: it needs new code
- **The refinement exists in 2D only at 100/8.** `refine_stay_positive` is reached only through `--bkg-mode negweight-refined`. The driver passes nothing but `random_state=seed+3` (`2d-unfolding/unfold_2d_omnifold_unbinned.py:2037-2042`). The lgbm defaults are 100 trees / 8 leaves (`:404-407`), and no flag sets the capacity (argparse `:1356-1522`). The 400/31 override exists only for the 5D npz path (`nd-unfolding/s5e_candidate.py:33`, via `s5n_pseudo`).
- **No frozen 2D path draws background-inclusive pseudo-data:**
  - purity `--closure` is signal-only (`:1887-1904`);
  - the coverage toys are signal-only, purity (`sbatch_coverage_toys_MEFHC.sh:63-72`);
  - the fixed-truth toys are signal-only (`PREREG-20261005-2d-fixed-truth-coverage.md:73-74`, "No background subtraction in closure");
  - the s5c/s5n pseudo-data are 5D only (`s5c_pseudo.py:41`), and no 2D npz or 2D background dump exists.
- **No seeds were declared and nothing ran.** K2 has no record to compare against: no 2D purity closure with background exists.
- **Adopted 2D covariance, for when C2 is built:**
  - record: `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:28-43`;
  - `stat` and `total` keys of S5 `production_cov.npz` `6689d2fc…`;
  - Q = `s5_plus_playlist.npz` `8ccb4d72…`;
  - central value `E_U`, `4f5a1b6d…`. It is plain LightGBM seed 42 with purity, not deterministic, per `DECISION-20261011-joseph-2d-central-lightgbm-seed42.md`.

## 3. P3/P4 not possible unchanged
- The 3D driver has no background-mode option at all; purity is hard-wired (`3d-unfolding/unfold_3d_omnifold_unbinned.py:371-424`).
- The ND driver's `negweight-refined` passes only `random_state=seed+3` (`nd-unfolding/unfold_nd_omnifold_unbinned.py:1016-1020`), so it gives configuration (d) at 100/8, not (e).
- Per the spec, 3D/4D stay in configuration (a) with their purity bias stated.

## 4. K3/F
**K3 (current inputs reproduce current outputs):**

| figure or product | result |
|---|---|
| `excess_eavail_W.py` on the current 5D product `630306e2…` vs `751bb859…` | `hData2D`, `hGenCV2D`, `hExcess2D` bitwise (contents and errors) |
| `export_fig_arrays.py` | regenerated npz is bitwise identical, sha `72394a2b…` |
| `make_figs.py` Fig. 2 | equals `paper_fig2_joint.pdf` `57f3cc60…` bitwise |
| `make_figs.py` Fig. 3 | equals `paper_fig3_generators.pdf` `e9d1bb01…` bitwise |
| `fig_numbers.py`, all Fig. 2/3 numbers | pass |
| note `eavailW_band.pdf` (ROOT `overlay_eavailW_band.py`) | **fails**: `0735a6d2…` vs `555c5f1e…`, still different after stripping the PDF date fields. No alternative was produced for it. |

**Container conversion (needed because the producer reads ROOT):** P5 was written with the production `und.write_thnd` and read back with the producer's own `load_data_xsec`. The readback is bitwise; the file is `xsec_5d_p5.root` `8f02eb50…`. Control: the current product repackaged the same way gives `excess_eavail_W` output identical to `751bb859…`.

**F outputs from P5:**
- `excess_eavail_W_p5.root` `7e3b2c01…`; `hGenCV2D` is bitwise unchanged.
- `fig_arrays_p5.npz` `a59ccf49…`; only `hData2D` and `hExcess2D` differ from the current arrays.
- Fig. 2 `c35057b3…` and Fig. 3 `6aef59eb…`.
- In (E_avail, W), P5/current is 0.99838 integrated and 0.988–1.004 per cell.

**Printed numbers that change at their printed precision:**

| quantity | printed now | from P5 |
|---|---|---|
| data total | 3.0699e-38 | 3.0650e-38 |
| `\gibuuCorner` | 1.61 | 1.60 |
| `\gibuuTotal` and `\genRatioTotHi` | 1.39 | 1.38 |
| `\figTwoHiHi` | 12–30 | 12–29 (computed 12.04–28.92) |
| `\figTwoLowW` | 23–31 | 23–30 (computed 22.51–30.30) |

Everything else stays within its printed precision.

**Not F:** the 3D/4D figures stay in configuration (a). `paper_joint_nulls` already uses configuration (e).

**Side finding:** `fig_numbers.py` reports four Fig. 1 (2D) values that disagree with `values.tex` on current inputs (`\binsTen`, `\pullMean`, `\pullRMS`, `\chiPaper`), and Fig. 1 itself does not reproduce bitwise. The likely cause is that `fig_arrays` predates the 2026-10-11 switch of the 2D central value. This is outside RE-1 and untouched.

## Ledger
| JobID | QOS | state | elapsed | charge |
|---|---|---|---|---|
| 60064887 `re1-f-chain` | debug, m3246 | COMPLETED 17:56–17:59 PDT | 191 s | 191/3600 × 256/256 = **0.0531** node-h |

The measurement session's jobs were not touched, and nothing was written to CFS.

## Deferred and deviations
- **Deferred for time:** nothing.
- **Not done because the spec cannot be executed as written:** C2, P3, P4, and F for `eavailW_band` (K3 failed).
- **Execution choices, to review:**
  - P5 was converted from npz to ROOT, with bitwise readback and a control.
  - The P5 export read a staged analysis root whose only differences are symlinks to the two P5-derived 5D files; its manifest records the shas.
  - Figures were rendered locally in the lock-file environment.
- These results are not a live record until committed.

Everything is under `/pscratch/sd/j/josephrb/methods-paper/re1-20261020/` (`deploy-2e2ffd20/`, `scripts/`, `k3/`, `f/`, `results/`, `logs/`). The local copy is `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/methods-re1/`; open `f/fig_numbers_current_vs_p5.tsv` and the `f/figs_p5/` PDFs first.

| script | sha256 |
|---|---|
| `p5_to_root.py` | `a8850e29` |
| `cmp_root_hists.py` | `c4280ee6` |
| `cmp_npz.py` | `19173a3d` |
| `re1_f_chain.sh` | `42157aed` |