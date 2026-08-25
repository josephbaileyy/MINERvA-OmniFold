# Retired cluster worktrees — 2026-08-24

Registry went 14 rows -> 2 (`MINERvA-OmniFold` @ main, `MINERvA-OmniFold-fe` @ fe-fps-campaign).
Twelve scratch worktrees removed. No content was lost: every removed HEAD is an ancestor of
`refs/remotes/github/main`, except `cee4b356`, which was an ancestor of NOTHING and was tagged
first (`evidence/retired-branchc-reconcile-cee4b356`, pushed to origin; also fetched into the
local clone, so two copies exist off purgeable pscratch).

## Recreate any tree

    git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold worktree add --detach <path> <sha>

| tree | sha | untracked kept here |
|---|---|---|
| gate5-data-only-frozen-377c713 | 377c713d | log_fe_nominal_nominal.txt |
| gate5-data-only-frozen-abbf7e0 | abbf7e02 | log_fe_nominal_nominal.txt |
| gate6-reconcile-56834281 | 4d96acf0 | one agent-B-p5b send JSON |
| gate6traj-reconcile-56847059 | b82ac63f | log_fe_nominal_nominal.txt |
| gate5-rereview.hywFA5 | 56d35afb | gate5_diff.txt |
| gate5-review.atToYF | 670e62df | gate5_diff.txt, repair.py |
| stamp-reconcile-56695424 | f139964f | ben106-stamp-verify-complete JSON + 38KB tracked diff |

`branchc-reconcile-56691812` (cee4b356), `clausec-rerun-20260821` (00be534f),
`expiry-c-verify-20260821` (ab5710f2), `laneb-c1-30c4d766` (576b0cd5),
`laneb-s0-158f4a5a` (158f4a5a) were clean — nothing to archive.

## Tested recovery, not asserted recovery

`377c713d` was the frozen deploy tree, so it got a real recovery test rather than a claim:
`git archive 377c713d | tar -x` into a scratch dir, then `diff -rq` against the live directory.
Result: identical except two gitignored `__pycache__` dirs. The 2422-vs-2420 file count gap was
two SYMLINKS (mode 120000) that `find -type f` skips; counting files+symlinks gives 2422 = 2422
with empty set-difference both ways. Its receipt
`docs/orchestration/state/gate5-do-train-array-active-57266000.json` also carries the full sha
(`377c713d1790d96d15f7d115d9c903fd556c5943`), so the discovery route survives independently.

## LATENT DEFECT, deliberately NOT fixed here

Three launchers still `:-`-default their CODE_REPO to the now-absent `gate6-reconcile-56834281`:

- `nd-unfolding/pet/sbatch_gate6_member_trajectory_array.sh:28`   GATE6_CODE_REPO
- `nd-unfolding/pet/sbatch_pet_fullevent_floor_replicate_array.sh:53`  G6_FLOOR_CODE_REPO
- `nd-unfolding/pet/sbatch_pet_fullevent_legx_2x2_array.sh:78`    G6_LEGX_CODE_REPO

This is the defaulted-CODE_REPO shape OI-136 ruling 17 removed from the 5D launchers, never
propagated to the gate6 PET ones. Removal is safe anyway: all three hash-pin their code and die
`code hash mismatch`, so a missing tree fails CLOSED, and a different tree later created at the
same path is caught too, because identity is bound by content hash rather than by path.

DO NOT "fix" this by converting the three `:-` to `:?` alone. That BREAKS all three launchers:
`GATE5_CODE_ROOT` can be `:?` only because four `submit_gate5_*.sh` controllers export it via
`EXPORTS="ALL,...,GATE5_CODE_ROOT=$CODE_ROOT,..."`. The three gate6 vars have NO supplier —
each is mentioned in exactly one file, the launcher's own `:-` line. The conversion needs a
paired export, or it turns a caught-afterward default into a cannot-run-at-all.

## AMENDMENT 2026-08-24 — gate5-data-only-frozen-377c713 was RESTORED

It was removed, then restored on the same day at lane claude-school-main's request, which
cited a governing artifact neither lane had read:
`docs/orchestration/RULING-20260819-lanec-issue54-frozen-deployment.md` (247 lines, verified
present on pushed main). Its §6 "Specifically NOT authorised" list, line 209, includes **"any
deletion or top-level reorg"** — not limited to repo content, which is what my own reading
("removing a directory takes nothing out of main") had turned on. The ruling's line 213
"Forbids" clause is narrower and does NOT cover deletion-as-cleanup, so the ruling is not
violated either way; §6 is the binding part, together with CLAUDE.md's requirement of an
exact removal-family authorization, which nothing cited supplies.

Restored from its own sha, then verified: HEAD 377c713d, 2422 tracked entries on disk against
2422 in the tree, `status --porcelain` showing only the untracked witness log, and that log
md5 9ad538c385e98adfe74114ce305129e0 identical to the copy archived here. Byte-identical to
its pre-removal state.

It stays until Joseph or lane C (freeze-policy owner) gives one line. The archive copy under
this directory is retained regardless — it is the untracked witness, which is NOT in git.

Registry is therefore 3 rows, not 2: primary, MINERvA-OmniFold-fe, and this frozen tree.
The other three of that batch (abbf7e02, 4d96acf0, b82ac63f) stay removed: no governing
ruling, no live LIVE-STATE row, no watch named in a receipt.

## AMENDMENT 2 — "armed" struck, and the defect now has an OI id

CORRECTION, 2026-08-24. An earlier version of this file said the other three trees had "no
armed watch". Struck: nothing measured whether any watch was ARMED. What is citable is that
a watch is NAMED in 377c713's receipt as a field value, not a filename:

    docs/orchestration/state/gate5-do-train-array-active-57266000.json:66
        "supervision": { "armed_watch": "gate5-do-train-57266000-r3", ... }

Two further citations: `docs/orchestration/deploy_oi135_watcher_swap.sh:76` sets
WATCH_OLD to that id — i.e. OI-135 treats it as the watch being REPLACED — and
`docs/orchestration/test_deploy_oi135_watcher_swap.py` exercises it with state='disarmed'.
So the name is real; "armed" was read off the FIELD NAME rather than measured against the
waker, and does not survive. Note that :380 of that same test file is
`test_disarmed_predecessor_is_not_read_as_armed`, whose docstring begins '"disarmed"
CONTAINS "armed"' — this repo already carries a guard against precisely this misreading.

The correct predicate for the three removed trees is: not named in any receipt's supervision
block, no row in LIVE-STATE.md, and — the one that actually settles content safety —
ANCESTOR OF PUSHED MAIN, which reproduces from a fresh clone where a ref count does not.

THE LATENT DEFECT IS NOW **OI-138** (commit f0bd77e5, pushed, control_plane_lint PASS;
verified present, and OI-153 absent, so the renumber into the 120-139 block did happen).
Cite OI-138 rather than the three file:line coordinates above. The row leads with the
remedy being wrong rather than the defect, and says explicitly: do NOT convert the three
`:-` to `:?` without adding a supplier.

## AMENDMENT 3 — gate5-data-only-frozen-377c713 REMOVED under authorization

Removed 2026-08-25T03:16:21Z (observed window 03:16:21Z..03:16:22Z). Supersedes Amendment 1,
which recorded it as restored and held.

Authorization: Joseph, given directly to the cleanup lane in session, confirming the standing
authority of lane claude-school-main. The authorization record was committed BEFORE the act at
f0b7fed2 (pushed), on RULING-20260819's own instruction that "Authorization receipts are
committed before they are acted on, and this document is a ruling, not a receipt". That record
carries the recreate command, the sufficiency argument, and the reference-vs-reconstruction
distinction; the removal time is reported to that lane for the receipt's
removal_performed_at_utc field, which was deliberately left PENDING until the act occurred.

Verified at removal: witness log md5 9ad538c385e98adfe74114ce305129e0 identical between the
live tree and the archived copy under this directory; HEAD
377c713d1790d96d15f7d115d9c903fd556c5943; only the untracked witness outstanding.
Verified after: directory GONE, 377c713d still an ancestor of pushed main, the full 40-hex sha
resolves to a commit object, cluster registry down to 2 rows.

RECOVER WITH:
    git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold worktree add --detach \
        /pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713 \
        377c713d1790d96d15f7d115d9c903fd556c5943
    cp <this archive>/gate5-data-only-frozen-377c713/untracked/log_fe_nominal_nominal.txt <tree>/

The witness log is NOT in git — it is the only part of this tree that the sha cannot restore,
which is why this archive is retained rather than deleted alongside the tree. Restoring the
tree without it reproduces 2422 tracked entries and loses the forensic witness.
