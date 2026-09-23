# ISSUE-65 — The tree already owns an instrument for did this withdrawal reach every site, and the 2026-09-21 seed-effect withdrawal was never registered in it — so the assurance published in its place is not re-runnable by the next lane

**Severity:** MEDIUM. **Status:** OPEN. **Index row:** `KNOWN_ISSUES.md` row 65. **Updated:** 2026-09-22.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

**MEASURED 2026-09-22 by an independent adversarial review.** `docs/orchestration/state/check-withdrawal-completeness-20260910.py` is a pinned per-file inventory of withdrawn claims that discovers unregistered files and fails closed on any count change; `--self-test` returns **exit 0, SELF-TEST PASSED**, so it is live. Its docstring names, among the four failures it was built for, *"a line-oriented `grep` acquitted it, because the survivor was line-wrapped"* and a stale `CATALOG.md` router entry — **which is exactly site 10**. Its `WITHDRAWN` table holds 8 claims and none is the *larger ensemble* corollary; no script in the tree matches that claim's wordings and nothing references `CORRECTION-20260921-seed-effect`. Instead `CORRECTION-20260921…` §4d publishes a standing set — *"ZERO live assertions"* — that no committed artifact reproduces, so checking it requires rebuilding a sweep by hand. **Registering the claim in the existing checker would have caught site 10 by content and would make the assurance re-runnable.** ⚠ **Pre-existing, NOT caused by this:** the checker currently exits 1 on two UNREGISTERED FILE discrepancies (`RECHECK-20260918-null-per-bin-distribution.md`, `REVIEW-20260910-z-acceptance-criteria-independent-derivation.md`); those files and the checker are untouched by `3035f8b8..a7e469d7`. **NOT REPAIRED:** registering a claim while the checker is red would bury the new row in a pre-existing failure.
