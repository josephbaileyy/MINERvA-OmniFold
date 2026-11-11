# DECISION 2026-11-11 — Joseph: the playlist 1A AnaTuples are copied to m3246's CFS space, under his PI's authorization

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The at-risk record** (`state/measurement-paper/5d-community-20261024/fd/retention-20261110/AT-RISK.md`, PR #1048)
  found that our playlist 1A AnaTuples on pscratch (253 data files, 80.6 GB; 41 MC files, 706.9 GB; 787,539,272,045 B in
  total) cannot be replaced from the public release. The release's 1A is a later reprocessing of the same events
  (`data-survey-20261022/SURVEY.md:34-37`). Every product so far, the 2D benchmark included, was built from our copy.
  The files are exposed to purge from 2026-12-15 (data) and 2026-12-19 (MC).
- **HPSS** has about 62.7 GB free (Joseph, 2026-11-11: 449.3 GB of 512 GB used). The small and medium at-risk inputs
  are archived there (`hpss-20261111/`, PR #1054); 1A does not fit.
- **The director noted** that m3246's CFS is the PI's shared project space. A copy of about 0.8 TB there would be the
  PI's to authorize (memory: do not claim a shared group resource without the PI). The director offered a read-only
  quota check first.

## Joseph's answers, verbatim

> wait could I not store the 1A anatuples on CFS?

(sha256 of the text plus a final newline begins `3fed9ffde88e84be`), and then:

> lets just add it to CFS, he's given me authorization to store things there

(`bdbed0e367dd2028`). "He" is the PI, Ben Nachman. The authorization is as Joseph reports it. It is not recorded
here from Ben directly.

## What is decided

1. **The 1A AnaTuples are copied to m3246's CFS space**, under `/global/cfs/cdirs/m3246/josephrb/`, the existing
   per-user directory that already holds the PRD release preservation copy (`FD-CT-RETENTION.md:32`). The target is a
   new directory named for this copy. pscratch is not deleted.
2. **The copy follows the HPSS archive's discipline:**
   - a read-only CFS quota check first, which must show room for the copy plus a margin;
   - each source read by O_NOATIME, so pscratch atimes do not move, with its size and mtime checked against
     AT-RISK's stat;
   - each written file's sha256 equal to the source bytes', verified by re-reading the CFS copy;
   - a manifest committed as the receipt;
   - run from a login or data-transfer node, never inside a Slurm job;
   - any failure STOPs, and nothing is overwritten or deleted.
   Each script goes to the director with its sha256 before it runs.
3. **The deadline:** the copy completes well before 2026-12-15.
4. **The 2D per-playlist universe files** (171 GB, exposed from 2026-12-09) are not part of this decision. They can be
   regenerated.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the copy's authorization and its conditions.
- **Not citable for:** the PI's authorization in his own words, or any change to an analysis input. The CFS copy is a
  preservation copy of the same bytes.

Nothing is submitted, deposited or tagged.

## Correction (director, 2026-11-11, after the decision): the copy already exists, and no new copy is made

This decision rested on the at-risk record's account, which did not search for existing copies of 1A
(`AT-RISK.md`: "Every other group's copies were not checked"). The valid-region lane then found, in committed records,
that all 294 1A AnaTuples already have sha256-verified copies in m3246's CFS:
- **data (253):** in `prd-release-preservation-20261008/anatuple-data-20261009/`, verified 2026-10-09
  (`docs/publication/corrections-20261008/RECORD-20261009-anatuple-data-cfs-copy.md`);
- **MC (41):** in `mc-1A-preservation-20261014/`, verified on dtn01 2026-10-15 on Joseph's "yes you can copy them"
  (`state/2d-closeout/preservation-20261014/cfs-copy-1A-mc/REPORT.md`).
A local cross-check matched all 294 by size and mtime to the pscratch files. A stat-only check from dtn01 on 2026-11-11
then found all 294 CFS copies present, with size and mtime equal to the manifest
(`fd/retention-20261110/cfs-1a-check-20261111/`, PR #1057).

**So item 2's copy is not made.** No copy script was written or run. The preservation goal of item 1 is already met
by the October copies. A second copy would add 0.79 TB of duplicate bytes to the shared space. Items 3 and 4 stand as
written. The data copy is mode 640, readable only by Joseph's own group; making it group-readable is Joseph's call, as
the 10-09 record says.
