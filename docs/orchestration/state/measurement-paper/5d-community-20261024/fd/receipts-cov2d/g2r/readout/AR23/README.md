# COV2D-G2R readout, phase AR23: `READOUT-AR23 PASS rc=0 verdict=UNDER-COVERS` (2026-11-14)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-readout-AR23.sh`, `6bec8fad7c4d527e86d1a43ba0d0f06a5e121c74638aa6a58d313f3c0d9f0ca2` (rev 2; the three connects differ only in PH, line 26).
- **Launcher:** `../launch-g2r.sh` `1f719ba3…` (its `readout-<PH>` arm; `../launch-g2r-readout-vs-ebf576f5.diff.txt`).
- **Go:** the director, "go 1f719ba3 with readout-data 56c34ad6, readout-G18 029ff7fb, readout-AR23 6bec8fad": one phase at a time, by hand, data → G18 → AR23, each after the previous phase's DONE, PASS and outputs verified in `$O/readout/<PH>/`; an overlap check against LL5D's 1146 paths before each.
- Full digests: `node-sha256.raw.txt` and `files.sha256`.

**CANNOT AUTHORIZE:** any adoption or wording. D1's adoption is Joseph's; the reading is in `../README.md`.

## The run

- **Overlap check** (`readout-ovl-AR23.out.txt`, `../readout_ovl.py`): `readout-ovl PH=AR23 host=login29: 21648 readout inputs (under $O 21640, MAT 8) x 1146 LL5D paths (1146 inodes): hits []`; `READOUT-OVL PASS`.
- **Launch** (`launch-stdout.txt`): `FENCE_CLEAR`, `DIGEST_MATCH`, `launched rc=0 at 2026-11-14T04:09:15Z`, `last line: DONE (polls=19 of 360, done_seen=1)`; the staged script and log removed (`removal.log.txt`; the launcher's `removal rc=2` is the final `ls`).
- **Connect log** (`connect.log.txt`, `b2428a08131f17591e45ac74f3c585cf0189a3cc6394a9515611888ef3a533fa`), 2026-11-14T04:09:13Z to 2026-11-14T04:15:36Z, host login02:
  - `squeue: [61255888 ll5d_rerun129_01 PENDING 2:30:00 1;]`;
  - `readout place=/dev/shm/josephrb-g2r-readout-AR23.OVOnIG clone head=401733bce290ce122cfbf38f1526e120f174b3ec porcelain_ignored=0 bound sums 19 OK TMPDIR=/dev/shm/josephrb-g2r-readout-AR23.OVOnIG/tmp`;
  - `map_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae`;
  - `175 products for AR23`;
  - `products.tsv 175 rows sha256 9534ddf451ab35725b282f7886ccfb72af9eff3639da65228d0f378ef8af4c64`;
  - `{"mat_setup_scripts": 6, "mismatches": 0}`;
  - `MAT preflight: MnvH1D PlotUtils::MnvH1D 14 bins`;
  - `G2R-TUNE verdict=UNDER-COVERS controls_failed=[] stop=[]`;
  - `READOUT-AR23 PASS rc=0 verdict=UNDER-COVERS`;
  - `clone porcelain_ignored after=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `blobs unchanged`;
  - `copied to /pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/AR23: blocks_g2r_AR23.npz null_g2r_AR23.json out.sha256 products.tsv readout.log score_g2r_AR23.json `;
  - `removed the readout place /dev/shm/josephrb-g2r-readout-AR23.OVOnIG rc=0 left=no`;
  - the log ends `DONE`.
- **Outputs** (`out.sha256.txt`), copied to `$O/readout/AR23/` and re-read there O_NOATIME, each equal:
  - `blocks_g2r_AR23.npz` `c060cb40232e0112ec440951f94841e87fc98b542a165eed2c8242898508a70a` (not committed; listed by sha256)
  - `null_g2r_AR23.json` `ae82601d7f8b2f5474bfe2a6060245c854eae2cbf90d706e8f1276971ff45872` (committed here)
  - `score_g2r_AR23.json` `fb6d1f7fddfa18124bf097087a2f895582ef0991f9888c5ab1ce16cefbbe3079` (committed here)
- `products.tsv.txt` lists each product the readout read, with its path and sha256; `readout.log.txt` is the readout's own log.
