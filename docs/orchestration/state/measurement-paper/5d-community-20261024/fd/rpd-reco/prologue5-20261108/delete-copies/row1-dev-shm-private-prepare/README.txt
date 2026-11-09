RPD-RECO #848 prologue rerun 5: deletion of the private prepare record and its root (2026-11-09T00:03Z, login27, 0 node-h)

The director gave the go after #953 merged (a50aa606). The cleanup connect is ../../rpd_prologue5_cleanup.sh, sha256
2d3e62bafe1e9cb39111e4885f958e387d84523a9810432449639400a548da50. It is declared in ledger.json in this directory, and
its sha256 at origin/main matched before launch.

WHAT RAN
  fence-mac.out          cov2d_fence.sh from the Mac before the connect: no cov2d-* job.
  The connect is pinned to login27, the only node holding the root, so no load survey was used. One ssh
  (saul -> login27) wrote it to a /dev/shm mktemp, compared its sha256 (it matched), then ran it. ssh's rc was 0,
  read unpiped.
  cleanup5.out           its stdout: the remote sha256, the in-script fence and the ledger between markers. The fence
                         was clear: squeue listed no job. Cleanup python rc=0; connect rc=0.
  cleanup5.err           its stderr: the NERSC login banner and the host line only.
  executed-ledger.json   the ledger block from cleanup5.out, as printed.

RESULT (executed-ledger.json)
  The private record .rpd-private/23ee3e970f74d1084106615b6dba8e6c4798e1728044d8831a90b8abc1296a66/prologue-prepare.json
  measured 81c3fb7af87602b13cff1cdad59e2faababffff8cd9d69a80a660fcffc3988e4, equal to the declared value.
  The whole root /dev/shm/limres-rpd-prologue5-20261108 was removed at 2026-11-09T00:03:55.508Z. That is 22197 files:
  the clone, the policy config, the check tools, the wrapper's captured output, the check outputs, the run directory
  and .rpd-private.
  still_present is []. rc 0.
  The run directory's files and the private record, before removal, are listed under before_run (19 entries).

Digests: SHA256SUMS.txt.
