# RDX read-only fetch connect (RDX-BINDING-1 addendum J7, ruling 2)

**Status: written and tested, not run.** It runs only on the director's go for these exact shas, after cov2d acks the
fence notice. Nothing has been fetched or read.

## What it fetches

From `B=/pscratch/sd/j/josephrb/rdx-20261112b`, under `$B/out`, 32 files:

- `products/<task>.npz` for the 15 tasks of `rdx_tasks.tsv` (X0, X0_lat, X1, X1p, X1w, X1t, X0c, X1c, X1pc, X1wc, X0t,
  X0g, X1g, X0q, X1q). Stage 3's stat-only listings put them at 96,063–189,035 bytes each (run-s3a-20261117 and
  run-s3b-20261117 READMEs), so the tar is a few MB.
- `inventory/<task>.jsonl` for the same 15 tasks.
- `logs/rdx_s3_a_61478320.out` and `logs/rdx_s3_b_61481240.out`.

## The code (rev 3, commit 3817eb0a)

| file | sha256 |
|---|---|
| `nd-unfolding/rdx/rdx_fetch_remote.py` | `89ea886d64a763c9a0fa24b7be3fd69fdbf5886b765678241370b184a21f2f0c` |
| `nd-unfolding/rdx/rdx_fetch_launch.sh` | `2650c5caf7a7846d99e8ff71def910dbd3c74ed329729113e10228d8768a9570` |
| `nd-unfolding/rdx/test_rdx_fetch.py` | `27ff97f1759425f43461671ae2a61664cae253dadf993098a0c021b090d2db69` |

The launcher pins the remote script's sha256 and refuses (exit 8) if the local copy differs.

Rev 2 fixes the two blockers from Grok's safety read of rev 1 (832f71d3):
- **B1:** the fence now reads every non-terminal state sacct supports, so a completing or configuring job counts. It
  is also read a second time, after the last file.
- **B2:** each file's full stat after its read is compared with its stat before the read, so a rewrite of the same
  length now exits 8.

Two more fixes came from the same read: unpack now checks the manifest's root, and the inner ssh no longer writes on
saul.

**Rev 3 fixes the STOP of 2026-11-18.** The rev 2 go ran at 18:40:48Z from a clean checkout at 3068cd63 on login27. The
remote refused at its first fence read with exit 9: `sacct: fatal: job state CF is not supported / accounted`. Nothing
was read, the tar was empty, nothing was unpacked, and cov2d got the end message. The local evidence is
`/Users/josephbailey/rdx-fetch-20261118/`. Per the director's ruling (b), the fence no longer passes a `-s` list,
because the codes that list accepts vary by site. It reads the State column instead, as described under the holds.

## The command (after the go)

```bash
bash nd-unfolding/rdx/rdx_fetch_launch.sh <new empty dir> <loginNN>
```

The launcher sends the local `rdx_fetch_remote.py` over ssh's stdin to `/usr/bin/python3 -` (3.6.15) on the login node,
through the connect launcher's hop (saul, then loginNN). The remote writes the tar to stdout, and the laptop receives
it as `<dir>/fetch.tar`. ssh's exit status is read unpiped. The laptop then unpacks into `<dir>/fetched` and prints
the tar's sha256.

## The holds

- **No job.** Nothing is submitted. The fetch is one ssh call to a login node.
- **Nothing is written on the cluster.** The script travels over stdin and the tar over stdout. Nothing is staged,
  not even under `/dev/shm`. The inner ssh (saul to loginNN) uses `ControlPath=none`, `StrictHostKeyChecking=yes` and
  `UpdateHostKeys=no`, so it writes no control socket or known_hosts entry on saul. If saul does not already know the
  login node's host key, the ssh refuses and nothing is fetched. Choose a login node that an earlier connect used.
- **O_NOATIME on every read.** The remote refuses (exit 3) on a platform without it. It records each file's stat
  before and after its read (size, mtime_ns, atime_ns, ino, dev) and keeps both in the manifest. It exits 8 (a STOP)
  if any field moved or the bytes read differ from the stat's size. That covers a moved atime, a rewrite of the same
  length and a replacement of the same size. The tar is complete either way.
- **The fence is sacct only.** The remote runs `sacct -X -n -P -u josephrb -S now-14days -o JobID,JobName,State`,
  with no `-s` list. It refuses (exit 9) in three cases:
  - sacct exits nonzero;
  - a row is malformed (not three fields, or no JobID);
  - a job of the families `cov2d|t2a|ll5d|e96data|rpd_|rsn_|rdx_|pfb_|ibukt-`, matched on its JobName, has a State
    outside the closed terminal set. That set is COMPLETED, FAILED, CANCELLED, "CANCELLED by <uid>", TIMEOUT,
    OUT_OF_MEMORY, NODE_FAIL, BOOT_FAIL, DEADLINE, PREEMPTED and REVOKED. Unknown and empty states refuse.

  Empty output from a successful sacct reads as clear. The fence is read again after the last file, and a job seen
  then also exits 9, after the tar. squeue is never called.
- **Refusals before output.** Exits 3, 9 and 4 (a missing file) all happen before anything is written to stdout.
- **The laptop unpack refuses (exit 2)** unless all of these hold:
  - the tar holds exactly the 32 declared files plus `manifest.json`, each a plain file at a declared path;
  - the manifest's root is the declared `$B/out`;
  - every sha256 and size matches the manifest;
  - each file's two stats are equal;
  - the manifest records O_NOATIME and two clear fence reads.

  On a refusal it writes nothing.
- **cov2d's ack** of the fence notice before the connect, and the end message after it.
- Any STOP, failure or timeout goes to the director unrepaired. Nothing is re-run.

## After the fetch

The read runs on the laptop in a clean clone at M_RDXR `9de8ef0d`, using `rdx_read.py` as bound by J7. It reads only
`<dir>/fetched`. This connect measures nothing and cannot authorize a reading.

## Receipt

- `tests.txt`: the 14 tests in a clean clone at 3817eb0a, exit 0. They run the fetch locally against a scratch root
  with a stub sacct. The cases are:
  - the fence classifying each state: completing, unknown, empty and malformed rows refuse; "CANCELLED by 123", the
    terminal states and other families' rows pass; the command has no `-s` and a 14-day window;
  - sacct failure, and a job seen only by the second fence read;
  - a missing file;
  - a rewrite of the same length and a replacement of the same size during a read, each exiting 8 with both stats
    recorded.

  They also check that the remote script parses as Python 3.6, exercise every unpack refusal (including a foreign root and
  moved stats), and test the launcher's argument and sha checks and its inner ssh options. The laptop has no
  O_NOATIME, so the fixture sets atime after mtime to keep relatime from moving it, and the manifest's `o_noatime` is
  set by the test for the unpack cases. The O_NOATIME refusal is tested on the laptop, and its real open is exercised
  only on the login node.
- **Not covered here:** the tests run under the laptop's Python 3.12. The 3.6 check is a grammar parse only, not a run
  under 3.6, and the APIs the script calls (`subprocess.run`, `st_*_ns`, `tarfile` stream mode) exist in 3.6.
