# RECORD — OI-161: two discharged DO-NOT-LAUNCH comments updated; OI-45 promoted (2026-10-28)

The close-items session owns `OI-161` (promoted from the director's standing list, #474). Measured
on top of `b6a797620`.

**What changed.** Lines 11–12 of `nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps.sh` and of
`nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps_cpu.sh` read *"DO NOT LAUNCH until Agent A
commits P2 (interface validation) and records the validated installed-binary fingerprint"*. They
now read that the hold is DISCHARGED: P2 was committed at `2e8c214a` (2026-07-15), its gate table
is ALL PASS (`nd-unfolding/active_universe_5d/INTERFACE_VALIDATION.md:43` at that commit), and the
binary fingerprint is recorded. They also say this is not a launch grant.

**Constraints kept.**
- **Same line count.** Line 13 onward is unchanged in both files, because records cite these
  launchers by line number (`OI-161` cites `:11`).
- Neither file's sha256 prefix or blob id appears anywhere else in the tree, so no binding is
  pinned to them. `verify_hash_bindings.py` reports `ALL BINDINGS INTACT`, exit 0, after the edit.
- `bash -n` passes on both.
- **Not a launch authorization.** The row says so, and so does the new comment. The FPS arm's
  standing on the publication path is a separate question, owned elsewhere.

## OI-161 — retired

Its terminal criterion, *"both hold comments state the discharge and cite 2e8c214a"*, is met by this
change. Dependency check: 0 hits for `OI-161` in KNOWN_ISSUES, DECISION, RULING, AUTHORIZATION,
OPERATIVE and `docs/publication/` records.

## OI-45 — promoted (the director's standing list, third)

It replaces OI-161 to keep the promoted queue at `current_work_min` = 10. Next action: *"Record
effective author and committer identity in each new lane receipt where practical."*
