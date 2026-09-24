> **RESOLVED 2026-09-23 — superseded.** The `20260922T053047Z` token is replaced by
> `runs/standard-p4-verifier/20260924T010110Z-known-issues-51-61-62-verdict.json` (PASS, code_rev `036f507e`, landed `5ee482e9`).
> The defect below stays in the old token's immutable bytes, which no longer authorize anything.

# ISSUE-63 — The 20260922T053047Z verifier PASS token contains a present-tense pointer to KNOWNISSUES rows that did not exist at its own coderev, and its fileschangedinscope counts the derived surface rather than its own declared scope. Neither is repairable: the token IS the sha256 of those bytes

**Severity:** MEDIUM. **Status:** RESOLVED (2026-09-23). **Index row:** `KNOWN_ISSUES.md` row 63. **Updated:** 2026-09-22.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

**MEASURED 2026-09-22 by an independent adversarial review.** (1) The verdict says the offset-0 convention defect is *"RECORDED IN KNOWN_ISSUES.md"* and that the `_shell_invoked_scripts` gap *"is RECORDED in KNOWN_ISSUES.md"*. At its `code_rev` `3035f8b8` and at the commit that minted it (`384c2eb1`) `KNOWN_ISSUES.md` is blob `39b69776…` with rows `5–11, 16, 17, 19–21, 23–60` and **zero** matches for `_shell_invoked_scripts`. Rows **61 and 62** were added three commits later at `9e78a8cf`, which is where those pointers resolve. (2) The verdict records `files_changed_in_scope: 13 / insertions: 1758`; measured over its own 23-path `review_scope` the figure is **14 files / 1988 insertions**, the 14th being `nd-unfolding/lib_member_resume.sh` (status `A`, +230/−0) — the very file the verdict added to scope, and it has no `per_file` entry. **Neither defect changes the PASS**: the added file is new, so *"additive or restrictive"* survives, and the token still resolves `TOKEN-OK`. **CHECK:** read that verdict's `files_changed_in_scope` as *on the derived surface*, and read its KNOWN_ISSUES pointers as satisfied at `9e78a8cf`, not at its `code_rev`. **NOT REPAIRABLE:** editing the verdict changes its sha256 and therefore invalidates the token it is.
