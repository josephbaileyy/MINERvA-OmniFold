# EVW5D BINDING 1: configuration (e)'s central per-event weights, steps 1–3 (connect, post, fetch), one CPU node, cap 0.5 node-h (director, 2026-11-25)

**Authority:** Joseph, 2026-11-25. The unbinned 5D central value is released in v1
(`docs/orchestration/DECISION-20261125b-joseph-5d-unbinned-release-cinfl-naming-wording.md`, #1338; scope in
`docs/orchestration/DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md`, #1326). The declaration is
`fd/evw5d-20261125/EVW5D-DECLARATION.md`, revision 5, sha256 `b7646dacc43b3978354b3233e357149d7ce8d802b702829188f6a87a63804923`.

**Binds** the package as merged to main in PR #1341 (merge `82b8a67adc8e639db09e8445f0558b405bc97130`), at the reviewed head
`aea3fe67ee5335d25ae28cf437340146a38c668c`, merged with `--match-head-commit`. The tool commit is **`e01dd863787b6ed0b6ccf836ea0a9b60ed6ac3c3`**, an ancestor
of that head. The code pin is `abdc88c52b909cfc1eb658ae97bd9defc8f640e7` (the ESS run's), and the namespace is
**`/pscratch/sd/j/josephrb/evw5d-20261125`**.

| file | sha256 |
|---|---|
| `nd-unfolding/evw5d/evw5d.py` | `f6f5bbb5ea1c0c7a704dfcd64e1f214c587db1e64db3d9c9ae4e943ac01ad990` |
| `nd-unfolding/evw5d/sbatch_evw5d.sh` | `60fd4ec26714b2ccb956bd5abec4ba07092eca4c2f80b9ee1ab85bb02fd3533a` |
| `fd/evw5d-20261125/launch/bound/evw5d_launch.sh` | `51805bc1cf1fef493b99b68cb906fc79e8955498a66d6ed52445757eb50dd6a1` |
| `fd/evw5d-20261125/launch/bound/evw5d_connect.sh` | `a002ec55c2c7701896a709ed032f5cfa3d57c4ca6af0a5401c3e47ae1f30b584` |
| `fd/evw5d-20261125/launch/bound/evw5d_post.sh` | `a7927177d93d25aa9aac2e417b81e162e6790f3d88aaf0f25d13cd21526109e2` |
| `fd/evw5d-20261125/launch/bound/evw5d_hpss.sh` | `c61d9d927f7ded2179d214e34a193a061cb4fa0979002733656edbf60b5b87c2` |
| `fd/evw5d-20261125/launch/fill_pins.sh` | `faf724f09bc61d635e5b8afd527b6e48d8dec50e240f3d77db5cec40022f7552` |
| `fd/evw5d-20261125/FOLLOWUPS.md` | `d9ab5a0d8657eee016c209d80902174dae8fee576e6d34edf49ef4789c3ad06e` |
| `ess_capture.py` (at the tool commit) | `4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. `ess_capture.py` is
`nd-unfolding/ess_e/ess_capture.py` at the tool commit.

## What the director checked

- **The shas.** Each file above was hashed from `git show` at main after the merge. Each scripted pin equals the
  lane's PINS.txt and its message. The code under `nd-unfolding/` changed after the tool commit only in `test_evw5d.py` and
  `evw5d_mutation.py`; `evw5d.py` and `sbatch_evw5d.sh` are byte-equal at the tool commit and at the head.
- **The bound copies.** Each bound launch script differs from its template only in the pins `fill_pins.sh` writes
  (and, in the launcher, the one-level-deeper TOP path). `evw5d_post.sh` is byte-equal to its template.
<!-- absence-ok: describes what the bound scripts' code does (its write paths and checks), not a claim that a result does not exist -->
- **The scripts, read directly.** The launcher stages each remote script in a private `/dev/shm` file and runs it only
  if its sha256 is the bound one. The connect makes its claim on `$OUT` with `mkdir`. It checks that the three inputs
  have their recorded sizes (stat only), that half the iris balance covers the 0.5 node-h bound, and that both fresh
  clones are clean at their pins with the producer and tool bytes recorded. It runs the environment pre-check, submits
  one sbatch with the inherited scheduler variables removed, and cancels the job unless scontrol shows one node, no
  array and 30:00. The job script repeats those checks and runs `evw5d.py` as one 32-CPU step. `evw5d.py` writes only
  under `$OUT/evw5d`, stages its inputs through O_NOATIME, and writes no weights unless gate 1 (C-BIND, `xsec_flat`
  byte-equal to fb5cc679) passes. The post reads the job's state from sacct; `squeue` is used only to see whether a
  job is queued, as in ESS's approved connect and post. The HPSS step archives from a private snapshot, retrieves the
  whole archive and runs `accepted()` on the retrieved copy. Nothing is written to CFS.
- **codex-school r3's five blocking items (on revision 4)**, each checked in revision 5's code: the HPSS step takes
  every pin and the file list from a snapshot and runs `accepted()` on the retrieved bundle; the checker's bytes are
  pinned on the HPSS and fetch paths; `read_npz` refuses duplicate or non-`NAME.npy` archive members before parsing;
  the key and formula are fixed texts checked on the saved bytes; `strict_json` refuses duplicate keys and
  `canonical` is type-sensitive.
- **The reads and checks, as the lane reported them:** codex-school r1–r3 (all blocking items taken);
  claude-personal Sonnet 5.5 r2 (GO WITH CHANGES, taken) and r3 on revision 5 (GO, all non-blocking, in
  `FOLLOWUPS.md`); 120 tests pass (`receipts/tests.txt`); mutation at the tool code: control PASS, 118/124 killed;
  the six survivors rerun against the final tests (`test_evw5d.py` sha256 `9caf260bafa139c9636240b5fc2143ee95e4a444756be5bfc943db0ddf0a042a`): 4 killed, 2 equivalent
  (FILE_KEY_TEXT and FILE_AXES, each also required by `check_constants_json`). Not mutated, and accepted by the
  director: C-PINS after the run and C-KEY's early exit.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **Steps 1–3 are bound**: `evw5d_launch.sh connect`, then `post` after the job has left the queue, then `fetch`.
   Any changed byte goes back to the director.
2. **The price: about 0.28 node-h, cap 0.5 node-h**, one regular CPU node, exclusive, 30:00, `--no-requeue`. The
   connect refuses if 0.5 node-h is above half of m3246's balance.
<!-- absence-ok: preconditions checked fresh before the connect (a valid certificate, the director's GO), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - a valid NERSC certificate, checked by command, with enough time left for the whole step. A step that cannot
     finish before the certificate expires waits. No session is used past its credential's expiry;
   - the director's GO, by message, naming this binding. The director gives it only when no other bound job reads
     the three inputs plainly during the window (an O_NOATIME atime check would trip on a concurrent plain read).
4. **One connect.** Any STOP, FAILED or refusal after contact is terminal, and nothing is rerun without the director.
   A gate-1 STOP (`STOP.json`, rc 8) goes to the director as a result.
5. **Steps 4–5 (hpss, fetch-products) are not yet bound.** After `fetch`, the lane sends the director the post's
   verdict, VERIFY line, findings (C-COMPLETE included, with its sizes), the charge from sacct and the
   `SHA256SUMS` digest. The director binds that digest in a second binding before the HPSS copy runs.
6. **Hosting and wording are Joseph's.** Where the 1.74 GB `weights.npz` is deposited, and every note sentence about
   the 5D weights (including that they are valid only for unions of fine cells), are Joseph's.

**CITABLE FOR:** that EVW5D's steps 1–3 were bound, and on what. **NOT CITABLE FOR:** any weight, completeness, cross
section or uncertainty, the five-axis purity product, or any note wording.
