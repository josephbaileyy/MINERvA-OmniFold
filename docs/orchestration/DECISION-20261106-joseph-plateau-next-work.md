# DECISION 2026-11-06 — Joseph: after the plateau, the per-period benchmark and the rounding fix first; new Claude lanes; sync the note repository

**Recorded by** the paper-tighten lane, as director.

## What led to it

**Round 4** of the methods draft (#864, `secondary-results/referee-methods-round4-20261106/`) scored PRD 3.5 and JINST
4.25, the same as round 2, even with the records on main brought into the text. All eight reads named the same
remaining items, and each is an analysis:
- the rounding instability;
- a coverage test run;
- the prior retention's mechanism;
- the 2D benchmark per run period;
- self-containment.

The director put three questions, with recommendations, through AskUserQuestion.

## Joseph's answers, verbatim

1. **Which work goes ahead now.** The options were:
   - the per-period 2D benchmark (recommended);
   - the rounding fix now (recommended);
   - the prior-retention study now;
   - a coverage test run (the director recommended deciding after Part 1).

   > Per-period 2D benchmark (Recommended), Rounding fix now (Recommended), Prior-retention study now, Coverage test run, okay we can put a short pause on the non recommended things if you want too just let me know

   sha256 begins `5cb72c022e6f251f`.
2. **Lanes for the new work.**

   > how about I hope claude lanes and tell them to contact you through peermessage?

   sha256 begins `45df82616f5dc3eb`. The director reads "hope" as "open".
3. **The note repository.**

   > Sync repo; hold deposit (Recommended)

   sha256 begins `40947340bbe114c8`.

## What is decided

1. **Now:**
   - **The per-period 2D benchmark.** Each run-period group's existing 2D unfold (`period-unfold-20261014`, #135) is
     compared with the published result. It is declared, priced and bound before it runs.
   - **The rounding-instability fix.** The mechanism is found first, then an estimator that averages over rounding
     perturbations is declared as a variant. Each step is declared, audited and bound before it runs.
2. **Authorized, and paused by the director under Joseph's "short pause" offer:**
   - **The prior-retention study.** It starts when one of the two lanes above frees up.
   - **A coverage test run.** Joseph's selection is his override of 1B's rule (iii), for a declared coverage test
     built like-for-like (DECISION-20261102-joseph-1b-redesign.md:78). It starts only after Part 1 (#861, the flux and
     detector groups) reports and shows whether a like-for-like construction holds for every group. It is declared,
     priced, audited and bound before it runs, and a campaign above half the group balance goes back to Joseph first.
3. **Lanes.** Joseph opens new Claude sessions, which contact the director by Peer Mesh. The director writes their
   handoffs.
4. **The note repository.** The standalone `MINERvA-OmniFold-Analysis-Note` repository is synced and pushed from current
   main, as AGENTS.md "Deliverable synchronization" requires. No wording changes. Any public deposit of the note waits.

## Not decided here

- Any wording.
- Any venue.
- Any submission or deposit.

Nothing is submitted, deposited or tagged.
