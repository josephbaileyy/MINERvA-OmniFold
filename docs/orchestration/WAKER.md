# WAKER — external-event continuation for the persistent orchestration campaign

Canonical home for the wait/continuation subsystem. Code: `wakerctl.py` (+
`test_wakerctl.py`); tracked config: `waker-config.json`; runtime state:
`state/waker/` (gitignored). The retired
`.agents/retired-skills/persistent-orchestrator/` skill references this file
instead of carrying operational detail. Human interaction: `OPERATOR-GUIDE.md`.
Shutdown/migration/bootstrap: `PORTING.md`.

## Why this exists (forensic findings, 2026-07-18/19)

| # | Failure | Evidence |
|---|---|---|
| F1 | Codex goal-mode auto-continuation woke the root with no event and burned tokens; disabling goals removed all automatic continuation | `QUIET-PERIODS.tsv` QP2/QP3, QP4 |
| F2 | Hand-built watcher resumed via a hard-coded nonexistent codex path → exit 127 after a real event; manual user recovery | QP5, `RUNS.tsv` MIG-WAKEG2-FAIL |
| F3 | `env python3` selected Python 3.6; classifier SyntaxError ×10 → false MONITOR_ERROR resume while production was healthy | MIG-WAKE-G2ARRAY-MONERR |
| F4 | tmux servers/PIDs are login-node-local; watcher liveness unverifiable from other nodes; LIVE-STATE claimed ACTIVE for an invisible session | `watch_*.sh` + tmux inspection |
| F5 | Resumes relied on inherited `CODEX_HOME` (root thread lives in `~/codex-homes/personal`, not `~/.codex`) and once lacked the authorized bypass flags | watcher sources; session-store audit |
| F6 | Three hand-cloned watcher scripts, five hand-namespaced re-arms (r2–r5); F2/F3 were introduced during those hand edits | `watch_g2_{smoke,dump}_resume.sh`, `watch_slurm_array_resume.sh` |
| F7 | Resumed orchestrator stopped after recommending the next Slurm action because the bounded prompt did not authorize it | user report; early wake prompts |
| F8 | No queue-latency, deadline, or heartbeat events; provider resets via one-off hard-coded `sleep` scripts | `resume_after_school_reset*.sh` |

## Architecture

Shared-filesystem **event spool** + deterministic **claim-based dispatcher** +
**scrontab-supervised tick**, with an optional foreground/tmux loop for lower
latency. Zero LLM calls occur unless an armed watch condition holds.

- **Producers** (`wakerctl scan`) evaluate armed watches — Slurm job/array
  terminal state, queue latency (epoch-based via `SLURM_TIME_FORMAT=%s`),
  provider reset instants, deadlines, heartbeats, file sentinels (how detached
  drivers and Codex-owned background sessions signal) — and emit immutable
  event receipts with deterministic ids (`evt-<watch-id>`), so duplicate
  producers collide harmlessly on atomic `link(2)` creation.
- **The live watch directory contains only non-terminal state.** Event
  creation snapshots the watch's action and context into the immutable event
  receipt. After terminal disposition the watch moves to
  `state/waker/archive/watches/`. This keeps historical Lustre inodes out of
  the scan path without deleting provenance. `wakerctl watch-compact` applies
  the same transition to legacy fired/disarmed watches, but moves a fired
  watch only after its `.done` marker exists.
- **The dispatcher** (`wakerctl dispatch`) claims each event exclusively
  (lease-stamped hard-link claims; Lustre/GPFS-coherent), serializes provider
  turns through one lease-guarded resume mutex, preflights the environment
  fail-closed (F2/F3), and performs **at most one** action per event: a resume
  of the root provider named by `waker-config.json` `root.profile` — `codex exec
  resume` with explicit `CODEX_HOME`, `--disable goals` and the authorized
  bypass flag, or `claude --print --resume` with the profile's explicit home
  (F5), each carrying that profile's pinned model and flags — or an
  `agentctl.py send` to a named worker, or a repo-internal command.
- **Exactly-once** comes from per-event claims, not process liveness: any
  login node may scan/dispatch concurrently; crashes are recovered by lease
  expiry (claim without invocation → reclaim; invocation without disposition →
  one `resume-outcome-unknown` reconciliation event after a grace period,
  never a blind re-run). Every transition is appended to
  `state/waker/LEDGER.tsv`; every event carries id, timestamp, source node,
  payload evidence, claim, invocation, and terminal disposition.
- **Supervision** is `scrontab` (`wakerctl install-cron`), which survives
  login-node reboots and is visible from every node (`scrontab -l`), fixing
  F4. `state/waker/last-tick.json` proves tick liveness from any node.
  `WAKER_STATE_DIR=/absolute/runtime/path wakerctl install-cron` persists that
  resolved runtime spool in the managed cron line, allowing a clean pinned
  control checkout without a state symlink or host-specific tracked edit.
  An optional `wakerctl run --poll-seconds 60` loop (tmux) lowers latency;
  it is redundant with, never a replacement for, the cron net.
- **Continuation authorization** (F7): every root-resume prompt carries the
  standing preamble — read the event receipt exactly once, preserve every
  worker UUID, never consume a reset credit, one usage snapshot before
  dispatch, then *continue with the next dependency-ready campaign action*
  and re-arm continuation watches before ending the turn.

### Event/claim state machine

```
watch: armed --condition holds--> fired (one event per watch)
event: NEW --claim(lease)--> CLAIMED --invoked marker--> INVOKED --rc--> DONE(resumed|failed)
       NEW --preflight fail--> BLOCKED (claim released; retried on a later tick, F2-safe)
       CLAIMED + lease expired + no invoked --> reclaimable
       INVOKED + grace expired + no done --> DONE(reconciled) + one recon event (exactly once)
       DONE(failed) --> retry event evt-X.rN (bounded by max_retries; each retry
                        is its own exactly-once chain)
```

### Rejected alternatives

- **Slurm `--dependency=afterany` notifier jobs**: measured shared-CPU
  eligible-queue p50 was 8,785 s (MIG-SCHED3) — the notifier would often wake
  hours after the event; also burns allocation. Optional, never primary.
- **`strigger`**: requires SlurmUser/admin privileges for job triggers at
  typical sites; execution environment undefined for users.
- **tmux-only watchers (status quo)**: node-local, reboot-fragile, invisible
  cross-node (F4); hand-cloning bred F2/F3.
- **Codex goals**: token-burning false wakes (F1); user requires goals stay
  disabled — continuation must be external.
- **systemd user units**: no lingering user managers on NERSC login nodes.
- **flock-only mutual exclusion**: correct on this Lustre mount today, but
  link-claims are mount-option-independent and leave durable owner evidence.

## Operating guide

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
P=/usr/bin/python3.11

$P wakerctl.py preflight                  # binaries, root profile, provider home + cwd
$P wakerctl.py smoke                      # isolated end-to-end proof (fake provider)

# Arm continuation for a job / array / sentinel / reset / deadline / latency:
$P wakerctl.py watch-add --id g2-target-<jobid> --kind slurm-job \
    --param job_id=<jobid> --context "Gate-2 target construction batch job."
$P wakerctl.py watch-add --id g2-array-<jobid> --kind slurm-array \
    --param job_id=<jobid> --param tasks=1-12 --context "..."
$P wakerctl.py watch-add --id school-reset --kind provider-reset \
    --param at_utc=2026-07-24T02:51:01+00:00 --param account=codex-school \
    --context "Codex school weekly reset; resume blocked verifier rounds."
$P wakerctl.py watch-add --id qlat-<jobid> --kind queue-latency \
    --param job_id=<jobid> --param threshold_seconds=14400 \
    --context "Queue hedge decision point; deterministic ownership rules apply."
$P wakerctl.py watch-add --id g2-driver-done --kind file-sentinel \
    --param path=/abs/path/DONE --param must_contain=rc=0 --context "..."

$P wakerctl.py status                     # watches/events/tick liveness, any node
$P wakerctl.py watch-compact              # archive terminal legacy watches
$P wakerctl.py tick                       # one manual scan+dispatch pass
$P wakerctl.py install-cron               # arm after saving a checked scrontab -l
$P wakerctl.py uninstall-cron             # rollback
```

Per-watch actions default to resuming the root thread from
`waker-config.json` (`root.thread_id` under `root.profile`). Use
`--action role-send --role R --prompt-file F` to continue a named worker via
`agentctl.py` instead. The dispatcher serializes all provider actions, so two
controllers can never message one persistent worker concurrently.

Watches are one-shot: a fired watch never re-fires. The resumed orchestrator
re-arms coverage for whatever it launches next (the resume preamble instructs
this). Retry policy: failed resumes retry up to `max_retries` (default 2)
as derived events; preflight failures block *without* consuming the event and
are retried by later ticks once the environment is repaired.

## Post-deployment hardening (2026-07-20)

First live cycle exposed two defects, both fixed and regression-tested:

- **F9 — cron wall killed the in-flight resume.** The 16:30 UTC dispatch ran
  inside a scrontab tick limited to `-t 00:10:00`; Slurm killed it mid-turn,
  stranding the event invoked-without-outcome until the 2 h reconciliation
  grace recovered it. Fixes: the managed block now uses `cron_walltime`
  (default `12:00:00`, must exceed the longest legitimate turn), and the
  dispatcher converts SIGTERM during an action into a recorded rc=143
  failure plus bounded retry instead of a silent strand.
- **F10 — silent campaign idle.** The recovered turn promoted Gate 2 and
  ended with no armed watch, so nothing could ever wake the campaign
  (~9 h lost). Fix: the **idle guard**. A turn may end only with ≥1 armed
  watch or a committed `state/waker/BLOCKED-ON-USER.json` naming the exact
  user decision required (the resume preamble now states this). If neither
  holds for `idle_guard_ticks` consecutive ticks, one `campaign-idle` event
  resumes the root — once per idle episode, so a misbehaving turn cannot
  cause a token drip. Writing BLOCKED-ON-USER silences the guard; the user
  **deletes that file after answering** to wake the campaign automatically
  within a few ticks.

**How to tell waiting from stopped** (`wakerctl.py status`): armed watches or
undispatched events → working/waiting, leave it alone. `campaign_idle: true`
with `blocked_on_user: true` → it needs you; read BLOCKED-ON-USER.json,
answer (ledger/prompt/commit as appropriate), delete the file. `blocked`
events → environment problem listed in the `.blocked` file. Neither watches
nor blockers nor idle flags → transient (guard will act within
`idle_guard_ticks` × 5 min).

## Notifications (how the user learns without polling)

`notify_command` in `waker-config.json` calls `notifyctl.py`, which currently
sends cluster-originated attention events through ntfy only. ntfy carries a
generic alert; detailed state stays in cluster receipts and is inspected with
Termius. Per-channel markers deduplicate delivery, and the waker marker is
written only after the enabled channel succeeds.

- a new `BLOCKED-ON-USER.json` declaration (body includes the ask and the
  answer instructions below);
- an event blocked by the environment (missing binary/home — the campaign
  cannot self-resume until someone repairs it);
- resume retries exhausted for an event.

Failed sends retry on later ticks; markers under `state/waker/notified/`
dedupe. Healthy progress, idle-guard self-healing, and ordinary event handling
do not alert. `status_report_interval_seconds` is 0, so routine status digests
are disabled; inspect status through Termius. Secrets live only in gitignored
`state/waker/notification-secrets.json` with mode 0600.

`heartbeat_command` invokes `notifyctl.py heartbeat` after every completed
tick. Once the secret file contains a Healthchecks-compatible URL, this is an
external dead-man signal: ntfy reports campaign problems, while Healthchecks.io
emails when the reporter itself stops. No heartbeat URL is a deliberate no-op,
so enrollment cannot break the ticker.

## Account-capacity routing

`usagectl.py` measures the three independent Codex homes (`personal`, `school`,
`school2`) and classifies each profile `READY`, `LOW`, `EXHAUSTED`,
`AUTH_REQUIRED`, or `UNKNOWN`. For a new bounded task,
`usagectl.py select --provider codex --json` chooses the best measured READY/LOW
account even if another account is unavailable. It never migrates a live
session. Before a root resume, the capacity guard checks the root's exact
profile; an unavailable root leaves the event unconsumed, pushes the block, and
retries after reset/auth recovery. Command actions and Slurm monitoring need no
LLM capacity and continue normally.

The continuity rule applies to an existing conversation, not to the whole
campaign. Do not make several sessions co-own `main` to hide an exhausted
account. The recovery pattern is:

1. keep exactly one accountable root and one serialized waker mutex;
2. run every writer in its own worktree and land only reviewed commits.
   `agentctl start` rejects a dirty Git checkout or a directory already owned
   by another registered role, and both `start` and `send` hold a cwd-keyed
   lock for the complete provider turn. When `--registry` names an external
   runtime registry, turn receipts are stored beside it under `agent-runs/`
   rather than dirtying the pinned control checkout;
3. use `usagectl.py select --provider codex --json` for each **new bounded
   worker**, or let `agentctl.py start --profile auto-codex ...` perform that
   fail-closed selection and record the concrete profile; never silently
   resume an existing UUID under another account;
4. when the root itself exhausts, create one fresh successor on the selected
   account, rehydrate it from `AGENTS.md`, fresh `LIVE-STATE.md`, and the exact
   governing `OI-*` record, then change the root binding once. Retire the old
   root before the successor can write. Conversation history is not the
   campaign database; committed receipts are;
5. use `agy` for bounded independent review or grading when its heartbeat is
   healthy. Its quota is not measurable, so it is not an automatic root or a
   capacity reserve. Agy must not share a writer checkout or independently
   push `main`.

This preserves scientific continuity while allowing provider/account
continuity to change at an explicit, auditable boundary.

The 2026-08-28 recovery applies that boundary explicitly: the former
`codex-waker` root UUID is retired from ownership, and the tracked root binding
names the fresh `claude-school` successor plus its isolated coordinator
worktree. This is one root replacement, not a second co-owner of `main`.

## Poisoned-inode recovery

If `status` or `tick` hangs, identify the exact watch file with bounded
per-file reads. A terminal watch may be moved to `state/waker/quarantine/`
only after its event receipt and `.done` disposition are independently read.
The move is recoverable and must name the file exactly. Reinstall the scrontab
only after saving and checking `scrontab -l`; cancel only the exact wedged cron
allocation, then run one bounded manual tick and read `last-tick.json`. Never
reset the repository or delete the runtime tree as a shortcut.

## Answering a BLOCKED-ON-USER stop

Read the ask, then deliver your decision one of three ways:

1. **Emit it (recommended).** Serialized by the dispatcher, so it can never
   collide with an in-flight turn, and your words arrive verbatim in the
   resume prompt:

   ```bash
   cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
   cat state/waker/BLOCKED-ON-USER.json          # read the exact ask
   rm state/waker/BLOCKED-ON-USER.json
   /usr/bin/python3.11 wakerctl.py emit --id user-decision-$(date -u +%Y%m%d-%H%M) \
     --type user-decision \
     --context "USER DECISION: <your answer, including any authorization you are granting>. Ledger this, delete any stale blocked declaration, proceed accordingly, and re-arm watches."
   ```

   The next tick (≤5 min) resumes the orchestrator with that context.

2. **Plain go-ahead.** If the ask was a simple yes/no and your answer is
   "yes, continue", just delete the file; the idle guard re-wakes the
   campaign with standing authorization within ~15 minutes.

3. **Direct turn.** For a nuanced back-and-forth, resume the root yourself —
   only when no resume is in flight (no event in `status` without a terminal
   state). Read `root.profile` and `root.thread_id` from `waker-config.json`
   and invoke that profile as `build_root_resume()` does: a manual invocation
   inherits neither the provider home nor the profile's pinned flags, and a
   hand-written flag set can grant the root a wider tool surface than its
   profile does. Carry the same decision text as above — `USER DECISION:
   <answer>. Delete state/waker/BLOCKED-ON-USER.json, ledger this, proceed,
   and re-arm watches before ending.`

Never answer by editing BLOCKED-ON-USER.json in place — the file's absence
is the wake signal, and text left inside it is read by nobody.

## Migration (live campaign), rollback, and smoke

1. `preflight` + `smoke` must pass (no live UUID, job, or output is touched).
2. Save `scrontab -l` with a checked zero exit status. Run `install-cron`, read
   the table again, and diff it; only the managed block may change. After one
   interval, confirm a fresh `state/waker/last-tick.json`.
3. Arm watches for the campaign's next external facts (currently the Gate-2
   target-construction job when it is submitted; the school Codex weekly
   reset if a blocked verifier round is waiting on it).
4. Legacy per-job scripts (`watch_g2_*`, `watch_slurm_array_resume.sh`,
   `resume_after_school_reset*.sh`) are retired from use but kept in-tree as
   provenance; do not arm them again. Kill any leftover tmux watcher sessions
   on their home nodes when convenient (`tmux kill-session -t g2-dump-wake-r2`
   on the node that owns it); all of them have already fired and completed.
5. Rollback: `uninstall-cron`, stop any `wakerctl run` loop, and re-arm a
   legacy watcher by hand if truly needed. Runtime state under `state/waker/`
   is inert without a tick and safe to leave in place.
6. Live-state dashboard: set `"wake": {"waker": true}` in
   `state/live-state.json` so `generate_live_state.py` renders watch/event/tick
   liveness instead of node-local tmux state.

## Handoff to the root orchestrator

- Your continuation now arrives as `wakerctl` resume turns. Each prompt names
  one event receipt under `docs/orchestration/state/waker/events/`; read it
  once, act, ledger, and **re-arm watches for everything you launch or wait
  on before ending the turn** — the cron tick does the waiting, you do not.
- Never bypass `agentctl.py` for worker follow-ups; every named worker UUID in
  `state/sessions.json` is preserved and unaffected by this subsystem.
- Reset-credit policy is unchanged: no consumption without new explicit
  user authorization naming the credit (note: zero personal Full reset
  credits remain as of 2026-07-19; the protected-reserve rule still stands
  for any future credits).
- Claude percentages may be stale and agy exposes none: heartbeat success
  proves availability only, never headroom. `usagectl.py snapshot --json`
  before any dispatch wave, as before.
- Queue hedging: arm a `queue-latency` watch at submission time; when it
  fires, decide placement per `SCHEDULING-STRATEGY.md` (a healthy RUNNING
  route always wins; cancel the exact duplicate before starting the
  alternative so two compute paths never write one output). Queue latency is
  strictly a wholly-prestart condition: the evaluator checks both current
  `squeue` rows and allocation-level `sacct` start evidence, and auto-disarms
  without a model wake as soon as any job or array element has started.
