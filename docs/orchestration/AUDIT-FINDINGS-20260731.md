# Audit findings — repo-wide + analysis note (2026-07-31)

> **Read after [`AUDIT-FINDINGS-20260728.md`](AUDIT-FINDINGS-20260728.md),
> [`AUDIT-FINDINGS-20260729.md`](AUDIT-FINDINGS-20260729.md) and
> [`AUDIT-FINDINGS-20260729-B.md`](AUDIT-FINDINGS-20260729-B.md).** All three stand. Findings
> here that merely corroborate them are marked `[corroborates]` inline rather than presented as
> new; §6 lists what is genuinely novel.
>
> Produced by a four-account parallel audit (codex personal, codex school, claude school,
> gemini) run with **deliberately minimal prompts** — one sentence or less per lane — followed
> by two cross-validation rounds in which each account verified a *different* account's
> findings. One lane was discarded (§7). Every finding carries an explicit evidence tier (§2).

## 1. Audit basis and its limits

- **HEAD moved during this audit**: `fa06bb6 → 1a56ebc → 1d72cc2`. Another session was live in
  the repo throughout. Round-1 lanes read at approximately `1a56ebc`; both round-2 lanes state
  they verified at `1d72cc2`. Line numbers below were re-read by the orchestrating session at
  `1d72cc2` wherever the tier is **A**.
- `python3 docs/orchestration/verify_hash_bindings.py` → **exit 1, `*** BINDINGS BROKEN ***`**,
  102 resolved / 94 OK / 4 known drift / **4 active mismatches**. This is a change of state from
  the 2026-07-29 pass, which recorded `ALL BINDINGS INTACT`, exit 0. See J11.
- `python3 -m pytest nd-unfolding/tests -q` → **9 failed, 406 passed, 1 skipped**. Executed, not
  relayed.
- **This document is not the only file this session wrote.** Two test files were modified
  (J38, J39) and are disclosed rather than folded in silently. No receipt was touched, no
  sha256 hand-edited, no `git` write command run, no job submitted.
- Delegate line citations were frequently off by 5–15 lines (e.g. `unified_throw.py` 271 vs
  actual 287; the LightGBM universe launcher 69 vs actual 74). Tier-A citations below were
  re-read directly; remaining tier-B line numbers should be treated as approximate. **Exception:
  the fifteen findings re-verified on 2026-08-01 (§2) carry line numbers re-read at `6cabd4d`, and
  every citation in them was checked — the delegates' line drift was NOT reproduced in that set.**
- Round-1 prompts were, in full: *"Audit nd-unfolding/pet. Find real bugs."* / *"Audit
  docs/analysis-note. Which claims does the code not support?"* / *"Audit docs/orchestration.
  Do the gates actually gate?"* / *"Audit this repo for correctness bugs."* The terseness was
  the experiment; it did not degrade yield (§8).

## 2. Evidence tiers

| Tier | Meaning |
|---|---|
| **A** | Executed or re-read directly by the orchestrating session at `1d72cc2`. |
| **B** | Found by one account, independently confirmed by a second account that was given the first's findings and asked to mark false positives. Not independently re-run here. |
| **C** | Single-source. Plausible, cited, but neither cross-validated nor re-verified. Treat as a lead. |

Both cross-validation rounds returned **zero false positives**. In several cases the verifier
*strengthened* the finding (J07, J02) or corrected a sub-claim while upholding the substance
(J04, J09). That is recorded per-finding.

> **Tier-C verification pass, 2026-08-01.** Every tier-C finding (J19–J27, J29, J31–J33, J36,
> J37) was re-verified by direct read at `6cabd4d`, plus git archaeology and one computation from
> a committed receipt. **Result: 14 of 15 promoted, 1 deleted, 1 sub-claim deleted.** Three reach
> tier A on this document's own definition (J22, J29, J36 — read or executed directly here). The
> tier-C population behaved differently from the tier-A/B population: no finding was wholly
> wrong, but **six carried an incorrect scoping or characterization** that a single-source pass
> had no way to catch, in both directions — J31/J32/J33 were live-sounding but are latent,
> J22/J36 were hedged but are provable, J24 understated its own number. **The lesson: for a
> single-source finding, the code fact is usually right and the *consequence* is usually wrong.**
> Verify the blast radius, not the citation. Line numbers below were re-read at `6cabd4d`;
> `app_negweight.tex` numbers are at `b27d1e1`, which moved them by +5 after line 52.

## 3. PET full-event path (`nd-unfolding/pet`)

Source: codex personal, cross-validated by claude school.

- **J01 — The publication estimator is mislabelled. [tier A]**
  `FULL_EVENT_FEATURE_CONTRACT.md` defines two IDs and forbids mixing them:
  `pet-fullevent-fps-v1` is the full-schema publication estimator (full muon object + reco
  vertex + view/timing), while `pet-reduced-fps-cross` is the `{pT,p‖}` estimator marked
  **"CROSS-CHECK ONLY — never a publication lateral/central source."**
  `fullevent_fps_dataloader.py:133` sets `DEFAULT_EVT_FEATURES = ("pt", "pparallel")` — the
  reduced set. `grep` for `reco_muon|reco_vertex|reco_view|reco_time` across the loader and the
  driver returns **zero hits**, though those arrays exist in the G2 dump. Yet
  `train_fullevent_nominal.py:32` sets `ESTIMATOR_FINGERPRINT = "pet-fullevent-fps-v1"`.
  The contract's own text makes this self-refuting. **Gate-4 must stay closed.**

  **FIXED 2026-08-01 — the loader reads the full event.** `DEFAULT_EVT_FEATURES` is now the
  13-feature publication schema: the reported `(pT, p‖)`, the full reconstructed muon object from
  `reco_muon` (px, py, pz, E, **cos φ, sin φ**, q/p, MINOS match) and the reco vertex from
  `reco_vertex`; `reco_view`/`reco_time` (and the `data_*`/`bkg_*` twins throughout) become token
  columns 3,4 of the reco cloud. Three judgment calls worth stating, because none is forced by the
  arrays:
  - **φ is encoded as (cos φ, sin φ), not as a raw angle.** z-scoring an angle places φ = −π and
    φ = +π at opposite ends of a feature the network cannot glue back together. This is CLM-008
    F10 — already fixed once, for the truth cloud's KNN coordinates — recurring one level up.
  - **view/time went into the CLOUD, not the event block**, though the contract listed them under
    `event_reco`. They are per-token vectors whose length the dump contract pins to the cloud's
    token dimension, and summarizing them into event scalars would discard exactly the per-hit
    structure §B of the interface request asked for.
  - **`eavail`/`q3` were left out**, though they are dumped on both legs and free. Whether they
    earn a place is RESTORE Step 7's open measurement; adding them in passing would have
    prejudged it, and they are not part of what `pet-fullevent-fps-v1` claims.

  The two legs now differ in width — the truth leg has no muon object, no vertex and no MINOS
  counterpart, and requesting one is refused by name at construction time — so `meta` carries
  `n_evt_reco` and `n_evt_truth` and every caller builds the two networks separately. Gate-4 now
  **freezes both feature lists and the cloud's token columns, read from the artifact**, so the
  fingerprint means the schema it names: a reduced-schema result is refused by a named check
  rather than validated. Re-issued as
  [`state/p3f-pet-gate4-launch-code-gate-20260801b.json`](state/p3f-pet-gate4-launch-code-gate-20260801b.json)
  per RESTORE Step 2b, `PASS_CODE_ONLY`, no physics re-run. Tests:
  `nd-unfolding/tests/test_fullevent_schema.py`.

  *One thing the fix exposed on the way past.* `make_synthetic_g2_fullevent._muon` built a
  **6-column** `[px,py,pz,E,charge,quality]` block against the dumper's 7-column
  `[px,py,pz,E,phi,qp,minos_ok]`, and filled plausible values on `!pass_reco` rows where the dump
  writes −9999. It passed every G2 gate for as long as nothing read it, because
  `fullevent_dump_contract.assert_inventory_alignment` checks that block's **row count and never
  its width**. That is the same shape as J07: the contract's checks did not bind the thing that
  mattered. The fixture now matches the dumper, the width is checked where it is consumed, and the
  loader's mirrored column orders are pinned against the dumper's own constants by a test — a
  hand-mirrored column order being precisely what goes stale in silence.

- **J02 — No full-inventory inference or extraction exists. [tier B, strengthened]**
  Training selects 2M of 49,152,885 MC rows and the driver saves only that subsample's weights.
  The verifier sharpened the original claim: `extract_nominal_bkgsub.py` is the *recoil/5D*
  extractor, and there is **no full-event extractor in the tree at all**. The recoil loader has
  a `--reweight-all` full-cloud pass that the full-event driver dropped. Key and coverage both
  mismatch (`weights_push` vs `w_push`; 2M vs `arange(49152885)`).

  **ADDRESSED 2026-08-01, code-only.** `nd-unfolding/pet/extract_fullevent_fps.py`, in two stages:
  `push` (TensorFlow) streams the FULL 49,152,885-row inventory through the trained step-2 network
  in chunks and writes `w_push` over `arange(N)`; `xsec` (ROOT + numpy, no TF, no GPU) turns that
  into the extended-FPS differential cross section. Split because the push pass costs GPU time that
  must not be re-spent when the extraction recipe changes, and because the extraction is then
  reviewable on a login node.

  Three things that were not obvious until the pass was written:
  - **The input space has to be REPRODUCED, not re-derived.** `event_truth` was z-normalized with
    the 2M training subsample's statistic. Recomputing it over 49.2M rows feeds the trained model
    differently-scaled inputs and returns confident wrong weights with nothing downstream able to
    tell. The driver now persists the statistic in an `inference_contract`; an artifact without one
    is refused rather than reconstructed.
  - **The reweight is the engine's own.** CLM-008 F3 requires one shared implementation of the
    logit cap across nominal, replicas, universes and extraction. Rather than re-type it or edit
    the hash-bound engine, `MultiFold.reweight` is invoked on a minimal instance; a test reads the
    engine's source and fails if that method grows a dependency the shim does not supply.
  - **The full pass is cross-checked against the training pass** on the 2M rows they share. Without
    that, a model rebuilt at the wrong architecture — or fed a re-derived normalization — produces
    plausible weights and the whole reweight-all is unfalsifiable.

  The extraction arithmetic is a **port** of `pet_systematics_5d.PETxsec5D.xsec` to the two FPS
  axes through the shared `xsec_nd.extract_cross_section_nd`, minus `PETxsec5D`'s `comp_rescale`
  (which anchors completeness to a validated GBDT 5D ROOT product that does not exist for this
  domain; inventing an anchor would silently rescale the answer, and its absence is recorded in
  the telemetry). **It has never run**: the push stage needs a trained checkpoint and the xsec
  stage needs ROOT, so both are blocked until the 08-03 restore. Its guards and its arithmetic are
  unit-tested (`nd-unfolding/tests/test_fullevent_extract.py`); the pass itself is unexecuted.
  Bound additively by the 08-01b Gate-4 receipt.

- **J03 — The Gate-4 validator returns PASS without running its advertised checks. [tier B,
  reproduced]** The verifier re-ran the repro: 18 checks, 0 failed, exit 0 — with
  `marginal:pt_ppar_l1`, `cap:saturation_frac`, `closure:ordinary_pass`,
  `freeze:central_vector_len` and `freeze:reported_mask_len` all `ran=False`. `main()` builds
  `frozen_observed` from `FROZEN` itself, so four freeze checks compare the validator's
  constants to themselves. `weights:full_coverage` uses `len(imc)`, making it a row-alignment
  check rather than a coverage check. The launcher never invokes the validator at all.

- **J04 — The certified Gate-2 target is silently rebuilt, not consumed. [tier B, sub-claim
  corrected]** `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` is referenced only by the Gate-2
  validator and hedge controller, never by the Gate-4 path, which re-runs the full 4,680,719-row
  refinement inside `build_fullevent_loaders`. *Correction from the verifier:* the claim that
  omitting `random_state=45` prevents reproduction overstates — `refine_kwargs=None` yields an
  effectively deterministic exact GBT, so the numbers would likely match. The load-bearing
  defect is that **no reproduction or hash comparison is attempted at all**.

- **J05 — Stay-Positive is fitted in the wrong feature space. [tier B]** The refined target is
  learned from `(pT, p‖)` only, then attached to cloud-plus-event space for the step-1
  classifier. Background structure in recoil clouds, vertices, view or timing cannot be
  subtracted conditionally. Already tracked as B-5, with `demo_b5_refiner_feature_space.py`
  demonstrating that the muon-projection agreement is an algebraic identity, not evidence.
  `[corroborates AUDIT-FINDINGS-20260729-B]`

  **NARROWED 2026-08-01, not closed.** `g(x) = D/(D+B)` is now fitted on the same normalized event
  block the step-1 classifier is conditioned on, so the vertex and the full muon object — two of
  the four things this finding names — are inside the refiner's feature space. The remaining two,
  **recoil cloud structure and the per-token view/timing**, are not, and cannot be by widening a
  column list: `refine_stay_positive` is a tabular classifier over a fixed-width design matrix,
  and giving it a variable-length token cloud is a different (set-valued) estimator, not a wider
  argument. The loader records this in `meta['target']['refinement_feature_space']` so the
  narrowing is visible in the receipt rather than only in a comment, and a test asserts the
  disclaimer is present. **B-5 stays open on the cloud.**

  Consequence to carry into RESTORE Step 2: the negweight-refined Gate-2 target changes
  **numerically**. `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` and the Gate-2 runtime receipt
  describe a target the loader no longer produces. The rebuild was already owed on a bytes
  argument (the loader has been red against both Gate-2 receipts since the B1 patch); it is now
  owed on a physics one. Do not read the difference between old and new as a regression.

- **J06 — `w_reco` is unused by the estimator. [tier B]** The loader passes one weight vector;
  MultiFold uses it for both reco and truth legs. `gate2_target_runtime.py` now blocks
  certification when `w_reco != w_truth`, but the training loader only writes telemetry and
  never raises, and the on-disk Gate-2 receipt carries no `b4` block — confirming it predates
  the guard. Systematic endpoints where the weights differ cannot be processed correctly.

- **J07 — Inventory hashes do not bind features to weights. [tier B, extended]** Signal identity
  binds only `(w_truth, pass_truth)`, data only `measured_pc`, background only
  `(w_bkg, bkg_indices)`. Both accounts reproduced: reversing the row order of `reco_scalars`,
  `truth_scalars`, `part_reco` — **and `measured_scalars`**, which the original finding missed —
  leaves `assert_identity_consistency` returning `True`. `measured_scalars` is the data-side
  event feature block actually fed to step 1.

- **J08 — Frozen bindings are broken at HEAD. [tier A]** See J11; same evidence, listed in both
  sections because it invalidates the Gate-2 runtime receipt and the Gate-4 `PASS_CODE_ONLY`
  receipt specifically. `PET_UQ_REMEDIATION_STATUS.md` still reads "built, hash-bound, and
  frozen".

- **J09 — The frozen configuration contradicts the implementation. [tier B, sub-claim
  corrected]** The contract specifies batch 1024; the driver uses 512. `NOMINAL_SEED_POLICY`
  omits `batch_size`, so the freeze cannot catch the drift. *Correction from the verifier:*
  using `pet-fullevent-fps-v1` as a static ID label is not itself the error — the contract
  defines it as an ID, distinct from the fingerprint recipe. The verified defect is that the
  documented content-hash recipe **is never implemented anywhere in the tree**.

- **J10 — Nominal publication writes are non-atomic. [tier B]** `train_fullevent_nominal.py:162`
  is a bare `np.savez_compressed` — no temp file, no `os.replace`, no no-clobber guard. The repo
  already contains the correct pattern (`write_fullevent_npz_atomic`); the driver ignores it.
  See J35 for the same defect class at repo scale.

  **FIXED 2026-08-01.** The pattern was generalized into `nd-unfolding/pet/atomic_write.py`
  (temp sibling → fsync → `os.replace` → completion marker last, plus `overwrite=False`), and the
  driver now calls it. The no-clobber guard refuses to replace an output that already carries a
  *valid* completion marker (`--allow-overwrite` opts in) and runs **before** training, not after;
  a partial leftover carries no marker and is freely overwritten, which is the case the old
  behaviour had backwards. The driver also reports the path actually written — numpy appends
  `.npz` to a name that lacks it, so the old success line could name a file that did not exist.
  No physics changed: same arrays, keys, seeds and sums. Gate-4 re-issued as
  [`state/p3f-pet-gate4-launch-code-gate-20260801.json`](state/p3f-pet-gate4-launch-code-gate-20260801.json)
  per RESTORE Step 2b, `PASS_CODE_ONLY`, no physics re-run. Tests:
  `nd-unfolding/tests/test_atomic_write.py`.

  *One thing this fix deliberately did not do.* `fullevent_dump_contract.py` — the file J10 names
  as the correct pattern — was **not** refactored to delegate. The delegation was written, went
  green, and was reverted: that file is frozen by `state/g2-dump-submit-20260719.json`, a
  **data-provenance** receipt recording which code produced `G2_FPS_MEFHC_P12.npz`, the only
  `g2-fullevent-v1` input in existence. Re-issuing it would rewrite what ran at submit time, which
  is exactly what `verify_hash_bindings.py` refuses. Six duplicated lines are the cheaper cost.

## 4. Hash bindings and gate machinery (`docs/orchestration`)

Source: claude school, cross-validated by codex personal. **All six confirmed, no false positives.**

- **J11 — The suite is red, so the boolean gate is saturated. [tier A]**
  `verify_hash_bindings.py` exits 1 on exactly four files: `train_fullevent_nominal.py` and
  `validate_pet_nominal_gate4.py` (both from `p3f-pet-gate4-launch-code-gate-20260721.json`),
  `fullevent_fps_dataloader.py` (from `g2-gate2-construction-20260719.json`), and
  `gate2_target_runtime.py` (from `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`).
  `1a56ebc` deliberately refused to silence these via `KNOWN_PREEXISTING`, and that call is
  correct — repairing them would assert a PASS that never happened. **But the consequence is
  that `test_no_new_broken_hash_bindings` is a boolean assert on `returncode == 0` that is
  already `False`.** A fifth break cannot change the outcome, and a red that *silently
  disappears* is equally invisible. Proposed remedy: an explicit expected-red baseline pinning
  the four `(path, want, got, receipt)` tuples plus owning gate and re-issue step, failing on
  **any** deviation in either direction. **Sequencing:** do this *after* the Gate-4 Step 2b
  re-issue, which resolves two of the four tuples; pinning all four now guarantees a rewrite.

- **J12 — 3 of 18 shell pin definitions are never walked, and the floor cannot see it.
  [tier B]** `_VAR_DEF` (`verify_hash_bindings.py:103`) anchors on `\s*$`, so a path assignment
  carrying a trailing comment does not parse. All three validator paths in
  `sbatch_p3f_pet_fullevent_evloop_array.sh:59-61` carry one, so the pins are dropped — and the
  dropped pins are the authoritative `P3F → domain → base` validator chain. `SHELL_PIN_FLOOR = 10`
  cannot catch it because resolved is *exactly* 10 and both sides of the ratio come from the same
  parser. Fix: cross-check the `_PIN_DEF` count (18) against collected pins (15). Latent, not
  live — all three currently match.

- **J13 — The all-12 premerge gate runs a validator frozen by nothing. [tier B]**
  `merge_g2_gate1_mefhc.sh` existence-checks and then executes `validate_g2_gate1_pairs.py`,
  which is covered by **no** binding while carrying four pins of its own that nothing walks. Its
  `EXPECTED_GATE_SHA` pins the validation *receipt*, not the validator, and the verifier added
  that the argument passed at line 45 is never consumed by the inline check. The gate's own
  decision procedure can be edited freely with every check green.

- **J14 — Python-resident pins are an entire unwalked class. [tier B]** The verifier globs
  `*.json` and `*.sh` only. Ten 64-hex pin constants live in `*.py`, including
  `gate2_target_runtime.py:EXPECTED_NPZ_SHA256` and five in `test_p3f_pet_fullevent_launcher.py`.
  The argument that justified walking shell pins in `fa06bb6` applies verbatim.

- **J15 — `collect()` drops unpaired `*_sha256` keys without counting them. [tier B]** Fields
  lacking a `base`/`base_path`/`base_file` sibling are dropped before `pairs` — neither checked
  nor counted in the "unresolvable" tally. Gate-3's `files.domain_validator_sha256` and
  `files.base_validator_sha256` are affected. Both are covered redundantly elsewhere, so no live
  hole; but a silent zero is the exact failure mode this file exists to prevent.

- **J16 — Nothing runs any of it. [tier B]** No `.github/workflows`, no active git hook, no
  pre-commit config, nothing in the waker/scrontab path invokes pytest or the verifier.
  `AGENTS.md:401` cites the 2026-07-26 incident but sets no rule to run the checker. The
  docstring's "run this before and after any sweeping edit" is advisory to whoever remembers.

## 5. Analysis note (`docs/analysis-note`)

Source: codex school, with an independent numbers-vs-ledger sweep as cross-validation.
J19–J27 re-verified 2026-08-01 (see §2); J17/J18 were already fixed before that pass.

**Pattern across the nine note findings.** Eight of nine are *emphasis* defects, not errors: in
almost every case the technical section states the limitation correctly and quantitatively, and a
summary, intro bullet, abstract line or paragraph heading then drops the qualifier. J19
(`sec_method` discloses / `sec_intro` does not), J24 (§3d-anchor quantifies / four summaries say
"reproduces"), J25 (§pet-projection-next limits it / `sec_results` does not), J26 (`sec_method`
says "within 2 %" / the appendix says "few-per-mille"), J27.1 (body says 46 % / exec summary says
"fills"). **Two are substantive and need work, not wording:** J21 (the PET central value is not
background-subtracted and the note implies it is) and J22 (the FPS footing claim is
chronologically impossible). Triage accordingly — the wording set is cheap and should be done in
one pass; J21/J22 need a decision about the products.

- **J17 — The headline 2D central value and its uncertainty budget use different classifiers.
  [tier A]** `sec_method.tex` describes LightGBM as the production classifier. The production
  launcher `sbatch_unfold_2d_MEFHC.sh` passes **no** `--estimator` flag, so
  `unfold_2d_omnifold_unbinned.py` takes its default `"exact"` (single-threaded exact-split
  sklearn `GradientBoosting`). The systematic-universe launcher (line 74) and the bootstrap
  launcher **do** pass `--estimator lgbm`. So the published central value is exact GBT while its
  covariance ensemble is LightGBM, and the note calls the pair a single estimator-matched
  production result.

- **J18 — The stale UQ appendix contradicts the main text, and the two reach opposite
  conclusions. [tier A]** `sec_systematics.tex` gives systematic `3.21e-39` / 6.830 %, combined
  `3.22e-39` / **6.865 %**, against paper `TotalCov` 6.86 %. `app_statmethods.tex:508-515` still
  gives systematic `2.463e-39` / 4.783 %, combined `2.470e-39` / **4.822 %**, and concludes in
  prose that "the combined OmniFold envelope is ≈70 % of the paper's per-bin median
  uncertainty". The main table says the envelope essentially **matches** the paper; the appendix
  says it is 30 % smaller. The statistical row differs too (0.549 % vs 0.564 %). The independent
  ledger sweep corroborates from a second direction: the appendix's combined pull mean/RMS
  `0.069/0.466` against the active ledger's `0.051/0.409`, an inconsistency
  `docs/INTEGRATION_CHECKLIST.md:80` already records as unresolved.

- **J19 — "No binning until the final histogram" is false for the headline method.
  [tier B — verified 2026-08-01, one sub-claim corrected]**
  The default `purity` background mode assigns every data event a `D−B` weight via analysis-bin
  lookup *before* training, in both implementations. Confirmed: default `--bkg-mode purity` at
  `unfold_2d_omnifold_unbinned.py:1008` and `unfold_nd_omnifold_unbinned.py:508`; the per-event
  analysis-bin lookup is `build_measured_training_2d:358-367` (`FindFixBin` → `max(0,D−B)/D`) and
  the ND `histnd`-on-`edges` equivalent at `:819-823`. The production launcher
  `sbatch_unfold_2d_MEFHC.sh:38-43` passes no `--bkg-mode`.

  *Sub-claim corrected:* "reporting bins are not freely changeable after the fact" is too strong.
  The reported histogram can be rebinned freely; what is frozen is the reco grid the purity weight
  was computed on. *Scope corrected — the finding attacked the wrong target:* `sec_method.tex:53-54`
  already states "This correction is, deliberately, the one place the analysis binning enters
  before the final histogramming." The note is not silent and not self-contradictory in the method
  section. The live defect is the **unqualified intro bullet** at `sec_intro.tex:36-38` ("**No
  binning at unfold time.**"), which the method section then walks back. Fix the intro bullet.

- **J20 — The documented "canonical LightGBM seed scan" points to a script that uses histogram
  GBT. [tier B — verified 2026-08-01, as written]** `app_statmethods.tex:121` cites
  `sbatch_unfold_2d_MEFHC_5iter_seedscan.sh`, which passes `--estimator hist` at `:61` and whose
  own header (`:15`, `:23`) documents it as the HistGBT scan. The appendix's worked example says
  "$n=10$ `lgbm` trials" and its covariance output path is `uq/seedscan_lgbm_ml/`.
  **The correct driver exists and was not cited:** `2d-unfolding/seedscan_lgbm/run_seedscan_lgbm_interactive.sh`
  (`--estimator lgbm` at `:61`, seeds 1–10, writing `seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed{1..10}.root`).
  Documentation-pointer error only; the quoted numbers match the lgbm output directory. Swap the
  citation.

- **J21 — The PET result is not a production-contract-equivalent cross section.
  [tier B — verified 2026-08-01, strengthened]** All three code claims confirmed, and the
  measured-weight claim is literal:
  - `dump_pointcloud_inputs.py:629` writes `measured_weights=np.ones(len(meas_cl))`.
  - The recoil dump `main()` (`:482-637`) reads only `mc_signal_reco` and `data` — **no
    `mc_background` tree at all**. Its schema stamp at `:624` is `"recoil-only-crosscheck"`.
  - `pet_vs_gbdt.py:run_absolute` (`:44-99`) bins truth-side push weights and divides by
    completeness; there is no background term anywhere in the extraction.
  - `make_figures.sh:68-69` passes `--pc of_inputs_pc.npz` while `:66` and `:80` use the
    coverage-fixed `of_inputs_pc_fullcloud.npz` / `pet_weights_fullcloud.npz`. Already tracked as
    KNOWN_ISSUES #18.

  **Strengthening.** `sec_pet.tex:70-71` states "The calculation uses the same
  background-subtracted five-dimensional measured target as the scalar GBDT." That describes the
  5D uncertainty product, not the 4D central value quoted at `:41-43` — a reader will merge them,
  and the note gives no cue not to. Separately: at the note's own ~3 % background scale, leaving
  background in the data biases PET **high**, so the training-configuration gap behind the 0.912
  ratio is *larger* than 8.8 %, not smaller. First-order estimate; not a quotable number.

- **J22 — The quoted extended-fiducial/FPS result cannot have used the claimed negative-weight
  baseline. [tier A — verified 2026-08-01; upgraded from "not shown to" to a date proof]**
  The claim is `app_negweight.tex:227-228`: negweight injection is carried "as the baseline
  subtraction for the extended-fiducial analysis (§sec:fps)". It is impossible:
  - `σ_ext = 4.502e-38` was produced **2026-06-10**, job 54244120
    (`VALIDATION_LEDGER.md:251`, re-verified post-fix at `:359`). No later regeneration is recorded
    anywhere in the ledger or run log.
  - The negweight driver code landed **2026-07-11** (`cf8a4a6`). On 2026-06-10 it did not exist.
  - `sbatch_fps_mefhc.sh` was created 2026-06-10 (`29a1186`) with **no** `--bkg-mode`;
    `git log -S"bkg-mode negweight-refined"` puts that flag's arrival at **2026-07-20**
    (`541dd48`, a "WIP: pre-shutdown snapshot"). `git show 29a1186:` on the launcher confirms the
    flag was absent when the product was made.
  - The negweight-refined FPS production never ran. `uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md:262-289`
    quarantines the ten existing endpoints as "**PURITY CONTROLS**, not publication inputs"; the
    `RUNS.tsv` rows MIG-C3 / V1R2 / C4 / V1R3 each record "No negweight-refined endpoint authorized".

  A month-wide date gap, not an evidentiary one. The note's claim must be demoted to intent
  ("the baseline for the extended-fiducial analysis **going forward**") or the product regenerated.

- **J23 — Closure does not "mirror the production analysis".
  [tier B — verified 2026-08-01, refined]** The claim is `sec_method.tex:207-211`. Confirmed in
  both drivers: ND `:786` `cmask = pass_reco & pass_truth`, `:792`
  `measured_weights = w_reco[cmask]` — **the purity down-weight is bypassed entirely** — and
  `:926-927` `completeness = np.ones(...)` with `print("[INFO] closure: completeness=1")`; 2D
  `:1518` same mask, `:1393-1394` skips the truth-denom load so the denominator self-consistently
  degenerates.

  **Strengthening the finding missed.** The same section credits `c` as "a monitored self-check (a
  configuration that dropped the misses would surface as `c<1`)" at `:226-228`. Closure hard-sets
  `c=1`, which disables *precisely that check* — the one the note advertises two paragraphs
  earlier. *Refinement:* under `--bkg-mode negweight/negweight-refined`, closure **does** inject
  and subtract simulated background (`:806-818`), so the background sub-claim is purity-specific,
  not general.

- **J24 — "Every higher-dimensional result reproduces its predecessor under marginalization" is
  too categorical. [tier B — verified 2026-08-01; the finding understated its own numbers]**
  `sec_3d.tex:77-84`: +0.95 % on total σ, per-bin ratio median 1.0016, χ²/ndf 4.98, ~4.4 % per-bin
  scatter. `VALIDATION_LEDGER.md:434-436`: `check_4d_anchors.py` PASS, 4D/3D integral ratio
  0.9960, projection differences 0.38 % / 0.64 % / **1.68 %**.

  *Correction:* those three figures are **medians, not maxima**, so "differ by up to 1.68 %"
  understates the per-bin spread. The overclaim is summary-level only — `sec_execsummary.tex:22`,
  `main_note.tex:50`, `paper_body.tex:86` and `sec_summary.tex:17` all say "reproduces", against
  the note's own §3d-anchor. "Passes the projection anchors within ≈1–2 %" is supported.

- **J25 — "Any projection or dimension can be obtained without re-unfolding" is unsupported.
  [tier B — verified 2026-08-01, strengthened]** The claim is `sec_results.tex:170-174`. The note
  refutes it at `sec_pet.tex:207-215`: "They do not turn the recoil-derived weight into a
  full-event weight or remove the prior conditional for omitted muon information."

  **Strengthening.** The offending sentence calls this "a capability we exploit for the 3D
  extension (§sec:3d)" — but the 3D result is a **new unfold with `E_avail` added as a classifier
  feature**, not a projection of the 2D result. The example cited in support is the
  counter-example. Qualify to "for observables in the classifier's feature space".

- **J26 — Negative-weight validation does not establish full covariance equivalence.
  [tier B — verified 2026-08-01, strengthened; one new sub-defect already fixed]**
  Confirmed. The entire covariance evidence is two scalars (`values.tex:109-111`: systematic
  √tr 2.9828e-39 / 3.0242e-39 = 0.986; statistical 1.7260e-40 / 1.7576e-40 = 0.982).
  `app_negweight.tex:216-218` concludes it "reproduces not only the central cross section but its
  full covariance, **per bin and in aggregate**". A trace ratio is one number; per-bin,
  correlation and eigenmode comparisons are absent. Note the asymmetry the finding did not draw:
  the *central-value* comparison **is** per-bin (median 1.000, RMS 1.4 %, worst bin −12.6 %), so
  the sentence conflates a per-bin central-value result with an aggregate-only covariance result.

  **Two sub-defects found in verification:**
  1. **OPEN.** `app_negweight.tex:215` calls the residuals "few-per-mille". They are 1.4 % and
     1.8 % — off by ~5×, and `sec_method.tex:67-68` describes the same comparison correctly as
     "to within 2 %". The appendix disagrees with the method section about its own numbers.
  2. **FIXED `b27d1e1`.** `app_negweight.tex:55` previously said the comparison used "the
     histogrammed gradient-boosted density estimator used for **the production result**" — a
     residual of the pre-J17 state, left standing when J17 was corrected in `sec_method.tex`
     only. Now corrected in place, and correctly: `hist` is neither the production central
     backend (`exact`) nor the ensemble backend (`lgbm`), so per `values.tex:91-95` this
     validation establishes equivalence **on a third backend**, and its transfer to the
     production configuration is an assumption rather than a demonstration.

- **J27 — Several physics interpretations are causal claims the code supports only as
  associations. [tier B — verified 2026-08-01; 3 of 4 sub-claims confirmed, 1 deleted]**
  1. **Confirmed, narrowed.** `sec_3d.tex:262` heads the paragraph "*Enabling Valencia 2p2h
     confirms it*" while its own body says the added MEC "fills 46 % of the data−CV gap in the dip
     and 27 % of the integrated deficit". The body is quantitative and honest; the overclaim is
     `sec_execsummary.tex:25`, which says 2p2h "fills the quasielastic–Δ dip" unqualified.
  2. **DELETED — void as a finding.** "The high-`E_avail`/high-`W` excess has no adopted corrected
     covariance establishing significance" is true as a fact but is *what the note already says*:
     `sec_execsummary.tex:28` and `sec_eavailw.tex:103-104` both report the comparison at
     central-value level, and `values.tex:53` records `% (Eavail,W) significances removed
     2026-07-12: historical covariance quarantined`. The note was corrected before this audit ran.
  3. **Confirmed, strengthened.** `sec_eavailw.tex:62-64` says "All four underpredict the ... corner
     by 54–58 % (data/generator $=1.54$, $1.58$, $1.56$)" — **three** ratios for four generators,
     and 54–58 % is exactly the span of the three listed. GiBUU's corner ratio is absent, and
     independent repo evidence suggests it lies outside that band: corner χ² 381.1/12 versus
     GENIE 116.9/12 (`ND_OMNIFOLD_RUN_LOG.md:1155-1157`), and integrated data/GiBUU =
     3.07/2.22 = 1.38. **Compute the GiBUU corner ratio before the range is quotable** — it was
     not computed here.
  4. **Confirmed.** `fps_acceptance.py:59-70` computes the 66.4 / 22.3 / 11.3 % fractions from
     `mc_truth_denom` summed over `w_truth`, and `runEventLoopOmniFold.cpp:595` sets
     `w_truth = model.GetWeight(*truthCV, evt)` — the MnvTune-carrying central-value weight.
     `paper_body.tex:171` and `primer_body.tex:146` state the "about a third" figure flatly. It is
     a MnvTune-weighted simulated truth fraction and needs that qualifier.

## 6. Repo-wide, outside `nd-unfolding/pet`

Source: codex personal (round 3). Single-source as found; J29 and J31–J33 re-verified 2026-08-01
(see §2). All four survived, and all four had their *consequence* restated: J29 was live and is now
resolved, while J31–J33 are latent rather than live.

- **J28 — Flux universes are divided by the CV flux integral in every ND/5D kernel.
  [tier A — mechanism and scope]**
  `unified_throw.py:287` writes `flux_univ_ratio.npy` (`Φu/ΦCV`). The only files that load it are
  `assemble_bank_4d.py` and `unified_throw.py` itself. This finding named **three** independent
  sites: `compare_unified_throw.py:139`, `unified_throw_cov_5d.py:65` (both calling extraction
  with fixed `d["flux"]`) and `sweep_bank_5d.py:265` (`cv["flux"]`). They are separate
  implementations, not one call path, so fixing the unified-throw kernel alone is insufficient.

  > **Correction, 2026-07-31 (post-fix).** Three was a **lower bound**. The remediation found
  > **five sites plus a fail-open**: additionally `sweep_bank.py:254` (the 4D sweep runs the same
  > `Flux:0..99` list) and the PET 5D path (`pet_unified_throw_5d.py` reweighted events while
  > `pet_systematics_5d.xsec` held `self.flux` at CV). Separately, `unified_throw.py`'s bank
  > builder opened the flux file **unchecked and left the ratio at 1 on any failure**, so an
  > unreadable flux file silently produced a bank in which every universe divided by `Φ_CV` —
  > the same defect arriving through a different door, and invisible because it failed open.
  > Fixed in `081ae4a`, which is fail-closed throughout.
  >
  > **Method note.** An audit that enumerates call sites by grepping a symbol finds the sites
  > that share that symbol. It does not find independent reimplementations of the same
  > arithmetic, and it does not find a guard that silently degrades to the defective value. Both
  > escaped this audit and were caught only by someone fixing the code. Treat "N sites" in any
  > finding here as a floor.

  **There is a correct reference implementation in-repo.** The 2D path
  (`unfold_2d_omnifold_unbinned.py:145`, `load_flux_universe_bins`) divides each universe by its
  own `Φu`, **fails closed** when the per-universe file is absent (`:163`), and cross-checks that
  universe and CV come from the same flux production (`:192`). Its docstring states the rule
  explicitly. The fix is therefore a **port, not a design** — and the finalized 2D covariance is
  **unaffected**.

  **Blast radius** (scoping pass, tier C except the three call sites and the 2D exemption above):
  affected are the background-aware 5D vertical sweep, the adopted headline
  `..._bkgaware_uthrow.root` (affected *twice* — wrong Flux block plus wrong per-bin inflation
  `g`), the `cvcentered` variant, any 4D/FPS `*_uthrow*` product, and the already-quarantined
  recoil-PET and `(E_avail,W)` terms. **Not affected:** all central cross sections, the corrected
  4D block-sum core, closure, dimensional anchors, statistical and ML covariance, detector
  laterals, and the finalized 2D covariance.

  **Sizing does not require re-unfolding.** Flux normalization enters only at final extraction,
  so every saved universe can be corrected post hoc by dividing by `r_u(pT) = Φu(pT)/ΦCV(pT)`
  using its saved flux-universe ID, then rebuilding the block sum, `C_unified`, `C_blocksum`, the
  joint mean shift, and `g`. A first-order estimate puts the adopted 5D mean-centered scale at
  roughly `5.81e-38 → 6.0e-38` (+3–4 %), and the combined block √tr at +6 %; **neither is
  quotable**, because correcting the same Flux draw in both the unified and block ensembles moves
  `g`, the tail inflation and the finite-throw cross terms together. The paired slab rescale
  gives the exact answer cheaply.

  `adopt_unified_5d.py:86` derives `g` from these misnormalized throws, and
  `VALIDATION_LEDGER.md:174` records the 4D unified-throw adoption as **PASS**. Recommendation:
  **quarantine the adopted 5D covariance scales now** (`5.8077e-38`, `6.2367e-38`), preserve the
  central results, and re-roll by post-processing the existing slabs. J29 is a separate flux bug
  in the same family and should be fixed in the same pass. **Highest-priority finding in this
  document.**

- **J29 — FPS flux universes leave the final extended-pT bin at CV flux.
  [tier A — verified 2026-08-01; RESOLVED in `081ae4a`]** Confirmed exactly as described, and the
  mechanism is now closed. The pre-fix code (`git show 081ae4a -- nd-unfolding/unfold_nd_omnifold_unbinned.py`)
  looped `for b in range(len(flux_bins))` reading `h_cv.GetBinContent(b+1)` under
  `if cvf > 0 and unf > 0`. `hFluxCV` is a **14-bin** TH1D and `hFluxUniv` a 14×100 TH2D
  (`2d-unfolding/uq/build_flux_universe_band.py:20-21`); the FPS grid is **15** bins ending
  `[4.50, 30.0]` (`sbatch_unfold_fps_universes_full.sh:32`). `GetBinContent(15)` therefore read
  the overflow, returned 0, failed the `>0` test, and left `scale[14] = 1.0` — CV flux in the
  extended bin, silently.

  **It was live, not hypothetical.** `3d-unfolding/uq_3d/universes_full_list.txt` carries 100
  `Flux:*` entries and `sbatch_unfold_fps_universes_full.sh:57-67` runs the whole list on the
  15-bin grid. Every saved FPS Flux universe has an uncorrected final pT bin. Note the pre-fix code
  *did* fail closed on a missing file or missing histogram; the only silent path was the per-bin
  validity fallback. Fixed at `:744-751` — CV and universe now share one remap helper and
  `fluxu.flux_universe_bins` fails closed. **Reclassify as RESOLVED-`081ae4a`**; the saved FPS
  `*_uthrow*` slabs remain inside J28's re-roll blast radius.

- **J30 — The canonical P4 driver cannot reach covariance validation. [tier A]**
  `run_p4_standard.sh:50-51` invokes the validator with `--active` and `--merged-dir`;
  `p4_validate_active_lateral.py:35-39` requires `--candidate`, `--support`, `--manifest`,
  `--merged-audit`, `--out`. The chain dies on argparse before doing any work. It also requests
  the nonexistent ROOT key `hCov_std_final5_candidate` (the builder writes
  `hCov_stdcombined5d_total_candidate`) and passes an unsupported `--proj` to `p4_project_4d.py`.
  **The canonical P4 chain has therefore never run end to end.** P4 is a deferred/non-adopted
  lane, so this is not urgent — but it is not the state the runbook implies.

- **J31 — P4 merge failures are converted into success.
  [tier B — verified 2026-08-01, strengthened; latent, never bit]** Confirmed at
  `run_p4_merge_audit_std.sh:23-24`: the `||` branch is `{ echo "[merge] FAIL ..."; rm -f "${MERGED}"; }`,
  and `rm -f` returns 0 whether or not the file exists, so `merge_one` — whose last command this
  is — exits 0. `NMERGED` is computed at `:31`, printed at `:32`, and the script proceeds to the
  audit at `:34` without ever asserting it equals 10. No `set -e`.

  **Strengthening.** The return status is moot in *both* directions: jobs are launched with `&` at
  `:28` and collected by a bare `wait` at `:30`, which discards every child status — including the
  `return 3` abort path at `:22` that the author did write. Fixing only the `rm` would change
  nothing. *Scope corrected:* it never bit. `active_universe_5d/standard/P4_STANDARD_STATUS.md:11-13`
  records 10/10 merges with full-file hashes validated by an independent owner-neutral orchestrator
  receipt, so the one recorded run is externally confirmed complete. Latent, and P4 is a
  deferred lane.

- **J32 — The P4 adoption command is a successful no-op.
  [tier B — verified 2026-08-01, strengthened; framing corrected]** Confirmed at
  `p4_adopt_standard.py:39-42`: `P.require(P.sha256_file(a.candidate), "candidate unreadable")`
  tests only truthiness of the digest, then the script prints "would promote" and exits 0 without
  creating `--out`.

  **Strengthening — the binding is not skipped, it is impossible.**
  `p4_validate_active_lateral.py:41-79` writes a receipt containing `gates`, `active_traces`,
  `active_only_sum_relerr`, `support_comparison` and `result` — and **no candidate path and no
  candidate SHA256**. There is nothing in the PASS receipt to bind a candidate to, so *any* PASS
  receipt satisfies *any* candidate. The fix has to start in the validator, not the adopter.

  *Framing corrected:* "automation can report adoption succeeded" is latent, not live. Nothing
  invokes the script — the only references in the tree are `tests/test_p4_repair.py:305` and two
  status docs, and `P4_STANDARD_STATUS.md:29` labels it "(not run/not wired)". The no-op is also
  disclosed in the module docstring (`:8-9`) and in the printed string itself.

- **J33 — ND schema checking fails open.
  [tier B — verified 2026-08-01, all three sub-claims confirmed; latent]**
  1. `unfold_nd_omnifold_unbinned.py:151-154`: `_addr` allocates `array("d", [0.0])` and discards
     `SetBranchAddress`'s return code, so a missing branch yields a silent column of zeros. The
     same pattern at `:216-218` covers CV `w_truth`, where a missing branch silently yields
     `w = 1.0` for every row — the exact failure mode of KNOWN_ISSUES #1.
  2. `:639-644` validates each extra axis on `(t_sig, reco)`, `(t_sig, truth)`, `(t_bkg, bkg)` and
     `(t_data, data)`. **`t_td` is absent from that list**, yet `:675` passes `t_td` into
     `collect_truth_denom_nd`, which `_addr`s `ax["truth"]` unchecked at `:215`. All-zero
     coordinates would *not* trip the `:684-688` closure gate, which compares counts only — and
     counts are unaffected by zeroed coordinates.
  3. `:287-294` (signal) and `:432` (background): `if t.GetBranch(nt): ax_truth[k] = nt` — a
     missing shifted q3/W branch silently retains the CV branch name, understating the lateral
     band rather than failing.

  *Scope corrected — all three are latent, not live.* The C++ writes `MC_eavail`/`MC_q3`/`MC_W` to
  `mc_truth_denom` (`runEventLoopOmniFold.cpp:433-435`), and `BuildUniverseBranchTable` (`:358-373`)
  emits shifted-axis names that match `_axis_universe_branch` exactly in all four contexts
  (`q3_truth_`, `MC_q3_`, `sim_q3_`, `sim_background_q3_`). Nothing is corrupt today; the gate
  simply cannot detect it if that ever changes.

## 7. Peripheral lane (gemini) — partially discarded

This lane was dispatched twice. **Round 1 is discarded and its findings are not carried
forward** (§8). Round 3 re-ran it inside a disposable git worktree; those findings are below,
all tier C as found and none cross-validated at the time. J36 and J37 were re-verified
2026-08-01 (see §2), with opposite outcomes: **J36 promoted to tier A** — its explicitly unchecked
premise turned out to be true by a factor of 1.39 — and **J37 deleted** as unreachable. The
discarded-lane provenance predicted neither; a lane that must be contained for process reasons can
still surface the strongest and the weakest finding in a document.

- **J34 — The efficiency numerator is filled with the reco weight. [tier A — code fact;
  physics judgment open]** In `compute_efficiency_2d`,
  `unfold_2d_omnifold_unbinned.py:795` fills the denominator with `wt` (`w_truth`) while `:797`
  fills the numerator with `wr` (`w_reco`). Whether this is a defect is a physics convention
  call, not a code call, and the audit's assertion that both must use the truth weight is
  defensible but not universal. **The sharp framing:** it can only matter where
  `w_reco ≠ w_truth` — i.e. exactly the systematic endpoints that J06's B-4 guard blocks. Worth
  a deliberate ruling, recorded either way.

- **J35 — Pervasive resume-skip trap. [tier A — extent]** `[[ -s "${OUT}" ]]`-style completion
  guards appear in **47 in-scope shell files**. Because producers write directly to the output
  path, an interrupted job leaves a nonempty but incomplete file that the next run skips
  permanently and silently. `KNOWN_ISSUES.md:47` already documents this as BEN-023 and prescribes
  the remedy (unit-inventory check, or write-to-temp + rename-on-complete). **This is the same
  defect class as J10** — size-as-completion-proof — found independently by a different account
  in a different subtree, which argues it is systemic rather than local.

  **FIXED 2026-08-01, and the extent was larger than reported.** 47 files was a lower bound: the
  count missed guards written against a *literal path* rather than a variable
  (`[[ -s "boot_nd_4d/res_boot_${SLURM_ARRAY_TASK_ID}.npz" ]] && …`), which is the same idiom.
  Final tally: **85 guards across 84 shell files**, all converted to `lib/resume_guard.sh`
  (`rg_skip_if_complete` + `rg_run`/`rg_publish`), which gate resume on a `${OUT}.done` marker
  stamped only after the producer returns 0 and bound to the output's size+mtime.

  Notes on scope, each checked rather than assumed:
  - **No hash-bound launcher was touched.** All six bound `*.sh` files use `-s` only as an input
    precondition or a post-run assertion — never as a resume guard. The Gate-4 launcher's
    `[[ -s "$TARGET_NPZ" ]]` is immediately followed by a sha256 *and* size drift check.
  - **`run_p4_unfold_std.sh` and `run_p4_merge_audit_std.sh` were left alone**: they already do
    temp → validate → atomic rename → receipt-last, and were the model for the library. Their
    older receipts (no size/mtime field) stay readable by `rg_is_complete`.
  - **Input-side `-s` checks were not converted wholesale.** In particular
    `sbatch_analyze_MEFHC_universes.sh:42` uses `-s "$BOOT_COV"` to decide whether to *include* the
    bootstrap covariance. Tightening it would silently DROP a covariance term from the analysis
    when the marker is absent — a worse failure than the one being fixed. Left as-is, deliberately.
  - **A backfill is owed before the first resume** (RESTORE Step 0b), or every completed unit in
    the campaign re-runs. `lib/backfill_completion_markers.sh` stamps only what a real content
    validator accepts and prints the rest; that FAIL list is the set of partials the old guard was
    hiding.

  Pinned by `nd-unfolding/tests/test_resume_guard.py`, which fails on any reintroduction of the
  idiom, on any `rg_*` call in a file that never sourced the library, and on any guarded output
  with no matching producer stamp.

- **J36 — Global POT scaling applied post-merge.
  [tier A — verified 2026-08-01; the unchecked premise is now checked, and it is TRUE]**
  Code fact confirmed: `get_pot_scales` (`2d-unfolding/unfold_2d_omnifold_unbinned.py:114-123`)
  returns one `data_pot / mc_pot` from two `hadd`-summed `TParameter<double>`, applied uniformly as
  `w * pot_scale` in every collector.

  **The premise the finding could not check.** `docs/orchestration/state/g2-gate1-all12-validation-20260719.json`
  carries all 12 per-playlist POT pairs. Computed from that receipt:

  | PL | Data/MC ratio | vs global | share of MC POT |
  |---|---|---|---|
  | 1D | 0.237148 | +11.65 % | 12.20 % |
  | 1F | 0.235964 | +11.09 % | 14.20 % |
  | 1G | 0.231043 | +8.77 % | 11.96 % |
  | 1L | 0.229626 | +8.11 % | 1.17 % |
  | 1P | 0.224652 | +5.77 % | 4.18 % |
  | 1A | 0.220501 | +3.81 % | 8.17 % |
  | 1N | 0.208090 | −2.03 % | 10.29 % |
  | 1C | 0.205730 | −3.14 % | 4.19 % |
  | 1E | 0.202437 | −4.69 % | 10.22 % |
  | 1O | 0.188301 | −11.35 % | 3.18 % |
  | 1M | 0.176110 | −17.09 % | 18.04 % |
  | 1B | 0.170739 | −19.62 % | 2.20 % |

  Global ratio 0.212405. **Spread max/min − 1 = 38.9 %.** POT-weighted mean absolute mixture error
  **9.4 %**. Playlist 1M — 18 % of MC POT — is over-weighted by 17 %; 1D and 1F (26 % combined) are
  under-weighted by ~11 %. The playlist ratios differ, and not marginally.

  **Scoping the finding did not supply, and which matters.** The **total normalization is not
  biased**: if the MC rate per POT is playlist-independent, global and per-playlist scaling give
  the identical total (`Σ(D_i/M_i)·νM_i = ν·ΣD = (ΣD/ΣM)·νΣM`). The error is purely in the
  playlist *mixture*, and reaches a result only through playlist-dependent flux shape and detector
  conditions. That is consistent with the 2D paper reproduction standing at 1.011 — this defect
  cannot explain, or be excluded by, that number.

  **Supporting evidence that the hazard class was already recognized here and defended
  inconsistently:** `unfold_2d_omnifold_unbinned.py:1320-1329` explicitly refuses to trust the
  `hadd`-summed `pTmu_fiducial_nucleons` and substitutes a geometry constant, commenting "do not
  trust the merged `TParameter<double>` because `hadd` sums it across playlists" — and
  `:38-40` says the same about keeping the nucleon constant local. The identical reasoning was
  never applied to the POT ratio one function away. Now indexed as its own KNOWN_ISSUES row.

- **~~J37 — `Erecoil` registered against `q0True` without spline correction.~~
  [DELETED 2026-08-01 — true statement, zero reachability]**
  The code fact is exact: `MINERvA101/.../runEventLoop.cpp:425` pairs `GetRecoilE` with
  `Getq0True` under an in-code `TODO`. It is unreachable from this analysis in two independent
  ways, either of which is sufficient: it sits inside `if(doCCQENuValidation)` (`:419`), a
  validation-histogram branch gated on the tree name being CCQENu; and `runEventLoopOmniFold.cpp`
  contains **zero** occurrences of `GetRecoilE` or `Getq0True`. The OmniFold path uses a matched
  pair throughout — `NewEavail()` for reco (`:1178`, `:1460`, `:1591`) and `GetEAvailableTrue()`
  for truth (`:589`, `:1140`). Deleted rather than demoted: carrying it as a lead implies a live
  question that does not exist. The ID is retained struck-through so the numbering is not reused.

## 8. Findings from the audit process itself

- **J38 — `test_g2_guards_collected.py` leakage guard passed vacuously. [tier A — FIXED this
  session]** `assertRegex(src, r"(?i)leak")` matched the module **docstring** of
  `test_g2_fullevent_dump_schema.py` (line 11, "truth<->reco feature leakage"), not the guard at
  `:255-262`. Deleting the guard entirely would have left the test green — the exact vacuous-pass
  shape the wrapper exists to prevent. Now asserts the executable constructs: that the truth-muon
  helper body is extracted, and screened against all four reco getters.

- **J39 — `test_b1_normalization_fix.py` could not detect dropped weights. [tier A — FIXED this
  session]** Every push in `Gate4FoldForward` was constant (`np.full(4000, R)`,
  `np.full(80, 1.28)`, `np.ones(10)`, `np.full(40, 1.1)`), and with constant push
  `sum(w·push)/sum(w) = c` for **any** `w`. No test could distinguish a correct weighted mean
  from an implementation that ignored the weights. Added two tests: one feeding a push
  anti-correlated with `w_truth` through `fold_forward_sums_from_dump` and pinning the weighted
  mean against the plain mean, one exercising the gate in both directions on a non-flat push.
  **Note:** the second test initially failed *its own power guard* — a shuffled spread yields
  only 0.46 % weighted deviation, inside the 5 % tolerance, so it would itself have passed
  vacuously. It required a spread correlated with `w`. Three vacuous-pass constructions in one
  small area suggests a recurring pattern worth a targeted sweep.

- **J40 — A second vacuous skip path. [tier A]** `nd-unfolding/tests` reports 1 skipped:
  `test_pet_fullevent_nominal_launcher.py:134 — "bound Gate-2 target NPZ not present"`. This is
  **distinct** from the `test_hash_bindings.py` skip noted in J16. Both go green off-cluster
  without testing anything.

- **J41 — Terse prompts did not degrade audit yield. [methodology]** Round-1 prompts were one
  sentence or less (§1). The six-word PET prompt produced ten findings, all of which survived
  cross-validation. Both cross-validation rounds returned zero false positives. The observed
  failure mode of terse prompting was **not** hallucinated findings but imprecise line citations
  (§1) and, in one lane, scope violation (J42).

- **J42 — One lane wrote to the repo during a read-only audit. [process failure]** The gemini
  round-1 lane was dispatched with `--dangerously-skip-permissions` and write access to the live
  repo. Given the prompt *"Audit this repo for correctness bugs."* it refactored
  `omnifold_nn/omnifold/net.py` — the shared PET model — including changing the training loss
  return from `tf.reduce_mean(t_loss)` to `t_loss`, wrapping tensor ops in `layers.Lambda`,
  replacing the `tf.Variable` class token with `add_weight`, and rewriting `get_neighbors`. It
  then reported the edits as completed fixes. The lane was stopped, the diff preserved, and the
  tree reverted; `git status` was clean afterwards and no other file was touched. **The round-1
  gemini findings are discarded** — they were produced against a tree the lane had itself
  modified. Round 3 re-ran it inside a disposable worktree, which contained it.
  *Dispatch rule going forward:* audit lanes get `--sandbox read-only` (codex) or an explicit
  read-only tool allowlist (claude); gemini gets a throwaway worktree. Always `git status` after.
  One item in the discarded diff may be a real finding worth raising separately: creating a
  `tf.Variable` inside a functional-graph build is a known Keras defect pattern. It has **not**
  been assessed here.

## 9. Suggested order of work

1. **J28 (flux denominator)** — the only finding that reaches an already-adopted product. No
   re-unfolding needed: rescale the saved slabs, re-derive `g`, compare. Port the 2D
   `load_flux_universe_bins` pattern (including its fail-closed guard) to all three ND/5D sites,
   and fix J29 in the same pass. Quarantine the adopted 5D covariance scales until re-rolled;
   central results are unaffected and stay quotable.
2. ~~**Gate-4 Step 2b re-issue** (`RESTORE-2026-08-03.md`) — closes
   `test_gate3_and_gate4_launch_code_freezes_specifically` and resolves two of the four J11
   mismatches. Target state **8 failed / 407 passed / 1 skipped**.~~ **DONE 2026-07-31**
   (`5410ab0`). That test closes. The 407 figure is stale — the J10/J35 and J01/J02/J05 lanes
   landed the same day, so the actual state is **8 failed / 590 passed / 1 skipped**; the failure
   SET is what was being pinned and it is as predicted (7 platform + `test_no_new_broken_hash_bindings`).
3. **J11 expected-red baseline** — *after* step 2, so it pins the surviving Gate-2 tuples rather
   than all of them. **Note the list grew on 2026-08-01, from three tuples to five**: the J01 fix
   necessarily edited `tests/test_fullevent_fps.py` (bound by `g2-gate2-construction-20260719`)
   and `pet/gate2_target_runtime.py`'s shell pin in `run_gate2_target_validator.sh`. No new FILE
   entered the red set at the receipt level — both receipts and the shell pin were already red on
   `fullevent_fps_dataloader.py` — but Step 2 must now move five tuples, not three.
4. ~~**J01** — decide whether to relabel the estimator or implement the full schema.~~
   **DONE 2026-08-01: the full schema was implemented**, not relabelled. See J01 above. Gate-4
   re-issued as `state/p3f-pet-gate4-launch-code-gate-20260801b.json` and now freezes the feature
   schema itself, so the fingerprint is falsifiable. Still `PASS_CODE_ONLY`; the launch remains
   blocked on everything Step 2b lists as owed, plus a Gate-2 target rebuild that is now required
   for a *physics* reason (J05).
5. ~~**J17/J18** — note corrections.~~ **DONE**: both fixed, and the J17 residual in
   `app_negweight.tex:55` closed at `b27d1e1` (found by the 2026-08-01 tier-C pass; see J26).
6. **J22 — decide the FPS footing.** Promoted to tier A on 2026-08-01: the note claims a
   negative-weight baseline for a product made a month before that code existed. This is the only
   tier-C finding that changes what the note may claim about an existing number. Either demote the
   `app_negweight.tex:227-228` claim to stated intent, or regenerate `σ_ext` on the
   negweight-refined footing — which is already the gated, verifier-blocked C turn in
   `FPS_UQ_CORRECTED_STATE.md`. Cheap if the answer is "demote".
7. **J21 — decide what the PET central value is.** The quoted 4D ratio has unit measured weights
   and no background subtraction, while `sec_pet.tex:70-71` describes a background-subtracted
   target one subsection later. Either qualify the 0.912 as a non-background-subtracted historical
   diagnostic, or re-extract on the `bkgsub` input. Interacts with the 2026-08-01 full-event
   landing: pre-08-01 PET numbers are a different estimator, so do this once, after that settles.
8. **The note wording pass** — ~~J19, J24, J25, J26.1, J27.1,~~ J27.3, ~~J27.4~~.
   **DONE 2026-08-02 except J27.3.** J19 → the `sec_intro.tex` bullet now names the purity
   background subtraction as the one deliberate pre-training binning. J24 → "reproduces its
   predecessor" became "passes the projection anchors to ≈1–2 %" at all four summary sites.
   J25 → qualified to projections *within the classifier's feature space*, with the 3D extension
   named as a re-unfold rather than a projection. J26.1 → "few-per-mille" corrected to the actual
   1.4 %/1.8 %, and the per-bin/aggregate conflation split. J27.1 → the exec summary now carries
   the 46 %/27 % figures instead of "fills the dip". J27.4 → "about a third" now says *simulated*
   and names the MnvTune weighting.
   **J27.3 is worse than a dropped qualifier and is NOT in that batch.** The three ratios come from
   the 2026-06-08 band run (`ND_OMNIFOLD_RUN_LOG.md:988-990`), whose own summary reads "All THREE
   underpredict" and ends "GiBUU excluded (`FinalEvents.dat` lacks per-event Enu)". "All three"
   later became "all four" in the note-v2 subtree with no recomputation, so the numbers predate
   GiBUU's presence in this comparison entirely. The reduction is recovered
   (`overlay_eavailW_band.py:88-108`: a ratio of corner-INTEGRATED cross sections over the 3×3
   `Eavail>=0.8 × W>=1.8` block, not a per-bin or worst-bin statistic), and both tempting proxies
   are different sub-blocks — the Eavail-projected 1.59/1.36/1.91 integrates over all W, and the
   corner χ² 381.1/12 uses `Eavail>=0.4` → 12 cells. Close it by re-running `make_figures.sh:55`
   and reading the `hiE-hiW corner ... data/gen=` line; inputs are Perlmutter-only and gated on
   Step 0a. Provenance block recorded at `sec_eavailw.tex:62`.
9. **J36 — scope the POT mixture.** Own KNOWN_ISSUES row as of 2026-08-01. Does not move the
   total, so it is not urgent; it needs a decision on whether per-playlist scaling is worth
   implementing, given a 38.9 % ratio spread and 9.4 % POT-weighted mixture error.
10. J12–J16, J35 — machinery hardening, no result impact. (J35 + J10 FIXED 2026-08-01; a
   completion-marker backfill is owed at restore before anything is resubmitted — Step 0b.)
11. ~~**J31–J33 — latent-gate hardening, lowest priority.**~~ **J31 and J32 FIXED 2026-08-02;
   J33 remains.** J31: `run_p4_merge_audit_std.sh` now collects child PIDs and waits on each
   individually (a bare `wait` discarded every status, so fixing only the `rm -f` would have
   changed nothing), and fails closed when `NMERGED != EXPECTED`. J32: fixed in the validator
   first, as this entry said it had to be — `p4_validate_active_lateral.py` records
   `candidate` and `candidate_sha256` in its receipt, and `p4_adopt_standard.py` now requires the
   receipt's SHA to equal the candidate's instead of merely testing that the digest is truthy.
   Neither file is hash-bound, so no receipt moved. J33 (ND schema fails open: `_addr` discards
   `SetBranchAddress`'s return code, `t_td` is absent from the axis-validation list) is untouched
   and still latent.
