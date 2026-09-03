# PROPOSAL 2026-09-03 — PET Gate-6 branch family: preservation performed, removal PROPOSED ONLY

**CITABLE FOR:** the measured branch topology in §2, the preservation and tested-recovery results in
§3–§4, the discovery routes in §5, the coverage-token finding in §6, the GAP-1 artifact verification
in §7, the ordered change set in §8, the manifest adjudications in §9, and the exact-ref deletion
proposal in §10.

**NOT CITABLE FOR:** any branch deletion (none performed, none authorized), any adoption, any PET
promotion, any equivalence or coverage result, any gate movement, any launch or resubmission
authority, any discharge, any count or gate change, any publication claim.

**State this record does NOT move.** Gate 6 remains `BLOCKED` under its five prohibitions. PET remains
**diagnostic and method-development only** (`DECISION-20260902` `R6`). `C_stat` remains
`EXISTS — UNVERIFIED, PAIRING DECLINED` — **neither verified nor paired here**. Gate 2 remains FAIL;
counts hold at CAND `1 of 7`, QUOTED `0 of 7`. No scalar-5D covariance is adopted. No `C_ML` exists.
`(cause 7, G)` stays permanently OPEN and ungraded; `Y` is not constructed. Cause-3 seed-scan
authority stays suspended. The `R5` stop is not used as submission authority.

## 1. Authority and inputs

| item | value |
|---|---|
| controlling decision | `docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` |
| decision sha256 | `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064` (re-measured) |
| operational snapshot (routing only, uncommitted) | `HANDOFF-20260902-operational-baseline-snapshot.md` |
| snapshot sha256 | `bc9867edba2c730b6beb9e0b5e2d82cc0d01a3295667804892585e4a860573b4` (re-measured) |
| base commit | `dae18f226a5c679e3a60ba7d875e3bfbf43f96ac` = `origin/main`, re-measured after `git fetch` |
| snapshot's anchor | `52cbda90` — **superseded**; `origin/main` had advanced |
| generated live state | `--check-freshness` = **STALE** (`Git 712de1b`, `HEAD dae18f22`). **NOT regenerated** — `OI-73` authored-input defect |
| governing rows read | `OI-130` (preservation/enumeration by class), `OI-182` (coverage-token semantics), `OI-136`, `OI-123`, `OI-126`, `OI-70`, `OI-73` |
| removal-family authorization | **NONE EXISTS.** This record is a proposal; §10 requires separate approval |

### 1.1 Provenance of the three branch-mining manifests, including an access gap

Only **one** of the three manifests existed as a durable artifact. The other two reported
`FILES CHANGED: none` and wrote nothing, so their manifests lived only in their session transcripts.
Both were recovered verbatim from the Codex rollouts before this work began; the recovery is recorded
because a manifest that exists only in a transcript is not a citable artifact, and the next session
will not find it by any repository route.

| manifest | target | durable location |
|---|---|---|
| 1 | `origin/codex/pet-gate6-strategy-20260825` (`0969e787`) | a Claude session scratchpad — **outside the repository, purgeable** |
| 2 | `origin/pet-gate6-strategy-20260825` (`a05baab1`) | **no file**; recovered from `.codex-school2` rollout `01a06513-e6d1` |
| 3 | `origin/codex/pet-gate6-gap1-full-inventory-20260830` (`310d7e63`) | **no file**; recovered from `.codex-school` rollout `01a06514-0706` |

**This is `OI-130`'s class, applied to audit output rather than to a quoted value.** Three audits were
performed and two left no repository trace. Their conclusions are reproduced in §9 so that this record,
which *is* tracked, carries them.

## 2. Measured branch topology — five refs, three tips, 37 commits, none on main

`git for-each-ref`, re-measured after `git fetch origin --tags`:

| ref | tip | ancestor of `origin/main`? |
|---|---|---|
| `refs/heads/pet-gate6-strategy-20260825` | `a05baab141e777d2c77290c3de2bf9844a11e178` | **no** |
| `refs/remotes/origin/pet-gate6-strategy-20260825` | `a05baab141e777d2c77290c3de2bf9844a11e178` | **no** |
| `refs/heads/codex/pet-gate6-gap1-full-inventory-20260830` | `310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed` | **no** |
| `refs/remotes/origin/codex/pet-gate6-gap1-full-inventory-20260830` | `310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed` | **no** |
| `refs/remotes/origin/codex/pet-gate6-strategy-20260825` | `0969e787c7773520bfb7076aa24b39ae08852c2e` | **no** |

Merge base with `main`: `e428a6456d1dbc4669933dd957051f87f8370008`. From it, `main` carries 288
commits, `a05baab1` 34, `310d7e63` 17, `0969e787` 14.

**`0969e787` is a strict ancestor of BOTH other tips** (`merge-base a05baab1 310d7e63` = `0969e787`),
so it is the 14-commit shared trunk and the two branch lines fork there. The union of unique commits
is **37** (`34 + 17 − 14`), verified directly by `rev-list --count a05baab1 310d7e63 --not e428a645`.

**Consequence, and it is why only two tags were cut:** tagging `a05baab1` and `310d7e63` reaches all 37
commits across all five refs. The third ref needs no tag of its own. Shared origins counted once, per
`AGENTS.md`.

`git cherry origin/main` marks every commit on every tip `+`: **nothing here is on `main` by any
route**, so the content safety of a deletion rests entirely on §3 and §4.

## 3. Preservation performed — two annotated tags, pushed

| tag | tag object | commit |
|---|---|---|
| `evidence/preserved-pet-gate6-strategy-20260825-a05baab1` | `76cf037ae911ba718ffbd37bd224de0d400b656d` | `a05baab141e777d2c77290c3de2bf9844a11e178` |
| `evidence/preserved-pet-gate6-gap1-20260830-310d7e63` | `eb0e8954412247b62a7182bbddc380f1324739e6` | `310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed` |

Both pushed to `origin` and confirmed **from the remote** with `git ls-remote --tags`, not from the
local ref cache. Each annotation carries the 40-hex tip, the refs it covers, the ancestry facts, the
"nothing here is live evidence" boundary, the `R6`/Gate-6 posture, and the §6 coverage warning.

**The family word is `preserved`, not `retired`, and the distinction is load-bearing.** Every existing
`evidence/retired-*` tag records a branch that *was* deleted. No branch has been deleted here and no
authorization exists, so `retired-` would have been a false claim baked into an immutable object.

## 4. Tested recovery, not asserted recovery — two independent cold tests

### 4.1 Fresh clone carrying no branch refs and no tags

`git clone --single-branch --branch main --no-tags` from `origin`. Measured in that clone **before**
any tag fetch: refs are `main` only, `git tag --list` is empty, and all three tips are **absent** —
`git cat-file -e` fails on each. That is the post-deletion world.

Then `git fetch origin tag <t1> tag <t2>` — **only the two tags, no branch refspec**:

- all three tips resolve, including `0969e787`, which has no tag of its own;
- `rev-list --count` returns **34** for `a05baab1` and **37** for the union — every commit recovered;
- **29 of 29** retained artifacts (§8 Track C set plus every file both manifests classed durable)
  extract **byte-identical** to the live branch refs. 0 mismatch, 0 absent.

### 4.2 The Perlmutter checkout — a different tree with a different remote name

Measured at `/pscratch/sd/j/josephrb/MINERvA-OmniFold` (path confirmed with `ls -d`):

- its remotes are `github` and `analysis-note`; **there is no `origin` there**;
- `remote.github.fetch` already carries `+refs/tags/evidence/*:refs/tags/evidence/*`;
- **before fetching, both tags were absent and both tips were unresolvable**
  (`fatal: could not get object info`) — pushing to `origin` did not make them discoverable there;
- after `git fetch github 'refs/tags/evidence/preserved-*:...'` (scoped to my two tags, to avoid
  disturbing a shared tree) all three tips resolve;
- the GAP-1 terminal receipt recovers at sha256
  `b7ee3e7ea3e9413feebaab7e18131af9d01c393592e02ba74f489688da378a34`, **identical in all three trees**
  (primary clone, cold clone, cluster);
- `for-each-ref --contains a05baab1` returns **only the tag** there — the CATALOG-mandated reachability
  test, which `git branch -a --contains` cannot perform because it cannot see tags;
- that checkout's `HEAD` was unchanged by the fetch (`32e403b8`, and its 726 pre-existing dirty entries
  are untouched). **`32e403b8` is an ancestor of `origin/main`: the cluster tree is behind.**

### 4.3 What recovery does NOT cover

**The GAP-1 backing products are not in any tag and cannot be.** Re-measured 2026-09-03: the product
root
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_ml_ensemble/gap1_full_inventory_3c4e63e5`
holds **56 files, 1,338,031,396 bytes** on **purgeable** pscratch (**16 T of 20 T used**). There is no
tape copy. A git tag preserves the receipt that *describes* them and nothing else. **This is exactly
`OI-130`'s class**, and it is the one part of this preservation that a scratch purge still defeats.

## 5. Discovery routes — and the measured fact that none existed

**Measured on `main` at `dae18f22`: no tracked file names `a05baab1`, `310d7e63`, `0969e787`,
`3c4e63e5` or `eceec13e` — zero files each.** The search was covering, not blind: the merge base
`e428a645` was used as a positive control and was found in 4 tracked files. So before this record
there was **no discovery route to 37 commits of Gate-6 provenance**, and a session would have had to
already know a sha to find any of it.

The surviving routes this commit creates:

1. **This record**, classified `LIVE` in `MANIFEST-overrides.tsv` and linked from `CATALOG.md`. Without
   an overrides row a new document defaults to `ARCHIVAL` (`generate_manifest.py:145`) and is invisible
   to the router, and `live_doc_indexed.py` stays silent because it checks declaration-versus-router
   consistency, never whether a declaration should have been made.
2. **The tag annotations**, which are immutable and carry the tips and the §6 warning.
3. `CATALOG.md` § *Anchored-but-unreachable commits*, which already documents the fetch mechanics.

**Name the remote; do not copy either name from a document.** It is `origin` in the local clone and
`github` on Perlmutter — this is a checkout property, and §4.2 measured both:

```bash
git remote -v                                                        # look first, then substitute
git fetch origin 'refs/tags/evidence/*:refs/tags/evidence/*'         # local clone
git fetch github 'refs/tags/evidence/*:refs/tags/evidence/*'         # Perlmutter
git show evidence/preserved-pet-gate6-gap1-20260830-310d7e63:docs/orchestration/state/gate6-full-inventory-result-57727774.json
git grep '<identifier>' evidence/preserved-pet-gate6-strategy-20260825-a05baab1 --
git for-each-ref --contains <sha>                                    # never `git branch -a --contains`
```

**The explicit tag refspec becomes mandatory only after deletion, which is why it must be recorded
now.** Git auto-follows a tag only when it is already downloading the object. While the five branches
exist, the tips arrive on an ordinary fetch and the tags come along. **The moment the branches are
deleted, the tips are reachable from `refs/tags/*` alone, and any checkout without the tag refspec can
never obtain them by ordinary fetch.** `CATALOG.md` records that this already happened once: six of ten
`evidence/*` tags were absent from the main checkout and `cat-file -t` failed on all six anchored
commits — "preservation had succeeded; discovery had not."

## 6. Verification that no quarantined PET result becomes canonical — ONE HARD BLOCK FOUND

This is the check the task required, and it did not come back clean.

**The GAP-1 terminal receipt must NOT be ported verbatim.** In
`docs/orchestration/state/gate6-full-inventory-result-57727774.json`, inside a block named
**`common_validation`**, at lines 98–99:

```
"truth_denominator_coverage_guarded": true,
"truth_denominator_coverage": 1.0,
```

Measured facts:

1. **Neither token is produced by any tracked code**, on the branch or on `main`. `git grep` over the
   branch tree finds `truth_denominator_coverage_guarded` in **the receipt and nowhere else**. The
   search was covering: the same sweep found `coverage_is_guarded` at
   `nd-unfolding/pet/extract_fullevent_fps.py:433`, so it was reading the tree.
2. **`assert_truth_denominator_coverage` returns no numeric coverage at all.** Its return
   (`extract_fullevent_fps.py:405-433`) is
   `{n_pass_truth, sum_w_pass_truth, coverage_basis, coverage_is_guarded, coverage_tol}`. **The `1.0`
   was manufactured by the flattening**, which also dropped `coverage_tol` and — the important one —
   `coverage_basis`, the string that says *"coverage == 1 by construction; no independent
   truth-denominator array exists in this dump to cross-check against"*. The honest disclaimer is the
   field that did not survive.
3. **`OI-182` does not cover these two keys.** It priced the defect for the **different** token
   `coverage_is_guarded`, and its two load-bearing findings — "nothing READS it" (writer plus one
   diagnostic summary) and the 23 digest pins — were measured on that string. Confirmed on `main`:
   `coverage_is_guarded` occurs in exactly the writer, one non-quotable diagnostic summary, and
   `OI-182`'s own row; **`truth_denominator_coverage_guarded` occurs nowhere on `main` at all.**
4. **Under `R6`, coverage is precisely the object that reopens PET** — "estimator-equivalence PLUS
   coverage, where coverage is a different object from verifying the construction." A receipt in `main`
   asserting a *measured-looking numeric* coverage of `1.0`, filed under `common_validation` beside
   genuinely measured quantities such as `maximum_observed_subsample_relative_deviation` and
   `truth_denominator_sum_w`, is the exact mechanism by which a quarantined PET result becomes
   canonical.

**A qualification note is not a sufficient remedy, and manifest 3's recommendation to port the receipt
"with an `OI-182` qualification" is declined on that ground.** `OI-182`'s own remedy is to emit the
assumption *as* an assumption, because a field named like a measurement whose value is fixed by
construction cannot disagree with anything. Here the number has **no producer at all**, so there is
nothing a caveat can qualify.

**In every other respect the receipt is well guarded**, and that is worth recording because it is what
makes the coverage block easy to miss: it carries all five prohibition keys verbatim, `C_ML: null`,
`publication_result: false`, `gate6_status: "BLOCKED"`, `authorization_exhausted: true`, and a
`non_authorizations` block with eight `false` entries.

**Surfaced, not applied:** `OI-182`'s scope should widen to these two tokens and to the flattening that
produced them. That row belongs to the PET/FPS extraction owner and **is not edited here**.

## 7. GAP-1 artifact verification — the five-digest gap is now closed

Manifest 3 verified 51 of 56 receipt-bound files and explicitly declined to rehash the five large
pushes (~1.3 GB). That gap is closed by reading every byte:

| population | result |
|---|---|
| product/validation artifacts bound by the receipt | **36 of 36** match — 0 mismatch, 0 missing |
| of which large (>1 MB) `GATE6_GAP1_FULL_PUSH.npz` | **5 of 5** match, 1,337,773,932 bytes rehashed |
| scheduler stdout/stderr slots | **20 of 20** present on disk |
| receipt total (`hash_inventory.total_files_hash_bound`) | 56 = 36 + 20 — reconciles exactly |
| files in the product root | 56, 1,338,002,724 bytes measured during the sweep |

**The 20 log slots carry only 16 distinct digest values**, because all five `cpu_array` stderr files are
byte-identical (`c0b89ac8…`), and all five on-disk files carry that digest — a consistent 5↔5 mapping.
A first pass keyed by digest instead of by slot reported "16 of 16" and would have been read as a
shortfall; the population on one side is *slots* and on the other *files*, and they are not the same
unit.

**What this does and does not establish.** It verifies that the receipt's artifact bindings match the
bytes on disk. It is **not** coverage, **not** estimator equivalence, **not** an independent
verification of `C_stat`, **not** a pairing, and **not** a promotion. Under `R6` it changes nothing
about PET's status, and it leaves §6 untouched: a receipt whose files all match their digests can still
contain a field with no producer.

## 8. The smallest ordered set of clean, current-main changes

**Track A — preservation. Delivered by this commit; nothing else here is time-critical.**

1. The two pushed evidence tags (§3), verified recoverable in three trees (§4).
2. This record, plus its `MANIFEST-overrides.tsv` `LIVE` row and its `CATALOG.md` links — the surviving
   discovery route (§5). Without these the tags are objects nothing points at.

**Track B — findings that need no PET decision and no compute. Surfaced with owners; not applied.**

3. `OI-182`'s scope widens to `truth_denominator_coverage_guarded` and the manufactured numeric
   `truth_denominator_coverage` (§6). Owner: the PET/FPS extraction owner.
4. The GAP-1 56-of-56 artifact verification (§7) is available as a measurement. It is **not** a ledger
   row and must not become one without its owner's act: recording it in `VALIDATION_LEDGER.md` is a
   `VL` allocation and a quotability decision, neither of which is assigned here.
5. `OI-130`'s class now has a second observed instance: two of three branch audits left no repository
   trace (§1.1). Owner: `OI-130`'s row.

**Track C — selective ports. NOT delivered; each needs an integration owner and structural repair
first.**

6. The deterministic CPU fixture set — the **only** item both surviving manifests independently class
   portable, and the only one that touches no PET result:
   `docs/orchestration/PET-V2-EQUIVALENCE-FIXTURE-CONTRACT-20260825.md`,
   `docs/orchestration/pet_v2_fixed_draw_equivalence_fixture.py`,
   `docs/orchestration/state/pet-v2-fixed-draw-equivalence-fixture-result-20260825.json`,
   `nd-unfolding/tests/test_pet_v2_fixed_draw_equivalence_fixture.py`.
   Preconditions before any port: inject archive locations rather than hardcoding `/pscratch`; do not
   reintroduce a hardcoded cluster root at `sys.path[0]` (`OI-136`); re-test on current `main`.
7. **Port nothing else.** In particular **never** `docs/orchestration/MANIFEST.tsv` or
   `docs/orchestration/verify_hash_bindings.py` — both advanced independently on `main`, and the branch
   copies would restore absent PET bindings while discarding later main-side changes. Not the GAP-1
   terminal receipt verbatim (§6). Not any retry wrapper, launcher, `sbatch_*`, proposal, or
   root-remap: they encode spent authority and historical absolute paths.

**Track D — redrafts. Specification work; not performed here.**

8. **The convergence-equivalence-versus-coverage distinction needs no port: it is already canonical.**
   `R6` states it directly, so manifest 3's "already landed, semantically" is adopted over manifest 2's
   "design worth redrafting" (§9).
9. Any fixed-draw or nonfinite-diagnostic specification is a **new predeclaration**, not a port. Old
   prose carries spent launch authority and pre-decision status language, and porting it would recreate
   exactly the ambiguity `R2` and `R4` were written to remove: `R2` authorizes specification only and
   `R4` suspends cause-3 scan authority pending both a Joseph-signed VOI note and a separate committed
   run authorization. Restating old authorization prose on `main` would put launchable-looking text
   next to a suspended authority.

**Track E — removal. Proposed only (§10). Requires separate approval.**

## 9. Where the three manifests disagreed, and how it is adjudicated

Preservation is unaffected by these — the tags keep everything either way. They matter only for porting.

| item | manifest 2 | manifest 3 | adjudication |
|---|---|---|---|
| `0c08d317` equivalence-vs-coverage | design worth redrafting | **already landed semantically** | **manifest 3.** `R6` makes it canonical; a redraft would duplicate a ruling |
| `45d55f13` core fixed-draw implementation | implementation worth porting | design only — *"do not port as executable code"* | **manifest 3.** It failed before measuring science on cross-checkout imports (`OI-136`); manifest 2's own §3 requires structural repair before behavior ports, so both converge on "not as-is" |
| `ed8244d3` ROOT shell-contract fix | implementation worth porting, adapt to guarded-run | execution residue | **unresolved, and left so.** Deliberately not adjudicated: the current `mnv_guarded_run.py` surface is another lane's interface and this record must not choose it |
| the three retry proposals | stale/conflicting (spent authority) | durable evidence | **both, on different questions.** They are durable *as provenance* and stale *as authority*. The tag preserves them; §8.7 forbids porting them |
| fixture result JSON | durable evidence | implementation | immaterial — same disposition either way |

Manifest 1 additionally recorded 21 of 21 enumerated digest bindings matching, 10 of 10 Leg-F receipt
tokens found on `main`, and a `sacct`-confirmed cost correction. Manifest 2 uniquely found the retry-3
proposal/validator schema mismatch (`changed_retries_authorized` written, `retry_authorized` checked)
and a concrete `KeyError: low` in `diagnose_gap3_nonfinite_energy.py`. Manifest 3 uniquely found the
GAP-1 lineage and the coverage-field conflict that §6 extends. **All three agree on the decisive
point: no commit on any tip is patch-equivalent to `main`, and no branch result is live evidence** —
none appears in `VALIDATION_LEDGER.md`, `RUNS.tsv`, the N-D run log or status, PET remediation status,
`OPEN_ITEMS.md` or `CLAIMS.md`.

## 10. Exact-ref deletion proposal — NOT EXECUTED, and mechanically blocked today

**No branch, local or remote, has been deleted. Nothing in §10 has been run.** It requires an exact
removal-family authorization naming these refs, which does not exist.

Were it approved, the exact and complete refspec set is:

```bash
# LOCAL (2 refs) -- blocked today, see the blockers below
git branch -D pet-gate6-strategy-20260825                        # a05baab141e777d2c77290c3de2bf9844a11e178
git branch -D codex/pet-gate6-gap1-full-inventory-20260830        # 310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed

# REMOTE (3 refs)
git push origin --delete pet-gate6-strategy-20260825                      # a05baab1...
git push origin --delete codex/pet-gate6-gap1-full-inventory-20260830      # 310d7e63...
git push origin --delete codex/pet-gate6-strategy-20260825                 # 0969e787c7773520bfb7076aa24b39ae08852c2e
```

Five refs, three distinct tips. **Verify each tip against this record before running any line**, and
re-measure `origin/main` first: a ref that has advanced since 2026-09-03T10:08Z is out of this
proposal's scope.

### 10.1 Blockers — two are mechanical, measured, not merely advisory

**B1. Two of the refs are checked out in live worktrees, and git refuses to delete them.**

| worktree | tip | branch |
|---|---|---|
| `/private/tmp/minerva-gap1-launch-rCenMq` | `310d7e63` | `refs/heads/codex/pet-gate6-gap1-full-inventory-20260830` |
| `/private/tmp/minerva-gap3-authorized-W8m3Bw` | `a05baab1` | `refs/heads/pet-gate6-strategy-20260825` |

Power-tested in both directions in a throwaway repository rather than asserted: deleting a branch that
no worktree holds returns **rc=0**; with the branch checked out in a worktree, `git branch -D` returns
**rc=1** with `error: Cannot delete branch 'X' checked out at '<path>'` and the branch survives;
after `git worktree remove`, deletion returns **rc=0**. So both local deletions are blocked until those
lanes release their trees. **Manifest 1 named the `a05baab1` lane as a live coordination constraint;
this is that constraint, measured, plus a second one it did not cover.**

Note the asymmetry: a local worktree does **not** block `git push origin --delete`. Deleting the remote
refs while those lanes hold the local branches would strand their upstreams and is the sequencing error
most likely to be made here.

**B2. Two detached audit worktrees from the Wave-1 audits are still present** —
`/private/tmp/minerva-wave1-pet-branch-target.JWnpvv` (`a05baab1`) and
`/private/tmp/mnv-wave1-gap1-audit.ZmZ8gn/wt` (`310d7e63`). Both are clean. They hold no branch ref and
so block nothing, but they belong to their own sessions and are **not removed here**; an audit worktree
removed by a third party is exactly the silent-edit hazard `AGENTS.md` warns about.

**B3. The GAP-1 backing products remain sole-copy on purgeable pscratch** (§4.3). Deletion does not
cause that, and preservation does not fix it. Anyone who wants those 1.34 GB durable must treat it as an
`OI-130` remediation with its own authorization; the `mnv-negweight-historical-20260821` tape step is
the working template.

**B4. `docs/orchestration/MANIFEST.tsv` regeneration is owed, is caused by THIS commit, and is not
performed here.** Attribution measured rather than assumed, because the three manifests' MANIFEST
finding is a *different* claim — theirs is that the **branch** copies conflict with newer `main`.

| tree | `generate_manifest.py --check` |
|---|---|
| base `dae18f22`, unmodified detached worktree | **rc=0, `OK`** — rows 708, LIVE 128, overrides 156 |
| this commit | **rc=1, `OUT OF DATE`** — rows 709, LIVE 129, overrides 157 |

So the red is **mine**, not pre-existing debt, and it is exactly one deterministic delta: the `LIVE`
document added in §5 plus its overrides row. Regenerating is the control-plane owner's act and is
withheld here only because reconciling generated files across concurrent lanes is that owner's job;
`generate_manifest.py --write` on this branch should produce precisely those three counter changes and
nothing else. **`LIVE-STATE.md` must not be regenerated at all** until `OI-73`'s authored-input defect
is resolved.

### 10.2 Recommendation

Approve preservation as done. **Do not approve deletion yet** — not because the evidence is at risk,
which §4 shows it is not, but because B1 makes two of the five refs undeletable today, and a partial
execution that removes the three remote refs while the local branches stay checked out is worse than
doing nothing: it destroys the remote backup of the exact objects two live lanes are still working on.
The correct sequence is B1 released, then all five refs in one authorized act, then re-verify §4.1 in a
fresh clone.
