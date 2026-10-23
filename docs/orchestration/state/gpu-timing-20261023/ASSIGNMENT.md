# Assignment: GPU-node timing of the 5D unfold unit (2026-10-23)

**Assigned by** the paper-tighten lane, as director. **Assigned to** the measurement session, under its phase-1
grant (`state/measurement-paper/BINDING-PHASE1-20261019.md:53`: at most 35 charged CPU node-h and 3 GPU node-h on
`m3246` / `m3246_g`; GPU charged so far 0, from `phase0/LEDGER.tsv` and `phase1/LEDGER.tsv`).

**This is a timing measurement, not a result.** It gives no coverage, uncertainty or claim, and it authorizes no
campaign. Joseph's criterion for any campaign it prices is recorded in
`DECISION-20261023-joseph-gpu-test-and-campaign-criterion.md`.

## Why

The only cost on the record for a brute-force 5D validation is CPU-based: 293.973 s per K = 5 pseudo unfold at 32
threads, packed 8 tasks per CPU node, ×1.25 packing, giving 0.012759 CPU node-h per unfold
(`state/next-preparation-20261009/gbdt/REPORT.md:416`, `:489-491`). The CPU pool cannot fund it. The GPU pool
(`m3246_g`, 42,727.4 node-h left at 2026-10-23 05:31 UTC, `state/measurement-scoping/iris-20261023.txt` on the
validation lane's branch) might, but the GPU cost is an unmeasured 2× guess from core counts. IBU-1 also showed a
3.8× per-task slowdown at full node packing (`state/2d-closeout/stageF/methods/ibu1/LEDGER-NOTES.md`). Joseph will
not send his request to Ben until this measurement is in.

## The design (fixed here, before any job)

- **Unit.** One recorded K = 5 pseudo unfold of configuration (e) (candidate R), by its frozen code path, from one of
  the 423 receipts behind the 293.973 s figure. The session names the receipt, its code commit, inputs (sha256) and
  seed in `RUN.md` here before submitting. If the 293.973 s receipts are not of configuration (e), say so, and use
  (e)'s recorded unit instead, naming both.
- **Arms.**
  - **C0, CPU node, packed:** 8 concurrent tasks × 32 threads (the costing's own packing). Per-task wall time.
  - **G1, GPU node, CPUs only, one task:** 1 task × 32 threads.
  - **G2, GPU node, CPUs only, packed:** 4 concurrent tasks × 32 threads (128 threads, the node's full CPU). Also
    2 × 32 if the time allows within the cap.
  - **G3, GPU node, LightGBM GPU training:** only if the analysis environment's LightGBM build supports a GPU device
    (`device_type` "cuda" or "gpu"). Test that with a one-line probe first. If it is unsupported, report it and stop.
    Do not build or install a new LightGBM without the director.
- **Controls.**
  - **K-T1:** the C0 and G1 products reproduce the recorded receipt's product bitwise (deterministic configuration).
    A mismatch voids that arm's timing as a measurement of the recorded unit.
  - **G3** is not expected to be bitwise. Report the maximum absolute and relative differences of `xsec_flat` from
    the recorded product, as a fact.
- **Readout,** per arm: per-task wall (median and range over the concurrent tasks), node throughput in unfolds per
  node-hour, and node-h per unfold on that node type. Then re-price the gbdt §9 table (1, 31, 101 and 288 unfolds per
  experiment, 4 × 4,404 experiments, ×1.25, /0.8) in GPU node-h from G2 (and from G3 if it runs and is usable),
  beside the CPU figures from C0. Show the arithmetic.
- **Compute cap:** at most 1.0 GPU node-h and 0.5 CPU node-h in all. Debug QOS where it fits; regular otherwise;
  never premium. Each job under 1 h. Ledger every job here in `LEDGER.tsv` (job id, QOS, elapsed, charge).
- **Storage:** `$PSCRATCH` only (`/pscratch/sd/j/josephrb/gpu-timing-20261023/`). Nothing to CFS.

## Pre-binding

This assignment is also the binding. The session commits `RUN.md` (the receipt chosen, exact commands, sbatch
scripts and their sha256) on a branch and tells the director. If `RUN.md` matches this design exactly, it may submit
straight away without waiting for a separate binding. Any departure from the design waits for the director.

## Report

`REPORT.md` here, with the measured numbers, the K-T1 outcome, the re-priced table and what was not done. Open a PR
and tell the director. No claim change, and no outward act.
