# AUTHORIZATION 2026-10-12 — 2D closeout: one walltime retry of P4 TIMEOUT jobs (a deviation from P4 DESIGN's retry rule)

**Issued by** the paper-tighten lane, as director, under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md) §3,
inside the bounds of
[`AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md`](AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md).
The 2d closer requested it at about 21:34Z, and the decision was sent by SendMessage at about 21:40Z. This
record restates that decision. The closer quotes the message itself in the diagnostics REPORT.

**CITABLE FOR:**
- cancelling the P4 jobs that cannot finish in 2 h;
- one resubmission of each P4 job that ends in TIMEOUT on its own 2 h limit, with the walltimes below.

**NOT CITABLE FOR:**
- any change to the binary, script, configuration, resources (other than walltime) or job split;
- a second retry;
- P0–P3, production, or anything outside the diagnostics grant.

## The rule and the deviation

P4 DESIGN §5 (`docs/orchestration/state/2d-closeout/stageB/diagnostics/p4/DESIGN.md` on
`closeout/stageb-diagnostics-20261012` at `bb4a4f2d`) allows a retry "only after a diagnosed
infrastructure cause (node failure, filesystem error, scheduler kill not caused by the job's own limits)".
A TIMEOUT on the job's own 2 h limit is excluded, so this retry is a deviation from that rule.

The 2 h walltime was priced from the one-file smoke as 98 × 17–30 s ≈ 0.5–0.8 h for 1M. The real loops
run over 6–16 M reco entries and 200–280 data files.

**Measured** with `sacct -X` from this lane at about 21:40Z:

| job | state |
|---|---|
| 59713341_0 (1A) | TIMEOUT at 02:00:04 |
| 1B | COMPLETED |
| 1C | COMPLETED |
| 1L | COMPLETED |
| 1D | RUNNING |
| 1E | RUNNING |
| 1F | RUNNING |
| 1G | RUNNING |
| 1M | RUNNING |
| 1N | PENDING |
| 1O | PENDING |
| 1P | PENDING |
| ctl1L | PENDING |
| P5 59713367 | PENDING |
| P5 59713368 | PENDING |

**Why the deviation does not weaken the rule's purpose.** The rule exists so that a result never selects a
rerun. Here:
- the cause is a pricing error that affects every job alike;
- the decision covers every job that times out, whatever its content;
- no G1 number from any job retried here has been read. The only G1 number read so far is 1B's, and 1B is
  not retried.

## Bounds

| item | value |
|---|---|
| cancel | 1D, 1E, 1F, 1G and 1M (running) and 1N (pending) |
| resubmit | 1A, 1D, 1E, 1F and 1G at `--time=06:00:00` |
| 1M, 1N | walltime = 1.5 × a projection from measured per-entry and per-data-file loop rates (1M's own signal-reco rate; 1A's or 1C's background and data rates), rounded up, capped at 11:30:00. The arithmetic goes in the REPORT. A projection above 11:30 means that job is not submitted and the closer reports to the director |
| identical | the sha-checked binary, script, job names `2dc_B4_<tag>`, 4 CPUs, `--mem=7600M`, shared QOS |
| partial output | moved to `out/<tag>.failed-<jobid>` by the recorded move of DESIGN §5. No G1 number is read from partial output |
| one retry | any P4 job that times out again, or that times out for the first time later (1O, 1P and ctl1L included), gets at most this one walltime retry. A second TIMEOUT is INCONCLUSIVE (walltime), with no further retry without the director. Other failures follow DESIGN §5 unchanged |
| P5 | before 59713367/8 start, the closer checks whether their caps (1:00 and 1:30) were priced the same way. If either cap is short, it is cancelled and resubmitted at 1.5 × a measured projection (< 12 h) before it runs |
| ceiling | unchanged: ≤ 3.0 charged CPU node-h for P4+P5, retries included, recomputed from `sacct` before each launch; the seed-43 pair keeps its declared check on actual charges |
| record | the deviation, its cause, this decision, the per-job walltimes and the moves go in `docs/orchestration/state/2d-closeout/stageB/diagnostics/REPORT.md` |

## Budget at decision time

The closer's figures are recomputed here with charge = elapsed × 4/256:

| item | node-h |
|---|---|
| P4 worst case at 6 h caps | 0.89 |
| longer 1M and 1N caps (up to 2 × 5.5 h × 4/256) | +0.17 |
| P5 seed-42 at its enforced caps | +1.25 |
| **total** | **≈ 2.31 of 3.0** |
