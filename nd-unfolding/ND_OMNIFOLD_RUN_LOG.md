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

2026-07-18 (Agent C, FPS 2nd repair round): ten FPS active-endpoint unfolds confirmed PURITY CONTROLS
(launchers omitted --bkg-mode → purity default) and QUARANTINED in `active_universe_5d/fps/unfolds/`;
read-only `fps_control_manifest.json` binds them (label=purity-control; publication gate rejects it).
Negweight-refined preflight hardened (fps_provenance v2 gates, hash-bound publication manifest + PASS
receipt at component build / P4 validate / active adopt / unified adopt; canonical 266/285 mask
committed as `fps_reported_mask.json`; full merged-input SHA256 reused from the orchestrator receipt
p4-merged-20260718; mandatory hJointMeanShift; transactional launchers into a separate
`unfolds_negweight_refined/` namespace). 41/41 ROOT-free tests PASS. No covariance/adoption produced,
no endpoints rerun. Canonical STATUS still deferred (ND_OMNIFOLD_STATUS.md dirty from another owner);
FPS status receipt in `uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md`. Gated on fps-adopt-verifier PASS.

2026-07-18 (Agent C, FPS repair-3): made the publication-manifest builder + every consumer mutually
executable and hash-recomputing. Consumers gate (manifest/receipt/recompute-all-hashes) before a lazy
ROOT import (login-safe); manifest binds canonical PATHS + strict 64-hex for unfold/input/config/source/
launcher/central/audit; P4 gating unconditional; schema-versioned receipt chain component_build ->
p4_validation -> active_adoption -> unified_adoption each binding the exact predecessor; two-field PASS
rejected; unified adoption binds CV sha + canonical 266/285 mask + hJointMeanShift(expected_dim=n)+hash;
one strict launcher validator (fps_endpoint_receipt.py) attributes the launcher actually used. Reused the
committed p4-merged-20260718 full-hash receipt (size/mtime + digest revalidated; no 748GB re-hash).
Tests: 49/49 unit + 9/9 REAL-CLI negatives PASS. No production run. PG0: ND_OMNIFOLD_STATUS.md canonical
status still deferred (pre-existing dirty file, no durable writer receipt — not staged/absorbed here);
FPS status in uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md. Gated on fps-adopt-verifier PASS.

- 2026-07-18 (Agent B, PET/F7 repair round on 9d7a4c6, code/static-test only — no GPU/Slurm/C++/
  G2/P3F/nominal/replicas/covariance): F7 coherent estimator-bootstrap over THREE inventories
  (data, signal-MC, background-MC) IMPLEMENTED and durability-hardened; nominal frozen to negweight
  + Stay-Positive (Option-A literal background-cloud injection), purity = regression control.
  Repairs: (1) extended fail-closed validator/tests for background factor+indices+n_bkg_full+order-
  evidence tamper/omission and data/signal/background global-before-subset replay; (2) NEW pure
  contract `pet/fullevent_dump_contract.py` (G2 schema gate petSchemaVersion=g2-fullevent-v1/
  hasFullEventSchema=1/fullPhaseSpace=1, strict complete manifest, 3-inventory alignment + vector-
  length + per-inventory identity/order hashes, forbidden-purity-fallback, atomic temp+rename) +
  repaired `pet/dump_pointcloud_inputs.py` to gate on it (old/recoil inputs fail closed; PyROOT G2
  read RUNTIME-BLOCKED pending Agent E's G2 ROOT; recoil dump only under --legacy-recoil-crosscheck,
  labeled non-G2); (3) `assert_publication_config` gate + quarantine banner on the recoil launcher
  `sbatch_pet_nominal_bkgsub.sh` (verified it routes through the recoil loader — not publication).
  35/35 ROOT-free tests PASS (test_fullevent_fps 25 + test_fullevent_dump_contract 10). VERDICT:
  EVIDENCE-BLOCKED — CLOSED needs the G2 background-cloud ROOT
  `runEventLoopOmniFold_PC_FPS_MEFHC_bkgcloud.root` + Agent-B-aligned full-schema NPZ with literal
  background clouds/scalars/w_bkg. Canonical ND STATUS deferred (ND_OMNIFOLD_STATUS.md dirty from
  another owner — PG0); PET receipt in `nd-unfolding/PET_P1_P5_SESSION_STATE.md`.

## 2026-07-18 — G2 full-event 1A smoke PASS + atomic publication (PET_UQ Gate 1)

Owner-held interactive gate (Agent E, G2 C++ source/runtime owner). Built+installed
the canonical `runEventLoopOmniFold` from source `486e53e` (binary sha256
`61d7dfbf7ee3…`, `opt/bin/` — not a build-tree copy) on interactive allocation
56100487. Ran the full playlist-1A event loop with `MNV101_DUMP_POINTCLOUD=1` +
`MNV101_FULL_PHASE_SPACE=1` (canonical manifests). Attempt 1 died on provider-turn
exit (Claude background-Bash was not OS-detached; partial frozen at 18.4M/22.19M
truth entries, preserved isolated in `g2_smoke/work/`, never used as evidence).
Attempt 2 via a `setsid` OS-detached driver (SID==PID 576350, reparented to init)
ran to `rc=0` (~28 min, 21:52→22:20 UTC). Validator
`nd-unfolding/pet/validate_g2_fullevent_smoke.py` (retains the `uchar_value`
normalization for the PyROOT `UChar_t`→1-char-string binding) PASS **50/50** — see
VALIDATION_LEDGER 2026-07-18 for the verified counts/POT/hashes. Atomically
published (same-fs rename, hash-verified) →
`nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root`; tracked receipt
`G2_1A_VALIDATION_RECEIPT.json` written last. Added a fail-closed 12-playlist
launcher `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh` (NOT submitted; the
orchestrator queues it after inspecting the pushed commit). No MEFHC merge / NPZ /
PET training / scientific endpoint. Canonical `ND_OMNIFOLD_STATUS.md` left untouched
(dirty from another owner — PG0).

## 2026-07-18 — G2 production launcher hardened (fail-closed recovery correction)

Correction only (no science numbers; the 1A ROOT/receipt/validator are unchanged).
Independent verifiers (orchestrator + Gemini `agy-g2-gate-verifier`) blocked array
submission on `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh` recovery logic.
Rewrote the launcher fail-closed: publication state classified by existence (not
size) — one-sided/zero-length/malformed/mismatched/stale pairs DIE before compute,
published final/receipt never auto-overwritten; 24 canonical manifest + binary +
validator SHA-256 bound at commit time (drift rejected pre-compute); resume validates
schema/playlist/PASS/exact path+hash/binary/manifest/validator/env/n_failed/n_checks;
ROOT+receipt publication made no-clobber atomic (hardlink→verify→unlink; removed
`os.replace`/`mv -f`); built-source commit recorded separately from runtime HEAD.
Verified without event-loop compute (bash -n, embedded-Python compile, 24+2 hash
bind, state-matrix + no-clobber race — all PASS). Launcher committed+pushed, NOT
submitted; orchestrator + the same Gemini UUID recheck the corrective commit. Owner
label corrected to Agent-E + UUID (route claude-school).

## 2026-07-19 — G2 production task 4 blocked on upstream-corrupt 1D row

The one-shot r2 watcher emitted a real array ERROR for task 4 / playlist 1D.
One task-only accounting reconciliation found `FAILED 1:0` after 56m59s. The
event loop itself completed and preserved a 14,150,286,041-byte work ROOT, but
the prepublication validator failed 1/50 checks: background entry 16074,
identity `(111114,296,375)`, carries a 31.37-billion-MeV reconstructed muon.
Direct inspection of source AnaTuple `run00111114`, entry 109204, confirmed the
same native muon and MINOS values, so this is upstream corruption rather than a
G2 dump/conversion defect. Its reconstructed `(pT,p_parallel)` is
`(2,960,428, 31,233,701)` GeV, far outside the canonical extended FPS domain
`pT<=30`, `p_parallel<=120` GeV.

No final 1D ROOT or receipt exists. The committed launcher would mechanically
quarantine the partial safely, but an unchanged retry is deterministically
blocked because it would reproduce the same row. The exact recovery gate is an
additive exhaustive domain validator that binds known out-of-domain exclusions
and fails on any corrupt in-domain row, followed by independent verification
and no-clobber publication of the preserved work ROOT. Hash-bound canonical
files remain untouched while other array tasks drain. The same Gemini verifier
UUID independently returned BLOCK on unchanged retry. Durable evidence:
`docs/orchestration/state/g2-array-task4-blocker-20260719.json`.

## 2026-07-19 — G2 tasks 4/1D and 5/1E recovered without recomputation

The r3 one-shot wake reported task 5 / playlist 1E `FAILED 1:0` after 50m18s.
Its event loop completed, but the sampled base validator found one corrupt data
muon among its first 20,000 rows. Source AnaTuple run 16019 entry 12886 carries
the identical native values; the row is at `(pT,p_parallel)=(239,965,961,714)`
GeV, far outside the retained `[0,30] x [0,120]` GeV FPS domain. As for 1D, an
unchanged rerun was deterministically blocked.

An additive validator exhaustively scanned every live reco/data scalar and muon
row, failed closed on non-finite/sentinel/in-domain corruption or scalar--muon
mismatch, composed all non-superseded base structural checks, and bound every
out-of-domain row. It found 2,643 such rows in 1D and 2,162 in 1E; all
non-superseded checks passed. The same Gemini verifier UUID first blocked three
fail-closed defects (census cap, structural parse error, receipt race), then
returned PASS after repair and explicitly authorized publication. The preserved
ROOTs were no-clobber hardlinked, independently rehashed, and receipt-published
last with rc=0: 1D `06be7e68...` (14,150,286,041 B), 1E `6ab0ac90...`
(11,651,881,243 B). This is conditional Gate-1 evidence: the downstream input
builder must enforce the receipt domain before training. No event loop was
rerun, no active array task was touched, and no reset credit was consumed.
Evidence: `docs/orchestration/state/g2-domain-recovery-20260719.json`.

## 2026-07-19 — G2 tasks 6/1F and 12/1P recovered without recomputation

The r4 one-shot event reported only tasks 6 and 12 failed while tasks 9 and 10
were still running. Both event loops completed and preserved their work ROOTs;
only post-loop sampled validation failed. Playlist 1F failed
`bkg_reco_muon_valid` (49/50 total checks), while 1P failed the background and
data sampled muon checks (48/50 total). Unchanged retries were blocked as
deterministic and wasteful.

The exact committed exhaustive gate from the independently verified 1D/1E
recovery passed both preserved artifacts. It bound every out-of-domain row
(3,183 for 1F; 985 for 1P), found zero fatal or non-superseded structural
failures, and confirmed every finite corrupt muon row lies outside the retained
`[0,30] x [0,120]` GeV domain. No-clobber publication and independent final
SHA-256 checks passed with rc=0: 1F `b5e7c28f...` (16,299,560,962 B), 1P
`e986dab2...` (4,631,598,593 B). No event loop was rerun. As before, downstream
training is conditional on explicit retained-domain enforcement. Evidence:
`docs/orchestration/state/g2-domain-recovery-r4-20260719.json`.

## 2026-07-19 — G2 Gate 1A all-12 per-playlist production PASS

The r5 one-shot event reported COMPLETE/0:0 for the eight originally nonfailed
tasks. One full-array accounting reconciliation recorded those eight normal
completions and the four previously reconciled sampled-validator exits. A new
fail-closed validator then checked the exact twelve-playlist set, canonical
binary/validator/launcher/manifests and environment, production or recovery
receipt chains, every recovered census row, all supporting receipts, sizes, and
recomputed all twelve large ROOT SHA-256 values on the existing holder.

Result: PASS, 12 pairs, zero failures, 113,500,285,444 bytes. Aggregate counts:
`mc_truth_denom == mc_signal_reco = 49,906,108`, background `566,036`, data
`4,119,797`, native misses `20,361,799`, mcPOT `4.978198462880827e21`, dataPOT
`1.057394261158926e21`. The persistent Gemini verifier independently returned
PASS and authorized the evidence commit. This closes Gate 1A per-playlist
production only. Gate 1B remains the no-clobber MEFHC merge plus complete aligned
full-schema NPZ; recovered rows require explicit downstream `[0,30] x [0,120]`
GeV exclusion before training. No PET production was started. Evidence:
`docs/orchestration/state/g2-gate1-all12-validation-20260719.json`.

## 2026-07-19 — G2 Gate 1B MEFHC merge PASS

The existing interactive holder merged the twelve hash-bound Gate-1A ROOTs in
playlist order. A first fail-closed attempt exposed ROOT's additive treatment of
the boolean `hasTruthOnlyMisses` (merged value 12, contract value 1) and published
nothing. The corrected attempt required exactly twelve input flags, normalized
that one semantic boolean to 1, and reran the full validation. Result: PASS,
113,496,440,965 bytes, SHA-256 `9a16331f...`, exact aggregate count/POT agreement,
zero structural failures, and 21,797 retained-domain exclusions bound. Receipt
publication was last. The next dependency-ready action is the reviewed
three-inventory P=12 NPZ dump in long CPU batch; no PET training has started.

## 2026-07-19 — G2 full-schema NPZ job 56116598 failed before publication

The one-shot terminal event reported `FAILED 1:0` after 1h14m07s on
`nid004131`. The dumper completed its retained-domain scans and wrote a
transactional temporary NPZ containing 49,152,885 signal, 4,116,128 data, and
564,591 background rows. The subsequent receipt-header validator invoked
`/usr/bin/python3.11`, which lacks NumPy, and raised `ModuleNotFoundError`.
The launcher's EXIT trap removed the temporary NPZ and receipt; the final NPZ
and receipt paths remained absent, so Gate 1B did not advance.

Recovery changes only interpreter selection: after sourcing the analysis
environment, the launcher resolves executable `python3`, proves it imports
NumPy before hashing or dumping, and reuses that interpreter for both receipt
checks. An unchanged retry is forbidden; one retry is permitted only after the
fail-closed launcher and `g2-dump-56116598-failure.json` are committed. No PET
or Gate-2 work was started and every persistent worker UUID was preserved.

## 2026-07-19 — G2 Gate 1B full-schema NPZ PASS

The committed fail-closed recovery launcher ran as singleton job `56120687`
and completed `0:0` in 1h09m47s on `nid004123`. It published the product first
and receipt last: `G2_FPS_MEFHC_P12.npz`, 9,897,374,636 bytes, SHA-256
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`.
Inventories contain 49,152,885 signal rows (20,573,521 pass reco; 49,150,928
pass truth), 4,116,128 data rows, and 564,591 background rows.

An independent compute-node validator rehashed the whole NPZ, reproduced all
42 member headers and the exact full-event schema markers, enforced the
canonical extended edges and `[0,30] x [0,120]` GeV retained domain, checked
miss sentinel guarding and POT consistency, and recomputed all three ordered
inventory hashes. Result: PASS, zero failures. This closes Gate 1. The next
dependency-ready action is Gate-2 literal `negweight-refined` target
construction; PET training remains forbidden until its own gate passes.

## 2026-07-19 — Gate-2 negweight-refined construction implemented (runtime pending)

The same persistent Agent-B UUID repaired the full-event loader to derive data
rows from `measured_pc`, construct the complete signed data plus literal
POT-scaled background-cloud inventory, apply coherent factors before each
replica's refinement, concatenate aligned measured features, and emit target
identity/sum/floor/fingerprint telemetry. Missing or tampered schema,
identities, POT, weights, clouds, alignment, and replica seeds fail closed.

Independent orchestrator execution passed 95 login-safe tests: 28 focused
Gate-2 tests plus 67 existing full-event/G2 contract tests. The fixture reaches
the real NumPy DataLoader boundary and independently checks the binned signed
and refined sums. This is construction evidence, not Gate-2 closure: the
deferred canonical `u2d.refine_stay_positive` has not yet run on the production
G2 NPZ in a ROOT-capable compute environment. No PET training was started.

## 2026-07-19 — G2 Gate 2 exact target runtime PASS

The queue hedge selected interactive holder `56140225`. After two changed,
fail-closed repairs (empty staging-file acceptance, then bypassing a
TensorFlow-dependent package initializer while loading the exact NumPy
dataloader source), run `gate2-target-r4` completed in 678.7 s and atomically
published weights first and its receipt last. The exact learned canonical
backend consumed all 4,116,128 data and 564,591 background rows; the final
4,680,719-row target is finite, nonnegative, normalized, and hash-bound.

A separate read-only validator rehashed the 9.9-GB input, output and code,
recomputed the locked configuration and signed-target hashes, and reproduced
the full 15x19 binned telemetry with zero failures. The same preserved agy
Gate-2 verifier UUID independently returned PASS; Agent B needed no correction.
Gate 2 is promoted. No PET training or Gate-3 production was started in this
wake. Evidence: `docs/orchestration/state/gate2-target-r4-reconciliation-20260719.json`.

## 2026-07-20 — P3F-scalar complete historical interface inventory PASS

The corrected third wrapper attempt, Slurm job `56163874`, completed `0:0` in
12m46s on `nid004130`. It ran validator commit
`c06d07e246ac430b98fdacac9808ab59174bc33e` with validator SHA-256
`678e4b15161ab7370fed5db42dddae2f8a97b8404ef30f87908ad72b974397e7`
and emitted the complete historical manifest without touching the stale
canonical path. The two earlier attempts remained prestart cancellations; no
physics ROOT was regenerated.

Independent reconstruction verified 120/120 SHA-bound files, zero missing,
extras, or failures, 120 unique producer-log hashes, exact producer split
`55961845`:1 plus `55972324`:119, per-file `COMPLETED/0:0`, all four migration
census fields, endpoint identities, four-tree schemas, POT, completeness,
native misses, and signal/background/data point-cloud contracts. The preserved
`agy-publication-redteam` UUID returned PASS and required no Agent-C correction.

The exact audited manifest (SHA-256 `8f957bf251728a7de57d4fe2ea8d00c2010c23d151e6c9c0a96d3ec31d4e60a8`)
was promoted to `active_universe_5d/fps/p3s_fps_manifest.json`; the superseded
4/120 incomplete manifest was retained in `preflight/archive/`. This commits
the P3F-scalar interface prerequisite only. P3F-PET source generation and PET
training were not started in this wake. Evidence:
`docs/orchestration/state/p3f-scalar-fullaudit-promotion-20260720.json`.

## 2026-07-20 — P3F-PET Gate-3 source-production code gate PASS

The real initialization deadline event was consumed exactly once after a
10-minute model-quiet interval. Preflight found no active compute writer, no
interactive allocation, no pre-existing P3F-PET full-event namespace, and an
exact frozen 5-band x 2-endpoint x 12-playlist inventory. Fresh generation is
required: the historical scalar endpoints were produced by the older binary
and remain controls only.

The preserved Agent-B and Agent-C UUIDs produced the full-schema endpoint
validator and collision-isolated batch launcher. Independent integration
closed the known 1D/1E/1F/1P out-of-domain composition issue, embedded the
complete atomic validation packet in each final receipt, and made both initial
publication and resume fail closed on binary/source/manifest/active-census and
nested validator evidence. The first same-UUID agy review overclaimed terminal
accounting and missed null report fields; that verdict was rejected, repaired,
and the same UUID returned PASS on the corrected bytes. All 146 frozen contract
regressions and 29 launcher tests pass, including an executable synthetic
receipt/resume/tamper round trip. This is code authorization only; Gate 3 is
open and nominal PET training remains prohibited. Evidence:
`docs/orchestration/state/p3f-pet-gate3-launch-code-gate-20260720.json`.

The code gate was committed and pushed at `784e360`. Fresh source array
`56169838` was then submitted as `0-119%16` on shared CPU with 4 requested
CPUs, 48 GiB, and 12 hours per task. The 48-GiB request is evidence-based:
prior full-event tasks reached roughly 37 GiB MaxRSS, so the older 16-GiB
scalar footing is unsafe. No interactive duplicate exists. Canonical terminal
and one-hour queue-latency watches are armed; Slurm and the external waker now
own progress without model polling. Gate 3 remains open and nominal PET is
still prohibited. Submission evidence:
`docs/orchestration/state/p3f-pet-gate3-source-submit-56169838.json`.

At the one-hour queue-latency wake, canonical per-task accounting disproved the
watch prompt's wholly-pending premise: tasks 0--14 had already completed
`0:0`, each with a matching PASS ROOT/receipt pair, while tasks 15--119 were
pending and no task was in an error state. Batch `56169838` therefore remains
the sole writer; it was not cancelled and no interactive allocation was
started. The wake exposed a control-plane bug in which completed array elements
had disappeared from `squeue`; `wakerctl` now requires allocation-level
`sacct` proof that no element ever started and auto-disarms latency watches
once start evidence exists. All 93 orchestration tests pass. The terminal array
watch remains armed, Gate 3 stays open, and nominal PET remains prohibited.
Evidence: `docs/orchestration/state/p3f-pet-gate3-queue-latency-reconciliation-56169838.json`.

## 2026-07-24 — Delta full-stats xps2 recoil PET training COMPLETE (shutdown insurance; not Gate-4/P5A)

During the Perlmutter maintenance window, the extended-phase-space (`xps2`)
**recoil-only** PET training completed on NCSA Delta. Job `20445933` ran on
`gpua012` under an 18-hour limit and finished `COMPLETED 0:0` in 9h32m32s on
4xA100 in the NGC `tensorflow:24.01-tf2-py3` container (TF 2.14.0, horovod
0.28.1). Recipe as frozen: `--niter 5 --epochs 8 --max-events 40000000`,
launcher seed 101, estimator seed 42. Per rank the loaders reported data
1,029,032 rows and MC 10,000,000 rows (4 ranks = 4.12M data / 40M MC), with
`pass_reco` 0.418-0.419.

Reweight-all over the complete generator set (`n=49,152,885`) gave push weights
`mean=1.0021 std=0.1588 finite=True`; the F3 logit-space cap of 30.0 saturated
`0/49152885` rows with weight-mass sum 4.9255e+07 and max 2.3737. A scan of the
79 MB job log for `traceback|error|nan|diverg` returns zero matches, and all
five OmniFold iterations are present. Output
`products/pet/pet_weights_fps_xps2_delta_s101.npz` (sha256 `9a09125f...f0c5`,
266,051,960 bytes) currently exists **only** on Delta `/u/jbailey2`; the NERSC
DTN outage extends past the Perlmutter restore date, so CFS staging is deferred.
The staged input hashes `dfd52750...812`, bit-identical to the Perlmutter input
already recorded in `docs/orchestration/RUNS.tsv`, so the transfer is
provenance-clean.

Getting there took four attempts and one real fix. `20412941` failed in 20s on
container/env setup; `20413251` completed the 10M fast check on `gpua059` in
2h44; the first full-stats attempt `20416508` hit the launcher's default 12-hour
wall on `gpua065` and was killed at `TIMEOUT`. Commit `c752d65` diagnosed the
cause as horovod slot allocation: the container's OpenMPI is not built with
SLURM PMI, so with `--ntasks-per-node=1` it could neither bootstrap through
SLURM nor size a 4-rank allocation from it, and setting `OMPI_MCA_plm=isolated`
together with `ras=^slurm` makes mpirun treat the node as standalone and fork
NP local ranks over NVLink/NCCL. With that fix and an 18-hour limit the same
40M recipe fit comfortably.

**Scope, stated explicitly.** This is the recoil-only `xps2` representation
cross-check and **not** a publication result. Per the artifact guard in
`docs/OPEN_ITEMS.md`, `of_inputs_pc_fps_xps2.npz` is not a full-event
publication input, so this run neither is nor advances the Gate-4/P5A full-event
nominal; the Gate-4 launcher remains `PASS_CODE_ONLY` with training unlaunched.
TF 2.14 on Delta A100 is not the authoritative TF 2.15 Perlmutter footing. No
extraction has been run against these weights, so **no cross-section number
exists** from this run. The matched GPU-floor repeat has not been run, so the
GPU-nondeterminism floor is unbounded and no spread from this run is
interpretable. Evidence: `docs/orchestration/RUNS.tsv` row
`DELTA-PET-FPS-XPS2-FULLSTATS`; job log
`/u/jbailey2/MINERvA-OmniFold/nd-unfolding/pet_train_fps_delta_20445933.out`.

## 2026-07-25 — Weight-level diagnostics on the Delta xps2 nominal (no allocation; still no floor)

The `20445933` push weights were pulled off Delta and characterized locally in
NumPy — no GPU, no allocation, no login-node compute. The transferred copy
hashes `9a09125f...f0c5` and reproduces the job log exactly (`mean=1.002075`,
`std=0.158825`, `sum=4.925490e+07`, `max=2.373705`), so the diagnostics are on
the real artifact. Full numbers:
`products/pet/pet_weights_fps_xps2_delta_s101.diagnostics.json`.

**Weight health.** Over all 49,152,885 generator rows the estimator retains
`ESS=4.7948e+07`, i.e. **ESS/n = 0.9755**, with weights confined to
`[0.409543, 2.373705]` and median 0.9886 (IQR 0.9105-1.0519). There are zero
non-finite, zero zero-valued and zero negative weights, so coverage is complete.
Tails are mild: `w>1.5` is 1.29% of events carrying 2.14% of the weight mass,
`w>2.0` is 0.044% carrying 0.092%, and **nothing exceeds 2.5**. The F3
logit-space cap of 30.0 is therefore inert by an enormous margin, and even a
drastic tightening to `w<=2.0` would touch 0.044% of events. `pass_truth` holds
for 49,150,928 of 49,152,885 rows (1,957 failing). This rehearses two P5A gate
requirements — finite/full-coverage weights and cap sensitivity — on real
full-stats weights. Note for extraction: the push weights sum 0.21% above unity,
so absolute normalization is not automatically preserved.

**10M-versus-40M convergence (not a floor).** Against the `20413251` fast check
on the same aligned rows and identical `mc_indices`, the two runs give Pearson
`r=0.914933`, total ratio 0.976460, per-event mean `|w40/w10 - 1| = 4.3870%`
(median 2.6812%) and `L1/sum = 4.4833%`. The 10M estimator is materially
different rather than merely noisier: `std` 0.124882 versus 0.158825 and `max`
1.875093 versus 2.373705. This is quantitative grounds for running the matched
GPU-floor repeat at the **nominal 40M configuration**; a 10M repeat would
characterize a different estimator, and the nondeterminism it is meant to
isolate would be swamped by the 4.4% statistics gap it introduces. An earlier
suggestion in this campaign to economize with a 10M repeat is therefore
withdrawn.

**Status unchanged.** These are diagnostics of the recoil-only `xps2`
cross-check, not publication numbers. No cross section has been extracted, and
with no matched repeat yet the GPU-nondeterminism floor remains unbounded. When
`pet_weights_fps_xps2_delta_s101_rep.npz` lands, the floor metrics are
`std(w_rep - w_nom)` and `L1/sum` on these same 49,152,885 aligned rows, and
must come in far below 4.4833% to be credible as nondeterminism-only — bearing
in mind the repeat will land on a different node, so it bounds nondeterminism
plus node-to-node variation.

## 2026-07-26 — Full-event (Gate-4/P5A) code path exercised on a synthetic fixture; two blockers found

Delta CPU job `20489224`, `COMPLETED 0:0` in 00:01:29 on `cn093`, commit `b5ec859`.
**Synthetic random data. Not a physics result, not the P5A closure receipt.**

**Why this ran.** `build_fullevent_loaders` fail-closes on any input that is not a
`g2-fullevent-v1` NPZ, and the only such file is `G2_FPS_MEFHC_P12.npz` on Perlmutter
`/pscratch`. During the 2026-07-22..08-03 maintenance nothing on Delta could reach the
full-event code path at all, so every latent launch defect was scheduled to surface on
08-04 instead of now. `pet/make_synthetic_g2_fullevent.py` removes that blind spot; it
writes through `fullevent_dump_contract.write_fullevent_npz_atomic`, so the fixture is
validated by the same schema/manifest/alignment/identity/no-purity gates as a real dump.

**What executed.** Negweight-refined target construction: 12000 data + 4000 bkg = 16000
measured rows, `raw_positive_sum` 12000.0, `raw_negative_sum` 406.996, `refined_sum`
11592.864 (= 12000 − 407.0), 58 rows floored to zero, `pot_scale` 0.1; all three stored
identity hashes recomputed and matched; CLM-007 satisfied from `measured_scalars`; clouds
built as reco (n,40,3) coord (1,2) and gen (n,40,8) coord (5,6,7). Ordinary closure
(purity control): push mean 0.9985, median 0.9979, std 0.0090, all finite; (pT,p‖)
marginal L1 0.0035; normalization deviation 0.0015.

**How much this closure is worth: little, by construction.** On random features there is
no structure to learn and the pseudo-data *is* the MC, so push ≈ 1 is nearly guaranteed
whether or not the estimator is correct. The PASS shows the code path runs end to end. It
has close to zero power to detect a real estimator defect, and is the same category of
weak control as the degenerate Gate-2 spatial check. The verdict line is tagged
`[SYNTHETIC FIXTURE - PLUMBING ONLY, NOT THE P5A RECEIPT] [purity control]` so it cannot
be harvested later as evidence.

**Blocker 1 — the P5A closure has been dead since 2026-07-19.**
`pet/closure_fullevent_fps.py` was committed at `9d7a4c6` (07-18) passing the recoil-only
`of_inputs_pc_fps_xps2.npz` with `bkg_mode="purity"`. The `g2-fullevent-v1` schema gate
landed the next day (`01d324a`) and rejects exactly that input. Verified by replaying the
staged xps2 member set (18 members, no `petSchemaVersion`) through the loader: raises
`[G2] input is not a g2-fullevent-v1 schema NPZ`. **The closure PASS recorded at `36ab84d`
was therefore obtained against the pre-gate dataloader and does not certify the current
code path.** The script is repaired in `b5ec859` (repo root from `__file__`, CLI recipe,
G2 default, negweight-refined default, synthetic tagging) but the receipt is only
reinstated by re-running against the real dump after the restore.

**Blocker 2 — the publication nominal cannot run on Delta at all.** The NGC container has
no ROOT (`sklearn 1.2.0`, `TF 2.14.0`, `horovod 0.28.1`, `numpy 1.24.4` present; `ROOT`
absent). `u2d.refine_stay_positive` — the canonical Stay-Positive refiner the
negweight-refined nominal requires — imports ROOT at module load. Delta can therefore run
only the purity control or an injected sklearn refinement, and the latter self-reports
`refinement_is_learned_production=False`. This holds **even after the data is staged**, so
the Gate-4 Delta port cannot deliver a publication nominal; it can only pre-validate the
launch path. Any P5A nominal must run on Perlmutter under TF 2.15.

**Gate-2 units question — failure modes now settled empirically** (the substantive answer
still needs the real dump). On known-unit inputs: dividing GeV scalars by 1000 retains
500/500 rows inside the canonical FPS grid, so the domain guard at
`gate2_target_runtime.py:432-435` passes silently and the `rel_l1`/`max_rel`/`cosine`
comparisons run on two identically-misscaled histograms; the pass-through patch on MeV
input retains 0/500 and dies loudly. The resolution procedure cannot return an ambiguous
answer.

Status unchanged: Gate-4 remains PASS_CODE_ONLY, P5A unlaunched, no cross section
extracted, the recoil xps2 GPU-nondeterminism floor still unbounded pending `20488861`.

## 2026-07-28 — GPU-nondeterminism floor BOUNDED; binning suppresses it rather than amplifying

The matched 40M repeat `20488861` completed `0:0` in 09:38:51 on **`gpua072`** — a
different node from the nominal `20445933` (`gpua012`, 09:32:32), so what follows bounds
nondeterminism **plus** node-to-node variation, as intended. The recipe echo confirms the
nominal configuration verbatim (`np=4 niter=5 epochs=8 train=40000000 seed=101`, estimator
seed 42, same `of_inputs_pc_fps_xps2.npz`), so there is no `--export=ALL` leakage; all five
iterations ran, no traceback, and the full-stats reweight covered all 49,152,885 rows.
`mc_indices` is bit-identical between the two runs, so the comparison is genuinely
row-aligned rather than merely same-length. The nominal artifact was **not** overwritten
(sha `9a09125f…` unchanged); the repeat is `85b595b2…`, 266,046,028 bytes.

**Per-event floor.** `L1/sum = 0.2060%` against the `4.4833%` 10M-vs-40M bar — **4.6% of
it, a 21.8x separation** — with `std(w_rep − w_nom) = 0.003572` (against a weight std of
0.1588), Pearson `r = 0.9997494` (vs `0.914933` for 10M-vs-40M) and total ratio `0.9997729`.
Zero non-finite, zero negative, zero zero-valued weights. The two trainings are the same
estimator to well within the statistics gap, so the floor is credible as nondeterminism-only
and the earlier decision to run the repeat at the nominal 40M rather than economizing at
10M is vindicated: a 10M repeat would have been swamped.

**Per-bin floor — the number that actually propagates.** A per-event floor is not what
enters a cross section; the binned spectrum is. Summing `w_truth * w_push` over `pass_truth`
events into the canonical extended FPS grid (15 pT x 19 p‖ = 285 bins, 266 occupied) gives
`L1/sum = 0.0349%`, **a further ~5.9x suppression** below the per-event 0.2060%. Per-bin
`|rel|` is median 0.0283%, mean 0.0571%, p99 0.4994%, max **0.6033%**. **No occupied bin
exceeds 1%**, and only 3 of 266 exceed 0.5%. Binning averages the per-event jitter down
rather than concentrating it.

**The prior expectation about where the risk sat was wrong.** The concern going in was the
outer catch bins — pT `4.5–30` and p‖ `60–120` — on the reasoning that sparse bins would
concentrate the tail events driving the per-event `max_abs_rel` of 14.89%. They are in fact
among the quieter regions: the pT catch row maxes at `0.2758%` (439 events), the p‖ catch
column at `0.2463%` (6,889 events), and the outer corner is `−0.0651%` (12 events). All
three worst bins are instead in the **pT `2.5–4.5` band at moderate p‖** — `[4.0,4.5]` with
44 events at `−0.6033%`, `[3.0,3.5]` with 2 events at `−0.5621%`, `[3.5,4.0]` with 11 events
at `−0.5233%`. The driver is raw sparsity (the least-occupied bin holds a single event), not
position on the grid, and the catch bins escape precisely because they are wide enough to
accumulate events. Every worst bin carries a negative sign, consistent with the global
total ratio of 0.9997729.

**Consequence for P5A.** The floor does not limit any extraction at this grid, so no third
repeat is justified: decomposing a 0.2% per-event / 0.035% per-bin effect into kernel-level
versus node-to-node parts would buy nothing, and `docs/OPEN_ITEMS.md` bars extending the
recoil-only campaign regardless. The transferable methodological result is that per-bin
floors must be quoted alongside per-event ones and that sparse-bin occupancy, not grid
position, predicts where reproducibility degrades — worth re-checking on the full-event
estimator, whose occupancy pattern will differ.

**Scope.** Recoil-only `xps2` cross-check. Not a covariance component, not a publication
number, not Gate-4/P5A (`is_publication_result=False` in both receipts). Gate-4 remains
PASS_CODE_ONLY, P5A unlaunched, no cross section extracted. Receipt:
`products/pet/pet_weights_fps_xps2_delta_s101_floor.json`; reproducer
`pet/floor_gpu_nondeterminism.py` (6m14s, 4.13 GiB peak on the Delta login node).

## 2026-07-28/29 — Host memory BOUNDED but thin; full-event audit finds Gate-4's CLI evaluates none of its physics checks

**Host-memory ladder.** Delta CPU job `20558496`, `COMPLETED 0:0`, 00:41:27 on `cn126`,
commit `68f1291`, ~11 CPU-hr. Five rungs at `--tokens 12` (the real dump's slot count, not
the generator's default 40), each with `max_events = 0.8138 x rows` so the
materialize-then-subsample pattern at `fullevent_fps_dataloader.py:520-521` is reproduced at
every scale. Peak RSS scales cleanly linearly —
`peak_GiB = 1.238e-6 * rows + 0.239` — from 0.766 GiB at 200k rows to 25.078 GiB at 20M,
with the high-water mark landing at `after_build_truth_cloud_1` at every rung.

Production (rows 49,152,885, max_events 40M) extrapolates to **~61 GiB per rank, ~246 GiB
across 4 ranks against a 251.6 GiB node — ~98% of capacity.**

**The prior projection was wrong in magnitude, right in location.** The ~78 GiB/rank hand
estimate that predicted a ~310 GiB hard OOM was ~25% high: it assumed the full-size numpy
temporaries inside `build_truth_cloud` all coexist at peak, and they are freed as the
expression evaluates. **But this is not a clearance to launch.** The measurement was on a
CPU node, so it excludes the host memory each rank pins for its CUDA context and TF's GPU
allocator; ~246 GiB is a lower bound, and ~1.5 GiB/rank of GPU-side overhead would consume
the entire remaining margin. Separately, `sacct` reported `MaxRSS 14.45 GiB` for a job whose
largest rung measured 25.08 GiB by `VmHWM` — `sacct MaxRSS` undersamples and must not be
used to size this. Synthetic fixtures and a non-production refiner: memory only.

**Full-event audit.** 13-agent orchestrated audit across six dimensions (unfolding,
negative weights/Stay-Positive, closure and test POWER, covariance, binning/mask/leakage,
code contracts and provenance), each dimension's findings put through an adversarial
refutation pass: **43 findings survived, 8 refuted, 5 blockers, 14 majors.** Report:
`docs/orchestration/AUDIT-FINDINGS-20260728.md`.

Two blockers were independently verified by the orchestrating session against the code
rather than taken on the agents' word:

1. **The Gate-4 CLI validator evaluates none of its four physics checks.**
   `validate_pet_nominal_gate4.py:223-229` calls `build_gate4_report` with no `marginal=`,
   `normalization=`, `saturation_frac=` or `closure=`, and `:169-176` silently skips every
   component whose argument is `None`. Worse, `:218-222` builds `frozen_observed` by copying
   `FROZEN["edges_pt"]`, `FROZEN["edges_pparallel"]`, `FROZEN["bin_order"]` and
   `FROZEN["seed_policy"]` into the "observed" dict, so `check_freeze` compares FROZEN to
   FROZEN. What remains is finiteness/coverage and index order, and
   `verdict = bool(checks) and all(...)` then returns PASS. Gate-4's PASS_CODE_ONLY status
   rests on a validator that cannot fail for physics reasons.

2. **`normalize=True` on both full-event loaders makes the unfold shape-only.**
   `fullevent_fps_dataloader.py:613` and `:658` both pass `normalize=True`;
   `omnifold_nn/omnifold/dataloader.py:110-113` rescales each loader's weights so the
   `pass_reco` sum equals 1e6, and `omnifold_nn/omnifold/omnifold.py:176-177` weights the
   step-1 classes by exactly those sums — so the POT-scaled data-vs-MC rate difference is
   gone at iteration 0 and nothing restores it. The repo documents this exact failure mode
   against itself: `omnifold_nn_core.py`'s `_balance_weights` docstring says that without
   multiplying the ratio back "the unfolded normalization collapses", and `_class_ratio`
   exists specifically as "the normalization to restore" — which the reference loop does and
   the full-event path does not. This is a testable candidate explanation for the ~10%
   PET/GBDT normalization gap the log currently attributes to under-iteration (`:919`
   records the higher-iteration retrain as "essentially flat", which fits this cause and not
   that one). Magnitude remains unverified; the audit proposes a login-safe scalar check on
   the real dump.

Status unchanged by this entry: Gate-4 remains PASS_CODE_ONLY, P5A unlaunched, no cross
section extracted. The audit is a code-and-methodology read; the real G2 dump was never
exercised, since Perlmutter is down until 08-03.

## 2026-07-29 — B1 adversarial re-verification: my own proposed fix was WRONG, and the ~10% PET/GBDT gap is explained by measured data already in this log

Four independent adversarial referees (three Claude Code subagents, one Gemini 3.1 Pro via
`agentctl` role `refute-fe-norm-physics-agy`), each instructed to default to REFUTED,
re-examined the B1 finding and the fix proposed for it in the previous entry. The mechanism
survived. **The proposed fix did not, and neither did the reasoning I used to justify it.**
Codex profiles were unreachable for this round (no `codex-homes/*` on the local machine) and
`claude-school` was unauthenticated, so the external cross-check is Gemini-only.

**The mechanism is CONFIRMED, and it is not a code-reading conjecture — it is already the
measured behavior of the recoil-only PET result.** `dataloader.py:110-113` rescales
`self.weight` in place (verified by executing the vendored module: `normalize=True` gives
`weight.sum() = 999999.96`, omitted gives the raw `15.0`, and `weight.base is caller_array`);
`omnifold.py:176-177` feeds exactly those arrays as the two step-1 class blocks, so W1/W0 == 1
at iteration 0. Step 2 (`omnifold.py:196-197`) trains on the same points and transmits
whatever rate `w_pull` carries without creating any, and the efficiency handling
(`:184-187`) only pins off-acceptance weights to 1. Nothing restores the ratio.

**This falsifies this log's own stated interpretation of the PET/GBDT gap.** `:466` records
`mean(w_push) = 1.0277` and the higher-iteration retrain records `1.0101` — it FELL.
Under-iteration predicts it *rising* toward the data's demand of 1.135 (`:930`, GBDT
data/CV). PET/CV is therefore 1.035 then 1.018, and 1.018/1.135 = 0.897, reproducing the
reported `PET/GBDT = 0.8970` (`:913`) to three digits. The entry at `:917-921` attributing
the gap to under-iteration should be treated as superseded: the normalization erasure
accounts for it quantitatively, on real MEFHC data, with no new run required.

**REFUTED — "keep shape-only and restore the yield ratio at extraction" is not a fix.** The
decisive line is `omnifold.py:185`, `new_weights = np.ones_like(self.weights_pull)`, with
only `[pass_reco]` receiving the classifier ratio. Off-acceptance events are pinned at 1 in
BOTH the correct and the normalized run — the normalized run does not carry `1/R` there. So
the loop is not scale-equivariant in the step-1 output: with `a(z)` the local reco
acceptance, step 2's optimum is `push'(z) = 1 + a(z)(R-1)` against `push(z) = 1`, and since
completeness (`pet_systematics_5d.py:146-152,161`) is built from `w_truth` only and is
identical in both runs, the per-bin ratio is

    sigma_correct(bin) / sigma_shape-only(bin) = 1 + a(bin) * (R - 1)

a function of acceptance, not a constant. No global scalar recovers it. With `R-1 ~ 0.10-0.19`
and global row acceptance 20,404,292/32,849,103 = 0.621
(`products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.summary.json:17-18`) and real per-bin spread,
the irreducible residual is a **few-percent bin-to-bin distortion correlated with
completeness — worst exactly in the low-completeness FPS-extension cells that are this
measurement's novelty**. Area-normalizing does not remove it, so "publish it as shape-only"
is not a safe harbor either. The error is better described as an acceptance-multiplicative
error than as a lost normalization.

**Also REFUTED — "just delete `normalize=True`" is wrong, for a reason not previously
identified.** The nominal trains on a bounded 2M MC subsample
(`validate_pet_nominal_gate4.py:55-56`) while the measured target is the FULL data+background
inventory (`fullevent_fps_dataloader.py:645-659`). With `normalize=False` the step-1 class
ratio becomes the arbitrary MC *sampling fraction*, not `R` — strictly worse than 1.
`normalize=True` is load-bearing.

**Correction to the previous entry's reasoning.** I cited `_balance_weights`/`_class_ratio`
as precedent for restoring normalization at extraction. That is backwards on two counts.
(1) `_balance_weights` is an *optimization* fix — its docstring (`omnifold_nn_core.py:158-169`)
attributes the ~1e-6 collapse to an MLP falling into the trivial bias solution — and
`_class_ratio` exists to undo `_balance_weights`' own side effect; neither concerns the
DataLoader, which the reference loop never constructs. (2) The restoration is **in-loop, per
step, per iteration**: `fit_reweight` recomputes `_class_ratio` from the current step's
weights at `:233` and applies it at `:246`, and is called twice per iteration (`:257`,
`:266`). The precedent therefore mandates carrying the ratio through the loop, not patching
the result afterward.

**The fix consistent with both the physics and the precedent** is to make the step-1 class
ratio equal the physical `R` computed from full-inventory POT-scaled sums: keep the MC loader
at 1e6 and pass `normalization_factor = 1e6 * R` to the data loader — the argument already
exists at `dataloader.py:13` — or restore in-loop as `omnifold_nn_core.py:246` does. That
preserves subsample invariance and the rate, and needs no change to the vendored mechanism.

**Two gates currently entrench the defect.** `gate2_target_runtime.py:411-412` and `:442-443`
hard-assert the step-1 target sums to exactly 1e6 (`rtol=3e-6, atol=2.0`), and Gate-4's
`check_normalization` (`validate_pet_nominal_gate4.py:107-110`) requires
`|sum(w*push)/sum(w) - 1| <= 1e-3` (`:61`). **A correctly normalized unfold moves the rate by
~13.5% and would FAIL that Gate-4 contract by two orders of magnitude, while the broken one
passes it.** Combined with the separately confirmed finding that the Gate-4 CLI never passes
`normalization=` at all, the contract as written cannot detect this and would reject its fix.

**Collateral corrections to the previous entry's Delta claim.** The conclusion (no canonical
Gate-2 on Delta) stands, but three of the four reasons given were wrong: the backend-string
check at `gate2_target_runtime.py:400` is derived from the same `refine_fn is None` predicate
as `:398` and is not an independent barrier; `refine_stay_positive` itself is pure
NumPy+sklearn and never touches ROOT (the module-level `import ROOT` at
`unfold_2d_omnifold_unbinned.py:21` is an accident of file layout); and the identity-hash
guard at `:402` binds *bytes, not a filesystem*, so a staged byte-identical copy would satisfy
it. The genuine code-enforced blocker is the hardcoded, non-overridable
`REPO = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold")` at `gate2_target_runtime.py:35`
(also `fullevent_fps_dataloader.py:40`), which dies at `:209` before ROOT is ever reached.
Framing this as "code, not policy" was also a false dichotomy — `RESTORE-2026-08-03.md:198-206`
HARD BAR #1 states the policy explicitly.

**Audit weakness recorded.** `refinement_is_learned_production` asserts only that no refiner
was *injected* (`fullevent_fps_dataloader.py:664` = `refine_fn is None`); monkeypatching
`fed.learned_stay_positive_refiner` keeps the flag `True` while a substitute runs. The
validator *records* but does not *assert* the loader/u2d sha256 (`:481-486`); the only sha
freeze is in the shell wrapper (`run_gate2_target_validator.sh:19-21,39-41`).

**New tool, login-safe and read-only:** `nd-unfolding/pet/check_step1_class_ratio.py` measures
`R` from the frozen dump reading only small 1-D members (never the point clouds). It is
fail-closed against the promoted Gate-2 receipt: it recomputes the signed-data numerator and
refuses to report `R` unless that reproduces `raw_signed_sum = 4006528.6006158064`. Verified
both paths against a synthetic fixture built to the receipt constants — valid input reports
`R` and the receipt check `OK`; a 10%-perturbed background exits 1 with
`numerator ... does not reproduce ...`. Note `w_truth` in the G2 npz is RAW, not POT-scaled
(`fullevent_fps_dataloader.py:551`; convention at `dump_pointcloud_inputs.py:183-186`), so the
physical denominator is `pot_scale * sum(w_truth[pass_reco])`; the script reports both
conventions because they differ by `1/pot_scale ~ 4.7x`.

Status unchanged: Gate-4 remains PASS_CODE_ONLY, P5A unlaunched, no cross section extracted,
`R` still unmeasured pending the 08-03 restore. What changed is the decision: **B1 option (b)
is off the table on physics grounds, option (a) as previously stated is also wrong, and the
target is now the `1e6 * R` / in-loop variant.**

## 2026-07-29 — B1 fix design recorded; two corrections to the previous entry

`docs/orchestration/B1-NORMALIZATION-FIX-DESIGN.md` now holds the proposed resolution, its
rationale, the rejected alternatives with reasons, the required tests, and the sequencing.
Nothing implemented; no frozen file touched.

Two corrections to the entry above.

**(1) The fix is `1e6 * R` on the measured loader, not `normalize=False` on both.** Keeping
the MC loader normalized to 1e6 makes the class ratio subsample-invariant for free — which
matters because the nominal trains on a bounded 2M MC subsample against a full measured
inventory — and it keeps absolute weight magnitudes in the same well-conditioned range as the
currently-working configuration. `normalization_factor` is already a DataLoader argument
(`omnifold_nn/omnifold/dataloader.py:13`, default 1e6, applied at `:113`), so the vendored
engine needs no change. `R` is computed *inside* the loader from full-inventory POT-scaled
sums, never piped or hardcoded: each bootstrap replica has its own yield ratio, so a frozen
constant would be wrong for every replica but the nominal.

**(2) Gate-4's `check_normalization` must be REPLACED, not retargeted to ~R.** The earlier
entry's "retarget to ~R" is wrong. `normalization=(sum_w_push, sum_w)`
(`validate_pet_nominal_gate4.py:160`) is a **truth-level** pair, and at truth level — over the
full population including off-acceptance events where `push == 1` — a correct unfold gives
`sum(w*push)/sum(w) -> 1 + <a>_w*(R-1)`, i.e. ~1.08 with row-fraction acceptance 0.621, not
`R`. That target depends on the acceptance, i.e. on the quantity being measured. The correct
check is a reco-level folded-forward closure: require
`pot_scale * sum(w_truth*push over pass_reco) == n_data - pot_scale*sum(w_bkg)`. That target
is measured rather than modelled, and it fails the current broken result while passing a
corrected one.

Also recorded: Gate-2's `learned_vs_normalized_clipped_*` telemetry is invariant under
retargeting the constant from `1e6` to `1e6*R` (both histograms renormalize to the same value
and `rel_l1` divides by it), so no diagnostic content is lost; and the dominant 08-03 hazard
is a *partial* fix — correcting the loader while leaving the hardcoded Gate-2 (`:411-412`,
`:442-443`) and Gate-4 assertions in place, so the corrected ~13.5% shift aborts the pipeline
inside the tight restore window. Section 2 of the design doc is entirely code-only and should
land before the restore.

### 2026-07-29 — audit pass B reviewed; two more corrections to the B1 fix design

`docs/orchestration/AUDIT-FINDINGS-20260729-B.md` (four-lane parallel audit, one lane
discarded) was reviewed and its load-bearing claims re-verified independently on this host
rather than relayed. Confirmed by direct execution: the suite baseline is exactly
**7 failed / 333 passed / 1 skipped**, all seven from the `/pscratch` literal at
`gate2_target_runtime.py:56` (so the document's §4 mutation matrix rests on a real baseline);
no JSON in the repo names `omnifold_nn/omnifold/net.py` or `omnifold.py` and
`verify_hash_bindings.py` resolves neither (B-1); all three cited independent-verification
transcripts have **zero** `git log --diff-filter=A` commits and 2026-07-21 is a hole in the
committed transcript dates (B-2); `w_reco` occurrence count in the full-event loader is 0 while
the 2D path uses both legs at `unfold_2d_omnifold_unbinned.py:1715-1716` (B-4); the eight
full-event arrays all have loader count 0 (B-3); `stress_closure_muon.py` was last touched at
`2732304` and is named by no JSON (B-6); both `test_g2_*.py` guard files sit under `pet/` with
no pytest config redirecting collection (B-8). Also confirmed the iteration-policy note:
`epochs=8` (`train_fullevent_nominal.py:36`) against `EarlyStopping` patience 10
(`omnifold.py:58`, not overridden at `:129-130`) and `ReduceLROnPlateau(patience=1000)`
(`:247`) — both stopping mechanisms are structurally unreachable at the frozen configuration.

**Correction 1 — Gate-4's new check must be a RATIO, not an absolute yield.** The previous
entry's reco-level closure
`pot_scale*sum(w_truth*push over pass_reco) == n_data - pot_scale*sum(w_bkg)` is not
subsample-invariant: `push` exists only for the 2M subsample of 49,152,885 rows while the
measured yield is full-inventory, so as written it fails a *correct* unfold by a factor
≈ N/n_sub ≈ 24. Use
`sum(w_truth*push over pass_reco) / sum(w_truth over pass_reco) == R`, which is exactly `R`
by construction of `R` and needs no subsample factor. The truth-level-vs-reco-level objection
recorded above was right; the absolute form was an over-reaction to it and the mask change was
sufficient. Credited to `AUDIT-FINDINGS-20260729-B.md` §7.

Two additions to §7 found in review. It calls this a mask-and-target change with "no new
machinery" — but Gate-4's CLI (`validate_pet_nominal_gate4.py:210-231`) loads only the driver's
weights npz and forwards `weights_push`/`mc_indices`; neither `w_truth` nor `pass_reco` is in
scope anywhere in that file, so **neither** form is computable today. The validator must open
the G2 dump and recompute `R` itself (the driver persisting the sums would have the gate certify
the driver's own arithmetic). And the tolerance has three terms, not one: a **structural floor**
that does not vanish with more iterations, because `omnifold.py:185` pins off-acceptance `pull`
to 1 so step 2 smooths `pass_reco` pushes toward 1 across acceptance classes; a finite-`niter`
term; and a subsample sampling term (the ratio is invariant in expectation, not algebraically).
Term 1 caps the check's power and must be quantified before the tolerance is frozen.

**Correction 2 — B-4 changes `R`, so it must be settled before `R` is frozen.** `R`'s
denominator uses `w_truth` because that is what the reco leg is actually fed. If B-4 is fixed
so the reco leg uses `w_reco`, the physical denominator becomes
`pot_scale*sum(w_reco[pass_reco])` and `R` moves by
`sum(w_truth[pass_reco])/sum(w_reco[pass_reco])`. B-4 and B1 are therefore not independent
items in the consolidated patch set. `check_step1_class_ratio.py` now reports R under both
denominators, the shift factor, and the `w_reco`-vs-`w_truth` comparison that is B-4's own
minimal check, so one pass over the dump on 08-03 answers both questions. Tested on synthetic
fixtures in both branches (bit-identical → "B-4 INACTIVE"; perturbed → "B-4 is ACTIVE" with the
shift factor).

Two smaller notes. B-1's heading overstates: `omnifold_nn/omnifold/dataloader.py` **is** bound,
by the Gate-2 receipt, jointly with `unfold_2d_omnifold_unbinned.py`,
`fullevent_fps_dataloader.py` and `gate2_target_runtime.py` — the body is correctly scoped to
`net.py`/`omnifold.py`. The accurate framing is that the freeze covers the vendored engine's
plumbing but not its physics, and it is a second reason the §2a fix routes through the existing
`normalization_factor` argument: the one vendored file Gate-2 does freeze stays byte-identical.
And the design doc's open question was mis-framed — the Gate-2 receipt moves regardless because
it binds the loader; the live question is only whether the canonical **refiner re-run** can be
skipped on `w_refined` being bit-identical.

### 2026-07-29 — a claimed hole in verify_hash_bindings.py, refuted before it was recorded

A review of the B1 implementer brief claimed `verify_hash_bindings.py` cannot detect an edit to
`omnifold_nn/omnifold/dataloader.py` because the Gate-2 receipt binds it by absolute
`/pscratch` path, putting it in the 301-unresolvable set. This session accepted that and
generalized it further — to the whole Gate-2 quartet, including the two files the B1 patch set
edits — and was about to write it into the audit doc and here as a finding.

**It is false.** `verify_hash_bindings.py:74-78` (`localize`) strips the
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/` prefix before hashing, and the docstring at
`:17-21` records that the remapping was added because that exact binding was missed on a first
pass. Driving `collect()`/`localize()` over every receipt JSON: `dataloader.py`,
`fullevent_fps_dataloader.py`, `gate2_target_runtime.py`, `train_fullevent_nominal.py` and
`validate_pet_nominal_gate4.py` all resolve and all MATCH. Only `omnifold/net.py` and
`omnifold/omnifold.py` are bound by nothing — audit B-1 stands exactly as written and does not
extend.

**The trap, recorded because it will recur.** `verify_hash_bindings.py:115-123` prints only the
summary, the known-drift list, and mismatches — it never names a binding that is OK. So
`grep <filename>` over its stdout is empty both for an unbound file and for a perfectly intact
one, which are the two cases B-1 exists to distinguish. Settle coverage from the receipt JSONs,
never from the verifier's stdout. This session hit the same trap earlier in the same review,
caught it when a `grep` for the Gate-4 files came back empty, went to the receipt — and failed
to apply that correction backwards to a claim it had already accepted.

Operationally: the verifier *is* a valid backstop for every file §2a/§2c/§2d touch, and a
MISMATCH on each edited file is the expected, correct signal that the receipt needs re-issuing.
The implementer brief's constraint bullet telling the implementer to distrust it and hand-record
sha256s has been withdrawn.

### 2026-07-31 — Step 2b executed: Gate-4 re-issued, and the validator's dead checks are wired

`p3f-pet-gate4-launch-code-gate-20260731.json` (`PASS_CODE_ONLY`, no physics re-run) supersedes the
07-21 receipt, whose five hashes move to `files_at_issue` — preserved on the record, no longer live,
no hash hand-edited. Eleven files bound: the original five re-frozen (the launcher and launcher_test
byte-identical, re-frozen only because the receipt moved) plus six additive — B-1's `net.py` and
`omnifold.py`, both closure scripts, `closure_b1_rate_injection.py`, `test_b1_normalization_fix.py`.
Verifier `92 OK → 101 OK`; the three remaining mismatches are Gate-2's, including the
`run_gate2_target_validator.sh` shell pin, which is a separate remediation site.

**What the re-issue window was actually for.** Audit B2 (`AUDIT-FINDINGS-20260729-B.md` §B2,
`AUDIT-FINDINGS-20260728.md` §B2) — reproduced by three independent dimensions. The Gate-4 CLI
called `build_gate4_report` without `marginal=`, `normalization=`, `saturation_frac=` or `closure=`,
and the builder **skipped** any component whose argument was `None`; `frozen_observed` was built by
copying four `FROZEN` entries into the "observed" dict, so four of six freeze checks compared FROZEN
to FROZEN; and it never populated `central_vector` or `reported_bin_mask`, so three more never ran.
Result: `verdict PASS, 0 failed` on `|N(1,0.3)|` noise, with the receipt still embedding the
tolerances a reader would assume were met. Two structural rules now hold: **absent evidence fails**
(each component emits a named `<component>:evidence_supplied` check rather than being dropped), and
**everything compared against FROZEN is read from the artifact** or recomputed from the dump.
Consequences: the driver persists the run's real seed policy, grid, unit-normalized 285-cell central
vector, reported mask, cap-saturation fraction and input sha256; both closure scripts gained `--json`
reports that are now **required** validator arguments (which is also how the purity control and the
2026-07-26 synthetic-fixture run stop being admissible as closure evidence in code rather than in
prose); `z['target']` is read at last and `refinement_is_learned_production` gated, so a Delta
sklearn-refined result cannot be validated as the publication nominal; and `--n-full` stops being an
optional flag whose omission silently skipped `index:in_range`. The four mutations the §4 audit found
uncaught (driver `niter`, driver `train_events`, validator `epochs`, garbage grid) are all covered
now.

**Retired, deliberately.** `check_normalization` — the truth-level `sum(w*push)/sum(w) ~ 1`
primitive — and `normalization_dev_max` with it. It had no caller, its target is acceptance-dependent
(`1 + <a>(R-1) ≈ 1.08`, not 1), and it survived the 07-29 patch only as a binding-preserving shim for
the two frozen `validator_test` cases that pinned its signature. Step 2b reserved that decision for
this window.

**Also landed:** the `FINDING-20260730` fail-closed non-finite event-feature guard, naming the
offending column, screening only the *selected* columns (so it does not fire on today's `(pt, p‖)`
schema despite the dump's ~1,700 non-finite `q3` rows, and does fire the moment the block widens) —
plus a finiteness assert at the head of `assert_no_truth_leakage`, which is a *dissimilarity* test
and so used to pass on an all-NaN block. That file is Gate-2-bound; Step 2 owns its binding.

**What this re-issue does NOT have.** No independent second reviewer — the 07-21 issue claimed an agy
red-team PASS; this one has only its own adversarial test coverage. B-2's citation was checked and is
**unrecoverable**: the 07-21 build capture is absent and there are zero 07-21 files under either
`runs/` directory, so it is dropped rather than carried forward (Step 6 is the recovery path). Owed:
the measured `fold_forward_ratio_dev_max` (needs the real R), the `stress_closure_muon.py` **run**
(the script is bound and reports, but the vendored PET net cannot be constructed under this host's TF
2.16/Keras 3 — `net.py:148` uses the Keras-2 idiom; Perlmutter TF 2.15 and Delta TF 2.14 both
satisfy it), and the ordinary closure receipt (Step 3).

### 2026-07-29 — restore runbook gains Step 2b (Gate-4 re-issue); a Step 6 claim corrected

**Step 2b added.** The B1 fix voids bindings in **three** receipts, and the runbook owned only
one of them. Step 2 covers the Gate-2 canonical-runtime freeze (scheduled there for the
separate MeV/GeV units question — B1 now rides along on the same re-issue). But design §2d
edits the Gate-4 **driver** (`train_fullevent_nominal.py`, to persist the reco-masked sums) and
**validator** (`validate_pet_nominal_gate4.py`, the ratio check plus the plumbing that makes it
fire at all), both frozen by `p3f-pet-gate4-launch-code-gate-20260721.json` — which binds five
files: driver, launcher, validator, launcher_test, validator_test. Nothing scheduled that
re-issue. Gate-4 is `PASS_CODE_ONLY` and has never run at runtime, so it costs a receipt and no
physics re-run, but P5A must not launch under a voided launch-code gate, so Step 2b sits before
Step 4. Numbered 2b rather than renumbering, to keep existing references to Steps 3–6 valid.

Step 2b also records the full expected-red set — five bindings across three receipts
(`fullevent_fps_dataloader.py` is bound **twice**, by `g2-gate2-construction-20260719.json` as
well as the target-runtime receipt; that second binding had been missed in two prior reviews) —
so an implementer who watches the verifier go red knows that is the fix working rather than
reaching for the one prohibited action. And it folds in three audit findings at zero marginal
cost while the receipt is open: bind `omnifold/net.py` + `omnifold/omnifold.py` (B-1, currently
in no receipt at all); bind and finally run `stress_closure_muon.py` (B-6 — verified login-safe
directly: synthetic events, no ROOT/`/pscratch`/dump, `reco=cloud, gen=cloud` and all-ones
masks at `:70-71`, though it does import TensorFlow and train); and resolve B-2's dangling
independence citation, whose `agy-publication-redteam` uuid is the same session Step 6 rescues.

**Step 6 correction.** Its closing paragraph claimed the four Codex-profile verifier roles are
Perlmutter-only because `~/codex-homes/{personal,school}` is absent and `usagectl.py snapshot`
returns `gate_ok: false`. That generalized an `agentctl` *registry* problem into an *account*
problem. Verified: `~/.codex-personal`, `~/.codex-school` and `~/.claude-school` are all
present locally; only `~/codex-homes` — the path `profiles.json` points at — is missing, and
both Codex accounts plus the school Claude account ran from this Mac during the 2026-07-29
four-lane audit by direct `CODEX_HOME=` / `CLAUDE_CONFIG_DIR=` invocation. Fixing
`profiles.json` makes all four roles reachable without touching Perlmutter. The `agy` roles
remain a genuinely different problem: their conversation state exists only in Perlmutter's
`$HOME` and no local config change recovers it.

### 2026-07-29 — B1 normalization fix IMPLEMENTED (code-only); the Gate-4 tolerance is now bracketed, not invented

`B1-NORMALIZATION-FIX-DESIGN.md` §2a/§2c/§2d plus both §4 tests landed as one patch set. Nothing
was measured, no job ran, `R` is still unknown until 08-03. Suite: **9 failed / 376 passed / 1
skipped**, i.e. the documented 7-failure `/pscratch` baseline unchanged, +45 new tests, +2
expected hash-binding failures. `verify_hash_bindings.py` went from `ALL BINDINGS INTACT` to
four MISMATCH lines, `88 OK -> 84 OK`.

**§2a — the loader.** `R` is derived inside `build_fullevent_loaders` and the measured
`DataLoader` takes `normalization_factor = STEP1_MC_NORMALIZATION * R`; the MC block keeps 1e6,
passed explicitly so the two are visibly the same base. The formula lives in ONE body,
`fed.step1_class_ratio`, with the `w_truth`-vs-`w_reco` (B-4) assumption stated at the
definition, and `fed.step1_class_ratio_from_dump` records the `w_reco == w_truth` comparison at
runtime — so 08-03's first run answers B-4 as a side effect and a flip is a one-body change.
`check_step1_class_ratio.py` (unbound) was refactored to call the same body: it is the tool that
MEASURES `R`, so a private copy there would have been the first place that rule broke.

**§2c — Gate-2 retargets four sites, not two.** The design says `:411-412` and `:442-443` become
`1e6*R` and calls the `learned_vs_normalized_clipped_*` telemetry invariant. It is invariant only
if `:445` and `:448` are retargeted as well — `refined_hist` now sums to `1e6*R`, so leaving
`clipped_norm` at `1e6` would compare two differently-scaled histograms and inflate `rel_l1` by
exactly `R`. The invariance claim itself is correct and is now pinned by a test. The gate derives
`R` from its own read of the dump inside its existing `np.load` block, never from the loader's
`meta`, and additionally requires the R numerator to reproduce the independently-binned
`raw_signed_sum` — same number by a different route. A drift guard refuses to run if the gate's
`NORMALIZATION` and the loader's `STEP1_MC_NORMALIZATION` ever diverge.

**§2d — the check could not be replaced in place, and the plumbing was most of the work.**
`test_pet_nominal_gate4_validator.py` is bound by the Gate-4 receipt and pins
`check_normalization`'s two-argument signature and `ratio ≈ 1` semantics, so it was generalized
(`target_ratio=1.0` default; the frozen test still passes) into a primitive, and the gate now
wires a NEW `check_fold_forward_ratio`. Retiring the legacy entry point is queued for Step 2b,
which re-freezes that test anyway. The driver persists the reco-masked sums, the validator
recomputes them from the G2 dump via a now-**required** `--inputs`, and their agreement is
asserted — the driver is a cross-check, never the source. A pre-B1 weights npz now aborts rather
than producing a green receipt with the check skipped, which was the original failure one level
down.

**The tolerance is bracketed rather than invented.** §2d could not say what it should be. With
acceptance statistically independent of the truth features — the worst case, since step 2's
regressor then cannot separate the acceptance classes — the recursion has a closed form
`push_k = R - (1-a)^k (R-1)`, so the floor is `(1-a)^k (R-1)/R`. Confirmed empirically by the new
`closure_b1_rate_injection.py` (observed vs predicted 1.1734/1.1800, 1.2577/1.2520, 1.2773/1.2923
at R=1.30, a=0.60, k=1/2/4). At the nominal that bound is **1.71%** against a defect size of
**11.9%**; `fold_forward_ratio_dev_max = 0.05` sits between them and is marked
`PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` in the frozen contract and in every receipt it emits.
A parameter-free companion check — the result must land nearer `R` than `1` — carries the
broken-vs-corrected discrimination with no threshold at all.

**A trap for 08-03: `epochs` is not the unit of optimization, steps are.** At the nominal's
`epochs=8` a small closure run is optimization-limited, not floor-limited, and reads as though
the fix underperforms: deviation 2.6–6.7% at N=8,000, 1.8–3.4% at N=30,000, 1.4–1.6% at
N=120,000, converging onto the 1.71% closed form from above as the step count rises. The 2M-row
nominal sits far to the right of that table. Do not run the closure small and conclude anything.

**Two corrections to the implementer brief and Step 2b, both about the same thing.** Both state
the expected red as "five bindings", which is right at the receipt level but wrong about what you
will see: `verify_hash_bindings.py:105-107` dedupes on `(path, expected_hash)`, and both Gate-2
receipts bind `fullevent_fps_dataloader.py` to the *same* sha256, so the second is collapsed and
only **four** MISMATCH lines print. Both Gate-2 receipts still need re-issuing. Both documents now
say so; the five-binding table remains the re-issue list, the verifier's line count is not.

**One thing the new tests nearly did silently.** The new test file installs a stub `omnifold`
package into `sys.modules` to reach the numpy-only DataLoader without importing TensorFlow. Left
installed, it rescued six of `test_fullevent_gate2.py`'s expected `/pscratch` failures — the
baseline briefly read 3F/382P instead of 7F/376P — because that module short-circuits when
`omnifold.dataloader` is already loaded. That is order-dependent coupling that would have read as
"the end-to-end loader boundary is covered off-cluster" when the coverage was a side effect of
file ordering. The stub is now installed and torn down by a context manager, and the 7-failure
baseline is preserved exactly.

Status unchanged otherwise: Gate-4 `PASS_CODE_ONLY`, P5A unlaunched, no cross section extracted,
nothing pushed. What 08-03 inherits is a patch set that leaves both re-issues performable, a
closure that sizes the one number still marked provisional, and a Gate-4 that now fails the
defect instead of tolerating it.

### 2026-07-30 — b3751cc adversarially reviewed: six real defects, and my "structural floor" was wrong

Three referee lanes against `b3751cc`, each given one narrow target and told to default to REFUTED
(`codex-personal` on the R computation, `codex-personal` again on Gate-4 §2d, `claude-school` on
Gate-2 §2c). Every finding below was reproduced locally before being accepted. Two lane-mechanics
notes for next time: **`codex-school` is out of workspace credits** (returns
`ERROR: Your workspace is out of credits`, exit 0 — a silent-looking failure), and **`claude -p`
needs `< /dev/null` exactly as `codex exec` does**, or it waits on stdin and returns a warning
instead of a report.

**The miss that mattered: `validate_gate2_target_receipt.py`.** The *independent* Gate-2 receipt
validator carried the bare `1e6` at four sites and was not among the four files the B1 patch
touched. Left alone it would have hard-failed a correct post-B1 product at `:104` (13.5% miss on
`rtol=3e-6`) and inflated its own `l1_fraction` by exactly `R` — verbatim the bug the b3751cc
commit message claims to have avoided in the neighbouring file. That is design §5's "partial fix
aborts inside the restore window", one file to the left of where I looked. Retargeted; `R` is read
from the receipt and then *corroborated* against ingredients that file derives from the dump
itself (its own binned `signed_hist.sum()` as numerator, its own `w_truth[pass_reco]` read as
denominator), because importing `step1_class_ratio` would break the "does not import the
construction loader" charter in its own docstring.

**`max_relative` was not invariant, and my test for it was a tautology.** §2c's invariance claim
holds for `l1_fraction` and `cosine` but not `max_relative`: its zero-guard
`denom = np.maximum(clipped_norm, 1e-12)` is an ABSOLUTE constant while `occupied` deliberately
admits `clipped_norm == 0 & refined_hist > 0`, so there the denominator pins while the numerator
scales — `max_rel` scales by exactly `R`. The floor is now a fixed FRACTION
(`EPS_NORM_FRAC = 1e-18`, reproducing `1e-12` bit-for-bit at `R == 1`). Benign on today's grid
(`negative_signed_cells == 0`) but the pending MeV/GeV units fix is expected to create exactly
those cells, in the same window. My test had re-typed the `rel_l1` algebra on strictly-positive
random data and asserted only `rel_l1` — never reaching `denom`, never checking `max_relative` or
`cosine`. The tautology pattern audit §4 diagnoses, in a test written to prevent one.

**Three Gate-4 defects, each a variant of "the check does not bite".**
- **`R == 1` failed a correct unfold outright.** The parameter-free discriminator is
  `|ratio-R| < |ratio-1|`; at `R == 1` that is `x < x`, False for every input, including a correct
  no-change result with `push == 1`. §4 explicitly contemplates `R` near 1.0. Now skipped when
  `|R-1| <= tol`, where it decides nothing anyway.
- **The validator never checked it was handed the dump the result was trained on.** The driver
  records `inputs_path`; nothing compared it to `--inputs`, so a different dump could supply every
  reference sum — and the reference being independent of the driver is the entire point of §2d.
- **Skipping the check produced a green verdict.** `--allow-missing-fold-forward` returned
  `verdict: PASS` and exit 0 with only a buried `promotable: false` dissenting. B2 one level up.
  Now `FAIL_NORMALIZATION_NOT_CHECKED`, exit 1.

**A `sig_factor` bug in the B-4 telemetry.** With `sig_factor = 2` and `w_reco == w_truth`
bit-for-bit, `R_shift_factor_if_B4_fixed` reported 2.0 and `R_if_reco_leg_used_w_reco` the nominal
`R` rather than the replica's — the reco leg was left unscaled while the numerator and the
`w_truth` denominator both carried the replica draws. Telemetry only, the normalization `R` was
never affected, but **B-4 is decided off these numbers**, so a replica reading would have argued
for a shift that does not exist.

**And a claim of mine that was simply wrong: the "structural floor" is not a floor.** §2d asserts
term 1 "does NOT vanish with more iterations — it is a property of the estimator, not of finite
`niter`", and I propagated that into the code and the closure. My own closed form refutes it:
`(1-a)^k -> 0`. `omnifold.py:184-187` forms `weights_pull = weights_push * new_weights`, so
off-acceptance events RETAIN the previous push and catch up each iteration — only `new_weights` is
pinned to 1, not `pull`. My own measurements said so too: 9.23% / 3.69% / 0.59% at `k = 1/2/4`.
At the frozen `niter = 2` the value and the tolerance bracket are unchanged, but "irreducible" was
the wrong justification — it would argue for a permanently loose gate and would wrongly imply more
iterations cannot improve the rate closure.

**B-6 cannot run on this host, and that is a better explanation than "nobody ran it".**
`stress_closure_muon.py` exits non-zero before printing a verdict: `PET` will not construct under
Keras 3 (`net.py:148` passes a `KerasTensor` to `tf.cast`), and this Mac has TF 2.16.2 / Keras
3.15 while `sbatch_pet_fullevent_nominal.sh:106` pins `tensorflow/2.15.0`. Transcript recorded at
`docs/orchestration/runs/b6-stress-closure-muon/`. So `RESTORE-2026-08-03.md` Step 2b's
"login-safe by construction ... budget CPU minutes" is right about resources and wrong about
runnability off-cluster. **Delta is the answer and needs no dump**: the script is fully synthetic
(`grep -c "refine_stay_positive|build_fullevent_loaders|\.npz"` → 0), so HARD BAR #1 (which bars
the *nominal* on Delta because the canonical refiner imports ROOT) does not apply, and Delta's
container is Keras 2. My own B1 closure was unaffected because it uses `MLP`, not `PET` — the
choice was luck, and it is now a documented reason for it.

**B-8 wired in, and its proposed fix would not have worked.** The finding is CONFIRMED on
substance — 503 guard checks never ran. But "add a `pytest.ini` / `conftest.py` collection path"
collects those two files and finds **zero** tests: they are `main()` scripts with no `test_`
functions and no `unittest.TestCase`. Run as scripts both exit 0 here — 29 + 474 = the 503 lane D
reported, now executed rather than relayed — and neither imports ROOT or `/pscratch`, so B-8's
stated risk that they might make the baseline a moving target is also refuted. Wired via
`nd-unfolding/tests/test_g2_guards_collected.py`, which shells out and gates on exit code AND the
reported check counts (a guard script that silently stopped checking would still exit 0).
A wrapper rather than an edit because `test_g2_domain_validator.py` is named by a receipt.

Suite **9 failed / 391 passed / 1 skipped** — the documented 7-failure `/pscratch` baseline
unchanged, +54 B1 tests, +6 guard-wrapper tests, +2 expected hash-binding failures. Verifier still
red on exactly the same four MISMATCH lines; `validate_gate2_target_receipt.py` is bound by nothing,
so retargeting it adds no receipt debt.

### 2026-07-30 — B-6 RETIRED: the omitted-muon stress closure PASSES on Delta, first recorded PASS anywhere

Run on NCSA Delta, `gpua092`, container `tf215.sif` (which contains **TF 2.14.0 / Keras 2.14.0** —
the filename is misleading and `AUDIT-FINDINGS-20260728.md:547` was right). Script sha256
`3c3e092f…4865a0`, **byte-identical to the local checkout**, Delta HEAD `68f1291`. Transcript:
`docs/orchestration/runs/b6-stress-closure-muon/20260730-stress_closure_muon.delta.capture.txt`.
Cost seconds of the 796 remaining GPU-hr.

```
[stress] injected per-stratum muon tilt alpha=1.20; recoil marginal held fixed
[stress] PRIOR       vs data L1/stratum: median=0.5820 max=0.7915
[stress] RECOIL-ONLY vs data L1/stratum: median=0.5811 max=0.7779
[stress] FULL-EVENT  vs data L1/stratum: median=0.0428 max=0.3496
STRESS CLOSURE PASS: full-event recovers the omitted muon variable; recoil-only cannot.
```

**B-6 is retired.** The finding was that this closure is named in Gate-4's own frozen contract
(`validate_pet_nominal_gate4.py:57-59`), was edited after the Gate-4 PASS, is bound by no receipt,
and had never recorded a PASS anywhere. It now has one, against code whose hash is recorded above.
Binding it is still Step 2b's job.

**Two launch gotchas, both worth having in the runbook.** Direct `python3` under `srun` **aborts**:
`omnifold/__init__.py` finds horovod in the Delta container and calls `hvd.init()`, and OMPI was
not built with SLURM PMI, so it dies with `OPAL ERROR: Unreachable in pmix3x_client.c` before
reaching any physics. `PET_TRAINING_ON_DELTA.md` already documents the shape of the fix for the
4-rank launcher; for a single-rank job it is `horovodrun -np 1 python3 …` inside `apptainer exec`.
Note this is why Step 5a's "no MPI" validation works while this did not — that path imports the
dataloader module directly and never executes the package `__init__`.

**What this does and does NOT say about B-3.** It says the event-feature channel is *decisive and
functional*: recoil-only recovers essentially nothing (median 0.5811 against a prior of 0.5820,
i.e. ~0.15% of the injected tilt) while the full-event estimator closes it to 0.0428 — a **13.6×**
residual reduction, using only the two muon scalars `(pt, pparallel)` the loader actually reads. So
the reduced representation is **not blind to the muon**, and the B-3 framing "the estimator
overstates what it saw" should not be read as "the estimator is crippled" — it is working, the
*label* is over-specific.

It does **not** measure whether the eight unread arrays add anything, and cannot: the injected tilt
is a function of the muon feature the loader already consumes, so by construction this closure
cannot separate "PET uses muon information" from "PET needs the full muon object". The evidence
that would settle B-3 is a *variant* of this closure injecting a tilt in an **unread** variable
(view/timing are the cheap candidates — per-token, present on all three reco-level legs, and
needing no truth counterpart because `m1`/`m2` take independent cloud dims). That is a small
extension of an existing script, needs no dump, and runs on Delta. Until it exists, extending the
feature block is a change with no measured benefit, and correcting
`FULL_EVENT_FEATURE_CONTRACT.md:19-21` remains the only claim that is actively false today.

### 2026-07-31 — Gate-2 final-writer pins re-armed; the shell pins are now walked

`run_gate2_target_validator.sh` froze its validator and loader by sha256 at 3d4cbdb. Both files
were rewritten afterwards — b3751cc (B1: `1e6*R` on the measured loader), f6a9e8e (six defects
from the adversarial review), and, validator only, 3b93409 (B-4 gated instead of recorded) — and
the pins were not re-issued in any of those commits. Lines 38-39 abort before any physics runs, so
**this route has never executed post-B1**: the 08-03 re-issue could not have run the `1e6*R` logic
through its own production path. The run log has no record of the route executing at all.

Pins moved `a8539d83…→f9e20f4c…` (validator) and `c0521d21…→538031732…` (loader). `EXPECTED_U2D_SHA`
and `EXPECTED_INPUT_SHA` still match and are untouched.

**What this restores and what it does not.** The constant is a precondition — "refuse to run if the
code changed" — and moving it re-arms that guard against current code. It does **not** restore the
frozen-at-hedge-submission property the `die` message claims ("validator changed after hedge
submission"); b3751cc ended that, and no edit here brings it back. The honest reading of these two
pins is now "unchanged since 3b93409", not "unchanged since the hedge".

**Editing the hash is not the general repair.** An earlier attempt in this session moved these two
pins inline, justified by a comment arguing that because the cluster copy is a `git pull` of this
repo, pin and pinned file always travel together and a stale pin is therefore unreachable code
rather than a guard. That reasoning is circular — the guard fires exactly when file and pin
diverge, and updating the pin to match is what converts it into a no-op, which was then cited as
evidence it had never been a guard. It was reverted. `verify_hash_bindings.py` has said the rule
since 2026-07-28: *do not just update the hash*. What makes this instance legitimate is that the
move is recorded, attributed to the commits that caused it, and scoped to a precondition rather
than to evidence.

**The four receipt bindings are NOT repaired and must not be.** `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`
(`PASS`), `g2-gate2-construction-20260719.json` (`CONSTRUCTION_PASS_RUNTIME_PENDING`), and both
Gate-4 launch-code bindings assert that a gate *passed against specific code*. Rewriting those
hashes would assert a PASS that never happened against the current files. They stay red pending an
actual re-run — Gate-4's rides Step 2b. They were deliberately **not** added to the verifier's
`KNOWN_PREEXISTING` list, which would silence them permanently; that call is still open, and is
only correct if those receipts are closed history rather than about to become informative again.

**The repair cascades, and the guard caught it.** `run_gate2_target_validator.sh` is itself pinned
by its two callers — `sbatch_gate2_target_validator.sh:18` (batch) and
`docs/orchestration/run_gate2_r4_detached.sh:11` (detached), both holding `EXPECTED_RUNNER_SHA`.
Editing the two constants inside the runner changed the runner's own hash and broke both, which
the extended verifier reported on the next run. Those were green immediately before this change,
so the break was caused by the repair, not inherited. Both moved `3e439626…→a8ba8934…`. The
cascade terminates there: nothing sha-pins either caller (`gate2-queue-hedge-armed-20260719.json`
names `sbatch_gate2_target_validator.sh` in `submission_command` only, and records no hash for
it). This is worth knowing before the next pin move — a re-pin is not a local edit, and without a
walker the second-order break is invisible.

Finding it also exposed a defect in the new guard: shell pins were deduped by *kind*, so two
launchers pinning the same runner to the same hash collapsed into one report and half the
remediation was hidden. Dedup is now per shell site; receipts still dedupe, where repeats are
noise rather than separate edits.

**Coverage.** fa06bb6 extended `verify_hash_bindings.py` to walk `EXPECTED_*_SHA` guards in `*.sh`,
which is the class of pin nothing had ever checked — 10 of 15 resolve to files in the checkout
(the rest are `/pscratch` data and built binaries). Its `SHELL_PIN_FLOOR` fails loudly if the
parser ever stops matching, since a source-parsing collector that silently finds nothing would
print ALL BINDINGS INTACT.

## 2026-08-04 — RESTORE Step 5 Delta-product durability verified

Both recoil-only `xps2` shutdown-insurance products are present in the declared CFS staging
directory. Their destination SHA-256 values and exact byte counts were recomputed rather than
copied from the truncated historical records. The full evidence is recorded in
`docs/orchestration/state/restore-step5-delta-durability-20260804.json` and the corresponding
`MIG-RESTORE-STEP5-DURABILITY-20260804` `RUNS.tsv` row.

This closes durability only. No copy or training was performed in the verification, and neither
artifact is a Gate-4/P5A or publication result.

## 2026-08-04 — B-4, Step 3 architecture, and construction-receipt lifecycle decided

The user delegated the three open RESTORE judgments and requested a durable repository record.
They are now one transaction in
`docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md`:

- Step 1 uses `w_reco`; Step 2 and truth-space yields use `w_truth`. The PET engine must carry
  distinct leg weights rather than replacing its one shared `mc.weight` wholesale. B1's `R`
  denominator follows the Step-1 `w_reco` ensemble.
- The nominal consumes and verifies the precomputed Gate-2 target. The ordinary identity closure
  gets an MC-only TF path and is labeled a plumbing smoke, while a nontrivial injected-reweight
  recovery closure supplies publication power. No combined ROOT/TF publication environment and no
  ROOT-to-TF closure handoff.
- The hand-authored 2026-07-19 construction attestation is superseded without changing or deleting
  any at-issue hash. Its entire binding block is historical; the runtime receipt owns the live
  Gate-2 freeze. No load-bearing path was added to the path-wide `KNOWN_PREEXISTING` exemption.

The environment finding was corrected at the same time: despite its launcher comment, the current
nominal does not consume `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy`; it reaches the same in-process
refinement as closure (audit J04). This entry records decisions and receipt lifecycle only. No
loader, engine, target, closure result, Gate-2/Gate-4 receipt, or training artifact was produced.
`nominal_pet_training_allowed` remains false.

## 2026-08-05 — D1/D2 implemented, Gate-2 re-issued twice, and the pin cascade walked to its end

**Gate-2 PASSED under D1/D2.** Numbers in `../VALIDATION_LEDGER.md`. Two runs: 56342333 (r1) and
56344268 (r2), both PASS, both producing the identical target digest `544b2f6a...`. r1 was superseded
within the hour because the audit repairs in 2cef7e6 moved `fullevent_fps_dataloader.py` after r1 had
hashed it, so r1's receipt pinned code that no longer existed. The loader diff was confined to the
`mc-only` branch and to comments — and the identical digests prove it was inert here — but "the change
was semantically inert" is exactly the reasoning hash pins exist to reject, so the gate was re-run.

**What D1 changed.** Step 1 consumes `w_reco`, step 2 and every truth-space quantity `w_truth`. The
vendored engine used one `mc.weight` for both legs, so a wholesale swap would have moved the defect
rather than fixed it. `normalize=True` derives ONE constant from `sum(w_reco[pass_reco])` and applies
it to both legs, which holds the per-event ratio at its measured [0.931, 0.998] — a reco-only MINOS
efficiency factor — instead of scaling it by 1.0189. Step 2 is scale-invariant, so this costs it
nothing.

**The B-4 gate was INVERTED, not deleted.** It used to block when the legs differed. Post-D1 that
would reject the correct configuration and accept the broken one, since the reco leg carries a
reco-only calibration and therefore differs on every selected row. It now blocks unless the reco leg
is fed `w_reco`.

**What D2 changed.** `bkg_mode='mc-only'` builds the MC side alone and cannot reach the refiner, so it
cannot import ROOT — the conflict that blocked RESTORE Step 3. The nominal now CONSUMES the published
target with provenance checks instead of silently rebuilding it (audit J04), and row ORDER is bound by
comparing recomputed inventory identity hashes, which no file digest can express.

**Bugs found and fixed along the way, recorded because each was invisible to the tests that existed.**

* The truth-space reporting spectrum was being built from the RECO leg: a variable named `w_mc` was
  pointed at the reco leg for a step-1 ratio and then reused for `reporting_spectra`, whose parameter
  is literally named `w_truth`. Both arrays are the right shape and the spectrum is unit-normalized,
  so the artifact looked healthy and was the wrong spectrum. Variables are now named by leg.
* Gate-4's independent fold-forward still read `w_truth` for a step-1-space quantity, which would have
  failed the strict independence check for a reason that was not a defect in either side.
* The ordinary closure's pseudo-data was built from the truth leg, so the identity closure would have
  been handed two densities differing by the efficiency factor and failed for unrelated reasons.
* The powered closure passed float64 weights into an engine whose logits are float32, dying inside a
  tf.function with a traceback naming only Keras internals. Caught by a 20-minute GPU smoke rather
  than by an 8-GPU-hour queued run.

**THE PIN CASCADE, which bit four times in one day and is the transferable lesson.** Any byte-level
edit to a hash-pinned file is a gate re-issue, whether or not it changes behaviour, and a file can be
both pinner and pinnee:

1. advancing `EXPECTED_LOADER_SHA` inside `run_gate2_target_validator.sh` changed that FILE's hash,
   breaking both callers that pin the runner;
2. fixing those callers, then editing the runner again, broke them a second time;
3. writing a one-line docstring note into the pinned loader would have invalidated the receipt being
   produced at that moment — caught and reverted before commit, the note moved to an unpinned file;
4. archiving the superseded receipts INTO the repo made the verifier red again immediately, because it
   walks every receipt it finds and an archived one keeps pinning the code current when it was written.

(4) needed the D3 at-issue convention applied to runtime receipts, and then to three 2026-07-19
orchestration records that pin the products AND each other — retiring a pin inside one changes that
file's hash and breaks its siblings' pins on it, so the chain had to be retired to a fixpoint
together rather than one file per round. The verifier's dedup key `(rel, want, src if .sh else "")`
masks siblings pinning the same (file, hash), which is why each fix appeared to reveal a new problem.

**End state.** Every LIVE Gate-2 pin is satisfied. The verifier reports exactly 8 mismatches, all
from `p3f-pet-gate4-launch-code-gate-20260801b.json`, all on files D1/D2 legitimately changed, and all
of which resolve when Step 2b re-issues that gate. No digest was hand-edited anywhere.

## 2026-08-06 — item (e) reassessed as already half-answered, k=4 arm launched, (d)+J28 planned jointly

Three things, one commit.

**(e) was overstated when it was opened.** The item said the `niter=3` justification is gate-shaped
and needs a regularization-shaped one. Re-reading `state/p3f-pet-gate4-launch-code-gate-20260806.json`
`seed_policy_change.measurement`: both halves of a bias-variance argument were already receipted and
had simply never been put in one sentence. At the measured operating point (R=1.1240802949941018,
a=0.4185618199216587, N=240k, epochs 8, seeds 7-54 both arms) the bias falls 0.038008 -> 0.021876 --
tracking the `B1-NORMALIZATION-FIX-DESIGN.md:329` closed form `(1-a)^k (R-1)/R` (0.037318 / 0.021698)
to under 0.1 pp -- while the 48-seed spread is flat (0.008153 -> 0.008444, ratio 1.036). Bias down at
fixed variance IS the regularization statement; the 6/48 -> 0/48 exceedance is its consequence, not a
separate argument. Recorded as **CLM-010**, scoped `VERIFIED-NUMERIC (scalar scope only)` because it
is the reco-level rate closure, not the differential cross section. The assembly is single-source
(this session) and is flagged as needing an independent check.

Also recorded, because it is the part that would otherwise be quietly assumed: the criterion is
reco-space and **data-computable**, so it does not fall to the note's own objection to Huang et al.'s
truth-level chi-square (`sec_method.tex:89-98`), and the scan is an MC closure with an injected
defect, so it is not the tuning-on-result loop `sec_method.tex:155-167` disclaims.

**Two gaps remain and they are narrower than the item implied.** (i) Scalar, not differential -- the
per-bin half comes FREE from job 56381674, because `closure_powered_truth_reweight.py:302-303` already
persists `h_prior`/`h_target`/`h_unfolded`/`h_untilted` as full per-bin arrays. No code change, no
Gate-4 re-issue, and specifically **do not** edit that driver mid-flight: `sbatch_powered_closure.sh`
pins its digest in `EXPECTED_DRIVER_SHA` and fails closed. (ii) Nothing bounds `k` above --
`(1-a)^k -> 0` predicts 0.012617 at k=4, so the receipted pair argues `k >= 3`, not `k = 3`.

**Job 56397442** (`nd-unfolding/pet/sbatch_b1_niter4_scan48.sh`, new, shared/gpu, 2 h wall) measures
the k=4 point: 48 seeds 7-54, every parameter read back out of the k=3 arm's own receipt entry rather
than from the script's defaults, which are the STALE recoil-only operating point (1.135 / 0.621 /
niter 2) -- the same hardcoded-superseded-constant trap the 08-06 FINDING is about. Predeclared, before
the data exists: **if the k=4 spread is also flat, the record must say the stopping point is set by
cost and by the literature default of 3 (`LITERATURE_NOTES.md:65`), NOT chosen by this measurement.**

**Verified in the same turn, not from memory:** job 56381674 is the a1 powered-closure re-run and is
running at `niter=3` -- the driver reads `NOMINAL_SEED_POLICY` (`closure_powered_truth_reweight.py:265`)
which `2b2e5f1` set to 3 at `train_fullevent_nominal.py:51`, and the job started after that commit.
Preflight PASS (gap 0.2343, floor/gap 0.0459). Its launcher's protocol comment still asserted
"niter 2"; behaviour was always correct (it overrides nothing) but the comment was false from
`2b2e5f1` onward. Fixed, with a note to read `configuration.niter` out of the report instead. That
file is not among the 22 live hash pins, so the edit is safe on its own.

**(d) + J28 planned as one pass**, at `docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`.
The material finding: **J28 is no longer blocked on the Perlmutter restore.** `VALIDATION_LEDGER.md`
still cited the 08-03 restore as the blocker; the restore completed and the inputs are all present --
365 `*slab*.npz` under `nd-unfolding/` (205 `uq_5d/`, 33 `uq_4d/`), the three `bank_uthrow_*` banks
with `cv.npz` + `flux_univ_ratio.npy`, and `rescale_flux_universes.py` from `081ae4a`. The re-roll is
schedulable now. Scratch is purgeable, so protecting those 365 slabs is Step 0 and the plan says so.
Ledger quarantine updated to point at the plan rather than at a blocker that has cleared.

## 2026-08-06 — D2 powered closure re-run at niter=3 COMPLETED AND FAILED (job 56381674)

**Result.** rc=3, `verdict=FAIL`, elapsed 01:58:19, `configuration.niter = 3` (confirmed in the
report, not inferred). Training-independent criteria passed as predicted: `gap = 0.234270` (>= 0.15),
`floor/gap = 0.045876` (<= 0.10), preflight cross-check AGREE. **The open number missed by more than
2x: `residual = 0.106159` vs budget `<= 0.0469`; `residual/gap = 0.4531` vs `<= 0.20`; recovery
`0.5469` vs predeclared `>= 0.80`.** Evidence in `pet/powered_closure/`:
`POWERED_CLOSURE_REPORT.slurm-56381674.json` (sha256 `d5a01f3f4ffd…`), `POWERED_PREFLIGHT.…json`,
`POWERED_CLOSURE_ARTIFACT.…npz`, `DONE.slurm-56381674.txt`. **Thresholds NOT touched** — the handoff
says diagnose on FAIL, and that instruction is correct.

**Diagnosis from the report's own per-bin arrays** (285 cells = 15 pT x 19 pparallel, pt-major). This
is the payoff of the arrays being persisted at `closure_powered_truth_reweight.py:302-303`: the
diagnosis cost zero additional compute.

- **Not a normalization failure.** `sum(h_prior) = sum(h_target) = sum(h_unfolded) = 1.0` exactly and
  `sum(h_unfolded - h_target) = 0.000000`. The B1 rate closure passing at k=3 and this failing are
  therefore *not* in contradiction — they measure different quantities.
- **Globally short, not locally broken.** `L1(unfolded-prior)/L1(target-prior) = 0.6549`; per-bin
  median recovery 0.8233; 128 of 262 bins below 0.8; **29 bins move the wrong way**.
- **Broadly distributed.** Top-10 cells carry 26.5% of the L1 residual, top-20 44.8%, top-50 75.1%.
  There is no small set of pathological cells to excise.
- **Edge-clustered worst cases** at `i_pparallel = 0` across pT 2–5 (cells 38/57/76/95, recovery
  0.17–0.24), plus a run at cells 191–194.

Direction right, magnitude short, normalization exact, spread across the grid = **over-regularization**,
not a defect. Two live hypotheses, deliberately not adjudicated here: (i) `niter=3` is too few for
SHAPE recovery even though it suffices for RATE closure; (ii) `epochs=8` leaves the fit
optimization-limited (`B1-NORMALIZATION-FIX-DESIGN.md:352-357` — epochs is not the unit of
optimization, steps are; the 2M half-size should sit right of that regime, but "should" is not
"measured"). **No niter=2 arm exists** — 56355818 was cancelled at 5:18 — so nothing here can be
attributed to the niter switch in either direction.

**Consequence for item (e), recorded the same turn.** Earlier today this session assembled the
receipted k=2/k=3 numbers into a bias-variance argument (CLM-010) and scoped it explicitly to the
reco-level RATE scalar, flagging that the differential version was still owed. That caveat was
load-bearing: the differential test has now run and failed. CLM-010's scalar claim stands as written;
it must not be read as evidence that k=3 suffices for the cross section. If hypothesis (i) holds, the
regularization argument points to k>3 — the opposite of a stopping point — which promotes the k=4 arm
(56397442) from formality to load-bearing.

**Gate-4 remains red and `nominal_pet_training_allowed: false` still holds.** Step 4 stays blocked.

Also this turn: BEN-026 amended after this session repeated it a third time (`pytest … | tail -15`
and `verify_hash_bindings.py | tail -12`), having read the rule in the same session — it composes with
BEN-028 into a *total* evidence loss, not a partial one, because SIGTERM arrives before any flush.
`test_hash_bindings.py` 4 passed (1:55:25); bindings intact across this commit's edits.

### 2026-08-06, same day — three corrections to the entry above, from the concurrent session

A second session was analysing 56381674 in parallel (`AUTONOMOUS_LOG_20260805.md` 14:20Z, commit
`291229e`) and got further on three points. Recorded rather than silently merged, because two of them
change conclusions this session had already written down.

1. **"Nothing is attributable to the niter switch" was too weak — the niter=2 run was unpassable BY
   CONSTRUCTION.** Acceptance from the report's own `samples` block is `837494/1999920 = 0.418764`;
   `RunStep2` pins the remaining 58.1% of truth rows to 1, so recovery has a structural ceiling
   `1-(1-a)^k`. Reproduced independently here: k=1 0.41876, **k=2 0.66216**, k=3 0.80364, k=4 0.88587.
   A 0.80 bar was **unreachable at k=2**, so `56355818` would have burned 12 h to prove it, and the
   2->3 switch was necessary for the criterion to be satisfiable at all — not merely preferable.
   *Their caveat, which stands:* this is B1's **RATE** bound applied by analogy to a **spectral L1**.
   Unproven transfer. Do not quote it as established.
2. **The bar was never checked against the ceiling.** k=3 ceiling 0.80364 vs `recovery_min = 0.80`
   leaves 0.36 pp. Same species as the inert-tolerance defect B1 fixed. Not a proposal to lower it.
3. **The tilt-direction asymmetry is the explanation; this session's "pparallel edge" reading was an
   artifact.** The tilt is a function of truth pT, so all 19 pparallel cells at one pT share it — the
   worst cells sit at pparallel 0 only because displacement is largest there. Real structure:
   down-tilted cells (pT 2–5, ~0.55x) recover 0.17–0.24, up-tilted (pT 12, ~2.65x) recover 0.72–0.91.
   The estimator resists moving DOWN.

Also from them, adopted here: `residual/gap` and `recovery` are one criterion stated twice
(`recovery == 1 - residual/gap` exactly, verified), so the FAIL is one missed criterion, not two; and
the reweight-logit-cap hypothesis is **refuted** (cap 30.0 spans 1e-13..1e13, injection needs
0.55..2.65, engine logged zero saturation lines).

Both sessions independently reached the same leading hypothesis — under-fitting, pointing at
`epochs=8` and the effective-iteration count — from different evidence. That is convergence, not
confirmation: neither has tested it.

### 2026-08-06 — k=4 arm: 56397442 lost to a walltime kill, resubmitted as the original 16+32 split

`56397442` (48 seeds, k=4, 2 h wall) will not finish and will write nothing. Measured from its own
log — 37 seeds started at 1:47:26 elapsed, i.e. **~2.9 min/seed** — 48 seeds needs ~2 h 20 m. The
driver writes its single `--json` only after the last seed returns, and the launcher writes to
`.partial` and renames on success, so a walltime kill correctly leaves no corrupt file and also **no
file**. ~1 h 50 m of GPU for zero product. Left to expire rather than cancelled: it produces nothing
either way, and letting it run out carries no risk of my arithmetic being wrong.

**Root cause was mine and it is now BEN-030.** The k=2/k=3 arms were each two jobs (seeds 7–22,
23–54). I consolidated k=4 into one job because a single file read as tidier, which silently removed
the only checkpointing this scan has, and I sized the wall from a stale "~7 minutes" note describing a
differently-shaped run instead of measuring the rate.

**Resubmitted** as `56400517` (seeds 7–22, 16) and `56400519` (seeds 23–54, 32), both 4 h wall, via
`B1_SEED_START` / `B1_SCAN_SEEDS` overrides on the same launcher. Output names now mirror the k=3 arm
exactly (`..._scan16_measured_N240k_niter4.json`,
`..._scan32_measured_N240k_niter4_seeds23plus.json`) so the four-arm set is file-for-file comparable.
The launcher carries the reason for the split inline so the next reader does not re-tidy it.

Predeclaration from this morning is unchanged and still binding: **if the k=4 spread is also flat, the
record must say the stopping point is set by cost and by the literature default of 3, not chosen by
this measurement.** Note the k=4 arm now matters more than when it was queued — the D2 failure raises
the possibility that k=3 is too few for SHAPE, in which case the k-question is open upward.

Verification this turn: standalone `verify_hash_bindings.py` (rerun unbuffered to a file, per the
amended BEN-026) reports **858 OK / ALL BINDINGS INTACT**, 4 known pre-existing submit-time drift,
matching `test_hash_bindings.py` 4 passed.

## 2026-08-06 — J28 flux re-roll: the exact corrected 5D covariance (Flux block was understated ~4.2×)

Job `56417324`, one Perlmutter CPU node via `srun -q interactive`, ~2 minutes wall. Step 1 of
`../docs/orchestration/PLAN-20260806-niter3-budget-and-J28-reroll.md`, run against its predeclared
rules. Inputs are the ensemble the **adopted** `uq_5d/unified_throw_cov_5d.root` was built from,
identified from two agreeing sources (`sbatch_uthrow_combine_5d_fast.sh:16-19` and the run-F entry at
`CORRECTED_UQ_PRODUCTION_STATUS.md:266-268`): 31 throw slabs = **122 throws**, 36 block units with
**100 flux units corrected**, `bank_uthrow_5d` (100 flux universes, max |r_u − 1| = 0.1371), CV
`products/5d/xsec_5d_MEFHC_5iter_lgbm.root`, 10,694 reported bins.

No re-unfolding: the correction `x/r_u` along `pT` is an identity, which is the whole reason this was
minutes rather than a re-throw campaign. Knob endpoints correctly untouched — every
`block5d_knob_*.npz` reports `0/2 corrected`, which is the tool working as designed, not failing.

    sqrt_tr_flux_block     3.892270e-39 -> 1.622406e-38   +316.83%
    sqrt_tr_blocksum       3.403264e-38 -> 3.750055e-38    +10.19%
    sqrt_tr_unified        4.343878e-38 -> 4.312442e-38     -0.72%
    sqrt_tr_cross          2.699457e-38 -> 2.129377e-38    -21.12%
    joint_mean_shift_norm  1.535143e-38 -> 1.885299e-38    +22.81%
    g_mean  mean-centered  1.0565550    -> 1.0295687        -2.55%
    g_mean  CV-centered    1.1117482    -> 1.1186232        +0.62%
    g_max                  22.302611    -> 17.202930       -22.87%

Physics: dividing every universe by `Φ_CV` instead of its own `Φu` **removes the normalization spread
the flux universes exist to carry**, so the defect *understated* the Flux block rather than inflating
it. Correcting it raises the block sum toward a nearly unchanged unified total, which is why the
finite-throw cross term collapses 21% and `g` falls toward 1.

**Two things the predeclared rules force into the record.** (1) The first-order estimate (+3–4% upward,
~+6% on the combined block) is **superseded and was not confirmed** — exact is +10.19% on the block sum
and *down* 0.72% on the unified total; rule 1 says the exact number replaces it. (2) The `g` direction
is **convention-dependent**: `mean_shift` grew 22.81% and CV-centering adds `shift²`, so mean-centered
`g_mean` falls 2.55% while CV-centered `g_mean` rises 0.62%. No adoption may quote a direction for `g`
until the F7 convention is settled. Both conventions agree `g_max` falls ~23%, a single-bin extremum
over 10,694 bins with no interval attached (rule 3); `n_throws = 122` is the real `n`.

**Adopts nothing** — the tool writes its own output and the ledger quarantine stays in force. These are
the **5-iteration GBDT 5D** slabs, not the PET lane whose policy moved 2 → 3, so this does not
discharge `OPEN_ITEMS.md` item (d). Receipt `uq_5d/rescaled_20260806/j28_reroll_20260806.json`;
write-up `../docs/orchestration/FINDING-20260806-j28-reroll-exact.md`.

## 2026-08-06 (same day, later) — CORRECTION to the entry above: the re-roll used 122 of 160 throws

The entry above says the re-roll's inputs were "the ensemble the **adopted**
`uq_5d/unified_throw_cov_5d.root` was built from." **That is wrong**, and this file is append-only, so
the correction is recorded here rather than by editing it.

Read from the adopted ROOT directly (`TFile.Open` → `Get`): **`n_throws = 160`**,
`sqrt_tr_unified = 4.4607819710748654e-38`, `joint_mean_shift_norm = 1.654393237996853e-38`. Job
`56417324` processed **122** throws. `uq_5d/uthrow_slabs_5d_sb/` holds slabs **0–30**; slabs **31–39
are gone** — run F was `[0-39%40]` at 4 throws/task, so 30×4 + one 2-throw slab = 122, and the missing
9 slabs are the remaining ~38 throws. They were lost from purgeable scratch *after* the combine ran.

Consequences:

- the re-roll's "before" sits **−2.62%** below the adopted `sqrt_tr_unified` and −7.21% below its mean
  shift, so the corrected **absolute** numbers are a **76.2% subsample** and are **not** drop-in
  replacements for the adopted covariance;
- the before → after **relative** changes stand unchanged (+316.83% flux block, +10.19% block sum,
  −0.72% unified), because both sides are computed from the same 122 slabs — that comparison was always
  controlled;
- **exact replacement of the adopted covariance requires re-throwing slabs 31–39.** Tracked as
  `OPEN_ITEMS.md` item (g).

Generalisable trap filed as **BEN-033**: read an ensemble's size from the **product**, never from the
launcher's globs — a launcher states what it *would* consume, the product records what it *did*, and the
two diverge exactly when inputs have been lost since. Two independent sources agreed on the input set and
both were the wrong *kind* of source, so agreement bought nothing.

**Also settled, and it was never actually open: the F7 mean-shift convention.**
`CORRECTED_UQ_PRODUCTION_STATUS.md:73-78` predeclared the test — `~floor` → mean-centered acceptable,
`>> floor` → also produce the CV-centered variant, report the shift either way, never silently drop it.
On the adopted ensemble `||mean_shift||` is **4.69×** the sampling floor `sqrt_tr/√160` (37.1% of
`sqrt_tr` against a 7.9% floor), rising to **4.83×** after the flux correction. `:325` had already
flagged that same 37% as NON-negligible on 07-13. So **mean-centered-only is disqualified** and the
operative `g` change is the CV-centered **+0.62%**, not the mean-centered −2.55% — the corrected
inflation edges slightly *up*. Only presentation remains a choice.

### 2026-08-06 — k=4 products committed; k=5 arm submitted as a completeness arm (56427556/56427557)

**k=4 landed and PASSED, both halves.** `56400517` (seeds 7–22, 01:34:24) and `56400519` (seeds 23–54,
03:16:09), pooled 48 seeds: closed form 0.012616, mean 0.014256, **sd 0.008023**, max 0.034619,
**0/48** over tol 0.05. Products committed here — they had been sitting untracked, which by this
repo's own rule means they did not exist.

Full k-series, 48 seeds per arm, identical operating point:

    k   closed form      mean         sd        max   exceed .05
    2      0.037318   0.038008   0.008153   0.053764        6/48
    3      0.021698   0.021876   0.008444   0.042750        0/48
    4      0.012616   0.014256   0.008023   0.034619        0/48
                       sd ratios: k2->k3 1.036, k3->k4 0.950

**The predeclaration fired exactly as written.** Bias falls monotonically and tracks the closed form;
variance is flat across all three arms. So the B1 measurement does **not** choose the stopping point,
and the record must not imply it did.

**The niter decision itself is already settled elsewhere — do not re-derive it here.**
[`FINDING-20260806-niter4-decision.md`](../docs/orchestration/FINDING-20260806-niter4-decision.md)
is the canonical record: `k=3` stands on cost and convention, the 0.80 closure bar is unreachable at
any `k <= 39`, and it discharges CLM-010 (ii). This entry adds only the arm and its sizing.

**k=5 submitted for bookkeeping**, at Joseph's request: `56427556` (seeds 7–22, 4 h) and `56427557`
(seeds 23–54, 8 h). **Predeclared before the data exists, so this cannot be read either way after the
fact:**
- k=5 is a *completeness* arm. It does **not** reopen the niter decision, which rests on cost and
  convention, not on this scan.
- The one genuinely new thing it can show: at k=5 the closed-form bias (0.007335) falls **below** the
  measured seed spread (~0.0080) for the first time. If variance is still flat there, the bias term is
  formally subdominant to seed noise — a clean, principled "nothing left to gain on this axis" marker.
- **If instead the spread GROWS at k=5, that is the first evidence of the classical bias–variance
  tradeoff anywhere in this campaign** and it is a finding, not a footnote. Nothing measured so far
  (k=2/3/4, all flat) has seen it.

**Sizing, per BEN-030's second rule.** Rates measured from the k=4 split arms themselves — 5.90 and
6.13 min/seed — not from the 48-seed job's apparent 2.9 min/seed, which did not reproduce on the split
runs (different nodes/contention). That is itself the argument for re-measuring rather than reusing a
rate. Scaled by k/4: k=5 ≈ 7.5 min/seed, so 16 seeds ≈ 2.0 h and **32 seeds ≈ 4.0 h, which would have
missed a 4 h wall** — hence 8 h on the second arm. The launcher now takes `B1_NITER` and names its
products by it; its filename stays `sbatch_b1_niter4_scan48.sh` because renaming a tracked script
cited in a RUN_LOG is forbidden, and a note in the header says so.

### 2026-08-07 — five-band active laterals: the gate was FOOTING, not coverage; publication unfolds launched (56430128)

**The expensive part of the publication gate was already done.** Every number here came from a command
run while writing this entry.

| stage | measured state |
|---|---|
| P3F active event loops (5 bands × 2 endpoints × 12 playlists) | **120/120**, ~700 GB |
| P3S standard (regression controls, not FPS endpoints) | **120/120**, ~510 GB |
| FPS merged endpoint omnifiles | **10/10**, 74.8 GB each, 748,174,751,685 B total |
| FPS endpoint unfolds in `active_universe_5d/fps/unfolds/` | 10/10 present — **`bkg_mode=purity`** |
| `active_scalar_lateral_fps_cov.root` | **absent** |
| publication manifest / PASS receipt / component_build / p4 receipts | **absent** |

So `OPEN_ITEMS.md`'s "full five-band coverage remains the publication gate" is, read literally,
**already satisfied** — all five kinematic bands are covered at both endpoints in both modes. What
actually blocks adoption is the estimator **footing**: `fps_provenance.PUBLICATION_BKG_MODE` is
`negweight-refined`, the ten existing unfolds ran the driver default `--bkg-mode=purity`, and
`fps_control_manifest.json` says so about itself (`"label": "purity-control"`,
`"publication_gate_rejects_this": true`). `require_publication_manifest` fails closed on that footing,
so a control cannot enter the rollup even by accident. Recorded as **BEN-036**; the prose in three
docs was the thing that was wrong, not the campaign.

**Preflight, all green before any compute was spent** (each redirected whole to a file, then read —
BEN-026):
- `fps_verify_merged_receipt.py` → **PASS**, `run_id=56090877`, 10/10 live size+`int(mtime)` equal to
  the committed inventory, so the 748 GB is provably unchanged since it was hashed and needs no
  second hash pass.
- `audit_merged_fps.json` → `result = PASS`.
- mask artifact fingerprint == canonical `23b2a2f4e75f2421…`.
- CV `uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` recomputes to **266 nonzero
  of 285** bins, fingerprint == canonical, sha256 `16d99350cbfe6997…` == the manifest's bound
  `central_cv_sha256`.
- `fps_build_publication_manifest.py` dry-run → exits 2 listing **exactly** the ten missing negweight
  outputs and nothing else, and emits no manifest. That is the whole point of running it early: it
  proves no *other* gate is lurking four hours downstream.

**Launched `56430128_[0-9]`** — the committed `sbatch_unfold_active_fps.sh`, unmodified, 4 h wall,
`--array=0-9%5`. It writes into the separate mode-explicit namespace
`active_universe_5d/fps/unfolds_negweight_refined/` and leaves the purity controls in `unfolds/`
untouched, refusing to run at all unless `BKG_MODE=negweight-refined`.

**Sizing, per BEN-030.** Measured from the July driver logs of the runs actually being repeated, not
from a note: `p4fps_unfold_driver.log` 05:34:31 → 07:06:12 and `p4fps_unfold_driver2.log`
08:39:11 → 10:11:42, i.e. **~1h32m per wave of 5 concurrent** at CPT=24, twice, consistent. Two waves
under the `%5` throttle ⟹ ~3–4 h against a 4 h wall, with headroom for the extra Stay-Positive
refinement pass that `negweight-refined` does and `purity` does not.

**Why the CV's own background mode does not contaminate the result.** `build_active_lateral_fps.py`
forms `D = [x₀ − cv, x₁ − cv]` then mean-centers: `Z = D − D.mean(axis=0)` = `[(x₀−x₁)/2, (x₁−x₀)/2]`.
The CV cancels **exactly**, so it fixes only the reported mask and the hash binding, never the
covariance. Worth stating because it is the obvious thing to worry about when the endpoints change
background mode and the CV does not.

Durable watch armed (a session-local monitor would die with the session): wakerctl
`fps-negweight-unfolds-56430128`, kind `slurm-array`, tasks `0-9`. Waker cron verified live —
`last_tick 2026-08-07T00:41:02Z`.

**Remaining chain once the ten land**, all committed infrastructure, each taking an explicit `--out`:
`fps_build_publication_manifest.py` → `build_active_lateral_fps.py` → `p4_validate_active_lateral_fps.py`
→ `adopt_active_lateral_fps.py`.

### 2026-08-07 — the five-band chain RAN END TO END: +10.96% lateral, +9.12% combined (56430128, 56431823)

**Unfolds.** `56430128_[0-9]`, all ten `COMPLETED` exit `0:0`, 29–38 min each against a 4 h wall. Ten
ROOTs + ten receipts in `active_universe_5d/fps/unfolds_negweight_refined/`, every receipt reading
`bkg_mode: negweight-refined`, `result: PASS`, `launcher: sbatch_unfold_active_fps.sh`. The purity
controls in `unfolds/` were not touched.

**The first chain attempt failed, and the failure was a real bug in committed infrastructure — BEN-040.**
`56431689` exited rc=2 at step 1 in 192 s (before any hashing, because PASS 1 aggregates and exits).
All ten endpoints reported `config estimator=None != lgbm` and the same for the other four footing
keys. Cause: `fps_endpoint_receipt.cmd_write` writes the footing as a **nested** `"footing"` block
while `fps_build_publication_manifest.py` read those keys off the **top level**. They were always
`None`, so that gate **could not pass for any input that has ever existed**. It is fail-closed, so
nothing wrong escaped — it simply blocked the chain. It survived because the test fixture was
hand-built flat, matching the buggy reader instead of the real writer. Measured: on the real receipt
the old reader fails 5 keys and the new one 0; on the old fixture both pass. Fix is one line plus
reshaping the fixture to the producer's actual output, which converts that test into the guard.

**`56431823` — ALL FOUR STEPS PASSED**, 53:56 wall (16 + 12 + 12 + 12 min; the per-step floor is the
748 GB `require_recompute_hashes` pass, not the 266×266 algebra).

Per-band sqrt-trace of the selection-complete active lateral:

    BeamAngleX            1.1493e-40
    BeamAngleY            9.3351e-41
    MuonResolution        4.3796e-40
    Muon_Energy_MINERvA   7.8043e-39      <- dominant
    Muon_Energy_MINOS     2.1341e-39
    total                 8.1040e-39      (== sum of the 5; rollup identity PASS)

**p4 validation `RESULT PASS`, zero fails.** 266×266, finite, PSD (`min/max eig = -3.87e-16`),
`rel_asymmetry = 0.0`, all 266 diagonal entries reported, dim tied to the recomputed canonical mask
`23b2a2f4…`. Exact 5 active + 5 support band inventories.

**The headline comparison — this is what the gate was for:**

    sqrt_tr  active (selection-complete)  8.10399e-39
    sqrt_tr  support-limited block        7.30356e-39
    ratio                                 1.10960     -> +10.96%

So restoring the migrated lateral support **raises** the five-band lateral block by ~11%. The
support-limited construction was understating it, which is the direction the quarantine assumed but
had never measured.

**Adoption.** `adopt_active_lateral_fps.py` → `uq_universe_fps_covariance_combined_activelat.root`
(cand `3039183cf81d8d8f`). Pure component sum vs same-source subtraction agree to
**`rel = 3.45e-16`** against a `1e-9` tolerance — the hard gate that the swap is a sum and not a
subtraction. The five replaced blocks are renamed `*__SUPERSEDED_support` and never re-summed;
`hCov_universe4d_active_lateral_total` is added. `MinosEfficiency` and the three `GEANT_*` bands stay
ordinary universe bands, as they must — they are weight-only, not kinematic.

Effect on the combined FPS budget (`hCov_combined4d_total`):

    before  8.040779e-39
    after   8.774217e-39      +9.1215%

**It is not a uniform inflation.** Per-bin σ ratio over the 266 reported bins runs
min **0.7897**, median **1.0071**, max **1.4402** — some bins tighten, the tail grows by up to 44%.
Anything quoting a single scale factor for this replacement would be wrong.

Products (ROOTs are `.gitignore`d as `*.root`; every JSON receipt is committed):
`fps_publication_manifest.json` (sha `303e6ff7d6205e2c…`), its PASS receipt,
`receipt_component_build.json`, `p4_summary_active_lateral_fps.json`, `receipt_p4_validation.json`,
`receipt_active_adoption.json`. Active cov sha `c82c6610e4943fe1…`.

Launcher: `sbatch_fps_active_lateral_chain.sh`, new here, 8 h wall sized off the ~3 TB of hashing the
four steps do rather than off the arithmetic.

**Verification `56432855` (1:06:50, both rc=0).** Suite **`764 passed`** in 33:22, zero failures —
note that is 764/764, *better* than the 763-passed + 1-known-J28-fixture-failure baseline, because
`ae90c9b` fixed that fixture; the new cluster baseline is a clean 764. Verifier: **`ALL BINDINGS
INTACT`**, 868 bindings resolved / 864 OK / 20 shell pins seen against a floor of 15, and the same
4 known pre-existing submit-time drifts as before (`gate2_queue_hedge_controller.sh`,
`pet/sbatch_dump_g2_mefhc.sh`, `wakerctl.py`, `test_wakerctl.py`) — none touched by this work.
Worth recording for the next reader: `verify_hash_bindings.py` prints **only** at the end
(all prints are in the summary block), so its log is 0 bytes for the entire ~33 min run. That is
BEN-028 in its structural form rather than its buffering form — judge it by CPU (it held ~99.6%
of wall) and never by log growth.

## 2026-08-07 — J28 adoption on the repaired 160-throw ensemble; corrected totals are ~9% SMALLER

Two jobs, chained by `--dependency=afterok` so the second could not run on an incomplete ensemble.

`56427580` (array tasks 30–39 of `sbatch_uthrow_run_5d_fast.sh`, all `COMPLETED 0:0`, 45m41s–1h25m47s)
regenerated throws 120–159, restoring the **160/160** the adopted covariance was built from. Regeneration is
bit-reproducible because `unified_throw_cov.py:222-223` seeds per *global* throw index, verified empirically
by the matching `flux_u` draws — so these are the original throws, not statistical stand-ins.

`56429334` (31m23s, rc=0) then adopted. Its fail-closed gate ran first and confirmed the mixed-provenance
split before any work: `160/160 throws present; unstamped 0-29, stamped 30-39 -- split as expected`. Only the
30 pre-J28 slabs were rescaled (120 throws); the 40 natively-corrected throws were left alone, because
`unified_throw_cov.py:255` stamps newly-written throws and rescaling a stamped slab would double-correct it.

    full-160 before -> after (like-for-like, both n=160)
    sqrt_tr_unified         4.4607819710748654e-38 -> 4.443673650575504e-38    -0.38%
    joint_mean_shift_norm   1.654393237996853e-38  -> 1.878696733368378e-38   +13.6%

    adopted totals            old          new        factor   median frac/bin
    mean-centered          4.3455e-38   5.2600e-38   x1.210    13.43% -> 13.61%
    CV-centered (F7)       4.3455e-38   5.6609e-38   x1.303    13.43% -> 14.09%

Both PSD OK. `n_throws = 160` read back from the corrected ROOT.

**The corrected totals are ~9% smaller than the quoted 5.81e-38 / 6.24e-38, and the mechanism is the point.**
Correcting the flux raised the block-sum toward a nearly unchanged unified total, which drove the
nonlinearity inflation `g` toward 1 (mean-centered median now exactly 1.000, only 26.2% of bins above it).
Since the adopted covariance is `lateral+stat+ML + G C_vert G`, a smaller `G` inflates the vertical block
less. The old value was overstated *because* the understated Flux block had inflated `g` — so the flux block
growing 4.2× and the total falling 9% are the same fact seen twice.

Two guards worth recording. `adopt_unified_5d.py:79-80` defaults `--out` to the July adopted product and
opens it `RECREATE` (`:158`); both calls passed explicit tagged paths and the job verified the July file
untouched (892224371 bytes, Jul 13 18:58). And the whole replacement rests on the rescale being an identity,
which was checked against an independent native computation rather than assumed — 1.4e-12 agreement over
10,694 bins (`validate_rescale_identity.py`).

**Not final, and not for J28 reasons.** The section heading *"CANDIDATE; final lateral replacement pending"*
still stands; `values.tex` is untouched. The five-band selection-complete laterals are the remaining gate
(running as `56430128_[0-9]`).

## 2026-08-07 — D2 under-fitting probe: the shortfall is 97.8% per-bin SCATTER, and a stale handoff instruction

Tasked from `HANDOFF-20260806-2246Z.md` §4, "test the under-fitting hypothesis ... neither tested it".
**That instruction was stale** — `docs/OPEN_ITEMS.md` (a) already recorded "(ii) `epochs=8`
optimization-limited: **measured false**" from the six history pickles, and already carried the
retraction of the tilt-direction structure the same handoff repeats as live. Filed as **BEN-037**; a
session routed through the handoff alone spends ~14 GPU-hours re-deriving a settled null.

**The new result, at zero GPU cost.** The closure scores `1 - E_w[|1-r_b|]` over 285 cells, and an
absolute value turns per-cell noise into a one-sided penalty. Splitting it (`r_b =
(u_b-p_b)/(t_b-p_b)`, `w_b = |t_b-p_b|`):

    aggregate L1 recovery          0.54685
    signed mean response  E_w[r]   0.63129     <- reproduces OPEN_ITEMS' number exactly
    dilution ideal                 0.63321
    bias vs ideal                 -0.00192
    SCATTER PENALTY                0.08443     <- 97.8% of the 0.086354 gap to the ceiling
    overshoot bins                 87 of 262, carrying 24.1% of displacement

**The estimator has essentially no bias left to remove; the powered closure is measuring per-cell
variance.** That is the substantive argument for redesigning the criterion rather than the estimator.
Two traps recorded as **BEN-038**: the per-band L1 column reads like undershoot where the signed bias
is ~0 (`a_b>=0.50`: L1 0.7943 vs ceiling 0.9704, bias only **-0.0116**; the `a_b>=0.70` band actually
*overshoots*, `E_w[r]=1.0333`) — this session wrote the wrong reading into a draft before the signed
split caught it — and an aggregate-phrased predeclared rule returns CONFIRMED for a synthetic pure
bias shift, which is how the unit test caught it.

Also ruled out free, from the artifact's 2,000,000 push weights: **saturation** (max implied logit
**1.041** against `REWEIGHT_LOGIT_CAP = 30.0`, zero rows near the cap) and **global shrinkage** (push
spans [0.562076, 2.832002] against an injected tilt range [0.548710, 2.653992]). The ceiling
reproduces exactly at **0.633208** (k=3) from the committed acceptance map. Low-acceptance cells
(`a_b < 0.01`, 23.2% of displacement) reach signed **+0.1525** against an independence ideal of
**0.0082** — transport observed, so **0.6332 is a reference curve, not a bound**.

**Code.** `closure_powered_truth_reweight.py` gained `--niter` / `--epochs` / `--early-stop`, each
defaulting to what it already used (`early_stop` read off `MultiFold.__init__`'s signature via
`inspect`, not mirrored as a literal). **The policy constant is untouched** — the queued nominal
`56415634` reads it. The report now records **effective** values in `configuration` plus
`configuration_policy` / `configuration_overrides` / `is_nominal_configuration` /
`early_stop_patience`, so Gate-4's `powered:nominal_configuration` fails closed on a probe report by
construction. Verified login-safe (importing the driver still does not import TensorFlow) and
byte-identical on the gate route (the engine's own `early_stop` default is 10, which is what it
already used). `sbatch_powered_closure.sh`'s `EXPECTED_DRIVER_SHA` moved `69bec696… -> a45fae7c…` with
the move recorded in-file: it is a submission-time guard, **no receipt binds this driver** (grepped
over `state/` and every `*.json`), and `56381674`'s log and report still record the old sha as what
ran. Its no-override guard now also forbids the three new flags. New:
`sbatch_powered_closure_budget_probe.sh` (writes to `powered_closure/underfit_probe/` under a
different report basename, so a diagnostic can never be read as gate evidence) and
`analyze_powered_closure_budget_probe.py`. `SHELL_PIN_FLOOR` 13 -> 15, counted before raising.

**Arms submitted** (IDs and parameters read back from `scontrol` in the submitting turn, BEN-027):
`56431649` ctl8 epochs=8 / 4h, `56431650` ep16 epochs=16 early_stop=1000 / 7h, `56431651` ep32
epochs=32 early_stop=1000 / 11h. Sized off `weights.slurm-56381674/*.pkl` mtimes — 2.00 min/epoch
step 1, 2.79 step 2, 14.4 min per epoch across all six trainings, reproducing the baseline's 1h58m.
Durable wakerctl watches `d2-probe-{ctl8,ep16,ep32}-<job>` armed; waker tick live 2026-08-07T01:50:23Z.
No fourth early-stopping arm: Keras 2.15 restores best weights **only** inside the stop branch, so with
this flat val curve it would likely never fire and would duplicate ep32 for ~8 GPU-hours.

**Suite.** BEFORE at `f3ba262`, clean tree, job `56430155`: 763 passed + 1 known J28-fixture failure,
verifier ALL BINDINGS INTACT (863 resolved, 859 OK, 18 pins). Rebased onto `github/main` mid-session;
`ae90c9b` **tracked** `test_uq_remediation.py` and **fixed** that fixture, so the baseline to compare
against is now **764 passed / 0 failed**. The rebase was blocked by that same file as an untracked
path — resolved per BEN-031 by copying it aside to
`/pscratch/sd/j/josephrb/d2_pull_backup_1786067384/`, never `git stash`.

**No threshold was touched.** `recovery_min = 0.80` is unchanged and is not evaluated by the analyzer.

## 2026-08-07 — GBDT close-out G-0/G-1: the standard lane can now express a background footing

Runbook `docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md`, packets G-0 and G-1. No physics ran.

**§1 state table re-verified against Perlmutter before acting** (it was written the same day, and
scratch is purgeable). All rows held: ten standard lateral ROOTs dated 2026-07-18 03:53–05:34Z with
**zero** `.done` receipts and ten logs; exactly one `*activelat*` product on scratch and it is the FPS
one; the J28 full-160 covariance present (2.67 GB, Aug 6 17:38); **no** `p4_standard_manifest.json` and
**no** `std_final5_candidate*` anywhere, i.e. P4-5D genuinely unbuilt. `sacct` re-confirmed
`56430128_[0-9]`, `56431823`, `56427580_[30-39]`, `56429334` all `COMPLETED 0:0`. The PET GPU job
`56431651` is still `PENDING (Priority)`, which is why this CPU-only lane does not contend.

**§3's log evidence independently re-derived in the same session**: all ten logs carry exactly one
`[INFO] measured training:` line and **zero** carry a `bkg-mode=` line — the purity branch is the
silent branch, so absence is positive identification (BEN-041).

**G-0.** The purity decision and its revisit obligation are now an open item in `docs/OPEN_ITEMS.md`,
including what would close it (a full 5D 187-universe both-mode comparison at 5-iter `lgbm`) and what
stands in for it today (§2.1: SYST ratio 0.9863, STAT 0.982, real-data totals −0.13%, plus the
ρ1 = D − B_u identity). The 5D leg of that evidence is a two-universe spot check at 1 iter/`hist`, so
the entry states explicitly that "footing proven irrelevant in 5D" must not be written.

**G-1.** The standard lane was footing-blind by construction (`KNOWN_ISSUES.md` #20(a)). Now:
`P4Config.bkg_mode` is validated and participates in `config_hash`; `P4Config.footing()` emits the
nested five-key + `bkg_mode` block in the **producer's** shape; `p4_lib.require_standard_footing`
fails closed on absent, mismatched, or **flattened** footing, mirroring
`fps_provenance.require_footing`'s "unprovable" semantics; `p4_lib.classify_log_bkg_mode` encodes the
two-branch print asymmetry so an indeterminate log returns `None` rather than defaulting to purity;
and `p4_evidence.py` writes both the declared `footing` and per-endpoint `footing_evidence`, blocking
when they disagree. `run_p4_unfold_std.sh` passes `--bkg-mode` explicitly, read from `P4Config` so the
launcher and the manifest cannot drift, and stamps it into both receipt shapes.

**This is a provenance change and a physics no-op** — `purity` is already the driver default
(`unfold_nd_omnifold_unbinned.py:566`), so a re-unfold must reproduce the 2026-07-18 ROOT hashes
exactly. That is the check that gates G-3; a hash change means stop, not adjust.

`fps_provenance.py` was deliberately **not** touched (verified by an empty diff): the standard
constants are a separate copy rather than an import, because the FPS grid constants are hash-pinned
into gates that just went green (BEN-040's lane).

Tests **41 passed / 0 failed** (28 pre-existing unchanged, 13 new). The purity fixture is a **verbatim
real unfold log** copied off scratch, not hand-assembled to match the consumer — the inversion BEN-040
records. A contract test pins the classifier to the driver's actual `print` statements so a producer
change fails a test instead of silently mislabelling a footing. `.gitignore`'s blanket `*.log` was
silently excluding that fixture, which would have passed locally and failed on a fresh checkout; a
negation scoped to `nd-unfolding/tests/fixtures/*.log` fixes it.

Next: G-3 (`STOP_AFTER=evidence`, then attest-or-reunfold), then the G-4 independent verifier.
`P4_VERIFIER_PASS` is **not** set by this session — `run_p4_standard.sh:41` only tests non-emptiness,
so setting it would defeat the checkpoint rather than pass it (`KNOWN_ISSUES.md` #21).

## 2026-08-07 — GBDT G-3 preflight: EVIDENCE-COMPLETE, and the ten ROOTs are attestable

`STOP_AFTER=evidence bash nd-unfolding/run_p4_standard.sh` inside its own CPU holder
(`ALLOC_JOB_NAME=gbdt-hold`, job **56445593**, `nid004290`, interactive QoS, node in ~20 s). A
separate holder deliberately, so the concurrent lane's shared `claude-hold` alloc was untouched.
Wall **~71 s** (11:58:45 → 11:59:56Z). Holder released and the lingering login-node `salloc` client
killed (AGENTS.md salloc lesson 3); `squeue --me` afterwards shows only the other lane's two PENDING
jobs.

**Stage 1** — 10/10 merged endpoint ROOTs SKIPped as valid (53.8 GB each, 538 GB total; nothing
re-merged), `merged=10/10 failed_children=0`, acceptance audit `passing=120/120 complete=True
missing=0 extras=0 failing=0`.

**Stage 2** — `EVIDENCE-COMPLETE`. All five independent cross-checks MATCH (central5d, mask5d,
endpoint_manifest, central4d, mask4d); `mask5d n=10694`, `mask4d n=4830`. Selection migration is
exactly the expected pattern: `BeamAngleX/Y` nonzero (4792/4700/4807/4808), the three
`MuonResolution`/`Muon_Energy` bands 0 (bin-migration-only).

**Attest-or-re-unfold: ATTESTABLE, decided by measurement.** All ten on-disk endpoint ROOTs were
sha256'd and compared to the committed manifest's `endpoint_sha256`: **10 match, 0 mismatch, 0
missing**. So stage 3 will legacy-attest and the runbook's ~1h40m re-unfold budget does not apply.
The reference manifest is preserved at
`docs/orchestration/state/p4-standard-attestation/p4_standard_manifest-20260718-preserved.json`
(scratch is purgeable, and stage 2 rewrites the live copy).

**Two things the preflight settled that the runbook could not.**
1. The pre-G-1 manifest has **no `footing` block and no `bkg_mode` in `config`** — read directly off
   the file. That is `KNOWN_ISSUES.md` #20(a) confirmed against the artifact rather than the prose,
   and it is what G-1 fixes.
2. §1's "no `p4_standard_manifest.json`" impression was **my own probe error**, not a runbook error:
   my first `find` used `-maxdepth 3` and the evidence dir is at depth 4. The manifest has existed
   since 2026-07-18 11:14, which is precisely why attestation is available.

**Stage 3 was deliberately NOT run.** `run_p4_unfold_std.sh` skips any endpoint that already has a
receipt, so writing receipts now — on pre-G-1 code — would stamp ten `.done` files with **no
`bkg_mode`**, and they would then be skipped forever. Deletions are frozen behind the reorg freeze
tag, so that would be an unfixable provenance regression. Stage 3 waits for the G-1 patch to reach
the cluster checkout.

**Blocked on that delivery, and it is not mine to force.** The canonical cluster checkout is at
`0028b49` and moved twice while this ran — a concurrent lane (push-provenance / pull-push
decomposition) is committing and pushing to `main` in that same tree. Switching its branch to my
`worktree-gbdt-closeout` would pull the code out from under a live session, so it is Joseph's call.
Note a cluster-side `git worktree` does **not** work around this: `p4_evidence.py` hardcodes `REPO`
and takes its `source_blobs` with `cwd=REPO`, so it would record the canonical tree's blobs while a
different file actually ran — a provenance lie of exactly the kind this packet exists to remove.

**G-4 is not the formality the runbook implies — see BEN-046.** The `standard-p4-verifier`
(`019f74cb-…`) **BLOCKed** repair-3 `74fa362` with six ranked defects; `followup-agent-A-standard-05.md`
is the repair-4 brief and **no repair-4 commit exists** (`git log 74fa362..HEAD` over `p4_*`/`run_p4_*`
returns only `d5bd5da`, an unrelated note-overclaims commit, plus the FPS lane's own repairs and this
packet). `P4_STANDARD_STATUS.md`'s "REPAIR round 3 complete" describes the attempt, not the verdict.

`P4_VERIFIER_PASS` remains unset by this session, per `KNOWN_ISSUES.md` #21.

## 2026-08-07 — GBDT G-4: the verifier's BLOCK still stands, and stages 4–6 cannot run at all

**Verdict: BLOCK. `P4_VERIFIER_PASS` NOT set by this session** (`KNOWN_ISSUES.md` #21 — the gate at
`run_p4_standard.sh:41` tests only non-emptiness, so setting it would defeat the checkpoint rather
than pass it). Covariance stages 4–6 are **not** authorized, and G-5 onward is untouched.

**Delegate attempts.** Two read-only lanes per `CLAUDE.md` were tried and neither returned a verdict:
`claude -p --allowedTools "Read,Grep,Glob,Bash"` on `claude-personal` hit a weekly account limit
(resets Aug 9), and `codex exec --sandbox read-only` hit a usage limit on `codex-personal` and then,
on `codex-school`, ran ~2.5 h and wedged in tool-use without emitting its verdict block (killed).
**No delegate opinion is recorded, and none is claimed.**

**What replaced it is better than a fresh opinion: the ORIGINAL verifier's verdict is committed in
this repo.** `docs/orchestration/runs/standard-p4-verifier/20260718T182040Z-send-8e4ca3d7.jsonl` is
the `standard-p4-verifier` session transcript, and its final agent message opens with **`BLOCK`** on
`74fa362`, with per-defect file:line citations. It confirms the chain is clean in the ways that were
checked (HEAD == `github/main` == `74fa362`, all 11 commit-owned paths byte-identical, no candidate
product, no working-tree contamination) and then says: *"Nevertheless, repair-3 does not safely
authorize construction."*

**Verifier defect 1 re-verified against HEAD in this same turn, and it is still 100% live — stages
4–6 would CRASH, not merely be unreviewed.** New `KNOWN_ISSUES.md` **#22**. Three mismatches:
- **Validator CLI.** Driver passes `--active … --support … --merged-dir …`
  (`run_p4_standard.sh:49-52`); `p4_validate_active_lateral.py:35-39` defines
  `--candidate --support --manifest --merged-audit --out`, all `required=True`. Two options passed
  do not exist and three required ones are missing → argparse aborts.
- **Projector CLI.** Driver passes `--proj` (`run_p4_standard.sh:54`); `p4_project_4d.py:46-49`
  defines only `--c5 --manifest --out --central-rel`. No `--proj` → argparse aborts.
- **Nonexistent ROOT key.** Driver names `hCov_std_final5_candidate` (`:50`, `:53`); a repo-wide
  grep finds that string **only in those two lines**. The builder writes
  `hCov_stdsyst5d_total_candidate` and `hCov_stdcombined5d_total_candidate`
  (`p4_build_components.py:159-162`).

So authorizing the token would not produce a candidate covariance — it would write a candidate ROOT
at stage 4 and then abort at stage 5. **The reason this was never noticed is that `STOP_AFTER`
defaults to `evidence`**, so the default path stops at stage 2 and stages 4–6 have never executed.
Today's preflight ran cleanly for exactly that reason. An unexecuted fail-closed path is an untested
one — BEN-040's lesson, one lane over.

**Scope consequence.** G-4 is not a checkpoint to walk through; it is an unstarted repair round
scoped by the six items in `docs/orchestration/followup-agent-A-standard-05.md`, of which defect 1
alone also requires re-ordering the stages (merged audit → unfold → endpoint evidence) and updating
`AGENT_A_HANDOFF.md:95` to the same executable contract. Repairing only the flag names would give a
chain that runs and is still wrong. Recorded as BEN-046 and `KNOWN_ISSUES.md` #22.

## 2026-08-07 — Re-running evidence re-attributes the endpoints to newer code (KNOWN_ISSUES #23)

Noticed by diffing the tracked `p4_standard_manifest.json` after the (idempotent) preflight rewrote
it. **Every physics binding was byte-identical** — `central5d_sha256`, `central4d_sha256`,
`mask5d_hash`, `mask4d_hash`, `config_hash` `5efd31a4…`, `endpoint_sha256`, `axis_edges`. So the
regeneration was numerically a no-op, which is the reassuring half and is also why it would be easy
to wave through.

The provenance half moved: `binary_sha256` `6b60fc51…` → `61d7dfbf…` (mtime +290,733 s ≈ 3.4 days),
`source_blobs.unfold` `7b65ebcf…` → `dc74c38f…`, `source_blobs.launcher` `559bc3fb…` → `f2a49e7d…`,
and their `source_commits`. Structural, not a race: `p4_evidence.py:150-151` hashes the C++ binary as
it is on disk at run time, and `:137-141` hash the **working-tree** copy of each source path. Neither
is tied to the artifact being described, so a manifest regenerated today asserts today's driver blob
and today's binary next to `endpoint_sha256` values for ROOTs produced on 2026-07-18 by the *older*
driver — a producer claim that is demonstrably false.

Nothing is corrupted and no quoted number moves. But this is the standing verifier's **defect 3**
("regenerate evidence only from exact committed blobs … record the commit containing each blob")
observed live, and an attestation built on the manifest would inherit the mis-attribution.

**Action taken:** the regeneration was **reverted** on the cluster (`git checkout --` on that one
tracked file) so the committed manifest still records the 07-18 producers, and the cluster tree is
back to 0 tracked-dirty — it is shared with a live concurrent lane and must not be left dirty. A copy
is preserved at `docs/orchestration/state/p4-standard-attestation/p4_standard_manifest-20260718-preserved.json`.
No hash was hand-edited and no tolerance was touched.

## 2026-08-07 — Repair-4 landed all six defects; the verifier closed two and BLOCKed on four

**Verdict BLOCK. `P4_VERIFIER_PASS` NOT set. Stages 4–6 remain unauthorized.** Receipt and full
transcript committed at `docs/orchestration/runs/standard-p4-verifier/20260807T134623Z-repair4-verdict.json`
and `…-repair4-transcript.txt`. Delegate: `codex exec --sandbox read-only` on `codex-school`,
188,847 tokens; it wrote nothing — `git status --short --untracked-files=all` and `git diff HEAD`
were both empty afterwards, so there was no diff to preserve.

**Repair-4 as built** (six commits, `ba2cdd8` `febb9a1` `c57746c` `6b875b2` `886c65f` `39c2cf4`):
driver reordered to merge+audit → unfold → evidence with the real validator/projector CLIs and a
candidate key single-sourced in `p4_lib`; content-validating resume via `p4_check_receipt.py`;
committed-blob provenance; `(band,index)` and both migration directions enforced on producing and
consuming sides; mandatory edge/bin-volume/4D-mask hashes plus an M-content hash; retained
components persisted; candidate-then-manifest-last; and an integration harness that executes a
real gate. `STOP_AFTER` default moved `evidence` → `audit`, because the reorder put a
receipt-WRITING stage before evidence and the old default would have started writing.

**Closed: defects 1 and 5.** **Outstanding: 2, 3, 4, 6** — all four accepted as correct.

1. **D2** — `validate_endpoint_receipt` requires `code_rev` to be a *non-empty string* and never
   compares it; no source blob is recorded at all, so an endpoint produced under changed source
   still skips. This is the **same non-emptiness anti-pattern the lane already records as
   `KNOWN_ISSUES.md` #21**, reproduced inside the gate written to end it. Worth stating plainly:
   the failure mode is not exotic, it is the one already written down.
2. **D3** — the dirty-source guard is **fail-open on deletion**: `need(_w is None or _c == _w)`
   passes when `git hash-object` fails on a missing file.
3. **D4** — containment matches the component sequence *anywhere*, so
   `/evil/active_universe_5d/standard/candidate/out.root` passes, and `normpath` does not resolve
   symlinks. Separately the PSD residual check was **named** a full-total identity: PSD of
   `C_combined − C_syst` is necessary, not sufficient, and never compares the residual to the
   bound stat+ML blocks.
4. **D6** — still executes no shell driver and no builder→validator happy path, and a test name
   blesses the weaker PSD check as the stronger claim. The shell-driver gap was disclosed in the
   test docstring, but disclosure is not coverage.

**Tests — read this before "fixing" anything.** The delegate reported **82/99**; a local re-run at
the same commit is **99/99**. The 17 shortfalls are an environment artifact: the read-only sandbox
has no writable temporary directory, so every `tempfile.TemporaryDirectory()` test errored before
reaching an assertion. The delegate diagnosed that itself and did not count it against the code.

**Repair-5 is scoped to exactly those four items.** Defects 1 and 5 are closed and must not be
re-opened. `4d` (no promotion in `p4_adopt_standard.py`) was judged an acceptable non-repair —
adoption is out of scope and the chain stops at CANDIDATE by design.

## 2026-08-07 — Repair-5 closed D3 and D4a; BLOCK again, and finding 1 is a bug I introduced

**Verdict BLOCK. `P4_VERIFIER_PASS` NOT set. Stages 4–6 remain unauthorized.** Receipt and
8,441-line transcript at `docs/orchestration/runs/standard-p4-verifier/20260807T220756Z-repair5-verdict.json`
and `…-repair5-transcript.txt`. `codex exec --sandbox read-only` on `codex-school`, 287,574
tokens; wrote nothing (`git status` clean afterwards, no diff to preserve).

**Closed: D3** (dirty-source fail-open on deletion) and **D4a** (containment, now realpath-
anchored and symlink-proof). The narrow stat+ML residual comparison and the untouched
`fps_provenance.py` constants were also accepted. **Six outstanding.**

**Finding 1 is the one that matters, and it is mine.** The legacy-attest path stamps the
CURRENT `CODE_REV` and `UNFOLD_BLOB` onto a receipt for a ROOT produced **2026-07-18 by an
older driver**, then the skip gate compares against those same current values and passes. So
the receipt asserts a producer that demonstrably did not produce the file. **This is the exact
provenance lie recorded as `KNOWN_ISSUES.md` #23 — which I found myself, in the manifest —
reproduced in the receipt while repairing something else.** A legacy-attested receipt must
carry the HISTORICAL producer, or record that the producer is unknown and refuse to let that
satisfy a source-identity comparison. Verified in-code at `run_p4_unfold_std.sh:60-68`.

**Finding 3 is the sharpest.** The D2 self-guard **stubs the live blob and revision to equal
its own fixture**, which is precisely the configuration in which finding 1 is invisible. A
self-guard that shares an assumption with the code it guards is not independent. Joseph's rule
that each repair must name an assertion which fails on reintroduction was right, and my
implementation of it had exactly the hole the rule exists to prevent.

**Finding 2** — my own pattern sweep missed `C_syst_eq_retained_plus_active_relerr`: recorded
by the builder, checked by neither consumer, and never recomputed, so a wrong-but-PSD `C_syst`
passes. It is *recomputable* now that repair-4's 4a persists the retained components, which
makes the omission worse, not better.

**Findings 5 and 6 overturn two judgement calls I made, correctly.** I reported the native-miss
fields and `check_support_comparison` as acceptable to leave. For the native-miss fields,
requiring `n > 0` plus mutual consistency needs no new physics and the real files already
satisfy it — I overstated the difficulty. For `check_support_comparison`, the point is not that
it is diagnostic but that the validator records it as `complete_support_comparison` in the PASS
gate list, so the label claims what the check does not deliver. **Finding 4**: making the
migration-policy comparison conditional on optional fields left the defect in place for every
caller that omits them — a repair that can be opted out of by omission.

**Tests.** Delegate 90/111 with 21 environment errors; local re-run at the same commit is
**111/111**. `TMPDIR` was exported specifically to remove the previous round's 17 tempfile
errors and did not reach the sandbox. Environment, not code — but finding 3 is the reminder
that passing locally is not the same as the guards being strong.

**Repair-6 is scoped to those six.** D3 and D4a are closed and must not be re-opened.

## 2026-08-07 — Re-unfold: NOT byte-identical, but NOT a semantics change. The ROOTs are non-deterministic.

**Job `56471429`**, CONC=6, ten endpoints, 0 failures. The ten 07-18 ROOTs were moved (not
deleted) to `active_universe_5d/standard/unfolds__SUPERSEDED_20260718/` first.

**sha256: 0 of 10 identical.** That trips the runbook's stop condition, so the chain stopped
here. But the sha256 test was the wrong instrument, and the right one gives the opposite answer.

**Histogram contents, new vs superseded, all 65856 bins:**

| | |
|---|---|
| max absolute bin difference | 6.5e-51 … 5.3e-49 |
| **max RELATIVE bin difference (worst of ten)** | **1.912e-11** |
| bins differing | ~10 677–10 694 of the 10 694 reported |

**Coherence test — is it a shift or is it noise?** Pooled over **106 940** reported bins:
mean `-1.758e-13`, sd `1.961e-12`, so **|mean|/sd = 0.090**; fraction of bins with positive
deviation **0.4594**. Per band, |mean|/sd ≤ 0.484. The **integrated cross section agrees to
`-2.6e-14`** — fourteen significant figures.

So the deviation is **scattered and sign-balanced, not coherent**: floating-point
non-determinism at the 1e-12 level, not a physics change. A real semantics change (a flux
renormalisation, a different background branch) would appear as a coherent ratio, and does not.

**Cause.** Almost certainly thread-order-dependent summation in LightGBM/OpenMP: the 07-18 run
used CONC=4, this one CONC=6, so a different core allocation gives a different reduction order,
and five OmniFold iterations amplify last-bit differences to ~1e-11. **Not confirmed by
experiment** — confirming it costs one ~30 min single-endpoint run at CONC=4.

**The load-bearing consequence, which is bigger than this comparison.**
**These ROOTs are not bit-reproducible, so sha256 identity is not a reproducibility property of
the computation — it pins one particular RUN.** Everything in this lane that treats an endpoint
hash as a derivation fingerprint inherits that:

- `endpoint_sha256` in `p4_standard_manifest.json` binds an artifact, not a derivation.
- **The legacy-attest design was built on an assumption that is false.** "Re-unfold and compare
  hashes" can never succeed, so attestation-by-hash could only ever have certified *the same
  file*, never *the same computation*. Repair-6 deleted that path for provenance reasons; this
  is a second, independent reason it had to go.
- Any future re-unfold changes all ten hashes and every binding computed from them
  (`endpoint_manifest_hash`, and the merged-inseparability comparison that consumes it).

**What a reproducibility gate must compare here is CONTENTS at a declared tolerance, not bytes.**
The observed floor is ~2e-11 relative per bin and ~3e-14 on the integral.

Before the run I predicted byte-identity, from J28's remap being the identity on this grid
(verified, `max abs diff 0.0`) and J33 being a fail-closed guard. That reasoning was right about
the two code changes and wrong about determinism — the differences do not come from either
commit. Recorded because the prediction being wrong for a reason unrelated to the hypothesis is
exactly the kind of near-miss that reads as confirmation later.

**Also, my miss:** the re-unfold script did not use `python3 -u`, so per-endpoint progress was
invisible for the whole 1h20m (BEN-028; the runbook says to use `-u`). Liveness had to be judged
from `sstat` CPU time and process count instead, which worked, but the script should carry `-u`.

## 2026-08-07 — CORRECTION to the entry above: the sign argument was wrong and is withdrawn

The re-unfold entry above called the deviation **"scattered and sign-balanced"** and offered
that as the discriminator against a coherent shift. **The sign half is wrong.** Joseph caught
it; re-derived here in the same turn:

    n = 106,940 reported bins,  SE(p) under p0 = 0.5  is  sqrt(0.25/n) = 0.001529
    observed fraction positive = 0.4594  ->  z = (0.5 - 0.4594)/0.001529 = 26.6 sigma

Bins are correlated so the effective n is smaller, but not nearly enough to rescue the claim:
at 10% effective n it is still 8.4 sigma, at 1% still 2.7 sigma, and reaching balance needs the
effective n down near **107** bins — not credible across 10,694 reported bins in each of ten
endpoints. **There IS a systematic sign preference.** Calling 0.4594 "≈ 0.5" was eyeballing a
number that is 26 sigma from its null.

**The conclusion is unchanged and is in fact better founded, but it now rests on MAGNITUDE
alone.** A different OpenMP partitioning is a different DETERMINISTIC rounding path, so a small
consistent sign bias at the 1e-13 level is the *expected* signature of that mechanism —
symmetric noise is not. `sqrt(N) * eps` for ~1e7 events is `7.0e-13` (double eps 2.22e-16),
against a measured pooled mean of `-1.76e-13`: same order. So the sign bias is evidence *for*
the round-off reading, not against it.

**The sign argument is withdrawn rather than patched**, because it was offered as the
discriminator against a coherent physics shift and it cannot do that job — a coherent shift
would ALSO show a sign preference. What separates the two hypotheses is scale:
max relative bin difference **1.9e-11** and integral agreement **2.6e-14**. Those numbers alone
carry the verdict.

Per Joseph: the CONC=4 confirmation run is skipped — thread order versus any other mechanism
does not change a 1e-13 verdict.

## 2026-08-08 — PET full-event nominal RE-TRAINED under the BEN-043 fix; Gate A/B bit-exact on both arms

**Job `56445883`** `COMPLETED` `0:0`, elapsed **06:00:44**, `2026-08-08T04:57:12` → `2026-08-08T10:57:56`
local (11:57:12Z → 17:57:56Z). Authorised by Joseph 2026-08-08 as option (1) of
`FINDING-20260807-checkpoint-is-not-the-trained-model.md` §6; gate receipt
`p3f-pet-gate4-launch-code-gate-20260807.json` with `nominal_pet_training_allowed: true`.

Products (the 2026-08-06 pair is archived under `pet/fullevent_nominal/superseded-20260806/`, digests
verified across the move):

    pet_fullevent_nominal_weights.npz   sha 58f664cdef266d09cbae22a5…   10,127,331 B
    pet_fullevent_floor_weights.npz     sha 14cccc231dfd92c93363eed2…   10,132,738 B

Both carry the BEN-043 contract: `step2_checkpoint` → `*_step2_final.weights.h5`, `step1_checkpoint`
added, `step2_checkpoint_best_epoch` retained, and
`checkpoint_semantics = "final-epoch weights, round-trip verified (BEN-043)"`. The driver's in-run
round-trip guard printed `(round-trip verified)` for both steps on both arms.

**Gate A/B — bit-exact on BOTH arms**, at the engine's own `batch_size = 512`:

    arm      A1 mc_indices   A2 truth norm   B(ii)    B(i) max rel dev   verdict
    nominal  bit-exact       bit-exact       72/72    0.000000e+00       GATE_AB_PASSED
    floor    bit-exact       bit-exact       72/72    0.000000e+00       GATE_AB_PASSED

Receipts `GATE_AB_PUSH_PROVENANCE.slurm-56445883.batch512.json` and `…floor-56445883.json`. The
batch-1000 receipt `…slurm-56445883.json` (`1.744800e-06`, FAIL) is retained deliberately: it is the
BEN-072 near-miss, caused by this gate defaulting to a batch size the engine does not use.

**Fold-forward ratio, and its reproducibility:**

    nominal  0.736746   34.46% below R = 1.1240802949941018
    floor    0.740546   34.12% below R
    spread   0.003800 = 0.516%

Two independent trainings at identical seeds agree to **0.52%**, so the ~34% deficit is a property of the
estimator at this configuration and not run-to-run variation.

**Step-1 decomposition on faithful weights** (`STEP1_DECOMPOSITION.slurm-56445883.json`,
`reconstruction_is_checkpoint_based: false`): step 1 delivers **58.6%** of its own objective
(`pull_final` 0.658944 vs R); **step 2 is exonerated** at a 0.44% undershoot of its own target and
1.010853 at iteration 1; and step 1's final increment is **wrong-signed** — `increment1` 0.648331 where
≈1.16 is required.

**NOT QUOTABLE.** Gate-4 remains red on D2 recovery, and predeclaration branch C stands: no product is
quoted while any leg is red. What changed is that full-event extraction is now *possible* —
`check_subsample_agreement` (tol 1e-3) was failing closed at 0.866 and is now 0 — and whether to run it is
Joseph's call, not a consequence of this run.

## 2026-08-09 — CLM-012 ADOPTED, Gate-4 branch A taken, and two jobs launched

**Joseph closed both open decisions.** Recorded here because a decision that lives only in mail is a
decision the next session cannot audit.

**1. CLM-012 adopted, and the bar is now a fraction of the achievable ceiling.** Gate-4's D2 criterion
moves from `recovery >= 0.80` ABSOLUTE to `recovery >= f * ceiling` with `f = 0.80` and
`ceiling = 0.618228` (per-event), giving a threshold of **0.494582** against a measured **0.546853** —
margin **0.052271**. Enforced as `residual_over_gap_max = 1 - f*ceiling = 0.505418`, derived in code
rather than restated, with `powered:criterion_derivation_consistent` failing the gate if the comment
and the enforced number ever disagree.

*Why this is a specification correction and not a tolerance raise:* 0.618228 < 0.80, so the retired bar
sat **above** the ceiling — no estimator, however good, could satisfy it. It was measuring the
acceptance and reporting the answer as an estimator verdict. That is the BEN-070/071 "threshold beyond
reach" defect with the inequality reversed: a gate that could never PASS rather than never FIRE.

*The one condition that rationale rests on, stated because it is easy to lose:* it holds under the
per-cell (Jensen-corrected) reading. CLM-012 caveat (iv-d) records that the scalar-scope curve gives
`1-(1-0.42351622)^3 = 0.808415`, **above** 0.80 — under that reading the old bar was satisfiable and
the rationale fails. The per-cell reading is the correct one, and it also makes the old bar look
*derived with a Jensen error* rather than invented (0.808415 is only 0.0084 above 0.80). Conditional
claim about a derivation, not an impossibility proof; `test_the_old_absolute_bar_sat_above_the_per_cell_ceiling`
goes red if a scalar-scope value is ever frozen in its place.

*Sensitivity, verified independently against Joseph's numbers (all five reproduce exactly):* the
+/-2 pp ceiling swing moves the threshold +/-0.016, worst case 0.510582, still cleared; the ceiling
would have to reach 0.683566 (+6.5 pp, 3.3x the stated sensitivity) to flip the verdict. Written into
the criterion text so the next reader does not redo it.

*Conditions (a)-(d) all met*, and per (c) the **injection is pinned alongside the weighting** —
amplitude 0.35, clip_z 3.0, rate-preserving, split_seed 7, half 2e6 — because a ceiling that is a
property of (detector x injection x weighting) is only a criterion once all three are specified.
Unpinned, BEN-045 repeats one level up.

*CLM-012 was NOT promoted past VERIFIED-NUMERIC.* Condition (d)'s re-derivation corrected the claim in
five places and withdrew its one prediction, so the model stays `ASSUMED`-grade. Adopting a bar is a
decision; it is not evidence for the model that motivated it.

**2. Gate-4: branch A.** Re-issued as `p3f-pet-gate4-launch-code-gate-20260809.json`; predecessor
`...-20260807.json` retired in the same commit with `files` renamed to `files_at_issue` per the repo
convention — its two hashes legitimately no longer match the tree and must not be expected to.
**Branch C still governs quotability:** the fold-forward deficit is untouched, so no product is quoted.
Gate-4's disposition is not a quotability verdict.

*Detour worth recording:* I first "fixed" the binding breakage by teaching `verify_hash_bindings.py` to
skip receipts marked `superseded_by`, then found the repo already had a mechanism —
`test_superseded_receipts_hold_no_live_bindings` requires the rename — and reverted mine. One mechanism,
already tested, beats a second one I invented because I had not looked. The skip also briefly appeared
to disable the Gate-2 runtime binding (three receipts share that basename; two are retired under
`superseded-*/`), which my basename-only output made look like self-supersession.

**3. Two jobs launched, both watched.**
  * `56525297` — **NON-QUOTABLE diagnostic full-event extraction**, the first real-input run of
    `extract_fullevent_fps.py`. Quarantined namespace, `NONQUOTABLE-DIAGNOSTIC` in every filename, and
    a manifest whose non-quotability is **proven, not asserted**: `require_quotable` recomputes the
    fold-forward deviation from the weights artifact (0.344577 vs FROZEN's 0.05, a 6.9x exceedance) and
    the builder launders a copy of its own manifest — publication schema and label, marker stripped —
    and dies rather than write if the gate accepts it. Flag-flipping, namespace-copying and renaming
    all fail to make it quotable.
  * `56525829` — **step-1 increment trajectory**, Joseph's top priority. The discriminator is
    iteration 0, where `weights_push == 1` and the ideal step-1 ratio's reco-weighted mean is exactly
    R: ~1.124 means step 1 starts correct and the iteration dynamics degrade it; ~0.65 means step 1 is
    broken before any feedback exists and the iteration story is a red herring. Disjoint code paths,
    which is what makes it worth a job. Read the engine first: `omnifold.py:189-200` confirms the
    target is `R/mean(push) = 1.1616`, `reweight()` is `w = exp(logit)` with label 1 = data so there
    is no inversion in the conversion, and `patience=10` inside `epochs=8` means `restore_best_weights`
    can never fire (consistent with BEN-043, not a second defect).

**Products:** `p3f-pet-gate4-launch-code-gate-20260809.json` (17 pins, validator re-pinned
`75a37217f208`, test `cdbce57d5b8b`). Bindings **ALL INTACT**, 120 resolved, 15 shell pins against
floor 15. Suite: `nd-unfolding/tests` **7 failed / 878 passed / 1 skipped** — the 7 documented
pre-existing path failures, unchanged. **Collection announced 970 -> 985** (+11 quarantine, +4
criterion).

## 2026-08-09 — NON-QUOTABLE full-event diagnostic attempt 1: reusable push, environment BLOCK

The real terminal event for Slurm job 56525297 was read and reconciled once. Accounting is FAILED
`1:0` after 14m06s. The expensive GPU stage nevertheless completed all 49,152,885 rows, wrote its
atomic push plus completion marker, pinned every one of 1,957 off-acceptance rows to one, and passed
the 2,000,000-row subsample-agreement check by a wide margin. Those bytes are preserved and reused.

The changed blocker is mechanical and exact: `sbatch_fullevent_diagnostic_extract.sh` invoked
`--stage all` under the TensorFlow module, although `extract_fullevent_fps.py` documents that push
needs TensorFlow/GPU and extraction needs PyROOT/CPU. The xsec stage died at `import ROOT`; no
quarantine manifest was written, so neither rejection boolean is yet confirmed and no completion
mail was sent. No cross-section number is quoted.

The committed repair is `pet/sbatch_fullevent_diagnostic_xsec_resume.sh`: it requires the completed
push job ID, preflights PyROOT in `root_6_28`, runs only `--stage xsec`, refuses output collisions,
then builds and independently asserts both publication-rejection booleans. Static and quarantine
tests pass 13/13. The original launcher remains untouched as provenance; an unchanged GPU retry is
prohibited. Receipt: `../docs/orchestration/state/diag-extract-56525297-failure-reconciliation.json`.
The repair was committed before compute, then submitted as CPU job 56527676 with terminal and
one-hour prestart queue watches. Its submission receipt is
`../docs/orchestration/state/diag-xsec-submit-56527676.json`.

## 2026-08-09 — NON-QUOTABLE diagnostic continuation COMPLETE, rejection proven

The terminal event for CPU job 56527676 was valid and read exactly once. One accounting read found
COMPLETED `0:0` on nid004116 in 1m32s. Stdout, stderr and the full run log were each read once; the
only stderr content was benign duplicate RooUnfold rootmap warnings. The job ran only the PyROOT
stage and reused the exact attempt-1 push path and SHA-256; no GPU recomputation occurred.

The read-only quarantine manifest was read once and independently checked. Its xsec hash matches the
artifact, its completion marker exists, both required publication-rejection booleans are true, and a
fresh recomputation rejects it on the physics alone. This is a successful diagnostic completion, not
a promoted result. No cross-section number is copied here or into the completion receipt.

The authorized completion mail command returned 0 for `josephrb@nersc.gov`; it contained the job and
gate status but no cross-section number. This records local mail acceptance, not an unverified claim
about downstream inbox delivery. Completion receipt:
`../docs/orchestration/state/diag-xsec-complete-56527676.json`.

Next dependency-ready action was executed: job 56525829 is still wholly prestart-pending on Priority,
so its terminal watch remains armed and a one-hour queue-latency watch now covers the batch-versus-
interactive routing decision. No duplicate writer was started.

## 2026-08-09 — Step-1 trajectory queue hedge: fresh A100 route selected

The real queue-latency event was read once and validated after 4,933 seconds of verified prestart
waiting. A single current snapshot still found batch job 56525829 PENDING on Priority and found none
of its JSON, run-log, stdout or stderr paths. The one live interactive allocation, 56525193
`gbdt-hold`, is a CPU-only GBDT-lane holder; it cannot run the A100 trajectory and was not disturbed.

The selected route is a fresh detached interactive A100 request, not a duplicate computation.
`pet/interactive_step1_trajectory_controller.sh` begins only after allocation, proves that allocation
is RUNNING with one GPU, locks against a second hedge, and then rechecks the exact batch and its
output paths. If the batch has started it exits in favour of the batch. If still pending, it cancels
only 56525829, requires terminal cancellation accounting, transfers watch ownership, and only then
runs the unchanged trajectory launcher in the allocation-ID namespace. Static safety tests and
shell syntax pass. Event receipt:
`../docs/orchestration/state/step1-queue-latency-56525829-reconciliation.json`.

The first detached request used `setsid` directly from the tool shell. Its reported PID vanished,
there was no named Slurm request, and its allocation log was empty; it did not persist and was not
rerun unchanged. The replacement supervision mechanism is a named OS-detached tmux session
`step1-ihedge-56525829`, proven live with pane PID 1456374. It owns the same committed salloc+
controller command. A file-sentinel watch covers the controller's terminal JSON and a 10-minute
deadline covers failure to acquire; the controller disarms that deadline as soon as allocation is
proven. The original batch remains the sole writer until then. Launch receipt:
`../docs/orchestration/state/step1-ihedge-launch-56525829.json`.

## 2026-08-09 — Step-1 interactive hedge missed its start deadline; batch retained

The real allocation-start deadline event was valid and read exactly once. One controller and
scheduler snapshot found no tmux session, no named `step1-ihedge-56525829` Slurm request, no route or
terminal receipt, and an empty tmux log. The proved pane PID from launch no longer exists as a live
controller. The interactive route therefore failed before allocation and never became a writer.

The same snapshot found original batch 56525829 still PENDING on Priority with zero runtime and no
product, stdout, stderr, or run log. There was no pending interactive request to cancel, and the
batch was not cancelled. It remains the sole writer. No replacement allocation or unchanged hedge
retry was launched. The batch terminal watch and controller-terminal file sentinel remain armed;
progress now depends on the batch terminal event. Receipt:
`../docs/orchestration/state/step1-ihedge-start-deadline-56525829-reconciliation.json`.

## 2026-08-09 — Step-1 trajectory COMPLETE: correct at iter0, degrades later

The terminal event for job 56525829 was valid and read exactly once. Accounting is COMPLETED `0:0`,
7m55s on one A100. Stdout, stderr, the complete run log, and the trajectory JSON were each read once
and hash-bound in the completion receipt. Stderr contains only a benign module version-change notice.
The submitted launcher and trajectory driver still match their committed hashes.

The artifact's `CORRECT_AT_ITER0_DEGRADES_LATER` verdict was independently recomputed. Iteration 0
achieves 1.233512 against exact R=1.124080 (1.09735x, correct sign); iteration 1 achieves 0.915166
against 1.028684 required and iteration 2 achieves 0.648331 against 1.161650, both wrong-signed. The
three decomposition anchors reproduce bit-exactly and cap saturation is zero throughout. History
minima show the step-1 checkpoints for iterations 0 and 1 are epoch 8/8, so their best-epoch files are
also last-epoch-faithful; iteration 2 uses the explicit BEN-043 final checkpoint.

The failure is therefore in post-feedback iteration dynamics, not a Step-1 normalization failure at
push=1. Code inspection further excludes stale cached labels/weights: the engine reuses feature
tensors and an index but rebuilds the current label/weight dataset every call. Fixed split/order and
warm-started model state remain distinct controlled hypotheses. Joseph's verdict mail was accepted by
the local MTA with rc=0. Branch C remains. Completion receipt:
`../docs/orchestration/state/step1-trajectory-complete-56525829.json`.

The next diagnostic was implemented without editing the shared hash-bound engine.
`pet/diagnose_step1_iteration_dynamics.py` subclasses it in-process and routes every arm through the
canonical full-input nominal driver and Gate-2/Gate-3 provenance checks. The completed nominal supplies
the warm/fixed baseline; a three-task array supplies warm/fresh, cold/fixed, and cold/fresh. Every task
owns an arm/job namespace and all code, target, receipt, and manifest inputs are pinned. The
predeclared repair definition is correct-sign iteration 2 with achieved/required >= 0.90. Six focused
tests, shell syntax, the canonical config gate, and all seven pins pass. Control plan:
`../docs/orchestration/state/step1-iteration-dynamics-control-plan.json`.

After a clean writer/capacity snapshot, the three controls were submitted as array `56531057`
(`0-2%3`). Batch is the deliberate placement: the experiment needs three independent A100s in
parallel and an 8h durable wall, while no interactive allocation existed. Every task was initially
PENDING on Priority with zero runtime and no output. Terminal and one-hour queue-latency watches are
armed; the orphaned sentinel for the failed 56525829 hedge was disarmed only after the original batch
completed. Submission receipt:
`../docs/orchestration/state/step1-dynamics-submit-56531057.json`.

A concurrent code audit then found that the engine's apparent post-iteration `1e-5` anneal is dead:
the trained clones are not reached by `CompileModels(fixed=True)` at `n_ensemble=1`, and `RunModel`
recompiles at full LR immediately before every fit anyway. The existing three-task array is already
committed and hash-pinned, so it was not edited in place. A separate `warm_fixed_annealed_lr` wrapper
forces only the fit-time compile at iterations 1/2 to `1e-5` for both steps, retains the warm model and
fixed split, and records all six actual optimizer rates. It passes four focused tests and eight pins;
the shared engine remains unchanged. Control plan:
`../docs/orchestration/state/step1-annealed-lr-control-plan.json`.

The annealed-LR control was committed at `0144d21` before submission, then launched as batch job
`56531204` on one A100/32 CPU with an 8h wall. Its job-owned namespace was absent before submission;
the initial scheduler snapshot was PENDING on Priority with zero runtime and no output. A terminal
watch and a one-hour prestart queue-latency watch are armed. The three-arm array `56531057` remains a
separate writer in its own namespaces. A combined mechanism verdict is deferred until both experiments
are independently reconciled. Submission receipt:
`../docs/orchestration/state/step1-annealed-lr-submit-56531204.json`.

The one-hour queue-latency event for array `56531057` was read exactly once and validated after 3813s
of verified prestart wait. One expanded snapshot found tasks 0/1/2 independently PENDING on Priority,
each at zero runtime, with all three output namespaces absent. No A100 interactive allocation,
detached controller, or tmux session existed. The closest full-input nominal (`56445883`) required
6h00m44s, which exceeds the four-hour interactive ceiling, and this experiment needs three independent
A100 arms. No replacement was therefore allocated or proven; no task was cancelled and batch remains
the sole writer. Its terminal watch and the independent `56531204` watches remain armed. Receipt:
`../docs/orchestration/state/step1-dynamics-queue-56531057-reconciliation.json`.

The independent queue-latency event for annealed-LR job `56531204` was likewise read exactly once and
validated after 3680s of verified prestart wait. The one exact-job snapshot found it PENDING on
Priority at zero runtime with its collision-isolated namespace absent. No A100 allocation, detached
controller, or tmux session existed. The same 6h00m44s full-input reference exceeds the four-hour
interactive ceiling, so no collision-safe replacement was available: the job was not cancelled and
batch remains its sole writer. The `56531204` terminal watch and separate array `56531057` terminal
watch remain armed. Receipt:
`../docs/orchestration/state/step1-annealed-lr-queue-56531204-reconciliation.json`.

## 2026-08-09 — Canonical standard 5D re-unfold `56495756` PUBLISHED, and its evidence closes

**Owed entry.** The re-unfold landed 2026-08-08 and this log did not record it; the only trace was
a fired wakerctl watch (`p4-std-receipts-56495756`). Recording it now, with every field below
taken from a command run in the same turn (`sacct`, the receipt JSONs, the evidence stdout) rather
than from memory.

**Job `56495756`** (holder job-name `gbdt-hold`, partition `urgent_milan_ss11`, 256 NCPUS).
Holder state **TIMEOUT at 03:00:05** — that is the 3 h interactive cap expiring on the *holder*,
not a failure: step `.0` **COMPLETED in 02:37:18** on 128 CPUs and published everything. Reading
the holder's state as the work's state is the misreading this note exists to prevent.

**Products.** Ten endpoint ROOTs and ten `.done` receipts in
`active_universe_5d/standard/unfolds/`. Each receipt carries `mode: produced` (never `attested`),
`bkg_mode: purity` with `bkg_mode_basis: "passed explicitly to the driver by this launcher"`,
`config_hash 4b41fab9…`, `code_rev 42268b6`, and the `unfold_blob` of the driver that ran.

**Evidence, re-run 2026-08-09 under job `56532439` at `7053f68`: EVIDENCE-COMPLETE.**

| | |
|---|---|
| OBS hashes `central5d` / `mask5d` / `central4d` / `mask4d` | 4/4 **MATCH** |
| reported bins | 5D 10 694, 4D 4 830 |
| endpoint reproduction vs the 07-18 reference | **10/10 within tolerance** |
| worst per-bin relative difference | **1.83e-11** (tol 1e-9, 54.6x margin) |
| worst integral relative difference | **2.87e-12** (tol 1e-11, 3.48x margin) |
| footing | `purity` on all ten, read from each endpoint's log |
| selection migration | nonzero on the four BeamAngle endpoints, exactly zero on the six others |

**The worst integral, 2.87e-12, would have FAILED the 1e-12 tolerance in force before 08-08.**
The widening was necessary rather than merely prudent, and it was the last one available — the
integral leg is a discriminator whose whole dynamic range is ~103x, so its margin is not slack.
Derivation and the pre-specified breach response are at `p4_lib.REPRO_RTOL_INTEGRAL`.

**What this does NOT authorize.** Stages 4-6 remain gated on a `standard-p4-verifier` PASS. The
candidate built today was produced by stepping around that gate under explicit instruction and
carries `publication_gate_rejects_this: true`; it is not a step toward adoption.

## 2026-08-09 — TEST COUNTS BEFORE 2026-08-09 ARE OVERSTATED FOR BOTH LANES. Read this before comparing any two.

`tests/test_p3f_pet_fullevent_launcher.py` executed `TEXT = open(LAUNCHER).read()` at MODULE
scope against a hardcoded `/pscratch` path. Off the cluster that raises during **collection**, and
pytest then aborts the **entire `nd-unfolding/tests/` directory** — not just that module. Fixed
2026-08-09 by excluding the module at collection level from `tests/conftest.py`.

**The fix did not only restore hygiene. It UNMASKED 7 real, pre-existing failures**, all
environment-dependent PET-lane tests (`test_fullevent_gate2.py` ×6 — `/pscratch` paths and
`ImportError: cannot import name 'DataLoader' from 'omnifold.dataloader'`; `test_gate2_target_runtime.py`
×1 — canonical NumPy DataLoader source missing). Those failures did not appear on 08-09. They had
been invisible for as long as the collection abort existed, because a directory that will not
collect reports nothing at all.

**Consequence for the record, and the reason this is its own entry:**

- Any off-cluster test count taken **before** 2026-08-09 counted only the modules that happened to
  collect before the abort, and is therefore **an undercount of the total and an overcount of the
  pass rate.** The post-fix numbers are 932 passing / 7 failing / 1 skipped.
- **Do not read the 7 as a regression.** Comparing a pre-fix count to a post-fix count will show
  failures appearing out of nowhere and tests appearing out of nowhere, and neither happened.
- This affects **both lanes**, not only the one that fixed it: the aborted collection took the
  GBDT/P4 suites down with the PET ones, and vice versa. A green report from either lane before
  this date is scoped to whatever collected.
- The general form: **a collection-time failure is not a test failure, it is a measurement
  outage.** A suite that cannot collect does not report red — it reports nothing, and nothing
  reads like fine. Judge suite health by collected count as well as pass count.

Cross-referenced from BEN-061, which covers the separate error made while fixing this (the first
attempt edited the PET module directly and drifted a sha256 frozen into a gate-3 receipt).

## 2026-08-09 — CANDIDATE built without a verifier PASS (deliberately). Stages 4-5 clean; stage 6 cannot pass.

Built under allocation `56532439` at code_rev `aa220b4` with `P4_NON_ADOPTABLE=1` and **no**
`P4_VERIFIER_PASS` — stages 4-6 invoked directly rather than through `run_p4_standard.sh`, by
explicit instruction, to find out whether those stages have defects of their own before another
provenance round. **This did not shorten the path to adoption and must not be read as progress
toward it.**

**Products** in `active_universe_5d/standard/candidate/` (scratch, purgeable):

| file | |
|---|---|
| `std_final5_candidate.root` | 42.3 GB; 45 bands, 40 retained; sqrt_tr_syst 4.3513e-38, sqrt_tr_full 4.3576e-38 |
| `std_component_manifest.json` | carries `publication_gate_rejects_this: true` + `adoption_requires` |
| `p4_standard_validation.json` | `RESULT PASS`, 11 gates, incl. `candidate_self_declares_non_adoptable` |
| `std_proj4d_candidate.root` | **not produced — stage 6 aborted** |

**Stage 4 clean.** Measured identities all at or below `4.6e-14` against a `1e-9` rtol.

**Stage 5 PASS**, and the self-declared rejection propagated into the receipt as a named gate, so
a downstream reader sees the refusal rather than only `result: PASS`.

**Stage 6 FAIL-CLOSED, on its first execution ever.** `projection mutates central (max rel
1.00e+00)`. That message is a mask: the `1.00` comes from 5 of 4830 4D bins that receive nothing
from the 5D support and carry **0.0000 %** of the 4D total. The real measurement, excluding them:

| | |
|---|---|
| median relative difference, marginal vs independent 4D | **4.43 %** |
| p90 / max | **20.8 % / 72.8 %** |
| bins over the 3 % tolerance | **3009 of 4825 (62 %)** |
| integral agreement | **1.005578** (0.56 %) |

Integrals agreeing to 0.56 % while bins disagree at a median of 4.4 % is a genuine shape
difference between two estimators, not a units or plumbing error.

**Escalated, not resolved.** The gate requires the 5D→4D marginal to reproduce the INDEPENDENT 4D
unfold per bin — which is the convention the campaign explicitly did **not** adopt on 2026-08-07
(4D *is* the marginal; the independent 4D is a cross-check). The gate predates that decision and
nothing forced the contradiction into the open while stages 4-6 were unreachable. **No tolerance
was touched and none will be**; a 3 % gate failing at a median of 4.4 % is not repaired by widening
it. Detail: `docs/orchestration/FINDING-20260809-stage6-central-gate-cannot-pass.md` (BEN-064).

Array `56531057` later emitted an error event, but not an aggregate-terminal one: tasks 0/1 failed
`1:0` after 25s/13s while task 2 remained pending. Each existing stdout/stderr and each result path was
read/checked once. Both failures occurred before training with `ModuleNotFoundError: No module named
'omnifold'`; all three result JSONs are absent. The launcher plus wrapper, driver, loader, engine,
target, target receipt, and Gate-3 manifest all match their committed hashes, so this is a launcher
environment defect and yields no scientific mechanism verdict. New r2 array and annealed-LR launchers
preserve every scientific pin, add `${REPO}/omnifold_nn` to `PYTHONPATH`, and fail closed on both
OmniFold imports before training. Shell syntax, three focused tests, and a live import probe pass.
Receipt: `../docs/orchestration/state/step1-dynamics-error-56531057.json`.

The changed repair was committed and pushed at `783e674` before any scheduler mutation. A fail-closed
check then confirmed old task `56531057_2` and sibling job `56531204` were still PENDING with no result;
both were cancelled without GPU runtime and their terminal watches disarmed. Replacement array
`56534116` and annealed-LR job `56534117` were submitted from the r2 launchers. All four new namespaces
were absent and all tasks were initially PENDING on Priority. Terminal and one-hour latency watches are
armed for both experiments. Joseph's mail explicitly reports no scientific verdict and the changed
repair; local MTA rc=0. Receipts:
`../docs/orchestration/state/step1-dynamics-r2-submit-56534116.json` and
`../docs/orchestration/state/step1-annealed-lr-r2-submit-56534117.json`.

The changed annealed-LR job `56534117` then crossed its one-hour prestart threshold. The wake event
was read once and matched the armed watch, job, and verified-prestart payload. A single scheduler and
ownership snapshot found the job still `PENDING (Priority)` at zero runtime, with its isolated
`slurm-56534117` namespace absent and no interactive A100 allocation. The measured full-input
reference `56445883` required 6h00m44s, longer than the four-hour interactive ceiling. No safe
replacement was allocated, so the batch job was retained as sole writer without cancellation or a
duplicate. Its terminal watch and corrected array `56534116` terminal watch remain armed. Receipt:
`../docs/orchestration/state/step1-annealed-lr-r2-queue-56534117-reconciliation.json`.

The changed factorial array `56534116` crossed the same one-hour prestart threshold. Its event was
read once and matched the armed watch, array ID, and verified-prestart payload. One expanded scheduler
and ownership snapshot found tasks 0-2 independently `PENDING (Priority)` at zero runtime, all three
isolated task namespaces absent, and no interactive A100 allocation. The experiment needs three A100
arms and the measured single-arm full-input reference took 6h00m44s, so no four-hour task-aware route
was safe or allocated. Batch remains the sole writer for every task; none was cancelled or duplicated.
The array and annealed-LR terminal watches remain armed. Receipt:
`../docs/orchestration/state/step1-dynamics-r2-queue-56534116-reconciliation.json`.

Changed array `56534116` later emitted one aggregate COMPLETE event: tasks 0-2 are each `COMPLETED
0:0`, with runtimes near three hours. The event, accounting snapshot, six task logs, and three
collision-isolated `STEP1_DYNAMICS.json` artifacts were each consumed once. Changed launcher commit
`783e674`, launcher hash, wrapper, driver, loader, shared engine, Gate-2 target and receipt, and Gate-3
manifest all match. The fail-closed import step necessarily passed before each COMPLETE wrapper run;
there is no import error, fail marker, or traceback, and every stdout ends with its arm-specific DONE
marker.

The frozen iteration-2 repair rule is correct sign plus achieved/required >=0.90. Warm/fresh fails
wrong-sign at 0.6636878; cold/fixed has the correct sign but fails at 0.7883825; cold/fresh fails
wrong-sign at 25.0654103. Therefore no factorial arm repairs: fixed split/order, Step-1 warm-start,
and their interaction are not sufficient standalone explanations. Receipt:
`../docs/orchestration/state/step1-dynamics-r2-complete-56534116.json`.

The same accounting snapshot found annealed-LR job `56534117` already `COMPLETED 0:0`; its armed
watch had not emitted. Its two logs and result were consumed once, all nine changed-launcher pins
match, and all six asserted fit rates are exactly the intended two `1e-4` iteration-0 fits followed
by four `1e-5` fits. Iteration 2 is nevertheless wrong-sign at 0.8958691, so the dead anneal does not
repair. The pending terminal watch was disarmed after this same-wave reconciliation to prevent a
duplicate wake. The combined verdict is intrinsic push feedback / representation-tail contraction;
Joseph's mail was accepted locally (`rc=0`). Branch C remains, with no threshold change, unchanged
retry, shared-engine edit, or publication promotion. Receipt:
`../docs/orchestration/state/step1-annealed-lr-r2-complete-56534117.json`.

A concurrent independent reading then exposed a specification conflict. The formal increment gate
above stands, but Gate-4's end-state normalization quantity gives annealed push `1.1109012` against
`R=1.1240802`: 1.172% low, inside the frozen 5%, versus the baseline's 34.46% deficit. The arm was
already 0.239% low after iteration 1, so its required iteration-2 correction is only `1.002396`;
scoring the next decrement as wrong-sign no longer distinguishes a poor end state. This does not
validate unfolded shape, and the arm's proposer declared a conflict of interest. No predeclaration
was overridden. A clarification mail with both readings was accepted locally (`rc=0`), and the choice
is escalated to Joseph with Branch C still closed.

## 2026-08-10 — Annealed powered-closure shape validation attempt 1 failed before training

Joseph selected the isolated annealed shape-validation option. The predeclaration and its two ranked
readings remain unchanged: the adopted `recovery >= 0.494582` criterion is primary and the assumed
`0.546853 +/- 0.02` comparison band is secondary. Job `56547490` reached `FAILED 1:0` after 81 seconds.
The frozen input hash, TensorFlow/OmniFold import, and training-independent protocol preflight all
passed; the latter emitted `PASS` with gap `0.2342704` and floor/gap `0.0458755`.

Training never started. The isolated `AnnealedMultiFold.__init__(*a, **kw)` wrapper masked the base
`MultiFold.__init__` signature, so the shared closure driver's fail-closed default lookup raised
`KeyError: 'early_stop'`. The recovery JSON, push artifact, quarantine manifest, weights, and anneal
LR proof are absent. Therefore this attempt supplies **no scientific verdict** and is neither evidence
for nor against the annealed arm. Joseph was mailed that number-free disposition (`rc=0`).

The changed repair is confined to the isolated wrapper and launcher: `functools.wraps` exposes the
base constructor contract, and the import preflight now asserts the inherited `early_stop=10` before
entering `srun`. Three login-safe regression tests, shell syntax, and a live TensorFlow/OmniFold
signature probe on interactive holder `56548506` pass. The shared engine and closure logic were not
edited; Branch C remains closed and neither threshold nor promotion status changed. Receipt:
`../docs/orchestration/state/annealed-shape-error-56547490.json`.

The repair commit `1ddc3f4` was pushed before scheduler mutation. Changed attempt `56552326` was then
submitted as one full-input A100 batch job with an eight-hour wall; the measured full-input reference
is approximately six hours, while the only live interactive holder is CPU-only and had less than
thirty minutes remaining. The job was initially `PENDING (Priority)` and its job-keyed report,
artifact, and manifest paths were all absent. Terminal and one-hour queue-latency watches are armed.
Receipt: `../docs/orchestration/state/annealed-shape-r2-submit-56552326.json`.

At the one-hour queue wake, the event's job, threshold, verified-prestart flag, and 3904-second wait
matched the armed watch. One expanded scheduler and ownership snapshot found `56552326` still
`PENDING (Priority)` at zero runtime. Its report, artifact, preflight receipt, quarantine manifest,
three logs, and weights namespace were all absent. No interactive allocation or detached A100
controller exists. Since the measured full-input reference is approximately 6h00m44s—longer than
the four-hour interactive ceiling—there is no proven alternative to receive ownership. Batch remains
the sole writer; it was not cancelled or duplicated, and its terminal watch remains the continuation
path. Receipt:
`../docs/orchestration/state/annealed-shape-r2-queue-56552326-reconciliation.json`.

Changed attempt `56552326` then completed all six fits and persisted its report, row/weight artifact,
preflight, histories, and fit-time LR proof, but Slurm recorded `FAILED 3:0`. The error is post-training
control flow: the shared closure driver still returns 3 against its explicitly retired absolute
`recovery >= 0.80` self-check, and the launcher's `set -e` stopped before its quarantine-manifest step.
No unchanged A100 retry is warranted.

Independent arithmetic on the four persisted 285-cell spectra gives gap `0.234270363`, floor/gap
`0.045875515`, residual `0.114182607`, and recovery **`0.512603276`**. The PRIMARY adopted criterion
passes (`>=0.494582400`, margin `+0.018020876`). The SECONDARY assumed baseline band rejects the arm:
recovery is `-0.034249724` below `0.546853`, outside `+/-0.02`. Per Amendment 1, PRIMARY decides and
the disagreement itself is the finding. The LR proof is exact: two iteration-0 fits at `1e-4`, then
four iteration-1/2 fits at `1e-5`. Joseph's verdict mail was accepted locally (`rc=0`).

This diagnostic does not authorize an engine edit, threshold change, promotion, or Branch C reopening.
A hash-pinned CPU-only finalizer will reuse the existing artifact to run the authoritative full-dump
re-derivation and create the missing dual-rejection quarantine manifest; it does not retrain. Receipt:
`../docs/orchestration/state/annealed-shape-r2-terminal-56552326.json`.
