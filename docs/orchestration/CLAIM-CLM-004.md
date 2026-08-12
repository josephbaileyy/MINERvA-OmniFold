# CLM-004 claim detail

## Original claim cell

Ordinary self-consistency closure on real xps2 tensors passes. B: median 1.059, L1 0.0021 @12k.

## Status history

VERIFIED-NUMERIC (null-test scope)

## Evidence artifact

fe5v seed0/12k: median 1.0587, L1 0.0021, norm-dev 0.0556 (exact repro); seed1/48k: median 1.0010, L1 0.0015, norm-dev 0.0014 (improves with scale)

## Data/config hash

same

## Commit

36ab84d

## Slurm job(s)

56003372

## Independent verifier

fe5v re-run (me)

## Residual history

WEAK BY DESIGN (codex F6, claude-school C4): push≡1 passes; normalization residual not gated. Value is only as the "does not move" arm paired with CLM-003
