# OPERATOR GUIDE — interacting with the orchestrator as a human

The campaign runs itself: external events wake the root Codex thread, turns
end, and quiet costs nothing. Your involvement is (1) reading status when
curious, (2) answering when notified, (3) debugging when something is loudly
wrong. Subsystem internals: `WAKER.md`. Migration/restore: `PORTING.md`.

## 1. Reading status (safe from any login node, zero tokens)

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 wakerctl.py status     # the two flags that matter:
                                           #   campaign_idle + blocked_on_user
tail -5 RUNS.tsv                           # what the last rounds did
cat LIVE-STATE.md                          # dashboard the orchestrator refreshes
squeue -u josephrb                         # compute
tail -f state/waker/logs/<event>.log       # a finished turn's full output
```

Interpretation: armed watches or running jobs → working, leave it alone.
`campaign_idle: true` alone → the idle guard will self-heal within ~15 min.
With `blocked_on_user: true` → it is waiting for you (you will also be
emailed). An event stuck in `blocked` → environment broken; see §4.

**In-flight test** before doing anything that touches the thread: an event
in `status` shown as `invoked` (not yet a terminal state) means a turn is
running — wait. Never open interactive `codex resume` on the root while
in-flight; watch `state/waker/logs/` or ledgers instead.

## 2. Getting notified

Current transport: independent **email + ntfy** fanout. Email uses
`/usr/bin/mail` to **josephrb@nersc.gov** (forwards to Stanford; verified
2026-07-20); ntfy sends a generic phone alert so detailed research context is
not placed in the push body. Fires exactly once per channel and condition — new
BLOCKED-ON-USER declaration, environment-blocked dispatch, retries
exhausted — plus a twice-daily status digest.

ntfy and heartbeat credentials are in the gitignored, mode-0600 file
`state/waker/notification-secrets.json`. From Termius, print only the topic
when you are ready to subscribe:

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 -c 'import json; print(json.load(open("state/waker/notification-secrets.json"))["ntfy"]["topic"])'
```

The external heartbeat remains inactive until that same secret file gets
a URL. After creating the external check, configure it without hand-editing
the secret file:

```bash
/usr/bin/python3.11 notifyctl.py set-heartbeat --url 'https://hc-ping.com/<check-id>'
/usr/bin/python3.11 notifyctl.py heartbeat
```

The ticker normally pings every five minutes. In Healthchecks.io, set this
check to a **10-minute period** and **20-minute grace**. The dashboard should
show a new ping about every five minutes. A missing ping first enters the
grace period and then becomes Down, at which point Healthchecks sends through
the notification integration configured in its web dashboard. The ping URL is
a credential: recreate the check to rotate it if the URL is exposed.

Other constraints:

- **Claude/Codex remote sessions** (claude.ai/code, Codex cloud) cannot
  reach Perlmutter's filesystem, so they cannot watch or wake anything.
  Use them only to reason about pasted status output; email/ntfy remain
  the push channel.

## 3. Answering when it needs you

Follow `WAKER.md` § "Answering a BLOCKED-ON-USER stop". Short form: read
`state/waker/BLOCKED-ON-USER.json`, delete it, then
`wakerctl.py emit --id user-decision-<stamp> --type user-decision
--context "USER DECISION: …"`. The next tick delivers it. Plain "yes"? Just
delete the file. Want a conversation? One bounded `codex exec resume` with
the pinned flags (exact command in WAKER.md) — only when nothing is
in-flight.

## 4. Approving staged campaign work from Termius

Agents may stage an exact command, but staging is not authorization and the
ticker ignores it until you approve its digest from an interactive TTY. The
queue starts empty. It executes at most one ready item per five-minute tick,
never invokes a shell, and never calls an LLM. It binds the repository HEAD
plus the launcher and any explicitly listed input files; drift makes the item
permanently `stale`. A claim without a terminal receipt becomes
`outcome-unknown` and is never retried automatically.

From Termius:

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 campaignctl.py list
/usr/bin/python3.11 campaignctl.py show --id <item-id>
/usr/bin/python3.11 campaignctl.py approve --id <item-id> --digest <full-sha256>
```

The approval command prints the full proposal and then asks you to type
`APPROVE <item-id> <first-12-digest>`. Verify the description, `kind`, exact
`argv`, working directory, dependencies, bound-file hashes, and repository
commit before typing it. The next healthy ticker executes it. Before it is
claimed, cancel with:

```bash
/usr/bin/python3.11 campaignctl.py revoke --id <item-id>
```

Scientific authorization is a separate gate. Approval means only “execute
this exact already-authorized command”; it cannot adopt a result, lift an
`OI-*` hold, authorize material compute, or waive `mnv_guarded_run.py`.

An agent stages work with a command such as:

```bash
/usr/bin/python3.11 campaignctl.py stage \
  --id <item-id> --kind read-only --description '<bounded purpose>' \
  --cwd . --bind <critical-input> -- \
  /usr/bin/python3.11 /pscratch/sd/j/josephrb/MINERvA-OmniFold/<script.py> <args>
```

## 5. Debugging safely

Ordered from safest to most invasive; stop at the first level that answers
your question.

1. **Artifacts only.** Event JSONs, `state/waker/LEDGER.tsv`,
   `state/waker/logs/*.log`, `runs/<role>/*.json` (worker transcripts),
   git log. Everything the system does leaves a receipt.
2. **Deterministic tools.** `wakerctl.py preflight` (environment),
   `smoke` (isolated end-to-end with a fake provider — always safe),
   the unit suite (`python3.11 -m unittest discover -p 'test_*.py'`).
3. **Ask a worker.** Route ONE bounded read-only question to a named
   worker through the dispatcher registry — never a raw CLI call, never
   two controllers on one role:
   ```bash
   /usr/bin/python3.11 agentctl.py show          # roles and UUIDs
   /usr/bin/python3.11 agentctl.py send --role agy-publication-redteam \
     "Status question only, change nothing: <question>. End the turn."
   ```
   agy roles are the cheap first choice; Codex verifier roles are scarce.
4. **Ask the root.** Bounded status turn (WAKER.md command), only when the
   in-flight test passes. It spends root-thread context — prefer 1–3.
5. **Environment repairs.** A `blocked` event names its problem (usually a
   moved codex binary after an nvm update). Fix the path in
   `waker-config.json`, run `preflight`; the event dispatches on the next
   tick — never delete or hand-edit spool files to "unstick" things.

Before creating a new provider task, inspect the capacity-aware recommendation:

```bash
/usr/bin/python3.11 usagectl.py select --provider codex --json
```

This may select `codex-school2` while another account is low or exhausted. It
does not authorize moving an existing UUID/thread between accounts.

Emergency stops (reversible, no state loss): `wakerctl.py watch-disarm
--id <id>` for one watch; `uninstall-cron` to pause all automatic
continuation (re-enable with `install-cron`). Never kill a running resume
turn; if one is misbehaving, let it end, then correct it with an emitted
event.

## 6. What a healthy week looks like

Emails: none. `RUNS.tsv`: new rows after each real event. `status`: watches
cycling armed → fired, events ending `resumed`, ticks advancing across
login nodes. Your only scheduled duty: the pre-shutdown checklist in
`PORTING.md` §3 before maintenance windows.
