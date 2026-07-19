Resume the same Agent-B UUID as PET/F7 Python interface owner. Gate 1A is now
committed and pushed at c286140. All twelve G2 full-event ROOT/receipt pairs
passed independent all-hash validation; canonical summary:
docs/orchestration/state/g2-gate1-all12-validation-20260719.json.

Implement the currently runtime-blocked publication-default G2 branch in
nd-unfolding/pet/dump_pointcloud_inputs.py against the exact G2 ROOT branches and
the existing fullevent_dump_contract.py / fullevent_fps_dataloader.py / F7
three-inventory contract. Preserve your UUID and existing ownership. Do not
touch the event-loop binary, per-playlist ROOTs/receipts, merge namespace,
Slurm jobs, PET training, P3F, covariance, adoption, or unrelated dirty files.

Required implementation:

- Read aligned signal, data, and background inventories, including full reco
  clouds with view/time, reco/data/background muon and vertex features, truth
  cloud/scalars, weights, pass flags, and real stable identities/order.
- Enforce the retained FPS domain pT in [0,30] GeV and p_parallel in [0,120]
  GeV before any row can enter training. This is mandatory for recovered
  1D/1E/1F/1P artifacts.
- Preserve native misses and prevent truth leakage into step 1.
- Emit exact G2 markers/fingerprint, measured scalars, literal aligned
  background clouds/scalars/w_bkg, and identity/order hashes required by the
  contract and F7 replay.
- Use write_fullevent_npz_atomic; no partial output, no purity fallback, no
  legacy/recoil path under the publication default.
- Add focused ROOT-free tests for branch/manifest mapping, domain exclusion,
  identity/order, background alignment, native misses, and fail-closed missing
  branch/tamper cases. Run all relevant existing ROOT-free suites.

The orchestrator is concurrently performing the no-clobber MEFHC ROOT merge on
the existing interactive holder. Do not wait/poll for it and do not run the
large ROOT integration in this turn if the merged receipt is not already
present. Return implementation/test evidence and exact remaining runtime step.
Do not commit; the implementation must land with its runtime product summary
after independent review. Preserve all existing changes outside your files.
