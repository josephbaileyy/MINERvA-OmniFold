# Same-UUID recheck: P3F-scalar validator repair round 2

Resume the same `agy-publication-redteam` UUID.  Read-only review; no edits,
commits, job launch, or polling.  Re-review the current uncommitted:

- `nd-unfolding/p3s_manifest_summary.py`
- `nd-unfolding/tests/test_p3s_historical.py`
- Agent-C turn 6 in `docs/orchestration/state/sessions.json`

Your previous BLOCK listed six defects.  Verify each is actually closed in code
and by meaningful tests, not just restated in the owner packet.  Independently
check the exact log regex, skip exclusion, allow-list, per-file unique producer,
MD5/FPS message/task mapping, `sacct` task terminal gate, mandatory hashes,
extras, launcher truthfulness, canonical protection, and no-clobber publish.

The orchestrator's independent real-evidence check now reports:

- indexed producer paths: 120;
- producer jobs: `55961845`: 1 and `55972324`: 119;
- unique producer-log SHA-256 values: 120;
- per-file bind/accounting failures: 0;
- extra endpoint ROOTs: 0;
- focused tests: 27/27 PASS; Python compilation and diff check PASS.

Red-team residual details too:

- `sacct -j JOB_TASK` currently returns the task allocation followed by batch
  and extern rows; verify parsing the first task allocation is safe and rejects
  absent/ambiguous cases.
- Verify terminal accounting evidence is represented sufficiently in the final
  per-file receipt, not merely checked and discarded.
- Historical standard-mode behavior may be explicitly unsupported/fail-closed;
  it must not silently use FPS provenance if invoked.
- Check that broken symlinks/pre-existing finals and publication failures cannot
  clobber data or leave a false successful receipt.
- A failed/incomplete scan may write a clearly failing preflight receipt, but it
  must exit nonzero and cannot touch the canonical manifest.

Return exactly one verdict: `PASS` authorizing a scoped code/test commit and the
read-only 0.681-TiB complete-manifest batch, or `BLOCK` with exact minimal
repairs.  Even on PASS, do not authorize manifest promotion or P3F-PET before
the batch artifact and independent artifact validation pass.
