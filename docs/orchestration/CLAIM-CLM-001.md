# CLM-001 claim detail

## Original claim cell

omnifold_nn PET event-feature path was dead (graph-disconnected if num_evt>0; recoil path always num_evt=0) and KNN coords defaulted to first-2-columns; commit fixes both backward-compatibly.

## Status history

VERIFIED-CODE

## Evidence artifact

V1 verdict C1 HOLDS; V2 CLAIM1 HOLDS (pre-commit source diffed via `git show 9d353e1^:…`)

## Data/config hash

—

## Commit

9d353e1

## Slurm job(s)

—

## Independent verifier

codex V1 + claude-school V2 (independent)

## Residual history

"silent no-op" wording imprecise (was unusable, not silent); TF smoke of B not preserved but fe5v stress runs exercise the path end-to-end
