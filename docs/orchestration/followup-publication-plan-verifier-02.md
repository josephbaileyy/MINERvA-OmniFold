Recheck only the one remaining blocker from your round-2 BLOCK in the same
publication-plan verifier session. Stay read-only.

The three controls now require the full-schema P3F-PET source inventory before
the publication nominal:

- P5A prerequisites include the complete committed P3F-PET source manifest and
  explicitly separate pre-nominal source production/validation from
  post-nominal endpoint retraining/covariance.
- The dependency graph now has `G2 -> P3FP -> NPET`.
- The PET DAG now places a committed Gate-3 P3F-PET inventory before Gate-4
  nominal, requiring exactly five bands by two endpoints by twelve playlists,
  joins, migration census, hashes, schema/estimator identity, atomic content
  validation, and the commit receipt. Gate 8 consumes those inputs for joint
  endpoint refinement/retraining/extraction.
- The optional hardening is also adopted: F7 replicas are independent
  single-rank jobs; Horovod and distributed rank slicing are prohibited.

Re-read the current versions of:
`docs/PUBLICATION_COMPLETION_RUNBOOK.md`,
`docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md`, and
`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`.

Return exactly `PASS` if the blocker is resolved without a new
publication-material ambiguity. Otherwise return `BLOCK` with the precise
remaining contradiction and smallest correction.
