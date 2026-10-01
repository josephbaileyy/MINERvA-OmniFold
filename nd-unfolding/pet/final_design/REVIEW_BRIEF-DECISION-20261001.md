# Review brief — independent read-only review of the terminal decision (fixed 2026-10-01, before coverage scoring)

This brief is a prerequisite of delivery (`HANDOFF-COLDSTART-20260929.md` §10): the terminal decision is not
reported as final until a review run under this brief is dispositioned. Its checks were agreed with the
coordinating Codex session (Joseph's request of 2026-09-30) before any coverage outcome existed; they are not
widened or narrowed after the coverage results are seen.

## Object under review (fixed)

- The **decision commit**: the commit on `pet-final-design-20260925` that adds the terminal `decide.py` output
  (`results/final/decision_final.json`) with the coverage file it used. The reviewer records its full sha and
  reviews nothing newer.
- At that commit: `PROTOCOL-20260925.md` (§6 and Amendments 1–5 plus any later coverage UNBLIND/extension
  amendments), `freeze/EVIDENCE_DECLARATION-20260927.json`, `freeze/COMPLETENESS-*.tsv`,
  `results/final/{evidence,decision}_look1*.json`, `results/final/scored_fb/`, the coverage scores and
  `coverage.py` output, `results/final/b1_dependence_look1.json`, `results/final/population_look1.json`,
  `results/final/population/`, `resources/cost_fb_look1-20260930.json`, `DECISION_RECORD-pet-final-design.md`,
  `REPORT-20260926.md` §6–8 and the deck.

## Reviewer and conduct

- A fresh session with no part in producing the decision, in an isolated git worktree at the decision commit;
  preferably Astra High via Codex (`docs/orchestration/CAMPAIGN-REVIEW-20260929.md` §5), otherwise a fresh
  read-only Claude session. Read-only: no commits, no cluster jobs, no edits; the owner (the orchestrator) writes
  every repair and the disposition.
- Every finding states its operand (file, field or line at the decision commit), a reproduction (command and
  output) or the exact text at issue, its material impact (does it change a verdict, a label, or only wording),
  and the disposition it asks for. A defective gate or label is kept separate from a demonstrated numerical error.
- The reviewer states what it could not verify in its environment (e.g. cluster-only inputs).

## Acceptance checks (each answered PASS / FAIL with evidence)

(a) No "more robust", "superior" or equivalence wording is derived from B2 or from any other contrast that is not
    resolved (overlapping intervals or a non-significant difference establish neither superiority nor equivalence).
(b) B1 is shown with its frozen independence-based verdict **and** the common-panel companion
    (`b1_dependence_look1.json`), with the estimands explicit: the evidence is insufficient to establish a per-unit
    failure probability ≤ 0.10 under within-draw dependence, and this is not presented as showing that it exceeds
    0.10.
(c) The FB population comparison is present for E0–E5 (`population_look1.json`) and for coverage (development tilt
    aggregate and regions; D4c up on E_avail × proton class, `vs_population`), with the limit stated that the other
    17 library cases have no population comparison.
(d) The scope travels with every sentence that names a selected or default design: the B = 6 member-mean estimator
    and interval of §9 as amended (2c.1), inference conditional on the frozen banks, signal-only simulation with no
    background model, generator cases as fixed-response reweightings, PET diagnostic, no publication uncertainty,
    no adoption.
(e) Every verdict word in the decision record, report §6–8, deck and PR #4 body matches `decision_look1.json`,
    `decision_final.json` and the `coverage.py` output (label and number), including "point-decided, statistically
    unresolved" where `statistically_unresolved` is true.

Core checks:

(f) Each look-1 and coverage verdict reproduces from the committed evidence with the committed `decide.py` /
    `coverage.py` (`analysis/run_look1.sh`; the coverage invocation recorded in the decision record).
(g) Blinding order: every final-bank group was scored only after its completeness manifest and its UNBLIND
    amendment were committed (commit order and job submit times); no coverage outcome entered a decision before
    its group was complete.
(h) No frozen rule, finalist, sizing or draw cut changed after a final-bank score of the rows it governs; every
    amendment after Amendment 4 is prospective for the rows it releases.
(i) The terminal outcome follows §6 with its amendments: eligibility (§6.1–6.4 and provenance) before ranking;
    the §6.6 order of 2c.3; the 3a.1 terminal default only where its conditions hold; never SELECTED while a
    decision-set member is pending.

## Budget and stopping

At most **two** review → repair cycles on the decision; after the second the owner records an explicit continue or
stop in the decision record. Findings that change no verdict, label or scope statement are dispositioned in
`REVIEW_DISPOSITION-DECISION-<date>.md` without restarting the review. A repair that changes a verdict re-runs only
checks (e)–(i) on the repaired commit.
