# COV2D addendum A4, phase N for G18: the null record and the blocks (2026-11-07)

**By** the `cov2d` session. This ran under COV2D-BINDING-2 addendum A4 (origin/main `d53b5f01`), with the director's go
for `connect-n-G18.sh` at the sha256 below.

**M = `ac25b66533788ceb18b1d4e5add259c53b216669`** (code `7177d0f8`).

> **Superseded at this path (2026-11-08).** `null_G18.json` here is now phase N's rerun at M_A5 (`6bd5259d…`,
> `phase-n-2/README.md`), under COV2D-BINDING-2's A5 M line, ruling 2. This page is run 1's receipt: its record
> `ecdb4be2…` is at `7db5cb80` (#886). The two records differ only in `M` and `utc`, and the field-equality
> control read EQUAL. `blocks_G18.npz` is unchanged.

- **MEASURES:** phase N for G18 (`COV2D-ADDENDUM-A4.md` §3). That is G18's null at C_T, with its thresholds and size,
  the blocks phase S needs, §9.8, §9.9 for the 486 non-toy products (X, the U, L and B), and the input inventory and identity (§3.4).
- **CANNOT AUTHORIZE:** phase S, until this record is merged to main by the director. Phase S then runs at this M with
  `--null-digest` equal to `null_G18.json`'s sha256 below.
  - It holds **no coverage reading**: no toy product was opened.
  - The numbers below describe the null distribution only.

**Result: `COV2D-NULL G18 PASS stops=0 controls_failed=0`, rc 0.**

## The records

| file | sha256 | bytes |
|---|---|---:|
| `null_G18.json` | `ecdb4be2fbb18852d32c1a4f9fb3cbc4107310d72c5bdeb2eb3651996ed0c41f` | 73,711 |
| `blocks_G18.npz` (force-added: `*.npz` is gitignored, `.gitignore:30`) | `7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d` | 3,015,016 |

- `null_G18.json`'s `blocks_npz_sha256` equals the npz's sha256 above.
- Both files are byte-identical to the node's (MATCH in `launch-nG18.out.txt`).
- No git attribute or filter applies to either path, so `git show origin/main:<path>` returns these bytes, and that is
  what phase S's gate hashes.

## What the record shows (all from `null_G18.json`)

- **`M`** is the binding's M; `truth` is G18; `verdict` is PASS; `stop` and `controls_failed` are empty;
  `pins_checked` is true.
- **Products:** `products_read` = 486, which is X, 175 U, 10 L and 300 B. Each is read through O_NOATIME and checked
  against its digest in #866's `completeness.tsv`.
- **No toy was opened:** `toy_paths_opened` = 0. The 300 toys are in the inventory by stat only (inode, size, mtime).
- **§9.9 over the 486 products:** `problems: []`. The `code` is one driverSha256 (`938c53c5…`) and one
  omnifoldHelperSha256 (`e9623412…`).
  - coverage-5b-audit's LOW (runArgv first exercised on real products) did not fire.
- **§9.8:** pass. Asymmetry 7.0e-17; min/max eigenvalue 1.05e-12; ndf 205.
- **Atime:** 495 inputs checked, `atime_moved: []`.
- **The open audit:** 530 guarded opens, 530 distinct, all 530 with the O_NOATIME bit; `refused: []`; 2,092 opens in all.
- **The inventory (§3.4)**, hashed without parsing:

  | file | sha256 | size |
  |---|---|---:|
  | `cells.npz` | `b198afac…dfd1b` | 4,321,842 |
  | `pseudo_a.json` | `163cf1aa…f416` | 451,196 |
  | `truth_xsec.npz` | `8bf3f0c8…2cd7` | 542,304 |

  - `pseudo_a.json`'s sha256 is the driver's G18 pin.
  - `cells.npz` matches the G18 size and minute A4 states. Its mtime is 2026-11-05 03:52:06 PST, inside G18's job
    window.
  - `identity: {"problems": []}`.
- **The null** (`null`, 2,000,000 draws, seed 5742000, ndf 205): χ² cut 214.089; joint q 0.69723 (se 3.2e-4); match_rel
  2.8e-16.
  - `null_minus` (C_T⁻): q 0.69793.
  - Thresholds at n = 300: k_joint 192, α_joint 0.025, α_cell 1.22e-4.
  - Size: joint 0.0192; the per-truth union bound 0.0363.

## The connect

- **The script:** `connect-n-G18.sh`, sha256 `c9b3e929f6369c51f5a77a09cecf31e725de8d36592e7dfef9375032951c9832`. The
  director had it before launch.
  - Its base is control95's approved `../../a2/stage5-control95/connect-95-run3.sh`; the diff is
    `connect-95-run3-to-n-G18.diff.txt`.
  - `connect-n-AR23.sh` differs from it in line 16 only (`T=`).
- **The launcher:** `launch-s5.sh`. Its diff against the committed `../../a2/stage5-control95/launch-s5.sh` is
  `launch-s5-n.diff.txt`, which holds the a4t case (receipted in `../../a4/cluster_tests/`) and the nG18/nAR23 cases.
- **The fence (`fence.txt`):** clear at 2026-11-07T17:50:34Z on login02. squeue was empty, and no cov2d job was
  unended in sacct.
- **Staging (`staged_sha.txt`):** the node digest equalled the local one (DIGEST_MATCH). Launched at 17:50:54Z
  (`launch.txt`).
- **The run (`connect-n-G18.log.txt`, `null_G18.log.txt`):**
  - **Deploy:** a fresh clone at M in `/dev/shm`, porcelain 0, HEAD = M, `READOUT-SHA OK` (`d1a3cff9…`).
  - **MAT:** pinned before sourcing (`{"mat_setup_scripts": 6, "mismatches": 0}`). The MnvH1D preflight read
    `PlotUtils::MnvH1D`, 14 bins. The record carries `mat_environment`.
  - **Interpreter:** Python 3.11.14, numpy 1.26.4, ROOT 6.28/12, nice 19, taskset -c 8-11, threads 1.
  - **Time:** elapsed 4:30.57, max RSS 1.10 GB, exit status 0.
  - **After:** porcelain 0, HEAD = M, and the `2d-unfolding/cov2d` blobs unchanged (`blobs.before.txt` =
    `blobs.after.txt`).
  - **Removal:** the clone (1.2 G) and tmp, rc 0.
- **Removal (`removal.log.txt`):** the six fetched files were hashed on the node, then the staged script and the whole
  `/dev/shm/josephrb-cov2d-n-G18` directory were removed, each with rc 0.
- **Not shown:** the ROOT rootmap warnings (27 lines, `class RooUnfold… found in libUnfoldUtilsDict.so is already in
  libRooUnfold.so`). They are in `null_G18.log.txt` and were filtered only from the connect log's tail.
- **0 node-h:** a login node, no job.

## Files

- `null_G18.json`, `blocks_G18.npz`;
- `connect-n-G18.sh`, `connect-95-run3-to-n-G18.diff.txt`, `launch-s5-n.diff.txt`, `launch-nG18.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`;
- `connect-n-G18.log.txt`, `null_G18.log.txt`, `blobs.before.txt`, `blobs.after.txt`.
