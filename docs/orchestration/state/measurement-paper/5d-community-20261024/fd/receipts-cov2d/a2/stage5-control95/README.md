# COV2D A2, stage 5: control 9.5 at M. **CONTROL-95 PASS** (run 3, 2026-11-07)

**By** the `cov2d` session. This ran under the director's ruling 2 of 2026-11-07: the bound `control95` CLI may run at
M now, as a login-node connect at 0 node-h, with a receipt PR. The ruling followed the stage-5 finding that M holds no
bulk readout driver; A4 is authorized for that.

**M = `a60547692df5f963e428cdfe4661fc51ab785b7b`** (COV2D-BINDING-2.md, A2 revision 2).

- **MEASURES:** whether the block code bound at M (`cov2d_blocks.py` blob `b9e63a38`) reproduces part B's S5_R blocks
  from part B's own products (COV2D-DECLARATION.md §9.5).
- **CANNOT AUTHORIZE:** A4, the readout, or any toy. It reads no bulk output and no toy error.
- **Why rerun:** run 2 (`../../control95/`, PASS 2026-11-04) ran at the amendment branch's `0bb6bca8`. Since then
  `cov2d_blocks.py` changed from `7c656f4a` to `b9e63a38`: it adds the open audit's guarded-open counts
  (`OpenAudit.counts`, recorded in `open_audit`), and nothing else. `cov2d.py` changed from `7dafdd3f` to `9e510e89`. Both
  are the blobs A2's bound table lists at M.

## The connect

- **The script:** `connect-95-run3.sh`, sha256 `6aa6658ed7f017d77e342a1acd3f96cef2d8c0c5a28cc99b6a37f554644e2efd`.
- **Its diff from run 2's approved connect** (`c1872353…`) is fields only (`connect-95-run2-to-run3.diff.txt`, 4 lines):
  - M;
  - the two blob literals, cov2d `9e510e89` and cov2d_blocks `b9e63a38`;
  - the comment naming the blocks blob and M.
- **The launcher:** `launch-s5.sh`. The copy here is the current one, whose only later change is a longer wait loop for
  cross-terms (720 polls, not 360). Its steps:
  1. **The fence**, read-only (`fence.txt`, 02:08:58Z): squeue empty, no unended cov2d attempt in sacct. FENCE_CLEAR.
  2. **Staging:** `/dev/shm/josephrb-cov2d-95.sh`. In a separate step, the node's sha256 equalled the local one:
     DIGEST_MATCH.
  3. **Launch** at 02:09:19Z, then a wait for `DONE`.
  4. **Fetch and removal:** the log and outputs were fetched, each local sha256 equal to the node's (5 of 5 MATCH,
     `removal.log.txt`). Then the staged script, every file, `tmp/mat_preflight.root`, `tmp/` and the directory were
     removed, rc 0 each.
- **The run:**
  - login02, 0 node-h, no job;
  - a fresh clone at M in `/dev/shm`, porcelain 0 and HEAD = M before and after;
  - blobs 9 of 9 before and after (`blobs.before.txt` = `blobs.after.txt`);
  - nice 19, `taskset -c 8-11`, thread caps 1;
  - Python 3.11.14, numpy 1.26.4, ROOT 6.28/12;
  - the MAT environment pinned as in run 2;
  - the MnvH1D preflight on `runEventLoopMC_1A.root` (sha256 `d54d2a2c…`, 14 bins);
  - the clone (1.2G) removed by the connect, rc 0.

## Result (`control95.json`, sha256 `873fdd8e4207598b69ce9c6e46c2e64fb4f2df58bb5fbda009caebe59f29e04a`)

- **COV2D-9.5 PASS**, with no STOP.
- **The comparison:**
  - all 44 `band_<b>` keys of part B's `production_cov.npz` compared, none missing;
  - worst relative difference 4.585e-16;
  - universe 4.97e-17, stat 0.0, against the tolerance of 1e-12.
- **The cells:** E_R's x equals `cells_x_EU`, and E_R's 205 reported cells equal `cmodel_2d.json`'s.
- **The products:** 486 read, each checked against part B's committed sums (175 universes, 10 laterals, 300 replicas
  and E_R).
- **The open audit:**
  - 1,603 opens logged, refused list empty;
  - 526 guarded opens (524 distinct paths), all 526 with the O_NOATIME bit;
  - the bypass scan has no hits.
- **atime:** checked on 516 inputs, 0 moved.
- **Modules:** every imported module resolved inside the clone.

These values match run 2's (worst 4.59e-16, universe 4.97e-17, stat 0.0), at M's bound code.

## Files

- `connect-95-run3.sh`, `connect-95-run2-to-run3.diff.txt`, `launch-s5.sh`;
- `fence.txt`;
- `connect-95.log.txt`, `control95.log.txt`, `control95.json`;
- `blobs.before.txt`, `blobs.after.txt`;
- `removal.log.txt`.
