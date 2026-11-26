# FD-VF BINDING 2b: the V_F Phase 2 fetch, attempt 2 (402 files, NuE from the committed copy, reader pre-flight) (director, 2026-11-26)

**Follows** FD-VF BINDING 2 (`FD-VF-BINDING-2.md`, #1364). Attempt 1's one read (login02, 04:51:16–04:51:22Z) ended
with rc 9, a refusal by design. The listed NuE constraint path runs through `MParamFiles`, which is a symlink, and the
reader's `O_DIRECTORY|O_NOFOLLOW` open refused it without following it. 112 of 403 files had streamed. Nothing on the
cluster changed. The partial tar was never verified and has been deleted (`fd/receipts-vf/p2/attempt1.txt`: 8,516,608
bytes, sha256 `22ffcba3…`, 112 members). Under binding 2's ruling 4, attempt 1 is terminal.

**Authority:** as for bindings 1 and 2. The director's rulings of 2026-11-26 for 2b:
- the NuE constraint comes from the committed byte-identical copy;
- the reader gets a pre-flight check;
- one narrow confirm read is run on the diff.

**Binds** the fetch as merged in PR #1365 (merge `30036efd0181713185b9e135420a68df43eb804c`, at the reviewed head `1c205337c1fe7e955f18b163c6a606bf983ef84d`):

| file | sha256 |
|---|---|
| `fd/receipts-vf/p2/fetch-list.tsv` | `65fb73ca9d866ba4bd87e87e6bfe0b9d84d9a34ef02d5ebc0238b308c5cd7bcc` |
| `fd/receipts-vf/p2/fetch-vfp2.sh` | `61f57c6c9cf6d8bd65e4a67b0902724d6054c65384a392f013a92ba06a0bfa4e` |
| `fd/receipts-vf/p2/fetch_vfp2_remote.py` | `0a5e4228e4d51780432dcda3d3cc15260165d550c46c80cbdec11f8959ed8eb3` |
| `nd-unfolding/fd_vf_p2.py` | `bddc687df811ab55fb60626dda5bb9e8452be5f53de33ba2cbe4a237fff72cb7` |
| `FD-VF-ADDITION-AMENDMENT-A4.md` | `1c5bc531923a087c3b63811587e43c8c79b9d6750dd78408f8205370b4b22f71` |
| `NuE copy (fetch-b5d/sorted_NuEConstraint_FHC_RHC_IMD.txt)` | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. The NuE copy lives at
`docs/orchestration/state/ben-b-20261124/blocks5d-20261124/run-20261124/session/records/fetch-b5d/`, with its
`.PROVENANCE` note. The list holds 402 files and 1,595,625,533 bytes.

## What the director checked

- **The shas.** Each was hashed by command at the reviewed head, and each equals tier3-design's request. The list has
  402 rows and no NuE row. The committed NuE copy hashes to `e38ad7d2…`, which equals its pin.
- **The reader's diff since binding 2, read directly.** `preflight()` runs before any file is opened.
  - It lstats BASE first and refuses unless BASE is a plain directory.
  - It then lstats every component of every listed path, with no readlink, so no atime moves.
  - It refuses, listing every offender, on a symlink, a missing component, a non-directory parent or a non-regular
    final file.
  - Listed paths must sit under BASE with no `..`, and never-read files are refused.
- **The reads, as the lane reported them.** Narrow confirm read 2b-1 was NO-GO: children were stat'ed through a
  symlinked BASE, which is now fixed by lstat'ing BASE first. Read 2b-2 was GO on every in-scope item. Its one finding,
  a check-then-use race needing a concurrent same-account actor, is non-blocking under the director's scope ruling:
  the `O_NOFOLLOW` open still refuses a swapped link, and every file's sha256 is checked against its pin. It goes to
  FOLLOWUPS. There are 34 tests, all passing.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **Attempt 2's fetch is bound** with the shas above, and with binding 2's rulings 1–3 and 5–6 otherwise unchanged:
   - one session;
   - any sha256 that differs from its pin is a STOP, and nothing is substituted;
   - 0 node-h, and nothing written on the cluster or on CFS;
   - a valid certificate checked by command, which expires at 2026-11-26T15:19:52Z;
   - fresh acks from cov2d, limitation-resolver and director-helper-3, with the window ending 900 s after the oldest
     ack, limitation-resolver told just before;
   - the director's GO naming this binding.
2. **One read.** Any STOP after contact is terminal. A pre-flight refusal comes to the director with its listed
   offenders, before any byte is streamed.
3. **The NuE remap.** In the local recompute, the one exact `/pscratch` NuE path maps to the committed copy, under K's
   own pin check, and the remap is logged (amendment A4).

**CITABLE FOR:** that V_F Phase 2's second fetch attempt was bound, and on what, and that attempt 1 ended in a refusal
by design with nothing changed. **NOT CITABLE FOR:** any covariance, reading or note wording.
