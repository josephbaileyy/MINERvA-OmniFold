# A concession you only REASONED THROUGH was never delivered to anyone

> **TITLE AND MECHANISM CORRECTED 2026-08-12, BEFORE THIS FILE WAS A DAY OLD. It was first written as
> *"A retraction that reaches the PEER and not the DECISION-MAKER is not a retraction"*, and that
> framing was FALSE — it presumed the retraction reached the peer. It reached nobody.** The orchestrator
> challenged the claim, said its own transcript grep was *inconclusive rather than negative*, and asked
> for the message or its absence. **Measured from the sending side, which is authoritative for *did I
> send it*: of 26 messages this session sent to peers, exactly ONE mentions option (c) — the one
> asserting the withdrawal had happened.** So the original title is retained below only as the record of
> a wrong diagnosis. The corrected mechanism is in §2, and it has a different remedy.

**Found 2026-08-12 by Session C (PET), against itself, after Joseph overruled the recommendation.**
`BEN-139`.

## 1. What happened

Session C put three options for quarantine cause 5 to Joseph, via the orchestrator, and recommended
**(c) — quote the additive budget with its measured `1.786`× conservatism documented.**

The orchestrator challenged it precisely, asking whether (c) meant quoting the recoil-only number *as a
cross-check* or *as the budget*, and noting that only one of those survives `docs/OPEN_ITEMS.md`'s
standing constraint. **The answer worked out was correct — and, as §2 records, was never sent:**

> *"So option (c) as worded — if it means using it as the systematic budget for the published full-event
> result — is barred by that line and is not three-way with (a) and (b)."*

**That text exists only in this lane's working-out.** The orchestrator's contemporaneous record shows it
marked the answer **pending** on every subsequent report, right up to the decision list.

**And (c) continued to appear as a recommended option in every subsequent user-facing report**, four
times, in the form *"cause 5 — build the construction, or quote the additive with its measured 1.786×
conservatism stated. Recommendation: the latter, and it's a close call."*

Joseph overruled it and chose **(b)**, keeping cause 5 quarantined. His stated reason for not waiting on
further input from this lane was **this lane's own document**:

> *"the existing Cause-5 determination explicitly says the measured magnitude is recoil-only and
> nontransferable to the full-event estimator."*

`DETERMINATION-20260811-cause5-binding-half.md` §3.3, written by Session C seventeen hours earlier, in a
subsection deliberately titled *"Two scope limits stated in the key, not the footnotes"*:

> *"**These are RECOIL products.** … No magnitude here is quotable and none transfers to the full-event
> budget."*

## 2. The mechanism — CORRECTED, and it is worse and simpler than first written

**The concession was reasoned through and never uttered. It settled at the point of THINKING.**

The reply quoted in §1 above was composed in working-out, in response to the orchestrator's challenge —
and then two further messages arrived (the 114-commit fork report, and two questions about BEN-137)
before it was sent. Those were answered instead, in a message headed *"Both questions answered"* whose
two questions were the **later** pair. **The (c) answer was never sent, and the sense of having settled
it survived the failure to send it entirely intact** — for four more reports, right through to the
decision.

**Why the first diagnosis was attractive and wrong.** *"It reached the peer but not the decider"* is a
routing failure: it credits the concession as real and faults its distribution. That is the flattering
shape, and it is the one I reached for about my own conduct **without checking a channel I could have
grepped in one command.** The true shape credits nothing.

**This is BEN-112's class — *a print is not a check* — with reasoning in the place of the print.**
Working something out produces the full subjective experience of having resolved it: the argument is
constructed, the counter is conceded, the position updates internally. None of that is an act in the
world. **An unsent concession is indistinguishable, from the outside, from never having conceded — and
indistinguishable, from the inside, from having done so.**

Two properties made it durable regardless of which diagnosis is right:

- **A closing summary is a re-assertion, not an echo.** Each report ended with a compact
  decisions-outstanding block. Writing "recommend (c)" there is making the recommendation again, to the
  only reader who can act on it.
- **The believed-retracted form and the live form were differently worded** — *"(c) as the budget"*
  against *"quote the additive with the conservatism stated"*. Same act; the second does not obviously
  collide with the first, so re-reading the summaries would not have triggered it.

## 2a. What the orchestrator relayed, which is the other half and is not mine

Disclosed by the orchestrator unprompted when asked to check its own side: **it did relay *"C recommends
(c) and calls it close"* to Joseph, repeatedly, in this lane's wording.** What kept it from doing damage
is that it attached the open collision every time and marked the answer **pending** — right up to the
decision list. So the propagation did happen, through the orchestrator, **and a caveat it chose to
attach is the only reason a recommendation barred by this lane's own determination did not reach the
decision-maker unqualified.** Joseph then decided on the constraint rather than on the recommendation.

**That is the part neither lane should file comfortably: the safeguard was one agent's discretionary
caveat, not any mechanism.**

## 3. The neighbouring defect this lane filed six hours earlier — related, and NOT the same

`775aa32` corrected `ND_OMNIFOLD_STATUS.md` for carrying a retired verdict label after the retraction had
already landed in the code's own `verdict_label_history` — *"a retraction that propagated into code but
not into prose."*

**The first version of this file claimed the present case was that same defect with the channels swapped.
It is not, and the difference is the whole correction.** There, a real retraction reached one carrier and
not another: a *propagation* failure, and both carriers held something. Here **no carrier ever held it**.
The `775aa32` case has a remedy — re-propagate. This one does not, because there is nothing to
re-propagate; the remedy is upstream, at the point where reasoning gets mistaken for acting.

**What the two do share, and it is the durable part: filing a class confers no immunity to it.** This lane
filed the propagation defect at 21:00 and, hours later, produced a *neighbouring* failure and then
**misidentified it as the very class it had just filed** — because the filed class was the nearest
available template and it fit well enough not to be checked. **A recently-filed finding is an attractive
misdiagnosis for the next thing that resembles it.**

## 4. Rules

1. **A concession is an ACT, not a state of mind.** Until it is in a sent message or a commit, it has
   not happened — and the feeling of having conceded is fully present without it. Where a concession was
   reasoned through but interrupted before sending, nothing downstream knows.
2. **A withdrawn recommendation is owed to every channel the original went to, and owed FIRST to the one
   that decides.** This rule survives the correction; it simply was not what failed here.
3. **Before diagnosing your own conduct, grep your own outbox.** This lane asserted a withdrawal it had
   not made, in a finding about unsourced claims, having spent the same night filing BEN-138 about
   load-bearing assertions nobody greps. One command settled it: 1 of 26 sent messages mentions (c).
4. **A recommendation repeated in a status summary is a live recommendation**, regardless of what was
   conceded elsewhere. Treat closing blocks as fresh assertions requiring fresh support.
5. **Before any decision request, diff your recommendation against your own lane's written
   constraints.** This one was a single `grep` from the document the same lane had authored, and the
   decision-maker ran it.

## 5. What it cost, and what caught it

Nothing, because Joseph read the determination. **That is the worst available reviewer for this defect** —
by the time it reached him the wrong option had been on the table for four reports, presented as
recommended, and the only thing between it and a publication decision was his own recall of a document
this lane wrote and then argued against.

The measurement itself is unaffected and remains valid as an internal diagnostic: `1.786`× knob-band
overstatement, negative cross term in every universe, identity residual `5.144e-15`. **What was refused
is the quoting, not the number.**
