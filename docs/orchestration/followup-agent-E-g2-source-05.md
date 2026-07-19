Resume the same Agent-E UUID `44b634fc-d211-4e09-9229-95a18d1984cc`
on flat Claude School. Keep the turn launcher-only. Do not fork/migrate,
subdelegate, consume a reset credit, touch/re-hash/rerun 1A evidence, run
compute, start an allocation, submit the array, advance PET, or edit any file
except `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh`.

Your corrective commit `09fe1d4` fixed the original one-sided published-state
and manifest-resume defects. The same independent Gemini verifier UUID rechecked
it and returned BLOCK on four remaining explicit-contract gaps, also confirmed
locally by the orchestrator:

1. The stale work quarantine uses `mv ... || true`; a failed move can fall
   through into the event loop with the fixed-name stale work ROOT present.
2. Immediately before ROOT publication only FINAL_ROOT absence is reasserted;
   RECEIPT absence is not, so a receipt race can create an inconsistent pair.
3. Resume does not validate receipt `binary_sha256_expected` or
   `built_source_commit` against immutable launcher bounds.
4. The hardlink publishers do not fully prove their documented postconditions:
   ROOT source absence after unlink; receipt destination identity/content and
   temp absence after unlink.

Apply the minimal fail-closed fix:

- Make quarantine failure fatal and prove the stale source no longer exists
  before continuing. Never mask its `mv` failure.
- Immediately before ROOT publication, call the same existence classifier (or
  equivalently test both final ROOT and receipt) and require exactly `RUN`.
- Pass `BUILT_SOURCE_COMMIT` into resume validation; require receipt
  `binary_sha256_expected == EXPECTED_BIN_SHA` and
  `built_source_commit == BUILT_SOURCE_COMMIT`.
- For ROOT hardlink publication, capture and compare device+inode and/or content
  identity, make source unlink failure fatal, and explicitly prove source
  absence. For receipt publication, capture/compare device+inode plus SHA-256,
  make temp unlink failure fatal, and explicitly prove temp absence. Existing
  destinations must remain unchanged on all races.
- Treat dangling symlinks as occupied paths everywhere publication state or
  destination absence is tested (`-e` alone is false for a dangling symlink).
  A small `path_occupied` helper using `-e || -L` is appropriate.
- Re-run `assert_input_footing` after the event loop and before invoking the
  validator, then again after validation immediately before publication. This
  makes a shared-worktree binary/validator/manifest drift during a multi-hour
  task fail closed rather than generate a misleading receipt.

Extend the existing temporary/mock tests for quarantine-move failure,
receipt-appeared-before-ROOT-publish, dangling-symlink ROOT/receipt states,
mutated `binary_sha256_expected`, mutated built-source commit, ROOT unlink
postcondition, receipt identity/content/temp-unlink postconditions, and
mid-run footing drift. Keep `bash -n`, all embedded-Python compilation, the
full previous state matrix, no-clobber races, 24 manifest/binary/validator hash
checks, no nested srun, both env flags, and empty queue.

Commit and push only the launcher. Do not add another status/run-log/ledger
paragraph for this narrow corrective patch; the commit is the durable code
receipt and the existing status already records the verifier correction.
Report commit, tests, and queue-readiness, but do not submit. The orchestrator
will do final local + same-Gemini verification and own sbatch dispatch.
