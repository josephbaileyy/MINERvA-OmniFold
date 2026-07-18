Resume your independent publication-redteam context for a read-only G2 source
and background-cloud readiness audit. Do not edit C++, scripts, or docs; do not
build, submit jobs, acquire allocations, or message other workers.

Inspect the current full-event PET contracts and actual implementation paths,
including at minimum:

- nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md
- nd-unfolding/pet/FULL_EVENT_INTERFACE_REQUEST.md if present
- nd-unfolding/PET_UQ_REMEDIATION_STATUS.md Gates 1-3
- current point-cloud/full-phase-space C++ event-loop writer(s)
- current point-cloud NPZ dump/load/join code
- sbatch_evloop_array_pointcloud_fps_bkgcloud.sh and the associated hadd/dump
  launchers if present
- Agent B's 9d7a4c6 F7 loader interface
- current scalar/recoil/tree schemas and stable event keys

Determine exactly why the aligned full-event background inventory does not yet
exist and whether the untracked bkgcloud launchers are scientifically safe.
Audit required data/signal/background/truth alignment; full reconstructed and
truth muon schemas; recoil geometry/timing/type/masks/residual summaries;
background weights/POT scaling; FPS truth denominator/native misses; extended
edges/order; selection-complete P3F compatibility; stable playlist/event keys;
and provenance/fingerprint/atomic-output requirements.

Return:

1. PASS/BLOCK for G2 source readiness today;
2. a ranked exact file/line gap list;
3. the smallest ordered implementation packet and ownership boundaries;
4. unit/smoke/closure/alignment evidence required before a 12-playlist run;
5. an interactive-vs-batch placement plan with resource/wall estimates,
   dependency-safe queue-early points, unique namespaces, and duplicate-writer
   protections.

Treat current recoil-only xps/xps2 products and any purity target as controls.
Do not recommend launching production merely because an sbatch script exists.
