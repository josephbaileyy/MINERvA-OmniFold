# CLM-006 claim detail

## Original claim cell

Full-event (reduced muon schema) estimator works END-TO-END on real FPS inputs: 2M train → reweight-all 49.2M → finite extended-grid xsec; Tier-1 comparison within ±10% median; conditioning effect vs recoil-only mapped.

## Status history

VERIFIED-NUMERIC (pilot scope, both arms PASS)

## Evidence artifact

fe_pilot/{pilot_out,ablation_ones_out}/{telemetry,pilot_meta,extended_grid_cells}.json. Engine gates: all 49,152,885 outputs finite; unit check bit-exact vs engine reweight (0.0), 3.6e-07 vs weights_push; miss neutrality exact on all 1,164,327 miss rows (bit-exact fraction 1.0). Weight health (purity arm): step-1 pull max 48.8 / ESS 95.8% of 2M; step-2 push on 49.15M mean 0.972, max 1.34, ESS 99.6%. Physics gate: Tier-1 per-cell median \|FE/recoil-only−1\| = 4.25% (purity) / 4.37% (ones) ≤ 10% predeclared → PASS; tails annotated (q90 17.2%, max 42.2%, 20.9% of 225 cells >10%). Tier-2 (41 cells): median 5.16%, \|FE/prior−1\| median 1.70% (prior-dominated cells stay near prior, as expected). Background-treatment effect (purity vs ones, same seed): per-cell median 0.98%, max 13.0%; purity pulls aggregate yield −0.9% vs ones — direction consistent with subtracting the 2.7% background.

## Data/config hash

pc:dfd52750 5d:ea5c256b scalars:9629fd47; seed 4242

## Commit

fe-fps-campaign@40f94ed

## Slurm job(s)

56010587 (purity) + 56010588 (ones)

## Independent verifier

orchestrator harvest of predeclared gates (dossier §P-slice); GBDT comparator correctly REFUSED by driver (no committed xps2 GBDT central) → predeclared fallback = recoil-only legacy (sha 15d34df3)

## Residual history

Comparator convention caveat: legacy recoil arm is niter=5 / 40M-row train vs pilot niter=2 / 2M — the residual scatter mixes iteration count + training stats with the representation effect; NOT a publication result (estimator `pet-fullevent-fps-pilot0`); real-scale muon-shift stress still deferred to P5B
