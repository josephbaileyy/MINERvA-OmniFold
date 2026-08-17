# A delegate failure has no reliable signal — not the exit code, not the absence of a known error string

**BEN-390.** Filed 2026-08-17 by the seconding lane (block `390-399`), on evidence first observed by
peer session `minerva-omnifold-72` and **re-derived here rather than transcribed** — with one of its three
claims confirmed exactly, one confirmed in a stronger form than reported, and one **not reproducible from
here**, recorded as such.

## The rule that comes out of it

> **A delegate succeeded iff its report file is non-empty AND matches the required final-message format.**
> Never the exit code. Never the absence of a known error string.

Both halves of the AND are load-bearing, and the second half is not decoration: **`agy`'s failure notice is
303 bytes of fluent prose**, so a non-emptiness check alone passes a dispatch that did nothing.

The executable form is `delegate_report_check.py` in this directory, with `test_delegate_report_check.py`
(15 tests) — written here rather than as a paragraph, per `CLAUDE.md`'s *"prefer the executable form of any
rule you are tempted to write down."* It is a check a dispatcher calls; nothing invokes it automatically,
which is stated plainly rather than left to be discovered.

## Evidence

Environment for everything below: `codex-cli 0.147.0`, `model gpt-5.6-sol`, macOS, this repo as `workdir`.
Aliases are **not** in scope in a non-interactive shell, so the account is selected by
`env CODEX_HOME="$HOME/.codex-{personal,school}"` — the form used for every measurement here.

### 1. The exit code is not a success signal in either direction

| when | delegate | invocation | exit | report file | source |
|---|---|---|---|---|---|
| 11:50Z | codex-personal | read-only, `--output-last-message`, inside a harness background task | **0** | present, containing **the prompt echoed back** | peer, not reproduced here |
| 13:05Z | codex-personal | trivial probe | **1** | — | peer |
| ~13:14Z | codex-personal | `exec --sandbox read-only --skip-git-repo-check --output-last-message` | **1** | **never created** | measured here |
| ~13:14Z | codex-school | same | **1** | **never created** | measured here |
| ~13:17Z | `agy -p` | headless, no `--dangerously-skip-permissions` | **0** | 303 B, a denial notice | measured here |

**What is confirmed:** exit 0 co-occurs with total failure — I reproduced that on `agy`, independently of
the peer's codex observation. So the "0 does not mean it worked" half stands on my own measurement.

**What is NOT confirmed:** I could not reproduce codex exit 0 on a usage-limit failure. Three of the four
codex observations are exit 1, including both of mine. **The discriminator is unknown and is not guessed at
here.** Candidates, none tested: `--output-last-message` presence, the harness background-task wrapper, an
MCP transport error that appeared only in the peer's second run
(`rmcp::transport::worker: worker quit with fatal … developers.openai.com/mcp`), or a behaviour change
during the day — the exit-0 case is the only observation predating 13:00Z. **Enumerating candidates is not
narrowing them**, and the row's conclusion does not depend on which is right: an exit code that is 0 on one
invocation and 1 on the next, for the same failure text on the same account 75 minutes apart, is unusable in
**either** direction.

### 2. The three delegates word exhaustion three different ways

Captured verbatim, both codex lines from a single side-by-side run of the same probe:

- **codex-personal** — `You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at Aug 20th, 2026 12:43 AM.`
- **codex-school** — `Your workspace is out of credits. Ask your workspace owner to refill in order to continue.`
- **agy headless** — no quota error at all: `jetski: no output produced — a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. command(<target>)). Alternatively, re-run with --dangerously-skip-permissions to auto-approve all tools.`

The peer's failover chain grepped `usage limit\|session limit`. **`out of credits` does not match it**, so the
fallback never fired and the chain reported success. That predicate is not merely incomplete: **it is keyed to
the one wording of the three that the exhausted account did not use**, and the third delegate's failure is not
a quota condition at all — it is a permission denial, so no quota vocabulary could ever have caught it.

**Both accounts are currently exhausted**, personal until `Aug 20th, 2026 12:43 AM`. That is state, not a
finding, and it will be false by the time most readers arrive.

### 3. Two failure modes of my own, found while probing

Neither is the peer's, both are in the same class, and both produce **no report file at all**:

- **`codex exec` blocks forever on stdin in a non-interactive shell.** Without `< /dev/null` it prints
  `Reading additional input from stdin...` (39 bytes) and waits. I killed it at 180 s and again at 300 s.
  **A hang is the worst member of this class**, because it is indistinguishable from a long-running job by
  every signal a dispatcher has — and this repo's `BEN-028` already records that quiet ≠ dead, which is
  exactly the reasoning that would talk you out of killing it.
- **`codex exec` outside a trusted directory** exits 1 with
  `Not inside a trusted directory and --skip-git-repo-check was not specified.` **A dispatch's `cwd` is part
  of its failure surface**, which is easy to miss when the dispatcher and the delegate run in different
  directories.

### 4. The check's own false positive, caught by testing it in the direction it acts

The first version of `delegate_report_check.py` carried `Reading additional input from stdin` as a plain
substring signature. **`codex exec` prints that line on every run, including successful ones and including
runs given `< /dev/null`** — measured, it is in the log of both probes that reached the API. As written, the
signature fired on every codex log ever captured. It is a genuine failure only when it is the *whole* output.

Fixed by moving it out of the signature table into a predicate that requires it to be the entire content,
with tests in both directions: it fires on the 39-byte hang capture and does **not** fire on a healthy log
that merely contains the line. This is `BEN-381`'s shape — *a check that fires on the healthy case gets
switched off* — caught inside the tool written to prevent the class, which is not reassuring and is why it
is recorded here rather than quietly fixed.

## Scope, and what this does not cover

`CLAUDE.md`'s rule that caps are **live-checked and never persisted** is about not trusting a *stale* cap
reading. This row is about the *check itself* being unreliable at dispatch time, which that rule does not
address: `usagectl.py snapshot` is a **pre**-dispatch capacity read, and nothing in the repo verified the
**post**-dispatch report until now.

**The signature table is incomplete by construction.** Every entry in it was discovered one dispatch at a
time, three of them today. Do not add a wording and consider the class closed — that is the move that
produced the broken failover predicate. The format check is the part that generalises.

## Re-deriving this

```bash
# the two wordings, side by side (both accounts, one probe each)
for acct in personal school; do
  env CODEX_HOME="$HOME/.codex-$acct" codex exec --sandbox read-only --skip-git-repo-check \
      --output-last-message /tmp/last_$acct.txt 'Reply with exactly: PROBE_OK' \
      > /tmp/full_$acct.log 2>&1 < /dev/null; echo "$acct EXIT=$?"
done
grep -hE 'ERROR' /tmp/full_personal.log /tmp/full_school.log

# agy: exit 0, non-empty output, no work done
cd "$(mktemp -d)" && agy -p 'Run the shell command `ls -la` and report its exact output.' \
    > out.log 2>&1 < /dev/null; echo "EXIT=$?"; cat out.log

# the check, against those very artifacts
python3 docs/orchestration/delegate_report_check.py /tmp/last_school.txt \
    --log /tmp/full_school.log --require-regex '^PROBE_OK'   # -> rc 2
cd docs/orchestration && python3 -m pytest test_delegate_report_check.py -q   # -> 15 passed
```

The account state will differ once the caps reset; the exit-code inconsistency, the three wordings and the
missing report file are properties of the tools.

## Cross-references

- `BEN-028` — a quiet log does not mean a dead job. The stdin hang is the same trap one level up, in the
  dispatch layer rather than the Slurm layer.
- `BEN-381` — an allow-list keyed on `file:line` is a false-positive generator. Section 4 is that defect
  inside this finding's own tool.
- `BEN-112` — *a print is not a check.* An exit code is not a check either, and for the same reason.
- `FINDING-20260817-a-narrowing-flag-guarantees-its-answer.md` (`BEN-391`) — the sibling filed in the same
  commit, from the same lane's dispatches. Both are one shape: **a signal that looks like evidence of the
  world when it is evidence about the instrument.**
