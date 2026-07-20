# Same-UUID independent review: Agent-C P3F-scalar validator repair

Resume your existing `agy-publication-redteam` UUID.  Read-only verification;
do not edit, commit, launch jobs, or poll Slurm.  Gate 2 is PASS; P3F-PET/PET
remain prohibited.

Review Agent C UUID `4580f42d-77db-4f59-88c4-1b2854f24d82`'s uncommitted repair:

- `nd-unfolding/p3s_manifest_summary.py`
- `nd-unfolding/tests/test_p3s_historical.py`
- owner output in the newest `agent-C-fps` turn in
  `docs/orchestration/state/sessions.json`
- original reuse audit
  `docs/orchestration/runs/agy-publication-redteam/20260720T035906Z-send-bf39a026.txt`

Independently inspect the diff and tests.  Return a publication-gate verdict on
the code only: `PASS` or `BLOCK`, with exact defects and the smallest repair
packet.  Do not treat Agent C's 22/22 tests as sufficient by assertion.

Explicit red-team targets:

1. Historical mode documents `--hash-files` as required, but verify that an
   invocation without it cannot still exit 0 with `complete=true`.
2. Verify the inventory is exact: missing and unexpected extra endpoint ROOTs
   must both fail.  Check whether the current `inventory_complete()` and test
   named “extra” really test extras.
3. A bounded producer-log census established the true file lineage:
   - 119 task outputs were written by array `55972324`;
   - task 0 was written by prior array `55961845`, and `55972324_0` only says
     `skip (exists)`;
   - each of the 120 actual producer logs shows binary MD5
     `e63c74961d699313ef155065fc790ff1` and the
     `MNV101_FULL_PHASE_SPACE` runtime message.
   Verify the manifest binds each file to its real producer job/task/log and
   log SHA-256 rather than accepting one or many unrelated corroborating logs.
4. The FPS launcher was uncommitted at submission.  Verify the code does not
   misrepresent today's file content/hash as the exact production-time launcher
   content.  It may truthfully bind observed candidate content plus per-task
   runtime behavior, with source commit/content explicitly unknown where no
   durable evidence proves it.
5. Verify historical mode rejects non-terminal/nonzero array evidence and
   ambiguous or partial log sets; observation-time HEAD/binary must remain
   separately labeled and non-authoritative.
6. Verify atomic publication is collision-safe (unique temp, no-clobber where
   required) and that the canonical stale manifest cannot be overwritten by a
   failed/incomplete historical run.
7. Recheck all four census fields, exact endpoint identity, schema, POT,
   completeness, point-cloud branches, per-file SHA-256, and failure exit codes.

State whether the repaired code may be committed now and whether the 0.681-TiB
read-only complete-manifest batch may be submitted.  Do not authorize manifest
promotion or P3F-PET before the batch artifact itself independently passes.
