---
name: persistent-orchestrator
description: Maintain named Claude, Codex, and agy workers across multiple debate, review, research, or verification rounds. Use when Codex must orchestrate separate account homes, migrate an orchestration campaign, route follow-ups to the same worker context, preserve role commitments, or avoid replacing persistent delegates with one-shot CLI calls.
---

# Persistent Orchestrator

Treat each role as one durable provider conversation. Use
`orchestration/agentctl.py` for every external-account turn.

## Start and resume

Start each role once:

```bash
/usr/bin/python3.11 orchestration/agentctl.py start --role ROLE --profile PROFILE \
  --prompt-file PROMPT_FILE
```

Resume that role for every later round:

```bash
/usr/bin/python3.11 orchestration/agentctl.py send --role ROLE --prompt-file PROMPT_FILE
```

Profiles are `codex-personal`, `codex-school`, `claude-personal`,
`claude-school`, `claude-school-legacy`, and `agy`. Use
`claude-school-legacy` only to resume the migrated A/B/C UUIDs stored under
the nested Perlmutter home; use `claude-school` for new flat-home roles. Never
bypass the dispatcher with raw one-shot commands. Never use provider shortcuts
such as `--last`, `--continue`, or `-c` when multiple roles may run
concurrently.

Use the configured frontier models: Claude `opus` (Opus 4.8), Codex
`gpt-5.6-sol` at `xhigh`, and agy `Gemini 3.1 Pro (High)`. The user authorizes
full permission bypass for these profiles. Preserve the dispatcher flags;
Codex uses `--dangerously-bypass-approvals-and-sandbox`, the installed
equivalent of `--yolo`, while Claude and agy use
`--dangerously-skip-permissions`.

## Adopt migrated sessions

When an existing session and its provider-side local state remain on this
machine, register it before sending another turn:

```bash
/usr/bin/python3.11 orchestration/agentctl.py adopt --role ROLE --profile PROFILE \
  --session-id UUID --cwd WORKING_DIRECTORY
```

Do not adopt a bare UUID copied from another machine unless the corresponding
provider session store was securely migrated too. Start a new role with the
handoff context instead.

## Run the campaign

1. Read the handoff, ledgers, open questions, and current registry first.
2. Define stable, unique role names and record their responsibilities.
3. Start independent first-round workers in parallel when useful.
4. Save every returned session ID before synthesis.
5. Route objections and revisions back to the same roles with `send`.
6. Update the campaign ledger after every round.
7. Stop only at the user's stated, verifiable end condition.

## Wait through external events, never through the model

Goals stay disabled. While nothing has happened, no Claude, Codex, or agy
call may run. Continuation after job completion/failure, provider resets,
queue-latency thresholds, deadlines, and missed heartbeats is delivered by
`orchestration/wakerctl.py` (design, state machine, and full operating guide:
`docs/orchestration/WAKER.md`):

```bash
/usr/bin/python3.11 orchestration/wakerctl.py watch-add --id ID --kind KIND \
  --param key=value ... --context "campaign context"
/usr/bin/python3.11 orchestration/wakerctl.py status
```

A turn may end only in one of two states: at least one armed watch covering
the next external fact, or a committed
`orchestration/state/waker/BLOCKED-ON-USER.json` naming the exact user
decision required. Ending with neither triggers the idle guard, which resumes
the root once per idle episode. Each real event resumes the saved root thread
exactly once with the correct CODEX_HOME, model, and permission flags;
duplicate events, controller restarts, stale locks, and wall-killed resumes
are absorbed by the claim ledger and bounded retries. Never hand-write
per-job watcher scripts or LLM sleep/poll loops; never re-arm the retired
`watch_g2_*`/`resume_after_school_reset*` scripts.

## Plan around measured capacity

Before each dispatch wave, after a cap, and before final synthesis, run:

```bash
/usr/bin/python3.11 orchestration/usagectl.py snapshot --json
```

Treat live Codex data as authoritative. Track the personal account's exact
seven-day reset time and preserve its two Full reset credits as emergency
reserve. Never consume a reset credit without a new, explicit user
authorization naming the credit action. Treat stale/missing Claude data and
agy's unavailable percentage as unknown. Follow
`docs/orchestration/LIVE-USAGE.md` and record material changes in the campaign
ledger.

Treat these local measurements as planning baselines, not guaranteed account
entitlements:

- Budget about 16–20 Codex xhigh+search calls per five-hour window per account.
- Budget about 42 Opus grading-size jobs from a 6% start, or roughly 45 per
  five-hour window; heavy research turns consume more.
- Treat Gemini as effectively uncapped for ordinary campaigns: 254 heavy
  High+search calls completed in one day without a cap.

Use a trivial content-free heartbeat to detect a reset. On a cap, record the
provider's reset time and route independent work to another account; do not
replace or lose the capped role's saved session. Avoid extreme login-node
bursts even where provider concurrency permits them.

If a resume fails, inspect the raw run artifacts and report the failure. Never
silently replace the role with a fresh conversation because that destroys its
context and argumentative identity.
