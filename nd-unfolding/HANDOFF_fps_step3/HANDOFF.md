# HANDOFF — PET-5D FPS uncertainty campaign (personal → claude-school)
Written 2026-07-02 ~11:45 by the personal-account session (job 83fd877b). Point claude-school here.

## ⚠️ The auto-wakeup does NOT transfer
The personal session drove this with `ScheduleWakeup` timers bound to that session. They stop when
that account stops. **claude-school must start its own monitoring loop** (`/loop` with no interval,
or its own ScheduleWakeup each turn). The SLURM jobs below keep running regardless — only the
orchestration/polling needs re-establishing. claude-school has a SEPARATE memory dir, so read THIS
file + the two state files in this dir (fps_pipeline_state.md, d5d7_state.md) for context.

## WHERE THINGS STAND
DONE (reported):
- GBDT-side **D5** (adopt_unified_5d.py → uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root,
  hist hCov_combined5d_total_uthrow; PSD-safe inflation transfer, √trace ×1.413). School has a
  cross-check variant uq_5d/gbdt_5d_covariance_adopted.root (both PSD, keep personal's as adopted).
- GBDT-side **D7** (pet/pet_vs_gbdt_uncertainty_5d.py on UNIFIED covs → products/pet/unified5d/):
  PET 16.7% vs GBDT 13.7% median frac, ratio 1.35, PET tighter in 30% → PET worse at 2M-train
  (the CV gap; full-stats closes it).
- **FPS headline PET weights**: products/pet/pet_weights_fps.npz (full-stats 32.9M push weights).

IN PROGRESS — **Step 3 (3-prior model-dependence envelope), DOMINANT extrapolation syst**:
- The cheap frozen-reweighter shortcut was PROVEN INVALID (xsec(rho) just propagates the prior
  ratio, corr=1.0000, no data reconvergence). User approved **option 1 = GBDT re-unfold + transfer**.
- CHAIN CANCELLED 2026-07-02 ~11:47 for clean handoff (jobs 55395620/55395622 were still PENDING,
  never ran — nothing lost). **claude-school: RESUBMIT it fresh** (all scripts + inputs persist):
  ```
  cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding
  DUMP=$(sbatch --parsable --qos=regular --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=0 sbatch_nn_dump_fps_5d.sh)
  sbatch --dependency=afterok:$DUMP sbatch_fps_reunfold_5d.sh
  ```
  → dump (→ of_inputs_5d_fps_full.npz) → reunfold (fps_gbdt_prior_reunfold_5d.py) →
  **products/pet/fps_envelope_5d/fps_modeldep_cov_5d.root** (hCov_modeldep5d) + fps_gbdt_envelope_5d_summary.json.
  (Both sbatch scripts already source the FIXED setup_salloc_env.sh.)

PENDING — **Step 4 (Tier-2 retraining-response, b-lite)**: NOT started. GPU work — CONFIRM SCOPE
WITH USER before launching.

CORRECTED SCOPE (2026-07-06, superseding the paragraph below which was DRIFT from the actual
plan of record — the 2026-06-29 uncertainty plan's item 4, "Tier-2 retraining-response at
8-10M, convergence curve justifies", matching docs/OPEN_ITEMS.md and pet_unified_throw_5d.py's
own infeasibility note): this is a CONVERGENCE-CURVE / ML-noise-floor check, NOT a full
per-universe PET retrain. Train a handful (<=6) of seed replicas of PET at 10M and 5M event
subsamples of the xps2 inputs, evaluate each via PETxsec5D, and take the spread across
replicas as sigma_retrain -- compare sigma_retrain/x by completeness tier against the 3-prior
envelope median to confirm the ML-retraining floor is well below the model-dependence signal.
PET systematics remain covered by the adopted GBDT 5D unified covariance + fractional
transfer (unchanged) -- Step 4 does NOT build a per-universe PET covariance and does NOT touch
bank_uthrow_5d.

~~PRIOR (drift, do not follow) — Plan: apply bank_uthrow_5d restricted-PS universe reweights to
in-acceptance FPS events, hold extra-miss at CV, retrain PET at 8-10M, δ=x_retrain−x_frozen,
subtract seed+7 jitter, add Cov(δ); + small FPS-universe validation dump.~~ This description
(a per-universe δ=x_retrain-x_frozen assembled into a full Cov(δ) across the 124-universe bank)
was never actually authorized scope and conflicts with pet_unified_throw_5d.py's own note that
per-universe PET retraining is "~160 GPU trainings; infeasible". Do not resurrect it without a
fresh, explicit user go-ahead.

## NEXT ACTIONS (in order)
0. RESUBMIT the step-3 chain (see the two-line sbatch block above) — the personal session
   cancelled it for a clean handoff; it never ran, so just resubmit under school's ownership.
1. Monitor the chain. When fps_modeldep_cov_5d.root lands: READ fps_gbdt_envelope_5d_summary.json
   and REPORT the two-tier model dependence (median/p90 for measured comp>=0.5 vs extrapolated
   comp<0.5 + completeness_profile — it should BLOOM in extrapolation, unlike the invalid frozen
   result ~20%). Sanity-check: the denom-vs-dump validation line + GBDT totals in fpsreunf5d_*.out.
2. Add C_modeldep to the PET FPS uncertainty budget (it's the dominant extrapolation systematic).
3. Confirm scope with user, then do Step 4.
   TRIAGE the chain only on FAILED/TIMEOUT/OOM. PENDING(Priority) = node starvation → wait, or
   regular-QoS resubmit after ~2h (dump already on regular). If a job FAILS in ~3s → env (see below).

## ENV (root_6_28) — FIXED 2026-07-02
setup_salloc_env.sh now activates root_6_28 by FULL PREFIX (the `module load python; conda activate
root_6_28` path broke when the default python module moved to conda 26.1.0; env was built under
24.10.0). All sbatch scripts source setup_salloc_env.sh (fixed). For claude-school's INTERACTIVE
ROOT/python work (redirected HOME), source ./rootenv.sh in this dir (HOME override + full-prefix
activate + cd to nd-unfolding). Gives ROOT 6.28/12 + lightgbm 4.6.0.

## CONSTRAINTS (carry over)
- CONFIRM scope/compute cost with user before large sbatch arrays or ANY GPU job (step 4).
- Do NOT modify existing TRACKED scripts/covariances. New files only under uq_5d/, products/, or
  new *_5d/*_fps scripts. (School's own new files are fine.)
- Two D5 variants reconciled: keep personal's *_uthrow.root as adopted, school's *_adopted.root as
  cross-check. School's fps_prior_nuwro_ratio_5d.npz is correct (PT_EXT = per-event LOOKUP grid).
- Remote is `github` NOT origin; commit direct to main only when the user asks.

## KEY FILES (all in nd-unfolding/ unless noted)
NEW this session: adopt_unified_5d.py, dump_w_source_fps.py (→of_inputs_5d_fps.npz, W-source bit-
aligned), build_fps_prior_genie_5d.py (→products/5d/fps_prior_genie_ratio_5d.npz),
fps_3prior_envelope_5d.py (INVALID frozen driver, documented negative result),
fps_gbdt_prior_reunfold_5d.py (the correct step-3 driver), sbatch_nn_dump_fps_5d.sh,
sbatch_fps_reunfold_5d.sh, rootenv_sbatch.sh (transient; retire after 55395620/55395622 finish).
INPUTS: of_inputs_pc_fps.npz (PET pc), of_inputs_5d_fps.npz (W-source), pet_weights_fps.npz,
fps_prior_{genie,nuwro}_ratio_5d.npz, bank_uthrow_5d/ (universe reweights for step 4).
Personal-account memory (school can't see it, listed for reference): pet_fps_headline_uncertainty_plan,
pet_vs_gbdt_5d_unified, d5_two_variants_reconciled, env_root628_activation_regression.
