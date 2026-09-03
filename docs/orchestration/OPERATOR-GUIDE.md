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
notified through ntfy). An event stuck in `blocked` → environment broken; see §4.

**In-flight test** before doing anything that touches the thread: an event
in `status` shown as `invoked` (not yet a terminal state) means a turn is
running — wait. Never open interactive `codex resume` on the root while
in-flight; watch `state/waker/logs/` or ledgers instead.

## 2. Getting notified

Current cluster-originated transport is **ntfy only**. It sends a generic phone
alert so detailed research context is not placed in the push body. It fires
once per actionable condition — a new BLOCKED-ON-USER declaration,
environment-blocked dispatch, exhausted retries, staged approval, or an
interactive agent needing input. Routine status digests are disabled; inspect
status through Termius when desired.

Outlook is reserved for the external Healthchecks.io dead-man alert. This
separates ordinary attention events from the independent warning that the
waker itself stopped reporting. Configure email in the Healthchecks.io web
dashboard; the cluster does not send that message.

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

- A standalone Claude Code-on-the-web or Codex cloud task cannot reach
  Perlmutter's filesystem. Claude **Remote Control launched on Perlmutter** is
  different: execution and filesystem access remain in that cluster process
  while the phone/browser is its interface. Use it only as a supervised,
  separate session; it may stage queue proposals but must never approve them
  or replace the deterministic ticker. ntfy remains the cluster push channel.

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
plus each command entrypoint and any explicitly listed input files; drift
makes the item permanently `stale`. For compute, the contract, guard, guarded
target, validator, and explicit bindings must all be committed at `HEAD`, with
working-tree bytes identical to their committed blobs. This check runs during
staging and again immediately before a claim. A claim without a terminal
receipt becomes `outcome-unknown` and is never retried automatically. A newly
staged item sends one deduplicated ntfy approval alert on the next ticker pass.

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

This TTY check prevents the noninteractive ticker from approving its own
work, but it is not cryptographic identity separation: a tool deliberately
given an interactive shell under the same Unix account could technically type
the phrase. The operating contract therefore forbids agents from running
`approve` or `revoke`; use a separate phone-held signing key in a future
version if protection from a compromised same-account agent is required.

```bash
/usr/bin/python3.11 campaignctl.py revoke --id <item-id>
```

Scientific authorization is a separate gate. Approval means only “execute
this exact already-authorized command”; it cannot adopt a result, lift an
`OI-*` hold, authorize material compute, or waive `mnv_guarded_run.py`.

Compute items additionally require `--contract <path>`. The contract must be
committed at the staged `HEAD` and its `campaign_id` must equal the queue item
id. Schema version 1 requires the scientific question; exact candidate and
input ids, locations, and SHA-256 digests; exhaustive return-code branches;
the decision consequence, unlocks, and prohibitions for every branch; maximum
GPU task-hours, CPU task-hours, and wall hours; output namespace; producer,
independent-validator, and decision-authority identities; validator version;
preservation behavior; retry policy; and this required validator command:

```json
"terminal_validator": {
  "argv": ["/usr/bin/python3.11", "path/to/validator.py"],
  "cwd": "."
}
```

The validator working directory is repository-relative. Its command entrypoint
is resolved and bound by the same rules as any other command. Producer,
independent-validator, and decision-authority identities must be pairwise
distinct after case folding. Exactly one `otherwise` branch covers every
unclassified terminal result, and every branch must name a decision
consequence.

Compute producers must route through `nd-unfolding/mnv_guarded_run.py`, either
directly or through an allowed Python interpreter. The guarded target after
the mandatory `--` is also bound. A typical command tail is:

```bash
/usr/bin/python3.11 nd-unfolding/mnv_guarded_run.py \
  --expect-root /path/to/repository -- path/to/producer.py <args>
```

The queue runs the producer first and then always runs `terminal_validator`,
including after producer failure, timeout, or launch failure. The validator
receives `CAMPAIGN_PRODUCER_RETURNCODE`; the sentinel
`TIMEOUT_OR_NOT_STARTED` represents the two cases without a process return
code. Producer and validator each receive the staged `timeout_seconds` limit,
which for compute cannot exceed `maximum_cost.wall_hours * 3600`. Only the
validator return code selects the terminal branch. A validator timeout or
launch failure selects `otherwise`. The outcome records both return codes and
both log paths.

Immediately before claiming a compute item, the queue reads
`docs/orchestration/state/r5-meter-receipt.json`. Tests may override that path
with `CAMPAIGN_R5_RECEIPT`. Exit code 6 and a `refused` outcome result if the
receipt is missing or malformed, is more than 24 hours old, reports
`fired.any`, has reached the stop date, or shows that current spend plus either
declared maximum task-hour cost would meet or exceed its ceiling. This check is
a prohibition, not spending authority. Refusal occurs before the claim and
does not consume the item, so a later tick may retry against a fresh receipt.
The refusal reason identifies the rule that fired. Non-compute items do not
consult this meter.

The safe terminal policy is enforced rather than inferred: preservation mode
is `preserve-first`, automatic retraining is false, and a retry requires new
authorization. The fixture at
`test_fixtures_campaign_contract/validator-failed-after-jobs-complete.json`
shows the branch where all jobs complete but the terminal validator fails.
Its queue outcome preserves the declared evidence first, records the decision
consequence, and becomes terminal, so a later tick cannot rerun it.

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
