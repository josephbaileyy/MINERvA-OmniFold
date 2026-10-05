# Proposed single calibration retry after the technical stop

**PENDING APPROVAL; no retry or full job is submitted.** Job `58198332` failed
before GPU validation or training. Its explicit no-retry stop remains effective.
This requests one exception for that named technical failure, without increasing
any aggregate ceiling or changing the scientific design.

The correction checks versions of the five actually imported modules under the
unchanged guard. The original `importlib.metadata.version` lookup fails because
the replacement path finder does not expose package-discovery hooks. A local
read-only reproduction and the corrected guarded version check are preserved in
[the terminal evidence](execution_runs/20260911-calibration/). No missing package,
learning defect or GPU-runtime compatibility verdict follows from the failure.
The unchanged scientific runner and tests remain bound to the original hashes.

## Exact requested action

One fresh calibration allocation: **1 A100, 32 reserved CPUs, 56 GiB, 1 hour
58 minutes**. Use the corrected driver, a clean isolated checkout at the retry
commit, a new output directory, and [the retry launcher](sbatch_calibration_retry.sh).
The launcher requires a hash-bound authorization explicitly naming `58198332`;
[the pending record](retry-authorization.pending.json) cannot authorize execution.

Run the same 49 cluster tests plus 10 subtests; verify the exact package versions
and an actual A100 operation; then the same 32,768/8,192 synthetic rows, seed 17,
injected mode, one iteration, one epoch and batch 1,024. Preserve separate
training/inference timing, closed artifacts, import records, actual accounting
and a second independently read-back copy. This is calibration, excluded from
all scientific seed comparisons.

A second technical failure stops again, with no further retry or replacement.
Only a complete calibration passing the existing integrity and 20% headroom
gates permits the unchanged 24-job matrix (8 seeds × 3 modes, two arms per job,
1,000,000 train / 250,000 test rows, 3 iterations × 5 epochs, at most two concurrent
jobs, each at most 12 hours). No model, criterion, mask, selection, weight or
sample-size change is an automatic fallback.

## Accounting and limits

The failed allocation consumed **79 seconds**. Reserving at most **7,080 seconds**
for this retry and **1,036,800 seconds** for all 24 full jobs gives at most
**289.988611 GPU-hours** including the failure, below the approved 290-hour cap.
At 32 reserved CPUs, plus the existing 16-hour preparation allowance, the maximum
is **9,295.635556 CPU-hours**, below 9,296. The shorter calibration wall preserves
these aggregate caps; it does not subtract already consumed time from accounting.
The original 50–240 GPU-hour planning estimate is still uncalibrated. Storage
remains at most 200 GiB including durable copies; no source payload is copied.

Results can address only the declared synthetic routing contrast. This grants
no real-source access/training, producer correspondence, covariance, uncertainty
coverage, central/statistical pairing, publication adoption or Gate-6 work.
