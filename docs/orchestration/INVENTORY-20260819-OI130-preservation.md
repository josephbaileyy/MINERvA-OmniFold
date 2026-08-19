# INVENTORY 2026-08-19 — checkout preservation: what a cleanup of the worktree estate would destroy

**Lane D (verifier), read-only.** Produced before any cleanup, at the mediator's request, because a
cleanup pass is the moment today's evidence disappears — `BEN-306` (*a deletion can retroactively break
a receipt*) and `BEN-477` (which exists only because a deletion was refused) are both from today.

**REVISION 3, 2026-08-19.** Two changes, both driven by facts that arrived after revision 2 was
published. **(1) `ecee9ff1` is anchored** — the tag revision 2 routed was created and pushed, and this
lane re-verified it against the remote (§7C); §2's hazard is historical and §1's row now reads
`PRESERVED`. **(2) §5.2's dropped-member reading is WITHDRAWN** — the author of the 08-19 endpoint
disclosed that the read was a four-row *filter*, not an enumeration, so it never asked about the fifth
file and cannot be evidence that anything was lost.

**REVISION 2, 2026-08-19T14:06Z.** Observed at local `HEAD` `fc878396`, `origin/main` `9413a8cb`.
Revision 1 was written at `origin/main` `b6cdd44b`; **six of its verdicts are now wrong and two are
inverted.** Both the corrections and the mechanism that produced them are recorded below rather than
silently patched, because *the mechanism is the finding* and the same defect took three parties.

> ### THIS IS NOT `OI-130`, AND THE FILENAME KEEPS THE MISNOMER SO THE CORRECTION IS FINDABLE
>
> It was commissioned as *"`OI-130`'s preservation inventory"*. `OI-130` asks a different question:
> *"for every value quoted in `docs/analysis-note/`, establish whether its backing artifact is tracked,
> preserved off scratch, or neither"* (`docs/OPEN_ITEMS.md:155`). Its unit is a **quoted value** and its
> scope is the **analysis note**. **This document's unit is a checkout and its scope is the worktree
> estate.** Filing this against `OI-130` would let *"OI-130 has an inventory"* be true of one
> enumeration and false of the other — the `BEN-080`/`BEN-082` id shape. **`OI-130` remains
> unenumerated and this document does not touch it.**

**Nothing here was deleted, moved, unlocked or pruned.** This lane created no tag and no branch, removed
no worktree, ran no `gc`, and touched only this file. **Two writes it did make, declared because an
inventory that hides its own footprint is worthless:** `git fetch origin --tags`, which was *required*
to see the anchors at all (§0), and a rebase of its own `lane-d` branch onto `origin/main` so this
revision lands on top of the published copy instead of needing a second cherry-pick (§7C).

---

## 0. THE METHOD WAS THE DEFECT — revision 1's reachability test could not see the answer

Revision 1, a citation-repair lane, and the mediator's own report to Joseph **all three** concluded that
`8e48a811` and `c1b63820` were *"reachable from nothing"*. All three were wrong, and wrong the same way:

```
git branch -a --contains 8e48a811     ->   (nothing)        exit 0
git for-each-ref --contains 8e48a811  ->   refs/tags/evidence/ben-468-baseline-8e48a811   [tag]
                                           refs/tags/evidence/ben-482-aae49f2a            [tag]
```

**`git branch -a --contains` CANNOT SEE TAGS.** Both commits had been preserved by annotated tags at
2026-08-19T01:40 (lane E). They were invisible for a second, compounding reason: **a tag pointing at an
otherwise-unreachable commit is not fetched by default**, so a lane that had not run
`git fetch origin --tags` could not see the tag either. **Three independent readings agreeing is not
verification when all three run the same blind instrument** — the agreement measured the instrument.

### The covering test this revision uses, and it is the one to reuse

```
git for-each-ref --contains <sha> --format='%(refname) %(objecttype)'     # ALL namespaces at once
git tag --points-at <sha>                                                # direct anchors
git cat-file -t <sha>                                                    # does the object still exist
git reflog show <branch>                                                 # the invisible fourth namespace
```

`for-each-ref` with no path argument covers `refs/heads`, `refs/remotes` **and** `refs/tags` in one
command. Revision 1's §5 warned *"`--contains` proves reachability now"*; the sharper warning is
**`--contains` proves reachability only within the namespace you asked about, and `git branch` silently
narrows it to two of three.**

### Two axes, not one, because CITED / SUPERSEDED / UNKNOWN conflates them

| axis | question | what destroys it |
|---|---|---|
| **RECOVERABILITY** | do these bytes exist anywhere else? | removing the *only anchor* — an unpushed branch, an unreferenced detached HEAD, or untracked files |
| **CITATION** | is this path or sha named in a receipt, finding, ledger or gate? | nothing, directly — but an unresolvable cited sha is `BEN-306` |

A worktree is **a checkout, not content**. Removing one deletes no commit: the objects live in the
shared `.git`. **A tree can be CITED and fully recoverable, or UNCITED and irrecoverable. Only the
second is destroyed by a cleanup, and it is the one no citation sweep finds.**

### A THIRD instrument defect, found while re-doing the citation sweep

Revision 1 swept for sha **8**-character prefixes. **This repo cites at 7, 8 and 40.** An 8-char sweep
for `e477afb1` and `ea4a4f3d` returns **zero substantive hits**; the 7-char sweep finds
`FINDINGS.md:718` (`BEN-382`, citing `e477afb`) and `FINDINGS.md:415` (`BEN-225`, citing `ea4a4f3`).
**Revision 1 would have declared two cited commits uncited.** Sweep at 7 and confirm at 40; a
fixed-width sha grep is `inference-from-absence-needs-a-covering-search` in a new register.

---

## 1. REACHABILITY, RE-DONE WITH THE COVERING TEST — every sha, every namespace

`H` = local branch, `R` = remote-tracking, `T` = tag, `—` = nothing.

| sha | subject / role | H | R | T | anchor of record | verdict |
|---|---|---|---|---|---|---|
| `8e48a811` | BEN-468 baseline worktree HEAD | — | — | **yes** | `evidence/ben-468-baseline-8e48a811` **pushed** | **PRESERVED** |
| `c1b63820` | agy-review worktree HEAD | — | — | **yes** | `evidence/agy-review-wt-c1b63820` **pushed** | **PRESERVED** |
| `aae49f2a` | BEN-482 fix | — | — | **yes** | `evidence/ben-482-aae49f2a` **pushed** | **PRESERVED** |
| `e477afb1` | BEN-382 pre-rebase evidence | — | — | **yes** | `evidence/ben-382-e477afb1` **pushed** | **PRESERVED** |
| `ea4a4f3d` | BEN-225 pre-rebase evidence | — | — | **yes** | `evidence/ben-225-ea4a4f3d` **pushed** | **PRESERVED** |
| `22668401` | standing compute grant | — | — | **yes** | `evidence/standing-compute-grant-22668401` **pushed** | **PRESERVED** |
| `ecee9ff1` | gate-2 instrument tree | — | — | **yes** | `evidence/ben-454-anchor-comparator-ecee9ff1` **pushed** | **PRESERVED — was AT RISK, §2 / §7C** |
| `9e96f0a5` | lane-b remedy-(A) tip | — | — | — | reflog only (`@{4}`) | at risk, uncited — §2 |
| `66fb1ed1` | lane-b-oi126 HEAD **now** | yes | `origin/main`, `origin/lane-b-member-axis-wip` | — | pushed | **RECOVERABLE** |
| `bb16c270` | `audit/20260731-findings` tip | yes | — | — | **local branch only** | **UNPUSHED — §4** |
| `b65f9ff2` | `codex/gregor-pet2-omnifold` tip | yes | — | — | **local branch only** | **UNPUSHED — §4** |
| `dd9fd1bb` `e89fa56f` `fc878396` `c8d52ee8` `783d648a` `1af59bf4` `c763318c` `b6cdd44b` `a31bcdd4` | lane / former tips | yes | `origin/main` | — | pushed | **RECOVERABLE** |

**All six `evidence/*` tags are on `origin`** — verified against the remote, not the local tag store:

```
git ls-remote --tags origin        ->  6 tags, all present, all peeled to the expected commit
   evidence/agy-review-wt-c1b63820^{}          c1b63820ead96e10518e9401791c399b8d3c17ae
   evidence/ben-225-ea4a4f3d^{}                ea4a4f3d796689c9220c427ec0e93df51e8eb568
   evidence/ben-382-e477afb1^{}                e477afb1524db5da1e026c884f0a88087d179455
   evidence/ben-468-baseline-8e48a811^{}       8e48a8117453a55b95f96c83a9e1592098f878e5
   evidence/ben-482-aae49f2a^{}                aae49f2a24aa44583e1df13786a2811692c3884c
   evidence/standing-compute-grant-22668401^{} 22668401eb217eda66004586220c426f73841ce3
```

This is the load-bearing upgrade and revision 1 missed all of it: **those six commits are now durable
off this machine.** A local `git gc --prune=now`, a `rm -rf` of every worktree, or the loss of the whole
laptop no longer destroys any of them. *A local tag would not have been enough; the push is what makes
the verdict `PRESERVED` rather than `anchored`.*

### The tag-not-repoint decision is CORRECT and this inventory recommends nothing against it

`evidence/ben-382-*` and `evidence/ben-225-*` were **tagged rather than repointed** because each finding
is *about a rebase relocating a verified claim* — `BEN-382` (*a `Checks:` trailer survives onto a tree
the hook never saw*) and `BEN-225` (*`pull --rebase` falsified a claim inside the commit message
carrying it*). **The pre-rebase sha IS the evidence; repointing to the post-rebase commit would delete
the thing the row demonstrates.** Checked against every recommendation in this document: **no conflict.**
§7C's "anchor it with a tag" applies the same reasoning to `ecee9ff1`, and §4's "push the branch, then
the checkout is disposable" applies to *work in progress*, never to a sha whose historical position is
the claim.

---

## 2. `ecee9ff1` — A LIVE `BEN-306`, AND REVISION 1 ASSERTED THE OPPOSITE

> **RESOLVED 2026-08-19 — anchored on the pushed tag `evidence/ben-454-anchor-comparator-ecee9ff1`
> (§7C), re-verified on the remote by this lane.** The section is kept in full and in the present tense
> because **the measurement is the evidence for the tag and the mechanism is reusable**; the six
> commands below are the ones to re-run against the next cited sha, and deleting them would leave the
> tag looking arbitrary. Read it as *what was true before the anchor*, not as a live hazard.

Revision 1's headline correction read:

> ```
> for-each-ref --contains ecee9ff1   ->   origin/lane-b-member-axis-wip     (a PUSHED remote branch)
> ```
> *"Its dependency is a pushed commit, so no local worktree is required to reproduce it — the estate
> could be deleted entirely and gate 2 would still be reproducible from GitHub."*

**That was true when written and is false now.** `origin/lane-b-member-axis-wip` has moved from
`ecee9ff1` to `66fb1ed1`. Re-measured this turn:

```
git for-each-ref --contains ecee9ff1   ->   (no refs, any namespace)
git cat-file -t ecee9ff1               ->   commit          (object still exists)
git reflog show worktree-lane-b-oi126  ->   ecee9ff1  @{6}  (the only thing holding it)
```

This is revision 1's own §5 caution #2 firing on revision 1, inside fourteen hours. **A reachability
verdict is perishable; a tag is not.** That is the general lesson and it is why §7C's remedy is a tag
rather than a policy.

**`ecee9ff1` is cited by name in two files on `origin/main`, four times and one time:**

```
docs/orchestration/DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md:1900,1911,1912,2744
docs/orchestration/HANDOFF-20260819-lane-b-member-axis.md
```

and the citation is substantive, not a passing mention — `:1912` reads *"`array_equal` True across all
`114,361,636` elements"* against `_th2_content` **at `ecee9ff1`**.

### The content is safe; the sha is not. These are different questions and only one is urgent

The commit was **rebased**, not lost. Its post-rebase equivalent `f7ab02ff` (*"Buffer fast path
DELETED…"*) is on `origin/main`. The cited instrument is the same bytes:

```
git rev-parse ecee9ff1:nd-unfolding/mii_anchor_comparator.py    -> a7cb2d9bb6a61a8e7c6dc45e1eadd4a34f2faf1c
git rev-parse f7ab02ff:nd-unfolding/mii_anchor_comparator.py    -> a7cb2d9bb6a61a8e7c6dc45e1eadd4a34f2faf1c   IDENTICAL
git rev-parse origin/main:nd-unfolding/mii_anchor_comparator.py -> 452ec4650fb69fe10f4ed1521ae2b997eafdf735   DIFFERENT
```

So: **blob `a7cb2d9b` is reachable from `origin/main` via `f7ab02ff` and can never be collected** — the
gate-2 measurement is reproducible forever. **What breaks is the citation's resolvability**: a reader
who runs `git show ecee9ff1:...` after the reflog expires gets *"not a valid object name"*, and the
determination's four citations become unverifiable. **That is exactly `BEN-306`, and note the trap: the
tree at `origin/main` HEAD is a *different* blob, so a reader who resolves the citation by path instead
of by sha silently reads the wrong file and gets no error.**

**The clock.** `gc.pruneExpire` and `gc.reflogExpireUnreachable` are both **unset** in this repo
(`git config --get` exits 1 for each), so the defaults apply: prune at `2.weeks.ago` for objects in no
reflog, and **reflog entries for unreachable commits expire at 30 days**. `ecee9ff1` is in a reflog, so
its nominal horizon is ~2026-09-18 — *unless* somebody runs `git gc --prune=now`,
`git reflog expire --expire-unreachable=now`, or deletes the now-merged `worktree-lane-b-oi126` branch,
**any of which collects it immediately.** A cleanup pass is precisely the event that does one of those.

**`9e96f0a5`** is in the same reflog-only state, is content-recoverable at `5afb7947` on `origin/main`,
and is **cited by nothing except this document** (7- and 8-char sweeps over `origin/main`, zero external
hits). It needs no anchor.

---

## 3. THE ESTATE HAS ALREADY BEEN CLEANED ONCE, WHICH IS THE ARGUMENT FOR DOING THIS NOW

Revision 1 recorded **ten** local worktrees. `git worktree list --porcelain` now returns **nine**. The
set difference — printed, not counted, per `BEN-468`:

```
GONE:   /Users/josephbailey/.claude-school/jobs/39b50e51/tmp/agy-review-wt   (c1b63820)
        ls -d  ->  No such file or directory;  absent from `git worktree list`
ADDED:  (none)
```

Revision 1 classified it *"genuinely disposable, cited nowhere — confirmed rather than assumed"*, and
that verdict holds: the 7- and 8-char sweeps over `origin/main` still find `c1b63820` in **no file but
this one**. **But the commit survives only because lane E tagged and pushed it forty minutes before the
directory vanished.** Nobody coordinated that. **The estate is being tidied by processes that do not
read this inventory, so "we will decide before anyone deletes anything" is already false.**

### Current local estate — nine worktrees

| tree | HEAD | branch | anchor | recoverable? |
|---|---|---|---|---|
| `MINERvA-OmniFold` (shared) | `9413a8cb` | `main` | pushed | yes |
| `.claude/worktrees/lane-b` | `e89fa56f` | `lane-b` | on `origin/main` | yes |
| `.claude/worktrees/lane-c` | `783d648a` | `lane-c` | `origin/lane-c` | yes |
| `.claude/worktrees/lane-d` | `fc878396` | `lane-d` | on `origin/main` | yes |
| `.claude/worktrees/lane-b-oi126` | `66fb1ed1` | `worktree-lane-b-oi126` | on `origin/main` | **yes — CHANGED, see below** |
| `.claude/worktrees/lane-e-causes-3-4` | `9413a8cb` | `worktree-lane-e-causes-3-4` | = `origin/main` | yes |
| `MINERvA-OmniFold-docs-control-plane` | `dd9fd1bb` | `codex/docs-control-plane` | on `origin/main` | yes |
| `MINERvA-OmniFold-gregor-pet2` | `b65f9ff2` | `codex/gregor-pet2-omnifold` | **local branch only, 29 ahead** | commits yes¹, untracked no |
| `jobs/40ec3d41/tmp/baseline-wt` | `8e48a811` | detached | **`evidence/ben-468-…`, pushed** | **yes — CHANGED** |

¹ *a local branch ref protects the commits from `gc`; it does not protect them from losing this machine.*

**`lane-b-oi126` is no longer irrecoverable.** Revision 1 had it at `9e96f0a5`, *"LOCAL ONLY, 35 ahead of
main, CITED + IRRECOVERABLE"*, and made it the estate's second-sharpest risk. Its branch has since been
rebased and merged: `66fb1ed1` is an ancestor of `origin/main`. **The tree is now an ordinary
disposable checkout** — except that it is `locked handoff 20260817-1133Z: keep locked across restart`,
so the lock is a *coordination* claim, not a preservation one, and only its owner should clear it.

**Third consecutive revision in which a recorded tip was stale on arrival** (`lane-b-oi126` twice,
`lane-e-causes-3-4` twice, `main` twice). **Recording a live tree's tip is not useful and this revision
stops treating it as a preservation fact.** The durable record is a tag; the tip is a timestamp.

---

## 4. THE TWO GENUINELY UNPUSHED BRANCHES

```
codex/gregor-pet2-omnifold   b65f9ff2   29 commits ahead of origin/main   no remote, no tag
audit/20260731-findings      bb16c270    2 commits ahead of origin/main   no remote, no tag   (no worktree)
```

Both are **safe from `gc`** — a local branch is a ref — and **unsafe from disk loss**, which is a
different risk that no cleanup triggers and no cleanup fixes. Neither sha is cited anywhere on
`origin/main` except in this document.

- `audit/20260731-findings` has **no worktree at all**, so no cleanup of the *estate* can touch it. It is
  out of scope for a directory sweep and should not be conflated with one.
- `MINERvA-OmniFold-gregor-pet2`'s **untracked content is the exposure, not its commits** — revision 1
  measured 1,161 paths / 15.9 MB not present in `git ls-tree -r b65f9ff2`. **I could not re-measure it
  this turn** (see §6.1) and I am not asserting the number; the *class* is confirmed and the directory
  still exists. Its path is referenced by
  `FINDING-20260813-local-git-config-is-not-lane-local.md` and a `standard-p4-verifier` repair-7
  transcript, so the tree is named in the record even though its tip is not.

---

## 5. CLUSTER — **CITED, NOT VERIFIED.** Every fact in this section is a prior measurement

**`ssh -o BatchMode=yes -o ConnectTimeout=15 saul.nersc.gov` → exit 255, no output**, run this turn.
`maintenance_20260819` began 2026-08-19T13:00Z and reserves 5,248 nodes for seven days. **Nothing below
was measured by this lane and nothing below can be re-measured until the reservation lifts.** Each item
carries its source and observation time so a reader can tell what is stale.

| fact | value | source | observed |
|---|---|---|---|
| cluster `HEAD` | `52df3985`, 98 behind `main` | mediator, relayed | 2026-08-19 12:09–12:40Z |
| `git status --porcelain` entries | 727 | mediator, relayed | 2026-08-19 12:40Z |
| modified **tracked** files | 4, by name — §5.1 | mediator, relayed | 2026-08-19 12:40Z |
| prior cluster `HEAD` | `7ac36ac`, 725 entries, 4 tracked | `OI-74` (lane E, first-hand) | 2026-08-17T15:24 |
| blob-level disposition of the tracked set | `state/cluster-uncommitted-inventory-20260812.json` | lane C, first-hand | 2026-08-12T12:03:33Z |
| twelve `gate5-*-frozen-*` trees clean, all pinned shas on `origin/main` | ~80–89 MB each, ~1.0 GB | revision 1 | 2026-08-19 ~04Z |
| cluster remote is named **`github`**, not `origin` | `git@github.com:josephbaileyy/…` | revision 1 + `OI-74` | — |

**`gate6traj-reconcile-56847059` is out of scope by standing instruction and was not read.**

> **RECOVERABLE ≠ REMOVABLE NOW.** `gate5-data-only-frozen-377c713` is the code pin of array
> **`57266000`, which is queued and cannot start before 2026-08-26T06:00**. Deleting it does not break
> the *record*; it breaks the *job*. This is the one line in the document that must survive any summary.

### 5.1 The four modified tracked files — **NOT "unowned/UNKNOWN"**, and revision 1 mischaracterised them

Revision 1 called them *"UNKNOWN … that no lane claims"*. **They were blob-diffed and dispositioned
seven days ago.** `state/cluster-uncommitted-inventory-20260812.json` (schema
`cluster-tree-uncommitted-inventory-v1`, recorded by lane C, explicitly read-only) records each with a
base blob, a current blob, a numstat and a salvage verdict:

| path | current blob | verdict | salvage |
|---|---|---|---|
| `docs/orchestration/state/sessions.json` | `0f9b29dd` | `DIFFERS-AND-BLOB-UNIQUE-TO-CLUSTER` | `REVIEW` — control-plane state, likely superseded by later local writes |
| `nd-unfolding/…/evidence/p4_endpoint_evidence.json` | `1317a88d` | `DIFFERS-AND-BLOB-UNIQUE-TO-CLUSTER` | `REVIEW` — standard-P4 evidence, P4 is HELD (decision 7) |
| `nd-unfolding/…/evidence/p4_merged_audit.json` | `e0960212` | `DIFFERS-AND-BLOB-UNIQUE-TO-CLUSTER` | `REVIEW` — same |
| `nd-unfolding/…/evidence/p4_standard_manifest.json` | `979329e7` | `DIFFERS-AND-BLOB-UNIQUE-TO-CLUSTER` | `REVIEW` — same |

`docs/OPEN_ITEMS.md:67` (`OI-74`) describes them by class — *"the four tracked ones are JSON evidence
and a session register, no source at all"* — and adds the specific live residue:
*"`p4_standard_manifest.json`'s current bytes are cited by no receipt and exist only on purgeable
scratch (backing it up to scratch is not preservation)."*

**So the genuinely open part is narrow and should be stated as such: they are identified, classified and
`REVIEW`-flagged; what is missing is that no receipt records them as PRESERVED.** That is a
one-command gap, not an unknown.

**Verified from this side, which is the part that was assertable without the cluster:** none of the five
unique blobs exists in the local object store —

```
git cat-file -t 0f9b29dd… b13b51d0… 1317a88d… e0960212… 979329e7…
   ->  fatal: git cat-file: could not get object info      (all five, exit 128)
```

A *positive* test, not an absence: the objects are genuinely not here. Revision 1's claim that these are
**the only bytes in the estate that exist in exactly one place** survives, and is now measured rather
than inferred.

### 5.2 A FIFTH unique-blob file was in the 08-12 set and is NOT in today's four — print the set

`BEN-468`: the before/after here is a containment claim, so the sets go in full, not the counts.

```
08-12 modified-tracked set (8):
  2d-unfolding/compare_to_models.py                      IDENTICAL-TO-CANONICAL
  2d-unfolding/model_comp_report.txt                     IDENTICAL-TO-CANONICAL
  nd-unfolding/adopt_unified_5d.py                       IDENTICAL-TO-CANONICAL
  docs/orchestration/state/sessions.json                 DIFFERS-AND-BLOB-UNIQUE
  docs/orchestration/state/waker/BLOCKED-ON-USER.json    DIFFERS-AND-BLOB-UNIQUE
  nd-unfolding/…/p4_endpoint_evidence.json               DIFFERS-AND-BLOB-UNIQUE
  nd-unfolding/…/p4_merged_audit.json                    DIFFERS-AND-BLOB-UNIQUE
  nd-unfolding/…/p4_standard_manifest.json               DIFFERS-AND-BLOB-UNIQUE

08-19 12:40Z modified-tracked set (4):  sessions.json, p4_endpoint_evidence.json,
                                        p4_merged_audit.json, p4_standard_manifest.json

DROPPED (4):  compare_to_models.py, model_comp_report.txt, adopt_unified_5d.py  — all IDENTICAL-TO-CANONICAL, no loss
              docs/orchestration/state/waker/BLOCKED-ON-USER.json               — DIFFERS-AND-BLOB-UNIQUE
ADDED   (0):  none
```

**THE SET DIFFERENCE ABOVE IS NOT A MEASUREMENT OF LOSS, AND SAYING SO IS THE WHOLE POINT OF THIS
SUBSECTION.** Revision 2 published it with the dropped member flagged and the caveat that the 08-19
endpoint was relayed. **The author of that endpoint has since disclosed what the command actually was,
and it settles the caveat in the direction that voids the inference:**

> the 12:40Z read filtered for modified tracked files with `grep -E '^( M|M |MM|AM)'` and returned
> exactly four; **it did NOT enumerate the 08-12 set and then diff.**

**So the four are what the filter was built to find, not an enumeration that the fifth failed to
survive.** `BLOCKED-ON-USER.json` sits under `docs/orchestration/state/waker/`, and nothing in a
four-row filtered result reports on it either way. **Do not read the four as evidence that the other
four are gone** — this document previously leaned toward *"the waker cron overwrote it, so those bytes
are already lost"*, and that reading is **withdrawn**: it was an inference from an absence produced by a
filter that never asked the question.

What survives is the shape of the risk, not an instance of it: `b13b51d0` was uniquely-valued on the
cluster on 2026-08-12, is dispositioned `REVIEW`, and **is not in the local object store** (tested
above). Its current status is **UNKNOWN and unmeasurable until the maintenance lifts.**

**The general rule, which is why the row stays:** a shrinking modified-tracked *count* reads as progress
and is equally consistent with silent loss, **and a filtered result cannot distinguish either from "I
did not look."** Resolve with `git cat-file -t b13b51d0` on the cluster, plus a full re-enumeration of
the modified-tracked set to diff against the 08-12 eight — **not** by re-counting and not by re-running
the same filter. The mediator has carried both onto the cluster-return list.

### 5.3 Unverified cluster-side loose end — `OI-135` step (e)

An aborted `generate_live_state.py` regeneration by the mediator **may** have registered a worktree
`/pscratch/sd/j/josephrb/live-state-regen-e8c857f3` in the **cluster** checkout's `.git`. The `ssh`
session died before producing output, so it probably never executed. **Unverified in both directions**
and unverifiable until the maintenance lifts. Recorded as `OI-135` step (e). **A stale
`.git/worktrees/` entry is harmless to preserve and is removed by `git worktree prune`** — which is a
cleanup this document does not authorise and which must not be run blind, because the same command
would unregister any *live* cluster worktree whose directory is temporarily unmounted.

---

## 6. WHAT THIS METHOD STILL CANNOT SEE

1. **I could not run `git status` in any tree but my own.** This session is worktree-isolated. So the
   dirty/untracked state of eight local worktrees is **not measured in this revision at all** —
   revision 1's filesystem-vs-`ls-tree` diff is not repeated and its numbers (notably 11,982 paths /
   440.4 MB in the shared checkout, and 1,161 / 15.9 MB in `gregor-pet2`) are **carried as prior
   readings, not re-verified.** They were an upper bound on *existence* and a poor guide to *value*:
   they include ignored build output and `.claude/` scratch. **One command from anyone who can run it in
   that tree settles it:** `git status --porcelain --ignored`.
2. **The citation sweep is `git grep` over `origin/main` at 7- and 8-char sha prefixes plus paths.** It
   cannot see a citation by **definite description** — *"the baseline tree"*, *"the frozen extraction"*
   — which is the common form, and it does not cover archived findings outside `origin/main`.
   **Absence from this sweep is evidence about the sweep.**
3. **The 22 non-frozen cluster worktrees are UNENUMERATED, not safe.**
   `annealed-nominal-recon.yL86x8`, `ben106-reconcile-56695424`, `branchc-*`, `gate5-rereview.*` and the
   rest were never opened, in revision 1 or here.
4. **HPSS and CFS are out of scope entirely.** Local machine and `/pscratch` only.
5. **Reachability is still perishable.** §2 is the proof. Every `RECOVERABLE` verdict above is true at
   `origin/main` `9413a8cb` and nothing re-checks it. **The only verdicts in this document that do not
   decay are the six `PRESERVED` rows, because a pushed tag is not a moving target.**

---

## 7. WHAT MAY SAFELY BE CLEANED ONCE JOSEPH AUTHORISES IT

**I am not cleaning anything and nothing below has been done.** Two categories, and the distinction is
the point: **"safe because recoverable" is a measurement and it is mine to assert. "Safe because
unwanted" is a judgement about value and it is not mine to make** — no row below is offered on that
ground, and where a tree is recoverable but somebody may still want it, the caveat column says so and
routes it rather than deciding.

### 7A. SAFE BECAUSE RECOVERABLE — asserted, with the evidence

Removing any of these destroys **no commit and no cited artifact**. Each row's anchor is named.

| may be removed | why it is safe (recoverability only) | caveat — not a safety claim |
|---|---|---|
| `.claude/worktrees/lane-b`, `lane-c`, `lane-d` | HEADs `e89fa56f`, `783d648a`, `fc878396` are all on `origin/main` | these lanes are **live**; whether they are wanted is their owners' call |
| `.claude/worktrees/lane-b-oi126` | `66fb1ed1` is on `origin/main` — **changed since revision 1** | **locked** `handoff 20260817-1133Z`; only its owner should clear the lock |
| `.claude/worktrees/lane-e-causes-3-4` | `9413a8cb` **is** `origin/main` | lane E is live |
| `MINERvA-OmniFold-docs-control-plane` | `dd9fd1bb` is on `origin/main` | — |
| `jobs/40ec3d41/tmp/baseline-wt` | `8e48a811` is on **pushed** `evidence/ben-468-baseline-8e48a811` | its 7 untracked paths are unmeasured (§6.1) |
| the 12 `gate5-*-frozen-*` cluster trees | all pinned shas on `origin/main`; eleven of twelve porcelain-0 | **EXCEPT `gate5-data-only-frozen-377c713`** — see 7B |

### 7B. NOT SAFE — do not clean, and each has a named reason

| do NOT remove | reason |
|---|---|
| `gate5-data-only-frozen-377c713` | code pin of queued array `57266000`; removal breaks the **job**, not the record |
| `MINERvA-OmniFold-gregor-pet2` | 29 unpushed commits, and ~15.9 MB untracked that is in exactly one place |
| the cluster's 4 modified tracked files | unique blobs, none in the local object store (§5.1) |
| `log_test.txt` (main checkout, untracked) | **DECIDED DELIBERATELY** — see below |
| the 22 non-frozen cluster worktrees | unenumerated, therefore unclassified (§6.3) |
| `main`, and anything under `.git/` | — |

**`log_test.txt` MUST NOT BE SWEPT, and the decision already exists so nobody need re-litigate it.**
`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md:8328` records: *"`log_test.txt` — DECIDED DELIBERATELY: left in
place, and the hazard raised against it does not apply."* The hazard was that
`generate_manifest.py` walks the filesystem and would inventory it; the walk is rooted at
`ORCHESTRATION = REPO/docs/orchestration` (`:24`, `:83`) and **the file is at the repo root**, so it
cannot be reached — confirmed by that entry's 0-dropped / 7-added set difference, in which it does not
appear. It is present (335 bytes, mtime 2026-08-14). **Not this lane's file, and not deleted.**

### 7C. THE ONE ACTION THAT HAD TO PRECEDE ANY CLEANUP — **DONE, 2026-08-19, by the mediator**

```
evidence/ben-454-anchor-comparator-ecee9ff1   ->   ecee9ff10fa6a592641143fb850b137d38c8b1f2
```

**Verified on the remote by this lane, not accepted on report** — `git ls-remote --tags origin` returns
the tag and its peeled `^{}` at the exact commit, and after `git fetch origin --tags` the covering test
that returned nothing in revision 2's §2 now returns:

```
git for-each-ref --contains ecee9ff1   ->   refs/tags/evidence/ben-454-anchor-comparator-ecee9ff1  [tag]
```

**`ecee9ff1` is `PRESERVED`.** It is no longer reflog-only, no longer on a gc clock, and no longer the
estate's live `BEN-306`. It was **tagged, not repointed**, for the `BEN-382`/`BEN-225` reason (§1), and
the tag message carries the reachability measurement, the five citations with `:1912` named as the
substantive one, the tag-not-repoint rationale and the blob trap — **so the reasoning survives
independently of this document**, which is the right place for it.

**Consequence for §7A: it is unblocked on recoverability grounds.** Every commit named in 7A is now on a
pushed ref, so removing any of those checkouts destroys no commit and no cited artifact. **That is a
recoverability verdict and nothing more.** The caveat column still routes: the live lanes, the locked
`lane-b-oi126` handoff and `baseline-wt`'s unmeasured untracked paths are unchanged, and **no row in 7A
has become a recommendation to remove anything.** 7B is untouched.

**Still outstanding, none of it urgent and none of it blocking:** push `codex/gregor-pet2-omnifold` and
`audit/20260731-findings` (29 and 2 commits — safe from `gc`, exposed only to losing the machine), and
**write a receipt for the four cluster files** once the maintenance lifts.

> **A small irony worth recording rather than hiding.** Committing this revision meant rebasing `lane-d`
> onto `origin/main`, which made revision 2's own commit `c3c16682` unreachable — the exact mechanism
> §2 documents. It is harmless *here* because the mediator had already cherry-picked the content to
> `526feb64` on `origin/main`, so the citable object is pushed and this one was never cited. **That is
> the general rule the estate should run on: cite the pushed sha, and a rebase costs nothing.**

---

## 8. SUMMARY — the corrections, so the changes are auditable rather than merged away

| revision 1 said | now | why it changed |
|---|---|---|
| `8e48a811` reachable from nothing | **PRESERVED**, pushed tag | `git branch -a --contains` cannot see tags |
| `c1b63820` reachable from nothing, disposable | **PRESERVED**, pushed tag; **its worktree is already gone** | same, plus the estate was cleaned in the interval |
| `ecee9ff1` on a pushed remote branch, *"gate 2 reproducible from GitHub"* | rev 2: **reflog only — live `BEN-306`**; rev 3: **`PRESERVED`** on `evidence/ben-454-anchor-comparator-ecee9ff1` | the branch moved; content safe at `f7ab02ff`, the sha was not — then the mediator tagged and pushed it |
| `lane-b-oi126` `9e96f0a5`, LOCAL ONLY 35 ahead, CITED + IRRECOVERABLE | `66fb1ed1`, **on `origin/main`, recoverable** | branch rebased and merged |
| the 4 cluster files are *"unowned / UNKNOWN"* | **dispositioned `REVIEW` on 2026-08-12 with blob shas**; only the *preservation receipt* is missing | the 08-12 inventory and `OI-74` were not consulted |
| ten local worktrees | **nine** | `agy-review-wt` removed by another process |
| `e477afb1` / `ea4a4f3d` uncited (implied by an 8-char sweep) | **cited by `BEN-382` and `BEN-225`** at 7 chars | the sweep's width was narrower than the repo's citation style |

**REVISION 3, 2026-08-19 — THE RESIDUAL RISK IS DISCHARGED.** Revision 2 closed by saying the estate's
risk was one commit and the highest-value act was a single annotated tag. **The mediator created it and
pushed it, and this lane verified it on the remote rather than on report** (§7C):
`evidence/ben-454-anchor-comparator-ecee9ff1`.

**Seven shas are now preserved off this machine on pushed tags, and no cited commit in the local estate
is reachable only from a reflog.** What remains is not a preservation problem:

- two unpushed branches (`codex/gregor-pet2-omnifold` 29, `audit/20260731-findings` 2) — safe from `gc`,
  exposed only to losing the machine, cited nowhere;
- `gregor-pet2`'s untracked content, and the shared checkout's — **unmeasured, not unsafe** (§6.1);
- the cluster's modified tracked files — **identified and dispositioned; the missing thing is a
  receipt** (§5.1);
- `b13b51d0`'s status — **UNKNOWN, and revision 2's lean toward "already lost" is withdrawn** (§5.2);
- the 22 non-frozen cluster worktrees — **unenumerated, therefore unclassified** (§6.3).

**The one thing that must not be lost in the good news:** `gate5-data-only-frozen-377c713` is
recoverable *and* must not be removed, because it is array `57266000`'s code pin (§7B). Recoverability
was never the whole question, which is why this document has always had two axes.

**And the durable lesson is the method, not the estate.** Two independent ways to declare a cited commit
disposable — **a namespace the query cannot see** (tags, invisible to `branch --contains`) and **a
precision the query cannot match** (an 8-char sweep against a repo that cites at 7) — produce the same
false conclusion from different causes, **and neither is visible in the output.** Three parties hit the
first today and revision 1 hit the second. Routed for a `FINDINGS.md` row by its owning lane; **this
document does not file it.**
