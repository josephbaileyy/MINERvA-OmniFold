# Perlmutter: persistent workers and Claude-to-Codex cutover

This runbook assumes:

- the workspace is `/global/homes/j/josephrb/MINERvA-OmniFold`,
- that Home path is a symlink to
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, so both names address the same
  checkout,
- orchestration files physically live under `docs/orchestration`, with a
  project-root `orchestration` compatibility symlink,
- the new root orchestrator uses `~/codex-homes/personal` (the `codex` account),
- its model is `gpt-5.6-sol` at `xhigh`,
- both Claude accounts use Opus 4.8 through the `opus` alias,
- both Codex accounts use `gpt-5.6-sol` at `xhigh`,
- agy uses `Gemini 3.1 Pro (High)`,
- `codex-school`, both Claude accounts, and agy remain independent delegates,
- the existing Claude campaign is already running on Perlmutter.

The commands below use the supplied NERSC username and workspace directly.

## 0. Replace the recursive shell aliases

The original aliases make `claude-personal` expand through `claude` and back
to `claude-personal`. Plain `claude` happens to work because zsh suppresses an
alias while expanding it. The Codex aliases contain the same latent cycle.
Replace those aliases in `~/.zshrc` with functions that call the real binary:

```zsh
unalias claude claude-personal claude-school 2>/dev/null
unalias codex codex-personal codex-school 2>/dev/null

claude-personal() {
  HOME="/global/homes/j/josephrb/claude-homes/personal" command claude "$@"
}

claude-school() {
  HOME="/global/homes/j/josephrb/claude-homes/school" command claude "$@"
}

claude() {
  claude-personal "$@"
}

codex-personal() {
  CODEX_HOME="/global/homes/j/josephrb/codex-homes/personal" command codex "$@"
}

codex-school() {
  CODEX_HOME="/global/homes/j/josephrb/codex-homes/school" command codex "$@"
}

codex() {
  codex-personal "$@"
}

export PATH="/global/homes/j/josephrb/.local/bin:$PATH"
```

Remove the six old `alias claude...` and `alias codex...` lines first, then:

```bash
source ~/.zshrc
type -a claude claude-personal claude-school codex codex-personal codex-school
claude-personal --version
claude-school --version
codex-personal --version
codex-school --version
```

These functions are for interactive use. The dispatcher does not rely on
aliases or functions; it launches the executables with the correct account
environment itself.

## 1. Freeze the current Claude campaign cleanly

Do not terminate Claude yet. Ask the current orchestrator:

```text
Prepare a lossless orchestrator handoff without dispatching new work.

Write docs/orchestration/MIGRATION-HANDOFF.md containing the objective, stopping
condition, verified results, unresolved questions, current plan, role
assignments, important file paths, commands, quota state, and the next three
recommended actions.

Write docs/orchestration/MIGRATION-WORKERS.json with one object per active worker:
role, profile/account, provider, exact session/thread/conversation UUID, cwd,
last completed turn, pending prompt, and where the provider session is stored.
Do not guess missing UUIDs; mark them MISSING. Update the campaign ledger and
then wait without starting another round.
```

For the current campaign this step is already complete. The downloaded
snapshot contains both files, timestamped `2026-07-18T09:07:00Z`. Preserve
them; do not regenerate or overwrite them during toolkit installation.

The snapshot records active A/C compute chains and an orchestrator fallback
wakeup. Before the Codex root sends any worker prompt, tell the old Claude
root:

```text
Cutover fence: disarm only orchestrator-side wakeups or background tasks that
could send another prompt to Agents A, B, or C. Do not cancel or alter any
Slurm allocation, holder, training, unfold, merge, or covariance process.
Write docs/orchestration/MIGRATION-DELTA.md with every ledger, git, scheduler,
worker-turn, output-validation, quota, and pending-action change since the
2026-07-18T09:07:00Z snapshot. Then confirm that you will send no more worker
turns and wait.
```

Treat `MIGRATION-HANDOFF.md` as the immutable snapshot and
`MIGRATION-DELTA.md` as the live cutover addendum. Never have Claude and Codex
send to the same worker UUID concurrently.

The root Claude conversation itself cannot be imported into Codex. The handoff
and repository artifacts are the migration boundary. Delegate UUIDs can be
adopted only if their local provider session stores remain available on the
same Perlmutter account homes.

## 2. Put the project on persistent NERSC storage

Use the existing Home-path entrypoint, noting that it resolves into pscratch.
On Perlmutter:

```bash
export PROJECT_DIR="/global/homes/j/josephrb/MINERvA-OmniFold"
cd "$PROJECT_DIR"
export PHYSICAL_PROJECT_DIR="$(readlink -f "$PROJECT_DIR")"
test "$PHYSICAL_PROJECT_DIR" = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
printf '%s\n' "$PHYSICAL_PROJECT_DIR"
showquota
```

The test must succeed. Copying to `$PROJECT_DIR/docs/orchestration` traverses
the project symlink and writes into the same pscratch checkout used by Agents
A/B/C. Keep important campaign artifacts committed and backed up according to
the applicable NERSC scratch-storage policy.

If the project already lives there, keep it in place. First create the remote
destination from the laptop:

```bash
ssh josephrb@perlmutter.nersc.gov \
  'mkdir -p /global/homes/j/josephrb/MINERvA-OmniFold/docs/orchestration'
```

Then transfer only the dispatcher files into the existing
`docs/orchestration` directory. Do not rsync the whole local directory: the
live campaign already has its own `README.md`, ledgers, dossier, rollout plan,
and handoff files.

```bash
cd /Users/josephbailey/new-physics
rsync -av \
  ./orchestration/agentctl.py \
  ./orchestration/codex-mcp-account.py \
  ./orchestration/profiles.json \
  ./orchestration/test_agentctl.py \
  ./orchestration/PERLMUTTER-MIGRATION.md \
  josephrb@dtn01.nersc.gov:/global/homes/j/josephrb/MINERvA-OmniFold/docs/orchestration/

rsync -avR \
  ./.mcp.json \
  ./.agents/skills/persistent-orchestrator \
  ./.claude/skills/persistent-orchestrator \
  josephrb@dtn01.nersc.gov:/global/homes/j/josephrb/MINERvA-OmniFold/
```

On Perlmutter, create the compatibility link only if no root-level path with
that name already exists:

```bash
cd /global/homes/j/josephrb/MINERvA-OmniFold
if [[ ! -e orchestration ]]; then
  ln -s docs/orchestration orchestration
else
  ls -ld orchestration
fi
readlink -f orchestration
```

The last command may print either the logical Home path or its physical
pscratch equivalent, depending on `readlink`; it must end in
`MINERvA-OmniFold/docs/orchestration`. If a real root-level `orchestration`
directory already exists, do not overwrite it; merge any `state`, `runs`, or
handoff files into `docs/orchestration` first, then replace it with the symlink
using a recoverable rename.

Do not copy account credential directories from the laptop. Authenticate the
Perlmutter installations independently.

## 3. Validate the installed kit

On Perlmutter:

```bash
cd "$PROJECT_DIR"
python3 --version
python3 -m py_compile orchestration/agentctl.py orchestration/codex-mcp-account.py
(cd orchestration && python3 -m unittest -v test_agentctl.py)
python3 orchestration/agentctl.py profiles
chmod 700 orchestration/agentctl.py orchestration/codex-mcp-account.py
```

The script needs Python 3.10 or newer and only uses the standard library. If
the default Python is older, load a current NERSC Python module first.

NERSC may expose the login home through `/global/homes/...` while resolving it
physically under `/global/u2/...`. Dispatcher account paths deliberately keep
the stable `/global/homes/...` spelling; both paths address the same storage.

## 4. Verify every account on Perlmutter

```bash
CODEX_HOME="/global/homes/j/josephrb/codex-homes/personal" command codex login status
CODEX_HOME="/global/homes/j/josephrb/codex-homes/school" command codex login status
HOME="/global/homes/j/josephrb/claude-homes/personal" command claude auth status
HOME="/global/homes/j/josephrb/claude-homes/school" command claude auth status
HOME="/global/homes/j/josephrb/claude-homes/school/claude-homes/personal" command claude auth status
"$HOME/.local/bin/agy" --help
```

If `claude-school` is unexpectedly logged out:

```bash
HOME="/global/homes/j/josephrb/claude-homes/school" command claude auth login
```

Confirm the configured executables and homes:

```bash
python3 orchestration/agentctl.py profiles
```

Edit `orchestration/profiles.json` if Perlmutter uses a different agy path or
account-home convention.

The third Claude check is the legacy nested home containing Agents A/B/C.
The supplied handoff records that home as authenticated and the flat school
home as unauthenticated. Keep the nested home intact until all three migrated
sessions finish. Authenticate the corrected flat `claude-school` home for new
roles when convenient.

### Models and permission policy

| Profile | Model | Non-interactive permission mode |
|---|---|---|
| `claude-personal` | Opus 4.8 (`opus`) | `--dangerously-skip-permissions` |
| `claude-school` | Opus 4.8 (`opus`) | `--dangerously-skip-permissions` |
| `claude-school-legacy` | Opus 4.8 (`opus`), migrated A/B/C only | `--dangerously-skip-permissions` |
| `codex-personal` | `gpt-5.6-sol`, `xhigh` | `--dangerously-bypass-approvals-and-sandbox` |
| `codex-school` | `gpt-5.6-sol`, `xhigh`, web search | `--dangerously-bypass-approvals-and-sandbox` |
| `agy` | `Gemini 3.1 Pro (High)` | `--dangerously-skip-permissions` |

The installed Codex CLI spells the requested `--yolo` behavior
`--dangerously-bypass-approvals-and-sandbox`. The dispatcher uses that exact
supported flag. This authorization applies to all listed accounts; keep the
working directory scoped to the trusted project.

## 5. Adopt resumable delegates from Claude

Read `MIGRATION-WORKERS.json`. The current snapshot supports these exact
adoptions:

```bash
python3 orchestration/agentctl.py adopt \
  --role agent-A-standard --profile claude-school-legacy \
  --session-id 14951826-0680-4e57-ac92-8a9970bc07f7 \
  --cwd /pscratch/sd/j/josephrb/MINERvA-OmniFold

python3 orchestration/agentctl.py adopt \
  --role agent-B-p5b --profile claude-school-legacy \
  --session-id 46e4af3e-c3f2-4fa5-abc7-f0da72817282 \
  --cwd /pscratch/sd/j/josephrb/MINERvA-OmniFold

python3 orchestration/agentctl.py adopt \
  --role agent-C-fps --profile claude-school-legacy \
  --session-id 4580f42d-77db-4f59-88c4-1b2854f24d82 \
  --cwd /pscratch/sd/j/josephrb/MINERvA-OmniFold
```

Do not adopt the old root orchestrator into Codex; use its handoff as the
migration boundary. Do not adopt Agent D: its UUID is explicitly `MISSING`,
and the candidate UUID in the roster is unconfirmed.

The adoption commands intentionally use the physical pscratch path recorded
in the worker roster. It is the resolved target of `$PROJECT_DIR`, not a
different checkout.

After adoption, continuity-check A and C one at a time with a status-only
prompt that forbids launching, cancelling, or modifying work. Reconcile their
answers against `MIGRATION-DELTA.md`, `squeue -u josephrb`, the current ledgers,
and validated output files before issuing an action prompt. Agent B is idle
and needs no immediate turn.

For any additional verified worker, use the general form:

```bash
python3 orchestration/agentctl.py adopt \
  --role <ROLE> \
  --profile <codex-personal|codex-school|claude-school|claude-school-legacy|agy> \
  --session-id <UUID> \
  --cwd "$PROJECT_DIR"
```

Then inspect the registry:

```bash
python3 orchestration/agentctl.py show
```

For a worker marked `MISSING`, start a new role using a prompt that contains
its role definition plus the relevant section of `MIGRATION-HANDOFF.md`. Do not
use `--last`, Claude `--continue`, or agy `--continue` to guess among concurrent
sessions.

## 6. Smoke-test each provider

Use disposable role names and distinct nonces. Example for agy:

```bash
python3 orchestration/agentctl.py start \
  --role migration-smoke-agy --profile agy \
  'Store nonce AGY-PM-42. Reply exactly READY.'

python3 orchestration/agentctl.py send \
  --role migration-smoke-agy \
  'Reply exactly with the nonce from your previous turn.'
```

Repeat with `codex-school` and `claude-school`. A successful second response
must recover information supplied only in the first turn.

## 7. Enable the durable Codex root

```bash
CODEX_HOME="/global/homes/j/josephrb/codex-homes/personal" command codex features enable goals
```

For a supervised session, use `tmux` so an SSH interruption does not kill the
controller:

```bash
tmux new -s physics-orchestrator
cd "$PROJECT_DIR"
CODEX_HOME="/global/homes/j/josephrb/codex-homes/personal" \
  command codex -C "$PROJECT_DIR" \
  -m gpt-5.6-sol \
  -c 'model_reasoning_effort="xhigh"' \
  --dangerously-bypass-approvals-and-sandbox \
  --search
```

In Codex, start the takeover with one explicit durable objective:

```text
/goal Use $persistent-orchestrator to take over this campaign. First read
orchestration/MIGRATION-HANDOFF.md, orchestration/MIGRATION-WORKERS.json, the
campaign ledger, and orchestration/state/sessions.json. Verify the adopted
workers with one continuity question each. Continue routing later rounds to
the same named workers until every handoff item is either verified and closed
or explicitly recorded as blocked with evidence. Keep the ledger current and
do not silently replace a failed worker.
```

The project Codex skill lives at
`.agents/skills/persistent-orchestrator/SKILL.md`; explicitly naming
`$persistent-orchestrator` guarantees that its routing rules are loaded.

## 8. Validate before ending Claude

Before closing the old Claude root, require the Codex root to show:

1. the parsed handoff objective and stopping condition,
2. the complete role-to-provider-to-UUID map,
3. one successful resumed response from every adopted role,
4. the next campaign round written to the ledger,
5. no use of `--last` or provider `--continue` shortcuts.

Only then end the old Claude session. Keep its handoff files permanently as
provenance.

## 9. Normal operation

```bash
# Start a new durable worker
python3 orchestration/agentctl.py start \
  --role <ROLE> --profile <PROFILE> --prompt-file <PROMPT_FILE>

# Continue the same worker
python3 orchestration/agentctl.py send \
  --role <ROLE> --prompt-file <FOLLOWUP_FILE>

# Audit identities and raw run paths
python3 orchestration/agentctl.py show
```

Run independent roles concurrently, but never send two simultaneous turns to
the same role. The dispatcher locks each role and atomically updates the shared
registry.

## 10. Perlmutter operating limits

The following are measured local-account baselines from July 2026. Expect the
Perlmutter logins to be similar or better, but verify rather than treating
them as contractual limits:

| Provider/account | Measured capacity | Planning rule |
|---|---|---|
| Each Codex account | About 16–20 `gpt-5.6-sol` xhigh+search calls per five-hour window; 16 jobs plus 6 probes reached the cap | Reserve several calls for synthesis and continuity checks |
| Claude School | 42 successful Opus+search jobs from a 6% start before the session cap; approximately 45 grading-size jobs per five-hour window | Heavy derivation/research turns cost more than grading jobs; initially use the same estimate for Claude Personal |
| agy/Gemini | 254 heavy High+search calls in one day, including a clean 32-concurrent burst, with no cap observed | Operationally treat as uncapped for ordinary campaigns, not literally unlimited |

Codex burst concurrency did not produce server rejection even at 64 calls per
account, but shared `CODEX_HOME` state raced at high concurrency and latency
grew through queueing. Do not use that burst level on Perlmutter login nodes.

Detect limits with a trivial content-free heartbeat, not by grepping research
output for words such as “limit” or “quota.” When a provider caps, save the
reported reset time in the campaign ledger, preserve the role's session ID,
route only independent work elsewhere, and resume the same role after reset.

Keep the controller lean. A few mostly network-waiting CLI delegates are
appropriate for a supervised login session, but do not reproduce the earlier
32- or 64-process burst tests on shared login nodes. Monitor aggregate usage
with `top -u "$USER"`.

For compute-heavy tools, large local analyses, or high worker concurrency, use
an interactive allocation. For a truly unattended, long-running controller,
use NERSC's workflow QOS rather than relying indefinitely on a login-node tmux
session. Test provider API connectivity in the chosen allocation before the
cutover.
