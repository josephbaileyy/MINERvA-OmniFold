# PILOT-FB copy connect (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3) (receipt)

**Status: written and tested, not run.** Revision 2 made the eight fixes K1–K8 the copy-connect read asked for
(`~/codex-reports/pilot-fb-audit/copy-connect/codex/report.md`; revision 1 was `8e2e3a1e`). Revision 3 is the
director's mechanical patch M1–M6 after the rev 2 read (`~/codex-reports/pilot-fb-audit/copy-connect-r2/codex/report.md`),
with residuals c1–c4 accepted. It runs only after the
smoke, on its own audit and the director's go for these exact shas, and after every fenced lane has acked (C1 ruling 3
step 1). Nothing has been copied.
<!-- absence-ok: an operational status of this connect, not a claim that a result does not exist -->

## What it copies

Into the stage the login-node smoke created, `/pscratch/sd/j/josephrb/pfb-20261117-stage`:
- `a0-refs/<name>`: RS1's 21 A0 products, the base `rs1_A0_b-_j-.npz` and jitters 1–20. They come from
  `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/A0/`, each at its pin in RS1's committed `runs-SHA256SUMS`. RS1's
  `rs1_A0_b-_j0.npz` is not copied (declaration line 189).
- `assess_receipt.json`: the σ receipt, from `<deploy>/docs/orchestration/state/s5e/cand/assess_receipt.json`, at
  `rounding_mechanism_analyze.SIGMA_RECEIPT_SHA256` (`84266e30…`).

Nothing else is written.

## The code (revision 3, commit 9d607e2f)

| file | sha256 |
|---|---|
| `nd-unfolding/pfb_copy_remote.py` | `6e38baa49a13c41a9370fe3db048e26fe0a5e382c78aca898e95d1ebb2c6faba` |
| `nd-unfolding/pfb_copy_launch.sh` | `72563b2114742a3dff82c46201012172c24bee4c559f5fdc389deff652dffa90` |
| `nd-unfolding/tests/test_pfb_copy.py` | `ca28f61756db58d87aed9dd843eeee6a4def19f5b6e34fdf8e942f826d54f623` |
| `nd-unfolding/tests/pfb_copy_testentry.py` | `e31bf0737aee438b001139430c1a049068d51efd92424320cbf33875bc762e3e` (test-only entry; never deployed) |

## The command (after the go)

```bash
bash nd-unfolding/pfb_copy_launch.sh <new empty dir> <loginNN> <deploy>
```

`<deploy>` is the clean checkout the smoke used. It must be an absolute `/pscratch/sd/j/josephrb/...` path, and its
git HEAD must be the pin in the smoke's receipt.

## The fixes (K1–K8)

| item | fix | test |
|---|---|---|
| **K1** one snapshot, verified at the endpoint | the launcher reads `pfb_copy_remote.py` once into memory, refuses unless that capture's sha256 is `SHA`, and sends that capture over ssh's stdin. Through saul, loginNN runs a fixed bootstrap: `/usr/bin/python3 -I -S -c 'import sys;exec(bytes.fromhex(sys.argv[1]))' BOOT SHA DEPLOY`. BOOT is the bootstrap's hex, so it needs no shell quoting, and SHA is on that command line. The bootstrap refuses (exit 10) unless stdin is a pipe or a socket, which catches an ssh `StdinNull`, and the bytes it reads hash to SHA. It then executes exactly those bytes. The laptop's verify runs from the same capture | `K1Snapshot` (tampered bytes and a /dev/null stdin each exit 10 with nothing written; the pinned bytes execute the production entry; an altered script at the launcher exits 8; the launcher reads once and sends the capture) |
| **K2** descriptor-anchored writes | the stage is opened `O_DIRECTORY\|O_NOFOLLOW`, fstat'ed, and its physical path (`/proc/self/fd`) must equal the literal declared stage. `mkdir a0-refs`, every `O_EXCL` create, and every readback go through `dir_fd`. Each copy is checked through its own descriptor, `O_RDWR`, written, fsync'ed, read back and fstat'ed, against its literal declared path | `K2Descriptors` (a symlink swapped in for the stage, and a stage under a symlinked parent, refuse with no write) |
| **K3** no test hooks in production | the production entry exits 2 before anything else if any `PFB_COPY_*` variable is set. Tests build their own `Config` in `tests/pfb_copy_testentry.py` | `K3NoTestHooks` |
| **K4** stat integrity | each source's open descriptor is fstat'ed before and after its read: size, mtime_ns, ctime_ns, atime_ns, mode, nlink, ino and dev. The path lstats before and after must identify that descriptor | `K4StatIntegrity` (a chmod during the read, and a path swap during the read, each exit 8 with nothing written) |
| **K5** fence parsing | `/usr/bin/sacct` by absolute path, with a fixed environment. Every row must have its three fields non-empty; a missing or blank field means not clear | `K5Fence` (`61\|\|RUNNING`, a blank state, a blank JobID, a failed sacct, an absent sacct and an active fenced job each exit 9; a fence that becomes active after the copy is exit 9 with the manifest and the copies left in place) |
| **K6** a strict verifier | it requires, for all 22 copies: the declared source and copy paths, both descriptor stat records (typed and equal), distinct source and copy inodes, path inodes identifying the descriptor, one link, the pin, and no moved field or problem. It also requires both fence reads, with their rows, from `/usr/bin/sacct`, and the smoke binding. Any missing field fails | `K6StrictVerify` (18 mutations, including the report's) |
| **K7** explicit STOP on I/O errors | a read-side error is exit 6, or exit 3 for an O_NOATIME EPERM, before any write. A write-side error after the first write is exit 6, with a partial-state manifest naming every created path, which stays in place. A stopped manifest never verifies | `K7IOErrors` (ENOSPC injected on the last copy; an O_NOATIME EPERM) |
| **K8** bind to the smoke | `smoke-receipt.json` is read through the stage's descriptor: a plain file with one link, valid JSON. Its stage must be the literal declared stage, its pin the deploy's git HEAD, and its `local_test` false, and it must record an INDEX sha256. Otherwise exit 2 | `K8SmokeBinding` |

## Revision 3: the mechanical patch M1–M6

| item | change | test |
|---|---|---|
| **M1** (K1) | the bootstrap exits 10, with its message, if `os.fstat(0)` raises (an EBADF from a closed fd 0). The launcher's BOOT hex and SHA change with it | `Rev3.test_m1_a_closed_stdin_exits_10` |
| **M2** (K5) | sacct's environment carries `HOME=/global/homes/j/josephrb` literally, never the inherited value | `Rev3.test_m2_sacct_gets_the_literal_home` |
| **M3** (K6) | verify requires every key in every record (`REQUIRED`). Every count, stat and inode field must have `type(x) is int`, so a bool is rejected. `copy_nlink` must be exactly 1 and `copy_mode` a regular file. The source stat record's (dev, ino) must be `source_inode`, and `bytes` must be the source's size. Each fence's command must be the exact argv the remote builds (`fence_argv`). Any exception in verify is exit 2, never a traceback | `Rev3.test_m3_the_verifier_is_strict` (the report's combined mutation, a missing name, a stat ino not its `source_inode`, nlink 2, a non-regular mode, and malformed and non-JSON manifests) |
| **M4** (K7) | every read before the first write is wrapped. The receipt, the INDEX and git HEAD exit 2 on an OSError; a source exits 5. A late lstat EIO is 5, while a source that vanished stays 8. Nothing is written | `Rev3.test_m4_an_io_error_before_the_first_write_writes_nothing` (an EIO injected on the receipt read; a late lstat EIO) |
| **M5** (K8) | `smoke-edges/INDEX.json` is opened through the stage's descriptor, as a plain file with one link, O_NOFOLLOW. Its sha256 must equal the receipt's `index_sha256`, or exit 2 | `Rev3.test_m5_the_index_must_be_the_receipts` (a missing INDEX, a wrong digest, a symlinked INDEX) |
| **M6** (the FIFO regression) | the receipt and the INDEX are `fstatat`'ed without following links and must be regular files of their own before the open. The open is `O_NONBLOCK`, and its fstat must be the same file | `Rev3.test_m6_a_fifo_receipt_refuses_without_blocking` (a FIFO receipt and a FIFO INDEX each refuse, under a 5 s timeout) |

## Accepted residuals (the director's ruling on rev 2)

- **(c1)** The saul relay and the loginNN shell are trusted transport.
- **(c2)** `/usr/bin/sacct`, `/usr/bin/git`, `/proc/self/fd` and the real O_NOATIME are proven only at the connect, where
  each fails closed.
- **(c3)** If the stage or `a0-refs` is renamed after it is opened, writes land in the renamed directory, inside our
  scratch. This is detected, and it STOPs with exit 6 without touching an original. Detection only.
- **(c4)** Bash capture drops NUL bytes. But the bytes hashed, sent and executed are the same capture, and it matches
  the pin.

## The holds (unchanged)

- No job, and no sbatch, srun or salloc.
- It writes only `a0-refs/` (21 files) and `assess_receipt.json` in the stage, and nothing on CFS.
- The inner ssh writes nothing on saul.
- Any STOP, failure or timeout goes to the director unrepaired. Nothing is re-run.

## Receipt

- `tests.txt`: the 25 tests in a clean clone at 9d607e2f, exit 0. They import `fb_pilot_analyze` and
  `rounding_mechanism_analyze`, which import `rounding_mechanism_probe` (the pins and the analysis's own copy check).
- **Not covered here:**
  - `/usr/bin/sacct` and `/usr/bin/git` on loginNN. If either is missing, the copy fails closed (9 or 2), a STOP for
    the director.
  - The real O_NOATIME open, and `/proc/self/fd` (the laptop tests use macOS's `F_GETPATH`).
  - A run under Python 3.6: only a grammar parse here.
