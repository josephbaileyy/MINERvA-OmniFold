# Agent authorship in this repository

*Draft, not adopted. The wording is still under review.*

AI coding agents did a large share of the work in this repository. This note says what the commit
history can and can't tell you about that, and what I claim.

## What the commit history shows

[`check_authorship_floor.py`](check_authorship_floor.py) counts commits that are attributed to me
but carry a `Claude-Session` trailer, which agent sessions add to their commits. Run it with
`python3 docs/sep-09-presentation/check_authorship_floor.py`. At commit `72a2ada5` (2026-09-20):

| | |
|---|---|
| commits | 3,094 |
| commits with a `Claude-Session` trailer | 290 |
| of those, committed under "Joseph Bailey" | 98 |
| commits with no trailer | 2,804 |

So at least 98 commits under my name were made by an agent session. That is 34% of the commits
that carry the trailer, and 7.2% of the 1,356 commits under my name.

That number is a lower bound, and a loose one. The trailer only appears when a session was set up
to write it, and much of the history predates that. A commit without the trailer may or may not
have been written by an agent; the history can't say which.

Re-running the script on later history gives larger totals, but the count of 98 has not changed.
Since mid-August, agent commits default to a separate "MINERvA-OmniFold agent (unattributed)"
identity rather than my name.

## Limits of the trailer

- A commit with the trailer came from an agent session.
- A commit without it is not evidence of human authorship.
- The trailer identifies a session, not how much of the change the agent wrote or who directed it.
- The script matches a substring, so a commit message that quotes the trailer would be counted. I
  haven't seen that happen, but the script can't rule it out.

The script stops with "cannot check" instead of reporting zero if it finds no trailers at all,
since a zero then would only mean the parse found nothing.

## What I claim

I direct this analysis and I am responsible for every scientific claim in it. Agents wrote much of
the code, the records, the checks and the prose here, under my direction. The commit history
doesn't separate those roles cleanly.

I am not giving a "percent written by AI" figure, because there is no way to measure it that I
would trust. [`measure_workflow_quantities.py`](measure_workflow_quantities.py) applies the same
standard to the other workflow numbers in this project and leaves out the ones that don't hold up;
for example, it reports the commit-size power-law fit as failed instead of quoting an exponent.

The scientific results don't depend on who wrote which commit. They rest on the receipts, digests,
preregistrations and independent checks in `docs/orchestration/`, which a reader can re-derive
without trusting the commit metadata. Where an independent check was blocked, that is recorded too;
see [`DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md`](../orchestration/DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md).

— Joseph Bailey
