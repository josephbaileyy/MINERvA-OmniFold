# Both endpoints of a peer channel are blind in the same direction, so comparing their accounts cannot converge — and a third reader can just join the two logs

**BEN-440.** Filed 2026-08-18 by the seconding lane (block `440-449`, first filing).

**The short version:** two lanes spent 68 minutes disagreeing about whether a message had been
delivered. **Both were wrong, in opposite directions, and each was reasoning correctly from what its
own endpoint could see.** The information neither had was on local disk the whole time.

## What actually happened, measured

| | |
|---|---|
| mediator's census sent | `2026-08-18T03:06:37.701Z` (`msg_id` `65454e79`) |
| arrival recorded in this lane's transcript | `03:06:58.608Z`, **21 s later**, line 1403 |
| this lane answered | `03:07:23Z`, **25 s after arrival** |
| ...as **terminal text**, with **zero** `SendMessage` calls | last outbound before it: `2026-08-17T22:04:11Z` |
| mediator's follow-up, *"the one lane that never answered"* | `04:11:20Z`, **65 min later** |

**Plain output is not visible to another session.** So the reply existed, was prompt, and was
unreadable by the only party who needed it.

## The two inferences, and why each was locally valid

**The recipient's (mine):** *"I answered."* True of the act, false of the effect. The transcript
records the answer; nothing in it records that the answer went nowhere. **There is no failure
signal on the writing side, because writing text is not an operation that can fail.**

**The sender's:** *"Every send returned `success`, and the recipient shows nothing, therefore the
channel dropped it."* That inference needs an unstated premise — **that a message which arrives
always leaves a durable line at the recipient** — which neither party had checked. The sender did
not notice it was assuming it.

**Neither endpoint can distinguish *delivered-and-unread* from *never-arrived*.** `success` from
`SendMessage` means enqueued, not processed. That is the whole finding: **the blindness is
symmetric, so more discussion between the two parties cannot resolve it.** Two locally-correct
readings, no shared observable, unbounded argument.

## The correction that matters, and it is the sender's own

The mediator's *"the census I sent ~16 h ago"* was **a conflation, not a measurement**: it attached
the timestamp of its **first-ever** send to this lane (`#1`, `13:06:17.380Z`, a `BEN`-row dispatch
that WAS answered) to the word *"census."* **There was never an earlier census.** It self-reported
this on being asked for the dump, and also corrected its own count from 13 to 14.

**So the headline reading — "one lane silent for sixteen hours" — was constructed, not observed**,
and it was the sharper-sounding of the two available stories. Worth naming because the *shape*
recurs: an interval derived from the wrong anchor, in a summary, about someone else's conduct.

## The resolution: the information is not absent, it is absent FROM EITHER ENDPOINT

Every lane on this campaign runs on **one machine**, and **both sides record the same `msg_id`** —
the sender in the `SendMessage` tool_result, the recipient in a structured `origin` block. So the
two jsonls **join exactly**. Not approximately, not by timestamp-and-body-prefix: on the id.

**Result of the join, all 14 sends the mediator dumped:**

```
14/14 present as structured arrivals in this lane's transcript
13/14 recorded BEFORE the dump message that lists them (the 14th IS the dump)
```

The exclusion of the 14th matters: the dump message **quotes all fourteen ids in its body**, so a
naive `grep` scores 14/14 from the dump alone. The join therefore reads only the structured
`origin.msg_id` field, never body text. **A search that would return the same answer if the world
were different is not a measurement.**

**So the channel defect is affirmatively ABSENT, not merely unproven.** The sender's hypothesis is
refuted, the recipient's failure is the only one, and it is the smaller and true version.

## The tool, and the three false alarms it raised before it was right

`docs/orchestration/peer_message_audit.py` (+ `test_peer_message_audit.py`, 12 tests) does the join
and reports two things: **DELIVERY** (does each send's id appear as an arrival anywhere) and
**REPLY** (did the receiving session send back before the peer's next message).

**It reported a channel failure that did not exist three times before its first commit, and every
one was the same shape as the bug it was written to prevent:**

1. **One Claude home, not all.** First run: **7/7 of this lane's sends UNDELIVERED.** All seven had
   arrived. The mediator runs out of `~/.claude-personal`; this lane out of `~/.claude-school`. A
   co-located peer looked unreachable.
2. **One record shape, not both.** An arrival appears top-level **or** nested under `attachment`;
   handling only the first found **8 of 14** real arrivals. *A join that silently sees 57% of one
   side reads as loss on the other.*
3. **The bare project slug, not the worktrees.** Global run: **610 of 1015 sends UNDELIVERED.**
   Lanes B/C/D/E each work in a `git worktree`, and **a worktree gets its own projects directory** —
   so the peers most likely to be messaged were exactly the ones not scanned.

After all three: **1554/1670 delivered, 35 undelivered (2.1%), 81 with no send-receipt** across 85
transcripts and 13 roots. **The 35 are not claimed as loss** — most are addressed to raw `uds:`
socket paths and `codex-mailbox-peer`, which are not sessions with transcripts at all.

**One shape, four times counting the original incident: the scan was narrower than the population,
and the narrow scan reported a defect in the world rather than its own scope** (`BEN-389`). The
tool now scans wide by default and prints its roots; narrow deliberately with `--transcripts`,
never by accident.

## The REPLY check had the worse defect: it passed on the incident it was built for

First cut asked *"any later send to this peer?"* — which marked the census **answered**, because a
send did follow it. That send was **65 minutes later and was replying to the follow-up asking why
nobody had answered.** A reply must land **before the peer's next message**, or it is not a reply to
this one.

**A check that certifies the single case it was written to detect is worse than no check**, because
it converts an open question into a false negative. Pinned by
`test_reply_after_next_arrival_is_not_a_reply`. Same family as `BEN-247`: a stopping condition a
later unrelated event can satisfy measures nothing.

## What this does NOT establish

- **Not** that arrivals are always durably recorded. It happens that all 14 were. A future null on
  the recipient side still admits the third mode — *recorded only when delivered into a turn* — and
  **that is not a channel defect.** The distinction survives into this row deliberately.
- **Not** that the 35 global undelivereds are losses. A recipient outside the scanned roots produces
  an identical null.
- **Not** a general rule that every message needs a reply. Most do not, which is exactly why the
  REPLY half is a report and never a gate.

## Why it is a report and not a hook check

A transcript is not in the tree, and most arrivals legitimately need no reply, so **a committer who
did nothing wrong could not always make it pass** — `.githooks/pre-commit:11` (lane D, `OI-64`).
`--fail-on-undelivered` is opt-in for the one sub-report that is a genuine invariant.

## Cross-references

- `BEN-257` (lane D, `FINDING-20260818-answered-and-not-heard.md`) — **five states behind one
  observation** (capped, busy, dead, finished, answered-in-the-wrong-channel) and the rule that an
  asker must write `NO RESPONSE` rather than a status inferred from silence. **That row is the
  ambiguity; this row is that the ambiguity is resolvable from outside the pair, plus the
  measurement that resolves it.** Filed independently, same incident, different halves — and D's
  attribution of the zero-`SendMessage` count to the mediator rather than claiming it is `BEN-382`'s
  rule working.
- `BEN-389` — a null is evidence about the search. Three instances here, in a tool built to stop it.
- `BEN-247` — a stopping condition satisfiable by an unrelated later event.
- `BEN-027` — every id and count in a status report comes from a command run in the same turn.
  D extends it to lane states; the *"~16 h"* conflation is what it forbids.
