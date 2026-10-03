# 2D statistical bootstrap spreads re-measured on the quoted pure-Poisson replicas (2026-10-03)

**Why.** App. A printed a total-σ relative std (0.068% → 0.061%), a per-bin median (0.532% → 0.564%) and a
per-bin p84 (1.235% → 1.215%) for N = 50 → 300. These came from the superseded seed-varying set (sbatch 53327775,
text from `bf11cf1f`, one day before the swap). The quoted block is the pure-Poisson set (`--seed 1`, sbatch
53489662; `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:99, :111-116`).

**Method.** `boot_spreads.py` (sha256 `a1f02d96…`) imports `2d-unfolding/uq/analyze_uq.py` unchanged
(sha256 `bf94c957…`, identical to the repository's) and applies its definitions to
`uq/2d_xsec_MEFHC_5iter_lgbm_boot{1..300}.root` on Perlmutter. Those are the files the pinned-seed launcher
`sbatch_unfold_2d_MEFHC_5iter_bootstrap_scaleup.sh` writes; mtimes 2026-05-27 13:18 to 2026-05-29 02:18 UTC. It
uses all 300 replicas and the first 50 (boot1–boot50). Run on Perlmutter login33, 2026-10-03, `root_6_28`. It wrote
only `/pscratch/sd/j/josephrb/note-boot-20261003/`.

**Controls (all pass).** The 300 replicas reproduce the stored rollup
`uq/bootstrap_MEFHC_300/uq_covariance_boot300.root` (sha256 `f7c734b1…`):
- covariance max |Δ| / max = 4.1e-16, mean max rel. diff 2.0e-15, the same 205 reported bins;
- √tr C = 1.8165e-40 and median 0.5494%, the quoted 1.817e-40 and 0.549%.

So these files are the set behind the quoted block. The files carry no seed metadata, and their `.done` markers
were backfilled on 2026-08-04, so "pinned seed" rests on the launcher and run log together with this identity.

**Result** (`boot_spreads.json`, sha256 `e0fa99d5…`).

| | first 50 | all 300 |
|---|---:|---:|
| total-σ relative std | 0.0674% | **0.0606%** |
| per-bin median relative spread | 0.5409% | **0.5494%** |
| per-bin p84 | 1.1945% | **1.2025%** |
| per-bin p16 | 0.3250% | 0.3332% |
| per-bin max | 3.40% | 3.31% |
| √tr C | 1.758e-40 | 1.817e-40 |

Single-lane measurement, not independently reviewed.
