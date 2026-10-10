# SB1 preparation package: independent review (c0)

**VERDICT: PASS WITH CHANGES.** The prototype, its derivation and guard, the matched UL/SL design, the unit
conversions and the ceiling arithmetic all hold up under independent checks. Four MATERIAL defects must be
repaired and re-reviewed before this package goes to Joseph for a resource authorization:
(1) the admission does not bind the launched bytes to the reviewed package commit;
(2) the retry rule cannot be executed as written, and its ledger under-counts charges;
(3) a node failure or OOM in a selective arm is scored as an S1 FAIL of prototype 1;
(4) REPORT §6.2's SL-timeout rule disagrees with the verifier and the retry rule.
Each repair is small and local. None needs a redesign.

## Setup facts

- Target: `9889b37870f708abf764e69ce703bdaa69aa5e3b` (`prep/sb1-ready-20261009`), package
  `docs/orchestration/state/next-preparation-20261009/sb1-prep/` (P below).
- Worktree: `/private/tmp/sb1-review-c0`, detached at the target. Scratch: `/private/tmp/sb1-review-scratch-c0`.
- Start 2026-10-10T05:35:11Z; end of measurement 2026-10-10T05:46Z (wall clock; review writing followed). Worktree removed with `git worktree remove --force` and scratch deleted afterwards, so the probe scripts named below no longer exist; each is described fully enough to re-run.
- `git status --porcelain --ignored`: empty at start, and empty (0 lines) at end. No tracked file was edited.
  Mutations ran only in `git archive` copies under scratch. Suites ran with `TMPDIR` set to scratch and
  `PYTHONDONTWRITEBYTECODE=1`.
- CPU: about 0.07 core-hours, estimated from the runners' own `time -p` user+sys figures (four suites
  about 87 s, four mutation runs about 135 s, probes about 15 s). At most two processes at once,
  `OMP_NUM_THREADS=1`.
- Cluster: two read-only `ssh saul.nersc.gov` calls (login05): `sacct` of the four named jobs, and
  `os.stat` of the three inputs and two references, plus `ls` of `baseline_flux/`. No jobs, no copies,
  no writes.
- Environment: Homebrew Python 3.13 + PyROOT from `root-config --libdir`. No training and no fits.

## Findings

### 1. MATERIAL: the admission binds HEAD's package to `package_commit` only by ancestry, so a launch can run unreviewed bytes
- **Where.** `P/sb1_admit.py:124-131`. `check()` requires only `merge-base --is-ancestor package_commit HEAD`.
  It then compares every file with `manifest/expected-code.json` as read at HEAD, so the manifest
  validates itself. `P/sb1_admit.py:179`: `package_commit` is whatever the operator passes to `draft`.
  REPORT.md:367 leaves it as a placeholder (`<this package's commit>`). Nothing ties the
  AUTHORIZATION record's content to that commit or to the manifest digest.
- **Evidence.** Probe `probe/pkgbind.py` builds a throwaway checkout with the test helpers and commits it
  (A). It then changes `branch_select.py`, reruns `make_manifest.py` and commits (B). Finally it runs
  `sb1_admit.py check` with `package_commit=A` and `commit=B`:
  ```
  package_commit A = 4709f0f0f3  HEAD B = 449a27fe03
  diff A..B:  3 files changed, 3 insertions(+), 3 deletions(-)
  check rc = 0 [sb1-admit] admission holds
  ```
  So any later edit to P on `main` passes admission silently, provided the manifest is regenerated.
  That includes this review's own repair batch, or another lane's edit. The verifier would also pass
  it, because it reads the manifest beside itself. "The fixed package" is therefore not enforced.
- **Smallest repair.** In `check()`, require that every manifest path, plus `manifest/expected-code.json`
  and `launch/ADMISSION-PROPOSAL.json`, has the same blob at `package_commit` and at HEAD
  (`git diff --quiet <package_commit> HEAD -- <paths>`). Also require that the AUTHORIZATION record's text
  contains the full `package_commit` sha (and preferably the manifest's sha256). Then add the negative
  test above.

### 2. MATERIAL: the retry rule cannot be executed as written, and `ledger` under-counts charges, so it can admit a cap breach
- **Where.**
  - Rule: `P/launch/launch-spec.json:167`, REPORT.md:291-293 and REPORT.md:401-410.
  - Ledger: `P/sb1_verify.py:385-407`.
  - Directory creation: `P/launch/sb1_unfold.sbatch:20`, `sb1_identity.sbatch:17`, `sb1_cv.sbatch:16`,
    `sb1_hash.sbatch:18` and `sb1_submit.sh:20`.
- **Evidence (mechanics).** Every batch script runs `mkdir "${SB1_OUT}/<JOB>"` under `set -e`.
  `sb1_run.py` reserves new receipt and output paths. `submission.json` is written with `open(...,"x")`.
  `outroot` is fixed by the admission. So a resubmission "under the same admission" exits at `mkdir`.
  No retry command exists: which script, which `--export`, which dependencies, which outroot, how
  `submission.json` learns the new id, and that H1 must run again. The operator would have to invent
  all of it, which contradicts the PASS terminal in REPORT.md:29-30 ("without inventing parameters").
- **Evidence (accounting).** `ledger` keys only on the original ids in `submission.json`, so a retried
  job's charge is invisible to every later ledger call. Probe (`ledger/`): UL is OOM at 300 s,
  SL/J1/C are cancelled unallocated, H1 runs, the UL retry runs 2,617 s, and SL then TIMEOUTs at
  1,800 s:
  ```
  == before UL retry: ledger --retry UL   ... = 1.7725 of 2.0 node-h   rc=0
  == after UL retry and SL TIMEOUT: ledger --retry SL
  charged 0.0850 + unfinished ceilings 0.8542 + retry 0.5000 = 1.4391 of 2.0 node-h   rc=0
  true committed = ... = 2.1719
  ```
  The ledger admits an SL retry that would take the committed total to 2.17 node-h. It also never adds
  the H1 rerun that any retry of an upstream job requires.
- **Smallest repair.** Either state "no retries under this admission; any failure ends SB1 INCONCLUSIVE
  and a rerun needs a new admission and outroot" (simplest, and the cap still holds at 1.699), or ship a
  `sb1_retry.sh`. That script would append the new id to an append-only `retries.json`, use a per-attempt
  job directory, and resubmit H1. `ledger` would then sum every id in `submission.json` and `retries.json`,
  plus the ceilings of every job that has to run again (dependents and H1). Add a test with the
  sequence above.

### 3. MATERIAL: an infrastructure kill during a selective arm's loaders is scored S1 FAIL, so overall FAIL
- **Where.** `P/sb1_verify.py:166-170`: a tree present in only one arm is a "difference", not
  "missing". `P/sb1_verify.py:302-304` and `364-365`: S1 FAIL means overall FAIL. This contradicts
  REPORT.md:29-32, 66-68 and §6.1, where S1 fails on a byte difference. It also contradicts the retry
  rule, which treats NODE_FAIL and OOM as retryable.
- **Evidence.** Probe (`partial/`): UL receipt complete with 4 loaders. SL receipt `status: running`
  with 2 loaders (killed). sacct `SL NODE_FAIL`:
  ```
  overall FAIL
  S1 FAIL ['mc_signal_reco: present in one arm only', 'mc_truth_denom: present in one arm only']
  P INCONCLUSIVE
  ```
  The same happens for a J1 or C selective process killed after its receipt's first write
  (`loaders: []`).
- **Smallest repair.** In `compare_loaders`, count a tree as a difference only when both receipts hold
  it and the digests or settings differ, or when the short receipt's status is `input-mismatch` or
  `selection-refused`. Otherwise (`running`, `error`, `driver-exit`) report it as missing, which gives
  INCONCLUSIVE. Add the probe above as a test.

### 4. MATERIAL: the SL-timeout rule in REPORT §6.2 (and `costs.json`) contradicts the verifier and the retry rule
- **Where.** REPORT.md:289-290 says "Reaching it means SL elapsed ≥ 0.69 × UL's reference, which fails
  S4. No retry is needed for a verdict". `P/costs.py:137-140` and `results/costs.json:255` say the same.
  But `P/sb1_verify.py:315-330` scores S2-S4 INCONCLUSIVE unless both jobs are COMPLETED, and
  `launch-spec.json:167` permits a TIMEOUT retry. The 0.69 figure is also taken against the historical
  reference, which REPORT says enters no criterion. The logically sound bound is SL ≥ 1,800 s >
  0.5 × UL's own 3,000 s limit.
- **Evidence.** Probe (`partial/`): UL COMPLETED, SL TIMEOUT 1800 with all four loaders recorded, J1 and
  C cancelled. The verifier gives `overall INCONCLUSIVE` with S1, S2, S3 and S4 all INCONCLUSIVE. Even
  with S4 forced to FAIL, overall stays INCONCLUSIVE, because `afterok` cancels J1 and C and leaves S1
  incomplete.
- **Smallest repair.** Change REPORT §6.2 and the `costs` note to "an SL TIMEOUT ends SB1 INCONCLUSIVE
  (J1 and C are cancelled); it is not retried". Otherwise implement "SL TIMEOUT with UL COMPLETED ⇒ S4
  FAIL" and run J1 with `afterany` on SL (after checking SL did not exit 4) so that S1 can complete.
  Then make the retry rule agree.

### 5. MINOR: several admission and verifier guards have no test that turns red when they are removed
- **Where.**
  - `P/sb1_admit.py`: 117-118 (checkout), 122-123 (dirty tree), 124-127 (ancestry),
    134-136 (launch-spec sha), 138-140 (job ceilings) and 145-147 (input stat now).
  - `P/sb1_verify.py`: 116-118 (unadmitted executed modules), 121-124 (receipt input stat vs H0)
    and 307-308 (NC requires `loaders == []`).
- **Evidence.** Scratch copy M1 has all nine checks disabled and the manifest regenerated.
  `test_launch_chain` (13 tests) passes, as do `test_package_consistency` 6 of 7 and `test_sb1_guarded`
  10 of 10. The one error is `test_the_unfold_argv...`, which reads the reference launcher
  `2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh`. My partial copy did not
  include that file, so the error comes from the copy, not from the mutation.
- **Smallest repair.** One refusal test per guard in `test_launch_chain`, using `admission(..., **override)`
  and the existing verdict helpers.

### 6. MINOR: J1's description disagrees with its script, and its forecast models a different job
- **Where.**
  - REPORT.md:329 and `sb1_identity.sbatch:11,32-42` say four parallel `--arm all` processes, then
    four selective ones.
  - REPORT.md:525, `launch-spec.json:113` and `costs.py:92-93,154` say three parallel, the
    "≈70 GB for three", and "3 × 120 s selective".
- **Repair.** State four and four everywhere. Recompute the J1 forecast and memory estimate for four
  processes, or merge `data` into the background process if three was intended.

### 7. MINOR: the header claims a reviewed PASS while the review is pending
- **Where.** REPORT.md:22 ("**PASS** ... a complete, reviewed package") versus §11 and §15 (pending).
- **Repair.** "Proposed: PASS (pending review)".

### 8. MINOR: the environment script is executed in every job but bound by nothing
- **Where.** `sb1_submit.sh:13` and `*.sbatch` lines 17-21 `source "${SB1_ENV_SETUP}"` (the canonical
  checkout's `setup_salloc_env.sh`). It is absent from `make_manifest.py` LAUNCH/GUARD, and `SB1_ENV_SETUP`
  can be overridden from the environment.
- **Risk.** It sets PATH, the interpreter and libraries. A change between UL and SL would unmatch the
  arms without any record. (Imports are still guarded.)
- **Repair.** Record its sha256 in `run.env` at submission. Have each job refuse if the digest differs, and
  write it into the receipts.

### 9. MINOR: a partial submission leaves charged jobs queued
- **Where.** `sb1_submit.sh:39`. The ERR trap only prints the ids. If `sbatch` fails after H0/UL are
  queued, they run without H1, and UL can charge 0.833 node-h.
- **Repair.** `scancel` the submitted ids inside the trap.

### 10. NOTE: the real-file limit understates what real-data equality cannot see
- REPORT.md:143-148 names only `pT_truth_<b>`. `operands/lateral_probe.json` also shows `MC_<b>` and
  `MC_pz_<b>` on `mc_signal_reco` equal to CV in 100 % of the sampled rows (frac_differs 0.0), so
  `MC` vs `MC_<b>` is equally invisible on the real file. The derived-name argument and the synthetic
  fixture still cover it. Add it to the sentence.

### 11. NOTE: forecast operands come from a contended array
- 55677843 ran as `--array=1-400%30` on a single-stripe file (`input_stat_20261010.psv`: stripe count 1).
  So the reference 2,617 s and `f_io=0.695` were measured with up to 29 concurrent readers, while SB1 runs
  alone. These are correctly labelled forecasts, but alone UL may be faster and its I/O fraction smaller,
  which would make S4 harder than the 0.35 forecast suggests. UL always runs right after H0's full read
  and before SL. Any server-side cache effect therefore favours UL, which is conservative for S4. Neither
  effect is stated.

### 12. NOTE: smaller wording points
- REPORT.md:409-410: a J1 rerun at 128 CPUs changes the spec, so it falls outside the authorized
  "six jobs of launch-spec.json". It needs a new **authorization**, not only "a new admission".
- REPORT.md:338: "64.5–186.6 GB observed on 374 tasks" was not re-measurable within my query scope.
- Overall FAIL on S1 is independent of P (`sb1_verify.py:364`). That matches §6.1 as written, and strict
  mode makes a wrong-bytes S1 difference practically unreachable.

## Independent checks performed

**A. Units (re-measured on login05, 05:38Z).**
- sacct `--units=K` gives:
  - 55677843_166.batch: MaxRSS 69191672K and MaxDiskRead 167271319.22K.
  - 55677843_22.batch: 67779200K and 167271412.52K.
  - 55677845.batch: 69842960K and 167271257.15K.
  - 59410433_1.batch: 16296360K and 2147779.01K.
- Billing (my reading of AllocTRES): 256 on all three regular jobs, 64 on the shared one.
- Allocations: regular mem=499509248K = 487,802 MiB = 511.5 GB; shared 124846080K = 121,920 MiB
  = 127.8 GB.
- My arithmetic:
  - 167271319.22 × 1024 = 171,285,830,881 B = 171.29 GB.
  - 69191672 × 1024 = 70.85 GB = 65.99 GiB.
  - 16296360 KiB = 16.69 GB.
- `sb1_verify.UNIT` uses powers of 1024, and the bounds use GB = 1e9.
- node-h = billing/256 × elapsed/3600. The 55677843_166 reference is 0.7269.
- All of these match the report.

**B. Cost.**
- Ceilings, recomputed from the `#SBATCH` lines and the submit-time `--time` (SL 00:30:00):
  0.005859 + 0.83333 + 0.5 + 0.1875 + 0.16667 + 0.005859 = 1.69922 node-h.
- Expected values: 0.0008 + 0.7269 + 0.2563 + 0.1165 + 0.0764 + 0.0011 = 1.178.
- Amdahl: 2.836 gives 923 s, and s=68 gives 825 s. J1 forecast: 10.33 s/GB × 112.1 GB + 520 = 1,678 s.
- All expected values are labelled forecasts with their sources.
- Hashing, verification and controls sit inside the H0/H1/J1 ceilings, and nothing charged lies outside
  them except retries and orphans (findings 2 and 9).

**C. Suites at 9889b378** (my runs, runner output):

| suite | result |
|---|---|
| `test_branch_select` | Ran 16, OK |
| `test_sb1_guarded` | Ran 10, OK |
| `test_launch_chain` | Ran 13, OK |
| `test_package_consistency` | Ran 7, OK |

- 0 skipped, and every rc was 0.
- Controls fire on bad inputs, and the positive chain passes.
- My own mutation spot-checks, in scratch copies:
  - **M2.** S4 bound loosened from 0.5 to 0.6: `test_slow_selective_arm_fails_s4` FAILED, rc=1.
  - **M3.** Active-set check removed from `SelectiveTree.verify`:
    `test_an_extra_activation_is_refused_before_the_first_read` FAILED in 4 of 4 subtests, rc=1.
- Recorded mutation log: 16 of 16 failures are assertion FAILs (one is an interpreter crash), not
  import errors. The code under mutation is unchanged between 864ecaba and 9889b378 (diff touches only
  REPORT, logs, `make_manifest.py`, the proposal and the test fixture).
- Guards with no red test: finding 5.

**D. Prototype 1 vs pinned driver.**
- Driver blob `e19aeb6d` and sha256 `3cc5adc7…` verified at the target.
- `expected_branches` matches the driver's branch logic for all four loaders: lines 211-219, 280-303,
  527-572 and 606-690, including the `use_weights` gating, bkg-weight-without-`use_weights` and the
  lateral pair test by presence. `main()` calls each loader once (1400-1405), and `run_loaders` matches
  `main()`'s arguments (edges 1304-1307).
- My recount from `operands/universe_branches.json`: 187 universes, and exactly 10 lateral universes
  (BeamAngleX/Y, MuonResolution and Muon_Energy_MINERvA/MINOS, `_0`/`_1`), with identical sets for
  `sim_pz_*`, `MC_pz_*`, `pT_truth_*` and `sim_background_pz_*`.
- Selected bytes: lateral 2.181 GB, vertical 2.145 GB, total 171.098 GB, CV file 2.144 GB.
- "Lateral" is established from data: the `lateral_probe.json` values match REPORT's table.
- Tree-state restoration covers statuses and the derived branches' addresses. Each SB1 process opens its
  own file, so reuse never occurs in the launched jobs.

**E. Matching and rules.**
- UL/SL share the admission commit, the argv (`comparison_key` drops only `--out`; it equals the 55677843
  launcher's), 128 threads, the regular 1×128 shape, default bkg mode and seed 42.
- Historical products enter only `unmatched_historical`.
- The overall logic in `sb1_verify.py:363-371` equals REPORT §6.1. §6.2 conflicts with it (finding 4).
- §6.4 keeps "equality is not coverage".

**F. Provenance.**
- `load_verified` registers the helper in `sys.modules` before the driver's `sys.path` insert (driver
  1719-1723).
- The canonical helper directory holds `omnifold.py` and `omnifold_old.py` locally. The Perlmutter
  contents of that directory are outside my query scope.
- Inputs: H0/H1 bracket plus stat, and inputs stat-matched at start and end. Re-measured
  size/mtime_ns/ino for all three inputs equal `input_stat_20261010.psv` and the proposal. The two
  references exist: 56,509 B and 55,484 B.
- Admission: the proposal is refused. The binding gaps are findings 1 and 8.

**G. Scope.**
- `git diff --name-only a16d5786 9889b378 | grep -v '^P/'` printed nothing. There are 34 files, all
  under P.
- No claim of a production speedup, adoption or authorization was found. The only overstatement is
  finding 7.
