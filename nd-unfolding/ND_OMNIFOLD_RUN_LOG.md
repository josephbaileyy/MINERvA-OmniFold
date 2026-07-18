# N-D OmniFold — Run Log (append-only)

## 2026-06-13 — (E_avail,W) W-resolved lateral covariance adopted (KNOWN_ISSUES #4 closed)

The last open thread closed. The (E_avail,W) covariance was rebuilt with the
lateral block computed DIRECTLY from the 18-universe 5D detector sweep (9
bands × ±1σ + matched CV, re-inferred on the five-axis grid) instead of the
4D-marginalised transfer. Ran on an **interactive node** (job 54391533, full
512 GB Milan node — the 230 G fits trivially) to skip the shared-QoS backlog;
detached `salloc → srun` so the compute survived a session interruption and
finished cleanly (rc=0, ~1.5 h wall incl. the 32.8M-row load).

Result: W-resolved lateral median **2.36%/bin** (√tr 9.52e-40) is LARGER than
the transferred 1.80% (7.99e-40) → adopted. C_total median **14.9%/bin**;
sweep-CV vs frozen-CV marginal max|ratio−1| = 0.007 (gate PASS). Corner
significances published→W-resolved: GENIE 9.0→8.9, +MEC 9.2→9.2, NuWro
10.5→**15.6**, GiBUU 18.2→**22.4**σ — the proper detector covariance DEEPENS
the DIS-corner deficit for the worst-fitting generators and barely moves
GENIE, so the physics conclusion strengthens. Technote `sec_eavailw` table +
caveat, `sec_openquestions`, `sec_execsummary` all updated and rebuilt (64 pp,
0 undefined refs, 0 overfull). Artifact
`products/5d/eavailW_covariance_wlat.root` (pre-fix file untouched).

## 2026-06-12 (later) — FPS UQ stage COMPLETE: covariance adopted (throw ×1.295)

The whole pre-staged chain drained with zero failures end-to-end. Sweep
187/187 → block-sum C_syst median 7.27%/bin (Flux-led medians 5.01%; trace
dominated by Muon_Energy_MINERvA — the energy scale moving the large low-p∥
extension rate, an FPS-specific feature) → + norm/stat/ML → combined 7.33%
(rank 222/266). Unified throw (160 throws): unified/block √tr ratio 1.301
raw, **1.295 jitter-corrected** — nonlinearity present but far milder than
the 4D ×2.01, consistent with 2D having less band-mixing room; cross-term
83.2% of block. Adoption (4D-style conservative max() transfer): 39.5% of
bins inflated (max g 5.93, corners), **final FPS covariance median
8.19%/bin, √tr 9.724e-39, PSD exact** →
`uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root`
is the publishable FPS covariance. All numbers in the ledger. Remaining for
the FPS campaign: the 200-toy coverage verdict (54326694 → analysis
54351540).

Same day, parallel: milestone commit 621886c pushed to github/main;
collaborator-questions draft `docs/COLLABORATOR_QUESTIONS.md`; Ascencio
fine-binned stage-1 CV re-unfold launched (54351853, union of their 44-cell
edges); NEUT re-checked — still no public source (T2K-internal git only);
W-lat detector sweep drained (19/19) → (E_avail,W) wlat covariance 54279319
queued.

## 2026-06-12 — PET-bank reassessment VERDICT: published budget was inflated ×2 (conservative)

The rebank chain (entry below) landed clean: alignment gate bit-identical,
then `pet_systematics.py` on the clean bank gives C_syst median **8.24% vs
the published 18.31%** — the old bank's garbage miss-row ratios (#12,
`_clip`ed to {1e-2,1,1e2}) had inflated the PET systematic ×2.2. C_stat
(4.18%) and C_ML (3.32%) are IDENTICAL to the published file, confirming the
bank is the only difference. Clean total 11.66%/bin vs published 23.02%
(≈12.3% once the transferred lateral is added) — the PET budget is now
comparable to the GBDT 4D budget (13.5–14.9%) instead of ~1.7× worse.
Published artifact untouched; clean numbers live in
`products/pet/pet_4d_covariance_combined_rebank.root`. KNOWN_ISSUES #12
fully RESOLVED; ledger entry added; technote PET numbers to be revised in
the next consolidation pass (together with the W-lat (E_avail,W) update).

## 2026-06-11 (later still) — PET-bank reassessment launched + LE-evolution overlays DONE

Two parallel items started while the FPS chain drains (user-approved):

- **PET-bank reassessment (KNOWN_ISSUES #12 residual)**: `bank_uthrow`
  regenerated with the post-fix dump — miss-row rhos pinned to 1.0, source =
  the merged **5D** MEFHC `_universes_full` file (NOT the 3D default;
  `of_inputs_pc.npz` row order is the 5D signal tree), axes eavail,q3
  (`sbatch_uthrow_dump_rebank.sh`, 54330164) → `pet_systematics.py` re-run
  behind it with a bit-identical w_truth alignment gate
  (`sbatch_pet_rebank.sh`, 54330166 →
  `products/pet/pet_4d_covariance_combined_rebank.root`, does NOT overwrite
  the published artifact). Compare C_syst median vs the published 18.31%
  when it lands. IDs in `.pet_rebank_jobs.txt`.
- **LE→ME beam-evolution overlays (OPEN_ITEMS 9) DONE**:
  `compare_le_evolution.py` + `reference_le/` (both arXiv tarballs public,
  as with Ascencio). Shape-only by construction. Filkins pT/p∥: ME harder in
  p∥ (LE/ME shape median 1.27), as expected from the flux. Rodrigues
  (E_avail,q3): edges nest exactly in our coarse grid; strict-coverage
  rebinning leaves q3≥0.4 comparable — shapes agree at the 10–25% level with
  LE softer at low E_avail in q3 0.6–0.8. Numbers in the ledger; figure
  `products/4d/le_evolution_compare.png`.

## 2026-06-11 (later) — FPS final assembly + extension validation staged; bank PASS

The two "still to write" items from the entry below are now written and
in flight (all IDs appended to `.fps_uq_chain_jobs.txt`):

- **Bank validation PASS**: `bank_uthrow_fps` (54314368) = 374 files / 37 GB;
  row counts identical to `of_inputs_fps.npz` (49,152,885 signal / 20,573,521
  pass-reco / 49,150,928 truth — two independent readers agree); miss pinning
  verified at scale (~99.99% of non-pass-reco rows have rho exactly 1.0, the
  remainder being genuine off-grid signal-loop rows); all arrays finite;
  flux_univ_ratio (100, 15). Throws + block units released.
- **Final combined assembly** (4D-mirror, dependency-wired): bootstrap combine
  (54325576) + split-seedscan combine (54325577) via `combine_cov_nd.py` →
  full budget C_syst+norm+C_stat+C_ML (54325578, `sbatch_fps_budget.sh`) →
  unified-throw adoption (54325579, `sbatch_adopt_fps.sh`, reuses the
  path-parametrized `adopt_unified_4d.py`; sigma-inflation transfer onto the
  sweep's vertical block, PSD by construction) →
  `uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined[_uthrow].root`.
- **Hidden-variable closure** (54326695): the N-D driver's
  `--closure-reweight-axis` now accepts any registry axis NOT being unfolded —
  its truth column is loaded for the Gaussian bump only and popped off every
  loader output before the unfold, so OmniFold stays blind to it; the closure
  block writes `hClosureRefND` (bump-reweighted truth xsec) for per-cell
  recovery maps. Run: FPS 2D grid, bump in true E_avail (defaults A=0.3,
  c=0.3, s=0.15), `sbatch_fps_hidden_closure.sh`. **Result: PASS** —
  published median 0.17% / extension median 0.77% (max 4.05%), well inside
  the tier-2 prior band; numbers in the ledger.
- **Coverage toys** (54326694, array 1–200%32): `coverage_toy_nd.py` —
  npz-based closure+bootstrap toy mirroring the 2D 200-toy recipe (pseudo-data
  = MC reco of pass_reco&pass_truth events, driver seed offsets, completeness
  = 1) → `cov_fps/res_toy_*.npz`. 3-toy subsample smoke PASS end-to-end.
- **Region-split analyzer** `fps_extension_validation.py`: published-PS
  (185 cells, the battery's conservative tan20 anchor mask) vs extension
  (100 cells) split for BOTH the closure recovery map and the per-bin toy
  coverage (target 68.27%, flag <65% as in 2D).

## 2026-06-11 — FPS UQ chain pre-staged end-to-end (8 jobs, dependency-wired)

While the 187-universe FPS sweep (54261359) drains, the entire remaining FPS
UQ stage was staged so it runs unattended:

- **Block-sum covariance** `sbatch_fps_cov.sh` (54314362, afterany the sweep,
  guards on matched CV + 187/187 files): `analyze_universes_nd.py` vs the
  MATCHED CV, +1.4% flat norm → `uq_fps/universe_stage2_fps/`.
- **Bootstrap (C_stat) + split-seedscan (C_ML)**: `nn_dump_inputs.py` gained
  the driver's `--pt-edges/--pz-edges/--full-phase-space` (incl. the
  bin-centre flux remap) → `of_inputs_fps.npz` (54314364), then 100 Poisson
  replicas (54314365) and 24 split-seeds (54314366), both afterok the dump.
- **Mandatory unified throw**: `unified_throw.py --dump` generalized to
  axes/edges/FPS (2D bank now supported; `compare_unified_throw.py` td-cols
  made 2D-tolerant) and **miss-row ratios pinned to 1.0** — the merged FPS
  file is pre-#12-fix, so appended-miss universe branches are garbage;
  pinning is exactly the post-fix event-loop CV-proxy behavior (signal-loop
  rows keep genuine ratios even when reco migrates off-grid; true vertical
  miss variation enters via the clean `mc_truth_denom`). Also added
  `SetBranchStatus` pruning (~10× I/O cut; smoke: 600k rows in 8 s) and a
  `--max-entries` smoke flag. Chain: bank dump 8 groups (54314368) → 160
  throws (54314369) + 12-knob/12-flux block units (54314370) → combine with
  jitter-null (54314371) → `uq_fps/unified_throw_cov_fps.root`.

Job IDs in `.fps_uq_chain_jobs.txt`. Still to write once these land: the
extension-region hidden-variable closure + coverage validation, and the final
combined covariance assembly (block-sum vs unified-throw decision, as in 4D).

## 2026-06-10 — KNOWN_ISSUES #3 RESOLVED: PET-native lateral band (54284039)

Second run with the miss-pin + rho_r fixes: alignment exact (32.85M rows),
CV-path consistency 0, full pass_truth in every universe. Native lateral
median **1.74%/bin vs 4.03% transferred**; total budget 22.5% vs published
23.0%. Band ordering MinosEfficiency > Muon_Energy_MINOS ≈ GEANT_Neutron >
GEANT_Proton/Pion > BeamAngle/MuonResolution — the weight-response bands
dominate, as expected when the clouds are invariant and the kinematic bands
act only through acceptance gating. Interpretation adopted: the frozen-push
native band misses per-universe retraining response → it is the optimistic
bound, the GBDT transfer the conservative one; **published 23.0% stands**,
true lateral ∈ [1.74%, 4.03%]. Numbers in the ledger; artifact
`products/pet/pet_4d_covariance_combined_wlat.root` (per-band blocks
included). KNOWN_ISSUES #3 closed.

## 2026-06-10 — DISCOVERY: garbage universe branches on miss rows (KNOWN_ISSUES #12)

Found by the first `pet_lateral_band.py` run (54282492: GEANT bands exactly
zero + a common huge offset in every kinematic universe). Root cause in
`runEventLoopOmniFold.cpp::AppendTruthOnlyMisses`: it rebinds the CV scalar
and cloud branches but NOT the per-universe weight/kinematics branches, whose
signal-loop-local buffers are out of scope → every appended miss row (12.35M
= 37.6% of the 5D MEFHC `mc_signal_reco`) carries freed-memory garbage in all
`w_truth_*/w_reco_*/MC_*/sim_*_<band>_<idx>` branches. Verified empirically:
denormals/±1e±182, only 27% coincidentally equal to CV.

**Why the validated campaigns survive (first-order exact):** the driver's
xsec ∝ unfold × denom / of_in. denom comes from `mc_truth_denom`, whose
universe branches ARE clean (filled in the truth loop). The garbage on signal
-tree miss rows fails the gates / weight-guards, removing those rows from
unfold AND of_in by the same per-bin factor, which cancels in the ratio. The
same structure protects `eavailW_covariance.py` (its rho on misses is mangled
identically in unfold and of_in; denominator clean). Residual is second-order
(step2_w-vs-bin-average covariation of the dropped rows).

**What is actually affected:** (a) the first pet_lateral_band run — its
completeness denominator also came from the signal tree → f² suppression
(fixed: miss rows pinned to CV, exact for 7/9 detector bands, ≲10 MeV
neglect for the BeamAngle truth rotation; resubmitted 54284039 with the
reco-weight ratio rho_r added so GEANT/MinosEfficiency carry their real
w_reco variation). (b) `pet_systematics.py` C_syst/C_flux: the bank's
miss-row universe/CV ratios were garbage mangled by `_clip` to {1e-2,1,1e2},
entering counts AND denom from the same tree → the published PET 18.31% syst
median is possibly distorted. Reassessment needs a bank regen (banks deleted
in the 06-10 cleanup) — flagged in KNOWN_ISSUES #12, decision deferred.

**C++ FIX (this commit, rebuilt + installed to opt/bin):** miss rows now get
deterministic CV proxies (universe weights := tde.w_truth, truth-mode shifted
kinematics := CV truth values, reco-mode := −9999) — a miss carries no
per-universe variation in the dump; true vertical miss variation lives in
`mc_truth_denom`. Existing dumps NOT regenerated (first-order protection +
cost); any future event-loop production picks the fix up automatically.

## 2026-06-10 — KNOWN_ISSUES #3 + #5 launched (PET-native laterals; MINOS quality diagnostic)

**#3 PET per-lateral (job 54280218, `pet_lateral_band.py` + sbatch):** the
deferred "re-dump clouds + 18 GPU inferences" plan collapsed to a CPU job
after two findings: (a) `PC_MEFHC.root` is exactly event-aligned with the
merged 5D `_universes_full` file (identical entry counts, all four trees) and
the PC npz kept every row, so per-universe shifted branches JOIN by row index
with no C++ re-dump; (b) the muon laterals leave the recoil clouds invariant
(Gap 1), so the trained PET push weights are reused frozen — what shifts is
joined from the 5D file (truth coords MC/MC_pz/MC_q3_<sfx>, reco gate
sim/sim_pz_<sfx>, universe weights). All 5 kinematic bands carry the full
suffixed sextet (verified); MinosEfficiency/GEANT are weight-only. The script
asserts full-row alignment (32.85M rows, 4 truth columns + w_truth) and
CV-path consistency before computing; band convention = analyze_universes_nd
(ZᵀZ/N de-meaned, vs PET CV). Output
`products/pet/pet_4d_covariance_combined_wlat.root` (+ per-band blocks); the
GBDT-transfer comparison printed by the job doubles as a test of the
engine-independence assumption used by `pet_lateral_correction.py`.
Documented approximation: w_push not re-trained per universe (second-order:
training-set composition at the acceptance edge + weight swap only).

**#5 RESULT (54280253, 3 min): quality cuts ACQUITTED** — DR(eff_data/eff_MC)
= 1.03–1.05 at p_MINOS 1–2.5 GeV (closing needed ~1.67), flat-to-rising with
p; data uniformly MORE efficient than MC, so the omitted cuts cannot produce
a low-p_|| data deficit. eqp_qp confirmed already-fractional (the /qp variant
guts high-p). KNOWN_ISSUES #5 stays OPEN as an upstream
acceptance/modeling effect, bounded by the 2D paper reproduction; full
numbers in `2D_OMNIFOLD_REFERENCE.md` §IsMinosMatchMuon.

**#5 MINOS quality diagnostic (job 54280253,
`2d-unfolding/minos_quality_diagnostic.py` + sbatch):** no rebuild, no
unfold. Findings while scoping: NoDeadtime(1) is already in the preCuts and
fit_pass is implied by the patched IsMinosMatchMuon (100% of matched events)
— NOT candidates. Live candidates: `minos_trk_quality==1` (23.5% of matched
1A MC events are quality-2) and the curvature-significance cut (both eqp_qp
interpretations tested). Method: conditional efficiency of the added cuts
among base-selected events (match+is_ok+tdead==0+fiducial), data vs MC vs
p_MINOS over the 1A AnaTuples via xrootd; corrected sum ratio = baseline ×
DR(eff_data/eff_MC). Closing the 0.6→1.0 gradient requires DR≈1.67 at low p
falling to ≈1.0 high — DR≈1 everywhere acquits the quality cuts. Verdict +
PNG land in `2d-unfolding/products/minos_quality_diagnostic.png`; detail home
`2D_OMNIFOLD_REFERENCE.md` §IsMinosMatchMuon.

## 2026-06-10 — KNOWN_ISSUES #1 verification PASS + W-resolved lateral campaign launched (#4)

**Driver fix verified (job 54271042, 21 min):** both bare-GENIE FPS unfolds
re-run with the always-pass-weights driver and the 1/pot_scale corrections
stripped from `fps_pilot_compare.py`/`fps_prior_envelope.py` reproduce the
ledger: 1A anchor 0.9995 / |Δ| median 0.65%; MEFHC tune/genie totals
4.502e-38 / 4.369e-38 (pre-fix corrected value 4.367e-38 — ML-jitter);
envelope medians 2.90% published / 7.86% extension (was 2.91%/7.88%).
KNOWN_ISSUES #1 → RESOLVED; ledger entry added. Bare-GENIE ROOTs on disk
(`products/5d/xsec_2d_FPS_{1A,MEFHC}_genie.root`) are now post-fix.

**W-resolved lateral campaign (KNOWN_ISSUES #4, user-approved):** replaces
the 4D-transferred lateral block in the (E_avail,W) covariance with real
re-inference. Verified first: the merged 5D `_universes_full` file carries
all shifted-W lateral branches (`sim_W_<band>_<idx>`, `MC_W_…`,
`W_truth_…`; 10 = 5 kinematic bands × 2, MinosEfficiency/GEANT are
weight-only and fall back to CV kinematics — same path the 4D 187-universe
sweep exercised). Campaign = 18 detector universes (6 muon/beam laterals +
3 GEANT bands) + matched CV, re-inferred on the full 5D axes:
- `sbatch_unfold_5d_detector.sh` (NEW): array 0–18%8 shared/32-core, task 0
  = matched CV (`--axes eavail,q3,W --seed 42`), outputs
  `uq_5d/universe_sweep/5d_xsec_MEFHC_5iter_lgbm_uni_full_<TAG>.root`.
  Job 54279318, dependency-queued behind the FPS sweep (54261359) per the
  I/O-bound lesson.
- `eavailW_covariance.py` extended with `--lateral-sweep-cv/-glob`: builds
  C_lateral from the sweep marginals vs the matched sweep CV with the
  `analyze_universes_nd.py` band convention (C_b = ZᵀZ/N de-meaned),
  carrying real (E_avail,W) off-diagonals (the transfer was diagonal-only);
  prints old-vs-new before adopting. Transfer path kept as default.
- `sbatch_eavailW_cov_wlat.sh` (NEW): chained job 54279319, requires all 18
  universes + CV on disk, writes `products/5d/eavailW_covariance_wlat.root`
  (pre-fix product kept for comparison).
Close-out: compare corner significances new-vs-old, then KNOWN_ISSUES #4 →
RESOLVED and technote (E_avail,W) numbers updated if they move.

## 2026-06-10 — Disk cleanup: 1.6 TB → 796 GB (~830 GB freed)

Deleted only artifacts redundant with kept-and-verified products (each merged
file checked: no recovery flag, per-tree entry counts equal the sum of its 12
inputs, POT counters exact):
- per-playlist `_universes_full` omnifiles: 5D-FPS (180G), 5D (133G), 4D
  (126G) — merged MEFHC files KEPT; re-merge would need evloop regeneration.
- per-playlist PC point-cloud omnifiles (46G) — merged `PC_MEFHC.root` KEPT.
- 2d-unfolding per-playlist non-full `_universes` (64G, May 22 stage-1) —
  superseded by the kept merged `_universes_full` (119G, all 187 bands).
- read-once banks `bank_sweep`/`bank_uthrow`/`bank_uthrow_4d` (95G) — pure
  caches; rebuild from the kept merged files via `assemble_bank_4d.py` /
  `sweep_bank.py` (one ~1–2 h job) if 4D/5D sweeps or throws are ever redone.
- `uq_4d/universe_stage2_4d_int/` (7.7G duplicate) and the standalone
  `uq_universe_4d_covariance.root` (7.7G) — strict subsets of the kept
  `_combined.root` (46 per-band + combined); adopted `_combined_uthrow.root`
  untouched.
- GiBUU `work_gibuu_arr` auxiliary output (140G): all task files deleted
  EXCEPT `FinalEvents.dat` (2.0G total, 80 tasks) — the complete per-event
  record every distiller reads, so any future GiBUU observable re-histograms
  from disk without re-running GiBUU (the lesson from the 06-03 cleanup,
  which forced regen job 54190920 for the W axis).
Pending jobs unaffected (sweep reads the merged FPS universes file; refix
reads the FPS CV omnifiles).

## 2026-06-10 — Driver no-weights normalization fix (KNOWN_ISSUES #1)

Root cause confirmed in `unfold_nd_omnifold_unbinned.py`: without
`--use-weights` the collector still sets `w_truth = w_reco = pot_scale` per
event and the binning uses them, but the OmniFold call passed `None` weights —
the step-1 classifier then absorbs the data/MC normalization gap (≈pot_scale)
into the learned weights and the binning applies pot_scale a second time ⇒
result globally low by exactly pot_scale. Fix: always pass the collected
POT-scaled weights to `ohf.omnifold` (a no-op in `--use-weights` mode — same
arrays as before; the in-flight FPS sweep is unaffected) and mirror them on
the closure pseudo-data side so closure stays self-consistent. The exact
global 1/pot_scale corrections were REMOVED from `fps_pilot_compare.py` and
`fps_prior_envelope.py`; pre-fix bare-GENIE ROOTs are stale. Verification
job 54271042 re-runs both bare-GENIE unfolds (1A + MEFHC) and the battery +
envelope; PASS = ledger ratios reproduce without any correction.

## 2026-06-10 — Ascencio cross-check UNBLOCKED and DONE (consistent)

The 2110.13372 supplemental data was assumed member-gated; it is in fact
inside the PUBLIC arXiv source tarball (`arxiv.org/e-print/2110.13372`,
`supplementalMELowRecoilData.txt`: 44-cell d²σ/(dEavail dq3) + full
covariance; copied to `3d-unfolding/genie/ascencio_2110.13372_supplemental.txt`).
New `compare_ascencio_fullcov.py`: merges both measurements onto the maximal
common (Eavail,q3) grid (per-fine-column tiling; 2 super-cells, Eavail<0.4 ×
q3 [0.4,0.6)/[0.6,1.2)), with our 4D marginalisation gated at pz<20 GeV to
mirror their muon cut, and propagates BOTH full covariances (ours = adopted
unified-throw combined) through the merge maps. Result: ours/Ascencio 1.092 /
1.063, pulls 1.29σ / 0.86σ, **full-cov χ²/ndf 1.68/2 (p=0.43) — consistent**.
Caveats: shared MINERvA systematics treated as independent; pμ≈pz at 20 GeV.
Numbers in the ledger; technote updated (abstract, §7.8 ¶+fig, §8, App. A
item 6); OPEN_ITEMS #1 closed (optional refinement: 44-cell on their fine
edges = re-unfold + sweep on that binning).

## 2026-06-09/10 — Full-phase-space (FPS) campaign: pilot GO → CV production + anchor gate PASS → UQ stage launched

Decision memo `FPS_PILOT.md`; numbers in `../VALIDATION_LEDGER.md` (2026-06-09
delta + 2026-06-10 FPS entries); bugs found → `../KNOWN_ISSUES.md` #1.

- **Infrastructure**: `MNV101_FULL_PHASE_SPACE` env switch in
  `runEventLoopOmniFold.cpp` (drops the four truth muon kinematic cuts, keeps
  ZRange/Apothem; reco selection unchanged — the truth-authoritative gate
  reclassifies former kinematic fakes as signal automatically). N-D driver
  gained additive `--pt-edges/--pz-edges/--full-phase-space` (θ-gate lift) and
  `--prior-reweight FILE[:HIST]` (truth-level (pT,pz) prior swap). Extended
  grid = exact paper edges + catch bins (pT +[4.5,30]; p∥ +[0,0.75] and
  +[60,120]). The per-pT integrated flux is constant (2e-14% spread) so the
  catch-bin flux remap is exact — no flux regeneration.
- **1A pilot** (jobs 54232749/54232780/54233015): anchor PASS (0.65% median),
  33.6% of fiducial CC truth rate outside the published cuts (22.4% p∥<1.5,
  11.2% θ>20°), eff<2% cells carry 27.7%, prior swap 3.0%/5.1% median
  (in/out). → GO with two-tier reporting. En route found the driver
  no-`--use-weights` pot_scale normalization bug (KNOWN_ISSUES #1; exact
  global correction applied in `fps_pilot_compare.py`).
- **CV production** (array 54244119, 12 playlists ~1.6 h each →
  `runEventLoopOmniFold_5D_FPS_{PL}.root`, 6.6 GB total) + **MEFHC battery**
  (54244120): hadd, acceptance (matches pilot fractions at 41M weighted
  truth), FPS unfold tune prior (total **4.502e-38**, +46% vs restricted
  3.073e-38), bare-GENIE prior, control (= frozen 2D production number
  exactly), plain closure on the extended grid (recovered/truth 1.0000
  everywhere), anchor + prior-swap compare. **Anchor gate PASS** (0.9994
  integral, 0.57% median per cell).
- **3rd prior**: raw NuWro flat events (work_nuwro_p*, no PS cut at
  generation) → `build_fps_prior_nuwro.py` NuWro/MnvTune (pT,pz) shape ratio
  (2M events, 0.06% GENIE rate uncovered, clip [0.2,5]);
  `sbatch_fps_envelope.sh` (54244178) ran the NuWro-prior unfold +
  `fps_prior_envelope.py`. **Result (2026-06-10)**: totals tune/NuWro/GENIE =
  4.502/4.475/4.367e-38 (±1.5%); per-cell half-spread median 2.91% published
  vs 7.88% (p90 62%, max 81%) extension — the tier-2 prior-dependence band,
  concentrated in the dead cells as expected.
- **UQ stage launched on the gate**: FPS `_universes_full` array 54254627
  (12 × 24 h walls, MNV101_DUMP_UNIVERSES + FPS) → SetMaxTreeSize merge
  54254628 (~190 GB expected). Next after the merge: matched CV + 187-universe
  sweep on the extended grid, bootstrap, split-seedscan, **unified throw
  (mandatory in FPS** — the migration-heavy corner that broke the 4D block sum
  ×2 is inside the measurement), extension-region hidden-variable closure +
  coverage.

## 2026-06-06 — Workstream F: W (hadronic invariant mass) 5th axis + truth diagnostics

Direction B of `../docs/FUTURE_DIRECTIONS.md` — add a physically-motivated 5th axis to
localise the open +2.2σ high-E_avail DIS-tail excess (DIS = high W). Done while the PET
higher-iteration retrain ran. User ask: investigate the other candidate observables too so
the expensive 12-playlist re-run happens ONCE.

**Investigation result:** W is the ONLY candidate with a clean reco estimator (truth
`GetTrueExperimentersW()` already existed; reco from `GetQ2Reco()` + `GetRecoilE()`).
Proton multiplicity and hadronic angle are clean in TRUTH (`mc_FSPart*`) but reco-limited —
the tuples carry only calorimetric clusters (energy+position), no per-particle id/momentum.
So W becomes a real axis; multiplicity/angle are dumped as TRUTH diagnostics (no reco
estimator yet → can't be OmniFold axes, but ready for the excess investigation).

**Code:**
- `CVUniverse.h`: `RecoW()` (mirrors `RecoQ3`: q0=recoil_E, Q² from muon kinematics,
  W=√(M²+2Mq0−Q²)); truth diagnostics `GetNProtonsTrue()` (KE>110 MeV), `GetNChargedPionsTrue()`,
  `GetHadronAngleTrue()` (polar angle of summed FS-hadron momentum).
- `runEventLoopOmniFold.cpp`: full W mirror of q3 across all sites (truth-denom, signal reco,
  miss-append, background, data, + per-universe lateral shifted `W_truth_/MC_W_/sim_W_` since
  W is muon+recoil dependent like q3). Truth diagnostics `MC_nproton/MC_npip/MC_hadangle` on
  the truth-denom cache + signal reco + miss. W/diagnostic branches are unconditional and the
  shifted-W rides the existing `MNV101_DUMP_UNIVERSES` gate → the EXISTING evloop launchers
  now produce W with NO new script (one re-run gives the full 5D + systematics inputs).
- `unfold_nd_omnifold_unbinned.py`: registered axis `W` (`lateral_invariant=False`,
  edges [0,1.1,1.4,1.8,2.2,3.0,100] GeV). `--axes eavail,q3,W` does the 5D unfold.

**Build:** batch job 54061121 COMPLETED clean (no errors).
**Smoke (interactive salloc 54061557, 1×1A file, `MNV101_DUMP_UNIVERSES=BeamAngleX`) — PASS:**
- mc_signal_reco: MC_W median 1.672 GeV (0.18–11.3), sim_W median 1.579 (reco-pass; W²<0→0
  guard as in reco q3); MC_q3 median 1.767 UNCHANGED (no q3/eavail regression); MC_nproton
  med 1/max 7, MC_npip med 1/max 11, MC_hadangle med 0.422 rad (∈[0,π]).
- data measured_W median 1.634; mc_background sim_background_W median 2.403.
- 16,791 truth-only misses appended, no segfault (W is scalar; q3 vector-rebind hazard N/A).
- shifted-W lateral branches present (MC_W_/sim_W_BeamAngleX_0/1); truth W shifts only 1.8%
  under BeamAngleX = correct (truth W from true muon kinematics is beam-angle-invariant, like
  truth q3). `smoke_W.sh` is the durable smoke driver.

**NEXT (gated on user approval — the expensive step):** re-run the 12-playlist event loop
(`sbatch_evloop_array_4d_universes_full.sh`, now also dumps W + diagnostics) → hadd → 5D
unfold `--axes eavail,q3,W` + anchors (W-marginal recovers the frozen 4D) → 5D covariance.


## 2026-06-06 — Workstream E: PET point cloud → REAL absolute cross section (method milestone)

`/plan` decision (user): elevate the validated PET point-cloud from a *shape* cross-check
(`pet_vs_gbdt.py` area-normalizes because PET trains on a 2M subsample) to a **real,
absolutely-normalized, full-statistics** cross section, at **method-milestone** scope
(closure + GBDT cross-check; full PET systematics deferred). Other directions recorded in
`../docs/FUTURE_DIRECTIONS.md`.

**Key enabler:** `MultiFold.reweight(events, model)` applies the trained classifier to *any*
events, so we train PET on a tractable subsample but **evaluate push weights on the full
32.8M gen cloud** (push weight is a normalization-independent per-event ratio), then bin
through the same absolute path the GBDT driver uses.

Code:
- `minerva_pet_dataloader.py`: added `--reweight-all` (after `of.Unfold()`, build the full
  loader and `of.reweight(full_gen, of.model2)` → save full-stats `w_push`,
  `mc_indices=arange(N)`) and `--closure` (pseudo-data = MC reco of pass_reco events).
- `pet_vs_gbdt.py`: added `--absolute` (+`--closure`) mode — bins `w_push*w_truth` via
  `unfold_nd_omnifold_unbinned.histnd`, reads `hCompletenessND_flat` from the GBDT 4D ROOT
  (completeness is reweight-independent), and calls `xsec_nd.extract_cross_section_nd` with
  the dump's flux/POT/nucleons. Writes `xsec_4d_PET_absolute.root` mirroring the GBDT naming
  and reports absolute total σ + per-axis median |Δ| vs GBDT (closure: recovered/truth ≈ 1,
  completeness=1).
- Launchers: `sbatch_pet_train.sh` extended (`--reweight-all`, env NITER/EPOCHS/TRAIN_EVENTS/
  CLOSURE, time→6h, saves `pet_weights_full.npz` / `pet_weights_closure.npz`); new
  `sbatch_pet_xsec.sh` (CPU/ROOT, absolute extraction + closure gate).

**Plumbing test (PASS):** ran `pet_vs_gbdt.py --absolute` on the existing 2M-subsample
weights → PET total σ 1.657e-39, **PET/GBDT = 0.0540 ≈ 2M/32.8M (0.061)**, per-axis |Δ| ~94%
(pure normalization deficit). Confirms the completeness reshape, flux/POT/nucleon load, and
`extract_cross_section_nd` path are correct; full-stats reweight should scale the total ~×16.4
to ≈2.7e-38 (near the GBDT 3.066e-38), leaving only the genuine PET-vs-GBDT method difference.

**Submitted (2026-06-06):** main chain `pet_train(full) 54050740 → pet_xsec 54050741`;
closure chain `pet_train(closure) 54050742 → pet_xsec(closure) 54050743`. Job ids in
`.pet_milestone_jobs.txt`. Gates: full-stats reweight mean≈1; closure recovered/truth≈1;
absolute PET/GBDT total ratio near 1 within the ML band.

**RESULTS (2026-06-06, all jobs COMPLETED) — milestone ACHIEVED.**
- **Gate 1 (full-stats reweight, mean≈1, finite) — PASS.** main `w_push` over 32.8M gen:
  mean **1.0277** std 0.107 finite; closure: mean **0.9884** std 0.0016 finite.
- **Gate 3 (closure recovered/truth ≈ 1) — PASS (decisive).** PET unfolding MC-reco-as-
  pseudo-data recovers MC truth: total **0.9884**, per-axis median |Δ| **pt 1.14% / pz 1.13%
  / eavail 1.15% / q3 1.13%** (uniform). ⇒ the absolute-extraction machinery
  (`extract_cross_section_nd` + GBDT completeness + flux/POT/nucleons) is **unbiased**;
  `xsec_4d_PET_closure.root`.
- **Gate 2 (absolute PET vs GBDT) — PET total σ = 2.796e-38 vs GBDT 3.066e-38, ratio
  0.9117**; per-axis median |Δ| pt 7.69% / pz 9.88% / eavail 9.31% / q3 6.47%
  (`xsec_4d_PET_absolute.root`, `pet_vs_gbdt_absolute.png`). The ~9% gap is **larger** than
  the ML band — but since closure is exact to ~1%, it is a genuine **training-config**
  difference (PET trained on the 2M subsample, niter=2/epochs=8, vs the full-stats 5-iter
  GBDT), not a normalization bug. PET under-iterates → pushes the real-data result less far
  from the prior than the GBDT does.

**Milestone status:** the PET point cloud now yields a **real, absolutely-normalized,
full-statistics** cross section, validated unbiased by closure (~1%) and cross-checked vs
GBDT (~9%, training-limited). This completes the method milestone (full PET systematics
deferred, `../docs/FUTURE_DIRECTIONS.md`). Obvious next tuning (not required for the
milestone): retrain PET with more iterations/epochs/events to close the ~9% GBDT gap toward
the ML band before the systematics campaign.


## 2026-06-03 — Workstream D kickoff: q3 4th axis + NN track

Implemented `../docs/HIGHER_DIM_OMNIFOLD_DESIGN.md` end-to-end.

**Axis-list refactor + N-D math**
- `xsec_nd.py`: N-D extraction/projection on `np.histogramdd`. Self-tests pass,
  incl. bit-equivalence-to-<1e-12 vs the frozen `3d-unfolding/xsec_3d.py` and the
  4D q3-marginal→3D Jacobian identity (max rel 3.8e-16).
- `unfold_nd_omnifold_unbinned.py`: driver parametrized over an `EXTRA_AXES`
  registry (pt,pz fixed; eavail,q3 as configurable extra axes). `--axes eavail`
  reproduces 3D; `--axes eavail,q3` is the 4D unfold. Launched an `--axes eavail`
  reproduction on the existing 3D omnifile as the refactor's validation.

**C++ q3 (event loop)**
- Added `CVUniverse::RecoQ3()` (calorimetric, `LowRecoilFunctions::GetLowRecoilQ3`
  lineage) + used MAT `Getq3True()` for truth; dumped `sim_q3/MC_q3/measured_q3/
  sim_background_q3` in `runEventLoopOmniFold.cpp` (24 q3 touchpoints, symmetric
  with the eavail schema). Verified branches `MasterAnaDev_recoil_E`, `mc_Q2`,
  `mc_primFSLepton` exist in the raw tuples.
- Built (`make -j8 runEventLoopOmniFold` + `make install`, exit 0) → fresh
  `MINERvA101/opt/bin/runEventLoopOmniFold`.
- Smoke test on one 1A file: truth MC_q3 ∈ [0.05, 85] GeV median 1.77 (clean);
  reco q3 median sane (1.5–3.8 GeV) with large calorimetric tails (max ~1e5 GeV
  on pathological recoil) that the catch-all top q3 bin absorbs, mirroring reco
  Eavail. Confirmed RecoQ3/Getq3True run without error.
- Submitted the 12-playlist re-run: **SLURM 53905768** (array 1-12) →
  `runEventLoopOmniFold_4D_${PL}.root` (CV-only). Chained: **53906839**
  (afterok) hadds → `runEventLoopOmniFold_4D_MEFHC.root`, runs the 4D CV unfold
  `xsec_4d_MEFHC_5iter_lgbm.root`, the anchors (`check_4d_anchors.py`), and the
  injected-q3 closure.

**NN / point-cloud track (Phase 2)**
- Vendored `ViniciusMikuni/omnifold` → `../omnifold_nn/` (git clone; PET + MLP,
  keras/TF — the only linked repo with a point-cloud net). Env: no TF in the ROOT
  conda env, but `module load tensorflow/2.15.0` is available (matches the repo's
  `tensorflow>=2.15` req) and GPU-capable.
- `omnifold_nn_core.py`: ROOT-free keras-MLP (from the vendored `net.py`) behind a
  sklearn fit/predict_proba with standardization + the estimator-agnostic two-step
  loop. `omnifold.py` got an `estimator="nn"` branch delegating to it (lazy TF).
- NN-vs-GBDT cross-check (same loop, same inputs, swap classifier): leg 1
  **53906721** (CPU/ROOT) dumps `of_inputs_3d.npz` + runs the GBDT leg
  (`res_lgbm_3d.npz`); leg 2 **53906748** (GPU, afterok) runs the keras-MLP leg
  (`res_nn_3d.npz`).

**First results + two bug fixes (2026-06-04)**
- Event loop (53905768) completed all 12 playlists; hadd → `runEventLoopOmniFold_4D_MEFHC.root`
  (3.4 GB, POT summed correctly).
- **GBDT npz cross-check leg validated the whole new stack**: `omnifold_loop` (the
  ROOT-free copy of the two-step loop) on the dumped 3D inputs gives total σ =
  **3.0785e-38** — exactly the frozen 3D headline. This confirms the axis-list
  readers (`nn_dump_inputs.py` uses the driver's `collect_*`), `xsec_nd.py`, and the
  loop, independently of ROOT plotting.
- **Bug 1 (fixed): THnSparseD segfault.** The 4D unfold wrote `hXSecND_flat` then
  segfaulted in the 4D `THnSparseD` Python write (C-level, so the driver's
  `try/except` could not catch it), aborting before the projections/anchors/closure.
  Dropped the THnSparse path entirely — the flat TH1D (C-order ravel) + the TH2D
  marginal + 1D projections are the canonical outputs; N-D structure is recovered by
  reshaping with the known edges. Same crash had hung the login-node 3D-repro run.
- **Bug 2 (fixed): NN normalization collapse.** The keras-MLP leg ran end-to-end on
  GPU (TF 2.15, GPU found) and recovered the correct dσ/dpt,dpz,dEavail **shape**,
  but the absolute normalization collapsed to **2.7e-44** (~1e-6 of GBDT): the MLP
  sat at the trivial class-balance bias `p=W1/(W0+W1)` and never learned the x-density
  ratio. Fix: train the NN on class-BALANCED weights (`_balance_weights`) and restore
  the true normalization via `w=(W1/W0)·p/(1-p)` (`_class_ratio`); GBDT keeps raw
  weights (it calibrates the absolute ratio directly). This is exactly the failure the
  "validate NN vs GBDT before trusting it" gate is meant to catch.
- Re-running with both fixes: 4D unfold+anchors+closure (53925395), NN leg (53925396).

**Phase 1 (q3 4D) — VALIDATED (2026-06-04, job 53925395).**
`xsec_4d_MEFHC_5iter_lgbm.root`, d⁴σ/(dp_T dp_‖ dE_avail dq3), lgbm 5-iter, q3 edges
[0,0.2,0.4,0.6,0.8,1.2,2.0,100] GeV:
- completeness c = 1.0000; total σ (4D integral) = **3.066e-38 cm²/nucleon**.
- **Jacobian identity exact**: 2D (p_T,p_‖) marginal integral == 4D integral (3.0665e-38).
- **4D recovers the frozen 3D** (independently run): median rel diff dσ/dp_T 0.38%,
  dσ/dp_‖ 0.64%, dσ/dE_avail 1.68% (max 4.2%) — within ML/stat noise; adding q3 as a
  feature does not bias the lower-D projections.
- **2D-marginal anchors the paper**: 4D/3D = 0.9960 (3D = 3.0789e-38).
- New **dσ/dq3** spectrum produced, all-positive (not required to be monotonic).
- **Injected-q3-shape closure PASSES**: per-q3-bin ratios [1.007, 0.989, 1.005, 1.000,
  1.000, 1.000, 1.000] track the injected mean factor 1.0142 → 4D OmniFold recovers an
  injected q3 shape. `.err` clean (no THnSparse segfault).

**Phase 2 (NN) — 2nd attempt still collapsed; root cause found.** The class-balance fix
alone left the NN at ~0 (even slightly negative = float noise). Diagnosed the real
killer: keras `validation_split` takes the last 20% *without shuffling*, and the step
data is ordered [class0; class1], so the validation set was single-class and
early-stopping/`restore_best_weights` picked a degenerate epoch. Fix: permute before
`fit`. Re-running the NN leg with the shuffle fix (the GBDT leg remains the 3.0785e-38
reference).

**Phase 2 (NN) — VALIDATED (2026-06-04, job 53928526, GPU TF 2.15).** With the
class-balance + shuffle fixes, the keras-MLP OmniFold (same two-step loop, same 3D
inputs, swap classifier) reproduces the GBDT cross section **within the ML band**:
- total σ: NN 3.1024e-38 vs GBDT 3.0785e-38 → **ratio 1.0078** (0.8%).
- per-bin median rel diff: dσ/dE_avail **0.66%**, dσ/dp_T **1.20%**, dσ/dp_‖ **1.36%**
  (max deviations 2.8% / 7.9% / 24.7%, confined to sparse tail bins).
This green-lights the vendored NN engine for the point-cloud phase (the design-doc
gate: the NN must match GBDT on a known case before being trusted where no GBDT
baseline exists). Net conclusion stands: GBDT remains the production engine for scalar
axes (q3 included); the NN is the path for variable-length point clouds, now verified to
agree on tabular inputs. The two NN failure modes found + fixed (class-balance bias;
unshuffled single-class `validation_split`) are documented in `omnifold_nn_core.py` for
whoever drives the PET point-cloud track next.

## 2026-06-04 — Follow-on campaign: all six "next steps" (prepub items + q3 systematics + PET)

Driven by the `/goal` to do all six documented follow-ons, parallelizing across sbatch waits.

**#2 Ascencio low-q3 bin-identical overlay — DONE (code + our-side spectra).**
`compare_ascencio_q3.py`: reshapes the 4D `hXSecND_flat` and projects dσ/dq3 + the
d²σ/(dq3 dEavail) low-q3 slices via `xsec_nd`. Bin-identical χ² path verified end-to-end
with a synthetic drop-in (5 matched q3 bins). Our-side PNGs written
(`ascencio_vs_unfolded_q3_{dq3,eavail_in_q3slices}.png`). The Ascencio data file is the one
remaining drop-in — HepData is Cloudflare/member-gated (not fetchable in-session, same as the
E_avail script); format documented in the script header.

**#5 Unbinned goodness-of-fit — DONE (job 53945834).** `unbinned_gof.py`: Classifier
Two-Sample Test (Lopez-Paz & Oquab) between data reco and OmniFold-reweighted MC reco, with
the CV prior as the sensitivity baseline. Result on the frozen 3D inputs:
- PRIOR/CV: acc 0.5226, AUC 0.5353, z=33.4, p≈5e-244 (classifier easily separates data/MC).
- UNFOLDED: acc 0.5009, AUC 0.5014, z=1.36, **p=0.17** (statistically indistinguishable).
The unbinned GoF is both sensitive (caught the prior mismatch at z=33) and PASSES after
unfolding — OmniFold removes the detectable reco-space mismatch. Weights saved to
`of_weights_3d.npz`.

**#4 Train/test-split seedscan + ensemble-mean CV — DONE (array 53946279, 24 splits +
combine 53947036).** `omnifold_loop` gained `train_frac`/`split_seed` (fit each classifier
on a random 80% subset, evaluate on all) — the genuine ML knob, since LightGBM at the
production settings is otherwise ~deterministic in the estimator seed. `seedscan_split.py`
(per split) + `combine_seedscan_split.py` (ensemble mean + cov):
- ensemble-mean total σ = 3.0786e-38 (matches frozen CV 3.0789e-38); run-to-run 0.016%.
- ML-split cov: sqrt-trace 2.645e-40, median rel 0.51%. **1.24× the pure-seed ML cov** — the
  train/test split adds ~24% ML uncertainty the old seedscan missed (the prepub point).
- ensemble-mean vs frozen CV: median shift 0.28%. Wrote `uq_cov_mlsplit_3d.root`.

**#6 PET point-cloud DataLoader — DONE (job 53946101, GPU TF 2.15).**
`minerva_pet_dataloader.py` adapts our event-loop arrays to the vendored
`omnifold.DataLoader`. Smoke test on GPU: the vendored **MLP** AND **PET** (Point-Edge
Transformer) both unfold our MINERvA data end-to-end through `MultiFold` (finite weights,
mean≈1.0). `pointcloud` mode prints an actionable error listing exactly the per-hadron
branches the event loop must dump (`part_reco_{E,px,py,pz,z}`, `part_gen_{E,px,py,pz,pdg}`
from cluster info + `mc_FSPart*`). Point-cloud track is wired; the one remaining piece is
the event-loop per-hadron dump.

**#1 Unified-throw vs block-sum cross-check — IN FLIGHT (job 53946996).**
`compare_unified_throw.py` (superposition test): the unified throw equals the block sum in
the linear regime, so the decisive cheap test is the cross term
`Delta_AB - (Delta_A + Delta_B)` from re-unfolded vertical-band shifts. `--dump` reads the
120 GB 3D universes omnifile once (extended `collect_signal_nd`/`collect_truth_denom_nd`
with `extra_wbranches`); `--analyze` runs CV + single + joint unfolds for MaCCQE/2p2h/MaRES
and reports the cross-term / linear ratio. Restricted to vertical bands (lateral kinematic
shifts can't compose from single-band dumps).

**#3 q3 systematic campaign — LAUNCHED (chained pipeline).**
C++: `runEventLoopOmniFold.cpp` now dumps shifted q3 for lateral universes
(`q3_truth_/MC_q3_/sim_q3_<band>_<idx>`), mirroring pT/pz at all 3 sites. q3 is NOT
lateral-invariant (verified: reco q3 shifts for 100% of passing events under BeamAngleX, ±1σ
pair brackets CV; truth q3 invariant under beam-angle bands, matching truth pT/pz). Rebuilt +
installed. The nd driver gained a `--universe` path with the q3 swap (`lateral_invariant`
axis flag; eavail keeps CV, q3 swaps for lateral universes) + Flux-universe flux division.
Chain (all dependency-gated): evloop array 53945111 (12 playlists, dump-all +q3) →
hadd 53947173 (SetMaxTreeSize merger) → validation universe 53947729 (MuonResolution:0,
exercises the q3 swap) → full 187-universe sweep 53947731 → 4D covariance 53947732
(`analyze_universes_nd.py`, block-sum + norm band). Outputs land under `uq_4d/`.

### 2026-06-04 (cont.) — #4 follow-through: ML-split band in the combined budget
`compare_mlsplit_combined.py` (non-destructive): the train/test-split ML cov is 1.24x the
seed-only ML cov (sqrt-trace 2.131e-40 -> 2.645e-40), but ML is sub-dominant, so the
COMBINED 3D budget moves only +0.04% (sqrt-trace 5.7243e-39 -> 5.7265e-39; median rel
uncertainty 10.374% -> 10.370%). Conclusion: adopt the larger, more honest split-ML band —
negligible total cost, removes the "init-only ML proxy" caveat. (Ascencio data for #2 stays
member-gated: confirmed absent from HepData/in-session, the MINERvA data-release page, and
arXiv ancillary; the overlay is a one-file drop-in.)

### 2026-06-04 (cont.) — A/B/C parallel tracks + #1 result

**#1 unified-throw — COMPLETED (job 53946996), result needs the jitter caveat.**
The +1sigma superposition test (MaCCQE/2p2h/MaRES) found cross-term/linear of 25-58%
(largest MaCCQE x MaRES 58%, per-bin median 24-48%) -- NOT the clean "<10% => linear".
BUT at this magnitude the OmniFold run-to-run jitter floor must be subtracted before
claiming genuine nonlinearity (the difference-of-differences accumulates ~4x the per-unfold
jitter; the ML-split study found ~0.5%/bin). A jitter null-mode was added
(compare_unified_throw.py --null: a 2nd CV unfold at seed+1) and re-run (job 53953284) to
make the number interpretable. Honest status: the single-seed superposition test is a cheap
probe that flags possible nonlinearity; the rigorous object remains a many-throw unified
covariance (where jitter averages down). So #1's answer: block-sum linearity is NOT cleanly
confirmed -> a full unified-throw covariance is the recommended pre-pub study (as flagged).

**B — refreshed combined cov + generator chi2 with split-ML band (job 53950089).**
write_combined_splitml.py wrote uq_combined3d_splitml.root (syst+stat+ML_split). The
4-generator full-cov chi2 ranking is UNCHANGED (Tune-v1 best, GiBUU worst; diagonal chi2/ndf
identical, e.g. Tune-v1 4.8->4.8). The split-ML band raises the cov rank 247->261 and shifts
the truncated chi2 slightly but changes NO physics conclusion -- the robustness check passes.
(compare_3d_fullcov_{oldml,splitml}.png)

**C — NTRIAL ensemble-mean CV (ensemble_cv.py).** The #4 split trials ARE the NTRIAL
ensemble; ensemble_cv.py turns the 24 trials into the ensemble-mean CV product
(ensemble_cv_3d.root: hXSec3D_ensembleMean + hSigma3D_ensembleSpread). Ensemble spread
(ML band) median 0.51%/bin; ensemble-mean vs frozen single-run CV median shift 0.28%.
This is the rhuang1/OmnifoldT2K + Mikuni n_ensemble convention.

**A — per-hadron point cloud (Phase 3): C++ DONE + validated, full pipeline chained.**
CVUniverse::GetTruthFSHadrons (mc_FSPart*, muon+nu dropped) + GetRecoClusters
(ExtraEnergyClusters_*) feed a gated point-cloud dump in runEventLoopOmniFold.cpp
(MNV101_DUMP_POINTCLOUD=1, off by default): per-event part_gen_{E,px,py,pz,pdg} +
part_reco_{E,x,y,z} on signal, part_reco_* on data. Rebuilt + smoke-verified (gen <4.4>,
reco <6.75> per event; example particle E=1179 MeV pdg=2212 proton). Bug found+fixed: the
miss-append (AppendTruthOnlyMisses) must rebind the vector branches via pointer-to-pointer
to empty vectors, else Fill() reads the signal loop's freed locals -> segfault.
dump_pointcloud_inputs.py reads + zero-pads the vectors to num_part=12 (validated on the
smoke file: gen (N,12,5), reco (N,12,4)); minerva_pet_dataloader.py pointcloud mode reads
the resulting npz into the vendored PET. Chained (CV-only, cheap): evloop_pc 53953733 ->
hadd+dump 53953910 -> PET train 53953911.

### 2026-06-04 (cont.) — #1 jitter-null RESOLVES the superposition probe
Jitter null (job 53953284, compare_unified_throw.py --null): ||CV(seed+1)-CV(seed)|| =
3.76e-40, so the difference-of-differences jitter floor (x4) = 1.50e-39. The largest
measured cross term ||cross|| = 1.18e-39 is BELOW that floor (cross/floor = 0.8x). So the
earlier "25-58% cross/linear" is dominated by OmniFold run-to-run jitter, NOT genuine
cross-band nonlinearity. Corrected conclusion: the single-throw superposition probe shows
NO clean evidence of nonlinearity (it is jitter-limited) -> consistent with the block-sum
being valid; the full unified-throw covariance (160 throws, jitter averages down as
1/sqrt(T)) is the definitive test and is running (dump 53956788 done + bank verified ->
throws 53956789 -> combine 53956790).

### 2026-06-04 (cont.) — sweep I/O optimization + 4D combined budget prep (in-flight state)

**q3 sweep is I/O-bound, not compute-bound.** Single-universe unfold timing: npz path 10 min
(16 cpu), full ROOT-read path 35-40 min (32 OR 128 cpu) -> the ~25 min single-threaded
PyROOT GetEntry read dominates; cores past ~16 don't help. So the sweep was switched
regular/128 -> **shared/32/%32** (same per-job time, faster to schedule, ~4x cheaper).

**Read-once bank (sweep_bank.py).** Durable speedup for re-runs: one GetEntry pass per group
banks the 175 VERTICAL universes' weights (mmap'd) instead of 187 re-reads; stage-2 unfolds
read an mmap slice (~10 min, no 120 GB read) and write the sweep's filename + hXSecND_flat
with skip-if-exists. The 12 LATERAL universes stay on the per-universe path (they gate on
shifted kinematics -> different kept-set each). Canonical covariance stays single-code-path
(the shared sweep); the bank is for re-runs (iters/binning) + the 4D unified throw.

**4D combined budget chained.** dump 4D npz (53961411) -> {ML seedscan x24 (53961806),
stat bootstrap x100 (53961808)} -> combine (53961810) -> combined budget (53961846,
analyze_universes_nd --bootstrap-cov C_syst+norm+C_stat+C_ML). bootstrap_nd.py +
combine_cov_nd.py are the lean npz-based 4D stat/ML tools.

**IN-FLIGHT JOB IDS (for resumption):** shared q3 sweep 53960731 -> cov4d 53960732;
sweep-bank dump 53960918; unified-throw run 53956789 -> combine 53956790; point-cloud
pc_down 53953910 -> PET 53953911; 4D budget chain 53961411/806/808/810/846.

**#1 RESOLVED:** jitter-null showed the superposition cross-terms (25-58%) are AT the jitter
floor (0.8x) -> noise, not nonlinearity -> leans block-sum-valid; full 160-throw unified
covariance (running) is the definitive test.

### 2026-06-04 (cont.) — PET point-cloud: pipeline validated, reco-cluster branch WRONG (follow-on)
The Phase-3 PET run exposed (validate-as-it-lands working): (1) shape crash -- gen carried
pdg (5 feat) vs reco 4; fixed (drop pdg, per-step feat counts). (2) NaN loss -- raw scales;
fixed (x1/1000, multiplicative to keep the energy==0 mask, net.py:128). (3) DECISIVE: the
reco cloud is built from the WRONG branch -- ExtraEnergyClusters_* is 94.7% empty in MC and
100% empty in DATA (an auxiliary collection, not the recoil). So PET step-1 (reco) still
NaN's (every cloud masked-empty) and the PET result (push mean 0.30) is NOT trustworthy --
do not report any PET-vs-GBDT number from it. The gen cloud (mc_FSPart, 27% empty, mean 3.17)
is correct.
FIX (follow-on, needs event-loop re-run): CVUniverse::GetRecoClusters should read the real
per-cluster recoil collection -- `cluster_energy`, `cluster_pos`, `cluster_z` (217
clusters/event in data), filtering `cluster_isMuontrack==0` for the non-muon hadronic
clusters. Then rebuild -> re-run the PC event loop -> re-dump (dump_pointcloud_inputs) ->
re-run PET -> pet_vs_gbdt. The whole PET PIPELINE (engine, masking, scalar storage, dump,
comparison) is built + validated; only the reco-cluster source branch is wrong.

### 2026-06-04 (cont.) — unified-throw combine: ratio-product construction is ARTIFACT-prone
Ran the unified-throw combine on 145 throws: unified/block-sum sqrt-trace ratio = 25x, one
eigenmode ~1000x the block-sum's, median rel 17% vs 8%. This is NOT a block-sum refutation --
it is an ARTIFACT. Diagnosis: throw TOTALS are sane (median 2.88e-38, +-6.3%, no outliers),
so the inflation is in a few low-stat BINS, not normalization. Root cause: the throw
MULTIPLIES single-band reweight ratios (w_band/w_cv) across 13 bands; for events with small
w_cv and/or several bands in their tails this compounds into large per-event weights that
land in specific bins (and the 145 throws were produced BEFORE the 99.9pct weight-cap commit
acb0239). Multiplying single-band ratios is NOT equivalent to re-unfolding a genuinely
jointly-shifted sample, so its covariance is not trustworthy.
DECISION: do NOT report the 25x. The methodologically sound #1 cross-check is the jitter-null
SUPERPOSITION test (additive Delta on re-unfolded deltas), which found cross-terms at the
OmniFold jitter floor -> block-sum consistent. A RIGOROUS unified throw requires TRUE
multi-band universes (event loop applying all systematics together per universe) -> a
documented follow-on, not the ratio-product proxy. unified_throw.py keeps the bank/throw
machinery but its combine output carries this caveat.

### 2026-06-04 — CONSOLIDATED bugs & fixes (this campaign)
Single index of every bug/artifact found and how it was resolved (commit in parens):

CODE BUGS (fixed):
1. Unified-throw bank dump OOM (64G) — python-list ratio accumulators at 33M events x ~26
   cols. Fix: typed array('f')/('d')/('b') accumulators (~8x leaner) + 110G. (627a920)
2. Point-cloud miss-append segfault — AppendTruthOnlyMisses Fill() read the signal loop's
   freed local std::vectors. Fix: rebind the part_* vector branches via pointer-to-pointer
   to empty vectors (ROOT object branches need vector<T>**, not vector<T>*). (2ff1dd5)
3. PET step-2 shape crash (expected (12,4) found (12,5)) — gen cloud carried the pdg column.
   Fix: drop pdg + build m2 with the gen feature count. (617d378)
4. PET 'Last val loss nan' — raw feature scales (positions ~1000s mm). Fix: x1/1000
   MULTIPLICATIVE scaling (keeps the energy==0 particle mask, net.py:128). (617d378)
5. LightGBM degenerate-split error (best_split_info.right_count>0) on extreme throws. Fix
   (throw path only, canonical estimator untouched): 99.9pct weight cap + try/except skip.
   (acb0239); same guard added to 4D bootstrap/seedscan (NO cap there -- would bias stat/ML).
   (c70397e)
6. Misleading throw log (printed sum of differential bins ~1e-36, not the integral). Fix:
   log total_xsec. (ae47278)
7. write_combined_splitml relative-path bug (ran from genie/, needed ../). Fixed inline +
   re-run (B job 53950089). 
10. pc_down (dump_pointcloud_inputs.py) OOM-killed at 48G (MaxRSS 50.3G) after looping all
    32.8M signal events -- python LIST of 32.8M small (P,nfeat) clouds + the np.asarray copy
    coexist at the end. Fix (same family as #1): PREALLOCATE contiguous (n,P,nfeat) float32
    arrays, fill by index k, slice [:k] (signal+data); ~15G peak. Launcher also skips the
    re-hadd if the 46G merged omnifile exists + skips the dump if of_inputs_pc.npz exists +
    --mem 48G->96G. Re-launched pc_down 54014343 -> PET 54014344. evloop_pc array (12/12) had
    COMPLETED fine; only the downstream reducer OOM'd. (7c81032)
11. q3 bank sweep universe NormDISCC:0 (banksweep _158) FAILED "sample_weight contains NaN"
    in the LGBM step-2 fit. Root cause: the bank DUMP left 83727 NaNs in NormDISCC_0_wt.npy
    (DIS-norm reweight is 0/0 for events with no nominal DIS contribution); healthy universes
    have 0 NaN. Fix (sweep_bank.py run stage): np.nan_to_num(wt,wr,tdw, nan=0 ...) at load --
    an undefined reweight contributes 0; no-op on finite universes. Re-ran _158 -> 54021365.
    This is the 187th q3 universe that gates cov4d. (uncommitted as of 2026-06-05)

DATA/METHOD BUGS (found; one needs a follow-on):
8. PET reco cloud built from the WRONG branch -- ExtraEnergyClusters_* is 94.7% empty (MC)
   / 100% empty (data). Correct: cluster_energy/cluster_pos/cluster_z, isMuontrack==0.
   FOLLOW-ON (needs event-loop re-run); no PET-vs-GBDT number reported. (35b4130)
9. Unified-throw ratio-product combine ARTIFACT (25x vs block-sum) -- multiplying single-band
   reweight ratios compounds low-w_cv tail events; NOT a valid joint throw. NOT reported.
   Valid #1 = jitter-null superposition (block-sum consistent); rigorous = true multi-band
   universes (follow-on). (29b7676)

EARLIER SESSION (already documented in prior RUN_LOG / omnifold_nn_core / memory): 4D
THnSparseD write segfault (-> flat TH1D); NN class-balance bias + unshuffled validation_split
(-> _balance_weights + permute); xsec_nd ULP exact-equality (-> relative tolerance).

### 2026-06-04 — interactive sweep orchestration + IN-FLIGHT MANIFEST
Batch fairshare throttled to ~2 slots after running hundreds of jobs, so the q3 vertical
bank sweep was moved to an INTERACTIVE node: `run_q3_sweep_interactive.sh` runs INSIDE an
salloc (`salloc --qos interactive ... bash run_q3_sweep_interactive.sh`) and launches up to
10 concurrent `srun --overlap` sweep_bank --run steps (skip-if-exists -> resumable across
salloc windows). MONITOR BY OUTPUT-FILE COUNT, not the salloc stdout (it buffers; a working
run looked "stuck" and was wrongly cancelled once -- lesson logged). PC event loops can run
the same way (run_pc_evloop_interactive.sh) but were put back on batch for simplicity.

IN-FLIGHT MANIFEST (jobs that should be in squeue; anything else is unexpected):
  - q3 vertical sweep: INTERACTIVE salloc (run_q3_sweep_interactive.sh), 175 bank-unfolds
  - q3 lateral: batch unfold4d_lat (sbatch_unfold_4d_lateral.sh), 12 driver unfolds
  - PC chain: batch evloop_pc -> pc_down -> PET (sbatch_evloop_array_pointcloud/pc_downstream/pet_train)
  - 4D stat: batch boot4d (sbatch_bootstrap_4d.sh) x100
  - 4D ML:   batch ssplit4d (sbatch_seedscan_split_4d.sh) x24
  - 4D stat+ML combine: batch comb4d_statml (afterok boot+ssplit)
  - q3 cov4d + 4D budget: run MANUALLY (analyze_universes_nd + combine_4d_budget) once all
    187 q3 universe files are present (the chained batch versions were cancelled in the
    interactive switch to keep the queue free of doomed-dependency zombies).

### 2026-06-06 — PET point-cloud refresh completed with corrected reco-cluster source
Reason for rerun: `pet_vs_gbdt.png` was stale because the first point-cloud chain used
`ExtraEnergyClusters_*`, which the 2026-06-04 audit found to be 94.7% empty in MC and
100% empty in data. Source inspection showed `CVUniverse::GetRecoClusters()` now uses the
real cluster collection (`cluster_energy`, `cluster_pos`, `cluster_z`) and filters
`cluster_isMuontrack`, so the stale artifact was replaced by a full point-cloud refresh.

CPU side was run inside the current interactive allocation, not as a new batch array:
rebuilt/installed `runEventLoopOmniFold`; reran all 12 point-cloud playlist event loops
with `MNV101_DUMP_POINTCLOUD=1`; `hadd` rebuilt
`runEventLoopOmniFold_PC_MEFHC.root` (46 GB, timestamp 2026-06-05 19:26 PDT);
`dump_pointcloud_inputs.py --num-part 12` rebuilt `of_inputs_pc.npz` (5.5 GB,
timestamp 2026-06-05 19:59 PDT). The dump reported:
`signal clouds: gen (32849103, 12, 5), reco (32849103, 12, 3); data
(4091707, 12, 3); num_part=12`. Existing merged/NPZ artifacts were archived with
`.stale_20260606T005039Z` / `.stale_20260606T022515Z` suffixes as applicable.

GPU PET training and comparison then completed:
- PET training job 54033990 (`pet_train`, gpu_shared): COMPLETED 0:0, 00:58:24.
  It ran the real point-cloud `MultiFold` on 2M events, with
  pass_reco=0.621, pass_gen=1.000, and saved `pet_weights.npz` (14 MB). Final smoke
  line: unfolded weights n=2000000, mean=1.0004, std=0.1157, finite=True.
- PET-vs-GBDT comparison job 54033991 (`pet_cmp`, shared): COMPLETED 0:0, 00:00:30.
  It archived the previous plot as `pet_vs_gbdt.png.stale_20260606T061012Z` and
  regenerated `pet_vs_gbdt.png` (109 KB, timestamp 2026-06-05 23:10 PDT).

Refreshed PET-vs-GBDT area-normalized shape median |diff| values:
- pT: 3.86%
- pz: 2.36%
- Eavail: 2.63%
- q3: 2.33%

Interpretation: with the corrected reco-cluster source, the point-cloud PET shape agrees
with the scalar 4D GBDT result at the few-percent level on the PET subsample. This is a
valid refreshed method/shape cross-check. It is not an absolute normalization measurement:
`pet_vs_gbdt.py` intentionally area-normalizes because the PET training uses a subsample.

---

## 2026-06-07 — Workstream E (PET hi-iter retrain) + Workstream F (W 5D unfold) landed

Both in-flight job chains from 2026-06-06 completed and validated.

### Workstream F: W (hadronic invariant mass) as 5th axis — 5D unfold PASS

5D CV event-loop array `evloop5d` (54062311, 12 playlists) COMPLETED, then
`hadd_unfold_5d` (54062313) merged -> `runEventLoopOmniFold_5D_MEFHC.root` (4.5 GB) and
ran the `--axes eavail,q3,W` (5D = pt,pz,eavail,q3,W) unfold (5 iter, lgbm):

- total sigma (5D integral): **3.07e-38 cm^2/nucleon**
- W-marginal -> frozen 4D anchor: **5D/4D = 1.0011** (PASS, <3% target). Per-shared-axis
  median |5D-4D|/4D: pt 0.68%, pz 0.31%, eavail 0.91%, q3 1.48% (max 4.22%). Adding W as a
  feature does not bias the lower-D projections or the total (same discipline as 4D/3D=0.9960).
- new dsigma/dW: 6 bins, all-finite, nonneg, integral 3.07e-38 (consistent with total).
- injected-W-shape closure (`closure_5d_Wbump.root`, A=0.3 bump): **median 1.0000, std 0.0062,
  max|dev| 0.227**; W 1D ratios all 1.000; injected mean factor 1.0000. The 5D machinery
  recovers an injected W shape without bias.

Artifacts: `xsec_5d_MEFHC_5iter_lgbm.root`, `closure_5d_Wbump.root`. The W axis is now a
validated 5th dimension; the 187-universe W systematic campaign remains deferred (binary
already dumps shifted W under MNV101_DUMP_UNIVERSES — no new code needed).

### Workstream E: higher-iteration PET retrain (niter5/epochs10/4M)

`pet_train` (54060166, gpu_shared) COMPLETED 05:53:53 — trained the real point-cloud MultiFold
on 4M events, then ran the **full-stats reweight-all** push-weight evaluation:
- unfolded (train) weights n=4,000,000 mean=1.0101 std=0.1631 finite=True
- full-stats w_push n=**32,849,103** mean=1.0101 std=0.1630 finite=True -> `pet_weights_full_hi.npz` (137 MB)

`pet_xsec` (54060169, CPU) COMPLETED — absolute extraction reusing the frozen GBDT
`hCompletenessND`:
- PET total sigma (4D) = **2.751e-38** cm^2/nucleon (n_truthpass=32,849,103, data_pot=1.057e21)
- GBDT total sigma = 3.066e-38; **PET/GBDT = 0.8970**
- per-axis median |diff| (ABSOLUTE): pt 7.52%, pz 11.57%, eavail 11.08%, q3 6.83%

Artifacts: `xsec_4d_PET_absolute_hi.root`, `pet_vs_gbdt_absolute_hi.png`.

Interpretation: the higher-iteration/epoch/larger-subsample retrain did **not** close the
~10% absolute PET/GBDT normalization gap (0.9117 at niter3/2M -> 0.8970 here); it is
essentially flat. This is consistent with a training-configuration / point-cloud-vs-scalar
architecture difference rather than a bug in the absolute machinery — the absolute extraction
path itself is validated by the clean closure (recovered/truth ~0.99) from the milestone run.
Closing the gap toward the ML band would require a PET-specific systematic/ensemble campaign
(deferred, docs/FUTURE_DIRECTIONS.md), not more iterations of a single training.

---

## 2026-06-07 — (E_avail, W) excess test: open question 6 is DIS-like (high-W)

`excess_eavail_W.py` (job run on interactive node nid004154, ~min) compares the unfolded
5D data cross section to the **GENIE CV prediction** (the OmniFold prior = POT-scaled
`mc_truth_denom`, completeness=1, pushed through the SAME `extract_cross_section_nd`) in the
(E_avail, W) plane. Single I/O pass over the 4.5 GB 5D omnifile (kept 32,846,302 truth events).

**Overall:** data/CV = 1.135 (the known ~13% integrated excess over GENIE CV).

**dσ/dE_avail data/CV rises toward high E_avail** — 1.18, 1.15, 1.09, 1.03, 1.11, 1.17,
**1.22** across the 7 bands; the two highest-E_avail bands (1.5–3.0, 3.0+) carry 25.3% + 31.8%
= **57% of the total positive excess**. This is open question 6's +2.2σ high-E_avail excess
at central value.

**WHERE in W (the new information):** the high-E_avail excess is **predominantly high-W
(DIS/transition)**. Of the positive excess, high-E_avail (≥0.8 GeV) carries **67.2%**, and
**83.2% of that sits at W≥1.8 GeV**. The single largest excess cell is the deep-DIS corner
(E_avail>3, W>3) at **21.9%** of all positive excess; (E_avail 1.5–3, W 1.8–2.2)=10.6% and
(E_avail 1.5–3 / 3+, W 2.2–3)=8.6%/7.1% follow — all high-E_avail × high-W. So the missing
strength behaves like a **deep-inelastic-tail modeling deficit**, exactly the hypothesis the
W axis was added to test.

**Secondary structure:** a low-W (W<1.1) excess of ~24–31% above CV across all E_avail (a
QE-like component, ~25% of positive excess but spread thin), and a localized **deficit**
(data<CV, ratio ~0.89–0.96) at W 1.4–1.8 for low/moderate E_avail (the Δ-resonance region) —
GENIE CV slightly over-predicts there.

**Caveat:** this is vs the GENIE CV only (single generator, no systematic covariance) — it
localizes the central-value excess, it does NOT re-derive the +2.2σ significance. Extending
to NuWro/GiBUU in (E_avail, W) (the `3d-unfolding/genie/` machinery run through W) is the
follow-up to turn this into a generator-band statement. Artifacts:
`products/5d/excess_eavail_W.{root,png}`.

## 2026-06-08 — Three-campaign closeout (PET 4D cov + (E_avail,W) generator band + rigorous unified throw)

Driven under a `/goal` to complete all three recorded follow-ons in parallel. Branch
`nd-campaign-genband-petsyst-uthrow` (off main after the 2026-06-07 work landed). Two
correctness saves this session: (i) `bank_uthrow` stores per-event universe/CV **ratios**
(median 1.0), NOT absolute weights — caught before it inflated both new covariances ~5×;
(ii) on interactive nodes LightGBM oversubscribes all cores across parallel procs (≈0 progress)
— sbatch's cgroup limit (16 cores/task) is required, so all the heavy re-unfolds run via sbatch.

### A. PET 4D combined covariance — `pet_systematics.py` → `products/pet/pet_4d_covariance_combined.root`
Publication-grade completion of the PET milestone (FUTURE_DIRECTIONS Sec 0). Frozen-reweighter
path: the trained full-stats PET push weights (`pet_weights_full.npz`) are held fixed and
re-binned per **reweight** universe (no per-universe re-inference — reweight universes share the
clouds), with the per-event ratios from `bank_uthrow` (verified bit-identical gen ordering to
`of_inputs_pc.npz`, w_truth diff = 0 over 32.85M events) and the CV completeness anchored to the
validated GBDT `hCompletenessND` (median rescale 1.215 → CV total σ 2.80e-38, matches milestone).
**Budget, median per reported bin (4796 bins):** C_syst **18.3%** (block-sum, 12 GENIE knobs +
100 flux universes, flux-dominated), C_stat **4.2%** (100 Poisson bootstraps), C_ML **3.3%**
(CV-vs-hi-iter training spread), **C_total 22.4%** — same syst>stat>ML hierarchy as the GBDT 4D
budget. Lateral (kinematic-shift) universes are the one approximation (frozen reco clouds).

### B. (E_avail,W) generator band — `3d-unfolding/genie/`, `overlay_eavailW_band.py` → `eavailW_band.{png,root}`
Turns open question 6 from a single-generator localization into a **generator-band statement**.
Regenerated GENIE-CV (2M, `gevgen`), GENIE+Valencia-MEC (1.5M), and NuWro (2M; native Enu threaded
through `nuwro_to_flat.C` for an experimenter's-W branch — verified, NuWro W median 1.92 GeV). New
`gen_to_xsec_eavailW.py` / `nuwro_to_xsec_eavailW.py` bin each onto the data's (E_avail,W) axis
(spline / per-event normalisation; W replicates `GetTrueExperimentersW`). **Result: the high-W
DIS excess is generator- AND tune-robust.** All three underpredict the high-E_avail×high-W corner
by 54–58% (data/gen = 1.54 CV, **1.58 +MEC**, 1.56 NuWro); enabling Valencia 2p2h does NOT close
it — it slightly **worsens** the corner (2p2h is low-W) — and NuWro misses it by the same margin.
At W∈[2.2,3.0) all three sit 23–25% below data (data 7.48e-39 vs 5.62–5.76e-39). GiBUU excluded
(`FinalEvents.dat` lacks per-event Enu). Propagated to technote item 6 + FUTURE_DIRECTIONS Sec B.

### C. Rigorous unified-throw covariance — `unified_throw_cov.py` → `uq_4d/unified_throw_cov.root`
The methodologically sound replacement for the artifact-prone ratio-product proxy (2026-06-04):
compose per-**event** weights `w_cv·∏_b ρ_b^{g_b}` (g_b~N(0,1) over the 12 reweight knobs) + one
sampled flux universe, then **re-unfold** each throw (OmniFold), and build the covariance directly
— the construction a true multi-band event-loop universe would produce, for the reweight bands.
75 throws (sbatch array + interactive, incremental-saved) vs a parallel block-sum (12 knobs + 12
flux units). **Result: sqrt-trace unified/block = 1.40 (per-bin σ median 1.16).** A jitter null
(2nd CV unfold) shows the OmniFold run-to-run floor is tiny (sqrt 3.07e-40, ~10× below the
cross-term), so the **jitter-corrected ratio is still 1.40** — the excess is real, not a seed
artifact. So the iterative unfolding combines the systematic bands with a significant **positive
nonlinear cross-term** (97.6% of the block-sum trace) that the block-sum drops: **the block-sum
underestimates the systematic covariance by ~16% per bin (robust median) to ~40% in sqrt-trace.**
This refines the prior single-throw probe ("cross-terms at the jitter floor → leaned block-sum
valid"); the full 12-band joint throw reveals the aggregate nonlinearity the pairwise probe could
not. Caveat: the median (1.16) is the robust statement; the larger sqrt-trace (1.40) is partly
driven by a few high-variance bins where Gaussian-tail throws compound several knobs. The unified
throw is the more conservative, correct object. Artifacts: `uq_4d/unified_throw_cov.root`
(C_unified, C_blocksum, C_cross), throw + block slabs under `uq_4d/uthrow_slabs/`.

## 2026-06-08 (cont.) — Four-extension campaign LAUNCH (rigorous follow-ons to the closeout)

Under a `/goal` to accomplish all four post-closeout extensions. Deep scoping first established
that the cheap shortcuts are blocked by data-alignment gaps (the PC bank, the 5D/W omnifile, and
the stored throw slabs use different event orderings / lack the needed columns), so each extension
needs either an event-loop/generator re-run or a careful bank reconstruction. New code written this
session: `dump_td_q3.py`, `assemble_bank_4d.py`, `pet_lateral_correction.py`,
`3d-unfolding/genie/gibuu_to_xsec_eavailW.py`, launchers `sbatch_td_q3.sh`, `sbatch_assemble_4d.sh`,
`sbatch_uthrow_{cov,block,combine}_4d.sh`, `sbatch_evloop_array_5d_universes_full.sh`,
`sbatch_pet_lateral.sh`, `sbatch_gibuu_mirror.sh`; `compare_unified_throw._xsec_for_weights`
generalized to an N-D truth-denom stack (4D-ready, 3D back-compatible).

### Task 14 — rigorous 4D unified throw (the 3D run was a probe). LAUNCHED, self-contained.
The 3D unified throw measured block-sum underestimation (1.16 median / 1.40 trace) on a coarse
(pt,pz,eavail) grid. To adopt it for the published 4D covariance it must live on the real
(pt,pz,eavail,q3) binning. The throw machinery is binning-agnostic (`d["edges"]` from the bank);
the only missing column was the truth-DENOMINATOR q3 (`bank_uthrow` is 3D). `dump_td_q3.py` recovers
it in one I/O pass over the 4D `_universes_full` omnifile's `mc_truth_denom` (collect_truth_denom_nd
is deterministic -> same ordering; the dump ASSERTS td_w bit-identity to the bank before writing).
`assemble_bank_4d.py` then builds `bank_uthrow_4d/` (q3 from the PC cloud -- verified max|diff|=0 to
the bank rows; data 4D from `of_inputs_4d`; weight arrays symlinked, binning-independent). Chain:
`td_q3`(54189950) -> `asm4d`(54190008) -> 4D throw array + block array -> combine ->
`uq_4d/unified_throw_cov_4d.root` (C_unified_4d/C_blocksum_4d/C_cross_4d, jitter-null corrected).

### Task 15 — PET lateral band, engine-independent. LAUNCHED (`pet_lat` 54190130).
The PET 4D budget froze the reco clouds, so lateral (detector-response) universes contributed ZERO
(its one approximation). `pet_lateral_correction.py` transfers the GBDT-measured lateral FRACTIONAL
covariance (sum of the 6 detector bands from `uq_universe_4d_covariance_combined.root`) onto the PET
bins via the shared 10976-cell grid: laterals are pure detector response, ~independent of the GBDT-vs-
PET density-ratio step, so the fractional response transfers. Adds `C_lateral` + refreshes `C_total`
in `products/pet/pet_4d_covariance_combined.root`. Full per-lateral PET re-inference (re-dump lateral
reco clouds + GPU re-inference) recorded as the residual deferral.

### Task 13 — generator-band significance via the (E_avail,W) covariance. GATING STEP LAUNCHED.
The fully-rigorous (E_avail,W) systematic covariance needs universe weights on the W-carrying events;
the 5D omnifile is CV-only and the W axis postdates the 4D systematic campaign, so the gating step is
a 5D `_universes_full` event-loop re-run (`ev5duni` 54190271, MNV101_DUMP_UNIVERSES, ~24h; the binary
already dumps shifted W). Confirmed NOT needing the multi-day 187-universe re-unfold sweep: the
completion path is the frozen-reweighter block-sum on the (E_avail,W) marginal (same methodology as
`pet_systematics`) + stat bootstrap + transferred lateral, then chi^2/significance of data vs each
generator in the high-W DIS corner (turns "data/gen=1.54" into N-sigma). [Tried + rejected cheaper
paths: PC-bank<->5D-omnifile scalar matching (orderings differ), and per-event W reconstruction from
the truncated 12-particle PC cloud (biased: W piles up 2.3x at W<1.1 and 1.9x at W>3).]

### Task 16 — GiBUU as the 4th band generator. LAUNCHED (`gibuu_mir` 54190366 -> regen).
The real blocker was that FinalEvents.dat was deleted in the cleanup (NOT a missing Enu -- col 15 IS
enu, the muon is ID 902, so experimenter's W is computable with no format change). `gibuu_mirror`
rebuilds the cleaned-up buuinput short-path mirror (CVMFS, compute node) then submits the 80-run regen;
`gibuu_to_xsec_eavailW.py` (written) bins it into (E_avail,W). Lowest-value extension (the band is
already 3-generator robust at 54-58% corner deficit) -- run as low-priority confirmation.

### Task 15 RESULT (DONE 2026-06-09) — PET lateral band folded in.
`pet_lateral_correction.py` transferred the GBDT lateral (6 detector bands) FRACTIONAL covariance
onto all 4796 PET reported bins (full 10976-grid overlap, 0 missing). Sanity: the transferred PET
lateral median frac (4.03%) matches the source GBDT lateral (4.02%) -- the fractional map preserved
magnitude. Updated PET 4D budget (median frac/bin): syst 18.31% / stat 4.18% / ML 3.32% / **lateral
4.03%** -> **TOTAL 23.02%** (was 22.4% with lateral=0). Small, as expected (lateral is subdominant),
but closes the one zero in the PET budget. `products/pet/pet_4d_covariance_combined.root` now carries
C_lateral + refreshed C_total. Residual deferral: full per-lateral PET reco-cloud re-inference.

### Task 13 INTERIM RESULT (2026-06-09) — dsigma/dEavail generator significance (the E_avail projection).
`eavail_generator_significance.py` marginalizes the published 4D combined covariance
(uq_universe_4d_covariance_combined, syst+stat+ML) to the E_avail axis via the project_marginal
linear map (C_y = M C_4d M^T, 7x7) and does a full-covariance chi^2 of data vs each generator's
dsigma/dEavail (the band files' hXSec_eavail). **The unfolded data is incompatible with all three
generators at high significance:** chi^2/ndf(7) = 725/7 (GENIE-CV), 865/7 (GENIE+MEC), 665/7 (NuWro)
-> nominal 25-29 sigma. Honest reading (diagnostics in-script): C_y is correlation-dominated
(condition number 8.7e5, smallest eigenvalue carries the shape direction), so the chi^2 lives in the
shape directions. Per-bin pulls (data-gen)/sqrt(diag) for GENIE-CV: [1.5, 7.7, 5.3, 0.8, 1.6, 4.5,
18.6] with data/gen ratio [1.07, 1.35, 1.18, 1.03, 1.05, 1.16, **2.41**]; the deep-DIS catch bin
[3,100] GeV dominates (18.6 sigma, data/gen 2.4x) BUT the result is robust to dropping it (~10 sigma
from the resolved bins: 7.7 sigma at 0.1-0.2, 5.3 at 0.2-0.4, 4.5 at 1.5-3.0). NuWro similar (broad,
+pulls at low AND high E_avail). So the open-question-6 excess is now a HIGH-SIGNIFICANCE,
multi-generator, full-covariance statement on the E_avail projection -- a broad excess strongest in
the DIS tail. Caveat: the [3,100] catch-bin uncertainty drives the headline number; the W-resolved
corner significance (which W cell) follows from the 5D `_universes_full` campaign (ev5duni, ~24h) ->
the (E_avail,W) covariance. GiBUU pending its regen. Run via the interactive allocation (alloc_run.sh)
because the shared sbatch QoS was backlogged -- per the /goal's short-job guidance.

## 2026-06-09 — Four-extension campaign RESULTS (compute landed)

The four-extension jobs launched the prior session all landed. Results below; tasks 14, 15, 16
DONE, task 13 W-resolved covariance running (`ew_cov` 54221942 afterok the 5D merge 54221741).

### Task 14 RESULT (DONE) — rigorous 4D unified throw + ADOPTED as the published 4D systematic.
The 160-throw 4D unified-throw covariance landed on the real (pt,pz,eavail,q3) analysis binning
(`uq_4d/unified_throw_cov_4d.root`; combine log `uq_4d/uthrow4d_comb_*.out`). Jitter floor is
negligible (sqrt 2.12e-39). **Jitter-corrected unified/block sqrt-trace = 2.01** (raw 2.01), i.e.
the block-sum UNDERESTIMATES the vertical systematic by ~2x in trace -- STRONGER than the 3D probe
(1.40). Per-bin sigma median ratio is 1.004, so the inflation is CONCENTRATED, not broad: the
variance-excess top 1% of bins carry 78% / top 5% carry 100% of the trace excess, and they are all
the **high-pT (pt bins 4-5), lowest-E_avail (0.0-0.1 GeV) corner** -- exactly where the migration
matrix is most off-diagonal and bands couple nonlinearly. p90 sigma ratio 1.60, p99 3.02, max 15.5.
Physically credible (not numerical pathology).

ADOPTION (`adopt_unified_4d.py` -> `uq_4d/.../uq_universe_4d_covariance_combined_uthrow.root`):
directly swapping the rank-160 C_unified into the 4830-bin combined breaks PSD (2285 neg eigenvalues,
most-neg = -1.25% of max), because 160 throws << 4830 bins is a noisy full-matrix estimate. So we
adopt the throw's per-bin MAGNITUDE (which converges fast and carries the cross-term) by transferring
its fractional inflation g_i = max(sigma_uni,sigma_blockbank)/sigma_blockbank >= 1 onto the SWEEP's
own vertical block: C_new = (C_comb - C_vert_sweep) + G C_vert_sweep G -- PSD by construction (verified
min-eig = -2.3e-16 of max = float roundoff). This is the same engine-independent fractional-transfer
logic as the task-15 PET lateral. Published 4D combined cov sqrt-trace 2.10e-38 -> 3.85e-38 (x1.84),
median frac/bin 13.5% -> 14.9%. The conservative max() never under-covers vs the block baseline.

### Task 16 RESULT (DONE) — GiBUU as the 4th band generator.
All 80 GiBUU FinalEvents.dat regenerated (the cleanup had deleted them; col 15 IS Enu, muon ID 902 ->
W computable, no format change). `gibuu_to_xsec_eavailW.py` binned 913,859 in-PS events -> (E_avail,W)
2D xsec, total sigma 2.22e-38 cm^2/nucleon (the MOST deficient generator, matches the validated smoke
test). `gibuu_cv_xsec_eavailW.root` has hXSec_eavailW (TH2D), hXSec_eavail, hXSec_W.

Re-ran `eavail_generator_significance.py` with all 4 generators AND the now-published unified-throw
4D cov (`..._uthrow.root`, hCov_combined4d_total_uthrow): the larger rigorous cov reduces the headline
(GENIE-CV 26.3->22.4 sigma) -- more conservative & honest. dsigma/dEavail: all four miss the data at
>21 sigma overall, >15 sigma in the DIS tail (E_avail>=0.8). GENIE-CV 532/7=22.4s, GENIE+MEC
652/7=24.9s, NuWro 513/7=21.9s, **GiBUU 481/7=21.2s**. Notably GiBUU spreads its deficit across the
WHOLE DIS tail (per-bin pulls 12.3/7.9/12.8 at E_avail 0.8-1.5/1.5-3.0/catch; data/gen 1.59 at
0.8-1.5, 1.36 at 1.5-3.0, 1.91 catch) rather than piling in the catch bin like the GENIE variants --
a qualitatively different, generator-robust confirmation of the high-E_avail excess.

### Task 13 (W-resolved) — DONE. (E_avail,W) frozen-reweighter covariance.
The 12 5D `_universes_full` omnifiles (133 GB) were merged (SetMaxTreeSize, 4.6 min on the
interactive alloc); `eavailW_covariance.py` does ONE CV 5D unfold for the frozen push weights and a
frozen-reweighter block-sum over 13 knob + 100 flux universes (re-binning, no re-inference -- same
methodology as pet_systematics), + diagonal stat + transferred 4D laterals, projects to the
(E_avail,W) marginal, and computes chi^2 / N-sigma of unfolded data vs all 4 generators'
hXSec_eavailW, including a high-W DIS corner sub-block (E_avail>=0.4 & W>=1.8 GeV).

**BUG CAUGHT BY THE SELF-VALIDATION GATE (then fixed):** the first full-stats run failed validation
at max|ratio-1|=1.44 -- the CV (E_avail,W) total came out 5.99e-38 vs the frozen 5D product's
3.07e-38 (~1.95x over-normalization). Diagnosis: `marginal_ew` was proven correct (it reproduces the
frozen product's own projection to ratio 1.000/bin), isolating the fault to `xsec_ew()` completeness:
the numerator was built from RECO-PASS truth events only, but the validated N-D driver
(unfold_nd_omnifold_unbinned.py:642) uses ALL truth-pass events because OmniFold step2 already does
the efficiency correction in truth space (so completeness ~1, signal/truth_denom phase-space match).
The reco restriction double-counted the efficiency -> xsec inflated by ~1/c. Fixed `of_in` to bin the
full truth-pass set. The re-run validates at max|ratio-1|=0.001 (CV total 3.070e-38). Without the
gate this would have put the data ~2x above every generator and produced fake >40-sigma significances.

**RESULT** (`products/5d/eavailW_covariance.root`: C_syst, C_stat, C_lateral, C_total, hData_ew):
C_total sqrt-tr 8.65e-39, **median 14.8%/bin** (MaRES/MvRES/MaCCQE-dominated; flux sqrt-tr 3.44e-39).
Generator chi^2/ndf over the full 42-bin (E_avail,W) plane: GENIE-CV 412.7/42 (16.7s), GENIE+MEC
390.5/42 (16.1s), NuWro 1148.4/42 (31.2s), GiBUU 1930.2/42 (>37s). **High-W DIS corner** (12 bins,
E_avail>=0.4 & W>=1.8 GeV): GENIE-CV 116.9/12 (9.0s), GENIE+MEC 121.1/12 (9.2s), NuWro 149.6/12
(10.5s), **GiBUU 381.1/12 (18.2s = most deficient)**. The excess is a genuine high-W DIS-region
feature (W>~1.8 GeV), not a low-W resonance artefact -- open question 6 is fully W-resolved. All four
extensions (13/14/15/16) now complete.

## 2026-06-19 — PET capstone campaign kickoff: raw-data unbinned unfolding beyond the measured phase space

User-directed campaign kickoff. Headline goal: push the PET point-cloud
OmniFold to a raw-data unbinned unfold beyond the measured (published)
phase space, in two steps. **Step 1**: full-statistics PET training to
close the residual PET-vs-GBDT CV gap (PET/GBDT 4D total ratio 0.9117, a
"~9%" gap per the existing rebank ledger entry). Kicked off with a timing
probe, job **54727164** (`sbatch_pet_train.sh`, since removed from the repo
by a later cleanup and superseded by the horovod launchers
`sbatch_pet_train_hvd.sh` / `sbatch_pet_train_fps_hvd.sh`): single-GPU,
`train=2000000` real point-cloud MultiFold per `pet_train_54727164.out`;
COMPLETED 15:56:15-16:10:39 (~14 min). **Step 2**: FPS-on-raw-inputs
capstone — re-dump with the truth muon phase-space cuts removed and run the
trained PET on the raw reconstructed clusters; flagged from the outset as
carrying NN-extrapolation risk beyond the training distribution, so a
3-prior systematic envelope (as already used in the 2D/5D FPS campaigns) is
mandatory before any FPS-PET number is quoted.

## 2026-06-28/29 — Truth-cloud coverage fix + full-cloud re-dump (Tier 2 landed)

Three commits landed the fix and its validation:
- **8cc54e9** (2026-06-28 12:31) `fix: fill truth FS-hadron cloud on
  truth-only miss rows` — `AppendTruthOnlyMisses` had been leaving
  `part_gen_*` empty on truth-only miss rows (conflating the correctly-empty
  reco cloud with the truth cloud, which does exist for a truth-pass event).
  Fixed in `runEventLoopOmniFold.cpp`: the truth-denom loop now caches the
  truth FS-hadron cloud via `GetTruthFSHadrons()` (the same accessor the
  signal loop uses), and `AppendTruthOnlyMisses` fills `part_gen_*` per miss
  row from that cache (`part_reco_*` stays empty — a miss has no reco
  clusters). Smoke-validated on playlist 1L: all 111,642 appended miss rows
  now carry a non-empty truth cloud (was ~0%).
- **8e79ebf** (2026-06-28 12:52) `pipeline: full-cloud re-dump chain
  (Tier 2)` — orchestration to realize the fix on production inputs under
  `*_fullcloud` names (hadd/npz/retrain/reproject), non-destructive to the
  baseline comparison files.
- **ddf4a7d** (2026-06-29 06:00) `note: reframe truth-cloud projection as
  coverage-fixed` — reframed the technote projection subsection from
  limitation to resolved.

Validation artifact
`nd-unfolding/products/pet/fullcloud/pointcloud_projection_summary.json`
(full-spectrum event census, N=**32,849,103**): pass_truth_and_reco
20,404,292, truth_only_miss 12,444,811, **has_cloud 32,848,929 / empty_cloud
174** (99.9995% coverage, was ~72.6% pre-fix per the commit message). E_avail
truth-cloud projection is now essentially unbiased vs the published unfold:
frac_within **98.78%**, RMS **0.0822**. W is NOT projectable from the
(12-hadron-truncated) cloud: frac_within only **19.7%**, RMS **3.24 GeV** —
the truncation that's fine for E_avail is not fine for W. Saturated
(exactly-12-hadron-truncated) rows are **2.31%** of the sample
(757,968/32,848,929) and carry a median E_avail bias of **-0.0355** — the
dominant residual source, small and confined to the truncated tail.

## 2026-06-29 — 5D GBDT systematic covariance campaign COMPLETE: Models/2p2h overtakes Flux as the dominant band

The 5D (pt,pz,Eavail,q3,W) universe sweep drained and the combined
covariance landed (`uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt`,
written 2026-06-29 07:23): **10694/65856 reported bins**; total systematic
**sqrt-trace 4.3391e-38, median 13.298%/bin**; combined (+stat+ML)
**sqrt-trace 4.3460e-38, median 13.433%/bin**. Per-band-group sqrt-trace
sums: Models **9.013e-38**, Hadronic response 3.885e-38, Muon reconstruction
2.742e-38, Normalization 4.507e-39, **Flux 3.875e-39**. Adding the W axis
flips the dominant systematic group from Flux (2D/3D/4D) to **GENIE
Models/2p2h** — Flux is now sub-dominant by more than an order of magnitude
in trace. New scripts landed for this campaign (untracked pending commit):
`sweep_bank_5d.py`, `analyze_universes_5d.py`,
`sbatch_sweep_bank_5d_{dump,run}.sh`, `sbatch_seedscan_split_5d.sh`,
`sbatch_bootstrap_5d.sh`, `sbatch_combine_5d_budget.sh`.

## 2026-06-29 — FPS cloud-fixed re-dump chain launched (capstone Step 2 prerequisite); disk cleanup

The old FPS point-cloud ROOTs predate the 06-28 truth-cloud fix, so before
capstone Step 2 (raw-data FPS-PET) can proceed, the full-phase-space
point-cloud dump has to be regenerated. Chain (all job states confirmed via
`sacct`):
- **evloop array 55288326** (12 playlists,
  `sbatch_evloop_array_pointcloud_fps.sh`, `MNV101_DUMP_POINTCLOUD=1` +
  `MNV101_FULL_PHASE_SPACE=1` together, CV-only): all 12 tasks **COMPLETED**
  2026-06-29 20:51 through 2026-06-30 00:10.
- **hadd 55288356** (`sbatch_hadd_pc_fps.sh`): COMPLETED; merged the 12
  per-playlist files into `runEventLoopOmniFold_PC_FPS_MEFHC.root`,
  **72,651,640,496 bytes** (`hadd_pc_fps_55288356.out`).
- **npz 55288408** (`sbatch_npz_pc_fps.sh`): COMPLETED; wrote
  `of_inputs_pc_fps.npz` (**6,575,612,207 bytes**) — signal clouds kept
  **32,917,278/49,906,108** gen rows, reco shape (32,917,278, 12, 3), data
  4,091,707 measured clusters.
- **PET FPS full-stats train 55288409** (`sbatch_pet_train_fps_hvd.sh`,
  horovod): submitted 2026-06-29 20:37, queued until 2026-07-01 23:42
  before starting; **RUNNING** as of this writing — header of
  `pet_train_fps_55288409.out` reads `train=40000000 ranks=4` with
  `niter=5 epochs=8`; the log (`nd-unfolding/log_minerva_pet.txt` mirrors
  this run) is through iteration 4 of the requested 5 as of 2026-07-02.

Same window, a disk cleanup ran on **2026-06-29** (bracketed by the
`2d-unfolding/` directory mtime, 19:45:54) that removed the merged non-FPS
`universes_full` files, sweep banks, per-playlist intermediates, 3D ML npz,
and old 2D archives — all with saved covariance endpoints kept. Verified via
`git status`: the four launcher scripts in
`2d-unfolding/archive_pre_phase18/` (`sbatch_evloop_array.sh`,
`sbatch_unfold_2d.sh`, `sbatch_unfold_2d_fullstats.sh`,
`sbatch_unfold_2d_fullstats_postfix.sh`) are deleted-but-unstaged, and the
whole `archive_pre_phase18/` directory is gone from disk (the historical
TB totals could not be re-verified from a disk artifact at this remove — only
the file-level deletions are directly checkable now). The regen path was
exercised almost immediately: the per-playlist + merged 5D `universes_full`
files needed by the unified-throw study below were freshly re-dumped
2026-06-29/30 (`runEventLoopOmniFold_5D_*_universes_full.root`, mtimes
06-29 22:47 / 06-30 03:18).

## 2026-06-29/30 — PET 5D uncertainty comparison vs GBDT: verdict WORSE (indicative, 2M-train anchor)

Two comparisons, both anchored to the 2M-train PET reweight
(`pet_weights_full.npz`) and both block-sum covariance (identical scheme for
PET and GBDT):
- `products/pet/pet_vs_gbdt_uncertainty_5d_summary.json` (written
  2026-06-29 19:29): on the **10550** common 5D bins, median per-bin
  fractional uncertainty **14.8%** (PET headline: clean block-sum
  C_syst+C_stat+C_ML + PET-native shifted-W lateral) vs **13.3%** (GBDT);
  median ratio **1.192**; PET tighter in only **38.4%** of bins.
  Vertical-only (no lateral) PET reads **14.7%** — the conclusion is not
  lateral-driven. **VERDICT: WORSE** than GBDT — contrast with the 4D
  verdict, COMPARABLE (11.8% vs 13.4%, ratio 0.950, PET tighter in 53.6% of
  4796 common bins; `pet_vs_gbdt_uncertainty_summary.json`).
- `products/pet/pet_5d_covariance_combined_unified_wlat_summary.json`
  (written 2026-06-30 08:39): PET's own unified-throw study (160 throws,
  frozen reweighter) on the 10550 reported bins gives **sqrt-tr unified
  1.5933e-37** vs **sqrt-tr block 2.7897e-38** — **unified/block ratio
  5.711** (median per-bin sigma ratio 1.216). This is far larger than the
  GBDT-side inflation found the next day (below) and is **flagged, not
  adopted**: it is a frozen-reweighter lower bound (omits the retraining-
  response nonlinearity), and the size of the ratio needs to be understood
  before any PET 5D unified-throw number is quoted in the note.

## 2026-06-30/07-01 — 5D GBDT unified-throw study: launched, drained, ADOPTED

Analogous to the 4D (×2.01) and FPS (×1.295) unified-throw studies:
jitter-matched block units (12 GENIE/hadronic knobs + 100 flux universes,
re-unfolded at the CV seed so OmniFold's own jitter cancels in the ratio)
vs true joint unified throws. Chain (job states via `sacct`): dump array
**55286192** (8 tasks, COMPLETED) → block/run arrays **55286273**/**55286275**
(21 tasks each, all COMPLETED 2026-06-30 07:11 through 2026-07-01 21:18) →
combine **55286276** (COMPLETED 2026-07-01 23:31-23:54). Scripts:
`sbatch_uthrow_{dump,run,block,combine}_5d.sh`, `unified_throw_cov_5d.py`,
`adopt_unified_5d.py`.

Result (`uq_5d/uthrow5d_comb_55286276.out`): 160 throws from 20 slabs,
10694 reported bins; **sqrt-trace unified 4.1209e-38 vs block 2.6749e-38,
raw ratio 1.541**; jitter-corrected **unified 4.1164e-38, ratio 1.539**
(cross-term 117.2% of block; jitter floor 1.932e-39, ~20x below the signal).
Far milder than the 4D ×2.01, closer to the FPS ×1.295. Notably the
per-bin picture is NOT uniform inflation: **median per-bin sigma ratio
unified/block = 0.830** (below 1 for most bins) even though the trace ratio
is 1.539 — the inflation is concentrated in a minority of bins that dominate
the trace, unlike a flat systematic-wide effect. **ADOPTED** (same
conservative per-bin max(sigma_unified, sigma_block) inflation transferred
onto the sweep's own vertical block, as in 4D/FPS):
`uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`
(written 2026-07-02 00:59). The adopted median per-bin fraction (over the
10550 bins PET also reports) reads **13.69%**, up from the pre-adoption
block-sum 13.33-13.43%
(`products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json`, GBDT
side) — a modest few-percent inflation, matching the mild 1.539 trace ratio.
This closes the 5D unified-throw gate: unlike 4D, the 5D block-sum median is
not materially inflated by the rigorous check.

A same-day follow-up
(`products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json`, written
2026-07-02 01:01) reran the PET-vs-GBDT comparison with both sides on their
unified-throw-adopted covariances: PET (using its own flagged-not-vetted
5.711x-inflated unified covariance) reads median **16.7%** vs GBDT's
now-adopted **13.7%**, ratio **1.346**, PET tighter in only 30% of bins —
still WORSE, and this comparison carries the same caveat as the PET-side
5.711 ratio above until that number is understood.

## 2026-07-03 — Background subtraction is frozen at CV across all systematic universes (KNOWN_ISSUES #13)

Audit triggered by an advisor comment on the analysis note's 0.35%-vs-0.2%
background sentence (`sec_experiment.tex`). Findings (code-verified):

- **Mechanism**: background is never injected as negative-weight events; the
  OmniFold step-1 measured target is real data down-weighted by a per-reco-bin
  purity factor `max(0, data - bkg)/data`
  (`unfold_nd_omnifold_unbinned.py` `build_measured_training_nd`, ~:400-421;
  2D analog `build_measured_training_2d`).
- **CV-only genuine background**: `collect_bkg_nd` (~:374-397) and the 2D
  `fill_bkg_reco_2d` take **no universe argument** — they read the CV `w_bkg`
  with `pot_scale` only. Signal and truth-denominator collectors DO take
  `universe_branch`; the background collector does not.
- **Banked sweeps freeze the whole target**: `sweep_bank.py` (~:150-160)
  builds `measured_weights` once in group 0 and every per-universe `do_run`
  (~:191,208) reloads it from `cv.npz`; `sweep_bank_5d.py` identical. So the
  4D/5D covariances contain **no background-modeling variation**.
- **Partial exception (2D only)**: the 2D per-universe driver adds signal
  *fakes* (`pass_reco & ~pass_truth`) from the universe-weighted signal
  arrays (`unfold_2d_omnifold_unbinned.py` ~:1230-1242), so the fakes term
  tracks universes in 2D; the ND/banked path does not.
- **Impact bound**: genuine background is 0.35% of the selected sample
  (playlist-1A post-MINOS-fix, `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:213`:
  1,256 POT-scaled bkg / ~3.59e5 data). Even a 100% background error moves
  the sample normalisation by ~0.35%, far below the ~10%+ total budgets;
  locally larger where backgrounds concentrate (low p||/pT — the published
  paper reaches ~10% in its lowest bins).
- **Cross-check vs published**: Ruterbories (2106.16210, p.5) predicts
  **8655 (0.2%)** background events under a *narrower* definition (wrong
  flavour + wrong sign + NC only; ours additionally counts
  out-of-fiducial-vertex events). Note text reworded accordingly
  (no more unqualified "consistent with").

Possible closure/fix paths (not yet done): (a) recompute our background under
the paper's definition to recover ~0.2% (needs a channel split of the
`mc_background` tree — check available truth branches); (b) wire
`universe_branch` through `collect_bkg_nd` and re-bank to add a background
block to the covariance (expected negligible at the 0.35% scale).

### 2026-07-03 follow-up — mc_background definition drift audited: NO double-count; 0.35% is playlist-1A genuine-only

Phase 18 (`d1bc881`, 2026-05-18) changed the C++ background fill from
`if(isSignal) continue;` to `if(isSignal && inPS_bkg) continue;`, so every
post-Phase-18 omnifile's `mc_background` INCLUDES out-of-PS signal fakes.
Audit results (uproot on `runEventLoopOmniFold_MEFHC.root` + run-log grep):

- **No fakes double-count, published 2D unaffected**: post-Phase-18
  `mc_signal_reco` is truth-in-PS gated (all 32,849,103 rows pass_truth), so
  the 2D driver's separate fakes-add finds n_fakes = 0 — a structural no-op.
  Fakes are subtracted exactly once (via the tree). The only nonzero
  fakes-add ever logged is a pre-Phase-18 1D baseline (n=6, 2026-03-26).
  The driver's justifying comment was stale → rewritten 2026-07-03
  (`unfold_2d_omnifold_unbinned.py` fakes block).
- **Rates by vintage**: post-P18 MEFHC `mc_background` = 125,725 POT-scaled
  = 3.05% of data (658,227 raw rows); within the 2D grid 119,132 (= the
  iter_test.log "incl. fakes" integral; TH2D::Integral drops the 5.24%
  out-of-grid overflow). Decomposition ≈ 0.35% genuine + ~2.7% fakes.
- **Genuine-only cannot be recomputed**: no pre-Phase-18 omnifile survives
  (the `*_minos_fix`/`*_phase18` files were deleted/renamed), and the tree
  carries no truth label to split genuine from fakes. Best genuine estimate
  remains the archived playlist-1A 0.35% (1,256 events,
  `2D_OMNIFOLD_RUN_LOG_ARCHIVE.md:213`). The analysis-note sentence now
  scopes 0.35% to playlist 1A accordingly.
- **Closure vs Ruterbories 8655 (0.2%)**: blocked on truth channel labels
  (nu PDG / current / vertex) absent from all dumps — add a channel-label
  branch to `mc_background` in the C++ and it rides along with the next
  gated 12-playlist re-run.

## 2026-07-04 — C++ change for BOTH #13 fixes written + built (STAGED, not launched)

Combined the KNOWN_ISSUES #13 per-universe-background fix and the Ruterbories
channel-label cross-check into one edit of
`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`, so a single
future 12-playlist re-run delivers both. **Staged only** — the change is inert
until the event loop runs with `MNV101_DUMP_UNIVERSES` set; nothing was
regenerated, re-banked, or committed. Held off launching to avoid regenerating
shared MEFHC omnifiles while the personal account's PET FPS steps 3/4 depend on
the current products (PET train `55445418` still running as of this entry).

- **Channel labels (0.2% cross-check)** — `LoopAndFillUnbinnedMCBackground`
  now dumps per-event truth labels on `mc_background`: `bkg_nuPDG`
  (`GetTruthNuPDG` → mc_incoming), `bkg_current` (`GetCurrent`, 1=CC/2=NC),
  `bkg_inttype` (`GetInteractionType` → mc_intType), and truth vertex
  `bkg_vtx_{x,y,z}` (`GetTrueVertex`, mm). Genuine-vs-fake split is deferred to
  OFFLINE analysis (wrong-flavour `nuPDG!=14`, NC `current==2`,
  out-of-fiducial from the vertex vs the driver's own minZ=5980/maxZ=8422/
  apothem=850) — the raw vertex is dumped rather than reimplementing the
  hexagon-apothem cut in the loop, so there is zero risk of divergence from the
  signal PS definition.
- **Per-universe background (#13 fix)** — new `UniverseKineContext::BkgTreeReco`
  + `BuildUniverseBranchTable` case emitting `sim_background_{,pz,q3,W}_<band>
  _<idx>` (own namespace, never aliases signal `sim_*`). Reco-mode universe
  branch table attached to `mc_background`: `w_bkg_<band>_<idx>` per (band,idx)
  + shifted lateral kinematics for non-vertical bands; gated on
  `MNV101_DUMP_UNIVERSES` + non-null `errorBands`; restores CV entry/MichelEvent
  state before `out->Fill()`. Caller passes `&error_bands`. Reco-mode only —
  background is a pure reco-space subtraction, no truth-mode table needed.
- **Build**: job `55476273` COMPLETED exit 0:0, clean compile, installed
  `opt/bin/runEventLoopOmniFold` mtime 06:45:09 > source 06:29:25. (First
  attempt `55476062` failed on env, NOT code: `setup_salloc_env.sh` resolves
  `root_6_28` against `$HOME`, which is the sandboxed school home in this
  session — real env is `/global/homes/j/josephrb/.conda/envs/root_6_28`;
  fixed via the script's own `ROOT628_PREFIX=` override, no file edit.)
- **Still deferred** (do NOT do before the re-run): the 12-playlist re-run →
  hadd → re-bank; then run the #13 covariance re-quote and the 0.2% closure.

### 2026-07-04 follow-up — Python consumers + offline channel-split analyzer (STAGED)

Wrote the Python side of both fixes (previously deferred), staged/unlaunched —
all four edited modules `py_compile` clean under python3 (the login-node bare
`python` is Python 2 and chokes on the repo's f-strings; always use `python3`).

- **`collect_bkg_nd` (`unfold_nd_omnifold_unbinned.py`)** now takes
  `universe_branch=(band, idx)`: reads `w_bkg_<sanitized-band>_<idx>` instead of
  CV `w_bkg`, and for LATERAL bands swaps the reco kinematics to
  `sim_background_/sim_background_pz_<band>_<idx>` + lateral-variant axes (q3, W)
  to `sim_background_<axis>_<band>_<idx>` (eavail is lateral-invariant, stays CV).
  The direct-driver call site (`main`, ~:579) now passes `universe_branch`, so an
  `--universe` unfold no longer freezes the background at CV. Also added an
  `extra_wbranches=` path returning per-universe `w_bkg` columns aligned to the
  CV-kept bkg events (5-tuple return only when requested — the other 6 callers
  are untouched, still 4-tuple). Branch-name helpers mirror the C++ schema:
  `u2d._universe_bkg_branch`, `_universe_kine_branches(..., "bkg_tree_reco")`,
  `_axis_universe_branch(..., "bkg_tree")`.
- **Banked vertical sweep (`sweep_bank.py`, `sweep_bank_5d.py`)** — `do_dump`
  now banks each vertical universe's `w_bkg` column (`{tag}_bkgw.npy`) and, in
  group 0, the CV bkg reco columns (`bkg_cols` in `cv.npz`). `do_run` rebins the
  CV background with that universe's `w_bkg` and recomputes the measured purity
  down-weight, replacing the frozen `cv["measured_weights"]`. Weight-only is the
  correct treatment here — the bank already handles vertical bands weight-only
  (CV kinematics), and the 12 lateral bands go through the direct-driver re-read
  path above. Graceful CV fallback when `bkg_cols`/`{tag}_bkgw.npy` is absent, so
  pre-#13 banks still run bit-identically.
- **`bkg_channel_split.py` (NEW)** — offline genuine-vs-fake channel split for
  the Ruterbories 0.2% closure. Reads the `bkg_nuPDG/current/inttype/vtx_{x,y,z}`
  labels and classifies each selected bkg event into mutually-exclusive
  {wrong_sign, wrong_flavour, nc, out_of_fiducial, fake}; reports NARROW genuine
  (wrong_sign+wrong_flavour+nc, compare 8655/0.2%) vs BROAD genuine (+out-of-fid,
  compare playlist-1A 0.35%), with fakes (numu-CC-in-fiducial = out-of-PS signal)
  called out as NOT genuine background. The ZRange(5980,8422)+Apothem(850)
  hexagon test is a bit-for-bit port of `CCInclusiveSignal.h`
  (`|y| < -|x|/√3 + 2·850/√3` AND `|x| < 850`, strict `<`); unit-tested for the
  fiducial edges and category partition. Fails loudly on a pre-2026-07-04
  omnifile (labels absent). Cannot run until the re-run produces the labels.

## 2026-07-12 — UQ audit remediation and presentation quarantine

An independent code audit invalidated the old adopted 4D/5D/FPS unified-throw
products and exposed the old PET statistical block as a frozen-weight
fluctuation rather than an estimator bootstrap. The affected covariance and
significance numbers remain on disk and in earlier ledger entries for
provenance, but are unquotable pending corrected production. Central cross
sections, closure tests, dimensional anchors, and the finalized 2D result are
not invalidated.

The corrected code now uses actual asymmetric +/- endpoints, one fixed
estimator seed, universe-mean centering with biased MAT `1/N`, a separately
stored joint mean shift, exact throw/replica manifests, coherent data+MC PET
draws with retraining, full covariance projection for `(Eavail,W)`, consistent
finite support, and fail-closed background/flux/bank validation. The legacy
one-sided PET unified path was ported to the same contract, and unsafe legacy
throw run/combine entry points were disabled. The expanded remediation suite
passes 18/18 tests; Python compilation, shell syntax, and diff checks pass.

`MNV101_ACTIVE_UNIVERSE=BAND:IDX` promotes one universe into the ordinary event
loop, rebuilding truth/reco selection, truth-authoritative IDs, backgrounds,
and native misses. Only five detector bands are genuinely kinematic
(BeamAngleX/Y, MuonResolution, Muon_Energy_MINERvA/MINOS); MinosEfficiency and
GEANT are weight-only. Before the 2026-07-16 presentation, production is
prioritizing corrected 5D stat/ML and joint throws plus a targeted full-MEFHC
three-band migration bound. Until that bound lands, corrected bank-based
numbers must be labeled preliminary and support-limited. Full five-band active
coverage remains the publication gate.

## 2026-07-12 — PET extraction environment seam and audit follow-ups

The PET replica extractor was found to require PyROOT after GPU training while
the replica jobs run under NERSC's TensorFlow 2.15 module, whose Python has no
`ROOT` module. The launcher now activates the analysis environment and invokes
the absolute `root_6_28` Python for extraction. The extractor also self-reexecs
through that environment before any ROOT-dependent import, which rescues the
already-snapshotted running and queued jobs without cancellation. A direct
TensorFlow-Python invocation of `extract_bootstrap_replica.py --help` completed
through the handoff with PyROOT loaded; the two active replicas remained healthy
in GPU training.

Audit hardening also made the unified-throw bank require exactly 100 PPFX IDs,
made incremental throw/block slab replacement atomic, and aligned the PET joint
throw with the GBDT tail contract (individual factors clipped, composed ratio
validated but not re-clipped). The expanded suite passes 20/20 tests. Scope
disclosures now state that corrected 4D/5D `C_ML` varies the train/test split at
fixed estimator seed 42, that only the joint mean shift is stored, and that the
current PET input's 4,091,707 measured-event weights are all one with no
reconstructed-background subtraction. The resulting PET bootstrap covariance
must therefore be labeled as belonging to that unsubtracted target.

## 2026-07-13 — Corrected background-subtracted PET components landed

The ordered PET remediation supersedes the unsubtracted-target state above and
has reached component gates 1--5 on the canonical 5D background-subtracted
target. The new point-cloud input has exact event-by-event data alignment to the
scalar target, byte-identical MC arrays, and preserves the old unit-weight input
as an unsubtracted control. The corrected nominal and same-seed GPU-floor repeat
passed full ordered coverage and extraction checks; GPU nondeterminism is
negligible relative to the retrained statistical and ML spreads. A strict
20-member coherent data+MC Poisson ensemble now supplies the first corrected PET
statistical component, and a 12-member crossed subsample/estimator-seed design
supplies the PET-specific ML component.

These products do not close the PET budget. The available vertical systematic
block still uses the pre-fix support-limited bank, the PET-native lateral block
has not been rebuilt on the background-aware/selection-complete inputs, and the
predeclared targeted per-universe retraining-response gate is outstanding. The
preliminary no-lateral total and its 4D marginal therefore remain outside the
analysis-note headline numbers. Twenty replicas are adequate for the current
component/per-bin diagnostic, but a larger inventory is advisable before
treating the rank-limited high-dimensional statistical matrix as
publication-grade.

## 2026-07-14 — Corrected 5D GBDT adoption and present PET campaign complete

The full 188-entry background-aware 5D re-quote changed the systematic
sqrt-trace by +0.14% and the combined block sum by +0.30%, closing the frozen-CV
background concern as negligible. The corrected mean-centered unified
covariance is adopted at sqrt-trace 5.8077e-38, with the 1.654e-38 joint mean
shift reported separately; the CV-centered 6.2367e-38 matrix is retained as a
conservative variant. Both are PSD.

The PET campaign then completed the predeclared six-band retraining response
and the corrected detector block. All six retraining probes were material; the
rank-six response term is the second-largest component by trace. The five-block
PSD total on the common 10,550-bin mask has sqrt-trace 3.8777e-38 and median
relative uncertainty 15.103%; its 4D marginal has median 12.365%. This closes
the present analysis-note campaign. Its statistical block contains 20 coherent
replicas. Expanding to 100 replicas is planned before publication but has not
yet been run. The detector block is a frozen-map shifted-detector response, not
per-universe PET retraining or shifted-cloud membership regeneration.

## 2026-07-15 — #16 active-universe interface validated (P2, Agent A)

The selection-complete active-universe event-loop mode
(`MNV101_ACTIVE_UNIVERSE=BAND:IDX`) was validated before launching any P3
production family. The binary was rebuilt and installed from the current
`runEventLoopOmniFold.cpp` (md5 `e63c74961d699313ef155065fc790ff1`, 9
`ACTIVE_UNIVERSE` strings) and exercised on a 4-MC/8-Data 1A smoke subset on a
`gpu_interactive` node (salloc 55933725), CPU-only via `srun --gres=none`. All
gates passed: the remediation unit suite (20/20); invalid band/index requests
fail closed (`nocolon`, `NotARealBand:0`, `BeamAngleX:999` → rc1); the CV smoke
carries `hasActiveUniverse=0`, band `cv`, and zero migration counters; the
`BeamAngleX:0` endpoint carries the correct `band/idx/isLateral=1` metadata and a
nonzero reco migration census (entrants=21, exits=21; truth 0/0, as expected for
a reco-level beam-angle shift) — the selection migration the CV-support-limited
dump-all bank cannot see; truth-authoritative completeness signal_reco/truth_denom
= 1.000000 on both CV and endpoint with native misses rebuilt
(nTruthOnlyMisses=66989); point-cloud branches are complete on all four trees
under `MNV101_DUMP_POINTCLOUD=1` (signal `part_gen_*`+`part_reco_*`; background
and data `part_reco_*`, ~99.7–99.9% populated); and the FPS flag produces
distinct behaviour (truth_denom 399015 vs standard 263111, ×1.52). Record and
readback validator in `nd-unfolding/active_universe_5d/INTERFACE_VALIDATION.md`
and `interface_smoke/`. The production launcher
(`sbatch_evloop_array_5d_active_laterals.sh`) is committed with P3S. The shared
`ND_OMNIFOLD_STATUS.md` one-liner is deferred: it carries a concurrent session's
uncommitted edit and was left untouched to avoid folding it into this commit.

## 2026-07-15 — #16 P3S standard active event loops IN PROGRESS (Agent A)

Not a completion gate — committing the P3S/P4 infrastructure and current status
only; no results are claimed and no numbers are quotable yet. The standard
active-universe production (5 kinematic bands × 2 endpoints × 12 playlists = 120
per-playlist ROOTs, `MNV101_ACTIVE_UNIVERSE=BAND:IDX` + `MNV101_DUMP_POINTCLOUD=1`,
no full-phase-space) is partially produced under
`active_universe_5d/standard/<BAND>_<EP>/`. Throughput is limited by global
/pscratch (Lustre) contention while four sessions run heavy I/O concurrently:
each output is ~6.7 GB (point clouds for P5), and the measured completion rate is
near zero at both MAX=12 and MAX=40 (loops progress at ~20–40 MB/min; they are
I/O-waiting, not broken). The run is fully resumable (skip-if-exists) and is
being ground out on CPU-interactive sallocs, relaunched across the 4 h wall.
Committed infrastructure: batch launcher `sbatch_evloop_array_5d_active_laterals.sh`,
interactive orchestrator `run_active_laterals_interactive.sh`, endpoint merge
`merge_active_endpoints.sh`, P4 endpoint-unfold orchestrator
`run_active_lateral_unfolds_interactive.sh`, P4 covariance validator
`p4_validate_active_lateral.py`, and receipt generator `p3s_manifest_summary.py`.
Full recipe, job IDs, and coordination notes in
`active_universe_5d/AGENT_A_HANDOFF.md`. The P3S completion gate (exact 120-file
manifest + per-mode summary + ledger + STATUS) will land when the inventory is
complete; P4 (scalar lateral covariance) follows.

### 2026-07-16 — P6-4D corrected 4D UQ: non-lateral core landed (Publication Agent D)

Rebuilt the corrected independent 4D (pt,pz,Eavail,q3) covariance under the KNOWN_ISSUES
#14 contract (actual asymmetric ± endpoints, one fixed estimator seed, throw-mean
centering with a separately stored mean shift, MAT biased 1/N, exact manifests, no jitter
subtraction). All outputs in `nd-unfolding/uq_4d/corrected/`; the old June `uq_4d/`
products are preserved, quarantined.
- **Throw bank reconstructed with NO event loop.** `bank_uthrow_4d` + its 3D source were
  deleted and no 4D `_universes_full` omnifile exists, so the June `assemble_bank_4d.py`
  path is dead. `assemble_bank_4d_from5d.py` rebuilds it from the surviving
  `bank_uthrow_5d`: that bank is event-aligned to `of_inputs_4d` (w_truth/w_reco
  BYTE-IDENTICAL, pt/pz/Eavail cols + all four edges identical); the 372 per-event
  universe-ratio arrays are binning-independent → symlinked; q3 + measured target come
  from of_inputs_4d, truth-denom from the 5D bank. CV-reproduce pilot PASS: reported mask
  identical (4830), total 3.0679e-38 vs central 3.0664e-38 (rel 4.8e-4), per-bin med 0.65%.
- **Corrected replicas regenerated** (June `_prehm` set is pre-remediation: corrected
  `bootstrap_nd.py` fixes the estimator seed at 42 + decorrelates data/MC Poisson): C_stat
  100 coherent bootstraps + C_ML 24 split-response, exact manifests validated. Ran on a
  4-node interactive GPU accelerator (this unfold is memory-bandwidth-bound ~4-6/node →
  scale with nodes) after CPU hours were restored; CPU batch as node-spread complement.
- **Combined covariance (guaranteed core), validated ALL_OK.** C_syst block-sum on the
  reused 187-file sweep (#13 background-CV null-effect) √tr 2.0931e-38 (median 13.37%/bin,
  rank 142) + 1.4% norm + C_stat 1.2117e-39 + C_ML 1.0499e-39 → COMBINED √tr 2.0992e-38,
  median 13.47%/bin, rank 264/4830; symmetric, finite, PSD (min-eig/max −2.8e-16).
  The Muon-reco lateral bands in the sweep are SUPPORT-LIMITED (labeled); the final
  lateral swap + adoption is GATED on Agent A's committed selection-complete standard
  lateral block and is NOT crossed here.
- **P7 projection code** `project_cov_nd.py` validated end-to-end (5D→4D marginal dry-run,
  candidate `uq_4d/corrected/projections_candidate/`, NOT quoted; final numbers gated on
  the final adopted 5D). **Unified-throw** (160 joint throws + 124 block units, seed 1000)
  and candidate adopt (mean + `--cv-centered`) were IN FLIGHT at this entry.

## 2026-07-18 — P4 standard-lateral chain hardened (REPAIR ONLY, Agent A)

Repair-only turn; independent MIG-V2 preflight = BLOCK, so NO covariance was built,
promoted, or adopted. Standard P4 chain hardened with fail-closed gates + exact
inventory hashing (`nd-unfolding/p4_lib.py`): 10-endpoint manifest / config /
mask-order sha256 hashes; merged-endpoint audit (four non-empty trees, finite
positive POT, `signal_reco==truth_denom`, native-miss + all census counters,
declared migration policy); atomic unfold completion markers + config/source
validation + fail-closed parallel return (`run_p4_unfold_std.sh`); a fail-closed
active-lateral validator requiring exactly the 5 kinematic bands, positive-finite
component traces, EXACT component sum, symmetry/PSD, complete support-limited
comparison, and 5D→4D projection non-mutation (`p4_validate_active_lateral.py`); and
a pure-component lateral-replacement step guarded against adopted-path overwrite
(`p4_lateral_replace.py`). The MAT two-endpoint formula is preserved
(`uq_math.mat_covariance`). Tests `nd-unfolding/tests/test_p4_repair.py`: 16/16 pass
over the eight verifier-identified failure modes (missing endpoint, truncated
output, missing census/migration, zero/absent component, order/hash mismatch,
missing support block, component-sum mismatch, invalid projection). The 10 standard
endpoint unfolds are content-validated 10/10 (open/non-zombie/not-recovered/finite
`hXSecND_flat`/common dim 65856/positive) but are NOT consumed this turn. Candidate
covariance construction is authorized only after the standard-p4-verifier
(019f74cb-b85d-7ba0-96c5-dfbd09e59159) returns PASS. STATUS one-liner deferred
(ND_OMNIFOLD_STATUS.md carries a concurrent session's uncommitted edit).

## 2026-07-18 — P4 standard chain connected end-to-end (REPAIR round 2, Agent A)

Second repair round after the standard-p4-verifier BLOCKed 553a6a6 ("not connected
end-to-end"). Still REPAIR-ONLY (MIG-V2 BLOCK): no covariance built/promoted/adopted;
no candidate exists. Added the ONE canonical driver `run_p4_standard.sh` that wires the
hardened, manifest-bound stages in order: merge+audit → `p4_evidence.py` (recompute+bind
hashes) → atomic/resumable unfold → [HARD GATE: verifier PASS] → `p4_build_components.py`
(named corrected bkgaware components + 5 active MAT bands, no globs) → fail-closed
`p4_validate_active_lateral.py` (mandatory `--merged-dir`) → `p4_project_4d.py` (5D→4D
mask/edge hashes + frozen-central byte-identical non-mutation). Retired/guarded the old
unsafe standard route (`merge_active_endpoints.sh`, `run_active_lateral_unfolds_interactive.sh`,
`run_active_laterals_interactive.sh`; bare-glob analyzer superseded). Read-only evidence
pass EVIDENCE-COMPLETE: recomputed bindings all MATCH the verifier's independent values —
central5d 630306e2, mask5d 74374b1a (10694), endpoint-manifest af568b4a, central4d
1fb82508, mask4d c977c643 (4830); selection migration nonzero for BeamAngleX/Y
(4700–4808) and exactly zero for the three bin-migration-only bands; mc_signal_reco==
mc_truth_denom per merged endpoint. Receipts committed under
`active_universe_5d/standard/evidence/`. Tests `tests/test_p4_repair.py` 20/20 (16 gate
+ 4 real-CLI integration, fail-closed). MAT biased-1/N preserved (`uq_math.mat_covariance`).
Candidate construction remains authorized only after the same standard-p4-verifier
returns PASS on this patch. Canonical STATUS deferred (concurrent uncommitted edit);
Agent-A status receipt at `active_universe_5d/standard/P4_STANDARD_STATUS.md`.

## 2026-07-18 — P4 STANDARD repair round 3 (Agent A, standard-only, REPAIR-ONLY)
Third fail-closed repair after the standard-p4-verifier BLOCKed round-2 (9428ca8).
NO candidate constructed/promoted/adopted this turn — candidate stages remain
gated behind a verifier PASS token. Repaired the 8 cited defects as one executable
canonical chain (`run_p4_standard.sh` STOP_AFTER=evidence default):
  1. Mutual executability — `p4_lib.py` ROOT-free gate library; ROOT lazy-imported
     everywhere so guards/tests run on the login node.
  2. Separate canonical stat/ML ROOTs (not the combined file) + PURE ADDITION only
     in `p4_build_components.py` (no subtraction anywhere).
  3. Complete mandatory manifest — `p4_evidence.py` now binds config+hash, source
     git blobs/commits, C++ binary sha256, edges/bin-volume hash, endpoint
     mask-equality, and the orchestrator merged-hash receipt.
  4. Reuse of the owner-neutral orchestrator merged receipt
     (`docs/orchestration/state/merged-input-hashes/p4-merged-20260718/`, size⇥mtime⇥path
     inventory) — NO new 538-GB hash pass.
  5. Later-only adoption CLI `p4_adopt_standard.py` (needs --i-understand-adoption;
     not run, not wired into the driver).
  6. Deterministic projection M in-code (`p4_project_4d.py`, CENTRAL_REL fixed,
     rejects CLI override) + byte-identical central non-mutation.
  7. Inseparable merged evidence (manifest 10 SHA == merged-audit 10 SHA gate).
  8. Real-CLI test harness: `tests/test_p4_repair.py` — 28 tests PASS.
Preflight (holder, read-only): recomputed central5d/mask5d/endpoint/central4d/mask4d
all MATCH the verifier; merged receipt bound (digest 6e6c4752…, 10 hashes);
`EVIDENCE-COMPLETE`. Receipts under `active_universe_5d/standard/evidence/`.
Canonical STATUS still deferred (ND_OMNIFOLD_STATUS.md dirty from another owner —
PG0); Agent-A receipt at `active_universe_5d/standard/P4_STANDARD_STATUS.md`.
Verifier must PASS this patch before any candidate-construction turn.
