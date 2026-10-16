# AUTHORIZATION 2026-10-16 — 2D closeout: move Stage C production to regular-QOS node packing (build step)

**Issued by** the paper-tighten lane, as director, under Joseph's compute delegation. It amends the
submission path bound by
[`AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md`](AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md).
This is step 1 of two. It authorizes the 2d closer to **build and test** a packed submission path. A binding
addendum on `origin/main` (step 2, §4) must exist before any pending job is cancelled or any pack is submitted.

**CITABLE FOR:**
- the measured reason the shared-QOS path cannot finish before the maintenance window;
- the director's choice of option O2 (regular QOS, single-node packs), and the requirements it must meet;
- a correction to the binding's maintenance time (§2).

**NOT CITABLE FOR:**
- a higher ceiling. It stays at 100.0 node-h, and committed grant ceilings under the delegation stay at 132.0 of 700;
- any change to analysis, rollup or driver code, or to any job's physics configuration;
- any result;
- cancelling, submitting or redeploying anything before the step-2 binding is on `origin/main`, other than the single smoke pack in §4.6.

## 1. Measured problem

These numbers were measured on `saul.nersc.gov` on 2026-10-16 at about 16:10Z, by the closer and re-measured by the director.

| quantity | value |
|---|---|
| our production state | 12 COMPLETED (C0 ×2, S3 ×10), 0 RUNNING, 389 PENDING (Reason=Resources), no failures and no timeouts |
| our start rate on `shared_milan_ss11` | 10 starts in 17.9 h (0.56/h), all of them 128-CPU S3 jobs. None of our 64-CPU jobs has started |
| `shared_milan_ss11` starts of ≥64 CPUs, last 24 h | 260 (director's count; the closer counts 188 at 64–127 CPUs and 72 at ≥128). The partition started 17,672 jobs in all, mean 7.95 CPUs |
| `regular_milan_ss11` single-node starts, last 24 h | 6,451 (director's count; the closer counts 5,799 for a slightly different window) |
| regular node | `CPUTot=256`, `RealMemory=515100` |
| needed rate | 389 queued jobs plus about 130 not yet submitted, all to finish before 2026-10-21T06:00Z. At about 0.5 starts/h, the remaining work would take about 34 days |

## 2. Correction to the binding

The binding's §4 and the director's earlier messages give the maintenance window's start as 06:00 UTC. That is wrong. `TZ=UTC scontrol show res maintenance_20261021` gives
`StartTime=2026-10-21T13:00:00 EndTime=2026-10-28T06:00:00`.
The jobs' `Deadline=2026-10-20T23:00:00` is cluster-local time (PDT), which is 2026-10-21T06:00Z. The Deadline therefore falls 7 h before maintenance, not at it. That is conservative, and it stays as it is. The binding's straddle condition still applies, measured against 13:00Z. Every time quoted from `sacct` or `scontrol` without `TZ=UTC` is PDT.

## 3. Ruling: O2

The closer offered three options:
- O1: keep the shared path;
- O2: regular QOS, single-node packs of 4 CV rows or 2 S4U rows;
- O3: a hybrid of the two.

premium, debug and interactive are not viable, for the reasons the closer measured. The director chooses **O2**:
- it is the only option backed by measured throughput at our job size;
- it keeps every per-row enforced cap.

O1 is rejected because it would run past 2026-11-15. O3 is rejected because it pays the same re-pin cost for most of the delay.

A pack does not change any member's physics. The analysis code and its inputs stay byte-identical, as do the output paths (`out/<member>/`):
- `analyze_prod.py`
- `s5_rollup.py`
- the production driver
- `driver_p1.py`
- `omnifold.py`
- each member's `jobs.tsv` row: config, seeds, inputs and its own cap.

## 4. Requirements for the step-2 binding

The closer delivers a package commit on its own branch and PR. The director binds it in a step-2 record only when all of the following hold.

1. **Charge stays capped per row.**
   - A pack's enforced charge equals the sum of its members' row caps under the binding's §2 formula.
   - A pack's wall cap is no larger than its members' common cap: 00:51:00 for CV packs, 00:30:00 for S4U packs.
   - `CEILING = 100.0` stays unchanged.
   - The gate counts in-flight liability per pack at the pack cap, and terminal charge per pack as measured.
   - The total enforced worst case is recomputed and reported. It must not exceed 117.8583 plus any rounding the closer itemizes.
2. **Resources fit the node.**
   - Members run as `srun --exact -n1 -c<cpus> --mem=<mem>` steps.
   - The sum of member memory must be at most `RealMemory` 515,100 MB. A test refuses a pack table that breaks this.
   - Each member's return code and Slurm step state are recorded separately.
   - One member failing does not cancel the others.
3. **Identity is not taken from the job name.**
   - Each step gets its member's name explicitly and checks it against its own `jobs.tsv` row.
   - A test shows that a mismatched or duplicated member is refused before it runs.
   - The dispatcher's billing refusal expects the pack's billing (256 for a full node), and it is tested at both the right and a wrong value.
4. **The retry and redo rules are member-level and fail closed.** Each rule has a test that fires on the bad case and stays silent on the good one:
   - a DEADLINE pack, or a CANCELLED pack that never started, owes only the members that have no output, and that is not an attempt;
   - a TIMEOUT or FAILED pack gives each member without validated output its one retry, as the binding allows;
   - a member with validated output is never re-run.
5. **Migration is exact.**
   - The cancel list is the never-started PENDING `2dc_P_*` jobs, measured from `squeue` at cancel time, not from a saved list.
   - Any shared job that has started by then is left alone, and its row is removed from the packs.
   - The ledger shows the 12 completed rows, plus any that started, with their measured charges.
   - S2b stays unsubmitted until it goes as packs.
6. **Tests and review.**
   - `test_launch.py` passes in full, with the runner's count reported.
   - One smoke pack (a single 4-member CV pack, at most 0.85 node-h at cap) runs on regular before the step-2
     record. It is the only pre-binding submission this record allows, and it carries out these steps:
     - It is submitted under the `2dc_P_` prefix, so that the gate's ledger counts it against the 100.0.
     - Its members are real rows whose shared jobs are still PENDING.
     - Before submitting, the closer cancels exactly those 4 shared jobs. Each must be never-started and have charge 0.
     - Those members' outputs are kept only if they pass the existing provenance checks.
   - The closer reports measured member and pack charges.
   - A fresh read-only verifier reviews the diff against this section, and its report is attached.
7. **Expected charge** is reported as measured from the smoke pack, not estimated. If it shows the gate would first refuse before S4b, the closer says so before the binding.

## 5. Interim conditions

Until the step-2 binding:
- nothing is cancelled, submitted or redeployed, except for the single smoke pack in §4.6 and its 4 member cancels;
- the 389 pending shared jobs stay queued, and if any start they run under the current binding;
- S2b is held.

The closer reports immediately if a shared job fails, times out or straddles the maintenance window.
