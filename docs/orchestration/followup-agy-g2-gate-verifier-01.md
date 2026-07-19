Resume the exact independent `agy-g2-gate-verifier` UUID created for the G2
gate. READ ONLY: no edits, commits, dispatch, Slurm changes, allocation, ROOT
hashing, event-loop/validator rerun, or PET advancement.

Recheck corrective commit `09fe1d428149bb7138efb77fd64c527fd4b1d0e4`
against your prior BLOCK on `9262e96`. Inspect only its exact three-file diff,
with primary attention to
`nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh`. Confirm the original
ROOT-only/receipt-only overwrite defect and manifest-resume gap are fixed.

Also independently rule on these orchestrator findings in the new launcher:

1. Stale work quarantine at the current lines 241-245 uses
   `mv ... || true`; if the move fails, execution appears able to continue into
   an event loop with the stale fixed-name work ROOT still present.
2. Immediately before ROOT publication, the current line 265 reasserts only
   `FINAL_ROOT` absence, not `RECEIPT` absence. A receipt appearing after the
   under-lock classification could therefore be paired with a newly published
   ROOT before receipt publication fails closed.
3. `validate_resume` checks receipt `binary_sha256` but appears not to check
   receipt `binary_sha256_expected` or `built_source_commit` against their
   immutable launcher bounds.
4. `publish_root_noclobber` runs `rm -f "$src"` but does not explicitly prove
   source absence afterward; `publish_receipt_noclobber` does not explicitly
   content/inode-check the linked destination or prove temp removal, despite
   the documented hardlink->verify->unlink contract.

Decide which are blocking versus defense-in-depth under the explicit gate:
fail closed for every stale/partial/racy state; never overwrite published
evidence; prove no-clobber postconditions; and bind resume to the complete
scientific/runtime footing. Check for any additional control-flow flaw. Use
only proportionate static and temporary-directory tests outside the repo.

Return `PASS` or `BLOCK`, exact file/lines, minimal corrections, whether the 1A
receipt remains valid, and exact tests. Do not modify files.
