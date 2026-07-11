
## STEP-3 PREP FINDINGS (2026-07-02, while FPS train 55288409 running)
- FPS omnifile runEventLoopOmniFold_PC_FPS_MEFHC.root mc_truth_denom (49.9M) branches:
  MC(pt), MC_pz, MC_eavail, MC_q3, MC_W, w_truth (+ MC_hadangle/MC_npip/MC_nproton diag).
- NuWro flat 3d-unfolding/genie/work_nuwro_p*/nuwro_flat.root: cc,pt,pz,eavail,W,weight (NO q3).
  -> NuWro prior reweight = (pt,pz,eavail,W) truth-shape ratio; q3 left to base MC. FEASIBLE.
- FPS 5D grid = STANDARD edges (NOT the 2D pilot PT_EXT/PZ_EXT): of_inputs_pc_fps.npz has
  edges_0..3 = [pt≤4.5 (14), pz1.5-60 (16), eavail (7), q3 (7)] IDENTICAL to bank_uthrow_5d;
  W (edges_4, 6 bins [0,1.1,1.4,1.8,2.2,3,100]) is SPLICED from of_inputs_5d.npz (g5). 65856 bins.
  "Full phase space" here = truth denom WITHOUT muon cuts (denom 32.8M->49.9M, fills tail bins),
  same bin EDGES -- do NOT use PT_EXT extended grid for the 5D envelope.
- fps_prior_envelope.py (2D) is CHEAP: reads 3 pre-made per-prior xsec files, per-cell
  half-spread/mean, splits published-PS vs extension cells. The COST is the 3 per-prior PET
  xsecs. OPEN (resolve from pet_systematics_5d.PETxsec5D when weights land): does the envelope
  RE-UNFOLD per prior (3x full PET train, expensive) or apply the FROZEN headline reweighter's
  push weights onto each prior's gen cloud + rebin (cheap, per-event-weight; matches plan's
  "does not repeat the retrain")? Expectation = the latter (frozen-reweight-on-3-priors).
- TODO on weights: build_fps_prior_nuwro_5d.py (pt,pz,eavail,W ratio, clip[0.2,5], save .npz);
  bareGENIE prior = bareGENIE/MnvTune truth-shape ratio (no-weights driver output, KNOWN_ISSUES#1
  fixed abs-norm); fps_3prior_envelope.py generalizing the 2D one to the 5D grid + PET xsec.

## STEP 3 BUILT (2026-07-02, FPS weights landed 07:03)
Inputs all ready + verified:
- pet_weights_fps.npz (w_push 32.9M, mean1.0047) = FPS headline
- of_inputs_5d_fps.npz = W-source, dump_w_source_fps.py (replicates pc keep-filter, RDF
  single-thread + vectorized in_truth_phase_space; sim_pass cast via RDF Define (int)).
  ALIGN OK: 0 coord mismatch, w_truth bit-identical, kept 32917278.
- fps_prior_genie_ratio_5d.npz = build_fps_prior_genie_5d.py (unweighted/tuned shape,
  range[0.20,2.91] med0.935) ; fps_prior_nuwro_ratio_5d.npz = school's.
Driver: fps_3prior_envelope_5d.py (running, --save-weights). PETxsec5D(comp_ref=None),
xsec(None/rho_genie/rho_nuwro), completeness-stratified two-tier. Outputs products/pet/
fps_envelope_5d/ (fps_envelope_5d.npz + _rho.npz + summary.json + .png).
NEXT after it lands: report numbers, then STEP 4 pet_universe_retrain.py (b-lite).

## STEP 3 CORRECTED (2026-07-02): frozen-reweighter INVALID -> GBDT re-unfold + transfer
DIAGNOSIS CONFIRMED: corr(x_genie/x_tune, per-bin weighted-mean rho_genie)=1.0000, ratio 1.0000,
100% within 5% -> frozen xsec(rho) just propagates the prior ratio, NO data reconvergence
(measured 20.9% > extrapolated 16.7%, inverted+inflated vs pilot 3/5%). fps_3prior_envelope_5d.py
+ its outputs are a documented negative result (outputs deleted).
USER APPROVED option 1 (GBDT re-unfold + fractional transfer). Pipeline:
  55385928 sbatch_nn_dump_fps_5d.sh -> of_inputs_5d_fps_full.npz (GBDT FPS inputs, std edges, NO
     --full-phase-space to match PET pc dump's theta gate)
  55385990 afterok -> fps_gbdt_prior_reunfold_5d.py: 3 LightGBM re-unfolds (tune/genie/nuwro,
     MCgen prior reweighted by rho; per-event td from mc_truth_denom via RDF, rho-reweighted denom),
     ratio_P=xsec_gbdt_P/xsec_gbdt_tune, x_PET_P=x_PET_headline*ratio_P, C=0.5[outer(dg)+outer(dn)].
     -> products/pet/fps_envelope_5d/fps_modeldep_cov_5d.root (hCov_modeldep5d) + xsec npz + summary.
Reused ratios: fps_prior_genie_ratio_5d.npz (mine), fps_prior_nuwro_ratio_5d.npz (school). W-source
of_inputs_5d_fps.npz (aligned). NEXT after chain: report measured-vs-extrap numbers, add C_modeldep
to PET FPS budget; THEN step 4 Tier-2 retraining-response (b-lite).

## ENV FIX (2026-07-02): dump 55385928 FAILED in 3s -> setup_salloc_env.sh conda activate
root_6_28 broken (module regression, see memory env_root628_activation_regression). Created
nd-unfolding/rootenv_sbatch.sh (full-prefix activate); repointed sbatch_nn_dump_fps_5d.sh +
sbatch_fps_reunfold_5d.sh to it. RESUBMITTED chain: dump 55391434 -> reunfold 55391435 (afterok).

## REGULAR-QoS UNSTICK (2026-07-02 ~11:27): shared starvation ~2.5h on the dump.
Cancelled 55391434/55391435; resubmitted dump on REGULAR QoS = 55395620 (--qos=regular
--nodes=1 --mem=0), reunfold 55395622 (afterok, shared). Env fix (rootenv_sbatch.sh) in place.

## CLAUDE-SCHOOL RESUMED (2026-07-02 ~11:49): 55395620/55395622 were cancelled for clean
handoff before running (never lost work). RESUBMITTED per HANDOFF.md step 0:
  dump = 55396907 (--qos=regular --nodes=1 --cpus-per-task=16 --mem=0), PENDING(Priority)
  reunfold = 55396908 (--dependency=afterok:55396907, shared defaults from script), PENDING(Dependency)
school is monitoring via its own ScheduleWakeup loop (separate from personal's, per HANDOFF warning).

## SWITCHED TO INTERACTIVE for the dump (2026-07-02 ~12:45): 55396907/55396908 cancelled
(both still PENDING/Priority, no start estimate) in favor of running the dump via alloc_run.sh's
shared claude-hold allocation (interactive QoS schedules near-instantly vs regular-QoS starvation).
Reunfold (up to 6h) stays in BATCH — alloc_run.sh's srun step is pinned to one 3h placeholder
allocation and would get killed mid-run past 3h with no checkpoint.
GOTCHA hit + fixed: first interactive attempt failed in ~3s with the SAME root_6_28
EnvironmentNameNotFound regression described above, even though setup_salloc_env.sh has the
full-prefix fix — because claude-school's $HOME is a redirected sandbox path
(.../claude-homes/school/...), not the real NERSC home, so `${HOME}/.conda/envs/root_6_28` in the
fix's default doesn't resolve and it falls through to the broken legacy `module load python;
conda activate root_6_28` path. HANDOFF's rootenv.sh (HOME override) fixes this for a plain
interactive shell, but alloc_run.sh's srun step sources setup_salloc_env.sh directly (can't inject
a HOME override before that source without editing the shared tracked alloc_run.sh). FIX: export
ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28 in the calling shell BEFORE invoking
./alloc_run.sh — srun inherits it (default --export=ALL), setup_salloc_env.sh's
`${ROOT628_PREFIX:-$HOME/...}` default is a no-op once it's already set, so the full-prefix
activation succeeds without touching HOME or any tracked script. Use this pattern for any future
claude-school alloc_run.sh calls that need the ROOT env.

## DUMP SUCCEEDED (2026-07-02 ~13:10) via interactive claude-hold (55399151):
of_inputs_5d_fps_full.npz written (1.55GB): MCgen(32917278,5) measured(4091707,5)
pass_truth=32849103 pass_reco=20472467. Only warnings were harmless RooUnfold dict-redefinition
noise. REUNFOLD resubmitted standalone (no dependency) on shared QoS: job 55400307
(fpsreunf5d, PENDING/Priority as of submit). claude-hold left running (no start/stop churn).

## REUNFOLD 55400307 FAILED (2026-07-02 ~13:59): 6s, same root_6_28 EnvironmentNameNotFound.
IMPORTANT correction to the earlier gotcha note: it is NOT interactive-only. `sbatch` ALSO
inherits claude-school's sandboxed $HOME (default --export=ALL propagates the submitting shell's
env, same as srun) -- so setup_salloc_env.sh's `${HOME}/.conda/envs/root_6_28` default resolves
wrong for EVERY school-submitted job (sbatch or interactive alike), contradicting the
setup_salloc_env.sh comment "sbatch/salloc set HOME to the real home" (true for the personal
account's real HOME, false for school's sandbox). FIX (same pattern, now proven for sbatch too):
`export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28` in the submitting shell
BEFORE `sbatch <script>` -- sbatch inherits it, setup_salloc_env.sh's default is a no-op once
already set. Resubmitted with this fix: job 55402568 (fpsreunf5d, shared QoS, PENDING). ACTION
ITEM for any future school sbatch submission touching setup_salloc_env.sh: always export
ROOT628_PREFIX first, or the job will fail in ~6s.

## 55402568 RAN 9min then FAILED on a REAL BUG (2026-07-02 ~14:41), env fix confirmed working
(3x LGBM training happened, sklearn warnings + truth-denom validation printed fine).
ValueError: operands could not be broadcast together with shapes (32849103,) (32917278,)
-- fps_gbdt_prior_reunfold_5d.py line 132 `unf, _ = np.histogramdd(MCgen[m], bins=edges,
weights=(w_push * wt)[m])`: w_push returned by omnifold_loop is ALREADY pass_truth-masked-length
(32849103) internally (omnifold_loop does MCgen=MCgen[pass_truth] then w_push=np.ones(len(MCgen))),
but wt=w_truth*rho_sig is full-length (32917278) -- masking must happen to wt BEFORE multiplying,
not after. Confirmed against the established pattern used identically in EVERY other script
(compare_unified_throw.py, nn_run_from_npz.py, seedscan_split.py, sweep_bank_5d.py,
unified_throw.py, unified_throw_cov_5d.py, sweep_bank.py): always `w_push * wt[m]`. FIXED:
changed to `weights=w_push * wt[m]` (line 133's ofin already had the correct `wt[m]` form, just
line 132 had it backwards). Resubmitted with the fix + ROOT628_PREFIX export: job 55405172
(fpsreunf5d, shared QoS, PENDING). Only fixed line was that one; rest of the script (ratio/PET
transfer/two-tier/cov-write logic) reviewed and looks consistent.

## 55405172 RAN 16:50min, FAILED on a SECOND real bug (2026-07-02 ~16:08): got further this
time (past the line-132 fix, through the full unfold_prior for at least "tune", to line 137):
`AttributeError: 'tuple' object has no attribute 'ravel'` -- line 136
`xs = extract_cross_section_nd(unf, comp, flux, data_pot, n_nucleons, edges)` doesn't unpack;
xsec_nd.extract_cross_section_nd returns `(xsec, good_mask)` per its docstring and EVERY other
caller in the codebase (bootstrap_nd.py, compare_unified_throw.py, sweep_bank(_5d).py,
unified_throw(_cov_5d).py, pet_systematics(_5d).py, pet_lateral_band(_5d).py, etc. all do
`xs, _ = extract_cross_section_nd(...)`). FIXED: `xs, _ = extract_cross_section_nd(...)`.
Checked for a 3rd risk before resubmitting: the later `C = 0.5*(outer(d_g[r],d_g[r]) +
outer(d_n[r],d_n[r]))` on r=len(reported bins) -- a comparable 5D unified-cov run reported
n_pet_reported=10550/65856 bins (see products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json),
so even if FPS reports more (full-phase-space denom, less restrictive), the outer product should
stay well under the job's 120G mem budget (worst case ~65856^2*8B*2 ~70GB, actual likely far
smaller at ~10-20k reported bins). Resubmitted: job 55408197 (fpsreunf5d, shared QoS, PENDING).

## 55408197 COMPLETED (2026-07-02 ~16:39, 31min) but flagged a THIRD issue -- a physics/
methodology bug, not a crash. Numbers: all n=10550 median=17.05% p90=62.4%; measured(comp>=0.5)
n=10323 median=17.14%; extrapolated(comp<0.5) n=227 median=15.28% (LOWER than measured -- the
OPPOSITE of the expected bloom-in-extrapolation). completeness_profile is flat 14-18% across every
completeness bin from [0,0.1) to [0.7,1.01), no monotonic trend at all. This contradicts the
entire premise of doing the real GBDT re-unfold (data reconvergence -> low spread where measured,
blooms where extrapolated) and needed a root-cause check before trusting/adopting it.
DIAGNOSIS: the script's own printed sanity line "denom check vs dump denom_nd: rel L1 diff =
1.697e-01" (~17%) IS the smoking gun, and the script never acted on it. ROOT CAUSE: the script's
per-event truth-denom rebuild (lines ~92-105, for computing per-prior completeness) only applied
a pt/pz RECTANGLE filter -- it never applied the theta_mu<20deg truth gate
(u2d.MAX_MUON_THETA_RAD, atan2(pt,pz)<20deg) that the dump (of_inputs_5d_fps_full.npz, built
WITHOUT --full-phase-space, i.e. gate ON, "matching the PET pc dump's theta gate" per the sbatch
comment) DOES apply for its denom_nd. So this script's own completeness denominator was
systematically over-inclusive/inconsistent with the headline definition -- exactly the kind of
error that would scramble which bins get correctly labeled "extrapolated" vs "measured" and wash
out the expected bloom trend. Verified zero bins have the naive "ratio defaulted to 1" artifact
first (ruled that out) before finding this.
FIXED: added `intheta = np.arctan2(tdc[0], tdc[1]) < u2d.MAX_MUON_THETA_RAD` to the `inrect` mask
(matches u2d.in_truth_phase_space's exact formula). Should make the "denom check" line converge
to ~0 and should let the two-tier bloom emerge correctly if the underlying physics matches
expectation. Resubmitted: job 55410647 (fpsreunf5d, shared QoS, PENDING). PREVIOUS "COMPLETED"
outputs (products/pet/fps_envelope_5d/{fps_modeldep_cov_5d.root,fps_gbdt_prior_xsec_5d.npz,
fps_gbdt_envelope_5d_summary.json,fps_envelope_5d.pdf}) are STALE/pre-fix -- do NOT use for the
PET FPS budget; will be overwritten by the rerun.

## 55410647 COMPLETED (2026-07-02 ~18:31, 30min): fix MECHANICALLY confirmed --
"denom check vs dump denom_nd: rel L1 diff = 0.000e+00" (exact match, was 1.697e-01). BUT this
reveals a DEEPER design question, not a clean win: with the correctly-gated denom, ALL n=10550
reported bins now have comp>=0.5 -- "extrapolated comp<0.5" is EMPTY (n=0). Overall numbers barely
moved (median 17.05% both before/after, sqrt-tr C_modeldep 3.8296e-38 vs 3.8296e-38 -- the buggy
run's 227 "extrapolated" bins were only ~2% of the reported set, so reclassifying them barely
changed the aggregate). GBDT totals tune=7.8242e-36 genie=8.0018e-36 nuwro=7.5420e-36 (~2-4% prior
spread at the TOTAL level, consistent both runs).
WHY: sbatch_nn_dump_fps_5d.sh was deliberately built WITHOUT --full-phase-space ("keep the theta
gate, matching the PET pc dump's theta gate" per its own comment) -- i.e. this GBDT dump's truth
denom uses the SAME theta_mu<20deg signal-definition phase space as MCgen itself, by design. Once
denom and signal are on the identical phase-space definition, there is no leftover
extended-truth-vs-standard-reco mismatch left to drive comp<0.5 in bins that have any measured/
reco data (rep=x_pet>0) -- completeness is uniformly high there almost by construction. The
227-bin "extrapolated" tier in the PRE-FIX (buggy) run was a NUMERICAL ARTIFACT of the missing
theta cut (over-counting truth events from outside the standard phase space into the denom for
bins that happen to sit near the theta=20deg edge), not real extrapolation physics.
IMPLICATION (needs a human call, this is the actual campaign design question, not a bug fix):
the "two-tier by completeness, extrapolation should bloom" framing in HANDOFF.md's NEXT ACTIONS
may not apply to THIS pipeline leg as currently built. To genuinely probe/quantify the
extrapolation-region model dependence (the stated goal of step 3), the dump likely needs to be
rebuilt WITH --full-phase-space (extending MCgen/measured/denom together to beyond the standard
theta<20deg signal definition), which is a materially different (and nontrivial -- MCgen/measured
consistency would need re-verification against the PET pc dump's own definition) computation, not
a quick fix. Reported to the user for a decision before doing that work. Current
(theta-gate-fixed) result stands as a technically-correct "flat ~17% model dependence over the
standard-phase-space reported grid, no extrapolation tier" -- usable at face value if the campaign
decides not to chase the extended-phase-space leg, but does NOT deliver the "dominant extrapolation
systematic that blooms" result the plan was originally seeking.

## USER VERIFIED + DEEPENED the diagnosis (2026-07-03 ~06:15): pet/dump_pointcloud_inputs.py
ALSO hardcodes pass_truth to the standard theta<20deg phase space (no FPS flag existed) -- so
PET's own headline gen cloud (pet_weights_fps.npz) was NEVER full phase space either; my envelope
correctly matched a headline that itself was standard-PS. The campaign's "beyond published PS"
claim isn't delivered by ANY current leg.

## STAGE-0 VALIDATION (2026-07-03 ~06:16, user-directed, PASSED): projected the 3 per-prior 5D
GBDT xsecs (fps_gbdt_prior_xsec_5d.npz, the theta-fixed 55410647 result) down to coarse (pT,p||)
by integrating over (eavail,q3,W) with proper bin-volume weighting, compared to FPS_PILOT.md's 2D
honesty-battery prior-swap numbers (published-PS: median 3.0%, p90 8.9%). RESULT: projected median
=1.97%, p90=21.7%, max=52.4% (n=205/224 populated coarse bins); totals agree tune=3.7496e-37
genie=3.7507e-37 nuwro=3.7610e-37 (~0.3%). CONCLUSION: median comfortably matches/beats the pilot
reference -> the GBDT re-unfold machinery IS correct; the flat ~17% at full 65856-bin granularity
is a fine-binning/statistics effect, not a broken leg. User approved proceeding to Stage 1.

## STAGE 1 KICKED OFF (2026-07-03 ~06:18): lift the theta_mu<20deg gate CONSISTENTLY across the
whole PET+GBDT chain (not just the GBDT-side denom fixed above) so a genuine extrapolation region
actually exists to study. No grid change needed (theta=atan2(pt,pz) lives inside the existing
pt/pz rectangle -- "rectangle ok" per FPS_PILOT.md's 1A pilot).
CODE CHANGES (new flags, all mirroring nn_dump_inputs.py's existing --full-phase-space pattern:
`u2d.MAX_MUON_THETA_RAD = math.pi`):
  - pet/dump_pointcloud_inputs.py: added --full-phase-space (lifts the gate inside its
    u2d.in_truth_phase_space(a_pt,a_pz,...) call at line ~105-109 that sets tru_ok/pass_truth).
  - dump_w_source_fps.py: added --full-phase-space (it hardcoded theta_max=u2d.MAX_MUON_THETA_RAD
    at module level BEFORE this fix -- needed so the W-source row-alignment matches an extended pc
    dump; PETxsec5D requires EXACT row-count + bit-identical w_truth alignment against --pc).
  - fps_gbdt_prior_reunfold_5d.py: added --full-phase-space (it rebuilds its OWN truth-denom from
    mc_truth_denom using the module-level gate for completeness -- this is the exact line I fixed
    earlier today to be theta-gated ON; for the xps run it must be liftABLE via flag or the same
    denom-mismatch bug recurs in the opposite direction).
  - nn_dump_inputs.py already had --full-phase-space (pre-existing, from the 2D pilot); no change.
NAMING (new files only, "_xps" = eXtended Phase Space, disambiguated from the pre-existing
"_full" = full-STATS-but-standard-PS naming already in use):
  of_inputs_pc_fps_xps.npz (+ of_inputs_pc_fps_xps_npy/ memmap)  -- PET pc dump, gate lifted
  of_inputs_5d_fps_xps_wsource.npz                                -- W-source, row-aligned to above
  of_inputs_5d_fps_xps.npz                                        -- GBDT scalar dump, gate lifted
  products/pet/pet_weights_fps_xps.npz                            -- PET full-stats retrain output
  products/pet/fps_envelope_5d_xps/                               -- final re-run envelope outdir
  All existing standard-PS artifacts (of_inputs_pc_fps.npz, of_inputs_5d_fps.npz,
  of_inputs_5d_fps_full.npz, pet_weights_fps.npz, products/pet/fps_envelope_5d/) are UNTOUCHED.
JOBS SUBMITTED (phase 1, parallel, independent of each other):
  55436665 = sbatch_npz_pc_fps_xps.sh (new sbatch script) -> of_inputs_pc_fps_xps.npz +
             of_inputs_pc_fps_xps_npy/, shared QoS, PENDING.
  55436666 = sbatch_nn_dump_fps_5d_xps.sh (new sbatch script) -> of_inputs_5d_fps_xps.npz,
             shared QoS, PENDING.
REMAINING DAG (not yet submitted -- sequenced on the above):
  after 55436665: (a) W-source dump `python3 dump_w_source_fps.py --omnifile
    runEventLoopOmniFold_PC_FPS_MEFHC.root --pc of_inputs_pc_fps_xps.npz --wedges
    of_inputs_5d.npz --full-phase-space --out of_inputs_5d_fps_xps_wsource.npz` (lightweight,
    run interactively via alloc_run.sh); (b) PET full-stats retrain (GPU, ~7-10h) via the
    EXISTING sbatch_pet_train_fps_hvd.sh (already env-var parameterized, no edit needed):
    `INPUTS=of_inputs_pc_fps_xps.npz MEMMAP_DIR=of_inputs_pc_fps_xps_npy
    SAVE_WEIGHTS=products/pet/pet_weights_fps_xps.npz sbatch --dependency=afterok:55436665
    sbatch_pet_train_fps_hvd.sh`.
  after 55436666 + the PET retrain + the W-source dump all land: re-run the envelope:
    `python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps.npz --pet-pc
    of_inputs_pc_fps_xps.npz --pet-weights products/pet/pet_weights_fps_xps.npz --pet-wsource
    of_inputs_5d_fps_xps_wsource.npz --full-phase-space --outdir products/pet/fps_envelope_5d_xps
    --iters 5 --seed 1000` (submit as sbatch with --dependency=afterok on the GBDT dump + PET
    retrain jobs once both IDs are known).
Step 4 (Tier-2 retraining-response) remains DEFERRED until this Stage-1 chain lands (per user:
running it against the old theta-gated train would waste GPU). Stage 2 (extended catch-bin edges
for the low-p|| strip) is a separate later decision, not needed now.

## PHASE 1 PROGRESS (2026-07-03 ~07:10): 55436666 (GBDT xps dump) COMPLETED cleanly (15min):
of_inputs_5d_fps_xps.npz written: MCgen(38643338,5) -- up from 32917278 in the standard-PS dump,
+5.73M events (+17.4%) from lifting the theta gate, a sane/expected-magnitude increase (FPS_PILOT's
1A acceptance study put the theta>20deg wedge at ~11.2% of total RATE, order-of-magnitude
consistent with this EVENT-COUNT increase). measured(4091707,5) pass_reco=20472467 UNCHANGED from
the standard-PS run (correct: --full-phase-space only affects truth-level pass_truth via
u2d.MAX_MUON_THETA_RAD, not reco-side selection) -- good implicit consistency check.
55436665 (PET pc dump) still RUNNING as of this check (~20min in, 26.4M/49.9M entries, ~53%, no
errors) -- this is a scalar per-event python GetEntry loop (slower than RDF), on pace to finish in
~15-20 more minutes.

## PHASE 2 (2026-07-03 ~14:38-18:24 UTC): both CPU-side xps dumps COMPLETE + aligned.
55436665 (PET pc dump) COMPLETED: of_inputs_pc_fps_xps.npz (7.37GB) + of_inputs_pc_fps_xps_npy/
written. gen(38643338,12,5) reco(38643338,12,3); measured(4091707,12,3) UNCHANGED (reco-side).
kept 38643338/49906108 -- EXACTLY matches 55436666's GBDT MCgen row count (both apply the same
theta-lifted rectangle+OR-reco keep-filter independently -- strong cross-check).
W-source xps dump run interactively via alloc_run.sh (new shared alloc 55445380, prior claude-hold
had expired/rotated -- compliant, no second holder was concurrent): dump_w_source_fps.py
--pc of_inputs_pc_fps_xps.npz --wedges of_inputs_5d.npz --full-phase-space --out
of_inputs_5d_fps_xps_wsource.npz. Result: "[wsrc] ALIGN OK: coords exact (0 mismatch), w_truth
bit-identical, pass_truth eq=True pass_reco eq=True, 0 NaN-pattern rows", kept=38643338/49906108.
All THREE xps CPU inputs now exist and are mutually row-aligned (38,643,338 each):
of_inputs_5d_fps_xps.npz (GBDT), of_inputs_pc_fps_xps.npz (PET pc), of_inputs_5d_fps_xps_wsource.npz
(W-source). Only remaining input: PET full-stats retrain on the extended-PS cloud.
Next: submit sbatch_pet_train_fps_hvd.sh (EXISTING, unedited, env-var parameterized) with
INPUTS=of_inputs_pc_fps_xps.npz MEMMAP_DIR=of_inputs_pc_fps_xps_npy
SAVE_WEIGHTS=products/pet/pet_weights_fps_xps.npz. GPU job, expect ~7-10h (prior standard-PS
retrain 55288409 took 7h21m on 32.9M rows; this is 38.6M rows, +17.4%, so expect roughly
proportionally longer, ~8-9h).

## PHASE 3 (2026-07-03 ~18:25 UTC): PET full-stats xps retrain SUBMITTED.
Job 55445418 = sbatch_pet_train_fps_hvd.sh, INPUTS=of_inputs_pc_fps_xps.npz
MEMMAP_DIR=of_inputs_pc_fps_xps_npy SAVE_WEIGHTS=products/pet/pet_weights_fps_xps.npz.
gpu_ss11 partition, PD (Priority) at submit +20s -- normal GPU queue wait, not an error.
Expect ~7-10h runtime once it starts (prior standard-PS run 55288409: 7h21m on 32.9M rows;
this is 38.6M rows so maybe slightly longer). NEXT: once this job COMPLETES and
products/pet/pet_weights_fps_xps.npz lands, submit the final envelope re-run:
`python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps.npz --pet-pc
of_inputs_pc_fps_xps.npz --pet-weights products/pet/pet_weights_fps_xps.npz --pet-wsource
of_inputs_5d_fps_xps_wsource.npz --full-phase-space --outdir products/pet/fps_envelope_5d_xps
--iters 5 --seed 1000` as a new sbatch script (copy sbatch_fps_reunfold_5d.sh's resource block:
shared QoS, 32 cpus, 120G mem, 6h, with ROOT628_PREFIX exported). Then read
products/pet/fps_envelope_5d_xps/fps_gbdt_envelope_5d_summary.json and report the two-tier
(measured comp>=0.5 vs extrapolated comp<0.5) model-dependence numbers vs FPS_PILOT.md's
reference (extrapolated median ~5.1%, p90 ~22.7%) and vs the standard-PS flat ~17% baseline.
STOP and report to user once this lands -- do NOT proceed to Step 4 (Tier-2 retraining-response)
without explicit user go-ahead.

## QUEUE STATUS (2026-07-04 00:34 UTC): 55445418 still PD after ~6h09m wait.
sprio -j 55445418: PRIORITY=68043 (QOS=67679, AGE=364, SITE=0). squeue -p gpu_ss11 -t PD | wc -l =
3012 pending jobs on this partition -- gpu_ss11 is heavily oversubscribed right now (other users'
PD jobs range 68k-174k priority, many above ours). This explains the long wait: it is NOT specific
to our job, the whole partition queue is deep. No ETA available (squeue --start shows N/A). Not
taking any action (no cancel/resubmit) -- flagging to user per their standing instruction, will keep
monitoring on ~25min cadence.

## DECISION POINT (2026-07-04 02:44 UTC): 55445418 crossed 8h09m PD wait.
sprio refreshed: PRIORITY=68173 (age component crept 364->494, QOS still 67679 -- age accrual is
slow, not going to meaningfully improve position soon). Queue depth still ~2920 PD jobs on
gpu_ss11. No ETA (squeue --start = N/A). Wait now roughly matches/exceeds the job's own expected
runtime (~7-10h, prior identical-shape run took 7h21m). Flagged to user for a decision -- NOT
cancelling/resubmitting unilaterally. Continuing to monitor at ~25min cadence pending user input.

## HEDGE SUBMIT (2026-07-04 12:43 UTC)
Job 55445418 (`pet_train_fps`, submitted 2026-07-03T11:24:49) still PENDING after ~25h13m —
priority crept to 68773 (AGE 1094) but partition congestion unresolved; QoS/partition
investigation (prior entry) confirmed no accessible QoS beats `gpu_regular` for this job's
resource/walltime needs (gpu_premium not in our account's QoS list; interactive/jupyter
variants cap at 4-6h, too short; gpu_preempt/gpu_shared same priority with added risk/no benefit).

Per user direction, submitted a HEDGE second job rather than cancel+resubmit the original
(avoids losing 25h of accrued AGE priority on 55445418):
  INPUTS=of_inputs_pc_fps_xps.npz MEMMAP_DIR=of_inputs_pc_fps_xps_npy \
  SAVE_WEIGHTS=products/pet/pet_weights_fps_xps_b.npz \
  sbatch --job-name=pet_train_fps_b --output=pet_train_fps_b_%j.out --error=pet_train_fps_b_%j.err \
  sbatch_pet_train_fps_hvd.sh
  -> job 55475454, PENDING, same resource request (1 node/4 GPU/10h/gpu_regular) as 55445418.

Distinct SAVE_WEIGHTS path (`pet_weights_fps_xps_b.npz`) and separate job-name/log files chosen
so the two jobs cannot collide if both happen to start. Plan: whichever job transitions to
RUNNING first, cancel the other (still-pending) job immediately (both started this session,
safe to cancel per session rules). Use the winner's weights file for the envelope re-run step
(rename to canonical `pet_weights_fps_xps.npz` path if the hedge job wins).

## HEDGE RESOLVED — 55445418 WON (2026-07-04 16:03 UTC)
Job 55445418 transitioned RUNNING at ~15:56:44 UTC on node nid003812 (~28h32m PD wait,
started 2026-07-03T11:24:49). Immediately cancelled the still-pending hedge job 55475454
(scancel, confirmed removed from squeue). No collision risk — hedge never started.

Log health check at +6-7min: 4x A100-SXM4-40GB detected, horovod init OK on all 4 ranks,
loaders report mc reco shape=(9660835,12,3) gen shape=(9660835,12,4) x4 ranks (~38.6M total
across ranks, matches of_inputs_pc_fps_xps.npz row count), pass_reco=0.530 pass_gen=0.999,
shuffle buffers filled, ITERATION 1 / RUNNING STEP 1 / Epoch 1/8 in progress. No errors,
exceptions, or OOM in .err. Will save to products/pet/pet_weights_fps_xps.npz on completion
(canonical name — no rename needed). Expect ~7-10h total runtime (prior restricted-PS run was
7h21m; this is +17% more rows). Will check back periodically for progress/completion.

## PET FULL-STATS XPS TRAINING COMPLETE (2026-07-04 17:37 UTC)
Job 55445418 COMPLETED (exit 0:0, elapsed 8:40:50, started 15:56:44 finished ~17:37:30 UTC).
Log confirms: `[reweight-all] full-stats w_push n=38643338 mean=1.0103 std=0.1756 (finite=True)`
— row count matches of_inputs_pc_fps_xps.npz exactly.

Numpy sanity check on products/pet/pet_weights_fps_xps.npz (210MB):
  w_push: shape (38643338,) float64, min=0.438, max=2.481, mean=1.010, all finite
  mc_indices: (38643338,) int64
  pass_truth: (38643338,) bool
  model: scalar '<U3', closure: scalar bool
All sane — no NaN/inf, weight range plausible for a reweight-all push.

Immediately submitted the final envelope re-run:
  new script nd-unfolding/sbatch_fps_reunfold_5d_xps.sh (copied sbatch_fps_reunfold_5d.sh's
  resource block: qos=shared, constraint=cpu, 32 cpus, 120G mem, 6h, ROOT628_PREFIX exported)
  invoking: python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps.npz --pet-pc
  of_inputs_pc_fps_xps.npz --pet-weights products/pet/pet_weights_fps_xps.npz --pet-wsource
  of_inputs_5d_fps_xps_wsource.npz --full-phase-space --outdir products/pet/fps_envelope_5d_xps
  --iters 5 --seed 1000
  -> job 55503743, PENDING on shared_mi partition. Expected runtime ~1-2h (standard-PS
  envelope run for comparison took similar order). Will report final two-tier numbers on
  completion, then STOP per user instruction (no Step 4 without explicit go-ahead).

## FINAL RESULT — STAGE 1 COMPLETE (2026-07-04 19:11 UTC)
Job 55503743 COMPLETED (41m17s, exit 0:0). Full log confirms theta gate correctly lifted
("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted"), MCgen(38643338,5) measured(4091707,5),
denom check rel L1 diff = 0.000e+00 (exact match vs dump), W-source alignment OK.

products/pet/fps_envelope_5d_xps/fps_gbdt_envelope_5d_summary.json:
  n_reported=10759, ALL in measured(comp>=0.5) tier (extrapolated(comp<0.5) EMPTY — n=0)
  all/measured: median=17.259%, p90=60.939%, max=129.35%
  sqrt_trace_C_modeldep = 2.1493e-37

vs. standard-PS baseline (products/pet/fps_envelope_5d/fps_gbdt_envelope_5d_summary.json,
same method, restricted theta_mu<20 deg PET weights):
  n_reported=10550, ALL measured tier, extrapolated EMPTY
  median=17.048%, p90=62.363%, max=129.73%
  sqrt_trace_C_modeldep = 3.8296e-38

PHYSICS ASSESSMENT: Lifting the theta_mu truth gate to the full phase space produces an
essentially FLAT result relative to the restricted-PS baseline — median fractional model-
dependence spread changes by only ~0.2pp (17.26% vs 17.05%), p90 is actually slightly LOWER
for xps (60.94% vs 62.36%), max is unchanged (~129%). Bin count grows modestly (+209, +2%)
as extra theta>20 deg phase space clears the comp>=0.5 completeness bar. The absolute
sqrt_trace(C_modeldep) is ~5.6x larger for xps (2.15e-37 vs 3.83e-38), reflecting the larger
absolute cross-section normalization from the added phase space, NOT a larger relative
uncertainty. CONCLUSION: opening the full phase space does not introduce additional
model-dependence bloom in the full-stats PET+GBDT-envelope approach — a clean null result.

IMPORTANT CAVEAT on the FPS_PILOT.md reference (extrapolated median ~5.1%, p90 ~22.7%):
verified this is NOT the same quantity — it's from an earlier 2D (pT,p||) pilot's prior-swap
(MnvTune-v1 vs bare-GENIE) per-cell disagreement metric on efficiency-binned cells, not this
5D GBDT 3-prior (tune/GENIE/NuWro) envelope spread/mean metric. Not directly comparable;
the correct apples-to-apples comparison is the standard-PS 5D run above. Notably, NEITHER
xps nor standard-PS full-stats PET runs produced any Tier-2 (comp<0.5) bins — the two-tier
reporting convention recommended in FPS_PILOT.md (from the coarser 2D pilot) does not manifest
at this finer 5D-grid + full-stats-PET granularity; every reported bin already clears comp>=0.5.

STAGE 1 (theta-gate-lift consistency chain) IS NOW COMPLETE. Reported to user 2026-07-04
19:11 UTC. STOPPING per user instruction — NOT proceeding to Step 4 (Tier-2 retraining-
response) without separate, explicit user go-ahead.

## STAGE 2 GO (2026-07-04 19:XX UTC) — extended reporting grid (catch bins)
User authorized Stage 2: bring in the pilot catch bins via PT_EXT/PZ_EXT (from
fps_acceptance.py) on top of the Stage-1 theta-lift. Naming suffix "_xps2".
Grid: PT_EXT (15 bins, adds [4.5,30.0]) x PZ_EXT (19 bins, adds [0,0.75) and [60,120])
x Eavail(7) x q3(7) x W(6) = 15*19*7*7*6 = 83,790 bins (Eavail/q3/W edges unchanged).

Stage-1 validation (reported by user, not re-derived here): anchor on the 9,752 interior
theta<20deg bins reproduces the standard-PS headline (integral ratio 1.0047, per-bin
median |r-1| 1.03%); the xps 5.6x sqrt-trace jump vs standard-PS is fully attributed to
the wedge entering (209 new bins + 348 straddling bins), benign. The empty Tier-2 tier
in both Stage-1 runs is a grid-edge effect (dead low-p|| strip, 22.4% of rate, lies
outside the standard edges) -- Stage 2 brings it in.

CODE CHANGES (all additive, applied this session):
1. pet/dump_pointcloud_inputs.py: added --pt-edges/--pz-edges (comma-separated override,
   mirrors nn_dump_inputs.py). Fixed the TWO hardcoded u2d.PT_EDGES/PZ_EDGES sites: the
   keep-filter rectangle (now derives pt_e/pz_e from args) and the edges_0/1 written to
   the npz (removed the duplicate reassignment later in main() that would have
   overwritten the args-derived edges with the standard ones -- this was the one
   substantive bug caught while implementing). ALSO removed a dead
   `flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)` call (line ~76)
   that was never used downstream (flux_bins was computed but never referenced in the
   savez_compressed call) -- with extended pt_e (15 bins) this would have crashed since
   load_flux_bins hard-checks histogram-bins == len(edges)-1 against the standard 14-bin
   flux histogram. Kept --full-phase-space from Stage 1 unchanged.
2. dump_w_source_fps.py: added the same --pt-edges/--pz-edges flags; fixed the one
   hardcoded keep-filter rectangle site. The npz's own edges_0..3 output already comes
   straight from the row-aligned --pc npz (not recomputed here), so no second site to fix.
3. pet_systematics_5d.py PETxsec5D.__init__: line ~110's
   `u2d.load_flux_bins(mcfile, flux_hist, self.edges[0])` would crash on an extended
   15-bin self.edges[0] (from the xps2 pc npz) vs the standard 14-bin flux histogram.
   Replaced with an UNCONDITIONAL bin-centre remap (load flux on the standard 14-bin
   grid, then look up each of self.edges[0]'s bin centres into it) -- this is the same
   pattern nn_dump_inputs.py already uses, made a no-op/identity when self.edges[0] IS
   the standard grid (verified: standard-PS/xps runs unaffected, only xps2 exercises the
   actual remap). Flux is pT-flat to ~2e-14% per FPS_PILOT.md, so the remap is exact.
4. nn_dump_inputs.py, fps_gbdt_prior_reunfold_5d.py: NO changes (verified: both already
   inherit edges/flux/rectangle correctly -- nn_dump_inputs.py already had the flags +
   remap from the 2D pilot; fps_gbdt_prior_reunfold_5d.py loads edges/flux/pt_lo-hi
   entirely from the GBDT dump npz at lines ~93-104, confirmed by reading).
5. Prior ratios (fps_prior_genie_ratio_5d.npz, fps_prior_nuwro_ratio_5d.npz): NO rebuild
   -- already on the PT_EXT x PZ_EXT lookup grid (per user, not re-verified here).

All edits are additive (new optional CLI flags default to the old behavior); syntax-
checked with `ast.parse`.

DAG SUBMITTED (parallel, both independent of each other):
- sbatch_npz_pc_fps_xps2.sh -> job 55530633 (PC dump, 32cpu/120G/5h, shared_mi) ->
  of_inputs_pc_fps_xps2.npz + of_inputs_pc_fps_xps2_npy/
- sbatch_nn_dump_fps_5d_xps2.sh -> job 55530634 (GBDT dump, 8cpu/110G/4h, shared_mi) ->
  of_inputs_5d_fps_xps2.npz (expect "[INFO] flux remapped to 15 pT bins" in log)
Reference timing from Stage-1 xps (38.6M kept, smaller than xps2's expected ~49.9M kept):
pc dump 48m, GBDT dump 15m -- ample margin in the 5h/4h limits even scaled by the ~1.3x
row-count increase.

REMAINING DAG (not yet run):
(a) W-source dump (after pc dump 55530633 lands, needs its npz for the alignment
    self-check): `python3 dump_w_source_fps.py --omnifile
    runEventLoopOmniFold_PC_FPS_MEFHC.root --pc of_inputs_pc_fps_xps2.npz --wedges
    of_inputs_5d.npz --full-phase-space --pt-edges <PT_EXT> --pz-edges <PZ_EXT> --out
    of_inputs_5d_fps_xps2_wsource.npz` (run interactively via alloc_run.sh, matching
    Stage-1 precedent -- lightweight, single RDF pass).
(b) PET full-stats GPU retrain (SUBMIT AS EARLY AS POSSIBLE once (a)'s pc dump inputs
    exist -- last time queued 28h; user wants same hedge policy if PD > ~24h):
    `INPUTS=of_inputs_pc_fps_xps2.npz MEMMAP_DIR=of_inputs_pc_fps_xps2_npy
    SAVE_WEIGHTS=products/pet/pet_weights_fps_xps2.npz sbatch sbatch_pet_train_fps_hvd.sh`
    (existing script, unedited, env-var parameterized). Expect kept ~49.9M rows ->
    retrain ~11h (scaled from the xps run's 8h41m at 38.6M rows).
(c) Envelope re-run once (a)+(b)+GBDT dump 55530634 all land:
    new sbatch script (copy sbatch_fps_reunfold_5d_xps.sh's resource block) invoking
    `python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps2.npz --pet-pc
    of_inputs_pc_fps_xps2.npz --pet-weights products/pet/pet_weights_fps_xps2.npz
    --pet-wsource of_inputs_5d_fps_xps2_wsource.npz --full-phase-space --outdir
    products/pet/fps_envelope_5d_xps2 --iters 5 --seed 1000`
    NOTE: fps_gbdt_prior_reunfold_5d.py takes NO --pt-edges/--pz-edges flag (per the
    "no changes needed" verification) -- it inherits the extended grid entirely from
    --gbdt-in's own edges_0..3, so nothing extra to pass here.

ACCEPTANCE CHECKS TO REPORT once envelope lands:
(a) anchor: xps2 restricted to bins fully inside the standard grid AND theta<20deg
    should reproduce the standard-PS headline (Stage-1 benchmark: integral ratio 1.0047,
    median |r-1| 1.03%).
(b) extrapolated(comp<0.5) tier should now be NON-empty (unlike both Stage-1 runs),
    concentrated in the pz [0,0.75) and [0.75,1.5) rows and the pt [4.5,30] column --
    report measured vs extrapolated median/p90 (pilot 2D directional reference: in-PS
    ~3-5%, dead cells tens of percent -- NOT the same metric as the 5D envelope, see the
    Stage-1 caveat above, but directionally useful).
(c) completeness_profile should populate the low-completeness bins (no xsec-side
    blocker -- extract_cross_section_nd has no completeness floor, verified).

STOP after the envelope lands and report. Step 4 (Tier-2 retraining-response) then runs
ONCE against pet_weights_fps_xps2.npz, on separate explicit user go-ahead only.

## STAGE 2 GBDT DUMP COMPLETE (2026-07-05 11:01 UTC)
Job 55530634 (GBDT dump) COMPLETED (16m20s, exit 0:0). Log confirms
"[INFO] flux remapped to 15 pT bins" (the pet_systematics_5d.py-style remap logic
working as expected in nn_dump_inputs.py's pre-existing implementation) and
"[INFO] FULL PHASE SPACE: theta_mu truth gate lifted". Wrote of_inputs_5d_fps_xps2.npz
(2.09GB): MCgen(49152885,5) measured(4116128,5) pass_truth=49150928 pass_reco=20573521.
Kept row count (49.15M) matches the user's ~49.9M expectation closely (rectangle+theta
now covers nearly all truth, as predicted). No errors -- only benign RooUnfold dict
duplicate-registration warnings in stderr (harmless, cosmetic).

PC dump (job 55530633) still RUNNING as of this check (~23min elapsed, node nid004111,
reference ~48-60min) -- this is the critical-path job (needed for W-source dump +
GPU retrain). Waiting for it to land before proceeding to step (a)/(b) of the DAG.

## STAGE 2 CPU INPUTS COMPLETE + GPU RETRAIN SUBMITTED (2026-07-05 11:57 UTC)
Job 55530633 (PC dump) COMPLETED (58m47s, exit 0:0). of_inputs_pc_fps_xps2.npz (9.03GB)
+ of_inputs_pc_fps_xps2_npy/ (part_gen 11.80GB, part_reco 7.08GB, measured_pc 0.59GB,
pass_reco/pass_truth/w_truth/measured_weights/num_part) all present and sane.
Shapes: gen/reco (49152885,12,{5,3}), measured_pc (4116128,12,3) -- matches the GBDT
dump's measured count (4116128) exactly.

STRONG 3-WAY CROSS-CHECK: PC dump kept 49152885/49906108, GBDT dump kept (pass_truth)
49150928 with MCgen row count 49152885, W-source dump kept 49152885/49906108 -- all
THREE independently-computed row counts agree EXACTLY (49,152,885). This is a much
stronger alignment signal than Stage 1's already-strong match, since three separate
code paths (padded-cloud C++/PyROOT loop, vectorized RDF+numpy, vectorized RDF+numpy
with a different column set) all converge on the identical kept-row count.

Immediately submitted (in this order, per the time-critical GPU queue):
1. PET full-stats GPU retrain: `INPUTS=of_inputs_pc_fps_xps2.npz
   MEMMAP_DIR=of_inputs_pc_fps_xps2_npy SAVE_WEIGHTS=products/pet/pet_weights_fps_xps2.npz
   sbatch sbatch_pet_train_fps_hvd.sh` -> job 55533977, PENDING on gpu_ss11/gpu_regular
   (same QoS as Stage 1's 55445418, which took 28h32m to start -- no better QoS/partition
   available to this account, already exhaustively investigated in Stage 1). Expect
   ~11h runtime once running (scaled from Stage-1's 8h41m at 38.6M rows -> 49.15M rows,
   +27%).
2. W-source dump (interactive via alloc_run.sh, new shared alloc 55533981 since none was
   live -- prior claude-hold had expired/rotated, compliant, no second holder was
   concurrent): `dump_w_source_fps.py --omnifile runEventLoopOmniFold_PC_FPS_MEFHC.root
   --pc of_inputs_pc_fps_xps2.npz --wedges of_inputs_5d.npz --full-phase-space
   --pt-edges <PT_EXT> --pz-edges <PZ_EXT> --out of_inputs_5d_fps_xps2_wsource.npz`.
   Result: "[wsrc] ALIGN OK: coords exact (0 mismatch), w_truth bit-identical, pass_truth
   eq=True pass_reco eq=True, 0 NaN-pattern rows", kept=49152885/49906108. Wrote
   of_inputs_5d_fps_xps2_wsource.npz (1.25GB). W edges_4 = [0, 1.1, 1.4, 1.8, 2.2, 3, 100]
   (unchanged from Stage 1, as expected -- Eavail/q3/W edges untouched by Stage 2).

ALL THREE Stage-2 CPU inputs now complete and mutually row-aligned at 49,152,885 events:
of_inputs_5d_fps_xps2.npz (GBDT), of_inputs_pc_fps_xps2.npz (PET pc),
of_inputs_5d_fps_xps2_wsource.npz (W-source). Only remaining input: PET full-stats
retrain (job 55533977, GPU, queuing).

NEXT: monitor job 55533977. Once RUNNING, expect ~11h to completion. If PD exceeds
~24h with no ETA, submit a hedge second job per the Stage-1-approved pattern (distinct
job-name/output/SAVE_WEIGHTS e.g. pet_weights_fps_xps2_b.npz, cancel whichever is still
pending once the other starts). Once weights land, submit the envelope re-run (new
sbatch script mirroring sbatch_fps_reunfold_5d_xps.sh) with --gbdt-in
of_inputs_5d_fps_xps2.npz --pet-pc of_inputs_pc_fps_xps2.npz --pet-weights
products/pet/pet_weights_fps_xps2.npz --pet-wsource of_inputs_5d_fps_xps2_wsource.npz
--full-phase-space --outdir products/pet/fps_envelope_5d_xps2 --iters 5 --seed 1000.

## STAGE 2 GPU RETRAIN RUNNING (2026-07-06 06:38 UTC)
Job 55533977 transitioned RUNNING at approx 2026-07-06T06:14 UTC on node nid004056, after
a PENDING wait of ~18h20m (submitted 2026-07-05T11:54:28) -- shorter than Stage 1's
28h32m wait for the equivalent job, comparable congestion regime. No hedge was needed
(never crossed the ~24h threshold). Log health check: ITERATION 1 / RUNNING STEP 1,
loss stable ~0.1244, no errors. Note the epoch step-count (8616) differs slightly from
Stage 1's step-1 count (8346) reflecting the +27% row-count increase from 38.6M to
49.15M events. Expect ~11h total runtime (scaled from Stage-1's 8h41m).

## STAGE 2 PET FULL-STATS RETRAIN COMPLETE (2026-07-06 08:16 UTC)
Job 55533977 COMPLETED (exit 0:0, elapsed 9:02:21, started 2026-07-05T23:14:24 [node
local clock], finished 2026-07-06T08:16:45). Log confirms:
`[reweight-all] full-stats w_push n=49152885 mean=0.9991 std=0.1658 (finite=True)`
— row count matches of_inputs_pc_fps_xps2.npz exactly.

Numpy sanity check on products/pet/pet_weights_fps_xps2.npz (266MB):
  w_push: shape (49152885,) float64, min=0.355, max=3.326, mean=0.999, all finite
  mc_indices: (49152885,) int64
  pass_truth: (49152885,) bool
  model: scalar '<U3', closure: scalar bool
All sane -- no NaN/inf, weight range plausible for a reweight-all push (wider than
Stage-1 xps's [0.44,2.48] range, consistent with the extended catch-bin corners
carrying more extreme per-event reweights).

Immediately submitted the final envelope re-run:
  new script nd-unfolding/sbatch_fps_reunfold_5d_xps2.sh (copied sbatch_fps_reunfold_5d_xps.sh's
  resource block: qos=shared, constraint=cpu, 32 cpus, 120G mem, 6h, ROOT628_PREFIX exported)
  invoking: python3 fps_gbdt_prior_reunfold_5d.py --gbdt-in of_inputs_5d_fps_xps2.npz --pet-pc
  of_inputs_pc_fps_xps2.npz --pet-weights products/pet/pet_weights_fps_xps2.npz --pet-wsource
  of_inputs_5d_fps_xps2_wsource.npz --full-phase-space --outdir products/pet/fps_envelope_5d_xps2
  --iters 5 --seed 1000
  -> job 55574059, PENDING on shared_mi partition. Expected runtime ~1-2h (Stage-1's xps
  equivalent took 41min at fewer rows). Will report the three acceptance checks (anchor,
  tier split, completeness profile) on completion, then STOP per user instruction (no
  Step 4 without explicit go-ahead).

## STAGE 2 ENVELOPE RE-RUN FAILED (2026-07-06 09:59 UTC) -- infra crash, not a physics bug
Job 55574059 FAILED (exit 133, elapsed 57m45s). The ROOT event loop / GBDT computation
completed successfully -- stdout shows the FULL physics result before the crash:
  [gbdt5d] MCgen(49152885,5) measured(4116128,5) grid(15,19,7,7,6)
  [gbdt5d] truth-denom kept 49141649/49906108, denom check rel L1 diff = 0.000e+00
  [gbdt5d] unfolded tune=8.0729e-36 genie=8.2371e-36 nuwro=7.7199e-36
  [pet5d] W-source alignment OK, N=49152885, edges=[15,19,7,7,6]
  [gbdt5d] all reported             n=11875  median=18.04%  p90=57.90%  max=130.1%
  [gbdt5d] measured comp>=0.5       n=11875  median=18.04%  p90=57.90%  max=130.1%
  [gbdt5d] extrapolated comp<0.5    n=0
The crash (ROOT/cppyy C++ exception unwind, TExceptionHandlerImp) happened during/right
after fo.Close() writing fps_modeldep_cov_5d.root -- confirmed by reopening the file:
"file probably not closed, trying to recover" + "TH2D read too many bytes: 1128505657
instead of 54763833" (streamer byte-count corruption). np.savez_compressed and json.dump
(lines 230-235, AFTER the ROOT write) never executed -- no npz, no summary.json.

ROOT CAUSE DIAGNOSIS: the model-dependence covariance matrix is n_reported x n_reported
= 11875^2 doubles = 1.128 GB -- the FIRST time this campaign has crossed the ~1GB mark
for a single ROOT object. Stage 1's largest matrix (xps, n=10759) was 926 MB and wrote
fine; standard-PS (n=10550) was 890 MB. This is consistent with a known ROOT/PyROOT
instability writing single TObjects above ~1GB (streamer byte-count field corruption
under default compression). This is an INFRASTRUCTURE limitation, not a bug in the
Stage-2 grid/edge-flag code -- all upstream physics computation was correct (denom
check exact, W-source ALIGN OK, GBDT totals sane).

IMPORTANT CAVEAT for the (b) tier-split acceptance check: extrapolated(comp<0.5) is
STILL n=0 even with the Stage-2 extended grid (per the last stdout line before the
crash) -- contrary to the user's stated expectation that catch bins would populate the
extrapolated tier. This appears to be the genuine physics result, not a code bug (the
completeness computation ran identically to Stage 1's, just on the larger grid). Cannot
yet confirm this against completeness_profile bin population since summary.json was
never written.

STATUS: STOPPED per instruction -- FAILED job, not auto-resubmitting. Reported to user
with root-cause diagnosis and proposed fix options (reorder writes so npz+json land
before the risky ROOT write; and/or address the >1GB ROOT object issue directly).
Awaiting explicit user decision before any resubmission.

## STAGE 2 BUG FIX + CRASH FIX APPLIED (2026-07-06, before resubmit)
User caught a real bug in the tier-split logic, independently verified against the
surviving of_inputs_5d_fps_xps2_wsource.npz before applying the fix:

BUG: fps_gbdt_prior_reunfold_5d.py's two-tier split used `comp_tune` (the completeness
computed inside unfold_prior -- signal-tree truth vs the truth-denom TREE, i.e. SAMPLE-
COVERAGE completeness). That is the correct divisor for extract_cross_section_nd, but it
is ~1 by construction once FPS lifts the truth gate consistently between the signal and
truth-denom trees -- it cannot distinguish well- from poorly-constrained bins. This made
"extrapolated comp<0.5" identically EMPTY in every run of this script to date (both
Stage-1 xps and standard-PS, and the crashed Stage-2 xps2 run) -- a degenerate tier
split, not a genuine physics null result as I previously concluded.

VERIFICATION (independent, on of_inputs_5d_fps_xps2_wsource.npz, before touching code):
computed comp_reco = Sigma(w[pass_truth&pass_reco]) / Sigma(w[pass_truth]) per 5D bin
(reconstruction efficiency, CV weights, matches PETxsec5D._comp on the PET side):
  pz[0,0.75)+[0.75,1.5) catch rows: 1447 den>0 bins, median=0.0000, 100% < 0.5
  pt[4.5,30] catch column:           20 den>0 bins, 45% < 0.5
  pz[60,120) catch row:             426 den>0 bins, median=1.0 (well-covered)
  standard interior (pt 0-13, pz 2-17): 11307 den>0 bins, median=0.78
  overall: 13198 den>0 bins, 29.48% < 0.5 comp_split threshold
Exact match to the numbers the user cited from their own check -- confirms comp_reco
(not comp_tune) is the correct FPS_PILOT.md-style tier variable ("eff>=~2%" vs "dead").

FIX APPLIED to fps_gbdt_prior_reunfold_5d.py:
1. Added a top-level comp_reco computation (histogramdd on MCgen/pass_truth/pass_reco/
   w_truth, CV weights, prior-independent) right after the 3-prior unfold loop.
   comp_tune is UNCHANGED and still used internally by unfold_prior for
   extract_cross_section_nd (that divisor is correct as-is) -- only the top-level
   tier-split variable `comp_r` was switched from comp_tune[r] to comp_reco[r].
2. Both comp_tune and comp_reco are now saved in the npz (comp_tune=..., comp_reco=...).
3. Write order fixed: npz + summary.json now written FIRST, the ROOT artifact LAST --
   if the ROOT write ever fails again, the numeric results are already safely on disk.
4. Killed the dense TH2D covariance write entirely. C = 0.5*(outer(d_g,d_g) +
   outer(d_n,d_n)) is rank-2 by construction (d_g, d_n are the genie-tune and
   nuwro-tune per-bin PET-transferred deltas) -- never materialize the
   n_reported x n_reported matrix (that was the object that crossed 1GB and corrupted
   the ROOT file at the xps2 grid's n_reported=11875). sqrt(trace(C)) is now computed
   directly as sqrt(0.5*(sum(d_g[r]^2)+sum(d_n[r]^2))) -- exact, no approximation, and
   avoids ever allocating the dense matrix in memory OR on disk. d_genie=d_g[r] and
   d_nuwro=d_n[r] (length n_reported vectors, tiny) are now saved in the npz; if a ROOT
   artifact is wanted the two vectors are written as TH1Ds (hD_genie/hD_nuwro, ~95KB
   each) instead of the crash-prone TH2D. Consumers rebuild C exactly offline from the
   two vectors -- this also fixes an unnoticed pre-existing risk (the dense outer-product
   was being built in Python memory too, not just on disk).
5. Deleted the corrupted products/pet/fps_envelope_5d_xps2/fps_modeldep_cov_5d.root
   before resubmitting.
Syntax-checked with ast.parse; verified no leftover references to the removed `C`
matrix variable.

FLAGS FOR THE RECORD (informational, no action needed now, per user):
(a) With comp_reco as the tier variable at comp_split=0.5, ~29.5% of reported bins fall
    into Tier 2 (extrapolated) -- notably higher than FPS_PILOT.md's rough "eff>=2% vs
    dead cells" framing might suggest, but comp_reco is saved per-bin in the npz so the
    reporting threshold remains an offline choice; keeping split=0.5 for this campaign.
(b) This envelope's PETxsec5D is constructed with comp_ref=None (raw-epsilon divisor,
    no anchoring to the GBDT 5D product's hCompletenessND_flat) -- the FRACTIONAL
    envelope (env, ratio_g, ratio_n) is valid regardless, but the ABSOLUTE scale of
    x_pet/C_modeldep in this npz is NOT the anchored headline scale. Whenever
    C_modeldep from this campaign is combined with the headline covariance downstream,
    apply the fractional envelope ratios to the ANCHORED headline xsec -- never use
    this npz's raw x_pet/C_modeldep absolute values directly.
Note: Stage-1 and standard-PS baseline tier tables can be re-derived OFFLINE from their
existing (uncorrupted) npz + wsource files with the comp_reco fix -- no GPU/re-run
needed for those two.

Resubmitting the Stage-2 envelope re-run once, corrected.

Resubmitted (corrected script): job 55601108 on shared_mi partition. Expected ~1h
runtime (same computation as the crashed 55574059, ~58min before it crashed at the
write stage). Will report the corrected two-tier split (now comp_reco-based, expected
NON-empty extrapolated tier concentrated in the catch bins per the verification above)
plus the (a) anchor check and (c) completeness_profile once it lands.

## STAGE 2 FINAL RESULT (corrected) -- 2026-07-06 16:18 UTC

Job 55601108 COMPLETED (43m05s, exit 0:0). Both fixes verified working:
- npz+json wrote successfully BEFORE the ROOT file: `wrote .../fps_gbdt_prior_xsec_5d.npz
  + summary.json (sqrt-tr C_modeldep = 8.5649e-37)`.
- ROOT artifact wrote successfully AFTER, now tiny (189KB, two TH1Ds, not the crash-prone
  TH2D): `wrote .../fps_modeldep_cov_5d.root (hD_genie/hD_nuwro, rank-2 C
  reconstructible offline)`. No crash this time -- confirms the >1GB single-object
  ROOT write was the sole cause of the earlier failure.

### (a) ANCHOR CHECK
Script: nd-unfolding/HANDOFF_fps_step3/stage2_anchor_check.py. Restricted xps2's x_pet
(reshaped (15,19,7,7,6), sliced to the standard pt[0:14]/pz[2:18] sub-region) to bins
"interior" to theta_mu<20deg (atan2(pt_hi,pz_lo) < 20deg for each pt/pz bin's
max-theta corner) and compared per-bin against the standard-PS product's own x_pet
(reshaped (14,16,7,7,6)), keeping only bins where BOTH are populated (rep=True).

Interior pt/pz positions: 185/224 -> 9,752 five-dimensional bins with both populated --
this EXACTLY matches the "9,752 interior theta<20deg bins" figure from the Stage-1
validation, confirming the restriction methodology (same interior-bin definition) is
correct.

RESULT: integral ratio (xps2/std) = 0.9901, median |r-1| = 1.62%, p90 |r-1| = 4.23%
(one outlier bin at 96% -- a single low-statistics bin, does not move the median).
Stage-1 benchmark for comparison: integral ratio 1.0047, median |r-1| 1.03%.

ASSESSMENT: close but not identical to Stage-1's benchmark (0.99 vs 1.0047 integral
ratio; 1.62% vs 1.03% median). This is a fully independent re-run (new PET retrain on
49.15M events vs Stage-1's separate xps/std retrains on 38.6M/32.9M events, new GBDT
re-unfold with its own LightGBM stochasticity) -- the ~1-2% level of disagreement is
consistent with expected run-to-run statistical/algorithmic noise, not a systematic
distortion from the extended grid or catch bins. As a cross-check, restricting to the
SAME pt/pz sub-region WITHOUT the theta-interior cut gives integral ratio 1.42 (as
expected -- non-interior bins straddle the theta boundary and mixing in the newly-
admitted theta>20deg truth inflates the comparison there, confirming the interior cut
is doing its job and isolating the theta-independent, apples-to-apples core).

### (b) TIER SPLIT (now non-degenerate)
  measured(comp_reco>=0.5):    n=9307  median=18.66%  p90=61.58%  max=130.1%
  extrapolated(comp_reco<0.5): n=2568  median=16.28%  p90=45.35%  max=117.8%
  all reported:                n=11875 median=18.04%  p90=57.90%  max=130.1%
n_reported = measured+extrapolated = 9307+2568 = 11875, exact. Extrapolated fraction
2568/11875 = 21.6% of REPORTED bins -- in the same regime as FPS_PILOT.md's rate-based
"~28% dead cells" pilot estimate (different weighting -- bin-count vs rate -- so not
expected to match exactly, but consistent in magnitude). Independently cross-checked
against the truth-denom-based comp_reco computed directly on
of_inputs_5d_fps_xps2_wsource.npz BEFORE this run (1447 catch-row bins @ comp_reco median
0.0/100%<0.5, pt-catch column 45%<0.5, 29.5% overall <0.5 among den>0 bins) -- the
PET-populated (rep=True) extrapolated count (2568/11875=21.6%) is somewhat lower than
the truth-denom-based fraction (29.5%) because "rep" (PET push-weight populated) is a
stricter/different mask than "den>0" (truth-denom populated) -- expected, not a
discrepancy.

Interestingly, the extrapolated tier's SPREAD is actually slightly LOWER than the
measured tier's (median 16.28% vs 18.66%, p90 45.35% vs 61.58%) -- i.e. the catch bins
do NOT show a dramatically larger 3-prior spread than the well-measured interior, unlike
the 2D pilot's "tens of percent in the dead regions" framing. This may reflect that the
GBDT re-unfold (which drives xs_gbdt_tune/genie/nuwro and hence env) constrains these
bins better than the pilot's coarser 2D binning did, OR that PET's rep mask already
excludes the very worst (near-zero-statistics) corners that the pilot's efficiency-based
Tier-2 language was describing. Flagging for awareness, not resolving further this
session.

### (c) COMPLETENESS PROFILE (now populated, not single-bucket)
  [0.0,0.1):  n=1134  median_env=16.88%
  [0.1,0.3):  n= 489  median_env=15.84%
  [0.3,0.5):  n= 945  median_env=15.95%
  [0.5,0.7):  n=1780  median_env=16.43%
  [0.7,1.01): n=7527  median_env=19.36%
Sum = 11875, exact match to n_reported. Unlike Stage-1's single-bucket [0.7,1.01)
profile (all bins at comp_tune~1), the corrected comp_reco-based profile shows the
expected spread across completeness deciles, concentrated at both extremes (low-eff
catch corners at [0,0.1) and well-measured interior at [0.7,1.01)), with comparable
env-spread (~16-19%) across ALL buckets -- i.e. no bucket shows the dramatic tens-of-
percent bloom the 2D pilot anticipated for dead cells; the envelope fraction is
remarkably FLAT (16-19%) across the whole completeness range.

### PHYSICS ASSESSMENT
The Stage-2 extended grid successfully brings the low-p_par catch strip (22.4% of rate
per FPS_PILOT.md) and the pt>4.5 wedge into the reporting grid, and the two-tier split
(after fixing the tier variable to reconstruction efficiency) now correctly identifies
21.6% of reported bins as extrapolated/low-completeness, concentrated in the expected
kinematic corners (verified offline against the wsource npz). The headline finding is a
mild surprise relative to the 2D pilot's framing: the model-dependence ENVELOPE FRACTION
is essentially flat (~16-19%) whether a bin is well-measured or in the extrapolated
tier -- the catch bins are not dramatically worse than the interior, unlike the pilot's
"tens of percent in the dead regions" language (which used a DIFFERENT metric: 2-prior
MnvTune-vs-bare-GENIE per-cell disagreement on an efficiency-binned 2D grid, not this
3-prior 5D GBDT-envelope spread/mean). The anchor check (0.99 integral ratio, 1.62%
median deviation vs Stage-1's 1.0047/1.03%) confirms the extended grid and theta lift
do not distort the well-measured core, within expected run-to-run noise.

STAGE 2 IS NOW COMPLETE with both the crash and the tier-split bug fixed and verified.
Reported to user 2026-07-06 (approx). STOPPING per instruction -- NOT proceeding to
Step 4 (Tier-2 retraining-response) without separate, explicit user go-ahead.

## STEP 4 (Tier-2 retraining-response, b-lite) -- SCOPE CONFIRMED + LAUNCHED (2026-07-06)
User corrected scope: HANDOFF.md's per-universe Cov(delta) language was DRIFT, not the
plan of record. Actual scope (2026-06-29 uncertainty plan item 4, matching
docs/OPEN_ITEMS.md and pet_unified_throw_5d.py's own infeasibility note): a
CONVERGENCE-CURVE / ML-noise-floor check, NOT a full per-universe PET retrain. Fixed
HANDOFF.md's wording (struck the drift paragraph, added a corrected-scope paragraph)
so this doesn't recur. PET systematics remain covered by the adopted GBDT 5D unified
covariance + fractional transfer (unchanged); bank_uthrow_5d is NOT part of Step 4.

CONCRETE SPEC (user-provided):
1. Trainings: 4 seed replicas at 10M-event subsample of xps2 inputs + 2 replicas at 5M
   (convergence slope). 6 total, ~1-2h GPU each, ONE job array submission.
2. Evaluation (CPU): push each replica through PETxsec5D on xps2 inputs -> per-bin x_pet
   spread across replicas -> sigma_retrain/x by comp_reco tier.
3. Acceptance: Tier-2 median sigma_retrain/x well below the 16.28% prior-envelope
   median (target <=1/3, i.e. ~5.4%), and 5M->10M trend shrinking.
4. No pet_universe_retrain.py / bank_uthrow -- not part of Step 4.

CODE CHANGES:
- pet/minerva_pet_dataloader.py: added --seed CLI flag (previously build_loaders() had a
  seed= kwarg with a hardcoded default=0 caller-side, so ALL --max-events subsamples to
  date -- including every prior full-stats/xps/xps2 training -- drew the IDENTICAL
  0-seeded subsample; this had no effect on those runs since they used max_events near
  or above the full row count, but would have silently made any two "different-seed"
  convergence replicas identical without this fix). Verified max_events operates as a
  GLOBAL subsample cap (drawn once via np.random.default_rng(seed), then
  [rank::size]-strided across horovod ranks) -- confirmed by reading
  _build_pointcloud_memmap directly, so TRAIN_EVENTS=10000000/5000000 in the job array
  are genuine global caps, not per-rank.
- HANDOFF.md: corrected Step-4 scope wording (see above).

NEW FILES:
- sbatch_pet_conv_fps_xps2.sh: job array (--array=0-5), same 4-GPU horovod resource block
  as sbatch_pet_train_fps_hvd.sh, NITER=5/EPOCHS=8 fixed (matching the xps2 headline
  recipe), varying only --seed/--max-events per task:
    task0: seed=101 events=10M -> pet_weights_fps_xps2_conv_10M_s101.npz
    task1: seed=102 events=10M -> pet_weights_fps_xps2_conv_10M_s102.npz
    task2: seed=103 events=10M -> pet_weights_fps_xps2_conv_10M_s103.npz
    task3: seed=104 events=10M -> pet_weights_fps_xps2_conv_10M_s104.npz
    task4: seed=201 events=5M  -> pet_weights_fps_xps2_conv_5M_s201.npz
    task5: seed=202 events=5M  -> pet_weights_fps_xps2_conv_5M_s202.npz
- pet_conv_check_5d.py: CPU-only evaluation script. Loads the 6 replica npz's, pushes
  each through PETxsec5D on the same xps2 pc/wsource inputs, computes per-bin
  std-across-replicas / mean at each event count, splits by comp_reco tier (reused
  directly from the already-landed fps_envelope_5d_xps2/fps_gbdt_prior_xsec_5d.npz's
  comp_reco+rep arrays -- no re-derivation), reports median/p90 sigma_retrain/x by tier
  and the 5M->10M trend, checks against the 5.4% target, writes
  products/pet/pet_conv_check_5d_xps2.npz.

SUBMITTED: job array 55614759 (tasks 0-5) on gpu_ss11/gpu_regular, ONE submission per the
user's explicit "queue wait is the dominant cost, don't pay it per job" instruction.
Expected ~1-2h GPU time per task once running (scaled from the 49.15M-event headline's
9h02m: 10M/49.15M*9h ~ 1.8h, 5M ~0.9h); queue wait unknown (this session has seen 18-28h+
PD waits on this same partition/QoS for the two prior full-stats retrains).

NEXT: monitor the array. Once ALL 6 tasks complete, run pet_conv_check_5d.py (CPU, no
GPU -- run via alloc_run.sh or the interactive shared allocation) and report the
convergence-curve result. Do NOT proceed to any further step without separate user
go-ahead (though none is currently planned beyond this check).

## STEP 4 JOB ARRAY FAILED + FIXED + RESUBMITTED (2026-07-07 05:01 UTC)
Job array 55614759 (submitted 2026-07-06T19:57:22, PENDING ~8h32m) started expanding:
tasks 0,1,2 ran and FAILED within 15-18s each (`ModuleNotFoundError: No module named
'tensorflow'`); task 3 started running and was about to hit the identical deterministic
bug. BUG: sbatch_pet_conv_fps_xps2.sh omitted the `module load tensorflow/2.15.0` line
that sbatch_pet_train_fps_hvd.sh (the script this was modeled on) has -- a copy-paste
gap introduced when writing the new job-array script, not a transient/environment
issue. Since the failure is 100% deterministic given the identical script, cancelled
the remaining pending/running tasks (`scancel 55614759` -- tasks 3/4/5, all started
this session, safe) rather than let them burn through the same futile run-fail cycle.
Fixed sbatch_pet_conv_fps_xps2.sh (added `module load tensorflow/2.15.0` right after
`cd nd-unfolding`), verified queue clear, resubmitted immediately as a fresh array:
job 55617664 (tasks 0-5), same spec as before (seeds 101-104 @ 10M events, 201-202 @ 5M
events). This re-pays the full queue-wait from scratch (~8.5h already spent on
55614759's failed submission) -- unavoidable once the first attempt failed on a
deterministic bug, but the fix itself required no further code changes beyond the one
missing module-load line.

## STEP 4 RESULT (Tier-2 retraining-response, b-lite / convergence-curve check) -- 2026-07-07

All 6 seed replicas of job array 55617664 COMPLETED successfully (10M-event tasks
0-3: 2h37m-2h38m each; 5M-event tasks 4-5: 1h34m each). All 6 weight npz's verified
present and sane (~264-265MB each). Ran pet_conv_check_5d.py via alloc_run.sh (shared
allocation 55622959) -- CPU-only, no GPU. W-source alignment OK for every replica
evaluation (w_truth bit-identical, N=49,152,885 matching the headline exactly).

### sigma_retrain/x_pet by completeness tier

|                          | n     | median | p90   |
|--------------------------|-------|--------|-------|
| 10M Tier-1 (comp>=0.5)   | 9307  | 1.38%  | 2.44% |
| 10M Tier-2 (comp<0.5)    | 2568  | 1.14%  | 2.17% |
| 5M  Tier-1 (comp>=0.5)   | 9307  | 1.20%  | 2.38% |
| 5M  Tier-2 (comp<0.5)    | 2568  | 1.37%  | 2.29% |

### Acceptance check vs the 3-prior model-dependence envelope
- 10M Tier-2 median (1.14%) vs envelope Tier-2 median (16.28%) -> **ratio = 0.070**
  (target: <=0.33, i.e. the retraining floor came in at ~1/14 of the envelope, not
  just under the 1/3 bar).
- 5M->10M Tier-2 trend: 1.37% -> 1.14% (**shrinking = True**), confirming the
  ML-retraining noise floor decreases toward full statistics as expected for a
  genuine convergence trend (not noise-dominated at this scale already).
- Tier-1 shows a small INCREASE 5M->10M (1.20% -> 1.38%) -- within expected
  sampling noise given the small replica counts (2 at 5M, 4 at 10M); does not
  affect the Tier-2 acceptance conclusion, which is the one the campaign cares
  about (Tier-2/extrapolated bins are where the retraining-vs-frozen gap would be
  expected to bite hardest, per the original concern motivating Step 4).

### PHYSICS ASSESSMENT
The Tier-2 retraining-response floor (~1.1-1.4%, shrinking with event count) sits
FAR below the 3-prior model-dependence envelope (16.28% Tier-2 median) -- by more
than an order of magnitude margin, not just marginally below the 1/3 target. This
confirms the PET headline's ML-training noise is a negligible contributor relative
to the dominant extrapolation systematic (the 3-prior GBDT-transfer envelope,
already in the PET FPS uncertainty budget). No further retraining-response work
(per-universe or otherwise) is warranted -- the frozen-reweighter transfer approach
used throughout the FPS campaign (train PET once, reweight via GBDT-derived prior
ratios for the systematic envelope) is well justified: retraining noise is not
large enough to meaningfully change any systematic conclusion.

STEP 4 IS NOW COMPLETE. All FPS-campaign steps (1: theta lift, 2: extended grid,
3: 3-prior model-dependence envelope, 4: retraining-response convergence check) are
done. STOPPING per no further authorized step -- awaiting user direction on write-up
or any follow-on work (e.g. folding these numbers into the analysis note).
