# Agent C repair round 2: close independent P3F-scalar validator blocks

Resume the same `agent-C-fps` UUID.  Preserve your uncommitted scoped repair and
fix it in place; do not touch unrelated dirty files.  Do not commit, launch the
0.681-TiB manifest scan, rerun physics, or start P3F-PET/PET.

The same-UUID agy publication redteam independently returned `BLOCK` on your
first repair.  Fix all of these, with focused negative tests:

1. Historical mode must require per-file SHA-256.  It must be impossible to
   exit 0 or write `complete=true` without `--hash-files`.
2. Require the exact expected inventory: all 120 expected files and zero extra
   endpoint ROOTs in the endpoint directories.  The current “extra” test does
   not test extras.
3. Bind every expected file to exactly one actual producer log—not aggregate
   corroboration.  A bounded census established:
   - 119 files were written by `55972324`;
   - task 0 was written by `55961845`; `55972324_0` is only a skip;
   - all 120 actual producer logs contain the validated MD5 and the runtime
     message `MNV101_FULL_PHASE_SPACE set`.
   Parse filenames with a strict regex such as
   `ev5d_active_fps_(JOB)_(TASK).out`; Gemini's suggested underscore split is
   wrong for these names.  Treat only an unambiguous `[active-fps] wrote PATH`
   as production; skip-only logs are not producers.  Verify log task,
   band/endpoint/playlist path mapping, MD5, full-phase runtime message, and bind
   producer job/task/log path/log SHA-256 per ROOT.  Missing or duplicate
   producers fail closed.  Require an explicit allow-list of producer jobs
   (`55961845`, `55972324`) rather than discovering arbitrary accepted jobs.
4. Query/match the exact producer task in accounting and require terminal
   `COMPLETED` with `0:0` for each allowed job/task.  Reject running, failed,
   missing, ambiguous, or nonzero evidence.  Make parsing unit-testable.
5. The FPS launcher was uncommitted at submit.  Do not label today's launcher
   hash/blob as production content.  Record it only as an observation-time
   candidate; set exact production content/source commit to unknown/null.  Bind
   the actual runtime behavior through the per-file logs above.
6. Make receipt publication unique-temp, same-filesystem, fsync'd and
   no-clobber.  A suggested implementation is mkstemp + file fsync + hard-link
   to the absent final path + unlink temp.  Do not use `os.replace` when the
   output must be collision protected.  Test pre-existing final and concurrent
   temp independence.
7. The canonical stale `p3s_fps_manifest.json` must never be overwritten by
   this historical-audit command, including through explicit `--out`.  Historical
   runs publish only to a preflight namespace and refuse an existing final;
   later promotion is a separate orchestrator gate.

Retain and re-test the four census fields, exact identity, four-tree schema,
finite positive POT, truth/reco completeness, miss metadata, point-cloud
branches, atomic receipt-last behavior, and explicit failure exits.  Add
negatives for missing hash flag, extra file, skip-only/missing/duplicate/wrong
producer, wrong MD5, absent FPS message, wrong task/path, nonterminal/nonzero
accounting, unproven launcher content, canonical output, and existing final.

Return verdict, exact diff scope, test count/results, and the exact corrected
batch command (including both allowed producer jobs) if code is ready for the
same agy UUID's second review.  Do not claim the manifest artifact passes; it
has not run.
