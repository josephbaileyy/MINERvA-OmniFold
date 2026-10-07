# Proposed resource amendment after scheduler preflight

**PENDING APPROVAL. No calibration or training allocation has started.**
This amends only the reservation profile and CPU ceiling of the already approved
[execution proposal](EXECUTION_PROPOSAL.md). Scientific code, samples, seeds,
training budgets, acceptance criteria, GPU-hour limits and stop conditions remain
frozen at preparation commit `9d598c083bca742944e30b4079c7390ece2be9d1`.

## Measured scheduler constraint

Perlmutter's `shared_gpu_ss11` partition reports
`DefMemPerCPU=1796 MaxMemPerCPU=1796` MiB. The queue admission check requires
32 Slurm CPUs per requested GPU. Read-only `sbatch --test-only` observed:

| Profile | Scheduler result |
|---|---|
| Approved: 1 GPU, 8 CPUs, 64 GiB | Rejected: memory adjustment requests 38 CPUs; queue requires 32 per GPU. |
| Control: 1 GPU, 8 CPUs, 14,368 MiB | Rejected: requests 8 CPUs; queue requires 32 per GPU. |
| Proposed: 1 GPU, 32 CPUs, 56 GiB | Accepted by scheduler test: 32 processors in `shared_gpu_ss11`. |

The original proposal's eight-CPU reservation was an implementation-planning
error. It is not possible to honor that per-allocation ceiling on this queue.
The control establishes that lowering memory alone does not solve it. Test-only
output includes a prospective job number/start estimate; it is **not a submitted
job or allocation**, and scheduler state remained empty after the checks.
Exact commands, timestamps, stdout, stderr and exit codes are preserved in
[execution_runs/20260911-preflight/](execution_runs/20260911-preflight/).

## Single requested change

Use **one A100, 32 reserved Slurm CPUs and 56 GiB RAM** for calibration and each
paired job. The training process will be constrained to eight CPUs of execution affinity;
accounting uses all 32 reserved CPUs, never the application's thread count.

| Ceiling | Approved original | Proposed amendment |
|---|---:|---:|
| Calibration wall / GPU-hours | 2 / 2 | unchanged |
| Full jobs / wall per job | 24 / 12 hours | unchanged |
| Total GPU-hours | 290 | unchanged |
| Reserved CPUs per allocation | 8 | **32** |
| RAM per allocation | 64 GiB | **56 GiB** |
| GPU-associated reserved CPU core-hours | 2,320 | **9,280** (= 290 × 32) |
| Separate preparation/accounting CPU core-hours | 16 | unchanged |
| Total CPU core-hour ceiling | 2,336 | **9,296** |
| Storage, including durable copy | 200 GiB | unchanged |
| Concurrent full jobs | 2 | unchanged |

The planning estimate remains 50–240 A100-hours, now corresponding to roughly
1,600–7,680 GPU-associated CPU core-hours. Those are estimates, not measured
throughput. Calibration must re-estimate runtime, memory and storage and show
≥20% headroom against **56 GiB** and the remaining grant before any full job.
No sample reduction, seed removal or model change is an automatic fallback.
The isolated GPU runtime and its preparation files count within working storage;
its complete resolved package versions and download hashes will be preserved.

The proposed calibration submission, already accepted by the scheduler's
read-only test, is:

```bash
sbatch --account=m3246_g --constraint=gpu --qos=shared \
  --nodes=1 --ntasks=1 --cpus-per-task=32 --gpus=1 --mem=56G \
  --time=02:00:00 nd-unfolding/pet/direct_token_comparison/sbatch_calibration.sh \
  CHECKOUT GPU_RUNTIME NEW_OUTPUT EXPECTED_COMMIT APPROVAL_JSON APPROVAL_SHA256
```

The prepared [launcher](sbatch_calibration.sh) and [driver](calibration_measure.py) wrap the
unchanged runner: 32,768 train / 8,192 test rows, seed 17, injected, one iteration,
one epoch, batch 1,024. It records actual Slurm allocation, GPU visibility,
versions, import guard, resource meter, tests, per-fit timing and closed outputs.
The eight-CPU application affinity limit cannot be used to call a 32-CPU allocation an
eight-CPU reservation. Existing source-audit CPU environments must not be reused
as if they were GPU environments.

The cluster test rehearsal covers the five descriptor/model/prong suites;
the legacy source-smoke suite is validated locally only. It imports two
receipt-bound readers with hardcoded cluster paths, while the isolated runner
imports neither. See [execution status](EXECUTION_STATUS-20260911.md) for this
test-scope distinction and the preserved guard restrictions.

Approval of this amendment permits the original campaign to proceed through
calibration and its existing conditional gate without another permission request
for covered steps. Until then, no allocation is submitted. All original
non-claims and the prohibitions on source access, covariance, adoption and Gate 6
remain operative.
