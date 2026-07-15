# PET UQ Production — live status (PET point-cloud campaign)

**Session scope:** PET point-cloud uncertainty campaign ONLY. Produce a
corrected, internally consistent PET budget on a **background-subtracted**
measured target: `C_total = C_syst + C_retrain + C_stat + C_ML + C_lateral`, all components
sharing one corrected nominal PET estimator (same central vector, reported-bin
mask, bin ordering, training target, extraction config). Ordered plan and gates
mirror `PET_UQ_REMEDIATION_STATUS.md` (the authoritative dependency map).

This file is THIS session's live PET execution tracker: job IDs, config
choices, gates, failures, recovery. It is NOT the GBDT execution tracker
(`CORRECTED_UQ_PRODUCTION_STATUS.md`, read-only to this session).

**Campaign endpoint (2026-07-14): COMPLETE for the present analysis note.**
The current statistical block uses 20 coherent replicas. A 100-replica
statistical ensemble is planned before publication and has **not** been run.

## Ownership boundary (do not violate)
A concurrent session owns the GBDT flow. READ-ONLY, never edit/launch/cancel/
overwrite: `uq_5d/`, `unified_throw_cov*`, GBDT bootstrap/seedscan/budget
scripts+products, eavailW production, the interactive `claude-hold` allocation
(currently job **55819787**, CPU 5D-systematic throws), and
`CORRECTED_UQ_PRODUCTION_STATUS.md`. `squeue -u josephrb` before every
scheduler action; never cancel a job this session did not submit. Preserve the
dirty worktree and all other-session changes.

## Output hygiene
Corrected products go to NEW paths carrying `bkgsub`/`corrected`. Never
overwrite or delete the unsubtracted artifacts (`of_inputs_pc_fullcloud.npz`,
old nominal/alternate PET weights, the 8 unsubtracted bootstrap replicas, and
covariances depending on them) — preserve them under explicit `unsubtracted`
labels as cross-checks only. They never enter the corrected budget.

---

## VERIFIED FACTS (checked this session, login-node numpy/zipfile — no ROOT)

- `of_inputs_5d.npz` = canonical background-subtracted 5D measured target.
  - 4,091,707 data rows. `measured` = (4091707, 5) float32, column order
    **(pt, pz, eavail, q3, W)** (`axes=['eavail','q3','W']`; `edges_0..4`).
  - `measured_weights` float64, all finite, range **[0,1]**, mean
    **0.970870709**, sum **3972518.476326796**.  ← matches scope exactly.
- `of_inputs_pc_fullcloud.npz` (6.6 GB) = unsubtracted full-cloud PET input.
  - Same 4,091,707 data rows; `measured_pc` = (4091707, 12, 3) reco cloud;
    `measured_weights` = **all ones** (unsubtracted). num_part P=12.
  - Stores MC `truth_scalars`/`reco_scalars` but **NO `measured_scalars`** for
    the data rows → the Phase-1 gap to fill.
- **MC side already aligned by construction:** `w_truth`, `w_reco`,
  `pass_reco`, `pass_truth` are **byte-identical (CRC32)** between
  `of_inputs_5d.npz` and `of_inputs_pc_fullcloud.npz` (32,849,103 MC rows). So
  the fullcloud dump reused the same event pipeline/ordering. `edges_0..3` are
  also byte-identical.
- 4D vs 5D scalar `measured_weights` differ on **3,836,331 / 4,091,707** events
  (max|Δ| 0.838). Do NOT mix 4D and 5D scalar targets.
- Source ROOT: `runEventLoopOmniFold_PC_MEFHC_fullcloud.root` (51 GB); its
  `data` tree carries the five alignment branches measured / measured_pz /
  measured_eavail / measured_q3 / measured_W (per scope; verified by Phase-1
  job). Do NOT relaunch a C++ event loop to change measured weights.

## FIXED DECISIONS
- **Dimensionality (gate 0): 5D canonical.** Train one corrected 5D PET
  estimator on the 5D bkgsub target; obtain 4D as the exact covariance marginal
  `C_4D = M C_5D M^T`, labeled "4D marginal of the corrected 5D PET estimator."
  Never a separately 4D-purity-trained estimator; never mix 4D/5D scalar
  weights.
- **PET C_ML is PET-specific** (not the GBDT seed scan): corrected-target PET
  training ensemble, ensemble-mean-centered crossed design over
  subsample/split seed × TF estimator seed. Not a nominal-vs-one-alternate
  outer product; do not blindly sum correlated seed covariances.
- **GPU nondeterminism belongs in C_ML**, not an ad-hoc floor subtraction from
  C_stat.
- Env: PET GPU training via sbatch with `--export=ALL,HOME=/global/homes/j/josephrb`
  (school-account HOME fix). ROOT work uses `ROOT628_PREFIX=/global/homes/j/
  josephrb/.conda/envs/root_6_28`. Preserve the self-reexec extraction handoff
  (`pet/extract_bootstrap_replica.py`); TF-module Python has no PyROOT
  (KNOWN_ISSUES #17).

---

## PHASED PLAN + GATES

| Phase | Deliverable | Gate | Status |
|---|---|---|---|
| 1 | Corrected bkgsub point-cloud input `of_inputs_pc_fullcloud_bkgsub_5d.npz` | data-row alignment exact; target sum exact; MC aligned; old input untouched; provenance JSON; e2e fixture | **COMPLETE ✓** (all gates PASS; e2e fixture PASS) |
| 2 | Corrected nominal 5D PET (one unbootstrapped train) | finite full-coverage weights; ordered MC indices; extraction passes; norm/marginal checks | **COMPLETE ✓** (job 55822534; σ=2.7511e-38) |
| 3 | Corrected GPU nondeterminism floor (1 identical-seed repeat) | floor recorded before interpreting C_stat/C_ML | **COMPLETE ✓** (floor NEGLIGIBLE: per-bin rel median 9.1e-06, total 4.9e-06) |
| 4 | Corrected C_stat (coherent data+MC Poisson replicas, fixed estimator/split seed) | strict manifest; full MC coverage; center on replica mean; pilot vs floor | **COMPLETE ✓** (20 replicas, 7.85%/bin, 8620× floor) |
| 5 | Corrected PET C_ML (crossed subsample-seed × TF-seed, no Poisson) | ensemble-mean-centered; same mask/order; seed metadata; vs floor | **COMPLETE ✓** (12 trains, 2.35%/bin; est 42%/int 51%/sub 7%) |
| 6 | Rebuilt C_syst (vertical) and PET-native detector/lateral block on corrected nominal | actual ±, MAT 1/N mean-centered, 100-flux inventory; corrected target/alignment | **COMPLETE 2026-07-14.** Vertical median 7.58%; detector/lateral median 2.11%. The latter is a frozen-map shifted-detector response, not per-universe PET retraining or shifted-cloud membership regeneration. |
| 7 | Targeted per-universe retraining-response verdict | predeclared materiality criterion (trace + per-bin tail) | **COMPLETE 2026-07-14 (bank-invariant, FINAL).** All 6 predeclared bands MATERIAL: MaRES 0.971, MaCCQE 1.244, LowQ2 0.950, CCQEPauliSupViaKF 0.812, 2p2h 0.660 (all overall+frac), flux:55 0.099 (frac-only). Null floor negligible (0.008%). **`C_retrain` assembled: rank-6, PSD (min eig −2.4e-91), √tr 2.190e-38, per-bin σ/CV median 4.18% (p90 6.6%, max 20%)** = 0.74× C_syst-prelim √tr, +24% in quadrature. Integral impact small (Δ_total <0.3%/band) — bin-incoherent redistribution the frozen-map C_syst misses. `products/pet/bkgsub/pet_cretrain_bkgsub_5d.npz`. Scope: retraining-response only; C_syst-final + lateral still run on bkgaware (#13 re-quote pending). |
| 8 | Final assembly `C_total`, `C_4D = M C_5D M^T` | all blocks common central/mask/order; PSD/eigen; manifests | **COMPLETE 2026-07-14 ✅.** All 5 components on the common PET 10550-mask/cv: C_syst 2.97e-38, C_retrain 2.19e-38, C_ml 8.04e-39, C_stat 7.44e-39, C_lateral 4.69e-39. **C_total √tr 3.878e-38, per-bin median 15.10%; PSD ✓ (min eig −2.4e-91, exactly symmetric); block-sum exact.** 4D marginal `C_4D=M C_5D M^T`: 4790 bins, cv4 finite+nonneg, PSD ✓, median 12.37%. No-double-count (Δ rel. frozen map). `products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.npz` (+summary). **#16 CAVEAT (label until bounded):** C_lateral's 5 KINEMATIC bands (√tr ≈1.71e-39, ~4.4% of C_total √tr) are selection-migration support-limited — `pet_lateral_band_5d.py` shifts CV-selected events but does not re-run selection, so migrations aren't captured. Weight-only bands (MinosEfficiency/GEANT, √tr ≈4.37e-39, the bulk) + vertical C_syst (truth-reweight) are NOT affected. Bounding needs the #16 targeted full-MEFHC 3-band `MNV101_ACTIVE_UNIVERSE` migration run (NOT yet done). |

The present campaign is complete through Phase 8. The pre-publication
100-replica statistical expansion remains a future run and must not be described
as completed in the note or ledger.

---

## LIVE JOBS
(squeue-checked before each action; only this session's jobs listed)

| Job ID | Name | Phase | Submitted | Status | Notes |
|---|---|---|---|---|---|
| 55821658 | pet_bkgsub_in | 1 | 2026-07-12 | **COMPLETED** (9m05s, exit 0) | shared/cpu. Tests 20/20 + 10/10 PET. All gates PASS; built + self-verified `of_inputs_pc_fullcloud_bkgsub_5d.npz`. |
| 55822061 | pet_bkgsub_intr | 1 | 2026-07-12 | CANCELLED (redundant) | Interactive insurance alloc; cancelled once batch got resources and pulled ahead (no write race — cancelled during ROOT read). Node freed. |
| 55822296 | pet_bkgsub_smoke | 1 | 2026-07-12 | **COMPLETED** (exit 0) | Interactive. E2E fixture: tiny + real corrected npz both reach `PETxsec5D.xsec()` under ROOT (PASS). Node relinquished. |
| 55822534 | pet_nom_bkgsub | 2 | 2026-07-12 | **COMPLETED** (1h06m, exit 0) | Corrected NOMINAL. σ=2.7511e-38; 65,856-bin grid (10,550 populated); full coverage; extraction PASS. `pet_nominal_bkgsub_5d_{weights,xsec}.npz` + summary.json. |
| 55826200 | pet_nom_bkgsub (floor) | 3 | 2026-07-12 | **COMPLETED** | Floor NEGLIGIBLE (per-bin rel median 9.1e-06). `pet_floor_bkgsub_5d_{weights,xsec}.npz` + `pet_floor_bkgsub_5d_diagnostic.json`. |
| 55826201-206 | pet_boot_one (RID 1-6) | 4 | 2026-07-12 | RUNNING (pilot) | C_stat pilot on bkgsub; coherent data+MC Poisson, fixed est42/sub0. → `bootstrap_replicas/5d/pet_bootstrap_5d_{1..6}.npz`. Combine via `combine_cov_nd --expected-ids 1-6 --cv <nominal>`. |
| 55830054-065 | pet_nom_bkgsub (cml) | 5 | 2026-07-12 | **COMPLETE** (12/12) | C_ml crossed ensemble. per-bin 2.35%; est 0.42/int 0.51/sub 0.07. `pet_cml_bkgsub_5d.npz` + summary. |
| 55834767-802 | pet_boot_one (RID 7-20) | 4 | 2026-07-12 | **COMPLETE** (20/20) | C_stat = 20 replicas; per-bin 7.85% (p90 50.8%). `pet_cstat_bkgsub_5d.npz`. |
| 55841466 | pet_csyst_prelim | 6 | 2026-07-12 | **COMPLETED** (28m, exit 0) | PRELIMINARY vertical C_syst: 7.58%/bin median (p90 21.6%), sqrt-tr 2.97e-38; model-dominated (2p2h/MaRES/flux). Support-limited (pre-fix bank); FINAL needs GBDT rebank. `pet_csyst_prelim_bkgsub_5d.npz` + summary. |
| 55871828 | pet_p7_MaRES_1 | 7 | 2026-07-13 | **FAILED** (ROOT import) | First attempt; training driver transitively imported ROOT via `pet_systematics_5d` under the TF-module python (KNOWN_ISSUES #17). Reached GPU/TF init then died. Fixed: ratio loader made ROOT-free (inline `RHO_CLIP` + `np.load` + `uq_math.guarded_ratio`). |
| 55877410 | pet_p7_MaRES_1 | 7 | 2026-07-13 | **COMPLETED** (~2h48m, exit 0) — **bank-invariant (verified), FINAL** | Phase-7 validation retrain (UNIVERSE=MaRES:+1). Result: ‖Δ‖=1.324e-38, ‖s‖=1.363e-38, **overall=0.971, frac=0.929 → MATERIAL=True**. Integral: frozen +1.83% → retrain +0.89% (retraining halves the frozen shift); corr(Δ,s)=**−0.71** (structured compensation). Null control (below) proved the training-noise floor negligible ⇒ this Δ is genuine response. Inputs bit-identical bkgaware↔pre-fix (see receipts) ⇒ FINAL. `pet_p7_MaRES_1_{weights,response}.npz` + summary. |
| 55881281 | pet_p7_null | 7 | 2026-07-13 | **COMPLETED** (exit 0) | **NULL CONTROL:** retrain at r=identity (nominal prior), same seed/config. Result: **‖Δ_null‖=2.31e-41 = 0.0077% of ‖CV‖, ZERO bins >1%CV, integral reproduced to 4.4e-6.** ⇒ training-noise floor is negligible (0.17% of MaRES's ‖Δ‖=1.32e-38). CORRECTS the earlier "incoherent scatter = noise" read: the PET training is reproducible at fixed seed to 0.008%, so **essentially all of MaRES's Δ is genuine retraining response, including the bin-incoherent part.** Fan-out to the predeclared set is JUSTIFIED (real response, not noise). `pet_p7_null_{weights,response}.npz` + summary. |
| 55884508 | pet_p7_2p2h_1 | 7 | 2026-07-13 | **COMPLETED** (1h08m, exit 0) — **bank-invariant (verified), FINAL** | 2p2h:+1 retrain. **overall=0.66, frac=0.971 → MATERIAL=True**; integral cv 2.7511e-38 → frozen 2.7488e-38 (−0.08%) → retrain 2.7566e-38 (+0.20%). `pet_p7_2p2h_1_{weights,response}.npz` + summary. |
| 55884510 | pet_p7_MaCCQE_1 | 7 | 2026-07-13 | **COMPLETED** (bank-invariant, FINAL) | **overall=1.244, frac=0.950 → MATERIAL** (‖Δ‖ > ‖s‖). Integral cv→frozen +1.20% → retrain +1.00%. |
| 55884511 | pet_p7_LowQ2_1 | 7 | 2026-07-13 | **COMPLETED** (bank-invariant, FINAL) | **overall=0.950, frac=0.998 → MATERIAL**. Integral frozen −0.36% → retrain −0.66%. |
| 55884512 | pet_p7_CCQEPauliSupViaKF_1 | 7 | 2026-07-13 | **COMPLETED** (bank-invariant, FINAL) | **overall=0.812, frac=0.959 → MATERIAL**. Integral frozen −0.32% → retrain −0.33%. |
| 55884576 | pet_p7_fluxrank | 7 | 2026-07-13 | **COMPLETED** (bank-invariant) | ‖s_u‖ ranking over 100 flux universes → **dominant u=55** (‖s‖=2.801e-38; top-5: 55,74,49,71,7). `p7/pet_p7_flux_rank.json`. |
| 55891571 | pet_p7_flux_55 | 7 | 2026-07-14 | **COMPLETED** (bank-invariant, FINAL) | Dominant-flux retrain (flux:55). **overall=0.099, frac=0.469 → MATERIAL (frac/bin-tail only)** — small L2 response (flux is normalization-like) but broad bin-tail. Completes the predeclared 6-band set. |
| — | **C_retrain assembled** | 7 | 2026-07-14 | **DONE** | `pet/assemble_cretrain.py` over 6 material bands → `products/pet/bkgsub/pet_cretrain_bkgsub_5d.npz` (+summary): rank-6, PSD, √tr 2.190e-38, σ/CV median 4.18%. FINAL Phase-7 deliverable; adds to C_syst-final downstream. |
| 55916531 | pet_clat_bkgsub | 8 | 2026-07-14 | **COMPLETED** (~15m run, exit 0) | Corrected PET-native lateral (detector; option 2, bkgsub weights+cloud + bkgaware omnifile). **ALIGNMENT VERIFIED 32.85M rows; CV-path max\|ratio−1\|=0.0.** C_lateral √tr **4.69e-39, median 2.11%/bin** (MinosEfficiency-dominated). mask+cv bit-identical to C_syst. Modest (native≪transferred, per #3). `products/pet/bkgsub/pet_clateral_bkgsub_5d.npz`. **#16: the 5 kinematic bands (√tr ≈1.71e-39) are selection-migration support-limited (branch-shift, not re-run selection); weight bands (√tr ≈4.37e-39) clean. Bound pending the full-MEFHC 3-band MNV101_ACTIVE_UNIVERSE run.** |
| — | **C_total FINAL assembly** | 8 | 2026-07-14 | **DONE ✅** | `assemble_ctotal_bkgsub.py --label final` (5 components). C_total √tr **3.878e-38, median 15.10%**, PSD ✓; 4D marginal median 12.37% (4790 bins), PSD ✓; block-sum exact. `pet_ctotal_bkgsub_5d_final.npz`. |
| 55885561-566 | pet_p7f_* | 7 | 2026-07-14 | **CANCELLED** (byte-identical dupes) | 6 bkgaware "FINAL" jobs — cancelled once verified the bkgaware bank is bit-identical to pre-fix for all consumed inputs (a re-run would only re-sample the negligible GPU floor). |

## DECISION LOG / GATES PASSED
- 2026-07-13: **PHASE 7 PREDECLARATION (fixed BEFORE any retraining result is
  inspected).** User authorized Phase 7 (2026-07-13, "GPU hours are available;
  CPU is not"). Predeclared here so the verdict cannot be post-hoc tuned.
  - **Targeted set** = the systematic bands that together carry ≥80% of the
    preliminary vertical C_syst variance (per-band sqrt-trace ranking), using the
    **+1σ endpoint** (t_1) per knob, plus the dominant flux universe:
    **MaRES (28.3%), 2p2h (24.7%), flux (12.7%), MaCCQE (9.0%), LowQ2 (8.6%),
    CCQEPauliSupViaKF (6.1%)** → cumulative 89.4%. Rationale: retraining-response
    is a per-band map-nonlinearity correction; the sub-dominant tail (each <5%)
    cannot move C_total materially even at 100% response, so retraining all
    12+100 universes is unjustified (NOT authorized). Laterals/detector universes
    are **excluded from this set** — they need selection-complete shifted point
    clouds (KNOWN_ISSUES #16), which do not exist; their retraining-response is a
    separate deferred gate, not this one.
  - **Materiality criterion** (per universe u, on the corrected-nominal reported
    mask; s_u = x_frozen − CV is the frozen one-sided shift, Δ_u = x_retrain −
    x_frozen the retraining response):
    `overall_ratio = ‖Δ_u‖/‖s_u‖` and `frac = mean(|Δ_u| > 0.25·|s_u|)`;
    **MATERIAL(u) := overall_ratio > 0.25 OR frac > 0.05.**
  - **Consequence rule:** if MATERIAL for any targeted band, the FINAL C_total
    gains `C_retrain = Σ_u outer(Δ_u, Δ_u)` over material bands (rank-1 per band),
    added to C_syst-final. If immaterial for all, the retraining-response is
    **documented as negligible and omitted** (never silently dropped).
  - **Driver:** `pet/phase7_retrain_universe.py` (disk-free r_u injection into the
    validated `minerva_pet_dataloader.build_loaders` training path; normalize is
    scale-homogeneous so the injection is exact) + `pet/phase7_extract_compare.py`
    (frozen vs retrained via `PETxsec5D`, same nominal cloud/mask, only w_push
    differs) + `pet/sbatch_phase7_retrain.sh` (GPU) + `tests/test_phase7.py` (8/8).
  - **STATUS (superseded 2026-07-14):** originally labeled PRELIMINARY pending the
    background-aware bank. That bank (`bank_uthrow_5d_bkgaware`) landed and was
    verified **bit-identical to `bank_uthrow_5d` for every file the
    retraining-response consumes** (see the 2026-07-14 CRITICAL FINDING receipts).
    Because `unified_throw.py --dump` is signal-only and KNOWN_ISSUES #13 changed
    only per-universe background, the retraining-response is **bank-invariant** ⇒
    these results are **FINAL, not pre-fix/stale**. No re-run on bkgaware is
    scientifically meaningful (it would only re-sample the negligible GPU floor).
- 2026-07-13: **PHASE 7 VALIDATION RETRAIN (MaRES:+1) COMPLETE + NULL CONTROL
  LAUNCHED (PRELIMINARY, pre-fix bank).** Job 55877410 retrained the PET map on
  the MaRES:+1 prior (mean r=1.04) at the nominal config/seed, extracted
  frozen-vs-retrained on the 10,550-bin reported mask.
  - **Criterion verdict:** ‖Δ‖=1.324e-38, ‖s‖=1.363e-38 → overall=0.971,
    frac(|Δ|>0.25|s|)=0.929 → **MATERIAL=True** (predeclared criterion, reported
    faithfully — not tuned post-hoc).
  - **But the number is NOT all physics.** Two facts show Δ mixes a genuine
    structured response with a training-noise floor: (a) integral cross-section
    frozen +1.83% → retrain +0.89% (retraining HALVES the frozen shift) and
    corr(Δ,s)=**−0.71** ⇒ the retrained map coherently REABSORBS ~half the prior
    shift (physically sensible; pure noise would give corr≈0); (b) Δ's signed sum
    keeps only 40% of its |mass| (vs 90% for s) and median |Δ|/CV=3% (vs 0.5% for
    s) that cancels in the integral ⇒ a large incoherent bin-level scatter
    consistent with network-to-network stochasticity. A raw
    `C_retrain = Σ outer(Δ,Δ)` would fold that noise floor into the covariance and
    over-inflate.
  - **Decision (does NOT alter the predeclared criterion):** run a NULL CONTROL
    (job 55881281) — retrain at r=identity, same seed/config — so ‖Δ_null‖
    measures the pure training-noise floor. `‖response‖² ≈ ‖Δ_u‖² − ‖Δ_null‖²`
    (independent noise adds in quadrature). Fan-out to the remaining predeclared
    bands is GATED on this: if ‖Δ_null‖ ≈ ‖Δ_MaRES‖ the criterion firing is a
    noise artifact and C_retrain must be built from the noise-subtracted/coherent
    response (or the robust integral-level damping), not raw Δ. Driver extended
    with an additive `universe=null` path (tests still 8/8); no change to the
    universe logic or the criterion.
- 2026-07-13: **NULL CONTROL RESULT — earlier "noise" read OVERTURNED (job
  55881281).** ‖Δ_null‖ = 2.31e-41 = **0.0077% of ‖CV‖** (zero bins > 1% CV;
  integral reproduced to 4.4e-6). That is **0.17% of MaRES's ‖Δ‖ = 1.32e-38**, so
  `‖response‖² = ‖Δ_MaRES‖² − ‖Δ_null‖² ≈ ‖Δ_MaRES‖²` — the noise correction is
  ~3e-6, negligible. **Correction to the previous entry:** the incoherent
  bin-level scatter in MaRES's Δ is NOT training noise; the PET pipeline is
  reproducible at fixed seed to 0.008%, so essentially ALL of Δ (integral-halving
  coherent part AND the bin-incoherent part) is a genuine retraining response the
  frozen-map C_syst misses. (Process lesson honored: the cheap decisive check —
  a null retrain — overturned a pattern-matched "it's just noise" hypothesis;
  cost one GPU job, saved a wrong C_retrain.) ⇒ C_retrain WILL be built from the
  raw Δ_u (rank-1 per material band), noise-subtraction unnecessary. Predeclared
  set fan-out submitted: 2p2h/MaCCQE/LowQ2/CCQEPauliSupViaKF :+1 (jobs
  55884508/510/511/512); dominant flux universe pending a ‖s_u‖ ranking.
- 2026-07-14: **PHASE 8 COMPLETE — FINAL PET C_total assembled ✅.** All 5
  components on ONE corrected PET nominal/10550-mask/cv (bit-identical cv verified
  across every block; masks array-equal):
  | component | √trace | per-bin rel median |
  |---|---|---|
  | C_syst-final (vertical) | 2.970e-38 | 7.58% |
  | C_retrain (Phase 7) | 2.190e-38 | 4.18% |
  | C_ml | 8.036e-39 | 2.35% |
  | C_stat | 7.439e-39 | 7.85% |
  | C_lateral (detector) | 4.690e-39 | 2.11% |
  | **C_total** | **3.878e-38** | **15.10%** |
  Checks: **PSD** (min eig −2.4e-91, exactly symmetric, finite); **block-sum exact**
  (√(Σ component traces)=√(tr C_total)=3.8777e-38); **4D marginal** C_4D=M C_5D M^T
  (integrate over W w/ bin widths): 4790 bins, cv4 finite+nonneg, PSD ✓, median
  12.37%. No double-count (C_retrain Δ measured rel. frozen map; doc+receipts in
  assembler). Product: `products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.npz` +
  summary. Ranking: C_syst > C_retrain > C_ml ≈ C_stat > C_lateral — the
  **retraining response is the 2nd-largest term** (frozen-map C_syst understates
  bin-level structure). KNOWN_ISSUES #15 flagged for close-out review (blocking
  gates — final syst/lateral/retraining — now closed).
  **#16 SUPPORT-LIMIT CAVEAT (corrected labeling 2026-07-14, after initial "final"
  call):** C_lateral's 5 KINEMATIC detector bands (BeamAngle X/Y, MuonResolution,
  Muon_Energy MINERvA/MINOS; √tr ≈1.71e-39, ≈4.4% of C_total √tr) do NOT capture
  selection migrations — `pet_lateral_band_5d.py` shifts CV-selected events but
  does not re-run selection. Weight-only bands (MinosEfficiency/GEANT, √tr
  ≈4.37e-39 = the bulk) and the vertical C_syst (truth-reweight) are unaffected.
  Impact on C_total is bounded/small (kinematic sub-block ≈0.2% of total variance),
  but per #16 the block is labeled support-limited until the targeted full-MEFHC
  3-band `MNV101_ACTIVE_UNIVERSE` migration bound lands (NOT yet run — the
  per-(band,idx) event-loop rerun; CORRECTED_UQ ISSUE-5 "D0 caveat"). This is the
  one residual caveat on the otherwise-final PET C_total.
- 2026-07-14: **PHASE 8 FINAL ASSEMBLY IN PROGRESS — gate open, C_lateral being
  built fresh.** GBDT session finished the #13 two-leg re-quote (null effect
  <0.3%; bkgaware products in `uq_5d/universe_stage2_5d_bkgaware/` +
  `universe_sweep_bkgaware/`), lifting the C_syst-final/lateral block.
  - **C_syst-final = `pet_csyst_prelim`** (the PET vertical model+flux block): it
    is bank-invariant (verified) and the #13 background re-quote is null <0.3%, so
    both "preliminary" caveats are lifted. The GBDT bkgaware covariances are a
    DIFFERENT estimator (LGBM CV, 10694-bin mask, √tr 4.35e-38) and cannot be
    summed into the PET C_total — estimator/mask/cv must match the PET nominal.
  - **`C_retrain` term added to the assembler** with an explicit NO-DOUBLE-COUNT
    note (module docstring + summary field): C_retrain uses Δ_u = x_retrain(r_u) −
    x_FROZEN(r_u) (response rel. to the frozen map), while C_syst uses s_u =
    x_frozen − CV; Δ_u subtracts the frozen shift C_syst carries, so the two blocks
    sum DISJOINT quantities. Receipts: `phase7_extract_compare.py` (s_u, delta
    separate) + `assemble_cretrain.py` (outer(delta,delta)). Added `cv` to the
    C_retrain npz (bit-identical to the C_syst cv).
  - **C_lateral (detector) — user chose option 2: build fresh on the corrected
    target** (not a matrix op; no corrected PET lateral existed, only the 2026-06-29
    pre-correction block). `pet_lateral_band_5d.py` (frozen-cloud transfer via
    reco-weight ratios; #3 method) re-run with the bkgsub weights + bkgsub cloud +
    bkgaware omnifile; added `--out-npz` to dump `C_lateral` on the corrected
    10550-mask/cv for the assembler (job 55916531, gpu_shared 2×GPU for ~114G RAM,
    `pet/sbatch_pet_clateral_bkgsub.sh` → `pet_clateral_bkgsub_5d.npz`).
    **48h time-box** (deadline ~2026-07-16 07:00, before the Wed-evening freeze);
    if it won't land, FALLBACK = transfer the old PET-native block's relative
    covariance onto the corrected nominal, labeled explicitly as a pre-correction
    transfer (conservative per KNOWN_ISSUES #3). Lateral-pending 4-component
    assembly run as a validation checkpoint only — **not shipped** (detector block
    too large to omit from a "final").
  - **On landing:** `assemble_ctotal_bkgsub.py --label final --clateral
    pet_clateral_bkgsub_5d.npz` → PSD/rank checks → write final numbers here +
    flag KNOWN_ISSUES #15 for close-out review.
- 2026-07-14: **PHASE 7 COMPLETE — `C_retrain` assembled (FINAL, bank-invariant).**
  All 6 predeclared bands retrained + extracted against the frozen map on the
  common corrected-nominal cloud/mask; null control gave a negligible training-
  noise floor (‖Δ_null‖ = 0.008% ‖CV‖), so every Δ_u is genuine response.
  Materiality (predeclared criterion, applied as fixed): **all 6 MATERIAL** —
  MaCCQE 1.244, MaRES 0.971, LowQ2 0.950, CCQEPauliSupViaKF 0.812, 2p2h 0.660
  (overall+frac); flux:55 0.099 (frac/bin-tail only — normalization-like flux
  needs little map-relearning). `pet/assemble_cretrain.py` →
  **`C_retrain = Σ outer(Δ_u,Δ_u)`, rank-6, PSD (min eig −2.4e-91), √tr 2.190e-38,
  per-bin σ/CV median 4.18% (p90 6.6%, max 20%)**. That is 0.74× the preliminary
  C_syst √tr and +24% in quadrature — a substantial BIN-LEVEL augmentation the
  frozen-map C_syst misses, even though integral shifts are small (Δ_total
  <0.3%/band ⇒ bin-incoherent redistribution). Product:
  `products/pet/bkgsub/pet_cretrain_bkgsub_5d.npz` + summary. Adds to C_syst-final
  downstream (which still needs the #13 vertical-sweep re-quote — see KNOWN_ISSUES
  #13; out of Phase-7 scope). NULL control is permanent (bank-independent).
- 2026-07-13: **CRITICAL FINDING — bkgaware bank is BIT-IDENTICAL to pre-fix for
  everything PET consumes; PET retraining-response is BANK-INVARIANT.**
  **REVIEW Q&A (receipts):** *"Did Phase 7 use the corrected (background-aware)
  bank?"* — The Phase-7 retraining-response consumes ONLY the `sig_<band>_t`
  signal truth-ratio files. Those are **bit-identical** between the pre-fix
  `bank_uthrow_5d` and the corrected `bank_uthrow_5d_bkgaware`, so running on
  either is equivalent — the results ARE on the corrected bank in every way that
  can affect them. Verification receipts (2026-07-14): (i) all **30** consumed
  files (24 knob endpoints `sig_<band>_t_{0,1}` + 6 flux `sig_flux_t_u`)
  bit-identical via `numpy.array_equal`; (ii) **0/374** size mismatches; `sig_*_r`,
  `flux_univ_ratio.npy`, `td_*`, and `cv.npz` (first 200 MB) also identical; file
  set identical (no new `bkg_*` columns); (iii) mechanism — `unified_throw.py
  --dump` reads `mc_signal_reco` per-universe for `sig_<band>` and reads
  `data`/`mc_background` ONLY in group 0 for the CV measured target, so the #13
  per-universe-background change is never ingested by the bank. Re-running on
  bkgaware would only re-sample the GPU floor already shown negligible (null
  control ‖Δ_null‖ = 0.008% ‖CV‖). **Scope:** this bank-invariance is specific to
  the retraining-response; C_syst-final and the PET-native lateral still run on
  `bank_uthrow_5d_bkgaware` (out of Phase-7 scope). When
  `bank_uthrow_5d_bkgaware` landed (374 files, 26 GB, from
  `run_rebank_bkgaware.sh` → `unified_throw.py --dump` on the NEW bkgaware
  omnifile, all 8 groups completed), the alignment gate found
  `sig_MaRES_t_1.npy` bit-identical to pre-fix (frac changed 0.0). Verified
  broadly: **all 30 truth-ratio files PET uses** (24 knob endpoints + 6 flux)
  bit-identical (numpy `array_equal`); **0 size mismatches across all 374 files**;
  `sig_*_r`, `flux_univ_ratio`, `td_*`, and `cv.npz` (first 200 MB) also
  identical; **file set identical** (no new `bkg_*` columns). ROOT CAUSE:
  `unified_throw.py --dump` reads `mc_signal_reco` (signal) for the per-universe
  `sig_<band>` ratios and `data`/`mc_background` ONLY in group 0 for the **CV**
  measured target; it never reads per-universe background. The #13 fix changed
  only per-universe BACKGROUND weights, so the bank (signal + CV-measured) is
  unchanged. ⇒ **the bkgaware omnifile's new info is not consumed by this bank.**
  - **Phase-7 consequence:** the retraining-response uses only `sig_<band>_t`
    (signal priors) → identical on both banks → the pre-fix results ARE final for
    the model-knob retraining-response. The 6 submitted bkgaware jobs
    (55885561-566) are byte-identical duplicates → HELD pending user decision.
    NULL control unaffected (bank-independent).
  - **BROADER (GBDT-session domain) — TRACED 2026-07-14, VERDICT = GAP → filed in
    KNOWN_ISSUES #13:** the per-universe background systematic (#13's whole point)
    does NOT flow into ANY currently-quoted covariance. The signal-only throw-bank
    can't carry it, AND the mechanism that can (vertical sweep `sweep_bank_5d.py`
    do_run → `analyze_universes_5d.py`, which rebuilds per-universe measured
    targets from `w_bkg`; + lateral direct-driver `collect_bkg_nd(universe_branch=)`)
    has never been run on the bkgaware omnifile (no `bank_sweep_5d`/`*_bkgw.npy`;
    `uq_5d/universe_sweep/` unfolds are pre-fix 2026-06-28/29; `sweep_bank_5d.py:39`
    still points at the non-bkgaware omnifile; RUN_LOG:1439 lists the re-quote as
    deferred). So GBDT/PET C_syst, and the (E_avail,W) block, all still freeze
    background at CV. **C_syst-final must include the vertical-sweep re-quote on
    the bkgaware omnifile — the throw-bank rebank alone does NOT close #13.** Does
    NOT gate the PET retraining-response (background priors never enter the
    signal-map response). Receipts + close-out steps: KNOWN_ISSUES #13.
- 2026-07-13: **BACKGROUND-AWARE BANK CONFIRMED IMMINENT → FINAL Phase-7 on it
  (user coordination).** The GBDT session's just-finishing job produces the
  background-aware/selection-complete rebank (KNOWN_ISSUES #13/#16 fix) as a
  **new, non-destructive** directory:
  `nd-unfolding/bank_uthrow_5d_bkgaware` (NOT `_bkg`) — same schema as
  `bank_uthrow_5d` (cv.npz + flux_univ_ratio.npy + per-band
  `sig_<band>_{t,r}_{0,1}.npy` + 100 per-universe `sig_flux_t_{u}.npy`; 374
  files, ~26 GB). `bank_uthrow_5d` stays untouched (the background-CV baseline the
  GBDT budget used). ETA readable ~23:50–00:00 PDT 2026-07-13. Upstream omnifile
  (if a PET-specific rebank were needed): `runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root`.
  - **Decision — Path A (point straight at the shared bkgaware bank; NO PET
    rebank):** verified `bank_uthrow_5d` is the SHARED throw-bank read directly by
    PET (`pet_systematics_5d._opt` + the Phase-7 driver load it; KNOWN_ISSUES #12
    rebank 54330164 fed this shared bank), and it already contains the
    per-universe `sig_flux_t_{u}.npy` my flux-rank reads. So the FINAL verdict just
    repoints `--bank bank_uthrow_5d_bkgaware`. Auto-"PRELIMINARY" tag (keyed on
    basename==`bank_uthrow_5d`) correctly flips to final-bank.
  - **Alignment GATE (before trusting FINAL):** bkgaware re-runs the event loop
    with background-aware universe weights but MUST preserve the 32,849,103-event
    signal-cloud order for PET alignment. `pet/launch_phase7_final.sh` asserts
    `sig_MaRES_t_1.npy` shape=(32849103,), finite, and differs-but-small vs pre-fix
    (nonzero-yet-bounded, background ~0.35% of sample); driver shape-guard +
    PETxsec5D bit-identical w_truth gate back it up.
  - **Non-destructive outputs:** FINAL writes to `products/pet/bkgsub/p7_final/`
    (job names `pet_p7f_*`); PRELIMINARY pre-fix artifacts stay in `p7/`. The
    NULL control is NOT rerun (r=identity is bank-independent; 0.008% floor stands).
  - **Ready-to-fire:** `pet/launch_phase7_final.sh` (alignment gate → submit 5
    non-flux retrains {MaRES,2p2h,MaCCQE,LowQ2,CCQEPauliSupViaKF}:+1 + flux rank on
    bkgaware). Watcher `bvntb4be2` fires when the bank dir appears. Then: dominant
    flux retrain after ranking → assemble `C_retrain` from material bands → FINAL
    C_total. Held pre-fix jobs (55884510/511/512/576) cancelled after FINAL launch.
- 2026-07-12: **PHASE 5 C_ml COMPLETE (12 jobs 55830054-65).** Crossed ensemble
  combined via `pet/combine_cml_bkgsub.py` (ensemble-mean-centered, PET-nominal
  CV>0 mask = 10,550 bins): sqrt-trace 8.04e-39, per-bin rel **median 2.35%** =
  2578× the floor ⇒ PASS. **Variance decomposition (median frac): estimator
  0.424, interaction 0.505, subsample 0.066.** ⇒ PET ML variation is
  estimator-seed + interaction dominated; a split-only (fixed-estimator) C_ml
  would capture only ~7% of it — validates the crossed design and confirms the
  GBDT split-only C_ml must NOT be substituted (AI1). Products:
  `pet_cml_bkgsub_5d.npz` (C_ml + members + seeds) + summary.
- 2026-07-13: **PHASE 4 FINAL C_stat (20 replicas RIDs 1-20).** `combine_cstat_bkgsub.py`:
  sqrt-trace 7.44e-39, per-bin rel **median 7.85%** (p90 50.8%), 8620× floor.
  Stable vs the 6-replica pilot (7.25%) → converged. `pet_cstat_bkgsub_5d.npz`.
- 2026-07-13: **PHASE 8 PRELIMINARY C_total + 4D marginal assembled**
  (`pet/assemble_ctotal_bkgsub.py`; tests 4/4). Components on the common
  10,550-bin corrected-nominal mask (verified identical mask + central across
  C_syst/C_stat/C_ml):
  - **C_total (5D) per-bin rel median 13.90%** (C_syst 7.58% ⊕ C_stat 7.85% ⊕
    C_ml 2.35%), sqrt-trace 3.166e-38. Symmetric (exact), PSD (min eig ~-1e-91),
    finite diagonal.
  - **4D marginal C_4D = M C_5D M^T**: exact density projection integrating W with
    its bin widths (PET xsec is a density; verified vs brute force). 4790 4D
    reported bins, cv finite/non-negative, per-bin rel median **10.95%**,
    symmetric + PSD. Labeled "4D marginal of the corrected 5D PET estimator."
  - **PRELIMINARY** (C_lateral omitted — GBDT rebank blocked; C_syst is the
    support-limited prelim). NOT for ledger/note. `pet_ctotal_bkgsub_5d.npz` +
    summary. FINAL awaits C_lateral + C_syst-final (GBDT rebank) + Phase-7 verdict.
- 2026-07-13: **PHASE 6 preliminary VERTICAL C_syst DONE (job 55841466).**
  `pet/build_csyst_prelim_bkgsub.py` (reproduces the validated `pet_systematics_5d`
  C_syst block; ONLY the vertical block — no forbidden nominal-vs-alt C_ml, no
  bogus C_total) on the corrected nominal + pre-fix `bank_uthrow_5d`, neutral
  invalid-ratio: CV total 2.7511e-38 (= nominal ✓), 10,550-bin mask (= C_stat/
  C_ml ✓), sqrt-trace 2.97e-38, **per-bin rel median 7.58%** (p90 21.6%).
  Dominant bands: MaRES 1.58e-38, 2p2h 1.48e-38, flux 1.06e-38, MaCCQE 8.9e-39
  → Models/2p2h-dominant (cf. KNOWN_ISSUES #12 clean-rebank 8.24% precedent).
  **PRELIMINARY / support-limited** (KNOWN_ISSUES #13/#16); NOT for ledger/note.
  FINAL requires the GBDT background-aware/selection-complete rebank.
- 2026-07-12: **PHASE 6/7/8 scoping (while C_stat/C_ml GPU drains).**
  - Phase 6 vertical C_syst: reuse the convention-corrected `pet_systematics_5d.py`
    C_syst path (per-band mean-centered `mat_covariance([x_-,x_+])` + 100-flux
    mean-centered, MAT 1/N, `--invalid-ratio neutral`) on the CORRECTED nominal
    push weights — but take ONLY its C_syst. Its built-in C_ML is the FORBIDDEN
    nominal-vs-`weights-alt` rank-1 outer product; C_ml comes from my crossed
    ensemble (`combine_cml_bkgsub.py`), C_stat from `combine_cstat_bkgsub.py`.
  - **DEPENDENCY (KNOWN_ISSUES #13/#16):** existing `bank_uthrow_5d` (Jun 30) is
    PRE-fix, CV-support-limited → PRELIMINARY C_syst only, labeled
    support-limited. The GBDT session is rebuilding the background-aware /
    selection-complete products NOW (`uthrow5d_runF/blkF/combF` →
    `uq_5d/..._sb/`, `uq_5d/unified_throw_cov_5d.root`); Phase-6 FINAL consumes
    those when they land. `uq_5d/` is GBDT-owned — READ-ONLY.
  - Phase 7 (targeted per-universe retraining) is GPU-gated behind the corrected
    nominal + frozen systematic blocks; Phase 8 (assemble C_total,
    C_4D=M·C_5D·M^T) needs all components on the common nominal mask/order.
- 2026-07-12: **PHASE 4 PILOT PASS (RIDs 1-6).** C_stat combined via
  `pet/combine_cstat_bkgsub.py` (strict `load_replica_manifest`, PET-nominal
  CV>0 mask = 10,550 bins, replica-mean-centered): sqrt-trace 8.23e-39, per-bin
  rel **median 7.25%**, p90 46.9%, max 346% → **7965× the GPU floor** ⇒ PASS
  (spread ≫ floor; floor uncontaminating). Large per-bin stat is the honest
  fine-grid 5D value; the 4D marginal (project over W) will be far tighter.
  **Scaling decision: C_stat = 20 replicas** (RIDs 1-20; launch 7-20). Balances
  per-bin estimate stability (~16% precision on each sigma) against leaving GPU
  headroom for Phases 6-8 before 07-15. NOTE: `combine_cov_nd` was NOT used (it
  reads a ROOT CV hist + applies the GBDT mask); the PET combiner is npz-based
  on the corrected-nominal mask, consistent with the C_ml combiner.
  Products: `pet_cstat_pilot_bkgsub_5d.npz` + summary (pilot; superseded by the
  20-replica final).
- 2026-07-12: **PHASE 4 early peek (3/6 pilot replicas, RIDs 1-3).** C_stat
  per-bin rel median **6.37%** (p90 42.6%), sqrt-trace 8.75e-39 → **~7000× the
  GPU floor** (9.1e-06). Statistical spread overwhelmingly dominates
  nondeterminism ⇒ Phase-4 gate direction confirmed (floor does not contaminate
  C_stat). Large per-bin stat is expected for PET on the fine 10,550-bin grid.
  Full 6-replica pilot combine + scaling decision pending remaining replicas.
  DRAIN NOTE: gpu_shared runs ~2 of my jobs concurrently; 18-job wave (pilot +
  C_ml) drains over several hours — acceptable vs the 07-15 deadline, so kept on
  robust batch rather than unattended multi-GPU interactive orchestration.
- 2026-07-12: **PHASE 3 COMPLETE (floor job 55826200).** GPU-nondeterminism
  floor = corrected nominal vs same-seed repeat (est42/sub0, no bootstrap):
  total σ rel diff **4.87e-06**; per-bin rel floor median **9.11e-06**, p90
  2.08e-05, p99 5.18e-05, max 4.87e-04; L2 diff/nominal 7.78e-06. **NEGLIGIBLE**
  vs the expected O(%) C_stat/C_ml spreads → the floor will not contaminate
  their interpretation; no floor-subtraction (forbidden) and no
  hierarchical-decomposition branch needed. Also confirms the fixed seeds pin
  training (so the C_ml seed-crossed design captures genuine training variation,
  not GPU noise). Diagnostic: `pet/floor_diagnostic_bkgsub.py` →
  `products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json`.
- 2026-07-12: **PHASE 5 C_ml LAUNCHED (12 jobs 55830054-65).** Crossed design,
  NO Poisson: subsample seed ∈ {0,1,2,3} × estimator seed ∈ {42,43,44}. Reuses
  `sbatch_pet_nominal_bkgsub.sh` (PET_NOM_OUTDIR=products/pet/bkgsub/cml,
  PET_NOM_TAG=s{S}_e{E}) → `cml/pet_s{S}_e{E}_bkgsub_5d_{weights,xsec}.npz`.
  Build C_ml about the JOINT training-ensemble mean (12 members); retain seed
  metadata to inspect estimator vs subsample response + interaction. NOT the
  GBDT C_ml, NOT a nominal-vs-alternate rank-1 outer product, NOT a blind sum of
  seed covariances. Cleared to run parallel to C_stat (Phases 2+3 pass).
- 2026-07-12: **PHASE 2 COMPLETE (job 55822534, 1h06m, exit 0).** Corrected
  nominal 5D PET trained + extracted. Gate PASS:
  - reweight-all on full 32.8M: w_push mean 1.0128, std 0.0752, finite.
  - extraction full ordered MC coverage (`problems=[]`), w_push∈[0.837,1.388];
    W-source aligned; completeness anchored to xsec_5d_MEFHC_5iter_lgbm.root
    (median rescale 1.258).
  - 5D xsec (14,16,7,7,6)=65,856 bins, 10,550 populated, finite/nonneg,
    **total σ = 2.7511e-38 cm²/nucleon** (in the expected PET range).
  - Artifacts: `products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz` (166 MB,
    gitignored), `..._xsec.npz` (91 KB, gitignored), `..._xsec.summary.json`
    (tracked). **This is THE corrected nominal every downstream block references.**
- 2026-07-12: **PHASE 3 + C_stat PILOT plan (predeclared).**
  - Phase 3 floor: re-run the EXACT nominal config once (est_seed 42, sub_seed
    0, no bootstrap) via `sbatch_pet_nominal_bkgsub.sh` with `PET_NOM_TAG=floor`
    → `pet_floor_bkgsub_5d_{weights,xsec}.npz`. Per-bin/total diff vs nominal =
    the GPU-jitter floor (diagnostic; recorded before interpreting C_stat/C_ml).
  - C_stat pilot: reuse the corrected `sbatch_pet_bootstrap_replica.sh`
    (coherent data+MC Poisson, fixed est_seed 42 & sub_seed 0, varies only the
    Poisson replica id) with `PET_INPUTS=of_inputs_pc_fullcloud_bkgsub_5d.npz`,
    `PET_BOOT_OUTDIR=products/pet/bkgsub/bootstrap_replicas`. **Predeclared pilot
    = RIDs 1-6.** Build C_stat about the replica mean from the strict 5D NPZs;
    compare spread to the floor before scaling to the full inventory. (The 4D
    replica artifacts the launcher also writes are cross-checks; the canonical
    4D is C_4D = M C_5D M^T.)
- 2026-07-12: **PHASE 2 config recorded + train launched.** Adopted per-train
  config (identical to the corrected C_stat bootstrap-replica launcher
  `pet/sbatch_pet_bootstrap_replica.sh`, so the floor / C_stat / C_ml /
  systematic blocks all reference THIS nominal — no silent config change):
  - corrected input: `of_inputs_pc_fullcloud_bkgsub_5d.npz` (Phase-1 validated)
  - W-source (5D splice): `of_inputs_5d.npz`
  - train events = **2,000,000**; iters (niter) = **2**; epochs = **8**
  - architecture = **PET** (vendored ViniciusMikuni/omnifold point-cloud)
  - estimator seed = **42**; subsample/split seed (`--seed`) = **0**
  - `--reweight-all`: push weights evaluated on the FULL 32.8M gen cloud
  - TF = tensorflow/2.15.0 module; 1 GPU, ~1 h (cf. unsubtracted replica 1h07m)
  - outputs: `products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz`,
    `products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz` (+ summary.json)
  - Rationale for 2M/niter2/epochs8 (not the 40M FPS train): this is the config
    the 5D PET-vs-GBDT result and the corrected replicas use; C_stat (~20-100
    retrains) and C_ml (12 retrains) are only feasible at ~1h/train. The 40M
    FPS full-stats train (~29 A100-hr) is a separate FPS deliverable.
  - Extraction: `pet/extract_nominal_bkgsub.py` (PyROOT self-reexec; enforces
    full ordered MC coverage; PETxsec5D; comp anchored to the GBDT 5D product).
  - Launcher: `pet/sbatch_pet_nominal_bkgsub.sh`.
- 2026-07-12: **PHASE 1 COMPLETE.** Corrected input built + verified + fixture PASS.
  - `of_inputs_pc_fullcloud_bkgsub_5d.npz` (6.65 GB) built (job 55821658, 9m05s,
    exit 0). Independent CRC check: all 9 cloud+MC arrays byte-identical to the
    unsubtracted input (preserved); `measured_weights` swapped to the exact 5D
    bkgsub target (differs from fullcloud ones, matches of_inputs_5d;
    sum=3972518.476326796); `measured_scalars` (4091707,5) bit-exact to
    of_inputs_5d.measured; edges_4 (W) + provenance labels added. Unsubtracted
    input UNTOUCHED (mtime Jun 28, still all-ones).
  - **E2E fixture PASS** (`pet/smoke_bkgsub_extraction.py`, interactive job
    55822296): the real corrected npz reaches `PETxsec5D.xsec()` under ROOT —
    W-source alignment OK (w_truth bit-identical; 1327 tolerated q3-NaN rows),
    completeness anchored to xsec_5d_MEFHC_5iter_lgbm.root (median rescale
    1.258), finite non-negative xsec on the full (14,16,7,7,6)=65,856-bin grid,
    unit-push total σ=2.7057e-38 (≈ prior/MC xsec). Tiny synthetic variant also
    PASS.
  - Artifacts: `of_inputs_pc_fullcloud_bkgsub_5d.npz`;
    `products/pet/bkgsub/of_inputs_pc_fullcloud_bkgsub_5d.provenance.json`;
    `products/pet/bkgsub/measured_scalars_fullcloud_dumporder.npz`.
- 2026-07-12: **PHASE 1 GATES PASS (job 55821658).** Proven under the ROOT env:
  - DATA alignment EXACT: 4,091,707 rows extracted from the fullcloud `data`
    tree (of 4,119,797 total; box pt[0,4.5]×pz[1.5,60]) == of_inputs_5d rows;
    `n_mismatch_rows=0`; every column (pt/pz/eavail/q3/W) `max|Δ|=0.0` at
    float32 (bit-exact event-by-event; measured_pc rows carry the right weights).
  - MC alignment: w_truth/w_reco/pass_reco/pass_truth CRC-identical.
  - WEIGHTS: n=4,091,707, finite, [0,1], sum=3972518.476326796 (exact).
  - Per-bin purity structure: 10,024 populated bins, 4 with within-bin spread
    (max 0.137) — float32 boundary artifact of the canonical target, expected.
  - Tests: 10/10 PET + 20/20 remediation. Provenance JSON + measured_scalars
    sidecar written to `products/pet/bkgsub/`.
- 2026-07-12: Verified scope facts + MC CRC alignment (above). MC alignment
  gate PASS by byte-identity.
- 2026-07-12: Dimensionality decision recorded: 5D canonical, 4D as marginal.
- 2026-07-12: Isolation — work in-place in the shared checkout (user-approved;
  repo `.claude/settings.json` sets `worktree.bgIsolation: none`). The multi-GB
  inputs (`of_inputs_5d.npz`, `of_inputs_pc_fullcloud.npz`, 51 GB fullcloud
  ROOT) are gitignored and absent from any worktree; products land in canonical
  `products/pet/bkgsub/`. No auto-commit; commit only per the project gate /
  when directed.

## REPRODUCIBILITY DEPENDENCY (coordinate)
The corrected **nominal**, **floor**, and **C_stat** replicas were produced by
`pet/sbatch_pet_bootstrap_replica.sh` → `pet/extract_bootstrap_replica.py`
(C_stat) — both PRESENT ON DISK but UNCOMMITTED (untracked): they carry the
personal-account extraction hot-fix (self-reexec into root_6_28; KNOWN_ISSUES
#17), which my scope says to PRESERVE, not revert. I did NOT commit them (they
are the concurrent session's authored work). For full reproducibility of C_stat
they must be committed by the doc/GBDT-owning session (or on user direction).
The Phase-2 nominal uses my own committed `pet/extract_nominal_bkgsub.py`.

## CAMPAIGN STATE (2026-07-13) — independent PET work COMPLETE
Delivered + committed (34185c1 → 4059ee8): corrected bkgsub input; nominal 5D
PET (σ=2.7511e-38); GPU floor (~1e-5, negligible); C_stat (20 replicas,
7.85%/bin); PET-specific C_ml (2.35%/bin, crossed design, est+interaction
dominated); preliminary vertical C_syst (7.58%/bin, support-limited);
preliminary C_total (13.90%/bin 5D, PSD) + 4D marginal (10.95%/bin, 4790 bins,
PSD). All on one corrected-nominal 10,550-bin mask. Full test suite green
(14 PET + 20 remediation).

BLOCKED on GBDT-owned background-aware/selection-complete rebank (`uq_5d/`, in
flight, read-only): C_syst FINAL, the PET-native lateral block, the
unified/block diagnostic. GPU-gated + methodological: Phase 7 targeted
per-universe retraining (predeclare set + materiality criterion; laterals also
need the selection-complete clouds; do NOT infer authorization for a full
187-universe retrain). FINAL C_total = these + Phase-7 verdict.

## COMMIT GATE (per project convention)
A PET result does not exist until ONE scoped commit carries: scripts+launchers,
product JSON/txt summary, VALIDATION_LEDGER entry, ND_OMNIFOLD_RUN_LOG entry,
ND_OMNIFOLD_STATUS one-liner, OPEN_ITEMS update, note update if appropriate.
Do NOT commit other sessions' dirty-worktree changes. If a clean scoped commit
is unsafe, leave PET work uncommitted and report what must be coordinated.

### Commit readiness (Phase 1) — 2026-07-12
Clean, self-contained scoped set (all untracked/new, ZERO entanglement with the
dirty shared docs):
- `pet/build_bkgsub_pointcloud_input.py`, `pet/sbatch_build_bkgsub_input.sh`,
  `pet/smoke_bkgsub_extraction.py`, `tests/test_pet_bkgsub_input.py`
- `PET_UQ_PRODUCTION_STATUS.md` (this file)
- `products/pet/bkgsub/of_inputs_pc_fullcloud_bkgsub_5d.provenance.json`
  (trackable product summary; the 6.2 GB npz + 71 MB scalars sidecar are
  gitignored, as intended).

**Coordination caveat:** the commit-gate's shared docs — `VALIDATION_LEDGER.md`,
`ND_OMNIFOLD_RUN_LOG.md`, `ND_OMNIFOLD_STATUS.md`, `docs/OPEN_ITEMS.md`,
`KNOWN_ISSUES.md` — are ALL currently dirty with the OTHER session's uncommitted
edits (git `M`). Editing them for the PET gate would either sweep in
other-session work or require fragile `git add -p` against concurrent edits, so
those shared-doc updates are DEFERRED to coordinate with the doc-owning session;
the full Phase-1 record lives here meanwhile. No commit without user direction
(CLAUDE.md: commit only when asked; shared checkout).
