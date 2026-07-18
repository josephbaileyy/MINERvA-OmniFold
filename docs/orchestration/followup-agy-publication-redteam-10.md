READ-ONLY audit the committed reset/usage routing in `135a07f`, focusing on
`docs/orchestration/resume_after_school_reset_1800.sh`, `LIVE-USAGE.md`,
`usage-policy.json`, `usagectl.py`, `profiles.json`, and the A/C/B prompt paths.
Do not edit, dispatch, run a heartbeat, alter the watcher process, or touch
Slurm/workers.

Check the script against the user's latest rules:

- every substantial A/C/B turn gets a complete unfiltered snapshot first;
- stale Claude percentage is unknown, not a cap;
- when unknown, a tiny disposable heartbeat uses corrected `claude-school`
  flat HOME, never the migrated legacy A/B/C UUIDs or nested home;
- heartbeat success is availability evidence only and invents no percentage;
- heartbeat/provider failure records output, immediately runs a complete
  post-error snapshot, stops the wave, and preserves exact roles;
- known fresh shared-account percentages come only from
  `accounts.claude-school`, never alias addition, and enforce reserves;
- A→C→B ordering is sequential and uses `agentctl.py send --role` only;
- no raw persistent-worker shortcut, replacement, duplicate process, compute,
  or reset-credit action is possible;
- the one August-12 personal Codex credit remains protected after the explicitly
  authorized July-31 reset, and the helper gate remains fail-closed;
- shell error handling, return-code capture, temp/lock behavior, and the detached
  currently armed execution are logically safe.

Return PASS or BLOCK before the 18:00 trigger. If BLOCK, provide an exact minimal
patch and explain whether the live PID must be rearmed. Distinguish harmless
logging/style issues from a routing or provider-safety defect.
