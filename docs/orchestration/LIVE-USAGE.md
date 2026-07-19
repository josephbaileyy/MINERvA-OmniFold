# Live cross-account usage for the orchestrator

Use `usagectl.py` as the sole machine-readable usage check. It reads both
Codex accounts live, reads timestamped Claude status-line caches, and reports
agy as unknown because the installed agy CLI has no usage endpoint.

`claude-school` and `claude-school-legacy` are two homes for the same provider
account. The JSON `accounts.claude-school` record is the routing authority: it
selects the freshest valid cache independently for each window and marks both
profile rows as shared capacity. Never add or otherwise treat the two profile
percentages as independent entitlements. Equal-timestamp disagreements choose
the higher used percentage, and rolling changes are recorded from the shared
account view rather than by adding alias observations.

## Hard policy

- Preserve the **one remaining personal Codex Full reset credit** (expires
  2026-08-12) as emergency reserve. The July-31 credit was consumed on
  2026-07-18 only after the user explicitly authorized that specific credit and
  live usage reached 0%.
- Never redeem a reset credit automatically or merely to increase throughput.
- Record the personal Codex seven-day reset time in the campaign ledger after
  every material change.
- Treat stale or missing Claude data as unknown; never infer a percentage from
  the number of recent jobs.
- A usage check must not replace or fork any worker session.

The helper has no reset-credit consumption code. It only calls Codex
`account/rateLimits/read`. `usage-policy.json` makes the reserve and warning
threshold explicit. A dispatch-authorizing snapshot has top-level
`"gate_ok": true` and exits zero. Missing, malformed, expired, inconsistent,
or below-reserve personal-credit evidence makes the gate false and exits 3;
configuration/runtime errors exit 2. A filtered `--profile` snapshot is
advisory and cannot pass the dispatch gate.

## Install on Perlmutter

Upload these files into the existing `docs/orchestration` directory:

```bash
cd /Users/josephbailey/new-physics
rsync -av \
  orchestration/usagectl.py \
  orchestration/usage-policy.json \
  orchestration/test_usagectl.py \
  orchestration/LIVE-USAGE.md \
  josephrb@dtn01.nersc.gov:/global/homes/j/josephrb/MINERvA-OmniFold/docs/orchestration/

rsync -avR \
  ./.agents/skills/persistent-orchestrator \
  ./.claude/skills/persistent-orchestrator \
  josephrb@dtn01.nersc.gov:/global/homes/j/josephrb/MINERvA-OmniFold/
```

Then validate on Perlmutter:

```bash
cd /global/homes/j/josephrb/MINERvA-OmniFold
chmod 700 orchestration/usagectl.py
/usr/bin/python3.11 -m py_compile orchestration/usagectl.py
(cd orchestration && /usr/bin/python3.11 -m unittest -v test_usagectl.py test_agentctl.py)
/usr/bin/python3.11 orchestration/usagectl.py snapshot
/usr/bin/python3.11 orchestration/usagectl.py snapshot --json
```

The personal Codex row should report `RESET CREDITS 1`. Its JSON must include
the seven-day `resets_at_utc` and each reset credit's expiry. Stop and tell the
user if `gate_ok` is false or if credit evidence is missing, malformed,
expired, inconsistent, or below one; do not attempt a reset. The Codex
app-server sometimes omits an inactive five-hour window. That is reported as
unknown and is never inferred from the seven-day value.

## Enable Claude snapshots

Claude exposes five-hour and seven-day usage to its interactive status line.
Install the recorder separately in each relevant Claude home:

```bash
/usr/bin/python3.11 orchestration/usagectl.py install-claude-statusline --profile claude-personal
/usr/bin/python3.11 orchestration/usagectl.py install-claude-statusline --profile claude-school-legacy
```

Install `claude-school` after that corrected flat home is authenticated. The
installer refuses to replace an existing custom status line. Inspect the
existing setting first; use `--replace` only if intentionally discarding it.

A cache appears after an interactive Claude session supplies rate-limit data.
The recorder keeps independent observation times per window, preserves the
prior cache on pre-response or malformed status events, and does not advance a
window's freshness when its API-derived values are unchanged. Stale, expired,
invalid, or absent windows expose no actionable percentage. For an on-demand
refresh, start a separate disposable interactive session in the desired
account home, request a tiny exact response, and exit. Do not use or alter the
migrated A/B/C UUIDs merely to refresh usage. Claude windows older than 30
minutes are labeled stale.

## Orchestrator routine

Run before each dispatch wave, after any cap error, and before final synthesis:

```bash
/usr/bin/python3.11 orchestration/usagectl.py snapshot --json
```

Use these routing rules:

1. Prefer live Codex percentages over historical call-count estimates.
2. Reserve enough personal Codex capacity for orchestration and synthesis.
3. Track the exact seven-day reset epoch/UTC time; re-read it because rolling
   windows can move.
4. Keep the remaining August-12 Full reset credit untouched unless the user
   explicitly authorizes that specific credit in a later message.
5. Use Claude percentages only when the cache is fresh; otherwise use a
   status-only availability probe or mark capacity unknown. Route school
   capacity from `accounts.claude-school`, never by summing its two aliases.
6. Treat agy as available/unknown/capped from heartbeat and error evidence,
   never as an invented percentage.
7. Write material usage changes and reset times to the campaign ledger.

A content-free heartbeat proves only that the provider can serve that tiny
request. It does not prove enough spend headroom for a substantial cached Opus
continuation: on 2026-07-19 the Claude-personal heartbeat returned
`HEARTBEAT_OK`, while the immediately following preserved E turn hit the
monthly spend limit. Treat the substantial turn's explicit cap as
authoritative and preserve its UUID.

Claude's user-visible percentages are **percent consumed**, whereas campaign
discussion often says "capacity" to mean percent remaining. A five-hour value
of 100% is exhausted; a reset to 0% is a fresh window. Record `used` versus
`remaining` explicitly. Also preserve the raw CLI error separately: the label
`monthly spend limit` can coexist with user-visible five-hour and seven-day
windows and does not establish which window caused rejection. On 2026-07-19
the user reported personal at 100% five-hour used and 76% seven-day used
(weekly reset in about 14h40), while school had reset to 0% five-hour used.
The local caches were stale, so these user-visible observations are fresher
than `usagectl`, but the approximate reset interval is not an exact timestamp.

## Prompt for the live GPT-5.6 orchestrator

```text
Read docs/orchestration/LIVE-USAGE.md and
docs/orchestration/usage-policy.json now. Use
`/usr/bin/python3.11 orchestration/usagectl.py snapshot --json` before every dispatch wave,
after any provider-limit error, and before final synthesis. Treat live Codex
rate-limit data as authoritative and stale/missing Claude or agy data as
unknown. Record the personal Codex seven-day reset time in the campaign ledger
whenever it changes. The personal Codex account currently has one Full reset
credit expiring 2026-08-12: preserve it as emergency reserve. Never call,
script, or suggest a reset-credit consumption operation unless I explicitly
authorize consuming a specific credit in a later message. Continue using
persistent worker UUIDs;
usage monitoring must never replace, fork, or concurrently message a worker.
Report the first usage snapshot and any warnings, then continue the existing
campaign from MIGRATION-HANDOFF.md plus MIGRATION-DELTA.md.
```
