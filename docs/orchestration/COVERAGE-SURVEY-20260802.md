# COVERAGE SURVEY 2026-08-02 — what this repo contains that nothing exercises

*Coverage, not defects. Nothing here is a bug report; the question throughout is "what evidence
exists that this runs?", and the answer is often "none" for things that are perfectly correct.*

Scope: the whole checkout at working-tree state of 2026-08-02 (branch `main`, two pre-existing
unstaged edits to `docs/INTEGRATION_CHECKLIST.md` and `docs/analysis-note/sec_eavailw.tex`,
neither touched). Read-only survey: nothing was fixed, moved, renamed, or deleted, and the
default test command's collection was not changed.

**Baseline re-measured before and after, unchanged:**
`python3 -m pytest nd-unfolding/tests -q` → **8 failed, 602 passed, 1 skipped**, the same failure
set (6 × `test_fullevent_gate2.py` + 1 × `test_gate2_target_runtime.py` off-Perlmutter
`/pscratch`, + `test_hash_bindings::test_no_new_broken_hash_bindings`).

---

## 1. Test files and which collection path reaches them

**41 test-named files.** (40 match `test_*.py`; the 41st, `2d-unfolding/uq/bottom_line_test.py`,
matches pytest's other default pattern `*_test.py`. Both patterns are collected by default, so 41
is the count pytest would consider.)

The default command collects **26 files / 611 tests**. There is **no `pytest.ini`, no
`setup.cfg`, no `[tool.pytest]`, no `testpaths`, no CI config, no Makefile, and no shell script
anywhere in the tree that invokes pytest** — verified by grep over `*.sh`/`*.yml`/`*.yaml`/
`*.toml`/`*.ini`/`*.cfg`. The only collection path that exists is a human typing the documented
command.

| location | files | pytest tests | reached by | note |
|---|---|---|---|---|
| `nd-unfolding/tests/` | 27 | 611 collected | default command | 26 collected; see next row |
| ↳ `test_p3f_pet_fullevent_launcher.py` | 1 | 29 | **Perlmutter only** | `conftest.py` `collect_ignore`s it because its module-level absolute `/pscratch` path is absent. By design — the file is SHA-bound in the Gate-3 gate and must stay byte-identical. |
| `docs/orchestration/` | 6 | 99 | **nothing** | Pytest-shaped and would run. No collection path reaches them. Run explicitly, 20 fail. Already recorded in `FINDING-20260802-orchestration-tests-never-run.md`. |
| `nd-unfolding/pet/` | 2 | **0** | **default command, indirectly** | Not pytest files at all — `main()`-style scripts. But `tests/test_g2_guards_collected.py` wraps both as subprocesses, gates on exit 0, and pins their self-reported check counts (29 + 474 = 503). **These are exercised.** |
| `omnifold_nn/omnifold/tests/` | 4 | **0** | **nothing** | See below. |
| `nd-unfolding/uq_fps/corrected/` | 1 | 4 | **nothing** | Real pytest tests. Collect only from a `nd-unfolding/` cwd (needs `uq_math` on `sys.path`); from repo root or their own dir they error. Referenced only in `FPS_UQ_CORRECTED_STATE.md`. |
| `2d-unfolding/uq/bottom_line_test.py` | 1 | **0** | **nothing** | `main()`-style script, needs PyROOT. Referenced in `AGENTS.md`, `VALIDATION_LEDGER.md`, `LITERATURE_NOTES.md`, and two RUN_LOGs — i.e. run by hand, results recorded, never automated. |

### The `omnifold_nn` four are not tests

`test_dataloader.py`, `test_omnifold.py`, `test_omnifold_pc.py`, `test_omnifold_parallel.py` are
vendored upstream **demo scripts**: module-level script bodies with **zero assertions** — the
"check" is a `print()`. They are referenced by **no file anywhere in the repo**.

Two further facts, both measured:

* 2 of the 4 cannot even be imported here (`ValueError: A KerasTensor cannot be used as input to a
  TensorFlow function` — the TF 2.16/Keras 3 vs vendored Keras-2 PET mismatch the repo notes
  elsewhere).
* Collecting the other two **has side effects**: importing `test_omnifold.py` runs a real
  MultiFold training at module scope. It took 118 s and wrote `omnifold_nn/log_test.txt` into the
  working tree. (That artifact was created by this survey and removed again; the tree was
  verified clean afterwards.) Anyone who "just adds `omnifold_nn` to collection" trains a model
  and dirties the tree.

### What I could not determine (category 1)

* Whether the 99 `docs/orchestration/` tests, or the 4 `uq_fps/corrected` tests, are run by
  anything **outside this checkout** — a scrontab entry, a waker job, or an operator's shell
  history. Nothing in the tree invokes them; that is the limit of what the tree can show.
* Whether the 2 Keras-broken `omnifold_nn` demos pass on Perlmutter under the vendored Keras-2
  env. Cannot be established off-cluster.

---

## 2. Executables with no RUNS.tsv row and no test

Inventory: **577 runnable artifacts** — 309 `*.sh`, 262 `*.py` entry points, 6 `*.cpp` with
`main()`. (18 of the 280 `*.py` were excluded as pure library modules: no shebang, no
`__main__` guard, no `argparse`, no `sys.argv`.)

| signal | count |
|---|---|
| has a `RUNS.tsv` row | **38 / 577** |
| referenced by a test | 63 / 577 |
| **no row, no test, no caller** | **371** (261 `.sh`, 107 `.py`, 3 `.cpp`) |
| no row, no test, but has a caller | 123 |

**`RUNS.tsv` is a very sparse coverage signal — 38 of 577.** Used alone it would flag 539
artifacts, which says nothing. The informative set is the 371 with no signal at all.

Independent cross-check (run separately, different method): counting a script as "referenced" if
its basename appears in **any** file in the tree including RUN_LOGs, ledgers and receipts — a
much more generous rule — still leaves **88 shell scripts named nowhere at all**. That 88 is a
strict subset of the 371, so the two methods are consistent; they bracket the answer. The gap
between 88 and 261 is scripts whose only mention is narrative provenance in a RUN_LOG or ledger,
never an invocation.

A second angle on the same question: of 563 non-test `.py`/`.sh` artifacts, only **55 are named
anywhere in the 26 collected test files** — and "named" there counts a mention in a docstring.

Full lists (371 unexercised; 123 called-but-unlogged) are in the appendix of this file.

### What I could not determine (category 2)

* Callers that build a script name at runtime from variables, globs, generated manifests, or
  external config with no literal filename in the repo. Such a caller would move an artifact from
  the 371 into the 123.
* Any run not recorded in `RUNS.tsv` — most of this campaign's compute predates the ledger or was
  submitted by hand. **"No RUNS.tsv row" means "not logged", not "never run."** For the 261 shell
  scripts this is the dominant caveat: most are `sbatch_*.sh` that plainly did run at some point,
  and `AGENTS.md` itself says 115 `sbatch_*.sh` names are load-bearing provenance.
* 14 artifacts have references that are provenance/hash/help-text only; they were counted as
  unexercised, which is a judgement call, not a fact.

---

## 3. Guards whose failing branch is unreachable

**30 confirmed. 0 plausible-but-unsettled. 0 unreachable-off-cluster-only.**

Enumerated from ~1,719 candidate guard/termination lines (`raise`, `sys.exit`, `assert`, shell
`exit`/`die`, error `return`) across 598 live `.py`/`.sh`/`.cpp`/`.h` files, then traced through
in-tree callers.

By reason:

* **~14 "unknown enum" raises** — `raise ValueError(f"unknown ctx={ctx!r}")` and kin, where every
  in-tree caller passes a literal from a fixed set (`unfold_2d/3d/nd_omnifold_unbinned.py`,
  `xsec_3d.py`, `uq_math.py`, `fps_provenance.py`, `minerva_pet_dataloader.py`,
  `fullevent_fps_dataloader.py`, `plot_uncertainty_fig6_7_style.py`). Weakest category: cheap
  defensive programming, dead only because callers are disciplined.
* **~5 truth/weight length checks** vacuous by upstream construction — e.g.
  `unfold_2d_omnifold_unbinned.py:1738`, `3d:617`, `nd:984`, `1d:411`. `omnifold.py` masks
  `MCgen_entries` by `MC_pass_truth_mask` and creates weights at exactly that length, and every
  caller rebuilds its truth array with the identical mask.
* **4 C++ `assert`s dead by constant** in `runEventLoopOmniFold.cpp` / `runEventLoop.cpp` — e.g.
  `:1922 assert(error_bands["cv"].size() == 1)` where that entry is unconditionally overwritten
  with a one-element initializer at `:1785`.
* **1 dominated by an earlier guard** — `unfold_2d_omnifold_unbinned.py:677` raises on
  `alt_universe_branch && universe_branch`, but the only caller path exits first at `:1200-1201`
  on the same condition at CLI level. *(Verified independently.)*
* Remainder: shape/existence checks in `uq_math.py` and `fps_provenance.py` guaranteed by their
  only callers.

### Deliberately NOT counted

The two vacuous paths the repo documents about itself — the Phase-18.2 fakes subtraction
(`unfold_2d_omnifold_unbinned.py:1485-1498`, "structural no-op") and the completeness `c ≡ 1`
division (`:1873-1876`) — **do not qualify**. They are unreachable *behaviour*, but neither
fails: one subtracts, the other prints a warning. Same for the documented J37
`Erecoil/Getq0True` path. They are no-ops, not dead guards.

### What I could not determine (category 3)

* **No shell guard was confirmed dead, at all.** Sourced variables, scheduler state, `eval`,
  command substitution, pipelines and `set -e` exceptions make nearly all shell reachability
  runtime-dependent. This is a real blind spot over 309 files, not an absence of findings.
* Hash/schema/receipt/ROOT-object/inventory validators were generally *not* classed as dead: a
  malformed file can exercise them even though every committed product currently passes.
* PyROOT / PlotUtils / LightGBM behaviour was not treated as compile-time fact unless the checked
  condition is fixed in this repo.
* Dynamic dispatch (`getattr`, imported callbacks, generated launch commands) can evade a textual
  caller search. Every "config-pinned" verdict is a claim about *current in-tree* invocation.

---

## 4. Receipt bindings that don't resolve — all of them enumerated

`verify_hash_bindings.py` prints `(N unresolvable: data files, off-repo artifacts, binaries)`.
That parenthetical is a **label, not a check**. Enumerated independently.

**The count is 308 today, not 303.** 303 was correct when
`FINDING-20260802-orchestration-tests-never-run.md` was written earlier the same day; receipts
have been added since. Current verifier output: `resolved 113 bindings (308 unresolvable...)`,
104 OK, 4 known pre-existing drift, 3 Gate-2 mismatches.

| extension | count |
|---|---|
| `.root` | 154 |
| `.out` | 121 |
| `.npz` | 11 |
| `.log` | 10 |
| *(no extension)* | 5 |
| `.json` | 4 |
| `.npy` | 1 |
| `.err` | 1 |
| `.py` | 1 |

**Testing the label two independent ways** — (a) does a file of that basename exist anywhere in
the checkout, (b) does the path resolve if re-based against `nd-unfolding/`, the receipt's own
directory, or any ancestor — both converge on the **same 3**:

| recorded path | correct base | state |
|---|---|---|
| `unfold_nd_omnifold_unbinned.py` | `nd-unfolding/` | **DRIFTED** — frozen `9431d56a…`, actual `3f6d3e06…` |
| `active_universe_5d/fps/covariance/audit_merged_fps.json` | `nd-unfolding/` | MATCH |
| `active_universe_5d/fps/covariance/fps_reported_mask.json` | `nd-unfolding/` | MATCH |

All three come from **one receipt**, `nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json`,
which records paths relative to `nd-unfolding/` while `localize()` joins to the repo root. So the
resolver bug affects **3 bindings, not 1** — the prior finding named only the `.py`. The two JSON
ones happen to still match, which is luck, not verification: nothing would have reported them if
they had drifted.

**Two things the label hides that are not data:**

1. **4 bindings pin `runEventLoopOmniFold`** — the canonical compiled analysis binary
   (`AGENTS.md`: "Canonical runtime binary ... do **not** call build-tree copies"). Three record
   the absolute `/pscratch` path, one records `MINERvA101/opt/bin/runEventLoopOmniFold`. The
   binary is not in the checkout (built in-tree, untracked), so all four are unresolvable **here**
   — they would resolve on Perlmutter. The single most load-bearing executable in the 2D/PET
   pipeline has four hash pins that this checkout can never verify.
2. **1 entry is not a file path at all.** `g2-attempt2-terminal`, from
   `docs/orchestration/state/qp5-wake-reconciliation-20260719.json`, is an *event name*. The
   collector's `<base>_sha256` + sibling `<base>` rule fires on `{"event": "g2-attempt2-terminal",
   "event_sha256": "ddfb87c2…"}` and harvests it as a binding. The "unresolvable" count is
   therefore not a clean measure of anything — at least one member is a collector false positive.

Net: of 308, **300 are genuinely data/log artifacts**, 4 pin an untracked binary, 3 are the
mis-based receipt, 1 is not a path. Full 308-row dump with receipt provenance is in the appendix.

### What I could not determine (category 4)

* **Whether any of the 300 data artifacts exist on Perlmutter and still match their frozen
  hashes.** This is the big one: the whole point of those bindings is unverifiable off-cluster,
  and 300 of 308 fall in it.
* Whether any recorded path refers to an artifact present in the checkout under a **different
  basename** (a rename). Both my tests key on basename or re-basing; neither detects a rename.
* The 36 absolute `/pscratch` paths are expected-absent here and were not investigated further.

---

## 5. Invariants asserted in `*_CONTRACT.md` with no executable check

`nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md` is the only `*_CONTRACT.md` in the tree (332
lines). **149 invariants** enumerated from it.

| | count |
|---|---|
| enforced by a check that runs in the default suite | **87** |
| enforced only by a check that does **not** run | 2 |
| **no executable check anywhere** | **57** |
| could not determine | 3 |

Rule used: enforced iff at least one executable check would fail when the sentence is violated in
the way it forbids. Compound sentences marked *(partial)* with the unenforced clause named.

**The 87 carry a large caveat.** For 8 of them the only check is
`validate_pet_nominal_gate4.check_freeze` (seed 42, niter 2, epochs 8, 2M subsample, canonical
edges, estimator ID). Its *logic* is unit-tested and does run (62 tests), but **the gate has never
been applied to a real artifact — no P5B nominal exists.** Marked `yes*`. Enforcement is latent,
not demonstrated.

Representative unchecked invariants (full 149-row table in the appendix):

* "Every P5B component MUST carry ONE of these fingerprints and never mix the two" — there is no
  full-event covariance assembler in the tree at all; the four `assemble_*`/`combine_*` scripts
  are the recoil-only `bkgsub` path the contract quarantines.
* "recoil-only PET UQ is NEVER attached to either" — `RECOIL_OR_OLD_INPUT_MARKERS` screens input
  *paths*, not UQ products; nothing refuses `products/pet/bkgsub/`.
* "EDGES … never as classifier inputs or training bins" — only the *value* of the edges is
  guarded, never their *use*.
* "PET trains UNBINNED on CONTINUOUS features" — no test asserts the input tensor contains no bin
  index.
* `batch 1024`, `Adam lr 1e-4`, the C_ml crossed-design rule, the fingerprint recipe itself, and
  the nominal product path — all unchecked.

**Enforced only by a check that does not run (2):**

* F9 save/reload assertion, at `pet/smoke_fullevent_tf.py:105-108` — not named `test_*.py`, not in
  `tests/`, wrapped by nothing (contrast the `test_g2_guards_collected.py` wrapper), and
  cluster-only regardless since it imports TF + `omnifold.PET` at module level.
* The F7 replica-vs-nominal target check, at `tests/test_fullevent_gate2.py:282` — one of the 8
  baseline reds, via the hardcoded `/pscratch` DataLoader literal at `:37`.

**A doc-internal contradiction, not a coverage gap** (independently verified): the truth-cloud
table at L99 says `KNN coords = (theta,phi) = (5,6)`; the CLM-008 F10 entry at L250 of the *same
document* says `coord_idx=(5,6,7)=(θ,cosφ,sinφ)`. The code implements `(5,6,7)` on an 8-column
cloud (`fullevent_fps_dataloader.py:204`) and a passing test pins `(5,6,7)`
(`test_fullevent_fps.py:96`). One sentence is enforced; the other is contradicted by a green test.

### What I could not determine (category 5)

* Whether the P3S-exclusion ("NEVER P3S standard", L321) is an **executable rejection** or only a
  labelling convention — resolving it needs `validate_p3f_pet_fullevent.py` read end to end.
* Whether the G3 prerequisite is actually enforced in production: `run_config_gate` requires
  `--gate3-manifest` to carry a PASS verdict, but the flag defaults to `None`, so it is opt-in at
  the launcher. Whether `sbatch_pet_fullevent_nominal.sh` always passes it was not audited.
* The "residual summaries" clause: the estimator ID `pet-fullevent-fps-v1` is *defined* (L19-21) to
  include residual summaries; L124 of the same doc says they are still not dumped; the Gate-4
  freeze enforces a 13-feature list without them. Counted enforced *(partial)*, but the definition
  and the freeze do not describe the same estimator.
* The "Estimated cost" (L211-223) and "P5A validation status" (L230-245) blocks were excluded from
  the 149 as estimates and result records rather than invariants. None has an executable check
  either; enumerating them as claims-to-verify is a separate pass.

---

## Method and provenance

Five categories surveyed in parallel by four accounts, all read-only; every headline number was
re-derived or spot-checked locally before being written here.

* Categories 1 and 4: this session, directly (pytest collection runs, and a script mirroring
  `verify_hash_bindings.collect`/`collect_shell`/`localize`).
* Category 2: codex-personal, `--sandbox read-only`. Cross-checked against an independent
  local count (88 ⊂ 371).
* Category 3: codex-school, `--sandbox read-only`. Two findings spot-checked against source.
* Category 5: claude-school, `--allowedTools Read,Grep,Glob,Bash`. It independently corrected two
  premises it was given and independently reproduced the 8/602/1 baseline; its KNN contradiction
  and its `TRUTH_ELIGIBLE_FEATURES` verdict were both verified against source here.

`git status` was checked after every delegate finished; the tree carried only the two
pre-existing edits throughout.

---

# Appendix A — category 2 full lists
## A.1 Unexercised: no RUNS.tsv row, no test, no caller (371)
```text
2d-unfolding/ibu_1d_projection/sbatch_ibu_1d_projection.sh  sh  Submits the 1D IBU-projection workflow.
2d-unfolding/sbatch_analyze_MEFHC_final.sh  sh  Submits the final MEFHC analysis.
2d-unfolding/sbatch_backend_bench_MEFHC.sh  sh  Submits the MEFHC backend benchmark.
2d-unfolding/sbatch_bkg_negweight_hist.sh  sh  Submits negative-background-weight histogram production.
2d-unfolding/sbatch_bkgnw_exact_refined.sh  sh  Submits the exact refined negative-weight study.
2d-unfolding/sbatch_closure_shapes_20.sh  sh  Submits the 20-shape closure study.
2d-unfolding/sbatch_coverage_toys_MEFHC.sh  sh  Submits MEFHC coverage toys.
2d-unfolding/sbatch_coverage_toys_MEFHC_200.sh  sh  Submits the 200-toy MEFHC coverage run.
2d-unfolding/sbatch_download_playlist.sh  sh  Submits playlist downloading.
2d-unfolding/sbatch_evloop_array.sh  sh  Submits the 2D playlist event-loop array.
2d-unfolding/sbatch_evloop_array_universes.sh  sh  Submits the universe event-loop array.
2d-unfolding/sbatch_evloop_array_universes_full.sh  sh  Submits the full-universe event-loop array.
2d-unfolding/sbatch_final_rollup_full.sh  sh  Submits the full final-results rollup.
2d-unfolding/sbatch_finalize_MEFHC.sh  sh  Submits MEFHC finalization and plotting.
2d-unfolding/sbatch_hadd_MEFHC.sh  sh  Submits MEFHC ROOT merging.
2d-unfolding/sbatch_hadd_MEFHC_universes.sh  sh  Submits MEFHC universe ROOT merging.
2d-unfolding/sbatch_hadd_MEFHC_universes_full.sh  sh  Submits full-universe MEFHC merging.
2d-unfolding/sbatch_hadd_MEFHC_universes_full_safe.sh  sh  Submits guarded full-universe merging.
2d-unfolding/sbatch_hadd_MEFHC_universes_full_v2.sh  sh  Submits the v2 full-universe merge.
2d-unfolding/sbatch_ibu_omnifold_cdelta.sh  sh  Submits the IBU/OmniFold covariance-delta comparison.
2d-unfolding/sbatch_ibu_omnifold_cdelta_gpu.sh  sh  Submits the GPU IBU/OmniFold covariance-delta comparison.
2d-unfolding/sbatch_minos_quality_diag.sh  sh  Submits the MINOS-quality diagnostic.
2d-unfolding/sbatch_negweight_cov_analysis.sh  sh  Submits negative-weight covariance analysis.
2d-unfolding/sbatch_rebuild_1A_universes.sh  sh  Rebuilds playlist-1A universe inputs.
2d-unfolding/sbatch_rebuild_1A_universes_full.sh  sh  Rebuilds full playlist-1A universe inputs.
2d-unfolding/sbatch_runEventLoop_baseline_flux_array.sh  sh  Submits per-playlist baseline-flux event loops.
2d-unfolding/sbatch_unfold_2d_1A_5iter_universes.sh  sh  Submits five-iteration 1A universe unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC.sh  sh  Submits the canonical MEFHC 2D unfold.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootsplit.sh  sh  Submits the five-iteration split-bootstrap unfold.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootstrap.sh  sh  Submits the five-iteration bootstrap unfold.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootstrap_negweight.sh  sh  Submits negative-weight bootstrap unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_bootstrap_scaleup.sh  sh  Submits scaled-up bootstrap unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_seedscan.sh  sh  Submits the five-iteration seed scan.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes.sh  sh  Submits five-iteration universe unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_CV.sh  sh  Submits the universe-matched CV unfold.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full.sh  sh  Submits full-universe MEFHC unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_CV.sh  sh  Submits the full-universe matched-CV unfold.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_negweight.sh  sh  Submits full-universe negative-weight unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh  sh  Submits full-universe purity-target unfolds.
2d-unfolding/sbatch_unfold_2d_MEFHC_8iter.sh  sh  Submits the eight-iteration MEFHC unfold.
2d-unfolding/sbatch_uni_CV_negweight.sh  sh  Submits the negative-weight universe CV.
2d-unfolding/sbatch_uni_CV_puritynew.sh  sh  Submits the purity-target universe CV.
2d-unfolding/sbatch_validate_1A_corrected.sh  sh  Submits corrected playlist-1A validation.
2d-unfolding/seedscan/run_seedscan_backward.sh  sh  Runs the backward seed scan.
2d-unfolding/seedscan/run_seedscan_interactive.sh  sh  Runs the interactive seed scan.
2d-unfolding/seedscan_lgbm/run_seedscan_lgbm_interactive.sh  sh  Runs the interactive LightGBM seed scan.
2d-unfolding/tension_iter/run_iter_lgbm.sh  sh  Runs the LightGBM tension iteration study.
2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh  sh  Submits the playlist-1A unbinned 1D unfold.
2d-unfolding/uq/run_bootstrap_interactive.sh  sh  Runs bootstrap replicas interactively.
2d-unfolding/uq/run_flux_ramp_interactive.sh  sh  Runs the flux-ramp study interactively.
2d-unfolding/uq/run_split_analysis.sh  sh  Runs split-sample uncertainty analysis.
2d-unfolding/uq/run_universe_array_interactive.sh  sh  Runs the universe array interactively.
2d-unfolding/uq/run_universe_omnifile_1A.sh  sh  Builds the playlist-1A universe omnifile.
3d-unfolding/genie/reduce_splines.sh  sh  Reduces GENIE spline inputs.
3d-unfolding/genie/run_eavailW_band.sh  sh  Runs the Eavail/W generator-band workflow.
3d-unfolding/genie/run_parallel_cv.sh  sh  Runs parallel generator CV jobs.
3d-unfolding/genie/run_parallel_fsi.sh  sh  Runs parallel FSI variations.
3d-unfolding/genie/run_parallel_nuwro.sh  sh  Runs parallel NuWro jobs.
3d-unfolding/genie/sbatch_gevgen_mec.sh  sh  Submits GENIE MEC event generation.
3d-unfolding/genie/sbatch_gevgen_mefhc.sh  sh  Submits MEFHC GENIE event generation.
3d-unfolding/genie/sbatch_gibuu_mirror.sh  sh  Submits the GiBUU mirror workflow.
3d-unfolding/genie/sbatch_nuwro_mefhc.sh  sh  Submits MEFHC NuWro production.
3d-unfolding/sbatch_bootstrap_3d.sh  sh  Submits 3D bootstrap replicas.
3d-unfolding/sbatch_evloop_array_3d.sh  sh  Submits the 3D playlist event-loop array.
3d-unfolding/sbatch_evloop_array_3d_universes_full.sh  sh  Submits the full-universe 3D event-loop array.
3d-unfolding/sbatch_hadd_3d_universes_full.sh  sh  Submits full-universe 3D ROOT merging.
3d-unfolding/sbatch_unfold_3d.sh  sh  Submits the canonical 3D unfold.
3d-unfolding/sbatch_unfold_3d_MEFHC_5iter_seedscan.sh  sh  Submits the 3D MEFHC seed scan.
3d-unfolding/sbatch_unfold_3d_MEFHC_5iter_universes_full.sh  sh  Submits full-universe 3D unfolds.
docs/analysis-note/build_all.sh  sh  Builds all analysis-note variants.
docs/analysis-note/make_figures.sh  sh  Regenerates analysis-note figures.
docs/jul-16-presentation/visual-prototypes/presentation-grade/export_frames.sh  sh  Exports presentation prototype frames.
docs/orchestration/gate2_queue_hedge_controller.sh  sh  Controls the Gate-2 queue hedge.
docs/orchestration/make_handoff_bundle.sh  sh  Creates an orchestration handoff bundle.
docs/orchestration/pipeline_post_reset_verifiers.sh  sh  Runs post-reset pipeline verifiers.
docs/orchestration/run_gate2_r4_detached.sh  sh  Launches detached Gate-2 round 4.
docs/orchestration/run_leads.sh  sh  Runs orchestration lead workers.
nd-unfolding/HANDOFF_fps_step3/rootenv.sh  sh  Sets up the handoff ROOT environment.
nd-unfolding/ai1_packed_loop.sh  sh  Runs the packed AI1 loop.
nd-unfolding/boot5d_packed_loop.sh  sh  Runs packed 5D bootstrap work.
nd-unfolding/evloop_bkgaware_packed_loop.sh  sh  Runs packed background-aware event loops.
nd-unfolding/pet/launch_phase7_final.sh  sh  Launches the final PET Phase-7 workflow.
nd-unfolding/pet/run_pet_refresh_interactive.sh  sh  Runs the interactive PET refresh.
nd-unfolding/pet/sbatch_build_bkgsub_input.sh  sh  Submits PET background-subtracted input construction.
nd-unfolding/pet/sbatch_coupled_phi_sweep_delta.sh  sh  Submits the coupled-phi delta sweep.
nd-unfolding/pet/sbatch_csyst_prelim_bkgsub.sh  sh  Submits preliminary PET systematic covariance.
nd-unfolding/pet/sbatch_feature_rank_arms_delta.sh  sh  Submits feature-ranking arms.
nd-unfolding/pet/sbatch_gate2_target_validator.sh  sh  Submits the Gate-2 target validator.
nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh  sh  Submits a PET bootstrap replica.
nd-unfolding/pet/sbatch_pet_clateral_bkgsub.sh  sh  Submits PET lateral background-subtraction work.
nd-unfolding/pet/sbatch_pet_nominal_bkgsub.sh  sh  Submits nominal PET background subtraction.
nd-unfolding/pet/sbatch_pet_smoke.sh  sh  Submits the PET smoke run.
nd-unfolding/pet/sbatch_pet_train_fullcloud.sh  sh  Submits full-cloud PET training.
nd-unfolding/pet/sbatch_pet_train_hvd.sh  sh  Submits HVD PET training.
nd-unfolding/pet/sbatch_pet_xsec.sh  sh  Submits PET cross-section extraction.
nd-unfolding/pet/sbatch_project_fullcloud.sh  sh  Submits full-cloud projection.
nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh  sh  Submits the PET-versus-GBDT refresh.
nd-unfolding/rootenv_sbatch.sh  sh  Sets up the batch ROOT environment.
nd-unfolding/run_4d_replicas_multinode.sh  sh  Runs multinode 4D replicas.
nd-unfolding/run_4d_replicas_packed.sh  sh  Runs packed 4D replicas.
nd-unfolding/run_4d_throws_interactive.sh  sh  Runs 4D throws interactively.
nd-unfolding/run_4d_throws_multinode.sh  sh  Runs multinode 4D throws.
nd-unfolding/run_4d_throws_packed.sh  sh  Runs packed 4D throws.
nd-unfolding/run_4dstatml_interactive.sh  sh  Runs interactive 4D statistical/ML work.
nd-unfolding/run_active_lateral_unfolds_interactive.sh  sh  Runs active-lateral unfolds interactively.
nd-unfolding/run_active_laterals_interactive.sh  sh  Runs active-lateral production interactively.
nd-unfolding/run_adopt_5d.sh  sh  Runs 5D result adoption.
nd-unfolding/run_ai1_combine.sh  sh  Combines AI1 products.
nd-unfolding/run_budget_4d.sh  sh  Builds the 4D uncertainty budget.
nd-unfolding/run_budget_5d.sh  sh  Builds the 5D uncertainty budget.
nd-unfolding/run_eavailW_5d.sh  sh  Runs the 5D Eavail/W projection.
nd-unfolding/run_merge_bkgaware.sh  sh  Runs the background-aware merge.
nd-unfolding/run_p4_standard.sh  sh  Runs the standard Phase-4 workflow.
nd-unfolding/run_q3_sweep_interactive.sh  sh  Runs the q3 sweep interactively.
nd-unfolding/run_rebank_bkgaware.sh  sh  Runs background-aware rebanking.
nd-unfolding/run_task13_interactive.sh  sh  Runs task 13 interactively.
nd-unfolding/sbatch_adopt_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D adoption.
nd-unfolding/sbatch_adopt_5d.sh  sh  Submits 5D adoption.
nd-unfolding/sbatch_adopt_fps.sh  sh  Submits FPS adoption.
nd-unfolding/sbatch_adopt_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS adoption.
nd-unfolding/sbatch_adopt_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS adoption.
nd-unfolding/sbatch_ai1_estimator_scan.sh  sh  Submits the AI1 estimator scan.
nd-unfolding/sbatch_analyze_4d_cov.sh  sh  Submits 4D covariance analysis.
nd-unfolding/sbatch_assemble_4d.sh  sh  Submits 4D product assembly.
nd-unfolding/sbatch_bootstrap_4d.sh  sh  Submits 4D bootstrap replicas.
nd-unfolding/sbatch_bootstrap_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D bootstraps.
nd-unfolding/sbatch_bootstrap_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D bootstraps.
nd-unfolding/sbatch_bootstrap_5d.sh  sh  Submits 5D bootstrap replicas.
nd-unfolding/sbatch_bootstrap_fps.sh  sh  Submits FPS bootstrap replicas.
nd-unfolding/sbatch_bootstrap_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS bootstraps.
nd-unfolding/sbatch_bootstrap_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS bootstraps.
nd-unfolding/sbatch_combine_4d_budget.sh  sh  Submits 4D budget combination.
nd-unfolding/sbatch_combine_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D combination.
nd-unfolding/sbatch_combine_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D combination.
nd-unfolding/sbatch_combine_4d_statml.sh  sh  Submits 4D statistical/ML combination.
nd-unfolding/sbatch_combine_5d_budget.sh  sh  Submits 5D budget combination.
nd-unfolding/sbatch_combine_boot_fps.sh  sh  Submits FPS bootstrap combination.
nd-unfolding/sbatch_combine_boot_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS bootstrap combination.
nd-unfolding/sbatch_combine_boot_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS bootstrap combination.
nd-unfolding/sbatch_combine_split_fps.sh  sh  Submits FPS split-sample combination.
nd-unfolding/sbatch_combine_split_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS split combination.
nd-unfolding/sbatch_combine_split_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS split combination.
nd-unfolding/sbatch_coverage_fps.sh  sh  Submits FPS coverage work.
nd-unfolding/sbatch_dump_fps_inputs.sh  sh  Submits FPS input dumping.
nd-unfolding/sbatch_eavailW_cov.sh  sh  Submits Eavail/W covariance construction.
nd-unfolding/sbatch_eavailW_cov_wlat.sh  sh  Submits Eavail/W covariance with laterals.
nd-unfolding/sbatch_eavail_sig.sh  sh  Submits Eavail significance calculation.
nd-unfolding/sbatch_evloop_1A_fps.sh  sh  Submits the playlist-1A FPS event loop.
nd-unfolding/sbatch_evloop_array_4d.sh  sh  Submits the 4D event-loop array.
nd-unfolding/sbatch_evloop_array_4d_universes_full.sh  sh  Submits the full-universe 4D event-loop array.
nd-unfolding/sbatch_evloop_array_5d.sh  sh  Submits the 5D event-loop array.
nd-unfolding/sbatch_evloop_array_5d_active_laterals.sh  sh  Submits standard 5D active-lateral event loops.
nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps.sh  sh  Submits FPS 5D active-lateral event loops.
nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps_cpu.sh  sh  Submits CPU FPS active-lateral event loops.
nd-unfolding/sbatch_evloop_array_5d_bkgaware_gpu.sh  sh  Submits GPU background-aware 5D event loops.
nd-unfolding/sbatch_evloop_array_5d_fps.sh  sh  Submits the 5D FPS event-loop array.
nd-unfolding/sbatch_evloop_array_5d_fps_universes_full.sh  sh  Submits full-universe 5D FPS event loops.
nd-unfolding/sbatch_evloop_array_5d_universes_full.sh  sh  Submits full-universe 5D event loops.
nd-unfolding/sbatch_evloop_array_pointcloud_fps.sh  sh  Submits FPS point-cloud event loops.
nd-unfolding/sbatch_excess_eavail_W.sh  sh  Submits excess-Eavail/W analysis.
nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh  sh  Submits GPU background-aware 5D finalization.
nd-unfolding/sbatch_fps_budget.sh  sh  Submits the FPS uncertainty budget.
nd-unfolding/sbatch_fps_budget_corrected_cpu.sh  sh  Submits the corrected-CPU FPS budget.
nd-unfolding/sbatch_fps_budget_corrected_gpu.sh  sh  Submits the corrected-GPU FPS budget.
nd-unfolding/sbatch_fps_cov.sh  sh  Submits FPS covariance construction.
nd-unfolding/sbatch_fps_coverage_analysis.sh  sh  Submits FPS coverage analysis.
nd-unfolding/sbatch_fps_envelope.sh  sh  Submits FPS prior-envelope construction.
nd-unfolding/sbatch_fps_genie_refix.sh  sh  Submits the FPS GENIE refix.
nd-unfolding/sbatch_fps_hidden_closure.sh  sh  Submits FPS hidden closure.
nd-unfolding/sbatch_fps_mask.sh  sh  Submits FPS reported-mask construction.
nd-unfolding/sbatch_fps_mefhc.sh  sh  Submits MEFHC FPS production.
nd-unfolding/sbatch_fps_pilot.sh  sh  Submits the FPS pilot.
nd-unfolding/sbatch_fps_reunfold_5d.sh  sh  Submits 5D FPS prior reunfolding.
nd-unfolding/sbatch_fps_reunfold_5d_xps.sh  sh  Submits XPS 5D FPS prior reunfolding.
nd-unfolding/sbatch_fps_reunfold_5d_xps2.sh  sh  Submits XPS2 5D FPS prior reunfolding.
nd-unfolding/sbatch_hadd_4d_universes_full.sh  sh  Submits full-universe 4D ROOT merging.
nd-unfolding/sbatch_hadd_5d_fps_universes_full.sh  sh  Submits full-universe 5D FPS ROOT merging.
nd-unfolding/sbatch_hadd_5d_universes_full.sh  sh  Submits full-universe 5D ROOT merging.
nd-unfolding/sbatch_hadd_active_fps.sh  sh  Submits active-FPS ROOT merging.
nd-unfolding/sbatch_hadd_active_fps_cpu.sh  sh  Submits CPU active-FPS ROOT merging.
nd-unfolding/sbatch_hadd_pc_fps.sh  sh  Submits FPS point-cloud ROOT merging.
nd-unfolding/sbatch_hadd_pc_fullcloud.sh  sh  Submits full-cloud ROOT merging.
nd-unfolding/sbatch_hadd_unfold_4d.sh  sh  Submits 4D merge and unfold.
nd-unfolding/sbatch_hadd_unfold_5d.sh  sh  Submits 5D merge and unfold.
nd-unfolding/sbatch_nn_dump_5d.sh  sh  Submits 5D neural-network input dumping.
nd-unfolding/sbatch_nn_dump_fps_5d.sh  sh  Submits 5D FPS neural-network input dumping.
nd-unfolding/sbatch_nn_dump_fps_5d_xps.sh  sh  Submits XPS FPS neural-network input dumping.
nd-unfolding/sbatch_nn_dump_fps_5d_xps2.sh  sh  Submits XPS2 FPS neural-network input dumping.
nd-unfolding/sbatch_nn_dump_lgbm.sh  sh  Submits LightGBM input dumping.
nd-unfolding/sbatch_nn_gpu.sh  sh  Submits GPU neural-network unfolding.
nd-unfolding/sbatch_npz_fullcloud.sh  sh  Submits full-cloud NPZ construction.
nd-unfolding/sbatch_npz_pc_fps.sh  sh  Submits FPS point-cloud NPZ construction.
nd-unfolding/sbatch_npz_pc_fps_xps.sh  sh  Submits XPS FPS point-cloud NPZ construction.
nd-unfolding/sbatch_npz_pc_fps_xps2.sh  sh  Submits XPS2 FPS point-cloud NPZ construction.
nd-unfolding/sbatch_pet_conv_fps_xps2.sh  sh  Submits XPS2 FPS PET convergence work.
nd-unfolding/sbatch_pet_lateral.sh  sh  Submits PET lateral-systematic work.
nd-unfolding/sbatch_pet_lateral_5d.sh  sh  Submits 5D PET lateral-systematic work.
nd-unfolding/sbatch_pet_lateral_band.sh  sh  Submits PET lateral-band construction.
nd-unfolding/sbatch_pet_rebank.sh  sh  Submits PET rebanking.
nd-unfolding/sbatch_pet_systematics.sh  sh  Submits PET systematic work.
nd-unfolding/sbatch_pet_systematics_5d.sh  sh  Submits 5D PET systematic work.
nd-unfolding/sbatch_pet_train_fps_delta.sh  sh  Submits delta-mode FPS PET training.
nd-unfolding/sbatch_pet_train_fps_hvd.sh  sh  Submits HVD FPS PET training.
nd-unfolding/sbatch_pet_uthrow_5d.sh  sh  Submits 5D PET universe throws.
nd-unfolding/sbatch_pilot_cv_check_4d_gpu.sh  sh  Submits the GPU 4D pilot-CV check.
nd-unfolding/sbatch_project_5d_to_4d_candidate_gpu.sh  sh  Submits GPU 5D-to-4D projection.
nd-unfolding/sbatch_seedscan_split.sh  sh  Submits the generic split seed scan.
nd-unfolding/sbatch_seedscan_split_4d.sh  sh  Submits the 4D split seed scan.
nd-unfolding/sbatch_seedscan_split_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D split seed scans.
nd-unfolding/sbatch_seedscan_split_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D split seed scans.
nd-unfolding/sbatch_seedscan_split_5d.sh  sh  Submits the 5D split seed scan.
nd-unfolding/sbatch_seedscan_split_fps.sh  sh  Submits the FPS split seed scan.
nd-unfolding/sbatch_seedscan_split_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS split seed scans.
nd-unfolding/sbatch_seedscan_split_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS split seed scans.
nd-unfolding/sbatch_sweep_bank_5d_dump.sh  sh  Submits 5D sweep-bank dumping.
nd-unfolding/sbatch_sweep_bank_5d_dump_bkgaware_gpu.sh  sh  Submits GPU background-aware 5D sweep-bank dumping.
nd-unfolding/sbatch_sweep_bank_5d_run.sh  sh  Submits 5D sweep-bank execution.
nd-unfolding/sbatch_sweep_bank_5d_run_bkgaware_gpu.sh  sh  Submits GPU background-aware 5D sweep-bank execution.
nd-unfolding/sbatch_sweep_bank_array.sh  sh  Submits the sweep-bank array.
nd-unfolding/sbatch_sweep_bank_dump.sh  sh  Submits generic sweep-bank dumping.
nd-unfolding/sbatch_sweep_bank_run.sh  sh  Submits generic sweep-bank execution.
nd-unfolding/sbatch_td_q3.sh  sh  Submits q3 training-data dumping.
nd-unfolding/sbatch_unbinned_gof.sh  sh  Submits unbinned goodness-of-fit analysis.
nd-unfolding/sbatch_unfold_4d_lateral.sh  sh  Submits a 4D lateral unfold.
nd-unfolding/sbatch_unfold_4d_rerun.sh  sh  Submits a 4D unfold rerun.
nd-unfolding/sbatch_unfold_4d_universes_full.sh  sh  Submits full-universe 4D unfolds.
nd-unfolding/sbatch_unfold_4d_validate_universe.sh  sh  Submits 4D universe validation.
nd-unfolding/sbatch_unfold_5d_detector.sh  sh  Submits the 5D detector-systematic sweep.
nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh  sh  Submits GPU background-aware detector unfolds.
nd-unfolding/sbatch_unfold_ascencio_fine.sh  sh  Submits the fine-grid Ascencio unfold.
nd-unfolding/sbatch_unfold_fps_universes_full.sh  sh  Submits full-universe FPS unfolds.
nd-unfolding/sbatch_unified_throw.sh  sh  Submits unified universe throws.
nd-unfolding/sbatch_uthrow_block.sh  sh  Submits universe-throw block construction.
nd-unfolding/sbatch_uthrow_block_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D throw blocks.
nd-unfolding/sbatch_uthrow_block_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D throw blocks.
nd-unfolding/sbatch_uthrow_block_5d.sh  sh  Submits 5D throw blocks.
nd-unfolding/sbatch_uthrow_block_fps.sh  sh  Submits FPS throw blocks.
nd-unfolding/sbatch_uthrow_block_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS throw blocks.
nd-unfolding/sbatch_uthrow_block_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS throw blocks.
nd-unfolding/sbatch_uthrow_combine.sh  sh  Submits universe-throw combination.
nd-unfolding/sbatch_uthrow_combine_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D throw combination.
nd-unfolding/sbatch_uthrow_combine_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D throw combination.
nd-unfolding/sbatch_uthrow_combine_5d.sh  sh  Submits 5D throw combination.
nd-unfolding/sbatch_uthrow_combine_fps.sh  sh  Submits FPS throw combination.
nd-unfolding/sbatch_uthrow_combine_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS throw combination.
nd-unfolding/sbatch_uthrow_combine_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS throw combination.
nd-unfolding/sbatch_uthrow_cov.sh  sh  Submits universe-throw covariance construction.
nd-unfolding/sbatch_uthrow_cov_4d_corrected_cpu.sh  sh  Submits corrected-CPU 4D throw covariance.
nd-unfolding/sbatch_uthrow_cov_4d_corrected_gpu.sh  sh  Submits corrected-GPU 4D throw covariance.
nd-unfolding/sbatch_uthrow_cov_fps.sh  sh  Submits FPS throw covariance.
nd-unfolding/sbatch_uthrow_cov_fps_corrected_cpu.sh  sh  Submits corrected-CPU FPS throw covariance.
nd-unfolding/sbatch_uthrow_cov_fps_corrected_gpu.sh  sh  Submits corrected-GPU FPS throw covariance.
nd-unfolding/sbatch_uthrow_dump.sh  sh  Submits universe-throw input dumping.
nd-unfolding/sbatch_uthrow_dump_5d.sh  sh  Submits 5D universe-throw input dumping.
nd-unfolding/sbatch_uthrow_dump_fps.sh  sh  Submits FPS universe-throw input dumping.
nd-unfolding/sbatch_uthrow_dump_rebank.sh  sh  Submits rebanked universe-throw dumping.
nd-unfolding/sbatch_uthrow_run.sh  sh  Submits universe-throw execution.
nd-unfolding/sbatch_uthrow_run_5d.sh  sh  Submits 5D universe-throw execution.
nd-unfolding/smoke_W.sh  sh  Runs the W-variable smoke check.
nd-unfolding/sweep_run_bkgaware_packed_loop.sh  sh  Runs packed background-aware sweep-bank work.
nd-unfolding/uq_fps/corrected/supervise_fps_uq.sh  sh  Supervises corrected FPS uncertainty jobs.
2d-unfolding/HANDOFF_bkg_negweight/compare_bkg_modes.py  py-entrypoint  Compares purity and negative-weight background-subtraction modes.
2d-unfolding/HANDOFF_bkg_negweight/negweight_toy.py  py-entrypoint  Runs a signed-weight LightGBM background-subtraction toy.
2d-unfolding/binned_study/scripts/plotHist_binned.py  py-entrypoint  Plots binned study histograms.
2d-unfolding/binned_study/scripts/plot_gaussian_style_ptmu_binned.py  py-entrypoint  Produces Gaussian-style binned pTmu plots.
2d-unfolding/binned_study/scripts/trace_binned_omnifold.py  py-entrypoint  Traces the binned OmniFold algorithm step by step.
2d-unfolding/combine_flux_MEFHC.py  py-entrypoint  Builds the POT-weighted MEFHC flux histogram.
2d-unfolding/normalize_xsec_shape.py  py-entrypoint  Builds self-normalized 2D cross-section shapes.
2d-unfolding/plot_2d_paper_comparison_shape.py  py-entrypoint  Plots normalized 2D paper-comparison slices and pulls.
2d-unfolding/plot_closure_2d.py  py-entrypoint  Plots playlist-1A 2D closure diagnostics.
2d-unfolding/unbinned_1d_study/ptmu_closure_iteration_study.py  py-entrypoint  Runs the pTmu closure and iteration study.
2d-unfolding/uq/_ours_only_chi2.py  py-entrypoint  Computes an OmniFold-only covariance chi-square.
2d-unfolding/uq/_univ_weight_stats.py  py-entrypoint  Summarizes per-band universe-weight variations.
2d-unfolding/uq/bottom_line_test.py  py-entrypoint  Runs the 2D/3D bottom-line measurement test.
2d-unfolding/uq/build_flux_universe_band.py  py-entrypoint  Builds the POT-weighted universe flux band.
2d-unfolding/uq/classifier_calibration.py  py-entrypoint  Studies classifier calibration and GBDT/NN robustness.
2d-unfolding/uq/closure/closure_alt_model.py  py-entrypoint  Runs alternative-model closure.
2d-unfolding/uq/closure/closure_hidden_var.py  py-entrypoint  Runs hidden-variable closure.
2d-unfolding/uq/coverage_toys.py  py-entrypoint  Evaluates coverage from toy Monte Carlo.
2d-unfolding/uq/ensemble_mean_cv.py  py-entrypoint  Computes an ensemble-mean CV and ML-stochasticity audit.
2d-unfolding/uq/gen_universe_list.py  py-entrypoint  Enumerates universe branches into a band/index list.
2d-unfolding/uq/rederive_flux_muonE_cross.py  py-entrypoint  Rederives the flux/muon-energy covariance cross-block.
2d-unfolding/uq/rescale_flux_universes.py  py-entrypoint  Rescales 2D universe products using universe-specific fluxes.
2d-unfolding/uq/verify_matcorr_vs_mnvh1d.py  py-entrypoint  Compares covariance construction with MnvH1D.
2d-unfolding/uq/verify_universe_omnifile.py  py-entrypoint  Verifies a universe-enabled omnifile.
3d-unfolding/build_bootstrap_band_3d.py  py-entrypoint  Builds the 3D statistical band from bootstrap replicas.
3d-unfolding/genie/compare_ascencio_eavail.py  py-entrypoint  Compares Eavail with the Ascencio low-q3 result.
3d-unfolding/genie/fsi_variation_xsec3d.py  py-entrypoint  Builds 3D cross sections for GENIE FSI variations.
3d-unfolding/genie/genie_mec_to_xsec3d.py  py-entrypoint  Histograms GENIE MEC events into the 3D cross section.
3d-unfolding/genie/gibuu_to_xsec3d.py  py-entrypoint  Histograms GiBUU events into the 3D cross section.
3d-unfolding/genie/gibuu_to_xsec_eavailW.py  py-entrypoint  Histograms GiBUU events into Eavail/W.
3d-unfolding/genie/make_flux_for_genie.py  py-entrypoint  Converts the MINERvA flux into a GENIE-readable TH1D.
3d-unfolding/genie/model_tune_xsec3d.py  py-entrypoint  Extracts the MINERvA Tune v1 3D prediction.
3d-unfolding/genie/nuwro_to_xsec3d.py  py-entrypoint  Histograms NuWro events into the 3D cross section.
3d-unfolding/genie/overlay_generators.py  py-entrypoint  Overlays generator predictions on the 3D result.
3d-unfolding/genie/write_combined_splitml.py  py-entrypoint  Writes a 3D covariance including split-sample ML uncertainty.
3d-unfolding/uq_3d/build_bootstrap_cov_3d.py  py-entrypoint  Builds 3D statistical covariance from bootstrap replicas.
docs/orchestration/codex-mcp-account.py  py-entrypoint  Starts Codex MCP with a named account home.
docs/orchestration/test_agentctl.py  py-entrypoint  Runs the agentctl test module directly.
docs/orchestration/test_generate_live_state.py  py-entrypoint  Runs the live-state-generation test module directly.
docs/orchestration/test_slurm_array_status.py  py-entrypoint  Runs the SLURM-array-status test module directly.
docs/orchestration/test_usagectl.py  py-entrypoint  Runs the usagectl test module directly.
docs/orchestration/test_wakerctl.py  py-entrypoint  Runs the wakerctl test module directly.
docs/orchestration/test_watch_slurm_array_resume.py  py-entrypoint  Runs the array-resume watcher test module directly.
lib/enumerate_backfill_families.py  py-entrypoint  Enumerates artifact families needing completion-marker backfill.
nd-unfolding/HANDOFF_fps_step3/stage2_anchor_check.py  py-entrypoint  Checks XPS2 against the standard phase-space anchors.
nd-unfolding/active_universe_5d/interface_smoke/p2_validate.py  py-entrypoint  Validates active-universe smoke output and metadata.
nd-unfolding/adopt_active_lateral_fps.py  py-entrypoint  Adopts the active-lateral FPS covariance block.
nd-unfolding/adopt_unified_fps.py  py-entrypoint  Adopts the final unified-throw FPS covariance.
nd-unfolding/assemble_bank_4d_from5d.py  py-entrypoint  Assembles a 4D throw bank from surviving 5D throws.
nd-unfolding/assemble_gbdt5d_adopted.py  py-entrypoint  Assembles the adopted GBDT 5D covariance.
nd-unfolding/audit_merged_fps.py  py-entrypoint  Audits merged FPS endpoints before unfolding.
nd-unfolding/bkg_channel_split.py  py-entrypoint  Splits genuine and fake background channels.
nd-unfolding/build_fps_prior_genie_5d.py  py-entrypoint  Builds the bare-GENIE 5D FPS prior.
nd-unfolding/build_fps_prior_nuwro_5d.py  py-entrypoint  Builds the NuWro-shaped 5D FPS prior.
nd-unfolding/combine_seedscan_split.py  py-entrypoint  Combines split seed scans into a CV and ML covariance.
nd-unfolding/compare_ascencio_fine.py  py-entrypoint  Compares against the fine-grid Ascencio result.
nd-unfolding/compare_ascencio_q3.py  py-entrypoint  Compares the 4D result with the low-q3 release.
nd-unfolding/compare_le_evolution.py  py-entrypoint  Compares low- and medium-energy beam shapes.
nd-unfolding/compare_mlsplit_combined.py  py-entrypoint  Measures the impact of split-sample ML covariance.
nd-unfolding/coverage_valid_nd.py  py-entrypoint  Evaluates N-D split-sample truth containment.
nd-unfolding/dump_w_source_fps.py  py-entrypoint  Builds the FPS W-source array for PET.
nd-unfolding/ensemble_cv.py  py-entrypoint  Builds an ensemble-mean central value.
nd-unfolding/fps_3prior_envelope_5d.py  py-entrypoint  Builds the 5D FPS three-prior envelope.
nd-unfolding/fps_build_control_manifest.py  py-entrypoint  Builds the FPS control provenance manifest.
nd-unfolding/p4_lateral_replace.py  py-entrypoint  Replaces the standard Phase-4 lateral covariance component.
nd-unfolding/pet/assemble_cretrain.py  py-entrypoint  Assembles the Phase-7 retraining covariance.
nd-unfolding/pet/check_step1_class_ratio.py  py-entrypoint  Measures the step-1 class ratio.
nd-unfolding/pet/combine_cml_bkgsub.py  py-entrypoint  Builds PET ML covariance from crossed seeds.
nd-unfolding/pet/combine_cstat_bkgsub.py  py-entrypoint  Builds corrected PET statistical covariance.
nd-unfolding/pet/demo_b5_refiner_feature_space.py  py-entrypoint  Demonstrates refiner training and cloud-space consumption.
nd-unfolding/pet/feature_rank_prep.py  py-entrypoint  Prepares the event-feature ranking cache.
nd-unfolding/pet/feature_rank_summarize.py  py-entrypoint  Summarizes feature-ranking arms.
nd-unfolding/pet/floor_diagnostic_bkgsub.py  py-entrypoint  Diagnoses the corrected PET GPU floor.
nd-unfolding/pet/floor_gpu_nondeterminism.py  py-entrypoint  Measures PET GPU nondeterminism.
nd-unfolding/pet/fps_census.py  py-entrypoint  Produces the FPS denominator, miss, and acceptance census.
nd-unfolding/pet/pet_vs_gbdt_uncertainty_5d.py  py-entrypoint  Compares PET and GBDT 5D per-bin uncertainties.
nd-unfolding/pet/pet_vs_gbdt_uncertainty_5d_unified.py  py-entrypoint  Compares unified-throw PET and GBDT uncertainties.
nd-unfolding/pet/plot_pet_representation_schematic.py  py-entrypoint  Draws the PET event-representation schematic.
nd-unfolding/pet/smoke_bkgsub_extraction.py  py-entrypoint  Runs end-to-end PET background-subtraction extraction smoke.
nd-unfolding/pet/smoke_fullevent_fps.py  py-entrypoint  Runs a full-event FPS smoke check.
nd-unfolding/pet/smoke_fullevent_tf.py  py-entrypoint  Runs the TensorFlow full-event interface smoke check.
nd-unfolding/pet_conv_check_5d.py  py-entrypoint  Evaluates the 5D PET convergence curve.
nd-unfolding/q3_vs_ascencio_metrics.py  py-entrypoint  Quantifies differences from the Ascencio result.
nd-unfolding/tests/test_b4_gating.py  py-entrypoint  Runs B-4 gating tests directly.
nd-unfolding/tests/test_coupled_phi_guards.py  py-entrypoint  Runs coupled-phi guard tests directly.
nd-unfolding/tests/test_flux_universe_fix.py  py-entrypoint  Runs flux-universe normalization tests directly.
nd-unfolding/tests/test_fps_cli_integration.py  py-entrypoint  Runs FPS CLI integration tests directly.
nd-unfolding/tests/test_fps_provenance.py  py-entrypoint  Runs FPS provenance tests directly.
nd-unfolding/tests/test_fullevent_dump_contract.py  py-entrypoint  Runs full-event dump-contract tests directly.
nd-unfolding/tests/test_fullevent_extract.py  py-entrypoint  Runs full-event extractor tests directly.
nd-unfolding/tests/test_fullevent_fps.py  py-entrypoint  Runs full-event FPS tests directly.
nd-unfolding/tests/test_fullevent_schema.py  py-entrypoint  Runs full-event schema tests directly.
nd-unfolding/tests/test_g2_dump_branch.py  py-entrypoint  Runs G2 dump-branch tests directly.
nd-unfolding/tests/test_g2_guards_collected.py  py-entrypoint  Checks that G2 guards are collected.
nd-unfolding/tests/test_gate2_target_runtime.py  py-entrypoint  Runs Gate-2 runtime tests directly.
nd-unfolding/tests/test_nd_branch_binding_fails_closed.py  py-entrypoint  Runs N-D branch-binding failure tests directly.
nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py  py-entrypoint  Tests the Phase-3 FPS full-event launcher directly.
nd-unfolding/tests/test_p3f_pet_fullevent_validator.py  py-entrypoint  Tests the Phase-3 FPS validator directly.
nd-unfolding/tests/test_p3s_historical.py  py-entrypoint  Runs Phase-3 historical-provenance tests directly.
nd-unfolding/tests/test_p4_repair.py  py-entrypoint  Runs standard Phase-4 repair tests directly.
nd-unfolding/tests/test_pet_assembly.py  py-entrypoint  Runs PET covariance-assembly tests directly.
nd-unfolding/tests/test_pet_bkgsub_input.py  py-entrypoint  Runs PET background-subtracted-input tests directly.
nd-unfolding/tests/test_pet_fullevent_nominal_launcher.py  py-entrypoint  Tests the PET nominal launcher directly.
nd-unfolding/tests/test_pet_nominal_gate4_validator.py  py-entrypoint  Tests the Gate-4 nominal validator directly.
nd-unfolding/tests/test_phase7.py  py-entrypoint  Runs Phase-7 mapping and materiality tests directly.
nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py  py-entrypoint  Runs corrected FPS uncertainty tests directly.
nd-unfolding/validate_combined_4d.py  py-entrypoint  Validates combined corrected 4D covariance.
MINERvA101/MINERvA-101-Cross-Section/runEventLoopMod.cpp  cpp-main  Implements the modified runEventLoop executable.
MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold_OLD.cpp  cpp-main  Implements the older archived OmniFold event loop.
MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold_OLDEST.cpp  cpp-main  Implements the oldest archived OmniFold event loop.
```

## No row, no test, but called by something — full list

```text
2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh  sh  2d-unfolding/sbatch_negweight_cov_analysis.sh
2d-unfolding/download_playlist.sh  sh  2d-unfolding/sbatch_download_playlist.sh
2d-unfolding/sbatch_build.sh  sh  nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh
2d-unfolding/uq/final_rollup_full.sh  sh  2d-unfolding/sbatch_final_rollup_full.sh
3d-unfolding/genie/run_fsi_reweight.sh  sh  3d-unfolding/genie/run_parallel_fsi.sh
3d-unfolding/genie/run_gevgen.sh  sh  3d-unfolding/genie/run_parallel_cv.sh; 3d-unfolding/genie/sbatch_gevgen_mec.sh; 3d-unfolding/genie/sbatch_gevgen_mefhc.sh
3d-unfolding/genie/run_nuwro.sh  sh  3d-unfolding/genie/run_parallel_nuwro.sh; 3d-unfolding/genie/sbatch_nuwro_mefhc.sh
3d-unfolding/genie/sbatch_gibuu_mefhc.sh  sh  3d-unfolding/genie/sbatch_gibuu_mirror.sh
3d-unfolding/genie/setup_genie.sh  sh  3d-unfolding/genie/run_fsi_reweight.sh; 3d-unfolding/genie/run_gevgen.sh; 3d-unfolding/genie/run_parallel_cv.sh
3d-unfolding/genie/setup_gibuu.sh  sh  3d-unfolding/genie/sbatch_gibuu_mefhc.sh; 3d-unfolding/genie/sbatch_gibuu_mirror.sh
3d-unfolding/genie/setup_nuwro.sh  sh  3d-unfolding/genie/run_nuwro.sh
alloc_run.sh  sh  docs/orchestration/gate2_queue_hedge_controller.sh; docs/orchestration/run_gate2_r4_detached.sh; nd-unfolding/run_task13_interactive.sh; nd-unfolding/uq_fps/corrected/supervise_fps_uq.sh
nd-unfolding/pet/run_gate2_target_validator.sh  sh  docs/orchestration/gate2_queue_hedge_controller.sh; docs/orchestration/run_gate2_r4_detached.sh; nd-unfolding/pet/sbatch_gate2_target_validator.sh
nd-unfolding/pet/sbatch_pc_downstream.sh  sh  nd-unfolding/pet/run_pet_refresh_interactive.sh; nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh
nd-unfolding/pet/sbatch_pet_compare.sh  sh  nd-unfolding/pet/run_pet_refresh_interactive.sh; nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh
nd-unfolding/pet/sbatch_pet_train.sh  sh  nd-unfolding/pet/run_pet_refresh_interactive.sh; nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh
nd-unfolding/pet/sbatch_phase7_retrain.sh  sh  nd-unfolding/pet/launch_phase7_final.sh
nd-unfolding/run_pc_evloop_interactive.sh  sh  nd-unfolding/pet/run_pet_refresh_interactive.sh
nd-unfolding/sbatch_evloop_array_pointcloud.sh  sh  nd-unfolding/pet/sbatch_refresh_pet_vs_gbdt.sh
nd-unfolding/sbatch_uthrow_block_4d.sh  sh  nd-unfolding/sbatch_assemble_4d.sh
nd-unfolding/sbatch_uthrow_combine_4d.sh  sh  nd-unfolding/sbatch_assemble_4d.sh
nd-unfolding/sbatch_uthrow_cov_4d.sh  sh  nd-unfolding/sbatch_assemble_4d.sh
nd-unfolding/uq_fps/corrected/run_fps_uq_packed.sh  sh  nd-unfolding/uq_fps/corrected/supervise_fps_uq.sh
start_alloc.sh  sh  alloc_run.sh
2d-unfolding/binned_study/scripts/unfold_ptmu_omnifold_binned.py  py-entrypoint  2d-unfolding/binned_study/scripts/trace_binned_omnifold.py
2d-unfolding/compare_to_models.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/compare_to_paper_fullcov.py  py-entrypoint  2d-unfolding/compare_to_models.py; 2d-unfolding/diagnose_tension.py; 2d-unfolding/sbatch_analyze_MEFHC_final.sh; 2d-unfolding/sbatch_analyze_MEFHC_universes.sh; 2d-unfolding/sbatch_finalize_MEFHC.sh; 2d-unfolding/uq/final_rollup_full.sh; 3d-unfolding/sbatch_unfold_3d.sh; docs/analysis-note/make_figures.sh
2d-unfolding/compare_to_paper_interior.py  py-entrypoint  2d-unfolding/sbatch_finalize_MEFHC.sh
2d-unfolding/diagnose_tension.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/ibu_1d_projection/build_1d_ibu_inputs.py  py-entrypoint  2d-unfolding/ibu_1d_projection/sbatch_ibu_1d_projection.sh
2d-unfolding/ibu_1d_projection/plot_ibu_1d_proj_vs_omnifold.py  py-entrypoint  2d-unfolding/ibu_1d_projection/sbatch_ibu_1d_projection.sh
2d-unfolding/ibu_omnifold_paired_cdelta.py  py-entrypoint  2d-unfolding/sbatch_ibu_omnifold_cdelta.sh; 2d-unfolding/sbatch_ibu_omnifold_cdelta_gpu.sh
2d-unfolding/minos_quality_diagnostic.py  py-entrypoint  2d-unfolding/sbatch_minos_quality_diag.sh
2d-unfolding/plot_2d_cross_section.py  py-entrypoint  2d-unfolding/plot_2d_paper_comparison.py; 2d-unfolding/plot_2d_threeway_fig13.py; 2d-unfolding/sbatch_finalize_MEFHC.sh; docs/analysis-note/make_figures.sh
2d-unfolding/plot_2d_paper_comparison.py  py-entrypoint  2d-unfolding/sbatch_finalize_MEFHC.sh; docs/analysis-note/make_figures.sh
2d-unfolding/plot_2d_threeway_fig13.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/plot_efficiency_fig5_style.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/plot_negweight_ratio.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/seedscan/analyze_seedscan.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/unbinned_1d_study/plot_gaussian_style_ptmu_unbinned.py  py-entrypoint  2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
2d-unfolding/unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py  py-entrypoint  2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
2d-unfolding/uq/analyze_universes.py  py-entrypoint  2d-unfolding/sbatch_analyze_MEFHC_final.sh; 2d-unfolding/sbatch_analyze_MEFHC_universes.sh; 2d-unfolding/uq/final_rollup_full.sh; 2d-unfolding/uq/plot_uncertainty_fig6_7_style.py
2d-unfolding/uq/analyze_uq.py  py-entrypoint  2d-unfolding/sbatch_analyze_MEFHC_final.sh; 2d-unfolding/uq/final_rollup_full.sh; 2d-unfolding/uq/run_split_analysis.sh
2d-unfolding/uq/closure/closure_truth_reweight.py  py-entrypoint  2d-unfolding/sbatch_closure_shapes_20.sh
2d-unfolding/uq/compare_split_bootstrap.py  py-entrypoint  2d-unfolding/uq/run_split_analysis.sh
2d-unfolding/uq/hadd_universes_full.py  py-entrypoint  2d-unfolding/sbatch_hadd_MEFHC_universes_full_safe.sh; 2d-unfolding/sbatch_hadd_MEFHC_universes_full_v2.sh; 3d-unfolding/sbatch_hadd_3d_universes_full.sh; nd-unfolding/merge_active_endpoints.sh; nd-unfolding/run_merge_bkgaware.sh; nd-unfolding/run_p4_merge_audit_std.sh; nd-unfolding/run_task13_interactive.sh; nd-unfolding/sbatch_hadd_4d_universes_full.sh; nd-unfolding/sbatch_hadd_5d_fps_universes_full.sh; nd-unfolding/sbatch_hadd_5d_universes_full.sh; nd-unfolding/sbatch_hadd_active_fps.sh; nd-unfolding/sbatch_hadd_active_fps_cpu.sh; nd-unfolding/sbatch_merge_active_array.sh
2d-unfolding/uq/plot_bootstrap_figs.py  py-entrypoint  docs/analysis-note/make_figures.sh
2d-unfolding/uq/plot_uncertainty_fig6_7_style.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/genie/compare_3d_fullcov.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/genie/compare_mec_eavail.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/genie/gen_to_xsec_eavailW.py  py-entrypoint  3d-unfolding/genie/run_eavailW_band.sh
3d-unfolding/genie/genie_to_xsec3d.py  py-entrypoint  3d-unfolding/genie/fsi_variation_xsec3d.py; 3d-unfolding/genie/gen_to_xsec_eavailW.py; 3d-unfolding/genie/genie_mec_to_xsec3d.py; 3d-unfolding/genie/mode_decomp_eavail.py
3d-unfolding/genie/gst_reader.py  py-entrypoint  3d-unfolding/genie/gen_to_xsec_eavailW.py; 3d-unfolding/genie/genie_to_xsec3d.py
3d-unfolding/genie/mode_decomp_eavail.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/genie/nuwro_to_xsec_eavailW.py  py-entrypoint  3d-unfolding/genie/run_eavailW_band.sh
3d-unfolding/genie/overlay_eavailW_band.py  py-entrypoint  3d-unfolding/genie/run_eavailW_band.sh; docs/analysis-note/make_figures.sh
3d-unfolding/genie/overlay_generators_band.py  py-entrypoint  3d-unfolding/genie/compare_ascencio_eavail.py; 3d-unfolding/genie/compare_mec_eavail.py; 3d-unfolding/genie/mode_decomp_eavail.py; docs/analysis-note/make_figures.sh
3d-unfolding/plot_eavail_spectrum.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/plot_minerva_landscape.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/unfold_3d_omnifold_unbinned.py  py-entrypoint  3d-unfolding/genie/compare_mec_eavail.py; 3d-unfolding/genie/fsi_variation_xsec3d.py; 3d-unfolding/genie/gen_to_xsec_eavailW.py; 3d-unfolding/genie/genie_mec_to_xsec3d.py; 3d-unfolding/genie/genie_to_xsec3d.py; 3d-unfolding/genie/gibuu_to_xsec3d.py; 3d-unfolding/genie/gibuu_to_xsec_eavailW.py; 3d-unfolding/genie/mode_decomp_eavail.py; 3d-unfolding/genie/model_tune_xsec3d.py; 3d-unfolding/genie/nuwro_to_xsec3d.py; 3d-unfolding/genie/nuwro_to_xsec_eavailW.py; 3d-unfolding/sbatch_bootstrap_3d.sh; 3d-unfolding/sbatch_unfold_3d.sh; 3d-unfolding/sbatch_unfold_3d_MEFHC_5iter_seedscan.sh; 3d-unfolding/sbatch_unfold_3d_MEFHC_5iter_universes_full.sh
3d-unfolding/uq_3d/analyze_universes_3d.py  py-entrypoint  3d-unfolding/uq_3d/plot_universe_3d_bands.py
3d-unfolding/uq_3d/plot_universe_3d_bands.py  py-entrypoint  docs/analysis-note/make_figures.sh
3d-unfolding/xsec_3d.py  py-entrypoint  3d-unfolding/genie/fsi_variation_xsec3d.py; 3d-unfolding/genie/genie_mec_to_xsec3d.py; 3d-unfolding/genie/genie_to_xsec3d.py; 3d-unfolding/genie/gibuu_to_xsec3d.py; 3d-unfolding/genie/model_tune_xsec3d.py; 3d-unfolding/genie/nuwro_to_xsec3d.py; 3d-unfolding/unfold_3d_omnifold_unbinned.py
nd-unfolding/adopt_unified_4d.py  py-entrypoint  nd-unfolding/sbatch_adopt_4d_corrected_cpu.sh; nd-unfolding/sbatch_adopt_fps.sh; nd-unfolding/sbatch_adopt_fps_corrected_cpu.sh; nd-unfolding/sbatch_adopt_fps_corrected_gpu.sh; nd-unfolding/uq_fps/corrected/supervise_fps_uq.sh
nd-unfolding/adopt_unified_5d.py  py-entrypoint  nd-unfolding/run_adopt_5d.sh; nd-unfolding/sbatch_adopt_5d.sh; nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh
nd-unfolding/analyze_universes_5d.py  py-entrypoint  nd-unfolding/run_budget_5d.sh; nd-unfolding/sbatch_combine_5d_budget.sh; nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh
nd-unfolding/analyze_universes_nd.py  py-entrypoint  nd-unfolding/sbatch_analyze_4d_cov.sh; nd-unfolding/sbatch_combine_4d_budget.sh; nd-unfolding/sbatch_combine_4d_corrected_cpu.sh; nd-unfolding/sbatch_combine_4d_corrected_gpu.sh; nd-unfolding/sbatch_fps_budget.sh; nd-unfolding/sbatch_fps_budget_corrected_cpu.sh; nd-unfolding/sbatch_fps_budget_corrected_gpu.sh; nd-unfolding/sbatch_fps_cov.sh
nd-unfolding/assemble_bank_4d.py  py-entrypoint  nd-unfolding/sbatch_assemble_4d.sh
nd-unfolding/bootstrap_nd.py  py-entrypoint  nd-unfolding/ai1_packed_loop.sh; nd-unfolding/boot5d_packed_loop.sh; nd-unfolding/run_4d_replicas_multinode.sh; nd-unfolding/run_4d_replicas_packed.sh; nd-unfolding/run_4dstatml_interactive.sh; nd-unfolding/sbatch_ai1_estimator_scan.sh; nd-unfolding/sbatch_bootstrap_4d.sh; nd-unfolding/sbatch_bootstrap_4d_corrected_cpu.sh; nd-unfolding/sbatch_bootstrap_4d_corrected_gpu.sh; nd-unfolding/sbatch_bootstrap_5d.sh; nd-unfolding/sbatch_bootstrap_fps.sh; nd-unfolding/sbatch_bootstrap_fps_corrected_cpu.sh; nd-unfolding/sbatch_bootstrap_fps_corrected_gpu.sh; nd-unfolding/uq_fps/corrected/run_fps_uq_packed.sh
nd-unfolding/build_fps_prior_nuwro.py  py-entrypoint  nd-unfolding/sbatch_fps_envelope.sh
nd-unfolding/check_4d_anchors.py  py-entrypoint  nd-unfolding/sbatch_hadd_unfold_4d.sh; nd-unfolding/sbatch_unfold_4d_rerun.sh
nd-unfolding/check_5d_anchors.py  py-entrypoint  nd-unfolding/sbatch_hadd_unfold_5d.sh
nd-unfolding/combine_cov_nd.py  py-entrypoint  nd-unfolding/run_ai1_combine.sh; nd-unfolding/run_budget_5d.sh; nd-unfolding/sbatch_combine_4d_corrected_cpu.sh; nd-unfolding/sbatch_combine_4d_corrected_gpu.sh; nd-unfolding/sbatch_combine_4d_statml.sh; nd-unfolding/sbatch_combine_5d_budget.sh; nd-unfolding/sbatch_combine_boot_fps.sh; nd-unfolding/sbatch_combine_boot_fps_corrected_cpu.sh; nd-unfolding/sbatch_combine_boot_fps_corrected_gpu.sh; nd-unfolding/sbatch_combine_split_fps.sh; nd-unfolding/sbatch_combine_split_fps_corrected_cpu.sh; nd-unfolding/sbatch_combine_split_fps_corrected_gpu.sh
nd-unfolding/compare_ascencio_fullcov.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/compare_ascencio_fine.py
nd-unfolding/coverage_toy_nd.py  py-entrypoint  nd-unfolding/sbatch_coverage_fps.sh
nd-unfolding/dump_td_q3.py  py-entrypoint  nd-unfolding/sbatch_td_q3.sh
nd-unfolding/eavailW_covariance.py  py-entrypoint  nd-unfolding/run_eavailW_5d.sh; nd-unfolding/run_task13_interactive.sh; nd-unfolding/sbatch_eavailW_cov.sh; nd-unfolding/sbatch_eavailW_cov_wlat.sh
nd-unfolding/eavail_generator_significance.py  py-entrypoint  nd-unfolding/sbatch_eavail_sig.sh
nd-unfolding/excess_eavail_W.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/sbatch_excess_eavail_W.sh
nd-unfolding/fps_acceptance.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/build_fps_prior_genie_5d.py; nd-unfolding/build_fps_prior_nuwro.py; nd-unfolding/build_fps_prior_nuwro_5d.py; nd-unfolding/fps_extension_validation.py; nd-unfolding/fps_pilot_compare.py; nd-unfolding/fps_prior_envelope.py; nd-unfolding/sbatch_fps_mefhc.sh; nd-unfolding/sbatch_fps_pilot.sh
nd-unfolding/fps_endpoint_receipt.py  py-entrypoint  nd-unfolding/run_active_fps_unfolds_interactive.sh; nd-unfolding/sbatch_unfold_active_fps.sh
nd-unfolding/fps_extension_validation.py  py-entrypoint  nd-unfolding/sbatch_fps_coverage_analysis.sh; nd-unfolding/sbatch_fps_hidden_closure.sh
nd-unfolding/fps_gbdt_prior_reunfold_5d.py  py-entrypoint  nd-unfolding/sbatch_fps_reunfold_5d.sh; nd-unfolding/sbatch_fps_reunfold_5d_xps.sh; nd-unfolding/sbatch_fps_reunfold_5d_xps2.sh
nd-unfolding/fps_pilot_compare.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/fps_extension_validation.py; nd-unfolding/fps_prior_envelope.py; nd-unfolding/sbatch_fps_genie_refix.sh; nd-unfolding/sbatch_fps_mefhc.sh; nd-unfolding/sbatch_fps_pilot.sh
nd-unfolding/fps_prior_envelope.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/sbatch_fps_envelope.sh; nd-unfolding/sbatch_fps_genie_refix.sh
nd-unfolding/fps_reported_mask.py  py-entrypoint  nd-unfolding/sbatch_fps_mask.sh
nd-unfolding/fps_unfold_complete.py  py-entrypoint  nd-unfolding/fps_build_publication_manifest.py; nd-unfolding/fps_endpoint_receipt.py
nd-unfolding/fps_verify_merged_receipt.py  py-entrypoint  nd-unfolding/fps_build_control_manifest.py; nd-unfolding/fps_build_publication_manifest.py
nd-unfolding/make_control_plots.py  py-entrypoint  docs/analysis-note/make_figures.sh
nd-unfolding/nn_dump_inputs.py  py-entrypoint  nd-unfolding/sbatch_dump_fps_inputs.sh; nd-unfolding/sbatch_nn_dump_5d.sh; nd-unfolding/sbatch_nn_dump_fps_5d.sh; nd-unfolding/sbatch_nn_dump_fps_5d_xps.sh; nd-unfolding/sbatch_nn_dump_fps_5d_xps2.sh; nd-unfolding/sbatch_nn_dump_lgbm.sh
nd-unfolding/nn_run_from_npz.py  py-entrypoint  nd-unfolding/sbatch_nn_dump_lgbm.sh; nd-unfolding/sbatch_nn_gpu.sh
nd-unfolding/omnifold_nn_core.py  py-entrypoint  nd-unfolding/bootstrap_nd.py; nd-unfolding/compare_unified_throw.py; nd-unfolding/coverage_toy_nd.py; nd-unfolding/fps_gbdt_prior_reunfold_5d.py; nd-unfolding/nn_run_from_npz.py; nd-unfolding/seedscan_split.py; nd-unfolding/sweep_bank.py; nd-unfolding/sweep_bank_5d.py; nd-unfolding/unbinned_gof.py; nd-unfolding/unified_throw.py; nd-unfolding/unified_throw_cov_5d.py; unbinned_unfolding/python/omnifold.py
nd-unfolding/p4_evidence.py  py-entrypoint  nd-unfolding/run_p4_standard.sh
nd-unfolding/p4_validate_active_lateral.py  py-entrypoint  nd-unfolding/run_p4_standard.sh
nd-unfolding/pet/build_csyst_prelim_bkgsub.py  py-entrypoint  nd-unfolding/pet/sbatch_csyst_prelim_bkgsub.sh
nd-unfolding/pet/closure_coupled_phi_sweep.py  py-entrypoint  nd-unfolding/pet/sbatch_coupled_phi_sweep_delta.sh
nd-unfolding/pet/closure_unread_variable_phi.py  py-entrypoint  nd-unfolding/pet/closure_coupled_phi_sweep.py
nd-unfolding/pet/extract_bootstrap_replica.py  py-entrypoint  nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh
nd-unfolding/pet/extract_nominal_bkgsub.py  py-entrypoint  nd-unfolding/pet/sbatch_pet_nominal_bkgsub.sh
nd-unfolding/pet/feature_rank_arms.py  py-entrypoint  nd-unfolding/pet/sbatch_feature_rank_arms_delta.sh
nd-unfolding/pet/measure_fullevent_host_memory.py  py-entrypoint  nd-unfolding/pet/sbatch_fe_hostmem_ladder_delta.sh
nd-unfolding/pet/minerva_pet_dataloader.py  py-entrypoint  nd-unfolding/pet/phase7_retrain_universe.py; nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh; nd-unfolding/pet/sbatch_pet_nominal_bkgsub.sh; nd-unfolding/pet/sbatch_pet_smoke.sh; nd-unfolding/pet/sbatch_pet_train.sh; nd-unfolding/pet/sbatch_pet_train_fullcloud.sh; nd-unfolding/pet/sbatch_pet_train_hvd.sh; nd-unfolding/sbatch_pet_conv_fps_xps2.sh; nd-unfolding/sbatch_pet_train_fps_delta.sh; nd-unfolding/sbatch_pet_train_fps_hvd.sh
nd-unfolding/pet/npz_to_npy.py  py-entrypoint  nd-unfolding/sbatch_npz_pc_fps.sh; nd-unfolding/sbatch_npz_pc_fps_xps.sh; nd-unfolding/sbatch_npz_pc_fps_xps2.sh
nd-unfolding/pet/pet_vs_gbdt.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/pet/sbatch_pet_compare.sh; nd-unfolding/pet/sbatch_pet_xsec.sh
nd-unfolding/pet/pet_vs_gbdt_uncertainty.py  py-entrypoint  docs/analysis-note/make_figures.sh
nd-unfolding/pet/phase7_flux_rank.py  py-entrypoint  nd-unfolding/pet/launch_phase7_final.sh
nd-unfolding/pet/phase7_retrain_universe.py  py-entrypoint  nd-unfolding/pet/sbatch_phase7_retrain.sh
nd-unfolding/pet/plot_event_displays.py  py-entrypoint  docs/analysis-note/make_figures.sh
nd-unfolding/pet/pointcloud_projection.py  py-entrypoint  docs/analysis-note/make_figures.sh; nd-unfolding/pet/sbatch_project_fullcloud.sh
nd-unfolding/pet_lateral_band.py  py-entrypoint  nd-unfolding/sbatch_pet_lateral_band.sh
nd-unfolding/pet_lateral_band_5d.py  py-entrypoint  nd-unfolding/sbatch_pet_lateral_5d.sh
nd-unfolding/pet_lateral_correction.py  py-entrypoint  nd-unfolding/sbatch_pet_lateral.sh
nd-unfolding/pet_systematics.py  py-entrypoint  nd-unfolding/pet/extract_bootstrap_replica.py; nd-unfolding/pet/pet_vs_gbdt_uncertainty.py; nd-unfolding/pet_lateral_band.py; nd-unfolding/pet_lateral_correction.py; nd-unfolding/sbatch_pet_rebank.sh; nd-unfolding/sbatch_pet_systematics.sh
nd-unfolding/pilot_cv_check_4d.py  py-entrypoint  nd-unfolding/sbatch_pilot_cv_check_4d_gpu.sh
nd-unfolding/plot_control_corner.py  py-entrypoint  docs/analysis-note/make_figures.sh
nd-unfolding/project_cov_nd.py  py-entrypoint  nd-unfolding/p4_evidence.py; nd-unfolding/p4_project_4d.py; nd-unfolding/sbatch_project_5d_to_4d_candidate_gpu.sh
nd-unfolding/q3_excess_projection.py  py-entrypoint  docs/analysis-note/make_figures.sh
nd-unfolding/replica_manifest.py  py-entrypoint  nd-unfolding/combine_cov_nd.py; nd-unfolding/combine_seedscan_split.py; nd-unfolding/pet/combine_cstat_bkgsub.py; nd-unfolding/pet_systematics.py; nd-unfolding/pet_systematics_5d.py
nd-unfolding/seedscan_split.py  py-entrypoint  nd-unfolding/run_4d_replicas_multinode.sh; nd-unfolding/run_4d_replicas_packed.sh; nd-unfolding/run_4dstatml_interactive.sh; nd-unfolding/sbatch_seedscan_split.sh; nd-unfolding/sbatch_seedscan_split_4d.sh; nd-unfolding/sbatch_seedscan_split_4d_corrected_cpu.sh; nd-unfolding/sbatch_seedscan_split_4d_corrected_gpu.sh; nd-unfolding/sbatch_seedscan_split_5d.sh; nd-unfolding/sbatch_seedscan_split_fps.sh; nd-unfolding/sbatch_seedscan_split_fps_corrected_cpu.sh; nd-unfolding/sbatch_seedscan_split_fps_corrected_gpu.sh; nd-unfolding/uq_fps/corrected/run_fps_uq_packed.sh
nd-unfolding/tests/test_fullevent_gate2.py  py-entrypoint  nd-unfolding/pet/measure_fullevent_host_memory.py
nd-unfolding/unbinned_gof.py  py-entrypoint  nd-unfolding/sbatch_unbinned_gof.sh
MINERvA101/MINERvA-101-Cross-Section/ExtractCrossSection.cpp  cpp-main  2d-unfolding/ibu_1d_projection/sbatch_ibu_1d_projection.sh; 2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp  cpp-main  2d-unfolding/sbatch_runEventLoop_baseline_flux_array.sh; 2d-unfolding/unbinned_1d_study/sbatch_unfold_1d_unbinned_1A.sh
```

---

# Appendix B — category 3, all 30 confirmed guards
### 2d-unfolding/unfold_2d_omnifold_unbinned.py:677  `if universe_branch is not None:`

reason: dominated by an earlier guard  
evidence: the only caller is at `:1378-1382`. Before either tuple is constructed, `:1200-1203` exits when `--closure-alt-universe` and `--universe` coexist. Thus `alt_universe_branch` and `universe_branch` cannot both reach this helper.  
what it would have caught: direct helper misuse that requested an alt-model closure and an active response universe simultaneously.

### 2d-unfolding/unfold_2d_omnifold_unbinned.py:1738  `if truth_pt_in.shape[0] != step2_weights.shape[0]:`

reason: vacuous by upstream construction  
evidence: `unbinned_unfolding/python/omnifold.py:105-108` applies `MC_pass_truth_mask` to `MCgen_entries`; `:123-124` creates weights with exactly that length; `:272` predicts once per retained truth row; `:294` returns that array. The caller supplies `sig["pass_truth"]` at `:1710-1724` and reconstructs `truth_pt_in` with the identical mask at `:1734`.  
what it would have caught: an OmniFold implementation returning a weight count different from its truth-pass input count.

### 3d-unfolding/unfold_3d_omnifold_unbinned.py:617  `if tpt.size != step2_weights.size:`

reason: vacuous by upstream construction  
evidence: the same OmniFold masking and output-length construction at `unbinned_unfolding/python/omnifold.py:105-124,272-294`; this caller passes `sig["pass_truth"]` at `3d-unfolding/unfold_3d_omnifold_unbinned.py:597-608` and selects `tpt` with that mask at `:614-616`.  
what it would have caught: loss or duplication of truth-event weights inside OmniFold.

### nd-unfolding/unfold_nd_omnifold_unbinned.py:984  `if tcols[0].size != step2_w.size:`

reason: vacuous by upstream construction  
evidence: `sig["pass_truth"]` is passed at `:963-977`; `tcols` is selected with the same mask at `:981-983`; the shared OmniFold implementation preserves that selected length at `unbinned_unfolding/python/omnifold.py:105-124,272-294`.  
what it would have caught: an N-D truth/weight alignment failure introduced inside OmniFold.

### 2d-unfolding/unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py:411  `if truth_in.shape[0] != step1_weights.shape[0] or truth_in.shape[0] != step2_weights.shape[0]:`

reason: vacuous by upstream construction  
evidence: the caller passes `sig["pass_truth"]` at `:396-404` and applies the same mask at `:406-409`; both returned arrays are constructed from the masked `MCgen_entries` length in `unbinned_unfolding/python/omnifold.py:105-124,256-294`.  
what it would have caught: a 1D truth vector and OmniFold result with different event counts.

### 2d-unfolding/binned_study/scripts/unfold_ptmu_omnifold_binned.py:93  `if max_abs_diff != 0.0:`

reason: vacuous by upstream construction  
evidence: `max_abs_diff` starts at literal `0.0` at `:62`. At `:65-72`, each `content` is immediately written with `SetBinContent` and read back from the same TH2D bin for comparison. There is no independent reconstruction or transformation.  
what it would have caught: corruption during a direct double-to-double ROOT bin copy.

### MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1922  `assert(error_bands["cv"].size() == 1);`

reason: dead by constant  
evidence: `error_bands["cv"]` is unconditionally overwritten with the one-element initializer `{new CVUniverse(options.m_mc)}` at `:1785`, with no intervening mutation of that entry before the assertion.  
what it would have caught: a missing or multi-universe CV band.

### MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp:98  `assert(!error_bands["cv"].empty() && ...);`

reason: dead by constant  
evidence: main unconditionally assigns exactly one CV universe at `:402`, then passes that map directly to `LoopAndFillEventSelection` at `:448`.  
what it would have caught: calling the MC selection loop without a CV universe.

### MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp:206  `assert(!truth_bands["cv"].empty() && ...);`

reason: dead by constant  
evidence: main unconditionally assigns exactly one truth CV universe at `:405`, then passes that map directly to `LoopAndFillEffDenom` at `:450`.  
what it would have caught: calling the truth-denominator loop without a CV universe.

### MINERvA101/MINERvA-101-Cross-Section/runEventLoop.cpp:476  `assert(error_bands["cv"].size() == 1 && ...);`

reason: dead by constant  
evidence: `error_bands["cv"]` is overwritten with the one-element initializer at `:402`; subsequent code reads but does not alter that vector before `:476`.  
what it would have caught: an ambiguous CV universe for flux integration.

### 2d-unfolding/unfold_2d_omnifold_unbinned.py:524  `raise ValueError(f"unknown kine_ctx={kine_ctx!r}")`

reason: config-pinned  
evidence: all in-tree calls pass one of the four handled literals: `bkg_tree_reco` at `:292`, `truth_tree` at `:563`, and `reco_tree_truth`/`reco_tree_reco` at `:652-653`; the 3D and N-D callers likewise use only those literals.  
what it would have caught: a new caller using an unimplemented ROOT-tree naming context.

### nd-unfolding/unfold_nd_omnifold_unbinned.py:216  `raise ValueError(f"unknown ctx={ctx!r}")`

reason: config-pinned  
evidence: its complete caller inventory is `truth_tree` at `:249`, `reco_tree_truth` and `reco_tree_reco` at `:338-339`, and `bkg_tree` at `:485`; all are handled above the raise.  
what it would have caught: an unsupported extra-axis branch namespace.

### 2d-unfolding/unfold_2d_omnifold_unbinned.py:885  `raise ValueError(f"Unknown closure_reweight shape: {shape}")`

reason: config-pinned  
evidence: argparse restricts the value to `gauss_pt` or `tilt_pz` at `:1039-1040`; both call sites consume that parsed value at `:1533` and `:1753`, and both values return before the raise.  
what it would have caught: an unimplemented closure deformation name.

### 2d-unfolding/unfold_2d_omnifold_unbinned.py:991  `raise ValueError(f"Unknown axis: {axis}")`

reason: config-pinned  
evidence: every in-tree call passes literal `pt` or `pz`: `:1942-1943` and `2d-unfolding/plot_2d_cross_section.py:300,302`.  
what it would have caught: a request to project the 2D result onto a nonexistent axis.

### 3d-unfolding/xsec_3d.py:79  `raise ValueError(f"axis must be pt/pz/eavail, got {axis!r}")`

reason: config-pinned  
evidence: all production and generator callers pass `pt`, `pz`, or `eavail`, including `3d-unfolding/unfold_3d_omnifold_unbinned.py:663-665,687`; its self-test iterates the fixed three-value tuple at `xsec_3d.py:131-132`.  
what it would have caught: an unsupported 3D marginal-projection axis.

### 2d-unfolding/unbinned_1d_study/ptmu_closure_iteration_study.py:249  `raise RuntimeError(f"Unknown stress mode: {args.stress_mode}")`

reason: config-pinned  
evidence: argparse permits only `nominal`, `tilt`, `bump`, and `tail` at `:767`; `morph_weight` handles all four before the raise and is called only with the parsed namespace at `:262`.  
what it would have caught: an unimplemented closure-stress model.

### nd-unfolding/pet/minerva_pet_dataloader.py:118  `raise ValueError(f"unknown mode {mode!r} (scalar|pointcloud)")`

reason: config-pinned  
evidence: its CLI restricts `--mode` to `scalar`/`pointcloud` at `:249`; internal calls use `args.mode` at `:303,384`, and the only external production caller passes literal `pointcloud` at `nd-unfolding/pet/phase7_retrain_universe.py:118,158`.  
what it would have caught: selection of an unavailable PET input representation.

### nd-unfolding/uq_math.py:18  `raise ValueError(f"unknown invalid-ratio policy: {invalid_policy}")`

reason: config-pinned  
evidence: all in-tree callers provide the default `error` or an argparse value restricted to `error`/`neutral`, for example `nd-unfolding/pet_systematics.py:149,166-167`, `pet_systematics_5d.py:198,215-216`, and `pet_unified_throw_5d.py:90,105-106`. Both policies are handled before `:18`.  
what it would have caught: an unsupported response to invalid systematic-weight ratios.

### nd-unfolding/fps_provenance.py:341  `raise FpsGateError(f"unknown transition {transition}")`

reason: config-pinned  
evidence: `TRANSITIONS` is the fixed four-element tuple at `:82`. Every caller uses a member literal: `build_active_lateral_fps.py:125`, `p4_validate_active_lateral_fps.py:165`, `adopt_active_lateral_fps.py:145`, and `adopt_unified_fps.py:143`; tests also use only members.  
what it would have caught: generation of a receipt for an undefined provenance transition.

### nd-unfolding/pet/fullevent_fps_dataloader.py:333  `raise ValueError(f"[EVT-SCHEMA] unknown transform {transform!r} ...")`

reason: dead by constant  
evidence: `transform` comes only from `_EVT_SPEC` at `:312`. The constant table at `:223-244` contains only `as_is`, `div_scale`, `mul_scale`, `cos`, and `sin`, exactly the cases handled at `:324-332`.  
what it would have caught: a misspelled transform added to the hard-coded event-feature schema.

### nd-unfolding/pet/fullevent_fps_dataloader.py:1072  `if bkg_mode not in ("negweight-refined", "purity"):`

reason: config-pinned  
evidence: the function default is `negweight-refined` at `:1044`; its CLI restricts values to the same pair at `:1377`; fixed production callers include `train_fullevent_nominal.py:209`, `gate2_target_runtime.py:455`, and `smoke_fullevent_fps.py:40`. Test wrappers also default to `negweight-refined`.  
what it would have caught: an unsupported full-event background treatment.

### 2d-unfolding/uq/plot_uncertainty_fig6_7_style.py:186  `raise ValueError(axis)`

reason: config-pinned  
evidence: every `projection_matrix` call is inside fixed loops over `("pz", "pt")` at `:337-340` and `:343-348`.  
what it would have caught: construction of an uncertainty projection for another axis.

### 2d-unfolding/uq/plot_uncertainty_fig6_7_style.py:200  `assert col == n_reported`

reason: vacuous by upstream construction  
evidence: `n_reported` is exactly `flat_reported.sum()` at `:180`. The nested traversal at `:191-199` increments `col` once, and only once, for every true element of the same `reported` array.  
what it would have caught: an internal omission or duplicate while assigning reported-bin matrix columns.

### 2d-unfolding/uq/plot_uncertainty_fig6_7_style.py:210  `raise ValueError(axis)`

reason: config-pinned  
evidence: every `central_projection` call receives the same fixed `pz`/`pt` loop value at `:337-356`; both values return before the raise.  
what it would have caught: a request for an unsupported central-value projection.

### nd-unfolding/fps_provenance.py:313  `if classify_manifest(manifest) != "publication":`

reason: dominated by an earlier guard  
evidence: `require_publication_manifest` first calls `require_manifest_inventory` at `:299` and `require_footing(... required_bkg_mode=PUBLICATION_BKG_MODE)` at `:301`. The latter rejects every endpoint not using the publication mode at `:241-256`. With complete inventory and all modes fixed, `classify_manifest` must return `publication` by `:263-266`.  
what it would have caught: a non-publication or mixed-mode manifest already rejected earlier in the same function.

### nd-unfolding/fps_provenance.py:110  `if not os.path.exists(path):`

reason: unreachable code position  
evidence: this guard is inside `sha256_partial`, defined at `:104`; repository-wide caller search finds no invocation of `sha256_partial`. The active provenance paths use full-file `sha256_file`.  
what it would have caught: a missing artifact supplied to the retired partial head/tail hashing path.

### nd-unfolding/uq_math.py:133  `if x.ndim != 2:`

reason: unreachable code position  
evidence: `finite_observable_mask` is called only at `:150-151` by `active_selection_masks`; repository-wide search finds no caller of `active_selection_masks`.  
what it would have caught: non-matrix coordinates passed to the unused active-selection kernel.

### nd-unfolding/uq_math.py:138  `if w.shape != (x.shape[0],):`

reason: unreachable code position  
evidence: the guard is in the same `finite_observable_mask` function reachable only through the uncalled `active_selection_masks` at `:144-161`.  
what it would have caught: per-event weights misaligned with coordinates in that unused kernel.

### nd-unfolding/uq_math.py:148  `if truth.shape != reco.shape or truth.ndim != 2 or truth.shape[1] < 2:`

reason: unreachable code position  
evidence: repository-wide search finds only the definition of `active_selection_masks` and no call site.  
what it would have caught: mismatched or underspecified truth/reco coordinate matrices.

### nd-unfolding/uq_math.py:158  `if flags.shape != (truth.shape[0],):`

reason: unreachable code position  
evidence: this is also inside the uncalled `active_selection_masks` function at `:144-161`.  
what it would have caught: a reconstruction-flag vector not aligned to the event arrays.

---

# Appendix C — category 5, all 149 invariants
| # | invariant (short quote, doc line) | check (file:line) | runs in default suite? |
|---|---|---|---|
| 1 | "full-event PET over the declared extended-FPS fiducial phase space (NOT 'full phase space')" (L8) | — | no check |
| 2 | "PET trains UNBINNED on CONTINUOUS features" (L13) | — | no check |
| 3 | "EDGES … never as classifier inputs or training bins" (L14) | — | no check |
| 4 | "Guarded by `assert_extended_fps_edges` (fail closed on paper grid)" (L15) | `pet/fullevent_fps_dataloader.py:102`,`:121`; `tests/test_fullevent_fps.py:25` | yes |
| 5 | "never share one ID across schemas" (L18) | `pet/validate_pet_nominal_gate4.py:633`; `tests/test_pet_nominal_gate4_validator.py:143` | yes* |
| 6 | "`pet-fullevent-fps-v1` = the FULL-schema publication estimator (…+ residual summaries)" (L19) | `pet/validate_pet_nominal_gate4.py:626`,`:653` | yes* *(partial: residual summaries not in the frozen list)* |
| 7 | "Requires the C++ full-event dump + fresh full-schema P3F" (L21) | `pet/fullevent_fps_dataloader.py:1074` | yes *(partial: no P3F-freshness check)* |
| 8 | "CROSS-CHECK ONLY — never a publication lateral/central source" (L23) | `pet/train_fullevent_nominal.py:221`; `pet/extract_fullevent_fps.py:175`; `tests/test_fullevent_extract.py:162` | yes |
| 9 | "Every P5B component … MUST carry ONE of these fingerprints and never mix the two" (L24) | — | no check |
| 10 | "recoil-only PET UQ is NEVER attached to either" (L25) | — | no check |
| 11 | "inputs: FPS CV full-event point-cloud npz built with `MNV101_FULL_PHASE_SPACE=1`" (L26) | `pet/fullevent_dump_contract.py:24`,`:41`; `pet/fullevent_fps_dataloader.py:1026` | yes |
| 12 | "recoil-only tensors → must be regenerated for the real central" (L27) | `pet/fullevent_fps_dataloader.py:1034`; `tests/test_fullevent_fps.py:454` | yes |
| 13 | "reco cloud (E,pos,z; KNN coord (pos,z))" (L29) | `pet/fullevent_fps_dataloader.py:175`; `tests/test_fullevent_fps.py:47` | yes |
| 14 | "truth cloud (E,px,py,pz,pdg,theta,phi; KNN coord (theta,phi))" (L30) | `pet/fullevent_fps_dataloader.py:204`; `tests/test_fullevent_fps.py:96` | yes *(code is (5,6,7); see §Could not determine)* |
| 15 | "`event_reco`/`event_data` = continuous reco muon …; `event_truth` = continuous truth muon" (L30) | `pet/fullevent_fps_dataloader.py:266`,`:273`; `tests/test_fullevent_fps.py:147` | yes |
| 16 | "Edges are reporting/covariance/validation only, never inputs" (L32) | — | no check |
| 17 | "preprocessing: cloud ÷1000 (MeV→GeV, mm→m)" (L33) | `pet/fullevent_fps_dataloader.py:128`; `tests/test_fullevent_fps.py:48` | yes |
| 18 | "non-finite→0 (pad/mask sentinel)" (L33) | — | no check |
| 19 | "z-normalized over pass_reco / pass_truth, !pass rows zeroed" (L34) | `pet/fullevent_fps_dataloader.py:487`; `tests/test_fullevent_fps.py:255` | yes |
| 20 | "vendored `omnifold_nn` PET (multi-input Model, explicit `coord_idx`, FiLM event conditioning)" (L35) | `pet/train_fullevent_nominal.py:229`; `tests/test_fullevent_fps.py:47` | yes *(partial: FiLM unchecked)* |
| 21 | "niter 2" (L36) | `pet/validate_pet_nominal_gate4.py:612`; `tests/test_pet_nominal_gate4_validator.py:159` | yes* |
| 22 | "epochs 8" (L36) | `pet/validate_pet_nominal_gate4.py:612` | yes* |
| 23 | "batch 1024" (L36) | — | no check |
| 24 | "Adam lr 1e-4" (L36) | — | no check |
| 25 | "train subsample 2M" (L36) | `pet/validate_pet_nominal_gate4.py:164`,`:612`; `tests/test_pet_nominal_gate4_validator.py:241` | yes* |
| 26 | "estimator seed 42 FIXED for central + vertical/end-to-end universes + C_stat" (L37) | `pet/validate_pet_nominal_gate4.py:612` | yes* *(nominal only)* |
| 27 | "C_ml varies subsample/split seed × TF estimator seed …, no Poisson" (L38) | — | no check |
| 28 | "nominal product `products/pet/fullevent_fps/pet_fullevent_fps_nominal_*`" (L40) | — | no check |
| 29 | "extended-FPS canonical (pT,p‖) grid (this file's CANONICAL_* edges)" (L41) | `pet/validate_pet_nominal_gate4.py:605`; `tests/test_pet_nominal_gate4_validator.py:152` | yes* |
| 30 | "fingerprint recipe … `sha256(git_commit(…) \|\| feature_list \|\| …)`" (L42) | — | no check |
| 31 | "Every covariance component summary must carry the SAME fingerprint or it is rejected at assembly" (L44) | — | no check |
| 32 | "nominal … is **negweight (ρ₁ = D − B) + Stay-Positive**" (L50) | `pet/fullevent_fps_dataloader.py:1200`,`:628`; `tests/test_fullevent_fps.py:352` | yes |
| 33 | "Option A LITERAL background-cloud injection … at weight −w_bkg·pot_scale, refined to non-negative" (L51) | `pet/fullevent_fps_dataloader.py:675`,`:708`; `tests/test_fullevent_gate2.py:105`,`:150` | yes |
| 34 | "purity … a matched REGRESSION CONTROL only, never the publication nominal" (L53) | `pet/fullevent_fps_dataloader.py:1023`; `pet/fullevent_dump_contract.py:57`; `tests/test_fullevent_fps.py:439` | yes |
| 35 | "`build_fullevent_loaders` defaults to `bkg_mode=\"negweight-refined\"`" (L54) | — | no check |
| 36 | "FAILS CLOSED without the background inventory" (L55) | `pet/fullevent_fps_dataloader.py:1200`; `tests/test_fullevent_fps.py:411` | yes |
| 37 | "REQUIRES aligned background clouds + scalars + `w_bkg`, row-aligned to the signal/data event order" (L57) | `pet/fullevent_fps_dataloader.py:1210`,`:1286`; `pet/fullevent_dump_contract.py:70` | yes *(partial: row-count, not event order)* |
| 38 | "rebuilt per replica under the F7 coherent 3-inventory bootstrap" (L58) | `pet/fullevent_fps_dataloader.py:736`; `tests/test_fullevent_gate2.py:270` | yes |
| 39 | "No purity-only P5B baseline may be launched" (L59) | `pet/fullevent_fps_dataloader.py:1023`; `tests/test_fullevent_fps.py:439` | yes |
| 40 | "Source only FPS CV event loops from `MNV101_FULL_PHASE_SPACE=1`" (L62) | `pet/fullevent_dump_contract.py:24`,`:41`; `tests/test_fullevent_dump_contract.py:68` | yes |
| 41 | "consumers without the flag must verify embedded FPS provenance and fail closed" (L64) | — | no check |
| 42 | "pT (16 edges): 0,0.07,…,30.0" (L67) | `pet/fullevent_fps_dataloader.py:64`,`:110`; `tests/test_fullevent_fps.py:22` | yes |
| 43 | "p‖ (20 edges): 0,0.75,…,120" (L68) | `pet/fullevent_fps_dataloader.py:67`,`:115` | yes |
| 44 | "Tier-1 acceptance-supported (eff≳2%), Tier-2 … carry a prior-dependence band" (L69) | — | no check |
| 45 | "Muon features cannot turn zero-efficiency cells into measured cells" (L70) | — | no check |
| 46 | "Scaffolding only …, NOT publication inputs … the representation is REBUILT" (L72) | `pet/fullevent_fps_dataloader.py:799`,`:1034` | yes |
| 47 | "reco cloud (step-1 detector) / measured (data) — SAME observable contract" (L79) | `tests/test_fullevent_schema.py:168` | yes |
| 48 | "recoil token E \| 0 \| GeV \| ÷1000 \| energy>0 = valid-token / pad mask" (L82) | `pet/fullevent_fps_dataloader.py:130`,`:172`; `tests/test_fullevent_fps.py:48` | yes |
| 49 | "recoil token pos \| 1 \| m \| ÷1000" (L83) | `pet/fullevent_fps_dataloader.py:130`,`:175` | yes *(partial: column identity via coord_idx only)* |
| 50 | "recoil token z \| 2 \| m \| ÷1000 \| KNN coord" (L84) | `pet/fullevent_fps_dataloader.py:175`; `tests/test_fullevent_fps.py:47` | yes |
| 51 | "recoil token view \| 3 \| raw \| Not rescaled" (L85) | `pet/fullevent_fps_dataloader.py:166`; `tests/test_fullevent_fps.py:61` | yes |
| 52 | "`*_view`, 1=X/2=U/3=V" (L85) | — | no check |
| 53 | "recoil token time \| 4 \| ÷100 (ns→O(1))" (L86) | `pet/fullevent_fps_dataloader.py:167`; `tests/test_fullevent_fps.py:63` | yes |
| 54 | "KNN neighborhood coords = **(pos, z) = cols (1,2)** … via PET `coord_idx`" (L87) | `pet/fullevent_fps_dataloader.py:161`,`:175`; `tests/test_fullevent_fps.py:60` | yes |
| 55 | "View and time are token FEATURES, never neighborhood coordinates" (L88) | `pet/fullevent_fps_dataloader.py:175`; `tests/test_fullevent_fps.py:60` | yes |
| 56 | "zero-pad/truncate to num_part=12 (loader top-N by energy)" (L90) | `pet/dump_pointcloud_inputs.py:487`; `tests/test_g2_dump_branch.py:273` | yes *(partial: the value 12 is pinned nowhere)* |
| 57 | "The dump pads all five vectors under one permutation (`pad_reco_cloud_tokens`)" (L90) | `tests/test_g2_dump_branch.py:261` | yes |
| 58 | "the loader … re-zeroes view/time from the energy mask … energy(col 0)==0 is the only pad authority" (L91) | `pet/fullevent_fps_dataloader.py:172`; `tests/test_fullevent_fps.py:68` | yes |
| 59 | "FS-hadron E,px,py,pz \| 0–3 \| GeV \| ÷1000" (L97) | `pet/fullevent_fps_dataloader.py:200`; `tests/test_fullevent_fps.py:95` | yes |
| 60 | "muon±13 & ν removed at source" (L97) | — | no check |
| 61 | "pdg \| 4 \| raw \| **retained**" (L98) | `pet/fullevent_fps_dataloader.py:201`; `tests/test_fullevent_fps.py:104` | yes |
| 62 | "theta,phi \| 5,6 \| rad \| raw … **KNN coords = (theta,phi)=(5,6)**" (L99) | `pet/fullevent_fps_dataloader.py:204`; `tests/test_fullevent_fps.py:96` | yes *(code is (5,6,7))* |
| 63 | "the FULL schema (13 features) … `DEFAULT_EVT_FEATURES`" (L102) | `pet/fullevent_fps_dataloader.py:266`; `tests/test_fullevent_schema.py:176` | yes |
| 64 | "`pt`,`pparallel` \| `*_scalars` cols 0,1 \| GeV" (L106) | `pet/fullevent_fps_dataloader.py:225`; `tests/test_fullevent_fps.py:151` | yes |
| 65 | "`mu_px`…`mu_E` \| `*_muon` cols 0–3 \| MeV→GeV" (L107) | `pet/fullevent_fps_dataloader.py:229`; `tests/test_fullevent_schema.py:107` | yes |
| 66 | "`mu_cos_phi`,`mu_sin_phi` \| col 4 \| azimuth encoded **periodically**" (L108) | `pet/fullevent_fps_dataloader.py:233`; `tests/test_fullevent_fps.py:191` | yes |
| 67 | "`mu_qp` \| col 5 \| MeV⁻¹→GeV⁻¹" (L109) | `pet/fullevent_fps_dataloader.py:239`; `tests/test_fullevent_schema.py:107` | yes *(partial: column pinned, reciprocal transform unasserted)* |
| 68 | "`mu_minos_ok` \| col 6 \| 0/1" (L110) | `pet/fullevent_fps_dataloader.py:240`; `tests/test_fullevent_schema.py:137` | yes |
| 69 | "`vtx_x`,`vtx_y`,`vtx_z` \| cols 0–2 \| mm→m" (L111) | `pet/fullevent_fps_dataloader.py:241`; `tests/test_fullevent_schema.py:113` | yes |
| 70 | "Column orders mirror `dump_pointcloud_inputs.RECO_MUON_BRANCHES` … pinned … by `tests/test_fullevent_schema.py`" (L113) | `tests/test_fullevent_schema.py:107`,`:113` | yes |
| 71 | "z-normalized with the RECO-MC statistic (data and background use the reco norm)" (L114) | — | no check |
| 72 | "the −9999 !pass_reco sentinel is carried by **every** one of these columns" (L116) | `tests/test_fullevent_schema.py:128`; `tests/test_g2_dump_branch.py:207` | yes |
| 73 | "the reduced schema stays a literal SUBSET" (L118) | `tests/test_fullevent_fps.py:189` | yes |
| 74 | "the dump pins their length to the cloud's token dimension P … so they are cloud columns 3,4" (L120) | `pet/fullevent_dump_contract.py:88`; `pet/fullevent_fps_dataloader.py:169`; `tests/test_fullevent_dump_contract.py:95` | yes |
| 75 | "STILL NOT DUMPED, so still absent: residual-energy summary tokens" (L124) | — | no check |
| 76 | "NOT adopted, deliberately: `eavail`, `q3`" (L126) | `pet/fullevent_fps_dataloader.py:266`; `pet/validate_pet_nominal_gate4.py:626` | yes* |
| 77 | "They are selectable via `feature_names` for that ranking" (L128) | `pet/fullevent_fps_dataloader.py:227`; `tests/test_b1_normalization_fix.py:1235` | yes |
| 78 | "Detector/MINOS features are step-1 ONLY. NEVER a truth counterpart — enforced … by `TRUTH_ELIGIBLE_FEATURES`" (L131) | `pet/fullevent_fps_dataloader.py:414`; `tests/test_fullevent_fps.py:228`; `pet/validate_pet_nominal_gate4.py:640` | yes |
| 79 | "retained as `REDUCED_EVT_FEATURES` … CROSS-CHECK ONLY" (L133) | `pet/fullevent_fps_dataloader.py:276`; `tests/test_fullevent_schema.py:240` | yes |
| 80 | "`[truth_muon_pT, truth_muon_p‖]` (truth_scalars cols 0,1)" (L137) | `pet/fullevent_fps_dataloader.py:273`; `tests/test_fullevent_fps.py:152` | yes |
| 81 | "z-normalized with the TRUTH-MC statistic" (L137) | — | no check |
| 82 | "NO MINOS/range/quality/vertex-detector counterparts; no sentinels" (L138) | `pet/fullevent_fps_dataloader.py:414`; `tests/test_fullevent_fps.py:228` | yes |
| 83 | "Padding mask: token energy (col 0) == 0" (L142) | `pet/fullevent_fps_dataloader.py:172`; `tests/test_fullevent_fps.py:68` | yes |
| 84 | "Muon is a distinguished EVENT feature (FiLM conditioning), so cloud tokens are all recoil" (L144) | — | no check |
| 85 | "a muon/recoil/view type embedding is only needed if muon becomes a cloud token" (L145) | — | no check |
| 86 | "Gate-4 freezes both feature lists so a reduced run can no longer validate under the full-schema fingerprint" (L159) | `pet/validate_pet_nominal_gate4.py:626`–`:637`; `tests/test_pet_nominal_gate4_validator.py:143` | yes* |
| 87 | "It is **NOT** a publication-ready feature set: P5A is NOT declared 'passed' on this reduced set" (L172) | `pet/train_fullevent_nominal.py:221` | yes |
| 88 | "`reco_scalars` muon (pT,p‖) = **-9999** for every non-pass_reco event" (L178) | `pet/dump_pointcloud_inputs.py` (`reco_scalar_row`); `tests/test_g2_dump_branch.py:207` | yes |
| 89 | "normalizes reco features over pass_reco events ONLY (truth over pass_truth ONLY) and zeroes the undefined rows post-normalization" (L180) | `pet/fullevent_fps_dataloader.py:487`; `tests/test_fullevent_fps.py:255` | yes |
| 90 | "they are masked by pass_reco in the step-1 loss" (L182) | — | no check |
| 91 | "The production full-event input build MUST preserve this handling" (L182) | `pet/fullevent_fps_dataloader.py:487` (single code path); `tests/test_g2_dump_branch.py:218` | yes |
| 92 | "NEVER a silent fallback to MC `reco_scalars`" (L190) | `pet/fullevent_fps_dataloader.py:1172`; `tests/test_fullevent_fps.py:300` | yes |
| 93 | "FAILS CLOSED on a missing `measured_scalars` unless `data_scalars_npz` is given" (L191) | `pet/fullevent_fps_dataloader.py:1153`–`:1176`; `tests/test_fullevent_fps.py:300` | yes |
| 94 | "4,116,128 rows == measured_pc, row-count gate enforced" (L193) | `pet/fullevent_fps_dataloader.py:1160`; `tests/test_fullevent_fps.py:306` | yes |
| 95 | "The production full-event FPS-CV npz should carry `measured_scalars` directly (dump-time)" (L195) | `pet/fullevent_dump_contract.py:29`,`:120`; `tests/test_g2_dump_branch.py:110` | yes |
| 96 | "a full event-by-event order proof … is a P5B hardening item" (L196) | — | no check *(self-declared gap)* |
| 97 | "Truth MINOS/range/match-quality: DO NOT EXIST … → absent from event_truth" (L200) | `pet/fullevent_fps_dataloader.py:251`,`:414`; `pet/test_g2_fullevent_dump_schema.py:250` | yes |
| 98 | "Muon full 4-vector/charge/vertex/view/timing at reco/data: pending C++ branches" (L201) | `pet/fullevent_fps_dataloader.py:1109`–`:1129`; `tests/test_fullevent_schema.py:249` | yes *(inverted — now required, not pending)* |
| 99 | "Nuclear-remnant truth token: not dumped" (L202) | — | no check |
| 100 | "add muon object + vertex + recoil view/timing + residual-energy branches under `MNV101_DUMP_POINTCLOUD`" (L205) | `pet/test_g2_fullevent_dump_schema.py:147`–`:192` (via `tests/test_g2_guards_collected.py:77`) | yes *(partial: residual-energy branches absent from the expected set)* |
| 101 | "P3F … supply selection-complete laterals; P3S standard endpoints are regression controls only" (L207) | see §Could not determine | undetermined |
| 102 | "NO covariance component or weight transfers automatically to the full-event estimator" (L228) | — | no check |
| 103 | "F10 … `build_truth_cloud` encodes azimuth as (cos φ, sin φ); KNN coord_idx=(5,6,7)" (L249) | `pet/fullevent_fps_dataloader.py:204`; `tests/test_fullevent_fps.py:96` | yes |
| 104 | "F9 … `smoke_fullevent_tf.py` t4 now saves/reloads `of.step2_models[0]` … and asserts it differs from the template" (L251) | `pet/smoke_fullevent_tf.py:105` | **no — never collected** |
| 105 | "F2 … `net.py` passes the token pad mask to `PET_head`; after FiLM `encoded *= token_mask`; … `attention_mask`" (L253) | — | no check |
| 106 | "F3 … raw logit head …; w = exp(clip(logit, ±`REWEIGHT_LOGIT_CAP`=30))" (L257) | `omnifold_nn/omnifold/omnifold.py:465`; `tests/test_b1_normalization_fix.py:1091` | yes *(partial: constant pinned, transform unexercised)* |
| 107 | "FAIL-CLOSED on non-finite logits, with saturated-count + weight-mass telemetry" (L259) | — | no check |
| 108 | "One shared implementation => identical in nominal/replicas/universes/extraction" (L261) | `tests/test_fullevent_extract.py:216` | yes |
| 109 | "Cap-sensitivity (25/30/35) is a P5B-nominal check" (L261) | — | no check |
| 110 | "Contract now spans THREE inventories (data, signal-MC, background-MC)" (L264) | `pet/fullevent_fps_dataloader.py:614`; `tests/test_fullevent_fps.py:318` | yes |
| 111 | "one global Poisson(1) per inventory over the FULL inventory BEFORE any subset; signal rng(seed+1e7); data rng(seed); bkg rng(seed+2e7)" (L266) | `pet/fullevent_fps_dataloader.py:614`–`:625`; `tests/test_fullevent_fps.py:325` | yes |
| 112 | "the background factor multiplies the … injection weight BEFORE Stay-Positive; refined target rebuilt PER REPLICA, never copied" (L269) | `pet/fullevent_fps_dataloader.py:642`; `tests/test_fullevent_fps.py:352`,`:363` | yes |
| 113 | "`validate_coherent_bootstrap` … FAIL-CLOSED on seed / inventory-order / fingerprint mismatch" (L271) | `pet/fullevent_fps_dataloader.py:750`; `tests/test_fullevent_fps.py:372` | yes |
| 114 | "draws global-before-subset and INDEXES by imc/ida — the post-subsample redraw is REMOVED" (L272) | `pet/fullevent_fps_dataloader.py:1241`; `tests/test_fullevent_fps.py:325` | yes *(partial: pure function only; loader path is in the failing gate2 tests)* |
| 115 | "persisting factors/seeds/mc_indices/inventory-order-hash/fingerprint in meta" (L273) | `pet/fullevent_fps_dataloader.py:1246`; `tests/test_fullevent_gate2.py:282` | **no — collected but fails off-cluster** |
| 116 | "`F7CoherentBootstrap` (7) covering deterministic replay, global-before-subset, …" (L274) | `tests/test_fullevent_fps.py:314`–`:418` (7 methods) | yes |
| 117 | "19/19 CPU tests pass" (L277) | — | no check |
| 118 | "F7 cannot execute or be declared CLOSED until the Option-A background inventory exists" (L278) | — | no check |
| 119 | "F8 … P5B adopts NO Horovod (independent single-rank GPU jobs)" (L284) | — | no check |
| 120 | "PRODUCTION DECISION GATE — DO NOT LAUNCH here" (L287) | — | no check |
| 121 | "G1. P5A committed" (L289) | — | no check |
| 122 | "G2. … dump branches added … AND FPS CV loops REGENERATED … (replaces the xps2 scaffolding)" (L290) | `pet/fullevent_fps_dataloader.py:1074`,`:1034` | yes |
| 123 | "G3. Agent C's P3F FPS active endpoints committed + gate-passed" (L293) | see §Could not determine | undetermined |
| 124 | "G4. Feature contract frozen (this file) with any reduction explicitly justified" (L295) | `pet/validate_pet_nominal_gate4.py:626`; `tests/test_pet_nominal_gate4_validator.py:143` | yes* |
| 125 | "No recoil-only covariance component or weight transfers to the full-event estimator" (L296) | — | no check |
| 126 | "Launch order (each on the frozen full-event FPS nominal, same mask/order/edges)" (L298) | — | no check |
| 127 | "reweight-all on full 49.2M" (L300) | `pet/extract_fullevent_fps.py:340`; `tests/test_fullevent_extract.py:120` | yes |
| 128 | "Freeze the reported-bin mask/cv/order here" (L301) | `pet/validate_pet_nominal_gate4.py:655`–`:684`; `tests/test_pet_nominal_gate4_validator.py:168` | yes* |
| 129 | "GPU FLOOR: 1 identical-seed repeat; record before interpreting C_stat/C_ML" (L302) | — | no check |
| 130 | "C_stat: coherent data+MC Poisson replicas (fixed est/split seed), replica-mean covariance, strict manifest" (L303) | `pet/fullevent_fps_dataloader.py:750`; `tests/test_fullevent_fps.py:372` | yes *(partial: coherence gate only; no C_stat assembler)* |
| 131 | "C_ML: PET-specific crossed (subsample-seed × TF-seed) ensemble, no Poisson" (L305) | — | no check |
| 132 | "apply the FULL physical input variation AND retrain … TOGETHER, then delta_u = x_u − x_CV … MAT mean-centered" (L306) | — | no check |
| 133 | "DO **NOT** form `C_syst_fixed_model + C_retraining`" (L313) | — | no check |
| 134 | "do NOT add a separate retraining covariance for a nuisance already carried by a joint … universe" (L315) | — | no check |
| 135 | "Targeted-endpoint → full-per-universe gate per PET_UQ_REMEDIATION_STATUS.md §6" (L316) | — | no check |
| 136 | "A nuisance that provably CANNOT change the mapping … may use the frozen-map response, documented" (L318) | — | no check |
| 137 | "The recoil-only campaign's additive C_syst+C_retrain is a QUARANTINED cross-check, never transferred" (L319) | — | no check |
| 138 | "SELECTION-COMPLETE LATERALS … NEVER P3S standard" (L321) | see §Could not determine | undetermined |
| 139 | "C_total = … on ONE mask/cv/order with the IDENTICAL estimator fingerprint on every component (reject on mismatch)" (L323) | — | no check |
| 140 | "NO separate additive C_retrain term" (L324) | — | no check |
| 141 | "Document each component's nuisance ownership + independence/coupling BEFORE summing; supply mean shifts" (L325) | — | no check |
| 142 | "PSD/symmetry/finite-diagonal" (L327) | — | no check *(recoil-only analogue runs)* |
| 143 | "exact 5D→4D marginal consistency" (L327) | — | no check *(recoil-only analogue runs)* |
| 144 | "extended-edge assertion" (L327) | — | no check *(function exists, never called at assembly)* |
| 145 | "two-tier reporting (Tier-1 measured vs Tier-2 prior-band)" (L328) | — | no check |
| 146 | "PET-vs-scalar only after both are on the SAME extended-FPS domain" (L329) | — | no check |
| 147 | "Coverage + 3-prior envelope on the extension regions" (L329) | — | no check |
| 148 | "Report candidate vs final products separately" (L330) | — | no check |
| 149 | "CPU for dumps/extraction/census/tests; GPU … for trainings" (L331) | — | no check |

## C.2 The 57 with no executable check — detail
### INV-1: "full-event PET over the declared extended-FPS fiducial phase space (NOT 'full phase space')"
doc line: 8
why nothing checks it: grepped the tree for any assertion on product naming/labelling strings; the only fingerprint strings checked are `pet-fullevent-fps-v1` / `pet-reduced-fps-cross`, which carry no phase-space wording.
what would have to be checkable: a naming lint over `products/pet/fullevent_fps/*` summaries and doc titles.

### INV-2: "PET trains UNBINNED on CONTINUOUS features"
doc line: 13
why nothing checks it: no test asserts the classifier input tensor contains no bin index. The nearest executable statement is the frozen `event_features_reco` list (`validate_pet_nominal_gate4.py:626`), which happens to contain only continuous quantities but does not test that property.
what would have to be checkable: a predicate over `_EVT_SPEC` asserting every adopted feature has a continuous transform.

### INV-3: "EDGES … never as classifier inputs or training bins"
doc line: 14
why nothing checks it: searched `build_fullevent_loaders`, `_EVT_SPEC` and the PET construction for any assertion that `edges_0`/`edges_1` never reach `reco_evt`/`gen_evt`/`reco`. Only the *value* of the edges is guarded, never their *use*.
what would have to be checkable: a guard asserting the edge arrays are not referenced downstream of the domain-retention step.

### INV-9: "Every P5B component … MUST carry ONE of these fingerprints and never mix the two"
doc line: 24
why nothing checks it: there is no full-event covariance assembler in the tree. `pet/assemble_ctotal_bkgsub.py`, `assemble_cretrain.py`, `combine_cml_bkgsub.py`, `combine_cstat_bkgsub.py` are all the recoil-only (`bkgsub`) path the doc quarantines at L225.
what would have to be checkable: a full-event `assemble_ctotal` that reads each component summary's `estimator_fingerprint` and rejects on mismatch.

### INV-10: "recoil-only PET UQ is NEVER attached to either"
doc line: 25
why nothing checks it: `RECOIL_OR_OLD_INPUT_MARKERS` (`fullevent_fps_dataloader.py:799`) screens input *paths*, not UQ products. No code reads `products/pet/bkgsub/` and refuses to attach it.
what would have to be checkable: a fingerprint field on every covariance product plus an assembly-time rejection of recoil-stamped components.

### INV-16: "Edges are reporting/covariance/validation only, never inputs"
doc line: 32
why nothing checks it: same search as INV-3; this is the feature-list restatement of it and is equally unenforced.
what would have to be checkable: as INV-3.

### INV-18: "non-finite→0 (pad/mask sentinel)"
doc line: 33
why nothing checks it: `_scale_clean` (`fullevent_fps_dataloader.py:130`) does the `nan_to_num`, but grepping every test for a NaN/inf fed into `build_reco_cloud`/`build_truth_cloud` returns nothing — all cloud fixtures are finite. (The *event-block* non-finite guard is well tested; the *cloud* one is not.)
what would have to be checkable: one fixture with a NaN token asserting the output is 0.

### INV-23: "batch 1024"
doc line: 36
why nothing checks it: the publication driver hardcodes `batch_size=512` (`pet/train_fullevent_nominal.py:239`), the artifact never persists a batch size, and `FROZEN["seed_policy"]` (`validate_pet_nominal_gate4.py:92`) has no batch entry. Grepped every test for a batch assertion on the full-event path: none.
what would have to be checkable: persist `batch_size` in the artifact and add it to `FROZEN["seed_policy"]`.

### INV-24: "Adam lr 1e-4"
doc line: 36
why nothing checks it: `1e-4` is the engine's default (`omnifold_nn/omnifold/omnifold.py:57`) and the driver never passes `lr`. Nothing persists or asserts it.
what would have to be checkable: persist the resolved `of.LR` in the artifact and freeze it.

### INV-27: "C_ml varies subsample/split seed × TF estimator seed …, no Poisson"
doc line: 38
why nothing checks it: no C_ML orchestrator exists for the full-event path (`pet/combine_cml_bkgsub.py` is the recoil one). Nothing enumerates the crossed design or asserts absence of Poisson.
what would have to be checkable: a C_ML manifest schema listing (subsample_seed, tf_seed) pairs with a no-`bootstrap_seed` assertion.

### INV-28: "nominal product `products/pet/fullevent_fps/pet_fullevent_fps_nominal_*`"
doc line: 40
why nothing checks it: `--out` is free-form in `train_fullevent_nominal.py:167`; no path-shape check anywhere.
what would have to be checkable: a launcher guard matching `--out` against the declared product prefix.

### INV-30: "fingerprint recipe … `sha256(git_commit(net.py,omnifold.py,dataloader.py,fullevent_fps_dataloader.py) || feature_list || preprocessing || edges || seed_policy || input_npz_sha)`"
doc line: 42
why nothing checks it: grepped the whole tree for `feature_list`, `git_commit`, `input_npz_sha`, "fingerprint recipe" — zero hits. `estimator_fingerprint` is everywhere a literal string, never a computed digest. `inputs_sha256` (`train_fullevent_nominal.py:342`) hashes only the input npz.
what would have to be checkable: implement the recipe as a function and have both the driver and validator compute it independently.

### INV-31: "Every covariance component summary must carry the SAME fingerprint or it is rejected at assembly"
doc line: 44
why nothing checks it: same as INV-9 — no full-event assembly step exists to do the rejecting.
what would have to be checkable: as INV-9.

### INV-35: "`build_fullevent_loaders` defaults to `bkg_mode=\"negweight-refined\"`"
doc line: 54
why nothing checks it: the signature default is correct (`fullevent_fps_dataloader.py:1044`) but no test calls the function without `bkg_mode` and asserts the negweight path. Every negweight test passes it explicitly. Separately, the module CLI defaults to `"purity"` (`:1377`), so the two defaults disagree with nothing to notice.
what would have to be checkable: one test inspecting the signature default, or a default-path call asserting `meta["bkg_mode"]`.

### INV-41: "consumers without the flag must verify embedded FPS provenance and fail closed"
doc line: 64
why nothing checks it: `build_fullevent_loaders` gates on `petSchemaVersion` only (`:1074`) — it never reads `fullPhaseSpace`. The `fullPhaseSpace=1` marker is checked at *write* time (`fullevent_dump_contract.py:41`) and at *launch* (`assert_publication_config:1026`), but a hand-built npz with `petSchemaVersion=g2-fullevent-v1` and `fullPhaseSpace=0` loads cleanly.
what would have to be checkable: add the `fullPhaseSpace` marker to the loader's own schema gate.

### INV-44: "Tier-1 acceptance-supported (eff≳2%), Tier-2 … carry a prior-dependence band"
doc line: 69
why nothing checks it: grepped for `Tier-1`/`Tier-2`/`tier` across `pet/` and `tests/` — the strings appear only in `FPS_PILOT.md` prose. No code computes an efficiency threshold or partitions the 285 cells.
what would have to be checkable: a reporting module that computes per-cell efficiency and emits a Tier partition the validator can gate on.

### INV-45: "Muon features cannot turn zero-efficiency cells into measured cells"
doc line: 70
why nothing checks it: no test compares the reported-cell mask before and after widening the event schema. `freeze:reported_mask_*` (`validate_pet_nominal_gate4.py:669`) checks length and non-emptiness only.
what would have to be checkable: a reduced-vs-full run whose reported masks are asserted identical.

### INV-52: "`*_view`, 1=X/2=U/3=V"
doc line: 85
why nothing checks it: every fixture generates views with `rng.integers(0,3)` or `(0,4)` (`test_fullevent_dump_contract.py:29`, `test_fullevent_gate2.py:59`) — arbitrary codes. No value-domain assertion exists on either the dump or loader side.
what would have to be checkable: a domain check that non-pad view entries are in {1,2,3}.

### INV-60: "muon±13 & ν removed at source"
doc line: 97
why nothing checks it: the C++ static guard (`pet/test_g2_fullevent_dump_schema.py`) checks forbidden truth-*detector* branches and the truth↔reco leakage screen, but never inspects `GetTruthFSHadrons`' body for the μ/ν exclusion. No Python-side PDG filter is asserted either.
what would have to be checkable: extend the static guard to pull `GetTruthFSHadrons`' body and require the ±13/±12/±14/±16 exclusion.

### INV-71: "z-normalized with the RECO-MC statistic (data and background use the reco norm)"
doc line: 114
why nothing checks it: the code is right (`fullevent_fps_dataloader.py:494` for `event_data`, `:1305` for `event_bkg`, both passing `(rmu, rsd)`), but grepping every test for an assertion tying `event_data`/`event_bkg` to `reco_norm_mean`/`reco_norm_std` returns nothing. `test_reco_and_data_share_a_schema_the_truth_leg_does_not` checks widths only.
what would have to be checkable: assert `event_data == (raw_data - meta["reco_norm_mean"]) / meta["reco_norm_std"]` on a fixture.

### INV-75: "STILL NOT DUMPED, so still absent: residual-energy summary tokens"
doc line: 124
why nothing checks it: a negative existence claim. `fullevent_dump_contract.REQUIRED_KEYS` (`:38`) simply omits them and the C++ guard's `expected` dict (`test_g2_fullevent_dump_schema.py:147`) does not list them. Nothing would fire if they appeared, nor if the doc went stale after they landed.
what would have to be checkable: an explicit assertion that the residual-token keys are absent from `REQUIRED_KEYS`, tied to the doc sentence.

### INV-81: "z-normalized with the TRUTH-MC statistic"
doc line: 137
why nothing checks it: `tmu`/`tsd` are computed at `fullevent_fps_dataloader.py:490` and applied at `:492`, but no test asserts `meta["truth_norm_mean"]` equals the pass_truth mean — the analogue of `test_sentinel_pass_masked_normalization` (`tests/test_fullevent_fps.py:266`) exists for the reco leg only. `assert_no_truth_leakage` proves the reco block is pure-reco; it says nothing about which statistic the truth block used.
what would have to be checkable: a truth-side mirror of the reco normalization-statistic assertion.

### INV-84: "Muon is a distinguished EVENT feature (FiLM conditioning), so cloud tokens are all recoil"
doc line: 144
why nothing checks it: no test asserts the muon never appears as a cloud token, and nothing in `tests/` references `net.py`'s FiLM path at all.
what would have to be checkable: an assertion that the reco cloud's token count/columns exclude the muon object.

### INV-85: "a muon/recoil/view type embedding is only needed if muon becomes a cloud token"
doc line: 145
why nothing checks it: conditional design statement; nothing in the tree tests for the absence of a type-embedding input.
what would have to be checkable: a network-shape assertion that `PET` is built with no type-embedding branch.

### INV-90: "they are masked by pass_reco in the step-1 loss"
doc line: 182
why nothing checks it: this is a property of the vendored engine's step-1 loss (`omnifold_nn/omnifold/omnifold.py`), and no test in `nd-unfolding/tests` exercises it. Every loss-path test would need TensorFlow.
what would have to be checkable: a numpy-level assertion that step-1 sample weights are zero on `~pass_reco` rows.

### INV-96: "a full event-by-event order proof … is a P5B hardening item"
doc line: 196
why nothing checks it: the doc declares this unmet. `fullevent_fps_dataloader.py:1160` and `fullevent_dump_contract.assert_inventory_alignment:70` enforce row *counts*; `inventory_order_hash:587` proves an inventory was not reordered *between* two reads but never proves data row *i* is the same physical event as MC row *i*.
what would have to be checkable: a stable event key (run/subrun/gate) dumped on both legs and compared row-wise.

### INV-99: "Nuclear-remnant truth token: not dumped"
doc line: 202
why nothing checks it: negative existence claim about the C++ dump; the static guard has no assertion on remnant branches.
what would have to be checkable: add a remnant-branch name to the guard's forbidden list at `test_g2_fullevent_dump_schema.py:250`.

### INV-102: "NO covariance component or weight transfers automatically to the full-event estimator"
doc line: 228
why nothing checks it: nothing reads `products/pet/bkgsub/` and refuses it; there is no full-event assembler to refuse it in.
what would have to be checkable: as INV-9, plus a path-marker guard on component inputs mirroring `RECOIL_OR_OLD_INPUT_MARKERS`.

### INV-105: "F2 … `net.py` passes the token pad mask to `PET_head`; after FiLM `encoded *= token_mask`; … `attention_mask`"
doc line: 253
why nothing checks it: `token_mask`/`attention_mask`/`PET_head` appear in `omnifold_nn/omnifold/net.py` and in this contract, and in no test file anywhere in the repo. Grep over all of `nd-unfolding/tests` and `nd-unfolding/pet` for those three symbols returns zero test hits.
what would have to be checkable: a shape/gradient test that padded tokens contribute nothing to the class token — needs TensorFlow, so cluster-only.

### INV-107: "FAIL-CLOSED on non-finite logits, with saturated-count + weight-mass telemetry"
doc line: 259
why nothing checks it: the code is at `omnifold_nn/omnifold/omnifold.py:465`-`469`; no test calls `MultiFold.reweight` (it needs TF). `tests/test_b1_normalization_fix.py:1091` reads the *constant* out of the source, not the behaviour.
what would have to be checkable: a TF smoke feeding a non-finite logit and asserting the raise — cluster-only.

### INV-109: "Cap-sensitivity (25/30/35) is a P5B-nominal check"
doc line: 261
why nothing checks it: `FROZEN["tolerances"]["cap_saturation_frac_max"]` (`validate_pet_nominal_gate4.py:102`) gates the saturation *fraction* at one cap; nothing runs the three-cap sweep or records its result.
what would have to be checkable: three extraction runs at cap ∈ {25,30,35} with a receipt field the gate reads.

### INV-117: "19/19 CPU tests pass"
doc line: 277
why nothing checks it: a count claim about a moment in time. `tests/test_fullevent_fps.py` now collects 35 tests, and no `TOTAL_CHECKS`-style pin exists for this file (unlike `tests/test_g2_guards_collected.py:49`, which does pin its counts).
what would have to be checkable: a count pin on the file, as the G2 guard wrapper does.

### INV-118: "F7 cannot execute or be declared CLOSED until the Option-A background inventory exists"
doc line: 278
why nothing checks it: the named artifact `runEventLoopOmniFold_PC_FPS_MEFHC_bkgcloud.root` appears in no code path; nothing asserts its absence keeps F7 open, and no status file is gated on it.
what would have to be checkable: a gate reading an F7 status field that cannot be set to CLOSED without the artifact's hash.

### INV-119: "F8 … P5B adopts NO Horovod (independent single-rank GPU jobs)"
doc line: 284
why nothing checks it: `build_fullevent_loaders` still accepts `rank`/`size` (`:1042`) and passes them to the DataLoader (`:1264`); no launcher guard forbids `size>1`, and no test asserts the sbatch scripts are single-rank.
what would have to be checkable: a launcher assertion that `size == 1`, or a script lint rejecting `horovodrun`/`hvd`.

### INV-120: "PRODUCTION DECISION GATE — DO NOT LAUNCH here"
doc line: 287
why nothing checks it: `tests/test_pet_fullevent_nominal_launcher.py:114` (`test_no_sbatch_or_submit_calls_in_script`) covers the *nominal launcher script*, not this document's gate, and this invariant is a procedural instruction to a reader.
what would have to be checkable: nothing executable — it is a human-process statement.

### INV-121: "G1. P5A committed (this interface + tests + contract + census + stress closure)"
doc line: 289
why nothing checks it: no receipt or gate file enumerates the five G1 artifacts; nothing blocks a P5B launch on their presence.
what would have to be checkable: a G1 manifest with hashes that the Gate-4 driver requires (as it already does for `--gate3-manifest`).

### INV-125: "No recoil-only covariance component or weight transfers to the full-event estimator"
doc line: 296
why nothing checks it: restatement of INV-102 inside the prerequisite list; same absence.
what would have to be checkable: as INV-102.

### INV-126: "Launch order (each on the frozen full-event FPS nominal, same mask/order/edges)"
doc line: 298
why nothing checks it: nothing enforces step ordering across the eight launch steps, and no shared mask/order/edges object is threaded through them (there is no C_total assembler to thread it into).
what would have to be checkable: a campaign manifest each step stamps and the next step verifies.

### INV-129: "GPU FLOOR: 1 identical-seed repeat; record before interpreting C_stat/C_ML"
doc line: 302
why nothing checks it: `--tag floor` exists (`train_fullevent_nominal.py:168`) but nothing asserts the floor run used identical seeds, nor that it precedes C_stat/C_ML interpretation.
what would have to be checkable: a floor receipt whose `seed_policy` is compared byte-for-byte against the nominal's, required before the C_stat gate.

### INV-131: "C_ML: PET-specific crossed (subsample-seed × TF-seed) ensemble, no Poisson"
doc line: 305
why nothing checks it: same as INV-27 — no full-event C_ML code path exists.
what would have to be checkable: as INV-27.

### INV-132: "apply the FULL physical input variation AND retrain … TOGETHER, then delta_u = x_u − x_CV … MAT mean-centered"
doc line: 306
why nothing checks it: grepped `pet/` for a full-event universe driver; `phase7_retrain_universe.py` is the recoil-era path and `pet_lateral_correction.py` is the scalar one. Nothing computes joint end-to-end deltas on the full-event estimator.
what would have to be checkable: a universe driver emitting per-universe `delta_u` receipts a covariance builder can gate on.

### INV-133: "DO **NOT** form `C_syst_fixed_model + C_retraining`"
doc line: 313
why nothing checks it: no full-event assembler exists to refuse the additive form. `pet/assemble_cretrain.py` *is* the recoil-only additive path and is unguarded against reuse.
what would have to be checkable: an assembler that rejects a component set containing both a fixed-model and a retraining term.

### INV-134: "do NOT add a separate retraining covariance for a nuisance already carried by a joint … universe"
doc line: 315
why nothing checks it: requires per-nuisance ownership metadata that no component summary carries.
what would have to be checkable: a `nuisance_owner` field per component plus a duplicate-ownership check.

### INV-135: "Targeted-endpoint → full-per-universe gate per PET_UQ_REMEDIATION_STATUS.md §6"
doc line: 316
why nothing checks it: the §6 materiality threshold is prose; no code reads it or computes the expansion decision.
what would have to be checkable: encode the §6 threshold and evaluate it against per-endpoint deltas.

### INV-136: "A nuisance that provably CANNOT change the mapping … may use the frozen-map response, documented as such"
doc line: 318
why nothing checks it: no component summary has a field recording "frozen-map, justified", so nothing can require the justification.
what would have to be checkable: a required `response_mode` + `justification` field validated at assembly.

### INV-137: "The recoil-only campaign's additive C_syst+C_retrain is a QUARANTINED cross-check, never transferred"
doc line: 319
why nothing checks it: the recoil assemblers run unguarded and nothing marks their outputs as untransferable.
what would have to be checkable: a quarantine stamp on `products/pet/bkgsub/*` that the full-event assembler rejects.

### INV-139: "C_total = … ONE mask/cv/order with the IDENTICAL estimator fingerprint on every component (reject on mismatch)"
doc line: 323
why nothing checks it: as INV-9/INV-31 — no full-event `assemble_ctotal`.
what would have to be checkable: as INV-9.

### INV-140: "NO separate additive C_retrain term"
doc line: 324
why nothing checks it: restatement of INV-133 at the summation step; same absence.
what would have to be checkable: as INV-133.

### INV-141: "Document each component's nuisance ownership + independence/coupling BEFORE summing; supply mean shifts"
doc line: 325
why nothing checks it: `nd-unfolding/fps_provenance.py:332`-`:344` does have mean-shift presence/finiteness checks (and they run — `tests/test_fps_provenance.py`), but that is the ND/FPS *scalar* provenance path, not the PET full-event one, and it carries no nuisance-ownership field.
what would have to be checkable: extend the provenance schema to the PET path with an ownership field.

### INV-142: "PSD/symmetry/finite-diagonal"
doc line: 327
why nothing checks it (for the full-event path): `pet/assemble_ctotal_bkgsub.psd_diagnostics` exists and is tested (`tests/test_pet_assembly.py:53`, runs), and `fps_provenance` has a PSD gate (`tests/test_fps_provenance.py:182`) — but both belong to the quarantined recoil / scalar-FPS paths. Nothing applies them to a full-event C_total, which does not exist.
what would have to be checkable: a full-event assembler reusing `psd_diagnostics`.

### INV-143: "exact 5D→4D marginal consistency"
doc line: 327
why nothing checks it (for the full-event path): `build_5d_to_4d_projection` is tested at `tests/test_pet_assembly.py:22` against a brute-force sum, but it is the recoil `assemble_ctotal_bkgsub` projection. The full-event estimator reports on a 2D (pT,p‖) grid and no 5D→4D full-event product exists.
what would have to be checkable: a full-event projection step, or the doc clause retired for this estimator.

### INV-144: "extended-edge assertion"
doc line: 327
why nothing checks it (at assembly): `assert_extended_fps_edges` exists (`fullevent_fps_dataloader.py:102`) and is called by the loader (`:1070`) and the extractor, but there is no assembly step to call it at, so the C_total-time assertion the sentence names never happens.
what would have to be checkable: call it from a full-event assembler.

### INV-145: "two-tier reporting (Tier-1 measured vs Tier-2 prior-band)"
doc line: 328
why nothing checks it: same absence as INV-44 — no Tier machinery exists anywhere.
what would have to be checkable: as INV-44.

### INV-146: "PET-vs-scalar only after both are on the SAME extended-FPS domain"
doc line: 329
why nothing checks it: `pet_vs_gbdt*.py` are the recoil-era comparison scripts; none of them asserts a common extended-FPS grid, and no full-event comparison script exists.
what would have to be checkable: a comparison entry point calling `assert_extended_fps_edges` on both inputs.

### INV-147: "Coverage + 3-prior envelope on the extension regions"
doc line: 329
why nothing checks it: the doc itself defers this (L244: "DEFERRED to P5B"). `nd-unfolding/fps_extension_validation.py` does coverage toys on the scalar FPS path; nothing does it for PET.
what would have to be checkable: a PET coverage/envelope product with a gated receipt.

### INV-148: "Report candidate vs final products separately"
doc line: 330
why nothing checks it: no product-status field exists on PET full-event outputs; nothing distinguishes candidate from final.
what would have to be checkable: a `product_status` field required in every summary.

### INV-149: "CPU for dumps/extraction/census/tests; GPU (shared + interactive) for trainings"
doc line: 331
why nothing checks it: a resourcing statement; no sbatch lint asserts the CPU/GPU partition per job class.
what would have to be checkable: a script lint over `pet/sbatch_*.sh` mapping job class to `--constraint`.

---

# Appendix D — category 4, all 308 unresolvable bindings

Columns: recorded path | frozen sha256 (first 16) | receipt that froze it | basename present in checkout

```text
/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/bin/runEventLoopOmniFold  |  61d7dfbf7ee38f39  |  nd-unfolding/pet/recover_g2_playlist.sh  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/bin/runEventLoopOmniFold  |  61d7dfbf7ee38f39  |  nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/bin/runEventLoopOmniFold  |  61d7dfbf7ee38f39  |  nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh  |  -
MINERvA101/opt/bin/runEventLoopOmniFold  |  61d7dfbf7ee38f39  |  nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json  |  -
g2-attempt2-terminal  |  ddfb87c26dfc3227  |  docs/orchestration/state/qp5-wake-reconciliation-20260719.json  |  -
nd-unfolding/g2_fullevent/logs/g2fe_dump_56116598.err  |  5794bd0cb1a35a1a  |  docs/orchestration/state/g2-dump-56116598-failure.json  |  -
active_universe_5d/fps/covariance/audit_merged_fps.json  |  19ca5c60aaaf7092  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  nd-unfolding/active_universe_5d/fps/covariance/audit_merged_fps.json
active_universe_5d/fps/covariance/fps_reported_mask.json  |  b994ec837fe32940  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  nd-unfolding/active_universe_5d/fps/covariance/fps_reported_mask.json
nd-unfolding/active_universe_5d/fps/preflight/p3s_fps_manifest_historical.json  |  8f957bf251728a7d  |  docs/orchestration/state/p3f-scalar-fullaudit-promotion-20260720.json  |  -
nd-unfolding/pet/g2_smoke/attempt2/g2_validation_v2.json  |  776addeb3453445b  |  nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json  |  -
active_universe_5d/fps/unfolds/unfold_BeamAngleX_0.log  |  9a337d92dd8ecaf2  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_BeamAngleX_1.log  |  cd54f145dd979219  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_BeamAngleY_0.log  |  e7592151fc99aa2d  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_BeamAngleY_1.log  |  e870ace3a0462d8b  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_MuonResolution_0.log  |  be5606aa1d3e3402  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_MuonResolution_1.log  |  13377275fe6bdd62  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_Muon_Energy_MINERvA_0.log  |  72668d97382cded3  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_Muon_Energy_MINERvA_1.log  |  4fb96596dd2dd6aa  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_Muon_Energy_MINOS_0.log  |  3d3608002881aa0b  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
active_universe_5d/fps/unfolds/unfold_Muon_Energy_MINOS_1.log  |  27c3a7c5bd04583c  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy  |  1ef7e0d2fa8c36a6  |  docs/orchestration/state/gate2-target-r4-reconciliation-20260719.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  docs/orchestration/state/g2-gate1b-npz-validation-20260719.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  nd-unfolding/g2_fullevent/gate2/benchmark/gate2-hedge-56139568/G2_GATE2_BENCHMARK.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  nd-unfolding/pet/run_gate2_target_validator.sh  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  nd-unfolding/pet/sbatch_pet_fullevent_nominal.sh  |  -
nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  docs/orchestration/state/gate2-queue-hedge-armed-20260719.json  |  -
nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260721.json  |  -
nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260731.json  |  -
nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz  |  fa6b346316024216  |  docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260801.json  |  -
nd-unfolding/products/pet/pet_weights_fps_xps2_delta_s101.npz  |  9a09125fd0cfd631  |  nd-unfolding/products/pet/pet_weights_fps_xps2_delta_s101.diagnostics.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55961845_0.out  |  515c2384e57cbb8a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_1.out  |  0a0ce89116293ced  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_10.out  |  9d4f3bb65cfec676  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_100.out  |  06bcbf209e9d6247  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_101.out  |  303005408f2e1751  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_102.out  |  e31ab9c1467d3614  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_103.out  |  72cda64836d3c237  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_104.out  |  37718711489c0eba  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_105.out  |  10875fdcb664baab  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_106.out  |  fdb63da7e940771b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_107.out  |  4b18f3721a3dc526  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_108.out  |  60843b8144c363b8  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_109.out  |  891c61052ce81fd4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_11.out  |  ad76076182903516  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_110.out  |  6d91fed56dc0e6ce  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_111.out  |  4b67cedf1875ac25  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_112.out  |  f9fd958915b6d92a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_113.out  |  7e1d01e18f7d13bd  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_114.out  |  c9b0dd5ad61cc7b1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_115.out  |  46fd696ef2b44261  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_116.out  |  0d6697369f221963  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_117.out  |  76407f07ef0edbe3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_118.out  |  40f7994052c39e75  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_119.out  |  2d507b136106a1f0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_12.out  |  241d2d36afa929af  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_13.out  |  4378d6356d6327ae  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_14.out  |  911c57c1babe93a9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_15.out  |  cd29d141f12064e8  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_16.out  |  ca4d4fd7030bfc5d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_17.out  |  c2617f1d828839c5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_18.out  |  62eb6399f1205f67  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_19.out  |  7702c0f64024d69d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_2.out  |  049bd5fa0bdef80b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_20.out  |  f680bdca39621ebb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_21.out  |  f60f3f619ff55fb2  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_22.out  |  fa0412f515a121cf  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_23.out  |  2da83587bde6731b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_24.out  |  86a301cba8d6fbef  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_25.out  |  a757227caa580753  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_26.out  |  5a5efcb636f32279  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_27.out  |  c22b2e17637ad901  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_28.out  |  75d15406c239db33  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_29.out  |  e452286964e05087  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_3.out  |  7cf7f7f88f435ed0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_30.out  |  abbd1a07137d02fb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_31.out  |  0834d3bac6ef0b2e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_32.out  |  a61ef3b529cad39d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_33.out  |  d4e87aa9e7d21d10  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_34.out  |  23cf69f01e706ee6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_35.out  |  5947e7ef03ece9f3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_36.out  |  f26a27f25f23c976  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_37.out  |  001fa597952c6dc8  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_38.out  |  40a6397ae05c8ae4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_39.out  |  538e68ee04604783  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_4.out  |  966a795e7e831959  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_40.out  |  3dd45fec26b68136  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_41.out  |  fb607dcca13cc25c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_42.out  |  092ebc42c3d530a6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_43.out  |  c5ecb8696526e5c0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_44.out  |  2c38c7b318a2c870  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_45.out  |  6c3c44a37f69a88a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_46.out  |  c38435830489fe37  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_47.out  |  e354e67436d95768  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_48.out  |  2832ec962456f513  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_49.out  |  88f48814fe61730d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_5.out  |  55e52b5f9cf43612  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_50.out  |  aca6433ed918bb0e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_51.out  |  8bc11a194ae9a5e0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_52.out  |  332eb213ec823e82  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_53.out  |  73513250f57230e1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_54.out  |  bc728bf63001414a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_55.out  |  426b0c65c4cb7734  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_56.out  |  503ae8190dc0cedc  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_57.out  |  8f14f4215a3352db  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_58.out  |  9adeca4379bac4e1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_59.out  |  117904ec00b8c34f  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_6.out  |  95ead7e26c25522d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_60.out  |  7303f8fc8fa67248  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_61.out  |  dbb41f59e508ee40  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_62.out  |  28b896e46342496c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_63.out  |  29332d354beaca06  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_64.out  |  6e7af044a341bbea  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_65.out  |  ceb48280cb442ed6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_66.out  |  c80d493042a974f6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_67.out  |  680d562661dbb235  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_68.out  |  c8f874cfba2fd749  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_69.out  |  5597ef8f5c19dd22  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_7.out  |  2d1fd57fffe5aa10  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_70.out  |  d92f9e292eadadd9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_71.out  |  76ede4f7a268c789  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_72.out  |  4fabffa7285819f9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_73.out  |  a0e4b7570e60b1da  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_74.out  |  54a8de49831c7d28  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_75.out  |  f619efdea43ecb26  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_76.out  |  c853d5fd9f33cb27  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_77.out  |  7e2871fafdd26a6f  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_78.out  |  7d24a683506c60f3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_79.out  |  208afe1354ce5bed  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_8.out  |  c311aba3309a6693  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_80.out  |  792bd0835091e81d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_81.out  |  5823fcdfff25dd18  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_82.out  |  0481120d0dc47912  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_83.out  |  00ebe21ddcea935e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_84.out  |  feb0ab904d9966c0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_85.out  |  c6f2388e8cdc5095  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_86.out  |  ebe55fe7b2df25d9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_87.out  |  eb7aaeae07628c7a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_88.out  |  2d7006534adfa337  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_89.out  |  063444a1eee918bb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_9.out  |  e407a0d0227c30c5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_90.out  |  e3057ae2bc3c6c68  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_91.out  |  a8e83fdb69a4efe2  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_92.out  |  e087708d188d4bc5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_93.out  |  79b88838b50de34c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_94.out  |  8d7ff0835b4ab69f  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_95.out  |  5f1b0f803b65dabb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_96.out  |  ed611ec2326f0491  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_97.out  |  33e647bdaf017b01  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_98.out  |  252acfd7f4726660  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/logs/ev5d_active_fps_55972324_99.out  |  c441bb70adaba2f8  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/g2_fullevent/logs/g2fe_dump_56116598.out  |  3d3f39fb07b3a6d9  |  docs/orchestration/state/g2-dump-56116598-failure.json  |  -
unfold_nd_omnifold_unbinned.py  |  9431d56a92e7d870  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  nd-unfolding/unfold_nd_omnifold_unbinned.py
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1A.root  |  be922fb79a83dbd1  |  nd-unfolding/g2_fullevent/final/G2_receipt_1A.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1A.root  |  be922fb79a83dbd1  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1B.root  |  a4a88415c7b56632  |  nd-unfolding/g2_fullevent/final/G2_receipt_1B.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1B.root  |  a4a88415c7b56632  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1C.root  |  518d90e495e155a5  |  nd-unfolding/g2_fullevent/final/G2_receipt_1C.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1C.root  |  518d90e495e155a5  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1D.root  |  06be7e6875f357af  |  nd-unfolding/g2_fullevent/final/G2_receipt_1D.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1D.root  |  06be7e6875f357af  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1E.root  |  6ab0ac90d75aa843  |  nd-unfolding/g2_fullevent/final/G2_receipt_1E.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1E.root  |  6ab0ac90d75aa843  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1F.root  |  b5e7c28f40325015  |  nd-unfolding/g2_fullevent/final/G2_receipt_1F.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1F.root  |  b5e7c28f40325015  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1G.root  |  70d7d0197e8ac141  |  nd-unfolding/g2_fullevent/final/G2_receipt_1G.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1G.root  |  70d7d0197e8ac141  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1L.root  |  a94ab3f4609e468a  |  nd-unfolding/g2_fullevent/final/G2_receipt_1L.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1L.root  |  a94ab3f4609e468a  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1M.root  |  819ec52f214f6971  |  nd-unfolding/g2_fullevent/final/G2_receipt_1M.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1M.root  |  819ec52f214f6971  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1N.root  |  2c9ef0d99c430d9d  |  nd-unfolding/g2_fullevent/final/G2_receipt_1N.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1N.root  |  2c9ef0d99c430d9d  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1O.root  |  d3ebb4ac272ecb2d  |  nd-unfolding/g2_fullevent/final/G2_receipt_1O.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1O.root  |  d3ebb4ac272ecb2d  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1P.root  |  e986dab2bc64fb80  |  nd-unfolding/g2_fullevent/final/G2_receipt_1P.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1P.root  |  e986dab2bc64fb80  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root  |  9a16331f1c02103e  |  docs/orchestration/state/g2-gate1b-npz-validation-20260719.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root  |  9a16331f1c02103e  |  nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json  |  -
/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root  |  9a16331f1c02103e  |  nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1A_active_BeamAngleX_0.root  |  6e0ee80619805e1f  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1B_active_BeamAngleX_0.root  |  466cde8b7b633c66  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1C_active_BeamAngleX_0.root  |  c47267562661c4d2  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1D_active_BeamAngleX_0.root  |  4ad1ebba568a2a3d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1E_active_BeamAngleX_0.root  |  bd6461ebb11de9a9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1F_active_BeamAngleX_0.root  |  d940b1f3d01421b0  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1G_active_BeamAngleX_0.root  |  4752df47057bc7ee  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1L_active_BeamAngleX_0.root  |  3d3031bf85e0a158  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1M_active_BeamAngleX_0.root  |  a339c4fe758c79d1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1N_active_BeamAngleX_0.root  |  02c4a2880ef30ecd  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1O_active_BeamAngleX_0.root  |  a5df5beda4d38629  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_0/runEventLoopOmniFold_5D_1P_active_BeamAngleX_0.root  |  ad9e6fc9c73096e5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1A_active_BeamAngleX_1.root  |  5eeb223c4cd2049d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1B_active_BeamAngleX_1.root  |  673a7d292f5d1d3b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1C_active_BeamAngleX_1.root  |  ba4724ac2762365a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1D_active_BeamAngleX_1.root  |  844437c3f9d3054a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1E_active_BeamAngleX_1.root  |  1c13c2bd1990b7fb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1F_active_BeamAngleX_1.root  |  4c116b95dc1fb26b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1G_active_BeamAngleX_1.root  |  d0680f5115991197  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1L_active_BeamAngleX_1.root  |  a51805dbcf14db78  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1M_active_BeamAngleX_1.root  |  24673636c592c717  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1N_active_BeamAngleX_1.root  |  8308b6200bd8104b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1O_active_BeamAngleX_1.root  |  a554eebd69c6a4c2  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleX_1/runEventLoopOmniFold_5D_1P_active_BeamAngleX_1.root  |  211b57edb1be1dc8  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1A_active_BeamAngleY_0.root  |  d24e403ba6219e4d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1B_active_BeamAngleY_0.root  |  1038d7f46381ac74  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1C_active_BeamAngleY_0.root  |  9bdb23ede5eb6c15  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1D_active_BeamAngleY_0.root  |  99df4e4339ca7b1a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1E_active_BeamAngleY_0.root  |  085652eca942b718  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1F_active_BeamAngleY_0.root  |  f9b97f353e6e1c02  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1G_active_BeamAngleY_0.root  |  cdf3539b3ba83ae3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1L_active_BeamAngleY_0.root  |  7d41915e11ab7fb4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1M_active_BeamAngleY_0.root  |  e5b42b081d8c297e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1N_active_BeamAngleY_0.root  |  8718d6c0d8a344b1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1O_active_BeamAngleY_0.root  |  8657c40b4fcba7db  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_0/runEventLoopOmniFold_5D_1P_active_BeamAngleY_0.root  |  7e99417f04310485  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1A_active_BeamAngleY_1.root  |  0976e39701b48b2b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1B_active_BeamAngleY_1.root  |  adff91fc6b81cf53  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1C_active_BeamAngleY_1.root  |  e84e1334ea24860b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1D_active_BeamAngleY_1.root  |  c9f13093759e6682  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1E_active_BeamAngleY_1.root  |  5fb66c02add01961  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1F_active_BeamAngleY_1.root  |  56e0a981ce050cc6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1G_active_BeamAngleY_1.root  |  8bdad31548401f38  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1L_active_BeamAngleY_1.root  |  0db79e179875d96f  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1M_active_BeamAngleY_1.root  |  c6d868ca47482408  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1N_active_BeamAngleY_1.root  |  1c4de6ee69d551ae  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1O_active_BeamAngleY_1.root  |  91dbe7da98a9a086  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/BeamAngleY_1/runEventLoopOmniFold_5D_1P_active_BeamAngleY_1.root  |  97340160d1b03b5c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1A_active_MuonResolution_0.root  |  d2e5a3b9a1f38504  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1B_active_MuonResolution_0.root  |  02f3b6829f86f2ca  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1C_active_MuonResolution_0.root  |  9799c7f3d3becd97  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1D_active_MuonResolution_0.root  |  efdd28c6924f2b4c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1E_active_MuonResolution_0.root  |  1c0a0c3a2771998b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1F_active_MuonResolution_0.root  |  16c08c1d5416c856  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1G_active_MuonResolution_0.root  |  0fdc7c1b36176c87  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1L_active_MuonResolution_0.root  |  8cf5ea7d4321f1ef  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1M_active_MuonResolution_0.root  |  64bd2c0e500066d5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1N_active_MuonResolution_0.root  |  07d1e0509250c3f4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1O_active_MuonResolution_0.root  |  d31d6ed784e47e46  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_0/runEventLoopOmniFold_5D_1P_active_MuonResolution_0.root  |  9bc611ada176e4dc  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1A_active_MuonResolution_1.root  |  e3e3af8e42b49c91  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1B_active_MuonResolution_1.root  |  1746dd4c4f08a6ee  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1C_active_MuonResolution_1.root  |  790143f68ed10560  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1D_active_MuonResolution_1.root  |  e963ba508ad0502d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1E_active_MuonResolution_1.root  |  31cc21e5583125f6  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1F_active_MuonResolution_1.root  |  199687eaead54488  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1G_active_MuonResolution_1.root  |  e9a5e71c6b114b7b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1L_active_MuonResolution_1.root  |  9006d2373c78ebe4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1M_active_MuonResolution_1.root  |  891c8c691d7f90c7  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1N_active_MuonResolution_1.root  |  08e460be87a0da59  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1O_active_MuonResolution_1.root  |  3fe6742c22ebaf38  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/MuonResolution_1/runEventLoopOmniFold_5D_1P_active_MuonResolution_1.root  |  5a891840bfc21d66  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1A_active_Muon_Energy_MINERvA_0.root  |  f1b53255c535dc1b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1B_active_Muon_Energy_MINERvA_0.root  |  3e04ff509f9171d5  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1C_active_Muon_Energy_MINERvA_0.root  |  ab898d98546bc56a  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1D_active_Muon_Energy_MINERvA_0.root  |  2363e358285f17f3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1E_active_Muon_Energy_MINERvA_0.root  |  b6143a750b67892d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1F_active_Muon_Energy_MINERvA_0.root  |  63d6947d5e490017  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1G_active_Muon_Energy_MINERvA_0.root  |  c300433eca9fd746  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1L_active_Muon_Energy_MINERvA_0.root  |  aa14b71ae859a975  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1M_active_Muon_Energy_MINERvA_0.root  |  76583615856dfb24  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1N_active_Muon_Energy_MINERvA_0.root  |  3a3651739abb3187  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1O_active_Muon_Energy_MINERvA_0.root  |  28836cd20588c0eb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_0/runEventLoopOmniFold_5D_1P_active_Muon_Energy_MINERvA_0.root  |  702eb9d1f6979497  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1A_active_Muon_Energy_MINERvA_1.root  |  0042c145892a0164  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1B_active_Muon_Energy_MINERvA_1.root  |  dc8b5efaacb06d9e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1C_active_Muon_Energy_MINERvA_1.root  |  05c0a1f5f8ae0bba  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1D_active_Muon_Energy_MINERvA_1.root  |  01a988fc4c0aa139  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1E_active_Muon_Energy_MINERvA_1.root  |  27df166701dee81e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1F_active_Muon_Energy_MINERvA_1.root  |  4949a6e22d4eff4c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1G_active_Muon_Energy_MINERvA_1.root  |  9df06b290ba9ef6c  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1L_active_Muon_Energy_MINERvA_1.root  |  897d0267fb624d99  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1M_active_Muon_Energy_MINERvA_1.root  |  3212b75b6020dedd  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1N_active_Muon_Energy_MINERvA_1.root  |  9ba6b9b185992f3d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1O_active_Muon_Energy_MINERvA_1.root  |  a1496ebef314a283  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINERvA_1/runEventLoopOmniFold_5D_1P_active_Muon_Energy_MINERvA_1.root  |  da8c3cfb989c1770  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1A_active_Muon_Energy_MINOS_0.root  |  f3509a2044340a16  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1B_active_Muon_Energy_MINOS_0.root  |  0eae2d97b1649019  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1C_active_Muon_Energy_MINOS_0.root  |  20a6b200b85173a3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1D_active_Muon_Energy_MINOS_0.root  |  6400a1094c3a6579  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1E_active_Muon_Energy_MINOS_0.root  |  73b05f3853290682  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1F_active_Muon_Energy_MINOS_0.root  |  36ed47f890de6a1d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1G_active_Muon_Energy_MINOS_0.root  |  ce93c5b7c215749d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1L_active_Muon_Energy_MINOS_0.root  |  68e5c60bf5c131c3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1M_active_Muon_Energy_MINOS_0.root  |  504a916ba93875f4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1N_active_Muon_Energy_MINOS_0.root  |  35e4487228a4179b  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1O_active_Muon_Energy_MINOS_0.root  |  d12355d8e86936f3  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_0/runEventLoopOmniFold_5D_1P_active_Muon_Energy_MINOS_0.root  |  44d51bad006cf5d4  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1A_active_Muon_Energy_MINOS_1.root  |  a1b465f67d6a56f7  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1B_active_Muon_Energy_MINOS_1.root  |  75897a395bdda72e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1C_active_Muon_Energy_MINOS_1.root  |  56444b19b9dd441d  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1D_active_Muon_Energy_MINOS_1.root  |  afcd97786e916fed  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1E_active_Muon_Energy_MINOS_1.root  |  cefc047a1632ec38  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1F_active_Muon_Energy_MINOS_1.root  |  bb336e9d53baa7a9  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1G_active_Muon_Energy_MINOS_1.root  |  2a3868285c48d791  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1L_active_Muon_Energy_MINOS_1.root  |  fa44accdbfaad8fc  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1M_active_Muon_Energy_MINOS_1.root  |  8a88274abd05a3a7  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1N_active_Muon_Energy_MINOS_1.root  |  ec451b746a75f26e  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1O_active_Muon_Energy_MINOS_1.root  |  6add96130c88e3eb  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/active_universe_5d/fps/Muon_Energy_MINOS_1/runEventLoopOmniFold_5D_1P_active_Muon_Energy_MINOS_1.root  |  83b8eca4009faec1  |  nd-unfolding/active_universe_5d/fps/p3s_fps_manifest.json  |  -
nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1D.root  |  06be7e6875f357af  |  docs/orchestration/state/g2-domain-recovery-20260719.json  |  -
nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1E.root  |  6ab0ac90d75aa843  |  docs/orchestration/state/g2-domain-recovery-20260719.json  |  -
nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1F.root  |  b5e7c28f40325015  |  docs/orchestration/state/g2-domain-recovery-r4-20260719.json  |  -
nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_1P.root  |  e986dab2bc64fb80  |  docs/orchestration/state/g2-domain-recovery-r4-20260719.json  |  -
nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root  |  51e46fddd061cae3  |  nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json  |  -
uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root  |  16d99350cbfe6997  |  nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json  |  -
uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root  |  16d99350cbfe6997  |  nd-unfolding/active_universe_5d/fps/covariance/fps_reported_mask.json  |  -
```
