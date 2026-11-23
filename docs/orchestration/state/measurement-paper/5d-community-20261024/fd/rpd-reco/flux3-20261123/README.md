# RPD-RECO flux rerun at 6896e787 (rpd_flux3): config and scripts (2026-11-23)

**By** limitation-resolver, for the director's binding 2 addendum 2. Nothing in this directory has run. The connect runs
only on the director's GO for its exact sha256, with cov2d's fresh ack.

## Why a third flux run

P0 at the sacct-only checkout cannot read flux2's records:
- Bound `fd_rpd_reco.py` (7302cc1d), in `extracted_flux` (`:1994-2013`), requires the flux custody receipt's
  `custody_code_sha256` to equal the digest of the custody module beside it.
- flux2's receipt records custody `867822e3` (binding 2's, with the squeue call). The checkout at 6896e787 (#1251's
  merge) carries `634670b3`, which reads sacct only.
- So P0 at 6896e787 would STOP with FLUX_CUSTODY. Both reads of the P0 package found this, and codex-school2
  reproduced it.

The director ruled (A) on 2026-11-23: rerun the flux stage at 6896e787, so that everything from flux3 on runs on the
sacct-only custody. The alternatives were refused:
- (B), P0 at 763ab4dd: the chain would carry the squeue call, executed or not;
- (C), editing `fd_rpd_reco.py` to accept the old sha: that breaks the extract's own code binding.

## What changes from flux2

[`tools/gen_flux3.py`](tools/gen_flux3.py) produces every file here from flux2's committed package by counted
replacements, and refuses any other change.

- **Config** (`production-config.ready.json`, `d797183b…`): flux2's `7ebc2aa9` with exactly two leaves changed:
  - `flux_extract/path` and `flux_custody/path` move from `rpd-reco-flux2-20261122/run/` to
    `rpd-reco-flux3-20261123/run/`.
  - The new custody's receipt needs nothing else in the config; only its fence record's keys changed.
  - The bound `flux_selection_digest`, computed with `fd_rpd_reco.py` at 6896e787, stays
    `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`.
  - S1's retention strings are unchanged.
- **The clone** moves from 763ab4dd to `6896e7871421469ce72c6b93188d2d1a55c82ec6`, in the connect's `S` and in the
  job's HEAD check. The pin lists, in the connect and the job, change from 11 to 14:
  - custody `867822e3…` → `634670b3…`;
  - added: `tests/test_fd_rpd_reco.py` `e1b92ef0…`, `tests/fd_rpd_reco_fence_mutation.py` `138bc5b4…`, and
    `tests/fd_rpd_reco_mutation.py` `f2612369…` (binding 2's value, unchanged at S);
  - every other pin is checked equal at S, through `git show`, by the generator.
- **Names and limits:**
  - the job is `rpd_flux3`, an rpd* name that every fence watches;
  - the root is `/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123`;
  - shared QOS and `--time 01:00:00`, as for flux2;
  - the fence copy's `WRITE_ROOTS` takes the new root.
- **The step-2 sacct fence tightens flux2's block** (the director's acceptance of P0 finding 8, and codex-school2's
  flux3 read). Beyond flux2's rules, an empty JobName, a padded JobName, or a State with no non-space character is
  malformed and refuses. The family match is case-insensitive (`tolower($2)`). Under flux2's block, `123||RUNNING`
  and `123|other|   ` cleared.
- **The fetch records the identity check** (the director's ruling (A), item 3). Step 2b compares each of the 12 factor
  products' sha256 with flux2's (run-61806073's committed `flux-extract.json`) and prints
  `FLUX2 IDENTITY: N/12 byte-identical`. If any differs, it prints a STOP and exits 15 after the records are sent. That
  is a STOP to the director, not a reading.
- **The fetch's finish test is stricter** (codex-school2, the flux3 read and its confirm). Without `job.rc`, it uses
  sacct's state only from a successful call and one checked parse: a single awk pass counts every row whose JobID
  equals the job's as a string, and the well-formed ones (12 fields, a non-blank State). It prints the State and node
  list only if there is exactly one row and it is well-formed, and its exit status is checked. Otherwise it reports
  "cannot tell" and exits 10, and can be run again. A malformed duplicate refuses in either order. flux2's fetch accepted a terminal row from a failed
  sacct call, and awk's numeric comparison matched `061900001` to job 61900001.
- **The launcher's `connect`** takes cov2d's ack file as its fourth argument, the same guard as P0's:
  - the first line is `ACK-UTC <YYYY-MM-DDTHH:MM:SSZ>`, a real UTC time at most 6 h old and at most 5 min ahead;
  - the ack text follows, non-empty;
  - the guard first copies the file byte for byte into the session as `ack.txt`, then validates that copy, so the
    bytes checked are the bytes recorded. A NUL byte refuses, and any refusal, a failed copy included, removes the
    copy. The ack time must convert to a number and the clock read must succeed before the age is computed. The session directory
    is the committed run record (the director: no ack-only ssh step).
- The connect's inherited comment that the launcher's fence mode runs `cov2d_fence.sh` now says that mode is refused.
  An earlier draft added `-B` to two Python calls; codex-school2 flagged it as outside ruling (A), and it was removed.

The normalized diffs against flux2's scripts (roots and names folded, blobs elided) show only these changes.

## Checks on these bytes

- `gen_flux3.py` rc 0. Re-running it after black reproduces all five files byte for byte.
- The overlap fence on this config, with the repo at 6896e787 as the clone: `FENCE OVERLAP: CLEAR (allowed 1, stops
  0)` over 57 staged originals (`tests/fence_overlap_real_config.out.txt`).
- [`tests/test_sacct_fence.sh`](tests/test_sacct_fence.sh) cuts the block from `rpd_flux3_connect.sh` itself. **24
  checks pass and 17/17 mutants are killed**, including five new cases (an empty name, a padded name, an empty State,
  a State of spaces only, an uppercase family name RUNNING) and a mutant for each tightening.
- [`tests/test_launch.sh`](tests/test_launch.sh) uses stubs and dummies only. **23 cases pass and 13/13 mutants are
  killed**:
  - the ack guard: missing, stale (which also leaves no copy), malformed and fresh cases, plus a future time,
    seconds 60, leading spaces, trailing words, empty text, no final newline (copied byte for byte), a NUL byte and a
    failed clock read (a stub `date`);
  - the exit status, the cert check and fence mode.
- [`tests/test_fetch_finish.sh`](tests/test_fetch_finish.sh) cuts step 0 from the fetch and runs it against a stub
  sacct (and, for one case, a stub awk). **11 cases pass and 5/5 mutants are killed**. The cases: sacct failing while
  printing a COMPLETED row (exit 10); RUNNING (10); two rows (10); no row (10); a row for `061900001` (10); a short row
  (10); a full row with a blank-State duplicate, in both orders (10); the parse printing a row but failing (10); one
  terminal row (it proceeds); `job.rc` present while sacct fails (`job.rc` decides).
- [`tests/test_identity.sh`](tests/test_identity.sh): **4 checks pass and 3/3 mutants are killed**. The 12 expected
  shas equal run-61806073's records; all equal gives 12/12; one changed or one missing gives 11/12 and DIFFERS; the
  fetch exits 15 before its success exit.
- **The squeue grep:** the connect, the fetch and the launcher contain no `squeue`. The generator asserts it.

The test outputs are in `tests/*.out.txt`.

## Reads

The reports are under `~/codex-reports/note-measurement/reads/`. Grok's account is out of credit, so codex-school2
reads in its place.

| read | report | sha256 | verdict |
|---|---|---|---|
| agy, the package | `flux3-20261123/agy/out.txt` | `c5c6ab48c41e65c9effdaa8f1625411c07b925100c99a847c0eae58596bb0aac` | GO |
| codex-school2, the package | `flux3-20261123/codex2/out.txt` | `1efbbe7da135b494c5f481b81c13079a16ee8ab55ee00e0a0623339199bdb0bd` | FIX |
| agy, confirm 1 | `flux3-delta1/agy/out.txt` | `6d2ff40cb0ad1a24a0041e247ea8ceea3ccf894b408c5a4f7adb3bfccd42f5b1` | GO |
| codex-school2, confirm 1 | `flux3-delta1/codex2/out.txt` | `438fda3dc0f2b284996f6d6fa3f37486b2f365d51e28062a43fce09f70978155` | FIX |
| agy, confirm 2 | `flux3-delta2/agy/out.txt` | `2307a757b9d4434b9803d59447177d00cbd5021674a3846709825ed0f179e7a4` | GO |
| codex-school2, confirm 2 | `flux3-delta2/codex2/out.txt` | `a267711f4d4f9eca005ec2e972a9f343b441bc6f9c51d644a2ec595ffe811e94` | FIX |
| codex-school2, confirm 3 | `flux3-delta3/codex2/out.txt` | `dfb4a065696a132502d7a32f1b9548ead0c3fe003870e4b28111463ace951279` | GO |

codex-school2's four blocking findings (the ack bytes, a State of spaces, the fetch trusting a failed sacct call, and
the `-B` additions) and agy's two notes (the fetch's header, the identity test's path outside the repo) were all taken
as fixes, described above. The confirms found further blocking items, all fixed above:
- confirm 1: the fetch proceeding without one well-formed row for the exact job (a numeric JobID compare, short rows);
  two ack-guard failure paths (a partial copy left behind, a failed clock read); and README hashes of the previous
  revision;
- confirm 2: the fetch trusted a failed awk parse, and a malformed duplicate row made it depend on row order.

Confirm 3 (GO) had two non-blocking notes, both taken after it:
- the fetch's refusal message now names all three conditions (sacct rc 0, parse rc 0, one well-formed row), so a
  failed sacct call with one good row is no longer described as a row problem;
- the test's stub awk now keys on `print st "|" nd`, which no mutant edits, so `duplicates-allowed` is killed only by
  the two duplicate cases.

Those two changes touch only a message string and a test stub, and every suite was rerun on them.

Everything else both reads checked reconciles: every payload reproduces byte for byte; the
config differs only in the two paths; the digest is `75c2a1f4`; both pin lists are 14 entries matching 6896e787; the
wrapper is unchanged; and the identity table equals run-61806073's records.

## Files and shas

| file | sha256 |
|---|---|
| `production-config.ready.json` | `d797183bb5d459285224e4ee4d3fc8a0cc6cd64b136745ebf182bd716800e229` |
| `rpd_flux3_connect.sh` | `0a50f7db15df9bb31fe574c588a43c7f455609bb5f34e0e5acadd66aa062fbb4` |
| `rpd_flux3_fetch.sh` | `40645b69f02ee67db830fc9f95e3c69bf79cf46a9db4fbada26ce9da7ccf0f2e` |
| `rpd_flux3_launch.sh` | `91ae3a6a35c97040cfc444b4b91b29e63682ae80bd9221f1a2e71e85470459f6` |
| `tools/fence_overlap.py` | `f6541713e2cd4c8b342da5b76f59eec0662555e1cbe97da9ad95a52995594b35` |
| `tools/gen_flux3.py` | `f760c20d8c739ba4cf1a181ef1a970fad48e6c80ba207c8ffc1376f26527eccc` |
| `tests/test_sacct_fence.sh` | `2a238d9285ef38b36cbe5c0ae8bb110e3c4285696d7e6f20fb9c8ab13c408ba8` |
| `tests/test_launch.sh` | `74a6b5662f4ea3f4e13c1e92c42c83a39d5e14c130d8fb8575e8c58834377ae8` |
| `tests/test_identity.sh` | `5a053f6bc80ba11e77d5e96fe5b197482722d4aeb9df9f4f75db623e11ca4e00` |
| `tests/test_fetch_finish.sh` | `b1def180f5f7c5b24e0a4144417cc26eb363380037a2c106dbefe64625130d4f` |

## Before the connect

1. The director's binding 2 addendum 2, at the merged commit and these shas.
2. cov2d's ack no older than 6 h, saved as the ack file, and tier3-design's ack.
3. A valid cert. Joseph renewed it to 2026-11-24T05:57:28Z; the launcher's check is the authority.
4. Then `bash rpd_flux3_launch.sh connect <new dir> <login node> <ack file>`, with the output written beside the
   session directory.
5. The fetch after the job ends, judged by sacct. A fetch exit of 15 (not flux2-identical) goes to the director.
   Exit 10 means not finished, or cannot tell; run it again later.
