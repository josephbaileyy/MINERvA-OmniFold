# DECISION 2026-10-19 — Joseph: methods-paper framing first; compute approved for the physics-measurement work

**Recorded by** the paper-tighten lane, as director (Stage F). After plain-language pass 2 (PR #162, `main`
`a148f22f`), the director told Joseph that the outside referees recommend major revision, and set out two framings:
- **a methods paper** with conditional generator tests;
- **a physics-measurement paper**, which would need the calorimetric response propagated through the calibration,
  the hybrid null hypotheses checked against independently simulated generator events, the carbon-versus-hydrocarbon
  difference quantified, and validated five-dimensional uncertainties.

Joseph's answer, verbatim:

> yes if this is what we need for a physics-measurement paper, I approve using all of our compute to do these things.
> I think it makes sense to do the methods framing target first too. how do you suggest we do this work? do you want
> to do the methods paper framing and work with the gpt and gemini reviewers and then you give me a handoff to give to
> a session to do the physics measurment paper? or do you want to do both? up to you

sha256 of the text plus a final newline begins `43e4900b9afa538f`.

## 1. What is decided

| item | decision | the director's reading |
|---|---|---|
| **Target order** | "do the methods framing target first" | The paper is recast as a methods paper with conditional generator tests, and that is the first target. "Target" is not a submission: Joseph's review with Ben, and every outward act (J6), still come first |
| **Compute** | "I approve using all of our compute to do these things" | Compute may be spent on the physics-measurement work items listed above, and on the methods-paper items that need computation. "Our compute" is read as Joseph's own share of the allocations (his user allocation within `m3246` and `m3246_g`, and Delta `bhvk`), **not** the whole `m3246` group allocation, which other members also use. The balances are measured before any plan is costed |
| **The 2026-10-10 pause** | reopened for item 4 | See §1a. The validated five-dimensional uncertainties need further 5D work, which Joseph paused on 2026-10-10. This approval removes the budget limit for that purpose. It does not show that a route exists: the records call the limitation scientific, not financial (`RECORD-20260927-s5p-stage2-exit.md:143-145`; `DELIVERY-20261006-s5p-campaign-terminal.md:148-151`), so the first phase must find a method before production |
| **Organization** | "up to you" | See §2 |

## 1a. The 2026-10-10 disposition, recorded here for the first time

Joseph's disposition of the D-ID diagnostic on 2026-10-10 was never committed. The committed D-ID report still lists the
endpoint-scope question as open (`state/next-preparation-20261009/d-id/REPORT.md:28`). The director's session memory
recorded it as follows:
- D-ID is accepted as a completed bounded diagnostic.
- Further GBDT production and tuning is paused: no I1, no I2, no strict-bounds study, no more iterations, no s5p
  extension.
- The joint-5D endpoint is not changed to coarser or selected functionals. Joseph keeps it as the long-term objective,
  but there is no affordable validated route to it now.

This decision lifts the pause for the physics-measurement work only. The endpoint stays as Joseph left it.

## 1b. Compute, measured 2026-10-19 16:40 UTC (`iris`; [`state/measurement-paper/iris-20261019.txt`](state/measurement-paper/iris-20261019.txt))

| project | Joseph (user) | group | left for the group |
|---|---|---|---|
| `m3246` CPU | 2,078.8 of 10,000 | 17,672.2 of 20,000 | 2,327.8 |
| `m3246_g` GPU | 1,295.8 of 90,000 | 133,774.0 of 180,000 | 46,226.0 |

- Joseph's own CPU headroom (7,921) exceeds what is left in the group pool, so **the group pool is the binding limit**.
- Since 2026-10-14 (17,193.7) the group has charged 478.5 CPU node-h, about 89 per day, and 35.8 of those were
  Joseph's. At that rate the CPU pool runs out around mid-November, whatever this project does.
- GPU is about 860 node-h per day, roughly 50 days left.
- How much of the shared group pool the measurement work may take is Joseph's call. Until he says otherwise, the
  director keeps the measurement work within half the CPU pool remaining at each grant.
- CFS `josephrb` measured 3.6 TB, over Joseph's 3 TB rule (1.1 TB on 2026-10-05). The measurement session writes
  nothing to CFS until this is cleared with Joseph.
- This approval is separate from the 2D closeout delegation (≤ 700 node-h, AUTHORIZATION-20261012), which is
  unchanged. It is the authorization for a new scientific analysis that `AGENTS.md` requires.

## 2. Organization (the director's choice)

- **The director** does the methods-paper framing with the outside reviewers (agy Gemini and codex-school GPT-6.1-sol),
  under the brief [`state/2d-closeout/stageF/METHODS-FRAMING.md`](state/2d-closeout/stageF/METHODS-FRAMING.md). The
  director keeps Stage C oversight and binding, the playlist-consistency construction and Stage F integration
  (DECISION 2026-10-16).
- **A separate session** does the physics-measurement work, from the handoff
  [`state/measurement-paper/HANDOFF-20261019.md`](state/measurement-paper/HANDOFF-20261019.md). Joseph opens it.
  It owns `docs/orchestration/state/measurement-paper/**` and its own study code and outputs.
- **Why two sessions.** The measurement items are compute campaigns that will run for weeks and need their own
  context and cluster monitoring. The methods paper is writing and review, and it should reach the Ben review without
  waiting on those campaigns.
- **The boundary.**
  - The measurement session does not edit the deliverables (paper, note, primer). Its results reach them through the
    director's Stage F integration.
  - Each campaign is specified and predeclared, with its acceptance criteria and cost, in a committed plan before
    production. The director records each compute grant against that plan, each job stays under 12 h, and the
    standing rules hold.
  - Claims remain Joseph's decisions.

## 3. Not changed

- Joseph is "not ready to publish anything yet". Nothing is submitted, deposited or tagged, and no coauthor,
  collaboration, MINERvA or NERSC contact is made without his explicit act.
- J3–J5 stay provisional until the review with Ben.
- New inference and delegation use only codex-school2, codex-school, claude-school and agy (DECISION 2026-10-16).
- **Cluster access** needs a NERSC certificate renewal, which is Joseph's act (`sshproxy` with his password and MFA).
  The certificate expired at 2026-10-19 09:15 UTC.
