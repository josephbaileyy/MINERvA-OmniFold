# PG0 ownership recheck: untracked dependency and proof strength

Continue the same PG0 audit in the exact `agy-publication-redteam` session.
Your prior `PG0-OWNERSHIP PASS` is not yet accepted. Work read-only.

Independent evidence:

- `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md` and
  `docs/PUBLICATION_COMPLETION_RUNBOOK.md` are tracked now;
- `docs/POST_PUBLICATION_REORG_PLAN.md` exists but is untracked;
- dirty `docs/OPEN_ITEMS.md` and `nd-unfolding/ND_OMNIFOLD_STATUS.md` add links
  to that untracked plan;
- committing only your recommended three canonical files would therefore
  create a broken Git/GitHub link;
- `MIG-PUB-AUDIT1` proves the control audit found/created policy artifacts but
  does not by itself prove authorship of every later uncommitted hunk.

Re-evaluate at hunk and artifact level. Determine, with direct evidence:

1. whether the untracked reorganization plan has a durable owner/receipt and is
   safe and necessary to land now;
2. whether the two canonical links should instead remain uncommitted or be
   omitted while preserving the untracked plan untouched;
3. whether each recommended canonical hunk has sufficiently strong provenance
   to stage without absorbing another owner's work;
4. the exact minimal file/hunk set that closes PG0 without broken references or
   data loss, including any required runbook/status/ledger receipt;
5. whether the FrInel_pi source-trace hunk really has ownership evidence, not
   merely plausible scientific content.

Do not recommend `git add` of a whole dirty file unless every hunk and every
new reference has been audited. Return `PG0-RECHECK PASS` only with a complete,
internally closed commit packet; otherwise `PG0-RECHECK BLOCK` and the precise
owner evidence still required.
