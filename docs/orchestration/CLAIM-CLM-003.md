# CLM-003 claim detail

## Original claim cell

Omitted-muon stress closure: recoil-only blind to per-stratum muon tilt; full-event recovers. B: 0.582/0.581/0.043.

## Status history

VERIFIED-NUMERIC (toy scope)

## Evidence artifact

fe5v seed0: 0.5820/0.5811/0.0428 (exact repro); seed1: 0.5801/0.5791/0.0390 (robust). Logs fe5v_stress_seed{0,1}.log

## Data/config hash

fe_verify/PROVENANCE_SHA256.txt

## Commit

9d353e1

## Slurm job(s)

56003372

## Independent verifier

fe5v re-run (me)

## Residual history

DESIGN caveats (codex F4,F5): decile normalization leaves within-decile corr(w_data,R)≈0.08–0.46 so recoil arm not blind *by construction* (empirically it was: 0.581≈prior 0.582); PASS thresholds permissive. Toy: identity detector, 20k events. Real-scale muon-shift test deferred to pilot/P5B
