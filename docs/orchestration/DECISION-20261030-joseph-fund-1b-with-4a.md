# DECISION 2026-10-30 (later) — Joseph: fund 1B, the coverage test, with 4A

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The coverage cheap tier has reported: 3a and 4C in `FD-CT-READERS-REPORT.md`, 5A in
`FD-CT-READERS-5A-REPORT.md`, 3b in `FD-CT-3B-REPORT.md` and 5B in `FD-CT-5B-REPORT.md`.
`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md` item 3 left 1B and 4B to be decided after that. An
independent synthesis
([`state/2d-closeout/stageF/methods/secondary-results/astra-consult-cheap-tier-20261030/REPORT.md`](state/2d-closeout/stageF/methods/secondary-results/astra-consult-cheap-tier-20261030/REPORT.md),
#537) recommended funding 1B with 4A and not funding 4B now.

The director asked three questions. This record covers the first, which Joseph answered. He asked for the
recommendation on 4B and an explanation of the 5B question. Those are recorded when he answers.

> Fund 1B (the coverage test) with 4A, at about 44.5–145 CPU node-hours on Perlmutter (22.5 production), declared and bound as usual?

Joseph's answer, verbatim:

> Fund it (Recommended)

sha256 of the text plus a final newline begins `23c5f08364975189`.

## What is decided

1. **1B runs with 4A,** as `LIMITATION-PLAN-ADDENDUM-20261028.md` scopes them. The option offered read: "Declared and
   bound in stages; the nominal control must pass before the production toys run. Every job under 12 h, CPU only."
   - The estimate is 44.5–145 CPU node-h on Perlmutter, 22.5 of them production. Each stage's binding sets its own
     ceiling, and the total stays inside that range.
   - A measurement session declares it, and the director binds each stage.
   - The nominal control comes first. Its failure is a STOP, and no production toys run.
2. **The report states** per-cell coverage with its standard error, the nominal-response scope, and what a pass means:
   "no undercoverage detected at the study's sensitivity". Under-coverage, if measured, is reported as measured.
3. **Under the standing approval for jobs under 12 h:** no GPU, no premium QOS, nothing to CFS.

## Not changed

- The reported covariance, every claim and number. Nothing is submitted, deposited or tagged.
- 4B and the 5B block are not decided here.
