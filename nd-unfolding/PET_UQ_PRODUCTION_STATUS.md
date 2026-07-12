# PET UQ Production — live status (PET point-cloud campaign)

**Session scope:** PET point-cloud uncertainty campaign ONLY. Produce a
corrected, internally consistent PET budget on a **background-subtracted**
measured target: `C_total = C_syst + C_stat + C_ML + C_lateral`, all components
sharing one corrected nominal PET estimator (same central vector, reported-bin
mask, bin ordering, training target, extraction config). Ordered plan and gates
mirror `PET_UQ_REMEDIATION_STATUS.md` (the authoritative dependency map).

This file is THIS session's live PET execution tracker: job IDs, config
choices, gates, failures, recovery. It is NOT the GBDT execution tracker
(`CORRECTED_UQ_PRODUCTION_STATUS.md`, read-only to this session).

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
| 4 | Corrected C_stat (coherent data+MC Poisson replicas, fixed estimator/split seed) | strict manifest; full MC coverage; center on replica mean; pilot vs floor | **PILOT running** (RIDs 1-6; combine via combine_cov_nd once landed) |
| 5 | Corrected PET C_ML (crossed subsample-seed × TF-seed, no Poisson) | ensemble-mean-centered; same mask/order; seed metadata; vs floor | **LAUNCHED** (4 sub × 3 est = 12 trains) |
| 6 | Rebuilt C_syst (vertical), PET-native lateral, unified/block diagnostic — on corrected nominal | actual ±, MAT 1/N mean-centered, 100-flux inventory; KNOWN_ISSUES #13/#16 respected | pending P2 + GBDT bank |
| 7 | Targeted per-universe retraining-response verdict | predeclared materiality criterion (trace + per-bin tail) | pending P2/P5/P6 |
| 8 | Final assembly `C_total`, `C_4D = M C_5D M^T` | all blocks common central/mask/order; PSD/eigen; manifests | pending all |

DONE requires all 13 items in the scope's DEFINITION OF DONE. This is a
multi-session, multi-GPU-hour campaign; blocked-on-GBDT items (lateral,
targeted retraining) are labeled preliminary/blocked, not final, if their
shared products are missing.

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
| 55830054-065 | pet_nom_bkgsub (cml) | 5 | 2026-07-12 | PENDING/RUNNING | C_ml crossed ensemble: sub{0,1,2,3}×est{42,43,44}=12, no bootstrap. → `cml/pet_s{S}_e{E}_bkgsub_5d_{weights,xsec}.npz`. |

## DECISION LOG / GATES PASSED
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
