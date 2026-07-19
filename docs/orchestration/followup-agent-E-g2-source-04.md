Resume the exact `agent-E-g2-source` UUID
`44b634fc-d211-4e09-9229-95a18d1984cc` on its current flat
`claude-school` route. Retain G2 ownership. Do not fork, migrate again,
subdelegate, consume a reset credit, rerun/re-hash the 1A ROOT, rerun the
validator/event loop, start an allocation, submit the array, or advance PET.

Commit `9262e96` correctly published the existing G2 1A PASS receipt and ROOT,
which remain valid. However, both the orchestrator and fresh independent Gemini
verifier `agy-g2-gate-verifier` independently BLOCKED array submission on the
launcher recovery logic:

- `sbatch_g2_fullevent_evloop_array.sh:91` only enters resume validation when
  BOTH final ROOT and receipt are nonempty. ROOT-only or receipt-only falls
  through, runs the loop, and later `mv -f` / `os.replace` can overwrite prior
  evidence. A failure after ROOT publication but before receipt publication
  creates exactly this state.
- Resume validates the recorded ROOT and binary, but not the current canonical
  manifest contents/paths, playlist, environment flags, validator content, or
  >=50-check threshold. Thus it can skip on inputs different from the receipt.

Fix only the committed launcher and the smallest co-located status/run-log
evidence needed for this correction. Do not modify `VALIDATION_LEDGER.md`
numbers, the 1A receipt, validator, ROOT, dirty `ND_OMNIFOLD_STATUS.md`, or the
unrelated old point-cloud launcher.

Required fail-closed behavior:

1. Classify publication state using existence, not size. Neither exists -> may
   run. Both exist -> validate fully and resume-skip only on exact match. Any
   one-sided, zero-length, malformed, mismatched, or stale pair -> die before
   environment setup/event-loop execution. Never automatically delete,
   quarantine, repair, or overwrite published final/receipt paths.
2. Bind the launcher at commit time to all 24 current canonical manifest
   SHA-256 values (12 Data + 12 MC), the exact binary SHA already present, and
   validator SHA
   `3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8`.
   Initial execution must reject manifest or validator drift before compute.
3. Resume must validate receipt schema, playlist, PASS, exact final path/hash,
   binary actual+expected hash, exact manifest paths+current hashes, validator
   path+current hash, both env flags, `n_failed==0`, and `n_checks>=50`.
4. Immediately before ROOT publication, reassert that neither final path
   exists. Replace overwrite-capable `mv -f` with a no-clobber same-filesystem
   atomic publication. `mv -n` is acceptable only if you then prove the source
   disappeared, destination appeared, and hash matches; an atomic hard-link
   publication followed by source unlink is also acceptable. Any race must
   preserve the pre-existing final and fail.
5. Receipt publication must also be atomic and no-clobber. Do not use
   `os.replace` on the final receipt. Write/fsync a unique same-directory temp,
   atomically link/publish only if final receipt is absent, then remove temp.
   A crash after ROOT publication is allowed to leave ROOT-only; the next run
   must stop for manual reconciliation.
6. Record the immutable built-source commit
   `486e53e677eb64eb9d622ff6e5daecb3e62aab22` separately from the runtime
   launcher/HEAD commit; do not label arbitrary runtime HEAD as the binary's
   source commit.
7. Update the G2 status owner label from stale account-centric
   `Claude-personal` to role-centric Agent-E + UUID (current route School), and
   append one concise ND RUN_LOG correction. Do not duplicate science numbers.

Run proportionate tests without event-loop compute:

- `bash -n` and compile all embedded Python;
- verify all 24 embedded manifest hashes against current canonical files and
  the validator/binary hashes;
- a temporary-directory state-matrix covering absent/valid pair/mismatched
  pair/ROOT-only/receipt-only/zero-length/malformed/manifest drift/validator
  drift;
- an explicit no-clobber publication race test proving an existing destination
  hash is unchanged and the attempted source is retained or otherwise safely
  isolated;
- static assertions for no `mv -f` or `os.replace` on final publication paths,
  no nested `srun`, both env flags, isolated namespaces, and empty live queue.

Stage only your scoped launcher + concise status/RUN_LOG correction, commit,
and push. Report commit/hash, exact changed paths, test results, and
queue-readiness. Do not submit; the orchestrator and same independent Gemini
UUID will recheck the corrective commit.
