# COV2D-G2R readout, phase data: `READOUT-data PASS rc=0 verdict=PASS` (2026-11-14)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-readout-data.sh`, `56c34ad69b2c3423128b982a3e12b328bbe3e53ccbbba9d8e6126a3c76103b3c` (rev 2; the three connects differ only in PH, line 26).
- **Launcher:** `../launch-g2r.sh` `1f719ba3…` (its `readout-<PH>` arm; `../launch-g2r-readout-vs-ebf576f5.diff.txt`).
- **Go:** the director, "go 1f719ba3 with readout-data 56c34ad6, readout-G18 029ff7fb, readout-AR23 6bec8fad": one phase at a time, by hand, data → G18 → AR23, each after the previous phase's DONE, PASS and outputs verified in `$O/readout/<PH>/`; an overlap check against LL5D's 1146 paths before each.
- Full digests: `node-sha256.raw.txt` and `files.sha256`.

**CANNOT AUTHORIZE:** any adoption or wording. D1's adoption is Joseph's; the reading is in `../README.md`.

## The run

- **Overlap check** (`readout-ovl-data.out.txt`, `../readout_ovl.py`): `readout-ovl PH=data host=login38: 21637 readout inputs (under $O 21629, MAT 8) x 1146 LL5D paths (1146 inodes): hits []`; `READOUT-OVL PASS`.
- **Launch** (`launch-stdout.txt`): `FENCE_CLEAR`, `DIGEST_MATCH`, `launched rc=0 at 2026-11-14T03:53:36Z`, `last line: DONE (polls=3 of 360, done_seen=1)`; the staged script and log removed (`removal.log.txt`; the launcher's `removal rc=2` is the final `ls`).
- **Connect log** (`connect.log.txt`, `957750e57a6bc43ac62b629d6d140cd0b9479c2db93744937b29a1555a3e21c3`), 2026-11-14T03:53:34Z to 2026-11-14T03:54:39Z, host login02:
  - `squeue: []`;
  - `readout place=/dev/shm/josephrb-g2r-readout-data.6NcKaX clone head=401733bce290ce122cfbf38f1526e120f174b3ec porcelain_ignored=0 bound sums 19 OK TMPDIR=/dev/shm/josephrb-g2r-readout-data.6NcKaX/tmp`;
  - `map_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae`;
  - `177 products for data`;
  - `products.tsv 177 rows sha256 a0f86fe191d6e02e4d4a9f9616dff6edaa2fadfb4384e9d56c333a92f771b8cf`;
  - `{"mat_setup_scripts": 6, "mismatches": 0}`;
  - `MAT preflight: MnvH1D PlotUtils::MnvH1D 14 bins`;
  - `G2R-DATA verdict=PASS controls_failed=[] stop=[]`;
  - `READOUT-data PASS rc=0 verdict=PASS`;
  - `clone porcelain_ignored after=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `blobs unchanged`;
  - `copied to /pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/data: data_g2r.json data_g2r.npz out.sha256 products.tsv readout.log `;
  - `removed the readout place /dev/shm/josephrb-g2r-readout-data.6NcKaX rc=0 left=no`;
  - `[PASS] weights_identical_across_playlists`;
  - `[PASS] weights_equal_constraint_file`;
  - `[PASS] weights_equal_vl175_build_json  {'sum': 211.01200325082078, 'n_eff': 19.060534772246488}`;
  - the log ends `DONE`.
- **Outputs** (`out.sha256.txt`), copied to `$O/readout/data/` and re-read there O_NOATIME, each equal:
  - `data_g2r.json` `cd975b64402325da489ae608277faf5f6d7a7cbebe4974465f90b07c336e083f` (committed here)
  - `data_g2r.npz` `3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b` (not committed; listed by sha256)
- `products.tsv.txt` lists each product the readout read, with its path and sha256; `readout.log.txt` is the readout's own log.
