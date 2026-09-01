# DECISION 2026-09-01 — Joseph RATIFIES the `OI-177` per-arm ceilings

**CITABLE FOR:** the amended per-arm decision ceilings of
`PROPOSAL-20260830-forward-only-rehearsal.md` §6, and the discharge of `OI-177`.
**NOT CITABLE FOR:** any gate movement, leg 6, the M(ii) family, adoption of any covariance, or any
authorization to launch. **Gate 2 remains FAIL. Nothing is adopted. CAND `1 of 7`, QUOTED `0 of 7`.**

## Authority

Joseph, 2026-09-01, in his own turn, answering the recommendation put to him with the arm-6 caveat
stated in the same message:

> *"I sign"*

Direct, not relayed. What was on the table when he signed, verbatim from that message: *"arm 2 -> 8,
arm 5 -> 60, arm 6 -> 40 task-hours, sum restated 70 GPU / 113 CPU"*, together with the disclosure
that **of the three figures, arm 6's is the least well-supported** and that arm 4 was deliberately
**not** proposed for change.

## THE RATIFIED TABLE

Unit: **task-hours**, per `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`. GPU-partition
work in A100 task-hours, CPU-partition work in CPU task-hours, auxiliary cores on a GPU allocation not
double-counted — §6's own convention, unchanged.

| arm | `aa67c426` (R1) | round 2 (R2) | §6 ceiling | **RATIFIED** | change |
|---|---:|---:|---:|---:|---|
| 1 bootstrap `boot5dG` | 15.38 | 14.86 | 20 GPU | **20 GPU** | unchanged |
| 2 seed split `ssplit5d` | 5.43 | 5.83 | 5 CPU | **8 CPU** | **+3** |
| 3 detector `det5dBKG` | 13.88 | 13.76 | 20 GPU | **20 GPU** | unchanged |
| 4 sweep `sweep5dBKGrun` | 25.54 | 26.28 | 30 GPU | **30 GPU** | unchanged |
| 5 uthrow run `uthrow5d_runF` | 30.94 | **49.11** | 30 CPU | **60 CPU** | **+30** |
| 6 uthrow block `uthrow5d_block` | 30.01 | 31.01 | 30 CPU | **40 CPU** | **+10** |
| 7 combine `uthrow5d_combF` | 0.42 | 0.58 | 5 CPU | **5 CPU** | unchanged |
| **sum of decision ceilings** | | | 70 / 70 | **70 GPU / 113 CPU** | CPU **+43** |

**Every ratified ceiling exceeds BOTH observed actuals on its arm** — checked per arm, not on the
sums, because a sum can be satisfied while a member is breached. Sums re-derived: GPU `20+20+30 = 70`;
CPU `8+60+40+5 = 113`.

**`PROPOSAL-20260830-forward-only-rehearsal.md` IS NOT EDITED.** It is `ARCHIVAL`, `terminal`,
`immutable:yes` with 14 inbound references, and this campaign retires by classification, never by
rewriting. §6's table stands as the historical record of what was authorized on 2026-08-30; **this
decision and `AMENDMENT-20260831-oi177-per-arm-ceilings.md` supersede it by reference from
2026-09-01.** A reader of §6 must follow its `OI-177` route to reach the live figures.

## What the ratification rests on, and where it is thin

**n=2 complete populations**, both at full declared array with zero non-`COMPLETED` tasks:
`aa67c426` (2026-08-24) and round 2 (jobs `57753239`–`57753248`, finished 2026-09-01T08:57:51Z,
374/374). `sacct` summed over **distinct task identities** — row-counting inflates to 447.

**Arm 6's basis is the weakest of the three and Joseph signed with that disclosed.** Its `+3.3%`
round-over-round is *not* reproducibility: R1 min/median/max `39.4 / 52.2 / 518.3` min against R2
`40.5 / 81.9 / 289.0`. Two unlike distributions whose sums coincide, R1's mean carried by a single
8.6-hour outlier (sd `99.9` on a mean of `85.7`). **40 covers both observed sums, which is the test
that matters for a ceiling**, but a third sample would be worth having before this figure is treated
as well-founded. Recorded here rather than in a footnote because a later lane inheriting `40` should
inherit its support too.

**Arm 4 holds at 30 and is the thinnest margin.** Not breached, and raising an unbreached ceiling
widens an authorization for no measured reason.

### ⚠ A denominator correction to the figure quoted at signature time

Arm 4's headroom was put to Joseph as **12.4%**. That is `(30 − 26.28) / 30` — divided by the
**ceiling**. Every other headroom figure in the amendment (§3's `30 / 47 / 44 / 17 / 29 / 33 %`) is
divided by the **actual**. Under the document's own convention arm 4 is **14.2%**, not 12.4%.
**The two numbers describe the same margin and neither changes any decision** — arm 4 was not
proposed for change under either — but the amendment mixed denominators without saying so, which is
this campaign's own *name-the-implicit-denominator* hazard appearing inside the document that files
it. Stated in full so the successor table is read on one convention:

| arm | R2 actual | ratified | headroom **/actual** | headroom /ceiling |
|---|---:|---:|---:|---:|
| 1 bootstrap | 14.86 | 20 | **34.6%** | 25.7% |
| 2 seed split | 5.83 | 8 | **37.2%** | 27.1% |
| 3 detector | 13.76 | 20 | **45.3%** | 31.2% |
| 4 sweep | 26.28 | 30 | **14.2%** | 12.4% |
| 5 uthrow run | 49.11 | 60 | **22.2%** | 18.1% |
| 6 uthrow block | 31.01 | 40 | **29.0%** | 22.5% |
| 7 combine | 0.58 | 5 | **762%** | 88.4% |

## The delegation boundary is not touched

The largest ratified ceiling is **60**, and the largest measured arm is **49.11** — `10.2×` inside the
strictly-under-500 threshold that reserves the call for Joseph. **No arm approaches it, so nothing here
tests or moves that boundary.** Note also that `DEFECT-20260825:172-176` records the `500` threshold as
a Codex session's own written claim about its own authority and **not Joseph speaking**; this decision
does not convert it into his words either, and must not be cited as evidence that he set 500.

## What this does NOT do

It does not move Gate 1 or Gate 2, discharge any quarantine cause, adopt any covariance, authorize any
compute, or lift the leg-6 prohibition. It does not ratify the *estimate* column as a forecast for any
future run — §3c and §3e record that CPU-partition arms are not reproducible in either elapsed or
`TotalCPU` between scheduler regimes, and these ceilings are set from the **worst observed regime**
rather than from a prediction. A third run may exceed them; that would be a new `OI-*`, not a defect
in this signature.

## Provenance of the numbers

Re-derived from `sacct` by the producing lane and independently confirmed against the personal-account
orchestrator's table to the digit on all seven arms. Round-2 outcome:
`RECORD-20260901-k0r2-round2-outcome.md`. Method, both rounds' actuals, the three-unit reconciliation
and the floor/median analysis: `AMENDMENT-20260831-oi177-per-arm-ceilings.md` §§1–3e. Unit ruling:
`DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`.
