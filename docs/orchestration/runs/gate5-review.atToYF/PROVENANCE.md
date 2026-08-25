# `gate5-review.atToYF` — surviving artifact

## `repair.py` — citable as METHOD, not as outcome

2030 bytes, md5 `ae7eb53dd3e0e3c82ca43a0f13d61f9b`, blob `def3e3239dfedd99d53d9b1e1884049a733d646f`.

A one-shot in-place patch script: it reads `nd-unfolding/pet/train_fullevent_replica.py`, applies
literal `content.replace(...)` substitutions, and writes it back.

**Why it is preserved when its result is already in git.** The *outcome* is tracked —
`coherent_bootstrap_factors` appears in that file on pushed `main`, introduced by commit
`56d35afb` ("gate5: persist full coherent signal factors"), and the old strings this script
matched on are recoverable from that commit's diff. What is **not** anywhere in git is the
*method*: that the change was applied mechanically by string substitution rather than by hand, in
this order, with these exact match strings. **Method is a distinct artifact from outcome**, and
its bytes are in no commit — which is the admission test recorded in
`../retired-worktree-archive-20260824/PROVENANCE.md`.

No citability warning is needed here: nothing could mistake a patch script for a receipt.

**Its sibling was correctly not preserved.** `gate5_diff.txt` (51,841 B) from this same worktree
**is** regenerable — it is `git show 670e62df` output, 1,152 lines against 1,152, with all 14
differing lines being index-abbreviation width (seven index lines × two hashes × one character).
Regenerating it today yields 8-hex where the archive had 7-hex; that is a `core.abbrev`
difference, **not corruption**.
