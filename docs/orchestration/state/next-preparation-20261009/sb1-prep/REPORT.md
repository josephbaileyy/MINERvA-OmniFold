# SB1 preparation: the selective-read benchmark package, ready for a resource decision

**CITABLE FOR:** what prototype 1 reads on the real universe omnifile (its derived branch sets and
selected bytes for the three patterns SB1 uses); the local, synthetic byte-equality evidence and its
negative and mutation controls; the frozen SB1 plan, its success and abort rules, its exact commands,
and its cost ceiling; which file bytes and which admission a later launch is bound to.
**NOT CITABLE FOR:** any Perlmutter throughput, memory or I/O of prototype 1 (nothing ran there);
equality on the real file (it is what SB1 would measure); any scientific result, uncertainty,
estimator equivalence, coverage, adoption, gate, production speedup, or compute authority. This
package is a proposal. It authorizes nothing, and nothing in it has been executed on the cluster.

| field | content |
|---|---|
| `Lane` | SB1 preparation (`sb1-prep`), next-preparation batch 2026-10-09 |
| `Decision` | *Is SB1 ready to measure whether reading only required ROOT branches preserves the actual production inputs and materially reduces universe-file I/O, memory and elapsed time at matched settings?* |
| `Branch` / `Base` / `Head` | `prep/sb1-ready-20261009` / `a16d5786` (merge of PR #68, the verified integration of the six lanes; `origin/main` at 2026-10-10T04:34Z) / the commit that carries this revision; the reviewed commits are in §11 |
| `Owned files` | everything under `docs/orchestration/state/next-preparation-20261009/sb1-prep/` (listed in §13). No other path was written |
| `Pinned inputs` | §2: driver sha256 `3cc5adc7…` (blob `e19aeb6d`), helper `e96234124a31…`, `n2/execution.py` `f35dacc6…`, guard `30162f57…`; speed head `318d3e45`, guard head `63257cd4`, structure head `0f4a059f` (all ancestors of the base); real-file operands read on a login node (`operands/`) |
| `Resources` | §14. Cluster compute, GPU, training, classifier fits: **0** |
| `Review` | §11 |
| `Model / effort` | owner: Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; effort not observable to the session |
| `Disposition` | §15 |
| `Next action` | §16: Joseph decides whether to permit running this fixed package under its 2.0 node-h cap |

`Q` = `docs/orchestration/state/next-preparation-20261009`; `P` = `Q/sb1-prep`.

## 0. Setup (campaign review §1)

- **Decision and terminals.** The decision is the sentence above. PASS: a complete, reviewed package
  that a named resource authorization can execute without inventing parameters. FAIL: its correctness
  or cost requirements demonstrably cannot be met. INCONCLUSIVE: a missing environment, input or
  measurement prevents admission.
- **Roles.** One owner (this session) and one fresh read-only reviewer on the frozen package: one
  initial review and one focused re-review after a single repair batch. The reviewer is a Claude
  subagent of the same model family, so the review is not cross-provider independent.
- **Budget.** 6 active hours including review, 3 local CPU core-hours, two compute threads, 8 GiB
  RAM, 2 GiB scratch, 10 MiB tracked; the final quarter protected. Cluster, GPU, training: 0.

## 1. Answer in brief

- **Yes, with one honest change to the specified comparison.** The package measures, on Perlmutter,
  exactly the question asked, at matched settings, inside the 2.0 node-h ceiling: planned ceilings
  sum to **1.699 node-h** (expected ≈ 1.19), and every verification is inside it. There are no
  retries under an admission; any failure ends SB1 INCONCLUSIVE.
- **The change.** Speed §9 compared two prototype-1 unfolds with the existing `purity_newomni`
  products. Those products were made by the July driver revision, so by this assignment's rule they
  cannot be a matched comparison. SB1 therefore runs its two 128-thread LightGBM universe unfolds as
  a **matched pair** on one genuinely lateral universe: `UL` (production loaders, every branch
  active) and `SL` (prototype 1). Both use the same commit, argv, node shape and threads. The
  historical products remain declared references, compared descriptively and marked UNMATCHED. The
  vertical universe `Flux:0`, which speed planned as a second prototype unfold, is covered by input
  identity only (§3.3). Measuring both universes as matched pairs would need a revised request of
  ≈ 2.85 node-h of ceilings (§7.5).
- **The lateral example is real, not a label.** The GEANT bands are vertical; speed's synthetic
  "lateral" `GEANT:0` was a mislabel. On the real file the lateral bands are BeamAngleX/Y,
  MuonResolution and Muon_Energy_MINERvA/MINOS. A read of 20,000 entries shows `Muon_Energy_MINOS_0`
  shifting the reconstructed kinematics in 100 % of rows, on signal and background. It also shifts
  the truth, reco and background weights in 70–92 % of rows. So SB1 uses `Muon_Energy_MINOS:0`
  (§3.2).
- **Prototype 1 is complete for all four loaders.** Branch sets are derived from the pinned loaders'
  own accesses, checked against an independent rule, and enforced so that an omitted or extra
  activation is refused before any value is read. On the real file's schema, a lateral universe
  unfold would read **2.18 GB of 171.10 GB** of zipped branch data (§4).
- **One real hazard was found and closed.** Reusing a tree after a pinned loader returns writes into
  freed buffers once its branches are re-activated. The test interpreter died with a segmentation
  violation. The wrapper now restores branch addresses as well as statuses (§4.3).
- **Equality is mandatory, and it is not coverage.** SB1 fails on the first loader byte difference,
  before training. An output difference with identical inputs is INCONCLUSIVE for output
  equivalence, never a failure of prototype 1. Byte equality on three patterns proves nothing about
  the other 185 universes' values, and nothing about any estimator, uncertainty or coverage (§6).

## 2. Baseline, inputs and what was read

- `git fetch origin` at 2026-10-10T04:34Z: `origin/main` = `a16d5786`. That is the merge of PR #68,
  whose integration REPORT records PASS on re-review. It is the verified merged pin, and the
  worktree `MINERvA-OmniFold-sb1-prep-20261009` was created from it on `prep/sb1-ready-20261009`.
  Speed `318d3e45`, guard `63257cd4` and structure `0f4a059f` are ancestors of it.
- Read: `AGENTS.md`; `CAMPAIGN-REVIEW-20260929.md`; `docs/CURRENT_WORK.md`;
  `docs/LOCAL_CHECKOUTS_AND_STORAGE.md`; integration REPORT §1–§12; speed REPORT §0–§15 with its
  `proto/`, `bench/` and `operands/`; guard-relevant parts of `nd-unfolding/mnv_guarded_run.py`;
  `n2/execution.py` and `n2/harness.py`; the n2 producer and dependency tests; the 2D driver's
  loaders, `main()` and provenance (`2d-unfolding/unfold_2d_omnifold_unbinned.py:211-336, 455-770,
  994-1033, 1306-1440, 1712-1790`); the C++ universe-branch writer
  (`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:221-380`); the two reference
  launchers (`2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh`,
  `Q/../ki84-rebuild-20261006/sbatch_ki84_replicas.sh`).
- **Callers and hash bindings of the driver.** The driver is not edited, and its blob `e19aeb6d` is
  bound by other receipts (speed §9, `verify_hash_bindings.py`). SB1 executes it from verified bytes
  and refuses any other sha256 (`sb1_run.py` `DRIVER_SHA256`).
- **Read-only remote evidence** (an authenticated `ssh` to `saul.nersc.gov`, login node only; no
  compute, no bulk copy):
  - `operands/universe_branches.json`: every tree's branch names, types and zipped bytes for both
    omnifiles, from the TTree headers (`operands/list_branches.py`).
  - `operands/lateral_probe.json`: the first 20,000 entries of the candidate bands' branches
    (`operands/lateral_probe.py`), a few MB read.
  - `operands/sacct_reference_and_billing.psv`: `sacct` of the completed reference jobs, with their
    billing TRES.
  - `operands/input_stat_20261010.psv`: `stat` of the three inputs. No prior sha256 of the universe
    file exists in the repository (searched), so the admission binds the file by size, mtime and
    inode, and SB1 hashes it before and after (§7.3).

## 3. What SB1 measures, and why its design moved from speed §9

### 3.1 The narrow comparison, preserved

The assignment fixes three components: matched input equality first; two 128-thread LightGBM
universe unfolds against the declared references; one shared-64 CV replica for a phase profile. All
three are kept. Their realization changes in two places, and both are forced by rules of the
assignment rather than by convenience:

| speed §9 | here | why |
|---|---|---|
| (a) all four loaders, all modes, on a full node (≈ 0.75 node-h), before any unfold | identity measured in every pattern: lateral inside `UL`/`SL` (`SL` stops before training on a difference); vertical in `J1` (loaders only, shared 64); CV in `C` | the all-branch read for the lateral pattern is exactly the read `UL` already pays for; doing it twice spends 0.75 node-h on duplicate bytes |
| (b) two prototype-1 unfolds (`Flux:0`, lateral) compared with `purity_newomni` products | `UL` (production loaders) and `SL` (prototype 1) on the lateral universe, same commit, argv, threads and node shape; the products are compared too, as UNMATCHED | the products come from another driver revision, so they "cannot be called a matched comparison" (assignment item 5). A matched timing, I/O, memory and output comparison needs a same-revision production arm |
| (c) one shared-64 CV replica with phase timers | unchanged, plus the CV pattern's loader identity on the same file | the CV pattern is part of the decision's input set |

### 3.2 The genuinely lateral universe

The C++ writer marks a universe lateral when `!IsVerticalOnly()` and writes shifted kinematics under
tree-specific names (`runEventLoopOmniFold.cpp:238-245, 309-380`). On the real file
(`operands/universe_branches.json`):

- `mc_truth_denom` uses `pT_truth_<b>`/`pz_truth_<b>`;
- `mc_signal_reco` uses `MC_<b>`/`MC_pz_<b>` and `sim_<b>`/`sim_pz_<b>`;
- `mc_background` uses `sim_background_<b>`/`sim_background_pz_<b>`;
- the bands with such branches are exactly BeamAngleX/Y, MuonResolution, Muon_Energy_MINERvA and
  Muon_Energy_MINOS (10 universes). GEANT bands have weight branches only.

`operands/lateral_probe.json`, fraction of the first 20,000 rows where the shifted branch differs
from CV:

| band | reco kinematics (signal, background) | truth kinematics | weights (truth / reco / bkg) |
|---|---|---|---|
| `Muon_Energy_MINOS_0` | 1.00, 1.00 | 0.00 | 0.91 / 0.92 / 0.70 |
| `Muon_Energy_MINERvA_0` | 1.00, 1.00 | 0.00 | 0 / 0 / 0 |
| `BeamAngleX_0`, `MuonResolution_0` | 1.00, 1.00 | 0.00 | 0 / 0 / 0 |
| `GEANT_Neutron_0` (vertical) | branches absent | absent | 0 / 0.52 / 0.60 |
| `Flux_0` (vertical) | absent | absent | 1.00 / 1.00 / 1.00 |

`Muon_Energy_MINOS:0` exercises the lateral kinematic swap on both reco trees and a weight variation
on all three MC trees. Its reference product is `55677843_166`: 2,617 s, MaxRSS 69,191,672 KiB
(70.85 GB), MaxDiskRead 167,271,319 KiB (171.29 GB).

**A limit of the real-file identity check.** The shifted truth kinematics equal CV in every sampled
row, and so do `MC_<b>`/`MC_pz_<b>` on `mc_signal_reco` (100 % equal in the sample). On real data a
loader that read `MC` instead of `pT_truth_<b>` or `MC_<b>` would return identical bytes, so
real-data equality cannot detect either substitution. Two other checks guard it: the derived branch
names (the selective arm activates exactly the names the pinned loader addresses, so a substitution
is impossible by construction), and the synthetic fixture, whose truth-lateral values differ from
CV (`test_a_wrong_rule_and_access_that_agree_are_caught_by_the_bytes`).

### 3.3 The vertical universe

`Flux:0` gets loader identity in `J1`: the four production loaders run with every branch active,
then the four prototype-1 loaders run, and digests are compared tree by tree. There is no `Flux:0`
unfold. Timing and memory are measured on the lateral pair only. That is a shrink, and it is stated
as one. The vertical pattern reads 2.145 GB against the lateral 2.181 GB, so the timing result is
expected to carry over, but that is a forecast. An exact request to measure it as well is in §7.5.

## 4. Prototype 1, complete (`branch_select.py`)

### 4.1 Mechanism

- **Derived from actual accesses.** `discover()` runs the pinned loader against `DiscoveryTree`.
  It forwards only the schema queries the loaders make (`GetBranch`, `GetListOfBranches`,
  `GetName`, `GetEntries`). It records each `SetBranchAddress` name without forwarding it, and
  raises at the first `GetEntry`. No entry is read, no address is left on the real tree
  (`test_discovery_reads_no_entry_and_leaves_no_address`), and any other tree method raises
  `UnmodelledAccess`.
- **Checked against a second statement.** `expected_branches()` restates the driver's selection
  rules (driver 211-219, 280-303, 551-572, 636-690). `derive()` refuses unless the access record
  equals it name for name and in order. The alt-model closure path is refused (not SB1's).
- **Refused before the first read.** `SelectiveTree` refuses `SetBranchAddress` on a name outside
  the derived set or on an inactive branch. At the first `GetEntry` it refuses unless the addressed,
  active and derived sets are equal and every derived branch holds a non-null address. Its interface
  is closed, like the discovery proxy's. After that check, `GetEntry` is rebound straight to ROOT,
  so the guard costs nothing per row.
- **Production arm.** `call_all()` runs the pinned loader unchanged and refuses unless every branch
  is active on entry. So the production arm cannot silently inherit a selection.
- **Digests.** For every array a loader returns, the sha256 of dtype, shape and bytes; for the two
  fill loaders, also the filled histogram's contents, Sumw2, statistics and entries.

### 4.2 Branch sets on the real schema (`results/costs.json`)

| pattern | `data` | `mc_background` | `mc_signal_reco` | `mc_truth_denom` | selected / all zipped bytes |
|---|---|---|---|---|---|
| lateral `Muon_Energy_MINOS:0` | `measured`, `measured_pz`, `measured_pass` | `sim_background_<b>`, `sim_background_pz_<b>`, `sim_background_pass`, `w_bkg_<b>` | `MC_<b>`, `MC_pz_<b>`, `sim_<b>`, `sim_pz_<b>`, `sim_pass`, `w_truth_<b>`, `w_reco_<b>` | `pT_truth_<b>`, `pz_truth_<b>`, `w_truth_<b>` | 2.181 / 171.098 GB |
| vertical `Flux:0` | same | CV kinematics, `sim_background_pass`, `w_bkg_Flux_0` | `MC`, `MC_pz`, `sim`, `sim_pz`, `sim_pass`, `w_truth_Flux_0`, `w_reco_Flux_0` | `MC`, `MC_pz`, `w_truth_Flux_0` | 2.145 / 171.098 GB |
| CV (CV file) | same | `sim_background`, `sim_background_pz`, `sim_background_pass`, `w_bkg` | the seven CV branches | `MC`, `MC_pz`, `w_truth` | 2.144 / 2.144 GB (the CV file holds nothing else) |

### 4.3 The reuse hazard, found by the restore test

The pinned loaders bind branches to `array` buffers local to the call. After the call returns,
Python frees them, but the branches keep the addresses. The production driver never reads such a
tree again. A wrapper that restores the statuses of a reused tree, though, re-activates those
branches, and the next `GetEntry` writes into freed memory. The first run of
`test_a_reused_tree_is_restored_and_reads_identically_afterwards` ended in `*** Break ***
segmentation violation` inside `array` allocation. `call_selective()` now snapshots the addresses of
the branches it lets the loader touch and restores them exactly (null on a fresh tree), then
verifies them. Mutant `restore-addresses-dropped` (§5.3) shows that the test catches the reversion.

## 5. Local verification (synthetic inputs only)

### 5.1 Fixture (`tests/make_fixture_omnifile.py`)

The fixture is a small omnifile in the real schema: the four trees, the real names and types
(`UChar_t` pass flags, `Int_t` counters), decoy branches the loaders must not read, two vertical
universes (`Flux_0`, `GEANT_Neutron_0`) and the lateral `Muon_Energy_MINOS_0` with every shifted
branch distinct from CV. About 1 % of rows sit on every boundary a loader tests:

- NaN, ±inf, `-0.0`;
- weights at `1e4` and one ulp either side, the background's `1e6` edge, negative weights;
- the rectangle edges and ±4 ulps around the 20° truth cut;
- `|x| > 1e3` for the data guard;
- pass flags 0, 1 and 2.

`TheFixture` asserts that the boundaries are present, so a regenerated fixture cannot silently
weaken the equality tests.

### 5.2 Suites (counts from the runner's own output; 0 skipped)

| suite | what it shows | result |
|---|---|---|
| `tests/test_branch_select.py` | prototype 1 against the pinned loaders. Byte equality in 15 loader × pattern cases: CV with and without weights, two vertical universes, the lateral one. The exact lateral and vertical branch lists. Restored statuses and addresses on a reused tree, including a partial entry state. Discovery reads nothing. Negative controls: the silent defect is real without the guard; **every** omitted activation (17, across the four loaders) and an extra one in each tree are refused before the first read; a loader reading another branch is refused by the rule; a wrong rule that agrees with a wrong loader is caught by the bytes; an unmodelled access is refused; digest sensitivity to sign, dtype, shape, one ulp and one fill | 16 OK |
| `tests/test_sb1_guarded.py` | the wrapper end to end, running the real driver's `main()` under the real `mnv_guarded_run.py` with `--require-provenance` in a throwaway checkout (stub helper, so nothing is trained). Positive: both arms complete; loader digests and settings are equal; all histograms are byte-identical; the helper executed is the checkout's own. Refused before any input is read (exit 3): no guard, a wrong helper digest, a changed driver even when committed and stated, an uncommitted executed file, an input touched after hashing, a wrong input digest, a reference from other arguments. Refused before training (exit 4): a reference whose bytes differ. Refused before the first read on the wrapper path (exit 5): omit and extra controls | 10 OK |
| `tests/test_launch_chain.py` | the unmodified `sb1_submit.sh` and all six batch scripts against a throwaway checkout, with `fake_slurm.py`. Covers dependency order, time limits and ids. The verifier passes the good run and rejects: an SL byte difference (S1 FAIL), 10.5 GiB read (S2 FAIL), a MiB value (S3; MiB is not read as KiB), elapsed 0.5004 × UL (S4 FAIL), a missing receipt (INCONCLUSIVE), H1 ≠ H0, a wrong executed digest, and a guard record with an outside origin (P FAIL). Added in the repair batch (review c0): a killed selective arm is INCONCLUSIVE, not FAIL, while a real difference with later trees missing still FAILs; an unadmitted executed module, a receipt stat unlike H0's, receipts from different environment setups (P FAIL); a control that returned a loader (NC FAIL); each admission guard refuses for its own stated reason (checkout, commit, ancestry, launch spec, ceilings, input stat now), as do a dirty tree, a package changed after its commit, and an authorization that does not name the package commit and manifest digest; an environment setup changed after submission stops the chain at H0. Also: the ledger arithmetic; a proposal cannot be submitted; hostile authorization paths, including a symlink; `draft` fills only mechanical fields | 25 OK |
| `tests/test_package_consistency.py` | `#SBATCH` lines, submit-time `--time` and dependencies equal the launch spec; the argv equals 55677843's; `results/costs.json` is current and its ceiling equals the literal sum; the manifest is current; the committed proposal cannot admit; the schema's required fields equal `sb1_admit.py`'s | 7 OK |

Environment: Homebrew Python 3.13.7 with PyROOT 6.36.000 from `root-config --libdir`, numpy 2.4.4.
The consistency suite also ran under conda Python 3.12.2 (no ROOT needed). One thread per command;
temporary directories removed by each suite. The batch scripts ran locally under macOS
`/bin/bash` 3.2. Perlmutter runs bash ≥ 4.4, and the scripts use no construct whose meaning differs
between the two (no `set -u`, no associative arrays).

### 5.3 Mutation controls (`checks/mutation.py`, `logs/mutation-results.json`)

Each mutant is applied in a fresh `git clone --shared` of commit `864ecaba`, after the unmutated
clone passed every targeted test (7 + 3 + 6 tests, no skips). **16 of 16 caught**
(`logs/mutation-results.json`).

| mutant | file | targeted test | result |
|---|---|---|---|
| `restore-addresses-dropped` | `branch_select.py` | `test_a_reused_tree_is_restored_and_reads_identically_afterwards` | caught (exit 129, interpreter crash) |
| `inactive-address-allowed` | `branch_select.py` | `test_every_omitted_activation_is_refused_before_the_first_read` | caught (exit 1) |
| `active-set-unchecked` | `branch_select.py` | `test_an_extra_activation_is_refused_before_the_first_read` | caught (exit 1) |
| `rule-unchecked` | `branch_select.py` | `test_a_loader_that_reads_another_branch_is_refused_by_the_rule` | caught (exit 1) |
| `discovery-forwards-addresses` | `branch_select.py` | `test_discovery_reads_no_entry_and_leaves_no_address` | caught (exit 1) |
| `all-arm-entry-unchecked` | `branch_select.py` | `test_a_partial_entry_state_is_restored_exactly` | caught (exit 1) |
| `histogram-not-digested` | `branch_select.py` | `test_selective_is_byte_identical_to_the_pinned_loaders` | caught (exit 1) |
| `reference-not-compared` | `sb1_run.py` | `test_a_reference_with_different_bytes_stops_before_training` | caught (exit 1) |
| `input-stat-unchecked` | `sb1_run.py` | `test_an_input_changed_after_hashing_is_refused` | caught (exit 1) |
| `driver-pin-unchecked` | `sb1_run.py` | `test_a_changed_driver_is_refused_even_when_committed_and_stated` | caught (exit 1) |
| `mib-read-as-1000` | `sb1_verify.py` | `test_a_mib_value_is_not_read_as_kib` | caught (exit 1) |
| `s2-bound-loosened` | `sb1_verify.py` | `test_too_many_bytes_read_fails_s2` | caught (exit 1) |
| `s4-bound-loosened` | `sb1_verify.py` | `test_slow_selective_arm_fails_s4` | caught (exit 1) |
| `guard-inventory-unchecked` | `sb1_verify.py` | `test_a_guard_record_from_another_root_is_not_a_pass` | caught (exit 1) |
| `proposal-admitted` | `sb1_admit.py` | `test_a_proposal_cannot_be_submitted` | caught (exit 1) |
| `symlinked-authorization` | `sb1_admit.py` | `test_hostile_authorization_paths_are_refused` | caught (exit 1) |

The first run, at `200bbde5` (`logs/mutation-results-run1-200bbde5.json`), caught 14 of 15. The
survivor, `symlinked-authorization`, was refused anyway by the later commit-blob check, so the test
never isolated the path rule. It now asserts the path rule's own refusal reason. The
guard-inventory mutant was added with the verifier's inventory check.

## 6. Frozen rules (before any run)

### 6.1 Criteria (`sb1_verify.py`)

| key | criterion | evidence |
|---|---|---|
| P | every receipt is strict, guarded, at the admitted commit with exactly the admitted module digests, all carrying the one environment-setup digest bound at submission. Each input's size, mtime and inode equal H0's at every job's start and end. H1 equals H0. Every guard record shows the guard installed on the admitted checkout alone, with the manifest's shim | receipts, `H0/H1/hashes.json`, `inventory*.jsonl` |
| **S1** (mandatory) | every loader's arrays and histogram are byte-identical between arms, with equal settings, in the lateral (UL vs SL), vertical (J1) and CV (C) patterns. Also C's unfold-time loaders equal its loader pass. The selective arm verified before its first read; the production arm entered with every branch active | receipts |
| NC | both J1 activation controls were refused (exit 5) before any loader returned | control receipts |
| S2 | SL `MaxDiskRead` ≤ 10 GB **and** ≤ 0.1 × UL's | `sacct` batch step |
| S3 | SL `MaxRSS` ≤ 30 GB **and** ≤ 0.5 × UL's | `sacct` batch step |
| S4 | SL elapsed ≤ 0.5 × UL elapsed (same argv, threads, node shape) | `sacct` allocation row |
| S5 | output equivalence UL vs SL: byte-identical histograms PASS; every `hXSec2D` bin within 1e-8 relative is PASS-AT-TOLERANCE; otherwise INCONCLUSIVE | outputs |
| S6 | C's hooked phases (loaders, digests, `omnifold`, measured-training build, efficiency, completeness, extraction, projections) cover ≥ 90 % of its wrapper wall | C receipt |

**Overall.** PASS iff P, S1, NC, S2, S3 and S4 pass. FAIL if S1 or NC fails, or if P and S1 pass
and S2, S3 or S4 is measured and fails. Otherwise INCONCLUSIVE. S5 and S6 are reported beside the
verdict and never change it. The absolute bounds are speed's (10 GB, 30 GB). The ratios are new,
and they are taken against the matched UL, not against 2,547 s.

### 6.2 Abort rules

- **Exit 3** (provenance or input refusal) or **exit 4** (a loader byte difference, which stops SL
  before training) or **exit 5** (selection refused outside a control) fails the job.
  `afterok` with `--kill-on-invalid-dep=yes` then cancels every later job except H1.
- **No retries under an admission** (`--no-requeue`; every job directory, receipt and output is
  created exclusively). An OOM, NODE_FAIL, TIMEOUT or cancellation ends SB1 INCONCLUSIVE, unless a
  frozen rule already decides it (an exit-4 difference is S1 FAIL). An SL TIMEOUT at 1,800 s is
  INCONCLUSIVE too: `afterok` cancels J1 and C, so S1 is incomplete. A rerun needs a new
  authorization, admission and outroot, and its request must count the node-h already charged
  against the same 2.0 node-h SB1 total (§7.4).
- A run killed partway is missing evidence, not a difference. A tree present in only one arm counts
  against S1 only when both receipts are complete (`sb1_verify.py` `compare_loaders`).

### 6.3 Trainer nondeterminism

LightGBM at 128 threads is not shown to be bitwise reproducible. The measured same-argument rerun
envelope, 5.8e-9, comes from `VL170` at 64 threads; the 128-thread envelope is unmeasured. With S1
passed, the two arms train on byte-identical inputs, so any UL/SL output difference is one sample of
128-thread rerun variation. It is never evidence against prototype 1. Above 1e-8 it is INCONCLUSIVE
for output equivalence until explained (S5). Differences from the historical products involve other
driver revisions, and C's also another commit and helper checkout. They are reported as UNMATCHED
and enter no criterion.

### 6.4 What a PASS would not show

- Byte equality on three patterns is not equality for the other 185 universes. Their branch names
  come from the same derivation, but their values are not compared.
- No estimator, uncertainty, coverage or publication property moves.
- Timing on one lateral universe is not a measurement for the vertical pattern, for an exact-backend
  unfold, for shared-64 packing, or for a sweep.
- A PASS licenses only a production-change proposal by the driver's owner (claimed by no current
  lane), with its own review and hash-binding record.

## 7. Launch package

### 7.1 Jobs (`launch/launch-spec.json`, `results/costs.json`)

Charge rule, from `operands/sacct_reference_and_billing.psv`: a regular full node bills 256 CPUs
whatever `--cpus-per-task` says (`55677843_166`: `billing=256`, `--cpus-per-task=128`). A shared job
bills its CPUs (`59410433_1`: `billing=64`). So `node_h = billing / 256 × elapsed_s / 3600`, and a
job's **ceiling** is `billing / 256 × time limit`.

| job | what | QOS, CPUs, billing | threads | limit | ceiling node-h | expected node-h (source) |
|---|---|---|---|---|---|---|
| H0 | `sb1_hash.py` on the three inputs, before everything | shared, 2, 2 | 1 | 45 min | 0.0059 | 0.0008 (0.5 GB/s assumed) |
| UL | `sb1_run.py unfold --arm all`, the 55677843 argv on `Muon_Energy_MINOS:0` | regular, 128, 256 | 128 | 50 min | 0.8333 | 0.7269 (2,617 s, `55677843_166`) |
| SL | same with `--arm selective --compare-digests UL` | regular, 128, 256 | 128 | 30 min | 0.5000 | 0.2563 (Amdahl: `f_io` 0.695 measured, `s_io` 14.6 laptop → 923 s) |
| J1 | `Flux:0` loader identity: four production loader processes in parallel, four selective ones, two controls | shared, 64, 64 | 1 each | 45 min | 0.1875 | 0.1248 (estimate, §8) |
| C | CV replica as `59410433_1` (`--bootstrap-seed 1 --seed 1`) with phase timers, then the CV loader identity | shared, 64, 64 | 64, then 1 | 40 min | 0.1667 | 0.0764 (840 s median + 2 × 130 s) |
| H1 | `sb1_hash.py` after everything, `sacct`, `sb1_verify.py verdict` | shared, 2, 2 | 1 | 45 min | 0.0059 | 0.0011 |
| | | | | | **1.6992** | **1.186** |

Every job that reads the universe file runs alone (`afterok` chain H0 → UL → SL → J1 → C; H1
`afterany` on all five). So there is no contention between SB1 jobs, and the peak simultaneous
memory is one job's:

- UL: 64.5–186.6 GB observed on 374 tasks (speed §3; not re-measured here), against 487,802 MiB on
  the node.
- SL: the 30 GB success bound.
- J1: about 70 GB estimated, against 121,920 MiB.
- C: 16.7 GB observed in `59410433_1`.
- H0/H1: under 1 GB.

**Thread placement** matches the references and is recorded, not imposed:

- UL and SL: one exclusive regular node, `--cpus-per-task=128`, `OMP_NUM_THREADS=128`, no
  `OMP_PROC_BIND`/`OMP_PLACES`, as `55677843`.
- C: shared 64 logical CPUs with `OMP_NUM_THREADS=64`, as `59410433`.
- Each receipt records the affinity mask size, the `OMP_*` and `SLURM_*` variables, the host and the
  package versions.

### 7.2 Exact commands (after admission only)

On Perlmutter, from the canonical checkout, after this branch is merged and Joseph's decision is
committed as `docs/orchestration/AUTHORIZATION-<date>-sb1.md`. That record must quote the package
commit (the reviewed commit that last changed `P`) and the sha256 of `P/manifest/expected-code.json`
at that commit, both in full:

```bash
C=<the commit that carries that AUTHORIZATION record>
git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold fetch origin
git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold worktree add --detach \
    /pscratch/sd/j/josephrb/MINERvA-OmniFold-sb1-${C:0:8} "$C"
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold-sb1-${C:0:8}
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
P=docs/orchestration/state/next-preparation-20261009/sb1-prep
python "$P/sb1_admit.py" draft --proposal "$P/launch/ADMISSION-PROPOSAL.json" \
    --authorization docs/orchestration/AUTHORIZATION-<date>-sb1.md \
    --package-commit <this package's commit> --out "$SCRATCH/sb1-admission-${C:0:8}.json"
bash "$P/launch/sb1_submit.sh" "$SCRATCH/sb1-admission-${C:0:8}.json"
```

- `draft` sets only the status, the authorization's path and digest, HEAD, the checkout and
  `outroot = /pscratch/sd/j/josephrb/sb1-<HEAD[:8]>`, then runs `check`. `sb1_submit.sh` runs
  `check` again, creates `outroot` (refusing an existing one), writes `run.env` and
  `submission.json`, and submits the six jobs. `check` also refuses if anything under `P`, an
  executed module or the guard differs between the package commit and HEAD.
- `run.env` binds the environment setup's sha256 at submission. Every job verifies it before
  sourcing the setup and refuses (exit 3) if it changed, and every receipt records it.
- If `sbatch` fails partway, the submit script cancels the jobs it already queued.
- A new detached worktree moves no deployed checkout, so it cannot disturb a pending job of another
  lane.
- Monitor with `squeue --me` and `sacct -j <ids>`.
- **Independent check after H1:** a reviewer re-queries `sacct -P --units=K -j <ids> -o
  JobID,JobName,State,ElapsedRaw,MaxRSS,MaxDiskRead,AllocTRES,ExitCode`, then re-runs `python
  $P/sb1_verify.py verdict --outroot <outroot> --admission <outroot>/admission.json --sacct
  <fresh.psv> --reference-product <UL_SL ref> --cv-reference-product <C ref> --out <own path>` on a
  login node, and reads the receipts directly.

### 7.3 Hashing and duplicate reads

The benchmark jobs never hash the 171 GB file. Reading it first would warm that node's page cache
before the timed read, and it would cost about 0.05–0.1 node-h per job. Instead, H0 and H1 hash all
three inputs on other nodes, before and after. Every guarded run then compares size, mtime and
inode with H0's record at its start and end. `sb1_admit.py expect` writes H0's digests into each
job's `--expect` only after checking that H0's stat equals the admitted one.

Universe-file bytes read by SB1, from `results/costs.json`:

- UL 171.1 GB;
- SL 2.18 GB;
- J1 171.1 + 2.15 GB;
- H0 and H1 171.1 GB each;

about 690 GB in total, all serialized.

### 7.4 No retries; the ledger

- **No retries under an admission.** The charge cannot exceed the six ceilings, 1.699 node-h.
  The 0.301 node-h below the cap is not spent.
- `sb1_verify.py ledger` adds charged node-h (`sacct` billing × ElapsedRaw) to the ceilings of every
  unfinished job, and exits 6 above 2.0.
- A rerun after a failure is a new authorization with its own admission and outroot. Its request
  must count what this admission charged against the 2.0 node-h SB1 total. A J1 rerun at
  `--cpus-per-task=128` (ceiling 0.375) changes the spec, so it falls outside the six authorized
  jobs and needs a new authorization, not only a new admission.

### 7.5 What the cap does not cover, and the exact revised request

The plan above is complete within 2.0 node-h. One extension is left out: measuring the vertical
pattern's timing as a matched pair as well (`UF`/`SF` on `Flux:0`, same shapes as UL/SL). That
would add 0.8333 + 0.5000 node-h of ceilings and could drop J1 (−0.1875), for a total ceiling of
≈ 2.85 node-h. **This package does not request it.** It is the exact revised request to make if a
matched vertical timing is wanted.

## 8. Cost accounting and unit conversions

- **Units.**
  - `sacct --units=K` prints powers of 1024: MaxDiskRead 167,271,319.22 KiB × 1024 =
    171,285,830,881 B = 171.29 GB; MaxRSS 69,191,672 KiB × 1024 = 70.85 GB = 65.99 GiB.
  - Bounds are in GB = 1e9 B. `sb1_verify.py` parses K/M/G/T/P as 1024^n, which
    `test_a_mib_value_is_not_read_as_kib` checks.
  - A shared-64 allocation is 121,920 MiB = 127.8 GB; a regular node is 487,802 MiB = 511.5 GB.
- **Ceilings.** 2/256 × 0.75 × 2 + 256/256 × 50/60 + 256/256 × 30/60 + 64/256 × 45/60 +
  64/256 × 40/60 = 0.01172 + 0.83333 + 0.5 + 0.1875 + 0.16667 = 1.69922 node-h
  (`test_the_committed_costs_are_current_and_within_the_ceiling` checks the literal).
- **Expected values (forecasts).**
  - UL: the reference task's 2,617 s. The 374-task spread is 2,350–2,751 s.
  - SL: speed's Amdahl estimate, `1 / ((1 − 0.695) + 0.695 / 14.6)` = 2.836, so 2,617 / 2.836 =
    923 s. The analytical `s_io` = 68 would give 825 s.
  - J1: the universe-file excess per GB, (2,547 − 778) / 171.29 = 10.33 s/GB. Applied to the signal
    tree's 112.1 GB that gives 1,157 s, plus 100 s of row work (the four parallel processes end with
    the signal tree), plus 4 × 120 s for the selective loaders and 60 s for the controls: 1,798 s.
  - C: the replica median 840 s plus two loader passes of about 130 s.
  - Hash rate 0.5 GB/s, assumed.
  - None of these is a Perlmutter measurement of prototype 1.
- **Scheduler charging.** Elapsed time is charged, not the limit; a failed or cancelled job is
  charged until it stops. Queue wait is not charged. The plan assumes no refunds for node failures.

## 9. Provenance and compatibility with the integrated guard and structure changes

- **Executed code** (`manifest/expected-code.json`; `sb1_run.py` executes exactly these, and strict
  mode refuses any other repository module):

  | file | sha256 |
  |---|---|
  | `P/sb1_run.py`, `P/branch_select.py` | as `manifest/expected-code.json` states at the package commit (not repeated here, so this report cannot carry a stale digest) |
  | `2d-unfolding/uq/coverage_fixed_truth/n2/__init__.py` | `65c577a8…` (as integration §4.2) |
  | `…/n2/execution.py` | `f35dacc6…` (as integration §4.2) |
  | `2d-unfolding/unfold_2d_omnifold_unbinned.py` | `3cc5adc7…` (blob `e19aeb6d`, unchanged) |
  | `unbinned_unfolding/python/omnifold.py` | `e96234124a31…` (unchanged) |

  The guard (`nd-unfolding/mnv_guarded_run.py` `30162f57…`, shim `sitecustomize.py` `b7f78a72…` and
  the other shim files) and every launch file are in the same manifest. `sb1_admit.py` checks all of
  them at HEAD and on disk.
- **The OI-136 path.** The driver inserts `/pscratch/sd/j/josephrb/MINERvA-OmniFold/
  unbinned_unfolding/python` at `sys.path[0]` before `from omnifold import …`. SB1 registers the
  frozen checkout's verified helper as `sys.modules["omnifold"]` first, so that import never
  searches the path. Any other import that resolves into the canonical checkout is refused by the
  guard (exit 3). `test_both_arms_strict_and_identical` asserts that the executed helper is the
  checkout's own.
- **A guard finding during development.** `platform.platform()` shells out to `/usr/bin/file`, and
  the guard refused that child (exit 3). The wrapper records `os.uname()` instead. This is the
  guard's launch contract working as designed.
- **Integration compatibility.**
  - `n2/execution.py` is called, not copied, at its integrated bytes.
  - R1's rule (a module outside the checkout is a refusal) is enforced by the same `load_code`
    pattern.
  - R2's authorization-path rule is restated in `sb1_admit.py`, because in `n2/harness.py` it is
    inline in an N2-specific function. The integration's hostile cases are tested here as well
    (§13 proposes the shared factoring).
  - Structure's changes (`reported_cells.py`, the UQ producers) are not executed by SB1. Strict mode
    would refuse them if they were imported.
- **Receipts.** Each guarded run writes a receipt with:
  - the identity (`n2` `finalize` output: guard state, HEAD, every executed file's path, sha256 and
    git blob);
  - the environment;
  - input stat at start and end;
  - every loader's branch set, settings and digests;
  - a timeline of every hooked call with `/proc/self/io` counters and peak RSS at each boundary;
  - the output's sha256.

  The guard writes its own inventory record per process.

## 10. Admission

- `launch/ADMISSION-PROPOSAL.json` is the proposed record, with status
  `PROPOSAL-NOT-AN-AUTHORIZATION` and a null authorization. `sb1_admit.py` refuses it, and so does
  `sb1_submit.sh` (`test_a_proposal_cannot_be_submitted`). `manifest/admission.schema.json` states
  its shape, and `sb1_admit.py` enforces its meaning (§7.2).
- **The decision needed from Joseph, exactly:** *permission to run the fixed SB1 package — the
  commit that freezes `P`, whose files `manifest/expected-code.json` pins — on Perlmutter CPU under
  account m3246, as the six jobs of `launch/launch-spec.json`, with at most 2.0 node-h charged in
  total (planned ceilings 1.699, expected ≈ 1.19), no retries under the admission, and no other
  compute, GPU or training.* This session does not issue that permission. The authorization record
  must name the package commit and the sha256 of `manifest/expected-code.json` in full;
  `sb1_admit.py` refuses one that does not.
- **What it cannot authorize** (also listed in the proposal):
  - a change to the production driver or the pinned helper;
  - replacing or changing an estimator;
  - claiming a production speedup;
  - the transfer measurement;
  - a matched sweep;
  - N2;
  - a KI-85 lift;
  - adoption, a changed gate or a quoted number;
  - publication;
  - a Rust/C++ rewrite;
  - any compute beyond the six jobs.
- **Relevance (integration §7).** SB1 matters only if option (b) "measure the transfer" or option
  (c)'s matched seed-1 sweep is to be priced. Neither is authorized by the 2026-10-09 ruling, so a
  decision not to run SB1 now is consistent with this package.

## 11. Independent review

- **Reviewer.** One fresh, read-only Claude Code subagent, explicitly authorized. It has no
  authorship of this package. It is the same model family as the owner, so the review is not
  cross-provider independent.
- **Initial review** at the fixed commit `9889b378`, 05:35Z → about 05:50Z, ≈ 0.07 core-h.
  - It worked in its own detached worktree, whose status was empty at start and end, and removed it.
  - It probed mutations only in `git archive` copies.
  - It made two read-only `ssh` queries (`sacct` of the four reference jobs, `stat` of the inputs
    and references).
  - Preserved verbatim: [`review/review.md`](review/review.md), sha256 `41f62d7aa2df2d23…`.
- **Verdict: PASS WITH CHANGES**: 4 MATERIAL, 5 MINOR, 3 NOTE.
- **What it reproduced independently:** every unit conversion and charge (A); every ceiling and
  expected value (B); the four suites, 0 skipped, plus two mutations of its own (C); the branch
  rules against the driver, the 10 lateral universes, the selected bytes (D); the matching of UL/SL
  (E); the input stat and the references' existence (F); scope (G).

| # | severity | finding | disposition (single repair batch) |
|---|---|---|---|
| 1 | MATERIAL | admission bound the run to `package_commit` only by ancestry, so a later edit plus a regenerated manifest passed | **fixed**: `check` refuses any difference under `P`, the executed modules or the guard between the package commit and HEAD, and requires the authorization's text to name the package commit and the manifest's sha256 in full. Tests: `test_a_package_changed_after_its_commit_is_refused` (the reviewer's probe), `test_an_authorization_that_does_not_name_the_package_is_refused` |
| 2 | MATERIAL | the retry rule could not be executed as written (exclusive directories, no retry command), and the ledger under-counted retried charges | **fixed by removal**: no retries under an admission. Any failure ends SB1 INCONCLUSIVE, and a rerun needs a new authorization that counts what was charged. `ledger` is plain accounting (§6.2, §7.4, spec `retry_rule`) |
| 3 | MATERIAL | a selective arm killed mid-loaders scored S1 FAIL | **fixed**: an absent tree is a difference only between two complete receipts; otherwise it is missing (INCONCLUSIVE). A real difference with later trees missing still FAILs. Tests for both |
| 4 | MATERIAL | §6.2's "SL timeout fails S4" contradicted the verifier | **fixed**: an SL TIMEOUT ends SB1 INCONCLUSIVE (§6.2, `costs.json`) |
| 5 | MINOR | nine admission/verifier guards had no red test | **fixed**: a refusal test per guard, each asserting its own reason, and a mutant per guard (§5.3) |
| 6 | MINOR | J1 was described as three processes in places | **fixed**: four everywhere; forecast recomputed (1,798 s, 0.1248 node-h; total expected 1.186) |
| 7 | MINOR | the header claimed a reviewed PASS while review was pending | **fixed** (header points to §15) |
| 8 | MINOR | the environment setup was sourced by every job but bound by nothing | **fixed**: `run.env` binds its sha256 at submission; each job verifies it before sourcing; receipts record it; P requires one digest across receipts. Tests: `test_an_environment_changed_after_submission_stops_the_chain`, `test_receipts_from_different_environments_are_not_a_pass` |
| 9 | MINOR | a partial submission left charged jobs queued | **fixed**: the ERR trap cancels every id already queued |
| 10 | NOTE | `MC_<b>`/`MC_pz_<b>` are also CV-equal on the real file | **fixed** in §3.2 |
| 11 | NOTE | the reference operands were measured under array contention | **disclosed** in §12 |
| 12 | NOTE | a J1 rerun at 128 CPUs needs a new authorization; the 374-task RSS range is speed's | **fixed** (§7.4; §7.1 cites speed §3) |

**Focused re-review:** pending (the one allowed).

## 12. Limitations and residual risks

- Every local result is synthetic and laptop-side (ROOT 6.36, Python 3.13). Perlmutter runs
  ROOT 6.28, Python 3.11 and numpy 1.26. The selection uses only long-standing `TTree`/`TBranch`
  calls, but equality on the real file is exactly what SB1 must measure.
- The J1 memory estimate (about 70 GB for four parallel production loaders) rests on speed's local
  RSS-per-byte factor. An OOM ends SB1 INCONCLUSIVE (§6.2, §7.4).
- The forecasts' operands were measured under contention. `55677843` ran as `--array=1-400%30`
  against a single-stripe file (`operands/input_stat_20261010.psv`: stripe count 1), so up to 29
  concurrent readers shared it. SB1 runs every universe-file reader alone, so UL may be faster and
  its I/O fraction smaller than the 2,617 s and `f_io` 0.695 suggest, which would make S4 harder to
  pass than the 0.35 forecast ratio. UL runs right after H0's full read. Any server-side cache
  effect therefore favours UL, which is conservative for S4.
- The hash rate is assumed. A hash job that times out leaves P INCONCLUSIVE. Its limit (45 min)
  allows 64 MB/s.
- `S6` attributes the driver's inline fill loops (`hTruth2D`, `hUnfold2D`) and the bootstrap draws
  to no phase. If they exceed 10 % of C's wall, S6 reports FAIL for D2's profile, which is a result,
  not a defect.
- The vertical pattern's timing is forecast, not measured (§3.3, §7.5).
- The wrapper times the helper's `omnifold` and seven driver functions by in-memory wrappers in both
  arms. The files are untouched, and the overhead is a few function calls plus about 1–2 s of
  hashing per arm, equal in both.

## 13. Owned files and requests for the integration owner (not done here)

**Files** (all under `P/`):

- `REPORT.md`;
- the prototype and wrapper: `branch_select.py`, `sb1_run.py`;
- the tools: `sb1_hash.py`, `sb1_admit.py`, `sb1_verify.py`, `costs.py`, `make_manifest.py`;
- `launch/`: `launch-spec.json`, `ADMISSION-PROPOSAL.json`, `sb1_submit.sh`, `sb1_hash.sbatch`,
  `sb1_unfold.sbatch`, `sb1_identity.sbatch`, `sb1_cv.sbatch`;
- `manifest/`: `expected-code.json`, `admission.schema.json`;
- `results/costs.json`;
- `operands/` (5 files plus 2 probe scripts);
- `tests/` (4 suites, the fixture writer, `fake_slurm.py`);
- `checks/mutation.py`;
- `logs/` (mutation results);
- `review/` (§11).

**Requests** (exact patches, for their owners):

1. **Manifest.** `REPORT.md` is pre-registered (`MANIFEST-overrides.tsv:535`, `MACHINE open`; routed
   from `CATALOG.md:84`). If `generate_manifest.py --check` reports this subtree, regenerate
   `MANIFEST.tsv` at integration, as for the other lanes. No override row is needed.
2. **`KNOWN_ISSUES.md`** (owner's choice). Speed §13's proposed row, with one sentence appended:
   *"Preparation for the confirmation benchmark, with a matched production arm, is in
   `state/next-preparation-20261009/sb1-prep/REPORT.md`; not run."*
3. **Speed REPORT** (closed lane; annotation only, the integration owner's call). §4 and §11 call the
   synthetic `GEANT:0` universe "lateral". GEANT bands are vertical on the real file (§3.2 here), so
   that test exercised a vertical-style weight swap plus decoy shifted kinematics, not a lateral
   universe. Its equality result stands; the label does not. Proposed annotation after the §4
   equality paragraph: *"(2026-10-10, sb1-prep §3.2: `GEANT:0` is a vertical band on the real file;
   the genuine lateral pattern is tested in sb1-prep.)"*
4. **`n2/harness.py`** (guard owner). Factor the R2 authorization-path block (lines 94-109) into a
   function, e.g. `authorization_record(rel, root) -> (path, norm)`, that both `check_admission` and
   `sb1-prep/sb1_admit.py` call. That would turn the restatement into one implementation. Not done
   here: `n2/` is outside this lane.

## 14. Resources

*Provisional, measured at the freeze for review (2026-10-10T05:31Z); final figures follow the review.*

| item | measured | cap |
|---|---|---|
| active time | 04:34Z → 05:31Z, ≈ 1 h | 6 h |
| local CPU (owner) | ≈ 0.45 core-h of timed commands: two mutation runs (user + sys ≈ 430 s and ≈ 450 s), four full-suite passes (≈ 95 s each), development runs and fixtures (≈ 0.1 core-h) | 3 core-h (owner + reviewer) |
| threads | one per command; at most two commands at once | 2 |
| peak RAM | ≈ 0.8 GB (fixture writer, test interpreters) | 8 GiB |
| scratch | ≈ 13 MB session scratch; each mutation clone (≈ 0.4 GB) and test temporary directory removed when its command ended | 2 GiB |
| tracked bytes | ≈ 0.42 MB in `P/` | 10 MiB |
| cluster | 0 node-h. Read-only `ssh` to a login node: two TTree header listings, one 20,000-entry branch read, `sacct` of four completed jobs, `stat`/`ls` of five files | 0 compute |
| GPU / training / fits | 0 / 0 / 0 | 0 |

## 15. Disposition

*Pending review. The owner's proposed disposition before review is PASS: a complete package whose correctness and cost requirements are met locally and fit the 2.0 node-h ceiling.*

## 16. Next action

- **Joseph:** decide whether to grant the §10 permission. If option (b) or (c) is not going to be
  priced, the right decision is not to run SB1 now; nothing else waits on it.
- **If granted:** commit the decision as an `AUTHORIZATION-` record, merge this branch, and run §7.2.
  Then an independent reviewer re-runs `sb1_verify.py` from a fresh `sacct` and records the verdict.
  Its result may justify only a driver-owner proposal for a production loader change, with its own
  review and hash-binding record.
- **Integration owner:** §13 items 1–4.
