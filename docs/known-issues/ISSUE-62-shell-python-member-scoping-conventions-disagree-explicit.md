# ISSUE-62 — The shell and Python member-scoping conventions disagree at an explicit offset of 0, so MNVESTSEEDOFFSET=0 writes unfolds into a member namespace that the evidence stage then does not read

**Severity:** MEDIUM. **Status:** OPEN. **Index row:** `KNOWN_ISSUES.md` row 62. **Updated:** 2026-09-22.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

**MEASURED 2026-09-22, both implementations run directly.** `lib_member_resume.sh`'s `mr_member_dir` returns the empty string **only when the variable is UNSET**; for a literal `"0"` it passes the canonical-integer regex and returns `member_k000000`, so `_mr_insert` scopes the path. `p4_evidence.py`'s `_member_scope` instead returns the path **unchanged** when `EST_SEED_OFFSET == 0` — while its docstring claims it is *"matching lib_member_resume.sh's `_mr_insert`"*. Measured on `/repo/nd-unfolding/active_universe_5d/standard/unfolds`: offset **unset** → both unchanged (agree); offset **`1200`** → both `…/nd-unfolding/mii/member_k001200/…` (agree); offset **`0`** → shell `…/nd-unfolding/mii/member_k000000/…`, Python **unchanged** (**disagree**). **Consequence:** a run declared at `0` produces ten member unfolds under `mii/member_k000000/` that no downstream stage reads, while `p4_evidence.py` reports on the baseline. **It is a silent no-op, NOT a corruption path** — it cannot overwrite an adopted product, and the baseline-overwrite guard is correctly disabled here only because `mr_prefix` has already redirected the output. **Not reachable by the authorized L2 member (`k=1200`), where the two agree exactly.** **CHECK:** never declare `MNV_EST_SEED_OFFSET=0`; leave it UNSET for baseline. **Fix when authorized:** make `_member_scope` branch on *declared-ness* rather than on the value, matching `mr_member_dir`, or make `mr_require_valid_offset` refuse a literal `0`.
