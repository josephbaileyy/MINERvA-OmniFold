# Where our 2D inputs differ from MINERvA's: the IBU-vs-published test chain (2026-11-23)

**By** the `ibu-chi-squared-issue` session (Claude Opus 5.5), for Joseph. Joseph authorized each step in that session.
He approved committing these records on 2026-11-23. The director reviews and merges. Joseph decides any note wording.

**The question.** Our K=10 binned IBU of the recorded 2D data sits at χ²/205 = 1.03 from the published 2D result
(PRD 104, 092007) on the published covariance. The signed target gives 0.96 ([OUTCOME-20261119-ibu-signed-data.md](../../OUTCOME-20261119-ibu-signed-data.md)).
Both results use the same data. This chain looks for where our inputs differ from MINERvA's.

**CITABLE FOR:** the controls and readings as measured, under each test's declaration, and the sentences below
written in "consistent with" terms.

**NOT CITABLE FOR:**
- a cause of the IBU or OmniFold difference from the publication;
- which input, ours or MINERvA's, is right;
- any statement about MINERvA's own code, selection or calibration;
- coverage, an estimator choice, or any note or paper wording.

## How each test was run

Each test's declaration was written and hashed before any number it reads was computed. It is stored as `DECLARATION.txt`, byte-identical to the file that was hashed, so the hashes below still verify. Where a control stopped
a test, an amendment was appended below the original text. The text above each amendment still hashes to the sha
declared at the time:

| test | declared sha (original) | file sha now (with amendments) |
|---|---|---|
| `truthtest` | `69efb1aa…` | same |
| `priortest` | `00bfccd4…` | same |
| `foldtest` | `f07b5d0b…` | same |
| `bkgtest` | `0210822b…` | same |
| `oflow` | `b280df9a…` | `7aa16c9d…` (amendment 1) |
| `lattest` | `634cffc3…` | `d3e3ac49…` (amendment 2) |
| `wstest` | `a02ddbd1…` | `80454dde…` (test W amendment 1) |

To check one, strip everything from the line `## Amendment` down, and the blank line before it, then hash the rest.

The scripts are committed as run. They carry the session's absolute paths: the scratchpad, `~/cov2d-work/figfetch/er-anc/`
and `/pscratch/sd/j/josephrb/`. Local runs used Python 3.11.18, ROOT 6.40.04, numpy 1.26.4 and scipy 1.17.1
(`rootmpl3108`). Perlmutter runs used Python 3.11.14, ROOT 6.28/12 and numpy 1.26.4 (`root_6_28`).

## The chain

| # | test | question | reading | in short |
|---|---|---|---|---|
| 1 | `truthtest` | Is our MC truth the shipped Tune v1 model? | **SYSTEMATIC** | χ²(shipped − ours)/205 = 1.572. The baselines are 0.011 for rounding alone and 0.43 for MC statistics, both at their 99th percentile. Shipped/ours rises with p‖ to +16–20 % at 40–60 GeV/c. It is +6–9 % in the lowest pT row. |
| 2 | `priortest` | Does the shipped shape, used as the IBU prior, move the IBU? | **MINOR** | K=10: 1.027 → 0.991 (f = 0.034). With the signed target: 0.961 → 0.922. Started from the published result itself, the IBU ends at 1.53. |
| 3 | `foldtest` | Does the published result, folded through our response, fit our reco data? | **PATTERNED: P‖, LOWPT** | χ²/n = 3.34, against 0.51 for our own K=10 result. Our data are 3–7 % below the fold at reco pT 0–0.07 and 6–24 % above it at reco p‖ 40–60. |
| 4 | `bkgtest` | Could our background subtraction close the 40–60 gap? | **INTERMEDIATE**; low pT **WRONG-SIGN** | All background is 7.1 % of data at 40–60 and would need ×2.29. At low pT, background cannot be the cause. |
| 5 | `oflow` | Are overflow fakes (true p‖ > 60) the cause? | **EXCLUDED**; **SCALE-INCONSISTENT** | They are 2.9 % of data at 40–60 and would need ×4.15. The 20–40 column would need ×40. |
| 6 | `lattest` | Do the standard lateral shifts of our response close either region? | 40–60 × Muon_Energy_MINOS **CLOSES-3**; all others **NO-EFFECT** | The 40–60 shape excess is +10.0 % at CV and +4.6 % at the +1σ shift, which raises MC reco momentum. A zero is reached at σ* = 2.007, just past the declared 2σ bar. MuonResolution, Muon_Energy_MINERvA and the beam angles have no effect on 40–60, and no band moves the low-pT row past its bar. |
| 7 | `wstest` S | Does one MINOS momentum scale fit the whole p‖ profile? | **TOP-ONLY** | σ = 0.056 [0.029, 0.083] from p‖ < 20, against 1.43 [1.25, 1.62] from p‖ ≥ 20. |
| 8 | `wstest` W | Do the shipped model's weights, applied per event in (E_ν, Q²), explain it? | **WEIGHT-MODEL-INADEQUATE** (inconclusive) | The fit matched the 40–60 truth (17.9 % → 0.2 %) but left +3.3 % in the lowest pT row, against a 2 % bar. Reported, not licensed: the 40–60 reco misfit goes 10.0 → 8.8 %, low pT −6.4 → −6.5 %, IBU K=10 0.961 → 1.186. |
| 9 | [`evloop`](evloop/results/README.md) | Do the official MINOS cuts, MasterAnaDev's momentum, a data-only MINOS scale or a data-only beam-angle offset fit the published result to our reco data? | **NONE** of the tested | Controls pass. MasterAnaDev `muon_P` equals `GetPmu` on every row, so that variant had no power. Removing the 40–60 excess needs a −2.7 % curvature scale, at fold χ² 4,522 against 395. |
| 10 | [`fig2`](fig2/README.md) | Do our selected data and MC match MINERvA's Fig. 2 in the two regions? | **UNRESOLVED** (both) | Descriptive: at 40–60 our data match theirs (+0.2 %) and our MC is 11 % low. At pT 0–0.07 our data and MC are both about 7 % low, with equal data/MC. |
| 11 | [`variants`](variants/README.md) | Is the truth difference already there against shipped bare GENIE? | **UPSTREAM**, against our *tuned* truth | Bare GENIE is +12.0 % in shape at 40–60 (Tune v1 +14.7 %). The test cannot separate an upstream difference from our tune weights without our own bare-GENIE truth. |
| 12 | [`flux`](flux/README.md) (first) | Does our constrained flux differ in shape from Valencia 2019's? | **not read**: wrong histogram | The first reconstruction used MAT's generation flux. The runtime flux is 0.996 of Valencia's in total and 4–11 % lower above 20 GeV in shape. |
| 13 | [`flux/fluxrw`](flux/README.md) | How much of the truth gap does that flux tail explain? | **FLUX-MAJOR** at truth p‖ 40–60; **FLUX-MINOR** at low pT | Reweighting by Valencia/MAT in E_ν closes 84 % of the shipped-vs-ours shape gap at 40–60 (93 % at 20–40). Reco S_COL moves only 0.100 → 0.095. |
| 14 | [`resp`](resp/README.md) | Do our p‖ migration and efficiency match the paper's Figs. 3 and 5? | **EFF-DIFF** | Migrations agree within 0.03. Our efficiency at true p‖ 40–60 is 0.747 against 0.861. Reco overflow (6 %) explains about half of the gap (descriptive). |
| 15 | [`axis`](axis/README.md) | Does a common beam-axis rotation explain the low-pT rows against Fig. 2? | **EDGE: AXIS-NO** | The deficit is largest at low p‖, the opposite of what a rotation predicts. Explained by test 16. |
| 16 | [`edges`](edges/README.md) | Are the paper's pT edges 0.075 / 0.325 / 0.475? | **EDGES-CONFIRMED** | The release's own TH2D axis stores them. Rebinning our data with them against Fig. 2 takes X from 104.9 to 19.4, and every affected row lands within 1.5 %. Our analysis uses 0.07 / 0.33 / 0.47; see the impact inventory. |

**Post hoc, read by no rule (`foldtest/posthoc_exclude.py`).** Dropping reco pT row 0 and the p‖ 40–60 column from the
IBU-vs-published χ² takes it from 210 to 100 over 176 cells. Cells were dropped from a correlated covariance, so this
is not an attribution.

## What the chain is consistent with

**Correction, 2026-11-24.** In the list below, "a reco effect confined to high-momentum, curvature-measured muons"
overreaches: the fold locates the disagreement in reco space, not its mechanism. "Beam angle" in the low-pT item means a
*data-only* angle offset; a difference common to data and MC, which test 10 suggests, was not tested. Tests 9–11 above
update the picture.
<!-- absence-ok: scoped to this lane's test chain; it names what these tests covered, not whether a study exists elsewhere -->

**Correction, 2026-11-24 (test 16).** The paper's pT edges are 0.075, 0.325 and 0.475; ours are 0.07, 0.33 and 0.47.
Every comparison above with the published cross section, or with the shipped models, in pT rows 0, 1, 3, 4, 5 and 6
therefore compares densities over different bins. That covers tests 1–3, 5–9, 11, 13 and 14. In particular, the low-pT
row findings (fold ROW −5.4 %, the truth test's +6–9 % lowest-pT row, and the fig2 low-pT deficit) are at least partly an
edge artefact. The 40–60 column is a p‖ bin and is unaffected by the pT edges as a whole column, but its per-cell values
in the affected rows are not. No test here has been rerun with the corrected edges.

- Our MC truth differs from MINERvA's shipped Tune v1 prediction beyond rounding and MC statistics. The events are the
  same public ones, so this is consistent with different event weights (flux or tune). It is not consistent with
  statistical noise. This contradicts `3d-unfolding/genie/README.md:110-112`. See [CORRECTION-genie-readme.md](CORRECTION-genie-readme.md).
- The IBU distance is consistent with coming from our response and reco data, not from the prior.
- At reco p‖ 40–60 the misfit is consistent with a reco effect confined to high-momentum, curvature-measured muons. Two
  forms remain: a momentum calibration that differs only there, or a selection acting at high momentum. These records
  cannot separate them. They are not consistent with overflow-fake handling, a uniform momentum scale, muon
  resolution or beam angle. Weights are disfavoured descriptively by test 8. That is not a licensed reading.
- The deficit at reco pT 0–0.07 is not explained by background, beam angle, resolution or either energy scale.
  Event-level weights explain it only in part. It remains open.

## Stops, amendments and blindness

- **`oflow`: STOP for a missing input, then amendment 1.** The pinned CV file's `mc_background` has no truth labels.
  The labels came from the `bkgaware` 5D file. Its `mc_background` equals the pinned CV's event by event (C-SAME),
  and its sum reproduces `hBkgReco2D` to 5×10⁻¹⁵ (C-BKG). No reading had been computed.
- **`lattest`: C-TRUTH STOP, then amendment 2.** C-TRUTH was mis-specified. `Muon_Energy_MINOS` changes `w_truth` by
  design, up to 5.4 %, because it is a flux-coupled universe with its own flux denominator. Because `hFlux_pt` is one
  constant, the amendment uses shape-only region statistics. **Disclosure:** the descriptive IBU χ² values were
  printed beside the STOP and seen by the analyst, not by Joseph, before amendment 2. They are not blind. The region
  readings were not computed before the amendment and are blind. Job 61879741 started 4 identical tasks because `-n 1`
  was omitted. All 11 outputs pass their hashes and zip CRC, and the CV build matches the archived response to 1×10⁻¹⁴.
  <!-- absence-ok: a statement of what this analysis computed and when, recorded for blindness, not a claim that a result does not exist -->
- **`wstest` W: C-ROW STOP, then amendment 1.** The CV copy and the `BeamAngleX_0` lateral are not row-aligned, and
  there is no event key to join on. The source became the single `bkgaware` file. C-CV passes at 5.6×10⁻¹⁴. No W number
  had been computed before the amendment.
- **`bkgtest`** corrects a sign error in the proposal before it. The 40–60 data sit above the fold, so dropping a
  subtraction moves the wrong way.

## Inputs opened, and custody

| input | how it was read | atime |
|---|---|---|
| `~/cov2d-work/figfetch/er-anc/xsec.root` (E_R, `a5c13fc3…`) and `cov_ptpl_minerva_inclusive_6GeV.root` (`6c6dce72…`) | local copies | n/a |
| `2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` | repo file | n/a |
| `/pscratch/sd/j/josephrb/ibukt-signed-data-a2.aOBfm4/out/study/signed_data.npz` (`7a35b7e2…`) | O_NOATIME stream, hash equal to the pin | unchanged |
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC.root` (the pinned CV, `43f8cc16…`) | O_NOATIME hash and copy to `oflow-split-20261123/cv.root`, then ROOT reads the copy only | unchanged |
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root` | ROOT, several times (`oflow`, `wstest` W amendment 1) | **moved**, first from 2026-09-27 08:25:39 to 2026-11-23 11:46:33 PST |
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` | O_NOATIME via `uproot`; stopped before completing | not checked |
| `/pscratch/sd/j/josephrb/cov2d-inputs-20261104/laterals/runEventLoopOmniFold_5D_MEFHC_active_<band>_<0,1>.root`, for Muon_Energy_MINOS, Muon_Energy_MINERvA, MuonResolution, BeamAngleX, BeamAngleY | ROOT, by job 61879741; `BeamAngleX_0` again by job 61880730 | **moved** |

The staging directory `/pscratch/sd/j/josephrb/oflow-split-20261123/` holds the CV copy, a throwaway `uproot` venv,
the scripts, `lat/` and `wsplit_a1.npz`.

**Compute.** All three jobs ran on account m3246, CPU, QOS interactive, on one node, on 2026-11-23:
- 61879741 `lattest-ibu`, COMPLETED, 1:13;
- 61880730 `wstest-ibu`, FAILED at C-ROW, 0:36;
- 61880806 `wstest-a1`, COMPLETED, 0:37.

Together that is about 0.04 node-h. Everything else ran on login02 or locally.

## Products in this directory

- `*/DECLARATION.txt`, the scripts, and `run.log` or `*.log`/`*.out`, with each run's printout.
- `truthtest/vectors.npz` and `priortest/vectors.npz`: the per-cell vectors that the later scripts read.
- `oflow/split.json` (`9a526f83…`): the background categories per reco cell.
- `lattest/lat/*.npz`: the binned (M, T, B) for the CV and the 10 laterals. Their hashes are in the session's
  `SHA256SUMS` on Perlmutter.
- `wstest/wsplit_a1.npz` (`1e491dff…`): the (E_ν, Q²)-split truth and response.
- `signed_data.npz` is not committed. It is the signed-target study's product and stays at its origin under its pin.
