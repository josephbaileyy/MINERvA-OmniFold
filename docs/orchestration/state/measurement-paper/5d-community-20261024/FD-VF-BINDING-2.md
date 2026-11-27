# FD-VF BINDING 2: the V_F Phase 2 fetch, one login02 read-only session, 0 node-h (director, 2026-11-26)

**Follows** FD-VF BINDING 1 (`FD-VF-BINDING-1.md`, #1352), whose Phase 1 connect ran cleanly (receipts #1356,
readings #1359). **Authority:** as for binding 1 (DECISION-20261125b §1, option C). Phase 2 uses route (1), the full
step-K replay through `cmd_k`/`k_compute`, as declaration §4.1 declares (the director's ruling of 2026-11-26).

**Binds** the fetch as merged in PR #1363 (merge `dfc2c3d2116d48ad32b580fc933636ec21087dd3`, at the reviewed head `b7453fa21de9a971fb303036650deb88660ececa`, code commit
`3e6c9b1c49251380586f44293e0b127ee2033726` for confirm read 7):

| file | sha256 |
|---|---|
| `fd/receipts-vf/p2/fetch-list.tsv` | `92ba5b0d7c2d8063baa85ab2d978793760e42f67966199b0e15e8aebd87102d2` |
| `fd/receipts-vf/p2/fetch-vfp2.sh` | `5c1fdcc1d85ec9c071984e8b6fa25443f88a7cb16e164162c93b679b39bffe09` |
| `fd/receipts-vf/p2/fetch_vfp2_remote.py` | `3ea593f5b9ed3b87b24e8c333c210fc4a979f847ef5b0fff94794f301cb1dfdc` |
| `nd-unfolding/fd_vf_p2.py` | `f03ee171f2e00f66e379dc39419a05373da07455b5e5d3556243f5ced235b211` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. The list holds 403 files
and 1,595,650,936 bytes, all under `/pscratch/sd/j/josephrb/`.

## What the director checked

- **The shas.** Each was hashed by command at the reviewed head, and each equals tier3-design's request. The list has
  403 rows, every path under `/pscratch/sd/j/josephrb/`.
- **The wrapper, read directly.** It refuses unless the host is login02, with a fixed exit code of 2. It decodes the
  embedded reader and list and checks each against its pin on the raw decoded stream. It runs the reader with
  `/usr/bin/python3 -I`, and writes nothing on the cluster: no file, not even in /dev/shm.
- **The reader, read directly.** It is declared Python 3.6 compatible, and the director found no newer syntax. It
  opens each path component below the base with `O_NOFOLLOW` and the file with `O_NOATIME|O_NOFOLLOW`, refusing
  anything that is not a regular file. It checks each file's size by `fstat` before sending a byte, hashes while
  streaming the tar to stdout, and stops with exit 9 on a size or sha256 that differs from the list.
- **The reads, as the lane reported them.** codex-school's confirm reads ran to round 7, which is GO under the
  director's 2026-11-26 scope ruling: constructions of a deliberately malformed archive are non-blocking, because the
  per-file sha256 against the pin is the gate. Its one MINOR is in FOLLOWUPS. There are 33 tests, all passing, and
  the list and wrapper regenerate byte for byte.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **The fetch is bound** with the shas above: one session,
   `ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < fetch-vfp2.sh > <local tar>`, then
   `fd_vf_p2.py fetch-verify` into `/Users/josephbailey/vf-p2-fetch-20261126/`. **Any sha256 that differs from its
   pin is a STOP, and nothing is substituted.** Any changed byte goes back to the director.
2. **The price: 0 node-h.** It is a login-node read with no Slurm job and nothing written on the cluster or on CFS.
<!-- absence-ok: preconditions checked fresh before the connect (acks, a valid certificate, the director's GO), not claims that a result does not exist -->
3. **Preconditions:**
   - a valid NERSC certificate, checked by command, with enough time for the whole fetch. The certificate expires at
     2026-11-26T15:19:52Z;
   - fresh acks from cov2d, limitation-resolver and director-helper-3, each read by `date -u`. The window ends 900 s
     after the oldest ack, and limitation-resolver is told just before the read. The ack names the gencmp-x staged
     `of_inputs_5d.npz` (07fccc1a), cov2d's G2R paths, the NuE constraint and fd-prr;
   - the director's GO, by message, naming this binding.
4. **One read.** Any STOP after contact is terminal. One exception is left to the director: if the reader fails
   before opening any file (an interpreter error, an empty stream), that is reported as a pre-read refusal, and the
   director decides whether one corrected retry is bound.
5. **Locally,** the tar is deleted after the verify. Only the verified tree is kept, outside the repository and
   outside /private/tmp, and it is removed after the Phase 2 receipts merge, keeping what is committed.
6. **The local recomputes** follow amendment A4 and the director's rulings of 2026-11-26: the I/O remap, the local
   run directory and the V_F input substitutions, with the OLD control reproducing G2R's `k.json` at 1e-12 for
   bit-identical inputs.

**CITABLE FOR:** that V_F Phase 2's fetch was bound, and on what. **NOT CITABLE FOR:** any covariance, reading or note
wording.
