# CLM-008 claim detail

## Original claim cell

P5B engineering debt (not P5A blockers): FiLM adds shift to padded tokens + classifier attention unmasked (F2); posinf→1 saturation clamp erases strongest reweights (F3, pre-existing); bootstrap draw after subsample incoherent with global draw (F7); distributed rank-slicing misaligned imc/data (F8); reload test saves untrained template (F9); truth-KNN phi not periodic (F10).

## Status history

VERIFIED-CODE (defect list)

## Evidence artifact

codex_audit.out F2,F3,F7,F9,F10 + F8

## Data/config hash

—

## Commit

9d353e1

## Slurm job(s)

—

## Independent verifier

codex V1

## 2026-07-17 — Residual history

CLOSED except F7 (2026-07-17): F10+F9 fixed (4043e3f/220c970); F2 (FiLM/attention pad-masking) + F3 (publication logit-space reweight, cap 30 predeclared, fail-closed, saturation telemetry) fixed in 25d8360, GPU-validated (56041808 rc=0); F8 MOOT by policy — no Horovod for P5B, single-rank jobs (reverts to hard gate if Horovod ever returns); F7 remains the sole open hard gate (C_stat: coherent global Poisson draw before subsetting)
