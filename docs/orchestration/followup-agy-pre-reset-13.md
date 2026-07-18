# Pre-reset A/C/B repair-wave audit

You are the existing `agy-publication-redteam` persistent reviewer. This is a
read-only preflight; preserve role continuity and do not edit files, dispatch
workers, launch Slurm, or claim scientific production.

Audit the three queued school-account prompts against the current repository
and the latest independent-verifier findings:

- `docs/orchestration/followup-agent-A-standard-04.md`
- `docs/orchestration/followup-agent-C-fps-03.md`
- `docs/orchestration/followup-agent-B-p5b-03.md`
- `docs/orchestration/MIGRATION-TAKEOVER-STATUS.md`
- the latest relevant A/C/B and verifier receipts named in
  `docs/orchestration/RUNS.tsv`

For each A, C, and B, report:

1. whether the queued prompt covers every still-open verifier blocker;
2. any instruction that conflicts with current code ownership, the commit
   gate, negweight/F7 ordering, or the no-runtime/no-production boundary;
3. any missing negative test, artifact-binding requirement, or atomicity check
   that can be added now to avoid another wasted constrained-provider turn;
4. an exact minimal prompt amendment, if needed.

Do not re-litigate already closed decisions and do not substitute for the
named continuity-bound verifiers. End with one of `WAVE-PREFLIGHT PASS` or
`WAVE-PREFLIGHT AMEND`, followed by a compact A/C/B checklist.
