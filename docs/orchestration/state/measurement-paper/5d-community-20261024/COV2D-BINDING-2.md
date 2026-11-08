# COV2D BINDING 2: the amendment's code, the job scripts and the pilot (director, 2026-11-05)

**Binds** [`COV2D-AMENDMENT-1.md`](COV2D-AMENDMENT-1.md), sha256
`777317bebaec0ad64feb1dba98eb9c9ceb3fbfeadd720e0f7d9b88e7c51a03cf`, and the code it lists, as on main at:

**M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`** (the merge of #778; code commit `5c0e02a2`)

**Under** [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md) §10 item 4, [`COV2D-BINDING-1.md`](COV2D-BINDING-1.md) and
[`COV2D-BINDING-1-A1.md`](COV2D-BINDING-1-A1.md). The amendment merged in #773 (`e9cadf47`). F3 merged in #776
(`8a258b38`), and its M-line tightening in #778.

## What the director checked

- **The digest.** The amendment's sha256 at M is the one above.
- **Every blob.** All 25 rows of the amendment's §9 tables (15 code files and 10 test files) equal their blobs at M.
  So do all 12 imported modules of §1: `re2_driver.py` `97f26a1d`, `cov2d_writer.py` `bb3892e5`, `cov2d_receipt.py`
  `d5718bf4`, `fd_1b_null.py` `1810161d`, `fd_1b_mc.py` `74aa8dac`, `re2c_rollup.py` `e41940cb`, `build_cmodel.py`
  `7a987e25`, `re2_k1.py` `62a1dc33`, `fd_rpd_inputs.py` `7c2e018f`, `s5e_deform.py` `2c11f9f6`, `pvl_lib.py`
  `81d509ba`, and `clip_probe.py` `f5683876`.
- **The audit** (coverage-5b-audit): parts 1–4, the final audit, the F1/F2 delta, F3 and its tightening. All are
  closed and nothing blocks (`fd/receipts-cov2d/amendment/AUDIT-*.md`).
  - F3, the submit script's binding check, was a fixed point. It was found by the director while drafting this
    binding, and no test reached it. The check now reads this file from origin/main after a fetch that must succeed,
    and binds M only on the line above.
- **The receipts at `5c0e02a2`:** 155 tests, 0 skipped. Mutants: 64 of 64 killed, 10 of them REQUIRED, and the
  harness exits 1 on any survivor.
- **The time limits** are written `HH:MM:SS` (`cov2d_jobs.limit_of`, `cov2d_pseudo.sbatch`). Every job checks its own
  `scontrol` TimeLimit and stops on a mismatch.

## Rulings

1. **The amendment is bound at M,** with the rulings it carries (§2), REPRICE before the bulk, and §7's statements.
   The deploy is a fresh clean checkout at M.
2. **The order is as `cov2d_jobs.order` enforces it, with the director told before each connect:**
   1. **The G18 pseudo-data job.** Its connect's sha256 comes to the director first.
   2. **The pilot,** after G18's pseudo-data PASS record is on main. Its connect's sha256 comes to the director first.
   3. **The pilot readout,** which comes to the director before the bulk (binding 1 ruling 1). The bulk opens only on
      PASS with `reprice_classes == []`. A REPRICE class goes to an amendment.
   4. **The bulk,** in the amendment's waves, after the director has read the pilot readout. Each connect's sha256
      comes to the director.
   - An `order()` admission is necessary but is not the director's go.
3. **The price.**
   - The cap stays at **165.8 node-h** (binding 1 ruling 3), and the gate prices every cov2d job.
   - The KillWait overrun is accepted as a disclosure, not a block: each job unfinished at the last submission adds at
     most its grace, for example 22 × 60 s = 0.37 node-h. The amendment states the grace as an assumed example (§5). The readout reports the final
     charge from sacct.
   - The charge stays far below half the balance. This is an operational go-ahead within the standing grant, reported
     to Joseph with this binding.
4. **The cluster lane is `cov2d`** for every job, as for control (2a) and staging.
5. **Tests in the cluster environments, before the G18 job.** This is binding 1 ruling 4's pattern, at 0 node-h, from a
   fresh clone at M on a login node, with no pscratch or CFS reads:
   - run each suite in the environment §8's table names for it;
   - name every environment;
   - commit the logs, the node, and the porcelain before and after as a receipt.

   A failure is fixed and reported before any connect. It cannot be shown away by running the suite in another
   environment.
6. **The STOP count stands at one** (CONTROL-2A, 2026-11-03). A second STOP ends (c) unless Joseph rules otherwise.
   - (2b) or §9.12 failing in the pilot is that second STOP.
7. **The schedule** of §10 is bound, including its terminal branch:
   - no `$UNI`-reading job submitted by 2026-12-01 means no bulk, and a report;
   - `$UNI` is exposed from 2026-12-19.
8. **Unchanged:** binding 1's rulings 5–7 (schedule, retention and HPSS, the paper and the note).

Nothing is submitted, deposited or tagged.

## Binding 2, addendum A2: private staged inputs, recording guards, and the AR23 rerun (director, 2026-11-06)

**Binds** [`COV2D-ADDENDUM-A2.md`](COV2D-ADDENDUM-A2.md), sha256
`9648a7bedd493ce8d0fdb636ff7fc3db6a5d72f819f8b329d7e090d6d2695d59`, and its code, as merged in #803 at:

**M = `cf533377c7f9e1638940c677b9af5242f3ba66f4`**

(code commit `038f28e8`; `git diff 038f28e8 cf533377 -- 2d-unfolding/cov2d/` is empty.)

**Under** `DECISION-20261105-joseph-ar23-stop-external-and-765-phrases.md` §1, which counts the AR23 firing as STOP #2,
rules it externally caused, and continues (c) under this addendum. **A third STOP of any kind, or any guard firing on a
private staged copy, ends (c).**

### What the director checked

- **The digest.** A2's sha256 at M is the one above.
- **The code is the code that was audited and receipted.** The cov2d tree at M equals `038f28e8`. The receipts at `038f28e8`:
  182 tests, 0 skipped; 91 of 91 mutants killed, 38 of them REQUIRED.
- **The audit** (coverage-5b-audit, `fd/receipts-cov2d/a2/AUDIT-A2.md`). Its findings, all closed: D1, a staged hash off
  its pin now writes a STOP record; D2, settle before guarding (fsync and two agreeing atime readings 5 s apart); L1,
  `pins_checked` is required on the pseudo-data records, and step B refuses an unpinned step A; N1, the `PRIOR_RECORDS`
  table, ruling R1, which admits exactly G18's and the pilot's committed bytes at `cb31611c`. The auditor ran the real
  `order()` on the committed records at a new M.
- **The two-M-line binding.** `cov2d_submit.sh` matches `^\*\*M = \`<M>\`\*\*`. The cov2d lane ran the real script on
  fixtures: each M is bound only by its own line, and a sha cited in prose or on an indented line is refused. The
  `cb31611c` line above stays as bound text. A deploy at `cb31611c` is refused by AR23's existing directory and by
  `order()`.

### Rulings

1. **A2 is bound at M.** The deploy is a fresh clean clone at M. A2's code is frozen unless a run STOPs.
2. **The classification of outcomes** is A2 §6 as ruled:
   - a guard verdict STOP on a private copy is a STOP;
   - a staged copy's hash off its pin is a STOP;
   - a refusal before any read or product (an existing directory, quota headroom under 2×, a dirty deploy, atime that
     does not settle) is not a STOP, and is reported;
   - a crash, OOM, kill or time-out is INVALID (§9.13). It is not a STOP; it comes to the director unrepaired and needs
     a go to rerun.
3. **A fixed conditional sequence.** It replaces binding 2's go for each connect, for this sequence only. Each stage
   proceeds automatically when the previous stage's declared PASS record is committed on main with M. Anything else
   stops and comes to the director. The cluster lane reports each connect's sha256 and result as it goes.
   1. **The A2 cluster-environment test run** at M:
      - the suites in P, R and RM, with every environment named;
      - the four Linux both-direction guard tests, shown running, not skipped;
      - the 1-minute compute-node showquota check, run as job `a2quota` outside the gate (about 0.02 node-h, reported in
        the receipt);
      - porcelain with `--ignored` before and after.
   2. **The AR23 pseudo-data rerun** into `pseudo/AR23-a2`, at `--time=04:00:00`.
   3. **The eight universe jobs**, the `$UNI` readers, after AR23's PASS. They must be submitted by 2026-12-01.
   4. **The rest of the bulk** in the amendment's waves, after all eight are submitted.
   5. **The blocks and readout login steps**, after the bulk.
4. **The director's notes owed to binding 2,** recorded here:
   - the REQUIRED set grew from 10 to 12 by ruling (i), with test blob `e3682f8d` and #797, and is 38 at A2;
   - test_cov2d's Receipt class (11 tests) runs only in the all-in-one local environment. It is skipped in every
     cluster environment, and §8's table is corrected accordingly;
   - Perlmutter maps `--qos=regular` to QOS `regular_1`, and the job's substring check admits it;
   - the D2 settle check and the `PRIOR_RECORDS` admission are the only changes to the order logic.
5. **Price.** The cap stays at 165.8 node-h, with about 9.6 spent so far. The AR23 rerun holds 4.0 at submission.
6. **The STOP count is two.** STOP #1 is CONTROL-2A (11-03). STOP #2 is the AR23 firing, ruled externally caused
   (11-05).

Nothing is submitted, deposited or tagged.

## Binding 2, addendum A2, revision 2: the quota check at submission and the fire tests' timing (director, 2026-11-06)

**Binds** `COV2D-ADDENDUM-A2.md`, sha256 `79de07edfacb8aa6972307910d4581484e47319d7336c5a19f5e4e2361e7d762`, and its code, as
merged in #817 at:

**M = `a60547692df5f963e428cdfe4661fc51ab785b7b`**

(code commit `94544e0b`; `git diff 94544e0b a6054769 -- 2d-unfolding/cov2d/` is empty.) It **supersedes A2's M line
above** (`cf533377`) for every stage from here.

**What led to it.** Stage 1 at `cf533377` FAILED (receipt #812). It wasn't a STOP: no production guard fired and nothing
was graded. There were two causes:
- step A's fire test didn't fire on Linux, a test-timing artefact of coarse atime ticks;
- showquota crashes on compute nodes, since `mmlsquota` is absent there, so step A's in-job quota check would have refused
  every run.

**What changed, exactly the director's unfreeze:**
- both fire tests sleep 0.25 s before the plain read;
- the quota check moves to the pseudo-data job's gate at submission, on the login node. It stats the seven staged inputs
  and requires showquota headroom of at least 2× their bytes, and it fails closed if showquota can't be read. Step A's
  in-job call is removed;
- TMPDIR is reset in the job scripts.

The audit (coverage-5b-audit) found no blocker: its own runs gave 87 tests passed and 12 skipped, and 3 of 3 new mutants
killed. The receipts at `94544e0b` show 184 tests, 0 skipped, and 92 of 92 mutants killed, 39 of them REQUIRED.

**Rulings.**
1. **A2 revision 2 is bound at M.** The code is frozen unless a run STOPs.
2. **The fixed conditional sequence of A2's ruling 3 restarts at stage 1 at this M,** with a fresh deploy,
   `cov2d-deploy-a6054769`. The `cf533377` deploy stays as left. Stage 1's compute-node `a2quota` job is dropped, and the
   login-node quota check takes its place.
3. **Everything else in A2's binding stands:** §6's classification, the STOP count of two, the third-STOP rule, and the
   price.

Nothing is submitted, deposited or tagged.

## Binding 2, addendum A3: the pilot-label collision (director, 2026-11-06)

**No new M.** The bound code, the job scripts and the tables at `a6054769` are unchanged. This addendum rules on a
planning defect and sets stage 4's PASS record.

**What led to it** (cov2d's reports, unrepaired):
- **The job.** G18_L (60895948) ended FAILED 1:0 after 1.81 node-h.
  - Its nine runs are each rc 0 with a digest, and its check reports `problems: []`.
  - It refused two runs at `cov2d_job.sbatch:41` ("exists; not overwritten"), and that skip sets the job's rc to 1.
- **The cause.** The pilot (60857636, at `cb31611c`) had written five labels into the same `$O/out` that the bulk
  tables reuse:
  - X_G18 and L_G18_BeamAngleX_0, in G18_L;
  - U_G18_Flux_0, in G18_Ua;
  - B_G18_001, in G18_Ba;
  - T_G18_5720000, in G18_Ta.
- **The other three jobs** each log one such skip.
- **cov2d's stat-only listing** at 13:04Z covered all 1,572 bulk labels of both truths: no other bulk label predates its
  job.
- **What reads the pilot's products.** No code in the sequence reads `$O/out/<label>` for a bulk label. The pilot
  readout opens only its three COMPARE labels, and it sees the five only through `SHA256SUMS.pilot.*` and
  `walls.pilot.*`. order() reads only committed records and the submissions log. gate() reads sacct only to price.

**Rulings.**
1. **The classification: INVALID for the five labels only, not a STOP.**
   - A STOP is "any step this declaration or the amendment says stops the campaign" (COV2D-DECLARATION §6 (iii)), and
     nothing declares a skipped existing output to be one. The STOP count stays at two.
   - The other runs in the four jobs stand on their own rc 0 and digests, but only where the job's exit 1 is shown to
     come solely from its expected skips. cov2d's `watch2.sh` match is that evidence: exit 1:0, every step COMPLETED 0:0,
     every walls rc 0, the skip set equal to the job's expected labels, no run-failure line, and walls rows plus skips
     equal to the table's rows.
   - Any other cause in any of the four jobs is a new report.
2. **The pilot's products do not count for the bulk.**
   - `cov2d_jobs.py`'s pilot() ran X_G18 and U_G18_Flux_0 at 64 CPUs, where the bulk runs them at 128. The pilot's own
     rule is that RE-2 claims equality only like for like.
   - All five are rerun in the bulk's configuration, so every bulk label has one provenance.
3. **The completion job, G18_C,** for exactly the five labels, with each row taken verbatim from `runs_G18.tsv` and the
   CPU counts of the bulk plan.
   - It goes through the bound `cov2d_submit.sh` and `cov2d_job.sbatch`.
   - Its connect-level pieces need coverage-5b-audit's GO before launch:
     - the G18C tables;
     - the pseudo-data route, which must resolve to G18's bytes under `pseudo_b.json`;
     - every use of `$TRUTH` and `DATA_TRUTH` on the G18C path, including the submission's table regeneration and
       compare;
     - the concurrent steps' memory sum against 487,802M;
     - the label listing.
   - On that GO it launches without the director. It is priced under the 165.8 cap like any other job.
4. **The rename.** Before G18_C's submission, its connect renames each of the pilot's five `$O/out/<label>` to
   `<label>.pilot-60857636`.
   - It uses `mv -n` and deletes nothing.
   - It records a B9-form ledger whose shas before and after equal the `SHA256SUMS.pilot.*` lines.
   - The ledger maps each of those lines to its new path. After G18_C, the old paths hold the bulk's bytes.
   - The pilot readout is not rerun.
5. **Every further submission's connect** stat-lists its job's labels against `$O/out` and refuses on any hit
   (`connect-wave.sh` v2, on the auditor's GO).
6. **Stage 4's PASS record** (A2 ruling 3, item 4) is a per-label completeness table over all 1,572 bulk labels:
   - each label has exactly one rc-0 walls row and one digest from a job at M, with its job id and job name;
   - for the five labels, that job is G18_C, with this addendum and the rename ledger cited;
   - beside the table, each FAILED job's match evidence under ruling 1.

   sacct's FAILED state for those four jobs does not block stage 5 when this record is committed on main.


## Binding 2, addendum A4: the bulk readout driver, phases N and S (director, 2026-11-07)

**Binds** `COV2D-ADDENDUM-A4.md`, sha256 `ea7113c01ba26696e3e5eb17f04c035d1bf311e5bd113a828240eac338631b49`, and its
code, as merged in #875 at:

**M = `ac25b66533788ceb18b1d4e5add259c53b216669`**

The code commit is `7177d0f8`, and `git diff 7177d0f8 ac25b665 -- 2d-unfolding/cov2d/` is empty. This M binds the
readout stage only: phase N and phase S, from `cov2d_readout.py`. The bulk products it reads stay those of the bulk's M
(`a6054769`), checked by A4's §9.9 provenance and #866's completeness digests.

**What led to it.** The stage-5 code bound at `a6054769` had no driver from the 1,572 bulk outputs to `assemble` →
`null_at_T` → `score` → the readouts. cov2d reported this before reading anything, and the director authorized A4 as an
amendment on 2026-11-07.

**What the director checked:**
- **The design.** coverage-5b-audit's design GO on A4-1, A4-2 and A4-3, all closed, at `e6444745`:
  - one code across both phases;
  - truth, role and seed taken from runConfig;
  - phase N only stats the toys.
- **The code.** Its code GO at `7177d0f8`, with no blockers and one LOW on its follow-up list. The auditor checked that:
  - the bound modules are unchanged;
  - phase S's gate refuses before any toy is opened;
  - phase N opens no toy;
  - §9.9 is implemented as declared.
- **The tests.** 36 tests OK, 37 of 37 mutants killed (19 REQUIRED), and the root_6_28 cluster receipt (`27f20b4b`)
  shows the atime guard live on Linux.
- **Nothing has read a bulk output** before this binding.

**Rulings:**
1. **The two-phase order is bound.**
   - Phase N writes `null_<T>.json` and `blocks_<T>.npz` per truth, and they are committed to main through a receipt PR
     the director merges.
   - Phase S refuses unless origin/main's `null_<T>.json` digest equals its `--null-digest`, with this M and verdict
     PASS. It refuses unless the blocks digest and the re-hashed input inventory match.
   - Only then does it open a toy product.
2. **§9.9 is new check logic, labelled as such in A4,** and is bound as declared:
   - one driverSha256;
   - dataFileSha256 equal to the realization or toy data file;
   - runArgv equal to its runs-table row;
   - the row's seed.

   A mismatch reads INVALID, fails closed before any toy is read, and comes to the director unrepaired, with the
   mechanism named.
3. **The step-A and step-B arrays** (cells.npz, truth_xsec.npz) are hash-pinned in phase N without being parsed. Their
   provenance before now has the limits A4 §3.4 states: G18's size and mtime, the mtime windows, and no earlier digest.
   These are disclosed limits, not STOPs.
4. **Each connect** sends its sha256 to the director before launch, from a fresh clone at this M. The fence logic runs
   first, inputs are read by O_NOATIME, ssh's rc is read unpiped, and each connect's receipt is a PR.
5. **The readout due date stays 2026-12-18.**

## Binding 2, addendum A5: the Cholesky cross-check's tolerance at full rank (director, 2026-11-07; rule bound, code to follow)

**No new M yet.** This addendum fixes a rule before any coverage reading exists. The code that implements it is bound
later, at its own M, after coverage-5b-audit audits it.

**What led to it.** G18's phase S at `ac25b665` is INVALID, with no reading produced or seen (cov2d's receipt).
- **The crash.** The driver crashed with rc 1 in the bound `fd_1b_mc.grade` (`nd-unfolding/fd_1b_mc.py:661-667`), with
  `Refusal: the non-null chi2 and the Cholesky chi2 differ`.
- **Why the check fires.** At ndf = 205, grade cross-checks the eigen-projected χ² (`fn.chi2_nonnull`, the statistic
  the declaration reads) against a Cholesky χ² to a relative 1e-9 (COV2D-DECLARATION §5.1: "with the Cholesky equality
  checked if ndf = 205"). G18's C_T has λ_min/λ_max = 1.0531e-12. That is just above the 1e-12 rank cut, so ndf = 205
  and the check runs on a matrix with condition number κ ≈ 9.5e11.
- **Why it can't pass.** Two backward-stable float64 solves of that matrix agree only to O(κ·ε) ≈ 2e-4 relative. The
  1e-9 tolerance can't be met by any correct implementation. cov2d's diagnostic, run on the committed G18 C_T with
  synthetic errors only and no toy, gives a maximum disagreement of about 4e-8 for 300 rows: 40 times the tolerance, and
  far below κ·ε.
- **AR23 is unaffected.** Its C_T is at 9.99e-13, so ndf = 204 and the check is skipped.

**Rulings.** These are made before any coverage number has been produced, from the matrix's conditioning alone.
1. **The cross-check's tolerance at ndf = 205** becomes `tol = max(1e-9, 10 · κ₂(C_T) · ε)`.
   - κ₂ = λ_max/λ_min of C_T, computed from C_T alone before any toy is read, and ε is float64's machine epsilon.
   - The score record records κ₂ and tol.
   - For G18 this gives about 2.1e-3.
   - The check keeps its purpose: an implementation error gives disagreements of order one, which it still catches.
2. **Unchanged:** the statistic (`chi2_nonnull`), the rank cut (1e-12), ndf, and every reading and licence.
3. **A grade Refusal must not crash the driver.** `phase_score` catches it, writes `score_<T>.invalid.json` with the
   refusal's text and the values it compared, prints a distinct INVALID verdict, and finishes Run (the atime and
   open-audit results).
4. **The implementation is cov2d's.**
   - It is a minimal change to `fd_1b_mc.grade` (a tolerance argument, with the default unchanged for 1B's ended uses)
     or a wrapper in `cov2d_readout.py`. Choose one and justify it.
   - Tests: on a fixture C_T with κ ≈ 1e12, the correct implementation passes and a deliberately wrong Cholesky
     refuses. The 1B default is unchanged.
   - REQUIRED mutants, coverage-5b-audit's audit, then this addendum's M line.
5. **The order:**
   - AR23's phase S may run now at M = `ac25b665`, because its ndf = 204 path doesn't reach the check. If it hits any
     other refusal, it's INVALID and reruns at A5's M.
   - G18's phase S reruns only at A5's bound M, from the same committed null (`ecdb4be2…`).
   - The G18 toys read in the INVALID run produced no output, and nothing from them was seen.

### Addendum A5, the M line: the code (director, 2026-11-08)

**Binds A5's code,** as merged in #900 at **M_A5 = `b1d56e4f08e62983784e34b2278f38a09a68eca0`**. The audited code head
is `49e42022`, and `git diff 49e42022 b1d56e4f -- 2d-unfolding/ nd-unfolding/fd_1b_mc.py` is empty. `76eb30d0` adds
receipts only.

| file | sha256 (prefix) |
|---|---|
| `2d-unfolding/cov2d/cov2d_readout.py` | `0c3ad137be128691` |
| `2d-unfolding/cov2d/cov2d_readouts.py` | `a288592ff0a726d6` |
| `2d-unfolding/cov2d/cov2d_score.py` | `6616e14ef32699ac` |
| `nd-unfolding/fd_1b_mc.py` (grade's `chol_tol` and `chol_out`; the 1B default 1e-9 is unchanged) | `936e1957d330e24d` |

**What the director checked:**
- **The code.** coverage-5b-audit's GO at `49e42022`
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/900#issuecomment-6716452638). A5-C1 is closed.
- **The mutants.** The lane's harness killed 24 of 24, including the auditor's V11 (the catch widened to any exception)
  and V12 (the catch widened to cov2d's own Refusal). The auditor's own V06 and V08 are killed.
- **The cluster receipt.** `76eb30d0`: 28 A5 tests RAN-OK under root_6_28, with the same failures as before in all four
  comparisons, all from the environment. 17 of 17 log sums match.
- **Nothing has read a toy** at this M.

**Rulings:**
1. **Ruling 1 is extended to C_T⁻.** The leave-out-MEC grade's cross-check uses the same rule, with κ₂ computed from
   C_T⁻ alone (`cholesky_check_minus`). Both grade calls are inside the catch of ruling 3.
2. **Ruling 5 is amended.** Phase S's gate needs a null recorded at the M it runs under, so G18's null is recomputed:
   - **phase N reruns for G18 at M_A5,** into a fresh run directory;
   - **a field-equality control** against the committed null `ecdb4be2…`. Every field must be equal except the fields
     that record the code identity (the M and the code digests). cov2d names those fields in the connect, before it
     runs. Any other difference is a STOP, reported unrepaired;
   - its receipt PR is merged before phase S;
   - **phase S then runs at M_A5** with `--null-digest` set to the new null's digest.
3. **The two held lows,** L-A5-a (κ₂ = inf on λ_min ≤ 0, so tol = inf and the check never compares) and L-A5-b (a NaN
   `max_rel_diff` passes `> tol`), **are closed for this run by a reading rule, not code.**
   - For every grade with ndf = 205, the score record must show a finite κ₂ and tol, and a finite `max_rel_diff` ≤ tol.
   - Otherwise the truth's score reads INVALID, and comes to the director unrepaired.
   - The code fix stays on the auditor's follow-up list.
4. **The launch guard.** cov2d disclosed that while testing its wrapper `go.sh`, it twice invoked it with the real digest
   of the old G18 connect. Both calls exec'd `launch-s5.sh nG18`, which refused at its first action because the run
   directory existed. Nothing was staged or run, and `run-nG18` is unchanged. The ruling:
   - a wrapper that can exec a real launcher is tested only against a stub launcher, never with real digests;
   - a launch without the director's go on that connect's sha256 is a STOP, whatever refuses it first;
   - this incident is recorded in the phase-N rerun's receipt.
5. **Unchanged:** A4's rulings 1–5, the statistic, the rank cut, ndf, every reading and licence, the fence (rs1_* and
   ens1_* job names allowed, cov2d-* or an unknown name refusing), and the readout due date.


Nothing is submitted, deposited or tagged.
