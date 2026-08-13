# Task handoff `[TASK-ID]`: `[bounded deliverable]`

**Template review state:** UNREVIEWED.

Use this for session-to-session transfer and operational dispatch. Keep
[`TASK.template.md`](TASK.template.md) as the compact scientific proposition
core; this template adds identity, authority, review, compute, storage, and
closeout fields.

## 1. Identity and review class

- Account/role: `[Claude-school A|B|C|D|Claude Personal|Codex]`
- Full session UUID: `[UUID]`
- Process-start boundary: `[UTC timestamp or provider start receipt]`
- Git author name/email: `[distinct agent identity]`
- Worktree/branch: `[absolute path]` / `[branch]`
- Base commit: `[full SHA]`
- Review class: `[ROUTINE|GATE]`
- Required reviewer(s): `[D]` or `[D and Codex, independently]`
- Current review state: `UNREVIEWED`

## 2. Required reading

- `docs/orchestration/LIVE-STATE.md` — verify `Observed:` and `Git:` against
  current state before relying on it.
- `docs/orchestration/FINDINGS.md` — read in full.
- Relevant `BEN-*` entries: `[list ids most likely to recur]`
- `KNOWN_ISSUES.md`
- Owning STATUS/RUN_LOG/reference files: `[exact paths]`
- Owning open item/claim/ledger rows: `[OI/CLM/VL ids and exact paths]`

## 3. Proposition and deliverable

- Falsifiable proposition: `[one sentence]`
- Deliverable: `[exact artifact(s)]`
- Why now / dependency satisfied: `[evidence]`
- Non-goals: `[explicit exclusions]`

## 4. Inputs and current state

| Input | Exact path/URI | Version or full SHA-256 | Read-only? |
|---|---|---|---|
| `[name]` | `[path]` | `[commit/hash]` | yes |

- Running jobs or external state this task depends on: `[IDs and observed state]`
- Facts not inferable from the tree: `[state explicitly, or NONE]`
- Superseded inputs that must not be used: `[exact paths/commits]`

## 5. Ownership and authority

- Sole writable paths/output namespace: `[exact paths]`
- Other active writers that may overlap: `[NONE or exact owner/path]`
- Allowed mutations: `[edits, launches, local commits]`
- Actions requiring Joseph: `[production adoption, external send, destructive
  cleanup, publication choice, scope expansion, purchase/quota request]`
- Forbidden actions: `[examples: edit review target, overwrite canonical
  product, cancel unrelated job, delete durable copy, push/merge]`

## 6. Required method and tests

- Independent method/formalism: `[method]`
- Acceptance tests and numerical tolerances: `[tests]`
- Refutation test: `[observation that falsifies the proposition]`
- Failure handling: `[diagnose, preserve evidence, propose repair; do not
  silently weaken the test]`
- Exact reproduction commands: `[commands]`

## 7. Compute and storage declaration

- Queue/resources/wall time: `[estimate]`
- Expected compute cost: `[node-hours/GPU-hours]`
- Output paths and expected size: `[paths/bytes]`
- Bit-reproducible from committed inputs? `[YES|NO; why]`
- Working storage: `[scratch/CFS/local]`
- Durable storage: `[Git/CFS/HPSS; exact destination]`
- HPSS quota/headroom checked? `[YES|NO|NOT APPLICABLE; evidence]`
- Integrity check: `[SHA-256, stored HPSS hashverify, structural scan, etc.]`
- Retention owner and release/supersession condition: `[owner + condition]`

## 8. Commit bundle

The result is incomplete until one commit contains, as applicable:

- implementation and launcher;
- product summary/receipt with full input and output hashes;
- `VALIDATION_LEDGER.md` entry for quotable numbers;
- owning RUN_LOG entry;
- owning STATUS one-liner;
- updated `docs/OPEN_ITEMS.md` pointer/status when the task closes or changes an
  open item;
- review state metadata.

Artifact commit: `[PENDING]`

## 9. Communication

- Durable recipient/message path: `[mailbox or committed repository artifact]`
- Notification recipients: `[roles]`
- Urgency: `[NORMAL|IMMEDIATE because running job/quoted number/irreversible action]`
- No progress chatter is required unless state changes the task's inputs,
  safety, cost, or correctness.

Notification body:

```text
Task-ID: <id>
Sender: <role, account, full UUID, process-start boundary>
Artifact: <path>
Commit: <full commit>
Review class/state: <ROUTINE|GATE> / <UNREVIEWED|REVIEWED|DISPUTED>
Requested action: <one sentence>
Message-ID: <durable id>
```

## 10. Final report and closeout

- Result: `[claim supported/refuted/qualified]`
- Evidence: `[exact paths, hashes, commands, job IDs]`
- Known limitations: `[list]`
- Recommended repair or next action: `[always include for a problem finding]`
- Review report(s): `[paths/commits]`
- Final review state: `[UNREVIEWED|REVIEWED|DISPUTED]`
- Next handoff: `[path or NONE]`
- Session disposition: `[CLOSE|CONTINUITY-ONLY|continue same bounded task]`
- `git status --short` after work/review: `[output]`
