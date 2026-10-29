# RECORD — MANIFEST-overrides.tsv sorted once; unsorted rows now refused (2026-10-28)

The director ruled on 2026-10-28 to do this after `note/n4-front-matter-20261028` (#480) merged.
It fixes the residual collision left by #464: every change that added a document appended its
overrides row at the file's last line, so two concurrent changes collided there (seen on #466,
#468 and #474).

## The reorder, proved to be only a reorder

At `55c270173`, `docs/orchestration/MANIFEST-overrides.tsv` holds a header and 1,050 rows, with no
repeated path. The header is unchanged, and the rows are sorted by path in byte order
(`LC_ALL=C sort`), each line kept byte for byte.

| check | before | after |
|---|---|---|
| bytes | 89,466 | 89,466 |
| rows | 1,050 | 1,050 |
| sha256 of the multiset of lines (each line kept whole, then sorted) | `a38ee16e37db99f0…` | `a38ee16e37db99f0…` |
| row multiset equal (`Counter`) | — | **True** |
| paths strictly increasing | no | **yes** |

The committed file then gains exactly **one** row beyond the reorder: this record's own,
inserted at its sorted position, making 1,051 rows. Every other line is one of the 1,050 above.

One `MANIFEST.tsv` cell moves: the overrides file's own `campaign`. That column is derived from the
first `…-campaign` token in a file's text, so a reorder changes it
(`20260919-cause3-two-member-campaign` → `20260922-pet-improvement-campaign`). No classification
moves.

## The check

`generate_manifest.py` `load_overrides()` now refuses rows that are not in strictly increasing path
order, through `override_order_problem()`. The error names the two lines and says to insert each
row at its sorted position, never at the end. Because every reader of the overrides goes through
`load_overrides()`, regeneration and CI's `--check` both refuse an unsorted file.

**Both directions:**
- `--self-test` gains four cases: a sorted list passes, while an out-of-order pair and a repeat
  both fire.
- `test_object_identity_checks.py` gains a test in a throwaway repository: the reversed file exits
  2 with "must be sorted by path", and the sorted file passes. Its fixtures now insert rows in
  sorted order. All 12 tests pass.
- On the unsorted file at `55c270173`, the new code fires
  (`line 3 … AMENDMENT-20260831-… sorts before line 2 … CAMPAIGN-REVIEW-20260929.md`).

## Open branches that touch the file, and the one-step rebase

Measured with `git diff <merge-base> <branch> -- docs/orchestration/MANIFEST-overrides.tsv` over every
unmerged remote branch:

- `fd/ct-readers-report` (#485) and `fd/ct-5b-inputs` (#481): the coverage session, live;
- `closeout/stage-a-selective-io-20261012-reviewed` and `salvage-pet-gate6-preservation-20260903`:
  old, with no open PR.

To resolve the conflict, keep `main`'s sorted file, add the branch's own new rows, and sort again:

    git checkout origin/main -- docs/orchestration/MANIFEST-overrides.tsv
    # append the branch's rows, then:
    python3 -c "p='docs/orchestration/MANIFEST-overrides.tsv';h,*r=open(p).read().splitlines();open(p,'w').write('\n'.join([h]+sorted(set(r),key=lambda x:x.split('\t')[0]))+'\n')"

After that, `generate_manifest.py --committed-only` regenerates as usual.
