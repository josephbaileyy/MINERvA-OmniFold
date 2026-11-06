REF-C2C1 step two, stage 3b: the READ (REF-C2C1-BINDING-2.md ruling 2.3; the director's rulings of 2026-11-06; code at
M = 77d76cfc). Run by limitation-resolver on the director's GO: refc2c1_read_login.sh, sha256
b162ba9ac8b12887e02ab3130dae4a9185f6fbdcfa2a0db684021e5e06c63f79, launched from main's bytes. It ran on login27 at
2026-11-06T13:43:50Z-13:44:43Z, at 0 node-h. Copied by O_NOATIME reads (launcher/pull3_tar.py) from
/pscratch/sd/j/josephrb/ref-c2c1-20261106/read/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: STOP, a control STOP from the reader. read.log: "STOP: failed controls ['C-PUB']; no reading was formed"; read
rc=1; read.done 1. No readout.json was written. STOP.json was written, sha256
968e0f2a071ce0671c08e9df7c3477d17a3bf6a8cb2258adb709ba8c99604153. Under the binding a control STOP goes to the director
unrepaired, and nothing has been re-run or changed. NOT OPENED by this lane: STOP.json and read.stdout (sha256
0dc7fecadd42e1619e4a472a8dc7fd8390fdacbc63c1282b7b8be8c736adad4f, 83 bytes). Both are committed here for the director to
read from main.
- THE LAUNCH (launcher/): launch_read_from_main.sh, sha256 48217abe0597c69b8e2bea48ea01632948a2cdcf3cc3675fb0c0fd3c9e53be39, a
  wrapper outside the audited set in the form of the completion's 40126474. On main fd4c572c, the read connect is b162ba9a
  (audited b162ba9a) and completion/REPLICAS-DONE-j4 is 5680f1f9 (recorded 5680f1f9). login27 re-hashed main's bytes to
  b162ba9a and launched; ssh rc 0 at 13:43:50Z (read-launch.out; read-check.out is the check-only run before it).
- THE GATE (read.log), all passed:
  - CENTRALS-DONE accepted;
  - REPLICAS-TIMEOUT-j0..3 and REPLICAS-DONE-j4 on main fd4c572c each equal to pscratch;
  - records failing their fields []; unit sets [73, 77, 77, 76, 47], disjoint, union 350, equal to lanes.tsv's 350;
    none without a PASS marker;
  - cells.root f06e4a26 on main and in the read directory;
  - HEAD M with porcelain 0; 8 blobs, 0 mismatches.
- THE READ: `ref_c2c1_read.py read` in root_6_28, 4 threads, nice 19, idle I/O; wall time 0:09.95, MaxRSS 389 MB
  (read.time). Before the STOP it had staged 2 files into read/inputs/ by O_NOATIME, the publication's
  cov_ptpl_minerva_inclusive_6GeV.root and one xsec.root (inputs-listing.txt: names and sizes, by stat; the staged copies
  are not committed).
- The COV2D inputs: logs-read/watch-after.txt is byte-identical to watch-before.txt (303 paths, owner, mode, atime, size),
  so no atime moved; none is owned by anyone else. Deploy porcelain --ignored is 0 before and after. THE FENCE, recorded:
  the full squeue at 13:43:50Z is in read.log.

Files: read.log, read.done, read.time, read.stdout, STOP.json; logs-read/ (the connect's copy, clone.log, the two
watch snapshots); inputs-listing.txt; launcher/ (the wrapper, its outputs, the copy script).
