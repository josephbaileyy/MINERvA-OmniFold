# DECISION 2026-10-25 — Joseph: scope the 5D fake-data test

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- S1 is complete (`state/measurement-paper/5d-community-20261024/S1-REPORT.md`, PR #348; rulings in
  `S1-DIRECTOR-RULINGS.md`, PR #349). Configuration (e) now has its own 5D covariance on the 16 H2 cells.
- The director recommended the next step: scope a fake-data test and the generator comparisons that use this
  covariance, at about 0 node-h. The result would be a costed plan for Joseph before anything runs.

Joseph's answer, verbatim:

> okay scope the fake data test, is this measurement ready for publishing?

sha256 of the text plus a final newline begins `ba6fd432f5694b07`.

## What is decided

1. **The fake-data test is scoped, at 0 node-h.** The measurement session writes
   `state/measurement-paper/5d-community-20261024/FD-PLAN.md` and opens it as a PR to the director. It covers:
   - the inventory of existing fake-data evidence for (e) on H2;
   - the circularity of fake-data truths that are also C_model,5D vertices;
   - test statistics declared before anything is read;
   - costs from measured unit costs;
   - risks.
2. **The generator comparisons are scoped in the same plan as a separate stage.** They read the data result, so running
   them needs Joseph's own approval, given after the fake-data stage reports.
3. **No compute is approved.** Any job needs Joseph's approval of the costed plan, then a declaration and a binding.

## Joseph's question, and where it is answered

Joseph asked whether this measurement is ready for publishing. The director answered in conversation. That answer is
not a decision, so it is not recorded here, and publishability stays Joseph's call.
<!-- absence-ok: states where an answer lives, not a claim that a result is absent from the repository -->

## Not changed

- **No GPU and no premium QOS.** Nothing is written to CFS.
- **Claims, KI-85, `\pubhold` and release text** are Joseph's. Nothing is submitted, deposited or tagged.
- **Publication** of a measurement from MINERvA data needs collaboration review, which is Joseph's act. Joseph's
  message to Ben stays held.
