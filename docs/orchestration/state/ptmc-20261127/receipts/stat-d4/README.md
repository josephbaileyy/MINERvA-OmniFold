# PTMC D4: the read-only stat connect (2026-11-27)

**What it was for.** It checks that REF-C2C1's own products, which the matched baseline (declaration §2.4, ruling D4)
is formed from, are still on /pscratch.

**Authorisations.**
- The director's GO for `ptmc_stat_launch.sh` (fa76d4e5…) with `ptmc_stat.sh` (6b775e313107d81b772e8bfcc6226fbafaf75a55be57c1db3bb72dd24a9e2142), once.
- cov2d's ack at 10:08:30Z.
- The NERSC cert was valid from 2026-11-27T02:04 to 2026-11-28T02:05 UTC.

**The run.**
- login04, 2026-11-27T10:08:52Z. The staged sha256 equalled the approved one.
- ssh rc 0, script rc 0, 0 node-h.
- It used lstat and find -printf only. No file was opened and nothing was written on /pscratch.

**Result:** `expected present 604 missing 0 (of 604)`.
- 1205 regular files are listed:
  - 903 under `units/c2_*`: c2_central, and c2_replica_b1..300, each as .npz, .done and .root;
  - 302 under `read-2/inputs`.
- None has zero size.
- File atimes run from 2026-11-06T07:31Z to 15:04Z. The purge window from the oldest is about 2027-01-01.
- The four directories' atimes read 2026-11-23T19:31Z, so this connect's readdir did not move them.

**Files.**
- `stat-launcher.txt`: the launcher's stdout.
- `session-out.txt`, `session-err.txt`: the session's own stdout and stderr (the stderr is NERSC's login banner).
- `harness.sh.txt`, `harness-out.txt`: the pre-run harness, 19/19.
  - It ran in debian:bookworm-slim with GNU find, with ROOT and the user substituted.
  - The launcher's STOP paths (a bad node name, a non-empty session dir, a changed script) were tested locally with
    no ssh.
