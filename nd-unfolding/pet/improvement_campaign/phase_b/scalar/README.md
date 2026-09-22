# Phase B1 — scalar, response-aware references for the historical endpoint

Report: `SCALAR_REFERENCES-20260922.md`. Machine-readable results: `results/`. Resource ledger:
`resources-B1.tsv`. PET is diagnostic method development; everything here is simulation only.

## Files

| file | role |
|---|---|
| `scalar_common.py` | imports the historical comparison modules (blob-checked against `68cf9d29`), captures the endpoint and its maps from `report_campaign.build_endpoint`, scores a push exactly as `score_campaign.score_run` does, reference curve `1-(1-a)^k` from `reference_calibration` / `characterize_regions` |
| `prepare_populations.py` | reproduces the historical halves / tilt / endpoint / reference and caches the scalar inputs (`populations.npz`, `populations.json`); refuses on any disagreement with the report |
| `binned_unfolding.py` | binned OmniFold / IBU in the engine's event-weight form (`carry_misses` = engine; `efficiency_corrected` = D'Agostini) |
| `scalar_omnifold.py` | two-step OmniFold mirroring `omnifold_nn/omnifold/omnifold.py`, with HGB / small-MLP / binned-oracle ratio classifiers |
| `features.py` | the named input sets (reco side refuses truth columns) |
| `run_ibu.py` | binned references vs k = 1..50 beside the reference curve |
| `run_scalar_omnifold.py` | scalar OmniFold, one (inputs, model, seed) task per array index, iterations 1..20 |
| `run_anchors.py` | oracle truth-level push (the injected function itself) = the closure's sampling-noise ceiling; identity push; historical pushes |
| `run_truth_learnability.py` | truth-only learnability of the known tilt on held-out events (a learnability diagnostic, not a bound) |
| `sbatch_scalar.sh` | guarded (`mnv_guarded_run.py`) CPU launcher from a clean pinned checkout |
| `test_scalar_references.py` | toys with known answers; bit-equality with the historical scorer; historical blob check |

## Rerun

On Perlmutter, from a clean clone of this branch pinned at commit `$SHA` (the scripts refuse a
dirty tree or a different HEAD):

```bash
SHA=<commit>; C=/pscratch/sd/j/josephrb/pet-improvement-20260922/checkouts/${SHA:0:8}
T=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1
P=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python     # python 3.11, numpy 1.26.4, sklearn 1.8.0
L=$C/nd-unfolding/pet/improvement_campaign/phase_b/scalar/sbatch_scalar.sh
NPZ=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
ID=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz

# 1. populations (reads the historical campaign outputs read-only)
sbatch --cpus-per-task=16 --mem=64G --time=01:00:00 --output=$T/slurm-%j.out $L $C $P $T/prep $SHA \
  prepare_populations.py --closure-npz $NPZ --identity-sidecar $ID \
  --campaign-dir /pscratch/sd/j/josephrb/campaign-20260920 --output-dir $T/prep
# 2. binned references and truth-only learnability
sbatch --cpus-per-task=8 --mem=16G --time=00:30:00 --output=$T/slurm-%j.out $L $C $P $T/ibu $SHA \
  run_ibu.py --populations $T/prep/populations.npz --iterations 50 --output $T/ibu/ibu.json
sbatch --cpus-per-task=16 --mem=24G --time=02:00:00 --output=$T/slurm-%j.out $L $C $P $T/learn $SHA \
  run_truth_learnability.py --populations $T/prep/populations.npz --output $T/learn/truth_learnability.json
sbatch --cpus-per-task=4 --mem=16G --time=00:20:00 --output=$T/slurm-%j.out $L $C $P $T/anchors $SHA \
  run_anchors.py --populations $T/prep/populations.npz --output $T/anchors/anchors.json
# 3. scalar OmniFold: {muon, muon_had} x {hgb, mlp} x 3 seeds, + muon_eavail x hgb x 3 seeds; 20 iterations each
sbatch --array=0-14 --cpus-per-task=16 --mem=24G --time=05:00:00 --output=$T/slurm-%A_%a.out $L $C $P \
  $T/omnifold $SHA run_scalar_omnifold.py --populations $T/prep/populations.npz --task-index ARRAY_TASK \
  --iterations 20 --output-dir $T/omnifold
```

Tests (any python with numpy, sklearn >= 1.7 for the classifier tests, pytest):
`python -m pytest -q -p no:cacheprovider nd-unfolding/pet/improvement_campaign/phase_b/scalar`.
On Perlmutter `module load python` supplies pytest; the classifier tests skip on older sklearn.
