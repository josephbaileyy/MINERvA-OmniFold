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

STEP B, THE DELETION (after step A's output is committed)
- flux1_delete.py will carry, as constants: the root's literal path; step A's listing digest and entry count; and the
  digests the records hold, namely the 12 factor products (../run-61206960/records/run/flux-extract.json) and the 63
  staged copies (54 files and 9 instrument files in prestage.json, whose sha256 99528ac8... is listed in the run
  README). It recomputes the listing with step A's code and requires the same digest. It reads each declared file
  with O_NOATIME and requires its digest. Only then does it remove the root by its literal path, and it verifies the
  root is absent. Exit 0 removed and absent; 4 STOP with nothing removed; 8 still present; 9 a removal failed.
- Its sha256 goes to the director before it runs, under the same launcher pattern.

Nothing is submitted, deposited or tagged, and no file leaves the repository.
<!-- absence-ok: the document's own status line -->
