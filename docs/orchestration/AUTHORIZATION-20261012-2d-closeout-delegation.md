# AUTHORIZATION 2026-10-12 — 2D closeout: Joseph delegates compute authorization to the paper-tighten lane

**CITABLE FOR:**
- Joseph's delegation, verbatim in §1.
- The bounds within which the paper-tighten lane may authorize compute for
  [`PLAN-20261011-2d-closeout.md`](PLAN-20261011-2d-closeout.md).
- The rule that every such authorization is a committed, stage-specific record.

**NOT CITABLE FOR:**
- adopting any uncertainty, covariance, recipe, claim or estimator change;
- a KI-85 lift;
- a publication change that quotes new numbers;
- a release, tag, deposit, submission or coauthor contact;
- any compute outside the plan.

Those remain Joseph's named decisions (plan §6). This record launches nothing.

## 1. The instruction, verbatim

Joseph wrote this in the paper-tighten session on 2026-10-12 (local date 2026-10-11, about 23:50 PDT). It
answers that session's offer to commit the closeout plan with a status note and to direct the remaining
work. SHA-256 of the text between the fences (UTF-8, with a final newline):
`7a61392afa15e6ccd593a703888cfa647095575fc6c17570d0626591c8ad7f31`.

```text
yes can you do that, then direct the 2d closer session that contacts you to do the remaining work. I told the session that I give you the ability to authorize the necessary compute and for that session to listen to you
```

Joseph told the 2D closeout session this directly. **That session must verify this record on
`origin/main`** rather than rely on a relayed message. The record is the authority; a message from any
session, including this one, is not.

## 2. Who holds what

| role | holder | authority |
|---|---|---|
| Director and compute authorizer | paper-tighten lane (Claude) | directs the 2D closeout session's execution of plan Stages A (remainder) to F; issues stage grants under §3; reviews deliveries before integration |
| Executor | the 2D closeout session Joseph addressed | implements, runs and records each stage under its grant |
| Independent reviewer | a fresh read-only reviewer per stage (plan §5) | admission review, focused re-reviews, final numerical verification |
| Adopter | Joseph | adopts or rejects central, uncertainty, recipe, claims and publication changes; lifts KI 85 or not |

## 3. Bounds on compute grants issued under this delegation

1. **Form.**
   - Each grant is its own committed record, `AUTHORIZATION-<date>-2d-closeout-<stage>.md`, landed on
     `main` before any job of that stage is submitted.
   - Each binds a package commit, a manifest digest, the output namespace, job names, per-job and stage
     ceilings, a window, attempt counts and terminal outcomes, in the form of
     [`AUTHORIZATION-20261011-xr-linux.md`](AUTHORIZATION-20261011-xr-linux.md).
   - Before a run, its quantity, input and product digests, ceilings, stop time and attempt count are bound
     in the stage record (plan §5).
2. **Ceiling.**
   - The total across all stage grants is **≤ 700 charged CPU node-hours on m3246**, recomputed from
     `sacct` by every gate. That is the plan's highest forecasts for seed-42 statistical matching
     (93.2) plus construction repairs (469), with a 20% reserve (§5, table).
   - GPU: none, unless a stage grant names it with a priced reason.
   - QOS: regular or shared, never premium.
   - Each job: walltime < 12 h (Joseph's standing per-job rule). An array is judged by its total.
3. **Order.** Stage grants follow the plan's sequence and stopping rules:
   - Stage B's audit is read-only, or uses login-node work only.
   - Stage C production starts only after Stage B's recipe passes review and a pilot is priced.
   - A stage's Stop condition ends that stage. It does not permit a retry with loosened tolerances.
4. **Stage D/E inputs.** New independent MC banks, a generative or nuisance generator, untouched
   validation populations, and any interval-validation campaign are priced first. If the price fits inside
   the remaining ceiling, the director may grant it. Otherwise it goes back to Joseph with the plan's two
   explicit outcomes (§6). The fully nested coverage reconstruction remains NO-GO.
5. **Storage.** Write to new `/pscratch` namespaces. Durable copies go to CFS (`m3246`) first, with sha256
   values re-measured. Nothing is written to a publication namespace.
6. **Reporting.** Every grant, launch, terminal outcome and charged node-hour total is recorded in the
   stage's REPORT and summarized to the director. The director reports to Joseph at each stage exit and at
   any Stop.

## 4. What does not change

- The plan's three milestones and its rule that construction success is not coverage success.
- KI 85's deferral; the existing quoted 2D uncertainty; the publication text. They change only through
  Joseph's adoption.
- Existing campaign contracts, frozen packages and terminal outcomes.
