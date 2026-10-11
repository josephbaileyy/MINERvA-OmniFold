# SB1 focused re-review of the record repairs (767d0f08)

**RE-REVIEW: REPAIRS ACCEPTED**

All three findings are repaired accurately and sufficiently. The repair introduces no new inaccuracy that affects a verdict, a criterion or a number. Three residual MINOR or NOTE points follow at the end. None of them blocks acceptance, and each can be fixed at the owner's discretion.

## Setup facts

- **Reviewer.** The same read-only reviewer as the admission review and the final verification. This is the one authorized re-review, scoped to the repairs.
- **UTC window.** Start 2026-10-11T02:00:48Z; end of checks 2026-10-11T02:03:50Z, review written just after.
- **Worktree.** `/private/tmp/sb1run-review-c`, detached at `767d0f08895ea7fc2c5817c8b83d6c0af249e074`; its parent is `4cab15aa`.
  - `git status --porcelain --ignored` printed 0 lines at start and 0 lines at end.
  - The worktree and `/private/tmp/sb1run-review-scratch-c` are removed after this file is written.
  - Nothing was edited or committed in the repository.
- **CPU.** Under 0.02 core-h: git diffs and four `generate_manifest.py --at-sha` runs.
- **Cluster.** No access needed and none used. No scheduler command was run.
- **Branch is pushed.** `git ls-remote origin refs/heads/run/sb1-20261010` = `767d0f08…`.

## (f) Scope of the change

- **Files.** `git diff --name-only 4cab15aa 767d0f08` lists exactly two files: `Q/sb1-run/REPORT.md` and `Q/sb1-run/review/final-verification.md`.
- **My verification is preserved unchanged.** `review/final-verification.md` has sha256 `bce837c95a9f16a7cd3ef3264c21c27b9a27120da14de55575355c1124b69a4c`, identical to my original `/private/tmp/sb1run-review-final.md`.
- **Package unchanged.** `git diff --quiet 016265cc 767d0f08 -- Q/sb1-prep` holds.
- **No criterion, number in a criterion or verdict changed.** I read the full REPORT.md diff.
  - The only edit inside the §7 criteria table is the P row's "measured" cell. It is reworded to disclose the refusal, and P stays **PASS**.
  - The S1–S6 rows, every number in them, the overall PASS and §6's accounting are untouched.
  - Every other change is added disclosure text, the new §7.6, the §8 summary and the new §11 items 5–6.

## Per-finding disposition

### Finding 1 (MATERIAL): ACCEPTED

| site | what changed | accurate? |
|---|---|---|
| P row (REPORT.md:326) | Now states that all 15 inventories satisfy P's rule (installed, `allow` empty, 0 origins outside, the manifest's shim, `violation` null), and that UL's and SL's inventories each record one refused child launch (`lscpu --parse=core`), which P's rule does not test | Yes. "Clean" is gone |
| §7.6 (lines 448–478) | Recorded facts and their sources | Yes. The `.err:11-15` citations are correct for both UL and SL: I re-read SL's lines 11–15. C and J1 show no guard refusal; J1's controls end `child-systemexit:5`, which is a selection refusal, not a launch refusal |
| §7.6 | Code path (loky affinity test, the `lscpu` fallback to `/proc/cpuinfo` core ids), the login23 measurement (64 vs 128), and C's exemption at affinity 64 | Yes |
| §7.6 | Labels the thread count as an inference, unrecorded, with the compute nodes' `/proc/cpuinfo` not read | Correct |
| §7.6 | Consequences: none for the verdict; the `omnifold` timings are not the production configuration's | Correct |
| §7.2 (lines 375–376) | Qualifies the frozen "128-thread" wording | Yes |
| §7.4 (lines 420–422) | Qualifies the `omnifold` phases | Yes |
| §10 "Measured" | Adds the 64-thread qualifier and the guarded-run share | Yes |
| §11 item 6 | Proposal to the guard owner and the helper owner, marked untested; asks future timed runs to record the effective thread count | Yes. Its residual is note R2 |

### Finding 2 (MINOR): ACCEPTED

- **§7.1 (lines 355–360).** It now says the J1 pairs are not matched: the `all` runs started together at 23:53:19Z, and the `selective` runs ran one after another, 00:16:14Z → 00:21:51Z. Those times are what I measured. It also says the `all` times include four-way contention and may overstate the saving.
- **§10.** Both the "Measured" bullet and the forecast bullet repeat the qualification for the 1,755.5 s basis.

### Finding 3 (MINOR): ACCEPTED

§6 (lines 291–294) now states:
- input stats are checked at each job's start and end against H0, and H1 = H0;
- the top-level env-setup digest is checked once, at each job's start, against the submission-time digest;
- the two sourced sub-setups are not covered.

The conclusion is narrowed to "none of SB1's inputs or its top-level setup". All three points are accurate.

### (d) §8 summary of my verification: faithful

- **Verdicts.** Both are stated exactly: RESULT VERIFIED: PASS, and RECORD: REPAIR NEEDED, disclosure only.
- **Setup facts.** The 01:52–01:57Z window, 0-line worktree status at start and end, and no sbatch, srun, salloc, scancel or cluster writes are all correct.
- **Recomputation summary.** It is correct:
  - 18 sacct rows equal field by field;
  - S1, NC and S6 recomputed with my own code;
  - S5: 12 of 16 histograms identical, the four named histograms differ, by at most 6.395e-13 in content and 6.55e-13 in errors;
  - C1 empty at 01:52:37Z.
- **Findings and notes.** The three-finding table keeps my severities, and notes 4–7 are represented correctly.
- **Placeholder.** §8.1 holds `RE-REVIEW_PENDING` (line 520), for the owner to replace with this verdict.

### (e) §11 item 5 (MANIFEST.tsv): accurate

I compared `generate_manifest.py --at-sha 4cab15aa` with `git show 4cab15aa:docs/orchestration/MANIFEST.tsv` using my own diff:
- the headers are identical;
- **77 rows added, all under `Q/sb1-run/`**, and 0 removed;
- **46 rows changed, none inside `Q/sb1-run/`**;
- the changed columns are `inbound_count` (46), `consumer` (2: `P/launch/sb1_submit.sh` and `P/sb1_verify.py`), and `lines` and `bytes` (1: MANIFEST.tsv itself);
- no class or other column changed.

The `--check` runs agree with the "since `f7135d31`" claim:

| `--at-sha` | result |
|---|---|
| `016265cc` | OK (exit 0) |
| `2b35ba52` | OK (exit 0) |
| `f7135d31` | OUT OF DATE (exit 1) |

Deferring the regeneration to integration is consistent with this lane's file scope.

## Residual points (not blocking)

- **R1, MINOR: one "128-thread" site was not qualified.** REPORT.md:582 (§10, "Precondition") still advises that a deployment proposal state "the 128-thread rerun envelope is unmeasured", with no pointer to §7.6. The sentence is still true, but this is exactly where a proposal author would carry the configuration forward.
  - Suggested fix: add "(and that UL/SL very probably trained with 64 LightGBM threads, §7.6)".
  - My finding 1 cited this sentence; it was then at line 497.
- **R2, NOTE: the first remedy in §11 item 6 conflicts with the guard's own policy.** Item 6's first option (line 627, "model `lscpu` as a leaf tool in the guard's launch grammar") runs against the refusal banner itself, which says "do not widen the leaf table to make a launcher pass" (`sb1_UL_59645300.err:15`). The item does mark both remedies as untested proposals for the guard owner. Mentioning the conflict, or preferring the explicit-`n_jobs` remedy, would save that owner a step.
- **R3, NOTE: §7.6 slightly overstates S3's independence.** Line 473 says "S1, S2 and S3 do not depend on training threads". S1 and S2 do not. sacct MaxRSS (S3) can depend weakly on the trainer's thread count, through per-thread buffers. Both arms ran with the same count, so S3 is still a matched comparison and its verdict stands. "S3 compares matched runs" would be the exact wording.
