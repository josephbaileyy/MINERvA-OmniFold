# D5/D7 state (GBDT-side, after unified cov landed 2026-07-02)
GBDT unified cov: uq_5d/unified_throw_cov_5d.root  (C_unified,C_blocksum,C_cross) DONE
D5 = adopt_unified_5d.py (PSD-safe inflation transfer, mirrors adopt_unified_4d.py):
  first run OOM (login bg cgroup, EXIT137); rewritten memory-frugal (row-by-row,
  peak ~2 matrices). Resubmitted as sbatch 55379222 (shared cpu --mem=32G).
  -> uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root
     (hist hCov_combined5d_total_uthrow)
D7 = pet/pet_vs_gbdt_uncertainty_5d.py on the two UNIFIED covs:
  parameterized with new --cov-method (in-place edits done, guard inactive this session).
  RUN when D5 output exists:
    python pet/pet_vs_gbdt_uncertainty_5d.py \
      --gbdt-cov uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root \
      --gbdt-cov-hist hCov_combined5d_total_uthrow \
      --pet-wlat products/pet/pet_5d_covariance_combined_unified_wlat.root \
      --outdir products/pet/unified5d \
      --label "PET vs GBDT, UNIFIED-throw covariance (both engines), 5D (pt,pz,Eavail,q3,W); PET anchored to 2M-train reweight - indicative" \
      --cov-method "unified-throw adopted, identical scheme for PET and GBDT"
ROOT env helper: source $CLAUDE_JOB_DIR/tmp/rootenv.sh (HOME=real, conda 24.10.0 base, activate root_6_28 by full prefix)
FPS train 55288409 RUNNING in parallel -> products/pet/pet_weights_fps.npz (headline).
