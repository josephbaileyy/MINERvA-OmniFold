RPD-RECO #848 prologue rerun 4: deletion of the private prepare record and its root (2026-11-08T08:50Z, login27, 0 node-h)

The director gave the go after #929 merged (68a36cf8). The cleanup connect is ../../rpd_prologue4_cleanup.sh, sha256
58b2942c901a1672759d6efda5157fe33db58bfefba25f97521285866a417594. It is declared in ledger.json in this directory, and
its sha256 at origin/main matched before launch.

WHAT RAN
  fence-mac.out          cov2d_fence.sh from the Mac before the connect: no cov2d-* job (08:50:40Z).
  The connect is pinned to login27, the only node holding the root, so no load survey was used. One ssh
  (saul -> login27) wrote it to a /dev/shm mktemp, compared its sha256 (it matched), then ran it. ssh's rc was 0,
  read unpiped.
  cleanup4.out           its stdout: the remote sha256, the in-script fence and the ledger between markers. The fence
                         was clear: one ens1_a1_dry job was RUNNING, which is an allowed name. Cleanup python rc=0;
                         connect rc=0.
  cleanup4.err           its stderr: the NERSC login banner and the host line only.
  executed-ledger.json   the ledger block from cleanup4.out, as printed.

RESULT (executed-ledger.json)
  The private record .rpd-private/3cdf27c8d29fe5d5407acb8ca456ade8a1df23de41ce5930c70a2a3bcb5cc522/prologue-prepare.json
  measured 7f12fdfdd14bf82ff1e9ba72324b9269bba183984f41cc6fdf5b4383573a0afb, equal to the declared value.
  The whole root /dev/shm/limres-rpd-prologue4-20261108 was removed at 2026-11-08T08:50:54.338Z. That is 21793 files:
  the clone, the policy config, the check tools, the wrapper's captured output, the check outputs, the run directory
  and .rpd-private.
  still_present is []. rc 0.
  The run directory's files and the private record, before removal, are listed under before_run (18 entries: the
  private record, eight run files and nine instrument copies).
