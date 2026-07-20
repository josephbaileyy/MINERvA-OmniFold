# Agent C continuity follow-up: P3F-scalar historical-provenance repair

Resume your existing `agent-C-fps` UUID and retain sole continuity ownership of
the FPS/P3F-scalar interface.  Gate 2 is committed PASS.  Do not rerun any
physics event loop, do not start P3F-PET/PET, and do not modify or promote any
negweight endpoint in this turn.

## Current evidence

- Slurm array `55972324_[0-119]` is historically recorded as terminal
  `COMPLETED/0:0`; the expected FPS active-universe directory appears to contain
  all 120 endpoint/playlists.
- Production-time installed-binary MD5 is
  `e63c74961d699313ef155065fc790ff1`, as recorded in
  `nd-unfolding/active_universe_5d/INTERFACE_VALIDATION.md` and the launcher
  controls used for the array.
- The existing untracked `fps/p3s_fps_manifest.json` is stale (4/120) and must
  not be promoted.
- A collision-isolated structural preflight is running as Slurm job `56162093`
  and writes only
  `fps/preflight/P3F_SCALAR_INTERFACE_PREFLIGHT.json`.  It is observation-time
  evidence, not production provenance.
- Preserved agy publication-redteam UUID
  `440f42ef-c271-4f77-a410-a4a999166f44` returned `PASS-REUSE`: no physics rerun,
  but P3F-PET remains blocked until the complete manifest securely binds
  historical provenance, every artifact hash, and migration census metadata.

## Required bounded work

Own the repair of `nd-unfolding/p3s_manifest_summary.py` and narrowly scoped
tests.  Work in the shared dirty tree without touching unrelated changes.

1. Add an explicit historical-provenance mode that is fail-closed.  It must not
   silently substitute current HEAD, the current installed G2 binary, or the
   current launcher for historical production facts.
2. Bind all expected 120 files by SHA-256 and retain the existing structural,
   playlist/endpoint identity, POT, truth/reco completeness, miss metadata, and
   point-cloud/schema checks.
3. Read and validate all four migration census TParameters:
   `activeUniverseTruthEntrants`, `activeUniverseTruthExits`,
   `activeUniverseRecoEntrants`, and `activeUniverseRecoExits`; aggregate them
   in the summary.
4. Negative-test missing historical inputs, missing/extra files, identity or
   endpoint mismatch, hash failure, and missing census metadata.  Publication
   must be atomic/receipt-last.
5. Inspect the actual array logs, launcher history, RUNS entries, and Slurm
   evidence before selecting provenance fields.  Important: repository history
   currently suggests the launcher may not have been committed at array-submit
   time (the first visible launcher commit is later).  Do **not** invent a
   `source_commit`.  If production source was uncommitted, represent that
   truthfully and bind the exact production launcher blob/content plus the raw
   durable evidence that establishes it.  Separate production-time facts from
   observation-time facts.
6. Do not overwrite the canonical stale manifest until the repaired validator
   has passed on all 120 files.  A temporary/output namespace is acceptable.

Return a concise owner packet containing: verdict; exact files changed; tests
and results; the provenance model; exact remaining blocker (including job
`56162093` if still unresolved); and whether the repaired canonical manifest is
ready for independent same-UUID agy verification.  Do not commit or push in
this turn: the orchestrator will apply the independent commit gate after the
preflight terminal receipt and verifier PASS.
