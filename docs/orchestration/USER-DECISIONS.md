# Joseph decision register

**Status:** LIVE pointer register. **Review state:** UNREVIEWED. This file records choices that require
Joseph's authority. It does not duplicate physics facts, verified numbers, or
open-item narratives; those remain in their canonical homes.

## Rules

- Valid states: `NEEDS JOSEPH`, `DECIDED`, `IMPLEMENTED`, `SUPERSEDED`.
- Record Joseph's words verbatim, with date/time and source context. Put agent
  interpretation in a separately labeled field.
- A recommendation is not authorization. Silence is not authorization.
- Link exact evidence, owning open item, and proposed implementation commit.
- When Joseph decides, record the choice here first; the owning worker then
  updates the canonical open item/status and records the implementation commit.
- Claude Personal may explain or relay a choice but may not silently convert
  its interpretation into Joseph's decision.

## Active decisions

| ID | State | Choice Joseph must make | Canonical evidence/owner | Recommendation | Implementation owner |
|---|---|---|---|---|---|
| UD-001 | NEEDS JOSEPH | After the current atomic tasks finish, authorize the staged rotation to fresh bounded A–D sessions and a fresh Claude Personal explainer session. | [`SESSION-WORKFLOW.md`](SESSION-WORKFLOW.md); current process state remains in [`LIVE-STATE.md`](LIVE-STATE.md). | Rotate at task boundaries; preserve old sessions as continuity-only. Do not interrupt active writers. | Claude-school A coordinates; each role closes its own handoff. |
| UD-002 | NEEDS JOSEPH | Choose whether the production definition should retain exact MAT behavior (`135` MeV subtraction) or use the physical charged-pion mass (`139.57` MeV). | `OI-30` in [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md). | Finish the covariance-projected materiality comparison, then choose explicitly; do not describe exact MAT compatibility and physical-mass correctness as the same goal. | B analyzes; C implements only after the decision. |
| UD-003 | NEEDS JOSEPH | Choose the reco-underflow repair/adoption path that governs whether the broader E_available species rule is adopted in production. | `OI-56` in [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md). | Use the existing offline sensitivity result to inform the choice; keep production unchanged until the coupled choice is explicit. | B analyzes; C implements after the decision. |

## Recorded decisions

No workflow-era decisions have been recorded yet. Move a row here only after
Joseph's verbatim choice is captured.

## Operational safeguards that are not decisions

- Do not interrupt or repurpose an active writer merely to enact this workflow.
- Current jobs, owners, unique write paths, and declared gates are taken only
  from a freshly regenerated [`LIVE-STATE.md`](LIVE-STATE.md).
- Current HPSS retention and verification actions remain in `OI-50`/`OI-55` of
  [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md).

## Entry template

```markdown
### UD-NNN — <short choice>

- State: NEEDS JOSEPH | DECIDED | IMPLEMENTED | SUPERSEDED
- Created (UTC): YYYY-MM-DDTHH:MM:SSZ
- Owning open item: OI-NN or NONE
- Decision requested: <one sentence>
- Options and consequences:
  - A: <consequence>
  - B: <consequence>
- Agent recommendation: <recommendation and why>
- Joseph verbatim: <exact quote or PENDING>
- Source context: <chat/message ID/date>
- Decision recorded (UTC): <timestamp or PENDING>
- Implementation owner: <role/session>
- Implementation commit: <full commit or PENDING>
- Verification/review commit: <full commit or PENDING>
```
