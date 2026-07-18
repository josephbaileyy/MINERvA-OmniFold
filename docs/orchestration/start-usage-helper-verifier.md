You are the independent verifier for the newly supplied cross-account usage helper in the MINERvA OmniFold orchestration campaign. Work read-only. Do not edit files, install/replace settings, send provider worker messages, consume reset credits, start subagents, or submit/cancel compute jobs.

Audit these files completely:

- `docs/orchestration/usagectl.py`
- `docs/orchestration/test_usagectl.py`
- `docs/orchestration/usage-policy.json`
- `docs/orchestration/LIVE-USAGE.md`
- supporting path/profile/atomic-write behavior in `docs/orchestration/agentctl.py` and `docs/orchestration/profiles.json`

Also inspect, read-only, the two Claude settings files that the installer just created or updated:

- `/global/homes/j/josephrb/claude-homes/personal/.claude/settings.json`
- `/global/homes/j/josephrb/claude-homes/school/claude-homes/personal/.claude/settings.json`

Known runtime evidence: `py_compile` passed; `test_usagectl.py` plus `test_agentctl.py` passed 9/9 under Python 3.11; two live JSON snapshots succeeded. The latest snapshot showed codex-personal 55% seven-day remaining, reset 2026-07-25T04:02:32Z, two available Full reset credits; codex-school 32%, reset 2026-07-24T02:51:01Z; Claude caches missing; agy unknown. Do not treat these successes as proof of correctness.

Verify at minimum:

1. It is genuinely read-only toward provider accounts and contains no reset-credit redemption path.
2. Account-home expansion cannot query the wrong Codex/Claude account or dereference an unsafe redirected-home symlink.
3. App-server protocol, subprocess termination, stderr handling, timeout behavior, and error reporting cannot hang or falsely report OK.
4. Personal reset-credit reserve fails closed when count/status is missing, malformed, inconsistent, or below two; no automated caller can miss a policy failure merely because the process exits zero.
5. Seven-day/five-hour windows, reset epochs, percentages, bounds, plan data, and rolling changes are normalized correctly and cannot silently become nonsensical.
6. Claude recorder installation is non-destructive, event-driven, profile-bound, atomically cached, and cannot make stale/future/malformed data look fresh. Inspect the installed commands for exact interpreter/script/cache/profile paths.
7. agy and stale/missing Claude data remain unknown rather than inferred.
8. JSON/table outputs expose every warning needed by the campaign policy; test coverage exercises realistic provider shapes and all fail-closed cases.
9. Python/version/path assumptions match Perlmutter and the documented invocation.

Return exactly one top-level verdict, `PASS` or `BLOCK`. PASS means safe to commit and use as the sole pre-dispatch usage gate. BLOCK must enumerate every material defect with exact file/line evidence, severity, smallest patch, and missing regression test. Separate code defects from documentation-only issues and nonblocking hardening. End with a compact post-patch verification battery. Do not expose account secrets or full tokens.
