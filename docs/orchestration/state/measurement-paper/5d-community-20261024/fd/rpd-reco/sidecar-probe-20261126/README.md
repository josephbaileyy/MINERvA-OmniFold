# RPD-RECO amendment 1: the read-only sidecar probe (2026-11-26)

The director gave a GO on 2026-11-26 to write this probe. **It runs only under a separate GO**, after tier3-design's
fresh ack. EVW2D goes first on NERSC, and the probe runs while no `geanttw_` job is queued or running.

**What it does** (amendment §2 and §8): one login02 ssh session, 0 node-h, no Slurm job, writing nothing on the
cluster.
1. **Pre-flight, before any file is opened:** it lstats every component of every path. A symlink or a wrong type
   refuses (exit 2). A missing file is reported, as the purge risk, and fails the probe (exit 9).
2. **The 12 omnifiles** `rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_<PL>.root` and `lat_zero.npz`
   (`measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz`) are stat-only: lstat, never opened. It reports each one's
   size, mtime, atime and purge exposure (atime + 56 days).
3. **The sidecar** `rdx-20261112b/out/dumps/truthx_RDX_ALL.npz` is the only file opened. The open is
   `O_NOATIME|O_NOFOLLOW|O_NONBLOCK`, through a descriptor walk that never follows a symlink. It is fstat'ed as the
   same regular file, streamed through sha256, then closed. Its atime, read by lstat before and after, must not move,
   and the digest must be `641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e`.

The report is one JSON object on stdout. Exit 0 means PASS: every path is present, the sidecar's digest is the pin, its
atime is unchanged, and the bytes read equal its size. The pattern is V_F Phase 2's fetch
(`fd/receipts-vf/p2/fetch_vfp2_remote.py`, FD-VF BINDING 2b).

| file | sha256 |
|---|---|
| `sidecar_probe_remote.py` (the reader) | `5de764bd1c1e80ba3b652de77912d8013e4207cf932c344a452888abc449e28b` |
| `sidecar-probe.sh` (the wrapper, built by `build_probe.sh`, embedding the reader as base64 and checking its sha256 on the node) | `54f149ceb1888c82bf1bcc712406ab1510b284fccc80edccf0abe1cd7d5666d1` |

**Run** (only under the run GO), from this directory:
`ssh -o ControlPath=none saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'" < sidecar-probe.sh > probe.json 2> probe.err`

**Checks:**
- `test_sidecar_probe.py`: 12 passed. It checks that only the sidecar is opened, and opened O_NOATIME; that a missing file,
  another digest, a moved atime or a short read each fail; that a symlink refuses before anything is opened; that
  nothing under BASE changes; and that the wrapper embeds exactly this reader and checks its sha256 and the node.
- `probe_mutation.py`: killed 8 of 8.
