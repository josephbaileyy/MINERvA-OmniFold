Resume the exact `agy-g2-gate-verifier` UUID. Final READ-ONLY G2 launcher
recheck only: no edits, commits, dispatch, Slurm changes, compute, allocation,
large ROOT hashing, validator/event-loop rerun, or PET work.

Verify launcher-only corrective commit
`15f750bb5efd4a9f36685b30256c0c97bab4e460` against your prior BLOCK on
`09fe1d4`. Inspect the exact diff and current launcher. Confirm all four gaps
you identified are closed:

- stale-work quarantine failure is fatal and source absence is proven;
- both ROOT and receipt absence are reasserted immediately before publish;
- resume binds `binary_sha256_expected` and `built_source_commit`;
- ROOT/receipt hardlink identity+content+unlink postconditions are proven.

Also verify dangling symlinks count as occupied and input footing is rechecked
after the long loop before validation and again immediately before publication.
Check for regressions in the original one-sided-state/manifest protections,
one-playlist-per-task array mapping, binary/validator/24-manifest bounds, both
G2 flags, isolated namespaces, flock, full validation before publication, no
nested srun, and receipt-last semantics.

Run proportionate static and small temporary-directory checks only. Return one
word `PASS` or `BLOCK` first, then exact evidence. A PASS authorizes the
orchestrator (not you) to submit the committed launcher. State separately that
the 1A receipt remains valid. Do not suggest extra defense-in-depth work unless
it is actually submission-blocking under the stated contract.
