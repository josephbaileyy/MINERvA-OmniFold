# rpd_p0, 2026-11-24 (login05): P0's records

**By** limitation-resolver, under [`FD-RPD-RECO-BINDING-2-ADDENDUM-3.md`](../../../../FD-RPD-RECO-BINDING-2-ADDENDUM-3.md)
(merged c1be6ca7), at M_P0 = `13aee9c05c7c36cf1cf1e642d58244400932e841`. P0 is described in [`../README.md`](../README.md).

**Result: DONE, `p0.rc` = `rc=0 cause=exit`.**
- All four steps (`pins --dry-run`, `p0 --dry-run`, `pins`, `p0`) ended PASS under the supervisor. The chain took
  25 s, from 03:18:07Z to 03:18:32Z.
- Every ruling-5 check holds (below).
- The price is 0 node-h: login node only, with no job.

- **CITABLE FOR:** that P0 ran as bound and passed its checks; its step records and their contents as records.
- **NOT CITABLE FOR:** any RPD-RECO result or note wording. The step records' own `does_not_license` list applies:
  which period or flux is correct, any correction or exclusion, a change to estimator or covariance, validation or
  coverage, or removing the unknown-cause clause.

## Preconditions (ruling 3)

- **The bound files.** The launch ran from a worktree detached at c1be6ca7. All ten bound sha256s re-hashed to the
  addendum's values there, including the runner hashed from the connect's heredoc (`3ef4abad…`).
- **cov2d's ack.** It is `ACK-UTC 2026-11-24T03:15:46Z` and cov2d's text, verbatim. The launcher read it at age 50 s
  and recorded it byte for byte as [`connect/ack.txt`](connect/ack.txt) (sha256 `bace3bce…`).
- **tier3-design's ack.** Given at 03:15:31Z, verbatim in [`acks/tier3-design-ack.txt`](acks/tier3-design-ack.txt).
- **The cert check.** The launcher read the cert as valid to 2026-11-25T01:36:35Z.
- **The run root.** Absent before the connect, on all four surveyed nodes and by the connect's own guard.

## The survey: [`survey/`](survey/)

The bound launcher (`b70998ff…`) ran in its `survey` mode on login05, login12, login21 and login30.
- The root was absent on all four.
- The 15-minute loads were 33.48, 51.69, 67.46 and 84.12, so login05 was chosen.

## The connect: [`connect/`](connect/) (login05, 03:16:46Z to 03:18:07Z)

ssh rc 0, script rc 0. The launcher's output was written beside the session directory, as `launcher.out.txt`.

- `node login05 staged sha256 6a1bed95…`, the bound connect.
- **Step 2, the sacct fence:** `sacct rows (14 days): 80; cov2d/t2a/rpd rows: 17`, `FENCE: clear`. Five
  `61885471_N|ibuchi_evl|RUNNING` rows were listed as unended. That family is outside the fence by the addendum's
  ruling 4, so they did not refuse.
- **Step 3, the clone:** `HEAD 6896e7871421469ce72c6b93188d2d1a55c82ec6; porcelain lines 0`, with the 14 pins equal.
- **Step 4, the config:** `sha256 3b2afde4… (expected 3b2afde4…)`.
- **Step 5, the in-place inputs:** `P0 INPUTS: PASS (14 files, 0 bad)`. flux3's `flux-extract.json` `90445ece…`,
  `flux-custody.json` `226c7a68…` and the 12 factor products each equal run-61861637's records, read with O_NOATIME.
- **Step 6, the retention record:** `P0 STAT: PASS (27 files, 0 missing or different)`.
  - The 24 dumps and the three gen2thin files have S1's bytes and inodes.
  - The earliest purge exposure is 2026-12-30T11:38:24Z (`lat_1A.npz`, atime 2026-11-04T11:38:24Z).
  - The table is [`records/stat-p0.txt`](records/stat-p0.txt).
- **Step 7, the overlap fence:** `FENCE OVERLAP: CLEAR (allowed 1, stops 0)` over 57 staged originals.
- **Step 8, the `/dev/shm` copy:** HEAD 6896e787, porcelain 0, the 14 pins again, config `3b2afde4…`.
- **Step 9, the runner:** sha256 `3ef4abad…`, pid 1269346 on login05 since 03:18:07Z (start ticks 46054889).
  `/dev/shm/limres-rpd-flux1` was handed over.

## The run (`records/`)

[`records/runner.out`](records/runner.out) shows:
- the runner at nice 19;
- `handoff.ok`;
- one monotonic deadline, 7200 s from the handoff;
- each step's PASS line;
- `== P0 DONE`;
- `removed /dev/shm/limres-rpd-flux1`.

The supervisor records (`records/sup-*.json`), one row per step:

| step | worker rc | signal | deadline signalled | past deadline | leftover | group gone | peak RSS |
|---|---|---|---|---|---|---|---|
| pins-dry | 0 | none | no | no | no | yes | 35,700,736 B |
| p0-dry | 0 | none | no | no | no | yes | 142,704,640 B |
| pins | 0 | none | no | no | no | yes | 37,748,736 B |
| p0 | 0 | none | no | no | no | yes | 140,455,936 B |

The largest peak is 0.143 GB, against the 8e9 B cap; the macOS estimate was 0.189 GB.

**The step records** (schema `fd-rpd-reco-step/1`, all status PASS, `code_sha256` `7302cc1d…`, `config_sha256`
`3b2afde4…`):
- `dry/pins.json` and `run/pins.json` carry `dry_run` true and false, with no predecessor;
- `dry/p0.json` and `run/p0.json` name, as `predecessor_sha256`, the sha256 of the pins record in their own directory
  (checked locally);
- `run_class` is `diagnostic`.

**The two pins records are held out of git.** Each names its staged dumps and `nn_*.npz` products by bare filename
as well as by absolute path. The receipt-artifact hook (`verify_receipt_artifacts.py`) reads the bare names as missing
deliverables and refuses the commit: 24 citations, 12 per record. The repo practice is not to widen the shared checker
from a lane, but to keep such records out of git, listed by sha256 (as flux1, flux2 and flux3 did with
`prestage.json`). Both were fetched, and each matched its printed sha256:

| record | bytes | sha256 |
|---|---|---|
| `dry/pins.json` | 12,069 | `ce181449d5ba6dbafc4a5831b7918c4d3cc538114062ce23c5e464291bcc3f76` |
| `run/pins.json` | 12,053 | `52fc41f41cf17954ceddab8c581aa327a62d160c059cbee8bf2941c1880e5c8a` |

These are exactly the `predecessor_sha256` values that the committed `dry/p0.json` and `run/p0.json` carry, so the
chain stays checkable from the committed records. The originals stay in the run root on pscratch.

## Ruling 5: the product

- **The in-place inputs** equal run-61861637's records: 14 of 14 (step 5 above).
- **The retention record** finds the 27 files with S1's bytes and inodes (step 6).
- **All four steps** exited clean under the supervisor (the table above).

## A finding for the director: P0's runtime estimate exceeds two hours

`run/p0.json`'s `result.runtime_estimate` is the bound code's planning estimate for the later steps:

| field | value |
|---|---|
| `exceeds_two_hours` | true |
| `needs_director_price` | true |
| `node_hours_authorized` | 0 |
| `planning_seconds_with_factor_10` | 52840.04 (the campaign total) |
| c0 | 50689.22 s |
| d2-predict | 2150.82 s |
| pins, p0, step0, d1, d2 | 0 s |
| `poisson_only_seconds` | 5284.00 |
| `poisson_draws` | 164,443,705,000 |
| `timing_sample_draws` | 262,144 in 0.00842 s |

- The record names three costs it did not measure: NPZ decompression, histogramming, and sorting weighted quantiles.
- Its `summary_only` note says "admission compares each step's own estimate".
- This is a reading of the record, reported to the director for pricing. It is not a P0 STOP: P0 itself ended DONE.

## The fetch: [`fetch1/`](fetch1/) (login05, 03:33:43Z to 03:33:44Z, bound fetch `12626af6…`)

Script rc 0, launcher rc 0. The fetch reported:
- `p0.rc: rc=0 cause=exit end=2026-11-24T03:18:33Z`, state DONE;
- `dry/staged: 43 files` and `run/staged: 43 files`, which stay on pscratch;
- 18 files sent, 384,121 bytes, `TAR END tar rc=0 base64 rc=0`.

The tar's 18 entries are all plain relative paths. Untarred locally, each matched its printed sha256 under
`shasum -c`. `records/` holds 16 of them; the two pins records are held out (above).

`fetch1/session.notar.out` and `fetch1/launcher.notar.out.txt` are the session and launcher outputs with the base64 tar
block replaced by one line. The full files had these sha256:
- `session.out`: `e0f313d3aeb117d7a56cc9701d7bca13207deb76b0183d61039f08f929174f2b`;
- the launcher output: `f5a71b9a5f9383fa963b325a975c1a480f79ad6c6ec5e572a706c44195e8140e`.

## Left on pscratch

`/pscratch/sd/j/josephrb/rpd-reco-p0-20261123` holds the clone, the tools, the staged copies (`dry/staged`,
`run/staged`) and the `.pgid` files. `/dev/shm/limres-rpd-flux1` on login05 was removed by the runner.

[`SHA256SUMS`](SHA256SUMS) covers every file in this directory except itself.
