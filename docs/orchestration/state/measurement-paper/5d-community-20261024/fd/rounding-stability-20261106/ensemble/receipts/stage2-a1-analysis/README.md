# ENS1 A1 stage-2 analysis: the receipt (2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The analysis was run under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`. The director pre-reviewed the connect's sha256 and
gave the go after the stage-2 full run's receipt (`../stage2-a1/`) and its POST-RUN PASS.

**Result: `BIAS_WORSE`.** The bound `ensemble_estimator_analyze.py --stage 2` exited 0 with that verdict.
- E₉₆ is worse than F at one truth, `stage0c_gibuu` (Stage 0c GiBUU), on the RMS metric.
- It is no worse at the other 16 judged truths. Every truth's floor is non-zero (`valid: true`), so the verdict is not
  INVALID.
- Under declaration §5.3, E₉₆ is therefore not described as a stabilised variant.
- The analysis ran on a login node at 0 node-h, so stage 2's spend stays 33.1347 of its 46.0 cap.

**CITABLE FOR:**
- the stage-2 verdict of ENS1 (declaration §5): BIAS_WORSE, with `worse = ["stage0c_gibuu"]`;
- the numbers in `ens1_stage2.json`, as the bound tool wrote them.

**NOT CITABLE FOR:**
- any statement that E₉₆ is a stabilised variant (§5.3: "BIAS_WORSE: … E₉₆ is not described as a stabilised
  variant");
- any use of the GiBUU bias magnitudes beyond "no worse" (FD-STAB §5.3, quoted below);
- any absolute statement about E₉₆'s bias;
- a paper sentence. Wording is Joseph's, through the PRD read.

## The connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_s2_analysis.sh` is the copy the connect wrote, sha256 `c5ee4378…`.
- The launcher is `ens1_a1_s2_analysis_launch.sh`, `f652f2d1…`.
- The launcher rc and ssh rc were both 0 (`launch-analysis.out.txt` holds the ssh rc line).

**`connect-analysis.log.txt`** (login37, 2026-11-08T23:53:50Z–23:54:11Z, rc 0):
- **Its preconditions:**
  - The stage-2 post-run's done file read 0, and its `s2-full-read.json` (`b0dcdb27…`, on pscratch) said PASS.
  - Stage 1's `ens1_stage1.json` is at `7f5a9ce4…`, STAB_PASS.
- **The fence:** pass. `squeue-before.txt` is empty.
- **The deploy:** HEAD is `f4d2d7f3` with 0 modified tracked files before and after.
- **The bound digests:** all eight sha256s match:

  | file | sha256 |
  |---|---|
  | `ensemble_estimator_analyze.py` | `1d6a0448…` |
  | probe | `807c40d3…` |
  | `estimator_stability_analyze.py` | `391fdc82…` |
  | s5c contract | `d54fd7c9…` |
  | sigma receipt | `84266e30…` |
  | h2 definition | `b6790761…` |
  | FD-STAB's SHA256SUMS | `e2c35e55…` |
  | FD-STAB's `readout-2/fd_stab.json` | `653356ae…` |

- **The reference copies:** the 70 copies are as at the stage-2 dry connect. `connect/refs-SHA256SUMS` is
  byte-identical to `../stage2-dry-a1/connect/refs-SHA256SUMS`.
- **The environment:** Python 3.11.14. `env-analysis.log.txt` shows the same two missing `setup.sh` warnings as the
  runs.
- **The output:** `ens1_stage2.json`, sha256 `c2ee701d7c23643b257f633410c8416d4ca4e8ce5eb8b8ad38ff3afd244c01fd`,
  6,326 bytes. It is committed here as the tool wrote it, with no key renamed.

## The readout (`ens1_stage2.json`)

**The keys and the sections that govern them:**
- **`bias`:** the criterion input of declaration §5.1–5.2.
  - Per truth, it holds RMS and MAX of b = X / X_true − 1 on the 16 reporting cells, for E₉₆ (`rms`, `max`) and F
    (`rms_control`, `max_control`).
  - It also holds the floors `delta_rms` and `delta_max`, from the bound `estimator_stability_analyze.no_worse`
    (`:118-128`).
  - `no_worse` is true when both excesses are within their floors.
- **`sd_upper`, `s_F`, `s_E_scaled`:** the §5.2 floor inputs.
  - The 95 % upper factors are 1.358 for E₉₆ (20 degrees of freedom) and 1.20 for F (50).
  - s_F is F's per-cell rounding SD. s_E is E₉₆'s, scaled by 1.358 / 1.20.
- **`truths_judged`, `worse`, `verdict`:** the §5.3 verdict over the 17 distinct truths.
- **`gibuu_readout_descriptive`:** the §5.3 readout, which is "printed and used by no criterion (FD-STAB §5.3)". It
  repeats the two GiBUU truths' RMS and MAX for E₉₆ and F. The verdict is fixed at `ensemble_estimator_analyze.py:331-332`
  (at M_A1), before this readout is assembled at `:333-334` and `:338`, so the verdict does not read it.

**Each truth's excess E − F against its floor** (the lane's arithmetic on the JSON's `bias`; the ratio is excess /
floor, and "no worse" needs both ratios ≤ 1):

| truth | ΔRMS | floor | ratio | ΔMAX | floor | ratio | no_worse |
|---|---|---|---|---|---|---|---|
| nominal | +0.000060 | 0.000380 | +0.16 | −0.000032 | 0.001735 | −0.02 | true |
| W1 | −0.000271 | 0.000392 | −0.69 | −0.000674 | 0.001294 | −0.52 | true |
| W2 | −0.000009 | 0.000412 | −0.02 | −0.000049 | 0.001290 | −0.04 | true |
| W3 | +0.000017 | 0.000387 | +0.04 | +0.000012 | 0.001294 | +0.01 | true |
| q3 | −0.000202 | 0.000444 | −0.45 | −0.000273 | 0.001290 | −0.21 | true |
| **stage0c_gibuu** | **+0.000512** | **0.000418** | **+1.23** | +0.000929 | 0.001783 | +0.52 | **false** |
| closure_nuwro | +0.000236 | 0.000519 | +0.46 | +0.001331 | 0.002339 | +0.57 | true |
| A7_genie_cv | +0.000032 | 0.000404 | +0.08 | +0.000679 | 0.001294 | +0.52 | true |
| A7_genie_mec | −0.000164 | 0.000421 | −0.39 | +0.000401 | 0.001735 | +0.23 | true |
| A7_nuwro | +0.000091 | 0.000514 | +0.18 | −0.002102 | 0.002281 | −0.92 | true |
| A7_gibuu | −0.000829 | 0.000465 | −1.78 | −0.003489 | 0.001783 | −1.96 | true |
| P1r | −0.000025 | 0.000384 | −0.06 | +0.000646 | 0.001294 | +0.50 | true |
| P2r | −0.000054 | 0.000538 | −0.10 | −0.000378 | 0.002339 | −0.16 | true |
| P3r | −0.000008 | 0.000497 | −0.02 | +0.000078 | 0.002281 | +0.03 | true |
| P1g | −0.000539 | 0.000370 | −1.45 | −0.000819 | 0.001294 | −0.63 | true |
| P2g | +0.000118 | 0.000553 | +0.21 | +0.000530 | 0.002281 | +0.23 | true |
| P3g | −0.000023 | 0.000384 | −0.06 | +0.000089 | 0.001294 | +0.07 | true |

- **At `stage0c_gibuu`:** E₉₆'s RMS is 0.056467 against F's 0.055955, an excess of 0.000512 over a floor of 0.000418.
  That is the one failed comparison. Its MAX excess, 0.000929, is within its floor.
- The largest ratio among the 33 other comparisons is closure_nuwro's MAX, +0.57.
- **The determinism control:** A7_mnvtune k = 1 equals nominal k = 1 bitwise. The analysis checks this and would have
  stopped otherwise.

### The GiBUU truths and the verdict

Both GiBUU truths, `A7_gibuu` and `stage0c_gibuu`, are among the 17 judged. The basis is these two sentences:
- `ENS1-DECLARATION.md` §5.3 (`:220`, `:225-226`): "**PASS:** no worse at all 17 truths." and "**The GiBUU
  readout** (A7 GiBUU and Stage 0c GiBUU biases, per estimator) is printed and used by no criterion (FD-STAB §5.3)."
- `FD-STAB-DECLARATION.md` §5.3 (`:206-209`): "**Neither the bias criterion beyond "no worse", nor any other
  criterion, nor the tie-break may use them**".

So "no worse" judges both GiBUU truths, and only their bias magnitudes are descriptive. The bound code does this. The
director confirmed this reading of the bound rule. The lane reports the verdict as the bound tool wrote it, with no
reinterpretation.

**The declared familywise rate** of a false "worse" over 17 truths × 2 metrics (`ENS1-DECLARATION.md:216-217`): "about
0.5 % with correctly estimated SDs, at most about 4.5 % if both are underestimated by their full factors."

**The stage-2 teardown does not bear on the verdict.** Task `ens1_stage0c_gibuu_k057` (k = 57 and 58 of this truth)
re-ran after a teardown exit (`../stage2-a1/`, "The teardown"). The re-run's `xsec_flat` and `xtrue_flat` equal the
first run's array for array, so the analysis reads the same values whichever run produced them.

## The results index

`ens1_stage2.json` is classed `included`: its `bias` key is a metric token. **The director's ruling A**, given for
`ens1_stage1.json` and applied to this file, is to commit the JSON as written with the four `--write` outputs:
- `RESULTS-INDEX.tsv` and `RESULTS-POPULATION.tsv`;
- `docs/analysis-note/records_results_index.tex` and `records_estimators.tex`.

`records_results_index.tex` is a generated records table, not authored paper text. There is no key rename and no waiver
row.
- **What the index records:** `--write` adds one row for this file, under the `bias` family, `UNATTRIBUTED` and
  `unreviewed`. That is accurate.
- **The other outputs:** `records_estimators.tex` regenerates unchanged.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has one row for this connect.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

**Next:** the director writes the ENS1 outcome record once this receipt and `../stage2-a1/` are merged.
