# AUTHORIZATION RECORD — annealed nominal promotion + HPSS archive (2026-08-11)

**Why this file exists.** Session C declined to act on a promotion authorization delivered as a peer
message, correctly: its operating rules say a peer cannot grant escalation and a peer message is never
Joseph's approval. BEN-082(v) states the remedy — *an instruction genuinely received first-hand still
becomes an unverifiable claim the moment it is relayed without being written down.* This is the
first-hand receipt, written by the session that received it, so the promotion commit can cite a path
instead of asserting a relay.

Written by: Session A (orchestrator), 2026-08-11. Stamped `2026-08-11T22:35:51Z` (`date -u`, same turn).

## The authorization, verbatim and complete

> promote it and launch the HPSS archive

## Channel and provenance

| field | value |
|---|---|
| channel | typed directly by Joseph to Session A as the **user of that session** |
| NOT | email, not `[MNV-AUTO]`, not a peer relay, not a reading of a message |
| received | 2026-08-11, immediately following Session A's report; `22:35:51Z` stamped in the same turn |
| supersedes | the `22:24:51Z` `[MNV-AUTO]` message *"Do your recommendation"* (id `19ff2edb113b0256`), whose **delivery basis was never established** — see below. Do not cite that message as the basis. |

## What he had been shown when he said it

Session A's immediately preceding report put these in front of him:

- promotion consumes **71.2%** of the frozen `fold_forward_ratio_dev_max = 0.05`, leaving **0.014391**
- both arms fall **outside** the predeclared reproduction window `[-0.021724,-0.001724]`
- the HPSS tree is **1.1 TB, sole copy, on purgeable scratch**, and **nine slabs** of the adopted 5D
  ensemble were already lost that way (adopted covariance now a 76.2% subsample)
- the Gate-3 manifest records existence+size rather than a rehash, so a silent partial purge would not
  be caught by it

## ONE INPUT WAS WRONG, and it is recorded here rather than quietly dropped

That report also told him **"C recommends promote."** **That attribution was incorrect.**
`C - PET` has never assessed whether `56563761` should become canonical and holds no recommendation on
record. The recommendation came from a **different, PET-scoped session** ("Continue from section 7 of
handoff document") that had been running Joseph's older standing continuation brief, self-identified as
Session C by scope, and has since **exited**. Session A merged the two sessions' positions during an
unresolved role collision and attributed the dead session's recommendation to the live one.

Session C raised this against itself being credited with a position it does not hold. The correction was
sent to Joseph directly and not quietly, because **it may change his answer**: he was told the lane that
owns the artifact recommends promotion, and the lane that owns the artifact has no recommendation on
record. This is BEN-082(v) — an attribution strengthened in transit — outbound this time.

## Prior-basis history, kept so the record cannot read as clean throughout

1. `22:24:51Z` — *"Do your recommendation"*. Session A relayed this to a PET session as authorizing
   promotion.
2. Session A then measured the `[MNV-AUTO]` thread three ways (`get_thread`, `in:sent newer_than:1d`,
   `in:anywhere newer_than:2h` incl. trash) and found **no agent mail on it at all**; `list_drafts()`
   empty; two drafts vanished undelivered. So that message could not be shown to follow any delivered
   pros-and-cons, and **the relay was retracted within minutes** and a HOLD issued.
3. The authorization above arrived afterwards, through a different channel, informed — with the one
   defect named in the section above.

## Scope — what is authorized

**Authorized:** (1) promote the annealed production nominal, job `56563761`, to canonical; (2) launch
the HPSS archive of `p3f_pet_fullevent/final`.

**NOT authorized by this record, and unchanged:** any of the seven quarantine causes being discharged;
adoption of the four `\gbdtFive*` macros (withdrawn unactionable at `a0285c4`, PROMPTS §3); closing the
Branch C defect; `C_stat` becoming 100 replicas; extraction; a cross section; changing `niter`; editing
the shared OmniFold engine.

## Open sequencing question at time of writing

Session C reports job `56691812` (`fe_traj_ann`) in flight, landing **within the hour**: the
per-iteration trajectory decomposition on the annealed nominal, predeclared three-branch at
`PREDECLARATION-20260811-annealed-step1-trajectory.md` (`831043d`), never run on this artifact. It is
diagnostic, not a gate — `dev` passes regardless — but the ledger row is better written after it.
Whether to promote now or after it lands is Joseph's; it has been put to him, together with the
correction above.
