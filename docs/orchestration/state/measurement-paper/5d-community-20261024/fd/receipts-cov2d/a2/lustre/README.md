# COV2D A2 item 5: /pscratch's Lustre atime settings, as far as a client can read them

**By** the `cov2d` session, 2026-11-05. Run on login02 with the director's GO for each sha. **MEASURES:** the mount
options and the client-side Lustre parameters on one login node. **CANNOT AUTHORIZE:** anything. A compute node's
settings were not read.

| probe | sha256 | log (sha256) | result |
|---|---|---|---|
| v1 `connect-lustre-atime.sh` | `2a426b1c…` | `lustre-atime-v1.log.txt` (`d212cc49…`) | mount options read; every `lctl` call rc 127, "command not found": `/usr/sbin` is not on the user PATH. This was the probe's defect, not a privilege refusal (`/usr/sbin/lctl` is `-rwxr-xr-x root`) |
| v2 `connect-lustre-atime-v2.sh` | `67fcff34…` | `lustre-atime-v2.log.txt` (`2b07a617…`) | v1 with `L=/usr/sbin/lctl` and new /dev/shm names; the director diffed the two before the GO |

**What can be read:**
- **The mount options** of `/pscratch` (`/proc/mounts`, `findmnt`): `rw,nosuid,nodev,checksum,rchecksum_force,flock,
  user_xattr,lruresize,lazystatfs,nouser_fid2path,verbose,encrypt,statfs_project`. There is no noatime, relatime,
  strictatime or lazytime option.
- **The client:** lctl 2.15.7.1_cray_20_ga54ba87, with one llite instance (`llite.scratch-ffff88a542593800`).
  - `lazystatfs=1` (statfs, not atime), `statahead_max=32`, `xattr_cache=1`.
  - Searching the llite parameter tree for atime, lazy and stat finds none named for atime.
  - `get_param 'mdc.*.atime*'` and `'llite.*.*atime*'` both give "No such file or directory".
  - `list_param -R 'mdc.*' | grep -i atime` is empty.

**What cannot be read from a client:** Lustre's atime update policy, for example the MDT's `atime_diff`. It is a
server-side parameter, and the client exposes no atime parameter. So whether a read's atime reaches what other nodes'
`stat` sees lazily is **not measured here**. It is consistent with the AR23 record, but not shown by it.
<!-- absence-ok: scopes what a client-side probe can read (no atime parameter exposed), as the decision asks the record to say -->

`removal.log.txt`: each probe's `/dev/shm` script and log were removed, rc 0. Each log's digest was taken on the node
before removal.
