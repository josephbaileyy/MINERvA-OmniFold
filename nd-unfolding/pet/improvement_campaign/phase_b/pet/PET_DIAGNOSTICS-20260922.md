# Phase B2 — PET stepwise diagnostics and first controlled feature arms (development stage)

## Running status (resume anchor; newest first)

- 2026-09-22 17:40Z: exp 1 configs (`configs/b2e1-H-K3-s{1..4}.json`) and launcher
  (`jobs/sbatch_b2.sh`) committed; submitting exp 1 through the UNMODIFIED A1 driver
  (`run_unfold.py`). Perlmutter task dir `/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB2/`.
- Next: B2 driver extension (per-iteration weights, resume, truth-only mode, input transforms),
  scorer, tests; exp 2/3 after the exp-1 gate.

## Pre-declared gate for experiment 1 (written before any B2 result exists)

The historical `ours` final per-seed recoveries (`configuration_comparison/campaign_report.json`
`per_run`, 8 seeds) span **[0.28888, 0.32563]**, mean 0.30367, sd 0.0134. Experiment 1 runs the
historical as-executed recipe through the A1 driver at K = 3 with 4 seeds.

- PASS if every seed lands inside [0.28888, 0.32563].
- If one or more seeds land outside: not an automatic failure (with 8 historical seeds, a draw from
  the same distribution falls outside their range with probability ~2/9). Accept faithfulness if
  the 4-seed mean lies inside the Welch-t 95 % interval for a difference of means of 0 against the
  8 historical seeds AND no seed is more than 3 historical sd from the historical mean; otherwise
  FAIL and stop to find out why before anything else.
