# PORTING — reproduce or restore the orchestration system

Written for the 2026-07-22 → 2026-08-03 Perlmutter shutdown; applies to any
migration. Companion documents: `WAKER.md` (continuation subsystem),
`OPERATOR-GUIDE.md` (human interaction), `PERLMUTTER-MIGRATION.md` (the
original laptop→Perlmutter migration, kept as reference).

## 1. Where the state lives

| State | Location | Survives maintenance? | Restore source |
|---|---|---|---|
| Code, config, skills, tracked receipts, RUNS.tsv | git `github` remote (`main`) | yes (off-site) | `git clone` |
| Untracked runtime state (waker spool/ledger, `runs/` transcripts, state receipts, `.mcp.json`) | repo on `/pscratch` | probably (scratch is not purged during downtime, but scratch is never guaranteed) | handoff bundle §2 |
| Provider continuity: every Codex thread, Claude session, agy conversation + credentials | `~/codex-homes/*`, `~/claude-homes/*`, `~/.gemini` on `/global/homes` | yes | handoff bundle §2 |
| Worker UUID registry | `docs/orchestration/state/sessions.json` (tracked) | yes | git |
| scrontab tick | Slurm controller state | not guaranteed across maintenance | `wakerctl.py install-cron` |
| Live Slurm jobs | scheduler | **no — all jobs die at shutdown** | armed slurm watches auto-reconcile (§4) |

## 2. The handoff bundle

```bash
cd docs/orchestration && HOME=/global/homes/j/josephrb bash make_handoff_bundle.sh
```

Produces `~/orchestration-handoff-<stamp>.tar.gz` + `.sha256` (~640 MB):
provider homes (codex personal/school, claude personal/school/legacy-nested,
agy `~/.gemini` + binary), repo-untracked orchestration state, scrontab and
environment snapshots, FILELIST. **It contains live credentials — never
commit it; `scp` it off-site for extra safety.** Last built:
`orchestration-handoff-20260720T042807Z.tar.gz`, sha256 `90703d7a…f804`.

## 3. Pre-shutdown checklist (run by 2026-07-21)

1. Let in-flight turns finish (`*-resume.invoked` without `.done` = wait).
2. Ensure the orchestrator committed and pushed its current round
   (`git status` clean of orchestration files; `git push github main`).
3. Rebuild the bundle (§2); `scp` bundle + `.sha256` off-site if desired.
4. Nothing else: armed watches, spool, and scrontab need no teardown. Jobs
   killed by the shutdown are reconciled automatically on restore.

## 4. Post-maintenance restore (2026-08-03)

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold   # if missing: re-clone + restore untracked from bundle
git fetch github && git status                # sanity: repo intact at expected head
cd docs/orchestration
/usr/bin/python3.11 wakerctl.py preflight     # codex path may change if nvm was rebuilt → edit waker-config.json codex_bin
scrontab -l | grep -q wakerctl || /usr/bin/python3.11 wakerctl.py install-cron
/usr/bin/python3.11 wakerctl.py status
echo test | mail -s "[MINERvA-waker] post-restore check" josephrb@nersc.gov
```

Then let the ticks run. Any watch armed over a job that died in the shutdown
observes CANCELLED/missing accounting within a few polls and wakes the root
with the error/monitor-error event — the orchestrator reconciles and
relaunches per its own receipts. Do not pre-emptively disarm or "clean up"
watches; that is the recovery mechanism.

## 5. Reproducing on a different machine

Prerequisites: `codex`, `claude`, `agy` CLIs installed and logged out;
Python ≥3.11; git clone of the repo.

1. Restore provider homes from the bundle to the same relative paths
   (`~/codex-homes/{personal,school}`, `~/claude-homes/{personal,school}`
   including the nested `school/claude-homes/personal` legacy home,
   `~/.gemini`), verify the tarball sha256 first.
2. Update `waker-config.json` `codex_bin`/`python` and `profiles.json` homes
   if paths differ. `wakerctl.py preflight` until clean, `smoke` to prove
   the loop.
3. No Slurm off-cluster: `slurm-job`/`slurm-array`/`queue-latency` watches
   are inert; `file-sentinel`, `deadline`, `provider-reset`, `heartbeat`
   still work. Replace the scrontab net with user cron
   (`*/5 * * * * python3 .../wakerctl.py tick --quiet`) or a supervised
   `wakerctl.py run`.
4. Session stores moved with their homes, so `agentctl.py send` resumes the
   same worker UUIDs unchanged. Never `adopt` a bare UUID whose store was
   not migrated (skill rule) — start a replacement role from the file
   handoff instead and record the discontinuity in `RUNS.tsv`.

## 6. Bootstrap prompts by model

### 6a. Codex — resume the existing root (preferred, store intact)

```bash
env CODEX_HOME=/global/homes/j/josephrb/codex-homes/personal \
  codex exec resume --disable goals --dangerously-bypass-approvals-and-sandbox \
  --model gpt-5.6-sol -c 'model_reasoning_effort="xhigh"' \
  019f749a-857b-7790-8cec-bc36b22908be \
  "Perlmutter maintenance is over (or the system was migrated). Read docs/orchestration/LIVE-STATE.md, the last 10 rows of RUNS.tsv, wakerctl status, and squeue once. Reconcile jobs that died in the shutdown from their receipts, re-arm watches for every dependency-ready action, refresh LIVE-STATE.md, and continue the campaign under the standing authorization in WAKER.md. Preserve every worker UUID; never consume reset credits; goals stay disabled."
```

### 6b. Codex — cold start (root session store lost)

Only if `~/codex-homes/personal/sessions/**/*019f749a*` is unrecoverable.
Start a NEW thread with `codex exec` under the same CODEX_HOME and this
prompt; never pretend continuity:

> Adopt the persistent-orchestrator role for the MINERvA OmniFold campaign
> as a REPLACEMENT root; the prior root thread 019f749a… is lost and its
> loss must be recorded in RUNS.tsv. Read, in order:
> `.agents/skills/persistent-orchestrator/SKILL.md`,
> `docs/orchestration/WAKER.md`, `LIVE-STATE.md`, `RUNS.tsv` (full),
> `state/sessions.json`, `MIGRATION-TAKEOVER-STATUS.md` (archival),
> `KNOWN_ISSUES.md`, and the publication runbook. Verify each worker UUID in
> the registry with one memory-only continuity question via
> `agentctl.py send` before trusting it. Then update
> `waker-config.json` `root.thread_id` to your own thread id (from the
> session store), commit that change, arm watches for the next
> dependency-ready action, and proceed. All WAKER.md invariants apply.

After its first turn, verify `root.thread_id` was updated — external wakes
resume whatever id that field holds.

### 6c. Claude — orchestrator or maintainer

Claude Code sessions in this repo load `.claude/skills/persistent-orchestrator`
(routes Codex workers through the `.mcp.json` MCP servers, Claude/agy through
`agentctl.py`). To make Claude the acting orchestrator (e.g. Codex service
outage), give it:

> Act as interim orchestrator for the MINERvA OmniFold campaign using
> $persistent-orchestrator. Read `WAKER.md`, `LIVE-STATE.md`, the tail of
> `RUNS.tsv`, and `state/sessions.json`. Do not replace or concurrently
> message any worker UUID; route follow-ups with `agentctl.py send`. Record
> every round in `RUNS.tsv`. External continuation stays with wakerctl —
> arm watches instead of waiting in-session. The Codex root thread remains
> canonical: when it is reachable again, write it a file handoff and stand
> down, recording the interim rounds.

For pure maintenance/debugging (the usual Claude role), `OPERATOR-GUIDE.md`
is the entrypoint; no special bootstrap needed.

### 6d. Interim Claude root (Codex capacity conservation) — ACTIVE

Performed 2026-07-20 with user authorization, at codex-personal 36%
remaining: the root in `waker-config.json` now points at interim Claude
session `4a8668e1-7fb2-41f9-8cc9-59caea50ea75` (profile `claude-school`,
started from `start-interim-root.md`, registered in `sessions.json` as
`interim-root`). wakerctl resumes it via `claude --print --resume` with the
school home and pinned flags; the canonical Codex thread `019f749a-…` is
untouched and its remaining capacity is reserve. Handback is automatic: the
armed `codex-personal-reset-20260726` provider-reset watch wakes the interim
root at the weekly reset (during the shutdown, so effectively at first tick
after the 2026-08-03 restore) to run the scripted single-resume handback and
restore root routing to Codex. Rules for the interim period: never
`agentctl send` to `interim-root` while it is the active root (same
in-flight rule as the Codex root); the interim shares the school Claude
quota with workers A/B/C/E, so heavy verification routes to agy.

## 7. Verification after any port

`preflight` clean → `smoke` PASS → full suite
(`/usr/bin/python3.11 -m unittest discover -s docs/orchestration -p 'test_*.py'`)
→ one manual `emit`/dispatch round trip against a disposable context if you
need end-to-end proof (§OPERATOR-GUIDE debugging) → notification test mail.
