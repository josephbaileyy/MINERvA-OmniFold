Resume your independent publication-redteam context. Your first pass found a
real contradiction within docs/OPEN_ITEMS.md: the early full-event/FPS gate
quarantines recoil-only PET inputs, while the later legacy capstone block still
describes those products as active and proposes partial/frozen retraining.

Perform a read-only canonical-control reconciliation across docs/OPEN_ITEMS.md,
KNOWN_ISSUES.md, nd-unfolding/ND_OMNIFOLD_STATUS.md,
nd-unfolding/PET_UQ_REMEDIATION_STATUS.md,
docs/PUBLICATION_COMPLETION_RUNBOOK.md,
docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md, and relevant workstream STATUS files.
Do not edit files or run compute.

Treat the committed runbook/dependency map/PET remediation DAG as the intended
locked publication route only where they agree, and independently flag any
remaining internal contradiction. Produce:

1. an exact line-by-line inventory of stale or contradictory statements;
2. the canonical destination for each fact under AGENTS.md's one-home rule;
3. minimal proposed replacement text/hunks that preserve chronology as
   explicitly labeled legacy/control evidence while removing it from the active
   route;
4. a list of any apparently correct uncommitted changes that must not be lost;
5. a PG0 PASS/BLOCK verdict after the hypothetical minimal patch.

Pay special attention to stale claims that scalar FPS purity outputs,
recoil-only PET, frozen-reweighter laterals, non-background-aware 5D products,
or partial-stat ensembles are publication candidates; stale job states; and
untracked/pending-commit claims that conflict with the repository commit gate.
Separate documentation repair from scientific evidence still requiring future
compute. Keep the answer compact but give exact paths and line numbers.
