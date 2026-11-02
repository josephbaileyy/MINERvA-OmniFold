# DECLARATION GENCMP amendment E: Stage G's diagnostics on the "CH, analysis definitions" predictions, and step C-R (2026-11-01)

**By** the limitation-resolver lane (Claude), for the director to bind.

**Under:**
- [`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`](../../../DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md)
  item 2, with the director's reading in [`FD-GENCMP-BINDING.md`](FD-GENCMP-BINDING.md): CPU only, jobs under 12 h,
  regular QOS, nothing written to CFS;
- [`DECISION-20261101-joseph-gencmp-paper-adoption.md`](../../../DECISION-20261101-joseph-gencmp-paper-adoption.md)
  (#651): items 1–2 adopt step A's CH rows and step B's "CH, analysis definitions" corner for Table IV; item 5 holds
  the 2D quadrant sentence; item 6 names, as its "one stated caveat", that C_model's shape ratios come from the
  carbon generators. The director's brief calls that caveat "item 8"; this amendment calls it item 6's caveat (S2);
- the director's brief of 2026-11-01 (by message). The paper lane found that Stage G's diagnostics still read the old
  predictions (generator definitions; NuWro and GiBUU on carbon). They are to be recomputed on the corner, so the paper
  can drop the scoping clause it adds this round. Item 6's caveat is to be measured if the same products allow it, and
  priced separately if not.

**Director's rulings of 2026-11-01 on this amendment (by message), applied here:**
1. **Two declarations.** E is the first: the Stage G recompute and step C-R. The cross-covariance test X
   ([`FD-GENCMP-XCOV-SCOPING.md`](FD-GENCMP-XCOV-SCOPING.md), #653) is the second.
   - X cites this amendment's `fd/gencmp-e/INPUTS.sha256` by its merge commit and does not re-pin E_R.
   - E is merged first.
2. **Host and caps.** E runs on the login node at 0 node-h. Item 8's two vertex unfolds count against their own
   0.5 node-h cap, which the director binds with E. Each part has its own outcome row (§8) and its own cost line in
   the report.
3. **Step C-R's numbers.** C-R does not depend on X, so its report may land before X runs. Under #651 item 5,
   `paper_body.tex:119` stays as it is until X reports. C-R's numbers only replace #648 §2.3's, and they go to Joseph
   together with X.
4. **R0 gates E.** Stage G's committed readouts must be reproduced on the old predictions, to their recorded
   precision, before any new number is computed. If R0 fails, E stops and reports.
5. **Review.** A fresh Sonnet subagent (not sol) audits the declaration and the code before the binding. Its prompt
   and answer are recorded verbatim beside this file, as with #643.

**Declares:**
- E-S, staging;
- E-M, materializing the corner as prediction files (control E0);
- E-R0, the old predictions through every tool (control R0, the gate);
- E-1, the corner through every tool (control XC);
- C-R, step C on the adopted 2D result;
- E2, item 6's caveat priced. Its code is not in this amendment (§6).

**MEASURES:** arithmetic by the bound Stage G tools on the declared predictions, and step C's arithmetic on `E_R` and
`Q_R`.

**CANNOT AUTHORIZE:** a reading, a Table IV or paper edit, a claim, or any run before the binding. The paper lane makes
the edits. Joseph rules on wording (#651, GENCMP ruling 4).

**NOT CITABLE FOR:**
- a validation of the reported covariance;
- a generator exclusion;
- C_model's dependence on the target, until E2 runs.

Paths are relative to the repository root unless absolute. `$P` = `/pscratch/sd/j/josephrb`; `$B` =
`$P/gencmp-e-20261101/`, absent before E-S. `FD` = `docs/orchestration/state/measurement-paper/5d-community-20261024`.

## 0. What reads the old predictions, and what this amendment recomputes

`docs/analysis-note/make_values_fived16.py` takes every printed number of the sixteen-cell result from pinned readouts
(`:29-70`). Each family the brief names comes from one Stage G tool, run on Stage G's five predictions
(`nd-unfolding/fd_g_compare.py:66-87`). Each tool has two committed arms:
- **with:** C_resp + C_PL,5D, under `fd/with-cpl/readout/`;
- **nopl:** C_resp, under `fd/readout/`. These are the "-nopl" keys.

| family (values keys) | readout | tool | key code |
|---|---|---|---|
| `g-*` incl. `g-*-nocresp-*`, `label-*`, pulls and g/f | `fd_g_readout.json` | `fd_g_compare.py` | `make_values_fived16.py:255-270` |
| `diag-*` | `fd_g_diag_readout.json` | `fd_g_diag.py` | `:395-400` |
| `r04-*`, `corr-*`, and the sensitivity records of `fd_g_followup_readout.json` | `fd_g_followup_readout.json` | `fd_g_followup.py` | `:271` |
| `sens-*` (the flux, detector and lateral weakening) | `fd_g_sens2_readout.json` (+ G-FOLLOWUP's records) | `fd_g_followup.py --part sens2` | `:271-285`, `:363-367` |
| `fb-*` (the flux bootstrap bands) | `fd_flux_boot_readout.json` | `fd_flux_boot.py` | `:429-451` |
| the sens figure, and the modes (note) and ratio (paper) figures | `fd_g_fig_{sens,modes,ratio}.{pdf,json}` | `fd_g_figures.py` from the four readouts above and F0b's | `FIGURES`, `:81-82` |

**Recomputed:** all five readouts in both arms, and the three figures in both arms.
- The brief names the sens figure.
- The modes figure (`sec_fived16.tex:307`) and the ratio figure (`paper_body.tex:236`) are drawn from the same
  readouts, so they move too. They are produced and named here. Whether to print them is the paper lane's call.

**Not recomputed, because they do not read the predictions:**
- F0b and F1: their grades use C_e, C_model and held-out truths, not the five predictions;
- the data product, the deposit candidate, f and every covariance block.

C_model itself is unchanged. Its vertices are still built from the carbon generators, which is #651 item 6's caveat and §6
here.

**A by-product.** In each arm, E-1's Stage G readout holds the corner's total and shape-only χ² for all four
predictions. XC (§3) requires them to equal `fd/gencmp/readout/defs.json`'s, the numbers #651 item 2 adopted. The paper
lane may therefore re-pin `READOUTS["g"]` (`make_values_fived16.py:37`) and `NOPL_READOUTS["g"]` to E-1's readouts and
keep one source for Table IV and the diagnostics.

## 1. Inputs

**`fd/gencmp-e/INPUTS.sha256`**, 42 pinned pscratch files, all present (`stat`, 2026-11-01; oldest atime 2026-10-24).
Every digest is copied from a committed record, and the file's header names the record for each family:

| family | what | count | pin source |
|---|---|---|---|
| S1/X | `$P/s1-20261024/s1_assembly.npz`, `$P/cresp-20261026/out/cresp.npz` | 2 | `fd_cpl_addition.py` `PINS` |
| P | Stage G's five predictions under `$P/s5p-20260926/` | 5 | `fd_g_compare.PREDICTIONS` |
| K | the ν-e + IMD flux constraint file | 1 | `s1_assemble.CONSTRAINT_SHA256` |
| B | step B's rebuilt analysis-definitions products, 6 samples × 5 seeds, and `rebuild.json` | 31 | `fd/gencmp/readout/rebuild_b.json` `outputs`; `defs.json` `rebuild_json_sha256` |
| R | `E_R` (`partb/out/ER/xsec.root`), `Q_R` (`partc-r2/combination/s5_plus_playlist.npz`), `C_PL_R` (`partc-r2/playlist/playlist_term.npz`) under `$P/2d-closeout-re2-20261023/` | 3 | `re2/run/hpss/members.sha256:1480`; `RE2-PARTC-REPORT.md:132`, `:129` |

**Committed inputs,** read from the deploy and pinned in the code:
- the H2 definition, the S1 readout, `cmodel_5d.json` and the s5p archive SHA256SUMS (`fd_g_compare.PINS`);
- the with-block extra block `fd/with-cpl/block/cpl_block.npz` (`d9aa32fd…`);
- `defs.json` (`544f4f43…`);
- the committed readouts and figures of both arms (`fd_gencmp_e.py` `COMMITTED`, `FIGURES`; `fd_cpl_addition.COMMITTED`).

**What C-R also reads.** GENCMP's own pins for P5, MnvTune v1, the 3D central value and PROJ3D come from
`fd/gencmp/INPUTS.sha256`, passed as a second `--inputs` file. Two files that pin one path differently stop the run.

## 2. The corner as prediction files (E-M), and what stays as it was

**The four predictions.** `fd_gencmp_e.py materialize` writes the four predictions of "CH, analysis definitions" to
`$B/pred/gencmp_e/<name>_ch_ana.npz`. It uses the functions `fd_gencmp.py defs` used to form the same corner
(`fd_gencmp.py:293-296`, `:357`):
- **GENIE CV and GENIE+MEC:** the five-seed mean of `xsec_flat` and `sumw2_flat`;
- **NuWro and GiBUU:** each of the carbon and hydrogen samples averaged over seeds, then combined 12:1 per nucleon by
  `fd_gencmp.combine`.

**What each file carries:**
- xsec, sumw2 and nevt as float64 on the 65,856-cell grid, with the grid's edges and a `meta_json` that names the
  prediction, its label, its 30 sources and `defs.json`'s digest. This is the structure `fd_g_compare.prediction_problems`
  checks.
- nevt is the five seeds' mean count per fine cell, summed over carbon and hydrogen. Stage G prints it per cell; it
  is descriptive and enters no statistic.

**The fifth prediction.** MnvTune v1, the analysis MC truth and Stage G's prior row, is copied unchanged
(`bf7bd278…`). It is the analysis's own truth, so it already has the analysis definitions.

**The manifest and the names.**
- One `SHA256SUMS` covers the five files.
- `predictions.json` records each as Stage G's tools take it: name, path, sha256, meta field, cells and label.
- The names, order and cells are Stage G's (`genie_cv`, `genie_mec`, `nuwro`, `gibuu` on its eight p_∥ < 4.5 cells,
  `mnvtune_v1`). Every rule that a bound tool keys on a name keeps its meaning.

**The labels** (`fd_gencmp_e.CHDEFS`).
- Each begins with Stage G's short name, so the values key `label-*` is unchanged, and then reads
  "CH, analysis definitions (rebuilt, GENCMP step B)".
- NuWro's carries its hydrogen label (`fd_gencmp.LABELS["nuwro_CH"]`).
- GiBUU's carries the full hydrogen label of binding ruling 2: "hydrogen: closure B3 failed;" then
  `fd_gencmp.LABELS["gibuu_CH"]`, plus Stage G's E_ν and p_∥ wording.

**Control E0.** For each of the four, before its file is written:
- its cell integrals g equal `defs.json`'s analysis-definitions g;
- its total and shape-only χ², under both matrices, equal `defs.json`'s.
- Both are to 1e-12 relative, with the worst g difference printed. `defs.json` was computed on a compute node and E-M
  runs on a login node, where BLAS may sum U x in another order. Bitwise equality is therefore not required, and that
  is said here in advance.
- E-M also checks that the staged `rebuild.json` is the one `defs.json` names.

## 3. The steps

| step | where | what | controls | stops if |
|---|---|---|---|---|
| E-S | login node | `fd_gencmp_e.py stage`: an O_NOATIME copy of each scratch pin to `$B/inputs/<path under $P>` | S: each copy is the pinned bytes; atime is compared before and after each read and recorded in `STAGE.json` | any digest differs |
| E-M | login node | `materialize` (§2) | E0; the rebuild directory is `defs.json`'s; MnvTune v1's staged file is Stage G's | any control fails |
| E-R0 | login node | `chain`, set `old`, arms `nopl` then `with`: Stage G, G-DIAG, G-FOLLOWUP, G-SENS2 and the flux bootstrap. Each runs as a subprocess of its bound tool on the staged copies, with each downstream step pinned to the sha256 of the readouts it reads (`fd_cpl_addition.Chain`, `UPSTREAM`, `STEP_PINS`); then the three figures and `fd_g_figures_check.py` | **R0** (below) | any R0 check fails: **E stops and reports**, and no new number is computed (ruling 4) |
| E-1 | login node | `chain`, set `chdefs`, both arms: the same tools with the predictions' root and manifest at `$B/pred`, and the set passed to each tool through its existing `predictions` argument (`run(a, pins, predictions)` in all four tools). Then the figures with `--prediction-set gencmp-chdefs`, and the check | P: each file is the bytes `predictions.json` records; **XC** (below) | P or XC fails |
| C-R | login node | §5 | §5 | §5 |

**R0, the gate.** In the old set, Stage G runs on the staged predictions. Each downstream step and the figures run on
the **committed** upstream readouts of that arm, pinned by their committed digests, as `fd_cpl_addition.without_arm`
does: each readout records its upstream's digest, so it can equal the committed one only if its upstream is the
committed one (`fd_gencmp_e.run_set`). In each arm, every readout E-R0 writes must equal the committed one
(`fd/readout/` for nopl, `fd/with-cpl/readout/` for with):
- the same JSON structure;
- every number, boolean and null to 1e-12 relative (`fd_cpl_addition.compare_numbers`);
- in the with arm, every string as well (`compare_strings`).

Only `argv`, `code_sha256` and the extra block's `file` (the path it was read from) are outside the comparison. In each
arm, every figure sidecar must equal the committed one in numbers and strings except `argv`, `code` and `versions`, and
every PDF must be the same bytes. Each readout check is first preceded by a check that the committed file is its pinned
bytes. This is fd_cpl_addition's control R, made stricter in the with arm.

**Why strings only in the with arm.** The committed with-arm readouts were written by the tools this branch runs. The
committed nopl readouts of G-DIAG, G-FOLLOWUP and the flux bootstrap were written by earlier versions: `fd_g_diag.py`
`7c161280…`, `fd_g_followup.py` `820b67c2…`, `fd_flux_boot.py` `f82bd4f4…`, as their `code_sha256` record. The
current versions reproduced them in structure and numbers in fd_cpl_addition's control R
(`FD-CT-5B-ADDITION-REPORT.md:119-125`), which did not compare strings. This choice is fixed here, before any run, and
is not a relaxation.

**Why R0 can hold.**
- The tools this branch runs are `fd_g_compare.py` `0a3c09cd…`, `fd_g_diag.py` `241bfd02…`, `fd_g_followup.py`
  `ec8cbc68…`, `fd_flux_boot.py` `d5b4bb09…`, `s1_assemble.py` `b157250a…` and `s5p_stage1_inspect.py` `26569afc…`.
  They are the files' sha256 at this branch's base and every with-arm readout's `code_sha256`. In the nopl arm they are
  the `code_sha256` of Stage G's and G-SENS2's readouts. The other three were written by the earlier versions above
  and reproduced numerically by the current ones (S1).
- The figure tool changes (§4), but only behind an option that defaults to today's behaviour.
- The environment is `root_6_28`. On a saul login node it has Python 3.11.14, numpy 1.26.4 and matplotlib 3.10.8,
  exactly the committed sidecars' `versions`.

**XC.** In each arm, the chdefs Stage G readout's g on each prediction's cells, and its total and shape-only χ², equal
`defs.json`'s to 1e-12:
- the with arm against `defs.json`'s `reported` matrix;
- the nopl arm against `without_C_PL5D`.

XC first requires each of the four corner predictions to be in the readout, and then compares each one. XC ties E-1
to the numbers #651 adopted.

**No tolerance is relaxed under this amendment.** R0's, E0's and XC's 1e-12, C3's figures and C-R's 1e-12 stand. A stop
caused by arithmetic noise is reported as a stop. A change to any tolerance needs a new declaration and binding (A7).

**Every tool reads copies.** The tools read only the staged copies, the files E-M wrote and committed files. No tool
opens a pscratch original. E-S's O_NOATIME reads are the only reads of the originals, and C-R's (§5) are O_NOATIME
too.

## 4. The figures' prediction set

`fd_g_figures.py` and `fd_g_figures_check.py` take `--prediction-set {stage-g, gencmp-chdefs}`, default `stage-g`.

**The default changes nothing:**
- the qualifiers, the required strings and the sidecar are today's;
- the option enters the sidecar's `options` only when it is not the default;
- the existing suites pass (`test_fd_g_figures.py`, `test_fd_cpl_addition.py`);
- R0 compares the default set's figures with the committed ones byte for byte.

**`gencmp-chdefs`:**
- **legend qualifiers:** "CH, analysis definitions" for all four generators. NuWro adds "hydrogen: supplement
  FLAGGED", and GiBUU adds "hydrogen: closure B3 failed" and "p_parallel < 4.5 cells only". MnvTune v1 keeps "prior (not
  an independent prediction)". Each stands in its prediction's label, so K7 holds.
- **K1** compares the readouts' labels and digests with the predictions passed in.
- **K0** refuses the set unless its predictions are passed (`fd_gencmp_e.py chain` passes them).
- The checker declares the drawn names independently. A test requires them to equal the figure tool's legend text in
  both sets.

## 5. Step C-R

- **Command:** `fd_gencmp.py overlap --arm refined --inputs fd/gencmp/INPUTS.sha256 --inputs fd/gencmp-e/INPUTS.sha256`,
  with `--cv2d`, `--q2d` and `--playlist` set to family R's three files. The other arguments are as in GENCMP step C.
- **The code path is step C's.** It changes only through `ARMS_2D`.
- **C3** compares the 2D integral with `E_R`'s recorded `hXSec2D.Integral("width")` = 3.069e-38, to four figures
  (`RE2-PARTC-REPORT.md:278-279`). Step C compared it with VL173's 3.0730e-38, to five figures.
- **New checks, each a stop:**
  - `Q_R`'s npz key `arm` is "refined", which `re2c_combine.py:252-253` writes;
  - `Q_R`'s central value is `E_R`. Its key is still named `cells_x_EU`; `re2c_combine.py:253` writes it, and in the
    refined arm `E_R` takes `E_U`'s role under the same keys (`RE2-DECLARATION-C.md:196`, `:207-214`). So max
    |CV/`cells_x_EU` − 1| over its 205 cells must be ≤ 1e-12;
  - `Q_R` covers every quadrant. Step C's "Q does not cover this quadrant" branch is a stop in C-R.
- **The outcome rule is step C's, unchanged,** read from the reported matrix C_total + C_resp + C_PL,5D against
  `Q_R`, over ρ ∈ [0, 1]:
  - agree;
  - agree below a correlation, with ρ* to four decimals;
  - differ.
  X replaces this rule with a measured ρ.
- **Control C-R3D.** The 3D descriptive rows read the same pinned 3D inputs as GENCMP step C, so each must equal
  `fd/gencmp/readout/overlap.json`'s 3D row to 1e-12 (S, d, d%, PROJ3D variance and the outcome; the file is pinned at
  `82b3528a…`). A difference stops the run. The 3D clause (#651 item 4) is
  unaffected.
- **Labels.** The readout records `arm_2d` = refined, `result_2d` = "E_R with Q_R", and step "C-R (Q26)".
- **What it supersedes.** Its 2D numbers supersede #648 §2.3's. They go to Joseph with X (ruling 3), and `:119` is not
  touched.

## 6. E2: #651 item 6's caveat, priced and not yet coded

**Why the same products cannot answer it.** C_model's vertices are real-data unfolds, each with the prior reweighted
to a generator's shape (`nd-unfolding/pv-ladder/build_cmodel5d.py:5-10`; `pv-ladder/config.json` `vertices`). The
NuWro and GiBUU vertices use the carbon files `475a2871…` and `48917692…`. Measuring the effect of the target needs two
new configuration (e) unfolds, with the CH files in their place:
- step A's combination in the generator definitions (`phase1/mp3b/.../mp3b_fine_nuwro.npz` `xsec_CH`,
  `phase1/mp3c/.../mp3c_fine_gibuu_frozen.npz` `xsec_CH`, both committed);
- the same reference GENIE CV, so only the target changes.

GENIE+MEC is already CH.

**The price.** The measured basis is PV-ladder job J5 (60206336). It ran five vertex and closure unfolds together on
one node in 811 s, for 0.2253 node-h (`pv-ladder/LEDGER.tsv:8`). Two unfolds fit in one such job, so the cap is **0.5
node-h**, one regular CPU job of ≤ 25 min.

**What follows the unfolds:**
- C_model,CH = SᵀS by `build_cmodel5d.py`'s rule, with the CH vertices;
- Stage G's total and shape-only χ² for the four corner predictions, recomputed with C_model,CH's absolute form in
  place of C_model_abs, in both arms;
- each prediction's change in χ², printed beside E-1's.

**The code.**
- What it needs: a vertex configuration with the CH files, and a Stage G run whose C_total uses C_model,CH.
- It is not on this branch. It lands as a follow-up commit, or as its own small PR with its own audit, and E2 does
  not run until its blobs are bound.
- The director binds its 0.5 cap with E (ruling 2).
- **When it runs is fixed now:** once its code is bound, E2 runs whatever E-1's numbers are, and its outcome row
  (§8) applies as written. Neither running nor withholding E2 depends on a result (A2).

## 7. Host, cost, reads and writes, HPSS

- **Host.** E-S, E-M, E-R0, E-1 and C-R all run on a saul login node, in `root_6_28`, from a fresh clone of the bound
  commit with empty porcelain, at **0 node-h**.
  - The basis is the precedent runs: GENCMP's steps A and C ran on a login node, and every Stage G tool's step is
    capped at 375 s by `fd_cpl_addition.TIMEOUT`.
  - If any step exceeds its timeout, the chain stops (rc 124), and nothing moves to a compute node without a new
    binding.
- **E2:** ≤ 0.5 node-h, regular QOS, CPU only.
- **Writes:** only under `$B`. Nothing goes to CFS, and nothing is written over a committed file.
- **Reads:** O_NOATIME for every pscratch original. A moved atime is a deviation, reported and not restored.
- **HPSS:** `$B` (inputs, predictions, chain outputs, logs) goes to `/home/j/josephrb/mnv-gencmp-e-20261101/`, after
  `hpssquota`, with an explicit file list. It is verified by `hsi hashverify` and by retrieval.
- **The report** commits the readouts, figures, `chain.json`, pins and logs under `FD/fd/gencmp-e/`, with the
  results index regenerated.

## 8. Outcomes, and what the paper says in each (fixed before any number is read)

| outcome | the paper |
|---|---|
| R0 fails in either arm | E stops; no new number is computed (the chdefs set never starts: `cmd_chain`). The paper keeps the lane's scoping clause ("carbon, generator definitions") on every Stage G diagnostic. The report names the first failing check |
| E0, P or XC fails | E stops; no number of the failing set is used, though an arm's readouts may already exist when XC runs. The paper is as for R0 failing. The report names the prediction and the quantity |
| E-1 completes | The paper lane re-pins `READOUTS` and `NOPL_READOUTS` for `g`, `diag`, `fup`, `sens2` and `fboot` to E-1's readouts and drops the scoping clause. Every regenerated number goes in as it falls. The report lists, mechanically, every values key of the families `g-`, `diag-`, `r04-`, `corr-`, `sens-` and `fb-` whose printed string differs. It does this by running `make_values_fived16.py`'s own formatting on a scratch copy, with `READOUTS` and `NOPL_READOUTS` pointed at E-1's readouts, and diffing the result against the committed `values_fived16.tex`. Every sentence that prints a listed key goes to Joseph through the paper lane, and none is reworded here. The figures the paper and the note print today (ratio, modes) are replaced one for one by E-1's, in the arm they print now. The sens figure is produced for the note. GiBUU's and NuWro's legends carry their hydrogen qualifiers |
| C-R, every quadrant reads as step C read it | the numbers replace #648 §2.3's in the records and go to Joseph with X. `:119` is unchanged until X reports (ruling 3) |
| C-R, a quadrant's reading changes (for example "agree below a correlation" to "differ") | the same, and named in the report as a change. A "differ" is a new problem for the director and Joseph (GENCMP ruling 4) |
| C-R stops (C3, the arm key, the central value, coverage, or C-R3D) | no C-R number is used; #648 §2.3 stands in the records, labelled as on the superseded 2D result; the report names the check |
| E2 runs | the caveat of #651 item 6 is replaced by its measurement: "Taking C_model's NuWro and GiBUU shape ratios from CH instead of carbon changes the χ² by at most Δ". Δ = max |χ²_CH − χ²_carbon| over the four corner predictions, both arms and both kinds (total and shape-only). Every signed difference is printed in the report |
| E2 not run | the caveat stays as #651 item 6 words it |

## 9. The code bound (blob digests at this branch's head, recorded in the PR and the binding)

| path | change |
|---|---|
| `nd-unfolding/fd_gencmp_e.py` | new: `stage`, `materialize`, `chain` |
| `nd-unfolding/fd_gencmp.py` | `overlap --arm {purity, refined}`, `--inputs` (repeatable); `ARMS_2D`; the `Q_R` arm, central-value and coverage checks; C-R3D against `OVERLAP_C` (`82b3528a…`) |
| `nd-unfolding/fd_g_figures.py` | `--prediction-set`; `run(a, pins, predictions)`; `PREDICTION_SETS`; K0's guard |
| `nd-unfolding/fd_g_figures_check.py` | `--prediction-set` with its own declared names; the sidecar's set checked |
| `nd-unfolding/tests/test_fd_gencmp_e.py` | new, 43 tests |
| `docs/.../fd/gencmp-e/INPUTS.sha256` | new (§1) |

**Unchanged and run by the chain:** `fd_g_compare.py`, `fd_g_diag.py`, `fd_g_followup.py`, `fd_flux_boot.py`,
`fd_cpl_addition.py` (its `Chain`, `step_argv`, `extra`, `compare_numbers`, `compare_strings`), `s1_assemble.py` and
`fd_gencmp_kin.py`.

**Tests.** Locally (Python 3.12.2, numpy 1.26.4, matplotlib 3.10.1), `python3 -B -m pytest tests/test_fd_gencmp_e.py
tests/test_fd_gencmp.py tests/test_fd_g_figures.py tests/test_fd_cpl_addition.py tests/test_fd_gencmp_rebuild.py`
gives 265 passed and 3 skipped. These are the new suite plus every suite whose code this branch touches or reuses.
The new suite tests each control both ways:
- stage's pin;
- E0's g and χ²;
- the set's file digests;
- R0's comparison and its exclusions;
- XC in each arm;
- the figure set's guard and legend agreement;
- C-R's arm key, C3 in both arms, C-R3D and two disagreeing inputs files.

**Not tested end to end.** The chain itself (E-R0 → E-1) has no end-to-end test on synthetic inputs. Its parts are
tested, the tools it runs have their own suites, and R0 on real inputs is its control.
<!-- absence-ok: a statement about this branch's own new suite (tests/test_fd_gencmp_e.py, every test listed by name), not a claim that a result does not exist -->

## 10. Limits

- **What E-1 can and cannot say.** E-1 changes the predictions only. Its χ² still use C_model from the carbon
  generators, which E2 measures. Every E-1 readout is labelled with its set.
- **GiBUU.** It is still compared on its eight cells, with its hydrogen label. The corner's GiBUU hydrogen sample is
  MP3-C's, and B3 failed on it.
- **C-R** keeps step C's bounded rule and its limited power (GENCMP declaration §10). X is the test.

## 11. Review

A fresh Sonnet subagent (not sol) audited the declaration and the code at head `0509718c` (ruling 5). Its prompt and its
answer are verbatim beside this file: `FD-GENCMP-AMENDMENT-E-REVIEW-PROMPT.txt` (the `<WORKTREE>`, `<TMPDIR>` and
`<HEAD>` placeholders were filled with this worktree, its scratch TMPDIR and `0509718c3`) and
`FD-GENCMP-AMENDMENT-E-REVIEW-ANSWER.txt`. Every finding is fixed or answered:

<!-- absence-ok: each row quotes an audit finding about this branch's own tests at head 0509718c, with the test that now covers it; none claims a result does not exist -->
| finding | what was done | where |
|---|---|---|
| A1, R0 excluded `/extra_block/path`; the key is `/extra_block/file` | fixed before any run | `fd_gencmp_e.R0_EXCLUDE`; §3 |
| B1, the old set fed new upstream readouts, so their digests (and the figure sidecars' `inputs_sha256`) could never equal the committed ones | fixed: the old set's downstream steps and figures run on the committed upstream readouts and pins, as `fd_cpl_addition.without_arm` | `fd_gencmp_e.run_set`; §3 |
| B2, `check_r0` and the order gate untested | tests on copies of the real committed readouts and figures of both arms (passing with argv, code_sha256 and the block's file changed; refusing a changed number or PDF byte); a test that the chdefs set never runs after an R0 failure | `test_r0_passes_on_committed_copies_and_refuses_one_change`, `test_the_chdefs_set_never_runs_after_an_r0_failure` |
| S1, the nopl readouts of G-DIAG, G-FOLLOWUP and the flux bootstrap were written by earlier tool versions | stated; R0 compares structure and numbers in the nopl arm, as the bound control R that already reproduced them, and adds strings in the with arm only. Fixed before any run | §3; `check_r0`; `test_r0_compares_strings_in_the_with_arm_only` |
| A2, E2's decision and Δ open | fixed: E2 runs once bound, whatever E-1 shows; Δ = max \|χ²_CH − χ²_carbon\| over predictions, arms and kinds, every signed difference printed | §6, §8 |
| A3, "qualitative change" a judgement | replaced by a mechanical diff of every printed values key in the six families | §8 |
| A4, which figures to print left open | the ratio and modes figures are replaced one for one; the sens figure is produced for the note | §0, §8 |
| A5, B4, the units diagnostic and the uncovered-quadrant branch had no outcome | both are stops in C-R (central value ≤ 1e-12; every quadrant covered), with an outcome row | `fd_gencmp.cmd_overlap`; §5, §8; two refusal tests |
| A6, NuWro's hydrogen flag not on its legend | added: "hydrogen: supplement FLAGGED" in its label and legend, and in the checker's declared name | `fd_gencmp_e.CHDEFS`; `fd_g_figures.PREDICTION_SETS`; `fd_g_figures_check.PREDICTION_SETS` |
| A7, tolerance relaxation | stated: no tolerance is relaxed under this amendment | §3 |
| B3, the K1 test re-typed the expression | the test now calls `fd_g_figures.check_chain` on the committed nopl readouts, passing and refusing | `test_check_chain_compares_against_the_passed_set` |
| B5, the MnvTune check had no refusal test | added | `test_refuses_a_staged_mnvtune_other_than_stage_gs` |
| B6, XC looped over the readout and refused only a total χ² | XC now requires each corner prediction; tests refuse a changed g, a changed shape-only χ² and a missing prediction, and pass the nopl arm against `without_C_PL5D` | `check_xc`; three tests |
| B7, P's names branch and E0's quantity untested | added | `test_load_chdefs_refuses_names_out_of_order`, `test_e0_names_the_quantity_that_differs` |
| S2, "#651 item 8" is not in the record | the caveat is cited as item 6's "one stated caveat", with the brief's name noted | header, §0, §6 |
| S3, the `cells_x_EU` citation | corrected to `re2c_combine.py:253` and `RE2-DECLARATION-C.md:196`, `:207-214` | §5 |
| S4, "no new number is computed" after XC | reworded: no number of the failing set is used | §8 |

Nothing is submitted, deposited or tagged.
