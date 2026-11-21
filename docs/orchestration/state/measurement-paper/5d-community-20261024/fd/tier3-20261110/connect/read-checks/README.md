# T3 read connect (c5): the checks made before it goes to the director (tier3-design, 2026-11-21)

T3-CONNECT-PLAN.md section 6 row c5 is "fetch both jobs' records, then `t3p_read.py` per the declaration §7". It had
no script. These are the two new scripts and the checks run on them, at 0 node-h, before the director's go.

- **`../t3p_read_connect.sh`**, sha256 `fb7788751ae2028e9b0a11e46577efcf9f10d030894b6dc0d0a9baa7026c5227`. It is
  derived from FD-PRR's reviewed read connect `prr_read.sh` (42716ca4…, `fd/receipts-prr/read/cluster/`). The diff is
  `prr_read-to-t3p_read_connect.diff.txt`. What differs:
  - the fence uses `t3p_submit.sh`'s sacct function (50e86da3), unchanged, in place of `squeue --me`, plus a window
    epoch;
  - the job states come from sacct for the three ids (61726250, 61728686, 61731751);
  - the deploy checks the six bound T3 files and the declaration and addendum V1 against their bound sha256 (the same
    values as `t3p_submit.sh`);
  - the products are checked against `log-floor/SHA256SUMS` (36 lines, and exactly 36 `.npz` under `runs/`), and
    log-dry's and log-q3's still hold;
  - `t3p_read.main`'s own stdout (its readout text) goes to /dev/null, so the log holds the verdict only;
  - the records are copied through `dd iflag=noatime` into `$OUT/fetch-read/`, each copy checked against its source,
    with a `RECORDS.SHA256SUMS` file, then put in one tar whose sha256 the log prints.
- **`../t3p_read_launch.sh`**, sha256 `ab71010486e2bd6c74c2728c44f26718cc171411f6c6135917a6fcb39314d542`. It is
  `t3p_launch.sh`'s pattern pinned to the read connect's sha256 (diff `t3p_launch-to-t3p_read_launch.diff.txt`).
  - After the session, it streams `fetch-read.tar`, `logs/connect-read.log` and `logs/connect-read.done` with
    `dd iflag=noatime`.
  - The tar's sha256 must equal the log's, and `RECORDS.SHA256SUMS` must check.
  - It fetches nothing if the connect bailed.

## The guarded read on test_t3p's planted fixture (`guarded_fixture_read.py`, `guarded-fixture-read.log.txt`)

The connect's Python body ran in a detached worktree at M_V1 = 8bb4e3b0, on `test_t3p.EndToEnd`'s planted run (M16 =
identity, the fixture's own patch). `ref_g1.PROTECTED` was widened over the temp root and the clone's parent. The
results:
- `{"verdict": "COMPLETE"}`, rc 0, and the out directory held exactly readout.json and readout.txt;
- the same guard refused a plain read outside the allowed roots (the control);
- the clone's `status --porcelain --ignored` was 0 afterwards.

## The shell flow in a Debian container (`standin.sh`, `Dockerfile.txt`, `standin-*.log.txt`)

- **Setup.** python 3.11, numpy 1.26.4 and scipy 1.16.3. The real OUT path `/pscratch/sd/j/josephrb/t3p-20261121`
  holds test_t3p's planted run with 36 products. The connect script was copied to `/dev/shm` and run as the launcher
  runs it.
- **Stubs.** Two only:
  - `sacct` (the three jobs' states);
  - `git clone`'s URL, rewritten to a `--shared` clone of the read-only host object store.

  The checkout, `rev-parse`, `status`, `sha256sum`, `dd iflag=noatime`, `find`, `tar`, `ionice` and the reader are the
  real tools.

| variant | what it plants | result |
|---|---|---|
| ok | nothing | Every check printed and passed; then the read raised at `priors()` (the planted products have 16 cells, the real M16 takes 65,856 fine bins), rc 1. The deploy stayed clean, the records were tarred (23 files), and the done file was 1. |
| incomplete | `log-q3/pair.json` pass false | verdict INCOMPLETE, rc 3; readout.json and readout.txt written; 25 records tarred |
| bail_running | t3p_floor RUNNING in sacct | `BAIL fence (sacct) not clear`, rc 9; nothing written, no done file |
| stale_sums | one byte of `log-floor/SHA256SUMS` changed | `STOP: the products are not log-floor/SHA256SUMS's`, rc 9, before the read |

The launcher's post-fetch commands were run with macOS tools on the ok and incomplete outputs. In both:
- the tar's sha256 equalled the log's;
- it extracted, and `RECORDS.SHA256SUMS` checked (rc 0);
- `connect-read.log` is outside the tar and is fetched beside it.

The ok variant's crash comes from the fixture's 16-cell products. The real products have FD-PRR's shape: C-PAIR and C-X
compared them with FD-PRR's products, bitwise (same dtype, shape and bytes). The COMPLETE path is the guarded fixture
read above.

<!-- absence-ok: a record of checks on unrun connect scripts; "nothing written" describes the bail path's output -->
