# COVFIX PG seal and ledger: dispositions of codex-school2's round-5 confirm read (cov2d, round 6)

The confirm read of 6ba32779 -> b9642de9 (`REPORT.md`, codex-school2, gpt-6.2-sol at high effort, 112,968 tokens)
returned NO-GO: 11 items FIXED, 10 PARTIAL, and six new defects (four MAJOR, two MINOR). The director ruled on
2026-11-27:
- The threat model is mistakes and lasting changes, not hostile same-account actors.
- Only a finding that could change a published number or a gate's acceptance, or cause a false STOP of a correct run,
  blocks.
- Round 6 folds items 1, 3, 4, 5, 6, 8, 9 and 10 below, each with a failing test first and mutants. Item 2 is folded
  only if it is a one-line reorder. Item 7 is deferred to PV.
- Round 6 is the last round. After its receipt run and one codex-school2 confirm read, everything outside the scope
  rule goes to `../../FOLLOWUPS.md`.

Every folded item was reproduced first: the new tests were run on b9642de9's unchanged modules (16 failures and 5
errors; `REPRO-r5.txt`).

<!-- absence-ok: each row states what this lane's own code did before its fix, as the read found it, not a claim that a result does not exist -->
| # | the read's finding | disposition |
|---|---|---|
| 1 (item 2) | `str.splitlines` breaks a directive line at `\v`, `\f`, `\r`, `\x1c`-`\x1e`, `\x85`, ` ` and ` `, but Slurm's parser ends a line only at `\n` and reads them as whitespace, so `#SBATCH --account=m3246\v--array=0-3` passed the filter while Slurm would read `--array` | `_script` splits only at `\n`. The strict form `#SBATCH( \S+)+` then refuses any such character inside a directive line. Test: `test_r5_1_*` (all nine separators, each refused by the directive rule's own message, then the plain form passes). Mutant: `r5-directive-splitlines`. |
| 2 (format 4) | a torn append after an older policy is refused as "not JSON" before the format diagnostic | Not folded: moving the check into `_entries()` is more than a one-line reorder. Both paths refuse. `FOLLOWUPS.md` item 2. |
| 3 (item 7) | a stray whose comm is truncated inside a UTF-8 character raised before `StepRefusal` was built, so the run said "internal error" with no inventory | `_proc_field` decodes comm with `backslashreplace`. Test: `test_r5_3_*`. Mutant: `r5-comm-strict-decode`. |
| 4 (item 8) | the 15 s bound was not enforced end to end: the SIGTERM cleanup re-hashed gpgconf before its timeout began, so a stalled read could use up Slurm's KillWait | `gpg_run` hashes gpg and gpgconf at its start, before the SIGTERM hold, and `_gpg_run` uses the verified paths, so nothing is hashed while a SIGTERM waits. R1's check before each use is kept; a changed gpgconf now refuses before gpg runs. Test: `test_r5_4_*` (a verify that stalls 20 s; the held SIGTERM still ends within the bound; 39.8 s before the fix). Mutants: `r5-verify-under-hold`, and `gpg-unverified-at-exec` and `gpgconf-unverified-at-exec` retargeted. |
| 5 (M1, M2, MAJOR) | the failure trap's hashing raised on one unreadable W file, so it added no hashes and skipped the scratch scan | The trap hashes file by file and counts the unreadable ones; the scratch scan runs whatever the hashing found. Any unreadable file is recorded (`trap_unreadable`), fails the run, and reduces the step-check inventory to its count, since the leak guard cannot know that file's hash. Tests: `test_r5_5_*` (a spill naming a readable file's hash is still removed; the inventory keeps only its count). Mutants: `r5-hash-file-error-raises`, `r5-unreadable-not-counted`, `r5-inventory-kept-when-unreadable`, and `sb-m1-trap-hashes-not-seen` retargeted. |
| 6 (gen-spec, MAJOR) | JSON keeps the last of two equal keys, so a first value holding a seed escaped the scan while the pinned file kept it | `load_spec` parses with a hook that refuses a duplicate key at any depth ("the gen-spec has a duplicate key"). Test: `test_r5_6_*` (top level, inside env_set, inside a required entry). Mutant: `r5-duplicate-keys-allowed`; `specpin-second-read` retargeted. |
| 7 (decryptors, MAJOR) | SealedManifest's backing dicts can be changed by a caller, which would stop publish_guard refusing a removed entry's hash | Deferred to the PV design round (no PV caller exists yet): `FOLLOWUPS.md` item 1. |
| 8 (publish_guard exemption, MINOR) | a verified, allowlisted sums line was refused when its digest happened to contain a seed's 8-hex form (`sha256(b'{"ratio": 1.02}\n')` contains `6bd2c85c` = 1808975964) | A false STOP of a correct run. Each verified digest, where it stands as a whole 64-hex token, is blanked before the seed and digit-run scan; everything else is still scanned. Test: `test_r5_8_*` (the reader's example passes; the seed's hex elsewhere, the digest inside a longer hex run, and the seed's decimal still refuse). Mutants: `r5-digest-token-not-exempt`, `r5-digest-substring-exempt`. |
| 9 (env_set (iii), MAJOR) | env_keep and env_set both admitted SCRATCH, which the director's ruling puts in neither | `load_spec` refuses SCRATCH in either list. Test: `test_r5_9_*`. Mutants: `r5-scratch-keepable`, `r5-scratch-settable`; `tmpdir-keepable`, `envset-overlap-ok` and `envset-tmpdir-ok` retargeted. |
| 10 (JE's note) | covfix_pg.py's docstring cited rev 11.4 and said the wrapper ran pg-connect with no allocation | Text only: rev 12 section 4.2, and the job check's reason is now the wrapper's exclusive salloc node (#1340), which the check makes sure of. |

**Mutation:** PG 229 mutants (219 + 10 new); 8 retargeted to round 6's lines with the same meaning
(`tmpdir-keepable`, `gpg-unverified-at-exec`, `gpgconf-unverified-at-exec`, `r4-proc-field-exe-as-text`,
`sb-m1-trap-hashes-not-seen`, `specpin-second-read`, `envset-overlap-ok`, `envset-tmpdir-ok`). Ledger 115 (114 + 1).
The receipts are single full runs against round 6's bytes (`../../code-receipts/`, `../../../../ledger/code-receipts/`).

**A stopped run (host load).** The first full PG run against these bytes started at 07:28:29Z on 2026-11-27 with
`--jobs 6` and was stopped at about 09:50Z. It had 23 kills, 4 TIMEOUTs at the harness's 3600 s limit
(`seed-limit-strict`, `u-stride`, `walk-errors-ignored`, `max-products`), and no survivors. The Mac's load average was
274 on 10 CPUs, with other lanes' long jobs running. A timeout counts as a survivor, so that run could not give 229/229,
and it wrote no receipt. All four mutants were killed in round 5's full run, and the tests that kill them run late in
the suite. With the director's agreement, the harness and its 3600 s limit are unchanged. The receipt run was relaunched
with `--jobs 3` once the heaviest of those jobs had finished and the load average was under 20. The stopped run's output is kept outside the repository; it is not a receipt.

**The receipt run** (`--jobs 3`, started 21:22:02Z on 2026-11-27, ended 2026-11-28) killed 229 of 229 PG mutants with
no survivor, timeout or harness error. The ledger killed 115 of 115. Both test suites are OK.

<!-- absence-ok: a coverage statement about this lane's own receipted test file and line trace, not a claim that a result does not exist -->
**Line trace.** covfix_pg.py is at 99%: lines 549-551 are untraced (round 5 was at 100%). They are round 6's
fallback in the trap for a W that cannot be walked at all: the run is marked failed and the scratch scan still
runs. The receipted test file has no test for it. An out-of-tree check after the receipt run (`REPRO-r5.txt`, last
block) made the walk raise inside the trap on round 6's unchanged bytes and got rc 1, `trap_unreadable: "failed"`,
and the scratch scan still ran. The branch only acts on a run that is already failing, so it cannot change a published
number or a gate's acceptance, and adding a test now would void this receipt. It is `../../FOLLOWUPS.md` item 3.
covfix_seal.py's 181-185 are the forked child's preexec body, untraceable as before.
