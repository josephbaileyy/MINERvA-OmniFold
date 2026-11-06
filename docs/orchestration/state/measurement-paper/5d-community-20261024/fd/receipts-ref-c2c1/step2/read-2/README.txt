REF-C2C1 step two, stage 3b, second run: the READ at M' (REF-C2C1-BINDING-2.md ruling 2.3; the director's rulings of
2026-11-06 on C-PUB's operand, #839 and #842: M' = af70e9c4685acdf2d64e30d812942bea1e7ccb0c). Run by limitation-resolver
on the GO of coverage-5b-audit (#843) and the director: refc2c1_read_login.sh, sha256
d37f6682d8124ba292efd6a17906e53ed0a87f332e60a42f171b42c92ec42b95 (../read-connect-2/), launched from main 2968b58a's
bytes. It ran on login04 at 2026-11-06T15:03:17Z-15:04:20Z, at 0 node-h. Copied by O_NOATIME reads (launcher/pull_tar.py)
from /pscratch/sd/j/josephrb/ref-c2c1-20261106/read-2/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS. read rc=0, read.done 0. readout.json was written, sha256
0ee21301744cf04df4e1ebf7224692a00fba5188532b31af9d596be8ce69cf5a, and no STOP.json. NOT OPENED by this lane: readout.json
and read.stdout (sha256 5d60666aaea0e19617efd11c614c12c216b4716cf588e8470f8e1e933bde32ea, 149 bytes, the reader's printed
readings). Both are committed here for the director to read from main.
- THE UNITS STAND (the binding's ruling 1 at M', and coverage-5b-audit's point): the units (the three centrals and the
  350 replicas) stand on their records at 77d76cfc. ref_c2c1.py is byte-identical at M' (128b4e00). The units' meta
  config_sha256 names 77d76cfc's config.json, which differs from M''s only in c_pub, and the read never compares that
  field.
- THE LAUNCH (launcher/):
  - launch_read2_from_main.sh, sha256 48ed4a9415f75926b37706b522c9e8bc888e70935150c3dc8c686fbb09ccc7e8, a wrapper outside
    the audited set. It is coverage-5b-audit's 22f9bc82 with one header comment corrected (read-connect/ to
    read-connect-2/); the auditor confirmed that reversing that line reproduces 22f9bc82 byte for byte.
  - On main 2968b58a the read connect is d37f6682 (audited d37f6682) and completion/REPLICAS-DONE-j4 is 5680f1f9.
  - The first attempt, at 14:56:16Z, failed at ssh (rc 255) before the login side ran, and nothing launched: read-2 and
    deploy-read-2 were absent, and login04's /dev/shm held no copy. The one retry, at 15:03:17Z, reached login04, which
    re-hashed main's bytes to d37f6682 and launched; ssh rc 0 (read2-launch.out; read2-check.out is the check-only run).
- THE GATE (read.log), all passed:
  - cells.root copied from the stopped read's $O/read by O_NOATIME: f06e4a26, as required; main's cells.root is f06e4a26;
  - CENTRALS-DONE accepted;
  - REPLICAS-TIMEOUT-j0..3 and REPLICAS-DONE-j4 on main 2968b58a each equal to pscratch;
  - records failing their fields []; unit sets [73, 77, 77, 76, 47], disjoint, union 350, equal to lanes.tsv's 350;
    none without a PASS marker;
  - HEAD M' with porcelain 0; 8 blobs, 0 mismatches.
- THE READ: `ref_c2c1_read.py read` at M' in root_6_28, 4 threads, nice 19, idle I/O; wall time 0:19.21, MaxRSS 391 MB
  (read.time). It staged 302 files into read-2/inputs/ by O_NOATIME: the publication's
  cov_ptpl_minerva_inclusive_6GeV.root and 301 xsec.root, E_R's central and its 300 replicas (inputs-listing.txt, names
  and sizes by stat; the staged copies are not committed). At M' the reader also refuses unless the staged E_R and
  covariance are C-PUB's source's, and it did not refuse.
- The COV2D inputs: logs-read/watch-after.txt is byte-identical to watch-before.txt (303 paths: owner, mode, atime, size),
  so no atime moved; none is owned by anyone else. Deploy porcelain --ignored is 0 before and after. THE FENCE, recorded:
  the full squeue at 15:03:17Z is in read.log.
- The results index (tools/registry/results_index.py --check, with this receipt staged): fresh and complete. readout.json
  is a tracked JSON in the roots and is not included, so there is no --write.
- The stopped first run's $O/read is unchanged, as ruled. Stage 4 (deleting the staged copies, with a B9-form ledger row)
  waits for this receipt's merge.

Files: read.log, read.done, read.time, read.stdout, readout.json; logs-read/ (the connect's copy, clone.log, the two watch
snapshots); inputs-listing.txt; launcher/ (the wrapper, its outputs, the copy script).
