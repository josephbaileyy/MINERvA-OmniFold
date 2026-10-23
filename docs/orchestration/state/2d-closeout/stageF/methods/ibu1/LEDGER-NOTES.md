# IBU-1 ledger notes: B1's time-out, B2's cancellation, and the proposed resubmission (2026-10-22)

**By** the validation lane, for the director. This note proposes one job and runs none until the director approves.
It changes none of the declaration's seeds, truths or reading rule ([`DECLARATION.md`](DECLARATION.md) as bound in
[`BINDING.md`](BINDING.md)). The charges are in [`LEDGER.tsv`](LEDGER.tsv).

**CITABLE FOR:** what B1 produced, why it overran, and the proposed limit with its derivation.
**NOT CITABLE FOR:** any IBU-1 result.

All times are PDT, from `sacct` and the task logs under `/pscratch/sd/j/josephrb/ibu1-20261022/run/logs/`.

## 1. B1 (60130899): stopped by its limit

- **Run:** lines 3–63, 18:06:20–18:25:35, ElapsedRaw 1155 s against a 0:19 limit. **TIMEOUT**, so the
  1.25 × projection rule stopped it.
- **Charge:** 0.3208 CPU node-h.
- **Steps:**
  - 41 steps completed 0:0.
  - 20 were cancelled at the limit: the three bootstraps, and 17 seed chunks that started late, as memory freed.
  - **Correction (2026-10-23, from the full-step sacct in [`receipts/sacct.txt`](receipts/sacct.txt), found by the
    IBU-1 report's review):** 40 numbered steps COMPLETED and 21 CANCELLED. The 21 are the three bootstraps and 18
    seed chunks. N_sigma_R's step (`.2`) counts as CANCELLED although its product had already been written (18:25:06),
    as the next section says. The counts above were taken from the guard lines (41), which include that step.
- **Memory:** peak step RSS 8.78 GB, inside the 11G step.

**Products** (re-read on Perlmutter: every `.npz` loads; every comparator gate present passes):

| unit | products / declared | comparator gates |
|---|---:|---|
| P_nominal | 400 / 400 | 400 pass |
| P_tilt | 400 / 400 | 400 pass |
| N_nominal_dev | 60 / 60 | 60 pass |
| N_nominal_val | 192 / 400 | — (no comparator) |
| N_gibuu | 22 / 400 | 2 pass (seeds in 301000–301059); 20 have no comparator |
| N_sigma_R | 1 / 1 | pass |
| P_sigma, N_sigma_s5n | 0 / 1 each | — |
| P_d1, D_P, D_N (job A) | 9 / 9, 1, 1 | 9 pass |

**Partial output.**
- `ibu1.py`'s `write` saves to `<target>.partial-<pid>.tmp` and then renames it with `os.replace`.
- No `.partial-*` file remains, so every `.npz` present is a complete product of the bound code.
- The per-seed products of cancelled chunks are therefore **kept, not excluded**.
- `run_experiments` and `run_bootstrap` skip a product that already exists (`ibu1.py:363,408`), so re-running a line
  finishes its chunk without recomputing.
- `N_sigma_R.npz` was written at 18:25:06. Its step was killed at 18:25:35, after the write and before the guard
  finished. Its re-run line skips the product and logs a clean exit.
  - **Correction (2026-10-23, found by the IBU-1 report's review):** the guard had in fact recorded the child's exit:
    its inventory record (`receipts/inventory/N_sigma_R.jsonl`) was written at 18:25:06 PDT with outcome
    `child-systemexit:0`. The step was cancelled at 18:25:35, after both.
- The two other bootstraps keep no checkpoint, so their 1,142 s of work is lost.

## 2. Why it overran

- **The projection.** It took job A's per-step rates: 8.6 s per build and 1.2 s per IBU, measured with 3 concurrent
  steps. It applied them to about 44 concurrent steps (487 GB ÷ 11G).
- **Assumed N rates.** The N rates (15 s per experiment) and the replica rate (3 s) were assumptions, because job A
  ran no N experiment and no replica.
- **Measured in B1 at full load:**
  - P experiments: 34.6–39.5 s each (task means). That is about 3.8 × job A.
  - N experiments: 38.8–46.4 s; 17.7–21.7 s once the load fell.
  - N replicas: 9.7 s each (`N_sigma_R`: 100 replicas in 1,111 s, less about 145 s of start-up).
- **(inference) Cause.** The per-step slowdown under ≈ 44-way packing is consistent with shared-node memory-bandwidth
  contention. It was not measured directly. Node throughput still rose, from 0.31 to about 1.1 experiments/s.

## 3. B2 (60130900): cancelled before it started

- **What it would have run:** lines 64–123, all N units (GiBUU, GiBUU_R, nominal_R, W1–W3), which share the
  underpriced N rate. Its 0:22 limit would have timed out the same way.
- **Action:** cancelled while PENDING (reason: Resources) at 18:50:32.
- **Charge:** ElapsedRaw 0, so 0 node-h.

## 4. Proposed resubmission: one job, C

- **Scope:** lines 3–123 in one job: B1's unfinished lines (their one permitted re-run, §6 Failures) together with
  B2's never-run lines (their first run).
- **Completed lines skip.** Lines 5–45 are complete and cost one input load each (≈ 145 s on one slot).
- **Unchanged:** the same deploy and pin (`7ea30e3d`), launcher, steps (2 CPUs, 11G), node count (1) and QOS
  (regular).
- **Remaining work:**
  - 1,846 experiments: 208 N_nominal_val, 378 N_gibuu, 20 N_gibuu_R, 40 N_nominal_R, and 400 each of W1–W3;
  - plus the P_sigma and N_sigma_s5n bootstraps, 200 replicas each.

**Projection: list scheduling of lines 3–123, in launch order, onto 44 slots.**
- **Inputs:**
  - 145 s start-up per step;
  - 40 s per remaining experiment, the upper end of B1's full-load task means;
  - 15 s per P replica. This is unmeasured, so it is set at 1.5 × the measured N replica rate. N replicas use 10 s.
- **Results by input set:**

| per experiment | per replica | projected wall |
|---|---|---:|
| 40 s | 10 s | 40.6 min |
| 40 s | 15 s (proposed) | **52.4 min**; the bootstrap is the long pole |
| 45 s | 20 s | 69.1 min |

- **Limit:** 1.25 × 52.4 min, giving **1:06:00**. That is inside the declaration's 1 h 30 min per job.

**Charge against the grant.**
- Worst case for C: 1.10 node-h, at its full limit.
- Charged so far: 0.0689 (A) + 0.3208 (B1) = 0.3897.
- Worst-case total: 1.49 CPU node-h. That is within the B cap (3.0), the declared worst case (3.5) and the 10 granted.

**If C fails or times out:**
- the lines it leaves unfinished have no further run (§6: "once more in one job");
- the verdict is then INCOMPLETE for the units they belong to;
- C is reported here, as B1 is.
