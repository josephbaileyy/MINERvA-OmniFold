# s5p (`OI-193`): owner decision — bounded production-budget extension (budget revision 7, 2026-10-04)

**CITABLE FOR:**
- the owner's decision to extend the s5p production budget, verbatim, with its timing and arithmetic;
- the new cumulative CPU ceiling and pool, and the reserve rule kept;
- the 10%-of-uncommitted check;
- what changes and what does not.

**NOT CITABLE FOR:** any scientific result, criterion or decision. No statistic, stopping rule, terminal status, seed,
batch or estimator setting changes. It is not a further increase: "further increases require my decision."

## 1. The decision (Joseph, verbatim)

Given in the campaign session on 2026-10-04, at about 04:50Z, in answer to the campaign's projection that one to three
nulls would end with the frozen `budget` status (campaign-state incident 2026-10-04T04:45Z):

> Choose B. My priority is the strongest defensible scientific conclusions from the frozen campaign.
>
> I authorize up to +25 CPU node-hours of additional production budget, funded by raising the cumulative cap, with the
> required verification/repair reserve preserved. Calculate and record the corresponding cumulative ceiling and execute
> budget revision 7 and the coordinated runner transition.
>
> Keep all scientific criteria unchanged. Complete the planned stopping procedure and independent verification, and
> report the achieved precision, power, and any unresolved limitations. This is a bounded extension; further increases
> require my decision.

The text arrived as pasted content. The campaign therefore asked the owner to confirm it, and to choose how the
reserve should be read. The question:

> "Is the pasted text your decision to add production budget, and which reserve reading should I use?"

The selected answer:

> "Yes — ceiling 376.52 (Recommended)" (production +25; cumulative cap 345.27 → 376.52; pool 310.184 → 341.434;
> verification/repair stays 20% of the pool, 62.037 → 68.287).

## 2. Arithmetic (CPU, billed node-hours)

| quantity | before (rev 6) | after (rev 7) | basis |
|---|---:|---:|---|
| production stage | 209.647 | **234.647** | +25.0, the authorized maximum |
| verification/repair | 62.037 | **68.287** | 20% of the new pool (the authorization's "Reserve 20%") |
| campaign pool (cap) | 310.184 | **341.434** | 234.647 + 68.287 + the finished stages 24.0 + 2.3 + 12.2 |
| cumulative ceiling | 345.27 | **376.52** | pool + prior charges 35.086 (s5c 20.086, s5n 4.601, s5e 10.399) |
| GPU | unchanged | unchanged | 114.904 node-h pool, 500 A100-h cumulative |

The ceiling rises by 31.25 rather than 25 because keeping the reserve at 20% of the pool takes a further 6.25.

**The 10% rule** ("each new pool … capped at 10% of current uncommitted allocation after reservations"), measured on
2026-10-04 at 04:41Z (`state/s5p/transition-r3/allocation-measurement-20261004T0441Z.txt`):
- m3246 had 20,000 allocated and 16,817.7 charged.
- 131 m3246 rows were pending or running, all of them this campaign's, holding about 32.75 node-h of reservations.
- So about 3,149.6 was uncommitted, and 10% of it is **314.96**.

| compared with 314.96 | value | result |
|---|---:|---|
| the new grant, the increment | 31.25 | passes |
| the pool's unspent remainder | about 113.9 | passes |
| the literal enlarged pool, including what is already spent | 341.434 | exceeds |

The original pool passed the rule when it was created (≤ 341.63 on 2026-09-26). The campaign reads "each new pool" as
the new grant, and records the literal comparison here so that reading is visible.

## 3. Timing and disclosure

The decision was made during production, after the controllers' looks had become visible: 21 looks, every one
"continue", with total k = 0 everywhere and NuWro's shape k = 1 at B = 779.

It changes only how far the frozen sequential procedure can run before the meter refuses a submission. The aim is to
let the planned stopping procedure complete rather than end in `budget` stops. It changes no statistic, criterion or
decision rule.

The motivation is retrospective, as the authorization requires. A shared-node slowdown raised timeouts to about 25% of
tasks over the 36 h to 2026-10-04T04Z, and lifted batch costs from about 4.8 to about 6.1 CPU node-h. With those costs
the projected end-game refusals would arrive before every null reached its stopping rule.

## 4. Execution

- Budget revision 7 is made live in `state/s5p/budget.json`.
- The ledger is rebound, and the six runners move to a new deploy through the coordinated transition r3. The procedure
  is the same as transition r2 (`RUNBOOK-20260930-s5p-transition-r2-budget-rev6.md` §3–4): preflight, two commits (A = rollback, rev 6; B = rev 7),
  two new deploys, validation, stop, rebind and start, and post-check.
- The scripts are `state/s5p/transition-r3/` (`plan.json`, `validate_deploy_r3.py`, `runners_r3.sh`).
- The execution record is the campaign-state incident written at completion.
- From then on every meter call must run from the r3 execution deploy.
