# DECISION 2026-10-28 — Joseph: scope the coverage limitation and three related items before choosing

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- Joseph asked what it would take to address the coverage limitation, and for a fresh agent to rate its importance.
- The independent consult (`secondary-results/astra-consult-coverage-20261028/`, PR #453) rated a nuisance-drawn
  coverage test 4 of 5. It recommended 1B with the control validated first, named a cheaper control-plus-one-truth
  variant, and named three items it judged to matter more:
  - a hadronic-response mismodeling test beyond C_resp;
  - the covariance's suitability for the quoted χ²;
  - tracing the run-period inconsistency into the sixteen-cell uncertainty.
- The director offered four ways forward: scope all of these first; run 1B now; run the cheaper variant; or keep the
  test deferred.

Joseph's answer, verbatim, the option he selected:

> Scope all four first (Recommended)

sha256 of the text plus a final newline begins `bee1d92a0bc5e4aa`.

## What is decided

1. **A costed scoping addendum to `LIMITATION-PLAN.md` is written, at 0 node-h.** Read-only checks are allowed. It
   covers:
   - 1B as designed;
   - the control plus one predeclared GENIE v3 truth;
   - a test of hadronic-response mismodeling beyond C_resp;
   - a check of the covariance's suitability for the quoted χ²;
   - tracing the run-period inconsistency into the sixteen-cell uncertainty.
2. **For each item it gives** what exists, the design, what it answers and what it cannot, its cost as measured units
   or stated assumptions, and which items can share runs.
3. **The addendum comes to Joseph,** who then chooses what runs. No compute is granted by this decision.
   `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` item 4's deferral stands until then.

## Not changed

- The paper's limitation statements and the final draft's work (d2).
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
