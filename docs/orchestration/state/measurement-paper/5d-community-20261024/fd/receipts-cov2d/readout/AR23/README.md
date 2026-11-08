# COV2D addendum A4, phase N for AR23: the null record and the blocks (2026-11-07)

**By** the `cov2d` session. This ran under COV2D-BINDING-2 addendum A4, with the director's go for `connect-n-AR23.sh`
at the sha256 below, and under the director's fence ruling (below).

**M = `ac25b66533788ceb18b1d4e5add259c53b216669`** (code `7177d0f8`).

- **MEASURES:** phase N for AR23 (`COV2D-ADDENDUM-A4.md` §3). That is AR23's null at C_T, with its thresholds and size,
  the blocks phase S needs, §9.8, §9.9 for the 486 non-toy products (X, the U, L and B), and the input inventory and
  identity (§3.4).
- **CANNOT AUTHORIZE:** phase S for AR23, until this record is merged to main by the director. Phase S then runs at this
  M with `--null-digest` equal to `null_AR23.json`'s sha256 below.
  - It holds **no coverage reading**: no toy product was opened.
  - The numbers below describe the null distribution only.

**Result: `COV2D-NULL AR23 PASS stops=0 controls_failed=0`, rc 0.**

## The records

| file | sha256 | bytes |
|---|---|---:|
| `null_AR23.json` | `80274e52c23365e5c6f84fad977576e54507bf186e1d04a8da8d596a75b0ac76` | 74,036 |
| `blocks_AR23.npz` (force-added: `*.npz` is gitignored, `.gitignore:30`) | `abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee` | 3,015,016 |

- `null_AR23.json`'s `blocks_npz_sha256` equals the npz's sha256 above.
- Both files are byte-identical to the node's (MATCH in `launch-nAR23.out.txt`).

## What the record shows (all from `null_AR23.json`)

- **`M`** is the binding's M; `truth` is AR23; `verdict` is PASS; `stop` and `controls_failed` are empty;
  `pins_checked` is true.
- **Products:** `products_read` = 486. Each is read through O_NOATIME and checked against its digest in #866's
  `completeness.tsv`.
- **No toy was opened:** `toy_paths_opened` = 0. The 300 toys are in the inventory by stat only.
- **§9.9 over the 486 products:** `problems: []`. The `code` is the same one driverSha256 (`938c53c5…`) and
  omnifoldHelperSha256 (`e9623412…`) as G18's record (`../G18/null_G18.json`).
  - coverage-5b-audit's runArgv LOW did not fire.
- **§9.8:** pass. Asymmetry 7.1e-17; min/max eigenvalue 9.99e-13; **ndf 204**.
  - The ndf is the rank above 10⁻¹² of the largest eigenvalue (`cov2d_blocks.py:110-114`; COV2D-DECLARATION.md:253).
  - AR23's smallest eigenvalue, 9.99e-13 of the largest, falls just under that cut, so the ndf is 204. G18's, 1.05e-12,
    falls just over, so G18's is 205.
  - §9.8 asserts symmetry and PSD and records the ndf (COV2D-AMENDMENT-1.md:135). The declaration provides for
    ndf < 205: "with the Cholesky equality checked if ndf = 205" (:253). The null's χ² cut is taken at ndf 204.
- **Atime:** 495 inputs checked, `atime_moved: []`.
- **The open audit:** 529 guarded opens, 529 distinct, all 529 with the O_NOATIME bit; `refused: []`; 2,091 opens in all.
  - G18's was 530. G18 also reads the pinned `runs_G18C.tsv`, whose rows supersede `runs_G18.tsv`'s
    (`cov2d_readout.py:149`), and AR23 reads one runs table.
- **The inventory (§3.4)**, hashed without parsing:

  | file | sha256 | size | mtime (PST) |
  |---|---|---:|---|
  | `cells.npz` | `e1994617…0e6c` | 4,321,842 | 2026-11-05 23:35:29 |
  | `pseudo_a.json` | `bdb7a57d…5994` | 455,646 | 2026-11-05 23:35:29 |
  | `truth_xsec.npz` | `b3895fbb…dca1` | 542,304 | 2026-11-06 00:50:47 |

  - `pseudo_a.json`'s sha256 is the driver's AR23 pin.
  - All three mtimes fall inside AR23's job window, 2026-11-05 22:19:09 to 2026-11-06 00:50:53 PST.
  - `identity: {"problems": []}`.
- **The null** (`null`, 2,000,000 draws, seed 5742000, ndf 204): χ² cut 213.066; joint q 0.69185 (se 3.3e-4); match_rel
  2.8e-16.
  - `null_minus` (C_T⁻): q 0.69238.
  - Thresholds at n = 300: k_joint 190, α_joint 0.025, α_cell 1.22e-4.
  - Size: joint 0.0175; the per-truth union bound 0.0348.

## The fence, and the director's ruling on it

**The first attempt (`fence-refused-1/`)** was refused by the launcher's fence at 17:57:04Z, before staging, so nothing
ran.
- squeue held `60970044 rs1_dry PENDING`. That is the RS1 lane's dry run, bound in RS1-BINDING-2 (#885), not a cov2d job.
- The fence then refused on any queued job of ours.
- A read-only waiter (`wait-nAR23.sh`) polled squeue once, at 17:57:52Z, and was stopped when the ruling arrived. It
  launched nothing.

**The ruling (director, 2026-11-07, after G18's phase N):** the launcher may proceed when the only queued or running
jobs of ours are RS1's (`rs1_dry` and `rs1_full`). It still refuses on any `cov2d-*` job and on any job name it does not
recognise.
- **The reason given:** RS1 is bound and reads no COV2D input. Its inputs are the 5D bank, the s5p bkg dump and FD-STAB's
  references (RS1-BINDING-1/2).
- **Backstop:** phase N's own guards would catch a concurrent read of a COV2D input: the atime check on all 495 inputs,
  and the open audit.

**The change** is `launch-s5-fence-ruling.diff.txt`: the squeue test now passes only lines whose job-name field is
exactly `rs1_dry` or `rs1_full`, and it prints each such line as `FENCE_ALLOWED_RS1`. The sacct test is unchanged.
- `fence-ruling-test.txt` runs the new test on seven synthetic fence outputs. It clears for an empty queue, `rs1_dry`,
  and `rs1_dry` + `rs1_full`. It refuses for `cov2d-g18`, `rs1_dry` + `rs1_dryx`, `interactive`, and an unended
  `cov2d-x` in sacct.

**This run's fence (`fence.txt`)** was clear under the ruling at 2026-11-07T18:01:26Z on login02:
- squeue held only `60970044 rs1_dry RUNNING`, printed as `FENCE_ALLOWED_RS1`;
- no cov2d job was unended in sacct.

## The connect

- **The script:** `connect-n-AR23.sh`, sha256 `47728db0d948b512de1219bfa9551ab384c2ff69ad1d6ece1dccc02d8b25e1ff`. The
  director had it before launch.
  - It differs from `../G18/connect-n-G18.sh` in line 16 only (`T=AR23`); see `connect-n-G18-to-AR23.diff.txt`.
- **Staging (`staged_sha.txt`):** the node digest equalled the local one (DIGEST_MATCH). Launched at 18:01:44Z
  (`launch.txt`).
- **The run (`connect-n-AR23.log.txt`, `null_AR23.log.txt`):**
  - **Deploy:** a fresh clone at M in `/dev/shm`, porcelain 0, HEAD = M, `READOUT-SHA OK` (`d1a3cff9…`).
  - **MAT:** pinned before sourcing (`{"mat_setup_scripts": 6, "mismatches": 0}`). The MnvH1D preflight read
    `PlotUtils::MnvH1D`, 14 bins.
  - **Interpreter:** Python 3.11.14, numpy 1.26.4, ROOT 6.28/12, nice 19, taskset -c 8-11, threads 1.
  - **Time:** elapsed 4:31.91, max RSS 1.10 GB, exit status 0.
  - **After:** porcelain 0, HEAD = M, and the `2d-unfolding/cov2d` blobs unchanged.
  - **Removal:** the clone (1.2 G) and tmp, rc 0.
- **Removal (`removal.log.txt`):** the six fetched files were hashed on the node, then the staged script and the whole
  `/dev/shm/josephrb-cov2d-n-AR23` directory were removed, each with rc 0.
- **Not shown:** the 27 ROOT rootmap warnings, which are in `null_AR23.log.txt` and filtered only from the connect log's
  tail.
- **0 node-h:** a login node, no job.

## Files

- `null_AR23.json`, `blocks_AR23.npz`;
- `connect-n-AR23.sh`, `connect-n-G18-to-AR23.diff.txt`, `launch-s5-fence-ruling.diff.txt`, `fence-ruling-test.txt`,
  `launch-nAR23.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`;
- `connect-n-AR23.log.txt`, `null_AR23.log.txt`, `blobs.before.txt`, `blobs.after.txt`;
- `fence-refused-1/`: `fence.txt`, `launch-nAR23.out.txt`, `wait-nAR23.sh`, `wait-nAR23.log.txt`.
