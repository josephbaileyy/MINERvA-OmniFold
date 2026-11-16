# COV2D-G2R readout, phase G18: `READOUT-G18 PASS rc=0 verdict=UNDER-COVERS` (2026-11-14)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-readout-G18.sh`, `029ff7fb3455c2e27289d1ecf68cb9483aa0dd212bf7384f2ca02e631e7d49a3` (rev 2; the three connects differ only in PH, line 26).
- **Launcher:** `../launch-g2r.sh` `1f719ba3…` (its `readout-<PH>` arm; `../launch-g2r-readout-vs-ebf576f5.diff.txt`).
- **Go:** the director, "go 1f719ba3 with readout-data 56c34ad6, readout-G18 029ff7fb, readout-AR23 6bec8fad": one phase at a time, by hand, data → G18 → AR23, each after the previous phase's DONE, PASS and outputs verified in `$O/readout/<PH>/`; an overlap check against LL5D's 1146 paths before each.
- Full digests: `node-sha256.raw.txt` and `files.sha256`.

**CANNOT AUTHORIZE:** any adoption or wording. D1's adoption is Joseph's; the reading is in `../README.md`.

## The run

- **Overlap check** (`readout-ovl-G18.out.txt`, `../readout_ovl.py`): `readout-ovl PH=G18 host=login31: 21642 readout inputs (under $O 21634, MAT 8) x 1146 LL5D paths (1146 inodes): hits []`; `READOUT-OVL PASS`.
- **Launch** (`launch-stdout.txt`): `FENCE_CLEAR`, `DIGEST_MATCH`, `launched rc=0 at 2026-11-14T04:00:56Z`, `last line: DONE (polls=17 of 360, done_seen=1)`; the staged script and log removed (`removal.log.txt`; the launcher's `removal rc=2` is the final `ls`).
- **Connect log** (`connect.log.txt`, `6e10e8ec5093db10a5c47b9d8a22977bd0267a1d3779890aef8e710166080b55`), 2026-11-14T04:00:54Z to 2026-11-14T04:07:05Z, host login02:
  - `squeue: [61255888 ll5d_rerun129_01 PENDING 2:30:00 1;]`;
  - `readout place=/dev/shm/josephrb-g2r-readout-G18.4lbzTe clone head=401733bce290ce122cfbf38f1526e120f174b3ec porcelain_ignored=0 bound sums 19 OK TMPDIR=/dev/shm/josephrb-g2r-readout-G18.4lbzTe/tmp`;
  - `map_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae`;
  - `175 products for G18`;
  - `products.tsv 175 rows sha256 f367f10a81c128650a7e5f6910f139f00aa3b062b01b5730f8f8716f8d5d4a6f`;
  - `{"mat_setup_scripts": 6, "mismatches": 0}`;
  - `MAT preflight: MnvH1D PlotUtils::MnvH1D 14 bins`;
  - `G2R-TUNE verdict=UNDER-COVERS controls_failed=[] stop=[]`;
  - `READOUT-G18 PASS rc=0 verdict=UNDER-COVERS`;
  - `clone porcelain_ignored after=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `blobs unchanged`;
  - `copied to /pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/G18: blocks_g2r_G18.npz null_g2r_G18.json out.sha256 products.tsv readout.log score_g2r_G18.json `;
  - `removed the readout place /dev/shm/josephrb-g2r-readout-G18.4lbzTe rc=0 left=no`;
  - the log ends `DONE`.
- **Outputs** (`out.sha256.txt`), copied to `$O/readout/G18/` and re-read there O_NOATIME, each equal:
  - `blocks_g2r_G18.npz` `55ad7cc4faa4680b49391a9d68f52fcaa707150bd1300915063d66a16be9bfbe` (not committed; listed by sha256)
  - `null_g2r_G18.json` `d6b84ec086477d615a3240f3bdf4ea677ad0f24f801cfe912b885ac1e225f003` (committed here)
  - `score_g2r_G18.json` `27374aab74793444ee20561ced1066247b225a40067092d7d181e186128b9ec2` (committed here)
- `products.tsv.txt` lists each product the readout read, with its path and sha256; `readout.log.txt` is the readout's own log.
