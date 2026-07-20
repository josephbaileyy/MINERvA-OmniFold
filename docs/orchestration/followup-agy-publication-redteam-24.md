You are the existing publication provenance red-team worker. Preserve your role and UUID.
Perform a read-only, decision-ready audit; do not edit, commit, launch jobs, poll job 56162093,
or start P3F-PET/PET training.

Current dependency: the runbook requires a committed P3F-scalar interface inventory before
the fresh full-schema P3F-PET source inventory. Gate 2 is committed PASS. The exact 5 bands x
2 endpoints x 12 playlists paths appear physically populated under
`nd-unfolding/active_universe_5d/fps/`, but the untracked `p3s_fps_manifest.json` is stale
(4/120, generated mid-production). Historical array 55972324 later reports many/all tasks
completed. Those artifacts were produced with binary md5
`e63c74961d699313ef155065fc790ff1`; the currently installed G2 binary has since changed.
Naively rerunning `p3s_manifest_summary.py` records observation-time HEAD/current binary and
could overclaim production provenance.

Inspect at minimum:

- `docs/PUBLICATION_COMPLETION_RUNBOOK.md`, P3F-PET prerequisite/order;
- `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md`, publication PET route;
- `nd-unfolding/p3s_manifest_summary.py`;
- `nd-unfolding/active_universe_5d/INTERFACE_VALIDATION.md`;
- `nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps{,_cpu}.sh`;
- historical Slurm/log evidence for array 55972324;
- the exact expected 120 artifact paths and stored ROOT metadata/schema;
- current git history and binary/source provenance boundaries.

A collision-isolated batch structural preflight is queued as job 56162093 and has a waker;
do not wait for or infer its outcome. Determine now:

1. whether the existing endpoint ROOTs can legitimately satisfy the *P3F-scalar interface*
   prerequisite (not P3F-PET full-schema production), and under what exact conditions;
2. the smallest fail-closed validator/receipt repair that binds production-time source,
   launcher, installed binary, exact 120 paths/hashes, schema/identity/counts/POT/misses,
   migration census and extended-FPS flags without substituting observation-time provenance;
3. whether Agent-C must own/write that repair and whether any artifact must be rerun;
4. the exact PASS/BLOCK gates before fresh P3F-PET production may start.

Return PASS-REUSE or BLOCK-RERUN with ranked evidence and a concise implementation packet for
the continuity-bound Agent-C owner. Do not authorize publication promotion yourself.
