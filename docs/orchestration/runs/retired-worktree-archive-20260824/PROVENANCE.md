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
| already recoverable from git | 9 | 106,971 |
| single-copy **and load-bearing** → committed here | 5 | 48,947 |
| single-copy, safe to lose | 16 | 6,520 |

The three sums reconcile to the archive's measured total of 162,438 bytes, which is the check
that nothing was double-counted or dropped.

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

## What is NOT here, deliberately

Two archived files are **superseded rather than redundant**, and are therefore neither committed
here nor safe to delete on a byte-identity argument:

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
