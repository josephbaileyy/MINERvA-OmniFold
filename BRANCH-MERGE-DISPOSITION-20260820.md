# Branch-merge disposition — all 18 non-main branches

Measured 2026-08-20 at `main = eb6aba5f9ef7c197766b2bb0ce58a24584afe2b2`, re-measured from
scratch rather than inherited. Supersedes the disposition in the handoff brief
`BRANCH-MERGE-HANDOFF.md` (session scratchpad, job 57294218) on two points, recorded below.

**Bottom line: there is nothing to merge.** Every branch is either already contained in `main`,
or its content landed on `main` and was then deliberately retired by the prepublication
compaction, or it was deliberately abandoned/excluded with a pushed tag. No merge is recommended,
and none was performed.

## Method

Two-dot `git diff main $b` is wrong here: it also lists every path `main` DELETED in the
compaction, which reads as "the lane's work never landed" when the opposite is true. Merge-base
relative instead:

    mb=$(git merge-base main $b); git diff --name-status $mb $b

Then, per path, three separate questions — is it in `main`'s tree now; did `main` ever have it
and delete it (`git log --diff-filter=D main -- $p`, *not* `git rev-list`, which rejects the
flag); and does the lane's blob differ from the version `main` retired. Answering only the first
is what produces a false "additive merge".

## Correction 1 — the "easy win" additive doc merges do not exist

The brief listed four documents as absent from `main` and safe to merge (`lane-c` x3,
`worktree-agent-ad6f28712c1118a2c` x1), and separately flagged `lane-d`'s document as a
resurrection question because `main` had deleted its path.

Measured: **all five are the same case.** Each was on `main` and was deleted by
`84607aa3 "Retire frozen orchestration history from live tree"` — 734 files deleted under
`docs/orchestration`, 145,356 deletions, 0 renames, an ancestor of `main`. And each lane blob is
**byte-identical to the version `main` retired**:

| document | lane | blob on lane | blob at `84607aa3^` | verdict |
|---|---|---|---|---|
| `FINDING-20260820-a-test-can-assert-the-defect.md` | ad6f2871 | `14aedf71c037` | `14aedf71c037` | identical |
| `DECISION-BRIEF-20260819-oi71-recovery-evidence.md` | lane-c | `4bd1af663f83` | `4bd1af663f83` | identical |
| `DETERMINATION-20260819-lanec-petclosure-is-legacy.md` | lane-c | `549a11429f75` | `549a11429f75` | identical |
| `RULING-20260819-lanec-measured-leg-is-two-products-not-a-contradiction.md` | lane-c | `49d1febc847f` | `49d1febc847f` | identical |
| `AUDIT-20260819-analysis-note-vs-record.md` | lane-d | `fb3fc5e0b90d` | `fb3fc5e0b90d` | identical |

So merging any of them re-adds a file the freeze removed. The brief applied that reasoning to
`lane-d` alone; it applies identically to the other four. The distinction it drew between "easy
additive win" and "Joseph's call" does not survive measurement — **all five are the same
authorization question**, and none is a text merge.

Corroboration at commit level: every lane commit has a same-subject counterpart already on
`main` (`d27f95d6`→`e839663d`, `5fb1bfbd`→`d8a1d7ef`, `251a1b4f`→`050b33ff`, `d7c713a9`→`9f233466`,
`52e1adaa`→`40e0ad9b`, `7bfcf51d`→`06cb845e`, `667a057a`→`9d05f2b1`, `b6cbf807`→`a56f0b14`).
`git cherry` still marks them `-` rather than `=`, because each lane commit also carried a
`MANIFEST.tsv` regeneration, so the patch-ids differ even where the document blobs are identical.
The blob equality above is the load-bearing evidence; the commit twins only corroborate it.

Recovery route is intact: every retired path is readable from
`evidence/prepublication-2026-08-20-0b329e8a` (**703 of 703** of the still-absent ones checked
individually), and that tag is confirmed **on the remote** by `git ls-remote --tags origin`, not
merely present locally.

The freeze was also not all-or-nothing, which matters for the decision below: of the 734 paths
`84607aa3` deleted, **31 were deliberately restored to `main`** afterwards by
`20af4e9e "Restore active evidence and control-plane guards"` (the `test_agentctl.py` /
`test_usagectl.py` control-plane guards, the `gate5-cstat-spec-measurements-20260814/` scripts,
the `p3f-hpss-to-cfs-20260818/` receipts and three `probe-oi126-*` state files). **703 remain
retired.** So a named, already-exercised route exists for bringing a specific retired path back
when it is still active evidence — the question for any of the five documents is whether it
qualifies, not whether the mechanism exists.

Consequence: the brief's two headline hazards — never text-merge the generated `MANIFEST.tsv`
(+1024/-264 on lane-c), and regenerate only in a clean worktree because `inventory()` at
`docs/orchestration/generate_manifest.py:69-72` sweeps untracked files under that directory — are
**moot**, because the doc merge they guard is not the right action. Both are correct as written;
they just have nothing to apply to. No manifest regeneration was run, and no file was created
under `docs/orchestration/` (which is why this report sits at the repo root).

## Correction 2 — the brief's enumeration covered 9 of 18 branches

Nine local branches were absent from the brief: `audit/20260731-findings`,
`audit/5d-nonbkgaware-20260820`, `codex/docs-control-plane`, `codex/prepublication-compaction`,
`codex/thin-main`, `lane-b`, `note-dead-number-repair`, `packet-b-quoted-number-debt`,
`receipt-2d-tune-chi2`, `worktree-gbdt-closeout-runbook`. Eight of those are `ahead=0` off their
merge base — fully contained in `main`, nothing unique. (This includes `lane-b`, the sole builder
for C_stat/OI-121: nothing of its work is unmerged.)

The tenth, `audit/20260731-findings`, was genuinely unmerged-looking and is the one item the
brief's method would not have surfaced. It resolves clean:

- `nd-unfolding/tests/test_b1_normalization_fix.py` — its two power tests
  (`test_varying_push_separates_the_weighted_mean_from_the_plain_mean`,
  `test_gate_accepts_a_correct_unfold_whose_push_is_not_flat`, closing a vacuous pass where every
  existing case fed a *constant* push and so could not distinguish a w-weighted mean from dropped
  weights) are **already on `main`** at lines 884 and 907, and the extracted bodies are
  byte-identical (3181 bytes both sides). The file blob differs only because `main`'s copy moved
  +770/-76 around them.
- `nd-unfolding/tests/test_g2_guards_collected.py` — blob identical to `main`.
- `docs/orchestration/AUDIT-FINDINGS-20260731.md` — survived the compaction; all 42 finding IDs
  (J01–J42) are present on both sides and `main`'s version is a strict superset (+515 lines).
- The branch tip `bb16c270` is preserved by the pushed tag
  `evidence/prepublication-excluded-audit-bb16c270` — i.e. it was *deliberately excluded* from the
  prepublication set, not overlooked.

## Confirmed from the brief, re-measured

- `worktree-agent-a26a858ce260f3238` — superseded. Its `mii_adopt_unified_5d_stamped.py` is the
  older copy; `main`'s differs and is the later one. Its two other source files are blob-identical
  to `main`.
- `worktree-peer-for-codex-gbdtfive-strike` / `-oi126-runnability` / `-prose-followup` — all three
  tips are on `origin` at the **same shas** (`7bbeba6c`, `627b3cf3`, `5409cfac`) as
  `abandoned/peer-for-codex-gbdtfive-strike`, `abandoned/peer-for-codex-oi126-probe-fix` (note the
  differing remote name), `abandoned/peer-for-codex-prose-followup`. Deleting the local refs loses
  nothing.
- `nd-unfolding/tests/test_oi126_test2_quotability.py` exists **only** on `627b3cf3` — never added
  to `main`, never deleted from it. It is the single genuinely-new file in the whole branch set. If
  wanted, take it from the abandoned ref; it is outside `docs/orchestration`, so no manifest or
  freeze question attaches.
- `codex/gregor-pet2-omnifold` — 29 commits, 604 files off merge base, 12 dirty files in the
  parent-dir worktree. Not touched, not cleaned, not stashed. Tip preserved by pushed tag
  `evidence/prepublication-excluded-gregor-b65f9ff2`.
- `nd-unfolding/mii_adopt_unified_5d_stamped.py` was not modified: verified blob-identical between
  `main` and `worktree-agent-ad6f28712c1118a2c`, so job 57294218's result still binds to a tree.
- The two locked worktrees named in the brief, `fps-audit-oi50` and `oi-repo-hijack-row`, do not
  appear in `git worktree list` at all and have no branches. Nothing to unlock; nothing was asked.

## For Joseph — two decisions, neither a merge

1. **Do any of the five retired documents come back?** They are not lost (703/703 recoverable from
   the pushed tag), so this is a question about what the live tree should say, not about recovering
   evidence, and `20af4e9e` shows the restore route is already established. The one with a live consumer is
   `DECISION-BRIEF-20260819-oi71-recovery-evidence.md`: OI-71 is still routed to you in
   `docs/CURRENT_WORK.md`, and that brief is the input to a decision you owe. Reading it from the
   tag costs nothing and needs no authorization; re-adding it to `main` reverses part of the freeze
   and needs yours.
2. **363 of the 703 still-retired filenames are still cited on `main`**, across 77 live files —
   concentrated in `RUNS.tsv` (267) and `state/sessions.json` (84), but also `README.md` (12),
   `FINDINGS-ARCHIVE-2026-08.md` (11), `INDEX-retracted-and-superseded-values.md` (8),
   `RESTORE-2026-08-03.md` (7), `LIVE-STATE.md` (6) and `state/live-state.json` (6). For a
   historical ledger like `RUNS.tsv` that is arguably correct — the tag is the discovery route.
   For live navigational docs (`README.md`, `LIVE-STATE.md`, `state/live-state.json`) it reads as a
   dangling reference. I did not change any of them: repointing citations across 77 files is a
   freeze-scope act, not a cleanup.

   One clean signal in the other direction: **`MANIFEST.tsv` cites none of the 703** — it was
   regenerated correctly after the compaction and is consistent with `main`'s tree. (My first pass
   reported 31 MANIFEST hits and 389/734 outside it; that was the 734-path denominator, which
   includes the 31 paths `20af4e9e` restored. Against the 703 that are actually still absent, the
   MANIFEST count is zero.)

Also noted, not acted on: `main`'s `FINDINGS.md` was pruned 744 → 115 lines by the compaction and
carries no BEN-510 entry. That is consistent with the retirement, not a gap — the index was pruned
along with the files it indexed.

## Re-anchoring note

Measurements above were taken at `main = eb6aba5f`. While this report was being written `main`
advanced to `1b9e074c "ledger: record both remedy-(A) write-path smoke jobs, pass and fail"` — the
peer session landing its `RUNS.tsv` rows for job 57294218, which has now reported PASS 3/3. Every
headline count was re-verified at `1b9e074c` and is unchanged: 323 files under
`docs/orchestration`, 703 of the 734 retired paths still absent, 363 of those still cited, 0 of
those cited by `MANIFEST.tsv`.

Worth recording because it is the same trap as the two-dot diff this report opens with, in a new
place: before rebasing, `git diff main HEAD` on this branch showed the peer's two new `RUNS.tsv`
rows as **deletions by me**, including the `REMEDYA-SMOKE-PASS` record. Nothing was deleted — the
branch simply predated those commits, and one side had moved. This branch is now rebased onto
`1b9e074c`; its only difference from `main` is this one added file, and
`HEAD:docs/orchestration` is byte-identical to `main:docs/orchestration` (tree `5158abe4`), so the
compaction's deletions and the peer's ledger rows are both intact.

## Authorization

No merge to `main` was performed, attempted, or authorized. The handoff relayed Joseph's sentence
("another session ... can do all of the branch merge ideating and doing") second-hand and
explicitly declined to treat it as merge authority; that is the right call, and it is moot here,
since the measurement says the correct action is no merge. No branch or ref was deleted — the
drop recommendations above are recommendations. No worktree was cleaned, unlocked, or pruned.
