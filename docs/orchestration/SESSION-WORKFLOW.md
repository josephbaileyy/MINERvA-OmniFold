# Multi-session workflow

**Status:** LIVE policy. **Review state:** UNREVIEWED. This document defines how Joseph, Claude Personal,
Claude-school sessions A–D, and Codex divide work. It does not replace the
scientific state in [`LIVE-STATE.md`](LIVE-STATE.md), the open-item ledger in
[`../OPEN_ITEMS.md`](../OPEN_ITEMS.md), or any workstream STATUS/RUN_LOG.

## 1. Authority and source of truth

1. Joseph makes scope, publication, production-adoption, external-send, and
   destructive-action decisions.
2. The committed Git tree is the authoritative bus. Chat, socket, and mailbox
   messages are notifications or analysis, never the only copy of a result.
3. A campaign result is usable only after the repository's commit bundle is
   complete: implementation/launcher, product summary or receipt, ledger
   entry, RUN_LOG entry, and STATUS one-liner in the same commit.
4. Each artifact has exactly one writer. Reviewers work read-only and do not
   silently repair the artifact they are judging.
5. A reviewer finding is advisory: state the concern, evidence, likely impact,
   and a concrete recommended repair. Reviewers do not issue independent
   stop/cancel/freeze commands. Joseph or the owning worker decides adoption,
   except that an already-declared repository gate remains binding.

## 2. Stable roles

| Participant | Default role | Does not own |
|---|---|---|
| Joseph | Final decisions and external communication | Routine coordination detail |
| Claude Personal | Remote-facing explainer and mediator; reconciles the tree before explaining decisions | Mandatory approval gates or production artifacts |
| Claude-school A | Coordinator: decomposes work, assigns one writer, tracks dependencies, and assembles handoffs | Independent review of its own artifact |
| Claude-school B | Uncertainty, covariance, and statistical-method specialist | General coordination |
| Claude-school C | PET/full-event implementation, NERSC compute, products, and storage execution | Independent review of its own artifact |
| Claude-school D | Default read-only reviewer for routine artifacts | Writing the artifact under review |
| Codex | Independent technical judge for gate-class work; cross-session workflow and targeted implementation when assigned | Silent production adoption or external sends |

Roles are stable; session UUIDs are not. Record the full UUID and process-start
boundary in every handoff and final report. Do not identify a worker by a stale
socket, PID, or short session reference.

## 3. Dispatch and review flow

### Routine artifact

1. A creates a bounded task packet from
   [`TASK-HANDOFF.template.md`](TASK-HANDOFF.template.md).
2. One worker owns the writable paths and commits the complete result bundle.
3. D reviews the original committed artifact read-only.
4. The owner records `REVIEWED` or `DISPUTED` with reviewer and review commit.
5. Claude Personal explains the outcome to Joseph when asked, after checking
   the cited tree state.

### Gate-class artifact

A task is gate-class if it can change a central value, covariance adoption,
analysis definition, publication claim, a production rerun, or a material
compute/storage commitment.

1. The writer commits the complete artifact and marks it `UNREVIEWED`.
2. D and Codex independently inspect the same original commit. Neither reads
   the other's report before submitting its own.
3. If both agree, the owner records `REVIEWED` with both reports.
4. If they disagree, the owner records `DISPUTED`; both reports must include a
   recommended resolution or discriminating test. The exact choice is entered
   in [`USER-DECISIONS.md`](USER-DECISIONS.md) for Joseph.

Review state must be visible near every quoted result:

```text
Review state: UNREVIEWED | REVIEWED | DISPUTED
Artifact commit: <full commit>
Reviewer(s): <role, full UUID, process-start boundary>
Review commit(s): <full commit(s) or NONE>
```

## 4. Session and context lifecycle

- Use one fresh session for one substantial bounded task.
- Start from a written handoff, not conversational memory.
- Let a session finish its current atomic artifact before rotating it unless
  continuing would overwrite or corrupt an active artifact.
- After the artifact and handoff are committed, mark the old session
  **continuity-only**: it may answer provenance questions but receives no new
  production work.
- Start a fresh session when any of these occurs: the task changes workstream;
  the session repeatedly confuses current and superseded state; it cannot name
  its input commit or owned paths; it makes two material factual corrections in
  one task; or its remaining context is too small to read the mandatory inputs
  and still produce the deliverable.
- Do not add more accounts until a measured capacity or independent-review
  bottleneck remains after bounded tasks and context rotation are in place.

Meta-work that does not affect a running job, a quoted number, an irreversible
action, or another worker's current input is batched into the end-of-task
handoff. Urgent corrections are committed and broadcast immediately.

## 5. Communication protocol

The durable Codex–Claude transport is defined in
`~/.codex-claude-bridge/MAILBOX_PROTOCOL.md`. Follow it exactly:

- one atomic file per substantive message;
- socket sends are optional wake notifications only;
- a delivery receipt is not an acknowledgment;
- preserve `Message-ID` and `In-Reply-To`;
- only text explicitly labeled `JOSEPH-VERBATIM` carries Joseph's authority;
- Claude/Codex analysis never authorizes external sends, destructive actions,
  purchases, publication choices, or scope expansion.

Every work notification should contain:

```text
Task-ID: <id>
Sender: <role, account, full UUID, process-start boundary>
Artifact: <path>
Commit: <full commit>
Review class/state: <ROUTINE|GATE> / <UNREVIEWED|REVIEWED|DISPUTED>
Requested action: <one sentence>
Message-ID: <durable mailbox id or repository receipt>
```

Claude Personal must distinguish Joseph's verbatim instruction from its own
interpretation, verify cited numbers against the tree, and visibly correct its
own errors. It is a remote explainer, not a trusted replacement for evidence.

## 6. Git and worktree discipline

- Give every account/session a distinct Git author identity. Do not use
  Joseph's identity for agent commits.
- Give each writer its own branch/worktree and unique output namespace.
- Record base commit, worktree path, writable paths, and full input hashes in
  the task packet.
- Review lanes are read-only. Always run `git status` after a review.
- Do not merge another lane's uncommitted state. Communicate by full commit
  IDs and exact artifact paths.
- If a branch is behind its upstream, do not create an authority-bearing merge
  or push until the divergence is reconciled deliberately.

## 7. Compute and storage discipline

Every compute-producing task declares before launch:

- expected node/GPU hours and queue;
- output paths and expected size;
- whether outputs are bit-reproducible from committed inputs;
- scratch/CFS/HPSS destination and retention owner;
- verification method (hash, structural scan, or both);
- supersession and release condition.

HPSS is a first-class design consideration, not cleanup afterthought. Preserve
irreplaceable or no-longer-reproducible inputs/products on tape; include tape
quota/headroom in production planning; and never delete a durable copy until a
named owner has verified its replacement and release condition. Current HPSS
facts and actions remain canonical in `OI-50`/`OI-55` of
[`../OPEN_ITEMS.md`](../OPEN_ITEMS.md), not here.

## 8. Day-to-day operating loop

1. Read and verify [`LIVE-STATE.md`](LIVE-STATE.md) against current `HEAD`.
2. Read [`FINDINGS.md`](FINDINGS.md), then the relevant code/status docs.
3. A selects the next dependency-ready task and fills a handoff packet.
4. The writer acknowledges exact inputs and owned paths before editing or
   launching compute.
5. The writer commits the full result bundle and sends a durable notification.
6. The required reviewer(s) inspect the original commit independently.
7. The owner records review state; Joseph-only choices go in
   [`USER-DECISIONS.md`](USER-DECISIONS.md).
8. Claude Personal gives Joseph a short explanation: decision, evidence,
   tradeoff, recommendation, and what happens next.
9. Close the task, write the next handoff, and rotate the session if a boundary
   or context trigger was reached.
