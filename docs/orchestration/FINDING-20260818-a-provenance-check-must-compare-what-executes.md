# A provenance check must compare what EXECUTES against what is CITED — and the unit is the callee, not the file

**Lane B, 2026-08-18. `BEN-483`.** My error, twice, in opposite directions, from one instrument. The
remedy is the mediator's.

---

## THE ONE PARAGRAPH

I certified a gated run by comparing the **frozen worktree** against **`origin/main`**. Execution
followed **neither**: `sbatch_bootstrap_5d_gpu.sh:22` hardcodes
`REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold` and `:24` does `cd "${REPO}/nd-unfolding"`, so the
Python that runs comes from the canonical **working tree** — which was **180 commits behind**
`origin/main`. *"Is the frozen copy the same as main?"* and *"is the copy that RUNS the same as the
copy I CITED?"* are different questions, and **only the second is about this hazard.** Then, correcting
for it, a file-level `md5` said **DIFFERENT** where the executed *function* was byte-identical. **Same
instrument, opposite error, both from comparing files rather than the code that runs.**

---

## 1. What would have happened

Nine GPU tasks, three offsets, and every product missing its identity stamp:

    grep -c 'est_seed_offset'  canonical  nd-unfolding/bootstrap_nd.py   ->  0
    grep -c 'est_seed_offset'  frozen     laneb-c1-.../bootstrap_nd.py   ->  2

`validate_replica` would have returned `INCOMPARABLE` on all nine — **correctly** — and all three pairs
would have exited 2. Nine GPU tasks to learn that a checkout was stale.

**It was caught only because I shipped the claim as a PRECONDITION rather than as a verified fact.** The
byte-identity claim beside it was wrong; the instruction to run
`git merge-base --is-ancestor 214acdbb HEAD` on the canonical tree was right, and it returned
`CANONICAL-NOT-OK`.

**The defect defeated the check for itself.** I verified the frozen tree against the remote; the hazard
is that execution follows a *third* tree. A check aimed at the wrong pair cannot detect that the pair is
wrong.

## 2. The second error, in the other direction

After the fast-forward, `seed_offset_policy.py` **differed** between canonical and frozen by 191 lines —
and `bootstrap_nd.py:14` imports it. File-level, that reads as fatal.

It was not, and **the mediator resolved it at the right granularity rather than accepting the file-level
answer**: `bootstrap_nd.py` uses exactly one thing from that module, `declared_offset()` at `:48`, and
**that function is byte-identical across both trees** (`md5 9265d3e230d2be73f5116aba0f975556`). The 191
lines were pure additions this leg never calls.

| direction | what the file-level check said | what was true |
|---|---|---|
| before the ff | **IDENTICAL** (frozen vs `origin/main`) | the executing tree was 180 commits behind |
| after the ff | **DIFFERENT** (frozen vs canonical) | the executed *function* was identical |

**THE RIGHT UNIT IS THE CALLEE, NOT THE FILE.** And the fix is not *"compare more files"* — a whole-file
comparison is simultaneously too coarse (it cannot tell you which tree executes) and too fine (it
reports differences in code nothing calls).

## 3. Why this is not just "the hardcoded `REPO`" finding again

The hardcoded-`REPO` exposure (279 tracked `.sh` carry the literal; 85/20 as previously measured) is the
**mechanism**. This row is about the **check**: I had already documented the mechanism, predicted it
would arrive as a live precondition, and *still* wrote a verification that could not see it — because I
compared the artifacts I had in hand rather than the ones the run would open.

**The launcher itself half-solves this and says so.** `:33-34` sources `lib_member_resume.sh` from
`_HERE` precisely so a frozen deployment gets its own frozen library, with a comment recording that the
cluster probe failed 16/16 when it did not. **The three pre-existing `${REPO}` sources above it were
left deliberately** — a repo-wide migration, not a patch. So the file contains both the fix and the
unfixed instances, three lines apart, and I read the fix and inferred the file was safe.

## 4. The remedy, and what it is not

**Write the precondition as a command the other party runs on the tree that executes.** Not *"I verified
X"* but *"run this and tell me what it says."* That is what saved this, and it is cheap:

    git -C <the tree the launcher cds to> merge-base --is-ancestor <required sha> HEAD

**And when a file-level difference appears, resolve it at the callee.** Enumerate what the entry point
actually imports and calls, and compare those symbols. A file-level `md5` is evidence about a file; a
run depends on symbols.

**What this is NOT:** a case for migrating 279 launchers inside a gated run. I declined that and the
mediator agreed. The migration is a separate piece of work with its own blast radius, and the
precondition form makes every gated run safe *without* it.

## 5. What it composes with

- **`BEN-482` §7** — *the union of two files cannot express a requirement, because a requirement is
  about what SHOULD be there.* This is its sibling: **a comparison of two files cannot express a
  dependency, because a dependency is about what gets CALLED.** Both are *"the domain of the check is
  not the domain of the claim."*
- **`my-recurring-failure-is-asymmetric-comparison`** — name both sides before believing a delta. Here I
  named one side (`origin/main`) that was not party to the run at all.
- **`a-claim-about-code-is-dated`** — and this adds a second axis to it: a claim about code is dated
  *and located*. `bootstrap_nd.py` was simultaneously stamped and unstamped, in two trees, at one
  instant.

## 6. What this does not establish

- **I have not audited whether earlier products were built from the stale tree.** The staleness lasted
  until 2026-08-18 and every `${REPO}`-rooted launcher run before then executed 180-commit-old Python
  while lanes verified against `origin/main`. The four probe runs are clean by construction (commands
  stubbed; library sourced relatively) and Gate-5 runs from `gate5-data-only-frozen-52df398`. **The rest
  is unsurveyed and I am recording that as an open question, not a claim.**
- The 279/85/20 counts are from an earlier measurement, not re-derived here.
- The canonical tree was **stale, not divergent** — 0 ahead, ancestor of `origin/main`, working tree
  clean on the file in question. A divergent tree would be a different and worse problem.
