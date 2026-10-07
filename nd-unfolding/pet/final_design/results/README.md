# final_design/results

Per-run outputs of the PET final-design study, copied here from Perlmutter by `harvest.sh`. The study ends at
[`../DECISION_RECORD-pet-final-design.md`](../DECISION_RECORD-pet-final-design.md).

## Moved off `main` on 2026-10-07 (reorg family A3)

Eight development and sizing directories left `main`: `dev1`, `dev2S`, `dev2Q`, `dev2P`, `dev2L`, `dev2T`, `s3p` and
`s3p_new`. That is 674 files. They were removed unchanged and are preserved at the evidence tag
`evidence/simplification-2026-10-07-fc97eaf9`. The exact paths are listed in
[`docs/POST_PUBLICATION_REORG_A3_PATHS.txt`](../../../../docs/POST_PUBLICATION_REORG_A3_PATHS.txt).

To recover a file without changing the checkout:

    git show evidence/simplification-2026-10-07-fc97eaf9:nd-unfolding/pet/final_design/results/<dir>/<file>

To get a directory back for a rebuild, check out a worktree at the tag:

    git worktree add --detach <path> evidence/simplification-2026-10-07-fc97eaf9

Two of the study's development summaries were built from these directories. Both rebuild from the tag:

- `../dev/DEV_TABLES-20260927.json`, built with `../dev/summarize_dev.py`;
- the S-N2 values in `../dev/SCREENS-20260927.json` for H2S1 and L128S1, built with `../dev/n2_table.py` from `s3p/`.

The rest of the S-N2 values come from `s3n/`, which stays here. The rebuild check and the recovery proofs are in
[`docs/POST_PUBLICATION_REORG_PLAN.md`](../../../../docs/POST_PUBLICATION_REORG_PLAN.md), *Family A3 executed*.
