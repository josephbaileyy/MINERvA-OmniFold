# DETERMINATION — step 1 of the `CODE_ROOT` sync: it is SAFE, it is not a merge, and the 08-12 fork no longer exists

**Lane E, 2026-08-17.** Step 1 of the mediator's dispatch: establish, before any write, whether the
four modified tracked files on `/pscratch/sd/j/josephrb/MINERvA-OmniFold` make a sync unsafe.

**READ-ONLY. Nothing written to the cluster. No `sbatch`, `scancel` or `scontrol`. The write itself
is NOT done and is held for Joseph** — my authorization for it comes from a peer, and a `git` write to
a checkout five lanes and running jobs read is outward-facing and not cheaply reversible. The mediator
is asking Joseph directly and explicitly declined to route it to a lane that would accept quorum
authorization.

---

## The headline, and it is not what the dispatch expected

> **There is no fork. `5fb7e38` is an ancestor of `origin/main` and ZERO commits are unique to the
> cluster. The operation is a FAST-FORWARD, not a merge.**

That matters because of what governs here. `cluster-local-fork-freeze-20260812.json`'s `purpose` field
carries **Joseph's decision of 2026-08-12, item 10**, quoted in
`OPEN_ITEMS-ARCHIVE-2026-08.md:1259-1264`:

> *"Do not reconcile or merge the 114-commit cluster fork during closeout. Freeze and record both
> heads plus the 22-pin comparison and the harness hash. Stop further divergence and use a clean
> canonical-based worktree for new cluster work after item 7. Inventory unique patches with
> range-diff after the publication freeze; no wholesale merge."*

**Read carelessly, that forbids this task.** I nearly reported it as a block on those grounds. It does
not, and the reason is measured rather than interpreted: **the decision is about the cluster's UNIQUE
COMMITS — the thing "inventory unique patches with range-diff" and "no wholesale merge" are about —
and there are none.**

```
git merge-base --is-ancestor 5fb7e38 origin/main   ->  true
git rev-list --count origin/main..5fb7e38          ->  0
```

The 114-commit (later 153-commit) fork was resolved by somebody between 08-12 and now. A
fast-forward does not merge anything; it advances a pointer, and it takes divergence to **zero**,
which is the direction *"stop further divergence"* asks for. **A future reader must not cite item 10
against a fast-forward without re-running those two commands** — the decision is live, and its subject
has ceased to exist.

---

## Step 1 proper: the four modified tracked files

Measured on the cluster this turn; `git status --porcelain --untracked-files=no` returns exactly four,
matching the mediator's count. **All four are LARGER than their committed versions and add far more
lines than they remove — they are accumulating artifacts, not stale copies:**

| path | `+/-` vs cluster HEAD | worktree bytes / HEAD bytes |
|---|---|---|
| `docs/orchestration/state/sessions.json` | +90 / −7 | 51 542 / 46 746 |
| `…/standard/evidence/p4_endpoint_evidence.json` | +60 / −30 | 5 661 / 3 053 |
| `…/standard/evidence/p4_merged_audit.json` | +20 / −10 | 7 706 / 7 236 |
| `…/standard/evidence/p4_standard_manifest.json` | +133 / −25 | 10 381 / 5 817 |

### A fast-forward cannot touch any of them, and this is a covered null

```
commits in range 5fb7e38..origin/main                          128    <- the control
  … touching nd-unfolding                                       18
  … touching docs/orchestration/state                           18
  … touching any of the four paths                               0
```

The range demonstrably *could* have hit them — 18 commits land in each of the two parent directories —
and none does. Git only checks out files an incoming commit changes, so the four survive untouched.

### And nothing else blocks the checkout either

78 paths are ADDED by the incoming commits. Cross-checked against the cluster filesystem: **0 collide
with an existing file**, so no untracked artifact (of the 721) blocks the checkout half-way.

**Conclusion for step 1: the sync is safe, and safe structurally — a fast-forward that touches none of
the modified files and collides with none of the untracked ones — rather than safe because I inspected
the diffs and judged them unimportant.**

---

## The real finding, which is INDEPENDENT of the sync and live right now

**`p4_standard_manifest.json`'s current cluster content is recorded NOWHERE.**

Cross-checking today's cluster digests against the only receipt that ever inventoried them:

| path | receipt's `cluster_sha256` (08-12) | measured today | verdict |
|---|---|---|---|
| `p4_endpoint_evidence.json` | `1317d0d3…` | `1317d0d3…` | **unchanged for five days; content is digest-cited by a committed receipt** |
| `p4_merged_audit.json` | `2e3fac26…` | `2e3fac26…` | **unchanged; digest-cited** |
| `p4_standard_manifest.json` | `67eb2177…` | **`71aace38…`** | **CHANGED — cited nowhere** |
| `sessions.json` | `e3206438…` | `0f5a81df…` | changed; a live session register, churns by design, not evidence |

A digest search over the whole repo returns **zero sites** for `71aace38…` and zero for `0f5a81df…`.
So the P4 standard manifest has drifted since the freeze inventory and **its current bytes exist only
on purgeable scratch, uncited by any receipt.** Scratch being purgeable, *"it is on the cluster"* is
not preservation.

**This is not a reason to block the sync — the sync does not endanger it. It is a reason to preserve
it whether or not the sync happens**, and preservation needs a decision I am not taking: committing
cluster-generated evidence into the repo is itself a write with provenance consequences, and HPSS is
over quota (`hpssquota`, not `hsi`).

**Also worth correcting rather than inheriting:** the freeze receipt recorded **12** tracked entries
with **5** `DIFFERS`; today **4** differ and 8 have converged, including
`sbatch_step1_trajectory_annealed.sh`, the only `.sh` in that list. **The receipt is a five-day-old
measurement and reads as current — `BEN-303`'s hazard, and the direction of its staleness is
favourable, which is the direction nobody re-checks.**

---

## What is NOT established

- **I have not verified the PET-guard claim myself.** The dispatch says the cluster's
  `inversion_screen.py` / `leg_mismatch.py` / `push_vs_acceptance.py` are pre-`OI-82`-fix and so do
  not refuse the arithmetic-slip value. That is consistent with the 128-commit gap and with those
  files being in it, but I measured the *gap*, not the *guards' behaviour on the executing copy*.
  Cheap to close and worth closing before the sync is sold as a correctness fix.
- **Whether a narrower code-only sync is preferable is moot** given the above: a fast-forward is
  cleaner than a partial checkout, it leaves the evidence files alone, and a partial sync would leave
  the tree at no commit at all — which is the `OI-64C` property (*"committed is not deployed"*) made
  permanent rather than fixed.
- **`56585597` not touched.** Identified by the mediator as the `wakerctl` cron watch, held with
  `user_env_retrieval_failed_requeued_held`, `restartCnt=1868`. Not ours to release; `scontrol` is
  prohibited; surfaced to Joseph.
