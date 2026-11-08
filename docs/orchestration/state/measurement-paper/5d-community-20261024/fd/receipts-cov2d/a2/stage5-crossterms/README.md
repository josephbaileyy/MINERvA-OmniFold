# COV2D A2, stage 5: readout (i), the cross terms, at M (2026-11-07)

**By** the `cov2d` session. This ran under the director's ruling 2 of 2026-11-07: the bound `cross-terms` CLI may run
at M now, as a login-node connect at 0 node-h, with a receipt PR.

**M = `a60547692df5f963e428cdfe4661fc51ab785b7b`.**

- **MEASURES:** COV2D-DECLARATION.md §6 (i), descriptive with no verdict. Over the 600 declared draws (300 per tune),
  each reco cell's histogram under product composition is compared with first order, in units of √F, F being that
  draw's first-order expected count in the cell (COV2D-AMENDMENT-1.md §4).
- **CANNOT AUTHORIZE:** a verdict, a change to C_T or the rule, or A4. It reads no bulk output and no toy error.

**Result:** `COV2D-CROSS-TERMS draws=600 atime_moved=0`, rc 0, `pins_checked: true`. The stat of all four inputs was
unchanged across the run.

## The connect

- **The script:** `connect-x1.sh`, sha256 `4dc6b184eb151b152292ba2d864ccb539f5d7f1e46ed0e1968e428a299fe4d20`.
- **Its base:** the approved §9.2 receipt connect `../../receipt/connect-r1.sh`. The diff is `connect-r1-to-x1.diff.txt`:
  - fields: M, W (`/pscratch/sd/j/josephrb/cov2d-crossterms-20261107`), and the log name;
  - the six bound files the CLI loads, checked by sha256 against the clone at M (`bound.sha256`): `cov2d.py`,
    `cov2d_readouts.py`, `cov2d_receipt.py`, `cov2d_pseudo.py`, `clip_probe.py` and `fd_1b_toys.py`;
  - the CLI, swapped from `cov2d_receipt.py` to `cov2d_readouts.py cross-terms`;
  - two additions:
    - a `stat` of the four inputs before and after, which the director's ruling asks for;
    - a `git status --porcelain --ignored` line after.
- **Reads:** every read outside the clone goes through O_NOATIME:
  - `cov2d_receipt.read_noatime` and `open_noatime` for $UNI, the constraint file and the two ratio files;
  - the only plain read, `fd_1b_toys.F1_SUMS`, is a committed file inside the fresh clone.
- **The run:** login02, nice 19, 0 node-h, no job.
  - **Start:** 02:11:38Z. The deploy was a fresh clone, porcelain 0 and HEAD = M. Bound files 6 of 6 OK.
  - **End:** 06:04:18Z. Elapsed 3:51:47 (`crossterms.time.txt`), max RSS 14.0 GB.
  - **After:** porcelain `--ignored` 0; `STAT_UNCHANGED` (`stat_before.txt` = `stat_after.txt`).

## The Mac crash during the run

Joseph's computer crashed while the connect was running. The connect is a detached login process (`setsid nohup`), so
it was unaffected. Only the Mac-side launcher died: the wait, fetch and removal loop of `../stage5-control95/launch-s5.sh x1`.

**Lost:** the launcher's local records for this connect: its fence output, the staged-digest comparison and the launch
time. They lived in a `/tmp` scratchpad that the reboot wiped.

**What remains:**
- **The fence.** The fence before control 9.5's launch, 3 minutes earlier at 02:08:58Z, was clear
  (`../stage5-control95/fence.txt`). The launcher refuses to stage unless its own fence is clear, and the connect did
  start, at 02:11:38Z.
- **The script on the node.** A read-only inspection at 02:45:19Z (`node-x1.sh`, `node-x1.out.txt`) found:
  - the CLI still running;
  - the staged `/dev/shm/josephrb-cov2d-x1.sh` with sha256 `4dc6b184…`;
  - squeue empty.

  The same digest was recorded at removal (`removal.log.txt`). The local copy was fetched back from the node and matches
  it.
- **The fetch.** `fetch-x1.sh` is the launcher's fetch tail alone, with no fence, staging or launch. It waited for the
  end line, then:
  - fetched the log and outputs, each local sha256 equal to the node's (8 of 8 MATCH);
  - removed the staged script, rc 0.

Nothing was rerun.

## Result (`crossterms.json`, sha256 `84a7f73ed7c348daad384fc8dbde83a4fbd06cc094b8f08faba2abcee8a457f4`)

| tune | draws | median \|z\| | p90 \|z\| | max \|z\| | (cell, draw) pairs with F ≤ 0, excluded | cells with F ≤ 0 in every draw |
|---|---:|---:|---:|---:|---:|---:|
| G18 | 300 | 1.299 | 5.028 | 21.885 | 5,700 | 19 |
| AR23 | 300 | 1.361 | 5.114 | 21.244 | 5,700 | 19 |

- **z** is (P − F)/√F per (reco cell, draw), with P the product-composition count and F the first-order count. These are
  descriptive quantities. The declaration fixes no reading for (i).
- **The per-draw arrays** F and P are in `crossterms.npz` (sha256 `178a3a3b…`): `G18_first`, `G18_product`,
  `AR23_first` and `AR23_product`, each 300 × 224.
- **The per-cell medians** are in `crossterms.json` (`per_cell_median_abs`).
- **The excluded pairs:** 5,700 = 19 × 300 at each tune, so every excluded pair lies in a cell with F ≤ 0 in every draw.

## Files

- `connect-x1.sh`, `connect-r1-to-x1.diff.txt`, `bound.sha256`;
- `node-x1.sh`, `node-x1.out.txt`, `fetch-x1.sh`;
- `connect-x1.log.txt`, `crossterms.out.txt`, `crossterms.time.txt`;
- `stat_before.txt`, `stat_after.txt`;
- `crossterms.json`, `crossterms.npz`;
- `removal.log.txt`.
