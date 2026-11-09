# AMENDMENT A1a.1: the candidate's install at LL5D's entry points, and the entry points tested over the real chain (2026-11-09)

**By** the `cov2d` session, for `coverage-5b-audit` to audit and the director to bind as an addendum to LL5D binding 2.
The calibration's rerun waits for that addendum and the director's go.

**Under:**
- **The director's ruling on ll5d_calib run 1** (job 61014290, INVALID; receipt PR #963), 2026-11-09, by message. It is
  an implementation defect found before any result was computed: `calibration.json` was never written, and nothing was
  read that could inform a choice. So it is not a STOP under #939, and the fix is not a post-hoc repair. It changes
  bound code, so it comes as amendment A1a.1, then the audit, then a binding 2 addendum, then the go on the rerun.
- **LL5D BINDING 2** (A1a at `e92e946759772d13e21055b21c69189c8b007183`) and **BINDING 3** (A1b). Each file this
  amendment changes is named in §1.
- **The rerun** uses the same declared seeds and N = 3,000. Nothing about the calibration's design changes.

**MEASURES:** nothing. **CANNOT AUTHORIZE:**
- the rerun before the binding 2 addendum and the director's go;
- any change to the design.

**CITABLE FOR:**
- the fix;
- the tests and the mock inventory (§3), at the digests in §1.

**NOT CITABLE FOR:**
- any coverage statement;
- the estimator's behaviour.

## 1. What changes

| file | change |
|---|---|
| `nd-unfolding/ll5d.py` | `install_config()` = `s5e_candidate.install(toys.CONFIG)`, called once at the entry of `calib_main` and of `gate_main`, before anything reads a truth. This is exactly what `fd_1b_mc.run_unfold` does at `fd_1b_mc.py:507` at `dbaaf09d46f7bfcf671b04cc161cfd57c16222f7`. Nothing else changes. |
| `nd-unfolding/tests/test_ll5d.py` | the `RealChain` tests (§2); `pristine_s5n()`; the law-control assertions made structural (§2) |
| `nd-unfolding/tests/test_ll5d_b.py` | the `RealUnfold` test (§2). `ll5d_b.py` is unchanged, since A1b's `run_unfold` already installs the candidate. |
| `nd-unfolding/tests/ll5d_a1a_mutation.py`, `ll5d_a1b_mutation.py` | the install mutants: three for A1a, one for A1b |
| the calibration and gate job scripts (connects; not in this commit) | each ends with `exit $rc`, so sacct's state is the step's. Run 1 read COMPLETED 0:0 on rc 1. The connects' M and bound `ll5d.py` digest move to this amendment's merge, and their sha256s go to the director then. |

Digests (sha256) of the files at the commit the receipts were made at (`fd/receipts-ll5d/a1a1/README.md`):

| file | sha256 |
|---|---|
| `nd-unfolding/ll5d.py` | `b49f5d5f793265ef0cf569abe1912838cce9280e692f4dd61100d05c133aec1f` |
| `nd-unfolding/ll5d_b.py` (unchanged) | `24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb` |
| `nd-unfolding/tests/test_ll5d.py` | `cd4fddc2edda142a67dad20326cdc6e0910f40df0304c8bc3073aabe3dd3fddc` |
| `nd-unfolding/tests/test_ll5d_b.py` | `918d75bfd9c2c89faa0250918e52fdbccb2e9dd2e83bc2353b5d4b86ddebc0c2` |

**The mechanism** (run 1's receipt, #963):
- `fd_1b_mc.truth_weight` dispatches the "ratio_nd" truth model to `s5n_pseudo.truth_weight`.
- `s5e_deform.install_ratio_truth`, which `s5e_candidate.install` calls, registers that model.
- A1a's entry points never installed it, and its tests mocked `fd_1b_mc.truth_weight`, so no test ran the real path.

## 2. The tests that close the gap (the director's items 2 and 3)

**The fixture, `RealChain` (test_ll5d.py).**
- It is A2.1's toy world (`test_fd_1b.World`), rewritten on disk so its files agree as the real bank's do:
  - the bank's td_* rows in `cv.npz`;
  - every bank tdw about tdw_ref within 2 % row by row;
  - the six bank GEANT tdw equal to tdw_ref;
  - the npz's and every detector universe's `denom_nd` equal to hist(tdw_ref);
  - the background dump's meta updated.
- It is then re-pinned (the detector receipt, the sf1-style manifest, `toys.make_pins`) and given a staged flux table.
- **Mocked, outside the chain only:**
  - the H2 definition's map and S1's functional (`s1_assemble`; the toy grid);
  - S1's assembly and reported matrix (`fd_1b_score`; the gate only);
  - the world's own patches (the input and constraint digests, the toy's sentinel rows and F1 sums);
  - O_NOATIME off (macOS);
  - the thread variables;
  - `ll5d.TDW_REF_SHA256`, set to the fixture's tdw_ref digest.
- **`pristine_s5n()`** puts `s5n_pseudo`'s own definitions, loaded afresh from its source, over the shared module for
  each test. Each test then starts from a fresh process's state, whatever earlier tests installed.

**The REQUIRED test.** `RealChain.test_truths_r_runs_the_real_truth_weight_after_the_install`:
- `truths_r` over the world's real F1 prep ratios, with `fd_1b_mc.truth_weight` unmocked, raises `ValueError("ratio_nd")`
  in the fresh state. That is run 1's crash.
- After `install_config()` it returns finite, positive r_T, different for the two truths.
- Its mutant (`install_config` installing nothing) is killed.

**The entry points, over the real chain:**
- `RealChain.test_calib_main_runs_the_real_chain`: `calib_main` from the fresh state, at N = 300 with 20 sets. It
  installs, loads the world, reads tdw_ref with D1, the truths and every universe, and writes its record. The install
  mutant is killed.
- `RealChain.test_gate_main_runs_the_real_chain`: `gate_main` from the fresh state. D1–D3 pass, r_T > 0, the receipt
  over the declared draws in both readings passes, the sealed clip-prep file is written, and the gate reads. The
  install mutant is killed.
- `RealUnfold.test_run_unfold_runs_every_role_over_the_real_chain` (test_ll5d_b.py): A1b's `run_unfold` for every role:
  central, seed, three blocks (an interaction, a Flux, a detector universe), a stat replica, a toy in each reading, the
  clipmean in each reading from the real gate's sealed clip-prep file by its sha256, and three controls.
  - The estimator is the only stand-in.
  - It makes 13 products. The `minus2` toy holds neither removed band, and the clipmean records the seal's sha256.
  - The install mutant (`ll5d_b.run_unfold` without the install) is killed.

**A fragile assertion found and replaced.**
- Two tests asserted that the law control holds on a toy null of 20 or 40 sets.
- That is 64 z-values at 4 SE estimated from that few sets. By the t distribution it fails in about 2–5 % of worlds,
  and PYTHONHASHSEED=17 reproduced it.
- They now check that the control was computed: finite z for every evaluation and cell, and a boolean verdict. The
  rule itself is `fd_1b_c2.control`, verbatim from `342c0ce5`.

**Found while making this amendment's receipts, and fixed before they were committed:**
- **Two install mutants survived the first run:** the gate's and `run_unfold`'s. Each test ran the calibration first,
  and its install carried over within the test. Each entry point now runs inside its own `pristine_s5n()`, and both
  mutants are killed.
- **Under numpy 2,** the toy world's constraint file carried `np.float64(...)` reprs, which the constraint reader
  cannot parse. This is the same cause as main's pre-existing numpy-2 errors in `test_fd_1b_mc`. `RealChain` rewrites
  the file in plain floats.
- **Seed values leaked into the verbose test logs:** the seed test's docstring wrote section 3.6's range, and
  `run_unfold` printed product names. A1a's collision check scans tracked `.txt` files, so these would have failed it
  once committed. The docstring no longer writes the range, and the test captures `run_unfold`'s output.
  - **For the director: a follow-up, not part of this amendment.** The pilot's and the bulk's receipts will carry
    product names with toy seeds (`ll5d_<truth>_toy_<reading>_<seed>.npz`) in their logs. A1a's check would flag
    those once they are committed, unless each is added to `OWN_SEED_FILES` by exact path, or the check's scope over
    receipts is ruled on.

## 3. Every other mock in test_ll5d.py and test_ll5d_b.py, and what covers it (the director's item 3)

| mock (target) | where | why it is safe, or what now covers the real call |
|---|---|---|
| `fd_1b_mc._load_world`, `ll5d.verified_weights`, `fd_1b_mc.truth_ratio`, `fd_1b_mc.truth_weight`, `fd_1b_mc.via_noatime` | test_ll5d `Jobs` (job_patches); test_ll5d_b `World` | **the gap.** Their real calls are now covered end to end by `RealChain` (calib_main, gate_main) and `RealUnfold` (run_unfold). The unit tests keep these mocks for their rule-level fixtures (consistent weights in memory). |
| `fd_1b_mc._unfold_s1`, `_unfold`, `_unfold_one64`, `_unfold_one32` (the estimator) | test_ll5d_b `Unfold`; `RealUnfold` (as `unfold_fn`) | OmniFold is not run on a test host. On the cluster the pilot's procedure controls (§10: four products reproduce S1's bitwise) and its walls are where the real estimator meets this code first. |
| `s1_assemble.fine_map`, `functional_matrix` | both suites, `RealChain` | they require the real H2 definition's digests and the real 5D grid. On the cluster, `c2_inputs` and the readouts require the definition's functional to equal S1's stored U (`same_functional`), and refuse otherwise. |
| `fd_1b_score.load_s1`, `reported_matrix` | both suites, `RealChain` (gate) | S1's assembly and data product are digest-pinned campaign files, which `fd_1b_score` (unchanged) checks on the cluster. `same_functional` holds U to S1's. |
| `fd_1b_mc.cmodel_parts`, `made_from` | test_ll5d_b `Pipeline` | C_model's committed builder and the definition's digests are campaign records. On the cluster `cmodel_parts` (unchanged) rebuilds S1's C_model to 10⁻¹² or refuses. |
| `fd_1b_null.null_contents` (fewer MC vectors) | test_ll5d_b `Pipeline` | the same function at 20,000 vectors instead of 2,000,000, for speed. |
| `fd_1b_mc.truth_weight` (a non-positive r) | test_ll5d_b `Unfold.test_r_t_must_be_positive_everywhere` | it injects a failure to test the refusal. |
| `fd_1b_mc.stat_experiment`, `fd_1b_c2.set_ratios`, `fd_1b_c2.c2_truth` | spies | pass-through wrappers that record or (P1's test) perturb one value of the real call's result. |
| `ll5d.truths_r` | `Jobs.test_a_failed_control_is_invalid_before_anything_is_read` | it forces a failed control. The real `truths_r` is covered by the REQUIRED test. |
| `ll5d.receipt` | `Jobs.test_the_clip_prep_is_sealed_and_moves_no_verdict` | it wraps the real receipt and drops the sealed products, to show the verdict's independence. |
| `ll5d.RECEIPT_PROBE`, `ll5d.TDW_REF_SHA256` | `Jobs`, fixtures | constants: the probe's size, and the fixture's own tdw_ref digest. The digest logic runs for real. |
| `fd_1b_toys.source_factors` | `SourceFactors` | replaced by a function that raises, to show it is never called. |
| `ll5d.calib_main`, `gate_main`; `ll5d_b.null_step`; `fd_1b_inv.atime_check` | `ExitCodes` (both suites) | they test `main()`'s exit-code and INVALID mapping alone. The entry points themselves are covered by `RealChain`. |
| `ll5d_b.weakened`; `ll5d_b.json.loads` | test_ll5d_b `Pipeline` | removing the label (it moves no verdict); a recording dict (the allowlist). |
| `fd_1b_inv.NOATIME_FLAG`, `fd_1b_inv.os.open`, `builtins.open`, `io.open` | every fixture; the `NoAtime` tests | macOS has no O_NOATIME. The NoAtime tests set a flag bit and record every open. The cluster has the flag. |
| `os.environ` (the thread variables) | fixtures, `ExitCodes` | the environment. `require_threads` is tested both ways. |
| `test_fd_1b.World.patches`: the input, background and constraint digests in `s1_assemble`, `s5p_universe.SENTINEL_ROWS`, `fd_1b_toys.F1_SUMS`, `fd_f1_tasks` | every fixture | the toy files' digests and constants in place of the real ones. The digest checks themselves run. |
| `s5n_pseudo` (`pristine_s5n`) | `RealChain`, `RealUnfold` | not a stand-in: it restores a fresh process's state. |
<!-- absence-ok: a scoping statement about the test host; the estimator runs on the cluster, first in the pilot -->

**A1b's entry points:**
- `run_unfold`: covered by `RealUnfold`, over the real chain except the estimator.
- `null_step` and `readout`: run on synthetic products in `Pipeline`, with the S1, C_model and definition stand-ins
  above. They read no truth weight and no universe weight.
- `clipcheck`: reads products and the sealed file only. `clip_offset` is tested directly.

## 4. Results

**Receipts** (`fd/receipts-ll5d/a1a1/`, made at `c58c0eda2f4ea6f4e3aec3b8c5800389bd0820da` from a clean checkout):
- `test_ll5d.py`: 72 tests, OK, at PYTHONHASHSEED 0, 1 and 2 under numpy 1.26.4, and OK under numpy 2.4.4.
- `test_ll5d_b.py`: 29 tests, OK, the same.
- `ll5d_a1a_mutation.py`: 50 mutants, all killed, the unmutated control PASS (72 tests).
- `ll5d_a1b_mutation.py`: 27 mutants, all killed, the unmutated control PASS (29 tests, none skipped).
- No receipt carries a seed value.

Nothing is submitted, deposited or tagged.
