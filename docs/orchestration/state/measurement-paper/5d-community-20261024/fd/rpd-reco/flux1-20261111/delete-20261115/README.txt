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

STEP B, THE DELETION (after step A's output is committed)
- What still needs the root: NEEDS.txt, the director's condition before step B. RPD-RECO's pending P0 reads the 12
  factor products and run/flux-extract.json from this root, so they stay; the clone, the 69 staged copies (54 inputs,
  among them the 9 instrument files, and 15 MAT dependencies; the earlier "63" counted the instrument files twice) and
  the records are committed or duplicates of originals that stay in place. run/prestage.json is the director's call.
- flux1_delete.py will carry, as constants: the root's literal path; step A's listing digest and entry count; the
  paths it keeps; and the digests the records hold (the staged copies' recorded sha256s, the records' committed
  counterparts). It recomputes the listing with step A's code and requires the same digest. It reads each declared
  file with O_NOATIME and requires its digest, and lstat's each pscratch original against its recorded stat_before.
  Only then does it remove the declared paths by literal path, and it verifies them absent and the kept files present.
  Exit 0 done; 4 STOP with nothing removed; 8 something still present or a kept file missing; 9 a removal failed.
- Its sha256 goes to the director before it runs, under the same launcher pattern.

Nothing is submitted, deposited or tagged, and no file leaves the repository.
<!-- absence-ok: the document's own status line -->
