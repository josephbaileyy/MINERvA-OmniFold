# xk: GENCMP X's step K re-pointed to COV2D-G2R (package; DRAFT for the director and coverage-5b-audit)

The director's XCOV ruling and xk design rulings (2026-11-16). `fd_xcov.py k --products g2r` re-points K's 2D side
(`fd_xcov_steps.PRODUCTS`):
- Q_R and S5_R become RE-2-shapes route A's. S5_R's band_<b> blocks are G2R's rebuilt band blocks: K1's 2D reference.
- the 2D band vectors become G2R's `A_<b>_<i>` products (pins: `INPUTS-g2r.sha256`, 177 rows from products.tsv);
- C-R becomes cr's readout (#1169), and cmodel_R becomes route A's (#1167).

C_PL_R, the S3 laterals, the stat replicas and the 5D side are unchanged. `--products re2`, the default, is K as it ran:
its readout has no `products` key and is otherwise produced unchanged. k1() also prints a `[K1 ratios]` line for every
band on stdout only (accepted by the director), so a re2 run and a g2r run show the K1 2D ratios side by side.

**Ruling 1 (V0, V1 and BOOT are reused, not rerun).** They read no 2D covariance product. `xk_copy.py` copies exactly
what cmd_k / k_compute read from `--run-dir` out of the original run directory: v0-a1/v0.json, v1-a2/v1.json, the BOOT
native lane record, boot/xcov (108 files) and inputs/of_inputs_5d.npz. It reads them O_NOATIME, each must equal
`fd/xcov/run/hpss/files.sha256`, and they go into two new run directories. The original k/ is untouched.

**Ruling 2 (V1's pairing).** V1 checks the MEFHC universes file's 2D weights against S1's. G2R unfolded from that file
under the same pin (220c479e = `cov2d.UNI_SHA256`), so the paired/bounded split carries over. The connect STOPs unless
the file hashes to X's pin. x-nbands, -paired and -bounded can then change only through K1's null list, which
`xk_report.py` prints per band, with the K1 ratios old beside new.

**Ruling 3 (the connect).** It runs on a login node: K took 11.27 s and 1.5 GB on login37
(fd/xcov/run/logs/k.log). The control runs re2 into scratch and must reproduce the committed fd/xcov/run/k/k.json
exactly (`xk_compare.py`: parsed equality, with no normalization needed). Then g2r runs. The fence is RE-2-shapes
rev 3's, verbatim. The template here is filled by `fill_connect_xk.py` at the package commit, and the filled connect
is sent by sha.

| file | what |
|---|---|
| `INPUTS-g2r.sha256` | route A's Q_R and S5_R, and G2R's 175 A_* products |
| `xk_copy.py`, `xk_compare.py`, `test_xk_tools.py` (+`.out.txt`) | copies and control comparison; 10/10 |
| `xk_report.py` | old beside new: route, primary, Q_R alone, x-nbands paired/bounded/total, nulls, K1 ratios |
| `test_fd_xcov.out.txt` | nd-unfolding/tests/test_fd_xcov.py with the XkProducts class: all pass |
| `run_xk_mutants.sh` (+`xk_mutants.out.txt`) | 5 mutants. 4 are killed by XkProducts. The 5th, which adds `products` under re2, can only be caught at run time: the control's comparison STOPs on the extra key (test_xk_tools) |
| `connect-g2r-xk.template.sh`, `fill_connect_xk.py`, `test_connect_xk.sh` | the connect and its stand-in |

**CANNOT AUTHORIZE:** any reading of K's outcome or any wording.
