# DECISION 2026-10-27 — Joseph: run the GENIE v3 bias test (1A) and the flux-correlation bootstrap (3D); keep the fake-data bias as a stated limitation

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The limitation plan (`state/measurement-paper/5d-community-20261024/LIMITATION-PLAN.md`, PR #421) costed
options for the sixteen-cell result's three limitations, under
`DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md` item 2:
- **Coverage:** 1C, 1A (about 0.84–1.25 node-h), 1B (about 45–146 node-h) and 1B′.
- **Bias:** (a), (a′), (b) and (c). (b) cannot cover A7 GiBUU at any κ.
- **Flux:** inherent; option 3D is a bootstrap over the 100 flux universes.

The director recommended 1A, (c) and 3D.

Joseph's answers, verbatim, the options he selected. For coverage:

> 1A: GENIE v3 bias test (Recommended)

sha256 of the text plus a final newline begins `f9a00841d71df4b1`.

For the bias:

> Keep as stated (Recommended)

sha256 of the text plus a final newline begins `22d224c2e14d5358`.

For the flux sensitivity:

> Yes, run 3D (Recommended)

sha256 of the text plus a final newline begins `1b499db0bd29da62`.

## What is decided

1. **1A runs: the GENIE v3 bias test,** F1 at a held-out truth. Joseph's earlier "skip F1 for now"
   (`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` item 3) is lifted for this test only.
   - **It is a bias test, not a coverage test:** Poisson-only pseudo-data cannot test interval width. The paper says so.
   - **How it runs:** the 5D measurement session declares it, the director binds it, and it then runs under the
     standing approval for jobs under 12 h. The plan prices it at about 0.84–1.25 node-h. No GPU and no premium QOS.
   - **Its grading** follows FD-PLAN's statistics and triggers. These are declared before any F1 product is read.
2. **The fake-data bias stays a stated limitation (c).** No non-closure or generator-shape term is added, and the
   reported covariance is unchanged.
3. **3D runs: a bootstrap of the flux correlations over the 100 universes.**
   - **It replaces the α = 0.1 weakening** in the paper's sensitivity sentence with a measured band, once it reports
     and the sentence's new form has passed the PRD read and the truth column.
   - **How it runs:** declared, then bound, on a login node at 0 node-h.
4. **1B and 1B′ are not run now.** They can be revisited after the review with Ben.
5. **The limitation sentences** in the paper and the note are revised from the results of 1A and 3D. Their final
   wording comes to Joseph with the final draft.
   <!-- absence-ok: the record's own scope (1B and 1B′ not run, the test not a coverage test), as decided; no claim that a result is absent from the repository -->

## Not changed

- No cell merges or new cuts after the data read (`FD-DIRECTOR-RULINGS.md`). κ = 1.
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
