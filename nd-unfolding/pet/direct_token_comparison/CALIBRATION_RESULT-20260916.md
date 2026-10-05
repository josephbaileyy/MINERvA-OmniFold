# Calibration passed; the frozen matrix is released — 16 September 2026

**CITABLE FOR:** the terminal state of job `58395631`, its preflight verdict, the
measured resource quantities, and the fact that the frozen 24-job matrix was released
by its own gates.
**NOT CITABLE FOR:** any learning, closure or representation conclusion. Calibration
scores are excluded from the comparison by construction, and no matrix result exists
at the time this is written.

## Terminal state

| field | measured |
|---|---|
| job | `58395631` (`pet-amended-calibration`) |
| Slurm state | **COMPLETED**, ExitCode **0:0** |
| elapsed | `00:07:06` = **426 s**; parent, `.batch` and `.extern` rows all 426 |
| window | 2026-09-16T00:04:24Z → 00:11:30Z |
| launcher markers | `terminal.txt` = `COMPLETE`, `exit-code.txt` = `0` |
| execution commit | `a0f5c274036ce557205b2ecd457297c1dda80bf4` |

This is the first calibration to start, let alone finish, in this campaign. The five
preceding GPU attempts all stopped inside software equivalence checking.

## Preflight verdict, with the stress failure carried in the verdict word

`preflight.json` reports terminal **`PASS-WITH-RECORDED-STRESS-FAILURE`**, gate
`key-bias-common-operands-v1`, mode `gpu`, with `stress_only_cases: ["variable"]` and
`stress_failures: ["variable/direct"]`. All eight case/routing pairs ran on a real
GPU:

| case | pooled | direct |
|---|---|---|
| `nominal` (**the production geometry**) | PASS | PASS |
| `masked` | PASS | PASS |
| `empty` | PASS | PASS |
| `variable` (stress only) | PASS | **FAILED-STRESS** |

`masked` and `empty` had never been reached before; both pass on both routes. The
recorded stress failure reports `max_abs=0.0001443326473236084`, **bit-identical** to
job `58354898`'s, so the discrepancy is deterministic and reproducible rather than a
transient.

The tests the gate requires passed on the deployment target: `69 passed, 10 subtests
passed` and `40 passed`, the latter including the 15 new stress-scope and production
geometry controls.

## Resource gates: PASS

`evaluate_calibration.py` run from the deployed checkout with
`--allocation-seconds 426 --prior-allocation-seconds 1021`. Decision **PASS**, all
seven checks:

| check | verdict |
|---|---|
| `per_job_time_20pct_headroom` | PASS |
| `campaign_gpu_20pct_headroom` | PASS |
| `campaign_cpu_20pct_headroom` | PASS |
| `host_memory_20pct_headroom` | PASS |
| `per_job_storage_20pct_headroom` | PASS |
| `working_storage_20pct_headroom` | PASS |
| `total_storage_20pct_headroom` | PASS |

Measured: `fit_seconds` 15.90, `inference_seconds` 8.10, `other_seconds` 23.33,
`peak_rss_KiB` 1,060,768, `output_bytes` 47,129,222.

Extrapolated by the evaluator's own upper batch-count method: **job 2.533 h** against
a 9.6 h allowance, **campaign 60.79 GPU-hours** and **1,945.4 reserved CPU-hours**,
host **30.98 GiB** against 44.8, per job **1.344 GiB** against 3.2, working storage
**38.30 GiB** against 80.

## Charge

| quantity | value |
|---|---|
| this allocation | **426 s** |
| prior conservative charge | **1,021 s** (742 + 279) |
| new conservative total | **1,447 s** = 0.401944 GPU-hours |
| reserved CPU-hours consumed | 12.862 |

Ceilings unchanged and far from binding: 290 GPU-hours, 9,296 reserved CPU-hours
including the 16-hour preparation allowance, 200 GiB.

## Evidence

| artifact | digest |
|---|---|
| full output, 419 files | `9530dc8eb81f13d7d52585cf20b61d161212aacd10ca09647c2dc1eb373cfec9` |
| receipts-only tier, 64 files | `5ff8fb535563c415a09d2e276ab326f20cf23b786d72ad8614f74d3fba851da8` |

Both digests were measured on the cluster and again after transfer, and both archives
were read back for file count. Committed under
`local_validation/20260916-calibration/`, together with `calibration-gate.json`.

## The matrix was released by the gates, and submitted

Under Joseph's 16 September direction — "If the existing gates pass, continue through
the already-authorized learning comparison without another permission request" — the
frozen 24-job matrix was deployed and submitted as array **`58396676`**, 24 real rows
confirmed with `squeue -r` rather than the bracket Slurm rewrites for arrays.

The matrix runs at commit `d98d94cc54650c92f687b4b6c391f4dd085d2d22`. The scientific
and execution code is **byte-identical** to the calibrated commit `a0f5c274` —
verified by diffing the model, producer, preflight, guarded-runner and gate files —
so the calibration covers what the matrix runs. Only the post-hoc reducer, the new
bound launcher, the bindings and documentation differ.

Deployment verified all 54 manifest hashes plus the authority, gate-scope and
full-matrix-launcher digests. The launcher expresses the grant's limits where Slurm
enforces them: `--array=0-23%2` for at most two concurrent full jobs, `--time=12:00:00`
per job, and each task re-verifies its own `(mode, seed)` against the frozen run card.

## What still cannot be said

No learning result exists yet. When the matrix closes, `summarize_runs.py` applies the
unchanged frozen criteria, and its `NO_PASS` would be inconclusive or a safeguard
failure, never a statement of inferiority. Calibration scores are excluded from the
comparison. Compute cost will be reported per arm alongside closure, because retaining
more information is expected to cost more and that is a price to state rather than a
verdict. Nothing here bears on real-data adoption, covariance, statistical pairing,
coverage or Gate 6, and the source-semantic prerequisites remain unresolved.
