# s5p (`OI-193`): re-forecast after the batch-3 looks began, and the checked slot-transfer option (2026-10-02)

**CITABLE FOR:** measured production progress and throughput to 2026-10-02T07:46Z; the revised terminal and cost
forecast under budget revision 6; the slot-transfer option (power's freed slots to NuWro and GiBUU), re-checked against
the meter's concurrency rule and the observed congestion, with its gain, cost, risk and decision window. **NOT
CITABLE FOR:** any decision, p-value or authorization. This is a projection, not a rule. Nothing is changed, and no
transition is authorized. Requested by Joseph through the peer session Codex (preparation only).

## 1. Measured (2026-10-02T07:46Z)

- **Looks:** 16 with B > 0, every one "continue" with k = 0 on both tests. The latest is GENIE MEC at B = 779
  (07:44Z), with its batch 4 submitted as `59192345` at throttle 3. MnvTune, CV, NuWro and GiBUU are on batch 3;
  power is on P1g, with 162 of its products.
- **Products:** 4,250 in total.
  - Rate: about 31 per hour over the last 5.8 h, about 39 per hour since 2026-10-01T15:51Z, and about 48.5 per hour
    averaged since 2026-09-30T18:22Z.
  - **The shared partition is congested again.** Only 4 of our 16 slots ran at 06:57Z and 07:46Z, the rest pending
    with reason `Resources`. The partition's pending count rose from 250 (10-01T15:51Z) to 624.
  - MEC batch 3 took 27.7 h at throttle 3, against 18.3 h for its batch 2.
- **Cost:** 19 closed batches measured 92.04 CPU node-h, a mean of 4.84. The production stage is at 143.04 of 209.647,
  counting open reservations. Envelope CPU is about 216 of 345.27. Verification/repair is 0 of 62.037.

## 2. Forecast (projection)

- **Remaining work:** about 3,770 experiments. That is about 3,345 calibration, assuming 7 batches per null at about
  1,370 products each, and about 425 power.
- **Aggregate rate projection:** terminal about **10-07T09Z** at the current 31/h, about **10-06T08Z** at the last
  16 h's 39/h, and about **10-05T13Z** at the 48.5/h average.
- **Critical path:** NuWro and GiBUU at throttle 2 still need batches b3–b6. At 26, 30 or 34 h per batch they finish
  about **10-06T05Z, 10-06T21Z or 10-07T13Z**.
- **Combined estimate: terminal about 2026-10-06 to 10-07.** It is later if the congestion persists. The earlier
  "10-06 midday" is the optimistic edge.
- **Cost:** about 194–199 CPU node-h for production (40–41 batches) against the 209.647 cap. One reservation-driven
  refusal and drain near the end remains possible, adding at most about a day. A terminal `budget` stop needs a mean
  above about 4.95 per batch; the measured mean is 4.84, so it remains unlikely.

## 3. The slot-transfer option, re-checked

**Constraint.** The meter enforces the 2-node cap on **open** admissions, and a lane's throttle is fixed when it
submits. So NuWro or GiBUU can submit at a higher throttle only after power's last array (P3g) has closed. Raising
both to 3 fits beside MEC, MnvTune and CV at 3 each: 15 of 16 slots.

| option | window (projected) | gain if uncongested | gain under current congestion | latest decision |
|---|---|---|---|---|
| A: NuWro and GiBUU 2 → 3 | from power's P3g closing to their b4 looks | about 16 h | **about 0**: our throttles are not binding while only 4 of 16 slots run | when power's P3g is submitted (re-dated at each power look) |
| B: both → 8 for b6 | from MEC, MnvTune and CV all being terminal to their b5 looks | about 19 h | small, unless the congestion clears | at the last of the MEC, MnvTune and CV final looks |

**The windows have moved.** Power has three sets left (P1g, P2g, P3g). At current rates, P3g closes not before about
10-04, later than the 10-03T19Z assumed on 10-01, so option A's window and latest decision move with it.

**Cost:** no change in billed compute (same batches, seeds and 8.5 reservations), no budget change and no rebind. The
new deploy's `budget.json` must be byte-identical to revision 6.

**Risk:** each transition is a two-lane runner move by the tested procedure. The steps:
1. `s5p_requeue.py` at the lane's current label, with the new throttle.
2. One commit and one new deploy.
3. A candidate validator and a post-start check, with the transition-r2 scripts parameterized to two lanes and the
   new throttle.

About 5 minutes of downtime; two six-lane moves have run cleanly. A raised submission made before the cap frees is
refused, and that refusal costs a drain.

**Recommendation: no transition now.** Under the present congestion neither option raises throughput: the
partition, not our throttles, decides how many of our tasks run. Re-check at each power look. If the congestion clears
and power's P3g is near closing, option A becomes worth about half a day and can be prepared for approval inside its
window. Option B is assessed when MEC, MnvTune and CV are terminal. Nothing within the authorization can make the
shared partition start more of our tasks: premium QOS is refused by the meter and costs 2×, and whole-node packing is
untested and runs only after terminal under a separate grant.

## 4. Unchanged

The frozen rules, the seeds and batches, the verification reserve, the cumulative caps, the terminal checklist
(`CHECKLIST-20261001-s5p-terminal-and-claims.md`) and the recompute lane's agreed comparison.
