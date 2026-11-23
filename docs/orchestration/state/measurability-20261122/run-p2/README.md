# MSR connect P, attempt 2: the probe ran, rc 0 (2026-11-23, tier3-design)

The run had the director's GO for attempt 2 (Joseph via the director, 2026-11-22), at package head `58f98a48`: connect
`msr_probe_connect.sh` fd7957fa, launcher 2f4a09f8, M `83d7aee5`. cov2d's fence rev 3 (7e81a721) was embedded.

- **Acks** (`lane/acks.tsv`, times from `date -u`): limitation-resolver 06:06:12Z, director-helper-3 06:06:18Z, cov2d
  06:06:44Z. The window ended at the oldest plus 900 s, 06:21:12Z (`lane/wend.txt`). limitation-resolver was told before
  the connect.
- **The session** ran on login38, 06:07:15Z–06:13:05Z (load 48.7 on 244 cores). ssh rc 0 and script rc 0. The /dev/shm
  copy was checked at fd7957fa. The tar `fetch-probe.tar` (sha256 da286042…, the log's) was fetched, and
  `RECORDS.SHA256SUMS` checked 29 files (`lane/launcher.out.txt`, `lane/records-check.txt`).

## What the log shows (`lane/connect-probe.log.txt`)

- **Fences:**
  - cov2d's fence rev 3 was CLEAR: `-S 2026-11-08T22:07:15`, 14 matching rows;
  - this lane's sacct fence was clear;
  - the one rpd_ row, 61806073 rpd_flux2, was COMPLETED;
  - the overlap was CLEAR: 1,482 pairs, 0 hits, plus the one allowed read-only interpreter pair.
- **Deploy:** the clone was at M with 0 porcelain lines before and after (pycache excluded). msr_build.py and
  msr_overlap.py were at their sha256.
- **Inventory** (stat and O_NOATIME sha256, `cluster/logs/stat.jsonl`):

  | input | sha256 |
  |---|---|
  | of_inputs_5d.npz | 07fccc1a… (its pin) |
  | bkg_dump.npz | 2addac8f… (its pin) |
  | stage.json | 0e58519f… |
  | log-floor/SHA256SUMS | 9870304d… |
  | re1 3D of_inputs_3d.npz | ecbff9f888ab19b5b9f7575ab41a27f83ab094f80efd4463790978c0145c318d (1,131,573,395 B) |
  | re1 4D of_inputs_4d.npz | a15cc6905f1273365f0116a973b0cbb28034b49a4d455da338ff9e5d8462b166 (1,341,266,457 B) |

- **The IBUKT bank:** at its recorded path, `prepare/out/bank.npz`, sha256 60416384… = A2's bank_sha256, 1,657,798,216 B.
  The stat of the root and of the file before and after the copy is identical, including atime: root 1795113716, file
  1795096824 (`cluster/logs/ibukt-stat-{before,after}.jsonl`).
- **Stage:** dd iflag=noatime copies of of_inputs_5d.npz, bkg_dump.npz and bank.npz, each at its pin.
- **Probe** (subsamples written by a separate process; 32,849,103 rows in each source):

  | part | f = 0.02 | f = 0.10 | full, two-point extrapolation | login gate |
  |---|---|---|---|---|
  | 5D | 3.4 s, 284,635,136 B | 4.7 s, 672,575,488 B | 19.3 s, 5,036,904,448 B | ok |
  | 2D | 1.4 s, 177,926,144 B | 5.9 s, 604,733,440 B | 56.5 s, 5,406,315,520 B | ok |

  **GATE login_ok = 1** (every part ≤ 1800 s and ≤ 8e9 B).
- **C-DID-CONS: EQUAL on both lists.**
  - J cells: 134 lines, sha256 bd1434b0… on both sides.
  - Occupied reco cells: 10,499 (D-ID's `reco_cells_expected`), sha256 8b82482b… on both sides.

  Both sides exited rc 0. The lists are in `cluster/didcons-*/`.
- **Records:** written and tarred after the clean-tree check; the connect ended rc 0.

## Disposition

C-DID-CONS is EQUAL, so C-DID is a STOP control in connect B (declaration rev 4). The probe numbers and the gate go to
the director, and connect B waits for its own GO. `$OUT` (/pscratch/sd/j/josephrb/msr-p-20261122) stays in place with the
deploy, the three staged copies and the probe directories, until the director rules on reuse or removal. Nothing was
written to CFS.

One note for connect B. The gate is per response, but `msr_build.py build` runs 5D, 2D and T3 in one process, and a
process's peak RSS does not fall. The two parts at about 5.0 and 5.4 GB could therefore stack past 8 GB. Connect B
should run each part in its own process, which is a change for the director's review.

Renamed records (git ignores `.err`, `.log` and `.out`) are listed in `RENAMES.tsv` with their sha256.
