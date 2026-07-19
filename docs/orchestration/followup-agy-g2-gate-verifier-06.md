Resume as the same independent G2 gate verifier UUID. Read-only audit the final
all-12 Gate-1 validator and its generated summary; do not edit, publish, submit,
merge, build inputs, dispatch roles, or replace any UUID.

Audit:

- nd-unfolding/pet/validate_g2_gate1_pairs.py
- docs/orchestration/state/g2-gate1-all12-validation-20260719.json
- the twelve final G2 receipts referenced by that summary
- only the supporting validation/domain receipts referenced by those receipts

The r5 watcher reported COMPLETE for the eight originally nonfailed tasks. One
full-array sacct reconciliation showed eight COMPLETED/0:0 tasks and four
FAILED/1:0 tasks (4/1D, 5/1E, 6/1F, 12/1P). Those four event loops completed but
sampled validation failed on finite corrupt out-of-domain muons; each preserved
ROOT was recovered without recomputation through the exact previously reviewed
domain gate. All twelve final pairs are present.

The new validator locally returned PASS with 12 pairs, zero failures,
113,500,285,444 total ROOT bytes, and aggregate counts:

- mc_truth_denom = mc_signal_reco = 49,906,108
- mc_background = 566,036
- data = 4,119,797
- nTruthOnlyMisses = 20,361,799
- mcPOTUsed = 4.978198462880827e21
- dataPOTUsed = 1.057394261158926e21

It recomputed every large ROOT SHA-256 with four readers after cheap fail-closed
checks. Check for any way it can omit a playlist, accept a stale/mismatched
receipt or manifest, fail to bind a supporting validator/domain receipt, accept
an invalid recovery census, misstate aggregate counts, or incorrectly close
Gate 1. Check that the conditional downstream retained-domain requirement is
truthfully preserved. Return PASS or BLOCK with exact required changes and state
whether Gate-1 evidence may be committed. Preserve your UUID.
