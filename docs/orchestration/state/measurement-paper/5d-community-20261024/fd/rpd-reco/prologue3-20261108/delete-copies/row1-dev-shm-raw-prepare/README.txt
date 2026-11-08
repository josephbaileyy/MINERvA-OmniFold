RPD-RECO #848 prologue rerun 3: deletion of the raw prepare record (2026-11-08T04:57Z, login04, 0 node-h)

The director gave the go after #919 merged (e907ae34). The cleanup connect is ../../rpd_prologue3_cleanup.sh, sha256
418c6aadad1384332a8866d4970d31ee3d7635c220316d6d5f03fcfcc48de761, declared in ledger.json in this directory.

WHAT RAN
  fence-mac.out          cov2d_fence.sh from the Mac before the connect: no cov2d-* job (04:57:41Z).
  The connect is pinned to login04, the only node holding the root, so no load survey was used. One ssh
  (saul -> login04) wrote it to a /dev/shm mktemp, compared its sha256 (matched), then ran it. ssh's rc was 0, read
  unpiped.
  cleanup3.out           its stdout: the remote sha256, the in-script fence (squeue listed no jobs: clear), and the
                         ledger between markers. Cleanup python rc=0; connect rc=0.
  cleanup3.err           its stderr: the NERSC login banner and the host line only.
  executed-ledger.json   the ledger block from cleanup3.out, as printed.

RESULT (executed-ledger.json)
  The raw run/prologue-prepare.json measured 337a88c893f0e1b24d90db8d940133d172f22a1d67f0aa7f8cc5f5044c73b5c8, equal to
  the declared value. The whole root /dev/shm/limres-rpd-prologue3-20261108 (21312 files: the clone, the policy config,
  the tools and the run directory) was removed at 2026-11-08T04:57:47.197Z. still_present is []. rc 0.
  The run directory's ten files before removal are listed under before_run. They include the pre-move view
  (ea71db55..., 170498 bytes). That view can be rebuilt from the committed view and module-paths.tsv
  (../../tools/move_module_paths.py).

CORRECTION OF #919's NOTE (from Grok's check, relayed by the director)
  #919's PR body, README.txt and commit message said the view keeps, per key, only the name, the presence on each side
  and the comparison. That is true of the fingerprints only: environment_snapshot.fingerprints is replaced by
  environment_snapshot.fingerprint_comparison, which carries just those three things per key.
  The committed view also carries the display values in plain text. Both environment_snapshot.values and
  environment_after_setup hold all 358 keys. They are the producer's environment_record(): a key whose name matches
  its credential pattern becomes "<redacted credential field>", and a user:password@ in a URL becomes <redacted>@.
  In this view exactly one key is redacted, SSH_AUTH_SOCK, and no value has a redacted URL. The other 357 values
  appear as set. The two sections are identical.
  This meets the director's condition, which concerned redacted keys and fingerprints. It matches what #881 already
  committed: ../../../prologue2-20261107/run/environment_after_setup.json, 358 keys, SSH_AUTH_SOCK redacted.
