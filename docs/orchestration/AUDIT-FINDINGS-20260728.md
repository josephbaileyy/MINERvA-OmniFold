# Audit findings — full-event PET path (2026-07-28)

Audit basis: local read-only checkout at `054cb3b`. `python3 docs/orchestration/verify_hash_bindings.py`
→ `88 OK / 4 known drift / ALL BINDINGS INTACT` at the time of writing. No file was
edited, no job was submitted or touched (Delta `20558496` left alone), no compute was run
on a login node.

---

## 1. Honest assessment: what state is the full-event PET path actually in?

**It is a code-complete, gate-decorated path that has never produced a physics number, and
the gates that decorate it certify substantially less than their names imply.**

Three things are simultaneously true:

1. **The path cannot currently run to completion.** `RESTORE-2026-08-03.md` Step 3 (the
   ordinary closure) and Step 4 (the nominal) both reach
   `learned_stay_positive_refiner()`, whose import target is not on `sys.path` for either
   driver (B4). Even if that is fixed, the artifact the driver writes cannot be consumed by
   the only extractor in the repo — wrong key name, and a 2M subsample where the extractor
   requires ordered coverage of all 49.15M rows (B3). So the sequence
   *train → validate → extract* has no working end.
2. **If it did run, the absolute cross section would be the prior's.** Both full-event
   `DataLoader`s are built with `normalize=True`, which forces each step-1 class to sum to
   1e6 and destroys the POT-scaled data-vs-MC rate difference before training. Nothing
   multiplies it back — unlike the reference loop, which explicitly does (B1). This is a
   quantitative, testable explanation for the ~10% PET/GBDT normalization gap the run log
   currently attributes to under-iteration.
3. **No gate would catch either.** The Gate-4 CLI validator computes *none* of the four
   physics checks its own receipt advertises, and four of its six freeze checks compare
   `FROZEN` against `FROZEN` (B2). Independently reproduced: it returns `verdict PASS`,
   `n_failed 0` on an artifact whose push weights are pure noise.

The positive findings are real and worth stating: the Gate-2 canonical-runtime receipt is
a genuine measurement on the real 49.15M-row dump, its signed-sum identities hold to
2.4e-07, and it independently **refutes** known finding B for the frozen configuration
(§4, M12) and **confirms** known finding A. The frozen-file discipline is working — no
binding has drifted since the `2732304` incident. What is missing is not discipline; it is
*power*: almost every check in the full-event chain is a structural identity, a
self-comparison, or a statistic that is maximized by a broken estimator.

Confidence note: findings whose verdict is marked *code-reading* below were confirmed by
opening the cited lines but could not be executed, because the only real full-event input
is on unreachable `/pscratch`. Findings marked *reproduced* were executed locally.

---

## 2. BLOCKS the publication nominal

### B1. `normalize=True` on both full-event loaders makes the unfold shape-only; the absolute d²σ inherits the GENIE prior's normalization

*Dimension: unfolding. Verdict: mechanism confirmed by code reading; magnitude unverified.*

**Claim.** `build_fullevent_loaders` passes `normalize=True` for the MC loader
(`nd-unfolding/pet/fullevent_fps_dataloader.py:613`) and for the negweight-refined measured
target (`:658`). `omnifold_nn/omnifold/dataloader.py:110-113` then rescales each loader's
weights so `sum(weight[pass_reco]) == normalization_factor` (1e6). The vendored step-1
classes are weighted by exactly those sums
(`omnifold_nn/omnifold/omnifold.py:176-177`: `class0 = weights_push*mc.weight*mc.pass_reco`,
`class1 = data.weight*data.pass_reco`), so at iteration 0 the class-weight ratio W1/W0 is
identically 1 and the physical rate difference is gone before any training. Nothing
restores it. `nd-unfolding/pet_systematics_5d.py:153-163` then computes the absolute cross
section as `sum(w_push*w_truth)/(completeness*flux*data_pot*n_nucleons)` with **no**
anchor to the measured yield.

This is not the convention used for the validated 2D/3D result. The reference loop
(`nd-unfolding/omnifold_nn_core.py:254-258`) feeds step 1 raw POT-scaled weights, and where
it does balance classes it explicitly restores the ratio — `_class_ratio` /
`_balance_weights` at `omnifold_nn_core.py:158-186`, whose own comment says otherwise
*"the unfolded normalization collapses"*. The PET path does the balancing and skips the
multiply-back.

**Failure scenario.** P5A completes post-restore. The extracted d²σ/dp_T dp_∥ total sits
within ~2% of the POT-scaled GENIE prior while the validated GBDT chain on the same data
shows a ~13.5% excess (`ND_OMNIFOLD_RUN_LOG.md:935`, data/CV = 1.135). The ~10% gap is
published or discovered late as an unexplained "PET/GBDT normalization gap" — the run log
already records it twice (`:473` ratio 0.9117; `:913` 0.8970) and at `:919` notes the
higher-iteration retrain was "essentially flat", i.e. **not** iteration-limited, which is
the signature this finding predicts. No gate catches it: `gate2_target_runtime.py:411-412`
and `:442-443` positively *assert* the step-1 target sums to exactly 1e6, and
`validate_pet_nominal_gate4.py:107-110` requires `|sum(w*push)/sum(w) - 1| <= 1e-3` — i.e.
the Gate-4 contract as written would FAIL a correctly normalized unfold and PASS the
shape-only one.

**Minimal check** (login-safe, no GPU, post-restore). Read only the scalar/1-D members of
`G2_FPS_MEFHC_P12.npz` (`w_truth`, `pass_reco`, `w_bkg`, `pot_scale`, measured row count)
and compute `R = (n_data - pot_scale*sum(w_bkg)) / sum(w_truth[pass_reco])`. If R ≈
1.09-1.10, the erasure quantitatively accounts for 0.9117/0.8970 and the cause is the
convention, not under-iteration.

**Frozen.** Yes. Dropping `normalize=True` voids the Gate-2 canonical-runtime receipt
(`G2_GATE2_TARGET_RUNTIME_RECEIPT.json` `code.loader`), and because the same receipt binds
`gate2_target_runtime.py` — whose 1e6 assertions at `:411-412`/`:442-443` would also have
to change — it is a **two-file re-issue plus a Gate-2 canonical-runtime re-run on the real
dump**. The alternative needs no frozen edit: keep shape-only and add an explicit
data-yield normalization to the extraction step, documented in `sec_method` as a deliberate
convention. **Decide which, explicitly, before P5A launches.**

---

### B2. The Gate-4 CLI validator evaluates none of its four physics checks, self-compares four of its six freeze checks, and returns PASS on pure noise

*Dimensions: unfolding, closure-power, code-integrity — **three independent dimensions
found this**. Verdict: reproduced.*

**Claim.** `nd-unfolding/pet/validate_pet_nominal_gate4.py:223-229` calls
`build_gate4_report` without `marginal=`, `normalization=`, `saturation_frac=` or
`closure=`, and `build_gate4_report` (`:169-176`) silently *skips* every component whose
argument is `None`. `:221-222` builds `frozen_observed` by copying `FROZEN['edges_pt']`,
`FROZEN['edges_pparallel']`, `FROZEN['bin_order']` and `FROZEN['seed_policy']` into the
"observed" dict, so `check_freeze` (`:133-143`) compares FROZEN to FROZEN. Because
`frozen_observed` also carries no `central_vector` or `reported_bin_mask`, the checks at
`:146-152` never run either — the 266/285 reported mask is untouched by the gate.

What actually executes: fingerprint, bkg_mode, four self-comparisons, weight
finiteness/non-negativity/non-emptiness/coverage-against-`len(imc)`, and index sortedness.
**15 checks, 0 failed, verdict PASS** on an npz whose `weights_push` is `|N(1,0.3)|` random
noise — reproduced. The emitted receipt nonetheless embeds
`frozen_contract.tolerances = {marginal_l1_max: 0.1, push_median_dev_max: 0.15,
normalization_dev_max: 0.001, cap_saturation_frac_max: 0.001}`, so a reader reasonably
concludes they were met.

Compounding: the iteration count is **not recoverable from the artifact**.
`train_fullevent_nominal.py:134-137` persists only `weights_push, mc_indices,
estimator_fingerprint, bkg_mode, tag, target` — no niter, epochs, seeds, input path or
input sha256. `freeze:seed_policy` is therefore unfalsifiable by construction. And a grep
for `target`/`refinement` over the validator returns **zero hits**: `z['target']` — the
sole carrier of `refinement_is_learned_production`, `refined_sum`, `pot_scale` and
`signed_target_hash` — is never read, even though the driver writes it.

Test power is nil: every test in `nd-unfolding/tests/test_pet_nominal_gate4_validator.py`
calls `check_freeze`/`build_gate4_report` directly with all arguments supplied
(`:23-42`); `test_freeze_seed_policy_tamper` (`:63-65`) proves the *function* rejects a
tampered policy, but the shipped CLI never feeds it one. The only test touching the CLI
module as shipped is `test_byte_compiles` (`:202`).

**Failure scenario.** The nominal is launched with `--niter 1 --epochs 2` (both plain CLI
args at `train_fullevent_nominal.py:97-98`, cross-checked against nothing). The validator
emits `verdict PASS` with `frozen_contract.seed_policy = {niter: 2, epochs: 8,
train_events: 2000000}` regardless of what ran. The Gate-4 receipt attests a configuration
that was never used, and no test fails.

**Minimal check** (zero cost, runnable now). Run the validator on two artifacts produced
with deliberately different `--niter`; the receipts are byte-identical apart from the result
sha256. Then hand-build `{weights_push: ones(1000), mc_indices: arange(1000),
estimator_fingerprint: 'pet-fullevent-fps-v1', bkg_mode: 'negweight-refined'}` and confirm
PASS.

**Scoping honesty.** Grep finds no caller of this validator outside its own test and two
doc/receipt mentions, and no runbook supplies `--nominal-weights`. So nothing is
*currently* mis-certified; the defect bites at P5A validation time.

**Frozen.** Yes — `docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260721.json`
binds the validator (`0cb4b41d…`) and the driver (`aa9f66a8…`). The fix set (driver
persists niter/epochs/seeds/input-sha; validator reads edges/bin_order/seed_policy/
`target.refinement_is_learned_production`/`signed_target_hash` **from the artifact**;
`build_gate4_report` FAILS rather than skips on `None`) is a **Gate-4 launch-code-gate
re-issue and re-run**. Its 14+36 tests are login-safe — no GPU, no data — so the re-run is
cheap and should be done regardless of the 08-03 window.

---

### B3. The nominal artifact cannot be extracted: wrong weight key, and a 2M-of-49.15M subsample where the extractor requires ordered full coverage

*Dimension: unfolding. Verdict: code-reading, both sides read.*

**Claim.** `train_fullevent_nominal.py:134-137` writes
`np.savez_compressed(out, weights_push=..., mc_indices=imc, ...)`. Two independent
incompatibilities with the only nominal extraction path:

1. **Key name.** `nd-unfolding/pet/extract_nominal_bkgsub.py:63` requires `"w_push"` and
   raises `SystemExit("[FAIL] … missing w_push/mc_indices")` otherwise.
2. **Coverage.** `of.weights_push` has length `max_events` = 2,000,000
   (`train_fullevent_nominal.py:37`, launcher `TRAIN_EVENTS=2000000` at
   `sbatch_pet_fullevent_nominal.sh:54`) while `imc` is a sorted random subset of the
   49,152,885-row inventory. `extract_nominal_bkgsub.py:69-72` requires
   `wp.size == idx.size == n_events` **and** `mc_indices == arange(n_events)`, failing with
   *"mc_indices not the ordered full-sample range (need --reweight-all)"*. The driver
   implements no `--reweight-all` step, although the frozen feature contract's launch order
   specifies one: `FULL_EVENT_FEATURE_CONTRACT.md:248` — *"NOMINAL: … MultiFold (2M
   subsample, niter2/epochs8, est-seed 42, reweight-all on full 49.2M)"*, repeated at
   `PET_P1_P5_SESSION_STATE.md:90`.

**Silent-corruption branch.** If the key is renamed by hand to route around (1),
`nd-unfolding/pet_systematics_5d.py:100-107` zero-fills `w_push` outside `mc_indices`
(`full = np.zeros(N); full[idx] = wp`), so ~95.9% of the MC enters the histogram at weight
0 and the total cross section comes out at roughly 4% of truth **with no error raised** —
because the guard that would have caught it (`validate_nominal_weights`) was the thing
bypassed by the rename.

Gate-4 passes the subsample artifact regardless: `check_mc_index_order`
(`validate_pet_nominal_gate4.py:81-91`) only requires sorted/unique/in-range, and
`check_weights_finite_coverage` is called with `n_expected = len(imc)` (`:163-168`), i.e.
coverage is compared against the subsample's own length.

Confirmed by directory listing that **no full-event cross-section extractor exists** —
`nd-unfolding/pet/` contains only `extract_nominal_bkgsub.py`,
`extract_bootstrap_replica.py`, `phase7_extract_compare.py`, all on the recoil 5D bkgsub
path.

**Failure scenario.** P5A is authorized post-restore, burns ~1.1-1.3 h GPU plus the matched
floor repeat, Gate-4 emits PASS, and extraction aborts on the missing key. Under time
pressure the key is renamed; the extraction then silently returns σ ≈ 4% of truth.

**Minimal check** (zero cost, runnable now, off-cluster). Build a fake npz with
`weights_push` of length 2,000,000 and
`mc_indices = np.sort(rng.choice(49152885, 2000000, replace=False))`; run the Gate-4
validator (expect PASS), then `extract_nominal_bkgsub.py --weights fake.npz …` (expect
`SystemExit`).

**Frozen.** Either route touches frozen code. Adding reweight-all + the `w_push` key to the
driver, and tightening `check_mc_index_order` to require `arange` coverage, are both a
**Gate-4 receipt re-issue and re-run**. Writing a *new* full-event extractor that accepts
the subsample contract explicitly needs no frozen edit and may be the cheaper path — but
the Gate-4 coverage check must still be tightened, so plan the re-issue either way.

---

### B4. The canonical Stay-Positive refiner is unimportable from **both** publication-path drivers: `<repo>/2d-unfolding` is never put on `sys.path`

*Dimension: code-integrity. Verdict: reproduced locally.*

**Claim.** `fullevent_fps_dataloader.py:306` does a bare
`from unfold_2d_omnifold_unbinned import refine_stay_positive`, but that module exists only
at `2d-unfolding/unfold_2d_omnifold_unbinned.py:409`. The loader's own path block
(`fullevent_fps_dataloader.py:40-43`) inserts **only** `{_REPO}/omnifold_nn` and
`{_REPO}/nd-unfolding`. `train_fullevent_nominal.py:24-28` inserts `_HERE`,
`nd-unfolding`, `nd-unfolding/pet`. `closure_fullevent_fps.py:41-44` inserts
`omnifold_nn`, `_ND`, `_HERE`. None adds `2d-unfolding`.
`sbatch_pet_fullevent_nominal.sh` sets no `PYTHONPATH` and `setup_salloc_env.sh` sets none.

The only caller that works is `gate2_target_runtime.py`, which inserts
`REPO/"2d-unfolding"` explicitly at `:357` — direct proof the entry is required and is not
present by default. That is why the Gate-2 receipt could record
`refinement_is_learned_production=True` while the Gate-4 path has never been exercised.

Reproduced locally with `sys.path = [nd-unfolding/pet, nd-unfolding, omnifold_nn]`:
`ModuleNotFoundError: No module named 'unfold_2d_omnifold_unbinned'`.

Test power: the only test touching it, `tests/test_fullevent_gate2.py:301-303`, asserts
`callable(fed.learned_stay_positive_refiner)` and deliberately never calls it; the shared
fixture helper at `:99` does `kw.setdefault("refine_fn", sklearn_refine)`, so every loader
test injects the shim and the default path has **zero** coverage. The Delta dryrun likewise
injects `sklearn_refine` and runs the closure with `--bkg-mode purity`, which returns at
`fullevent_fps_dataloader.py:625` before the refiner.

**Failure scenario.** `RESTORE-2026-08-03.md` Step 3 — the *first* item on the post-restore
critical path — loads the 9.9 GB NPZ, verifies identities, builds the reco+truth clouds
**and the full 4.68M-row measured/background clouds** (`:629-641`), then dies at `:647` →
`:306`. Same crash for Step 4, after the config gate has already printed PASS. Minutes-to-
hours of the restore window burned on a two-line path bug — and the temptation on the spot
is to inject a shim, which silently yields `refinement_is_learned_production=False`, which
per B2 the Gate-4 validator would still stamp PASS.

**Likely second blocker on the same line.** `unfold_2d_omnifold_unbinned.py:21` does an
unguarded module-scope `import ROOT`, while `sbatch_pet_fullevent_nominal.sh:105-106`
sources `setup_salloc_env.sh` (root_6_28 conda prefix) and *then* `module load
tensorflow/2.15.0`, so the interpreter that runs the driver at `:109` is the TF-module
python, which very probably has no ROOT bindings. The Gate-2 receipt is consistent with
this: `environment.tensorflow = "not imported/not required"`, python 3.11.14 — the one time
the canonical refiner ran, it ran in a ROOT-capable, TF-free interpreter. **Fixing
`sys.path` alone may not clear the path.** Check both on the same node visit.

**Minimal check.** Now, off-cluster:
`python3 -c "import sys; sys.path.insert(0,'nd-unfolding/pet'); import fullevent_fps_dataloader as fe; fe.learned_stay_positive_refiner()"`
→ expect `ModuleNotFoundError`. On Perlmutter, first thing:
`module load tensorflow/2.15.0 && python3 -c "import ROOT, sys; print(sys.executable)"` and
`python3 -c "import sys; sys.path.insert(0,'2d-unfolding'); import unfold_2d_omnifold_unbinned"`.

**Frozen.** All three natural fix sites are bound. `closure_fullevent_fps.py` is
**known-not-frozen** and free to edit, which covers Step 3 but *not* Step 4. For the
nominal, the zero-gate-cost route is `export PYTHONPATH=$REPO/2d-unfolding:$PYTHONPATH`
supplied from the submit environment or in `setup_salloc_env.sh`, which is bound by no
receipt and is sourced at `sbatch_pet_fullevent_nominal.sh:105`, before the training body.
Editing the launcher or driver voids the **Gate-4 launch-code gate**; editing the loader's
path block voids the **Gate-2 receipt (two-file re-issue, needs the real dump)**.

---

### B5. `niter=2` is hardcoded with no stopping criterion and no convergence evidence, contradicting the documented production method and the repo's own diagnosis

*Dimension: unfolding. Verdict: code-reading.*

**Claim.** The publication nominal fixes `niter=2` in three places:
`train_fullevent_nominal.py:36-37` (`NOMINAL_SEED_POLICY`), `sbatch_pet_fullevent_nominal.sh:52`
(`NITER=2`), and `validate_pet_nominal_gate4.py:55-56` (`FROZEN['seed_policy']`). There is
no stopping criterion of any kind: `MultiFold.Unfold` (`omnifold_nn/omnifold/omnifold.py:161-166`)
is a bare `for i in range(self.start, self.niter)` with no weight-change, pull-vs-push or
held-out convergence test, and no per-iteration weight snapshot is saved.

`niter=2` is below the vendored default of 3 (`omnifold.py:55`), below the ≥5 the repo's
own literature notes call typical (`LITERATURE_NOTES.md:66-70`), below the n=5 the analysis
note declares as the production count and justifies empirically
(`docs/analysis-note/sec_method.tex:98-100, 139-141`), and below the frozen recoil-only PET
recipe (`--niter 5`, `PET_TRAINING_ON_DELTA.md:15`). The run log diagnoses this exact
configuration as under-iterated (`ND_OMNIFOLD_RUN_LOG.md:476-478`).

**The justification does not transfer.** `sec_method.tex:94-97` justifies few iterations
because *"our prior already describes the data shapes well … and the data pull is
dominantly a normalization"* — but per B1 the PET path **discards precisely that
normalization pull**, leaving only the shape pull, which is the part that needs iterations.

No niter sweep or iteration-stability tool exists for the full-event path. The only
iteration-stability number in the repo (0.026% for 5→10) belongs to the 2D GBDT chain.
Neither `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md`, `docs/PUBLICATION_COMPLETION_RUNBOOK.md`
nor `PET_UQ_REMEDIATION_STATUS.md` mentions the full-event iteration count at all.

**Failure scenario.** The residual data-vs-prior *shape* pull in (p_T, p_∥) is only
partially applied, biasing the reported double-differential shape toward GENIE in exactly
the extrapolation cells the extended-FPS grid exists to expose. Because the ordinary closure
is insensitive by construction (M2), the stress closure runs at `niter=3` on synthetic
clouds, and Gate-4 records the iteration count from its own constant rather than the
artifact (B2), nothing in the repo distinguishes this from a converged result.

**Minimal check** (post-restore, ~2 × 1.1-1.3 h GPU per `FULL_EVENT_FEATURE_CONTRACT.md:248`).
Run the nominal at `--niter 2` and `--niter 5` with identical seeds (est 42, sub 0,
epochs 8, 2M) and compare the `pass_truth`-binned spectrum on the 285-cell FPS grid:
report L1/sum and per-bin max|Δ|. **Predeclare the acceptance bar before looking** — the
recoil floor work gives a scale (10M-vs-40M training-statistics bar 4.4833%, GPU-nondeterminism
floor 0.2060%, `ND_OMNIFOLD_RUN_LOG.md:2200-2210`).

**Frozen.** Yes. Changing niter in the driver or validator voids
`p3f-pet-gate4-launch-code-gate-20260721.json` → **Gate-4 re-issue and re-run**. Note the
sweep itself needs no frozen edit (`--niter` is a CLI arg); only *adopting* a different
nominal does.

---

## 3. Should fix eventually

Ordered by severity within this tier. None of these alone stops a number from being
produced, but several make an existing PASS mean less than it reads.

### M1. Gate-2's `/1000.0` collapses all 285 cells into cell (0,0); the "independent" validator repeats the identical error

*Dimensions: negweights, closure-power, binning-leakage — **three independent dimensions
found this**. Verdict: CONFIRMED, and settled from repo-local evidence alone.*

The open units question is **closed, against the `/1000`**.
`gate2_target_runtime.py:421-422` divides `measured_scalars`/`bkg_reco_scalars` by 1000.0
before histogramming against `CANONICAL_PT_EDGES`/`CANONICAL_PPARALLEL_EDGES`, but the
scalars are already GeV: `dump_pointcloud_inputs.py:62-63` declares
`FPS_PT_LO/HI = 0.0, 30.0  # GeV` and `FPS_PZ_LO/HI = 0.0, 120.0  # GeV`, `:76` labels the
scalar branches "(GeV)", and `in_fps_domain` (`:126-129`) gates the **raw** branch values
against that box for signal, data (`:377`) and background (`:424`) — 4,116,128 data rows
survived, impossible under an MeV hypothesis. Corroborated by
`validate_g2_fullevent_domain.py:40-41,62,236-237` (asserts scalar == MeV four-vector/1000),
by `G2_MEFHC_DOMAIN_VALIDATION.json` (`in_domain_scalar_muon_mismatch = 0` for all three
inventories at ROOT level), and by `floor_gpu_nondeterminism.py:90,102-104` histogramming
the same scalars against the same edges with **no** `/1000` and getting 266 populated bins.

Arithmetic: max p_T/1000 = 0.030 < first p_T edge 0.07; max p_∥/1000 = 0.120 < first p_∥
edge 0.75. Every row lands in cell (0,0). The receipt proves it happened:
`learned_vs_normalized_clipped_l1_fraction` and `_max_relative` are bit-identical at
`3.7792752997484056e-07`, which is exactly
`(learned_refined_normalized_sum 1000000.37792753 − 1e6)/1e6`; `cosine = 1.0` exactly;
`negative_signed_cells = 0`. The binned check reproduces the sum check already made at
`:442`.

`validate_gate2_target_receipt.py:107-108` copies the same `/1000.0`, so the "independent"
validation is not independent of this error — at `:151-156` it merely requires
bit-agreement (rtol 5e-12) with the recorded telemetry, i.e. it confirms the numbers were
copied, not that they mean anything.

**Consequence.** The learned-vs-closed-form shape metrics — per M7 the only diagnostic that
separates a correct Stay-Positive refinement from a degenerate one — are structurally
incapable of registering anything. A one-cell histogram is also invariant under **any
permutation** of `w_refined` within or across the data/background blocks, so a refiner
returning the right multiset in the wrong row order is certified PASS (see M7).

**Severity is major, not blocker**, for a reason worth stating: the `/1000` exists **only**
in the validator's binned check. The loader's `_scale_clean`
(`fullevent_fps_dataloader.py:89-91`) applies `/1000` to `part_*` clouds only, and
`build_event_features` z-score-normalizes the scalars with no unit rescale. **No weight,
target, normalization or physics number is misscaled** — what is lost is the evidentiary
value of one check. `gate2_target_runtime.py:523-526` also explicitly labels these metrics
"decision telemetry, not an invented equality threshold" and applies no threshold, so the
Gate-2 PASS never rested on them; the hard gates are the signed-sum identities at
`:411-412`, `:438-439`, `:442-443`, which are invariant to a uniform rescale.

**Trap in fixing it.** On the correct grid `negative_signed_cells` will very likely be > 0,
which flips `validate_gate2_target_receipt.py:159` (`require(negative_signed_cells == 0)`)
to BLOCK. That is the check being wrong, not the physics — clipping cells where POT-scaled
background exceeds data is exactly what eq. 6 prescribes. Whoever fixes the units must
respecify that requirement **in the same change** rather than reverting the units. (Note:
whether any cell actually goes net-negative is empirical — background is 2.66% of data
globally — so do not pre-commit to `> 0` as an assertion either.)

**Minimal check.** Post-restore:
`python3 -c "import numpy as np; z=np.load(NPZ); print(np.percentile(z['measured_scalars'][:,:2],[0,50,100],axis=0))"`
→ GeV gives ~[0, 0.5, 30] / [0, 5, 120]. Then re-run `gate2_target_runtime.py validate`
with `:421-422` as `[:, :2]` (no `/1000`) and report `occupied_cells`,
`negative_signed_cells`, `l1_fraction`, `max_relative` against the published
`G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` (670 s, CPU-only).

**Frozen.** Yes — `gate2_target_runtime.py` and `fullevent_fps_dataloader.py` are bound
together by `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`: a **two-file re-issue and a Gate-2
canonical-runtime re-run on the 9.9 GB NPZ**. `validate_gate2_target_receipt.py` is not in
the frozen map, but fixing it alone breaks its own `:151-156` bit-agreement against the
frozen receipt, and its state JSON
`docs/orchestration/state/g2-gate2-runtime-independent-validation-20260719.json` must be
re-issued too. `RESTORE-2026-08-03.md` Step 2 already reserves this work — but its stated
procedure ("run it against the real dump to answer the units question") is now
unnecessary: **the units are decided offline, today.** Only the *re-validation* needs the
dump.

### M2. The ordinary closure is maximized by a broken estimator, discards the entire measured target, and drops its own normalization criterion from the verdict

*Dimensions: unfolding, closure-power (three separate findings merged). Verdict: CONFIRMED.*

Three defects in one script, all mutually reinforcing.

**(a) Structural zero power — input-independent.** The known-weak claim (run log;
`RESTORE-2026-08-03.md:180-188`) is that the 2026-07-26 closure had near-zero power
*because it ran on a synthetic fixture*. That understates it.
`closure_fullevent_fps.py:113-115` builds
`pdata = DataLoader(reco=reco[pr], weight=np.asarray(mc.weight)[pr], normalize=True,
reco_evt=reco_evt[pr])` — literally the same rows with the same weights as the MC loader's
`pass_reco` subset, both renormalized to 1e6. Step 1 is trained to separate a sample from
itself; the Bayes-optimal solution is p = 0.5, logit = 0, and `omnifold.py:466` gives
`w = exp(clip(logit)) = 1` exactly. Both pass criteria at `:141-142` are then attained at
their optimum: marginal L1 = 0 < 0.10 and `|median(push) − 1|` = 0 < 0.15. **An estimator
that has learned nothing — a diverged net collapsed to a constant, a silently detached FiLM
event branch, an untrained clone — produces a perfect closure score, and the PASS metric
improves monotonically as the estimator gets worse.** Re-running against the real G2 dump
restores provenance but *not* power.

Corollary (found independently): corrupting the truth-side MC weights is also invisible.
Replacing `w_truth = w_truth_full[imc]` (`fullevent_fps_dataloader.py:608`) with ones —
unfolding from a flat prior instead of GENIE — cancels exactly in the L1 statistic, because
`:132-134` weights `H_truth` by `wt` and `H_rw` by `wt*push` from the *same* corrupted
`mc.weight`. Mutation-tested: zero behavioural test failures. Partial coverage does exist —
`fullevent_fps_dataloader.py:585-591` `_verify_stored_identity` binds the *read* of
`(w_truth_full, pass_truth)` from the dump — so what is unbound is only the
`w_truth_full[imc]` → DataLoader hand-off.

**(b) The negweight-refined measured target is built and thrown away.**
`closure_fullevent_fps.py:100` binds `data` from `build_fullevent_loaders` and never
references it again (verified by grep: the only later occurrences of the token are
`--data-scalars`, `a.data_scalars`, `pdata`, a docstring and an f-string). The closure
therefore exercises **none** of the measured half: the learned Stay-Positive refinement's
values, data/background row alignment, `event_bkg`'s normalization, or the literal
background injection reaching step 1. Cost of the discarded work, from the Gate-2 receipt
on the real dump: `loader_and_full_refinement_seconds = 670.98` and a 4,680,719-row learned
refinement — at `--max-events` defaulting to 12000. Gate-4 nonetheless composes this as
check `closure:ordinary_pass` (`validate_pet_nominal_gate4.py:119-126`), described as
proving the estimator "does NOT move when it should not".

Calibration: `--bkg-mode` is not *only* a log tag. It selects which fail-closed guards run
inside the loader (`:560-578` background presence and `pot_scale > 0`;
`refine_signed_measured:354-360` length/finiteness/non-negativity), so a wrong `pot_scale`
sign *would* raise. What is genuinely uncovered is the refinement's **values**, row
alignment, and `event_bkg` normalization.

**(c) The normalization criterion is computed, printed, then dropped.** `:139-140` computes
`norm_ok = |sum(w*push)/sum(w) − 1|` and prints it; `:141-142` builds `ok` from L1,
`|median(push) − 1|` and finiteness only — `norm_ok` never enters the verdict (grep: the
token appears at `:139` and `:140` and nowhere else). And the L1 at `:135` is computed on
histograms each divided by its own sum, so it is normalization-blind *by construction* —
which is precisely why a separate norm criterion was written. Gate-4's CLI never applies
its frozen `normalization_dev_max = 1e-3` either (B2). So the criterion exists in three
places and is enforced in none.

*Do not* quote the 0.0015 value from the 2026-07-26 log as "already violating the 1e-3
bar": that run was a 12,000-row synthetic fixture in `bkg_mode=purity`, tagged
`[SYNTHETIC FIXTURE - PLUMBING ONLY, NOT THE P5A RECEIPT]`, and harvesting it as physics
evidence is exactly what HARD BAR 4 forbids.

**(d) Configuration mismatch.** Closure defaults are `niter=2/epochs=6/max-events=12000`
(`:61-62`) against the nominal's `niter=2/epochs=8/max-events=2000000` — a 167× smaller
training set and a different epoch budget. Even a fully restored closure receipt does not
certify the nominal's configuration.

**Failure scenario.** On 08-03 the closure is re-run against the real dump, prints
"ORDINARY CLOSURE PASS" with L1 ≈ 0.00x, and the P5A closure receipt is re-issued. Weeks
later the nominal is found to have trained a step-1 net whose event-feature branch
contributes nothing; the closure would have reported its *cleanest possible* PASS in
exactly that case, and because the receipt is green the defect is not looked for.

**Minimal check / fix** — all in `closure_fullevent_fps.py`, which is **known-not-frozen
and free to edit** (zero gate cost):
1. Negative control: add `--null-estimator` that skips `of.Unfold()` and sets `push = 1`,
   and assert the closure **PASSES** — documenting in the receipt that the test cannot
   distinguish a null estimator from a correct one.
2. Real power: inject a known truth-level reweight into the pseudo-data (machinery exists —
   the 2D gaussian-bump and 3D E_avail-bump closures, `LITERATURE_NOTES.md:145-162`) and
   require recovery with residual/injected ≪ 1 (the 2D/3D closures achieve 0.098/0.102).
   Run at the **nominal** niter/epochs/max-events.
3. Feed the real `data` loader to MultiFold, or delete the discarded build and pass
   `--bkg-mode purity` explicitly — and stop letting Gate-4 present this closure as
   evidence about the negweight-refined target.
4. `ok = … and (norm_ok < a.norm_tol)` with `--norm-tol` defaulting to 1e-3.
5. A second statistic comparing `H_truth` built from the **raw input** `w_truth` against
   `H_truth` from `mc.weight`, so a weight substitution cannot cancel.

### M3. The test suite is blind to every behaviour-changing mutation in the frozen loader; only the sha256 binding notices, and it fires identically for a comment

*Dimension: closure-power. Verdict: CONFIRMED, including on a Perlmutter-equivalent copy.*

Seven independent semantic mutations to `fullevent_fps_dataloader.py` each produced exactly
one extra failure — `test_hash_bindings.py::test_no_new_broken_hash_bindings` — and no
other: **M1** `:608` `w_truth = w_truth_full[imc]` → `ones_like` (flat prior); **M2** `:337`
`np.vstack([fd, fb])` → `[fb, fd]`; **M3** `CANONICAL_PT_EDGES` 0.47 → 0.45 (`:48`); **M4**
`:123` truth-cloud kinematics no longer through `_scale_clean` (truth cloud left in MeV
while reco is GeV); **M5** `:123` px/py swapped; **M7** `:612-613` `reco_evt`/`gen_evt`
swapped on the MC DataLoader — *direct truth leakage*, and `assert_no_truth_leakage` runs at
`:547`, **before** the DataLoader construction, so it cannot see it. Only **M6**
(`build_reco_cloud` `coord_idx (1,2)→(0,1)`, `:98`) was caught, by
`test_fullevent_fps.py:47`.

The obvious objection — that 6 of the 7 baseline failures are the only tests driving
`build_fullevent_loaders` end to end, so an off-Perlmutter run under-measures — was closed:
a Perlmutter-equivalent copy (hardcoded `REPO` literals repointed at the scratch checkout)
gave a 339-passed baseline with all six end-to-end tests green, and **all seven mutations
reproduced the same result there**. The blindness is not a platform artifact.

A sha256 binding cannot distinguish a units bug from a whitespace edit, and it is precisely
the check that a legitimate gate re-issue deliberately refreshes. **During the planned
Gate-2 two-file re-issue (M1), the loader has effectively zero behavioural test coverage.**
This is the `2732304` failure mode with the polarity reversed: last time the edits were
inert and the hashes moved; next time the hashes move legitimately and the edits are not
inert.

**Fix** — four assertions, all in `nd-unfolding/tests/`, which is **not hash-bound**, so
zero gate cost. Each maps to one mutation above:
- `mc.weight` ∝ `w_truth[imc]` (normalize only rescales), `!= w_reco * k`, `std > 0` → M1
- `mc.reco_evt` equals `event_reco`, not `event_truth` → M7
- `feat[:n_data]` equals `refine_feat_data` row-for-row and `feat[n_data:]` equals
  `refine_feat_bkg` → M2
- `CANONICAL_PT_EDGES`/`CANONICAL_PPARALLEL_EDGES` pinned to **independent literals**, and
  `build_truth_cloud` asserting `cloud[0,0,0:4] == [2.0, 0.0, 0.0, 2.0]` for a 2 GeV forward
  proton (pins both the MeV→GeV scaling and the px/py/pz order) → M3, M4, M5

Do this **before** the Gate-2 re-issue, not after.

### M4. No model selection: EarlyStopping never fires, the reduced-LR schedule is dead code, the best checkpoint is never reloaded, and the only convergence telemetry is mislabelled

*Dimension: unfolding. Verdict: code-reading. File is NOT receipt-bound.*

Four defects in `omnifold_nn/omnifold/omnifold.py` that jointly remove every mechanism by
which non-convergence or over-training could be caught or corrected:

1. `early_stop` defaults to 10 (`:57` → `self.patience` at `:128`) and the nominal runs
   `epochs=8` (`train_fullevent_nominal.py:36`), so `EarlyStopping` (`:250-252`) can never
   trigger. Under Keras 2.x — the production stacks (TF 2.15 on Perlmutter per the
   launcher's `module load tensorflow/2.15.0`; TF 2.14 in the Delta NGC container)
   — `restore_best_weights` acts only inside the `wait >= patience` branch of
   `on_epoch_end`, so best weights are never restored and the reweight uses the epoch-8
   model. (Keras 3 moved the restore into `on_train_end`; verified on the locally installed
   keras 3.15.0. **Version-dependent — must be pinned per TF version on-cluster.**)
2. `ReduceLROnPlateau` is constructed with `patience=1000` (`:247`) — inert.
3. The reduced learning rate for iterations ≥ 1 — the regularizer that makes later
   iterations small refinements in the reference implementation — is **dead**. `Unfold`
   calls `self.CompileModels(fixed=True)` at `:166`, but that compiles only the
   never-trained templates `self.model1`/`self.model2` (`:375-376`); the models actually fit
   are the clones in `self.step1_models`/`self.step2_models`, and `RunModel` recompiles them
   at `:276` via `CompileModel(model_e, num_steps)` with `fixed` defaulting to `False`
   (`:367`), so `get_optimizer` returns Adam at `self.LR = 1e-4` every iteration instead of
   `min_learning_rate = 1e-5`.
4. `ModelCheckpoint(save_best_only=True)` (`:256-259`) writes best-val_loss weights to disk
   and they are **never loaded back**, so the per-iteration `.weights.h5` files are not the
   models that generated the published push weights — **the result cannot be re-derived
   from its own checkpoints.**

On top of this, `:287` logs `f"Last val loss {hist.history['val_loss'][0]}"` — index `[0]`
is the **first** epoch. The training log reports the epoch-0 validation loss under the
label "Last" and carries no information about whether either classifier converged.

**Failure scenario.** Either PET classifier overfits or drifts between its best epoch and
epoch 8 (plausible: a 2-block transformer at LR 1e-4 on 5.3M weighted rows with ~58% of
step-1 MC rows carrying weight 0 because they fail `pass_reco`). Push weights come from the
epoch-8 model, the log prints the epoch-0 loss as "Last", the on-disk checkpoint holds a
different (better) model, and the closure that would nominally catch a bad estimator is the
one that rewards a constant output (M2a).

**Minimal check** (no extra GPU, the moment any full-event training exists). `RunModel`
already pickles `hist.history` next to each checkpoint (`:291-292`,
`model_name.replace('.weights.h5','.pkl')`). Load them and print, per iteration and per
step, the full val_loss curve plus `argmin(val_loss)` versus the final epoch index. If
`argmin != 7` for any of the four fits, the run used a non-optimal model. Separately, pin
the Keras behaviour on-cluster:
`python -c "import inspect,keras;print(inspect.getsource(keras.callbacks.EarlyStopping.on_train_end))"`.

**Frozen.** `omnifold_nn/omnifold/omnifold.py` is bound by **no receipt** (verified: it is
not among the 92 resolved bindings), so it is editable without a gate re-issue — **but it is
the shared engine for nominal, replicas, universes and extraction, so any change must be
treated as an estimator-fingerprint change.** The config-only workaround (`early_stop =
epochs − 2`, or raise epochs) is passed from the driver, which **is** Gate-4-frozen.

### M5. The publication central value is a single stochastic transformer training, `n_ensemble=1`

*Dimension: unfolding. Verdict: code-reading.*

`MultiFold` is constructed at `train_fullevent_nominal.py:129-132` without `n_ensemble`, so
it defaults to 1 (`omnifold.py:57`) and the reweight-averaging machinery at `:230-238` and
`:441-471` (`avg_weights += w/len(models)`) reduces to a single model.
`LITERATURE_NOTES.md:52-55` records the field practice: *"4-10 ensemble members typical.
T2K uses 5 trials … and averages the reweighting factors into the central value."* The
repo's own 2026-06-03 audit (`:130-141`) concluded that for the stochastic 3D backend
*"adopting the 10-seed ensemble mean is a genuine, low-risk improvement"*, and
prepublication item #2 (`:293-300`) says the same. The 2D argument that ensembling is moot
(`sec_method.tex:141-145`, ensemble mean agreeing to 0.28%) rests on the sklearn exact-GBT
being nearly deterministic and does **not** transfer to a transformer.

The only ML-stochasticity handling in the full-event plan is one matched repeat at
*identical* seeds (`FULL_EVENT_FEATURE_CONTRACT.md:250`, launcher `tag=floor`), which
bounds bit-level nondeterminism, not model-init/split variance — and the existing floor
receipt is recoil-only with `is_publication_result=False`. Combined with `niter=2` and one
seed, there is **no spread of any kind** from which under-training, a bad initialization or
a diverged fit would be visible.

**Failure scenario.** A referee asks the standard OmniFold question — how many reweighting
trials are averaged into the central value — and the answer is one, for a transformer. If
that draw sits in the tail (the repo's own 3D study found frozen-vs-ensemble pulls with
p90 = 1.48σ), the published central value is off by ~1 ML-σ with no way to know, because
the matched repeat reuses the same seeds and cannot expose it.

**Minimal check** (~3 × 1.1-1.3 h GPU). Run the nominal at estimator seeds 42/43/44, same
subsample seed, and report the per-bin spread of the 285-cell spectrum plus the total-σ
spread. If it is comparable to or larger than the intended C_ML band, adopt the ensemble
mean. **Averaging over separate runs needs no frozen edit;** setting `n_ensemble>1` inside
MultiFold is a one-kwarg change to the Gate-4-frozen driver → Gate-4 re-issue.

### M6. Prior dependence is unassessed for the full-event path, and the existing PET prior envelope freezes the learned mapping — which the campaign's own contract forbids

*Dimension: unfolding. Verdict: code-reading. File is NOT frozen.*

The prior enters twice and only one is varied. **(a) As the reweighting base:** step 2
(`omnifold.py:194-204`) regresses pull weights onto the MC gen distribution, so the push
function itself is learned relative to the prior — and per B1 the absolute normalization
*is* the prior's. **(b) As the per-event truth weight in the reported binning.**

The dominant extrapolation systematic, `nd-unfolding/fps_3prior_envelope_5d.py`, varies only
(b). Its own header (`:5-7, :20-22`) states the full-stats push weights *"are held FIXED,
and each prior enters ONLY as a per-event truth reweight ρ — so all three priors are
re-binned from the SAME trained network, no re-inference."* That is exactly the
additive/fixed-model structure the corrected covariance contract forbids:
`PET_P1_P5_SESSION_STATE.md:94-98` — *"P5B vertical/flux systematics MUST be END-TO-END
JOINT universes … FORBIDDEN: additive C_syst_fixed_model + C_retrain."* Swapping
MnvTune → bare-GENIE → NuWro changes the step-2 target and therefore the learned push
function, so a fixed-`w_push` envelope is a **lower bound** on prior dependence, not the
systematic. And this tool is the 5D recoil path; **there is no full-event analogue, so for
the publication estimator prior dependence is currently quantified by nothing at all.**

**Failure scenario.** The result is published with a model-dependence band derived (by
analogy or by porting the 5D tool) from a fixed-mapping ρ reweight. In the low-completeness
extended-FPS cells — the [4.5,30] GeV p_T and [0,0.75] GeV p_∥ catch bins the extended grid
exists to expose — true prior dependence is dominated by the re-learned mapping, which the
band does not contain. Undercoverage in exactly the cells carrying the novelty claim.

**Minimal check** (one re-unfold, not a campaign). Retrain the full-event nominal once with
MC weights replaced by bare-GENIE (ρ applied to `w_truth` **before**
`build_fullevent_loaders`, not after extraction) and compare the 285-cell spectrum against
the fixed-`w_push` ρ-reweight of the nominal. The difference is the part the frozen-mapping
envelope omits; report it per completeness tier. `fps_gbdt_prior_reunfold_5d.py` is the
existing re-unfold precedent — read it first to reuse the ρ plumbing. **No frozen file
needs editing to run this.**

### M7. No gate binds the refined target to eq. 6 or to the Gate-2-certified refinement, and a permuted refinement output is accepted

*Dimensions: negweights (two findings merged), closure-power. Verdict: CONFIRMED, measured
by driving the real module.*

The closed-form and learned refinement forms **are** mathematically consistent (both are
`w̃ = |w|·clip(2g−1, 0)` with `g = D/(D+B)`; `stay_positive_refine_binned:263-274` vs
`u2d.refine_stay_positive:436-454`). What is missing is any binding of the *product*.

**(a) `refine_signed_measured` validates three things only** — row alignment
(`fullevent_fps_dataloader.py:354`), finiteness (`:357`), non-negativity (`:359`). Measured
by driving the real module (200k data / 30k bkg on a 2-D reco manifold,
pot_scale = 0.2124, D = 200000.0, B = 6419.8, D−B = 193580.2), it **accepts**
`lambda f,s: np.abs(s)` → 206419.8 (+6.63%), `np.ones_like(s)` → 230000.0 (+18.81%), and
`np.zeros_like(s)` → 0.0 (−100%). None raise. A correct GBC (depth 3 / n 100, u2d's
defaults) gives 194004.3 (+0.22%).

*But a Σw̃ = D−B gate is the wrong fix, by that same measurement:* a **degenerate** flat-g
refiner (depth 1 / n_estimators 1) lands at 193478.8 — only −0.05% from D−B — while its
binned L1 against the closed-form target is 0.0738 vs 0.0054 for the correct fit. With flat
g, `Σ|w|(2ḡ−1) = (D+B)·(D−B)/(D+B) = D−B` exactly, but the **shape** is (D+B): the
background is *added* rather than subtracted. So a sum identity has near-zero power against
the realistic failure. The diagnostic with real power already exists — the
learned-vs-closed-form binned L1/max_rel/cosine at `gate2_target_runtime.py:448-453` — and
its two defects are that it is declared non-gating telemetry (`:523-526`) and that M1's
`/1000` destroys it. **The actionable ask is a threshold on those metrics after the units
fix, not a sum identity.** (Also note `gate2_target_runtime.py:436-439` *does* independently
bind `raw_positive_sum − raw_negative_sum` at rtol 2e-11; what is unbound is specifically
`refined_sum`. And the docstring at `:346` promises fail-closed behaviour on *failure*, not
rejection of an all-ones *input* — it is not false as written.)

Reassurance worth recording: the canonical refiner already ran once on the real
4,680,719-row inventory. `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` `runtime_target` records
`g_min 0.1165`, `g_max 0.9870` (not flat), `frac_clipped 4.27e-06`, `n_floored_zero 20`,
`refined_sum 4006527.656` vs `raw_pos − raw_neg 4006528.601` — agreement to 2.4e-07. A
2-feature depth-3 × 100-tree GBDT spanning g ∈ [0.12, 0.99] is not globally underfitting.
**Residual local bias in the sparse high-p_T / high-p_∥ corners and the low-p_∥ FPS catch
bins remains possible and is a bounded-systematic question, not a blocker.**

**(b) Row correspondence between features and signed weights is unasserted.**
`build_signed_measured_inventory` stacks `feat = np.vstack([fd, fb])` (`:337`) and
`signed = concat([data_signed, bkg_signed])` (`:338`); the two orders must agree for
`g(x) = D/(D+B)` to be learned on the right labels. The only test of the output structure
asserts `feat.shape`, never its contents (`test_fullevent_gate2.py:110`), and
`test_misaligned_output_rejected` (`:174-177`) uses a wrong-**length** return, so a
same-length permutation passes. `meta['target']['signed_target_hash']` (`:669`) hashes the
**input** signed array — there is no order evidence binding `w_refined` to the rows of
`meas_cloud_all`. Per M1, a one-cell histogram cannot see it either.

Mechanism precision for the test author: the canonical refiner is element-wise
(`unfold_2d_omnifold_unbinned.py:436-454`) so it preserves input order; the live risk is
the `feat`/`signed` desync *inside* `build_signed_measured_inventory`. With the vstack
swapped, `w_refined` is still row-aligned to `meas_cloud_all` — what breaks is that each
event's Stay-Positive factor `2g(x_i)−1` is evaluated at a *different* event's (p_T, p_∥):
a mislabelled classifier producing a smoothly wrong refinement.

**(c) Nothing on the Gate-4 path reads `refinement_is_learned_production`.** The only two
enforcing call sites are `gate2_target_runtime.py:398` and
`validate_gate2_target_receipt.py:162` — both target-only Gate-2 tools that do not run in
the training path. `train_fullevent_nominal.py:137` stores `target=meta.get('target')` into
the nominal npz and never inspects it; the Gate-4 validator never reads `z['target']` at
all (grep: zero hits). `assert_publication_config` (`fullevent_fps_dataloader.py:439-469`),
described in the driver docstring as *"the authoritative fail-closed publication gate"*,
runs on a pre-compute cfg dict and has no knowledge of `refine_fn`.

*Scope honestly:* the shim-injection scenario is **not** reachable by default — the driver
exposes no `--refine-fn` flag and never passes one (`:120-122`), so
`refinement_is_learned_production` is unconditionally `True` for any npz that driver
writes; and the launcher pins the target NPZ by sha256 + size before any compute
(`sbatch_pet_fullevent_nominal.sh:35, 101`). The **better-founded** variant of the same gap:
the driver passes no `refine_kwargs`, so the nominal calls `u2d.refine_stay_positive` with
`params=None` — `GradientBoostingClassifier()` at sklearn defaults, `random_state` unset —
whereas the Gate-2-certified target used
`{"estimator":"exact","device":"cpu","params":{"random_state":45},"verbose":True}`
(`gate2_target_runtime.py:386-391`, frozen in the receipt's `configuration_sha256`). **Nothing
compares the nominal npz's `target.signed_target_hash` / `refined_sum` / `pot_scale` /
`n_floored_zero` against `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, and the Gate-4 driver
rebuilds the refined target from scratch rather than consuming the hash-bound Gate-2 product
`G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` (sha `1ef7e0d2…`).** That comparison is the
single highest-value, lowest-cost addition here.

**Frozen.** (a) and (b) are in `fullevent_fps_dataloader.py` → **Gate-2 two-file re-issue +
re-run**. (c) is a validator-only change → **Gate-4 re-issue + re-run** (login-safe tests).
Tests for (b) go in `tests/test_fullevent_gate2.py`, which is **not** frozen — free.

### M8. The stress closure, Gate-4's only evidence that the estimator *moves*, has no absolute recovery criterion

*Dimension: closure-power. Verdict: CONFIRMED. File is NOT frozen.*

`stress_closure_muon.py:113-114`: `recoil_fails = median(res_r) > 0.5*median(prior)` and
`full_recovers = median(res_f) < 0.5*median(res_r)`. The second is **doubly relative** —
`res_f` is never compared to the prior. So `res_r = 4×` prior and `res_f = 1.5×` prior
satisfies both predeclared conditions and prints "STRESS CLOSURE PASS" (1.5 < 2.0) **even
though the full-event unfold is worse than doing nothing**, and Gate-4 records
`stress_recoil_blind` and `stress_fullevent_recovers` as True.

Separately, the script shares no code with the production path (no
`fullevent_fps_dataloader` symbol appears in it; it builds its own clouds at `:42-73`), so
a PASS says nothing about `build_truth_cloud`'s angular coordinates, the (p_T, p_∥) event
block, or the FPS domain. **This half is a documented design property, not a defect** — the
docstring (`:2-16`) frames it as a deliberately controllable synthetic omitted-variable
demonstration for KNOWN_ISSUES #19, and it cannot use the real loader because the only
`g2-fullevent-v1` input is the Gate-2 dump. Reading `gen == reco` (`:70`), `pass_reco` all
True, and `num_evt = 1` (`:74-77`) as defects mistakes a minimal ablation for a broken
production replica. Do not "fix" those.

**Fix** (free — not frozen): `full_recovers = (median(res_f) < 0.5*median(res_r)) and
(median(res_f) < c*median(prior))` with `c` predeclared, and print `res_f/prior`. Add a
pure-function test of the verdict logic with synthetic (prior, res_r, res_f) triples
including the (4×, 1.5×) case, asserting FAIL. Note mutating `:117` to `if True:` produces
the unchanged 7-failed/333-passed baseline — the verdict logic has **zero** test coverage,
as does `closure_fullevent_fps.py`'s (`ok = True`, `--l1-max 0.10 → 10.0`, and an
axis-transposition at `:132` are all invisible; the transposition is also invisible to the
statistic itself, since `H_truth` and `H_rw` transpose identically).

### M9. The bootstrap-replica coherence contract cannot be satisfied as emitted

*Dimension: negweights. Verdict: CONFIRMED by executing against the real module.*

F7 step 3/4 (*"persist per-category factors … re-consume the SAME signal + background draws
… fail closed"*, `fullevent_fps_dataloader.py:215-217`) is not achievable with the object
the loader emits. `meta['bootstrap']` (`:602-606`) contains `bkg_bootstrap_factor` but
**not** `bkg_indices`, and `validate_coherent_bootstrap:409-410` raises whenever the factor
is present without the indices — executed: *"[F7] bkg factor persisted but bkg_indices
(order evidence) omitted"*. Worse, the key is present even when `has_bkg` is False (value
`None`, `:606`), so the raise fires for a background-free input too. It also never persists
a **data** factor, and `validate_coherent_bootstrap` has no data branch at all (`:385-431`)
— yet the data Poisson draw directly sets the positive half of the refined replica target
(`build_signed_measured_inventory:335`). Injecting a deliberately wrong
`data_bootstrap_factor` (rng(999) instead of rng(seed)) still returns True.

Both replica guards are dead in production: `assert_refined_target_is_replica` (`:371`) and
`validate_coherent_bootstrap` (`:385`) have **zero** non-test call sites, and no caller
anywhere passes `bootstrap_seed` (`gate2_target_runtime.py:381` passes None;
`train_fullevent_nominal.py:120-122` passes nothing).

Frame this as a **producer/validator inconsistency inside one frozen file**, not an
invitation to weaken the gate: `bkg_indices` is already a required dump key
(`fullevent_dump_contract.py` `BKG_KEYS`; hashed at `dump_pointcloud_inputs.py:236`), so
persisting it is the obvious fix, and the guard fails *loudly*, which is the right
direction.

Also note `coherent_bootstrap_factors` draws the data factor from
`default_rng(int(seed))` (`:256`) while the MC subsample uses `default_rng(seed)` (`:518`) —
for a replica where `bootstrap_seed` equals the subsample seed these consume the same bit
stream. Avoidable by seed policy (the frozen subsample seed is 0), but **decide and document
it explicitly** rather than leaving it to chance.

**Frozen.** Yes — `fullevent_fps_dataloader.py` → **Gate-2 two-file re-issue + re-run**.
Fix: add `bkg_indices`, `data_indices` and `data_bootstrap_factor` to `meta['bootstrap']`;
add a data branch to `validate_coherent_bootstrap` mirroring `:406-417`; and call both
guards from whatever replica driver is written. Since P5B cannot run before P5A, this is
not urgent — but it must be fixed *before* the first replica, because a silently
mis-estimated C_stat is not detectable after the fact.

### M10. The canonical grid exists in two independent hardcoded copies, no test compares them, and the edge guard is self-referential

*Dimension: closure-power. Verdict: CONFIRMED by mutation.*

The reporting/covariance/manifest side defines `PT_EDGES`/`PZ_EDGES` at
`nd-unfolding/fps_provenance.py:25-28`; the estimator side defines `CANONICAL_PT_EDGES`/
`CANONICAL_PPARALLEL_EDGES` at `fullevent_fps_dataloader.py:47-52`. They are numerically
equal today (verified) and **nothing compares them**. `assert_extended_fps_edges` (`:63-86`)
compares a dump's stored edges only to the dataloader's own constant, so a value-level edit
to that constant makes the guard tautologically pass; the only literal rejections are the
paper top/bottom edges (`:82-85`). Every test reference is module-to-module
(`test_fullevent_fps.py:23,26,34,37`; `test_g2_dump_branch.py:105` compares
`dp.FPS_PT_HI` to `fed.CANONICAL_PT_EDGES[-1]`; `test_pet_nominal_gate4_validator.py:45-49`
asserts only bin **counts**, which a value change leaves intact).

Mutation results: dataloader 0.47 → 0.45 → only `test_hash_bindings` fires.
`fps_provenance.py` 0.47 → 0.45 → **zero detection of any kind** — it is neither hash-bound
(not among the 92 resolved bindings) nor pinned by any test literal.

**Failure scenario.** A one-digit edge edit. If it lands in the dataloader during the
planned Gate-2 re-issue, the estimator's domain guard, the dump's edge check and Gate-4's
freeze all pass while the grid silently diverges from the one the publication manifest, the
266/285 reported mask and every covariance block are built on — the cross section is
extracted on one grid and reported on another.

Calibration: *"nothing anywhere notices"* on the `fps_provenance` side is slightly too
strong — `fps_control_manifest.json` persists the literal `53119a40…` at `:50, :113, :135`
and `require_common_fingerprints` (`fps_provenance.py:236`) compares against a recomputed
`layout_fingerprint()`, so a consumer re-gating the **committed** manifest would raise. The
gap is that no test re-gates it.

**Fix** — four pure-python assertions in an unfrozen test file, zero cost:
`assert_array_equal(fps_provenance.PT_EDGES, fed.CANONICAL_PT_EDGES)` and the p_∥ pair;
`layout_fingerprint() == '53119a407987c3b65911581ead7701b6a12d10742c6156682603a30da80a97fe'`
(verified to match the manifest today); both arrays against explicit literals; and sanity
bounds (`PT_EDGES[-1] > 4.5`, `PZ_EDGES[0] < 1.5`, `PZ_EDGES[-1] > 60.0`).

### M11. `verify_hash_bindings.py` silently discards in-repo bindings whose recorded path is not root-relative, and files them under a reassuring label

*Dimension: code-integrity. Verdict: CONFIRMED by re-running the module's own `collect()`.*

`localize()` (`docs/orchestration/verify_hash_bindings.py:74-78`) tries exactly two
resolutions — strip the Perlmutter root, then join to repo root — and returns `None`
otherwise; `main()` (`:101-103`) counts that as `unresolved` and `:115-116` prints
*"(301 unresolvable: data files, off-repo artifacts, binaries)"* before `:126` can print
`ALL BINDINGS INTACT`.

At least three of those 301 are real in-repo artifacts recorded relative to a different cwd,
**including a Python source file**: `fps_control_manifest.json` binds
`evidence.unfold_source.path = "unfold_nd_omnifold_unbinned.py"` (sha `9431d56a…`), which
actually lives at `nd-unfolding/unfold_nd_omnifold_unbinned.py` — verified by `shasum -a
256` to match exactly, i.e. currently correct **by luck**. Same for
`active_universe_5d/fps/covariance/fps_reported_mask.json` (`b994ec83…`) and
`audit_merged_fps.json` (`19ca5c60…`). Re-running `collect()` and filtering for
None-localizing source-like paths yields exactly 5 entries; the other 2 genuinely do not
exist in the checkout.

`nd-unfolding/unfold_nd_omnifold_unbinned.py` is **absent from the frozen-file map** at
`start-audit-executor.md:26-33`, so an editor would reasonably believe it free — yet it is
the ND driver that calls `u2d.refine_stay_positive` at `:873` and whose sha256 is the FPS
control manifest's provenance evidence. **The arbiter that exists specifically to catch the
`2732304` failure mode has a blind spot of the same shape.**

Calibration: the docstring at `:23` does hedge — *"Exit 0 if every RESOLVABLE binding
matches"* — so the defect is concentrated in the human-facing label at `:115-116`, which
converts a known limitation into false reassurance. Scope: these three are covariance
*provenance* hashes, not Gate-2/3/4 code freezes, so the exposure is provenance
falsification rather than a voided gate PASS.

**Fix** (free — the verifier lives under `docs/`, is free to edit, and carries no binding of
its own): add a basename fallback that resolves to a unique in-repo match and fails loudly
on ambiguity, and split the counter into "off-repo/data" vs "in-repo, unmatched or
ambiguous" so the second bucket is never zero-by-labelling. **No gate re-run needed.** Also
add `nd-unfolding/unfold_nd_omnifold_unbinned.py` to the frozen-file map in the executor
brief.

### M12. The in-flight host-memory ladder's headline projection answers the wrong configuration — known finding B is REFUTED for the frozen nominal

*Dimensions: closure-power, code-integrity — two dimensions converged. Verdict: CONFIRMED.*

**This partly refutes known finding B.** Three legs:

1. **A real-data peak-RSS anchor already exists in-tree.**
   `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` records `environment.max_rss_kib = 11,632,724` =
   **11.09 GiB** in a single process, from a run of `build_fullevent_loaders` on the real
   49,152,885-row inventory with `bkg_mode=negweight-refined`, full measured inventory and
   `verify_identities=True`. That is an order of magnitude below the ~78 GiB/rank hand
   estimate. It is consistent with exactly **one** full materialization of `part_gen`:
   from `G2_FPS_MEFHC_P12_RECEIPT.json`, `part_gen` is float32 (49152885, 12, 5) = 10.99 GiB
   and `part_reco` is 6.59 GiB, and `loader:520` releases the part_reco temporary before
   `:521` creates the part_gen one. **So the materialize-then-subset pattern in finding B is
   real, but the temporaries are freed rather than accumulated.**
2. **The nominal is single-rank.** `sbatch_pet_fullevent_nominal.sh:6-8` is
   `--nodes=1 --ntasks=1 --gpus=1` with no MPI/horovodrun anywhere, and
   `docs/orchestration/CLAIMS.md` CLM-008 records F8 as *"MOOT by policy — no Horovod for
   P5B, single-rank jobs."* No ×4 multiplication applies. Every in-repo caller of
   `build_fullevent_loaders` passes no rank/size at all.
3. **The stated ×4 mechanism is wrong anyway.** `omnifold_nn/omnifold/dataloader.py:67-107`
   shards with `x[rank::size]` — basic slicing, i.e. a strided **view** that keeps the full
   base array alive — so moving rank/size earlier into the DataLoader would not reduce
   per-rank RSS.
4. **The extrapolation target is the wrong configuration.**
   `measure_fullevent_host_memory.py:51` hardcodes `REAL_MAXEV = 40_000_000` and `:52`
   derives `SUBSAMPLE_RATIO = 0.8138`. The frozen full-event nominal is **2,000,000**
   (`train_fullevent_nominal.py:37`, `validate_pet_nominal_gate4.py:56`,
   `sbatch_pet_fullevent_nominal.sh:54`) — ratio 0.041, not 0.8138. 40M/4-rank is the
   **recoil-only xps2** recipe (`PET_TRAINING_ON_DELTA.md:15,103`;
   `sbatch_pet_train_fps_delta.sh:49`), and `PET_UQ_PRODUCTION_STATUS.md:494` states the
   rationale for "2M/niter2/epochs8 (not the 40M FPS train)" explicitly.

**Do NOT read this as "cancel job 20558496".** Leave it alone. Its correct use is to
**re-scope how the output is read**: `sbatch_fe_hostmem_ladder_delta.sh:47` has
`RUNGS="200000 2000000 5000000 10000000 20000000"`, which *includes and brackets* the frozen
2M point, so the ladder does measure the relevant configuration. What is inapplicable is
only the summary banner's 40M / 49.15M / ×4 extrapolation (`:131`). Take the **2,000,000
rung** as the answer for the publication nominal.

Two caveats to state rather than paper over: the 11.09 GiB anchor was taken at
`max_mc_events = 200,000`, so it pins the *dominant, max_events-independent* term (the
`part_gen` materialization) but not the cloud-construction increment — the honest
projection for the 2M nominal is **~11.1 GiB + O(few GiB) ≈ 13 GiB single-rank**, which
strengthens the refutation. And the one configuration that *is* plausibly large is the
**no-subsample** build (`max_events=None`, the loader default at `:472`), which a
full-inventory reweight-all / extraction pass would use (B3, CLM-006's "2M train →
reweight-all 49.2M"). No such full-event script exists yet; when it is written, check its
peak against **Perlmutter's shared-QoS memory share** (`--qos=shared --cpus-per-task=32`,
no `--mem`), not against Delta's 251.6 GiB node.

**Consequence of getting this wrong:** scheduling a loader refactor (shard-before-build /
chunked construction / a memmap builder) on the 08-03 critical path against a non-problem —
at the cost of voiding the Gate-2 loader binding and forcing a two-file re-issue — while the
actual launch blocker (B4) sits unlisted.

**Also confirms known finding A.** The real dump carries **12** token slots
(`G2_FPS_MEFHC_P12_RECEIPT.json`: `part_gen (49152885,12,5)`, `num_part: 12`), and the
ladder correctly overrides `TOKENS=12` (`sbatch_fe_hostmem_ladder_delta.sh:28,48` — with an
explicit "ON PURPOSE" comment), so finding A is already mitigated in the running job. It is
**not** fixed elsewhere: `sbatch_fullevent_dryrun_delta.sh:39` still defaults `TOKENS=40`,
so every cost/shape/wall-clock number from that dryrun overstates the truth cloud by
40/12 = 3.3×. That file is not frozen — change the default to 12.

### M13. The per-bin nondeterminism floor is a spatially coherent high-p_T row shift, not sparsity — and the study discards the arrays needed to use it correctly

*Dimension: binning-leakage. Verdict: code+receipt reading; recoil-only.*

`ND_OMNIFOLD_RUN_LOG.md:2215, 2227-2229` concludes *"the driver is raw sparsity … not
position on the grid"* and that the worst-bin signs are consistent with the global total
ratio. Both are contradicted by the receipt's own numbers
(`products/pet/pet_weights_fps_xps2_delta_s101_floor.json`, `per_bin_floor.worst_bins`):
all 12 worst bins sit in the **single** p_T row [2.5, 4.5] and all 12 `rel_pct` are
negative. |rel| vs n_events: 0.562% at n=2, 0.523% at n=11, 0.603% at n=44, 0.486% at
n=93, 0.427% at n=590, 0.400% at n=3504, 0.296% at n=57178 — a 28,589× range in n yields
only a 1.9× change in |rel|, where per-event jitter would give ~1/√n = 169×. And
`per_event_floor.total_ratio = 0.9997729` (a −0.0227% global shift), so these bins are
13-27× the global offset. The two trainings differ by a **coherent ~−0.3% to −0.6%
multiplicative shift of one p_T row**. 10 of the 12 are reported bins that also fail the
repo's own tan20 acceptance criterion.

A fully correlated shift across ~11-15 reported bins does not average down in a shape
comparison or χ², so the aggregate scalar 0.0349% — and the "5.9× suppression by binning"
framing underpinning HARD BAR 3 — is the wrong summary for a per-bin double-differential
product. `floor_gpu_nondeterminism.py:106` **deletes** `relbin` and `:143-157` persists only
summary stats plus the worst 12, so the correlation structure is unrecoverable without
re-reading the Delta-local, single-copy weight NPZs.

**Failure scenario.** A future covariance treats the floor as diagonal 0.0349% (or omits it,
since `is_covariance_component=False`) while the real effect is a ~0.4% fully-correlated
shift concentrated in the high-p_T FPS extension rows — exactly the rows whose reported bins
lie outside MINOS acceptance and whose prior spread the ledger already flags at 62-81%
(`VALIDATION_LEDGER.md:236-241`).

**Minimal check — no new GPU time and no third training (HARD BAR 3 respected).** Re-run
`floor_gpu_nondeterminism.py` on the two **existing** Delta NPZs (batch, not login) with
`relbin`/`N_bin`/`S_nom` added to the saved output, then (a) regress `log|rel|` on `log n`
within the p_T 2.5-4.5 row — coherent shift predicts slope ≈ 0, sparsity predicts −0.5 —
and (b) print the population-weighted mean of `relbin` for each of the 15 p_T rows.
`floor_gpu_nondeterminism.py` is **explicitly known-not-frozen**, so this is a free edit.

**Caveat, load-bearing:** this is recoil-only xps2, so the **magnitude does not transfer** to
full-event and must not be promoted (HARD BAR 2). The **structural** conclusion — a scalar
floor is the wrong summary for a per-bin product — does transfer.

### M14. `assemble_ctotal_bkgsub.py` asserts a soundness its own Gate 7 forbids

*Dimension: covariance. Verdict: CONFIRMED as a documentation contradiction; the affected
product is already quarantined.*

`assemble_ctotal_bkgsub.py:119` is an unconditional `C_total = sum(Cs.values())` and its
docstring (`:10-21`) justifies it by arguing the blocks are disjoint. Disjointness is not
the issue: the correct total for a retrained response is
`Σ_u outer(s_u+Δ_u, s_u+Δ_u) = C_syst + C_retrain + Σ_u [outer(s_u,Δ_u)+outer(Δ_u,s_u)]`,
and the cross term is silently zero. `assemble_cretrain.py:68` adds only
`np.outer(delta, delta)`; `phase7_extract_compare.py:182` already saves **both**
`delta_reported` and `s_reported`, so the cross term needs zero new compute — yet nothing
anywhere forms `s_u·Δ_u` (grep for `s_reported` returns only unrelated ROOT histogram names).

**This is a documentation trap, not an uncovered published error.** The omission is already
recorded verbatim at `VALIDATION_LEDGER.md:59-63`, prohibited in advance by
`PET_UQ_REMEDIATION_STATUS.md:228-230` (Gate 7: *"Do not build or add separate frozen-map and
retraining covariances for the same nuisance"*), and the affected product is **QUARANTINED**
(`VALIDATION_LEDGER.md:46`; `PRESENTATION_SAFE_TABLE.md:34`, Tier 3). It is also recoil-only
PET, barred from promotion by HARD BAR 2.

**Do not quote a "63% of trace" bound for it.** `C_syst` is a mean-centered two-endpoint
`mat_covariance` plus a 1/N flux block (`build_csyst_prelim_bkgsub.py:4-7`), **not**
`Σ_u outer(s_u,s_u)`, so `||s_u|| = norm_delta/overall_ratio` is not the vector being added
to — the implied `Σ||s_u||²` (1.27e-75) exceeds the entire C_syst trace (8.82e-76), which
proves the decomposition wrong. Rank is 6, not 5 (`flux_55` is material and carries the
largest `||s_u||`).

**Actionable item:** fix `assemble_ctotal_bkgsub.py:10-21` and the
`cretrain_no_double_count` summary field so they stop asserting soundness Gate 7 forbids,
before anyone reuses this code to build the *full-event* budget. **Minimal check** (pure
numpy, login-runnable, zero new compute): load the six
`products/pet/bkgsub/p7/pet_p7_<tag>_response.npz` files and print
`s_u·Δ_u/(||s_u||·||Δ_u||)` per band. Not frozen.

---

### Minor items (record, do not schedule against the 08-03 window)

- **Measured DataLoaders never receive rank/size while the MC one does**
  (`fullevent_fps_dataloader.py:612-614` vs `:621-622`, `:658-659`). *Found by two
  dimensions.* Inert today — no caller passes rank/size at all, and the launcher is
  single-rank. **Do not "fix" it by adding rank/size at `:658`:** the recoil reference shards
  *upstream* (`minerva_pet_dataloader.py:217-218` strides both index arrays, then passes
  rank/size to neither loader, `:240-241`), so under this codebase's own convention the
  measured omission is correct and the MC forwarding is the deviation. Note also
  `omnifold/dataloader.py:51` sets `nmax` from the **pre-shard** count while
  `omnifold.py:131` computes `num_steps_reco` from it, so a mixed-convention run mis-counts
  steps regardless. `PUBLICATION_COMPLETION_RUNBOOK.md` (Gate 5) states outright that
  *"Horovod and distributed rank slicing are prohibited"* — the cleanest resolution is to
  have `build_fullevent_loaders` **raise on `size > 1`**, making the prohibition structural.
  No test anywhere passes rank or size (grep over `tests/*.py`: no matches), and
  `gate2_target_runtime.py:415-416` structurally pins Gate-2 to `size=1`.
- **`test_fullevent_gate2.py:159-162` uses `lambda f,s,**k: np.abs(s)` to exercise the
  bare-array return path**, and `test_no_all_ones_purity_substitution` (`:226-230`) asserts
  only `not np.allclose(w, w.flat[0])`. The first is not a claim that abs-weights are
  physically supported (it is the shortest non-negative lambda), and the second has exactly
  the power its name claims. But the file is **not frozen and freely editable**, so change
  the lambda to `np.clip(s,0,None)` and add the two tests with real power: `refined_sum`
  vs `raw_pos − raw_neg` on a fixture where they differ materially, and a learned-vs-
  `stay_positive_refine_binned` per-cell agreement threshold.
- **Nothing pins the cloud token dimension.** `fullevent_dump_contract.py:88` derives `P`
  from `part_reco.shape[1]` and never checks `part_gen.shape[1] == P`; `REQUIRED_KEYS`
  (`:38`) omits `num_part` even though the real dump carries it;
  `build_fullevent_loaders` performs no token check at all; and
  `train_fullevent_nominal.py:123-128` passes one `num_part=P` to **both** models. Both
  in-repo writers are self-consistent (`dump_pointcloud_inputs.py:315,321` allocate from one
  argument; `make_synthetic_g2_fullevent.py:117-118` builds both at one `tokens`), which is
  why this has never bitten. `net.py:79` uses a fixed-shape Keras `Input`, so a mismatch
  raises rather than silently truncating. Fix by requiring
  `part_gen.shape[1] == part_reco.shape[1] == num_part` in `fullevent_dump_contract.py`
  (**not** in the frozen map) — verify first that the existing dump satisfies it, which it
  does.
- **The config gate accepts an input with no `estimator_fingerprint` and then stamps the
  publication one on it.** `train_fullevent_nominal.py:72` tests
  `not in (None, ESTIMATOR_FINGERPRINT)` and `:76` unconditionally sets
  `cfg['estimator_fingerprint'] = ESTIMATOR_FINGERPRINT`, so the loader-side check at
  `fullevent_fps_dataloader.py:450-453` reads a value the driver just wrote — and
  `:135` stamps it into the output, which the Gate-4 validator reads back as its
  `freeze:fingerprint` evidence. The Gate-4 receipt's `fail_closed_on[0]` ("unset rejected")
  is *literally* true of the gate it names; the defect is that the driver pre-fills the value
  the gate tests. Gate-4 re-issue, or correct the wording. Mitigated on the launcher path by
  `EXPECTED_TARGET_SHA`.
- **Identity hashes do not cover the arrays that are trained on.**
  `_verify_stored_identity` is called with `(w_truth, pass_truth)`, `(measured_pc,)` and
  `(w_bkg, bkg_indices)` (`fullevent_fps_dataloader.py:583-591`; write side fixed at
  `fullevent_dump_contract.py:102-104`); `part_gen`, `part_reco`, `truth_scalars` and
  `measured_scalars` are unbound. Because `w_truth`/`pass_truth` are per-row, any
  **reordering** does change the hash — the surviving hole is a content rewrite that
  preserves those row-for-row. Mitigated for the launcher (`sbatch:101-102` sha256s the whole
  9.9 GB file) and for Gate-2 (`gate2_target_runtime.py:139-153` does the same and
  cross-checks both Gate-1 receipts) — but **not** for `closure_fullevent_fps.py`, which
  hashes nothing. Cheap fix: add the file-level sha256 assertion to that unfrozen script
  against `G2_FPS_MEFHC_P12_RECEIPT.json` `npz.sha256` = `fa6b3463…a29625`. Extending the
  identity hashes themselves would need a dump regeneration plus Gate-1/Gate-2 re-issue —
  not worth it.
- **`assert_no_truth_leakage` is a clone-and-compare tautology.** `:193` rebuilds the block
  with the same `_event_block` call and the same `pass_reco`-masked mean/std that produced
  `event_reco` at `:171`, so the first assertion cannot fail unless
  `build_event_features` itself is edited; the second clause detects only a wholesale
  truth-for-reco substitution. Reachability *is* fine (the `:547` call is unconditional and
  all five in-repo consumers enter through `build_fullevent_loaders`). It does pin the
  masked normalization and the post-normalization zeroing, which a previously-real bug
  violated, so "near-zero power" overstates. Note `event_data` needs no leakage assertion —
  the `data` tree has no truth branches (`validate_g2_fullevent_smoke.py:138-141`) — and the
  real `event_data` hazard (silent fallback to MC scalars) *is* fail-closed at `:528-542`.
  The off-by-one row-pairing scenario is structurally impossible in the frozen reader
  (`dump_pointcloud_inputs.py:325-345` writes all per-event arrays at the same index in one
  `GetEntry` iteration). What survives: no gate binds cloud **content** (only ROOT branch
  *names*), and the docstring at `:25-27` overreaches. Cheap defense-in-depth mirrors an
  existing pattern (`pointcloud_projection.py:142-146` asserts the ROOT `MC` branch equals
  `truth_scalars[:,0]`): add the reco-side equivalent in a **new unbound script**.
- **Top-edge inclusivity differs between conventions.** `dump_pointcloud_inputs.py:126-129`
  retains p_T == 30.0 (`<=` on both ends); `np.histogram2d` puts it in the last bin;
  `unfold_nd_omnifold_unbinned.py:474` (`np.digitize(c,e)-1`) yields index 15 and `:480`
  drops it. Latent — nothing clips to the domain, and a float32 scalar landing bit-exactly on
  30.0 or 120.0 is negligible. Also note `build_measured_training_nd` is the ND/LGBM
  purity-style target and is **not** on the PET publication path. Disposition: a comment or a
  shared bin-index helper, not a code change.
- **PSD is fail-closed in the adoption path but report-only where PET products are built.**
  `fps_provenance.py:395-398` `require_psd` raises and `adopt_unified_fps.py:112`,
  `adopt_unified_4d.py:125-126`, `adopt_unified_5d.py:153-154` all raise before their writes;
  `assemble_ctotal_bkgsub.py:59-65` computes `psd_diagnostics` (at `:127`/`:135`, i.e.
  *before* the savez at `:139`, and serialized into the summary) with **no raise**, and
  `project_cov_nd.py:191-192` prints OK/FAIL then writes at `:194-207` **without persisting
  `psd_ok` or `min_eig`**. Near-unreachable in practice — every C_total component is PSD by
  construction and the recorded `min_eig` is −2.4e-91 (roundoff) — and
  `project_cov_nd.py:209` self-labels its output "(CANDIDATE — do not quote)". One worthwhile
  change: persist `psd_ok`/`min_eig` as TParameters alongside `sqrt_tr` so a projected
  covariance carries its own verdict.
- **Ratio banks are stored in float16.** `unified_throw.py:175` (`def sv(name, arr,
  dt=np.float16)`) is the only float16 write in the repo and produced `bank_uthrow_fps`. The
  *range* story does not explain the documented 1803 bad rows — those are localised to
  LowQ2 +1σ, HighQ2 +1σ and MFP_N −1σ, whereas the dump shares one CV denominator across all
  bands per event (`:165-171`), so overflow would hit every band on the same events; the
  band-localised non-positive pattern is what a negative GENIE numerator gives, exactly as
  documented. The *precision* story has teeth: 9.77e-4 relative spacing just above 1.0
  survives exponentiation (`uq_math.py:83`) and the 12-band product
  (`unified_throw_cov.py:179-181`) into a one-sided positive variance bias in the
  mean-centered band covariance, worst in cells with a handful of events. Check by counting
  exactly-inf / exactly-zero / strictly-negative entries separately per bank file, and bound
  the bias by re-dumping one group at float32 and diffing band sqrt-traces.
- **Documentation, not code: the "MAT biased 1/N" contract is stated too broadly.**
  `FPS_UQ_CORRECTED_STATE.md:26-30, 78-79` asserts 1/N across the budget and lists
  `combine_cov_nd.py` as enforcing it, but `combine_cov_nd.py:20` is
  `(Z.T@Z)/(Xr.shape[0]-1)` and `pet_systematics{,_5d}.py:191/226` use `np.cov(..., ddof=1)`,
  while `analyze_universes_nd.py:94` and `uq_math.py:96-104` are 1/N. **The code is right and
  the doc is loose:** 1/(N−1) is correct for bootstrap/split replica ensembles (draws from a
  sampling distribution) and 1/N is the MAT convention for a fixed universe set —
  `combine_seedscan_split.py:68` documents this in-line. Amend the doc; change no covariance.
- **Coverage validation covers 5.4% of the budget.** `uq_fps/corrected/coverage_valid_fps.json`
  validates C_stat only (sqrt-tr 4.339e-40 of a combined 8.041e-39), and no containment or
  pull test exists for C_syst, the adopted matrix, or the combined matrix. State that
  explicitly wherever coverage is cited. The variant_A/variant_B gap (0.776 vs 0.687) is
  **not** unexplained — `bootstrap_nd.py:32-33` Poisson-fluctuates both data and MC, so the
  bootstrap C_stat is expected to exceed the closure-toy spread, and the observed direction is
  over-coverage, i.e. conservative. Record that reconciliation in the artifact.
- **`adopt_unified_fps.py` has no `--cv-centered`** (argparse `:49-59`) while
  `adopt_unified_4d.py:53-56` and `adopt_unified_5d.py:81` do, and
  `fps_provenance.py:488-501` `require_mean_shift` has **no magnitude bar** (presence,
  finiteness, dimension only). Add the bar (record the realized
  `||mean_shift||/sqrt(trace(C_unified))` in the receipt regardless) and add the flag for
  parity. **Do not import the 28.5% materiality figure** — 1.654e-38 / 5.8077e-38 /
  6.2367e-38 are the corrected **5D GBDT** candidate on 10,694 bins
  (`VALIDATION_LEDGER.md:30-44`), a path that *has* `--cv-centered` and *did* build the
  CV-centered artifact; no FPS mean-shift magnitude is established anywhere.

---

## 4. NOT ASSESSED — this is not a clean bill of health

**Perlmutter has been in maintenance for the whole of this audit, so the real full-event
input `G2_FPS_MEFHC_P12.npz` (9,897,374,636 B, sha `fa6b3463…a29625`) was never exercised.
Every statement about what the code *does on real data* is code reading plus the committed
Gate-2 receipt — not observation.** The sole copy is on **purgeable `/pscratch` with no
backup**.

**Physics quantities that are unverifiable today**

- Whether the normalization erasure (B1) quantitatively explains the ~10% PET/GBDT gap.
  Mechanism confirmed by code; magnitude inferred from the run log's `w_push` means
  (0.999-1.028) versus GBDT data/CV = 1.135. Needs `R` from the dump.
- **The true POT values.** `dataPOTUsed`/`mcPOTUsed` in the merged MEFHC ROOT, and whether
  `d['pot_scale'] == data_pot/mc_pot`. No copy exists in the repo — the Gate-1 receipt binds
  only dtype and shape — so `pot_scale = 0.21240500334472884` is currently unverifiable **in
  principle**, not just in practice.
- Whether the learned refinement is **locally** correct on real data (M7). The single most
  important open question in the negative-weight dimension. Needs the dump plus
  `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` re-projected on the correct GeV grid.
  `g_min 0.116 / g_max 0.987` is encouraging but says nothing bin-by-bin.
- How many extended-FPS cells have POT-scaled background exceeding data (M1's fix trap).
- Whether `measured_scalars` is row-**order** aligned to `measured_pc`. Row *count* is
  enforced; order is bound by no hash (`data_identity_hash` covers `measured_pc` alone).
- Whether `d['part_reco']` genuinely contains reconstructed cluster quantities. The only
  protection is a ROOT branch-**name** check; deciding this needs the npz or
  `runEventLoopOmniFold.cpp`, neither of which is in this repo.
- Direct confirmation that `measured_scalars`/`bkg_reco_scalars` hold GeV. Concluded from
  producing code + three corroborating consumers + the receipt's `rel_l1 == max_rel`
  identity, not from reading the arrays. One percentile print settles it.

**Convergence and estimator behaviour — entirely unobserved**

- Whether any full-event training converges at `niter=2`. No sweep has ever been run; no
  tool exists. The 0.026% (5→10) figure belongs to the 2D GBDT chain.
- The actual per-epoch val_loss curves, hence whether the epoch-8 model is best (M4). The
  pickled histories would answer it, but no full-event nominal has run, so none exists.
- Keras `EarlyStopping.restore_best_weights` semantics under TF 2.15 / TF 2.14. Only keras
  3.15.0 was readable locally. **One `inspect.getsource` call on-cluster fixes M4's severity.**
- Whether `clone_model` (`omnifold.py:263`) freshly initializes the subclassed PET model
  under TF 2.14/2.15. The completed recoil trainings are strong empirical evidence, but the
  weight-init semantics were not verified.
- Whether the ~1.5 GB step-2 `from_tensor_slices` constant and the full-size 5.3M `.shuffle`
  buffer (`omnifold.py:336-341, :354`) fit at nominal scale. Adjacent to the ladder; scales
  as tokens¹, so a 40-token fixture would exceed the 2 GB protobuf limit where the real
  12-token dump does not.
- Whether the composed Gate-4 closure legs would pass on real data **at all**: the ordinary
  closure has never run against the real dump (the `36ab84d` PASS predates the
  `g2-fullevent-v1` gate and is dead), and the stress closure has only run on rng clouds.
- Whether the stress closure passes on **any** hardware — it imports TF at module scope, so
  it was not runnable here.
- Prior dependence under a genuine re-unfold (M6). Needs the dump plus a retrain per prior.

**Covariance — largest structural gap**

- **There is no full-event covariance builder in this repository at all.** Grep for
  `fullevent` across `nd-unfolding/*.py` and `nd-unfolding/pet/*.py` returns only dump,
  loader, gate, closure, launcher and validator files — never a covariance builder. The
  entire UQ chain (`unified_throw_cov.py`, `analyze_universes_nd{,_5d}.py`,
  `pet_systematics{,_5d}.py`, `assemble_ctotal_bkgsub.py`, `adopt_unified_*.py`) operates on
  the scalar/recoil-lineage point clouds. So the audit question *"could the recoil-only floor
  leak into a full-event covariance?"* **cannot be answered by inspecting one — it does not
  exist.** M13/M14 are about the code that will be reused to build it.
- **The adopted ROOT products themselves.** `unified_throw_cov_fps.root`,
  `uq_universe_fps_covariance_combined{,_uthrow}.root`, the 4D/5D equivalents, the throw and
  block slabs, and the jitter-null values are all on `/pscratch`, gitignored and
  fingerprinted rather than committed. Every claim about their contents is derived from code
  + run log/ledger/status docs, **not from reading the matrices**. Specifically unverified:
  the realized `g` distribution beyond "median 1.000 / max 1.61 / 82 of 266 bins > 1";
  `diag(C_vert_sweep)` vs `diag(C_blocksum)`; and whether any shipped covariance currently
  fails PSD.
- `s_u·Δ_u` inner products (M14) — only the p7 **summary** JSONs are in this checkout.
- The float16 bad-row classification (exactly-0/inf vs negative-finite) — 37 GB of banks on
  `/pscratch`.
- What fraction of bank rows sit at the `RHO_CLIP` ceiling. The counts were printed as
  `[ratio][WARN] … clipping N/size ratios` and live only in Slurm logs on `/pscratch`.
- Whether the FPS unified/block ratio of 0.999 survives an identity-response null.
- Per-bin C_stat / C_ML / combined σ for the least-occupied reported bins — the ledger quotes
  only medians over 266 bins.
- Whether the LGBM CV>0 266-bin set is the **same** set as the truth-MC occupancy 266 in the
  floor study. The coincidence is suggestive but unverified; the two come from different
  inputs.
- Actual n_MC per reported bin for the **full-event** dump. All occupancy numbers used here
  are recoil-only xps2.

**Test and gate coverage not reached**

- **7 of the 340 tests never execute off-Perlmutter** (all in
  `test_fullevent_gate2.EndToEndLoaderBoundary` / `FailClosed` / `ReplicaReuseGuard` plus
  `test_gate2_target_runtime.TargetOnlyDataLoader`), because `test_fullevent_gate2.py:24`
  hardcodes a `/pscratch` REPO for the vendored DataLoader. Those are exactly the tests that
  reach the real loader boundary. This was **partly mitigated** by building a
  Perlmutter-equivalent copy and re-running the mutation matrix there (M3), but the
  equivalence is a repointed literal, not the real environment. `test_p3f_pet_fullevent_launcher.py`
  is skipped by `conftest` `collect_ignore` and was **not** mutation-tested at all.
- **Gate-3 was not audited.** `test_p3f_pet_fullevent_launcher.py` (frozen, 320 lines) is
  skipped here, and `validate_p3f_pet_fullevent.py` / `test_p3f_pet_fullevent_validator.py`
  were not read in depth. Gate-3 is a **gap**, not a pass.
- `test_fps_provenance.py` (372 lines) and `test_fps_cli_integration.py` were grepped, not
  read in full.
- **`pytest` was not run.** The 7 known failures are platform artifacts and a green run is
  near-zero evidence; the mutation work above is the substitute.
- The extraction / reweight-all stage (CLM-006's "2M train → reweight-all 49.2M") was not
  audited — B3 establishes that no full-event extractor exists, not that a correct one would
  be sound.
- Perlmutter shared-QoS memory policy. `sbatch_pet_fullevent_nominal.sh` requests
  `--qos=shared --gpus=1 --cpus-per-task=32` with **no `--mem`**, so the cgroup ceiling is
  whatever the proportional policy grants. ~13 GiB fits under any plausible share, but the
  policy was not confirmed.
- **Delta job 20558496's results were not read** (no cluster access; job deliberately left
  alone). M12 rests on the committed Gate-2 receipt and the launcher/driver source, not on
  the ladder's own numbers.
- The four allow-listed drifted bindings were accepted as submit-time provenance on the
  documented rationale; not re-derived from git history.

---

## 5. Recommended order of work

Perlmutter returns **2026-08-03 22:00 PT**. The sole copy of the G2 dump is on purgeable
`/pscratch` with no backup. Order accordingly: **durability first, then the things that make
the restore window productive, then the window itself.**

**Now, off-cluster, zero gate cost** (all of this can be done before 08-03 and none of it
touches a frozen file)

1. **Reproduce B4, B3 and B2 locally** — three one-liners in §2. Ten minutes buys certainty
   that the critical path is broken before it is stood up. Then pick B4's fix route:
   `PYTHONPATH` supplied from the submit environment is the only zero-gate option for the
   nominal, and also check whether the TF 2.15 module even has ROOT.
2. **Add the four behavioural loader assertions (M3) and the grid-equality assertions
   (M10)** to `nd-unfolding/tests/`, which is not hash-bound. Do this **before** the Gate-2
   re-issue, not after — that re-issue is precisely the window in which the loader has no
   behavioural coverage.
3. **Fix `verify_hash_bindings.py` (M11)** — basename fallback + honest counter labels — and
   add `nd-unfolding/unfold_nd_omnifold_unbinned.py` to the frozen-file map. The arbiter
   should be sound before it is relied on for the re-issues below.
4. **Prepare the Gate-4 re-issue as a single change set** (B2 + B3 + M7c + the fingerprint
   minor): driver persists niter/epochs/seeds/input-path/input-sha; validator reads
   edges/bin_order/seed_policy/`target.*`/`signed_target_hash` **from the artifact** and
   compares them against `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`; `build_gate4_report` FAILS
   rather than skips on `None`; `check_mc_index_order` requires `arange` coverage. Its 14+36
   tests are login-safe, so **the Gate-4 gate can be re-run before 08-03 without data or
   GPU.** Doing it now converts the restore window from "discover the gate is empty" to
   "run a gate that means something".
5. **Give the ordinary closure real power (M2)** — negative control, injected truth-level
   reweight, `norm_ok` in the verdict, raw-`w_truth` cross-check, and either feed the real
   `data` loader or drop the discarded build. `closure_fullevent_fps.py` is explicitly
   known-not-frozen. Also add the stress closure's absolute criterion (M8) and its
   verdict-logic unit test. **A closure that cannot be maximized by a null estimator is the
   single highest-value deliverable available before the restore.**
6. **Decide B1 explicitly and write the decision down**: (a) carry W1/W0 through step 1 —
   a Gate-2 two-file re-issue requiring the dump, so it must be planned now and executed
   post-restore; or (b) keep shape-only and add an explicit data-yield normalization to
   extraction, documented in `sec_method` as a deliberate convention — no frozen edit. **This
   is a physics-convention decision, not a code decision, and it should not be made under
   time pressure on 08-03.**
7. **Documentation-only corrections**, cheap and easy to lose later: `assemble_ctotal_bkgsub.py`
   docstring + `cretrain_no_double_count` (M14); the "MAT biased 1/N" scoping; the
   coverage-scope caveat and the A/B reconciliation in `coverage_valid_fps.json`;
   `sbatch_fullevent_dryrun_delta.sh` `TOKENS` 40 → 12 (known finding A).
8. **When job 20558496 lands, read it re-scoped (M12):** take the **2,000,000** rung as the
   answer for the publication nominal, compare against the 11.09 GiB Gate-2 anchor, and
   ignore the 40M / ×4 summary banner. **If it comes out near ~13 GiB, say so plainly and
   cancel the loader-refactor line of work** — that frees the whole 08-03 window. Do not
   re-submit the job; if it died, diagnose from its log.

**First hour after `/pscratch` returns — before any GPU**

9. **Back up `G2_FPS_MEFHC_P12.npz`** to `/global/cfs/cdirs/m3246/josephrb` and verify sha
   `fa6b3463…a29625`. It is 9.9 GB, single-copy, on purgeable scratch, and every remaining
   item depends on it. Also push the two Delta weight NPZs (`9a09125f…`, `85b595b2…`,
   ~532 MB, ~76 GPU-hr to regenerate) per the executor brief. **Nothing else competes with
   this.**
10. **Run the cheap login-safe reads that close four findings at once:** the GeV percentile
    print (M1), `R` for B1, the `pot_scale` cross-check against `dataPOTUsed`/`mcPOTUsed`, and
    the `import ROOT` check under the TF 2.15 module (B4). All are seconds of I/O and they
    determine what the rest of the window is for.

**Then, on-cluster**

11. **Execute the Gate-2 units re-issue (M1)** as one deliberate two-file change —
    `/1000` removed, `require(negative_signed_cells == 0)` respecified, the
    learned-vs-closed-form metrics promoted from telemetry to a thresholded gate (M7a) —
    followed by a Gate-2 canonical-runtime re-run on the real dump (~670 s, CPU-only) and a
    re-issue of both `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` and the independent-validation
    state JSON. Never hand-edit a sha. Fold in any B1 option-(a) loader change **in the same
    re-issue** — do not pay for two Gate-2 re-runs.
12. **Re-run the closures with power (M2, M8) against the real dump**, at the nominal
    niter/epochs/max-events, and only then re-issue the P5A closure receipt. A receipt from
    the current closure would be worth no more than the dead one it replaces.
13. **Then, and only then, spend GPU:** the niter 2-vs-5 pair (B5, ~2 × 1.2 h) and the
    3-seed ensemble spread (M5, ~3 × 1.2 h), with acceptance bars predeclared before
    looking. Both are diagnostics, not the nominal. Read the pickled val_loss histories from
    every one of them (M4) — free, and it answers whether model selection matters at all.
14. **Launch the P5A nominal last**, once the extraction path exists end to end (B3), Gate-4
    means something (B2), the normalization convention is settled and written down (B1), and
    the iteration count is either justified or changed (B5).
15. **Deferred until P5B is actually in view:** the bootstrap replica contract (M9) and the
    end-to-end joint prior re-unfold (M6). Both must be fixed **before the first replica or
    universe**, not after — a mis-estimated C_stat or an under-covered model-dependence band
    is not detectable downstream.

**Standing constraints observed throughout:** no publication nominal on Delta (no ROOT); no
promotion or extension of the recoil-only xps2 path; no third GPU-nondeterminism floor
repeat; `--bkg-mode purity` is a labelled control, never the nominal; never harvest a
synthetic-fixture run as physics evidence; never hand-edit a receipt sha256; and **do not
de-root the `/pscratch` literals** — `fullevent_fps_dataloader.py:611` and
`fps_verify_merged_receipt.py:22` are load-bearing.
---

# Addendum — measured host-memory ladder (Delta 20558496)

*Added by the orchestrating session, not by the audit agents. This supersedes both the
original ~310 GiB projection and any inference about finding B, because it is a
measurement rather than a reading.*

Delta job `20558496`, `COMPLETED 0:0`, 41:27 on `cn126`, ~11 CPU-hr, script at commit
`68f1291`. Five rungs, `--tokens 12`, `max_events = 0.8138 x rows` at every rung so the
materialize-then-subsample pattern of `fullevent_fps_dataloader.py:520-521` is reproduced
at each scale. Peak is per-process `VmHWM`, single rank.

| rows (signal) | max_events | peak RSS |
|---|---|---|
| 200,000 | 162,757 | 0.766 GiB |
| 2,000,000 | 1,627,575 | 2.554 GiB |
| 5,000,000 | 4,068,937 | 6.297 GiB |
| 10,000,000 | 8,137,874 | 12.558 GiB |
| 20,000,000 | 16,275,749 | 25.078 GiB |

Clean linear scaling: `peak_GiB = 1.238e-6 * rows + 0.239`. Excluding the
intercept-dominated 200k rung the slope is ~1.252e-6 GiB/row. The checkpoint trace puts
the peak at `after_build_truth_cloud_1` at every rung, exactly where predicted.

**The production case is rows = 49,152,885 (with max_events = 40M): ~61 GiB per rank,
~246 GiB across 4 ranks, against a 251.6 GiB node — about 98% of capacity.**

**The hard-OOM projection is refuted; "comfortable" is not the conclusion.** The original
~78 GiB/rank estimate was ~25% high (it assumed the full-size numpy temporaries in
`build_truth_cloud` all coexist; they are freed as the expression evaluates). But the
measured result still lands within ~2-3% of the ceiling, and two caveats push the wrong way:

1. **This was a CPU node.** Each rank on `gpuA100x4` additionally pins host memory for its
   CUDA context and TF's GPU allocator, which this measurement cannot see. So ~246 GiB is a
   **lower bound** on the real 4-rank GPU-node peak. A per-rank CUDA/TF host overhead of
   even ~1.5 GiB consumes the entire remaining margin.
2. **`sacct` undersamples.** It reported `MaxRSS 15149752K` (14.45 GiB) for a job whose
   largest rung measured 25.08 GiB by `VmHWM`. Do not size anything from `sacct MaxRSS`.

**Recommendation.** Do not launch P5A at `-np 4` on a 251.6 GiB node on the strength of
this. Either confirm with a real 4-rank GPU run at a reduced rung and measure the true
per-rank GPU-side overhead, or reduce the peak (shard before building the clouds, or build
them chunked), or use a larger-memory node — Delta has ~2 TB nodes in the `full` partition,
though Perlmutter GPU nodes are also 256 GB, so on Perlmutter this is a live risk.

**Known defect in the reporting script.** The ladder's summary prints a first
extrapolation line labelled `max_events=40M` which plugs 40,000,000 into a fit of
peak-vs-*rows*; that corresponds to a 40M-row fixture with max_events=32.5M, not the
production case. The physically correct line is the second one, `full 49.15M dump`. The
label should be fixed before anyone reads the first line as the answer.

---

# Addendum — adversarial re-verification of B1 (2026-07-29)

Four referees, each instructed to default to REFUTED: three Claude Code subagents (mechanics,
Delta feasibility, physics) and one Gemini 3.1 Pro via `agentctl` role
`refute-fe-norm-physics-agy`. Codex was unreachable this round (no `codex-homes/*` on the
local machine; `usagectl snapshot` returns `gate_ok: false` on exactly that) and
`claude-school` was unauthenticated, so the external cross-check is Gemini-only.

**This addendum supersedes recommendation item 6 above.** Item 6 framed B1 as a choice
between (a) carrying W1/W0 through step 1 and (b) keeping shape-only with an explicit
data-yield normalization at extraction. **Option (b) is refuted on physics grounds, and
option (a) as literally stated — deleting `normalize=True` — is also wrong.** Both referees
that examined the physics agreed the mechanism is real; they disagreed on whether a scalar can
repair it, and reading `omnifold.py:185` settles that against the scalar.

## Confirmed, and stronger than originally stated

The mechanism is not a code-reading conjecture. It is the measured behavior of the existing
recoil-only PET result: `ND_OMNIFOLD_RUN_LOG.md:466` gives `mean(w_push) = 1.0277`, the
higher-iteration retrain gives `1.0101` — it **fell**, while under-iteration predicts it
rising toward the data's 1.135 (`:930`). PET/CV = 1.018 and 1.018/1.135 = 0.897, matching the
reported `PET/GBDT = 0.8970` (`:913`) to three digits. The `:917-921` under-iteration
interpretation is superseded.

Mechanics of the erasure were verified by execution, not inspection: `normalize=True` yields
`data.weight.sum() = 999999.96`, omitting it yields the raw `15.0`, and
`d.weight.base is caller_array` is `True` — `dataloader.py:110-113` mutates a view in place.

## Refuted: a post-hoc scalar cannot repair it

`omnifold.py:185` is `new_weights = np.ones_like(self.weights_pull)`, with only `[pass_reco]`
overwritten by the classifier ratio. Off-acceptance events are pinned at **1 in both** the
correct and the normalized run — the normalized run does not carry `1/R` there — so the loop
is not scale-equivariant in the step-1 output. With `a(z)` the local reco acceptance, step 2's
optimum is `push'(z) = 1 + a(z)(R-1)` against `push(z) = 1`, and completeness
(`pet_systematics_5d.py:146-152,161`) is built from `w_truth` only and is identical in both
runs, so

    sigma_correct(bin) / sigma_shape-only(bin) = 1 + a(bin) * (R - 1)

which is acceptance-dependent. The best global scalar leaves residual `~ (R-1)(abar - a(bin))`:
a few-percent bin-to-bin distortion correlated with completeness, **worst precisely in the
low-completeness FPS-extension cells this measurement exists to report**. Area-normalizing does
not remove it, so shape-only is not a safe harbor. Characterize this as an
acceptance-multiplicative error, not a lost normalization.

## Refuted: deleting `normalize=True` is also wrong

The nominal trains on a bounded 2M MC subsample (`validate_pet_nominal_gate4.py:55-56`) while
the measured target is the full data+background inventory
(`fullevent_fps_dataloader.py:645-659`). With `normalize=False` the class ratio becomes the MC
*sampling fraction*, not `R`. `normalize=True` is load-bearing.

## The reference precedent was cited backwards

`_balance_weights` is an optimization fix (`omnifold_nn_core.py:158-169`: an MLP on imbalanced
class totals collapses to the trivial bias solution), and `_class_ratio` undoes its own side
effect. Neither concerns the DataLoader, which the reference loop never constructs. And the
restoration is **in-loop, per step, per iteration** — `fit_reweight` recomputes the ratio at
`:233` and applies it at `:246`, called twice per iteration (`:257`, `:266`). The precedent
mandates carrying the ratio through the loop, not patching the result afterward.

## The revised target

Make the step-1 class ratio equal the physical `R` from full-inventory POT-scaled sums: keep
the MC loader at 1e6 and pass `normalization_factor = 1e6 * R` to the data loader (the
argument already exists at `dataloader.py:13`), or restore in-loop as `omnifold_nn_core.py:246`
does. Preserves subsample invariance and the rate; no change to the vendored mechanism.

## Two gates entrench the defect

`gate2_target_runtime.py:411-412` and `:442-443` hard-assert the step-1 target sums to exactly
1e6 (`rtol=3e-6, atol=2.0`). Gate-4's `check_normalization`
(`validate_pet_nominal_gate4.py:107-110`, tol `1e-3` at `:61`) requires
`|sum(w*push)/sum(w) - 1| <= 1e-3`. **A correctly normalized unfold moves the rate ~13.5% and
would fail that contract by two orders of magnitude while the broken one passes.** Read
together with B2 — the Gate-4 CLI never passes `normalization=` — the contract as written
cannot detect this and would reject its own fix.

## Corrections to this document's Delta claim

Conclusion stands (no canonical Gate-2 on Delta); three of four reasons were wrong.
`:400`'s backend-string check derives from the same `refine_fn is None` predicate as `:398`
and is not independent. `refine_stay_positive` is pure NumPy+sklearn and never touches ROOT —
the module-level `import ROOT` at `unfold_2d_omnifold_unbinned.py:21` is an accident of file
layout. The `:402` identity guard binds bytes, not a filesystem, so a staged byte-identical
copy satisfies it. **The genuine blocker is the hardcoded non-overridable
`REPO = Path("/pscratch/...")` at `gate2_target_runtime.py:35`** (also
`fullevent_fps_dataloader.py:40`), which dies at `:209` before ROOT is reached. "Code, not
policy" was a false dichotomy: `RESTORE-2026-08-03.md:198-206` HARD BAR #1 is explicit.

## New audit weakness

`refinement_is_learned_production` asserts only that no refiner was *injected*
(`fullevent_fps_dataloader.py:664` = `refine_fn is None`). Monkeypatching
`fed.learned_stay_positive_refiner` keeps the flag `True` while a substitute runs. The
validator records but does not assert the loader/u2d sha256 (`:481-486`); the only sha freeze
lives in `run_gate2_target_validator.sh:19-21,39-41`.

## Deliverable: `nd-unfolding/pet/check_step1_class_ratio.py`

Login-safe, read-only, reads only small 1-D members. Fail-closed against the promoted Gate-2
receipt: recomputes the signed-data numerator and refuses to report `R` unless it reproduces
`raw_signed_sum = 4006528.6006158064`. Verified both paths against a synthetic fixture built to
the receipt constants — valid input reports `R` with check `OK`; a 10%-perturbed background
exits 1. `w_truth` is RAW, not POT-scaled (`fullevent_fps_dataloader.py:551`; convention at
`dump_pointcloud_inputs.py:183-186`), so the physical denominator is
`pot_scale * sum(w_truth[pass_reco])`; both conventions are reported because they differ by
`1/pot_scale ~ 4.7x`.

`R` remains unmeasured until the 08-03 restore. The sign, mechanism, and non-scalar character
of the error do not depend on its value.
