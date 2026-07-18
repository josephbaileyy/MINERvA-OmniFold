Your committed G2 source packet `486e53e` received an independent agy PASS.
Resume as the SAME durable G2 C++ source owner. This turn authorizes only an
OWNER-HELD INTERACTIVE compile/install of the canonical binary and a playlist-1A
full-event extended-FPS runtime smoke. It does NOT authorize the 12-playlist
array, MEFHC merge/NPZ, PET training, or any scientific endpoint.

Before compute, read AGENTS.md's current interactive/batch rules and the agy
acceptance checklist in your prior handoff. Inspect live `squeue -u $USER` and
`./alloc_run.sh --status`. The orchestrator observed no jobs/holders at 14:41
UTC; re-check rather than trusting that observation. Use exactly one
`alloc_run.sh` interactive holder for this short single-node gate. Do not submit
an equivalent sbatch, do not create a second holder, and leave the allocation
alive afterward. If any conflicting writer/holder appears, stop and report it.

Required stages:

1. Confirm HEAD contains `486e53e`, the four G2 files are clean, and no unrelated
   dirty file will be staged. Re-run the 474-check source guard.
2. Build and install `runEventLoopOmniFold` through the established in-tree
   environment/build path on the interactive node. Record the exact source
   commit, build command, installed canonical path, binary SHA-256, and compiler
   result. Never use or leave a build-tree binary as the runtime target.
3. Only after compile PASS, run a collision-free playlist-1A event-loop smoke
   with BOTH `MNV101_DUMP_POINTCLOUD=1` and
   `MNV101_FULL_PHASE_SPACE=1`, using the canonical installed binary and the
   canonical 1A manifests. Use a G2-smoke-only output namespace under
   `nd-unfolding/pet/`; write `.partial` then atomically rename after validation.
   Do not overwrite canonical or prior recoil-only ROOT/NPZ paths. If the full
   1A loop must outlive the LLM turn, launch a detached, logged, owner-identifiable
   command inside the single allocation and report PID/job/output/log plus a
   safe same-owner follow-up trigger; never claim PASS while it runs.
4. On a completed ROOT, add/run a login-safe or compute-node validator that
   fails closed on all of these:
   - positive POT and four expected trees;
   - exact metadata `petSchemaVersion=g2-fullevent-v1`,
     `hasFullEventSchema=1`, `fullPhaseSpace=1`;
   - runtime resolution and actual population of `ev_run/ev_subrun/ev_gate`,
     `cluster_view/cluster_time`, all declared reco/truth muon/vertex branches;
   - distinct data/reco/truth schemas with forbidden truth-detector/data-truth
     counterparts absent;
   - for every inspected/all feasible row, equal E/pos/z/view/time vector
     lengths; background cloud + `w_bkg` present and aligned;
   - native misses have `sim_pass=0`, reco muon/vertex sentinels and empty reco
     vectors, but valid cached truth identity/muon/vertex/cloud;
   - `mc_signal_reco` entry count equals `mc_truth_denom` after Phase-18.2
     bilateral dedupe (the by-construction completeness/c_global=1 invariant);
   - no default-path/selection/POT regression visible in the smoke.
5. Update only `nd-unfolding/pet/G2_FULLEVENT_CPP_DUMP_STATUS.md` and a compact
   G2-owned machine-readable smoke receipt/validator. Commit+push those evidence
   files only if the smoke completes and passes. Do not stage the large ROOT/log,
   dirty canonical ND STATUS/OPEN_ITEMS/KNOWN_ISSUES, or Agent A/B/C files. If
   only build completes or the smoke is still running, keep status explicitly
   BUILD-PASS/SMOKE-PENDING and do not make a publication-evidence commit.

Report the exact interactive job ID, placement rationale, build/binary evidence,
smoke state, output namespace, validation counts, commit if any, and remaining
gate. Preserve the one-writer rule and do not end the allocation.
