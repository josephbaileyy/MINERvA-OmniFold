Resume the exact `fps-adopt-verifier` session UUID
`019f74bb-a4e7-7ba3-9598-b6b73b7f5831`. Read-only review only; do not edit,
dispatch, create endpoints/covariance/adoption products, or absorb unrelated
dirty work.

Resolve the latest successful `agent-C-fps` receipt from `state/sessions.json`.
Its repair-3 target is commit `1771be2`, claimed pushed to `github/main`, with
49/49 ROOT-free tests plus 9/9 actual-CLI integration negatives. Independently
verify the live remote target and restrict the audit to the exact commit-owned
paths; treat later C-owned drift as contamination and ignore other owners' dirt.

Re-audit every prior BLOCK at executable depth:

1. A manifest emitted by the declared builder must be directly consumable by
   the component builder and carry canonical paths plus strict 64-hex hashes
   for all ten unfold/input/config/source/launcher/central/audit artifacts.
   Every consumer must recompute live hashes. Probe missing paths, same-size
   substitutions, non-hex strings, missing tags, wrong canonical edges, and
   flat-versus-TH2 C-order disagreement.
2. Publication manifest/receipt must be unconditional in P4. Verify a
   schema-versioned hash chain for component build -> P4 validation -> active
   adoption -> unified adoption; each step must bind the exact predecessor,
   central/mask/order/component/candidate identity. Two-field PASS objects,
   purity/default aliases and substituted same-dimension inputs must fail.
3. Audit both batch and interactive launchers through the shared strict endpoint
   receipt validator: actual launcher attribution, unique temps, validate before
   atomic ROOT publication, receipt last, exact resume recomputation, stale
   output rejection, exact ten-tag inventory, and aggregate nonzero worker
   failure. Confirm no receipt can be minted for a stale pre-existing ROOT.
4. Verify unified adoption binds publication CV SHA, canonical 266/285 mask,
   exact order, `hJointMeanShift(expected_dim=n)`, mean-shift hash, and centering
   policy while preserving MAT `1/N`, pure addition, superseded naming, alias
   rejection, and unchanged purity-control hashes.
5. Execute the reported unit and real-script CLI batteries and add independent
   adversarial probes where coverage is weaker than the claim. Confirm tests
   reach the intended gate instead of merely failing argparse/import.
6. Verify commit-gate receipts landed together in `VALIDATION_LEDGER.md`,
   `ND_OMNIFOLD_RUN_LOG.md`, and the co-located FPS state. The canonical
   `ND_OMNIFOLD_STATUS.md` remains an independently documented PG0 dirty-file
   ownership block; do not waive it, but do not conflate it with technical
   endpoint authorization if the scoped workstream receipt is otherwise sound.

Confirm no `unfolds_negweight_refined/`, publication endpoint, covariance,
candidate, or adoption product was created. Return one falsifiable verdict:

- PASS only if commit `1771be2` is production-preflight ready for a later
  separate ten-endpoint negweight-refined launch (not adoption); enumerate all
  runtime gates still necessarily deferred to those not-yet-created ROOTs.
- Otherwise BLOCK with ranked defects, direct path/line/probe evidence, and the
  smallest exact repair. A successful process return code is not a PASS.
