# Known issues, bugs, and code debt — INDEX

One line per issue, pointer to the canonical home for detail. **This file is an
index, not a copy** — update the pointer target, not this file, when an issue
evolves. Add new issues here the moment they are found, so they never get
buried in run-log prose.

## Open code debt

| # | Issue | Status | Detail lives in |
|---|---|---|---|
| J | **2026-07-31 four-account audit — 42 findings (J01–J42), indexed here as one block.** **TIER-C VERIFIED 2026-08-01: all 15 single-source findings (J19–J27, J29, J31–J33, J36, J37) re-checked at `6cabd4d` — 14 promoted, J37 deleted as unreachable, J27's significance sub-claim deleted as already-disclosed. No FINDING is tier C any more; only J28's blast-radius scoping still is.** Three reached tier A: **J22** the note claims a negative-weight baseline for the FPS `4.502e-38`, but that product predates the negweight code by a month (`cf8a4a6` 07-11 vs job 54244120 on 06-10; the launcher flag arrived 07-20) — the footing claim must be demoted or the product regenerated; **J36** global POT scaling discards per-playlist Data/MC ratios that span **38.9 %** (own row below); **J29** was live for all 100 FPS Flux universes, now RESOLVED in `081ae4a`. **J21** the quoted PET 0.912 ratio has unit measured weights and no background subtraction. J31–J33 downgraded from live to **latent** (no current corruption). Eight of nine note findings are qualifiers dropped between a technical section and a summary, not errors. Highlights of the original pass, each with an evidence tier in the detail doc: **J28** PPFX flux universes divided by the CV integral at five ND/5D sites plus a fail-open — reaches the adopted 5D covariance; code FIXED `081ae4a`, numbers NOT re-rolled, ledger scales QUARANTINED. **J11** hash bindings red at HEAD; Gate-4 pair resolved by the Step 2b re-issue (`5410ab0`), Gate-2 pair still red pending a Gate-2 re-run, which is correct. **J17/J18** the note's estimator claim and its stale pre-fluxfix UQ appendix — both FIXED. **J01/J02/J05** the loader read `{pt,pparallel}` while the driver stamped `pet-fullevent-fps-v1`; no full-event extractor existed at all; the Stay-Positive target was fitted in a narrower space than the classifier. **FIXED 2026-08-01**: the loader reads every G2 extension array (muon object + reco vertex as event features, view/timing as cloud token columns), Gate-4 now freezes the feature schema so the fingerprint is falsifiable, `nd-unfolding/pet/extract_fullevent_fps.py` is the full-inventory reweight-all + FPS extraction (code-only, never run — needs the 08-03 restore), and the refiner is fitted in the classifier's space. Gate-4 re-issued (`…-20260801b.json`). **J05/B-5 stays OPEN on the per-token cloud**, and the Gate-2 target must be rebuilt at Step 2 for a physics reason, not just a bytes one. **J35/J10** size-as-completion-proof (the nominal NPZ write + 85 guards in 84 shell files — J35's "47 in-scope files" was a lower bound; literal-path guards were missed) — same class as BEN-023, **FIXED 2026-08-01** via `lib/resume_guard.sh` + `nd-unfolding/pet/atomic_write.py`; Gate-4 re-issued (`…-20260801.json`); **backfill owed at restore** (Step 0b) or the first resume re-runs the campaign. **J42** an audit lane with write access refactored `omnifold_nn/omnifold/net.py`; reverted, and the dispatch rule is now in `AGENTS.md`. | MIXED — see detail doc per finding | `docs/orchestration/AUDIT-FINDINGS-20260731.md` |
| 1 | **N-D driver no-`--use-weights` mode is globally low by pot_scale** (unscaled unit MC weights into OmniFold vs POT-scaled binning weights). FIX APPLIED 2026-06-10: driver always passes the POT-scaled weights (closure pseudo-data mirrors them); 1/pot_scale corrections REMOVED from `fps_pilot_compare.py`/`fps_prior_envelope.py`. Verification job 54271042 PASS: both bare-GENIE unfolds + battery + envelope reproduce the ledger numbers without correction. | RESOLVED 2026-06-10 | `VALIDATION_LEDGER.md` (2026-06-10 fix-verification entry) |
| 2 | **Coverage 200-toy ROOTs not on disk** — headline coverage numbers documented but not regenerable from the checkout. REGEN DONE 2026-06-11 (arrays 54273493/54273495, 200 toys → `2d-unfolding/uq/coverage/`): `uq/coverage_toys.py` reproduces every documented number EXACTLY (mean 68.71%, median 68.50%, ⟨\|r\|⟩ 0.794, signed +0.006±0.082, 97.6% bins ≥65%, same 5/205 below, STATUS PASS). | RESOLVED 2026-06-11 | `VALIDATION_LEDGER.md` (Validation Diagnostics) |
| 3 | **PET lateral band is a frozen-cloud transfer**, not per-lateral re-inference. RESOLVED 2026-06-10 (job 54284039, `pet_lateral_band.py`): PET-native band computed via the event-aligned 5D join (alignment asserted over all 32.85M rows; miss rows pinned to CV per #12; reco-weight ratio carries the GEANT/MinosEfficiency response). Result: native median 1.74% vs transferred 4.03%; total budget 22.5% vs published 23.0%. The transfer is the CONSERVATIVE side (frozen-push misses retraining response), so the published budget stands; `products/pet/pet_4d_covariance_combined_wlat.root` is the cross-check artifact. | RESOLVED (transfer validated as conservative) | `VALIDATION_LEDGER.md` (2026-06-10 PET-native lateral entry) |
| 4 | **(E_avail,W) lateral block is transferred from 4D**, spread over W by the CV shape. RESOLVED 2026-06-13 (interactive job 54391533, `eavailW_covariance.py --lateral-sweep-*` over the 18-universe 5D detector sweep + matched CV): the W-resolved block (median 2.36%/bin, √tr 9.52e-40) is LARGER than the 4D-transferred approximation (1.80%, 7.99e-40) and was adopted; sweep-CV vs frozen-CV marginal max\|ratio−1\|=0.007. Corner significances moved published→W-resolved: GENIE 9.0→8.9, +MEC 9.2→9.2, NuWro 10.5→**15.6**, GiBUU 18.2→**22.4**σ — the proper detector covariance DEEPENS the DIS-corner deficit for the worst-fitting generators, does not soften it. Technote table + exec summary + open-questions updated; `products/5d/eavailW_covariance_wlat.root`. | RESOLVED 2026-06-13 (W-resolved block adopted; conclusion strengthened) | `VALIDATION_LEDGER.md` (2026-06-13 W-lat entry) |
| 5 | **Low-p∥ MINOS sum-ratio gradient persists** after the IsMinosMatchMuon fix (0.6 at p∥=1.5–2 rising to ~1.0 above 20 GeV/c) — likely MINOS geometric acceptance/range-out the MINERvA-101 path does not implement. Matters more for FPS (p∥<1.5 region). 2026-06-10 diagnostic (job 54280253): official muon-quality cuts ACQUITTED — eff_data/eff_MC ≈ 1.03–1.05 at low p (needed ~1.67), data uniformly MORE efficient than MC, so missing cuts cannot cause the deficit. Cause remains upstream MINOS acceptance/efficiency or generator modeling; impact bounded by the 2D paper reproduction (1.011). | OPEN (quality cuts ruled out; bounded) | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` §IsMinosMatchMuon |

| 12 | **Universe branches on appended miss rows are uninitialized garbage** (pre-2026-06-10 dumps): `AppendTruthOnlyMisses` never rebound the per-universe weight/kinematics branches, so all 12.35M miss rows (37.6% of the 5D MEFHC `mc_signal_reco`) carry freed-memory values (denormals, ±1e±182) in every `w_truth_*/w_reco_*/MC_*/sim_*_<band>_<idx>` branch. **Production sweeps are first-order protected**: the driver's xsec = unfold×denom/of_in takes denom from `mc_truth_denom` (universe branches CLEAN there) and the garbage-induced miss loss cancels between unfold and of_in; same structure protects `eavailW_covariance.py`. **Affected**: `pet_systematics.py` C_syst/C_flux (bank miss-row rhos mangled by `_clip` to {1e-2,1,1e2} → published PET 18.31% syst median possibly distorted; bank deleted in cleanup, reassessment needs bank regen) — assess before quoting PET budget beyond milestone status. C++ FIXED 2026-06-10 (miss rows now carry deterministic CV proxies; rebuilt+installed); existing dumps NOT regenerated. `pet_lateral_band.py` pins miss rows to CV explicitly. PET-bank reassessment DONE 2026-06-12 (rebank 54330164 + re-run 54330166, alignment gate bit-identical): the garbage bank had inflated the PET C_syst median **18.31% → clean 8.24%** (stat/ML blocks identical — perfect control); clean total 11.66% vs published 23.02%. Published budget was conservative (over-covered), no result invalidated; quote the rebank artifact going forward and revise the technote PET numbers. | RESOLVED 2026-06-12 (published budget conservative; clean = rebank artifact) | `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-06-10 #12 entry); C++ comment in `AppendTruthOnlyMisses` |
| 13 | **Genuine background was frozen at CV in systematic universes.** **RESOLVED 2026-07-14** — full **188-universe** background-aware re-quote run on `runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root`: **both legs** (169 vertical via `sweep_bank_5d.py` `--dump`/`--run` with per-universe `w_bkg` + 18 lateral via the `collect_bkg_nd(universe_branch=)` direct driver with shifted `sim_background_<axis>` + 1 matched CV) → `analyze_universes_5d.py` + `adopt_unified_5d.py` (mean & CV-centered). Adopted covs `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware{,_uthrow,_uthrow_cvcentered}.root`, **both PSD** (min-eig/max ~1e-16). **VERDICT: null-effect refinement (<0.3% everywhere)** — C_syst 4.345e-38→4.351e-38 (+0.14%), combined 4.345→4.358e-38 (+0.30%), adopted mean 5.80→5.81e-38, CV-centered 6.23→6.24e-38 — confirming the analysis is insensitive to the background-CV approximation. _Historical trace:_ C++ now writes per-universe background weights/kinematics and Python consumes them; banked sweeps fail closed unless those columns exist. Existing banks/products predate the fix, so it is inert until the 12-playlist dump-all rerun, merge, and re-bank complete. **UPDATE 2026-07-14 (traced verdict = GAP; the re-quote is NOT the throw-bank rebank):** the dump-all rerun + merge landed (`runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root`) and a bkgaware THROW-bank was built (`bank_uthrow_5d_bkgaware`, 374 files) — **but that bank comes from `unified_throw.py --dump`, which is SIGNAL-ONLY** (reads `mc_signal_reco` per-universe for `sig_<band>`; reads `mc_background` only in group 0 for the CV measured target), so it carries **zero** per-universe background columns and is bit-identical to `bank_uthrow_5d` for every consumed file. Consequently **NO currently-quoted covariance includes the per-universe background systematic** — background is still frozen at CV in all of them: GBDT unified-throw C_syst (`compare_unified_throw.py:115,120` pins `measured`/`measured_weights` to the CV bank; `unified_throw_cov.py:177-193` throws vary signal+flux only), PET C_syst (`pet_systematics_5d.py:203-218` varies only truth `rho`; background enters solely via the frozen bkgsub target), and the (E_avail,W) covariance (`eavailW_covariance.py:182,187` builds one CV `measured_weights` for all universes). The one mechanism that DOES rebuild a per-universe measured target from `w_bkg` is the **vertical sweep re-quote** — `sweep_bank_5d.py` do_run (`:177` banks `{tag}_bkgw.npy`, `:232-241` rebuilds `measured_weights` per universe, `:243-246` fail-closed unless `--allow-cv-background`) → `analyze_universes_5d.py:91-100` block-sum — plus the lateral direct-driver via `collect_bkg_nd(universe_branch=)` (`unfold_nd_omnifold_unbinned.py` ~:664). **These have NOT been run on the bkgaware inputs:** no `bank_sweep_5d`/`*_bkgw.npy` exist; `uq_5d/universe_sweep/` unfolds are dated 2026-06-28/29 (pre-fix); `sweep_bank_5d.py:39` still defaults to the non-bkgaware omnifile; RUN_LOG:1439 still lists "run the #13 covariance re-quote" as deferred. **To close:** `sweep_bank_5d.py --dump --omnifile ...bkgaware.root` → `--run` all vertical universes → `analyze_universes_5d.py` (+ lateral direct-driver on bkgaware), then compare sqrt-trace vs the CV-frozen covariance. NOTE: the **PET Phase-7 retraining-response is unaffected** (it consumes only signal truth ratios, bit-identical across banks — see `PET_UQ_PRODUCTION_STATUS.md` receipts); this gap is about C_syst-final/lateral, not Phase 7. | **RESOLVED 2026-07-14** (188-universe re-quote, both legs; <0.3% null-effect; all adopted covs PSD) | `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` (2026-07-14 B5' receipts + baseline-vs-bkgaware table); `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-07-03/04, 2026-07-12 entries); `nd-unfolding/PET_UQ_PRODUCTION_STATUS.md` (2026-07-14 CRITICAL FINDING) |
| 14 | **Old unified/adopted 4D/5D/FPS covariances use the wrong contract** — one-sided endpoint powers, CV centering, varying estimator seeds, and scalar jitter subtraction. Replacement code uses actual asymmetric endpoints, one fixed estimator seed, throw-mean centering, a separately stored mean shift, MAT-biased `1/N`, exact manifests, and no jitter subtraction; 20 tests pass. **UPDATE 2026-07-14:** corrected-contract code committed and the corrected 5D artifacts are adopted — combined `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` + adopted `..._uthrow.root` (mean-centered, headline) and `..._uthrow_cvcentered.root` (CV-centered, conservative variant); throw-mean centering with the mean shift stored separately (`hJointMeanShift`), one fixed estimator seed, actual asymmetric endpoints, no jitter subtraction. These supersede the #13 bkg-CV re-quote inputs (both are the same 188-universe corrected build). 4D/FPS use the identical committed contract. | RESOLVED 2026-07-14 (corrected-contract code committed; corrected 5D artifacts adopted) | `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`; `docs/OPEN_ITEMS.md` §Active remediation gate |
| 15 | **Old PET statistical covariance is not an estimator bootstrap.** Replacement replicas fluctuate data and MC coherently, retrain at fixed estimator seed, apply the same MC draw during extraction, and require complete manifests. A corrected 20-replica component has landed on the background-subtracted target, but old PET totals and PET-vs-GBDT precision claims remain unquotable until the final systematic/lateral and targeted-retraining gates close; enlarge the statistical inventory before publication-level full-covariance use. **FLAGGED FOR CLOSE-OUT REVIEW 2026-07-14:** the three blocking gates are now CLOSED — C_syst-final (bank-invariant vertical + #13 background re-quote null <0.3%), C_lateral (PET-native detector rebuilt on the corrected target, job 55916531, alignment-verified, √tr 4.69e-39), and Phase-7 targeted-retraining (C_retrain rank-6 PSD √tr 2.19e-38). The corrected FINAL PET C_total is assembled and validated: √tr **3.878e-38, per-bin median 15.10%**, PSD in 5D + 4D marginal, block-sum exact, no double-count (`products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.npz`). REMAINING before RESOLVED/quotable: the C_stat inventory is 20 replicas ("enlarge before publication-level use" caveat still stands) — reviewer to decide whether 20 suffices or to enlarge; then PET-vs-GBDT precision claims become quotable. **Deferral decision (user, 2026-07-14):** C_stat enlargement is intentionally deferred to POST-presentation, to be scoped alongside the full-stats FPS training (not blocking the talk; C_total final stands as-is for it). | OPEN → **CLOSE-OUT REVIEW** (blocking gates closed; C_total final; C_stat inventory-size call pending) | `docs/OPEN_ITEMS.md` §Active remediation gate; `nd-unfolding/PET_UQ_PRODUCTION_STATUS.md` (2026-07-14 PHASE 8 COMPLETE) |
| 16 | **Dump-all lateral universes are CV-support-limited.** `MNV101_ACTIVE_UNIVERSE=BAND:IDX` now rebuilds selection, IDs, backgrounds, and native misses for one promoted universe. Five bands are genuinely kinematic; a targeted full-MEFHC bound is in flight for the presentation, while full 5-band coverage remains pending. Bank-derived corrected covariances must be labeled support-limited until bounded. **PET C_total link (2026-07-14):** the corrected PET C_total's C_lateral (`pet_clateral_bkgsub_5d.npz`) inherits this — its 5 KINEMATIC bands (√tr ≈1.71e-39) shift CV-selected events without re-running selection, so migrations aren't captured; weight-only bands (MinosEfficiency/GEANT) + vertical C_syst are clean. Bounded impact (≈4.4% of C_total √tr) but labeled support-limited until the 3-band bound lands. The targeted full-MEFHC 3-band migration bound is NOT yet run (no promoted-universe products/jobs on disk as of 2026-07-14). | OPEN (implementation verified; production bound pending — NOT started) | `docs/OPEN_ITEMS.md` §Active remediation gate; `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`; `nd-unfolding/PET_UQ_PRODUCTION_STATUS.md` (2026-07-14 #16 caveat) |
| 18 | **`pet_event_displays.png` / `pet_cardinality*.png` had no generating script** — ad-hoc products (absent from `make_figures.sh`), used in the July-16 talk (PET outlook) and the note on white plates. RESOLVED 2026-07-10: `nd-unfolding/pet/plot_event_displays.py` now regenerates all four PET-input figures (`pet_event_displays`, `pet_cardinality_{real,withremnant}`, `pet_truncation_retention`), light by default and dark via `TECHNOTE_DARK=1`, added to `make_figures.sh` (PET section, one invocation). **Staleness trap fixed at the same time:** the original figures were built from `of_inputs_pc.npz` (2026-06-05), which PREDATES the 06-28 truth-cloud coverage fix (#12-adjacent, commit `8cc54e9`) — that file left the truth cloud EMPTY on 72% of truth-only-miss rows (27% of all events), producing a spurious cardinality-0 spike and a biased truth mean of ~3.3. The generator now reads the coverage-FIXED `of_inputs_pc_fullcloud.npz` (empty-cloud rate 0.00%): correct truth cardinality is mean **4.43** real / **4.57** with GENIE nuclear remnants, rising smoothly to a k=2 peak with no k=0 spike. Retention/num_part argument unaffected (12th-slot 0.09%, 2.31% saturation). NOTE: `pet_vs_gbdt.py` in `make_figures.sh` still passes `--pc of_inputs_pc.npz` — verify whether the note's PET result should move to the fixed/`bkgsub` input before publication. | RESOLVED 2026-07-10 (versioned generator on FIXED input + make_figures.sh) | `nd-unfolding/pet/plot_event_displays.py`; `docs/analysis-note/make_figures.sh`; `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (06-28 truth-cloud fix) |
| 19 | **The full-event PET estimator is code-complete but unexercised, and no full-event FPS result exists.** ~~Point-cloud mode drops the muon from both classifier levels and does not wire event features through PET/MultiFold.~~ **That reason expired 2026-08-01** (`dfef335`): `DEFAULT_EVT_FEATURES` is now the 13-feature publication schema (reported (pT,p_parallel) + the muon object from `reco_muon` + reco vertex), view/timing became cloud token columns, the two legs carry separate widths via `n_evt_reco`/`n_evt_truth`, and `pet/extract_fullevent_fps.py` supplies the reweight-all + FPS extraction that J02 found missing entirely. **Decision update 2026-08-04:** the remaining blocker is now precisely specified, not an environment choice: implement separate `w_reco` Step-1 / `w_truth` Step-2 weights, make the nominal consume the hash-bound Gate-2 target, and give closure an MC-only TF path plus a powered injected-reweight test. The current nominal and closure both silently rebuild Stay-Positive in a ROOT-incompatible TF process, and the closure discards the measured target it built. Gate-2 and Gate-4 re-issues remain pending; no publication training is allowed. Separately, the older `of_inputs_pc_fps.npz` and angle-only `of_inputs_pc_fps_xps.npz` paths do not implement the complete extended FPS gate/grid. Current PET central/UQ products remain recoil-representation cross-checks; they cannot support a full-event PET result over the declared extended fiducial phase space. | **OPEN — PUBLICATION BLOCKER for full-event FPS PET** (D1/D2 implementation + Gate-2/Gate-4 re-issues pending) | `docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md`; `docs/OPEN_ITEMS.md` §PET full-event + FPS measurement-domain gate |
| 20 | **The standard (non-FPS) P4 provenance chain cannot record a background footing at all, and the ten standard lateral endpoint unfolds on scratch are purity-footed, unreceipted, and were produced by a retired launcher.** Found 2026-08-07 by a footing check on `nd-unfolding/active_universe_5d/standard/unfolds/`. Three separable defects. **(a) Footing-blind by construction:** `p4_evidence.py` contains no `bkg`/`footing`/`mode` handling — `p4_standard_manifest.json` binds `endpoint_sha256` plus code/config hashes only. Contrast `fps_provenance.require_footing`, which fails closed when an entry has no `bkg_mode` ("unprovable"). So whichever footing the standard 5D chain is declared to stand on, that choice is **unprovable downstream** until a field exists to hold it. **(b) The existing ten are purity-footed,** positively identified (not merely unstamped) by the same three-part evidence `fps_build_control_manifest.py` uses: neither possible producer passes `--bkg-mode` (`run_p4_unfold_std.sh:43`, retired `run_active_lateral_unfolds_interactive.sh:40`); the driver default is `purity` (`unfold_nd_omnifold_unbinned.py:566`); and the driver announces its mode *only* on the negweight branches (`:842`, `:895`) while the purity branch (`:883`) is silent and instead emits `build_measured_training_nd`'s `[INFO] measured training: sum=… zero=…`, which all ten logs carry and no log carries a `bkg-mode=` line. `--bkg-mode` and both announcements landed together in `cf8a4a6` (2026-07-11), a week before these 2026-07-18 files, so the absence is informative rather than a version gap. **(c) No receipts, retired producer:** the directory holds **zero** `.done` files, though `run_p4_unfold_std.sh` writes one last after an atomic rename (and its legacy-attest path writes one too); the ROOTs date 2026-07-18 03:53–05:34Z while `run_p4_unfold_std.sh` was added the *same day* in `553a6a6` as the fail-closed repair. Note (b) is **consistent with the rest of the chain** — only eleven launchers in the repo pass `--bkg-mode` and all are 2D-negweight/FPS/PET, so the central, 169 vertical and 18 detector unfolds are purity-footed too. Whether that is publication-correct is a scope question on runbook locked-decision 1 ("Scalar FPS/N-D") and is **Joseph's call**; it sizes the remaining GBDT work by an order of magnitude. Fix for (a) is cheap and is required under either answer. **UPDATE 2026-08-07 — (a) FIXED, (b) DECIDED, (c) still owed.** **(b) DECIDED by Joseph 2026-08-07: the standard 5D chain is quoted on `purity`, revisited before submission** (runbook §2 reading (A)); the revisit obligation is an open item in `docs/OPEN_ITEMS.md` (G-0) and what would close it is a full 5D 187-universe both-mode comparison at 5-iter lgbm — the present 5D evidence is a two-universe spot check at 1 iter/`hist`, so **do not write "footing proven irrelevant in 5D"**. **(a) FIXED (G-1):** `p4_lib.P4Config` gains a validated `bkg_mode` (participating in `config_hash`), `P4Config.footing()` emits the nested five-key + `bkg_mode` block in the *producer's* shape, `p4_lib.require_standard_footing` fails closed on absent/mismatched/flattened footing with `fps_provenance.require_footing`'s "unprovable" semantics, and `p4_evidence.py` now writes both `footing` (declared) and `footing_evidence` (per-endpoint, classified from the unfold log) into `p4_standard_manifest.json` and blocks when they disagree. `p4_lib.classify_log_bkg_mode` encodes BEN-041's asymmetry — the driver announces only on the negweight branches, so measured-training-signature + no `bkg-mode=` line *positively identifies* purity, while a log with neither is `None` = unprovable rather than assumed-purity. `run_p4_unfold_std.sh` now passes `--bkg-mode` explicitly (read from `P4Config`, so launcher and manifest cannot drift) and stamps `bkg_mode` into both receipt shapes; the value is the driver default, so this is a **provenance change and a physics no-op — produced ROOTs must hash identically to the 2026-07-18 ones**. 13 new tests (41 total green), fixture is a verbatim real unfold log, plus a contract test pinning the classifier to the driver's actual print statements. **`fps_provenance.py` deliberately untouched** — the standard constants are a separate copy, not an import (BEN-040's lane is hash-pinned and freshly green). **(c) still owed:** the ten ROOTs remain unreceipted pending the G-3 attest-or-reunfold step. | **(a) FIXED 2026-08-07; (b) DECIDED 2026-08-07 = purity, revisit deferred; (c) OPEN — attestation pending G-3** | `docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md` §2–§3; `nd-unfolding/p4_lib.py`; `nd-unfolding/p4_evidence.py` |
| 21 | **`run_p4_standard.sh`'s "HARD GATE" on covariance construction checks only that a variable is non-empty, so it cannot distinguish a verifier PASS from a caller asserting one.** `:41` reads `if [[ -z "${P4_VERIFIER_PASS}" ]]; then … Refusing.` — any string (`P4_VERIFIER_PASS=x`) authorizes stages 4–6. Nothing binds the value to a `standard-p4-verifier` verdict, a receipt file, or the committed patch hash that the comment at `:11` says the verifier must PASS on. Found 2026-08-07 while scoping how much of the GBDT close-out could run unattended. Two reasons this matters more than it looks: (a) the refusal message *names the variable to set*, so the failure mode is not "agent guesses the bypass" but "gate documents its own bypass to whoever hits it"; (b) it guards the transition from validated inputs to a candidate publication covariance, which is exactly where an independent check is worth the most. Note the chain is otherwise well-shaped here — it stops at `std_final5_candidate.root` and prints `CANDIDATE only; adoption is a separate authorized step`, so the *adoption* boundary is real; it is only the verifier boundary that is nominal. Same family as BEN-040 (a fail-closed gate that cannot fail in the direction that matters). Fix options, cheapest first: require the token to equal the sha256 of a `standard-p4-verifier` receipt JSON whose `verdict` is PASS and whose `code_rev` matches `git rev-parse HEAD`; or drop the env var and read that receipt directly. **Until fixed, treat the gate as a human checkpoint and do not let an executing agent set the variable** — recorded as a trap in the GBDT close-out runbook §5. **2026-08-07 — THIS GATE WAS LOAD-BEARING, not hypothetical.** The GBDT close-out session was instructed to run G-0→G-4 unattended, reached this gate, and stopped without setting the variable. Had it self-authorized — which the refusal message invites by naming the variable — stages 4–6 would have run and **broken a stage**: they are non-executable at HEAD (#22), so the chain would have written a candidate ROOT at stage 4 and then died on an argparse error at stage 5, leaving an unvalidated candidate covariance on disk in the candidate namespace with no validation receipt and no projection. Worse, the failure would have looked like a transient tooling problem rather than what it is — the still-outstanding defect 1 of six that BLOCKed repair-3 (BEN-046) — so the likely next move under "finish the task" pressure is to *fix the flags* and re-run, producing a chain that executes and is still wrong on the other three sub-parts of defect 1 plus defects 2–6. **So the gate's value here was not that it caught a bad candidate; it was that it stopped an agent from turning six known unrepaired defects into a plausible-looking artifact.** That is the argument for binding the token to a receipt rather than deleting the gate as advisory: an advisory gate that is honoured only by convention did, in this instance, do the entire job. Note also that a fix must not be "check the variable harder" — an agent that can set an env var can write a receipt file; bind it to the sha256 of a `standard-p4-verifier` receipt whose `verdict` is PASS **and** whose `code_rev` equals `git rev-parse HEAD`, or drop the variable and read that receipt directly. | **OPEN — gate is advisory in practice; treat as human checkpoint. Demonstrated load-bearing 2026-08-07: an autonomous run would have crossed it and broken a stage.** | `docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md` §5; `nd-unfolding/run_p4_standard.sh:11,41`; `KNOWN_ISSUES.md` #22; `docs/orchestration/REPAIR4-DEFECT-STATUS-20260807.md` |
| 22 | **`run_p4_standard.sh` stages 4–6 are non-executable at HEAD: the driver calls the validator and projector with retired argument schemas and a ROOT key nothing produces.** So the `P4_VERIFIER_PASS` gate (#21) guards a path that **cannot succeed even when authorized** — it would abort at stage 5 on an argparse error, after stage 4 had already written a candidate ROOT. Found 2026-08-07 executing the close-out runbook's G-4; this is verifier defect 1 of the six that BLOCKed repair-3 `74fa362`, still 100% live, re-verified against HEAD in the same turn. Three separable mismatches. **(a) Validator CLI:** the driver passes `--active … --support … --merged-dir …` (`run_p4_standard.sh:49-52`), but `p4_validate_active_lateral.py:35-39` defines `--candidate --support --manifest --merged-audit --out`, all `required=True`. `--active` and `--merged-dir` do not exist, and three required options are absent. **(b) Projector CLI:** the driver passes `--proj "${CAND}/M_5d_to_4d.npz"` (`run_p4_standard.sh:54`), but `p4_project_4d.py:46-49` defines only `--c5 --manifest --out --central-rel`; there is no `--proj`. **(c) Nonexistent ROOT key:** the driver names `hCov_std_final5_candidate` twice (`run_p4_standard.sh:50,53`), and a repo-wide grep finds that string **only in those two lines** — nothing writes it. `p4_build_components.py:159-162` writes `hCov_active5d_<band>`, `hCov_active5d_total`, `hCov_stdsyst5d_total_candidate`, and `hCov_stdcombined5d_total_candidate`. **Why it survived:** `STOP_AFTER` defaults to `evidence`, so the default path stops at stage 2 and stages 4–6 have never been executed — an unexecuted path is an untested one (the BEN-040 lesson, one lane over). The 2026-08-07 preflight ran cleanly precisely because it stopped before this. **Do not repair by editing the driver alone** — the argument names are the visible symptom, and verifier defect 1 also requires the stage ORDER to change (merged audit → unfold → endpoint evidence) and `AGENT_A_HANDOFF.md:95` to be updated to the same executable contract. Repairing only the flags would produce a chain that runs and is still wrong. **Confirmed independently by Joseph 2026-08-07**, who checked all three mismatches himself and authorized repair-4 as this lane's next packet. **RESOLVED 2026-08-07 by repair-4 (`ba2cdd8`) and CLOSED by an independent verifier pass** (`runs/standard-p4-verifier/20260807T134623Z-repair4-verdict.json`, which closed defects 1 and 5). Stage order is merge+audit → unfold → evidence; the validator and projector are called with the options they actually define; and the candidate key is single-sourced in `p4_lib.CANDIDATE_TOTAL_KEY` and read back by the driver, so it cannot drift again. Note the knock-on: because the reorder puts a receipt-WRITING stage before evidence, `STOP_AFTER` now defaults to `audit` rather than `evidence`. **Stages 4–6 are still not authorized** — that is the verifier gate (#21), and repair-4 BLOCKed on four other defects. | **RESOLVED 2026-08-07 (verifier-closed); stages 4–6 still gated on #21 and repair-5** | **`docs/orchestration/REPAIR4-DEFECT-STATUS-20260807.md` — all six defects with per-sub-part HEAD status**; `docs/orchestration/runs/standard-p4-verifier/20260718T182040Z-send-8e4ca3d7.jsonl` (the original BLOCK, with citations); `nd-unfolding/run_p4_standard.sh:49-55` |
| 23 | **`p4_evidence.py` binds the code that exists NOW, not the code that produced the artifacts it is attesting — so re-running it silently re-attributes the endpoints to a newer driver and a newer C++ binary.** Found 2026-08-07 by re-running the (idempotent) evidence stage and diffing the tracked `p4_standard_manifest.json`. Every **physics** binding was stable — `central5d_sha256`, `central4d_sha256`, `mask5d_hash`/`mask4d_hash`, `config_hash`, `endpoint_sha256`, `axis_edges` all byte-identical — which is the reassuring half. The provenance half moved: `binary_sha256` `6b60fc51…` → `61d7dfbf…` (`binary_mtime` +290,733 s ≈ 3.4 days), `source_blobs.unfold` `7b65ebcf…` → `dc74c38f…`, `source_blobs.launcher` `559bc3fb…` → `f2a49e7d…`, plus the corresponding `source_commits`. The cause is structural, not a race: `:150-151` hashes `MINERvA101/opt/bin/runEventLoopOmniFold` **as it is on disk at run time**, and `_blob`/`_srccommit` (`:137-141`) hash the **working-tree** copy of each source path. Neither is tied to the artifact being described. **Why it matters:** the ten endpoint ROOTs are dated 2026-07-18 and were produced by the *older* driver blob; after a re-run the manifest asserts today's `unfold` blob and today's binary alongside 07-18 `endpoint_sha256` values, i.e. it claims a producer that demonstrably did not produce them. Nothing is corrupted and no number moves — but the manifest is weaker as evidence exactly where it is meant to be strongest, and an attestation built on it inherits the mis-attribution. This is the standing verifier's **defect 3** ("regenerate evidence only from exact committed blobs … record the commit containing each blob") observed live. **Mitigations, cheapest first:** record the producing blob/binary from the endpoint `.done` receipts rather than re-deriving it from the working tree; or fail closed when `source_commits.unfold` is not an ancestor of the commit that the receipts name; or split the manifest's "what exists now" fields from its "what produced this" fields so the two can never be read as one claim. The 2026-08-07 preflight's regeneration was reverted (`git checkout --`) so the committed manifest still records the 07-18 producers, and a copy of it is preserved at `docs/orchestration/state/p4-standard-attestation/p4_standard_manifest-20260718-preserved.json`. | **OPEN — provenance mis-attribution on re-run; no number affected; part of the six-defect repair-4 scope (BEN-046)** | `nd-unfolding/p4_evidence.py:137-141,150-151`; `docs/orchestration/followup-agent-A-standard-05.md` (defect 3) |
| 24 | **`endpoint_sha256` binds an ARTIFACT, not a derivation — the standard 5D endpoint ROOTs are not bit-reproducible, so hash-based attestation can only ever certify "same file", never "same computation", and any legitimate re-unfold breaks the whole manifest chain.** Measured 2026-08-07 by re-unfolding all ten endpoints from the same merged inputs, same committed driver, same `--seed 42`, same `--bkg-mode purity` (job `56471429`, 10/10, zero failures) and comparing against the 2026-07-18 set: **0 of 10 sha256 match**, while the CONTENTS agree to a worst per-bin relative difference of **1.9e-11** and an integrated cross section of **2.6e-14**. The physics is unchanged; the bytes are not. Cause is reduction order — LightGBM/OpenMP partitioning depends on thread count (07-18 ran CONC=4, the re-run CONC=6) and five OmniFold iterations amplify last-bit differences; `sqrt(N)*eps` for ~1e7 events is `7.0e-13`, the same order as the measured pooled mean `-1.76e-13`. **Why this is a design defect and not a curiosity:** (a) `p4_standard_manifest.json`'s `endpoint_sha256` pins one particular RUN, so it cannot answer "was this produced by the declared computation?"; (b) `endpoint_manifest_hash` is derived from those ten hashes, and the validator's merged-inseparability gate consumes it, so **a correct, authorized re-unfold invalidates the entire chain** — a manifest that breaks on correct behaviour is a defect in the manifest, not in the behaviour; (c) the legacy-attest path (`run_p4_unfold_std.sh`, removed in repair-6) rested on "re-unfold and compare hashes", which **could never have succeeded** — it could only certify that a file had not changed on disk, which is a storage-integrity property, not a provenance one. **What should replace it:** content comparison at a declared tolerance, `p4_lib.check_reproducibility` with `REPRO_RTOL_PER_BIN = 1e-9` and `REPRO_RTOL_INTEGRAL = 1e-12` — a SPECIFICATION set by Joseph 2026-08-07, ~2 orders above the measured floor so a CONC change does not force a re-derivation, with `REPRO_MEASURED_FLOOR` recorded separately so re-measuring can never silently move the gate. Keep sha256 for storage integrity (has this file changed since I wrote it?) and stop reading it as derivation identity. | **OPEN — tolerance declared and helper landed; the manifest chain still binds hashes and must be migrated to content comparison** | `nd-unfolding/p4_lib.py` (`check_reproducibility`, `REPRO_*`); `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-08-07 re-unfold entry + its correction) |
| J36 | **Global POT scaling discards the per-playlist Data/MC ratio, skewing the MC playlist mixture.** `get_pot_scales` (`2d-unfolding/unfold_2d_omnifold_unbinned.py:114-123`) reads two `hadd`-summed `TParameter<double>` from the merged ROOT and returns one `data_pot/mc_pot`, applied uniformly as `w * pot_scale` in every collector. Verified 2026-08-01 from the 12 per-playlist pairs in `docs/orchestration/state/g2-gate1-all12-validation-20260719.json`: the ratios span **0.1707 (1B) to 0.2371 (1D), max/min − 1 = 38.9 %**, against a global 0.2124. Under global scaling playlist 1M (18.0 % of MC POT) is over-weighted by 17.1 % and 1D+1F (26.4 % combined) under-weighted by ~11 %; POT-weighted mean absolute mixture error **9.4 %**. **The total normalization is NOT biased** — global and per-playlist scaling agree exactly when the MC rate per POT is playlist-independent — so this cannot explain or be excluded by the 2D paper reproduction at 1.011. The error is purely in the playlist *mixture* and propagates only through playlist-dependent flux shape and detector conditions. Note the same `hadd`-summing hazard **is** explicitly defended two functions away for `pTmu_fiducial_nucleons` (`:1320-1329`, "do not trust the merged `TParameter<double>`") and trap #8 below; the POT ratio was never given the same treatment. Needs a scoping decision, not urgent. | **OPEN — scoping decision owed; no result withdrawn** | `docs/orchestration/AUDIT-FINDINGS-20260731.md` §7 J36 |

## Resolved traps that WILL bite again if forgotten

| # | Trap | Detail lives in |
|---|---|---|
| 6 | **Never bare-`hadd` a `_universes_full` omnifile** — ROOT 100 GB TTree rollover aborts mid-merge leaving a partial missing the data+bkg trees. Use `2d-unfolding/uq/hadd_universes_full.py`. | `2d-unfolding/2D_OMNIFOLD_REFERENCE.md` §Event-loop workflow |
| 7 | **Never feed the event loop a combined MEFHC manifest** — it silently applies the first playlist's flux to all 12. Run per playlist, merge after. | same |
| 8 | **`hadd` sums `TParameter<double>`** — POT summing across playlists is correct; a per-file nucleon count would be inflated 12×, hence the fixed tracker constant 3.2353e30. | same |
| 9 | **Pre-2026-04-25 event-loop outputs** use the IsMinosMatchMuon stub (≈10% background) — regenerate before comparing to paper numbers. | same |
| 10 | **eavailW completeness double-count** (2026-06-09, FIXED): OmniFold step-2 already efficiency-corrects; an extra reco-pass completeness division inflated the data ~2×. Caught by the marginal self-validation gate — keep that gate in any new covariance script. | `docs/FUTURE_DIRECTIONS.md` tombstone → `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` (2026-06-09) |
| 11 | **Stale PET `ExtraEnergyClusters_*` input** (FIXED): wrong, mostly-empty branch; point-cloud chain rebuilt from `CVUniverse::GetRecoClusters()`. | `VALIDATION_LEDGER.md` (Known Audit Findings) |
| 17 | **Never run PET cross-section extraction in the TensorFlow-module Python** — it has no PyROOT. The PET replica launcher switches to the activated `root_6_28` interpreter after GPU training, and the extractor self-reexecs there so already-snapshotted jobs are safe. | `nd-unfolding/pet/{sbatch_pet_bootstrap_replica.sh,extract_bootstrap_replica.py}` |

## Resume-skip validates existence, not completeness (found 2026-07-17, 4D corrected uthrow)
`[[ -s $OUT ]] && skip` resume guards (used across many sbatch launchers) treat any non-empty
output as done. Producers that atomic-save per-unit into one file (e.g. `unified_throw_cov.py
do_throws` per-throw saves) leave VALID-but-partial files when interrupted — the resume then
permanently skips them. Bit us: comb4dCc 55971617 failed on 15/160 missing throws because slabs
31,34-39 were partial leftovers of an interrupted multinode run; all 40 array tasks "COMPLETED".
Caught only by the combine's `--expected-throws` manifest gate. Repair: partials moved to
`uq_4d/corrected/uthrow_slabs_4d/partial_20260716_interrupted/`, regen 56025478 -> combine
56025481 -> adopt 56025483. Fix pattern for future launchers: content-validated resume (open the
file, check unit inventory) or write-to-temp + rename-on-complete. (BEN-023.)

**FIXED REPO-WIDE 2026-08-01** (closes BEN-023 and audit J35 + J10, which are the same defect
found independently in two subtrees). Completion is now an explicit record, not an inference from
size: `lib/resume_guard.sh` provides `rg_skip_if_complete` / `rg_run` / `rg_publish`, which stamp a
`${OUT}.done` marker **only after the producer exits 0** and bind it to the output's size+mtime, so
a later truncation invalidates its own marker. An interrupted producer cannot leave one behind, so
the resume re-runs. 85 guards across 84 shell files converted. The marker convention is deliberately
the one `nd-unfolding/run_p4_unfold_std.sh` already used — that script was the in-repo precedent and
is left alone, as is `run_p4_merge_audit_std.sh`; both already validate content.

On the Python side (J10) `nd-unfolding/pet/atomic_write.py` carries the transaction —
temp sibling → fsync → `os.replace` → marker last — and `train_fullevent_nominal.py:254` uses it
instead of the bare `np.savez_compressed`, plus a no-clobber guard that refuses to replace an
output already marked complete (`--allow-overwrite` opts in) and that fires *before* the eight
GPU-hours. Gate-4 re-issued as
`docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260801.json` (Step 2b; no physics
re-run). `fullevent_dump_contract.py` was deliberately left byte-identical — it is frozen by the
G2 **dump-provenance** receipt, not a code gate; see that receipt's `not_reissued_deliberately`.

**Two traps in the fix itself.**
1. **Nothing on disk has a marker.** The first resume after this lands re-runs everything.
   Run `lib/backfill_completion_markers.sh --validator {root|npz} --glob '<pattern>'` over the live
   output trees *before* resubmitting — RESTORE-2026-08-03 Step 0b. Read its FAIL list: those are
   the partials the old guard was hiding.
2. **`RESUME_ADOPT_LEGACY=1` is the old bug, opted into.** It adopts on a bare size check and warns
   every time. Prefer a validator.

Regression-pinned by `nd-unfolding/tests/test_resume_guard.py`, whose repo-wide scan fails if
`[[ -s $OUT ]] && skip` reappears anywhere, and `nd-unfolding/tests/test_atomic_write.py`.

## The engine's "Last val loss" prints the FIRST epoch, not the last

`omnifold_nn/omnifold/omnifold.py:303` logs `hist.history['val_loss'][0]` under the label
`Last val loss`. Index 0 is **epoch 1**. Anyone judging convergence from the training log is reading the
first epoch of the fit.

Found 2026-08-06 by a fresh-context review of the D2 powered-closure FAIL (job 56381674), and it had
already done damage: two sessions independently proposed "the fit is optimization-limited, raise
`epochs`" without opening the history pickles. The pickles refute it -- step-2 train loss moves 3.2e-5
across 8 epochs in iteration 2, and that iteration's `val_loss` gets *worse* (0.829560 -> 0.829612, best
at epoch 1). A fit with no remaining gradient signal, mislabelled as a fit starved of steps.

Related, same file: `ModelCheckpoint(save_best_only=True)` (`:272-275`) writes **best-val** weights, while
`reweight` uses the **last-epoch in-memory** model. On-disk checkpoints are therefore not bit-identical to
what a run actually used -- calibrate before trusting an inference-only reproduction from them.

Fixing the label touches `omnifold.py`, which is hash-bound by the Gate-4 launch-code gate, so it must
ride a deliberate re-issue rather than a drive-by edit.

Extended 2026-08-07: the plateau is a property of **all six** trainings of `56381674`, not just iteration
2 (train loss moves 1.13e-3 across 8 epochs on the first, 3.0e-5 on the last; val argmin at {5,5,7,1,6,5}
of 8). Two consequences for anyone reading these logs. `EarlyStopping(patience=10)` **cannot fire** at
`epochs=8`, and Keras 2.15 restores best weights *only* inside its stop branch (`on_train_end` merely
prints) -- so every run on this campaign has used last-epoch weights, and the `ModelCheckpoint` mismatch
noted above is therefore the norm rather than an edge case. `ReduceLROnPlateau` is at `patience=1000`
(`:263-265`) and `get_optimizer` returns a bare Adam at a flat LR (`:376-380`, `num_steps` accepted and
unused), so no schedule ever engages either. Table and consequences:
`docs/orchestration/FINDING-20260807-d2-underfitting-probe.md` §1.

## The FPS extractor divides the cross section by a reco efficiency it must not divide by

**RESOLVED 2026-08-06** (option A, authorized by Joseph; fix reviewed by an independent fresh-context
session before commit). Left here rather than deleted: the *reason it survived* is the reusable part.

**Severity, CORRECTED.** The first write-up of this entry said "2.36x on the integral and 398x in the
lowest `p_parallel` bin". Both numbers were wrong and both were too small:

* `2.36 = 1/<a>` is what you would get dividing the *aggregate* by the *global* acceptance. The code
  divided **cell by cell**, so by Jensen the integral inflates far more:
  `sum_b m_b/a_b / sum_b m_b = **122.6**` from the committed acceptance map, and **48-177x** per pT row
  over the rows carrying >99% of the truth mass.
* `398 = 1/0.00251` is the `p_parallel` **marginal slice** [0, 0.75], not a cell. The worst single
  **cell** is `a_b = 0.0012397`, i.e. **807x**.

Recomputed independently this turn from `products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`.
Legs 1-3 below were verified in source before the finding was relayed.

1. `extract_fullevent_fps.py:390-404` `completeness_2d` computes
   `c = sum_w(pass_truth & pass_reco) / sum_w(pass_truth)` -- **reco efficiency**. Its docstring says
   "Verbatim `PETxsec5D._comp`".
2. `xsec_nd.py:79` places it in the **denominator**: `denom = completeness * flux * n_nucleons * pot * vol`.
3. `extract_fullevent_fps.py:431-434` histograms `(w_truth * push)` over **all** `pass_truth` rows,
   including truth-only misses, whose `push` is the `nu_k` OmniFold step 2 assigns them
   (`omnifold.py:218-220`). `counts` is therefore **already acceptance-corrected**, so dividing by
   efficiency is a **double correction**.

On this exact 285-cell grid the correct completeness is **identically 1**: the validated GBDT FPS unfolds
carry `globalCompleteness = 1.0000000000000002` with all 266 nonzero `hCompletenessND_flat` bins at
1.000000, and `unfold_nd_omnifold_unbinned.py:993-999` defines completeness as a **coverage** correction,
not an efficiency. `PETxsec5D` only ever survived carrying an efficiency there because
`pet_systematics_5d.py:127-141` overrides its own value with the GBDT one; the FPS port deliberately
dropped that anchor (`extract_fullevent_fps.py:459-461`, "NONE -- no such anchor exists for this domain").
**That comment is false** -- the anchor exists in this repo, on this grid, and it is the constant 1.

**Two tests look like coverage and provide none:**

- `tests/test_fullevent_extract.py:351-376` recomputes the formula by calling `ex.completeness_2d` **itself**
  and asserts bit-equality (`rtol=0, atol=0`). It verifies the extractor calls the helpers it calls, and has
  **zero power** over whether the quantity is the right physics. This is the self-agreement antipattern of
  `AUDIT-FINDINGS-20260729-B.md` section 4.
- `tests/test_fullevent_extract.py:331-342` **pins the reco-efficiency semantics as intended behaviour**, so
  anyone repairing the double-correction must first break a test that reads as authoritative.

**FIXED via (A): the division is gone.** Joseph authorized (A) on 2026-08-06. The argument recorded in
the extractor is now **structural rather than empirical**: `extract_cross_section_nd`'s `completeness`
argument means *coverage of the truth denominator by the OmniFold input*
(`unfold_nd_omnifold_unbinned.py:992-999` builds it as `of_in/denom_nd`), and this extractor has no
separate truth denominator -- the declared fiducial domain **is** `pass_truth` -- so coverage is **1 by
construction**. The GBDT `globalCompleteness = 1.0000000000000002` is corroboration, not the reason;
leading with the measurement is what invites a future re-anchoring. Option (B) (mask `counts` to
`pass_truth & pass_reco`) was rejected: it would delete the FPS extension the campaign exists to add.

`comp` keeps one role, **as a reporting mask only**. It subsumes `denom > 0` by construction, so the
reported domain is set entirely by the reco efficiency; this **preserves** the pre-fix domain, since
`comp == 0` already forced those cells to 0. It is a **floor**, not the acceptance-supported vs
model-dependent tiering decision, which remains open at `docs/OPEN_ITEMS.md:430-438` and covers far more
truth mass (25.93% below `a_b < 0.01`) than this mask's 4 cells (4.6e-7 of truth mass).

Coverage = 1 is now **guarded, not assumed**: `assert_truth_denominator_coverage` fails closed, mirroring
`unfold_nd_omnifold_unbinned.py:747-752`, which raises rather than assuming its analogue.

**Step 4b is unblocked.** Step 4 was never affected.

## The same construction exists in `pointcloud_projection.py`, off the gated path

`nd-unfolding/pet/pointcloud_projection.py:236-241` has the identical shape -- `counts` over
`pass_truth`, `comp = ofin/denom`, passed as the divisor. It is **not** on the gated publication product
path, so it is recorded rather than fixed, so that it is not rediscovered as a new finding. Anything
promoting that path to a product must settle it first.

## The closure driver persists no inference contract

`closure_powered_truth_reweight.py:287` saves only `dump_rows_a/b`, `weights_push`, `mc_indices`.
Architecture comes from `meta` (`:261-263`) and the input normalization is derived inside
`build_fullevent_loaders` at run time, so **there is no stored normalization to assert against** when
reproducing a run by inference. The nominal driver stores its norms; the closure driver does not. Any
inference-only reproduction must reproduce the same row population (`dump_rows_b` makes that possible) and
must treat the spectrum reproduction as its only falsification handle.

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

## `step1_class_ratio` in the nominal artifact is a stored TARGET, not an achieved measurement

Found 2026-08-07 by making the mistake. Investigating the nominal's fold-forward failure I read
`pet_fullevent_nominal_weights.npz`'s `step1_class_ratio = 1.1240802949941018`, saw it equal Gate-2's R
exactly, and concluded *"not the classic step-1 defect — that signature is the class ratio forced to 1, ours
is exactly R."* **That inference is invalid.** `train_fullevent_nominal.py:464` sets
`class_ratio = target_meta.get("step1_class_ratio")` — from the loader's target metadata — and stores it
verbatim at `:505`. `fullevent_fps_dataloader.step1_class_ratio_from_dump` derives R from the dump's data/MC
yields. So the field is **the target R, re-stored**; it can never disagree with R and therefore carries **zero
information** about what step 1 achieved. Agreement is tautological.

The trap is the name. A field called `step1_class_ratio` sitting beside genuine measurements
(`cap_saturation_frac`, `fold_forward_sum_w_push_reco`) reads as "the class ratio step 1 produced". It is a
copy of the input. **Consequence:** the step-1 under-achievement hypothesis is *not* ruled out for the
2026-08-07 nominal, and it is now the leading candidate — the historical defect drives the effective ratio
toward 1, and a folded-forward ratio of 0.7465 against a required 1.1241 is the right direction for it.

**Fix forward, two parts.** (1) Rename or re-document the stored field so it cannot be read as an outcome —
`step1_class_ratio_target` would have prevented this. (2) The achieved value has now been measured by
trajectory job `56525829`: iteration 0 is correct-sign and within 9.74% of R, while iterations 1 and 2
are wrong-signed. The defect is therefore in post-feedback iteration dynamics, not an initial class-ratio
normalization failure. Detail and exact numbers: `docs/orchestration/FINDING-20260807-step1-under-achieves.md`.

## 25 tests ran only from purgeable scratch, and one still does

Found 2026-08-07 while working plan Step 4. The cluster suite collected **764** tests against the local
tree's 710, and part of that gap was not path-dependent skips: **two test files existed only on
`/pscratch`, in neither tree's git**.

- `nd-unfolding/tests/test_uq_remediation.py` — **20 tests**, including the cluster suite's single
  remaining failure. Now **tracked** (and its fixture fixed, below).
- `nd-unfolding/tests/test_cstat_100rep.py` — **5 tests**, **still untracked**, because it imports
  `combine_cstat_bkgsub_100rep`, and **that module is untracked too**. Committing the test alone would
  guarantee a *collection error* (`ModuleNotFoundError` interrupts the whole run), which is strictly worse
  than a failing test. Committing both would import unreviewed code into the tracked tree. Left for a
  decision rather than resolved unilaterally.

Why this matters beyond tidiness: 25 tests enforcing campaign invariants were one `/pscratch` purge from
vanishing, and nothing in git referenced them, so a fresh clone silently ran 25 fewer checks than the
cluster did. This is the same failure that cost 38 unified throws and left two production launchers
untracked until 2026-08-06 — a purgeable filesystem holding load-bearing artifacts nothing else records.
**When local and cluster collection counts disagree, resolve the difference to specific files before
assuming it is environmental.**

## The J28 combine guard was rejecting a stale fixture, not being over-strict

`test_uq_remediation.py::UnifiedThrowTests::test_synthetic_slab_and_block_combine_end_to_end` failed on both
trees because its synthetic slabs carried no `flux_normalized` stamp, and `081ae4a` correctly made
`--combine` refuse unstamped slabs (`unified_throw_cov.py:332,372`). Plan Step 4 framed the question as
*fixture-stale versus guard-over-strict*; the answer is **fixture-stale**.

A fixture built inside the test has no flux normalisation to get wrong — there is no `Φ_CV` division to
correct — so it is normalised by construction and the stamp states that. **Stamping loses no coverage**: the
rejection behaviour is separately asserted by
`test_flux_universe_fix.CombineRefusesUnstampedSlabs::test_predicate_accepts_only_a_stamped_slab`, verified
still passing after the change. The guard stays fail-closed, which is the point of it.

## J28's scope misses a sixth site: `eavailW_covariance.py` divides every flux universe by the CV flux

The J28 fix commit `081ae4a` touches **12 files and `eavailW_covariance.py` is not among them**, and
neither `AUDIT-FINDINGS-20260731.md` nor this file scopes it into J28's blast radius. But it carries
the same defect by the same mechanism:

- `:104` loads `flux_bins` **once**, from the CV histogram `pTmu_reweightedflux_integrated`;
- `:232` passes that same CV array into `extract_cross_section_nd` on **every** call, with no
  per-universe override — contrast a fixed site, `unified_throw_cov_5d.py:67`, which threads
  `d["flux"] if flux is None else flux` precisely so a universe can supply its own `Φu`;
- `:259 def _y_band(sig_u, td_u)` takes weight arrays only — there is no flux parameter to thread;
- `:274-276` runs **all 100 PPFX flux universes** through `_y_band` and forms
  `C_flux = mat_covariance(fX)`, added into `C_syst` at `:277`.

So every flux universe is divided by `Φ_CV` instead of its own `Φu`, which **removes the normalization
spread the flux universes exist to carry** and therefore *understates* `C_flux`. Direction is fixed by
the same identity the re-roll used; magnitude is not, because this is a **code read and has not been
run** — do not quote a number for it. For scale only, the analogous correction in the 5D lane raised
`sqrt_tr_flux_block` by 316.83%.

Nothing quoted today is wrong: `values.tex:53-54` records the (E_avail,W) significances as removed
2026-07-12, and `sec_eavailw.tex:136-138` states compatibility "is not evaluated without the corrected
projected covariance." But that corrected covariance **is** a stated deliverable, and it could not be
built from this script as it stood. Found 2026-08-06 by a fresh-context review of the Step 2
classification and confirmed independently at the mechanism level.

**CODE FIXED 2026-08-06, NO NUMBER PRODUCED — the same footing 081ae4a had for the first five sites**
("the code fix is committed, fail-closed, and mutation-tested … no corrected number exists yet").
`xsec_ew` and `_y_band` now take a `flux` override, and the flux loop resolves a per-universe table via
`flux_universe.resolve_flux_ratio_table` — reusing the helper 081ae4a already shipped rather than
inventing a mechanism. `flux=None` still means the CV flux, which is **correct** for the CV and for
every knob band (a knob does not move the flux integral) and wrong only for a flux universe; same
`d["flux"] if flux is None else flux` shape as `unified_throw_cov_5d.py:67`.

**Fail-closed, no silent CV fallback:** `resolve_flux_ratio_table` refuses to run when neither a bank
nor a `--flux-universe-file` is usable, and `_validate_ratio_table` separately rejects an all-ones table
as "the J28/Task #70 bug, not a valid table". Reproducing the old behaviour now requires an explicit
`--allow-cv-flux-universes`, which prints that it understates `C_flux`.

Guarded by `tests/test_flux_universe_fix.py::EavailWFluxBlockIsPerUniverse` — static, because this
module imports ROOT and reads a 142 GB omnifile, and **proved to have power**:
`test_the_prefix_source_would_fail` reconstructs the pre-fix source and requires all three guards to
fire. The guards use unittest assertions rather than bare `assert`, so `python -O` cannot silently empty
them. `eavailW_covariance.py` was also added to that file's `SyntaxOfTouchedFiles` list.

**Still open:** no `(E_avail,W)` covariance has been rebuilt with the fix — that needs the cluster and
belongs with the `M C_5D M^T` projection `OPEN_ITEMS.md` requires. The script is bound by no receipt or
gate, so this changed no hash binding (verified: ALL BINDINGS INTACT).

## The step-2 checkpoint is not the model that produced `weights_push`, and full-event extraction is blocked by it (found 2026-08-07)

`omnifold.py:272-275` checkpoints with `save_best_only=True`; `:266-268` sets
`EarlyStopping(patience=self.patience, restore_best_weights=True)` and `:128` takes `patience` from the
engine default `10`. At the nominal `epochs=8` the patience can never be exhausted, and Keras 2.15
restores best weights only inside the `wait >= patience` stop branch, so **the model in memory at
`reweight` time is the last epoch while the file on disk is the best-val-loss epoch.**

`train_fullevent_nominal.py:497` stores `of.weights_push` — the last-epoch output.
`inference_contract["step2_checkpoint"]`, which `extract_fullevent_fps.py:253` loads, is the best-epoch
file. Measured with `nd-unfolding/pet/gate_ab_push_provenance.py` (jobs `56445441`, `56445569`):

    Gate A1  rebuilt mc_indices vs stored      bit-exact, 0 differing rows of 2,000,000
    Gate A2  rebuilt truth normalization       bit-exact against the contract
    Gate B(ii) stored push == 1.0 off-shell    72/72 exact
    Gate B(i)  checkpoint vs stored push       max rel dev 8.663e-01, median 8.34e-03, p90 1.68e-01

The aggregate agrees to **1e-4** (fold-forward ratio 0.746483 vs 0.746407), which is why no coarse check
ever caught it. Batching non-associativity is excluded (2.9e-06 between batch 1000 and 512), GPU
nondeterminism is excluded (bit-identical across two jobs), and the matched floor run reproduces the
signature, so it is structural.

**Effect: `check_subsample_agreement` (`extract_fullevent_fps.py:347`, default `tol=1e-3`, called
unconditionally at `:609`) fails closed, so the full-event push stage cannot run.** That is the gate
working as designed — do **not** raise `--subsample-agreement-tol`, and do not point
`--step2-checkpoint` elsewhere: **no last-epoch checkpoint exists**, because `save_best_only=True` never
wrote one. The artifact's `weights_push` is currently unreproducible from the repo's own products.

The artifact itself is self-consistent (`central_vector` was computed in-process from the same
`weights_push`), so this does not invalidate the nominal central value — it blocks *reproducing* it and
blocks any consumer that rebuilds from the checkpoint.

**Still open, and Joseph's call** — the options are written up in
`docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md` §6: save the last-epoch
weights (recommended; no estimator change, needs a re-run), make best-epoch the estimator (redefines the
nominal, needs a gate re-issue), or extract from the best-epoch checkpoint and accept the inconsistency
(not recommended). Filed as BEN-043.

**And a trap in the fix itself:** `self.model1`/`self.model2` are assigned once in `__init__`
(`omnifold.py:123-124`) and never reassigned; training runs on the `clone_model` copies held in
`step1_models`/`step2_models` (`:278-287`, `:293`), and `clone_model` does not copy weights. **So
`of.model2` still holds its initial random initialization when `Unfold()` returns** — implementing the fix
as `of.model2.save_weights(...)` would persist an untrained network. Use `of.step2_models[0]` (and
`of.step1_models[0]`). Both files that would change are sha-pinned by the live Gate-4 code gate (keys
`driver`, `estimator_engine_multifold`), so the edit needs a gate re-issue in the same commit.

## The engine's per-iteration learning-rate anneal is dead code, so every iteration trains at full LR (found 2026-08-09)

`MultiFold.Unfold()` calls `self.CompileModels(fixed=True)` after each iteration
(`omnifold_nn/omnifold/omnifold.py:177`). `fixed=True` routes to
`get_optimizer(..., fixed=True)` -> `Adam(learning_rate=1e-5)` instead of `self.LR`, so the evident
intent is to anneal the learning rate once the first iteration has established a coarse solution.

**It has no effect, for two independent reasons.**

1. `CompileModels` compiles `self.model1` and `self.model2` — and those objects are **never trained**.
   `RunModel` trains `model_e`, which at iteration 0 is `tf.keras.models.clone_model(model)` appended to
   `step1_models`/`step2_models`, and at later iterations is that same clone retrieved from those lists.
   It only reaches the trained clones under `if self.n_ensemble > 1`, and
   `train_fullevent_nominal.py:54` sets `n_ensemble = 1`. This is the same trap as issue #26 / BEN-043:
   `self.model1` and `self.model2` are not the trained models.
2. Even where it does reach a clone, `RunModel` **unconditionally recompiles immediately before
   `fit()`**: `self.CompileModel(model_e, num_steps)` at `:292`, with `fixed` defaulting to `False`, i.e.
   the full `self.LR`. Any `fixed=True` compile is therefore overwritten before training in every
   configuration.

So in the publication configuration **every step-1 and step-2 fit runs at the full learning rate with
warm-started weights**, and no annealing occurs at any iteration.

**Why this matters right now rather than as tidy-up.** The 2026-08-09 step-1 trajectory
(`STEP1_TRAJECTORY.slurm-56525829.json`) showed the fold-forward deficit is created *by iterating*:
`push dev` goes `-0.0279 -> -0.1392 -> -0.3446`, with the signature of a collapsing high-ratio tail
(`p95` 4.6474 -> 1.4682, a 3.17x shrink; median 0.13-0.24 throughout, so the mean is a tail phenomenon).
Full-LR retraining of a warm-started classifier every round is exactly the regime in which a learned
representation is reshaped hard enough to lose that tail — so this dead anneal is a **candidate mechanism
for the degradation**, not merely a cosmetic defect. The concurrent step-1 dynamics factorial
(`56531057`) tests warm-start and split reuse but has **no learning-rate arm**; its predeclared
"no arm repairs" branch attributes the residue to "intrinsic push feedback / representation-tail
contraction", for which this would be a cheap fourth arm.

**Do not "fix" this silently.** `omnifold.py` is shared engine code on the gated path, and repairing the
anneal would change every published number. It is recorded here as a measured property of the estimator
that produced the current results.

