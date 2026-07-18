# PG0 dirty-canonical ownership and contradiction audit

Continue the exact existing `agy-publication-redteam` session. Work read-only:
do not edit, stage, commit, revert, delete, dispatch, or launch compute.

The publication-control gate PG0 is blocked because canonical files including
`docs/OPEN_ITEMS.md`, `KNOWN_ISSUES.md`, and
`nd-unfolding/ND_OMNIFOLD_STATUS.md` have uncommitted hunks from concurrent or
unknown owners. Audit current worktree diffs, Git history/blame, campaign
`RUNS.tsv`, saved worker roles, co-located STATUS/RUN_LOG files, the P0-P8
publication runbook, and `MIGRATION-TAKEOVER-STATUS.md`.

Deliver:

1. A hunk-level ownership map for every dirty canonical file relevant to PG0:
   likely durable role/person, evidence strength, and whether the hunk is
   scientifically current, stale, conflicting, or unrelated.
2. Exact contradictions with current locked gates, especially recoil versus
   full-event PET, purity versus `negweight-refined`, optional versus mandatory
   PET retraining, reduced-schema versus G2 full-schema, and stale closed/open
   item states.
3. A minimal no-data-loss reconciliation packet: exact hunks that can be
   adopted verbatim, exact hunks that need owner confirmation, and exact stale
   statements that should be replaced only after owner authorization.
4. The safest sequencing/role routing so A/C/B post-reset commits do not absorb
   or overwrite unknown work. Prefer co-located receipts until canonical
   ownership is proven.
5. A strict PG0 verdict: what evidence is sufficient to close the canonical
   index/durability blocker, and what remains genuinely blocked.

Do not infer ownership merely from subject matter; cite Git/receipt/file
evidence. Do not clean or normalize the worktree. End with `PG0-OWNERSHIP PASS`
if an actionable no-data-loss map is complete, or `PG0-OWNERSHIP BLOCK` with
the missing provenance.
