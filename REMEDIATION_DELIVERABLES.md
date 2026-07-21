# UQ Remediation — Deliverables & Verification Record

**Status:** working-tree deliverable, UNCOMMITTED. HEAD `3e85589` unchanged.
**Session (claude-school):** independent audit + verification of the in-flight
UQ remediation. No commit/push. No large jobs launched. Shared allocation
`55798579` left running. All user-owned / personal-account dirty files
preserved.

Provenance tags below:
- **[VERIFIED]** — re-checked directly in this session (code read + evidence).
- **[RELAYED]** — carried from the prior remediation handoff; not independently
  re-derived here.

---

## 1. Verification results (this session)

### 1.1 Remediation test suite — [VERIFIED] 16/16 PASS
`python3 -m unittest discover -s nd-unfolding/tests -q` → **Ran 16 tests, OK**
(run on compute node `nid004282`; the `EnvironmentNameNotFound: root_6_28`
line is stderr chatter from the conda-by-name fallback — tests ran under the
system numpy and passed). Coverage: asymmetric ± interpolation & invalid-ratio
guard; MAT mean-centred 1/N pair covariance; fixed-seed null → 0; synthetic
slab/block combine end-to-end + expected-throws gate; unified-bank
missing-endpoint rejection; covariance projection; non-uniform density
integral; lateral migration masks (both directions); finite-support
signal/denominator closure; replica-manifest rejection (missing/dup/NaN/wrong
shape); PET MC bootstrap-factor reproducibility + float32; measured-data
retrain response; strict full-coherent-draw replica + manifest write; in-
pipeline NN `sys` import; PET CLI fixed estimator seed.

### 1.2 Active-universe C++ mode — [VERIFIED] CORRECT
`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp`
(`MNV101_ACTIVE_UNIVERSE=BAND:IDX`). Checked line-by-line:

- **State restoration (truth census, ll. 505–518).** For the first occurrence
  of each deduped key it sets the CV comparison universe, computes the CV
  truth-denominator pass, then restores `truthCV->SetEntry(i)` +
  `model.SetEntry(*truthCV, evt)` before the fill. `w_cv` (a captured double)
  is unaffected. Restore is unconditional w.r.t. pass, and precedes
  `if(!activePassesTruth) continue;`. ✔
- **State restoration (reco census, ll. 972–990).** Runs in `SetTruth(false)`
  after `passesReco` is computed; compares CV reco selection; restores
  `recoCV->SetEntry(i)` + `model.SetEntry(*recoCV, evt)`. The subsequently-read
  `sim*`/`w_reco`/`sim_pass` use the already-captured `passesReco` and the
  restored entry. ✔
- **SetTruth static flag.** Re-established at the top of every truth iteration
  (`SetTruth(true)`, l.489) and every reco iteration (`SetTruth(false)`,
  l.943). No cross-iteration leak from a census or the relocated `continue`. ✔
- **Relocated `if(!isSignalTruth) continue;` (l.1000).** The truth-branch
  assignment is now guarded by `if(isSignalTruth)` and the skip moved below the
  reco-mode block so the reco migration census sees all reco entries. Filled-
  tree content is byte-identical to the pre-change path for kept (signal)
  events; non-signal events still `continue` before `out->Fill()`. Only extra
  cost is computing `sim*` for non-signal events that are then skipped — no
  correctness effect. In non-active mode (`comparisonCV==nullptr`) the census
  block is fully skipped. ✔
- **Band resolution & guards (ll. 1509–1560).** Rejects unknown/unmatched
  band, out-of-range idx, null pointers, and reco/truth `IsVerticalOnly`
  mismatch; `MNV101_ACTIVE_UNIVERSE` + `MNV101_SKIP_SYST` rejected up front
  (returns `badCmdLine`). ✔
- **Propagation.** `recoCV`/`truthCV` point at the active universe objects;
  background loop receives the active `recoCV` (l.1666) → active selection,
  kinematics, weights; data loop keeps `data_universe` (data-CV, l.1668). ✔
- **Metadata (ll. 1572–1590, 1689–1700).** Invariants (`hasActiveUniverse`,
  `activeUniverseIndex`, `activeUniverseIsLateral`) are `TParameter<int>` with
  merge mode `'f'` (keep-first); `activeUniverseBand` is a `TNamed`; migration
  counters are default-merge `TParameter<long>` (additive). ✔

### 1.3 Post-final-edit hadd metadata smoke — [VERIFIED] PASS (with a caveat)
Inspected node-local ROOTs. The **authoritative** post-rebuild file
`/tmp/mnv101_active_pc_final_hadd.root` (single written 08:45, after the
08:40:45 rebuild) — duplicate hadd of the point-cloud active-lateral output:

| key | single | dup-hadd | expected |
|---|---|---|---|
| activeUniverseBand | BeamAngleX | BeamAngleX | invariant ✔ |
| hasActiveUniverse | 1 | **1** | invariant ✔ |
| activeUniverseIsLateral | 1 | **1** | invariant ✔ |
| activeUniverseIndex | 0 | 0 | invariant ✔ |
| activeUniverseRecoEntrants | 5 | **10** | additive ✔ |
| activeUniverseRecoExits | 2 | **4** | additive ✔ |
| nTruthOnlyMisses | 16791 | **33582** | additive ✔ |
| mc_truth_denom / mc_signal_reco | 65911 | 131822 | additive ✔ |

Confirms `'f'` merge preserves invariants while counters sum, on real event-
loop output. **Caveat / gotcha:** the `lat`/`cv`/`vert` single ROOTs were
written 08:33–08:35, *before* the 08:40 rebuild, so their invariant
`TParameter<int>`s carry the old default `'+'` merge → their hadd sums
`hasActiveUniverse`/`isLateral` to 2. This is a stale-artifact behavior of
pre-rebuild smoke files, **not** a defect in the installed binary. Do not use
`mnv101_active_lat_hadd.root` to judge merge behavior; use the pc_final files.

Point-cloud active-lateral content [RELAYED, consistent with inspection]:
appended misses have truth clouds + empty reco clouds + `sim_pass=false`;
signal/background/data vector-size gates pass.

### 1.4 PET bootstrap replica machinery — [VERIFIED] coherent & consistent
Traced the full statistical-replica chain (`pet/minerva_pet_dataloader.py`,
`pet_bootstrap.py`, `pet/extract_bootstrap_replica.py`,
`pet/sbatch_pet_bootstrap_replica.sh`):

- The MC Poisson draw is applied to the **full** `w_truth` array
  (`build_loaders` l.122, before the `--max-events` subsample l.128), using
  `default_rng(seed + 10_000_000).poisson(1.0, N)`.
- `--reweight-all` re-evaluates push weights on the full gen cloud
  (`max_events=None` → `imc = arange(N)`), so saved `mc_indices` is the ordered
  full range and `w_push` covers all N events.
- The saved `mc_bootstrap_factor = mc_poisson_factor(N, seed)[imc]` uses the
  **identical** draw (`default_rng(seed + 10_000_000).poisson(1.0, N)`), so the
  training draw and the extraction draw are one coherent per-event draw.
- `validate_full_replica_weights` re-derives that draw and rejects any
  seed mismatch, partial/unordered coverage, non-finite, or draw
  inconsistency → the invalid frozen-`w_push` `C_stat` cannot be rebuilt.
- Completeness is held at the fixed nominal GBDT anchor
  (`products/{4d,5d}/xsec_*_MEFHC_5iter_lgbm.root`), so replica-to-replica
  variation is purely statistical.

### 1.5 PET replica launcher review (item 5) — [VERIFIED] CLEAN
`pet/sbatch_pet_bootstrap_replica.sh`:
- Inputs present: `of_inputs_pc_fullcloud.npz` (6.5 GB), `of_inputs_5d.npz`
  (1.5 GB).
- Training config `niter=2, epochs=8, max-events=2 000 000` is **identical** to
  the nominal fullcloud train (`pet/sbatch_pet_train_fullcloud.sh:21`), so
  replicas reproduce the nominal footing (correct — vary only the bootstrap
  seed).
- Single-replica launcher (not an array); `REPLICA_ID` required + integer-
  validated; `set -eo pipefail` (avoids the conda-nounset trap); atomic strict
  4D + 5D NPZ extraction. Header explicitly gates ensemble runs behind
  approval.
- Minor note: `extract_bootstrap_replica.py`'s `--pc` default is `of_inputs_pc.npz`,
  but the launcher always passes `--pc "$INPUTS"` explicitly, so the default is
  never used. No action needed.

---

## 2. Changed-file inventory

**Remediation-owned — [VERIFIED] this session:**
- `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp` — active-
  universe mode (the `MNV101_DUMP_POINTCLOUD` background-cloud hunk in the same
  diff is **user-owned**, preserved untouched).
- `nd-unfolding/uq_math.py` *(new)* — asymmetric interpolation, MAT/joint
  covariance, projection, selection masks, finite-support mask.
- `nd-unfolding/unified_throw_cov.py` — strict combine (required
  `--expected-throws`, exact throw-id inventory, endpoint/flux-bank
  completeness, non-finite/duplicate rejection, no jitter subtraction).
- `nd-unfolding/replica_manifest.py` *(new)* — strict replica ingestion.
- `nd-unfolding/pet_bootstrap.py` *(new)*, `nd-unfolding/pet/extract_bootstrap_replica.py` *(new)*,
  `nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh` *(new)*.
- `nd-unfolding/pet/minerva_pet_dataloader.py` — coherent draw + `--estimator-seed`
  + `--reweight-all` full-coverage save.
- `nd-unfolding/tests/` *(new)* — `test_uq_remediation.py`, `run_inpipeline_nn_smoke.py`.
- `unbinned_unfolding/python/omnifold.py` — `import sys` fix.

**Remediation-owned — [RELAYED] (not re-read this session):**
- `nd-unfolding/pet_systematics.py`, `pet_systematics_5d.py`,
  `pet_lateral_band.py`, `pet_lateral_band_5d.py`,
  `eavailW_covariance.py`, `bootstrap_nd.py`, `combine_cov_nd.py`,
  `coverage_toy_nd.py`, `unfold_nd_omnifold_unbinned.py`,
  `seedscan_split.py`, `combine_seedscan_split.py`,
  `fps_3prior_envelope_5d.py`, `fps_gbdt_prior_reunfold_5d.py`.
- `nd-unfolding/sbatch_uthrow_combine{,_4d,_5d,_fps}.sh`,
  `sbatch_combine_{4d_statml,5d_budget,boot_fps,split_fps}.sh`,
  `run_4d_throws_interactive.sh`, `sbatch_fps_{hidden_closure,mefhc,pilot}.sh`
  (combine-side strict validation + fixed-seed wiring; spot-checked
  `sbatch_uthrow_combine_5d.sh` → adds `--expected-throws 0-159`, drops the
  jitter-subtraction language).
- Docs (methodology/qualification only): `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`,
  `docs/analysis-note/*.tex`, `values.tex`.

**NOT remediation — user / personal-account, leave alone:**
`2d-unfolding/uq/negweight_uni/`, `2d-unfolding/uq/purity_newomni/`,
`2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md`,
`nd-unfolding/products/pet/fps_envelope_5d{,_xps,_xps2}/`,
`nd-unfolding/sbatch_evloop_array_pointcloud_fps_bkgcloud.sh`,
`nd-unfolding/sbatch_hadd_pc_fps_bkgcloud.sh`,
`nd-unfolding/sbatch_fps_negweight_central.sh`, `pet-fps.json`, and the
`MNV101_DUMP_POINTCLOUD` background-cloud hunk in the C++ diff.

---

## 3. Tests — run vs. still-required

**Run & passing [VERIFIED]:** 16-test suite; ROOT metadata inspection of 6
active-universe smoke ROOTs. **[RELAYED] passing:** `xsec_nd.py` self-tests;
`py_compile` of the PET stack; `bash -n` of the launcher; `git diff --check`;
in-pipeline `omnifold.py` NN 1-iter (4 misses); PET bootstrap 5k-event smoke
(seed 7 reconstructs the coherent 32,849,103-event draw); C++ build+install.

**Still-required before quoting corrected uncertainties:**
- End-to-end PET replica extraction on a *genuinely complete small fixture*
  (the strict extractor rejects subsampled weights, so a training-only smoke
  cannot exercise the extractor path).
- A bounded active-universe event-loop smoke rebuilt entirely *after* the merge-
  mode edit for lat/cv/vert (pc_final already covers this; optional for full
  symmetry).
- The corrected covariance / PET-C_stat production runs themselves (§4) — none
  exist yet.

---

## 4. Rerun DAG (corrected uncertainty production)

None of the corrected UQ products exist yet. Stages, gates, and approximate
resources (walltimes are [RELAYED] order-of-magnitude, confirm before
submitting; **all sbatch below require explicit user approval**):

**Decision gate D0 — throw source.** The lateral systematic throws can come
from (a) the existing per-universe *bank* (`MNV101_DUMP_UNIVERSES` shadow
branches, CV-support-limited) now driven with fixed seed + asymmetric ±
interpolation, or (b) the new selection-complete active-universe event-loop
mode. Choose per band; (b) is required where CV-support truncation biases a
lateral band. This choice sets whether Stage 1 is a reweight-bank build or a
per-(band,idx) event-loop array.

1. **Throw inputs.**
   - (a) bank: regenerate/confirm `bank_uthrow_{4d,5d}` weight dumps.
   - (b) active: per-(band,idx) event loops via `MNV101_ACTIVE_UNIVERSE`,
     per-playlist then hadd (never a combined manifest — AGENTS.md flux trap).
   - *Gate:* fixed estimator seed logged; migration census non-zero for
     laterals, 0/0 for verticals.
2. **Per-throw unfold** → per-throw xsec slabs (`uthrow{,4d,5d}_slab_*.npz`)
   and matched block-endpoint slabs (`block*_*.npz`). Shared/regular QOS.
3. **Combine** → `unified_throw_cov{,_4d,_5d}.root` via
   `unified_throw_cov*.py --combine ... --block-slabs ... --expected-throws LO-HI --null`.
   *Gates (now enforced):* `--expected-throws` exact-inventory match; both knob
   endpoints + contiguous flux bank present; `--null` fixed-seed norm == 0.
4. **Adopt** (4D/5D): re-run the inflation-transfer adoption
   (`adopt_unified_*.py`) → adopted covariance; eigen-check PSD.
5. **PET C_stat.** Approved small replica ensemble via
   `sbatch_pet_bootstrap_replica.sh` (vary `REPLICA_ID`, hold estimator seed) →
   strict 4D/5D replica NPZs → `replica_manifest` → covariance. GPU shared QOS,
   ~O(hours)/replica. *Gate:* strict full-coverage validation passes for every
   replica.
6. **(Eavail,W) covariance.** Rebuild from the corrected projected-5D
   statistical covariance (`eavailW_covariance.py` + `project_covariance`).
7. **Budgets / significances / PET-vs-GBDT precision.** Recompute only after
   1–6 land; then refresh `values.tex` (single source of truth) and the ledger.

Every result must clear the AGENTS.md commit gate (ledger + RUN_LOG + STATUS
one-liner in the same commit) before it is quotable.

---

## 5. Claim table

| Claim / product | Disposition | Basis |
|---|---|---|
| Active-universe selection-complete mode is correct | **RETAIN** | [VERIFIED] §1.2–1.3 |
| PET bootstrap chain is coherent; strict extractor guards coverage | **RETAIN** | [VERIFIED] §1.4 |
| Unified-throw combine strict validation + fixed-seed null | **RETAIN** | [VERIFIED] §1.1, §2 |
| Asymmetric ± interpolation; MAT mean-centred 1/N comparator | **RETAIN (method)** | [VERIFIED] tests |
| Old unified/adopted 4D/5D/FPS covariances | **RECOMPUTE** | superseded by fixed-seed/asymmetric method; §4 |
| Old PET `C_stat`, total budgets, PET-vs-GBDT precision | **RECOMPUTE** | frozen-`w_push` invalid; needs §4.5 |
| (Eavail,W) covariance & derived significances | **RECOMPUTE** | needs corrected projected-5D input, §4.6 |
| Any significance derived from the above covariances | **QUALIFY→REMOVE until recomputed** | dependency chain |
| Phase-18.2 2D headline (σ_total, χ²/ndf, bin ratios) | **RETAIN** | unaffected by this remediation |

---

## 6. Explicitly UNQUOTABLE until §4 completes
Old unified/adopted/FPS 4D & 5D covariance products and every significance
built on them; old PET statistical covariance (`C_stat`), total error budgets,
and PET-vs-GBDT precision claims; (Eavail,W) covariance and its significances.
Do not quote numeric uncertainties from any pre-remediation UQ artifact in the
note, primer, paper, or a talk.

---

## 7. Proposed doc updates (methodology only — NO numbers, propose not apply)
- **KNOWN_ISSUES.md:** (i) frozen-`w_push` PET `C_stat` invalid — replicas must
  fully retrain; (ii) unified-throw combine requires `--expected-throws` +
  complete endpoint/flux bank; (iii) `--null` must be identically zero (no
  jitter subtraction); (iv) pre-rebuild active-universe smoke ROOTs sum
  invariant metadata under hadd (stale-artifact gotcha, §1.3).
- **docs/OPEN_ITEMS.md:** add the §4 rerun DAG as the live to-do; mark the old
  UQ products unquotable-pending-recompute.
- **analysis note (all three builds):** state the asymmetric ± interpolation,
  fixed estimator seeds, mean-centred joint covariance with the mean shift
  reported separately, the MAT 1/N comparator from actual ± re-unfolds, and the
  no-jitter-subtraction/no-auto-inflation prescription — qualitatively, with no
  regenerated numbers. Preserve all spelling-only user edits already present.

---

## 8. Meta-deliverables (available on request)
A clean blind-audit prompt (no candidate defects revealed), a per-fix
"try to disprove this" verification prompt for a second model, and an interim-
presentation disclaimer were requested in the handoff. They are separable from
the technical record above; say the word and I'll draft them. A ready
disclaimer line for any interim talk:

> "Systematic and statistical uncertainty covariances are being regenerated
> under a corrected fixed-seed / fully-retrained prescription; all uncertainty
> magnitudes shown are provisional and not for citation."
