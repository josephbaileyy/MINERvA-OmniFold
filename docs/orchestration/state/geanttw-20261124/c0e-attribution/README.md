# C0e attribution: P0's 23 NOT ALLOWED paths (2026-11-26)

P0's check STOPPED on C0e (`check.txt`, the check connect's output, verbatim). The director ruled that C0e's
allowed list may be widened only on evidence. This folder holds that evidence. It is read-only parsing of the two
jobs' own strace logs, which were fetched without being changed.

## What was fetched

One read-only connect fetched the logs, under the director's GO and cov2d's ack
`cov2d-ACK-geanttw-c0e-fetch-2026-11-26T16:24:56Z`. It ran on login26 at 2026-11-26T16:25:16Z, with ssh rc 0 and
scp rc 0, and it wrote nothing on the cluster. Each local copy's sha256 equals the one `sha256sum` printed on the
cluster before the copy. All paths are under B = `/pscratch/sd/j/josephrb/geanttw-20261124`:

| file | bytes | sha256 |
|---|---|---|
| `run/p0/pin/strace.pin.1L` | 403079 | `ab6f8e06286ad8df209e24c42801eb50861ca8242546dad1e42bb675fe4c07a6` |
| `run/p0/pat/strace.pat.1L` | 400554 | `ca06b2f7010e85759591e0028d8d96f0ca58ad6f8c53516fd83d3b228190b0d5` |
| `run/p0/p0_check.json` | 29610 | `f2e8b4bcbaed5cfa9c3d7adb9f6a5bf285dddb430b63a8587ce3de3b14292663` |

The logs themselves are not committed. They stay at those paths under B.

## Method

`attribute.py` parses both logs with p0_check.py's own `OPEN` and `RESUMED` regexes and its `_opened()`, taken from
p0_check.py at M = `4fe6add5de54544196ddb90ac09cf033d8411515` (sha256
`8b06b783e1da05fb82e8419011359485f16463c688c81a96798db71b65859186`). So it sees exactly the successful opens C0e
judged. Its output is `attribution.json`. For each of the 23 paths and each build, it gives every open's line, PID,
flags, whether the PID is the main one, and whether the open used `O_DIRECTORY`. It also gives each child PID's first
five successful opens, and the hits of the director's test. The main PID is the log's first PID: 1346746
in pin and 722811 in pat. strace starts the binary, and that PID's first successful opens are the
conda ROOT libraries.

    python3 -I attribute.py <p0_check.py's directory at M> <a directory holding check.txt and the two logs>

## Result

The result is identical in both builds: all 23 paths appear in pin (23/23) and in pat (23/23).
- **Seven library directories:** opened by the main PID, always `O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY`. They
  come in one run, in `LD_LIBRARY_PATH` order, which is a search-path directory scan.
- **`cuda.h`:** opened by the main PID as a regular file. It comes right after probes of `/etc/debian_version`,
  `/etc/SuSE-release` and the SDK's `version.txt`, and just before cling's `.hipVersion` probe. That is clang's
  CUDA-installation detection.
- **`/var/lib/sss/mc/passwd`:** opened by the main PID as a regular file. It comes right after `libnss_sss.so.2`
  loads, and just before ROOT reads `system.rootrc`. That is the NSS user lookup.
- **14 Lmod files:** opened only by two child PIDs per build, never by the main PID. The first child opens
  `init/bash`, and its first five opens are `ld.so.cache`, `libreadline`, `libdl`, `libc` and `libtinfo`, followed
  by the locale files: a bash. The second child opens `libexec/addto` and the 12 `tools/*.lua`, then Lua 5.3's
  luaposix modules: Lua running Lmod's `addto`. Both children appear right after the main PID's first MC AnaTuple
  open.

**The director's test** asked whether the main PID opens any of the 23 as a regular file (not `O_DIRECTORY`), other
than `cuda.h` and the SSSD cache. It found 0 cases (`test2_stop_hits`).

**The limit of this evidence.** The jobs traced `openat` and `open` only. So these logs cannot show whether a file's
content was read, and they cannot show which process spawned a child, because no `clone` or `execve` was traced.
The test above is the strongest one these logs support.

**Files here.**
- `check.txt`: the check connect's output.
- `attribute.py` and `attribution.json`: the attribution.
- `README.md`: this file.
