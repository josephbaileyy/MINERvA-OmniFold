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
| UD-003 | NEEDS JOSEPH | Choose the reco-underflow repair/adoption path that governs whether the broader E_available species rule is adopted in production. | `OI-56` in [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md). | Use the existing offline sensitivity result to inform the choice; keep production unchanged until the coupled choice is explicit. | B analyzes; C implements after the decision. |

## Recorded decisions

Move a row here only after Joseph's verbatim choice is captured.

### UD-002 — keep 135 MeV as the defined constant in the E_avail definition

- State: DECIDED
- Created (UTC): 2026-08-13T12:36:16Z (`39b0021e8`, as a row of *Active decisions*)
- Owning open item: `OI-30`, retired 2026-10-31
- Decision requested: Choose whether the production definition should retain exact MAT behavior (`135` MeV
  subtraction) or use the physical charged-pion mass (`139.57` MeV).
- Options and consequences:
  - A: keep `135` MeV as a defined constant of the observable, as the paper prints it.
  - B: use `139.57` MeV, which changes the observable's definition.
- Agent recommendation: A, as put to Joseph: *"UD-002: keep 135 MeV as the defined constant in the E_avail
  definition (the paper already says 'a defined constant of 135 MeV'; the alternative was 139.57 MeV)?"*
- Joseph verbatim: "Keep 135 MeV (Recommended)" (sha256 of the text plus a final newline begins
  `2f53fcc2fb3a1160`)
- Source context: Joseph's answer to the director, 2026-10-31, recorded in
  [`DECISION-20261031-joseph-oi51-oi137-ud002.md`](DECISION-20261031-joseph-oi51-oi137-ud002.md#what-is-decided)
  item 3 (#603).
- Decision recorded (UTC): 2026-10-31T22:03:02Z (`96f539cd9`, the decision record's commit)
- Agent interpretation: no change is owed. The paper says the constant *"is used consistently by the analysis and
  every prediction"* (`docs/analysis-note/paper_body.tex:35` @ `4ede47e34`).
- Reopened for pricing 2026-10-31, without being reversed:
  [`DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md`](DECISION-20261031-joseph-eavail-switch-pricing-and-edits.md)
  item 1 (`b1348c794`), with Joseph's verbatim "Price a switch to 139.57".
  - The price is
    [`ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md`](ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md)
    (#622).
  - Its §7 measures the switch's first-order size on the 16 reported cells: at most 0.19σ per cell, and 0.42σ as one
    coherent shift, under the reported covariance (0.21σ and 0.42σ without the run-period block C_PL,5D).
- Kept 2026-11-01: Joseph verbatim "Keep 135 (Recommended)" (sha256 of the text plus a final newline begins
  `d13ef6f830671ea8`).
  - Recorded in [`DECISION-20261101-joseph-eavail-keep-135.md`](DECISION-20261101-joseph-eavail-keep-135.md) (#636).
  - Decision recorded (UTC): 2026-11-01T13:31:32Z (`dfd153aa8`).
  - State stays DECIDED, A.
  - That decision's item 2, the departure sentence after Eq. (1), belongs to the paper rewrite lane.
  - Its item 3, the correction of `docs/EAVAIL_DEFINITION.md`, is this row's follow-up.
- Implementation owner: none
- Implementation commit: none owed
- Verification/review commit: PENDING

## Operational safeguards that are not decisions

- Do not interrupt or repurpose an active writer merely to enact this workflow.
- Current jobs, owners, unique write paths, and declared gates are taken only
  from a freshly regenerated [`LIVE-STATE.md`](LIVE-STATE.md).
- HPSS: `OI-50`, `OI-52` and `OI-55` of [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md) are retired. The latest
  reading (446 of 512 GiB on the user quota, 2026-10-31) is in
  [`RECORD-20261031-close-items-waiting-joseph-rows-retired.md`](RECORD-20261031-close-items-waiting-joseph-rows-retired.md#4-oi-52-retired-with-josephs-iris-reading)
  §4. A new retention or verification action is filed as a new open item.

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
