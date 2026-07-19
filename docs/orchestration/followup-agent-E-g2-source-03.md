Resume the exact `agent-E-g2-source` UUID
`44b634fc-d211-4e09-9229-95a18d1984cc` and retain G2 source/runtime ownership.
Do not replace or fork this role, subdelegate, consume a reset credit, rerun the
smoke, start another allocation, or launch PET production.

Attempt 2 is terminal and must be reused:

- `nd-unfolding/pet/g2_smoke/attempt2/DONE` exists and `loop.rc` is `0`;
- the only ROOT is the existing 9,419,026,130-byte
  `attempt2/runEventLoopOmniFold.root`;
- no event-loop writer remains;
- canonical binary SHA-256 is
  `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`;
- holder `56100487` was reused for Stage-4 validation; do not request another.

The first validator run exposed a validator-only PyROOT binding issue:
`UChar_t` leaves are returned as one-character strings. Direct ROOT probes
confirmed native misses carry zero `sim_pass`/`mu_reco_minos_ok`, -9999 reco
sentinels and empty reco clouds. Review and retain the minimal `uchar_value`
normalization now present in
`nd-unfolding/pet/validate_g2_fullevent_smoke.py`. The repaired run produced
`attempt2/g2_validation_v2.json`: PASS, 50/50 checks, with counts truth=signal
4,073,230, background=44,900, data=360,123, native misses=1,596,619. Recheck
that receipt and its SHA-256
`776addeb3453445bcb1e6fa45f81ed41ffe7f713a1cb2da0eac729eccf007b25`;
do not rerun the event loop.

Complete only the G2 gate:

1. Hash and bind the existing attempt-2 ROOT, binary, source commit `486e53e`,
   canonical 1A manifest contents, validator blob and validation receipt.
2. Atomically move the already-validated ROOT on the same filesystem to the
   isolated final path
   `nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root`. Never touch
   canonical recoil-only or pre-G2 products. Verify the final path/hash after
   the move and write a schema-versioned tracked receipt
   `nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json` last. The receipt
   must record all 50 checks/counts, exact paths/hashes, binary/source footing,
   smoke start/end/rc and atomic publication.
3. Update the co-located `G2_FULLEVENT_CPP_DUMP_STATUS.md`,
   `VALIDATION_LEDGER.md`, and `ND_OMNIFOLD_RUN_LOG.md` truthfully. Do not stage
   the unrelated dirty canonical `ND_OMNIFOLD_STATUS.md`.
4. Add a tracked, fail-closed 12-playlist production launcher at
   `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh`, but do not submit it.
   It must use the exact canonical binary hash above, one playlist per array
   task, canonical per-playlist manifests, both
   `MNV101_DUMP_POINTCLOUD=1` and `MNV101_FULL_PHASE_SPACE=1`, no nested srun,
   isolated `nd-unfolding/g2_fullevent/` work/final namespaces, unique
   temporaries, full G2 validation before atomic ROOT publication, a hash-bound
   per-playlist receipt written last, and content-validated resume. It must
   reject stale/partial outputs, binary drift, missing manifests, duplicate
   writers and any old recoil/purity namespace. Preserve the unrelated
   untracked `nd-unfolding/sbatch_evloop_array_pointcloud_fps_bkgcloud.sh`.
5. Run syntax/static/receipt checks, stage only E-owned paths plus the required
   ledger/RUN_LOG receipt files, commit, and push. Do not submit the array; the
   orchestrator will inspect the commit and live queue, then queue it only if
   this G2 gate is committed and pushed.

Report the final ROOT and receipt hashes, 50-check counts, changed paths, test
commands/results, commit hash, and whether the launcher is queue-ready. If any
gate fails, leave the attempted ROOT isolated, record the exact blocker, and do
not claim PASS or authorize the array.
