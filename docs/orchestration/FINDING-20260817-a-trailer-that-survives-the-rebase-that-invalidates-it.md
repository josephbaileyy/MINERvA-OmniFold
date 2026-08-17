# FINDING — the `Checks:` trailer survives a rebase that changes the tree it attests

**Lane E, 2026-08-17.** `BEN-382`. Found while pushing unrelated work, within an hour of the trailer's
deployment at `4dfeccd`. **No code changed by this finding; remedies are routed to the trailer's author.**

---

## The measurement

```
e477afb   committed via `git commit`   -> hook ran, printed "pre-commit: 9 checks passed",
                                          commit-msg appended  Checks: 9 passed
origin/main had moved (24690b9), so:  git rebase origin/main
                                       -> CONFLICT in docs/orchestration/CATALOG.md, resolved by hand
75fc88d   produced by `git rebase --continue`
          git diff --stat e477afb 75fc88d   ->  docs/orchestration/CATALOG.md | 2 +-
          git log -1 --format='%(trailers:key=Checks)' 75fc88d   ->  Checks: 9 passed
```

**No hook output was printed during the rebase, and none of the nine checks ran.** Git invokes
`pre-commit` and `commit-msg` on `git commit`; rebase replays commits through an internal path that does
not. The trailer is carried in the **commit message**, which rebase preserves verbatim, so it arrives on
the new commit as though it had been earned there.

**The tree is genuinely different.** This was not a clean fast-forward replay — the rebase hit a real
conflict and I resolved it by hand. So `75fc88d` carries an attestation computed against a tree that
`75fc88d` does not have.

## Why this is worse than the absence case the trailer was built for

`4dfeccd`'s own rationale is that **a hook which never ran leaves a durable absence** rather than a
missing terminal line — the `BEN-370` failure, where the only symptom was that a line did not print.

**This is the inverse, and it is the more damaging direction.** A durable **presence** asserts a check
that did not run:

* `BEN-084` — an artifact asserting the wrong thing beats no artifact for damage.
* `BEN-112` — *a print is not a check*, now in its most durable form, because a commit trailer is
  permanent, auditable, and therefore **trusted more than a terminal line ever was.**

The trailer's value proposition is that a reader auditing history can distinguish checked from unchecked
commits. **Under rebase that distinction is not sound**, and an auditor has no way to tell from the
commit alone.

## The exposure is the ordinary path, not an edge case

This repo's standing instruction is *"rebase BEFORE measuring anything you will quote, or re-measure
after"*, and `origin/main` moves constantly with five or more concurrent lanes. **`commit → rebase →
push` is therefore the normal route to `main`, not an unusual one.** Every commit that takes it carries a
trailer it did not earn.

**The conflict case is the dangerous one.** A hand-resolved conflict is precisely when the committed tree
diverges most from the tree the hook saw — and it is also when a lane is most likely to have introduced
something a check would catch.

## No harm in this instance, verified rather than assumed

```
bash .githooks/pre-commit          (run directly against the rebased tree)
  -> pre-commit: 9 checks passed
  -> HOOK EXIT=0
```

**So the trailer on `75fc88d` is TRUE. It was simply not EARNED by that commit object.** That distinction
is the whole finding: **truth by luck is not evidence.** Had my conflict resolution broken an index entry
or a hash binding, the trailer would have said `9 passed` just as confidently.

## Remedies — routed, not applied

The lane that finds a hole in a shared mechanism is not automatically the one who should redesign it —
`BEN-370`'s own closing rule, and the same separation applied in `BEN-381`.

1. **Verify at PUSH time rather than commit time.** The pre-push tree is final and is the only point that
   rebase, `--amend`, cherry-pick and squash cannot bypass. This is the structural fix.
2. **Failing that, bind the trailer to a tree sha** — `Checks: 9 passed tree=<sha>` — so a reader can
   check in one command whether the attestation applies to the commit it sits on. An unbindable trailer
   is `BEN-380`'s definite description in a third notation.
3. **`git rebase --exec` is a partial fix and relies on remembering**, which is the class the dispatcher
   header itself names as *"the convention-that-requires-remembering problem"*.

## The class, which is why this is filed rather than messaged

This lane filed three findings on 2026-08-17 and they are one defect in four notations:

| notation | how it decays | id |
|---|---|---|
| a definite description (*"the adopted product"*) | silently re-points when a second object satisfies it | `BEN-380` |
| a section cross-reference (`CRITERIA §4.8`) | dangles when sections are renumbered — and never existed | `BEN-381` |
| a `file:line` allow-list | goes red on an added comment | `BEN-381` |
| a commit trailer with no tree binding | survives onto a tree it never described | `BEN-382` |

**EVIDENCE MUST BE BOUND TO WHAT IT IS EVIDENCE ABOUT.** Each of these is an attestation whose subject
can move out from under it without the attestation changing, and in every case the failure is silent and
in the reassuring direction. Bind by content, by name, or by digest — never by position.
