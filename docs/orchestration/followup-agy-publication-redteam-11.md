Recheck only the reset-watcher BLOCK you reported. READ ONLY; do not edit,
dispatch, heartbeat, alter PID 904875, or touch Slurm/workers.

Inspect the current diff of
`docs/orchestration/resume_after_school_reset_1800.sh`. Confirm that every
failed `run_role` now performs its post-error complete snapshot, returns the
provider error, and the caller immediately exits so C/B cannot run after an
A/C failure. Also confirm `bash -n` footing and that the rearmed PID/child
(`904875`/current child) execute the patched file. Return PASS or the exact
remaining defect. Do not reopen already-PASSed areas unless this patch regressed
them.
