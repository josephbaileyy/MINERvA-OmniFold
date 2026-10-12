# Stage B admission review: commit `45fd98f7`, `docs/orchestration/state/2d-closeout/stageB/REPORT.md`

**Reviewer:** a fresh, read-only session (Claude Opus 5.5). I wrote my own code and read the worker scripts only to learn which input files they used. I did not redo the C04/X01 verification, apart from checking how KI 95/96 state it and confirming that C04 also holds on the July sweep.
**Date:** 2026-10-12. **Worktree:** detached at `45fd98f7`. **Cluster:** saul `login05`, ROOT 6.28 (`root_6_28`). I ran no Slurm job and wrote only under `.../2d-closeout-stageAB-20261012/review-b/`.

## Verdict: **PASS WITH CHANGES**

Every worker-measured number I recomputed reproduces, most of them exactly. **EXIT CONDITIONAL** is the right verdict: EXIT MET would need a final recipe, and R10 says the recipe is not final yet. The source table does assign all 44 bands in `uq/universes_full_list.txt` and every C01–C10 and X01–X03 source. None of the findings below is MATERIAL. Seven MINOR findings should be fixed before the PR goes to the director. They concern record text, pricing convention and how the stakes are stated. None of them changes a measured number.

## Findings

### MATERIAL
None.

### MINOR

**M1. G1's consequence and its repair cost are not stated.**
- Where: REPORT.md:53, 56–58, 224–232, 362–365.
- I traced the code path. `mc_signal_reco` drops reco-tree-in-PS events whose truth-tree row fails PS (`runEventLoopOmniFold.cpp:1203-1212`). `mc_background` also skips them (`:1454-1456`). So they are neither modeled nor subtracted.
- If the census finds them, the effect is a **bias in the adopted central value** (`E_U`, DECISION-20261011), not only a missing uncertainty term. The repair would most likely need new event-loop omnifiles: the CV, the 187-universe dump and the active files, followed by re-unfolding the central value and every block.
- §7 says "Not included: a G2 repair … and all Stage D/E work". It is silent on G1.
- Failure scenario: Joseph prices Stage C at 47.8–78.5 node-h. P4 then confirms G1 at about 1%. The real cost, and a change to the central value, appear only after approval.
- Fix: say that a confirmed G1 changes the adopted central value, and give a bracketed G1 repair cost or mark it explicitly as unpriced.

**M2. The §8 Stop analysis does not test G1 against "missing selection support".**
- Where: REPORT.md:367–375.
- §8 tests only the beam-angle laterals under that heading. G1 is a support gap: events absent from both trees, and they cannot be measured from saved products.
- The plan's Stop wording is "missing selection support … Record the specific missing input and acquisition route".
- CONDITIONAL is defensible because the route is named and priced. But the record should argue why G1 is a routed candidate and not a Stop. Otherwise a reader can call the verdict wrong.

**M3. The KI 95 and KI 96 remedies point at outputs this record retires.**
- Where: KNOWN_ISSUES.md:85 ("100 existing `universe_sweep_fluxfix` outputs") and :86 ("the two existing `Muon_Energy_MINOS` outputs").
- The same commit retires the May sweep (R1, REPORT.md:275–276), and R4 (REPORT.md:281) and the C04 row (REPORT.md:256) replace or name the July/active inputs.
- Failure scenario: a Stage C executor follows the KI row and builds the repaired flux and MINOS blocks from the retired May sweep.
- I checked that C04 transfers to July (see the numbers table: weighted 3.747% on July against 3.655% on May). Only the text needs to change: "the adopted (May) sweep for the diagnostic number; the July sweep under R1".

**M4. "July qualified" and "passes" do not survive being read alone.**
- Where: KNOWN_ISSUES.md:83 ("The July `purity_newomni` sweep passes this row's bar") and the REPORT.md:134 heading.
- REPORT.md:147–148 carries the limit: the July products have no driver or input digest, their tie to the omnifile rests on mtimes, and P2 bridges this. The KI note omits that limit.
- The limit is stronger than the record says. The July products (CV mtime 2026-07-08 18:48 UTC) predate `cf8a4a67` (2026-07-11), the first commit that contains `_universe_bkg_branch`. Yet their backgrounds vary per universe (185/187). **So the July sweep ran on uncommitted driver code.** REPORT.md:154–156 dates the feature by that commit.
- Fix: add "provisional pending the P2 bridge; producer revision uncommitted/unknown" to the KI 93 note and to the heading.

**M5. The KI 92 note mislabels a number and lacks the NOT QUOTABLE label.**
- Where: KNOWN_ISSUES.md:82 and REPORT.md:128–129.
- "total median 6.8298% → 6.8267%" is the universe+normalization block (`C_U`), not the quoted 6.871% total. On the quoted total, my figures are 6.8707% → 6.8674%.
- The KI 95 and 96 rows carry "NOT QUOTABLE". This row does not.
- Fix: relabel the figure as "C_U+norm median" and add the label.

**M6. The 20% reserve is computed against the subtotal, not the total.**
- Where: REPORT.md:342–344, 359–360.
- The record takes 20% of the subtotal, which is 16.7% of the total. The repository's own cost model (`state/uncertainty-preparation-20261008/c/costs.py:9,43,308`) defines the reserve as ≥20% **of the admitted total**, i.e. admitted = subtotal / 0.8.
- On that convention the pilot ceiling must be at least 14.75 node-h. The 14.5 ceiling holds an 18.6% reserve. Production becomes 49.8–81.8, not 47.8–78.5.
- Fix: either state the convention used and argue for it against plan §4 Stage C ("at least 20% reserved"), or raise the figures.

**M7. The pilot is requested before the recipe is final, and R0 depends on an unmerged delivery.**
- Where: REPORT.md:318–348, 270–274.
- Plan §4 Stage C says "After admitting the final recipe, run a small representative pilot". Here the pilot carries the Stage B diagnostics P4 and P5, which themselves need code patches.
- R0 and P2's lower bound rely on `--branch-select derived`. That option is absent from the driver at `45fd98f7` (the selective-I/O delivery is not merged).
- Fix: name this as a sequencing deviation for the director to accept, or split P4/P5 into a Stage B diagnostic grant. Also state the P2 price when the port is not merged: 5 × u_U = 3.3–3.8 node-h. That figure is already inside the stated upper bound.

### NOTE

- **N1. Citation errors.**
  - The PRD comment is at `unfold_2d_omnifold_unbinned.py:27`, not `:26`. The wrong line appears at REPORT.md:272 and in the committed STATUS correction (`2D_OMNIFOLD_STUDY_STATUS.md` ≈ :47).
  - The key gate is at `runEventLoopOmniFold.cpp:1203-1212`, not `:1134-1136` (REPORT.md:226). Lines 1134–1136 only compute `isSignalTruth`/`inPhaseSpace`.
  - `sim_pass` is assigned at `:1175`, not `:1176` (REPORT.md:167).
- **N2. The u_E label is wrong.** REPORT.md:329 says "2 CPUs". Array 55985231 ran with billing=10 / 10 CPUs. The charge, 0.077 node-h, is right only with billing 10.
- **N3. The KI 94 note attributes a prior measurement as new.** It presents the data-stream purity conditioning as "Also". It was recorded on 2026-10-06 (`ASSESSMENT-20261008-2d-estimator-pairing.md:86-87`; `state/ki84-adopt-20261006/purity_datastream_check.json`, purity median 0.975). The report body cites it; the KI row does not.
- **N4. R7 is sound, but its reasoning should be written down, and its precision is low.**
  - A fixed-seed bootstrap's variance already contains the bootstrap×seed interaction. So adding only the factorial's seed *main* effect as C08 is the correct random-effects decomposition, and adding the existing 10-seed scan would double-count the interaction. The record should say this.
  - The main effect from 5 seed triplets has 4 degrees of freedom (REPORT.md:261, 357).
- **N5. R2 is a decision for Joseph.** It lowers the diagnostic median by about 0.8 points and rests on MAT's FHC+RHC+IMD constraint. The paper's 4.01% exceeds it for an unexplained reason. The weighted covariance is MAT's convention and is statistically sound. "Not needed" (REPORT.md:306) is true for MAT-conformance but not for the comparison with the paper.
- **N6. The joint-law Stop passes by convention.** At REPORT.md:372–373 it passes because MAT's in-band convention is adopted as the joint law. Whether that reproduces the paper's flux×energy-scale correlation is explicitly unresolved.
- **N7. A missing NOT QUOTABLE label.** The `2D_VALIDATION_FOR_3D.md` correction (≈ :100–105) quotes 3.655% without the "NOT QUOTABLE" label used in the STATUS correction.
- **N8. Two source-table rows could be explicit.** No row says where data-POT counting uncertainty sits. C09 does not name the iteration-count/regularization dependence.
- **N9. MinosEfficiency has a small G2-class inconsistency.** It is a reco-side band, yet it modifies signal-tree truth weights (July `hTruth2D` ≠ CV; denominator equal; c−1 = 4.8e-4). Negligible, but the same class as G2.
- **N10. R3 applies a different authority principle from C04.** It drops a band that MAT's standard map registers, while C04 uses MAT-conformance as its authority. The record should state the principle once: physics intent over implementation.
- **N11. Two evidence arrays live only on `/pscratch`.** `sweeps.npz` and `adopted_cov.npz` (REPORT.md:382–384) back the exact `C_U` rebuild. Same durability risk the record flags for the active files.
- **N12. P1 declares no criterion.** It states no acceptance criterion or power (REPORT.md:336). The expected median data-stream change is about 3%, which only the paired design could resolve.
- **N13. Positive findings, in the record's favour.**
  - KI 91's numeric test used per-playlist omnifiles. I confirmed that the merged file's first 200,000 `mc_truth_denom` rows equal 1A's, including `Flux_5` and `Flux_77`.
  - The July laterals, GEANT, `NormDISCC`, `EtaNCEL` and `MaNCEL` truth inputs equal the July CV's bitwise. This is stronger KI-93 evidence than the record cites.
- **N14. The KI 95/96 rows match VERIFICATION.md.** Every number and the "unresolved" and "rough" qualifiers are faithful: 4.993→3.655, 4.893→3.557, 0.9565→1.0015, n_eff 19.1, the 5.2e-17 control, 1.1e-15, 1.0004186/0.9953532, 2.305→2.281, 0.113→0.367, 6.934/5.403, 6.090/4.216/4.230, and ±16%.

## Recomputed numbers (mine next to the record's)

| item | record | mine |
|---|---|---|
| KI 92 identity | 8 pairs byte-identical; differ from CV in 5.9–10.7% of rows | **Byte-identical** in a **3,000,000-row chunk** of `mc_signal_reco` (`w_truth`, `w_reco`) and of `mc_truth_denom`, and in **all 658,227** `mc_background` rows. Fraction differing from CV: 7.91% (signal chunk), 10.73% (denominator chunk), 5.89% (background). The only weight ratios present are 0.906977 and 1.093023, i.e. (0.43∓0.04)/0.43 |
| KI 92 σ, `C_U`+norm | ratio median 0.999908, min 0.99551; 6.8298% → 6.8267% | 0.999908 / 0.99551; 6.8298% → 6.8267% |
| KI 92 σ, quoted total | not given | 6.8707% → 6.8674%; ratio median 0.999909, min 0.99582; integral 5.39125% → 5.39124% |
| KI 92 on July | ratio median 0.999924 | 0.999924 (min 0.99742) |
| Covariance file | `62590df7` called "adopted" | its universe blocks equal the pinned `077912e3` (vl170) exactly |
| July CV vs `E_U` | ten inputs bitwise equal; 1.42e-11 | all **12** saved input histograms and all parameters bitwise equal; `hXSec2D` 1.4245e-11 |
| No-op universes | `NormDISCC_0/1` 9.5e-13 / 1.43e-11; `EtaNCEL` 3.0e-7, background ≤ 8.8e-6 | 9.53e-13 / 1.430e-11; `EtaNCEL_0` 3.03e-7, background 7.9e-6 on reported cells |
| July inputs | data equal 187/187; POT/target/flux equal in non-flux | 187/187; 87/87 non-flux equal; all 100 Flux universes use their own Φ_u |
| May KI 93 | all 87 non-flux truth inputs differ; `NormDISCC` 1.9% | 87/87 `hTruth2D` and `hOFInputTruth2D` differ; `NormDISCC_0` max 1.88%; `EtaNCEL_0` truth integral 0.8791. The May Flux files hold only `hXSec2D`, so their truth input cannot be checked |
| P06 | May background and training input = CV in 87/87; July varies in 185/187 | 87/87 and 87/87; July 185/187 (both `NormDISCC` endpoints equal) |
| C05a `BeamAngleY_1` | exits 1,422; entrants 1,072; background rows 658,243 (worker file) | 1,422; 1,072; 658,243 vs 658,227; 20,402,891 common rows with bitwise-equal kinematics and weights (all 32,849,103 rows read) |
| C05a `Muon_Energy_MINERvA_1` | support-identical | 0 exits, 0 entrants; 20,406,963/20,406,963 kinematics and weights bitwise equal; background 658,227 both |
| KI 94 (July CV, 205 bins) | eB/√D median 0.072, >0.1 in 60; purity median 0.975, min 0.536 at (0,0) with D = 919, B = 426.7; understatement median 1.029, >1.25 in 6, max 1.95; template-only 0.26% / 4.5%; 1/p max 1.87 | 0.07217 (p84 0.1247, max 0.3024), 60; 0.97456, 0.53573 at (0,0) with 919 / 426.667; 1.02855, 6, 1.9501; 0.260% / 4.47%; 1.8666 |
| KI 94 code path | purity before the Poisson multipliers | **Correct.** `build_measured_training_2d` at `:1475` is applied to unresampled data; `measured_weights *= b_data` follows at `:1654`; `hMeasTrain2D` = p·D to 2.6e-12. For the binned purity estimator, the formula √(1+(eB/√D)²)/p is correct |
| G2 mechanism | miss rows carry the CV truth weight | **Confirmed** in code (`runEventLoopOmniFold.cpp:861-862`) and in data: 681,613 of the first 3M signal rows carry the CV weight in `Flux_3`, `Flux_50` and `MaRES_0`, and all but one of them have `sim_pass`=0 with `w_reco`=`w_truth`; in the denominator, 2 of 3M rows match CV |
| G2 completeness | Flux 18%, MaRES 10%, MvRES/MaCCQE 5%, ~1e-14 otherwise; MINOS denominator −0.96% | 18.23%, 10.47%, 5.24% / 4.81%, 1.6e-14; MINOS_0 denominator 0.99037. **`MaRES_0` rebuilt from the omnifile:** max 6.763%, equal to the product to 3.5e-14; denominator ratio 0.935543, also equal |
| C04 on July (new) | not measured | unweighted 5.158% → weighted **3.747%**; integral 5.045% → 3.640%. May reproduces 4.993 → 3.655 and 4.893 → 3.557, with mean/CV 0.9565 → 1.0015. Σw 211.012; n_eff 19.06 |
| Unit costs | u_CV 0.058–0.066; u_U 0.65–0.76; u_sel ≈ 0.25; u_E ≈ 0.077 at "2 CPUs"; XR 3.09 | 0.0581 / 0.0631 / 0.0658; 0.654–0.761; 0.247; u_E is billing **10**, long-job median 0.0756, max 0.192; XR 3.091 |
| Pilot and production arithmetic | 7.4–11.8; total 8.9–14.2; ceiling 14.5; production 47.8–78.5 | sums reproduce (7.42–11.73); see M6 for the reserve convention |
| Compute claim | 0 node-h | `sacct` shows 0 jobs named `2dc*` since 10-11; the probe returned 5 rows, so it could see jobs |

**Citations spot-checked (17):**
- Correct: `unfold…:248`, `:338`, `:1475`, `:1654`, `:1678`, `:1379-1388`; `analyze_universes.py:258-259`, `:274-280`; `build_flux_universe_band.py:59-75,99-103`; pairing assessment `:86-87`; `runEventLoopOmniFold.cpp:1191`, `:1447`, `:1454-1456`, `:1698,1701`, `:1712`, `:794-905`; MAT `FluxSystematics.cxx:24-31`, `GenieSystematics.cxx:241-257`, `:658-671`, `MuonSystematics.cxx:202`, `GetFluxIntegral.cpp:25-29`.
- Wrong: `:26` (→ :27), `:1134-1136` (→ :1203-1212), `:1176` (→ :1175). See N1.

**Hygiene:**
- `generate_manifest.py --check --at-sha 45fd98f7`: OK, exit 0. Its `unused_overrides=1` already exists at `46c410ae`.
- `verify_hash_bindings.py`: ALL BINDINGS INTACT, exit 0.
- `verify_receipt_artifacts.py --rev 45fd98f7`: exit 0. 14 artifacts, 0 missing. 66 UNRESOLVED, which is the unchanged pinned inventory.
- Evidence checksums:
  - `SHA256SUMS.local`: 6/6 OK.
  - `SHA256SUMS.nersc`: 52/52 present files OK.
  - Both `.json.gz` files match when decompressed.
  - Six cluster files re-measured, including both `.npz`: all match.

## Scratch paths
- Cluster: `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/review-b/`. Scripts: `rb_products.py`, `rb_omni.py`, `rb_follow.py`, `rb_jtruth.py`, `rb_ki91merge.py`. Outputs: matching `.json` and `.log` files, plus `rb_omni_g2_c.npy`.
- Local: `/private/tmp/claude-501/review-b-scratch/`. Holds the same scripts, `rb_products.json`, `sacct_55985231.psv`, `cluster_sums.txt`, `hash.out` and `receipt.out`.

## Worktree status
- `/private/tmp/claude-501/review-b-45fd98f7` (detached `45fd98f7`): `git status --short` empty at start and at end. **Removed.**
- Main checkout: unchanged from session start (the same 3 modified orchestration files and the same untracked files).
- Cluster checkout `32e403b8`: unchanged.
- Nothing was edited, committed or pushed.