# s5p (`OI-193`): throughput after the throttle change, revised ETA and cost forecast (2026-09-30, after batch 1 / P2)

**CITABLE FOR:** the measured batch durations and costs of batch 0 / P1 and batch 1 / P2, owed to the owner under the
2026-09-28T20:50Z scheduling change; the batch-1 looks; a projected ETA and an end-game forecast under the frozen
meter and queue rules; the owner's options, costed. **NOT CITABLE FOR:** any claim, p-value decision or rule change.
The looks are controller looks; rejections are decided only by the evaluator's Holm step at terminal. The forecast
is a projection, not a rule, and nothing is changed by this record.

## 1. Measured (to 2026-09-30T19:47Z)

Each duration runs from a batch's submission to its look, which the runner makes when the array leaves the scheduler.

| lane | batch 0 / P1 (throttle 2) | batch 1 / P2 (throttle) | batch-1 look |
|---|---:|---:|---|
| power | 21.5 h | 22.8 h (3) | P2 final 195 of 200; P3 submitted 12:30Z |
| MnvTune_v1 | 23.1 h | 23.4 h (3) | B = 393, k = 0 / 0, continue (min 1200) |
| GENIE_2_12_10_CV | 23.4 h | 26.2 h (3) | B = 393, k = 0 / 0, continue (min 1200) |
| GENIE_2_12_10_MEC | 18.9 h | 22.7 h (3) | B = 387, k = 0 / 0, continue |
| NuWro_21_09 | 23.2 h | 28.4 h (2) | B = 397, k = 0 / 0, continue |
| GiBUU_2019 | 23.7 h | 27.6 h (2) | B = 395, k = 0 / 0, continue |

- **Throughput: the throttle change produced no measurable gain.**
  - Total product rate: about 49 per hour in both phases (1,166 products in about 23.7 h for batch 0 / P1, and
    1,340 from 2026-09-29T16:33Z to 2026-09-30T19:47Z).
  - Every lane slowed in batch 1, the throttle-3 lanes by about 10% on average and the throttle-2 lanes by about 19%.
  - The arrays were mostly pending with reason `Resources` on the shared partition (757 pending jobs on 09-29), so the
    partition, not the throttle, limits throughput.
- **Seed losses:** batch 1 lost fewer seeds than batch 0: 13 of 1,200 (1.1%), against 34 of about 1,200 (about 3%).
  There are 26 time-limit kills in total, and no other failure.
- **Cost:** 12 closed batches measured 56.293 CPU node-h, a mean of 4.691 (SD 0.400, SE 0.115). Batch 0 averaged 4.79
  and batch 1 averaged 4.59 (receipt `state/s5p/diag/meter-measure-batch1-report-20260930T1947Z.json`).
  - At 19:47Z the production stage was charged 107.295 of 200, including six open reservations of 8.5.
  - Envelope CPU: 180.787 of 345.27. The verification/repair stage is untouched (0 of 62.037).

## 2. Forecast (projection; `state/s5p/diag/s5p_endgame_forecast_20260930.py` → `endgame-forecast-20260930T1947Z.txt`)

**Assumptions:**
- **Batches still needed:** at about 1–3% loss per batch, six batches give B ≈ 1,180–1,190. That is below both the
  1,200 floor of the MnvTune and GENIE CV nulls and the B ≈ 1,196 at which a k = 0 null's 99.5% upper end falls
  under 0.005. So each calibration null is expected to need **7 batches**; NuWro, with 3 losses so far, may need
  only 6. Power needs 6 sets, so about 40–41 batches in all, 12 of them closed.
- **Batch duration:** each lane's latest batch duration is assumed to persist.

**The end game under the frozen rules.** Each running lane always holds one open batch charged at 8.5, against a
measured cost of about 4.7, so near the end the reservation squeeze makes the meter refuse a submission. The queue
line then drains until no s5p job is queued, retries once, and writes a terminal `budget` status if refused again.

| cost / batch | production cap 200 (frozen) | cap 209.647 (unallocated moved in) |
|---|---|---|
| 4.69 (the measured mean) | one refusal (CV b6, about 10-05T02Z); drain; retry admitted; **terminal about 10-07T15–19Z**; about 187–192 measured | no refusal; **terminal about 10-06T13–17Z** |
| 4.83 | two refusals; if NuWro needs 7 batches, **NuWro ends with a terminal `budget` status at 6 batches** (B ≈ 1,190); terminal about 10-07T12Z | no refusal; about 10-06T13–17Z |
| 4.95 | two refusals; **GiBUU ends `budget` at 6 batches** if NuWro needs 7; terminal about 10-07/08 | at most one drain; about 10-06/07 |

**Readings:**
- **Terminal is expected around 2026-10-06 to 10-08.** With no binding cap it would be about 10-06T17Z; at the
  measured mean, the frozen reservation squeeze adds about a day.
- **A terminal `budget` status becomes likely if the remaining batches average above about 4.8.** That is about one
  SE above the measured mean. It would end one external null at B ≈ 1,190. Its p stays valid at the B reached,
  and a k = 0 decision at 0.005 stays determinable (B ≥ 737). The record would show `budget`, not `rule met`.
- **The power lane is expected to finish about 10-04**, after which its three slots stay idle (throttles are fixed
  per array).

## 3. Disposition and the owner's options

**Intervention is not justified now.** At the measured mean the frozen rules complete every lane, and nothing binds
before about 10-04T12Z.

| option | effect | cost / risk |
|---|---|---|
| A. no change (frozen) | terminal about 10-07; a terminal `budget` stop for one external null if the cost/batch drifts above about 4.8 | none now |
| B. budget revision: move the unallocated 9.647 CPU node-h into production (200 → 209.647) | removes the refusals up to about 4.83/batch and the `budget`-stop risk up to about 4.95; terminal about 1 day earlier | an owner decision; needs a ledger `rebind` and a **coordinated six-runner transition** to a new deploy (finding s5p-F5), done while every lane waits on an array, and before about 10-04 |
| C. give power's slots to NuWro/GiBUU after about 10-04 | small, given the partition-bound throughput shown above | a scheduling change plus runner transitions; not recommended |

**Next checkpoint.** The campaign re-forecasts at the batch-3 looks (about 10-02). If the running mean exceeds about
4.75, or the forecast shows a `budget` stop, it will prepare option B's transition and its checks first, and only
then ask the owner for approval. The latest safe execution is before the first projected refusal (about 10-04T12Z).

**Campaign-review note** (the advisory [`CAMPAIGN-REVIEW-20260929.md`](CAMPAIGN-REVIEW-20260929.md), committed at
`093ad566`):
- **Decision answered:** the frozen joint-5D inference of amendment 7.
- **Terminal conditions:** those of amendment 7 and handoff §8. An honest terminal includes `budget` or undetermined
  outcomes.
- **Owner:** this campaign session.
- **Independent reviewer:** the recompute lane, reviewed code 0142a228.
- **Review and repair budget:** retry limits S2 and the 20% verification/repair reserve, both unchanged.
- **Reassessment:** at the checkpoint above.
