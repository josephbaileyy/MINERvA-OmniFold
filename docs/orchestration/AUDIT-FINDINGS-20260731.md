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
  re-read directly; tier-B and tier-C line numbers should be treated as approximate.
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

- **J02 — No full-inventory inference or extraction exists. [tier B, strengthened]**
  Training selects 2M of 49,152,885 MC rows and the driver saves only that subsample's weights.
  The verifier sharpened the original claim: `extract_nominal_bkgsub.py` is the *recoil/5D*
  extractor, and there is **no full-event extractor in the tree at all**. The recoil loader has
  a `--reweight-all` full-cloud pass that the full-event driver dropped. Key and coverage both
  mismatch (`weights_push` vs `w_push`; 2M vs `arange(49152885)`).

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

- **J19 — "No binning until the final histogram" is false for the headline method. [tier C]**
  Claimed in `sec_intro.tex` and `sec_method.tex`, but the default `purity` background mode
  assigns every data event a `D−B` weight via analysis-bin lookup *before* training, in both the
  2D and ND implementations. So the measurement is not fully unbinned, reporting bins are not
  freely changeable after the fact, and a self-consistent change to the background-correction
  binning requires another run. The claim is defensible only for the negative-weight path.

- **J20 — The documented "canonical LightGBM seed scan" points to a script that uses histogram
  GBT. [tier C]** `app_statmethods.tex:121` cites `sbatch_unfold_2d_MEFHC_5iter_seedscan.sh`,
  which passes `hist`, not `lgbm`.

- **J21 — The PET result is not a production-contract-equivalent cross section. [tier C]** The
  quoted PET central value was produced with unit measured-event weights and without the MC
  background tree; the extraction script performs no background subtraction. The figure recipe
  additionally generates PET central plots from the old `of_inputs_pc.npz` while surrounding
  text discusses the coverage-fixed `of_inputs_pc_fullcloud.npz`. The 0.912 PET/GBDT ratio is
  supportable as a historical diagnostic, not as a coverage-complete comparison.

- **J22 — The quoted extended-fiducial/FPS result is not shown to use the claimed negative-weight
  baseline. [tier C]** The recorded regeneration on that footing was cancelled and no replacement
  central product was adopted; a later-edited launcher cannot establish how the existing
  `4.502e-38` product was generated.

- **J23 — Closure does not "mirror the production analysis". [tier C]** Closure restricts
  pseudo-data to reco-and-truth-passing signal MC and forces completeness to 1. It tests training
  and extraction bookkeeping, not real-data background subtraction, empirical completeness, or
  extrapolation beyond detector support.

- **J24 — "Every higher-dimensional result reproduces its predecessor under marginalization" is
  too categorical. [tier C]** Documented tests show approximate agreement: 3D→2D differs by
  0.95 % in normalization with 4.4 % per-bin scatter; 4D anchor projections differ by up to
  1.68 %. "Passes the projection anchors within ≈1–2 %" is supported; exact reproduction is not.

- **J25 — "Any projection or dimension can be obtained without re-unfolding" is unsupported.
  [tier C]** True only for projections of variables already in the classifier's feature space; a
  variable omitted from the classifier remains conditioned on the simulation prior. The PET
  section itself acknowledges this.

- **J26 — Negative-weight validation does not establish full covariance equivalence. [tier C]**
  The appendix claims reproduction "per bin and in aggregate" and calls the replacement fully
  validated. The recorded comparison establishes ≈0.986 and 0.982 ratios of covariance
  trace-derived scales plus central-value summaries — not element-wise covariance, correlations,
  eigenmodes, or that every difference is sampling noise.

- **J27 — Several physics interpretations are causal claims the code supports only as
  associations. [tier C]** Added MEC fills ≈46 % of the low-`E_avail` dip gap (not "2p2h
  confirmed"); the high-`E_avail`/high-`W` excess has no adopted corrected covariance
  establishing significance; "all four generators underpredict the corner by 54–58 %" has no
  committed GiBUU corner ratio; and the "published cuts discard a third of the signal rate"
  figure derives from `mc_truth_denom` weighted by the MnvTune prior, so it is a
  MnvTune-weighted simulated truth rate, not a model-independent measured fraction.

## 6. Repo-wide, outside `nd-unfolding/pet`

Source: codex personal (round 3). Single-source except where marked.

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

- **J29 — FPS flux universes leave the final extended-pT bin at CV flux. [tier C]** The ND driver
  correctly remaps the 15-bin FPS pT grid onto the 14-bin reference flux grid for CV, but its
  universe loop requests histogram bin `b+1` directly. For the `[4.5,30]` FPS bin that reads the
  14-bin histogram's overflow, the validity condition fails, and the scale silently stays 1. The
  production launcher demonstrably supplies the 15-bin grid.

- **J30 — The canonical P4 driver cannot reach covariance validation. [tier A]**
  `run_p4_standard.sh:50-51` invokes the validator with `--active` and `--merged-dir`;
  `p4_validate_active_lateral.py:35-39` requires `--candidate`, `--support`, `--manifest`,
  `--merged-audit`, `--out`. The chain dies on argparse before doing any work. It also requests
  the nonexistent ROOT key `hCov_std_final5_candidate` (the builder writes
  `hCov_stdcombined5d_total_candidate`) and passes an unsupported `--proj` to `p4_project_4d.py`.
  **The canonical P4 chain has therefore never run end to end.** P4 is a deferred/non-adopted
  lane, so this is not urgent — but it is not the state the runbook implies.

- **J31 — P4 merge failures are converted into success. [tier C]** In
  `run_p4_merge_audit_std.sh:23`, a failed merge executes `echo` then `rm`, and the function
  returns the successful `rm` status rather than the merge failure. Background jobs are collected
  by a bare `wait`, and `NMERGED` is printed but never asserted to equal 10.

- **J32 — The P4 adoption command is a successful no-op. [tier C]**
  `p4_adopt_standard.py:39` checks only that hashing the candidate returns a nonempty string,
  never binding that hash to the validation receipt or component manifest. It then prints that it
  "would promote" the candidate and exits 0; `--out` is never created. Automation can report
  adoption succeeded while no adopted product exists.

- **J33 — ND schema checking fails open. [tier C]** `_addr()` initializes to zero and ignores
  `SetBranchAddress` failure. Startup validation checks extra-axis branches on signal, background
  and data trees but omits `mc_truth_denom`, so missing truth-denominator axes can become
  all-zero coordinates and corrupt completeness. Missing lateral q3/W branches likewise retain CV
  values silently, understating detector covariance instead of failing.

## 7. Peripheral lane (gemini) — partially discarded

This lane was dispatched twice. **Round 1 is discarded and its findings are not carried
forward** (§8). Round 3 re-ran it inside a disposable git worktree; those findings are below,
all tier C unless marked, and none were cross-validated.

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

- **J36 — Global POT scaling applied post-merge. [tier C]** A single global
  `pot_scale = data_pot / mc_pot` is read from the `hadd`-merged ROOT file and applied uniformly.
  Because `hadd` sums the POT metadata and concatenates trees, per-playlist Data/MC POT ratios
  are discarded; if playlists differ, the combined MC mix is skewed. **Unverified, and the
  premise that playlist ratios differ materially is itself unchecked.**

- **J37 — `Erecoil` registered against `q0True` without spline correction. [tier C]** In
  `MINERvA101/.../runEventLoop.cpp:425`, with an in-code `TODO` acknowledging it. Baseline
  reference code, not the OmniFold path; relevance depends on whether that definition is carried
  forward.

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
2. **Gate-4 Step 2b re-issue** (`RESTORE-2026-08-03.md`) — closes
   `test_gate3_and_gate4_launch_code_freezes_specifically` and resolves two of the four J11
   mismatches. Target state **8 failed / 407 passed / 1 skipped**.
3. **J11 expected-red baseline** — *after* step 2, so it pins the two surviving Gate-2 tuples
   rather than four.
4. **J01** — decide whether to relabel the estimator or implement the full schema. Blocks any
   Gate-4 launch regardless of the gate's state.
5. **J17/J18** — note corrections; cheap, and J18 currently has the document contradicting
   itself in print.
6. J12–J16, J35 — machinery hardening, no result impact.
