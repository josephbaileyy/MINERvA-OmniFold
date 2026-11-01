# DECISION 2026-11-01 — Joseph: reopen 1B as an investigation of gate D; compute approved for resolving limitations

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- Joseph asked whether a fully validated measurement with clean results is possible, and for a physics referee review.
- Two blind referee reports and a read-only qualifications inventory were taken
  ([`state/2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/REPORT.md`](state/2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/REPORT.md)).
  Both referees prefer that the limitations be resolved, not moved to the note.
- Joseph also shared another agent's reading. It recommended a bounded investigation of the covariance and
  pseudo-experiment mismatch before any large coverage ensemble.
- 1B had stopped under its bound fork: gate D FAIL (`FD-1B-STAGE2-REPORT.md` §4.1) and the diagnosis NOT LOCALIZED
  (`FD-1B-DIAG-REPORT.md`, #634). The director told Joseph that reopening it was his decision.

Joseph's words, verbatim, in his own message:

> I asked another agent and it also said this about the paper, can we look into these things? Do you want me to slash clear one of the open sessions or start a new one?

sha256 of the text plus a final newline begins `6c33dcf974d7ec44`.

Then, after the director's view of 1B:

> yes lets reopen it, in general I approve of any compute needed that would resolve limitations of our research

sha256 of the text plus a final newline begins `98044f862e4e5114`.

## What is decided

1. **1B is reopened as an investigation of gate D's mismatch.** This supersedes the "1B stops" branch of
   `FD-1B-DIAG-DECLARATION.md` §4 for this purpose only. Gate D's readout, the diagnosis and their verdicts stand
   as recorded.
   - **The question:** do the systematic-universe covariance (S1's blocks) and the pseudo-experiments propagate the
     same uncertainty through the same estimator? Where they differ, which of them is wrong?
   - **Where to look first:** the interaction group. Its per-cell σ ratio has median 1.659 and range 0.418–6.521,
     against 0.996 for flux and 0.973 for detector (`FD-1B-STAGE2-REPORT.md` §4.1).
   - **Candidate mechanisms, none of them measured:**
     - the prior-versus-response gap the 1B declaration anticipated, which in most cells now needs the opposite sign;
     - estimator noise of the size of the reported rounding instability, acting on bands with two universes each.
     A declaration may add others.
   - **Allowed outcomes, fixed before any new number is read:**
     - the pseudo-experiment design must change;
     - the covariance must change;
     - the estimator must be stabilised;
     - unresolved.
     Each outcome is a finding. None of them is a coverage result.
   - **Forbidden:** changing the pseudo-experiments, the covariance or the window in order to make gate D pass. Any
     change must follow from a finding, and a coverage ensemble needs its own declaration and binding.
   - **Owners:**
     - coverage-5b declares and runs the investigation;
     - the director binds it before anything runs;
     - coverage-5b-audit reviews the declaration and the report.
2. **Compute.** Compute needed to resolve a limitation of the research is approved. Each campaign is still declared,
   priced and bound before it runs, and its report gives the cost measured.
   - **The director's reading, which Joseph may override:**
     - The hardware and storage rules stay in force: CPU only, jobs under 12 h, regular QOS, nothing written to CFS.
       This approval names an amount of compute, not those rules.
     - The node-hours are the group's allocation, shared with others. The last balance recorded was 2,074.5 node-h
       remaining. A single campaign priced above half of the remaining group balance comes back to Joseph with its
       price before it is bound.

## Not decided here

- Whether the paper stays a measurement or is recast as a methods study.
- Any claim, number or abstract wording.
- The other limitations' work items. They are planned from the inventory and declared one by one.
- Retention of the per-playlist event-loop files. Joseph's 11-01 choice to let them age out stands unless he
  changes it.

Nothing is submitted, deposited or tagged.
