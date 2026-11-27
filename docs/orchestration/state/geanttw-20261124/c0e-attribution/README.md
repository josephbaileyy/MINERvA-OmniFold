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

The originals stay at those paths under B. Byte-for-byte copies are committed in `first-check/` (below).

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
- `first-check/`: the first check's records and the script that moves them aside (below).

## The first check's records, and moving them aside (`first-check/`)

The director ruled that the check re-run needs a fresh deploy at a new M. The deploy step refuses on an existing
`B/deploy`, and check rewrites `B/run/p0/p0_check.json`, so the first check's state must move aside before the
re-run. Its records are kept here first.

- **`p0_check.json`, `strace.pin.1L` and `strace.pat.1L`:** the fetched copies listed above, byte for byte, so
  their sha256s equal the table at the top of this file. `p0_check.json` is the first check's JSON, with C0e FAIL.
- **`build.log`:** `B/run/p0/build.log`, the build's record, holding the five CHECKs and the SO, BIN, RPATH and
  PROD lines. `p0_check.json` names it, so the receipt carries it. It was fetched in one more read-only connect,
  under the director's GO and cov2d's ack `cov2d-ACK-geanttw-buildlog-fetch-2026-11-26T20:22:19Z`. That connect ran
  on login33 at 2026-11-26T20:22:34Z, and the local sha256 equals the one `sha256sum` printed on the cluster. The
  file is committed with `git add -f`, because `*.log` is ignored. Neither the aside script nor the check re-run
  changes it.
- **`aside_first_check.sh M COV2D_ACK`:** one login-node connect, run from the Mac.
  - It runs cov2d's fence (`cov2d_fence.sh` rev 3, read with `git show M:`) and STOPs on any nonzero rc.
  - Then, in one fresh ssh, it renames inside B: `B/deploy` → `B/deploy-4fe6add5`, and `B/run/p0/p0_check.json`
    → `B/run/p0/p0_check-4fe6add5.json`.
  - Both renames are checked before either runs: a missing source or an existing target refuses, and nothing moves.
  - Each rename is `mv -n`, checked afterwards. Nothing is deleted, and nothing else is written.
  - It runs only on the director's GO, named in the binding, and with a fresh cov2d ack.
- **`test_aside_first_check.py`:** 11 pytest cases, run with `python3 -m pytest first-check/test_aside_first_check.py`.
  They cover:
  - both renames, with contents kept;
  - a fence failure;
  - an existing target and a missing source, each of which refuses and moves nothing;
  - bad arguments;
  - the test-only ssh override;
  - the fixed ssh options and root;
  - no deletion or redirection in the remote part.

| file | bytes | sha256 |
|---|---|---|
| `first-check/p0_check.json` | 29610 | `f2e8b4bcbaed5cfa9c3d7adb9f6a5bf285dddb430b63a8587ce3de3b14292663` |
| `first-check/strace.pin.1L` | 403079 | `ab6f8e06286ad8df209e24c42801eb50861ca8242546dad1e42bb675fe4c07a6` |
| `first-check/strace.pat.1L` | 400554 | `ca06b2f7010e85759591e0028d8d96f0ca58ad6f8c53516fd83d3b228190b0d5` |
| `first-check/build.log` | 2221 | `626c4faf64686d01c095d1bf989aa8fdaf9e3f21f7fae52f373c4bfad7f79e23` |
| `first-check/aside_first_check.sh` | 3019 | `9be3cdf3d7b5a6e551547653da8b895e4e4b1fbfe5498c4f476a0a53309c7954` |
| `first-check/test_aside_first_check.py` | 5116 | `c78889b825b44bfcfcfb6928dbe39142dd685b5bf8dc10a83a11f45fbe2bb7f9` |
