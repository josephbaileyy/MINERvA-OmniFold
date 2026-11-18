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

## The code (commit 9685b74e)

| file | sha256 |
|---|---|
| `nd-unfolding/rdx/rdx_fetch_remote.py` | `a346771e214c0f96fbaba629d2f69e12988c4609a5b0581ab0e0bbe7939a2223` |
| `nd-unfolding/rdx/rdx_fetch_launch.sh` | `c28f4ce0e6456f1e1c2f7216eae2bc3bc382cce4df95fa9d0b9de218ae54ee60` |
| `nd-unfolding/rdx/test_rdx_fetch.py` | `1b7f836c257f96f0027c0d1962b7613786878540859af20903434af82df29d76` |

The launcher pins the remote script's sha256 and refuses (exit 8) if the local copy differs.

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
  not even under `/dev/shm`.
- **O_NOATIME on every read.** The remote refuses (exit 3) on a platform without it. It records each file's atime
  before and after its read and exits 8 (a STOP) if any atime or size moved. The tar is complete either way.
- **The fence is sacct only.** The remote runs `sacct -X -n -P -u josephrb -s PD,R,RQ,S -o JobID,JobName,State` and
  refuses (exit 9) if sacct fails or any job of the families `cov2d|t2a|ll5d|e96data|rpd_|rsn_|rdx_|pfb_|ibukt-` is
  pending, running, requeued or suspended. squeue is never called.
- **Refusals before output.** Exits 3, 9 and 4 (a missing file) all happen before anything is written to stdout.
- **The laptop unpack refuses (exit 2)** unless the tar holds exactly the 32 declared files plus `manifest.json`, each
  as a plain file at a declared path; every sha256 and size matches the manifest; and the manifest records O_NOATIME,
  no moved atime and a clear fence. On a refusal it writes nothing.
- **cov2d's ack** of the fence notice before the connect, and the end message after it.
- Any STOP, failure or timeout goes to the director unrepaired. Nothing is re-run.

## After the fetch

The read runs on the laptop in a clean clone at M_RDXR `9de8ef0d`, using `rdx_read.py` as bound by J7. It reads only
`<dir>/fetched`. This connect measures nothing and cannot authorize a reading.

## Receipt

- `tests.txt`: the 10 tests in a clean clone at 9685b74e, exit 0. They run the fetch locally against a scratch root
  with a stub sacct (the fence in both directions, sacct failure, a missing file), check that the remote script parses
  as Python 3.6, exercise every unpack refusal, and test the launcher's argument and sha checks. The laptop has no
  O_NOATIME, so the fixture sets atime after mtime to keep relatime from moving it, and the manifest's `o_noatime` is
  set by the test for the unpack cases. The O_NOATIME refusal is tested on the laptop, and its real open is exercised
  only on the login node.
- **Not covered here:** the tests run under the laptop's Python 3.12. The 3.6 check is a grammar parse only, not a run
  under 3.6, and the APIs the script calls (`subprocess.run`, `st_*_ns`, `tarfile` stream mode) exist in 3.6.
