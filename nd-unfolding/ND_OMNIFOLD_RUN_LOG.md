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

CPU finalizer `56562169` completed `0:0` in 41 seconds with empty stderr. It reused the committed
source report, artifact, preflight, and quarantine manifest without retraining or overwriting. The
authoritative Gate-4 powered-closure evaluator independently rebuilt all four spectra from the frozen
dump and persisted row/weight artifact: the largest difference from the reported spectra is
`5.898e-12` against the `1e-9` tolerance. Its 31 powered-closure checks and 47 total checks have zero
failures; all 14 exact hashes, the disjoint `2M+2M` split, Gate-2 identity, source digest, producer
receipt, and six fit-time LR records pass.

The final scientific reading is therefore fixed: PRIMARY PASS at recovery `0.512603276`, SECONDARY
TRADE-OFF/ARM-REJECTED at `-0.034249724` versus baseline, with criterion disagreement as the finding.
The dual quarantine rejection was recomputed and remains true. The isolated diagnostic still does not
authorize a shared-engine edit, threshold change, promotion, or Branch C reopening. Receipt:
`../docs/orchestration/state/annealed-shape-finalizer-complete-56562169.json`.

## 2026-08-10 — Annealed production nominal attempt 1 stopped at the canonical no-clobber guard

Job `56563092` exited `1:0` after 72 seconds. Its configuration and Gate-2 target-provenance gates
passed, including the adopted `seed_policy.lr_policy`, but the driver then found the completed
pre-anneal artifact at the canonical path and correctly refused to overwrite it. Training never
started: zero fits ran, `lr_policy_realized` and the fold-forward deviation do not exist, and the
predeclared reproduction test was not evaluated. This is operationally a failed launch and
scientifically null; it is not evidence that the anneal failed to take effect.

Before this reconciliation completed, a concurrent campaign lane committed the separate-directory
launcher and submitted changed job `56563761`. It is the sole writer to
`fullevent_nominal_annealed/`; every output and log was absent while it remained `PENDING (Priority)`
at 13:59Z. It does not use `--allow-overwrite`. It trains the nominal and a matched GPU-floor repeat,
which the predeclaration permits only as a scatter measurement with both values reported; it is not
powered-closure recovery. Recovery, extraction, cross section, and promotion remain out of scope.
The measured multi-hour A100 path does not fit the interactive wall, so the 12-hour batch route is
retained. Its terminal watch is armed. Receipts:
`../docs/orchestration/state/annealed-nominal-error-56563092.json` and
`../docs/orchestration/state/annealed-nominal-submit-56563761.json`.

Job `56563761` then completed `0:0` in 6h00m36s. Both atomically published artifacts and their
size/mtime-bound completion markers validate, and the canonical 2026-08-08 baseline remains at SHA-256
`58f664cdef266d09...`. Independent artifact arithmetic reproduces nominal deviation
`-0.035608971` and matched-floor deviation `-0.035482196`, both outside the frozen
`[-0.021724,-0.001724]` window. Their absolute scatter is only `0.000126775`; the nominal gap to
the expected `-0.011724` is `0.023884971`, or 188.4 times the measured same-path scatter.

Both artifacts independently record and verify two iteration-0 fits at `1e-4` and four later fits at
`1e-5`, with equal seed policies and realized-LR lists. The anneal therefore ran: the predeclared
verdict is **FINDING — code paths disagree**, not policy failure. No averaging, repeat, or band change
was made.

A bounded static postmortem found one important provenance distinction: diagnostic `56534117` used
driver SHA `66aa1f8f...`, while production used `5fda80df...`. The 105-line diff is confined to moving
the anneal into the production driver plus declared/realized LR telemetry and persistence; the shared
engine is byte-identical. The diagnostic wrapper calls `nominal.main`, so its loader is not an
independent implementation; its extra `cache`, `RunStep1`, and `RunStep2` methods wrap `super` for
telemetry. The production path is internally reproducible, but current evidence does not isolate
wrapper instrumentation/timing from another TensorFlow path effect. A new paired ablation would be a
new experiment and requires Joseph's choice. No recovery, extraction, cross section, promotion,
threshold change, or Branch C opening occurred. Receipt:
`../docs/orchestration/state/annealed-nominal-complete-56563761.json`.

## 2026-08-11 — Scalar-5D P4 Packet B channel test passed; real-cluster close remains pending

The unique timestamped artifact event `evt-p4-packetb-channel-test-20260811T1211Z` was consumed
once and validated against event HEAD `683bdcc`. It establishes a working BEN-067-safe delivery
path and durable implementations plus adversarial acceptance demonstrations for PB1 through PB5.
It does **not** establish a real-cluster PASS, a scoped verifier PASS, or adoption. PB5's exact
disposition is bounded-and-documented at the Phase-16 IBU verdict, not fixed.

A current-tree independent check ran 17 focused standard-library `unittest` cases: PB1's ten
required rejections plus accept-control, PB2's six-module producing-closure binding and legacy
grandfathering, the non-adoptable marker directions, endpoint reproduction discriminators, and
PB3's publish-after-blockers mechanism/order all pass. This corroborates the code/fixture layer;
the cluster layer remains separate.

Real-cluster execution is allocation `56636802`, step `56636802.0`, with one 128-CPU interactive
node. Its evidence stage reached `EVIDENCE-COMPLETE`: four central/mask bindings match and all ten
endpoints reproduce within the declared `1e-9` per-bin / `1e-11` integral tolerances. At
reconciliation, `STAGE56_START` was present while `STAGE56_END` was absent; the step was actively
reading the support family. It is the sole writer. The command sets `P4_NON_ADOPTABLE=1`, forbids a
nonempty `P4_VERIFIER_PASS`, and performs no adoption. Content-sentinel and allocation-terminal
watches cover completion. Only after independent terminal validation will the preserved
`standard-p4-verifier` UUID `019f74cb-b85d-7ba0-96c5-dfbd09e59159` receive a scoped follow-up via
`agentctl.py send`. Receipt:
`../docs/orchestration/state/p4-packetb-channel-test-20260811T1211Z.json`.

## 2026-08-11 — Packet B real-state run passed PB1/PB3/PB4; verifier blocked PB2 and repair landed

The completed file-sentinel event and `packetB_run.out` were each consumed once. Slurm step
`56636802.0` completed `0:0` in 17m43s (128 CPUs, max RSS 36,577,160 KB). The driver measured stages
5+6 at 17m00s; the invalid harness epoch stamps were discarded. The candidate, support family, and
projected ROOT independently match their bound hashes. PB1 closed 45 support bands as 40 retained +
5 active/replaced with 48 covariance keys. PB3 published exactly three consumable evidence files
with no pending/failed residue. PB4 binds component-manifest hash `a76904e3...` and carries
`publication_gate_rejects_this` inside the projected ROOT. No artifact was adopted.

The preserved standard verifier returned **BLOCK on PB2 only**: the six-module producing-closure
helper was correct but production never used it, so the endpoint writer recorded one blob and the
resume checker validated one blob. The exact Agent-A UUID was migrated from the expired legacy
school home to the corrected school home by a no-clobber, hash-verified session-store copy and an
atomic registry switch; its content-free heartbeat returned `AVAILABLE`.

Agent A then wired PB2 into production. Schema-2 endpoint receipts contain the derived six-path
committed-blob map; `p4_check_receipt.py` independently derives and requires the same map before
`SKIP`; and only the closed class with neither schema nor map is grandfathered. Real CLI/launcher
tests cover direct, transitive, omitted, unrelated, malformed-schema, legacy, and skip-reachability
directions. Root review tightened declared schema 1 to reject and reproduced **269 passed + 25
subtests**, plus clean shell/Python syntax and diff checks. The repair changes no ROOT, covariance,
physics, threshold, or scheduler state. Packet B remains pending the same verifier UUID on this
committed patch; the candidate and projection remain non-adoptable and publication-rejected.

Receipts: `../docs/orchestration/state/p4-packetb-stage56-56636802-reconciliation.json` and
`../docs/orchestration/runs/agent-A-standard/20260811T125432Z-packetB-pb2-repair.md`.

The committed `f67352f` re-review confirmed the production wiring but found one last presence bug:
`dict.get()` made explicit JSON null indistinguishable from an absent schema/record key. Three null
shapes inherited grandfathering and null schema beside a valid map passed outright. The same Agent-A
UUID changed the rule to key membership: only a receipt containing neither field is grandfathered;
every present null is malformed. Four real-CLI null negatives plus an absent-vs-null helper pair
were added. Root reproduced **274 passed + 29 subtests** and clean syntax/diff checks. This remains a
code-only repair pending the same verifier UUID. A separate open tool gap is recorded in OPEN_ITEMS:
the recorded-fields sweep misses unquoted shell JSON substitutions even though the two affected
fields are genuinely gated. Receipt:
`../docs/orchestration/state/p4-packetb-pb2-null-repair-20260811.json`.

The same verifier UUID then returned **PASS** on exact pushed commit `1440b58`. PB2 and overall
Packet B are closed. This is an implementation/real-state promotion gate only: the 5D candidate and
its projected product remain self-declared publication rejects under `P4_NON_ADOPTABLE=1`, and no
adoption is authorized or performed. The recorded-fields sweep extractor false negative remains a
separate owner-neutral tooling item. Final receipt:
`../docs/orchestration/state/p4-packetb-final-pass-20260811.json`.

The owner-neutral sweep defect was then closed without another provider dispatch. Shell JSON-key
harvesting now accepts any value representation after the colon, so the unquoted `%s` values used
for `receipt_schema` and `surface_blobs` can no longer disappear from the mechanical inventory. A
focused regression binds both fields to the production launcher; the guarded snapshot moves from
113 to 115 recorded-but-not-same-line-compared fields and retains 28 named gates. The proportional
P4 guard battery passed **172 tests + 31 subtests**. This changes only audit coverage: the receipt
gate, ROOT products, physics, thresholds, and non-adoptable state are unchanged. Receipt:
`../docs/orchestration/state/p4-packetb-sweep-extractor-fix-20260811.json`.

## 2026-08-11 — discharge criteria for quarantine causes 1, 2, 3, 4, 6 (Session B, uncertainty construction)

No compute. Criteria written before remediation, per instruction, and nothing is discharged by writing
them. `../docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`.

**The framing, which is why no criterion existed.** The 2026-07-12 quarantine says the old products
*"used one or more of"* seven causes — a statement about a **class**, and a class has no construction, so
there was no subject a criterion could be about. Discharge is therefore defined per **(cause × artifact)**
pair, with four legs, all required: **C**ode (defect-free path at a pinned revision), **P**rovenance (the
artifact is provably that path's output, not merely contemporaneous — BEN-083), **M**agnitude (the
defective-vs-corrected difference measured on the artifact's *own* inputs), **T**est (power-tested both
directions; presence as well as absence). M is the leg that makes discharge falsifiable: without it,
*"fixed and it did not matter"* and *"fixed and never run"* are indistinguishable in every document.

**Honest state for the artifact the four `\gbdtFive*` macros quote** — the adopted 5D GBDT covariance,
10,694 reported bins of `GRID_NBINS = 65856`:

| cause | C | P | M | T | verdict |
|---|---|---|---|---|---|
| 1 one-sided endpoint interpolation | OPEN | OPEN | OPEN | OPEN | OPEN |
| 2 CV centering | MET | OPEN | **MET** (F7 predeclared; 4.69× → 4.83× the sampling floor) | OPEN | OPEN, nearest |
| 3 varying estimator seeds | MET | OPEN | UNRESOLVED | OPEN | OPEN |
| 4 scalar jitter subtraction | MET | OPEN | UNRESOLVED | OPEN | OPEN |
| 6 incomplete statistical projection | OPEN | OPEN | OPEN | OPEN | OPEN, furthest |

Recommended remediation order, cheapest first: **2 → 4 → 3 → 1 → 6**. Cause 6 is on the critical path for
two deliverables at once, since its `(E_avail,W)` leg also gates the generator ratios.

**Six findings, `BEN-100`–`BEN-105`.** Two bear on numbers proposed for the paper. (a) The J28 replacement
pair `5.2600e-38`/`5.6609e-38` is footed on the **non**-background-aware sweep (`4.3455e-38`, median
`13.432%`), while the values it would replace, `5.81e-38`/`6.24e-38`, are **background-aware**
(`4.3578e-38`, median `13.359%` = `\gbdtFiveBlockMedian` `13.36`): `sbatch_j28_adopt_5d.sh` never passes
`--combined` and `adopt_unified_5d.py:76-77` defaults to the non-bkgaware product, so the two pairs differ
in **two** inputs, not one. Found by failing to derive `13.36` from `13.43` — BEN-077's heuristic. Footing
choice left **UNRESOLVED**; `values.tex` untouched. (b) No committed artifact can prove the construction
contract for that covariance at all: the seed, null norm and centering convention live only in the
`.gitignore`d ROOT, so the provenance leg of four causes is unsatisfiable from the repository. **The
highest-leverage single item found is a receipt, not a re-run.**

**Repairs landed in this commit, all documentation.** Five citations of the F7 predeclared criterion
retargeted from line numbers to quoted content (`CORRECTED_UQ_PRODUCTION_STATUS.md` is prepend-ordered;
the rule drifted `66 → 73 → 84 → 98 → 108 → 112` while four documents kept citing `:73-78`, and a second
citation had drifted `325 → 364`), plus a header on that file saying why. `INTEGRATION_CHECKLIST.md`'s
GATED list re-verified row by row: the binding gate was **absent from it entirely** and is now its first
row; the genuinely stale row (`χ²/ndf 1.699` reconcile, done 2026-07-16) is struck with its evidence; the
FPS row's decayed *reason* is corrected while its verdict stands; and **the row this session was told to
strike as stale is live and was strengthened instead** — `#16` is OPEN and `ESTIMATOR_REGISTRY.md:29`
attaches it to `omnifold-5d-lgbm`, so striking it would have deleted the live publication gate on the very
product this lane is unblocking (BEN-100). `sbatch_j28_adopt_5d.sh` deliberately left byte-unchanged
despite a BEN-026 `| tail -25` at `:109,111`, so it stays faithful to the run it documents (BEN-104).

Nothing adopted, nothing re-run, no ROOT written, `values.tex` untouched. Routed to Session A for review
before remediation begins.

## 2026-08-11 — criteria APPROVED; per-artifact column on the seven causes; two corrections (Session B)

No compute. Follow-up to `a8ab03e` after the orchestrator approved the four-leg criteria unmodified and
accepted the remediation order 2 → 4 → 3 → 1 → 6.

**The seven-cause list at `VALIDATION_LEDGER.md:65-88` now carries the artifact per row**, and the
DISCHARGED row names the FPS product (266 reported bins) in the row itself. Assigned after this lane
declined an instruction to strike `INTEGRATION_CHECKLIST.md`'s 5D-lateral row as stale: that row is live,
`#16` is OPEN, and `ESTIMATOR_REGISTRY.md:29` attaches it to `omnifold-5d-lgbm` — the 5D GBDT covariance,
10,694 of 65,856 bins, whose P4-5D lateral has not been built. The discriminator is a number neither
description contains: **266 ≠ 10694**. No status changed; the table names the subject each status was
always about, and records that for the artifact the four `\gbdtFive*` macros quote the count is **zero of
seven, not one of seven** (BEN-100). The GBDT lane having exited, the ledger row came here rather than
being routed.

**`PROCEDURE-gbdtFive-macro-update.md` §2 corrected — its conclusion was wrong and its search was right.**
§2 searched `sec_systematics.tex:158-172` for `from / summary / rollup / artifact / ledger / taken / \ref`,
correctly found none, and concluded *"no source claim can be silently re-pointed."* But `:162` reads *"the
**background-aware** block sum has median per-bin uncertainty `\gbdtFiveBlockMedian`"* — an attribution to a
**sample and a footing** rather than to a file, invisible to any filename-shaped search and every bit as
falsifiable by a value swap. Writing the non-bkgaware J28 pair under it would make the sentence false:
BEN-087's trap reached by a carrier §2 was not looking for. §4's `\gbdtFiveBlockMedian` row is upgraded from
*"not established as the same quantity"* to **established as a different one** — `13.36` is the bkgaware
median `13.359%`, `13.43%` is the same quantity non-bkgaware — so it is **not** a fourth macro that holds
while three change. The rule: an attribution sweep must cover populations, footings and samples, because
those are written with ordinary adjectives (*background-aware*, *selection-complete*, *full-event*,
*recoil-only*, *five-band*) rather than with citation verbs. BEN-102.

**BEN-105's attribution corrected before the row was two hours old, and the correction belongs in the
record.** It first said the orchestrator filed `BEN-089`, on no evidence beyond it being the only other
session known to be writing findings — an unsourced attribution in the row complaining about carelessness,
which is BEN-082's shape. Measured instead:
`git log origin/main -S'BEN-089' --format='%H %s' -- docs/orchestration/FINDINGS.md` returns **`2b50c3f`**,
the PET-scoped session on an older standing brief, since exited — so the correction routes to **C - PET**,
and as first written the row would have sent the next reader to a session that cannot act. Also recorded:
the verifier was assigned `090-099` from the bottom while this lane opened `100+` with `089-099` as a
buffer, both within ten minutes and from the same enumeration. Nothing collided, and it did not collide
because of a buffer one lane left and another filled upward into — **fourth instance, and luck with a good
outcome is not a working process.**

Nothing adopted, no ROOT written, `values.tex` untouched.

## 2026-08-11 — cause 5's binding half determined; construction defect sized; two jobs launched (Session C, PET)

**Determination.** `VALIDATION_LEDGER.md:83-84` quarantines the recoil-PET budget pending *a joint
nuisance--retraining construction* AND *selection-complete detector samples*. Asked which is binding.
**Answer: the joint construction. The samples already exist and have since 2026-07-20.**

Measured this session, all from commands rather than from status text:
`nd-unfolding/p3f_pet_fullevent/final/` holds **120 ROOT + 120 receipt, 1.1 TB**, all **120 receipts
`PASS`** (every file parsed, not sampled), inventory 5 band x 2 endpoint x 12 playlist exactly matched,
schema `g2-fullevent-v1` (binary sha `61d7dfbf` from `486e53e`, `MNV101_DUMP_POINTCLOUD=1` +
`MNV101_FULL_PHASE_SPACE=1`, i.e. full-event and not recoil), promoted **`GATE3_PROMOTED_PASS`
2026-07-20T23:58:00Z** with `expected_tasks 120 / reconciled_tasks 120 / errors []`.

**The trap this sat on.** `KNOWN_ISSUES.md` #19's true *"no full-event FPS RESULT exists"* has been read
downstream as *"no full-event anything exists"*. Inputs and products are different objects, and the
conflation mis-sizes the remaining work by a 120-endpoint C++ event-loop dump.

**Construction defect sized (new).** The joint object does not exist and what does exist is the defect:
`C_syst` + `C_retrain` keeps `outer(s,s) + outer(Delta,Delta)` and drops both cross terms.
Measured on the six committed Phase-7 response arrays by
`pet/measure_joint_vs_additive_nuisance_retrain.py`, receipt
`products/pet/bkgsub/pet_joint_vs_additive_retrain.json`: the cross term is **negative in every
universe**, and on the five knob endpoint-universes the additive construction gives sqrt-trace
`3.093207e-38` against the joint `1.731571e-38` -- **overstating by 1.786x**, realized per-universe
range 1.086-2.928. Identity `||delta||^2 == ||s||^2+||Delta||^2+2 s.Delta` verified to 5.144e-15;
reproduces Phase 7's separately recorded `corr = -0.71` as cos -0.714 / Pearson -0.711; tool
power-tested in all four directions. RECOIL products, so no magnitude is quotable and none transfers --
what transfers is the sign and size of the omitted term.

**Jobs launched.**
- **56691812** `fe_traj_ann` (`pet/sbatch_step1_trajectory_annealed.sh`, qos=shared, 1 GPU, -t 4:00:00)
  -- does the Branch C iteration-dynamics defect survive the LR anneal? Two arms: ARM 1 is a positive
  control re-running the pre-anneal trajectory against the **committed** `56445883` decomposition
  receipt, and if it does not reproduce, ARM 2 is not read at all; ARM 2 is the full three-stage chain on
  the annealed nominal `56563761`. No training -- saved per-iteration checkpoints only. Predeclared
  three-branch at `831043d`, `docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md`,
  with UNRESOLVED flagged as the **most likely** single outcome because the annealed arm sits near
  `push ~ R` where `|required-1| < 0.02` makes the sign criterion return no information.
  Watch `branchC-traj-annealed-56691812` armed.
- **56692312** `hpss_p3f_fe` (`pet/sbatch_hpss_protect_p3f_fullevent.sh`, qos=xfer, -t 12:00:00) --
  `hsi ls` returned only `~/backups`, so 1.1 TB of Gate-3-promoted input was the SOLE copy on purgeable
  scratch, the same exposure that already cost nine throw slabs (`docs/OPEN_ITEMS.md` item (g)).
  Verification is by **digest**: local md5 against an md5 computed SERVER-SIDE by `hsi hashcreate`, so
  content is checked without reading 1.1 TB back. Completion condition
  `n_archived_digest_verified == 240` (120 ROOT + 120 receipt), not 120. Resume guard is digest-based per
  BEN-023. Watch `hpss-protect-p3f-56692312` armed.

**`INTEGRATION_CHECKLIST.md` -- two PET rows corrected.** The full-event row's verdict stands with its
reason sharpened (product vs input). The **PET 100-replica `C_stat`** row had been readable as *"the note
quotes `C_stat` as if it had 100 replicas"*; checked and it does not -- `7.439e-39` appears in **zero**
`.tex` files, and `sec_pet.tex:110-112` already states *"based on 20 coherent replicas ... more limited
than the 100-replica target"*. So the claim needing change was the checklist row, not the note, and
producing the 100 is recorded as **not scheduled** with its reason rather than silently dropped: 80 more
full-PET-retrain GPU jobs to sharpen a number that is unquoted, inside the quarantined recoil `C_total`,
and belonging to a superseded estimator -- while the note independently requires a **fresh** statistical
ensemble for the full-event replacement.

**Nothing discharged.** Cause 5 remains OPEN; six of seven quarantine causes remain open; no PET
magnitude became quotable; Branch C not lifted; the annealed nominal NOT promoted (held pending Joseph's
sequencing answer, `docs/orchestration/AUTHORIZATION-20260811-annealed-promotion-and-hpss.md`).

## 2026-08-11 — construction-contract receipt; the footing mismatch proven from the products (Session B)

Read-only cluster read, no compute, nothing adopted, `values.tex` untouched. Script
`receipt_construction_contract_5d.py`, receipt `uq_5d/receipt_construction_contract_5d.json` (67 KB), log
`uq_5d/receipt_construction_contract_5d.log` (whole stream, no `tail`). Predeclared at
`../docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md`; **verdict B1** on the
artifacts the branch set named.

**Stamps, both throw ROOTs.** `fixed_seed_null_norm` **present** — `1.9706093906025077e-50` pre-J28,
`5.8223488501140625e-50` J28-corrected, tol `1e-12`; `n_throws` `160` both; `joint_mean_shift_norm`
`1.654393237996853e-38` and `1.878696733368378e-38`, the latter matching the ledger digit for digit;
`hJointMeanShift` a **separate** `TH1D[10694]` on both. Slab census: **one estimator seed, `1000`**, over 40
throw and 36 block slabs, 160-throw union contiguous. Present-not-absent is the criterion, because
`unified_throw_cov.py:482-483` writes the null key only under `--null`.

**The footing mismatch is proven FROM THE PRODUCTS.** `adopt_unified_5d.py:166` stamps `sqrt_tr_old` = the
√Tr of the `--combined` it was given, so each adopted product records its own footing: `\gbdtFiveAdoptTrace`
and `\gbdtFiveCVTrace` carry **`4.357790406860002e-38` (bkgaware)**; the proposed `5.2600e-38` / `5.6609e-38`
and the July `5.802415620046235e-38` all carry **`4.345454363683128e-38` (non-bkgaware)**. No launcher
reading required. Three of four cells of a 2 × 2 in (footing × J28) already existed, so the effects separate:

    block-sum footing effect                                              +0.2839%
    ADOPTED mean-centered footing effect, pre-J28 (5.802416 -> 5.807716)  +0.0914%
    J28 effect, FOOTING-MATCHED (both non-bkgaware)                       -9.3486%
    J28 effect computed across footings, as PROCEDURE §4 had it           -9.4313%

**`sec_systematics.tex:170-173`'s `0.30%` is the BLOCK-SUM figure (exactly `+0.2839%`); the effect on the
ADOPTED covariance is `+0.0914%`** — the per-bin `max()` inflation transfer damps it ~3×. Applying the
note's `0.30%` to an adopted scale overstates the footing effect threefold.

**Job `56693207`** (`sbatch_readopt_5d_bkgaware_footing.sh`, `--qos=shared`, 6 h wall, submitted
2026-08-11T22:50Z, PENDING/Priority at submission, watch `readopt-footing-56693207` armed and confirmed)
fills the empty cell: four arms from one unchanged throw ROOT, **controls first** — C1/C2 must reproduce
`5.2600e-38`/`5.6609e-38` or branch **B3** says the diagnosis is unsafe — and A1 tested against the
**pre-registered** no-interaction value **`5.264776e-38`**. Predeclaration:
`../docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md`. Fail-closed input gate checks all
13 `VERT_BANDS` on **both** footings before doing work, so B4 is excluded up front. Nothing is re-thrown or
re-combined; no `tail`/`head` anywhere; `--out` explicit on all four arms.

**Two findings, and both are against my own work.** BEN-106: every contract stamp is **absent from every
adopted product** — `adopt_unified_5d.py:166-167` writes only the two traces — so the artifact that would be
*published* cannot prove its own contract, and causes 2/3/4 are provable for the throw ROOT and not for the
covariance the note quotes. BEN-107: my branch set was quantified over **one** artifact where the chain has
two hops, so *"present upstream, absent downstream"* was expressible by none of its four branches;
separately, two predeclared paths were wrong because I hand-expanded `TAG` and dropped a suffix, which made
the first probe report the products ABSENT — the UNRESOLVED branch that a typo impersonates on purgeable
storage. **BEN-104's harm is refuted while its mechanism stands:** read whole, the truncated adopt log did
contain every ingredient, with ~7 lines of margin out of 25, nine of which are `RooUnfold` warnings.

Causes 3 and 4 now need only their test legs; cause 2 only its guard. **Zero of seven discharged.**

## 2026-08-11 — (E_avail,W) GiBUU corner ratio recovered; all four recomputed together (Session B)

Seconds of login-node compute, read-only inputs. Log (whole stream, no `tail`)
`../3d-unfolding/genie/eavailW_band_20260811_allfour.log`, 2,498 bytes; outputs written to **dated**
names so the note's current `eavailW_band.{png,root}` are untouched. Predeclared at
`../docs/orchestration/PREDECLARE-20260811-gibuu-corner-ratio.md`; **branch G1** — and I had
pre-registered **G2** as most likely, so the prediction was wrong in the reassuring direction.

**Not gated by the quarantine, and structurally so:** `data/gen` here is a ratio of two central-value
corner integrals over 3×3 = 9 cells (`overlay_eavailW_band.py:88-108`) with **no covariance in it**. The
covariance-dependent **significances** stay gated. The checklist row bundled the two in one line; it is
now split, because the easy error runs both ways — treating the ratio as blocked, or reading the ratio's
closure as unblocking the significance.

    generator    corner integral   data/gen   note had   integrated sigma
    GENIE-CV       8.7918e-39       1.535       1.54        2.4446e-38
    GENIE+MEC      8.5484e-39       1.579       1.58        2.4829e-38
    NuWro          8.6369e-39       1.563       1.56        2.3444e-38
    GiBUU          8.3893e-39       1.609    UNCOMPUTED     2.2227e-38
    data           1.3497e-38         --         --         3.0699e-38

**GiBUU lands outside 1.54–1.58**, so per that paragraph's own predeclared rule (*"widen the span only if
it lands outside"*) `sec_eavailw.tex` moves to **54–61%** / band **1.54–1.61**, and its `W∈[2.2,3.0)`
sentence extends from three generators at 23–25% to four at **23–26%** (GiBUU 25.81% below data).

**Why it was uncomputed, measured:** `gibuu_cv_xsec_eavailW.root` is dated **2026-06-09**, one day *after*
the 2026-06-08 three-generator run — the input did not exist yet — and `overlay_eavailW_band.py:97-98`
**fails open** on a missing `--gen` (`print MISSING`, `continue`), so the script could always emit a
complete-looking three-generator table with the fourth reduced to one line.

**The three reproduce at the note's printed precision; identity is NOT established.** The only surviving
record of the 2026-06-08 values is `ND_OMNIFOLD_RUN_LOG.md:988-990` at three significant figures, and the
data file `products/5d/excess_eavail_W.root` (**2026-07-14**) postdates them by five weeks, so a
third-decimal shift is masked by rounding (BEN-086). That is why all four were recomputed **together**
rather than GiBUU being appended to three older numbers — the same defect as the `\gbdtFive*` footing
mismatch, avoided by predeclaring it.

**Controls reproducing exactly**, which is what makes the set trustworthy: GiBUU integrated `2.2227e-38`
and data `3.0699e-38` against the paragraph's own `2.22`/`3.07` and `values.tex \sigData`; and
`sec_3d.tex:151`'s ordering GiBUU < NuWro < GENIE CV at `2.2227e-38 < 2.3444e-38 < 2.4446e-38`.

**A normalization inconsistency found while closing this, ROUTED not changed.** `sec_eavailw.tex` gives
two deficits two sentences apart in two normalizations, each rendered as a bare percentage: *"underpredict
… by 54–61%"* is **generator**-relative (`data/gen − 1`); *"sit 23–26% below the data"* is **data**-relative
(`1 − gen/data`). Each is right by its own arithmetic. In a common normalization the corner deficit is
**34.9–37.8%** data-relative (or high-W is **29.8–33.6%** generator-relative), so `54–61` against `23–26`
reads as a ~2.4× contrast where the consistent answer is ~1.5×. The convention is an authorial choice about
a physics claim, so it is recorded in the `.tex` comment block and routed rather than resolved here.

## 2026-08-11 — Branch C annealed trajectory interactive twin failed before its control; batch retained

The external event for interactive allocation `56693776` was consumed once. Accounting records
`FAILED 0:15` after 35 seconds on four A100s/128 CPUs. Its sole run log contains the banner and Python
executable four times: a bare `srun` inherited four tasks. Three ranks raised `IndexError` while mapping
`hvd.local_rank()` to their visible GPU list; one rank completed the import/hash preflight and printed
the start of ARM 1 before the step received SIGTERM. No control trajectory, Gate-A/B, decomposition, or
annealed trajectory JSON with the `56693776` suffix exists.

Therefore **no scientific branch is read**: ARM 1 did not produce its committed-anchor reproduction,
so ARM 2 is not read regardless of partial log text. The separately submitted one-task batch twin
`56691812` had started on one A100 and is the sole valid route in a collision-isolated job namespace;
its terminal watch remains armed. There is no interactive retry. The launcher now fails with exit 64
before TensorFlow import or output setup when `SLURM_STEP_NUM_TASKS`/`SLURM_NTASKS` is not one, with two
focused tests. The running batch was launched from the exact pre-repair launcher committed with the
predeclaration at `831043d`; the repair changes only future route fail-closure.

Receipts: `../docs/orchestration/state/branchc-traj-annealed-srun-error-56693776.json` and
`../docs/orchestration/state/branchc-traj-annealed-batch-active-56691812.json`.
## 2026-08-11 — wakerctl.scan() per-watch guard, power-tested in four directions (Session B)

No compute. Closes the `scan()` single point of failure filed in `../KNOWN_ISSUES.md` and assigned by the
orchestrator. **Diagnosis confirmed rather than inherited:** `evaluate()` at `:606` unguarded,
`_write_tick_receipt` at `:616` after the loop, `tick()` calling `scan()` at `:1101` unguarded — and
`evaluate()` **ends with an explicit `raise WakerError(f"unknown watch kind: {kind}")`**, so the likeliest
malformation from a schema change aborts the loop by design, not by accident.

**One refinement that changed the test.** `load_watches()` already wraps `read_json` in
`contextlib.suppress(OSError, json.JSONDecodeError)`, so a **corrupt** watch file is skipped and harms
nothing — a fixture writing garbage bytes would have **passed against the unfixed code**. The dangerous
watch is valid JSON with bad content. That is what the test arms.

**Fix.** Per-watch `try/except` around `evaluate` + `emit_event` + `save_watch`; ledger
`watch-evaluate-error`; bump the existing `unreliable` counter; both writes individually guarded so nothing
in the per-watch path can abort the tick, including the code recording that it failed. `last-tick.json`
gains `watch_errors`, **written unconditionally** so `0` differs from written-by-an-older-version, plus
`watch_error_detail` when non-empty. Existing readers unaffected — `wakerctl.py:1182` and the liveness rule
both read `at_utc`.

**Two things I did NOT do, both deliberate and one against instruction.** The watch is **not disarmed**: an
exception here need not be permanent, and retiring a watch on one bad tick is the same fail-open-into-silence
the guard exists to end. And `tick()`'s call to `scan()` is left **unguarded** — wrapping it would let the
tick receipt survive a *total* `scan()` failure, and since `last-tick.json` is the liveness signal a broken
waker would then read as HEALTHY, manufacturing BEN-084's *"artifact asserting a state it cannot have"* while
fixing another defect. Stated to the orchestrator with the reasoning rather than done quietly.

**POWER-TESTED IN FOUR DIRECTIONS.** `ScanPerWatchIsolationTests`, 7 tests, all pass. The suite carries the
**pre-fix `scan()` body inline as a live positive control**, asserting the scenario raises *and* skips the
receipt *and* never reaches the valid watch. Ids are `aaa-broken` / `zzz-valid` because `load_watches()`
iterates `sorted(glob)` and with the order reversed every assertion would pass against the unguarded source.
Mutations: **M1** remove the guard → 5 of 7 fail; **M2** drop `watch_errors` → 3 fail; **M3** write
`watch_errors` only when non-zero (the null-as-absent shape) → **exactly one test fails, the presence
assertion, and nothing else notices.** M3 is the one that matters: it is the refactor a reasonable
maintainer makes next month, and one line is holding it. BEN-108.

**No regression.** `test_wakerctl.py` 17 failed / 37 passed against 17 / 30 before — same 17 pre-existing
failures, +7 passes. Whole `docs/orchestration` 20 / 86 against the 20 / 79 recorded 2026-08-02: identical
failure set.

**⚠ The new test is NOT collected by the project test command, and I am not silently fixing that.** The
command is `pytest nd-unfolding/tests`; there is no `pytest.ini` / `setup.cfg` / `testpaths`, so
`docs/orchestration`'s **106** tests are in no baseline and **20 have been red since at least 2026-07-20**
(`../docs/orchestration/FINDING-20260802-orchestration-tests-never-run.md`, re-measured today). Widening
collection changes the announced baseline for every lane and imports 20 red tests into it, so it is a shared
decision and is **routed, not taken.** Counts in BEN-079 form: `pytest nd-unfolding/tests` = **1008**,
`pytest docs/orchestration` = **106**, both on the **local Mac checkout** @ `8c99e36` — not comparable with
cluster counts.

Unrelated to and not touching `p3f-pet-gate3-queue-latency-reconciliation-56169838.json`, which is Session
C's to dispose of; the pin's lapse is C's finding and I relied on my own reading of the code, not on it.

## 2026-08-11 — TEST legs for quarantine causes 1, 2, 3, 4; and the F7 ratio corrected (Session B)

No compute. Remediation in the orchestrator-approved order 2 → 4 → 3 → 1. Ten tests in
`tests/test_uq_remediation.py::QuarantineCauseGuardTests`, **28/28 pass** in that file. Two small code
additions, both additive and neither touching an existing caller.

**Cause 4's null-as-absent gap, closed at the source.** `unified_throw_cov.py` wrote
`fixed_seed_null_norm` **only** when `--null` was passed, so a product built without it carries no null
key at all and a criterion phrased *"the null norm is not large"* passes on it **vacuously**. Now
`fixed_seed_null_checked` is written **unconditionally** beside it, in both the ROOT and the returned
dict. The norm itself is still written only when measured — **a number nobody measured must not be
invented as `0.0`** — so "checked and zero" and "not checked" are now distinct readable states.

**Cause 2's F7 rule, codified as a predicate.** `uq_math.mean_shift_sampling_floor`,
`mean_shift_over_floor`, `f7_cv_centered_required`, with `F7_FLOOR_MULTIPLE = 2.0`. The threshold is a
**codification, not a repo decision** — the predeclared rule is qualitative and no number was recorded —
placed so a shift *at* the floor is unambiguously below and the measured ratios unambiguously above, and
deliberately not tuned to sit just under the measured value. One test pins the boundary explicitly so
changing it fails a test that names it.

**AND THE F7 NUMBER ITSELF IS WRONG — found while writing its test.** See the ledger entry
"2026-08-11 F7 mean-shift ratio on the ADOPTED ensemble". `4.6912×` reproduces the recorded `4.69×`
exactly; `4.83×` turns out to be the **122-throw** morning re-roll (`4.8288×`), not the adopted 160. The
like-for-like post-J28 value is **`5.3478×`**. The ledger's own subsample warning sat twelve lines away
and was never applied to this ratio. **No verdict moves** — `5.35 > 4.83 > 2.0`, mean-centered-only stays
disqualified, more strongly — which is precisely why it survived: a wrong number pointing the same way as
the right one is invisible to anyone checking the conclusion. Third instance of the class this session,
now named: **BEN-109**.

**POWER-TESTED, SIX MUTATIONS, files restored byte-exact (md5 verified before and after).**

    N1  mat_covariance CV-centers instead of mean-centering   -> 1 fail (cause 1)
    N2  mat_covariance renamed away                           -> 6 fail, incl. the PRESENCE test
    N3  f7_cv_centered_required always False                  -> 2 fail (cause 2)
    N4  F7_FLOOR_MULTIPLE moved to 10.0, above the measured   -> 2 fail, incl. the boundary pin
    N5  mixed-seed rejection made unreachable                 -> 1 fail (cause 3)
    N6  fixed_seed_null_checked reverted to conditional       -> 1 fail, the PRESENCE assertion ONLY

**N6 repeats the wakerctl result exactly: the null-as-absent revert is caught by one test and nothing
else.** Two independent instances in one session where a presence assertion is the sole guard against
*"only write it when there's something to report"* — the refactor a reasonable maintainer makes next
month. BEN-108.

Cause 3's test asserts **both** directions in one case — one seed ACCEPTED, mixed seeds REJECTED —
because rejection alone would also pass for a guard that rejects everything.

**Suite state, and two red tests that are NOT mine.** `pytest nd-unfolding/tests` = **1018 collected**,
9 failed / 1008 passed / 1 skipped on the **local Mac checkout**; 7 are the known off-Perlmutter
ImportError/`/pscratch` failures. The other two are accounted for exactly and belong elsewhere:
- `test_p4_sweep_snapshots` **340 != 337** — three `.sh` files added since the snapshot commit
  (`76a62f8`), enumerated by `git diff --diff-filter=A`: `pet/sbatch_hpss_protect_p3f_fullevent.sh`,
  `pet/sbatch_step1_trajectory_annealed.sh` (both PET) and `sbatch_readopt_5d_bkgaware_footing.sh`
  (mine). `337 + 3 = 340`, no unexplained file. **Not updated here** — the snapshot is a P4-lane artifact
  and two of the three additions are another lane's to confirm; blessing them because I ran the suite
  last is the "who authorized this" problem. Routed.
- `test_resume_guard::test_no_shell_file_reintroduces_a_size_only_resume_guard` — a **false positive on a
  COMMENT**: it matches `pet/sbatch_hpss_protect_p3f_fullevent.sh:35`, whose text is
  *"`[[ -s $OUT ]] && skip` is precisely the shape"* — prose **documenting** the anti-pattern trips the
  guard against it. Another lane's file and another lane's guard; routed, not edited.

## 2026-08-11 — cause 6's C leg: the (E_avail,W) projector had BEN-064's unguarded construction (Session B)

No compute. `eavailW_covariance.py:328-330` builds `Mew` by scatter-assign into a zero matrix, so any
`(E_avail,W)` cell no reported 5D bin reaches leaves an **all-zero row**, and `M C M^T` gives that bin an
exactly zero row and column — a reported bin with **zero statistical uncertainty**, which downstream reads
as an infinitely precise measurement rather than as missing data.

**This is BEN-064's defect in a second file.** The 2026-08-09 repair landed in
`p4_lib.build_projection_M`, whose own comment states the mechanism — *"those rows of M are all-zero, so
they survive to the central check"* — and `require`s zero orphan rows. That repair was scoped to the
finding's **artifact** (the 5D→4D marginal) rather than to its **shape** (a scatter-assigned projection
with unchecked destination coverage), and this projector was not in scope. It is the projector quarantine
cause 6 is about. BEN-110.

**Fixed differently on purpose, and the difference is the point.** `p4_lib` fails closed, because in a
5D→4D marginal a reported low bin with no high support is definitionally an error. `eavailW` **reports and
warns** rather than aborting, because the `(E_avail,W)` plane is kinematically constrained by
`W² = M² + 2·M·E_avail − Q²`, so an empty cell can be physically correct and failing closed would make a
legitimate geometry unrunnable. Same defect, opposite correct handling, decided by whether the empty state
is reachable in the domain — the same test BEN-084 used to allow a heuristic in one slot and refuse it in
another.

**Tested in two halves plus a positive control**, `Cause6ProjectionCoverageTests`, 31/31 in the file.
*Numeric*: a 2×2 with one orphan row projects to a covariance that is finite, symmetric, **PSD**, and has
`C[1,1] == 0.0` exactly — so **PSD is not the check that catches this**, which matters because PSD is the
check this campaign reaches for. *Static*: the module now computes and names the orphan set (this module
imports ROOT and reads a 142 GB omnifile, so it cannot be executed here — same constraint and convention
as `test_flux_universe_fix.EavailWFluxBlockIsPerUniverse`). *Control*: `test_the_prefix_source_would_fail`
reconstructs the pre-fix source and requires the static assertions to fail on it.

**Mutations, files restored byte-exact (md5 verified):** P1 remove the guard block → 2 fail. **P2 change
`Mew.any(axis=1)` to `axis=0`** — i.e. check *source* coverage instead of *destination*, which is the
original one-directional bug — → caught. P2 is the one that matters: it is the mutation that looks right.

## 2026-08-11 — Branch C: the iteration-dynamics defect does NOT survive the LR anneal (Session C, PET)

Job **56691812** COMPLETED `0:0` in **21:45**, one A100, no training. Predeclared three-branch at
**831043d** BEFORE submission
(`docs/orchestration/PREDECLARATION-20260811-annealed-step1-trajectory.md`); launcher
`pet/sbatch_step1_trajectory_annealed.sh`. Full numbers in `VALIDATION_LEDGER.md` §2026-08-11.

**ARM 1 (CONTROL, pre-anneal 56445883)** reproduced the COMMITTED 56445883 decomposition anchors
**bit-exactly** (`increment1` 0.648331, `push_prev` 0.967659, `push_final` 0.736746, all
`rel_dev = 0.000e+00`), so the instrument was established against a committed anchor before the treatment
arm was read. End-to-end `ach/req` **0.9721 / 0.8608 / 0.6554**, iterations 1-2 WRONG-signed.

**ARM 2 (TREATMENT, annealed 56563761)** `GATE_AB_PASSED` with **`B(i) max rel dev = 0.0`** — the saved
checkpoints reproduce the stored `weights_push` exactly, so these are the run's own weights and not a
reconstruction (the pre-anneal artifact's B(i) failed at 0.866 when BEN-043 was written). End-to-end
`ach/req` **1.1101 / 1.0329 / 0.9644**, **all three correct-signed**.

**PREDECLARED BRANCH: REPAIRED.** Iterations 1 and 2 are both sign-correct and within 10%
(0.0329, 0.0356). **And the guard that would have voided it did not fire:** the predeclaration named
UNRESOLVED-via-domain-of-validity as the MOST LIKELY outcome, since the annealed arm sits near
`push ~ R`; measured, `|required - 1|` is 0.1241 / 0.0992 / 0.0319, all above the 0.02 no-information
floor. So REPAIRED is a measured branch rather than the nearer of two.

**The decisive contrast is the SHAPE.** `push dev` pre-anneal runs **-2.79% -> -13.92% -> -34.46%**
(monotonic divergence); annealed runs **+11.01% -> +3.29% -> -3.56%** (damped oscillation converging to
within 3.6% of R). Cap saturation 0.0 at all six iterations across both arms, so no clipping artifact.
The defect 56525829 localized to "iteration dynamics" is a property of the **retired full-LR policy**,
not of iterating -- the discrimination `KNOWN_ISSUES.md:430-439` asked for.

**Two by-products.**
1. ARM 1 supplies the end-to-end numbers the 2026-08-09 ledger row never had, so the wrong-sign claim at
   iterations 1-2 now holds END-TO-END and not only on the first-leg field. It also shows the first-leg
   field's bias is **not one-directional**: at iteration 0 it reports an overshoot (1.0974) where
   end-to-end is an undershoot (0.9721).
2. **Harness defect found by running it on a configuration that fails the other way:** ARM 2's emitted
   label reads `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN` for a measured **+11.01% OVERSHOOT. The third branch
   keys on `|dev| > 0.10` and is direction-blind. No number affected; NOT patched, because the run's four
   receipts bind the harness at sha `1acb1869c57f9772`. Filed and indexed:
   `FINDING-20260811-trajectory-label-is-direction-blind.md`.

**Scope.** Not a cross section, not an uncertainty, discharges no quarantine cause, does not by itself
lift Branch C, and is NOT a promotion. New and unexplained: the annealed arm's +11.01% overshoot at
iteration 0, larger than the pre-anneal arm's -2.79% there.

**Also this turn:** an earlier interactive hedge of this same measurement (`56693776`) failed -- a bare
`srun` inherited **NTasks=4** and ran four copies of a single-rank script, three dying in Horovod GPU
selection while rank 0 entered ARM 1 and looked healthy. Reconciled at `cdf5927` with a single-rank guard
and a launcher test. The batch twin was the sole valid route. `sacct -o NTasks` is the check; a growing
log and a passing preflight were not.

## 2026-08-11 — four-arm bkgaware footing re-adoption: controls reproduce, the effect DOUBLES (Session B)

Job `56693207`, `COMPLETED`, ~14 min, `--qos=shared`. Four arms from **one unchanged** throw ROOT —
nothing re-thrown, nothing re-combined. Whole stream at `uq_5d/readopt_footing_56693207.out`, no
`tail`/`head`. Watch `readopt-footing-56693207` armed and fired. Predeclared with a pre-registered value
at `../docs/orchestration/PREDECLARE-20260811-bkgaware-footing-readopt.md`. **Nothing adopted;
`values.tex` untouched; zero of seven causes discharged.**

    arm                  --combined      sqrt_tr_old    sqrt_tr_new    x       median frac/bin   PSD
    A1 bkgaware   MC     bkgaware        4.3578e-38     5.2696e-38     1.209   13.36% -> 13.57%  -3.19e-16
    A2 bkgaware   CV     bkgaware        4.3578e-38     5.6743e-38     1.302   13.36% -> 14.02%  -3.23e-16
    C1 control    MC     non-bkgaware    4.3455e-38     5.2600e-38     1.210   13.43% -> 13.61%  -4.87e-16
    C2 control    CV     non-bkgaware    4.3455e-38     5.6609e-38     1.303   13.43% -> 14.09%  -3.92e-16

**Both controls reproduce job `56429334` digit for digit** — values, ratios, medians and PSD minima —
so **branch B3 is excluded** and the footing diagnosis holds. The `g` census is identical across footings
(it comes from the throw ROOT, not from `--combined`), which is the internal check that had to hold. And
the run printed **both** block-sum medians itself, `13.36%` bkgaware and `13.43%` non-, independently
confirming `\gbdtFiveBlockMedian`.

**THE RESULT IS AN INTERACTION.** The 2 × 2 completes to: footing effect **+0.0914%** pre-J28 and
**+0.1831%** post-J28, a factor **2.004**; J28 effect **−9.3486%** non-bkgaware and **−9.2655%**
bkgaware. Pre-registered no-interaction prediction **5.264776e-38**, measured **5.2696e-38**, high by
**+0.0916%** — which is the pre-J28 footing effect over again, so the deviation *is* the doubling.
Mechanism: the flux correction drove `g` toward 1 (`×1.335 → ×1.210`), so `C_comb` carries more of the
adopted total and a change to it transmits more directly; measured transmission of the `+0.2839%`
block-sum change rose **32% → 65%**. **A footing-matched replacement therefore cannot be obtained by
scaling** — applying the pre-J28 `+0.0914%` gives `5.2648e-38` and is wrong by half the effect.

**Predeclaration honesty, and it is a finding against me (BEN-111).** Branches B1/B2 were phrased against
*"the +0.30% bkgaware refinement"* — the **block-sum** figure — while the predicted quantity is the
**adopted** one, where the same change is `+0.0914%`. Against that prose the answer reads B1 (moved
`+0.183%`, under `0.30%`); against the pre-registered **number** it is **B2**. **The prose would have
recorded "no interaction" for a measured factor of two.** That is the identical block-sum-vs-adopted
conflation I had found in `sec_systematics.tex:170-173` and routed, committed one document later. The
prose thresholds are **withdrawn as decision criteria**; the verdict rests on the pre-registered value.
A predeclared branch expressed as a number forces you to name a quantity and a basis; one expressed in
words does not.

**Suite state:** `pytest nd-unfolding/tests` = **1021 collected**, enumerated failures **9**, the same
named set as before this session's work — 7 known off-Perlmutter, plus the two routed to PET
(`test_p4_sweep_snapshots` count drift and the `test_resume_guard` false positive on a comment). One
earlier run reported **10** without enumeration and I did not capture which line; two further runs both
returned **9** with the enumerated set above, so the count is stable at 9 and the single 10 stands
unexplained rather than diagnosed. **BEN-088 rule (v) is exactly why it could not be chased** — I read a
count without the matched lines, so there is nothing to go back to. `1011 + 9 + 1 = 1021`, consistent.

## 2026-08-11 — footing re-adoption eight-file hash receipt complete

Read-only batch job **56695130** (`readopt5d_hash`) completed `0:0` in **1:37**. It stable-read ~89 GB
without ROOT writes: corrected throw input, background-aware and non-background-aware combined inputs,
all four `56693207` arm products, and the untruncated source log. The receipt has exactly eight unique
records with path, byte size, mtime and SHA-256; source job `56693207`; committed launcher SHA-256
`cc77d8caf9df4562200172ae27aa22613184f2a49f38221b5ce789ddfe52e5cc`; source-log SHA-256
`6fd6db410ca162bef98feac1ca5db991a4045de051c7174810e75b5fbcb5b4bf`; and flags
`read_only=true`, `adopts_nothing=true`, `verdict=HASHES_COMPLETE`. Independent reconciliation checked
all required fields and the A1/A2/C1/C2 input map: **PASS**.

Committed receipt:
`../docs/orchestration/state/readopt-footing-hash-receipt-56695130.json`. This closes only the
predeclared provenance receipt. It changes no B2 number, adopts nothing, edits no `values.tex`, and
discharges zero quarantine causes.
## 2026-08-11 — BEN-106 stamp propagation: written, BROKEN, fixed, verification in flight (Session B)

`adopt_unified_5d.py` now carries the upstream construction contract into every adopted product —
`fixed_seed_null_norm`, `joint_mean_shift_norm`, `n_throws` as `upstream_*` plus an unconditional
`*_checked` flag each, and `centering_convention` / `uthrow_source` / `combined_source` as `TNamed`s.
This closes the **provenance leg for causes 2, 3 and 4 at once** — the artifact that would be published
becomes able to prove its own construction instead of requiring a reader to know to walk one hop upstream
to a `.gitignore`d 2.7 GB throw ROOT. **NOT claimed closed until job `56695424` reads the stamps back out
of a ROOT the new code wrote.**

**The first version was broken and printed that it had worked.** `ROOT.TFile.Open(args.uthrow, "READ")`
re-opened the throw file partway through the output-writing block, and **`TFile.Open` re-points ROOT's
global current directory** — so all six `TParameter.Write()` calls targeted the read-only *input*
(`Directory ... is not writable`, six times) and, after `Close()`, the three `TNamed`s had no file at all
(`The current directory (PyROOT) is not associated with a file`). **Python carried on, exit 0, and printed
`[adopt5d] provenance stamped: centering=mean-centered …`.** An 892 MB product with a correct covariance
and zero stamps.

Caught by reading the stamps back out of the product — the one check I could have waved through as
ceremony on a change already compiled, linted and reasoned about. Filed as **BEN-112**, whose sharp edge is
that **the defect landed inside the fix for a defect of the same shape**: BEN-106 is *"the product cannot
prove its own provenance"*, and the first fix produced a product that **asserted** it had been stamped and
had not — converting "no evidence" into "false evidence", which BEN-084 already records as the worse
failure. Two smaller instances in the same block: `print("provenance stamped")` is a verdict-only line
with nothing behind it (BEN-077 applied to a log message), and `py_compile` passed while `os` was
unimported because a `NameError` is not a `SyntaxError` — `pyflakes` caught that.

**Repair:** capture the upstream values in plain Python while the throw file is *already* open at the top
of `main()`, never re-open it; `fo.cd()` explicitly before writing; and **assert the six stamps read back
from `fo` before printing anything**, raising `SystemExit` if they do not. The print can no longer outlive
the fact.

The broken 892 MB test product is renamed `BROKEN_UNSTAMPED_do_not_use_STAMPTEST_v1.root` rather than
deleted — it is the evidence — so it cannot be mistaken for a valid stamped product.

**Also:** the first attempt ran on a **login node at load 37 with 31 users** and took >13 minutes against
~4 on a dedicated node, with an empty log throughout because I omitted `PYTHONUNBUFFERED` from the ad-hoc
wrapper. Liveness was judged by `pgrep`, per BEN-028, not by the quiet log. The re-run is a batch job.

**Cause 4's Magnitude leg is now BOUNDED rather than measured**, and labelled as such in the criteria: the
retired procedure's scalar is not defined by any surviving specification, so constructing one and calling
the difference a measurement would be the invented-criterion failure this work exists to prevent. Bound:
the largest estimator-noise quantity in the budget is `\gbdtAiEstTrace` `1.306e-39`, which removed in
quadrature from the adopted `5.2696e-38` is **−0.0307%**; the over-generous estimator⊕ML bound `1.9836e-39`
gives **−0.0709%**. So the retired subtraction's effect on this product is **below 0.1% of the
sqrt-trace** — two orders below the footing effect and three below J28's. The measured fixed-seed null on
the same product is `5.8223e-50`, `1.31e-12` of the sqrt-trace: at the fixed seed there is nothing left to
subtract.

## 2026-08-11 — BEN-106 cluster read-back job durably covered

The repaired implementation and its launcher are committed at `5856eeb` and `034871c`. Shared-CPU job
**56695424** was submitted at 16:48:01Z with 32 requested CPUs, 180 GB and one hour, writing only
`uq_5d/readopt_20260811_footing/STAMPTEST2_bkgaware_meancentered.root`. At reconciliation it remained
prestart-pending on Priority and was the sole writer. Implementation SHA-256 is
`e1260e8dec2d39cb4653a8b4b02a198d04ea103d548a2d90b5f003f0b8044c35`; launcher SHA-256 is
`589bc4a16fc2780fd9c90936ebd6ceb4c9a1f467d50fc64650555240bdc27221`.

Terminal watch `stamp-verify-56695424` is armed. A terminal `0:0` is necessary but not sufficient:
reconciliation must read the test ROOT back and require the three `*_checked` stamps plus centering,
throw-source and combined-source stamps. Until then BEN-106's provenance legs remain **OPEN**. The test
product adopts nothing and authorizes no `values.tex` or threshold change.

## 2026-08-12 — P3F-PET full-event source archive complete and digest-verified

Transfer job **56692312** (`hpss_p3f_fe`) completed `0:0` in **1:26:34**. The committed launcher
`6dc863b` wrote to HPSS directory `mnv-p3f-pet-fullevent-final` and verified each object by comparing a
local MD5 with `hsi hashcreate`'s server-side MD5 plus an HPSS size readback. The final manifest contains
**240 unique objects: 120 selection-complete full-event endpoint ROOTs and their 120 Gate-3 receipts**.
All 240 carry matching 32-hex digests and positive matching sizes; `n_archived_digest_verified=240`,
`n_not_archived=0`, `not_archived=[]`, `complete=true`. The whole-stream log has 240 `[ok]`, zero skip,
zero failure lines; stderr is empty.

Independent terminal receipt:
`../docs/orchestration/state/hpss-protect-p3f-complete-56692312.json`. The resume guard is digest-based,
but no retry is required because there is no unverified object. This protects the already-satisfied
selection-complete detector-sample half of quarantine cause 5 off purgeable scratch. The binding joint
nuisance/retraining construction half remains **OPEN**; no covariance is adopted and no scientific
threshold changes.

## 2026-08-11 — BEN-106 VERIFIED; cause 1's path audited; no cause discharged (Session B)

**Job `56695424` COMPLETED 2:54.** `adopt_unified_5d.py` now asserts its six provenance stamps read back
from the output before printing, so COMPLETED is itself the verification. Re-read afterwards by a
**separate process**, because the in-process assertion and an external read are different instruments
(BEN-088 rule vi): eleven keys present in the new product, **all nine new ones ABSENT in the same arm
built by the pre-fix code**, and `sqrt_tr_old`/`sqrt_tr_new` bit-identical at
`4.357790406860002e-38` / `5.269625166386846e-38` — the change adds provenance and moves no number.

**Scope stated because it is the whole of what this establishes.** The provenance leg of causes 2, 3 and
4 is MET **for the footing-matched candidate**. The currently-quoted X — July `…_bkgaware_uthrow.root`
behind `\gbdtFiveAdoptTrace` `5.81e-38` — predates the stamping and carries none of them. MET for the
artifact that would replace X; OPEN for X as it stands.

**Cause 1's C leg, audited and committed as executable tests** (`Cause1PathAuditTests`) rather than prose,
so it re-runs instead of decaying. Transitive closure from the four production entry points is 11 modules;
four construct a covariance and all four are correct — `uq_math.mat_covariance`; `unified_throw_cov`'s
`joint_throw_covariance` and its knob-pair and flux `mat_covariance`; `analyze_universes_5d:97-98`'s
**inlined** mean-centered biased `1/N`; and `analyze_universes_5d:107-109`'s `np.outer`, which is the
documented rank-1 target-nucleon norm band and not a one-sided construction. **Both one-sided sites the
2026-07-12 sweep found and left unfixed are provably off the path** — they are `pet_*`, no `pet_*` module
is reachable, and they belong to cause 5. `unified_throw.py:391`'s unbiased `1/(N−1)` is off-path too
(3D legacy, `hXSec3D`, imported by nothing on this path).

**The audit's real yield was a hole in this session's OWN cause-1 test.** That test pins
`uq_math.mat_covariance` — and `analyze_universes_5d` does not call it, it reimplements it. So the guard
would have stayed green while the convention on the site that actually built X's sweep `C_syst` changed.
Now pinned directly. Four mutations, files restored byte-exact: making a `pet_*` module reachable, making
`unified_throw` reachable, CV-centering the inlined site, and adding a new one-sided `np.outer` are each
caught. **A correct audit that leaves the guard pointing at the wrong site is not a closed leg**, and the
only reason this surfaced is that the criterion demanded the path be enumerated rather than asserted.

**Also recorded from the audit's first draft:** `unified_throw` appeared in my initial reachability list
only because I had **seeded it as an entry point**. Its presence was a property of my seeding, not a
measurement — caught by the next step of the same audit. The committed test seeds only the four real
production entry points and pins `unified_throw`'s absence explicitly.

**NO CAUSE IS DISCHARGED.** Cause 2 now reads four METs, which by the criteria's own §0 is the discharge
condition, and I am **routing rather than declaring** it: the P leg holds for the candidate and not the
quoted product, and F7's *presentation* half (CV-centered as sole headline vs both side by side) is still
recorded open in this file. Declaring the first discharge of the 2026-07-12 quarantine has publication
consequences and is not a session's call to make at the end of its own work.

Suite: `pytest nd-unfolding/tests` = **1025 collected**, 35/35 in `test_uq_remediation.py`.

## 2026-08-11 — SCOPE CORRECTION to commit 8d0034f: it contains nine files it does not mention (Session B)

`8d0034f` is titled *"BEN-106 VERIFIED by an independent reader; cause 1's path audited"* and its body
describes only that work. **Its diff also contains nine files I did not author**, swept in by my use of
`git add -A` on a checkout four sessions share.

> **ATTRIBUTION CORRECTED 2026-08-11, and this is the half that was actively wrong rather than merely
> incomplete.** This entry first said all nine were *"authored by other lanes"*. **Eight of them are
> JOSEPH'S OWN uncommitted editing session** — verified in the raw diff rather than inherited: the added
> lines carry `\gk{...}` advisor queries from Gregor paired with **`\jrb{Fixed!}` replies from Joseph**
> (3 such lines, 6 `\gk{}` lines), plus a terminology sweep (`seedscan` → training-seed variation,
> `\sqrt{\mathrm{Tr}}` → `\sqrt{\mathrm{Tr}\,C}`). Only `check_canonical_designation.py` is a peer
> lane's (Session C's). **So this did not commit an agent's draft; it committed the USER'S in-progress
> reply to his advisor, under a message about provenance stamps** — a materially more sensitive thing,
> and the apology is owed to him rather than to C. Raised by the orchestrator; verified here before
> being written, because the same message reported that its own confirming grep had returned zero from
> over-escaping and the strings were plainly present.

The nine, with correct ownership:

    docs/analysis-note/app_statmethods.tex          (28 lines)
    docs/analysis-note/main_note.tex
    docs/analysis-note/paper_body.tex
    docs/analysis-note/sec_3d.tex
    docs/analysis-note/sec_experiment.tex           (an in-progress \jrb{} reply to an advisor query)
    docs/analysis-note/sec_method.tex
    docs/analysis-note/sec_results.tex
    docs/analysis-note/sec_systematics.tex
    nd-unfolding/pet/check_canonical_designation.py (261 lines — Session C's)

The eight `.tex` files are **Joseph's**; the one `.py` is **Session C's**.

**Mine in that commit are only:** `VALIDATION_LEDGER.md`, `docs/orchestration/CRITERIA-…-1-2-3-4-6.md`,
`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` and
`nd-unfolding/tests/test_uq_remediation.py`.

**NOT REVERTED, deliberately.** All nine are legitimate work that landed correctly; three commits from two
lanes now sit on top (`461ba00`, `a8e1d70`, `19ff8b6`), and C has since referenced
`check_canonical_designation.py` in two further commits. Reverting to fix an attribution would break live
work to correct a record — the wrong trade, and this repo's convention is to leave written history written
and index the correction. This entry is that index.

**The cost is attribution, not content:** `git log --follow` on eight manuscript files and one PET script
now answers *"why did this change?"* with a message about provenance stamps. **And it committed the
user's own in-progress replies to his advisor, at a moment he did not choose** — which is not a
filing error. BEN-113.

**The check that would have caught it is not `git status` but `git diff --cached --stat`** — what the
commit will *contain*, rather than what the tree *has*. Those differ exactly when someone else is working,
which on this checkout is always.

Found by acting on the orchestrator's instruction to verify the shared index before committing, after
Session C's isolated-index remedy failed silently on first use (`12ef478`). `git update-index --refresh`
reported `sec_experiment.tex: needs update` — a file I had never opened — which is what exposed this.
**Two lanes, two different staging mechanisms, the same outcome the same night: a commit containing more
than its author knew.** That is the shared checkout being a concurrency hazard rather than two slips.

## 2026-08-11 — "the suite is green except the 7 known" was a claim about a subtree (BEN-114)

Answering the orchestrator's state request, I re-derived the suite count instead of quoting my own
earlier report, and the earlier report does not survive that. **Both scopes, measured in one turn:**

| invocation | result |
|---|---|
| `pytest nd-unfolding/tests` | **7 failed / 1017 passed / 1 skipped** |
| `pytest nd-unfolding/tests docs/orchestration` | **27 failed / 1103 passed / 1 skipped** |

The 7 are the known off-Perlmutter `/pscratch` set (6 `test_fullevent_gate2.py`, 1
`test_gate2_target_runtime.py`), so **every suite claim I made this session was true of what it
measured** and none of them named what that was. The **20-failure delta belongs to no known set**: 17
`test_wakerctl.py`, 2 `test_watch_slurm_array_resume.py`, 1 `test_usagectl.py`.

**Environmental, and not a regression.** `wakerctl.py:1` and `:195` pin `/usr/bin/python3.11`, absent
here (`python3` is 3.12.2); the dispatch cases return `('evt-*', 'blocked')` against an expected
`'resumed'`, which is the missing-binary path, and `test_usagectl.py:630` asserts the interpreter's
existence directly. `git log -S'/usr/bin/python3.11'` puts the pin at `be4cd78`, long before my
`4ff5d47` scan() guard — so my change did not cause these and no code repair is indicated.

**UNVERIFIED and recorded as such: whether these 20 pass on Perlmutter is unknown.** `/usr/bin/python3.11`
may well exist there, which would make this purely a local-checkout artifact — but I have not run it, and
the comfortable inference is exactly the thing this entry exists to stop.

Routed to the orchestrator as a correction to a number it was carrying. The transferable rule is in
BEN-114: **quote the invocation with the count**, because a subtree count laundered into a repo-wide
claim is an artifact asserting a state it cannot have, and on a shared checkout the scope you omit is
systematically the other lanes'.

### Amendment — the cluster verification confirmed the headline and reproduced the finding (BEN-114)

The orchestrator had cluster reachability and ran it rather than routing it:

    /usr/bin/python3.11 -m unittest discover -p "test_*.py"   [cluster docs/orchestration]
    -> Ran 99 tests in 1.494s / OK / exit 0

**The 20 pass on Perlmutter.** `/usr/bin/python3.11` exists there, the dispatch path resolves, and all 20
were confirmed inside that corpus by the 17/2/1 file split rather than assumed. **Environmental
diagnosis: CONFIRMED. My UNVERIFIED above is discharged.**

The run also disclosed **99 cluster vs 106 local**, attributed to module-level `def test_` functions that
`unittest discover` cannot collect. **That attribution does not survive checking, and the real cause is
the one this campaign already knows about:**

| check (local, this turn) | result |
|---|---|
| `pytest docs/orchestration --collect-only` | 106 |
| node ids matching `::Class::method` | **106** |
| node ids matching `^file.py::function$` | **0** |

Every test in that tree is a `TestCase` method, so `discover` can see all 106. The 7 are **`4ff5d47`'s
`ScanPerWatchIsolationTests`** — 7 methods, in the wakerctl scan() guard commit **deliberately not
deployed to the cluster**. Local per-file: 54 + 31 + 8 + 8 + 3 + 2 = 106; a cluster tree predating that
commit holds 47 in `test_wakerctl.py` and totals 99. Discriminator routed to the orchestrator:
`grep -c "def test_"` on the cluster file, or its `git log --oneline -1`. **Stated as hypothesis pending
that one command, not as established.**

**Two consequences.** (1) The verification of BEN-114 was scoped by an unnamed argument, same as the
finding it verified — but the argument was the **tree**. On the known local/cluster fork the working tree
is part of the invocation exactly as a path is, and it is the part nobody quotes. Rule (iv): quote the
revision with the invocation. (2) The sharper one — **the 7 tests missing from the cluster run are the
guard tests for the fix missing from the cluster.** Not "7 tests were outside the invocation" but "the
cluster runs the unguarded wakerctl, and the tests that would prove the guard works are absent because
the guard is." That is the sentence to carry, and it strengthens rather than weakens the case for
deploying `4ff5d47`.

The peer's headline survived and its explanation did not. Re-deriving the operands locally is what
separated them; agreement would not have.

## 2026-08-12 — scope correction: `8fd1e08` and `7c3f617` each contain another lane's work

Filed by Session A (orchestrator) against a commit that is not its own, by agreement with its author,
in the `ae7e615` form. **Nothing is amended or reverted** — both commits are pushed, and rewriting
history to fix provenance falsifies a second thing to correct the first.

| commit | its subject says | its diff actually is |
|---|---|---|
| `8fd1e08` | BEN-114's real mechanism | **A's two files** — `PROMPTS-20260811-four-session-closeout.md` and `waker_fired_but_unread.sh`, 2 files / 51 insertions, named nowhere in the message |
| `7c3f617` | BEN-137/138 + ledger amendment | **also carries B's BEN-114 second amendment** |
| `c3b39e1` | — | the rescue: B's `KNOWN_ISSUES.md` block, 33 lines, one file, nothing foreign |

**Three lanes, three commits, one window of about four minutes, and every one of us was applying the
published remedy correctly at the time.** B had split C's BEN-137 row out of its own staged set with
`git apply --cached --unidiff-zero` roughly ten minutes earlier — so B protected C's line from B's
commit, and C's commit then took B's.

**Why the remedy chain did not hold.** `git add -A` → stage by path → split by hunk each refine *what
you stage*; the defect is *that staging is shared at all*. `git diff --cached --stat` is a read of
shared mutable state, so it is a TOCTOU check rather than a guard: A ran it, it correctly showed four
files where two were expected, A unstaged B's two — and the loss happened in the window after that
read. Path-granular discipline also fails silently in the case where two lanes touch the **same** path,
and `FINDINGS.md`, `KNOWN_ISSUES.md`, `VALIDATION_LEDGER.md` and the RUN_LOGs are precisely the files
every lane writes.

**The remedy, and it is one flag rather than a structural change** (B's, and B raised it against its own
argument for per-lane worktrees): `git commit -m ... -- <pathspec>` builds a **temporary index from the
working tree**, so it structurally cannot absorb another lane's staged content. Two limits, so nobody
adopts it as unconditional: it commits the whole working-tree file for that path, so it closes the
cross-file race and **not** the same-file one — use `GIT_INDEX_FILE=$(mktemp)` when both apply — and a
lane holding a stale staged blob of a file another lane just committed will revert that line if it
commits from the staged copy. **Do not `git add` at all when the pathspec form will do; staging is the
exposure.** Verify with `git show --stat` *after* the commit exists: that is the only read racing
nothing. Filed by B as BEN-115 at `3292345`.

This entry itself was written to the working tree and committed with `git commit -F <file> --
<pathspec>`, with no `git add`.

## 2026-08-12 — scope correction: `f7ccdd8` carries B's BEN-116, and the precondition is also TOCTOU

Filed by Session A against its own commit. **Not amended, not reverted** — it is pushed, and B's
BEN-116 content is intact inside it. Only the attribution is wrong.

`git show f7ccdd8 -- docs/orchestration/FINDINGS.md | grep -E '^[+-]\| BEN-[0-9]+'` returns three
lines: `+| BEN-116` and a `-`/`+` pair on `BEN-134`. Both are B's. The commit message describes an
id-block table and nothing else.

**Why this is a finding and not a repeat.** The precondition B had just written into BEN-115 — verify
the shared file is clean in the working tree immediately before naming it — was applied exactly:
`git status --porcelain -- docs/orchestration/FINDINGS.md` returned empty, then
`git commit -F <file> -- <pathspec>` with no `git add`. B edited the file inside that window and the
pathspec form took the working-tree lines. **So the precondition is itself a read of shared state with
a window before the write** — the same sentence that was written about `git diff --cached --stat` two
hours earlier, now true of its own replacement.

Third layer of one defect. `git add -A` → stage by path → split by hunk → staged-diff read →
clean-tree precondition: every step narrowed *what you name* and none removed the window.

**Surviving rule, superseding the pre-commit forms:**

1. Nothing done **before** the commit closes the window on a contended file. Not `add -A`, not
   path-granular staging, not hunk splitting, not `git diff --cached --stat`, not the clean-tree check.
2. `git commit -- <pathspec>` still helps substantially, but only for files you **do not name**. For a
   named file it takes the working tree, staged or not (B's T2, D's T2, reproduced by A).
3. **Read the committed contents afterwards, every time, and file a scope correction when it fires.**
   A detector, not a preventer — and the only technique that has caught an absorption at the moment it
   happened rather than hours later. It has now done so twice, including here.

**Five absorption events across four lanes in one night:** `8fd1e08` (B's subject, A's files),
`7b26803` (D's subject, C's BEN-137 row), `7c3f617` (C's subject, B's BEN-114 amendment), one of D's
ten found by D's own T2 audit, and `f7ccdd8` (A's subject, B's BEN-116). Every one by a session
applying the then-current published remedy, and the last by the session that had just relayed it.

Detected post-hoc by `git show HEAD -- <path> | grep -cE '^[+-]\| BEN-[0-9]+'` returning 3 where 0 was
expected, seconds after the commit. This entry was written with the same procedure and checked the
same way.

## 2026-08-12 — Joseph's five decisions: Cause 2 discharged for the candidate, job 56720356

Authorization for everything in this entry: **Joseph → Session A (orchestrator, typed directly) →
Session B**, 2026-08-12, recorded per BEN-082(v). Five items were routed; four landed, one cannot be
executed from this session and is returned.

### Item 1 — CAUSE 2 DISCHARGED, candidate only. The first discharge of the 2026-07-12 quarantine.

*"Declare Cause 2 discharged only for the footing-matched, stamp-verified J28 candidate, identified by
exact artifact path/hash."* **The artifact did not exist when the instruction arrived** — measured, not
assumed: A1/A2 (16:18–16:20 on 08-11) are footing-matched and hashed but predate BEN-106's stamp
propagation; `STAMPTEST2` is stamped but unhashed, mean-centered only and test-named; no stamped
CV-centered twin existed at all. Declaring on A1/A2 while citing stamps verified on a *different* file
is the invented-after-the-fact closure the criteria document exists to prevent, so the arms were
regenerated **with** stamps under adoption names.

Job **`56720356`**, `sbatch_adopt_stamped_footing.sh`, COMPLETED `00:05:20`, exit `0:0`. Launcher and
predeclaration were committed at `46b1257` **before** submission; the executed file's sha256
`18c7e4ce…` was verified equal to the committed blob, because the cluster tree is `683bdcc`, 114
commits behind, and pulling 114 commits into a tree three other lanes are using is the larger risk.

**Branch S1 of [the predeclaration](../docs/orchestration/PREDECLARE-20260812-stamped-footing-adoption-candidate.md).**
Predeclared `5.2696e-38` / `5.6743e-38`; measured `5.2696e-38` (×1.209) and `5.6743e-38` (×1.302).
**No value moved** — Joseph's *"do not change the value"* holds. S2 (reproduction failure → discharge
does **not** proceed) and S3 (UNRESOLVED) were live outcomes and are not what happened.

| role | path | sha256 |
|---|---|---|
| headline, mean-centered | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | `4f168e83eaeb4bc7191a4e13e219c7ff06556e5ad30b9df4fcc249e6720c7ec2` |
| conservative variant, CV-centered | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_cvcentered_20260812.root` | `dbcd5359c76e5c12b97ec8819980cb11c492f051f054a50d9b0bca2bd02fb9dd` |
| input, unified throw | `nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` | `4cb02ae767c887b5fc43554a8f2c4a1821d25fdf547aeeeedbe8b3d57f8b4281` |
| input, bkgaware combined | `.../universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a` |

Both products stamp **and read back** `n_throws=160`, `joint_mean_shift_norm=1.878696733368378e-38`,
`fixed_seed_null_norm=5.8223488501140625e-50` — the read-back is an assertion that raises, not a print
(BEN-112). Receipt and whole stream copied off purgeable scratch into
`nd-unfolding/uq_5d/readopt_20260811_footing/`; the log was copied entire, never through `tail`
(BEN-026). **The `.out` is matched by `.gitignore` and is therefore NOT tracked** — it sits at
`nd-unfolding/uq_5d/readopt_20260811_footing/adopt_stamped_56720356.out`, sha256 `da61b47ca7742d1f24f9fbc84ba19a83757b86cbc3d55b21b2ab2d9eabb792f9`,
893 bytes, 27 lines, on both scratch and this checkout. Recorded rather than force-added: the
ignore rule is deliberate, and every number the log carries is transcribed into this entry and
into the committed `STAMPED_HASH_RECEIPT.slurm-56720356.json`, so the hash is what makes the
untracked copy falsifiable.

**BOTH COUNTS: 1 of 7 for this candidate, 0 of 7 for the July product `values.tex` quotes.**
`values.tex` is untouched, the four `\gbdtFive*` macros remain gated, and the overall quarantine stands.
Joseph asked for both numbers explicitly so this cannot be read as *"one down, six to go"* — the
discharge attaches to an artifact the note does not yet cite.

### Item 3 — footing: retain background-aware, and split the two effects

`+0.2839%` is the **block-sum** effect; the **adopted-value** effect is `+0.0914%` pre-J28 and
`+0.1831%` post-J28. All three re-derived from `VALIDATION_LEDGER.md:108/109/409` in the same turn as
the edit rather than transcribed from the routing message. `sec_systematics.tex` and
`VALIDATION_LEDGER.md:723` now carry all three, so a reader cannot pick up one and apply it to the
other — which is not hypothetical, it is **BEN-111**, where my own predeclared branch set was anchored
on the rounded `0.30%` block-sum figure while predicting the adopted quantity.

### Item 5 — the 1.17 E_avail scale: unresolved UPSTREAM, not merely uncited here

Joseph read the public MAT source and reports the header carries the bare constant with no explanatory
comment. That **replaces** this repo's standing *"the upstream comment has not been read"*, which
pointed the next agent at a document that does not contain the answer. Publication-freeze requirement
recorded in both homes: do not change the value or rerun; before freeze require **either** an
authoritative calibration rationale / collaboration confirmation **plus** identification of the
systematic that covers it, **or** an explicit assumption **plus** a quantified sensitivity. Lineage
alone is insufficient. Status: **ASSUMED and UNRESOLVED**.

### PROSE — one normalization throughout in `sec_eavailw.tex`

Both comparisons now state data/generator: corner `1.54/1.58/1.56/1.61`, W∈[2.2,3.0) `1.30/1.33/1.31/1.35`.
The W-band ratios were **computed from the source cross-sections** in
`3d-unfolding/genie/eavailW_band_20260811_allfour.log:22-23`, not converted from the rounded `23–26%`,
because converting rounded endpoints manufactures precision the source lacks (BEN-086). Falsifiable
cross-check per BEN-077: the same operands reproduce the previous wording exactly — 22.95 / 24.85 /
23.61 / 25.81 %, i.e. *"23–26% below the data"*. **The convention changed; no number moved.** The
spurious contrast a reader used to infer was ~2.4×; consistently normalized it is ~1.2×.

### Item 11 — per-lane git identity, per-invocation only

`git -c user.name=... -c user.email=...` per commit; **no shared git config written**. Effective
identity for these commits is `Lane B (uncertainty construction) <josephrb+laneb@stanford.edu>`,
recorded here as the lane receipt Joseph asked for. D's measured nuance holds: `-c user.email` sets
**both** author and committer, whereas `GIT_AUTHOR_EMAIL` would set only the author — verified on the
first commit that used it (`9925ba8`).

### Item 6 — NOT DONE, and it cannot be done from this session

Gregor's correction is **not sent**. Verified three independent ways rather than assumed, because A's
constraint was explicitly *confirm the channel delivers before reporting it sent*:

1. **There is no send tool.** The connected Gmail surface exposes read, label, trash, spam and *draft*
   operations only. No send.
2. **The connected mailbox is Joseph's personal account** (`jrbailey555@gmail.com`), not a
   collaboration channel — 201 threads in 30 days, all personal.
3. **There is no correspondence with Gregor in it at all**, and his address appears nowhere in the repo,
   so there is no thread to reply into and no recipient to address.

This confirms the standing note that this channel accepts drafts and delivers nothing. **Joseph's
verbatim text is returned to Session A for him to send**, unparaphrased and unedited. The source-side
half was already correct before this decision arrived (`efd4c6b` fixed the `\jrb{}` reply in
`sec_experiment.tex`); what remains is the record correction to the person, which is the half that
matters and the half I cannot perform.

## 2026-08-12 — HPSS over-allocation notice: residency inventoried at 1.4573 TB, and the copy it looked like was not the cause

A NERSC notice that user `josephrb` is over the HPSS allocation reached this session by relay (Codex via a
peer session, quoting a forwarded mail from Ben). **Nothing in it is Joseph verbatim and it authorizes no
deletion**; both facts are recorded in the receipt, and the decision it implies is routed to Session A.

**Measured, all read-only:** `hsi du -s` over all four top-level HPSS entries gives
**1,457,304,348,109 B (1.4573 TB) in 279 files**. That agrees with the two digest-verified manifests
(1,457,304,332,415 B, 276 files) to **15,694 B in 3 files** — `backups/` (2 files, pre-campaign, dated
2026-02-20) plus `mnv-p3f-smoketest` (1 file). Their block-rounded ceiling is 16,384 B, over the residual
by 690 B, inside the 1,533 B of 512-byte slack available across 3 files. File counts reconcile exactly
(240 + 36 + 1 + 2 = 279), and each archive directory's HPSS mtime equals its Slurm `End` to the minute.
**Pre-campaign residency is 1.1e-8 of the total: this campaign's two archives *are* the residency**, so
there is no legacy archive to reclaim or blame.

**The attribution, which is the part that would have cost something.** The notice is stamped
2026-08-12 06:50:13 PDT. Job **56762440** (quoted products, 0.322 TB) ran 06:49:24 → 07:22:48 PDT, so the
notice fired **49 s into a 2004 s copy — 2.4% elapsed, ~7.9 GB moved of 322 GB** at that job's own
measured 161.15 MB/s. The overage was already set by job **56692312** (p3f full-event, 1.135 TB,
**77.9%** of residency), which finished 13.7 h earlier. Slurm and the notice were confirmed to share one
clock (`date +%Z%z` → `PDT-0700`) rather than assumed. The snapshot time NERSC used is unstated, so it was
enumerated instead of guessed: a snapshot before 2026-08-11 15:39 would put residency at 15,694 B, which
cannot exceed an allocation, so that case is **excluded by the notice existing** — and every surviving
case puts p3f alone over the line. **The conclusion does not depend on the unknown.** It also yields a
bound: the user HPSS allocation is **< 1.135 TB**, so the overage is **> 0.3223 TB**. A 1 TB default would
fit that bound but is a guess and is flagged as one — Iris is the authority and was not read.

This matters because the running copy was the obvious suspect *and* the one archive whose 36 files back
technote-quoted numbers, 35 of them named only by `VALIDATION_LEDGER.md`. The plausible culprit and the
costliest set to lose were the same set. Filed as **BEN-118**.

**Three of the four reduction levers are measurably empty.** Deduplication frees **0 B**: the p3f
manifest (sha256 `c9e1902e…`, verified against its receipt before use) has **240/240 distinct md5 and
240/240 distinct basenames**, the quoted set 36/36 distinct, and cross-archive overlap is zero by
enumeration. Supersession is worth **~9.98 GB, 0.68%**, and only by deleting the uncorrected member of the
five `X/` vs `X/corrected/` pairs — proven-distinct content whose whole point is which products are
corrected. The one genuine supersession, `mnv-p3f-smoketest`, is ≤ 12.8 kB. **The discipline that made
these archives trustworthy — collision guard, digest verification, enumerated non-overlap — is exactly
what leaves them no slack.** Only the prospective lever is live: difference future protection asks against
these 279 catalogued objects first.

So the remaining options are both Joseph's: accept Ben's offer to raise the allocation, or authorize
per-item deletion. Tracked as **OI-48**, and the causing archive is quarantine cause 5 — Session C's, so it
was measured and not touched. Receipt:
`../docs/orchestration/state/hpss-residency-inventory-20260812.json`.

## 2026-08-12 — the same audit ran in two lanes: three corrections to mine, and the stale 206.5% explained

A parallel lane had already audited HPSS (`RECEIPT-20260812-hpss-space-audit.md`, `8ec4e62`/`243af2f`),
which I found on fetching before pushing. **Three-way agreement, no shared operand:** their per-directory
`hsi du`, their single `hsi du -s .` at HPSS home, and my two digest-verified manifests plus a 15,694 B
residual all give **1,457,304,348,109 B / 279 files**. Their direct measurement of that residual
(smoketest 12,334 + backups 3,360) equals my *inferred* residual exactly and sits inside the per-directory
ceilings I had bounded from block counts, so the 512-byte rounding-slack argument is confirmed rather than
merely plausible.

**Three corrections to my receipt, all pre-push.** (1) Dedup frees **12,334 B, not 0 B** — the one
byte-identical pair on HPSS is smoketest's single file against a p3f object, a *cross-directory* duplicate.
I checked md5 uniqueness *within* each archive and took cross-archive non-overlap from job 56762440's
receipt, whose enumeration covered the quoted set against p3f and never covered smoketest: **I asserted an
absolute total from two partial scopes.** (2) The quota **is** readable from the CLI —
`hpssquota` at `/global/common/software/nersc/bin/hpssquota`. I probed `hsi quota`, `hsi lsquota`,
`myquota` and `showquota`, got `unrecognized command` and a table listing only home and pscratch, and
concluded the instrument did not exist, when what I had established was that **four instruments do not
report it**. The other lane made the identical error and self-diagnosed it as scope. Two lanes
independently: *an absence of the answer in the tools you thought of is not an absence of the tool.*
(3) There are **three** options, not two — **MOVE** is the live answer, and the one that costs no science:
CFS `m3246` has ~20,990 GB free and moving the 240 p3f objects takes HPSS to 58.6%. My receipt offered
only increase-or-delete because it never considered a second destination.

**What this lane adds, `hpssquota` run first-hand:** quota **512.00 GiB**, charged **1.03 TiB**,
**206.5%**, exit 1. Their audit said that reading predates the quoted copy; I identified what it therefore
contains, to the byte — charged = p3f 1,134,998,230,283 + smoketest 12,334 + backups 3,360 =
**1,134,998,245,977 B = 1.0323 TiB**, which displays as `1.03TiB` **and** 206.5%, matching the instrument
on both printed fields, with residency-minus-that equal to the quoted archive at **zero remainder**. Full
residency would display 1.33TiB / 265.1%. **Operationally:** sizing a reduction from the live reading
targets 545.05 GiB, the committed state needs **845.22 GiB**, and the 300.17 GiB gap *is* the quoted
archive. Their addendum's 845.22 GiB is right for the eventual state and their OI-48's 206.5% is right for
now — both true of different snapshots, and neither document said which to act on. It also confirms the
attribution from the **accounting** side, independently of timestamps: the copy that looked guilty is
provably absent from the charged figure that declared the overage.

**Resolution of the id collision.** Both lanes appended after OI-47, so we both wrote OI-48 — the exact
shape BEN-080/082 warns about, where *"OI-48 closed"* is true of one and false of the other. Mine was
**deleted, not renumbered**: theirs has the denominator, the move option and the scratch evidence, and a
second storage row would only give the two somewhere to drift. I added one sentence to their row instead.
**BEN-118 corrected** from "Dedup 0 B" to "12 kB of 1.46 TB". One discrepancy left for them: their row
says *"the 16:24 copy"*, while `sacct` in the same turn with the TZ confirmed `PDT-0700` gives
06:49:24 → 07:22:48 PDT = 13:49:24 → 14:22:48 UTC. 16:24 matches neither, and the BEN-069 timezone family
already has three instances — flagged to them, not edited into their document.

## 2026-08-12 — BEN-119 and BEN-120: my power test missed its own conclusion, and the duplicate-id gate covers one ledger of four

**BEN-119, on Session D's routing.** D was right that this belonged in `FINDINGS.md` rather than in one
audit receipt's `POWER_TEST` block — a finding about how agents fail has a canonical home, and a receipt is
a record of one audit. The finding: my HPSS battery ran 20 assertions green and caught all three byte
corruptions correctly, **and every one of them left the attribution checks green**, because those rest on
timestamps and the mutations perturbed bytes. The receipt's whole load-bearing claim was asserted by checks
nothing had ever made fail. M4 and M5 exist for that. The transferable form is **a check that carries the
verdict reads as a restatement of it, so it is the check least likely to be power-tested** — mutating it
feels like mutating the answer, and "obviously it fails" is a prediction about code nobody ran. D's
sharpening is why it earns a row: this is a **third axis** after BEN-162 (sibling function) and BEN-117
(call path), and passing on one says nothing about the other two. Long form:
`FINDING-20260812-power-test-axis-selection.md`, indexed; 34 `FINDING-*.md`, 0 unindexed.

**BEN-120, from C's BEN-142.** C's load-bearing observation is that the three-way `OI-48` collision was in
**allocation, not namespace** — BEN-080's prefixing rule was fully satisfied and could not help — and that
it surfaced as a git conflict *only* because all three rows landed at the table's end. So I asked whether a
mechanism already existed, and found one: `whose_row.py:436 check_ledger_ids()` does check duplicates, two-
sided, against the real file. **It is called with `VALIDATION_LEDGER.md` and nothing else** (`:551`), and
its id parsing is VL-specific rather than merely its call site — `int(v[2:])` yields `-48` for `OI-48` and
raises for `BEN-118`. `BEN_ROW`, `CLM_ROW` and `OI_ROW` all already exist twenty lines above it. The
remedy was written for the VL re-id and the occasion set its scope, which is the class BEN-162/163 name.

Scanned all four id-bearing ledgers: **OI 50 ids, BEN 140, CLM 12, VL 108 — zero duplicates anywhere.**
So this is a near miss, not a live defect: today's four hand-catches (three `OI-48`, plus my own
byte-identical `BEN-116` pair at `a484a2f`) were all attentiveness, the mechanism BEN-105 counts four
failures of. `KNOWN_ISSUES.md` is reported **UNSCANNED, not clean** — it has no per-row id scheme.

**The design constraint matters more than the gap.** `check_ledger_ids` bundles three invariants and only
one generalises: duplicates are universal, dense-from-1 is VL-only. Widening the existing call would fire
**64 false failures on FINDINGS.md's legitimate archive gaps**, through `merge_guard.sh`, which exits 3 and
blocks every lane's merge — and BEN-118's own second half is that a check refusing for the wrong reason
teaches operators to override it. **Routed to Session D rather than applied**, with the sketch and the
contract-text updates it implies: `whose_row.py` is in active edit by D this hour (BEN-169), and patching
it now reproduces exactly what produced `a484a2f`. Ingredients:
`../docs/orchestration/state/ledger-id-uniqueness-scan-20260812.json`.

**Correction accepted from A.** I flagged their `16:24` and proposed it as a fourth `BEN-069` timezone
instance. A verified `sacct` with the TZ printed and showed `16:24` is 2 h 02 m from 14:22 UTC and 2 h 35 m
from 13:49 UTC, so **no offset produces it** — it is the `0.874 TB` family instead, a figure repeated from
a relay without asking what produced it. Flagging the number was right; my family attribution was wrong.

## 2026-08-12 — the 4D adopted covariance is WAITING-USER, not unstarted: I checked the blocker instead of taking the read

Session A offered me the 4D adopted covariance as "the only one of the three unstarted **and** unblocked".
I said I would verify by checking the blocker rather than accepting that, and it is **blocked**.
`INTEGRATION_CHECKLIST` "Claims GATED" #8 gates it on three things, and the third is upstream: the 4D
unified throw wants `3d-unfolding/runEventLoopOmniFold_MEFHC_3D_universes_full.root`, which I stat-ed and
found **absent both locally and on `/pscratch/sd/j/josephrb/MINERvA-OmniFold`**. The upstream item
(`CORRECTED_UQ_PRODUCTION_STATUS.md`, "Pending decisions / gates" 3) names three options, and they are a
**decision, not a computation**. Filed as **OI-55**, WAITING-USER, with what each option costs: (a) regen
is mechanically available — both launchers exist on the cluster — but scratch is at 79.7% and HPSS is over
quota, so it is a storage decision too; (b) marginalizing 5D→4D is cheapest and is the one with a
**measured** failure, median 4.43% against a 3% per-bin gate while integrals agree to 0.56%
(`FINDING-20260809-stage6-central-gate-cannot-pass.md`); (c) accept the sweep-based 4D combined without
inflation and label it. **The row previously read as a compute gate, which is why it was offered as
unblocked work — and the misreading survived until the file was actually stat-ed.** That is now recorded in
the row itself.

**Two repairs to the GATED list, and one thing I deliberately did NOT repair.** The `(E_avail,W)`
SIGNIFICANCES bullet **contradicted itself**: three lines after recording GiBUU's corner ratio as landed
at **1.609**, it instructed the reader to recover the "separately UNCOMPUTED" GiBUU corner ratio by
re-running `make_figures.sh:55`. Struck, with the mechanism named — the satisfied gate and its own closure
sat **eight lines apart in one bullet**, so the 2026-08-11 re-verification and the closure edit each read
the half they came for. The two genuinely open preconditions are untouched.

The thing I did not touch: the binding row says *"zero are discharged for the 5D GBDT covariance"*, and
after discharging cause 2 today my first instinct was that this had gone stale. It has **not**. `VL63`
reads *"DISCHARGED 2026-08-12 for the footing-matched, stamp-verified candidate ONLY … still OPEN for the
adopted 5D GBDT covariance that `values.tex` quotes"*, so **zero is exactly right for the artifact this
row names**, and editing it would have converted a correct statement into a false one on the strength of my
own recent work. This is the (cause × artifact) rule doing the job it was written for — and it is worth
recording that the near-miss came from the discharger, who had the most reason to believe the number moved.

## 2026-08-12 — repair-4 increment 1: `p4_evidence.py` de-rooted, which is the cluster-P4 hold's release condition

Repair-4 authorized to this lane by Session A (A is migrating). Code/tests/receipts only, **no cluster
P4 run** — Joseph's hold stands and names `p4_evidence.py`'s hardcoded root as its release condition.

**Baseline measured first: the suite was 111 green while the verifier's verdict was BLOCK.** The reason
is visible in the test file — it reads `p4_evidence.py` with `.read_text()` and asserts on source
strings; it never imports it. It *cannot*: the module is straight-line top-level code that imports
`ROOT` and, until now, called `os.makedirs` at import under a hardcoded `/pscratch` path. **That is
BEN-119's axis problem at repo scale** — 111 assertions covering source text, none covering behaviour,
which is exactly why defect 6 of the brief demands an integration matrix that *executes* the drivers
and asserts the specific intended failure rather than a generic nonzero.

Fixed: `REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"` → `REPO = P.REPO_ROOT; ND = P.ND_ROOT`.
The resolver is **not new** — repair-5 (D4a) put it in `p4_lib` with the comment *"which also makes it
testable off-cluster"*, and `p4_evidence` has imported `p4_lib` the whole time. **One more remedy
bounded to the file that failed** (BEN-162/163): `p4_lib` was de-rooted, its importer was not. And the
real defect is **disagreement**, not the literal — every containment guard in `p4_lib` checks against
`p4_lib.REPO_ROOT` while this module carried its own, so the two could differ with no guard able to see
it. Also moved the import-time `os.makedirs` to the write site, ordered before the first `.PENDING`,
so the docstring's read-only claim is true of the import.

**Power-tested, both directions, and the negative control is committed rather than described.** Suite
111 → **115**. Then the pre-fix form was reconstructed in the real file and the three de-rooting tests
each failed on their own assertion — `/pscratch` present, `P.REPO_ROOT` absent, import-time `makedirs`
back — after which the file was restored and re-verified by sha256 (`70604e73…`) and a full green run.
A fourth test rebuilds the old form in a temp copy so the control runs on every future invocation, and
it asserts its own anchor line still exists, so it fails loudly if it goes stale rather than passing
vacuously. One subtlety the tests had to handle: the de-rooting commit deliberately **quotes** the old
path in a comment, so the checks strip comment lines — a raw substring check would fire forever on the
explanation of its own fix.

Remaining: defects 1–6 of `followup-agent-A-standard-05.md`, unworked since 2026-08-07. Two
preconditions carried forward for whoever runs the chain: **stage 3 must not run on pre-G-1 code** (it
writes ten receipts with no `bkg_mode`, the launcher skips endpoints that already have one, deletions
are frozen → unfixable provenance regression) and **G-1 is code-only, not on the cluster checkout**.

## 2026-08-12 — repair-4 increment 2 (`a517826`): the callee was de-rooted and the callers were not

Increment 1 was necessary and **not sufficient**, and the way it fell short is the class I had cited
in its own commit message an hour earlier. All three shell drivers — `run_p4_standard.sh`,
`run_p4_merge_audit_std.sh`, `run_p4_unfold_std.sh` — carried the identical
`REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"`, and two of them `cd "${ND}"` **before** invoking
the de-rooted `p4_evidence.py`. So the chain stayed pinned to one checkout *through the caller*:
I fixed the callee and left the callers, which is BEN-162/163 verbatim.

Each driver now derives `ND` from `${BASH_SOURCE[0]}` and `REPO` from its parent, and **fails closed
with exit 3** when no `p4_lib.py` sits beside it. The idiom is safe for exactly these three and the
code says why: no `#SBATCH` header, invoked as `bash run_p4_*.sh` under an existing allocation, so
`BASH_SOURCE` is the real path — an sbatch-submitted script is spooled by Slurm and would resolve to
the spool copy. All three `bash -n` clean.

**The three new tests execute the drivers** — the first behavioural tests in a suite whose other 115
assert on source text. 115 → **118**. Power-tested by reverting all three: each failed on its own
assertion, and the load-bearing one is **`expected exit 3, got 1`**. The un-de-rooted driver *does*
fail in a foreign tree — late, for the wrong reason, with a generic abort. **A test asserting merely
"nonzero" would have been green on the defect**, which is what defect 6 means by *"assert the specific
intended failure, not a generic argparse nonzero"*, now demonstrated rather than asserted. Restored
and re-verified by sha256 (`38721b9a…`, `dcae976a…`, `412086a3…`) plus a full green run.

Two defects of my own, both caught by running things rather than reading them:

- **A test bug that would have passed on the cluster and failed only locally.** I compared bash's
  resolved `cd && pwd` output against an unresolved temp path; on macOS `/var` is a symlink to
  `/private/var`. For a test whose entire subject is path resolution, "green on the cluster, red on
  the laptop" is the worst available outcome. Both sides now `resolve()`.
- **`a517826`'s commit body has a hole**: `-m` with a backticked `bash run_p4_*.sh` was globbed by
  zsh, so the body reads *"invoked as  under an existing allocation"*. **This is BEN-164's shape**,
  and BEN-164 also records that the *amend* which fixed it orphaned the sha — so this is recorded
  here and the sha is left intact rather than rewritten. The clause survives verbatim in the
  committed `P4_STANDARD_STATUS.md`, so no information is lost, only the commit body is degraded.
Operational rule for this lane: **use `git commit -F <file>` for any body containing backticks**,
which is what the earlier commits today did without incident.

## 2026-08-13 — Gate 6 PET ML ensemble complete 5/5; existing Session-A result canonically closed

Array `56834281_[1-5]` reached aggregate terminal state. Same-turn `sacct -X` resolved the logical/raw
pairs rather than repeating member 5 under the array alias (BEN-210/211): `1→56834282`, `2→56834283`,
`3→56835083`, `4→56835084`, `5→56834281`. Every task is `COMPLETED 0:0`; elapsed times are
`03:02:38`, `03:05:15`, `02:59:03`, `03:00:38`, and `02:59:23`; five distinct `.done` artifacts exist.

Session A had already completed the scientific reconciliation after the last task ended and committed it
at `92551a4`, so this wake did not reread logs, seed policies, or member arrays. That receipt confirms the
persisted realized policies `(42,0)…(46,4)`, the promoted Gate-2 target, the five per-member deviations,
and the two source identities. Contrary to the wake's tentative context, the inventory **was predeclared
before submission**: commit `6bd3707` fixed `N=5` and the exact seed table; `0f5fee2` later repaired the
launch environment and resubmitted `56834281`.

The literal predeclared comparison passes by the letter: spread `0.227213` exceeds the declared
within-process floor `1.26775e-4`. **This does not establish that Gate 6 resolved estimator variation
at all.** The result is not promoted. Members 2, 4, and 5 exceed the Gate-4 nominal dev bar and set
90% of the spread. Against the one-pair across-node/process floor, the all-five and two-qualifying-member
comparisons differ (`13.9x` versus `1.4x`), so **neither margin is quotable** while convergence is routed.
The products do not persist the execution environment that the floor is intended to expose; host/GPU
identity was recoverable only from sidecar markers and logs. Whether the spread is estimator variation or
non-convergence is routed to the PET owner. No `C_ML`, central-value change, retry, provider reset, or UUID
change occurred in this reconciliation.

## 2026-08-13 — Gate 6 owner disposition and five-member no-training trajectory preflight

The legacy school OAuth home refused Agent B's next turn. Under the standing account-migration
authorization, the root JSONL plus its five-file session subtree were copied no-clobber into the
authenticated flat school home, hash-verified, and the registry switched under the role lock. The
same UUID `46e4af3e-c3f2-4fa5-abc7-f0da72817282` then resumed successfully; no replacement role or
reset credit was used.

Agent B returned `BLOCK_FOR_PREDECLARED_CONTROL`. The five finished members are valid inventory, but
their literal spread-vs-floor pass does not license `C_ML`: the declared floor is within-process,
three members outside the nominal bar dominate the spread, and the predeclaration did not contain a
branch for that shape. Ensemble-mean centering is a component convention only and does not move the
promoted nominal central.

The smallest discriminator trains nothing. A same-turn preflight found exactly eight expected
checkpoint files in each isolated member directory. The artifacts' recorded normalized-target path
is now absent because that exact target was archived before the Gate-5 rerun; the archived copy is
bound by SHA-256 `544b2f6a…`, so the diagnostic tooling gained an explicit hash-required override
rather than recreating or repointing the canonical path. The fixed all-member rule uses only numeric
`end_to_end_achieved_over_required`: absolute deviations must be non-increasing over iterations
0→1→2 and at most 0.10 at iteration 2. Any member failure blocks the family; no passing subset may be
promoted. The categorical harness label is excluded because it is direction-blind; signed
`push_dev_vs_R` is retained. A five-task collision-isolated GPU array is the selected route because
all arms can run in parallel and no interactive allocation existed at preflight.

The predeclaration, target-override tests, and five-task launcher were committed and pushed at
`3c5c307` before submission. Array `56847059_[1-5]` was then submitted as the sole writer; all five
tasks were `PENDING (Priority)` at the launch receipt. Terminal and one-hour queue-latency watches are
armed. This launch performs inference only and does not authorize `C_ML`, Leg 2, a central move, or a
Gate-4 disposition.
## 2026-08-13 — Gate 6 member trajectories complete; one of five passes, family BLOCKED

Array `56847059_[1-5]` completed all five no-training tasks `0:0`. Same-turn accounting resolves the
logical/raw mapping as `1→56847061`, `2→56847062`, `3→56847971`, `4→56848031`, and `5→56847059`,
with elapsed times from 13:44 to 14:00 on one A100 per member. All member logs finish cleanly. Every
Gate A/B receipt passes exact MC-index and truth-normalization identity, Gate B(i) has zero relative
deviation, Gate B(ii) has exactly one off-shell construction, and all three reproduction anchors are
exact. The launcher is the predeclared `3c5c307` content (`13a598f…`) and every member uses the
explicit archived target with SHA-256 `544b2f6a…`.

The predeclared evidence is the numeric `end_to_end_achieved_over_required` only. Absolute deviations
over iterations 0/1/2 are member 1 `0.519482/0.124001/0.019310` (PASS), member 2
`0.141819/0.152498/0.101483` (FAIL), member 3 `0.056478/0.041552/0.042650` (FAIL), member 4
`0.125205/0.174153/0.180208` (FAIL), and member 5 `0.238559/0.228871/0.246523` (FAIL). The signed
push deviations are recorded in the canonical receipt and ledger. Because the criterion requires all
five members, the family is BLOCKED. No subset, `C_ML`, central move, Leg 2, or unchanged retry follows.
Gate 4's user disposition is independent.

## 2026-08-13 — Gate 5 dedicated coherent-replica path reviewed and N=50 submitted

The Gate-5 continuation wake was valid and had not already been reconciled. Gate 6 remained durably
blocked at `19585b7`, while the bit-identical Gate-2 re-issue left Gate 5 dependency-ready. No other
lane had landed the predeclared two-stage replica implementation and no Gate-5 writer existed.

The new path leaves the hash-pinned nominal driver byte-identical. A CPU/ROOT stage enumerates each
complete ordered data, signal, and background inventory, draws coherent Poisson factors from seeds
50000–50049, and learns a fresh Stay-Positive target. A dedicated GPU adapter then reuses the exact
nominal annealed-training transaction while persisting both the training-subset and complete signal
factor streams. Artifacts and receipts are atomic and collision-protected; each training task depends
on the same-index target task through Slurm `aftercorr`.

Focused acceptance produced 25 passes and 4 environment skips; the direct P4 snapshot test passed
7/7, syntax/compile checks passed, and scheduler `--test-only` accepted the final request. The broad
repository suite was not represented as green: it had seven pre-existing environment/archive-binding
failures among 1075 passes, and its one stale snapshot was subsequently regenerated and passed
directly. The same preserved `agy-publication-redteam` UUID first returned BLOCK because the initial
adapter retained only subset signal factors. Commit `56d35af` added complete-factor persistence and
hash verification, after which the same verifier returned PASS.

Scheduler preflight exposed two site-policy details: direct `gpu_shared` is not an accepted request,
and requesting 64G with one GPU increases the billed CPU count beyond that queue's supported policy.
The final launcher requests `shared` plus one GPU and scheduler-default memory, which Slurm maps to
`gpu_shared` on `shared_gpu_ss11`. Failed target attempt `56857167` was cancelled before start when
its paired GPU submission was rejected; it ran for zero seconds and wrote no output.

The accepted launch uses frozen code checkout `b82ac63`. Target array `56857232_[0-49]` uses shared
CPU nodes, 16 requested CPUs, 64G, three hours, and at most ten concurrent tasks. Training array
`56857233_[0-49]` uses one A100, 32 CPUs, scheduler-default memory, eight hours, at most ten concurrent
tasks, and dependency `aftercorr:56857232`. Both were pending at the launch receipt. Terminal watches
`gate5-targets-56857232` and `gate5-training-56857233` are armed, so progress is now scheduler-driven
without LLM polling. No partial subset may be promoted and `C_stat` remains prohibited before 50/50.

## 2026-08-13 — Gate 6 retry design written; three of four member failures are robust, family still blocks

Lane B took Gate 6 (P5B.2, `C_ML`) and delivered a written design only:
`docs/orchestration/PLAN-20260813-gate6-cml-retry-design.md`. **Nothing was executed, no member was
selected or excluded, no `C_ML` was constructed, the central did not move, Leg 2 did not start, and no
retired margin is quoted.** All five prohibitions in the blocking receipt are honoured by every leg.

Two properties of the measurement were settled first, because both are cheaper than a training and
both change the fault description a retry has to explain.

The metric is not two quantities but one. `end_to_end_achieved_over_required` equals
`1 + push_dev_vs_R` to a worst deviation of `2.220e-16` over all 15 committed values, because `base`
cancels identically in `(m_push/base)/(R/base)` at `step1_increment_trajectory.py:236-257`. So the
metric is `mean_w_reco(push_k)/R`, and the predeclaration's requirement to record the signed field
"so a monotone one-sided drift can be distinguished from two-sided scatter" is satisfied trivially and
adds no witness (VL122, BEN-122). `R` is common to all five members — `step1_class_ratio` is built
from the full inventory and is subsample-invariant — so the five finals are directly comparable and
disagree about the pushed-weight normalization by `1.461867` (VL123).

The trajectory reads iterations 0 and 1 from best-epoch checkpoints and iteration 2 from `_final`,
because `ckpt()` prefers `_final` and only iteration 2 has one in the launcher's asserted 8-file
inventory. The monotonicity clause's second comparison therefore crosses a tier boundary whose gap the
harness's own docstring puts at ~1.3% (BEN-043) while warning it "would NOT survive it if the question
were a few-percent one". **Member 3's sole failing margin is `+0.001098` at exactly that step** — 12x
below the systematic in its own comparison — and it passes the `0.10` band by `0.057350`. Members 2
and 4 rise at the tier-clean step (`+0.010679`, `+0.048948`) and member 5's band excess is `+0.146523`,
so **three failures survive and the family verdict `BLOCK` at VL121 is unchanged** (VL124–VL125,
BEN-121). Two further clause defects are recorded rather than acted on: the zero-tolerance
monotonicity test penalises stationarity, which is what convergence looks like, and the `0.10` band's
provenance is a verdict-label cut on iteration 0 at `step1_increment_trajectory.py:299`, not a
tolerance derived for iteration 2.

The Gate-6 comparison used the declared within-process floor `1.26775e-04` for members trained in five
separate tasks on five nodes; the across-process floor is `1.62987e-02`, `128.6x` larger and known from
one pair (VL126). Member 3's total deviation is `2.617x` that floor and member 1's final is `1.185x`
it, so the interpretation currently rests on an `n=1` scale.

**OI-15's premise is false and was corrected in place.** `train_fullevent_nominal.py:335-336` already
declares `--estimator-seed` and `--subsample-seed` as independent flags,
`sbatch_pet_fullevent_ml_ensemble.sh:111` passes both, and its lines 114-128 re-read the realized
`seed_policy` off the persisted artifact and fail closed on a mismatch. No code gate has to be
re-issued to vary seeds, which removes the sequencing dependency the assignment flagged. The residual
is narrower: products do not persist host/GPU/process identity — the thing an across-process floor
exists to expose — and since the driver is `/files/driver/path` in the live Gate-4 code gate (19
pinned paths), the fix belongs in a new launcher's sidecar receipt copying
`train_fullevent_replica.py:347-353`, not in the pinned driver.

The design proposes three ordered legs: a zero-training tier calibration on the existing five members
(no gate re-issue — `step1_increment_trajectory.py` is not in the Gate-4 pin list, verified against
the receipt); four across-process draws of the fixed `(42,0)` policy to turn the `n=1` floor into
`n=5`; and a 2x2 crossed sub-factorial on `{42,46}x{0,4}` needing two new trainings, which is what
separates estimator initialization from training subsample. The executed design is diagonal, so those
two factors are perfectly confounded today and no analysis of these five members can attribute the
variance. Six new trainings, ~18 GPU-h, three waves each a single job under 12 h.

**One item needs Joseph's explicit sign-off and is called out as such:** the `(42,0)` floor
replication is the control the predeclaration already names verbatim, but gated behind "If all five
pass". The design asks to invert that precondition, on the grounds that the floor is the scale that
makes the numbers interpretable and the failure is when it is needed. That whether member 1 is both
the only converged member and the carrier of the adopted nominal's policy means anything is `n=1` — a
hypothesis this leg tests, not a finding.

Gate 4's estimator-arm disposition remains an independent user decision and blocks `C_ML` construction
regardless of how any leg comes out.

**`MANIFEST.tsv` is deliberately NOT updated here, and the reason is a trap worth naming.** It was
already out of date at `39b0021` before this change, so regenerating it looked like tidying. But
`generate_manifest.py` inventories the filesystem, and regenerating it from a `git worktree` **removed
37 rows** — `.DS_Store`, `__pycache__/*.pyc`, `.pytest_cache/`, `state/locks/*.lock`, `runs/*.log` —
untracked litter that exists in the main checkout and not in a fresh worktree. Committing that would
have deleted rows describing files that do exist, and the next lane regenerating from the main checkout
would flip them straight back. **The generated authority on what is LIVE is worktree-dependent through
untracked files; regenerate it only from the main checkout.** The new design file is therefore
unregistered, and is reachable instead from the five pointers added in this commit (this log, the
ledger block, `ND_OMNIFOLD_STATUS.md`, `OI-15`, and `BEN-121`).

**Lane attribution, and the instrument that does NOT work for it.** `git config --local` is the obvious
way to give a lane its own identity and it is wrong here: from a linked worktree `--local` resolves to
`$GIT_COMMON_DIR/config`, i.e. the **shared** `.git/config` of the main checkout, so it retargets the
identity for every worktree and the main checkout at once and four lanes doing it would fight over one
key. This lane set it, the key was gone within the hour, and the first commit was still authored
"Joseph Bailey". `git config --worktree` is the per-worktree instrument, but it requires
`extensions.worktreeConfig=true`, which is itself a repo-wide change. What this lane uses instead
touches no shared state at all: `git commit --author='Lane B (Gate 6) <josephrb@stanford.edu>'`
per commit, matching lane C's existing convention. Separates `git log --author` without configuring
anything (BEN-214).

## 2026-08-13 — Gate 5 (C_stat) first family reconciliation, lane C

Ownership of Gate 5 (P5B.1) moved to lane C this turn. First reconciliation pass over the live N=50
campaign, read-only: no job interrupted, modified or requeued, and nothing written into the cluster
code tree, which must stay clean at `b82ac63` while either array is live. The reconciler therefore ran
from `/pscratch/sd/j/josephrb/gate5-reconcile-lanec`, outside any git tree — an audit that had to
modify its own subject to run would not be one.

**Verdict `PARTIAL`, and `PARTIAL` is the deliverable.** 16 of 50 target receipts present, all 16
passing all 29 checks; 0 of 50 training receipts; no failures in either array. Nothing centred, nothing
summarised: Gate 5's own rule is that a missing replica invalidates the declared ensemble manifest, so
16 of 50 is not a 16-replica ensemble. `nd-unfolding/pet/reconcile_gate5_family.py` contains no
covariance code at all — deliberately, so it cannot be talked into producing a number from a partial
family — and two of its 50 tests assert that it *refuses*: identical targets must return `BLOCK`, and
2-of-3 must return `PARTIAL`.

**The finding that mattered was a selection effect, not an oversight.** Of the three coherent Poisson
streams, signal and background are replay-compared at the target stage and independently re-hashed at
the training stage, both fail-closed — good work. The **data** factors are persisted nowhere and
compared nowhere, because the loader's telemetry dict exposes no data equivalent, so nothing downstream
ever consumed them as an array and nothing had a reason to persist them. Verification coverage followed
the *data flow*; the data factors are what generate the measured-side variance `C_stat` exists to
quantify. The two orderings were opposite. Closed for this family by re-drawing all three streams
(16/16 match, data included); the structural fix is one key in a dict and is `OI-60`. `BEN-151`.

**The per-member training time was the number gating "when does the family land," and it was
unmeasured.** Still not a completed-member wall time (0 of 50 finished), so it was measured per *step*
against a loop structure that is enforced rather than assumed — `validate_artifact` fails closed unless
realized fits are exactly (2 base-LR, 4 annealed). Step 1 35:38, step 2 22:07, iteration 57:45, three
iterations plus measured 2:55 startup = **2:56:11 ≈ 2.94 h**, cross-checked against the log's own
reco/gen step counts (0.599 expected vs 0.621 measured). Family lands **~19:20–20:10 PDT**. Against
the predeclaration's `06:00:36`-per-training basis the ratio is **2.05**, confirming from the opposite
direction that that wall time covered two trainings — `BEN-152`. The predeclaration text is
deliberately not edited: its value is being fixed before the result, and no branch criterion references
cost.

**`BEN-150`**, found by mechanically re-deriving `R` from its published operands rather than by
suspicion: `sum_w_reco_pass_reco_raw` exists at two nesting levels holding different numbers, with the
outer `_raw` carrying the *scaled* value. Re-derive from the nested one and you get `1.124623` against
`1.1253110723074478` — 6.1e-4, which reads as precision noise. Second defect `BEN-077`'s
ingredients heuristic has caught with nobody suspecting one.

**A correction of this lane's own, bannered rather than replaced.** The deferral reason recorded at
`c249f78` for the `:112` repair — that editing the driver would break
`GATE5_EXPECTED_TRAIN_DRIVER_SHA` — is withdrawn. The launcher checks `git -C "$CODE_ROOT"` and hashes
a `$DRIVER` under `$CODE_ROOT`, never this repo, and three commits landed on `main` during the live
campaign and tripped nothing: a reason equally true of every commit in the window cannot be why this
one is withheld. Found by lane D, verified by the mediator, and verified here on the running code —
having already read those launcher lines earlier in the same pass and repeated the inherited
justification anyway, which is `BEN-148`'s shape in this lane's own hand. The actual constraints are
intact: the repair rides the next launch paired with a `CODE_ROOT` sync (`OI-57`), and nothing may be
pulled into `CODE_ROOT` while the array is live.

Artifacts: `docs/orchestration/state/gate5-family-reconciliation-20260813.json`; `BEN-150`/`151`/`152`
with long-form detail; `OI-60`/`OI-61` for the next launch.

## 2026-08-13 — Gate 5 target array terminal; independent 50-member replay prepared

The `gate5-targets-56857232` event was read once and validated. Fresh accounting names every logical
task `0-49`: all 50 are `COMPLETED/0:0`, with elapsed times `00:38:27-00:46:10`. All 50 stdout logs
bind `index=i` to seed `50000+i`; all 50 target arrays, target receipts, and both completion-marker
families are present. A same-turn structural reconciliation independently re-hashed the 50 targets and
returned 50/50 target checks passing. Its overall verdict is correctly `PARTIAL`, solely because only
five training receipts existed at that instant; that is not converted into a target PASS.

The terminal target gate now has a dedicated target-only mode. It independently hashes the immutable
9.9 GB source, re-draws and hashes every data/signal/background Poisson stream, binds each target and
both markers, enforces seeds and family distinctness, and requires the exact Gate-3/code pins plus the
learned-production Stay-Positive and `assert_refined_target_is_replica` evidence. Its 73 power tests
pass, including corruption and missing-member controls. A short collision-isolated CPU launcher was
added; it writes only a job-scoped validation report and cannot touch the live training namespaces.
Training array `56857233` and its existing terminal watch remain unchanged. No subset, `C_stat`,
Gate-6 action, retry, provider dispatch, reset credit, or worker replacement occurred.

Preflight receipt: `docs/orchestration/state/gate5-targets-terminal-preflight-56857232.json`.
The committed validator was then submitted as shared-CPU job `56872614` (8 GB, 20 minutes), initially
pending for priority, with job-scoped output and terminal watch `gate5-target-reconcile-56872614`.

### Validator attempt 1 failed before validation; immutable-root attempt 2 submitted

Job `56872614` started after its pending interval and failed in six seconds with `1:0`. Stdout was
empty; stderr contained only `[gate5-target-reconcile][FAIL] code HEAD drift`; neither report nor
marker exists. The validator did not read any campaign product. The defect was in orchestration: the
job pinned `ac540d5`, then the same worktree was necessarily advanced to `70be58a` by the receipt and
LIVE-STATE commits before Slurm scheduled it.

This is not retried unchanged. Job `56873858` uses new job-scoped outputs and a dedicated immutable
detached worktree at exact HEAD `70be58a` (validator `11e4f440…`, launcher `f031f17c…`). The receipt
writer remains in the separate reconciliation worktree, so documentation commits cannot move the code
root beneath the queued job. Its terminal watch is `gate5-target-reconcile-r2-56873858`; training
`56857233` and its existing watch remain untouched. No target science verdict, subset, `C_stat`,
Gate-6 action, reset credit, provider turn, or UUID change follows from the failed instrument.

### Gate 5 target stage promoted PASS at changed attempt 56873858

The changed validator completed `0:0` in `00:01:47` from clean immutable HEAD `70be58a`. Its empty
stderr, stdout, report, and completion marker were each read once. The marker binds the 168,512-byte
report at sha256 `388f5447…`; both say `TARGETS_COMPLETE_PASS`. The report independently re-hashed the
9,897,374,636-byte source as `fa6b3463…`, re-hashed all 50 targets, and re-drew all 150 coherent
data/signal/background factor streams. All 50 target hashes and each 50-member factor-hash family are
distinct; seeds are exactly 50000–50049; every target records 50 checks passed and zero failed; all 21
family checks pass. The exact pinned validator source has 48 target-check call sites, with its two
marker sites each executing twice, which accounts for the recorded 50 checks without an unnamed gap.
The 73 power tests pass against the same source hash.

The target stage is therefore **PROMOTED PASS**. This does not promote the full Gate-5 family or
construct `C_stat`: at the same-turn snapshot training `56857233` has 10 complete receipts/artifacts,
9 running tasks, 31 pending tasks, and no terminal errors. It remains the sole writer under watch
`gate5-training-56857233`. No subset, Gate-6/C_ML action, reset credit, provider dispatch, or UUID
change occurred. Canonical receipt:
`docs/orchestration/state/gate5-target-family-promotion-56873858.json`.
## 2026-08-13 14:55 PDT — Gate 5: target leg complete, throughput collapse diagnosed, lane C

**Target leg is DONE: 50 of 50 COMPLETED and all 50 pass all 29 reconciliation checks.** All 50 target
digests distinct, all three factor-hash families distinct across the family, none equal to the Gate-2
nominal, and 50 distinct `R` values straddling the nominal `1.1240802949941018` — which is independent
quantitative evidence the measured-side Poisson draw is live across the whole family, since a collapsed
draw would show identical values.

**The training leg met the reconciler for the first time and passed: 23 receipts, 23 passing all 11
checks**, including the binding that matters — each member's recorded target digest equals the digest
this tool re-hashed from disk for that same replica, so no member trained against another's target. And
the `NAME_MISMATCH` guard added at `69c577b` stayed **silent** on 23 correctly-named receipts, which is
the half that proves it is a check rather than an alarm.

**Per-member training time is now measured and the projection is retired.** Mean `3:00:30`, min
`2:58:21`, max `3:04:48`, n=23, from the receipts' own timers and consistent with `sacct` elapsed. The
per-step extrapolation made before any member finished gave `3:01:39` — 0.6% high, inside the measured
range. Quote `3:00:30`; the earlier 2.94 h and 3.03 h figures are superseded.

**Throughput collapsed from 10 concurrent to 2 at 12:34 PDT, and the campaign is not the cause.**
`shared_gpu_ss11` has essentially zero idle capacity — 1631 nodes `alloc` at `208768/0/0/208768`, with
the only idle CPUs on nodes that are draining, reserved, completing, or *planned* for jobs the scheduler
has already committed them to. Concurrency of 10 was achievable this morning and is not achievable now.

Three things were eliminated before landing there, and two of the eliminations are findings in their own
right. The array throttle is **not** binding — `Reason=JobArrayTaskLimit` on all 25 pending tasks while
2 run against `ArrayTaskThrottle=10`, a reason string naming a limit demonstrably not being reached,
which cost two lanes their first hypothesis (`BEN-153`). The QOS has no per-user running or TRES cap —
established only after two parties made two *different* off-by-one column misreads of the same
headerless `sacctmgr -nP` line within minutes, both landing on plausible-but-wrong causes (`BEN-154`).
The dependency is fully satisfied, all 50 targets being complete.

A latent second constraint is recorded but explicitly **not** claimed as the cause: QOS
`MaxJobsAccruePU=2` allows two priority-accrual slots per **user**, and `sprio` shows both held by lane
B's `g6_floor` array (`AGE=138`, `AGE=231`) while the Gate-5 array sits at `AGE=0`. Gate 5 still holds
the highest total priority of the three, so this is not what is costing it a start — but it cannot
improve its position with time while a competitor can. Per-*user*, so lane separation does not separate
it, and neither lane could have predicted contending here.

**The ETA is now reported as bounds rather than a time**, and the earlier `~19:49 vs ~20:40 PDT`
disagreement is moot: both figures assumed five clean waves of ten, and wave 3 only ever started five
members. (For the record, the 51-minute gap between them was real and explicable — `19:49` was when the
*first* member of wave 5 would finish and `20:40` the *last*, each slot staying ~49 min behind the first.)
Remaining 25 members at the measured `3:00:30` are **~7.5 h at 10 concurrent and ~37.6 h at 2**. Per-member
time is stable to ±3%; the unknown is entirely external cluster occupancy, which this lane cannot predict
and will not pretend to. Walltime is not at risk — 8 h requested against ~3 h used, and queue delay does
not consume it.

Nothing was resubmitted, requeued, held, cancelled or modified; `GATE5_CODE_ROOT` untouched with 25
members still to exec from it; no `C_stat` constructed, because 23 of 50 is not a 23-replica ensemble.
Holding lane B's array would free both accrual slots and is **routed to its owner as a recommendation,
not taken** — it is B's job, and it would not fix partition saturation, which is the present blocker and
is nobody's here to fix.

## 2026-08-13 — Gate 6 Leg F first wave: 2 of 4 new draws in, branch 1 already excluded, NO verdict

Submission provenance for array `56863958` landed late and out of order because the session that
submitted it died mid-campaign; the launch receipt was recovered from its worktree and committed
unmodified at `847034a`. This entry closes the chronology gap and then reports the first wave. The
predeclaration, launcher and tests landed at `ef020b9` **before** submission, which is the part that
matters — the rule was fixed before any draw existed.

**What ran.** `sbatch --array=2-5%2 sbatch_pet_fullevent_floor_replicate_array.sh` → `56863958`,
submitted 06:22 PDT at `--nice=10000`. Joseph authorized inverting the precondition (*"Yes let B do
it"*), so the control the member-trajectory predeclaration already named verbatim — *"five total
across-process draws of the fixed member-1 policy `(42,0)`, including four new runs with persisted
execution-environment identity"* — runs on the **failing** branch instead of the passing one. Draw 1
is the existing `member_1` artifact, reused and **not** retrained (`v[2] = 0.9806897311812962`); the
launcher refuses draw 1 by name with the reason in the message.

**This is a measurement, not a retry, and Gate 6 is not unblocked by any outcome.** Every draw uses
the identical seed pair `(42,0)`; only process, node and GPU vary, which is why it proceeds under
`do_not_retry_unchanged`. All five prohibitions at `19585b7` remain live, and the launcher writes them
into every draw's sidecar with `c_ml_construction_allowed: false` and `is_a_retry: false`, so the
commit record cannot later be read as the block having softened. `C_ML` needs a separate decision from
Joseph, and Gate 4's estimator-arm disposition blocks construction independently regardless.

**Tasks 2 and 3 `COMPLETED 0:0`** in `03:15:09` and `03:15:26`, both on `nid008264`. Tasks 4 and 5 are
still queued. **All eight predeclared validity clauses PASS on both new draws** — `R` exactly
`1.1240802949941018`, `mc_indices` array-equal to member 1's across all 2,000,000 rows, realized
policy `(42,0)/niter 3/epochs 8/2e6 rows/batch 512` read off the artifact rather than off the launch
command, `GATE_AB_PASSED` with bit-exact MC-index and truth-normalization identity, reproduction gate
`rel_dev` exactly `0.0` on all three quantities, 8 `.weights.h5` in each draw's own `w_nominal`, and
execution identity persisted (host, GPU uuid, both HEADs, all bound digests).

**The rule was applied by code, not by hand.** `nd-unfolding/pet/gate6_floor_statistics.py`
(`637ee33d…`) is the executable form of the predeclaration: 52 tests, 16/16 mutations caught, module
restored byte-identical afterwards, and **written and mutation-tested while draws 4 and 5 were still
queued** so the thresholds could not be tuned to the data. It exits `3` (INCOMPLETE) here rather than
emitting a verdict, and refuses to verdict on fewer than five valid draws — a test asserts that
refusal names `do_not_select_passing_subset`, because that property is the one most likely to be
quietly relaxed later under schedule pressure. Numbers at VL127–VL129; receipt at
`docs/orchestration/state/gate6-floor-replication-partial-56863958.json`.

**Branch 1 is already unreachable, and that is a deduction from the frozen rule rather than a new
one.** `max−min` is non-decreasing when draws are added and all three present draws are valid, so the
partial `F_range[2] = 0.0523993868023519` is a lower bound on the final value and already exceeds the
frozen `0.05`. This moves no threshold, selects no subset — it is valid precisely because nothing was
excluded — and reaches no verdict. `FLOOR_LARGE_TRAJECTORY_IS_PROCESS_DETERMINED` needs a further
`0.1216` of spread from draws 4 or 5; two of the five committed members would supply it and three
would not, so `FLOOR_INTERMEDIATE` is live and would attribute nothing.

**The finding the predeclaration fixed no rule for, reported because it bears on the question and on
Leg X.** The categorical trajectory *label* is not reproducible at fixed seed. Member 1 and draw 2 are
`UNDER_ACHIEVES_AT_ITER0_SAME_SIGN`; **draw 3, same `(42,0)`, is `BROKEN_AT_ITER0` with
`end_to_end_sign_is_wrong=true`**, and its `v[0] = 0.8400494065800533` falls between members 4
(`0.8747948243043495`) and 5 (`0.7614411106789466`) — the two members whose identical label was read
as seed sensitivity. At iteration 0 the same-seed spread is already `89.6%` of the five-member spread
from three draws. **This is iteration 0 and the verdict is defined at iteration 2 only**, so it is an
observation and not the answer; letting it become the answer is exactly the after-the-fact rule change
the predeclaration exists to prevent. It is recorded, not acted on.

**Consequence for Leg X, reported before submission rather than after, which is what Joseph asked
for.** The `{42,46}×{0,4}` 2×2 is authorized and is **not** submitted. Two of its four cells exist
(`(42,0)` = member 1, `(46,4)` = member 5) so only `(42,4)` and `(46,0)` would run. With one run per
cell there is no replication, so at iteration 0 its main effects would be indistinguishable from
process noise at `89.6%` of the member spread. At iteration 2 the same-seed spread is `15.1%`, so a
2×2 read **at iteration 2 only, with the floor quoted alongside** is still informative. Either the 2×2
gets replication or its readout is restricted; which one, and whether to spend the GPU-hours, goes to
Joseph rather than being assumed. The floor completes first — Lane B's sequencing, which Joseph
explicitly declined to lift.

**A claim in the predeclaration is now false, and the document is deliberately not edited.** It states
Gate 5's pending tasks are held by their own array cap and dependency *"not by resource scarcity — so
Gate 5's throughput is bounded at ten concurrent regardless of this submission."* That was measured
true at submission (10 `g5train` + 10 `g5targ` running). At 14:53 PDT Gate 5 runs **2** of its 10-task
cap with `56857232` fully `COMPLETED` and no dependency outstanding, so the cap is not binding.
Measured: `shared_gpu_ss11` has 128 running and 127 pending across all users; **14 pending jobs outrank
Gate 5** at priority `67679` and **94 outrank this leg** at `57910`, only one of which is ours. Both
arrays are priority-starved on a contended partition, and `Reason=JobArrayTaskLimit` is displayed on
both while the cap is not the operative constraint. A predeclaration that gets edited after the fact is
worth nothing, so the correction lives here and in the receipt, not in the document.

**Credit where it belongs on the reason string:** lane C got there first and independently, as BEN-153
with a long-form finding, from `sinfo` (1631 nodes `alloc`, zero idle CPUs). My instance is a second
array — Leg F at **0** running against a `%2` cap — refuted by a different measurement, queue position.
Two arrays and two independent checks make it a class, which is the only thing my row (BEN-126) adds;
the analysis is lane C's.

**This leg has cost Gate 5 nothing and the starvation was reported rather than worked around.**
`--nice=10000` keeps this array exactly 10,000 below Gate 5 at every scheduling decision (measured
`57910` against `67689`/`67705`), and it has had zero tasks running since 14:16 PDT while Gate 5 has
had two. The self-cap has not been raised, no task has been resubmitted, and `--nice` has not been
lowered. `GATE5_CODE_ROOT` (`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`) was not read,
written, synced or cleaned, and a test asserts the launcher never references it. The cluster repo was
not synced either — `gate6_floor_statistics.py` was `scp`'d as a single file and verified byte-identical
on both sides. **The reason first written here — *"the cluster's `fullevent_fps_dataloader.py` is
modified-but-uncommitted and load-bearing for the live Gate-5 array"* — is FALSE and is corrected in the
2026-08-13 16:0x entry below.** The `scp`-not-pull conclusion is unchanged; its actual binding reason is
`OI-57`'s HEAD check.

**Two tooling traps, both filed.** `sacct -j 56863958` lists tasks 2, 3 and 5 but **not** task 4,
whose pending element Slurm split under a new `JobIDRaw` (`56883015`) — a resume guard enumerating
from `sacct` would treat it as nonexistent (BEN-125). And three boundary tests written to sit *exactly*
on `0.05` and `0.10` all silently landed just outside: `1.05-1.0` is `0.050000000000000044` and
`abs(1.10-1)` is `0.10000000000000009`, so `<=` versus `<` is only testable at the predicate, not
through the data path (BEN-124). The same class of thing bit the frozen threshold: `0.1740029887300910`
is the 16-decimal *rendering* of `0.5 × S_range[2]`, one float step above the exact half-range, so the
transcription check compares at 16 decimals and reports the `5.55e-17` delta rather than demanding bit
equality — which would have failed on a correctly transcribed number, and did, on the first run.

**Not done, deliberately.** Leg 0 (checkpoint-tier calibration) is unauthorized. No Gate-6 member has
been re-verdicted, including member 3, whose sole failing margin is `+0.001098` at the tier-crossing
step. No subset selected, no central moved, no `C_ML` constructed, no reset credit consumed. Watch
`gate6-floor-replication-56863958` stays armed and carries the full rule, both thresholds, all eight
validity clauses, the four non-establishments and all five prohibitions, so a successor that reads only
the event still cannot over-conclude.
### 2026-08-13 15:12 PDT — deployment parity: "committed" is not "running" (lane C, BEN-156, OI-64)

Second instance of one class in a single day. A peer extended `reconcile_gate5_family.py` at `ac540d5`;
the copy actually executing, at `/pscratch/sd/j/josephrb/gate5-reconcile-lanec/`, still held `69c577b`'s
logic. `OI-57`'s `GATE5_CODE_ROOT` was the first instance, and **both were caught by attention rather
than by mechanism.** A run against the stale reconciler would not have crashed: it would have written a
correctly-schema'd family artifact — right field names, `tool_sha256` faithfully recording the stale
hash — computed from superseded checks, with nothing in the output saying so.

**The reflexive defence is itself the defect.** *"Is the running file's content in the repo?"* returns
**true** on the stale copy, because the stale copy was committed. So the check committed here reports
`STALE_BUT_COMMITTED` as a state of its own, kept apart from `UNCOMMITTED` because the two have
different repairs (re-deploy vs find who hand-edited scratch), and from `IN_ODB_UNREACHABLE`, because
`git cat-file -e` succeeds on a blob that `git add` created and no commit ever contained. Exit 2 means
*could not look*; exit 3 means *looked and found drift* — separated so a mistyped path cannot read as a
clean bill of health.

New: `nd-unfolding/pet/verify_executing_copy_is_committed.py` with 20 tests, every check exercised in
**both** directions. Power-tested on the real artifact rather than only on fixtures: fed
`git show 69c577b:...`, whose sha256 `e536540d` is the exact `tool_sha256` recorded in
`state/gate5-throughput-collapse-20260813.json`, i.e. **the file that was executing at 14:55 today** →
`STALE_BUT_COMMITTED`, exit 3. The other direction, against every copy that exists on scratch → **3 of
3 `CURRENT`, exit 0.** The copies were located by `find`, not from memory, and there are **three**, two
of them peers' — a report naming only mine would have been incomplete in the direction that matters.

Two corrections inside this same pass, both recorded rather than quietly absorbed. (1) The helper was
first named `commits_containing_blob` claiming *"commits whose tree contains this blob"*; the live
negative control listed `ac540d5`, which **removed** that content, because `--find-object` searches
diffs, not trees. Renamed `commits_whose_diff_touches_blob` — `BEN-149`'s shape inside a tool written
to catch that class, caught by reading output against a name. (2) Two zeros that were about my search:
an **inferred** receipt path returned 0 (real root read out of the previous run's own artifact, where
there are 23) and two guessed reconciler paths returned ABSENT (an unbounded `find` located three).
Neither zero was reported as anything.

Campaign state, measured this turn: targets `56857232` 50/50 COMPLETED; training `56857233` at 25
PENDING / 2 RUNNING via `squeue -r`; 23 training receipts and 23 weights `.npz` on disk against 50
target receipts; a basename census returns those three names and nothing else, so the `NAME_MISMATCH`
surface is empty by measurement. Verdict **`PARTIAL`**, unchanged from 14:55, `C_stat` null. The
reconciler was deliberately **not** re-run: the receipt count has not moved, so a re-run reproduces the
15:02 artifact at the cost of ~23 × 49M-variate replays. Tasks 23 and 24 started 12:34:53 and land
~15:35 PDT at the measured `3:00:30`.

Lane B's array was **not** held. The mediator's arithmetic settles it: Gate 5 leads by ~9,760 priority
points while accrual runs at ~2 points/minute, so closing that gap takes on the order of three days and
freeing the accrual slots buys Gate 5 nothing measurable. Nothing on scratch was modified, re-deployed
or cleaned; all three copies were already `CURRENT`.

**The check has no caller yet — `OI-64`, stated rather than implied.** An unwired check is a check
nobody runs, which is how this class got two instances in one day.

## 2026-08-13 — Gate 6 Leg X: readout fixed at iteration 2 by Joseph, predeclared and NOT submitted

Lane B put a design question to Joseph after Leg F's first wave and he answered it: *"Sure, do iteration
2."* So Leg X — the `{42,46}×{0,4}` 2×2 — keeps **one run per cell, no replication, read at iteration 2
only.** The predeclaration, launcher and tests are committed **before either new cell exists and before
anything is submitted**, which is the same discipline Leg F used and the reason its numbers are usable.

**Why the restriction exists, on the face of the record, because a reader in six months will otherwise
see an unreplicated 2×2 and assume nobody noticed.** Leg F measured the across-process spread at one
fixed seed pair. As a fraction of the five-member spread it is **89.6%** at iteration 0, 49.4% at
iteration 1 and **15.1%** at iteration 2. At iteration 0 process variation alone accounts for ~90% of
what the five members showed, so a 2×2 read there would report seed main effects indistinguishable from
process noise — **and would report them with the same apparent precision as a real result**, which is
the failure mode rather than the absence of one. Iteration 2 is also where the Gate-6 band applies and
where Leg F's verdict is defined. **The restriction is what makes the design sound, not a limitation of
it.** The honest half: nothing licenses an iteration-0 or -1 claim from Leg X, and the launcher
deliberately does **not** filter those values out of the receipt, because suppressing them would hide
the caveat instead of stating it.

**The reference scale is the whole reason the floor runs first, and it is now arithmetic rather than
assertion.** Every cell is one draw, so `Var(E) = ¼(4σ²) = σ²` — each main effect and the interaction
has standard error **exactly** the across-process `σ`, which a 2×2 with one run per cell cannot supply
from inside itself. `σ̂ = F_sd[2]` from the completed Leg F carries **4 degrees of freedom**, so the
threshold is `t_{0.975,4} = 2.7764451051977987 × σ̂` — the multiplier is fixed now and `σ̂` is substituted
later. A gaussian `1.96` would be optimistic here and a round `2` unmotivated; both are the kind of
number that gets chosen after seeing the data. **One effect carries the verdict** (the estimator-seed
main effect, named before any value exists because it is the axis Joseph's question names); the
subsample main effect and the interaction are reported only. A null is reported as
`ESTIMATOR_INIT_EFFECT_NOT_RESOLVED_AT_MDE` **with its MDE published**, never as "no effect" — BEN-213
is exactly this trap, and pre-registration is not power.

**Sequencing is enforced by code, not by memory.** The launcher refuses to start unless a Leg F result
receipt reports `n=5`, zero invalid draws, a terminal `FLOOR_*` verdict and a positive `F_sd[2]` — before
`mkdir`, before the writer lock, before the module load, before any GPU work. Six rejection cases are
tested (absent, `n<5`, an invalid draw at `n=5`, non-terminal verdict, missing `σ`, zero `σ`) plus an
acceptance case as the negative control, without which all six would pass on a gate that refuses
everything. The obvious workaround is named in the failure message. *"Floor first"* is Joseph's standing
instruction and Lane B's own argument, and `CLAUDE.md` is explicit that the executable form of a rule
beats the written one.

**Clause 5 had to change shape from Leg F's, and the change is a positive control.** Leg F could demand
`mc_indices` equality with member 1 because every draw shared `subsample_seed=0`. Leg X cannot: half its
cells sit at `subsample_seed=4`, so equality is required **by level** — a cell must match the existing
member at its own level and must **differ** from the other. Measured this turn on the two existing
cells: **`1,999,982` of `2,000,000` rows differ**, so the axis the design exists to separate genuinely
moves. A 2×2 whose subsample axis does not move is not a 2×2, and now that is a check rather than a hope.

**Two defects this work found in itself.** The first version of the launcher ran `mkdir -p` **before**
the sequencing gate; its own battery caught that the gate then never executed off-cluster at all, and
that a refused submission would still have created an empty cell directory. The ordering is now asserted
as `gate < mkdir < lock < module < train`. And mutation testing found **two gaps in my own battery**: a
mutation replacing only the *first* of the launcher's two `t(4)` occurrences — the one in the failure
message, leaving the arithmetic correct — passed a test that asserted mere presence; and a mutation
deleting the operator-facing ineligibility notice passed a test that asserted the word `INELIGIBLE`,
which also appears in a sidecar key. **A half-substituted constant and a word that appears twice are the
same defect class**: presence is not the property you meant to assert. Both tests now count occurrences
and anchor on the specific line. Final: 32 tests, 18/18 mutations caught, launcher byte-identical after.

**Gate 6 is not unblocked and this is not a step toward `C_ML`.** All five prohibitions at `19585b7`
remain live. Leg X answers seed-versus-estimator — a question the executed diagonal table
`(42,0)…(46,4)` makes *unanswerable*, because estimator init and subsample are perfectly confounded
there. `C_ML` needs a separate decision from Joseph that he has not made, and Gate 4's estimator-arm
disposition blocks construction independently. No member is retrained: cells `(42,0)` and `(46,4)` are
`member_1` and `member_5`, read-only, and both a range guard and an independent anti-diagonal guard
refuse to train them. **Nothing is submitted** — the floor is not closed, and `shared_gpu_ss11` is
saturated, so queueing Leg X early to gain position would compete with Lane B's own floor and with
Gate 5. Authorization receipt:
`docs/orchestration/state/gate6-legx-readout-authorization-20260813.json`.

Floor progress at 15:24 PDT: task 4 **started** on `nid008332` — a different node from tasks 2 and 3,
which both ran on `nid008264`, so the across-node coverage the first wave lacked is now being filled.
Task 5 remains queued.

## 2026-08-13 16:0x — correction: nothing on scratch is uncommitted. `git status` said "modified" on a file that is byte-current

**Right conclusion, wrong reason, and the wrong reason is the dangerous half.** Twice today Lane B wrote
that the cluster's `fullevent_fps_dataloader.py` is *"modified-but-uncommitted and load-bearing for the
live Gate-5 array."* The mediator declined to relay that unverified and measured it; Lane B then measured
it independently rather than take the correction on trust. **Both measurements agree and Lane B's original
claim is false.** A future lane reading "uncommitted work on purgeable scratch" would go looking for work
to rescue and find none — which is why this is corrected in place rather than left as a footnote.

Measured across the three checkouts this leg touches, one command, this turn:

| checkout | HEAD | `status --porcelain` | working file | **HEAD blob** |
|---|---|---|---|---|
| `gate6traj-reconcile-56847059` = `GATE5_CODE_ROOT` | `b82ac63` | 1 line, an untracked log | `e1402370…` | **`e1402370…`** |
| `MINERvA-OmniFold` (the science repo) | `683bdcc` | 748 lines, `M` on the loader `+38/−5` | `e1402370…` | **`57f33f87…`** |
| `gate6-reconcile-56834281` (diagnostics) | `4d96acf` | 1 line, an untracked json | `e1402370…` | **`e1402370…`** |

**`GATE5_CODE_ROOT` is clean and Gate 5 is not training against uncommitted code.** The dirty tree is a
different one, and the decisive measurement is its **HEAD blob**: `57f33f87…` is the *old* version while
the working file is `e1402370…`, which `git show origin/main:` confirms is the **committed** current
version, last touched at `6a4b903`. So `git status` reports `M` because that tree's HEAD predates the
Gate-5 replica-architecture change, **not** because the file is uncommitted. The state is
`STALE_BUT_COMMITTED`. Nothing is at risk on scratch and there is no lost work.

**This is a live independent instance of lane C's BEN-156, arriving from the opposite direction, and it
confirms C's design was not over-engineering.** C built a four-state model because *"is it committed?"*
returns **true** on a stale executing file. This is the mirror: **`git status` returns "modified" on a
file that is byte-identical to `origin/main`.** A two-state view misleads in both directions, and C's
classifier gets this right where the reflexive check does not. Filed as BEN-127, pointing at C's long form.

**The `scp`-not-`git pull` conclusion is unchanged; the binding reason is `OI-57`, verified in source this
turn.** `sbatch_gate5_replica_train_array.sh` reads
`[[ "$(git -C "$CODE_ROOT" rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || die "code HEAD drift"`, so a pull in
`CODE_ROOT` fails **every remaining Gate-5 task closed**. Three digest checks follow it — replica driver,
pinned nominal driver, and `EXPECTED_LOADER_SHA` — so the guard is layered rather than single. **Scope
honestly stated: only the loader was characterized.** The science repo's other 747 porcelain entries were
not, so "do not pull there either" stands on precaution, not on measurement.

**And the reason this never threatened Leg F or Leg X: both launchers bind CONTENT, not HEAD.** They
`sha256sum` the loader against `e1402370…` and die on mismatch, which is exactly why a stale HEAD in the
science repo they train from cannot affect them — the property Gate-2 provenance already relies on
(`assert_target_provenance` binds by content, not receipt identity). The four-state confusion is
invisible to a digest check, which is the argument for using one.

**Floor progress, and the mediator is right that this is more than a caveat.** Tasks 2 and 3 both ran on
`nid008264`, so **the first wave was not measuring across-node variance at all** — which is the thing an
*across-process* floor exists to expose. Lane B recorded that as an honest caveat; the sharper statement
is that the first wave could not have been the answer even at `n=5`. Task 4 is running on `nid008332` and
is filling it rather than having it assumed.
### 2026-08-13 ~15:50 PDT — codex's audit of the Gate-5 reconciler: seven items, all confirmed (lane C, BEN-157, OI-65)

**Promotion is BLOCKED and I accept the block.** Codex's independent read-only audit of
`reconcile_gate5_family.py` — a tool this lane wrote — reports seven defects. **Every one confirmed;
none refuted.** Five reproduced by running the tool on synthetic families built from its own fixtures,
two by reading code whose behaviour is not in doubt. Three carry qualifications and every qualification
makes the finding **sharper**, not weaker. Nothing repaired: part 7 is pending, and a fix aimed at a
milestone risks the wrong line.

**The tool whose only job is to refuse a partial family passes on zero members.** `:528` is
`--n type=int` with no floor and every completeness comparison is against it: `--n 0` on an empty
directory returns **rc=0 and the exact `FAMILY_COMPLETE_PASS`**, and a real 3-member family passes at
`--n 3` while being `PARTIAL` at `--n 50` — **the artifacts unchanged, only the caller's claim about
how many there should be.** The file's own `:7` states the principle its parser does not enforce.

**And my tests do not merely miss it; they are written in its idiom.** The complete-family test uses
`n=3`, the clean-name test `n=2`, and `test_partial_family_is_PARTIAL_and_never_PASS` builds 2 and runs
`n=3` — proving 2/3 ≠ 3/3, never 49/50 ≠ a *fixed* 50. **No test anywhere asserts `n` must be 50.**

**The single sharpest line in the audit: `completion_marker_valid` is never read.** Grep returns two
hits in the whole tree — the producer writing it at `train_fullevent_replica.py:358`, and **my own
fixture copying it** at `test_reconcile_gate5_family.py:194`. Zero in the reconciler. The receipt
asserts its own marker validity and nothing checks the assertion, so **a receipt declaring itself
invalid passes.**

**Yesterday's `NAME_MISMATCH` guard is routed around structurally.** The stray scan is reachable only
inside `if not os.path.exists(rec)`, so a receipt at the *correct* name never enters it: rename the
weights, update the receipt, and you get an exact pass with `name_mismatch=0` and the canonical
filename absent from disk. **The guard catches a file that disagrees with the launcher; it cannot catch
a receipt that agrees with a wrong file.** The guard itself is still sound — clean names stay silent,
no false positive found — it is aimed one branch too narrowly. The asymmetry is inside one file I
wrote: the target stage has the anchor at `:324`, the training stage has none.

**The verifier checks a claim where the launcher checks content.** The producer records **three**
digests (`:367-374`), the launcher checks all three plus HEAD (`:41-44`), and the reconciler checks
`head_at_runtime` — **itself a claim in the receipt, not a measurement** — plus one loader sha. "The
launcher checks them" is not a defence: `BEN-156`, filed this morning in this same tool, established
that the executing copy can differ from the committed one, which is precisely the class an independent
verifier exists for.

**Required inputs are optional and their checks evaporate.** Null `R` and its operands, with the
marker re-stamped so nothing else fires: `rc=0`, exact pass, **43 passed / 0 failed**,
`r_derivation: {"R_recorded": null}`. Four checks vanished and nothing reported their absence — while
`--skip-replay`, fifteen lines away, already implements the correct behaviour by downgrading the
verdict to a named suffix. **I built the right mechanism for one optional check and applied it to none
of the others.**

**And the name-pin test never opens the launcher.** `test_expected_names_match_the_launcher` asserts
the constants against **string literals duplicated in the test file**, under a docstring promising it
pins them to the Slurm-captured batch script. **I described these to a peer as "constants pinned by a
test to the launcher." That was false and is withdrawn here** — the test pins the constants to a copy
of themselves, `BEN-149` exactly, inside the test written to prevent the filename defect I fixed at
`69c577b`.

**One invariant, not seven patches:** the reconciler derives every quantity it checks from the
filesystem at canonical paths and from constants pinned in the tool, **never from the receipt's account
of itself** — with the corollary that a required input which is absent **fails closed or downgrades the
verdict**, and never silently removes its own check. Lane B reached the same sentence from provenance:
both launchers **bind content, not HEAD**. B's HEAD-blob measurement also confirmed this morning's
four-state classifier **from the direction it was not built for** — `git status` saying "modified" on a
file byte-identical to `origin/main`, where mine says `STALE_BUT_COMMITTED` on one `git status` calls
clean.

**What is not invalidated:** 50 target receipts and 24 training receipts are real and passed their
checks, and every campaign run used the default `n=50` and correctly reported `PARTIAL`. **What is
blocked:** using this tool to *declare* promotability, because at a genuine 50/50 its exact pass is
indistinguishable **in the artifact** from one emitted at a caller-chosen `n`, or on receipt-only
trainings, or with the R checks never run. Not a wrong answer — **an unfalsifiable one**, the condition
this tool exists to prevent elsewhere. **I will not run a promotion pass on the current tool even at
50/50.**

**Four of my own probes failed first, and the fourth is the one to keep.** The fixture writes markers
with no `mtime`; my first `mtime` attempt landed in the same second as `mark_complete`; without `--out`
the tool prints a condensed summary with no per-replica rows, so my probe printed `check failures:
NONE` — **true of an empty dict, not of the run**; and my first null-R probe changed the receipt's byte
size, so a marker check fired and returned `BLOCK`, **which would have read as refuting item 6**. I
caught that, re-stamped, re-ran, and confirmed. Codex flagged the same confound independently and we
agree — the coherent run was already done. Had I sent the confounded result it would have been
`BEN-207` aimed at my own refutation.

**The uncomfortable part, stated plainly: I could not have found this by auditing myself, because my
tests share the tool's blind spot** — same idiom, same fixtures, same reasoning. That is a stronger
argument for an independent lane than any process document.

Campaign measured this turn: `squeue -r` 25 PENDING / 1 RUNNING, **24 training receipts** of 50, 50/50
targets. `PARTIAL`, `C_stat` null. Nothing re-run against the campaign, nothing re-deployed, no code or
test modified, `GATE5_CODE_ROOT` untouched.

### 2026-08-13 ~16:10 PDT — BEN-157 R1 landed: the declared inventory is pinned, not passed (lane C)

Codex's part 7 closed the audit against commit `6d3660f` rather than against a message, and the repair
was authorized. **R1 only.** R2/R3/R4 remain unapplied and **promotion remains BLOCKED**.

`DECLARED_INVENTORY = 50` is now pinned in the tool. The number was **already** declared in the file —
`SEED_POLICY` reads `gate5-cstat-n50-v1` — and simply unenforced, so an import-time assertion **binds
the two** rather than introducing a second source of truth: change one without the other and it is a
hard error, not a silently different gate. `--n` survives as an **assertion only**, checked before any
artifact is read, and a disagreeing value writes **no report at all** — a caller who asked the wrong
question must not receive a well-formed artifact measured against their own premise, because that
artifact is what a promotion decision would later rest on.

Measured both directions on the real tool. **Before:** `--n 0` on an empty root → rc=0 and the exact
`FAMILY_COMPLETE_PASS`. **After:** rc=**3**, stderr naming the pinned value and the policy string, no
report. And the honest run still reports honestly — no `--n`, empty root → rc=**2**, `PARTIAL`,
`targets_present 0 want 50`. A check that rejected every `--n` would also have "rejected" the wrong
ones, so both the pinned value and the omitted flag were confirmed to still work.

**Usage is exit 3, not 2, and this corrected my own proposal.** I had proposed 2, copying the sibling
`verify_executing_copy_is_committed.py`. That would have been wrong here: `2` already meant *the family
is not complete*, so reusing it would have collapsed **"could not look"** into **"looked and found it
short"** — the exact distinction I insisted on when writing the sibling. The two tools now use opposite
assignments, documented at both sites, because preserving this tool's contract with its launcher
outranks cosmetic consistency between tools.

**The test half is the load-bearing part and it landed in the same commit.** The suite did not merely
miss the defect — it was written in the defect's idiom: complete-family at `n=3`, clean-name at `n=2`,
and `test_partial_family_is_PARTIAL_and_never_PASS` building 2 and running `--n 3`, which proves
2/3 ≠ 3/3 and says nothing about 49/50 against a **fixed** 50. `_run_main` no longer takes a size; it
runs as production does, with no `--n`. Every test meaning "complete" builds `DECLARED_INVENTORY`, every
test meaning "short" builds fewer, **and there is no `--n` left to move.** Three small fixtures were
deliberately left small — they call `reconcile_target`/`reconcile_training` directly and never reach
`main()`, so they are unit-level rather than the idiom. **73 → 90 tests in this file, 110 across both
suites.** New coverage includes the defect in its *general* form (`test_a_short_family_has_NO_n_that_
makes_it_pass` over sizes 0/1/49, not merely `--n 0`), that a bad `--n` against a **nonexistent** root
is still usage rather than `PARTIAL`, and that usage and incomplete carry different exit codes.

**Two defects I introduced and caught, both recorded rather than quietly fixed.** A mechanical
`args.n` → `DECLARED_INVENTORY` rewrite also hit **`args.nominal_target_sha`**, because `args.n` is its
prefix — `BEN-032`'s shape, a substring filter over a set that is not defined by substrings; caught by
grepping the result instead of trusting the replace count. And `_run_main` returned the report by
opening a fixed path, so `rep is None` meant *"no file there"* rather than *"this run wrote none"* — in
a test that runs twice, the second run, **the one asserted to write nothing**, read the first run's
report. Four tests failed and were right to. Fixed by deleting the output path *before* running, so the
file's presence afterwards is evidence about this run: the write-condition rule, inside the helper
written to check for it.

**R1 deliberately creates deployment drift, and the receipt records it as a falsifiable prediction.**
All three deployed copies read `CURRENT` before this commit, because HEAD's blob was still the
pre-repair version; after it lands they must read `STALE_BUT_COMMITTED` with exit 3, and if they read
`CURRENT` the parity tool is broken. Nothing was deployed — that is a separate, verified step, two of
the three copies are unowned (`OI-64`), and a re-deploy must also update
`GATE5_RECON_EXPECTED_VALIDATOR_SHA`, which pins the validator by content and will therefore refuse a
stale-or-unannounced copy. New tool sha `85ca74f3…`, superseding `11e4f440…`.

**Not fixed by R1:** receipt-supplied artifact paths with no canonical anchor, no training-stage
`.done`, `completion_marker_valid` never read, marker `mtime` omitted, one of three driver digests
compared, checks that evaporate when their input is absent, and the name-pin test asserting against a
copy of its own string. R1 closes the **headline** — the tool can now tell a complete family from an
empty one — **not the class.**

Campaign measured this turn: `squeue -r` 24 PENDING / 1 RUNNING, **25 training receipts** of 50 — half
the family has landed. `PARTIAL`, `C_stat` null. Nothing run against the campaign, nothing deployed,
`GATE5_CODE_ROOT` untouched.

### 2026-08-13 ~16:45 PDT — an archived Gate-2 receipt marked in its directory but not in itself (lane C, BEN-158)

Routed from lane A. `gate2/final/superseded-20260813-pre-gate5-rerun/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`
sat inside a `superseded-*` directory with **`status: PASS`**. The supersession was recorded in the
directory name and in `NOTE.md` and **never in the file**, so anything reading the file rather than the
path read it as live — and a reader grepping `PASS` is doing precisely that. A's Gate-4 defect was the
**mirror image**: a successor that named its predecessor while the predecessor was never marked. Same
failure, opposite half.

A's template used verbatim rather than reinvented: `status: SUPERSEDED` + `superseded_by`/`_on`/`_why`,
`code` → `code_at_issue`, digests preserved — and **asserted, not claimed**: the conversion refuses to
write unless the digest multiset is byte-identical (13 values, unchanged). `verdict` deliberately left
alone; it states what that run found, which is still true, while `status` is the live-vs-retired axis.
`test_archived_gate2_receipts_hold_no_live_bindings` now passes, 6 of 6 in that file.

**The half that was not on the ticket, and the reason this got a finding.** `VALIDATION_LEDGER.md`
`VL89` certifies the receipt at `336e8e27`. Measured across every version that has existed: the
archived copy hashed **`23935993` on its first commit** — the `sha256` → `sha256_at_issue` rename
happened *as part of* the archiving, in the same commit that created the directory. **The archive was
never byte-identical to the certified digest**, twelve hours before I touched it; my marking moved it
again to `c959a3a8`. And `NOTE.md` publishes that digest in a table headed *"so the bit-identity claim
can be checked against these rather than against a memory of them"* — inviting a reader to compare it
against the neighbouring file, which would show a mismatch and read as corruption.

**VL89 is not wrong.** It certifies the 08-05 re-issued receipt and those bytes remain recoverable at
`8a9d22c` — verified rather than asserted, `git show … | sha256sum` reproduces `336e8e27` exactly. What
was wrong is that nothing on disk said so. **No digit of any digest was changed:** VL89's *quantity*
cell now names which receipt, which commit, and that no file on disk carries it; `NOTE.md` carries the
caveat and the recovery command.

**The durable tension, stated because it will recur: a retirement convention that annotates a file in
place cannot coexist with a ledger digest that certifies that file's bytes** — and it must not be the
digest that gives. A's template never hit this because `docs/orchestration/state/*.json` is not
digest-certified; Gate-2 runtime receipts are. Re-digesting the ledger row was rejected outright as the
antipattern every hash gate here exists to catch. The general form is the day's recurring lesson: **an
archive's provenance has to travel in the artifact, not in its neighbourhood** — and a directory name, a
sibling `NOTE.md`, and a successor's commit message are all neighbourhood.

Campaign untouched by any of this: 25 of 50 training receipts, `PARTIAL`, `C_stat` null, R2/R3/R4
unapplied and promotion still blocked.

### 2026-08-13 ~17:20 PDT — BEN-157 R2: derive from the filesystem, never from the receipt's account of itself (lane C)

One treatment for audit items 2–5 rather than four patches, which is the mediator's point that seven
patches would leave an eighth. **R3 and R4 remain unapplied; promotion remains BLOCKED.**

**Item 3.** The training stage hashed `art['path']` straight from the receipt, compared against
nothing. It now hashes the canonical `GATE5_REPLICA_WEIGHTS.npz` and adds `artifact_path_is_canonical`,
testing the receipt's path claim against the launcher's name. Codex's attack — rename the weights,
update the receipt to match — produced an **exact pass** before and **fails** now. The asymmetry was
inside one file I wrote: the target stage already had this anchor at `:324`.

**Item 2.** The target stage read two `.done` sentinels; the training stage read none. It now checks
the weights marker and the receipt's own.

**Item 4.** The hand-rolled `done_*` size comparison is replaced by a **call** to
`atomic_write.is_complete`, which compares size *and* mtime — so divergence becomes impossible rather
than merely fixed once. One hand-rolled check is retained because it adds what the primitive cannot do:
`is_complete` derives the marker path from the subject, so **a marker copied from another replica with
matching size and mtime would satisfy it.** The import is **fail-loud**: this file deploys to scratch as
a single script, and the tempting *"if atomic_write is missing, do the size-only check"* fallback **is**
the defect, so it exits 3 naming the file to copy.

**Item 5.** The tool read `head_at_runtime` — itself a *claim* in the receipt, not a measurement — plus
one loader sha, while the producer records **three** digests and the launcher checks all three. Now all
three are required present, re-hashed from their recorded paths where those resolve, and required
**constant across the family**. Constancy rather than a pin because the driver digests **float by
design** (OI-57/OI-58): a pin matches every member equally and so cannot catch a driver that changed
*mid-flight*, which is the actual exposure. Named `code_<role>_matches_disk`, deliberately not
`..._is_the_right_driver` — it proves the file at a recorded path matches its record, nothing more.

**One check I drafted and deleted before running anything.** Codex reported that a receipt declaring
itself invalid passes. True, but the sharper form is that **no receipt from this producer can declare
itself invalid** — `train_fullevent_replica.py:358` writes the Python literal `True`. Requiring it would
be a check that cannot fail, which is the class this whole repair is about. `weights_marker_is_complete`
is the measurement it gestures at. Filed as `OI-66`.

**And a check of mine that could not fail, caught by its own power test.** I put the training code
digests at the row's top level; `constant_across_family` reads `row['invariants']`, so **every member
resolved to `None`, producing one group — indistinguishable from unanimous agreement.** The invariant
certified the family while measuring nothing. `test_a_driver_that_changed_MID_FAMILY_is_caught` failed
because only the per-member check fired. Had I written the positive half alone this would have shipped
green. The wider fix: `constant_across_family` now reports whether the path **resolved**, and both loops
assert it — a latent trap that covered the twelve pre-existing target invariants too, not just mine.

**Verified against the live family before landing, because fixtures prove logic and not
deployability.** If any new assumption disagreed with production, R2 would fail all 50 members and block
the campaign it exists to certify. Read-only: real `artifact.path` **is** canonical; both training
markers **do** exist in production (the producer always wrote them — item 2 was a verifier gap, not a
producer gap); all three code paths resolve inside `CODE_ROOT`, so the disk re-hash runs for all three
including the loader; and **`is_complete` is false for 0 of 150 real subjects**, so delegating to the
primitive does not reject the live family. Had any of those been false the right move was to hold R2,
not weaken it.

**Fixtures had three defects that hid these items**, repaired in the same commit: markers hand-written
with no `mtime` (so the mtime axis was never exercised and the primitive rejected fixture markers for
unrelated reasons), **no training `.done` at all** — codex's part-7 observation — and `code` digests with
no `path`, so the disk re-hash would have silently skipped on every fixture.

**90 → 100 tests.** Full suite 1297 passed / 4 failed, down from 7: all three hash-binding tests are
green after lane A's Gate-4 retirement and this lane's Gate-2 one. The remaining four are pre-existing
and outside my diff (shell-file count 354→357, a tensorflow config-gate leak, an absent `/pscratch`
path, a temp-path assertion).

**New deployment constraint created by R2:** `atomic_write.py` must be copied beside the reconciler.
That belongs in the re-deployment step rather than being discovered during it (`OI-64`).

Campaign this turn: `squeue -r` 17 PENDING / **8 RUNNING** — concurrency recovered from 2 as the
partition freed up, which is external and keeps the ETA bounds rather than a time. 25 receipts of 50,
`PARTIAL`, `C_stat` null. Nothing deployed, `CODE_ROOT` untouched, campaign not re-run.

### 2026-08-13 ~18:05 PDT — BEN-157 R3 and R4: all seven audit items repaired (lane C)

**R3 — a weaker run can no longer emit a stronger verdict.** `--skip-replay` already did this right,
downgrading to a named suffix. `--source-npz` and `--nominal-target-sha` did not: absent, their checks
simply never ran and the verdict was full strength. **Two treatments, because they are two different
things.** A missing *tool input* is the caller's choice, so it downgrades and names itself
(`SOURCE_UNHASHED`, `NOMINAL_UNCHECKED`). A missing *required receipt field* is a defect in the
artifact, so it **fails the member** — `R_published_by_receipt` and `R_operand_published[...]` for the
four operands. Conflating them would tell the reader the **tool** ran weakly when in fact the
**receipt** is incomplete, pointing the next person at the wrong file. The axes are also reported as
`weakened_axes` and `is_full_strength`, so nobody has to parse a verdict string to learn what is
missing.

**What R3 exposed in my own suite: six tests asserted the full-strength verdict while passing neither
optional input.** The suite was certifying as full-strength exactly the runs whose evidence was
incomplete. They now assert the honest string, and a new test proves the bare `FAMILY_COMPLETE_PASS`
is still **reachable** — downgrading absent evidence is only correct if full strength remains
attainable, otherwise the strongest verdict becomes unreachable and readers learn to ignore the suffix.

**R4 — the name-pin test opens the launcher.** It had asserted the constants against string literals
duplicated a few lines above, under a docstring promising it pinned them to the Slurm-captured batch
script; it could not have failed if the launcher changed, which is the one thing it existed to catch,
and I had described it to a peer as doing the opposite. It now reads
`sbatch_gate5_replica_train_array.sh`, loose about shell syntax and strict about the name. **And it is
power-tested**: a tampered copy of the launcher text must be rejected by the same parse, because a
launcher-reading check that cannot fail is no better than the literal it replaced — the missing half
was the entire original defect.

**Verified against the live family before landing, because R3's fail-closed checks are the risky
kind.** Had any of the five required R fields been absent or differently named in production, R3 would
have failed all 50 target members and blocked the campaign it exists to certify. Measured read-only:
**all 50 target receipts publish `step1_class_ratio` and all four operands; members missing any
required field: NONE.**

One consequence worth stating: the armed watch command passes `--nominal-target-sha` but **not**
`--source-npz`, so a future live run will correctly report `FAMILY_COMPLETE_PASS_SOURCE_UNHASHED`
rather than the bare string. That is intended. The source identity has exactly one independent check
and it lives in `state/gate5-source-npz-verified-20260813.json`, not in the replica artifacts (OI-58).

**All seven items are now closed in code, 73 → 104 tests.** Three residuals are **recorded, not
closed**: `is_complete`'s whole-second `mtime` resolution (changing it means changing a primitive with
other callers); no receipt is hashed against anything, so a receipt's only integrity evidence is its
marker; and `artifact.completion_marker_valid` is a hardcoded literal, deliberately not read.

**Promotion is still not authorised, and the reason is not the code.** The repaired tool has never run
against the campaign, because that requires deploying it — a separate verified step that must now also
copy `atomic_write.py`. Whoever advances Gate 5 needs a 50/50 `FAMILY_COMPLETE_PASS` from the
**deployed** repaired tool with its `weakened_axes` recorded, and I would not accept my own PASS from a
copy whose parity had not been checked.

Campaign this turn: `squeue -r` 15 PENDING / **10 RUNNING** — concurrency back to the full array
throttle. 25 receipts of 50, no failures in either array, `PARTIAL`, `C_stat` null.

### 2026-08-13 ~18:40 PDT — the repaired reconciler is deployed, parity measured, and exercised live (lane C)

Deployment authorized with five conditions, all honoured. The standard applied is my own sentence
quoted back at me: **a 50/50 pass from a copy whose parity has not been checked is not evidence.**

**Parity measured in both directions in one turn.** BEFORE: the reconciler read
`STALE_BUT_COMMITTED` (head blob `1d33a229` vs executing `590affaf`) and `atomic_write.py` read
**MISSING** — exit 3. AFTER: **2 of 2 CURRENT**, exit 0. The BEFORE state is stated rather than
implied, because a deployment whose prior state you cannot name is one whose effect you cannot
attribute. Cluster and local `sha256sum` agree for both files independently of the parity tool's
blob-oid path.

**The fail-loud import was tested on the real deployment, deliberately.** The reconciler went over
FIRST with `atomic_write.py` absent, and running it against the live campaign root returned **exit 3,
no report**, naming the missing module and the file to copy. R2 made that dependency hard and refuses
to fall back to the weaker size-only marker check; until now that refusal existed only as an
unexercised branch and a comment. This is its negative control, on the actual deployment.

**First live exercise of R1–R4 — a diagnostic, not a promotion pass.** `PARTIAL`, exit 2. **50 targets
present and all 50 passing; 25 trainings present and all 25 passing**, with 10 correctly reported
`IN_PROGRESS` and 15 `NOT_STARTED`. The only family failure is `trainings_present 25 != 50`.

**And I checked that the new checks RAN rather than merely not failing**, because "nothing failed" is
compatible with "nothing ran" — today's own R2 draft shipped an invariant that resolved to `None` for
every member and therefore could not fail. **54 checks per target row, uniform** (was 47 before the
repair — R3's five R-field checks and R2's marker changes account for it); 24 per training row; **six
training invariants, each resolving to a single group, with zero `invariant_path_resolves` failures.**
All three driver digests agree across all 25 members. `weakened_axes` correctly reads
`['REPLAY_SKIPPED', 'SOURCE_UNHASHED']` and `is_full_strength` false, so the run does not claim more
than it did.

**A scare I checked and dropped, which is worth more here than a clean bill of health.** All 25
replicas record `nominal_driver_unmodified = 91144bee`, while `p3f-pet-gate4-launch-code-gate-20260812.json`
pins the nominal driver at `5fda80df`. Read alone that says the Gate-5 family trained against a driver
Gate 4 never certified — and the field is literally named `_unmodified`. **It is not true:** the 20260812
gate is `SUPERSEDED`, and its successor pins `91144bee`, exactly what the replicas ran. What stopped
the false report was **lane A's retirement marking** — the predecessor said `SUPERSEDED`, which is why I
looked for a successor instead of treating its pin as live. Same shape as today's `BEN-158` from the
reader's side, and direct evidence that marking a predecessor pays off in a way no test measures.

**No new `BEN` filed and block `230-239` deliberately NOT claimed.** `FINDINGS.md`'s own rule is to
write a block into the table in the same commit as the first filing into it. This deployment produced
no failure — the fail-loud import, the parity flip and the check counts are all positive results.
Claiming a ten-block to hold nothing would make the table describe an allocation no finding justifies,
which is the shape the block system exists to prevent. I will take it at my next real finding.

**What a promotion pass will still require:** 50 of 50, `FAMILY_COMPLETE_PASS` with `weakened_axes ==
[]` and `is_full_strength` true — so no `--skip-replay` and `--source-npz` supplied — **and parity
re-checked at that moment**, because the repo may move again and a pass from a copy verified hours
earlier is the same defect one step removed.

`GATE5_CODE_ROOT` untouched (three digests were READ through the receipts' recorded paths, nothing
written). The two unowned non-lane-C copies untouched. Campaign: 25 COMPLETED / 10 RUNNING / 15
PENDING, no failures, `PARTIAL`, `C_stat` null.

### 2026-08-14 ~21:00 PDT(-1) — OI-60 answered: the data factors are recoverable, and the loader's own telemetry ties them (lane C)

Routed with a deadline attached, because the array is still writing members. **Answer: (b) — not
persisted as an array, exactly recoverable, nothing being lost, no hold warranted.** Read-only
throughout; `GATE5_CODE_ROOT` untouched.

**First, a correction to the task as relayed.** It described the stream as *"the Gate-5 data-factor
stream (signal and background factors)"*. That is backwards: signal and background are the two streams
that **are** handled — replay-compared at the target stage and re-hashed at the training stage. The
**data** stream is the one with no array-compare anywhere, and it is the one generating `C_stat`'s
measured-side variance. That inversion is `BEN-151`'s whole point, and answering the question as phrased
would have reported the already-verified streams as the exposure and missed the real one.

**Where it is computed:** `fullevent_fps_dataloader.py:621`, inside `coherent_bootstrap_factors`
(`:614-625`), called at `:1321`.

**Where it is written — established by listing a completed member's files, not by reading code.**
`replica_00` contains exactly the two receipts and their `.done` markers, `GATE5_REPLICA_WEIGHTS.npz`
and its marker, and 11 `w_nominal` checkpoints. **There is no factor array of any kind.** What *is*
written is the hash: `build_fullevent_replica_target.py:284`, plus the seed, all three inventory sizes,
and the hash contract — every input the recovery needs.

**Recovery exhibited on real data, all 50 members, run locally off the cluster tree** so a match cannot
be an artefact of reading the producing code's own state. 50/50 data hashes reproduce. Signal (49.2M
variates) and background reproduce too — positive controls proving the whole contract reproduces rather
than one stream coinciding; had they failed, my numpy's PCG64 would have been the suspect. Negative
controls: seed+1 and n_data−1 both fail to match.

**And the part that goes beyond recovery, which is the real content of OI-60.** BEN-151 recorded that
re-hashing cannot prove the *loader applied* those factors, and called that unclosable without
loader-side persistence. **That was too pessimistic.** At `:948-951` the loader computes
`n_data_eff = float(df.sum())` from the array it actually received, shape-guarded to `(n_data_rows,)`,
and `:971` builds `R` from it — and both `n_data_effective` and `R` are persisted. **Measured:
`sum(canonical draw) == recorded n_data_effective` exactly, 50 of 50.**

**What that proves and what it does not:** the applied array had the same **length** and the same
**sum** as the canonical draw. It does **not** prove array identity — a permutation, or any change
conserving the total, would pass. And the limit is **demonstrated rather than argued**: only 49 of the
50 `n_data_effective` values are distinct. `replica_03` and `replica_08` share `4114512` while their
`data_factor_sha256` differ, so there are two real members in this family the sum cannot separate and
the hash can. Corroboration: the spread is 9101 rows against `sqrt(4116128) = 2029`, and the expected
range of 50 draws is ~4.5 sd ≈ 9100 — what independent Poisson draws should give.

**Consequence for the 35 completed members: nothing is lost, nothing needs re-running, and this is not
a decision for Joseph tonight.** OI-60's first clause stands and its second is withdrawn — *"cannot be
verified by any stage"* is false, since the reconciler has been re-drawing and comparing this hash
since the first family pass. What remains genuinely open is array identity of the loader's applied
factors, which needs a producer-side change and should ride the next launch with OI-57/OI-58 rather
than being retrofitted mid-family. Row narrowed accordingly.

Campaign: 35 receipts of 50, 5 PENDING / 10 RUNNING, no failures, `PARTIAL`, `C_stat` null.

### 2026-08-14 ~21:30 PDT(-1) — the Gate-5 promotion evidence is now IN the repo, and its four claims re-derive from the copy (lane C)

Codex's advisory item 2, routed urgent and correctly so: **scratch turnover is the only failure here
that cannot be undone.** The 168,512-byte report carried the 50 per-target check lists, the 150 replay
values, the distinct-hash counts and the empty failure lists that `TARGETS_COMPLETE_PASS` rests on — its
digest was bound in **four** places and the object was in none of them. That is `BEN-077`'s
unfalsifiable-receipt shape with a purge timer attached.

**Rescued into `state/gate5-target-promotion-evidence-56873858/`, original filenames preserved**, and
**all three digests re-verified after the copy**: report `388f5447…` (168,512 B, equal to the bound
value), marker `4d7bce7e…`, stdout `41dd3d08…`. A copy that did not hash to `388f5447` would have been
worthless, so that is stated as a measurement rather than as a step performed.

**All four claims re-derived from the committed copy alone**, no cluster access: 50/50 PASS; **150
replay values, 150 of 150 equal to the recorded hash**; data/signal/background hashes 50/50 distinct
each, target digests 50/50 distinct; failure lists empty at both family and row level. Independent
cross-check: the report's `data_factor_sha256_REDRAWN` for `replica_00` equals the value I re-derived
locally off-cluster in this session's OI-60 work — two independent redraws, one contract.

**My first extraction got claim 2 wrong and it is recorded.** I looked for boolean flags, found 50, and
printed `DERIVED 150: False`. The 150 are three *redrawn hashes* per member, not booleans. Wrong
extraction, not a defect in the promotion — and the third time today that a zero of mine was a statement
about my search rather than about the tree.

**A caveat found while re-deriving, and it is the useful part.** The promotion ran on the **pre-repair**
validator (`11e4f440`, before R1–R4). Five of the seven defects cannot reach it — `--n` was passed as 50
over 50 real rows, items 2/3/5 are training-stage receipt-trust defects and this run is `stage=target`,
item 7 is test-only. **Two could:** the marker check compared size but not `mtime`, and
`no_replica_target_equals_the_nominal_target` is **absent from the report's check names**, so
`--nominal-target-sha` was never supplied and under R3 this run would read
`TARGETS_COMPLETE_PASS_NOMINAL_UNCHECKED`. (`--source-npz` *was* supplied — the 9.9 GB source was
independently re-hashed to `fa6b3463…`.)

**Both gaps are already closed by measurement rather than argument:** the repaired tool was run over the
same 50 targets earlier this session *with* the nominal sha supplied, and all 50 passed at **54 checks
per row against the promotion run's 50**, including markers now delegated to `atomic_write.is_complete`
(size **and** mtime). So the target promotion is not invalidated and now rests on stronger evidence than
it originally did.

**Item 4, the stale preflight, reconciled.** Top-level verdict read `..._INDEPENDENT_REPLAY_PENDING`
while the receipt's own `changed_attempt_2` recorded job `56873858` COMPLETED with
`TARGETS_COMPLETE_PASS`. Advanced to `..._INDEPENDENT_REPLAY_COMPLETE` with the original string
preserved verbatim in `verdict_at_issue` — a receipt that silently rewrites its own history is worse
than one that is stale — and the advance is guarded by an assertion that attempt 2 really is a completed
pass. Same class as `BEN-158`: state recorded in one place and not the other.

**`RUNS.tsv:296` routed, not edited.** *"all data/signal/background factors independently verified"* is
accurate for signal and background, accurate for the data **hash**, and overstated for the loader's
**use** of the data factors, where the evidence is length and sum via `n_data_effective` rather than
array identity. Recommended narrowing recorded in the receipt; it is a durable cross-lane ledger row and
editing it unilaterally is the overreach I declined on the OI-id collision.

`GATE5_CODE_ROOT` untouched; scratch originals left in place; three reads and no writes to the cluster.
Campaign: 35 receipts of 50, `PARTIAL`, `C_stat` null.
## 2026-08-13 21:3x — `C_syst` scoped: 124 endpoints, ~402 GPU-h at k=1, and the blocker is a code gate

Written while Gate 6 Leg F's draw 5 sits queued behind our **own** Gate-5 array. Draws 2, 3 and 4 are
`COMPLETED 0:0` (`03:15:09` / `03:15:26` / `03:12:35`; `nid008264`, `nid008264`, **`nid008332`**), so the
across-node coverage the first wave lacked is now in. **Design only: nothing submitted, no cluster state
mutated, and the floor verdict work is deliberately NOT started** — that runs when draw 5 lands.

**`C_syst` was the only P5B component where the campaign could not state what it would take.** It now can.
`docs/orchestration/SCOPING-20260813-csyst-joint-nuisance-retraining.md`.

**The inventory is 124 endpoints**, from the code rather than from prose: 12 knob bands
(`pet_systematics_5d.py:42-43`) × 2 `±1σ` endpoints each = 24, plus **100** PPFX flux universes
(`N_FLUX` at `unified_throw.py:52`, gate `require_truth_ratio_bank(..., expected_flux=100)`). The 10
lateral endpoints are a separate component and are excluded from that count.

**The crux resolves against us, and the repo already contained the measurement.** `unified_throw.py:19-22`
calls the 124 *"VERTICAL (weight-only)"* bands — which is a statement about the **event loop**, not a
frozen-map exemption. Weight-only means cloud membership is unchanged, so verticals need no new event loop,
no per-endpoint merge and none of `C_lateral`'s ~1.1 TB. It does not mean the learned map is unchanged: in
OmniFold step 1 the classifier separates data from MC-reco *using the MC weights*, so changing the prior
changes the map. And `products/pet/bkgsub/pet_joint_vs_additive_retrain.json` measures it — over the 5
universes with both operands stored, **`‖Δ‖` is comparable to `‖s‖` and LARGER for `MaCCQE`**
(`1.28115e-38` vs `1.02987e-38`). **So `C_syst` does not reweight away; it is the schedule-dominating
component.** Recoil numbers, therefore not quotable — the transferable part is the structure.

**Cost, with the operands so it can be contradicted.** Per-retrain wall measured this turn from `sacct`:
Gate 5 `10866.7 s = 3.0185 h` mean over **n=35** COMPLETED (min `2:58:48`, max `3:08:01`); Leg F's draws,
which include the three diagnostic stages a `C_syst` endpoint also needs, `11663.3 s = 3.2398 h`. Using
the latter: `124 × 3.2398 = 401.7 GPU-h`, `40.2 h` wall at the observed concurrency of 10 — and **that
division is arithmetic, not a schedule**, which today's queue proves. Flux alone is `324 GPU-h`, **81%** of
the total. `k` replicates per endpoint multiply everything.

**The `k` question is where the cost is actually decided, and there is a nearly free way to settle it.**
Phase 7's `null` identity-retrain control gives `‖Δ_null‖ = 2.3124629464350753e-41` against a 5-band joint
`√tr` of `1.7315713222649896e-38` — `749×`, so `k=1` looks ample. But that control is within-process, and
`VL126` already measured within-vs-across at `128.6×`. **Illustration, explicitly not a derivation** (the
two are in different units and are not commensurable): at that inflation the weakest band's margin falls
from `177×` to `1.38×` — not resolved. **Gate 6 Leg F's five draws are exactly the across-process
identity-retrain control this needs, in the full-event representation, and each has already written a
complete weights npz** — extracting the xsec vector from them would settle `k` for **zero additional GPU
time**. That is outside Leg F's predeclared rule, so it is listed as a decision and **not done.**

**The structural blocker, and it is why this component had no design rather than a partial one.**
`train_fullevent_nominal.py` cannot retrain on a universe prior — its whole CLI was read, and there is
**no `--universe`, no truth-ratio bank, no per-event reweight.** `phase7_retrain_universe.py` has all of
it and is recoil-era (`niter=2`, recoil inputs, produces the **increment** not the joint shift, extraction
*"uses the nominal cloud"*). And the obvious fix is gated: verified against the live receipt,
`state/p3f-pet-gate4-launch-code-gate-20260813.json` is `PASS_CODE_ONLY`, `superseded_by: null`, and its
`files.driver.path` **is** `train_fullevent_nominal.py` at `91144bee…` — the digest Leg F and Leg X pin. So
adding a universe axis is a **code-gate re-issue**, not an edit. **A decision, not an engineering task.**

**Two citation defects found in my own draft, both by checking rather than by review.** The `≥100 GPU-h`
and `170–250` figures are at `OPEN_ITEMS-ARCHIVE-2026-08.md:696`, **not** the live `OPEN_ITEMS.md` the
determination cites — **I repeated the stale pointer before checking it**, and caught it only by grepping
for the *number* instead of the claim. That is a third variant of the citation-rot class: unlike BEN-215
(commit verified as a string) and BEN-216 (file never existed), here **both the file and the number still
exist — just not together**, because the item was archived. Filed as BEN-128. I did **not** fix the
determination's pointer: that file is another lane's, and editing a peer's document to correct my reading
of it is the BEN-204 shape. Separately I dropped an "861 pins" figure carried from memory and replaced it
with the live receipt's measured **19 `files` entries**, plus the note that
`verify_hash_bindings.collect()` harvests any `path`+`sha256` dict so the blast radius exceeds the 19.

**Seven things the scoping states it cannot establish**, each as "needs X" rather than as a hedge — chiefly
the across-process noise floor in xsec units, the retraining response for the 7 unmeasured knob bands and
99 of 100 flux universes, and whether any nuisance qualifies for the frozen-map exception at all. **No
nuisance has such a proof today.**

Gate 6 remains **BLOCKED** at `19585b7`, five prohibitions live. Leg X remains authorized and unsubmitted.
Cause 5 remains **OPEN** — measuring what a construction would cost is not building it.

**Addendum, same turn — a near-miss that belongs in the record rather than in a finding.** Before pulling,
my tree showed **two** Gate-4 launch-code-gate receipts, `20260812` and `20260813`, *both* with
`superseded_by: null`, binding `train_fullevent_nominal.py` to **different** digests (`5fda80df…` vs
`91144bee…`). That would have made "the live receipt" ambiguous and undercut the scoping's §4.1. It was
**already repaired on `origin/main`, 25 commits ahead of me** — `20260812` now carries `superseded_by`,
`files: 0` and `files_at_issue: 17` with `5fda80df…` preserved verbatim, which is exactly the repair the
pre-commit hook's own text prescribes (*"re-issue or retire the owning receipt … every digest preserved
verbatim"*). Merging origin/main took the verifier from `*** BINDINGS BROKEN ***` (2 mismatches, the other
being lane C's reconciler, also already fixed) to `ALL BINDINGS INTACT`, with no action from me.

Two mechanisms combined to make a stale snapshot look like a live defect, and the mediator's note names
the second: the whole-tree binding arm was added to the hook on 2026-08-13, and **the hook FILE is the
main checkout's while the CHECKS it runs are the worktree's own copy** (the dispatcher `cd`s to
`git rev-parse --show-toplevel`). So a newly added arm is **inert in a worktree until that worktree
pulls** — which is why my two earlier commits printed "4 checks passed" and this one hit six. **Pull
before reporting a tree-wide condition.** One command, and it is the difference between a finding and a
false alarm. Filed as BEN-129, which closes Lane B's block `100-129`.

Also adopted this turn: lane A's OI-* block table at `e4db2e2`. **Lane B's OI block is `80-89`.** No OI id
was allocated by this work — OI-3 is an existing row and was edited in place, not renumbered.

### 2026-08-14 — codex's mutation test: my prediction was wrong, and the fix is the only check with power over the applied data factor (lane C, BEN-230)

Codex asked whether any stage's validation has power over the data factor or is merely comparing the
builder to itself. **Codex was right and I had committed the opposite prediction to a receipt
beforehand**, which is the only reason the error is on the record rather than quietly absorbed.

**What I predicted:** a sum-changing mutation *"WILL be caught by `n_data_effective` and by `R`"`.
**Measured: it is not.** A `+137`-count mutation of the LOADER-applied factor, propagated exactly as the
loader propagates it (`n_data_effective` → numerator → `R` → normalisation) with the builder's
`data_factor_sha256` untouched, **passed 57 of 57 checks and shifted `R` by 13.6%.**

**Why.** The loader computes `R` *from* `n_data_effective` (`dataloader:971`), so a mutated factor gives
a mutated `n_data_effective` and a mutated `R` that re-derive from each other exactly. The R check
confirms arithmetic the mutation already made self-consistent. `n_data_effective` existed in the tool
only as an **operand** of that derivation, compared to nothing. **I reasoned from where a quantity comes
from to whether it is checked — different questions, and the gap between them is where this class
lives.**

**The fix ties it outside the receipt's own arithmetic.** The loader computes `n_data_effective` at
`:951` as `float(df.sum())` from the array it actually received, shape-guarded at `:949`, and it is
persisted — so comparing it to the sum of *our* redraw is **the only check anywhere with power over the
loader's applied data factor**. The same mutation now **FAILS, on that check alone**, and a test asserts
the R checks still do not fire so the power is not misattributed.

**Proves length and sum, not identity.** A permutation still passes — pinned as a **test** rather than
left as a caveat, and demonstrated live: `replica_03` and `replica_08` share `n_data_effective =
4114512` with differing `data_factor_sha256`. Closing identity is producer-side and stays with OI-60.

**A third fixture defect exposed.** The new check failed on **every honest fixture**, 55 of 108 tests:
`_build_target_receipt` hardcoded `n_data_effective = 1010.0` against `N_DATA = 1000` — internally
consistent and unrelated to the fixture's own draw. **Every fixture already modelled the state the
mutation creates, so the suite could not have caught this class.** Fixed by deriving it as the loader
does. 108 tests pass.

**Live impact: none, and that is measured, not assumed.** `sum(canonical draw) == n_data_effective` holds
for all 50 target receipts (measured earlier tonight for OI-60), which is exactly what the new check
compares — so it passes the live family. The deployed copy is now stale by this commit and must be
re-synced before any promotion run, per the standing rule.

**Block `230-239` taken** and written into the table in this same commit as `BEN-230`, its first filing;
`130-159` is exhausted. Rule 2 and the allocate-forward paragraph were pointing at `230-239` and now
point at `240-249`, updated by the lane that took the block, as rule 4 requires.

**The generalisation:** *a receipt whose numbers all re-derive is evidence of arithmetic, not of
measurement.* Publishing operands lets a reader recompute a verdict; it does not make it falsifiable.
Falsifiability needs an anchor the producer did not also compute. That is `BEN-077` one turn further on.

Campaign: 36 receipts of 50, 4 PENDING / 10 RUNNING, no failures, `PARTIAL`, `C_stat` null.

### 2026-08-14 08:44 UTC — Gate-5 training terminal preflight; independent artifact gate added

Wake `evt-gate5-training-56857233` was valid and had no prior terminal-family receipt. Same-turn
accounting independently found all 50 logical tasks `COMPLETED/0:0` (first end 2026-08-13 07:42 UTC,
last end 2026-08-14 01:33 UTC), agreeing with the event. The runtime namespace contains all 50
training receipts, weights NPZs, both marker families, and both task-log families. This is terminal
inventory evidence, not yet family promotion and not a `C_stat` result.

The already repaired/deployed family reconciler independently replays the three Poisson streams and
checks receipt/file/marker/code continuity, but its training leg does not open the NPZ content.
`validate_gate5_training_artifacts.py` closes that separate evidence layer: exact fixed policy and
independently regenerated 2M-row subsample, 2 base plus 4 annealed optimizer fits, full canonical
signal factor and exact subset restriction, full ordered background factor, source/target/identity
bindings, all task logs/accounting, and collision-isolated namespaces. Six focused power/contract
tests pass; the batch wrapper is syntax-clean and fail-closes on immutable HEAD and three code hashes.

The route is intentionally a short CPU batch rather than a login-node run: it redraws 50 complete
factor streams and reads 50 compressed training artifacts, while no interactive allocation exists.
It writes job-scoped reports and a promotion marker only if both validators pass. It contains no
extraction or covariance code. No subset, `C_stat`, Gate-6/C_ML action, provider dispatch, reset credit,
or UUID change occurred. Exact preflight:
`../docs/orchestration/state/gate5-training-terminal-preflight-56857233.json`.

**Launch addendum, 08:46 UTC.** The validation route landed and pushed at `987a45c`; job `56933831`
was submitted from that immutable detached worktree with exact HEAD and three code-hash guards. It is
pending on CPU resources with a 30-minute wall, writes only job-scoped validation outputs, and has
terminal watch `gate5-family-validate-56933831` armed. The absence of a live interactive allocation
made this short durable batch the collision-free route; no duplicate validator or replica writer was
created. Receipt: `../docs/orchestration/state/gate5-family-validator-active-56933831.json`.
### 2026-08-14 ~01:45 PDT — GATE 5 FAMILY IS 50/50 AND THE VERDICT IS `FAMILY_COMPLETE_PASS` AT FULL STRENGTH (lane C)

Both arrays terminal. `56857232` 50 COMPLETED, `56857233` 50 COMPLETED, **queue fully drained, zero
failures at any point in either array.** 50 target receipts, 50 training receipts, 50 weights `.npz`,
every artifact carrying its `.done` marker.

**Parity verified in the SAME TURN as the run, before it, not hours earlier** — 2 of 2 `CURRENT`, exit 0,
repo `d2bc94b`, and `git log HEAD..origin/main` empty over both deployed paths. *A 50/50 pass from a copy
whose parity was not checked is not evidence* is my own sentence and it applies to my own output.

**The run was full strength: no `--skip-replay`, `--source-npz` supplied.** The three-stream re-draw
actually ran — ~49M signal variates per member across 50 members. Exit 0, stderr empty.

```
verdict            FAMILY_COMPLETE_PASS        <-- BARE, no suffix
weakened_axes      []
is_full_strength   True
replay_performed   True
targets            50 PRESENT / 50 PASS        58 checks per row
trainings          50 PRESENT / 50 PASS        24 checks per row
name mismatches    0
family failures    NONE
C_stat             null
```

`58` checks per target row is worth reading against history: **50** at the pre-repair promotion, **54**
after R1–R4 with replay skipped, **58** with the replay performed. The gate the family passed tonight is
materially stronger than the one it would have passed this morning.

**Evidence rescued off scratch immediately**, because tonight's own lesson was a promotion report living
only on purgeable scratch with its digest bound in four places. Doing that twice would be inexcusable.
`state/gate5-family-promotion-evidence-20260814/`, report `ca99effa…` (277,601 B) **re-verified after the
copy**, and **the verdict re-derived from the committed copy rather than from the scratch read**.

**The draw is live across the whole family** — 50 of 50 distinct on target digests, all three factor-hash
streams, and weights digests; 50 distinct `R` from `1.1225496…` to `1.1253110…` with the nominal
`1.1240802949941018` **strictly inside**. A collapsed draw would show identical values. Diagnostic of the
draw, **not** a component of `C_stat`.

**`BEN-230`'s check ran on 50 of 50 members and agreed 50 of 50** — its first exercise on the full live
family, hours after codex's mutation test showed 57 of 57 checks passing a 13.6% shift in `R`. Its limit
is unchanged and stated: length and sum, **not identity**; `replica_03` and `replica_08` still share
`n_data_effective = 4114512` with differing hashes, so the bound is real in this very family.

**What tonight does NOT do, stated because a pass invites over-reading.** `C_stat` is still `null` and
this lane did not construct it — the reconciler has no covariance code by design, and that design does
not stop applying now that the family is complete. `FAMILY_COMPLETE_PASS` is the
completeness-and-coherence gate; **extraction and centring on the replica mean are the next step and a
separate, reviewable action.** It does not close `OI-60`, and no run of this tool can. Five residuals are
carried forward explicitly in the receipt rather than allowed to drift into looking closed.

`GATE5_CODE_ROOT` was never touched, across the whole campaign.

### 2026-08-14 08:57 UTC — Gate-5 training family promoted after job-specific NPZ validation

The one-shot event for read-only CPU job `56933831` was valid and the event had not already been
reconciled. Lane C had independently committed the full-strength family replay at `bed45a3`, so that
expensive work was not duplicated. The remaining job-specific evidence was reconciled: `COMPLETED/0:0`
in 2m18s, empty stderr, immutable validator HEAD `987a45c`, and every promotion-marker hash binding
re-derived.

The family report is the bare `FAMILY_COMPLETE_PASS`, full strength, replay performed, 50/50 targets
and 50/50 trainings, zero failures. The independent artifact report is
`GATE5_TRAINING_ARTIFACTS_PASS`: 50/50 members and zero failed checks, covering the frozen subsample,
2+4 optimizer schedule, complete signal/background factors, source/target/identity bindings, logs,
accounting, and collision isolation. The scratch reports were hash-preserved into the repository; the
family report is byte-identical to Lane C's committed `ca99effa…` copy.

Promotion verdict: `GATE5_TRAINING_FAMILY_PROMOTION_PASS`. This is a training-family promotion only.
`C_stat` is still null, no subset is selected, and Gate 6 remains unchanged. The next dependency-ready
action is the predeclared 50-member full-input extraction and complete manifest. Receipt:
`../docs/orchestration/state/gate5-training-family-promotion-56933831.json`.

### 2026-08-14 09:14 UTC — Gate-5 full-input extraction implementation accepted

The dedicated replica extractor was implemented without changing the Gate-4-pinned nominal extractor.
It calls the nominal path's model rebuild, engine reweight, ordered-coverage checks, xsec arithmetic and
atomic writer. Its Gate-5-only adapter replays the persisted full factors and applies the full signal
draw to both truth counts and completeness/reporting-mask construction. The background draw remains
bound to the already-verified per-replica Stay-Positive target; background rows do not enter the final
truth-space binning.

The terminal validator is fail-closed on the declared family: 49/50 produces a BLOCK report and never a
49-member covariance. The actual TensorFlow-runtime acceptance command passed 181/181 tests. A real
replica-0 preflight independently replayed all 49,152,885 signal factors and recovered factor hash
`892d1531…`. Batch was selected over interactive because this is a 50-member, ten-concurrent-GPU family
that must outlive a single interactive allocation. `C_stat` remains null. Receipt:
`../docs/orchestration/state/gate5-extraction-implementation-20260814.json`.

### 2026-08-14 09:16 UTC — Gate-5 extraction submission attempt refused before job creation

The first submit call from immutable HEAD `d0a07cf` created no job: Slurm rejected the array request
because explicit `--mem=64G` raised the billing allocation to 38 CPU cores for one A100, while
`gpu_shared_ss11` permits 32 cores per GPU. This is a changed prestart launcher blocker, not an
extraction failure. The analogous full-input push used about 6.9 GiB MaxRSS, and the existing accepted
Gate-5 training launcher uses the queue's memory default, so the correction removes the explicit memory
request while retaining 32 CPUs, one A100 and the 2h wall. No output or job ID exists from this attempt;
the retry must run from a new immutable commit.

### 2026-08-14 09:20 UTC — Gate-5 extraction array and complete-family validator launched

The changed launcher was committed/pushed at `7dc8c34` and frozen in an immutable clean worktree.
Slurm accepted extraction array `56935552_[0-49]`: one A100 and 32 CPUs per task, queue-default
57,472 MiB, 2h wall and at most ten concurrent. Every task owns only
`fullevent_cstat_n50/replicas/replica_XX/extraction/`; all product and marker paths were absent before
submission and every writer refuses collisions.

CPU job `56935553` depends `afterany:56935552` so it writes a truthful family BLOCK report even if a
member fails; only `GATE5_EXTRACTION_FAMILY_COMPLETE_PASS` at 50/50 promotes. External terminal watches
`gate5-extraction-56935552` and `gate5-extraction-manifest-56935553` are armed. Batch, rather than
interactive, is the correct route for this 50-GPU-task family and lets Slurm plus the detached waker
advance without LLM turns. `C_stat` remains null. Receipt:
`../docs/orchestration/state/gate5-extraction-active-56935552.json`.

### 2026-08-14 09:47 UTC — Gate-5 extraction array changed launcher/data-root failure

The external error event was valid but early, not aggregate-terminal: task 0 was `FAILED/1:0`, task 1
was running, and tasks 2-49 remained prestart-pending. Every extant task log and output namespace was
inventoried once. Replica 0 completed and atomically published its full ordered 49,152,885-row push;
its payload and marker revalidate. It then failed before any xsec write because the driver's default
`mcfile` was derived from immutable code worktree `7dc8c34`, while the flux ROOT is off-repository under
the canonical data root. There is no xsec, summary, task receipt, family promotion, or science verdict.

Because every untouched member carried that same deterministic launcher defect, exact array `56935552`
was canceled rather than allowed to consume 49 GPUs on unchanged failures. Its original after-any CPU
validator `56935553` and watch are preserved to publish the truthful partial-family BLOCK. The changed
continuation requires the flux path explicitly, reuses a push only after its atomic marker passes, keeps
all final collision guards, and waits for the predecessor to terminate before writing. The repaired
runtime battery passes 184/184. No subset, `C_stat`, Gate-6/`C_ML`, provider dispatch, reset credit, or
worker replacement occurred. Receipt:
`../docs/orchestration/state/gate5-extraction-failure-56935552.json`.

### 2026-08-14 09:51 UTC — Changed Gate-5 extraction continuation launched

The repair and failure evidence were committed and pushed at `2f65a36`, then checked out into immutable
clean worktree `gate5-extraction-r2-frozen-2f65a36`. Submission preflight found exactly one published
extraction artifact pair: replica 0's valid complete push and marker. No xsec, summary, task receipt, or
other replica push existed. Changed array `56936015_[0-49]` depends `afterany:56935552`, retains the
ten-A100 concurrency cap, and will reuse replica 0 only after the runtime marker/content gate passes.
Every other member performs its full push once. Every xsec call receives the canonical data-root flux
explicitly.

Changed CPU manifest `56936016` depends `afterany:56936015` and still requires a bare 50/50 family PASS.
Original manifest `56935553` was not canceled or repurposed: it remains independently watched and will
record the first array's partial-family BLOCK. Watches `gate5-extraction-r2-56936015` and
`gate5-extraction-r2-manifest-56936016` are armed. `C_stat` remains null; no subset, provider dispatch,
reset credit, UUID change, Gate-6, or `C_ML` action occurred. Active receipt:
`../docs/orchestration/state/gate5-extraction-r2-active-56936015.json`.

### 2026-08-14 10:02 UTC — Original Gate-5 complete-family manifest BLOCKED 0/50

After-any validator `56935553` ran from the original immutable `7dc8c34` worktree for 43 seconds and
exited `1:0`. This is the validator's intentional fail-closed return for its atomically written
`GATE5_EXTRACTION_FAMILY_BLOCKED` report: stderr is empty, the stdout verdict is 0/50, and the completion
marker matches the report path, size and mtime. All members 0-49 are listed explicitly as failures;
`C_stat` is null and no subset is selected.

Members 1-49 have no valid push, xsec, summary, or receipt from the original array. Member 0 needs the
more precise reading: changed r2 task `56936015_0` completed `0:0` before the old validator started and
published r2 final products into the shared member namespace. The old validator did not misattribute
them: its runtime-HEAD, source-array-job and extractor-code pins all fail against those r2 products.
Thus the original family remains terminally BLOCKED even though reusable scientific work is being
continued under a separately pinned attempt.

No original-family promotion, unchanged retry, subset, `C_stat`, Gate-6/`C_ML`, provider dispatch,
reset credit, or worker replacement occurred. At the reconciliation snapshot, r2 task 0 was complete,
r2 tasks 1-49 were pending Priority, and changed manifest `56936016` remained dependency-held. Their
terminal watches remain the dependency-ready continuation. Receipt:
`../docs/orchestration/state/gate5-extraction-manifest-block-56935553.json`.

### 2026-08-14 ~05:00 PDT — THE `C_stat` SPEC IS COMMITTED, AND WRITING IT SURFACED TWO BLOCKERS (lane C)

`OI-121` authorized — Joseph's *"go ahead"*, relayed. **Read the scope, not the word:** the authorization
is for **two independent implementations from one written spec**, compared element-wise. Builder 1 is lane
B, builder 2 a cold `codex` session, comparator D, judge `codex` background. **Lane C is the spec and does
not write the covariance code** — C kept covariance out of the extractor on purpose
(`extract_fullevent_replica.py:350,412`, `validate_gate5_extraction_family.py:194,260`,
`submit_gate5_extraction_r2_n50.sh:34`) and should not be the one to erode that property.

Landed: [`SPEC-20260814-gate5-cstat-construction-v1.md`](../docs/orchestration/SPEC-20260814-gate5-cstat-construction-v1.md)
plus the machine contract [`pet/gate5_cstat_contract.json`](pet/gate5_cstat_contract.json). **No
implementation in either.** Decided so no builder decides: the covaried key (`xsec`), the binning, the
flattening string, replica ordering, centring, normalization, and the reporting domain. **Left open on
purpose:** rank and the object's name.

**Three measurements drove it, all from the published artifacts, none from a document.**

1. **The grid is `15 × 19 = 285`, not the 224-cell paper grid in `AGENTS.md:345-351`** — the source dump
   is extended-FPS (`pT` to 30.0; `p∥` 0–0.75 and 60–120). A builder trusting the documented grid
   produces a 224-cell object and **every element of the comparison misaligns.** Stated first in the spec
   for that reason.
2. **The reporting mask is drawn per replica and the flicker OCCURS.** D found the mechanism
   (`extract_fullevent_replica.py:190-196` puts the signal Poisson factor *inside* `completeness_2d`;
   `:517-518` hard-zeroes `comp > 0` failures) and was explicit it had not measured an occurrence. **C
   measured it: 3 cells reported in some but not all of 14 members, one in only 9 of 14**, with
   `n_cells_populated` telemetry varying `260/261/262`. In such a cell part of the "variance" is the mask
   switching off. **Both builders compute the identical wrong number there and agree perfectly** —
   element-wise agreement has no power over a defect in the input to both, which is exactly why it is
   declared in the spec rather than left to code. `BEN-231`.
3. **The spread is ~90× counting statistics and the network is unseeded.** `4.478%` relative sd on the
   total cross section against `0.0493%` Poisson on 4.1M data events; `set_seed` appears **nowhere** in
   `nd-unfolding/` or `omnifold_nn/`. Members differ by their draw **and** by free-running training
   stochasticity, so the object is `C_stat + C_train`, **inseparable from this family.** `BEN-232`,
   `OI-92`, and the long-form
   [`FINDING-20260814-ninety-times-counting-statistics.md`](../docs/orchestration/FINDING-20260814-ninety-times-counting-statistics.md).

**Centring was decided, with a number rather than a preference.** Replica mean. Nominal-centring inflates
the trace **6.013×**, and the excess is *exactly* the offset term `N/(N-1)·‖mean−nominal‖²` — a **bias**,
not a fluctuation, with the replica mean `+7.56%` above that nominal. And the only 285-cell nominal
artifact on disk is named `NONQUOTABLE-DIAGNOSTIC`, so nominal-centring was never an available option.

**Two corrections to the state I was handed, both inference-for-measurement.** The array's throttle is
`ArrayTaskThrottle=10`, **not 2** — two concurrent tasks was observed occupancy under `(Priority)`, so
raising the cap buys nothing. And **I nearly reported a 7-hour throughput collapse that never happened**:
`sacct` prints local time while I had asked `date -u`, and the gap was *exactly* 7 h. Task 13 finished two
minutes before I looked. `BEN-233`.

**Nothing was constructed.** 14 of 50 extractions published at spec time; the spec was written *during*
the wait precisely so nobody starts early. `GATE5_CODE_ROOT` untouched, no `scancel`/`scontrol`/resubmit,
`OI-60` and `OI-66` not closed.

### 2026-08-14 ~06:00 PDT — THE RANK ESCALATION WAS WRONG TO RAISE: IT WAS SETTLED BEFORE LAUNCH (lane C)

**`OI-91` is CLOSED BY REFERENCE the same day I raised it, and the closing document is one I should have
read instead of escalating.** `PREDECLARATION-20260813-gate5-coherent-replicas-n50.md` (`6bd3707`,
**2026-08-12 23:29**, before the replica code path existed) states verbatim: *"Rank is not the criterion —
1431 bins is unreachable at any affordable `N`, and the rank-deficient GoF treatment is already disclosed
under `OI-29`. The criterion is precision on a subdominant component: `1/√(2(N−1))`, giving 10.1% at
`N=50`."* Joseph's decision in it, verbatim: **"sounds good, get N=50 up and running."**

**Mine was the FOURTH approach to that closed question** — `OI-122` records two more on 2026-08-14. The
pattern is worth naming because the cost is Joseph's attention: **rank ≤ 49 is arithmetically obvious from
`N=50` and any bin count, so every agent that computes it experiences it as a finding**, while the
predeclaration that settled it is not a file anyone reads on the way to a covariance. Mitigation is in the
document the next agent must read anyway — `SPEC` §7 now opens with the citation and the line *if you have
just derived that rank ≤ 49 is a problem, read the predeclaration before writing anything.*

**What made this cheap to close was narrowing it before the answer arrived.** When `OI-122` landed I had
already reduced `OI-91` from *"declare a rank treatment"* to *"does `OI-29`'s treatment extend to this
262-cell object?"* — a yes/no with a citable answer rather than a decision to consume. It extends. The
**measurement is kept** (285-cell grid, 262 reported, ceiling binding tightly at `N−1`) because it was not
known before today; only the escalation is withdrawn.

**The strongest thing found this round is that my two centring/normalization decisions were already the
adopted convention.** `combine_cstat_bkgsub.py:57-58` — the Phase-4 builder for the 5D `C_stat` the
analysis already uses — is `Z = Xr - Xr.mean(0)` then `C = (Z.T @ Z) / (N - 1)`. Replica-mean-centred,
`1/(N-1)`. So `CSTAT-D1`/`D2` are **not new decisions**, and the builders' output composes with the
existing chain **without a translation step**. Recorded as reason **zero**, ahead of my own 6.013× argument.

**And that file also shows why this chain has `BEN-231` and the adopted one does not.** Production masks on
the **central value** (`rep = cv > 0`, `:56`) — replica-**independent**, immune to flicker by construction.
The equivalent here would mask on the nominal extraction, and the only 285-cell nominal is explicitly
**non-quotable**. So one missing quotable nominal causes **both** the centring constraint and the flicker.
**Producing a quotable nominal full-event extraction would retire `BEN-231` outright** rather than manage it.

**Two consumer-side predeclarations added, `OI-93`, taken before any number exists because that is the only
honest time.** (a) **Hartlap** — the new part is not the `N=50, p=262` singularity we knew about, but that
**a truncation to `p_effective < N` chosen to make inversion possible still carries finite-`N` bias, and
the bias makes χ² too SMALL** — it errs in the flattering direction. (b) **Peelle's Pertinent Puzzle** — the
FPS chain carries `+ norm 1.4%`, so the precondition is present, and PPP yields a *better-looking* χ²
beside a wrong normalisation, so nothing in the fit output flags it. **All external citations here are
UNVERIFIED** (delegate research, Gemini 3.1 Pro, both `codex` accounts out of quota) and are labelled as
such in every place they appear.

**`CSTAT-N1`, answering the mediator's sharpest question: there is NO separate diagonal data-statistical
term in the PET chain.** `assemble_ctotal_bkgsub.py:4` is `C_total = C_syst + C_stat + C_ml + C_retrain`,
no diagonal addend, and `C_stat` is the replica object. So the reported field rescue — *add the full-rank
diagonal data-stat term* — is **not** what this chain does, and our statistical term restores nothing.
Rank in the total comes from **subadditivity over independent low-rank blocks**, which explains B's 222/266
with no diagonal term needed, and means **the total's rank is a budget** that degrades if any component's
universe count drops. Answered from the source, not by inference. **I started measuring the per-component
ranks and killed it: 76 minutes of CPU in 5 minutes of wall on a shared login node was my error**, and the
question is B's anyway — B's 222/266 is on the 266-cell lgbm mask, not this spec's 262.

### 2026-08-14 ~06:40 PDT — ONE BUILDER, AND THE SHAPE RULING: BOTH FORMS, WITH THE REDUCTION CHECKED (lane C)

**Joseph dropped the second builder** — *"Okay yeah drop the second builder."* The spec is rewritten so
**no independence claim is available anywhere in it**, because none is. The reason that matters most is the
one that indicts the original design: **this spec pins `dof`, `centring`, `ravel_order` and member
selection — exactly the decisions above the kernel that would have been the only source of genuine
divergence. The better the spec, the less two builders could differ.** D also measured `Xc.T @ Xc` and
`np.einsum` as **bitwise identical** (both dispatch to BLAS `dgemm`), so the two builds were likely one
computation. What the artifact now gets is spec conformance, a regression against `combine_cstat_bkgsub.py`,
and D's element-wise harness — **proportionate for 0.669%/bin against `C_syst`'s 7.27%**, and claiming more
would be the failure this campaign keeps filing.

**§3.1 RULED, as decider: emit BOTH forms plus the full-grid mask.** `C` is `(n_reported, n_reported)` — the
deliverable the assembler consumes — `C_full` is `(285,285)`, `reported_mask` is the `(285,)` map, and the
builder MUST assert `C == C_full[np.ix_(mask, mask)]` **bit-identically.** Full-form-only leaves *the
reduction verified by nobody*, and the reduction is the one step B and D independently flagged as
error-prone because **the reported set is contiguous only within rows.** Reduced-only loses the fixed
dimension. Both-forms is D's proposal, the bit-identical formulation is B's, and **D disclosed that its
harness was already built for `(285,285)` and then argued for the option costing it rework** — an interest
declared and argued against is stronger evidence than none.

**The common mask is the FPS `266`, NOT this family's `262`, and the authority is the consumer.**
`assemble_ctotal_bkgsub.py:104-107` **fails closed** on a mask mismatch against `C_syst`, so building on 262
would have `C_stat` rejected *at assembly* — the translation step `OI-121` exists to eliminate. Safe because
the nesting is now verified **three ways**: D's containment check (`b9d0803`), B independently from the other
direction, and **C from a third artifact** — subtracting D's four cells `{228,251,252,253}` from this
family's 23 never-reported leaves exactly **19**, the zero count a 266 mask must have. Census on 266:
**259 always + 3 flickering + 4 identically zero**, and the four are declared by index because undeclared
zero rows read as failure.

**A correction I owed on those four.** They had been justified by PET telemetry's
`n_cells_masked_zero_acceptance = 4`, described as count-and-mechanism agreeing across two artifacts.
**Measured over 18 members that field takes the values {2,3,4,5,6}** — it is itself a per-replica draw, being
computed with the replica's signal factor applied. The **nesting stands** and never depended on it; what does
not stand is treating `4` as a property of the family rather than of the nominal. Not to be carried into a
technote as family-level agreement.

**`CSTAT-D0e`: `n_reported` is DECLARED from the mask, never inferred from the diagonal** — and the trap is
live in tracked code, which I read rather than took on relay. `p4_validate_active_lateral_fps.py:72` does
`int(np.sum(d > 0))`; a cell can be **reported and carry zero variance**, and on this object it is wrong by
construction because the 266 mask deliberately holds four zero cells, so it would read 262. Its neighbour
`:70`, `bool(ev[0] >= -1e-12*abs(ev[-1]))`, is a **negativity** test that an exact zero satisfies, so a
rank-49 matrix passes `psd=True` silently — and `min_over_max_eig` at `:69` already records the evidence, so
a threshold is missing, not a measurement. Both in `KNOWN_ISSUES.md`; guarded on the `C_stat` side, not
repaired in another lane's path.

**Adopted from B's requirements document, in my own voice and labelled as ratification** —
`layout_fingerprint`, `dof`, `centering`, `ravel_order`, the full-grid `reported_mask`. **That document is
B's INPUT, dispatched before this spec existed, and it is not the spec**; the header now says so, because D
was right that a builder-authored spec-shaped document compromises the design if nobody states which it is.
**B's finding that this spec relies on and did not produce:** `receipt_model_chi2_2d.py` justifies
`ndf = n_reported` by a scan whose stated condition — *effective rank not far below `n_reported`*, measured
204/205 — **is false at 49/262.**

**`max_abs_asymmetry` promoted to a REQUIRED key, and a misattribution recorded rather than quietly
absorbed.** The strengthening arrived as a correction to a rule reading *"symmetrise explicitly and record
the asymmetry you symmetrised away"* — **this spec never contained that rule**; its first draft already
forbade symmetrising. Adopted anyway, because *required and named* beats *reported*. Recorded because a spec
that accepts edits to rules it does not contain has stopped being an authority.

**`member_xsec_sha256` and a new `CSTAT-R3f` (constant `slurm_array_job_id`), both required, and the reason
is measured:** the **failed** r1 array `56935552` and the live r2 `56936015` **write to the same output
root.** r1 died before writing any product so nothing is contaminated — **but a glob would have taken its
products had any existed, which is luck rather than design.** Digests catch a stale duplicate within one
array; the array id catches a clean product from the wrong array.

### 2026-08-14 ~06:10 PDT — `BEN-232` IS REFUTED AND THE GREP IS THE FINDING (lane C)

**I reported that the Gate-5 replica network was unseeded. It is not. The estimator seed is pinned at 42
on all 50 members and enforced per member.** The mediator flagged it; I verified rather than accepted:
the launcher (`sbatch_gate5_replica_train_array.sh:63-71`) passes only `--bootstrap-seed`/`--replica-index`;
`train_fullevent_replica.py:236` calls `nominal.main()` **without** `--estimator-seed`, so `:335` defaults
from `NOMINAL_SEED_POLICY` (`:69` = 42) and `:376` runs `tf.keras.utils.set_random_seed(42)`; and
**measured, all 50 `GATE5_REPLICA_WEIGHTS.npz` carry ONE `seed_policy` with `estimator_seed: 42`**, with
`:275` fail-closing on drift. So agreement is enforced, not coincidental.

**Why the search could not have worked, which is the part with reuse value (`BEN-235`).** I ran
`grep -rln "set_seed"`, got nothing, and published *"`set_seed` appears nowhere."* The API is
**`set_random_seed`**, and **`"set_random_seed"` does not contain the substring `"set_seed"`** — the
intervening `random_` breaks it. `tf.random`, `np.random.seed`, `TF_DETERMINISTIC_OPS`, `PYTHONHASHSEED`
all miss `tf.keras.utils.*` as well. **Not one pattern could have matched the line that refutes me**, so the
silence carried no information and I converted it into a headline finding, a long-form document, an `OI` to
Joseph, and a claim that the published total double-counts a component. **An inference from absence is only
as strong as the search that would have refuted it.** Worse than `BEN-234`, filed hours earlier, because I
did not even label this one — a `grep` returning nothing *feels* like a measurement.

**The refutation is in every place the claim was**, not annotated: `BEN-232`'s row rewritten, its long-form
retitled and rebuilt, `OI-92` CLOSED, `SPEC` §8 replaced wholesale, and the contract's `CSTAT-O2` block
replaced. **`C_stat` is correctly named and no Joseph turn is needed.**

**What survives is a physics question, and it is now DECOMPOSED rather than merely narrowed.** Leg F pins
`EST=42`/`SUB=0` for every draw at `bootstrap_seed = -1`
(`sbatch_pet_fullevent_floor_replicate_array.sh:48-50,185-186`, read directly), so **`VL130` is the residual
GPU/process non-determinism floor that survives a full seed pin** — a stronger claim than its old
"across-process training noise" label, and B has relabelled it. B then closed the normalization axis in
**2.6 s of numpy**, without the extraction stage, by seeing that `σ_tot`'s denominator is identical across
draws so the relative spread of the total equals that of the numerator `Σ_j w_truth·push_d`. **I re-derived
every figure and they reproduce to rounding:**

```
family spread          4.478%   = 90.8x Poisson    100.00% of variance
non-determinism floor  1.918%   = 38.9x Poisson     18.35% of variance
quadrature residual    4.046%   = 82.1x Poisson     81.65% of variance
Poisson n_data=4116128 0.0493%                      shares sum to 100.00%
```

Negative control holds — `cap_saturation_frac = 0.0` on every draw, so not a logit-clipping artefact — and
the mechanism shows directly in per-draw `mean(push)`: `1.0776 / 1.0913 / 1.0472 / 1.0825`. **So the gap is
neither an unseeded network nor counting statistics: 18.35% is measured process non-determinism and 81.65%
is unexplained.** B's reading, which neither of us asserts, is the learned map's response to the draw — the
legitimate content of `C_stat` for an unfolding estimator. **If so the name is right, and ~18% of the
component's variance being non-determinism rather than data statistics belongs in the receipt either way.**
Three caveats travel with it: the floor is on the **2M-subsample numerator** not the published total; the
quadrature split **assumes independence**; and `n=4` carries **40.8%** fractional uncertainty per sd
(→35.4% when draw 5 lands), with `1/√k` recorded as an **assumption** because `n=4` cannot test it.

**`CSTAT-O2a` is RELEASED and its shape improved.** I had queued it to *establish* the floor; Leg F pins the
**no-draw** floor, so the test now pins the **with-draw** floor against an existing baseline and **the
difference is the map response** — one comparison, not a fresh measurement, and it is what decides whether
the 81.65% is real content. **Sequenced after `56936015` drains and `nice`d**, because extraction is the
critical path and floor draw 5 is still in flight.

**And the pair really did lack a proof, so `CSTAT-D4` now writes it.** `C_stat` varies the Poisson draw
with the seed pinned and enforced; `C_ML` varies the seed with the draw fixed (`RUNBOOK:223-224`). Disjoint
inputs, no double count — **enforced rather than lucky**, since `:275` would fail a family whose seed policy
drifted. That was the real gap under a wrong claim, and it is closed.

**`BEN-236` — a third mask, and a set collision at 259.** Adopting B's constraint (no consumer may use a
training artifact's `reported_bin_mask` as the reporting domain) and then measuring it changed it twice: the
training mask is **not constant** (`{257:3, 258:21, 259:26}` over 50 members, union 259, intersection 256),
and **the training union's 259 is a DIFFERENT SET from the extraction intersection's 259** — the extraction
union holds `{254, 281, 284}` besides, and `254` is a flickering cell. **A matching count is not a matching
set.**

**`CSTAT-R7` added, and it is the one `OI-122` obligation that is mine:** the receipt MUST state that
`N=50` gives **10.1%** fractional uncertainty on the estimated sd, not the **7.1%** the `N=100`
predeclaration targeted. That disclosure is what the downward revision was accepted under, it is additive
and true regardless of how the supersession is recorded, and publishing the number without it is the only
ordering that would be wrong.

### 2026-08-14 ~06:30 PDT — `OI-122` EXECUTED: THE `N=100` PREDECLARATION IS RETIRED IN PLACE (lane C)

**I declined this an hour ago and was right to; Joseph then authorized it and I executed.** Verbatim
**"Yes I authorize it"**, answering the exact question *"do you authorize marking … as SUPERSEDED, naming
the N=50 document, retiring rather than deleting it?"*, and **committed at `4d28e78` BEFORE the act** per
`BEN-082(v)`. My three grounds for declining all held and none was overridden: the row assigned ratification
to Joseph; the act overrides a committed verdict clause and so is scientific rather than clerical; and lane
B had already declined the same task, so being asked next was routing around a declining lane. **The
mediator recorded that last one against itself in the ledger.**

**The retirement is purely additive: 65 insertions, 0 deletions.** No sentence of the 2026-08-12 document
was edited. Checked before annotating that **no `sha256` of its bytes exists anywhere** — all references are
by path — so `BEN-158`'s annotate-in-place hazard does not apply. Classified `ARCHIVAL` + `superseded` +
`canonical_successor`, **deliberately not `DEAD`**: Joseph's own reasoning is that *a predeclaration you
delete when it becomes inconvenient is not a predeclaration*, and a visible superseded one is what proves
the supersession happened in the open.

**Grounded in AUTHORITY, not precision.** The file's `:10` reads *"NOTHING IS LAUNCHED BY THIS FILE AND
NOTHING MAY BE"* and its §4 condition 4 says of itself *"This file is not that authorization."* So the
supersession records that the standing was **never exercised**, rather than overruling a decision the
document had standing to make. Grounding it in *"50 is precise enough"* would have invited a referee to
adjudicate `1/√(2(N−1))` at 50 against 100, which is not what happened.

**The header defuses the `:73` `INSUFFICIENT` clause rather than merely superseding it.** That sentence —
*"fewer than 100 complete manifests at assembly … not repaired by rescaling"* — is what made this look like
a live conflict to two independent readers for most of today. **Its trigger is *at assembly*, and no
assembly ever occurred under this file.** A header saying only "superseded" leaves that trap armed.

**And one thing the ratification did not ask for, which a cold reader needs: the document's QUALITY
branches were MET by the successor, not dodged.** `SEED LEAK` — *"any replica whose estimator seed differs
from the fixed value; fail closed"* — **passes**, and I can measure it: all 50 weights artifacts carry one
`seed_policy` with `estimator_seed: 42`, and `train_fullevent_replica.py:275` fail-closes on drift, so the
fail-closed behaviour the branch demanded is *implemented* rather than merely observed. `CENTRING ERROR`
**passes** — replica mean, independently required by `RUNBOOK:213`. `NON-PSD` is not yet evaluable.
**`INSUFFICIENT` is the only branch that differs.** So the two documents never disagreed about estimator
quality; they disagreed about inventory size alone, which is the axis the successor changed in the open,
before launch, with a stated criterion.

**Action 2 was already done and correctly did not wait for him** — `CSTAT-R7` requires the receipt to state
`N=50` → **10.1%** against the **7.1%** targeted at `N=100`. Retiring the document does not discharge that;
it is what the downward revision was accepted under.


## 2026-08-14 — lane B, documentary: Gate 4's disposition is CLOSED, and eleven live citations say otherwise (`BEN-244`)

**Asked by the mediator, answered read-only; no job, no artifact, nothing on the cluster touched.**

**BOTH GATE-4 ACTS HAPPENED ON 2026-08-13, each with its own committed record.** The arm was selected
by Joseph, verbatim *"Okay do the annealed"*
(`docs/orchestration/AUTHORIZATION-20260813-gate4-estimator-disposition.md:12`). `56563761` was
promoted to canonical at commit `6b68d12`, `promoted_at_utc 2026-08-13T02:52:32Z`
(`state/p3f-pet-gate4-nominal-promotion-56563761.json`, `verdict: PROMOTED`), with
`scope.artifact_promoted` flipped 3 minutes earlier at `156d1d6`. **The promotion was authorized by
the mediator under Joseph's delegated go** — *"if all you need is a go command, feel free to authorize
it yourself"* — and **both receipts carry a `DO_NOT_RECORD_AS` field refusing to record it as
Joseph's** (`p3f-…-promotion:17`, `annealed-nominal-complete:220`). Two acts, two parties, and the
record can tell them apart.

**TWELVE LIVE REFERENCES WRITTEN AFTER 02:53 UTC STILL CALL IT AN UNMADE USER DECISION.** Every one
dated by `git blame`; not one is superseded or dated text. **Five are lane B's**, including
`ND_OMNIFOLD_RUN_LOG.md:5913` and `:6124` — corrected here, by append, because this file is
append-only. **Two are inside frozen `PREDECLARATION-*` documents of completed runs and cannot be
edited at all**; they are recorded in the finding instead. The full inventory with owners is in
`docs/orchestration/FINDING-20260814-a-decision-that-reached-its-own-record-and-nowhere-else.md`.

**AND THE CLAIM STRENGTHENED IN TRANSIT.** The only machine-readable statement anywhere is
`state/gate6-member-trajectories-result-56847059.json:119`,
`gate4_user_disposition_remains_independent: true` — measured, the sole Gate-4 mention in that
receipt. It asserts **scope independence**. Lane B rendered it as *"an independent user decision that
**blocks** construction"* and named that receipt as the source. A stale fact is recoverable by
re-reading the source; a fact that got *stronger* on the way to its citation is not, because
re-reading the source stops looking like a contradiction.

**WHAT ACTUALLY BLOCKS `C_ML`, worked forward from the contract rather than backward from the
citation.** `RUNBOOK:223-224` names no user decision; `RUNBOOK:213-214`'s *"every component uses the
P5A central"* is the real Gate-4 link and it is now **discharged**. Three live blockers remain, none
of them a disposition: (1) `family_verdict BLOCK_GATE6_ML_ENSEMBLE`, `passing_members [1]`,
`failing_members [2,3,4,5]`, five prohibitions applied — **a measurement failure**; (2)
`combine_cml_bkgsub.py:75,81-82` reads its mask and reference from a nominal *extraction* product,
and `annealed-nominal-complete:142` records `extraction_run: false` with extraction on the promotion
receipt's `NOT_authorized` list; (3) `--expect 12` crossed members against Leg 1's five — and
`combine_cml_bkgsub.py:84-86` makes that mismatch a **`WARN`, not a `FAIL`**, so **the code would
build `C_ML` from the one passing member**. `do_not_select_passing_subset` is enforced on people, not
by the builder.

**THE DESIGNATION'S OWN FAIL-CLOSED GUARD HAS BEEN RED SINCE THE PROMOTION.**
`nd-unfolding/pet/check_canonical_designation.py` exists so that *"the safety of that choice rests
entirely on the reference inventory being COMPLETE"* (`:2-10`). **Run at `849b70f`: exit 1** — 8
unaccounted files and a `COUNT DRIFT`, and **the two records of the promotion are themselves among
the occurrences it cannot account for** (`p3f-…-promotion:67`, `AUTHORIZATION…:271`), with the drift
at `annealed-nominal-complete:226`, the prose the supersession added. `VERDICTS-20260811-session-D.md:452`
records the same script at `exit=0, PASS` on 08-11. **It is absent from `.githooks/pre-commit`'s check
list and from its declined list** — the exact condition that dispatcher's own comment at `:25-27` was
written about after `verify_hash_bindings.py`. Second instance, same gate's namespace. **And zero of
its 54 entries are dispositioned `RETARGET`** (the token appears once, in the legend), so no consumer
in the tree follows the canonical designation and the extraction launchers are written to stay pinned
to the 08-08 artifact.

**WHAT IS GENUINELY STILL OPEN, named narrowly, because "closed" is the answer most likely to be
wrong in a convenient direction.** Not the disposition. (a) **The quotability of `VL100 =
0.512603276`**, which is the recovery number the whole physics argument rests on and which comes from
closure `56552326`, every artifact prefixed `NONQUOTABLE-DIAGNOSTIC.` with `quotable: False`; the
promotion receipt declines to discharge it (`:95`) and **it is tracked under no `OI-*` id** — measured.
(b) `recovery_evaluated: false` at the promoted configuration. (c) `VL101`'s baseline `0.546853` is
not established as uninflated (`VALIDATION_LEDGER.md:1811`). Plus two bookkeeping defects that each
read as a live block: `annealed-nominal-complete:152-156` still carries
`next_dependency.state: BLOCKED_ON_USER`, eight lines below the `artifact_promoted: true` that
superseded it, and its `declaration` pointer `state/waker/BLOCKED-ON-USER.json` **does not exist**
(untracked at `a45f17b`).

**Nothing was executed and nothing is unblocked by this entry.** Gate 6's five prohibitions at
`19585b7` remain live, Leg X remains unsubmitted pending Joseph's answer, and correcting a stale
blocker citation is not authorization to pass the blocker it was standing in front of.

## 2026-08-14 — lane A, documentary: Joseph AUTHORIZES the Gate-6 retry, and Gate 6 stays blocked

**Nothing was executed, nothing was submitted, and nothing on the cluster was touched.** Lane A wrote a
verbatim authorization record and three bookkeeping corrections. The mediator sequences the legs.

**The authorization, verbatim and complete** — `docs/orchestration/AUTHORIZATION-20260814-gate6-retry.md`:

> Also yes I authorize the gate 6 retry

Transcribed by `personal-orchestrator` (peer session `minerva-omnifold-58`) from Joseph's typed message
immediately preceding its dispatch. **Lane A copy-pasted the block and cannot see the original; it attests
only that its text matches what it received** — the same division of attestation as the 08-12 and 08-13
records, and written before acting per `HANDOFF-20260812-1145Z.md:126`.

**ALL FIVE PROHIBITIONS AT `19585b7` REMAIN LIVE AND THE AUTHORIZATION CLEARS NONE OF THEM.** Verified this
turn at `state/gate6-member-trajectories-result-56847059.json:112-118`. The natural misreading is that a
retry authorization discharges `do_not_retry_unchanged`; it does not, and the reason is worth keeping:
**`do_not_retry_unchanged` forbids an *unchanged* retry, so a changed retry was never inside its scope and
there was never anything to lift.** What Joseph supplied is the user go to spend compute — the thing
`ND_OMNIFOLD_STATUS.md:40` said was missing. **The prohibition set is unchanged at five, and any later record
showing four has expanded scope without authority.** Family state also re-verified from `:109-111`:
`BLOCK_GATE6_ML_ENSEMBLE`, `passing_members [1]`, `failing_members [2, 3, 4, 5]`.

**Not authorized, each verified rather than relayed:** not Leg X (which `STATUS:59` correctly calls
*"authorized"* — it holds a *readout* authorization and is nonetheless deliberately unsubmitted; this record
changes neither half); not skipping Leg 0, whose ordering `PLAN-20260813-gate6-cml-retry-design.md:144-146`
calls *"forced, not stylistic"*; not `C_ML`; not member selection, **including member 1, the only passing
member and the one a convenient reading would take**; not the VL100 quotability question.

**A `C_ML` CITATION VERIFIED, A DEFECT RE-DERIVED, AND `OI-72` WITHDRAWN THE SAME HOUR IT WAS FILED.**
`combine_cml_bkgsub.py:75` defaults `--cv` to the nominal extraction product and `:81-82` takes **both its
reference and its positivity mask** from it, so `C_ML` genuinely needs that product — that part stands.
**The rest was wrong twice over and is corrected here rather than quietly adjusted.** Lane A measured the
member-count guard as a `[cml][WARN]` that built anyway and filed `OI-72` as a new find. It was **not new** —
already documented as part of `BEN-244` at `FINDING-20260814-a-decision…:96` and in the lane-B entry above at
`:7531` — and lane A **did not grep for whether the defect was already known before filing it**, which is
*"inference from absence needs a covering search"* applied to novelty instead of existence. It was also **no
longer open**: lane B fixed it at **`4d04ceb`, 2026-08-14 19:45:25**, fail-closed by default with an explicit
`--allow-incomplete-family` escape that rewrites the output to a `NONQUOTABLE-DIAGNOSTIC.` path, plus
`tests/test_cml_family_completeness_fails_closed.py`. **Lane B's diagnosis is worse than lane A's:** at 1
member of 12 the builder exited **0** with **both files written**, and with `n−1 = 0` the covariance was
**entirely NaN** while the decomposition printed `subsample=0.000 estimator=0.000 interaction=0.000` — a NaN
matrix at the publication path under a clean-reading summary, into a log this filesystem block-buffers for
hours (`BEN-028`). **`OI-72` is withdrawn, and its id is kept rather than reused** because it is cited in a
landed commit message (`BEN-216`/`BEN-219`). **Lane A's measurement was correct where it was taken** —
`git show c29e3522:nd-unfolding/pet/combine_cml_bkgsub.py` still shows the `WARN` — and `4d04ceb` arrived in
the rebase between commit and push. **That is the second `BEN-225` instance tonight, and both were caught by
that finding's own remedy:** re-run every count, absence and line number after `git pull --rebase` and before
`git push`.

**Three bookkeeping items, all three of which the 08-14 lane-B entry above had already diagnosed:**

1. **`OI-23` DISCHARGED**, and **its residual was transferred rather than dropped.** Its own next-action cell
   said discharge was *"contingent only on `56563761` REMAINING the final nominal … (`artifact_promoted:
   False`)"* — a **superseded field value**: `annealed-nominal-complete-56563761.json:144` has read
   `artifact_promoted: true` since the promotion at `6b68d12`, `promoted_at_utc 2026-08-13T02:52:32Z`,
   **36 hours before this entry**. **But the row's *"contingent only on"* is wrong, and the promotion receipt
   says so in the same breath as the promotion:** `p3f-pet-gate4-nominal-promotion-56563761.json:102` lists
   *"That `OI-23` is discharged"* under `explicitly_not_claimed`, naming a **second** residual the row never
   mentioned — the closure's `quotable: False`. **So the row and the receipt disagreed, and the receipt is
   right.** `OI-23` is discharged on the configuration question only, with that residual carried to `OI-71`
   under its own id. Discharging it while silently dropping the receipt's stated reason would have been
   `BEN-244` committed knowingly.
2. **`OI-71` FILED** — the quotability of `VL100 = 0.512603276`, the recovery number the annealed physics
   argument rests on, from closure `56552326` whose every artifact is prefixed `NONQUOTABLE-DIAGNOSTIC.`.
   Tracked under **no id at all** before tonight; `WAITING-USER`, and **a tracker, not a verdict** — the
   assistant lane is determining quotability separately and lane A did not attempt to answer it.
3. **`next_dependency` CORRECTED** in `annealed-nominal-complete-56563761.json`, which carried
   `state: BLOCKED_ON_USER` eight lines below the `artifact_promoted: true` that superseded it. **Which of
   its three offered branches was taken is now recorded: branch 2**, *"accept the current production path as
   authoritative and separately authorize its promotion"* — evidenced by the promotion receipt, `verdict
   PROMOTED`, `6b68d12`. Branch 1 (the paired implementation-ablation) is recorded as **declined**, because
   the predeclaration declines it in its own words — *"No fourth run… A fourth run would refine `sd 0.0247`
   without changing any decision"* — the code-path finding having been retracted at `535668d`. Superseded in
   place using the file's own dated idiom, **value-only and additive, so `:152-156` still resolves** for the
   two entries that cite it by that span; per `BEN-219` both are left alone, having been correct when written.
   **AND THE POINTER CLAIM IS CORRECTED, INCLUDING THE VERSION IN THE LANE-B ENTRY ABOVE AND IN THE DISPATCH
   THAT ASKED FOR THE FIX.** Both describe `state/waker/BLOCKED-ON-USER.json` as, in effect, gone —
   *"does not exist (untracked at `a45f17b`)"*. The absence is confirmed (`git ls-tree -r origin/main` on
   `state/waker/` returns nothing, so it is tree-based and not a worktree artefact), **but *"no referent"* is
   wrong, and reading `a45f17b`'s body rather than its subject is what shows it.** That untracking was
   **Joseph's decision**: `.gitignore:11` ignores the `state/waker/` runtime spool, gitignore does not apply
   to already-tracked files, and this was the lone versioned file inside it — it *"collided on every
   shared-tree merge"* and was in the list that blocked the P4 cluster run. The commit body **preserves the
   contents** at `/pscratch/sd/j/josephrb/BLOCKED-ON-USER.preserved-20260811.json` and warns that pulling the
   commit **removes each checkout's working copy**, which is exactly why it is absent here. **So the referent
   exists, was named on purpose, and is merely unreadable from a local checkout — a deliberate decision, not
   drift.** Lane A did not read it (nothing in this dispatch went near the cluster) and invented nothing.

4. **A FOURTH ITEM, NOT DISPATCHED — a digest in a promotion receipt was already wrong, and the check that
   exists for exactly this said `ALL BINDINGS INTACT` while it was.** Found because correcting item 3 changes
   the edited file's sha256, so lane A went looking for who records it.
   `p3f-pet-gate4-nominal-promotion-56563761.json:74` read *"versus the git record `fc4fcbe863963b22…`"* —
   **and that value was stale before tonight's edit, not because of it.** Measured: the file at `c29e3522`
   hashes to `67c487cd0190…`. The receipt was edited after the note was written and the note did not follow.
   **`verify_hash_bindings.py` resolved 175 bindings and reported `ALL BINDINGS INTACT` with that digest
   wrong**, because **a sha256 written into prose is not a binding** — there is no `files`/`sha256` pair to
   resolve, so the one check built for this failure cannot see it, and neither can the receipt-binding floor
   of 140. Same shape as a green count being a statement about what ran rather than what was checked.
   **Corrected in lane A's own file** (`annealed-nominal-complete-56563761.json:150` assigns this receipt to
   Session A — *"Session A writes the separate promotion receipt against this commit's sha"* — so this is the
   one edit tonight that needed no ownership disclosure) **by removing the point value rather than refreshing
   it** — a digest of a concurrently-edited document is stale at its next edit, and refreshing it restarts the
   same clock. Replaced with the derivation (`git show <ref>:<path> | shasum -a 256`) plus both observed
   values **quoted with their refs**, which is the part that was missing. The cluster-side digest
   `81849396…` is left exactly as recorded and **explicitly not re-measured** — nothing went near the cluster.
   **Not filed as a `BEN-*` row or an `OI-*`**: it is one prose digest, now corrected, and the generalisation
   is already written in `CONVENTION-verifying-a-check-is-deployed.md`. Flagged to the mediator instead, since
   whether the verifier should learn to resolve prose digests is a scope question and not lane A's to settle.

**AND A SELF-INFLICTED VARIANT OF THE SAME TRAP, worth one sentence because it needs no concurrency at all.**
Two of this entry's citations were falsified **by this entry's own edits**: `STATUS:52` became `:59` because
the STATUS one-liner above it grew by seven lines, and the promotion receipt's `:95` became `:102` because
item 4 inserted a block above it. **`BEN-225` needs a rebase and another lane; this needs neither** — a line
citation into a file you are editing in the same commit is stale the moment you edit it, and it will not be
caught by re-running anything after the rebase unless the line numbers are re-derived rather than re-used.
Both corrected; caught by re-deriving every cited line with `grep -n` rather than trusting the numbers
recorded 40 minutes earlier.

**Nothing is unblocked by this entry.** Gate 6 is blocked at `19585b7`, all five prohibitions stand, Leg 0
runs first, and **an authorization to retry is an authorization to gather evidence, not a verdict.**

## 2026-08-14 — lane A, documentary: OI-71 carries D's falsification; two findings filed; the LIVE-STATE blocker cannot be regenerated away

**Nothing executed, nothing submitted, no cluster contact.** Four dispatched items; the fourth returned a
negative result that is more useful than the fix it was meant to confirm.

**1. `OI-71` NOW CARRIES THE FALSIFICATION, and the whole exposure is in one row.** Lane D's read-only test
at `f4267b4` (`state/vl100-foldforward-shape-test-20260814.json`, `BEN-252`) returns
`VERDICT: SHAPE-DEPENDENT. NOT scale-only.` **Re-verified from the object rather than relayed:** truth-grid
per-cell ratio `0.17301984808816961 → 1.4201434284841605`, `ratio_sd 0.3371` over `noise_expected_sd
0.004931` = **`observed_over_noise 68.36`**; reco grid corroborates independently at **`36.25`**; the
structure is in p∥ (marginal `0.272 → 1.321`, factor **4.9**) and is **not** a dead-cell artefact — those
cells sit *above* the global mean (`0.833` vs `0.717`), so excluding them would not rescue the argument. The
global-scale control is a real test: `k` fixed from the denominator alone reproduced the numerator to
`2.0e-13`. **The two framings reconcile and both are in the row:** `ratio_sd/noise = 68.36` is the same
statement as `rel_sd 47.0%` against a *relative* noise of `0.69%`.
**The three facts that were true in three separate files now sit in one cell**, which is the `BEN-244` shape:
`VL100` comes from a closure declaring `quotable: False`; that closure's quotability argument is falsified;
and `recovery_evaluated` remains `False` at the promoted configuration (`explicitly_not_claimed[2]`).
**AND ONE QUALIFIER RESTORED, which the dispatch assigning this row had dropped:** lane D examined **one of
the four** quotability grounds. The other three are hygiene rather than physics and were **not** looked at,
so *"the quotability argument has been falsified"* is true of the physics ground and overstated as a summary
of all four — `BEN-220`'s own class, applied to a relay of `BEN-220`'s author. D's other two limits are in
the row too: it does **not** say `VL100` is wrong, and it does **not** quantify how far `VL100` moves, which
needs a shape-corrected recomputation that **was not run**.

**2. `BEN-227` — a sha256 written into PROSE is not a binding.** A wrong digest in
`p3f-pet-gate4-nominal-promotion-56563761.json` survived `verify_hash_bindings.py` reporting
`ALL BINDINGS INTACT` across **175** resolved bindings **and** cleared `RECEIPT_BINDING_FLOOR=140` at 160.
Neither guard is broken: a binding is a `files`/`sha256` **pair**, and a digest in a sentence has none, so
both were **silent about a string shaped like their subject.** **Prose scanning was ruled against** — it
false-positives on every digest quoted as history, which `INDEX-retracted-and-superseded-values.md` does on
purpose. Prescription is the remedy already applied: **remove the point value rather than refreshing it,
write the derivation, quote every digest WITH its ref.** Scope ruled by the mediator after lane A declined
to rule it; the tooling question is left open in the row.

**3. `BEN-228` — a line citation into a file you are editing IN THAT COMMIT is stale the moment you edit it**,
and **`BEN-225`'s remedy does not catch it.** Re-running a check after `pull --rebase` re-runs the *check*;
it does not re-derive the *number*. No rebase, no second lane, no concurrency — **strictly cheaper to
trigger than `BEN-225`, so it will happen more often**, and every commit that both edits a file and cites a
line in it is exposed. Rule: derive after the last edit, search for the **content** not the line, and prefer
content addresses that survive insertion (`explicitly_not_claimed[2]`) over coordinates (`:95`).
**Also corrected while filing these: lane A's own block row said `221-229` free, wrong since `BEN-221`** —
`220-228` are filed and only `229` remains. That cell is the narration this table's own *"derived, not
narrated"* rule warns about, and it is now marked a hint rather than an authority.

**4. THE AUTHORIZED REGENERATION RAN, AND THE DEAD BLOCKER SENTENCE DOES NOT CLEAR. MY OWN HYPOTHESIS WAS
WRONG.** I had told the mediator that `ND_OMNIFOLD_STATUS.md:40` was the likely upstream of the reprinted
sentence. **It is not, and no STATUS prose is.** Measured: `generate_live_state.py:22` sets
`DEFAULT_CONFIG = state/live-state.json`, reads it at `:286`, and its only write target is
`DEFAULT_OUTPUT = LIVE-STATE.md` (`:23`, `:322`) — **the script never writes `live-state.json`.** The dead
sentence is `live-state.json`'s `blockers[3]`, i.e. **the generator's hand-authored INPUT**, reprinted
verbatim at `LIVE-STATE.md:53`. Run with `--stdout` so nothing was published: the regenerated output differs
from the committed file in **exactly three things** — `Observed:`, the `Git:` sha with its worktree count,
and one trailing newline. **The blocker text is byte-identical.**
**And the reason it has survived is a documented falsehood:** `MANIFEST.tsv:616` classifies
`live-state.json` as `MACHINE / state-artifact / generated` **naming `generate_live_state.py` as its
producer** — a script that only ever reads it. **So the one file that can retire the sentence is the one
every agent correctly believes is generated and must not be hand-edited, and the prescribed remedy —
regenerate — is provably incapable of clearing it.** Filed `OI-73`; `OI-70`'s class, worse instance, because
this one inverts a control-plane data flow rather than mislabelling a document's lifecycle. **Neither file
was edited** — the dispatch that authorized the regeneration also forbade hand-editing them, and naming the
file was the instruction. Two things left for whoever owns it: `blockers[2]`'s *"no retry"* needs the word
**unchanged**, and **regenerate only from a clean tree** — the `Git:` line published `worktree entries: 4`
from lane A's dirty tree against `1` committed, which is `BEN-183` waiting to happen.

## 2026-08-14 ~23:00 EDT / 2026-08-15 03:0xZ — Gate 6 Leg 0 (tier calibration): code + launcher PREPARED, NOTHING SUBMITTED

`--checkpoint-tier {auto,best-epoch,final}` added to `nd-unfolding/pet/step1_increment_trajectory.py`
(`48f8353d` → `ca2128ac`), defaulting to `auto`, which is byte-for-byte the pre-flag rule — **zero existing
callers change.** The tier resolver was lifted out of `main()` to module level so it is testable without the
TensorFlow stack `main()` imports; `nd-unfolding/tests/test_step1_trajectory_checkpoint_tier.py` is 13 tests,
including a power proof that reconstructs the pre-flag resolver and requires the no-fallback assertions to
reject it. An explicit tier **never** falls back, because a silent downgrade would make a best-vs-final
contrast compare a tier against itself and measure the gap as zero — the exact conclusion the leg tests.

**The PLAN's Gate-4 claim is right and its launcher claim is wrong, and both were derived rather than
relayed.** `step1_increment_trajectory.py` appears in none of the 138 string leaves of
`p3f-pet-gate4-launch-code-gate-20260813.json` (19 distinct pinned paths) → **no Gate-4 re-issue.** But the
sha is hardcoded in **three** launchers, not one, and **two of those launchers are hash-bound by active run
receipts**, so the in-place re-pin the PLAN describes is not available: it was made in all three, and
`verify_hash_bindings.py` returned rc=1 with two MISMATCHes plus a red `test_hash_bindings.py`. Reverted to
byte-identical rather than "fixed" — that verifier's docstring forbids repairing a stale pin by editing the
hash, and both receipts are submit-time provenance of COMPLETED runs. Filed `BEN-270`; residual hazard
`OI-123`.

**So the new pin lands in a NEW launcher**, `nd-unfolding/pet/sbatch_gate6_leg0_tier_calibration_array.sh`,
which runs from a mandatory `G6_LEG0_CODE_REPO` and explicitly refuses both `gate6-reconcile-56834281` and
the frozen `gate6traj-reconcile-56847059` (guard exercised against a trailing slash and against a
symlink whose name is innocent but whose target is frozen). All three existing launchers are untouched and
their pins remain correct against the scratch tree they actually read, verified still `48f8353d` there.

**NOT SUBMITTED, and the report precedes the submission by instruction.** Nothing of this user's is running
or queued that pins the edited file — `squeue -u josephrb` at 2026-08-15T02:53:55Z shows only `56585597`
(scrontab, PENDING/BeginTime). Jobs `56978466` (FAILED 17:39:53) and `56975592` (COMPLETED 17:36:40) belong
to other lanes and were read via `sacct` only; no `scancel`, no `scontrol update`, no resubmission.

**What Leg 0 does NOT do, restated because it is a constraint:** member 3 is not promoted, selected or
removed; the family still blocks on 2, 4 and 5; no `C_ML`, no Leg F, no Leg X, no member selection, no
central move. All five Gate-6 prohibitions at `19585b7` stay live and this clears none of them. The only
thing it can change is the **fault description** the retry must explain — three real failures or four.
Threshold `0.0010978917643007513` re-derived here from the committed receipt's own
`absolute_deviation_from_one` array, not taken from the brief; all five rows of the PLAN's section-1a table
reproduce from that receipt. Products summary:
`docs/orchestration/state/gate6-leg0-tier-calibration-prepared-20260814.json`.

## 2026-08-14 — P5A annealed extraction: `56978466` diagnosed, launcher repaired to the two-environment split, HELD UNSUBMITTED

Job `56978466` (`p5a_ann_extract`, `nid001585`) FAILED `6:0` after `00:12:57`, 2026-08-14
17:26:56–17:39:53 PDT = 2026-08-15T00:26:56–00:39:53Z. Timezone frame established rather than assumed:
`sacct` reports Pacific, the launcher's `[p5a]` lines and the `.done` sidecar report UTC, and the
sidecar's epoch `1786754388` reconciles the two.

**Neither a physics nor an identity failure, and the record should say so plainly.** All six guards
`G0`–`G5` passed — arm-by-schema (`lr_policy.schedule = fit-time-anneal-after-iteration-0`), weights
`559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e`, inputs
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625`, checkpoint contained, outputs
outside the arm. Exit 6 is `sbatch_p5a_fullevent_nominal_extract.sh`'s "extraction driver failed".

**The expensive work succeeded and is on disk.** The reweight completed `49152885/49152885` and wrote
`fullevent_nominal_annealed_extraction_unpromoted/P5A-ANNEALED-UNPROMOTED.push.slurm-56978466.npz`;
its own subsample-agreement check passed at `max_rel_dev 2.554037696012494e-05` against `tolerance
1e-3`, with `subsample_agreement_is_vacuous: false`. Re-verified independently this turn: `sha256
a1debdb7105f3e531ec2e6ec5e08192d026238d5bac7eb5fe389e7e8f71bb9c9`, 262448947 bytes, regular file,
zip intact, 11 keys, `w_push` 49152885 float64 all-finite, `mc_indices` exactly `arange`,
`validate_push_coverage → []`, `inputs_sha256` equal to `G4`'s pin, `source_weights` resolving to the
annealed arm. Recomputed `w_push` min/max/mean `0.3674599826335907 / 8.050625801086426 /
1.0630889183749077` reproduce the stored telemetry exactly.

**The failure was an interpreter choice.** `extract_fullevent_fps.py:463` → `2d-unfolding/
unfold_2d_omnifold_unbinned.py:21` → `ModuleNotFoundError: No module named 'ROOT'`. The driver's own
header (`:16-23`) already states that `xsec` "needs ROOT and numpy, no TensorFlow, no GPU" and that the
stages are split so the GPU push is not re-spent; the launcher ran `--stage all` under
`tensorflow/2.15.0`, which carries no ROOT.

**Repair (`cd31545859e58ecde1f0fecec59dbac76bd7e91d185057045c9b3c50e4f03d11`).** Two-environment split
after `sbatch_gate5_replica_extract_array.sh`, which was **read as a template only** — it is hash-bound
by an active receipt and editing it would fail `verify_hash_bindings.py`. `G0`–`G5` are **byte-identical**
to the version that ran (region diff empty, 83 lines both sides; the exact ran-bytes remain recoverable
at `git show HEAD~:…` = `5da812f8ca3ab955ba568efa656f9379c5c948d195d1f051a4f466888583ba8b`). Added
strictly on top: `G6` push reuse gated on identity not existence (`BEN-023`'s class — sha pin, `.done`
marker, schema/fingerprint/coverage, inputs-sha agreement, non-vacuous agreement check) and `G7` a ROOT
import preflight ordered **before any long work**, sharing one `root_env_run` definition with the real
`xsec` stage.

**Measured, and it is why the naive repair would have been wrong:** invoking
`$ROOT628_PREFIX/bin/python3 -c 'import ROOT'` directly **segfaults** (rc=139, cling "cannot extract
standard library include paths"); it works only once `setup_salloc_env.sh` has activated the env by full
prefix. Verified working combination: ROOT `6.28/12`, numpy `1.26.4`, `unfold_2d_omnifold_unbinned` and
the driver both importable.

**Power tests, both new guards, both directions:** wrong sha pin → `rc=7` with zero `G6 PASS` lines;
payload with no `.done` → `rc=7` "must be treated as PARTIAL"; `ROOT628_PREFIX=/usr` → `rc=8`
reproducing `56978466`'s exact `ModuleNotFoundError` in seconds at zero GPU cost. Real payload + real
env → `rc=0`, `G0..G7 all PASS, no job submitted, no GPU used`.

**NOT SUBMITTED — the report precedes the submission by instruction, and the mediator's go is pending.**
No `scancel`, no `scontrol update`, no other lane's job touched; `56978466` was read via `sacct` only.
`/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` untouched. **Promotion is NOT authorized and
nothing here performs it:** outputs stay in `fullevent_nominal_annealed_extraction_unpromoted/`,
`MARK=P5A-ANNEALED-UNPROMOTED`, and `NOT_CANONICAL.json` is still written — now also carrying the push
provenance sha and, discharged for the first time, the OWED VL100 scope annotation (D's **physics**
ground falsified at `f4267b4`, per-cell ratio 0.173→1.420, 68× clear of noise; the other **three**
grounds are hygiene and were **not** examined, so the argument as a whole is **not** falsified).
Finding: `BEN-280`.

## 2026-08-14 — OI-120(c) verdict repair: `56975592` printed `LEAKAGE` and its own arms said the opposite

**No cluster work. Nothing submitted, nothing cancelled, no `scontrol`.** Job `56975592` was read only
from its preserved stdout, already copied off `/pscratch` by Joseph. This is lane D's probe and **lane D was
not running: the mediator diagnosed the defect, this repair lane verified and applied it, and D did not
review it.**

**PRINTED VERDICT** (job `56975592`, COMPLETED, exit 0):
`LEAKAGE -- event_reco changed when only a truth array changed`

**CORRECTED VERDICT** (same recorded arms, replayed off-cluster, nothing re-run):
`NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations, through the production loader`

Both are recorded, and the printed one is not deleted anywhere: a reader must be able to see that the tool
said `LEAKAGE` and why that was wrong.

**The arms, which is why the headline was falsifiable at all.** Baseline `event_reco` sha256
`8c88e15968f5c1962678f16ae1bb0646522fcf55bfa8412bfe067c59472e8bf5`, shape `[49152885, 13]`, `float32`.

| arm | perturbation | expected | observed |
|---|---|---|---|
| `P0` | `reco_scalars` x1.01 (CONTROL) | `CHANGED` | `CHANGED` → `e665e9604dcf2d011ddf56382b3475d8cab9843f37068281f4b992cd97c01393` |
| `P1` | `truth_scalars` x1.05 | `IDENTICAL` | `IDENTICAL` (baseline sha) |
| `P2` | `truth_scalars` rows permuted | `IDENTICAL` | `IDENTICAL` (baseline sha) |
| `P3` | `part_gen` (truth cloud) x1.05 | `IDENTICAL` | `IDENTICAL` (baseline sha) |
| `P4` | `w_truth` x1.05 | `IDENTICAL` | `VOID` — `arrays_actually_changed: {}`, `proxy_hits: 0` |

The control fired, so the probe had demonstrated power; three real truth perturbations (each confirmed to
have landed by the proxy) left `event_reco` bit-identical. **That is a clean negative result.** The one
failing arm failed by **not running**.

**CAUSE — one token.** The arm flag is tri-state: `True` ran-and-matched, `False` ran-and-**CONTRADICTED**
(the only value that may produce `LEAKAGE`), `None` did-not-run-**exclude**. At `f6a52ed`, `:219` assigned a
`VOID` arm `False`; the scoring filter at `:232` excludes on `is not None`, so an arm that never ran entered
the scored set, forced `clean` False, and the verdict fell through to the `LEAKAGE` else-branch. **The
probe's own docstring at `:41-44` already stated the intended semantics** — *"a perturbation that did not
perturb turns 'no leakage' into 'no test'"* — so the docstring was right and the code was wrong. Fixed to
`None` at `:224` (`143f859`).

**Caught only because the receipt shipped its ingredients** (`BEN-077`, `CONVENTION-receipt-ingredients.md`;
second defect this heuristic has caught with nobody suspecting one). The verdict sentence is unfalsifiable
alone — a `LEAKAGE` headline on a leakage probe is what a real leak looks like. The per-arm `sha256`,
`arrays_actually_changed` and `proxy_hits` published beside it made the contradiction **arithmetic**.

**Direction: it failed ALARMING, not quiet** — a void arm can never make a dirty run look clean, because
`clean` is an `all()` over a falsy injection. Strictly the safer direction, and still not free: truth leakage
is the campaign's most load-bearing purity property, so a false `LEAKAGE` competes for exactly the attention
a real blocker would need.

**Regression, written BEFORE the fix and observed failing on it:**
`docs/orchestration/test_probe_oi120c_verdict.py` — **3 of 6 RED** at `f6a52ed` (the three reproduce the
job's exact printed string off-cluster in 0.06 s), **6 of 6 GREEN** at `143f859`. It pins **both**
directions: a void arm must not manufacture `LEAKAGE`, and a genuinely `CHANGED` truth arm must still
produce it (green before and after by design, so the fix cannot be satisfied by deleting the detector). Its
arms are parsed out of the preserved stdout rather than hand-written, so the headline test is a **replay** of
`56975592`, not a re-enactment.

**`P4` is a real open question and is NOT closed — `OI-124`. The offered hypothesis is REFUTED.** The
dispatch suggested the loader/trainer consumes its own weights rather than the NPZ's raw arrays. Measured
against `HEAD`'s `nd-unfolding/pet/fullevent_fps_dataloader.py`, it does not hold: `:1121` opens the NPZ,
`:1251` `w_truth_full = np.asarray(d["w_truth"])` is the **first and only** read of the key, and the
trainer's weights **are** derived from it (`:1323`/`:1332` → `weight=w_truth` at `:1349`). The real cause is
the probe's own early-stop ordering, and it is **structural**: `event_reco` is fully assigned at `:1241`,
ten lines before `w_truth` is ever read (`awk 'NR>=1121 && NR<=1241 && /w_truth/'` returns nothing; the keys
read in that window contain the three arms that fired and not `w_truth`). So `P4`'s predeclared `IDENTICAL`
is **true by control flow** and no perturbation of `w_truth` can make that arm fail there. It was not a test
that missed — it was a test that could not exist where it ran. **Limit:** those line numbers are from the
local checkout at `HEAD`; `/pscratch` was not read. Corroboration, not proof — D's probe docstring,
written against the cluster tree, independently cites `:1241`/`:1247` and the local file matches exactly.

**PRESERVED ARTIFACT, and it was the only copy.**
`docs/orchestration/state/oi120c-loader-purity-perturbation-56975592.txt`, 5047 B, sha256
`ec5581363f440b153057126996e30f2325cf63c94b27442559a087046522912c`. Now tracked, verified with
`git ls-files` rather than `git add`'s exit code (`BEN-260`).

**Not fixed on purpose, to keep an unreviewed edit to one token:** the all-void `UNRESOLVED` branch is
worded *"the loader refused every truth perturbation"* when `VOID` is not `REFUSED`, and the per-arm print
labels a void arm `REFUSED` while its `observed` column still reads `VOID`. Both in `OI-124`.

Findings: `BEN-290`. Code debt: `KNOWN_ISSUES` 49. Claim evidence pointer (no state change): `CLM-002`.

## 2026-08-15 — Gate 6 LEG 0 SUBMITTED as array 56993778_[1-5]; Gate 6 stays blocked

**Authorized by Joseph (`AUTHORIZATION-20260814-gate6-retry.md`, `043d572`), sequenced by the mediator, submitted
by lane A. Inference only, no training, 01:00:00 walltime, 1 GPU, `qos=shared`, account `m3246` — inside the
standing 12 h authorization.**

**Job identity read from `squeue`, not from `sbatch`'s stdout** (`sbatch` printed `56993778`; `squeue -j 56993778 -r`
is what is quoted here). At `2026-08-15T04:28:48Z`: array **`56993778_[1-5]`**, name `g6_leg0_tier`, **all five
tasks `PENDING`, reason `(None)`**. `sacct -X -P` corroborates, `Submit 2026-08-14T21:28:39`.
**THE FRAME, established in the same turn rather than assumed** (`BEN-233`): `sacct` printed `21:28:39` against
`date -u` `04:28:48Z`, so `sacct` is on **UTC−0700** and `21:28:39` PDT **is** `04:28:39Z` — 9 s before the UTC
read, consistent. No timestamp here is compared across frames.

## Why Leg 0 needed a new checkout, and the finding that came out of building it

The launcher requires `G6_LEG0_CODE_REPO` and refuses both frozen trees. **The obvious candidate could not be
used and neither could the science repo:** `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is at **`683bdcc`**
(`2026-08-11T08:01:25-04:00`), carries **751 uncommitted paths**, and **`git cat-file -t 692c6bd` returns
"Not a valid object name"** — the commit adding `--checkpoint-tier` does not exist in the tree every launcher
reads as `SCI_REPO`. **Filed as `OI-74` on its own** rather than inside this leg's receipt, on the mediator's
instruction, because *the workaround removed the symptom without touching the cause* and the next lane to
trust that tree will not be running Leg 0.

**Checkout: `/pscratch/sd/j/josephrb/gate6-leg0-fa14db5`.** Cloned from the science repo (read-only on it) and
then fetched from GitHub for the missing commits. Verified: `HEAD fa14db5`, **`692c6bd` IS an ancestor**
(`git merge-base --is-ancestor`), **0 dirty**, and `step1_increment_trajectory.py` = `ca2128ac…`, which is the
digest the launcher enforces at `:125`.

**Frozen trees verified untouched AFTER the clone, not merely left alone:** `gate6-reconcile-56834281`'s
trajectory file is still `48f8353d…` (pre-flag, correct for that tree), `gate6traj-reconcile-56847059` was
never read or written, and the science repo re-measured at `683bdcc` with the same 751 paths.
**`verify_hash_bindings.py` returned `ALL BINDINGS INTACT` twice** — baseline in lane A's local worktree before
anything, and inside the new checkout afterwards. **Nothing was re-pinned and no digest was edited.**

## A dry check was built because the launcher has none, and it is the reusable part

30 read-only checks replicating every guard that does not need a GPU, run on a login node in seconds:
the frozen-tree guard against both the raw and canonicalized `CODE_REPO`; the sbatch log directory (which
lives **outside** the checkout, so a missing one loses the logs rather than failing loudly); all 7 `CODE_PET`
pins plus the engine; the archived target `544b2f6a…`; per member 1–5 the artifact/`.done` pair, the artifact
sha against the `56847059` set, and the absence of any pre-existing `leg0-tier` output; and **the forced
tier's own precondition — all 6 best-epoch checkpoints present per member**, without which a missing file
surfaces as a mid-run `SystemExit` after ~10 minutes of GPU. `DRYCHECK: ALL PASS`, re-run immediately before
`sbatch` in the same command.

## The threshold, derived rather than accepted

From `gate6-member-trajectories-result-56847059.json` directly: member 3's
`absolute_deviation_from_one` = `[0.05647845006729013, 0.04155197108751185, 0.0426498628518126]`, so
`nonincreasing` is false because **iter2 exceeds iter1**, and the margin is
`0.0426498628518126 − 0.04155197108751185` = **`0.0010978917643007513`**. Bit-for-bit equal to the figure
relayed by the mediator — **the only relayed number of the campaign's last day to survive derivation
unchanged**, against four that did not.

## WHAT LEG 0 CANNOT DO, written here and not only in the receipt

**Member 3 is NOT promoted, selected, or excluded**, whatever it returns. The family still blocks on **2, 4
and 5**. **All five prohibitions at `19585b7` stay live and this leg clears none of them** — a changed retry
was never inside `do_not_retry_unchanged`'s scope, so there was nothing to lift. No `C_ML`, no Leg F draw, no
Leg X. **If the measured tier gap exceeds `0.0010978917643007513`, the only thing that changes is the fault
description the retry must explain** — from four real failures to three.

**Liveness will be judged by `sstat` CPU time and produced artifacts, never by log growth**: on this Lustre
filesystem `st_blksize` is 4 MiB and a healthy multi-hour run can emit zero progress lines (`BEN-028`).

## Two corrections against lane A, both found by lane A

1. **Lane A duplicated `692c6bd`** — independently building the same flag, a regression test and the same
   three-pin discovery while that work was already landing. **The commit was dropped** (`reset --hard
   origin/main`) rather than merged, because two implementations of one function is how a subtle defect lands,
   and `692c6bd` additionally carries the launcher and prepared receipt. **Nothing of lane A's survives.** The
   mediator has recorded the cause as its own double-dispatch.
2. **Lane A's earlier "this session cannot submit Leg 0" was a false conclusion from a true measurement.**
   `which sbatch` → not found and `/pscratch` absent are both correct **of the local shell**, and neither
   covers the configured NERSC ssh route that this submission used. **A null result from a non-covering search
   is not evidence of absence** — the defect lane A had been flagging in others all evening, committed against
   its own capabilities. Retracted before it reached a receipt; the claim never landed in a commit.
3. **And a third, about a checker lane A wrote:** the cell-count audit `awk -F'|'` used in earlier entries
   **counts `\|` escapes as cell separators**, so its report that `OI-56` carries 9 cells was wrong — `OI-56`
   carries **7**, correctly. `OI-30` and `OI-62` at 8 are real. **A naive splitter reported a document defect
   that was an artifact of the splitter**, which is `BEN-186`'s shape: the instrument was never validated
   against a case it would get wrong.

## 2026-08-15 — documentary: the VL100 falsification was a MIS-TARGET, not a refutation, and the mediator propagated it into three places

**Nothing executed, nothing submitted, no cluster contact of any kind.** No `sbatch`, no `scancel`, no
`scontrol`; `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` untouched. Local reads and edits only.

**THE CAUSE, NAMED: the mediator session relayed lane D's finding as established into three places —
`OI-71` (via the dispatch that had lane A write it), the P5A `NOT_CANONICAL.json` output contract (via
lane C), and a user report — before checking which artifact the finding measured.** This entry corrects
that propagation. It is not a record that drifted on its own and must not be read as one.

**WHAT IS ACTUALLY THE CASE**, established at `66c1f0e`/`5ce5e2f` and re-verified here from the object
rather than relayed: `NONQUOTABLE-DIAGNOSTIC.manifest.slurm-56552326.json` carries `job_id 56552326` and
the annealed closure's own `push_sha256`, then names `weights_path`/`weights_sha256` = the **pre-anneal**
`fullevent_nominal/` file and computes its `fold_forward` block, its `rejection_reason` and
`publication_gate_rejects_this_on_physics_alone` **from that file**. So **lane D read exactly the artifact
the manifest names as the source of its own rejection — D followed the record, and the record is what is
wrong** (`BEN-312`). D's arithmetic reproduces exactly and is presumably correct *about the pre-anneal
nominal run*. **The physics ground is MIS-TARGETED, not falsified**, and `"NOT QUOTABLE on the physics
alone"` is a true statement about a run that is not this one. Separately, *"one of the four quotability
grounds, the other three hygiene and unexamined"* was a **count with no members** (`BEN-313`).

**Routes, not numbers** (`BEN-227`/`BEN-228` — a receipt value copied into a second file diverges from it):
`state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json` for every figure with its operands,
`FINDING-20260815-the-quarantine-measured-a-different-run.md` for the grounds reconstruction,
`FINDING-20260815-a-restatement-is-not-a-second-measurement.md` for the mechanism.

**FOUR FILES CORRECTED**, all *beside* lane D's work and none of it touched — `f4267b4`, D's finding text,
D's receipt and D's rows are unaltered, and D is not running:

1. **`docs/OPEN_ITEMS.md`, `OI-71`** — lead cell, `(2)`, `(3)`, `(4)`'s attribution, the count sentence and
   the closing-carelessly warning. The `(2)` number pile is **gone and replaced by routes**, since it
   restated D's receipt values into a second file. Refs column now also carries the correction receipt,
   both 2026-08-15 findings and the un-submitted proposal. Row still declares `WAITING-USER`, **now on
   `G4` alone**. Lane A filed this row and the mediator's text is what was corrected in it.
2. **`nd-unfolding/pet/sbatch_p5a_fullevent_nominal_extract.sh`** — the **generator** of the
   `NOT_CANONICAL.json` contract, header comment and the `vl100_quotability_scope` /
   `promotion_would_require` / `THE_GAP` keys. The key now leads with a `STATUS` field stating that any
   emitted copy lacking it predates the correction. **The header edit is deliberately line-count-neutral
   (13/13) so that `sbatch_p5a_fullevent_nominal_extract.sh:153-182`, cited for guard `G1` in two
   committed receipts and in `BEN-311`, still resolves to `G1`.** Verified: `bash -n` clean, all three `PY`
   heredocs compile, and the generator was **executed** against stub arguments — it emits valid JSON, the
   corrected keys are present, and `0.173`/`68x` no longer appear anywhere in the emitted document.
3. **`docs/orchestration/HANDOFF-20260815-0455Z.md`** — the `OI-71` bullet, corrected in place and marked
   as having been wrong, because this file is what a new session is told to read first.
4. **`VALIDATION_LEDGER.md`** — the `VL100` pointer paragraph gains the `BEN-312` attribution (the manifest
   named the arm) and the `BEN-313` retraction. Still routes, not numbers; the `VL100` row itself untouched.

**DELIBERATELY NOT EDITED, and why — each of these still carries the superseded phrasing:**

* **The two earlier entries in this log** (`:7686-7712` lane A's, and the P5A submission entry at `:7845`).
  This file is **append-only chronology**; they record what was believed when written and this entry is the
  correction beside them.
* **`state/p5a-extraction-submitted-56978466.json:67`**, **`state/RECEIPT-vl100-shape-corrected-foldforward-20260815.json:14`**
  and **`state/probe-vl100-shape-correction-scan-20260815.py:174`** — emitted receipts and the probe that
  wrote one. A receipt records what its run asserted; rewriting one destroys that. `BEN-313` is already
  filed against the middle one.
* **The P5A products already on `/pscratch`** under `fullevent_nominal_annealed_extraction_unpromoted/`.
  Their `NOT_CANONICAL.json` carries the old text. **The generator is corrected; the emitted artifacts are
  not, by instruction**, and the new `STATUS` key is how a reader tells the two apart.

**NOT ESTABLISHED BY THIS LANE, and not claimed:** the two arms' digests and `seed_policy` schemas
(`58f664cd…` with no `lr_policy` key vs `559a1020…` at `fit-time-anneal-after-iteration-0`) were **not
re-measured here** — the `.npz` files are not in this checkout and the cluster was not contacted. They are
cited from the correction receipt, which enumerates the schema keys. What *was* verified locally from the
object is the manifest's own pointer set, which is the part this reframing rests on. **`OI-71` stays OPEN
on `G4`; no closure run was submitted and none is authorized without Joseph.**

---

## 2026-08-15 — THE 63-CELL "SPARSE EDGE" IS NEITHER SPARSE NOR AN EDGE; ITS "3.1% OF THE CROSS-SECTION" IS 15.5%; AND P5A SITS OUTSIDE ITS OWN 50-REPLICA FAMILY

Peer session `B`, on the mediator's dispatch to characterise the tail of
`state/p5a-nominal-vs-cstat-family-percell-20260815.json` and decide whether those cells belong in a
published measurement. **Read-only on the cluster; no mask, `C_stat` or extraction product was touched.**
All operands: `state/RECEIPT-20260815-cstat-tail-geometry-and-weighting-correction.json`.

**The receipt's arrays carry no cell ids, so the binding was PROVEN before anything was built on it:**
`per_cell_family_rel_sd` equals `sqrt(diag C)/mean` on `cell_index[quotable_mask]` to `5.5e-16`, and
`per_cell_ratio` equals nominal/mean recomputed from the 50 **raw** member `npz` to `6.0e-16`. Six of the
receipt's scalars then reproduce exactly. The 257 are the 262-union minus the 5 flicker cells.

**1. THE PRIOR UNDER TEST — "they are the thin edge and overlap the dead and flicker sets" — IS REFUTED
ON ALL THREE COUNTS.** One contiguous 4-connected band at **p_parallel 6–20 GeV** across nearly every
`pT` row, bounded by well-behaved cells on both sides. Overlap with the 23 dead and 5 flicker cells is
**zero and definitionally so** (dead are outside the 262; flicker is excluded from the 257 by
`CSTAT-D3c`), so adjacency was the only meaningful test and **1 of 63** touches either. Median acceptance
`a_b` **0.859** — the **highest on the grid** — holding **26.5% of all reco-accepted truth mass**. The
genuinely sparse region is the opposite corner: `p_parallel < 1.5` is 21.1% of truth mass and **0.24%** of
reco-accepted mass. **And spread is ANTI-correlated with acceptance** (median `relSD` 0.050 where
`a_b<0.05`, 0.243 where `a_b>0.5`), because where acceptance vanishes the answer is the prior and the
prior does not fluctuate across replicas — **so low replica spread means prior-dominated, not
well-measured**, which disqualifies any spread-based tier rather than merely weakening it.

**2. TWO OF THE RECEIPT'S DERIVED FIGURES WERE WRONG — `BEN-340`, filed with a detail file.** Its
`WHY_THIS_OVERSTATES` attributes `1.10267 → 1.05656` to a **domain** mismatch; both are over the **same
257 cells** and the step removes the **bin widths**. `sum(nom·width)` reproduces the receipt's own
`nominal_total` to `2.9e-5` (residual = the 5 flicker cells, to `0.7%`; confirmed at source by the
extraction's `total_sigma_cm2_per_nucleon`) while the unweighted sum is `11.3x` off. **So the `+10.267%`
survives.** *"3.1% of the cross-section"* was the tail's share of the **unweighted family-mean density
sum**; of the published nominal integral it is **15.5%**. Caught only by failing to re-derive a published
total from published operands — `BEN-077` working as designed.

**WHAT SURVIVES AND IS STRENGTHENED, stated because a correction reads as a demolition:** the median
per-cell ratio is weighting-independent and stands, and dropping the 63 moves the width-weighted total
ratio to **`0.99471`** — a stronger statement of *"concentrated, not global"* than the receipt made.

**3. PRECEDENT SETTLES THE TIERING QUESTION, AND IT IS OUR OWN PREDECESSOR.** All **63 of 63** are cells
MINERvA published: the release grid is `1.5 < p_parallel < 60` and the band's edges are its edges. Derived
independently from `2d-unfolding/minerva_paper_anc/bin_mapping.txt` → **224** paper cells, matching the
count `AGENTS.md` states. In that release (**Phys. Rev. D 104 (2021) 092007**, corrected from the 2020
paper this lane first cited) **19 bins are unreported and every one is in the `theta_mu<20°` corner** —
removed by the *signal definition*, never for being statistically weak; the paper says the bins *adjacent*
to the hole have **lower efficiency** and reports them anyway. **MINERvA measured the same 84 bins at a
median fractional statistical uncertainty of 1.6%** where this family's spread is **67%**.

**4. THE FINDING THAT OUTRANKS THE TASK — `OI-126`, filed separately so a *"change nothing"* tiering
conclusion cannot absorb it.** The P5A nominal **exceeds all fifty replicas in 44 of the 63 cells** (and
at least 45 of 50 lie below it in **every** one), while agreeing with the family at `p_parallel<6`
(median z `−0.13`). Sign reverses above 20 GeV. **Not skew** — `nom/median` is worse than `nom/mean`.
Leading candidate, **measured but NOT established as the cause**: the arms use different Stay-Positive
backends (nominal `precomputed:gate2-published-target`, learned; replicas recompute `exact` on
`max_mc_events=200000`). **Ruled out**: same driver, same anneal, same `niter`, same rows, same inputs
sha256, identical POT/nucleons/flux/`n_pass_truth`/domain. **The diagnostic is costed and NOT submitted —
it is a submission and it is Joseph's.**

**RECOMMENDATION, and it is a recommendation and not an act:** keep all 262 cells, change nothing, open no
new tier, and treat the divergence as a blocker on P5A promotion and on quoting `C_stat` as P5A's
statistical covariance.

**DELIBERATELY NOT DONE:** the mask, `C_stat` and every extraction product are untouched; no job was
submitted; the corrected receipt's original values are **retained beside** their `RETRACTED` markers
rather than overwritten (`BEN-227`); and **`MANIFEST.tsv` is one line stale for `FINDINGS.md` after this
commit — left so deliberately**, because regenerating it would have inventoried this lane's then-uncommitted
files (`BEN-332`; the correct precondition is `git status -- docs/orchestration` clean, not a worktree).

---

## 2026-08-15 — THE `OI-126` DIAGNOSTIC JOSEPH AUTHORIZED DOES NOT EXIST AS AN OPERATION, AND THE OBSTRUCTION ANSWERED PART OF THE QUESTION

Peer session `B`. Joseph authorized the `OI-126` re-extraction verbatim (*"Yes submit it"*). **Nothing was
submitted, no GPU time was spent, and nothing should be submitted for it:** the operation it names has no
entry point. **The un-runnability is this lane's error, in `OI-126` as first committed at `c1e7a69`.**

**Four fail-closed guards form a closed ring.** `train_fullevent_replica.py:320` refuses any
`replica_index` outside `[0,50)` or any seed other than `50000+index` — there is no value meaning
*bootstrap disabled*; `build_fullevent_replica_target.py:153` applies the same constraint, so the replica
path cannot build a non-replica target; `fullevent_fps_dataloader.py:736-747` refuses a nominal target
inside the replica path (*"can never stand in for one"*); and `train_fullevent_nominal.py:253-255` is the
mirror, refusing any target that carries a `bootstrap_seed`. They trace to the J04/D2 audit. **Weakening
one is a different authorization from spending GPU time and is not covered by an authorization to submit a
job** (`OI-123`, one level up). Recommended against even asking.

**How the error happened, because the generalisation is reusable and is now in `BEN-340`'s finding:** the
cost was derived from a replica receipt's real `total_seconds`, and *runnability* was inferred from the
existence of the two named scripts. **A proposal has two independent preconditions — affordable and
possible — and the expensive-looking one is not the one that fails.** The tell is the same as `BEN-340`'s:
**the derivation was never attempted.**

**WHAT THE OBSTRUCTION BOUGHT.** The guards prove the arms' targets differ **by design** — the nominal
consumes the certified published target, each replica must rebuild its own — so *whether* they differ was
never the question. That retired the hypothesis the job existed to test, before the job.

**MECHANISM NARROWED READ-ONLY INSTEAD.** Receipt
`state/RECEIPT-20260815-oi126-mechanism-narrowing.json`; both probes and the cluster probe's verbatim
stdout are committed beside it.

1. **The target is NOT the mechanism, and `OI-126`'s own leading candidate is REFUTED.** Each replica
   target is the nominal target times a **Poisson(1) multiplicity** times one shared constant:
   multiplicity fractions match the Poisson(1) pmf for `k=0..5` to better than 0.5%, the zero fraction is
   `exp(-1)` to `8e-4`, totals agree to `6.5e-5`, and on rows both arms keep **the two refinements agree
   to 0.068%**. The `refinement_backend` metadata differs; the arrays do not. **A metadata difference was
   read as a physics difference** — the same class of error as the costing above, on the same day.
2. **Shrinkage toward the prior is REFUTED, and it inverts the suspicion.** In the band the **nominal
   agrees with the MC prior to ~5%** while the family mean is **~0.4x the prior** — not between them (3.2%
   of the 63 cells) — and the band is not where the nominal departs most from the prior. **It is the
   replicas that are anomalous, not the nominal.**
3. **Not a subset of diverged trainings.** All 50 members are low in the band (median member/nominal
   `0.246`) and healthy below it (`1.015`, sd `0.037`), and a replica's band deficit is **uncorrelated
   with its overall level** (`r = 0.09`).
4. **The deficit is a function of `p_parallel` alone.** `log(mean/nominal)` is explained `R^2 = 0.868` by
   `p_parallel` alone against `R^2 = 0.018` by `pT` alone; three cells in different `pT` rows sharing
   `p_parallel[8,9)` give `4.985 / 4.950 / 4.938` with identical member counts. **A separable
   multiplicative factor is not a statistical effect.** It points at the replica extraction path, where
   `gate5_signal_factor_applied_to_truth_counts` is `true` and the nominal's summary carries no such
   field. **Named as the suspect and NOT established: the factor arrays are not on disk, only their
   sha256.**

**DECLARED BEFORE THE NEXT MEASUREMENT, NOT AFTER:** none of this unblocks `OI-126`, which blocks pairing
`C_stat` with P5A. It does not identify *which* factor, does not decide training-versus-extraction, does
not show `C_stat` is wrong — **a per-cell factor common to all 50 members may largely cancel in a
*centred* covariance, which was not computed** — and does not show P5A is right, since a nominal agreeing
with the prior is consistent both with a correct measurement and with an unfolding that barely moved.

**NEXT MEASUREMENT, RUNNABILITY-CHECKED THIS TIME** by listing the keys of both push files rather than
assuming them: bin `w_push` in truth `(pT, p_parallel)` for the nominal and one replica and compare per
`p_parallel` column. It splits training from extraction. Read-only numpy, no driver, no guard, no
TensorFlow; ~1.6 GB resident and a few core-minutes. **It is a different measurement from the one Joseph
approved and needs its own yes — that consent does not travel.**

---

## 2026-08-15 — `OI-126` SPLIT: THE p∥ DEFICIT IS IN THE TRAINING, THE EXTRACTION IS FAITHFUL, AND BOTH SUSPECTS ARE NOW RETIRED

Peer session `B`. Authorized by Joseph under the standing grant for agreed sub-12 h work.
**Predeclared at `449ec52` BEFORE the probe ran**; thresholds fixed there and applied **in code**
(`state/eval-oi126-predeclared-readings-20260815.py`) so the reading could not be chosen afterwards.
`MATCHED: ['TRAINING']` — exactly one of the four predeclared readings.

**The measurement.** `T_a(cell) = Σ w_truth·w_push_a` over all **49,150,928** `pass_truth` rows binned in
truth `(pT, p∥)`, for the P5A nominal `56978466` and `replica_00`; `R_push = T_nom/T_rep` against the
end-to-end `R_xsec`. `mc_indices` asserted identical between arms **and** the identity map; every
`pass_truth` row landed inside the grid (0 outside); all 257 quotable cells usable, 0 dropped. Ran inside
`salloc 57020313` (`-A m3246 -C cpu -q interactive`), 21 s wall, exit 0, empty stderr.

| region | n | median `R_push` | median `R_xsec` | median ratio |
|---|---|---|---|---|
| control, p∥ < 6 GeV | 128 | `1.0114` | `1.0130` | — (`abs(ratio−1)` = **`0.00139`**) |
| band, p∥ 6–20 GeV | 84 | **`5.0467`** | **`5.0365`** | **`1.0000`** |
| p∥ > 20 GeV | 45 | `0.5449` | `0.5394` | `0.9965` |

**Control passed to 0.139%** against a predeclared `≤ 0.10`, so the band readings are usable — the
truth-side binning reproduces what the extraction does. **In the band the push already carries the entire
factor of five.** The `>20 GeV` sign reversal is in the push too. p∥-separability survives in the push
(`R² = 0.839` p∥-only against `0.030` pT-only), which the predeclaration listed as the expected secondary
outcome — **declared and realized, recorded as such rather than written up as a discovery.**

**BOTH MECHANISMS THIS CAMPAIGN NAMED ARE NOW REFUTED BY MEASUREMENT.** The **target** went first (replica
targets are the nominal target × Poisson(1) × one shared constant; refinements agreeing to 0.068%), and now
the **extraction**: `gate5_signal_factor_applied_to_truth_counts` is **exonerated and retired as the
suspect, not merely unconfirmed.**

**WHAT IT MEANS, NARROWLY.** The only input difference between the arms is a Poisson(1) bootstrap on the
measured target. So **the OmniFold fit moves by a factor of ~5 in p∥ 6–20 GeV under Poisson resampling of
the measured leg — in bins MINERvA reports at 1.6% statistical uncertainty** (`PRD 104 (2021) 092007` data
release, all 84 of those bins reported).

**AND WHAT IT DOES NOT DO — all five declared in advance, none weakened after the fact.** It does **not**
clear `OI-126`, which blocks pairing `C_stat` with P5A; does **not** identify the factor's form; does
**not** show whether `C_stat` survives a **centred** reduction (not computed); does **not** show P5A is
right; and one replica is not the family. **Nothing here is "verified"** — the probe is one script by one
lane and its internal asserts are self-checks. `C_stat` itself is **not** independently verified: `VL132`
records **one** builder where `OI-121` authorized two blind ones.

**THE DECISION THIS CREATES, WHICH IS NOT THIS LANE'S.** A bootstrap family whose fits disagree by ~5× in
the best-accepted, second-most-populated region of the grid is either **(a)** correctly reporting that this
estimator is unstable there — in which case `C_stat`'s band entries are honest and the published p∥ 6–20
uncertainties are enormous and must be quoted as such — or **(b)** evidence that a Poisson bootstrap of the
measured leg is not a valid statistical-uncertainty proxy for this estimator, in which case `C_stat` needs
a different construction and `OI-121`/`OI-122` reopen. **These have opposite publication consequences and
the measurement localises without adjudicating between them.**

**Cheapest evidence-based way to decide (a) vs (b), designed and NOT run:** test whether the fit's band
sensitivity tracks **measured-leg** statistics per p∥ column — each replica's measured target has 36.8% of
its rows at zero weight, so thin-data sensitivity would scale with measured rather than truth row count.
**Offered as a design and explicitly not a result.**

**One scope note against a misreading of the numbers:** this probe compares the nominal to `replica_00`
alone, so cells with `R_xsec > 1.5` number **65** here and are **not** the family-mean **63** of `OI-126`.
The band used for the reading is geometric (p∥ columns 10–15, 84 cells), replica-independent, and was fixed
in the predeclaration.
## 2026-08-15 — control plane: three of four `blockers` were false, one vetoed authorized work, and the documented fix for it is a no-op

**No cluster contact of any kind.** No `sbatch`, `scancel`, `scontrol`, `ssh`; `gate6traj-reconcile-56847059`
untouched; no receipt-bound launcher repinned; the cluster science repo was not pulled. Local reads, two
generator runs, and edits.

**AUTHORITY.** Joseph authorized the correction; the mediator relayed it and **the verbatim grant was
committed at `2266840` BEFORE this lane acted on it**, per `BEN-082(v)`. The standing 12-hour clause in that
same message was **not** acted on and is not treated here as a permission expansion.

**WHAT WAS WRONG — five fields, not the three the dispatch named.** `state/live-state.json` renders to
`LIVE-STATE.md`, the file `CLAUDE.md` routes every new session to **first**:

* `blockers[1]` prohibited `C_stat` *"until array 56936015 and validator 56936016 return … 50/50"* — both
  terminal, and `C_stat` is **built** (`VL132`, sha256 `6c3b4e00…`).
* `blockers[2]` paraphrased `do_not_retry_unchanged` as **"no retry"** — dropping the qualifier and so
  **forbidding the CHANGED Gate-6 retry Joseph authorized at `043d572`**. This is the one that cost
  something: a blocker list is read as a veto.
* `blockers[3]` was the Gate-4 estimator-arm sentence, dead since 2026-08-13.
* `state` said tasks 1–49 pending and `C_stat` null. `next_authorized_action` told a session to **wait for
  work that had finished**.

**Found because the file contradicted itself** — `next_authorized_action` states the `unchanged` qualifier
correctly eleven lines below the blocker that drops it. A ledger read cannot detect a row that is
confidently wrong, only one that is internally inconsistent.

**WHAT WAS WRITTEN.** `blockers` now has 4 rows, each carrying a `WITNESS:` naming the artifact that would
falsify it. `blockers[1]` was **NOT deleted** — the constraint *changed rather than lifted*: `C_stat` exists
but was built by **one** builder against a two-blind-builder authorization, its quotable sub-block is **257**
not 262, and `CSTAT-R7` labels it `INSUFFICIENT` at `N=50` with `OI-122`'s supersession unratified. Deleting
it would have converted a real limit into no limit, which is the same failure in the direction that licenses
quoting. `blockers[2]` enumerates the five prohibitions **by key**. `OI-126` was **absent entirely** and is
now row 4. The Gate-4 row is **deleted** and its anti-misread function moved to a new `scope_notes` field.
`state` and `next_authorized_action` rewritten. `LIVE-STATE.md` regenerated: **freshness `FRESH :: Git ==
HEAD`**, 74 lines before and after.

**THE ROOT-CAUSE FIX WAS ATTEMPTED, MEASURED TO BE A NO-OP, AND REVERTED.** `OI-73` prescribes reclassifying
the mislabelled input via `MANIFEST-overrides.tsv`. `generate_manifest.py` applies the override and then
`if is_runs_or_state(rel):` runs **unconditionally afterwards** and resets `event_status = "generated"` — so
the overrides file is **inert for every `state/` and `RUNS` path**. **Worse: the discarded override is still
added to `applied_overrides`, so it counts in `overrides=N` and is excluded from the "unused overrides"
warning — the one diagnostic built to catch a dead override is blind to this case by construction.**
Measured: `overrides=49`, `event_status=generated`, exit 0, row unchanged. The no-op line was **removed**
rather than left, because a dead override that reports as applied is a trap. `immutable` is unreachable for
the same reason (`derive_immutable` returns `yes` for `is_runs_or_state`, and the overrides file has no such
column). **The real fix is a CODE change that reclassifies every `state/` and `RUNS` row; it was NOT made —
not authorized, and it must not ride a documentary commit.** `OI-73`(2) stays OPEN on that. `BEN-321`.

**`OI-70`'s MECHANICAL HALF DISCHARGED, on its rigorous criterion.** `generate_manifest.py` run from the
clean main checkout. Row count `817 → 824`; and because **a rising total cannot prove nothing was dropped**,
the path sets were set-differenced: **0 dropped, 7 added**, all 7 real files committed by other lanes today.
Two lanes previously declined this run for want of that criterion.

**`log_test.txt` — DECIDED DELIBERATELY: left in place, and the hazard raised against it does not apply.**
The concern was that `generate_manifest.py` walks the filesystem and would inventory it. The walk is rooted
at `ORCHESTRATION = REPO/docs/orchestration` (`:24`, `:83`) and **the file is at the repo root**, so it
cannot be reached; confirmed by the set-difference above, in which it does not appear. Not this lane's file,
and not deleted. **`worktree entries: 2` in the committed output is a transient**: the field counts the
*generating* session's own dirty tree, and a session correcting `live-state.json` necessarily has that edit
in flight, so the value can never describe the post-commit tree (`OI-73`).

**NO LEDGER ROW AND NO `*_STATUS.md` LINE, deliberately.** This commit establishes **no new verified number**
— every figure it cites is routed to `VL132`, `OI-126`'s receipt or the Gate-6 receipt — so a
`VALIDATION_LEDGER` row would invent one. And no `*_STATUS.md` owns the control plane: per `CLAUDE.md`'s own
table the canonical home for *"what is happening right now"* **is** `LIVE-STATE.md`, which is what was
corrected. Bolting an orchestration line onto a science status file would write a fact outside its home.

**A `BEN-228` INSTANCE FOUND IN PASSING.** `OI-73` cites the defective row as `MANIFEST.tsv:616`; at `HEAD`
that line is a **different** row, the manifest having grown by 7. The row was located by content
(`awk -F'\t' '$1=="…/live-state.json"'`), not by coordinate.

**NOT ESTABLISHED, and not claimed:** why `C_stat` ended up single-builder (the ledger records the outcome
and the prohibition on claiming independence, not the decision — that is lane B's or the mediator's answer);
none of the physics was reproduced; and `blockers[0]` was checked only to the extent that its validator
receipt exists — **a blocker asserting a negative cannot be discharged by finding its receipt.**

## 2026-08-15 — the hash-binding guard cannot see the Gate-5 implementation pins, and its own accounting has no cell for them

**No cluster contact.** No `sbatch`, `scancel`, `scontrol`, `ssh`; `gate6traj-reconcile-56847059`
untouched; no receipt-bound launcher repinned; the cluster science repo not pulled. Local reads only, plus
`FINDINGS.md` / `OPEN_ITEMS.md` / this log.

**RAISED BY THE MEDIATOR, RE-DERIVED HERE.** The mediator relayed the mechanism plus figures it had partly
verified and partly received from the `OI-124` peer session, and **explicitly said not to inherit its
chain.** Every number below was re-measured in this session with the repo's own `collect()`. They matched,
which is stated because `BEN-300` says to check whether agreeing statements have separate origins — here
they do, and that is what corroboration looks like when it holds.

**THE MECHANISM.** `verify_hash_bindings.py:137-152` harvests a `(path, sha256)` pair only where a
`<base>_sha256` carries a sibling `<base>`/`<base>_path`/`<base>_file`. **There is no `else`.** The Gate-5
receipts store role-keyed hashes with **no path key of any kind**, so they are never harvested.

**MEASURED.** 261 JSONs under `docs/orchestration`, 0 unparseable: **413 pairs**, of which **0** name
`fullevent_fps_dataloader.py`, **0** name `build_fullevent_replica_target.py`, **1** names
`reconcile_gate5_family.py`. Counted from each file's HEAD digest rather than from role names, those files
are pinned by **12 / 4 / 4** receipts, **5 / 1 / 1** of them `-active-`; the dataloader's five include
`gate6-floor-replication-active-56863958`, the Leg F entry in the control plane's live-job list (*a
repo-recorded state — no cluster command was run*). `gate5-target-array-active-56857232`'s
`implementation` block is **6 of 6 invisible**.

**WHY THIS OUTRANKS A COVERAGE GAP.** The tool prints `resolved 180 bindings (600 unresolvable: data
files, off-repo artifacts, binaries)`. `unresolved` at `:234-240` counts **only pairs `collect()` DID
harvest** whose path then failed to localize. **Role-keyed hashes are in neither cell.** So a reader asking
the careful question — *did it account for everything it saw?* — gets a ledger that balances, and **the
residue line makes the gap harder to find rather than easier.** `RECEIPT_BINDING_FLOOR = 140` is met at
`165` over a set that structurally excludes these pins.

**Two details sharper than the totals.** The single visible `reconcile_gate5_family.py` pin is in a
**terminal** preflight receipt while the pin in `gate5-family-validator-active-56933831` is invisible —
**coverage anti-correlated with liveness** for that file. And the 6-of-6 receipt still contributes 2 pairs
for other objects, so it **looks covered** to a spot-check.

**THE SCARY NUMBER IS THE WRONG ONE, SO BOTH ARE RECORDED.** 1181 `*_sha256` keys, 123 paired, **1058
unpaired — but most are content hashes with no file to compare** (`receipt_` 127, `root_` 120, `row_` 108,
`stdout_`, `stderr_`). **The defensible figure is 122 occurrences across 51 receipts whose role name
denotes repo CODE.** Role-name matching is used to BOUND the problem for costing and must not be used to
FIX it — see the rejection below.

**NOT lane A's `OI-64` and not `OI-64(f)`.** A's row is the **wiring** defect and is **RESOLVED** — the
gate runs; `pre-commit: 7 checks passed` on this lane's own commits tonight. `(f)` is **erosion**, coverage
sliding as bindings are legitimately retired. **This is a class never admitted to the accounting at all.**
Filed as **`OI-127`**, a new id rather than an addition to A's row, because attaching a live item to a
resolved row buries it and because A's row is half of an ID collision (`BEN-159`, `BEN-223`). Freeness
derived immediately before taking it and allocated in the same commit as the finding — the `BEN-*` block
discipline applied to a namespace that has none. That exposure is carried, not fixed.

**THE COST ANSWER, which is what the mediator asked for.** **(1) ~15 lines and it is NOT a fix:** count
the unpaired keys in the same walk and print a **third cell** beside `resolved`/`unresolvable`. Changes
nothing about what is verified, so **no past green is reclassified**, and it gives a later widening a
before/after baseline. **(2) New receipts carry a sibling path key** — convention plus a lint scoped to
newly-added receipts. **(3) Retro-fitting the 51 existing receipts is FORBIDDEN, not merely expensive:**
they are immutable records, many terminal, and rewriting one so a guard can see it is the act this repo
refused this morning for the emitted P5A products. **Historical coverage is unrecoverable; the achievable
goal is that the output stop implying it already holds.** **REJECTED: inferring path from role name** — it
would make the guard assert a target the receipt never named, which is `BEN-312` exactly, whose
`recomputed_from` claim was TRUE and rigorously recomputed from the wrong file. **The collector was
deliberately NOT widened**, per the dispatch and on its reasoning: widening changes what every historical
green meant and needs its own change with its own count.

**FOUND IN PASSING, one line to fix: `OI-66` DOES NOT EXIST.** `verify_hash_bindings.py:121` says *"Tracked
as OI-66"* and lane C's `OI-65` cites it, but there is no such row — A's `OI-64` folded `(f)`/`(g)` in as
sub-parts by design and the code comment was never repointed. `BEN-215` class.

**AND MY OWN CELL-COUNT INSTRUMENT WAS THE BROKEN ONE.** A naive `split('|')` reported `OI-127` at 8 cells
against a 7-cell majority; the row was correct and **the counter counts `\|` escapes as separators** —
exactly the defect this log already records against an earlier `awk -F'|'` audit. Re-counted with
`re.split(r'(?<!\\)\|', ...)`: **7 logical cells, matching 85 of 88 rows.** A second instrument reporting a
document defect that is an artifact of the instrument.

**NOT ESTABLISHED, and a reader must not infer it: NO BINDING WAS SHOWN TO BE BROKEN.** This is coverage,
not drift — the invisible pins were **not** compared against their files, and the guard's greens may all be
true of what they checked. Also unexamined: which of the 122 are genuine bindings, and whether
`collect_shell()` / `SHELL_PIN_FLOOR = 15` has the same hole. `BEN-322`, `OI-127`.

## 2026-08-15 — `ACTIVE` was the else-branch: Leg F showed live for 24 h after it finished, and the whole compute table was a non-observation

**Cluster contact: FOUR READ-ONLY `sacct` QUERIES over `ssh`, nothing else.** No `sbatch`, `scancel`,
`scontrol`, no submission, no requeue; `gate6traj-reconcile-56847059` untouched; no receipt-bound launcher
repinned; cluster science repo not pulled. Rendering fix authorized by the mediator.

**THE DEFECT.** `slurm_array_status.build_snapshot` classified `ERROR` / `COMPLETE` / **`else: ACTIVE`**,
and `UNKNOWN` is explicitly excluded from the error branch. So an unobservable task raised no error, was
not complete, and **fell into the same bucket as a task positively observed `RUNNING`.** `ACTIVE` was not
mapped from `UNKNOWN`; it was **what was left over.**

**MEASURED HERE, not relayed.** `sacct -X`: `56863958_[2-5]` all `COMPLETED 0:0`, elapsed ~03:15 each,
ending `2026-08-13T14:08:51` / `14:16:55` / `18:35:57` / **`2026-08-14T09:02:08`**. Leg F was rendered
`ACTIVE` **more than 24 h after it finished.**

**IT IS THE WHOLE TABLE.** `56936015` → **50/50 `COMPLETED 0:0`**; `56936016` → `COMPLETED 0:0`, ended
`2026-08-14T07:31:33`. All three rows read `ACTIVE`. **Zero of the three states in that table were
observations** — a bigger result than the one row that was reported.

**AND THE GENERATOR CANNOT REACH SLURM FROM THIS HOST AT ALL.** `which sacct squeue scontrol sbatch` →
all four not found. So `runner()` raises `OSError`, both texts are empty, every task parses `UNKNOWN`
(`reason: not-visible`), and the else-branch fires. **The compute table has never been evidence when
generated off-cluster and never could have been.** It is not a live view that went stale; it is a
rendering of *no data* that has always read as a state.

**THE EVIDENCE OF NON-OBSERVATION WAS CAPTURED AND THEN DISCARDED.** `build_snapshot` returns
`observer_errors` — here `squeue:[Errno 2] No such file or directory` and the same for `sacct` — and
`unknown_tasks`. **The renderer used neither**, printing `error_tasks` only, which is empty in exactly this
case, so the Errors cell read `none`. **`BEN-322`'s shape one layer up:** there the guard's accounting had
**no cell** for what it could not see; here the cell exists, is populated correctly, and is not rendered.

**The row printed its own refutation:** `| 56863958_[2-5] | **ACTIVE**: UNKNOWN=4 | none | ? CPU, ?, ? |`.
**The bold word is what a scanning reader takes; the qualifier that negates it is unbolded two characters
later**, and `? CPU, ?, ?` renders absence as tabular data.

**WHAT IT COST, AND THIS LANE'S SHARE OF IT.** The `OI-124` peer reported Leg F running while costing a
Gate-5 re-issue; the mediator relayed it; the `Assistant` lane built *"re-issue the dataloader binding
after Leg F terminates"* on it; the mediator carried that to Joseph as a scheduling constraint on a **~39
GPU-h** experiment. **Four parties propagated a fictional constraint.** This lane wrote *"Leg F's liveness
is quoted from the control plane's job list, not measured; no cluster command was run"* — correct
provenance, and **not enough: `ssh sacct` cost one command and this lane flagged the gap instead of
closing it. LABELLING A CLAIM UNVERIFIED IS CHEAPER THAN VERIFYING IT AND DOES NOT SUBSTITUTE FOR IT.**

**FRESH AND WRONG.** At the moment it asserted this, `LIVE-STATE.md` — the file `CLAUDE.md` routes every
session to **first** — reported `FRESH :: Git == HEAD`. Its own header warns that regeneration *"does NOT
revalidate `Declared state`, which is authored prose"*; that warning is **scoped to the hand-authored
part and silent about the compute table**, which a reader trusts precisely *because* it looks
machine-derived. **The most-trusted region of the file was the least-caveated.**

**A TEST ASSERTED THE DEFECT.** `test_missing_is_active_unknown_not_false_terminal` demanded
`overall == "ACTIVE"` for a task nothing could see. **Its intent was right** — an unobserved task must not
be reported terminal, because a false *"done"* licenses reading a result — **and `ACTIVE` was the wrong
safe side**, defending against a false terminal by asserting a false liveness. Rewritten to assert the
intent (`!= COMPLETE`) *and* the defect it permitted (`!= ACTIVE`), with the old assertion preserved in its
docstring. **A test can pin a defect while its name states a correct principle.**

**WHAT WAS CHANGED.** `ACTIVE` now requires **positive evidence** (`any(state in ACTIVE_STATES)`);
unknowns with no positive evidence give a new **`UNOBSERVED`**; `ERROR`/`COMPLETE` keep precedence;
partial visibility (`BEN-229`'s split-array trap) is `UNOBSERVED`, since a task invisible to `sacct` is not
thereby running. The row renders **`STATE UNAVAILABLE — NOT A LIVENESS CLAIM`** with `observer_errors`
verbatim and `declared (not observed):` resources, plus a **table-level warning** whenever any row is
unobserved, because a per-row caveat is read *after* the eye has taken the bolded state. **`UNKNOWN` was
rejected as the token deliberately: it is skimmable, and skimming was the failure.**

**BOTH MACHINE CONSUMERS TRACED, NOT ASSUMED** — `watch_slurm_array_resume.sh:85-95` (`UNOBSERVED` falls
to the `*)` arm and increments `unreliable`, as the `ACTIVE`-with-unknowns path did) and
`wakerctl.py:440-446` (`UNOBSERVED` implies non-empty `unknown_tasks`, so it takes `unreliable_step()` as
before). **Behaviour-identical, and the reason matters more than the result: those consumers already
DISTRUSTED `overall` and gated on `observer_errors`/`unknown_tasks`. Two of three consumers used the
evidence fields; only the human-facing generator trusted the verdict.** So `schema_version` was not
bumped.

**VERIFIED:** 7 tests added plus the rewrite, **18 green** across `test_slurm_array_status` and
`test_generate_live_state`, including a **power test that re-implements the pre-fix classification and
asserts it reproduces `ACTIVE`** — the suite is known able to fail, not assumed to — and a true-positive
test that one observed `RUNNING` task still yields `ACTIVE`, so the fix is not uniformly pessimistic.
**Two failures in `test_watch_slurm_array_resume.py` are NOT from this change**: they preflight a
`/pscratch` path absent on this host, and the same 2 fail at `HEAD` in a clean throwaway `git worktree`.

**AND A CORRECTION TO THIS LANE'S OWN METHOD, third instrument to misreport today.** The finding first
claimed *"no consumer branches on `overall`"* — from a `grep` piped through `head -15`, which **truncated
away both real consumers** while showing 15 unrelated `overall_ratio`/`overall scale` hits. That is
`BEN-026` applied to my own search, and it would have put a false claim into a finding about tools
asserting states they do not have. Caught by grepping the two known consumers **by name**. After the
`| tail` exit code and the `split('|')` cell counter, this is the third.

**NOT DONE:** the wake/waker and usage-gate rows were not audited for the same pattern; only the compute
table was examined. **And this does not make the table evidence** — on a host without Slurm it now says so
loudly, and making it a live view requires regenerating from a host that can reach Slurm. `BEN-323`.

## 2026-08-15 — `OI-81` is NOT drift; `OI-58`'s fix is available on the unpinned side; and two critical-path items have unreachable owners

**No cluster contact.** No `sbatch`, `scancel`, `scontrol`, `ssh`; `gate6traj-reconcile-56847059` untouched;
no receipt-bound launcher repinned; cluster science repo not pulled. **Lane C's script was RUN and READ,
never edited.** Nothing entered `docs/analysis-note/`.

**`OI-81` — ANSWERED: NOT REAL DRIFT (`BEN-325`).** `check_canonical_designation.py` → exit 1,
`74 files, 216 namespace occurrences, 54 inventory entries`, **20 UNACCOUNTED + 1 COUNT DRIFT, and nothing
in it indicates the protected artifact changed.** Classified as the guard does not: **13 prose mentions, 7
code consumers that open the path** — failed RED identically, so RED means *"a document was written"* and
*"a new consumer appeared"* indistinguishably. **Its one enforced signal fires on PROSE:** the `RECORD-FROZEN`
count drift on `annealed-nominal-complete-56563761.json` is line `245`, reading *"fullevent_nominal/ IS NOT
TOUCHED …"* — **a sentence reassuring that the protected thing is untouched is what makes the guard say
something changed.** **Credit where due: `:28-32` anticipates `BEN-311`'s sibling trap and matches by PATH
SEGMENT**, closing by design the trap that later bit two other lanes. **The flaw is one thing:
`RECORD-APPEND` waives the COUNT for files it itself defines as designed to ACCRUE and STILL ENFORCES
PRESENCE**, so each new finding needs hand-adding to a dict inside the script — and **4 of the 20 are
today's findings about this very namespace, so investigating the artifact turns its own safety guard RED.**
One unaccounted file is `sbatch_p5a_fullevent_nominal_extract.sh`, which **this lane edited this morning**.
**The remaining substance is real and is NOT closed: 7 consumers lack dispositions**, one being
`probe-vl100-foldforward-shape-20260814.py:46` — the exact line `BEN-311`/`BEN-312` are about, opening the
**pre-anneal** sibling deliberately. **Fix is C's and needs no GPU; do NOT close by adding 20 dict entries.**

**`OI-58` — THE STAMPING DEFECT IS TWO SITES, ONE CHAIN, AND THE FIX IS AVAILABLE.** Hop 1,
`train_fullevent_replica.py:~105-112`: source leg checks **path and size only**, then copies
`source["sha256"]` into `_verified_input_sha256`, eleven lines below `:99`'s genuine `sha256_file(target_npy)`.
Hop 2, `train_fullevent_nominal.py:642`: stamps that value into the artifact under a comment claiming *"the
digest that was actually verified"* — **verified at the source: true on the nominal path, false on the
replica path.** **PIN STATUS MEASURED BOTH WAYS, because `BEN-322` established role-keyed pins are invisible
to `verify_hash_bindings`: `train_fullevent_nominal.py` is in FOUR pin lists including the live
`gate6-leg0-tier-calibration-prepared-20260814.json` `pinned_paths[8]` — DO NOT TOUCH, `OI-123` class.
`train_fullevent_replica.py` is in NO pin list**, and `submit_gate5_replica_n50.sh:50` recomputes its digest
at submit, so it floats by design. **So fixing hop 1 makes hop 2's stamp AND its comment true without
editing the pinned file — no re-issue, no repin.** **And a cheaper, stronger fix than the prescribed "mirror
`:99-101`" exists: `submit:25` ALREADY hashes the 9.22 GiB input against a hardcoded `EXPECTED_INPUT_SHA`
before any job starts and `:48` exports it — and NO Python reads it.** Binding to that frozen constant costs
zero I/O and is strictly stronger than comparing against the receipt's copy. **Not made: report only, per
the dispatch.** `OI-57`'s cell asserts *"a tree-wide grep finds no stored driver digest"* — **literally false,
three receipts store it**; the substance (no *enforced* pin) survives and the phrasing would stall a lane.

**AND THE ROW-SHAPE POINT THE MEDIATOR ASKED FOR:** `OI-58`'s next-action column carried **only** the
citation fix, discharged at `c7eb704`. **The stamping defect lived in the blocker column with no remedy ever
specified — so it could be neither closed nor scheduled.** A defect described in an evidence field with no
action is invisible to any process that works from next-actions. The remedy is now written into that column.

**`BEN-324` — AN OWNER RECORDED IN AN ARTIFACT IS NOT AN OWNER WHO CAN BE ASKED.** `gate5_cstat_contract.json`
names its lane in its own `lane` field and that name had no addressee; `minerva-omnifold-f7` was asked twice
and did not answer. **`lane` is provenance, not a routing table** — `ListAgents` reports liveness, never
ownership; sessions are renamed and respawned keeping their names; and a lane label is not an address, which
is why naming a different peer `C` as the spec owner produced a correct refusal. **`BEN-300` one level out
and worse: a task re-dispatches by availability, a SPEC RULING DOES NOT.** **Two critical-path items are
blocked on unreachable owners at once** — `OI-81` (C's script) and `OI-58`/`OI-57` (owner never identified) —
which is what makes it structural rather than an anomaly. **No mechanism proposed, deliberately:** an
`OWNERS.tsv` is the hand-maintained index of a source-less fact `BEN-228`/`BEN-300` warn about, and
`ROW-OWNERS.tsv` already has all 12 `CLM-*` rows UNASSIGNED (`OI-53`). **Enforcement is attention.**

**NOT ESTABLISHED:** that the canonical designation is **safe** — `BEN-325` says the RED is not evidence of
drift, it does **not** audit the artifact, and a byte change in the annealed weights would not appear in that
guard at all. Why `minerva-omnifold-f7` did not answer was not diagnosed. And the `OI-58` fix was **not
written or tested** — only located and costed.

## 2026-08-15 — OI-58 hop 1 FIXED on the unpinned side: the replica source digest is now measured, and bound to a frozen constant nothing was reading

**No cluster contact.** No `sbatch`, `scancel`, `scontrol`, `ssh`; `gate6traj-reconcile-56847059` untouched;
**no receipt-bound launcher repinned**; cluster science repo not pulled. Fix authorized by the mediator on
Joseph's standing grant, in the stronger form this lane recommended rather than the prescribed mirror.

**WHAT WAS WRONG.** `train_fullevent_replica.py` hashed the target at `:99` and, **eleven lines later**,
verified the 9.22 GiB source by **path, size, and the mere presence of a digest in the receipt** — then
copied that digest into `_verified_input_sha256`. `train_fullevent_nominal.py:642` stamps it into every
replica artifact under a comment reading *"the digest that was actually verified"*, **true on the nominal
path and false on the replica path.** A same-path, same-size content change was invisible.

**THE PART THAT GENERALISES, and it is why this is `BEN-326` rather than a chore: THE STRONGER ANCHOR WAS
ALREADY COMPUTED, ALREADY EXPORTED, AND READ BY NOBODY.** `submit_gate5_replica_n50.sh:25` hashes the input
against a **hardcoded** `:14` digest and `die`s before either array is submitted; `:48` exports it as
`GATE5_EXPECTED_INPUT_SHA`; `:54`/`:57` pass it via `sbatch --export`. **`grep` over every `.py` returns zero
readers**, while `sbatch_gate5_replica_train_array.sh:17-22` consumes **four** sibling `GATE5_EXPECTED_*`
pins fail-closed and skips this one. **Fourth instance today of a qualifying fact computed then discarded
before the consumer — and the FIRST where the discarded fact was STRONGER than the one used.**

**WHAT THE GUARD NOW PROVES THAT IT DID NOT BEFORE.** Before: the file is at the expected path, has the
expected size, and the receipt contains some 64-character string — reported as verified. After: the file's
**measured** digest equals **both** the receipt's claim **and** the constant the submit controller checked
against a hardcoded literal. So the stamped field is a **measurement**, anchored to the **frozen source**
rather than to the document quoting it. Fail-closed three ways: missing export aborts (never a silent skip),
receipt disagreement aborts, frozen-constant disagreement aborts.

**WHY IT NEEDED NO RE-ISSUE AND NO REPIN.** Measured both ways, since `BEN-322` established role-keyed pins
are invisible to `verify_hash_bindings.py`: `train_fullevent_nominal.py` is in **four** pin lists including
the live `gate6-leg0-tier-calibration-prepared-20260814.json` `pinned_paths[8]` — **not touched**, an
`OI-123` `die … 3`; `train_fullevent_replica.py` is in **no** pin list and `submit:50` recomputes its digest
at submit. **Hop 2's stamp and its false comment become true because hop 1 now verifies.**

**VERIFIED, both directions, 5 green** (`tests/test_gate5_replica_driver.py`): absent env aborts; a source
agreeing with the receipt but **not** the frozen constant is refused — **the case an `OI-57`-only fix would
have admitted**; **same path, same size, one byte flipped is caught**, with size-preservation and the
receipt's now-stale claim asserted inside the test so it cannot quietly stop testing that; and a mutant
asserts the pre-fix copy would have stamped a digest the file no longer has. `git status` after: only the
two intended files plus the pre-existing untracked `log_test.txt`.

**`OI-57`'s FALSE CELL CORRECTED.** *"A tree-wide grep finds no stored driver digest"* is literally false —
**three receipts carry it**, two of them `-active-`. The substance it defended survives and is now stated
properly: **none of them is an ENFORCED pin** (role-keyed, so invisible per `BEN-322`; launcher constant
floats). **Stored-but-unenforced, not absent** — the old phrasing would make a lane find three hits and
stall, which is what that cell existed to prevent.

**NOT FIXED, and none of it is claimed:** the existing 50 artifacts still carry the copied field (hence the
citation discharge at `c7eb704`); the repair reaches production only when `CODE_ROOT` syncs, which `OI-74`
blocks; and **this must not motivate a Gate-5 re-issue** — it rides one.

**AND A METHOD ERROR OF MINE, fourth instrument today.** Checking whether I had broken an unrelated test, I
ran it **alone** at `HEAD` (passed) and **inside a `-k` subset** in my tree (failed), and briefly concluded I
had broken it. **Two different conditions; the comparison was invalid.** The same subset at `HEAD` reproduces
the identical failure — pre-existing order pollution in `test_pet_fullevent_nominal_launcher.py`, unrelated.
**Comparing a test's status across two trees requires the same selection in both.**

## 2026-08-15 — the Leg 0 "5.2% non-determinism" is a checkpoint-tier gap, and the run said so before three documents read it otherwise

**NO COMPUTE SPENT AND NONE PROPOSED.** Four read-only `sacct`/`squeue` queries and file reads on
`/pscratch`; no `sbatch`, `scancel`, `scontrol`; `gate6traj-reconcile-56847059` untouched; nothing
repinned; the five Gate-6 prohibitions at `19585b7` stay live; nothing promoted; nothing into
`docs/analysis-note/`. Correction authorized by the mediator and landed **beside** `674df29`, not over it.

**WHAT WAS WRONG.** `674df29`'s body and the handoff read *"it is a real non-determinism localised to the
step that produces `push_final`"* and *"the same computation, on the same committed checkpoints … several
times `BEN-043`'s ~1.3% checkpoint-tier gap"*, and called the tier comparison *"the obvious next
measurement."* **All three are wrong, and `member_1`'s own trajectory receipt recorded why before any of
them were written:** `"gate_is_cross_tier": true`, `"checkpoint_tier_requested": "best-epoch"`, and all
three checkpoints at `"provenance_tier": "best-epoch"`. The gate compared a **forced best-epoch**
reconstruction against a receipt produced at a **different tier**.

**THE TWO BIT-EXACT REPRODUCERS ARE THE MECHANISM, and the original reading had them backwards.**
`increment1` and `push_prev` reproduce at `rel_dev` **exactly `0.0`** across separate processes — **a run
with process non-determinism does not reproduce two of three quantities bit-exactly** — while the only
quantity that moves is the one depending on the **final-iteration** checkpoint, exactly where the tiers
diverge. A clean one-checkpoint substitution, not noise. **So the 5.2% IS a checkpoint-tier gap and cannot
be "several times" one: it is a measurement OF that gap, comparing a thing to itself.** The Gate-6 floor
question is untouched by this run.

**THE EXIT-CODE PREDICTION IS FALSIFIED 2-OF-3.** *"Expect them to exit `1:0` as well"* — measured:
`_1`/`_2`/`_5` `FAILED 1:0`, **`_3` and `_4` `COMPLETED 0:0`** (`00:13:52` / `00:13:43`). **3 of 5 failed
the cross-tier gate, 2 passed**, consistent with a tier shift landing under `REPRO_RTOL = 0.02` on some
members. Elapsed times corroborate: failures `~10:15`-`10:23`, passes `~13:43`-`13:52`, the difference being
the trajectory the passes emit — `m1`'s is a **1,703-byte refusal stub**, `m3`'s is **7,495 bytes**. Leaving
`_3`-`_5` to run was still right, and their receipts are why this was settleable read-only.

**`BEN-229` CLOSES CONFIRMED, and recorded on its own row rather than only here** (the handoff asked for the
count either way, and a prediction whose resolution lives elsewhere is one nobody closes):
`sacct -X -j 56993778 | wc -l` → **5** at terminal, every task owning a row. Its scope — that `sacct`
under-reports only between *split* and *start* — is confirmed rather than merely unfalsified.

**WHY IT TOOK A DAY, which is the transferable half.** `gate_is_cross_tier` is a **top-level key in a 1.7 KB
file, beside the very numbers three documents quoted**, and the `REPRO_RTOL` mismatch was read off
**stdout**, which does not carry it. **A gate whose comparison is known at run time to be invalid as a
determinism test must say so in the FAILURE MESSAGE** — `[traj] reproduction gate FAILED (CROSS-TIER: not a
determinism test)` cost nothing. **Fifth instance in two days of a qualifying fact computed, persisted, and
not put where the reader was looking** (`BEN-321`, `BEN-322`, `BEN-323`, `BEN-326`).

**THE `final`-TIER ARM WAS NOT RUN, and that is the mediator's decision on this lane's recommendation.**
Costed from this array's own `sacct` elapsed at **0.9744 GPU-h** (`615+623+832+823+615 s`, one A100 per
task); the launcher `sbatch_gate6_leg0_tier_calibration_array.sh` is in **no pin list** and its digest is in
zero receipts, so it needs no repin, and `train_fullevent_nominal.py` (`pinned_paths[8]`) is not involved —
the driver is `step1_increment_trajectory.py`. **`TRAJ_TIER` is hardcoded at `:61` and not env-overridable**,
so the arm needs a launcher edit that is nonetheless free of pins. **If it is ever run, its predeclared
expectation must be BIT-EXACT REPRODUCTION so it can fail loudly**; running it under the retracted framing
would have let its result be read against a hypothesis now known to be wrong.

**DELIBERATELY NOT TOUCHED: `4421013`'s conclusion that member 3's Gate-6 FAIL is a measurement artifact.**
`m3` is one of the two that COMPLETED, which is worth re-reading against it — **recorded by the mediator as
an open Gate-6 question needing its owner and a predeclaration, not a quick check by a documentary lane.**

**AND A NEAR-MISS OF MINE.** I first read `checkpoint_tier_requested` from the **decomposition** receipt, got
`None` from `dict.get`, and was one step from filing *"the tier is not recorded in the artifact whose purpose
was tier calibration"*. **The key lives in the trajectory receipt and reads `"best-epoch"` correctly.** A
`.get()` returning `None` for a key that was never in the file you opened is not a missing field. Caught by
dumping the key set; it never reached a claim.

## 2026-08-15 — standard-P4 stage 3 RAN on 2026-08-08 and this log said it did not (`BEN-352`)

**Appended, not rewritten.** This log is append-only, so the two entries this corrects are left standing
where they are: **`:3614`** (*"Stage 3 was deliberately NOT run"*) and **`:5705-5706`** (the two
preconditions carried forward). Read them with this entry. **Both were accurate as chronology — they
record what the lane believed and decided on those dates — and both are false as present-tense fact.**

**MEASURED THIS SESSION, READ-ONLY, on `saul.nersc.gov`** in
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/unfolds/`: **ten
endpoint ROOTs and ten `.done` receipts, all dated 2026-08-08**, each

```
mode      = produced
bkg_mode  = purity
code_rev  = 42268b6dfa2e60a0e4bd491b11ad9b11d0228273
```

Receipt `t` stamps span `2026-08-08T13:41:45Z` → `14:59:03Z`; ROOT mtimes `06:40`–`07:59` local. `42268b6`
**contains** `5a4009f` (G-1), `febb9a1` (the resume-gate repair) and `2654731` (the legacy-attest
deletion), each verified by `git merge-base --is-ancestor`. The run is holder allocation **`56495756`**
(`gbdt-hold`, `WorkDir` `/pscratch/sd/j/josephrb/MINERvA-OmniFold`), step **`56495756.0`** (`bash`,
`COMPLETED`, `05:21:46`→`07:59:04`, elapsed `02:37:18`); the allocation itself shows `TIMEOUT` at
`08:21:46`, which is the **holder** expiring after the work finished, not a failed unfold.

**AND G-1 IS ON THE CLUSTER CHECKOUT.** Cluster `HEAD` = `683bdcc`;
`git merge-base --is-ancestor 5a4009f HEAD` in that tree → **true**; the wiring is live in the working
tree (`run_p4_unfold_std.sh:37` reads `bkg_mode` from `P4Config`, `:90` passes `--bkg-mode`).

**THE IRREVERSIBILITY CLAIM AT `:3614` IS REFUTED IN CODE, AND IT WAS TRUE WHEN WRITTEN.** `:3614` says
the launcher *"skips any endpoint that already has a receipt"*, so pre-G-1 receipts *"would then be
skipped forever"*. That described the **pre-repair-4** gate — `[[ -s ROOT && -s RECEIPT ]]` plus a
ROOT-key check, the form `p4_lib.py:784-787` documents and disowns — and it was **fixed by `febb9a1` on
2026-08-07, the same day the entry was written.** The gate today (`run_p4_unfold_std.sh:77-84`) skips
**only when `p4_check_receipt.py` PASSES**; on failure it prints `STALE ... -> re-running`, `rm -f`s the
receipt and re-runs transactionally. `bkg_mode` is a REQUIRED key (`p4_lib.py:796-797`, enforced
`:949-950`) and is **COMPARED** (`:961-962`). **A pre-G-1 receipt therefore FAILS the gate and is
re-run: the gate cast as the trap is the repair mechanism.** Cost of a pre-G-1 stage 3 is compute, not
irreversibility, and the deletion freeze never applied — the `rm -f` is the launcher's own, on scratch.

**WHAT THIS DOES NOT SETTLE — two items escalated to Joseph, deliberately not adjudicated here (`OI-75`).**

1. **The run is unreconciled with the standing hold.** `P4_STANDARD_STATUS.md:4` records Joseph's hold —
   *"no cluster P4 run"* — and **there is no record of the 2026-08-08 run anywhere in this repo**: not in
   this log, not in a ledger, not in a products summary. This entry is the first. **Whether the run was
   authorized is Joseph's question, already put to him and unanswered.** Recorded plainly, not excused:
   **well-formed artifacts attest to provenance, never to permission**, and this entry must not be read
   as retroactive authorization.
2. **The ten products are untracked and exist only on purgeable scratch.** `git ls-files` over that
   directory → **0** on both checkouts; `git status --ignored` marks every ROOT `!!`. Per this repo's own
   rule a result does not exist until its commit lands — **which is precisely why five documents say
   stage 3 never ran.** Products total **4.8 MB** (ten ROOTs at ~480 KB); the 53.8 GB × 10 in
   `p4_lib.py:790` is the **merged inputs**, not these outputs. **Nothing was copied into the repo** —
   whether these land is a provenance and authorization call blocked on item 1, not a storage call.

**NOTHING RUN, NOTHING PROMOTED, NOTHING REPINNED.** Read-only cluster access throughout. The
`standard-p4-verifier` `BLOCK` and the "NOT BUILT" status of the standard 5D lateral are **unaffected**:
this corrects what is true about G-1 and stage 3, and clears no gate.

---

## 2026-08-15 — `standard-p4-verifier` **repair-8**: the live verdict was measurably stale, and this is the first pass in the chain with usable test evidence

**Verdict: `BLOCK`. `defects_outstanding: 10`. `authorizes_covariance_stages_4_6: false`.**
Receipt: `docs/orchestration/runs/standard-p4-verifier/20260815T232546Z-repair8-verdict.json`,
`code_rev 7d884da`. Supersedes `20260810T012645Z-repair7-verdict.json`.

**WHY REPAIR-7 HAD TO BE RE-RUN, measured not assumed.**
`p4_lib.paths_unchanged_between('5c25333', HEAD, review_scope)` → `False`, **25 of its 43 scope files
changed**, so `p4_check_verifier_token.py:126-132` would refuse that verdict today **for staleness
alone, independently of its BLOCK**. Five of its fourteen defects are closed in tree, two of them
(`c308a9c` 19:37, `ea89701` 01:09 next day) landing **after** the verdict was written. A repair plan
built on the repair-7 list would have redone finished work.

**THE PRECONDITION IS DISCHARGED, and it is the most useful thing in this entry.** Repair-7's
`next_action` required *"an environment where the complete suite is executable"*; its `tests.result`
recorded **120 failed, 57 errors** from a read-only tmpdir and said outright that this *"prevent[ed]
verification of the claimed seven PET failures."* With `TMPDIR=/Users/josephbailey/local-research/.p4verifier-tmp-20260815`
— verified writable by **actually writing**, and confirmed through the suite's own guard
(`conftest.TMPDIR_WRITABLE = True`) — the same suite returns **3 failed, 1383 passed, 1 skipped** in
71.66 s, reproduced at 70.66 s. **117 of repair-7's failures and all 57 of its errors were
environmental artifacts.** No defect in the new verdict rests on them.

The three real failures, each triaged in isolation rather than as a block:
`test_gate2_target_runtime` fails alone too (hard `/pscratch` path, off-cluster, PET lane);
`test_pet_fullevent_nominal_launcher::test_config_gate_only_cli_no_train` **passes alone** — test-order
pollution, another test leaves `tensorflow` in `sys.modules`; and
`test_p4_sweep_snapshots::test_pipeline_sweep_matches_its_snapshot` fails alone (`368 != 354`), which is
**real and in scope** and is this round's one new defect.

**CLOSED (5), each re-verified in code at HEAD, never inherited.** #1 evidence publication ordering
(`c308a9c`, `p4_evidence.py:437-471`; crosscheck `need()` at :466-469 now precedes the publish at :471,
and the last `blockers.append` in the file is :401) · #2 resume provenance (`32489a6`+`f67352f`,
`p4_lib.py:493-506,575+`, producer `run_p4_unfold_std.sh:55,119`, consumer `p4_check_receipt.py:37,117`)
· non-adoptable-marker bypass (`a1c9d10`, `p4_adopt_standard.py:32-46`) · stage-6 reachable 4D support
(`a1c9d10`, `p4_project_4d.py:130-137,193-194`) · projection marker propagation (`ea89701`,
`p4_project_4d.py:94-115,182,195-198`).

**STILL OPEN (8).** #5 and #4 are **critical and live**, because they are in the gate that authorizes
stages 4–6 (`run_p4_standard.sh:88-95` shells out to it) and `p4_check_verifier_token.py` is
**byte-identical to the reviewed revision**. Measured this session: `code_rev_in_history('HEAD')`,
`('main')`, `('HEAD~0')` all return `True`, and with `code_rev = "HEAD"` the staleness check
`paths_unchanged_between('HEAD', HEAD, surface)` returns **ok=True, 0 differing** — *the gate's own
anti-staleness rule is vacuous against a symbolic revision*. #4: a declared `review_scope` is trusted
verbatim with no union against the execution surface, and the 18-module fallback omits
`p3s_manifest_summary.py` (measured). Also open: #7 (mutation harness, **self-declared debt in
`c308a9c`**), #8 (`tools_p4_sweep_recorded_fields.py:16-19` still omits `p4_check_verifier_token.py`),
#9 (`P4_STANDARD_STATUS.md:56` still says *"NO covariance candidate exists"* — false; and `git ls-files`
finds **no** tracked path containing `56495756`), plus the two byte-identical `p4_lib.py` functions
(`check_projection_validity`'s non-independent second leg; `crosscheck_marginal_vs_independent` emitting
NaN summaries beside **zero** threshold counts, demonstrated on a NaN input) and `conftest.py`'s
`TmpdirGuardItself`, which is carried **structurally** — it could not be exercised, because this round
deliberately created the writable tmpdir that makes it inert.

**#6 IS REPAIRED AND IS *NOT* CERTIFIED HERE, and that is deliberate.** `0055826` implements both
halves against the support family (`p4_lib.py:373-431`, wired at `p4_validate_active_lateral.py:233-235`,
eleven blind adversarial fixtures all called correctly). **Its author declined to certify it**, verbatim:
*"NOT claiming #6 closed — that is Joseph's call on the packet, not mine to assume and not the
oversight's to grant."* This verifier does not grant what the author declined to assume. It is counted
in `defects_outstanding` and needs **no lane work** — only Joseph's packet decision.

**NOTHING RUN ON THE CLUSTER, NOTHING PROMOTED, NOTHING ADOPTED, NOTHING REPINNED.** No `sbatch`,
`scancel` or `scontrol`; PET array `57038937` untouched; `gate6traj-reconcile-56847059` untouched; no
`p4_*` source edited — reviewing, not repairing. The sweep snapshot was **not** `--update`d. The five
Gate-6 prohibitions at `19585b7` are untouched and nothing entered `docs/analysis-note/`.

**ADDENDUM, same session, measured after the commit landed — `HEAD` moved under this review and the
receipt is deliberately NOT being edited.** The repair-8 verdict declares `code_rev 7d884da`, which is
the tree it actually read. Its commit's parent is **`4a10adf`**, not `7d884da`: a peer lane pushed
*"The OI-8 precondition is REFUTED IN CODE…"* mid-review. **Measured, not assumed:**
`paths_unchanged_between('7d884da', HEAD, review_scope)` → **1 of 19 files differ**, and that one file
is `P4_STANDARD_STATUS.md`. **No code file in scope changed**, so every closure and every
still-open code defect in the verdict stands exactly as written.

`4a10adf` rewrote 79 lines of that status file (`BEN-352`: G-1 is on the cluster checkout and stage 3
already ran post-G-1). **Defect #9 was therefore re-verified against `HEAD` after the drift, not left
on the pre-drift reading** — and it holds: the headline still reads *"REPAIR round 3 complete; NO
covariance candidate exists"* (now line 71, was 56), which remains false at `HEAD`, and
`git ls-files | grep 56495756` still returns **0** tracked paths. The peer's edit concerned stage 3 and
G-1, not the candidate-exists claim, so the two findings do not collide.

**The receipt is left byte-identical on purpose.** A verdict records what was found at a moment; editing
a committed one to absorb later events is how a receipt stops being evidence. The drift belongs in the
append-only chronology, which is here. **And it is a live instance of the very defect the verdict
carries as #5:** the reviewed revision stopped being `HEAD` while the review was still running, and
nothing in the gate would have noticed — a verdict citing a symbolic `code_rev` would have papered over
exactly this and reported zero differing files.

## 2026-08-15 — fold-forward instrumented closure READ; both arms recorded; OI-125 narrowed, not closed

Arm 1 was resubmitted as `57038937_{3,4,5}` under `AUTHORIZATION-20260815-arm1-resubmit.md` and
completed `0:0` at ~1:57 each; arm 0 is `57012031_{0,1,2}`, complete since the morning. **Nobody had
recorded either result.** This session read all six receipts, re-derived both results from the
artifacts, and landed them. **No GPU, no `sbatch`, no `scancel`, no `scontrol` — two read-only ssh
reads and one login-node python over `/pscratch`.**

**Arm 1's provenance is intact and the copy-order condition held.** `logs/ff_57038937_{3,4,5}.out`
line 1 prints the **four**-pin G0 line and lines 2-5 print the four digests, including the wrapper at
`ee269b09…` — so those tasks ran the fixed wrapper under the hardened launcher, which is the only
clean path the authorization allowed. Arm 0's logs print the **three**-pin line: it predates the
wrapper pin, which is expected and does not compromise it — `4e85f0e`'s entire diff is inside the
`if correct:` branch, so arm 0's code path is behaviourally identical across the two wrapper
versions. That is read off the diff, not assumed.

**The first result is a quantity no receipt contains.** The recorder hooks `RunStep1`, so it records
the push entering iterations 0/1/2 and never the push `RunStep2(2)` leaves — while
`train_fullevent_nominal.py:576-577` computes the *nominal's* fold-forward from `push` **after**
`Unfold()`. So the closure's like-for-like number is the end-of-run one, and it is recorded nowhere.
Reading the last recorded row in its place manufactures a `−1.9%`-vs-`+1.1%`, ~105-sd, sign-flipped
"disagreement" with the predeclaration. Recovered properly the answer **AGREES** with §2. Numbers,
controls and ingredients: `VALIDATION_LEDGER.md` (`FF1`-`FF7`) and
`docs/orchestration/state/RECEIPT-foldforward-instrumented-closure-20260815.json`. Filed as
`BEN-360`; `OI-125` is **narrowed and stays OPEN**, and closing it by citing this reconstruction
would make the remaining hole invisible exactly as that row warns.

**The second result is informative against its own prediction.** §6 declared in advance that a ~1%
rescale would likely move recovery by less than the draw spread and that the honest report would then
be a BOUND. It is not: the effect is `16.2×` the pooled within-arm sd with disjoint arm ranges and
9/9 realized pairwise exceedance, **negative**. The reason is measured rather than guessed — §6 sized
the perturbation off the end-of-run ratio while the correction is applied to the consumed one, so the
realized rescale was `4.6%` at iteration 1, not `1%`. **The same conflation that made §2 look refuted
made §6 look conservative; it is one error, not two** (`BEN-361`). All three §7 outcomes are excluded
and §1's gate passes.

**Two writer fixes landed with it, both for FUTURE receipts only — the six are the record and were
not rewritten.** Non-quotability now rides as a field (`label`, the key
`pet_diagnostic_quarantine.require_quotable` already refuses on) instead of only in the filename and
`artifact.path`; and the retired-`0.80`-bar self-report is renamed away from `recovery_criteria_met`,
mirroring `closure_powered_annealed_lr.py`. G0's **wrapper** pin moved `ee269b09` → `b24cfefe` in the
same commit, which is the maintenance action that launcher's own header prescribes — the driver
(`a45fae7c`), annealed wrapper (`ce9f11f4`) and engine (`3a2022b0`) pins are byte-identical and
untouched, so no receipt-bound pin moved and this is not `OI-123`/`BEN-270` territory.

Suite `1409 passed, 4 failed, 1 skipped`; the same 4 failures reproduce at `HEAD` in a throwaway
worktree (`1382 passed`) and none touch these files. The `+27` is 7 new tests here plus 20 from
`test_p4_token_gate_scope_and_rev.py`, which a peer lane landed at `5fc06b6` **while this session was
running** — `HEAD` moved `b5e067d` → `5fc06b6` mid-read. Measured, not assumed: none of the six files
in that drift is in this lane's scope, and this lane's own baseline digest `ee269b09` was re-read off
`HEAD` after the drift.

**Nothing promoted, nothing designated quotable, the central not moved. The five Gate-6 prohibitions
at `19585b7` are untouched, `gate6traj-reconcile-56847059` was not touched, and nothing entered
`docs/analysis-note/`.**

## 2026-08-16 — the OI-6 note text was already written before it was dispatched; verified independently, nothing rewritten

**NOTHING WAS WRITTEN INTO `docs/analysis-note/`.** No compute; no cluster contact; nothing repinned;
nothing promoted; the five Gate-6 prohibitions at `19585b7` stay live. **The one file changed by this
entry's commit is `FINDINGS.md`** (a `BEN-300` annotation) plus this log.

**THE TASK WAS ALREADY COMPLETE WHEN IT REACHED THIS LANE.** Joseph's `OI-6` ruling landed `361d83e`
`16:51 -0400`; the note text landed `e61624b` `18:52` (*"Place the standard-5D purity footing and its limit
in the analysis note: app_negweight.tex B.6, note build only, all three builds pass"*) and was refined
`7d884da` `19:01` (*"B.6's footing evidence was one epoch out of date: G-1 pins and stamps the mode the note
said was inferred from a default"*). The dispatch arrived after `c179a35`, i.e. **at least two hours after
completion.** Found by reading the target file before writing. **Had this lane started from the brief it
would have written a second copy of an existing subsection into a file whose gate Joseph had opened for
exactly one passage.** Recorded as a second instance on `BEN-300`, with the addition that matters: this
row's thesis is that a task's HOLDER has no machine-derivable source, which is right — but **whether the
work is already done usually does**, and one `git log -S` over the target artifact answers it before
dispatch. Duplicate *dispatch* has a cheap check that duplicate *assignment* does not.

**INDEPENDENT VERIFICATION OF THE EXISTING TEXT — `app_negweight.tex` §B.6
(`\label{sec:negweight-footing}`), against Joseph's ordered boundary rather than against the relay.**

Every SAY item is present: purity-footed (and *positively* identified — pinned in code via
`STANDARD_BKG_MODE`, passed explicitly by the canonical launcher, stamped into every endpoint receipt,
rather than inferred from a default); **a recorded choice, not a silent default**, with both dates and both
grounds, and with *"it is that consequence, not the cost, that decided it"* preserved for the J28
invalidation; the ~1–2% measured size; and the published pair as *measurement plus matched control at
different footings*, naming `fps_provenance.PUBLICATION_BKG_MODE`.

**Numbers RE-DERIVED from `RUNBOOK-20260807-gbdt-closeout.md` §2.1, not taken from the relay**, and the
note ships its operands so a reader can re-derive them (`BEN-077`): `2.9828e-39 / 3.0242e-39 = 0.98631`
against macro `\nwSystRatio = 0.986`; `1.7260e-40 / 1.7576e-40 = 0.98202` against `\nwStatRatio = 0.982`;
`\nwPctTot = -0.13`, `\nwMedianBin = 1.000`, `\nwRmsBin = 1.4`. All five macros exist in `values.tex` and
all five match the runbook.

**The structural argument is there and is stronger than the brief asked:** the $\rho_1 = D-B$ identity makes
the two constructions the same estimand, the residual displaces every universe by ~0.1%, and a systematic
covariance is the spread *across* universes — so the ratio lands at `0.986` **rather than near the ~3% size
of the purity correction itself**, which is the comparison that makes it structural rather than lucky.

**THE PROHIBITED CLAIM IS ABSENT AND IS ACTIVELY DEFENDED.** The text states in bold that there is **no**
full 5D 187-universe both-footing comparison at the publication configuration (5 iterations, `lgbm`),
enumerates what the 5D evidence actually is (two-universe spot check at 1 iteration on the `hist` backend,
with its numbers, plus the displacement argument, plus the 2D full-statistics result), says it is *not*
ample for the stronger statement, and adds **"that statement should not be introduced here by a later
edit"**. It also closes the adjacent route: the `lgbm`-vs-`exact` caveat is *"a reason the choice is safe,
not evidence that it is immaterial."*

**THE TWO GATES ARE SEPARATED, which was the `BEN-082` risk.** *"Nothing here adopts the standard
five-dimensional covariance"*, with the verifier's `BLOCK`, fourteen defects outstanding, and
*"it does not authorise the covariance-construction stages"* — *"The two questions are independent."*

**BUILD AND CONTAINMENT, measured twice because `build_all.sh` exits 0 with undefined references on a cold
tree.** `bash build_all.sh` (it is mode 644 and its own header says `bash`, so `./build_all.sh` returns 126
— **not** a build failure) → **exit 0 on both passes, zero undefined reference/citation mentions in either,
and the two passes' verdict lines are byte-identical**, so there was no first-pass artefact to mistake for a
pass. `main_note.pdf` 86 pp, `main_primer.pdf` 5 pp, `main_paper.pdf` 7 pp. `check_dead_containment.py` →
`RESULT :: PASS`, note carrying 18/18 struck literals and **0 of 18** in both outward builds.

**Containment verified at PDF level, not only from the include list:** `app_negweight` is included by
`main_note.tex` only (1/0/0), and `pdftotext` finds the footing text's distinctive strings **7 times in
`main_note.pdf` and 0 times in both `main_paper.pdf` and `main_primer.pdf`.**

**NO INTERACTION with the stale `values.tex` macros**, which were not to be touched and were not:
`app_negweight.tex` contains zero `gbdtFive` references, and `\gbdtFiveAdoptTrace 5.81e-38`,
`\gbdtFiveCVTrace 6.24e-38`, `\gbdtFiveMeanShift 1.65e-38` remain at `values.tex:58-60` unchanged. The
footing text uses only the `nw*` set.

**NOT ESTABLISHED:** whether the *physics* of the footing choice is right — this lane verified that the note
says what Joseph ordered and does not say what he prohibited, which is a boundary check, not a review of
the measurement. And `OI-6`'s explicit obligation to revisit the footing before submission is recorded in
the note and is **not** discharged by any of this.

## 2026-08-16 — `VL134`–`VL140` independently re-derived by a second lane; the arm-1 `G0` condition discharged from the task logs

**Append-only.** Executor lane, read-only: `ssh` reads and login-node `python` over `/pscratch`, plus
local reads of the tracked tree. **No `sbatch`, `scancel`, `scontrol`, resubmission, or write to the
cluster checkout; no GPU.** Verifies `bb91391`'s rows, which one lane built.

**THE AUTHORIZATION'S BINDING CONDITION IS DISCHARGED, and it needed a task log rather than a dry run.**
`AUTHORIZATION-20260815-arm1-resubmit.md` made copy order part of the grant and specified a
self-identifying line: **3 pins means the old launcher ran and provenance is not intact; 4 means the
hardened one did.** Line 1 of all three arm-1 logs reads `G0 PASS
driver/annealed-wrapper/engine/instrumentation all match their digests`, and the logs print the four
digests, wrapper `ee269b09…` — **the repaired file of `4e85f0e`, so arm 1 exercised the `BEN-314` dtype
fix.** `sacct`: `57038937_{3,4,5}` **`COMPLETED 0:0`** at `01:56:59`/`01:57:24`/`01:58:29`, against
`~2:00 FAILED 1:0` for the float64 attempt. Arm 0 `57012031_{0,1,2}` still `COMPLETED 0:0`, untouched as
the grant required. The wrapper pin has since moved `ee269b09 → b24cfefe` for report-annotation fixes;
`sbatch_foldforward_instrumented_closure.sh:86-92` documents the move and **the logs preserve what they
ran**, so arm 1 needs no repin and is not orphaned by it.

**`VL134`/`VL135` reproduce to 10 digits, `VL136`–`VL139` to every digit the ledger prints** — including
the exact permutation enumeration, re-run here at `2/20`, `p = 0.1`, confirmed as the **design floor** at
3-vs-3 and not evidence of weakness. Arm-0 mean `1.0108786131109` against ledger `1.010878613`; Δrecovery
`−0.006888480` at `16.228` pooled sd, ranges disjoint, `9/9` realized pairwise.

**The independence is in the starting point, not the conclusion.** This lane used the **raw unnormalized
`w_reco`** from the inventory — summing to `682772`, not the loader's `1e6` — with a freshly written
reduction and masks rebuilt from the input NPZ. **Ratio agreement at `1e-13` across two different
normalizations demonstrates the scale invariance more strongly than the receipt's `3.5e-12` control,
because it arose incidentally rather than by construction.** Each `.npz` is bound to the log of the task
that wrote it: all six `sha256`-16 prefixes match the producing task's own `artifact … (sha …)` line and
all six are distinct, so these are six productions and the arrays reduced are the arrays those tasks
wrote. `weights_push` confirmed **post-`Unfold()` at the site** — `:332-333`, saved at `:351-352` — not
inferred from a description of it.

**The `59`-row population question, resolved by measurement.** `|pass_reco & pass_truth| = 836975` equals
the recorder's own `n_pass_reco` on all six runs, and `|pass_reco & ¬pass_truth| = 59` accounts for the
whole difference from the `837034`-row `pass_reco` population the `1.011418` prediction used. Sensitivity
`7.7e-07` against a `5.39e-04` residual — **`0.14%` of it, so `VL134`'s AGREE is unaffected**, and the
closure lane discloses both populations and the sensitivity. **One citation corrected:** the defining
site is `s1_b = pr[ib] & pg[ib]` at `:296`, received by `mcB` at `:311`; the receipt's `:305` lands inside
an unrelated `FLOAT32` comment. A slip, not a defect in the number — recorded because a `file:line`
exists so a later reader can falsify the claim cheaply, and one pointing elsewhere cannot be.

**LIMITS, stated because a verdict-only receipt is unfalsifiable (`BEN-077`).** Both lanes reduce the
**same six `weights_push` arrays** — one production, no second run — and the six recovery values still
have one source each, their own `G3` line. **`VL134` is now twice-derived, not recorded.** `OI-125` stays
**NARROWED, NOT CLOSED**: two reconstructions agreeing is still two reconstructions, and the caution that
neither `1.011418` nor `VL134` may close it is unchanged. Nothing promoted, nothing quotable, central
unmoved, the five Gate-6 prohibitions at `19585b7` untouched, nothing into `docs/analysis-note/`.

**`BEN-315` gained a fifth instance in the course of this work, and it was the lane's own tooling.** A
`if len(s) < 200: print(...)` walker used to survey the receipt silently dropped **18 of its 280 leaves**,
including the 250-character field that *defines* the population — on which evidence the lane concluded the
receipt documented that population by count and not definition, and was one edit from filing it as a
`BEN-077` row. `grep -c pass_truth` returns `1`. **A length filter over a document is a semantic filter:
the short leaves are values, the long ones are the definitions and caveats.** Recorded in §6 of the long
form, with the generalisation that **unreported omission is the entire defect in both truncation
instances** — `head -8` and `len(s) < 200` — and a one-line `N of M omitted` count defeats both.

*Receipt:* `docs/orchestration/state/RECEIPT-independent-verification-vl134-vl140-20260816.json`.

## 2026-08-16 — repair-10's `N3` confirmed BY MEASUREMENT and corrected twice: the gate measures BLAS accumulation order, and its docstring's disclaimer was quoted as its promise (`BEN-316`)

**Append-only.** Executor lane, read-only: local reads plus an in-process probe that restores what it
monkeypatches. **`p4_lib.py` NOT edited.** No compute, no cluster access, no authorization consumed.
Second read of the defect `20260816T062458Z-repair10-verdict.json` says its `BLOCK` rests on.

**DISPOSITION FIRST: the defect is REAL, confirmed at `HEAD`, and the `BLOCK` IS NOT DISTURBED.** The six
other defects, `self_guards_adequate: NO` and `authorizes_covariance_stages_4_6: false` stand untouched.
This lane holds no `P4_VERIFIER_PASS` token and adjudicates nothing. What is corrected is the verdict's
quotation and its stated basis — `AGREED-WITH-CORRECTION`, the shape `BEN-352` recorded as unexpressible
by a plain agree/disagree bit.

**WHAT THE LEG CAN MEASURE, and it is not projection validity.** `check_projection_validity`
(`p4_lib.py:1413-1435`) compares `project()` = `M @ C_high @ M.T` against `MH = M @ C_high` followed by
`direct[i,:] = MH[i,:] @ M.T` row by row. **That loop IS `MH @ M.T` by the definition of matrix
multiplication** — the same product written out one row at a time — so the only quantity `err` can hold is
the difference between a row-at-a-time `GEMV` and a whole-matrix `GEMM`. Measured at `HEAD`, with
`p4_lib.py` **byte-identical to the verdict's `code_rev` `0e83b54`** (`git diff --stat` empty):
`relerr = 1.851e-16` against threshold `1e-9`, **5.40e6× headroom**; `project()` **bit-identical** to the
one-shot; row loop differing from it by `8.882e-16`. On the suite's own fixture
(`tests/test_p4_repair.py:136-143`) the error is **exactly `0.0`**, so `assertLess(relerr, 1e-12)` compares
zero to a tolerance — `BEN-314`/`BEN-312` family, **not filed separately** because an identity leg that
cannot fail cannot be given a test that can.

**CORRECTION 1 — THE QUOTATION IS INVERTED, and this is the part a later reader would carry forward.**
`N3` states the docstring *promises* its leg *"compares against an independently-produced product."*
`p4_lib.py:1414-1415` says, verbatim: **"Recomputation identities only -- nothing here compares against an
independently-produced product."** The words match because the verdict lifted them from the sentence that
**negates** them. The real overclaim is narrower and different — *"a direct block-sum recomputation"* by
*"an independent route"* — and **the two point at different repairs**: the quoted promise would have a lane
build the product comparison the function deliberately refuses, where the actual overclaim is fixed either
by writing a genuine `sum_{a,b} M[i,a] C[a,b] M[j,b]` accumulation or by deleting the leg and the sentence
together and letting symmetry, PSD and shape/coverage carry the gate honestly.

**CORRECTION 2 — "A CHECK THAT CANNOT FAIL" IS CHECKABLE AND FALSE.** Mutation-tested: a `2.0 *` edit to
`project()`, still symmetric and still PSD, **IS caught** at `rel 5.000e-01 > 1e-09`. So the leg is a
**source-drift regression guard on `project()`** — a real if modest function, and exactly the class the
docstring's *other* sentence claims. What it cannot do is anything about validity: a corrupted `M`
(row 0 ×3, `project()` untouched) **passes at `3.033e-17`**. **The precise defect: not a check that cannot
fail, but one that cannot fail for any reason connected to the validity of the projection.** `N3`'s
severity survives that narrowing intact — stages 4-6 need the second thing and the gate supplies only the
first — **but a defect stated in a falsifiable form that turns out false is the kind a repair lane
dismisses wholesale, including the two-thirds of it that is correct.**

**NOT A NEW DISCOVERY.** `ND_OMNIFOLD_RUN_LOG.md:8805` already names *"`check_projection_validity`'s
non-independent second leg"* from repair-8. **This is the second lane to read it and the first to measure
it.** Nothing here re-litigates the 2026-08-09 gate removal at `:1399-1412`, which is Joseph's
re-specification and a separate question from whether what replaced it does what it says.

**Executable, per `CLAUDE.md`'s preference for the executable form:**
`docs/orchestration/state/probe-projection-identity-leg-20260816.py` — any cwd, no arguments, writes
nothing, `ALL REPRODUCED` at exit 0, **and exits non-zero if the leg's behaviour changes, including when
`N3` is repaired**, at which point it retires with the defect rather than being silenced. The number table
above goes stale invisibly; the probe does not.

*Long form:* `docs/orchestration/FINDING-20260816-the-gate-that-measures-blas-blocking-noise.md`.

## 2026-08-16 — arm 0's instrumentation is attested by NOTHING on the run side, `VL138` survives the version split anyway, and no receipt attests the anneal (`BEN-317`)

**Append-only.** Executor lane, read-only: `ssh` reads over `/pscratch`, local reads and `git` history.
**Nothing edited, nothing submitted, no authorization consumed.** Filed against this lane's own
instrumentation, checking whether the wrapper defects it named on 2026-08-15 still stand now that arm 0's
numbers are `VL134`/`VL135`/`VL136` and arm 1's contrast is `VL138`.

**No number is overturned.** Two of three gaps are closed by measurement below; the third is bounded and
left open. All three were invisible from the receipts.

**ARM 0 RAN THE 3-PIN LAUNCHER AND NOBODY APPLIED THE AUTHORIZATION'S OWN TEST TO IT.** That test cleared
the *resubmit*; line 1 of all three arm-0 logs is `G0 PASS driver/annealed-wrapper/engine all match their
recorded digests` — **three pins**, because arm 0 predates `c6edc13`, **and the wrapper pin is the one that
covers the instrumentation.** The old launcher also printed **no per-file digests at all**, so arm 0's logs
do not record even the three values they checked.

**WHICH WRAPPER ARM 0 RAN, ESTABLISHED FROM ITS PRODUCTS RATHER THAN THE TIMELINE.** Two versions existed
at arm 0's `12:23:59Z` launch. `948e2b07`'s `install_fold_forward_recorder(base)` had **no `correct`
parameter**, so it wrote none of `fold_forward_arm` / `fold_forward_correction_applied` /
`records[].correction_requested` — **all three present** in arm 0's report (`arm0_instrumented_only`,
`False`, `False`). An unrenamed `recovery_criteria_met` and an absent non-quotability `label` exclude
`b24cfefe`; the timeline excludes `ee269b09` (`12:55:45Z`). **⇒ arm 0 ran `253f25c0`.** That digest appears
in exactly **one** tracked file — the authorization — where it means *the stale copy to be replaced*;
**this entry is the first place the linkage is written down.**

**THE TWO ARMS OF `VL138` RAN DIFFERENT WRAPPER VERSIONS, AND THE CONTRAST SURVIVES.** `git diff c5c360e
4e85f0e` on the wrapper is **one hunk, 21 insertions, 1 deletion**, every changed line inside the
`if correct:` block at `:141` — the `BEN-314` dtype repair. **Arm 0 runs `correct=False` and never enters
it**, so the two versions are behaviourally identical on arm 0's path. **Diffed, not assumed** — which is
the only thing separating this from `BEN-315`.

**STILL OPEN: NO RECEIPT ATTESTS THAT THE ANNEAL TOOK EFFECT.** All six ran `--annealed` and the
composition is real (`closure_foldforward_instrumented.py:303-308`), but the wrapper binds `lr_records` and
discards it, writing only `fold_forward_composed_with_annealed_arm = True`. **That boolean records that the
install function was CALLED, and is `True` even when `fit_lr_records` is EMPTY** — precisely the state
`closure_powered_annealed_lr.py:114-115` fails closed on. `assert_anneal_took_effect` is reachable only from
that module's `main()` (`:178`), which the wrapper bypasses by design, **so the one guard that separates an
annealed run from an un-annealed one is in the tree, wired into a path these six runs did not take**
(`BEN-312` family). Measured: **no `lr_proof` in any of the six receipts; no `[annealed] LR pattern
VERIFIED` in any of the twelve `.out`/`.err` files** — the only `anneal|learning` matches are the word
inside the `G0` line — **and none of the 29 wrapper tests exercises the annealed composition.**

**WHAT BOUNDS IT, SHORT OF ATTESTING IT.** The band `VL136` passes against comes from proven-annealed runs:
`state/annealed-shape-r2-terminal-56552326.json` carries `anneal_lr_proof pass = True`, *"two fits at
9.999999747378752e-05"* and *"four fits at 9.999999747378752e-06"*, `records = 6` — the expected count at
`niter=3`. Arm 0 is **bit-identical** to that run on `h_prior`, `h_target` and `h_untilted` (`0.0` max abs
cell difference) and its recovery sits **`0.535` declared draw-sd** from the three-run mean inside a
**`1.557e-03`** band, so an un-annealed arm 0 would have had to land there by coincidence. **But the static
spectra match because the INPUTS and INJECTION match, which carries no learning-rate information** — so
this bounds the risk and **must not be recorded as attestation.** **Disposition: a PROVENANCE gap, not a
suspicion of a wrong configuration.**

**THE FIX IS TWO LINES, NOT ONE, AND IS WEAKER THAN IT LOOKS.** `base_lr` is derived from the records
themselves (`:177`), so the assertion is **partly self-referential**: it catches an empty record list and a
wrong *pattern*, but **cannot** catch a globally wrong base rate, since the highest observed rate becomes
the standard. `ANNEALED_LR = 1e-5` (`:47`) is a literal and is checked; the base rate is not. **Not
implemented, not authorized, and it cannot retro-attest the six runs** — nothing can, short of a rerun.

**THE TRANSFERABLE RULE, AND IT INDICTS AN ACTION THIS LANE WAS AUTHORIZED TO TAKE.** The only direct
witness to arm 0's instrumentation was the file on `/pscratch`, and **the authorized arm-1 resubmit
overwrote it.** The copy was required, the copy order was the binding condition, and executing it was
correct — **and it destroyed the last direct evidence of what arm 0 ran.** It survives only because the
interlock demonstration happened to print `253f25c0…` in a refusal message: **a by-product of testing the
gate, not a decision to preserve provenance.** A clean one-step "copy both", which the authorization's own
table recommends, would have lost it. **RULE: before overwriting any cluster file a completed run's
provenance depends on, record its digest in the same turn.** General form, and it is the worse half:
**`G0`'s pin set defines what a run can prove about itself after the fact, so a file added to the pin map
later leaves every EARLIER run permanently unattested on that axis — and the earlier runs are the ones
already published.**

*Long form:* `docs/orchestration/FINDING-20260816-the-arm-whose-instrumentation-nothing-pinned.md`.

## 2026-08-16 — the anneal attestation IMPLEMENTED: a future run now proves the anneal took effect, and the self-referential limit was CLOSED rather than documented (`BEN-317`)

**Append-only.** Executor lane. **Code change, no run:** wrapper + launcher + 11 tests. No GPU, no
`sbatch`, no promotion, nothing into `docs/analysis-note/`, the five Gate-6 prohibitions at `19585b7`
untouched. Approved by the mediator under Joseph's standing grants after **this lane's escalation was
overruled — correctly.**

**THE ESCALATION WAS WRONG AND THAT IS PART OF THE RECORD.** This lane wrote that the fix *"is yours and
Joseph's call, not mine"* because the wrapper is `G0`-pinned and its six products are in the ledger. Joseph
pushed back. Tested against the grants: **not a run** (no GPU, so `b5e067d`'s one-GPU-day bar is not
engaged), **not promotion** (`c1afe7a` does not reach it), and the pin is in the launcher's **own `PINS`
array** — already moved once the same night with the move documented, i.e. a pin tracking a file that
legitimately changed, **not `OI-123`'s "repin a receipt-bound launcher to make a check pass."** Ordinary
repair work. **Over-escalation has a cost like under-escalation does: it puts a decision in front of the
principal that the standing grants already answered.**

**WHAT LANDED.** `attest_anneal_took_effect` in `closure_foldforward_instrumented.py`, emitting
`anneal_lr_proof` in the form run `56552326`'s proof already uses (fit counts per rate, record count vs
`niter`). The launcher's `G3` now **refuses a product without a passing proof**. Wrapper pin moved
`b24cfefe → 0e1471ba` **in the same commit**, documented as move 2 at `:86-105`.

**THE LIMIT THIS LANE DECLARED YESTERDAY TURNED OUT TO BE CLOSABLE, AND THAT CHANGED THE DESIGN.** The
`BEN-317` filing said the fix was "two lines, not one" and **partly self-referential**, because
`closure_powered_annealed_lr.py:177` derives `base_lr = max(r["learning_rate"] for r in lr_records)` — so
whatever the highest observed rate is *becomes* the standard, and a run at 10× every intended rate is
perfectly self-consistent. **That is true of the sibling and did not have to be true here.** The engine
DECLARES its base rate — `self.LR`, `omnifold.py:127`, defaulted `1e-4` at `:57`, never overridden by
`closure_powered_truth_reweight.py:328-331` — so the recorder captures it off the live instance
(`engine_declared_LR`, `anneal_start`) and the attestation compares against a **declared** value rather than
an **inferred** one.

**THE IMPROVEMENT IS DEMONSTRATED, NOT ARGUED.**
`test_A_GLOBALLY_WRONG_BASE_RATE_IS_CAUGHT_HERE_AND_NOT_BY_THE_SIBLING` builds base fits at `1e-3` with
annealed fits correct at `1e-5`, **runs `cpa.assert_anneal_took_effect` on it and shows it PASSING**, then
shows this one refusing. **A claim that one guard is stronger than another is worth exactly the case where
they disagree**, so the test executes both instead of reasoning about their sources.

**POWER-TESTED BEFORE LANDING (`BEN-314`: a guard that passes on what it exists to catch is worse than
none).** 11 new tests, **every one a demonstrated refusal rather than an asserted success**: empty records,
`None` records, a wholly un-annealed run, annealing the wrong iteration, a missing/NaN/zero/negative
declared rate, the `start` boundary, and the discriminating case. `G3`'s assertion was separately exercised
against four bad reports — proof absent, `pass=False`, zero annealed fits, proof not a dict — and **refused
all four**, with the valid one passing. **41 passed** in the wrapper suite (the pin test failed first, as
designed, until the pin moved), **154 passed** across the hash-binding/preflight/receipt/powered selection,
and both of the launcher's embedded python blocks compile.

**ONE DELIBERATE NON-FATAL CHECK, declared rather than buried.** Fit COUNT is recorded and cross-checked
against `2 × niter` but does **not** raise; only the RATES fail closed. This function runs *after* a
multi-hour GPU run, and a false refusal over a count whose invariance across future engine paths this lane
has not established would discard a good run's annotation. The rates are what the predeclaration is about.

**IT RETRO-ATTESTS NOTHING.** The six 2026-08-15 receipts are **left unmodified — they are the record.** They
ran `b24cfefe` or earlier, carry the boolean alone, and remain **BOUNDED, NOT ATTESTED**; only runs launched
after this commit carry `anneal_lr_proof`. Said in three places that cannot drift apart from the code: the
field note the wrapper writes, the launcher header at `:100-105`, and
`test_the_proof_does_not_claim_to_cover_the_six_existing_products`, which fails if the wording is removed.
`VALIDATION_LEDGER.md`'s `VL134`–`VL140` block now carries the same statement where a reader consuming those
numbers will meet it.

**Rule 4c note:** `p4_lib.py` is on the 20-path surface and this work is entirely in `nd-unfolding/pet/` plus
`tests/`, so 4c is not engaged by it. Landed rather than left uncommitted, as instructed.

## 2026-08-16 — the END-OF-RUN push is now RECORDED BY THE RUN, predeclared before anything carries it, with NO run attached

**Append-only.** Executor lane. **Zero-GPU code change:** wrapper + launcher + 8 tests + predeclaration.
No `sbatch`, no run requested or authorized, no promotion, nothing into `docs/analysis-note/`, the five
Gate-6 prohibitions at `19585b7` untouched, the six 2026-08-15 receipts unmodified. Approved by the
mediator directly as a zero-GPU change; **the 3-draw run that would exercise it was DENIED the same day.**

**WHAT IT CLOSES.** `Unfold` is `for i in range(start, niter): RunStep1(i); RunStep2(i);
CompileModels(fixed=True)` (`omnifold.py:172-177`) and `RunStep2` assigns `self.weights_push` (`:220`). The
existing hook records at CONSUMPTION, so **the push `RunStep2(niter-1)` leaves is consumed by nothing and
recorded by no row** — and that is the quantity `OI-125` needs, because
`closure_powered_truth_reweight.py:332-333` takes `of.weights_push` after `Unfold()` and
`train_fullevent_nominal.py:576-577` computes the nominal's `0.736746` the same way. The series goes from 3
points to 4. `BEN-360`'s gap, closed for future runs.

**THE OVERLAP IS A FREE INTERNAL GATE AND IT IS THE BEST PART.** The push `RunStep2(i)` leaves *is* the
push `RunStep1(i+1)` consumes, so `niter-1` of the new rows duplicate existing rows **by construction** —
gated to EXACT equality (`!=` on floats, no tolerance). **It holds for both arms**, because the `RunStep1`
row is the PRE-correction measurement. A disagreement means one hook reads at the wrong moment and the
end-of-run value cannot be trusted either. **Gated twice: in the wrapper, and again independently in the
launcher's `G3`, which does not take the wrapper's word for it.**

**THE REDUCTION WAS EXTRACTED TO ONE PLACE (`_ff_reduce`) RATHER THAN COPIED.** Two hooks computing "the
same" fold-forward from two similar blocks is exactly how the overlapping rows would silently stop
agreeing — and the cross-check would then be comparing two implementations instead of two points in time,
which is `BEN-300`'s shape one level down. A test asserts the single definition.

**POWER-TESTED, per the mediator's condition and `BEN-314`.** The load-bearing claim is that the hook's
final capture is bit-identical to what the driver persists, because only `CompileModels(fixed=True)`
intervenes. **Demonstrated on a fixture that mirrors the engine's loop including that trailing call** —
omitting it would have assumed what the test exists to show — and paired with
`test_THE_ASSERTION_ABOVE_HAS_POWER_a_pre_delegation_capture_FAILS_it`, which shows a wrong-moment capture
FAILING the same assertion. Without that control the bit-identity test could pass vacuously on a fixture
whose pushes happened to be equal. `G3`'s new assertions separately exercised against five bad reports —
record absent, not flagged, wrong count, **hooks disagreeing**, push non-numeric — **refused all five**,
valid one passes. **167 passed** across the wrapper and `p4_repair` suites; the pin test failed first, as
designed, until the pin moved.

**PREDECLARED BEFORE ANYTHING CARRIES IT** —
`docs/orchestration/PREDECLARATION-20260816-endofrun-push-recording.md`, per `BEN-361`: a predeclared
expectation is worth its timestamp and nothing else. **E3 is the load-bearing prohibition: a future
recorded value CANNOT validate `VL134` and must not be reported as confirming it.** The driver takes no
seed flag (only `--split-seed`; launcher `:23-24`), so any later run is a NEW SAMPLE of the same
configuration — if the two are printed together they are two samples, not a measurement and its check. E4
declares the expected `≈-3%` gap from the last consumed row as the ARTEFACT, so a future run cannot report
it as a finding. E5 declares `deviation_from_R` on the new row as having no adopted threshold and forbids
building a gate from it in the document that first reports it.

**Wrapper pin MOVE 3, `0e1471ba → 7499814e`, same commit**, documented at `:111-127` beside moves 1 and 2.
Driver/annealed/engine pins byte-identical. **Ordering fixed in the record rather than left to whoever
launches next: this and the anneal attestation (`1b09a47`) both land BEFORE anything launches, because a
run wants both.**

**IT DOES NOT CLOSE `OI-125`.** That is about numbers already in the ledger, which cannot be retroactively
recorded. `VL134` stays a **re-reduction of a persisted array** — twice-verified to `1e-13`, reliable, and
still reader-computed. What a recorded value changes is *who* computed it.

**`BEN-315`'s executable form adopted, and it is now a two-lane finding.** The mediator ran a near-identical
truncating walker over the same receipt on the same night and was misled the same way, which makes it a
property of the tool rather than either lane's carelessness. §6a of the long form now ships a `survey()`
that prints `N FIELD(S) OMITTED` **with their paths** — tested against the receipt it failed on: 263 leaves
printed, 17 reported omitted, and the report names
`/RESULT_1.../masks/recorder_population_s1_b`, the field whose absence was wrongly claimed. **The 17-vs-18
discrepancy is reconciled in the text**: one leaf is exactly 200 characters and falls on the other side of
`<` vs `<=`. `263 + 17 = 280`. That a one-character difference in an arbitrary cutoff moves a field between
"read" and "invisible" is the argument for the omission report, not a footnote to it.

## 2026-08-16 — `BEN-318`: redundancy that arises by construction is a free internal check, and a cross-check must share exactly what it is not testing

**Append-only.** Executor lane. Documentation only — no code, no run, no cluster access, `p4_lib.py` clean
and untouched (rule 4c). Filed while holding for lane A's `N3` repair, which **has not landed**: measured
this turn, `git log -1 -- nd-unfolding/p4_lib.py` still returns `5fc06b6`.

**Filed as its own row at the mediator's direction, not as a clause inside `BEN-360`** — the reason
`BEN-361` had to be separated from it: **a clause inside another finding is read as that finding's
illustration rather than as a rule in its own right.**

**§1, the habit.** `67c94df`'s `RunStep2` hook produces `niter` rows of which `niter-1` **duplicate rows
already in the report**, because the push `RunStep2(i)` leaves IS the push `RunStep1(i+1)` consumes. **The
duplication was not designed — it fell out of hooking two adjacent points in one loop.** Trim it (smaller
output, no information lost, **and no check**) or enforce it (gate to EXACT equality, `!=` on floats, no
tolerance). **Trimming is the tempting move: it looks like housekeeping, a reviewer optimising for concision
would ask for it, and "those rows are already in the report" is TRUE.** What it discards is the only thing
in the run capable of catching `BEN-360`'s failure. **Before, "the recorder might read at the wrong moment"
was a paragraph in a finding; after, the run refuses.** `CLAUDE.md`'s trade reached from the other
direction, **and it cost nothing** — both numbers were already being produced and the only decision was
whether anything compared them.

**§2, and it is the part that took work: this finding appears to CONTRADICT `BEN-316`, filed hours earlier
by this same lane, so it is resolved here rather than left to a later reader who will notice.** `BEN-316`
condemns `check_projection_validity` for checking `M C M^T` against a second computation that **re-encodes
the same formula** — *"`BEN-300`'s single-source case"* — and then this finding's own gate **deliberately
makes both sides share one implementation**, `_ff_reduce` being *extracted* so the two hooks cannot compute
the fold-forward differently, where two copies would have been more independent. **The lane argued for
independence in the morning and against it in the evening. Both are right.**

The resolution is **what the check is FOR.** The identity leg claims *the formula is correctly implemented*,
so it must share the INPUTS and differ in the ROUTE — and it fails precisely because it shares the route,
the thing it claims to test. The overlap gate claims *two hooks read the same array at the same logical
MOMENT*, so it must share the REDUCTION exactly and differ only in the moment. **Duplicate the reduction
and the gate fails in the mirror-image way: any implementation difference surfaces as a value difference,
and a value difference is INDISTINGUISHABLE from a timing error** — it would fire on a formatting change
and report *"the hooks disagree"* when what disagreed was the arithmetic. **A confounded check is not a
weaker check; it is a check of a DIFFERENT PROPOSITION.**

**RULE: a cross-check must SHARE exactly what it is not testing and DIFFER in exactly what it is.** Ask what
the check CLAIMS before reusing an implementation — **"more independent" is not automatically stronger, and
"shared" is not automatically a restatement.** The cheap diagnostic for the `BEN-316` family: **a check
whose two sides differ in nothing that matters cannot fail; one whose sides differ in too much cannot
localise.**

**RECORDED AGAINST THIS LANE, because the wrong reason does not generalise:** `_ff_reduce` was extracted for
**tidiness** first. Only afterwards did it become clear that with two copies the gate would compare
implementations rather than moments — **while looking identical in the report and in the test names.** The
right decision was reached for the wrong reason.

*Long form:* `docs/orchestration/FINDING-20260816-share-what-you-are-not-testing.md`.

## 2026-08-16 — the `G0` REVISION GATE: an expectation the tree cannot supply about itself (`BEN-301` fixed, not documented)

**Append-only.** Executor lane. **Local work only** — no cluster access, nothing launched, no run
authorized, `p4_lib.py` untouched. Predeclared before implementation:
`docs/orchestration/PREDECLARATION-20260816-g0-revision-gate.md`.

**WHAT `BEN-301` IS, and it was measured rather than imagined.** The cluster held wrapper `ee269b09`
against a cluster pin literal reading `ee269b09`, so **`G0` would have PASSED** while the checkout sat 663
commits behind and the run would have carried none of `MOVE 2`/`MOVE 3`/`MOVE 4`. **A digest pin
authenticates content against an expectation stored in the same tree, so it is blind to the tree being
stale — both sides go stale together and agree perfectly.**

**THE FOUR ITEMS, ranked, because items 1-2 alone would LOOK like a fix.** (1) `FF_EXPECT_REV` required,
**no default**; (2) assert `git rev-parse HEAD` equals it; (3) **compare each pinned file against
`git show $FF_EXPECT_REV:<relpath>` — the blob at a NAMED REVISION, not a co-located literal**; (4) extend
the pin set to `train_fullevent_nominal.py`. **Only item 3 fixes the defect**: a tree can be at its own
`HEAD` and still be 663 commits stale. `G0`'s literals survive as **cross-checks**; the revision is the
authority, and a literal disagreeing with the blob is now a refusal.

**ITEM 4 CLOSES A `BEN-312` GAP FOUND WHILE ADJUDICATING `(A′)`.**
`closure_powered_truth_reweight.py:224` does `from train_fullevent_nominal import NOMINAL_SEED_POLICY`
**unconditionally, inside `main()`**, and that dict supplies `niter`/`epochs`/`batch_size`/`train_events`/
`lr_policy`. It was **not pinned**, so a dirty copy could change what the run trained while `G0` reported
`PASS` on four files. Pinned at `91144bee`. The `G0` log line now names **five** files; runs before this
print four, which is itself a provenance marker in `BEN-317`'s sense.

**THE VACUITY GUARD, which is the first thing a later reader will try to remove.** `FF_EXPECT_REV` must
match `^[0-9a-f]{40}$`; `HEAD`, `main`, `master`, `@`, `HEAD~0`, `HEAD^{}`, `refs/heads/main`, a 12-hex
abbreviation, a 39-hex string and any uppercase form are **REFUSED**. Without it `FF_EXPECT_REV=HEAD`
resolves against the stale tree itself and passes for every file forever — **repair-9's defect verbatim, in
a second gate, six days later.** Mirrors `p4_check_verifier_token.py`'s `is_literal_commit_sha`.

**FAIL CLOSED ON ABSENCE is the property the design rests on, and it answers lane B's objection.** Prose did
not prevent lane B's recurrence — the trap was documented 440 lines up in the file that reintroduced it. **A
prose rule fails silently when unread; a value check fails silently when nobody supplies the value; a
required variable with no default cannot be silently omitted — omission is a refusal.** Precedent in this
campaign: `BEN-317`'s `fold_forward_composed_with_annealed_arm` was **`True` on EMPTY input**, which is why
replacing it was worth doing. **A guard satisfiable by the absence of its own evidence IS the defect.**

**POWER-TESTED, 17 cases, every one a demonstrated refusal (`BEN-314`), against THROWAWAY repositories and
never the live tree (`BEN-332`), with mutations in the WORKING TREE the gate reads rather than the index
(repair-10's staged-copy trap).** Axis per control (`BEN-342`): vacuity; existence; **`BEN-301` staleness**;
uncommitted drift; the literal being cross-checked not authoritative; absence; a file absent at that
revision; a file outside the repo; and a clean tree at the named revision **passing**, so the suite is not
satisfied by a gate that refuses everything.

**THE CONTROL THAT LICENSES ITEM 3, and without it the claim is unfalsifiable:**
`test_AND_THE_OLD_COLOCATED_LITERAL_CHECK_ACCEPTS_THAT_SAME_TREE` executes the pre-fix comparison on the
identical stale checkout and **shows it PASSING**, then shows the new gate refusing. **A claim that one
guard beats another is worth exactly the case where they disagree** (`BEN-318` §2) — the same standard as
`test_A_GLOBALLY_WRONG_BASE_RATE_IS_CAUGHT_HERE_AND_NOT_BY_THE_SIBLING`.

**LIVE DEMONSTRATION on the real repo and the real five-file pin set** (read-only): `PASS` at
`1f6bafa89279ad08c5953b793a411438bc75ef25` printing all five digests, which match the launcher's literals;
`--rev HEAD` **REFUSED** as symbolic; an expectation naming `HEAD~3` **REFUSED** with the `BEN-301` message.

**WHY THE LOGIC IS IN A PYTHON HELPER.** `G0` uses `declare -A`, needing bash ≥ 4, and the only bash on the
development machine is **3.2.57** — so `tests/test_foldforward_launcher_guards.sh` SKIPS there, and
`LauncherWrapperPinTest` already records the consequence: *"a pin that only a skipped test checks is a pin
that goes stale silently."* A revision gate whose power test could not run locally would inherit that
exactly. The launcher keeps a **minimal bash-3.2 preamble** that authenticates the helper against the
revision *before* invoking it. **THE BOOTSTRAP IS NOT FULLY CLOSED AND IS STATED, NOT HIDDEN:** a file that
checks pins cannot authenticate itself; the preamble closes one level and the preamble itself is trusted,
mitigated only by being short enough to read in full.

**TWO TEST BUGS FOUND AND FIXED, both instructive.** The wiring guard was **defeated by the launcher's own
comment warning against `${FF_EXPECT_REV:-HEAD}`** — a test a comment can trip is measuring the wrong text,
so those assertions now read a comment-stripped copy. And `${FF_EXPECT_REV:-}` was removed from the code
even though the following `-n` check made it harmless: the launcher uses `set -eo pipefail`, not `set -u`,
so no `:-` is needed, which makes *"`FF_EXPECT_REV` never appears with `:-`"* a **bright line**. *"An empty
default is fine"* is an arguable line, and the next reader arguing it is how `:-HEAD` gets added.

**THIS DOES NOT MOVE THE WRAPPER PIN.** The launcher is edited, not the wrapper; `e284cdbc` (lane B's
`MOVE 4`) is unchanged. The DRIVER is not repinned (`BEN-270`) and driver/annealed/engine literals are
byte-identical — `train_fullevent_nominal.py` is an **addition** to the set, not a repin of anything.
Tests: **189 passed** across the three affected suites, **34** on the hash-binding/preflight selection.

## 2026-08-16 — the `(A′)` runtime-and-receipt closure: the cluster update is THREE files, and both "dirty" runtime deps are content-identical to local

**Append-only.** Executor lane. **READ-ONLY throughout** — `ssh` reads and `sha256sum` over `/pscratch`,
local reads and `git` plumbing. **No `sbatch`, `scancel`, `scontrol`, resubmission, pull, or write of any
kind to the cluster. Nothing launched.** Artifact:
`docs/orchestration/state/RECEIPT-aprime-runtime-receipt-closure-20260816.json`.

**THE STOPPING CONDITION HELD AND THE ANSWER IS SMALL.** Of the runtime closure, exactly **three** items
need action: the launcher (cluster `ee317ccd` vs local `4ffd5655`), the wrapper (cluster `ee269b09` vs local
`e284cdbc`, missing `MOVE 2`/`3`/`4`), and `ff_revision_gate.py`, **absent** on the cluster. **Everything
else the run reads is content-identical between the trees** — annealed wrapper, driver, all five
`omnifold/*` modules, the quarantine module, the dump contract, `pet_bootstrap`, the Gate-4 validator,
`atomic_write`.

**AND THAT INCLUDES BOTH FILES `git status` CALLS DIRTY, which is the most useful thing in the inventory.**
`train_fullevent_nominal.py` (`M`, 9/26) and `fullevent_fps_dataloader.py` (`M`, 38/5) are **byte-identical
to local `HEAD`**. **The dirt is a FORWARD PORT relative to a stale `HEAD`, not divergence — "dirty" on a
stale tree can mean "already updated", and that is invisible from `git status` alone.** Consumed values
checked rather than assumed: `NOMINAL_SEED_POLICY` value-identical, `LR_POLICY_ANNEALED` byte-identical
including `base_lr 1e-4`, and the diff touches neither assignment; the loader's edit is the Gate-5
`precomputed_target_replica_seed` split, unreachable at `bootstrap_seed None`. **Recorded with that
comment's own caveat — *"That is an argument, not evidence"* — because the evidence here is only that the
two trees' CONTENT matches, which makes the reachability question moot for this comparison.**

**A CONSEQUENCE OF MY OWN GATE, STATED BEFORE JOSEPH IS ASKED FOR TIME RATHER THAN DISCOVERED AFTER.**
`G0b` asserts `git rev-parse HEAD == FF_EXPECT_REV`, required and non-symbolic. **Copying three files into a
tree 663 commits behind leaves `HEAD` unchanged, so the gate REFUSES — correctly.** "Copy the pinned files
and launch" is therefore **permanently unavailable on any path**, and the eventual launch requires the
cluster tree genuinely to be at a named revision. That is the intended outcome and it is **stricter than
`(A′)` alone**, so it changes the cost of the launch and not only its safety.

**STILL OPEN, and it is the same shape `f521468` just fixed one instance of:**
`fullevent_fps_dataloader.py` is an **unconditional runtime import that the launcher does not pin** —
`BEN-312` identically to `train_fullevent_nominal.py`, and `f521468` closed only the latter. It is
content-identical across trees today, **which is exactly the state `train_fullevent_nominal.py` was in
before anyone looked.** Recommend pinning it; **not done here**, because it is receipt-bound and
hash-pinned by the Gate-2 runtime, so a pin is a separate predeclared change rather than a drive-by.

**TWO ERRORS OF MY OWN, RECORDED BECAUSE THEY ARE THE SAME ERROR TWICE IN ONE COMMAND.** I first measured
`pet_bootstrap.py` and `verify_hash_bindings.py` under `nd-unfolding/pet/` and reported both **ABSENT ON
BOTH TREES**. Both guesses were wrong: they live at `nd-unfolding/pet_bootstrap.py` and
`docs/orchestration/verify_hash_bindings.py`. `pet_bootstrap.py` is in fact **identical** on both trees.
**`BEN-315`: a null result is evidence about the search, not about the world**, and it was caught only
because the paths were then located with `git ls-files` instead of the null being believed. Had I not
checked, this receipt would have reported two phantom missing files and understated the closure.

**One genuine difference worth naming, though not blocking:** `docs/orchestration/verify_hash_bindings.py`
is `ff410e2d` locally and `ca83948e` on the cluster. **The tool that VERIFIES hash bindings is itself a
different program on the two trees**, so "verified on the cluster" and "verified locally" are not the same
claim. Not on this run's path; recorded so it is not discovered during a dispute.

**Explicitly UNTRIAGED, per the stopping condition:** the remaining **17** tracked-dirty and **all 735**
untracked files. Two of the 19 are in the closure and both are measured above. The rest are **not claimed
harmless** — they are a preservation question for whoever updates the tree, not a launch question. Also
recorded from the mediator's measurement rather than re-measured: the cluster remote is named **`github`,
not `origin`**, and a second worktree `fe-fps-campaign` shares the area, so any update command written from
local muscle memory will fail or do the wrong thing.

## 2026-08-16 — CORRECTION by append to the `(A′)` closure receipt: a digest in it was stale before its own commit landed (`BEN-228` inside the anti-staleness artifact)

**Append-only, correcting the entry above rather than rewriting it** — it was true as chronology and wrong
as present tense. Read-only, local, nothing launched.

**THE ERROR.** The receipt recorded the launcher's local digest as `4ffd565531f2b437`. That was correct at
`f521468`, when it was measured, and **wrong by the time the receipt's own commit `df242cc` landed**: lane
B's `f386aa0` edited the launcher's comment block in between (the `~105 appears nowhere` retraction). The
value at `df242cc` is **`99424a83277b70d6`**, re-derived this turn with
`git show df242cc:<path> | shasum -a 256` rather than taken from the relay. **All other entries re-measured
at `df242cc` and unchanged**; the launcher was the only drift.

**WHY IT MATTERS MORE THAN A WRONG HEX STRING.** `BEN-228` — true-when-written, then read later as present
tense — **occurring inside the artifact built to prevent exactly that class of error**, and caught by the
mediator re-measuring rather than by any care taken while writing it. **It is not fixable by being more
careful:** the launcher is a file several lanes edit routinely, so any static digest of it is a claim about
a moment and nothing in the surrounding prose marks which moment.

**THE FIX IS STRUCTURAL, not a better value.** The receipt now (a) binds every local digest to
`df242cc1b0eff8ebd93dd82f3d75b1f000539bf4`, (b) ships `HOW_TO_RECOMPUTE_INSTEAD_OF_TRUSTING_THIS_FILE` with
the exact commands, insisting on `git show <rev>:<path> | sha256sum` and **not** `sha256sum <path>`, which
measures whatever the reader's own lane last edited, (c) marks the launcher **VOLATILE** and carries **both**
values with the moment each belongs to — deliberately, not as a hedge — and (d) states the dirty-vs-divergent
test that produced this receipt's main finding, since `git status` alone cannot express it.

**`BEN-315` INSTANCE COUNT ADDED, because the frequency is the finding, not any one instance.** Three in one
session across three lanes: the mediator's length-filtered walker; the mediator again asserting an operand
*"derives from nothing"* without grepping for it (it is in the receipt at `:23`, correctly computed and
correctly labelled `of_that_row`); and this lane reporting two files **ABSENT ON BOTH TREES** from two wrong
path guesses. **Two of the three would have shipped a false absence into a document. NONE was caught by a
rule** — all three were caught by somebody running the search a second time. **So `BEN-315` is not a lane's
bad habit; it is the default failure mode of reading a large tree, and the only demonstrated defence is a
second search by a second party.** Recorded with the limit of the executable defence already landed: §6a's
`survey()` printing `N FIELD(S) OMITTED` defeats the truncation instances but **not** a wrong path guess,
which is what two of the three were — for that the defence is `git ls-files | grep -E '/<name>$'` before
believing any null.

**`verify_hash_bindings.py` upgraded from "not blocking" to a directed item in the cluster-update plan.**
Local `ff410e2d`, cluster `ca83948e`: **the tool that ADJUDICATES hash bindings is a different program on the
two trees**, so *"verified on the cluster"* and *"verified locally"* are two different claims in the **same
words** — `BEN-082`'s shape located in the adjudicator rather than in a document, where a pin dispute
settled with one binary and re-checked with the other yields two honest and opposite answers. **Direction
recorded: the cluster copy moves FORWARD to the local one** as part of bringing the tree to a named
revision, not the reverse and not left split — the cluster's copy is clean at its stale `HEAD`, so it is what
that `HEAD` contains rather than a deliberate local modification. **No cluster write performed.**

**Deferred deliberately, on the mediator's instruction to stay available for the N3 second read:** pinning
`fullevent_fps_dataloader.py`, which is the same `BEN-312` shape as `train_fullevent_nominal.py` and needs
its own predeclaration because it is receipt-bound and hash-pinned by the Gate-2 runtime. 17 revision-gate
tests still green.

## 2026-08-16 — N3 + N4 repair: the projection gate now checks its own premise (lane A)

**Dispatch.** `N3` (high, `p4_lib.py check_projection_validity`) and `N4` (medium,
`crosscheck_marginal_vs_independent`), both outstanding at the repair-10 verdict
(`20260816T062458Z`, `BLOCK`, `authorizes_covariance_stages_4_6: False`). One commit, because verifier
rule 4b invalidates a PASS when an in-scope file differs between the reviewed commit and `HEAD`, and both
edited modules — `p4_lib.py` and `p4_project_4d.py` — are on the 20-path standard-P4 execution surface.

**Before-check, run in the same turn as the first edit:** `HEAD 7023870`; `git log -1 -- nd-unfolding/p4_lib.py`
→ `5fc06b6`; working tree clean for that file; `grep -c 'direct[i, :] = MH[i, :] @ M.T'` → 1. Re-checked
after landing, so a concurrent edit by the other `A` would surface as a conflict rather than an overwrite.

**`N3` — what was wrong, and why the prescribed fix was not enough (`BEN-328`).** The second leg computed
`MH = M @ C_high` then `direct[i,:] = MH[i,:] @ M.T`: the same BLAS product re-associated, so its `relerr`
measured accumulation order (~1.9e-16 against a 1e-9 threshold, and exactly 0.0 on the unit test's own
fixture). The brief prescribed a groups-and-weights block sum. **Measured before implementing: that route
cannot reach the predeclared bar.** A block sum reading its groups AND weights off `M` computes `M C M^T`
by definition, so a row scaled by 3, one weight scaled by 3, a column moved to the wrong row, and two rows
swapped all came back `1.5e-16 .. 5.0e-16` — invisible. **"Wrong" is a relation between `M` and its recipe,
so no function of `(C_high, M)` can decide it.** Repaired as two gates:

- `_block_sum_projection` — numpy reductions, no matrix multiplication, independent of `project()`'s
  expression (catches a doubled result at rel `5.0e-1`). **1.00 s vs 6.62 s for the BLAS product at the real
  10694 → 4825 shape**, because `M` carries one nonzero per column: the honest route is the cheaper one.
- `check_projection_matrix_matches_recipe` — rebuilds `M` from `(edges, drop_axis, mask_high, mask_low)` via
  `unravel_index`/`ravel_multi_index`/`searchsorted` (deliberately not `build_projection_M`'s `//`-and-`%`
  loop, which would make the comparison a tautology) and requires **exact** equality. Catches the probe's
  corruption at `max|diff| 3.0`. Wired into `p4_project_4d.py` at construction, where the ingredients are in
  hand; a library gate nobody calls is the defect class this repair is about.

`M` carries **width weights, not 0/1 membership** (`M[row,col] = wdrop[k]`); the recipe fixture uses unequal
W widths so a weight error is distinguishable from a mapping error. The self-contradicting docstring is
resolved by **scoping** the promise, not deleting it, and the blindness is now asserted in a test and
recorded in the receipt (`projection_identity_gates_M: False`) rather than left to a docstring.

**`N4`.** Finiteness accounting added, **`REPORT ONLY` unchanged** — the function still raises on nothing but
a shape mismatch, which is its specification. `BEN-329`: one non-finite input bin poisons **every** output
bin, because `0.0 * nan` is `nan`, so sparsity is not a containment argument; on the real products one bad
5D bin of 10,694 takes all 4,825 4D bins with it, and `median`/`p90`/`p99`/`max` go `nan` while
`n_over_3pct` reports `0` (`nan > 0.03` is False). Counts, `*_finite_only` summaries and a loud `note` are
now reported, and the printed `[xcheck]` line carries the fact — `BEN-327`'s shape, since a nan-poisoned
median prints as a plausible number and stdout is what a reader actually reads.

**Before/after is one command.** `docs/orchestration/state/probe-projection-identity-leg-20260816.py`
(lane D's, extended here) run against the pre-repair `p4_lib.py` — `sha256 aa3470e4…`, matching the baseline
lane D recorded at `3fe11de` — exits **2**, `PRE-REPAIR TREE -- the defect is live and M is ungated`, and
reproduces the `3.033e-17` corrupted-`M` pass. The repaired tree exits **0**. `BEN-316`'s sections 1–4 are
**expected** to keep passing and do: section 4 is "a corrupted `M` passes the identity leg", still true by
construction. The probe keeps the two expectation sets in separate buckets, because one exit code meaning
both "`BEN-316` no longer reproduces" and "the repair has not landed" licenses opposite conclusions.

**Tests.** 6 new in `tests/test_p4_repair.py`. Full suite **1461 passed / 2 failed / 1 skipped**, compared
**same-selection at `HEAD`** (`1455 passed / 2 failed / 1 skipped`): the two failures are identical and
pre-existing — `test_gate2_target_runtime` needs an absent `/pscratch` path, and
`test_pet_fullevent_nominal_launcher::test_config_gate_only_cli_no_train` is the known order-dependent
pollution (it passes when its file is selected alone). **Zero regressions.** `TMPDIR` set explicitly.

**Drift chain, followed to the end rather than silenced.** The 14 new recorded fields tripped
`test_p4_sweep_snapshots`; regenerated with the documented `--update` so the count change lands in review
(`115 → 129` fields, `28 → 29` gates), which then tripped the test binding the inventory *document* to the
snapshot, so `REPAIR6-RECORDED-NOT-CHECKED-INVENTORY.md` is updated and names the new fields. Recorded
there: the sweep is grep-level and cannot see `n_over_3pct_finite_only` and its two siblings, written
through an f-string key — a pre-existing limit of the extractor, named because a field the inventory cannot
see is what the inventory is for.

**Line citations that move.** `p4_project_4d.py` insertions shift the repair-8 verdict's anchors, derived
rather than computed: `:130`/`:132`/`:133` unchanged, `:182 → :204`, `:193 → :218`, `:197 → :222`. The
verdict JSONs are receipts and were **not** edited.

**Not done, deliberately.** No run, no `sbatch`, no covariance construction — the repair-10 `BLOCK` stands and
this commit does not lift it; `authorizes_covariance_stages_4_6` remains `False` and only the verifier can
change that. `P4_VERIFIER_PASS` untouched. The remaining outstanding count is the verifier's to restate: lane
B refuted `#7` by measurement, so 6 by that account, but this lane asserts no total.

### 2026-08-16, later — correction to the entry above: `BEN-328`'s impossibility claim was too strong

The entry above states *"so no function of `(C_high, M)` can decide it."* **That is false, and it is
corrected here rather than edited above, because this log is append-only.**

The independent second read on `N3`/`N4` **held the remedy and refuted the argument for it**, by
construction. Reproduced by this lane before accepting it: a function of `M` **alone** — (a) exactly
one nonzero per column, (b) all nonzeros positive, (c) every row carries the same multiset of nonzero
values — **catches 3 of the 4 corruptions this lane chose.** Clause (c) follows from the construction
itself, since `M[row,col] = wdrop[k]` depends on the dropped index and never on the row. Measured:
row scaled by 3, one weight scaled by 3, and one column moved to the wrong row are all caught with no
recipe; **two rows swapped is a pure relabeling — verified as the same multiset of rows — so every
structural invariant survives it and it provably needs the recipe.**

**The remedy is unaffected: the recipe gate is still necessary, and repair-11 returned PASS on it.**
What narrows is the argument. The harm in the original wording is specific: it licenses a future lane
to skip a cheap structural check on the grounds that checking is impossible — the same shape as the
docstring this repair fixed, a claim strong enough that a later reader stops looking.

**Operational sharpening, measured here and beyond what the second read claimed:** the invariant's
entire discriminating power is clause (c) — (a)+(b) alone catch **none** of the four. Clause (c)
dissolves with drop-axis coverage (distinct row multisets `1` full, `4` at 10% dropped, `6` at 30%,
`7` at 50%), and on the production configuration it cannot hold at all: 10,694 reported 5D bins over
4,825 reported 4D bins is a **mean W multiplicity of 2.216 of 6**. *Not* measured on the real masks,
which need unreadable ROOT products — an implication of committed counts, stated as such. **So the
claim is false in general, and on this configuration the recipe gate does all the work anyway.**

**The same overreach is in two other places and is NOT corrected here, deliberately:**

- `p4_lib.py:1417` and `:1485` assert it in docstrings. **Not edited: `p4_lib.py` is on the 20-path
  standard-P4 execution surface, and repair-11's PASS (`48ac04d`, `code_rev a8f7b2f`,
  `authorizes_covariance_stages_4_6: True`) would be invalidated by an in-scope edit under rule 4b.**
  A prose fix is not worth re-verifying an authorization the campaign has been blocked on. Queued.
  Nearby claims at `:1530` and `:1550` are correctly scoped to *recomputation identities* and stay
  true as written.
- **`docs/orchestration/runs/standard-p4-verifier/20260816T220615Z-repair11-verdict.json:19` asserts
  it too** — *"No function of `(C_high, M)` can decide whether `M` is the right matrix"* — inside the
  verdict that authorizes stages 4-6, where B1 is recorded as `UNSATISFIABLE-AS-WRITTEN`. **A receipt
  is immutable: cited, not amended.** The load-bearing copy of the error is therefore the one this
  lane cannot fix, and the verifier owns it. Its `B1`-was-defective finding is unaffected — B1 aimed
  the demand at the identity route, which genuinely cannot meet it.

## 2026-08-16 — STANDARD-P4 STAGES 4-6 EXECUTED under the repair-11 PASS: the first covariance construction this lane has ever been authorized to run (lane B)

**`chain rc=0`, all six stages, Slurm `57128458` on `nid004254`, 22:38:14Z → 23:26:07Z (~48 min).**
Receipt with every operand: [`state/RECEIPT-20260816-p4-standard-stages456.json`](../docs/orchestration/state/RECEIPT-20260816-p4-standard-stages456.json).
Whole stream preserved off purgeable scratch as
[`state/p4-stages456-20260816-run.out`](../docs/orchestration/state/p4-stages456-20260816-run.out)
— **`.out`, not `.log`, and force-added, because `.gitignore:13-15` ignores all three of `*.out`/`*.err`/`*.log`.** My first commit of this entry claimed the log was committed and it was not: `git add` reported the path ignored and the commit proceeded without it, so the receipt cited an artifact git never carried. **That is exactly `e7aea2c`'s trap — *"Recover 9 receipt-cited `.out` artifacts git never carried"* — and `KNOWN_ISSUES 48`, which records that `verify_receipt_artifacts.py` cannot see `.out`/`.err`/`.log` evidence and so reads green on precisely this case.** Corrected in the following commit; the claim is left visible here rather than silently repaired.

**AUTHORIZATION, and the token was re-derived not relayed.** The dispatch supplied a 64-hex value; a
peer-supplied hex string is exactly the shape of a fabricated token, so it was recomputed here with
`shasum -a 256` over the tracked verdict and matched: `90dc0175…`. The gate then accepted it on the
cluster — `TOKEN-OK … verdict=PASS, code_rev=a8f7b2f, scope=UNION of the standard-P4 EXECUTION surface
(20 tracked paths)` — with the zeros control returning `TOKEN-REJECT`.

**THE PRECONDITION THAT MATTERED, and it is the reason this entry exists rather than a post-mortem.**
`p4_build_components.py:177` opens `--out` with `RECREATE`, and the live `std_final5_candidate.root`
was the **audited object** of `20260810T0600Z-product-audit-5d-verdict.json` with its digest bound in
two manifests. The GO rested on a preserved-snapshot argument that covered the **three stage-3 evidence
JSONs** and not the candidate: measured, that snapshot was **51 files / 742 KiB**, which cannot hold a
39.4 GiB file, and a covering search of all of scratch found the candidate in exactly one place. The run
was **held** until the five artifacts were preserved, and then verification of the backup was made a
**fail-closed precondition inside the runner** — it recomputes the preserved copy's `sha256` and
compares it to the **audited** digest `602bbcf2…` before the chain may start.

**IT MATTERED IN FACT, NOT ONLY IN PRINCIPLE: the rebuilt candidate is NOT byte-identical to the Aug-9
product** — `950f8cb1…` vs `602bbcf2…`, `42,326,607,877 B` vs `42,326,583,908 B`. Without the copy the
audited object would be gone.

**STAGES 1-3 NO-OP, 20 of 20 as predicted read-only before the run.** Rather than run
`STOP_AFTER=audit` — which **exits at `:67` before stage 2 and is therefore silent about stage-2 resume
by construction** — the launcher's own SKIP predicates were reproduced standalone and read-only, with
two rejection controls firing in the same run (wrong `--tag`; foreign `--merged`). Predicted 10/10 and
10/10; observed `[merge] SKIP` ×10 and `[unfold] SKIP … (receipt validated)` ×10, **0 endpoints
re-unfolded**. Stage 3 wrote as expected (`EVIDENCE-COMPLETE: all required fields proven`), footing
`purity` on all ten.

**PRODUCTS (CANDIDATE ONLY).**

| stage | result |
|---|---|
| 4 components | `sqrt_tr_syst=4.3513e-38`, `sqrt_tr_full=4.3576e-38`, `bands=45`, `retained=40`, candidate `950f8cb1…` |
| 5 validate | **`RESULT PASS`**, 11 gates, `support_ratio=1.000` — **including `band_set_completeness_vs_support_family`**, the gate `OI-128` made `p4_adopt_standard.py` require; this is the first receipt to carry it under the repaired code |
| 6 project | `n=4825` of 4830 reported 4D bins (5 unreachable: `9679, 9686, 9714, 9721, 10169`), `projection_identity=3.76e-16` |

**R11-1 EXECUTION WITNESS — PASS, and deliberately not "the run was green".** repair-11's one
outstanding defect is that the wiring test is *text-level*, so a commented-out call satisfies it; a
passing run says nothing about whether the check ran. The witness is a value the check **computes**:
`projection_M_recipe_check` is present in the produced receipt with `nnz=10694`,
`entries_differing=0`, route *"unravel_index/ravel_multi_index/searchsorted (independent of
build_projection_M)"*. **Independently recounted rather than read back:** `M` is the width-weighted
marginalization 5D→4D, so every reported 5D bin contributes to exactly one 4D bin, hence `nnz` must
equal `mask5d_nreported` — **10694 == 10694**, with `M_shape == [4825, 10694] == [neffective,
nreported]` and `4825 == 4830 − 5`. Note `projection_identity_gates_M: false`, which is the honest
`BEN-316` record: the identity leg does **not** gate `M`, and the recipe check is what does.

**A CROSS-CHECK A READER SHOULD SEE, surfaced because a receipt that omitted it would let a green chain
read as agreement.** Marginal vs INDEPENDENT 4D route, explicitly no pass/fail in the code:
`n=4825 median=0.0443 p90=0.2083 max=0.7285 over3%=3009 integral_ratio=1.005578`. **3009 of 4825 bins
differ by >3%, max 72.9%, while the integrals agree to 0.56%.** This bears on marginalization-vs-direct,
**not** on the projection identity (`3.76e-16`), and it is a measurement rather than a gate.

**WHAT THIS DOES NOT ESTABLISH.** Not the real-product `C4 = M C5 Mᵀ` identity — outside this verdict,
and a green stage 6 is not it. Not adoption or promotion; **construction is not adoption** and the five
Gate-6 prohibitions at `19585b7` stay live. Not `self_guards_adequate`, which repair-11 records as `NO`.
Not a repair of R11-1's test, which is still text-level — this supplies a run-time witness only.

**Environment, per `BEN-347` filed the same day:** `setup_salloc_env.sh` → `root_6_28`, **Python
3.11.14 / ROOT 6.28/12**, *not* the tensorflow module, under which `import ROOT` raises
`ModuleNotFoundError` and silently turned a read-only probe into a false `10/10 WOULD-RERUN`.
Dispatched with `./alloc_run.sh` per `AGENTS.md` (orchestrator inside the allocation; no external
`srun --jobid=`); allocation left up per the leave-it-running rule. Runner and all three probes are
committed under `docs/orchestration/state/` because scratch is purgeable.

## 2026-08-16 — `hRowIndex4D` READ OUT OF THE OBJECT: the Aug-10 audit's own `gaps_remaining[0]` closed, after the identity run it superseded was cancelled as redundant (lane B)

**`VERDICT: PASS`, 0 failures, mutation control fired.** Predeclared at `319f1e4` **before** execution:
[`PREDECLARATION-20260816-hrowindex4d-readback.md`](../docs/orchestration/PREDECLARATION-20260816-hrowindex4d-readback.md).
Receipt: [`RECEIPT-20260816-hrowindex4d-readback.json`](../docs/orchestration/state/RECEIPT-20260816-hrowindex4d-readback.json).
Log force-added (`KNOWN_ISSUES 48`): [`hrowindex4d-readback-20260816.out`](../docs/orchestration/state/hrowindex4d-readback-20260816.out).

**WHY THIS RAN AND THE CONSENSUS RUN DID NOT.** Joseph authorized the real-product `C4 = M C5 Mᵀ`
identity *"if there's consensus"*; both lanes confirmed; **I then reversed my own confirm to DENY.** My
justification — *"nothing, anywhere, reads the persisted 4D product back"* — was **false**, taken from a
`grep` over two globs. An unrestricted `git grep` finds
`runs/standard-p4-verifier/20260810T0630Z-cross-object-script.py`: *"Read-only, independent
cross-object audit: `C4_stored ?= M C5 M^T`. **No pipeline modules are imported. M is reconstructed
solely from hard-coded analysis edges** … Writes: none."* Its verdict already records
`identity_verdict = ESTABLISHED`, independent `M` content hash `2f042f76…` equal to the pipeline's,
19/19 block census, 17 element probes at disagreement `0`, rank `263 = 263 = 263`. **The check we had
authorized already existed and did not share `M` with the producer — the exact limit lane A asked to be
attacked was already absent from it.**

**And it could not have come out differently:** replicating that script's own content-hash convention,
the rebuilt `C5` total hashes **`f26b3bfe…`** and the stored `C4` **`c1fe11b1…`** — **both bit-identical
to the audited objects.** Which also explains a coincidence noticed before it was understood: stage 6's
`projection_identity_relerr = 3.7568690548899724e-16` equals the Aug-10 figure to all 17 digits
**because both are computed over the same bytes.**

**WHAT WAS ACTUALLY OPEN** is `gaps_remaining[0]` of that verdict — *"Exact covariance-row to physical-bin
labels remain unaudited. A verified `hRowIndex4D` of length 4825 matching the independently derived
effective4 index vector"*. `hRowIndex4D` was written **that same day** in response to it
(`p4_project_4d.py:186`) and **nothing verified it for six days**, because `:226-227` hashes
`np.nonzero(m4_eff)[0]` — the *same in-memory array* used to write the histogram three lines earlier.
**It hashes the intent, not the artifact.** Receipt-side fix is `OI-129`'s (lane A).

**RESULTS.** Derived from the grid **shape** and the two central supports only — **no `p4_lib`, no
`build_projection_M`, no `AXIS_EDGES` values, no bin widths**, so this leg is not exposed to the
edge-array question at all:

| check | result |
|---|---|
| `G1` read-back == independent derivation | **PASS** — all `4825` row labels agree exactly |
| `G2` length asserted | `4825` bins == `4825` == covariance dimension `4825×4825` |
| `G3` read-back digest vs recorded | both `de966d2a…` — now two digests of **different objects** |
| `G4` unreachable set | derived `[9679, 9686, 9714, 9721, 10169]` == recorded |
| `G5` well-formed | integral, strictly increasing, `[0, 10975] < 10976` |
| `G6` read-only **proven** | `f042e746…` before **and** after |
| `G7` mutation control | row 100 `153 → 154`; equality **and** digest comparisons both fired |

Independent counts reproduce the Aug-10 audit: `m5 = 10694`, `m4 = 4830`, `effective4 = 4825`,
`unreachable = 5`.

**UNPREDECLARED EXTENSION, labelled as a measurement and not a gate result:** the rebuilt 5D candidate
carries **`hRowIndex5D`**, which the Aug-10 audits never saw and nothing had verified. Same instrument:
`10694` bins == covariance dimension == `nonzero(m5)`, integral, strictly increasing, `[0, 65855]`,
mutation control fires. **Weaker than the 4D leg and the receipt says so** — no before/after digest of
the 39.4 GiB file was taken, so it does not *prove* read-onlyness the way the 4D check does.

**PROVENANCE CONSEQUENCE, and it supersedes a code comment.** The rebuilt 5D candidate has **49 keys vs
the audited 47**, the new one being `hRowIndex5D` — which accounts for the 23,969-byte growth at
**unchanged covariance content**. `p4_build_components.py:213-220` states the already-audited 42.3 GB
artifact is *"deliberately NOT rewritten"* because `602bbcf2…` is the digest the 4D, 5D and cross-object
audits all verified. **The authorized stages-4-6 run did rewrite it**, so that premise no longer holds:
the three audits' **scientific** conclusions transfer (content is bit-identical), while their
**whole-file digest bindings** are stale and need re-pointing at `950f8cb1…`. **Not a defect** — the
rewrite added the row-index array those same audits asked for.

**Covering search stated in the receipt**, because the withdrawn proposal is what taught the lesson:
unrestricted `git grep` on `hRowIndex4D`, `std_proj4d_candidate`, `hCov_std_proj4d`, `proj4d_candidate`;
the only `hRowIndex4D` hits are the writer, a comment, an inventory entry, and the verdict that names it
as a remaining gap. **Bounded conclusion: nothing verified it between 2026-08-10 and this run.**

Read-only throughout; write set is this receipt, the log and three probes. `W_AXIS = 4` remains unpinned
at `p4_project_4d.py:27` — raised with lane C for repair-12 or a follow-on, not edited here.

## 2026-08-16 — CORRECTION: the `hRowIndex4D` receipt named an allocation that had already timed out, and `alloc_run.sh` working correctly is what hid it (lane B)

**`BEN-027` inside a receipt.** `RECEIPT-20260816-hrowindex4d-readback.json` recorded
`slurm: 57128458` — asserted from memory of an earlier dispatch rather than from a command run in the
same turn. Measured now: **`57128458` TIMED OUT at `2026-08-16T18:37:31` PDT after `03:00:03`, about
1h44m before that check ran.**

**The right one, derived from step records rather than reasoning:**

```
sacct -j 57142574   .0  20:04:56-20:05:25  29s   the C4/C5 content-identity probe
                    .1  20:16:40-20:16:52  12s   THE hRowIndex4D READBACK
                    .2  20:17:43-20:17:52   9s   the 5D key listing
                    .3  20:18:40-20:18:54  14s   the hRowIndex5D extension
```

Four dispatches, four steps, in the order issued. Cross-check: `337399f` landed `23:21:19 -0400` =
`20:21` PDT, inside `57142574` (started `20:04:51` PDT). **Every measured value in that receipt is
unaffected — the products were read, not the queue. The defect is attribution, not result.**

**And the stages 4-6 receipt was RIGHT, now verified rather than assumed:** `57128458.1`,
`15:38:09 → 16:26:07`, `00:47:58`, `COMPLETED` — agreeing **to the second** with that run's own log
(`22:38:14Z → 23:26:07Z`). A bonus corroboration falls out: **`57128458.0`, 6 s, `FAILED`** is the first
dispatch that died on `bash: /tmp/p4_runner_laneB.sh: No such file or directory`, so the step record
confirms `BEN-347`'s node-local `/tmp` account independently of the log.

**WHY IT WAS INVISIBLE, which is the transferable part.** `AGENTS.md` documents that `alloc_run.sh`
*"auto-requests a fresh one when the previous 3-hour allocation has expired"* — so **the wrapper behaved
exactly as designed, every dispatch succeeded, and nothing failed to prompt a re-check.** A stale id
survives precisely when the tooling is good: an expired allocation that *broke* the run would have been
caught in seconds.

**Same family as this session's `fetch && rebase && commit` defect and it generalises the same way: bind
a claim to the thing that can be re-derived, and re-derive it in the turn you assert it.** A job id in a
receipt is a measurement, not a label — and so is a job id in a dispatch footer, which is how the same
stale figure reached four lanes as *"held and idle, leave it up"*. **A constraint block is a status
report and goes stale like any other.**

## 2026-08-17 — Joseph's question answered: the stage-6 marginal-vs-direct disagreement is an IDENTITY, not a commutation effect (`BEN-319`)

**Append-only.** Executor lane. **READ-ONLY:** five ROOT reads on the login node under
`setup_salloc_env.sh`, plus local code reads. Nothing written on the cluster, no job submitted or
cancelled, **no run needed or requested**. Receipt:
`docs/orchestration/state/RECEIPT-stage6-marginal-vs-direct-anatomy-20260817.json`.

**Allocation state DERIVED in the turn this was written, not carried (`BEN-303`):** `57128458` **TIMEOUT**,
ended `2026-08-16T18:37:31` after `03:00:03` — that is the dead id the stage-6 run was reported under.
`57142574` **RUNNING** since `2026-08-16T20:04:51`. This analysis used neither; login-node reads only.

**THE ANSWER: neither mathematics nor a defect, as the question was posed.**
`max | rel − (frac_seen − 1) | = 1.187e-14` against `max|rel| = 0.7285`, where `frac_seen[r]` is the summed
**reported** 5D `hUnfoldND` over column `r`'s W bins over the 4D `hUnfoldND`. **The cross-section
conversion cancels exactly: the cross-check IS the per-column content ratio minus one and carries no
information beyond it.** `corr = 1.000`, verified **algebraically** rather than relied on, because a
correlation of 1 can still hide an offset.

**ALL THREE COMMUTATION MECHANISMS REFUTED BY ONE TABLE.** Median `|rel|` by reported-W-count: `nW=1 →
0.0572`, `2 → 0.0519`, `3 → 0.0363`, `4 → 0.0215`, `5 → 0.0190`, `6 → 0.0264`. **At `nW=1` the row of `M`
has one entry — the "marginalization" is multiplication by a single width and none occurs — and those bins
disagree the MOST.** A commutation effect must **vanish** where there is nothing to marginalize; this one
is maximal there. **The wrong sign of dependence, which no coupling strength repairs.**

**WHAT IT IS:** a typical 4D column reports **2 of its 6** W bins (median coverage `0.333`, fully covered
`3.56%`). On the commensurable subset — `frac_seen` within 1% of 1, `n=702` of `4825` — the two products
agree to **`0.45%` median, max `0.999%`**. The `4.4%` is inherited one-for-one from two reported supports
being different subsets of one spectrum.

**PROJECTOR EXONERATED INDEPENDENTLY:** `M @ x5` against the 5D producer's own `hXSecND_dropLast_flat` —
which no projecting-lane code touches — agrees at `max rel 3.107e-16`, median exactly `0`.
`p4_project_4d.py:22-25` already asserted this; it is **confirmed by measurement rather than cited.**

**NOISE STORY EXCLUDED BY DATA, NOT ARGUMENT** (`BEN-025`, realized exceedance): median `|rel|` by
cross-section quartile is **flat** at `[0.0373, 0.0456, 0.0553, 0.0439]`, and the `|rel|>10%` bins are
**3.6× brighter** than typical (`3.852e-41` vs `1.070e-41`). Only the five bins above `50%` are faint.
*"Concentrated in low-occupancy bins"* is plausible and **false**.

**AGAINST THIS LANE, TWICE, in the course of producing it.** (1) The mechanism-2 probe returned exactly
`0.0000` on all 4825 bins — **the signature of an identity, not an agreement** — so it was re-run under
three weightings: unfolded-xsec `1.19e-14`, **UNIFORM** `1.03e-14`, width-only `1.14e-14`. **A quantity
that does not move when you change its own weights is not measuring the weighting** (`BEN-316`'s shape in
this lane's own instrument). **Its real content was kept rather than deleted:** invariance under uniform
weights means completeness has **no W-dependence within a column**, so mechanism 2 via efficiency is
**structurally absent** rather than small — which is a different and stronger statement than "we measured
it and it was tiny." (2) A *"|rel| grows with W-shape concentration"* result was **withdrawn as
corroboration** on noticing its top quartile `[1.00,1.00]` was exactly the `nW=1` bins — `BEN-300` applied
to this lane's own evidence.

**THE DEFECT IS THE LABEL, filed as `BEN-319`.** The printed line and the manifest present
`median / p90 / max / over3%` as **estimator disagreement** when they measure **support mismatch** — and
that framing licensed an entire physics hypothesis space. **It fails by being INVESTIGATED rather than
loudly.** Fix: report `frac_seen` alongside, or quote only the commensurable subset. **NOT PATCHED** —
repair-12 was under this lane's verification when this was found, and the lane that verifies a gate should
not also edit the module under it.

**CONVENTION INTACT AND STRENGTHENED.** Bin-by-bin equality was never coherent between products on
different supports, so retiring the `3%` gate (2026-08-09) was right. **One wording correction:** the
docstring says the comparison *"characterises the independent unfold"* — it does **not**. It characterises
**the support difference between the two products**, a third thing belonging to neither estimator.

**STILL OPEN, and not to be read as closed:** `frac_seen > 1.01` in **1876 of 4825 columns (39%)** — the
summed **reported** 5D content **exceeds** the 4D content, which *"the 5D reports a subset"* cannot
explain. **The well-posed question survives — why do the two unfolds distribute content differently across
columns given different supports — and that is where mechanisms (1) and (3) could legitimately live.**
Carried to Joseph as a proposal; no run designed and none requested. It is smaller and better posed than
the question this lane was handed, **and saying so is not a claim to have answered it.**

*Long form:* `docs/orchestration/FINDING-20260817-a-crosscheck-that-measures-a-different-thing-than-its-name.md`.

## 2026-08-17 — repair-12 VERIFIED: PASS on C1-C5 by a lane that authored none of it, and the token is minted as a RECORD with no run pending

**Append-only.** Executor lane acting as `standard-p4-verifier` for repair-12 only. **No surface file
edited, `P4_VERIFIER_PASS` never set by hand, nothing launched, `57142574` untouched, and the minting
verifier has not consumed the token and will not.** Verdict:
`docs/orchestration/runs/standard-p4-verifier/20260817T045149Z-repair12-verdict.json`.

**WHY THIS LANE.** Lane C wrote the bar as the verifier lane and then **refused to judge its own
implementation** — `89c6e12`'s rule one layer down. That refusal is recorded as correct behaviour and is
why this verdict exists. This lane authored no part of repair-12 and holds no prior token.

**THE ANNOUNCEMENT AND THE ARMING WERE SEPARATED DELIBERATELY.** The sha256 of a verdict **is** the token,
so writing it mints an authorization. This lane reported `PASS` first and minted only on the mediator's
word — not hedging the verdict, refusing to let concluding and arming be one act.

**NO RUN IS PENDING AGAINST THIS AUTHORIZATION, and it is stated first in the verdict** because an
authorization with no requester is the kind of standing capability someone later consumes assuming it was
minted for them. Measured this turn, not carried: `squeue` shows only `56585597` (waker cron) and
`57142574` (`claude-hold`) — **no P4 job queued or running**; `sacct -j 57128458` shows step **`.1`
COMPLETED `0:0` in `00:47:58`**, which is the stages 4-6 execution under repair-11, and step `.0` FAILED
`127:0` in 6s (command not found), which is **not** it. **The covariance already exists; construction is
still not adoption.**

**C1 PASS** — `require_verifier_token()` is the FIRST statement in each stage's `main()`
(`p4_build_components.py:82`, `p4_validate_active_lateral.py:56`, `p4_project_4d.py:54`) and calls
`resolve()`, the wrapper's own function. Verified by execution: a 64-hex non-matching token and a
passphrase are both refused **by the digest machinery** with `sha256` in the message and **not** the
unset-message, which is what distinguishes resolving from an emptiness check.

**C2 PASS** — the gated set is read out of `run_p4_standard.sh` and **printed at run time**:
`['p4_build_components.py', 'p4_validate_active_lateral.py', 'p4_project_4d.py']`. 9/9, including
`test_MUTATION_an_added_stage_script_enters_the_set` — **the case a hand-written tuple cannot pass**, which
is what the predeclaration demanded — and a gateless wrapper deriving `[]` rather than concluding "nothing
needs gating".

**C3 PASS, AND THE WRONG-REASON HAZARD WAS MEASURED ON A REAL PRE-REPAIR CHECKOUT** rather than taken from
the implementer's report. A throwaway worktree at `63a397c^` (removed afterwards): the ungated stage-6
module returns **`rc=2` with argparse `usage:` under ALL THREE token conditions**, no `sha256`, no
`P4_VERIFIER_PASS`. **So a bare `assertNotEqual(rc, 0)` WOULD have passed pre-repair for entirely the wrong
reason.** Each control carries at least one assertion that fails on exactly that output — two of the three
carry two, and `assertNotIn(unset-message)` is the sharpest because it is what proves the gate **resolves**.
**`BEN-344` checked for and not found.** Positive direction: unit-level with `resolve` substituted, which is
the only route available since no token can resolve in this tree by construction — **and the gap that
substitution leaves is closed elsewhere**, at `test_p4_token_gate_scope_and_rev.py:187`, which exercises the
real `resolve` positive path.

**COVERAGE MOVED, NOT DROPPED** — `test_project_rejects_protected_out_path` now asserts **which** gate
refuses (`assertIn("P4_VERIFIER_PASS")`, `assertNotIn("unrecognized arguments")`), and the path guard is
exercised directly in both directions. **No test-mode bypass exists**, checked by grep on the gate module —
one would have re-opened `KNOWN_ISSUES #21` in the module repair-12 exists to close.

**LAZY ROOT PROVEN EXECUTABLY, not read** — all three modules import on a machine with no ROOT and
`ROOT in sys.modules` is `False` afterwards, so `C3` is demonstrable wherever the suite runs.

**C4 PASS, re-earned rather than carried.** repair-11's token confirmed dead **by running the resolver**:
`TOKEN-REJECT … 4 file(s) in its scope have CHANGED at HEAD`, naming exactly the four modules repair-12
touched — **its death is by design and is not recorded as a finding.** 4a: `63a397c…` is a literal sha and
an ancestor of HEAD `773c940…`. 4b: the 20-path surface is byte-identical between them, measured over all
twenty rather than sampled. 4c: no surface file dirty. Targeted suites 9/9 and 81/81. **Neither repair-11's
baseline nor lane C's predeclared `B3` figure is carried.**

**C5 PASS** — `falsified_by` on every condition row, on the outstanding row, and **on the PASS itself**:
*a control that fires on the pre-repair form for a reason other than the gate.* Had any control rested on
nonzero-exit alone, this verdict would be `BLOCK`.

**O2 — THE PUBLISHED BASELINE'S ENVIRONMENT WAS INCOMPLETE, and this is the SECOND instance of the class in
one night.** `TMPDIR` is a third variable and it moves the count: under `/private/tmp` the suite reads
**2 failed / 1479 passed / 1 skipped**; under the default `TMPDIR`,
`test_matching_override_is_hash_bound` fails with `'/tmp/…' != '/private/tmp/…'` — the macOS symlink —
giving **3 failed / 1478 passed**. **Both are correct readings of the same tree.** The first instance was
colour. **Corrected spec: commit sha + colour + `TMPDIR` + platform.** An environment quoted incompletely
is a number that can be neither reproduced nor contradicted. **It does not touch repair-12:** every one of
those failures is a known off-cluster environment failure unrelated to the token gate.

**O1 routed to lane C, not fixed here** — `test_a_passphrase_is_refused_as_not_a_digest` carries **one**
discriminator where its siblings carry two. It has power today, and would go vacuous **silently** if
argparse's message ever mentioned `sha256`. **The lane that verifies a gate should not also edit its tests.**

**Review scope declared at six paths — the four surface modules plus the two test files, because the tests
ARE the evidence** and a PASS that did not bind them could survive deletion of its own proof. The commit's
two documentation files were read and deliberately excluded: a token that dies on a doc edit while claiming
to protect evidence teaches a later reader the wrong thing about what it guards.

## 2026-08-17 — quarantine causes 3 and 4: the shared P leg measured on the adoption candidate (Lane E)

Session E, commissioned by session `personal`. Predeclared at `9c03c67`
(`docs/orchestration/PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md`) **before any stamp was
read**; branch set `S1`–`S5` with every predicted value sourced to a committed file.

**Run.** `nd-unfolding/receipt_candidate_stamps_5d.py` (new; sha256
`1628c76b3008780b7dbe7427c2b390f5119a90bc0a62df02e7c4b9f0be19d2f7`, **verified equal on both sides of the
copy** — the cluster tree is `5fb7e38`, this checkout `00e794e`). Perlmutter `login08`, interactive,
`rc=0`, ~2 minutes, **no batch job and no compute allocation consumed.** Whole stream to
`/pscratch/sd/j/josephrb/lane-e/run.out` and filtered on read (BEN-026); `stderr` is the nine known
duplicate-class `TInterpreter::ReadRootmapFile` warnings. Every ROOT opened `READ`; nothing rebuilt,
nothing modified, nothing adopted, `values.tex` untouched.

**Result: branch `S1`.** Both adoption-candidate arms of job `56720356` carry all six self-checked stamps
**and** all three `upstream_*` values, matching the predeclaration digit for digit:

    A1 stamped_bkgaware_meancentered_20260812.root  4f168e83…  892170881 B  mean-centered
       sqrt_tr_old 4.357790406860002e-38  sqrt_tr_new 5.269625166386846e-38  ratio 1.2092424541784845
    A2 stamped_bkgaware_cvcentered_20260812.root    dbcd5359…  892232198 B  cv-centered
       sqrt_tr_old 4.357790406860002e-38  sqrt_tr_new 5.67431104455928e-38   ratio 1.3021073789200188
    both: upstream_n_throws 160, upstream_joint_mean_shift_norm 1.878696733368378e-38,
          upstream_fixed_seed_null_norm 5.8223488501140625e-50  (tol 1e-12, 37 orders of margin)

The two ratios reproduce `VALIDATION_LEDGER.md:187-190`'s A1 ×1.209 / A2 ×1.302 and are **derived from
operands carried in the same receipt**, per `CONVENTION-receipt-ingredients.md`. Positive control
`STAMPTEST2` reproduced `ben106-stamp-verify-complete-56695424.json` exactly and its sha256
`2465e3e9…` is recorded for the first time. **Negative controls: the two July products the note quotes
came back with all nine propagation stamps ABSENT in the same run** — the reader shown failing in the
direction it acts, and `S5` was declared to dominate `S1` so a leak there would have voided the subjects.

**Receipt:** `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`.

**T legs re-derived rather than inherited** (BEN-344): three mutations in an isolated worktree, each
failing **exactly one** test and leaving the others green — `unified_throw_cov.py:417` mixed-seed
rejection disabled → cause-3 test fails *"SystemExit not raised"*; `:509` `fixed_seed_null_checked`
dropped → cause-4 flag test fails; `:435` scalar jitter subtraction reintroduced → cause-4 AST test fails
*"['st_uni - jitter_floor'] != []"*. Restored, `git diff HEAD` empty, full suite **35/35 pass**.

**NO CAUSE IS DISCHARGED.** The `P` leg moved for causes 3 and 4, for the **candidate only**. Cause 4's
`M` is UNRESOLVED by construction (`CRITERIA` §2: the counterfactual has no surviving specification) and
cause 3's `M` is graded two different ways inside `CRITERIA-20260811` itself. Both are judgements and
**neither was taken.** Full record and the three corrections to the citation chain:
`docs/orchestration/DETERMINATION-20260817-causes-3-4-provenance-measured.md`, `BEN-380`.

## 2026-08-17 — quarantine cause 1: the endpoint census and the magnitude that "does not exist anywhere" (Lane E)

Session E, commissioned by session `personal`. Predeclared at `a2a3a8a` **before any covariance was
reconstructed** (`docs/orchestration/PREDECLARE-20260817-cause1-endpoint-census-and-magnitude.md`),
branch set `C1`–`C5` with **two dominators**. Result: **`C1`**.

**Run.** `nd-unfolding/receipt_cause1_endpoint_census_5d.py` (new; sha256
`0bb03405f7db839a1bd4e26d3bc767c8e9c6c8d62fd6a28f1e947adee5cec704`, verified equal both sides of the
copy). Perlmutter `login08`, interactive, `rc=0`, **no batch job**. Whole stream to
`/pscratch/sd/j/josephrb/lane-e/c1.out`, filtered on read (BEN-026). The reader **imports production's
own `load_flat`, `UNI_RE` and `category_for_band` from `analyze_universes_5d`** rather than
reimplementing them, so a discrepancy cannot be its parsing. Diagonal-only **by sufficiency** — trace and
per-bin σ depend only on the diagonal, so no 10,694² matrix is formed, and **nothing is claimed about
off-diagonal structure.**

**Positive control first (branch `C2` was declared to void the comparison on any failure): all EIGHT
committed numbers in `uq_universe_5d_summary.txt` reproduced** — reported bins `10694/65856`, total syst
√Tr `4.3515e-38` (got `4.351483e-38`), median rel `13.235%` (got `13.23461%`), and all five category
sums. Tolerance `5e-4`, stated with its derivation (half a unit in the summary's last printed figure).

**`P` — census, which did not exist.** 44 bands / 188 files: **42 ± pair bands, every one with both
endpoints; `Flux` exactly 100 at indices `0…99` contiguous.** Non-pairs recorded rather than smoothed:
`2p2h` has **N=3** (declared as an unknown before measuring; excluded from the counterfactual, carried
unchanged in both totals) and one `…_uni_full_CV.root` carries no numeric index so production's `UNI_RE`
skips it. **P leg criterion satisfied, by a committed artifact.**

**`M` — the number `CRITERIA` §2 says "does not exist anywhere". It exists:**

    as-built  (mean-centered, biased 1/N)   sqrtTr 4.351483e-38            median rel 13.2346%
    one-sided CV-centered, endpoint 0       sqrtTr 4.610136e-38  x1.059440 median rel 14.8405%  (+1.61 pp)
    one-sided CV-centered, endpoint 1       sqrtTr 4.487828e-38  x1.031333 median rel 15.7383%  (+2.50 pp)

Both endpoints computed rather than trusting `unified_throw_cov.py:52-53`'s comment — **and they
disagree in opposite senses** (ep0 larger √Tr, ep1 larger median), so **the endpoint choice alone is worth
~2.7% of √Tr.** Per-band trace-ratio distribution over the 40 non-degenerate pair bands (BEN-064,
distribution not a max): ep0 min `0.6377` median `2.0261` p90 `4.3256` max `5.8024`, **35 of 40 above 1**;
ep1 min `0.6111` median `1.6797` p90 `3.9487` max `8.6838`, **34 of 40 above 1**. So *"one-sided
overstates"* holds **in aggregate and not universally**.

**`EtaNCEL` and `NormDISCC` excluded from the distribution** — as-built √Tr `4.187e-45` and `8.043e-51`,
five and eleven orders below the smallest real band, so the `1e-42` cut is a property of the data and not
a tuned threshold. **They are the sharpest demonstration of the defect, in absolute terms: both knobs
have no systematic effect at all, and the one-sided form fabricates `1.279e-39` of variance for each.**

**Mechanism, measured not asserted:** `‖sweep CV unfold − products/5d CV‖ = 1.7054569831625e-39`, a
**0.906% max relative common baseline offset**. Mean-centering cancels it exactly; CV-centering converts
it to a spurious rank-1 term in every band — precisely `CRITERIA` §2's stated defect, now sourced.
**X as built is unaffected**; the offset matters only to the counterfactual. Whether a 0.9% sweep-vs-CV
offset is itself worth investigating is a separate question, flagged for the owning lane.

**`C` and `T` re-derived.** `CRITERIA` §3 grades `C` MET citing **`(§4.8)`, which does not exist** — §4
runs 4.1–4.7. The audit is real and is executable (`Cause1PathAuditTests`), so this is a **citation**
defect. Four mutations, restored and `git diff HEAD` empty after each: **M1** drop mean-centering at
`analyze_universes_5d.py:97` → audit test fails; **M2** rename `uq_math.mat_covariance` → two tests fail,
one with *"has disappeared"*, i.e. fails rather than skipping; **M3** `import pet_systematics_5d` →
pet-reachability test fails; **M4** *one comment line, no semantic change* → the outer-product guard
fails on **line drift alone**. Full suite **35/35** restored.

**Four METs on the letter of §0 — and NOT declared.** Session B reached this position on cause 2 and
routed; the reasoning does not weaken because the lane changed. The single question a decider must answer
is stated in `DETERMINATION-20260817-cause1-census-and-magnitude-measured.md` §6. New defect filed as
`BEN-381` (the `file:line` allow-list) and **deliberately not fixed** — a lane must not both grade a leg
and modify the instrument that grades it.
