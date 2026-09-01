# FINDING 2026-09-01 — the `P` leg is already satisfied; `M` is the blocker, and §4.2 is dissolved

**CITABLE FOR:** the `P`-leg status table below, read off committed receipts.
**NOT CITABLE FOR** discharging any cause. Gate 2 remains **FAIL**; CAND `1 of 7`, QUOTED `0 of 7`.

Run at the `claude-school` k=0 lane's suggestion, as step 1 of a proposed grading sequence: **measure
whether the candidate's stamps satisfy `P` before grading anything**, because
`CRITERIA-20260811…md` §4.2 says the `P` leg of causes 1–4 is *"currently unsatisfiable from the
repository."* If that still held, grading would return UNRESOLVED on `P` by construction.

**It does not still hold.** §4.2 was written 2026-08-11 about **X**, and it proposed its own remedy —
*"The cheap fix is a receipt, not a re-run… That single artifact moves the P leg of four causes at
once and is the highest-leverage item in this document."* **That receipt was written on 2026-08-17
and is committed.** Nobody appears to have gone back and marked §4.2 satisfied.

## Measured — three tracked, predeclared receipts

| cause | `P` leg | evidence | branch |
|---|---|---|---|
| **1** | **MET** | `receipt_cause1_endpoint_census_5d.json` — *"per-band census committed, both endpoints present for every pair band, `Flux` exactly 100 contiguous"* | `C1` |
| **2** | discharged for the candidate 2026-08-12 | `SCOREBOARD:125`, candidate-only scope | — |
| **3** | **MET — for the CANDIDATE** | `receipt_candidate_stamps_5d.json` | `S1` |
| **4** | **MET — for the CANDIDATE** | same | `S1` |

`receipt_candidate_stamps_5d.json` is explicit that it reads *"the ADOPTION-CANDIDATE arms of job
`56720356` rather than off the test product of job `56695424`"*, and its verdict is that **both
candidate arms carry all six self-checked stamps and all three `upstream_*` values, matching the
predeclaration, with zero mismatches** — while **both July negative controls came back with every
stamp absent.** That is `(cause × artifact)` scoping working exactly as §0 describes: the same leg is
satisfiable for one artifact and not the other, and the receipt measured both.

## THE BLOCKER IS `M`, AND BOTH RECEIPTS SAY SO THEMSELVES

Neither receipt discharges anything, and each says why in its own words:

- `receipt_candidate_stamps_5d.json`: *"Under S1 this does NOT discharge cause 3 or cause 4: cause 4's
  `M` leg is recorded UNRESOLVED in CRITERIA §2 and no stamp read changes that, and cause 3's `M` is
  graded differently in `CRITERIA` §2 (`M(ii)` UNRESOLVED) than in §3 (MET). Both are judgements and
  neither is taken here."*
- `receipt_cause1_endpoint_census_5d.json`: *"`M` MEASURED is not `M` ACCEPTABLE. Whether this
  magnitude leaves X's published numbers standing is a physics-presentation judgement and is NOT taken
  here."*

**This confirms the school lane's ordering against my own.** I had placed `OI-172` and `OI-173`
alongside the grading as parallel blockers. They are not parallel — **they are the `M` leg**, and §0
calls `M` *"the leg that makes discharge falsifiable"* and *"the leg everyone skips."* Grading before
they are answered would produce UNRESOLVED verdicts the specification already determines.

## What each remaining cause actually needs

| cause | what is left | cost |
|---|---|---|
| **1** | `OI-172` — is the measured magnitude *acceptable*? A physics-presentation judgement | free, Joseph |
| **3** | `M(ii)` needs **its own measurement**; `CRITERIA:194` records `\gbdtAiEstTrace` CANNOT SERVE on footing | **~1 GPU-node-hour** |
| **4** | `OI-173` — what does `M` mean when the defect never touched the stored inputs? | free, Joseph |
| **7** | **criteria must be WRITTEN** — `CRITERIA`'s title covers causes 1, 2, 3, 4 and 6 only; cause 7 appears solely in §4.1 as a finding that its discharge is for a **different product** (FPS, 266 bins) | free, but it is drafting, not grading |
| **6** | a cluster rebuild it has never had | the expensive one |

**So of the four causes the 2026-08-31 ruling made gradeable, two are blocked on a free judgement,
one needs about a GPU-node-hour, and one needs criteria written before it can be graded at all.**

## Limits

- This reads committed receipts; it re-measures none of their contents.
- Cause 1's census is over **X's own bank** (`inputs.glob = uq_5d/universe_sweep_bkgaware/…`,
  `cv = products/5d/xsec_5d_MEFHC_5iter_lgbm.root`). `OI-172` records why that is not the artifact-scope
  problem it would be for a stamp leg — cause 1's `P` criterion is a **bank inventory, not a stamp**.
  **That reasoning is `OI-172`'s and is not re-derived here.**
- §4.2's text is left standing and unedited; this record supersedes it by reference, per the campaign's
  retirement-by-classification norm.
