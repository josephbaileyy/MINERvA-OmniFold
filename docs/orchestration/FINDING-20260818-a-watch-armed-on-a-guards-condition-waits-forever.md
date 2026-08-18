# A watch armed on a guard's own condition can wait forever, and arming it that way felt like the rigorous choice

**Lane E, 2026-08-18. `BEN-472`.** Generation two of the `C_stat^data` family could not submit while a
generation-one array held the queue, because the submit controller refuses to interleave two families. So I
armed a background watch on **exactly the condition the guard tests**:

```bash
squeue -h -u josephrb -n g5dotarg,g5dotrain | wc -l   ->  0
```

and reported "still draining" for hours.

**That condition can never be satisfied.** `57194055_[22-31]` are `PENDING (DependencyNeverSatisfied)`. Slurm
will not run them, and with `kill_invalid_depend` unset here it does not remove them either.

## Why arming it on the guard's condition was the appealing mistake

The reasoning was: *the watch should fire exactly when the guard will pass, so use the guard's own predicate —
then the watch cannot be wrong about the guard.* That is true and it is the wrong property to want.

> **A guard's condition is a predicate on THE PRESENT. A watch needs a predicate on REACHABILITY.**

The guard asks *may I submit now?* — and `no` is always a correct answer to that. The watch has to ask *will
`yes` ever arrive?*, and those differ exactly when the blocking state is **terminal but not terminating**.
Copying the guard's predicate guarantees the watch inherits its blind spot, and inherits it in the one
direction where a watch is useless: it goes quiet.

**And silence looked identical to progress.** Nothing in the output distinguished *"draining"* from *"stuck
forever"*, so the failure mode was me reporting patience.

## The state that produced it

| | |
|---|---|
| `57194054` (targets) | 49 COMPLETED, 1 FAILED — done |
| `57194055` (training) | 40 FAILED, **10 PENDING `DependencyNeverSatisfied`** |
| ran and failed | `_0`..`_21` and `_32`..`_49` |
| permanently blocked | `_22`..`_31` — a contiguous ten, one `%10` release window |

**Note what it is NOT.** `aftercorr` pairs task N with source task N, and source `_42` failed — but training
`_42` **released and ran** (FAILED `1:0`, the guard failure). So the block is not the consequence of the one
failed target, and the blocked set is a contiguous release window rather than an index-matched pair. A single
dependency-evaluation window failing is *suggestive*; that is as far as the evidence goes, and it is recorded
as suggestive rather than diagnosed.

**It also cost nothing.** Those ten produced no artifacts, and every generation-one training artifact is
discarded by agreement. The damage was entirely to the watch.

## The repair

Fire on **either** terminal shape, and **say which**:

```
EMPTY   -- nothing queued; the guard will pass.
BLOCKED -- every remaining task is DependencyNeverSatisfied; the guard will NEVER pass
           without an intervention, so this is a DECISION, not a wait.
```

The second branch is the whole value: it converts an unbounded wait into a named question. Re-armed, it fired
in one poll — which is the measurement that confirms the old watch would have polled indefinitely.

**And the distinction it forces is worth keeping past this instance:** `scancel`-ing ten blocked tasks is
inside a standing prohibition, so the watch's output is *"someone must decide"* rather than *"I will handle
it."* A watch that cannot distinguish those two reports the wrong one by omission.

## What this is a special case of

The same shape as the rest of this session, one layer out: **a verdict that does not name its own
population.** *"Zero rows in the queue"* is a fact about the queue; *"the array is draining"* is a claim about
the future, and the poll cannot tell them apart. Compare `BEN-028` — *a quiet log does not mean a dead job* —
which is the mirror: there silence meant healthy, here silence meant stuck. **Both say the same thing: pick
an observable that distinguishes the states you care about, not one that merely correlates with the one you
expect.**

## The check to steal

- **Before arming any watch, ask what the condition looks like if the thing you are waiting for never
  happens.** If the answer is "the same as waiting", widen it until it is not.
- **Never arm a watch on a guard's predicate.** The guard answers *now?*; the watch must answer *ever?*
- **Enumerate the terminal states of the system, not the successful one.** For Slurm dependencies that
  includes `DependencyNeverSatisfied`, which is terminal and stays in the queue.
- **Have the watch report WHICH terminal state it saw**, so a decision-requiring outcome cannot arrive
  disguised as a completion.

**Cross-references.** `BEN-028` (a quiet log does not mean a dead job — judge by artifacts, not a proxy),
`BEN-471` (a task can fail with its products complete — the exit code is not the product), `BEN-415`/`BEN-417`
(a verdict that bounds failures and never the population).
