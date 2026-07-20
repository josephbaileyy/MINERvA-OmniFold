You are the preserved FPS selection-shift continuity owner `agent-C-fps`, UUID
`4580f42d-77db-4f59-88c4-1b2854f24d82`. Your availability heartbeat passed.
Implement only the new Gate-3 fresh-ROOT production launcher and its focused
login-safe tests. Do not edit the validator being written by Agent B, do not
touch existing scalar/G2 launchers or user-dirty files, do not launch compute,
do not commit/push, and do not start PET training.

Corrected footing:

- Generate fresh full-event ROOTs from the canonical raw Data/MC manifests.
  Existing scalar/purity/reduced-schema ROOTs are controls only.
- Exact inventory: bands `BeamAngleX`, `BeamAngleY`, `MuonResolution`,
  `Muon_Energy_MINERvA`, `Muon_Energy_MINOS`; endpoints `0,1`; playlists
  `1A,1B,1C,1D,1E,1F,1G,1L,1M,1N,1O,1P`; mapping task 0..119 by
  band-major, endpoint, playlist.
- Installed binary SHA-256 is
  `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`,
  built-source commit `486e53e677eb64eb9d622ff6e5daecb3e62aab22`.
  The active-interface commit `2e8c214...` is its ancestor and the current C++
  source is byte-identical to the built source.
- Runtime flags must be exactly active universe + point cloud + full phase
  space, with `MNV101_DUMP_UNIVERSES` unset.
- Use the hardened recovery/publication mechanics in
  `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh` as the pattern, without
  modifying it.

Create only:

1. `nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh`
2. `nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py`

Use the collision-isolated namespace
`nd-unfolding/p3f_pet_fullevent/{work,final,logs}`. Configure shared CPU,
4 CPUs, 48G, 12h, array `0-119%16`. Each task owns one unique
band/endpoint/playlist work directory, ROOT, validation JSON, and final receipt.
Bind the exact 24 canonical manifest SHA-256 values from the committed G2
launcher, expected binary SHA, built-source commit, new validator path/hash,
base G2 validator path/hash, and launcher hash supplied at submission. Use
existence-based RUN/CHECK/DIE classification; dangling symlinks count occupied;
per-task nonblocking flock; quarantine WORK-only partials; no-clobber hardlink
ROOT publication with identity/hash proof; unique same-directory receipt temp
with fsync and no-clobber receipt publication LAST. Reassert all footing before
compute, after the event loop, after validation, and immediately before publish.
Existing final/receipt one-sided or mismatched states must die without mutation.
Resume-skip only after full rehash and validator/manifest/binary/identity/receipt
match.

Invoke the event loop with the exact three flags and the new validator with
explicit expected band/endpoint/playlist. Production receipt schema:
`p3f-pet-production-playlist-receipt-v1`; include job/task/node, final ROOT
hash/size, input manifest hashes, binary/build/source/launcher/validator hashes,
environment flags, active identity and census, base-G2 validation counts, and
publication time. Add a define-only selftest mode. Because Agent B is creating
the validator concurrently, use a loud fail-closed placeholder token
`__P3F_VALIDATOR_SHA256__` for its bound hash; tests must prove launch is
impossible until the orchestrator replaces it.

Return exact changed files, test commands/results, hashes, and residual
blockers. Leave edits uncommitted for orchestrator integration.
