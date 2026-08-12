## The PET covariance summaries carry no estimator stamp — the fact lives only in the launcher

`products/pet/bkgsub/pet_cstat_bkgsub_5d.summary.json` and its siblings record `n_replicas`,
`replica_ids`, `n_reported_bins`, the sqrt-trace and per-bin ratios — and **nothing about the estimator
that produced them**: no `niter`, no schema/feature set, no commit, no job id. Their producers
(`pet/combine_cstat_bkgsub.py`, `pet/assemble_ctotal_bkgsub.py`) do not record it either, because they
combine replica outputs and never see the training config.

**Correction, 2026-08-06:** an earlier version of this entry said the fact "was never written down."
That is wrong, and wrong in the direction that matters. `pet/sbatch_pet_nominal_bkgsub.sh:42` pins
`NITER="${PET_NITER:-2}"`, its header at `:29` states `iters = 2` in as many words, and `:14` carries
the banner **"QUARANTINED RECOIL-ONLY CROSS-CHECK LAUNCHER — NOT a publication path"**, with `:15-17`
naming the recoil loader and the bkgsub purity target and noting that "C_stat, C_ml, and systematic
blocks all reference THIS nominal." So the provenance is recorded — just not in the artifact a reader
of the covariance would open.

That makes the classification **stronger**, not weaker. These components are disqualified from the
`niter=3` budget by three *positive* facts, not by an absence: they were built at **`niter=2`**, on a
path the repo itself labels **non-publication**, over a **10550-bin recoil domain** (against 10694 for
the 5D lane re-rolled in `uq_5d/rescaled_20260806/j28_reroll_20260806.json`). This satisfies
`PLAN-20260806-niter3-budget-and-J28-reroll.md` rule 5, which demands a stated reason rather than the
absence of a reason to doubt.

The debt that remains is the **stamp**, and it is real: nothing in the artifact chain would have told a
future reader any of the above, and the whole `bkgsub` budget — C_syst, C_retrain, C_stat, C_ml,
C_lateral and the assembled C_total — hangs off that one quarantined nominal.

**Fix forward:** any new covariance component must stamp the estimator config it was computed under
(at minimum `niter`, schema/feature-set identifier, and the producing commit) into its own summary,
the way `train_fullevent_nominal.py` stamps `seed_policy` into its weights artifact. A covariance
without that stamp is unclassifiable from the artifact the moment the estimator moves, and the
estimator has now moved twice (full-event schema 2026-08-01, `niter` 2026-08-06).

