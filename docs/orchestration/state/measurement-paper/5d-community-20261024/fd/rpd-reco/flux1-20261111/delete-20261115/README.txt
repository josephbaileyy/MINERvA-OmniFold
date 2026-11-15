RPD-RECO flux connect 1: deleting the run's pscratch root under a ledger row (limitation-resolver lane, 2026-11-15).

WHAT AND WHY
- The root /pscratch/sd/j/josephrb/rpd-reco-flux-20261111 holds the run's 12 factor products, the staged copies, the
  clone, the private prepare record and the job's files (../run-61206960/README.md, "Left on pscratch"). The receipt is
  merged, and the director lifted the LL5D HOLD on 2026-11-15 and asked for the deletion by sha.
- It runs in two connects, each on the director's go by sha, in the precedent of the per-period benchmark's deletion
  (2d-closeout/per-period-benchmark-20261106/receipts/delete-copies): every path declared, every recorded digest
  matched by an O_NOATIME read, and only then removal by literal path, then absence verified.

STEP A, THE INVENTORY (this commit; read-only)
- flux1_inventory.py (Python >= 3.6, stdlib; the login node's /usr/bin/python3 is 3.6.15). It lists every directory
  through a descriptor opened with O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_NOATIME and lstat's every entry relative to
  it. It reads no file's contents, follows no symlink, and writes and removes nothing. It prints every entry outside
  clone/ (kind, bytes, relative path, symlink target), clone/'s counts and listing digest, and the sha256 of the whole
  canonical listing. It reports entries on another device, entries owned by another uid, other kinds, and symlinks
  that resolve outside the root.
- flux1_cleanup_launch.sh (mode inventory): rpd_flux1_launch.sh's pattern. One ssh session enters at saul.nersc.gov
  and hops to the chosen login node, with the script on stdin. The node writes it to /dev/shm under umask 077, checks
  its sha256 against the approved one (else deletes it and exits 8), runs it at nice 19 under /usr/bin/python3 -B, and
  removes the copy. ssh's rc is read unpiped. 0 node-h, no Slurm job.
- Before the connect: the certificate's validity (TZ=UTC ssh-keygen -L, read only), the login survey and the COV2D
  fence through rpd_flux1_launch.sh's approved survey and fence modes (cov2d_fence.sh 16a2a5cd...).
- Tests: test_inventory.py (5 tests, OK on Python 3.12 and 3.10). An audit hook records every open, and the test
  requires that no file was opened. Planting a one-byte read of each file fails that test. The other tests cover the
  digest's stability and sensitivity, a symlink outside the root, a symlinked or missing root and an off-login host.
  The script parses as Python 3.6 (ast feature_version); the APIs it uses (os.listdir(fd), lstat/readlink with dir_fd)
  exist from 3.3. test_launch.sh (TEST-LAUNCH.out): five plumbing cases through local ssh and /dev/shm stand-ins: the
  staged run and copy removal; an altered local script (rc 8); a non-login node name (rc 9); a session dir that is not
  empty (rc 9); and a copy that differs on the node (rc 8, nothing left).

STEP A, THE RUN (2026-11-15, on the director's go "go 074c56a9 52957587 for step A, the read-only inventory, run
once"; stepA/)
- Shas from main's bytes at 9855389f2: flux1_inventory.py 074c56a9..., flux1_cleanup_launch.sh 52957587...,
  rpd_flux1_launch.sh 8354aece..., cov2d_fence.sh 16a2a5cd.... Certificate valid 2026-11-14T10:36:00Z to
  2026-11-15T10:37:34Z (TZ=UTC ssh-keygen -L, read only).
- Survey (stepA/survey/, 02:48Z): login05, 06, 08, 09 and 10 answered, and the root exists on each. login07 printed
  nothing. login06 had the lowest 1-minute load (41.30).
- Fence (stepA/fence/, login06, 02:49:01Z): FENCE CLEAR. squeue held only RDX's rdx_s1_1A (RUNNING), whose inputs are
  outside the root (tier3-design's notice).
- Inventory (stepA/inventory/, login06, 02:49:16Z to 02:49:23Z): ssh rc 0, the staged copy's sha256 equal to the
  approved one, script rc 0, the /dev/shm copy removed. Python 3.6.15.
  - root: dev 3592384858, ino 882727459953338490, uid 112498, mode 40700;
  - 24,422 entries, 22,190 files, 3,424,040,979 bytes; listing sha256
    6e9a273506598728091867436ef2fa562f3418f9726175d2d43bfb0ddce6ee89; problems 0 (every entry on the root's device and
    owned by this uid, no other kinds, no symlink outside the root);
  - clone/: 24,283 entries (2,093 directories, 22,069 files, 121 symlinks), 1,166,884,424 bytes, listing sha256
    9a85268d4f113460ef94c682f15ca7578534ffc7ce46da1348eefd6d848fd71f;
  - run/: 120 entries, 2,256,851,244 bytes: the 12 factor products (591,245,748 bytes), run/original-inputs (54
    staged files, 1,617,556,047 bytes), run/mat-data (the staged MAT tree, 37,943,898 bytes), run/real-mnv-check,
    run/prepare-check, run/staged, run/tmp and the run's records;
  - the job's files at the top (job.out, job.rc, connect.log and the rest), tools/fence_overlap.py, and
    .rpd-private/<hash>/prestage.json (the private prepare record, 258,133 bytes).

STEP B, THE DELETION (built 2026-11-15; runs only on the director's go by sha)
- The director's scope (2026-11-15): delete the clone, the 69 staged copies (each verified against its original's
  recorded stat first) and the records (each digest checked). Keep in place the 12 factor products,
  run/flux-extract.json, run/prestage.json and the .rpd-private record (until RPD-RECO closes). NEEDS.txt has the
  reasons.
- gen_delete.py builds flux1_delete.py (GEN-DELETE.out) from step A's committed inventory, the held-out prestage.json
  (sha256 99528ac8..., checked; a copy stays on pscratch, kept) and the committed files the digests come from. It
  copies step A's listing() and canon() verbatim, by AST. It classifies all 22,190 files and asserts none is left
  over:
  - 22,069 clone files, deleted on clone/'s listing digest 9a85268d... (a checkout of 763ab4dd);
  - 69 staged copies, each by its recorded sha256 read with O_NOATIME. 64 have a pscratch original that must lstat
    (no read) to its recorded stat_before size and mtime_ns. The 5 whose originals were files of the job's
    /dev/shm repository copy were checked at generation against git blobs at 763ab4dd (equal);
  - 37 records, each by the sha256 of its committed counterpart (run-61206960/records/, ../production-config.ready.json,
    ../tools/fence_overlap.py; the two prepare-check copies by their originals' recorded digests);
  - 15 files kept.
- flux1_delete.py (sha256 eb5315459e2dd077c40d19e47eaa5f1fb2baa40f509a1289b932f24ef25c5e56) removes nothing unless
  every check passes:
  1. a login node;
  2. the whole listing equals step A's (6e9a2735..., 24,422 entries), and so does clone/'s;
  3. every staged copy and original as above;
  4. every record's digest.
  It then removes 26 files by literal path and 8 trees (clone, run/original-inputs, run/mat-data,
  run/prepare-check, run/staged, run/real-mnv-check, run/tmp, tools) with shutil.rmtree, which does not follow
  symlinks. It requires the remaining listing to be exactly the 18 kept entries. Exit 0 done; 4 STOP with nothing
  removed; 8 the remaining tree differs; 9 a removal failed.
- flux1_cleanup_launch.sh gains a delete mode with that sha (launcher sha256 bf6302161d94a00cebccead08ac4cad9561f33ab6bcafe90f392b98edca7eeab; the inventory mode is unchanged).
- Tests: test_delete.py, 11 tests, OK on Python 3.12 and 3.10, with its constants replaced by a fixture's:
  - the happy path keeps exactly the kept set and leaves the originals untouched;
  - each STOP shows, through an audit hook on os.remove, os.rmdir and shutil.rmtree, that nothing was removed: a
    changed staged byte, a missing original, an original's moved mtime, an extra entry, a changed record, an off-login
    host, a symlinked root;
  - a failed removal returns 9, and a wrong kept set returns 8;
  - the committed script's constants are consistent with step A and the scope.
  Deleting the STOP gate fails 4 of them. test_launch.sh case 6 stages the delete mode the same way (TEST-LAUNCH.out).
  The script parses as Python 3.6.

FOLLOW-UP (the director, 2026-11-15)
- F-KEEP-HPSS: the kept files (the 12 factor products, flux-extract.json, prestage.json, about 592 MB) are exposed to
  pscratch's purge, and P0 pins them by sha256. They should get an HPSS copy before the purge window, in a separate
  package when convenient. The .rpd-private record is deleted when RPD-RECO closes.

Nothing is submitted, deposited or tagged, and no file leaves the repository.
<!-- absence-ok: the document's own status line -->
