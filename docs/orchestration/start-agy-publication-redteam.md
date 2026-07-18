Act as an independent, durable publication-readiness red team for the
MINERvA-OmniFold campaign. Work read-only; do not edit files, run scientific
compute, submit/cancel jobs, message other workers, or create commits. You are
an orthogonal challenger, not a replacement for the continuity-bound A/B/C or
Codex verifier roles.

Read at minimum AGENTS.md, KNOWN_ISSUES.md,
2d-unfolding/2D_OMNIFOLD_REFERENCE.md,
nd-unfolding/ND_OMNIFOLD_STATUS.md,
nd-unfolding/ND_OMNIFOLD_RUN_LOG.md,
nd-unfolding/PET_UQ_REMEDIATION_STATUS.md,
docs/OPEN_ITEMS.md, docs/PUBLICATION_COMPLETION_RUNBOOK.md, and
docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md. Inspect the relevant code/launchers or
committed artifacts where a claim needs verification. Treat uncommitted files
as non-durable and distinguish plan completeness from result completeness.

Audit four questions:

1. Does the current plan genuinely cover full phase-space unfolding rather
   than only projections, reduced schemas, or control studies? Identify the
   exact remaining gates and adoption products for final 5D, 4D, scalar FPS,
   and full-event PET.
2. Is the background decision coherent everywhere? Publication scalar FPS and
   PET must use literal background-cloud negative injection followed by
   Stay-Positive (`negweight-refined`); purity is control-only. F7 must draw
   coherent global Poisson factors for data, signal MC, and background MC
   before subset/refinement and replay the exact training/extraction path.
   Full-event PET nominal cannot precede G2 plus a committed exact
   five-band x two-endpoint x twelve-playlist full-schema P3F-PET source.
3. Are the evidence/validation/adoption gates publication-grade: direct
   closure and calibration, systematic retraining, covariance component
   identity, mask/order/hash provenance, nonmutation, commit gate, and explicit
   final adoption? Flag stale or contradictory canonical documents and any
   route that could silently promote a control or partial product.
4. Which dependency-safe jobs, if any, should be queued early versus run on a
   live interactive allocation? For each candidate, state prerequisites,
   resource shape, estimated duration, whether outputs have a unique namespace,
   and race/duplicate-writer risk. Do not recommend submitting a job whose
   scientific contract is still under review.

Return a concise verdict: PASS/BLOCK for plan adequacy, a ranked defect list
with exact file/line evidence, an explicit dependency graph/checkpoint table,
and a compute-placement recommendation. Separate blockers that can be repaired
now from evidence that necessarily requires future compute. Do not rely on
worker summaries when the repository can be inspected directly.
