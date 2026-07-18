Resume your independent red-team context for a focused read-only review of the
current uncommitted usage-helper alias patch. Do not edit files or run provider
workers. The user clarified that `claude-school` and
`claude-school-legacy` authenticate the same provider account even though their
homes/caches are distinct.

Inspect the working-tree changes to orchestration/usagectl.py,
orchestration/usage-policy.json, orchestration/test_usagectl.py, and
docs/orchestration/LIVE-USAGE.md. The intended semantics are:

- both profile caches remain independently integrity/freshness checked;
- one top-level `accounts.claude-school` capacity view selects the freshest
  valid observation independently per window;
- the aliases are marked shared and are never summed or treated as separate
  entitlements;
- a missing flat cache can fall back to fresh legacy cache;
- the existing fail-closed Codex reserve gate is unchanged;
- malformed alias policy/member/provider data fails safely;
- stale/missing Claude windows remain unknown.

The documented test command currently reports 35/35 PASS, and a live snapshot
shows one consolidated account at 85% used / 15% remaining from the fresher
flat cache, reset 18:00 UTC, while retaining the older legacy row only as an
alias observation.

Return PASS or BLOCK first. Challenge temporal edge cases: reset boundaries,
newer observations with lower usage, equal-timestamp disagreement, partial
windows split across aliases, stale fallback, policy schema, JSON/table
clarity, state/change tracking, and any route that could double-count or hide
capacity. For BLOCK give the smallest exact code/test/doc repairs. Do not
review unrelated dirty files.
