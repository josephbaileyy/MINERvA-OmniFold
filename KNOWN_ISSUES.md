# Known issues, bugs, and code debt — INDEX

One line per issue, pointer to the canonical home for detail. **This file is an
index, not a copy** — update the pointer target, not this file, when an issue
evolves. Add new issues here the moment they are found, so they never get
buried in run-log prose.

## Live issues

| id | severity | status | one-sentence failure | detail | updated |
|---|---|---|---|---|---|
| J | HIGH | OPEN | The 2026-07-31 four-account audit retains unresolved publication and provenance findings. | [audit detail](docs/orchestration/AUDIT-FINDINGS-20260731.md) | 2026-08-01 |
| 5 | MEDIUM | OPEN | The low-p_parallel MINOS sum-ratio gradient persists after the matching fix and is not explained by official muon-quality cuts. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-06-10 |
| 8 | HIGH | OPEN | Merged TParameters can corrupt intensive values, flags, and ratios derived from separately valid extensive totals. | [merge-semantics finding](docs/orchestration/FINDING-20260809-tparameter-merge-semantics.md) | 2026-08-09 |
| 16 | HIGH | OPEN | Bank-derived lateral covariances remain support-limited until the promoted-universe migration bound is adopted. | [open remediation gate](docs/OPEN_ITEMS.md) | 2026-07-14 |
| 19 | BLOCKER | OPEN | No quotable full-event FPS PET result exists because the Branch-C measurement-domain and inference gates remain unmet. | [cause-5 determination](docs/orchestration/DETERMINATION-20260811-cause5-binding-half.md) | 2026-08-12 |
| 20 | HIGH | OPEN | The standard-P4 chain still requires its open attestation leg even though earlier construction and purity decisions are settled. | [GBDT closeout runbook](docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md) | 2026-08-07 |
| 21 | CRITICAL | OPEN | The P4 verifier gate is advisory in practice and can be crossed without a human checkpoint. | [repair status](docs/orchestration/REPAIR4-DEFECT-STATUS-20260807.md) | 2026-08-07 |
| 23 | HIGH | OPEN | Re-running P4 evidence can misattribute old endpoint artifacts to the code and binary present now. | [verifier defect brief](docs/orchestration/followup-agent-A-standard-05.md) | 2026-08-07 |
| 24 | HIGH | OPEN | Endpoint SHA-256 binds storage identity rather than derivation identity and breaks on legitimate nondeterministic re-unfolds. | [ND run log](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-08-07 |
| J36 | HIGH | OPEN | Global POT scaling discards per-playlist Data/MC ratios and skews the MC playlist mixture at eight live sites. | [merged-extensives finding](docs/orchestration/FINDING-20260809-derived-from-merged-extensives.md) | 2026-08-09 |
| 26 | MEDIUM | OPEN | The inherited 1.17 reconstructed-E_avail scale has recorded lineage but no upstream or local justification. | [open external-input item](docs/OPEN_ITEMS.md) | 2026-08-12 |
| 28 | LOW | OPEN | The engine labels the first validation loss as the last, concealing the actual final and best epochs. | [issue detail](docs/known-issues/ISSUE-28-last-val-loss-prints-first-epoch.md) | 2026-08-07 |
| 30 | MEDIUM | OPEN | The off-gate point-cloud projection repeats the reco-efficiency double correction and must be settled before promotion. | [issue detail](docs/known-issues/ISSUE-30-pointcloud-projection-double-completeness.md) | 2026-08-06 |
| 31 | MEDIUM | OPEN | The powered-closure driver persists no normalization or architecture contract for inference-only reproduction. | [issue detail](docs/known-issues/ISSUE-31-closure-inference-contract-missing.md) | 2026-08-06 |
| 32 | HIGH | OPEN | PET covariance summaries omit the estimator configuration needed to classify their footing after the estimator changes. | [issue detail](docs/known-issues/ISSUE-32-pet-covariance-estimator-stamp-missing.md) | 2026-08-06 |
| 33 | MEDIUM | OPEN | The stored step1_class_ratio is an input target whose name invites it to be misread as an achieved measurement. | [issue detail](docs/known-issues/ISSUE-33-step1-class-ratio-is-target.md) | 2026-08-07 |
| 34 | HIGH | OPEN | Load-bearing tests and a required module remain only on purgeable scratch and disappear from fresh-clone collection. | [issue detail](docs/known-issues/ISSUE-34-tests-on-purgeable-scratch.md) | 2026-08-07 |
| 36 | HIGH | OPEN | The E_avail-W covariance has not been rebuilt after fixing its per-universe flux normalization. | [issue detail](docs/known-issues/ISSUE-36-eavailw-flux-universe-normalization.md) | 2026-08-06 |
| 38 | HIGH | OPEN | The engine's per-iteration learning-rate anneal is dead code, so warm-started fits run at full learning rate. | [issue detail](docs/known-issues/ISSUE-38-dead-learning-rate-anneal.md) | 2026-08-09 |
| 39 | HIGH | WONTFIX | Resetting the step-1 model and refreshing its split together diverges even though either intervention alone helps. | [issue detail](docs/known-issues/ISSUE-39-cold-model-fresh-split-diverges.md) | 2026-08-09 |
| 40 | MEDIUM | WONTFIX | Powered-closure reports compute recovery_criteria_met against the retired bar rather than the authoritative Gate-4 criterion. | [superseded-value index](docs/orchestration/INDEX-retracted-and-superseded-values.md) | 2026-08-10 |
| 42 | CRITICAL | OPEN | A failed scrontab listing makes wakerctl install-cron replace the table with only its managed block. | [issue detail](docs/known-issues/ISSUE-42-wakerctl-install-cron-fail-open.md) | 2026-08-11 |
| 43 | LOW | WONTFIX | cron-tick.log records crashes rather than successful ticks, so its staleness means health and its growth means failure. | [issue detail](docs/known-issues/ISSUE-43-cron-tick-log-semantics.md) | 2026-08-11 |
| 45 | MEDIUM | OPEN | The Gate-3 queue-latency receipt pins a historical wakerctl revision and has no declared current disposition. | [issue detail](docs/known-issues/ISSUE-45-wakerctl-gate3-pin-lapsed.md) | 2026-08-11 |
| 46 | MEDIUM | OPEN | The lateral-FPS matrix validator reports a PSD flag an exact-zero eigenvalue satisfies and infers the reported-bin count from the diagonal, so a rank-deficient covariance and an undercounted n_reported both pass. | [issue detail](docs/known-issues/ISSUE-46-mat-gates-records-without-gating-and-infers-a-declared-count.md) | 2026-08-14 |
| 47 | **HIGH** | **FIXED 2026-08-14** | `combine_cml_bkgsub.py` treated an incomplete `C_ML` family as a `WARN` and built from whatever it found, so `do_not_select_passing_subset` was enforced on people only. **Measured at Gate 6's live state — 1 member of `--expect 12`: exit 0, BOTH products written, and `n-1 = 0` made the covariance ENTIRELY NaN** while the two-way decomposition printed `subsample=0.000 estimator=0.000 interaction=0.000`, i.e. a NaN matrix at the publication path under a clean-reading summary. Now a hard `SystemExit`; a diagnostic needs `--allow-incomplete-family`, which writes to a `NONQUOTABLE-DIAGNOSTIC.`-prefixed path with `quotable: false`. Regression written FIRST and observed failing 5/5 at `HEAD`. | [`tests/test_cml_family_completeness_fails_closed.py`](nd-unfolding/tests/test_cml_family_completeness_fails_closed.py), `BEN-244` | 2026-08-14 |
| 48 | MEDIUM | OPEN | `verify_receipt_artifacts.py` cannot see a receipt's `.out`/`.err`/`.log` evidence or any artifact cited by bare filename, so it reads green on the `*.out` case of the trap it was written for. Two independent causes, both measured at `701b6c9`: `.out` is absent from `EXT` (`:39`, which lists `.npz/.npy/.h5/.hdf5/.root/.pkl/.parquet`), and `named_artifacts()` (`:66`) requires a path starting with `docs/orchestration/state/` while `state/gate5-cstat-spec-measurements-20260814.json`'s `evidence` keys are bare filenames — **so adding `.out` to `EXT` alone would not fix it.** A third face of the same narrowness: `scan()` (`:77`,`:83`) reads only `state/*.json`, which is why the script's own `--historical` case 2 (`849b70f^`) reports *does NOT fire* — that needle is named by a `METHOD-DECLARATION*.md`. **NOT a wrong check:** its docstring (`:19-23`) argues the narrow scope from measurement (349 of 351 named paths are cluster products, so widening fires on all of them). The defect is that its name and its hook line invite the broader inference. Now wired as pre-commit check 7 with the gap stated at the call site. Fixing it needs a scope decision by its owner, not a tuple edit. | [`docs/orchestration/verify_receipt_artifacts.py`](docs/orchestration/verify_receipt_artifacts.py), `BEN-260` | 2026-08-14 |
| 49 | HIGH | **FIXED 2026-08-14** | The `OI-120(c)` loader-purity probe computed its VERDICT from a tri-state arm flag encoded in a boolean, so an arm that **never ran** was indistinguishable from an arm that **contradicted its predeclaration** and manufactured a `LEAKAGE` verdict. `True` = matched, `False` = CONTRADICTED (the only value that may produce `LEAKAGE`), `None` = did-not-run/exclude; `:219` at `f6a52ed` assigned a `VOID` arm `False`, and the scoring filter at `:232` excludes on `is not None`. **Measured at job `56975592` (COMPLETED, exit 0): printed `LEAKAGE -- event_reco changed when only a truth array changed` while its own receipt published a fired control (`e665e960…` vs baseline `8c88e159…`) and three truth arms BIT-IDENTICAL to baseline** — the sole failing arm had `proxy_hits: 0`. Fixed to `None` at `:224`; the recorded arms now replay to `NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations`. **Fails ALARMING, not quiet** (`clean` is an `all()`, so a void arm cannot make a dirty run look clean). Regression written FIRST and observed **3 of 6 RED** at `f6a52ed`, 6/6 GREEN after, pinning both directions and replaying its arms out of the preserved stdout. **Two cosmetic residues left unpatched on purpose** (a void arm is reported with REFUSED's wording) and the probe's `P4` arm is **unfalsifiable at its capture point** — both in `OI-124`. | [`docs/orchestration/test_probe_oi120c_verdict.py`](docs/orchestration/test_probe_oi120c_verdict.py), `BEN-290`, `OI-124` | 2026-08-14 |
| 50 | MEDIUM | OPEN | **`docs/analysis-note/build_all.sh` exits 0 on a COLD tree while leaving undefined references in all three PDFs, because it runs `latexmk` once per target and the reference pass count is short by one.** A first-invocation green is therefore NOT a pass, and the failure is silent in exactly the situation a fresh checkout or a cleaned tree puts you in. Measured on a cold tree at `92b2873`: 93 undefined references in `main_note`, 6 in `main_paper`, 1 in `main_primer`, all resolving to zero on a second invocation — and the paper and primer do not include the file that commit edited, so it is the script and not any one change. **Recorded here 2026-08-15 by lane A because until now it lived only in `92b2873`'s commit body, which is not a place anyone looks before running a build; the trap it protects against is publishing a PDF full of `??`.** NOT FIXED, and deliberately so on both occasions: a pass-count edit interacts with the NERSC `texlive/2024` module path that neither lane could test, so it belongs to the note's owner. **Workaround, and it is the whole remedy: run `build_all.sh` twice and grep the per-target `.log` for `There were undefined references` before believing the exit code.** Re-checked 2026-08-15 on the `sec:negweight-footing` (B.6) builds — the tree was WARM both times, all invocations exited 0 with zero `Reference ... undefined` warnings in all three per-target logs, so those runs did not re-exercise the cold case and are not evidence against it. **Do not read the 30 `undefined` hits per log as this defect**: they are `T1/cmtt` font-shape warnings, identical in all three builds including the two that include no edited file. | `docs/analysis-note/build_all.sh`, commit `92b2873`, `BEN-350`/`BEN-351`'s episode | 2026-08-15 |

## Resolved traps that WILL bite again if forgotten

| id | severity | status | one-sentence failure | detail | updated |
|---|---|---|---|---|---|
| 6 | TRAP | WONTFIX | Never bare-hadd a _universes_full omnifile because ROOT rollover can leave a partial merge without data and background trees. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-08-12 |
| 7 | TRAP | WONTFIX | Never feed the event loop a combined MEFHC manifest because it applies the first playlist's flux to every playlist. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-08-12 |
| 9 | TRAP | RESOLVED | Never compare pre-2026-04-25 event-loop outputs to paper numbers because they use the obsolete MINOS-match stub. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-04-25 |
| 10 | TRAP | FIXED | Do not add a reco-pass completeness division after OmniFold step 2; the marginal self-validation gate must catch this double correction. | [ND run log](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-06-09 |
| 11 | TRAP | FIXED | Do not use the stale mostly-empty PET ExtraEnergyClusters branches; the point-cloud chain uses CVUniverse::GetRecoClusters(). | [validation ledger](VALIDATION_LEDGER.md) | 2026-06-10 |
| 17 | TRAP | WONTFIX | Never extract PET cross sections in the TensorFlow-module Python because it lacks PyROOT. | [replica launcher](nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh) | 2026-08-12 |
| 25 | TRAP | FIXED | Report writers must capture helper output instead of letting print-only results vanish from committed artifacts. | [model comparison receipt](2d-unfolding/receipt_model_chi2_2d.json) | 2026-08-11 |
| 27 | TRAP | FIXED | Resume guards must validate artifact completeness and integrity rather than existence alone. | [audit detail](docs/orchestration/AUDIT-FINDINGS-20260731.md) | 2026-08-01 |
| 29 | TRAP | FIXED | Cross-section extraction over all truth-pass rows must not divide again by reconstructed acceptance. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-06 |
| 35 | TRAP | FIXED | A fail-closed production guard may correctly reject a stale synthetic fixture rather than being over-strict. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-06 |
| 37 | TRAP | FIXED | Persist final-epoch checkpoints and round-trip them against stored push weights before permitting downstream extraction. | [BEN-043 resolution](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-08-08 |
| 41 | TRAP | RETRACTED | Do not quote one-shot results from the unstable diagnostic wrapper family as estimator properties. | [retracted-value index](docs/orchestration/INDEX-retracted-and-superseded-values.md) | 2026-08-11 |
| 44 | TRAP | FIXED | Per-watch failures must be isolated and surfaced through watch_errors without making whole-scan failures look healthy. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-11 |

## `p4_validate_active_lateral_fps.py` — two gates that cannot fail on a rank-deficient covariance

Found 2026-08-14 by lane C while writing the `C_stat` spec; **both lines read directly, not relayed.**
Not repaired here — it is another lane's validator path and no current artifact is mis-certified by it —
but recorded because a future reader will otherwise take its output as evidence it cannot supply.

```
:69   r["min_over_max_eig"] = float(ev[0] / max(1e-300, abs(ev[-1])))
:70   r["psd"]              = bool(ev[0] >= -1e-12 * abs(ev[-1]))
:72   r["n_reported"]       = int(np.sum(d > 0))
```

1. **`:70` is a negativity test, not a rank test.** An exact zero eigenvalue satisfies it, so a
   **rank-49** matrix passes `psd=True` silently. Gate-5's `C_stat` is rank ≤ 49 against 266 cells by
   construction (predeclared, `OI-91`), so this gate will pass it and say nothing. **The measurement needed
   to catch it is already recorded one line above** — `min_over_max_eig` at `:69` — so what is missing is a
   rank threshold, not data.
2. **`:72` infers the reported-bin count from the diagonal, and that is not the same quantity.** A cell can
   be **reported** (`comp > 0`) and still carry exactly zero replica variance, if every draw lands on the
   same value — plausible in a low-occupancy catch bin, and the extended-FPS grid has catch bins precisely
   where occupancy is thinnest. Its diagonal is `0.0` and the count silently **undercounts**. On Gate-5's
   `C_stat` it is wrong by construction: the adopted 266-cell common mask deliberately contains **four
   identically-zero cells** (PET truth mass, zero reco acceptance), so `sum(d > 0)` reads **262** where
   `n_reported` is **266**.

**Guarded on the C_stat side rather than fixed here:** `CSTAT-D0e` requires `n_reported` to be declared
from `reported_mask.sum()` and forbids deriving it from `diag(C)`, and requires a zero on the reduced
diagonal to be **reported by index rather than dropped** — dropping one would silently change the published
dimension. See `SPEC-20260814-gate5-cstat-construction-v1.md` §3.1.
