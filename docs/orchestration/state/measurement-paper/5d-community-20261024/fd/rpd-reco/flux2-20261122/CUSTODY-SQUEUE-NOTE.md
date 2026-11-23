# Note: custody prepare's squeue ran in flux1 and flux2 (2026-11-23)

Custody prepare's squeue at `fd_rpd_reco_custody.py:408` ran read-only in flux1 and flux2. It was removed before P0
(PR #1251).

- In binding 2's code (763ab4dd, custody sha256 `867822e3…`), the COV2D fence ran
  `squeue -u josephrb -h -o %i|%j|%T|%M|%l` inside each job and then a `sacct -j` read of two named jobs. Both runs
  record its output in `run/cov2d-fence.json`:
  - flux2: [`run-61806073/records/run/cov2d-fence.json`](run-61806073/records/run/cov2d-fence.json), `queue_stdout`
    showing only 61806073 itself;
  - flux1: `../flux1-20261111/run-61206960/records/run/cov2d-fence.json`.
- Joseph's standing rule is "sacct, never squeue". The flux2 package (connect, fetch, launcher) was sacct-only, but
  this bound module was outside the package reads. limitation-resolver disclosed it in the #1248 report, and the
  director is disclosing it to Joseph.
- No result rests on it, because the sacct read also ran and both fences passed.
- The fix is in [`../custody-sacct-20261123/REPORT.md`](../custody-sacct-20261123/REPORT.md): the fence now makes
  two narrow-window sacct reads, fail-closed in cov2d_fence.sh rev 2's pattern, probed once on Perlmutter. P0 READY binds the new custody sha.
