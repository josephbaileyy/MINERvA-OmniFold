You are the preserved publication PET contract owner `agent-B-p5b`, UUID
`46e4af3e-c3f2-4fa5-abc7-f0da72817282`. Your availability heartbeat passed.
Implement only the new Gate-3 validator and its focused tests; do not edit any
existing shared validator/launcher, do not touch user-dirty files, do not launch
compute, do not commit/push, and do not start PET training.

Corrected footing (independently checked by the orchestrator):

- Gate-3 requires FRESH 120-file selection-shifted full-event ROOT generation.
  Existing scalar ROOTs were produced by the older MD5 `e63c...` binary and are
  controls only; they do not establish `g2-fullevent-v1`.
- Current canonical installed binary:
  `MINERvA101/opt/bin/runEventLoopOmniFold`, SHA-256
  `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`,
  MD5 `f4f18045d74d5109dcd0f6abce9dc968`.
- It was built from commit `486e53e677eb64eb9d622ff6e5daecb3e62aab22`.
  Commit `2e8c214abc4b3ffc4ef371e8da6b5f107611862f` (active-universe
  interface) is its ancestor and current C++ source is byte-identical to the
  `486e53e` source (SHA-256 `57792e42...`). Thus the exact runtime combination
  is `MNV101_ACTIVE_UNIVERSE=BAND:IDX`, `MNV101_DUMP_POINTCLOUD=1`, and
  `MNV101_FULL_PHASE_SPACE=1`.
- Existing base G2 validator is
  `nd-unfolding/pet/validate_g2_fullevent_smoke.py`; do not weaken or modify it.

Create only:

1. `nd-unfolding/pet/validate_p3f_pet_fullevent.py`
2. `nd-unfolding/tests/test_p3f_pet_fullevent_validator.py`

The new validator must compose the complete existing G2 validator result and
fail closed unless all base G2 checks pass. Add exact active-universe checks:
`activeUniverseBand` equals the expected band, `activeUniverseIndex` equals the
expected endpoint, `hasActiveUniverse=1`, `activeUniverseIsLateral=1`, and all
four signed/nonnegative migration-census TParameters exist and are integral.
Validate the expected band/endpoint/playlist CLI arguments against the declared
5-band x 2-endpoint x 12-playlist inventory. Ensure the four trees, background
clouds/weights, data and MC identities, full-event metadata, native misses,
completeness, branch parity, finite/populated content, and base G2 schema remain
owned by the composed base result. The output JSON must bind the input ROOT
path/hash/size, base validator path/hash/result, this validator hash, expected
and observed identity/census, counts, and a single PASS/FAIL verdict. Receipt
writing must be unique-temp + fsync + atomic replace only to a caller-supplied
WORK path; it must never publish the final ROOT or production receipt.

Tests must be login-safe/ROOT-free, cover the exact inventory mapping and
negative identity/census/base-result cases, syntax-check the implementation,
and prove no output is published on failure. Reuse helpers where safe but do
not alter current G2 evidence. Return exact changed files, test commands/results,
hashes, and residual blockers. Leave edits uncommitted for orchestrator review.
