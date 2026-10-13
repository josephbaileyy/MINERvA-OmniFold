# 2D closeout Stage B: input and recipe assessment, source table and priced Stage C pilot

**CITABLE FOR:**
- the Stage B saved-product and code-path reads of
  [`PLAN-20261011-2d-closeout.md`](../../../PLAN-20261011-2d-closeout.md) §4: KI 91, KI 92, KI 93, P06/C06,
  C05a, X01, KI 94/C03 and the role of `C_ML`, plus the C04 flux finding;
- the independently verified defects recorded as `KNOWN_ISSUES.md` rows 95 (C04) and 96 (X01);
- the C01–C10 / X01–X03 source table, the proposed uncertainty recipe, the missing inputs and their
  acquisition routes;
- the priced Stage C pilot request.

**NOT CITABLE FOR:**
- any quotable uncertainty, covariance or budget. Every budget figure here is **DIAGNOSTIC, NOT QUOTABLE**;
  the quoted 2D uncertainty is unchanged;
- adoption of the recipe, of a repaired covariance or of any estimator-contract change: those are Joseph's
  (plan §6; delegation §4);
- coverage, calibration or a KI-85 lift;
- Stage C compute authority. The pilot request below is a request; Stage C needs its own committed grant.

| field | content |
|---|---|
| `Owner` | 2D closeout executor (2d closer), directed by the paper-tighten lane under [`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../AUTHORIZATION-20261012-2d-closeout-delegation.md) |
| `Grant` | [`AUTHORIZATION-20261012-2d-closeout-stageAB.md`](../../../AUTHORIZATION-20261012-2d-closeout-stageAB.md) (sha256 `917d8d80…`, verified on `origin/main` before any cluster work) |
| `Deliverable` | B of the director's 2026-10-12 assignment |
| `Branch` / `Base` | `closeout/stage-b-20261012` / `origin/main` `46c410ae` (PR #94). Reads were made at `7edb65fa`; every cited code path is byte-identical between the two |
| `Decision` | Is every material source assigned, are its inputs feasible, and is there a reviewable final recipe with a priced pilot (plan §4 Stage B exit)? |
| `Terminal outcomes` | EXIT MET; EXIT CONDITIONAL (named open items resolved by a priced pilot); STOP (missing selection support, joint-law evidence or required populations) |
| `Reviewer` | §10: review PASS WITH CHANGES (0 MATERIAL), repaired |
| `Compute` | Login-node reads on saul (`login05`) and local analysis only. **No Slurm job under the Stage A/B grant: 0 of 2.0 charged node-h used.** Writes only under `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/` |
| `Workers / reviewers` | Four read-only worker forks of this session (flux; GENIE/truth; background/ML; laterals/sources), one independent C04/X01 verifier, one Stage B reviewer (§10). All Claude Opus 5.5 |

`E` = [`evidence/`](evidence/) (copies of every script and output named here; `SHA256SUMS.nersc` re-measured
on the cluster and checked after the copy). Code citations are `file:line` at `7edb65fa` unless stated.
`Q` = `docs/orchestration/state/next-preparation-20261009`.

## 1. Answer

**EXIT CONDITIONAL.** Every C01–C10 / X01–X03 source is assigned an input, a law and a propagation (§3), and a
complete recipe is proposed for review (§4). One further source is **not** assigned: data-POT counting (C07′), a
materiality decision for Joseph (§3, §5, R10). The inputs exist, with two exceptions that are named, routed and
priced (§5). No Stop condition is met (§8).

The reads found more than the plan anticipated:

| item | finding | verification | record |
|---|---|---|---|
| **C04 flux** (new) | **DEFECT.** The quoted flux band ignores MAT's ν-e+IMD universe weights: per-cell median 4.993% → 3.655% weighted; integral 4.893% → 3.557% | **independently verified** | KI 95 |
| **X01** | **DEFECT.** `Muon_Energy_MINOS` universes divide by Φ_CV; their event weights carry the correlated flux. The adopted total has no cross block, and none should be added | **independently verified** | KI 96 |
| KI 91 flux index | **Identity established** by a code chain and an exact numeric test with a powered control | worker; Stage B review | KI 91 note |
| KI 92 Rvn1pi/Rvp1pi | **Confirmed** in all four weight families; effect negligible (median σ ratio 0.99991) | worker; Stage B review | KI 92 note |
| KI 93 truth inputs | May sweep: **all 87** non-flux universes affected, broader than recorded. July `purity_newomni` sweep **passes** the KI-93 bar **provisionally** (pending P2; producer revision uncommitted) | worker; Stage B review | KI 93 note |
| P06/C06 background | **Confirmed**: May background frozen at CV in 87/87 non-flux universes (re-measured twice). July varies it in 185/187 | two workers | KI 93 note |
| KI 94/C03 | **Confirmed**: no background-template fluctuation is propagated. Also, the bootstrap's data stream holds purity fixed, scaling σ by p (understated by up to 1/p = 1.87) | worker; Stage B review | KI 94 note |
| C05a laterals | Six muon-scale/resolution universes **qualified** (event-level identity with active-mode files). The four **beam-angle** universes are **not** (up to 1,465 wrong exits / 1,344 missing entrants each) | worker; Stage B review | §2.7 |
| G1 gap class | ~~**Candidate.** Reco-in/truth-out events land in neither omnifile tree (≈1.8% of reco entries per a code comment). **If confirmed, it biases the adopted central value**, not only the uncertainty~~ **Corrected 2026-10-13: NOT A DEFECT.** P4 census MEASURED nG1 = 0 over all 12 playlists; the class is empty in the production CV configuration and `E_U` is not implicated | P4 census, [`diagnostics/REPORT.md`](diagnostics/REPORT.md) §2 | §2.10 |
| G2 miss-row stand-in | **Candidate.** Dump-mode truth-only miss rows carry the CV truth weight in every universe; completeness then deviates from 1 by up to 18% (Flux) and the driver divides by it. **Corrected 2026-10-13: NOT RESOLVED ABOVE TRAINER NOISE** (P5, `MaRES_0`, seeds 42 and 43: shift median 0.31–0.41 σ_band but 0.96–1.23 σ_ML, seed-to-seed z correlation 0.11, NOT CONFIRMED). No repair triggered by the pre-declared rule; a repair, if chosen, is re-unfolds only | P5, [`diagnostics/REPORT.md`](diagnostics/REPORT.md) §3 | §2.11 |

**Why CONDITIONAL, not MET.** G1 could be an unmodelled, unsubtracted background at the percent level, which
would bias the adopted central value `E_U` itself, and G2 could bias every truth-weight-varying universe. The July
products also ran on an uncommitted driver revision (§2.5), so their qualification is provisional until the pilot's
P2 bridge. Neither can be settled from saved products. Each has a diagnostic in the
Stage C pilot request (§7). If either is confirmed as material, the recipe gains a repair before production.
**Update 2026-10-13:** neither was confirmed as material. G1 = 0 (not a defect) and G2 is NOT RESOLVED ABOVE
TRAINER NOISE in `MaRES_0` ([`diagnostics/REPORT.md`](diagnostics/REPORT.md)). The P2 bridge is still open. This
REPORT's terminal outcome is unchanged here; any re-grading is the director's.

**Diagnostic budget (NOT QUOTABLE)**, from the independent verification's per-cell recomputation (205 cells):
adopted 6.871% median / 5.391% integral; with the C04 repair 6.090% / 4.216%; with C04 and X01 6.090% / 4.230%.
The other repairs (seed-42 statistics with three streams, KI 92, the July block, beam-angle laterals) are not
yet in that number. Under R1 the flux block comes from the July sweep, where the reviewer measured the same effect:
5.158% → 3.747% per-cell median, 5.045% → 3.640% integral (NOT QUOTABLE).

## 2. The reads, issue by issue

### 2.1 KI 91, flux-universe index identity: IDENTITY ESTABLISHED

- **Code chain** (MAT `35097b65`, MAT-MINERvA `50d76314`; cluster paths under
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/`):
  1. both event loops set `SetNuEConstraint(true)` and `SetNFluxUniverses(100)`
     (`runEventLoopOmniFold.cpp:1698,1701`; `runEventLoop.cpp:348,351`);
  2. `GetFluxSystematicsMap` pushes `FluxUniverse(chain, 1, i)` for i = 0..99 in order (`MAT/PlotUtils/FluxSystematics.cxx:24-31`);
  3. the omnifile names branch `w_<prefix>_Flux_<idx>` after the vector position (`runEventLoopOmniFold.cpp:328-350`)
     and fills it with `model.GetWeight(*u)` (`:1226-1247`, `:1481-1485`). The reviewer confirmed that the merged
     file's first 200,000 `mc_truth_denom` rows equal playlist 1A's, including `Flux_5` and `Flux_77`, so the
     per-playlist test carries to the merged omnifile;
  4. the event weight is CV × `FRW.GetFluxErrorWeight(Enu, pdg, u)` (`Model.h:53-66`; `FluxSystematics.cxx:65-79`;
     `FluxReweighter.cxx:1691-1716`);
  5. the flux integral's universe u is ∫ hist(u) of the same `m_fluxReweightNu` object (`util/GetFluxIntegral.cpp:25-29`;
     `FluxReweighter.cxx:1321-1351`);
  6. `build_flux_universe_band.py:59-75,99-103` puts universe u in column u+1 of `hFluxUniv`, which the driver reads
     for `--universe Flux:u` (`unfold_2d_omnifold_unbinned.py:145-196,1373-1386`).
- **Numeric test** (`E/b-flux/ki91_identity.py`; three playlists, one per flux group): saved per-playlist universe
  integrals equal FRW's ∫hist(u) exactly; for 900 events, all 100 weight ratios match FRW universe u at the solved
  Eν (max residual 5.5e-14, 0 unsolved). **Control:** shifting the columns by one gives a minimum residual of 0.245,
  so the test has power. The reco and truth weight ratios agree to 4.4e-16.
- This supersedes the "Pearson 0.96" docstring evidence that lane C's Audit 2 found insufficient.

### 2.2 C04, the flux constraint weights: DEFECT, independently verified (KI 95)

Verified by a fresh reviewer with its own code
([`verify-c04-x01/VERIFICATION.md`](verify-c04-x01/VERIFICATION.md), preserved verbatim). In summary:
- MAT applies the ν-e+IMD constraint as per-universe weights on the Flux band (`MnvFluxConstraint.h`
  `CorrectFluxUniv` only calls `SetUnivWgt`) and corrects the CV (`CorrectCV`). `CalcCovMx` is the weighted
  covariance, and `HistWrapper.cxx:305-320` carries the weights onto every event histogram in a standard MAT
  analysis. Our rollup (`2d-unfolding/uq/analyze_universes.py:258-259`) is unweighted and mean-centred.
- The weights equal the constraint file's first 100 Flux entries; Σw = 211; **n_eff = 19.1**.
- Recomputed: flux median **4.993% → 3.655%**; integral **4.893% → 3.557%**; universe mean/CV 0.9565 → 1.0015.
  Control: the adopted universe total to 5.2e-17, and the quoted total median exactly 6.871%.
- The "MAT-conformant, byte-for-byte" check (`uq/verify_matcorr_vs_mnvh1d.py`, `b480c261`) never calls
  `SetUnivWgts` and ran on the pre-flux-fix sweep, so it could not have caught this.
- The published flux block (median 4.014%, integral 4.002%) is consistent with a constrained flux, not with 4.99%.
  Why it exceeds our weighted 3.655% is unresolved (the FHC-only-constraint inference is not established).
- **Repair:** weighted `CalcCovMx` over existing universe outputs. **No re-unfold.** The diagnostic numbers above
  use the adopted (May) sweep; the construction uses the July sweep (R1), where the effect is 5.158% → 3.747%.
- **Decision for Joseph (review N5):** the weighted covariance is MAT's convention and statistically sound, and it
  lowers the diagnostic median by about 0.8 points. It rests on MAT's FHC+RHC+IMD constraint, while the published
  flux block (4.01%) is larger for an unexplained reason.

### 2.3 X01, flux × muon energy: DEFECT, independently verified (KI 96)

- The driver swaps Φ only for `Flux` (`unfold_2d_omnifold_unbinned.py:1373-1389`). The MINOS event weights carry
  `GetSysUniFluxWeightCorrection` (`MuonSystematics.cxx:202`), whose matching flux-integral universes MAT builds under
  `use_muon_correlations` (`FluxReweighter.cxx:1360-1398`). Φ_MINOS,u/Φ_CV = 1.0004186 and 0.9953532.
- MINOS per-cell median 2.305% → 2.281%; MINOS integral σ 0.113% → 0.367%.
- The flux the analysis uses inherits the ν-e+IMD constraint in its CV (and in its spread once KI 95 is repaired).
  The low-recoil information enters MAT only through the MINOS universes' correlated flux, which the omnifile
  already carries in the numerator.
- The adopted 6.87% contains **no** flux×muon-energy cross block (it equals the sum of its blocks;
  `rederive_flux_muonE_cross.py` reads only the pre-fix product). The paper-derived ρ = 0.900 block must **not**
  be added on top of the X01 repair: it would double-count. Whether the paper's cross block equals MAT's in-band
  correlation cannot be settled from the data release (missing input: the paper's per-band construction).
- **Repair:** rescale the two MINOS outputs by Φ_CV/Φ_MINOS,u. Exact; no re-unfold.

### 2.4 KI 92, one GENIE shift counted twice: CONFIRMED, negligible

- In the current universe omnifile (sha256 `220c479e…`, 171,117,087,867 B), all eight Rvn1pi/Rvp1pi column pairs are
  byte-identical across the four weight families the driver reads (`w_truth`/`w_reco` in `mc_signal_reco`, `w_truth`
  in `mc_truth_denom`, `w_bkg`), while each differs from CV in 5.9–10.7% of rows (`E/b-genie-truth/rv_columns.json`).
- Cause: MAT's `GenieRvx1piUniverse::GetGenieWeight` gives non-resonant-pion events the same constant
  (0.43 ± 0.04) in both bands, and the standard map registers both (`GenieSystematics.cxx:241-257,353-372,658-671`).
- **Rebuild:** the adopted `C_U` (`62590df7…`) was rebuilt exactly from the saved May vectors (max relative
  difference 0.0). Dropping Rvp1pi: per-cell σ ratio median 0.999908 (min 0.99551); total median 6.8298% →
  6.8267%; integral unchanged at 5.3909%. On the July sweep: median 0.999924.
- The 6.8298% → 6.8267% figures are the `C_U`+normalization median. On the quoted total, the reviewer measured
  6.8707% → 6.8674% (NOT QUOTABLE).
- **Repair:** a rollup rule (Rvx1pi counted once). No compute.
- **Side finding:** `NormDISCC` is null at the weight level (all eight columns byte-identical to CV; its July
  universes reproduce CV to ≤ 1.43e-11). Why the knob is null in this MC is not established (§5, G3).

### 2.5 KI 93, May vs July truth inputs: May RETIRED, July QUALIFIED PROVISIONALLY (pending the P2 bridge; producer revision uncommitted)

- **May sweep (`universe_sweep_fluxfix`):** all 87 non-flux universes have `hTruth2D` and `hOFInputTruth2D` that
  differ from `E_U`'s, including universes whose truth must equal CV (laterals; the null `NormDISCC`, which sits
  1.9% from CV in May against 1.4e-11 in July). Their data, background and training inputs equal CV (P06).
  The May file and code revision are unavailable. **Retire the May sweep** from the new construction.
- **July `purity_newomni` sweep, 187 universes + CV `b8457af7…`:** passes the KI-93 bar.
  - The CV has all ten saved inputs bitwise equal to `E_U`'s and reproduces `E_U` to 1.42e-11.
  - `hDataReco2D` equals CV in 187/187; POT, target count and flux parameters equal in every non-flux universe.
  - No-op universes reproduce CV: `NormDISCC_0/1` to 9.5e-13 / 1.43e-11 (inside the frozen 1e-8);
    `EtaNCEL` (background change ≤ 8.8e-6 only) to 3.0e-7.
  - Execution: the 188 job logs record seeds 42/43/44, `lgbm`, `bkg-mode=purity`, `OMP_NUM_THREADS=128` and the
    omnifile path; every log completion matches its product mtime within 120 s.
  - **Limit:** the products record no driver or input digest. Their tie to omnifile `220c479e` rests on mtimes.
  - **Producer revision uncommitted (review M4).** The July products (CV mtime 2026-07-08 18:48 UTC) predate
    `cf8a4a67` (2026-07-11), the first commit containing `_universe_bkg_branch`, yet their backgrounds vary per
    universe. So the July sweep ran on driver code that was never committed at that state.
  - **Consequence.** The qualification is **provisional**. Pilot P2 re-runs July universes with the frozen,
    committed producer and must reproduce them within a frozen envelope (no-op universes to the frozen 1e-8; others
    to an envelope declared before P2 runs). If P2 fails, the July block is rebuilt (187 × u_U,sel…u_U = 47–142
    node-h; §7 contingency).
  - The reviewer also found the July laterals', GEANT, `NormDISCC`, `EtaNCEL` and `MaNCEL` truth inputs bitwise
    equal to the July CV's.
- The July `negweight` sweep is **not** matched to `E_U` (its CV differs by up to 12%).
- Pricing operand: July universe unfolds took 2,355–2,738 s (median 2,530 s) on one regular node.

### 2.6 P06/C06, background-model variation: CONFIRMED frozen in May; July is background-aware

- The current driver re-derives background, purity and training weights per universe (`fill_bkg_reco_2d`,
  `unfold_2d_omnifold_unbinned.py:248` ff.; `hMeasSub2D = D − B` at `:1472-1474`; `build_measured_training_2d`
  `:338`, called at `:1475`), since `cf8a4a67` (2026-07-11, KI #13), after the May sweep was made.
- May: `hBkgReco2D` and `hMeasTrain2D` are bitwise CV in **87/87** non-flux universes (both the background and the
  GENIE/truth workers re-measured this independently). July: background differs from CV in **185/187** (only the
  null `NormDISCC_0/1` equal).
- Reco-level size of the missing variation in May (all non-flux bands in quadrature): σ_B/√D median 0.24, max 1.95.
  The unfolded-level size cannot be separated from KI 93 and trainer noise; the July block supplies the construction.

### 2.7 C05a, selection-limited lateral bands: six QUALIFIED, four beam-angle NOT

- **What dump mode keeps** (`runEventLoopOmniFold.cpp`, last changed `486e53e6`): every signal event in the truth
  phase space, whatever its reco result (`:1182-1216`), with shifted kinematics per lateral universe
  (`:1237-1250`); the stored pass flag is the **CV** selection (`:1152,1176`); the background tree is CV-selected
  (`:1447`). (`sim_pass` is assigned at `:1175`.) The driver re-applies only the reco window to shifted kinematics (`unfold_2d_omnifold_unbinned.py:705,731-742`).
  The muon enters the cuts only through `MaxMuonAngle(20°)` (`:1710-1715`), which energy-scale and resolution
  shifts do not change and beam-angle shifts do.
- **Event-level comparison** of the July dump omnifile with the 5D standard-mode active-universe merged files
  (`nd-unfolding/active_universe_5d/standard/merged/*_active_<u>.root`), all 32,849,103 rows
  (`E/b-lateral/dump_vs_active.py`, `cmp_<u>.json`):
  - rows align (truth identical row by row in all 10 universes);
  - **MuonResolution, Muon_Energy_MINERvA, Muon_Energy_MINOS (both endpoints): support-identical.** In-window pass
    sets identical, shifted kinematics and weights bitwise equal, background identical; the committed census
    (`p4_merged_audit.json` @ `0f1b7b8d`) shows 0 entrants and 0 exits;
  - **BeamAngleX/Y (both endpoints): not qualified.** 1,126–1,465 exits wrongly kept and 1,003–1,344 entrants
    missing per universe; reco-level cell errors up to 5.0–10.7% of CV content, up to 35× the band's own reco-level
    shift in θ = 20° edge cells; background rows 657,905–658,652 against 658,227. The bands are small (0.10–0.15%
    median, max ≈ 1%), and the unfolded-level effect is not measured.
- **CV equivalence:** the sha256 of all 17 CV columns and the 3 data columns are equal between the 2D CV omnifile
  (`E_U`/L0 input) and the July dump file (`E/b-lateral/cv_digest.json`). Signal/denominator closure holds for active
  `Muon_Energy_MINOS_0` (26,947,895.641046 both sides); the other nine closures are not yet read.
- **Repair (recipe R4):** unfold all 10 lateral universes from the existing active merged files. **No new event
  loop.** Durability risk: those files (≈ 538 GB) exist only on `/pscratch` (Jul 17–18); they need a CFS copy
  before Stage C relies on them.

### 2.8 KI 94/C03, background-template statistics: CONFIRMED missing; recipe specified

- No background-template fluctuation is propagated ("intentionally NOT bootstrapped",
  `unfold_2d_omnifold_unbinned.py:1671-1679`); the MC stream multiplies signal rows only.
- **Data-stream conditioning.** Purity weights are computed from the un-resampled data (`:1475`) and the Poisson
  multipliers applied afterwards (`:1651-1654`), so a bin's target is p·D* rather than D* − B and its variance p²D.
  This is recorded as conditioning (`ASSESSMENT-20261008-2d-estimator-pairing.md:86-87`), but its size is material
  where purity is low.
- **Numbers** (July CV, 205 reco bins; `E/b-bkg-ml/bkg_pn.json`): eB/√D median 0.072, > 0.1 in 60 bins (reproduces
  A4 item 5); purity median 0.975, min 0.536 (reco bin (0,0): D = 919, B = 426.7); data-stream σ understatement
  √(1+(eB/√D)²)/p median 1.029, > 1.25 in 6 bins, max 1.95. Template statistics alone add median 0.26%, max 4.5%;
  un-freezing purity dominates (1/p up to 1.87).
- **Event sharing** (`runEventLoopOmniFold.cpp:1186-1212,1454-1456`; the truth-key gate at `:1203-1212`): reco-passing rows of `mc_signal_reco`
  and `mc_background` are disjoint. A truth-in/reco-out event can sit in `mc_background` and also as a miss row in
  `mc_signal_reco` (unmeasured, "shared class"); reco-in/truth-out events are in neither tree (G1).
- **Recipe:** R5 (§4).

### 2.9 The role of `C_ML`

Three distinct objects, measured to different extents:

| object | value | source |
|---|---|---|
| fixed-seed reproducibility | 1.4e-11 (`E_U` vs L0) | Stage A §3.8 |
| seed arbitrariness | seeds 1–10 differ from `E_U` in all 205 cells, median 1.6e-3 to 2.3e-3; σ_ML/σ_S median 0.26, max 0.73 | seedscan products; `uq/seedscan_lgbm_ml/uq_covariance_ml.root` |
| sampling × seed, nuisance × seed | **unmeasured** | — |

- The VL170 replicas pin seeds 1/2/3 and so contain input-perturbation trainer instability but no seed scatter;
  universe unfolds pin 42/43/44. A4 item 3: `NormNCRES` moves the training input by 6.3e-5 and the output by up to
  1.47%, so instability and seed effects are not separable without a factorial design.
- `uq/boot_data` and `uq/boot_mc` (200 each, 2026-06-14) predate provenance (seeds unrecorded): development
  references only.
- **Design property:** the trainer is deterministic at a fixed seed (1.4e-11), so an unreplicated two-way layout
  identifies both main effects and the interaction as the residual. Recipe R7 (§4) and production item S4 (§7).

### 2.10 G1, the reco-in/truth-out gap class: CANDIDATE, missing input

**Correction 2026-10-13: resolved, NOT A DEFECT.** Pilot P4 (a reviewed census patch over all 12 playlists,
489 MC files) measured **nG1 = 0** and wG1 = 0: every skipped reco-tree signal-in-phase-space background entry
(20,498,013) has its key in the reco signal tree, and no signal-loop event lacks a truth-tree record. The no-op
control is IDENTICAL and all 12 outputs are IDENTICAL to the May production files on common branches, so the
census ran on `E_U`'s own input. The "~1.8%" comment below does not describe the shipped configuration. The text
below is the original candidate statement. See [`diagnostics/REPORT.md`](diagnostics/REPORT.md) §2.

- `mc_signal_reco` keeps an event only if its key is in the truth-tree set (`runEventLoopOmniFold.cpp:1203-1212`);
  `mc_background` skips reco-tree signal-in-phase-space events (`:1454-1456`). An event that is signal in phase
  space on the reco tree but out of it on the truth tree is therefore in **neither** tree. The code comment puts
  this at "~1.8% of reco entries" (`:1191`, measured at Phase 18). How many pass the reco selection, and whether
  they should be subtracted as background (fakes by the truth-tree definition), is not recorded.
- `mc_background` has no event IDs, so the class cannot be measured from saved products. **Missing input**; route
  and price in §5 and §7 (P4).
- **Consequence if confirmed (review M1).** These events are neither modelled nor subtracted, so a confirmed G1
  changes the adopted central value (`E_U`, DECISION-20261011), not only an uncertainty term, and needs Joseph's
  re-adoption. The repair would most likely need new event-loop omnifiles (the CV, the 187-universe dump and the
  active files) and re-unfolding the central value and every block. Priced in §7 as a contingency.

### 2.11 G2, miss rows carry the CV truth weight: CANDIDATE

**Correction 2026-10-13: NOT RESOLVED ABOVE TRAINER NOISE.** Pilot P5 unfolded `MaRES_0` with the miss rows
carrying their own universe truth weights (from `mc_truth_denom`) against the production stand-in, at seeds 42
and 43. Both pairs pass every gate. The shift is large against the band (median r1 0.305 and 0.411) but not
resolved above LightGBM seed noise (median r3 0.96 and 1.23 ≤ 2), it does not repeat across seeds (Pearson
z43 vs z42 = 0.113 < 0.5, NOT CONFIRMED), and it does not track the completeness deviation. Final routing under
the rules frozen before data: NOT RESOLVED ABOVE TRAINER NOISE. Flux universes are unmeasured. The correct
universe weights are already in `mc_truth_denom`, so any G2 repair is re-unfolds only. The text below is the
original candidate statement. See [`diagnostics/REPORT.md`](diagnostics/REPORT.md) §3.

- In dump mode, appended truth-only miss rows carry the CV truth weight as a stand-in for every universe weight
  (`runEventLoopOmniFold.cpp:794-905`); the comment calls this "exact for detector bands (truth untouched)".
- That is not true for any universe whose truth weights vary, including `Muon_Energy_MINOS` (its denominator sum
  falls 0.96%; the X01 correlated-flux weight is truth-Eν based). The July completeness `hOFCompleteness2D` then
  deviates from 1 by up to 18% (Flux), 10% (MaRES), 5% (MvRES, MaCCQE), and ≈ 1e-14 where truth weights do not
  vary (`E/b-lateral/completeness_scan.json.gz`). The driver divides each cell by c.
- Whether the per-cell division reproduces a correctly weighted unfold depends on how the OmniFold weights vary
  within a cell, so it is an approximation of unknown size, not yet shown to be a defect. Active-mode files give
  c = 1 by construction (laterals only). Diagnostic: §7 P5.
- The reviewer confirmed the mechanism in code (`runEventLoopOmniFold.cpp:861-862`) and data (681,613 of the first 3M
  signal rows carry the CV weight in `Flux_3`, `Flux_50` and `MaRES_0`), and rebuilt `MaRES_0`'s completeness from
  the omnifile (max 6.763%, equal to the product to 3.5e-14).
- `MinosEfficiency`, a reco-side band, also modifies signal-tree truth weights (c − 1 = 4.8e-4): negligible, but
  the same class (review N9).

## 3. Source table (C01–C10, X01–X03), updated for KI 92–96

Status vocabulary: **ELIGIBLE** (inputs exist and pass their checks), **REPAIR** (inputs exist; a specified
change is needed), **MISSING** (an input does not exist; route in §5), **OPEN QUESTION** (whether the source needs
a band at all is a decision; route in §5).

| id | source | input | law | conditioning | propagation | correlation partners | independent evidence | status |
|---|---|---|---|---|---|---|---|---|
| C01 | data statistics | data rows of the CV omnifile (`43f8cc16`, the frozen producer's input) | Poisson(1) per data event | MC and nuisances fixed | re-unfold each replica at seed 42 with purity recomputed from D\*, B\* (R5) | C02, C03 (via purity), C08 (X02) | coverage not yet tested (KI 85, Stage D) | REPAIR: seed 42 (P07); purity conditioning (§2.8) |
| C02 | signal-MC statistics | `mc_signal_reco` rows, with completeness from unresampled truth (KI 84) | Poisson(1) per signal row (`rng` offset 10⁷) | data fixed in its arm | same replicas | C01, C03 (shared class), C08 | — | REPAIR: seed 42 |
| C03 | background-template statistics | `mc_background` rows (658,227) with `w_bkg` | Poisson(1) per row (`rng` offset 2×10⁷); shared draw with a signal-tree miss row if G1/shared-class reads show overlap | data and signal fixed in the bkg-only arm | refill B\* → purity → training weights → unfold, inside the same replicas | C01 (purity), C02 (shared class), C06 (reuse draws across universes in any universe × bootstrap work) | unit check: bkg-only stream reproduces Σw² of B at reco level; b ≡ 1 reproduces the central | REPAIR: new stream (KI 94) |
| C04 | flux | 100 PPFX universes of the July sweep; Φ_u from `flux_integral_universes_MEFHC.root` (`5eecae84`) | constrained multi-universe: MAT constraint weights (n_eff 19.1) | data fixed | weighted `CalcCovMx` about the weighted mean | X01 (in-band only), C07 | KI 91 identity (§2.1); MAT `CalcCovMx` on the saved MnvH1D (3.53% integral) | REPAIR: weights (KI 95); G2 |
| C05a | lateral bands (10 universes) | active-mode merged files (beam angle required; muon scale/resolution for one construction mode) | MAT ±1σ pairs | data fixed | re-unfold from the active files; mean-centred 1/N | C04 (X01), C05b, C08 (X03) | event-level dump-vs-active census (§2.7) | REPAIR: beam angle; MINOS also needs the X01 denominator |
| C05b | weight-only detector bands (MinosEfficiency, GEANT ×3; 8 universes) | July sweep | MAT ±1σ pairs | data fixed | mean-centred 1/N | C05a, C08 | July qualification (§2.5); c = 1 (GEANT), c−1 = 4.8e-4 (MinosEfficiency) | ELIGIBLE |
| C06 | interaction model (GENIE, FSI, 2p2h, RPA; background-aware) | July sweep, Rvx1pi once, `NormDISCC` null | MAT ±1σ pairs (2p2h: 3) | data fixed | background-aware per universe (current driver); mean-centred 1/N | C03, C08 (X03), C09 | July qualification; KI 92 rebuild; P06 census | REPAIR: KI 92 rule; G2 |
| C07 | target normalization | 1.4% rank-1, scaled to the adopted central | fully correlated scale | none | one site (`uq/analyze_universes.py:274-280` via `--add-norm`) | C04 | lane C Audit 1 (counted once) | ELIGIBLE |
| (C07′) | data POT counting | the POT normalization of data (1.057394e21) | — | — | **not assigned a separate band**: no POT-counting uncertainty is in the adopted or the proposed construction; the analysis note's paraphrase of Ruterbories §V (`docs/analysis-note/app_statmethods.tex:330-338`) names only the 1.4% target count; the paper itself was not read here, and absence from a paraphrase is weak evidence. Flagged for Joseph (review N8) | C07 | — | OPEN QUESTION |
| C08 | estimator variability | factorial panel (S4) | seed main effect at the adopted estimator | data and MC fixed | sample covariance over seed triplets | X02, X03 | panel interaction terms | REPAIR: measure (R7) |
| C09 | unfolding-model dependence, including the iteration count (5) and regularization | development closures only | signed allowance B−/B+ | fixed response | separate allowance, not added in quadrature by default | C06 | — | MISSING (Stage D: independent-generator 2D truths) |
| C10 | response departures | none outside the parametrized family | stated assumption | — | — | — | — | MISSING (Stage D) |
| X01 | flux × muon energy | MINOS universes' in-band correlated flux | MAT in-band correlation | — | MINOS ÷ Φ_MINOS,u; no separate cross block | C04, C05a | MAT code path (§2.3) | REPAIR (KI 96) |
| X02 | bootstrap × seed | factorial panel part (i) | interaction | — | reported, not subtracted | C01, C02, C08 | panel | REPAIR: measure |
| X03 | universes × retraining | factorial panel part (ii) | interaction | — | reported, not subtracted | C04–C06, C08 | panel | REPAIR: measure |

## 4. Proposed recipe (for review; adoption is Joseph's)

- **R0 Producer.** L0's frozen central-value procedure (Stage A §1): LightGBM, seeds 42/43/44, 5 iterations,
  `--use-weights`, `bkg_mode purity`, on the current `main` driver after a default-path regeneration of L0 within
  the frozen 1e-8 (pilot P0). The PRD 104/106 citation in the `# Paper binning` comment of
  `2d-unfolding/unfold_2d_omnifold_unbinned.py` (line 27 before the selective-I/O merge, line 30 after) is fixed in
  the same driver change, so the digest moves once. `--branch-select derived` exists only once the
  selective-I/O delivery is merged (PR #95); it may be used for universe runs only after its first real-file equality
  check (delivery REPORT §11; pilot P2).
- **Authority principle (review N10).** MAT conformance governs how a band is computed (C04's weights, X01's
  denominator). Physics intent governs whether a band is counted: a band MAT registers twice for one physical knob
  (KI 92) is counted once.
- **R1 Systematic block.** The July `purity_newomni` sweep (187 universes, CV `b8457af7`), with these exclusions
  and repairs; the May sweep is retired.
- **R2 Flux.** Weighted `CalcCovMx` with the constraint weights (KI 95). MINOS divided by Φ_MINOS,u (KI 96). No
  paper-derived cross block. Joseph's decision (§2.2).
- **R3 GENIE.** Rvx1pi counted once (drop Rvp1pi). `NormDISCC` kept as a null band (zero contribution) until its
  intent is established (G3).
- **R4 Laterals.** All 10 from the active-mode merged files, after a CFS copy and the nine remaining closure reads.
- **R5 Statistical block.** A seed-42 ensemble of 300 replicas (planning size, not a precision proof) with three
  independent Poisson(1) streams: data, signal MC, background rows. **Estimator-contract change:** purity is
  recomputed from the resampled D\* and B\*. The central is unchanged (b ≡ 1 reproduces it), but the statistical
  law changes, so this needs the reviewer's and Joseph's explicit sign-off. Completeness stays unresampled (KI 84).
  The separable background term comes from a bkg-only arm.
- **R6 Normalization.** 1.4% once, scaled to the adopted central.
- **R7 `C_ML`.** Not added as an independent block by default. Measure by the factorial panel; carry the seed
  main effect as C08 and report the interactions X02/X03 with their uncertainties; no automatic subtraction.
  Reasoning (review N4): a fixed-seed bootstrap's variance already contains the bootstrap × seed interaction, so the
  seed main effect is the correct random-effects increment, and adding the existing 10-seed scan on top would count
  the interaction twice. With 5 seed triplets the main effect has 4 degrees of freedom, so it is imprecise.
- **R8 Model and response.** C09 as a separate scoped allowance and C10 as a stated assumption, both Stage D.
- **R9 Conventions.** MAT centring (weighted mean for the constrained Flux band, mean otherwise), 1/N; centring,
  rank, PSD and ensemble error reported (plan Stage C).
- **R10 Open items before production.** G1 and G2 resolved by the pilot (§7); if either is material, the recipe
  gains its repair and returns for review. Joseph decides whether data-POT counting (C07′) needs a band.
  **Updated 2026-10-13** ([`diagnostics/REPORT.md`](diagnostics/REPORT.md)): G1 NOT A DEFECT (nG1 = 0); G2 NOT RESOLVED ABOVE TRAINER NOISE in `MaRES_0`
  (neither is MATERIAL, so neither repair is triggered by the pre-declared rule; how G2 is carried is the
  director's and Joseph's call); C07′ determined under Joseph's rule: not documented as a band, so omitted
  with a disclosure.

## 5. Missing inputs and acquisition routes

| item | what is missing | route | cost |
|---|---|---|---|
| G1 gap class | count and reco-pass rate of reco-in/truth-out events; whether they belong in the background | instrumented event-loop pass (a counter, no new outputs) over the 12 playlists, or an ID-carrying AnaTuple read | ≈ 0.9 node-h (12 loops × ≈ 0.077 node-h, from array 55985231); needs a reviewed counter patch; jobs ≈ 2–5 h, above the A/B grant's 1 h bound. **Acquired 2026-10-13 (P4): nG1 = 0, 0.5290 node-h actual; [`diagnostics/REPORT.md`](diagnostics/REPORT.md)** |
| G2 miss-row stand-in | size of the per-cell-c approximation for truth-weight-varying universes | pilot P5: compare one vertical universe unfolded with universe-weighted miss rows against the July product | design needed (a driver option or a re-weighted copy of the miss rows); unpriced until designed. **Acquired 2026-10-13 (P5, `MaRES_0`, seeds 42 and 43): NOT RESOLVED ABOVE TRAINER NOISE, 0.7233 node-h actual; [`diagnostics/REPORT.md`](diagnostics/REPORT.md)** |
| G3 `NormDISCC` | whether the knob should be null in this MC | GENIE/MAT intent (collaboration question) | none |
| Shared class (C03) | overlap of background rows with signal-tree miss rows | as G1 (same pass) | included in G1. **2026-10-13: P4 did not measure the overlap itself; the C03 recipe's shared-draw clause stays as written** |
| Active files durability | CFS copy of the 10 active merged files (≈ 538 GB) | copy to `/global/cfs/cdirs/m3246/` with re-measured sha256 (CFS first) | I/O only |
| C09, C10 | independent-generator 2D truths; response departures | Stage D | unpriced |
| Paper flux construction | which constraint file and PPFX version the publication used | collaboration question | none; not needed for a MAT-conformant construction |
| C07′ data-POT counting | whether a POT-counting uncertainty belongs in the construction, and its size | Joseph's materiality decision; the paper's own normalization section (not only the note's paraphrase) and MINERvA convention | none |

## 6. KNOWN_ISSUES records

- **New rows (independently verified):** 95 (C04 flux constraint weights) and 96 (X01 MINOS flux denominator).
- **Dated evidence notes appended** to rows 91 (identity evidence), 92 (confirmed, negligible), 93 (May broader;
  July qualified provisionally, pending P2; P06 confirmed) and 94 (confirmed; data-stream purity conditioning). Status cells are unchanged:
  closure is the row owner's.
- **Corrections appended** to `2D_OMNIFOLD_STUDY_STATUS.md` (PRD 104, 092007 citation; "both ν-e-constrained") and
  `2D_VALIDATION_FOR_3D.md` ("both constrained"). No history text is rewritten.
- G1 and G2 are candidates, not KI rows, until verified.

## 7. Stage C pilot and resource request

**Unit costs** (charge = elapsed × billing / 256, the rule that reproduces XR's 3.09 node-h;
`Q/xr-linux/results/final/sacct-final-ledger.psv`):

| unit | measured | charge |
|---|---|---|
| u_CV: CV-omnifile LightGBM unfold, 64 CPUs, shared | L0 836 s; L1 909 s; SB1 C 948 s | 0.058–0.066 node-h |
| u_U: universe unfold, all branches, full regular node | SB1 UL 2,604 s; July sweep median 2,530 s (2,355–2,738) | 0.65–0.76 node-h |
| u_U,sel: universe unfold, selective read | SB1 SL 888 s (prototype; the in-driver port is unmeasured) | ≈ 0.25 node-h |
| u_A: lateral unfold from an active merged file (≈ 54 GB) | unmeasured | bracketed 0.25–0.72 |
| u_E: one playlist event-loop pass, shared, billing 10 | array 55985231: median 1.97 h, max 4.92 h | ≈ 0.077 node-h (long-job median 0.076, max 0.192) |

**Pilot (requested), all diagnostic, no quoted product written:**

| item | content | runs | node-h |
|---|---|---|---|
| P0 | producer bridge: current-driver default CV unfold vs L0 (frozen 1e-8), plus the derived path on the CV | 2 × u_CV | 0.12–0.13 |
| P1 | statistical streams at seed 42: 20 joint (data + MC + bkg, purity from D\*, B\*), 20 fixed-purity (VL170 law at seed 42), 20 bkg-only; same bootstrap seeds. A mechanism and timing check, not a precision measurement: with 20 replicas a per-cell σ ratio carries ≈ 16% unpaired error, so only the paired design can resolve the expected ≈ 3% median change (review N12). Declared checks: b ≡ 1 reproduces the central; the bkg-only stream's reco-level variance matches Σw² of B; the paired σ ratio is reported with its uncertainty, with no pass/fail | 60 × u_CV | 3.5–4.0 |
| P2 | universe cases on the July inputs with the frozen producer: `NormDISCC_0` (no-op; reproduces July and CV), `MaRES_0`, one large Flux universe, `Muon_Energy_MINOS_0`; derived path, plus one default run for the first real-file equality | 4 × u_U,sel + 1 × u_U (up to 5 × u_U if the port is slow) | 1.7–3.8 |
| P3 | laterals from active files: `BeamAngleX_0`, `Muon_Energy_MINOS_0` | 2 × u_A | 0.5–1.4 |
| P4 | G1 census: instrumented event loop over 12 playlists | 12 × u_E | 0.9 |
| P5 | G2 diagnostic: one vertical universe with universe-weighted miss rows | 1–2 × u_U, after design | 0.7–1.5 |
| | **subtotal** | | **7.4–11.8** |
| | **≥ 20% reserve of the admitted total** (admitted = subtotal / 0.8) | | **1.9–3.0** |
| | **admitted total** | | **9.3–14.8** |
| | **pilot request (ceiling)** | | **15.0 node-h** |

The reserve follows the repository's cost model (`state/uncertainty-preparation-20261008/c/costs.py`: ≥ 20% of the
admitted total), not 20% of the subtotal (review M6).

Jobs: CV unfolds on shared QOS (64 CPUs, ≈ 15 min); universe and active unfolds on one regular node (< 1 h);
event loops on shared QOS (≤ 5 h). All < 12 h, CPU only, no premium. P4 and P5 need small reviewed code changes
(a counter; a miss-row weighting option) before submission.

**Sequencing (review M7), for the director to accept or split.** Plan §4 Stage C runs the pilot after the final
recipe is admitted. Here P4 (G1) and P5 (G2) are really Stage B diagnostics that the recipe's finality depends on,
and P0–P3 are the Stage C pilot proper. Either grant them together as requested, or issue P4–P5 as a Stage B
diagnostic grant first (≈ 1.6–2.4 node-h before reserve) and P0–P3 after the recipe is final. P2's lower bound
assumes the selective-I/O port (PR #95) is merged; without it, P2 is 5 × u_U = 3.3–3.8 node-h, inside the stated
upper bound.

**Stage C production estimate (not requested; repriced from the pilot):**

| item | runs | node-h |
|---|---|---|
| S1 statistical ensemble, 300 replicas, three streams | 300 × u_CV | 17.4–19.8 |
| S2 bkg-only separable arm, 100 replicas | 100 × u_CV | 5.8–6.6 |
| S3 remaining 8 laterals from active files | 8 × u_A | 2.0–5.8 |
| S4 `C_ML` factorial: (i) 20 bootstrap × 5 seed triplets; (ii) 7 universe settings × 5 seeds | 100 × u_CV + 35 × (u_U,sel…u_U) | 14.6–33.2 |
| S5 rollups, C04/X01/KI-92 repairs, matrices | login node | 0 |
| **subtotal** | | **39.8–65.4** |
| **admitted total, ≥ 20% reserve** (subtotal / 0.8) | | **49.8–81.8** |

**Contingencies, not included** (each needs its own decision):
- ~~a **G1 repair** if P4 confirms a material effect: new event-loop omnifiles (CV, 187-universe dump, active files;
  the dump-mode loop cost is not recorded here, so this part is **unpriced**) plus re-unfolding the central value
  and every block (≈ 187 × u_U,sel…u_U = 47–142 node-h on top of S1–S4), and Joseph's re-adoption of the central;~~
  **Corrected 2026-10-13: not needed; P4 measured G1 = 0** ([`diagnostics/REPORT.md`](diagnostics/REPORT.md));
- a **G2 repair** if P5 shows a material effect: re-running ≈ 170 truth-weight-varying universes, 43–129 node-h,
  ~~plus event loops~~ **(corrected 2026-10-13: no event loops; the weights are in `mc_truth_denom`, so re-unfolds
  only. P5 routed NOT RESOLVED ABOVE TRAINER NOISE, so the pre-declared rule does not trigger it; [`diagnostics/REPORT.md`](diagnostics/REPORT.md))**;
- a **July rebuild** if P2 fails its envelope: 47–142 node-h;
- all Stage D/E work. Against the plan's
forecasts (matching 25.5–93.2; repairs 79–469) and the delegation's 700 node-h ceiling, the construction without
a G2 repair is well inside both.

## 8. Stop conditions

None met.
- **Selection support:** the beam-angle laterals lack it in dump mode, but selection-complete inputs exist
  (active files) and need only re-unfolds. **G1 is also a support gap** (events in neither tree). It is a routed
  candidate rather than a Stop because its existence and size are unknown, its acquisition route is named and
  priced (P4, ≈ 0.9 node-h). If P4 confirms a material G1,
  that is a Stop-or-repair decision at that point (§7 contingency). **2026-10-13: P4 measured G1 = 0, so this
  support gap does not exist and is not a Stop** ([`diagnostics/REPORT.md`](diagnostics/REPORT.md)).
- **Joint-law evidence:** X01 is carried by MAT's in-band correlation, whose inputs exist; no transplanted
  correlation is needed. This passes **by adopting MAT's in-band convention as the joint law**; whether it reproduces
  the paper's flux × energy-scale correlation is unresolved (§2.3; review N6).
- **Required populations:** for construction, none is missing. Stage D's independent populations (C09, C10, coverage)
  remain the plan's separate dependency and are not a Stage B Stop.

## 9. Compute and evidence

- **Slurm under the Stage A/B grant:** none. **0 of 2.0 charged node-h.** All reads were on `login05`.
- **Cluster outputs:** every worker and verifier script and output is under
  `/pscratch/sd/j/josephrb/2d-closeout-stageAB-20261012/{b-flux,b-genie-truth,b-bkg-ml,b-lateral,verify-c04}/`, and
  copied to `E/` with `E/SHA256SUMS.nersc` (re-measured on the cluster; the copies check against it). Two large
  arrays (`b-genie-truth/sweeps.npz`, `adopted_cov.npz`) are listed there by sha256 and not copied. Local-only worker
  scripts are in `E/local-*` with `E/SHA256SUMS.local`. The two `.npz` arrays back the exact `C_U` rebuild and live
  only on `/pscratch` (review N11); a CFS copy belongs with the active files' copy under the Stage C grant.
- Two outputs are stored gzip-compressed (`gzip -n`), because they list cluster product filenames that the
  receipt-artifact gate would otherwise read as untracked deliverables: `E/b-genie-truth/may_flux.json.gz` and
  `E/b-lateral/completeness_scan.json.gz`. Their uncompressed sha256 is the one in `E/SHA256SUMS.nersc`; check
  with `gunzip -c <file>.gz | shasum -a 256`.

## 10. Independent review

**Setup.** One fresh read-only reviewer, a general-purpose Claude Opus 5.5 session, in its own detached worktree
at `45fd98f7` (empty `git status` at start and end; removed). Cluster reads on `login05` under `review-b/`; no Slurm
job (its `sacct` probe confirms 0 `2dc*` jobs). Budget: one review plus at most two focused re-reviews (plan §5).
C04 and X01 had their own independent verification (§2.2–2.3).

**Review of `45fd98f7`: PASS WITH CHANGES** (0 MATERIAL, 7 MINOR, 14 NOTE), preserved verbatim at
[`review/review-45fd98f7.md`](review/review-45fd98f7.md). With its own code it reproduced: KI 92 byte identity (3M-row
chunks and all background rows) and the σ effect; the July CV vs `E_U` (12 inputs bitwise; 1.4245e-11); the no-op
universes; P06 (87/87); `BeamAngleY_1`'s 1,422 exits and 1,072 entrants over all rows and `Muon_Energy_MINERvA_1`'s
identity; every KI-94 statistic and the driver order; G2's mechanism and `MaRES_0` completeness; the unit costs and
the arithmetic; the evidence checksums. It also measured C04 on the July sweep (5.158% → 3.747%). It judged EXIT
CONDITIONAL the right verdict.

**Repair batch 1 (cycle 1 of at most 2):**

| finding | disposition |
|---|---|
| M1: G1's consequence and repair cost unstated | §1, §2.10 and §7 now say a confirmed G1 biases the adopted central and give its contingency (partly unpriced) |
| M2: §8 did not test G1 against missing selection support | §8 argues why G1 is a routed candidate, not a Stop |
| M3: KI 95/96 remedies named retired May outputs | rows now say the diagnostic uses the adopted (May) sweep and the construction uses July (R1) |
| M4: "July qualified" too strong; the July sweep ran on uncommitted driver code | §2.5 heading and body, §1 and the KI 93 note now say provisional pending P2, producer revision uncommitted; P2 carries a frozen envelope; July rebuild added as a contingency |
| M5: KI 92 figure mislabelled, no NOT QUOTABLE | relabelled `C_U`+norm; quoted-total figures added; label added |
| M6: reserve taken on the subtotal | reserve now ≥ 20% of the admitted total: pilot 9.3–14.8 (as rounded at delivery), ceiling 15.0; production 49.8–81.8 |
| M7: pilot before the final recipe; R0 depends on PR #95 | sequencing stated for the director (grant together, or P4–P5 first); P2 price without the port stated |
| N1 citations (`:27`/`:30`, `:1203-1212`, `:1175`); N2 u_E billing; N3 KI 94 note attribution; N4 R7 reasoning and 4 dof; N5 R2 as Joseph's decision; N6 joint law by convention; N7 NOT QUOTABLE in the 3D correction; N8 POT and iteration rows; N9 MinosEfficiency; N10 authority principle; N11 `.npz` durability; N12 P1 criterion; N13 positive findings | all applied in place |
| N14: KI 95/96 faithful to the verification | no change |

**Focused re-review of `2b3774f7` (cycle 1 of at most 2): PASS WITH CHANGES**, preserved verbatim at
[`review/rereview-2b3774f7.md`](review/rereview-2b3774f7.md). M1–M3, M5–M7 and N2–N13 resolved; pricing checked
correct. Residues: R1 ("passes"/"qualified" unqualified in §1, §6 and the CATALOG row), R2 (a stale `:26` in R0),
R3 (C07′ unassigned but absent from §1, §5 and R10, and outside the table's vocabulary), N-a (a circular clause in
§8), N-b (rounding).

**Delivery commit.** It applies R1–R3, N-a and N-b as wording: "provisionally" in §1 and §6 and the CATALOG row; R0
cites the comment by content; C07′ is named in §1 and R10, gains a §5 row and an OPEN QUESTION status, and its paper
claim is scoped to the note's paraphrase; the §8 clause is deleted; the pilot reserve and admitted total round up
(1.9–3.0; 9.3–14.8). Wording only, and **not re-reviewed**; the second repair cycle was not needed.

**Same-model caveat.** Owner, workers, verifier and reviewer are Claude Opus 5.5 sessions. Distinct sessions of
one model are not cross-provider independence (plan §5).

## 11. Limits

- Every budget figure is diagnostic. The quoted 2D uncertainty and every publication text are unchanged.
- KI 91, 92, 93, P06, C05a and KI 94 rest on worker measurements; the Stage B review re-checks them.
- The July products carry no driver or input digest; their qualification rests on saved inputs, logs and mtimes,
  bridged by pilot P2.
- The beam-angle effect after unfolding, G1 and G2 are unmeasured. **Updated 2026-10-13:** G1 measured (nG1 = 0);
  G2 measured in `MaRES_0` only, NOT RESOLVED ABOVE TRAINER NOISE ([`diagnostics/REPORT.md`](diagnostics/REPORT.md)); the beam-angle effect remains unmeasured.
- Unit costs for the in-driver selective port and for active-file unfolds are unmeasured; the pilot measures them.
