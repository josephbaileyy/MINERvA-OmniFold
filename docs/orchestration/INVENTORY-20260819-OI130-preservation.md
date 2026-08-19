# INVENTORY 2026-08-19 — checkout preservation: what a cleanup of the worktree estate would destroy

**Lane D (verifier), read-only.** Produced before any cleanup, at the mediator's request, because a
cleanup pass is the moment today's evidence disappears — `BEN-306` (*a deletion can retroactively break
a receipt*) and `BEN-477` (which exists only because a deletion was refused) are both from today.

> ### THIS IS NOT `OI-130`, AND THE FILENAME KEEPS THE MISNOMER SO THE CORRECTION IS FINDABLE
>
> It was commissioned as *"`OI-130`'s preservation inventory"*. I read the row before filing under it,
> and **`OI-130` asks a different question**: *"for every value quoted in `docs/analysis-note/`,
> establish whether its backing artifact is tracked, preserved off scratch, or neither — and report the
> count in each state"* (`docs/OPEN_ITEMS.md:155`). Its instance is `\gbdtAiEstTrace` and an untracked
> `uq_cov_ai1est_5d.root`; its unit is a **quoted value**, and its scope is the **analysis note**.
>
> **This document's unit is a checkout and its scope is the worktree estate.** The two share a theme —
> *what does a purge destroy* — and share no rows. **Filing this against `OI-130` would let
> *"OI-130 has an inventory"* be true of one enumeration and false of the other**, which is the
> `BEN-080`/`BEN-082` id shape and the reason `OI-129` is explicitly kept separate in `OI-130`'s own
> row. **`OI-130` remains unenumerated and this document does not touch it.**
>
> Nothing here needs an id to be useful; it needs to be read before a deletion. If it should get one,
> that is an owner's act, not mine.

**Nothing here was deleted, moved, unlocked or modified.** Every number is from a command run in this
turn. Local shas were read from `git worktree list --porcelain`, not from anyone's table — **and the
table I was given as a starting point disagrees with the porcelain in three places** (§1).

---

## 0. Method: TWO AXES, because CITED / SUPERSEDED / UNKNOWN conflates them

A worktree is **a checkout, not content**. Removing one deletes no commit: the objects live in the
shared `.git`. So *"is it cited"* is the wrong first question. The two that matter are:

| axis | question | what destroys it |
|---|---|---|
| **RECOVERABILITY** | do these bytes exist anywhere else? | removing the *only anchor* — an unpushed branch, an unreferenced detached HEAD, or untracked files |
| **CITATION** | is this path or sha named in a receipt, finding, ledger or gate? | nothing, directly — but an unresolvable cited sha is `BEN-306` |

**A tree can be CITED and fully recoverable** (re-adding the worktree at that sha reconstructs it
byte-identically) **or UNCITED and irrecoverable** (untracked scratch nobody names). **Only the second
is destroyed by a cleanup, and it is the one no citation sweep finds.**

---

## 1. THREE CORRECTIONS TO THE STARTING TABLE, one of which inverts its headline

Measured from `git worktree list --porcelain` this turn:

| tree | table said | porcelain says |
|---|---|---|
| `.claude/worktrees/lane-b-oi126` | `ecee9ff1` | **`9e96f0a5`** |
| `.claude/worktrees/lane-e-causes-3-4` | `377c713d` | **`1af59bf4`** (and `c763318c` eight minutes earlier) |
| the rest | — | agree |

**And the headline claim is misattributed.** I was told *"`lane-b-oi126` @ `ecee9ff1` is the tree you ran
gate 2 against; remove it and the gate-2 receipt refers to something that no longer exists."*

```
for-each-ref --contains ecee9ff1   ->   origin/lane-b-member-axis-wip     (a PUSHED remote branch)
for-each-ref --contains 9e96f0a5   ->   worktree-lane-b-oi126             (LOCAL ONLY, 35 ahead of main)
```

**I never opened `lane-b-oi126`.** Gate 2 ran against `origin/lane-b-member-axis-wip` @ `ecee9ff1`,
extracted with `git show` into `/tmp` on the cluster. **Its dependency is a pushed commit, so no local
worktree is required to reproduce it** — the estate could be deleted entirely and gate 2 would still be
reproducible from GitHub.

`lane-b-oi126` **is** worth preserving, for a reason unrelated to gate 2: its branch is unpushed. And
the remedy that follows is different — **push the branch**, then the checkout is disposable. Keeping a
*directory* to preserve a *commit* is the wrong instrument, and it fails the moment somebody tidies it.

`lane-e-causes-3-4` moving twice in eight minutes is its own caution: **a live tree's sha is not a
stable identifier**, so an inventory that pins one is stale on arrival. Pin the *branch*, not the tip.

---

## 2. LOCAL ESTATE — 10 worktrees

`R` = recoverable elsewhere. `NOT-IN-TREE` = files on disk absent from `git ls-tree -r <HEAD>`
(so: untracked **and** ignored — see §5 for why that overstates value and not existence).

| tree | HEAD | branch | anchor | R | NOT-IN-TREE | class |
|---|---|---|---|---|---|---|
| `MINERvA-OmniFold` (shared) | `b6cdd44b` | `main` | pushed | yes | **11,982 / 440.4 MB** | **UNKNOWN** |
| `.claude/worktrees/lane-d` | `a31bcdd4` | `lane-d` | pushed | yes | 17 / 0.0 MB | SUPERSEDED |
| `.claude/worktrees/lane-c` | `b6cdd44b` | `lane-c` | pushed | yes | 12 / 0.2 MB | SUPERSEDED |
| `.claude/worktrees/lane-b` | `e89fa56f` | `lane-b` | pushed | yes | 17 / 0.0 MB | SUPERSEDED |
| `.claude/worktrees/lane-e-causes-3-4` | `1af59bf4` | pushed branch | pushed | yes | 23 / 0.4 MB | **LIVE** |
| `MINERvA-OmniFold-docs-control-plane` | `dd9fd1bb` | `codex/docs-control-plane` | pushed | yes | 1 / 0.0 MB | SUPERSEDED |
| `.claude/worktrees/lane-b-oi126` | `9e96f0a5` | `worktree-lane-b-oi126` | **LOCAL ONLY, 35 ahead** | **no** | 40 / **5.0 MB** | **CITED + IRRECOVERABLE** |
| `MINERvA-OmniFold-gregor-pet2` | `b65f9ff2` | `codex/gregor-pet2-omnifold` | **LOCAL ONLY, 29 ahead** | **no** | 1,161 / **15.9 MB** | **IRRECOVERABLE** |
| `jobs/39b50e51/tmp/agy-review-wt` | `c1b63820` | detached | **NO REF AT ALL** | **no** | 1 / 0.0 MB | **IRRECOVERABLE, uncited** |
| `jobs/40ec3d41/tmp/baseline-wt` | `8e48a811` | detached | **NO REF AT ALL** | **no** | 7 / 0.2 MB | **CITED + IRRECOVERABLE** |

### The two detached HEADs are the sharpest destruction risk in the estate

`for-each-ref --contains` returns **zero refs** for both `c1b63820` and `8e48a811`. **The worktree is
the only thing keeping either commit alive**; remove it and the commit is unreachable and GC-able.

And `8e48a811` **is cited on `origin/main` in three files**, one of them a filed finding:

```
docs/orchestration/FINDING-20260819-cardinality-cannot-witness-containment.md   (BEN-468 long form)
docs/orchestration/FINDINGS.md
docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md
```

**That is `BEN-306` waiting to happen, and it fires on removing a directory nobody would hesitate
over** — a temp path under a *job* directory, named `baseline-wt`, in a tree that looks like scratch.
`agy-review-wt` is the same shape and **is cited nowhere** (0 files), so it is genuinely disposable —
confirmed rather than assumed, as asked.

### The remedy is three pushes, not a preservation policy

```
worktree-lane-b-oi126        9e96f0a5   35 commits ahead of main, on no remote
codex/gregor-pet2-omnifold   b65f9ff2   29 commits ahead of main, on no remote
audit/20260731-findings      bb16c270    2 commits ahead of main, on no remote
```
plus **tag or branch the two detached HEADs** (a `preserve/*` branch at `8e48a811`, likewise `c1b63820`
if wanted). **After five one-line commands, every commit in the estate is on a pushed ref and every
worktree becomes a disposable checkout.** That converts an open-ended preservation question into a
finished one, and it is strictly better than keeping directories, because a directory can be deleted by
someone who never read this file.

---

## 3. CLUSTER — 34 worktrees; the frozen trees are fully reconstructible

**All twelve frozen trees are CLEAN and all twelve pinned shas are on `origin/main`:**

```
gate5-data-only-frozen-{152306a,224779e,377c713,3efefa4,52df398,70824e2,742be22,abbf7e0,d0c42bd}
gate5-extraction-frozen-{7dc8c34,d0a07cf}   gate5-extraction-r2-frozen-2f65a36
porcelain 0 for eleven of twelve (abbf7e0 has 1);  ~80-89 MB each, ~1.0 GB total
```

So re-adding a worktree at that sha reconstructs any of them byte-identically. **SUPERSEDED on
recoverability** — but note the distinction that a recoverability verdict does *not* settle:

> **RECOVERABLE ≠ REMOVABLE NOW.** `gate5-data-only-frozen-377c713` is the code pin of **array
> `57266000`, which is queued and cannot start before 2026-08-26T06:00** (`maintenance_20260819`
> reserves 5,248 nodes for seven days). Deleting it does not break the *record*; it breaks the *job*.

Six of the twelve are named in `docs/orchestration/state/*.json` receipts; the citations resolve to
shas, not to paths, so they survive removal.

**`gate6traj-reconcile-56847059` is out of scope by standing instruction and was not read.**

### The cluster remote is named `github`, not `origin`

Confirmed: `github git@github.com:josephbaileyy/MINERvA-OmniFold.git`, plus an `analysis-note` remote.
Recorded because pushing to `origin` there fails, and it reportedly cost a freeze today.

---

## 4. THE FOUR UNOWNED MODIFIED TRACKED FILES — **UNKNOWN**, and the only ones with no other copy

Shared cluster checkout, 727 porcelain entries of which **exactly four are modified tracked files**:

```
 M docs/orchestration/state/sessions.json                                        +97
 M nd-unfolding/active_universe_5d/standard/evidence/p4_endpoint_evidence.json   +-90
 M nd-unfolding/active_universe_5d/standard/evidence/p4_merged_audit.json        +-30
 M nd-unfolding/active_universe_5d/standard/evidence/p4_standard_manifest.json  +-158
                                                       303 insertions(+), 72 deletions(-)
last commits: 2026-07-18 and 2026-07-29, both Joseph Bailey
```

**These are the only bytes in the entire estate that exist in exactly one place and are guaranteed to be
destroyed by an ordinary cleanup** — a checkout, a hard reset, or a fresh clone all discard them
silently and report success. Three-plus weeks of uncommitted drift, in files last committed by Joseph,
that no lane claims.

**Classified UNKNOWN and NOT touched**, as instructed. The action that costs nothing and settles it is a
stash object or a copy to a dated path **before** any cleanup — not a decision about whether they
matter, which nobody currently can make.

---

## 5. WHAT THIS METHOD CANNOT SEE

Stated because an inventory silent about its own reach is a control silent in `BEN-456`'s third
register — it executes, outside the case.

1. **I could not run `git status` in any tree but my own.** This session is worktree-isolated and
   redirecting git at another checkout is refused. So the **dirty/untracked state of nine local
   worktrees is measured indirectly**, by diffing the filesystem against `git ls-tree -r <HEAD>`. That
   count is an **upper bound on existence and a poor guide to value**: it includes ignored build output
   and `.claude/` scratch, which is most of the shared checkout's 11,982 / 440 MB. **I do not know how
   much of that 440 MB is unique.** Someone who can run `git status --porcelain --ignored` in that tree
   can settle it in one command; I could not.
2. **`--contains` proves reachability *now*.** A branch deleted between this inventory and the cleanup
   changes the answer, and nothing re-checks.
3. **The citation sweep is `git grep` over `origin/main` for paths and sha7 prefixes.** It cannot see a
   citation by *definite description* — *"the baseline tree"*, *"the frozen extraction"* — which is the
   common form. **Absence from this sweep is evidence about the sweep.**
4. **I did not enumerate untracked content in the 22 non-frozen cluster worktrees**, only the 12 frozen
   ones. `annealed-nominal-recon.yL86x8`, `ben106-reconcile-56695424`, `branchc-*`, `gate5-rereview.*`
   and the rest are **UNCLASSIFIED**, not safe.
5. **HPSS and CFS are out of scope entirely.** This is the local machine and `/pscratch` only.

---

## 6. SUMMARY

| bucket | members |
|---|---|
| **IRRECOVERABLE if removed** | `lane-b-oi126` (35 unpushed), `gregor-pet2` (29 unpushed, 15.9 MB untracked), `agy-review-wt` + `baseline-wt` (**no ref at all**), the 4 unowned modified files |
| **CITED** | `baseline-wt` `8e48a811` (3 files incl. `BEN-468`'s long form), `lane-b-oi126` (4 files incl. its handoff), 6 frozen trees (receipt-cited by **sha**, so removal-safe) |
| **SUPERSEDED** | 4 lane worktrees, `docs-control-plane`, 12 cluster frozen trees — all reconstructible from pushed shas |
| **LIVE — do not remove regardless** | `lane-e-causes-3-4`; `gate5-data-only-frozen-377c713` (array `57266000`, blocked until 2026-08-26) |
| **UNKNOWN** | the 4 unowned modified tracked files; 440 MB in the shared local checkout; 22 unenumerated cluster worktrees |

**The single highest-value action is not a preservation policy. It is five one-line commands** — push
three branches, anchor two detached HEADs — after which nine of the ten local worktrees and all twelve
frozen trees are disposable, and the residue is four uncommitted files that need an owner, not a rule.
