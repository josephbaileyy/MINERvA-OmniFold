# Focused re-review, cycle 2: Session 3 (structure), repair batch f0deb0be..90788f5f

I reviewed the repair batch `e083c5ca` and `90788f5f` read-only, in a clean review worktree at
`90788f5fa4bdb2f09b691b6f38875551e9ae2f87`.

**Verdict: ACCEPT.** All five cycle-1 findings are handled correctly: four are fixed and finding 5 is
deferred with a stated reason. All three mutants are now caught. The repair adds no new defect or
overclaim; two trivial notes are listed at the end.

## (a) Disposition of the cycle-1 findings

| # | Cycle-1 finding | Repair | Assessment |
|---|---|---|---|
| 1 | Guard paths without a test | `e083c5ca` adds these tests:<br>• `test_legacy_bootstrap_is_block_summed`: `hMean2D` only, no `hReportedCells`.<br>• `test_mismatched_bootstraps_are_refused`: subtests for perm, omit and noid, each asserting an empty `--outdir`.<br>• `test_ours_only_refuses_a_permuted_universe_and_warns_on_a_legacy_one`.<br>• An archive-target assertion in the rollup refusal test. | **Correct.** The mutants now fail (see (b)). The equal-count permutation coverage moved into a subtest; it was not lost. The covariance-shape refusal is still covered only by the harness, which is acceptable. |
| 2 | "Nothing written" | §3 and §3.2 now say "no output file written (only the empty `--outdir`)". No code change. | **Correct.** The reason given is reasonable. §10 notes that the message of commit `40330351` cannot be amended. |
| 3 | Wording | §12 now says "three … junctions" and names the count-only quoted-number junctions. The proxy qualifier is restored in `2D_OMNIFOLD_REFERENCE.md` and §13. The garbled §1 line is replaced. The parallel derivation is disclosed. | **Correct.** I found no residual overclaim. |
| 4 | Missed 3D caller | A §1 note cites `sbatch_unfold_3d_MEFHC_5iter_universes_full.sh:26-27`, the 14×16 grid, and off-grid failure in both versions. | **Correct.** It matches what I measured in cycle 1. |
| 5 | Shared writable edge arrays | Deferred to §7 item 6. Reason: a read-only buffer passed to PyROOT's `TH2D(const double*)` was not tested. | **Acceptable deferral.** This was informational and has no current effect. |

## (b) Mutants, re-run independently in a scratch copy

I used a scratch mirror with the 90788f5f tests and the unchanged scripts. Each mutation was asserted
to apply, and the copy was restored afterwards.

- Baseline: `test_reported_cells.py` ran 18 tests, all OK. `test_final_rollup_full_refusal.py` passed
  in the mirror with 1 skip, the git control. In-tree it passed all 3.
- Universe check in `_ours_only_chi2.py:116-117` removed: **FAILS**
  `test_ours_only_refuses_a_permuted_universe_and_warns_on_a_legacy_one`.
- `mean_fallback="hMean2D"` in `analyze_universes.py:150` removed: **FAILS**
  `test_legacy_bootstrap_is_block_summed`.
- Refusal loop moved below `archive_old_full_rollup` in `final_rollup_full.sh`: **FAILS**
  `test_refuses_while_a_pinned_product_exists`, in both subtests ("the archive step moved files before
  the refusal").
- Count-only `require_same_cells`, as a control: fails 4 tests, including the new perm subtest and the
  new universe test.

## (c) New defects or overclaims; source unchanged

- **No non-test source file changed.** `git diff --stat f0deb0be 90788f5f` touches only:
  - the two test files;
  - `2D_OMNIFOLD_REFERENCE.md`, with 3 lines of wording;
  - `REPORT.md`;
  - `logs/review-repair-mutants.txt`;
  - `review/review-cycle1.md`, which is byte-identical to my saved report.

  `analyze_uq.py`, `analyze_universes.py`, `_ours_only_chi2.py`, `reported_cells.py` and
  `final_rollup_full.sh` are byte-identical (`cmp`) to the reviewed `f0deb0be` versions.
- **The new test counts are right.** §8 says "18 passed; system python3 18 run, 10 skipped". That is
  3 Grid + 5 Contract tests needing no ROOT, plus 5 RootIdentity + 5 ScriptGuard tests needing it.
- **The new tests run no real work.** All inputs are synthetic and live in temp dirs.
- **The §10 and §11 statements are consistent with the facts.** These cover the reviewer's interrupted
  run, the 2.6 h stall and about 0.1 core-h.
- Trivial notes, no action needed:
  - **Phrasing in §3.2.** "The two added in the repair batch" is loose: net 16 → 18, but 3 tests were
    added and 1 was folded into subtests.
  - **The mutant log.** `logs/review-repair-mutants.txt` numbers its mutants M1–M3, which clashes with
    cycle 1's M-numbers, and it has a stray `1` line.
  - **Brittle empty-directory check.** `test_mismatched_bootstraps_are_refused` asserts
    `iterdir() == []`. It would raise an error, not fail cleanly, if the refusal were later moved above
    `os.makedirs`. That would be an improvement that the test then penalizes.

## Resources

About 15 minutes and under 0.05 core-h, with 2 threads per command. No network or cluster use.

`git -C /Users/josephbailey/local-research/MINERvA-OmniFold-next-structure-review-20261009 status --short`:
(empty; `--ignored` is also empty)
