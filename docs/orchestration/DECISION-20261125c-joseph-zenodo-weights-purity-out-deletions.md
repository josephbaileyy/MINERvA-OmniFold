# DECISION 2026-11-25 (c) — Joseph: all weight files on Zenodo in the same release, the five-axis purity weights left out, and two deletions

**Recorded by** the director. It adds to `DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md` (#1326) and
`DECISION-20261125b-joseph-5d-unbinned-release-cinfl-naming-wording.md` (#1338). Joseph gave every item below
directly to the director, in the director's session, on 2026-11-25 (Pacific), answering the director's list of open
decisions. Quoted words are Joseph's.

## 1. Hosting: every weight file on Zenodo, in the same release

The director asked where the weight files should be hosted (about 3 GB in all; the 5D per-event `weights.npz` alone is
about 1.74 GB), on Zenodo with the release or elsewhere. Joseph: "yes can we do them all on zenodo on the same
release?" The 2D central weights (EVW2D) and the 5D central weights (EVW5D) go into the same Zenodo release as the
rest of the deposit. Joseph publishes Zenodo after Ben approves. No lane deposits, uploads or tags anything.

## 2. The five-axis purity weights are left out of v1

The five-axis purity-product weights (configuration (a)) do not reproduce their result (median mismatch 0.58 %),
while configuration (e)'s sixteen-cell weights do. Joseph: "we can leave the purity weights out." v1 releases no
per-event weights for configuration (a).

## 3. Attempt 1's scratch namespace may be deleted

EVW5D's attempt 1 ended at a false STOP before its job started (`fd/evw5d-20261125/EVW5D-BINDING-2.md`). Its namespace
`/pscratch/sd/j/josephrb/evw5d-20261125` holds two clones and logs, and the logs are committed in
`fd/evw5d-20261125/receipts/attempt1/`. Joseph: "yes we can delete it." The director assigns the removal to ibu-chi:
that exact path only, after attempt 2's fetch, with a listing before and the absence after as a receipt.

## 4. The 1B branch is deleted

`decl/1b-staged-a2-1-20261103` was preserved by Joseph's annotated tag `evidence/1b-staged-a2-1-20261103` (tag
6b3769c9, commit 342c0ce5). Joseph: "yes we can delete it." The director checked that the branch tip equals the tag's
commit, then deleted the remote branch on 2026-11-25. The tag remains on origin.

**CITABLE FOR:** what Joseph decided, and when. **NOT CITABLE FOR:** any number, or any note wording.
