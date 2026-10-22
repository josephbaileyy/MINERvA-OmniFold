# Assignment: the W-bias confirming test for KI 98 (2026-10-22)

**Assigned by** the paper-tighten lane, as director (Stage F). **Assigned to** the measurement session. Joseph told
the measurement session to take all its decisions, compute included, from the director.

## Why

- **The request.** Joseph asked for this test to be run. His words reached the director by a relay from
  minerva-omnifold-2c, his personal-account session (2026-10-22):

  > I think perlmutter is back so can you send try and see if the delegator or measurement session will do the W test?
  > you might have to wait for their usage to reset

  A relay grants nothing by itself. The authority for this assignment is:
  - the director's standing direction of the measurement session;
  - DECISION-20261019-joseph-methods-first-and-measurement-compute.md. Its compute covers the methods-paper items that
    need computation and the validated five-dimensional uncertainties. It lifts the 2026-10-10 pause for that work.
  - the standing approval of any single job under 12 h.
- **The measurement session declined the relay** (2026-10-22) for three reasons:
  - the record would go under `state/2d-closeout/**`, which its handoff forbids it to edit;
  - the test is outside MP-1 to MP-5;
  - Perlmutter was mostly still in maintenance.

  It offered to declare and run the test once assigned, with a record location. This record is that assignment.
- **The question** (KNOWN_ISSUES row 98; `state/2d-closeout/stageF/methods/M2-RATEFAIL-DIAGNOSIS.md` §6 and the
  "Cheap confirming test"):
  - At the s5c tilt point the residual bias grows with W.
  - Its size and ordering match 0.111·f_bkg, the change in B/S when the signal rate drops by 10% and the background
    does not.
  - It is not established whether it comes from that change or from the estimator alone.

## The test

These are the diagnosis's own terms, with no other code change.

- **Arms.** Tilt pseudo-experiments on the same seeds, run three ways:
  - **(a)** as run: background drawn fresh and not reweighted;
  - **(b)** with `--no-background` (`s5c_pseudo.py:131-132`);
  - **(c)** with the background scaled by 0.9 as well, so that B/S is unchanged by the tilt.
- **Seeds.** About 4–9 per arm, at about 0.015 node-h each (`FEASIBILITY-20260925-s5c-scalar5d-measurement-and-inference.md:21`).
- **Separate cluster read, no compute.** Read the per-functional means and SDs of the 400 existing tilt products.
  They replace the inferred table of the diagnosis.

## Conditions

1. **Declare before running.** The measurement session commits a declaration before any job is submitted, at
   `docs/orchestration/state/ki98-wbias-test/DECLARATION.md`. It must give:
   - the code commit;
   - the seeds;
   - the per-arm count;
   - the functionals read (at least EW9, EW10, EW16, J116 and J224, and the W-band summary of the diagnosis);
   - the metric: the corrected mean residual per functional in units of its σ, with its standard error;
   - the decision rule, stated numerically. For example: "the W-graded residual is attributed to the B/S change if
     the W ≥ 3 GeV residual in (c) is consistent with zero at 2 SE and differs from (a) by more than 2 SE; to the
     estimator if (c) is consistent with (a)". The session sets the exact rule; it may not change it after any result.
   - the compute cap.

   The director binds the declaration on notification. A run started before binding is held, not used.
2. **Compute:**
   - at most **0.5 node-h** in total, against the estimate of 0.1–0.2;
   - each job under 12 h;
   - regular QOS only, never premium;
   - Joseph's own share of `m3246` (DECISION-20261019 §1 reading);
   - ledgered as the measurement session's other jobs are;
   - **outputs on `$PSCRATCH`, not CFS** (Joseph's rule: CFS under 3 TB; it was at 3.6 TB).
3. **Records.** All records go under `docs/orchestration/state/ki98-wbias-test/`:
   - the declaration;
   - the job ids;
   - the receipts;
   - a REPORT.md with the measured numbers and which branch of the rule they meet.

   The session does not edit `state/2d-closeout/**`, KNOWN_ISSUES, the paper or the note. The director integrates
   the outcome into those.
4. **No outward act.** No claim change. The result goes to the director, who reports it to Joseph.

## Status

Assigned 2026-10-22. Perlmutter availability is the measurement session's to check before submitting: at 02:01 PDT
10-22 it reported 546 nodes down and 63 mixed.
