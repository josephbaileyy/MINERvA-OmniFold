> **RESOLVED 2026-09-23 — superseded.** The `20260922T053047Z` token is replaced by
> `runs/standard-p4-verifier/20260924T010110Z-known-issues-51-61-62-verdict.json` (PASS, code_rev `036f507e`, landed `5ee482e9`).
> The defect below stays in the old token's immutable bytes, which no longer authorize anything.

# ISSUE-68 — The same PASS token mis-attributes a ratio in its uqmath.py per-file summary

**Severity:** MEDIUM. **Status:** RESOLVED (2026-09-23). **Index row:** `KNOWN_ISSUES.md` row 68. **Updated:** 2026-09-22.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

The token says *"`4.69x/4.83x` were the 122-throw re-roll"*. **`4.83×` was; `4.69×` was not.** `VALIDATION_LEDGER` VL32–VL34: `VL32` = full-160 **pre**-J28 = `4.6912×`; `VL34` = the **122-throw** morning re-roll = `4.8288×`; `VL33` = full-160 post-J28 adopted = `5.3478×`. The ledger says so in the singular (*"`4.83×` does not come from the adopted ensemble: it is the 122-throw morning re-roll"*), and **the code comment the token was summarising is correct** — only the token's summary of it is wrong. The verdict is unaffected (`uq_math.py` is COMMENT ONLY: 6 insertions, 1 deletion, all comment, `git diff a8f7b2f0 3035f8b8 -- nd-unfolding/uq_math.py`). **NOT REPAIRABLE** for the same reason as row 67.
