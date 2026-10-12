# Selective I/O: opt-in derived-branch reading for the supported 2D driver

**CITABLE FOR:**
- the implementation and local verification of `--branch-select derived` in
  `2d-unfolding/unfold_2d_omnifold_unbinned.py`;
- its caller and frozen-package compatibility, as measured here;
- the check-routing and manifest changes proposed to integration.

**NOT CITABLE FOR:**
- any cross section, uncertainty, coverage or calibration result;
- a cluster runtime, or a whole-sweep or production speedup, of this implementation;
- deployment, adoption, a production-training change, or authority to change a launcher.

| field | content |
|---|---|
| `Lane` | selective I/O (the owner registered in `CATALOG.md`'s 2026-10-11 table and `Q/xr-sb1-integration/REPORT.md` §8) |
| `Decision` | Can SB1's measured selective-reading improvement become a supported opt-in path, while preserving loader semantics, the existing default behaviour and recoverable frozen reproduction? |
| `Branch` / `Base` | `impl/selective-io-20261010` / `origin/main` `3892e769043cddebfd58ec19e1ab1a567eb01784` (PR #77's merge; no later commit at the 05:08Z fetch) |
| `Commits` | `a35b1a3f`: behaviour change (driver, tests, usage doc). The record commit follows (§12). No structural cleanup was needed, so there is no separate cleanup commit |
| `Owner / reviewer` | One owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code. One fresh read-only reviewer, a general-purpose subagent on the same model. The campaign review's suggested Astra High reviewer is not selectable in this session |
| `Review budget` | One initial review; at most two focused repair/re-review cycles |
| `Terminal` | PASS (reviewed and ready for integration), FAIL or INCONCLUSIVE (§13) |
| `Budget` | 8 active h including review and delivery; 6 local core-h; 2 threads; 8 GiB; 3 GiB scratch beyond worktrees; 20 MiB tracked evidence; no cluster job, GPU, production training or benchmark |

`Q` = `docs/orchestration/state/next-preparation-20261009`. `S` = `Q/selective-io` (this record).

## 1. Answer

**Yes, locally verified, with the limits in §11.**
- `--branch-select derived` is an opt-in mode of the supported 2D driver.
- On synthetic fixtures it gives every loader's caller the same arrays (dtype, shape and bytes) and
  the same filled histograms as the default. Through the real command line, under the OI-136 guard,
  it gives the same OmniFold inputs, estimator arguments and outputs in six modes. These outputs
  come from a stub helper with deterministic weights: nothing was trained.
- The default, `--branch-select all`, makes the same loader calls as before. Its OmniFold inputs and
  outputs (stub helper, no training) equal those of the pre-change driver (`3892e769`). Only the recorded paths, the driver's
  digest and `runConfig`'s new `branch_select` key differ.
- The frozen SB1 and XR packages pin the old driver. At a later `HEAD` they refuse the new driver, by
  design (§7.2). At their own commits they pass (§7.3). A check-routing script for integration is
  in `S/checks/`.

## 2. Baseline and required reading

- **Refs.** `git fetch origin` at 2026-10-11T05:08Z: `origin/main` = `3892e769`, the stated
  baseline, with no later commit. The worktree is isolated, at
  `MINERvA-OmniFold-selective-io-20261010`. The canonical checkout's untracked files were not touched.
- **Read:**
  - `AGENTS.md`, `docs/CURRENT_WORK.md` and `CAMPAIGN-REVIEW-20260929.md`;
  - `README.md`, "Before changing the 2D driver";
  - `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, "2D Python unfolding contract";
  - `Q/sb1-prep/REPORT.md`, with `branch_select.py`, `sb1_run.py` and the four test files;
  - `Q/sb1-run/REPORT.md` §§2–3, 6–7 and 9–11;
  - `Q/xr-sb1-integration/REPORT.md`, all of it, especially §8.
- **The driver at base.** It is git blob `e19aeb6d`, sha256 `3cc5adc7…`, the bytes SB1 and XR pin.
  SB1's completed head `339e6ab0` is an ancestor of the base. Its evidence is used as integrated,
  with the receipt renames recorded at `Q/xr-sb1-integration/REPORT.md` §4.

## 3. Constraints checked before editing

- **The rooted import.** Joseph's 2026-08-23 ruling (`AUTHORIZATION-20260903-oi136-failopen-repair.md`
  §2; `README.md`) rests on two conditions:
  - the `sys.path` insert stays inside `main()`;
  - `unbinned_unfolding/python/omnifold.py` keeps its digest.

  Neither changed:
  - the insert is unchanged, now at `:2061` (`sys.path.insert`; the literal is at `:2059`), inside
    `main()`;
  - the helper is not touched.

  Both condition tests in `test_oi136_rooted_insert_ratchet.py` pass, and so does the whole suite (§7.1).
- **Hash bindings.** The driver's three sha256 pins are already drifted and listed in
  `verify_hash_bindings.py` `KNOWN_PREEXISTING`:
  - the negweight durability receipt;
  - the Gate-2 launcher;
  - `gen5d-build.json`, a run record that the verifier does not check.

  They stay drifted, at a different digest. The frozen SB1/XR receipts and manifests name `3cc5adc7…`
  in forms the gate does not resolve (`Q/xr-sb1-integration/REPORT.md` §8, condition 3). Measured
  after the edit: `verify_hash_bindings.py` prints **ALL BINDINGS INTACT**, inventory unchanged.
  No receipt names the edited driver as live evidence.
- **Ownership.** This lane writes only:
  - the driver;
  - one new test file, `2d-unfolding/tests/test_selective_io.py`;
  - one usage subsection in `2D_OMNIFOLD_REFERENCE.md`;
  - `S/`.

  Nothing under `Q/sb1-prep/`, `Q/sb1-run/`, `Q/two-d-followup/`, `Q/xr-*` or any XR deployment or
  output was written. Nothing changed in the guard, the helper, an estimator setting, a launcher, a
  shared register, a catalog, a manifest or the binding constants.
- **Concurrent XR work.** The two write sets are disjoint (§8).

## 4. The implementation (`a35b1a3f`)

All of it is inside the driver, so the driver digest `main()` already records (`driverSha256`)
covers the executed selection code. No module is imported from elsewhere, which keeps the change out
of the OI-136 import question.

| piece | where | what it does |
|---|---|---|
| `--branch-select {all,derived}` | `:1511` | default `all` |
| `call_loader(func, tree, *args, branch_select, selection_log, **kwargs)` | `:1056` | `all`: returns `func(tree, *args, **kwargs)`, the call `main()` made before, on the real tree, with no status change. `derived`: the steps below |
| `derive_loader_branches` | `:1044` | runs the loader against `_DiscoveryTree` (`:895`) up to its first `GetEntry`, recording `SetBranchAddress` names without forwarding them and reading no entry. The list must equal `expected_loader_branches` (`:991`) exactly, names and order, and no name may repeat |
| `expected_loader_branches` | `:991` | the static rule for the four loaders, built from the loaders' own name helpers (`_universe_*_branch`, `_universe_kine_branches`), so the sanitization and naming conventions exist once |
| `_SelectedTree` | `:928` | the loader's view of the tree. It refuses a `SetBranchAddress` outside the derived set or on an inactive branch. Before the first `GetEntry` it verifies that the addressed, active and derived sets are equal and that every derived branch holds an address; then it hands `GetEntry` straight to ROOT. Any other tree method raises `UnmodelledTreeAccess` |
| restore | `call_loader`'s `finally` | puts back the entry branch statuses and the addresses of the derived branches, then verifies both. Without the address restore, a reused tree would be written through freed loader buffers (the segfault SB1 recorded) |
| record | `:1735`, `:2369` | each loader's tree, branches, branch count and verification. Printed as one `[INFO] branch-select=derived:` line per loader, and written as a `branchSelection` TNamed (derived only). `runConfig` (`vars(args)`) records `branch_select` in both settings |

Differences from prototype 1 (`Q/sb1-prep/branch_select.py` at `d4335d3b`):

| prototype 1 | here |
|---|---|
| wrapped the loaders from outside | called from `main()` |
| `extra=`/`omit=` arguments for its negative controls | none: the tests perturb the applied set by patching `apply_branch_selection` |
| its own `sanitize()` | reuses the driver's helpers |
| refused the alt-model closure path | supports it, with the two alt weights in the rule, tested |
| `call_all` refused a tree with any inactive branch | the default makes no check at all, as before |
| | refusal is `BranchSelectionError`, a `RuntimeError` subclass: the run stops with a traceback, exit 1, and no output is written |

Unchanged:
- the four loaders' bodies and signatures;
- every argument they receive;
- everything after them in `main()`, including the estimator arguments;
- the helper import;
- the default path.

## 5. Supported opt-in usage

```
python3 2d-unfolding/unfold_2d_omnifold_unbinned.py <the usual arguments> --branch-select derived
```

- **Modes.** Every mode of `main()` works:
  - CV, with or without `--use-weights`;
  - `--universe` lateral and vertical, including `Flux:N` with `--flux-universe-file`;
  - `--closure` and its variants, including `--closure-alt-universe`;
  - `--bootstrap-seed`/`--bootstrap-streams`;
  - every `--bkg-mode`.

  In closure mode the truth-denominator loader is not called, as before, so three loaders are selected.
- **Launchers.** No launcher passes the flag, so every existing launcher, receipt and campaign is on
  the default path.
- **Under the guard.** It runs under `nd-unfolding/mnv_guarded_run.py` as before. The derived path
  starts no process.
- **Documentation.** `2d-unfolding/2D_OMNIFOLD_REFERENCE.md`, the new subsection "Opt-in selective
  branch reading", records the usage, what SB1 measured and what it did not.

## 6. Tests

`2d-unfolding/tests/test_selective_io.py`: 27 tests, about 40 s locally. Fixture: SB1's
`make_fixture_omnifile.py`, loaded read-only from the frozen package.

| class | tests | covers (SB1 control it reuses) |
|---|---|---|
| `TheFixture` | 2 | the fixture reaches every boundary: pass flags 0/1/2, ±4 ulps of the 20° cut, weights at and past 1e4 and 1e6, non-finite and negative, `-0.0`, `\|x\|>1e3`; lateral branches differ from CV; vertical ones have no kinematics (`test_branch_select.TheFixture`) |
| `Loaders` | 11 | derived = direct call = `all`, byte for byte, for 15 loader × pattern cases (CV unweighted/weighted, `Flux_0`, `GEANT_Neutron_0`, `Muon_Energy_MINOS_0`); the alt-closure path; the lateral and vertical branch lists; the default passes the real tree and changes no status; a reused tree (two selections, then a default read on the same object); a partial entry state; discovery reads no entry and leaves no address; an empty tree; a missing universe branch fails with the default's error; an unknown mode is refused (`test_branch_select.Equality`) |
| `Refusals` | 8 | each of the 17 derived branches omitted in turn (the lateral pattern), and one extra activation per tree, are refused before the first read with the tree restored; the silent defect is reproduced without the guard; a loader reading another branch is refused by the rule; a wrong rule that agrees with a wrong loader passes the guard and is caught only by the bytes; unmodelled access; digest power (`test_branch_select.NegativeControls`) |
| `CommandLine` | 6 | the real script, run under `mnv_guarded_run.py` in a throwaway git checkout, with a stub helper that records what `ohf.omnifold` receives and returns deterministic non-unit weights. Six modes × both settings: CV, CV unweighted, lateral `Muon_Energy_MINOS:0` with `lgbm`, vertical `Flux:0` with a flux-universe file, alt-model closure, bootstrap + `negweight` with `hist`. Asserted: every module loaded from the checkout (guard inventory); identical OmniFold inputs and estimator arguments; identical output objects (each histogram's X- and Y-axis bin edges, contents and errors with flow, and entries; TParameters; TNamed), except `runConfig` (only `branch_select` and `out`), `runArgv` and the added `branchSelection`; the selections recorded; the default equal to the pre-change driver in four modes; two mutant drivers (omit, extra) refused through the entry point with no output and no training, while their default path still runs (`test_sb1_guarded`) |

- **What the CLI tests do not run.** The real helper and training. The stub stands in, so the
  equality of OmniFold inputs is shown directly. Trained-output equality is not shown here; SB1
  measured it on the real file at 6.4e-13 relative (§9).
- **Do the tests fail when they should?** `S/logs/mutation-run-2.txt` records six deliberate
  driver mutants (`S/checks/mutants.py`), each run against `Loaders` and `Refusals` and then
  reverted, with the driver's sha256 re-checked. Its failure lists are complete; the first run,
  `S/logs/mutation-run.txt`, had five mutants and cut each list at 12 lines (review F4). Every mutant
  was caught:

  | mutant | tests that failed |
  |---|---|
  | no verification at the first entry | the four extra-activation cases |
  | no inactive-branch refusal | every omitted-activation case |
  | no status restore | the reuse, partial-state, empty-tree and refusal-restore tests |
  | the default applying a selection | the default and equality tests |
  | the rule forgetting the alt weights | the alt-closure test |
  | no address restore | the three reused-tree cases, by an assertion on the restored null addresses. Before repair batch 1 this mutant was detected only by a segfault (review F5) |

  The counts per mutant are 4, 17, 26, 17 (16 failures and 1 error), 1 and 3 failing tests or subtests.

- **ROOT 6.28.** SB1's only 6.28 failure was a fixture-*reading* problem
  (`Q/sb1-run/REPORT.md` §3): `RDataFrame.AsNumpy` returns a `UChar_t` column as `str` objects
  under 6.28. The loaders read it through `SetBranchAddress` into `array("B")`.
  - These tests never call `AsNumpy`. `column()` reads every fixture column per row, exactly as the
    loaders do, and the boundary test asserts the flag set `{0, 1, 2}` on those values.
  - The fixture writer (`RDF.FromNumpy` + `Snapshot`) is SB1's, which ran on 6.28 on the login node.
  - **Not run on 6.28 here**: there is no local 6.28, and no cluster use was authorized (§7.4).
  - The CLI class skips itself where `/pscratch/.../unbinned_unfolding/python` exists. There the
    driver's rooted insert would load the canonical helper, not the stub, and the guard would refuse it.
- **The frozen SB1 tests** are unchanged, and pass at their commit (§7.3).

## 7. Checks

Local only:
- macOS, Python 3.13.7, ROOT 6.36.00, numpy 2.4.4;
- `OMP_NUM_THREADS=1`, a scratch `TMPDIR`, at most two processes;
- no Slurm client on this host (`which sbatch scancel squeue sacct srun salloc` finds none), so no
  scheduler call was possible.

Logs are in `S/logs/`.

### 7.1 Executed on the implementation

At `a35b1a3f`, in this worktree; the only untracked path is `S/`.
- Summary: `S/logs/suites-a35b1a3f.txt`.
- Full runner output: `S/logs/full/suites-a35b1a3f/`.
- Runner: `S/checks/run_suites.sh`.

| check | interpreter | result |
|---|---|---|
| `2d-unfolding/tests/test_selective_io.py` (new) | 3.13 + ROOT 6.36 | **27 OK** |
| `2d-unfolding/tests/test_bootstrap_completeness_ki84.py` (real `main()`, stub helper) | same | **15 OK** |
| `2d-unfolding/tests/test_reported_cells.py` | same | **18 OK, 5 skipped** (no matplotlib in this interpreter; the skipped tests exercise the reporting script, not the driver) |
| `2d-unfolding/tests/test_final_rollup_full_refusal.py` | same | **3 OK** |
| N2 `test_producer_provenance` / `test_n2_harness` / `test_producer_final_dependencies` | same | **26 OK / 22 OK / 5 skipped** (the last needs matplotlib for the real analyzer) |
| `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` / `test_oi136_failopen_inventory_ratchet.py` | same | **10 OK / 7 OK**. Both of the driver's condition tests pass. The 2026-10-09 caveat about red ratchet suites does not reproduce here |
| `nd-unfolding/tests/test_flux_universe_fix.py` | same | **51 OK** |
| `nd-unfolding/tests/test_hash_bindings.py` | 3.12 + pytest | **33 passed** |
| `verify_hash_bindings.py` | 3.12 | **ALL BINDINGS INTACT**: inventory 148 / `1b610bb3…`, unchanged from the base |
| `verify_receipt_artifacts.py` | 3.12 | **0 missing**. TRACKED 9, OFF-AREA 28, BY-PATH 7, UNRESOLVED 66, pinned digest `49916d28…` unchanged |
| pre-commit hook at `a35b1a3f` | system | **13 checks passed** |
| mutation power (§6) | 3.13 + ROOT | **5 of 5 mutants caught**; driver restored and digest re-checked (`S/logs/mutation-run.txt`; `S/checks/mutants.py`) |
| `generate_manifest.py --check --at-sha` | 3.12 | OK at `3892e769`; **OUT OF DATE at `a35b1a3f`**, from the new files. Integration regenerates it (§10.2) |

### 7.2 Expected frozen-package mismatches at a later `HEAD`

At `a35b1a3f`, in this worktree. The frozen packages' bytes equal their commits
(`git diff --quiet d4335d3b HEAD -- Q/sb1-prep` and `07428e5d HEAD -- Q/two-d-followup/xr` both hold).
- Summary: `S/logs/frozen-at-head-a35b1a3f.txt`.
- Full output: `S/logs/full/frozen-at-head-a35b1a3f/`.

| frozen check at a later `HEAD` | result | cause |
|---|---|---|
| SB1 `test_package_consistency` | 1 of 7 fails: `test_the_manifest_is_current` | `make_manifest.py --check`: "manifest or proposal OUT OF DATE" (the driver digest in `expected-code.json`) |
| SB1 `test_branch_select` | module import error, 0 tests run | `load_verified` refuses the driver: "has sha256 `6be77c51…`, expected `3cc5adc7…`" |
| SB1 `test_sb1_guarded` | 7 failures, 2 errors of 10 | `sb1_run.py` refuses the changed driver: "pinned loaders `3cc5adc7…`", or "has sha256 `6be77c51…`" |
| SB1 `test_launch_chain` | 4 failures, 11 errors of 29 | the fake chain's jobs run `sb1_run.py`, which refuses the driver. Their receipts are therefore missing (`FileNotFoundError` on `J1/control_omit.json` and others), and the verifier's criteria are computed over absent jobs |
| XR `xr_admit.py manifest --check` | rc 3, "manifest/expected-code.json is OUT OF DATE" | the driver's digest |
| XR `tests/test_xr.py` | 15 failures, 2 errors of 42 | the driver digest (`6be77c51…` against `3cc5adc7…`) appears in 14 refusal messages; the other failures follow from the same refusals |

- **Attribution.** These failures come from the driver change and nothing else:
  - the identical checks pass on the base `3892e769` (§7.3), with the same interpreter and venv;
  - the base and `a35b1a3f` differ in three paths: the driver, the new test file and the reference
    doc (`git diff --name-only`);
  - no file in either package mentions the latter two (`grep`: 0 hits).
- **Why this is expected, not a defect.** Both packages are immutable evidence pinned to the driver
  they admitted, which is what the integration record predicted (`Q/xr-sb1-integration/REPORT.md` §8,
  condition 3). Their manifests, references and tests are not edited, repinned or weakened.

### 7.3 The frozen packages at their own commits

Same interpreter and venv for all three:
- Python 3.13.7, ROOT 6.36;
- LightGBM 4.6.0 and scikit-learn 1.8.0, in a scratch venv with system site packages;
- numpy 2.4.4.

| tree | SB1 suites (consistency / branch select / guarded / launch chain) | XR `manifest --check` / suite | log |
|---|---|---|---|
| base `3892e769` (old driver; package bytes equal to their commits) | 7 / 16 / 10 / 29 OK | current / 42 OK | `S/logs/frozen-at-base-3892e769.txt` |
| `d4335d3b` (SB1's package commit), via `frozen_package_checks.sh sb1` | 7 / 16 / 10 / 29 OK, rc 0 | n/a | `S/logs/frozen-routing-sb1.txt` |
| `07428e5d` (XR's package commit), via `frozen_package_checks.sh xr` | n/a | current / 42 OK, rc 0 | `S/logs/frozen-routing-xr.txt` |

- **The routing script's refusal branches.**
  - It refuses with exit 2 when the package at `HEAD` differs from its commit: run from a
    no-checkout worktree at `d4335d3b~1`, where the SB1 package does not yet exist.
  - It refuses with exit 2 on bad usage.

  Both are recorded in `S/logs/frozen-routing-refusals.txt`. Every scratch worktree was removed after use.
- **An earlier batch.** `S/checks/frozen_all.sh` also ran both packages at `d4335d3b` and
  `07428e5d`. `S/logs/frozen-at-d4335d3b.txt` and `S/logs/frozen-at-07428e5d.txt` show the same
  passes. One fault in that batch was mine:
  - I edited `run_frozen.sh` (to add full-output capture) while the `d4335d3b` invocation was still
    reading it;
  - that invocation then stopped with a bash syntax error (`S/logs/frozen-batch-stderr.txt`), after
    its four SB1 results were recorded and before its XR lines, which do not apply at that commit;
  - the routing-script runs above are the clean record for both commits.

### 7.4 Unavailable verification

| verification | status |
|---|---|
| ROOT 6.28 / Python 3.11 / numpy 1.26 (the cluster's `root_6_28`) | **not run.** There is no local 6.28, and no cluster use was authorized. The tests avoid the one construct known to differ (§6) |
| A real-file run of `--branch-select derived` (universe or CV omnifile) | **not run**: no cluster job, no bulk copy. The real-file equality evidence is SB1's, for prototype 1 (§9, §11) |
| Trained output with the real helper | **not run**: no training was authorized. The CLI tests compare OmniFold inputs and estimator arguments through a stub |
| Tests needing matplotlib (5 + 5 skips) | unavailable in this interpreter; they exercise reporting scripts, not the driver's loaders |
| The CLI class on Perlmutter | it skips itself where the rooted helper path exists (§6) |

## 8. Caller and reproduction compatibility

Population: `git grep` at the base for the driver's name and its four loaders, outside the frozen
`sb1-prep`, `two-d-followup` and `speed` packages, then each hit opened. The first version of this
table missed the module's other importers (review F2); the row for them was added in repair batch 1.

| caller | how it uses the driver | effect |
|---|---|---|
| every `2d-unfolding/sbatch_*.sh`, `seedscan*/`, `tension_iter/`, `uq/run_*_interactive.sh`, `ki84-rebuild` launcher | runs the script without `--branch-select` | default path; the same loader calls as before |
| `uq/coverage_fixed_truth/fixed_truth_toy.py` (N2) | imports the driver from hashed bytes and calls `collect_signal_arrays_2d` directly | unchanged signature and body. `test_producer_provenance` (26) and `test_n2_harness` (22) pass. A future N2 launch states the driver digest it executes, so it must name the new digest if it runs after a merge, as for any driver edit |
| `3d-unfolding/unfold_3d_omnifold_unbinned.py`, `xsec_3d.py`, `genie/gen_to_xsec5d.py`, `docs/analysis-note/redraw_central_only.py`, `ibu_1d_projection/build_1d_ibu_inputs.py` | import constants (`PT_EDGES`, `PZ_EDGES`), `make_th2d`/`make_th1d` and the branch-name helpers | unchanged. The only module-level additions are three standard-library imports (`contextlib`, `inspect`, `io`) and new names |
| 49 importers outside `Q`'s state packages: 36 in `nd-unfolding/`, 6 in `nd-unfolding/pet/`, 3 in `nd-unfolding/tests/`, and one each in `2d-unfolding/`, `2d-unfolding/uq/`, `3d-unfolding/` and `docs/analysis-note/` (count: `git grep -l -E "import unfold_2d_omnifold_unbinned\|from unfold_2d_omnifold_unbinned import\|\"unfold_2d_omnifold_unbinned\"\|'unfold_2d_omnifold_unbinned'" 6486867f -- '*.py'`, excluding `docs/orchestration/state/`; review F2. The re-review counts 44 files with an import statement, plus 5 that load or stub the module by name or path: re-review N1). Among them `unfold_nd_omnifold_unbinned.py`, `pet_systematics*.py`, `sweep_bank*.py`, `s5c_with_estimator.py` (which monkeypatches `refine_stay_positive` and `_make_bkg_classifier`) and `plot_2d_cross_section.py` | constants, histogram and branch-name helpers, `refine_stay_positive`/`_make_bkg_classifier`. Only N2 calls one of the four loaders | unaffected. Importing the module adds three standard-library imports and new definitions; the ROOT declaration is lazy (`_branch_address_api()`); none uses `import *` |
| `2d-unfolding/tests/test_bootstrap_completeness_ki84.py` | runs the real `main()` with a stub helper; compares against the pre-fix blob `4e7c20bb` | 15/15 pass. It records `driverSha256` of the current bytes, so it moves with the edit by design |
| `nd-unfolding/tests/test_oi136_*` | the driver's insert stays in a function; the helper digest | pass (§3, §7.1) |
| Frozen SB1 package `Q/sb1-prep` (`d4335d3b`) | loads the driver against `DRIVER_SHA256 = 3cc5adc7…`; its manifest pins it | refuses the new driver at a later `HEAD` (§7.2); passes at its commit (§7.3) |
| Frozen XR package `Q/two-d-followup/xr` (`07428e5d`) | `expected-code.json` pins the driver at `3cc5adc7…`; `xr_admit.py` executes it from the frozen worktree | `manifest --check` reports OUT OF DATE at a later `HEAD` (§7.2); current at its commit (§7.3) |

**Reproduction.**
- **Historical outputs.** Every one was made on the default path by an earlier blob. `git show
  <commit>:2d-unfolding/unfold_2d_omnifold_unbinned.py` recovers each.
- **The default here.** It equals the base driver's in OmniFold inputs and outputs (§6,
  `test_the_default_equals_the_driver_before_this_change`).
- **Receipts.** No receipt is relabelled. SB1's receipts and its benchmark remain evidence about
  prototype 1 wrapping blob `e19aeb6d`, not about this implementation. This implementation's own
  evidence is local and synthetic (§6, §7).

**Concurrent XR work.**
- **What XR does.** It runs a separate repair and reproduction with the pre-selective-I/O driver and
  its own pinned deployment.
- **Write sets.** This lane wrote nothing of XR's: no package, environment, output, deployment or
  canonical cluster checkout. It contacted no cluster at all.
- **No dependency.** XR does not depend on this implementation:
  - XR's packages name blob `e19aeb6d` (sha256 `3cc5adc7…`);
  - `Q/xr-sb1-integration/REPORT.md` §8 condition 2 requires the new XR package to keep naming
    that blob, from a base before any selective-I/O merge or as an execution-only record copy.
- **Merge order.** Merging this branch moves `main`'s driver. An XR package built from a base after
  that merge would no longer name the blob it tests. So the XR owner should build from a base before
  the merge, as §8 of the integration record already requires; this branch should not be merged into
  an XR package.

## 9. Performance: measured versus unmeasured

| quantity | status | source |
|---|---|---|
| Matched speedup of the mechanism, one lateral universe (`Muon_Energy_MINOS:0`) on one regular node | **measured, on prototype 1 (the wrapper), not on this in-driver port**: elapsed 2,604 → 888 s; MaxDiskRead 171.3 → 2.36 GB; sacct MaxRSS 69.5 → 17.2 GB | `Q/sb1-run/REPORT.md` §7 (frozen PASS; S5 PASS-AT-TOLERANCE, max relative difference 6.40e-13, not byte-identical; S6 profiling coverage FAIL, 86.93 %) |
| Vertical (`Flux:0`) loader times, loaders only, one thread | measured on prototype 1, not a matched pair (J1's all-branch loaders ran concurrently, the selective ones sequentially): `collect_signal_arrays_2d` 1,331.7 → 133.4 s; `collect_truth_denom_arrays` 607.3 → 62.4 s | same, §7.1 |
| The port's own cost | **unmeasured on the real file.** The port runs the same steps as prototype 1: one discovery pass to the first `GetEntry`, `SetBranchStatus`, a guarded first read, then direct `GetEntry`. It differs in where it is called from, the name helpers and the alt weights. No reason for a different cost is known, but none was measured | §4 |
| Whole-sweep speedup | **unmeasured** | none |
| 128-thread production runtime | **unmeasured.** Both SB1 timed runs very probably trained with 64 LightGBM threads, not 128: the guard refused loky's `lscpu` probe, and loky fell back to counting physical cores per socket (an inference; the receipts do not record the thread count) | `Q/sb1-run/REPORT.md` §7.6 |
| Process heap | **no reduction shown.** `ru_maxrss` was 14.17 vs 14.10 GB; what makes up the 4× sacct MaxRSS difference is unexplained | `Q/sb1-run/REPORT.md` §7.4 |
| Phase attribution | S6 FAIL: about 13 % of the CV job's wall was not covered by the hooks | `Q/sb1-run/REPORT.md` §7.3 |

Training threading is not changed here. An explicit `n_jobs`, or a guard change for the `lscpu`
probe, belongs to the pinned helper's and the guard's owners (`Q/sb1-run/REPORT.md` §11 item 6).

## 10. Proposals for integration (not applied here)

1. **Check routing for the frozen packages (integration).** The SB1 and XR packages pin the old
   driver, so their at-`HEAD` checks refuse it by design (§7.2). Run them at their own commits.
   - `S/checks/frozen_package_checks.sh {sb1|xr} [PYTHON]` does this:
     - it first confirms the commit is present and the package bytes at `HEAD` equal those at the
       commit;
     - it then runs the package's own suites (SB1), or its `manifest --check` and suite (XR), in a
       throwaway detached worktree at `d4335d3b` or `07428e5d`;
     - it removes the worktree.
   - Proposed routing: in integration's check table, replace "SB1 package suites" and "XR manifest
     check / suite" at the integration tree with these two commands. Keep the
     `git diff --quiet <commit> HEAD -- <package>` byte checks at `HEAD`, which stay meaningful.
   - Measured (§7.3): `sb1` rc 0 at `d4335d3b`; `xr` rc 0 at `07428e5d`.
   - No package, manifest or test is edited, and no reference is repinned.
2. **`MANIFEST.tsv` regeneration (integration).** `generate_manifest.py --check --at-sha` is OK at the
   base and OUT OF DATE at this branch's head, because the new files are not inventoried.
   - Measured at the record commit: 38 new rows (exactly the files under `S/`), 61 existing rows
     with changed derived columns (reference lists and inbound-reference counts), and 0 rows removed.
     Recount at the delivered head (§13).
   - Integration should regenerate it once from source when merging, as for SB1
     (`S/proposals/MANIFEST-regeneration.txt`).
   - A tracked diff of the table is deliberately not provided. It would itself name every path it
     lists, which moves their inbound-reference counts, so it could never be current: my first
     attempt showed exactly this.
   - `Q/selective-io/REPORT.md` already has its `MACHINE open` override row (added by integration).
3. **Catalog (integration).** An outcome line for the selective-I/O row of `CATALOG.md`'s
   2026-10-11 table: "implemented as opt-in `--branch-select derived`; locally verified; terminal
   §13; no cluster measurement of the port".
4. **Undated line citations into the driver (their owners).** Six live files cite driver line numbers
   without a commit, and several were already stale before this change:
   - `KNOWN_ISSUES.md:47` (`:1611-1612`);
   - `docs/publication/audit-20261008/CLAIM-TABLE-20261008.tsv:12` (`:1121-1131`);
   - `nd-unfolding/pet/check_step1_class_ratio.py:44` and `fullevent_fps_dataloader.py:837`
     (`:1715-1716`);
   - `ibu_1d_projection/build_1d_ibu_inputs.py:119`;
   - the ratchet message in `test_oi136_rooted_insert_ratchet.py:314` (`:1679`).

   Every line after the import block moves: by +3 before the new section at `:773`, by +319 from
   `compute_efficiency_2d` to `main()`, and by up to +343 at the end of `main()`. Citing a function name or a commit would keep them valid. None is edited here.
5. **SB1's ROOT 6.28 test (sb1-prep owner, frozen).** `test_branch_select.py:128` stays non-portable
   in the frozen package. The new tests avoid that construct (§6). No repair to the frozen file is
   proposed, because it is immutable evidence.

## 11. Residual limitations

- **No cluster or real-file run of this implementation.** Its equality is shown on SB1's synthetic
  fixture and through a stub helper. On the real universe file, SB1 measured the prototype, not this
  port. A first opt-in use on real data should compare its `branchSelection` record with SB1's
  selections (`Q/sb1-run/evidence/outroot/SL/receipt.json`), and its outputs with a matched default run.
- **ROOT 6.28 is not exercised here** (§7.4). The selection uses `SetBranchStatus`, `GetBranchStatus`,
  `SetBranchAddress`, `TBranch::GetAddress`/`SetAddress`, `ResetBranchAddress` and one
  `gInterpreter.Declare`. SB1 ran all of these on 6.28 in `branch_select.py`.
- **Trained outputs are not compared here.** Only training inputs and estimator arguments are. With
  identical inputs the trained output is the estimator's business: SB1 measured a 6.4e-13 relative
  difference between two runs, and the driver's 128-thread rerun envelope is unmeasured.
- **The guard's protection is limited to the four loaders and the tree methods they use.** A future
  loader that reads through `GetLeaf`, `tree.<branch>`, `TTreeReader` or `RDataFrame` is refused by
  the closed interface, not silently mis-read. A new loader needs its own rule in
  `expected_loader_branches`, or `call_loader` refuses it.
- **The default's provenance changes slightly.** `runConfig` gains `"branch_select": "all"`, so an
  exact string comparison of `runConfig` with a pre-change output differs by that key. The driver's
  digest changes too, as for any edit.
- **Frozen tests at `HEAD`.** After a merge, the SB1 and XR suites run at `HEAD` are red by design
  until integration adopts the routing in §10.1.
- **The XR suite's environment** here is numpy 2.4.4 against the XR record's 2.4.6. The suite passed
  at both its commit and the base (§7.3), so this did not matter for these checks.

## 12. Review

- **Setup.**
  - One fresh read-only reviewer: a general-purpose subagent, Claude Opus 5.5. It is not the campaign
    review's suggested Astra High, which this session cannot select.
  - It works in its own detached worktree at the record commit, removed afterwards.
  - Rubric:
    - loader semantics;
    - callers;
    - provenance;
    - frozen-path compatibility;
    - equivalence operands;
    - scope and ownership;
    - the accuracy of this record's claims.
  - Budget: one initial review and at most two focused repair/re-review cycles.
- **Initial review** of `6486867f`, 06:08–06:27Z, about 0.13 local core-h, by the reviewer's own
  account.
  - Its worktree had 0 changed files at start and end and was removed. It made no cluster contact,
    and its mutants ran on a scratch copy outside every checkout.
  - Preserved verbatim at `S/review/review-6486867f.md`.
  - **Verdict: PASS WITH CHANGES.** 0 MATERIAL, 3 MINOR, 4 NOTE.
  - **What it reproduced:**
    - the scope diff;
    - the new suite (27 OK), KI-84 (15) and the rooted-insert ratchet (10);
    - both gates;
    - `frozen_package_checks.sh` for both packages;
    - the at-`HEAD` refusals;
    - the manifest delta (38/61/0).
  - **Its own probes,** eight of them; all passed with byte-identical arrays and restored state:
    - an exception inside a loader after it sets addresses;
    - reusing a tree after a refusal;
    - a derived read on a tree a default read had used;
    - a caller-disabled needed branch;
    - a two-file `TChain`;
    - unweighted universe runs;
    - alt-model plus universe together;
    - positional optional arguments.
- **Repair batch 1** (cycle 1 of at most 2):

  | finding | disposition |
  |---|---|
  | F1 MINOR: the CLI comparison checked X edges only | `output_objects()` now also compares Y-axis edges and entries (test change) |
  | F2 MINOR: the §8 caller table missed the module's other importers | row added: 49 importers, counted at `6486867f`, unaffected |
  | F3 MINOR: §1 and the reference subsection did not say the outputs come from a stub | both now say so |
  | F4 NOTE: the insert is at `:2061`; the mutation log was truncated; the probe is loky's | fixed; six mutants rerun with complete lists (`S/logs/mutation-run-2.txt`); the reference subsection corrected |
  | F5 NOTE: the address restore was detected only by a segfault | the reuse test now asserts the restored null addresses. The new mutant M6 (no address restore) fails three assertions deterministically |
  | F6 NOTE: the XR manifest check ran under bare `python3`; an unreachable commit read as "differs" | the script now uses the chosen interpreter and refuses an absent commit with its own message (exit 2). Rerun: `S/logs/frozen-routing-xr-2.txt` |
  | F7 NOTE: the rule restates the loaders' logic, by design | recorded in §11; no change |

  No driver byte changed in this batch.
- **Focused re-review** of `446e2857` (cycle 1 of at most 2), by the same reviewer, 06:32–06:35Z,
  about 0.02 local core-h.
  - Its worktree had 0 changed files at start and end and was removed. It made no cluster contact.
  - Preserved verbatim at `S/review/rereview-446e2857.md`.
  - **Verdict: PASS.** F1–F6 resolved as dispositioned and F7 needs no change. No new defect. The
    preserved first review is byte-identical to what the reviewer wrote.
  - It reran the new suite (27 OK) and mutant M6 (three assertion failures, no segfault), and tallied
    the mutation log (4/17/26/17/1/3). It checked the routing script's new refusal (exit 2,
    worktree count unchanged).
  - One NOTE (N1): the importer count's method was not stated exactly. The delivery commit writes
    the exact pattern and the re-review's 44 + 5 split beside it (§8).
- **Delivery commit.** It preserves the re-review, writes N1's wording, and fills §13 and the manifest
  recount. Wording only, and **not re-reviewed**. The second repair cycle was not needed.

## 13. Resources and terminal

| item | limit | used |
|---|---|---|
| active hours | 8, including review and delivery | prompt received ≈ 05:07Z; record commit 06:06Z; review 06:08–06:27Z; re-review 06:32–06:35Z; delivery ≈ 06:40Z: **≈ 1.6 h** |
| local CPU core-hours | 6 | **≈ 0.9 in total.** Owner ≈ 0.75: user+sys where timed (suites 295 s and frozen checks 182 s at `a35b1a3f`; routing runs 113 + 167 + 169 s), and an estimate for the untimed rest (two earlier suite passes, the base and frozen-commit batch, 11 mutant runs, the repaired suite, the venv setup). Reviewer ≈ 0.15, self-reported |
| threads | 2 | 1 per process; at most 2 processes at once |
| RAM | 8 GiB | largest measured process 0.89 GB peak RSS (the new suite, `/usr/bin/time -l`) |
| scratch beyond worktrees | 3 GiB | about 0.2 GiB: venv 165 MiB, logs and fixtures. The four scratch worktrees (about 0.42 GiB each, at most one at a time) were removed |
| tracked evidence | 20 MiB | `S/` is 0.25 MiB |
| cluster / GPU / training / benchmark | none | **none**: no cluster contact of any kind, no GPU, no training, no benchmark |

**Terminal: PASS.** The opt-in implementation is independently reviewed (initial review PASS WITH
CHANGES, with 0 MATERIAL findings; focused re-review PASS) and ready for integration.
- **Merge.** Branch `impl/selective-io-20261010`, pushed as a draft PR; not merged, not deployed.
- **What integration needs to do (§10):**
  - route the frozen SB1/XR checks to their commits with `S/checks/frozen_package_checks.sh`;
  - regenerate `MANIFEST.tsv` from source. At the delivered head the delta is
    43 new rows (the files under `S/`), 61 existing rows with changed derived columns, 0 removed;
  - optionally, add the catalog outcome line.
- **What PASS does not include:**
  - a cluster or ROOT 6.28 run of this implementation;
  - a real-file equality run;
  - trained-output equality;
  - any new performance number.

  The measured speedup remains SB1's single matched lateral pair, for prototype 1 (§9). No launcher
  uses the opt-in path, and no production use, adoption or training change follows from this record.
