# V-HALF-R first-build precondition: the w_truth check (receipt, 2026-11-11)

**By** the limitation-resolver lane, on the director's go of 2026-11-11, given ahead of the build because the answer
decides whether C6 and C7 can be built at all. Run under V-HALF-R-BINDING-1's first-build precondition (AMENDMENT-1
A3.4's weights rule and A8.2 2a). One login-node connect, 0 node-h.

**RESULT: PASS.** In the pinned 5D MC npz (`of_inputs_5d.npz`, sha256 `07fccc1a…`), every w_truth that a share or a
tilt counts is finite and nonnegative.

| row set | rows | non-finite | negative | zero | min | max |
|---|---:|---:|---:|---:|---:|---:|
| all | 32,849,103 | 0 | 0 | 0 | 0.000276 | 3.895 |
| pass_truth | 32,849,103 | 0 | 0 | 0 | 0.000276 | 3.895 |
| shares (pass_truth, true fine cell in Ω) | 32,846,301 | 0 | 0 | 0 | 0.000276 | 3.895 |
| tilt (true fine cell in Ω, any pass_truth) | 32,846,301 | 0 | 0 | 0 | 0.000276 | 3.895 |

The values are copied from [`wtruth.json`](wtruth.json) (sha256 `aa70534aa50686796979c2ffbf7f7d2a0340723cb6a0f0bfc4f5f8c4cce6c14c`).
That file was extracted from `connect/session.out`, and its sha256 equals the one the node printed.

**CITABLE FOR:** that w_truth is finite and nonnegative on the rows V-HALF-R's shares and tilts count, in the pinned
npz; the row counts above.

**NOT CITABLE FOR:** any binning, response fraction, share, V-HALF quantity or candidate outcome. The record also
shows every row passing pass_truth, and 2,802 rows lying outside Ω or outside the grid. Both are descriptions, and
this receipt makes no reading of them.

## The run

The scripts are under `../../`, committed at `22f2c64e`:
- `vhr_wtruth_launch.sh`, sha256 `51024b0f…`;
- `vhr_wtruth_connect.sh`, sha256 `a9a98ac0…`;
- `vhr_wtruth_check.py`, sha256 `51448813…`;
- the fence: the committed `cov2d_fence.sh`, sha256 `16a2a5cd…`.

1. **Survey** (`survey/`, 2026-11-11T03:21Z): one read-only ssh session read `/proc/loadavg`, nproc and the work
   directory's existence on six nodes.
   - login27 was the quietest, at 9.74 / 10.00 / 12.21 on 244 cores, with the work directory absent.
   - The others: login02 26.85, login33 39.40, login37 40.04, login21 46.27 and login05 72.81.
2. **Fence** (`fence/`, login27, 03:22:06Z): `FENCE CLEAR`.
   - squeue held only `61078463 ll5d_gate_G18 PENDING` and `61078506 ll5d_gate_AR23 PENDING`.
   - Of 28 cov2d/t2a sacct rows in 14 days, none was unended.
   - The node checked the staged copy's sha256 (`16a2a5cd…`).
3. **Connect** (`connect/`, login27, 03:22:21Z to 03:22:55Z): ssh rc 0, script rc 0, checker rc 0.
   - The node staged the copy at `a9a98ac0…`, equal to the approved sha256.
   - The fresh clone was at `f3d02e6d`, with HEAD equal and porcelain 0.
   - The checker (`51448813…`), `s5p_stage1_inspect.py` (`26569afc…`) and `h2_definition.json` (`b6790761…`) were each
     at their pinned sha256.
   - Python 3.10.19 and numpy 2.2.6 (omnifold_py310), threads 1, nice 19.
   - The checker verified the npz's sha256, read MCgen, pass_truth and w_truth through O_NOATIME (`"o_noatime": true`),
     and rebuilt Ω. Ω reproduced h2_definition.json's fine map (`930326a3…`), with 63,168 of 65,856 fine cells.
   - **The npz's stat was unchanged** (size, mtime, atime): `1548438020 1782610308 1794179838` before and after.
   - The record was printed, and `/dev/shm/limres-vhr-wtruth` was removed by its literal path. Nothing was written to
     pscratch or CFS.

`*/session.err` and `survey/survey.err` hold NERSC's login banner.

Nothing is submitted, deposited or tagged.
