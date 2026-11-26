# geanttw P0 receipts (2026-11-26)

**P0 PASSES** on its second check. The first check's C0e FAIL stands as recorded. This folder holds every connect's
output and the cluster records. It covers two bindings:

- **GEANTTW-BINDING-P0** (#1385, M = `4fe6add5de54544196ddb90ac09cf033d8411515`) covers deploy, build, p0 and the
  first check. That check FAILED C0e on 23 environment paths, and every other control passed. The FAIL record and
  the attribution of the 23 paths are in `../c0e-attribution/`: `check.txt` is that connect's output, and
  `first-check/` holds its JSON, strace logs and `build.log`.
- **GEANTTW-BINDING-P0-CHECK2** (#1398, M = `4e9708a820acfc151cbc4695244d9aa1de6fa8ad`) covers the aside, a fresh
  deploy, and the check re-run with the revised C0e from #1394. That re-run gave **P0 PASS**.

No job was re-run. The two P0 jobs ran once.

## Connects, in order

Each connect used a fresh ssh: `ControlMaster=no`, `ControlPath=none`, `BatchMode=yes`, `ProxyJump=none` and
`ProxyCommand=none`. Each ran on the director's GO and a fresh cov2d ack, and from a clean checkout of its M.
cov2d's fence (`cov2d_fence.sh` rev 3, sha256 `7e81a721…`, read from M) printed FENCE CLEAR before every geanttw
step. The certificate was valid until 2026-11-27T14:22:19Z.

| file | step | cov2d ack | host, UTC | rc |
|---|---|---|---|---|
| `connects/preflight.out` | read-only `iris` + `sacct` | `cov2d-ACK-geanttw-preflight-2026-11-26T15:26:40Z` | login02, 15:27:22Z | 0 |
| `connects/p0-deploy.out` | deploy @ 4fe6add5; S0 re-hash `fe0bc458…` PASS | `cov2d-ACK-geanttw-p0-deploy-2026-11-26T15:43:11Z` | login36, 15:44:54Z | 0 |
| `connects/p0-build.out` | build; five CHECKs PASS | `cov2d-ACK-geanttw-p0-build-2026-11-26T15:45:39Z` | login21, 15:50:21Z | 0 |
| `connects/p0-p0.out` | p0; smoke, fence and cap gates; two jobs submitted | `cov2d-ACK-geanttw-p0-submit-2026-11-26T15:51:36Z` | login21, 15:52:22Z | 0 |
| `connects/p0-watch1.out` | read-only `sacct` + job-log read | `cov2d-ACK-geanttw-p0-watch-series-2026-11-26T15:52:45Z` | login38, 16:20:40Z | 0 |
| `../c0e-attribution/check.txt` | first check: **C0e FAIL**, P0 FAIL | `cov2d-ACK-geanttw-p0-check-2026-11-26T16:22:17Z` | login37, 16:22:56Z | 8 |
| `connects/check2-aside.out` | aside: `deploy` → `deploy-4fe6add5`, `p0_check.json` → `p0_check-4fe6add5.json` | `cov2d-ACK-geanttw-check2-aside-2026-11-26T20:49:21Z` | login05, 20:57:35Z | 0 |
| `connects/check2-deploy.out` | deploy @ 4e9708a8; S0 re-hash `fe0bc458…` PASS | `cov2d-ACK-geanttw-check2-deploy-2026-11-26T20:57:57Z` | login01, 20:59:11Z | 0 |
| `connects/check2-check.out` | second check: C0a–C0f all PASS, **P0 PASS** | `cov2d-ACK-geanttw-check2-check-2026-11-26T20:59:41Z` | login09, 21:00:16Z | 0 |

There were also three read-only fetches, under the acks `cov2d-ACK-geanttw-c0e-fetch-…T16:24:56Z`,
`cov2d-ACK-geanttw-buildlog-fetch-…T20:22:19Z` and `cov2d-ACK-geanttw-receipts-fetch-…T21:00:47Z`. The first two
are recorded in `../c0e-attribution/README.md`. The third brought the files in `cluster/`: it ran on login37 at
21:01:07Z, and each local copy's sha256 equals the one `sha256sum` printed on the cluster before the copy.
`cluster/build.log` comes from the second fetch, at 20:22:34Z, with sha256 `626c4faf…`, and is the same bytes as
`../c0e-attribution/first-check/build.log`. The second check's `p0_check.json` names it. The check re-run only
reads it, and nothing after the build writes it.

`connects/p0-build.out` is the build connect's output with **one redaction**. Line 30 is the cherry-pick's echo of
the upstream commit's author email, replaced by `<[email redacted]>`. The unredacted output's sha256 is
`90ff8244f4a0b7c5979584b5185e72047376d6870fb251f160528b767512de90`.

## The jobs

| | pin | pat |
|---|---|---|
| job, name | 62042572, `geanttw_p0_pin_1L` | 62042575, `geanttw_p0_pat_1L` |
| sacct | COMPLETED 0:0, 00:05:53 | COMPLETED 0:0, 00:07:15 |
| start, end (UTC) | 16:13:24Z, 16:19:17Z | 16:13:24Z, 16:20:39Z |
| binary md5 | `35a20fbcc7ab4c50541d8842a0f00a5e` | `2070a26f9b76b7313e902c6d5c10ea73` |
| output sha256 | `48e34d4402b0ec6ce20bed7926df7bbf1d108bc8f3284b5493a63bc1ebbc48fc` | `56112321d18b18f077befd519667611c521ba448969b7c15df167a9072891164` |

- **Request:** each job asked for 1 node, 2 CPUs per task and 16G, on the shared QOS. `sacct` shows AllocCPUS 10
  for each.
- **Charge:** at the declaration's rate of 0.0391 node-h per hour, the two jobs' 788 s come to about 0.0086
  node-h. That is an ESTIMATE; the measured charge was not read. Either way it is far under P0's [0.02, 0.08] and the
  8.0 cap.
- **Gate:** `cluster/ll5d_atime_post.txt` records cov2d's LL5D atime-post, 2026-11-15T02:21:21Z, written at
  15:52:13Z.

## The NuE file (condition (c))

These are the job logs' lines, from `cluster/geanttw_p0_*.out`:
- The mtime (2021-08-31T15:49:26Z) and the size (25403) are unchanged in both jobs, so nothing wrote the file.
- The atime moved from 16:08:09Z to 16:14:05Z (pin) and 16:14:01Z (pat). That is each loop's one plain read
  under the exception.
- **(a) The access at 16:08:09Z.** It predates both jobs' start (16:13:24Z), and P0 made no access to the file
  then. The director traced it to diag's test C (`precharge_c`), whose `measure.cpp` and `truth.cpp` set
  `SetNuEConstraint(true)`. The director recorded it as a miss in test C's binding.
- **(b) The out-of-order after-reads.** pat's after-read, at 16:20:37Z, shows 16:14:01Z, earlier than the
  16:14:05Z that pin showed at 16:19:16Z. That fits Lustre's lazily merged atime across clients, and it does not
  bear on the reads.

## Two misses in the preflight overlap check (minerva-lib's)

1. **The NuE file.** The check did not ask whether test C opens the NuE file, and it does. The director's test C
   binding had the same miss first.
2. **A stale status.** The check said test C was not running. Its remainder was submitted at about 15:27Z, the
   minute of the preflight's `sacct` read (15:27:22Z).

## Files

| file | bytes | sha256 |
|---|---|---|
| `connects/check2-aside.out` | 790 | `1d587bb5e5621af727d735ff393ed6ec6a89f8ce6a2eb2a4028db69396703f6f` |
| `connects/check2-check.out` | 2837 | `a22aaec4683afbfac79fe2463285b55777f2774807b299236073f0b2af8e0358` |
| `connects/check2-deploy.out` | 1680 | `8094d8e899e8f6e1a7d5e32ceaa5dbae66f0f11f86b275d49ef08718507d745b` |
| `connects/p0-build.out` | 6843 | `7e6a5966c89875718087befebd9415496d3522bb2e020366d16e1ee8d8bad134` |
| `connects/p0-deploy.out` | 1676 | `b66cbb0824324619d301c5ca89e5d88fcddce4d7f237bb9026ed5f14804e02fd` |
| `connects/p0-p0.out` | 8659 | `7a1c88ce17afcf81f25dc40739a90b9ba5b7751ac57b7b8e9d0c34b92394d123` |
| `connects/p0-watch1.out` | 2406 | `1fe1a4aa8ea835670a30fa700d505274d798811b222195dfa2a8091abffad08d` |
| `connects/preflight.out` | 4554 | `28670a80708b05b38a8c1100d41ec5debe09abb1841b201fb2165b7eb40e5530` |
| `cluster/acks.log` | 1120 | `28fe5101a37f32605439eb4250af10594f7324c7f023f0110088357baa26d10a` |
| `cluster/build.log` | 2221 | `626c4faf64686d01c095d1bf989aa8fdaf9e3f21f7fae52f373c4bfad7f79e23` |
| `cluster/geanttw_p0_pat_1L_62042575.out` | 34584 | `de0a4af7d6f61915c2c34fad1d00d4642e6e969148ba6c8c7c2831462f60658b` |
| `cluster/geanttw_p0_pin_1L_62042572.out` | 34584 | `a9861b1bade650ec309b179b7300a921b12b5763417bdb7d9f5647d1f23dacab` |
| `cluster/ll5d_atime_post.txt` | 75 | `401b833b5668971a4b423e69a75441de6cd17830ff9435bbcea4ab970e389c5a` |
| `cluster/p0_check.json` | 28053 | `4e78ed95bd530325aba0c1c45f125a835f3e17d6dea095a59335431813ee7989` |
| `cluster/sacct-p0-jobs.txt` | 206 | `a4dce7e0383aad2cbd9ec2cefea5e7d0d86f273e592599478665a5cab614b767` |
| `cluster/submissions.log` | 238 | `3ece6f060901c4a5cc5451998ea139545ee0e93fce19dcb534df93c7220c1c59` |
