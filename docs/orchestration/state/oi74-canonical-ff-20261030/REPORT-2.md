# REPORT 2 — OI-74: the second run of `ff2.sh` fast-forwarded the canonical checkout to `ed3590ea2` (2026-10-30)

**By** the close-items session. **Reports** the one run that [`BINDING-2.md`](BINDING-2.md) authorizes, of
[`ff2.sh`](ff2.sh) (sha256 `c0e393b08daaf20738b0657a6acea62083579d67a1f6c28f1f9a3186523fb851`) under
[`DECLARATION-2.md`](DECLARATION-2.md). The director said "go" after I told them I was about to connect.

**Outcome: DONE, with no STOP.** `/pscratch/sd/j/josephrb/MINERvA-OmniFold` moved from `32e403b84` to `ed3590ea2` on
`main`. It has no tracked changes. The four files were moved aside and then recreated by the merge with the same bytes.
Every post-check passed.

**CITABLE FOR:** what the transcript prints: every precondition, the fetch, P5, the four re-hashes and moves, the
merge, and C1–C5.

**NOT CITABLE FOR:**
- what any file says. No contents, logs or waker state were read;
- who wrote the four files, or when;
- which untracked path accounts for the fifth step of C3's fall (§3).
<!-- absence-ok: scoping statements about what this run's own transcript covers -->

## 1. The run

**One ssh to `saul.nersc.gov`,** answered by `login37` from 23:15:50Z to 23:16:40Z. The command was DECLARATION-2's
§6, run once from this directory. Transcript: [`run2/session.txt`](run2/session.txt), 66 lines, sha256
`d3798f91d8d369dda2b24d221e981403f9fba509b0f5e1299efa9d5fabd04b78`. Local rc 0, `ssh_rc 0`, git 2.51.0. One line
holds git's `Updating files` progress meter, with carriage returns, as git printed it.

| step | printed | result |
|---|---|---|
| P1 | `squeue_me_jobs 0` | pass |
| P2 | head `32e403b84e9e8f9d9bc435028749f896653c7a43`, branch `main` | pass |
| P3 | `tracked_rc 0`; exactly ` M docs/orchestration/LIVE-STATE.md`, ` M docs/orchestration/state/live-state-last-known.json` | pass |
| P4 | `untracked_before 731` | — |
| P6 | aside listing `LIVE-STATE.md SHA256SUMS live-state-last-known.json`; `tree_equals_aside YES` | pass (17, 16, 18 and 19 did not fire) |
| W2 | `checkout_rc 0`, `tracked_after_restore 0` | done |
| W3 | `fetch_rc 0`; `github/main` `ed3590ea245f23bd4c7d1f21e1dd4b6dd0fa558e`; behind 3768, ahead 0 | done |
| P5 | added 13720, present 6, identical 6, differ 0, untracked_not_ignored 4 (exactly the four) | pass |
| W5 | each of the four re-hashed equal to main's blob, then moved | done |
| P1b | `squeue_rc 0 squeue_me_jobs 0` | pass |
| W4 | `merge_rc 0`, 23:16:08Z to 23:16:33Z; `Updating 32e403b84..ed3590ea2`, `Fast-forward` | done |
| C1–C5 | see §2 | all pass; `DONE` |
<!-- absence-ok: rows of a table of the transcript's own steps -->

**The four, re-hashed just before each move** (want is main's blob, have is the file's):

| path | blob (want = have) | sha256 of the moved copy |
|---|---|---|
| `docs/orchestration/dashboard.html` | `26993f762bdbdf1cbeaa56eebf37a1c5d802d868` | `5bc229c6ab5efb7e85ee04a87af4aa90fed425ef51af637052143b3b84d22b00` |
| `docs/orchestration/dashboard_collector.py` | `f08b12e8be73d3eda1096f627f052b953baac141` | `e65cb1936e1ea895724b6f8428b1f5e98ee4338dd7f89d4552b7d7e9ab6071b2` |
| `docs/orchestration/test_dashboard_collector.py` | `e10f59723336f335d46bc57c9b69b89fcbf556f8` | `74eb77f57a3c4f7c077aa797c310b5cf42c7c8b0bf7eabbf740c2a28cbe5ba70` |
| `nd-unfolding/tests/test_cstat_100rep.py` | `5ce3dbdf84f3cf1a0b779bb7924c2eade424baf2` | `ec47ec61524d3dec8dc8f4dbda9ecd97afb161794ad4a61b9f8d37bbe51f5aad` |

The last column is what
`/pscratch/sd/j/josephrb/oi74-ff-20261030/untracked-at-added-paths/SHA256SUMS` holds.

## 2. The post-check

| | printed | must be | result |
|---|---|---|---|
| C1 | head `ed3590ea2…`, branch `main`, `head_equals_fetched_main YES` | the fetched main | pass |
| C2 | `tracked_changes 0` | 0 | pass |
| C3 | `untracked_after 726 before 731` | not above 731 | pass |
| — | `aside_check` OK ×2, `moved_check` OK ×4 | OK | pass |
| C5 | `tracked_and_equal YES` ×4 | YES for each | pass |

**C4, what now loads new code from this tree:**
- changed paths: A 13720, M 274, D 7;
- `nd-unfolding/*.sh` naming the tree: 200 at the old commit, 214 now; across `*.sh` and `*.py`, 576 now;
- `unbinned_unfolding/python/omnifold.py`: blob `5966663bfe88…`, unchanged;
- `2d-unfolding/unfold_2d_omnifold_unbinned.py`: `9b43a07ad9be…` to `1a0c4a99ddf0…`;
- `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`: absent, then `c586b706c90f…`.

**Cross-checked locally** against `ed3590ea2`, and all of these match the transcript:
- `git rev-list --count 32e403b84..ed3590ea2` is 3,768;
- `git diff --diff-filter=A/M/D` gives 13,720, 274 and 7;
- both 2D blobs, from `git ls-tree`.

## 3. What the run left behind, and one count not explained

**On pscratch:**
- the aside directory `/pscratch/sd/j/josephrb/oi74-ff-20261030`, with:
  - the first run's two live-state copies and their `SHA256SUMS`;
  - `untracked-at-added-paths/`, holding the four copies and their `SHA256SUMS`.

  It stays. On the director's word, it joins the pscratch retention list, which the director keeps.
- the fetch's objects. `refs/remotes/github/main` moved from `eac51ab2e` to `ed3590ea2`, plus 1 new branch and no new
  tags.

No job was launched, nothing was written to CFS, and no untracked file other than the four was touched.

**C3 fell by 5, but only four files became tracked. This is not explained; the post-check passes either way.** One
more untracked entry left `git status`'s `??` list across the merge. The transcript prints only counts, so which entry
it was is not known, and the director ruled out a connect to find out.

**Checked locally, without a connect.** One candidate cause: `status` collapses an untracked directory into one line,
so a file under a formerly untracked directory could move the count by a different amount. That does not hold for the
four. Both their directories were tracked at `32e403b84`: `docs/orchestration/` had 607 tracked files and
`nd-unfolding/tests/` had 101. So each of the four was its own `??` line, which accounts for exactly 4.

The fifth would need the cluster's untracked list, which no transcript prints. Neither the collapsed-directory cause
nor the grown `.gitignore` rules (61 lines added, 1 deleted, between `32e403b84` and `ed3590ea2`) is tested for it.
<!-- absence-ok: a scoping statement; the cluster's untracked paths were never printed by either run -->

## 4. OI-74

**OI-74 is retired, on the director's word that its terminal criterion is met.** The canonical checkout is on current
main, with no tracked changes. That is the reconciliation the 2026-10-30 measurement asked for. The authority chain:
- Joseph's decision
  [`DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md`](../../DECISION-20261030-joseph-oi74-second-run-and-pr-p6.md)
  (#558), item 1;
- the director's [`BINDING-2.md`](BINDING-2.md) (#563);
- this report.

**Dependency check.** Search: `git grep -n 'OI-74'` over the tree @ `ed3590ea2`, excluding `OPEN_ITEMS.md` and the
generated views. Every hit is one of these records or the history before them: the two 2026-10-30 RECORDs, the
decisions #544 and #558, and the files in this directory. Six older documents cite OI-74 for the August drift; none
of them waits on the row being open.

**The row's own 2026-08-17 text names two residuals.** Both were checked locally at `ed3590ea2`:
- *"the real residual is a MECHANISM"*: the tree will drift again, and *"the check that would notice is
  `verify_executing_copy_is_committed.py`, which has no caller"*. `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py:7`
  quotes this. That check now has callers. The launchers `sbatch_gate5_data_only_{target,train}_array.sh` and
  `sbatch_bootstrap_5d_gpu.sh` each run it (3 lines each, already at `32e403b84`). The row routes the mechanism to
  OI-64, not to itself.
- *"`p4_standard_manifest.json`'s current bytes are cited by no receipt and exist only on purgeable scratch"*.
  `nd-unfolding/active_universe_5d/standard/evidence/p4_standard_manifest.json` is tracked: it was added in
  `9428ca8df` (2026-07-18) and is blob `0aa93760` at both `32e403b84` and `ed3590ea2`. The tree had no tracked change
  to it before the run (P3), and has none after it (C2). So its bytes are in git, not only on scratch. Whether a
  receipt cites them was not checked.
<!-- absence-ok: scoping statement; the receipt citation of the manifest was not searched exhaustively -->
