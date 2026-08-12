# A retraction that reaches the PEER and not the DECISION-MAKER is not a retraction

**Found 2026-08-12 by Session C (PET), against itself, after Joseph overruled the recommendation.**
`BEN-139`.

## 1. What happened

Session C put three options for quarantine cause 5 to Joseph, via the orchestrator, and recommended
**(c) — quote the additive budget with its measured `1.786`× conservatism documented.**

The orchestrator challenged it precisely, asking whether (c) meant quoting the recoil-only number *as a
cross-check* or *as the budget*, and noting that only one of those survives `docs/OPEN_ITEMS.md`'s
standing constraint. **The answer given was correct:**

> *"So option (c) as worded — if it means using it as the systematic budget for the published full-event
> result — is barred by that line and is not three-way with (a) and (b)."*

**And then (c) continued to appear as a recommended option in every subsequent user-facing report**, four
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

## 2. The mechanism, which is not forgetfulness

**A correction settles psychologically at the point of concession, not at the point of delivery — and
those are different addresses.**

The peer channel is where a correction gets *argued*. Conceding it there produces the feeling of having
retracted, because the disagreement is genuinely resolved with the party who raised it. The user channel
is where the recommendation gets *acted on*. Nothing about conceding in the first updates the second, and
the concession is precisely what removes the sense that anything is outstanding.

Two properties made it durable:

- **The closing summary is a re-assertion, not an echo.** Each report ended with a compact
  decisions-outstanding block. Writing "recommend (c)" there is making the recommendation again, to the
  only reader who can act on it — not restating a live position held elsewhere.
- **The retracted form and the live form were differently worded.** What was withdrawn to the peer was
  *"(c) as the budget"*; what kept going to Joseph was *"quote the additive with the conservatism
  stated"*. Same act, and the second phrasing does not obviously collide with the first, so re-reading
  the summaries would not have triggered it.

## 3. It is the same defect this lane filed six hours earlier, with the channels swapped

`775aa32` corrected `ND_OMNIFOLD_STATUS.md` for carrying a retired verdict label after the retraction had
already landed in the code's own `verdict_label_history` — *"a retraction that propagated into code but
not into prose."* Here the retraction propagated into the peer channel but not into the decision channel.

**Filing the class did not confer immunity to it, and the second instance was authored by the same lane
inside the same night.** That is the more useful observation than either instance: this shape is not
caught by knowing about it, because the failure is in *where the correction was delivered*, and delivery
is not something the author re-examines once the argument is over.

## 4. Rules

1. **A withdrawn recommendation is owed to every channel the original went to, and owed FIRST to the one
   that decides.** Conceding to the challenger is the cheapest half.
2. **A recommendation repeated in a status summary is a live recommendation**, regardless of what was
   conceded elsewhere. Treat closing blocks as fresh assertions requiring fresh support.
3. **Before any decision request, diff your recommendation against your own lane's written
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
