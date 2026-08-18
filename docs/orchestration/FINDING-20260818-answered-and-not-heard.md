# FINDING 2026-08-18 — answered and not heard: a channel whose failure is silent at both ends

**BEN-257.** Lane D (verifier), filed at lane A's request and routed by the mediator. **A's
zero-`SendMessage` count is the mediator's measurement, attributed rather than claimed** — I did not
read A's transcript and cannot.

## What happened

The mediator censused every lane. Lane A composed an answer and emitted it as **terminal output**,
making **zero `SendMessage` calls**. The tool's own contract is explicit:

> *"Your plain text output is NOT visible to other agents — to communicate, you MUST call this tool."*

So **A had answered, and A had not been heard.**

## Why it is a finding and not a slip

Neither party had any signal telling them which world they were in.

| party | what they observed | what they could conclude |
|---|---|---|
| lane A | an answer, composed and emitted | *"I responded."* |
| the mediator | nothing | *"A is capped, or busy, or dead."* |

Both readings are locally correct. **There is no delivery receipt and no sender-side error**, so the
sender cannot detect non-delivery and the asker cannot distinguish non-delivery from non-response.
The census then carried a lane state **inferred from silence**, which is the part that reaches a
document.

**Same species as [`BEN-255`](FINDING-20260817-the-fix-for-the-last-instance-is-the-mechanism-of-this-one.md):
the verdict is not wrong — the signal that would distinguish the two readings does not exist.** There
it was a gate honestly green on one population and red on another; here it is an answer honestly sent
and honestly not received.

**The asymmetry is what makes it durable.** The cost falls entirely on the party who cannot detect
it. A lane that answers in text pays nothing and learns nothing; the asker pays, and pays again if
the inferred state reaches a report.

## The rules

1. **A census answer is not an answer until it is a `SendMessage`.** Terminal text is for the user,
   not for peers, and the tool says so.
2. **An asker treating silence as a lane state must write `NO RESPONSE`**, not a status inferred from
   it. This is [`BEN-027`](FINDINGS.md) — *every id, rank, count and queue name in a status report
   must come from a command run in the same turn* — **applied to lane states rather than job ids.**
   A lane's state is as much a measurement as a queue name, and "silent" is not one of its values.
3. **Write-time complement**, from `BEN-256`'s Rule 3: before inferring from a channel's output, ask
   **what else produces that same output.** Silence is produced by capped, busy, dead, finished, and
   *answered-in-the-wrong-channel* — five states behind one observation.

## What this does not claim

Not that anyone was careless — A composed a correct answer and the mediator asked rather than
inferred when it mattered (it asked me directly whether `57199158` was mine rather than attributing
it, which is `BEN-027` working). **The defect is in the channel, which reports success identically to
silence, and no amount of care at either end produces the missing signal.** That is the same closing
note as `BEN-256`: local diligence does not compensate for an interface that cannot express the
distinction.
