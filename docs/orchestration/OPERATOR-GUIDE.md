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
  "argv": [
    "/usr/bin/python3.11", "nd-unfolding/mnv_guarded_run.py",
    "--expect-root", "/path/to/repository", "--", "path/to/validator.py"
  ],
  "cwd": "."
}
```

The validator working directory is repository-relative. Producer,
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

**The guard argv itself is checked, on the producer and on the validator, at
staging and again before the claim.** The guard decides which tree an
interpreter may import from, so its own arguments decide what it will accept,
and a green guard run proves only as much as its argv allowed it to refuse.
For a compute item the argv must carry exactly one `--expect-root`, before the
mandatory `--`, given as an absolute path resolving to the queue's own
repository root. It must **not** carry `--allow` at all: `--allow` declares an
import tree in another checkout, and `mnv_guarded_run.py`'s own header records
that on a production arm it is forbidden outright. Staging `--allow <foreign
checkout>` previously let the guard resolve the cross-tree import it exists to
refuse and exit 0 — the guard's positive control passing for the wrong tree.
Also refused anywhere in the argv: the `-S`, `-I` and `-E` interpreter flags,
and any element that begins with `PYTHON` and contains `=`
(`PYTHONPATH=…`, `PYTHONSAFEPATH=…`, `PYTHONNOUSERSITE=…`), because each
rewrites import resolution before the guard is installed. The item JSON lives
in the state directory rather than in Git, so these checks run again inside
`validate_unchanged`: an argv hand-edited after staging, with its digest
recomputed, is refused at approval and at the tick.

**For a compute item the terminal validator obeys exactly the producer's
rules**, at staging and again before the claim: it must route through
`mnv_guarded_run.py`, and the guarded target after `--` must be a repository
`.py` file committed at `HEAD` with identical working-tree bytes, bound like
any other input. An unguarded validator command is refused at staging. This is
not decoration: the validator alone resolves the terminal branch, so it is the
last place decisive logic can be imported from another checkout, and a
committed validator that imports from an uncommitted directory outside the
checkout previously produced a `succeeded` terminal outcome. When the guard
refuses (exit 3, a measured import-tree violation) that is an unclassified
terminal result and resolves to `otherwise`, never to the pass branch.

The queue runs the producer first and then always runs `terminal_validator`,
including after producer failure, timeout, or launch failure. The validator
receives `CAMPAIGN_PRODUCER_RETURNCODE`; the sentinel
`TIMEOUT_OR_NOT_STARTED` represents the two cases without a process return
code. Only the validator return code selects the terminal branch. A validator
timeout or launch failure selects `otherwise`. The outcome records both return
codes and both log paths.

**`maximum_cost.wall_hours` is ONE deadline for the whole execution, not an
allowance for each command.** The deadline is fixed when the producer starts:
the producer is capped by whichever of the staged `timeout_seconds` and the
remaining budget is smaller, and the validator then receives exactly what the
producer left. If nothing is left the validator is **not started**, and the
outcome resolves to `otherwise` with `wall_budget_exhausted` true and the
reason `wall budget exhausted before validation`; the preserve-first actions
and the decision referral still apply. The staged `timeout_seconds` for a
compute item still cannot exceed `maximum_cost.wall_hours * 3600`, since a
per-command timeout larger than the shared budget could never be honoured. The
outcome records `wall_seconds`, `producer_timeout_seconds`, and
`validator_timeout_seconds`, so a receipt shows how the one budget was split.

Immediately before claiming a compute item, the queue reads
`docs/orchestration/state/r5-meter-receipt.json`. Tests may override that path
with `CAMPAIGN_R5_RECEIPT`. Exit code 6 and a `refused` outcome result if the
receipt is missing or malformed, is more than 24 hours old, is dated later than
the queue clock by more than 60 seconds of tolerated skew, reports `fired.any`,
has reached the stop date, or leaves no headroom for this item once every other
reserving item is counted. Freshness is bounded on
both sides on purpose: an age-only bound accepted a receipt dated a day after
the queue clock, which is how a stale measurement can be made to look
permanently fresh.

**The receipt must be committed, and the Perlmutter measurer commits it before
any compute can be admitted.** A measurement that exists only in a working tree
is not evidence — `AGENTS.md` makes a result live only once its evidence has
landed in a commit — so the receipt must be a repository-relative path inside
this checkout, tracked, and byte-identical to its blob at `HEAD`. Anything else
is exit 6 with the reason `receipt is not committed at HEAD`: an absolute path,
a path outside the checkout, an untracked file, and a file edited after it was
committed. A schema-valid receipt copied to `/tmp` previously admitted compute.
`CAMPAIGN_R5_RECEIPT` may override only the **relative** path, which is what
lets the tests commit a receipt inside a temporary repository; it can no longer
point the queue at a file the repository does not record.

Order the work accordingly: **meter and commit the receipt first, then stage,
then approve, then let the ticker run it.** A receipt commit moves `HEAD`, and
an item staged against an earlier `HEAD` is `stale` under the drift rule that
already governs every binding, so an item staged before its receipt has to be
staged again.

**R5 admission is atomic and reserved.** A ceiling belongs to the queue, not to
an item. Besides the receipt's spend and this item's `maximum_cost`, the
headroom check counts the full declared `maximum_cost` of every other compute
item that is not in a terminal outcome: `staged`, `approved`, and claimed or
running (`outcome-unknown`) all reserve, while `refused`, `failed`,
`succeeded`, `stale`, and `revoked` release the reservation. Refusal is
inclusive in either column — spend plus reservations plus this item meeting the
ceiling is already a refusal — and the reason names the items holding the
reservation. With 490 GPU task-hours recorded, two six-hour items each
projected 496 and both were admitted, although together they project 502; now
the second is refused while the first is in flight. The refusal is retryable
and not consumed, so when the whole queue is over-committed every affected item
is refused until a human revokes one or the measurer commits a fresh receipt —
that release is never something a tick decides for itself.

The headroom check and the claim that admits the item happen under **one
exclusive lock**, `state/campaign-queue/admission.lock`, an `O_EXCL` file
naming its owner `host:pid`. Two tickers therefore cannot both read the same
receipt, both find room, and both claim. A tick that finds the lock held claims
nothing and exits 5 with `outcome-unknown` and the holder in its reason; it has
written no outcome, so a later tick retries. A lock older than the admitting
item's `timeout_seconds` plus its whole wall budget is stale and is removed,
with the removal logged to `state/campaign-queue/logs/admission-lock.log` and
to stderr before it is taken. A lock that cannot be read or dated is treated as
held, because "we cannot tell how old this is" must never resolve as "old
enough to break"; clearing that one is a manual act, after you have confirmed
from `list` and the logs that no ticker is still running the item it names.

The receipt must also be **this** stop's receipt, not merely a well-formed one.
`t0_utc` must equal `2026-09-02T13:44:27Z` exactly — the commit instant of
`9ce59a59`, the commit that landed
`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, which §3 names
as the baseline — and `decision_record` must equal
`docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
exactly. Anything else metered a different interval or a different ruling.
`campaignctl.py` and `r5_meter.py` pin the same instant, record, and stop date,
and a cross-module test fails if the two ever drift apart.

This check is a prohibition, not spending authority. Refusal occurs before the
claim and does not consume the item, so a later tick may retry against a fresh
receipt. The refusal reason identifies the rule that fired. Non-compute items do
not consult this meter.

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
