# Retired-worktree archive — the load-bearing files, brought into git

On 2026-08-24 twelve cluster worktrees were removed. Their untracked content was archived to
`$HOME/retired-worktree-archive-20260824` on `/global/u2` by the lane that performed the
removals. That archive was **single-copy, and nothing enforced its retention** — no rule, hook,
quota reservation or immutability bit. This directory closes that gap for the files that
needed it.

## What was measured before choosing

All 30 archived files were classified by computing each one's git blob id (`git hash-object`)
and testing membership in the set of objects reachable from **pushed** refs — 19,964 objects
over 20 remote-tracking refs, validated in both directions first (a known-pushed blob present,
a fabricated sha absent).

| bucket | files | bytes |
|---|---|---|
| already recoverable from git | 8 | 52,508 |
| single-copy **and load-bearing** → committed here | 8 | 109,109 |
| single-copy, safe to lose | 14 | 821 |

The three sums reconcile to the archive's measured total of 162,438 bytes, which is the check
that nothing was double-counted or dropped.

**That table is a measurement of the archive AS IT STOOD when it was scoped on 2026-08-25, not a
description of it now** — stating this because an undated classification reads as present tense,
which is the defect `OI-139` is about and which this document would otherwise commit. As of
2026-08-25 the archive on `/global/u2` holds **3 files, 8,230 apparent bytes**: its own corrected
README, plus the only two files that are neither committed here nor provably redundant
(`repair.py`, md5 `ae7eb53dd3e0e3c82ca43a0f13d61f9b`; the `ben106` draft, md5
`cab014704fe74ba22cbd946ec6ebafda`). Everything else was deleted by the lane that owns it, after
each file was verified redundant. Nothing enforces the retention of those last two.

## The five committed here, and why each is irreplaceable

| path | bytes | md5 | why |
|---|---|---|---|
| `retired-worktree-archive-20260824/README.md` | 8347 | `0cbc679c5497e6bda30677ab132abf13` | The archive's own index: every tree's sha, recovery commands, tested-recovery results, md5s, three amendments. It is what makes the other 29 files interpretable, and it was itself single-copy. |
| `stamp-reconcile-56695424/uncommitted-tracked.diff` | 38422 | `1c8c7fe435a591bd851a69b792009070` | **Uncommitted tracked modifications — by definition these cannot be in git.** The only non-empty one of the seven archived trees; the other six diffs are 0 bytes. |
| `gate5-data-only-frozen-abbf7e0/logs/log_fe_nominal_nominal.txt` | 671 | `64df6c17daabb3b3469bd6cd0b34f6c5` | Forensic run log. All three archived `log_fe_nominal_nominal.txt` files have **distinct** md5s, so this is not a duplicate of the others. This is the `abbf7e0` arm that `state/live-state.json` cites in the run-3/run-4 diagnosis. |
| `gate6traj-reconcile-56847059/logs/log_fe_nominal_nominal.txt` | 671 | `8d6f4bd6203a0e357be4f35c8863cfde` | Same class, distinct content. |
| `gate6-reconcile-56834281/agent-B-p5b/20260813T082207Z-send-f98547f3.json` | 836 | `56899cfc4def8c8d3880a19aee12dacd` | `agent-B-p5b` is cited by at least three **tracked** documents (`AUDIT-FINDINGS-20260729-B.md`, `LIVE-STATE.md`, `MIGRATION-TAKEOVER-STATUS.md`) while having **zero** tracked files under `runs/`. Tracked prose cited a referent that survived only in this archive. Its original repo-relative path inside that worktree was `docs/orchestration/runs/agent-B-p5b/20260813T082207Z-send-f98547f3.json`; it is filed here under the tree it was recovered from, per the `runs/<tree-name>/` convention. |

Every md5 above was verified against the archived source at copy time.

## Path convention, and its honest strength

Follows `docs/orchestration/runs/clausec-rerun-20260821/` — measured to be the **only** one of
the twelve worktrees removed on 2026-08-24 whose artifacts had been preserved this way (35
tracked files). **n=1: a precedent, not established practice.** `gate5-data-only-frozen-377c713`
was the second instance; these are the third through seventh.

## THE ADMISSION TEST — apply this, not a judgement

A file from a removed worktree is committed here **if and only if its blob hash is absent from
the set of objects reachable from pushed `main`.**

    git hash-object <file>          # then test membership in:
    git rev-list --objects --remotes | awk '{print $1}' | sort -u

Validate that set in **both** directions before trusting it — a known-pushed blob must be
present and a fabricated sha must be absent — because an unvalidated membership test answers
"not in git" for everything. Two lanes ran it independently and agreed on every verdict while
measuring different populations (19,964 objects over all remote-tracking refs; 19,563 over
`refs/remotes/github/main` alone), which is the useful kind of agreement: same conclusions from
different denominators.

**This test exists to stop `runs/` becoming a dumping ground.** The risk of preserving anything
at all is that undecided files accumulate and a later reader cannot distinguish
*preserved-because-irreplaceable* from *preserved-because-nobody-chose*. Withholding files does
not prevent that — it leaves the same ambiguity on a filesystem where nothing enforces anything.
Stating the test does: the next candidate is admitted or refused by a measurement rather than by
whoever happens to be holding it. Credit for that framing to the branch-cleanup lane.

**Size is explicitly not a criterion.** A standard that preserved a 54 KB working-tree diff
because its bytes were in no commit, and discarded a 2 KB repair script on the identical finding,
would be a standard about size. Both were admitted.

**Passing the test is not the same as being citable.** `stamp-reconcile-56695424/`'s superseded
draft passes it and is marked **NOT CITABLE** in that directory's `PROVENANCE.md`, with the
authoritative file named. Admission preserves bytes; it confers no standing.

## CORRECTION 2026-08-25 — one file moved from (a) to (b), and it was nearly deleted

The counts above are the **corrected** ones. As first filed they read 9 / 5 / 16, because this
lane classified `gate5-rereview.hywFA5/untracked/gate5_diff.txt` (54,463 B) as regenerable via
`git diff 02a2091 c39ac60`. **That recipe was wrong and produces 1,724 bytes — 3.2% of the
file.**

Cause: `02a2091..c39ac60` is the `index` line of the **first of seven** file-diffs inside a
multi-file diff (`p4-sweep-snapshots.json`, `build_fullevent_replica_target.py`, three
`sbatch_gate5_replica_*.sh`, `train_fullevent_replica.py`, `test_gate5_replica_driver.py`), and
six of the seven "before" sides are `0000000` — new files. **An index line names two blobs; it
does not describe the artifact containing it.** Reading one as a provenance recipe is the same
error as reading a field named `armed_watch` as a live state.

The branch-cleanup lane caught it before deleting anything, and it is the reason the content
survives at all — it now survives HERE, in git, and the archive's copy was subsequently and
correctly deleted as redundant once this commit made it so. Verified here independently, and no route regenerates it: `git show 56d35afb` is
8,890 B, `git diff 56d35afb^ 56d35afb` is 8,707 B, and a `-U3`→`-U25` context sweep on
`670e62df` spans 51,669–53,474 B / 1,146–1,209 lines, never reaching 54,463 B / 1,195 lines —
and the archived file uses *shorter* 7-hex index lines, so it genuinely contains more content.
Most likely a **working-tree** diff, which by definition is in no commit. It is therefore
sole-copy and load-bearing, and is committed at
`docs/orchestration/runs/gate5-rereview.hywFA5/gate5_diff.txt`, md5
`31d2f070aba56cbd3385ddf001c5f7da`, verified against the live archive copy.

Its sibling `gate5-review.atToYF/untracked/gate5_diff.txt` (51,841 B) **is** genuinely
regenerable and was deleted: it is `git show 670e62df` output, 1,152 lines against 1,152, with
all 14 differing lines being index-abbreviation width (7-hex vs 8-hex — seven index lines × two
hashes × one character = 14 bytes). Regenerating it today yields 8-hex where the archive had
7-hex; that is a `core.abbrev` difference, **not corruption**.

## What is NOT here, deliberately

**AMENDED 2026-08-25 — both of the files described below were subsequently COMMITTED**, under
Joseph's authorization and with the branch-cleanup lane's agreement, once the admission test above
was applied to them consistently: both blobs are absent from pushed `main`, exactly as the
rereview diff's was. They are at `runs/gate5-review.atToYF/repair.py` and
`runs/stamp-reconcile-56695424/ben106-stamp-verify-complete-56695424.SUPERSEDED-DRAFT-NOT-CITABLE.json`.
The paragraph below is kept as the reasoning that was current when this file was first written,
and it is why the counts above changed from 8/6/16 to 8/8/14. The two files were:

- `gate5-review.atToYF/untracked/repair.py` (2030) — a spent one-shot patch script. Its *effect*
  is in the tracked target (`coherent_bootstrap_factors` is present in
  `nd-unfolding/pet/train_fullevent_replica.py` on pushed main), but the script itself is in no
  commit.
- `stamp-reconcile-56695424/untracked/docs/orchestration/state/ben106-stamp-verify-complete-56695424.json`
  (3669) — an **earlier draft** of a tracked file: archived at `00:39:00Z` with different key
  names, tracked final at `00:43:07Z`, both carrying the same `event_sha256`.

Calling these "safe to lose" is a judgement, not a measurement — which is exactly the
distinction the rest of this note is built on, so it is stated rather than buried.

## Authorization

Joseph, 2026-08-25, relayed via the interpreter session: *"commit the 5 files in bucket (b)
using the runs/<tree-name>/ pattern, same as 377c713."* This `PROVENANCE.md` is one file beyond
that instruction and is disclosed as such; the precedent directory has no counterpart, but five
files spread over five directories do not explain themselves.
