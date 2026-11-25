# codex-school2 read 3 of the PG seal code and the ledger, at af5fdd5b: dispositions

The verdict was NO-GO (`REPORT.md`). The reader's bytes have sha256
`db913595f6666abef822b5fe771acb6a295211f8469baf75673e188706ecd268`. The committed file adds one line, the
`absence-ok` waiver above item 10 that the pre-commit absence check needs. It has sha256
`d66383e9d91ffcfd3e2a64a21bae13ed437a7e30b727cbbc5811b88ec80b6cae`; deleting that line restores the reader's bytes.

The director gave a GO on 2026-11-24 for items 1–6 and 8–10 and ruled on item 7. **Each finding was reproduced by a
failing test on the round-3 code before it was fixed.**
- Ledger findings: the tests are `test_covfix_ledger.Round3Findings`.
- PG findings 6 and 8: the tests are `test_covfix_seal.Round3Findings`. They ran against af5fdd5b's modules through a
  shim that writes the old four-key gen-spec. All five failed: 4 failures and 1 error.
- Items 7 (the detector) and 9 (the inventory) add new behaviour. Their tests failed until it existed.

Every finding reproduced. None was fixed blind.

| # | finding | disposition |
|---|---|---|
| 1 | a cap amendment below spent + held is bypassed by an existing intent | `amend_cap` refuses a cap below the group's spent + held (fixed lines included), and replay refuses such an amendment. `claim()` rechecks the group cap and the ceiling with the intent held. That recheck fires after an overrun charge (TIMEOUT beyond the limit). Tests: `test_f1_*`, `test_f4_replay_refuses_an_amendment_below_held`. |
| 2 | one claim can launch an array | `submit` reads the script once. Every `#SBATCH` directive must be on the allow-list (`EXTRA_OK`); `--array`, `-a`, `--nodes=` and a bare `#SBATCH` are refused before any sbatch. The bytes go to sbatch on **stdin**, never by path. sbatch, scontrol and scancel get an environment with **every** `SBATCH_*` and `SLURM_*` variable removed (the director's note). scontrol showing `ArrayJobId` or `ArrayTaskId` is a mismatch, so the job is scancelled and a STOP is recorded. Tests: `test_f2_*`. |
| 3 | a reconcile between sbatch and record skips verification; a failed scancel is recorded as "scancelled" | `record_submission` is idempotent for the same intent and job. A recorded job always goes through scontrol, and a pass records `verified`. `accept` (and replay) require a verified submission, so a job recovered from sacct by name (kind `recovered`, never verified) can never have products accepted. scancel's exit status is checked; a failure is recorded as "scancel failed; the job may run". Tests: `test_f3_*`. |
| 4 | replay accepts what the live API refuses | Replay now requires: job IDs that are canonical decimal **strings** (an int 42 is refused); a claim before `submitted` or `recovered`; the intent gate (`_fits`) at every intent line; amendments at or above spent + held; acceptance only of a verified job with a 64-hex sha256; and release evidence for any zero charge. `recovered` is an explicit transition. Tests: `test_f4_*`. |
| 5 | an unknown start releases the whole hold | A zero ElapsedRaw releases the hold (charge 0) **only** on CANCELLED with Start `None` (the director's rule). Any other terminal state with zero elapsed is charged the full reservation. Every charge persists its sacct row as `evidence`, and replay checks the evidence behind a zero charge. Tests: `test_f5_*`, `ZeroAndCanon`. |
| 6 | an equal-length overwrite with mtime kept is missed; one unreadable entry aborts the scans; a failed removal disarms the trap | A regular file's signature includes `st_ctime_ns`; restoring mtime with `utime` still moves ctime. The post-run and trap scans collect walk and lstat errors and carry on. An unreadable file is a hit (removed, and the run fails); an unlistable directory fails the run (`scratch_scan_errors`). The trap is disarmed only when `remove_verified` returns True, so a False retries in the trap. Tests: `test_f6_*` (overwrite, unreadable, unlistable, false removal). |
| 7 | a setsid child survives end_group | **The director's ruling: (a) plus a detector.** F1's bound pipeline never detaches, so this falls under §4.2's same-account cooperative assumption, like R2, and is disclosed in §4.2 (rev 12). Just before the seal, `step_cgroup_check()` reads `/proc/self/cgroup` (it must be a single v2 entry) and that cgroup's `cgroup.procs`. It refuses to seal if any pid is there other than the sealer's own and its ancestors'. An unreadable or non-v2 cgroup is a STOP. Ancestors rather than "declared children" is a deviation the director accepted: the generator is reaped by then, and the wrapper shares the step. A reparented escapee (parent pid 1, a subreaper outside the step, or the sealer itself) is refused. The summary records counts only: `step_cgroup` = {pids, ancestors}. The synthetic-seal rehearsal runs the detector on a compute node and records what the step holds; if it does not work there, the question returns to the director. Tests: `test_f7_*`. |
| 8 | SIGTERM can interrupt GPG cleanup | `gpg_run` installs a handler that only records a SIGTERM for the whole run: gpg, the agent shutdown and the home's removal. It then restores the previous handler and delivers a held SIGTERM to it. The handler is not inherited across exec, so gpg and gpgconf see the default. Test: `test_f8_*` (a SIGTERM sent during the gpgconf call; SystemExit is raised and the home is gone). |
| 9 | a log-only PRODUCTS.json is receipted | The gen-spec has a fifth key, `required`: a non-empty list of distinct `{"pattern", "count"}`, each pattern relative with no `..`, each count an integer ≥ 1. After the run, each pattern must match exactly its count of regular files under W (fnmatchcase; links never followed), or there is no receipt (`required_products`). The director accepted this generic list as the interim. tune-generator's code-defined `pg_lib.py inventory` prints the same format: 93 patterns covering 201 files at the pin candidate 2b57d84e9decd94db5af3a482851c8218a91b42f (`pg_lib.py` sha256 20c8a824fda9d511af07cc2638e3b1e45c2edb5bcb2ae67118c205445029cb8f), which superseded c12d2d28. It is pinned by the binding once the director accepts A2. Tests: `test_f9_*`. |
| 10 | receipt provenance | (a) The PG line trace listed `covfix_ledger`, because the two coverage data files shared a directory and the report had no `--include`. Each now has its own directory, and each report has its own `--include`. (b) r2's DISPOSITIONS said "single full runs"; it is corrected in place, with a note. (c) Round 4's mutation receipts are single full runs against the committed bytes, so no historical test file needs archiving. |

**Round-2 items the read left PARTIAL:**
- 3, signal cleanup: item 8.
- 5, required products: item 9.
- 6: items 6 and 7.
- 10 and 12: items 4 and 5.
- 13: items 1–3. The connect-side digest verification is the connect's, not this code's.
- 7, `read_ciphertext()` accepting a supplied map: left as is. Its only callers pass the map parsed from the pinned,
  decrypted manifest after `seal_check`. Making the reader re-parse the index is noted for the director.

**Mutation:** see `pg/seal/code-receipts/mutation.txt` and `ledger/code-receipts/mutation.txt`, both single full runs.
- Ledger: 100 mutants, all killed. The first pass left 15 survivors; each was killed by a new test before the final
  run. Three more cover launch failures the line trace showed unexecuted. One more covers the branch the af5fdd5b
  trace left partial: a fixed line counts only in its own group's total.
- PG: 130 mutants, all killed. A first pass left 6 survivors: an lstat error, scan errors alone, the trap's tolerant rescan, exact counts, a hybrid cgroup file and a gap in the ancestor chain. Each was killed by a new test before the final run. Two more cover the SIGTERM holder off the main thread and under the default handler. The harness now uses failfast and counts a timeout as a survivor.
