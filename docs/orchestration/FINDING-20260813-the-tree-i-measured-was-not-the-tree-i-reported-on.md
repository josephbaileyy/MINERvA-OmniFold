# FINDING 2026-08-13 — the tree I measured was not the tree I reported on

**BEN-183, BEN-184.** Lane D (verifier). The first is against myself; the second came out of chasing it.
The design review these belong to is `VERDICTS-20260811-session-D.md` §V50.

## 1. A measurement whose scope went unstated (BEN-183)

I ran `verify_hash_bindings.py`, got two `MISMATCH` lines and `*** BINDINGS BROKEN ***`, and made them
the decisive evidence in a design review — the sentence the verdict was framed on was *"day one, the
hook prints `5 checks passed` while the gate prints `*** BINDINGS BROKEN ***`."*

**I ran it in `.claude/worktrees/lane-d`, at a commit that predated both repairs.** Verified after the
fact:

```
6637d63 (what I pushed) parents: dd27cee cfe3422
  5ad5ac7  (A's Gate-4 retirement, 18:59)  ancestor of dd27cee?  NO
  466ab0d  (C's BEN-157 R2, 19:53)         ancestor of dd27cee?  NO
```

So I measured, then merged `origin/main`, then pushed — and **the commit I shipped contains the repairs
the measurement I reported did not.** On `main`: `ALL BINDINGS INTACT`, exit 0, and
`test_hash_bindings.py` 6/6. Both breaks had been closed by two lanes independently, hours before I
looked.

**Why it is worth a row rather than a shrug.** This is the class the whole day's auditing was about,
turned on the auditor: `BEN-174` (a summary more confident than its source), `BEN-179` (a correction
applied to the paragraph rather than the claim), and in the *same message* as this error, a disclosed
slip where `git log -1 -- <path>` misled me about which commit staged a file. **This is that slip one
level out.** Not the wrong command against the right object — the right command against the wrong
object.

The tell was available and free: `git log --oneline -1` at the top of the same command block. I ran
`git status --porcelain` for cleanliness and never asked *which commit is this clean at.*

> **Check:** put the ref in the sentence that carries the number. Not "the gate reports X" but "the gate
> reports X at `<sha>`." A lane worktree, a stale fetch, and `main` are three different repositories
> that answer to the same commands, and a verdict built on a measurement inherits that measurement's
> scope **silently** — nothing in the output says which tree produced it.

**A second prediction failed on test, and in the other party's favour.** Chasing the correction, I
expected the day's two retirements to instantiate `OI-65`'s divergence, since A used `status:
SUPERSEDED` *and* the field rename while C used the field rename alone. Measured: C's receipt has **no
`files` key**, so the `"files" not in payload` clause retires it under the status-side predicate too.
**Both predicates agree; A's measured-zero survives.** Recorded because a corrected auditor looking for
a replacement finding is exactly the moment to state a failed prediction rather than quietly drop it.

## 2. The floor that covers one half (BEN-184)

Looking for what the clean tree *did* leave open produced the round's most useful result.

```python
failed = bool(new_bad) or blind or (a.strict and bool(known_bad))
blind  = shell_resolved < SHELL_PIN_FLOOR        # SHELL_PIN_FLOOR = 15
```

`blind` protects the **shell-pin** half, and the source is emphatic about why: *"Do NOT lower the floor
to make this pass — an unwalked pin is how the Gate-2 pair went stale."* The module's header tells the
whole story of how that floor was earned.

**The receipt half has no floor.** `ok` can fall to any value, zero included, and while `new_bad` is
empty the gate prints `ALL BINDINGS INTACT` and exits 0.

**And the correct repair convention is what erodes it.** Retiring a superseded receipt means renaming
`sha256` → `sha256_at_issue` — which is exactly what removes it from `collect()`'s harvest. A's
conversion did this impeccably: digest multiset asserted identical across 30 values, 17 digests on
removed lines and the same 17 on added lines, no digest edited, and the launch-code floor checked before
converting. **Every retirement is right, and coverage falls with no signal.** The repair path and the
erosion path are the same path.

Its sibling already solved this. `test_hash_bindings` carries `_LAUNCH_CODE_FLOOR` with the comment
*"a discoverer that matches nothing reports success."*

> **Check:** when a gate has two collectors, ask whether both are floored. **Third instance today** —
> `BEN-173` (a `_verified_` field with a positive control, its twin without), `BEN-180` (a band tested
> above 1 and never below), and now a floored shell collector beside an unfloored receipt collector.
> The asymmetry is never in the half someone was thinking about.

**Consequence for the hook decision:** if this gate becomes the hook's guarantee, the receipt half needs
a floor **before** it is installed. A green that erodes one legitimate retirement at a time is the
failure mode the hook is being added to prevent.
