# Lane A verification record — 2D estimator pairing

Preparation evidence for `docs/orchestration/ASSESSMENT-20261008-2d-estimator-pairing.md`. It grants
no compute and changes no gate, band, adoption or publication scope.

- **Base:** `f8e2bf8535a90d7ed1315530cff3b80860ef9f9c`. Branch `prep/uncertainty-a-pairing-20261008`,
  worktree `MINERvA-OmniFold-uncprep-a-20261008` (created 2026-10-09T06:09Z; 44 GiB free before).
- **Commits:** `acb338a2` (`[uncprep-A] CONTRACT`), `971fc00c` (driver provenance records, behavior
  fix), then the FREEZE commit that adds this file.
- **Local environment:** macOS Darwin 25.6.0. `python3` 3.12.2 (conda; numpy 1.26.4, uproot 5.6.2,
  pytest 8.3.4) for the independent checks and the `nd-unfolding` tests. `python3.13` 3.13.7
  (Homebrew; ROOT 6.36.000, numpy 2.4.4) with `PYTHONPATH=$(root-config --libdir)` for the PyROOT
  test. `TMPDIR=/private/tmp/minerva-uncprep-a-20261008/tmp`; `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=4`.
- **Logs:** every log cited here is copied under `logs/` next to this file.
- **Remote reads:** `ssh saul.nersc.gov`, read-only. Directory listings, `sha256sum`, `grep` of
  existing logs, `sacct` of finished jobs, and a byte copy of ~505 small products (33 MB, ≤55 KB each,
  plus covariance files). No allocation, job, training or login-node analysis was run. The
  multiplexed connection (pinned to login05) hung at ~06:25Z, so later reads used
  `-o ControlPath=none` (login12).

## 1. Checks, commands and exit codes

Every test file was read before it ran. None trains a model, reads real validation samples or
submits a job. The PyROOT test stubs the OmniFold classifier and builds a synthetic 6,000-event
input. The others are AST scans, synthetic fixtures, or local subprocess shims.

| # | Check | Command (from the worktree root unless noted) | Exit | Result |
|---|---|---|---|---|
| 1 | KI-84 regression, base | `PYTHONPATH=$(root-config --libdir) python3.13 -m unittest 2d-unfolding/tests/test_bootstrap_completeness_ki84.py -v` | 0 | 8/8 pass, 0 skipped |
| 2 | KI-84 negative control (pre-fix driver `4e7c20bb`, sha256 `8ebe0277…`) | scratch tree `$TMPDIR/negctl/2d-unfolding/{unfold_2d_omnifold_unbinned.py = git show 4e7c20bb:…, tests/<current test>}`, same command from `$TMPDIR/negctl` | 1 | **2 FAIL as expected**: `test_bootstrapped_replica_has_unit_completeness_in_every_bin` (`boot7: max \|c-1\| = 2.48 over 198 bins`) and `test_bootstrapped_completeness_is_bitwise_the_central_value`; 2 pass (fixture premise, MC still resampled); `PathsTheFixMustNotChange` **skipped by design** (the scratch tree has no git, so it cannot fetch the pre-fix blob; that class compares post-fix with pre-fix and ran in #1) |
| 3 | KI-84 regression + provenance tests, after `971fc00c` | as #1 | 0 | 14/14 pass, 0 skipped |
| 4 | Provenance mutation (write loop replaced by `for name, value in []:`) | scratch tree `$TMPDIR/mutctl`, `-m unittest 2d-unfolding.tests.test_bootstrap_completeness_ki84.RunProvenanceIsRecorded` | 1 | 5 of 6 new tests fail; the sixth (histograms unchanged) passes, as it should |
| 5 | `OI-136` rooted-insert ratchet, base | `python3 -m unittest nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py -v` | 1 | **RED at the base**: 9/10 pass. `test_no_file_outside_the_named_set_feeds_a_rooted_insert` lists 9 new sites (For E, item 1). The 2D-arm tests pass: `omnifold.py` digest `e96234124a31…` held, insert inside a function |
| 6 | `OI-136` fail-open inventory ratchet, base | `python3 -m unittest nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py -v` | 1 | **RED at the base**: 6/7. Recorded 9 files / `0939e159…`, measured 18 / `04357e1a…` |
| 7 | #5 and #6 after `971fc00c` | same | 1, 1 | failure lists byte-identical to the base runs (`diff` empty) |
| 8 | k=0 separated roots (2D dormancy arm) | `python3 -m unittest nd-unfolding/tests/test_k0_5ab_separated_roots.py -v` | 0 | 4/4, base and after |
| 9 | flux-universe fix suite (reads the driver's `PT_EDGES`) | `python3 -m unittest nd-unfolding/tests/test_flux_universe_fix.py -v` | 0 | 51/51, base and after |
| 10 | P4 resume closure (the driver is in its producing set) | `python3 -m unittest nd-unfolding/tests/test_p4_resume_integration.py -v` | 0 | 50/50 after |
| 11 | hash bindings | `python3 -m pytest -q nd-unfolding/tests/test_hash_bindings.py -p no:cacheprovider`; `python3 docs/orchestration/verify_hash_bindings.py --root .` | 0, 0 | 33 passed; `ALL BINDINGS INTACT` (the driver's two `8ebe0277` pins were already `KNOWN_PREEXISTING` since `bb4b0b6f`) |
| 12 | full-event extractor (stubs the driver module) | `python3 -m unittest nd-unfolding/tests/test_fullevent_extract.py -v` | 0 | 28/28 after |
| 13 | pre-commit hook | on each commit | 0 | `13 checks passed` (both commits) |
| 14 | independent recomputation | `python3 -I $TMPDIR/check_a.py $TMPDIR/ops 2d-unfolding/minerva_paper_anc` (script in §6) | 0 | §3; wall 1.7 s, peak RSS 74 MB |

`unittest` with `test_hash_bindings.py` collects 0 tests (`NO TESTS RAN`, exit 5) because the file is
written for pytest. That run is **not** counted; #11 is the real run.

## 2. Product digests (byte copies under `$TMPDIR/ops`, sha256)

All match the committed receipts (`state/ki84-adopt-20261006/recompute_2d_budget.json`, ledger
`VL170`/`VL172`, `2D_OMNIFOLD_REFERENCE.md` for the central product).

| product | sha256 |
|---|---|
| `2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` (`E_C`) | `142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5` |
| `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` (CV42) | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` |
| `uq/seedscan_lgbm_ml/uq_covariance_ml.root` | `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9` |
| `uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root` (VL170) | `71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115` |
| `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root` (VL162, read only) | `f7c734b1127e2cf75ccf2cc4241062b5dced2d55fcec785fa0d42ec861c10270` |
| `uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root` | `077912e3e7a53376c6df89ee1af4a2a504fe1f49423bab88780204beccd952f5` |
| `minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` |
| `seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed{1..10}.root`, concatenated in shell-glob order (seed 1, 10, 2, …, 9) | `84942b09009b58695a07d55f45112da6e39817c241c952acace31810a8e6d6c0` |
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py`, **today** | `e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a` (= the ratchet constant; last commit `541dd48c`, 2026-07-20; clean) |

`uq/universe_sweep_fluxfix/` holds 100 regular files (the rescaled Flux universes, `hXSec2D` only),
87 symlinks to the unscaled `uq/` universes, and a symlink to CV42. It was copied with `tar h`.

## 3. Independent recomputation (own code, uproot, no repository analyzer imported)

| quantity | recomputed | stored / quoted |
|---|---|---|
| edges of `E_C`, CV42 vs the paper binning | identical | — |
| masks: `E_C>0`, CV42`>0`, VL170 replica mean`>0`, ML-scan mean`>0`, paper `StatOnly` diag`>0` | all identical, 205 bins | 205 |
| paper CSV `xs>0` set vs `StatOnly` diag`>0` vs ROOT `StatOnly` | identical | — |
| VL170 replicas present | seeds 1–300 exactly | 300 |
| max \|c−1\| over truth-denominator bins: 300 replicas / `E_C` | 1.58e-14 / 1.58e-14 | 1.6e-14 |
| `C_S` (np.cov ddof 1 over 300) vs stored | max \|Δ\|/max 4.0e-16; √tr 1.9312e-40 | 1.931e-40 |
| `C_ML` (np.cov ddof 1 over 10) vs stored | 3.3e-16; √tr 5.0605e-41 | 5.061e-41 |
| `C_U` (44 bands, 187 universes, MAT 1/N, + 0.014·x_CV42 rank-1) vs `hCov_universe_total` | max \|Δ\|/max **0.0** | — |
| `hCov_combined − hCov_universe_total − C_S` | 7.2e-14 of max `C_S` | — |
| sweep-dir CV vs `uq/` CV42 `hXSec2D` | identical | — |
| block-sum median relative σ, x = CV42 / x = `E_C` | 6.8707 % / 6.8269 % | 6.87 % |
| `C_S` median σ/x: replica mean / CV42 / `E_C` | 0.6739 % / 0.6738 % / 0.6848 % | 0.674 % |
| paper-only χ²/ndf (paper TH2D) | 3.6609 | 3.661 |
| combined χ²/ndf, log-normal, pull mean/RMS | 1.4716, 1.4548, 0.0514 / 0.4055 | 1.472, 1.455, 0.051 / 0.405 |
| Fig. 6/7 medians, p∥ / p_T: Statistical, Total, ML | 0.2527 / 0.2491 %, 5.9000 / 6.2203 %, 0.0441 / 0.0421 % | 0.253 / 0.249, 5.900 / 6.220, 0.044 / 0.042 |
| total cross section `E_C` / CV42 | 3.07331e-38 / 3.07302e-38 | 3.073e-38 |
| deterministic inputs `E_C` vs CV42 (`hDataReco2D`, `hBkgReco2D`, `hTruth2D`, `hEffDen`, `hOFTruthDenom2D`, `hOFInputTruth2D`, `hFlux_pt`, POT, nucleons, flux integral, iterations) | all bitwise identical | — |
| replica 1 vs `E_C` (`hBkgReco2D`, `hOFTruthDenom2D`, `hOFInputTruth2D`, `hFlux_pt`) | bitwise identical | — |
| `hBkgReco2D` in the 87 non-Flux universes vs CV42 | bitwise identical in 87/87 (background frozen at CV) | — |
| `fluxSource` string, `E_C`, CV42, seedscan | `…/runEventLoopMC_MEHFC.root` (pre-`c7ae2206` name); VL170 replicas: `…_MEFHC.root`; `hFlux_pt` identical | — |

Central-value comparisons (205 bins; σ_S = √diag `C_S`; σ_ML = √diag `C_ML`):

| comparison | \|Δ\|/x median / p84 / max | \|Δ\|/σ_S median / p84 / max | bins > 1σ_S / > 2σ_S | total ratio |
|---|---|---|---|---|
| lgbm seed 1 (CV omnifile) vs `E_C` | 0.97 / 2.67 / 12.50 % | 1.30 / 2.76 / 8.32 | 126 / 62 | 0.99990 |
| lgbm 10-seed mean vs `E_C` | 0.99 / 2.74 / 12.20 % | 1.33 / 2.81 / 8.35 | 130 / 62 | 0.99990 |
| CV42 vs `E_C` | 0.98 / 2.85 / 12.18 % | 1.32 / 2.70 / 8.38 | 132 / 66 | 0.99991 |
| CV42 vs lgbm seed 1 | 0.18 / 0.51 / 1.79 % | 0.30 / 0.53 / 1.28 | 3 / 0 | 1.00001 |
| VL170 replica mean vs lgbm seed 1 | 0.14 / 0.48 / 3.37 % | 0.23 / 0.52 / 1.36 | 3 / 0 | 1.00010 |
| VL170 replica mean vs `E_C` | 0.93 / 2.65 / 12.60 % | 1.34 / 2.78 / 8.48 | 131 / 60 | 1.00000 |

\|`E_C` − lgbm seed mean\|/σ_ML: median 5.15, p84 11.95, max 31.3. \|CV42 − lgbm seed mean\|/σ_ML:
median 0.83, p84 1.78, max 4.46. σ_ML/σ_S: median 0.26, p84 0.42, max 0.73. These are descriptive
measurements. None is a covariance-transfer test.

## 4. Remote evidence for executed bytes

| read | result |
|---|---|
| `sacct -j 53116554,53034070 -X …` | `53116554 unfold_MEHFC regular_1 COMPLETED 2026-05-18T12:57:08 → 2026-05-19T08:15:51, ElapsedRaw 69523, 256 CPUs, 487802M`; `53034070 unfold_MEHFC_p18` (the Phase-18.1 predecessor) 69627 s |
| `sacct -j 53116554 --format=JobID,MaxRSS,AveRSS,TotalCPU,ElapsedRaw` | batch step MaxRSS **16,786,760 K**, TotalCPU **19:18:00** over 69,523 s elapsed, so one core was busy throughout (sklearn exact is single-threaded; the LightGBM and HistGBT backends are OpenMP) |
| `git show d1bc8813:2d-unfolding/unfold_2d_omnifold_unbinned.py` | no `estimator`, `random_state` or `--seed` anywhere: one backend (sklearn `GradientBoosting`), unseeded. `d1bc8813` was committed 2026-05-18 10:56 -0700; the backend option arrived in `baa0a76f` on 2026-05-19 |
| `git show d1bc8813:2d-unfolding/sbatch_unfold_2d_MEHFC.sh` | `--omnifile runEventLoopOmniFold_MEHFC.root --mcfile baseline_flux/runEventLoopMC_MEHFC.root --iters 5 --use-weights --out 2d_crossSection_omnifold_MEHFC_5iter.root`. Renamed to `MEFHC` on 2026-05-28 (`c7ae2206`); the product keeps its 2026-05-19 08:15 mtime |
| job log of `53116554` | **not found** (`find … -name "unfold_MEFHC_53116554*"` over `2d-unfolding/` and `MINERvA101/archive_pre_migration_*`, depth 3) |
| VL170 pilot log `ki84-rebuild-20261006/logs/boot_1_59409026.out` | `code=…/MINERvA-OmniFold-ki84-20261006 head=bb4b0b6fbb8a…`, `bkg-mode=purity`, `Poisson bootstrap: seed=1, streams=both`, `Pinned GBDT seeds: step1=1, step2=2, regressor=3`, `GBDT estimator: lgbm (device=cpu)`, `Phase-17 MC bootstrap: completeness uses the un-resampled MC truth weights`, `global completeness c = 1.0000` |
| VL170 array logs `boot_1_59410433.out`, `boot_300_59410433.out` | same lines; `seed=1` / `seed=300` |
| all 300 array logs | **not completed.** Four attempts to `grep` the 300 logs in one pass (06:25–06:55Z; mux and direct connections, per-file and single-pass, remote `timeout`) exceeded the session's 120 s window or returned no output, while single-file reads succeeded. Diagnosed as slow reads of that directory, not missing files; stopped under the retry rule. Coverage of replicas 2–299 therefore rests on the launcher's HEAD/clean-tree guard (exit 3 on mismatch) and on sacct's 303 COMPLETED tasks, not on their logs |
| universe sweep / matched CV logs | only July logs (`5567xxxx`, negweight and puritynew variants) are in `2d-unfolding/`; the May sweep's are absent |
| seedscan_lgbm logs | none in `seedscan_lgbm/` |

Runtime origin of the OmniFold helper for `E_S`: the driver at `bb4b0b6f` inserts
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python` at `sys.path[0]` inside `main()`,
so the helper came from the canonical checkout rather than the frozen code checkout the launcher
verified. That file's last commit is `541dd48c` (2026-07-20), and today its digest equals the
ratchet's pinned constant. Its bytes on 2026-10-06 were not recorded, so this stays **unavailable**,
not inferred. The analyzers in `rollup_vl170_adoption.sh` also ran from the canonical checkout, and
their digests are not in the adoption receipts. §3 reproduces their outputs from their inputs, which
verifies the computation but not the origin.

## For E

1. **Both `OI-136` ratchets are red at the base** (#5, #6). Nine `.py` files added in October feed
   the canonical root into `sys.path[0]`, and none is on the named list:
   `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`, `…/ki85_compare.py`,
   `state/ki84-adopt-20261006/{purity_datastream_check,recompute_2d_budget}.py`,
   `state/ki84-rebuild-20261006/{boot_spreads_vl170,compare_ki84_band,predict_ki84}.py`,
   `state/note-boot-20261003/boot_spreads.py`, `state/uqpaper-median-20261006/paper_median.py`.
   The hook does not run these tests. The nine arrived between 2026-10-03 (`649e3bd2`) and 2026-10-06 (`62115adc`, `8a50498a`), and all nine are unlisted at the pin. None is an A
   path. Seven are receipts, which are records and must not be edited. The two producers are live.
   `fixed_truth_toy.py` (line 158, the OmniFold helper) is the coverage toy producer a successor
   design would reuse. Its helper origin is therefore not set by the launching tree (assessment §2.4, item 1).
   Owner: the `OI-136` route (repair or classification under that authorization's process), not
   this lane.
2. **STATUS backend label.** `2D_OMNIFOLD_STUDY_STATUS.md` headline "MEFHC 5-iter lgbm" is wrong for
   the central product; its "Phase 18.2 pipeline … exact GBT" is right (`P01`). The Stage-2 table
   rows are LightGBM and correctly so. STATUS is E's surface.
3. **Budget denominator.** The printed 6.87 % divides by the LightGBM seed-42 CV. Divided by the
   quoted central value, the same covariance gives 6.83 % (`P14`). Fig. 6/7 divides by `E_C` (`P15`).
   No number is wrong as computed. The quoted pair mixes two denominators, so any record that
   describes the budget as "relative to the central value" needs the qualifier.
4. **Ordinal alignment proposal (not implemented).** The five masks agree for today's bytes (`P12`).
   But `compare_to_paper_fullcov.py` (not an A path) and `analyze_universes.py --bootstrap-cov`
   align covariances by ordinal position after a count/shape check only. A guard in
   `analyze_universes.py` alone would cover one of three consumers. Proposed design: every
   covariance writer stores its reported mask (for example a `hReportedMask2D`), and every consumer
   refuses on membership mismatch. One owner should land it across the writers and consumers.
5. **No `## For E` ownership conflict.** D's inventory (`d126a115`) claims none of A's five
   conditional paths. A used two of them (the driver and the KI-84 test) and handed no file to D.

## 5. D's reference corrections — factual check (D stays the writer)

Checked against D's commits `00803510` and `abc1e6f7` on `origin/prep/uncertainty-d-navigation-20261008`.

- **Bootstrap item 4 (`00803510`): CORRECT** in every factual clause. The scaleup, legacy 1–50,
  negweight and bootsplit launchers, `uq/run_bootstrap_interactive.sh` and the VL170 record all pass
  `--seed 1`. The scaleup header names Slurm `53327775` as the seed-varying predecessor. CV42 uses
  `--seed 42`. The central launcher passes neither `--seed` nor `--estimator`. Both coverage-toy
  launchers pass `--seed "${SEED}"`. One qualification: "separable … only under that condition"
  reads correctly as a necessary condition. Separability itself (`C_S` and `C_ML` uncorrelated) has
  not been measured, so the item should not be read as sufficient.
- **Import constraint (`abc1e6f7`): CORRECT, two precision notes.** `AUTHORIZATION-20260903-oi136-failopen-repair.md:41`
  carries Joseph's ruling: insert inside `main()`, sha pinned, advancing needs a Gate-2 re-run. The
  `omnifold.py`-digest condition is stated as the decision's premise in
  `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py:266-274`, not in the ruling text. Cite both.
  The reference also says the ratchet "fails if either condition breaks". That is true of those two
  tests, but the suite is red at the base for an unrelated reason ("For E", item 1), so a reader running it will
  see red before touching the driver.
- **"Which script produced the quoted 2D uncertainty" table (`abc1e6f7`): CORRECT** (statistical,
  systematic, ML and combined rows all verified in §3–§4). Two additions are factual and would
  prevent a misreading. (a) The VL170 record's "frozen code checkout" supplies the driver, but the
  OmniFold helper comes from the canonical checkout through the rooted insert (§4). (b) The 87
  symlinked universes in `uq/universe_sweep_fluxfix/` have background frozen at CV (§3), because the
  May sweep predates the `KNOWN_ISSUES #13` wiring (`cf8a4a67`, 2026-07-11).
- **D's "For A" item 1, the `VL162` half.** The scaleup launcher passes `--seed 1`, and there is
  content evidence too. The VL170 pilot, rerun with `--estimator lgbm --seed 1 --bootstrap-seed 1`,
  reproduces VL162 replica 1's `hUnfold2D` to 3.2e-12 relative
  (`state/ki84-rebuild-20261006/compare_pilot_seed1.json`), while LightGBM seeds differ from one
  another by a median 0.17 %. So VL162 replica 1 ran at seed 1. The other 299 rest on the launcher text.
- **D's "For A" item 2.** `rollup_vl170_adoption.sh` is the active VL172 route: its products' digests
  are those in the adoption receipts, and §3 reproduces them. The ML covariance's content equals
  `analyze_uq.py`'s definition over `seedscan_lgbm/…seed{1..10}.root` (3.3e-16), which is step (a) of
  `final_rollup_full.sh`. The executed-bytes log of that step is not on disk.
- **Caution on D's ML row, `3848b1ce` (factual, for D to word).** The paragraph's guard statement is
  accurate for the rows it names (the replica record and universe launchers skip complete outputs;
  the rollup refuses existing directories). The ML row has **no** guard, and "step (a) of
  `uq/final_rollup_full.sh`" cannot be run alone: the script runs (a)–(d). Step (a) overwrites the
  pinned `uq/seedscan_lgbm_ml/uq_covariance_ml.root` (`3b6b48ec…`). Step (b) overwrites the
  sha-pinned VL162 file `uq/bootstrap_MEFHC_300/uq_covariance_boot300.root` (`f7c734b1…`). Step (c)
  archives and regenerates `uq/universe_stage2_MEFHC_full/`. A ROOT rewrite changes the bytes even
  when the content is unchanged. To reproduce the ML covariance alone, write to a new directory:
  `python uq/analyze_uq.py --glob 'seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root' --outdir <new> --out-root uq_covariance_ml.root`.
- **D06 (central backend label): answer `exact`.** sklearn `GradientBoosting`, unpinned seed, with
  the evidence class in `pairings.tsv` `P01`.

## 6. Independent check script (verbatim as run; its two JSON outputs are stored verbatim as `logs/check_a_output.txt` and `logs/check_a_extra_output.txt`, `.txt` so the receipt scanner does not read a log as a receipt)

```python
#!/usr/bin/env python3
"""Lane A independent checks on the existing 2D products (read-only, no training).

Independent implementation: reads ROOT files with uproot (no PyROOT) and does not import the
repository analyzers. Inputs are the byte-copied products under OPS (sha256 recorded in
P/a/verification.md). Prints a JSON summary.

    python3 -I check_a.py OPS_DIR PAPER_ANC_TXT_DIR > check_a.json
"""
import glob
import json
import os
import re
import sys

import numpy as np
import uproot

OPS, ANC = sys.argv[1], sys.argv[2]
D = os.path.join(OPS, "MINERvA-OmniFold/2d-unfolding")
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
DA = np.diff(PT)[:, None] * np.diff(PZ)[None, :]


def h2(path, name="hXSec2D"):
    h = uproot.open(path)[name]
    v = h.values(flow=False)
    ex, ey = h.axis(0).edges(), h.axis(1).edges()
    return v, ex, ey


def sq(path, name):
    return uproot.open(path)[name].values(flow=False)


def q(a):
    a = np.asarray(a, float)
    return {"median": float(np.median(a)), "p16": float(np.percentile(a, 16)),
            "p84": float(np.percentile(a, 84)), "max": float(np.max(a)), "min": float(np.min(a))}


out = {}
central_p = os.path.join(D, "2d_crossSection_omnifold_MEFHC_5iter.root")
cv42_p = os.path.join(D, "uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")
xc, ex, ey = h2(central_p)
x42, ex2, ey2 = h2(cv42_p)
out["edges_match_paper_binning"] = bool(np.allclose(ex, PT) and np.allclose(ey, PZ)
                                        and np.allclose(ex2, PT) and np.allclose(ey2, PZ))
out["shape"] = list(xc.shape)
out["central_total_xsec_cm2_per_nucleon"] = float((xc * DA).sum())
out["cv42_total_xsec_cm2_per_nucleon"] = float((x42 * DA).sum())

# --- paper reported set and global order: gid = (Ptbin-1)*16 + (P||bin-1)
paper = np.zeros(224)
for line in open(os.path.join(ANC, "data_result_ptpl_2D_minerva_inclusive_6GeV.txt")).read().split("\n")[1:]:
    if not line.strip():
        continue
    pzb, ptb, xs = line.split(",")[:3]
    paper[(int(ptb) - 1) * 16 + (int(pzb) - 1)] = float(xs)
stat_diag = np.zeros(224)
for line in open(os.path.join(ANC, "cov_ptpl_minerva_inclusive_6GeV_stat.txt")).read().split("\n")[1:]:
    if not line.strip():
        continue
    i, j, c = line.split(",")
    if i == j:
        stat_diag[int(i)] = float(c)
m_paper_xs = paper > 0
m_paper_stat = stat_diag > 0
out["paper_set_xs_gt0_equals_statdiag_gt0"] = bool((m_paper_xs == m_paper_stat).all())
out["n_paper_reported"] = int(m_paper_stat.sum())

# Paper ROOT: TotalCovariance; confirm the TH2D axis convention and that the text total matches ROOT
pr = uproot.open(os.path.join(D, "minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"))
ptot = np.array(pr["TotalCovariance"].member("fElements")).reshape(224, 224)
pstat = np.array(pr["StatOnlyCovariance"].member("fElements")).reshape(224, 224)
ph = pr["pt_pl_cross_section"]
pv = ph.values(flow=False)
out["paper_th2d_shape"] = list(pv.shape)
pv_flat = np.zeros(224)
if pv.shape == (14, 16):
    for a in range(14):
        for b in range(16):
            pv_flat[a * 16 + b] = pv[a, b]
else:
    for a in range(16):
        for b in range(14):
            pv_flat[b * 16 + a] = pv[a, b]
out["paper_root_th2d_vs_csv_max_rel"] = float(np.max(np.abs(pv_flat[m_paper_xs] - paper[m_paper_xs]) / paper[m_paper_xs]))
out["paper_root_statdiag_set_equals_csv_set"] = bool(((np.diag(pstat) > 0) == m_paper_xs).all())


def mask_rowmajor(x2):
    return (x2 > 0).ravel(order="C")


masks = {"central_exact_gt0": mask_rowmajor(xc), "cv42_lgbm_gt0": mask_rowmajor(x42)}

# --- bootstrap VL170: 300 rebuilt replicas
reps = sorted(glob.glob(os.path.join(OPS, "ki84-rebuild-20261006/replicas/2d_xsec_MEFHC_5iter_lgbm_boot*.root")))
R = np.stack([h2(p)[0] for p in reps])
out["n_vl170_replicas"] = len(reps)
seeds = sorted(int(re.search(r"boot(\d+)\.root$", p).group(1)) for p in reps)
out["vl170_replica_seed_set_is_1_to_300"] = seeds == list(range(1, 301))
rmean = R.mean(0)
masks["vl170_replica_mean_gt0"] = mask_rowmajor(rmean)
# completeness of each replica
cmax = 0.0
for p in reps:
    c = sq(p, "hOFCompleteness2D")
    t = sq(p, "hOFTruthDenom2D")
    sel = t > 0
    cmax = max(cmax, float(np.max(np.abs(c[sel] - 1.0))))
out["vl170_replica_max_abs_c_minus_1_over_truthdenom_bins"] = cmax
cc = sq(central_p, "hOFCompleteness2D")
tc = sq(central_p, "hOFTruthDenom2D")
out["central_max_abs_c_minus_1"] = float(np.max(np.abs(cc[tc > 0] - 1.0)))

# --- seedscan lgbm (ML block)
ss = sorted(glob.glob(os.path.join(D, "seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root")),
            key=lambda p: int(re.search(r"seed(\d+)\.root$", p).group(1)))
S = np.stack([h2(p)[0] for p in ss])
masks["seedscan_mean_gt0"] = mask_rowmajor(S.mean(0))
masks["paper_statdiag_gt0"] = m_paper_stat
ref = masks["paper_statdiag_gt0"]
out["mask_equal_to_paper_set"] = {k: bool((v == ref).all()) for k, v in masks.items()}
out["mask_counts"] = {k: int(v.sum()) for k, v in masks.items()}
M = ref
n = int(M.sum())

# --- recompute the bootstrap covariance and compare with the stored VL170 product
Rr = R.reshape(len(reps), -1, order="C")[:, M]
Cb = np.cov(Rr, rowvar=False, ddof=1)
Cb_stored = sq(os.path.join(D, "uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root"), "hCov2D_reported")
out["boot_vl170_recomputed_vs_stored_max_abs_over_max"] = float(np.max(np.abs(Cb - Cb_stored)) / np.max(np.abs(Cb_stored)))
out["boot_vl170_sqrt_trace"] = float(np.sqrt(np.trace(Cb)))

# --- recompute ML covariance
Sr = S.reshape(len(ss), -1, order="C")[:, M]
Cml = np.cov(Sr, rowvar=False, ddof=1)
Cml_stored = sq(os.path.join(D, "uq/seedscan_lgbm_ml/uq_covariance_ml.root"), "hCov2D_reported")
out["ml_recomputed_vs_stored_max_abs_over_max"] = float(np.max(np.abs(Cml - Cml_stored)) / np.max(np.abs(Cml_stored)))
out["ml_sqrt_trace"] = float(np.sqrt(np.trace(Cml)))

# --- recompute the universe covariance (MAT mean-centred 1/N per band, + 1.4% norm rank-1 on CV)
uni = {}
pat = re.compile(r"_uni_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")
skipped = []
for p in sorted(glob.glob(os.path.join(D, "uq/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_*.root"))):
    mm = pat.search(os.path.basename(p))
    if not mm:
        skipped.append(os.path.basename(p))
        continue
    uni.setdefault(mm.group("band"), []).append((int(mm.group("idx")), h2(p)[0]))
out["universe_files_skipped_by_pattern"] = skipped
out["universe_n_bands"] = len(uni)
out["universe_n_universes"] = sum(len(v) for v in uni.values())
x42r = x42.ravel(order="C")[M]
Cu = np.zeros((n, n))
for band, lst in uni.items():
    Dm = np.stack([(a - x42).ravel(order="C")[M] for _, a in sorted(lst, key=lambda t: t[0])])
    Z = Dm - Dm.mean(0, keepdims=True)
    Cu += Z.T @ Z / Dm.shape[0]
Cu += np.outer(0.014 * x42r, 0.014 * x42r)
U = os.path.join(D, "uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root")
Cu_stored = sq(U, "hCov_universe_total")
Ccomb_stored = sq(U, "hCov_combined")
out["universe_recomputed_vs_stored_max_abs_over_max"] = float(np.max(np.abs(Cu - Cu_stored)) / np.max(np.abs(Cu_stored)))
out["combined_minus_universe_minus_boot_max_abs_over_max_boot"] = float(
    np.max(np.abs(Ccomb_stored - Cu_stored - Cb_stored)) / np.max(np.abs(Cb_stored)))
sweep_cv = os.path.join(D, "uq/universe_sweep_fluxfix/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root")
if os.path.exists(sweep_cv):
    out["sweep_dir_cv_equals_uq_cv_hXSec2D"] = bool(np.array_equal(h2(sweep_cv)[0], x42))

# --- budget (block sum) with the two candidate denominators
Ctot = Cu_stored + Cb_stored + Cml_stored
xcr = xc.ravel(order="C")[M]
out["block_sum_median_rel_pct_denominator_cv42"] = float(100 * np.median(np.sqrt(np.diag(Ctot)) / x42r))
out["block_sum_median_rel_pct_denominator_exact_central"] = float(100 * np.median(np.sqrt(np.diag(Ctot)) / xcr))
out["boot_median_rel_pct_den_cv42"] = float(100 * np.median(np.sqrt(np.diag(Cb_stored)) / x42r))
out["boot_median_rel_pct_den_exact_central"] = float(100 * np.median(np.sqrt(np.diag(Cb_stored)) / xcr))
out["boot_median_rel_pct_den_replica_mean"] = float(100 * np.median(np.sqrt(np.diag(Cb)) / rmean.ravel(order="C")[M]))

# --- combined chi2 vs paper (pinv on the 205 block), central exact
P = paper[M]
d = xcr - P
Ct = ptot[np.ix_(M, M)] + Ccomb_stored + Cml_stored
chi2 = float(d @ np.linalg.pinv(Ct) @ d)
out["combined_chi2_per_ndf_recomputed"] = chi2 / n
chi2p = float(d @ np.linalg.pinv(ptot[np.ix_(M, M)]) @ d)
out["paper_cov_chi2_per_ndf_recomputed"] = chi2p / n

# --- central-value comparisons (descriptive; no transfer claim)
sb = np.sqrt(np.diag(Cb_stored))
sml = np.sqrt(np.diag(Cml_stored))
seed1 = S[0].ravel(order="C")[M]
smean = S.mean(0).ravel(order="C")[M]
rm = rmean.ravel(order="C")[M]


def cmp(a, b, label):
    r = np.abs(a - b) / b
    z = (a - b) / sb
    return {"label": label, "abs_rel_diff_pct": {k: 100 * v for k, v in q(r).items()},
            "signed_diff_over_sigma_boot": q(z), "abs_diff_over_sigma_boot": q(np.abs(z)),
            "n_bins_abs_diff_gt_1_sigma_boot": int((np.abs(z) > 1).sum()),
            "n_bins_abs_diff_gt_2_sigma_boot": int((np.abs(z) > 2).sum()),
            "total_ratio": float((a * DA.ravel(order="C")[M]).sum() / (b * DA.ravel(order="C")[M]).sum())}


out["cmp"] = [
    cmp(seed1, xcr, "lgbm seed1 (CV omnifile, stat-block training seed) vs exact central"),
    cmp(smean, xcr, "lgbm seedscan mean (n=10) vs exact central"),
    cmp(x42r, xcr, "lgbm seed42 full-omnifile CV (systematic baseline) vs exact central"),
    cmp(x42r, seed1, "lgbm seed42 full-omnifile CV vs lgbm seed1 CV omnifile"),
    cmp(rm, seed1, "VL170 replica mean vs lgbm seed1 unbootstrapped"),
    cmp(rm, xcr, "VL170 replica mean vs exact central"),
]
# seed-to-seed lgbm ML spread in units of sigma_boot
out["ml_sigma_over_boot_sigma"] = q(sml / sb)
# is seed42 inside the lgbm seed distribution? (omnifile differs, so descriptive only)
z42 = (x42r - smean) / np.sqrt(np.diag(Cml_stored))
out["cv42_minus_seedscan_mean_over_sigma_ml"] = q(np.abs(z42))
zex = (xcr - smean) / np.sqrt(np.diag(Cml_stored))
out["exact_minus_seedscan_mean_over_sigma_ml"] = q(np.abs(zex))

# --- deterministic inputs: CV omnifile (central) vs full omnifile (cv42)
inp = {}
for name in ["hDataReco2D", "hBkgReco2D", "hTruth2D", "hEffDen", "hOFTruthDenom2D", "hOFInputTruth2D", "hFlux_pt"]:
    a = sq(central_p, name)
    b = sq(cv42_p, name)
    den = np.maximum(np.abs(a), 1e-300)
    inp[name] = {"identical": bool(np.array_equal(a, b)), "max_rel": float(np.max(np.abs(a - b) / den))}
for name in ["dataPOT", "mcPOT", "potScale", "nNucleons", "fluxIntegral_m2_per_POT", "nIterations"]:
    a = uproot.open(central_p)[name].member("fVal")
    b = uproot.open(cv42_p)[name].member("fVal")
    inp[name] = {"central": a, "cv42": b, "identical": a == b}
inp["fluxSource"] = {"central": str(uproot.open(central_p)["fluxSource"].member("fTitle")),
                     "cv42": str(uproot.open(cv42_p)["fluxSource"].member("fTitle"))}
out["central_vs_cv42_deterministic_inputs"] = inp
# one VL170 replica: deterministic inputs that the bootstrap should leave alone
r1 = reps[seeds.index(1)] if False else [p for p in reps if p.endswith("boot1.root")][0]
inp1 = {}
for name in ["hBkgReco2D", "hOFTruthDenom2D", "hFlux_pt"]:
    inp1[name] = bool(np.array_equal(sq(central_p, name), sq(r1, name)))
inp1["hOFInputTruth2D_equals_central"] = bool(np.array_equal(sq(central_p, "hOFInputTruth2D"), sq(r1, "hOFInputTruth2D")))
out["replica1_vs_central_inputs_identical"] = inp1
print(json.dumps(out, indent=1, default=float))


def _extra():
    """Second pass: paper values from the ROOT TH2D (not the 3-sig-fig CSV), log-normal chi2, and the
    Fig. 6/7 projections C_1D = P C P^T over the reported bins, central = exact product."""
    o = {}
    Pv = pv_flat[M]
    d2 = xcr - Pv
    Cp = ptot[np.ix_(M, M)]
    Ct2 = Cp + Ccomb_stored + Cml_stored
    o["paper_cov_chi2_per_ndf_th2d"] = float(d2 @ np.linalg.pinv(Cp) @ d2) / n
    o["combined_chi2_per_ndf_th2d"] = float(d2 @ np.linalg.pinv(Ct2) @ d2) / n
    r = np.log(xcr / Pv)
    Vl = Ct2 / np.outer(Pv, Pv)
    o["combined_lognormal_chi2_per_ndf_th2d"] = float(r @ np.linalg.pinv(Vl) @ r) / n
    sig = np.sqrt(np.diag(Ct2))
    pull = d2 / sig
    o["combined_pull_mean_rms"] = [float(pull.mean()), float(pull.std())]
    rep2 = M.reshape(14, 16)
    dpt, dpz = np.diff(PT), np.diff(PZ)
    cols = [(ix, iy) for ix in range(14) for iy in range(16) if rep2[ix, iy]]
    Ppt = np.zeros((14, n)); Ppz = np.zeros((16, n))
    for c, (ix, iy) in enumerate(cols):
        Ppt[ix, c] = dpz[iy]
        Ppz[iy, c] = dpt[ix]
    xm = np.where(rep2, xc, 0.0)
    cen = {"pt": (xm * dpz[None, :]).sum(1), "pz": (xm * dpt[:, None]).sum(0)}
    for ax, Pm in (("pz", Ppz), ("pt", Ppt)):
        for tag, C in (("Statistical", Cb_stored), ("Total", Cu_stored + Cb_stored + Cml_stored),
                       ("ML", Cml_stored)):
            s = np.sqrt(np.maximum(np.diag(Pm @ C @ Pm.T), 0)) / cen[ax]
            o[f"fig67_{ax}_{tag}_median_pct"] = float(100 * np.median(s))
    return o


print(json.dumps(_extra(), indent=1))
```

## 7. Changed paths and callers

| path | commit | change | callers checked |
|---|---|---|---|
| `2d-unfolding/unfold_2d_omnifold_unbinned.py` | `971fc00c` | new module-level `run_provenance(args, helper_module)`; `main()` writes six `TNamed` records after `fluxSource` and prints the driver/helper lines. sha256 `d17638ef…` → `d6434d03c4a86b1ce4ff429d8fe7804abcf7fb4c7ae9a6d99ad4f96c324cf4f7` | 47 importers use only existing module names (D's inventory); no existing name, signature or histogram changed. Tests #8–#12 pass. Pre-fix bit-identity (#3, `PathsTheFixMustNotChange`) holds for `hXSec2D`, `hUnfold2D`, completeness, efficiency |
| `2d-unfolding/tests/test_bootstrap_completeness_ki84.py` | `971fc00c` | stub may carry a `__file__` (env `U2D_STUB_HELPER_FILE`); new class `RunProvenanceIsRecorded` (6 tests). sha256 → `615f5f538841eb111b47598f6c1efe35684392dfb2674320613a13e8404d89f5` | the file's existing 8 tests unchanged and passing |

Not changed: `uq/analyze_uq.py`, `uq/analyze_universes.py`, `uq/rollup_vl170_adoption.sh` (no defect
found; "For E" item 4 is a cross-owner proposal). `omnifold.py`, every receipt, every product and
`verify_hash_bindings.py` are untouched. Existing products do not gain the new records. Only future
runs write them.

## 8. Limitations and skips

- The all-replica log sweep (§4) was not completed.
- Skips: only `PathsTheFixMustNotChange` in the negative-control scratch tree (#2), by design. No
  other check skipped. Skipped tests are not counted as passes.
- Unavailable: the executed-bytes logs of `53116554` (central), the May universe sweep and matched
  CV, and the lgbm seedscan; the OmniFold helper's bytes at any historical run time; the LightGBM
  and sklearn library versions of every run.
- The local PyROOT is 6.36.000 on Python 3.13. The production environment is `root_6_28`. The KI-84
  test exercises extraction logic with a stubbed classifier, not scientific coverage.
- The independent check reads the products on disk on 2026-10-09. Their digests match the receipts.
- The universe Flux rescale (Φ_CV/Φ_u) was not re-derived at product level. Only its synthetic
  tests (#9) ran.
